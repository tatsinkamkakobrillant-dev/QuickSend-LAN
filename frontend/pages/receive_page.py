
import os
import customtkinter as ctk
from tkinter import filedialog, messagebox


class ReceivePage(ctk.CTkFrame):

    def __init__(self, parent):
        super().__init__(parent, fg_color="transparent")

        self.receive_folder = os.path.join(
            os.path.expanduser("~"),
            "Downloads",
            "QuickSend"
        )

        os.makedirs(self.receive_folder, exist_ok=True)

        ctk.CTkLabel(
            self,
            text="Recevoir un fichier",
            font=("Arial", 23, "bold"),
            text_color="#142D4E"
        ).pack(anchor="w", padx=20, pady=(20, 8))

        ctk.CTkLabel(
            self,
            text="Configurez le dossier dans lequel vos fichiers seront reçus.",
            font=("Arial", 13),
            text_color="#52647A"
        ).pack(anchor="w", padx=20, pady=(0, 20))

        self.receive_frame = ctk.CTkFrame(
            self,
            fg_color="white",
            corner_radius=12,
            border_width=1,
            border_color="#DCE5F2"
        )
        self.receive_frame.pack(
            fill="both",
            expand=True,
            padx=20,
            pady=10
        )

        ctk.CTkLabel(
            self.receive_frame,
            text="Dossier de réception",
            font=("Arial", 16, "bold"),
            text_color="#142D4E"
        ).pack(pady=(40, 10))

        self.folder_label = ctk.CTkLabel(
            self.receive_frame,
            text=self.receive_folder,
            font=("Arial", 12),
            text_color="#52647A",
            wraplength=650
        )
        self.folder_label.pack(pady=10, padx=20)

        ctk.CTkButton(
            self.receive_frame,
            text="Choisir un dossier",
            height=40,
            fg_color="#1769D2",
            hover_color="#1255AD",
            command=self.choose_folder
        ).pack(pady=15)

        self.status_label = ctk.CTkLabel(
            self.receive_frame,
            text="● Dossier de réception configuré",
            font=("Arial", 13, "bold"),
            text_color="#168653"
        )
        self.status_label.pack(pady=10)

        ctk.CTkLabel(
            self.receive_frame,
            text="En attente de fichiers...",
            font=("Arial", 16, "bold"),
            text_color="#142D4E"
        ).pack(pady=(30, 8))

        ctk.CTkLabel(
            self.receive_frame,
            text="La réception réelle sera activée après l'intégration du backend UDP.",
            font=("Arial", 12),
            text_color="#718096",
            wraplength=650
        ).pack(pady=5)

    def choose_folder(self):

        folder = filedialog.askdirectory(
            title="Choisir le dossier de réception",
            initialdir=self.receive_folder
        )

        if folder:
            self.receive_folder = folder

            self.folder_label.configure(
                text=self.receive_folder
            )

            self.status_label.configure(
                text="● Dossier de réception configuré",
                text_color="#168653"
            )
