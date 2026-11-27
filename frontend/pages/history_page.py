"""Historique réel des transferts enregistrés dans la base SQLite."""

import customtkinter as ctk

from frontend.components.icons import get_icon
from frontend.services.app_state import UNAVAILABLE

STATUS_STYLE = {
    "terminé": ("Terminé", "#2BB73B", "#0A720B"),
    "réussi": ("Terminé", "#2BB73B", "#0A720B"),
    "échec": ("Échec", "#C4474D", "#A4252B"),
    "failed": ("Échec", "#C4474D", "#A4252B"),
    "en cours": ("En cours", "#F48F0C", "#A85C00"),
}


class HistoryRow(ctk.CTkFrame):

    def __init__(self, parent, entry, format_time):
        super().__init__(parent, fg_color="#F8F9FE", corner_radius=8, height=36)
        self.pack_propagate(False)

        direction = str(entry.get("direction", "")).lower()
        received = direction.startswith("reçu") or direction == "received"
        icon = "download" if received else "upload"
        color = "#0A720B" if received else "#0B62F2"

        ctk.CTkLabel(
            self, text="",
            image=get_icon(icon, color, 18), fg_color="transparent"
        ).place(x=10, y=10)

        ctk.CTkLabel(
            self, text=str(entry.get("filename", UNAVAILABLE)),
            font=("Segoe UI", 12, "bold"), text_color="#142D4E", anchor="w"
        ).place(x=34, y=7, relwidth=0.29)

        ctk.CTkLabel(
            self, text="Reçu" if received else "Envoyé",
            font=("Segoe UI", 11), text_color=color
        ).place(relx=0.34, y=7)

        ctk.CTkLabel(
            self, text=str(entry.get("peer", UNAVAILABLE)),
            font=("Segoe UI", 11), text_color="#52647A", anchor="w"
        ).place(relx=0.43, y=7, relwidth=0.18)

        ctk.CTkLabel(
            self, text=format_time(str(entry.get("created_at", ""))),
            font=("Segoe UI", 11), text_color="#52647A"
        ).place(relx=0.63, y=7)

        status = str(entry.get("status", "")).strip().lower()
        label, icon_color, text_color = STATUS_STYLE.get(
            status, (status or UNAVAILABLE, "#F48F0C", "#A85C00")
        )
        ctk.CTkLabel(
            self, text="",
            image=get_icon("check" if status in STATUS_STYLE and "échec" not in status else "close",
                           icon_color, 15),
            fg_color="transparent"
        ).place(relx=1, x=-62, y=10)
        ctk.CTkLabel(
            self, text=label, font=("Segoe UI", 10, "bold"),
            text_color=text_color, anchor="e", width=56
        ).place(relx=1, x=-6, y=9, anchor="ne")


class HistoryPage(ctk.CTkFrame):

    def __init__(self, parent, state=None, on_navigate=None):
        super().__init__(parent, fg_color="transparent")
        self.state = state

        header = ctk.CTkFrame(self, fg_color="transparent")
        header.pack(fill="x", padx=20, pady=(20, 8))
        ctk.CTkLabel(
            header, text="Historique des transferts",
            font=("Segoe UI", 23, "bold"), text_color="#142D4E", anchor="w"
        ).pack(side="left")

        ctk.CTkButton(
            header, text="Actualiser", width=110, height=34,
            fg_color="#1769D2", hover_color="#1255AD",
            command=self.refresh
        ).pack(side="right")

        ctk.CTkLabel(
            self, text="Consultez les fichiers envoyés et reçus.",
            font=("Segoe UI", 13), text_color="#52647A", anchor="w"
        ).pack(anchor="w", padx=20, pady=(0, 12))

        self.message = ctk.CTkLabel(
            self, text="", font=("Segoe UI", 12), text_color="#52647A", anchor="w"
        )
        self.message.pack(anchor="w", padx=20)

        self.history_frame = ctk.CTkFrame(
            self, fg_color="white", corner_radius=12,
            border_width=1, border_color="#DCE5F2"
        )
        self.history_frame.pack(fill="both", expand=True, padx=20, pady=(10, 20))

        table_head = ctk.CTkFrame(
            self.history_frame, fg_color="#EAF1FA", corner_radius=8, height=32
        )
        table_head.pack(fill="x", padx=14, pady=(10, 4))
        table_head.pack_propagate(False)

        for text, relx in [
            ("Fichier", 0.03), ("Type", 0.34), ("Appareil", 0.43),
            ("Heure", 0.63), ("Statut", 0.84)
        ]:
            ctk.CTkLabel(
                table_head, text=text, font=("Segoe UI", 11, "bold"),
                text_color="#142D4E", anchor="w"
            ).place(relx=relx, y=7)

        self.rows_frame = ctk.CTkFrame(self.history_frame, fg_color="transparent")
        self.rows_frame.pack(fill="both", expand=True, padx=14, pady=(0, 10))

        self.refresh()

    def refresh(self):
        if self.state is None:
            self.message.configure(text="Historique indisponible.", text_color="#A4252B")
            return
        self.message.configure(text="Chargement de l'historique…", text_color="#52647A")

        def done(history, error_message, _error):
            if self.winfo_exists() == 0:
                return
            for widget in self.rows_frame.winfo_children():
                widget.destroy()
            if error_message:
                self.message.configure(
                    text=f"Historique indisponible : {error_message}",
                    text_color="#A4252B"
                )
                return
            if not history:
                self.message.configure(
                    text="Aucun transfert enregistré pour le moment.",
                    text_color="#52647A"
                )
                return
            self.message.configure(
                text=f"{len(history)} transfert(s) enregistré(s).",
                text_color="#0A720B"
            )
            for entry in history:
                HistoryRow(
                    self.rows_frame, entry, self.state.format_time
                ).pack(fill="x", pady=2)

        self.state.refresh_history_async(self, done)
