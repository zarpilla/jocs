"""
La centraleta del Miceli (Escena 2, dissabte al capvespre, sota terra). Art definitiu, a 1×.

Una cova entre les arrels del roure, de prop i una mica des de dalt (la composició de la referència 2):
  - a dalt, el **forat** per on entra l'última llum del capvespre, i l'**escala** de mà que en baixa (en volum,
    tres_d): per aquí entra l'Iri. Un raig de llum baixa fins a terra, amb pols que sura (`ANIMS`);
  - les parets són d'arrels, amb els **fils** del Miceli apagats (blau fosc), i al fons a l'esquerra el pas cap a les
    galeries; a l'esquerra la paret es tanca cap a la càmera;
  - a la dreta, una arrel enorme i, encastat, el **tauler** de la centraleta: el taulell en volum, girat cap a la
    sala, amb clavilles de bolet; el plafó amb rodes de coure, el **radar** d'arrels (pantalla rodona de mica,
    apagada) i el rètol «MICELI»; el llum de bolet que hi penja, i el **corn** de fusta que surt de l'arrel;
  - entre l'escala i el tauler, les **tres arrels** del trencaclosques 2.2: el mateix dibuix tres vegades (a ull nu
    són iguals);
  - al terra, a l'esquerra del raig, una arrel que surt de terra en arc (capa del davant amb la seva línia base: s'hi
    passa per darrere i per davant);
  - primer pla: arrels gruixudes a dalt a l'esquerra i falgueres a les cantonades de baix (`FRONT`).
Decorats: `fil_saba` (penja del taulell, brilla una mica), `radar_ences` (la pantalla verda amb el node 12 aixafat),
`xarxa_encesa` (tots els fils turquesa fins al sostre, l'arrel del mig encesa per dins i el fil de saba lligat).
Animacions: la pols al raig de llum (`pols`) i una hifa que penja del sostre i tremola amb el corrent (`hifa`).

El món (per al taulell, l'escala i el terra): x a la dreta, y amunt (0 = terra), z endins; 1 unitat = 1 px a la
distància on un personatge fa la seva mida (escala 1). Les parets de la cova, orgàniques, es pinten en pantalla.
"""
import functools
import math
import random

from PIL import Image

import hd640  # noqa: F401  (abans de cap hd.rooms: posa la llibreria a 640×360)

from hd.pix import Canvas, Light, W, H, mix
from hd640.rooms.arrel_comu import (BOTTOM, BARK, MOSS, EARTH, CLAY, LEAF, PLANK, IRONK, STONE, CREAM,
                                    COPPER, LAMPW, TURQ, GLOW_T, fbm, hr, arrel, bolet, filament, falguera, ombra,
                                    lletres, ample, hud_negre, sense, _diff)
from hd640.tres_d import Camera, Escena, Llum

# ─── La càmera i el món ──────────────────────────────────────────────────────
# Mirant de cara al fons de la cova, des de dalt (l'horitzó és per sobre de la pantalla: picat sense que les
# verticals convergeixin). Al terra, v = −20 + 380·260 / z: l'escala va de ≈0,74 al fons a ≈1,07 a baix de tot.
EYE_H, F, CY = 260, 380, -20
CAM = Camera(pos=(0, EYE_H, 0), yaw=0.0, pitch=0.0, f=F, centre=(320, CY))

LADDER = ((-112, 520), (-84, 520))                 # les potes de l'escala, a terra (x, z)
LADDER_TOP = (-26, 340, 92)                        # cap on s'inclina (dx, y de dalt, dz)
DESK = (255, 478, 120, 36, 52, -0.68)               # el taulell: cx, cz, ample, fons, alt, angle
PANEL_H = 92                                       # el plafó, damunt del taulell
HOLE = (232, -6, 62, 32)                           # el forat de dalt, en pantalla: cx, cy, rx, ry
ROOTS_X = (340, 378, 416)                          # les tres arrels (arrel_1, arrel_2, arrel_3)
ARCH = (100, 112, 46, 56)                          # el pas cap a les galeries: cx, cy, rx, ry

LIGHT = Light(ambient=-0.15, vignette=(46, 1), floor_fade=None)
LIGHT.width = W
LIGHT.point(232, 18, r=290, k=2.0, squash=0.9, power=1.4)                          # el forat
LIGHT.point(282, 214, r=160, k=0.9, squash=1.8, power=1.5)                         # on toca el raig, a terra
LIGHT.point(526, 44, r=190, k=1.5, squash=1.0, power=1.4)                          # el llum de bolet del tauler
LLUMS = [Llum((255, 196, 466), 300, 2.4, power=1.4),                               # el llum del tauler
         Llum((-120, 380, 600), 650, 1.2, power=1.3)]                              # el forat

SCREEN = [(4, 14, 8), (8, 30, 16), (14, 60, 30), (30, 110, 50), (80, 190, 90), (170, 250, 170), (230, 255, 230)]
MICA = [(12, 14, 12), (22, 28, 24), (36, 44, 38), (56, 66, 58), (90, 104, 94), (150, 166, 156)]
SKYH = [(120, 90, 70), (180, 140, 100), (220, 180, 130), (240, 210, 160), (250, 232, 196), (255, 246, 226)]


def _p(x, z, y=0.0):
    u, v, _ = CAM.projecta((x, y, z))
    return round(u), round(v)


def _desk_pt(lx, y, lz):
    cx, cz, _, _, _, a = DESK
    c, s = math.cos(a), math.sin(a)
    return (cx + lx * c - lz * s, y, cz + lx * s + lz * c)


def _z_de_v(v):
    return F * EYE_H / max(1e-3, v - CY)


def base(X):
    """La y de pantalla on la paret toca el terra (a l'esquerra, la paret es tanca cap a la càmera)."""
    return 156 + 8 * fbm(X / 40, 0.5, 4) + max(0, 70 - X) * 1.0


# ─── La cova ───────────────────────────────────────────────────────────────

def parets(cv):
    """El fons: arrels que baixen i es torcen (tubs, de llum al mig i foscos a les juntures), el sostre més fosc, el
    pas cap a les galeries i el forat de llum."""
    for y in range(0, BOTTOM + 1):
        for x in range(W):
            ph = x / 18 + math.sin(y / 46 + x / 110) * 1.6 + (fbm(x / 60, y / 80, 3) - 0.5) * 2.4
            f = ph % 1.0
            tub = math.sin(f * math.pi) ** 0.7
            lvl = 2.0 + tub * 2.0 + (fbm(x / 3, y / 9, 8) - 0.5) * 1.0 + (hr(int(ph), 0, 2) - 0.5) * 0.8
            lvl -= max(0.0, 1 - y / 50) * 0.9                                     # el sostre, més fosc
            cv.put(x, y, CLAY, lvl, lit=1.0)
    # el pas cap a les galeries: un arc fosc, més fosc com més endins
    cx, cy, rx, ry = ARCH
    for y in range(cy - ry, BOTTOM):
        for x in range(cx - rx - 2, cx + rx + 3):
            nx, ny = (x - cx) / rx, (y - cy) / ry
            d = nx * nx + min(ny, 0) ** 2
            if d <= 1 and y < base(x) + 2:
                cv.put(x, y, CLAY, 0.5 + d * 2.0 + (fbm(x / 6, y / 10, 12) - 0.5) * 0.8, lit=0.25)
            elif d <= 1.18 and y < base(x):
                cv.put(x, y, CLAY, 4.6 - (d - 1) * 8, lit=0.8)                     # la vora de l'arc, gastada
    # el forat de dalt: el cel del capvespre, i la vora de terra encesa
    hx, hy, hrx, hry = HOLE
    for y in range(0, hy + hry + 8):
        for x in range(hx - hrx - 12, hx + hrx + 13):
            nx, ny = (x - hx) / hrx, (y - hy) / hry
            d = nx * nx + ny * ny
            if d <= 1:
                cv.put(x, y, SKYH, 5.4 - d * 2.6 + (fbm(x / 8, y / 4, 31) - 0.5) * 0.6, lit=0)
            elif d <= 1.4:
                cv.put(x, y, CLAY, 7.6 - (d - 1) * 10 + (fbm(x / 3, y / 3, 32) - 0.5) * 1.6, lit=0)
    # unes arrels fines que creuen el forat, a contrallum
    for k, (x0, x1, sag) in enumerate(((180, 262, 9), (214, 300, 6))):
        for i in range(120):
            t = i / 119
            x = x0 + (x1 - x0) * t
            y = 4 + k * 7 + math.sin(t * math.pi) * sag
            cv.put(x, y, BARK, 0.6, lit=0)
    cv.glow(hx, 6, 90, (255, 222, 160), 0.55)


def terra(cv):
    """El terra (projectat: la textura s'empetiteix cap al fons): terra, clapes de molsa, fulles seques, pedretes."""
    for X in range(W):
        y0 = int(base(X))
        for Y in range(y0, BOTTOM + 1):
            z = _z_de_v(Y + 0.5)
            x = (X + 0.5 - 320) * z / F
            lvl = 3.0 + (fbm(x / 30, z / 30, 16) - 0.5) * 1.8 + (fbm(x / 6, z / 6, 17) - 0.5) * 0.8
            if fbm(x / 70, z / 60, 18) > 0.6 and fbm(x / 8, z / 8, 19) > 0.5:
                cv.put(X, Y, MOSS, lvl - 0.2)
            elif hr(int(x / 7), int(z / 7), 20) > 0.975:
                cv.put(X, Y, LEAF, lvl - 1.2)                                       # fulles seques que han caigut
            elif hr(int(x / 4), int(z / 4), 21) > 0.985:
                cv.put(X, Y, STONE, lvl + 0.2)
            else:
                cv.put(X, Y, EARTH, lvl)
        # la línia paret-terra no és neta: una ombra que la trenca
        for Y in range(y0, y0 + 5):
            if 0 <= Y <= BOTTOM and hr(X, Y, 22) < 0.8 - (Y - y0) * 0.16:
                cv.put(X, Y, EARTH, 1.2)


def vora(cv):
    """El peu de les parets: pedres, arrels petites que entren al terra, matolls de molsa i bolets."""
    rnd = random.Random(5)
    for _ in range(16):
        x = rnd.uniform(10, 580)
        if 222 < x < 268 or 320 < x < 440:
            continue
        y = base(x) + rnd.uniform(-1, 6)
        r = rnd.uniform(2, 8) if rnd.random() < 0.7 else rnd.uniform(8, 11)
        cv.disc(x, y, r * 1.5, r * 0.7, STONE, lambda nx, ny: 2.2 - ny * 1.4 - nx * 0.5, lit=1.0)
    for x, y, h, r in ((172, 172, 5, 5), (182, 174, 3, 3), (300, 168, 4, 5), (438, 172, 4, 4), (60, 214, 5, 6),
                       (70, 220, 3, 4), (150, 236, 4, 5)):
        bolet(cv, x, y, h, r, glow=0, cap=LEAF, stem=CREAM)


# Una arrel que surt del terra, fa un arc i hi torna a entrar, a l'esquerra del raig: un moble del pla mitjà (capa del
# davant amb la seva línia base) perquè els personatges hi passin per darrere i per davant. En pantalla: els dos peus
# (on entra a terra) i el punt de control de l'arc.
ARC = ((88, 237), (138, 196), (198, 233))
ARC_BASE = 235                                      # la línia base: on l'arrel toca a terra


def arrel_arc(cv):
    """L'arrel en arc, amb dos bolets de terra al llom."""
    p0, p1, p2 = ARC
    arrel(cv, p0, p1, p2, 7, 5, base=3.0, seed=86, moss=True, lit=1.0)
    for x, y, h, r in ((126, 213, 4, 4), (133, 212, 3, 3)):
        bolet(cv, x, y, h, r, glow=0, cap=LEAF, stem=CREAM)


def _evita(x, y):
    """On no hi ha fils: el forat del sostre, el pas de les galeries i el terra."""
    hx, hy, hrx, hry = HOLE
    ax, ay, arx, ary = ARCH
    return (((x - hx) / (hrx + 10)) ** 2 + ((y - hy) / (hry + 8)) ** 2 <= 1
            or (((x - ax) / (arx - 2)) ** 2 + (min(0, y - ay) / (ary - 2)) ** 2 <= 1 and y < base(x))
            or y > base(x) - 1)


# (x, y, angle, llargada): neixen al peu de la paret i pugen fins al sostre
FILS_PARET = [(14, 226, -1.3, 420), (44, 200, -1.5, 420), (160, 166, -1.6, 380), (196, 164, -1.8, 300),
              (292, 162, -1.4, 380), (446, 162, -1.7, 380), (306, 164, -1.9, 240)]
FILS_TRONC = [(596, 236, -1.75, 420), (626, 200, -1.6, 380)]


def fils(cv, encesa, quins=FILS_PARET, llavor=40):
    """La xarxa a les parets: apagada, blau fosc; encesa, turquesa fins al sostre."""
    for i, (x, y, a, l) in enumerate(quins):
        filament(cv, x, y, a, l, llavor + i, glow=1.0 if encesa else 0, branch=3, k=5.0 if encesa else 3.0,
                 dim=not encesa, sostre=0, evita=_evita, cap=-math.pi / 2)
    if quins is FILS_PARET:
        for x, y, h, r in ((34, 178, 5, 6), (46, 182, 3, 4), (150, 160, 4, 5), (310, 150, 3, 4), (458, 150, 4, 4)):
            bolet(cv, x, y, h, r, glow=1.0 if encesa else 0.12)


def escala(e):
    """L'escala de mà: dues potes i els graons, del terra fins al forat (surt per dalt)."""
    dx, ytop, dz = LADDER_TOP
    for k, (x, z) in enumerate(LADDER):
        e.cable('escala', [(x, 0, z), (x + dx, ytop, z + dz)], PLANK, 5.2 - k * 0.8, gruix=6.0)
    for y in range(26, ytop, 34):
        t = y / ytop
        (xa, za), (xb, zb) = LADDER
        e.cable('escala', [(xa + dx * t, y, za + dz * t), (xb + dx * t, y, zb + dz * t)], PLANK, 4.8, gruix=4.4)


# ─── Les tres arrels ───────────────────────────────────────────────────────

@functools.lru_cache(maxsize=None)
def _arrel_img():
    """Una arrel que baixa del sostre i entra al terra, amb dues arrels petites: la mateixa per a totes tres."""
    cv = Canvas(36, 180, transparent=True)
    arrel(cv, (19, -4), (12, 70), (18, 168), 7.5, 5.5, ramp=CLAY, base=1.4, seed=60, moss=False, lit=0)
    arrel(cv, (19, -4), (12, 70), (18, 168), 6.5, 4.5, base=4.6, seed=61, moss=False, lit=0)
    arrel(cv, (17, 60), (8, 70), (3, 92), 2.4, 1.2, base=3.0, seed=62, moss=False, lit=0)
    arrel(cv, (16, 112), (27, 122), (32, 150), 2.4, 1.2, base=3.0, seed=63, moss=False, lit=0)
    arrel(cv, (16, 160), (8, 166), (2, 172), 3.0, 1.6, base=2.6, seed=64, moss=False, lit=0)
    arrel(cv, (19, 160), (28, 166), (34, 171), 3.0, 1.6, base=2.6, seed=65, moss=False, lit=0)
    return cv.img


def arrels(cv, encesa):
    img = _arrel_img()
    sh = Image.new('RGBA', img.size, (14, 8, 6, 0))
    sh.putalpha(img.getchannel('A').point(lambda a: 120 if a else 0))
    for x in ROOTS_X:
        y0 = round(base(x)) + 6 - img.height
        ombra(cv, x + 4, round(base(x)) + 4, 14, 3, k=0.7)
        cv.img.alpha_composite(sh, (x - 18 + 5, y0 + 2))                           # l'ombra a la paret
        cv.img.alpha_composite(img, (x - 18, y0))
    cv.P = cv.img.load()
    if encesa:                                                                      # la viva, encesa per dins
        x = ROOTS_X[1]
        y0 = round(base(x)) + 6 - img.height
        for y in range(4, 166):
            xx = x - 18 + 15 + math.sin(y / 14) * 1.5 + (12 - 15) * (y / 166)
            cv.put(xx, y0 + y, TURQ, 5.6, lit=0)
            if y % 3 == 0:
                cv.put(xx + 2, y0 + y, TURQ, 4.6, lit=0)
        for y in range(10, 166, 26):
            cv.glow(x - 3, y0 + y, 16, GLOW_T, 0.35)


# ─── L'arrel gran i el tauler ──────────────────────────────────────────────

def tronc(cv):
    """L'arrel gruixuda de la dreta, on és encastat el tauler: ve cap a la càmera i baixa fins a terra."""
    for y in range(0, BOTTOM + 1):
        c = 612 + math.sin(y / 50) * 8 - max(0, y - 150) * 0.12
        w = 36 + max(0, y - 170) * 0.35
        for x in range(int(c - w), W):
            u = (x - c) / w
            lvl = 4.0 - u * 0.9 - max(0, -u) ** 6 * 1.8 + (fbm(u * 8, y / 30, 51) - 0.5) * 2.0
            lvl += (fbm(x / 4, y / 16, 52) - 0.5) * 1.0
            cv.put(x, y, BARK, lvl, lit=0.8)


def _panell(estat):
    """El plafó del tauler, de cara i a 2× (240×184 = 120×92 unitats): taulons, rodes de coure, el radar d'arrels,
    el born, i el rètol «MICELI»."""
    cv = Canvas(240, 184, transparent=True)
    for y in range(184):
        for x in range(240):
            plank = y % 30 < 2
            v = 3.6 - (1.6 if plank else 0) + (fbm(x / 6, y / 30, 3) - 0.5) * 1.0 + (hr(x // 2, y // 30, 4) - 0.5) * 0.6
            if x < 4 or x > 235 or y < 4:
                v += 1.0
            cv.put(x, y, PLANK, v, lit=0)
    # les rodes de fusta i coure, amb el seu indicador
    for x, y, r in ((30, 70, 18), (30, 126, 13), (74, 60, 11), (198, 150, 9), (216, 112, 8)):
        cv.disc(x, y, r, r, COPPER, lambda nx, ny: 3.6 - nx * 0.8 - ny * 1.2, lit=0)
        cv.disc(x, y, r * 0.42, r * 0.42, COPPER, 1.6, lit=0)
        cv.line(x, y, x + r * 0.7, y - r * 0.7, IRONK, 3.0, lit=0)
        cv.ring(x, y, r, COPPER, 1.4, lit=0, step=4)
    # cables que van de les rodes al radar
    for (x0, y0), (x1, y1) in (((48, 70), (130, 80)), ((44, 126), (126, 130)), ((86, 60), (140, 54))):
        for i in range(60):
            t = i / 59
            cv.put(x0 + (x1 - x0) * t, y0 + (y1 - y0) * t + math.sin(t * math.pi) * 8, IRONK, 2.4, lit=0)
    # el radar: una pantalla rodona de mica dins un cèrcol de coure
    rx, ry, rr = 166, 94, 40
    cv.disc(rx, ry, rr + 7, rr + 7, COPPER, lambda nx, ny: 3.8 - ny * 1.6 - nx * 0.4, lit=0)
    cv.ring(rx, ry, rr + 7, COPPER, 1.2, lit=0, step=2)
    if 'radar' in estat:
        def scr(nx, ny):
            d = math.hypot(nx, ny)
            v = 2.0 + (1.8 if abs(d % 0.34 - 0.17) > 0.15 else 0)                  # els anells
            if abs(nx) < 0.025 or abs(ny) < 0.025:
                v += 1.0
            a = math.atan2(ny, nx)
            sweep = (a + 2.2) % (2 * math.pi)                                       # l'escombrada, amb la cua
            if sweep < 0.9:
                v += 2.2 * (1 - sweep / 0.9)
            v += (hr(int(nx * 40), int(ny * 40), 7) - 0.5) * 0.9                   # (tremola: neu a la pantalla)
            return v
        cv.disc(rx, ry, rr, rr, SCREEN, scr, lit=0)
        # la xarxa al radar: nodes i fils, i el node 12 aixafat (vermell, trencat)
        nodes = [(-22, -14), (-6, -26), (14, -18), (24, 4), (8, 18), (-14, 22), (-26, 4), (0, 0)]
        for (ax, ay), (bx, by) in zip(nodes, nodes[1:] + nodes[:1]):
            for i in range(30):
                t = i / 29
                cv.put(rx + ax + (bx - ax) * t, ry + ay + (by - ay) * t, SCREEN, 4.6, lit=0)
        for ax, ay in nodes:
            cv.disc(rx + ax, ry + ay, 3, 3, SCREEN, 6.0, lit=0)
        nx_, ny_ = rx + 24, ry + 4                                                  # el node 12
        for dx, dy in ((-4, -4), (-3, -3), (3, -3), (4, -4), (-3, 3), (-4, 4), (3, 3), (4, 4), (0, 0), (1, 1),
                       (-1, -1), (1, -1), (-1, 1), (2, 2), (-2, -2), (2, -2), (-2, 2)):
            cv.flat(nx_ + dx, ny_ + dy, (255, 90, 60))
        lletres(cv, '12', nx_ - 6, ny_ + 7, (200, 255, 200))
        cv.glow(rx, ry, 56, (120, 240, 140), 0.25)
    else:
        cv.disc(rx, ry, rr, rr, MICA, lambda nx, ny: 1.4 - ny * 0.6 + (fbm(nx * 3, ny * 3, 9) - 0.5) * 0.8, lit=0)
        for i in range(26):                                                          # el reflex, a la mica
            cv.put(rx - 26 + i, ry - 22 + i * 0.3, MICA, 4.6 - i * 0.08, lit=0)
            cv.put(rx - 24 + i, ry - 19 + i * 0.3, MICA, 3.6 - i * 0.08, lit=0)
    # el born, sota el radar: dos borns de llautó
    for bx in (154, 178):
        cv.disc(bx, 150, 5, 5, COPPER, lambda nx, ny: 4.4 - ny * 1.4, lit=0)
        cv.disc(bx, 150, 2, 2, IRONK, 1.0, lit=0)
    # el rètol «MICELI», en una post clara clavada a dalt (lletra fosca sobre fusta clara: es llegeix en escorç)
    s = 'MICELI'
    tw = ample(s, 2)
    sx0, sy0 = 120 - tw // 2 - 10, 8
    cv.rect(sx0, sy0, sx0 + tw + 20, sy0 + 30, PLANK, lambda x, y: 7.2 - (y - sy0) * 0.04 + (hr(x, y, 5) - 0.5) * 0.5,
            lit=0)
    cv.rect(sx0, sy0 + 30, sx0 + tw + 20, sy0 + 32, PLANK, 2.0, lit=0)
    for nx in (sx0 + 4, sx0 + tw + 15):
        cv.disc(nx, sy0 + 15, 2, 2, IRONK, 2.0, lit=0)
    lletres(cv, s, sx0 + 10, sy0 + 6, (44, 24, 12), k=2)
    return cv.img


def tauler(cv, estat):
    """El taulell (en volum, girat cap a la sala) i el plafó, el llum de bolet, les clavilles i el corn."""
    cx, cz, w, d, h, a = DESK
    e = Escena(cv, CAM, LLUMS, ambient=-0.4)
    # l'ombra del taulell a terra
    e.foscor('ombra', _desk_pt(-w / 2 - 14, 0.3, d / 2 + 8), _desk_pt(w / 2 + 6, 0.3, d / 2 + 8),
             _desk_pt(w / 2 + 6, 0.3, -d / 2 - 24), _desk_pt(-w / 2 - 14, 0.3, -d / 2 - 24),
             lambda s, t: 0.75 * min(1.0, min(s, w + 20 - s) / 12) * min(1.0, min(t, d + 32 - t) / 10))

    def taulons(s, t, P):
        return 3.0 - (1.2 if int(t) % 13 == 0 else 0) + (fbm(s / 20, t / 4, 11) - 0.5) * 0.9

    def tapa(s, t, P):
        return 4.4 - (1.0 if int(s) % 24 < 1 else 0) + (fbm(s / 30, t / 3, 12) - 0.5) * 0.7

    e.caixa_girada('tauler', cx, cz, w, d, h, a, PLANK, 3.0,
                   cares={'davant': {'ramp': PLANK, 'lvl': taulons}, 'esquerra': {'ramp': PLANK, 'lvl': taulons},
                          'dreta': {'ramp': PLANK, 'lvl': taulons}, 'dalt': {'ramp': PLANK, 'lvl': tapa}})
    # el plafó, dret al darrere del taulell
    lz = d / 2 - 2
    e.quad('panell', _desk_pt(-w / 2, h + PANEL_H, lz), _desk_pt(w / 2, h + PANEL_H, lz), _desk_pt(w / 2, h, lz),
           _desk_pt(-w / 2, h, lz), tex=(_panell(frozenset(estat)), (0, 0, 120, 92), 2))
    # les clavilles: bolets petits clavats al taulell
    encesa = 'xarxa' in estat
    for i, lx in enumerate(range(-50, 52, 11)):
        u, v = _p(*[_desk_pt(lx, h, -6)[k] for k in (0, 2)], y=h)
        on = encesa and i % 3 != 1
        bolet(cv, u, v, 4, 3, glow=0.7 if on else 0, cap=TURQ if on else LEAF, stem=CREAM)
    # el llum: un bolet gros que penja d'una arrel del sostre, sobre el tauler
    lu, lv = _p(255, 466, 196)
    for y in range(0, lv - 8):
        cv.put(lu + math.sin(y / 9) * 1.2, y, BARK, 2.4, lit=0.3)
    bolet(cv, lu, lv, 4, 10, glow=0.0, cap=LAMPW, stem=CREAM, lit=0)
    cv.disc(lu, lv - 4, 9, 3, LAMPW, 5.2, lit=0)
    cv.glow(lu, lv, 60, (255, 210, 140), 0.4)
    # el corn per escoltar, de fusta, que surt de l'arrel gran
    for i in range(36):
        t = i / 35
        x, y = 626 - t * 40, 92 + t * 14
        r = 2.5 + t * 8
        cv.disc(x, y, r * 0.5, r, PLANK, lambda nx, ny: 4.4 - ny * 1.4 - nx * 0.4, lit=0.6)
    cv.disc(584, 106, 4, 10, IRONK, lambda nx, ny: 0.6 + nx * 0.6, lit=0)
    cv.ring(584, 106, 4.5, PLANK, 5.2, lit=0, step=10)
    return e


# ─── El fil de saba ───────────────────────────────────────────────────────

def _cap_fil():
    """On és lligat el fil de saba al taulell (la cantonada de l'esquerra)."""
    cx, cz, w, d, h, a = DESK
    return _p(*[_desk_pt(-w / 2 + 3, h, -d / 2 + 4)[k] for k in (0, 2)], y=h - 2)


def fil_solt(cv):
    """El fil de saba, solt: penja del taulell fins a terra i hi fa un rotllo; brilla una mica."""
    x0, y0 = _cap_fil()
    pts = []
    for i in range(70):
        t = i / 69
        pts.append((x0 - t * 10 + math.sin(t * 5) * 2.5, y0 + t * 38))
    for i in range(40):
        a = i / 39 * 2 * math.pi * 1.3
        pts.append((x0 - 12 + math.cos(a) * 7, y0 + 40 + math.sin(a) * 2))
    for x, y in pts:
        cv.put(x, y, TURQ, 5.2, lit=0)
        cv.put(x + 1, y, TURQ, 3.8, lit=0)
    cv.glow(x0 - 8, y0 + 30, 22, GLOW_T, 0.4)


def fil_lligat(cv):
    """El fil de saba lligat a l'arrel del mig: una catenària encesa del taulell a l'arrel."""
    x0, y0 = _cap_fil()
    x1 = ROOTS_X[1] - 2
    y1 = round(base(x1)) - 50
    n = 160
    for i in range(n + 1):
        t = i / n
        x = x0 + (x1 - x0) * t
        y = y0 + (y1 - y0) * t + math.sin(t * math.pi) * 26
        cv.put(x, y, TURQ, 6.2, lit=0)
        cv.put(x, y + 1, TURQ, 4.6, lit=0)
        if i % 16 == 0:
            cv.glow(x, y, 8, GLOW_T, 0.35)
    for k in range(3):                                                              # el nus a l'arrel
        cv.disc(x1 + 1, y1 + k * 2, 3, 1.5, TURQ, 6.6, lit=0)
    cv.glow(x1, y1, 16, GLOW_T, 0.5)


# ─── El raig de llum ──────────────────────────────────────────────────────

BEAM = ((232, 14, 44), (290, 222, 86))             # (x, y, mitja amplada) a dalt i a baix


def _beam(y):
    (xa, ya, wa), (xb, yb, wb) = BEAM
    t = max(0.0, min(1.0, (y - ya) / (yb - ya)))
    return xa + (xb - xa) * t, wa + (wb - wa) * t, t


def raig(cv):
    def k(x, y):
        if y > BEAM[1][1] + 10:
            return 0
        cx, hw, t = _beam(y)
        d = abs(x - cx) / hw
        return max(0.0, 1 - d) ** 1.5 * 0.3 * (1 - t * 0.35)
    cv.tint(150, 0, 400, BEAM[1][1] + 10, (255, 220, 160), k)


# ─── Primer pla ────────────────────────────────────────────────────────────

def primer_pla(cv):
    """Arrels gruixudes que emmarquen per dalt i per l'esquerra, i falgueres a les cantonades de baix (fosques)."""
    arrel(cv, (-24, 10), (40, 60), (20, 290), 20, 13, base=1.3, seed=81, moss=False, lit=0.6)
    arrel(cv, (-10, -14), (120, 24), (196, -24), 15, 7, base=1.6, seed=82, moss=False, lit=0.6)
    arrel(cv, (660, 290), (620, 238), (548, 300), 15, 11, base=1.8, seed=83, moss=True, lit=0.5)
    for i, (x, y, a, l, s) in enumerate(((-4, 268, 1.0, 110, -1), (26, 270, 1.4, 84, 1), (82, 272, 1.75, 56, 1),
                                          (560, 272, 1.9, 70, 1), (610, 268, 2.3, 100, 1))):
        falguera(cv, x, y, a, l, side=s, lvl=1.4, rim=1, seed=20 + i)


@functools.lru_cache(maxsize=None)
def _davant():
    cv = Canvas(light=LIGHT, transparent=True)
    primer_pla(cv)
    cv.rect(0, BOTTOM + 1, W - 1, H - 1, [(0, 0, 0)], 0, lit=0)
    img = cv.img
    a = img.load()
    for y in range(BOTTOM + 1, H):                                                  # (el HUD no és primer pla)
        for x in range(W):
            a[x, y] = (0, 0, 0, 0)
    return img


# ─── Composició ────────────────────────────────────────────────────────────

@functools.lru_cache(maxsize=None)
def _render(estat=frozenset()):
    """Tota la sala amb un estat: 'radar' (el radar encès), 'fil' (el fil de saba solt), 'xarxa' (tot encès)."""
    cv = Canvas(light=LIGHT)
    encesa = 'xarxa' in estat
    parets(cv)
    fils(cv, encesa)
    terra(cv)
    vora(cv)
    ombra(cv, (ARC[0][0] + ARC[2][0]) / 2, ARC_BASE + 1, (ARC[2][0] - ARC[0][0]) / 2 + 4, 4, k=0.6)
    arrel_arc(cv)
    e = Escena(cv, CAM, LLUMS, ambient=-0.3)
    escala(e)
    arrels(cv, encesa)
    tronc(cv)
    fils(cv, encesa, FILS_TRONC, 70)
    tauler(cv, estat)
    if 'fil' in estat:
        fil_solt(cv)
    if encesa:
        fil_lligat(cv)
    raig(cv)
    cv.img.alpha_composite(_davant())
    cv.P = cv.img.load()
    hud_negre(cv)
    return cv.img


def _base():
    return _render(frozenset())


def bg(cv):
    cv.img.paste(_base())
    cv.P = cv.img.load()


def _decorat(estat, sobre=()):
    """Un decorat: la sala amb aquell estat, menys la sala amb l'estat `sobre` (només el que canvia, i mai el primer
    pla). El fil de saba es mira sobre el radar encès (sempre hi és quan el fil penja)."""
    def draw(cv):
        img = _render(frozenset(estat))
        cv.img.alpha_composite(sense(_diff(img, _render(frozenset(sobre))), _davant()))
        cv.P = cv.img.load()
    return draw


PROPS = {
    'fil_saba': _decorat(('radar', 'fil'), ('radar',)),
    'radar_ences': _decorat(('radar',)),
    'xarxa_encesa': _decorat(('radar', 'xarxa')),
}


# ─── Animacions ─────────────────────────────────────────────────────────────

def _frames_pols():
    """Pols que sura al raig de llum (cada mota fa un llaç tancat: el bucle no salta)."""
    img = _base()
    davant = _davant().load()
    motes = []
    for k in range(46):
        y = BEAM[0][1] + 6 + hr(k, 11) * (BEAM[1][1] - BEAM[0][1] - 10)
        cx, hw, _ = _beam(y)
        motes.append((cx + (hr(k, 12) - 0.5) * hw * 1.4, y, 4 + hr(k, 13) * 9, 3 + hr(k, 14) * 7, hr(k, 15),
                      1 + int(hr(k, 16) * 2)))
    n = 48
    frames = []
    for i in range(n):
        cv = Canvas(light=LIGHT, img=img.copy())
        t = i / n
        for (x0, y0, ax, ay, ph, fx) in motes:
            a = 2 * math.pi * (t + ph)
            x = round(x0 + ax * math.sin(fx * a))
            y = round(y0 + ay * math.sin(a + ph * 3))
            cx, hw, _ = _beam(y)
            inside = max(0.0, 1 - abs(x - cx) / hw)                    # només es veu dins la llum
            tw = 0.5 + 0.5 * math.sin(a * 2 + ph * 7)                  # i fa pampallugues
            alpha = inside ** 0.7 * (0.35 + 0.5 * tw)
            if alpha > 0.08 and 0 <= x < W and 0 <= y < BOTTOM and not davant[x, y][3]:
                cv.flat(x, y, mix(cv.get(x, y), (255, 236, 190), alpha))
        frames.append(_diff(cv.img, img))
    return frames


HIFA = (306, 2, 84)                                # la hifa que penja del sostre: x, y de dalt, llargada


def _frames_hifa():
    """Una hifa llarga que penja del sostre i tremola amb el corrent del forat; una guspira hi baixa a poc a poc."""
    img = _base()
    hx, hy, L = HIFA
    n = 32
    frames = []
    for i in range(n):
        cv = Canvas(light=LIGHT, img=img.copy())
        t = i / n
        sway = math.sin(2 * math.pi * t) * 3.0 + math.sin(4 * math.pi * t + 1) * 0.8
        pts = []
        for k in range(L):
            s = k / L
            pts.append((hx + sway * s * s + math.sin(s * 6 + t * 2 * math.pi) * 0.6 * s, hy + k))
        for k, (x, y) in enumerate(pts):
            cv.put(x, y, CREAM, 3.6 - k / L * 1.0, lit=0)                          # una hifa blanquinosa, al llum
            if k < L * 0.4:
                cv.put(x + 1, y, CREAM, 2.4, lit=0)
        x, y = pts[-1]
        cv.disc(x, y + 1, 1.6, 2.2, CREAM, 3.6, lit=0)                             # el pes de la punta: una espora
        g = pts[int(t * (L - 1))]
        cv.put(g[0], g[1], TURQ, 5.6, lit=0)                                        # la guspira que hi baixa
        frames.append(_diff(cv.img, img))
    return frames


ANIMS = {'pols': {'frames': _frames_pols, 'frameDuration': 130},
         'hifa': {'frames': _frames_hifa, 'frameDuration': 110}}


# ─── Capes del davant ─────────────────────────────────────────────────────

def _mask_davant(x, y):
    return _davant().getpixel((x, y))[3] > 0


@functools.lru_cache(maxsize=None)
def _arc():
    cv = Canvas(light=LIGHT, transparent=True)
    arrel_arc(cv)
    return cv.img


def _mask_arc(x, y):
    return _arc().getpixel((x, y))[3] > 0


FRONT = [{'id': 'davant_arrel', 'mask': _mask_arc, 'baseline': ARC_BASE, 'zIndex': 20},
         {'id': 'davant', 'mask': _mask_davant, 'baseline': 999, 'zIndex': 20}]


# ─── Geometria (coordenades de sala) ─────────────────────────────────────────

def _rect(*pts, pad=0):
    us, vs = [p[0] for p in pts], [p[1] for p in pts]
    return (max(0, round(min(us)) - pad), max(0, round(min(vs)) - pad), min(W - 1, round(max(us)) + pad),
            min(BOTTOM, round(max(vs)) + pad))


def _escala_a(v):
    return F / _z_de_v(v)


def _geometria():
    cx, cz, w, d, h, a = DESK
    dpt = lambda lx, y, lz: CAM.projecta(_desk_pt(lx, y, lz))[:2]  # noqa: E731
    # el radar: al plafó, a (83, 47) de 120×92
    rad_lx = -w / 2 + 83
    rad_y = h + PANEL_H - 47
    radar = _rect(dpt(rad_lx - 24, rad_y + 24, d / 2), dpt(rad_lx + 24, rad_y - 24, d / 2))
    taulell = _rect(dpt(-w / 2, 0, -d / 2), dpt(w / 2, 0, -d / 2), dpt(-w / 2, h + PANEL_H, d / 2),
                    dpt(w / 2 - 50, h + PANEL_H, d / 2), dpt(w / 2, h, d / 2))
    (fl, fb), (ll, lb) = _p(*LADDER[0]), _p(*LADDER[1])
    dx, ytop, dz = LADDER_TOP
    top = CAM.projecta((LADDER[0][0] + dx, ytop, LADDER[0][1] + dz))
    peu = (round((fl + ll) / 2) + 14, fb + 14)
    fx, fy = _cap_fil()
    things = {
        'escala': {'rect': _rect((fl - 6, fb + 6), (ll + 6, lb), (top[0] - 6, max(0, top[1]))), 'walk': peu},
        'tauler': {'rect': taulell, 'walk': (round(dpt(-w / 2, 0, -d / 2)[0]) - 6, round(dpt(-w / 2, 0, -d / 2)[1]) + 16)},
        'radar': {'rect': radar, 'walk': (round(dpt(-10, 0, -d / 2)[0]), round(dpt(-10, 0, -d / 2)[1]) + 14)},
        'corn': {'rect': (566, 80, 630, 124), 'walk': (560, 226)},
        'fils_paret': {'rect': (0, 18, 196, 150), 'walk': (150, 190)},
        'fil_saba': {'rect': (fx - 24, fy - 4, fx + 6, fy + 46), 'walk': (fx - 26, fy + 52)},
    }
    for n, x in enumerate(ROOTS_X, start=1):
        b = round(base(x))
        things[f'arrel_{n}'] = {'rect': (x - 13, 12, x + 13, b + 4), 'walk': (x + 2, b + 22)}
    # el terra on es camina: del fons fins a baix, sense el taulell ni el racó de l'esquerra
    fl_ = dpt(-w / 2 - 4, 0, -d / 2 - 4)
    fr_ = dpt(w / 2 + 2, 0, -d / 2 - 4)
    walk = [(40, 222), (70, 186), (110, 176), (440, 174), (round(fl_[0]) - 4, round(fl_[1]) - 2),
            (round(fr_[0]), round(fr_[1]) + 2), (600, 236), (606, BOTTOM - 1), (34, BOTTOM - 1)]
    v_top, v_bot = min(p[1] for p in walk), max(p[1] for p in walk)
    espora = (round(fl_[0]) - 46, round(fl_[1]) + 10)
    beam_foot = (BEAM[1][0], BEAM[1][1])
    return {
        'things': things,
        'spawns': {'iri': peu, 'espora': espora},
        'walkable': walk,
        # l'arrel en arc no es trepitja: s'hi fa la volta
        'forats': [[(round((ARC[0][0] + ARC[2][0]) / 2 + ((ARC[2][0] - ARC[0][0]) / 2 + 2) * math.cos(a * math.pi / 5)),
                     round(ARC_BASE + 4 * math.sin(a * math.pi / 5))) for a in range(10)]],
        'floorSquash': 0.4,
        'regions': [{'id': 'perspectiva', 'active': True, 'scaleEnabled': True, 'scaleWalkSpeed': True,
                     'scaleTop': round(_escala_a(v_top - 2), 3), 'scaleBottom': round(_escala_a(v_bot + 2), 3),
                     'points': [(0, v_top - 2), (W - 1, v_top - 2), (W - 1, v_bot + 2), (0, v_bot + 2)]}],
        # L'ombra de contacte: la llum dominant és el raig del forat (el punt de terra on toca).
        'characterShadow': {'enabled': True, 'color': '#0a0604', 'alpha': 0.45, 'squash': 0.38, 'core': 0.6,
                            'light': {'x': beam_foot[0], 'y': beam_foot[1], 'stretch': 0.7, 'reach': 150}},
        'characterLights': {
            'ambient': '#7a6656',
            'lights': [{'x': 240, 'y': 40, 'radius': 300, 'color': '#ffd79a', 'intensity': 1.1},
                       {'x': _p(255, 466, 196)[0], 'y': _p(255, 466, 196)[1], 'radius': 200, 'color': '#ffc878',
                        'intensity': 0.9}],
        },
    }


GEOMETRIA = _geometria()
