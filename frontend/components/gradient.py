"""Cadre à dégradé horizontal (customtkinter ne le gère pas nativement)."""

import customtkinter as ctk
from PIL import Image


def _mix(start, end, ratio):
    a = tuple(bytes.fromhex(start.strip("#")))
    b = tuple(bytes.fromhex(end.strip("#")))
    return tuple(int(a[i] + (b[i] - a[i]) * ratio) for i in range(3))


class GradientFrame(ctk.CTkFrame):
    """Un ``CTkFrame`` dont le fond est un dégradé de gauche à droite."""

    def __init__(self, parent, start="#EBF1FE", end="#6CADFD",
                 corner_radius=2, **kwargs):
        super().__init__(parent, fg_color=start,
                         corner_radius=corner_radius, **kwargs)

        self._start = start
        self._end = end
        self._last_size = (0, 0)
        self._image = None

        self._background = ctk.CTkLabel(self, text="", fg_color="transparent")
        self._background.place(x=0, y=0, relwidth=1, relheight=1)

        self.bind("<Configure>", self._on_configure)

    def _on_configure(self, event):
        width = max(1, self.winfo_width())
        height = max(1, self.winfo_height())
        if (width, height) == self._last_size:
            return

        self._last_size = (width, height)
        strip = Image.new("RGB", (width, 1))
        pixels = strip.load()
        for x in range(width):
            pixels[x, 0] = _mix(self._start, self._end, x / max(1, width - 1))

        strip = strip.resize((width, height), Image.Resampling.NEAREST)
        self._image = ctk.CTkImage(light_image=strip, dark_image=strip,
                                   size=(width, height))
        self._background.configure(image=self._image)
