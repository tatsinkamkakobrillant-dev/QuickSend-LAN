"""Pied de page : adresse IP, port UDP et informations réseau."""

from __future__ import annotations

import customtkinter as ctk

from feature.transfer_service import get_local_ip


class Footer(ctk.CTkFrame):
    def __init__(self, parent, port=5000):
        super().__init__(
            parent,
            fg_color="#142D4E",
            corner_radius=10,
            height=48,
        )

        self.pack_propagate(False)
        self.port = port

        information = [
            f"Adresse IP : {get_local_ip()}",
            f"Port UDP : {self.port}",
            "Réseau : Local (LAN)",
            "QuickSend LAN © 2026",
        ]
        self.labels = []
        for info in information:
            label = ctk.CTkLabel(
                self,
                text=info,
                font=("Arial", 11),
                text_color="white",
            )
            label.pack(side="left", padx=15, expand=True)
            self.labels.append(label)

    def set_port(self, port: int) -> None:
        self.port = port
        self.labels[1].configure(text=f"Port UDP : {port}")
