"""Lecture des informations réseau réelles du poste (Windows en priorité).

Les valeurs qui ne peuvent pas être lues sont remplacées par ``Indisponible`` :
aucune adresse, passerelle ou type de réseau n'est inventé ici.
"""

from __future__ import annotations

import re
import subprocess

UNAVAILABLE = "Indisponible"

_IPV4 = re.compile(
    r"(?:Adresse\s+IPv4|IPv4\s+Address)[^\n:]*:\s*"
    r"(\d{1,3}(?:\.\d{1,3}){3})",
    re.IGNORECASE,
)
# Les sorties Windows sont parfois décodées avec une autre page de code :
# seuls les mots stables sont utilisés comme repères (pas d'accent).
_MASK = re.compile(
    r"(?:Masque|Subnet\s+Mask)[^\n:]*:\s*"
    r"(\d{1,3}(?:\.\d{1,3}){3})",
    re.IGNORECASE,
)
_GATEWAY = re.compile(
    r"(?:Passerelle|Default\s+Gateway)[^\n:]*:\s*"
    r"(\d{1,3}(?:\.\d{1,3}){3})",
    re.IGNORECASE,
)


def _run(command: list[str], timeout: float = 2.0) -> str:
    flags = getattr(subprocess, "CREATE_NO_WINDOW", 0)
    result = subprocess.run(
        command,
        capture_output=True,
        text=True,
        errors="replace",
        timeout=timeout,
        check=False,
        creationflags=flags,
    )
    return result.stdout or ""


def _network_type(description: str) -> str:
    text = description.lower()
    if "wi-fi" in text or "wifi" in text or "sans fil" in text or "wireless" in text:
        return "Wi-Fi"
    if "ethernet" in text or "filaire" in text:
        return "Ethernet"
    return UNAVAILABLE


def read_interfaces() -> dict[str, dict[str, str]]:
    """Retourne {ip: {'mask', 'gateway', 'type'}} pour les cartes actives."""

    interfaces: dict[str, dict[str, str]] = {}
    try:
        output = _run(["ipconfig"])
    except (OSError, subprocess.SubprocessError):
        return interfaces

    adapter = ""
    current_ip: str | None = None
    for line in output.splitlines():
        stripped = line.strip()
        if not stripped:
            continue
        # Les intitulés de cartes ne sont pas indentés dans ipconfig.
        if not line[:1].isspace() and stripped.endswith(":"):
            adapter = stripped.rstrip(":")
            continue

        address = _IPV4.search(line)
        if address:
            current_ip = address.group(1)
            if current_ip in ("127.0.0.1", "0.0.0.0"):
                current_ip = None
                continue
            interfaces[current_ip] = {
                "mask": UNAVAILABLE,
                "gateway": UNAVAILABLE,
                "type": _network_type(adapter),
            }
            continue

        if current_ip is None:
            continue
        mask = _MASK.search(line)
        if mask:
            interfaces[current_ip]["mask"] = mask.group(1)
        gateway = _GATEWAY.search(line)
        if gateway:
            interfaces[current_ip]["gateway"] = gateway.group(1)

    return interfaces
