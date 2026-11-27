"""Point d'entrée de QuickSend LAN (interface graphique ou ligne de commande)."""

from __future__ import annotations

import argparse
import socket
import sys
import time
from pathlib import Path

from feature.transfer_service import (
    TransferService,
    find_available_udp_port,
    get_local_ip,
)

BASE_DIR = (
    Path(sys.executable).resolve().parent
    if getattr(sys, "frozen", False)
    else Path(__file__).resolve().parent
)
DEFAULT_FOLDER = Path.home() / "Downloads" / "QuickSend"
DEFAULT_DATABASE = BASE_DIR / "quicksend.db"


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description="QuickSend LAN - transfert de fichiers sur le réseau local en UDP."
    )
    parser.add_argument(
        "--mode",
        choices=("gui", "receive", "send", "discover"),
        default="gui",
        help="mode de fonctionnement (défaut : gui)",
    )
    parser.add_argument("--port", type=int, default=5000, help="port UDP (défaut : 5000)")
    parser.add_argument(
        "--folder",
        default=str(DEFAULT_FOLDER),
        help="dossier de réception (défaut : ~/Downloads/QuickSend)",
    )
    parser.add_argument(
        "--db",
        default=str(DEFAULT_DATABASE),
        help="chemin de la base SQLite (défaut : ./quicksend.db)",
    )
    parser.add_argument(
        "--name",
        default=socket.gethostname(),
        help="nom de l'appareil annoncé sur le réseau",
    )
    parser.add_argument("--file", help="fichier à envoyer (mode send)")
    parser.add_argument("--to", dest="host", help="adresse IP du destinataire (mode send)")
    parser.add_argument(
        "--discover-timeout",
        type=float,
        default=2.0,
        help="durée de la recherche d'appareils en secondes",
    )
    return parser


def _service_from_args(args: argparse.Namespace) -> TransferService:
    return TransferService(
        receive_folder=args.folder,
        database_path=args.db,
        port=args.port,
        device_name=args.name,
    )


def _print_progress(sent: int, total: int) -> None:
    percent = int(sent * 100 / total) if total else 100
    print(f"\rTransfert : {percent}% ({sent}/{total} octets)", end="", flush=True)


def main(argv: list[str] | None = None) -> int:
    args = build_parser().parse_args(argv)

    # Sur une machine où un autre QuickSend (ou un autre programme) occupe déjà
    # le port, on bascule sur un port voisin plutôt que de refuser de démarrer.
    if args.mode in {"gui", "receive"}:
        available_port = find_available_udp_port(args.port)
        if available_port != args.port:
            print(f"Port UDP {args.port} occupé, utilisation du port {available_port}.")
            args.port = available_port

    if args.mode == "gui":
        try:
            from frontend.windows.main_window import MainWindow
        except ImportError as exc:
            raise SystemExit(
                "Interface graphique indisponible. Installez les dépendances avec :\n"
                "  python -m pip install -r requirements.txt\n"
                f"Détail : {exc}"
            ) from exc

        app = MainWindow(
            receive_folder=args.folder,
            database_path=args.db,
            port=args.port,
            device_name=args.name,
        )
        app.mainloop()
        return 0

    service = _service_from_args(args)

    if args.mode == "receive":
        service.start()
        print(
            f"QuickSend LAN en écoute sur le port UDP {service.port}\n"
            f"Adresse IP locale : {get_local_ip()}\n"
            f"Dossier de réception : {service.receive_folder}\n"
            "Appuyez sur Ctrl+C pour arrêter."
        )
        try:
            while True:
                time.sleep(1)
        except KeyboardInterrupt:
            print("\nArrêt du service de réception.")
        finally:
            service.stop()
        return 0

    if args.mode == "send":
        if not args.file or not args.host:
            raise SystemExit("Les options --file et --to sont obligatoires en mode send.")
        source = Path(args.file).expanduser()
        if not source.is_file():
            raise SystemExit(f"Fichier introuvable : {source}")
        try:
            service.send_file(source, args.host, progress=_print_progress)
        except (OSError, RuntimeError, ValueError) as exc:
            print(f"\nÉchec du transfert : {exc}", file=sys.stderr)
            return 1
        print(f"\nFichier '{source.name}' envoyé à {args.host}.")
        return 0

    print("Appareils QuickSend détectés :")
    devices = service.discover_devices(timeout=args.discover_timeout)
    if not devices:
        print("  Aucun appareil (vérifiez qu'un récepteur est démarré).")
    for device in devices:
        print(f"  - {device['name']}  {device['ip']}:{device['port']}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
