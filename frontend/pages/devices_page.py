"""Page « Appareils » : découverte UDP et scan des machines du WiFi."""

from __future__ import annotations

import threading

import customtkinter as ctk

from feature.transfer_service import get_local_ip


class DevicesPage(ctk.CTkFrame):
    def __init__(self, parent, service=None):
        super().__init__(parent, fg_color="transparent")
        self.service = service

        ctk.CTkLabel(
            self,
            text="Appareils connectés",
            font=("Arial", 23, "bold"),
            text_color="#142D4E",
        ).pack(anchor="w", padx=20, pady=(20, 8))

        ctk.CTkLabel(
            self,
            text="Liste des machines joignables sur votre réseau Wi-Fi local.",
            font=("Arial", 13),
            text_color="#52647A",
        ).pack(anchor="w", padx=20, pady=(0, 12))

        action_bar = ctk.CTkFrame(self, fg_color="transparent")
        action_bar.pack(fill="x", padx=20)

        self.refresh_button = ctk.CTkButton(
            action_bar,
            text="Rechercher des appareils",
            height=38,
            fg_color="#1769D2",
            hover_color="#1255AD",
            command=self.refresh,
        )
        self.refresh_button.pack(side="left")

        self.status_label = ctk.CTkLabel(
            action_bar,
            text=f"Adresse locale : {get_local_ip()}",
            font=("Arial", 11),
            text_color="#718096",
        )
        self.status_label.pack(side="left", padx=15)

        ctk.CTkLabel(
            self,
            text="ℹ Seuls les appareils avec QuickSend lancé peuvent recevoir un fichier.",
            font=("Arial", 11),
            text_color="#718096",
        ).pack(anchor="w", padx=20, pady=(6, 0))

        self.devices_frame = ctk.CTkScrollableFrame(
            self,
            fg_color="white",
            corner_radius=12,
            border_width=1,
            border_color="#DCE5F2",
        )
        self.devices_frame.pack(fill="both", expand=True, padx=20, pady=12)

        self.refresh()

    # ------------------------------------------------------------------
    # Découverte
    # ------------------------------------------------------------------

    def _alive(self) -> bool:
        try:
            return bool(self.winfo_exists())
        except Exception:
            return False

    def refresh(self) -> None:
        self.refresh_button.configure(state="disabled", text="Analyse en cours...")
        self.status_label.configure(text="Analyse du réseau Wi-Fi...")
        threading.Thread(target=self._discover, daemon=True).start()

    def _discover(self) -> None:
        try:
            devices = self.service.scan_network(timeout=6.0) if self.service else []
        except Exception:  # noqa: BLE001 - l'interface reste utilisable
            devices = self.service.discover_devices(timeout=1.5) if self.service else []
        try:
            self.after(0, lambda: self._show_devices(devices))
        except Exception:
            pass

    # ------------------------------------------------------------------
    # Affichage
    # ------------------------------------------------------------------

    def _show_devices(self, devices) -> None:
        if not self._alive():
            return

        for widget in list(self.devices_frame.winfo_children()):
            widget.destroy()

        quicksend = [item for item in devices if item.get("kind") == "quicksend"]
        others = [item for item in devices if item.get("kind") != "quicksend"]

        self.refresh_button.configure(state="normal", text="Rechercher des appareils")
        self.status_label.configure(
            text=f"{len(devices)} appareil(s) · {len(quicksend)} QuickSend · {get_local_ip()}"
        )

        if not devices:
            ctk.CTkLabel(
                self.devices_frame,
                text=(
                    "Aucun appareil joignable.\n"
                    "Vérifiez que vous êtes sur le même Wi-Fi et que le pare-feu "
                    "autorise les ping."
                ),
                font=("Arial", 14),
                text_color="#718096",
                wraplength=650,
                justify="center",
            ).pack(pady=50)
            return

        if quicksend:
            self._section(f"Appareils QuickSend ({len(quicksend)}) - réception possible")
            for device in quicksend:
                self._card(device, ready=True)

        if others:
            self._section(f"Autres appareils du Wi-Fi ({len(others)})")
            for device in others:
                self._card(device, ready=False)

    def _section(self, title: str) -> None:
        ctk.CTkLabel(
            self.devices_frame,
            text=title,
            font=("Arial", 13, "bold"),
            text_color="#142D4E",
            anchor="w",
        ).pack(fill="x", padx=6, pady=(12, 4))

    def _card(self, device: dict, ready: bool) -> None:
        card = ctk.CTkFrame(
            self.devices_frame,
            fg_color="#F3F6FA",
            corner_radius=10,
            border_width=1,
            border_color="#DCE5F2",
        )
        card.pack(fill="x", pady=5, padx=4)

        ctk.CTkLabel(
            card,
            text=f"◆ {device['name']}",
            font=("Arial", 14, "bold"),
            text_color="#142D4E",
            anchor="w",
        ).pack(fill="x", padx=15, pady=(10, 2))

        detail = f"IP : {device['ip']}"
        if ready:
            detail += f"    Port UDP : {device['port']}"
        ctk.CTkLabel(
            card,
            text=detail,
            font=("Arial", 12),
            text_color="#52647A",
            anchor="w",
        ).pack(fill="x", padx=15, pady=(0, 4))

        ctk.CTkLabel(
            card,
            text="● Prêt à recevoir" if ready else "● QuickSend non installé / non lancé",
            font=("Arial", 11, "bold"),
            text_color="#168653" if ready else "#D18A20",
            anchor="w",
        ).pack(fill="x", padx=15, pady=(0, 10))
