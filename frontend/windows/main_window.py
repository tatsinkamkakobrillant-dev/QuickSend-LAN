
import customtkinter as ctk

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

    SIDEBAR_WIDTH = 190
    COMPACT_WIDTH = 68
    FOOTER_HEIGHT = 42
    TOPBAR_HEIGHT = 40
    HEADER_HEIGHT = 95
    COMPACT_BREAKPOINT = 1050

    def __init__(self):
        super().__init__()

        self.title("QuickSend LAN")
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

        self.topbar = TopBar(self.workspace)
        self.topbar.grid(row=0, column=0, sticky="ew")

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

        self.pages = {
            "Accueil": HomePage,
            "Appareils": DevicesPage,
            "Envoyer un fichier": SendPage,
            "Recevoir un fichier": ReceivePage,
            "Historique": HistoryPage,
            "Paramètres": SettingsPage,
            "À propos": AboutPage
        }

        self.current_page = None
        self.current_name = None
        self.show_page("Accueil")

        self.bind("<Configure>", self._on_root_configure)
        self.protocol("WM_DELETE_WINDOW", self._on_close)
        self.after(150, self._on_root_configure)
        self._schedule_status_refresh()

    # ------------------------------------------------------------------
    # Navigation
    # ------------------------------------------------------------------
    def show_page(self, page_name):
        if page_name not in self.pages:
            return

        if self.current_page is not None:
            self.current_page.destroy()

        page_class = self.pages[page_name]
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
        self.destroy()
