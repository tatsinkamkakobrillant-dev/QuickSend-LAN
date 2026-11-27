"""Barre supérieure sombre : identité de l'application uniquement.

La décoration de fenêtre est gérée par le système (aucun faux bouton).
"""

import customtkinter as ctk

from frontend.components.icons import get_icon


class TopBar(ctk.CTkFrame):

    def __init__(self, parent, on_close=None):
        super().__init__(parent, height=40, fg_color="#0C2D58",
                         corner_radius=0)
        self.pack_propagate(False)

        ctk.CTkLabel(
            self, text="",
            image=get_icon("plane", "#8FB6EE", 18),
            fg_color="transparent"
        ).place(x=18, y=11)

        ctk.CTkLabel(
            self, text="QuickSend LAN",
            font=("Segoe UI", 13, "bold"),
            text_color="#FFFFFF"
        ).place(x=44, y=9)

        ctk.CTkLabel(
            self, text="Partage de fichiers sur réseau local",
            font=("Segoe UI", 10),
            text_color="#AFC6E8"
        ).place(x=152, y=11)
