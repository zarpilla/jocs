"""
La portada, a 640×360. EN 3D (hd640/tres_d.py), a 1×: «SUMA ZERO» damunt la ciutat de nit.

Un pla de cinema des d'un terrat, a l'altura del pis de l'Iri:
  - a primer pla, a l'esquerra, el **bloc del pis**, gran i en 3/4: la façana de maó amb la finestra encesa de verd
    (l'Iri a contrallum, l'ordinador), el veí que mira la tele, i el cantó que fuig cap al fons;
  - els **cables** surten per la finestra, ressegueixen la façana i pugen pel cantó fins a la **parabòlica** del
    terrat, que apunta a l'horitzó;
  - l'**avinguda** fuig en diagonal entre els terrats (dipòsits, antenes, finestres), que s'empetiteixen i es
    perden a la boira de llum de la ciutat, fins a la **torre daurada del BCMU**, petita, al punt de fuga;
  - el rètol de neó de **La Propina**, magenta, damunt d'un terrat a la dreta;
  - a baix a la dreta, l'ampit del nostre terrat i una antena, en silueta.
Els botons de la GUI `portada` van a 220..420 × 261..328: allà només hi ha terrats.

Capes (com abans): el fons no té el títol, que és la capa `titol` («Comença» l'esvaeix i el pròleg comença al
mateix pla). `pis_vida` és el bucle d'espera: l'Iri tecleja (el codi corre al monitor), el neó de La Propina fa
pampallugues, la tele del veí, el led de la parabòlica, el llum de la torre i alguna estrella.
El pròleg (proleg_ginebra.py) fa servir aquest mateix pla, i les animacions que hi passen són aquí:
  - `senyal_va`: un pols de llum surt de la parabòlica i arriba a la torre del BCMU, que s'il·lumina;
  - `pis_porta`: el monitor fa un flaix, hi surt una porta oberta i l'Iri aixeca els braços; `pis_festa`, el bucle.

El dibuix pla (la finestra, el títol, la parabòlica) és a portada_pla_comu.py. El món: x a la dreta, y amunt
(0 = el carrer), z cap al fons; l'avinguda va al llarg de z, i la torre és al final.
"""
import functools
import math

import numpy as np
from PIL import Image

import hd640  # noqa: F401  (abans que cap hd.rooms: posa la llibreria a 640×360)
from hd640 import llum
from hd.pix import Light, Canvas, W, H, hr, mix
from hd.rooms.exterior import fbm
from hd.rooms.comu import text, text_width, outline, _diff, NEON
from hd640.rooms import portada_pla_comu as PL
from hd640.rooms.portada_pla_comu import SKYP, ROOF, BLOCK, WARM, TEAL, GOLD, RAISE, N_VIDA, VIDA_MS
from hd640.tres_d import Camera, Escena, Llum

LIGHT = Light(ambient=0.0, vignette=None, floor_fade=None)

# ─── La càmera i el món ─────────────────────────────────────────────────────

HOR = 176                                  # l'horitzó a la pantalla
F = 420
EYE = (200.0, 470.0, -200.0)               # la càmera: damunt un terrat, a l'altura del pis de l'Iri
TOWER_P = (20.0, 0.0, 32000.0)             # la torre del BCMU, al final de l'avinguda
TOWER_U = 532                              # on la volem a la pantalla


def _yaw():
    a = math.atan2(TOWER_P[0] - EYE[0], TOWER_P[2] - EYE[2])
    return a - math.atan((TOWER_U - 320) / F)


CAM = Camera(pos=EYE, yaw=_yaw(), pitch=0.0, f=F, centre=(320, HOR))

FL = 80                                    # l'alçada d'un pis
IB = (-420.0, -60.0, 150.0, 470.0, 480.0)  # el bloc de l'Iri: x0, x1, z0, z1, alçada (sis pisos)
TOPY = IB[4] + 20                          # el capdamunt de l'ampit
AV = (-60.0, 100.0)                        # l'avinguda (de façana a façana)
BLK, STR = 320.0, 120.0                    # la llargada d'una illa i l'amplada d'un carrer
COLW = 360.0                               # l'amplada d'una illa (en x)
WINW, WINH = 64, 56                        # les finestres de la façana de l'Iri (com la del dibuix pla)
IRI_WIN = (2, 5)                           # la de l'Iri: columna i pis
TV_WIN = (1, 3)                            # la del veí de la tele
DISH_P = (-104.0, TOPY + 30.0, 186.0)      # el centre del plat de la parabòlica
LNB_P = (-80.0, TOPY + 36.0, 180.0)        # el capçal (el led) de la parabòlica

MOON = Llum((-90000.0, 70000.0, 50000.0), 1e7, 1.1, power=1.0)   # la lluna, darrere a l'esquerra (no surt)
AMBIENT = -0.2

FACADE = [(5, 4, 10), (9, 7, 16), (14, 11, 24), (21, 16, 33), (30, 23, 44), (42, 32, 56),
          (120, 74, 24), (190, 130, 50), (236, 180, 90), (255, 222, 150)]
FACADE_B = [(4, 6, 14), (8, 11, 22), (13, 17, 32), (20, 25, 44), (28, 34, 56), (40, 46, 70),
            (60, 110, 170), (110, 160, 220), (170, 210, 245), (220, 236, 255)]
ROOFR = [(3, 2, 8), (6, 5, 13), (10, 8, 19), (15, 12, 26), (22, 17, 34), (31, 24, 44), (42, 33, 56)]
STREET = [(3, 3, 7), (7, 6, 12), (13, 10, 16), (26, 18, 20), (52, 34, 24), (100, 66, 34), (170, 116, 56),
          (230, 176, 96)]
SIL = [(2, 2, 6), (5, 4, 10), (9, 7, 15), (14, 11, 21)]
HAZE = (70, 36, 84)


def _p(P):
    u, v, _ = CAM.projecta(P)
    return u, v


# ─── El cel ─────────────────────────────────────────────────────────────────

STARS = [(int(hr(i, 11) * W), int(hr(i, 12) * (HOR - 30)), hr(i, 13)) for i in range(170)]


def sky(cv, frame=0):
    for y in range(0, H):
        for x in range(W):
            t = y / HOR
            lvl = 0.5 + 5.6 * max(0.0, t) ** 2.2 + (hr(x // 3, y // 3) - 0.5) * 0.2
            lvl += 1.2 * max(0.0, 1 - math.hypot((x - TOWER_U) / 260, (y - HOR) / 70))   # la claror de la ciutat
            cv.put(x, y, SKYP, lvl, lit=0)
    stars(cv, frame)


def stars(cv, frame=0, mask=None):
    for i, (x, y, b) in enumerate(STARS):
        if mask is not None and not mask(x, y):
            continue
        if b > 0.75 and hr(i, 14) > 0.6 and (frame + i) % N_VIDA in (3, 4):   # algunes fan pampallugues
            b = 0.5
        cv.flat(x, y, (210, 200, 240) if b > 0.75 else (110, 100, 150) if b > 0.3 else (70, 60, 104))
        if b > 0.96:
            for dx, dy in ((-1, 0), (1, 0), (0, -1), (0, 1)):
                cv.flat(x + dx, y + dy, (96, 84, 136))


# ─── La ciutat: illes de cases al llarg de l'avinguda ───────────────────────

def _illes():
    """(x0, x1, z0, z1, alçada, llavor) de cada illa, de lluny a prop (sense la de l'Iri)."""
    out = []
    for row in range(0, 40):
        z0 = IB[2] + row * (BLK + STR)
        if z0 > 16000:
            break
        z1 = z0 + BLK
        for side in (-1, 1):
            for col in range(0, 7):
                if side < 0:
                    x1 = AV[0] - col * (COLW + STR)
                    x0 = x1 - COLW
                else:
                    x0 = AV[1] + col * (COLW + STR)
                    x1 = x0 + COLW
                if side < 0 and col == 0 and row == 0:
                    continue                                       # el bloc de l'Iri (a part)
                seed = row * 31 + col * 7 + (0 if side < 0 else 500)
                # mirant només les que entren al quadre
                us = [_p((x, 0, z))[0] for x in (x0, x1) for z in (z0, z1)]
                if max(us) < -40 or min(us) > W + 40 or z1 < EYE[2] + 50:
                    continue
                h = FL * (2 + int(hr(seed, 1) * 3.6))
                if hr(seed, 2) > 0.9 and row > 3:
                    h += FL * 3                                    # algun edifici alt, de lluny
                if side > 0 and row < 7:
                    h = min(h, FL * (2 if col == 0 else 3) + (FL if row > 3 else 0))   # els de la dreta, baixos:
                    #                                                es veu l'avinguda des de dalt
                # una illa són dues o tres cases d'alçades diferents
                n = 2 + int(hr(seed, 3) * 2)
                cut = [z0 + BLK * k / n for k in range(n + 1)]
                for k in range(n):
                    hk = max(FL * 2, h + FL * int((hr(seed, 10 + k) - 0.5) * 2.4))
                    out.append((x0, x1, cut[k], cut[k + 1], hk, seed * 5 + k))
    out.sort(key=lambda b: -math.hypot((b[0] + b[1]) / 2 - EYE[0], (b[2] + b[3]) / 2 - EYE[2]))
    return out


def _facana(seed, dist, blue=False):
    """Els nivells d'una façana de lluny: paret fosca, finestres apagades i alguna d'encesa."""
    k = F / max(dist, 1)
    small = k < 0.09

    def lvl(s, t, P):
        col, fl = int(s // 40), int(t // FL)
        a, b = s % 40, t % FL
        base = 1.6 + (hr(int(s // 7), int(t // 9), seed) - 0.5) * 0.4
        if fl < 0:
            return base
        win = (10 <= a < 30) and (22 <= b < 58)
        if small:
            win = (6 <= a < 34) and (16 <= b < 64)
        if not win:
            return base + (0.5 if b < 4 else 0)                       # la cornisa de cada pis
        r = hr(col, fl, seed)
        if r > 0.8:
            return 7.4 - (0.6 if b > 46 else 0) + (hr(col, fl, seed + 1) - 0.5)
        return 0.4
    return lvl


def _terrat(seed, L1=None, L3=None):
    def lvl(s, t, P):
        v = 3.0 + (hr(int(s // 10), int(t // 10), seed) - 0.5) * 0.6 + (fbm(P[0] / 90, P[2] / 90, seed % 50) - 0.5) * 1.0
        if s < 8 or t < 8 or (L1 and s > L1 - 8) or (L3 and t > L3 - 8):
            v += 1.2                                                 # l'ampit, que agafa la lluna
        return v
    return lvl


def _street_lvl(s, t, P):
    x, z = P[0], P[2]
    lvl = 1.0 + (hr(int(x // 12), int(z // 12), 41) - 0.5) * 0.3
    # els fanals de l'avinguda i dels carrers: bassals de llum taronja
    for lx in (AV[0] + 14, AV[1] - 14):
        lz = round((z - 40) / 220) * 220 + 40
        d = math.hypot((x - lx) * 1.0, (z - lz) * 0.7)
        if d < 90:
            lvl += 3.6 * (1 - d / 90) ** 1.5
    if AV[0] < x < AV[1] and abs(x - (AV[0] + AV[1]) / 2) < 2 and int(z // 60) % 2:
        lvl += 1.6                                                  # la ratlla del mig
    return lvl


def _lamps():
    """Els fanals de l'avinguda (punts del món, a peu de carrer)."""
    out = []
    for lx in (AV[0] + 14, AV[1] - 14):
        for k in range(0, 70):
            z = 40 + k * 220
            if z > 15000:
                break
            out.append((lx, 0.0, z))
    return out


def _cotxes():
    """Uns quants cotxes a l'avinguda: (x, z, cap a on). Els que s'acosten fan llum blanca; els que se'n van, vermella."""
    return [(AV[0] + 40 if hr(k, 5) > 0.5 else AV[1] - 40, 900 + hr(k, 6) * 9000, hr(k, 5) > 0.5) for k in range(14)]


# ─── La torre del BCMU ─────────────────────────────────────────────────────

TW, TD, TH = 1100.0, 800.0, 4400.0        # amplada, fons i alçada de la torre
T_ANG = 0.62


def _torre_lvl(face, base):
    def lvl(s, t, P):
        fl = int(t // 170)
        col = int(s // 150)
        win = (t % 170) > 60 and (s % 150) > 30
        v = base - t / TH * 0.8 + (0.7 if (t % 170) < 26 else 0)
        if win and hr(col, fl, 7 + face) > 0.55:
            v += 1.2
        return v
    return lvl


def torre(e):
    cx, _, cz = TOWER_P
    e.caixa_girada('torre', cx, cz, TW, TD, TH, T_ANG, GOLD, 2.0,
                   cares={'davant': {'ramp': GOLD, 'lvl': _torre_lvl(0, 2.2)},
                          'esquerra': {'ramp': GOLD, 'lvl': _torre_lvl(1, 1.2)},
                          'dreta': {'ramp': GOLD, 'lvl': _torre_lvl(2, 1.0)},
                          'darrere': {'ramp': GOLD, 'lvl': _torre_lvl(3, 1.0)},
                          'dalt': {'ramp': GOLD, 'lvl': 3.6}})
    e.caixa_girada('torre', cx, cz, TW + 160, TD + 160, 220, T_ANG, GOLD, 3.0, y0=TH,
                   cares={'dalt': {'ramp': GOLD, 'lvl': 3.8}})       # el coronament


def tower_top():
    return _p((TOWER_P[0], TH + 220 + 1400, TOWER_P[2]))


def tower_sign(cv, frame=0, flash=0.0):
    """L'antena (amb el llum vermell), el rètol «BCMU» i el halo de la torre: en pantalla, al damunt."""
    ax, ay = tower_top()
    bx, by = _p((TOWER_P[0], TH + 220, TOWER_P[2]))
    cx = round(ax)
    cv.vline(cx, round(ay) + 1, round(by), GOLD, 2.0, lit=0)
    w = text_width('BCMU')
    text(cv, 'BCMU', cx - w // 2, round(by) - 8, GOLD, 4, lit=0)
    cv.flat(cx, round(ay), (110, 30, 30) if frame % N_VIDA == 6 else (255, 90, 70))
    if flash:
        cv.glow(cx, ay, 6 + 10 * flash, (150, 255, 220), 0.9 * flash)
        cv.flat(cx, round(ay), (230, 255, 244))
        cv.glow(cx, (by + _p(TOWER_P)[1]) / 2, 40, (120, 255, 220), 0.25 * flash)


# ─── El bloc de l'Iri ───────────────────────────────────────────────────────

def _maons(cv, w, h, seed=0, fosc=0.0):
    for y in range(h):
        for x in range(w):
            row = y // 8
            brick = (y % 8 == 0) or ((x + (row % 2) * 9) % 18 == 0)
            lvl = (2.0 if brick else 2.8) + (hr(x // 3, y // 3, seed) - 0.5) * 0.35 - fosc
            lvl -= 0.25 * (hr((x + (row % 2) * 9) // 18, row, seed + 1) > 0.8)   # algun maó més fosc
            cv.put(x, y, BLOCK, lvl, lit=0)


def _ty(y):
    """Una alçada del món → la y de la textura de la façana (0 = el capdamunt de l'ampit)."""
    return round(TOPY - y)


def _win_box(col, fl, w=WINW, h=WINH, cols=3, width=None):
    width = width or (IB[1] - IB[0])
    cx = width * (col + 0.5) / cols
    x0 = round(cx - w / 2)
    y1 = _ty(fl * FL + 14)
    return x0, y1 - h + 1, x0 + w - 1, y1


def _finestra(cv, box, kind, frame=0, seed=0):
    """Una finestra qualsevol de la façana: `kind` = 'fosca', 'persiana', 'encesa', 'tele'."""
    x0, y0, x1, y1 = box
    mx = (x0 + x1) // 2
    if kind == 'encesa':
        cv.rect(x0, y0, x1, y1, WARM, lambda x, y: 1.2 + (y - y0) / (y1 - y0) * 0.8, lit=0)
        cv.rect(x0, y0, x0 + (x1 - x0) // 3, y1, [(90, 40, 30), (140, 70, 40)], 0.6, lit=0)   # la cortina
    elif kind == 'tele':
        tv = (0.6, 0.6, 1.0, 0.6, 0.3, 0.6, 0.8, 0.6)[frame % N_VIDA]   # la tele fa pampallugues
        cv.rect(x0, y0, x1, y1, [(16, 22, 56), (30, 44, 100), (50, 70, 150)], tv, lit=0)
        cv.disc(x0 + 40, y1 - 9, 5, 6, [(6, 8, 18)], 0, lit=0)        # el cap de qui mira, a contrallum
        cv.rect(x0 + 34, y1 - 4, x0 + 46, y1, [(6, 8, 18)], 0, lit=0)
    else:
        cv.rect(x0, y0, x1, y1, [(4, 4, 8), (8, 8, 15), (12, 12, 22)], lambda x, y: 0.6 + (0.6 if (x - y) % 23 == 0 else 0),
                lit=0)
        if kind == 'persiana':
            n = 6 + int(hr(seed, 3) * 10)
            for j in range(n):
                cv.hline(x0, x1, y0 + j * 3, BLOCK, 1.8, lit=0)
                cv.hline(x0, x1, y0 + j * 3 + 1, BLOCK, 1.2, lit=0)
    cv.vline(mx, y0, y1, BLOCK, 1.2, lit=0)                            # el muntant
    outline(cv, x0 - 1, y0 - 1, x1 + 1, y1 + 1, BLOCK)
    cv.rect(x0 - 3, y1 + 1, x1 + 3, y1 + 3, BLOCK, lambda x, y: 3.6 if y == y1 + 1 else 2.2, lit=0)   # l'ampit
    cv.rect(x0 - 2, y0 - 3, x1 + 2, y0 - 2, BLOCK, 3.0, lit=0)         # la llinda


IRI_BOX = _win_box(*IRI_WIN)
TV_BOX = _win_box(*TV_WIN)


@functools.lru_cache(maxsize=None)
def _iri_finestra(frame=0, mode='espera', k=0):
    """La finestra de l'Iri del dibuix pla (portada_pla_comu.window), retallada."""
    tmp = Canvas(light=LIGHT, transparent=True)
    PL.window(tmp, frame, mode, k)
    wx0, wy0, wx1, wy1 = PL.WIN
    return tmp.img.crop((wx0 - 4, wy0 - 1, wx1 + 5, wy1 + 5))


@functools.lru_cache(maxsize=None)
def facana(frame=0, mode='espera', k=0):
    """La façana del davant del bloc de l'Iri (la que mira la càmera): maó, sis pisos de finestres, la de l'Iri."""
    w, h = int(IB[1] - IB[0]), int(TOPY) + 1
    cv = Canvas(w=w, h=h, light=LIGHT)
    _maons(cv, w, h, 3)
    cv.rect(0, 0, w - 1, 5, BLOCK, lambda x, y: 3.4 + (0.6 if y == 0 else 0) - (1.2 if y == 5 else 0), lit=0)   # l'ampit
    cv.rect(0, _ty(IB[4]) - 2, w - 1, _ty(IB[4]) + 2, BLOCK, lambda x, y: 3.2 - (y - _ty(IB[4])) * 0.4, lit=0)  # la cornisa
    for fl in range(0, 6):
        cv.hline(0, w - 1, _ty(fl * FL), BLOCK, 1.4, lit=0)            # les línies dels forjats
        for col in range(3):
            if (col, fl) == IRI_WIN:
                continue
            seed = col * 7 + fl
            kind = 'tele' if (col, fl) == TV_WIN else ('encesa' if hr(seed, 1) > 0.82 else
                                                      'persiana' if hr(seed, 2) > 0.45 else 'fosca')
            _finestra(cv, _win_box(col, fl), kind, frame, seed)
    x0, y0, x1, y1 = IRI_BOX
    win = _iri_finestra(frame, mode, k)
    cv.img.alpha_composite(win, (x0 - 4 + (WINW - 65) // 2, y1 - win.height + 5))
    # un regalim d'humitat sota l'ampit del terrat i una taca
    for j in range(60):
        if hr(j, 51) > 0.3:
            cv.put(40 + (j % 3 == 0), 8 + j, BLOCK, 1.0, lit=0)
    return cv.img


@functools.lru_cache(maxsize=None)
def lateral():
    """La façana del cantó, que fuig cap al fons de l'avinguda (fosca: la lluna és a l'altra banda)."""
    w, h = int(IB[3] - IB[2]), int(TOPY) + 1
    cv = Canvas(w=w, h=h, light=LIGHT)
    _maons(cv, w, h, 5, fosc=0.4)
    cv.rect(0, 0, w - 1, 5, BLOCK, lambda x, y: 3.0 + (0.6 if y == 0 else 0) - (1.2 if y == 5 else 0), lit=0)
    cv.rect(0, _ty(IB[4]) - 2, w - 1, _ty(IB[4]) + 2, BLOCK, lambda x, y: 2.8 - (y - _ty(IB[4])) * 0.4, lit=0)
    for fl in range(0, 6):
        cv.hline(0, w - 1, _ty(fl * FL), BLOCK, 1.0, lit=0)
        for col in range(3):
            seed = col * 13 + fl + 40
            kind = 'encesa' if hr(seed, 1) > 0.85 else 'persiana' if hr(seed, 2) > 0.5 else 'fosca'
            _finestra(cv, _win_box(col, fl, w=48, cols=3, width=w), kind, 0, seed)
    for y in range(0, h):                                              # el baixant, al cantó
        cv.put(6, y, BLOCK, 3.2, lit=0)
        cv.put(7, y, BLOCK, 2.0, lit=0)
        if y % 60 == 0:
            cv.hline(5, 8, y, BLOCK, 3.8, lit=0)
    return cv.img


def _fp(tx, ty, out=1.0):
    """Un punt de la textura de la façana del davant → el món (`out`: separat de la paret)."""
    return (IB[0] + tx, TOPY - ty, IB[2] - out)


def bloc(e, tex):
    x0, x1, z0, z1, h = IB
    e.quad('lateral', (x1, TOPY, z0), (x1, TOPY, z1), (x1, 0, z1), (x1, 0, z0), tex=(tex['lateral'], (0, 0, z1 - z0, TOPY + 1)))
    e.quad('facana', (x0, TOPY, z0), (x1, TOPY, z0), (x1, 0, z0), (x0, 0, z0), tex=(tex['facana'], (0, 0, x1 - x0, TOPY + 1)))
    # la cornisa que sobresurt (la de dalt i la de cada balcó): fa una ratlla d'ombra sota
    e.caixa('cornisa', x0 - 4, x1 + 6, h - 2, h + 2, z0 - 6, z1, BLOCK, 3.0,
            cares={'sota': {'ramp': BLOCK, 'lvl': 0.6}, 'davant': {'ramp': BLOCK, 'lvl': 3.4},
                   'dreta': {'ramp': BLOCK, 'lvl': 2.4}})


def _cables_pts():
    """Els tres cables: surten per la finestra, van al cantó, pugen fins al terrat i a la parabòlica."""
    x0, y0, x1, y1 = IRI_BOX
    out = []
    for j in range(3):
        a = _fp(x1 + 2, y0 + 12 + j * 4, 1.5)
        corner = (IB[1] + 1.5 + j * 2, a[1] + 8, IB[2] - 1.5)
        pts = [a]
        for i in range(1, 8):                                          # pengen una mica
            t = i / 8
            pts.append((a[0] + (corner[0] - a[0]) * t, a[1] + (corner[1] - a[1]) * t - math.sin(t * math.pi) * 9,
                        a[2] + (corner[2] - a[2]) * t))
        pts += [corner, (corner[0], TOPY + 1, corner[2] - 2), (corner[0] - 6, TOPY + 4, IB[2] + 10),
                (DISH_P[0] + 8 + j * 3, TOPY + 2, DISH_P[2] - 4), (DISH_P[0] + 4, DISH_P[1] - 16, DISH_P[2] + 2)]
        out.append(pts)
    return out


CABLE_COLS = ([(10, 10, 14), (36, 36, 44), (70, 70, 82)], [(50, 8, 12), (120, 24, 28), (170, 40, 40)],
              [(8, 22, 40), (24, 60, 100), (40, 100, 150)])


@functools.lru_cache(maxsize=None)
def _dish_img(led=True):
    """La parabòlica (el dibuix pla de sempre, una mica més grossa), amb el capçal mirant a la torre."""
    cv = Canvas(w=48, h=40, light=LIGHT, transparent=True)
    dx, dy = 18, 18
    cv.disc(dx + 4, dy - 3, 13, 10, [(30, 34, 44), (70, 76, 90), (130, 136, 150), (190, 196, 206)],
            lambda nx, ny: 2.2 + nx * 1.0 - ny * 0.6, lit=0)
    for a in range(0, 360, 3):                                         # la vora del plat
        cv.put(round(dx + 4 + math.cos(math.radians(a)) * 13), round(dy - 3 + math.sin(math.radians(a)) * 10),
               [(30, 34, 44), (80, 86, 100)], 0.6, lit=0)
    cv.line(dx + 4, dy - 3, dx + 20, dy - 9, [(200, 206, 214)], 0, lit=0)
    cv.line(dx + 4, dy + 4, dx + 20, dy - 9, [(150, 156, 170)], 0, lit=0)
    cv.rect(dx + 19, dy - 11, dx + 21, dy - 8, [(90, 20, 20)] if not led else [(250, 60, 60)], 0, lit=0)
    if led:
        cv.flat(dx + 20, dy - 10, (255, 170, 160))
    cv.rect(dx - 1, dy + 6, dx + 1, 39, [(20, 20, 28), (50, 50, 60)], lambda x, y: 1 if x == dx - 1 else 0, lit=0)   # el pal
    return cv.img


DISH_FOOT = (19, 39)                                                   # el peu del pal, a la imatge


def parabolica(e, led=True):
    e.caixa('terrat', IB[0], IB[1], TOPY - 1, TOPY, IB[2], IB[3], ROOFR, 2.0)
    e.sprite('parabolica', _dish_img(led), DISH_FOOT, (DISH_P[0], TOPY, DISH_P[2]))


def led_xy():
    k = CAM.escala((DISH_P[0], TOPY, DISH_P[2]))
    u, v = _p((DISH_P[0], TOPY, DISH_P[2]))
    return u + (38 - DISH_FOOT[0]) * k, v + (8 - DISH_FOOT[1]) * k


# ─── La Propina i el primer pla ─────────────────────────────────────────────

NEON_Z = IB[2] + 3 * (BLK + STR) + 40                    # el rètol, al terrat d'una illa de la dreta
NEON_X = (AV[1] + 20, AV[1] + 280)
NEON_Y = (FL * 2 + 16, FL * 2 + 86)


@functools.lru_cache(maxsize=None)
def _neon_img(on=True):
    """El rètol de La Propina, de lletres grosses (×3) per llegir-se de lluny."""
    small = Canvas(w=60, h=8, light=LIGHT, transparent=True)
    col = (255, 120, 200) if on else (90, 30, 70)
    text(small, 'LA PROPINA', 1, 1, NEON, 0, lit=0, flat=col)
    w = int(NEON_X[1] - NEON_X[0])
    h = int(NEON_Y[1] - NEON_Y[0])
    cv = Canvas(w=w, h=h, light=LIGHT)
    cv.rect(0, 0, w - 1, h - 1, [(14, 6, 16), (24, 10, 26)], lambda x, y: 0.6 + (0.6 if (x // 4 + y // 4) % 2 else 0), lit=0)
    outline(cv, 0, 0, w - 1, h - 1, [(70, 24, 60)] if on else [(30, 10, 26)])
    outline(cv, 3, 3, w - 4, h - 4, [(150, 40, 110)] if on else [(40, 14, 34)])
    from pixels import nearest
    big = nearest(small.img, (small.img.width * 4, small.img.height * 4))
    tw = text_width('LA PROPINA') * 4
    cv.img.alpha_composite(big, ((w - tw) // 2 - 4, (h - 32) // 2 + 2))
    return cv.img


def rètol(e, on=True):
    x0, x1 = NEON_X
    y0, y1 = NEON_Y
    z = NEON_Z
    for x in (x0 + 30, x1 - 30):                                       # les potes
        e.caixa('rètol_potes', x - 3, x + 3, FL * 2, y0, z + 2, z + 8, SIL, 1.6)
    e.quad('rètol', (x0, y1, z), (x1, y1, z), (x1, y0, z), (x0, y0, z), tex=(_neon_img(on), (0, 0, x1 - x0, y1 - y0)))


def _s(u, y, d):
    """El punt del món a l'alçada `y` que es veu a la columna `u` de la pantalla, a la profunditat `d`."""
    x1 = (u - CAM.centre[0]) * d / F
    cy, sy = math.cos(CAM.yaw), math.sin(CAM.yaw)
    return (EYE[0] + x1 * cy + d * sy, y, EYE[2] - x1 * sy + d * cy)


def primer_pla(e):
    """L'ampit del nostre terrat, que entra en diagonal per baix a la dreta, i un dipòsit d'aigua en silueta."""
    A, B = _s(540, 400, 300), _s(700, 400, 150)
    dx, dz = B[0] - A[0], B[2] - A[2]
    L = math.hypot(dx, dz)
    ang = math.atan2(dz, dx)
    e.caixa_girada('primer_pla', (A[0] + B[0]) / 2, (A[2] + B[2]) / 2, L, 14, 70, -ang, SIL, 1.0, y0=330,
                   cares={'dalt': {'ramp': SIL, 'lvl': 2.6}, 'davant': {'ramp': SIL, 'lvl': 0.8},
                          'darrere': {'ramp': SIL, 'lvl': 1.4}})
    # una xemeneia de maó amb una antena de televisió, tallades per la vora
    T = _s(668, 400, 300)
    e.caixa('primer_pla', T[0] - 22, T[0] + 22, 330, 452, T[2] - 18, T[2] + 18, SIL, 1.2,
            cares={'dalt': {'ramp': SIL, 'lvl': 2.6}, 'esquerra': {'ramp': SIL, 'lvl': 1.8}})
    e.caixa('primer_pla', T[0] - 26, T[0] + 26, 452, 460, T[2] - 22, T[2] + 22, SIL, 2.0,
            cares={'dalt': {'ramp': SIL, 'lvl': 3.0}, 'esquerra': {'ramp': SIL, 'lvl': 2.4}})
    ax, az = T[0] - 8, T[2]
    e.cable('primer_pla', [(ax, 460, az), (ax, 600, az)], SIL, 1.8, gruix=2.4)
    for k, y in enumerate((590, 572, 556)):
        L = 46 - k * 9
        e.cable('primer_pla', [(ax - L, y, az + L * 0.4), (ax + L, y + 4, az - L * 0.4)], SIL, 1.8, gruix=1.4)
    # el fil de l'antena, que baixa fent panxa fins a l'ampit
    e.cable('primer_pla', [(ax, 580, az), (ax - 20, 520, az - 30), (ax - 30, 450, az - 70), (ax - 34, 402, az - 110)], SIL,
            1.4, gruix=1.0)


# ─── Composició ────────────────────────────────────────────────────────────

def escena(cv, tex, led=True, neon=True, frame=0):
    sky(cv, frame)
    e = Escena(cv, CAM, [MOON], ambient=AMBIENT)
    e.quad('carrer', (-60000, 0, 40000), (60000, 0, 40000), (60000, 0, 0), (-60000, 0, 0), ramp=STREET, lvl=_street_lvl)
    torre(e)
    dist = {}
    for (x0, x1, z0, z1, h, seed) in _illes():
        sid = 'illa%d' % seed
        d = math.hypot((x0 + x1) / 2 - EYE[0], (z0 + z1) / 2 - EYE[2])
        dist[sid] = d
        fac = {'ramp': FACADE_B if hr(seed, 9) > 0.8 else FACADE, 'lvl': _facana(seed, d)}
        e.caixa(sid, x0, x1, 0, h, z0, z1, FACADE, 2.0,
                cares={'davant': fac, 'darrere': fac, 'esquerra': fac, 'dreta': fac,
                       'dalt': {'ramp': ROOFR, 'lvl': _terrat(seed, x1 - x0, z1 - z0)}})
        if d < 5000:
            _coses_terrat(e, sid, x0, x1, z0, z1, h, seed)
    rètol(e, neon)
    bloc(e, tex)
    for pts, col in zip(_cables_pts(), CABLE_COLS):
        e.cable('cables', pts, col, 1.6, gruix=1.3)
    parabolica(e, led)
    primer_pla(e)
    e.dist = dist
    return e


def _coses_terrat(e, sid, x0, x1, z0, z1, h, seed):
    """Dipòsits d'aigua, antenes i màquines de l'aire, damunt dels terrats de prop."""
    for k in range(3):
        r = hr(seed, 20 + k)
        if r < 0.45:
            continue
        cx = x0 + 40 + hr(seed, 30 + k) * (x1 - x0 - 80)
        cz = z0 + 30 + hr(seed, 40 + k) * (z1 - z0 - 60)
        if r > 0.8:                                                    # un dipòsit amb potes
            e.caixa(sid, cx - 22, cx + 22, h + 16, h + 52, cz - 18, cz + 18, ROOFR, 3.0,
                    cares={'dalt': {'ramp': ROOFR, 'lvl': 4.2}})
            for dx in (-16, 16):
                e.cable(sid, [(cx + dx, h, cz - 14), (cx + dx, h + 16, cz - 14)], ROOFR, 2.0, gruix=3)
        elif r > 0.6:                                                  # una antena
            e.cable(sid, [(cx, h, cz), (cx, h + 70, cz)], ROOFR, 3.0, gruix=2)
            e.cable(sid, [(cx - 20, h + 60, cz), (cx + 20, h + 60, cz)], ROOFR, 3.0, gruix=1.5)
        else:                                                          # una màquina de l'aire
            e.caixa(sid, cx - 16, cx + 16, h, h + 20, cz - 12, cz + 12, ROOFR, 2.6,
                    cares={'dalt': {'ramp': ROOFR, 'lvl': 4.0}})


def _llums_ciutat(cv, e):
    """Els fanals i els llums dels cotxes, on no els tapa res; i la boira de llum de la ciutat cap al fons."""
    W_ = cv.w
    ids = e.ids
    carrer = ids.index('carrer')
    for P in _lamps():
        u, v = _p(P)
        U, V = round(u), round(v)
        if 0 <= U < W and 0 <= V < H and e.amo[V * W_ + U] == carrer:
            k = CAM.escala(P)
            uu, vv = _p((P[0], 60, P[2]))
            cv.flat(round(uu), round(vv), (255, 214, 140))
            if k > 0.15:
                cv.glow(uu, vv, 3 + 8 * k, (255, 190, 110), 0.35)
    for x, z, ve in _cotxes():
        u, v = _p((x, 6, z))
        U, V = round(u), round(v)
        if 0 <= U < W and 0 <= V < H and e.amo[V * W_ + U] == carrer:
            col = (255, 246, 220) if ve else (230, 40, 40)
            cv.flat(U, V, col)
            if CAM.escala((x, 0, z)) > 0.12:
                cv.flat(U + 1, V, col)


def _boira(img, e):
    """La perspectiva atmosfèrica: les illes llunyanes es tenyeixen del color de l'aire de la ciutat."""
    a = np.asarray(img, dtype=np.float32).copy()
    amo = np.frombuffer(e.amo, dtype=np.uint16).reshape(H, W)
    k = np.zeros(len(e.ids), dtype=np.float32)
    for i, sid in enumerate(e.ids):
        d = e.dist.get(sid)
        if d is not None:
            k[i] = min(0.78, max(0.0, (d - 900) / 9000) ** 0.7 * 0.8)
        elif sid in ('carrer', 'torre'):
            k[i] = 0.45 if sid == 'carrer' else 0.3
    kk = k[amo]
    yy = np.arange(H, dtype=np.float32)[:, None]
    kk = kk * np.clip(1.15 - np.abs(yy - HOR) / 160, 0.5, 1.0)
    # (amb un dither de Bayer, perquè no quedi llis)
    kk = np.floor(kk * 10 + llum._bayer(H, W)) / 10
    a[..., :3] = a[..., :3] * (1 - kk[..., None]) + np.array(HAZE, dtype=np.float32) * kk[..., None]
    return Image.fromarray(a.clip(0, 255).astype(np.uint8), 'RGBA').copy()


def _fx():
    wx, wy = _p(_fp((IRI_BOX[0] + IRI_BOX[2]) / 2, (IRI_BOX[1] + IRI_BOX[3]) / 2))
    nx, ny = _p(((NEON_X[0] + NEON_X[1]) / 2, (NEON_Y[0] + NEON_Y[1]) / 2, NEON_Z))
    light = [llum.wash(wx, wy, 120, (60, 230, 190), k=0.9, air=0.06, squash=1.0),         # la finestra de l'Iri
             llum.wash(nx, ny, 80, (255, 80, 200), k=0.8, air=0.05, squash=1.4)]           # el neó
    tone = [llum.grade(contrast=1.1, pivot=40, sat=1.15, lift=(4, 1, 9))]
    bloom = [llum.bloom(thr=140, radii=((2, 0.5), (8, 0.4), (24, 0.2)))]
    return light, bloom, tone


def _amb_llum(img):
    light, bl, tone = _fx()
    return llum.apply(img, light + bl + tone, scale=1)


@functools.lru_cache(maxsize=None)
def _textures(frame=0, mode='espera', k=0):
    return {'facana': facana(frame, mode, k), 'lateral': lateral()}


def _render(**kw):
    cv = Canvas(light=LIGHT)
    e = escena(cv, _textures(), **kw)
    _llums_ciutat(cv, e)
    img = _boira(cv.img, e)
    cv2 = Canvas(light=LIGHT, img=img)
    tower_sign(cv2)
    return cv2.img, e


@functools.lru_cache(maxsize=None)
def _base():
    return _render()


@functools.lru_cache(maxsize=1)
def base():
    """El fons de la portada (sense el títol), amb la llum: el pròleg en fa la capa `pis`."""
    return _amb_llum(_base()[0])


def bg(cv):
    cv.img.paste(base())
    cv.P = cv.img.load()


PROPS = {}


# ─── Capes ──────────────────────────────────────────────────────────────────

@functools.lru_cache(maxsize=None)
def _neon_off():
    """El rètol apagat, projectat (una capa)."""
    _, e = _base()
    return e.capa(_neon_img(False), {'rètol'})


def _fotograma(frame=0, mode='espera', k=0, neon=True, led=True, extra=None, flash=0.0):
    """El fons amb un estat (la finestra, el neó, el led, el llum de la torre), amb la llum, menys el fons."""
    img, e = _base()
    img = img.copy()
    img.alpha_composite(e.capa(facana(frame, mode, k), {'facana'}))
    if not neon:
        img.alpha_composite(_neon_off())
    cv = Canvas(light=LIGHT, img=img)
    if not led:
        lx, ly = led_xy()
        cv.rect(round(lx) - 1, round(ly) - 1, round(lx), round(ly), [(90, 20, 20)], 0, lit=0)
    tower_sign(cv, frame, flash)
    stars(cv, frame, mask=lambda x, y: e.amo[y * W + x] == 0)
    if extra:
        extra(cv)
    return _diff(_amb_llum(cv.img), base())


def _vida(i):
    return _fotograma(frame=i, neon=i % N_VIDA != 5, led=i % 4 != 0)


def _empty():
    return Canvas(light=LIGHT, transparent=True).img


def _title_frames():
    cv = Canvas(light=LIGHT, transparent=True)
    PL.title(cv)
    return [cv.img]


def signal(cv, frame):
    """El pols de llum que va de la parabòlica a la torre, amb una cueta, fent un arc per damunt dels terrats."""
    ax, ay = led_xy()
    bx, by = tower_top()
    n = 10
    for k, (dt, a) in enumerate(((0, 1.0), (0.025, 0.5), (0.05, 0.25))):
        t = frame / n - dt
        if t < 0:
            continue
        te = 1 - (1 - t) ** 1.6                                        # (de lluny, més a poc a poc)
        px = ax + (bx - ax) * te
        py = ay + (by - ay) * te - math.sin(te * math.pi) * 46
        if k == 0:
            cv.glow(px, py, 8, (120, 255, 220), 0.7)
            cv.rect(px - 1, py, px + 1, py, [(220, 255, 240)], 0, lit=0)
            cv.flat(px, py - 1, (220, 255, 240))
            cv.flat(px, py + 1, (220, 255, 240))
        else:
            cv.glow(px, py, 5, (120, 255, 220), 0.5 * a)
            cv.flat(px, py, (120, 220, 200))


def _signal_frames():
    """El pols va de la parabòlica a la torre (10 fotogrames), la torre s'il·lumina i s'apaga; acaba buit."""
    frames = [_fotograma(extra=lambda cv, i=i: signal(cv, i)) for i in range(10)]
    frames += [_fotograma(flash=f) for f in (1.0, 0.8, 0.6, 0.4, 0.2)]
    return frames + [_empty()]


# Totes dues sales: `pis_vida` és la capa del bucle d'espera (a la portada, damunt del fons; al pròleg, damunt de la
# capa opaca `pis`), i les altres són etiquetes d'aquesta capa o de `senyal`, que les indicacions d'escena hi posen.
PIS_VIDA = {'frames': lambda: [_vida(i) for i in range(N_VIDA)], 'frameDuration': VIDA_MS, 'zIndex': 6}
PIS_PORTA = {'frames': lambda: [_fotograma(frame=i % N_VIDA, mode='porta', k=i) for i in range(len(RAISE))],
             'frameDuration': 120, 'loop': False, 'prop': 'pis_vida'}
PIS_FESTA = {'frames': lambda: [_fotograma(frame=i, mode='festa') for i in range(2)], 'frameDuration': 260,
             'prop': 'pis_vida'}
SENYAL = {'frames': lambda: [_empty()], 'frameDuration': 1000, 'loop': False, 'zIndex': 6}
SENYAL_VA = {'frames': _signal_frames, 'frameDuration': 110, 'loop': False, 'prop': 'senyal'}

ANIMS = {
    'pis_vida': {**PIS_VIDA, 'zIndex': 1},
    'titol': {'frames': _title_frames, 'frameDuration': 1000, 'loop': False, 'zIndex': 3},
}

GEOMETRIA = {'things': {}, 'spawns': {}, 'walkable': [(200, 253), (267, 253), (267, 261), (200, 261)]}
