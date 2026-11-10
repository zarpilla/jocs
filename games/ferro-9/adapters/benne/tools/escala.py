"""
Escala de l'art de Ferro-9: els dissenys (personatges, objectes, sales) es dibuixen en coordenades
de 352×198 i es rasteritzen a la resolució del joc. Si es canvia la resolució, només cal tocar això
(i les constants de benne-content.ts).
"""
DESIGN_W, DESIGN_H = 352, 198
GAME_W, GAME_H = 480, 270
SCALE = GAME_W / DESIGN_W  # 15/11


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
