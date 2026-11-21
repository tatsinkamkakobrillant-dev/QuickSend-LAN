"""Page « Appareils » : découverte UDP des autres machines du LAN."""

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
            text="Retrouvez les ordinateurs QuickSend disponibles sur votre réseau local.",
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

        self.devices_frame = ctk.CTkScrollableFrame(
            self,
            fg_color="white",
            corner_radius=12,
            border_width=1,
            border_color="#DCE5F2",
        )
        self.devices_frame.pack(fill="both", expand=True, padx=20, pady=12)

        self.refresh()

    def _alive(self) -> bool:
        try:
            return bool(self.winfo_exists())
        except Exception:
            return False

    def refresh(self) -> None:
        self.refresh_button.configure(state="disabled", text="Recherche en cours...")
        self.status_label.configure(text="Recherche des appareils sur le LAN...")
        threading.Thread(target=self._discover, daemon=True).start()

    def _discover(self) -> None:
        devices = self.service.discover_devices(timeout=1.5) if self.service else []
        try:
            self.after(0, lambda: self._show_devices(devices))
        except Exception:
            pass

    def _show_devices(self, devices) -> None:
        if not self._alive():
            return

        for widget in list(self.devices_frame.winfo_children()):
            widget.destroy()

        self.refresh_button.configure(state="normal", text="Rechercher des appareils")
        self.status_label.configure(
            text=f"{len(devices)} appareil(s) détecté(s) · {get_local_ip()}"
        )

        if not devices:
            ctk.CTkLabel(
                self.devices_frame,
                text="Aucun appareil détecté. Vérifiez que le récepteur est actif sur l'autre machine.",
                font=("Arial", 14),
                text_color="#718096",
                wraplength=650,
            ).pack(pady=40)
            return

        for device in devices:
            card = ctk.CTkFrame(
                self.devices_frame,
                fg_color="#F3F6FA",
                corner_radius=10,
                border_width=1,
                border_color="#DCE5F2",
            )
            card.pack(fill="x", pady=6, padx=4)

            ctk.CTkLabel(
                card,
                text=f"◆ {device['name']}",
                font=("Arial", 14, "bold"),
                text_color="#142D4E",
                anchor="w",
            ).pack(fill="x", padx=15, pady=(10, 2))
            ctk.CTkLabel(
                card,
                text=f"IP : {device['ip']}    Port UDP : {device['port']}",
                font=("Arial", 12),
                text_color="#52647A",
                anchor="w",
            ).pack(fill="x", padx=15, pady=(0, 10))
