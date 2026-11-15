"""
La seu del BCMU a 640×360: les peces comunes de hd/rooms/bcmu.py (paleta, marbre, logotip, estació del tub
pneumàtic, rètols), redibuixades a ×4/3 per a les sales del banc de hd640/rooms.

  - la paleta és la mateixa (s'importa de hd/rooms/bcmu.py);
  - `marble`: el gra i les vetes a l'escala nova (no s'amplien: són d'un píxel, i més fines);
  - `logo(cv, cx, y, k)`: el mateix logotip; `k` ja és la mida real (r = 5·k), passa-hi k ×4/3 respecte de 480;
  - `tub_station(cv, x0, y0, x1, y1, vell=False, capsule=None)`: pensada per a uns 27×59 px (els 20×44 de 480 ×4/3),
    amb el tub de vidre de 9 px, abraçadores, la comporta amb reblons i la palanca;
  - `sign`: un rètol amb la font petita de les sales.
"""
import math

import hd640  # noqa: F401  (posa la llibreria de dibuix a 640×360)
from hd.pix import hr
from hd.rooms.comu import obox, outline, text, text_width  # noqa: F401
from hd.rooms.bcmu import (MARBLE, VEIN, BRASS, MAHOG, NAVYB, CARPET, CONCB, LINOB, DUST, GLASSB,  # noqa: F401
                           SCREENB)

K = 4 / 3


def marble(cv, x0, y0, x1, y1, lvl, seed=1, lit=1.0):
    """Marbre crema amb vetes diagonals suaus (deterministes), a l'escala de 640."""
    for y in range(int(y0), int(y1) + 1):
        for x in range(int(x0), int(x1) + 1):
            n = (hr(x // 4, y // 4, seed) - 0.5) * 0.35 + (hr(x, y, seed + 7) - 0.5) * 0.12
            v = math.sin((x * 0.045 + y * 0.0825) + math.sin(y * 0.0375 + seed) * 2.2 + seed)
            # una veta secundària, més fina, que creua la principal
            v2 = math.sin((x * 0.021 - y * 0.06) + math.sin(x * 0.02 + seed * 2) * 1.6 + seed * 3)
            vein = 1.1 if abs(v) < 0.026 else (0.45 if abs(v) < 0.07 else 0)
            vein += 0.35 if abs(v2) < 0.018 else 0
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
                    rim = d > r - 1.0 and r >= 4                        # una vora fosca d'un píxel als grans
                    cv.put(xx, yy, BRASS, lvl + (0.8 if small else 0) - d / r * 0.8 - (0.9 if rim else 0), lit)


def tub_station(cv, x0, y0, x1, y1, vell=False, capsule=None):
    """L'estació del tub pneumàtic: placa de llautó, el tub de vidre que puja pel sostre i la comporta amb la palanca.

    Mida pensada per a uns 27×59 px. Amb `vell`, pols i llautó apagat (la de 1958).
    `capsule`: y de dalt d'una càpsula que puja pel tub (per a les animacions)."""
    lv = 2.4 if vell else 3.4
    cx = (x0 + x1) // 2
    # el tub de vidre, des del sostre fins a la comporta (9 px, amb dues llums)
    for y in range(0, y0 + 8):
        for x in range(cx - 4, cx + 5):
            edge = x in (cx - 4, cx + 4)
            hi = 0.9 if x == cx - 2 else (0.4 if x == cx - 1 else 0) + (0.3 if x == cx + 2 else 0)
            cv.put(x, y, GLASSB, (2.0 if edge else 3.4) - (1.0 if vell else 0) + hi)
    if capsule is not None:                                              # la càpsula, vista a través del vidre
        cy0, cy1 = max(0, capsule), min(y0 + 7, capsule + 11)
        for y in range(cy0, cy1 + 1):
            for x in range(cx - 3, cx + 4):
                cap = y - capsule in (0, 1, 10, 11)                      # les tapes de llautó
                cv.put(x, y, BRASS if cap else MAHOG,
                       (4.4 if cap else 3.6) + (1.0 if x == cx - 2 else 0) - (0.8 if x == cx + 3 else 0))
        cv.tint(cx - 3, cy0, cx + 3, cy1, (200, 230, 228), 0.18)           # el vidre per davant
    for yy in range(5, y0, 29):                                          # les abraçadores, amb un cargol
        cv.rect(cx - 5, yy, cx + 5, yy + 2, BRASS, lv)
        cv.hline(cx - 5, cx + 5, yy, BRASS, lv + 1.0)
        cv.put(cx + 5, yy + 1, BRASS, lv - 1.4)
    # la placa i la comporta
    obox(cv, x0, y0 + 5, x1, y1, BRASS, lv)
    for rx, ry in ((x0 + 2, y0 + 7), (x1 - 2, y0 + 7), (x0 + 2, y1 - 2), (x1 - 2, y1 - 2)):   # reblons
        cv.put(rx, ry, BRASS, lv + 1.4)
    obox(cv, x0 + 4, y0 + 13, x1 - 4, y1 - 16, BRASS, lv - 1.2)
    cv.disc(cx, y0 + 24, (x1 - x0) / 2 - 7, 7, GLASSB, lambda nx, ny: 2.6 - ny + (-0.8 if vell else 0))
    cv.put(cx - 4, y0 + 21, GLASSB, 5.0 - (1.2 if vell else 0))         # el reflex de la finestreta
    cv.rect(x0 + 5, y1 - 12, x1 - 5, y1 - 9, MAHOG, 2.0)                 # la ranura
    cv.hline(x0 + 5, x1 - 5, y1 - 12, MAHOG, 0.8)
    cv.line(x1 - 3, y1 - 21, x1 + 4, y1 - 29, BRASS, lv + 1.0)           # la palanca
    cv.line(x1 - 2, y1 - 21, x1 + 5, y1 - 29, BRASS, lv - 0.2)
    cv.disc(x1 + 4, y1 - 31, 2.2, 2.2, [(110, 20, 22), (150, 30, 30), (210, 60, 50), (240, 120, 100)],
            lambda nx, ny: 2.2 - nx - ny)
    if vell:
        for i in range(55):                                              # pols
            px = x0 + int(hr(i, 3) * (x1 - x0))
            py = y0 + 5 + int(hr(i, 4) * (y1 - y0 - 5))
            cv.put(px, py, DUST, 3.0)
        text(cv, '1958', cx - text_width('1958') // 2, y1 - 7, BRASS, 1.4)
    else:
        logo(cv, cx, y1 - 5, k=0.7, lvl=lv + 0.6)


def sign(cv, x0, y0, s, ramp, lvl, ink=(250, 244, 230)):
    """Un rètol rectangular amb text centrat (font petita del joc), amb més marge que a 480."""
    w = text_width(s)
    obox(cv, x0, y0, x0 + w + 9, y0 + 12, ramp, lvl)
    text(cv, s, x0 + 5, y0 + 4, [ink], 0, flat=ink)
    return x0 + w + 9
