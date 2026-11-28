"""
El taller de l'Arenga. EN 3D (hd640/tres_d.py), a 1×.

Un taller petit, endreçat com un quiròfan, amb llum de fluorescent. Una càmera alta que mira de biaix la cantonada
del fons a l'esquerra:
  - a la paret de l'esquerra, en escorç, la **porta** estanca oberta cap a la sala de màquines (d'on ve una claror
    verdosa) i el rotllo de cable penjat;
  - a la paret del fons, el **tauler** d'eines, gairebé de cara (s'hi ha de llegir la silueta buida de la clau de
    vàlvules), amb la **cisalla** i la **clau de tubs** penjades a la barra de baix; l'extintor de CO2;
  - el **banc** de treball, separat de la paret i girat: el sobre de fusta vist des de dalt amb el cargol de banc, el
    torn, el pot de llapis i l'entrepà vell en un plat; la calaixera, les potes i la caixa d'eines vermella a sota;
    damunt, el prestatge amb els pots i les capses de cargols;
  - el bidó d'oli, separat de la paret (s'hi passa per darrere);
  - el fluorescent penjat del sostre, que fa el bassal de llum freda al terra;
  - primer pla: un tub que baixa a la dreta, la cadena del polispast que penja i un carro de planxes a baix.

Tot el detall ve del dibuix pla de sempre (taller_pla_comu.py), projectat; la cisalla i la clau de tubs es dibuixen
planes i es projecten pel tauler.

El món: x a la dreta (0 = la paret de la porta), y amunt (0 = el terra), z cap al fons (280 = la paret del tauler);
1 unitat = 1 píxel de sala a la distància on un personatge fa ≈110 px (escala 1).
"""
import functools
import math

import hd640  # noqa: F401  (abans de cap hd.rooms: posa la llibreria a 640×360)
from PIL import Image

from hd.pix import Canvas, Light, W, H, hr, mix
from hd.rooms.arenga import WALL, DECK, CAB, DARK, WHITEP, YELL, SEAG, REDP, BRASS, ENG_LIGHT as ENG
from hd.rooms.exterior import fbm
from hd640.rooms import sota
from hd640.rooms import taller_pla_comu as PL
from hd640.rooms.taller_pla_comu import WOOD, STEELT, TUBEC, PEG
from hd640.rooms.rebost_pla_comu import plate_wall, engine_door
from hd640.tres_d import Camera, Escena, Llum

BOTTOM = 259                                       # la sala acaba aquí (a sota, la barra de verbs)
FY = PL.FLOOR_Y                                    # al dibuix pla, el terra (203)
FY0 = 28                                           # al dibuix pla, on comença la paret (a dalt, el sostre pintat)
HW = FY - FY0                                      # l'alçada de les parets (175)
ZW = 280                                           # la paret del fons (la del tauler)
XL = 106                                           # al dibuix pla, la cantonada: a l'esquerra, la paret de la porta
XR = 900                                           # on s'acaba la paret del fons (fora de la pantalla)
BANC = (430, ZW - 60, 196, 46, 0.28)               # el banc: x, z del centre, llarg, fons, gir
BANC_H = FY - PL.BENCH_TOP                         # l'alçada del sobre (54)
BIDO = (236, ZW - 96, 17, 42)                      # el bidó d'oli: x, z, radi, alçada
TUB = (230, 110, HW - 6)                           # el fluorescent: x i z del centre, alçada


def _w(fx):
    """Una x del dibuix pla de la paret del fons → la x del món."""
    return fx - XL


def _wz(fx):
    """Una x del dibuix pla de la paret de la porta → la z del món."""
    return ZW - XL + fx


def _y(fy):
    """Una y del dibuix pla (el terra, a 203) → l'alçada del món."""
    return FY - fy


CAM = Camera(pos=(380, 150, -200), yaw=-0.34, pitch=0.12, f=410, centre=(320, 96))

LIGHT = Light(ambient=0.0, vignette=None, floor_fade=None)  # (la llum és la del món: la de l'Escena)
LLUMS = [Llum((TUB[0] - 30, TUB[2] - 6, TUB[1]), 330, 1.5, power=1.3),
         Llum((TUB[0] + 30, TUB[2] - 6, TUB[1]), 330, 1.5, power=1.3),           # el fluorescent
         Llum((-30, 70, _wz(46)), 170, 1.6, power=1.5)]                           # la sala de màquines, per la porta

# la llum de les textures: la del dibuix pla, sense la vinyeta ni l'enfosquiment de baix
TEX_LIGHT = Light(ambient=-0.3, vignette=None, floor_fade=None)
TEX_LIGHT.points = list(PL.LIGHT.points)

FOSC = [(2, 4, 4), (5, 9, 8), (9, 15, 13), (14, 22, 19), (20, 30, 26), (28, 40, 34)]


# ─── Les textures: el dibuix pla de sempre ───────────────────────────────────

@functools.lru_cache(maxsize=None)
def _paret():
    """Les dues parets planes, de cara: la planxa, la porta oberta cap a les màquines, el rotllo de cable, el tauler
    d'eines i l'extintor (el banc, el bidó i el prestatge van en 3D)."""
    cv = Canvas(light=TEX_LIGHT)
    plate_wall(cv, seed=3)
    PL.door(cv)
    PL.board(cv)
    ex = _extres_pla()
    cv.img.alpha_composite(ex.crop((80, 84, 108, 126)), (80, 84))                 # el rotllo de cable
    cv.img.alpha_composite(ex.crop((410, 142, 432, 186)), (410, 142))             # l'extintor
    cv.P = cv.img.load()
    return cv.img


@functools.lru_cache(maxsize=None)
def _extres_pla():
    cv = Canvas(light=TEX_LIGHT, transparent=True)
    PL.extras(cv)
    return cv.img


@functools.lru_cache(maxsize=None)
def _banc_pla():
    """El banc, el prestatge i el que hi ha a sobre, plans sobre transparent (en surten els retalls)."""
    cv = Canvas(light=TEX_LIGHT, transparent=True)
    PL.bench(cv)
    return cv.img


@functools.lru_cache(maxsize=None)
def _paret_nua():
    cv = Canvas(light=Light(ambient=-0.2, vignette=None, floor_fade=None))
    plate_wall(cv, seed=8)
    return cv.img


def _eina(draw):
    cv = Canvas(light=TEX_LIGHT, transparent=True)
    draw(cv)
    return cv.img


# ─── Les superfícies ────────────────────────────────────────────────────────

def _planxa(s, t, P):
    """Planxa estriada en coordenades del món: planxes de 100 amb soldadures, i les estries en parelles creuades."""
    x, z = P[0], P[2]
    if x % 100 < 1.2 or z % 70 < 1.2:
        return 1.1
    if x % 100 < 2.2 or z % 70 < 2.2:
        return 3.0
    a, b = int(x / 3.2) % 4, int(z / 3.2) % 4
    v = 2.6 + (fbm(x / 70, z / 50, 9) - 0.5) * 0.5
    if (a == 0 and b in (0, 1)) or (a == 2 and b in (2, 3)):
        v += 0.9
    elif (a == 1 and b == 1) or (a == 3 and b == 3):
        v -= 0.3
    return v


def _cilindre(e, sid, x, z, r, h, ramp, lvl=2.6, anelles=(), y0=0.0, n=18, llum=(-1.15, 0.9)):
    """Un cilindre dret (un bidó): facetes amb la llum de costat i la tapa vista des de dalt."""
    for i in range(n):
        a0, a1 = 2 * math.pi * i / n, 2 * math.pi * (i + 1) / n
        A = (x + r * math.cos(a0), z + r * math.sin(a0))
        B = (x + r * math.cos(a1), z + r * math.sin(a1))
        lum = llum[1] * math.cos((a0 + a1) / 2 - math.pi * llum[0])

        def lv(s, t, P, lum=lum):
            yy = h - t
            an = any(abs(yy - a) < 1.6 for a in anelles)
            return lvl + lum + (0.9 if an else 0) - (0.7 if yy < 2.5 else 0)
        e.quad(sid, (A[0], y0 + h, A[1]), (B[0], y0 + h, B[1]), (B[0], y0, B[1]), (A[0], y0, A[1]), ramp=ramp, lvl=lv)
    e.quad(sid, *[(x + dx, y0 + h, z + dz) for dx, dz in ((-r, r), (r, r), (r, -r), (-r, -r))], ramp=ramp,
           lvl=lambda s, t, P: (lvl + 0.8 if math.hypot(s - r, t - r) < r - 2.5 else lvl + 1.8) +
           (0.9 if math.hypot(s - r - 7, t - r + 3) < 2.5 else 0),
           forma=lambda s, t: math.hypot(s - r, t - r) <= r)


def _banc_P(lx, y, lz):
    """Un punt del banc (lx al llarg, lz cap al fons, des del centre) → el món."""
    bx, bz, _, _, a = BANC
    c, s = math.cos(a), math.sin(a)
    return (bx + lx * c - lz * s, y, bz + lx * s + lz * c)


def _banc_caixa(e, sid, lx0, lx1, lz0, lz1, y0, y1, ramp, lvl, cares=None):
    """Una caixa alineada amb el banc (de lx0 a lx1 al llarg, de lz0 a lz1 cap al fons)."""
    cx, _, cz = _banc_P((lx0 + lx1) / 2, 0, (lz0 + lz1) / 2)
    e.caixa_girada(sid, cx, cz, lx1 - lx0, lz1 - lz0, y1 - y0, BANC[4], ramp, lvl, y0=y0, cares=cares)


def _bfx(fx):
    """Una x del dibuix pla del banc → la posició al llarg del banc."""
    return (fx - (429 + 624) / 2) * BANC[2] / 195


def escena(cv, tex):
    """Tot el taller, de lluny a prop. → l'Escena (qui ha pintat què)."""
    e = Escena(cv, CAM, LLUMS, ambient=-0.35)
    zn = CAM.pos[2] + 40
    paret, nua, bpl = tex['paret'], tex['nua'], tex['banc']
    # la sala de màquines, a l'altra banda de la porta (una claror verdosa a la paret de davant)
    dz0, dz1 = _wz(19), _wz(72)
    e.quad('maquines', (-70, 150, dz1 + 40), (-70, 150, dz0 - 40), (-70, 0, dz0 - 40), (-70, 0, dz1 + 40), ramp=WALL,
           lvl=lambda s, t, P: 2.6 - abs(P[2] - (dz0 + dz1) / 2) / 40 - t * 0.008, dues_cares=True)
    # el sostre, fosc, amb els baos i les safates de cables
    e.quad('sostre', (0, HW, zn), (XR, HW, zn), (XR, HW, ZW), (0, HW, ZW), ramp=ENG,
           lvl=lambda s, t, P: 1.0 + (fbm(P[0] / 60, P[2] / 40, 4) - 0.5) * 0.6, dues_cares=True)
    for bx in range(-11 - XL + 85 * 2, XR, 85):
        e.caixa('sostre', bx - 3, bx + 11, HW - 10, HW, zn, ZW, ENG, 1.8,
                cares={'sota': {'ramp': ENG, 'lvl': 1.3}, 'dreta': {'ramp': ENG, 'lvl': 2.2}})
    for z in (ZW - 40, ZW - 120):
        e.caixa('sostre', 0, XR, HW - 17, HW - 14, z - 10, z + 10, CAB, 2.4, cares={'sota': {'ramp': CAB, 'lvl': 1.6}})
        for k, col in enumerate(([(20, 20, 24), (40, 36, 30), (70, 50, 34)], [(40, 12, 10), (110, 40, 34), (160, 70, 50)],
                                 [(12, 20, 40), (30, 50, 80), (60, 90, 130)])):
            e.cable('sostre', [(0, HW - 13, z - 6 + k * 6), (XR, HW - 13, z - 6 + k * 6)], col, 1.8, gruix=2.2)
    # la paret de la porta (x = 0): de prop, planxa; cap a la cantonada, el dibuix pla (x 0..106)
    e.quad('paret_esq_prop', (0, HW, zn), (0, HW, ZW - XL), (0, 0, ZW - XL), (0, 0, zn), tex=(nua, (100, FY0, 500, FY)))
    e.quad('paret_esq', (0, HW, ZW - XL), (0, HW, ZW), (0, 0, ZW), (0, 0, ZW - XL), tex=(paret, (0, FY0, XL, FY)))
    # la paret del fons (z = 280): el dibuix pla (x 106..640) i, a la dreta, més planxa
    e.quad('paret_fons', (0, HW, ZW), (W - XL, HW, ZW), (W - XL, 0, ZW), (0, 0, ZW), tex=(paret, (XL, FY0, W, FY)))
    e.quad('paret_fons_dreta', (W - XL, HW, ZW), (XR, HW, ZW), (XR, 0, ZW), (W - XL, 0, ZW), tex=(nua, (0, FY0, 400, FY)))
    # el tub d'aigua de mar, a dalt de la paret del fons
    e.tub('tubs', (-2, _y(32), ZW - 7), (XR, _y(32), ZW - 7), 3.5, SEAG, 3.0, brides=80)
    # el terra
    e.quad('terra', (0, 0, ZW), (XR, 0, ZW), (XR, 0, zn), (0, 0, zn), ramp=DECK, lvl=_planxa)
    # la llum: el bassal del fluorescent, i la claror de la sala de màquines que entra per la porta
    tx, tz, _ = TUB
    e.claror((tx - 260, 0.5, tz + 180), (tx + 260, 0.5, tz + 180), (tx + 260, 0.5, tz - 180), (tx - 260, 0.5, tz - 180),
             (220, 236, 230), lambda s, t: 0.24 * max(0.0, 1 - math.hypot((s - 260) * 0.75, t - 180) / 200))
    e.claror((0, 0.6, dz1 + 10), (110, 0.6, dz1 + 30), (110, 0.6, dz0 - 50), (0, 0.6, dz0 - 10), (130, 190, 150),
             lambda s, t: 0.2 * max(0.0, 1 - s / 110))
    # la foscor dels racons
    e.foscor('racons', (0, 0.7, ZW), (XR, 0.7, ZW), (XR, 0.7, zn), (0, 0.7, zn),
             lambda s, t: max(0.5 * max(0.0, 1 - t / 24), 0.45 * max(0.0, 1 - s / 24)))
    e.foscor('cantonada', (0, HW, ZW - 0.5), (60, HW, ZW - 0.5), (60, 0, ZW - 0.5), (0, 0, ZW - 0.5),
             lambda s, t: 0.5 * max(0.0, 1 - s / 60))
    e.foscor('sostre_fosc', (0, HW - 0.5, ZW - 0.6), (XR, HW - 0.5, ZW - 0.6), (XR, 0, ZW - 0.6), (0, 0, ZW - 0.6),
             lambda s, t: 0.45 * max(0.0, 1 - t / 34))
    # el prestatge de damunt el banc, a la paret, amb els pots i les capses (un sol retall, de cara)
    sy = _y(80)
    e.caixa('prestatge', _w(435), _w(616), sy, sy + 5, ZW - 16, ZW, WOOD, 3.4,
            cares={'dalt': {'ramp': WOOD, 'lvl': 4.2}, 'davant': {'ramp': WOOD, 'lvl': 3.6}})
    for fx in (445, 605):
        e.caixa('prestatge', _w(fx), _w(fx + 4), sy - 15, sy, ZW - 12, ZW, CAB, 2.8)
    e.sprite('prestatge', bpl.crop((436, 47, 613, 75)), ((613 - 436) / 2, 28), ((_w(436) + _w(613)) / 2, sy + 5, ZW - 8))
    # el bidó d'oli, separat de la paret, amb els degotalls
    bx, bz, br, bh = BIDO
    e.foscor('ombra_bido', (bx - 30, 0.8, bz + 26), (bx + 34, 0.8, bz + 26), (bx + 34, 0.8, bz - 26), (bx - 30, 0.8, bz - 26),
             lambda s, t: 0.6 * max(0.0, 1 - ((s - 32) / 30) ** 2 - ((t - 26) / 24) ** 2) * 1.6)
    _cilindre(e, 'bido', bx, bz, br, bh, SEAG, 2.6, anelles=(bh * 0.3, bh * 0.66))
    # el banc de treball, girat: la calaixera, les potes, el travesser, la caixa d'eines i el sobre
    lw, ld = BANC[2] / 2, BANC[3] / 2
    corners = [_banc_P(lx, 0.8, lz) for lx, lz in ((-lw - 8, ld + 10), (lw + 8, ld + 10), (lw + 8, -ld - 8), (-lw - 8, -ld - 8))]
    e.foscor('ombra_banc', *corners, lambda s, t: 0.55 * min(1.0, max(0.0, t / 16)) * min(1.0, max(0.0, s / 12)) *
             min(1.0, max(0.0, (BANC[2] + 16 - s) / 12)))
    e.foscor('ombra_banc', _banc_P(-lw - 20, 0.9, ld + 40), _banc_P(lw, 0.9, ld + 40),
             _banc_P(lw, 0.9, ld), _banc_P(-lw - 20, 0.9, ld),
             lambda s, t: 0.4 * min(1.0, t / 30))                               # l'ombra del fluorescent, cap al fons
    cal0, cal1 = _bfx(432), _bfx(488)
    _banc_caixa(e, 'banc', cal0, cal1, -ld + 2, ld - 2, 0, BANC_H - 9, ENG, 3.0,
                cares={'davant': {'tex': (bpl, (432, PL.BENCH_TOP + 11, 489, FY + 6))},
                       'esquerra': {'ramp': ENG, 'lvl': 2.2}, 'dalt': {'ramp': ENG, 'lvl': 3.0}})
    for lx in (_bfx(616), ):
        for lz in (-ld + 3, ld - 6):
            _banc_caixa(e, 'banc', lx, lx + 4, lz, lz + 3, 0, BANC_H - 9, ENG, 2.6)
    _banc_caixa(e, 'banc', cal1, _bfx(616), ld - 6, ld - 3, 10, 13, ENG, 2.2)
    _banc_caixa(e, 'banc', _bfx(507), _bfx(552), -ld + 6, ld - 12, 0, 24, REDP, 3.0,
                cares={'davant': {'ramp': REDP, 'lvl': lambda s, t, P: 1.6 if abs(t - 8) < 1 else 3.0},
                       'dalt': {'ramp': REDP, 'lvl': lambda s, t, P: 4.0 if abs(s - 22) < 7 and abs(t - 10) < 3 else 3.4},
                       'esquerra': {'ramp': REDP, 'lvl': 2.2}})
    _banc_caixa(e, 'banc', -lw, lw, -ld, ld, BANC_H - 9, BANC_H, WOOD, 3.6,
                cares={'davant': {'tex': (bpl, (429, PL.BENCH_TOP, 625, PL.BENCH_TOP + 10))},
                       'esquerra': {'ramp': WOOD, 'lvl': 3.0},
                       'dalt': {'ramp': WOOD, 'lvl': lambda s, t, P: 4.4 - (0.7 if int(s) % 31 < 1 else 0)
                                - (0.8 if hr(int(s // 3), int(t // 3), 31) > 0.95 else 0) + (fbm(s / 30, t / 8, 6) - 0.5) * 0.5}})
    # les coses de damunt el banc, dretes: el cargol de banc, el pot de llapis, l'entrepà i el torn
    top = BANC_H
    for (a, y0, b, y1, lz) in ((430, 124, 471, 149, -6), (476, 122, 491, 149, 6), (499, 136, 533, 151, -4),
                               (553, 122, 621, 149, 4)):
        P = _banc_P(_bfx((a + b) / 2), top, lz)
        e.sprite('banc_dalt', bpl.crop((a, y0, b, y1)), ((b - a) / 2, y1 - y0 - 1), P)
    # el fluorescent, penjat del sostre: els cables, la pantalla i el tub
    e.cable('llum', [(tx - 44, HW, tz), (tx - 44, TUB[2] + 4, tz)], CAB, 2.4, gruix=0.8)
    e.cable('llum', [(tx + 44, HW, tz), (tx + 44, TUB[2] + 4, tz)], CAB, 2.4, gruix=0.8)
    e.caixa('llum', tx - 53, tx + 53, TUB[2], TUB[2] + 5, tz - 7, tz + 7, CAB, 3.0,
            cares={'sota': {'ramp': TUBEC, 'lvl': lambda s, t, P: 3.4 if 3 < t < 11 else 1.4}})
    e.tub('llum', (tx - 49, TUB[2] - 1.5, tz), (tx + 49, TUB[2] - 1.5, tz), 2.0, TUBEC, 3.2)
    # primer pla: un tub que baixa a la dreta, la cadena del polispast i un carro amb planxes
    e.tub('primer_pla', (478, 0, 60), (478, HW, 60), 8, FOSC, 2.0, brides=55)
    e.tub('primer_pla', (466, 0, 72), (466, HW, 72), 4, FOSC, 1.6, brides=40)
    e.caixa('primer_pla', 60, 66, HW - 8, HW, 14, 20, FOSC, 2.0)
    for k in range(18):
        y = HW - 8 - k * 6
        e.caixa('primer_pla', 62 - (k % 2) * 1.5, 64 + (k % 2) * 1.5, y - 5, y, 16 - (1 - k % 2) * 1.5, 18 + (1 - k % 2) * 1.5,
                FOSC, 2.6)
    e.caixa_girada('primer_pla', 62, 18, 12, 8, 10, 0.3, FOSC, 2.4, y0=HW - 8 - 18 * 6 - 10)          # el ganxo
    e.caixa_girada('primer_pla', 50, -20, 80, 44, 26, -0.25, FOSC, 1.6,
                   cares={'dalt': {'ramp': FOSC, 'lvl': lambda s, t, P: 3.2 - (1.0 if int(t) % 9 < 1.5 else 0)},
                          'davant': {'ramp': FOSC, 'lvl': 1.4}, 'esquerra': {'ramp': FOSC, 'lvl': 2.2}})
    for k in range(4):
        e.caixa_girada('primer_pla', 46 + k * 3, -24 + k * 2, 70, 4, 50 - k * 6, -0.25, FOSC, 2.4 - k * 0.3, y0=26)
    return e


# ─── Composició ─────────────────────────────────────────────────────────────

def _proj(P):
    u, v, _ = CAM.projecta(P)
    return u, v


@functools.lru_cache(maxsize=None)
def _textures():
    return {'paret': _paret(), 'nua': _paret_nua(), 'banc': _banc_pla(), 'extres': _extres_pla()}


def _post(img):
    """El halo del fluorescent, damunt l'escena."""
    cv = Canvas(light=LIGHT, img=img.copy())
    u, v = _proj((TUB[0], TUB[2] - 2, TUB[1]))
    cv.glow(u, v, 110, (220, 236, 230), 0.2)
    cv.glow(u, v, 34, (255, 255, 255), 0.35)
    return cv.img


def _render(tex=None):
    cv = Canvas(light=LIGHT)
    e = escena(cv, tex or _textures())
    cv.rect(0, BOTTOM + 1, W - 1, H - 1, [(0, 0, 0)], 0, lit=0)    # la barra de verbs: negre
    return cv.img, e


@functools.lru_cache(maxsize=None)
def _base():
    return _render()


@functools.lru_cache(maxsize=None)
def _base_llum():
    return _post(_base()[0])


def bg(cv):
    cv.img.paste(_base_llum())
    cv.P = cv.img.load()


def _prop(draw):
    """Una eina penjada a la barra del tauler (un prop): plana i projectada pel tauler, amb la llum."""
    def fn(cv):
        _, e = _base()
        img = _base()[0].copy()
        img.alpha_composite(e.capa(_eina(draw), {'paret_fons'}))
        cv.img.alpha_composite(sota.fast_diff(_post(img), _base_llum()))
        cv.P = cv.img.load()
    return fn


PROPS = {'cisalla': _prop(PL.cisalla), 'clau_tubs': _prop(PL.clau_tubs)}


# ─── Animacions ─────────────────────────────────────────────────────────────

def _frames_fluorescent():
    """El fluorescent té la reactància cansada: de tant en tant fa pampallugues, com quan s'encén."""
    base = _base_llum()
    tu, tv = _proj((TUB[0], TUB[2] - 2, TUB[1]))
    a = _proj((TUB[0] - 49, TUB[2] - 2, TUB[1]))
    b = _proj((TUB[0] + 49, TUB[2] - 2, TUB[1]))
    dims = {44: 0.8, 45: 0.15, 46: 0.85, 47: 0.85, 48: 0.4, 50: 0.25}   # fotograma → quant s'apaga
    empty = Image.new('RGBA', base.size, (0, 0, 0, 0))
    frames, fets = [], {}
    for i in range(56):
        k = dims.get(i, 0)
        if not k:
            frames.append(empty)
            continue
        if k not in fets:
            cv = Canvas(light=LIGHT, img=base.copy())
            cv.darken(0, 0, W - 1, BOTTOM,
                      lambda x, y: k * max(0.0, 1 - math.hypot(x - tu, (y - tv) * 1.2) / 420), dither=False)
            if k > 0.5:                                               # el tub, gairebé apagat (els extrems roents)
                n = int(abs(b[0] - a[0])) + 1
                for j in range(n):
                    x = a[0] + (b[0] - a[0]) * j / n
                    y = a[1] + (b[1] - a[1]) * j / n
                    col = (150, 120, 110) if j < 3 or j > n - 4 else (90, 98, 96)
                    for dy in (0, 1):
                        cv.flat(x, y + dy, col)
            fets[k] = sota.fast_diff(cv.img, base)
        frames.append(fets[k])
    return frames


def _frames_mosca():
    """Una mosca que no deixa en pau l'entrepà vell: s'aixeca, fa voltes i hi torna a parar."""
    base = _base_llum()
    src = base.load()
    P = _banc_P(_bfx(514), BANC_H + 9, -4)                          # on es para (damunt del pa)
    lx, ly = (round(c) for c in _proj(P))
    k = CAM.escala(P)
    fly_n, rest_n = 34, 22
    frames = []

    def put(p, x, y, col):
        if 0 <= x < W and 0 <= y < H:
            p[x, y] = tuple(col[:3]) + (255,)
    for i in range(fly_n + rest_n):
        img = Image.new('RGBA', base.size, (0, 0, 0, 0))
        p = img.load()
        if i < fly_n:
            s = i / fly_n
            x = round(lx + (21 * math.sin(2 * math.pi * s) + 9 * math.sin(6 * math.pi * s)) * k)
            y = round(ly - (19 * math.sin(math.pi * s) + 7 * math.sin(4 * math.pi * s)) * k)
            put(p, x, y, (16, 14, 18))
            put(p, x + 1, y, (30, 26, 30))
            wy = y - 1 if i % 2 else y + 1                           # les ales, que vibren
            if 0 <= wy < H:
                put(p, x, wy, mix(src[x, wy][:3], (200, 210, 220), 0.55))
                put(p, x + 1, wy, mix(src[min(W - 1, x + 1), wy][:3], (200, 210, 220), 0.4))
        else:
            j = i - fly_n
            dx = 1 if (j // 6) % 2 else 0                            # camina una mica per l'entrepà
            put(p, lx + dx, ly, (16, 14, 18))
            put(p, lx + dx + 1, ly, (30, 26, 30))
            put(p, lx + dx, ly - 1, mix(src[lx + dx, ly - 1][:3], (170, 180, 190), 0.35))
            if j % 7 in (2, 3):                                      # es frega les potes
                put(p, lx + dx - 1, ly, (40, 34, 30))
        frames.append(img)
    return frames


ANIMS = {'fluorescent': {'frames': _frames_fluorescent, 'frameDuration': 100},
         'mosca': {'frames': _frames_mosca, 'frameDuration': 70}}


# ─── Capes del davant i geometria (coordenades de sala, projectades) ─────────

def _amo(ids):
    def mask(x, y):
        _, e = _base()
        return e.ids[e.amo[y * e.cv.w + x]] in ids
    return mask


def _p(x, z, y=0.0):
    u, v, _ = CAM.projecta((x, y, z))
    return round(u), round(v)


def _rect_mon(*Ps):
    pts = [CAM.projecta(P) for P in Ps]
    return (max(0, round(min(p[0] for p in pts))), max(0, round(min(p[1] for p in pts))),
            min(W - 1, round(max(p[0] for p in pts))), min(BOTTOM, round(max(p[1] for p in pts))))


def _escala_a(v):
    """L'escala d'un personatge amb els peus a la y de pantalla `v` (al terra, la profunditat només depèn de v)."""
    lo, hi = -300.0, 2000.0
    for _ in range(60):
        z = (lo + hi) / 2
        if CAM.projecta((250, 0, z))[1] > v:
            lo = z
        else:
            hi = z
    return CAM.escala((250, 0, (lo + hi) / 2))


def _poly_banc(marge):
    lw, ld = BANC[2] / 2 + marge, BANC[3] / 2 + marge
    return [_banc_P(lx, 0, lz) for lx, lz in ((-lw, -ld), (lw, -ld), (lw, ld), (-lw, ld))]


def _poly_bido(marge):
    bx, bz, br, _ = BIDO
    r = br + marge
    return [(bx - r, 0, bz - r), (bx + r, 0, bz - r), (bx + r, 0, bz + r), (bx - r, 0, bz + r)]


def _z_a_v(x, v):
    """La z del terra que cau a la y de pantalla `v`, a la x del món `x`."""
    lo, hi = -300.0, 2000.0
    for _ in range(50):
        z = (lo + hi) / 2
        if CAM.projecta((x, 0, z))[1] > v:
            lo = z
        else:
            hi = z
    return (lo + hi) / 2


def _bp(lx, lz):
    P = _banc_P(lx, 0, lz)
    return P[0], P[2]


# El terra on es camina (al món): de la porta fins al banc, i per darrere del cap del banc; el davant, on el
# personatge arriba a 1,2 (v ≈ 226).
V_DAVANT = 226
WALK_MON = ([(14, ZW - 26), (_w(420), ZW - 26), _bp(-BANC[2] / 2 + 30, BANC[3] / 2 + 14),
             _bp(-BANC[2] / 2 - 14, BANC[3] / 2 + 6), _bp(-BANC[2] / 2 - 14, -BANC[3] / 2 - 18),
             _bp(-BANC[2] / 2 + 90, -BANC[3] / 2 - 18), (380, _z_a_v(380, V_DAVANT))] +
            [(x, _z_a_v(x, V_DAVANT)) for x in (300, 200, 100)] + [(40, _z_a_v(40, V_DAVANT - 6)), (14, 110)])
_WALK = [_p(x, z) for x, z in WALK_MON]
_V_FONS, _V_PROP = min(v for _, v in _WALK), max(v for _, v in _WALK)

# Capes del davant: el primer pla (sempre davant), el bidó i el banc (qui hi passa per darrere, hi queda darrere).
FRONT = [
    {'id': 'davant', 'mask': _amo({'primer_pla'}), 'baseline': 999, 'zIndex': 20},
    {'id': 'davant_bido', 'mask': _amo({'bido'}), 'baseline': _p(BIDO[0], BIDO[1] - BIDO[2] + 4)[1], 'zIndex': 20},
    {'id': 'davant_banc', 'mask': _amo({'banc', 'banc_dalt'}),
     'baseline': _p(*_bp(-BANC[2] / 2, -BANC[3] / 2))[1] - 4, 'zIndex': 20},
]


def _eina_rect(x0, y0, x1, y1):
    return _rect_mon((_w(x0), _y(y0), ZW), (_w(x1), _y(y1), ZW))


GEOMETRIA = {
    'things': {
        'porta': {'rect': _rect_mon((0, _y(84), _wz(4)), (0, 0, _wz(80))), 'walk': _p(26, _wz(46))},
        'tauler': {'rect': _eina_rect(108, 36, 417, 123), 'walk': _p(_w(264), ZW - 50)},
        'cisalla': {'rect': _eina_rect(137, 125, 212, 145), 'walk': _p(_w(173), ZW - 46)},
        'clau_tubs': {'rect': _eina_rect(224, 125, 245, 159), 'walk': _p(_w(235), ZW - 46)},
        'banc': {'rect': _rect_mon(*[_banc_P(lx, y, lz) for lx in (-BANC[2] / 2, BANC[2] / 2)
                                     for lz in (-BANC[3] / 2, BANC[3] / 2) for y in (0, BANC_H + 26)]),
                 'walk': _p(*_bp(-40, -BANC[3] / 2 - 22))},
    },
    'spawns': {'iri': _p(170, 170), 'vet': _p(260, 150)},
    'walkable': _WALK,
    'forats': [[_p(x, z) for x, _, z in _poly_bido(6)]],
    'floorSquash': 0.42,                           # (la càmera, picada: el terra es veu aixafat)
    # L'ombra de contacte: la llum dominant és el fluorescent (el punt del terra a sota).
    'characterShadow': {'enabled': True, 'color': '#06080a', 'alpha': 0.42, 'squash': 0.4, 'core': 0.6,
                        'light': {'x': _p(TUB[0], TUB[1])[0], 'y': _p(TUB[0], TUB[1])[1], 'stretch': 0.5, 'reach': 200}},
    'regions': [{'id': 'perspectiva', 'active': True, 'scaleEnabled': True, 'scaleWalkSpeed': True,
                 'scaleTop': round(_escala_a(_V_FONS - 2), 3), 'scaleBottom': round(_escala_a(_V_PROP + 2), 3),
                 'points': [(0, _V_FONS - 2), (W - 1, _V_FONS - 2), (W - 1, _V_PROP + 2), (0, _V_PROP + 2)]}],
    # la llum de la sala sobre els personatges, en temps d'execució
    'characterLights': {
        'ambient': '#8a9690',                                                           # taller, llum freda
        'lights': [
            {'x': _p(TUB[0], TUB[1], TUB[2])[0], 'y': _p(TUB[0], TUB[1], TUB[2])[1], 'radius': 320,
             'color': '#dcece6', 'intensity': 0.9},                                     # el fluorescent
            {'x': _p(0, _wz(46), 70)[0], 'y': _p(0, _wz(46), 70)[1], 'radius': 120,
             'color': '#82be96', 'intensity': 0.6},                                     # la sala de màquines
        ],
    },
}

# Coses per mirar (tasca 061), en píxels de pantalla.
GEOMETRIA['things'].update({
    'pots': {'rect': (415, 45, 610, 90), 'walk': (430, 188)},
    'bido': {'rect': (295, 148, 330, 197), 'walk': (352, 206)},   # al costat, no davant (309)
})
