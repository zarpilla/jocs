"""
Aigua Verne — `palau_servei` (P): els passadissos de servei del palau orbital. EN 3D (hd640/tres_d.py), a 1×.

L'altra cara del palau: gris, funcional, llum de fluorescent. La càmera, alta i girada cap a la cantonada de
l'esquerra, veu un tros de passadís en L:
  - a la paret de l'esquerra (el casc), en escorç, el cartell «SOMRIU. ET VEU.» i l'ull de bou a l'espai (ANIMS
    `estrelles`);
  - a la paret del fons, l'**ascensor de servei** (porta d'acer amb el lector de targetes vermell) i el
    **passaplats** amb les **safates** (sempre);
  - a la dreta, el passadís que gira i fuig cap al fons, fins al moll de càrrega, il·luminat;
  - a dalt, les **canonades** del palau (aigua «només per a piscines», vapor, aire), que fan la cantonada i
    travessen el passadís; la vàlvula vermella baixa cap a l'ascensor;
  - al mig, separat de tot i girat, el **carro** de flors de plàstic d'en Nil (s'hi passa per darrere), i a la
    dreta el carro de neteja de la Lia, amb la galleda i el pal de fregar;
  - primer pla: unes caixes de cartró a baix a l'esquerra i una canonada gruixuda que travessa per dalt, fosques.

Tot el detall ve dels passadissos plans de sempre (palau_servei_pla_comu.py), dibuixats de cara i projectats.

El món: x a la dreta (0 = la paret del casc), y amunt (0 = el terra), z cap al fons (300 = la paret del fons);
1 unitat = 1 píxel de sala a la distància on un personatge fa 100 px (escala 1).
"""
import functools
import math

import hd640  # noqa: F401  (abans de cap hd.rooms: posa la llibreria a 640×360)
from hd.pix import Canvas, Light, W, H, hr
from hd.rooms.exterior import fbm
from hd640.rooms import palau_servei_pla_comu as PL
from hd640.rooms.palau_comu import (GRIS, CROM, BLANC, BLAU, VERMELL, VERD, NEGRE, estrelles_frames)
from hd640.tres_d import Camera, Escena, Llum

YELLOW, PLAST = PL.YELLOW, PL.PLAST
BOTTOM = 259                                       # la sala acaba aquí (a sota, la barra de verbs)
ZW = 300                                           # la paret del fons
HW = 214                                           # el sostre
ELEV = (46, 186)                                   # l'ascensor (amb el marc i el lector): x0, x1 a la paret del fons
HATCH = (222, 338)                                 # el passaplats (amb el marc): x0, x1
OBERT = (392, 482, 162)                            # el passadís que gira: x0, x1 i l'alçada
PAS_ANG, PAS_L = 0.35, 640                         # el passadís: el gir (cap a la dreta) i la llargada
CARRO = (318, 188, 0.42)                           # el carro de flors: x, z del centre i el gir
CARRO_WD = (86, 34)
NETEJA = (548, 262)                                # el carro de neteja
POSTER_Z = (150, 204)                              # el cartell, a la paret del casc
ULL = (242, 136, 30)                               # l'ull de bou: z, y del centre i el radi
TUBS = ((196, 7, BLANC, 4.2), (180, 5, GRIS, 3.8), (169, 3.4, CROM, 3.6))   # y, radi, rampa, nivell
VALV_X = 204                                       # la vàlvula vermella i el tub que baixa cap a l'ascensor

CAM = Camera(pos=(290, 190, -190), yaw=-0.12, pitch=0.16, f=380, centre=(330, 72))

LIGHT = Light(ambient=0.0, vignette=None, floor_fade=None)
LLUMS = [Llum((150, 208, 170), 280, 1.9, power=1.3),       # els fluorescents
         Llum((450, 208, 170), 280, 1.9, power=1.3),
         Llum((280, 80, 300), 120, 0.9, power=1.6),        # la cuina, pel passaplats
         Llum((520, 120, 560), 420, 1.4, power=1.0),       # els llums del passadís
         Llum((640, 100, 880), 360, 2.4, power=1.0)]       # el moll de càrrega, al fons


# ─── Les textures: els passadissos plans de sempre ──────────────────────────

@functools.lru_cache(maxsize=None)
def _pla():
    """La paret plana de sempre amb l'ascensor, el passaplats (amb les safates), el cartell i els rètols."""
    cv = Canvas(light=PL.LIGHT)
    PL.paret(cv)
    PL.ascensor(cv)
    PL.passaplats(cv)
    PL.safates(cv)
    return cv.img


@functools.lru_cache(maxsize=None)
def _ull():
    """L'ull de bou pla (→ la imatge i les estrelles brillants, per l'animació)."""
    cv = Canvas(light=PL.LIGHT)
    cv.rect(540, 52, 604, 116, GRIS, 4.4)
    bright = PL.ull_de_bou(cv)
    return cv.img, tuple(bright)


@functools.lru_cache(maxsize=None)
def _carros():
    cv = Canvas(light=PL.LIGHT, transparent=True)
    PL.carro_flors(cv)
    PL.carro_neteja(cv)
    return cv.img


@functools.lru_cache(maxsize=None)
def _valvula():
    cv = Canvas(light=PL.LIGHT, transparent=True)
    PL.canonades(cv)
    return cv.img.crop((214, 58, 239, 82))


@functools.lru_cache(maxsize=None)
def _etiqueta(text, ramp_i):
    from hd640.rooms.palau_comu import lletres
    w = len(text) * 4 + 6
    cv = Canvas(w, 9, transparent=True)
    cv.rect(0, 0, w - 1, 8, (BLAU, VERMELL, VERD)[ramp_i], 2.4, lit=0)
    lletres(cv, text, 3, 2, (236, 240, 246))
    return cv.img


# ─── Les superfícies ────────────────────────────────────────────────────────

def _planxa(lvl0, pw=96, seed=3):
    """La paret gris del servei: planxes llises amb cargols, el para-xocs de goma i el sòcol, en coordenades del
    món (P[1] = l'alçada)."""
    def L(s, t, P):
        y = P[1]
        u = s % pw
        v = lvl0 + (fbm(s / 60, y / 50, seed) - 0.5) * 0.4 + (hr(int(s) // 3, int(y) // 3) - 0.5) * 0.15
        if 36 <= y < 42:
            return 3.4 + (1.6 if y >= 41 else -1.0 if y < 37 else 0)      # el para-xocs dels carros
        if y < 36:
            v -= 0.9                                                      # el sòcol, més fosc
        if y < 1.5:
            return 1.4
        if u < 1:
            v -= 1.6
        elif u < 2:
            v += 0.8
        if (u < 5 or u > pw - 5) and int(y) % 34 == 17 and (u % 9 < 1.5):
            v += 1.4                                                      # els cargols
        return v
    return L


def _terra(s, t, P):
    """Les rajoles de vinil grises, amb la línia groga a un pam de les parets i les marques de fregar."""
    x, z = P[0], P[2]
    v = 3.6 + (hr(int(x) // 4, int(z) // 4, 7) - 0.5) * 0.3 + (fbm(x / 90, z / 60, 4) - 0.5) * 0.6
    if x % 64 < 1.2 or z % 64 < 1.2:
        v -= 1.0
    for cx, cz in ((330, 120), (420, 150), (250, 220)):              # les marques de fregar (arcs)
        d = math.hypot((x - cx) / 1.0, (z - cz) * 2.4)
        if abs(d - 34) < 0.9 and z < cz:
            v += 0.7
    return v


def _linia_groga(e, P0, P1):
    """La línia groga de seguretat, a terra, entre dos punts (x, z)."""
    (x0, z0), (x1, z1) = P0, P1
    dx, dz = x1 - x0, z1 - z0
    n = math.hypot(dx, dz)
    nx, nz = -dz / n * 1.6, dx / n * 1.6
    e.quad('terra', (x0 - nx, 0.2, z0 - nz), (x1 - nx, 0.2, z1 - nz), (x1 + nx, 0.2, z1 + nz), (x0 + nx, 0.2, z0 + nz),
           ramp=YELLOW, lvl=3.2, dues_cares=True)


def escena(cv, tex):
    e = Escena(cv, CAM, LLUMS, ambient=0.0)
    zn = CAM.pos[2] + 40
    XR = W + 260
    ox0, ox1, oh = OBERT
    pla = tex['pla']
    # ── el passadís que gira i fuig cap al fons, en diagonal (es pinta primer: es veu pel forat de la paret) ──
    dx, dz = math.sin(PAS_ANG), math.cos(PAS_ANG)
    L = PAS_L

    def Q(x, y, k):                                                    # un punt del passadís: x a la boca, k endins
        return (x + dx * k, y, ZW + dz * k)
    fx0, fx1 = Q(ox0, 0, L), Q(ox1, 0, L)
    # el fons: la porta oberta del moll de càrrega, blanca de llum, amb unes caixes a contrallum
    e.quad('passadis', Q(ox0, oh, L), Q(ox1, oh, L), Q(ox1, 0, L), Q(ox0, 0, L), ramp=BLANC,
           lvl=lambda s, t, P: (7.4 if 22 < s < 74 and t > 34 else 3.0) - (3.4 if 26 < s < 44 and t > 118 else 0)
           - (3.4 if 58 < s < 70 and t > 132 else 0))
    e.quad('passadis', Q(ox0, oh, 0), Q(ox0, oh, L), Q(ox0, 0, L), Q(ox0, 0, 0), ramp=GRIS, lvl=_planxa(4.0, seed=8))
    e.quad('passadis', Q(ox1, oh, L), Q(ox1, oh, 0), Q(ox1, 0, 0), Q(ox1, 0, L), ramp=GRIS, lvl=_planxa(3.4, seed=9))
    e.quad('passadis', Q(ox0, oh, L), Q(ox1, oh, L), Q(ox1, oh, 0), Q(ox0, oh, 0), ramp=GRIS, dues_cares=True,
           lvl=lambda s, t, P: 2.6 - (1.0 if t % 64 < 2 else 0)
           + (4.6 if (L - t + 40) % 130 < 36 and abs(s - 45) < 6 else 0))     # els fluorescents del passadís
    e.quad('passadis', Q(ox0, 0, L), Q(ox1, 0, L), Q(ox1, 0, 0), Q(ox0, 0, 0), ramp=GRIS, lvl=_terra,
           dues_cares=True)
    e.claror(Q(ox0, 0.3, L), Q(ox1, 0.3, L), Q(ox1, 0.3, 0), Q(ox0, 0.3, 0), (236, 240, 236),
             lambda s, t: 0.55 * max(0.0, 1 - t / 420) ** 1.6 + 0.12)
    e.foscor('passadis', Q(ox0 + 0.5, oh, 0), Q(ox0 + 0.5, oh, L), Q(ox0 + 0.5, 0, L), Q(ox0 + 0.5, 0, 0),
             lambda s, t: 0.35 * max(0.0, 1 - s / 300))
    _linia_groga(e, Q(ox0 + 6, 0, 0)[::2], Q(ox0 + 6, 0, L - 40)[::2])
    # ── la paret del casc (x = 0), amb el cartell i l'ull de bou ──
    e.quad('paret_esq', (0, HW, zn), (0, HW, ZW), (0, 0, ZW), (0, 0, zn), ramp=GRIS, lvl=_planxa(4.0, seed=5))
    pz0, pz1 = POSTER_Z
    e.quad('cartell', (0.5, 136, pz0), (0.5, 136, pz1), (0.5, 76, pz1), (0.5, 76, pz0), tex=(pla, (17, 91, 73, 151)))
    uz, uy, ur = ULL
    e.quad('ull', (0.5, uy + ur, uz - ur), (0.5, uy + ur, uz + ur), (0.5, uy - ur, uz + ur), (0.5, uy - ur, uz - ur),
           tex=(tex['ull'], (550, 62, 594, 106)), forma=lambda s, t: (s - ur) ** 2 + (t - ur) ** 2 <= ur * ur)
    # ── la paret del fons (z = 300), amb el forat del passadís ──
    e.quad('paret_fons', (0, HW, ZW), (XR, HW, ZW), (XR, 0, ZW), (0, 0, ZW), ramp=GRIS, lvl=_planxa(4.2),
           forma=lambda s, t: not (ox0 < s < ox1 and t > HW - oh))
    for a, b in ((ox0 - 6, ox0), (ox1, ox1 + 6)):                              # el marc del forat
        e.caixa('paret_fons', a, b, 0, oh + 6, ZW - 4, ZW, GRIS, 4.6)
    e.caixa('paret_fons', ox0 - 6, ox1 + 6, oh, oh + 6, ZW - 4, ZW, GRIS, 5.0)
    ex0, ex1 = ELEV
    e.quad('ascensor', (ex0, 148, ZW - 0.5), (ex1, 148, ZW - 0.5), (ex1, 0, ZW - 0.5), (ex0, 0, ZW - 0.5),
           tex=(pla, (76, 78, 216, 226)))
    hx0, hx1 = HATCH
    e.quad('passaplats', (hx0, 120, ZW - 0.5), (hx1, 120, ZW - 0.5), (hx1, 36, ZW - 0.5), (hx0, 36, ZW - 0.5),
           tex=(pla, (254, 104, 370, 190)))
    e.quad('passaplats', (hx0 - 6, 37, ZW - 8), (hx1 + 6, 37, ZW - 8), (hx1 + 6, 37, ZW), (hx0 - 6, 37, ZW), ramp=CROM,
           lvl=5.6)                                                            # el taulell, que sobresurt
    e.quad('rotul', (hx0 - 12, 160, ZW - 0.5), (hx0 + 88, 160, ZW - 0.5), (hx0 + 88, 146, ZW - 0.5),
           (hx0 - 12, 146, ZW - 0.5), tex=(pla, (244, 66, 344, 80)))
    e.quad('rotul', (ox1 + 14, 128, ZW - 0.5), (ox1 + 90, 128, ZW - 0.5), (ox1 + 90, 116, ZW - 0.5),
           (ox1 + 14, 116, ZW - 0.5), tex=(pla, (372, 106, 448, 118)))
    # ── el terra ──
    e.quad('terra', (0, 0, ZW), (XR, 0, ZW), (XR, 0, zn), (0, 0, zn), ramp=GRIS, lvl=_terra)
    _linia_groga(e, (0, ZW - 8), (ox0 - 8, ZW - 8))
    _linia_groga(e, (ox1 + 8, ZW - 8), (XR, ZW - 8))
    _linia_groga(e, (8, ZW - 8), (8, zn))
    e.foscor('racons', (0, 0.5, ZW), (XR, 0.5, ZW), (XR, 0.5, zn), (0, 0.5, zn),
             lambda s, t: max(0.5 * max(0.0, 1 - t / 26), 0.45 * max(0.0, 1 - s / 22)))
    e.foscor('cantonada', (0, HW, ZW - 0.5), (40, HW, ZW - 0.5), (40, 0, ZW - 0.5), (0, 0, ZW - 0.5),
             lambda s, t: 0.45 * max(0.0, 1 - s / 40))
    e.foscor('davant', (0, 0.5, 150), (XR, 0.5, 150), (XR, 0.5, zn), (0, 0.5, zn),
             lambda s, t: 0.4 * min(1.0, t / 200) ** 1.4)                     # (lluny dels fluorescents)
    # la claror càlida de la cuina, pel passaplats, i la blanca del passadís, en diagonal pel terra
    e.claror((hx0 - 30, 0.4, ZW - 2), (hx1 + 50, 0.4, ZW - 2), (hx1 + 10, 0.4, ZW - 90), (hx0 - 60, 0.4, ZW - 90),
             (255, 214, 160), lambda s, t: 0.18 * max(0.0, 1 - t / 90) * max(0.0, math.sin(math.pi * s / 196)))
    e.claror((ox0 - 10, 0.4, ZW), (ox1 + 4, 0.4, ZW), (ox1 + 70, 0.4, ZW - 160), (ox0 - 40, 0.4, ZW - 160),
             (236, 244, 240), lambda s, t: 0.4 * max(0.0, 1 - t / 170) ** 1.2 * max(0.0, math.sin(math.pi * min(1.0, s / max(1.0, 92 + t * 0.5)))))
    # ── les canonades: per la paret del fons i la del casc, fent la cantonada, i travessant el forat ──
    for k, (y, r, ramp, lv) in enumerate(TUBS):
        zt = ZW - 10 - k * 6 + r
        xt = 10 + k * 6 + r
        e.tub('canonades', (xt, y, zn + 60), (xt, y, zt), r, ramp, lv - 0.4, brides=90)
        e.tub('canonades', (xt, y, zt), (XR, y, zt), r, ramp, lv, brides=120)
    for k, (txt, xx) in enumerate((('AIGUA - NOMÉS PISCINES', 70), ('VAPOR', 70), ('AIGUA - NOMÉS PISCINES', 520))):
        y, r, _, _ = TUBS[0 if k != 1 else 1]
        zt = ZW - 10 - (0 if k != 1 else 6) + r - r - 0.6
        im = _etiqueta(txt, 0 if k != 1 else 1)
        e.quad('canonades', (xx, y + 4.5, zt), (xx + im.width, y + 4.5, zt), (xx + im.width, y - 4.5, zt),
               (xx, y - 4.5, zt), tex=(im, (0, 0, im.width, im.height)))
    # la vàlvula vermella i el tub que baixa cap a l'ascensor
    e.tub('canonades', (VALV_X, TUBS[0][0], ZW - 8), (VALV_X, 152, ZW - 8), 4, BLANC, 4.0)
    e.sprite('canonades', tex['valvula'], (12, 12), (VALV_X, 166, ZW - 14))
    for x in range(70, XR, 130):                                               # els suports
        e.caixa('canonades', x, x + 3, TUBS[2][0] - 6, HW, ZW - 4, ZW, GRIS, 2.6)
    # ── el carro de flors d'en Nil, al mig, girat ──
    cx, cz, ang = CARRO
    cw, cd = CARRO_WD
    e.foscor('ombra', (cx - 60, 0.6, cz + 40), (cx + 50, 0.6, cz + 40), (cx + 50, 0.6, cz - 30), (cx - 60, 0.6, cz - 30),
             lambda s, t: 0.55 * max(0.0, 1 - ((s - 52) / 54) ** 2 - ((t - 34) / 30) ** 2) * 1.6)
    _carro_flors(e, tex, cx, cz, cw, cd, ang)
    # ── el carro de neteja de la Lia ──
    _carro_neteja(e, tex)
    # ── primer pla: caixes a baix a l'esquerra, i una canonada gruixuda que travessa per dalt ──
    cart = [(18, 12, 8), (40, 28, 16), (66, 48, 28), (96, 72, 42), (130, 100, 62)]

    def cinta(lv0):
        return lambda s, t, P: lv0 + (1.6 if abs(t - 20) < 2.5 or abs(s - 32) < 2.5 else 0) \
            + (fbm(s / 10, t / 10, 3) - 0.5) * 0.6
    e.caixa_girada('primer_pla', 22, 64, 64, 40, 46, 0.25, cart, 1.6,
                   cares={'dalt': {'ramp': cart, 'lvl': cinta(2.4)},
                          'davant': {'ramp': cart, 'lvl': lambda s, t, P: 1.8 + (1.4 if 10 < s < 30 and 8 < t < 18 else 0)}})
    e.caixa_girada('primer_pla', 40, 70, 40, 30, 30, -0.2, cart, 1.4, y0=46,
                   cares={'dalt': {'ramp': cart, 'lvl': cinta(2.6)}})
    e.tub('primer_pla', (452, -10, 64), (452, 260, 64), 11, GRIS, 1.6, brides=58, llum_dir=(-1.0, 0.2))
    e.tub('primer_pla', (440, 238, 64), (300, 238, 64), 6, GRIS, 1.4)
    return e


def _carro_flors(e, tex, cx, cz, cw, cd, ang):
    """El carro de flors: dos pisos de reixa verda, quatre pals, la nansa, les rodes; les galledes de flors i les
    capses d'«en Nil», dibuixades planes i posades dretes a sobre."""
    VERDC = [(10, 30, 14), (20, 60, 28), (40, 100, 50), (70, 150, 80), (120, 200, 120)]
    c, s_ = math.cos(ang), math.sin(ang)

    def P(lx, y, lz):
        return (cx + lx * c - lz * s_, y, cz + lx * s_ + lz * c)
    for lx in (-cw / 2 + 2, cw / 2 - 2):
        for lz in (-cd / 2 + 2, cd / 2 - 2):
            p = P(lx, 0, lz)
            e.cable('carro', [(p[0], 6, p[2]), (p[0], 56, p[2])], CROM, 4.6, gruix=1.6)
            e.cable('carro', [(p[0], 5, p[2]), (p[0], 0.5, p[2])], NEGRE, 1.2, gruix=4)  # la roda
    grid = {'ramp': VERDC, 'lvl': lambda s, t, P: 2.4 + (1.2 if (s % 6 < 1.4 or t % 6 < 1.4) else -0.6)}
    side = {'ramp': VERDC, 'lvl': 3.2}
    for y0 in (12, 50):
        e.caixa_girada('carro', cx, cz, cw, cd, 3, ang, VERDC, 3.0, y0=y0,
                       cares={'dalt': grid, 'davant': side, 'esquerra': side, 'dreta': side})
    # les capses d'en Nil, al pis de baix, i les galledes de flors, al de dalt (dretes, com el dibuix pla)
    cr = tex['carros']
    e.sprite('carro', cr.crop((420, 194, 478, 220)), (29, 25), P(-4, 15, 0))
    e.sprite('carro', cr.crop((420, 128, 506, 185)), (43, 56), P(-2, 53, 0))
    p = P(cw / 2 + 2, 56, 0)
    e.cable('carro', [P(cw / 2 - 2, 56, -cd / 2 + 4), P(cw / 2 + 8, 76, -cd / 2 + 4)], CROM, 5.0, gruix=1.4)
    e.cable('carro', [P(cw / 2 + 8, 76, -cd / 2 + 4), P(cw / 2 + 8, 76, cd / 2 - 4)], NEGRE, 2.0, gruix=2.4)


def _carro_neteja(e, tex):
    nx, nz = NETEJA
    cr = tex['carros']
    e.foscor('ombra', (nx - 50, 0.6, nz + 30), (nx + 80, 0.6, nz + 30), (nx + 80, 0.6, nz - 30), (nx - 50, 0.6, nz - 30),
             lambda s, t: 0.5 * max(0.0, 1 - ((s - 60) / 64) ** 2 - ((t - 30) / 28) ** 2) * 1.6)
    # el carro de les tovalloles (contra la paret) i la galleda groga amb l'escorredor, girada
    e.caixa_girada('neteja', nx + 50, nz + 6, 44, 30, 50, -0.15, GRIS, 3.0,
                   cares={'davant': {'tex': (cr, (578, 176, 625, 230))}, 'dalt': {'ramp': NEGRE, 'lvl': 2.4}})
    e.caixa_girada('neteja', nx, nz - 8, 38, 24, 22, 0.35, YELLOW, 3.0,
                   cares={'dalt': {'ramp': [(20, 50, 70), (40, 90, 110), (90, 150, 160)],
                                   'lvl': lambda s, t, P: 1.4 if 3 < s < 35 and 3 < t < 21 else 9}})
    e.caixa_girada('neteja', nx + 4, nz - 4, 16, 12, 10, 0.35, GRIS, 3.4, y0=22)
    # el pal de fregar, recolzat a la paret
    e.cable('neteja', [(nx - 6, 18, nz - 12), (nx + 4, 140, ZW - 3)], CROM, 4.6, gruix=1.6)
    e.cable('neteja', [(nx + 4, 140, ZW - 3), (nx + 5, 148, ZW - 2)], BLAU, 2.6, gruix=2.2)


# ─── Composició ────────────────────────────────────────────────────────────

@functools.lru_cache(maxsize=None)
def _textures():
    return {'pla': _pla(), 'ull': _ull()[0], 'carros': _carros(), 'valvula': _valvula()}


@functools.lru_cache(maxsize=None)
def _base():
    cv = Canvas(light=LIGHT)
    e = escena(cv, _textures())
    cv.rect(0, BOTTOM + 1, W - 1, H - 1, [(0, 0, 0)], 0, lit=0)    # la barra de verbs: negre
    return cv.img, e


def bg(cv):
    img, _ = _base()
    cv.img.paste(img)
    cv.P = cv.img.load()


def safates(cv):
    """Les safates (ja són al fons, al passaplats: el decorat, si algun dia cal, és el mateix tros projectat)."""
    _, e = _base()
    sf = Canvas(light=PL.LIGHT, transparent=True)
    PL.safates(sf)
    cv.img.alpha_composite(e.capa(sf.img, {'passaplats'}))


PROPS = {'safates': safates}


def _frames_estrelles():
    _, e = _base()
    img, bright = _ull()
    return [e.capa(f, {'ull'}) for f in estrelles_frames(img, list(bright), n=10, seed=9)]


ANIMS = {'estrelles': {'frames': _frames_estrelles, 'frameDuration': 300}}


def _amo(ids):
    def mask(x, y):
        _, e = _base()
        return e.ids[e.amo[y * e.cv.w + x]] in ids
    return mask


# ─── Geometria (coordenades de sala, projectades) ────────────────────────────

def _p(x, z, y=0.0):
    u, v, _ = CAM.projecta((x, y, z))
    return round(u), round(v)


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


V_DAVANT = 244                                     # la vora de davant del terra on es camina (escala ≈1,2)


def _zf(x, v=V_DAVANT):
    lo, hi = -100.0, 2000.0
    for _ in range(60):
        z = (lo + hi) / 2
        if CAM.projecta((x, 0, z))[1] > v:
            lo = z
        else:
            hi = z
    return round((lo + hi) / 2)


def _vpeu(x, z):
    return CAM.projecta((x, 0, z))[1]


def _forat_carro(m=8):
    cx, cz, ang = CARRO
    cw, cd = CARRO_WD
    c, s_ = math.cos(ang), math.sin(ang)
    a, b = cw / 2 + m, cd / 2 + m
    return [_p(cx + lx * c - lz * s_, cz + lx * s_ + lz * c) for lx, lz in ((-a, -b), (a, -b), (a, b), (-a, b))]


# El terra on es camina (al món): el tros de passadís davant l'ascensor i el passaplats, una mica del passadís que
# gira (cap al fons), i fins al carro de neteja; el carro de flors és un forat (s'hi pot fer la volta).
OX0, OX1, _ = OBERT
WALK_MON = [(16, _zf(16)), (16, 284), (OX0 + 4, 284), (OX0 + 8 + 120 * math.sin(PAS_ANG), 300 + 120 * math.cos(PAS_ANG)),
            (OX1 - 10 + 120 * math.sin(PAS_ANG), 300 + 120 * math.cos(PAS_ANG)), (OX1 - 8, 290),
            (NETEJA[0] - 34, 284), (NETEJA[0] - 40, 236), (640, 230), (640, _zf(640)), (300, _zf(300))]
_WALK = [_p(x, z) for x, z in WALK_MON]
_V_FONS, _V_PROP = min(v for _, v in _WALK), max(v for _, v in _WALK)

FRONT = [
    {'id': 'davant_carro', 'mask': _amo({'carro'}), 'baseline': round(max(v for _, v in _forat_carro(0))) - 4,
     'zIndex': 20},
    {'id': 'davant_neteja', 'mask': _amo({'neteja'}), 'baseline': round(_vpeu(NETEJA[0], NETEJA[1] - 22)),
     'zIndex': 20},
    {'id': 'davant', 'mask': _amo({'primer_pla'}), 'baseline': 999, 'zIndex': 20},
]

GEOMETRIA = {
    'things': {
        'ascensor': {'rect': _rect_mon((ELEV[0], 148, ZW), (ELEV[1], 0, ZW)), 'walk': _p(110, 280)},
        'safates': {'rect': _rect_mon((HATCH[0], 70, ZW - 8), (HATCH[1], 34, ZW - 8)), 'walk': _p(280, 276)},
        'carro': {'rect': _rect_mon(*[(x, y, z) for (x, z) in
                                      [(CARRO[0] + dx, CARRO[1] + dz) for dx in (-44, 44) for dz in (-30, 30)]
                                      for y in (0, 100)]),
                  'walk': _p(CARRO[0] - 10, CARRO[1] - 56)},
        'canonades': {'rect': _rect_mon((60, TUBS[0][0] + 8, ZW - 8), (600, TUBS[2][0] - 4, ZW - 8)),
                      'walk': _p(240, 250)},
    },
    'spawns': {'vet': _p(200, 200), 'lia': _p(NETEJA[0] - 44, NETEJA[1] - 14), 'nil': _p(CARRO[0] + 62, CARRO[1] - 6)},
    'walkable': _WALK,
    'forats': [_forat_carro()],
    'floorSquash': 0.45,
    'characterShadow': {'enabled': True, 'color': '#101216', 'alpha': 0.42, 'squash': 0.45, 'core': 0.6,
                        'light': {'x': _p(300, 190)[0], 'y': _p(300, 190)[1], 'stretch': 0.6, 'reach': 140}},
    'regions': [{'id': 'perspectiva', 'active': True, 'scaleEnabled': True, 'scaleWalkSpeed': True,
                 'scaleTop': round(_escala_a(_V_FONS - 2), 3), 'scaleBottom': round(_escala_a(_V_PROP + 2), 3),
                 'points': [(0, _V_FONS - 2), (W - 1, _V_FONS - 2), (W - 1, _V_PROP + 2), (0, _V_PROP + 2)]}],
}
