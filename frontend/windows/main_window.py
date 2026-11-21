
import customtkinter as ctk

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

    def __init__(self):
        super().__init__()

        self.title("QuickSend LAN")
        self.geometry("1250x780")
        self.minsize(1050, 680)
        self.configure(fg_color="#F3F6FA")

        # Menu latéral
        self.sidebar = Sidebar(
            self,
            on_navigate=self.show_page
        )
        self.sidebar.pack(side="left", fill="y")

        # Zone principale
        self.content_area = ctk.CTkFrame(
            self,
            fg_color="#F3F6FA",
            corner_radius=0
        )
        self.content_area.pack(
            side="right",
            fill="both",
            expand=True,
            padx=15,
            pady=12
        )

        self.content_area.grid_columnconfigure(0, weight=1)
        self.content_area.grid_rowconfigure(1, weight=1)
        self.content_area.grid_rowconfigure(2, minsize=48, weight=0)

        # Bandeau supérieur
        self.header = Header(self.content_area)
        self.header.configure(height=82)
        self.header.grid(
            row=0,
            column=0,
            sticky="ew",
            pady=(0, 12)
        )

        # Conteneur des pages
        self.page_container = ctk.CTkFrame(
            self.content_area,
            fg_color="transparent"
        )
        self.page_container.grid(
            row=1,
            column=0,
            sticky="nsew",
            pady=(0, 10)
        )

        # Pied de page
        self.footer = Footer(self.content_area)
        self.footer.configure(height=42)
        self.footer.grid(
            row=2,
            column=0,
            sticky="ew"
        )

        # Correspondance entre menu et pages
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

        # Afficher la page d'accueil au démarrage
        self.show_page("Accueil")

    def show_page(self, page_name):

        if page_name not in self.pages:
            return

        # Supprimer l'ancienne page
        if self.current_page is not None:
            self.current_page.destroy()

        # Créer la nouvelle page
        page_class = self.pages[page_name]

        if page_name == "Accueil":
            self.current_page = page_class(
                self.page_container,
                on_navigate=self.show_page
            )
        else:
            self.current_page = page_class(
                self.page_container
            )

        self.current_page.pack(
            fill="both",
            expand=True
        )

        # Actualiser le menu actif
        self.sidebar.set_active(page_name)
