
import customtkinter as ctk


class AboutPage(ctk.CTkFrame):

    def __init__(self, parent):
        super().__init__(parent, fg_color="transparent")

        ctk.CTkLabel(
            self,
            text="À propos de QuickSend LAN",
            font=("Arial", 23, "bold"),
            text_color="#142D4E"
        ).pack(anchor="w", padx=20, pady=(20, 8))

        ctk.CTkLabel(
            self,
            text="Découvrez notre application de partage de fichiers.",
            font=("Arial", 13),
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

        ctk.CTkLabel(
            self.about_frame,
            text="◆ QuickSend LAN",
            font=("Arial", 30, "bold"),
            text_color="#1769D2"
        ).pack(pady=(45, 10))

        ctk.CTkLabel(
            self.about_frame,
            text="Le partage de fichiers simplifié sur votre réseau local.",
            font=("Arial", 14),
            text_color="#52647A"
        ).pack(pady=8)

        ctk.CTkLabel(
            self.about_frame,
            text="Version 1.0",
            font=("Arial", 13, "bold"),
            text_color="#168653"
        ).pack(pady=15)

        ctk.CTkLabel(
            self.about_frame,
            text="Projet académique réalisé en équipe.",
            font=("Arial", 14, "bold"),
            text_color="#142D4E"
        ).pack(pady=(25, 12))

        members = [
            "Frontend : Brillant",
            "Backend : Etoundi",
            "Base de données : Michelle"
        ]

        for member in members:
            ctk.CTkLabel(
                self.about_frame,
                text=member,
                font=("Arial", 13),
                text_color="#52647A"
            ).pack(pady=5)

        ctk.CTkLabel(
            self.about_frame,
            text="QuickSend LAN © 2026",
            font=("Arial", 11),
            text_color="#718096"
        ).pack(pady=(30, 15))
