"""Petites icônes vectorielles générées à la volée pour l'interface.

Aucun fichier image externe n'est nécessaire : les icônes sont dessinées avec
PIL puis converties en ``CTkImage``. Elles restent nettes à toute taille.
"""

import math

from PIL import Image, ImageColor, ImageDraw
from customtkinter import CTkImage

_CACHE = {}
_SCALE = 4
_GRID = 64


def _rgba(value, alpha=255):
    if isinstance(value, str):
        rgb = ImageColor.getrgb(value)
    else:
        rgb = tuple(value[:3])
    return rgb + (alpha,)


def _lighter(value, ratio=0.65):
    rgb = ImageColor.getrgb(value) if isinstance(value, str) else tuple(value[:3])
    rgb = tuple(int(c + (255 - c) * ratio) for c in rgb)
    return _rgba(rgb)


def _draw_icon(name, draw, s, color):
    """Dessine l'icône ``name`` sur une grille logique de 64 x 64."""

    def p(*coords):
        return [(x * s / _GRID, y * s / _GRID) for x, y in coords]

    def box(x0, y0, x1, y1):
        return (x0 * s / _GRID, y0 * s / _GRID,
                x1 * s / _GRID, y1 * s / _GRID)

    def line(points, width=4, fill=None):
        draw.line(p(*points), fill=fill or _rgba(color),
                  width=max(1, int(width * s / _GRID)), joint="curve")

    c = _rgba(color)
    soft = _lighter(color, 0.55)

    if name == "plane":
        draw.polygon(p((3, 31), (61, 5), (43, 59), (30, 41),
                       (17, 36), (30, 29)), fill=c)
        line(((30, 29), (61, 5)), width=2, fill=soft)

    elif name == "home":
        draw.polygon(p((3, 31), (32, 6), (61, 31)), fill=c)
        draw.rectangle(box(11, 28, 53, 59), fill=c)
        draw.rectangle(box(27, 41, 37, 59), fill=soft)

    elif name == "monitor":
        draw.rectangle(box(5, 9, 59, 45), outline=c,
                       width=max(1, int(5 * s / _GRID)))
        line(((32, 45), (32, 54)), width=5)
        line(((20, 55), (44, 55)), width=5)

    elif name == "download":
        line(((32, 7), (32, 41)), width=6)
        draw.polygon(p((18, 31), (46, 31), (32, 48)), fill=c)
        line(((9, 50), (9, 57), (55, 57), (55, 50)), width=5)

    elif name == "upload":
        line(((32, 49), (32, 15)), width=6)
        draw.polygon(p((18, 25), (46, 25), (32, 8)), fill=c)
        line(((9, 52), (9, 59), (55, 59), (55, 52)), width=5)

    elif name == "clock":
        draw.ellipse(box(7, 7, 57, 57), outline=c,
                     width=max(1, int(5 * s / _GRID)))
        line(((32, 32), (32, 17)), width=5)
        line(((32, 32), (45, 39)), width=5)

    elif name == "gear":
        draw.ellipse(box(19, 19, 45, 45), outline=c,
                     width=max(1, int(5 * s / _GRID)))
        for angle in range(0, 360, 45):
            rad = math.radians(angle)
            x1 = 32 + 17 * math.cos(rad)
            y1 = 32 + 17 * math.sin(rad)
            x2 = 32 + 28 * math.cos(rad)
            y2 = 32 + 28 * math.sin(rad)
            line(((x1, y1), (x2, y2)), width=8)
        draw.ellipse(box(27, 27, 37, 37), fill=soft)

    elif name == "info":
        draw.ellipse(box(7, 7, 57, 57), outline=c,
                     width=max(1, int(5 * s / _GRID)))
        draw.ellipse(box(29, 17, 35, 23), fill=c)
        line(((32, 28), (32, 47)), width=5)

    elif name == "wifi":
        draw.arc(box(4, 22, 60, 66), 205, 335, fill=c,
                 width=max(1, int(5 * s / _GRID)))
        draw.arc(box(15, 34, 49, 62), 205, 335, fill=c,
                 width=max(1, int(5 * s / _GRID)))
        draw.ellipse(box(27, 49, 37, 59), fill=c)

    elif name == "globe":
        draw.ellipse(box(7, 7, 57, 57), outline=c,
                     width=max(1, int(4 * s / _GRID)))
        draw.ellipse(box(23, 7, 41, 57), outline=c,
                     width=max(1, int(3 * s / _GRID)))
        line(((8, 32), (56, 32)), width=3)

    elif name == "bolt":
        draw.polygon(p((35, 3), (13, 36), (29, 36),
                       (23, 61), (51, 26), (34, 26)), fill=c)

    elif name in ("file", "image"):
        draw.polygon(p((13, 5), (41, 5), (52, 16), (52, 59), (13, 59)),
                     fill=c)
        draw.polygon(p((41, 5), (41, 16), (52, 16)),
                     fill=_rgba((255, 255, 255), 210))
        if name == "image":
            draw.ellipse(box(20, 27, 27, 34), fill=_lighter(color, 0.8))
            draw.polygon(p((18, 52), (29, 38), (37, 47), (44, 39), (49, 52)),
                         fill=_lighter(color, 0.75))

    elif name == "check":
        draw.ellipse(box(7, 7, 57, 57), fill=c)
        line(((17, 33), (28, 44), (47, 22)), width=6, fill=_rgba((255, 255, 255)))

    elif name == "close":
        line(((16, 16), (48, 48)), width=6)
        line(((48, 16), (16, 48)), width=6)

    elif name == "chevron":
        line(((22, 18), (42, 32), (22, 46)), width=6)

    elif name == "stop":
        draw.rectangle(box(14, 14, 50, 50), fill=c)

    elif name == "files":
        draw.rectangle(box(20, 6, 57, 45), outline=c,
                       width=max(1, int(4 * s / _GRID)))
        draw.rectangle(box(8, 17, 45, 56), fill=_rgba((255, 255, 255), 235),
                       outline=c, width=max(1, int(4 * s / _GRID)))
        line(((15, 28), (35, 28)), width=3)
        line(((15, 38), (30, 38)), width=3)

    else:
        raise ValueError(f"Icône inconnue : {name}")


def get_icon(name, color="#0B62F2", size=32, opacity=1.0):
    """Retourne un ``CTkImage`` pour l'icône demandée (mise en cache)."""

    key = (name, color, int(size), round(opacity, 3))
    if key in _CACHE:
        return _CACHE[key]

    side = int(size * _SCALE)
    image = Image.new("RGBA", (side, side), (0, 0, 0, 0))
    draw = ImageDraw.Draw(image)
    _draw_icon(name, draw, side, color)

    if opacity < 1.0:
        alpha = image.getchannel("A").point(lambda a: int(a * opacity))
        image.putalpha(alpha)

    image = image.resize((int(size), int(size)), Image.Resampling.LANCZOS)
    ctk_image = CTkImage(light_image=image, dark_image=image,
                         size=(int(size), int(size)))
    _CACHE[key] = ctk_image
    return ctk_image
