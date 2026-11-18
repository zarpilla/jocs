"""
La cuina del pis (Escena 1, la Vet), de nit. EN 3D (hd640/tres_d.py), a 1×.

La càmera és alta i mira de biaix la cantonada del fons a l'esquerra, com a l'estudi (és l'habitació del costat):
  - a la paret de l'esquerra, en escorç, el **taulell** amb volum (la tapa de fusta, els armaris de formica, el
    sòcol enfonsat), els **armaris de dalt** que sobresurten, les rajoles verdes i la **finestra** al pati de llums;
    damunt del taulell, el microones, la cafetera, la pila de **plats** a l'aigüera i el fruiter;
  - a la paret del fons, el **passaplats** (la mateixa obertura que el de l'estudi, vista des de l'altre costat:
    obert, s'hi veu l'estudi, lila i cian), el penjador amb la bomber i la **porta** del pis;
  - la **nevera** separada de la paret i una mica girada (davant, costat i tapa, amb les capses de dalt); oberta,
    la porta gira cap a la càmera i es veu la llum de dins;
  - la **taula** de la cuina, girada, amb les cadires i l'hule a quadres: s'hi passa per darrere;
  - el cubell, la capsa de pizza recolzada, el plat d'en Diu i l'estora de la porta, a terra;
  - el **mosaic hidràulic** del terra, en coordenades del món (les rajoles s'empetiteixen cap al fons);
  - el **llum penjant** al mig: fa el bassal de llum càlida al terra i les ombres; els racons, foscos;
  - primer pla: la bombona de butà, la canonada del gas i el respatller d'una cadira, en silueta.

Tot el detall ve del dibuix pla de sempre (pis_cuina_pla_comu.py), projectat; els decorats (el cable de la
cafetera, la nevera oberta, el passaplats obert) es dibuixen en 3D i en surt la diferència. Damunt de tot, la llum
de Suma Zero (hd640/llum.py): el llum càlid, el cian del passaplats, el bloom i la corba de to.

El món: x a la dreta (0 = la paret del taulell), y amunt (0 = el terra), z cap al fons (300 = la paret del fons);
1 unitat = 1 píxel de sala a la distància on un personatge fa ≈111 px (escala 1).
"""
import functools
import math

import hd640  # noqa: F401  (abans de cap hd.rooms: posa la llibreria a 640×360)
from hd640 import llum
from hd.pix import Canvas, Light, W, H, hr
from hd.rooms.comu import _diff, PLASTIC, SHEET, RED
from hd.rooms.exterior import fbm
from hd640.rooms import pis_cuina_pla_comu as PL
from hd640.rooms.pis_cuina_pla_comu import (PLASTER, CREAM, FRIDGEB, WOOD, STEELB, PORC, TILEF, TERRA, SLATE,
                                            CYANL, BRICKL, FRIDGE_IN, CLOTH, TV_SEQ, TOP_Y)
from hd640.tres_d import Camera, Escena, Llum

BOTTOM = 259                                       # la sala acaba aquí (a sota, la barra de verbs)
ZW = 300                                           # la paret del fons
HW = 200                                           # l'alçada de les parets (el dibuix pla fa 200 fins al terra)
XL = 290                                           # al dibuix pla, fins aquí és la paret del taulell (l'esquerra)
XB0 = 200                                          # al dibuix pla, on comença la paret del fons
XR = 640                                           # on s'acaba la paret del fons (fora de la pantalla)
CX = 40                                            # el fons del taulell (des de la paret)
CTOP = 48                                          # l'alçada del taulell
FRIDGE = (94, 264, 84, 54, 142, 0.07)              # la nevera: x, z del centre, ample, fons, alt, gir
BIN = (156, 280)                                   # el cubell (x, z)
TABLE = (178, 60, 72, 48, 46, 0.38)               # la taula: x, z del centre, ample, fons, alt, gir
WASHER = (478, 268, 56, 50, 62, -0.1)              # la rentadora, al costat de la porta: x, z, ample, fons, alt, gir
LAMPP = (214, 150, 168)                            # la bombeta del llum penjant
DIU = (214, 196)                                    # el plat d'en Diu (x, z)


def _wz(fx):
    """Una x del dibuix pla de la paret del taulell → la z del món."""
    return ZW - XL + fx


def _wx(fx):
    """Una x del dibuix pla de la paret del fons → la x del món."""
    return fx - XB0


def _y(fy):
    """Una y del dibuix pla (el terra, a 200) → l'alçada del món."""
    return HW - fy


HATCH = (_wx(PL.HATCH[0]), _wx(PL.HATCH[2]), _y(PL.HATCH[3]), _y(PL.HATCH[1]))      # x0, x1, y0, y1
WIN = (_wz(PL.WINDOW[0]), _wz(PL.WINDOW[2]), _y(PL.WINDOW[3]), _y(PL.WINDOW[1]))   # z0, z1, y0, y1
DOOR = (_wx(552), _wx(626), 0, _y(51))
SOCKET = (_wz(128), _y(137))                                                        # l'endoll de la cafetera (z, y)

CAM = Camera(pos=(410, 200, -240), yaw=-0.42, pitch=0.2, f=470, centre=(320, 84))

LIGHT = Light(ambient=0.0, vignette=None, floor_fade=None)  # (la llum és la del món: la de l'Escena)
TEXL = Light(ambient=-0.2, vignette=None, floor_fade=None)  # la dels dibuixos plans (les textures): neutra
HATCH_C = ((HATCH[0] + HATCH[1]) / 2, (HATCH[2] + HATCH[3]) / 2, ZW)
LLUMS = [Llum(LAMPP, 360, 3.0, power=1.25),                                     # el llum penjant
         Llum((HATCH_C[0], HATCH_C[1], ZW - 6), 80, 0.7, power=1.6),            # el passaplats (les pantalles)
         Llum((4, (WIN[2] + WIN[3]) / 2, (WIN[0] + WIN[1]) / 2), 90, 0.5)]      # la finestra


def _llums(estat):
    out = list(LLUMS)
    if 'obert' in estat:
        out.append(Llum((HATCH_C[0], HATCH_C[1], ZW - 4), 170, 1.4, power=1.3))
    if 'nevera' in estat:
        fx, fz, fw, fd, fh, fa = FRIDGE
        out.append(Llum((fx, 70, fz - fd / 2 - 6), 120, 0.9, power=1.5))
    return out


# ─── Les textures: el dibuix pla de sempre ───────────────────────────────────

def _paret_esq(rain=0, tv=None):
    """La paret del taulell, de cara: arrebossat, les rajoles verdes (amb l'endoll) i la finestra."""
    cv = Canvas(light=TEXL)
    PL.wall(cv)
    PL.backsplash(cv)
    PL.window(cv, rain=rain, tv=tv)
    return cv.img


def _paret_fons():
    """La paret del fons, de cara: arrebossat, el passaplats, el penjador i la porta."""
    cv = Canvas(light=TEXL)
    PL.wall(cv)
    PL.hatch(cv)
    PL.coats(cv)
    PL.door(cv)
    return cv.img


def _mobles(led=False, rellotge=True, nevera=False):
    """Els mobles i les coses de damunt, dibuixats plans sobre transparent (en surten els retalls)."""
    cv = Canvas(light=TEXL, transparent=True)
    PL.upper_cabinets(cv)
    PL.counter(cv)
    PL.microwave(cv)
    PL.cafetera(cv)
    PL.sink(cv)
    PL.fruit_bowl(cv)
    PL.fridge(cv)
    PL.floor_things(cv)
    if nevera:
        PL.nevera_oberta(cv)
    if led:                                                       # la placa de la cafetera, encesa
        cv.rect(81, TOP_Y, 84, TOP_Y + 1, [(255, 60, 40)], 0, lit=0)
    if not rellotge:                                              # el 00:00 del microones, apagat
        cv.rect(*PL.CLOCK, [(8, 16, 10), (14, 26, 16)], 0.6, lit=0)
    return cv.img


def _llum_penjant():
    """La pantalla del llum, de vidre ambre, amb la bombeta (sense el halo: el fa la llum)."""
    cv = Canvas(light=TEXL, transparent=True)
    lx, ly = PL.LAMP
    cv.rect(lx - 3, ly - 20, lx + 3, ly - 17, STEELB, 3.0, lit=0)
    shade = [(lx - 5, ly - 17), (lx + 5, ly - 17), (lx + 16, ly - 4), (lx + 16, ly - 1), (lx - 16, ly - 1), (lx - 16, ly - 4)]
    cv.poly(shade, PL.GLASSA, lambda x, y: 2.0 + (y - ly + 17) * 0.16 + (1.2 if x < lx - 4 else 0)
            + (0.6 if (x - lx) % 5 == 0 else 0), lit=0)
    PL.outline_poly(cv, shade, PL.GLASSA)
    cv.hline(lx - 15, lx + 15, ly - 1, PL.LEMON, 5.0, lit=0)
    cv.disc(lx, ly + 1, 4, 3, PL.LEMON, 5.6, lit=0)
    return cv.img.crop((lx - 17, ly - 21, lx + 18, ly + 5))


def _pizza():
    cv = Canvas(light=TEXL, transparent=True)
    PL.pizza_nevera(cv)
    return cv.img


def _tonyina():
    cv = Canvas(light=TEXL, transparent=True)
    PL.tonyina(cv)
    return cv.img


T = 24                                             # el costat d'una rajola del mosaic


def _terra_tex():
    """El mosaic hidràulic, vist des de dalt: un píxel per unitat del món, x de 0 a XR i z de ZW a -60.
    Rajola crema amb un cercle i quarts de cercle terracota, juntes fosques i el desgast de cada peça."""
    cv = Canvas(XR, ZW + 60, light=TEXL)
    for j in range(ZW + 60):
        z = ZW - j
        for x in range(XR):
            fu, fv = (x / T) % 1.0, (z / T) % 1.0
            if fu < 0.05 or fv < 0.05:
                cv.put(x, j, SLATE, 1.6)                                     # la junta
                continue
            tu, tv = int(x // T), int(z // T)
            wear = (hr(tu, tv) - 0.5) * 0.5 + (hr(x // 2, z // 2) - 0.5) * 0.25 + (fbm(x / 70, z / 50, 5) - 0.5) * 0.8
            dc = math.hypot(fu - 0.5, fv - 0.5)
            dk = min(math.hypot(fu - a, fv - b) for a in (0, 1) for b in (0, 1))
            if hr(tu, tv, 31) > 0.93 and abs(fu - fv) < 0.03:
                cv.put(x, j, TILEF, 0.8)                                     # una rajola esquerdada
            elif 0.25 < dc < 0.32:
                cv.put(x, j, TERRA, 1.9 + wear)
            elif dk < 0.18:
                cv.put(x, j, SLATE, 2.2 + wear)
            elif dc < 0.08:
                cv.put(x, j, TERRA, 1.8 + wear)
            else:
                cv.put(x, j, TILEF, 3.0 + wear)
    return cv.img


@functools.lru_cache(maxsize=None)
def _textures():
    return {'esq': _paret_esq(), 'fons': _paret_fons(), 'mobles': _mobles(), 'terra': _terra_tex(),
            'llum': _llum_penjant()}


# ─── Les superfícies ────────────────────────────────────────────────────────

def _arrebossat(lvl0, seed=3):
    """L'arrebossat mostassa, en coordenades del món (on el dibuix pla no arriba)."""
    def L(s, t, P):
        v = lvl0 + (hr(int(s // 3), int(t // 3), seed) - 0.5) * 0.35 + (hr(int(s // 15), int(t // 12), seed + 4) - 0.5) * 0.4
        if t > HW - 8:
            v = 2.2 if t > HW - 7 else 3.4                     # el sòcol de fusta (el pinta WOOD? no: to fosc)
        return v
    return L


def _carta(e, sid, img, box, x, dy=0.0, dz=0.0):
    """Un dibuix pla dret damunt el taulell, girat com la paret (de cara a +x): `box` = el retall del dibuix pla."""
    fx0, fy0, fx1, fy1 = box
    z0, z1 = _wz(fx0) + dz, _wz(fx1) + dz
    y0, y1 = _y(fy0) + dy, _y(fy1) + dy
    return e.quad(sid, (x, y0, z0), (x, y0, z1), (x, y1, z1), (x, y1, z0), tex=(img, box))


def _en_caixa(cx, cz, ang):
    c, s_ = math.cos(ang), math.sin(ang)

    def P(lx, y, lz):
        return (cx + lx * c - lz * s_, y, cz + lx * s_ + lz * c)
    return P


def _ombra(e, sid, cx, cz, rx, rz, k=0.55, dx=0.0, dz=0.0):
    """Una ombra el·líptica al terra (amb un desplaçament: la llum del llum la tira cap enfora)."""
    cx, cz = cx + dx, cz + dz
    e.foscor(sid, (cx - rx, 0.6, cz + rz), (cx + rx, 0.6, cz + rz), (cx + rx, 0.6, cz - rz), (cx - rx, 0.6, cz - rz),
             lambda s, t: k * min(1.0, max(0.0, 1 - ((s - rx) / rx) ** 2 - ((t - rz) / rz) ** 2) * 1.6))


def _lluny(x, z):
    """Cap on tira l'ombra el llum penjant: el desplaçament d'una ombra a (x, z), en unitats."""
    dx, dz = x - LAMPP[0], z - LAMPP[2]
    d = math.hypot(dx, dz) or 1
    k = min(16.0, d * 0.12)
    return dx / d * k, dz / d * k


FOSC = [(4, 3, 4), (9, 6, 6), (16, 11, 9), (24, 17, 13), (33, 24, 18), (44, 32, 24)]
HULE = [(24, 6, 8), (52, 12, 14), (90, 24, 24), (128, 42, 36), (164, 76, 60), (190, 160, 136)]


def escena(cv, tex, estat=frozenset()):
    """Tota la sala, de lluny a prop. `estat`: els decorats que hi són ('cable', 'nevera', 'obert'). → l'Escena."""
    e = Escena(cv, CAM, _llums(estat), ambient=-0.5)
    zn = CAM.pos[2] + 60
    esq, fons, mob = tex['esq'], tex['fons'], tex['mobles']
    hx0, hx1, hy0, hy1 = HATCH
    obert = 'obert' in estat
    # el passaplats obert: a l'altra banda, l'estudi (maó lila, el terra fosc i la llum cian de les pantalles)
    if obert:
        zs = ZW + 12                                                       # el gruix de la paret
        e.quad('estudi', (hx0 - 80, HW, ZW + 260), (hx1 + 80, HW, ZW + 260), (hx1 + 80, 0, ZW + 260),
               (hx0 - 80, 0, ZW + 260), ramp=BRICKL,
               lvl=lambda s, t, P: (1.8 if int(t) % 9 == 8 or int(s + (12 if int(t // 9) % 2 else 0)) % 24 == 0 else 3.4)
               + (hr(int((s + (12 if int(t // 9) % 2 else 0)) // 24), int(t // 9), 5) - 0.5) * 0.6)
        e.quad('estudi', (hx0 - 80, 0, ZW + 260), (hx1 + 80, 0, ZW + 260), (hx1 + 80, 0, zs), (hx0 - 80, 0, zs),
               ramp=SLATE, lvl=lambda s, t, P: 1.6 - (0.8 if int(s) % 26 == 0 else 0))
        e.claror((hx0 - 80, HW, ZW + 259), (hx1 + 80, HW, ZW + 259), (hx1 + 80, 0, ZW + 259), (hx0 - 80, 0, ZW + 259),
                 (60, 210, 200), lambda s, t: 0.6 * max(0.0, 1 - math.hypot(s - 120, t - 120) / 120))
        # els brancals i l'ampit (el gruix de la paret), de fusta
        e.quad('passaplats', (hx0, hy1, ZW), (hx0, hy1, zs), (hx0, hy0, zs), (hx0, hy0, ZW), ramp=WOOD, lvl=2.2)
        e.quad('passaplats', (hx1, hy1, zs), (hx1, hy1, ZW), (hx1, hy0, ZW), (hx1, hy0, zs), ramp=WOOD, lvl=1.6)
        e.quad('passaplats', (hx0, hy0, zs), (hx1, hy0, zs), (hx1, hy0, ZW), (hx0, hy0, ZW), ramp=WOOD, lvl=3.0)

    def forat(s, t):
        return not (hx0 + 3 < s < hx1 - 3 and HW - hy1 + 3 < t < HW - hy0 - 3)
    # la paret del taulell (x = 0): de prop, arrebossat; cap a la cantonada, el dibuix pla
    e.quad('paret_esq_prop', (0, HW, zn), (0, HW, ZW - XL), (0, 0, ZW - XL), (0, 0, zn), ramp=PLASTER, lvl=_arrebossat(2.0))
    e.quad('paret_esq', (0, HW, ZW - XL), (0, HW, ZW), (0, 0, ZW), (0, 0, ZW - XL), tex=(esq, (0, 0, XL, HW)))
    # la paret del fons (z = 300): el dibuix pla (x 236..640) i, a la dreta, més arrebossat
    e.quad('paret_fons', (0, HW, ZW), (W - XB0, HW, ZW), (W - XB0, 0, ZW), (0, 0, ZW), tex=(fons, (XB0, 0, W, HW)),
           forma=forat if obert else None)
    e.quad('paret_fons_dreta', (W - XB0, HW, ZW), (XR, HW, ZW), (XR, 0, ZW), (W - XB0, 0, ZW), ramp=PLASTER,
           lvl=_arrebossat(2.6, seed=5))
    # el terra: el mosaic hidràulic
    e.quad('terra', (0, 0, ZW), (XR, 0, ZW), (XR, 0, -60), (0, 0, -60), tex=(tex['terra'], (0, 0, XR, ZW + 60)))
    # el bassal de llum càlida sota el llum, el cian del passaplats i la claror freda de la finestra
    e.claror((LAMPP[0] - 200, 0.3, LAMPP[2] + 200), (LAMPP[0] + 200, 0.3, LAMPP[2] + 200),
             (LAMPP[0] + 200, 0.3, LAMPP[2] - 200), (LAMPP[0] - 200, 0.3, LAMPP[2] - 200), (255, 196, 120),
             lambda s, t: 0.22 * max(0.0, 1 - math.hypot(s - 200, t - 200) / 190) ** 1.4)
    e.claror((hx0 - 40, 0.4, ZW), (hx1 + 40, 0.4, ZW), (hx1 + 60, 0.4, ZW - 90), (hx0 - 60, 0.4, ZW - 90),
             (70, 200, 210), lambda s, t: (0.32 if obert else 0.14) * max(0.0, 1 - abs(s - 65) / 70) * max(0.0, 1 - t / 90))
    # lluny del llum, el terra s'enfosqueix (el bassal de llum)
    e.foscor('penombra', (0, 0.35, ZW), (XR, 0.35, ZW), (XR, 0.35, -60), (0, 0.35, -60),
             lambda s, t: 0.55 * min(1.0, max(0.0, math.hypot(s - LAMPP[0], ZW - t - LAMPP[2]) - 110) / 230))
    # la foscor dels racons
    e.foscor('racons', (0, 0.5, ZW), (XR, 0.5, ZW), (XR, 0.5, zn), (0, 0.5, zn),
             lambda s, t: max(0.5 * max(0.0, 1 - t / 26), 0.4 * max(0.0, 1 - s / 50)))
    e.foscor('cantonada', (0, HW, ZW - 0.5), (70, HW, ZW - 0.5), (70, 0, ZW - 0.5), (0, 0, ZW - 0.5),
             lambda s, t: 0.5 * max(0.0, 1 - s / 70))
    e.foscor('sostre_fosc', (0, HW - 0.5, ZW - 0.6), (XR, HW - 0.5, ZW - 0.6), (XR, 0, ZW - 0.6), (0, 0, ZW - 0.6),
             lambda s, t: 0.55 * max(0.0, 1 - t / 70))
    e.foscor('sostre_fosc', (0.5, HW, zn), (0.5, HW, ZW), (0.5, 0, ZW), (0.5, 0, zn),
             lambda s, t: 0.55 * max(0.0, 1 - t / 70))
    # l'estora de la porta
    d0, d1 = DOOR[0] + 4, DOOR[1] - 4
    e.quad('estora', (d0, 0.4, ZW - 4), (d1, 0.4, ZW - 4), (d1 + 2, 0.4, ZW - 26), (d0 - 2, 0.4, ZW - 26),
           ramp=[(20, 14, 10), (40, 30, 20), (64, 48, 30), (90, 70, 44), (120, 96, 60)],
           lvl=lambda s, t, P: 2.4 + (0.8 if (int(s) + int(t)) % 4 == 0 else 0) - (1.2 if s < 2 or t > 20 else 0))
    # el taulell: els armaris de sota (el davant, el dibuix pla), la tapa de fusta i l'aigüera
    z0, z1 = _wz(14), ZW - 2
    e.foscor('ombra_taulell', (CX, 0.6, z1), (CX + 18, 0.6, z1), (CX + 18, 0.6, z0), (CX, 0.6, z0),
             lambda s, t: 0.55 * max(0.0, 1 - s / 18))
    e.caixa('taulell', 0, CX - 3, 0, CTOP - 4, z0 + 2, z1, CREAM, 2.0,
            cares={'dreta': {'tex': (mob, (14, 166, 280, 220))}, 'davant': {'ramp': CREAM, 'lvl': 2.4}})
    e.caixa('taulell', 0, CX + 1, CTOP - 4, CTOP, z0, z1 + 2, WOOD, 3.0,
            cares={'dalt': {'ramp': WOOD, 'lvl': lambda s, t, P: 3.4 + (hr(int(t // 6), 1) - 0.5) * 0.3
                            + (fbm(s / 8, t / 40, 3) - 0.5) * 0.5 - (0.8 if s > CX - 1 else 0)},
                   'dreta': {'ramp': WOOD, 'lvl': lambda s, t, P: 4.0 if t < 1 else 2.4},
                   'davant': {'ramp': WOOD, 'lvl': 2.6}})
    sz0, sz1 = _wz(149), _wz(227)
    e.quad('aiguera', (5, CTOP + 0.2, sz1), (CX - 6, CTOP + 0.2, sz1), (CX - 6, CTOP + 0.2, sz0), (5, CTOP + 0.2, sz0),
           ramp=STEELB, lvl=lambda s, t, P: 3.4 if (s < 1.5 or s > CX - 12.5 or t < 1.5 or t > sz1 - sz0 - 1.5)
           else (3.0 if abs(t - 39) < 1 else 1.4 + s * 0.04))
    # els armaris de dalt, que sobresurten de la paret
    e.foscor('ombra_armaris', (0.5, _y(89), _wz(150)), (0.5, _y(89), _wz(18)), (0.5, _y(89) - 26, _wz(18)),
             (0.5, _y(89) - 26, _wz(150)), lambda s, t: 0.6 * max(0.0, 1 - t / 26))
    e.caixa('armaris', 0, 30, _y(89), _y(27), _wz(19), _wz(134), CREAM, 2.6,
            cares={'dreta': {'tex': (mob, (19, 27, 134, 89))}, 'dalt': {'ramp': CREAM, 'lvl': 3.0},
                   'davant': {'ramp': CREAM, 'lvl': 2.2}})
    _carta(e, 'armaris', mob, (31, 10, 55, 28), 14)                           # el pot de galetes
    _carta(e, 'armaris', mob, (106, 0, 115, 28), 14)                          # l'ampolla de vi buida
    # el microones (una caixa amb el davant dibuixat), la cafetera, la tassa, els plats i el fruiter
    e.caixa('microones', 4, 34, _y(154), _y(125), _wz(21), _wz(68), PLASTIC, 1.6,
            cares={'dreta': {'tex': (mob, (21, 125, 68, 155))}, 'dalt': {'ramp': PLASTIC, 'lvl': 2.6}})
    if 'cable' in estat:
        e.cable('cable', [(24, CTOP + 0.8, _wz(110)), (24, CTOP + 0.8, _wz(118)), (12, CTOP + 0.8, SOCKET[0] - 2),
                          (4, CTOP + 3, SOCKET[0]), (1.2, SOCKET[1] - 2, SOCKET[0])],
                [(30, 28, 26), (80, 76, 70), (140, 134, 124), (196, 190, 178)], 2.4, gruix=1.6)
        e.caixa('cable', 0.5, 3.5, SOCKET[1] - 5, SOCKET[1] + 1, SOCKET[0] - 3, SOCKET[0] + 3, PLASTIC, 2.6)
    _carta(e, 'cafetera', mob, (76, 115, 114, 154), 18)
    _carta(e, 'cafetera', mob, (119, 143, 132, 153), 26)
    _carta(e, 'plats', mob, (145, 118, 242, 160), 20)
    _carta(e, 'fruiter', mob, (241, 135, 273, 153), 22)
    # el cubell i la capsa de pizza recolzada
    bx, bz = BIN
    _ombra(e, 'ombra_cubell', bx, bz, 18, 14, 0.5, *_lluny(bx, bz))
    e.caixa('cubell', bx - 13, bx + 13, 0, 43, bz - 13, bz + 13, STEELB, 2.6,
            cares={'davant': {'tex': (mob, (411, 171, 438, 214))}, 'dalt': {'ramp': STEELB, 'lvl': 4.0},
                   'dreta': {'ramp': STEELB, 'lvl': lambda s, t, P: 1.8 - (0.6 if int(s) % 5 == 0 else 0)}})
    e.quad('pizza_vella', (bx + 16, 33, ZW - 2), (bx + 44, 33, ZW - 2), (bx + 44, 0, ZW - 12), (bx + 16, 0, ZW - 12),
           tex=(mob, (440, 184, 468, 217)))
    # la nevera, separada de la paret i una mica girada, amb les capses de dalt
    fx, fz, fw, fd, fh, fa = FRIDGE
    P = _en_caixa(fx, fz, fa)
    _ombra(e, 'ombra_nevera', fx, fz - 4, fw / 2 + 10, fd / 2 + 10, 0.6, *_lluny(fx, fz))
    davant = {'tex': (tex.get('nevera', mob), (293, 67, 377, 212))}
    e.caixa_girada('nevera', fx, fz, fw, fd, fh, fa, FRIDGEB, 3.0,
                   cares={'davant': davant, 'dalt': {'ramp': FRIDGEB, 'lvl': 4.2},
                          'dreta': {'ramp': FRIDGEB, 'lvl': lambda s, t, P: 2.4 - (0.8 if t > fh - 4 else 0)
                                    - (0.4 if int(s) % 18 == 0 else 0)},
                          'esquerra': {'ramp': FRIDGEB, 'lvl': 2.0}})
    top = P(0, fh, -4)
    e.sprite('nevera_dalt', mob.crop((299, 43, 367, 67)), (34, 23), top)
    if 'nevera' in estat:
        # la porta de baix, oberta cap a la càmera (la frontissa és a la dreta)
        hinge = P(fw / 2, 0, -fd / 2)
        th = math.radians(128)
        ang = fa + math.atan2(-math.sin(th), -math.cos(th))
        dl = fw - 4
        cxd = hinge[0] + math.cos(ang) * dl / 2
        czd = hinge[2] + math.sin(ang) * dl / 2
        hp = fh * (211 - 97) / 145

        def balconets(s, t, P_):
            if t < 3 or t > hp - 3 or s < 3 or s > dl - 3:
                return 4.4
            if int(t) % 30 in (0, 1, 2):
                return 5.4                                                   # els balconets
            if int(t) % 30 > 18 and int(s) % 12 in range(3, 8):
                return 2.0 + (int(s) // 12) % 3                              # les ampolles
            return 3.4
        e.caixa_girada('porta_nevera', cxd, czd, dl, 6, hp, ang, FRIDGEB, 3.6,
                       cares={'davant': {'ramp': FRIDGE_IN, 'lvl': balconets}, 'dalt': {'ramp': FRIDGEB, 'lvl': 5.0},
                              'darrere': {'ramp': FRIDGEB, 'lvl': 2.6}})
        e.claror(P(-fw / 2 - 30, 0.5, -fd / 2), P(fw / 2 + 40, 0.5, -fd / 2), P(fw / 2 + 40, 0.5, -fd / 2 - 90),
                 P(-fw / 2 - 30, 0.5, -fd / 2 - 90), (230, 246, 240),
                 lambda s, t: 0.35 * max(0.0, 1 - abs(s - 72) / 80) * max(0.0, 1 - t / 90))
    _rentadora(e, estat)
    # el plat d'en Diu, a terra (vermell, amb el pinso)
    dx, dz = DIU
    e.quad('plat_diu', (dx - 13, 0.8, dz + 13), (dx + 13, 0.8, dz + 13), (dx + 13, 0.8, dz - 13), (dx - 13, 0.8, dz - 13),
           ramp=RED, lvl=lambda s, t, P: 3.4 - (t - 13) * 0.06 - (1.2 if math.hypot(s - 13, t - 13) > 11.5 else 0),
           forma=lambda s, t: math.hypot(s - 13, t - 13) < 13)
    e.quad('plat_diu', (dx - 8, 1.6, dz + 8), (dx + 8, 1.6, dz + 8), (dx + 8, 1.6, dz - 8), (dx - 8, 1.6, dz - 8),
           ramp=[(30, 20, 10), (60, 40, 20), (90, 64, 30), (120, 88, 44)],
           lvl=lambda s, t, P: 1.8 + (1.2 if hr(int(s), int(t), 7) > 0.7 else 0),
           forma=lambda s, t: math.hypot(s - 8, t - 8) < 8)
    # el passaplats obert: les portetes, la de dalt girada amunt i la de baix abatuda (fa de lleixa)
    if obert:
        for (ya, k) in ((hy1, 1), (hy0, -1)):
            def fulla(s, t, P_):
                if s < 3 or s > hx1 - hx0 - 3 or t < 3 or t > 25:
                    return 3.0
                return 2.0 + (0.6 if int(s - t) % 9 == 0 else 0)
            e.quad('portetes', (hx0 + 1, ya, ZW - 28), (hx1 - 1, ya, ZW - 28), (hx1 - 1, ya, ZW - 0.5),
                   (hx0 + 1, ya, ZW - 0.5), ramp=CYANL if k > 0 else WOOD, lvl=fulla, dues_cares=True)
            e.caixa('portetes', hx0 + 1, hx1 - 1, ya - 2, ya, ZW - 28, ZW - 0.5, WOOD, 2.4,
                    cares={'dalt': {'ramp': CYANL, 'lvl': fulla}} if k > 0 else None)
    # la taula de la cuina, girada, amb l'hule a quadres, i les dues cadires
    tx, tz, tw, td, th_, ta = TABLE
    PT = _en_caixa(tx, tz, ta)
    _ombra(e, 'ombra_taula', tx, tz, tw / 2 + 10, td / 2 + 10, 0.55, *_lluny(tx, tz))
    _cadira(e, 'cadira_fons', *_off(PT, 0, td / 2 + 12), ta + math.pi)
    for lx in (-tw / 2 + 4, tw / 2 - 4):
        for lz in (-td / 2 + 4, td / 2 - 4):
            q = PT(lx, 0, lz)
            e.caixa('taula', q[0] - 1.6, q[0] + 1.6, 0, th_ - 4, q[2] - 1.6, q[2] + 1.6, STEELB, 3.0)

    def hule(s, t, P_):
        cx_, cz_ = int(s // 8), int(t // 8)
        v = 3.4 if (cx_ + cz_) % 2 else (2.2 if cx_ % 2 else 4.2)
        return v + (fbm(s / 20, t / 20, 9) - 0.5) * 0.6
    e.caixa_girada('taula', tx, tz, tw, td, 4, ta, HULE, 3.0, y0=th_ - 4,
                   cares={'dalt': {'ramp': HULE, 'lvl': hule},
                          'davant': {'ramp': HULE, 'lvl': lambda s, t, P_: 2.4 if t < 2 else 4.4 if int(s) % 8 < 4 else 2.0},
                          'esquerra': {'ramp': HULE, 'lvl': 2.6}, 'dreta': {'ramp': HULE, 'lvl': 2.2}})
    # damunt la taula: el llibre de la Vet, obert, i una tassa
    e.quad('taula', PT(-20, th_ + 0.3, 6), PT(4, th_ + 0.3, 6), PT(4, th_ + 0.3, -10), PT(-20, th_ + 0.3, -10),
           ramp=SHEET, lvl=lambda s, t, P_: 4.0 - (1.4 if abs(s - 12) < 0.8 else 0) - (0.8 if int(t) % 3 == 0 and 2 < s < 22 and s != 12 else 0))
    q = PT(18, th_, -6)
    e.caixa('taula', q[0] - 3.5, q[0] + 3.5, th_, th_ + 8, q[2] - 3.5, q[2] + 3.5, PORC, 3.6,
            cares={'dalt': {'ramp': [(20, 10, 6), (40, 22, 12)], 'lvl': 1.0}})
    _cadira(e, 'cadira', *_off(PT, -tw / 2 - 13, 2), ta + math.pi / 2 + 0.15)
    # el llum penjant: el fil des del sostre i la pantalla
    lt = tex['llum']
    e.cable('llum', [(LAMPP[0], HW, LAMPP[2]), (LAMPP[0], LAMPP[1] + 20, LAMPP[2])], SLATE, 2.0, gruix=1.0)
    e.sprite('llum', lt, (17, 22), LAMPP)
    # primer pla: la bombona de butà, la canonada del gas i una cadira, en silueta
    BUTA = [(6, 2, 2), (16, 6, 4), (30, 12, 6), (50, 22, 8), (76, 34, 12), (104, 50, 18)]
    e.tub('primer_pla', (12, 0, -4), (12, 48, -4), 17, BUTA, 2.4, llum_dir=(0.8, -0.5))
    e.tub('primer_pla', (12, 48, -4), (12, 60, -4), 7, FOSC, 2.4, llum_dir=(0.8, -0.5))
    e.tub('primer_pla', (446, 0, -22), (446, HW, -22), 4.5, FOSC, 1.8, brides=50, llum_dir=(-0.8, 0.3))   # el gas
    _cadira(e, 'primer_pla', 462, 40, -0.5, fosc=True)
    return e


def _rentadora(e, estat):
    """La rentadora, al costat de la porta, una mica separada i girada: l'ull de bou, el tauler i el sabó a dalt."""
    wx, wz, ww, wd, wh, wa = WASHER
    _ombra(e, 'ombra_rentadora', wx, wz - 4, ww / 2 + 8, wd / 2 + 8, 0.55, *_lluny(wx, wz))

    def davant(s, t, P_):
        r = math.hypot(s - ww / 2, t - 36)
        if t < 12:
            return 4.6 if int(s) % 9 == 0 and 30 < s < 50 else (3.8 if 6 < s < 20 and 4 < t < 8 else 5.4)
        if r < 12:
            return 1.6 + (2.4 if abs(s - ww / 2 + 4) < 2 and t < 32 else 0)        # el vidre de l'ull de bou
        if r < 15:
            return 6.4 - (t - 21) * 0.08                                           # la goma i l'anella
        return 5.2 - t * 0.02 - (1.0 if t > wh - 4 else 0)
    e.caixa_girada('rentadora', wx, wz, ww, wd, wh, wa, PORC, 3.0,
                   cares={'davant': {'ramp': PORC, 'lvl': lambda s, t, P_: davant(s, t, P_) - 1.4},
                          'dalt': {'ramp': PORC, 'lvl': 4.0}, 'esquerra': {'ramp': PORC, 'lvl': 2.0}})
    P = _en_caixa(wx, wz, wa)
    q = P(-10, 0, 4)
    e.caixa('rentadora', q[0] - 8, q[0] + 8, wh, wh + 18, q[2] - 5, q[2] + 5, CLOTH[1], 2.6,
            cares={'davant': {'ramp': CLOTH[1], 'lvl': lambda s, t, P_: 3.4 if 4 < t < 10 else 2.2}})


def _off(PT, lx, lz):
    p = PT(lx, 0, lz)
    return p[0], p[2]


def _cadira(e, sid, cx, cz, ang, fosc=False):
    """Una cadira de cuina (de fusta, el seient de skai): les potes, el seient i el respatller."""
    P = _en_caixa(cx, cz, ang)
    rm, rs = (FOSC, FOSC) if fosc else (WOOD, [(20, 6, 8), (46, 12, 14), (80, 22, 24), (116, 38, 34), (150, 64, 52)])
    if not fosc:
        _ombra(e, 'ombra_' + sid, cx, cz, 18, 16, 0.5, *_lluny(cx, cz))
    for lx in (-13, 13):
        for lz in (-13, 13):
            q = P(lx, 0, lz)
            e.caixa(sid, q[0] - 1.4, q[0] + 1.4, 0, 28, q[2] - 1.4, q[2] + 1.4, rm, 2.4)
    e.caixa_girada(sid, cx, cz, 32, 32, 4, ang, rs, 2.8, y0=28,
                   cares={'dalt': {'ramp': rs, 'lvl': lambda s, t, P_: 3.0 - abs(s - 16) * 0.03 - abs(t - 16) * 0.03}})
    for lx in (-13, 13):
        q = P(lx, 0, 14)
        e.caixa(sid, q[0] - 1.4, q[0] + 1.4, 32, 64, q[2] - 1.4, q[2] + 1.4, rm, 2.4)
    q = P(0, 0, 14)
    e.caixa_girada(sid, q[0], q[2], 30, 3, 10, ang, rm, 2.8, y0=52)


# ─── Composició i llum ──────────────────────────────────────────────────────

def _proj(P):
    u, v, _ = CAM.projecta(P)
    return u, v


def _fx(estat=frozenset()):
    lx, ly = _proj(LAMPP)
    hx, hy = _proj(HATCH_C)
    wx, wy = _proj((0, (WIN[2] + WIN[3]) / 2, (WIN[0] + WIN[1]) / 2))
    light = [llum.wash(lx, ly + 60, 300, (255, 190, 110), k=0.9, air=0.05, squash=0.8),        # el llum, càlid
             llum.wash(lx, ly + 2, 40, (255, 220, 150), k=0.6, air=0.25, squash=1.0),          # la bombeta
             llum.wash(hx, hy + 20, 90 if 'obert' in estat else 60, (80, 220, 220),
                       k=0.8 if 'obert' in estat else 0.5, air=0.06),                          # el passaplats, cian
             llum.wash(wx, wy, 90, (120, 150, 220), k=0.5, air=0.04, squash=0.8)]              # la finestra, freda
    if 'nevera' in estat:
        fx, fz, fw, fd, fh, fa = FRIDGE
        nx, ny = _proj((fx, 60, fz - fd / 2))
        light.append(llum.wash(nx, ny + 30, 110, (200, 236, 255), k=0.35, air=0.05, squash=0.9))
    tone = [llum.grade(contrast=1.1, pivot=40, sat=1.15, lift=(8, 4, 2))]
    bloom = [llum.bloom(thr=150)]
    return light, bloom, tone


def _render(estat=frozenset(), tex=None):
    cv = Canvas(light=LIGHT)
    e = escena(cv, tex or _textures(), estat)
    cv.rect(0, BOTTOM + 1, W - 1, H - 1, [(0, 0, 0)], 0, lit=0)    # la barra de verbs: negre
    return cv.img, e


@functools.lru_cache(maxsize=None)
def _base():
    return _render()


def _amb_llum(img, estat=frozenset(), bloom=True):
    light, bl, tone = _fx(estat)
    return llum.apply(img, light + (bl if bloom else []) + tone)


@functools.lru_cache(maxsize=None)
def _base_llum():
    return _amb_llum(_base()[0])


def bg(cv):
    cv.img.paste(_base_llum())
    cv.P = cv.img.load()


def _tex(**kw):
    t = dict(_textures())
    t.update(kw)
    return t


@functools.lru_cache(maxsize=None)
def _estat(*estat):
    """La sala amb aquells decorats: (imatge crua, Escena)."""
    tex = _tex(mobles=_mobles(led='cable' in estat)) if 'cable' in estat else _textures()
    if 'nevera' in estat:
        tex = _tex(nevera=_mobles(nevera=True))
    return _render(frozenset(estat), tex)


def _decorat(*estat):
    """Un decorat: la sala amb aquell estat, menys la de sempre (només el que canvia), amb la llum."""
    def draw(cv):
        img, _ = _estat(*estat)
        out = _diff(_amb_llum(img, frozenset(estat), bloom=False), _amb_llum(_base()[0], bloom=False))
        cv.img.alpha_composite(out)
        cv.P = cv.img.load()
    return draw


def _dins_nevera(flat):
    """Una cosa de dins la nevera (la pizza, la tonyina): dibuixada plana i projectada pel davant de la nevera
    oberta, damunt del decorat `nevera_oberta`."""
    def draw(cv):
        img, e = _estat('nevera')
        capa = e.capa(flat(), {'nevera'})
        top = img.copy()
        top.alpha_composite(capa)
        st = frozenset({'nevera'})
        cv.img.alpha_composite(_diff(_amb_llum(top, st, bloom=False), _amb_llum(img, st, bloom=False)))
        cv.P = cv.img.load()
    return draw


PROPS = {
    'passaplats_obert': _decorat('obert'),
    'cable_cafetera': _decorat('cable'),
    'nevera_oberta': _decorat('nevera'),
    'pizza_nevera': _dins_nevera(_pizza),
    'tonyina': _dins_nevera(_tonyina),
}


# ─── Animacions ─────────────────────────────────────────────────────────────

def _fotograma(capes):
    """El fons amb unes capes damunt, amb la llum, menys el fons amb la llum."""
    img, _ = _base()
    img = img.copy()
    for c in capes:
        img.alpha_composite(c)
    return _diff(_amb_llum(img), _base_llum())


def _frames():
    """La pluja al vidre de la finestra."""
    _, e = _base()
    return [_fotograma([e.capa(_paret_esq(rain=i), {'paret_esq'})]) for i in range(8)]


def _frames_tele():
    """A l'altra banda del pati, la tele del veí canvia de color amb els plans de la pel·lícula."""
    _, e = _base()
    return [_fotograma([e.capa(_paret_esq(tv=None if (col, k) == TV_SEQ[0] else (col, k)), {'paret_esq'})])
            for col, k in TV_SEQ]


def _frames_rellotge():
    """El 00:00 del microones parpelleja (ningú l'ha posat en hora des de l'últim tall de llum)."""
    _, e = _base()
    off = _fotograma([e.capa(_mobles(rellotge=False), {'microones'})])
    return [_diff(_base_llum(), _base_llum()), off]


ANIMS = {
    'pluja': {'frames': _frames, 'frameDuration': 200},
    'tele': {'frames': _frames_tele, 'frameDuration': 260},
    'rellotge': {'frames': _frames_rellotge, 'frameDuration': 550},
}


def _amo(ids):
    def mask(x, y):
        _, e = _base()
        return e.ids[e.amo[y * e.cv.w + x]] in ids
    return mask


def _p(x, z, y=0.0):
    u, v, _ = CAM.projecta((x, y, z))
    return round(u), round(v)


# Capes del davant: el primer pla i la taula amb les cadires. Per davant de la taula ja no es camina (l'escala hi
# passaria d'1,2): qui hi passa, hi passa per darrere, i la taula el tapa.
FRONT = [
    {'id': 'davant', 'mask': _amo({'primer_pla'}), 'baseline': 999, 'zIndex': 20},
    {'id': 'davant_taula', 'mask': _amo({'taula', 'cadira', 'cadira_fons'}),
     'baseline': BOTTOM, 'zIndex': 20},
]


# ─── Geometria (coordenades de sala, projectades) ────────────────────────────

def _rect_mon(*Ps):
    pts = [CAM.projecta(P) for P in Ps]
    return (max(0, round(min(p[0] for p in pts))), max(0, round(min(p[1] for p in pts))),
            min(W - 1, round(max(p[0] for p in pts))), min(BOTTOM, round(max(p[1] for p in pts))))


def _carta_rect(box, x, marge=2):
    fx0, fy0, fx1, fy1 = box
    return _rect_mon((x, _y(fy0) + marge, _wz(fx0) - marge), (x, _y(fy1) - marge, _wz(fx1) + marge),
                     (x, _y(fy0) + marge, _wz(fx1) + marge), (x, _y(fy1) - marge, _wz(fx0) - marge))


def _nevera_rect(box):
    """Un retall del dibuix pla de la nevera (de cara), projectat pel davant de la nevera."""
    fx, fz, fw, fd, fh, fa = FRIDGE
    P = _en_caixa(fx, fz, fa)
    k = fh / 145
    x0, y0, x1, y1 = box
    return _rect_mon(*[P(-fw / 2 + (x - 293) * fw / 84, fh - (y - 67) * k, -fd / 2) for x in (x0, x1) for y in (y0, y1)])


# El terra on es camina (al món): davant el taulell, la nevera i el cubell, fins a la porta, i per darrere de la
# taula (per davant, ja és el primer pla: l'escala passaria d'1,2).
WALK_MON = [(48, 96), (92, 92), (200, 132), (248, 84), (300, 104), (400, 148), (470, 176), (476, 230), (444, 236),
            (434, 288), (200, 288), (180, 262), (138, 262), (138, 224), (48, 222)]


def _cantons(cx, cz, ang, lx0, lx1, lz0, lz1):
    P = _en_caixa(cx, cz, ang)
    return [_off(P, lx, lz) for lx, lz in ((lx0, lz0), (lx1, lz0), (lx1, lz1), (lx0, lz1))]


_WALK = [_p(x, z) for x, z in WALK_MON]
_V_FONS, _V_PROP = min(v for _, v in _WALK), max(v for _, v in _WALK)


def _escala_a(v):
    """L'escala d'un personatge amb els peus a la y de pantalla `v` (al terra, la profunditat només depèn de v)."""
    lo, hi = 1.0, 2000.0
    for _ in range(60):
        z = (lo + hi) / 2
        if CAM.projecta((260, 0, z))[1] > v:
            lo = z
        else:
            hi = z
    return CAM.escala((260, 0, (lo + hi) / 2))


_FR = FRIDGE
_FP = _en_caixa(_FR[0], _FR[1], _FR[5])

GEOMETRIA = {
    'things': {
        'cafetera': {'rect': _carta_rect((76, 115, 114, 154), 18), 'walk': _p(64, _wz(95))},
        'plats': {'rect': _carta_rect((145, 118, 242, 160), 20), 'walk': _p(64, _wz(190))},
        'nevera': {'rect': _rect_mon(*[_FP(lx, y, lz) for lx in (-_FR[2] / 2, _FR[2] / 2) for lz in (-_FR[3] / 2, _FR[3] / 2)
                                       for y in (0, _FR[4] + 20)]),
                   'walk': _p(_FR[0] + 10, _FR[1] - _FR[3] / 2 - 40)},
        'pizza_nevera': {'rect': _nevera_rect((304, 107, 355, 123)), 'walk': _p(_FR[0] + 10, _FR[1] - _FR[3] / 2 - 40)},
        'tonyina': {'rect': _nevera_rect((307, 133, 355, 153)), 'walk': _p(_FR[0] + 10, _FR[1] - _FR[3] / 2 - 40)},
        'passaplats': {'rect': _rect_mon((HATCH[0], HATCH[3], ZW), (HATCH[1], HATCH[2], ZW)),
                       'walk': _p((HATCH[0] + HATCH[1]) / 2 + 6, 272)},
        'porta': {'rect': _rect_mon((DOOR[0], DOOR[3], ZW), (DOOR[1], DOOR[2], ZW)),
                  'walk': _p((DOOR[0] + DOOR[1]) / 2, 282)},
    },
    'spawns': {'vet': _p(220, 150)},
    'walkable': _WALK,
    'floorSquash': 0.45,                           # (la càmera, picada: el terra es veu aixafat)
    # L'ombra de contacte: la llum dominant és el llum penjant (el punt del terra just a sota).
    'characterShadow': {'enabled': True, 'color': '#120806', 'alpha': 0.5, 'squash': 0.42, 'core': 0.6,
                        'light': {'x': _p(LAMPP[0], LAMPP[2])[0], 'y': _p(LAMPP[0], LAMPP[2])[1], 'stretch': 0.7,
                                  'reach': 150}},
    'regions': [{'id': 'perspectiva', 'active': True, 'scaleEnabled': True, 'scaleWalkSpeed': True,
                 'scaleTop': round(_escala_a(_V_FONS - 2), 3), 'scaleBottom': round(_escala_a(_V_PROP + 2), 3),
                 'points': [(0, _V_FONS - 2), (W - 1, _V_FONS - 2), (W - 1, _V_PROP + 2), (0, _V_PROP + 2)]}],
    # la llum de la sala sobre els personatges, en temps d'execució
    'characterLights': {
        'ambient': '#8a7466',                                                           # cuina de nit, càlida
        'lights': [
            {'x': _p(LAMPP[0], LAMPP[2], LAMPP[1])[0], 'y': _p(LAMPP[0], LAMPP[2], LAMPP[1])[1], 'radius': 300,
             'color': '#ffbe78', 'intensity': 1.0},                                     # el llum penjant
            {'x': _p(HATCH_C[0], ZW, HATCH_C[1])[0], 'y': _p(HATCH_C[0], ZW, HATCH_C[1])[1], 'radius': 110,
             'color': '#50dcd2', 'intensity': 0.5},                                     # el passaplats
            {'x': _p(HATCH_C[0], ZW, HATCH_C[1])[0], 'y': _p(HATCH_C[0], ZW, HATCH_C[1])[1], 'radius': 170,
             'color': '#50e6d2', 'intensity': 0.9, 'whenPropVisible': 'passaplats_obert'},
            {'x': _p(_FR[0], _FR[1] - _FR[3] / 2, 70)[0], 'y': _p(_FR[0], _FR[1] - _FR[3] / 2, 70)[1], 'radius': 150,
             'color': '#e0f4ff', 'intensity': 0.8, 'whenPropVisible': 'nevera_oberta'},
        ],
    },
}
