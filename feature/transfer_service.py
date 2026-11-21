from __future__ import annotations

import json
import os
import socket
import sqlite3
import struct
import tempfile
import threading
from datetime import datetime, timezone
from pathlib import Path


class TransferService:
    """Réception TCP, envoi de fichiers et historique SQLite."""

    CHUNK_SIZE = 64 * 1024
    MAX_HEADER_SIZE = 64 * 1024

    def __init__(
        self,
        receive_folder: str | Path,
        database_path: str | Path = "quicksend.db",
        port: int = 5000,
    ) -> None:
        if not 1 <= port <= 65535:
            raise ValueError("Le port doit être compris entre 1 et 65535.")

        self.receive_folder = Path(receive_folder).expanduser()
        self.receive_folder.mkdir(parents=True, exist_ok=True)
        self.database_path = Path(database_path)
        self.port = port

        self._stop_event = threading.Event()
        self._server_socket: socket.socket | None = None
        self._server_thread: threading.Thread | None = None

        self._initialize_database()

    def start(self) -> None:
        """Démarre le serveur de réception dans un thread."""
        if self._server_thread and self._server_thread.is_alive():
            return

        self._stop_event.clear()
        server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        server.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        server.bind(("0.0.0.0", self.port))
        server.listen()
        server.settimeout(1.0)

        self._server_socket = server
        self._server_thread = threading.Thread(
            target=self._serve,
            name="QuickSendReceiver",
            daemon=True,
        )
        self._server_thread.start()

    def stop(self) -> None:
        """Arrête le serveur de réception."""
        self._stop_event.set()
        if self._server_socket:
            self._server_socket.close()
            self._server_socket = None
        if self._server_thread:
            self._server_thread.join(timeout=2)
            self._server_thread = None

    def send_file(self, file_path: str | Path, host: str) -> None:
        """Envoie un fichier à l'adresse IP fournie, ou lève une exception."""
        path = Path(file_path)
        if not path.is_file():
            raise FileNotFoundError(f"Fichier introuvable : {path}")

        size = path.stat().st_size
        metadata = json.dumps(
            {"name": path.name, "size": size}
        ).encode("utf-8")

        try:
            with socket.create_connection((host, self.port), timeout=10) as conn:
                conn.sendall(struct.pack("!I", len(metadata)))
                conn.sendall(metadata)

                with path.open("rb") as file:
                    while chunk := file.read(self.CHUNK_SIZE):
                        conn.sendall(chunk)

                response = self._receive_response(conn)
        except OSError as exc:
            self._record(path.name, "envoyé", host, "échec")
            raise ConnectionError(f"Échec de l'envoi vers {host}: {exc}") from exc

        if not response.get("ok"):
            reason = response.get("error", "Erreur de réception")
            self._record(path.name, "envoyé", host, "échec")
            raise RuntimeError(reason)

        self._record(path.name, "envoyé", host, "terminé")

    def get_history(self, limit: int = 100) -> list[dict[str, str]]:
        """Retourne les transferts les plus récents."""
        with sqlite3.connect(self.database_path) as connection:
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

    def _serve(self) -> None:
        while not self._stop_event.is_set():
            server = self._server_socket
            if server is None:
                break
            try:
                conn, address = server.accept()
            except socket.timeout:
                continue
            except OSError:
                if self._stop_event.is_set():
                    break
                raise

            threading.Thread(
                target=self._handle_client,
                args=(conn, address[0]),
                daemon=True,
            ).start()

    def _handle_client(self, conn: socket.socket, host: str) -> None:
        temporary_path: str | None = None
        filename = "fichier inconnu"

        try:
            with conn:
                header_size = struct.unpack("!I", self._read_exact(conn, 4))[0]
                if not 1 <= header_size <= self.MAX_HEADER_SIZE:
                    raise ValueError("En-tête de transfert invalide.")

                metadata = json.loads(self._read_exact(conn, header_size))
                filename = Path(metadata["name"]).name
                size = int(metadata["size"])

                if not filename or size < 0:
                    raise ValueError("Nom ou taille de fichier invalide.")

                destination = self._available_destination(filename)
                with tempfile.NamedTemporaryFile(
                    mode="wb",
                    dir=self.receive_folder,
                    prefix=".quicksend-",
                    delete=False,
                ) as temporary:
                    temporary_path = temporary.name
                    remaining = size
                    while remaining:
                        chunk = conn.recv(min(self.CHUNK_SIZE, remaining))
                        if not chunk:
                            raise ConnectionError("Transfert interrompu.")
                        temporary.write(chunk)
                        remaining -= len(chunk)

                os.replace(temporary_path, destination)
                temporary_path = None
                self._record(filename, "reçu", host, "terminé")
                self._send_response(conn, {"ok": True})

        except (OSError, ValueError, KeyError, TypeError, json.JSONDecodeError) as exc:
            if temporary_path and os.path.exists(temporary_path):
                os.unlink(temporary_path)
            self._record(filename, "reçu", host, "échec")
            try:
                self._send_response(conn, {"ok": False, "error": str(exc)})
            except OSError:
                pass

    def _initialize_database(self) -> None:
        self.database_path.parent.mkdir(parents=True, exist_ok=True)
        with sqlite3.connect(self.database_path) as connection:
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
        with sqlite3.connect(self.database_path) as connection:
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

    @staticmethod
    def _read_exact(conn: socket.socket, size: int) -> bytes:
        data = bytearray()
        while len(data) < size:
            chunk = conn.recv(size - len(data))
            if not chunk:
                raise ConnectionError("Connexion interrompue.")
            data.extend(chunk)
        return bytes(data)

    @classmethod
    def _send_response(cls, conn: socket.socket, response: dict) -> None:
        payload = json.dumps(response).encode("utf-8")
        conn.sendall(struct.pack("!I", len(payload)) + payload)

    @classmethod
    def _receive_response(cls, conn: socket.socket) -> dict:
        size = struct.unpack("!I", cls._read_exact(conn, 4))[0]
        if not 1 <= size <= cls.MAX_HEADER_SIZE:
            raise ValueError("Réponse du destinataire invalide.")
        return json.loads(cls._read_exact(conn, size))