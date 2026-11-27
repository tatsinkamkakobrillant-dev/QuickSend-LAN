"""Fenêtre principale de QuickSend LAN."""

from __future__ import annotations

import customtkinter as ctk

from feature.transfer_service import TransferService, find_available_udp_port

from frontend.components.sidebar import Sidebar
from frontend.components.topbar import TopBar
from frontend.components.header import Header
from frontend.components.footer import Footer

from frontend.pages.home_page import HomePage
from frontend.pages.devices_page import DevicesPage
from frontend.pages.send_page import SendPage
from frontend.pages.receive_page import ReceivePage
from frontend.pages.history_page import HistoryPage
from frontend.pages.settings_page import SettingsPage
from frontend.pages.about_page import AboutPage
from frontend.services.app_state import AppState


class MainWindow(ctk.CTk):
    """Application : menu latéral, bandeau, pages et service UDP partagé."""

<<<<<<< HEAD
    SIDEBAR_WIDTH = 190
    COMPACT_WIDTH = 68
    FOOTER_HEIGHT = 42
    TOPBAR_HEIGHT = 40
    HEADER_HEIGHT = 95
    COMPACT_BREAKPOINT = 1050

    def __init__(self):
=======
    def __init__(
        self,
        receive_folder=None,
        database_path="quicksend.db",
        port=5000,
        device_name=None,
        service=None,
    ):
>>>>>>> origin/dev
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
<<<<<<< HEAD
        self.geometry("1400x900+20+15")
        self.minsize(880, 620)
        self.configure(fg_color="#F8F9FE")

        self.app_state = AppState()
        self.app_state.start()

        self._compact = False
        self._status_job = None

        self.grid_columnconfigure(0, weight=0, minsize=self.SIDEBAR_WIDTH)
        self.grid_columnconfigure(1, weight=1)
        self.grid_rowconfigure(0, weight=1)
        self.grid_rowconfigure(1, minsize=self.FOOTER_HEIGHT)

        self.sidebar = Sidebar(self, on_navigate=self.show_page)
        self.sidebar.grid(row=0, column=0, sticky="ns")

        self.workspace = ctk.CTkFrame(
            self, fg_color="#F8F9FE", corner_radius=0
        )
        self.workspace.grid(row=0, column=1, sticky="nsew")

        self.workspace.grid_columnconfigure(0, weight=1)
        self.workspace.grid_rowconfigure(0, minsize=self.TOPBAR_HEIGHT)
        self.workspace.grid_rowconfigure(1, minsize=self.HEADER_HEIGHT)
        self.workspace.grid_rowconfigure(2, weight=1)
=======
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
>>>>>>> origin/dev

        self.topbar = TopBar(self.workspace)
        self.topbar.grid(row=0, column=0, sticky="ew")

<<<<<<< HEAD
        self.header = Header(self.workspace, state=self.app_state)
        self.header.grid(row=1, column=0, sticky="nsew")

        self.page_container = ctk.CTkScrollableFrame(
            self.workspace, fg_color="transparent"
        )
        self.page_container.grid(
            row=2, column=0, sticky="nsew", padx=(24, 12), pady=(8, 8)
        )
        self.page_container.grid_columnconfigure(0, weight=1)
        self.page_container.grid_rowconfigure(0, weight=1)

        self.footer = Footer(self)
        self.footer.grid(row=1, column=0, columnspan=2, sticky="ew")
=======
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
>>>>>>> origin/dev

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
<<<<<<< HEAD
        self.current_name = None
        self.show_page("Accueil")

        self.bind("<Configure>", self._on_root_configure)
        self.protocol("WM_DELETE_WINDOW", self._on_close)
        self.after(150, self._on_root_configure)
        self._schedule_status_refresh()

    # ------------------------------------------------------------------
    # Navigation
    # ------------------------------------------------------------------
=======
        self._update_status()

        self.show_page("Accueil")

    def _update_status(self) -> None:
        running = self.service.is_running
        self.header.status.configure(
            text="●  Récepteur actif" if running else "●  Récepteur arrêté",
            text_color="#8BE9B7" if running else "#FFD166",
        )

>>>>>>> origin/dev
    def show_page(self, page_name):
        if page_name not in self.pages:
            return

        if self.current_page is not None:
            self.current_page.destroy()

        page_class = self.pages[page_name]
<<<<<<< HEAD
        self.current_page = page_class(
            self.page_container, on_navigate=self.show_page, state=self.app_state
        )
        self.current_page.grid(row=0, column=0, sticky="nsew")
        self.current_name = page_name
        self.sidebar.set_active(page_name)

        refresh = getattr(self.current_page, "refresh", None)
        if page_name != "Accueil" and callable(refresh):
            refresh()

    # ------------------------------------------------------------------
    # Cycle de vie et adaptabilité
    # ------------------------------------------------------------------
    def _on_root_configure(self, _event=None):
        width = self.winfo_width()
        if width < 1:
            return
        scaling = ctk.ScalingTracker.get_window_dpi_scaling(self)
        logical_width = width / scaling if scaling else width
        compact = logical_width < self.COMPACT_BREAKPOINT
        if compact == self._compact:
            return
        self._compact = compact
        self.grid_columnconfigure(
            0, minsize=self.COMPACT_WIDTH if compact else self.SIDEBAR_WIDTH
        )
        self.sidebar.set_compact(compact)

    def _schedule_status_refresh(self):
        self.header.refresh()
        self._status_job = self.after(10000, self._schedule_status_refresh)

    def _on_close(self):
        if self._status_job is not None:
            try:
                self.after_cancel(self._status_job)
            except Exception:
                pass
        self.app_state.shutdown()
=======
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
>>>>>>> origin/dev
        self.destroy()
