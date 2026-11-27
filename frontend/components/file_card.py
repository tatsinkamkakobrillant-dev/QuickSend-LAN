 
import customtkinter as ctk


class FileCard(ctk.CTkFrame):

    def __init__(self, parent, title, value, description):
        super().__init__(
            parent,
            fg_color="white",
            corner_radius=12,
            border_width=1,
            border_color="#E5EAF0"
        )

        # Titre de la carte
        self.title_label = ctk.CTkLabel(
            self,
            text=title,
            font=("Segoe UI", 14),
            text_color="#718096"
        )
        self.title_label.pack(
            anchor="w",
            padx=20,
            pady=(18, 5)
        )

        # Valeur principale
        self.value_label = ctk.CTkLabel(
            self,
            text=value,
            font=("Segoe UI", 28, "bold"),
            text_color="#142D4E"
        )
        self.value_label.pack(
            anchor="w",
            padx=20,
            pady=2
        )

        # Description complémentaire
        self.description_label = ctk.CTkLabel(
            self,
            text=description,
            font=("Segoe UI", 12),
            text_color="#718096"
        )
        self.description_label.pack(
            anchor="w",
            padx=20,
            pady=(2, 15)
        )
