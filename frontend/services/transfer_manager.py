"""Suivi et annulation des transferts UDP côté frontend.

Le service UDP fourni par le projet n'expose pas d'API d'annulation par
fichier. Ce module enveloppe ses méthodes internes pour :

* enregistrer le socket créé pour chaque transfert ;
* connaître le nom et la direction de chaque fichier ;
* interrompre un transfert en fermant son socket et en ignorant son
  enregistrement dans l'historique.

Aucune valeur n'est simulée : l'état affiché reflète les sockets réellement
utilisés par ``TransferService``.
"""

from __future__ import annotations

import itertools
import json
import threading
import time
from pathlib import Path
from typing import Any, Callable

from frontend.services.constants import UNAVAILABLE

_tls = threading.local()

FINAL_STATUSES = {"Terminé", "Annulé", "Échec"}
STATUS_COLORS = {
    "En attente": ("#A85C00", "#FBE8CE"),
    "En cours": ("#0B62F2", "#DBE9FD"),
    "Terminé": ("#0A720B", "#CDF0E2"),
    "Annulé": ("#A4252B", "#F7DCDE"),
    "Échec": ("#A4252B", "#F7DCDE"),
}


class TransferManager:
    """Registre des transferts en cours, avec annulation par identifiant."""

    def __init__(self, service: Any):
        self.service = service
        self._lock = threading.RLock()
        self._records: dict[int, dict[str, Any]] = {}
        self._ids = itertools.count(1)
        self._original_make_socket = None
        self._original_record = None
        self._original_receive = None
        self._attached = False
        self.attach()

    # ------------------------------------------------------------------
    # Accrochage au service
    # ------------------------------------------------------------------
    def attach(self) -> None:
        if self._attached or self.service is None:
            return
        self._original_make_socket = getattr(self.service, "_make_socket", None)
        self._original_record = getattr(self.service, "_record", None)
        self._original_receive = getattr(self.service, "_receive_transfer", None)

        if self._original_make_socket is not None:
            self.service._make_socket = self._make_socket
        if self._original_record is not None:
            self.service._record = self._record
        if self._original_receive is not None:
            self.service._receive_transfer = self._receive_transfer
        self._attached = True

    def detach(self) -> None:
        if not self._attached or self.service is None:
            return
        if self._original_make_socket is not None:
            self.service._make_socket = self._original_make_socket
        if self._original_record is not None:
            self.service._record = self._original_record
        if self._original_receive is not None:
            self.service._receive_transfer = self._original_receive
        self._attached = False

    # ------------------------------------------------------------------
    # Enveloppes des méthodes du backend
    # ------------------------------------------------------------------
    def _new_record(
        self,
        direction: str,
        filename: str | None,
        peer: Any,
        path: str | None = None,
        status: str = "En attente",
    ) -> int:
        with self._lock:
            transfer_id = next(self._ids)
            self._records[transfer_id] = {
                "id": transfer_id,
                "direction": direction,
                "filename": filename or UNAVAILABLE,
                "peer": str(peer) if peer else UNAVAILABLE,
                "path": path,
                "status": status,
                "progress": 0,
                "cancel_event": threading.Event(),
                "socket": None,
                "created_at": time.time(),
            }
            return transfer_id

    def _make_socket(self):
        sock = self._original_make_socket()
        transfer_id = getattr(_tls, "transfer", None)
        with self._lock:
            record = self._records.get(transfer_id) if transfer_id else None
            if record is not None:
                record["socket"] = sock
        return sock

    def _receive_transfer(self, offer, peer):
        """Crée une fiche dès qu'une offre de fichier entrant est acceptée."""

        transfer_id = self._new_record(
            "réception", self._offer_filename(offer),
            peer[0] if peer else UNAVAILABLE,
            status="En cours",
        )
        _tls.transfer = transfer_id
        try:
            return self._original_receive(offer, peer)
        except Exception:
            # La fermeture volontaire du socket provoque une OSError attendue :
            # elle ne doit pas remonter dans la console.
            with self._lock:
                record = self._records.get(transfer_id)
            if record is not None and record["cancel_event"].is_set():
                return None
            raise
        finally:
            self._forget_socket(transfer_id)
            _tls.transfer = None

    @staticmethod
    def _offer_filename(offer) -> str:
        try:
            payload = getattr(offer, "payload", b"") or b""
            metadata = json.loads(payload.decode("utf-8", "replace"))
            name = Path(str(metadata.get("name", ""))).name
            return name or "Fichier entrant"
        except Exception:
            return "Fichier entrant"

    def _record(self, filename, direction, peer, status):
        """Évite d'écrire un échec dans l'historique pour un transfert annulé."""

        transfer_id = getattr(_tls, "transfer", None)
        record = self._records.get(transfer_id) if transfer_id else None
        if record is not None:
            if record["cancel_event"].is_set():
                return None
            normalized = str(status).strip().lower()
            if normalized in ("terminé", "réussi", "success"):
                self._set_status(transfer_id, "Terminé", 100)
            elif normalized in ("échec", "failed"):
                self._set_status(transfer_id, "Échec")
        if self._original_record is not None:
            return self._original_record(filename, direction, peer, status)
        return None

    # ------------------------------------------------------------------
    # État des transferts
    # ------------------------------------------------------------------
    def _set_status(self, transfer_id: int, status: str, progress: int | None = None) -> None:
        with self._lock:
            record = self._records.get(transfer_id)
            if record is None:
                return
            record["status"] = status
            if progress is not None:
                record["progress"] = progress

    def _set_progress(self, transfer_id: int, progress: int) -> None:
        with self._lock:
            record = self._records.get(transfer_id)
            if record is not None and not record["cancel_event"].is_set():
                record["progress"] = max(0, min(100, int(progress)))

    def _forget_socket(self, transfer_id: int) -> None:
        with self._lock:
            record = self._records.get(transfer_id)
            if record is not None:
                record["socket"] = None

    def begin_send(self, paths: list[str], host: str) -> list[int]:
        """Prépare une file de fichiers à envoyer vers ``host``."""

        ids: list[int] = []
        for path in paths:
            ids.append(self._new_record(
                "envoi", Path(path).name, host, path=str(path)
            ))
        return ids

    def start_send(
        self,
        transfer_id: int,
        progress: Callable[[int, str], None] | None = None,
    ) -> None:
        """Envoie un fichier préparé ; les annulations sont traduites en succès muet."""

        with self._lock:
            record = self._records.get(transfer_id)
        if record is None:
            return
        if record["cancel_event"].is_set():
            self._set_status(transfer_id, "Annulé")
            return

        _tls.transfer = transfer_id
        self._set_status(transfer_id, "En cours", 0)

        def report(sent, total):
            ratio = min(100, int(sent * 100 / max(1, total))) if total else 100
            self._set_progress(transfer_id, ratio)
            if progress is not None:
                progress(ratio, record["filename"])

        try:
            self.service.send_file(record["path"], record["peer"], progress=report)
        except Exception:
            if record["cancel_event"].is_set():
                self._set_status(transfer_id, "Annulé")
            else:
                self._set_status(transfer_id, "Échec")
                raise
        else:
            if record["cancel_event"].is_set():
                self._set_status(transfer_id, "Annulé")
            else:
                self._set_status(transfer_id, "Terminé", 100)
        finally:
            _tls.transfer = None
            self._forget_socket(transfer_id)

    # ------------------------------------------------------------------
    # Annulation
    # ------------------------------------------------------------------
    def cancel(self, transfer_ids: list[int] | set[int]) -> int:
        """Annule les transferts demandés en fermant leurs sockets UDP."""

        cancelled = 0
        for transfer_id in transfer_ids:
            try:
                transfer_id = int(transfer_id)
            except (TypeError, ValueError):
                continue
            with self._lock:
                record = self._records.get(transfer_id)
                if record is None or record["status"] in FINAL_STATUSES:
                    continue
                record["cancel_event"].set()
                record["status"] = "Annulé"
                sock = record["socket"]
            if sock is not None:
                try:
                    sock.close()
                except OSError:
                    pass
            cancelled += 1
        return cancelled

    def cancel_all(self, direction: str | None = None) -> int:
        return self.cancel([
            item["id"] for item in self.snapshot(
                direction=direction, include_finished=False
            )
        ])

    # ------------------------------------------------------------------
    # Lecture pour l'interface
    # ------------------------------------------------------------------
    def snapshot(
        self,
        direction: str | None = None,
        include_finished: bool = True,
    ) -> list[dict[str, Any]]:
        with self._lock:
            items = [dict(record) for record in self._records.values()]

        if direction is not None:
            items = [item for item in items if item["direction"] == direction]
        if not include_finished:
            items = [item for item in items if item["status"] not in FINAL_STATUSES]
        items.sort(key=lambda item: item["created_at"], reverse=True)

        for item in items:
            item.pop("cancel_event", None)
            item.pop("socket", None)
            item.pop("path", None)
            item.pop("created_at", None)
        return items

    def active_count(self, direction: str | None = None) -> int:
        return len(self.snapshot(direction=direction, include_finished=False))

    def clear_finished(self) -> None:
        with self._lock:
            for transfer_id, record in list(self._records.items()):
                if record["status"] in FINAL_STATUSES:
                    del self._records[transfer_id]
