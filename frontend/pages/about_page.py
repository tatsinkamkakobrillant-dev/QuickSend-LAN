
import customtkinter as ctk

from frontend.components.icons import get_icon


class AboutPage(ctk.CTkFrame):

<<<<<<< HEAD
    def __init__(self, parent, state=None, on_navigate=None):
=======
    def __init__(self, parent, service=None):
>>>>>>> origin/dev
        super().__init__(parent, fg_color="transparent")

        ctk.CTkLabel(
            self,
            text="À propos de QuickSend LAN",
            font=("Segoe UI", 23, "bold"),
            text_color="#142D4E"
        ).pack(anchor="w", padx=20, pady=(20, 8))

        ctk.CTkLabel(
            self,
            text="Découvrez notre application de partage de fichiers.",
            font=("Segoe UI", 13),
            text_color="#52647A"
        ).pack(anchor="w", padx=20, pady=(0, 20))

        self.about_frame = ctk.CTkFrame(
            self,
            fg_color="white",
            corner_radius=12,
            border_width=1,
            border_color="#DCE5F2"
        )
        self.about_frame.pack(
            fill="both",
            expand=True,
            padx=20,
            pady=10
        )

        title_frame = ctk.CTkFrame(self.about_frame, fg_color="transparent")
        title_frame.pack(pady=(45, 10))
        ctk.CTkLabel(
            title_frame, text="",
            image=get_icon("plane", "#1769D2", 38),
            fg_color="transparent"
        ).pack(side="left", padx=(0, 10))
        ctk.CTkLabel(
            title_frame,
            text="QuickSend LAN",
            font=("Segoe UI", 30, "bold"),
            text_color="#1769D2"
        ).pack(side="left")

        ctk.CTkLabel(
            self.about_frame,
            text="Le partage de fichiers simplifié sur votre réseau local.",
            font=("Segoe UI", 14),
            text_color="#52647A"
        ).pack(pady=8)

        ctk.CTkLabel(
            self.about_frame,
            text="Version 1.0",
            font=("Segoe UI", 13, "bold"),
            text_color="#168653"
        ).pack(pady=15)

        ctk.CTkLabel(
            self.about_frame,
            text="Projet académique réalisé en équipe.",
            font=("Segoe UI", 14, "bold"),
            text_color="#142D4E"
        ).pack(pady=(25, 12))

        members = [
            "Frontend : Tatsinkam",
            "Backend : Etoundi",
            "Base de données : Fowa"
        ]

        for member in members:
            ctk.CTkLabel(
                self.about_frame,
                text=member,
                font=("Segoe UI", 13),
                text_color="#52647A"
            ).pack(pady=5)

        ctk.CTkLabel(
            self.about_frame,
            text="QuickSend LAN © 2026",
            font=("Segoe UI", 11),
            text_color="#718096"
        ).pack(pady=(30, 15))
