"""
La Conjura de l'Avet — `postcredits`: la porteria, de nit, temps després. Art definitiu, EN 3D (hd640/tres_d.py), a 1×.

Una versió pròpia i senzilla de la porteria (la sala `porteria` del joc és d'un altre mòdul): el passadís de pedra
que s'allunya cap a la dreta, amb la volta de canó, dues torxes a la paret del fons i la resta fosc. A l'esquerra, la
porta gran del monestir, de taulons i ferro, tancada amb la barra. Al mig, en **Bonfill** de guàrdia, assegut al banc
amb la llança recolzada a la paret: aguanta un pergamí (del dret, ara) i el segueix amb el dit, lletra a lletra
(«Sant... i... sen... ya.»). Al costat, el faristol amb el llibre d'entrades.

Primer pla: l'arc de la volta, fosc, a dalt, i el muntant d'una porta a la dreta.

ANIMS: `torxes` (les dues flames i la seva claror) i `bonfill` (el dit que va seguint les lletres, i el cap que s'hi
acosta).
"""
import functools
import math

from PIL import Image

import hd640  # noqa: F401  (abans de cap hd.rooms: posa la llibreria a 640×360)

from hd.pix import Canvas, Light, W, mix
from hd640.tres_d import Camera, Escena, Llum
from hd640.rooms.nit_comu import (BOTTOM, PEDRA, LLOSA, FUSTA, FERRO, FOC, PERGAMI, TINTA, TELA, fbm, hr, carreus,
                                  lloses, taulons, veta, flama, ombra, hud_negre, sense, sense_hud, mascara, _diff)

F = 360
CAM = Camera(pos=(40, 160, 0), yaw=0.42, pitch=0.2, f=F, centre=(320, 110))

ZB = 270                      # la paret del fons (la del banc i les torxes)
XL = -10                      # la paret de la porta
XR = 1400
ZF = 40
YV = 210                      # on arrenca la volta
TORXES = ((70, 140, ZB - 10), (420, 140, ZB - 10))
BANC = (200, 26, ZB - 20, 110, 30)       # cx, alt, cz, ample, fons
FARISTOL = (296, ZB - 44)
BONFILL = (196, ZB - 26)                  # on seu (x, z: el peu del banc)

LLUMS = [Llum(TORXES[0], 280, 4.8, power=1.7), Llum(TORXES[1], 280, 4.8, power=1.7)]
AMBIENT = -0.6
LIGHT = Light(ambient=0.0, vignette=None, floor_fade=None)

# En Bonfill: el saig del comte (casquet de ferro, barba negra, gonella blava del comte, capa bruna, botes)
PELL = [(52, 30, 24), (96, 58, 42), (140, 92, 66), (180, 128, 94), (210, 162, 124), (232, 194, 158)]
BARBA = [(10, 8, 8), (22, 16, 14), (38, 28, 22), (56, 42, 32)]
GONELLA = [(10, 14, 26), (18, 26, 44), (28, 40, 66), (42, 58, 90), (60, 80, 116), (84, 106, 142)]
CAPA = [(18, 12, 8), (34, 22, 14), (54, 36, 22), (76, 52, 32), (100, 70, 44)]
CUIR = [(14, 8, 6), (28, 16, 10), (46, 28, 16), (66, 42, 24), (90, 60, 34)]


def _p(x, y, z):
    u, v, _ = CAM.projecta((x, y, z))
    return round(u), round(v)


# ─── El passadís ─────────────────────────────────────────────────────────────

def passadis(e):
    def terra(s, t, P):
        return lloses(P[0], P[2], mida=(46.0, 40.0), seed=15, base=3.0)

    e.quad('terra', (XL, 0, ZB), (XR, 0, ZB), (XR, 0, ZF), (XL, 0, ZF), ramp=LLOSA, lvl=terra)

    def paret(s, t, P):
        return carreus(s, t, alt=26.0, seed=17, base=3.2) - max(0.0, (P[1] - 150) / 80)

    e.quad('paret', (XL, YV, ZB), (XR, YV, ZB), (XR, 0, ZB), (XL, 0, ZB), ramp=PEDRA, lvl=paret)
    e.quad('paret_porta', (XL, YV + 80, ZB), (XL, YV + 80, ZF), (XL, 0, ZF), (XL, 0, ZB), ramp=PEDRA,
           lvl=lambda s, t, P: carreus(s, t, alt=26.0, seed=19, base=2.8), dues_cares=True)
    # la volta de canó: llesques de quart de cercle (del fons cap a nosaltres)
    n = 10
    R = (ZB - ZF) * 0.9
    for k in range(n):
        a0, a1 = math.pi / 2 * k / n, math.pi / 2 * (k + 1) / n
        z0, z1 = ZB - math.sin(a0) * R, ZB - math.sin(a1) * R
        y0, y1 = YV + (1 - math.cos(a0)) * R * 0.0 + math.sin(a0) * 0 + R * (1 - math.cos(a0)) * 0.6, \
            YV + R * (1 - math.cos(a1)) * 0.6
        e.quad('volta', (XL, y1, z1), (XR, y1, z1), (XR, y0, z0), (XL, y0, z0), ramp=PEDRA,
               lvl=lambda s, t, P, k=k: carreus(s, P[2], alt=24.0, seed=23, base=2.4) - k * 0.12, dues_cares=True)


def porta(e, cv):
    """La porta gran del monestir, a la paret de l'esquerra: dues fulles de taulons amb ferramenta i la barra posada."""
    z0, z1, h = ZB - 150, ZB - 20, 170
    zc, r = (z0 + z1) / 2, (z1 - z0) / 2
    pts = [_p(XL + 0.5, h - r + math.sin(math.pi * k / 16) * r, zc + math.cos(math.pi * k / 16) * r) for k in range(17)]
    pts = [_p(XL + 0.5, 0, z1)] + pts + [_p(XL + 0.5, 0, z0)]
    cv.poly(pts, FUSTA, lambda x, y: 3.6 - (1.4 if (x % 7) == 0 else 0) + (fbm(x / 3, y / 20, 32) - 0.5) * 0.9, lit=0)
    for y in (30, 100, 150):
        a, b = _p(XL + 1, y, z0 + 4), _p(XL + 1, y, z1 - 4)
        cv.line(a[0], a[1], b[0], b[1], FERRO, 3.4, lit=0)
    # la barra
    a, b = _p(XL + 3, 80, z0 - 10), _p(XL + 3, 80, z1 + 10)
    for d in range(4):
        cv.line(a[0], a[1] + d, b[0], b[1] + d, FUSTA, 4.4 - d * 0.6, lit=0)
    # el contorn de pedra (dovelles)
    for k in range(0, 17, 2):
        A = _p(XL + 0.6, h - r + math.sin(math.pi * k / 16) * r, zc + math.cos(math.pi * k / 16) * r)
        B = _p(XL + 0.6, h - r + math.sin(math.pi * k / 16) * (r + 14), zc + math.cos(math.pi * k / 16) * (r + 14))
        cv.line(A[0], A[1], B[0], B[1], PEDRA, 1.6, lit=0)


def torxa(e, cv, P, fase=0.0, flama_on=True):
    """Una torxa en una argolla de ferro de la paret."""
    x, y, z = P
    e.cable('torxa', [(x, y - 30, ZB - 1), (x, y - 4, z)], FERRO, 3.0, gruix=3.0)
    e.cable('torxa', [(x - 1, y - 44, z + 2), (x + 1, y - 2, z)], FUSTA, 3.4, gruix=5.0)
    u, v = _p(x, y, z)
    cv.disc(u, v + 1, 3, 2, [(20, 10, 6), (60, 24, 10), (120, 50, 16)], 1.6, lit=0)
    if flama_on:
        flama(cv, u, v, 16, 7, fase, seed=int(x) % 7)


def banc(e):
    cx, h, cz, w, d = BANC
    fusta = {'ramp': FUSTA, 'lvl': lambda s, t, P: veta(s, t, seed=41, base=3.8)}
    e.caixa('banc', cx - w / 2, cx + w / 2, h - 5, h, cz - d / 2, cz + d / 2, FUSTA, 3.4,
            cares={'dalt': {'ramp': FUSTA, 'lvl': lambda s, t, P: veta(s, t, seed=42, base=4.6)}, 'davant': fusta})
    for x in (cx - w / 2 + 6, cx + w / 2 - 12):
        e.caixa('banc', x, x + 6, 0, h - 5, cz - d / 2 + 3, cz + d / 2 - 3, FUSTA, 2.6)


def faristol(e, cv):
    """El faristol amb el llibre d'entrades obert (ninots en lloc de noms)."""
    x, z = FARISTOL
    e.cable('faristol', [(x, 0, z), (x, 62, z)], FUSTA, 4.2, gruix=5.0)
    for a in (0.5, 2.6, 4.7):
        e.cable('faristol', [(x, 10, z), (x + math.cos(a) * 12, 0, z + math.sin(a) * 9)], FUSTA, 2.6, gruix=3.0)
    e.quad('faristol', (x - 20, 74, z + 8), (x + 20, 74, z + 8), (x + 20, 60, z - 8), (x - 20, 60, z - 8), ramp=FUSTA,
           lvl=3.0)
    e.quad('faristol', (x - 18, 76, z + 7), (x + 18, 76, z + 7), (x + 18, 62, z - 7), (x - 18, 62, z - 7),
           ramp=PERGAMI, lvl=lambda s, t, P: 4.6 - (2.0 if int(t) % 4 == 0 and 3 < s % 18 < 15 else 0)
           - (0.8 if 17 < s < 19 else 0))


# ─── En Bonfill (dibuix pla, assegut) ────────────────────────────────────────

def _bonfill(dit=0, cap=0):
    """En Bonfill assegut, de cara i una mica girat cap a la dreta, amb el pergamí obert a les mans. `dit`: on té el
    dit al pergamí (0..3); `cap`: el cap una mica avançat (0 o 1). Figura d'1×: uns 64 px assegut."""
    cv = Canvas(60, 72, transparent=True)
    # les botes i les cames (assegut: les cuixes cap a nosaltres, curtes; les canyelles avall)
    for x0 in (20, 33):
        cv.rect(x0, 54, x0 + 7, 66, GONELLA, lambda x, y: 2.0 + (1 if x < x0 + 3 else 0), lit=0)
        cv.rect(x0 - 1, 62, x0 + 8, 70, CUIR, lambda x, y: 2.4 - (y - 62) * 0.1 + (0.8 if x < x0 + 3 else 0), lit=0)
        cv.rect(x0 - 2, 68, x0 + 9, 71, CUIR, 1.0, lit=0)
    # la capa (darrere, a les espatlles) i el cos (gonella blava, cinturó)
    cv.poly([(12, 22), (48, 22), (52, 56), (8, 56)], CAPA, lambda x, y: 2.6 - (abs(x - 30) / 30) * 1.4, lit=0)
    cv.poly([(16, 22), (44, 22), (46, 50), (14, 50)], GONELLA, lambda x, y: 3.6 + (x - 30) * -0.03 + (fbm(x / 4, y / 6, 3) - 0.5) * 0.6,
            lit=0)
    cv.rect(14, 40, 46, 43, CUIR, 2.6, lit=0)
    cv.rect(28, 40, 31, 43, [(60, 50, 20), (130, 110, 50), (200, 170, 90)], 1.6, lit=0)
    # les cuixes (la gonella cau sobre els genolls)
    cv.poly([(14, 46), (46, 46), (48, 58), (12, 58)], GONELLA, lambda x, y: 3.0 + (y - 46) * 0.08, lit=0)
    # el cap: el coll gruixut, la cara, la barba negra, el casquet de ferro
    hx, hy = 30 + cap, 12 + cap
    cv.rect(hx - 5, hy + 8, hx + 5, hy + 12, PELL, 2.2, lit=0)
    cv.disc(hx, hy + 2, 8, 9, PELL, lambda nx, ny: 3.6 - nx * 0.5 - ny * 0.3, lit=0)
    cv.disc(hx, hy + 8, 8, 5, BARBA, lambda nx, ny: 1.6 - ny * 0.4, lit=0)
    cv.disc(hx, hy - 4, 9, 6, FERRO, lambda nx, ny: 4.4 - nx * 1.0 - ny * 1.2, lit=0)
    cv.rect(hx - 9, hy - 1, hx + 9, hy, FERRO, 3.0, lit=0)
    for dx in (-3, 3):                                               # els ulls, mig aclucats (llegeix)
        cv.flat(hx + dx, hy + 3, (30, 18, 14))
        cv.flat(hx + dx + 1, hy + 3, (30, 18, 14))
    cv.flat(hx - 4, hy + 1, BARBA[1])                                # les celles, arrufades
    cv.flat(hx + 4, hy + 1, BARBA[1])
    cv.rect(hx - 1, hy + 4, hx + 1, hy + 6, PELL, 4.4, lit=0)        # el nas
    cv.rect(hx - 2, hy + 8, hx + 2, hy + 8, [(90, 40, 34)], 0, lit=0)   # la boca, que lletreja
    # el pergamí, obert a les mans (del dret!), amb ratlles de lletra
    px0, py0, px1, py1 = 14, 30, 46, 46
    cv.poly([(px0, py0 + 2), (px1, py0), (px1 + 1, py1 - 1), (px0 - 1, py1)], PERGAMI,
            lambda x, y: 4.8 - (y - py0) * 0.05 - (1.6 if (y - py0) % 4 == 2 and 3 < x - px0 < 29 else 0), lit=0)
    cv.rect(px0 - 2, py0, px0 + 1, py1, PERGAMI, 5.4, lit=0)         # els rotlles dels extrems
    cv.rect(px1 - 1, py0 - 1, px1 + 2, py1 - 1, PERGAMI, 5.4, lit=0)
    # les mans: una aguanta, l'altra segueix la línia amb el dit
    cv.disc(px0, py1 - 3, 3, 3, PELL, 3.4, lit=0)
    fx = px0 + 6 + dit * 6
    cv.disc(fx, py0 + 9, 3, 3, PELL, 3.6, lit=0)
    cv.rect(fx - 1, py0 + 5, fx, py0 + 8, PELL, 4.2, lit=0)          # el dit
    return cv.img


def _bonfill_sprite(e, dit=0, cap=0):
    x, z = BONFILL
    img = _bonfill(dit, cap)
    return e.sprite('bonfill', img, (30, 70), (x, 0, z - 14))


def llanca(e):
    """La llança, recolzada a la paret al costat del banc."""
    cx, h, cz, w, d = BANC
    x = cx + w / 2 + 10
    e.cable('llanca', [(x, 0, ZB - 8), (x + 8, 200, ZB - 2)], FUSTA, 4.6, gruix=3.6)
    u, v = _p(x + 8, 200, ZB - 2)
    cv = e.cv
    cv.poly([(u - 2, v), (u + 2, v), (u + 1, v - 14), (u, v - 16)], FERRO, lambda xx, yy: 4.6 - (xx - u) * 0.4, lit=0)


def ombres(e):
    cx, h, cz, w, d = BANC
    e.foscor('ombra', (cx - w / 2 - 20, 0.3, ZB), (cx + w / 2 + 60, 0.3, ZB), (cx + w / 2 + 60, 0.3, ZB - 50),
             (cx - w / 2 - 20, 0.3, ZB - 50), lambda s, t: 0.5 * max(0.0, 1 - (50 - t) / 30))
    # el fons del passadís, cap a la dreta, es perd en la foscor
    e.foscor('ombra', (700, 0.3, ZB), (XR, 0.3, ZB), (XR, 0.3, ZF), (700, 0.3, ZF), lambda s, t: min(0.85, s / 300))
    e.foscor('ombra', (700, YV + 200, ZB - 0.5), (XR, YV + 200, ZB - 0.5), (XR, 0, ZB - 0.5), (700, 0, ZB - 0.5),
             lambda s, t: min(0.85, s / 300))


def primer_pla(cv):
    """L'arc de la volta a dalt, fosc, i el muntant d'una porta a la dreta, en silueta."""
    COL = [(5, 4, 5), (10, 8, 9), (18, 13, 13), (28, 20, 18), (40, 28, 24)]
    for x in range(W):
        top = 16 + 20 * math.sin(math.pi * min(1.0, x / W)) * 0
        y1 = int(26 - 18 * math.sin(math.pi * x / W) ** 0.5 * 0.8)
        for y in range(0, y1 + 1):
            cv.put(x, y, COL, 1.4 + (fbm(x / 12, y / 6, 3) - 0.5) * 0.7 + (1.4 if y > y1 - 2 else 0), lit=0)
    for y in range(0, BOTTOM + 1):
        for x in range(604, W):
            cv.put(x, y, COL, 1.8 + (1.6 if x < 606 else 0) + (fbm(x / 6, y / 24, 4) - 0.5) * 0.8, lit=0)


@functools.lru_cache(maxsize=None)
def _davant():
    cv = Canvas(light=LIGHT, transparent=True)
    primer_pla(cv)
    return sense_hud(cv.img)


def _munta(torxes_on=True, bonfill_on=True, fase=0.0):
    cv = Canvas(light=LIGHT)
    e = Escena(cv, CAM, LLUMS, ambient=AMBIENT)
    passadis(e)
    porta(e, cv)
    ombres(e)
    for P in TORXES:
        torxa(e, cv, P, fase, flama_on=torxes_on)
        if torxes_on:
            u, v = _p(*P)
            cv.glow(u, v - 6, 80, (255, 180, 100), 0.2)
            cv.glow(u, v - 6, 20, (255, 226, 160), 0.45)
    llanca(e)
    banc(e)
    if bonfill_on:
        _bonfill_sprite(e)
    faristol(e, cv)
    cv.img.alpha_composite(_davant())
    cv.P = cv.img.load()
    hud_negre(cv)
    return cv.img, e


@functools.lru_cache(maxsize=None)
def _base():
    return _munta()[0]


def bg(cv):
    cv.img.paste(_base())
    cv.P = cv.img.load()


PROPS = {}


def _frames_torxes():
    img = _base()
    sense_flama = _munta(torxes_on=False)[0]
    frames = []
    n = 12
    for i in range(n):
        cv = Canvas(light=LIGHT, img=img.copy())
        for k, P in enumerate(TORXES):
            u, v = _p(*P)
            box = (u - 12, v - 30, u + 13, v + 4)
            cv.img.paste(sense_flama.crop(box), box[:2])
            cv.P = cv.img.load()
            flama(cv, u, v, 16, 7, (i / n + k * 0.4) % 1.0, seed=int(P[0]) % 7)
            cv.glow(u, v - 6, 20, (255, 226, 160), 0.4 + 0.1 * math.sin(2 * math.pi * (i / n * 2 + k * 0.3)))
        frames.append(sense(_diff(cv.img, img), _davant()))
    return frames


def _frames_bonfill():
    """El dit que segueix les lletres (sant... i... sen... ya), i el cap que s'hi acosta a cada síl·laba."""
    img = _base()
    frames = []
    for dit, cap in ((0, 0), (0, 1), (1, 1), (1, 0), (2, 1), (2, 0), (3, 1), (3, 0)):
        im, e = _munta(bonfill_on=False)
        _bonfill_sprite(e, dit, cap)
        faristol(e, e.cv)
        e.cv.img.alpha_composite(_davant())
        e.cv.P = e.cv.img.load()
        frames.append(sense(_diff(e.cv.img, img), _davant()))
    return frames


ANIMS = {'torxes': {'frames': _frames_torxes, 'frameDuration': 110},
         'bonfill': {'frames': _frames_bonfill, 'frameDuration': 600}}

GEOMETRIA = {'things': {}, 'spawns': {}}
