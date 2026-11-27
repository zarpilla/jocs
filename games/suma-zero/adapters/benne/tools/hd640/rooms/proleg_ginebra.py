"""
El pròleg (cinemàtica), a 640×360. EN 3D (hd640/tres_d.py), a 1×: Ginebra de nit, la seu del Banc Central Mundial
Unificat, vista des de la vora del llac.

Un contrapicat: la càmera és arran d'aigua, al moll, i mira amunt la torre del banc, que és a l'altra banda de la
rada, en 3/4 (el davant, amb la pantalla gegant, i el costat que fuig cap a l'esquerra; les verticals convergeixen
cap amunt):
  - la **torre de vidre** damunt d'un **sòcol de pedra** amb el vestíbul encès, el coronament amb «BCMU» daurat, l'antena
    amb el llum vermell i les finestres de qui encara treballa; a la façana del davant, la **pantalla**: de primer, el
    logotip del banc; després, el Director Bonfill grava l'anunci;
  - el **moll de l'altra banda** fuig cap a l'esquerra, amb les cases de mansarda i els fanals que s'empetiteixen; al
    llac, el **raig d'aigua**, il·luminat; al fons, les muntanyes retallades i la lluna;
  - el **llac**, negre i quiet, que ho emmiralla tot (trencat per les ones);
  - a primer pla, en silueta: un fanal del moll a l'esquerra, les branques d'un plàtan que pengen de dalt i un
    noray amb la corda a baix.

És una cinemàtica que avança amb cada frase (vegeu rooms/proleg_ginebra.json). Comença al pla de la portada (la capa
opaca `pis`, el fons de portada.py), que «Comença» deixa sense títol: el pols de llum surt de la parabòlica de l'Iri
cap a la torre (`senyal_va`) i el pla es fon en trama (`pis_fon`) cap a Ginebra. Les lletres del BCMU fan una espurna
(`lletres_brilla`). La pantalla s'encén (`pantalla_entra`), el Director parla (`pantalla_parla`), perd el somriure i
mira fora de camp (`pantalla_talla`, `pantalla_queixa`) i el torna a posar (`pantalla_somriu`). «Lluny. Prou lluny»:
torna el pla del pis (`pis_torna`), i al monitor s'obre una porta (`pis_porta`, `pis_festa`).
Animació de fons: `nit` (el raig, els reflexos al llac i el llum de l'antena).

El dibuix pla (la pantalla, el bust del Director, les lletres) és a proleg_ginebra_pla_comu.py. Els crèdits
(credits.py) fan servir aquesta mateixa escena, amb la pantalla apagada.
El món: x a la dreta, y amunt (0 = l'aigua), z cap al fons; la càmera és a l'origen, a 30 d'alçada.
"""
import functools
import math

import numpy as np
from PIL import Image

import hd640  # noqa: F401  (abans que cap hd.rooms: posa la llibreria a 640×360)
from hd640 import llum
from hd.pix import Light, Canvas, W, H, hr, mix
from hd.rooms.comu import outline, _diff
from hd.rooms.exterior import fbm
from hd640.rooms import proleg_ginebra_pla_comu as PL
from hd640.rooms.proleg_ginebra_pla_comu import (NIGHT, MOUNT, WATER, STONE, GLASSB, WARM, COOL, GOLD, JET,
                                                 BONFILL)  # noqa: F401  (BONFILL: el fan servir altres sales)
import hd640.rooms.portada as portada
from hd640.tres_d import Camera, Escena, Llum

LIGHT = Light(ambient=0.0, vignette=None, floor_fade=None)

# ─── La càmera i el món ─────────────────────────────────────────────────────

F = 420
# (el centre, més avall que el de la pantalla: tota la vista baixa, i les lletres del BCMU queden sota la caixa
# del narrador, que va sempre a dalt al mig, també quan té dues línies; tasca 236)
BAIXA = 42
CAM = Camera(pos=(0.0, 30.0, 0.0), yaw=0.10, pitch=-0.2, f=F, centre=(320, 200 + BAIXA))
HOR = round(CAM.projecta((0, 30, 1e7))[1])            # l'horitzó a la pantalla

TX, TZ, TA = 300.0, 1450.0, 0.32          # la torre: el centre (x, z) i el gir
TPX = 3.75                                # unitats del món per píxel de la textura de la façana
FW, FH = 150, 176                         # la textura de la façana del davant (px)
SW = 96                                   # la del costat
TW, TD, TH = FW * TPX, SW * TPX, FH * TPX  # amplada, fons i alçada del vidre
PH = 96.0                                 # el sòcol de pedra
SCR_AT = (20, 34)                         # on va la pantalla, a la textura del davant
JET_P = (-1000.0, 0.0, 2700.0)            # el raig d'aigua
JET_H = 640.0
MOON = (560, 46)

_C, _S = math.cos(TA), math.sin(TA)


def tp(lx, y, lz):
    """Un punt de la torre (coordenades locals: lx al llarg del davant, lz cap al fons) al món."""
    return (TX + lx * _C - lz * _S, y, TZ + lx * _S + lz * _C)


def _p(P):
    u, v, _ = CAM.projecta(P)
    return u, v


LLUNA = Llum((40000.0, 60000.0, 90000.0), 1e7, 0.9, power=1.0)       # la lluna, al fons a la dreta
CIUTAT = Llum((TX - 200, 20.0, TZ - 400), 900, 1.2, power=1.6)       # els fanals del moll, des de baix

SKYN = NIGHT
QUAY = [(6, 6, 10), (12, 11, 16), (20, 18, 24), (30, 27, 32), (42, 38, 42), (58, 53, 56), (78, 72, 72)]
HOUSE = [(5, 5, 12), (9, 9, 20), (14, 14, 28), (20, 20, 36), (28, 27, 46), (38, 36, 56),
         (130, 84, 30), (210, 150, 60), (250, 210, 120)]
SIL = [(1, 1, 4), (4, 4, 9), (8, 8, 15), (12, 12, 21)]
WAT = [(1, 2, 6), (3, 5, 12), (5, 8, 18), (8, 12, 25), (12, 17, 33), (18, 23, 42)]


# ─── El cel, la lluna i les muntanyes (en pantalla: són a l'infinit) ─────────

def sky(cv):
    for y in range(0, HOR + 1):
        for x in range(W):
            cv.put(x, y, SKYN, 1.3 + 3.8 * (y / HOR) ** 1.6 + (hr(x // 3, y // 3) - 0.5) * 0.2
                   + 0.8 * max(0.0, 1 - math.hypot(x - MOON[0], y - MOON[1]) / 160), lit=0)
    for i in range(150):                                                 # estrelles
        x, y = int(hr(i, 1) * W), int(hr(i, 2) * (HOR - 70))
        b = hr(i, 3)
        if math.hypot(x - MOON[0], y - MOON[1]) < 40:
            continue
        cv.flat(x, y, (200, 200, 230) if b > 0.7 else (110, 110, 150) if b > 0.25 else (70, 70, 110))
        if b > 0.95:
            for dx, dy in ((-1, 0), (1, 0), (0, -1), (0, 1)):
                cv.flat(x + dx, y + dy, (90, 90, 130))
    mx, my = MOON                                                        # la lluna, petita, amb taques
    cv.glow(mx, my, 34, (180, 190, 230), 0.28)
    cv.disc(mx, my, 8, 8, [(200, 200, 190), (236, 234, 220), (250, 250, 240)], lambda nx, ny: 1.4 - nx * 0.8, lit=0)
    for dx, dy, r in ((-3, -2, 1.6), (2, 2, 1.2), (-1, 4, 1.0), (3, -4, 0.8)):
        cv.disc(mx + dx, my + dy, r, r, [(186, 184, 176), (214, 212, 200)], 0.4 + dx * 0.1, lit=0)


def mountains(cv):
    """El Salève i companyia, retallats contra el cel, neu a les crestes; una franja de llums de la riba de lluny."""
    for x in range(W):
        u = x / 1.33
        h1 = HOR - 46 - 10 * math.sin(u / 47) - 6 * math.sin(u / 13 + 1) - 4 * hr(x // 8, 4) + math.sin(x / 3.3) * 0.7
        h2 = HOR - 24 - 6 * math.sin(u / 31 + 2) - 3 * hr(x // 5, 5)
        for y in range(int(h1), HOR + 1):
            depth = y - h1
            snow = depth < 2.6 + math.sin(x / 5) and math.sin(u / 47) > 0.4
            if snow:
                cv.put(x, y, [(40, 46, 70), (60, 66, 90), (100, 106, 130)], 1.2 - depth * 0.3 + (0.4 if x % 7 < 3 else 0),
                       lit=0)
            else:
                cv.put(x, y, MOUNT, 1.6 - depth * 0.02 + (0.3 if hr(x // 4, y // 6, 9) > 0.8 else 0), lit=0)
        for y in range(int(h2), HOR + 1):
            cv.put(x, y, MOUNT, 0.9, lit=0)
        if hr(x, 77) > 0.7:                                              # la riba de lluny: llumets
            cv.flat(x, HOR - 1 - int(hr(x, 78) * 2), (200, 160, 100) if hr(x, 79) > 0.3 else (140, 170, 210))


# ─── La torre del BCMU (textures planes) ────────────────────────────────────

def _vidre(w, h, seed, apagades=False, sheen_at=24):
    """Una façana de vidre: forjats, muntants, el reflex de la lluna en diagonal i les finestres de qui treballa."""
    cv = Canvas(w=w, h=h, light=LIGHT)
    floor_h, bay = 8, 10
    for y in range(h):
        for x in range(w):
            floor = y % floor_h == 0
            mull = x % bay == 0
            sheen = max(0, 1 - abs(x - sheen_at - y * 0.3) / 13) * 1.4
            lvl = 2.2 + y / 260 + sheen + (1.0 if floor else 0) + (0.5 if mull else 0)
            cv.put(x, y, GLASSB, lvl, lit=0)
    for fy in range(2, h - 4, floor_h):
        for fx in range(2, w - 6, bay):
            r = hr(fx, fy, seed)
            if r > (0.72 if not apagades else 0.9):
                ramp = COOL if hr(fx, fy, seed + 2) > 0.8 else WARM
                cv.rect(fx, fy + 1, fx + 7, fy + 5, ramp, lambda px, py: 2.0 + hr(fx, fy, 1) - (py - fy) * 0.15, lit=0)
                if hr(fx, fy, seed + 3) > 0.5:                              # algú a la taula, a contrallum
                    sx = fx + 2 + int(hr(fx, fy, seed + 4) * 3)
                    cv.rect(sx, fy + 3, sx + 1, fy + 5, [(20, 14, 10)], 0, lit=0)
                    cv.flat(sx, fy + 2, (20, 14, 10))
                elif hr(fx, fy, seed + 5) > 0.5:                            # una persiana mig abaixada
                    for py in range(fy + 1, fy + 3):
                        cv.tint(fx, py, fx + 7, py, (20, 16, 20), 0.5 if py % 2 else 0.3)
    return cv


SCR_BOX = (PL.SCREEN[0] - 2, PL.SCREEN[1] - 2, PL.SCREEN[2] + 3, PL.SCREEN[3] + 3)   # la pantalla i el marc


def _screen_img(**kw):
    """La pantalla del dibuix pla (proleg_ginebra_pla_comu.screen), retallada, sense el halo (el fa la llum)."""
    tmp = Canvas(light=LIGHT)
    PL.screen(tmp, **kw)
    return tmp.img.crop(SCR_BOX)


def _apagada_img():
    from hd640.rooms import credits_pla_comu as CR
    tmp = Canvas(light=LIGHT)
    CR.pantalla_apagada(tmp)
    return tmp.img.crop(SCR_BOX)


@functools.lru_cache(maxsize=None)
def _vidre_davant(apagades=False):
    return _vidre(FW, FH, 9, apagades).img


@functools.lru_cache(maxsize=None)
def _vidre_costat(apagades=False):
    cv = _vidre(SW, FH, 19, apagades, sheen_at=70)
    for X, Y, x, y in cv.pixels():                                       # el costat, a l'ombra
        r, g, b, a = cv.P[X, Y]
        cv.P[X, Y] = (r * 3 // 4, g * 3 // 4, b * 4 // 5, a)
    return cv.img


def facana(variant='pròleg', **screen_kw):
    """La façana del davant: el vidre i la pantalla. `variant`: 'pròleg' (la pantalla amb `screen_kw`) o 'crèdits'
    (apagada, amb el rètol de «FORA DE SERVEI», i menys finestres enceses)."""
    img = _vidre_davant(variant == 'crèdits').copy()
    scr = _apagada_img() if variant == 'crèdits' else _screen_img(**screen_kw)
    img.alpha_composite(scr, SCR_AT)
    return img


@functools.lru_cache(maxsize=None)
def _lletres_img():
    """«BCMU» en lletres daurades grosses (les del dibuix pla), damunt del coronament."""
    tmp = Canvas(w=80, h=40, light=LIGHT, transparent=True)
    PL.big_word(tmp, 'BCMU', 40, 4, 3)
    bb = tmp.img.getbbox()
    return tmp.img.crop((bb[0] - 1, bb[1] - 1, bb[2] + 1, bb[3] + 1))


LW = 340.0                                                               # l'amplada de les lletres al món


@functools.lru_cache(maxsize=None)
def _socol_img():
    """El davant del sòcol de pedra: carreus, el vestíbul encès amb les columnes i el vigilant."""
    w, h = 210, int(PH / TPX * 1.0) + 1
    cv = Canvas(w=w, h=h, light=LIGHT)
    for y in range(h):
        for x in range(w):
            cv.put(x, y, STONE, 2.6 + (0.8 if x % 21 < 4 else 0) - y * 0.03 + (0.3 if y % 7 == 0 else 0)
                   + (hr(x // 2, y // 2, 3) - 0.5) * 0.3, lit=0)
    cv.rect(0, 0, w - 1, 2, STONE, lambda x, y: 4.2 + (0.6 if y == 0 else 0), lit=0)
    m = w // 2
    cv.rect(m - 20, 9, m + 20, h - 1, WARM, lambda x, y: 1.8 + (0.4 if y > h - 8 else 0), lit=0)   # el vestíbul
    cv.rect(m - 4, 12, m + 4, 15, GOLD, 2.6, lit=0)                                                 # el logotip
    cv.flat(m - 8, 18, (30, 20, 10))                                                                # el vigilant
    cv.rect(m - 9, 19, m - 7, h - 2, [(30, 20, 10)], 0, lit=0)
    for cx in (m - 14, m - 1, m + 12):
        cv.rect(cx, 9, cx + 1, h - 1, STONE, 1.2, lit=0)
    cv.hline(m - 22, m + 22, 8, STONE, 4.6, lit=0)
    return cv.img


@functools.lru_cache(maxsize=None)
def _bandera_img():
    cv = Canvas(w=16, h=40, light=LIGHT, transparent=True)
    cv.vline(0, 1, 39, STONE, 3.4, lit=0)
    cv.flat(0, 0, GOLD[3])
    cv.rect(1, 1, 13, 9, GOLD, lambda x, y: 2.4 + (0.6 if y == 1 else 0) - (0.5 if y == 9 else 0), lit=0)
    cv.rect(5, 3, 8, 6, GOLD, 1.2, lit=0)
    return cv.img


def torre(e, variant='pròleg', screen_kw=None):
    a, b = TW / 2, TD / 2
    # el moll de l'altra banda, on s'assenta la torre
    e.caixa_girada('moll', TX - 200, TZ + 200, TW + 1600, TD + 900, 14, TA, QUAY, 2.2, y0=-6,
                   cares={'dalt': {'ramp': QUAY, 'lvl': 2.6}, 'davant': {'ramp': QUAY, 'lvl': 1.6},
                          'esquerra': {'ramp': QUAY, 'lvl': 1.2}})
    # el sòcol de pedra
    sa, sb = a + 60, b + 50
    e.quad('socol', tp(-sa, PH + 8, -sb), tp(sa, PH + 8, -sb), tp(sa, 8, -sb), tp(-sa, 8, -sb),
           tex=(_socol_img(), (0, 0, _socol_img().width, _socol_img().height)))
    e.quad('socol', tp(-sa, PH + 8, sb), tp(-sa, PH + 8, -sb), tp(-sa, 8, -sb), tp(-sa, 8, sb),
           ramp=STONE, lvl=lambda s, t, P: 1.8 + (0.6 if int(s) % 70 < 12 else 0) - t * 0.004)
    e.caixa_girada('socol', TX, TZ, 2 * sa + 16, 2 * sb + 16, 6, TA, STONE, 4.0, y0=PH + 8,
                   cares={'dalt': {'ramp': STONE, 'lvl': 4.4}, 'davant': {'ramp': STONE, 'lvl': 4.6},
                          'esquerra': {'ramp': STONE, 'lvl': 3.4}})
    y0 = PH + 14
    # el vidre: el costat (a l'esquerra, a l'ombra) i el davant, amb la pantalla
    tex_c = _vidre_costat(variant == 'crèdits')
    e.quad('costat', tp(-a, y0 + TH, b), tp(-a, y0 + TH, -b), tp(-a, y0, -b), tp(-a, y0, b), tex=(tex_c, (0, 0, SW, FH)))
    tex_d = facana(variant, **(screen_kw or {}))
    e.quad('facana', tp(-a, y0 + TH, -b), tp(a, y0 + TH, -b), tp(a, y0, -b), tp(-a, y0, -b), tex=(tex_d, (0, 0, FW, FH)))
    # el coronament de pedra
    yc = y0 + TH
    e.caixa_girada('coronament', TX, TZ, TW + 24, TD + 24, 34, TA, STONE, 3.2, y0=yc,
                   cares={'dalt': {'ramp': STONE, 'lvl': 2.4}, 'davant': {'ramp': STONE, 'lvl': lambda s, t, P: 3.6 - t * 0.04
                                                                          + (0.6 if int(s) % 22 < 3 else 0)},
                          'esquerra': {'ramp': STONE, 'lvl': 2.2}})
    # les lletres, dretes damunt del coronament, i l'antena
    li = _lletres_img()
    lh = LW * li.height / li.width
    e.quad('lletres', tp(-LW / 2, yc + 40 + lh, -b + 30), tp(LW / 2, yc + 40 + lh, -b + 30), tp(LW / 2, yc + 40, -b + 30),
           tp(-LW / 2, yc + 40, -b + 30), tex=(li, (0, 0, li.width, li.height)))
    for lx in (-LW / 2 + 30, LW / 2 - 30):
        e.cable('lletres_pal', [tp(lx, yc + 34, -b + 32), tp(lx, yc + 42, -b + 32)], STONE, 2.0, gruix=5)
    e.cable('antena', [tp(a - 50, yc + 34, 0), tp(a - 50, yc + 200, 0)], STONE, 3.0, gruix=4)
    for k in range(4):
        e.cable('antena', [tp(a - 64, yc + 70 + k * 30, 0), tp(a - 36, yc + 70 + k * 30, 0)], STONE, 2.4, gruix=2)
    # la bandera, al sòcol (no fa vent per als bancs)
    e.sprite('bandera', _bandera_img(), (0, 39), tp(a + 40, PH + 14, -b - 20), escala_img=TPX * 1.4)


def antenna_xy():
    return _p(tp(TW / 2 - 50, PH + 14 + TH + 34 + 204, 0))


# ─── El moll de l'altra banda, amb les cases ────────────────────────────────

SHORE = [(-5200.0, 6800.0), (-2400.0, 3400.0), (TX - TW / 2 - 300, TZ - 60)]       # de lluny cap a la torre
SHORE_R = [(TX + TW / 2 + 260, TZ + 200), (2600.0, 3800.0)]                        # i cap a la dreta


def _cases():
    """Cases de cinc o sis pisos amb mansarda al llarg del moll: (cx, cz, ample, fons, alt, gir, llavor)."""
    out = []
    for segs, side in ((SHORE, -1), (SHORE_R, 1)):
        for (ax, az), (bx, bz) in zip(segs, segs[1:]):
            L = math.hypot(bx - ax, bz - az)
            ang = math.atan2(bz - az, bx - ax)
            n = int(L // 190)
            for k in range(n):
                t = (k + 0.5) / n
                seed = int(ax) // 7 + k * 13
                w = 160 + hr(seed, 1) * 40
                cx, cz = ax + (bx - ax) * t, az + (bz - az) * t
                # una mica enrere del moll
                cx -= math.sin(ang) * 120 * side * -1
                cz += math.cos(ang) * 120
                out.append((cx, cz, w, 180, 150 + hr(seed, 2) * 110, -ang, seed))
    return out


def _casa_lvl(seed, base=1.6):
    def lvl(s, t, P):
        col, fl = int(s // 28), int(t // 34)
        a, b_ = s % 28, t % 34
        v = base + (hr(int(s // 6), int(t // 8), seed) - 0.5) * 0.4
        if 8 <= a < 20 and 8 <= b_ < 26:
            if hr(col, fl, seed) > 0.62:
                return 7.2 + (hr(col, fl, seed + 1) - 0.5)
            return 0.4
        return v
    return lvl


def cases(e):
    for (cx, cz, w, d, h, ang, seed) in sorted(_cases(), key=lambda c: -c[1]):
        e.caixa_girada('cases', cx, cz, w, d, h, ang, HOUSE, 1.6,
                       cares={'davant': {'ramp': HOUSE, 'lvl': _casa_lvl(seed, 1.8)},
                              'esquerra': {'ramp': HOUSE, 'lvl': _casa_lvl(seed + 3, 1.0)},
                              'dreta': {'ramp': HOUSE, 'lvl': _casa_lvl(seed + 5, 1.2)},
                              'dalt': {'ramp': HOUSE, 'lvl': 2.6}})
        # la mansarda: una teulada més estreta
        e.caixa_girada('cases', cx, cz, w - 30, d - 30, 40, ang, HOUSE, 2.4, y0=h,
                       cares={'dalt': {'ramp': HOUSE, 'lvl': 3.0}, 'davant': {'ramp': HOUSE, 'lvl': 2.6},
                              'esquerra': {'ramp': HOUSE, 'lvl': 1.8}, 'dreta': {'ramp': HOUSE, 'lvl': 1.8}})
    # el moll, de pedra, al llarg de la riba
    for segs in (SHORE, SHORE_R):
        for (ax, az), (bx, bz) in zip(segs, segs[1:]):
            L = math.hypot(bx - ax, bz - az)
            ang = math.atan2(bz - az, bx - ax)
            e.caixa_girada('moll', (ax + bx) / 2 - math.sin(ang) * -60, (az + bz) / 2 + math.cos(ang) * 60, L + 40, 220,
                           14, -ang, QUAY, 2.0, y0=-6, cares={'davant': {'ramp': QUAY, 'lvl': 1.4},
                                                            'dalt': {'ramp': QUAY, 'lvl': 2.4}})


def _fanals():
    out = []
    for segs in (SHORE, SHORE_R):
        for (ax, az), (bx, bz) in zip(segs, segs[1:]):
            L = math.hypot(bx - ax, bz - az)
            for k in range(int(L // 150)):
                t = (k + 0.5) / int(L // 150)
                out.append((ax + (bx - ax) * t, 0.0, az + (bz - az) * t - 50))
    return out


# ─── El primer pla ──────────────────────────────────────────────────────────

FANAL_P = (-240.0, 8.0, 440.0)
QUAY_EDGE = ((-420.0, 540.0), (60.0, 150.0))           # la vora del nostre moll: de l'esquerra al fons cap a baix


def primer_pla(e):
    """El nostre moll a baix a l'esquerra (la vora de pedra en diagonal), un fanal, un noray amb la corda, i les
    branques d'un plàtan que pengen de dalt: tot en silueta."""
    (ax, az), (bx, bz) = QUAY_EDGE
    # el moll: el terra (fins a la càmera) i la cara que dona a l'aigua
    e.quad('primer_pla', (ax, 8, az), (bx, 8, bz), (bx - 300, 8, bz - 120), (ax - 300, 8, az - 120),
           ramp=SIL, lvl=lambda s, t, P: 1.2 + (1.6 if t < 5 else 0) + (hr(int(s // 22), int(t // 22), 5) - 0.5) * 0.5
           - (0.6 if int(s) % 44 < 2 or int(t) % 44 < 2 else 0), dues_cares=True)
    e.quad('primer_pla', (ax, 8, az), (bx, 8, bz), (bx, -12, bz), (ax, -12, az), ramp=SIL, lvl=0.6, dues_cares=True)
    fx, fy, fz = FANAL_P
    e.tub('primer_pla', (fx, 190, fz), (fx, fy + 20, fz), 4.0, SIL, 1.4, brides=50, llum_dir=(0.8, 0.2))
    e.tub('primer_pla', (fx, fy + 22, fz), (fx, fy, fz), 8, SIL, 1.2, llum_dir=(0.8, 0.2))         # el peu
    e.caixa('fanal', fx - 9, fx + 9, 190, 214, fz - 9, fz + 9, LANTERN, 2.6,
            cares={'davant': {'ramp': LANTERN, 'lvl': 3.0}, 'dreta': {'ramp': LANTERN, 'lvl': 2.4},
                   'esquerra': {'ramp': LANTERN, 'lvl': 2.0}})                                       # el fanal, encès
    e.caixa('primer_pla', fx - 12, fx + 12, 214, 219, fz - 12, fz + 12, SIL, 1.4)
    e.cable('primer_pla', [(fx, 219, fz), (fx, 230, fz)], SIL, 1.2, gruix=2)
    # el noray, arran de la vora, i la corda que se'n va a l'aigua
    nx, nz = -150.0, 345.0
    e.tub('primer_pla', (nx, 8, nz), (nx, 22, nz), 5, SIL, 1.8, llum_dir=(0.6, 0.6))
    e.tub('primer_pla', (nx, 22, nz), (nx, 25, nz), 6.5, SIL, 2.6, llum_dir=(0.6, 0.6))
    e.cable('primer_pla', [(nx + 4, 20, nz), (nx + 30, 12, nz + 20), (nx + 70, 3, nz + 60), (nx + 110, 0, nz + 120)], SIL,
            1.6, gruix=2.2)
    # les branques del plàtan, des de dalt a l'esquerra

    def branca(P, a, L, n, seed):
        if n == 0 or L < 6:
            FULLES.append(P)
            return
        Q = (P[0] + math.cos(a) * L, P[1] + math.sin(a) * L, P[2] + (hr(seed, 9) - 0.5) * 20)
        e.cable('branques', [P, Q], SIL, 1.2, gruix=max(1.2, n * 1.6))
        for k, da in enumerate((-0.5, 0.45)):
            branca(Q, a + da + (hr(seed, k) - 0.5) * 0.4, L * 0.7, n - 1, seed * 3 + k + 1)
    FULLES.clear()
    branca((-470.0, 360.0, 330.0), -0.3, 130, 5, 3)
    branca((-430.0, 400.0, 300.0), 0.05, 110, 4, 8)


LANTERN = [(40, 28, 16), (120, 86, 40), (200, 150, 80), (250, 214, 140)]


FULLES = []


def fulles(cv, e):
    """Fulles de plàtan als extrems de les branques: taques fosques, amb una vora que agafa la lluna."""
    idx = e._idx_de('branques')
    for i, P in enumerate(FULLES):
        u, v = _p(P)
        k = CAM.escala(P)
        for j in range(5):
            du = (hr(i, j, 1) - 0.5) * 22 * k
            dv = (hr(i, j, 2) - 0.5) * 16 * k
            r = (5 + hr(i, j, 3) * 5) * k
            cv.disc(u + du, v + dv, r, r * 0.6, SIL, lambda nx, ny: 0.8 + (2.2 if nx + ny * 0.3 > 0.55 else 0), lit=0)
            for y in range(int(v + dv - r), int(v + dv + r) + 1):
                for x in range(int(u + du - r), int(u + du + r) + 1):
                    if 0 <= x < W and 0 <= y < H and cv.P[x, y][:3] in [c for c in SIL]:
                        e.amo[y * W + x] = idx


# ─── Composició ────────────────────────────────────────────────────────────

def _aigua(s, t, P):
    x, z = P[0], P[2]
    return 1.6 + math.sin(z / 9 + math.sin(x / 70) * 2) * 0.35 + (fbm(x / 160, z / 40, 31) - 0.5) * 0.8


def escena(cv, variant='pròleg', screen_kw=None):
    sky(cv)
    mountains(cv)
    e = Escena(cv, CAM, [LLUNA, CIUTAT], ambient=-0.3)
    e.quad('aigua', (-40000, 0, 30000), (40000, 0, 30000), (40000, 0, 60), (-40000, 0, 60), ramp=WAT, lvl=_aigua)
    cases(e)
    torre(e, variant, screen_kw)
    primer_pla(e)
    fulles(cv, e)
    return e


def fanals(cv, e):
    W_ = cv.w
    for P in _fanals():
        u, v = _p((P[0], 26, P[2]))
        U, V = round(u), round(v)
        bu, bv = _p((P[0], 8, P[2]))
        if not (0 <= U < W and 0 <= V < H):
            continue
        if e.ids[e.amo[V * W_ + U]] not in ('', 'cases', 'moll', 'aigua'):
            continue
        cv.flat(U, V, (255, 220, 150))
        if CAM.escala(P) > 0.2:
            cv.flat(U, V + 1, (200, 150, 90))
        cv.glow(u, v, 3 + 10 * CAM.escala(P), (255, 210, 140), 0.4)


def jet(cv, e, frame=0):
    """El raig d'aigua, il·luminat, damunt del llac (en pantalla, de la mida que toca a aquella distància)."""
    bx, by = _p(JET_P)
    _, top = _p((JET_P[0], JET_H, JET_P[2]))
    k = CAM.escala(JET_P) / 0.16
    ok = lambda x, y: e.ids[e.amo[int(y) * W + int(x)]] in ('', 'aigua', 'cases', 'moll')   # noqa: E731
    bx = round(bx)
    for y in range(int(top), int(by)):
        t = (y - top) / (by - top)
        wdt = (1 + t * 6.5 + (2.6 if y < top + 13 else 0)) * k
        for x in range(int(bx - wdt), int(bx + wdt) + 1):
            if 0 <= x < W and 0 <= y < H and ok(x, y) and hr(x, y + frame * 4, 4) > 0.25 + t * 0.3:
                cv.put(x, y, JET, 3.6 - abs(x - bx) / max(1, wdt) * 1.6 - t * 0.8, lit=0)
    for j in range(110):                                                 # la ploma que cau, a la dreta (el vent)
        a = hr(j, frame, 5)
        x = bx + 3 + int(a * 26 * k)
        y = top + int(a * a * 56 * k) + int(hr(j, 6, 7) * 8)
        if 0 <= x < W and 0 <= y < H and ok(x, y):
            cv.flat(x, y, JET[2] if hr(j, 8) > 0.5 else JET[3])
    for j in range(30):                                                  # l'escuma a la base
        x = bx + int((hr(j, frame, 11) - 0.5) * 18 * k)
        y = round(by) - 1 - int(hr(j, 12) * 3)
        if 0 <= x < W and 0 <= y < H and ok(x, y):
            cv.flat(x, y, JET[3])
    cv.glow(bx, top + 40, 40, (190, 210, 240), 0.12)


def antenna(cv, on=True):
    ax, ay = antenna_xy()
    cv.rect(round(ax) - 1, round(ay) - 1, round(ax) + 1, round(ay), [(90, 20, 20), (255, 60, 50)], 1 if on else 0, lit=0)
    if on:
        cv.glow(ax, ay, 8, (255, 60, 50), 0.4)


@functools.lru_cache(maxsize=None)
def _vora():
    """Per a cada columna, la primera fila de llac (on toca el que s'hi emmiralla) i la màscara de l'aigua."""
    _, e = _base('pròleg')
    amo = np.frombuffer(e.amo, dtype=np.uint16).reshape(H, W)
    water = amo == e.ids.index('aigua')
    edge = np.full(W, H, dtype=np.int32)
    for x in range(W):
        ys = np.nonzero(water[:, x])[0]
        if len(ys):
            edge[x] = ys[0]
    return edge, water


def reflex(img, frame=0, variant='pròleg'):
    """El llac emmiralla el que té a sobre (a cada columna, des de la vora), trencat per les ones."""
    edge, water = _vora()
    a = np.asarray(img, dtype=np.float32).copy()
    src = a.copy()
    yy, xx = np.mgrid[0:H, 0:W]
    d = yy - edge[None, :]
    wob = np.round(np.sin(yy * 0.52 + frame * 0.8) * np.minimum(4, np.maximum(d, 0) / 10)).astype(int)
    sx = np.clip(xx + wob, 0, W - 1)
    sy = np.clip(2 * edge[None, :] - yy - 1, 0, H - 1)
    s = src[sy, sx, :3]
    lum = s.sum(axis=2)
    k = np.clip(1 - d / 150, 0, 1) * np.where(lum > 240, 0.55, 0.22)
    k = k * (((yy + xx // 4) % 2 == 0) | (lum > 400))                    # a ratlles (les ones)
    k = k * water * (d >= 0)
    a[..., :3] = a[..., :3] * (1 - k[..., None]) + s * k[..., None]
    # el camí de la lluna: espurnes en una franja que s'eixampla cap a nosaltres
    dm = yy - HOR
    band = np.abs(xx - MOON[0] - np.sin(yy * 0.7 + frame) * 2) < 3 + dm * 0.22
    rnd = _soroll(frame)
    sp = band & water & (dm > 1) & (rnd > 0.55 + np.abs(xx - MOON[0]) / (3 + dm * 0.22) * 0.35) & ((yy % 2) == 0)
    a[sp, :3] = a[sp, :3] * 0.3 + np.array([200, 205, 230], dtype=np.float32) * 0.7
    return Image.fromarray(a.clip(0, 255).astype(np.uint8), 'RGBA').copy()


@functools.lru_cache(maxsize=None)
def _soroll(frame):
    yy, xx = np.mgrid[0:H, 0:W]
    return ((np.sin((xx // 2) * 12.9898 + yy * 78.233 + (frame % 3) * 37.719) * 43758.5453) % 1.0)


def _fx():
    sx, sy = _p(tp(-TW / 2 + (SCR_AT[0] + 55) * TPX, PH + 14 + TH - (SCR_AT[1] + 42) * TPX, -TD / 2))
    lx, ly = _p(tp(0, PH / 2, -TD / 2 - 60))
    light = [llum.wash(sx, sy, 150, (110, 150, 240), k=0.4, air=0.02, squash=0.9),        # la pantalla
             llum.wash(lx, ly, 70, (255, 200, 120), k=0.6, air=0.04, squash=1.6),         # el vestíbul
             llum.wash(sx, HOR + 40, 70, (90, 130, 230), k=0.5, air=0.08, squash=0.35,
                       box=(0, HOR + 8, W, H))]                                           # i la pantalla, al llac
    tone = [llum.grade(contrast=1.08, pivot=40, sat=1.1, lift=(2, 3, 9))]
    # (la pantalla no fa bloom: si no, la cara del Director es crema)
    yc = PH + 14 + TH
    pts = [_p(tp(-TW / 2 + fx * TPX, yc - fy * TPX, -TD / 2)) for fx in (SCR_AT[0], SCR_AT[0] + 111)
           for fy in (SCR_AT[1], SCR_AT[1] + 87)]
    x0, x1 = min(p[0] for p in pts), max(p[0] for p in pts)
    y0, y1 = min(p[1] for p in pts), max(p[1] for p in pts)
    bloom = [llum.bloom(thr=150, radii=((2, 0.45), (8, 0.35), (22, 0.18)),
                        mask=lambda x, y: 1 - 0.85 * ((x >= x0) & (x <= x1) & (y >= y0) & (y <= y1)))]
    return light, bloom, tone


def _amb_llum(img):
    light, bl, tone = _fx()
    return llum.apply(img, light + bl + tone, scale=1)


@functools.lru_cache(maxsize=None)
def _base(variant='pròleg'):
    """L'escena sense els efectes que es mouen (el raig, el reflex, l'antena) → (imatge, Escena)."""
    cv = Canvas(light=LIGHT)
    e = escena(cv, variant)
    fanals(cv, e)
    return cv.img.copy(), e


def _acaba(img, frame=0, variant='pròleg', on=True):
    """Hi posa el raig, l'antena, el reflex al llac i la llum."""
    _, e = _base(variant)
    cv = Canvas(light=LIGHT, img=img.copy())
    jet(cv, e, frame)
    antenna(cv, on)
    return _amb_llum(reflex(cv.img, frame, variant))


@functools.lru_cache(maxsize=None)
def base_llum(variant='pròleg'):
    return _acaba(_base(variant)[0], 0, variant)


def bg(cv):
    cv.img.paste(base_llum())
    cv.P = cv.img.load()


PROPS = {}


def nit_frames(variant='pròleg'):
    return [_diff(_acaba(_base(variant)[0], i, variant, on=i % 3 != 2), base_llum(variant)) for i in range(6)]


def _empty():
    return Canvas(light=LIGHT, transparent=True).img


def _sense_llac(img):
    """Treu d'una capa el llac (el reflex quiet desentonaria amb les ones de `nit`)."""
    _, water = _vora()
    a = np.array(img)
    a[water, 3] = 0
    return Image.fromarray(a)


def _screen(**kw):
    img, e = _base()
    img = img.copy()
    img.alpha_composite(e.capa(facana(**kw), {'facana'}))
    return _sense_llac(_diff(_acaba(img), base_llum()))


D = {'state': 'director'}


def _screen_clip(steps):
    return lambda: [_screen(**k) if k is not None else _empty() for k in steps]


PANTALLA = {
    'pantalla': {'frames': lambda: [_empty()], 'frameDuration': 1000, 'loop': False, 'zIndex': 2},
    'pantalla_entra': {'frames': _screen_clip([{'fx': 'glitch'}, {'fx': 'soroll'}, {'fx': 'soroll2'}, {'fx': 'ratlla'},
                                               {**D, 'fx': 'mig'}, {**D, 'fx': 'flaix'}, {**D}]),
                       'frameDuration': 100, 'loop': False, 'prop': 'pantalla'},
    'pantalla_parla': {'frames': _screen_clip([{**D}, {**D, 'talk': True}]), 'frameDuration': 170, 'prop': 'pantalla'},
    'pantalla_quiet': {'frames': _screen_clip([{**D}]), 'frameDuration': 1000, 'loop': False, 'prop': 'pantalla'},
    'pantalla_talla': {'frames': _screen_clip([{**D}, {**D, 'smile': False}, {**D, 'smile': False},
                                               {**D, 'smile': False, 'look': True}]),
                       'frameDuration': 140, 'loop': False, 'prop': 'pantalla'},
    'pantalla_queixa': {'frames': _screen_clip([{**D, 'smile': False, 'look': True},
                                                {**D, 'smile': False, 'look': True, 'talk': True}]),
                        'frameDuration': 170, 'prop': 'pantalla'},
    'pantalla_somriu': {'frames': _screen_clip([{**D, 'smile': False, 'look': True}, {**D, 'smile': False}, {**D}]),
                        'frameDuration': 160, 'loop': False, 'prop': 'pantalla'},
}


# ─── L'espurna de les lletres ──────────────────────────────────────────────

def _glint_frames():
    """Una espurna travessa en diagonal les lletres daurades del capdamunt (i acaba buida)."""
    src = _lletres_img()
    a0 = np.array(src).astype(int)
    h, w = a0.shape[:2]
    gold = a0[:, :, 3] > 0
    img, e = _base()
    frames = []
    for i in range(12):
        p = -6 + (w + 12) * i / 11
        out = a0.copy()
        for y in range(h):
            for x in range(w):
                if not gold[y, x]:
                    continue
                dd = abs(x + y * 0.7 - p)
                k = 1.0 if dd < 2 else 0.5 if dd < 4 else 0
                if k:
                    out[y, x, :3] = a0[y, x, :3] + (np.array([255, 252, 230]) - a0[y, x, :3]) * k
        if i == 6:                                                       # i una estrelleta al mig
            cx, cy = w // 2 + 8, 1
            for dx, dy in ((0, 0), (-1, 0), (1, 0), (0, -1), (0, 1), (-2, 0), (2, 0)):
                if 0 <= cy + dy < h and 0 <= cx + dx < w:
                    out[cy + dy, cx + dx] = [255, 255, 240, 255] if abs(dx) + abs(dy) < 2 else [250, 220, 140, 255]
        lay = img.copy()
        lay.alpha_composite(e.capa(Image.fromarray(out.astype(np.uint8)), {'lletres'}))
        frames.append(_sense_llac(_diff(_acaba(lay), base_llum())))
    return frames + [_empty()]


LLETRES = {
    'lletres': {'frames': lambda: [_empty()], 'frameDuration': 1000, 'loop': False, 'zIndex': 2},
    'lletres_brilla': {'frames': _glint_frames, 'frameDuration': 70, 'loop': False, 'prop': 'lletres'},
}


# ─── El pla del pis (la portada sense títol), damunt de Ginebra ────────────
# `pis` és el fons de la portada, opac, damunt de tot; `pis_fon` el fon en trama (quadrets de 2 px, ordre de Bayer)
# i `pis_torna` el torna a posar. `pis_vida` i `senyal` són les capes de la portada (vegeu portada.py).

BAYER = np.array([[0, 8, 2, 10], [12, 4, 14, 6], [3, 11, 1, 9], [15, 7, 13, 5]])
FON = 8


def _dissolve(k):
    """La portada amb una part `k`/FON dels quadrets ja fosa (0: sencera; FON: res)."""
    a = np.array(portada.base()).copy()
    yy, xx = np.mgrid[0:a.shape[0], 0:a.shape[1]]
    t = BAYER[(yy // 2) % 4, (xx // 2) % 4]
    a[t < k * 16 / FON, 3] = 0
    return Image.fromarray(a)


PIS = {
    'pis': {'frames': lambda: [_dissolve(0)], 'frameDuration': 1000, 'loop': False, 'zIndex': 5},
    'pis_fon': {'frames': lambda: [_dissolve(k) for k in range(1, FON + 1)], 'frameDuration': 80, 'loop': False,
                'prop': 'pis'},
    'pis_torna': {'frames': lambda: [_dissolve(k) for k in range(FON - 1, -1, -1)], 'frameDuration': 80,
                  'loop': False, 'prop': 'pis'},
    'pis_vida': portada.PIS_VIDA,
    'pis_porta': portada.PIS_PORTA,
    'pis_festa': portada.PIS_FESTA,
    'senyal': portada.SENYAL,
    'senyal_va': portada.SENYAL_VA,
}

# L'ordre compta: cada capa abans de les seves etiquetes (draw_placeholders les hi afegeix).
ANIMS = {
    'nit': {'frames': nit_frames, 'frameDuration': 260},
    **PANTALLA,
    **LLETRES,
    **PIS,
}

# La veu del Director (personatge invisible): sota el mig de la pantalla, perquè el text li surti just a sobre (entre
# el rètol BCMU i la pantalla): se sap que parla la pantalla, i no tapa ni la cara ni el rètol «EN DIRECTE» (tasca 008).
GEOMETRIA = {'things': {}, 'spawns': {'bonfill': (388, 200 + BAIXA)}, 'walkable': [(200, 253), (267, 253), (267, 261), (200, 261)]}
