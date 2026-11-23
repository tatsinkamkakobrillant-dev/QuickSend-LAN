"""Page « Paramètres » : dossier de réception et port UDP."""

from __future__ import annotations

import customtkinter as ctk
from tkinter import filedialog, messagebox


class SettingsPage(ctk.CTkFrame):
    def __init__(self, parent, service=None, on_settings_saved=None):
        super().__init__(parent, fg_color="transparent")
        self.service = service
        self.on_settings_saved = on_settings_saved

        self.receive_folder = str(service.receive_folder) if service else ""
        self.udp_port = service.port if service else 5000

        ctk.CTkLabel(
            self,
            text="Paramètres",
            font=("Arial", 23, "bold"),
            text_color="#142D4E",
        ).pack(anchor="w", padx=20, pady=(20, 8))

        ctk.CTkLabel(
            self,
            text="Configurez les préférences de QuickSend LAN.",
            font=("Arial", 13),
            text_color="#52647A",
        ).pack(anchor="w", padx=20, pady=(0, 20))

        self.settings_frame = ctk.CTkFrame(
            self,
            fg_color="white",
            corner_radius=12,
            border_width=1,
            border_color="#DCE5F2",
        )
        self.settings_frame.pack(fill="both", expand=True, padx=20, pady=10)

        ctk.CTkLabel(
            self.settings_frame,
            text="Dossier de réception",
            font=("Arial", 15, "bold"),
            text_color="#142D4E",
        ).pack(anchor="w", padx=25, pady=(30, 8))

        self.folder_label = ctk.CTkLabel(
            self.settings_frame,
            text=self.receive_folder,
            font=("Arial", 12),
            text_color="#52647A",
            wraplength=650,
        )
        self.folder_label.pack(anchor="w", padx=25, pady=5)

        ctk.CTkButton(
            self.settings_frame,
            text="Modifier le dossier",
            command=self.choose_folder,
        ).pack(anchor="w", padx=25, pady=10)

        ctk.CTkLabel(
            self.settings_frame,
            text="Port de communication UDP",
            font=("Arial", 15, "bold"),
            text_color="#142D4E",
        ).pack(anchor="w", padx=25, pady=(25, 8))

        self.port_entry = ctk.CTkEntry(self.settings_frame, width=180, height=38)
        self.port_entry.insert(0, str(self.udp_port))
        self.port_entry.pack(anchor="w", padx=25, pady=5)

        ctk.CTkButton(
            self.settings_frame,
            text="Enregistrer les paramètres",
            fg_color="#168653",
            hover_color="#116B42",
            command=self.save_settings,
        ).pack(anchor="w", padx=25, pady=25)

        ctk.CTkLabel(
            self.settings_frame,
            text="Le changement de port redémarre automatiquement le récepteur UDP.",
            font=("Arial", 11),
            text_color="#718096",
        ).pack(anchor="w", padx=25)

    def choose_folder(self):
        folder = filedialog.askdirectory(
            title="Choisir le dossier de réception",
            initialdir=self.receive_folder,
        )
        if folder:
            self.receive_folder = folder
            self.folder_label.configure(text=folder)

    def save_settings(self):
        try:
            port = int(self.port_entry.get().strip())
            if not 1 <= port <= 65535:
                raise ValueError
        except ValueError:
            messagebox.showerror(
                "Erreur",
                "Veuillez saisir un port UDP valide entre 1 et 65535.",
            )
            return

        self.udp_port = port
        try:
            if self.service:
                self.service.configure(receive_folder=self.receive_folder, port=port)
        except (OSError, ValueError) as exc:
            messagebox.showerror("Paramètres", str(exc))
            return

        if self.on_settings_saved:
            self.on_settings_saved()
        messagebox.showinfo(
            "Paramètres",
            "Paramètres enregistrés. Le récepteur UDP utilise le nouveau port.",
        )
