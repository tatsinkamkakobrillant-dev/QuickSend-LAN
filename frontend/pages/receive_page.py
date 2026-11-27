"""Réception multiple : dossier réel, suivi et annulation des fichiers entrants."""

import customtkinter as ctk
from tkinter import filedialog

from frontend.components.transfer_list import TransferListCard
from frontend.services.app_state import UNAVAILABLE, run_async

NAVY = "#142D4E"
MUTED = "#52647A"


class ReceivePage(ctk.CTkFrame):

    def __init__(self, parent, state=None, on_navigate=None):
        super().__init__(parent, fg_color="transparent")
        self.state = state
        self.receive_folder = (
            str(state.settings.receive_folder) if state else UNAVAILABLE
        )
        self._poll_job = None
        self._base_detail = ""
        self._last_detail_text: str | None = None

        ctk.CTkLabel(
            self, text="Recevoir des fichiers",
            font=("Segoe UI", 23, "bold"), text_color=NAVY, anchor="w"
        ).pack(anchor="w", padx=20, pady=(20, 8))

        ctk.CTkLabel(
            self,
            text="Plusieurs fichiers peuvent être reçus en même temps ; annulez ceux que vous ne souhaitez plus recevoir.",
            font=("Segoe UI", 13), text_color=MUTED, anchor="w"
        ).pack(anchor="w", padx=20, pady=(0, 14))

        frame = ctk.CTkFrame(
            self, fg_color="white", corner_radius=12,
            border_width=1, border_color="#DCE5F2"
        )
        frame.pack(fill="x", padx=20)

        ctk.CTkLabel(
            frame, text="Dossier de réception",
            font=("Segoe UI", 15, "bold"), text_color=NAVY, anchor="w"
        ).pack(anchor="w", padx=20, pady=(16, 4))

        self.folder_label = ctk.CTkLabel(
            frame, text=self.receive_folder, font=("Segoe UI", 12),
            text_color=MUTED, wraplength=640, anchor="w"
        )
        self.folder_label.pack(anchor="w", padx=20, pady=2)

        self.choose_button = ctk.CTkButton(
            frame, text="Choisir un dossier", height=34,
            fg_color="#1769D2", hover_color="#1255AD",
            command=self.choose_folder
        )
        self.choose_button.pack(anchor="w", padx=20, pady=(8, 4))

        self.status_label = ctk.CTkLabel(
            frame, text="", font=("Segoe UI", 13, "bold"),
            text_color=MUTED, wraplength=640, anchor="w"
        )
        self.status_label.pack(anchor="w", padx=20, pady=(10, 2))

        self.detail_label = ctk.CTkLabel(
            frame, text="", font=("Segoe UI", 11),
            text_color=MUTED, wraplength=640, anchor="w"
        )
        self.detail_label.pack(anchor="w", padx=20, pady=(2, 16))

        self.transfer_list = TransferListCard(
            self, "Fichiers en cours de réception",
            on_cancel=self.cancel_transfers,
            on_clear=self._clear_finished
        )
        self.transfer_list.pack(fill="both", expand=True, padx=20, pady=(14, 20))

        self.refresh()
        self._poll_job = self.after(500, self._poll)

    # ------------------------------------------------------------------
    def refresh(self):
        if self.state is None:
            self.status_label.configure(
                text="Réception indisponible : service non chargé.",
                text_color="#A4252B"
            )
            self._base_detail = ""
            self._set_detail("")
            return

        if self.state.running:
            self.status_label.configure(
                text="Réception active — en attente de fichiers entrants.",
                text_color="#0A720B"
            )
            detail = (
                f"Adresse IP : {self.state.local_ip()}    "
                f"Port UDP : {self.state.port}"
            )
        else:
            self.status_label.configure(
                text="Réception indisponible : service UDP arrêté.",
                text_color="#A4252B"
            )
            detail = self.state.startup_error or "Aucune écoute active."

        self._base_detail = detail
        self._set_detail(detail)

    def _set_detail(self, text: str) -> None:
        if text != self._last_detail_text:
            self.detail_label.configure(text=text)
            self._last_detail_text = text

    def choose_folder(self):
        if self.state is None:
            return
        folder = filedialog.askdirectory(
            parent=self.winfo_toplevel(),
            title="Choisir le dossier de réception",
            initialdir=self.receive_folder
        )
        if not folder:
            return

        self.choose_button.configure(state="disabled", text="Enregistrement…")
        self.status_label.configure(
            text="Enregistrement du dossier…", text_color="#1769D2"
        )

        def worker():
            self.state.configure(receive_folder=folder)

        def done(_result, error):
            if not self.winfo_exists():
                return
            self.choose_button.configure(state="normal", text="Choisir un dossier")
            if error is None:
                self.receive_folder = str(self.state.settings.receive_folder)
                self.folder_label.configure(text=self.receive_folder)
                self.refresh()
            else:
                self.status_label.configure(
                    text=f"Impossible d'appliquer le dossier : {error}",
                    text_color="#A4252B"
                )

        run_async(self, worker, done)

    # ------------------------------------------------------------------
    def cancel_transfers(self, ids: list[int]):
        manager = self.state.transfers if self.state else None
        if manager is None:
            return
        count = manager.cancel(ids)
        self.status_label.configure(
            text=f"{count} réception(s) annulée(s).", text_color="#A4252B"
        )
        self.transfer_list.clear_selection()
        self._refresh_list()

    def _clear_finished(self):
        manager = self.state.transfers if self.state else None
        if manager is not None:
            manager.clear_finished()
        self._refresh_list()

    def _refresh_list(self):
        manager = self.state.transfers if self.state else None
        if manager is None:
            self.transfer_list.set_transfers([])
            return
        self.transfer_list.set_transfers(manager.snapshot(direction="réception"))

    def _poll(self):
        if not self.winfo_exists():
            return
        self._refresh_list()
        manager = self.state.transfers if self.state else None
        count = manager.active_count("réception") if manager else 0
        text = (
            f"{count} réception(s) en cours · {self._base_detail}"
            if count else self._base_detail
        )
        self._set_detail(text)
        self._poll_job = self.after(500, self._poll)

    def destroy(self):
        if self._poll_job is not None:
            try:
                self.after_cancel(self._poll_job)
            except Exception:
                pass
        super().destroy()
