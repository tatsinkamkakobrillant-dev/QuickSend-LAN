
import socket
import customtkinter as ctk


class Footer(ctk.CTkFrame):

    def __init__(self, parent):
        super().__init__(
            parent,
            fg_color="#142D4E",
            corner_radius=10,
            height=48
        )

        self.pack_propagate(False)

        ip_address = self.get_local_ip()

        information = [
            f"Adresse IP : {ip_address}",
            "Port UDP : 5000",
            "Réseau : Local (LAN)",
            "QuickSend LAN © 2026"
        ]

        for info in information:
            label = ctk.CTkLabel(
                self,
                text=info,
                font=("Arial", 11),
                text_color="white"
            )
            label.pack(
                side="left",
                padx=15,
                expand=True
            )

    @staticmethod
    def get_local_ip():
        try:
            connection = socket.socket(
                socket.AF_INET,
                socket.SOCK_DGRAM
            )
            connection.connect(("8.8.8.8", 80))
            ip_address = connection.getsockname()[0]
            connection.close()
            return ip_address

        except OSError:
            return "Non disponible"
