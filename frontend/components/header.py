
import customtkinter as ctk


class Header(ctk.CTkFrame):

    def __init__(self, parent):
        super().__init__(
            parent,
            fg_color="#142D4E",
            corner_radius=12,
            height=95
        )

        self.pack_propagate(False)

        # Partie gauche : identité de l'application
        self.left_frame = ctk.CTkFrame(
            self,
            fg_color="transparent"
        )
        self.left_frame.pack(
            side="left",
            fill="y",
            padx=25
        )

        self.title = ctk.CTkLabel(
            self.left_frame,
            text="◆  QuickSend LAN",
            font=("Arial", 24, "bold"),
            text_color="white"
        )
        self.title.pack(
            anchor="w",
            pady=(17, 2)
        )

        self.subtitle = ctk.CTkLabel(
            self.left_frame,
            text="Le partage de fichiers simplifié sur votre réseau local",
            font=("Arial", 12),
            text_color="#C5D7ED"
        )
        self.subtitle.pack(anchor="w")

        # Partie droite : statut de l'application
        self.status = ctk.CTkLabel(
            self,
            text="●  En attente",
            font=("Arial", 13, "bold"),
            text_color="#FFD166"
        )
        self.status.pack(
            side="right",
            padx=25
        )
