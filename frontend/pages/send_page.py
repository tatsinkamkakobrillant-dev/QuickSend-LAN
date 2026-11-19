
import os
import customtkinter as ctk
from tkinter import filedialog, messagebox


class SendPage(ctk.CTkFrame):

    def __init__(self, parent):
        super().__init__(
            parent,
            fg_color="transparent"
        )

        self.selected_file = None
        self.selected_device = None

        # Appareils de démonstration
        self.devices = {
            "PC-ETOUNDI": "192.168.1.10",
            "PC-MICHELLE": "192.168.1.11",
            "PC-TEST": "192.168.1.12"
        }

        ctk.CTkLabel(
            self,
            text="Envoyer un fichier",
            font=("Arial", 23, "bold"),
            text_color="#142D4E"
        ).pack(anchor="w", padx=20, pady=(20, 8))

        ctk.CTkLabel(
            self,
            text="Sélectionnez un fichier et choisissez un appareil destinataire.",
            font=("Arial", 13),
            text_color="#52647A"
        ).pack(anchor="w", padx=20, pady=(0, 20))

        self.send_frame = ctk.CTkFrame(
            self,
            fg_color="white",
            corner_radius=12,
            border_width=1,
            border_color="#DCE5F2"
        )
        self.send_frame.pack(
            fill="both",
            expand=True,
            padx=20,
            pady=10
        )

        # Informations du fichier
        self.file_label = ctk.CTkLabel(
            self.send_frame,
            text="Aucun fichier sélectionné",
            font=("Arial", 15),
            text_color="#718096"
        )
        self.file_label.pack(pady=(30, 10))

        self.file_info_label = ctk.CTkLabel(
            self.send_frame,
            text="",
            font=("Arial", 12),
            text_color="#52647A",
            justify="center"
        )
        self.file_info_label.pack(pady=5)

        # Sélection du fichier
        self.select_button = ctk.CTkButton(
            self.send_frame,
            text="Sélectionner un fichier",
            height=42,
            fg_color="#1769D2",
            hover_color="#1255AD",
            command=self.select_file
        )
        self.select_button.pack(pady=12)

        # Sélection du destinataire
        ctk.CTkLabel(
            self.send_frame,
            text="Choisir un appareil destinataire",
            font=("Arial", 14, "bold"),
            text_color="#142D4E"
        ).pack(pady=(15, 8))

        self.device_menu = ctk.CTkOptionMenu(
            self.send_frame,
            values=list(self.devices.keys()),
            width=250,
            height=38,
            fg_color="#1769D2",
            button_color="#1255AD",
            command=self.select_device
        )
        self.device_menu.set("Sélectionner un appareil")
        self.device_menu.pack(pady=5)

        self.device_info_label = ctk.CTkLabel(
            self.send_frame,
            text="Aucun appareil sélectionné",
            font=("Arial", 12),
            text_color="#718096"
        )
        self.device_info_label.pack(pady=8)

        # Bouton d'envoi
        self.send_button = ctk.CTkButton(
            self.send_frame,
            text="Envoyer le fichier",
            height=42,
            fg_color="#168653",
            hover_color="#116B42",
            state="disabled",
            command=self.send_file
        )
        self.send_button.pack(pady=15)

    def select_file(self):

        file_path = filedialog.askopenfilename(
            title="Sélectionner un fichier à envoyer"
        )

        if file_path:
            self.selected_file = file_path

            filename = os.path.basename(file_path)
            extension = os.path.splitext(filename)[1]

            file_size = os.path.getsize(file_path)

            if file_size < 1024 * 1024:
                size_text = f"{file_size / 1024:.2f} Ko"
            else:
                size_text = f"{file_size / (1024 * 1024):.2f} Mo"

            self.file_label.configure(
                text=f"Fichier sélectionné : {filename}",
                text_color="#168653"
            )

            self.file_info_label.configure(
                text=(
                    f"Extension : {extension if extension else 'Aucune'}\n"
                    f"Taille : {size_text}"
                )
            )

            self.update_send_button()

    def select_device(self, device_name):

        self.selected_device = device_name

        ip_address = self.devices[device_name]

        self.device_info_label.configure(
            text=f"Appareil : {device_name}\nAdresse IP : {ip_address}",
            text_color="#168653"
        )

        self.update_send_button()

    def update_send_button(self):

        if self.selected_file and self.selected_device:
            self.send_button.configure(state="normal")
        else:
            self.send_button.configure(state="disabled")

    def send_file(self):

        # Vérifier le fichier
        if not self.selected_file or not os.path.isfile(self.selected_file):
            messagebox.showerror(
                "Erreur",
                "Veuillez sélectionner un fichier valide."
            )
            return

        # Vérifier le destinataire
        if not self.selected_device:
            messagebox.showwarning(
                "Destinataire manquant",
                "Veuillez sélectionner un appareil destinataire."
            )
            return

        filename = os.path.basename(self.selected_file)
        ip_address = self.devices[self.selected_device]

        # Demander confirmation
        confirmation = messagebox.askyesno(
            "Confirmation du transfert",
            f"Voulez-vous préparer l'envoi de ce fichier ?\n\n"
            f"Fichier : {filename}\n"
            f"Destinataire : {self.selected_device}\n"
            f"Adresse IP : {ip_address}"
        )

        if confirmation:
            messagebox.showinfo(
                "Transfert non disponible",
                "Votre sélection est confirmée.\n\n"
                "Le transfert réel sera disponible après "
                "l'intégration du module de communication UDP."
            )
