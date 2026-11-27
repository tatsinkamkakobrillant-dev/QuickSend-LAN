"""Menu latéral sombre de QuickSend LAN."""

import tkinter as tk

import customtkinter as ctk

from frontend.components.icons import get_icon

NAVY = "#01234F"
BLUE = "#006BF7"
HOVER = "#0B54A8"
WHITE = "#FFFFFF"
COMPACT_WIDTH = 68
FULL_WIDTH = 190

ITEM_TOP = 148
ITEM_HEIGHT = 44
ITEM_GAP = 4


class SidebarItem(ctk.CTkButton):

    def __init__(self, parent, name, icon_name, command=None):
        super().__init__(
            parent,
            text=name,
            image=get_icon(icon_name, WHITE, 22),
            compound="left",
            anchor="w",
            border_spacing=10,
            width=174,
            height=ITEM_HEIGHT,
            corner_radius=10,
            fg_color="transparent",
            hover_color=HOVER,
            text_color="#D8E4F7",
            font=("Segoe UI", 13),
            command=lambda: command(name) if command else None,
            cursor="hand2",
        )
        self.name = name
        self.active = False

    def set_active(self, active):
        self.active = active
        self.configure(
            fg_color=BLUE if active else "transparent",
            text_color=WHITE if active else "#D8E4F7",
        )

    def set_compact(self, compact):
        self.configure(
            text="" if compact else self.name,
            width=54 if compact else 174,
            anchor="center" if compact else "w",
        )


class Sidebar(ctk.CTkFrame):

    def __init__(self, parent, on_navigate=None):
        super().__init__(parent, width=FULL_WIDTH, fg_color=NAVY, corner_radius=0)

        self.pack_propagate(False)
        self.on_navigate = on_navigate
        self.buttons = {}
        self.compact = False

        self.watermark = ctk.CTkLabel(
            self, text="",
            image=get_icon("plane", "#3691F4", 60, opacity=0.28),
            fg_color="transparent"
        )
        self.watermark.place(x=60, y=52)

        self.logo_icon = ctk.CTkLabel(
            self, text="",
            image=get_icon("plane", "#FFFFFF", 22),
            fg_color="transparent"
        )
        self.logo_icon.place(x=16, y=9)

        self.logo_label = ctk.CTkLabel(
            self, text="QuickSend LAN",
            font=("Segoe UI", 14, "bold"),
            text_color=WHITE,
            width=140,
            anchor="w"
        )
        self.logo_label.place(x=46, y=10)

        items = [
            ("Accueil", "home"),
            ("Appareils", "monitor"),
            ("Envoyer un fichier", "plane"),
            ("Recevoir un fichier", "download"),
            ("Historique", "clock"),
            ("Paramètres", "gear"),
            ("À propos", "info")
        ]

        for index, (name, icon_name) in enumerate(items):
            item = SidebarItem(
                self, name, icon_name,
                command=lambda page=name: self.navigate(page)
            )
            item.place(x=8, y=ITEM_TOP + index * (ITEM_HEIGHT + ITEM_GAP))
            self.buttons[name] = item

        self.network_art = tk.Canvas(
            self, width=168, height=60,
            bg=NAVY, highlightthickness=0, bd=0
        )
        self._draw_network(self.network_art)
        self.network_art.place(x=11, rely=1, y=-106)

        self.footer_icon = ctk.CTkLabel(
            self, text="",
            image=get_icon("plane", "#8FB6EE", 16),
            fg_color="transparent"
        )
        self.footer_icon.place(x=16, rely=1, y=-50)

        self.footer_name = ctk.CTkLabel(
            self, text="QuickSend LAN",
            font=("Segoe UI", 10, "bold"),
            text_color="#D8E4F7",
            anchor="w",
            width=130
        )
        self.footer_name.place(x=38, rely=1, y=-50)

        self.footer_motto = ctk.CTkLabel(
            self, text="Connecter • Partager • Collaborer",
            font=("Segoe UI", 8),
            text_color="#8FA9D2",
            anchor="w",
            width=180
        )
        self.footer_motto.place(x=16, rely=1, y=-31)

    @staticmethod
    def _draw_network(canvas: tk.Canvas) -> None:
        """Petit motif vectoriel sans ressource externe."""

        nodes = [(20, 30), (84, 10), (148, 30), (84, 52)]
        links = [(0, 1), (1, 2), (0, 3), (3, 2), (0, 2)]
        for start, end in links:
            canvas.create_line(
                nodes[start][0], nodes[start][1],
                nodes[end][0], nodes[end][1],
                fill="#1C4C87", width=2
            )
        for index, (x, y) in enumerate(nodes):
            radius = 7 if index == 1 else 5
            canvas.create_oval(
                x - radius, y - radius, x + radius, y + radius,
                fill="#0B3A72", outline="#3691F4", width=2
            )

    def navigate(self, page_name):
        if self.on_navigate:
            self.on_navigate(page_name)

    def set_active(self, page_name):
        for name, button in self.buttons.items():
            button.set_active(name == page_name)

    def set_compact(self, compact: bool) -> None:
        """Passe en navigation icônes seules sur les fenêtres étroites."""

        if compact == self.compact:
            return
        self.compact = compact
        self.configure(width=COMPACT_WIDTH if compact else FULL_WIDTH)

        for item in self.buttons.values():
            item.place(x=6 if compact else 8)
            item.set_compact(compact)

        for widget in (
            self.watermark, self.logo_label, self.network_art,
            self.footer_icon, self.footer_name, self.footer_motto,
        ):
            if compact:
                widget.place_forget()
            else:
                if widget is self.watermark:
                    widget.place(x=60, y=52)
                elif widget is self.logo_label:
                    widget.place(x=46, y=10)
                elif widget is self.network_art:
                    widget.place(x=11, rely=1, y=-106)
                elif widget is self.footer_icon:
                    widget.place(x=16, rely=1, y=-50)
                elif widget is self.footer_name:
                    widget.place(x=38, rely=1, y=-50)
                else:
                    widget.place(x=16, rely=1, y=-31)

        self.logo_icon.place(x=23 if compact else 16, y=9)
