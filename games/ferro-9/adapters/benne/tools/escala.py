"""
Escala de l'art de Ferro-9: la geometria (room_designs.py, els punts dels personatges) és en coordenades de
352×198 i es passa a la resolució del joc. L'art es dibuixa directament a la resolució del joc: a 640×360 és el de
hd640/ (sales, personatges, inventari, GUI, font); fins a l'11/2026 era a 480×270 (hd/).

RESOLUCIO tria quin art fan servir les eines (draw_placeholders, draw_characters, draw_items, hd/render):
640 → hd640/, 480 → hd/. La resolució del projecte Benne és la de game-config.json (hd640/aplica.py la posa).
"""
RESOLUCIO = 640
DESIGN_W, DESIGN_H = 352, 198
GAME_W, GAME_H = (640, 360) if RESOLUCIO == 640 else (480, 270)
SCALE = GAME_W / DESIGN_W  # 20/11 a 640, 15/11 a 480


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
