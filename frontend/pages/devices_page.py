
import customtkinter as ctk


class DevicesPage(ctk.CTkFrame):

    def __init__(self, parent):
        super().__init__(
            parent,
            fg_color="transparent"
        )

        ctk.CTkLabel(
            self,
            text="Appareils connectés",
            font=("Arial", 23, "bold"),
            text_color="#142D4E"
        ).pack(anchor="w", padx=20, pady=(20, 8))

        ctk.CTkLabel(
            self,
            text="Retrouvez les ordinateurs disponibles sur votre réseau local.",
            font=("Arial", 13),
            text_color="#52647A"
        ).pack(anchor="w", padx=20, pady=(0, 20))

        self.devices_frame = ctk.CTkFrame(
            self,
            fg_color="white",
            corner_radius=12,
            border_width=1,
            border_color="#DCE5F2"
        )
        self.devices_frame.pack(
            fill="both",
            expand=True,
            padx=20,
            pady=10
        )

        ctk.CTkLabel(
            self.devices_frame,
            text="Aucun appareil détecté pour le moment.",
            font=("Arial", 14),
            text_color="#718096"
        ).pack(pady=40)
