"""
La Conjura de l'Avet — `bugaderia`, la bugaderia del monestir (acte 2, Iri). Capvespre. Sala «de prop». EN 3D, a 1×.

Una sala baixa de pedra, plena de vapor (ANIMS `vapor`), amb la llum blava d'una finestra petita i una llàntia al
mur; amb el foc encès (decorat `foc_ences`: flames animades i més vapor), tot es torna taronja. La càmera és a la
cantonada de davant a l'esquerra i mira cap a la cantonada del fons a la dreta, una mica avall:
  - a la paret del fons: la **pila de llenya** en tres munts ben diferents (`llenya_pi`: clara i resinosa;
    `llenya_pollancre`: blanca i lleugera; `llenya_alzina`: fosca i densa), el **fogó** de pedra amb la **tina**
    gran de coure al damunt, i la **porta** del claustre (oberta: la galeria blava del capvespre);
  - a la paret de la dreta: la finestra petita, el clau amb les **tisores** de bugadera (un prop) i, davant, el
    **bagul** de roba vella, girat;
  - per terra, dues tines petites i lloses molles;
  - primer pla (FRONT): la corda amb les **robes** esteses, en diagonal; la Iri hi passa per darrere (la capa es
    talla en franges, cadascuna amb la línia base del terra que hi ha sota la corda).

Decorats: `bagul_obert`, `foc_ences` (animat), `tina_negra`, `habits_estesos` (els dos hàbits negres penjats a la
perxa del costat del fogó, fumejant) i `tisores_agafades` (el clau buit i la marca a la paret).

El món: x a la dreta (0 = la paret de l'esquerra), y amunt, z cap al fons (280 = la paret del fons).
"""
import functools
import math

import numpy as np
from PIL import Image

from hd.pix import Canvas, Light
from hd640.tres_d import Camera, Escena, Llum
from hd640.rooms.claustre_comu import (
    ajusta_geometria,
    W, H, RH, GRES, BLANC, LLOSA, FUSTA, FERRO, FOC, LLI, NEGRE, COURE, FANG, PEDRA, nz, fbm, hr, smooth, diferencia, mur_pedra,
    sense_hud, fosc_hud, mascara_amo, escala_v, v_escala)

CAM = Camera(pos=(170, 140, -250), yaw=0.24, pitch=0.16, f=400, centre=(320, 110))
XW, ZW, HW = 440, 280, 164                         # la paret de la dreta, la del fons, el sostre
LIGHT = Light(ambient=0.0, vignette=None, floor_fade=None)

LLENYA = (10, 150, 52)                             # x0, x1 (a la paret del fons), fondària
MUNTS = {'llenya_pi': (12, 54), 'llenya_pollancre': (58, 100), 'llenya_alzina': (104, 148)}
FOGO = (176, 316, 46, 64)                         # x0, x1, alçada, fondària (contra la paret del fons)
TINA = (246, ZW - 34, 50, 56)                     # cx, cz, radi, alçada (damunt el fogó)
PORTA = (346, 404, 120)                           # x0, x1, alçada (a la paret del fons)
FINESTRA = (150, 196, 92, 128)                    # z0, z1, y0, y1 (a la paret de la dreta)
TISORES = (96, 112)                               # z, y del clau (paret de la dreta)
BAGUL = (372, 92, 84, 46, 40, -0.34)              # cx, cz, ample, fons, alçada, gir
PERXA = (408, 186, 262, 132)                      # x, z0, z1 (al llarg de la paret de la dreta), alçada
CORDA = ((-60, 154, -40), (XW, 156, 150))         # la corda de les robes, de davant a l'esquerra al fons a la dreta
TINETES = ((132, 150, 26), (326, 196, 22))        # les tines petites: x, z, radi
LLANTIA = (0, 120, 112)                           # la llàntia del mur de l'esquerra: x, z, y


# ─── Modes de llum ───────────────────────────────────────────────────────────

def _llums(foc):
    ll = [Llum((XW - 6, 116, 172), 380, 1.2, power=1.2),            # la finestra (blava)
          Llum((LLANTIA[0] + 10, LLANTIA[2], LLANTIA[1]), 220, 1.0, power=1.4),
          Llum((380, 70, ZW - 10), 200, 0.7, power=1.3)]          # la porta del claustre
    if foc:
        ll.append(Llum(((FOGO[0] + FOGO[1]) / 2, 30, ZW - 70), 420, 2.6, power=1.1))
    return ll


# ─── Dibuixos plans ──────────────────────────────────────────────────────────

def _paret_fons():
    """La paret del fons vista de cara: XW × HW (x del món, y = HW − alçada). La porta (oberta a la galeria blava) i
    la boca del fogó (la volta fosca on va el foc) amb el sutge damunt."""
    cv = Canvas(XW, HW)
    mur_pedra(cv, 0, 0, XW, HW, 3.4, 3)
    # el sutge del fogó, que puja per la paret
    f0, f1 = FOGO[0], FOGO[1]
    for y in range(0, HW - FOGO[2]):
        for x in range(f0 - 10, f1 + 10):
            t = (HW - FOGO[2] - y) / (HW - FOGO[2])
            cx = (f0 + f1) / 2
            k = max(0.0, 1 - abs(x - cx) / ((f1 - f0) / 2 + 10 - t * 20)) * (0.75 - t * 0.5)
            if k > 0:
                o = cv.P[x, y]
                m = 1 - min(0.8, k * (0.7 + nz(x / 6, y / 8, 5) * 0.6))
                cv.P[x, y] = (int(o[0] * m), int(o[1] * m), int(o[2] * m), 255)
    # la porta: la galeria del claustre al capvespre, a través (blau), amb el marc de gres
    x0, x1, ph = PORTA
    r = (x1 - x0) / 2
    cx, ya = (x0 + x1) / 2, HW - ph + r
    blau = [(14, 20, 40), (22, 30, 56), (34, 44, 76), (50, 62, 96), (72, 84, 116), (100, 110, 138)]
    for y in range(int(HW - ph - 9), HW):
        for x in range(int(x0 - 9), int(x1 + 10)):
            d = math.hypot(x - cx, y - ya) if y < ya else abs(x - cx)
            if d <= r:
                t = (y - (HW - ph)) / ph
                lvl = 2.6 + t * 1.6 + (nz(x / 6, y / 6, 4) - 0.5) * 0.4
                if abs(x - (x0 + 14)) < 3 and y > HW - ph * 0.8:
                    lvl = 0.6                                         # una columna de la galeria, a fora
                cv.put(x, y, blau, lvl, lit=0)
            elif d <= r + 8:
                a = int((math.atan2(y - ya, x - cx) + math.pi) * 5)
                cv.put(x, y, GRES, 4.4 + (a % 2) * 0.6 - (1.2 if d - r < 1.3 else 0), lit=0)
    return cv.img


def _paret_dreta():
    """La paret de la dreta vista de cara: (ZW + 200) × HW (x = ZW − z, y = HW − alçada): la finestreta amb el cel
    blau i els barrots, el clau de les tisores."""
    w = ZW + 200
    cv = Canvas(w, HW)
    mur_pedra(cv, 0, 0, w, HW, 3.6, 7)
    z0, z1, y0, y1 = FINESTRA
    fx0, fx1, fy0, fy1 = ZW - z1, ZW - z0, HW - y1, HW - y0
    cel = [(30, 40, 70), (44, 58, 96), (64, 82, 124), (92, 110, 150), (130, 146, 178)]
    for y in range(fy0 - 5, fy1 + 6):
        for x in range(fx0 - 5, fx1 + 6):
            if fx0 <= x <= fx1 and fy0 <= y <= fy1:
                cv.put(x, y, cel, 3.4 - (y - fy0) / (fy1 - fy0) * 1.4 + (nz(x / 8, y / 5, 9) - 0.5), lit=0)
            else:
                cv.put(x, y, GRES, 4.8 - (1.0 if y > fy1 else 0), lit=0)              # el marc i l'ampit
    for bx in range(fx0 + 10, fx1, 12):
        cv.rect(bx, fy0, bx + 1, fy1, FERRO, 1.6, lit=0)
    # el clau de les tisores
    tz, ty = TISORES
    X, Y = ZW - tz, HW - ty
    cv.rect(X - 1, Y - 1, X + 1, Y + 1, FERRO, 3.6, lit=0)
    return cv.img


def _tisores_img():
    """Les tisores de bugadera (grosses: 18×44), penjades pel forat d'un ull."""
    cv = Canvas(20, 46, transparent=True)
    # els dos ulls (anelles), a dalt
    for cx in (6, 13):
        for a in range(0, 360, 12):
            x = cx + math.cos(math.radians(a)) * 4.2
            y = 6 + math.sin(math.radians(a)) * 4.8
            cv.put(x, y, FERRO, 4.4 - math.sin(math.radians(a)) * 0.8, lit=0)
            cv.put(x + 0.6, y, FERRO, 3.6, lit=0)
    # les fulles, una mica obertes
    for k in range(32):
        t = k / 31
        for side, x0 in ((-1, 7.5), (1, 11.5)):
            x = x0 + side * (1 - t) * 1.5 + (-side) * t * 2.5
            w = 2.6 - t * 1.8
            for dx in np.arange(-w, w + 0.01, 0.5):
                cv.put(x + dx, 12 + k, FERRO, 5.4 - (dx + w) * 0.5 - t * 0.6, lit=0)
    cv.disc(9.5, 13, 1.6, 1.6, FERRO, 2.0, lit=0)                          # el clau del mig
    return cv.img


def _pila_img(nom):
    """Un munt de llenya vist de cara (44×52): les testes dels troncs, cadascuna de la seva mena."""
    w, h = 46, 54
    cv = Canvas(w, h, transparent=True)
    if nom == 'llenya_pi':            # clar, resinós: testes grogues amb anells i gotes de resina
        ramp, base, escorca = [(70, 46, 22), (120, 84, 40), (170, 128, 64), (206, 168, 96), (232, 204, 136),
                               (248, 228, 176)], 3.4, [(40, 26, 16), (70, 44, 26), (100, 66, 38)]
    elif nom == 'llenya_pollancre':   # blanc i lleuger
        ramp, base, escorca = [(110, 106, 96), (150, 146, 134), (190, 186, 172), (220, 218, 204), (240, 238, 228),
                               (252, 252, 246)], 3.6, [(80, 86, 80), (120, 126, 118), (160, 164, 154)]
    else:                             # alzina: fosca i densa, més prima
        ramp, base, escorca = [(30, 14, 12), (54, 26, 20), (82, 42, 30), (110, 60, 40), (140, 82, 54),
                               (166, 106, 70)], 3.0, [(14, 10, 10), (28, 20, 18), (44, 32, 26)]
    r = 6.5 if nom != 'llenya_alzina' else 5.2
    files = 4 if nom != 'llenya_alzina' else 5
    k = 0
    for fila in range(files):
        y = h - r - 1 - fila * (r * 1.75)
        n = int((w - 2) // (2 * r)) - (fila % 2)
        for i in range(n):
            x = 1 + r + (fila % 2) * r + i * 2 * r + (hr(k, fila, 3) - 0.5) * 2
            k += 1
            rr = r * (0.8 + hr(k, 5) * 0.35)
            cv.disc(x, y, rr, rr, escorca, lambda nx, ny: 1.4 - ny * 0.8, lit=0)
            cv.disc(x, y, rr - 1.2, rr - 1.2, ramp,
                    lambda nx, ny, k=k: base - ny * 0.6 - (0.9 if int(math.hypot(nx, ny) * 4) % 2 else 0) * 0.6, lit=0)
            if nom == 'llenya_pi' and hr(k, 9) < 0.5:
                cv.flat(x + 1, y - 1, (255, 214, 120))                        # una gota de resina
            if nom == 'llenya_alzina':
                cv.line(x - rr * 0.5, y, x + rr * 0.5, y + 1, ramp, 0.6, lit=0)  # les esquerdes radials
    return cv.img


def _roba_img(seed, w, h, ramp=LLI, negre=False):
    """Una peça de roba estesa (camisa, llençol): plecs verticals i la vora de baix ondulada."""
    cv = Canvas(w, h + 6, transparent=True)
    for x in range(w):
        baix = h - 2 + math.sin(x / 4 + seed) * 2 + (hr(x // 3, seed) - 0.5) * 2
        for y in range(int(baix)):
            plec = math.sin(x / (3.2 + seed % 3) + seed) * 0.8
            lvl = (3.6 if not negre else 2.6) + plec - (y / h) * 0.6 + (nz(x / 4, y / 7, seed) - 0.5) * 0.4
            if y < 2:
                lvl += 0.6
            cv.put(x, y, ramp, lvl, lit=0)
    return cv.img


def _habit_img(seed):
    """Un hàbit negre penjat (34×96): les espatlles, les mànigues, la caputxa al darrere; regalima."""
    w, h = 40, 98
    cv = Canvas(w, h, transparent=True)
    cx = w / 2
    for y in range(4, h):
        t = (y - 4) / (h - 4)
        half = 9 + t * 9 if y > 14 else 6 + (y - 4) * 0.4
        for x in range(int(cx - half), int(cx + half) + 1):
            nx = (x - cx) / half
            cv.put(x, y, NEGRE, 2.6 - abs(nx) * 0.8 + math.sin(x / 2.5 + seed) * 0.5, lit=0)
    for side in (-1, 1):                                       # les mànigues
        for k in range(36):
            x = cx + side * (12 + k * 0.18)
            y = 16 + k
            cv.rect(x - 3, y, x + 3, y, NEGRE, 2.0 + side * 0.3, lit=0)
    cv.rect(cx - 16, 3, cx + 16, 5, FUSTA, 3.6, lit=0)        # la penja
    return cv.img


# ─── L'escena ────────────────────────────────────────────────────────────────

def _terra_fn(s, t, P):
    x, z = P[0], P[2]
    fila = int((z + 600) // 38)
    off = (fila % 2) * 24
    peca = int((x + off + 600) // 48)
    lvl = 3.0 + (hr(peca & 255, fila & 255, 11) - 0.5) * 1.0 + (nz(x / 7, z / 7, 12) - 0.5) * 0.5
    if (z + 600) % 38 < 1.6 or (x + off + 600) % 48 < 1.6:
        lvl -= 1.3
    # la regueró per on va l'aigua, al mig, cap a la porta
    if abs(x - 300 - (z - 100) * 0.3) < 3 and z > 60:
        lvl -= 0.5
    # els bassals (molls, més foscos amb un reflex)
    if fbm(x / 40, z / 30, 13) > 0.6:
        lvl += 0.5 if nz(x / 3, z / 3, 14) > 0.7 else -0.5
    return lvl


def _sostre_fn(s, t, P):
    x, z = P[0], P[2]
    lvl = 1.8 + (nz(x / 30, z / 4, 15) - 0.5) * 0.5
    if (x + 600) % 70 < 12:
        lvl += 0.8 + (0.6 if (x + 600) % 70 < 3 else 0)
    return lvl


@functools.lru_cache(maxsize=None)
def _paret_esq():
    cv = Canvas(ZW + 300, HW)
    mur_pedra(cv, 0, 0, ZW + 300, HW, 3.0, 13)
    return cv.img


@functools.lru_cache(maxsize=None)
def _textures():
    return _paret_fons(), _paret_dreta()


def escena(cv, foc=False, bagul_obert=False, tina_negra=False, habits=False, tisores=False, robes=True,
           marca_tisores=False):
    fons, dreta = _textures()
    e = Escena(cv, CAM, _llums(foc), ambient=-0.1 if not foc else 0.2)
    e.quad('sostre', (-200, HW, -300), (XW, HW, -300), (XW, HW, ZW), (-200, HW, ZW), ramp=FUSTA, lvl=_sostre_fn,
           dues_cares=True)
    e.quad('paret_fons', (0, HW, ZW), (XW, HW, ZW), (XW, 0, ZW), (0, 0, ZW), tex=(fons, (0, 0, XW, HW)))
    e.quad('paret_dreta', (XW, HW, ZW), (XW, HW, -200), (XW, 0, -200), (XW, 0, ZW), tex=(dreta, (0, 0, ZW + 200, HW)))
    e.quad('paret_esq', (0, HW, -300), (0, HW, ZW), (0, 0, ZW), (0, 0, -300), tex=(_paret_esq(), (0, 0, ZW + 300, HW)))
    e.quad('terra', (0, 0, ZW), (XW, 0, ZW), (XW, 0, -300), (0, 0, -300), ramp=LLOSA, lvl=_terra_fn)
    # les bigues del sostre (fugen cap al fons)
    for x in range(40, XW, 70):
        e.caixa('sostre', x, x + 12, HW - 12, HW, -300, ZW, FUSTA, 1.6,
                cares={'sota': {'ramp': FUSTA, 'lvl': 2.2}, 'esquerra': {'ramp': FUSTA, 'lvl': 2.6},
                       'dreta': {'ramp': FUSTA, 'lvl': 1.4}})
    # els racons foscos
    e.foscor('ombra_fons', (0, 0.2, ZW), (XW, 0.2, ZW), (XW, 0.2, ZW - 24), (0, 0.2, ZW - 24),
             lambda s, t: 0.4 * (1 - t / 24))
    e.foscor('ombra_dreta', (XW - 20, 0.2, ZW), (XW, 0.2, ZW), (XW, 0.2, -200), (XW - 20, 0.2, -200),
             lambda s, t: 0.4 * (s / 20))
    # la claror de la porta pel terra (blava) i, amb el foc, el bassal taronja davant el fogó
    x0, x1, _ = PORTA
    e.claror((x0 - 6, 0.3, ZW), (x1 + 6, 0.3, ZW), (x1 - 20, 0.3, ZW - 120), (x0 - 50, 0.3, ZW - 120),
             (90, 110, 150), lambda s, t: 0.35 * (1 - t / 120))
    if foc:
        f0, f1 = FOGO[0], FOGO[1]
        e.claror((f0 - 120, 0.3, ZW - 40), (f1 + 100, 0.3, ZW - 40), (f1 + 100, 0.3, ZW - 300), (f0 - 120, 0.3, ZW - 300),
                 (255, 150, 60), lambda s, t: 0.42 * max(0.0, 1 - math.hypot((s - (f1 - f0 + 220) / 2) / 200, t / 230)))
    # la pila de llenya (tres munts, contra la paret del fons), amb les testes de cara
    for nom, (a0, a1) in MUNTS.items():
        img = _pila_img(nom)
        d = LLENYA[2]
        e.caixa(nom, a0, a1, 0, 50, ZW - d, ZW, FUSTA, 1.2,
                cares={'davant': {'tex': (img, (0, 0, img.width, img.height))},
                       'dalt': {'ramp': FUSTA, 'lvl': lambda s, t, P: 3.4 + math.sin(P[0] * 0.9) * 0.8 - (1.2 if nom == 'llenya_alzina' else 0)},
                       'dreta': {'ramp': FUSTA, 'lvl': lambda s, t, P: 2.0 + math.sin(P[1] * 0.9) * 0.8}})
    e.foscor('ombra_llenya', (LLENYA[0], 0.25, ZW - LLENYA[2]), (LLENYA[1] + 8, 0.25, ZW - LLENYA[2]),
             (LLENYA[1] + 8, 0.25, ZW - LLENYA[2] - 18), (LLENYA[0], 0.25, ZW - LLENYA[2] - 18),
             lambda s, t: 0.45 * (1 - t / 18))
    # el fogó: un banc de pedra amb la boca del foc, i la tina gran damunt
    f0, f1, fh, fd = FOGO

    def boca(s, t, P):
        x, y = P[0], P[1]
        cx = (f0 + f1) / 2
        if abs(x - cx) < 34 and y < 34 and (y < 22 or math.hypot(x - cx, y - 22) < 34 * 0.9 and abs(x - cx) < 30):
            return 0.2 if not foc else 1.6
        fila = int(y) // 12
        lvl = 3.6 + (hr(int(x + fila * 9) // 26 & 255, fila, 21) - 0.5) * 1.0 - (1.0 if int(y) % 12 == 0 else 0)
        return lvl - (1.2 * (y / fh) if abs(x - cx) < 50 else 0)            # el sutge de dalt
    e.caixa('fogo', f0, f1, 0, fh, ZW - fd, ZW, PEDRA, 3.4,
            cares={'davant': {'ramp': PEDRA, 'lvl': boca}, 'dalt': {'ramp': PEDRA, 'lvl': 3.6},
                   'esquerra': {'ramp': PEDRA, 'lvl': 2.8}})
    # la tina de coure: un cilindre de discs, amb la vora gruixuda
    tx, tz, tr, th = TINA
    _cilindre(e, 'tina', tx, tz, tr, fh, fh + th, COURE, 3.4)
    _disc_dalt(e, 'tina', tx, tz, tr + 2, fh + th, COURE, 5.0)
    for k in range(18):                                   # els reblons de la vora
        a = math.pi * 2 * k / 18
        e.sprite('tina', _reblo(), (0, 0), (tx + math.cos(a) * (tr + 0.5), fh + th - 4, tz + math.sin(a) * (tr + 0.5)))
    aigua = [(6, 8, 10), (12, 14, 18), (20, 22, 28), (34, 36, 42)] if tina_negra else \
        [(40, 50, 52), (64, 76, 76), (92, 104, 100), (124, 134, 126), (160, 168, 158)]
    _disc_dalt(e, 'tina', tx, tz, tr - 4, fh + th - 3, aigua, 2.4 if tina_negra else 2.6)
    # la perxa (al costat del fogó) amb, si de cas, els hàbits negres
    px_, pz0, pz1, ph = PERXA
    for z in (pz0, pz1):
        e.caixa('perxa', px_ - 2, px_ + 2, 0, ph, z - 2, z + 2, FUSTA, 2.6)
    e.tub('perxa', (px_, ph, pz0), (px_, ph, pz1), 1.8, FUSTA, 3.4)
    if habits:
        for k, z in enumerate((pz1 - 10, pz0 + 18)):
            e.sprite('habits', _habit_img(k * 3 + 1), (20, 3), (px_, ph + 2, z), escala_img=1.0)
    # les tines petites
    for k, (x, z, r) in enumerate(TINETES):
        _cilindre(e, 'tinetes', x, z, r, 0, r * 1.1, FUSTA, 3.0, cercols=True)
        _disc_dalt(e, 'tinetes', x, z, r, r * 1.1, FUSTA, 4.0)
        _disc_dalt(e, 'tinetes', x, z, r - 3, r * 1.1 - 2, [(30, 40, 44), (50, 62, 64), (80, 92, 90)], 1.6)
    # el bagul, girat, davant la paret de la dreta
    bx, bz, bw, bd, bh, bang = BAGUL
    e.foscor('ombra_bagul', (bx - 60, 0.2, bz + 40), (bx + 60, 0.2, bz + 40), (bx + 60, 0.2, bz - 50),
             (bx - 60, 0.2, bz - 50), lambda s, t: 0.5 * max(0.0, 1 - math.hypot((s - 56) / 56, (t - 46) / 40)))
    tapa = _bagul_tapa()
    e.caixa_girada('bagul', bx, bz, bw, bd, bh, bang, FUSTA, 2.6,
                   cares={'davant': {'tex': (_bagul_davant(), (0, 0, 84, 40))},
                          'dalt': ({'tex': (tapa, (0, 0, 84, 46))} if not bagul_obert else
                                   {'tex': (_bagul_dins(), (0, 0, 84, 46))}),
                          'esquerra': {'ramp': FUSTA, 'lvl': 2.0}, 'dreta': {'ramp': FUSTA, 'lvl': 2.0}})
    if bagul_obert:
        # la tapa, oberta cap enrere (dreta)
        c, s_ = math.cos(bang), math.sin(bang)

        def P(lx, y, lz):
            return (bx + lx * c - lz * s_, y, bz + lx * s_ + lz * c)
        a, b = bw / 2, bd / 2
        e.quad('bagul', P(-a, bh + bd * 0.95, b + 6), P(a, bh + bd * 0.95, b + 6), P(a, bh, b), P(-a, bh, b),
               tex=(tapa, (0, 0, 84, 46)), dues_cares=True)
    # la llàntia del mur de l'esquerra (encesa)
    lx, lz, ly = LLANTIA
    e.sprite('llantia', _llantia_img(), (2, 6), (lx + 1, ly, lz), escala_img=1.0)
    # les tisores (prop) al clau
    if tisores:
        tz, ty = TISORES
        e.sprite('tisores', _tisores_img(), (9.5, 2), (XW - 1.5, ty, tz), escala_img=1.0)
    if marca_tisores:
        tz, ty = TISORES
        e.claror((XW - 0.6, ty - 2, tz - 7), (XW - 0.6, ty - 2, tz + 7), (XW - 0.6, ty - 42, tz + 7),
                 (XW - 0.6, ty - 42, tz - 7), (150, 140, 120), lambda s, t: 0.25 if abs(s - 7) < 4 - t * 0.04 else 0)
    # el primer pla: la corda i les robes esteses
    if robes:
        A, B = CORDA
        e.cable('corda', [A, ((A[0] + B[0]) / 2, (A[1] + B[1]) / 2 - 8, (A[2] + B[2]) / 2), B], FUSTA, 2.6, gruix=1.2)
        for k, t in enumerate((0.10, 0.27, 0.70, 0.86)):
            P0 = (A[0] + (B[0] - A[0]) * t, A[1] + (B[1] - A[1]) * t - 8 * math.sin(t * math.pi),
                  A[2] + (B[2] - A[2]) * t)
            wimg = (46, 36, 34, 42)[k]
            himg = (64, 50, 46, 58)[k]
            img = _roba_img(k * 7 + 2, wimg, himg)
            # cada peça segueix la direcció de la corda (un quad dret, amb la textura)
            dx, dz = (B[0] - A[0]), (B[2] - A[2])
            L = math.hypot(dx, dz)
            ux, uz = dx / L, dz / L
            Q0 = P0
            Q1 = (P0[0] + ux * wimg, P0[1], P0[2] + uz * wimg)
            e.quad('robes', Q0, Q1, (Q1[0], Q1[1] - himg, Q1[2]), (Q0[0], Q0[1] - himg, Q0[2]),
                   tex=(img, (0, 0, wimg, himg)), dues_cares=True)
            for px in (Q0, Q1):
                e.sprite('robes', _pinca_img(), (1, 1), (px[0] + ux * 3 * (1 if px is Q0 else -1), px[1] + 2,
                                                       px[2] + uz * 3 * (1 if px is Q0 else -1)))
    return e


def _cilindre(e, sid, cx, cz, r, y0, y1, ramp, lvl, cercols=False):
    """Un cilindre dret (la tina, les tines petites): franges verticals de quads, amb la llum per cara."""
    n = 20
    for i in range(n):
        a0, a1 = math.pi * 2 * i / n, math.pi * 2 * (i + 1) / n
        P0 = (cx + math.cos(a0) * r, y1, cz + math.sin(a0) * r)
        P1 = (cx + math.cos(a1) * r, y1, cz + math.sin(a1) * r)
        am = (a0 + a1) / 2
        # (la llum ve de davant a l'esquerra: la cara que hi mira, més clara; la de la dreta, a l'ombra)
        sh = math.cos(am - math.radians(215)) * 1.8
        lv = lvl + sh
        if cercols:
            lv = (lambda s, t, P, l=lvl + sh: l + (0.0 if abs(P[1] - (y1 - y0) * 0.25 - y0) > 2 and
                                              abs(P[1] - (y1 - y0) * 0.75 - y0) > 2 else -1.4) - 0.6
                  * (1 if int(P[0] + P[2]) % 7 == 0 else 0))
        e.quad(sid, P1, P0, (P0[0], y0, P0[2]), (P1[0], y0, P1[2]), ramp=ramp, lvl=lv)


def _disc_dalt(e, sid, cx, cz, r, y, ramp, lvl):
    e.quad(sid, (cx - r, y, cz + r), (cx + r, y, cz + r), (cx + r, y, cz - r), (cx - r, y, cz - r), ramp=ramp,
           lvl=lambda s, t, P: (lvl(s, t, P) if callable(lvl) else lvl) - math.hypot(s - r, t - r) / r * 0.6,
           forma=lambda s, t: math.hypot(s - r, t - r) <= r, dues_cares=True)


def _bagul_davant():
    cv = Canvas(84, 40)
    for y in range(40):
        for x in range(84):
            cv.put(x, y, FUSTA, 3.0 + (nz(x / 2, y / 9, 31) - 0.5) * 0.8 - (1.0 if y % 10 == 0 else 0), lit=0)
    for x in (6, 76):
        cv.rect(x, 0, x + 3, 39, FERRO, 2.6, lit=0)
    cv.rect(38, 4, 46, 14, FERRO, 3.4, lit=0)                              # el pany
    cv.rect(41, 8, 43, 11, FERRO, 0.6, lit=0)
    return cv.img


def _bagul_tapa():
    cv = Canvas(84, 46)
    for y in range(46):
        for x in range(84):
            cv.put(x, y, FUSTA, 3.6 + (nz(x / 9, y / 2, 33) - 0.5) * 0.8 - (1.0 if x % 14 == 0 else 0), lit=0)
    for x in (6, 76):
        cv.rect(x, 0, x + 3, 45, FERRO, 3.0, lit=0)
    return cv.img


def _bagul_dins():
    """El bagul obert, vist de dalt: roba vella plegada (hàbits marrons i una pell), molt usada."""
    cv = Canvas(84, 46)
    cv.rect(0, 0, 83, 45, FUSTA, 1.2, lit=0)
    for k, (x0, y0, x1, y1, ramp, l) in enumerate(((4, 4, 44, 40, FANG, 3.0), (40, 6, 80, 26, NEGRE, 2.6),
                                                   (42, 24, 80, 42, LLI, 3.0))):
        for y in range(y0, y1):
            for x in range(x0, x1):
                cv.put(x, y, ramp, l + math.sin((x + y * 0.4) / 3 + k) * 0.6 - (0.6 if y == y1 - 1 else 0), lit=0)
    return cv.img


def _reblo():
    cv = Canvas(2, 2, transparent=True)
    cv.rect(0, 0, 1, 1, COURE, 1.4, lit=0)
    return cv.img


def _pinca_img():
    cv = Canvas(3, 6, transparent=True)
    cv.rect(0, 0, 2, 5, FUSTA, 4.6, lit=0)
    return cv.img


def _llantia_img():
    cv = Canvas(12, 14, transparent=True)
    cv.disc(5, 8, 5, 2.6, FANG, lambda nx, ny: 3.2 - ny, lit=0)
    cv.disc(9, 4, 1.5, 3, FOC, lambda nx, ny: 5.8 - ny * 1.2, lit=0)
    return cv.img


# ─── Fons, props, animacions ─────────────────────────────────────────────────

@functools.lru_cache(maxsize=None)
def _render(**k):
    cv = Canvas(W, H, light=LIGHT)
    e = escena(cv, **k)
    if k.get('foc'):
        _tenyeix(cv, (1.12, 0.92, 0.72))
    else:
        _tenyeix(cv, (0.86, 0.92, 1.08))
    _llum_llantia(cv)
    return fosc_hud(cv.img), e


def _tenyeix(cv, f):
    a = np.asarray(cv.img).astype(np.float32)
    a[..., :3] *= np.array(f, np.float32)
    cv.img.paste(Image.fromarray(a.clip(0, 255).astype(np.uint8), 'RGBA'))
    cv.P = cv.img.load()


def _llum_llantia(cv):
    lx, lz, ly = LLANTIA
    u, v, _ = CAM.projecta((lx + 8, ly, lz))
    a = np.asarray(cv.img).astype(np.float32)
    yy, xx = np.mgrid[0:H, 0:W]
    k = np.clip(1 - np.hypot((xx - u) / 90, (yy - v) / 110), 0, 1) ** 1.6 * 0.9
    a[..., :3] *= (1 + k[..., None] * np.array([0.6, 0.35, 0.1], np.float32))
    cv.img.paste(Image.fromarray(a.clip(0, 255).astype(np.uint8), 'RGBA'))
    cv.P = cv.img.load()


def _base():
    return _render()[0]


def bg(cv):
    cv.img.paste(_base())
    cv.P = cv.img.load()


@functools.lru_cache(maxsize=None)
def _robes_mask():
    return mascara_amo(_render()[1], {'robes', 'corda'})


def _decorat(**k):
    def draw(pc):
        d = diferencia(_render(**k)[0], _base())
        a = np.asarray(d).copy()
        a[_robes_mask().array] = 0                            # les robes són una capa a part
        pc.img.alpha_composite(sense_hud(Image.fromarray(a, 'RGBA')))
        pc.P = pc.img.load()
    return draw


PROPS = {
    'tisores': _decorat(tisores=True),
    'bagul_obert': _decorat(bagul_obert=True),
    'tina_negra': _decorat(tina_negra=True),
    'habits_estesos': _decorat(habits=True),
    'tisores_agafades': _decorat(marca_tisores=True),
}


def _vapor_frames(n, forca, seed, foc=False):
    """El vapor de la tina: bufs blanquinosos que pugen i s'escampen pel sostre (transparents)."""
    tx, tz, tr, th = TINA
    u0, v0, _ = CAM.projecta((tx, FOGO[2] + th, tz))
    s = CAM.escala((tx, 0, tz))
    yy, xx = np.mgrid[0:RH, 0:W].astype(np.float32)
    rob = _robes_mask().array[:RH]
    out = []
    for i in range(n):
        ph = i / n
        a = np.zeros((RH, W), np.float32)
        for b in range(9):
            t = (ph + b / 9) % 1.0
            cx = u0 + math.sin(t * 5 + b * 1.7 + seed) * 18 * s + (t * 60 * s if b % 2 else -t * 40 * s)
            cy = v0 - t * 80 * s
            r = (12 + t * 40) * s
            fade = smooth(0, 0.15, t) * (1 - smooth(0.6, 1.0, t))
            d = np.hypot((xx - cx) / r, (yy - cy) / (r * 0.7))
            a += np.clip(1 - d, 0, 1) ** 1.5 * fade
        a = np.clip(a * forca, 0, 0.6)
        img = np.zeros((H, W, 4), np.uint8)
        col = (230, 214, 196) if foc else (196, 206, 220)
        img[:RH, :, 0], img[:RH, :, 1], img[:RH, :, 2] = col
        alpha = (a * 255).astype(np.uint8)
        alpha[rob] = 0
        # (a quadres: dithering, perquè sigui pixel art)
        bay = np.tile(np.array([[0, 8, 2, 10], [12, 4, 14, 6], [3, 11, 1, 9], [15, 7, 13, 5]]) / 16, (RH // 4 + 1, W // 4))[:RH, :W]
        alpha = np.where(a > bay * 0.5, (np.clip(a, 0.15, 0.55) * 255).astype(np.uint8), 0)
        alpha[rob] = 0
        img[:RH, :, 3] = alpha
        out.append(Image.fromarray(img, 'RGBA'))
    return out


@functools.lru_cache(maxsize=None)
def _foc_frames():
    """El foc encès: el decorat sencer (tota la llum taronja) amb les flames de la boca del fogó i més vapor."""
    # La llum del foc: l'escena encesa tal com és, menys on hi ha els altres decorats (el bagul obert, la tina negra,
    # els hàbits, el clau buit): allà, un taronja translúcid, perquè continuïn veient-se a sota, il·luminats.
    base = np.asarray(_base()).astype(np.float32)[..., :3]
    lit = np.asarray(_render(foc=True)[0]).astype(np.float32)[..., :3]
    altres = np.zeros((H, W), bool)
    for k in ({'bagul_obert': True}, {'tina_negra': True}, {'habits': True}, {'marca_tisores': True}, {'tisores': True}):
        altres |= np.asarray(diferencia(_render(**k)[0], _base()))[..., 3] > 0
    C = np.array([255, 146, 60], np.float32)
    alfa = np.clip(((lit - base) * (C - base)).sum(-1) / np.maximum(1.0, ((C - base) ** 2).sum(-1)), 0, 0.5)
    d = np.zeros((H, W, 4), np.uint8)
    canvi = (lit != base).any(-1)
    d[canvi, :3] = lit[canvi].astype(np.uint8)
    d[canvi, 3] = 255
    d[altres, :3] = C.astype(np.uint8)
    d[altres, 3] = (alfa[altres] * 255).astype(np.uint8)
    d[_robes_mask().array] = 0
    d[RH:] = 0
    # (la boca del fogó i la tina, tal com són enceses: opaques)
    m = mascara_amo(_render(foc=True)[1], {'fogo'}).array
    d[m, :3] = lit[m].astype(np.uint8)
    d[m, 3] = 255
    f0, f1, fh, fd = FOGO
    cx = (f0 + f1) / 2
    vap = _vapor_frames(8, 1.0, 3, foc=True)
    out = []
    for i in range(8):
        fr = Canvas(W, H, transparent=True)
        fr.img.paste(Image.fromarray(d, 'RGBA'))
        fr.P = fr.img.load()
        # les flames: llengües que pugen i es mouen
        for k in range(9):
            x = cx - 26 + k * 6.5
            hgt = 16 + 10 * abs(math.sin(i * 0.9 + k * 1.3)) + hr(i, k, 3) * 6
            for j in range(int(hgt)):
                t = j / hgt
                wdt = (1 - t) * 3.2
                xx = x + math.sin(t * 4 + i + k) * 2.4 * t
                for dx in np.arange(-wdt, wdt + 0.01, 0.5):
                    P = (xx + dx, 3 + j * 0.9, ZW - fd - 0.5)
                    u, v, _ = CAM.projecta(P)
                    if 0 <= u < W and 0 <= v < RH:
                        fr.put(u, v, FOC, 6.2 - t * 4.4 - abs(dx) / max(0.5, wdt) * 1.2, lit=0)
        fr.img.alpha_composite(vap[i])
        out.append(fr.img)
    return out


ANIMS = {
    'vapor': {'frames': lambda: _vapor_frames(10, 0.55, 1), 'frameDuration': 160},
    'foc_ences': {'frames': lambda: list(_foc_frames()), 'frameDuration': 110},
}


# ─── Capes del davant: les robes, en franges ─────────────────────────────────

FRANJA = 16


def _corda_v(u):
    """La fila de pantalla del terra just sota la corda, a la columna u (la línia base de la franja)."""
    A, B = CORDA
    best = None
    for k in range(201):
        t = k / 200
        P = (A[0] + (B[0] - A[0]) * t, 0, A[2] + (B[2] - A[2]) * t)
        pu, pv, _ = CAM.projecta((P[0], A[1], P[2]))
        if best is None or abs(pu - u) < best[0]:
            best = (abs(pu - u), round(CAM.projecta(P)[1]))
    return best[1]


def _franja_mask(x0):
    def m(x, y):
        return x0 <= x < x0 + FRANJA and _robes_mask()(x, y)
    return m


# (només les franges on hi ha roba: la màscara és de l'escena, i es calcula en importar)
_ROBA_X = np.nonzero(mascara_amo(_render()[1], {'robes'}).array.any(axis=0))[0]
FRONT = [{'id': f'davant_robes_{x0 // FRANJA:02d}', 'mask': _franja_mask(x0), 'baseline': _corda_v(x0 + FRANJA / 2),
          'zIndex': 20}
         for x0 in range(0, W, FRANJA) if ((_ROBA_X >= x0) & (_ROBA_X < x0 + FRANJA)).any()]


# ─── Geometria ───────────────────────────────────────────────────────────────

def _p(x, z, y=0.0):
    u, v, _ = CAM.projecta((x, y, z))
    return round(u), round(v)


def _rect(*Ps):
    pts = [CAM.projecta(P) for P in Ps]
    return (max(0, round(min(p[0] for p in pts))), max(0, round(min(p[1] for p in pts))),
            min(W - 1, round(max(p[0] for p in pts))), min(RH - 1, round(max(p[1] for p in pts))))


def _girat(cx, cz, ang):
    c, s = math.cos(ang), math.sin(ang)
    return lambda lx, lz: (cx + lx * c - lz * s, cz + lx * s + lz * c)


def _sota(cx, cz, w, d, ang, marge=8):
    g = _girat(cx, cz, ang)
    return [_p(*g(lx, lz)) for lx, lz in ((-w / 2 - marge, -d / 2 - marge), (w / 2 + marge, -d / 2 - marge),
                                          (w / 2 + marge, d / 2 + marge), (-w / 2 - marge, d / 2 + marge))]


def _z_escala(k, x=220):
    lo, hi = -250.0, ZW
    for _ in range(50):
        z = (lo + hi) / 2
        if CAM.escala((x, 0, z)) > k:
            lo = z
        else:
            hi = z
    return (lo + hi) / 2


_VN = v_escala(CAM, 1.18)


def _a_v(x, v):
    """El punt de terra de la paret x (del món) que cau a la fila v de pantalla."""
    lo, hi = -400.0, ZW
    for _ in range(50):
        z = (lo + hi) / 2
        if CAM.projecta((x, 0, z))[1] > v:
            lo = z
        else:
            hi = z
    return _p(x, (lo + hi) / 2)


_WALK = [_p(12, ZW - LLENYA[2] - 14), _p(FOGO[0] - 6, ZW - LLENYA[2] - 14), _p(FOGO[0] - 6, ZW - FOGO[3] - 10),
         _p(FOGO[1] + 4, ZW - FOGO[3] - 10), _p(PORTA[0] - 6, ZW - 6), _p(PORTA[1] + 6, ZW - 6),
         _p(XW - 14, ZW - 20), _a_v(XW - 14, _VN), _a_v(12, _VN)]
_VS = [v for _, v in _WALK]

bx, bz, bw, bd, bh, bang = BAGUL
_bag = []
_g = _girat(bx, bz, bang)
for lx in (-bw / 2, bw / 2):
    for lz in (-bd / 2, bd / 2):
        X, Z = _g(lx, lz)
        _bag += [(X, 0, Z), (X, bh, Z)]

def _caixa_robes():
    """La caixa de les dues peces de roba de l'esquerra (les més grosses), en pantalla."""
    m = mascara_amo(_render()[1], {'robes'}).array[:RH, :W // 4]
    ys, xs = np.nonzero(m)
    return (int(xs.min()), int(ys.min()), int(xs.max()), int(ys.max()))


GEOMETRIA = {
    'things': {
        'bagul': {'rect': _rect(*_bag), 'walk': _p(bx - 66, bz - 10)},
        'tina': {'rect': _rect((TINA[0] - TINA[2], FOGO[2] + TINA[3] + 4, TINA[1] - TINA[2]),
                               (TINA[0] + TINA[2], FOGO[2], TINA[1] - TINA[2])), 'walk': _p(TINA[0] - 10, ZW - FOGO[3] - 24)},
        'fogo': {'rect': _rect((FOGO[0], FOGO[2], ZW - FOGO[3]), (FOGO[1], 0, ZW - FOGO[3])),
                 'walk': _p((FOGO[0] + FOGO[1]) / 2 - 20, ZW - FOGO[3] - 24)},
        **{nom: {'rect': _rect((a0, 52, ZW - LLENYA[2]), (a1, 0, ZW - LLENYA[2])),
                 'walk': _p((a0 + a1) / 2, ZW - LLENYA[2] - 26)} for nom, (a0, a1) in MUNTS.items()},
        'robes': {'rect': _caixa_robes(),
                  'walk': _p(220, 60)},
        'tisores': {'rect': _rect((XW, TISORES[1] + 4, TISORES[0] - 10), (XW, TISORES[1] - 44, TISORES[0] + 10)),
                    'walk': _p(XW - 40, TISORES[0] + 30)},
        'porta': {'rect': _rect((PORTA[0], PORTA[2], ZW), (PORTA[1], 0, ZW)), 'walk': _p((PORTA[0] + PORTA[1]) / 2, ZW - 14)},
    },
    'spawns': {'iri': _p((PORTA[0] + PORTA[1]) / 2, ZW - 40)},
    'walkable': _WALK,
    'forats': [_sota(bx, bz, bw, bd, bang, marge=6), _sota(PERXA[0], (PERXA[1] + PERXA[2]) / 2, 10, PERXA[2] - PERXA[1], 0, 4), _sota(TINETES[0][0], TINETES[0][1], 2 * TINETES[0][2],
                                                         2 * TINETES[0][2], 0, marge=4),
               _sota(TINETES[1][0], TINETES[1][1], 2 * TINETES[1][2], 2 * TINETES[1][2], 0, marge=4)],
    'floorSquash': 0.38,
    # La llum dominant: la finestra de la dreta (freda) i, amb el foc, el fogó del fons (l'ombra cap a davant).
    'characterShadow': {'enabled': True, 'color': '#141018', 'alpha': 0.42, 'squash': 0.38, 'core': 0.6,
                        'light': {'x': _p((FOGO[0] + FOGO[1]) / 2, ZW - 30)[0], 'y': _p((FOGO[0] + FOGO[1]) / 2, ZW - 30)[1],
                                  'stretch': 0.5, 'reach': 220}},
    'characterLights': {
        'ambient': '#6c7088',
        'lights': [
            {'x': _p(XW, 160, 112)[0], 'y': _p(XW, 160, 112)[1], 'radius': 260, 'color': '#9cb2e0', 'intensity': 0.35},
            {'x': _p(LLANTIA[0] + 10, LLANTIA[1], LLANTIA[2])[0], 'y': _p(LLANTIA[0] + 10, LLANTIA[1], LLANTIA[2])[1],
             'radius': 200, 'color': '#ffc070', 'intensity': 0.35},
            {'x': _p((FOGO[0] + FOGO[1]) / 2, ZW - 60, 30)[0], 'y': _p((FOGO[0] + FOGO[1]) / 2, ZW - 60, 30)[1],
             'radius': 360, 'color': '#ff9a48', 'intensity': 0.6, 'whenPropVisible': 'foc_ences'},
        ],
    },
    'regions': [{'id': 'perspectiva', 'active': True, 'scaleEnabled': True, 'scaleWalkSpeed': True,
                 'scaleTop': escala_v(CAM, min(_VS)), 'scaleBottom': escala_v(CAM, max(_VS)),
                 'points': [(0, min(_VS)), (W - 1, min(_VS)), (W - 1, max(_VS)), (0, max(_VS))]}],
}

ajusta_geometria(GEOMETRIA)
