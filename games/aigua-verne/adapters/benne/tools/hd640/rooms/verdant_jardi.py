"""
Aigua Verne — `verdant_jardi` (L, de lluny: persones de ≈83 px). Escena 5. EN 3D (hd640/tres_d.py), a 1×.

El jardí de la residència d'estiu del Magnat, a Verdant: el planeta dels rics, on tot és de plàstic. Una càmera a
l'altura d'una persona alta, sense mirar avall, amb l'horitzó a y = 100: el cel blau d'anunci, els turons d'un verd
impossible amb arbres de piruleta i viles blanques, i la bardissa retallada amb regle que tanca el jardí. La
**residència**, blanca i or, girada cap a l'esquerra (la façana amb el pòrtic i la paret de la dreta que fuig), amb
les boles de boix a la porta (en Fidel s'hi posa al davant: és un sprite a part) i el **climatitzador**, que degota
a una **reixa** a terra (l'única aigua de veritat del jardí). Al davant, a la dreta, el **cobert del jardiner**:
fusta pintada de verd, vella, humana, girat cap a l'altra banda (la façana i la paret de l'esquerra), que tapa el
cantó de la residència. A l'esquerra, la **Cantimplora** (el model canònic de cantimplora_comu.py: la popa tallada
per la vora, la proa que fuig cap al fons a la dreta, el costat d'estribord amb la matrícula, la porta de la bodega
encesa i el nom, i la **rampa** abaixada a la gespa; a contrallum, amb l'ombra llarga endavant), la **plataforma de
la llançadora** i el **panell del preu**. La **gespa
artificial**, a franges de segar que fugen cap a l'horitzó; el camí de marbre de la porta; el parterre de **flors de
plàstic**, els **aspersors** i un flamenc. Primer pla: mates de boix retallades a les dues cantonades de baix, a
l'ombra. Es passa per darrere de la rampa (entre la rampa i la proa, arran del buc).

El detall (la façana, el cobert, el climatitzador, el panell, el rètol de la llançadora, les boles de boix, els
aspersors i el flamenc) ve del jardí pla de sempre (verdant_jardi_pla_comu.py), dibuixat de cara i projectat.

Decorat: `galleda_reixa` (la galleda d'en Nil sota el degoteig). ANIMS: `boira` (els aspersors), `degoteig`.

El món: x a la dreta (0 = la càmera), y amunt, z endavant; 1 unitat = 1 px a la distància on un personatge fa la
seva mida normal (z = 500). Al terra, l'escala d'un personatge és (v − 100) / 140, exacta.
"""
import functools
import math

import hd640  # noqa: F401  (posa la llibreria de dibuix a 640×360)
from PIL import Image

from hd.pix import Canvas, Light, W, H, hr
from hd.rooms.exterior import fbm, smooth
from hd640.rooms import verdant_jardi_pla_comu as PL
from hd640.rooms.verdant_comu import (SKYV, TURF, HILLV, WHITEV, MARBLE, GOLDV, GLASSV, CYANF, SHEDG, ZINC, BLACKT,
                                      OLIVE, SAFETY, RUSTV, MAGENTA, YELLOWF, ORANGEF, VIOLETF, panell_preu, flor,
                                      arbre_rodo, galleda)
from hd640.rooms.cantimplora_comu import Cantimplora
from hd640.tres_d import Camera, Escena, Llum

RH = 260                                           # la sala (per sota, la barra de verbs)
HOR = 100                                          # l'horitzó (la càmera no mira avall: les verticals, verticals)
CAM = Camera(pos=(0, 140, 0), yaw=0.0, pitch=0.0, f=500, centre=(320, HOR))
SUN = (118, 22)                                    # el sol, al cel (a dalt a l'esquerra, al fons: contrallum)
BARDISSA_Z = 1500

LIGHT = Light(ambient=0.0, vignette=None, floor_fade=None)
LLUMS = [Llum((-9000, 7000, 12000), 1e7, 1.4, power=1.0)]    # el sol, darrere a l'esquerra (ombres cap endavant i a la dreta)
AMBIENT = 0.3
TL = Light(ambient=0.7, vignette=None, floor_fade=None)       # la llum de les textures (el món d'anunci: tot brilla)


def _add(a, b, k=1.0):
    return (a[0] + b[0] * k, a[1] + b[1] * k, a[2] + b[2] * k)


def _up(P, h):
    return (P[0], P[1] + h, P[2])


# La residència: girada 29°, la façana mira cap a l'esquerra i endavant; la paret de la dreta fuig cap al fons
FK = 1.4                                           # unitats del món per píxel del dibuix pla de la façana
TH = -0.5
TF = (math.cos(TH), 0.0, math.sin(TH))             # al llarg de la façana, d'esquerra a dreta
NF = (math.sin(TH), 0.0, -math.cos(TH))            # la normal de la façana (cap a la càmera)
FX0, FX1, FY0, FY1 = PL.RX0 - 8, PL.RX1 + 8, 18, 208   # el retall del dibuix pla (la base, a y = 208)
FW = (FX1 - FX0) * FK
R = (300.0, 0.0, 900.0)                            # el cantó de baix a la dreta de la façana
LC = _add(R, TF, -FW)                              # el cantó de l'esquerra
BK = _add((0, 0, 0), NF, -240)                     # cap enrere (la fondària de la casa)


def _facana(fx, fy, out=0.0):
    """Un punt del dibuix pla de la façana (x del pla, y amb la base a 208) al món; `out`: tantes unitats endavant."""
    P = _add(_add(LC, TF, (fx - FX0) * FK), NF, out)
    return (P[0], (FY1 - fy) * FK, P[2])


DOOR_C = _facana((PL.DOOR[0] + PL.DOOR[2]) / 2, FY1)
BOIX = [_facana(304, FY1, 22), _facana(400, FY1, 22)]
AC = _facana(PL.RX0 + 30, FY1, 16)                 # el climatitzador, a l'esquerra del pòrtic, arran de la façana
REIXA = _add(AC, NF, 26)

# El cobert d'en Nil: girat 24° cap a l'altra banda, la façana mira cap a la dreta; la paret de l'esquerra fuig
CK = 1.3
THC = 0.42
TFC = (math.cos(THC), 0.0, math.sin(THC))
NFC = (math.sin(THC), 0.0, -math.cos(THC))
CX0, CX1, CY0, CY1 = PL.SX0 - 9, PL.SX1 + 9, 88, 205
LCC = (250.0, 0.0, 640.0)
BKC = _add((0, 0, 0), NFC, -130)


def _cobert(fx, fy, out=0.0):
    P = _add(_add(LCC, TFC, (fx - CX0) * CK), NFC, out)
    return (P[0], (CY1 - fy) * CK, P[2])


COBERT_PORTA = _cobert((PL.SDOOR[0] + PL.SDOOR[2]) / 2, CY1)

# La Cantimplora (el model canònic, cantimplora_comu): a l'esquerra, la popa a prop (tallada per la vora) i la proa
# que fuig cap al fons a la dreta; la porta, a estribord (el costat que es veu), amb la rampa abaixada a la gespa
NAU = Cantimplora(popa=(-440.0, 560.0), rumb=math.pi / 2 - 0.3, porta='estribord')
PORTA_L, PORTA_T, RAMPA_OUT = NAU.PORTA_L, NAU.PORTA_T, NAU.RAMPA_OUT
SOL_DIR = (-9000.0, 7000.0, 12000.0)               # cap al sol (el de LLUMS): l'ombra de la nau, endavant i a la dreta
LLANC = (-120.0, 730.0, 48.0)                      # la plataforma de la llançadora: centre i radi
PAL = (-64.0, 744.0)
PANELL = (-214.0, 1000.0)
PARTERRE = (14.0, 610.0, 60.0)
SPRINK = ((236.0, 560.0), (-74.0, 520.0))
FLAMENC = (96.0, 770.0)
CAMI_X = (150.0, 168.0)                            # el camí de marbre: el mig a la porta i a baix


# ─── Les textures: el jardí pla de sempre ────────────────────────────────────

def _pla(fn):
    cv = Canvas(light=TL, transparent=True)
    fn(cv)
    return cv.img


@functools.lru_cache(maxsize=None)
def _textures():
    return {
        'facana': _pla(lambda cv: PL.residencia(cv, boix=False)),
        'cobert': _pla(PL.cobert),
        'clima': _pla(PL.climatitzador),
        # (els sprites: el retall i el punt que toca a terra)
        'panell': (_pla(lambda cv: panell_preu(cv, 186, 112, '', post=46, w=44)).crop((180, 104, 238, 186)), (28, 80)),
        'llanc': (_pla(PL.llancadora).crop((90, 116, 146, 187)), (24, 76)),
        'boix': (_pla(lambda cv: PL.bola_boix(cv, 40, 40, 7)).crop((28, 20, 52, 42)), (12, 20)),
        'aspersor': (_pla(lambda cv: PL.aspersor(cv, 20, 20)).crop((12, 8, 28, 24)), (8, 12)),
        'flamenc': (_pla(lambda cv: PL.flamenc(cv, 30, 40)).crop((18, 6, 44, 44)), (12, 34)),
        'galleda': (_pla(lambda cv: galleda(cv, 30, 30, s=0.62, plena=True)).crop((14, 2, 46, 34)), (16, 28)),
    }


# ─── El fons (en pantalla): el cel, els turons ───────────────────────────────

def fons(cv):
    for y in range(0, HOR + 60):
        t = min(1.0, y / HOR)
        for x in range(W):
            d = math.hypot(x - SUN[0], (y - SUN[1]) * 1.2)
            cv.put(x, y, SKYV, 1.2 + 5.6 * t ** 1.3 + 2.6 * max(0.0, 1 - d / 120) ** 2, lit=0)
    PL.nuvol(cv, 250, 30, 1.0)
    PL.nuvol(cv, 540, 18, 1.2)
    PL.nuvol(cv, 418, 52, 0.6)
    cv.glow(SUN[0], SUN[1], 44, (255, 255, 236), 0.9)
    for k in range(12):
        a = k * math.pi / 6 + 0.13
        for r in range(12, 28 if k % 2 else 22):
            if r % 2 == 0:
                cv.flat(SUN[0] + math.cos(a) * r, SUN[1] + math.sin(a) * r, (255, 252, 214))
    cv.disc(SUN[0], SUN[1], 8, 8, [(255, 236, 140), (255, 248, 190), (255, 255, 236), (255, 255, 255)],
            lambda nx, ny: 3.4 - nx * 0.6 - ny * 0.6, lit=0)
    # turons de gespa perfecta (corbes de sinus, ni un roc), amb arbres de piruleta i viles blanques
    base = HOR + 52
    for x in range(W):
        h1 = HOR - 14 + 7 * math.sin(x / 70 + 0.6) + 3 * math.sin(x / 31)
        h2 = HOR - 2 + 5 * math.sin(x / 46 + 2.1)
        for y in range(int(h1), base):
            cv.put(x, y, HILLV, 4.0 - (y - h1) * 0.035 + (0.9 if y - h1 < 1.5 else 0), lit=0)
        for y in range(int(h2), base):
            cv.put(x, y, HILLV, 3.0 - (y - h2) * 0.02 + (1.0 if y - h2 < 1.5 else 0), lit=0)
    for vx in (88, 196, 470, 600):
        vy = int(HOR - 14 + 7 * math.sin(vx / 70 + 0.6) + 3 * math.sin(vx / 31)) + 3
        cv.rect(vx - 5, vy - 6, vx + 5, vy, WHITEV, lambda x, y: 5.4 if x < vx + 2 else 4.0, lit=0)
        cv.hline(vx - 6, vx + 6, vy - 6, GOLDV, 4.6, lit=0)
        for wx in range(vx - 3, vx + 4, 3):
            cv.flat(wx, vy - 3, GLASSV[2])
        cv.rect(vx - 8, vy + 1, vx + 1, vy + 1, CYANF, 3.4, lit=0)
    for tx, r in ((60, 3), (140, 4), (166, 3), (232, 3), (300, 4), (520, 3), (556, 4), (630, 3)):
        tb = int(HOR - 2 + 5 * math.sin(tx / 46 + 2.1)) + 2
        arbre_rodo(cv, tx, tb, r, lit=0)


# ─── El terra (en el món) ────────────────────────────────────────────────────

def _dist_seg(x, z, A, B):
    dx, dz = B[0] - A[0], B[1] - A[1]
    u = max(0.0, min(1.0, ((x - A[0]) * dx + (z - A[1]) * dz) / (dx * dx + dz * dz)))
    return math.hypot(x - A[0] - dx * u, z - A[1] - dz * u), u


def _gespa(s, t, P):
    """Gespa artificial a franges de segar (al llarg de z: fugen cap a l'horitzó), amb els brins que brillen."""
    x, z = P[0], P[2]
    far = smooth(900, 1500, z)
    band = int(math.floor((x + 1000) / 46)) % 2
    v = 4.0 + (0.7 if band else -0.15) * (1 - far * 0.6) - far * 0.3
    if hr(int(x) // 2, int(z) // 3, 9) > 0.9:
        v += 0.8 * (1 - far)
    elif hr(int(x) // 2, int(z) // 3, 10) > 0.93:
        v -= 0.6 * (1 - far)
    return v


def _cami(s, t, P):
    """El camí de lloses de marbre blanc, de la porta fins a baix (lloses del món: grans a prop)."""
    x, z = P[0], P[2]
    row = int(z // 34)
    off = 23 if row % 2 else 0
    v = 4.8 + (fbm(x / 20, z / 20, 61) - 0.5) * 0.5
    if z % 34 < 1.6 or (x + off) % 46 < 1.6:
        v -= 1.6
    return v


def _cami_x(z):
    k = (z - 440) / (DOOR_C[2] - 440)
    return CAMI_X[1] + (CAMI_X[0] - CAMI_X[1]) * k


# ─── Les peces ──────────────────────────────────────────────────────────────

def cilindre(e, sid, cx, cz, r, y0, y1, ramp, lvl, n=32):
    """Un cilindre vertical: les facetes que es veuen. `lvl(angle, y, P)`."""
    for i in range(n):
        a0, a1 = 2 * math.pi * i / n, 2 * math.pi * (i + 1) / n
        p0 = (cx + r * math.cos(a0), cz + r * math.sin(a0))
        p1 = (cx + r * math.cos(a1), cz + r * math.sin(a1))
        e.quad(sid, (p0[0], y1, p0[1]), (p1[0], y1, p1[1]), (p1[0], y0, p1[1]), (p0[0], y0, p0[1]), ramp=ramp,
               lvl=lambda s, t, P: lvl(math.atan2(P[2] - cz, P[0] - cx), P[1], P))


def disc(e, sid, cx, cz, r, y, ramp, lvl, ri=0.0):
    """Un disc (o una anella, amb `ri`) pla, a l'alçada `y`."""
    e.quad(sid, (cx - r, y, cz + r), (cx + r, y, cz + r), (cx + r, y, cz - r), (cx - r, y, cz - r), ramp=ramp, lvl=lvl,
           forma=lambda s, t: ri * ri <= (s - r) ** 2 + (t - r) ** 2 <= r * r)


def ombra(e, cx, cz, rx, rz, k=0.5, sid='ombra'):
    """Una ombra el·líptica a terra, desplaçada cap endavant i a la dreta (el sol és darrere a l'esquerra)."""
    e.foscor(sid, (cx - rx, 0.3, cz + rz), (cx + rx, 0.3, cz + rz), (cx + rx, 0.3, cz - rz), (cx - rx, 0.3, cz - rz),
             lambda s, t: k * min(1.0, 1.8 * max(0.0, 1 - ((s - rx) / rx) ** 2 - ((t - rz) / rz) ** 2)))


def bardissa(e):
    """La bardissa del fons, retallada amb regle: un prisma verd perfecte que tanca el jardí."""
    z = BARDISSA_Z
    e.caixa('bardissa', -6000, 6000, 0, 34, z, z + 30, TURF, 3.0,
            cares={'davant': {'ramp': TURF, 'lvl': lambda s, t, P: 2.6 + (hr(int(s) // 2, int(t) // 2, 3) - 0.5) * 0.8
                              - (1.0 if t > 30 else 0)},
                   'dalt': {'ramp': TURF, 'lvl': lambda s, t, P: 4.8 + (hr(int(s) // 3, int(t) // 3, 4) - 0.5) * 0.6}})


def residencia(e, tex):
    # la paret de la dreta, que fuig: blanca, carreus a la planta baixa, la cornisa d'or, dues finestres
    hw = (FY1 - 36) * FK

    def paret(s, t, P):
        y = P[1]
        if (208 - 48) * FK <= y <= (208 - 44) * FK:
            return 5.0                                             # (la cornisa: es pinta d'or a sobre)
        v = 3.6 + (fbm(s / 30, y / 20, 21) - 0.5) * 0.3
        if y < (208 - 100) * FK and int(y) % 13 < 1:
            v -= 0.8
        for wx in (70, 170):
            if wx < s < wx + 40 and 30 < y < 110:
                return 1.8 + (1.4 if (s - wx + (110 - y) * 0.6) % 34 < 5 else 0)
        return v
    e.quad('residencia', _up(R, hw), _up(_add(R, BK), hw), _add(R, BK), R, ramp=WHITEV, lvl=paret)
    e.quad('residencia', _up(R, (208 - 44) * FK), _up(_add(R, BK), (208 - 44) * FK), _up(_add(R, BK), (208 - 49) * FK),
           _up(R, (208 - 49) * FK), ramp=GOLDV, lvl=lambda s, t, P: 3.6 - t * 0.2)
    # la façana: el dibuix pla
    e.quad('residencia', _up(LC, (FY1 - FY0) * FK), _up(R, (FY1 - FY0) * FK), R, LC,
           tex=(tex['facana'], (FX0, FY0, FX1, FY1)))


def cobert(e, tex):
    h_ra = (CY1 - 130) * CK                        # l'alçada del ràfec
    A = _cobert(PL.SAPEX[0], PL.SAPEX[1])
    Ee = _cobert(PL.SX0 - 8, 130)
    # la paret de l'esquerra, que fuig: taulons verds amb la pintura saltada
    LB = _add(LCC, BKC)

    def taulons(s, t, P):
        y = P[1]
        peel = fbm(s / 7, y / 9, 83)
        if peel > 0.66:
            return 2.4 + (peel - 0.66) * 4 - (1.4 if s % 9 < 1 else 0)
        return 2.8 - (1.6 if s % 9 < 1 else 0) + (fbm(s / 5, y / 30, 81) - 0.5) * 0.9 - (1.2 if y < 5 else 0)
    e.quad('cobert', _up(LB, h_ra), _up(LCC, h_ra), LCC, LB, ramp=SHEDG, lvl=taulons)
    # el vessant de l'esquerra de la teulada, de xapa ondulada rovellada
    e.quad('cobert', _up(_add(A, BKC), 0), A, Ee, _add(Ee, BKC), ramp=ZINC, dues_cares=True,
           lvl=lambda s, t, P: 3.2 + (0.8 if int(t / 3) % 2 else -0.4) + (1.0 if fbm(s / 20, t / 8, 85) > 0.62 else 0))
    # la façana: el dibuix pla
    e.quad('cobert', _cobert(CX0, CY0), _cobert(CX1, CY0), _cobert(CX1, CY1), _cobert(CX0, CY1),
           tex=(tex['cobert'], (CX0, CY0, CX1, CY1)))


def climatitzador(e, tex):
    x0, y0, x1, y1 = PL.AC
    w, h = (x1 - x0 + 1) * FK, (y1 - y0 + 1) * FK
    leg = (199 - y1) * FK
    for lx in (-w / 2 + 4, w / 2 - 4):
        P = _add(AC, TF, lx)
        e.caixa_girada('clima', P[0], P[2], 3, 3, leg, TH, WHITEV, 3.6)
    e.caixa_girada('clima', AC[0], AC[2], w, 20, h, TH, WHITEV, 4.2, y0=leg,
                   cares={'davant': {'tex': (tex['clima'], (x0, y0, x1 + 1, y1 + 1))},
                          'dalt': {'ramp': WHITEV, 'lvl': 5.4}, 'esquerra': {'ramp': WHITEV, 'lvl': 4.6},
                          'dreta': {'ramp': WHITEV, 'lvl': 3.0}})
    # el tub de desguàs, que surt per baix i fa colze fins a la reixa
    P0 = _add(AC, TF, (PL.DRIP[0] - (x0 + x1) / 2) * FK)
    e.cable('clima', [(P0[0], leg, P0[2]), (P0[0], 8, P0[2]), _up(_add(_add(P0, NF, 14), (0, 0, 0)), 8)], ZINC, 4.2,
            gruix=2.6)


def _tub_fi():
    x0, _, x1, _ = PL.AC
    P0 = _add(AC, TF, (PL.DRIP[0] - (x0 + x1) / 2) * FK)
    return _up(_add(P0, NF, 14), 7)


def reixa(e):
    x, z = REIXA[0], REIXA[2]
    e.foscor('ombra', (x - 32, 0.3, z + 14), (x + 32, 0.3, z + 14), (x + 32, 0.3, z - 14), (x - 32, 0.3, z - 14),
             lambda s, t: 0.45 * max(0.0, 1 - ((s - 32) / 32) ** 2 - ((t - 14) / 14) ** 2) * 1.5)   # la taca d'humitat
    e.quad('reixa', (x - 20, 0.5, z + 8), (x + 20, 0.5, z + 8), (x + 20, 0.5, z - 8), (x - 20, 0.5, z - 8), ramp=ZINC,
           lvl=lambda s, t, P: (3.6 if (s % 4 < 1.4 or s < 1.5 or s > 38.5 or t < 1.5 or t > 14.5) else
                                (0.6 if hr(int(s), 3) > 0.5 else 1.6)))


def boix(e, tex):
    for k, P in enumerate(BOIX):
        ombra(e, P[0] + 10, P[2] - 8, 18, 10, 0.5)
        e.sprite(f'boix{k}', *tex['boix'], P, escala_img=FK * 1.4)


def cantimplora(e):
    """La Cantimplora canònica: el costat de la porta, a contrallum (el sol és darrere a l'esquerra), la bodega encesa,
    la rampa abaixada a la gespa i l'ombra llarga que cau endavant i a la dreta, per la gespa."""
    NAU.dibuixa(e, ombra={'sol': SOL_DIR, 'k': 0.45})
    NAU.resplendor(e.cv, k=0.6)


def llancadora(e, tex):
    cx, cz, r = LLANC
    ombra(e, cx + 10, cz - 6, r + 6, r * 0.8, 0.45)
    cilindre(e, 'llancadora', cx, cz, r, 0, 4, WHITEV, lambda a, y, P: 2.6 + math.cos(a + 2.4) * 0.6)
    disc(e, 'llancadora', cx, cz, r, 4, MARBLE, lambda s, t, P: 4.6 - (t / r) * 0.3)
    disc(e, 'llancadora', cx, cz, r - 6, 4.1, GOLDV, 4.6, ri=r - 8.5)
    for k in range(12):
        a = k * math.pi / 6
        u, v, _ = CAM.projecta((cx + math.cos(a) * (r - 2.5), 4.2, cz + math.sin(a) * (r - 2.5)))
        e.cv.flat(u, v, CYANF[3])
    # la J de «jardiners», pintada al mig
    e.quad('llancadora', (cx - 10, 4.2, cz + 12), (cx + 10, 4.2, cz + 12), (cx + 10, 4.2, cz - 12), (cx - 10, 4.2, cz - 12),
           ramp=[(20, 100, 50), (40, 150, 70), (80, 190, 110)], lvl=1.6,
           forma=lambda s, t: (11 < s < 15 and t < 18) or (15 < t < 22 and 4 < s < 15) or (t > 12 and 3 < s < 7 and t < 20))
    # el pal amb el rètol i l'horari
    ombra(e, PAL[0] + 14, PAL[1] - 8, 16, 6, 0.4)
    e.sprite('llancadora_pal', *tex['llanc'], (PAL[0], 0, PAL[1]), escala_img=FK)


def panell(e, tex):
    ombra(e, PANELL[0] + 26, PANELL[1] - 16, 34, 10, 0.4)
    e.sprite('panell', *tex['panell'], (PANELL[0], 0, PANELL[1]), escala_img=1.7)


def cami(e):
    x0, x1 = CAMI_X
    e.quad('cami', (x0 - 26, 0.2, DOOR_C[2] - 8), (x0 + 26, 0.2, DOOR_C[2] - 8), (x1 + 30, 0.2, 400),
           (x1 - 30, 0.2, 400), ramp=MARBLE, lvl=_cami)


def parterre(e, cx, cz, r, sid='parterre', fosc=0.0):
    """El parterre: la vorada de marbre, la terra de plàstic i anelles de flors, cada anella d'un color."""
    ombra(e, cx + 8, cz - 6, r + 8, r * 0.85, 0.35, sid=sid)
    cilindre(e, sid, cx, cz, r + 4, 0, 4, MARBLE, lambda a, y, P: 4.0 - fosc + math.cos(a + 2.4) * 0.6)
    disc(e, sid, cx, cz, r + 4, 4, MARBLE, 5.0 - fosc, ri=r)
    disc(e, sid, cx, cz, r, 3.0, TURF, lambda s, t, P: 1.4 - fosc + (hr(int(s), int(t), 91) - 0.5) * 0.6)
    rings = ((0.9, MAGENTA), (0.72, CYANF), (0.54, YELLOWF), (0.36, ORANGEF), (0.16, VIOLETF))
    pts = []
    for k, (f, ramp) in enumerate(rings):
        n = max(4, int(70 * f * r / 60))
        for i in range(n):
            a = 2 * math.pi * i / n + k * 0.3
            pts.append((cz + math.sin(a) * r * f, cx + math.cos(a) * r * f, ramp))
    cv = e.cv
    idx = e._idx_de(sid)
    for z, x, ramp in sorted(pts, reverse=True):                   # de darrere cap a davant
        k = CAM.escala((x, 0, z))
        u, v0, _ = CAM.projecta((x, 3, z))
        _, v1, _ = CAM.projecta((x, 10, z))
        s = 3 if k > 1.15 else 2 if k > 0.6 else 1
        for vv in range(int(v1) + 1, int(v0) + 1):
            cv.put(round(u), vv, TURF, 4.4 - fosc, lit=0)
        flor(cv, round(u), round(v1), ramp, size=s, lit=0)
        for yy in range(int(v1) - s - 1, int(v0) + 1):
            for xx in range(round(u) - s - 1, round(u) + s + 2):
                if 0 <= xx < W and 0 <= yy < RH:
                    e.amo[yy * cv.w + xx] = idx


def sprites_petits(e, tex):
    for k, (x, z) in enumerate(SPRINK):
        ombra(e, x + 4, z - 3, 7, 3, 0.4)
        e.sprite(f'aspersor{k}', *tex['aspersor'], (x, 0, z), escala_img=FK)
    ombra(e, FLAMENC[0] + 8, FLAMENC[1] - 4, 10, 4, 0.4)
    e.sprite('flamenc', *tex['flamenc'], (FLAMENC[0], 0, FLAMENC[1]), escala_img=FK)


def primer_pla(e):
    """Mates de boix rodones, a baix a l'esquerra i a baix a la dreta, a l'ombra, tallades per la vora."""
    e.roca('primer_pla', (-196, 0, 330), 60, TURF, 0.7, llum_dir=(-0.6, -0.7), aplana=0.95, seed=4)
    e.roca('primer_pla', (-120, 0, 318), 34, TURF, 0.5, llum_dir=(-0.6, -0.7), aplana=1.0, seed=7)
    e.roca('primer_pla', (236, 0, 344), 52, TURF, 0.6, llum_dir=(-0.6, -0.7), aplana=1.0, seed=9)


def escena(cv, tex):
    e = Escena(cv, CAM, LLUMS, ambient=AMBIENT)
    fons(cv)
    bardissa(e)
    e.quad('terra', (-8000, 0, BARDISSA_Z), (8000, 0, BARDISSA_Z), (8000, 0, 300), (-8000, 0, 300), ramp=TURF,
           lvl=_gespa)
    e.claror((-8000, 0.2, BARDISSA_Z), (8000, 0.2, BARDISSA_Z), (8000, 0.2, 900), (-8000, 0.2, 900), (200, 236, 210),
             lambda s, t: 0.25 * smooth(200, 600, 600 - t))       # la boira de perfum, al fons
    cami(e)
    # de lluny a prop
    panell(e, tex)
    ombra(e, R[0] + 90, R[2] - 40, 120, 50, 0.4)
    residencia(e, tex)
    climatitzador(e, tex)
    reixa(e)
    boix(e, tex)
    cobert(e, tex)
    sprites_petits(e, tex)
    llancadora(e, tex)
    parterre(e, *PARTERRE)
    cantimplora(e)
    primer_pla(e)
    return e


# ─── Composició ─────────────────────────────────────────────────────────────

@functools.lru_cache(maxsize=None)
def _base():
    cv = Canvas(light=LIGHT)
    e = escena(cv, _textures())
    for y in range(RH, H):                                         # sota la sala: negre
        for x in range(W):
            cv.flat(x, y, (0, 0, 0))
    return cv.img, e


def bg(cv):
    img, _ = _base()
    cv.img.paste(img)
    cv.P = cv.img.load()


def galleda_reixa(cv):
    """La galleda d'en Nil sota el tub del climatitzador, damunt la reixa, recollint les gotes."""
    c2 = Canvas(light=LIGHT, transparent=True)
    e2 = Escena(c2, CAM, LLUMS, ambient=AMBIENT)
    P = _tub_fi()
    e2.sprite('galleda', *_textures()['galleda'], (P[0], 0, P[2]), escala_img=FK)
    _, e = _base()
    W_ = e.cv.w
    px = c2.P
    for y in range(RH):
        for x in range(W_):
            if e.ids[e.amo[y * W_ + x]] in ('primer_pla', 'cobert'):
                px[x, y] = (0, 0, 0, 0)
    cv.img.alpha_composite(c2.img)


PROPS = {'galleda_reixa': galleda_reixa}

PERFUM = [(255, 214, 240), (240, 200, 255), (255, 255, 255), (214, 240, 255)]


def _frames_boira():
    """Els aspersors no reguen: escombren el jardí amb un raig de perfum (gotetes rosades, liles i blanques) que
    va i ve, i deixen una boira a quadres que s'esvaeix (tot del món: més petit com més lluny)."""
    base, e = _base()
    frames = []
    n = 16
    D = 30.0
    for i in range(n):
        im = Image.new('RGBA', base.size, (0, 0, 0, 0))
        P, B = im.load(), base.load()

        def put(x, y, col, k=1.0):
            x, y = int(x), int(y)
            if 0 <= x < W and 0 <= y < RH and e.ids[e.amo[y * W + x]] != 'primer_pla':
                o = B[x, y]
                P[x, y] = (int(o[0] + (col[0] - o[0]) * k), int(o[1] + (col[1] - o[1]) * k),
                           int(o[2] + (col[2] - o[2]) * k), 255)
        for k, (wx, wz) in enumerate(SPRINK):
            sx, sy, _ = CAM.projecta((wx, 0, wz))
            sc = CAM.escala((wx, 0, wz)) * FK
            ph = 2 * math.pi * (i / n) + k * 2.2
            for y in range(int(sy - 20 * sc), int(sy + 4 * sc)):
                for x in range(int(sx - 30 * sc), int(sx + 31 * sc)):
                    d = ((x - sx) / (30 * sc)) ** 2 + ((y - sy + 6 * sc) / (11 * sc)) ** 2
                    if d < 1 and (x + 2 * y + i) % 4 == 0 and hr(x // 3, y // 2, (i + k) // 3) > 0.35 + d * 0.5:
                        put(x, y, (255, 214, 244), 0.45 - d * 0.25)
            for j in range(0, int(D), 2):
                d = j + (i % 2)
                x = sx + math.sin(ph) * d * sc
                y = sy - (9 + d * (1 - d / D) * 0.8 - d * 0.18 * math.cos(ph)) * sc
                put(x, y, PERFUM[(j // 2 + k) % 4])
            ex = sx + math.sin(ph) * D * sc
            ey = sy - (9 - D * 0.18 * math.cos(ph)) * sc
            for q in range(10):
                put(ex + (hr(q, i, k) - 0.5) * 8 * sc, ey + (hr(q, i, k + 5) - 0.5) * 4 * sc, PERFUM[q % 4])
        frames.append(im)
    return frames


def _frames_degoteig():
    """La gota que cau del tub del climatitzador a la reixa (o a la galleda)."""
    base, e = _base()
    T = _tub_fi()
    x, y0, _ = CAM.projecta(T)
    _, y1, _ = CAM.projecta((T[0], 0.5, T[2]))
    frames = []
    for i in range(12):
        im = Image.new('RGBA', base.size, (0, 0, 0, 0))
        P = im.load()

        def put(xx, yy, col):
            xx, yy = int(xx), int(yy)
            if 0 <= xx < W and 0 <= yy < RH and e.ids[e.amo[yy * W + xx]] not in ('primer_pla', 'cobert'):
                P[xx, yy] = col + (255,)
        if 1 <= i < 5:
            put(x, y0 + 1, (150, 210, 250))
            if i >= 3:
                put(x, y0 + 2, (200, 236, 255))
        elif 5 <= i < 9:
            yy = y0 + 3 + (i - 5) ** 2 * 1.2
            if yy < y1:
                put(x, yy, (200, 236, 255))
                put(x, yy - 1, (120, 190, 240))
        elif i == 9:
            for dx, dy in ((-2, -1), (2, -1), (-1, -2), (1, -2)):
                put(x + dx, y1 + dy, (200, 236, 255))
        frames.append(im)
    return frames


ANIMS = {'boira': {'frames': _frames_boira, 'frameDuration': 140},
         'degoteig': {'frames': _frames_degoteig, 'frameDuration': 160}}


def _amo(ids):
    def mask(x, y):
        _, e = _base()
        return e.ids[e.amo[y * e.cv.w + x]] in ids
    return mask


def _v(z):
    return round(HOR + CAM.f * CAM.pos[1] / z)


# Capes del davant: el personatge hi passa per darrere si té els peus més amunt (més lluny) que la seva base.
FRONT = [
    *[{'id': f'davant_boix{k}', 'mask': _amo({f'boix{k}'}), 'baseline': _v(P[2]), 'zIndex': 20}
      for k, P in enumerate(BOIX)],
    {'id': 'davant_clima', 'mask': _amo({'clima'}), 'baseline': _v(AC[2] - 6), 'zIndex': 20},
    {'id': 'davant_flamenc', 'mask': _amo({'flamenc'}), 'baseline': _v(FLAMENC[1]), 'zIndex': 20},
    {'id': 'davant_parterre', 'mask': _amo({'parterre'}), 'baseline': _v(PARTERRE[1]), 'zIndex': 20},
    {'id': 'davant_pal', 'mask': _amo({'llancadora_pal'}), 'baseline': _v(PAL[1]), 'zIndex': 20},
    # la rampa de la Cantimplora: qui va entre la rampa i la proa, arran del buc, hi passa per darrere
    {'id': 'davant_rampa', 'mask': _amo({'rampa'}), 'baseline': _v(NAU.terra(sum(PORTA_L) / 2, RAMPA_OUT * 0.75)[1]),
     'zIndex': 20},
    {'id': 'davant', 'mask': _amo({'primer_pla'}), 'baseline': 999, 'zIndex': 20},
]


# ─── Geometria (coordenades de sala, projectades) ─────────────────────────────

def _p(x, z, y=0.0):
    u, v, _ = CAM.projecta((x, y, z))
    return round(u), round(v)


def _pP(P):
    return _p(P[0], P[2])


def _rect(*Ps):
    pts = [CAM.projecta(P) for P in Ps]
    return (max(0, round(min(p[0] for p in pts))), max(0, round(min(p[1] for p in pts))),
            min(W - 1, round(max(p[0] for p in pts))), min(RH - 1, round(max(p[1] for p in pts))))


def _cercle(cx, cz, r, n=12):
    return [_p(cx + r * math.cos(2 * math.pi * i / n), cz + r * math.sin(2 * math.pi * i / n)) for i in range(n)]


Z_PROP = 470                                       # el terra on es camina no baixa d'aquí (escala ≈1,07)
_F_R = _add(R, NF, 26)                             # davant la façana, a 26 unitats
_F_L = _add(LC, NF, 26)
_C_L = _add(LCC, NFC, 22)                          # davant el cobert
_C_LB = _add(_add(LCC, BKC), TFC, -20)             # al llarg de la paret de l'esquerra del cobert
# El terra on es camina (al món): de la rampa fins al cobert, de baix fins a la façana; davant el peu de la rampa i,
# per la banda de la proa, arran del buc (per darrere de la rampa) sense tocar les potes. Forats: el parterre, el
# climatitzador, les boles de boix i el flamenc.
_SL = sum(PORTA_L) / 2
_NAU_W = [(-140, 1010), (-140, 760), NAU.terra(205, 170), NAU.terra(205, 116), NAU.terra(PORTA_L[1] + 10, 112),
          NAU.terra(PORTA_L[1] + 10, RAMPA_OUT + 14), NAU.terra(PORTA_L[0] - 10, RAMPA_OUT + 14)]
WALK_MON = [(_NAU_W[-1][0], Z_PROP), (380, Z_PROP), (388, 640), (_C_L[0], _C_L[2]), (_C_LB[0], _C_LB[2]),
            (_F_R[0], _F_R[2]), (_F_L[0], _F_L[2]), *_NAU_W]
_WALK = [_p(x, z) for x, z in WALK_MON]
_V_FONS, _V_PROP = min(v for _, v in _WALK), max(v for _, v in _WALK)


def _ac_forat():
    c, s = math.cos(TH), math.sin(TH)
    a, b = 26, 18
    return [_p(AC[0] + lx * c - lz * s, AC[2] + lx * s + lz * c) for lx, lz in ((-a, -b), (a, -b), (a, b), (-a, b))]


GEOMETRIA = {
    'things': {
        'rampa': {'rect': _rect(NAU.buc(PORTA_L[0] - 6, PORTA_T[1] + 0.06), NAU.buc(PORTA_L[1] + 6, PORTA_T[1] + 0.06),
                                *NAU.rampa_cantons()),
                  'walk': _p(*NAU.terra(_SL, RAMPA_OUT + 22))},
        'porta_residencia': {'rect': _rect(_facana(PL.DOOR[0] - 4, PL.DOOR[1] - 4), _facana(PL.DOOR[2] + 4, FY1)),
                             'walk': _pP(_add(DOOR_C, NF, 34))},
        'porta_cobert': {'rect': _rect(_cobert(PL.SDOOR[0] - 4, PL.SDOOR[1] - 6), _cobert(PL.SDOOR[2] + 4, CY1)),
                         'walk': _pP(_add(COBERT_PORTA, NFC, 30))},
        'flors': {'rect': _rect((PARTERRE[0] - PARTERRE[2] - 4, 12, PARTERRE[1] - PARTERRE[2]),
                                (PARTERRE[0] + PARTERRE[2] + 4, 0, PARTERRE[1] + PARTERRE[2])),
                  'walk': _p(PARTERRE[0] + 30, PARTERRE[1] - PARTERRE[2] - 20)},
        'aspersors': {'rect': _rect((SPRINK[1][0] - 10, 18, SPRINK[1][1]), (SPRINK[0][0] + 10, 0, SPRINK[0][1])),
                      'walk': _p(SPRINK[0][0] - 30, SPRINK[0][1] - 26)},
        'reixa': {'rect': _rect(_up(_add(AC, TF, -22), 76), _add(REIXA, TF, 22), _add(REIXA, NF, 10)),
                  'walk': _pP(_add(REIXA, NF, 30))},
        'panell_preu': {'rect': _rect((PANELL[0] - 44, 140, PANELL[1]), (PANELL[0] + 44, 0, PANELL[1])),
                        'walk': _p(-140, 960)},
        'llancadora': {'rect': _rect((PAL[0] - 30, 126, PAL[1]), (LLANC[0] + LLANC[2], 0, LLANC[1] - LLANC[2])),
                       'walk': _p(LLANC[0] + 20, LLANC[1] - LLANC[2] - 20)},
    },
    'spawns': {
        'nil': _p(PARTERRE[0] + 52, PARTERRE[1] - 40),
        'fidel': _pP(_add(DOOR_C, NF, 20)),
        'iri': _p(20, 500),
        'vet': _p(-110, 560),
    },
    'walkable': _WALK,
    'forats': [_cercle(PARTERRE[0], PARTERRE[1], PARTERRE[2] + 8), _ac_forat(), _cercle(FLAMENC[0], FLAMENC[1], 10, 6)]
              + [_cercle(P[0], P[2], 16, 8) for P in BOIX] + [_cercle(PAL[0], PAL[1], 8, 6)],
    # La càmera aixafa el terra: 140 d'alçada a ≈600 de fons (on es camina) → 0,23.
    'floorSquash': 0.25,
    # L'ombra de contacte: el sol és al fons a l'esquerra (contrallum), l'ombra cau cap endavant i a la dreta.
    'characterShadow': {'enabled': True, 'color': '#0a3a1a', 'alpha': 0.4, 'squash': 0.26, 'core': 0.6,
                        'light': {'x': 0.75, 'y': 0.3, 'direction': True, 'stretch': 0.6}},
    'regions': [{'id': 'perspectiva', 'active': True, 'scaleEnabled': True, 'scaleWalkSpeed': True,
                 'scaleTop': round((_V_FONS - 2 - HOR) / CAM.pos[1], 3),
                 'scaleBottom': round((_V_PROP + 2 - HOR) / CAM.pos[1], 3),
                 'points': [(0, _V_FONS - 2), (W - 1, _V_FONS - 2), (W - 1, _V_PROP + 2), (0, _V_PROP + 2)]}],
}
