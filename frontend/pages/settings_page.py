"""Paramètres partagés avec le service UDP (dossier et port)."""

import customtkinter as ctk
from tkinter import filedialog

from frontend.services.app_state import UNAVAILABLE


class SettingsPage(ctk.CTkFrame):

    def __init__(self, parent, state=None, on_navigate=None):
        super().__init__(parent, fg_color="transparent")
        self.state = state

        ctk.CTkLabel(
            self, text="Paramètres", font=("Segoe UI", 23, "bold"),
            text_color="#142D4E", anchor="w"
        ).pack(anchor="w", padx=20, pady=(20, 8))

        ctk.CTkLabel(
            self, text="Configurez les préférences de QuickSend LAN pour cette session.",
            font=("Segoe UI", 13), text_color="#52647A", anchor="w"
        ).pack(anchor="w", padx=20, pady=(0, 14))

        self.settings_frame = ctk.CTkFrame(
            self, fg_color="white", corner_radius=12,
            border_width=1, border_color="#DCE5F2"
        )
        self.settings_frame.pack(fill="both", expand=True, padx=20, pady=(0, 20))

        ctk.CTkLabel(
            self.settings_frame, text="Dossier de réception",
            font=("Segoe UI", 15, "bold"), text_color="#142D4E", anchor="w"
        ).pack(anchor="w", padx=25, pady=(28, 8))

        folder = (
            str(state.settings.receive_folder) if state else UNAVAILABLE
        )
        self.folder_label = ctk.CTkLabel(
            self.settings_frame, text=folder, font=("Segoe UI", 12),
            text_color="#52647A", wraplength=640, anchor="w"
        )
        self.folder_label.pack(anchor="w", padx=25, pady=4)

        self.folder_button = ctk.CTkButton(
            self.settings_frame, text="Modifier le dossier",
            command=self.choose_folder
        )
        self.folder_button.pack(anchor="w", padx=25, pady=10)

        ctk.CTkLabel(
            self.settings_frame, text="Port de communication UDP",
            font=("Segoe UI", 15, "bold"), text_color="#142D4E", anchor="w"
        ).pack(anchor="w", padx=25, pady=(24, 8))

        self.port_entry = ctk.CTkEntry(self.settings_frame, width=180, height=38)
        self.port_entry.insert(
            0, str(state.port if state else UNAVAILABLE)
        )
        self.port_entry.pack(anchor="w", padx=25, pady=4)

        ctk.CTkLabel(
            self.settings_frame,
            text="Le service réécoute automatiquement sur le port appliqué.",
            font=("Segoe UI", 11), text_color="#52647A", anchor="w"
        ).pack(anchor="w", padx=25, pady=(6, 0))

        self.save_button = ctk.CTkButton(
            self.settings_frame, text="Enregistrer les paramètres", height=38,
            fg_color="#168653", hover_color="#116B42",
            command=self.save_settings
        )
        self.save_button.pack(anchor="w", padx=25, pady=(22, 8))

        self.status_label = ctk.CTkLabel(
            self.settings_frame, text="", font=("Segoe UI", 12, "bold"),
            text_color="#52647A", wraplength=640, anchor="w"
        )
        self.status_label.pack(anchor="w", padx=25, pady=(4, 20))

    def choose_folder(self):
        if self.state is None:
            return
        folder = filedialog.askdirectory(
            parent=self.winfo_toplevel(),
            title="Choisir le dossier de réception",
            initialdir=str(self.state.settings.receive_folder)
        )
        if folder:
            self.folder_label.configure(text=folder)
            self.status_label.configure(
                text="Nouveau dossier sélectionné. Enregistrez pour l'appliquer.",
                text_color="#1769D2"
            )
            self._pending_folder = folder
        else:
            self._pending_folder = None

    def save_settings(self):
        if self.state is None:
            self.status_label.configure(
                text="Paramètres indisponibles : service non chargé.",
                text_color="#A4252B"
            )
            return

        try:
            port = int(self.port_entry.get().strip())
            if not 1 <= port <= 65535:
                raise ValueError
        except ValueError:
            self.status_label.configure(
                text="Veuillez saisir un port UDP valide entre 1 et 65535.",
                text_color="#A4252B"
            )
            return

        pending_folder = getattr(self, "_pending_folder", None)
        self.save_button.configure(state="disabled", text="Enregistrement…")
        self.status_label.configure(
            text="Application des paramètres…", text_color="#1769D2"
        )

        def worker():
            self.state.configure(
                receive_folder=pending_folder, udp_port=port
            )

        def done(_result, error):
            if self.winfo_exists() == 0:
                return
            self.save_button.configure(state="normal", text="Enregistrer les paramètres")
            if error is None:
                self._pending_folder = None
                self.folder_label.configure(
                    text=str(self.state.settings.receive_folder)
                )
                self.port_entry.delete(0, "end")
                self.port_entry.insert(0, str(self.state.port))
                self.status_label.configure(
                    text=f"Paramètres appliqués. Port actif : {self.state.port}.",
                    text_color="#0A720B"
                )
                self.state.refresh_network()
            else:
                self.status_label.configure(
                    text=f"Impossible d'appliquer les paramètres : {error}",
                    text_color="#A4252B"
                )

        from frontend.services.app_state import run_async
        run_async(self, worker, done)
