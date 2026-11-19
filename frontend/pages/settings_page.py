
import os
import customtkinter as ctk
from tkinter import filedialog, messagebox


class SettingsPage(ctk.CTkFrame):

    def __init__(self, parent):
        super().__init__(parent, fg_color="transparent")

        self.receive_folder = os.path.join(
            os.path.expanduser("~"),
            "Downloads",
            "QuickSend"
        )
        os.makedirs(self.receive_folder, exist_ok=True)

        self.udp_port = 5000

        ctk.CTkLabel(
            self,
            text="Paramètres",
            font=("Arial", 23, "bold"),
            text_color="#142D4E"
        ).pack(anchor="w", padx=20, pady=(20, 8))

        ctk.CTkLabel(
            self,
            text="Configurez les préférences de QuickSend LAN.",
            font=("Arial", 13),
            text_color="#52647A"
        ).pack(anchor="w", padx=20, pady=(0, 20))

        self.settings_frame = ctk.CTkFrame(
            self,
            fg_color="white",
            corner_radius=12,
            border_width=1,
            border_color="#DCE5F2"
        )
        self.settings_frame.pack(
            fill="both",
            expand=True,
            padx=20,
            pady=10
        )

        # Dossier de réception
        ctk.CTkLabel(
            self.settings_frame,
            text="Dossier de réception",
            font=("Arial", 15, "bold"),
            text_color="#142D4E"
        ).pack(anchor="w", padx=25, pady=(30, 8))

        self.folder_label = ctk.CTkLabel(
            self.settings_frame,
            text=self.receive_folder,
            font=("Arial", 12),
            text_color="#52647A",
            wraplength=650
        )
        self.folder_label.pack(anchor="w", padx=25, pady=5)

        ctk.CTkButton(
            self.settings_frame,
            text="Modifier le dossier",
            command=self.choose_folder
        ).pack(anchor="w", padx=25, pady=10)

        # Port UDP
        ctk.CTkLabel(
            self.settings_frame,
            text="Port de communication UDP",
            font=("Arial", 15, "bold"),
            text_color="#142D4E"
        ).pack(anchor="w", padx=25, pady=(25, 8))

        self.port_entry = ctk.CTkEntry(
            self.settings_frame,
            width=180,
            height=38
        )
        self.port_entry.insert(0, str(self.udp_port))
        self.port_entry.pack(anchor="w", padx=25, pady=5)

        ctk.CTkButton(
            self.settings_frame,
            text="Enregistrer les paramètres",
            fg_color="#168653",
            hover_color="#116B42",
            command=self.save_settings
        ).pack(anchor="w", padx=25, pady=25)

    def choose_folder(self):

        folder = filedialog.askdirectory(
            title="Choisir le dossier de réception",
            initialdir=self.receive_folder
        )

        if folder:
            self.receive_folder = folder
            self.folder_label.configure(text=folder)

    def save_settings(self):

        try:
            port = int(self.port_entry.get())

            if not 1 <= port <= 65535:
                raise ValueError

            self.udp_port = port

            messagebox.showinfo(
                "Paramètres",
                "Les paramètres ont été enregistrés pour cette session."
            )

        except ValueError:
            messagebox.showerror(
                "Erreur",
                "Veuillez saisir un port UDP valide entre 1 et 65535."
            )
