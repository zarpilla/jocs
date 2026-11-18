"""
El moll de càrrega del BCMU (Escena 4b, l'Iri). EN 3D (hd640/tres_d.py), a 1×.

Una càmera alta, a l'esquerra del moll, que mira de biaix la cantonada del fons a la dreta:
  - a la paret del fons, la **persiana** enrotllada: fora, el pati amb les dues **furgonetes** blindades recolzades
    al moll (el darrere, el sostre i el costat), i més enllà el matí de Ginebra (l'edifici veí, el llac i el Jet
    d'Eau); la llum del dia entra pel forat i s'escampa en diagonal pel terra;
  - el rètol blau marí i or «MOLL DE CÀRREGA», el rellotge de fitxar i el casiller; al peu de la paret, els tres
    **tècnics** de la Rius amb la caixa d'eines;
  - el **toro**, separat de tot i girat, amb el palet de caixes a les forques i el llum giratori (s'hi passa per
    darrere); la **màquina de cafè**, una mica girada, i les caixes «FRÀGIL» al racó;
  - a la paret de la dreta, en escorç, l'**ascensor** de servei amb el lector de targetes;
  - primer pla: una columna d'acer a l'esquerra, i un pilot de palets i una tanca groga a la dreta.

Tot el detall ve del dibuix pla de sempre (bcmu_moll_pla_comu.py): les parets, les furgonetes, la màquina, els
tècnics i el llum del toro es projecten (textures i sprites). Animació: `llum_toro` (el llum giratori del toro, i el
fluorescent del mig que fa un parpelleig).

El món: x a la dreta (XR = la paret de la dreta), y amunt (0 = el terra del moll), z cap al fons (ZW = la paret de la
persiana); 1 unitat = 1 píxel de sala a la distància on un personatge fa ≈111 px (escala 1).
"""
import functools
import math

import hd640  # noqa: F401  (abans de cap hd.rooms: posa la llibreria a 640×360)
from hd640 import llum
from hd.pix import Canvas, Light, W, H, hr
from hd.rooms.comu import _diff, obox, text, text_width, PLASTIC, RED
from hd.rooms.exterior import fbm
from hd640.rooms import bcmu_moll_pla_comu as PL
from hd640.rooms.bcmu_moll_pla_comu import (BLOCKW, FLOORC, STEEL, YELH, FORK, COFFEE, PALLET, BOXC, TYRE)
from hd640.rooms.bcmu import NAVYB, BRASS
from hd640.tres_d import Camera, Escena, Llum

BOTTOM = 259                                       # la sala acaba aquí (a sota, la barra de verbs)
ZW = 300                                           # la paret del fons (la de la persiana)
XR = 420                                           # la paret de la dreta (la de l'ascensor)
HW = 248                                           # l'alçada de les parets
FX = 186                                           # al pla, la x que cau a x = 0 del món (paret del fons)
RX = 423                                           # al pla de la paret de la dreta, la x que cau a la cantonada
DOCK = -60                                         # el pati de fora, més avall que el moll

CAM = Camera(pos=(0, 190, -260), yaw=0.34, pitch=0.16, f=410, centre=(320, 78))
LIGHT = Light(ambient=0.0, vignette=None, floor_fade=None)  # (la llum és la del món: la de l'Escena)
TL = Light(ambient=-0.2, vignette=None, floor_fade=None)    # la del dibuix pla de les textures


def _w(fx):
    """Una x del dibuix pla de la paret del fons → la x del món."""
    return fx - FX


def _wz(fx):
    """Una x del dibuix pla de la paret de la dreta → la z del món (de la cantonada cap a la càmera)."""
    return ZW + RX - fx


def _y(fy):
    """Una y del dibuix pla (el terra, a 200) → l'alçada del món."""
    return PL.FLOOR_Y - fy


OPEN = (_w(PL.OPEN[0]), _w(PL.OPEN[2]), _y(43))   # el forat de la persiana: x0, x1, y de dalt (sota les lamel·les)
ELEV = (_wz(613), _wz(533), _y(53))                # l'ascensor: z0, z1 (a la paret de la dreta), y de dalt
TECNICS = ((70, ZW - 26, 'U', False), (92, ZW - 40, 'L', True), (114, ZW - 30, 'L', False))  # x, z, cara, mirall
TOOLBOX = (46, ZW - 18)
FORK_C = (196, 150, -0.5)                          # el toro: x, z del centre, gir (les forques, cap a l'esquerra)
COFFEE_C = (346, ZW - 30, -0.22)                   # la màquina de cafè: x, z, gir
CRATES_C = (392, ZW - 30)                          # les caixes «FRÀGIL», al racó
VANS = ((-162, -52, 132), (-38, 50, 120))          # les furgonetes: x0, x1, alçada sobre el pati
TUBES = ((60, 150), (300, 170))                    # els fluorescents (x, z), penjats del sostre

FOSC = [(4, 4, 6), (9, 9, 12), (15, 15, 19), (22, 22, 27), (31, 31, 37), (42, 42, 48)]
DAY = (255, 246, 222)

LLUMS = [Llum((-60, 130, ZW + 30), 420, 2.2, power=1.3),             # el dia, per la persiana
         Llum((TUBES[0][0], 210, TUBES[0][1]), 330, 1.5, power=1.3),  # el fluorescent del mig
         Llum((TUBES[1][0], 210, TUBES[1][1]), 300, 1.3, power=1.4)]  # el de l'ascensor


# ─── Les textures: el dibuix pla de sempre ───────────────────────────────────

@functools.lru_cache(maxsize=None)
def _tex_fons():
    """La paret del fons, de cara: el bloc, la persiana, el rètol, el rellotge i el casiller."""
    cv = Canvas(light=TL)
    PL.wall(cv)
    PL.shutter(cv)
    PL.time_clock(cv)
    s2 = 'ARMILLA OBLIGATÒRIA'                                            # (el rètol, a part: sobresurt)
    text(cv, s2, 330 - text_width(s2) // 2, 81, [(30, 30, 36)], 0, flat=(44, 44, 50))
    return cv.img


@functools.lru_cache(maxsize=None)
def _tex_dreta():
    """La paret de la dreta, de cara: el bloc i l'ascensor."""
    cv = Canvas(light=TL)
    PL.wall(cv)
    PL.elevator(cv)
    return cv.img


@functools.lru_cache(maxsize=None)
def _tex_fora():
    cv = Canvas(light=Light(ambient=-0.4, vignette=None, floor_fade=None))
    PL.outside(cv)
    return cv.img


@functools.lru_cache(maxsize=None)
def _tex_coses():
    """Les furgonetes, la màquina de cafè, les caixes del racó i el rètol del toro, plans."""
    cv = Canvas(light=TL)
    PL.van(cv, 141, 101, 227, 200)
    PL.van(cv, 29, 91, 128, 208)
    PL.coffee_machine(cv)
    PL.crates_right(cv)
    PL.house_sign(cv)
    cv.rect(560, 300, 620, 310, FORK, 3.4)
    text(cv, 'NO TOCAR', 566, 302, [(40, 20, 6)], 0, flat=(40, 20, 6))
    return cv.img


VAN_BOX = ((29, 91, 129, 196), (141, 101, 228, 188))   # el darrere de cada furgoneta (sense les rodes)
COFFEE_BOX = (400, 93, 446, 201)
CRATE_BOX = ((496, 152, 529, 177), (501, 131, 526, 152))
NOTOCAR_BOX = (560, 300, 621, 311)
SIGN_BOX = (261, 53, 401, 73)


def _tecnic_img(spec, facing, mirror):
    """Un tècnic sencer, a la mida normal (≈111 px): la imatge i els peus."""
    from PIL import Image
    import hd.characters as C
    PL.DC.install()
    img = C.person(spec, facing)
    feet = (round(PL.DC.f(25)), round(PL.DC.f(83)))
    if mirror:
        img = img.transpose(Image.FLIP_LEFT_RIGHT)
        feet = (img.width - 1 - feet[0], feet[1])
    # una mica més foscos: són al fons
    px = img.load()
    for y in range(img.height):
        for x in range(img.width):
            r, g, b, a = px[x, y]
            if a:
                px[x, y] = (int(r * 0.86), int(g * 0.88), int(b * 0.92), a)
    return img, feet


@functools.lru_cache(maxsize=None)
def _tecnics():
    out = []
    for (spec, f, _, mirror), (x, z, _, _) in zip(PL.TECNICS, TECNICS):
        img, feet = _tecnic_img(spec, f, mirror)
        if f == 'L':                                                      # el mòbil, a les mans: una llumeta blava
            hx = feet[0] + (6 if mirror else -6)
            for dy in range(4):
                img.putpixel((hx, feet[1] - 52 + dy), (190, 230, 255, 255) if dy else (235, 248, 255, 255))
                img.putpixel((hx + 1, feet[1] - 52 + dy), (150, 200, 240, 255))
        out.append((img, feet))
    return out


def _beacon_img(phase):
    """El llum giratori, pla (sobre transparent), en una fase: la imatge i el punt de la base."""
    cv = Canvas(light=TL, transparent=True)
    lx, ly = PL.BEACON
    obox(cv, lx - 4, ly - 1, lx + 4, ly + 3, PLASTIC, 2.4)
    PL.beacon(cv, phase)
    box = (lx - 6, ly - 11, lx + 7, ly + 4)
    return cv.img.crop(box), (lx - box[0], ly + 3 - box[1])


# ─── Les superfícies ────────────────────────────────────────────────────────

def _bloc(lvl0, seed=3):
    """Bloc de formigó en coordenades del món (s, t des del cantó de dalt): on el dibuix pla no arriba."""
    def L(s, t, P):
        row = int(t // 12)
        off = 16 if row % 2 else 0
        if t % 12 > 11 or (s + off) % 32 < 1:
            return lvl0 - 1.2
        return lvl0 + (hr(int((s + off) // 32), row, seed) - 0.5) * 0.5 + (hr(int(s) // 2, int(t) // 2, 11) - 0.5) * 0.3
    return L


def _terra(s, t, P):
    """Formigó en coordenades del món: lloses de 128 amb junts, taques d'oli, les línies grogues i la zebra."""
    x, z = P[0], P[2]
    n = (fbm(x / 50, z / 30, 7) - 0.5) * 0.7 + (hr(int(x) // 3, int(z) // 2, 8) - 0.5) * 0.25
    v = 3.4 + n
    if x % 128 < 1.2 or z % 128 < 1.2:
        v = 2.0
    oil = fbm(x / 26 + 3, z / 14, 12)
    if oil > 0.68:
        v -= (oil - 0.68) * 9
    return v


def _llum_dia(x, z):
    """Quanta llum del dia (0..1) cau al terra: el forat de la persiana projectat en diagonal cap a la càmera."""
    # el sol entra baix, de l'esquerra i del fons: cada punt mira enrere cap al forat
    k = (ZW - z) / 1.0
    xw = x + k * 0.42
    if not (OPEN[0] + 4 < xw < OPEN[1] - 4) or z > ZW:
        return 0.0
    return max(0.0, 1 - k / 260) * 0.38 * min(1.0, (xw - OPEN[0]) / 30, (OPEN[1] - xw) / 30)


def _caixa_local(e, sid, cx, cz, ang, lx, lz, w, d, h, ramp, lvl=3.0, y0=0.0, cares=None):
    """Una caixa_girada amb el centre a (lx, lz) del sistema d'un objecte girat (centre cx, cz, gir ang)."""
    c, s_ = math.cos(ang), math.sin(ang)
    e.caixa_girada(sid, cx + lx * c - lz * s_, cz + lx * s_ + lz * c, w, d, h, ang, ramp, lvl, y0=y0, cares=cares)


def _local(cx, cz, ang, lx, y, lz):
    c, s_ = math.cos(ang), math.sin(ang)
    return (cx + lx * c - lz * s_, y, cz + lx * s_ + lz * c)


def ombra(e, sid, x, z, rx, rz, k=0.55, dx=10, dz=-14):
    """Una ombra suau al terra sota una cosa (una el·lipse una mica desplaçada, cap on no hi ha la llum)."""
    x, z = x + dx, z + dz
    e.foscor(sid, (x - rx, 0.6, z + rz), (x + rx, 0.6, z + rz), (x + rx, 0.6, z - rz), (x - rx, 0.6, z - rz),
             lambda s, t: k * max(0.0, 1 - ((s - rx) / rx) ** 2 - ((t - rz) / rz) ** 2) * 1.6)


def fora(e, tex):
    """Fora: el fons (el dibuix pla del matí), el pati assolellat i les dues furgonetes."""
    zf = ZW + 440
    e.quad('fora', (-320, 194, zf), (78, 194, zf), (78, 7, zf), (-320, 7, zf),
           tex=(tex['fora'], (PL.OPEN[0], PL.OPEN[1], PL.OPEN[2], 139)))
    e.quad('fora', (-400, DOCK, zf), (260, DOCK, zf), (260, DOCK, ZW), (-400, DOCK, ZW), ramp=PL.FLOORC,
           lvl=lambda s, t, P: 5.4 + (hr(int(P[0]) // 3, int(P[2]) // 2, 4) - 0.5) * 0.5
           + (fbm(P[0] / 40, P[2] / 20, 2) - 0.5) * 0.6 - (1.6 if int(P[0] + 400) % 150 < 2 else 0))
    coses = tex['coses']
    for (x0, x1, hh), box in zip(VANS, VAN_BOX):
        z0, z1 = ZW + 8, ZW + 280
        y0, y1 = DOCK + 14, DOCK + 14 + hh
        e.foscor('fora', (x0 - 6, DOCK + 0.5, z1 + 30), (x1 + 30, DOCK + 0.5, z1 + 30), (x1 + 30, DOCK + 0.5, z0),
                 (x0 - 6, DOCK + 0.5, z0), lambda s, t: 0.6)

        def costat(s, t, P, y1=y1):
            v = 2.0 + (fbm(s / 30, t / 9, 5) - 0.5) * 0.3
            if 30 <= t <= 34:
                return 3.8                                                   # la franja d'or (es veu a la vora)
            return v - (0.6 if int(s) % 60 < 2 else 0)
        e.caixa('furgonetes', x0, x1, y0, y1, z0, z1, NAVYB, 2.4,
                cares={'davant': {'tex': (coses, box)},
                       'dalt': {'ramp': NAVYB, 'lvl': lambda s, t, P: 3.6 - (1.2 if int(s) % 24 < 2 else 0)},
                       'dreta': {'ramp': NAVYB, 'lvl': costat}, 'esquerra': {'ramp': NAVYB, 'lvl': costat}})
        e.caixa('furgonetes', x0 + 6, x1 - 6, y1, y1 + 3, z0 + 20, z0 + 140, STEEL, 3.0)   # la baca
        e.caixa('furgonetes', x0 - 2, x1 + 2, DOCK, y0 + 12, z0 - 4, z0 + 4, STEEL, 3.0)    # el para-xocs
        for wx in (x0 + 6, x1 - 18):
            e.caixa('furgonetes', wx, wx + 12, DOCK, y0, z0 + 30, z0 + 64, TYRE, 1.4)


def parets(e, tex):
    zn = CAM.pos[2] + 60
    fons, dreta = tex['fons'], tex['dreta']
    fx0, fx1 = PL.OPEN[0], PL.OPEN[2]
    ytop = _y(43)
    HF = PL.FLOOR_Y                                  # fins aquí, el dibuix pla; a sobre, bloc
    # la paret del fons: a l'esquerra del forat (més bloc), el forat, a la dreta fins a la cantonada; i a dalt
    e.quad('paret_fons', (-460, HW, ZW), (XR, HW, ZW), (XR, HF, ZW), (-460, HF, ZW), ramp=BLOCKW, lvl=_bloc(3.6))
    e.quad('paret_fons', (-460, HF, ZW), (_w(0), HF, ZW), (_w(0), 0, ZW), (-460, 0, ZW), ramp=BLOCKW, lvl=_bloc(3.6))
    e.quad('paret_fons', (_w(0), HF, ZW), (OPEN[0], HF, ZW), (OPEN[0], 0, ZW), (_w(0), 0, ZW),
           tex=(fons, (0, 0, fx0, HF)))
    e.quad('paret_fons', (OPEN[0], HF, ZW), (OPEN[1], HF, ZW), (OPEN[1], ytop, ZW), (OPEN[0], ytop, ZW),
           tex=(fons, (fx0, 0, fx1, 43)))
    e.quad('paret_fons', (OPEN[1], HF, ZW), (XR, HF, ZW), (XR, 0, ZW), (OPEN[1], 0, ZW),
           tex=(fons, (fx1, 0, FX + XR, HF)))
    # la paret de la dreta: de la cantonada fins on arriba el dibuix pla, i bloc fins a la càmera
    e.quad('paret_dreta', (XR, HW, ZW), (XR, HW, zn), (XR, HF, zn), (XR, HF, ZW), ramp=BLOCKW, lvl=_bloc(3.6, 5))
    e.quad('paret_dreta', (XR, HF, ZW), (XR, HF, _wz(W)), (XR, 0, _wz(W)), (XR, 0, ZW),
           tex=(dreta, (RX, 0, W, HF)))
    e.quad('paret_dreta', (XR, HF, _wz(W)), (XR, HF, zn), (XR, 0, zn), (XR, 0, _wz(W)), ramp=BLOCKW, lvl=_bloc(3.6, 5))
    # la franja de perill i el sòcol continuen per la part de bloc
    e.quad('paret_dreta', (XR - 0.4, 24, _wz(W)), (XR - 0.4, 24, zn), (XR - 0.4, 0, zn), (XR - 0.4, 0, _wz(W)),
           ramp=YELH, lvl=lambda s, t, P: (3.0 if int(s + t) // 8 % 2 == 0 else 0.4) if t < 11 else 1.8)
    e.quad('paret_fons', (-460, 24, ZW - 0.4), (_w(0), 24, ZW - 0.4), (_w(0), 0, ZW - 0.4), (-460, 0, ZW - 0.4),
           ramp=YELH, lvl=lambda s, t, P: (3.0 if int(s + t) // 8 % 2 == 0 else 0.4) if t < 11 else 1.8)


def terra(e):
    zn = CAM.pos[2] + 60
    e.quad('terra', (-460, 0, ZW), (XR, 0, ZW), (XR, 0, zn), (-460, 0, zn), ramp=FLOORC, lvl=_terra)
    # la pintura groga (i el negre de la vora del moll), damunt
    def groc(s, t, P):
        return 2.8 - (0.9 if hr(int(P[0]) // 3, int(P[2]) // 2, 10) > 0.86 else 0)
    for z0, z1 in ((-20, -16), (50, 54)):
        e.quad('terra', (-460, 0.2, z1), (XR, 0.2, z1), (XR, 0.2, z0), (-460, 0.2, z0), ramp=YELH, lvl=groc)
    e.quad('terra', (OPEN[0], 0.2, ZW), (OPEN[1], 0.2, ZW), (OPEN[1], 0.2, ZW - 12), (OPEN[0], 0.2, ZW - 12),
           ramp=YELH, lvl=lambda s, t, P: 3.2 if int(s - t) % 14 < 7 else -2.0)
    # la zebra davant l'ascensor (barres en diagonal)
    for k in range(5):
        za = ELEV[0] + 6 + k * 18
        e.quad('terra', (XR - 66, 0.2, za + 10), (XR - 10, 0.2, za + 4), (XR - 10, 0.2, za - 4), (XR - 66, 0.2, za + 2),
               ramp=YELH, lvl=lambda s, t, P: 2.8 - (0.9 if hr(int(P[0]) // 2, int(P[2]) // 2, 10) > 0.85 else 0))


def llums_terra(e):
    """El dia que entra en diagonal i els bassals de llum sota els fluorescents."""
    e.claror((-460, 0.4, ZW), (XR, 0.4, ZW), (XR, 0.4, -100), (-460, 0.4, -100), DAY,
             lambda s, t: _llum_dia(s - 460, ZW - t))
    for tx, tz in TUBES:
        e.claror((tx - 140, 0.5, tz + 90), (tx + 140, 0.5, tz + 90), (tx + 140, 0.5, tz - 90), (tx - 140, 0.5, tz - 90),
                 (230, 240, 250), lambda s, t: 0.12 * max(0.0, 1 - math.hypot((s - 140) / 140, (t - 90) / 90)))
    # la foscor dels racons, al peu de les parets
    e.foscor('racons', (-460, 0.5, ZW), (XR, 0.5, ZW), (XR, 0.5, -200), (-460, 0.5, -200),
             lambda s, t: max(0.5 * max(0.0, 1 - t / 26), 0.5 * max(0.0, 1 - (880 - s) / 30)))
    e.foscor('cantonada', (XR - 70, HW, ZW - 0.6), (XR, HW, ZW - 0.6), (XR, 0, ZW - 0.6), (XR - 70, 0, ZW - 0.6),
             lambda s, t: 0.45 * max(0.0, s / 70) ** 1.5)
    e.foscor('cantonada', (XR - 0.6, HW, ZW - 80), (XR - 0.6, HW, ZW), (XR - 0.6, 0, ZW), (XR - 0.6, 0, ZW - 80),
             lambda s, t: 0.45 * max(0.0, s / 80) ** 1.5)


def tecnics(e):
    tb = TOOLBOX
    ombra(e, 'ombres', tb[0], tb[1], 14, 10)
    e.caixa('caixa_eines', tb[0] - 10, tb[0] + 10, 0, 12, tb[1] - 6, tb[1] + 6, RED, 2.6,
            cares={'dalt': {'ramp': RED, 'lvl': lambda s, t, P: 3.4 - (1.4 if abs(t - 6) < 1 else 0)}})
    e.caixa('caixa_eines', tb[0] - 4, tb[0] + 4, 12, 16, tb[1] - 1, tb[1] + 1, STEEL, 3.4)
    for (x, z, _, _), (img, feet) in sorted(zip(TECNICS, _tecnics()), key=lambda p: -p[0][1]):
        ombra(e, 'ombres', x, z, 14, 7, k=0.6, dx=8, dz=-8)
        e.sprite('tecnics', img, feet, (x, 0, z))


def toro(e, tex):
    """El toro, girat: el cos, el contrapès, la cabina, el pal, les forques amb el palet i les caixes."""
    cx, cz, a = FORK_C
    ombra(e, 'ombra_toro', cx - 20, cz, 90, 46, k=0.6)
    sid = 'toro'

    def cos_lvl(s, t, P):
        return 3.2 + (hr(int(s) // 2, int(t) // 2, 40) - 0.5) * 0.25 - (1.0 if abs(t - 22) < 0.8 else 0)
    # les rodes de darrere, el cos i les de davant (del costat que es veu)
    def roda(lx, lz):
        e.tub(sid, _local(cx, cz, a, lx, 13, lz - 4), _local(cx, cz, a, lx, 13, lz + 4), 13, TYRE, 1.8,
              llum_dir=(-0.3, 1.0))
        e.tub(sid, _local(cx, cz, a, lx, 13, lz - 5 if lz < 0 else lz + 5),
              _local(cx, cz, a, lx, 13, lz - 5.5 if lz < 0 else lz + 5.5), 5, STEEL, 3.4)
    for lx in (-22, 50):
        roda(lx, 33)
    _caixa_local(e, sid, cx, cz, a, 12, 0, 92, 62, 40, FORK, 3.0, y0=14,
                 cares={'dalt': {'ramp': FORK, 'lvl': 4.2}, 'davant': {'ramp': FORK, 'lvl': cos_lvl},
                        'darrere': {'ramp': FORK, 'lvl': cos_lvl}, 'esquerra': {'ramp': FORK, 'lvl': 2.6},
                        'dreta': {'ramp': FORK, 'lvl': 2.2}})
    for lx in (-22, 50):
        roda(lx, -33)
    # el rètol «NO TOCAR», al costat que es veu
    P0 = _local(cx, cz, a, -12, 40, -31.4)
    P1 = _local(cx, cz, a, 34, 40, -31.4)
    e.quad(sid, P0, P1, (P1[0], 32, P1[2]), (P0[0], 32, P0[2]), tex=(tex['coses'], NOTOCAR_BOX))
    _caixa_local(e, sid, cx, cz, a, 64, 0, 16, 64, 56, FORK, 2.2, y0=4,
                 cares={'dalt': {'ramp': FORK, 'lvl': 3.4},
                        'davant': {'ramp': FORK, 'lvl': lambda s, t, P: 2.6 - (1.2 if int(t) % 6 < 1 and t > 8 else 0)},
                        'darrere': {'ramp': FORK, 'lvl': lambda s, t, P: 2.6 - (1.2 if int(t) % 6 < 1 and t > 8 else 0)}})
    # el seient i el volant
    _caixa_local(e, sid, cx, cz, a, 34, 0, 22, 30, 10, PLASTIC, 1.8, y0=52)
    _caixa_local(e, sid, cx, cz, a, 46, 0, 5, 30, 28, PLASTIC, 1.6, y0=60)
    e.cable(sid, [_local(cx, cz, a, -6, 52, 0), _local(cx, cz, a, -2, 68, 0)], PLASTIC, 1.6, gruix=2.0)
    e.cable(sid, [_local(cx, cz, a, -8, 70, -8), _local(cx, cz, a, -4, 70, 8)], PLASTIC, 2.4, gruix=2.4)
    # la cabina: quatre pals i el sostre de reixa
    for lx in (-26, 48):
        for lz in (-29, 29):
            _caixa_local(e, sid, cx, cz, a, lx, lz, 4, 4, 82, PLASTIC, 2.2, y0=52)
    _caixa_local(e, sid, cx, cz, a, 11, 0, 80, 64, 4, PLASTIC, 2.6, y0=134,
                 cares={'dalt': {'ramp': PLASTIC, 'lvl': lambda s, t, P: 3.2 if int(s) % 7 < 2 or t < 2 or t > 62 else 0.4}})
    # el pal de les forques, amb la cadena
    for lz in (-20, 20):
        _caixa_local(e, sid, cx, cz, a, -40, lz, 6, 6, 150, STEEL, 2.8, y0=2,
                     cares={'davant': {'ramp': STEEL, 'lvl': 3.6}})
    _caixa_local(e, sid, cx, cz, a, -40, 0, 6, 46, 4, STEEL, 3.4, y0=148)
    _caixa_local(e, sid, cx, cz, a, -42, 0, 2, 4, 130, STEEL, 1.6, y0=10)
    # les forques i el palet amb les caixes
    _caixa_local(e, sid, cx, cz, a, -46, 0, 4, 52, 30, STEEL, 2.4, y0=4)
    for lz in (-14, 14):
        _caixa_local(e, sid, cx, cz, a, -70, lz, 50, 7, 3, STEEL, 3.4, y0=4)
    _caixa_local(e, 'palet', cx, cz, a, -74, 0, 52, 66, 9, PALLET, 3.0, y0=7,
                 cares={'davant': {'ramp': PALLET, 'lvl': lambda s, t, P: 1.0 if 2 < t < 6 and int(s) % 17 > 5 else 3.0},
                        'darrere': {'ramp': PALLET, 'lvl': lambda s, t, P: 1.0 if 2 < t < 6 and int(s) % 17 > 5 else 3.0},
                        'esquerra': {'ramp': PALLET, 'lvl': lambda s, t, P: 0.8 if 2 < t < 6 and int(s) % 22 > 6 else 2.6}})

    def caixa_lvl(s, t, P, base=3.4):
        return base - (1.4 if abs(t - 10) < 1 else 0) + (hr(int(s) // 3, int(t) // 3, 6) - 0.5) * 0.3
    for lx, lz, w, d, h, y0, aa in ((-84, -14, 26, 30, 24, 16, 0.0), (-62, -12, 22, 28, 22, 16, 0.08),
                                    (-76, 16, 30, 30, 26, 16, -0.05), (-74, 0, 26, 28, 22, 42, 0.12)):
        c2 = {'dalt': {'ramp': BOXC, 'lvl': lambda s, t, P: 4.0 - (1.4 if abs(s - w / 2) < 1.5 else 0)},
              'davant': {'ramp': BOXC, 'lvl': caixa_lvl}, 'darrere': {'ramp': BOXC, 'lvl': caixa_lvl},
              'esquerra': {'ramp': BOXC, 'lvl': lambda s, t, P: caixa_lvl(s, t, P, 2.6)}}
        P = _local(cx, cz, a, lx, 0, lz)
        e.caixa_girada('palet', P[0], P[2], w, d, h, a + aa, BOXC, 3.0, y0=y0, cares=c2)
    # el llum giratori, damunt del sostre
    img, peu = _beacon_img(0)
    e.sprite('llum_toro', img, peu, _local(cx, cz, a, 18, 138, 0), escala_img=1.4)


def beacon_peu():
    cx, cz, a = FORK_C
    return _local(cx, cz, a, 18, 138, 0)


def maquina(e, tex):
    """La màquina de cafè, una mica girada: el davant és el dibuix pla; el costat dret, amb el cop de puny."""
    cx, cz, a = COFFEE_C
    w, d, h = (COFFEE_BOX[2] - COFFEE_BOX[0]) * 1.1, 40, (COFFEE_BOX[3] - COFFEE_BOX[1]) * 1.1
    ombra(e, 'ombres', cx, cz, 30, 26, k=0.55)

    def costat(s, t, P):
        v = 3.0 - t * 0.006
        if math.hypot((s - 22) / 7, (t - 68) / 10) < 1:
            return v - 1.4 + math.hypot((s - 22) / 7, (t - 68) / 10) * 1.2       # el cop de puny
        return v
    e.caixa_girada('maquina', cx, cz, w, d, h, a, COFFEE, 2.6,
                   cares={'davant': {'tex': (tex['coses'], COFFEE_BOX)}, 'dalt': {'ramp': COFFEE, 'lvl': 4.0},
                          'dreta': {'ramp': COFFEE, 'lvl': costat}, 'esquerra': {'ramp': COFFEE, 'lvl': 3.4}})


def caixes_raco(e, tex):
    x, z = CRATES_C
    ombra(e, 'ombres', x, z, 30, 22, k=0.5)
    e.caixa('caixes', x - 22, x + 22, 0, 7, z - 20, z + 20, PALLET, 3.0,
            cares={'davant': {'ramp': PALLET, 'lvl': lambda s, t, P: 0.8 if 2 < t < 5 and int(s) % 15 > 5 else 3.0}})
    for (bx0, bx1, y0, y1, dz), box in zip(((x - 20, x + 20, 7, 37, 0), (x - 14, x + 14, 37, 62, 3)), CRATE_BOX):
        e.caixa('caixes', bx0, bx1, y0, y1, z - 18 + dz, z + 18 - dz, BOXC, 3.0,
                cares={'davant': {'tex': (tex['coses'], box)}, 'dalt': {'ramp': BOXC, 'lvl': 4.0},
                       'esquerra': {'ramp': BOXC, 'lvl': 2.8}})


def retol(e, tex):
    """El rètol de la casa, una placa que sobresurt de la paret (més gran que al pla, perquè es llegeixi)."""
    x0, x1, y0, y1 = _w(SIGN_BOX[0]), _w(SIGN_BOX[2]), _y(SIGN_BOX[3]), _y(SIGN_BOX[1])
    k, xc, yc = 1.3, (x0 + x1) / 2, (y0 + y1) / 2
    x0, x1, y0, y1 = xc - (xc - x0) * k, xc + (x1 - xc) * k, yc - (yc - y0) * k + 6, yc + (y1 - yc) * k + 6
    e.caixa('retol', x0, x1, y0, y1, ZW - 4, ZW, NAVYB, 2.0,
            cares={'davant': {'tex': (tex['coses'], SIGN_BOX)}, 'sota': {'ramp': NAVYB, 'lvl': 1.0},
                   'esquerra': {'ramp': BRASS, 'lvl': 3.0}})
    e.foscor('retol', (x0 + 2, y0, ZW - 0.5), (x1 + 4, y0, ZW - 0.5), (x1 + 4, y0 - 6, ZW - 0.5), (x0 + 2, y0 - 6, ZW - 0.5),
             lambda s, t: 0.4)


def ascensor(e):
    """El marc de l'ascensor sobresurt una mica de la paret (els muntants i la llinda, d'acer)."""
    z0, z1, yt = ELEV
    for za, zb in ((z0, z0 + 6), (z1 - 6, z1)):
        e.caixa('ascensor', XR - 4, XR, 0, yt, za, zb, STEEL, 3.0, cares={'esquerra': {'ramp': STEEL, 'lvl': 3.8}})
    e.caixa('ascensor', XR - 4, XR, yt - 6, yt, z0, z1, STEEL, 3.0, cares={'sota': {'ramp': STEEL, 'lvl': 1.4}})


def primer_pla(e):
    """Una columna d'acer a l'esquerra, i un pilot de palets i una tanca groga a la dreta."""
    # la columna (un perfil en H), tallada per la vora
    cx, cz = -70, -60
    e.caixa('primer_pla', cx - 10, cx + 10, 0, HW + 40, cz - 4, cz + 4, FOSC, 1.6,
            cares={'davant': {'ramp': FOSC, 'lvl': lambda s, t, P: 2.0 - (0.8 if s > 24 else 0) + (0.8 if s < 3 else 0)}})
    for dz in (-12, 12):
        e.caixa('primer_pla', cx - 11, cx + 11, 0, HW + 40, cz + dz - 2, cz + dz + 2, FOSC, 2.2,
                cares={'davant': {'ramp': FOSC, 'lvl': lambda s, t, P: (3.6 if s > 19 else 2.6) - (1.4 if int(t) % 60 < 2 else 0)},
                       'dreta': {'ramp': FOSC, 'lvl': 3.2}})
    e.caixa('primer_pla', cx - 16, cx + 16, 0, 10, cz - 18, cz + 18, FOSC, 2.4)
    # el pilot de palets a la dreta, una mica girat
    for k in range(6):
        e.caixa_girada('primer_pla', 360 + (k % 2) * 3, -30, 90, 70, 9, 0.35 + (k % 3) * 0.03, FOSC, 2.0, y0=k * 10,
                       cares={'davant': {'ramp': FOSC, 'lvl': lambda s, t, P: 0.6 if 2 < t < 6 and int(s) % 30 > 9 else 2.6},
                              'esquerra': {'ramp': FOSC, 'lvl': lambda s, t, P: 0.6 if 2 < t < 6 and int(s) % 24 > 8 else 2.2},
                              'dalt': {'ramp': FOSC, 'lvl': lambda s, t, P: 3.0 if int(s) % 18 < 10 else 1.0}})
    # la tanca groga (desenfocada a prop): dos pals i una barra
    TANCA = [(30, 22, 4), (60, 46, 8), (110, 84, 14), (160, 124, 22), (200, 160, 30)]
    for x in (250, 320):
        e.tub('primer_pla', (x, 0, -60), (x, 64, -60), 4, TANCA, 2.2)
    e.tub('primer_pla', (246, 60, -60), (324, 60, -60), 3.4, TANCA, 2.6)


def escena(cv, tex, estat=frozenset()):
    """Tota la sala, de lluny a prop. → l'Escena (qui ha pintat què)."""
    e = Escena(cv, CAM, LLUMS, ambient=-0.2)
    fora(e, tex)
    parets(e, tex)
    terra(e)
    llums_terra(e)
    ascensor(e)
    retol(e, tex)
    tecnics(e)
    caixes_raco(e, tex)
    maquina(e, tex)
    toro(e, tex)
    primer_pla(e)
    return e


# ─── Composició i llum ──────────────────────────────────────────────────────

def _proj(P):
    u, v, _ = CAM.projecta(P)
    return u, v


def _fx():
    ox, oy = _proj(((OPEN[0] + OPEN[1]) / 2, 60, ZW))
    t1 = _proj((TUBES[0][0], 120, TUBES[0][1]))
    t2 = _proj((TUBES[1][0], 120, TUBES[1][1]))
    light = [llum.wash(ox, oy + 40, 240, (255, 240, 210), k=0.3, air=0.03, squash=0.8),  # el dia
             llum.wash(t1[0], t1[1], 220, (220, 236, 255), k=0.25, air=0.02, squash=0.9),
             llum.wash(t2[0], t2[1], 200, (220, 236, 255), k=0.2, air=0.02, squash=0.9)]
    tone = [llum.grade(contrast=1.08, pivot=60, sat=1.1, lift=(3, 4, 8))]
    bloom = [llum.bloom(thr=215)]
    return light, bloom, tone


@functools.lru_cache(maxsize=None)
def _textures():
    return {'fons': _tex_fons(), 'dreta': _tex_dreta(), 'fora': _tex_fora(), 'coses': _tex_coses()}


def _render(estat=frozenset(), tex=None):
    cv = Canvas(light=LIGHT)
    e = escena(cv, tex or _textures(), estat)
    cv.rect(0, BOTTOM + 1, W - 1, H - 1, [(0, 0, 0)], 0, lit=0)    # la barra de verbs: negre
    return cv.img, e


@functools.lru_cache(maxsize=None)
def _base():
    return _render()


def _amb_llum(img, bloom=True):
    light, bl, tone = _fx()
    return llum.apply(img, light + (bl if bloom else []) + tone)


@functools.lru_cache(maxsize=None)
def _base_llum():
    return _amb_llum(_base()[0])


def bg(cv):
    cv.img.paste(_base_llum())
    cv.P = cv.img.load()


PROPS = {}


# ─── El llum giratori del toro ─────────────────────────────────────────────

def _sprite_capa(e, sid, img, peu_img, peu, escala_img=1.0):
    """Un fotograma d'un dibuix pla dret (un sprite de l'escena), on aquell sprite és el que es veu (o on no hi ha
    ningú al davant)."""
    from PIL import Image
    from pixels import nearest
    idx = e.ids.index(sid)
    k = e.cam.escala(peu) * escala_img
    u, v, _ = e.cam.projecta(peu)
    w, h = max(1, round(img.width * k)), max(1, round(img.height * k))
    im = nearest(img, (w, h)) if k >= 1 else img.resize((w, h), Image.Resampling.BOX)
    ox, oy = round(u - peu_img[0] * k), round(v - peu_img[1] * k)
    out = Image.new('RGBA', (e.cv.w, e.cv.h), (0, 0, 0, 0))
    src, dst, W_ = im.load(), out.load(), e.cv.w
    for y in range(h):
        Y = oy + y
        if not 0 <= Y < e.cv.h:
            continue
        for x in range(w):
            X = ox + x
            if 0 <= X < W_ and e.ids[e.amo[Y * W_ + X]] in (sid, 'toro') and src[x, y][3] >= 128:
                dst[X, Y] = src[x, y]
    return out


def _glow(img, cx, cy, r, col, k):
    """Un halo additiu (el llum taronja) damunt la imatge."""
    import numpy as np
    from PIL import Image
    a = np.asarray(img).astype(np.float32)
    ys, xs = np.mgrid[0:a.shape[0], 0:a.shape[1]]
    d = np.clip(1 - np.hypot((xs - cx) / r, (ys - cy) / (r * 0.7)), 0, 1) ** 1.6 * k
    for i in range(3):
        a[..., i] = np.clip(a[..., i] + d * col[i], 0, 255)
    return Image.fromarray(a.astype(np.uint8), 'RGBA')


def _fosc(img, cx, cy, rx, ry, k):
    """El fluorescent que parpelleja: el bassal de llum de sota, més fosc."""
    import numpy as np
    from PIL import Image
    a = np.asarray(img).astype(np.float32)
    ys, xs = np.mgrid[0:a.shape[0], 0:a.shape[1]]
    d = 1 - np.clip(1 - np.hypot((xs - cx) / rx, (ys - cy) / ry), 0, 1) * k
    d[BOTTOM + 1:] = 1
    for i in range(3):
        a[..., i] = a[..., i] * d
    return Image.fromarray(a.astype(np.uint8), 'RGBA')


def _frames():
    img0, e = _base()
    base = _base_llum()
    peu = beacon_peu()
    bu, bv = _proj((peu[0], peu[1] + 10, peu[2]))
    tu, tv = _proj((TUBES[0][0], 0, TUBES[0][1]))
    out = []
    for i in range(8):
        phase = i % 4
        im, pi = _beacon_img(phase)
        img = img0.copy()
        img.alpha_composite(_sprite_capa(e, 'llum_toro', im, pi, peu, escala_img=1.4))
        img = _amb_llum(img)
        if phase in (0, 1, 2):
            dx = (-1, 0, 1)[phase]
            img = _glow(img, bu + dx * 16, bv, 46 if phase == 1 else 34, (255, 140, 40), 0.55 if phase == 1 else 0.38)
        if i == 5:
            img = _fosc(img, tu, tv - 30, 230, 120, 0.22)
        out.append(_diff(img, base))
    return out


ANIMS = {'llum_toro': {'frames': _frames, 'frameDuration': 180}}


# ─── Capes del davant ─────────────────────────────────────────────────────────

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
    {'id': 'davant_toro', 'mask': _amo({'toro', 'palet', 'llum_toro'}),
     'baseline': _p(*_local(FORK_C[0], FORK_C[1], FORK_C[2], -20, 0, -40)[::2])[1], 'zIndex': 20},
    {'id': 'davant_maquina', 'mask': _amo({'maquina'}), 'baseline': _p(COFFEE_C[0], COFFEE_C[1] - 20)[1], 'zIndex': 20},
]


# ─── Geometria (coordenades de sala, projectades) ────────────────────────────

def _rect_mon(*Ps):
    pts = [CAM.projecta(P) for P in Ps]
    return (max(0, round(min(p[0] for p in pts))), max(0, round(min(p[1] for p in pts))),
            min(W - 1, round(max(p[0] for p in pts))), min(BOTTOM, round(max(p[1] for p in pts))))


def _escala_a(v):
    """L'escala d'un personatge amb els peus a la y de pantalla `v` (al terra, la profunditat només depèn de v)."""
    lo, hi = 1.0, 4000.0
    for _ in range(60):
        z = (lo + hi) / 2
        if CAM.projecta((200, 0, z))[1] > v:
            lo = z
        else:
            hi = z
    return CAM.escala((200, 0, (lo + hi) / 2))


# El terra on es camina (al món): del primer pla (on l'escala arriba a ≈1,2) fins al peu de la paret del fons (sense
# caure del moll), deixant els tècnics, la màquina, les caixes del racó i el muntant de l'ascensor; el toro, un forat.
Z_NEAR = -40                                       # (a prop, es retalla on l'escala arriba a ≈1,2: V_MAX)
WALK_MON = [(-150, Z_NEAR), (-150, ZW - 18), (OPEN[1] + 4, ZW - 18), (OPEN[1] + 4, ZW - 52), (140, ZW - 58),
            (300, ZW - 50), (320, ZW - 64), (372, ZW - 66), (XR - 14, ZW - 62), (XR - 14, Z_NEAR)]
def _retalla_v(poly, vmax):
    """El polígon de pantalla retallat per sota de la y `vmax` (on l'escala arriba a ≈1,2)."""
    out = []
    for (ax, ay), (bx, by) in zip(poly, poly[1:] + poly[:1]):
        if ay <= vmax:
            out.append((ax, ay))
        if (ay <= vmax) != (by <= vmax):
            k = (vmax - ay) / (by - ay)
            out.append((round(ax + (bx - ax) * k), vmax))
    return out


def _v_a_escala(k):
    lo, hi = 0.0, 600.0
    for _ in range(40):
        v = (lo + hi) / 2
        if _escala_a(v) < k:
            lo = v
        else:
            hi = v
    return int(lo)


V_MAX = min(BOTTOM - 4, _v_a_escala(1.2))
_WALK = _retalla_v([_p(x, z) for x, z in WALK_MON], V_MAX)
_WALK = [(min(W - 1, max(0, u)), v) for u, v in _WALK]
_V_FONS, _V_PROP = min(v for _, v in _WALK), max(v for _, v in _WALK)
_FORAT_TORO = [_p(*_local(FORK_C[0], FORK_C[1], FORK_C[2], lx, 0, lz)[::2]) for lx, lz in
               ((-104, -40), (78, -40), (78, 40), (-104, 40))]

_VAN_PTS = [(x, y, ZW + 8) for x0, x1, hh in VANS for x in (x0, x1) for y in (DOCK + 14, DOCK + 14 + hh)]
_FUR = _rect_mon(*_VAN_PTS)
_FUR = (_FUR[0], _FUR[1], _FUR[2], min(_FUR[3], _p(0, ZW)[1]))
_TEC = _rect_mon(*[(x + dx, y, z) for x, z, _, _ in TECNICS for dx in (-18, 18) for y in (0, 112)])
_MAQ = _rect_mon(*[_local(COFFEE_C[0], COFFEE_C[1], COFFEE_C[2], lx, y, lz) for lx in (-26, 26) for lz in (-20, 20)
                   for y in (0, 118)])
_ASC = _rect_mon((XR, ELEV[2], ELEV[0]), (XR, ELEV[2], ELEV[1]), (XR, 0, ELEV[0]), (XR, 0, ELEV[1]))
_LL = beacon_peu()

GEOMETRIA = {
    'things': {
        'furgonetes': {'rect': _FUR, 'walk': _p(-60, ZW - 30)},
        'tecnics': {'rect': _TEC, 'walk': _p(96, ZW - 70)},
        'maquina': {'rect': _MAQ, 'walk': _p(COFFEE_C[0] - 20, COFFEE_C[1] - 80)},
        'ascensor': {'rect': _ASC, 'walk': _p(XR - 50, (ELEV[0] + ELEV[1]) / 2)},
    },
    'spawns': {'iri': _p(-40, 90), 'rius': _p(330, 150)},
    'walkable': _WALK,
    'forats': [_FORAT_TORO],
    'floorSquash': 0.4,
    # L'ombra de contacte: la llum dominant és el dia que entra per la persiana; l'ombra cau cap a la càmera i a la dreta.
    'characterShadow': {'enabled': True, 'color': '#10141c', 'alpha': 0.42, 'squash': 0.38, 'core': 0.6,
                        'light': {'x': _p(-60, ZW + 40)[0], 'y': _p(-60, ZW + 40)[1], 'stretch': 0.7, 'reach': 200}},
    'regions': [{'id': 'perspectiva', 'active': True, 'scaleEnabled': True, 'scaleWalkSpeed': True,
                 'scaleTop': round(_escala_a(_V_FONS - 2), 3), 'scaleBottom': round(_escala_a(_V_PROP + 2), 3),
                 'points': [(0, _V_FONS - 2), (W - 1, _V_FONS - 2), (W - 1, _V_PROP + 2), (0, _V_PROP + 2)]}],
    # la llum de la sala sobre els personatges, en temps d'execució
    'characterLights': {
        'ambient': '#a8acb4',
        'lights': [
            {'x': _p(-40, ZW, 80)[0], 'y': _p(-40, ZW, 80)[1], 'radius': 300, 'color': '#fff0d2', 'intensity': 0.9},  # el dia
            {'x': _p(TUBES[0][0], TUBES[0][1], 160)[0], 'y': max(0, _p(TUBES[0][0], TUBES[0][1], 160)[1]),
             'radius': 260, 'color': '#e0ecff', 'intensity': 0.5},                                             # els tubs
            {'x': _p(TUBES[1][0], TUBES[1][1], 160)[0], 'y': max(0, _p(TUBES[1][0], TUBES[1][1], 160)[1]),
             'radius': 240, 'color': '#e0ecff', 'intensity': 0.5},
            {'x': _p(_LL[0], _LL[2], _LL[1])[0], 'y': _p(_LL[0], _LL[2], _LL[1])[1], 'radius': 70,
             'color': '#ff8c28', 'intensity': 0.6},                                                            # el llum del toro
        ],
    },
}
