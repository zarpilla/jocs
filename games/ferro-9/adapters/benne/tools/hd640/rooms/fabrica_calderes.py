"""
Sala de calderes (Acte 1-3, Iri). EN 3D (hd640/tres_d.py), a 1×.

Una càmera alta, a l'esquerra, que mira de biaix la cantonada del fons a la dreta:
  - a la paret del fons, la **porta del magatzem** (EINES), el **tauler d'anuncis** damunt la **porta del moll**, la
    canonada amb la vàlvula vermella i el rellotge (les 3 i 10);
  - a la paret de la dreta, en escorç, els manòmetres de la línia de vapor, la **porta de la cambra** i el **llum
    d'alarma**;
  - la **caldera gran**, un cilindre de coure separat de la paret, damunt el fogar de maó amb la boca del foc; la
    pila de carbó i la pala al costat;
  - l'**escriptori del capatàs**, separat i girat, amb el flexo verd, el cafè i el diari;
  - una vagoneta de carbó al mig (s'hi passa per darrere) i, en primer pla, una columna de ferro reblada a
    l'esquerra i sacs de carbó en silueta a baix a la dreta.

La llum: el foc (taronja, des de baix, l'ombra cap enrere), el flexo del capatàs i, quan està encès, l'alarma
vermella. Tot el detall ve del dibuix pla de sempre (fabrica_calderes_pla_comu.py), projectat.

El món: x a la dreta (0 = la vora esquerra del dibuix pla), y amunt (0 = el terra), z cap al fons (300 = la paret
del fons); 1 unitat = 1 píxel de sala a la distància on un personatge fa ≈110 px (escala 1).
"""
import functools
import math
import random

import hd640  # noqa: F401  (abans de cap hd.rooms: posa la llibreria a 640×360)
from PIL import Image

from hd.pix import Canvas, Light, W, H, hr, WALNUT, GOLD, COPPER, RUST, BRICK, IRON, PAPER, LAMPG, RED
from hd640.rooms import fabrica_calderes_pla_comu as PL
from hd640.rooms.fabrica_calderes_pla_comu import (STONE, STEAM, COAL, ENAMEL, frame_diff, steam, drift,  # noqa: F401
                                                    contact_shadow)
from hd640.tres_d import Camera, Escena, Llum

BOTTOM = 259                                       # la sala acaba aquí (a sota, la barra de verbs)
ZW = 300                                           # la paret del fons
HW = PL.FLOOR_Y                                    # l'alçada de les parets (el dibuix pla fa 211 fins al terra)
XC = 490                                           # al dibuix pla, la cantonada: a la dreta, la paret de la cambra
ZR = -80                                           # fins on arriba la paret de la dreta (cap a la càmera)
XL = -320                                          # fins on arriba la paret del fons per l'esquerra

BOILER = (171, 214, 63)                            # la caldera: x, z del centre, radi
BODY = (HW - 171, HW - 61)                         # el cos: y de baix (damunt el fogar) i de dalt
FOGAR = (99, 243, 142, 262, HW - 172)              # el fogar de maó: x0, x1, z0, z1, alçada
DESK = (408, 196, 70, 36, 44, -0.38)               # l'escriptori del capatàs: x, z del centre, ample, fons, alt, gir
VAG = (262, 96, 50, 32, 34, 0.42)                 # la vagoneta: x, z, ample, fons, alt (de la caixa), gir
SEGELL = (335, 25)                                 # on ha caigut el segell (x, z)
COAL_PILE = (76, 150)                              # la pila de carbó (x, z)


def _wz(fx):
    """Una x del dibuix pla de la paret de la cambra → la z del món."""
    return ZW - (fx - XC)


def _y(fy):
    """Una y del dibuix pla (el terra, a 211) → l'alçada del món."""
    return HW - fy


CAM = Camera(pos=(170, 215, -260), yaw=0.3, pitch=0.24, f=400, centre=(320, 72))

LIGHT = Light(ambient=0.0, vignette=None, floor_fade=None)  # (la llum és la del món: la de l'Escena)
FIRE_P = (171, 16, FOGAR[2] - 4)                            # la boca del foc
LAMP_P = None                                               # (el flexo: es calcula amb l'escriptori)
ALARM_P = (XC - 8, _y(69), _wz(596))                        # el llum d'alarma


def _desk_pt(lx, y, lz):
    cx, cz, w, d, h, a = DESK
    c, s = math.cos(a), math.sin(a)
    return (cx + lx * c - lz * s, y, cz + lx * s + lz * c)


LAMP_P = _desk_pt(20, DESK[4] + 26, 4)
LLUMS = [Llum(FIRE_P, 380, 2.6, power=1.5),                # el foc
         Llum((171, 60, 120), 200, 0.8, power=1.2),        # la resplendor del foc a l'aire
         Llum(LAMP_P, 120, 1.6, power=1.6)]                # el flexo del capatàs


def _llums(alarma=False):
    if not alarma:
        return LLUMS
    return LLUMS + [Llum(ALARM_P, 170, 1.8, power=1.4)]


# ─── Les textures: el dibuix pla de sempre ───────────────────────────────────

def _tex_light(alarm=False):
    """La llum del dibuix pla, sense la vinyeta ni l'enfosquiment de baix (en 3D, la fa el món)."""
    lt = Light(ambient=0.3, vignette=None, floor_fade=None)
    lt.point(PL.FIRE_X, PL.FIRE_Y - 5, r=307, k=2.6, squash=0.95, power=2.0)
    if alarm:
        lt.point(596, 72, r=83, k=1.5, power=1.8)
    lt.point(429, 155, r=93, k=1.4, squash=1.2, down=True)
    return lt


def _murs(cv):
    """El sostre, el maó i el sòcol."""
    PL.ceiling(cv)
    PL.brick_wall(cv, 0, 19, W - 1, 202, seed=11, base=1.5, extra=PL.soot)
    PL.wall_plinth(cv, 203, 210)


@functools.lru_cache(maxsize=None)
def _paret(alarm=False):
    """Les dues parets planes, de cara: tot el dibuix pla menys la caldera, el fogar, el carbó i l'escriptori."""
    cv = Canvas(light=_tex_light(alarm))
    _murs(cv)
    PL.pipe_h(cv, 0, W - 1, 21, 7, COPPER, 2.2, flange_every=85)
    PL.pipe_h(cv, 248, W - 1, 33, 5, IRON, 2.4, flange_every=64, seed=8)
    for x in range(27, W, 85):
        PL.bracket(cv, x, 28)
    for y in range(39, 93):                                            # la gotera de rovell
        if hr(y, 9) > 0.25:
            cv.put(344, y, RUST, 2.2 - (y - 39) / 40, 0.6)
        if y < 67 and hr(y, 7) > 0.5:
            cv.put(345, y, RUST, 1.6, 0.6)
    cv.put(344, 93, RUST, 3.0, 0.6)
    # la porta del magatzem
    cv.rect(7, 79, 81, 86, STONE, lambda x, y: [3.6, 3.2, 3.0, 2.6, 2.4, 2.2, 2.0, 0.8][y - 79] + (hr(x // 4, 79) - 0.5) * 0.3)
    for x in range(7, 82, 15):
        cv.vline(x, 80, 85, STONE, 1.2)
    PL.plank_door(cv, 11, 87, 77, 207, base=2.2)
    cv.rect(28, 99, 60, 109, ENAMEL, lambda x, y: 3.8 if 28 < x < 60 and 99 < y < 109 else 1.6, 0.6)
    PL.text(cv, 44 - PL.text_w('EINES') // 2, 101, 'EINES', IRON, 1.0, 0)
    # el tub de la caldera al sostre (la caldera ara és lluny de la paret: només en queda la boca)
    PL.front(cv, alarm)
    # l'escriptori del capatàs ara és un moble: a la paret, el maó de sempre
    net = Canvas(light=_tex_light(alarm))
    _murs(net)
    cv.img.paste(net.img.crop((372, 142, 448, 212)), (372, 142))
    return cv.img


@functools.lru_cache(maxsize=None)
def _caldera(t=0.0):
    """La caldera i el fogar (el dibuix pla), amb el foc al moment t."""
    cv = Canvas(light=_tex_light())
    PL.back(cv)
    PL.fire(cv, t)
    return cv.img


@functools.lru_cache(maxsize=None)
def _peces():
    """El flexo, el segell i el diari, plans sobre transparent (en surten els sprites)."""
    cv = Canvas(light=_tex_light(), transparent=True)
    cv.disc(429, 180, 7, 2.2, IRON, lambda nx, ny: 3.4 - nx - ny)
    for i in range(24):
        cv.put(429 + round(math.sin(i / 8) * 3), 179 - i, IRON, 3.0)
        cv.put(430 + round(math.sin(i / 8) * 3), 179 - i, IRON, 1.6)
    for y in range(147, 156):
        t = (y - 147) / 8
        half = 5 + t * 7
        for x in range(round(428 - half), round(428 + half) + 1):
            u = (x - 428) / half
            cv.put(x, y, LAMPG, 3.0 - u * 1.4 - (1 - t) * 0.6 + (1.2 if y == 148 and u < -0.2 else 0), 0.3)
    cv.hline(417, 440, 156, [(255, 236, 170)], 0, 0)
    # la tassa de cafè
    cv.rect(408, 167, 415, 176, PAPER, lambda x, y: 4.2 - (x - 408) * 0.35)
    cv.hline(408, 415, 167, IRON, 1.0)
    cv.hline(409, 414, 168, WALNUT, 0.6)
    cv.ring(417.5, 171, 2.6, PAPER, 3.0, step=20)
    # el segell (sense l'empremta ni l'ombra del terra: les fa el món)
    seg = Canvas(light=_tex_light(), transparent=True)
    PL.segell(seg)
    img = cv.img
    s = seg.img.crop((400, 213, 444, 248))
    img.alpha_composite(s, (400, 213))
    return img


LAMP_BOX = (416, 146, 442, 183)
CUP_BOX = (406, 166, 421, 177)
SEG_BOX = (400, 213, 444, 248)


# ─── Les superfícies ────────────────────────────────────────────────────────

def _mao(lvl0, seed=3):
    """Maó socarrimat en coordenades del món (s, t des del cantó de dalt): on el dibuix pla no arriba."""
    def L(s, t, P):
        row = int(t // 8)
        off = 10 if row % 2 else 0
        bx = int((s + off) // 19)
        if t % 8 > 7 or (s + off) % 19 < 1:
            return lvl0 - 1.2
        v = lvl0 + (hr(bx, row, seed) - 0.5) * 0.7
        if t % 8 < 1:
            v += 0.45
        if t < 19:
            v = 0.5 + (0.25 if (int(s) // 3 + int(t)) % 9 == 0 else 0)          # el sostre
        elif t < 53:
            v -= (53 - t) / 53 * 0.7                                            # el sutge de dalt
        if t > HW - 9:
            v = 2.0 + (hr(int(s) // 29, 77) - 0.5) * 0.5 if t > HW - 8 else 3.3  # el sòcol
        return v
    return L


def _lloses(s, t, P):
    """El terra de lloses grans, en coordenades del món: les juntes fugen i s'empetiteixen, taques i esquerdes."""
    x, z = P[0], P[2]
    row = math.floor(z / 34)
    off = 22 if row % 2 else 0
    col = math.floor((x + off) / 46)
    fx, fz = (x + off) % 46, z % 34
    n = hr(col, row, 5)
    v = 2.3 + (n - 0.5) * 0.7 + (hr(int(x) // 3, int(z) // 2, row) - 0.5) * 0.2
    if hr(int(x) // 6, int(z) // 4, 7) > 0.9:
        v -= 0.35                                                       # taques d'oli i de sutge
    if hr(col, row, 9) > 0.8 and abs(fx - 8 - fz * 0.9 - hr(col, row, 10) * 10) < 0.7:
        v -= 0.9                                                        # una esquerda
    if fx < 1.2 or fz < 1.2:
        return 0.8
    if fz < 2.4:
        v += 0.35                                                       # el cantell il·luminat
    return v


def _cyl(sid, e, cx, cz, r, y0, y1, n, tex=None, ramp=COPPER, lvl=2.4, a0=-math.pi, a1=math.pi):
    """Un cilindre vertical de n cares (la caldera): `tex(a0, a1)` → kwargs de quad (la textura de cada cara)."""
    def P(a, y):
        return (cx + r * math.sin(a), y, cz - r * math.cos(a))
    for i in range(n):
        aa = a0 + (a1 - a0) * i / n
        ab = a0 + (a1 - a0) * (i + 1) / n
        kw = tex(aa, ab) if tex else None
        if kw is None:
            kw = {'ramp': ramp, 'lvl': lvl}
        e.quad(sid, P(aa, y1), P(ab, y1), P(ab, y0), P(aa, y0), **kw)


def escena(cv, estat=frozenset(), t=0.0):
    """Tota la sala, de lluny a prop. `estat`: els decorats que hi són ('segell', 'alarma'). → l'Escena."""
    alarma = 'alarma' in estat
    e = Escena(cv, CAM, _llums(alarma), ambient=-0.5)
    paret, cald = _paret(alarma), _caldera(t)
    zn = CAM.pos[2] + 40
    # la paret del fons (z = 300): a l'esquerra, maó; després, el dibuix pla (x 0..490)
    e.quad('paret_fons_esq', (XL, HW, ZW), (0, HW, ZW), (0, 0, ZW), (XL, 0, ZW), ramp=BRICK, lvl=_mao(1.6, seed=7))
    e.quad('paret_fons', (0, HW, ZW), (XC, HW, ZW), (XC, 0, ZW), (0, 0, ZW), tex=(paret, (0, 0, XC, HW)))
    # la paret de la dreta (x = 490): el dibuix pla (x 490..640) i, cap a la càmera, més maó
    e.quad('paret_dreta', (XC, HW, ZW), (XC, HW, _wz(W)), (XC, 0, _wz(W)), (XC, 0, ZW), tex=(paret, (XC, 0, W, HW)))
    e.quad('paret_dreta_prop', (XC, HW, _wz(W)), (XC, HW, ZR), (XC, 0, ZR), (XC, 0, _wz(W)), ramp=BRICK,
           lvl=_mao(1.6, seed=9))
    # el terra
    e.quad('terra', (XL, 0, ZW), (XC, 0, ZW), (XC, 0, zn), (XL, 0, zn), ramp=STONE, lvl=_lloses)
    # la llum del foc al terra, davant la boca, i (si està encès) el vermell de l'alarma
    fx, fz = FIRE_P[0], FIRE_P[2]
    e.claror((fx - 200, 0.3, fz + 10), (fx + 200, 0.3, fz + 10), (fx + 200, 0.3, fz - 220), (fx - 200, 0.3, fz - 220),
             (255, 150, 60), lambda s, t: 0.55 * max(0.0, 1 - math.hypot((s - 200) / 1.6, t) / 150) ** 1.3)
    if alarma:
        ax, ay, az = ALARM_P
        e.claror((XC - 0.5, HW, az + 110), (XC - 0.5, HW, az - 110), (XC - 0.5, 0, az - 110), (XC - 0.5, 0, az + 110),
                 (255, 50, 40), lambda s, t: 0.42 * max(0.0, 1 - math.hypot(s - 110, t - (HW - ay)) / 100) ** 1.2)
        e.claror((XC - 160, 0.4, az + 90), (XC, 0.4, az + 90), (XC, 0.4, az - 90), (XC - 160, 0.4, az - 90),
                 (255, 50, 40), lambda s, t: 0.22 * max(0.0, 1 - math.hypot(160 - s, t - 90) / 140))
    # la foscor dels racons i de dalt
    e.foscor('racons', (XL, 0.5, ZW), (XC, 0.5, ZW), (XC, 0.5, zn), (XL, 0.5, zn),
             lambda s, t: max(0.6 * max(0.0, 1 - t / 26), 0.55 * max(0.0, 1 - (XC - XL - s) / 26)))
    e.foscor('cantonada', (XC - 70, HW, ZW - 0.5), (XC, HW, ZW - 0.5), (XC, 0, ZW - 0.5), (XC - 70, 0, ZW - 0.5),
             lambda s, t: 0.5 * max(0.0, s / 70) ** 2)
    e.foscor('cantonada2', (XC - 0.5, HW, ZW), (XC - 0.5, HW, ZW - 70), (XC - 0.5, 0, ZW - 70), (XC - 0.5, 0, ZW),
             lambda s, t: 0.5 * max(0.0, 1 - s / 70) ** 2)
    e.foscor('dalt', (XL, HW, ZW - 0.6), (XC, HW, ZW - 0.6), (XC, 0, ZW - 0.6), (XL, 0, ZW - 0.6),
             lambda s, t: 0.5 * max(0.0, 1 - t / 70))
    e.foscor('esq', (XL, HW, ZW - 0.6), (60, HW, ZW - 0.6), (60, 0, ZW - 0.6), (XL, 0, ZW - 0.6),
             lambda s, t: 0.55 * max(0.0, 1 - s / 300))
    # ─ la caldera: el fogar de maó amb la boca, i el cos de coure (un cilindre separat de la paret) ─
    bx, bz, br = BOILER
    x0, x1, z0, z1, fh = FOGAR
    # l'ombra del foc: la caldera en fa una de llarga cap enrere, a la paret i al terra
    e.foscor('ombra_caldera', (x0 - 10, 0.6, ZW), (x1 + 10, 0.6, ZW), (x1 + 10, 0.6, z0 - 8), (x0 - 10, 0.6, z0 - 8),
             lambda s, t: 0.55 * min(1.0, max(0.0, (ZW - z0 + 8 - t) / 16)))
    e.caixa('fogar', x0, x1, 0, fh, z0, z1, BRICK, 2.0,
            cares={'davant': {'tex': (cald, (x0, HW - fh, x1 + 1, HW))},
                   'dalt': {'ramp': IRON, 'lvl': lambda s, t, P: 2.6 - (0.8 if int(s) % 9 == 0 else 0)},
                   'esquerra': {'ramp': BRICK, 'lvl': _mao(2.0, seed=12)},
                   'dreta': {'ramp': BRICK, 'lvl': _mao(1.6, seed=13)}})
    yb, yt = BODY

    def tex_cos(aa, ab):
        if aa < -math.pi / 2 or ab > math.pi / 2:
            return None
        return {'tex': (cald, (PL.CX + PL.HALF * math.sin(aa), PL.FLOOR_Y - yt, PL.CX + PL.HALF * math.sin(ab),
                               PL.FLOOR_Y - yb))}
    _cyl('caldera', e, bx, bz, br, yb, yt, 28, tex=tex_cos, lvl=1.4)
    # la cúpula: anelles de coure cada cop més estretes, i la tapa
    for k in range(5):
        ra, rb = br * math.cos(k / 5 * 1.3), br * math.cos((k + 1) / 5 * 1.3)
        ya, yb_ = yt + 19 * math.sin(k / 5 * 1.3) / math.sin(1.3), yt + 19 * math.sin((k + 1) / 5 * 1.3) / math.sin(1.3)
        for i in range(24):
            aa, ab = -math.pi + 2 * math.pi * i / 24, -math.pi + 2 * math.pi * (i + 1) / 24
            Pa = lambda a, r, y: (bx + r * math.sin(a), y, bz - r * math.cos(a))  # noqa: E731
            e.quad('caldera', Pa(aa, rb, yb_), Pa(ab, rb, yb_), Pa(ab, ra, ya), Pa(aa, ra, ya), ramp=COPPER,
                   lvl=2.0 + k * 0.35 - abs(math.sin((aa + ab) / 2 + 0.5)) * 0.8)
    rt = br * math.cos(1.3)
    e.quad('caldera', (bx - rt, yt + 19, bz + rt), (bx + rt, yt + 19, bz + rt), (bx + rt, yt + 19, bz - rt),
           (bx - rt, yt + 19, bz - rt), ramp=COPPER, lvl=3.0, forma=lambda s, t: (s - rt) ** 2 + (t - rt) ** 2 < rt * rt)
    # la vora de baix del cos, damunt el fogar
    _cyl('caldera', e, bx, bz, br + 2, yb, yb + 4, 28, ramp=IRON, lvl=2.6)
    # el tub de sortida cap al sostre, la vàlvula de seguretat i el xiulet
    e.tub('caldera', (bx - 4, yt + 17, bz + 6), (bx - 4, HW + 10, bz + 6), 9, COPPER, 2.6, brides=40)
    e.tub('caldera', (bx + 34, yt + 8, bz - 18), (bx + 34, yt + 26, bz - 18), 3, GOLD, 3.2)
    e.tub('caldera', (bx + 34, yt + 26, bz - 18), (bx + 34, yt + 30, bz - 18), 5, GOLD, 3.6)
    # la canonada de la vàlvula entra a la caldera pel costat
    e.tub('caldera', (248 + 4, _y(160), ZW - 2), (bx + br - 2, _y(160), bz + 10), 4, COPPER, 2.4)
    # ─ la pila de carbó al costat del fogar, la pala clavada i trossos escampats ─
    cxp, czp = COAL_PILE
    e.foscor('ombra_carbo', (cxp - 46, 0.6, czp + 34), (cxp + 46, 0.6, czp + 34), (cxp + 46, 0.6, czp - 34),
             (cxp - 46, 0.6, czp - 34), lambda s, t: 0.6 * max(0.0, 1 - ((s - 46) / 46) ** 2 - ((t - 34) / 34) ** 2) * 1.5)
    rnd = random.Random(3)
    for k in range(9):
        a, d = rnd.uniform(0, 6.28), rnd.uniform(0, 1) ** 0.7 * 26
        e.roca('carbo', (cxp + math.cos(a) * d, 0, czp + math.sin(a) * d * 0.7), 13 - d * 0.25, COAL, lvl=2.2,
               llum_dir=(0.7, -0.6), aplana=0.7, seed=k + 2)
    for k in range(14):
        a, d = rnd.uniform(0, 6.28), rnd.uniform(28, 60)
        e.roca('carbo', (cxp + 20 + math.cos(a) * d, 0, czp - 10 + math.sin(a) * d * 0.6), rnd.uniform(1.5, 3.2), COAL,
               lvl=2.4, aplana=0.6, seed=k + 20)
    e.cable('pala', [(cxp + 14, 4, czp - 6), (cxp + 22, 40, czp - 2), (cxp + 28, 62, czp + 1)], WALNUT, 3.0, gruix=3.0)
    e.caixa('pala', cxp + 24, cxp + 33, 60, 64, czp - 2, czp + 4, WALNUT, 3.4)
    # ─ l'escriptori del capatàs, girat: el tauler, el faldó amb el calaixet, les potes; el flexo, el cafè i el diari ─
    cx, cz, w, d, h, a = DESK
    e.foscor('ombra_taula', _desk_pt(-w / 2 - 6, 0.6, d / 2 + 12), _desk_pt(w / 2 + 14, 0.6, d / 2 + 12),
             _desk_pt(w / 2 + 14, 0.6, -d / 2 - 6), _desk_pt(-w / 2 - 6, 0.6, -d / 2 - 6),
             lambda s, t: 0.55 * max(0.0, 1 - ((s - (w + 20) / 2) / ((w + 20) / 2)) ** 4 - ((t - (d + 18) / 2) / ((d + 18) / 2)) ** 4))
    for lx in (-w / 2 + 4, w / 2 - 4):
        for lz in (-d / 2 + 4, d / 2 - 4):
            P = _desk_pt(lx, 0, lz)
            e.caixa_girada('taula', P[0], P[2], 4, 4, h - 4, a, WALNUT, 2.4,
                           cares={'davant': {'ramp': WALNUT, 'lvl': 2.8}, 'esquerra': {'ramp': WALNUT, 'lvl': 2.2}})

    def faldo(s, t, P):
        v = 2.4 + (hr(int(s) // 3, 71) - 0.5) * 0.25
        if abs(s - w / 2) < 9 and 1.5 < t < 6.5:
            v = 3.4 + (0.6 if t < 2.5 else 0) - (1.2 if t > 5.5 else 0)       # el calaixet
            if abs(s - w / 2) < 1.5 and 3 < t < 5:
                return 4.4
        return v
    e.caixa_girada('taula', cx, cz, w - 6, d - 6, 8, a, WALNUT, 1.8, y0=h - 12,
                   cares={'davant': {'ramp': WALNUT, 'lvl': faldo}, 'esquerra': {'ramp': WALNUT, 'lvl': 1.6}})
    e.caixa_girada('taula', cx, cz, w, d, 4, a, WALNUT, 3.0, y0=h - 4,
                   cares={'dalt': {'ramp': WALNUT, 'lvl': lambda s, t, P: 3.3 + (hr(int(s) // 5, 61) - 0.5) * 0.4
                                   + (hr(int(s), int(t) // 3, 62) - 0.5) * 0.15},
                          'davant': {'ramp': WALNUT, 'lvl': 4.0}, 'esquerra': {'ramp': WALNUT, 'lvl': 2.6}})
    # el diari plegat
    np_ = [_desk_pt(lx, h + 0.4, lz) for lx, lz in ((-26, 8), (-4, 10), (-2, -6), (-24, -8))]
    e.quad('diari', *np_, ramp=PAPER, lvl=lambda s, t, P: 3.4 - (1.0 if int(s) % 4 == 0 and 2 < t < 14 else 0))
    pk = _peces()
    e.sprite('tassa', pk.crop(CUP_BOX), (414 - CUP_BOX[0], 176 - CUP_BOX[1]), _desk_pt(4, h, -4))
    e.sprite('flexo', pk.crop(LAMP_BOX), (429 - LAMP_BOX[0], 182 - LAMP_BOX[1]), _desk_pt(20, h, 4))
    # el segell (decorat), dret a terra, amb l'empremta vermella
    if 'segell' in estat:
        sx, sz = SEGELL
        e.quad('segell', (sx + 6, 0.5, sz + 2), (sx + 18, 0.5, sz + 2), (sx + 18, 0.5, sz - 6), (sx + 6, 0.5, sz - 6),
               ramp=RED, lvl=lambda s, t, P: 2.2 if (s < 1 or s > 11 or t < 1 or t > 7) and hr(int(s), int(t), 2) > 0.2
               else -9, forma=lambda s, t: (s < 1 or s > 11 or t < 1 or t > 7) and hr(int(s), int(t), 2) > 0.2)
        e.foscor('segell', (sx - 14, 0.6, sz + 8), (sx + 14, 0.6, sz + 8), (sx + 14, 0.6, sz - 8), (sx - 14, 0.6, sz - 8),
                 lambda s, t: 0.6 * max(0.0, 1 - ((s - 14) / 14) ** 2 - ((t - 8) / 8) ** 2) * 1.5)
        e.sprite('segell', pk.crop(SEG_BOX), (420 - SEG_BOX[0], 247 - SEG_BOX[1]), (sx, 0, sz))
    # ─ la vagoneta de carbó, girada, amb les rodes i el carbó a dalt ─
    vx, vz, vw, vd, vh, va = VAG
    c_, s_ = math.cos(va), math.sin(va)

    def Pv(lx, y, lz):
        return (vx + lx * c_ - lz * s_, y, vz + lx * s_ + lz * c_)
    e.foscor('ombra_vagoneta', Pv(-vw / 2 - 8, 0.6, vd / 2 + 10), Pv(vw / 2 + 8, 0.6, vd / 2 + 10),
             Pv(vw / 2 + 8, 0.6, -vd / 2 - 6), Pv(-vw / 2 - 8, 0.6, -vd / 2 - 6),
             lambda s, t: 0.6 * max(0.0, 1 - ((s - vw / 2 - 8) / (vw / 2 + 8)) ** 4 - ((t - vd / 2 - 8) / (vd / 2 + 8)) ** 4))

    def planxa(base):
        def L(s, t, P):
            v = base + (hr(int(s) // 4, int(t) // 4, 31) - 0.5) * 0.4
            if int(s) % 14 == 0 or t < 2:
                v += 0.9                                                  # els reforços
            if int(s) % 14 == 2 and int(t) % 6 == 3:
                v += 1.6                                                  # els reblons
            if hr(int(s) // 2, int(t) // 3, 33) > 0.9:
                return v - 0.5
            return v
        return L
    for lx in (-vw / 2 + 10, vw / 2 - 10):
        for lz in (vd / 2 + 1, -vd / 2 - 1):                              # les rodes (de lluny a prop)
            e.tub('vagoneta', Pv(lx, 7, lz), Pv(lx, 7, lz + (2 if lz > 0 else -2)), 7, IRON, 2.2)
    e.caixa_girada('vagoneta', vx, vz, vw, vd, vh, va, RUST, 2.0, y0=7,
                   cares={'davant': {'ramp': RUST, 'lvl': planxa(2.2)}, 'esquerra': {'ramp': RUST, 'lvl': planxa(2.8)},
                          'dreta': {'ramp': RUST, 'lvl': planxa(1.4)},
                          'dalt': {'ramp': COAL, 'lvl': lambda s, t, P: 1.8 + (hr(int(s) // 3, int(t) // 3, 4) - 0.5) * 2.2
                                   - (1.6 if s < 2.5 or t < 2.5 or s > vw - 2.5 or t > vd - 2.5 else 0)}})
    for k in range(5):
        e.roca('vagoneta', Pv(-16 + k * 8, vh + 7, (k % 2) * 6 - 3), 9 - abs(k - 2) * 1.5, COAL, lvl=2.0,
               aplana=0.6, seed=40 + k)
    # ─ primer pla: la columna reblada a l'esquerra i els sacs de carbó a la dreta ─
    FOSC = [(4, 3, 6), (10, 7, 10), (18, 12, 14), (28, 18, 18), (40, 26, 22), (54, 36, 28)]
    e.tub('primer_pla', (75, -10, -60), (75, HW + 60, -60), 16, FOSC, 2.0, brides=46, llum_dir=(1.0, 0.2))
    for cxs, czs, rr, sd in ((430, -40, 30, 4), (478, -20, 26, 5), (392, -66, 24, 6)):
        e.roca('primer_pla', (cxs, 0, czs), rr, FOSC, lvl=2.4, llum_dir=(-0.8, -0.5), aplana=0.75, seed=sd)
    return e


# ─── Composició ─────────────────────────────────────────────────────────────

def _render(estat=frozenset(), t=0.0):
    cv = Canvas(light=LIGHT)
    cv.S = 1                                                       # (tres_d: un píxel de sala per píxel real)
    e = escena(cv, estat, t)
    _to_foc(cv.img)
    cv.rect(0, BOTTOM + 1, W - 1, H - 1, [(0, 0, 0)], 0, lit=0)    # la barra de verbs: negre
    return cv.img, e


def _proj(P):
    u, v, _ = CAM.projecta(P)
    return u, v


def _to_foc(img):
    """El to taronja del foc a tota la meitat esquerra (en pantalla, com al dibuix pla)."""
    import numpy as np
    a = np.asarray(img).astype(np.float32)
    fx, fy = _proj(FIRE_P)
    yy, xx = np.mgrid[0:a.shape[0], 0:a.shape[1]]
    d = np.hypot(xx - fx, (yy - fy) * 1.1)
    k = (np.clip(1 - d / 360, 0, 1) ** 1.8 * 0.16)[..., None]
    a[..., :3] = a[..., :3] + (np.array([255, 140, 60], np.float32) - a[..., :3]) * k
    img.paste(Image.fromarray(a.clip(0, 255).astype(np.uint8), 'RGBA'))


@functools.lru_cache(maxsize=None)
def _base():
    return _render()


def bg(cv):
    cv.img.paste(_base()[0])
    cv.P = cv.img.load()


def _decorat(*estat, box=None):
    def draw(cv):
        img, _ = _render(frozenset(estat))
        cv.img.alpha_composite(frame_diff(img, _base()[0], box))
        cv.P = cv.img.load()
    return draw


PROPS = {
    'segell': _decorat('segell'),
    'alarma_encesa': _decorat('alarma', box=(330, 0, W, BOTTOM + 1)),
}


# ─── Animació: el foc respira, les guspires pugen i el vapor s'escapa ──────

def _vapor(t):
    """El vapor (en pantalla, a la mida de la profunditat): la vàlvula de seguretat de la caldera i la brida."""
    bx, bz, br = BOILER
    cv = Canvas(light=_tex_light(), transparent=True)
    for P, puffs in ((( bx + 34, BODY[1] + 30, bz - 18), [(0, 0, 5, 0.9), (7, -7, 8, 0.75), (18, -11, 11, 0.55),
                                                            (32, -12, 13, 0.35)]),
                     ((252, _y(79), ZW - 6), [(0, 0, 4, 0.8), (8, -6, 7, 0.6), (19, -11, 8, 0.35)])):
        u, v = _proj(P)
        k = CAM.escala(P)
        steam(cv, drift([(u + dx * k, v + dy * k, r * k, a) for dx, dy, r, a in puffs], (t * 2) % 1), lit=0.6)
    return cv.img


def _ambient_frames(n=16):
    base, e = _base()
    out = []
    for i in range(n):
        t = i / n
        img = base.copy()
        img.alpha_composite(e.capa(_caldera(t), {'fogar', 'caldera'}))
        img.alpha_composite(_vapor(t))
        _to_foc_frame = img
        out.append(frame_diff(_to_foc_frame, base))
    return out


ANIMS = {'ambient': {'frames': _ambient_frames, 'frameDuration': 110}}


def _amo(ids):
    def mask(x, y):
        _, e = _base()
        return e.ids[e.amo[y * e.cv.w + x]] in ids
    return mask


def _p(x, z, y=0.0):
    u, v, _ = CAM.projecta((x, y, z))
    return round(u), round(v)


# Capes del davant: el primer pla (sempre davant), l'escriptori del capatàs i la vagoneta.
_ALARMA = ('alarma_encesa',)
FRONT = [
    {'id': 'davant', 'mask': _amo({'primer_pla'}), 'baseline': 999, 'zIndex': 20, 'variants': _ALARMA},
    {'id': 'davant_taula', 'mask': _amo({'taula', 'flexo', 'tassa', 'diari'}), 'baseline': _p(DESK[0], DESK[1])[1],
     'zIndex': 20, 'variants': _ALARMA},
    {'id': 'davant_vagoneta', 'mask': _amo({'vagoneta'}), 'baseline': _p(VAG[0], VAG[1])[1], 'zIndex': 20},
]


# ─── Geometria (coordenades de sala, projectades) ────────────────────────────

def _rect_mon(*Ps):
    pts = [CAM.projecta(P) for P in Ps]
    return (max(0, round(min(p[0] for p in pts))), max(0, round(min(p[1] for p in pts))),
            min(W - 1, round(max(p[0] for p in pts))), min(BOTTOM, round(max(p[1] for p in pts))))


def _escala_a(v):
    """L'escala d'un personatge amb els peus a la y de pantalla `v` (al terra, la profunditat només depèn de v)."""
    lo, hi = 1.0, 3000.0
    for _ in range(60):
        z = (lo + hi) / 2
        if CAM.projecta((260, 0, z))[1] > v:
            lo = z
        else:
            hi = z
    return CAM.escala((260, 0, (lo + hi) / 2))


# El terra on es camina (al món): davant la porta del magatzem, per davant de la caldera i el carbó, fins a la porta
# del moll i la de la cambra; per davant, fins on el personatge fa ≈1,2.
def _z_escala(k, x=300):
    """La z del terra on un personatge fa escala k."""
    lo, hi = -2000.0, 3000.0
    for _ in range(60):
        z = (lo + hi) / 2
        if CAM.escala((x, 0, z)) > k:
            lo = z
        else:
            hi = z
    return z


V12 = round(CAM.projecta((300, 0, _z_escala(1.2)))[1])     # la y de pantalla on un personatge fa 1,2


def _retalla_v(poly, vmax):
    """Un polígon de pantalla retallat per la pantalla i per sota de la y `vmax` (el terra més a prop és per al primer
    pla, on el personatge passaria d'1,2)."""
    for keep, cut in ((lambda p: p[1] <= vmax, lambda a, b: (a[0] + (b[0] - a[0]) * (vmax - a[1]) / (b[1] - a[1]), vmax)),
                      (lambda p: p[0] >= 0, lambda a, b: (0, a[1] + (b[1] - a[1]) * (0 - a[0]) / (b[0] - a[0]))),
                      (lambda p: p[0] <= W - 1, lambda a, b: (W - 1, a[1] + (b[1] - a[1]) * (W - 1 - a[0]) / (b[0] - a[0])))):
        out = []
        for A, B in zip(poly, poly[1:] + poly[:1]):
            if keep(A):
                out.append(A)
            if keep(A) != keep(B):
                out.append(cut(A, B))
        poly = out
    return [(round(u), round(v)) for u, v in poly]


WALK_MON = [(-200, 286), (92, 286), (93, 180), (46, 178), (46, 118), (262, 120), (262, 286), (482, 286),
            (482, -300), (-200, -300)]
_WALK = _retalla_v([CAM.projecta((x, 0, z))[:2] for x, z in WALK_MON], V12)
_V_FONS, _V_PROP = min(v for _, v in _WALK), max(v for _, v in _WALK)


def _forat(cx, cz, w, d, a, m=8):
    c, s = math.cos(a), math.sin(a)
    return [_p(cx + lx * c - lz * s, cz + lx * s + lz * c) for lx, lz in ((-w / 2 - m, -d / 2 - m), (w / 2 + m, -d / 2 - m),
                                                                          (w / 2 + m, d / 2 + m), (-w / 2 - m, d / 2 + m))]


_DOOR_M = (11, 77, _y(87))                          # la porta del magatzem: x0, x1, y de dalt
_DOOR_C = (_wz(563), _wz(629), _y(88))              # la porta de la cambra: z0, z1, y de dalt
_DOOR_L = (279, 364, _y(133))                       # la porta del moll
_TAULER = (265, 375, _y(43), _y(117))

# (tasca 327) L'escriptori i, davant, en Tul a la cadira, retallats del contorn del terra (no com a forat): entre tots
# dos no s'hi passa (l'Iri s'hi enganxava, mig dins seu), ni per darrere de l'escriptori; el camí li passa pel davant.
# (Un forat que surt per la vora del terra el camí el travessava per la vora.)
def _walk_tul(walk):
    out = []
    for q in walk:
        if q == (404, 111):
            out += [(356, 117), (367, 216), (422, 216), (430, 128)]
        else:
            out.append(q)
    return out


GEOMETRIA = {
    'things': {
        'porta_magatzem': {'rect': _rect_mon((_DOOR_M[0], _DOOR_M[2], ZW), (_DOOR_M[1], 0, ZW)), 'walk': _p(44, 270)},
        # (tasca 260) davant de la porta i a la dreta de l'escriptori: a la cantonada del darrere, qui entrava de la
        # cambra quedava tapat per l'escriptori d'en Tul
        'porta_cambra': {'rect': _rect_mon((XC, _DOOR_C[2], _DOOR_C[0]), (XC, 0, _DOOR_C[1])), 'walk': (440, 150)},
        'tauler': {'rect': _rect_mon((_TAULER[0], _TAULER[2], ZW), (_TAULER[1], _TAULER[3], ZW)), 'walk': _p(320, 262)},
        'alarma': {'rect': _rect_mon((XC, _y(52), _wz(578)), (XC, _y(88), _wz(616))), 'walk': (440, 150)},
        'segell': {'rect': _rect_mon(*[(SEGELL[0] + dx, y, SEGELL[1] + dz) for dx in (-12, 20) for dz in (-8, 8)
                                       for y in (0, 34)]),
                   'walk': _p(SEGELL[0] - 26, SEGELL[1] - 12)},
        'porta_moll': {'rect': _rect_mon((_DOOR_L[0], _DOOR_L[2], ZW), (_DOOR_L[1], 0, ZW)), 'walk': _p(321, 276)},
    },
    'spawns': {'iri': _p(200, 90), 'capatas': _p(VAG[0] + 83, VAG[1] - 41), 'sic': _p(452, 214)},
    'walkable': _walk_tul(_WALK),
    'forats': [_forat(VAG[0], VAG[1], VAG[2], VAG[3], VAG[5], m=6)],
    'floorSquash': 0.4,                            # (la càmera, picada: el terra es veu aixafat)
    # L'ombra de contacte: la llum dominant és el foc (el punt del terra davant la boca); llarga, cap enrere.
    'characterShadow': {'enabled': True, 'color': '#0c0608', 'alpha': 0.45, 'squash': 0.4, 'core': 0.6,
                        'light': {'x': _p(FIRE_P[0], FIRE_P[2])[0], 'y': _p(FIRE_P[0], FIRE_P[2])[1], 'stretch': 0.9,
                                  'reach': 200}},
    'regions': [{'id': 'perspectiva', 'active': True, 'scaleEnabled': True, 'scaleWalkSpeed': True,
                 'scaleTop': round(_escala_a(_V_FONS - 2), 3), 'scaleBottom': round(_escala_a(_V_PROP + 2), 3),
                 'points': [(0, _V_FONS - 2), (W - 1, _V_FONS - 2), (W - 1, _V_PROP + 2), (0, _V_PROP + 2)]}],
    # la llum de la sala sobre els personatges, en temps d'execució
    'characterLights': {
        'ambient': '#7a6a66',
        'lights': [
            {'x': _p(FIRE_P[0], FIRE_P[2], FIRE_P[1])[0], 'y': _p(FIRE_P[0], FIRE_P[2], FIRE_P[1])[1], 'radius': 300,
             'color': '#ff9640', 'intensity': 1.2},                                     # el foc
            {'x': _p(LAMP_P[0], LAMP_P[2], LAMP_P[1])[0], 'y': _p(LAMP_P[0], LAMP_P[2], LAMP_P[1])[1], 'radius': 110,
             'color': '#ffe29a', 'intensity': 0.7},                                     # el flexo
            {'x': _p(ALARM_P[0], ALARM_P[2], ALARM_P[1])[0], 'y': _p(ALARM_P[0], ALARM_P[2], ALARM_P[1])[1],
             'radius': 170, 'color': '#ff3c28', 'intensity': 1.0, 'whenPropVisible': 'alarma_encesa'},
        ],
    },
}

# Coses per mirar (tasca 065): rectangles de pantalla i el punt on s'hi va.
GEOMETRIA['things'].update({
    'caldera': {'rect': (135, 20, 255, 145), 'walk': (190, 160)},
    'foc': {'rect': (165, 145, 228, 185), 'walk': (200, 190)},
    'vagoneta': {'rect': (272, 150, 333, 205), 'walk': (300, 215)},
    'rellotge': {'rect': (356, 12, 376, 33), 'walk': GEOMETRIA['things']['tauler']['walk']},
})
