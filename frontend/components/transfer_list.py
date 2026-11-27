"""Liste partagée des transferts avec sélection et annulation.

Les lignes sont créées une seule fois puis mises à jour sur place : cela évite
les clignotements des cases à cocher et des boutons pendant la réception.
"""

import customtkinter as ctk

from frontend.components.icons import get_icon
from frontend.services.transfer_manager import FINAL_STATUSES, STATUS_COLORS

NAVY = "#142D4E"
MUTED = "#52647A"


class TransferListCard(ctk.CTkFrame):
    """Carte affichant les fichiers suivis et permettant de les annuler."""

    def __init__(self, parent, title, on_cancel=None, on_clear=None):
        super().__init__(
            parent, fg_color="white", corner_radius=12,
            border_width=1, border_color="#DCE5F2"
        )
        self.on_cancel = on_cancel
        self.on_clear = on_clear
        self._transfers: list[dict] = []
        self._rows: dict[int, _TransferRow] = {}
        self._vars: dict[int, ctk.BooleanVar] = {}
        self._empty_visible = True
        self._last_count_text: str | None = None
        self._cancel_selected_state: str | None = None
        self._cancel_all_state: str | None = None

        header = ctk.CTkFrame(self, fg_color="transparent")
        header.pack(fill="x", padx=14, pady=(12, 6))

        ctk.CTkLabel(
            header, text=title, font=("Segoe UI", 15, "bold"),
            text_color=NAVY, anchor="w"
        ).pack(side="left")

        self.count_label = ctk.CTkLabel(
            header, text="0 fichier", font=("Segoe UI", 11),
            text_color=MUTED
        )
        self.count_label.pack(side="right")

        self.rows = ctk.CTkScrollableFrame(
            self, fg_color="#FAFBFE", corner_radius=8, height=150
        )
        self.rows.pack(fill="both", expand=True, padx=14, pady=(4, 6))

        self.empty_label = ctk.CTkLabel(
            self.rows, text="Aucun transfert suivi pour le moment.",
            font=("Segoe UI", 11), text_color=MUTED
        )
        self.empty_label.pack(pady=18)

        actions = ctk.CTkFrame(self, fg_color="transparent")
        actions.pack(fill="x", padx=14, pady=(0, 12))

        self.cancel_selected = ctk.CTkButton(
            actions, text="Annuler la sélection", height=32,
            fg_color="#C4474D", hover_color="#A4252B",
            image=get_icon("stop", "#FFFFFF", 15),
            command=self._cancel_selected
        )
        self.cancel_selected.pack(side="left")

        self.cancel_all = ctk.CTkButton(
            actions, text="Tout annuler", height=32,
            fg_color="#E4EDFB", hover_color="#CFDFF6",
            text_color=NAVY, command=self._cancel_all
        )
        self.cancel_all.pack(side="left", padx=(8, 0))

        if on_clear is not None:
            ctk.CTkButton(
                actions, text="Nettoyer", height=32, width=90,
                fg_color="transparent", hover_color="#E4E8F0",
                text_color=MUTED, command=on_clear
            ).pack(side="right")

        self._update_buttons()

    # ------------------------------------------------------------------
    def set_transfers(self, transfers: list[dict]) -> None:
        """Met à jour les lignes sans les détruire quand la liste est stable."""

        transfers = list(transfers)
        ids = {transfer["id"] for transfer in transfers}

        if ids != set(self._rows):
            # Nouvelle liste : reconstruire les lignes (cas peu fréquent).
            for row in self._rows.values():
                row.destroy()
            self._rows = {}
            self._vars = {}
            for transfer in transfers:
                variable = ctk.BooleanVar(value=False)
                row = _TransferRow(
                    self.rows, transfer, variable, self._update_buttons
                )
                row.pack(fill="x", pady=2)
                self._rows[transfer["id"]] = row
                self._vars[transfer["id"]] = variable
        else:
            # Même liste : ne modifier que ce qui a réellement changé.
            for transfer in transfers:
                row = self._rows.get(transfer["id"])
                if row is not None:
                    row.update(transfer)

        if transfers and self._empty_visible:
            self.empty_label.pack_forget()
            self._empty_visible = False
        elif not transfers and not self._empty_visible:
            self.empty_label.pack(pady=18)
            self._empty_visible = True

        active = [
            item for item in transfers
            if item.get("status") not in FINAL_STATUSES
        ]
        count_text = f"{len(transfers)} fichier(s) · {len(active)} en cours"
        if count_text != self._last_count_text:
            self.count_label.configure(text=count_text)
            self._last_count_text = count_text

        self._transfers = transfers
        self._update_buttons()

    def selected_ids(self) -> list[int]:
        return [
            transfer_id for transfer_id, variable in self._vars.items()
            if variable.get()
        ]

    def clear_selection(self) -> None:
        for variable in self._vars.values():
            variable.set(False)
        self._update_buttons()

    # ------------------------------------------------------------------
    def _active_ids(self) -> list[int]:
        return [
            item["id"] for item in self._transfers
            if item.get("status") not in FINAL_STATUSES
        ]

    def _update_buttons(self) -> None:
        selected = any(
            variable.get() and item.get("status") not in FINAL_STATUSES
            for item in self._transfers
            for variable in [self._vars.get(item["id"])]
            if variable is not None
        )
        selected_state = "normal" if selected else "disabled"
        if selected_state != self._cancel_selected_state:
            self.cancel_selected.configure(state=selected_state)
            self._cancel_selected_state = selected_state

        all_state = "normal" if self._active_ids() else "disabled"
        if all_state != self._cancel_all_state:
            self.cancel_all.configure(state=all_state)
            self._cancel_all_state = all_state

    def _cancel_selected(self) -> None:
        ids = [
            item_id for item_id in self.selected_ids()
            if any(t["id"] == item_id and t.get("status") not in FINAL_STATUSES
                   for t in self._transfers)
        ]
        if ids and self.on_cancel:
            self.on_cancel(ids)

    def _cancel_all(self) -> None:
        ids = self._active_ids()
        if ids and self.on_cancel:
            self.on_cancel(ids)


class _TransferRow(ctk.CTkFrame):

    DIRECTION = {
        "envoi": ("upload", "#0B62F2", "Envoyé à"),
        "réception": ("download", "#0A720B", "Reçu de"),
    }

    def __init__(self, parent, transfer: dict, variable: ctk.BooleanVar,
                 on_change=None):
        super().__init__(
            parent, fg_color="#F0F3FA", corner_radius=8,
            border_width=1, border_color="#DCE5F2", height=52
        )
        self.pack_propagate(False)
        self._status: str | None = None
        self._progress: int | None = None

        self.checkbox = ctk.CTkCheckBox(
            self, text="", variable=variable,
            command=on_change,
            width=22, checkbox_width=17, checkbox_height=17
        )
        self.checkbox.place(x=8, y=16)

        icon_name, icon_color, verb = self.DIRECTION.get(
            transfer.get("direction", ""), ("file", "#52647A", "")
        )
        ctk.CTkLabel(
            self, text="", image=get_icon(icon_name, icon_color, 20),
            fg_color="transparent"
        ).place(x=36, y=15)

        ctk.CTkLabel(
            self, text=str(transfer.get("filename", "Indisponible")),
            font=("Segoe UI", 12, "bold"), text_color=NAVY, anchor="w"
        ).place(x=64, y=4, relwidth=0.55)

        ctk.CTkLabel(
            self, text=f"{verb} {transfer.get('peer', 'Indisponible')}",
            font=("Segoe UI", 10), text_color=MUTED, anchor="w"
        ).place(x=64, y=21, relwidth=0.55)

        self.status_label = ctk.CTkLabel(
            self, text="", font=("Segoe UI", 10, "bold"),
            corner_radius=8, width=74
        )
        self.status_label.place(relx=1, x=-8, y=6, anchor="ne")

        self.bar = ctk.CTkProgressBar(
            self, height=5, width=90, corner_radius=3,
            fg_color="#DDE5F2"
        )
        self.bar.place(relx=1, x=-10, y=30, anchor="ne")

        self.update(transfer)

    def update(self, transfer: dict) -> None:
        """Applique uniquement les champs qui ont changé."""

        status = str(transfer.get("status", "Indisponible"))
        if status != self._status:
            color, background = STATUS_COLORS.get(status, (MUTED, "#E4E8F0"))
            self.status_label.configure(
                text=status, text_color=color, fg_color=background
            )
            self.bar.configure(progress_color=color)
            self.checkbox.configure(
                state="disabled" if status in FINAL_STATUSES else "normal"
            )
            self._status = status

        progress = int(transfer.get("progress", 0) or 0)
        if progress != self._progress:
            self.bar.set(progress / 100)
            self._progress = progress
