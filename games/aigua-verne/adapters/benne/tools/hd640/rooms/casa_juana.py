"""
Aigua Verne — `casa_juana` (P), Escena 3: l'interior del casc bolcat on viu la Juana, al fons de l'antic mar.
EN 3D (hd640/tres_d.py), a 1×.

Una càmera una mica alta i picada mira la cantonada de l'esquerra: el mirall de popa (la paret de l'esquerra, de
taules, amb la **porta** entreoberta i la sal enlluernadora de fora) fuig cap a la paret del fons, que és el costat
de la barca; a dalt, el fons de la barca fa de sostre, una volta baixa amb la quilla, i les **costelles** de fusta
pugen per la paret i s'hi corben com les d'una balena. A la paret del fons, la **prestatgeria** plena de llibres (un
volum separat de la paret), l'**ull de bou** amb el raig de llum on balla la pols, i els **mapes** del mar clavats, amb
el gràfic on la línia només baixa. Al mig, separada i girada, la taula de la Juana, amb la ràdio, papers i una tassa, i
la **làmpada** de petroli penjada de la quilla; al costat, el tamboret. A la dreta, l'**aquari** buit damunt del moble,
també girat, amb el rètol «PER QUAN TORNIN»; al racó, l'estufa i el tub que puja. Piles de llibres per terra, la
catifa de drap, i en primer pla el puntal fosc que aguanta la quilla i una pila de llibres a contrallum.

Es passa per darrere de la taula, de l'aquari, de l'estufa i de les piles de llibres. Llum càlida de la làmpada (la
que fa l'ombra dels personatges), llum freda de fora (la porta i l'ull de bou), racons foscos.

Tot el detall de les parets i els mobles ve de la casa plana de sempre (casa_juana_pla_comu.py), dibuixada de cara i
projectada. ANIMS: `flama` (la làmpada), `pols` (la pols al raig de l'ull de bou).

El món: x a la dreta (0 = el mirall de popa), y amunt (0 = el terra), z cap al fons (300 = la paret del fons);
1 unitat = 1 píxel de sala a la distància on un personatge fa 100 px (escala 1).
"""
import functools
import math
from array import array

import hd640  # noqa: F401  (abans de cap hd.rooms: posa la llibreria a 640×360)
from PIL import Image

from hd.pix import Canvas, Light, W, H, hr, mix, PAPER, MANILA, GOLD, RED, GREEN, NAVY
from hd.rooms.exterior import fbm, vnoise
from hd640.rooms import casa_juana_pla_comu as PL
from hd640.rooms.casa_juana_pla_comu import WOODI, RIB, DAY, BOOKS
from hd640.rooms.aqua_comu import SAND, PAINTW, STEELA, BLACKT, RUSTA
from hd640.tres_d import Camera, Escena, Llum, llum_personatges

BOTTOM = 259                                       # la sala acaba aquí (a sota, la barra de verbs)
ZW = 300                                           # la paret del fons (el costat de la barca)
XR = 760                                           # on s'acaba la sala per la dreta (fora de pantalla)
SP = 150                                           # on la paret del fons comença a corbar-se cap al sostre
ZK, YK = 150.0, 206.0                              # la quilla (el cim de la volta)
PORTA = (150.0, 214.0, 126.0)                      # la porta, al mirall de popa: z0, z1 i l'alçada
TAULA = (282.0, 170.0, 0.3)                        # la taula: el centre (x, z) i el gir
TW, TD, TH = 128.0, 58.0, 70.0
LAMP = (276.0, 150.0, 174.0)                       # el vidre de la làmpada (penja de la quilla)
ULL = (240, 104)                                   # (al pla, x 300: la paret és 60 més a l'esquerra)
DX = 60                                            # (la paret del pla, desplaçada cap a l'esquerra)                               # l'ull de bou, a la paret del fons (x, y)
AQUARI = (492.0, 232.0, -0.32)                     # el moble de l'aquari: el centre (x, z) i el gir
ESTUFA = (604.0, 262.0)
RIBS = (56, 180, 296, 422, 544, 664)          # les costelles (x)
PUNTAL = (470.0, 66.0)
PILA2 = (560.0, 150.0)                             # la pila de llibres de la dreta, més a prop                             # el puntal del primer pla (x, z)

CAM = Camera(pos=(300, 180, -250), yaw=-0.10, pitch=0.14, f=420, centre=(330, 58))

LIGHT = Light(ambient=0.0, vignette=None, floor_fade=None)   # (la llum és la del món: la de l'Escena)
T_LIGHT = Light(ambient=0.35, vignette=None, floor_fade=None)  # (les textures, sense llums pròpies)
LLUMS = [
    Llum(LAMP, 330, 2.6, power=1.3),                            # la làmpada
    Llum((-60, 80, (PORTA[0] + PORTA[1]) / 2), 330, 1.6, power=1.3),   # la claror de fora, per la porta
    Llum((ULL[0], ULL[1], ZW - 30), 120, 0.9, power=1.5),      # l'ull de bou
]
AMBIENT = -0.7


def volta(phi):
    """La secció de la volta (el sostre): phi = 0 a dalt de la paret del fons, π/2 a la quilla; → (z, y)."""
    return ZK + (ZW - ZK) * math.cos(phi), SP + (YK - SP) * math.sin(phi)


def sostre_y(z):
    """L'alçada del sostre a la profunditat z."""
    c = max(-1.0, min(1.0, (z - ZK) / (ZW - ZK)))
    return SP + (YK - SP) * math.sqrt(max(0.0, 1 - c * c))


# ─── Les textures: la casa plana de sempre ───────────────────────────────────

def _pla(fn, w=W, h=H, fons=None):
    cv = Canvas(w, h, light=T_LIGHT, transparent=fons is None)
    if fons is not None:
        cv.rect(0, 0, w - 1, h - 1, [fons], 0, lit=0)
    fn(cv)
    return cv.img


@functools.lru_cache(maxsize=None)
def _textures():
    # la paret del fons: el folre (la part dreta, fins a la paret), l'ull de bou i els mapes, una mica més avall
    folre = _pla(PL.folre)
    paret = Image.new('RGBA', (XR + DX, 152), (0, 0, 0, 255))
    paret.paste(folre.crop((0, 72, 640, 224)), (0, 0))
    paret.paste(folre.crop((60, 72, 240, 224)), (640, 0))
    ull = _pla(PL.ull_de_bou).crop((268, 75, 328, 135))
    paret.alpha_composite(ull, (ULL[0] + DX - 30, 152 - ULL[1] - 30))
    mapes = _pla(PL.mapes).crop((356, 34, 488, 150))
    paret.alpha_composite(mapes, (356, 34 + 44 - 72))
    porta = _pla(lambda cv: PL.porta(cv, fulla=False))
    return {
        'paret': paret,
        'porta': porta,
        'prestatgeria': _pla(PL.prestatgeria),
        'aquari': _pla(PL.aquari, fons=(40, 34, 28)),
        'estufa': _pla(PL.estufa),
        'taula': _pla(PL.taula),
        'lampada': _pla(PL.lampada),
    }


# ─── Superfícies procedurals (en coordenades del món) ─────────────────────────

def _taules(lvl0, pas=13, seed=3):
    """Traques de fusta al llarg de x (el folre, el sostre): `t` és l'alçada al llarg de la superfície."""
    def L(s, t, P):
        p = t / pas
        pf = p % 1
        x = P[0]
        v = lvl0 + (hr(int(p), int(x) // 70, seed) - 0.5) * 0.8 + (vnoise(x / 30, t / 6, 4) - 0.5) * 0.8
        if pf < 0.09:
            v -= 1.8
        elif pf < 0.2:
            v += 0.5
        if (x + int(p) * 37) % 140 < 2:
            v -= 1.4                                                   # els empalmes
        return v
    return L


def _terra(s, t, P):
    """El terra: taules de pi velles que fugen cap al fons, amb sorra a les juntes; gastat on es trepitja."""
    x, z = P[0], P[2]
    gx = x / 17
    pf = gx % 1
    v = 3.4 + (hr(int(math.floor(gx)), 4) - 0.5) * 0.8 + (vnoise(x / 20, z / 30, 81) - 0.5) * 0.7
    if pf < 0.08:
        v -= 1.8 if hr(int(gx), int(z) // 9, 2) > 0.3 else -1.4      # la junta (de vegades, plena de sorra)
    if (z + int(gx) * 53) % 190 < 1.2:
        v -= 1.4                                                       # els caps de les taules
    return v


def _catifa(cx, cz, ang, w, d):
    RUG = [[(40, 20, 20), (90, 40, 34), (140, 70, 52), (180, 110, 80)],
           [(20, 30, 46), (40, 60, 90), (70, 96, 130), (110, 140, 170)],
           [(60, 50, 30), (120, 100, 60), (170, 150, 100), (210, 190, 140)]]
    c, s_ = math.cos(ang), math.sin(ang)

    def P(a, b):
        return (cx + a * c - b * s_, 0.4, cz + a * s_ + b * c)
    return RUG, (P(-w / 2, d / 2), P(w / 2, d / 2), P(w / 2, -d / 2), P(-w / 2, -d / 2))


# ─── Les peces ──────────────────────────────────────────────────────────────

def costella(e, xr, sid='costelles'):
    """Una costella: puja per la paret del fons i segueix la volta; se'n veu la cara de dins i el costat que mira
    la càmera."""
    g, w = 12.0, 10.0                                                  # el gruix (cap a dins) i l'amplada
    x0, x1 = xr - w / 2, xr + w / 2
    xs = x1 if xr < CAM.pos[0] else x0                                 # el costat que es veu
    # el tram recte
    e.quad(sid, (xs, SP, ZW), (xs, SP, ZW - g), (xs, 0, ZW - g), (xs, 0, ZW), ramp=RIB, dues_cares=True,
           lvl=lambda s, t, P: 2.0 + (vnoise(s / 3, t / 14, xr) - 0.5) * 0.8)
    e.quad(sid, (x0, SP, ZW - g), (x1, SP, ZW - g), (x1, 0, ZW - g), (x0, 0, ZW - g), ramp=RIB,
           lvl=lambda s, t, P: 3.6 - abs(s - w / 2) * 0.12 + (vnoise(s / 3, t / 14, xr + 1) - 0.5) * 0.9
           - (1.2 if s < 1 or s > w - 1 else 0))
    # la corba
    n = 6
    for i in range(n):
        a0, a1 = (math.pi * 0.72) * i / n, (math.pi * 0.72) * (i + 1) / n
        (za, ya), (zb, yb) = volta(a0), volta(a1)
        # cap a dins: la normal de la volta, aproximada
        def inw(phi):
            nz, ny = -math.cos(phi) / (ZW - ZK), -math.sin(phi) / (YK - SP)
            k = math.hypot(nz, ny)
            return nz / k, ny / k
        (ia, ja), (ib, jb) = inw(a0), inw(a1)
        A, B = (za + ia * g, ya + ja * g), (zb + ib * g, yb + jb * g)
        e.quad(sid, (xs, ya, za), (xs, yb, zb), (xs, B[1], B[0]), (xs, A[1], A[0]), ramp=RIB, dues_cares=True,
               lvl=1.6)
        e.quad(sid, (x0, B[1], B[0]), (x1, B[1], B[0]), (x1, A[1], A[0]), (x0, A[1], A[0]), ramp=RIB, dues_cares=True,
               lvl=lambda s, t, P: 3.0 - abs(s - w / 2) * 0.12 + (vnoise(s / 3, t / 14, xr + 2) - 0.5) * 0.8
               - (1.2 if s < 1 or s > w - 1 else 0))


def llibres_pila(e, sid, x, z, n, seed, ang=0.0, fosc=0.0):
    """Una pila de llibres a terra, cadascun una mica girat. `fosc`: nivells de menys (a contrallum)."""
    y = 0.0
    for j in range(n):
        bw = 22 + hr(seed, j, 1) * 9
        bd = 15 + hr(seed, j, 5) * 5
        bh = 4.5 + hr(seed, j, 2) * 3
        a = ang + (hr(seed, j, 3) - 0.5) * 0.5
        ramp = BOOKS[int(hr(seed, j, 4) * len(BOOKS))]
        e.caixa_girada(sid, x + (hr(seed, j, 6) - 0.5) * 4, z + (hr(seed, j, 7) - 0.5) * 4, bw, bd, bh, a, ramp,
                       2.2 - fosc, y0=y,
                       cares={'dalt': {'ramp': ramp, 'lvl': 3.0 - fosc},
                              'davant': {'ramp': PAPER, 'lvl': lambda s, t, P: 3.4 - fosc - (0.8 if t % 1.5 < 0.5 else 0)},
                              'dreta': {'ramp': ramp, 'lvl': 1.8 - fosc}})
        y += bh


def taula(e, tex):
    tx, tz, ang = TAULA
    c, s_ = math.cos(ang), math.sin(ang)

    def P(a, b, y=0.0):
        return (tx + a * c - b * s_, y, tz + a * s_ + b * c)
    # l'ombra de la taula (la làmpada és just a sobre: a sota, fosc)
    e.foscor('ombra', P(-TW / 2 - 10, TD / 2 + 10, 0.6), P(TW / 2 + 10, TD / 2 + 10, 0.6),
             P(TW / 2 + 10, -TD / 2 - 10, 0.6), P(-TW / 2 - 10, -TD / 2 - 10, 0.6),
             lambda s, t: 0.6 * min(1.0, min(s, t, TW + 20 - s, TD + 20 - t) / 14))
    for a, b in ((-TW / 2 + 6, -TD / 2 + 6), (TW / 2 - 6, -TD / 2 + 6), (-TW / 2 + 6, TD / 2 - 6), (TW / 2 - 6, TD / 2 - 6)):
        q = P(a, b)
        e.caixa_girada('taula', q[0], q[2], 5, 5, TH - 6, ang, RIB, 3.4)
    e.caixa_girada('taula', tx, tz, TW, TD, 6, ang, WOODI, 4.6, y0=TH - 6,
                   cares={'dalt': {'ramp': WOODI, 'lvl': lambda s, t, P: 5.4 - (1.6 if t % 14 < 1 else 0)
                                   + (vnoise(s / 20, t / 3, 80) - 0.5) * 0.8},
                          'davant': {'ramp': WOODI, 'lvl': 3.4}, 'dreta': {'ramp': WOODI, 'lvl': 2.4},
                          'esquerra': {'ramp': WOODI, 'lvl': 2.4}})
    # damunt: papers, la llibreta vermella, la tassa, la ràdio
    for a, b, w, d, k in ((-22, -4, 24, 17, 0.1), (-4, 6, 20, 15, -0.2), (-44, 10, 18, 13, 0.4)):
        q = P(a, b)
        e.caixa_girada('taula', q[0], q[2], w, d, 0.6, ang + k, PAPER, 4.8, y0=TH)
    q = P(-48, -10)
    e.caixa_girada('taula', q[0], q[2], 18, 13, 3, ang - 0.3, RED, 2.6, y0=TH,
                   cares={'dalt': {'ramp': RED, 'lvl': 3.0}, 'davant': {'ramp': PAPER, 'lvl': 4.4}})
    q = P(44, -12)
    e.caixa_girada('taula', q[0], q[2], 7, 7, 8, ang, PAINTW, 4.2, y0=TH,
                   cares={'dalt': {'ramp': [(40, 20, 10), (70, 40, 20)], 'lvl': 1.0}})
    # la ràdio: el davant, el dibuix pla
    q = P(14, 8)
    img = tex['taula']
    e.caixa_girada('taula', q[0], q[2], 32, 16, 22, ang, WOODI, 3.6, y0=TH,
                   cares={'davant': {'tex': (img, (392, 156, 423, 178))}, 'dalt': {'ramp': WOODI, 'lvl': 5.0},
                          'dreta': {'ramp': WOODI, 'lvl': 2.6}})
    r = P(28, 12, TH + 22)
    e.cable('taula', [r, (r[0] + 6, r[1] + 16, r[2] + 4)], STEELA, 4.6, gruix=0.8)
    # el tamboret
    sx, sz = P(TW / 2 + 22, -6)[0], P(TW / 2 + 22, -6)[2]
    e.foscor('ombra', (sx - 18, 0.6, sz + 14), (sx + 18, 0.6, sz + 14), (sx + 18, 0.6, sz - 14), (sx - 18, 0.6, sz - 14),
             lambda s, t: 0.5 * max(0.0, 1 - ((s - 18) / 18) ** 2 - ((t - 14) / 14) ** 2) * 1.6)
    for a, b in ((-8, -6), (8, -6), (0, 8)):
        e.caixa('taula', sx + a - 1.5, sx + a + 1.5, 0, 40, sz + b - 1.5, sz + b + 1.5, RIB, 3.4)
    e.caixa_girada('taula', sx, sz, 26, 22, 4, ang + 0.4, WOODI, 4.8, y0=40)


def tamboret():
    tx, tz, ang = TAULA
    c, s_ = math.cos(ang), math.sin(ang)
    a, b = TW / 2 + 22, -6
    return tx + a * c - b * s_, tz + a * s_ + b * c


def aquari(e, tex):
    """L'aquari buit damunt del moble, separat de la paret i girat: el davant del vidre, el dibuix pla."""
    ax, az, ang = AQUARI
    img = tex['aquari']
    e.foscor('ombra', (ax - 66, 0.6, az + 30), (ax + 66, 0.6, az + 30), (ax + 66, 0.6, az - 34), (ax - 66, 0.6, az - 34),
             lambda s, t: 0.6 * min(1.0, min(s, t, 132 - s, 64 - t) / 12))
    e.caixa_girada('aquari', ax, az, 104, 44, 40, ang, WOODI, 3.4,
                   cares={'davant': {'tex': (img, (500, 187, 601, 226))}, 'dalt': {'ramp': WOODI, 'lvl': 5.0},
                          'esquerra': {'ramp': WOODI, 'lvl': 2.2}, 'dreta': {'ramp': WOODI, 'lvl': 2.2}})
    # el vidre: el fons i els costats verdosos, la sorra; el davant, el dibuix pla (amb el rètol)
    GL = [(40, 56, 54), (70, 94, 90), (110, 140, 134), (156, 184, 176), (204, 224, 216)]
    e.caixa_girada('aquari', ax, az, 96, 38, 60, ang, GL, 1.6, y0=40,
                   cares={'davant': {'tex': (img, (502, 126, 599, 187))},
                          'dalt': {'ramp': STEELA, 'lvl': lambda s, t, P: 4.6 if s < 2 or s > 94 or t < 2 or t > 36 else 0.6},
                          'esquerra': {'ramp': GL, 'lvl': lambda s, t, P: 2.6 if t < 48 else 3.8},
                          'dreta': {'ramp': GL, 'lvl': lambda s, t, P: 2.6 if t < 48 else 3.8}})


def estufa(e, tex):
    sx, sz = ESTUFA
    img = tex['estufa']
    e.foscor('ombra', (sx - 30, 0.6, sz + 26), (sx + 30, 0.6, sz + 26), (sx + 30, 0.6, sz - 30), (sx - 30, 0.6, sz - 30),
             lambda s, t: 0.6 * max(0.0, 1 - ((s - 30) / 30) ** 2 - ((t - 28) / 28) ** 2) * 1.5)
    e.caixa_girada('estufa', sx, sz, 30, 26, 52, -0.2, BLACKT, 2.4,
                   cares={'davant': {'tex': (img, (607, 177, 638, 230))}, 'dalt': {'ramp': BLACKT, 'lvl': 3.6}})
    e.tub('estufa', (sx + 2, sostre_y(sz) + 4, sz + 4), (sx + 2, 52, sz), 4, STEELA, 3.4, brides=30)
    e.caixa_girada('estufa', sx - 6, sz - 4, 7, 7, 10, 0.2, PAINTW, 4.2, y0=52)              # la cafetera


def lampada(e, tex):
    img = tex['lampada'].crop((330, 85, 355, 116))
    x, y, z = LAMP
    e.linia((x, sostre_y(z) - 4, z), (x, y + 15, z), [(80, 60, 20), (150, 120, 50), (220, 190, 110)], 1.4)
    e.sprite('lampada', img, (12, 15), (x, y, z))


def primer_pla(e):
    """El puntal fosc que aguanta la quilla, a la dreta, i una pila de llibres a contrallum, a baix a l'esquerra."""
    px, pz = PUNTAL
    e.caixa('primer_pla', px - 9, px + 9, 0, 260, pz - 9, pz + 9, RIB, 1.4,
            cares={'esquerra': {'ramp': RIB, 'lvl': lambda s, t, P: 2.4 + (vnoise(s / 3, t / 20, 9) - 0.5) * 0.9
                                - (1.0 if s < 1.5 or s > 16.5 else 0)},
                   'davant': {'ramp': RIB, 'lvl': lambda s, t, P: 1.3 + (vnoise(s / 3, t / 20, 8) - 0.5) * 0.7}})
    e.cable('primer_pla', [(px - 9, 120, pz - 9.5), (px + 9, 118, pz - 9.5)], [(30, 22, 16), (60, 46, 30), (90, 70, 46)],
            1.4, gruix=2.4)                                            # una corda lligada al puntal
    e.cable('primer_pla', [(px - 9, 119, pz - 9.5), (px - 20, 80, pz - 12), (px - 16, 50, pz - 12)],
            [(30, 22, 16), (60, 46, 30), (90, 70, 46)], 1.2, gruix=1.6)
    llibres_pila(e, 'primer_pla_llibres', 70, 20, 7, 11, 0.4, fosc=1.8)
    llibres_pila(e, 'primer_pla_llibres', 104, 8, 4, 12, -0.3, fosc=2.0)


def escena(cv, tex):
    """Tota la sala, de lluny a prop. → l'Escena (qui ha pintat què)."""
    e = Escena(cv, CAM, LLUMS, ambient=AMBIENT)
    e.amo = array('H', bytes(2 * cv.w * cv.h))         # (més de 255 superfícies: l'amo de cada píxel, en 16 bits)
    zn = CAM.pos[2] + 60
    # el sostre: la volta, de traques al llarg de x, en tires
    n = 10
    for i in range(n):
        a0, a1 = math.pi * 0.86 * i / n, math.pi * 0.86 * (i + 1) / n
        (za, ya), (zb, yb) = volta(a0), volta(a1)
        e.quad('sostre', (0, ya, za), (XR, ya, za), (XR, yb, zb), (0, yb, zb), ramp=WOODI, dues_cares=True,
               lvl=lambda s, t, P, i=i: _taules(2.6 - 0.1 * i, seed=5)(s, P[2] * 0.5 + i * 31, P))
    # la quilla
    e.caixa('quilla', 0, XR, YK - 16, YK, ZK - 9, ZK + 9, RIB, 2.6,
            cares={'davant': {'ramp': RIB, 'lvl': lambda s, t, P: 2.4 + (1.6 if abs(s % 32 - 16) < 1.2 and abs(t - 8) < 1.2 else 0)},
                   'sota': {'ramp': RIB, 'lvl': 3.2}})
    # la paret del fons: el folre, amb l'ull de bou i els mapes (el dibuix pla)
    paret = tex['paret']
    e.quad('paret_fons', (0, SP, ZW), (XR, SP, ZW), (XR, 0, ZW), (0, 0, ZW), tex=(paret, (DX, 2, XR + DX, 152)))
    # el mirall de popa (la paret de l'esquerra): taules i la porta
    e.quad('paret_esq', (0, YK, zn), (0, YK, ZW), (0, 0, ZW), (0, 0, zn), ramp=WOODI,
           lvl=lambda s, t, P: _taules(3.0, pas=15, seed=7)(s, YK - P[1], (P[2], 0, P[2])),
           forma=lambda s, t: YK - t <= sostre_y(zn + s) + 1)
    z0, z1, ph = PORTA
    e.quad('porta', (0.5, ph + 5, z0 - 5), (0.5, ph + 5, z1 + 5), (0.5, 0, z1 + 5), (0.5, 0, z0 - 5),
           tex=(tex['porta'], (35, 95, 109, 226)))
    # el terra
    e.quad('terra', (0, 0, ZW), (XR, 0, ZW), (XR, 0, zn), (0, 0, zn), ramp=WOODI, lvl=_terra)
    RUG, rq = _catifa(282, 138, 0.3, 230, 110)
    e.quad('catifa', *rq, ramp=RUG[0],
           lvl=lambda s, t, P: 2.2 + (0.8 if (int(s) + int(t)) % 2 else 0) + (vnoise(s / 9, t / 3, 82) - 0.5) * 0.8
           - (1.2 if int(s / 230 * 14) % 3 == 1 else 0) + (1.0 if int(s / 230 * 14) % 3 == 2 else 0)
           - (1.4 if s < 2 or s > 228 else 0))
    # el bassal de llum càlida de la làmpada, al terra
    lx, _, lz = LAMP
    e.claror((lx - 170, 0.5, lz + 120), (lx + 170, 0.5, lz + 120), (lx + 170, 0.5, lz - 150), (lx - 170, 0.5, lz - 150),
             (255, 200, 120), lambda s, t: 0.2 * max(0.0, 1 - math.hypot(s - 170, (t - 120) * 1.1) / 170) ** 1.4)
    # la foscor dels racons: on les parets es troben amb el terra i entre elles, i al fons de la volta
    e.foscor('racons', (0, 0.5, ZW), (XR, 0.5, ZW), (XR, 0.5, zn), (0, 0.5, zn),
             lambda s, t: max(0.6 * max(0.0, 1 - t / 30), 0.5 * max(0.0, 1 - s / 30)))
    e.foscor('racons', (0.3, YK, zn), (0.3, YK, ZW), (0.3, 0, ZW), (0.3, 0, zn),
             lambda s, t: 0.45 * max(0.0, 1 - (ZW - zn - s) / 50))
    e.foscor('racons', (0, SP, ZW - 0.3), (XR, SP, ZW - 0.3), (XR, 0, ZW - 0.3), (0, 0, ZW - 0.3),
             lambda s, t: max(0.5 * max(0.0, 1 - s / 50), 0.35 * max(0.0, 1 - t / 30)))
    # la llum de fora: una falca freda que entra per la porta i s'escampa en diagonal pel terra
    e.claror((0, 0.5, z1 + 10), (190, 0.5, z1 - 40), (190, 0.5, z0 - 140), (0, 0.5, z0 - 6), DAY,
             lambda s, t: 0.42 * max(0.0, 1 - s / 190) ** 1.1 * max(0.0, math.sin(math.pi * min(1.0, t / max(1.0, 70 + 0.5 * s)))))
    for k in range(70):                                                # la sorra que hi ha entrat
        sx, sz = hr(k, 1) * 110, z0 - 60 + hr(k, 2) * 130
        if hr(k, 3) > 0.3:
            u, v, _ = CAM.projecta((sx, 0, sz))
            if 0 <= u < W and 0 <= v < BOTTOM:
                cv.put(u, v, SAND, 6.0, lit=0)
    # les costelles
    for xr in RIBS:
        costella(e, xr)
    # la prestatgeria, separada de la paret: el davant, el dibuix pla
    pres = tex['prestatgeria']
    e.foscor('ombra', (56, 0.6, ZW), (178, 0.6, ZW), (178, 0.6, ZW - 46), (56, 0.6, ZW - 46),
             lambda s, t: 0.6 * max(0.0, 1 - (t - 12) / 34) if t > 12 else 0.6)
    e.caixa('prestatgeria', 62, 172, 0, 166, ZW - 38, ZW - 13, WOODI, 2.4,
            cares={'davant': {'tex': (pres, (122, 58, 233, 224))}, 'dalt': {'ramp': RIB, 'lvl': 4.2},
                   'esquerra': {'ramp': RIB, 'lvl': 2.6}, 'dreta': {'ramp': RIB, 'lvl': 3.4}})
    # el raig de l'ull de bou: baixa de biaix fins al terra
    ux, uy = ULL
    e.claror((ux - 12, uy + 14, ZW - 1), (ux + 12, uy + 14, ZW - 1), (ux + 44, 0.8, ZW - 120), (ux - 6, 0.8, ZW - 120),
             DAY, lambda s, t: 0.16 * (1 - abs(s - 12) / 14) * (1 - t / 260))
    e.claror((ux - 10, 0.7, ZW - 60), (ux + 50, 0.7, ZW - 60), (ux + 50, 0.7, ZW - 140), (ux - 10, 0.7, ZW - 140), DAY,
             lambda s, t: 0.28 * max(0.0, 1 - ((s - 30) / 30) ** 2 - ((t - 40) / 40) ** 2))
    # piles de llibres a terra (pel fons i pel mig)
    for x, z, nb, seed, a in ((80, 236, 7, 1, 0.2), (136, 252, 5, 2, -0.3), (190, 222, 9, 3, 0.5), (400, 214, 4, 4, -0.2)):
        llibres_pila(e, 'piles', x, z, nb, seed, a)
    llibres_pila(e, 'piles2', *PILA2, 8, 5, 0.3)
    # un llibre obert a terra
    e.caixa_girada('piles', 250, 96, 30, 20, 1.5, -0.4, PAPER, 4.8,
                   cares={'dalt': {'ramp': PAPER, 'lvl': lambda s, t, P: 4.8 - (2.0 if abs(s - 15) < 0.8 else 0)
                                   - (1.0 if t % 3 < 0.8 and 3 < s < 27 and abs(s - 15) > 2 else 0)}})
    aquari(e, tex)
    estufa(e, tex)
    taula(e, tex)
    lampada(e, tex)
    primer_pla(e)
    return e


# ─── Composició ────────────────────────────────────────────────────────────

@functools.lru_cache(maxsize=None)
def _base():
    cv = Canvas(light=LIGHT)
    e = escena(cv, _textures())
    u, v, _ = CAM.projecta(LAMP)
    cv.glow(u, v, 52, (255, 210, 130), 0.3)                        # el halo de la làmpada
    cv.rect(0, BOTTOM + 1, W - 1, H - 1, [(0, 0, 0)], 0, lit=0)    # la barra de verbs: negre
    return cv.img, e


def bg(cv):
    img, _ = _base()
    cv.img.paste(img)
    cv.P = cv.img.load()


PROPS = {}


# ─── Animacions ────────────────────────────────────────────────────────────

def _frames_flama():
    """La flama de la làmpada: el cor del vidre i el halo tremolen."""
    u, v, _ = CAM.projecta(LAMP)
    k_ = CAM.escala(LAMP)
    x, y = round(u), round(v + 2 * k_)
    out = []
    for i in range(8):
        img = Image.new('RGBA', (W, H), (0, 0, 0, 0))
        P = img.load()
        k = 0.5 + 0.5 * math.sin(i / 8 * 2 * math.pi * 2 + hr(i, 1)) * (0.5 + 0.5 * hr(i, 2))
        fh = 3 + int(k * 3)
        for yy in range(y + 3 - fh, y + 4):
            hw = 1.4 * (1 - (y + 3 - yy) / (fh + 1)) + 0.4
            for xx in range(int(x - hw), int(x + hw) + 1):
                P[xx, yy] = (255, 250, 220, 255) if abs(xx - x) < 1 else (255, 200, 90, 255)
        for yy in range(y - 26, y + 26):
            for xx in range(x - 26, x + 26):
                d = math.hypot(xx - x, yy - y) / 26
                if 0.3 < d < 1 and hr(xx, yy, i) < (1 - d) * 0.2 * k and P[xx, yy][3] == 0:
                    P[xx, yy] = (255, 214, 140, 70)
        out.append(img)
    return out


def _frames_pols():
    """La pols que balla al raig de l'ull de bou (punts del món dins el raig, projectats)."""
    ux, uy = ULL
    out = []
    n = 16
    for i in range(n):
        img = Image.new('RGBA', (W, H), (0, 0, 0, 0))
        P = img.load()
        for k in range(30):
            t = (hr(k, 1) + i / n * (0.3 + hr(k, 4) * 0.2) * (1 if k % 2 else -1)) % 1
            s = hr(k, 2)
            # el raig: de l'ull de bou (ZW, uy) al terra (ZW − 120, 0), i s'eixampla
            wx = ux - 12 + s * 24 + t * (s * 26 + 6) + math.sin(i / n * 2 * math.pi + k) * 2
            wy = (uy + 14) * (1 - t)
            wz = ZW - 1 - 120 * t
            u, v, _ = CAM.projecta((wx, wy, wz))
            a = int(170 * (1 - abs(s - 0.5) * 2) * (1 - t * 0.6))
            if 0 <= u < W and 0 <= v < BOTTOM:
                P[int(u), int(v)] = (255, 250, 230, a)
        out.append(img)
    return out


ANIMS = {'flama': {'frames': _frames_flama, 'frameDuration': 120},
         'pols': {'frames': _frames_pols, 'frameDuration': 140}}


# ─── Capes del davant ───────────────────────────────────────────────────────

def _amo(ids):
    def mask(x, y):
        _, e = _base()
        return e.ids[e.amo[y * e.cv.w + x]] in ids
    return mask


def _p(x, z, y=0.0):
    u, v, _ = CAM.projecta((x, y, z))
    return round(u), round(v)


def _vz(z):
    """La y de pantalla d'un punt del terra a la profunditat z (al mig de la sala)."""
    return CAM.projecta((300, 0, z))[1]


def _base_v(cx, cz, w, d, ang):
    """La línia base d'un moble girat: la y de pantalla del seu cantó de davant (el més baix a la pantalla)."""
    c, s_ = math.cos(ang), math.sin(ang)
    return max(CAM.projecta((cx + a * c - b * s_, 0, cz + a * s_ + b * c))[1]
               for a in (-w / 2, w / 2) for b in (-d / 2, d / 2))


FRONT = [
    {'id': 'davant_taula', 'mask': _amo({'taula'}), 'baseline': round(_base_v(TAULA[0], TAULA[1], TW, TD, TAULA[2]) - 8),
     'zIndex': 20},
    {'id': 'davant_aquari', 'mask': _amo({'aquari'}),
     'baseline': round(_base_v(AQUARI[0], AQUARI[1], 104, 44, AQUARI[2]) - 6), 'zIndex': 20},
    {'id': 'davant_estufa', 'mask': _amo({'estufa'}), 'baseline': round(_vz(ESTUFA[1] - 8)), 'zIndex': 20},
    {'id': 'davant_piles', 'mask': _amo({'piles'}), 'baseline': round(_vz(222)), 'zIndex': 20},
    {'id': 'davant_piles2', 'mask': _amo({'piles2'}), 'baseline': round(_vz(PILA2[1] - 10)), 'zIndex': 20},
    {'id': 'davant', 'mask': _amo({'primer_pla', 'primer_pla_llibres'}), 'baseline': 999, 'zIndex': 20},
]


# ─── Geometria (coordenades de sala, projectades) ────────────────────────────

def _rect_mon(*Ps):
    pts = [CAM.projecta(P) for P in Ps]
    return (max(0, round(min(p[0] for p in pts))), max(0, round(min(p[1] for p in pts))),
            min(W - 1, round(max(p[0] for p in pts))), min(BOTTOM, round(max(p[1] for p in pts))))


def _caixa_terra(cx, cz, w, d, ang, m=0.0):
    c, s_ = math.cos(ang), math.sin(ang)
    w, d = w / 2 + m, d / 2 + m
    return [_p(cx + a * c - b * s_, cz + a * s_ + b * c) for a, b in ((-w, -d), (w, -d), (w, d), (-w, d))]


def _cercle(cx, cz, r, n=8):
    return [_p(cx + r * math.cos(2 * math.pi * i / n), cz + r * math.sin(2 * math.pi * i / n)) for i in range(n)]


# El terra on es camina (al món): de la porta fins a l'estufa, davant la prestatgeria i els mapes, sense arribar al
# puntal ni a la pila de llibres del primer pla.
def _x_u(u, z):
    """La x del terra que cau a la x de pantalla `u` a la profunditat z."""
    lo, hi = -500.0, 1500.0
    for _ in range(50):
        x = (lo + hi) / 2
        if CAM.projecta((x, 0, z))[0] < u:
            lo = x
        else:
            hi = x
    return (lo + hi) / 2


ZN = 98.0                                          # la vora de davant (escala ≈1,2)
WALK_MON = [(24, ZN), (24, 236), (52, 236), (52, 256), (240, 268), (440, 268), (440, 214), (_x_u(632, 214), 214),
            (_x_u(632, ZN + 30), ZN + 30), (PUNTAL[0] - 6, ZN)]
_WALK = [_p(x, z) for x, z in WALK_MON]
_V_FONS, _V_PROP = min(v for _, v in _WALK), max(v for _, v in _WALK)


def _escala_a(v):
    """L'escala d'un personatge amb els peus a la y de pantalla `v` (al terra, la profunditat només depèn de v)."""
    lo, hi = 1.0, 2000.0
    for _ in range(60):
        z = (lo + hi) / 2
        if CAM.projecta((300, 0, z))[1] > v:
            lo = z
        else:
            hi = z
    return CAM.escala((300, 0, (lo + hi) / 2))


_LU, _LV = _p(LAMP[0], LAMP[2])
_TB = tamboret()

GEOMETRIA = {
    'things': {
        'porta': {'rect': _rect_mon((0, PORTA[2] + 6, PORTA[0] - 6), (0, 0, PORTA[1] + 6)),
                  'walk': _p(40, (PORTA[0] + PORTA[1]) / 2 - 10)},
        'mapes': {'rect': _rect_mon((358 - DX, 146, ZW), (486 - DX, 30, ZW)),
                  'walk': _p(360, 236)},
        'llibres': {'rect': _rect_mon((62, 166, ZW - 38), (172, 0, ZW - 38)), 'walk': _p(120, 222)},
        'aquari': {'rect': _rect_mon(*[(AQUARI[0] + a, y, AQUARI[1] + b) for a in (-52, 52) for b in (-22, 22)
                                       for y in (0, 100)]),
                   'walk': _p(AQUARI[0] - 30, AQUARI[1] - 60)},
        'finestra': {'rect': _rect_mon((ULL[0] - 22, ULL[1] + 22, ZW), (ULL[0] + 22, ULL[1] - 22, ZW)),
                     'walk': _p(ULL[0], 236)},
    },
    'spawns': {'juana': _p(_TB[0] + 6, _TB[1] - 14), 'iri': _p(160, 120), 'vet': _p(230, 92)},
    'walkable': _WALK,
    'forats': [_caixa_terra(TAULA[0], TAULA[1], TW, TD, TAULA[2], 6), _caixa_terra(AQUARI[0], AQUARI[1], 104, 44,
                                                                                AQUARI[2], 8),
               _cercle(ESTUFA[0], ESTUFA[1], 26), _cercle(190, 222, 18, 6), _cercle(400, 214, 18, 6),
               _cercle(_TB[0], _TB[1], 16, 6), _cercle(PILA2[0], PILA2[1], 18, 6)],
    # L'ombra de contacte: la làmpada, just damunt la taula (el punt del terra de sota), càlida i a prop.
    'floorSquash': 0.42,
    'characterShadow': {'enabled': True, 'color': '#1a0e08', 'alpha': 0.42, 'squash': 0.42, 'core': 0.6,
                        'light': {'x': _LU, 'y': _LV, 'stretch': 0.8, 'reach': 130}},
    'regions': [{'id': 'perspectiva', 'active': True, 'scaleEnabled': True, 'scaleWalkSpeed': True,
                 'scaleTop': round(_escala_a(_V_FONS - 2), 3), 'scaleBottom': round(_escala_a(_V_PROP + 2), 3),
                 'points': [(0, _V_FONS - 2), (W - 1, _V_FONS - 2), (W - 1, _V_PROP + 2), (0, _V_PROP + 2)]}],
    # La llum de la sala sobre els personatges (characterLights del motor): la casa de fusta, càlida i fosca: la
    # làmpada, la claror freda de la porta i l'ull de bou.
    'characterLights': {
        'ambient': '#8a7464',
        'lights': [
            llum_personatges(CAM, LLUMS[0].pos, LLUMS[0].r, '#ffc880', 0.55),  # la làmpada
            llum_personatges(CAM, LLUMS[1].pos, LLUMS[1].r, '#eef2ff', 0.5),  # la porta
            llum_personatges(CAM, LLUMS[2].pos, LLUMS[2].r, '#dde8ff', 0.2),  # l'ull de bou
        ],
    },
}
