"""
La caixa de cadenes de l'Arenga (Escena 6, onze de la nit). EN 3D (hd640/tres_d.py), a 1×.

Fosca, estreta, alta i rovellada, vista des de dalt de la cantonada de popa, com qui treu el cap a un pou:
  - al fons, el **mamparo de col·lisió** (el dibuix pla de sempre, projectat), amb els **graons** soldats que pugen
    (en volum) fins a l'**escotilla** del sostre, que queda fora del quadre: se'n veu la llum groga de coberta, que
    baixa en con per damunt dels graons i s'escampa per terra;
  - els costats del buc, inclinats (la proa es tanca cap a baix), amb les quadernes que fugen;
  - a l'esquerra, la **cadena** de l'àncora que baixa de l'escobén i s'apila (baula per baula, en volum), i un tram
    que ve per terra cap a la càmera;
  - a terra, la reixa de fusta damunt del fang, i un bassal sota la gota que cau del sostre;
  - el decorat `manta` (Escena 6): el rotllo de cap vell on seu la Juana, la manta amb plecs i el paper de l'entrepà;
  - primer pla: el durmen de popa, fosc, arran de la vora de baix, amb baules soltes.
La llum: el con groc de l'escotilla (pols a l'aire) i tota la resta a les fosques.

El món: x a la dreta, y amunt (0 = la reixa), z cap al fons (250 = el mamparo); 1 unitat = 1 píxel de sala a la
distància on un personatge fa ≈110 px (escala 1).
"""
import functools
import math
import random

import hd640  # noqa: F401  (abans de cap hd.rooms: posa la llibreria a 640×360)

from hd.pix import Canvas, Light, W, H, hr, mix, PAPER
from hd.rooms.arenga import CAB, DARK, REDP
from hd.rooms.comu import _diff
from hd.rooms.exterior import fbm
from hd640.rooms import caixa_cadenes_pla_comu as PL
from hd640.rooms.caixa_cadenes_pla_comu import HULL, CHAIN, MUD, WOOL, WOOD, NIGHT
from hd640.rooms.pallol import anella, rotllo
from hd640.tres_d import Camera, Escena, Llum

BOTTOM = 259                                       # la sala acaba aquí (a sota, la barra de verbs)
ZW = 250                                           # el mamparo del fons
TOP = 19                                           # al dibuix pla, on comença el mamparo (a sobre, els baos)
HT = PL.FLOOR_Y - TOP                              # l'alçada del mamparo pla (184)
HW = 240                                           # l'alçada del sostre (a sobre del dibuix pla, més planxa)
FX0 = 40                                           # al dibuix pla, la x que va a la x = -20 del món
XL0, XR0 = 40, 470                                 # els costats del buc, a terra
INCL = 60 / HT                                     # (i s'obren cap amunt: 60 unitats cada 184)
XL1, XR1 = XL0 - INCL * HW, XR0 + INCL * HW        # al sostre
HATCH = (282, 352, ZW - 44)                        # l'escotilla: x0, x1, z del cantó de davant (l'altre, el mamparo)
RUNGS = (300, 334)                                 # els graons: x0, x1
PILE = (128, 168, 92, 104)                         # la pila de cadena: x, z, radi, alçada
HAWSE = (136, 186)                                 # el tub de l'escobén (x, z), al sostre
DRIP = (236, 150)                                  # on cau la gota (x, z)
HAWSER = (412, 174)                                # el rotllo on seu la Juana (x, z)

CAM = Camera(pos=(300, 180, -230), yaw=-0.1, pitch=0.14, f=420, centre=(320, 40))

LIGHT = Light(ambient=0.0, vignette=None, floor_fade=None)  # (la llum és la del món: la de l'Escena)
TL = Light(ambient=-0.3, vignette=None, floor_fade=None)     # la llum de les textures
HC = ((HATCH[0] + HATCH[1]) / 2, HW, (HATCH[2] + ZW) / 2)    # el centre de la boca de l'escotilla
LLUMS = [Llum((HC[0], HW - 4, HC[2]), 330, 2.6, power=1.5),          # la llum de coberta, que baixa
         Llum((HC[0] + 30, 30, HC[2] - 60), 150, 0.9, power=1.6)]     # la que rebota a terra
LAMPG = [(160, 120, 40), (255, 210, 110), (255, 246, 200)]
FOSC = [(2, 2, 2), (6, 4, 4), (12, 8, 7), (20, 12, 10), (30, 18, 14), (42, 26, 18)]
ROPEJ = PL.ROPE


def _cone(y):
    """El con de llum de l'escotilla a l'alçada y: (x del centre, z del centre, mitja amplada)."""
    t = (HW - y) / HW
    return HC[0] + t * 46, HC[2] - t * 70, 30 + t * 62


# ─── Les textures ────────────────────────────────────────────────────────────

@functools.lru_cache(maxsize=None)
def _mamparo():
    """El mamparo de col·lisió, de cara (amb els reforços, les soldadures i el rovell)."""
    cv = Canvas(light=TL)
    PL.walls(cv)
    return cv.img


# ─── Les superfícies ────────────────────────────────────────────────────────

def _buc(lvl0, seed):
    """La planxa del buc, en coordenades del món (s al llarg de z, t avall pel costat): les quadernes corbes, amb
    l'ombra al costat, les juntes i el rovell."""
    def L(s, t, P):
        z = P[2]
        v = lvl0 + (hr(int(z) // 3, int(t) // 4, seed) - 0.5) * 0.5 + (fbm(z / 30, t / 24, seed) - 0.5) * 0.9
        d = (z + 12) % 58
        if d < 6:
            v += 1.0 if d < 1.5 else 0.5                               # la quaderna
            if int(t) % 14 == 0:
                v += 1.2                                               # reblons
        elif d < 10:
            v -= 0.8                                                   # l'ombra de la quaderna
        if abs(t - 70) < 1:
            v -= 1.2
        if hr(int(z) // 2, 5, seed) > 0.9 and (t % 60) < 30 * hr(int(z) // 2, 6, seed):
            v += 0.5                                                   # regalims de rovell
        return v
    return L


def _reixa(s, t, P):
    """La reixa de fusta damunt del fang: llistons al llarg de z, amb nusos, i el fang entre llistó i llistó."""
    x, z = P[0], P[2]
    u = (x + 6) % 29
    if u >= 20:
        return 1.6 + (hr(int(x) // 3, int(z) // 3, 51) - 0.5) * 0.8                 # el fang (rampa MUD: vegeu ramp)
    v = 2.8 + (hr(int((x + 6) // 29), int(z) // 40, 2) - 0.5) * 0.7 + (fbm(x / 12, z / 50, 3) - 0.5) * 0.8
    if u < 1.5:
        v += 0.8
    elif u > 18:
        v -= 0.9
    if int(z + hr(int((x + 6) // 29), 7) * 90) % 90 < 1.2:
        v -= 1.4                                                       # junta de testa
    if hr(int((x + 6) // 29), int(z) // 6, 52) > 0.95:
        v -= 1.0                                                       # un nus
    return v


def _baula(e, sid, c, ang, tilt, lvl, rx=7.0, rz=4.4, gruix=2.6):
    """Una baula de cadena al món: un anell ovalat al voltant de `c`, girat `ang` (vertical) i inclinat `tilt`."""
    ca, sa = math.cos(ang), math.sin(ang)
    ct, st = math.cos(tilt), math.sin(tilt)
    u = (ca, 0.0, sa)                                                  # l'eix llarg, horitzontal
    v = (-sa * ct, st, ca * ct)                                        # l'eix curt, inclinat
    pts = []
    for k in range(13):
        a = 2 * math.pi * k / 12
        pts.append((c[0] + math.cos(a) * rx * u[0] + math.sin(a) * rz * v[0],
                    c[1] + math.cos(a) * rx * u[1] + math.sin(a) * rz * v[1],
                    c[2] + math.cos(a) * rx * u[2] + math.sin(a) * rz * v[2]))
    e.cable(sid, pts, CHAIN, lvl, gruix=gruix)
    e.cable(sid, [(c[0] - v[0] * rz * 0.8, c[1] - v[1] * rz * 0.8, c[2] - v[2] * rz * 0.8),
                  (c[0] + v[0] * rz * 0.8, c[1] + v[1] * rz * 0.8, c[2] + v[2] * rz * 0.8)], CHAIN, lvl - 0.4,
            gruix=gruix * 0.7)                                         # el travesser


def _llum_a(P):
    """Quanta llum de l'escotilla arriba a un punt (per a les coses que es pinten sense la llum de l'escena)."""
    cx, cz, hw = _cone(max(0.0, min(HW, P[1])))
    d = math.hypot(P[0] - cx, P[2] - cz) / (hw * 1.6)
    return max(0.0, 1 - d) * 1.8


def pila(e, sid):
    """La pila de cadena: un munt fosc i, a sobre, les baules, de les del darrere a les del davant."""
    px, pz, R, Hh = PILE
    e.roca(sid, (px, 0, pz + 6), R * 0.8, FOSC, lvl=1.4, llum_dir=(0.6, -0.5), aplana=(Hh - 8) / (R * 0.8 * 1.6), seed=6)
    rnd = random.Random(7)
    links = []
    for i in range(420):
        a = rnd.random() * 2 * math.pi
        r = R * math.sqrt(rnd.random()) * 0.98
        x, z = px + math.cos(a) * r, pz + math.sin(a) * r * 0.85
        h = Hh * max(0.0, 1 - (r / R) ** 1.5)
        y = max(2.5, h - rnd.random() * 6)
        links.append((x, y, z, rnd.uniform(0, math.pi), rnd.uniform(0.2, 1.4) * rnd.choice((-1, 1))))
    links.sort(key=lambda L: -e.cam.vista((L[0], L[1], L[2]))[2])
    for x, y, z, ang, tilt in links:
        lvl = 2.6 + y / Hh * 1.6 + _llum_a((x, y, z)) + (hr(int(x * 3), int(z * 3), 4) - 0.5) * 1.0
        _baula(e, sid, (x, y, z), ang, tilt, lvl)
    # la cadena que penja del tub de l'escobén fins a dalt de la pila
    hx, hz = HAWSE
    y = HW - 30
    k = 0
    while y > Hh - 8:
        _baula(e, sid, (hx + math.sin(k * 0.5) * 1.2, y, hz), 0.0 if k % 2 else math.pi / 2, math.pi / 2,
               2.4 + _llum_a((hx, y, hz)), rx=4.6, rz=7.0, gruix=2.6)
        y -= 10
        k += 1


def manta(e):
    """El rotllo de cap vell, la manta plegada de qualsevol manera i el paper de l'entrepà (Escena 6)."""
    hx, hz = HAWSER
    e.foscor('ombra_manta', (hx - 70, 0.7, hz + 40), (hx + 60, 0.7, hz + 40), (hx + 60, 0.7, hz - 80),
             (hx - 70, 0.7, hz - 80), lambda s, t: 0.7 * max(0.0, 1 - ((s - 65) / 65) ** 2 - ((t - 60) / 60) ** 2) * 1.5)
    e.quad('manta', (hx - 20, 0.5, hz + 22), (hx + 20, 0.5, hz + 22), (hx + 20, 0.5, hz - 22), (hx - 20, 0.5, hz - 22),
           ramp=DARK, lvl=0.6, forma=lambda s, t: (s - 20) ** 2 + (t - 22) ** 2 < 16 ** 2)
    rotllo(e, 'manta', hx, hz, 30, 6, ROPEJ, 3.0, gruix=4.8, pas=4.2)

    # la manta, als peus del rotllo, una mica girada: una graella de trossos que fan plecs (la llum de l'escena
    # els pinta cadascun segons cap on mira), amb les ratlles vermelles
    a = 0.18
    c, s_ = math.cos(a), math.sin(a)
    NX, NZ, LX, LZ = 12, 6, 96, 40

    def alt(i, j):
        lx, lz = i / NX, j / NZ
        h = 2.2 + 2.6 * math.sin(lx * 9 + lz * 3) * math.sin(lz * 3.1 + 0.4) + (fbm(lx * 4, lz * 4, 4) - 0.5) * 4
        return max(0.8, h * (1 - abs(lz - 0.5) * 0.6))

    def P(i, j):
        lx, lz = i / NX * LX - LX / 2, j / NZ * LZ - LZ / 2
        return (hx - 8 + lx * c - lz * s_, alt(i, j), hz - 52 + lx * s_ + lz * c)
    for j in range(NZ - 1, -1, -1):
        for i in range(NX):
            ramp = REDP if j == 3 else WOOL
            e.quad('manta', P(i, j + 1), P(i + 1, j + 1), P(i + 1, j), P(i, j), ramp=ramp,
                   lvl=(2.4 if j == 3 else 3.0) + (hr(i, j, 5) - 0.5) * 0.4 - (0.8 if j == 0 else 0))
    # el paper de l'entrepà, una bola rebregada, i unes molles
    FOIL = [(40, 40, 44), (90, 90, 96), (150, 150, 156), (200, 200, 206), (236, 236, 240)]
    e.roca('manta', (hx + 56, 0, hz - 56), 6, FOIL, lvl=3.0, llum_dir=(-0.6, -0.7), aplana=0.8, seed=9)
    for dx, dz in ((66, -64), (70, -60)):
        e.quad('manta', (hx + dx, 0.6, hz + dz + 1), (hx + dx + 1.5, 0.6, hz + dz + 1), (hx + dx + 1.5, 0.6, hz + dz),
               (hx + dx, 0.6, hz + dz), ramp=PAPER, lvl=4.0)


def escena(cv, tex, estat=frozenset()):
    """Tota la sala, de lluny a prop. `estat`: 'manta'. → l'Escena (qui ha pintat què)."""
    e = Escena(cv, CAM, LLUMS, ambient=-0.5)
    zn = CAM.pos[2] + 60
    x0, x1, hz0 = HATCH
    # el sostre (la coberta per sota), amb el forat de l'escotilla i els baos
    e.quad('sostre', (XL1 - 40, HW, zn), (XR1 + 40, HW, zn), (XR1 + 40, HW, ZW), (XL1 - 40, HW, ZW), ramp=HULL, lvl=1.4,
           dues_cares=True, forma=lambda s, t: not (x0 < s + XL1 - 40 < x1 and t + zn > hz0))
    for bz in (40, 110, 180):
        e.caixa('baos', XL1 - 40, XR1 + 40, HW - 14, HW, bz, bz + 10, HULL, 1.6,
                cares={'sota': {'ramp': HULL, 'lvl': 1.2}, 'davant': {'ramp': HULL, 'lvl': 2.0}})
    # el mamparo del fons: el dibuix pla (els costats del buc el tapen)
    xa, xb = XL0 - INCL * HT, XR0 + INCL * HT
    e.quad('mamparo_dalt', (XL1, HW, ZW), (XR1, HW, ZW), (XR1, HT, ZW), (XL1, HT, ZW), ramp=HULL,
           lvl=lambda s, t, P: 2.6 + (hr(int(s) // 3, int(t) // 4, 41) - 0.5) * 0.5 + (fbm(s / 30, t / 20, 4) - 0.5) * 0.8
           + (0.9 if (P[0] + 48) % 69 < 6 else 0) - (1.2 if abs(t - 30) < 1 else 0))
    e.quad('mamparo', (xa, HT, ZW), (xb, HT, ZW), (xb, 0, ZW), (xa, 0, ZW),
           tex=(tex['mamparo'], (FX0, TOP, FX0 + xb - xa, PL.FLOOR_Y)))
    # els costats del buc, inclinats: la proa es tanca cap a baix
    e.quad('buc_esq', (XL1, HW, zn), (XL1, HW, ZW), (XL0, 0, ZW), (XL0, 0, zn), ramp=HULL, lvl=_buc(2.2, 3))
    e.quad('buc_dreta', (XR1, HW, ZW), (XR1, HW, zn), (XR0, 0, zn), (XR0, 0, ZW), ramp=HULL, lvl=_buc(2.0, 4))
    # el terra: el fang i la reixa
    e.quad('terra', (XL0, 0, ZW), (XR0, 0, ZW), (XR0, 0, zn), (XL0, 0, zn), ramp=WOOD,
           lvl=_reixa)
    e.foscor('fang', (XL0, 0.2, ZW), (XR0, 0.2, ZW), (XR0, 0.2, zn), (XL0, 0.2, zn),
             lambda s, t: 0.45 if (s + XL0 + 6) % 29 >= 20 else 0.0)
    # el bassal sota la gota, amb el reflex de la boca
    dx, dz = DRIP
    e.foscor('bassal', (dx - 46, 0.3, dz + 17), (dx + 46, 0.3, dz + 17), (dx + 46, 0.3, dz - 17), (dx - 46, 0.3, dz - 17),
             lambda s, t: 0.5 * min(1.0, 3 * max(0.0, 1 - ((s - 46) / (44 + hr(int(t), 1) * 4)) ** 2 - ((t - 17) / 16) ** 2)))
    e.claror((dx - 46, 0.35, dz + 17), (dx + 46, 0.35, dz + 17), (dx + 46, 0.35, dz - 17), (dx - 46, 0.35, dz - 17),
             (255, 214, 140), lambda s, t: 0.32 * max(0.0, 1 - abs(s - 54 - (t - 17) * 0.3) / 9)
             * max(0.0, 1 - ((s - 46) / 44) ** 2 - ((t - 17) / 16) ** 2))
    # la llum de coberta a terra i al mamparo, i la foscor dels racons
    cx, cz, hw = _cone(0)
    e.claror((cx - 140, 0.5, cz + 120), (cx + 140, 0.5, cz + 120), (cx + 140, 0.5, cz - 120), (cx - 140, 0.5, cz - 120),
             (255, 210, 130), lambda s, t: 0.42 * max(0.0, 1 - math.hypot(s - 140, (t - 120) * 1.2) / 140) ** 1.4)
    e.claror((HC[0] - 120, HW, ZW - 0.4), (HC[0] + 120, HW, ZW - 0.4), (HC[0] + 120, 0, ZW - 0.4), (HC[0] - 120, 0, ZW - 0.4),
             (255, 200, 120), lambda s, t: 0.38 * max(0.0, 1 - abs(s - 120) / (40 + t * 0.4)) * max(0.0, 1 - t / 230))
    e.foscor('racons', (XL0, 0.5, ZW), (XR0, 0.5, ZW), (XR0, 0.5, zn), (XL0, 0.5, zn),
             lambda s, t: max(0.6 * max(0.0, 1 - t / 30), 0.6 * max(0.0, 1 - s / 30), 0.6 * max(0.0, 1 - (XR0 - XL0 - s) / 30)))
    e.foscor('racons_sostre', (XL1, HW, ZW - 0.6), (XR1, HW, ZW - 0.6), (XR1, 0, ZW - 0.6), (XL1, 0, ZW - 0.6),
             lambda s, t: 0.5 * max(0.0, 1 - t / 50) * (0 if x0 - XL1 - 10 < s < x1 - XL1 + 10 else 1))
    # els graons soldats al mamparo, de terra a l'escotilla, i el rovell que en regalima
    r0, r1 = RUNGS
    for y in range(18, int(HW) - 6, 15):
        e.caixa('graons', r0, r1, y, y + 3, ZW - 7, ZW, CAB, 3.4,
                cares={'dalt': {'ramp': CAB, 'lvl': 4.4}, 'davant': {'ramp': CAB, 'lvl': 2.8}})
        for xx in (r0, r1 - 3):
            e.caixa('graons', xx, xx + 3, y - 4, y, ZW - 6, ZW, CAB, 2.0)
    # el tub de l'escobén, que baixa del sostre, amb la brida, i la pila de cadena
    hx, hz = HAWSE
    e.tub('cadenes', (hx, HW + 10, hz), (hx, HW - 34, hz), 12, HULL, 3.0, brides=0)
    e.tub('cadenes', (hx, HW - 34, hz), (hx, HW - 37, hz), 15, HULL, 3.6)
    pila(e, 'cadenes')
    if 'manta' in estat:
        manta(e)
    # la cadena que surt de la pila cap a la càmera, per terra (baules alternes: planes i de cantó)
    for k in range(16):
        t = k / 15
        x, z = 180 + t * 70 + math.sin(t * 5) * 12, 120 - t * 96
        _baula(e, 'cadena_terra', (x, 2.5 if k % 2 else 4.2, z), math.atan2(-96, 70) + (0.2 if k % 2 else -0.1),
               0.1 if k % 2 else 1.45, 3.0 + _llum_a((x, 0, z)), gruix=3.0)
    # primer pla: el durmen de popa, de banda a banda
    e.caixa('primer_pla', XL0 - 80, XR0 + 80, 0, 14, -6, 14, FOSC, 2.2,
            cares={'dalt': {'ramp': FOSC, 'lvl': lambda s, t, P: 3.4 - (1.2 if int(P[0]) % 61 < 2 else 0)
                            + (fbm(s / 30, t / 6, 2) - 0.5) * 0.8},
                   'davant': {'ramp': FOSC, 'lvl': 1.4}})
    for k, (x, z, a) in enumerate(((112, 40, 0.4), (96, 52, 1.7), (380, 34, 2.6), (396, 44, 0.9))):
        _baula(e, 'primer_pla', (x, 16, z), a, 0.25 if k % 2 else 1.3, 2.4, gruix=3.4)
    return e


# ─── Composició ────────────────────────────────────────────────────────────

def _proj(P):
    u, v, _ = CAM.projecta(P)
    return u, v


@functools.lru_cache(maxsize=None)
def _textures():
    return {'mamparo': _mamparo()}


def _haze(cv):
    """El con de llum de l'escotilla (pols a l'aire), en pantalla: un trapezi entre la boca i el terra."""
    from hd.pix import B4
    rows = []
    for k in range(0, 41):
        y = HW * (1 - k / 40)
        cx, cz, hw = _cone(y)
        u, v = _proj((cx, y, cz))
        rows.append((v, u, hw * CAM.escala((cx, y, cz))))
    for (va, ua, wa), (vb, ub, wb) in zip(rows, rows[1:]):
        for Y in range(max(0, int(va)), min(BOTTOM, int(vb) + 1)):
            f = (Y - va) / max(1e-3, vb - va)
            uc, w = ua + (ub - ua) * f, wa + (wb - wa) * f
            for X in range(max(0, int(uc - w)), min(W, int(uc + w) + 1)):
                c = 1 - abs(X - uc) / w
                k = 0.17 * c * (1 - Y / 360)
                if k > B4[Y & 3][X & 3] * 0.35:
                    cv.flat(X, Y, mix(cv.get(X, Y), (255, 214, 130), k))


def _render(estat=frozenset(), tex=None):
    cv = Canvas(light=LIGHT)
    escena_ = escena(cv, tex or _textures(), estat)
    _haze(cv)
    u, v = _proj((HC[0], HW - 30, HC[2]))
    cv.glow(u, max(v, 0), 90, (255, 200, 110), 0.4)
    cv.rect(0, BOTTOM + 1, W - 1, H - 1, [(0, 0, 0)], 0, lit=0)    # la barra de verbs: negre
    return cv.img, escena_


@functools.lru_cache(maxsize=None)
def _base():
    return _render()


def bg(cv):
    cv.img.paste(_base()[0])
    cv.P = cv.img.load()


def _decorat(*estat):
    """Un decorat: la sala amb aquell estat, menys la de sempre (només el que canvia)."""
    def draw(cv):
        img, _ = _render(frozenset(estat))
        cv.img.alpha_composite(_diff(img, _base()[0]))
        cv.P = cv.img.load()
    return draw


PROPS = {'manta': _decorat('manta')}


# ─── Animacions ─────────────────────────────────────────────────────────────

def _frames_pols():
    """Pols que sura al con de llum (cada mota fa un llaç tancat: el bucle no salta)."""
    img, _ = _base()
    motes = []
    for k in range(45):
        y = 10 + hr(k, 11) * (HW - 20)
        cx, cz, hw = _cone(y)
        P = (cx + (hr(k, 12) - 0.5) * hw * 1.4, y, cz + (hr(k, 17) - 0.5) * hw)
        u, v = _proj(P)
        s = CAM.escala(P)
        motes.append((u, v, (5 + hr(k, 13) * 11) * s, (4 + hr(k, 14) * 9) * s, hr(k, 15), 1 + int(hr(k, 16) * 2),
                      _proj((cx, y, cz))[0], hw * s))
    n = 48
    frames = []
    for i in range(n):
        cv = Canvas(light=LIGHT, img=img.copy())
        t = i / n
        for (cx, cy, ax, ay, ph, fx, ccx, hw) in motes:
            a = 2 * math.pi * (t + ph)
            x = round(cx + ax * math.sin(fx * a))
            y = round(cy + ay * math.sin(a + ph * 3))
            inside = max(0.0, 1 - abs(x - ccx) / hw)                   # només es veu dins la llum
            tw = 0.5 + 0.5 * math.sin(a * 2 + ph * 7)                  # i fa pampallugues
            alpha = inside ** 0.7 * (0.35 + 0.45 * tw)
            if alpha > 0.08 and 0 <= x < W and 0 <= y < BOTTOM:
                cv.flat(x, y, mix(cv.get(x, y), (255, 232, 180), alpha))
        frames.append(_diff(cv.img, img))
    return frames


WATER = (196, 178, 132)
SPARK = (240, 226, 190)


def _frames_gota():
    """Una gota: es forma al sostre, cau, esquitxa al bassal i en surten dues rodones que s'esvaeixen."""
    img, _ = _base()
    dx, dz = DRIP
    top = _proj((dx, HW, dz))
    tx, ty = round(top[0]), round(top[1])
    pool = _proj((dx, 0.3, dz))
    px, py = round(pool[0]), round(pool[1])
    s = CAM.escala((dx, 0, dz))
    n = 40
    frames = []
    for i in range(n):
        cv = Canvas(light=LIGHT, img=img.copy())
        if i < 16:                                                      # la gota s'infla
            g = i / 15
            cv.flat(tx, ty, mix(cv.get(tx, ty), WATER, 0.4 + 0.4 * g))
            if g > 0.3:
                cv.flat(tx, ty + 1, mix(cv.get(tx, ty + 1), WATER, 0.3 + 0.6 * g))
            if g > 0.6:
                cv.flat(tx - 1, ty + 1, mix(cv.get(tx - 1, ty + 1), WATER, 0.4 * g))
                cv.flat(tx, ty + 2, mix(cv.get(tx, ty + 2), WATER, 0.5 * g))
            if g > 0.85:
                cv.flat(tx, ty + 3, mix(cv.get(tx, ty + 3), SPARK, 0.8))
        elif i < 22:                                                    # cau, cada cop més de pressa
            k = (i - 15) / 6
            y = round(ty + 3 + (py - 5 - ty - 3) * k * k)
            x = round(tx + (px - tx) * k * k)
            for j in range(1 + int(k * 5)):
                if 0 <= y - j < BOTTOM:
                    cv.flat(x, y - j, mix(cv.get(x, y - j), SPARK, 0.85 - j * 0.13))
        else:                                                           # l'esquitx i les rodones
            k = i - 22
            if k < 4:
                for sx, sy in ((-2, -3 - k), (2, -3 - k), (0, -4 - k), (-3, -1 - k // 2), (3, -1 - k // 2)):
                    x, y = px + sx * (1 + k // 2), py + sy
                    cv.flat(x, y, mix(cv.get(x, y), SPARK, 0.7 - k * 0.15))
            for r0 in (0, 5):
                r = (k - r0) * 1.9 * s
                if 1 <= r <= 20 * s:
                    fade = 1 - r / (21 * s)
                    for a in range(0, 360, 4):
                        x = round(px + math.cos(math.radians(a)) * r * 1.8)
                        y = round(py + math.sin(math.radians(a)) * r * 0.42)
                        if hr(x, y, k) < 0.4 + fade * 0.6:
                            cv.flat(x, y, mix(cv.get(x, y), (200, 168, 104), 0.25 + 0.4 * fade))
        frames.append(_diff(cv.img, img))
    return frames


ANIMS = {'pols': {'frames': _frames_pols, 'frameDuration': 130},
         'gota': {'frames': _frames_gota, 'frameDuration': 80}}


# ─── Capes del davant ─────────────────────────────────────────────────────

def _amo(ids):
    def mask(x, y):
        _, e = _base()
        return e.ids[e.amo[y * e.cv.w + x]] in ids
    return mask


def _p(x, z, y=0.0):
    u, v, _ = CAM.projecta((x, y, z))
    return round(u), round(v)


FRONT = [
    {'id': 'davant', 'mask': _amo({'primer_pla'}), 'baseline': 999, 'zIndex': 20},
    {'id': 'davant_cadenes', 'mask': _amo({'cadenes'}), 'baseline': _p(PILE[0], PILE[1])[1], 'zIndex': 20},
]


# ─── Geometria (coordenades de sala, projectades) ────────────────────────────

def _rect_mon(*Ps):
    pts = [CAM.projecta(P) for P in Ps]
    return (max(0, round(min(p[0] for p in pts))), max(0, round(min(p[1] for p in pts))),
            min(W - 1, round(max(p[0] for p in pts))), min(BOTTOM, round(max(p[1] for p in pts))))


def _escala_a(v):
    lo, hi = 1.0, 3000.0
    for _ in range(60):
        z = (lo + hi) / 2
        if CAM.projecta((260, 0, z))[1] > v:
            lo = z
        else:
            hi = z
    return CAM.escala((260, 0, (lo + hi) / 2))


def _z_v(x, v):
    lo, hi = -100.0, 2000.0
    for _ in range(50):
        z = (lo + hi) / 2
        if CAM.projecta((x, 0, z))[1] > v:
            lo = z
        else:
            hi = z
    return round((lo + hi) / 2)


V_PROP = 199                                       # on es camina més a prop (escala ≈1,2)
# El terra on es camina (al món): de la pila de cadena al costat de la dreta, fins als graons.
WALK_MON = ([(150, 232), (232, 238), (452, 238)] + [(x, _z_v(x, V_PROP)) for x in (452, 340, 230)]
            + [(170, _z_v(170, V_PROP)), (204, 150)])
_WALK = [_p(x, z) for x, z in WALK_MON]
_V_FONS, _V_PROP = min(v for _, v in _WALK), max(v for _, v in _WALK)
_PX, _PZ, _PR, _PH = PILE

GEOMETRIA = {
    'things': {
        'escotilla': {'rect': _rect_mon((HATCH[0] - 6, HW + 20, ZW), (HATCH[1] + 6, HW, HATCH[2]), (RUNGS[0], 0, ZW),
                                        (RUNGS[1], 0, ZW)),
                      'walk': _p(RUNGS[1] + 30, ZW - 24)},     # (a la dreta de l'escala: davant, la tapava)
        'cadenes': {'rect': _rect_mon(*([(_PX + dx, 0, _PZ + dz) for dx in (-_PR, _PR) for dz in (-_PR * 0.85, _PR * 0.85)]
                                        + [(HAWSE[0], HW, HAWSE[1]), (_PX, _PH, _PZ)])),
                    'walk': _p(_PX + _PR + 30, _PZ - 30)},
        'manta': {'rect': _rect_mon(*[(HAWSER[0] + dx, y, HAWSER[1] + dz) for dx in (-58, 64) for dz in (-76, 30)
                                      for y in (0, 36)]),
                  'walk': _p(HAWSER[0] - 70, HAWSER[1] - 40)},
    },
    'spawns': {'iri': _p(300, 170), 'vet': _p(240, 186), 'juana': _p(HAWSER[0], HAWSER[1] - 26)},
    'walkable': _WALK,
    'floorSquash': 0.42,
    # L'ombra de contacte: la llum dominant és la de l'escotilla (el punt de terra a sota de la boca).
    'characterShadow': {'enabled': True, 'color': '#060302', 'alpha': 0.5, 'squash': 0.4, 'core': 0.6,
                        'light': {'x': _p(_cone(0)[0], _cone(0)[1])[0], 'y': _p(_cone(0)[0], _cone(0)[1])[1],
                                  'stretch': 0.8, 'reach': 140}},
    'regions': [{'id': 'perspectiva', 'active': True, 'scaleEnabled': True, 'scaleWalkSpeed': True,
                 'scaleTop': round(_escala_a(_V_FONS - 2), 3), 'scaleBottom': round(_escala_a(_V_PROP + 2), 3),
                 'points': [(0, _V_FONS - 2), (W - 1, _V_FONS - 2), (W - 1, _V_PROP + 2), (0, _V_PROP + 2)]}],
    # (a les fosques, però el personatge s'ha de llegir fins i tot al fons: una mica més d'ambient)
    'characterLights': {
        'ambient': '#76645a',
        'lights': [{'x': _p(HC[0], HC[2], HW - 20)[0], 'y': _p(HC[0], HC[2], HW - 20)[1], 'radius': 340,
                    'color': '#ffcf82', 'intensity': 1.2}],
    },
}
