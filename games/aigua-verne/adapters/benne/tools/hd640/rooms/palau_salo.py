"""
Aigua Verne — `palau_salo` (L: persones de ≈83 px): el saló de la Gran Subhasta de l'Aigua, al palau orbital.
EN 3D (hd640/tres_d.py), a 1×.

Una càmera alta, al fons de la sala a la dreta (darrere el públic), que mira de biaix cap a la cantonada de l'escenari:
la paret de la porta de la galeria fuig cap al fons a l'esquerra, i la del fons, amb la **pantalla** gegant entre
cortines de vellut granat i els dos finestrals a l'espai, travessa el quadre. Davant, l'**escenari** de marbre (un
volum, amb els graons del mig i el faristol amb el **martell**, a la dreta); les files de cadires daurades amb els
inversors asseguts, d'esquena, que s'empetiteixen cap a l'escenari; la catifa granat del passadís del mig, que porta
l'ull a la pantalla; a la dreta, la taula del **cava**, girada, amb les estovalles, la piràmide de copes, la glaçonera i
la **safata** d'argent a la punta. Primer pla: un pilar en ombra i el vellut d'una cortina, tallats per la vora de
l'esquerra. Es passa per darrere de les files de cadires, de la taula del cava i del faristol.

El detall ve del dibuix pla (palau_salo_pla_comu.py): la paret del fons sencera (com abans, de cara), les cadires amb
els inversors, les copes i la safata. PROPS: `grafic_112`, `grafic_84`, `grafic_52`, `grafic_31`, `grafic_29` (el gràfic
del preu, dibuixat pla i projectat per la pantalla). ANIMS: `estrelles`.

El món: x a la dreta (0 = la paret de la porta), y amunt (0 = el terra), z cap al fons (520 = la paret de la pantalla);
1 unitat = 1 píxel de sala a la distància on un personatge fa ≈83 px. La paret del fons és el dibuix pla de sempre
(x 60..580, y 12..150) a 1,5 unitats per píxel.
"""
import functools
import math

import hd640  # noqa: F401  (abans de cap hd.rooms: posa la llibreria a 640×360)
from hd.pix import Canvas, Light, W, hr
from hd.rooms.comu import _diff
from hd640.rooms import palau_salo_pla_comu as PL
from hd640.rooms import palau_galeria_pla_comu as GP
from hd640.rooms.palau_comu import MARB, ORP, GRANAT, RH
from hd640.tres_d import Camera, Escena, Llum

PERSONA = 83
BOTTOM = RH - 1
KP = 1.5                                           # unitats del món per píxel del dibuix pla de la paret del fons
PX0, PY0, PX1, PY1 = 60, 12, 580, 150              # el tros del dibuix pla que fa de paret del fons
XR, ZW = round((PX1 - PX0) * KP), 520              # la paret de la dreta (no es veu) i la del fons
YP = round((PY1 - PY0) * KP)                       # fins on arriba el dibuix pla de la paret del fons
YC = 300                                           # el sostre
ZN = -300
XM = round((320 - PX0) * KP)                       # el mig de la pantalla (i del passadís)
# l'escenari: x0, x1, el davant (z) i l'alçada (la de les cortines al dibuix pla)
ST = (round((168 - PX0) * KP), round((472 - PX0) * KP), 430, round((PY1 - PL.STAGE_Y) * KP))
GRAONS = (XM - 48, XM + 48, 3, 12)                 # els graons del mig: x0, x1, quants i la petja
FARISTOL = (566, 468)                              # el faristol (x, z), damunt l'escenari
FILES = (238, 278, 318, 358)                       # les files de cadires (z)
BLOCS = ((92, XM - 52), (XM + 52, 636))            # els dos blocs de cadires (x0, x1), a banda i banda del passadís
PAS = 32                                           # d'una cadira a l'altra
CATIFA = (XM - 36, XM + 36)
TAULA = (708, 214, -0.62, 124, 44, 38)             # la taula del cava: centre (x, z), gir, llarg, ample, alt
PORTA = (536, 616, 112)                            # la porta de la galeria, al dibuix de la paret de l'esquerra
ARANYES = ((XM - 120, 176, 150), (690, 186, 250))
PILAR = (204, 12)                                   # el pilar del primer pla (x, z)

CAM = Camera(pos=(600, 236, -230), yaw=-0.32, pitch=0.18, f=420, centre=(320, 78))

LIGHT = Light(ambient=0.0, vignette=None, floor_fade=None)    # (la llum és la del món: la de l'Escena)
LLUMS = [Llum((x, y - 10, z), 380, 1.3, power=1.3) for x, y, z in ARANYES] + [
    Llum((XM, 110, ZW - 30), 300, 1.1, power=1.4),               # la pantalla
    Llum((TAULA[0], 120, TAULA[1]), 160, 1.0, power=1.6),        # el llum de la taula del cava
]
AMBIENT = -0.7


# ─── Les textures ───────────────────────────────────────────────────────────

@functools.lru_cache(maxsize=None)
def _tex():
    fons, bright = PL.paret_fons_pla()
    esq = Canvas(GP.ESQ_W, YC, light=GP.LLUM_PLA)
    GP.paret_esq(esq, porta=PORTA, retol='GALERIA', amplada=GP.ESQ_W, alcada=YC)
    return {'fons': fons, 'bright': bright, 'esq': esq.img}


_VT = GP.venes(XR + 2, ZW - ZN + 2, 27)
_NT = GP.soroll(XR + 2, ZW - ZN + 2, 40, 28)


def _marbre(base, tile=52, seed=5):
    def L(x, z):
        iu, iv = math.floor(x / tile), math.floor(z / tile)
        ax, az = x - iu * tile, z - iv * tile
        if ax < 1.3 or az < 1.3:
            return base - 1.4
        zi = min(ZW - ZN + 1, max(0, int(z - ZN)))
        xi = min(XR + 1, max(0, int(x)))
        return (base + (hr(iu, iv, seed) - 0.5) * 0.6 - float(_VT[zi, (xi + seed * 131) % (XR + 2)]) * 1.8
                + (float(_NT[zi, xi]) - 0.5) * 0.5)
    return L


def _es_or(x, z, tile):
    iu, iv = math.floor(x / tile), math.floor(z / tile)
    return (iu % 2 == 0 and x - iu * tile < 1.3) or (iv % 2 == 0 and z - iv * tile < 1.3)


_TERRA = _marbre(6.0)


def _sostre(s, t, P):
    a, b = P[0] % 80, P[2] % 80
    if a < 3 or b < 3:
        return 3.4 if (a < 1.2 or b < 1.2) else 5.6
    return 5.2 if 12 < a < 68 and 12 < b < 68 else 4.4


@functools.lru_cache(maxsize=None)
def _cadires():
    """[(fila, x, z, ocupada, seed)]: les cadires de les quatre files (a la primera, gairebé totes ocupades)."""
    out = []
    for r, z in enumerate(FILES):
        for b, (x0, x1) in enumerate(BLOCS):
            x = x0 + (r % 2) * 6
            i = 0
            while x <= x1:
                seed = r * 50 + b * 20 + i
                out.append((r, x, z, hr(seed, 7) > (0.15 if r < 2 else 0.4), seed))
                x += PAS
                i += 1
    return out


# ─── L'escena ───────────────────────────────────────────────────────────────

def escena(cv):
    T = _tex()
    e = Escena(cv, CAM, LLUMS, ambient=AMBIENT)
    e.quad('sostre', (0, YC, ZN), (XR, YC, ZN), (XR, YC, ZW), (0, YC, ZW), ramp=MARB, lvl=_sostre, dues_cares=True)
    e.quad('paret_fons', (0, YP, ZW), (XR, YP, ZW), (XR, 0, ZW), (0, 0, ZW), tex=(T['fons'], (PX0, PY0, PX1, PY1), 1))
    e.quad('paret_fons_dalt', (0, YC, ZW), (XR, YC, ZW), (XR, YP, ZW), (0, YP, ZW), ramp=MARB,
           lvl=lambda s, t, P: 5.0 + (1.4 if YC - t - YP < 3 else 0) - (1.4 if 8 < t < 12 else 0)
           + (0.8 if 20 < t < YC - YP - 12 and s % 60 < 50 and s % 60 > 6 else 0))
    e.quad('paret_esq', (0, YC, ZN), (0, YC, ZW), (0, 0, ZW), (0, 0, ZN), tex=(T['esq'], (0, 0, GP.ESQ_W, YC), 1))
    e.quad('paret_dreta', (XR, YC, ZW), (XR, YC, ZN), (XR, 0, ZN), (XR, 0, ZW), ramp=MARB, lvl=4.4)
    # el terra de marbre, amb els filets d'or, i la catifa granat del passadís
    e.quad('terra', (0, 0, ZW), (XR, 0, ZW), (XR, 0, ZN), (0, 0, ZN), ramp=MARB, lvl=lambda s, t, P: _TERRA(P[0], P[2]))
    e.quad('terra', (0, 0.1, ZW), (XR, 0.1, ZW), (XR, 0.1, ZN), (0, 0.1, ZN), ramp=ORP, lvl=4.6,
           forma=lambda s, t: _es_or(s, ZW - t, 52) and not CATIFA[0] - 2 < s < CATIFA[1] + 2)
    c0, c1 = CATIFA
    e.quad('catifa', (c0, 0.3, ST[2]), (c1, 0.3, ST[2]), (c1, 0.3, ZN), (c0, 0.3, ZN), ramp=GRANAT,
           lvl=lambda s, t, P: 3.2 + (hr(int(P[0] / 3), int(P[2] / 3), 8) - 0.5) * 0.6 - (0.8 if t % 40 < 1.5 else 0))
    for a in (c0, c1 - 4):
        e.quad('catifa', (a, 0.4, ST[2]), (a + 4, 0.4, ST[2]), (a + 4, 0.4, ZN), (a, 0.4, ZN), ramp=ORP, lvl=4.6)
    # la foscor dels racons
    e.foscor('racons', (0.5, 0.5, ZW), (160, 0.5, ZW), (160, 0.5, ZN), (0.5, 0.5, ZN),
             lambda s, t: 0.55 * max(0.0, 1 - s / 70) ** 1.4)
    # l'escenari: el volum de marbre, amb els plafons d'or al davant, i els graons del mig
    x0, x1, zs, hs = ST
    e.foscor('ombra_escenari', (x0 - 10, 0.6, zs), (x1 + 10, 0.6, zs), (x1 + 10, 0.6, zs - 30), (x0 - 10, 0.6, zs - 30),
             lambda s, t: 0.5 * max(0.0, 1 - t / 30))
    e.caixa('escenari', x0, x1, 0, hs, zs, ZW, MARB, 5.0, cares={
        'dalt': {'ramp': MARB, 'lvl': lambda s, t, P: _marbre(6.8, 44, 11)(P[0], P[2])},
        'davant': {'ramp': MARB, 'lvl': lambda s, t, P: 4.8 - t * 0.04 + (1.6 if t < 2 else 0)
                   + (1.0 if (s % 80 < 1.5 or s % 80 > 78.5) and 5 < t < hs - 4 else 0)},
        'dreta': {'ramp': MARB, 'lvl': 3.8}})
    e.quad('escenari', (x0, hs - 2, zs - 0.4), (x1, hs - 2, zs - 0.4), (x1, hs - 5, zs - 0.4), (x0, hs - 5, zs - 0.4),
           ramp=ORP, lvl=4.8)
    g0, g1, ng, gp = GRAONS
    for k in range(ng):                                            # de lluny (el de dalt) a prop
        z0 = zs - gp * (k + 1)
        e.caixa('escenari', g0 - k * 6, g1 + k * 6, 0, hs * (ng - k) / (ng + 1), z0, zs - gp * k, MARB, 5.6, cares={
            'dalt': {'ramp': MARB, 'lvl': 7.2}, 'davant': {'ramp': MARB, 'lvl': 4.8}})
    # el faristol, damunt l'escenari, amb el martell
    fx, fz = FARISTOL
    e.caixa_girada('faristol', fx, fz, 34, 20, 44, -0.2, MARB, 5.6, y0=hs, cares={
        'davant': {'ramp': MARB, 'lvl': lambda s, t, P: 6.0 - t * 0.02 + (2.0 if abs(s - 17) < 5 and 12 < t < 24 else 0)
                   - (1.4 if s < 2 or s > 32 or t < 2 else 0)},
        'dalt': {'ramp': ORP, 'lvl': 5.0}})
    e.caixa_girada('faristol', fx, fz, 40, 24, 4, -0.2, ORP, 4.4, y0=hs + 44)
    img, peu = PL.martell_img()
    e.sprite('faristol', img, peu, (fx + 8, hs + 48, fz))
    # les files de cadires, de lluny a prop (amb la seva ombra)
    for r in range(len(FILES) - 1, -1, -1):
        z = FILES[r]
        for b0, b1 in BLOCS:
            e.foscor(f'ombra_fila{r}', (b0 - 14, 0.6, z + 10), (b1 + 18, 0.6, z + 10), (b1 + 18, 0.6, z - 14),
                     (b0 - 14, 0.6, z - 14), lambda s, t: 0.4 * max(0.0, 1 - abs(t - 12) / 12))
        for rr, x, zz, ocu, seed in _cadires():
            if rr == r:
                img, peu = PL.cadira_img(seed, ocu)
                e.sprite(f'fila{r}', img, peu, (x, 0, zz), escala_img=1.15)
    # els llums d'aranya
    img, peu = GP.aranya_img()
    for x, y, z in ARANYES:
        e.cable('aranya', [(x, YC, z), (x, y, z)], ORP, 4.0, gruix=1.4)
        e.sprite('aranya', img, peu, (x, y, z))
    # la taula del cava: les estovalles fins a terra, la garlanda d'or, les copes i la safata
    tx, tz, ta, tl, tw, th = TAULA
    e.foscor('ombra_taula', (tx - 90, 0.6, tz + 50), (tx + 90, 0.6, tz + 50), (tx + 90, 0.6, tz - 60),
             (tx - 90, 0.6, tz - 60),
             lambda s, t: 0.6 * max(0.0, 1 - ((s - 90) / 84) ** 2 - ((t - 50) / 46) ** 2) * 1.4)

    def garlanda(s, t):
        return 4 < t < 8 and (s % 10) < 7 and abs((t - 4) - 3 * math.sin((s % 10) / 10 * math.pi)) < 1.2

    def plecs(base):
        return lambda s, t, P: (base + math.sin(s * 0.42) * min(1.0, t / th) * 1.0 + (1.6 if garlanda(s, t) else 0)
                                - (1.0 if t < 1.5 else 0))
    e.caixa_girada('taula', tx, tz, tl, tw, th, ta, MARB, 6.6, cares={
        'davant': {'ramp': MARB, 'lvl': plecs(6.4)}, 'dreta': {'ramp': MARB, 'lvl': plecs(5.0)},
        'esquerra': {'ramp': MARB, 'lvl': plecs(5.4)}, 'dalt': {'ramp': MARB, 'lvl': 7.6}})
    c, s_ = math.cos(ta), math.sin(ta)

    def Gt(lx, lz):
        return (tx + lx * c - lz * s_, th, tz + lx * s_ + lz * c)
    img, peu = PL.copes_img()
    e.sprite('taula', img, peu, Gt(26, 4), escala_img=1.2)
    img, peu = PL.safata_img()
    e.sprite('safata', img, peu, Gt(-46, -6), escala_img=1.3)
    # primer pla: un pilar en ombra a l'esquerra, i el vellut d'una cortina recollida, tallats per la vora
    px_, pz = PILAR

    def estries(base):
        return lambda s, t, P: base + (0.9 if s % 9 < 2 else -0.5 if s % 9 > 7 else 0)
    e.caixa('primer_pla', px_ - 20, px_ + 20, 0, YC, pz - 20, pz + 20, MARB, 0.6, cares={
        'dreta': {'ramp': MARB, 'lvl': estries(1.6)}, 'davant': {'ramp': MARB, 'lvl': estries(0.4)}})
    # la cortina: penja del sostre, recollida cap al pilar (els plecs, verticals i més foscos a baix)
    e.quad('primer_pla', (px_ + 20, YC, pz - 21), (px_ + 120, YC, pz - 21), (px_ + 66, 90, pz - 21),
           (px_ + 20, 50, pz - 21), ramp=GRANAT,
           lvl=lambda s, t, P: 2.2 + math.sin((P[0] - px_) * 0.45 - t * 0.012) * 1.1 - t * 0.006, dues_cares=True)
    e.tub('primer_pla', (px_ + 18, 100, pz - 24), (px_ + 70, 106, pz - 24), 3, ORP, 3.4)   # el cordó d'or
    e.foscor('ombra_prop', (0, 0.7, 70), (XR, 0.7, 70), (XR, 0.7, -60), (0, 0.7, -60),
             lambda s, t: 0.55 * min(1.0, t / 110) ** 1.2)
    return e


# ─── Composició ─────────────────────────────────────────────────────────────

@functools.lru_cache(maxsize=None)
def _base():
    cv = Canvas(light=LIGHT)
    e = escena(cv)
    cv.rect(0, BOTTOM + 1, W - 1, cv.h - 1, [(0, 0, 0)], 0, lit=0)
    return cv.img, e


def bg(cv):
    img, _ = _base()
    cv.img.paste(img)
    cv.P = cv.img.load()


def _grafic(n):
    def fn(cv):
        _, e = _base()
        fons = _tex()['fons']
        tmp = Canvas(light=PL.LLUM_PLA, img=fons.copy())
        PL.grafic(tmp, n)
        cv.img.alpha_composite(e.capa(_diff(tmp.img, fons), {'paret_fons'}))
    return fn


PROPS = {f'grafic_{n}': _grafic(n) for n in (112, 84, 52, 31, 29)}


def _frames_estrelles(n=10, seed=5):
    _, e = _base()
    T = _tex()
    base = T['fons']
    out = []
    for i in range(n):
        cv = Canvas(img=base.copy())
        for k, (x, y) in enumerate(T['bright']):
            ph = (hr(k, seed) * n + i) % n
            if ph < 1:
                for dx, dy in ((0, 0), (1, 0), (-1, 0), (0, 1), (0, -1)):
                    cv.flat(x + dx, y + dy, (40, 40, 70) if (dx or dy) else (130, 136, 170))
            elif ph < 2:
                for dx, dy in ((1, 0), (-1, 0), (0, 1), (0, -1)):
                    cv.flat(x + dx, y + dy, (190, 196, 230))
        out.append(e.capa(_diff(cv.img, base), {'paret_fons'}))
    return out


ANIMS = {'estrelles': {'frames': _frames_estrelles, 'frameDuration': 300}}


# ─── Capes del davant ───────────────────────────────────────────────────────

def _amo(ids):
    def mask(x, y):
        _, e = _base()
        return e.ids[e.amo[y * e.cv.w + x]] in ids
    return mask


def _v(x, z, y=0.0):
    return CAM.projecta((x, y, z))[1]


FRONT = [
    *[{'id': f'davant_fila{r}', 'mask': _amo({f'fila{r}'}), 'baseline': round(_v(XM, z)), 'zIndex': 20}
      for r, z in enumerate(FILES)],
    {'id': 'davant_faristol', 'mask': _amo({'faristol'}), 'baseline': round(_v(FARISTOL[0], FARISTOL[1], ST[3])),
     'zIndex': 20},
    {'id': 'davant_taula', 'mask': _amo({'taula', 'safata'}), 'baseline': round(_v(TAULA[0], TAULA[1])), 'zIndex': 20},
    {'id': 'davant', 'mask': _amo({'primer_pla'}), 'baseline': 999, 'zIndex': 20},
]


# ─── Geometria (coordenades de sala, projectades) ────────────────────────────

def _p(x, z, y=0.0):
    u, v, _ = CAM.projecta((x, y, z))
    return round(u), round(v)


def _rect_mon(*Ps):
    pts = [CAM.projecta(P) for P in Ps]
    return (max(0, round(min(p[0] for p in pts))), max(0, round(min(p[1] for p in pts))),
            min(W - 1, round(max(p[0] for p in pts))), min(BOTTOM, round(max(p[1] for p in pts))))


def _girat(cx, cz, w, d, ang, marge=0.0):
    c, s = math.cos(ang), math.sin(ang)
    a, b = w / 2 + marge, d / 2 + marge
    return [(cx + lx * c - lz * s, cz + lx * s + lz * c) for lx, lz in ((-a, -b), (a, -b), (a, b), (-a, b))]


# El terra on es camina (al món): tota la platea, des de la paret de la porta fins a la taula del cava i el peu de
# l'escenari (i fins on el personatge no passa de ≈1,2). Forats: els dos blocs de cadires i la taula.
WALK_MON = [(16, 60), (16, ST[2] - 10), (GRAONS[0] - 8, ST[2] - 10), (GRAONS[0] - 8, ST[2] - GRAONS[3] * 3 - 8),
            (GRAONS[1] + 8, ST[2] - GRAONS[3] * 3 - 8), (GRAONS[1] + 8, ST[2] - 10), (XR - 16, ST[2] - 10),
            (XR - 16, 60)]
_WALK = GP.retalla([CAM.projecta((x, 0, z))[:2] for x, z in WALK_MON])
_V_FONS, _V_PROP = min(v for _, v in _WALK), max(v for _, v in _WALK)


def _escala_a(v):
    lo, hi = -200.0, 3000.0
    for _ in range(60):
        z = (lo + hi) / 2
        if CAM.projecta((XM, 0, z))[1] > v:
            lo = z
        else:
            hi = z
    return CAM.escala((XM, 0, (lo + hi) / 2))


def _bloc(b0, b1):
    return [_p(x, z) for x, z in ((b0 - 16, FILES[0] - 18), (b1 + 18, FILES[0] - 18), (b1 + 18, FILES[-1] + 10),
                                  (b0 - 16, FILES[-1] + 10))]


_PZ = (PORTA[0] + ZN, PORTA[1] + ZN)                # la porta, en z del món
_TP = [(x, y, z) for x, z in _girat(TAULA[0], TAULA[1], TAULA[3], TAULA[4], TAULA[2]) for y in (0, TAULA[5] + 40)]
_SAF = (TAULA[0] - 46 * math.cos(TAULA[2]) + 6 * math.sin(TAULA[2]),          # la safata (x, z), a la punta de la taula
        TAULA[1] - 46 * math.sin(TAULA[2]) - 6 * math.cos(TAULA[2]))
_SR = _rect_mon((_SAF[0] - 20, TAULA[5] + 14, _SAF[1]), (_SAF[0] + 20, TAULA[5] - 4, _SAF[1]))
_TR = _rect_mon(*_TP)

GEOMETRIA = {
    'things': {
        'porta_galeria': {'rect': _rect_mon((0, PORTA[2] + 26, _PZ[0] - 10), (0, 0, _PZ[1] + 10)),
                          'walk': _p(36, (_PZ[0] + _PZ[1]) / 2)},
        'pantalla': {'rect': _rect_mon(((PL.SCR[0] - PX0 - 8) * KP, YP - (PL.SCR[1] - PY0 - 8) * KP, ZW),
                                       ((PL.SCR[2] - PX0 + 8) * KP, YP - (PL.SCR[3] - PY0 + 8) * KP, ZW)),
                     'walk': _p(XM, ST[2] - GRAONS[3] * 3 - 14)},
        'escenari': {'rect': _rect_mon((ST[0], ST[3], ZW), (ST[1], 0, ST[2]), (ST[0], 0, ST[2])),
                     'walk': _p(XM, ST[2] - GRAONS[3] * 3 - 14)},
        'martell': {'rect': _rect_mon((FARISTOL[0] - 20, ST[3] + 62, FARISTOL[1]),
                                      (FARISTOL[0] + 24, ST[3], FARISTOL[1])),
                    'walk': _p(GRAONS[1] + 40, ST[2] - 20)},
        'safata': {'rect': _SR, 'walk': _p(_SAF[0] - 34, _SAF[1] - 10)},
        'cava': {'rect': (max(_TR[0], _SR[2] + 1), _TR[1], _TR[2], _TR[3]), 'walk': _p(TAULA[0] - 96, TAULA[1] - 20)},
    },
    # en Verne, damunt l'escenari, darrere el faristol; en Holm i en Kessel, a la platea
    'spawns': {'iri': _p(40, (_PZ[0] + _PZ[1]) / 2 - 20), 'verne': _p(FARISTOL[0] - 4, FARISTOL[1] + 22, ST[3]),
               'holm': _p(200, 150), 'kessel': _p(560, 196)},
    'walkable': _WALK,
    'forats': [_bloc(*BLOCS[0]), _bloc(*BLOCS[1]),
               [_p(x, z) for x, z in _girat(*TAULA[:2], TAULA[3], TAULA[4], TAULA[2], 8)]],
    'floorSquash': 0.45,
    'characterShadow': {'enabled': True, 'color': '#2a2030', 'alpha': 0.38, 'squash': 0.45, 'core': 0.6,
                        'light': {'x': _p(ARANYES[0][0], ARANYES[0][2])[0], 'y': _p(ARANYES[0][0], ARANYES[0][2])[1],
                                  'stretch': 0.6, 'reach': 140}},
    'regions': [{'id': 'perspectiva', 'active': True, 'scaleEnabled': True, 'scaleWalkSpeed': True,
                 'scaleTop': round(_escala_a(_V_FONS - 2), 3), 'scaleBottom': round(_escala_a(_V_PROP + 2), 3),
                 'points': [(0, _V_FONS - 2), (W - 1, _V_FONS - 2), (W - 1, _V_PROP + 2), (0, _V_PROP + 2)]}],
}
