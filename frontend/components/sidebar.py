
import customtkinter as ctk


class Sidebar(ctk.CTkFrame):

    def __init__(self, parent, on_navigate=None):
        super().__init__(
            parent,
            width=220,
            fg_color="#142D4E",
            corner_radius=0
        )

        self.pack_propagate(False)
        self.on_navigate = on_navigate
        self.buttons = {}

        # Logo
        self.logo = ctk.CTkLabel(
            self,
            text="QuickSend LAN",
            font=("Arial", 21, "bold"),
            text_color="white"
        )
        self.logo.pack(pady=(30, 35))

        # Rubriques du menu
        menu_items = [
            "Accueil",
            "Appareils",
            "Envoyer un fichier",
            "Recevoir un fichier",
            "Historique",
            "Paramètres",
            "À propos"
        ]

        for item in menu_items:
            button = ctk.CTkButton(
                self,
                text=item,
                anchor="w",
                height=42,
                fg_color="transparent",
                hover_color="#25466B",
                text_color="white",
                font=("Arial", 14),
                corner_radius=8,
                command=lambda name=item: self.navigate(name)
            )

            button.pack(fill="x", padx=15, pady=5)
            self.buttons[item] = button

    def navigate(self, page_name):
        if self.on_navigate:
            self.on_navigate(page_name)

    def set_active(self, page_name):
        for name, button in self.buttons.items():
            if name == page_name:
                button.configure(fg_color="#25466B")
            else:
                button.configure(fg_color="transparent")
