
import customtkinter as ctk


class HistoryPage(ctk.CTkFrame):

    def __init__(self, parent):
        super().__init__(parent, fg_color="transparent")

        ctk.CTkLabel(
            self,
            text="Historique des transferts",
            font=("Arial", 23, "bold"),
            text_color="#142D4E"
        ).pack(anchor="w", padx=20, pady=(20, 8))

        ctk.CTkLabel(
            self,
            text="Consultez les fichiers envoyés et reçus.",
            font=("Arial", 13),
            text_color="#52647A"
        ).pack(anchor="w", padx=20, pady=(0, 20))

        self.history_frame = ctk.CTkFrame(
            self,
            fg_color="white",
            corner_radius=12,
            border_width=1,
            border_color="#DCE5F2"
        )
        self.history_frame.pack(
            fill="both",
            expand=True,
            padx=20,
            pady=10
        )

        # En-tête du tableau
        header = ctk.CTkFrame(
            self.history_frame,
            fg_color="#EAF1FA",
            corner_radius=8
        )
        header.pack(fill="x", padx=15, pady=(20, 10))

        columns = [
            ("Fichier", 2),
            ("Type", 1),
            ("Appareil", 1),
            ("Statut", 1)
        ]

        for title, weight in columns:
            header.grid_columnconfigure(weight - 1, weight=weight)

        for index, (title, weight) in enumerate(columns):
            ctk.CTkLabel(
                header,
                text=title,
                font=("Arial", 12, "bold"),
                text_color="#142D4E"
            ).grid(
                row=0,
                column=index,
                padx=10,
                pady=12,
                sticky="w"
            )

        ctk.CTkLabel(
            self.history_frame,
            text="Aucun transfert enregistré.",
            font=("Arial", 14),
            text_color="#718096"
        ).pack(pady=60)

        ctk.CTkLabel(
            self.history_frame,
            text="L'historique sera connecté à la base de données SQLite.",
            font=("Arial", 12),
            text_color="#718096"
        ).pack(pady=5)
