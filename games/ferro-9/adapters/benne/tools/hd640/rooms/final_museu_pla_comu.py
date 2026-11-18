"""
**El dibuix pla de sempre** (font de les textures de la sala en 3D, final_museu.py).

Final «La fugida»: la Sala de la Memòria, uns mesos després, convertida en un museu de veritat. Llum càlida de
focus, la llibreta de torn exposada, la clau anglesa a la vitrina, la foto del torn de nit restaurada (la cara de
l'Iri sencera i un cartellet «DESAPAREGUDA» a sota) i el sòcol de l'holograma apagat, tapat amb un drap.
Fa de conserge el Cargol vell, rovellat, al costat de la porta.

`bg(cv, mira=True)`: la Mira d'Orís, a la foto; sense, al seu lloc hi ha un buit net. Al joc, la Mira és el
prop `foto_mira` (només si l'Iri la va salvar), i en Cargol conserge, el prop `conserge_cargol` (només si li
van reparar la memòria).

A 640×360 (hd/rooms/final_museu.py redibuixat a ×4/3): la mateixa composició, amb els rètols en la lletra de 4×7
(MUSEU DE LA MEMÒRIA ja porta l'accent de la lletra), més gent i més detall a la foto, la llibreta escrita amb més
línies, la fàbrica de la foto gran amb finestres i rellotge, plafons cargolats, fusta amb veta i un drap amb trama.
La Vet i en Cargol són els de 640. El fons quiet (sense la gradació dels focus) es fa un cop per combinació de
props; els fotogrames només hi tornen a passar la llum que respira, la pols i el reflex.
"""
import math
from functools import lru_cache

import numpy as np
from PIL import Image

import hd640  # noqa: F401  (posa la llibreria de dibuix a 640×360)
from hd.pix import Canvas, B4, W, H, ramp, mix, STEEL, IRON, PAPER, GOLD, WALNUT, RED, WARN, COPPER
from hd640.rooms.gavina_passadis_pla_comu import PILOT, text, text_w, hr, CachedLight
from hd640.rooms.fabrica_cambra_pla_comu import FE9
from hd640.draw_characters import cargol, person, VET, DENIM, M
try:
    from hd640.rooms.gavina_memoria_pla_comu import SEPIA, FRAME, VELVET, spot_cone
except ImportError:                                   # (paletes de 480; spot_cone rep coordenades en píxels)
    from hd.rooms.gavina_memoria import SEPIA, FRAME, VELVET, spot_cone

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
CAP = [(18, 22, 40), (30, 36, 62), (46, 54, 90), (70, 80, 120)]                            # la gorra del conserge
SPOT = (255, 226, 176)

FLOOR_Y = 205
SPOTS = {'foto': (173, 16), 'llibreta': (221, 16), 'fabrica': (413, 16), 'vitrina': (509, 16)}
TGT = ((173, 85), (292, 83), (413, 85), (509, 131))       # on apunta cada focus
PEDX, PEDY = 461, 317                     # sòcol apagat, en primer terme
CGX, CGY = 595, 269                       # peus del Cargol
VTX, VTY = 128, 285                       # peus de la Vet
BX0, BX1, BY = 200, 400, 251              # el banc


def warm_pool(x, y):
    """Bassals de llum al terra sota els focus i al primer terme."""
    if y < FLOOR_Y:
        return 0.0
    v = 0.9 * max(0.0, 1 - math.hypot((x - 320) / 307, (y - 229) / 45))
    v += 1.2 * max(0.0, 1 - math.hypot((x - 133) / 147, (y - 280) / 53)) ** 1.2
    v += 1.5 * max(0.0, 1 - math.hypot((x - 507) / 147, (y - 296) / 59)) ** 1.2
    return v


LIGHT = CachedLight(ambient=0.15, vignette=(75, 35), floor_fade=(285, 93))
LIGHT.add(spot_cone(*SPOTS['foto'], *TGT[0], 93, 2.6))
LIGHT.add(spot_cone(*SPOTS['llibreta'], *TGT[1], 85, 2.2))
LIGHT.add(spot_cone(*SPOTS['fabrica'], *TGT[2], 69, 2.0))
LIGHT.add(spot_cone(*SPOTS['vitrina'], *TGT[3], 75, 2.3))
LIGHT.add(warm_pool)


# ─── Paret i terra ──────────────────────────────────────────────────────────

PW = 64                                   # amplada dels plafons


def wall(cv):
    for y in range(0, FLOOR_Y):
        for x in range(W):
            px = (x - 5) % PW
            pid = (x - 5) // PW
            lvl = 3.0 + (hr(pid, 2) - 0.5) * 0.15 + (hr(x // 3, pid, 7) - 0.5) * 0.06
            if y < 13:                                                      # sostre, amb una motllura
                lvl = 1.2 + (0.8 if y in (9, 10) else 0) + (0.4 if y == 11 else 0)
            elif y == 13:
                lvl = 4.0
            elif y == 14:
                lvl = 2.6
            elif y < 17:
                lvl = 1.0
            elif y < 149:
                if px == 0:
                    lvl = 1.6
                elif px == 1:
                    lvl += 0.6
                elif px == 2:
                    lvl += 0.25
                elif px == PW - 1:
                    lvl -= 0.5
                elif px == PW - 2:
                    lvl -= 0.2
                lvl -= max(0.0, 1 - (y - 17) / 21) * 1.2
            elif y < 154:
                lvl = 2.0                                                   # (el passamà de fusta, més avall)
            elif y < 195:
                lvl = 2.8 + (0.2 if px < 3 else 0) - (1.0 if y == 154 else 0) - (0.5 if y == 155 else 0)
                if px == 0:
                    lvl = 1.6
            else:
                lvl = 1.0
            cv.put(x, y, CREAM, lvl)
    # cargols de llautó a les cantonades dels plafons
    for x0 in range(5 - PW, W, PW):
        for xx in (x0 + 6, x0 + PW - 7):
            for yy in (25, 140):
                if 0 <= xx < W - 1:
                    cv.put(xx, yy, GOLD, 4.6, 0.4)
                    cv.put(xx + 1, yy, GOLD, 3.4, 0.4)
                    cv.put(xx, yy + 1, GOLD, 2.8, 0.4)
                    cv.put(xx + 1, yy + 1, CREAM, 1.8)
    # el passamà, de fusta encerada (amb veta)
    for y in range(149, 154):
        for x in range(W):
            cv.put(x, y, WALNUT, [5.4, 4.8, 4.0, 3.0, 1.4][y - 149] + (hr(x // 9, y, 5) - 0.5) * 0.3)
    # sòcol de fusta fosca
    for y in range(195, FLOOR_Y):
        for x in range(W):
            cv.put(x, y, WALNUT, [4.4, 3.2, 2.6, 2.2, 2.0, 1.8, 1.6, 1.4, 1.2, 0.6][y - 195] +
                   (hr(x // 7, y // 2, 6) - 0.5) * 0.3)


def floor(cv):
    vx, vy, S, K = 320, 40, 1.7, 933.3
    for y in range(FLOOR_Y, H):
        d = y - vy
        v = K / d
        vi = math.floor(v)
        fv = (vi + 1 - v) * d * d / K
        fv2 = (v - vi) * d * d / K
        for x in range(W):
            u = (x - vx) / d * S
            ui = math.floor(u)
            fu = (u - ui) * d / S
            fu2 = (ui + 1 - u) * d / S
            lvl = 3.0 + (hr(ui, vi, 7) - 0.5) * 0.25 + (hr(x // 5, y // 2, 9) - 0.5) * 0.1
            if fu < 1 or fv < 1:
                lvl = 1.8                                                   # junta
            elif fu2 < 1 or fv2 < 1:
                lvl -= 0.3
            elif fu < 2 or fv < 2:
                lvl += 0.25                                                 # cantell encerat
            if y < 213:
                lvl -= (213 - y) / 8 * 0.9
            cv.put(x, y, WAX, lvl)


def reflect(cv, y0=FLOOR_Y, y1=H - 1, k=0.22, depth=80):
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
    """Marc de 5 píxels amb bisell, i ombra a la paret."""
    if shadow:
        cv.darken(x0 + 3, y0 + 3, x1 + 4, y1 + 4, 0.7)
    for y in range(y0, y1 + 1):
        for x in range(x0, x1 + 1):
            dd = min(x - x0, x1 - x, y - y0, y1 - y)
            if dd > 4:
                continue
            lvl = [2.0, 4.8, 4.0, 3.0, 2.2][dd]
            if (x1 - x) < 5 or (y1 - y) < 5:
                lvl -= 0.8
            if dd == 2 and (x + y) % 5 == 0:
                lvl += 0.5                                                  # el filet daurat, picat
            cv.put(x, y, rp, lvl)


def spot(cv, sx, sy):
    cv.rect(sx - 3, 14, sx + 3, 18, IRON, lambda x, y: 3.4 - (x - sx) * 0.2)
    cv.poly([(sx - 7, 19), (sx + 4, 17), (sx + 7, 25), (sx - 4, 28)], IRON, lambda x, y: 3.6 - (x - sx) * 0.19)
    cv.put(sx, 19, IRON, 5.4)                                              # el cargol de l'articulació
    cv.line(sx - 6, 20, sx + 3, 18, IRON, 4.6)                             # cantell il·luminat
    cv.line(sx - 4, 28, sx + 7, 25, [SPOT], 0, 0)
    cv.line(sx - 4, 27, sx + 6, 24, [(236, 206, 160)], 0, 0)
    cv.glow(sx + 1, 28, 16, (255, 230, 180), 0.7)


# ─── La foto del torn de nit, restaurada ───────────────────────────────────

FX0, FY0, FX1, FY1 = 123, 49, 223, 123
PX0, PY0, PX1, PY1 = FX0 + 5, FY0 + 5, FX1 - 5, FY1 - 5
IRI_X = 152


def foto(cv, mira):
    frame(cv, FX0, FY0, FX1, FY1)
    for y in range(PY0, PY1 + 1):
        for x in range(PX0, PX1 + 1):
            lvl = 2.6 + (y - PY0) / 53 + (hr(x // 4, y // 4, 3) - 0.5) * 0.2 + (hr(x, y, 8) - 0.5) * 0.12
            if (x - PX0) % 16 == 0 and y < PY0 + 35:
                lvl -= 0.6
            if y < PY0 + 5:
                lvl -= 0.6
            fd = math.hypot(x - 203, y - 75)
            if fd < 12:
                lvl += (1 - fd / 12) * 2.8
            cv.put(x, y, SEPIA, lvl, 0.3)
    people = [(139, 37, True), (IRI_X, 36, False), (164, 31, False), (177, 39, True), (191, 36, True)]
    for k, (px, h, cap) in enumerate(people):
        if k == 2 and not mira:
            continue
        top = PY1 - h
        for y in range(top + 9, PY1 + 1):
            half = 4 + (1 if y > top + 12 else 0)
            for x in range(px - half, px + half + 1):
                lvl = 1.4 - (x - px) * 0.075 + (0.6 if x == px - half else 0) + (0.4 if y == top + 9 else 0)
                if abs(x - px) == half - 1 and y > top + 13:
                    lvl -= 0.3                                              # els braços
                cv.put(x, y, SEPIA, lvl, 0.3)
        cv.rect(px - 1, top + 7, px + 1, top + 9, SEPIA, 3.6, 0.3)
        cv.disc(px, top + 4, 3.3, 4, SEPIA, lambda nx, ny: 4.8 - nx * 0.8 - ny * 0.4, 0.3)
        if cap:
            cv.rect(px - 4, top - 1, px + 3, top + 1, SEPIA, 1.2, 0.3)
            cv.hline(px - 5, px + 1, top + 2, SEPIA, 0.8, 0.3)               # la visera
        else:
            cv.rect(px - 3, top - 1, px + 3, top + 1, SEPIA, 0.8, 0.3)
            cv.vline(px - 4, top + 1, top + 6, SEPIA, 0.8, 0.3)
        # ulls: ara totes les cares hi són
        cv.put(px - 1, top + 4, SEPIA, 2.2, 0.3)
        cv.put(px + 1, top + 4, SEPIA, 2.2, 0.3)
        cv.put(px, top + 6, SEPIA, 3.6, 0.3)
    # l'Iri: l'abric clar obert, la trena i un mig somriure
    itop = PY1 - 36
    for y in range(itop + 9, PY1 + 1):
        half = 4 + (1 if y > itop + 12 else 0)
        for x in range(IRI_X - half, IRI_X + half + 1):
            lvl = 3.6 - (x - IRI_X) * 0.11 + (0.6 if x == IRI_X - half else 0)
            if y > itop + 11 and x == IRI_X:
                lvl = 1.2                                                   # l'abric obert
            elif y > itop + 11 and x == IRI_X + 1:
                lvl = 2.2
            cv.put(x, y, SEPIA, lvl, 0.3)
    cv.vline(IRI_X - 4, itop + 1, itop + 7, SEPIA, 0.8, 0.3)
    for y in range(itop + 8, itop + 20):                                     # la trena, per sobre l'espatlla
        cv.put(IRI_X - 3 - (y > itop + 11), y, SEPIA, 0.6 + (y % 2) * 0.8, 0.3)
    cv.put(IRI_X - 1, itop + 6, SEPIA, 2.6, 0.3)
    cv.put(IRI_X, itop + 6, SEPIA, 2.6, 0.3)
    cv.put(IRI_X + 1, itop + 5, SEPIA, 2.6, 0.3)
    if mira:
        mx, mtop = 164, PY1 - 31
        cv.vline(mx + 4, mtop + 2, mtop + 11, SEPIA, 0.8, 0.3)
        cv.hline(mx - 1, mx + 1, mtop + 6, SEPIA, 2.0, 0.3)
    # el Cargol, nou de trinca
    cv.rect(204, PY1 - 29, 213, PY1 - 13, SEPIA, lambda x, y: 5.0 - (x - 204) * 0.22, 0.3)
    cv.rect(205, PY1 - 36, 212, PY1 - 31, SEPIA, 5.4, 0.3)
    cv.put(207, PY1 - 34, SEPIA, 0.6, 0.3)
    cv.put(210, PY1 - 34, SEPIA, 0.6, 0.3)
    cv.hline(207, 210, PY1 - 32, SEPIA, 3.6, 0.3)                          # la reixa de la boca
    cv.vline(208, PY1 - 40, PY1 - 37, SEPIA, 4.0, 0.3)
    cv.put(208, PY1 - 41, SEPIA, 6.0, 0.3)
    cv.rect(205, PY1 - 12, 207, PY1, SEPIA, 3.6, 0.3)
    cv.rect(210, PY1 - 12, 212, PY1, SEPIA, 3.6, 0.3)
    cv.put(208, PY1 - 24, SEPIA, 6.4, 0.3)
    cv.put(209, PY1 - 24, SEPIA, 5.6, 0.3)
    cv.darken(PX0, PY0, PX1, PY1, lambda x, y: max(0.0, 0.5 - min(x - PX0, PX1 - x, y - PY0, PY1 - y) / 9), dither=False)
    # vidre nou del marc: un reflex
    for i in range(13):
        if hr(i, 9) > 0.3:
            cv.put(PX0 + 53 + i, PY0 + 13 - i, [(255, 244, 220)], 0, 0)
    for i in range(6):
        cv.put(PX0 + 58 + i, PY0 + 16 - i, [(236, 224, 204)], 0, 0)

    # cartellet nou, sota l'Iri: «DESAPAREGUDA»
    s = 'DESAPAREGUDA'
    tw = text_w(s)
    cx0 = IRI_X - 11
    cx1 = cx0 + tw + 7
    cy0 = FY1 + 8
    cv.darken(cx0 + 3, cy0 + 3, cx1 + 3, cy0 + 15, 0.7)
    cv.rect(cx0, cy0, cx1, cy0 + 12, PAPER, lambda x, y: 4.8 - (y - cy0) * 0.06)
    cv.hline(cx0, cx1, cy0, PAPER, 5.8)
    cv.vline(cx1, cy0, cy0 + 12, PAPER, 3.0)
    cv.hline(cx0, cx1, cy0 + 12, PAPER, 2.6)
    text(cv, cx0 + 4, cy0 + 3, s, WALNUT, 1.0, 0)
    cv.put(IRI_X, cy0 - 2, PAPER, 5.8)                                          # la puntera, cap a l'Iri
    cv.hline(IRI_X - 1, IRI_X + 1, cy0 - 1, PAPER, 5.8)


# ─── La llibreta de torn, oberta en una vitrina de paret ───────────────────

def llibreta(cv):
    X0, Y0, X1, Y1 = 237, 44, 347, 123
    frame(cv, X0, Y0, X1, Y1, WALNUT)
    # fons de vellut
    for y in range(Y0 + 5, Y1 - 4):
        for x in range(X0 + 5, X1 - 4):
            cv.put(x, y, VELVET, 1.8 + (hr(x // 2, y // 2, 4) - 0.5) * 0.3 - (0.8 if y < Y0 + 9 else 0) -
                   (0.4 if x < X0 + 8 else 0), 0.5)
    # la llibreta: tapes de cuiro i dues pàgines
    cx = (X0 + X1) // 2
    PT, PB, PWD = 59, 107, 41
    cv.rect(cx - PWD - 3, PT - 3, cx + PWD + 3, PB + 3, COPPER, lambda x, y: 1.6 - (y - PT) / 80, 0.6)
    cv.hline(cx - PWD - 3, cx + PWD + 3, PB + 3, COPPER, 0.6, 0.3)
    for side in (-1, 1):
        for y in range(PT, PB + 1):
            for x in range(cx + (1 if side > 0 else -PWD), cx + (PWD if side > 0 else -1) + 1):
                u = abs(x - cx) / PWD
                lvl = 4.4 - (0.9 if u < 0.12 else 0) - (0.4 if u < 0.25 else 0) + (hr(x // 4, y, 8) - 0.5) * 0.2
                if y in (PT, PB):
                    lvl -= 0.5
                if u > 0.97 and y % 2:
                    lvl -= 0.6                                              # el gruix de les pàgines
                cv.put(x, y, PAPER, lvl, 0.6)
    cv.vline(cx, PT - 1, PB + 1, COPPER, 0.6, 0.3)
    # escriptura a mà (llapis), una mica tremolosa, amb alguna lletra alta
    for y in range(PT + 5, PB - 3, 4):
        x = cx - 37
        while x < cx - 5:
            n = 2 + int(hr(x, y, 1) * 6)
            for i in range(n):
                if x + i < cx - 5:
                    cv.put(x + i, y + (1 if hr(x + i, y, 2) > 0.8 else 0), WALNUT, 1.6 + hr(x + i, y) * 0.6, 0.3)
                    if hr(x + i, y, 5) > 0.88:
                        cv.put(x + i, y - 1, WALNUT, 2.0, 0.3)
            x += n + 2
    # pàgina dreta: l'esbós de la cambra (tres bobines) amb una fletxa, i unes línies
    bx, by = cx + 8, PT + 5
    for x in range(bx, bx + 20):
        cv.put(x, by, WALNUT, 1.8, 0.3)
        cv.put(x, by + 24, WALNUT, 1.8, 0.3)
    for y in range(by, by + 25):
        cv.put(bx, y, WALNUT, 1.8, 0.3)
        cv.put(bx + 19, y, WALNUT, 1.8, 0.3)
    for k in range(3):
        for y in range(by + 4, by + 21):
            if y % 2:
                cv.hline(bx + 4 + k * 5, bx + 5 + k * 5, y, COPPER, 2.4, 0.3)
    for i in range(8):
        cv.put(bx + 24 + i, by + 8 - (i % 2), WALNUT, 1.8, 0.3)                 # «una fletxa»
    cv.put(bx + 30, by + 5, WALNUT, 1.8, 0.3)
    cv.put(bx + 30, by + 9, WALNUT, 1.8, 0.3)
    for y in range(by + 29, PB - 3, 4):
        x = cx + 5
        while x < cx + 37:
            n = 2 + int(hr(x, y, 3) * 6)
            for i in range(n):
                if x + i < cx + 37:
                    cv.put(x + i, y, WALNUT, 1.6 + hr(x + i, y) * 0.6, 0.3)
            x += n + 2
    # vidre amb reflex
    for i in range(21):
        cv.put(X0 + 11 + i, Y0 + 29 - i, [(255, 246, 226)], 0, 0)
        if i < 12:
            cv.put(X0 + 17 + i, Y0 + 32 - i, [(236, 220, 196)], 0, 0)
    # títol a la paret, a sota
    s = 'LLIBRETA DE TORN'
    tx = cx - text_w(s) // 2
    text(cv, tx, Y1 + 8, s, WALNUT, 1.2, 0)
    cv.hline(tx, tx + text_w(s) - 1, Y1 + 17, GOLD, 3.2, 0.4)


# ─── La fàbrica Aldaia: fotografia gran on abans hi havia l'holograma ──────

def fabrica(cv):
    X0, Y0, X1, Y1 = 371, 53, 456, 123
    frame(cv, X0, Y0, X1, Y1)
    for y in range(Y0 + 5, Y1 - 4):
        for x in range(X0 + 5, X1 - 4):
            lvl = 2.2 + (y - Y0) / 40 + (hr(x // 3, y // 3, 13) - 0.5) * 0.25 + (hr(x, y, 14) - 0.5) * 0.12
            cv.put(x, y, SEPIA, lvl, 0.3)
    # la nau, la casa del rellotge i les xemeneies (el mateix pla del pròleg)
    base = 105
    cv.rect(X0 + 7, 84, 419, base, SEPIA, 1.2, 0.3)
    cv.poly([(X0 + 7, 84), (419, 84), (412, 77), (X0 + 12, 77)], SEPIA, 0.8, 0.3)
    cv.hline(X0 + 12, 412, 77, SEPIA, 1.8, 0.3)
    cv.poly([(416, base), (416, 83), (432, 72), (449, 83), (449, base)], SEPIA, 1.5, 0.3)
    cv.line(416, 83, 432, 72, SEPIA, 2.6, 0.3)
    cv.disc(432.5, 81, 2.7, 2.7, SEPIA, 4.6, 0.3)                           # el rellotge
    cv.put(432, 80, SEPIA, 1.6, 0.3)
    cv.put(433, 81, SEPIA, 1.6, 0.3)
    for x0, top in ((X0 + 12, 65), (407, 68), (444, 63)):
        cv.rect(x0, top, x0 + 3, 84, SEPIA, 1.0, 0.3)
        cv.hline(x0 - 1, x0 + 4, top, SEPIA, 1.8, 0.3)
        for i in range(11):                                                 # fum
            cv.put(x0 + 1 + i, top - 3 - i // 2 - (i % 2), SEPIA, 3.6 + hr(i, x0) * 0.6, 0.3)
            cv.put(x0 + 2 + i, top - 4 - i // 2, SEPIA, 3.2, 0.3)
    for x in range(X0 + 11, 416, 5):                                       # finestres enceses
        cv.rect(x, 89, x + 1, 93, SEPIA, 5.0, 0.3)
        cv.put(x, 91, SEPIA, 4.0, 0.3)
    for x in (421, 426, 439, 444):
        cv.rect(x, 88, x + 1, 92, SEPIA, 5.0, 0.3)
    cv.rect(430, 96, 434, base, SEPIA, 6.0, 0.3)                          # la porta oberta
    # el riu, amb el reflex de les finestres
    for y in range(base + 1, Y1 - 4):
        for x in range(X0 + 5, X1 - 4):
            lvl = 1.4
            if (x - X0 - 11) % 5 == 0 and x < 416 and hr(x, y, 4) > 0.45:
                lvl = 4.0 - (y - base) * 0.12
            elif (x + y * 3) % 7 == 0 and hr(x, y, 4) > 0.6:
                lvl = 2.6
            cv.put(x, y, SEPIA, lvl, 0.3)
    cv.darken(X0 + 5, Y0 + 5, X1 - 5, Y1 - 5,
              lambda x, y: max(0.0, 0.5 - min(x - X0 - 5, X1 - 5 - x, y - Y0 - 5, Y1 - 5 - y) / 8), dither=False)
    s = 'ALDAIA · FERRO-9'
    text(cv, (X0 + X1) // 2 - text_w(s) // 2, Y1 + 8, s, WALNUT, 1.2, 0)


# ─── Vitrina: la clau anglesa del Lot 1, que no s'ha rovellat mai ──────────

def vitrina(cv):
    VX0, VX1, GT = 475, 543, 119
    cv.rect(VX0 + 3, 161, VX1 - 3, 204, CREAM,
            lambda x, y: 4.6 - (x - VX0) / 53 - (2.4 if y > 199 else 0) + (0.8 if x == VX0 + 3 else 0) -
            (0.8 if y == 161 else 0))
    cv.hline(VX0 + 2, VX1 - 2, 160, CREAM, 5.6)
    cv.vline(VX1 - 3, 161, 204, CREAM, 2.4)
    # la placa de llautó
    cv.rect(491, 171, 527, 182, GOLD, lambda x, y: 3.6 - (y - 171) * 0.11, 0.3)
    cv.hline(491, 527, 171, GOLD, 4.6, 0.3)
    cv.hline(491, 527, 182, GOLD, 2.2, 0.3)
    for sx in (493, 525):
        cv.put(sx, 176, GOLD, 5.4, 0)
        cv.put(sx, 177, GOLD, 2.4, 0)
    s = 'LOT 1'
    text(cv, 509 - text_w(s) // 2, 173, s, WALNUT, 1.0, 0)
    for y in range(GT, 160):
        for x in range(VX0, VX1 + 1):
            cv.put(x, y, CREAM, 2.8 + (y - GT) / 80, 0.6)
    cv.rect(VX0 + 3, 144, VX1 - 3, 159, VELVET, lambda x, y: 3.4 - (y - 144) * 0.09)
    cv.hline(VX0 + 3, VX1 - 3, 144, VELVET, 4.6)
    cv.darken(484, 153, 531, 155, 0.8)                                      # ombra de la clau
    # la clau: mànec de ferro-9 polit i dues boques
    for x in range(488, 522):
        for dy, lv in enumerate((6.4, 5.4, 4.2, 2.8)):
            cv.put(x, 149 + dy, FE9, lv, 0)
    cv.disc(485, 151, 4.5, 3.7, FE9, lambda nx, ny: 5.4 - nx * 1.2 - ny * 1.6, 0)
    cv.disc(523, 151, 4.8, 4.0, FE9, lambda nx, ny: 5.4 - nx * 1.2 - ny * 1.6, 0)
    cv.rect(481, 149, 484, 152, VELVET, 3.4)
    cv.rect(525, 149, 529, 152, VELVET, 3.4)
    for x in range(496, 513, 3):
        cv.put(x, 150, FE9, 3.6, 0)                                       # el segell gravat
        cv.put(x + 1, 151, FE9, 6.0, 0)
    cv.glow(504, 149, 24, (220, 236, 255), 0.35)
    cv.poly([(488, 156), (504, 156), (503, 159), (489, 159)], PAPER, 4.4)
    cv.hline(491, 499, 157, PAPER, 3.0, 0)                                 # (la fitxa, escrita a mà)
    # la tapa i els muntants de fusta, i el vidre
    cv.rect(VX0 - 1, GT - 4, VX1 + 1, GT - 1, WALNUT, lambda x, y: 5.0 - (y - GT + 4) * 0.8)
    cv.hline(VX0 + 3, VX1 - 3, GT, [(255, 240, 210)], 0, 0)
    cv.vline(VX0, GT, 159, WALNUT, 5.0)
    cv.vline(VX0 + 1, GT, 159, WALNUT, 3.4)
    cv.vline(VX1 - 1, GT, 159, WALNUT, 3.4)
    cv.vline(VX1, GT, 159, WALNUT, 2.4)
    for i in range(19):
        cv.put(VX0 + 8 + i, 133 - i, [(255, 248, 230)], 0, 0)
        if i % 3:
            cv.put(VX0 + 12 + i, 139 - i, [(230, 216, 196)], 0, 0)
        cv.put(VX0 + 40 + i // 2, 131 - i, [(236, 224, 204)], 0, 0)
    cv.glow(508, 133, 40, (255, 236, 200), 0.25)


# ─── Expositor de fullets nous (museu, no corporació) ──────────────────────

def expositor(cv):
    EX0, EX1 = 571, 617
    for lx in (EX0 + 4, EX1 - 6):
        cv.rect(lx, 181, lx + 2, 208, WALNUT, lambda x, y, lx=lx: 3.0 - (x - lx) * 0.5)
    cv.rect(EX0 + 3, 205, EX1 - 3, 208, WALNUT, 2.4)
    cv.rect(EX0, 139, EX1, 184, WALNUT, lambda x, y: 2.6 - (x - EX0) / 80 + (hr(x // 5, y // 3, 2) - 0.5) * 0.2)
    cv.hline(EX0, EX1, 139, WALNUT, 5.0)
    cv.rect(EX0 - 1, 131, EX1 + 1, 139, GOLD, lambda x, y: 3.4 - (y - 131) * 0.15, 0.3)
    cv.hline(EX0 - 1, EX1 + 1, 131, GOLD, 4.6, 0.3)
    text(cv, (EX0 + EX1 + 1) // 2 - text_w('MUSEU') // 2, 132, 'MUSEU', WALNUT, 1.0, 0)
    for row, y0 in enumerate((143, 156, 169)):
        for col, x0 in enumerate((EX0 + 3, EX0 + 25)):
            cv.rect(x0, y0, x0 + 18, y0 + 11, PAPER, 4.6, 0.4)
            cv.rect(x0 + 2, y0 + 2, x0 + 8, y0 + 7, SEPIA, 2.0 + (row + col) % 2, 0.3)        # una foto petita
            cv.put(x0 + 5, y0 + 4, SEPIA, 4.2, 0.3)
            cv.vline(x0 + 5, y0 + 5, y0 + 7, SEPIA, 3.4, 0.3)
            cv.hline(x0 + 10, x0 + 16, y0 + 3, CREAM, 3.0, 0)
            cv.hline(x0 + 10, x0 + 15, y0 + 5, CREAM, 3.0, 0)
            cv.hline(x0 + 10, x0 + 14, y0 + 7, CREAM, 3.4, 0)
            cv.hline(x0 + 2, x0 + 16, y0 + 9, CREAM, 3.4, 0)
            cv.hline(x0 - 1, x0 + 19, y0 + 12, WALNUT, 4.0)


# ─── El sòcol de l'holograma, apagat i tapat amb un drap ───────────────────

def socol_apagat(cv):
    cx, by = PEDX, PEDY
    R, top = 40, by - 40
    # ombra al terra
    cv.darken(cx - R - 11, by - 5, cx + R + 13, by + 11,
              lambda x, y: 0.9 - abs((x - cx - 4) / (R + 13)) ** 2 - abs(y - by - 1) / 11)
    # cos cilíndric de plaques (fred: no és d'aquest museu)
    for y in range(top, by + 1):
        for x in range(cx - R, cx + R + 1):
            nx = (x - cx) / R
            if y > by - 8 and (nx * nx + ((y - (by - 8)) / 8) ** 2) > 1:
                continue
            lvl = 4.6 - nx * 1.6 - abs(nx) ** 3 * 2.2 - (y - top) / 35
            ang = math.degrees(math.asin(max(-1, min(1, nx))))
            a = (ang + 90) % 30
            if abs(a - 15) > 14:
                lvl = 1.6
            elif a < 2.2:
                lvl += 0.6                                                  # cantell de la placa
            if y == top + 21:
                lvl -= 1.0                                                  # junta horitzontal
            elif y == top + 22:
                lvl += 0.4
            cv.put(x, y, STEEL, lvl)
    for ang in range(-75, 90, 30):
        x = round(cx + math.sin(math.radians(ang)) * (R - 3))
        for yy, lv in ((top + 8, 7.0), (by - 8, 6.0)):
            cv.put(x, yy, STEEL, lv)
            cv.put(x + 1, yy + 1, STEEL, lv - 4.0)
    # tapa amb l'emissor mort (el vidre blau, fosc i polsós)
    cv.disc(cx, top, R, 8, STEEL, lambda nx, ny: 6.0 - ny * 0.8 - nx * 0.8)
    cv.disc(cx, top, R - 7, 5.9, STEEL, 2.4)
    cv.disc(cx, top + 0.5, R - 9, 4.5, DEAD, lambda nx, ny: 2.6 - (nx * nx + ny * ny) * 1.4 - nx * 0.6, 0)
    cv.disc(cx, top + 0.5, 12, 1.9, DEAD, 0.4, 0)
    for i in range(7):
        cv.put(cx - 21 + i, top - 1 - (i > 3), DEAD, 4.0, 0)                  # un reflex mort al vidre
    for i in range(14):                                                    # pols
        a = hr(i, 71) * 2 * math.pi
        rr = 0.3 + hr(i, 72) * 0.6
        cv.put(round(cx + math.cos(a) * rr * (R - 10)), round(top + 0.5 + math.sin(a) * rr * 4), DEAD, 3.0, 0)

    # el drap: posat per damunt, deixa veure l'emissor a l'esquerra i cau en plecs per davant i per la dreta
    def rim(x):                                                      # vora de davant de la tapa
        nx = (x - cx) / (R + 3)
        return top + 8.7 * math.sqrt(max(0.0, 1 - nx * nx))

    def back(x):
        nx = (x - cx) / (R + 3)
        return top - 9.3 * math.sqrt(max(0.0, 1 - nx * nx))

    def hem(x):
        u = max(0.0, (x - (cx - 12)) / (R + 15))
        return rim(x) + 3 + 35 * u ** 1.7 + math.sin(x / 3.1) * (1.1 + 1.33 * u) + ((x // 5) % 2) * u * 1.33

    @lru_cache(maxsize=None)
    def covered(x, y):
        if x > cx + R + 3 + (2.0 * math.sin(y / 4.0) if y > rim(x) else 0) + max(0, y - by + 5):
            return False
        if y < back(x) - 1 or y > min(hem(x), by + 1):
            return False
        return (x - cx) * 7 + (y - top) * 9 > -53                      # vora esquerra, en diagonal

    for y in range(top - 12, by + 3):
        for x in range(cx - 27, cx + R + 11):
            if not covered(x, y):
                continue
            nx = (x - cx) / R
            if y <= rim(x):
                lvl = 5.2 - nx * 0.5 + (math.sin((x - cx) / 6.7 + y * 0.22) * 0.4)
            else:
                d = (y - rim(x)) / 35
                fold = math.sin((x - cx) / 4.3 - d * 2.0)
                lvl = 4.0 - nx * 1.4 + fold * (0.5 + d * 1.2) - d * 0.8
                if abs(y - rim(x)) < 2:
                    lvl += 0.9                                         # el plec de la vora de la tapa
            if not covered(x, y + 1) or not covered(x, y + 2):
                lvl -= 1.4                                             # gruix del bord
            elif not covered(x, y + 3):
                lvl -= 0.5
            if not covered(x - 1, y) or not covered(x, y - 1):
                lvl += 0.6
            lvl += 0.15 if (x + y) % 2 else -0.05                      # la trama de la tela
            cv.put(x, y, CLOTH, lvl)
    cv.darken(cx - 16, top, cx + R + 8, by,
              lambda x, y: 0.7 if not covered(x, y) and covered(x, y - 3) and y > rim(x) else 0)
    # cable desendollat, serpentejant pel terra
    for i in range(53):
        t = i / 52
        x = round(cx - R + 3 - t * 45)
        y = round(by - 4 + t * 12 + math.sin(t * 7) * 3.3)
        cv.put(x, y, IRON, 3.0)
        cv.put(x, y + 1, IRON, 1.8)
        cv.put(x, y + 2, IRON, 0.6)
    ex, ey = cx - R - 43, by + 8
    cv.rect(ex - 5, ey - 1, ex, ey + 2, IRON, lambda x, y: 4.0 - (y - ey + 1) * 0.8)     # la clavilla
    cv.vline(ex - 5, ey - 1, ey + 2, IRON, 1.4)
    cv.hline(ex - 8, ex - 6, ey - 1, COPPER, 5.0)
    cv.hline(ex - 8, ex - 6, ey + 2, COPPER, 4.0)
    # el cartell
    kx0, ky0 = cx - 33, top + 16
    kw, kh = 55, 19
    cv.darken(kx0 + 3, ky0 + 3, kx0 + kw + 3, ky0 + kh + 3, 0.7)
    cv.rect(kx0, ky0, kx0 + kw, ky0 + kh, PAPER, lambda x, y: 4.6 - (y - ky0) * 0.075 - (x - kx0) * 0.015)
    cv.hline(kx0, kx0 + kw, ky0 + kh, PAPER, 2.4)
    text(cv, kx0 + kw // 2 - text_w('APAGAT') // 2 + 1, ky0 + 2, 'APAGAT', RED, 3.4, 0)
    text(cv, kx0 + kw // 2 - text_w('PER SEMPRE') // 2 + 1, ky0 + 11, 'PER SEMPRE', WALNUT, 1.4, 0)
    for tx_, d in ((kx0 - 1, 1), (kx0 + kw + 1, -1)):                      # cinta adhesiva als cantons
        for i in range(5):
            for w in (0, 1):
                cv.put(tx_ + (i + w) * d, ky0 - 1 + i, MANILA_T, 4.2 - w * 0.6, 0.4)


# ─── El Cargol, conserge ───────────────────────────────────────────────────

def warm(spr, k):
    """Tenyeix un sprite amb la calor del museu (el sprite té la llum pròpia)."""
    a = np.asarray(spr).astype(np.float64)
    m = a[..., 3] > 0
    rgb = a[..., :3]
    rgb[m] = np.round(rgb[m] + (np.array((255, 200, 140)) - rgb[m]) * k)
    return Image.fromarray(a.astype(np.uint8), 'RGBA')


def conserge(cv):
    # galleda i pal de fregar
    gx, gy = 547, 264
    cv.darken(gx - 12, gy - 3, gx + 15, gy + 4, lambda x, y: 0.9 - abs(x - gx - 1) / 15 - abs(y - gy) / 5)
    cv.poly([(gx - 9, gy - 17), (gx + 9, gy - 17), (gx + 7, gy), (gx - 7, gy)], WARN,
            lambda x, y: 3.6 - (x - gx) * 0.135 - (y - gy + 17) * 0.03)
    for yy in (gy - 11, gy - 4):                                             # els cèrcols de la galleda
        hw = 9 - 2 * (yy - gy + 17) / 17
        cv.hline(round(gx - hw) + 1, round(gx + hw) - 1, yy, WARN, 4.6)
        cv.hline(round(gx - hw) + 1, round(gx + hw) - 1, yy + 1, WARN, 2.2)
    cv.hline(gx - 9, gx + 9, gy - 17, WARN, 5.0)
    cv.hline(gx - 8, gx + 8, gy - 16, IRON, 1.0)
    cv.line(gx - 9, gy - 17, gx, gy - 25, IRON, 3.0)
    cv.line(gx + 9, gy - 17, gx, gy - 25, IRON, 2.4)
    cv.line(gx + 3, gy - 16, gx + 20, gy - 83, WALNUT, 4.6)
    cv.line(gx + 4, gy - 16, gx + 21, gy - 83, WALNUT, 3.4)
    cv.line(gx + 5, gy - 16, gx + 22, gy - 83, WALNUT, 2.0)
    for i in range(-5, 6):
        cv.line(gx + 4, gy - 16, gx + 4 + i, gy - 5, CLOTH, 3.6 - abs(i) * 0.25)
    # el Cargol vell, de cara, amb una ombra de contacte
    spr = warm(cargol('D', old=True), 0.12)
    fx, fy = 36, 80
    cv.darken(CGX - 29, CGY - 3, CGX + 29, CGY + 5, lambda x, y: 0.9 - abs(x - CGX) / 32 - (y - CGY + 3) / 11)
    cv.img.alpha_composite(spr, (CGX - fx, CGY - fy))
    # una gorra de conserge, de visera, entre les antenes
    cx, cy = CGX - fx + 36, CGY - fy + 23
    cv.disc(cx, cy, 9.3, 4, CAP, lambda nx, ny: 2.4 - nx - ny * 0.6, 0.3)
    cv.hline(cx - 6, cx + 4, cy - 3, CAP, 3.4, 0.3)
    cv.hline(cx - 11, cx + 8, cy + 3, [(14, 14, 24)], 0, 0)
    cv.hline(cx - 12, cx + 5, cy + 4, [(24, 26, 40)], 0, 0)
    cv.hline(cx - 10, cx + 2, cy + 5, [(18, 18, 30)], 0, 0)
    cv.put(cx, cy - 1, GOLD, 5.0, 0)
    cv.put(cx + 1, cy - 1, GOLD, 4.0, 0)
    cv.put(cx, cy, GOLD, 3.0, 0)


# ─── La Vet, d'esquena, davant la foto (ja sense la granota de presa) ───────

JACKET = M((22, 30, 30), (36, 52, 50), (54, 78, 70), (76, 106, 90), (104, 138, 112), (140, 172, 140), dith=0.0)


def vet(cv):
    spec = dict(VET, legs=DENIM, top=JACKET, forearm=JACKET)
    spec['hooks'] = {k: v for k, v in VET['hooks'].items() if k in ('hair_back', 'hair')}
    spr = warm(person(spec, 'U'), 0.10)
    cv.darken(VTX - 21, VTY - 4, VTX + 24, VTY + 4, lambda x, y: 0.95 - abs(x - VTX - 1) / 24 - abs(y - VTY) / 7)
    cv.img.alpha_composite(spr, (VTX - 34, VTY - 111))
    # llum del focus de la foto al cabell
    for y in range(VTY - 111, VTY - 88):
        for x in range(VTX - 8, VTX + 12):
            o = cv.P[x, y]
            if o[0] > 150 and hr(x, y, 31) > 0.5:
                cv.P[x, y] = mix(o, (255, 236, 196), 0.35) + (255,)


def flors(cv, x0, y0):
    """Un pom de flors embolicat en paper, deixat al banc."""
    cv.poly([(x0, y0), (x0 + 21, y0 - 5), (x0 + 24, y0 - 1), (x0 + 3, y0 + 4)], PAPER, lambda x, y: 4.6 - (y - y0) * 0.3)
    cv.line(x0 + 3, y0 + 1, x0 + 21, y0 - 3, PAPER, 3.4)                      # el plec del paper
    for i in range(8):
        cv.line(x0 + 19, y0 - 3, x0 + 29 + (i % 3), y0 - 5 - i // 2, LEAF, 2.6 + (i % 2) * 0.6)
    for dx, dy, c in ((24, -8, RED), (28, -4, WARN), (31, -9, RED), (27, -12, PAPER), (33, -5, RED), (23, -4, WARN)):
        cv.disc(x0 + dx + 5, y0 + dy, 2.1, 1.9, c, lambda nx, ny: 4.6 - nx - ny, 0.4)
        cv.put(x0 + dx + 5, y0 + dy, c, 2.6, 0.4)
    cv.darken(x0 + 1, y0 + 4, x0 + 35, y0 + 5, 0.6)


# ─── Fons ──────────────────────────────────────────────────────────────────

@lru_cache(maxsize=None)
def _quiet(mira=False, cargol=False):
    """El fons quiet abans de la gradació final (és el mateix a tots els fotogrames)."""
    cv = Canvas(light=LIGHT)
    wall(cv)
    floor(cv)

    # rètol nou del sostre, de fusta i llautó
    title = 'MUSEU DE LA MEMÒRIA'
    tw = text_w(title)
    tx = 293 - tw // 2
    cv.darken(tx - 8, 32, tx + tw + 10, 33, 0.6)
    cv.rect(tx - 9, 18, tx + tw + 8, 31, WALNUT, lambda x, y: 2.6 - (y - 18) * 0.08 + (hr(x // 8, y, 3) - 0.5) * 0.3, 0.3)
    cv.hline(tx - 9, tx + tw + 8, 18, WALNUT, 4.6, 0.3)
    cv.hline(tx - 9, tx + tw + 8, 31, WALNUT, 1.0, 0.3)
    for sx in (tx - 6, tx + tw + 5):
        cv.put(sx, 24, GOLD, 5.4, 0)
        cv.put(sx, 25, GOLD, 2.6, 0)
    text(cv, tx, 23, title, GOLD, 5.0, 0)

    # carril i focus
    for hx in range(130, 560, 110):
        cv.vline(hx, 9, 13, IRON, 2.0)
    cv.hline(93, 560, 14, IRON, 4.0)
    cv.hline(93, 560, 15, IRON, 3.0)
    cv.hline(93, 560, 16, IRON, 1.4)
    for sx, sy in SPOTS.values():
        spot(cv, sx, sy)

    # porta (la mateixa d'abans, però oberta de bat a bat: ara s'hi entra i se'n surt)
    DX0, DX1, DT = 16, 81, 80
    cv.rect(DX0 - 5, DT - 5, DX1 + 5, 204, CREAM,
            lambda x, y: 4.8 if x < DX0 - 2 or y < DT - 2 else (1.8 if x > DX1 + 1 else 3.0))
    for y in range(DT, 205):
        for x in range(DX0, DX1 + 1):
            # passadís il·luminat al fons
            lvl = 4.4 - abs(x - 48) / 40 - (y - DT) / 160
            if y > 181:
                lvl = 3.0 - (y - 181) / 21 - (0.4 if (y - 181) in (3, 8, 15) else 0)
            cv.put(x, y, CREAM, lvl, 0.4)
    for i in range(5):                                                      # fulles plegades contra el marc
        cv.vline(DX0 + i, DT, 204, STEEL, 3.4 - i * 0.45)
        cv.vline(DX1 - 4 + i, DT, 204, STEEL, 2.0 + i * 0.25)
    cv.glow(48, 147, 53, (255, 236, 200), 0.25)
    s = 'SORTIDA'
    sw = text_w(s)
    sx0 = 49 - sw // 2 - 3
    cv.rect(sx0, 63, sx0 + sw + 5, 73, PILOT, 1.5, 0)
    text(cv, sx0 + 3, 65, s, PILOT, 3.5, 0)
    cv.glow(49, 68, 21, (90, 255, 140), 0.25)

    foto(cv, mira)
    llibreta(cv)
    fabrica(cv)
    vitrina(cv)
    expositor(cv)

    # banc de fusta per seure davant la foto
    cv.darken(BX0 - 5, BY + 19, BX1 + 8, BY + 25, lambda x, y: 0.8 - (y - BY - 19) / 8)
    for lx in (BX0 + 11, BX1 - 13):
        cv.rect(lx, BY + 5, lx + 4, BY + 21, WALNUT, lambda x, y, lx=lx: 3.0 - (x - lx) * 0.4)
    cv.rect(BX0, BY - 4, BX1, BY, WALNUT,
            lambda x, y: 5.0 - (y - BY + 4) * 0.25 + (hr(x // 12, y, 3) - 0.5) * 0.4 + (hr(x // 3, y, 4) - 0.5) * 0.15)
    cv.rect(BX0, BY + 1, BX1, BY + 5, WALNUT, lambda x, y: 2.8 - (y - BY - 1) * 0.3)
    cv.hline(BX0 + 5, BX1 - 5, BY + 13, WALNUT, 1.6)
    cv.hline(BX0 + 5, BX1 - 5, BY + 14, WALNUT, 1.0)

    cv.darken(0, FLOOR_Y, W - 1, FLOOR_Y + 4, lambda x, y: 0.5 - (y - FLOOR_Y) * 0.105)
    reflect(cv, FLOOR_Y, BY - 5)

    flors(cv, BX0 + 16, BY - 5)
    socol_apagat(cv)
    if cargol:
        conserge(cv)
    vet(cv)
    return cv.img


@lru_cache(maxsize=None)
def _vignette():
    """La vinyeta suau que tanca el pla (factor per píxel)."""
    y, x = np.mgrid[0:H, 0:W]
    d = np.hypot((x - 320) / 400, (y - 160) / 253)
    return np.clip(1 - np.maximum(0.0, d - 0.62) * 1.1, 0.0, 1.0)[..., None]


def bg(cv, mira=False, cargol=False, t=0.0):
    cv.img.paste(_quiet(mira, cargol))

    # ─── Gradació final: calidesa de focus, i pols daurada als cons ─────────
    # (amb t, la llum dels focus respira i la pols sura; t = 0 és el fons quiet)
    P = cv.P
    for k, ((sx, sy), (tx_, ty_)) in enumerate(zip(SPOTS.values(), TGT)):
        breath = 1 + 0.35 * math.sin(2 * math.pi * (t * (1 + k % 2) + k * 0.27))
        for y in range(sy + 11, ty_ + 40):
            u = (y - sy) / (ty_ + 40 - sy)
            half = 4 + u * 40
            mx = sx + (tx_ - sx) * u
            for x in range(int(mx - half), int(mx + half) + 1):
                a = 0.10 * breath * (1 - abs(x - mx) / half) * (1 - u * 0.7)
                if 0 <= x < W and a > B4[y & 3][x & 3] * 0.25:
                    P[x, y] = mix(P[x, y], (255, 232, 190), a) + (255,)
    spots = list(SPOTS.values())
    for i in range(120):                                                     # motes de pols als feixos
        k = int(hr(i, 1) * 4)
        (sx, sy), (tx_, ty_) = spots[k], TGT[k]
        u = 0.15 + hr(i, 2) * 0.8
        ph = hr(i, 4)
        sp = 1 + int(hr(i, 5) * 2)                                           # cicles per bucle: 1 o 2
        x = round(sx + (tx_ - sx) * u + (hr(i, 3) - 0.5) * 53 * u + 3.3 * math.sin(2 * math.pi * (sp * t + ph)))
        y = round(sy + (ty_ - sy) * u + 2.7 * math.sin(2 * math.pi * (t + ph * 1.7)) + 2.0 * math.cos(2 * math.pi * (sp * t + ph)))
        a = 0.35 + 0.35 * (0.5 + 0.5 * math.sin(2 * math.pi * (2 * t + ph * 3)))  # parpelleja quan travessa la llum
        if 0 <= x < W and 0 <= y < H:
            P[x, y] = mix(P[x, y], (255, 240, 200), a) + (255,)
    # un reflex que passa pel vidre de la vitrina (fora del vidre a t = 0)
    g = t * 2.2 - 0.6
    if 0 < g < 1:
        gx = 475 + g * 68
        for y in range(120, 160):
            for x in range(475, 544):
                d = abs((x - gx) + (y - 140) * 0.6)
                if d < 3.3:
                    P[x, y] = mix(P[x, y], (255, 250, 236), 0.35 * (1 - d / 3.3)) + (255,)
    # tint càlid de tot el pla i vinyeta suau
    a = np.asarray(cv.img).astype(np.float64)
    rgb = a[..., :3]
    rgb = np.round(rgb + (np.array((255, 196, 128)) - rgb) * 0.07)
    rgb = np.floor(rgb * _vignette())
    a[..., :3] = rgb
    cv.img.paste(Image.fromarray(a.astype(np.uint8), 'RGBA'))


def _mask(a, b):
    """Píxels on dues imatges difereixen (numpy bool H×W)."""
    return np.any(np.asarray(a) != np.asarray(b), axis=-1)


@lru_cache(maxsize=None)
def _render(mira=False, cargol=False):
    cv = Canvas(light=LIGHT)
    bg(cv, mira=mira, cargol=cargol)
    return cv.img


def _diferencia(cv, **amb):
    """Només els píxels que canvien respecte del fons sense res: la Mira a la foto, o en Cargol."""
    on, off = _render(**amb), _render()
    m = Image.fromarray((_mask(on, off) * 255).astype(np.uint8), 'L')
    cv.img.paste(on, mask=m)


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
    base = _render()
    props = _mask(_render(mira=True), base) | _mask(_render(cargol=True), base)
    blocked = props.copy()                                                  # amb un píxel de marge
    for dy in (-1, 0, 1):
        for dx in (-1, 0, 1):
            blocked |= np.roll(np.roll(props, dy, axis=0), dx, axis=1)
    frames = []
    for i in range(n):
        cv = Canvas(light=LIGHT)
        bg(cv, t=i / n)
        m = _mask(cv.img, base) & ~blocked
        fr = Image.new('RGBA', (W, H), (0, 0, 0, 0))
        fr.paste(cv.img, mask=Image.fromarray((m * 255).astype(np.uint8), 'L'))
        frames.append(fr)
    return frames


ANIMS = {'ambient': {'frames': _ambient_frames, 'frameDuration': 110}}
