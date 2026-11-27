<<<<<<< HEAD
"""Pied de page sombre occupant toute la largeur de la fenêtre."""

import customtkinter as ctk

from frontend.components.icons import get_icon


class Footer(ctk.CTkFrame):

    def __init__(self, parent):
        super().__init__(parent, fg_color="#01234F",
                         corner_radius=0, height=42)
        self.pack_propagate(False)

        divider = ctk.CTkFrame(self, fg_color="#607093",
                               corner_radius=0, height=1)
        divider.place(x=0, y=0, relwidth=1)

        ctk.CTkLabel(
            self, text="QuickSend LAN @ 2026 - Projet Licence 3",
            font=("Segoe UI", 10),
            text_color="#D8E4F7"
        ).place(x=20, y=12)

        ctk.CTkLabel(
            self, text="Un réseau local plus connecté !",
            font=("Segoe UI", 10),
            text_color="#D8E4F7",
            anchor="e",
            width=230
        ).place(relx=1, x=-58, y=12, anchor="ne")

        chevron = ctk.CTkLabel(
            self, text="",
            image=get_icon("chevron", "#3691F4", 16),
            fg_color="transparent"
        )
        chevron.place(relx=1, x=-26, y=12)
=======
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
>>>>>>> origin/dev
