"""Service de transfert de fichiers UDP pour QuickSend LAN.

Le protocole applicatif utilise des datagrammes UDP de petite taille et un
accusement de réception par paquet (stop-and-wait) : les fichiers arrivent donc
intégralement et dans le bon ordre, même si UDP ne garantit rien par lui-même.
"""

from __future__ import annotations

import ipaddress
import json
import math
import os
import socket
import sqlite3
import struct
import tempfile
import threading
import time
import uuid
from contextlib import contextmanager
from dataclasses import dataclass
from datetime import datetime, timezone
from pathlib import Path
from typing import Callable

# ---------------------------------------------------------------------------
# Protocole
# ---------------------------------------------------------------------------

MAGIC = b"QSND"
VERSION = 1

MSG_OFFER = 1      # annonce d'un nouveau transfert (nom, taille, taille des paquets)
MSG_ACCEPT = 2     # le récepteur accepte et donne son port de travail
MSG_DATA = 3       # morceau de fichier
MSG_ACK = 4        # accusement de réception d'un morceau
MSG_RESULT = 5     # résultat final du transfert
MSG_DISCOVER = 6   # recherche d'appareils sur le LAN
MSG_ANNOUNCE = 7   # réponse à une recherche
MSG_DONE = 8       # l'expéditeur demande le résultat final

_HEADER = struct.Struct("!4sBB16sII")  # magic, version, type, session, seq, taille
HEADER_SIZE = _HEADER.size
MAX_PAYLOAD = 1200                     # < MTU ethernet (pas de fragmentation IP)
MAX_DATAGRAM = HEADER_SIZE + MAX_PAYLOAD + 64

ProgressCallback = Callable[[int, int], None]


@dataclass(frozen=True)
class _Packet:
    type: int
    session: bytes
    seq: int
    payload: bytes

    @classmethod
    def encode(
        cls,
        packet_type: int,
        session: bytes,
        seq: int = 0,
        payload: bytes = b"",
    ) -> bytes:
        return _HEADER.pack(MAGIC, VERSION, packet_type, session, seq, len(payload)) + payload


def _decode(data: bytes) -> _Packet | None:
    """Décodage tolerant : les datagrammes inconnus sont simplement ignorés."""
    if len(data) < HEADER_SIZE or len(data) > MAX_DATAGRAM:
        return None

    magic, version, packet_type, session, seq, length = _HEADER.unpack_from(data)
    if magic != MAGIC or version != VERSION:
        return None
    if length != len(data) - HEADER_SIZE or length > MAX_PAYLOAD:
        return None

    return _Packet(packet_type, session, seq, data[HEADER_SIZE:])


def _json_bytes(value: dict) -> bytes:
    return json.dumps(value, ensure_ascii=True).encode("utf-8")


def _json_dict(payload: bytes) -> dict:
    value = json.loads(payload.decode("utf-8"))
    if not isinstance(value, dict):
        raise ValueError("Message de transfert invalide.")
    return value


def get_local_ip() -> str:
    """Retourne l'IP LAN de la machine (aucun paquet n'est réellement envoyé)."""
    probe = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    try:
        probe.connect(("8.8.8.8", 80))
        return probe.getsockname()[0]
    except OSError:
        return "Non disponible"
    finally:
        probe.close()


# ---------------------------------------------------------------------------
# Service
# ---------------------------------------------------------------------------


class TransferService:
    """Réception, envoi, découverte d'appareils et historique SQLite (UDP)."""

    CHUNK_SIZE = 1200
    MAX_HEADER_SIZE = 64 * 1024  # conservé pour compatibilité avec l'ancienne API

    def __init__(
        self,
        receive_folder: str | Path,
        database_path: str | Path = "quicksend.db",
        port: int = 5000,
        device_name: str | None = None,
        ack_timeout: float = 0.5,
        max_retries: int = 12,
    ) -> None:
        if not 1 <= port <= 65535:
            raise ValueError("Le port doit être compris entre 1 et 65535.")
        if ack_timeout <= 0:
            raise ValueError("Le délai d'attente doit être positif.")
        if max_retries < 1:
            raise ValueError("Le nombre de tentatives doit être positif.")

        self.receive_folder = Path(receive_folder).expanduser()
        self.receive_folder.mkdir(parents=True, exist_ok=True)
        self.database_path = Path(database_path)
        self.database_path.parent.mkdir(parents=True, exist_ok=True)
        self.port = port
        self.device_name = device_name or socket.gethostname()
        self.ack_timeout = ack_timeout
        self.max_retries = max_retries

        self.transfer_timeout = 15.0   # inactivité maximale pendant une réception
        self.result_window = 2.0       # durée pendant laquelle on redit le résultat

        self._stop_event = threading.Event()
        self._server_socket: socket.socket | None = None
        self._server_thread: threading.Thread | None = None
        self._active_sockets: set[socket.socket] = set()
        self._sockets_lock = threading.Lock()
        self._transfer_threads: set[threading.Thread] = set()
        self._threads_lock = threading.Lock()

        self._initialize_database()

    # ------------------------------------------------------------------
    # Cycle de vie
    # ------------------------------------------------------------------

    @property
    def is_running(self) -> bool:
        return bool(self._server_thread and self._server_thread.is_alive())

    def start(self) -> None:
        """Démarre l'écoute UDP dans un thread."""
        if self.is_running:
            return

        self._stop_event.clear()
        server = self._make_socket()
        try:
            server.bind(("0.0.0.0", self.port))
        except OSError:
            server.close()
            raise
        server.settimeout(0.5)

        self._server_socket = server
        self._server_thread = threading.Thread(
            target=self._serve,
            name="QuickSendUdpReceiver",
            daemon=True,
        )
        self._server_thread.start()

    def stop(self) -> None:
        """Arrête l'écoute et les transferts en cours."""
        self._stop_event.set()

        if self._server_socket is not None:
            self._server_socket.close()
            self._server_socket = None

        with self._sockets_lock:
            for sock in list(self._active_sockets):
                try:
                    sock.close()
                except OSError:
                    pass
            self._active_sockets.clear()

        with self._threads_lock:
            transfers = list(self._transfer_threads)
        for thread in transfers:
            thread.join(timeout=3)

        if self._server_thread is not None:
            self._server_thread.join(timeout=2)
            self._server_thread = None

    def configure(
        self,
        *,
        receive_folder: str | Path | None = None,
        port: int | None = None,
    ) -> None:
        """Met à jour les paramètres et redémarre l'écoute si elle était active."""
        was_running = self.is_running
        self.stop()

        if receive_folder is not None:
            self.receive_folder = Path(receive_folder).expanduser()
            self.receive_folder.mkdir(parents=True, exist_ok=True)
        if port is not None:
            if not 1 <= port <= 65535:
                raise ValueError("Le port doit être compris entre 1 et 65535.")
            self.port = port

        if was_running:
            self.start()

    # ------------------------------------------------------------------
    # Envoi
    # ------------------------------------------------------------------

    def send_file(
        self,
        file_path: str | Path,
        host: str,
        progress: ProgressCallback | None = None,
    ) -> None:
        """Envoie un fichier à ``host`` via UDP ou lève une exception.

        ``progress`` reçoit (octets_envoyés, taille_totale) après chaque paquet
        accusé. Il est appelé depuis le thread qui envoie le fichier.
        """
        path = Path(file_path).expanduser()
        if not path.is_file():
            raise FileNotFoundError(f"Fichier introuvable : {path}")

        try:
            ipaddress.ip_address(host)
        except ValueError as exc:
            raise ValueError(f"Adresse IP invalide : {host}") from exc

        size = path.stat().st_size
        session = uuid.uuid4().bytes
        offer_payload = _json_bytes(
            {"name": path.name, "size": size, "chunk_size": self.CHUNK_SIZE}
        )
        offer = _Packet.encode(MSG_OFFER, session, 0, offer_payload)

        sock = self._make_socket()
        peer = (host, self.port)
        completed = False

        try:
            answer = self._request(
                sock,
                offer,
                peer,
                session,
                {MSG_ACCEPT, MSG_RESULT},
            )
            if answer.type == MSG_RESULT:
                content = _json_dict(answer.payload)
                raise RuntimeError(content.get("error", "Transfert refusé."))

            content = _json_dict(answer.payload)
            peer = (host, int(content["port"]))

            total_chunks = math.ceil(size / self.CHUNK_SIZE)

            with path.open("rb") as source:
                for seq in range(1, total_chunks + 1):
                    chunk = source.read(self.CHUNK_SIZE)
                    packet = _Packet.encode(MSG_DATA, session, seq, chunk)

                    acked = False
                    for _ in range(self.max_retries):
                        try:
                            sock.sendto(packet, peer)
                        except OSError as exc:
                            raise ConnectionError(
                                f"Échec de l'envoi vers {host}: {exc}"
                            ) from exc

                        answer = self._wait_for(
                            sock, session, {MSG_ACK, MSG_RESULT}, peer=peer
                        )
                        if answer is None:
                            continue

                        if answer.type == MSG_RESULT:
                            final = _json_dict(answer.payload)
                            if not final.get("ok"):
                                raise RuntimeError(
                                    final.get("error", "Erreur de réception")
                                )
                            completed = True
                            break

                        ack_content = _json_dict(answer.payload)
                        if int(ack_content.get("seq", -1)) == seq:
                            acked = True
                            if progress is not None:
                                sent = min(seq * self.CHUNK_SIZE, size)
                                try:
                                    progress(sent, size)
                                except Exception:
                                    pass
                            break

                    if completed:
                        break
                    if not acked:
                        raise ConnectionError(
                            f"Le destinataire {host} n'accuse pas réception du paquet {seq}."
                        )

            if not completed:
                done = _Packet.encode(MSG_DONE, session)
                for _ in range(self.max_retries):
                    try:
                        sock.sendto(done, peer)
                    except OSError as exc:
                        raise ConnectionError(
                            f"Échec de l'envoi vers {host}: {exc}"
                        ) from exc

                    answer = self._wait_for(sock, session, {MSG_RESULT}, peer=peer)
                    if answer is not None:
                        final = _json_dict(answer.payload)
                        if not final.get("ok"):
                            raise RuntimeError(
                                final.get("error", "Erreur de réception")
                            )
                        completed = True
                        break

                if not completed:
                    raise ConnectionError(
                        f"Aucune confirmation de réception reçue de {host}."
                    )

        except RuntimeError:
            self._record(path.name, "envoyé", host, "échec")
            raise
        except (OSError, ValueError, KeyError, TypeError, json.JSONDecodeError) as exc:
            self._record(path.name, "envoyé", host, "échec")
            if isinstance(exc, ConnectionError):
                raise
            raise ConnectionError(f"Échec de l'envoi vers {host}: {exc}") from exc
        finally:
            sock.close()

        self._record(path.name, "envoyé", host, "terminé")

    # ------------------------------------------------------------------
    # Réception
    # ------------------------------------------------------------------

    def _serve(self) -> None:
        server = self._server_socket
        if server is None:
            return

        while not self._stop_event.is_set():
            try:
                data, address = server.recvfrom(MAX_DATAGRAM)
            except socket.timeout:
                continue
            except OSError:
                break

            packet = _decode(data)
            if packet is None:
                continue

            if packet.type == MSG_DISCOVER:
                response = _Packet.encode(
                    MSG_ANNOUNCE,
                    packet.session,
                    0,
                    _json_bytes({"name": self.device_name, "port": self.port}),
                )
                self._safe_send(server, response, address)
            elif packet.type == MSG_OFFER:
                thread = threading.Thread(
                    target=self._run_transfer,
                    args=(packet, address),
                    name="QuickSendUdpTransfer",
                    daemon=True,
                )
                with self._threads_lock:
                    self._transfer_threads.add(thread)
                thread.start()

    def _run_transfer(self, offer: _Packet, peer: tuple[str, int]) -> None:
        try:
            self._receive_transfer(offer, peer)
        finally:
            with self._threads_lock:
                self._transfer_threads.discard(threading.current_thread())

    def _receive_transfer(self, offer: _Packet, peer: tuple[str, int]) -> None:
        session = offer.session
        filename = "fichier inconnu"

        try:
            metadata = _json_dict(offer.payload)
            filename = Path(str(metadata["name"])).name
            size = int(metadata["size"])
            chunk_size = int(metadata.get("chunk_size", self.CHUNK_SIZE))
            if not filename or size < 0 or not 1 <= chunk_size <= MAX_PAYLOAD:
                raise ValueError("Métadonnées de transfert invalides.")
        except (ValueError, KeyError, TypeError, json.JSONDecodeError):
            return

        transfer_socket = self._make_socket()
        with self._sockets_lock:
            self._active_sockets.add(transfer_socket)
        try:
            transfer_socket.bind(("0.0.0.0", 0))
        except OSError:
            transfer_socket.close()
            with self._sockets_lock:
                self._active_sockets.discard(transfer_socket)
            return

        temporary_path: str | None = None
        temporary = None
        result: dict

        try:
            port = transfer_socket.getsockname()[1]
            accept = _Packet.encode(
                MSG_ACCEPT,
                session,
                0,
                _json_bytes({"port": port, "chunk_size": chunk_size}),
            )
            self._safe_send(transfer_socket, accept, peer)

            total_chunks = math.ceil(size / chunk_size)
            received: set[int] = set()
            last_activity = time.monotonic()

            descriptor, temporary_path = tempfile.mkstemp(
                prefix=".quicksend-", dir=self.receive_folder
            )
            temporary = os.fdopen(descriptor, "r+b")
            temporary.truncate(size)

            while len(received) < total_chunks and not self._stop_event.is_set():
                idle = time.monotonic() - last_activity
                if idle > self.transfer_timeout:
                    raise TimeoutError("Transfert interrompu (aucune donnée reçue).")

                transfer_socket.settimeout(min(0.5, self.transfer_timeout - idle))
                try:
                    data, sender = transfer_socket.recvfrom(MAX_DATAGRAM)
                except socket.timeout:
                    continue
                except OSError:
                    break

                packet = _decode(data)
                if packet is None or packet.session != session:
                    continue
                if packet.type != MSG_DATA or sender[0] != peer[0]:
                    continue

                seq = packet.seq
                if not 1 <= seq <= total_chunks:
                    continue

                expected = (
                    chunk_size
                    if seq < total_chunks
                    else size - (total_chunks - 1) * chunk_size
                )
                if len(packet.payload) != expected:
                    continue

                last_activity = time.monotonic()
                temporary.seek((seq - 1) * chunk_size)
                temporary.write(packet.payload)
                received.add(seq)

                ack = _Packet.encode(MSG_ACK, session, seq, _json_bytes({"seq": seq}))
                self._safe_send(transfer_socket, ack, sender)

            if self._stop_event.is_set():
                raise ConnectionError("Transfert interrompu (service arrêté).")

            temporary.flush()
            temporary.close()
            temporary = None

            destination = self._available_destination(filename)
            os.replace(temporary_path, destination)
            temporary_path = None

            result = {"ok": True}
            self._record(filename, "reçu", peer[0], "terminé")

        except Exception as exc:  # noqa: BLE001 - tout échec doit être signalé
            result = {"ok": False, "error": str(exc) or type(exc).__name__}
            self._record(filename, "reçu", peer[0], "échec")
        finally:
            if temporary is not None:
                try:
                    temporary.close()
                except OSError:
                    pass
            if temporary_path and os.path.exists(temporary_path):
                try:
                    os.unlink(temporary_path)
                except OSError:
                    pass
            with self._sockets_lock:
                self._active_sockets.discard(transfer_socket)

        result_packet = _Packet.encode(MSG_RESULT, session, 0, _json_bytes(result))
        self._safe_send(transfer_socket, result_packet, peer)

        # Le résultat peut être perdu : on répond aux nouvelles demandes du
        # expéditeur pendant une courte fenêtre.
        deadline = time.monotonic() + self.result_window
        while not self._stop_event.is_set() and time.monotonic() < deadline:
            remaining = deadline - time.monotonic()
            transfer_socket.settimeout(min(0.2, max(0.01, remaining)))
            try:
                data, sender = transfer_socket.recvfrom(MAX_DATAGRAM)
            except (socket.timeout, OSError):
                continue

            packet = _decode(data)
            if packet is None or packet.session != session or sender[0] != peer[0]:
                continue
            if packet.type == MSG_DATA:
                ack = _Packet.encode(
                    MSG_ACK, session, packet.seq, _json_bytes({"seq": packet.seq})
                )
                self._safe_send(transfer_socket, ack, sender)
            if packet.type in (MSG_DATA, MSG_DONE):
                self._safe_send(transfer_socket, result_packet, sender)

        transfer_socket.close()

    # ------------------------------------------------------------------
    # Découverte et historique
    # ------------------------------------------------------------------

    def discover_devices(self, timeout: float = 1.0) -> list[dict[str, str | int]]:
        """Cherche les appareils QuickSend sur le réseau local."""
        session = uuid.uuid4().bytes
        sock = self._make_socket()
        sock.setsockopt(socket.SOL_SOCKET, socket.SO_BROADCAST, 1)
        probe = _Packet.encode(MSG_DISCOVER, session)
        devices: dict[str, dict[str, str | int]] = {}

        try:
            for target in ("<broadcast>", "127.0.0.1"):
                try:
                    sock.sendto(probe, (target, self.port))
                except OSError:
                    pass

            deadline = time.monotonic() + timeout
            while time.monotonic() < deadline:
                remaining = deadline - time.monotonic()
                sock.settimeout(max(0.01, remaining))
                try:
                    data, address = sock.recvfrom(MAX_DATAGRAM)
                except (socket.timeout, OSError):
                    break

                packet = _decode(data)
                if (
                    packet is None
                    or packet.type != MSG_ANNOUNCE
                    or packet.session != session
                ):
                    continue

                try:
                    info = _json_dict(packet.payload)
                except (ValueError, UnicodeDecodeError, json.JSONDecodeError):
                    continue

                ip = address[0]
                name = str(info.get("name") or ip)
                port = int(info.get("port", self.port))
                # Le même appareil peut répondre en broadcast et en loopback :
                # on écarte l'adresse locale si l'adresse LAN est déjà connue.
                if ip == "127.0.0.1" and any(
                    item["name"] == name
                    and item["port"] == port
                    and item["ip"] != "127.0.0.1"
                    for item in devices.values()
                ):
                    continue
                devices[ip] = {"name": name, "ip": ip, "port": port}
        finally:
            sock.close()

        return list(devices.values())

    def get_history(self, limit: int = 100) -> list[dict[str, str]]:
        """Retourne les transferts les plus récents."""
        with self._database() as connection:
            connection.row_factory = sqlite3.Row
            rows = connection.execute(
                """
                SELECT filename, direction, peer, status, created_at
                FROM transfers
                ORDER BY id DESC
                LIMIT ?
                """,
                (limit,),
            ).fetchall()
        return [dict(row) for row in rows]

    # ------------------------------------------------------------------
    # Utilitaires internes
    # ------------------------------------------------------------------

    @staticmethod
    def _make_socket() -> socket.socket:
        sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        try:
            sock.setsockopt(socket.SOL_SOCKET, socket.SO_RCVBUF, 1 << 20)
        except OSError:
            pass
        return sock

    @staticmethod
    def _safe_send(sock: socket.socket, payload: bytes, peer: tuple[str, int]) -> None:
        try:
            sock.sendto(payload, peer)
        except OSError:
            pass

    @staticmethod
    def _wait_for(
        sock: socket.socket,
        session: bytes,
        types: set[int],
        peer: tuple[str, int] | None = None,
        timeout: float | None = None,
    ) -> _Packet | None:
        deadline = time.monotonic() + (timeout or 0.5)
        while True:
            remaining = deadline - time.monotonic()
            if remaining <= 0:
                return None
            sock.settimeout(remaining)
            try:
                data, address = sock.recvfrom(MAX_DATAGRAM)
            except (socket.timeout, OSError):
                return None

            packet = _decode(data)
            if packet is None or packet.session != session:
                continue
            if packet.type not in types:
                continue
            if peer is not None and address[0] != peer[0]:
                continue
            return packet

    def _request(
        self,
        sock: socket.socket,
        packet: bytes,
        peer: tuple[str, int],
        session: bytes,
        types: set[int],
    ) -> _Packet:
        for _ in range(self.max_retries):
            try:
                sock.sendto(packet, peer)
            except OSError as exc:
                raise ConnectionError(str(exc)) from exc

            answer = self._wait_for(
                sock,
                session,
                types,
                peer=peer,
                timeout=self.ack_timeout,
            )
            if answer is not None:
                return answer
        raise ConnectionError("Le destinataire ne répond pas.")

    @contextmanager
    def _database(self):
        connection = sqlite3.connect(self.database_path)
        try:
            with connection:
                yield connection
        finally:
            connection.close()

    def _initialize_database(self) -> None:
        with self._database() as connection:
            connection.execute(
                """
                CREATE TABLE IF NOT EXISTS transfers (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    filename TEXT NOT NULL,
                    direction TEXT NOT NULL,
                    peer TEXT NOT NULL,
                    status TEXT NOT NULL,
                    created_at TEXT NOT NULL
                )
                """
            )

    def _record(
        self, filename: str, direction: str, peer: str, status: str
    ) -> None:
        with self._database() as connection:
            connection.execute(
                """
                INSERT INTO transfers (filename, direction, peer, status, created_at)
                VALUES (?, ?, ?, ?, ?)
                """,
                (
                    filename,
                    direction,
                    peer,
                    status,
                    datetime.now(timezone.utc).isoformat(),
                ),
            )

    def _available_destination(self, filename: str) -> Path:
        destination = self.receive_folder / filename
        if not destination.exists():
            return destination

        stem, suffix = destination.stem, destination.suffix
        index = 1
        while True:
            candidate = destination.with_name(f"{stem} ({index}){suffix}")
            if not candidate.exists():
                return candidate
            index += 1
