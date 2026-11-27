"""Liste des appareils réellement découverts sur le réseau local."""

import customtkinter as ctk

from frontend.components.icons import get_icon
from frontend.services.app_state import UNAVAILABLE


class DeviceRow(ctk.CTkFrame):

    def __init__(self, parent, device):
        super().__init__(
            parent, fg_color="#F7F9FD", corner_radius=8,
            border_width=1, border_color="#DCE5F2", height=54
        )
        self.pack_propagate(False)

        ctk.CTkLabel(
            self, text="",
            image=get_icon("monitor", "#0B62F2", 26),
            fg_color="transparent"
        ).place(x=14, y=13)

        ctk.CTkLabel(
            self, text=str(device.get("name", UNAVAILABLE)),
            font=("Segoe UI", 14, "bold"), text_color="#142D4E", anchor="w"
        ).place(x=52, y=7, relwidth=0.5)

        ctk.CTkLabel(
            self,
            text=f"{device.get('ip', UNAVAILABLE)} · UDP {device.get('port', UNAVAILABLE)}",
            font=("Segoe UI", 11), text_color="#52647A", anchor="w"
        ).place(x=52, y=29, relwidth=0.6)

        ctk.CTkLabel(
            self, text="",
            image=get_icon("check", "#2BB73B", 18),
            fg_color="transparent"
        ).place(relx=1, x=-30, y=17)


class DevicesPage(ctk.CTkFrame):

    def __init__(self, parent, state=None, on_navigate=None):
        super().__init__(parent, fg_color="transparent")
        self.state = state

        header = ctk.CTkFrame(self, fg_color="transparent")
        header.pack(fill="x", padx=20, pady=(20, 8))

        ctk.CTkLabel(
            header, text="Appareils connectés",
            font=("Segoe UI", 23, "bold"), text_color="#142D4E",
            anchor="w"
        ).pack(side="left")

        self.refresh_button = ctk.CTkButton(
            header, text="Actualiser", width=110, height=34,
            fg_color="#1769D2", hover_color="#1255AD",
            command=self.refresh
        )
        self.refresh_button.pack(side="right")

        ctk.CTkLabel(
            self,
            text="Retrouvez les ordinateurs qui répondent à la découverte sur votre réseau local.",
            font=("Segoe UI", 13), text_color="#52647A", anchor="w"
        ).pack(anchor="w", padx=20, pady=(0, 12))

        self.message = ctk.CTkLabel(
            self, text="", font=("Segoe UI", 12), text_color="#52647A", anchor="w"
        )
        self.message.pack(anchor="w", padx=20)

        self.devices_frame = ctk.CTkFrame(
            self, fg_color="white", corner_radius=12,
            border_width=1, border_color="#DCE5F2"
        )
        self.devices_frame.pack(fill="both", expand=True, padx=20, pady=(10, 20))

        self.refresh()

    def refresh(self):
        if self.state is None:
            self._show_message("Service indisponible.", "#A4252B")
            return

        self.refresh_button.configure(state="disabled", text="Recherche…")
        self._show_message("Recherche d'appareils en cours…", "#52647A")

        def done(devices, error_message, _error):
            if self.winfo_exists() == 0:
                return
            self.refresh_button.configure(state="normal", text="Actualiser")
            if error_message:
                self._show_message(f"Découverte indisponible : {error_message}", "#A4252B")
                self._render([])
                return
            if not devices:
                self._show_message("Aucun appareil détecté pour le moment.", "#52647A")
            else:
                self._show_message(f"{len(devices)} appareil(s) détecté(s).", "#0A720B")
            self._render(devices)

        self.state.refresh_devices_async(self, done, force=True)

    def _show_message(self, text, color):
        self.message.configure(text=text, text_color=color)

    def _render(self, devices):
        for widget in self.devices_frame.winfo_children():
            widget.destroy()
        if not devices:
            return
        for device in devices:
            DeviceRow(self.devices_frame, device).pack(fill="x", padx=14, pady=(12, 0))
