"""Bandeau d'accueil en dégradé avec l'état de connexion réel."""

import customtkinter as ctk

from frontend.components.gradient import GradientFrame
from frontend.components.icons import get_icon


class Header(GradientFrame):

    def __init__(self, parent, state=None):
        super().__init__(parent, start="#EBF1FE", end="#6CADFD",
                         corner_radius=2, height=95)
        self.pack_propagate(False)
        self.state = state

        self.logo = ctk.CTkLabel(
            self, text="",
            image=get_icon("plane", "#0B62F2", 54),
            fg_color="transparent"
        )
        self.logo.place(x=20, y=20)

        self.title = ctk.CTkLabel(
            self, text="QuickSend LAN",
            font=("Segoe UI", 32, "bold"),
            text_color="#041E53"
        )
        self.title.place(x=88, y=14)

        self.subtitle = ctk.CTkLabel(
            self,
            text="Partage de fichiers rapide sur votre réseau local",
            font=("Segoe UI", 14),
            text_color="#071461"
        )
        self.subtitle.place(x=90, y=64)

        self.status_pill = ctk.CTkFrame(
            self, fg_color="#CDF0E2", corner_radius=20,
            width=200, height=40
        )
        self.status_pill.place(relx=1, x=-32, y=20, anchor="ne")
        self.status_pill.pack_propagate(False)

        self.status_dot = ctk.CTkLabel(
            self.status_pill, text="",
            image=get_icon("check", "#2BB73B", 16),
            fg_color="transparent"
        )
        self.status_dot.place(x=14, y=12)

        self.status_label = ctk.CTkLabel(
            self.status_pill, text="Indisponible",
            font=("Segoe UI", 13, "bold"),
            text_color="#A85C00"
        )
        self.status_label.place(x=38, y=8)

        self.status_detail = ctk.CTkLabel(
            self, text="Vérification du service…",
            font=("Segoe UI", 10),
            text_color="#0A720B"
        )
        self.status_detail.place(relx=1, x=-32, y=68, anchor="ne")

        self.refresh()

    def set_status(self, text, detail=None, color="#0A720B"):
        self.status_label.configure(text=text, text_color=color)
        if detail is not None:
            self.status_detail.configure(text=detail, text_color=color)

        dot_color = "#2BB73B" if color == "#0A720B" else (
            "#E08A1E" if color == "#A85C00" else "#C4474D"
        )
        self.status_dot.configure(image=get_icon("check", dot_color, 16))

    def refresh(self):
        if self.state is None:
            return
        text, detail, color = self.state.status()
        background = (
            "#CDF0E2" if color == "#0A720B"
            else "#FBE8CE" if color == "#A85C00"
            else "#F7DCDE"
        )
        self.status_pill.configure(fg_color=background)
        self.set_status(text, detail, color)
