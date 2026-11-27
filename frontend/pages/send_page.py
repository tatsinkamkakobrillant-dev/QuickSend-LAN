"""Envoi d'un ou plusieurs fichiers, avec suivi et annulation."""

"""Page « Envoyer un fichier » : envoi UDP réel avec suivi de progression."""

from __future__ import annotations

import ipaddress
import os
<<<<<<< HEAD
=======
import threading
from pathlib import Path
>>>>>>> origin/dev

import customtkinter as ctk
from tkinter import filedialog

from frontend.components.icons import get_icon
from frontend.components.transfer_list import TransferListCard
from frontend.services.app_state import run_async

NAVY = "#142D4E"
MUTED = "#52647A"


def _size_text(path: str) -> str:
    try:
        size = os.path.getsize(path)
    except OSError:
        return "Taille indisponible"
    if size < 1024 * 1024:
        return f"{size / 1024:.1f} Ko"
    return f"{size / (1024 * 1024):.1f} Mo"


class SendPage(ctk.CTkFrame):
    def __init__(self, parent, service=None):
        super().__init__(parent, fg_color="transparent")

<<<<<<< HEAD
    def __init__(self, parent, state=None, on_navigate=None):
        super().__init__(parent, fg_color="transparent")

        self.state = state
        self.pending_paths: list[str] = []
        self.selected_device = None
        self.devices: dict[str, str] = {}
        self.sending = False
        self._remaining = 0
        self._poll_job = None

        ctk.CTkLabel(
            self, text="Envoyer des fichiers",
            font=("Segoe UI", 23, "bold"), text_color=NAVY, anchor="w"
=======
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
>>>>>>> origin/dev
        ).pack(anchor="w", padx=20, pady=(20, 8))

        ctk.CTkLabel(
            self,
<<<<<<< HEAD
            text="Sélectionnez plusieurs fichiers et un appareil détecté sur le réseau.",
            font=("Segoe UI", 13), text_color=MUTED, anchor="w"
        ).pack(anchor="w", padx=20, pady=(0, 14))

        send_frame = ctk.CTkFrame(
            self, fg_color="white", corner_radius=12,
            border_width=1, border_color="#DCE5F2"
        )
        send_frame.pack(fill="x", padx=20)

        selection = ctk.CTkFrame(send_frame, fg_color="transparent")
        selection.pack(fill="x", padx=20, pady=(18, 4))

        self.selection_label = ctk.CTkLabel(
            selection, text="Aucun fichier sélectionné",
            font=("Segoe UI", 14, "bold"), text_color=NAVY, anchor="w"
        )
        self.selection_label.pack(side="left")

        ctk.CTkButton(
            selection, text="Ajouter des fichiers", width=170, height=34,
            image=get_icon("files", "#FFFFFF", 16), compound="left",
            fg_color="#1769D2", hover_color="#1255AD",
            command=self.select_files
        ).pack(side="right")

        ctk.CTkButton(
            selection, text="Tout retirer", height=32, width=90,
            fg_color="#E4EDFB", hover_color="#CFDFF6", text_color=NAVY,
            command=self.clear_files
        ).pack(side="right", padx=(0, 8))

        self.pending_list = ctk.CTkScrollableFrame(
            send_frame, fg_color="#FAFBFE", corner_radius=8, height=104
        )
        self.pending_list.pack(fill="x", padx=20, pady=(6, 10))
        self._render_pending()

        target = ctk.CTkFrame(send_frame, fg_color="transparent")
        target.pack(fill="x", padx=20, pady=(2, 6))

        ctk.CTkLabel(
            target, text="Destinataire", font=("Segoe UI", 13, "bold"),
            text_color=NAVY, anchor="w"
        ).pack(side="left")

        self.device_menu = ctk.CTkOptionMenu(
            target, values=["Aucun appareil détecté"], width=260, height=34,
            fg_color="#1769D2", button_color="#1255AD",
            command=self.select_device, state="disabled"
        )
        self.device_menu.set("Aucun appareil détecté")
        self.device_menu.pack(side="left", padx=(14, 8))

        ctk.CTkButton(
            target, text="Actualiser", width=90, height=32,
            fg_color="#E4EDFB", hover_color="#CFDFF6", text_color=NAVY,
            command=self.refresh_devices
        ).pack(side="left")

        self.status_label = ctk.CTkLabel(
            send_frame, text="", font=("Segoe UI", 12, "bold"),
            text_color=MUTED, wraplength=700, anchor="w"
        )
        self.status_label.pack(anchor="w", padx=20, pady=(8, 4))

        self.send_button = ctk.CTkButton(
            send_frame, text="Envoyer les fichiers", height=40,
            fg_color="#168653", hover_color="#116B42",
            state="disabled", command=self.start_send
        )
        self.send_button.pack(anchor="w", padx=20, pady=(4, 18))

        self.transfer_list = TransferListCard(
            self, "Fichiers en cours d'envoi", on_cancel=self.cancel_transfers,
            on_clear=self._clear_finished
        )
        self.transfer_list.pack(fill="both", expand=True, padx=20, pady=(14, 20))

        self.refresh_devices()
        if self.state is not None and not self.state.running:
            self.status_label.configure(
                text="Envoi indisponible : service UDP arrêté.",
                text_color="#A4252B"
            )

    # ------------------------------------------------------------------
    # Sélection des fichiers
    # ------------------------------------------------------------------
    def select_files(self):
        paths = filedialog.askopenfilenames(
            parent=self.winfo_toplevel(),
            title="Sélectionner un ou plusieurs fichiers à envoyer"
        )
        if not paths:
            return
        for path in paths:
            if path not in self.pending_paths:
                self.pending_paths.append(path)
        self._render_pending()
        self.status_label.configure(text="")
        self.update_send_button()

    def clear_files(self):
        self.pending_paths.clear()
        self._render_pending()
        self.update_send_button()

    def _render_pending(self):
        for widget in self.pending_list.winfo_children():
            widget.destroy()

        if not self.pending_paths:
            ctk.CTkLabel(
                self.pending_list,
                text="Ajoutez un ou plusieurs fichiers pour préparer l'envoi.",
                font=("Segoe UI", 11), text_color=MUTED
            ).pack(pady=20)
        else:
            for path in self.pending_paths:
                row = ctk.CTkFrame(self.pending_list, fg_color="transparent", height=26)
                row.pack(fill="x")
                row.pack_propagate(False)
                ctk.CTkLabel(
                    row, text="", image=get_icon("file", "#0B62F2", 16),
                    fg_color="transparent"
                ).pack(side="left")
                ctk.CTkLabel(
                    row, text=os.path.basename(path),
                    font=("Segoe UI", 11), text_color=NAVY, anchor="w"
                ).pack(side="left", padx=(6, 6))
                ctk.CTkLabel(
                    row, text=_size_text(path), font=("Segoe UI", 10),
                    text_color=MUTED
                ).pack(side="left")
                ctk.CTkButton(
                    row, text="×", width=24, height=22,
                    fg_color="transparent", hover_color="#F7DCDE",
                    text_color="#A4252B",
                    command=lambda p=path: self._remove_file(p)
                ).pack(side="right")

        self.selection_label.configure(
            text=(
                f"{len(self.pending_paths)} fichier(s) sélectionné(s)"
                if self.pending_paths else "Aucun fichier sélectionné"
            )
        )

    def _remove_file(self, path: str):
        if path in self.pending_paths:
            self.pending_paths.remove(path)
        self._render_pending()
        self.update_send_button()

    # ------------------------------------------------------------------
    # Destinataire
    # ------------------------------------------------------------------
    def refresh_devices(self):
        if self.state is None:
            self.status_label.configure(
                text="Découverte indisponible : service non chargé.",
                text_color="#A4252B"
            )
            return

        def done(devices, error_message, _error):
            if not self.winfo_exists():
                return
            if error_message:
                self.status_label.configure(
                    text=f"Découverte indisponible : {error_message}",
                    text_color="#A4252B"
                )
                return
            self.devices = {
                f"{device['name']} ({device['ip']})": device["ip"]
                for device in devices
            }
            labels = list(self.devices) or ["Aucun appareil détecté"]
            self.device_menu.configure(
                values=labels, state="normal" if self.devices else "disabled"
            )
            if not self.devices or self.selected_device not in self.devices.values():
                self.selected_device = None
                self.device_menu.set(labels[0])
            self.update_send_button()

        self.state.refresh_devices_async(self, done, force=True)
=======
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
        self.file_label.pack(pady=(10, 2))

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
        ).pack(pady=5)

        # Destinataire
        ctk.CTkLabel(
            self.send_frame,
            text="Appareil destinataire",
            font=("Arial", 14, "bold"),
            text_color="#142D4E",
        ).pack(pady=(4, 3))

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
        self.ip_entry.pack(pady=4)

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
        self.progress.pack(pady=(6, 2))

        self.status_label = ctk.CTkLabel(
            self.send_frame,
            text="Prêt à envoyer",
            font=("Arial", 12),
            text_color="#52647A",
        )
        self.status_label.pack(pady=(0, 3))

        self.send_button = ctk.CTkButton(
            self.send_frame,
            text="Envoyer le fichier",
            height=42,
            fg_color="#168653",
            hover_color="#116B42",
            state="disabled",
            command=self.send_file,
        )
        self.send_button.pack(pady=(2, 8))

        self._discover()

    # ------------------------------------------------------------------
    # Sélection
    # ------------------------------------------------------------------

    def select_file(self):
        file_path = filedialog.askopenfilename(
            title="Sélectionner un fichier à envoyer"
        )
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
            text=f"Fichier sélectionné : {filename}",
            text_color="#168653",
        )

        self.file_info_label.configure(
            text=(
                f"Extension : {extension if extension else 'Aucune'}\n"
                f"Taille : {size_text}"
            )
        )
>>>>>>> origin/dev

    def select_device(self, label: str):
        self.selected_device = self.devices.get(label)
        self.update_send_button()

<<<<<<< HEAD
    def update_send_button(self):
        if self.sending:
            return
        ready = bool(
            self.pending_paths and self.selected_device
            and self.state and self.state.transfers and self.state.running
        )
        self.send_button.configure(state="normal" if ready else "disabled")

    # ------------------------------------------------------------------
    # Envoi et annulation
    # ------------------------------------------------------------------
    def start_send(self):
        if self.sending or not self.pending_paths or not self.selected_device:
            return
        manager = self.state.transfers if self.state else None
        if manager is None:
            self.status_label.configure(
                text="Suivi des transferts indisponible.", text_color="#A4252B"
            )
            return

        paths = list(self.pending_paths)
        try:
            ids = manager.begin_send(paths, self.selected_device)
        except Exception as exc:
            self.status_label.configure(
                text=f"Impossible de préparer l'envoi : {exc}",
                text_color="#A4252B"
            )
            return

        self.pending_paths.clear()
        self._render_pending()
        self.sending = True
        self._remaining = len(ids)
        self.send_button.configure(state="disabled", text="Envoi en cours…")
        self.status_label.configure(
            text=f"Envoi de {len(ids)} fichier(s) vers {self.selected_device}…",
            text_color="#1769D2"
        )

        for transfer_id in ids:
            def worker(tid=transfer_id):
                manager.start_send(tid)

            def done(_result, error, tid=transfer_id):
                if not self.winfo_exists():
                    return
                self._remaining -= 1
                if error is not None:
                    self.status_label.configure(
                        text=f"Échec d'un transfert : {error}",
                        text_color="#A4252B"
                    )
                if self._remaining <= 0:
                    self.sending = False
                    self.send_button.configure(
                        state="normal", text="Envoyer les fichiers"
                    )
                    self.update_send_button()
                    if error is None:
                        self.status_label.configure(
                            text=f"{len(ids)} fichier(s) traité(s).",
                            text_color="#0A720B"
                        )
                self._refresh_list()

            run_async(self, worker, done)

        self._refresh_list()
        self._poll_job = self.after(300, self._poll)

    def cancel_transfers(self, ids: list[int]):
        manager = self.state.transfers if self.state else None
        if manager is None:
            return
        count = manager.cancel(ids)
        self.status_label.configure(
            text=f"{count} transfert(s) annulé(s).", text_color="#A4252B"
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
        self.transfer_list.set_transfers(manager.snapshot(direction="envoi"))

    def _poll(self):
        if not self.winfo_exists():
            return
        self._refresh_list()
        manager = self.state.transfers if self.state else None
        if manager is not None and manager.active_count("envoi"):
            self._poll_job = self.after(300, self._poll)
        else:
            self._poll_job = None
            if self.sending:
                self.sending = False
                self.send_button.configure(state="normal", text="Envoyer les fichiers")
                self.update_send_button()

    def destroy(self):
        if self._poll_job is not None:
            try:
                self.after_cancel(self._poll_job)
            except Exception:
                pass
        super().destroy()
=======
    def _alive(self) -> bool:
        try:
            return bool(self.winfo_exists())
        except Exception:
            return False

    def _discover(self) -> None:
        if not self.service:
            return

        threading.Thread(
            target=self._discover_worker,
            daemon=True,
        ).start()

    def _discover_worker(self) -> None:
        devices = self.service.discover_devices(timeout=1.0)
        self.after(0, lambda: self._set_devices(devices))

    def _set_devices(self, devices) -> None:
        if not self._alive():
            return

        self.devices = {
            device["name"]: device["ip"]
            for device in devices
        }

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
        ready = (
            bool(self.selected_file)
            and self._valid_ip(self.ip_variable.get())
        )

        self.send_button.configure(
            state="normal" if ready and not self.sending else "disabled"
        )

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
            messagebox.showerror(
                "Erreur",
                "Veuillez sélectionner un fichier valide.",
            )
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

        self.status_label.configure(
            text="Transfert en cours...",
            text_color="#1769D2",
        )

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
            self.service.send_file(
                source,
                host,
                progress=progress,
            )
            schedule(lambda: self._finish(True, host))

        except Exception as exc:
            schedule(lambda error=exc: self._finish(False, error))

    def _finish(self, success: bool, value) -> None:
        if not self._alive():
            return

        self.sending = False
        self.update_send_button()

        if success:
            self.progress.set(1)

            self.status_label.configure(
                text=f"Fichier envoyé à {value} ✔",
                text_color="#168653",
            )

            messagebox.showinfo(
                "Transfert terminé",
                f"Le fichier a bien été envoyé à {value}.",
            )

        else:
            self.status_label.configure(
                text="Échec du transfert",
                text_color="#C53030",
            )

            messagebox.showerror(
                "Échec du transfert",
                str(value),
            )
>>>>>>> origin/dev
