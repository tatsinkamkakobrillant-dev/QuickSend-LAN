"""Page « Envoyer un fichier » : envoi UDP réel avec suivi de progression."""

from __future__ import annotations

import ipaddress
import os
import threading
from pathlib import Path

import customtkinter as ctk
from tkinter import filedialog, messagebox


class SendPage(ctk.CTkFrame):
    def __init__(self, parent, service=None):
        super().__init__(parent, fg_color="transparent")

        self.service = service
        self.selected_file = None
        self.selected_device = None
        self.devices: dict[str, str] = {}
        self.sending = False

        ctk.CTkLabel(
            self,
            text="Envoyer un fichier",
            font=("Arial", 23, "bold"),
            text_color="#142D4E",
        ).pack(anchor="w", padx=20, pady=(20, 8))

        ctk.CTkLabel(
            self,
            text="Sélectionnez un fichier, puis un appareil ou saisissez son adresse IP.",
            font=("Arial", 13),
            text_color="#52647A",
        ).pack(anchor="w", padx=20, pady=(0, 20))

        self.send_frame = ctk.CTkFrame(
            self,
            fg_color="white",
            corner_radius=12,
            border_width=1,
            border_color="#DCE5F2",
        )
        self.send_frame.pack(fill="both", expand=True, padx=20, pady=10)

        self.file_label = ctk.CTkLabel(
            self.send_frame,
            text="Aucun fichier sélectionné",
            font=("Arial", 15),
            text_color="#718096",
        )
        self.file_label.pack(pady=(22, 6))

        self.file_info_label = ctk.CTkLabel(
            self.send_frame,
            text="",
            font=("Arial", 12),
            text_color="#52647A",
            justify="center",
        )
        self.file_info_label.pack(pady=2)

        ctk.CTkButton(
            self.send_frame,
            text="Sélectionner un fichier",
            height=38,
            fg_color="#1769D2",
            hover_color="#1255AD",
            command=self.select_file,
        ).pack(pady=10)

        # Destinataire
        ctk.CTkLabel(
            self.send_frame,
            text="Appareil destinataire",
            font=("Arial", 14, "bold"),
            text_color="#142D4E",
        ).pack(pady=(8, 6))

        device_row = ctk.CTkFrame(self.send_frame, fg_color="transparent")
        device_row.pack()

        self.device_menu = ctk.CTkOptionMenu(
            device_row,
            values=["Recherche..."],
            width=230,
            height=36,
            fg_color="#1769D2",
            button_color="#1255AD",
            command=self.select_device,
        )
        self.device_menu.set("Recherche...")
        self.device_menu.pack(side="left", padx=(0, 8))

        ctk.CTkButton(
            device_row,
            text="↻",
            width=36,
            height=36,
            fg_color="#52647A",
            hover_color="#3E4F66",
            command=self._discover,
        ).pack(side="left")

        self.ip_variable = ctk.StringVar()
        self.ip_variable.trace_add("write", lambda *_: self.update_send_button())
        self.ip_entry = ctk.CTkEntry(
            self.send_frame,
            textvariable=self.ip_variable,
            placeholder_text="Adresse IP (ex : 192.168.1.10)",
            width=280,
            height=36,
        )
        self.ip_entry.pack(pady=8)

        self.device_info_label = ctk.CTkLabel(
            self.send_frame,
            text="Aucun destinataire sélectionné",
            font=("Arial", 12),
            text_color="#718096",
        )
        self.device_info_label.pack(pady=2)

        # Progression
        self.progress = ctk.CTkProgressBar(self.send_frame, width=420)
        self.progress.set(0)
        self.progress.pack(pady=(14, 4))

        self.status_label = ctk.CTkLabel(
            self.send_frame,
            text="Prêt à envoyer",
            font=("Arial", 12),
            text_color="#52647A",
        )
        self.status_label.pack(pady=(0, 8))

        self.send_button = ctk.CTkButton(
            self.send_frame,
            text="Envoyer le fichier",
            height=42,
            fg_color="#168653",
            hover_color="#116B42",
            state="disabled",
            command=self.send_file,
        )
        self.send_button.pack(pady=(4, 18))

        self._discover()

    # ------------------------------------------------------------------
    # Sélection
    # ------------------------------------------------------------------

    def select_file(self):
        file_path = filedialog.askopenfilename(title="Sélectionner un fichier à envoyer")
        if not file_path:
            return

        self.selected_file = file_path
        filename = os.path.basename(file_path)
        extension = Path(filename).suffix
        size = os.path.getsize(file_path)
        size_text = (
            f"{size / 1024:.2f} Ko"
            if size < 1024 * 1024
            else f"{size / (1024 * 1024):.2f} Mo"
        )

        self.file_label.configure(
            text=f"Fichier sélectionné : {filename}", text_color="#168653"
        )
        self.file_info_label.configure(
            text=(
                f"Extension : {extension if extension else 'Aucune'}\n"
                f"Taille : {size_text}"
            )
        )
        self.update_send_button()

    def _alive(self) -> bool:
        try:
            return bool(self.winfo_exists())
        except Exception:
            return False

    def _discover(self) -> None:
        if not self.service:
            return
        threading.Thread(target=self._discover_worker, daemon=True).start()

    def _discover_worker(self) -> None:
        devices = self.service.discover_devices(timeout=1.0)
        self.after(0, lambda: self._set_devices(devices))

    def _set_devices(self, devices) -> None:
        if not self._alive():
            return

        self.devices = {device["name"]: device["ip"] for device in devices}
        values = list(self.devices) or ["Aucun appareil détecté"]
        self.device_menu.configure(values=values)
        self.device_menu.set(values[0])
        self.select_device(values[0])

    def select_device(self, device_name):
        if device_name not in self.devices:
            self.selected_device = None
            return

        self.selected_device = device_name
        ip_address = self.devices[device_name]
        self.ip_variable.set(ip_address)
        self.device_info_label.configure(
            text=f"Appareil : {device_name}\nAdresse IP : {ip_address}",
            text_color="#168653",
        )
        self.update_send_button()

    def update_send_button(self) -> None:
        ready = bool(self.selected_file) and self._valid_ip(self.ip_variable.get())
        self.send_button.configure(state="normal" if ready and not self.sending else "disabled")

        ip = self.ip_variable.get().strip()
        if ip:
            color = "#168653" if self._valid_ip(ip) else "#D18A20"
            self.device_info_label.configure(text_color=color)

    @staticmethod
    def _valid_ip(value: str) -> bool:
        try:
            ipaddress.ip_address(value.strip())
            return True
        except ValueError:
            return False

    # ------------------------------------------------------------------
    # Envoi
    # ------------------------------------------------------------------

    def send_file(self):
        if not self.selected_file or not os.path.isfile(self.selected_file):
            messagebox.showerror("Erreur", "Veuillez sélectionner un fichier valide.")
            return

        host = self.ip_variable.get().strip()
        if not self._valid_ip(host):
            messagebox.showwarning(
                "Destinataire manquant",
                "Veuillez saisir une adresse IP valide ou choisir un appareil.",
            )
            return

        filename = os.path.basename(self.selected_file)
        confirmation = messagebox.askyesno(
            "Confirmation du transfert",
            f"Envoyer ce fichier via UDP ?\n\n"
            f"Fichier : {filename}\n"
            f"Destinataire : {host}",
        )
        if not confirmation:
            return

        self.sending = True
        self.send_button.configure(state="disabled")
        self.progress.set(0)
        self.status_label.configure(text="Transfert en cours...", text_color="#1769D2")
        threading.Thread(
            target=self._send_worker,
            args=(self.selected_file, host),
            daemon=True,
        ).start()

    def _send_worker(self, source: str, host: str) -> None:
        def progress(sent: int, total: int) -> None:
            def update():
                if not self._alive():
                    return
                self.progress.set(sent / total if total else 1)
                self.status_label.configure(
                    text=f"Transfert en cours... {sent}/{total} octets"
                )

            try:
                self.after(0, update)
            except Exception:
                pass

        def schedule(callback) -> None:
            try:
                self.after(0, callback)
            except Exception:
                pass

        try:
            self.service.send_file(source, host, progress=progress)
            schedule(lambda: self._finish(True, host))
        except Exception as exc:  # noqa: BLE001 - erreur affichée à l'utilisateur
            schedule(lambda error=exc: self._finish(False, error))

    def _finish(self, success: bool, value) -> None:
        if not self._alive():
            return

        self.sending = False
        self.update_send_button()
        if success:
            self.progress.set(1)
            self.status_label.configure(
                text=f"Fichier envoyé à {value} ✔", text_color="#168653"
            )
            messagebox.showinfo(
                "Transfert terminé", f"Le fichier a bien été envoyé à {value}."
            )
        else:
            self.status_label.configure(text="Échec du transfert", text_color="#C53030")
            messagebox.showerror("Échec du transfert", str(value))
