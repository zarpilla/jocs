"""
Final «La fugida»: la Sala de la Memòria, uns mesos després, convertida en un museu de veritat. Llum càlida de
focus, la llibreta de torn exposada, la clau anglesa a la vitrina, la foto del torn de nit restaurada (la cara de
l'Iri sencera i un cartellet «DESAPAREGUDA» a sota) i el sòcol de l'holograma apagat, tapat amb un drap.
Fa de conserge el Cargol vell, rovellat, al costat de la porta.

`bg(cv, mira=True)`: la Mira d'Orís, a la foto; sense, al seu lloc hi ha un buit net. Al joc, la Mira és el
prop `foto_mira` (només si l'Iri la va salvar), i en Cargol conserge, el prop `conserge_cargol` (només si li
van reparar la memòria).
"""
import math

from hd.pix import (Canvas, Light, B4, W, H, hr, ramp, mix, STEEL, IRON, PAPER, GOLD, WALNUT, RED, WARN, COPPER)
from hd.rooms.gavina_passadis import PILOT, text, text_w
from hd.rooms.gavina_memoria import SEPIA, FRAME, VELVET, spot_cone
from hd.rooms.fabrica_cambra import FE9
from hd.characters import cargol, person, VET, DENIM, M

# Plafons del museu nou: crema càlid, ombres de color tabac
CREAM = ramp((16, 12, 16), (38, 30, 32), (66, 54, 52), (98, 84, 76), (132, 116, 100), (164, 148, 124),
             (194, 178, 150), (218, 204, 174), (236, 226, 200), (248, 242, 222), n=10)
# Terra de resina, ara encerat i càlid
WAX = ramp((10, 8, 12), (22, 18, 22), (38, 32, 34), (58, 50, 48), (82, 72, 64), (110, 98, 84), (142, 128, 106),
           (178, 162, 132), n=9)
CLOTH = ramp((26, 22, 26), (54, 48, 50), (90, 82, 80), (126, 118, 110), (160, 152, 138), (192, 184, 166),
             (220, 212, 192), n=7)
MANILA_T = [(64, 44, 28), (110, 82, 48), (158, 126, 74), (198, 166, 102), (226, 198, 136), (244, 224, 170)]
LEAF = [(14, 30, 16), (26, 56, 26), (44, 90, 38), (70, 128, 54), (110, 170, 80)]
DEAD = ramp((6, 10, 16), (12, 22, 32), (22, 38, 52), (36, 58, 74), (60, 88, 104), n=5)     # vidre de l'emissor, apagat
SPOT = (255, 226, 176)

FLOOR_Y = 154
SPOTS = {'foto': (130, 12), 'llibreta': (166, 12), 'fabrica': (310, 12), 'vitrina': (382, 12)}
PEDX, PEDY = 346, 238                     # sòcol apagat, en primer terme
CGX, CGY = 446, 202                       # peus del Cargol
VTX, VTY = 96, 214                        # peus de la Vet


def warm_pool(x, y):
    """Bassals de llum al terra sota els focus i al primer terme."""
    if y < FLOOR_Y:
        return 0.0
    v = 0.9 * max(0.0, 1 - math.hypot((x - 240) / 230, (y - 172) / 34))
    v += 1.2 * max(0.0, 1 - math.hypot((x - 100) / 110, (y - 210) / 40)) ** 1.2
    v += 1.5 * max(0.0, 1 - math.hypot((x - 380) / 110, (y - 222) / 44)) ** 1.2
    return v


LIGHT = Light(ambient=0.15, vignette=(56, 26), floor_fade=(214, 70))
LIGHT.add(spot_cone(*SPOTS['foto'], 130, 64, 70, 2.6))
LIGHT.add(spot_cone(*SPOTS['llibreta'], 219, 62, 64, 2.2))
LIGHT.add(spot_cone(*SPOTS['fabrica'], 310, 64, 52, 2.0))
LIGHT.add(spot_cone(*SPOTS['vitrina'], 382, 98, 56, 2.3))
LIGHT.add(warm_pool)


# ─── Paret i terra ──────────────────────────────────────────────────────────

def wall(cv):
    pw = 48
    for y in range(0, FLOOR_Y):
        for x in range(W):
            px = (x - 4) % pw
            lvl = 3.0 + (hr((x - 4) // pw, 2) - 0.5) * 0.15
            if y < 10:
                lvl = 1.2 + (0.8 if y in (7, 8) else 0)
            elif y == 10:
                lvl = 4.0
            elif y < 13:
                lvl = 1.0
            elif y < 112:
                if px == 0:
                    lvl = 1.6
                elif px == 1:
                    lvl += 0.6
                elif px == pw - 1:
                    lvl -= 0.5
                lvl -= max(0.0, 1 - (y - 13) / 16) * 1.2
            elif y < 116:
                lvl = [4.4, 3.6, 2.4, 1.4][y - 112]                         # passamà (ara de fusta, vegeu més avall)
            elif y < 146:
                lvl = 2.8 + (0.2 if px < 2 else 0)
                if px == 0:
                    lvl = 1.6
            else:
                lvl = [3.6, 1.6, 1.4, 1.3, 1.2, 1.0, 0.8, 0.4][y - 146]
            cv.put(x, y, CREAM, lvl)
    # el passamà, de fusta encerada
    for y in range(112, 116):
        cv.hline(0, W - 1, y, WALNUT, [5.4, 4.4, 3.2, 1.4][y - 112])
    # sòcol de fusta fosca
    for y in range(146, FLOOR_Y):
        cv.hline(0, W - 1, y, WALNUT, [4.4, 2.6, 2.2, 2.0, 1.8, 1.6, 1.2, 0.6][y - 146])


def floor(cv):
    vx, vy, S, K = 240, 30, 1.7, 700.0
    for y in range(FLOOR_Y, H):
        d = y - vy
        v = K / d
        vi = math.floor(v)
        fv = (vi + 1 - v) * d * d / K
        for x in range(W):
            u = (x - vx) / d * S
            ui = math.floor(u)
            fu = (u - ui) * d / S
            lvl = 3.0 + (hr(ui, vi, 7) - 0.5) * 0.25
            if fu < 1 or fv < 1:
                lvl = 1.8
            if y < 160:
                lvl -= (160 - y) / 6 * 0.9
            cv.put(x, y, WAX, lvl)


def reflect(cv, y0=FLOOR_Y, y1=H - 1, k=0.22, depth=60):
    for y in range(y0, y1 + 1):
        sy = 2 * (FLOOR_Y - 1) - y
        if sy < 0:
            break
        a = k * max(0.0, 1 - (y - FLOOR_Y) / depth)
        for x in range(W):
            if a > B4[y & 3][x & 3] * 0.45:
                s, o = cv.P[x, sy], cv.P[x, y]
                if sum(s[:3]) > sum(o[:3]):
                    cv.P[x, y] = mix(o, s, a) + (255,)


def frame(cv, x0, y0, x1, y1, rp=FRAME, shadow=True):
    """Marc de 4 píxels amb bisell, i ombra a la paret."""
    if shadow:
        cv.darken(x0 + 2, y0 + 2, x1 + 3, y1 + 3, 0.7)
    for y in range(y0, y1 + 1):
        for x in range(x0, x1 + 1):
            dd = min(x - x0, x1 - x, y - y0, y1 - y)
            if dd > 3:
                continue
            lvl = [2.0, 4.6, 3.6, 2.4][dd]
            if (x1 - x) < 4 or (y1 - y) < 4:
                lvl -= 0.8
            cv.put(x, y, rp, lvl)


def spot(cv, sx, sy):
    cv.rect(sx - 2, 11, sx + 2, 13, IRON, 3.0)
    cv.poly([(sx - 5, 14), (sx + 3, 13), (sx + 5, 19), (sx - 3, 21)], IRON, lambda x, y: 3.6 - (x - sx) * 0.25)
    cv.line(sx - 3, 21, sx + 5, 19, [SPOT], 0, 0)
    cv.glow(sx + 1, 21, 12, (255, 230, 180), 0.7)


# ─── La foto del torn de nit, restaurada ───────────────────────────────────

FX0, FY0, FX1, FY1 = 92, 37, 167, 92
PX0, PY0, PX1, PY1 = FX0 + 4, FY0 + 4, FX1 - 4, FY1 - 4
IRI_X = 114


def foto(cv, mira):
    frame(cv, FX0, FY0, FX1, FY1)
    for y in range(PY0, PY1 + 1):
        for x in range(PX0, PX1 + 1):
            lvl = 2.6 + (y - PY0) / 40 + (hr(x // 3, y // 3, 3) - 0.5) * 0.2
            if (x - PX0) % 12 == 0 and y < PY0 + 26:
                lvl -= 0.6
            if y < PY0 + 4:
                lvl -= 0.6
            fd = math.hypot(x - 152, y - 56)
            if fd < 9:
                lvl += (1 - fd / 9) * 2.8
            cv.put(x, y, SEPIA, lvl, 0.3)
    people = [(104, 28, True), (IRI_X, 27, False), (123, 23, False), (133, 29, True), (143, 27, True)]
    for k, (px, h, cap) in enumerate(people):
        if k == 2 and not mira:
            continue
        top = PY1 - h
        for y in range(top + 7, PY1 + 1):
            half = 3 + (1 if y > top + 9 else 0)
            for x in range(px - half, px + half + 1):
                cv.put(x, y, SEPIA, 1.4 - (x - px) * 0.1 + (0.6 if x == px - half else 0), 0.3)
        cv.rect(px - 1, top + 5, px + 1, top + 7, SEPIA, 3.6, 0.3)
        cv.disc(px, top + 3, 2.5, 3, SEPIA, lambda nx, ny: 4.8 - nx * 0.8 - ny * 0.4, 0.3)
        if cap:
            cv.rect(px - 3, top, px + 2, top + 1, SEPIA, 1.2, 0.3)
        else:
            cv.rect(px - 2, top, px + 2, top + 1, SEPIA, 0.8, 0.3)
            cv.vline(px - 3, top + 1, top + 4, SEPIA, 0.8, 0.3)
        # ulls: ara totes les cares hi són
        cv.put(px - 1, top + 3, SEPIA, 2.2, 0.3)
        cv.put(px + 1, top + 3, SEPIA, 2.2, 0.3)
    # l'Iri: l'abric clar obert, la trena i un mig somriure
    itop = PY1 - 27
    for y in range(itop + 7, PY1 + 1):
        half = 3 + (1 if y > itop + 9 else 0)
        for x in range(IRI_X - half, IRI_X + half + 1):
            lvl = 3.6 - (x - IRI_X) * 0.15 + (0.6 if x == IRI_X - half else 0)
            if x == IRI_X and y > itop + 8:
                lvl = 1.2                                                   # l'abric obert
            cv.put(x, y, SEPIA, lvl, 0.3)
    cv.vline(IRI_X - 3, itop + 1, itop + 5, SEPIA, 0.8, 0.3)
    for y in range(itop + 6, itop + 15):                                     # la trena, per sobre l'espatlla
        cv.put(IRI_X - 2 - (y > itop + 8), y, SEPIA, 0.6 + (y % 2) * 0.8, 0.3)
    cv.hline(IRI_X - 1, IRI_X, itop + 5, SEPIA, 2.6, 0.3)
    if mira:
        mx, mtop = 123, PY1 - 23
        cv.vline(mx + 3, mtop + 2, mtop + 8, SEPIA, 0.8, 0.3)
        cv.hline(mx - 1, mx + 1, mtop + 5, SEPIA, 2.0, 0.3)
    # el Cargol, nou de trinca
    cv.rect(153, PY1 - 22, 160, PY1 - 10, SEPIA, lambda x, y: 5.0 - (x - 153) * 0.3, 0.3)
    cv.rect(154, PY1 - 27, 159, PY1 - 23, SEPIA, 5.4, 0.3)
    cv.put(155, PY1 - 26, SEPIA, 0.6, 0.3); cv.put(158, PY1 - 26, SEPIA, 0.6, 0.3)
    cv.vline(156, PY1 - 30, PY1 - 28, SEPIA, 4.0, 0.3)
    cv.rect(154, PY1 - 9, 155, PY1, SEPIA, 3.6, 0.3); cv.rect(158, PY1 - 9, 159, PY1, SEPIA, 3.6, 0.3)
    cv.put(156, PY1 - 18, SEPIA, 6.4, 0.3)
    cv.darken(PX0, PY0, PX1, PY1, lambda x, y: max(0.0, 0.5 - min(x - PX0, PX1 - x, y - PY0, PY1 - y) / 7), dither=False)
    # vidre nou del marc: un reflex
    for i in range(10):
        if hr(i, 9) > 0.3:
            cv.put(PX0 + 40 + i, PY0 + 10 - i, [(255, 244, 220)], 0, 0)

    # cartellet nou, sota l'Iri: «DESAPAREGUDA»
    s = 'DESAPAREGUDA'
    tw = text_w(s)
    cx0 = IRI_X - 8
    cx1 = cx0 + tw + 5
    cy0 = FY1 + 6
    cv.darken(cx0 + 2, cy0 + 2, cx1 + 2, cy0 + 11, 0.7)
    cv.rect(cx0, cy0, cx1, cy0 + 9, PAPER, lambda x, y: 4.8 - (y - cy0) * 0.08)
    cv.hline(cx0, cx1, cy0, PAPER, 5.8)
    cv.vline(cx1, cy0, cy0 + 9, PAPER, 3.0)
    cv.hline(cx0, cx1, cy0 + 9, PAPER, 2.6)
    text(cv, cx0 + 3, cy0 + 2, s, WALNUT, 1.0, 0)
    cv.put(IRI_X, cy0 - 1, PAPER, 5.8)                                          # la puntera, cap a l'Iri
    cv.hline(IRI_X - 1, IRI_X + 1, cy0, PAPER, 5.8)


# ─── La llibreta de torn, oberta en una vitrina de paret ───────────────────

def llibreta(cv):
    X0, Y0, X1, Y1 = 178, 33, 260, 92
    frame(cv, X0, Y0, X1, Y1, WALNUT)
    # fons de vellut verd fosc
    for y in range(Y0 + 4, Y1 - 3):
        for x in range(X0 + 4, X1 - 3):
            cv.put(x, y, VELVET, 1.8 + (hr(x // 2, y // 2, 4) - 0.5) * 0.3 - (0.8 if y < Y0 + 7 else 0), 0.5)
    # la llibreta: tapes de cuiro i dues pàgines
    cx = (X0 + X1) // 2
    PT, PB = 44, 80
    cv.rect(cx - 33, PT - 2, cx + 33, PB + 2, COPPER, lambda x, y: 1.6 - (y - PT) / 60, 0.6)
    for side in (-1, 1):
        for y in range(PT, PB + 1):
            for x in range(cx + (1 if side > 0 else -31), cx + (31 if side > 0 else -1) + 1):
                u = abs(x - cx) / 31
                lvl = 4.4 - (0.9 if u < 0.12 else 0) - (0.4 if u < 0.25 else 0) + (hr(x // 3, y, 8) - 0.5) * 0.2
                if y in (PT, PB):
                    lvl -= 0.5
                cv.put(x, y, PAPER, lvl, 0.6)
    cv.vline(cx, PT - 1, PB + 1, COPPER, 0.6, 0.3)
    # escriptura a mà (llapis), una mica tremolosa
    for y in range(PT + 4, PB - 2, 3):
        x = cx - 28
        while x < cx - 4:
            n = 2 + int(hr(x, y, 1) * 5)
            for i in range(n):
                if x + i < cx - 4:
                    cv.put(x + i, y + (1 if hr(x + i, y, 2) > 0.8 else 0), WALNUT, 1.6 + hr(x + i, y) * 0.6, 0.3)
            x += n + 2
    # pàgina dreta: l'esbós de la cambra (tres bobines) i unes línies
    bx, by = cx + 6, PT + 4
    for x in range(bx, bx + 15):
        cv.put(x, by, WALNUT, 1.8, 0.3); cv.put(x, by + 18, WALNUT, 1.8, 0.3)
    for y in range(by, by + 19):
        cv.put(bx, y, WALNUT, 1.8, 0.3); cv.put(bx + 14, y, WALNUT, 1.8, 0.3)
    for k in range(3):
        for y in range(by + 3, by + 16):
            if y % 2:
                cv.hline(bx + 3 + k * 4, bx + 4 + k * 4, y, COPPER, 2.4, 0.3)
    for i in range(6):
        cv.put(bx + 18 + i, by + 6 - (i % 2), WALNUT, 1.8, 0.3)                 # «una fletxa»
    for y in range(by + 22, PB - 2, 3):
        x = cx + 4
        while x < cx + 28:
            n = 2 + int(hr(x, y, 3) * 5)
            for i in range(n):
                if x + i < cx + 28:
                    cv.put(x + i, y, WALNUT, 1.6 + hr(x + i, y) * 0.6, 0.3)
            x += n + 2
    # vidre amb reflex
    for i in range(16):
        cv.put(X0 + 8 + i, Y0 + 22 - i, [(255, 246, 226)], 0, 0)
        if i < 9:
            cv.put(X0 + 13 + i, Y0 + 24 - i, [(236, 220, 196)], 0, 0)
    # títol a la paret, a sota
    s = 'LLIBRETA DE TORN'
    tx = cx - text_w(s) // 2
    text(cv, tx, Y1 + 6, s, WALNUT, 1.2, 0)
    cv.hline(tx, tx + text_w(s) - 1, Y1 + 12, GOLD, 3.2, 0.4)


# ─── La fàbrica Aldaia: fotografia gran on abans hi havia l'holograma ──────

def fabrica(cv):
    X0, Y0, X1, Y1 = 278, 40, 342, 92
    frame(cv, X0, Y0, X1, Y1)
    for y in range(Y0 + 4, Y1 - 3):
        for x in range(X0 + 4, X1 - 3):
            lvl = 2.2 + (y - Y0) / 30 + (hr(x // 2, y // 2, 13) - 0.5) * 0.25
            cv.put(x, y, SEPIA, lvl, 0.3)
    # la nau, la casa del rellotge i les xemeneies (el mateix pla del pròleg)
    base = 79
    cv.rect(X0 + 5, 63, 314, base, SEPIA, 1.2, 0.3)
    cv.poly([(X0 + 5, 63), (314, 63), (309, 58), (X0 + 9, 58)], SEPIA, 0.8, 0.3)
    cv.poly([(312, base), (312, 62), (324, 54), (337, 62), (337, base)], SEPIA, 1.5, 0.3)
    cv.disc(324.5, 61, 2, 2, SEPIA, 4.6, 0.3)
    for x0, top in ((X0 + 9, 49), (305, 51), (333, 47)):
        cv.rect(x0, top, x0 + 2, 63, SEPIA, 1.0, 0.3)
        for i in range(8):                                                  # fum
            cv.put(x0 + 1 + i, top - 2 - i // 2 - (i % 2), SEPIA, 3.6 + hr(i, x0) * 0.6, 0.3)
            cv.put(x0 + 2 + i, top - 3 - i // 2, SEPIA, 3.2, 0.3)
    for x in range(X0 + 8, 312, 4):                                       # finestres enceses
        cv.rect(x, 67, x + 1, 70, SEPIA, 5.0, 0.3)
    for x in (316, 320, 329, 333):
        cv.rect(x, 66, x + 1, 69, SEPIA, 5.0, 0.3)
    cv.rect(323, 72, 326, base, SEPIA, 6.0, 0.3)                          # la porta oberta
    # el riu i el reflex
    for y in range(base + 1, Y1 - 3):
        for x in range(X0 + 4, X1 - 3):
            cv.put(x, y, SEPIA, 1.4 + (2.6 if (x - X0) % 4 == 0 and hr(x, y, 4) > 0.6 and x % 4 == 0 else 0), 0.3)
    cv.darken(X0 + 4, Y0 + 4, X1 - 4, Y1 - 4, lambda x, y: max(0.0, 0.5 - min(x - X0 - 4, X1 - 4 - x, y - Y0 - 4, Y1 - 4 - y) / 6), dither=False)
    s = 'ALDAIA · FERRO-9'
    text(cv, (X0 + X1) // 2 - text_w(s) // 2, Y1 + 6, s, WALNUT, 1.2, 0)


# ─── Vitrina: la clau anglesa del Lot 1, que no s'ha rovellat mai ──────────

def vitrina(cv):
    VX0, VX1, GT = 356, 407, 89
    cv.rect(VX0 + 2, 121, VX1 - 2, 153, CREAM, lambda x, y: 4.6 - (x - VX0) / 40 - (2.4 if y > 149 else 0) + (0.8 if x == VX0 + 2 else 0))
    cv.hline(VX0 + 1, VX1 - 1, 120, CREAM, 5.6)
    cv.vline(VX1 - 2, 121, 153, CREAM, 2.4)
    cv.rect(368, 128, 395, 136, GOLD, lambda x, y: 3.6 - (y - 128) * 0.15, 0.3)
    text(cv, 370, 130, 'LOT 1', WALNUT, 1.0, 0)
    for y in range(GT, 120):
        for x in range(VX0, VX1 + 1):
            cv.put(x, y, CREAM, 2.8 + (y - GT) / 60, 0.6)
    cv.rect(VX0 + 2, 108, VX1 - 2, 119, VELVET, lambda x, y: 3.4 - (y - 108) * 0.12)
    cv.hline(VX0 + 2, VX1 - 2, 108, VELVET, 4.6)
    cv.darken(363, 115, 398, 116, 0.8)                                      # ombra de la clau
    # la clau: mànec de ferro-9 polit i dues boques
    for x in range(366, 391):
        cv.put(x, 112, FE9, 6.4, 0)
        cv.put(x, 113, FE9, 5.0, 0)
        cv.put(x, 114, FE9, 3.0, 0)
    cv.disc(364, 113, 3.4, 2.8, FE9, lambda nx, ny: 5.4 - nx * 1.2 - ny * 1.6, 0)
    cv.disc(392, 113, 3.6, 3.0, FE9, lambda nx, ny: 5.4 - nx * 1.2 - ny * 1.6, 0)
    cv.rect(361, 112, 363, 114, VELVET, 3.4)
    cv.rect(394, 112, 396, 114, VELVET, 3.4)
    for x in range(372, 384, 2):
        cv.put(x, 113, FE9, 3.6, 0)                                       # el segell gravat
    cv.glow(378, 112, 18, (220, 236, 255), 0.35)
    cv.poly([(366, 117), (378, 117), (377, 119), (367, 119)], PAPER, 4.4)
    cv.rect(VX0 - 1, GT - 3, VX1 + 1, GT - 1, WALNUT, lambda x, y: 5.0 - (y - GT + 3))
    cv.hline(VX0 + 2, VX1 - 2, GT, [(255, 240, 210)], 0, 0)
    for x in (VX0, VX1):
        cv.vline(x, GT, 119, WALNUT, 5.0 if x == VX0 else 2.4)
    for i in range(14):
        cv.put(VX0 + 6 + i, 100 - i, [(255, 248, 230)], 0, 0)
        if i % 3:
            cv.put(VX0 + 9 + i, 104 - i, [(230, 216, 196)], 0, 0)
        cv.put(VX0 + 30 + i // 2, 98 - i, [(236, 224, 204)], 0, 0)
    cv.glow(381, 100, 30, (255, 236, 200), 0.25)


# ─── Expositor de fullets nous (museu, no corporació) ──────────────────────

def expositor(cv):
    EX0, EX1 = 428, 463
    for lx in (EX0 + 3, EX1 - 4):
        cv.rect(lx, 136, lx + 1, 156, WALNUT, 3.0)
    cv.rect(EX0 + 2, 154, EX1 - 2, 156, WALNUT, 2.4)
    cv.rect(EX0, 104, EX1, 138, WALNUT, lambda x, y: 2.6 - (x - EX0) / 60)
    cv.hline(EX0, EX1, 104, WALNUT, 5.0)
    cv.rect(EX0 - 1, 98, EX1 + 1, 104, GOLD, lambda x, y: 3.4 - (y - 98) * 0.2, 0.3)
    text(cv, EX0 + 8, 99, 'MUSEU', WALNUT, 1.0, 0)
    for row, y0 in enumerate((107, 117, 127)):
        for col, x0 in enumerate((EX0 + 2, EX0 + 19)):
            cv.rect(x0, y0, x0 + 14, y0 + 9, PAPER, 4.6, 0.4)
            cv.rect(x0 + 2, y0 + 2, x0 + 6, y0 + 6, SEPIA, 2.0 + (row + col) % 2, 0.3)        # una foto petita
            cv.hline(x0 + 8, x0 + 12, y0 + 3, CREAM, 3.0, 0)
            cv.hline(x0 + 8, x0 + 11, y0 + 5, CREAM, 3.0, 0)
            cv.hline(x0 + 2, x0 + 12, y0 + 8, CREAM, 3.4, 0)
            cv.hline(x0 - 1, x0 + 15, y0 + 9, WALNUT, 4.0)


# ─── El sòcol de l'holograma, apagat i tapat amb un drap ───────────────────

def socol_apagat(cv):
    cx, by = PEDX, PEDY
    R, top = 30, by - 30
    # ombra al terra
    cv.darken(cx - R - 8, by - 4, cx + R + 10, by + 8,
              lambda x, y: 0.9 - abs((x - cx - 3) / (R + 10)) ** 2 - abs(y - by - 1) / 8)
    # cos cilíndric de plaques (fred: no és d'aquest museu)
    for y in range(top, by + 1):
        for x in range(cx - R, cx + R + 1):
            nx = (x - cx) / R
            if y > by - 6 and (nx * nx + ((y - (by - 6)) / 6) ** 2) > 1:
                continue
            lvl = 4.6 - nx * 1.6 - abs(nx) ** 3 * 2.2 - (y - top) / 26
            ang = math.degrees(math.asin(max(-1, min(1, nx))))
            if abs((ang + 90) % 30 - 15) > 14:
                lvl = 1.6
            cv.put(x, y, STEEL, lvl)
    for ang in range(-75, 90, 30):
        x = round(cx + math.sin(math.radians(ang)) * (R - 2))
        cv.put(x, top + 6, STEEL, 7.0)
        cv.put(x, by - 6, STEEL, 6.0)
    # tapa amb l'emissor mort (el vidre blau, fosc i polsós)
    cv.disc(cx, top, R, 6, STEEL, lambda nx, ny: 6.0 - ny * 0.8 - nx * 0.8)
    cv.disc(cx, top, R - 5, 4.4, STEEL, 2.4)
    cv.disc(cx, top + 0.5, R - 7, 3.4, DEAD, lambda nx, ny: 2.6 - (nx * nx + ny * ny) * 1.4 - nx * 0.6, 0)
    cv.disc(cx, top + 0.5, 9, 1.4, DEAD, 0.4, 0)
    for i in range(5):
        cv.put(cx - 16 + i, top - 1 - (i > 2), DEAD, 4.0, 0)                  # un reflex mort al vidre
    # el drap: posat per damunt, deixa veure l'emissor a l'esquerra i cau en plecs per davant i per la dreta
    def rim(x):                                                      # vora de davant de la tapa
        nx = (x - cx) / (R + 2)
        return top + 6.5 * math.sqrt(max(0.0, 1 - nx * nx))

    def back(x):
        nx = (x - cx) / (R + 2)
        return top - 7.0 * math.sqrt(max(0.0, 1 - nx * nx))

    def hem(x):
        u = max(0.0, (x - (cx - 9)) / (R + 11))
        return rim(x) + 2 + 26 * u ** 1.7 + math.sin(x / 2.3) * (0.8 + u) + ((x // 4) % 2) * u

    def covered(x, y):
        if x > cx + R + 2 + (1.5 * math.sin(y / 3.0) if y > rim(x) else 0) + max(0, y - by + 4):
            return False
        if y < back(x) - 1 or y > min(hem(x), by + 1):
            return False
        return (x - cx) * 7 + (y - top) * 9 > -40                      # vora esquerra, en diagonal

    for y in range(top - 9, by + 3):
        for x in range(cx - 20, cx + R + 8):
            if not covered(x, y):
                continue
            nx = (x - cx) / R
            if y <= rim(x):
                lvl = 5.2 - nx * 0.5 + (math.sin((x - cx) / 5.0 + y * 0.3) * 0.4)
            else:
                d = (y - rim(x)) / 26
                fold = math.sin((x - cx) / 3.2 - d * 2.0)
                lvl = 4.0 - nx * 1.4 + fold * (0.5 + d * 1.2) - d * 0.8
                if abs(y - rim(x)) < 1.5:
                    lvl += 0.9                                         # el plec de la vora de la tapa
            if not covered(x, y + 1) or not covered(x, y + 2):
                lvl -= 1.4                                             # gruix del bord
            if not covered(x - 1, y) or not covered(x, y - 1):
                lvl += 0.6
            cv.put(x, y, CLOTH, lvl)
    cv.darken(cx - 12, top, cx + R + 6, by, lambda x, y: 0.7 if not covered(x, y) and covered(x, y - 2) and y > rim(x) else 0)
    # cable desendollat, serpentejant pel terra
    for i in range(40):
        t = i / 39
        x = round(cx - R + 2 - t * 34)
        y = round(by - 3 + t * 9 + math.sin(t * 7) * 2.5)
        cv.put(x, y, IRON, 2.4)
        cv.put(x, y + 1, IRON, 0.8)
    ex, ey = cx - R - 32, by + 6
    cv.rect(ex - 4, ey - 1, ex, ey + 1, IRON, lambda x, y: 4.0 - (y - ey + 1))     # la clavilla
    cv.put(ex - 5, ey - 1, COPPER, 5.0); cv.put(ex - 5, ey + 1, COPPER, 5.0)
    # el cartell, penjat d'un cordill
    kx0, ky0 = cx - 22, top + 12
    cv.darken(kx0 + 2, ky0 + 2, kx0 + 35, ky0 + 16, 0.7)
    cv.rect(kx0, ky0, kx0 + 33, ky0 + 14, PAPER, lambda x, y: 4.6 - (y - ky0) * 0.1 - (x - kx0) * 0.02)
    cv.hline(kx0, kx0 + 33, ky0 + 14, PAPER, 2.4)
    text(cv, kx0 + 3, ky0 + 2, 'APAGAT', RED, 3.4, 0)
    text(cv, kx0 + 3, ky0 + 8, 'PER SEMPRE', WALNUT, 1.4, 0, gap=0)
    for tx_, d in ((kx0 - 1, 1), (kx0 + 31, -1)):                          # cinta adhesiva als cantons
        for i in range(4):
            cv.put(tx_ + i * d + (1 if d < 0 else 0), ky0 - 1 + i, MANILA_T, 4.2, 0.4)
            cv.put(tx_ + i * d + 1 + (1 if d < 0 else 0) * -1, ky0 - 1 + i, MANILA_T, 3.6, 0.4)


# ─── El Cargol, conserge ───────────────────────────────────────────────────

def conserge(cv):
    # galleda i pal de fregar
    gx, gy = 410, 198
    cv.darken(gx - 9, gy - 2, gx + 11, gy + 3, lambda x, y: 0.9 - abs(x - gx - 1) / 11 - abs(y - gy) / 4)
    cv.poly([(gx - 7, gy - 13), (gx + 7, gy - 13), (gx + 5, gy), (gx - 5, gy)], WARN,
            lambda x, y: 3.6 - (x - gx) * 0.18 - (y - gy + 13) * 0.04)
    cv.hline(gx - 7, gx + 7, gy - 13, WARN, 5.0)
    cv.hline(gx - 6, gx + 6, gy - 12, IRON, 1.0)
    cv.line(gx - 7, gy - 13, gx, gy - 19, IRON, 3.0)
    cv.line(gx + 7, gy - 13, gx, gy - 19, IRON, 2.4)
    cv.line(gx + 3, gy - 12, gx + 16, gy - 62, WALNUT, 4.0)
    cv.line(gx + 4, gy - 12, gx + 17, gy - 62, WALNUT, 2.4)
    for i in range(-4, 5):
        cv.line(gx + 3, gy - 12, gx + 3 + i, gy - 4, CLOTH, 3.6 - abs(i) * 0.3)
    # el Cargol vell, de cara, amb una ombra de contacte
    spr = cargol('D', old=True)
    fx, fy = 27, 60
    cv.darken(CGX - 22, CGY - 2, CGX + 22, CGY + 4, lambda x, y: 0.9 - abs(x - CGX) / 24 - (y - CGY + 2) / 8)
    # el sprite té la llum pròpia; el tenyim una mica amb la calor del museu
    P = spr.load()
    for y in range(spr.height):
        for x in range(spr.width):
            p = P[x, y]
            if p[3]:
                P[x, y] = mix(p, (255, 200, 140), 0.12) + (p[3],)
    cv.img.alpha_composite(spr, (CGX - fx, CGY - fy))
    # una gorra de conserge, de visera, entre les antenes
    cx, cy = CGX - fx + 27, CGY - fy + 17
    cv.disc(cx, cy, 7, 3, [(18, 22, 40), (30, 36, 62), (46, 54, 90), (70, 80, 120)], lambda nx, ny: 2.4 - nx - ny * 0.6, 0.3)
    cv.hline(cx - 8, cx + 6, cy + 2, [(14, 14, 24)], 0, 0)
    cv.hline(cx - 9, cx + 4, cy + 3, [(24, 26, 40)], 0, 0)
    cv.put(cx, cy - 1, GOLD, 5.0, 0)


# ─── La Vet, d'esquena, davant la foto (ja sense la granota de presa) ───────

JACKET = M((22, 30, 30), (36, 52, 50), (54, 78, 70), (76, 106, 90), (104, 138, 112), (140, 172, 140), dith=0.0)


def vet(cv):
    spec = dict(VET, legs=DENIM, top=JACKET, forearm=JACKET)
    spec['hooks'] = {k: v for k, v in VET['hooks'].items() if k in ('hair_back', 'hair')}
    spr = person(spec, 'U')
    P = spr.load()
    for y in range(spr.height):
        for x in range(spr.width):
            p = P[x, y]
            if p[3]:
                P[x, y] = mix(p, (255, 200, 140), 0.10) + (p[3],)
    cv.darken(VTX - 16, VTY - 3, VTX + 18, VTY + 3, lambda x, y: 0.95 - abs(x - VTX - 1) / 18 - abs(y - VTY) / 5)
    cv.img.alpha_composite(spr, (VTX - 25, VTY - 83))
    # llum del focus de la foto al cabell
    for y in range(VTY - 83, VTY - 66):
        for x in range(VTX - 6, VTX + 9):
            o = cv.P[x, y]
            if o[0] > 150 and hr(x, y, 31) > 0.5:
                cv.P[x, y] = mix(o, (255, 236, 196), 0.35) + (255,)


def flors(cv, x0, y0):
    """Un pom de flors embolicat en paper, deixat al banc."""
    cv.poly([(x0, y0), (x0 + 16, y0 - 4), (x0 + 18, y0 - 1), (x0 + 2, y0 + 3)], PAPER, lambda x, y: 4.6 - (y - y0) * 0.4)
    for i in range(6):
        cv.line(x0 + 14, y0 - 2, x0 + 22 + (i % 3), y0 - 4 - i // 2, LEAF, 2.6)
    for i, (dx, dy, c) in enumerate(((18, -6, RED), (21, -3, WARN), (23, -7, RED), (20, -9, PAPER), (25, -4, RED), (17, -3, WARN))):
        cv.disc(x0 + dx + 4, y0 + dy, 1.6, 1.4, c, lambda nx, ny: 4.6 - nx - ny, 0.4)
    cv.darken(x0 + 1, y0 + 3, x0 + 26, y0 + 4, 0.6)


# ─── Fons ──────────────────────────────────────────────────────────────────

def bg(cv, mira=False, cargol=False, t=0.0):
    wall(cv)
    floor(cv)

    # rètol nou del sostre, de fusta i llautó
    title = 'MUSEU DE LA MEMORIA'
    tw = text_w(title)
    tx = 220 - tw // 2
    cv.darken(tx - 6, 24, tx + tw + 8, 25, 0.6)
    cv.rect(tx - 7, 14, tx + tw + 6, 23, WALNUT, lambda x, y: 2.6 - (y - 14) * 0.1, 0.3)
    cv.hline(tx - 7, tx + tw + 6, 14, WALNUT, 4.6, 0.3)
    cv.hline(tx - 7, tx + tw + 6, 23, WALNUT, 1.0, 0.3)
    text(cv, tx, 16, title, GOLD, 5.0, 0)
    cv.put(tx + text_w('MUSEU DE LA MEM') + 1, 15, GOLD, 5.0, 0)            # l'accent de MEMÒRIA
    cv.put(tx + text_w('MUSEU DE LA MEM') + 2, 14, GOLD, 4.0, 0)

    # carril i focus
    cv.hline(70, 420, 11, IRON, 3.0)
    cv.hline(70, 420, 12, IRON, 1.4)
    for sx, sy in SPOTS.values():
        spot(cv, sx, sy)

    # porta (la mateixa d'abans, però oberta de bat a bat: ara s'hi entra i se'n surt)
    DX0, DX1, DT = 12, 61, 60
    cv.rect(DX0 - 4, DT - 4, DX1 + 4, 153, CREAM, lambda x, y: 4.8 if x < DX0 - 2 or y < DT - 2 else (1.8 if x > DX1 + 1 else 3.0))
    for y in range(DT, 154):
        for x in range(DX0, DX1 + 1):
            # passadís il·luminat al fons
            lvl = 4.4 - abs(x - 36) / 30 - (y - DT) / 120
            if y > 136:
                lvl = 3.0 - (y - 136) / 16
            cv.put(x, y, CREAM, lvl, 0.4)
    for x in (DX0, DX0 + 1, DX0 + 2, DX0 + 3):                              # fulles plegades contra el marc
        cv.vline(x, DT, 153, STEEL, 3.4 - (x - DX0) * 0.6)
    for x in (DX1 - 3, DX1 - 2, DX1 - 1, DX1):
        cv.vline(x, DT, 153, STEEL, 2.0 + (x - DX1 + 3) * 0.3)
    cv.glow(36, 110, 40, (255, 236, 200), 0.25)
    cv.rect(24, 48, 50, 55, PILOT, 1.5, 0)
    text(cv, 25, 49, 'SORTIDA', PILOT, 3.5, 0, gap=0)
    cv.glow(37, 52, 16, (90, 255, 140), 0.25)

    foto(cv, mira)
    llibreta(cv)
    fabrica(cv)
    vitrina(cv)
    expositor(cv)

    # banc de fusta per seure davant la foto
    BX0, BX1, BY = 150, 300, 188
    cv.darken(BX0 - 4, BY + 14, BX1 + 6, BY + 19, lambda x, y: 0.8 - (y - BY - 14) / 6)
    for lx in (BX0 + 8, BX1 - 10):
        cv.rect(lx, BY + 4, lx + 3, BY + 16, WALNUT, lambda x, y: 3.0 - (x - lx) * 0.5)
    cv.rect(BX0, BY - 3, BX1, BY, WALNUT, lambda x, y: 5.0 - (y - BY + 3) * 0.3 + (hr(x // 9, y, 3) - 0.5) * 0.4)
    cv.rect(BX0, BY + 1, BX1, BY + 4, WALNUT, lambda x, y: 2.8 - (y - BY - 1) * 0.4)
    cv.hline(BX0 + 4, BX1 - 4, BY + 10, WALNUT, 1.6)

    cv.darken(0, FLOOR_Y, W - 1, FLOOR_Y + 3, lambda x, y: 0.5 - (y - FLOOR_Y) * 0.14)
    reflect(cv, FLOOR_Y, BY - 4)

    flors(cv, BX0 + 12, BY - 4)
    socol_apagat(cv)
    if cargol:
        conserge(cv)
    vet(cv)

    # ─── Gradació final: calidesa de focus, i pols daurada als cons ─────────
    # (amb t, la llum dels focus respira i la pols sura; t = 0 és el fons quiet)
    TGT = ((130, 64), (219, 62), (310, 64), (382, 98))
    for k, ((sx, sy), (tx_, ty_)) in enumerate(zip(SPOTS.values(), TGT)):
        breath = 1 + 0.35 * math.sin(2 * math.pi * (t * (1 + k % 2) + k * 0.27))
        for y in range(sy + 8, ty_ + 30):
            u = (y - sy) / (ty_ + 30 - sy)
            half = 3 + u * 30
            mx = sx + (tx_ - sx) * u
            for x in range(int(mx - half), int(mx + half) + 1):
                a = 0.10 * breath * (1 - abs(x - mx) / half) * (1 - u * 0.7)
                if 0 <= x < W and a > B4[y & 3][x & 3] * 0.25:
                    cv.P[x, y] = mix(cv.P[x, y], (255, 232, 190), a) + (255,)
    for i in range(70):                                                      # motes de pols als feixos
        k = int(hr(i, 1) * 4)
        (sx, sy), (tx_, ty_) = list(SPOTS.values())[k], TGT[k]
        u = 0.15 + hr(i, 2) * 0.8
        ph = hr(i, 4)
        sp = 1 + int(hr(i, 5) * 2)                                           # cicles per bucle: 1 o 2
        x = round(sx + (tx_ - sx) * u + (hr(i, 3) - 0.5) * 40 * u + 2.5 * math.sin(2 * math.pi * (sp * t + ph)))
        y = round(sy + (ty_ - sy) * u + 2.0 * math.sin(2 * math.pi * (t + ph * 1.7)) + 1.5 * math.cos(2 * math.pi * (sp * t + ph)))
        a = 0.35 + 0.35 * (0.5 + 0.5 * math.sin(2 * math.pi * (2 * t + ph * 3)))  # parpelleja quan travessa la llum
        if 0 <= x < W and 0 <= y < H:
            cv.P[x, y] = mix(cv.P[x, y], (255, 240, 200), a) + (255,)
    # un reflex que passa pel vidre de la vitrina (fora del vidre a t = 0)
    g = (t * 1.0) * 2.2 - 0.6
    if 0 < g < 1:
        gx = 356 + g * 51
        for y in range(90, 120):
            for x in range(356, 408):
                d = abs((x - gx) + (y - 105) * 0.6)
                if d < 2.5:
                    cv.P[x, y] = mix(cv.P[x, y], (255, 250, 236), 0.35 * (1 - d / 2.5)) + (255,)
    cv.tint(0, 0, W - 1, H - 1, (255, 196, 128), 0.07)
    # vinyeta suau per tancar el pla
    for y in range(H):
        for x in range(W):
            d = math.hypot((x - 240) / 300, (y - 120) / 190)
            k = max(0.0, d - 0.62) * 1.1
            if k > 0:
                o = cv.P[x, y]
                f = max(0.0, 1 - k)
                cv.P[x, y] = (int(o[0] * f), int(o[1] * f), int(o[2] * f), 255)


_CACHE = {}


def _diferencia(cv, **amb):
    """Només els píxels que canvien respecte del fons sense res: la Mira a la foto, o en Cargol."""
    clau = tuple(sorted(amb))
    if clau not in _CACHE:
        on, off = Canvas(light=LIGHT), Canvas(light=LIGHT)
        bg(on, **amb)
        bg(off)
        _CACHE[clau] = (on, off)
    on, off = _CACHE[clau]
    for y in range(H):
        for x in range(W):
            p = on.P[x, y]
            if p != off.P[x, y]:
                cv.P[x, y] = p


def foto_mira(cv):
    _diferencia(cv, mira=True)


def conserge_cargol(cv):
    _diferencia(cv, cargol=True)


PROPS = {'foto_mira': foto_mira, 'conserge_cargol': conserge_cargol}


# ─── Animació de fons ──────────────────────────────────────────────────────
# La llum dels focus respira, la pols sura i parpelleja dins els cons i un reflex passa pel vidre de la
# vitrina. Cada fotograma només té els píxels que canvien respecte del fons quiet (t = 0), i mai no toca
# els píxels que pinten els props (la Mira a la foto, en Cargol), perquè es pinta per damunt.

def _ambient_frames(n=16):
    base = Canvas(light=LIGHT)
    bg(base)
    blocked = set()
    for amb in ({'mira': True}, {'cargol': True}):
        on = Canvas(light=LIGHT)
        bg(on, **amb)
        for y in range(H):
            for x in range(W):
                if on.P[x, y] != base.P[x, y]:
                    for dx in (-1, 0, 1):
                        for dy in (-1, 0, 1):
                            blocked.add((x + dx, y + dy))
    frames = []
    for i in range(n):
        cv = Canvas(light=LIGHT)
        bg(cv, t=i / n)
        fr = Canvas(light=LIGHT, transparent=True)
        for y in range(H):
            for x in range(W):
                p = cv.P[x, y]
                if p != base.P[x, y] and (x, y) not in blocked:
                    fr.P[x, y] = p
        frames.append(fr.img)
    return frames


ANIMS = {'ambient': {'frames': _ambient_frames, 'frameDuration': 110}}
