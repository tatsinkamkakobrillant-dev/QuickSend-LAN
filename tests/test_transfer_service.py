"""Tests d'intégration du transfert UDP (aucun réseau externe requis)."""

from __future__ import annotations

import hashlib
import ipaddress
import os
import socket
import tempfile
import threading
import unittest
from pathlib import Path

from feature import transfer_service as ts
from feature.transfer_service import TransferService


def _free_port() -> int:
    with socket.socket(socket.AF_INET, socket.SOCK_DGRAM) as probe:
        probe.bind(("127.0.0.1", 0))
        return probe.getsockname()[1]


class TransferServiceTests(unittest.TestCase):
    def setUp(self) -> None:
        self.tmp = tempfile.TemporaryDirectory()
        self.root = Path(self.tmp.name)
        self.received_dir = self.root / "received"
        self.sent_dir = self.root / "sent"
        self.sent_dir.mkdir()

        self.port = _free_port()
        self.service = TransferService(
            self.received_dir,
            self.root / "quicksend.db",
            self.port,
            device_name="PC-TEST",
            ack_timeout=0.2,
            max_retries=10,
        )
        self.service.start()

    def tearDown(self) -> None:
        self.service.stop()
        self.tmp.cleanup()

    def _make_file(self, name: str, content: bytes) -> Path:
        path = self.sent_dir / name
        path.write_bytes(content)
        return path

    def test_small_text_file(self) -> None:
        content = b"Bonjour QuickSend UDP !\n" * 20
        source = self._make_file("bonjour.txt", content)

        self.service.send_file(source, "127.0.0.1")

        target = self.received_dir / "bonjour.txt"
        self.assertTrue(target.exists())
        self.assertEqual(target.read_bytes(), content)

        directions = {(row["direction"], row["status"]) for row in self.service.get_history()}
        self.assertIn(("envoyé", "terminé"), directions)
        self.assertIn(("reçu", "terminé"), directions)

    def test_large_binary_file(self) -> None:
        content = os.urandom(700_000)
        source = self._make_file("image.bin", content)

        self.service.send_file(source, "127.0.0.1")

        target = self.received_dir / "image.bin"
        self.assertEqual(target.stat().st_size, len(content))
        self.assertEqual(
            hashlib.sha256(target.read_bytes()).hexdigest(),
            hashlib.sha256(content).hexdigest(),
        )

    def test_empty_file(self) -> None:
        source = self._make_file("vide.txt", b"")

        self.service.send_file(source, "127.0.0.1")

        target = self.received_dir / "vide.txt"
        self.assertTrue(target.exists())
        self.assertEqual(target.read_bytes(), b"")

    def test_duplicate_name_is_renamed(self) -> None:
        source = self._make_file("rapport.pdf", b"%PDF-1.4 rapport")

        self.service.send_file(source, "127.0.0.1")
        self.service.send_file(source, "127.0.0.1")

        self.assertTrue((self.received_dir / "rapport.pdf").exists())
        self.assertTrue((self.received_dir / "rapport (1).pdf").exists())

    def test_discovery_finds_local_receiver(self) -> None:
        devices = self.service.discover_devices(timeout=0.8)

        self.assertTrue(
            any(device["name"] == "PC-TEST" for device in devices),
            msg=f"Appareils découverts : {devices}",
        )

    def test_discovery_uses_every_local_network_broadcast(self) -> None:
        sent: list[tuple[str, int]] = []

        class FakeSocket:
            def setsockopt(self, *_args) -> None:
                pass

            def sendto(self, _payload: bytes, target: tuple[str, int]) -> None:
                sent.append(target)

            def settimeout(self, _value: float) -> None:
                pass

            def recvfrom(self, _size: int):
                raise socket.timeout

            def close(self) -> None:
                pass

        interfaces = [
            ("192.168.10.5", ipaddress.ip_network("192.168.10.0/24")),
            ("10.0.0.8", ipaddress.ip_network("10.0.0.0/24")),
        ]
        original_interfaces = ts._local_ipv4_interfaces
        original_socket = self.service._make_socket
        ts._local_ipv4_interfaces = lambda: interfaces
        self.service._make_socket = lambda: FakeSocket()

        try:
            devices = self.service.discover_devices(timeout=0.05)
        finally:
            ts._local_ipv4_interfaces = original_interfaces
            self.service._make_socket = original_socket

        self.assertEqual(devices, [])
        self.assertIn(("192.168.10.255", self.service.port), sent)
        self.assertIn(("10.0.0.255", self.service.port), sent)
        self.assertIn(("<broadcast>", self.service.port), sent)
        self.assertIn(("127.0.0.1", self.service.port), sent)

    def test_scan_network_marks_quickSend_and_other_devices(self) -> None:
        interfaces = [("192.168.50.10", ipaddress.ip_network("192.168.50.0/24"))]
        original_interfaces = ts._local_ipv4_interfaces
        original_discover = self.service.discover_devices
        original_ping = self.service._ping

        ts._local_ipv4_interfaces = lambda: interfaces
        self.service.discover_devices = lambda timeout=1.0: [
            {"name": "PC-QUICKSEND", "ip": "192.168.50.20", "port": 5000}
        ]
        self.service._ping = lambda host, timeout=0.5: host in {
            "192.168.50.20",
            "192.168.50.30",
        }

        try:
            devices = self.service.scan_network(timeout=0.2)
        finally:
            ts._local_ipv4_interfaces = original_interfaces
            self.service.discover_devices = original_discover
            self.service._ping = original_ping

        by_ip = {str(device["ip"]): device for device in devices}
        self.assertEqual(by_ip["192.168.50.20"]["kind"], "quicksend")
        self.assertEqual(by_ip["192.168.50.20"]["name"], "PC-QUICKSEND")
        self.assertEqual(by_ip["192.168.50.30"]["kind"], "network")
        self.assertNotIn("192.168.50.10", by_ip)

    def test_lost_datagram_is_retransmitted(self) -> None:
        content = (
            "Le premier paquet sera perdu, mais le transfert doit réussir." * 40
        ).encode("utf-8")
        source = self._make_file("perte.txt", content)
        original_decode = ts._decode
        state = {"dropped": False}

        def flaky_decode(data: bytes):
            packet = original_decode(data)
            if packet and packet.type == ts.MSG_DATA and not state["dropped"]:
                state["dropped"] = True
                return None
            return packet

        ts._decode = flaky_decode
        try:
            self.service.send_file(source, "127.0.0.1")
        finally:
            ts._decode = original_decode

        self.assertTrue(state["dropped"])
        self.assertEqual((self.received_dir / "perte.txt").read_bytes(), content)

    def test_two_concurrent_transfers(self) -> None:
        first = self._make_file("a.txt", b"A" * 5_000)
        second = self._make_file("b.txt", b"B" * 7_000)
        errors: list[Exception] = []

        def send(path: Path) -> None:
            try:
                self.service.send_file(path, "127.0.0.1")
            except Exception as exc:  # noqa: BLE001
                errors.append(exc)

        threads = [
            threading.Thread(target=send, args=(first,)),
            threading.Thread(target=send, args=(second,)),
        ]
        for thread in threads:
            thread.start()
        for thread in threads:
            thread.join(timeout=30)

        self.assertFalse(errors, msg=f"Erreurs de transfert : {errors}")
        self.assertEqual((self.received_dir / "a.txt").read_bytes(), b"A" * 5_000)
        self.assertEqual((self.received_dir / "b.txt").read_bytes(), b"B" * 7_000)

    def test_invalid_ip_is_rejected(self) -> None:
        source = self._make_file("test.txt", b"contenu")

        with self.assertRaises(ValueError):
            self.service.send_file(source, "pas-une-ip")

    def test_progress_callback(self) -> None:
        content = os.urandom(5_000)
        source = self._make_file("progres.bin", content)
        updates: list[tuple[int, int]] = []

        self.service.send_file(
            source,
            "127.0.0.1",
            progress=lambda sent, total: updates.append((sent, total)),
        )

        self.assertTrue(updates)
        self.assertEqual(updates[-1], (len(content), len(content)))


if __name__ == "__main__":
    unittest.main()
