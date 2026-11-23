"""Page « Historique » : transferts enregistrés dans SQLite."""

from __future__ import annotations

import customtkinter as ctk


class HistoryPage(ctk.CTkFrame):
    def __init__(self, parent, service=None):
        super().__init__(parent, fg_color="transparent")
        self.service = service

        ctk.CTkLabel(
            self,
            text="Historique des transferts",
            font=("Arial", 23, "bold"),
            text_color="#142D4E",
        ).pack(anchor="w", padx=20, pady=(20, 8))

        header_row = ctk.CTkFrame(self, fg_color="transparent")
        header_row.pack(fill="x", padx=20, pady=(0, 12))
        ctk.CTkLabel(
            header_row,
            text="Consultez les fichiers envoyés et reçus.",
            font=("Arial", 13),
            text_color="#52647A",
        ).pack(side="left")

        ctk.CTkButton(
            header_row,
            text="↻ Actualiser",
            height=32,
            fg_color="#1769D2",
            hover_color="#1255AD",
            command=self.refresh,
        ).pack(side="right")

        self.history_frame = ctk.CTkScrollableFrame(
            self,
            fg_color="white",
            corner_radius=12,
            border_width=1,
            border_color="#DCE5F2",
        )
        self.history_frame.pack(fill="both", expand=True, padx=20, pady=10)

        self.refresh()

    def _alive(self) -> bool:
        try:
            return bool(self.winfo_exists())
        except Exception:
            return False

    def refresh(self) -> None:
        if not self._alive():
            return

        for widget in list(self.history_frame.winfo_children()):
            widget.destroy()

        header = ctk.CTkFrame(self.history_frame, fg_color="#EAF1FA", corner_radius=8)
        header.pack(fill="x", padx=6, pady=(8, 6))
        for column, (title, weight) in enumerate(
            [("Fichier", 3), ("Type", 1), ("Appareil", 2), ("Statut", 1)]
        ):
            header.grid_columnconfigure(column, weight=weight)
            ctk.CTkLabel(
                header,
                text=title,
                font=("Arial", 12, "bold"),
                text_color="#142D4E",
            ).grid(row=0, column=column, padx=10, pady=10, sticky="w")

        rows = self.service.get_history(limit=100) if self.service else []
        if not rows:
            ctk.CTkLabel(
                self.history_frame,
                text="Aucun transfert enregistré.",
                font=("Arial", 14),
                text_color="#718096",
            ).pack(pady=60)
            return

        for row in rows:
            line = ctk.CTkFrame(self.history_frame, fg_color="#F8FAFD", corner_radius=8)
            line.pack(fill="x", padx=6, pady=3)
            for column, weight in enumerate([3, 1, 2, 1]):
                line.grid_columnconfigure(column, weight=weight)

            status_ok = row["status"] == "terminé"
            values = [
                row["filename"],
                "↑ Envoyé" if row["direction"] == "envoyé" else "↓ Reçu",
                row["peer"],
                "✔ Terminé" if status_ok else "✖ Échec",
            ]
            for column, value in enumerate(values):
                color = (
                    "#168653" if status_ok else "#C53030"
                    if column == 3
                    else "#142D4E"
                    if column == 0
                    else "#52647A"
                )
                ctk.CTkLabel(
                    line,
                    text=value,
                    font=("Arial", 11, "bold" if column in (0, 3) else "normal"),
                    text_color=color,
                    anchor="w",
                ).grid(row=0, column=column, padx=10, pady=9, sticky="w")
