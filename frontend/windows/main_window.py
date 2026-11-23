"""Fenêtre principale de QuickSend LAN."""

from __future__ import annotations

import customtkinter as ctk

from feature.transfer_service import TransferService, find_available_udp_port

from frontend.components.sidebar import Sidebar
from frontend.components.header import Header
from frontend.components.footer import Footer

from frontend.pages.home_page import HomePage
from frontend.pages.devices_page import DevicesPage
from frontend.pages.send_page import SendPage
from frontend.pages.receive_page import ReceivePage
from frontend.pages.history_page import HistoryPage
from frontend.pages.settings_page import SettingsPage
from frontend.pages.about_page import AboutPage


class MainWindow(ctk.CTk):
    """Application : menu latéral, bandeau, pages et service UDP partagé."""

    def __init__(
        self,
        receive_folder=None,
        database_path="quicksend.db",
        port=5000,
        device_name=None,
        service=None,
    ):
        super().__init__()

        if service is None:
            port = find_available_udp_port(port)
            service = TransferService(
                receive_folder=receive_folder,
                database_path=database_path,
                port=port,
                device_name=device_name,
            )
        self.service = service
        self.service.start()

        self.title("QuickSend LAN")
        self.geometry("1250x780")
        self.minsize(1050, 680)
        self.configure(fg_color="#F3F6FA")
        self.protocol("WM_DELETE_WINDOW", self.on_close)

        # Menu latéral
        self.sidebar = Sidebar(self, on_navigate=self.show_page)
        self.sidebar.pack(side="left", fill="y")

        # Zone principale
        self.content_area = ctk.CTkFrame(
            self,
            fg_color="#F3F6FA",
            corner_radius=0,
        )
        self.content_area.pack(
            side="right",
            fill="both",
            expand=True,
            padx=15,
            pady=12,
        )

        self.content_area.grid_columnconfigure(0, weight=1)
        self.content_area.grid_rowconfigure(1, weight=1)
        self.content_area.grid_rowconfigure(2, minsize=48, weight=0)

        # Bandeau supérieur
        self.header = Header(self.content_area)
        self.header.configure(height=82)
        self.header.grid(row=0, column=0, sticky="ew", pady=(0, 12))

        # Conteneur des pages
        self.page_container = ctk.CTkFrame(
            self.content_area,
            fg_color="transparent",
        )
        self.page_container.grid(row=1, column=0, sticky="nsew", pady=(0, 10))

        # Pied de page
        self.footer = Footer(self.content_area, port=self.service.port)
        self.footer.configure(height=42)
        self.footer.grid(row=2, column=0, sticky="ew")

        self.pages = {
            "Accueil": HomePage,
            "Appareils": DevicesPage,
            "Envoyer un fichier": SendPage,
            "Recevoir un fichier": ReceivePage,
            "Historique": HistoryPage,
            "Paramètres": SettingsPage,
            "À propos": AboutPage,
        }
        self.current_page = None
        self._update_status()

        self.show_page("Accueil")

    def _update_status(self) -> None:
        running = self.service.is_running
        self.header.status.configure(
            text="●  Récepteur actif" if running else "●  Récepteur arrêté",
            text_color="#8BE9B7" if running else "#FFD166",
        )

    def show_page(self, page_name):
        if page_name not in self.pages:
            return

        if self.current_page is not None:
            self.current_page.destroy()

        page_class = self.pages[page_name]
        common = {"service": self.service}
        if page_name == "Accueil":
            common["on_navigate"] = self.show_page
        if page_name == "Paramètres":
            common["on_settings_saved"] = self._on_settings_saved

        self.current_page = page_class(self.page_container, **common)
        self.current_page.pack(fill="both", expand=True)

        refresh = getattr(self.current_page, "refresh", None)
        if callable(refresh):
            refresh()

        self.sidebar.set_active(page_name)
        self._update_status()

    def _on_settings_saved(self) -> None:
        self.footer.set_port(self.service.port)
        self._update_status()

    def on_close(self) -> None:
        self.service.stop()
        self.destroy()
