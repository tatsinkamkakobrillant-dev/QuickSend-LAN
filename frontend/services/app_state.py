"""État applicatif partagé : service UDP, réseau, appareils et historique.

Toutes les valeurs affichées par l'interface proviennent de ce module. Quand
une information ne peut pas être obtenue, la constante ``UNAVAILABLE`` est
utilisée : aucune valeur de démonstration n'est mêlée aux données réelles.
"""

from __future__ import annotations

import importlib.machinery
import importlib.util
import sqlite3
import sys
import threading
import tkinter as tk
from dataclasses import dataclass
from datetime import datetime
from pathlib import Path
from typing import Any, Callable

from frontend.services import system_info
from frontend.services.constants import UNAVAILABLE
from frontend.services.transfer_manager import TransferManager

PROJECT_ROOT = Path(__file__).resolve().parents[2]
DATABASE_PATH = PROJECT_ROOT / "quicksend.db"
DEFAULT_FOLDER = Path.home() / "Downloads" / "QuickSend"
DEFAULT_PORT = 5000


@dataclass
class AppSettings:
    """Options prises en charge par le backend (session en cours)."""

    receive_folder: Path = DEFAULT_FOLDER
    udp_port: int = DEFAULT_PORT


def _load_backend_module():
    """Charge le service UDP, y compris depuis son fichier compilé si besoin."""

    name = "feature.transfer_service"
    try:
        return importlib.import_module(name)
    except Exception:
        pass

    cache = PROJECT_ROOT / "feature" / "__pycache__"
    candidates = sorted(
        cache.glob("transfer_service.cpython-*.pyc"),
        key=lambda path: path.stat().st_mtime,
        reverse=True,
    )
    for candidate in candidates:
        try:
            sys.modules.pop(name, None)
            loader = importlib.machinery.SourcelessFileLoader(name, str(candidate))
            spec = importlib.util.spec_from_loader(name, loader)
            if spec is None:
                continue
            module = importlib.util.module_from_spec(spec)
            sys.modules[name] = module
            loader.exec_module(module)
            return module
        except Exception:
            sys.modules.pop(name, None)
    return None


def run_async(
    master: tk.Misc,
    worker: Callable[[], Any],
    callback: Callable[[Any, BaseException | None], None],
) -> None:
    """Exécute ``worker`` hors du thread Tk puis rapporte le résultat dans Tk."""

    def target():
        result: Any = None
        error: BaseException | None = None
        try:
            result = worker()
        except BaseException as exc:  # rapporté à l'interface, jamais silencieux
            error = exc

        def done():
            try:
                callback(result, error)
            except tk.TclError:
                pass  # la vue a été fermée pendant le traitement

        try:
            master.after(0, done)
        except (tk.TclError, RuntimeError):
            # L'application peut être fermée pendant qu'un thread travaille.
            pass

    threading.Thread(target=target, daemon=True).start()


class AppState:
    """Source unique de vérité utilisée par toutes les vues."""

    def __init__(self):
        self.settings = AppSettings()
        self._module = _load_backend_module()
        self.service = None
        self.startup_error: str | None = None
        self.actual_port: int = self.settings.udp_port

        self.devices: list[dict[str, Any]] = []
        self.devices_error: str | None = None
        self.devices_updated: float = 0.0

        self.history: list[dict[str, str]] = []
        self.history_error: str | None = None

        self.transfers: TransferManager | None = None
        self._network: dict[str, str] | None = None

    # ------------------------------------------------------------------
    # Service UDP
    # ------------------------------------------------------------------
    def start(self) -> None:
        if self._module is None:
            self.startup_error = "Module de transfert UDP introuvable"
            return

        try:
            receive_folder = str(self.settings.receive_folder)
            Path(receive_folder).mkdir(parents=True, exist_ok=True)
            finder = getattr(self._module, "find_available_udp_port", None)
            port = (
                int(finder(self.settings.udp_port))
                if finder is not None
                else self.settings.udp_port
            )
            service = self._module.TransferService(
                receive_folder,
                database_path=str(DATABASE_PATH),
                port=port,
            )
            service.start()
            self.service = service
            self.actual_port = int(service.port)
            self.transfers = TransferManager(service)
        except Exception as exc:
            self.startup_error = str(exc) or type(exc).__name__

    @property
    def running(self) -> bool:
        return bool(self.service and getattr(self.service, "is_running", False))

    @property
    def port(self) -> int:
        return self.actual_port if self.service else self.settings.udp_port

    def status(self) -> tuple[str, str, str]:
        """(libellé, détail, couleur) pour le badge de connexion."""

        if self._module is None:
            return ("Indisponible", "Service de transfert non chargé", "#A85C00")
        if self.startup_error:
            return ("Hors ligne", f"Service UDP arrêté : {self.startup_error}", "#A4252B")
        if not self.running:
            return ("Hors ligne", "Service UDP arrêté", "#A4252B")
        if self.local_ip() == UNAVAILABLE:
            return ("Connexion limitée", "Aucune adresse IPv4 locale", "#A85C00")
        return ("En ligne", f"Écoute UDP active sur le port {self.port}", "#0A720B")

    def local_ip(self) -> str:
        getter = getattr(self._module, "get_local_ip", None) if self._module else None
        try:
            address = getter() if getter else UNAVAILABLE
        except Exception:
            address = UNAVAILABLE
        if address and address != UNAVAILABLE:
            return address

        for ip in system_info.read_interfaces():
            return ip
        return UNAVAILABLE

    def send_file(self, file_path: str, host: str, progress=None) -> None:
        if not self.running:
            raise RuntimeError("Le service de transfert UDP n'est pas actif.")
        self.service.send_file(file_path, host, progress=progress)

    def send_files(self, paths: list[str], host: str) -> list[int]:
        """Prépare l'envoi de plusieurs fichiers et retourne leurs identifiants."""

        if not self.running or self.transfers is None:
            raise RuntimeError("Le service de transfert UDP n'est pas actif.")
        return self.transfers.begin_send(paths, host)

    # ------------------------------------------------------------------
    # Paramètres
    # ------------------------------------------------------------------
    def configure(self, receive_folder: str | Path | None = None, udp_port: int | None = None) -> None:
        if receive_folder:
            folder = Path(receive_folder).expanduser()
            folder.mkdir(parents=True, exist_ok=True)
            self.settings.receive_folder = folder
        if udp_port is not None:
            self.settings.udp_port = int(udp_port)

        if self.service is not None:
            finder = getattr(self._module, "find_available_udp_port", None)
            port = (
                int(finder(self.settings.udp_port))
                if finder is not None
                else self.settings.udp_port
            )
            self.service.configure(
                receive_folder=str(self.settings.receive_folder), port=port
            )
            self.actual_port = int(self.service.port)
        else:
            self.start()

    def shutdown(self) -> None:
        if self.transfers is not None:
            try:
                self.transfers.cancel_all()
                self.transfers.detach()
            except Exception:
                pass
            self.transfers = None
        if self.service is not None:
            try:
                self.service.stop()
            except Exception:
                pass
            self.service = None

    # ------------------------------------------------------------------
    # Réseau
    # ------------------------------------------------------------------
    def network_info(self) -> dict[str, str]:
        if self._network is not None:
            return dict(self._network)

        ip = self.local_ip()
        mask = UNAVAILABLE
        network = UNAVAILABLE

        interfaces_getter = (
            getattr(self._module, "_local_ipv4_interfaces", None)
            if self._module
            else None
        )
        if interfaces_getter:
            try:
                for address, ipv4_network in interfaces_getter():
                    if str(address) == ip:
                        mask = str(ipv4_network.netmask)
                        network = str(ipv4_network)
                        break
            except Exception:
                pass

        details = system_info.read_interfaces().get(ip, {})
        if mask == UNAVAILABLE:
            mask = details.get("mask", UNAVAILABLE)

        self._network = {
            "ip": ip,
            "port": str(self.port),
            "mask": mask,
            "gateway": details.get("gateway", UNAVAILABLE),
            "type": details.get("type", UNAVAILABLE),
            "network": network,
        }
        return dict(self._network)

    def refresh_network(self) -> dict[str, str]:
        self._network = None
        return self.network_info()

    # ------------------------------------------------------------------
    # Appareils
    # ------------------------------------------------------------------
    def discover_devices(self, timeout: float = 1.0) -> list[dict[str, Any]]:
        if self._module is None:
            raise RuntimeError("Module de découverte indisponible.")
        service = self.service
        if service is None:
            raise RuntimeError("Le service UDP n'est pas démarré.")

        devices = service.discover_devices(timeout=timeout)
        return [
            {
                "name": str(device.get("name") or device.get("ip") or UNAVAILABLE),
                "ip": str(device.get("ip", UNAVAILABLE)),
                "port": int(device.get("port") or self.port),
            }
            for device in devices
        ]

    def refresh_devices_async(
        self,
        master: tk.Misc,
        callback: Callable[[list[dict[str, Any]], str | None, BaseException | None], None],
        timeout: float = 1.0,
        force: bool = False,
    ) -> bool:
        """Lance une découverte ; retourne False si une recherche est déjà fraîche."""

        import time

        if not force and self.devices_updated and time.monotonic() - self.devices_updated < 25:
            callback(list(self.devices), self.devices_error, None)
            return False

        def worker():
            return self.discover_devices(timeout=timeout)

        def done(result, error):
            import time

            if error is None:
                self.devices = result
                self.devices_error = None
                self.devices_updated = time.monotonic()
            else:
                self.devices_error = str(error) or type(error).__name__
            callback(list(self.devices), self.devices_error, error)

        run_async(master, worker, done)
        return True

    # ------------------------------------------------------------------
    # Historique
    # ------------------------------------------------------------------
    def get_history(self, limit: int = 1000) -> list[dict[str, str]]:
        if self.service is not None:
            rows = self.service.get_history(limit=limit)
            return [dict(row) for row in rows]

        connection = sqlite3.connect(DATABASE_PATH)
        try:
            connection.row_factory = sqlite3.Row
            rows = connection.execute(
                "SELECT filename, direction, peer, status, created_at "
                "FROM transfers ORDER BY id DESC LIMIT ?",
                (limit,),
            ).fetchall()
            return [dict(row) for row in rows]
        finally:
            connection.close()

    def transfer_count(self) -> int:
        try:
            connection = sqlite3.connect(DATABASE_PATH)
            try:
                return int(connection.execute("SELECT COUNT(*) FROM transfers").fetchone()[0])
            finally:
                connection.close()
        except sqlite3.Error:
            return len(self.history)

    def refresh_history_async(
        self,
        master: tk.Misc,
        callback: Callable[[list[dict[str, str]], str | None, BaseException | None], None],
    ) -> None:
        def worker():
            return self.get_history()

        def done(result, error):
            if error is None:
                self.history = result
                self.history_error = None
            else:
                self.history_error = str(error) or type(error).__name__
            callback(list(self.history), self.history_error, error)

        run_async(master, worker, done)

    @staticmethod
    def format_time(value: str) -> str:
        """Heure locale lisible à partir d'un horodatage ISO de la base."""

        try:
            parsed = datetime.fromisoformat(value)
            return parsed.astimezone().strftime("%H:%M")
        except (ValueError, TypeError):
            return UNAVAILABLE
