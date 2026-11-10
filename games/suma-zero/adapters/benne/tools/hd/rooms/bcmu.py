"""
La seu del BCMU (Acte 2 i 3): paleta i peces comunes a totes les sales del banc, perquè semblin el mateix edifici.

To: un edifici de 1958 que el banc ha anat «modernitzant» per sobre. A dalt (vestíbul, despatxos): marbre crema
amb vetes, llautó i fusta fosca, llum càlida i cara; tot net, tot fred. A baix i darrere (moll, passadís de servei,
escombraries, seguretat): el mateix edifici sense maquillatge, formigó, linòleum, fluorescents i la pols de 1958.
El color de la casa és un blau marí institucional amb or; l'accent de Suma Zero (cian de pantalla, magenta) només
a les pantalles i als llums.

Peces que es repeteixen:
  - `tub_station(cv, x0, y0, x1, y1, vell=False)`: l'estació del tub pneumàtic (llautó, tub de vidre, comporta),
    la mateixa a totes les sales; `vell=True` per a la de 1958 de la sala d'escombraries (pols, sense polir).
  - `logo(cv, cx, y, k)`: el logotip del BCMU (un cercle partit, com un pastís on una porció ho és tot).
  - `marble(cv, x0, y0, x1, y1, lvl)`: marbre crema amb vetes.
"""
import math

from hd.pix import hr
from hd.rooms.comu import obox, outline, text, text_width

# ─── Paleta ────────────────────────────────────────────────────────────────
MARBLE = [(40, 34, 30), (74, 64, 56), (112, 100, 88), (150, 138, 122), (186, 174, 154), (214, 204, 184), (234, 226, 208), (248, 244, 230)]
VEIN = [(60, 50, 48), (96, 84, 78), (130, 118, 108)]
BRASS = [(36, 24, 10), (70, 48, 18), (112, 80, 28), (160, 118, 40), (204, 160, 62), (236, 202, 104), (252, 236, 170)]
MAHOG = [(16, 8, 8), (32, 14, 12), (52, 24, 18), (76, 36, 24), (102, 50, 32), (132, 68, 42), (164, 92, 58)]
NAVYB = [(6, 8, 18), (12, 16, 34), (20, 26, 52), (30, 40, 74), (44, 58, 100), (64, 82, 130), (96, 116, 162)]
CARPET = [(20, 6, 10), (40, 10, 16), (66, 16, 24), (96, 24, 32), (128, 36, 40), (160, 54, 50)]
CONCB = [(14, 14, 16), (26, 26, 30), (40, 40, 44), (56, 56, 60), (74, 74, 78), (96, 96, 98), (120, 120, 120), (148, 146, 142)]
LINOB = [(16, 18, 20), (28, 32, 34), (42, 48, 50), (58, 66, 66), (76, 86, 84), (98, 108, 104)]
DUST = [(30, 26, 22), (52, 46, 38), (78, 70, 58), (106, 96, 80), (136, 126, 106)]
GLASSB = [(20, 34, 40), (34, 56, 64), (54, 84, 92), (84, 120, 126), (130, 170, 172), (200, 230, 228)]
SCREENB = [(4, 14, 20), (8, 30, 40), (14, 54, 68), (24, 90, 104), (50, 140, 150), (110, 210, 210), (200, 255, 250)]


def marble(cv, x0, y0, x1, y1, lvl, seed=1, lit=1.0):
    """Marbre crema amb vetes diagonals suaus (deterministes)."""
    for y in range(int(y0), int(y1) + 1):
        for x in range(int(x0), int(x1) + 1):
            n = (hr(x // 3, y // 3, seed) - 0.5) * 0.35
            v = math.sin((x * 0.06 + y * 0.11) + math.sin(y * 0.05 + seed) * 2.2 + seed)
            vein = 1.1 if abs(v) < 0.035 else (0.45 if abs(v) < 0.09 else 0)
            cv.put(x, y, MARBLE, lvl + n - vein, lit)


def logo(cv, cx, y, k=1, lvl=4.0, lit=1.0):
    """El logotip del BCMU: un cercle d'or on una porció (gairebé tot) està separada de la resta."""
    r = 5 * k
    for yy in range(int(y - r), int(y + r) + 1):
        for xx in range(int(cx - r), int(cx + r) + 1):
            dx, dy = xx - cx, yy - y
            d = math.hypot(dx, dy)
            if d <= r:
                a = math.degrees(math.atan2(dy, dx)) % 360
                gap = 300 <= a <= 312 or 348 <= a <= 360
                if not gap:
                    small = 312 < a < 348
                    cv.put(xx, yy, BRASS, lvl + (0.8 if small else 0) - d / r * 0.8, lit)


def tub_station(cv, x0, y0, x1, y1, vell=False, capsule=None):
    """L'estació del tub pneumàtic: placa de llautó, el tub de vidre que puja pel sostre i la comporta amb la palanca.

    Mida pensada per a uns 20×44 px (les zones de room_designs.py). Amb `vell`, pols i llautó apagat (la de 1958).
    `capsule`: y de dalt d'una càpsula que puja pel tub (per a les animacions)."""
    lv = 2.4 if vell else 3.4
    cx = (x0 + x1) // 2
    # el tub de vidre, des del sostre fins a la comporta
    for y in range(0, y0 + 6):
        for x in range(cx - 3, cx + 4):
            edge = x in (cx - 3, cx + 3)
            cv.put(x, y, GLASSB, (2.0 if edge else 3.4) - (1.0 if vell else 0) + (0.8 if x == cx - 1 else 0))
    if capsule is not None:                                              # la càpsula, vista a través del vidre
        cy0, cy1 = max(0, capsule), min(y0 + 5, capsule + 8)
        for y in range(cy0, cy1 + 1):
            for x in range(cx - 2, cx + 3):
                cap = y - capsule in (0, 8)                              # les tapes de llautó
                cv.put(x, y, BRASS if cap else MAHOG, (4.4 if cap else 3.6) + (1.0 if x == cx - 1 else 0) - (0.8 if x == cx + 2 else 0))
        cv.tint(cx - 2, cy0, cx + 2, cy1, (200, 230, 228), 0.18)           # el vidre per davant
    for yy in range(4, y0, 22):                                          # les abraçadores
        cv.rect(cx - 4, yy, cx + 4, yy + 1, BRASS, lv)
    # la placa i la comporta
    obox(cv, x0, y0 + 4, x1, y1, BRASS, lv)
    obox(cv, x0 + 3, y0 + 10, x1 - 3, y1 - 12, BRASS, lv - 1.2)
    cv.disc(cx, y0 + 18, (x1 - x0) / 2 - 5, 5, GLASSB, lambda nx, ny: 2.6 - ny + (-0.8 if vell else 0))
    cv.rect(x0 + 4, y1 - 9, x1 - 4, y1 - 7, MAHOG, 2.0)                  # la ranura
    cv.line(x1 - 2, y1 - 16, x1 + 3, y1 - 22, BRASS, lv + 1.0)           # la palanca
    cv.disc(x1 + 3, y1 - 23, 1.6, 1.6, [(150, 30, 30), (210, 60, 50)], 1)
    if vell:
        for i in range(30):                                              # pols
            px = x0 + int(hr(i, 3) * (x1 - x0))
            py = y0 + 4 + int(hr(i, 4) * (y1 - y0 - 4))
            cv.put(px, py, DUST, 3.0)
        text(cv, '1958', cx - text_width('1958') // 2, y1 - 5, BRASS, 1.4)
    else:
        logo(cv, cx, y1 - 4, k=0.5, lvl=lv + 0.6)


def sign(cv, x0, y0, s, ramp, lvl, ink=(250, 244, 230)):
    """Un rètol rectangular amb text centrat (font petita del joc)."""
    w = text_width(s)
    obox(cv, x0, y0, x0 + w + 7, y0 + 10, ramp, lvl)
    text(cv, s, x0 + 4, y0 + 3, [ink], 0, flat=ink)
    return x0 + w + 7
