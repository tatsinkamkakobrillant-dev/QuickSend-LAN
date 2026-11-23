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

        self.body = ctk.CTkFrame(self, fg_color="transparent")
        self.body.pack(fill="both", expand=True)

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
        )
        self.welcome_frame.pack(fill="x", pady=(0, 10))

        ctk.CTkLabel(
            self.welcome_frame,
            text="Bienvenue sur QuickSend LAN !",
            font=("Arial", 20, "bold"),
            text_color="#142D4E",
        ).pack(anchor="w", padx=20, pady=(15, 5))

        ctk.CTkLabel(
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

        self.stats_frame.grid_columnconfigure(0, weight=1)
        self.stats_frame.grid_columnconfigure(1, weight=1)

        # Fonctions principales
        ctk.CTkLabel(
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
            )

        self.actions_frame.grid_columnconfigure(0, weight=1)
        self.actions_frame.grid_columnconfigure(1, weight=1)

        # État du réseau
        self.network_frame = ctk.CTkFrame(
            self.right_panel,
            fg_color="white",
            corner_radius=12,
            border_width=1,
            border_color="#DCE5F2",
        )
        self.network_frame.pack(fill="x", pady=(0, 10))

        ctk.CTkLabel(
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

    def navigate(self, page_name):
        if self.on_navigate:
            self.on_navigate(page_name)

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
