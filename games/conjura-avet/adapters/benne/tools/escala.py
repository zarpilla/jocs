"""
Escala de l'art. Ni un ou es dissenya directament a la resolució del joc, 640×360 (escala 1): l'art és a
hd640/ (sales, personatges, inventari, GUI, font). Fins a l'11/2026 era a 480×270 (hd/), i a Ferro-9 es dissenyava
a 352×198.

RESOLUCIO tria quin art fan servir les eines (draw_placeholders, draw_characters, draw_items, room_designs):
640 → hd640/, 480 → hd/. La resolució del projecte Benne és la de game-config.json (hd640/aplica.py la posa).
"""
RESOLUCIO = 640
DESIGN_W, DESIGN_H = (640, 360) if RESOLUCIO == 640 else (480, 270)
GAME_W, GAME_H = DESIGN_W, DESIGN_H
SCALE = GAME_W / DESIGN_W  # 1


def box(x0, y0, x1, y1, k=SCALE):
    """Rectangle de píxels inclusiu en coordenades de disseny → rectangle inclusiu real."""
    import math
    return (math.floor(x0 * k), math.floor(y0 * k), math.floor((x1 + 1) * k) - 1, math.floor((y1 + 1) * k) - 1)


def pt(x, y, k=SCALE):
    """Punt (centre de píxel) en coordenades de disseny → real."""
    return (round((x + 0.5) * k - 0.5), round((y + 0.5) * k - 0.5))


def n(v, k=SCALE):
    """Una longitud."""
    return round(v * k)
