"""
Aigua Verne — la portada (pantalla sencera de 640×360, sense barra de verbs; mida de lluny).

Terra-2 de lluny, al capvespre de pols: el sol baix i vermellós a l'esquerra, enterbolit; el cel que passa de
l'ocre al morat i les primeres estrelles. Els camps secs fins a l'horitzó, amb les ombres llargues. La Canonada
s'alça a la dreta fins a dalt de tot, on penja un dels dipòsits orbitals (el cilindre blanc amb la gota blava).
A baix a l'esquerra, petita, la Cantimplora aparcada al port, amb la rampa oberta i els llums encesos.

El títol, «AIGUA VERNE», és l'etiqueta d'una ampolla d'aigua de Verne: blanca i blava, una mica rovellada, i
les lletres són de vidre, mig plenes d'aigua (cadascuna fins a un nivell diferent).

A baix a la dreta, el pou d'una granja amb la bomba de Verne (blanca, amb la gota blava), quieta, i la canonada
de terra que va del pou a la base de la Canonada. Del peu de la rampa de la nau surt un corriol cap a la posta.

La meitat de baix (els botons de la GUI van a 220..420 × 224..328) només té cel baix i camp.
ANIMS: `pols` (la pols que passa arran de terra), `llums` (els llums vermells de la Canonada i de la nau que fan
pampallugues) i `titol` (el títol, en una capa a part amb l'aigua de dins les lletres que es gronxa: «Comença»
l'esvaeix i el pròleg, `proleg_terra2`, continua al mateix pla).
"""
import hd640  # noqa: F401  (abans de cap hd.rooms: posa la llibreria a 640×360)

import functools
import math

from hd.pix import Canvas, Light, W, H, hr, mix, RUST
from hd.rooms.comu import text, text_width
from hd.rooms.exterior import fbm, smooth
from hd640.rooms.nau_comu import (OLIVE, SAFETY, STEELN, WBLUE, WHITEV, COL, BLACKT, INK, PAPERN, drop,
                                  diposit_orbital, canonada)

# Art a 2× (1280×720 per a una sala de 640×360): el mateix dibuix, amb les formes, el dither i la llum a la
# resolució real (hd1280/canvas2x.py); el motor el mostra a 1/2 (artScale al .room.json).
ART_SCALE = 2
from hd1280.canvas2x import Canvas2x as Canvas  # noqa: E402,F811
from hd.pix import Canvas as Canvas1x  # noqa: E402,F401  (llenços auxiliars en píxels de sala: figures, textos)

HOR = 252
SUN = (96, 236)
CAN_X = 548                              # la Canonada
TANK = (548, 22)                         # el dipòsit orbital
SHIP = (34, 334)                         # la Cantimplora: popa i terra
PUMP = (488, 318)                        # la bomba de Verne: el pal del balancí i terra
PIPE = ((506, 315), (CAN_X - 10, HOR - 2))   # la canonada de terra, del pou a la base de la Canonada
LABEL = (122, 26, 518, 192)              # l'etiqueta del títol
S = 8                                    # el «píxel» de les lletres grosses

_ANIM = {'pols': None, 'llums': None}

LIGHT = Light(ambient=0.0, vignette=None, floor_fade=None)

# ─── Rampes ─────────────────────────────────────────────────────────────────
DUSK = [(14, 10, 26), (24, 16, 38), (38, 22, 48), (56, 30, 54), (80, 40, 58), (108, 54, 58), (140, 72, 58),
        (172, 96, 62), (204, 126, 70), (228, 156, 84), (244, 186, 108), (252, 214, 146), (255, 238, 196)]
PLAIN = [(18, 12, 14), (30, 20, 20), (46, 30, 26), (64, 42, 32), (86, 56, 38), (110, 72, 46), (136, 92, 56),
         (164, 114, 68), (192, 138, 84)]
HILLS = [(34, 22, 34), (50, 30, 40), (68, 40, 46), (88, 52, 50), (110, 66, 56)]
CREAM = [(96, 86, 72), (142, 132, 112), (184, 176, 156), (214, 208, 190), (232, 228, 214), (244, 242, 232),
         (252, 251, 246)]
NAVY = [(6, 12, 34), (10, 22, 60), (16, 36, 92)]
GLASS = [(150, 176, 206), (184, 206, 228), (212, 228, 242), (232, 242, 250)]
WATER = [(10, 40, 110), (18, 64, 156), (30, 92, 196), (52, 128, 226), (96, 170, 244), (170, 214, 255)]

LETTERS = {
    'A': ['01110', '10001', '10001', '11111', '10001', '10001', '10001'],
    'I': ['11111', '00100', '00100', '00100', '00100', '00100', '11111'],
    'G': ['01111', '10000', '10000', '10011', '10001', '10001', '01111'],
    'U': ['10001', '10001', '10001', '10001', '10001', '10001', '01110'],
    'V': ['10001', '10001', '10001', '10001', '01010', '01010', '00100'],
    'E': ['11111', '10000', '10000', '11110', '10000', '10000', '11111'],
    'R': ['11110', '10001', '10001', '11110', '10100', '10010', '10001'],
    'N': ['10001', '11001', '10101', '10011', '10001', '10001', '10001'],
}


# ─── Cel ────────────────────────────────────────────────────────────────────

def sky(cv):
    for y in range(0, HOR + 1):
        t = y / HOR
        for x in range(W):
            d = math.hypot(x - SUN[0], (y - SUN[1]) * 1.8)
            lvl = 0.8 + 6.4 * t ** 1.7 + 4.0 * max(0.0, 1 - d / 260) ** 2.2
            # bandes de pols allargades
            band = fbm(x / 160, y / 9, 61)
            lvl += (band - 0.5) * 1.4 * t
            lvl -= 0.6 * smooth(0.55, 0.75, fbm(x / 90, y / 14, 62)) * t ** 2
            cv.put(x, y, DUSK, lvl, lit=0)
            if t < 0.45 and hr(x, y, 63) > 0.9975:                         # les primeres estrelles
                cv.flat(x, y, (170, 160, 190) if hr(x, y, 64) > 0.5 else (110, 96, 140))
    # el sol: un disc enterbolit, partit per les bandes de pols
    cv.glow(SUN[0], SUN[1], 70, (255, 200, 130), 0.5)
    for y in range(SUN[1] - 11, SUN[1] + 12):
        for x in range(SUN[0] - 11, SUN[0] + 12):
            if (x - SUN[0]) ** 2 + (y - SUN[1]) ** 2 <= 121 and not (y - SUN[1]) % 6 == 3:
                cv.put(x, y, DUSK, 12.0 - (y - SUN[1] + 11) * 0.05, lit=0)
    # turons llunyans, morats
    for x in range(W):
        h = HOR - 3 - 9 * fbm(x / 80, 0.5, 65) - 4 * fbm(x / 20, 1.5, 66)
        for y in range(int(h), HOR + 1):
            cv.put(x, y, HILLS, 2.6 - (y - h) * 0.08 + 1.4 * max(0.0, 1 - abs(x - SUN[0]) / 200), lit=0)


def tank_and_pipe(cv, light=None):
    # la Canonada, de l'horitzó fins al dipòsit, amb els llums vermells
    canonada(cv, CAN_X, TANK[1] + 6, HOR - 6, 1.0, 3.0, ring=9, haze=(200, 120, 90), haze_k=0.45)
    # la llum del sol, de costat, a l'esquerra de la columna
    cv.tint(CAN_X - 4, TANK[1], CAN_X - 1, HOR, (255, 170, 100), lambda x, y: 0.25)
    cv.tint(CAN_X + 1, TANK[1], CAN_X + 4, HOR, (60, 30, 70), lambda x, y: 0.3)
    cv.tint(CAN_X - 4, TANK[1], CAN_X + 4, HOR, (40, 24, 60), lambda x, y: 0.35 * (1 - (y - TANK[1]) / (HOR - TANK[1])))
    for y in range(TANK[1] + 30, HOR - 20, 50):
        on = light is not None and (light + y // 50) % 4 == 0
        cv.flat(CAN_X, y, (255, 70, 50) if on else (130, 30, 30))
        if on:
            cv.glow(CAN_X, y, 5, (255, 80, 60), 0.6)
    # l'estació de la base, a l'horitzó
    cv.rect(CAN_X - 10, HOR - 5, CAN_X + 10, HOR, COL, lambda x, y: 0.8 - (x - CAN_X) * 0.03, lit=0)
    cv.rect(CAN_X - 10, HOR - 6, CAN_X + 10, HOR - 6, COL, 2.0, lit=0)
    for x in range(CAN_X - 8, CAN_X + 9, 4):
        cv.flat(x, HOR - 5, (255, 210, 120))
    # el dipòsit orbital: un cilindre blanc amb la gota, il·luminat de baix per la posta
    diposit_orbital(cv, TANK[0], TANK[1], 64, 8)
    cv.tint(TANK[0] - 36, TANK[1] - 9, TANK[0] + 36, TANK[1] + 9, (255, 160, 90),
            lambda x, y: 0.35 * max(0.0, (y - TANK[1] + 4) / 18) + 0.1 * max(0.0, (TANK[0] - x) / 50))
    cv.tint(TANK[0] - 36, TANK[1] - 9, TANK[0] + 36, TANK[1] + 9, (40, 30, 70),
            lambda x, y: 0.4 * max(0.0, (TANK[1] - y - 4) / 10))
    # els panells solars i els braços
    for side in (-1, 1):
        x0 = TANK[0] + side * 40
        for j in range(2):
            cv.rect(min(x0, x0 + side * 20), TANK[1] - 2 + j * 3, max(x0, x0 + side * 20), TANK[1] - 1 + j * 3,
                    [(20, 30, 60), (40, 60, 110), (80, 110, 170)], 1.4 + j * 0.3, lit=0)
        cv.hline(min(TANK[0] + side * 34, x0), max(TANK[0] + side * 34, x0), TANK[1], STEELN, 4.0, lit=0)
    if light is not None and light % 2 == 0:
        cv.flat(TANK[0] - 33, TANK[1] - 1, (255, 80, 60))
        cv.flat(TANK[0] + 33, TANK[1] - 1, (120, 255, 120))


# ─── Camps i port ───────────────────────────────────────────────────────────

def plain(cv):
    vx = 320
    for y in range(HOR + 1, H):
        t = (y - HOR) / (H - HOR)
        for x in range(W):
            ang = math.atan2(y - (HOR - 30), x - vx)
            furrow = math.sin(ang * 70) * 0.5
            lvl = 4.6 - t * 3.0 + furrow * (0.3 + t) + (fbm(x / 40, y / 6, 67) - 0.5) * 1.2
            lvl += 2.2 * max(0.0, 1 - math.hypot(x - SUN[0], (y - HOR) * 4) / 260) * (1 - t)   # la claror de la posta
            cv.put(x, y, PLAIN, lvl, lit=0)
    # la boira de pols arran de l'horitzó
    cv.tint(0, HOR - 14, W - 1, HOR + 18, (220, 140, 90), lambda x, y: 0.28 * max(0.0, 1 - abs(y - HOR) / 18))
    # el camí del port, de terra més clara
    for y in range(HOR + 1, H):
        t = (y - HOR) / (H - HOR)
        cx = 300 - 220 * t ** 1.2
        hw = 1 + 20 * t
        for x in range(int(cx - hw), int(cx + hw) + 1):
            cv.put(x, y, PLAIN, 5.0 - t * 2.6 + (hr(x // 3, y // 2, 68) - 0.5) * 0.8, lit=0)
    # el corriol, del peu de la rampa de la nau cap a la posta (per on se'n van l'Iri i la Vet al pròleg)
    for i in range(600):
        x, y, sc = path_xy(i / 599)
        y = round(y)
        hw = 0.5 + 2.4 * sc
        for xx in range(int(x - hw), int(x + hw) + 1):
            edge = abs(xx - x) / max(0.5, hw)
            if hr(xx // 2, int(y), 82) > 0.3 + 0.5 * edge ** 2:
                cv.put(xx, y, PLAIN, 5.4 - (1 - sc) * 0.8 - edge * 1.0 + (hr(xx, int(y), 83) - 0.5) * 0.8, lit=0)
    # una tanca vella i rocs
    for x in range(380, 640, 22):
        y = HOR + 10 + (x - 380) // 30
        cv.vline(x, y - 4, y, BLACKT, 1.6, lit=0)
    for x in range(380, 640):
        y = HOR + 8 + (x - 380) // 30
        if hr(x // 22, 69) > 0.2:
            cv.flat(x, y, mix(cv.get(x, y), (30, 20, 22), 0.6))


PATH = [(54, 339), (36, 339), (22, 328), (19, 310), (28, 292), (50, 276), (82, 263), (110, 253)]


@functools.lru_cache(maxsize=None)
def _path_pts():
    """El corriol, suavitzat (Chaikin) i repartit per igual al llarg del camí."""
    pts = [tuple(map(float, p)) for p in PATH]
    for _ in range(4):
        out = [pts[0]]
        for (ax, ay), (bx, by) in zip(pts, pts[1:]):
            out += [(0.75 * ax + 0.25 * bx, 0.75 * ay + 0.25 * by), (0.25 * ax + 0.75 * bx, 0.25 * ay + 0.75 * by)]
        pts = out + [pts[-1]]
    acc = [0.0]
    for (ax, ay), (bx, by) in zip(pts, pts[1:]):
        acc.append(acc[-1] + math.hypot(bx - ax, by - ay))
    n, out, j = 600, [], 0
    for i in range(n + 1):
        d = acc[-1] * i / n
        while j < len(acc) - 2 and acc[j + 1] < d:
            j += 1
        k = (d - acc[j]) / max(1e-9, acc[j + 1] - acc[j])
        out.append((pts[j][0] + (pts[j + 1][0] - pts[j][0]) * k, pts[j][1] + (pts[j + 1][1] - pts[j][1]) * k))
    return tuple(out)


def path_xy(u):
    """El corriol: surt del peu de la rampa, volta la popa de la nau i se'n va cap a la posta (u=0 a la rampa, u=1
    a l'horitzó, sota el sol). → (x, y, escala de 0 a 1)"""
    pts = _path_pts()
    x, y = pts[round(max(0.0, min(1.0, u)) * (len(pts) - 1))]
    return x, y, max(0.0, (y - HOR + 2) / (339 - HOR + 2))


def ground_pipe(cv):
    """La canonada de terra, del pou a la base de la Canonada: blanca, amb abraçadores, més prima de lluny."""
    (ax, ay), (bx, by) = PIPE
    n = max(abs(bx - ax), abs(by - ay)) * 2
    for i in range(n + 1):
        u = i / n
        x, y = round(ax + (bx - ax) * u), round(ay + (by - ay) * u)
        thick = 2 if u < 0.55 else 1
        cv.put(x, y, COL, 3.6 - u * 0.8, lit=0)
        if thick == 2:
            cv.put(x, y + 1, COL, 2.0, lit=0)
        cv.darken(x, y + thick, x, y + thick, 0.35)
    for k in range(1, 6):                                                # les abraçadores
        u = k / 6
        x, y = round(ax + (bx - ax) * u), round(ay + (by - ay) * u)
        cv.put(x - 1, y, STEELN, 1.6, lit=0)
        cv.put(x + 1, y, STEELN, 1.6, lit=0)


def pipe_xy(u):
    (ax, ay), (bx, by) = PIPE
    return ax + (bx - ax) * u, ay + (by - ay) * u


def bomba_verne(cv, phase=0.25):
    """La bomba de Verne al pou d'una granja: un balancí blanc amb la gota blava. El cap del balancí (a la dreta)
    puja i baixa damunt del pou; a l'esquerra, la manovella amb el contrapès. `phase` (0..1): una cabotada."""
    px, gy = PUMP
    # l'ombra, cap a la dreta (el sol és a l'esquerra)
    cv.darken(px - 16, gy - 1, px + 44, gy + 3,
              lambda x, y: 0.6 if ((x - px - 12) / 30) ** 2 + ((y - gy - 1) / 2.4) ** 2 <= 1 else 0)
    # el sòcol
    cv.rect(px - 16, gy - 2, px + 20, gy, STEELN, lambda x, y: 1.8 - (y - gy + 2) * 0.4, lit=0)
    # el pou: el capçal blau, amb la gota
    wx = px + 15
    cv.rect(wx - 3, gy - 7, wx + 3, gy - 3, WBLUE, lambda x, y: 3.2 - (x - wx) * 0.25, lit=0)
    cv.hline(wx - 4, wx + 4, gy - 8, WBLUE, 4.2, lit=0)
    cv.flat(wx, gy - 5, (220, 236, 255))
    # el pal (una A)
    pv = (px, gy - 18)
    cv.line(px - 5, gy - 2, pv[0], pv[1], STEELN, 2.6, lit=0)
    cv.line(px + 4, gy - 2, pv[0], pv[1], STEELN, 1.4, lit=0)
    # la manovella i el contrapès, a l'esquerra
    ang = 2 * math.pi * phase
    ck = (px - 11, gy - 7)
    cv.rect(ck[0] - 2, ck[1] - 1, ck[0] + 2, gy - 2, STEELN, 1.2, lit=0)
    cw = (ck[0] - 3 * math.cos(ang), ck[1] - 3 * math.sin(ang))
    cv.disc(cw[0], cw[1], 2.6, 2.6, STEELN, 2.2, lit=0)
    pin = (ck[0] + 3 * math.cos(ang), ck[1] + 3 * math.sin(ang))
    # el balancí: puja del costat del pou quan la manovella baixa
    a = 0.2 * math.sin(ang)
    lx, ly = pv[0] - 12 * math.cos(a), pv[1] + 12 * math.sin(a)
    rx, ry = pv[0] + 15 * math.cos(a), pv[1] - 15 * math.sin(a)
    cv.line(lx, ly, pin[0], pin[1], STEELN, 2.8, lit=0)                  # la biela
    n = 40
    for i in range(n + 1):
        t = i / n
        x, y = lx + (rx - lx) * t, ly + (ry - ly) * t
        cv.put(x, y - 1, WHITEV, 4.6, lit=0)
        cv.put(x, y, WBLUE if 0.3 < t < 0.6 else WHITEV, 3.0, lit=0)
    cv.flat(pv[0], pv[1], INK)
    # el cap de cavall, damunt del pou, i la barra que hi baixa
    hx, hy = round(rx), round(ry)
    cv.rect(hx, hy - 2, hx + 1, hy + 3, WHITEV, lambda x, y: 4.2 - (y - hy) * 0.3, lit=0)
    cv.flat(hx + 2, hy, WHITEV[5])
    cv.vline(hx + 1, hy + 4, gy - 9, STEELN, 3.2, lit=0)
    # la gota de Verne al balancí
    gx, gy2 = round(pv[0] + 4 * math.cos(a)), round(pv[1] - 4 * math.sin(a))
    cv.flat(gx, gy2 - 2, (40, 110, 220))


def cantimplora(cv, light=None, off=False):
    """La nau, de costat, petita, mirant a la dreta: un buc panxut oliva amb la franja taronja, nou dipòsits
    curts en fila al llom, la cabina alçada al morro, l'aleta de cua i la rampa de popa abaixada.
    `off`: apagada (el pròleg): sense llum a la cabina ni a la rampa, el llum de navegació i la brasa morts."""
    x0, gy = SHIP
    L = 124
    top, bot = gy - 34, gy - 10
    cy = (top + bot) / 2
    # l'ombra, llarga cap a la dreta (el sol és a l'esquerra)
    cv.darken(x0 + 10, gy - 2, x0 + L + 60, gy + 5, lambda x, y: 0.7 if ((x - x0 - L / 2 - 26) / (L / 2 + 26)) ** 2 +
              ((y - gy - 1) / 3.6) ** 2 <= 1 else 0)
    cv.tint(x0 + 2, gy - 4, x0 + 50, gy + 8, (255, 190, 110), lambda x, y: 0.45 * max(0.0, 1 - math.hypot(
        x - x0 - 22, (y - gy) * 3) / 26))
    # les potes
    for lx in (x0 + 26, x0 + 70, x0 + 106):
        cv.line(lx, bot, lx - 3, gy, BLACKT, 1.8, lit=0)
        cv.hline(lx - 6, lx, gy, BLACKT, 2.4, lit=0)
    # l'aleta de cua
    cv.poly([(x0 + 4, top + 2), (x0 + 20, top + 2), (x0 + 8, top - 12), (x0 + 2, top - 12)], OLIVE,
            lambda x, y: 4.6 - (y - top + 12) * 0.08, lit=0)
    cv.rect(x0 + 2, top - 12, x0 + 8, top - 9, SAFETY, 4.2, lit=0)
    # els nou dipòsits: cilindres curts amb la tapa rodona, separats
    for k in range(9):
        tx = x0 + 22 + k * 10
        for y in range(top - 8, top + 2):
            for x in range(tx, tx + 8):
                u = (x - tx) / 7
                if y < top - 6 and (u < 0.15 or u > 0.85):
                    continue
                cv.put(x, y, OLIVE, 5.0 - u * 2.2 - (1.0 if y == top - 3 else 0), lit=0)
        cv.flat(tx + 1, top - 7, OLIVE[8])
    # el buc
    for x in range(x0, x0 + L + 1):
        u = (x - x0) / L
        hh = 0.7 + 0.3 * min(1.0, u * 8) if u < 0.85 else 1.0 - ((u - 0.85) / 0.15) ** 2 * 0.6
        a, b = cy - (cy - top) * hh, cy + (bot - cy) * hh
        for y in range(int(a), int(b) + 1):
            v = (y - a) / max(1, b - a)
            lvl = 4.0 - v * 2.0 + (1.0 - u) * 1.2 - (0.9 if (x - x0) % 21 == 0 else 0)
            ramp = SAFETY if 0.42 < v < 0.56 else OLIVE
            if hr(x // 2, y // 2, 70) > 0.93:
                ramp, lvl = RUST, 2.0
            cv.put(x, y, ramp, lvl, lit=0)
        cv.flat(x, int(a) - 1, INK)
        cv.flat(x, int(b) + 1, INK)
    # la cabina, alçada al morro, amb les finestres enceses
    cv.poly([(x0 + L - 34, top + 1), (x0 + L - 26, top - 9), (x0 + L - 8, top - 9), (x0 + L, top + 3)], OLIVE,
            lambda x, y: 4.4 - (y - top + 9) * 0.1, lit=0)
    for i in range(4):
        wx = x0 + L - 26 + i * 5
        cv.rect(wx, top - 6, wx + 2, top - 3, [(24, 26, 32), (44, 48, 56)] if off else [(200, 140, 60), (255, 210, 130)],
                1.0, lit=0)
    if not off:
        cv.glow(x0 + L - 17, top - 5, 12, (255, 200, 120), 0.3)
    # els motors, a popa, amb una brasa
    cv.rect(x0 - 5, int(cy) - 4, x0, int(cy) + 4, STEELN, 1.6, lit=0)
    cv.flat(x0 - 6, int(cy), (60, 46, 44) if off else (255, 140, 60))
    # la rampa abaixada, a popa, i la llum de dins
    cv.poly([(x0 + 10, bot), (x0 + 26, bot), (x0 + 32, gy), (x0 + 6, gy)], OLIVE, 2.4, lit=0)
    cv.rect(x0 + 12, bot - 6, x0 + 24, bot, [(14, 10, 12), (26, 20, 22), (40, 30, 30)] if off else
            [(160, 100, 40), (230, 170, 90), (255, 220, 160)], 1.4, lit=0)
    # el llum de navegació
    lx, ly = x0 + L - 17, top - 14
    cv.vline(lx, ly + 1, top - 10, BLACKT, 1.6, lit=0)
    on = light is not None and light % 3 == 0 and not off
    cv.flat(lx, ly, (255, 80, 60) if on else (60, 22, 22) if off else (120, 30, 30))
    if on:
        cv.glow(lx, ly, 5, (255, 80, 60), 0.6)
    # el port: una grua petita i uns contenidors, en silueta, al costat
    gx = x0 + 150
    cv.vline(gx, gy - 34, gy, BLACKT, 1.2, lit=0)
    cv.vline(gx + 2, gy - 34, gy, BLACKT, 1.2, lit=0)
    cv.hline(gx - 8, gx + 22, gy - 34, BLACKT, 1.2, lit=0)
    cv.vline(gx + 18, gy - 33, gy - 22, BLACKT, 1.0, lit=0)
    cv.flat(gx + 1, gy - 35, (255, 90, 60))
    for k in range(3):
        cx = x0 + 132 + k * 13
        cv.rect(cx, gy - 6 - (k % 2) * 6, cx + 11, gy, [(30, 22, 26), (60, 40, 40), (200, 210, 230)],
                0.8 if k != 1 else 1.6, lit=0)


# ─── El títol ──────────────────────────────────────────────────────────────

def _cells(word, x0, y0):
    out = []
    col = 0
    for ch in word:
        for r, bits in enumerate(LETTERS[ch]):
            for c, b in enumerate(bits):
                if b == '1':
                    out.append((x0 + (col + c) * S, y0 + r * S, ch))
        col += 6
    return out


def _wordw(word):
    return len(word) * 6 * S - S


LEVELS = {0: (0.58, 0.40, 0.66, 0.52, 0.30), 1: (0.46, 0.62, 0.36, 0.70, 0.55)}   # fins on és plena cada lletra


def title(cv, phase=0.0):
    x0, y0, x1, y1 = LABEL
    # l'etiqueta: paper blanc (una mica groguenc), corbada com una ampolla (fosca als cantons)
    for y in range(y0, y1 + 1):
        for x in range(x0, x1 + 1):
            u = (x - x0) / (x1 - x0)
            lvl = 4.6 - (2 * u - 1) ** 4 * 2.6 + (0.6 if 0.18 < u < 0.24 else 0) + (hr(x // 2, y // 2, 71) - 0.5) * 0.3
            cv.put(x, y, CREAM, lvl, lit=0)
    # les franges blaves de dalt i de baix, amb una onada blanca
    for band, (ya, yb) in enumerate(((y0, y0 + 15), (y1 - 15, y1))):
        for y in range(ya, yb + 1):
            for x in range(x0, x1 + 1):
                u = (x - x0) / (x1 - x0)
                wave = math.sin(x / 9 + band * 2) * 2.2
                inner = (y - ya) if band == 1 else (yb - y)
                if band == 0 and y > yb - 4 + wave * 0.6:
                    continue
                if band == 1 and y < ya + 4 + wave * 0.6:
                    continue
                lvl = 2.6 - (2 * u - 1) ** 4 * 2.0 + (0.5 if 0.18 < u < 0.24 else 0)
                cv.put(x, y, WBLUE, lvl, lit=0)
                if abs(y - (yb - 3 if band == 0 else ya + 3) - wave * 0.6) < 0.8:
                    cv.flat(x, y, mix(cv.get(x, y), (220, 236, 255), 0.7))
    # el text petit de les franges: el lema de Verne i el preu
    s1 = 'PERQUÈ LA SET NO ESPERA'
    text(cv, s1, (x0 + x1 - text_width(s1)) // 2, y1 - 7, None, 0, flat=(230, 240, 255))
    s2 = 'AIGUA DE DIPOSIT ORBITAL  ·  1 L'
    text(cv, s2, (x0 + x1 - text_width(s2)) // 2, y0 + 2, None, 0, flat=(230, 240, 255))
    # les lletres grosses, de vidre, mig plenes d'aigua
    lines = ('AIGUA', 'VERNE')
    ly = (y0 + 22, y0 + 22 + 7 * S + 10)
    for li, word in enumerate(lines):
        wx = (x0 + x1 - _wordw(word)) // 2 + (10 if li == 0 else 10)
        cells = _cells(word, wx, ly[li])
        filled = {(cx_, cy_) for cx_, cy_, _ in cells}
        # l'ombra i el contorn
        for cx_, cy_, _ in cells:
            cv.rect(cx_ + 3, cy_ + 3, cx_ + S + 2, cy_ + S + 2, [mix(CREAM[2], (0, 0, 0), 0.25)], 0, lit=0)
        for cx_, cy_, _ in cells:
            cv.rect(cx_ - 2, cy_ - 2, cx_ + S + 1, cy_ + S + 1, [NAVY[0]], 0, lit=0)
        for cx_, cy_, ch in cells:
            k = 'AIGUA'.index(ch) if li == 0 else 'VERNE'.index(ch) if ch != 'E' else (1 if cx_ < wx + 3 * 6 * S
                                                                                       else 4)
            col_idx = (cx_ - wx) // (6 * S)
            level = LEVELS[li][col_idx]
            top_l, bot_l = ly[li], ly[li] + 7 * S
            wl_base = bot_l - (bot_l - top_l) * level
            for py in range(cy_, cy_ + S):
                for px in range(cx_, cx_ + S):
                    wl = wl_base + math.sin(px / 7 + phase + col_idx * 1.3) * 2.0
                    edge_t = (px, py - S) if False else None
                    if py < wl:
                        # vidre buit: blanc blavós, amb un reflex
                        lvl = 2.0 - (py - top_l) / (7 * S) * 0.8
                        if (px - cx_) < 2 and (cx_ - S, cy_) not in filled:
                            lvl += 1.0
                        cv.put(px, py, GLASS, lvl, lit=0)
                    else:
                        d = (py - wl) / max(1, bot_l - wl)
                        lvl = 4.2 - d * 2.6 + (0.6 if (px - cx_) < 2 and (cx_ - S, cy_) not in filled else 0)
                        cv.put(px, py, WATER, lvl, lit=0)
                        if py - wl < 1.2:
                            cv.flat(px, py, (220, 240, 255))
                        elif py - wl < 6 and hr(px, py, 72) > 0.94:
                            cv.flat(px, py, (180, 220, 255))          # bombolles
                    if py == cy_ and (cx_, cy_ - S) not in filled:
                        cv.flat(px, py, mix(cv.get(px, py), (255, 255, 255), 0.5))
                    if px == cx_ + S - 1 and (cx_ + S, cy_) not in filled:
                        cv.flat(px, py, mix(cv.get(px, py), NAVY[2], 0.4))
        # cantons arrodonits: es treuen els píxels dels cantons de fora
        for cx_, cy_, _ in cells:
            for dx, dy, nx_, ny_ in ((-2, -2, -S, -S), (S + 1, -2, S, -S), (-2, S + 1, -S, S), (S + 1, S + 1, S, S)):
                if (cx_ + nx_, cy_) not in filled and (cx_, cy_ + ny_) not in filled:
                    px, py = cx_ + dx, cy_ + dy
                    cv.flat(px, py, cv.get(px + (1 if dx < 0 else -1) * 3, py) if False else CREAM[4])
    # la gota de Verne, grossa, al costat de «AIGUA»
    drop(cv, x0 + 30, ly[0] + 40, 13, WBLUE, 3.6)
    cv.disc(x0 + 26, ly[0] + 36, 2.5, 3.5, WBLUE, 6.4, lit=0)
    # rovell: les vores esquerdades, taques i un regalim del cantó de dalt a la dreta
    for k in range(70):
        side = k % 4
        if side == 0:
            px, py = x0 + int(hr(k, 73) * (x1 - x0)), y0 + int(hr(k, 74) * 4)
        elif side == 1:
            px, py = x0 + int(hr(k, 73) * (x1 - x0)), y1 - int(hr(k, 74) * 4)
        elif side == 2:
            px, py = x0 + int(hr(k, 74) * 5), y0 + int(hr(k, 73) * (y1 - y0))
        else:
            px, py = x1 - int(hr(k, 74) * 5), y0 + int(hr(k, 73) * (y1 - y0))
        r = 1 + hr(k, 75) * 3
        cv.disc(px, py, r, r * 0.8, RUST, lambda nx, ny: 2.6 + nx * 0.6 + (hr(int(nx * 4), int(ny * 4), k) - 0.5),
                lit=0)
    for j in range(46):                                                 # el regalim
        if hr(j, 76) > 0.2:
            cv.put(x1 - 22 + (1 if j > 30 else 0), y0 + 2 + j, RUST, 2.8 - j * 0.04, lit=0)
    for k in range(10):                                                 # esquerdes de l'esmalt
        px, py = x0 + 8 + int(hr(k, 77) * (x1 - x0 - 16)), y0 + 16 + int(hr(k, 78) * (y1 - y0 - 32))
        for j in range(4 + int(hr(k, 79) * 6)):
            cv.flat(px + j, py + int(math.sin(j + k) * 1.2), mix(cv.get(px + j, py), (120, 100, 80), 0.5))
    # el cantó de baix a l'esquerra, esquinçat i doblegat
    for j in range(12):
        for i in range(12 - j):
            cv.put(x0 + i, y1 - j, CREAM, 2.4 - i * 0.06, lit=0)
    cv.line(x0, y1 - 12, x0 + 12, y1, [INK], 0, lit=0)
    # el contorn de l'etiqueta
    for x in range(x0 - 1, x1 + 2):
        cv.flat(x, y0 - 1, INK)
        if x > x0 + 12:
            cv.flat(x, y1 + 1, INK)
    for y in range(y0 - 1, y1 + 2):
        cv.flat(x0 - 1, y, INK) if y < y1 - 12 else None
        cv.flat(x1 + 1, y, INK)
    cv.darken(x0 + 4, y1 + 2, x1 + 4, y1 + 5, 0.5)
    cv.darken(x1 + 2, y0 + 4, x1 + 5, y1 + 5, 0.5)


# ─── La pols ───────────────────────────────────────────────────────────────

def dust(cv, frame):
    """Cortines de pols que passen arran de terra, de dreta a esquerra."""
    for y in range(HOR - 26, H):
        t = (y - HOR + 26) / (H - HOR + 26)
        for x in range(W):
            u = (x + frame * 6) / 120
            d = fbm(u, y / 10, 81) - 0.52 + 0.16 * math.sin(u * 3 + y / 30)
            if d > 0:
                a = min(1.0, d * 3.0) * 0.32 * (1 - abs(t - 0.4))
                if a > 0 and (a > 0.2 or hr(x, y, frame) < a * 4):
                    o = cv.get(x, y)
                    cv.flat(x, y, mix(o, (214, 150, 104), a))


# ─── Composició ────────────────────────────────────────────────────────────

def scene(cv, light=None, ship_off=False, pump=True):
    """L'escena sense el títol (el fons de la portada i del pròleg). Per a les capes del pròleg: `ship_off`, la nau
    apagada; `pump=False`, sense la bomba (per dibuixar-la en una altra posició)."""
    sky(cv)
    tank_and_pipe(cv, light)
    plain(cv)
    ground_pipe(cv)
    if pump:
        bomba_verne(cv)
    cantimplora(cv, light, off=ship_off)


def bg(cv):
    scene(cv, _ANIM['llums'])
    if _ANIM['pols'] is not None:
        dust(cv, _ANIM['pols'])


@functools.lru_cache(maxsize=None)
def _base_img():
    cv = Canvas(light=LIGHT)
    bg(cv)
    return cv.img.copy()


def base_img():
    """El fons (sense títol ni animacions), per fer-hi capes a sobre: no el modifiquis, copia'l."""
    return _base_img()


def diff(img, base=None, force=()):
    """Els píxels de `img` que canvien respecte de `base` (el fons), i tots els de les caixes de `force`."""
    import numpy as np
    from PIL import Image
    a = np.asarray(img.convert('RGBA')).copy()
    b = np.asarray((base or _base_img()).convert('RGBA'))
    same = (a == b).all(axis=2)
    s = img.width // W                                     # les caixes són en coordenades de sala (art a 2×: ×2)
    for x0, y0, x1, y1 in force:
        same[max(0, y0 * s):(y1 + 1) * s, max(0, x0 * s):(x1 + 1) * s] = False
    a[same] = (0, 0, 0, 0)
    return Image.fromarray(a, 'RGBA')


@functools.lru_cache(maxsize=None)
def _frames(key, n):
    """(La portada i el pròleg en fan servir els mateixos: es dibuixen una sola vegada.)"""
    out = []
    for f in range(n):
        _ANIM[key] = f
        try:
            cv = Canvas(light=LIGHT)
            bg(cv)
        finally:
            _ANIM[key] = None
        out.append(diff(cv.img))
    return out


def _title_frames(n=8):
    out = []
    for f in range(n):
        cv = Canvas(light=LIGHT, img=_base_img().copy())
        title(cv, f * math.pi / 4)
        out.append(diff(cv.img))
    return out


PROPS = {}

POLS = {'frames': lambda: _frames('pols', 16), 'frameDuration': 160}
LLUMS = {'frames': lambda: _frames('llums', 12), 'frameDuration': 260}

ANIMS = {
    'pols': POLS,
    'llums': LLUMS,
    'titol': {'frames': _title_frames, 'frameDuration': 180, 'zIndex': 3},
}

GEOMETRIA = {'things': {}, 'spawns': {}}
