<<<<<<< HEAD
"""Page d'accueil : synthèse réelle du service, du réseau et de l'historique."""

import tkinter as tk

import customtkinter as ctk

from frontend.components.icons import get_icon
from frontend.services.app_state import UNAVAILABLE

NAVY_TEXT = "#041E53"
MUTED = "#52647A"
GREEN = "#0A720B"
BLUE = "#0B62F2"
ORANGE = "#A85C00"
RED = "#A4252B"


class StatCard(ctk.CTkFrame):

    def __init__(self, parent, title, background, border, value_color):
        super().__init__(
            parent, fg_color=background, corner_radius=10,
            border_width=1, border_color=border, height=105
        )
        self.pack_propagate(False)

        ctk.CTkLabel(
            self, text=title, font=("Segoe UI", 14, "bold"),
            text_color=NAVY_TEXT
        ).place(x=16, y=10)

        self.value_label = ctk.CTkLabel(
            self, text="…", font=("Segoe UI", 26, "bold"),
            text_color=value_color
        )
        self.value_label.place(x=16, y=38)

        self.description_label = ctk.CTkLabel(
            self, text="Chargement…", font=("Segoe UI", 11),
            text_color=MUTED
        )
        self.description_label.place(x=16, y=79)

        self.badge = ctk.CTkLabel(
            self, text="", font=("Segoe UI", 9, "bold"),
            text_color=GREEN, fg_color="#CDF0E2", corner_radius=10
        )
        self.badge.place(relx=1, x=-12, y=12, anchor="ne")

    def set_value(self, value, description=None):
        self.value_label.configure(text=str(value))
        if description is not None:
            self.description_label.configure(text=description)

    def set_badge(self, text, color=GREEN, background="#CDF0E2"):
        self.badge.configure(text=text, text_color=color, fg_color=background)


class FeatureCard(ctk.CTkFrame):
    """Carte cliquable, utilisable à la souris et au clavier."""

    def __init__(self, parent, icon_name, icon_color, title,
                 description, command=None):
        super().__init__(
            parent, fg_color="#F0F3FA", corner_radius=8,
            border_width=1, border_color="#CFD8E8", height=62
        )
        self.pack_propagate(False)
        tk.Frame.configure(self, takefocus="true")

        self.command = command
        self.default_background = "#F0F3FA"
        self.default_border = "#CFD8E8"

        icon = ctk.CTkLabel(
            self, text="",
            image=get_icon(icon_name, icon_color, 26),
            fg_color="transparent"
        )
        icon.place(x=14, y=18)

        ctk.CTkLabel(
            self, text=title, font=("Segoe UI", 13, "bold"),
            text_color=NAVY_TEXT
        ).place(x=52, y=9)

        ctk.CTkLabel(
            self, text=description, font=("Segoe UI", 10),
            text_color=MUTED
        ).place(x=52, y=35)

        self.bind("<Button-1>", self._invoke)
        self.bind("<Return>", self._invoke)
        self.bind("<space>", self._invoke)
        self.bind("<Enter>", self._on_enter)
        self.bind("<Leave>", self._on_leave)
        self.bind("<FocusIn>", self._on_focus)
        self.bind("<FocusOut>", self._on_focus_out)

    def _invoke(self, _event=None):
        if self.command:
            self.command()

    def _on_enter(self, _event=None):
        self.configure(fg_color="#E4EDFB", border_color="#8FB6EE")

    def _on_leave(self, _event=None):
        if not self.focus_get() == self:
            self.configure(fg_color=self.default_background,
                           border_color=self.default_border)

    def _on_focus(self, _event=None):
        self.configure(fg_color="#E4EDFB", border_color=BLUE)

    def _on_focus_out(self, _event=None):
        self.configure(fg_color=self.default_background,
                       border_color=self.default_border)


class TransferRow(ctk.CTkFrame):

    STATUS = {
        "terminé": ("Terminé", "check", GREEN),
        "réussi": ("Terminé", "check", GREEN),
        "success": ("Terminé", "check", GREEN),
        "échec": ("Échec", "close", RED),
        "failed": ("Échec", "close", RED),
        "en cours": ("En cours", "clock", ORANGE),
    }

    def __init__(self, parent, entry, format_time):
        super().__init__(parent, fg_color="transparent", height=40)
        self.pack_propagate(False)

        direction = str(entry.get("direction", "")).strip().lower()
        received = direction.startswith("reçu") or direction == "received"
        icon_name = "download" if received else "upload"
        icon_color = GREEN if received else BLUE

        ctk.CTkLabel(
            self, text="",
            image=get_icon(icon_name, icon_color, 22),
            fg_color="transparent"
        ).place(x=6, y=8)

        filename = str(entry.get("filename", UNAVAILABLE))
        peer = str(entry.get("peer", UNAVAILABLE))
        verb = "Reçu de" if received else "Envoyé à"
        ctk.CTkLabel(
            self, text=filename, font=("Segoe UI", 12, "bold"),
            text_color=NAVY_TEXT, anchor="w"
        ).place(x=36, y=2, relwidth=0.55)

        ctk.CTkLabel(
            self, text=f"{verb} {peer}", font=("Segoe UI", 10),
            text_color=MUTED, anchor="w"
        ).place(x=36, y=21, relwidth=0.55)

        ctk.CTkLabel(
            self, text=format_time(str(entry.get("created_at", ""))),
            font=("Segoe UI", 10), text_color=MUTED
        ).place(relx=0.86, y=7)

        status = str(entry.get("status", "")).strip().lower()
        label, status_icon, color = self.STATUS.get(
            status, (status or UNAVAILABLE, "clock", ORANGE)
        )
        ctk.CTkLabel(
            self, text="",
            image=get_icon(status_icon, color, 15),
            fg_color="transparent"
        ).place(relx=1, x=-66, y=6)
        ctk.CTkLabel(
            self, text=label, font=("Segoe UI", 9, "bold"),
            text_color=color, anchor="e", width=58
        ).place(relx=1, x=-6, y=8, anchor="ne")


class NetworkCard(ctk.CTkFrame):

    def __init__(self, parent):
        super().__init__(
            parent, fg_color="#F8F9FE", corner_radius=10,
            border_width=1, border_color="#CBD6F0"
        )

        banner = ctk.CTkFrame(self, fg_color="#0C2D58", corner_radius=8, height=46)
        banner.pack(fill="x", padx=1, pady=1)
        banner.pack_propagate(False)

        ctk.CTkLabel(
            banner, text="",
            image=get_icon("wifi", "#8FB6EE", 26),
            fg_color="transparent"
        ).place(x=16, y=10)

        ctk.CTkLabel(
            banner, text="État du réseau",
            font=("Segoe UI", 15, "bold"),
            text_color="#FFFFFF"
        ).place(x=52, y=10)

        body = ctk.CTkFrame(self, fg_color="transparent")
        body.pack(fill="x", padx=16, pady=(12, 14))

        self.status_label = ctk.CTkLabel(
            body, text="Vérification…",
            font=("Segoe UI", 13, "bold"), text_color=ORANGE, anchor="w"
        )
        self.status_label.grid(row=0, column=0, columnspan=2, sticky="w", pady=(0, 10))

        self.values = {}
        rows = [
            ("Type de réseau", "type"),
            ("Passerelle", "gateway"),
            ("Masque de sous-réseau", "mask"),
        ]
        for index, (title, key) in enumerate(rows, start=1):
            ctk.CTkLabel(
                body, text=title, font=("Segoe UI", 11),
                text_color=MUTED, anchor="w"
            ).grid(row=index, column=0, sticky="w", pady=4)
            value = ctk.CTkLabel(
                body, text=UNAVAILABLE, font=("Segoe UI", 11, "bold"),
                text_color=NAVY_TEXT, anchor="e"
            )
            value.grid(row=index, column=1, sticky="e", pady=4, padx=(12, 0))
            self.values[key] = value

        body.grid_columnconfigure(0, weight=1)
        body.grid_columnconfigure(1, weight=0)

    def set_info(self, info, status):
        label, _detail, color = status
        text = {
            "En ligne": "Réseau fonctionnel",
            "Connexion limitée": "Connexion limitée",
            "Hors ligne": "Hors ligne",
            "Indisponible": UNAVAILABLE,
        }.get(label, label)
        self.status_label.configure(text=text, text_color=color)
        for key, widget in self.values.items():
            widget.configure(text=info.get(key) or UNAVAILABLE)


class AddressRibbon(ctk.CTkFrame):

    def __init__(self, parent):
        super().__init__(
            parent, fg_color="#DBE9FE", corner_radius=8,
            border_width=1, border_color="#9DC1FB", height=48
        )
        self.pack_propagate(False)

        ctk.CTkLabel(
            self, text="",
            image=get_icon("info", BLUE, 22),
            fg_color="transparent"
        ).place(x=12, y=13)

        self.labels = {}
        for column, key in enumerate(("ip", "port", "type")):
            label = ctk.CTkLabel(
                self, text=UNAVAILABLE, font=("Segoe UI", 11),
                text_color=NAVY_TEXT, anchor="w"
            )
            label.grid(row=0, column=column, sticky="w", padx=(48 if column == 0 else 18, 6))
            self.labels[key] = label
            self.grid_columnconfigure(column, weight=1)

    def set_info(self, info):
        self.labels["ip"].configure(text=f"Mon adresse IP : {info.get('ip', UNAVAILABLE)}")
        self.labels["port"].configure(text=f"Port UDP : {info.get('port', UNAVAILABLE)}")
        self.labels["type"].configure(text=f"Réseau : {info.get('type', UNAVAILABLE)}")


class HomePage(ctk.CTkFrame):

    def __init__(self, parent, on_navigate=None, state=None):
        super().__init__(parent, fg_color="transparent")

        self.on_navigate = on_navigate
        self.state = state
        self.stacked = None
        self.action_columns = None
=======
"""Page d'accueil : état du réseau, statistiques et derniers transferts."""

from __future__ import annotations

import threading

import customtkinter as ctk

from feature.transfer_service import get_local_ip


class HomePage(ctk.CTkFrame):
    def __init__(self, parent, on_navigate=None, service=None):
        super().__init__(parent, fg_color="transparent")

        self.on_navigate = on_navigate
        self.service = service
        self.local_ip = get_local_ip()
        self.port = service.port if service else 5000
>>>>>>> origin/dev

        self.grid_columnconfigure(0, weight=804)
        self.grid_columnconfigure(1, weight=414)
        self.grid_rowconfigure(0, weight=1)

<<<<<<< HEAD
        self.left_panel = ctk.CTkFrame(self, fg_color="transparent")
        self.left_panel.grid(row=0, column=0, sticky="nsew", padx=(0, 10))
        self.left_panel.grid_columnconfigure(0, weight=1)

        self.right_panel = ctk.CTkFrame(self, fg_color="transparent")
        self.right_panel.grid(row=0, column=1, sticky="nsew")
        self.right_panel.grid_columnconfigure(0, weight=1)

        self._build_welcome()
        self._build_stats()
        self._build_actions()
        self._build_ribbon()
        self._build_network()
        self._build_transfers()

        self.bind("<Configure>", self._on_configure)
        self.refresh()

    # ------------------------------------------------------------------
    # Construction
    # ------------------------------------------------------------------
    def _build_welcome(self):
        card = ctk.CTkFrame(
            self.left_panel, fg_color="#FFFFFF", corner_radius=12,
            border_width=1, border_color="#DCE5F2", height=92
=======
        self.center_panel = ctk.CTkFrame(self.body, fg_color="transparent")
        self.center_panel.pack(side="left", fill="both", expand=True, padx=(0, 8))

        self.right_panel = ctk.CTkFrame(self.body, fg_color="transparent", width=290)
        self.right_panel.pack(side="right", fill="y")
        self.right_panel.pack_propagate(False)

        # Bienvenue
        self.welcome_frame = ctk.CTkFrame(
            self.center_panel,
            fg_color="white",
            corner_radius=12,
            border_width=1,
            border_color="#DCE5F2",
>>>>>>> origin/dev
        )
        card.pack(fill="x")
        card.pack_propagate(False)

        ctk.CTkLabel(
<<<<<<< HEAD
            card, text="",
            image=get_icon("monitor", BLUE, 58),
            fg_color="transparent"
        ).place(x=18, y=17)
=======
            self.welcome_frame,
            text="Bienvenue sur QuickSend LAN !",
            font=("Arial", 20, "bold"),
            text_color="#142D4E",
        ).pack(anchor="w", padx=20, pady=(15, 5))
>>>>>>> origin/dev

        texts = ctk.CTkFrame(card, fg_color="transparent")
        texts.place(x=96, y=16, relwidth=0.86)
        ctk.CTkLabel(
<<<<<<< HEAD
            texts, text="Bienvenue sur QuickSend LAN !",
            font=("Segoe UI", 17, "bold"), text_color=NAVY_TEXT,
            anchor="w"
        ).pack(anchor="w")
        ctk.CTkLabel(
            texts,
            text="Partagez vos fichiers facilement avec les autres ordinateurs du réseau.",
            font=("Segoe UI", 11), text_color=MUTED, anchor="w"
        ).pack(anchor="w", pady=(6, 0))

    def _build_stats(self):
        frame = ctk.CTkFrame(self.left_panel, fg_color="transparent", height=105)
        frame.pack(fill="x", pady=(10, 0))
        frame.pack_propagate(False)

        self.devices_card = StatCard(
            frame, "Appareils détectés", "#DBE9FD", "#95BDFD", BLUE
        )
        self.devices_card.grid(row=0, column=0, sticky="nsew", padx=(0, 5))

        self.transfers_card = StatCard(
            frame, "Transferts effectués", "#D2F3E5", "#9FD7CE", "#168653"
        )
        self.transfers_card.grid(row=0, column=1, sticky="nsew", padx=(5, 0))
        frame.grid_columnconfigure(0, weight=1)
        frame.grid_columnconfigure(1, weight=1)

    def _build_actions(self):
        heading = ctk.CTkFrame(self.left_panel, fg_color="transparent", height=34)
        heading.pack(fill="x", pady=(14, 0))
        heading.pack_propagate(False)
=======
            self.welcome_frame,
            text="Transférez vos fichiers par UDP entre ordinateurs du même réseau local.",
            font=("Arial", 12),
            text_color="#263F69",
            wraplength=650,
        ).pack(anchor="w", padx=20, pady=(0, 15))

        # Statistiques
        self.stats_frame = ctk.CTkFrame(self.center_panel, fg_color="transparent")
        self.stats_frame.pack(fill="x", pady=(0, 12))

        _, self.devices_value = self.create_stat_card(
            self.stats_frame,
            "Appareils détectés",
            "0",
            "Sur le réseau local",
            "#DCEAFF",
            "#A9C9F5",
            "#0866D9",
            0,
        )
        _, self.transfers_value = self.create_stat_card(
            self.stats_frame,
            "Transferts effectués",
            "0",
            "Depuis le démarrage",
            "#D8F3E8",
            "#A9E2C9",
            "#168653",
            1,
        )
>>>>>>> origin/dev

        ctk.CTkLabel(
<<<<<<< HEAD
            heading, text="",
            image=get_icon("bolt", "#F48F0C", 22),
            fg_color="transparent"
        ).place(x=0, y=5)

        ctk.CTkLabel(
            heading, text="Fonctions principales",
            font=("Segoe UI", 16, "bold"), text_color=NAVY_TEXT
        ).place(x=32, y=5)

        self.actions_grid = ctk.CTkFrame(self.left_panel, fg_color="transparent")
        self.actions_grid.pack(fill="x", pady=(8, 0))
        self.actions_grid.grid_columnconfigure(0, weight=1)
        self.actions_grid.grid_columnconfigure(1, weight=1)

        actions = [
            ("upload", BLUE, "Envoyer un fichier",
             "Partager un document, une image…", "Envoyer un fichier"),
            ("download", "#168653", "Recevoir un fichier",
             "Accepter des fichiers entrants", "Recevoir un fichier"),
            ("monitor", "#4D2DC1", "Voir les appareils",
             "Découvrir les ordinateurs du LAN", "Appareils"),
            ("gear", "#F48F0C", "Paramètres",
             "Configurer l'application", "Paramètres"),
        ]

        self.action_cards = [
            FeatureCard(
                self.actions_grid, icon, color, title, description,
                command=lambda page=page: self.navigate(page)
=======
            self.center_panel,
            text="Fonctions principales",
            font=("Arial", 17, "bold"),
            text_color="#142D4E",
        ).pack(anchor="w", pady=(2, 8))

        self.actions_frame = ctk.CTkFrame(self.center_panel, fg_color="transparent")
        self.actions_frame.pack(fill="x")

        actions = [
            ("Envoyer un fichier", "#1769D2", "Envoyer un fichier"),
            ("Recevoir un fichier", "#168653", "Recevoir un fichier"),
            ("Voir les appareils", "#7355C5", "Appareils"),
            ("Paramètres", "#52647A", "Paramètres"),
        ]
        for index, (name, color, page) in enumerate(actions):
            ctk.CTkButton(
                self.actions_frame,
                text=name,
                height=48,
                fg_color=color,
                hover_color=color,
                font=("Arial", 12, "bold"),
                corner_radius=9,
                command=lambda p=page: self.navigate(p),
            ).grid(
                row=index // 2,
                column=index % 2,
                padx=5,
                pady=5,
                sticky="ew",
>>>>>>> origin/dev
            )
            for icon, color, title, description, page in actions
        ]
        self._apply_action_columns(2)

    def _build_ribbon(self):
        self.ribbon = AddressRibbon(self.left_panel)
        self.ribbon.pack(fill="x", pady=(14, 0))

<<<<<<< HEAD
    def _build_network(self):
        self.network_card = NetworkCard(self.right_panel)
        self.network_card.pack(fill="x")

    def _build_transfers(self):
        card = ctk.CTkFrame(
            self.right_panel, fg_color="#FFFFFF", corner_radius=10,
            border_width=1, border_color="#CBD6F0"
=======
        # État du réseau
        self.network_frame = ctk.CTkFrame(
            self.right_panel,
            fg_color="white",
            corner_radius=12,
            border_width=1,
            border_color="#DCE5F2",
>>>>>>> origin/dev
        )
        card.pack(fill="both", expand=True, pady=(14, 0))

        banner = ctk.CTkFrame(card, fg_color="#EAF1FA", corner_radius=8, height=42)
        banner.pack(fill="x", padx=1, pady=1)
        banner.pack_propagate(False)
        ctk.CTkLabel(
<<<<<<< HEAD
            banner, text="Derniers transferts",
            font=("Segoe UI", 14, "bold"), text_color="#082F64"
        ).place(x=14, y=9)

        self.transfers_list = ctk.CTkFrame(card, fg_color="transparent")
        self.transfers_list.pack(fill="both", expand=True, padx=10, pady=(8, 4))

        self.empty_label = ctk.CTkLabel(
            self.transfers_list,
            text="Aucun transfert enregistré pour le moment.",
            font=("Segoe UI", 11), text_color=MUTED
        )
        self.empty_label.pack(pady=18)

        ctk.CTkButton(
            card, text="Voir tout l'historique",
            image=get_icon("chevron", NAVY_TEXT, 16),
            compound="right", anchor="center",
            height=38, fg_color="#DDE5F2", hover_color="#C9D6EA",
            text_color=NAVY_TEXT, font=("Segoe UI", 12, "bold"),
            corner_radius=8, command=lambda: self.navigate("Historique")
        ).pack(fill="x", padx=14, pady=(4, 14))

    # ------------------------------------------------------------------
    # Données
    # ------------------------------------------------------------------
    def refresh(self):
        if self.state is None:
            return
        self.devices_card.set_value("…", "Recherche d'appareils…")
        self.devices_card.set_badge("Analyse", BLUE, "#DBE9FD")
        self.transfers_card.set_value("…", "Lecture de l'historique…")

        info = self.state.network_info()
        self.ribbon.set_info(info)
        self.network_card.set_info(info, self.state.status())

        self.state.refresh_devices_async(self, self._devices_ready)
        self.state.refresh_history_async(self, self._history_ready)

    def _devices_ready(self, devices, error_message, _error):
        if error_message:
            self.devices_card.set_value(UNAVAILABLE, "Découverte indisponible")
            self.devices_card.set_badge(UNAVAILABLE, ORANGE, "#FBE8CE")
            return

        self.devices_card.set_value(len(devices), "Appareils détectés")
        if not self.state or not self.state.running:
            self.devices_card.set_badge("Service arrêté", ORANGE, "#FBE8CE")
        elif devices:
            self.devices_card.set_badge("Détectés", GREEN, "#CDF0E2")
        else:
            self.devices_card.set_badge("Aucun", MUTED, "#E4E8F0")

    def _history_ready(self, history, error_message, _error):
        if error_message:
            self.transfers_card.set_value(UNAVAILABLE, "Historique indisponible")
        else:
            total = self.state.transfer_count() if self.state else len(history)
            self.transfers_card.set_value(total, "Depuis le début de l'historique")
        self._render_transfers(history)

    def _render_transfers(self, history):
        for widget in self.transfers_list.winfo_children():
            widget.destroy()

        if not history:
            ctk.CTkLabel(
                self.transfers_list,
                text="Aucun transfert enregistré pour le moment.",
                font=("Segoe UI", 11), text_color=MUTED
            ).pack(pady=18)
            return

        for entry in history[:4]:
            TransferRow(
                self.transfers_list, entry, self.state.format_time
            ).pack(fill="x", pady=2)

    # ------------------------------------------------------------------
    # Adaptation de la mise en page
    # ------------------------------------------------------------------
    def _apply_action_columns(self, columns):
        if columns == self.action_columns:
            return
        self.action_columns = columns
        for index, card in enumerate(self.action_cards):
            card.grid(
                row=index // columns, column=index % columns,
                sticky="nsew",
                padx=(0, 5) if columns == 2 and index % 2 == 0 else (
                    (5, 0) if columns == 2 else (0, 5)
                ),
                pady=(0, 10) if index // columns == 0 else 0
            )
        self.actions_grid.grid_columnconfigure(0, weight=1)
        self.actions_grid.grid_columnconfigure(1, weight=1 if columns == 2 else 0)

    def _on_configure(self, event):
        scaling = ctk.ScalingTracker.get_window_dpi_scaling(self)
        width = event.width / scaling if scaling else event.width
        stacked = width < 880
        if stacked != self.stacked:
            self.stacked = stacked
            if stacked:
                self.grid_columnconfigure(0, weight=1)
                self.grid_columnconfigure(1, weight=0)
                self.grid_rowconfigure(0, weight=0)
                self.grid_rowconfigure(1, weight=1)
                self.left_panel.grid(row=0, column=0, sticky="nsew", padx=0)
                self.right_panel.grid(row=1, column=0, sticky="nsew", pady=(14, 0))
            else:
                self.grid_columnconfigure(0, weight=804)
                self.grid_columnconfigure(1, weight=414)
                self.grid_rowconfigure(0, weight=1)
                self.grid_rowconfigure(1, weight=0)
                self.left_panel.grid(row=0, column=0, sticky="nsew", padx=(0, 10))
                self.right_panel.grid(row=0, column=1, sticky="nsew")
        self._apply_action_columns(1 if width < 620 else 2)
=======
            self.network_frame,
            text="État du réseau",
            font=("Arial", 16, "bold"),
            text_color="#142D4E",
        ).pack(anchor="w", padx=15, pady=(12, 8))

        connected = self.local_ip != "Non disponible" and bool(
            self.service and self.service.is_running
        )
        ctk.CTkLabel(
            self.network_frame,
            text="● Récepteur UDP actif" if connected else "● Récepteur UDP arrêté",
            font=("Arial", 12, "bold"),
            text_color="#168653" if connected else "#D18A20",
        ).pack(anchor="w", padx=15, pady=3)

        for info in [
            f"Adresse IP : {self.local_ip}",
            f"Port UDP : {self.port}",
        ]:
            ctk.CTkLabel(
                self.network_frame,
                text=info,
                font=("Arial", 11),
                text_color="#52647A",
            ).pack(anchor="w", padx=15, pady=5)

        # Derniers transferts
        self.recent_frame = ctk.CTkFrame(
            self.right_panel,
            fg_color="white",
            corner_radius=12,
            border_width=1,
            border_color="#DCE5F2",
        )
        self.recent_frame.pack(fill="both", expand=True)

        ctk.CTkLabel(
            self.recent_frame,
            text="Derniers transferts",
            font=("Arial", 16, "bold"),
            text_color="#142D4E",
        ).pack(anchor="w", padx=15, pady=(12, 8))

        self.recent_list = ctk.CTkScrollableFrame(
            self.recent_frame,
            fg_color="transparent",
        )
        self.recent_list.pack(fill="both", expand=True, padx=10, pady=(0, 10))
        self._discover_devices()

    def _discover_devices(self) -> None:
        if not self.service:
            return

        def worker():
            devices = self.service.discover_devices(timeout=1.0)

            def update():
                if self._alive():
                    self.devices_value.configure(text=str(len(devices)))

            try:
                self.after(0, update)
            except Exception:
                pass

        threading.Thread(target=worker, daemon=True).start()

    def _alive(self) -> bool:
        try:
            return bool(self.winfo_exists())
        except Exception:
            return False

    def refresh(self) -> None:
        if not self._alive():
            return
        history = self.service.get_history(limit=5) if self.service else []
        self.transfers_value.configure(text=str(len(history)))

        for widget in list(self.recent_list.winfo_children()):
            widget.destroy()

        if not history:
            ctk.CTkLabel(
                self.recent_list,
                text="Aucun transfert enregistré.",
                font=("Arial", 12),
                text_color="#718096",
            ).pack(pady=20)
            return

        for row in history:
            icon = "↑" if row["direction"] == "envoyé" else "↓"
            color = "#168653" if row["status"] == "terminé" else "#D18A20"
            line = ctk.CTkFrame(self.recent_list, fg_color="#F3F6FA", corner_radius=8)
            line.pack(fill="x", pady=3)
            ctk.CTkLabel(
                line,
                text=f"{icon} {row['filename']}",
                font=("Arial", 11, "bold"),
                text_color="#142D4E",
                anchor="w",
            ).pack(fill="x", padx=8, pady=(5, 0))
            ctk.CTkLabel(
                line,
                text=f"{row['peer']} · {row['status']}",
                font=("Arial", 10),
                text_color=color,
                anchor="w",
            ).pack(fill="x", padx=8, pady=(0, 5))
>>>>>>> origin/dev

    def navigate(self, page_name):
        if self.on_navigate:
            self.on_navigate(page_name)
<<<<<<< HEAD
=======

    @staticmethod
    def create_stat_card(
        parent,
        title,
        value,
        description,
        background,
        border,
        value_color,
        column,
    ):
        card = ctk.CTkFrame(
            parent,
            fg_color=background,
            corner_radius=10,
            border_width=1,
            border_color=border,
        )
        card.grid(
            row=0,
            column=column,
            padx=(0, 6) if column == 0 else (6, 0),
            sticky="nsew",
        )

        ctk.CTkLabel(
            card,
            text=title,
            font=("Arial", 14, "bold"),
            text_color="#142D4E",
        ).pack(pady=(12, 3))

        value_label = ctk.CTkLabel(
            card,
            text=value,
            font=("Arial", 27, "bold"),
            text_color=value_color,
        )
        value_label.pack(pady=2)

        ctk.CTkLabel(
            card,
            text=description,
            font=("Arial", 11),
            text_color="#263F69",
        ).pack(pady=(2, 12))

        return card, value_label
>>>>>>> origin/dev
