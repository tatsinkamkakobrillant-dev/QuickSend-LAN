"""Page « Recevoir un fichier » : état du récepteur UDP et dossier de réception."""

from __future__ import annotations

import os

import customtkinter as ctk
from tkinter import filedialog, messagebox


class ReceivePage(ctk.CTkFrame):
    def __init__(self, parent, service=None):
        super().__init__(parent, fg_color="transparent")
        self.service = service

        self.receive_folder = str(service.receive_folder) if service else os.path.join(
            os.path.expanduser("~"), "Downloads", "QuickSend"
        )

        ctk.CTkLabel(
            self,
            text="Recevoir un fichier",
            font=("Arial", 23, "bold"),
            text_color="#142D4E",
        ).pack(anchor="w", padx=20, pady=(20, 8))

        ctk.CTkLabel(
            self,
            text="Le récepteur UDP tourne en arrière-plan dès le lancement de l'application.",
            font=("Arial", 13),
            text_color="#52647A",
        ).pack(anchor="w", padx=20, pady=(0, 20))

        self.receive_frame = ctk.CTkFrame(
            self,
            fg_color="white",
            corner_radius=12,
            border_width=1,
            border_color="#DCE5F2",
        )
        self.receive_frame.pack(fill="both", expand=True, padx=20, pady=10)

        ctk.CTkLabel(
            self.receive_frame,
            text="Dossier de réception",
            font=("Arial", 16, "bold"),
            text_color="#142D4E",
        ).pack(pady=(35, 8))

        self.folder_label = ctk.CTkLabel(
            self.receive_frame,
            text=self.receive_folder,
            font=("Arial", 12),
            text_color="#52647A",
            wraplength=650,
        )
        self.folder_label.pack(pady=8, padx=20)

        ctk.CTkButton(
            self.receive_frame,
            text="Choisir un dossier",
            height=38,
            fg_color="#1769D2",
            hover_color="#1255AD",
            command=self.choose_folder,
        ).pack(pady=10)

        self.status_label = ctk.CTkLabel(
            self.receive_frame,
            text="",
            font=("Arial", 13, "bold"),
            text_color="#168653",
        )
        self.status_label.pack(pady=12)

        self.toggle_button = ctk.CTkButton(
            self.receive_frame,
            text="Arrêter le récepteur",
            height=38,
            fg_color="#C53030",
            hover_color="#9B2525",
            command=self.toggle_receiver,
        )
        self.toggle_button.pack(pady=(0, 10))

        ctk.CTkLabel(
            self.receive_frame,
            text="Les fichiers reçus sont écrit dans un fichier temporaire puis "
            "renommés une fois le transfert confirmé.",
            font=("Arial", 12),
            text_color="#718096",
            wraplength=650,
            justify="center",
        ).pack(pady=(18, 10))

        self.refresh()

    def _alive(self) -> bool:
        try:
            return bool(self.winfo_exists())
        except Exception:
            return False

    def refresh(self) -> None:
        if not self._alive():
            return
        running = bool(self.service and self.service.is_running)
        self.status_label.configure(
            text="● Récepteur UDP actif" if running else "● Récepteur UDP arrêté",
            text_color="#168653" if running else "#D18A20",
        )
        self.toggle_button.configure(
            text="Arrêter le récepteur" if running else "Démarrer le récepteur",
            fg_color="#C53030" if running else "#168653",
            hover_color="#9B2525" if running else "#116B42",
        )
        if self.service:
            self.receive_folder = str(self.service.receive_folder)
            self.folder_label.configure(text=self.receive_folder)

    def choose_folder(self):
        folder = filedialog.askdirectory(
            title="Choisir le dossier de réception",
            initialdir=self.receive_folder,
        )
        if not folder:
            return

        self.receive_folder = folder
        self.folder_label.configure(text=folder)
        if self.service:
            try:
                self.service.configure(receive_folder=folder)
            except OSError as exc:
                messagebox.showerror("Dossier invalide", str(exc))

    def toggle_receiver(self):
        if not self.service:
            return
        try:
            if self.service.is_running:
                self.service.stop()
            else:
                self.service.start()
        except OSError as exc:
            messagebox.showerror("Récepteur UDP", str(exc))
        self.refresh()
