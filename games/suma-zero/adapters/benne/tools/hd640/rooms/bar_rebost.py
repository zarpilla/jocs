"""
El rebost i despatx d'en Tomàs, darrere el bar La Propina. EN 3D (hd640/tres_d.py), a 1×.

Una càmera alta, a la dreta, que mira de biaix la cantonada del fons a l'esquerra (com l'estudi de l'Iri):
  - a la paret de l'esquerra, en escorç, la **porta del bar** (amb la ratlla de llum per sota, que talla l'ombra dels
    peus de qui passa) i el penjador amb la jaqueta de pana i el davantal;
  - a la paret del fons (maó emblanquinat amb humitats i la canonada que goteja), el quadre elèctric, el calendari,
    el suro amb les factures i el «PROHIBIT FUMAR» cremat;
  - l'**escriptori** d'en Tomàs separat de la paret i girat (tres cares: el frontal amb els calaixos i el **pany
    intel·ligent**, el costat i el taulell amb el flexo, les factures, la calculadora, el cendrer i el marc), i la
    cadira de skai al costat: s'hi passa per darrere;
  - les **caixes de cervesa** apilades de qualsevol manera contra la paret, la capsa de tovallons, la
    **prestatgeria** metàl·lica (llaunes, llimones, garrafes, cafè) i el barril; la fregona a la galleda;
  - la **bombeta** nua penjada al mig, amb l'arna, que fa un bassal de llum càlida i deixa els racons a les fosques;
  - primer pla: sacs de sucre en silueta a baix a l'esquerra, i caixes i una canonada a la dreta.

Tot el detall ve del dibuix pla de sempre (bar_rebost_pla_comu.py), projectat; el calaix obert i la recepta són
l'escena amb un estat, menys la de sempre.

El món: x a la dreta (0 = la paret de la porta), y amunt (0 = el terra), z cap al fons (300 = la paret del fons);
1 unitat = 1 píxel de sala a la distància on un personatge fa ≈111 px (escala 1).
"""
import functools
import math

from PIL import Image

import hd640  # noqa: F401  (abans de cap hd.rooms: posa la llibreria a 640×360)
from hd640 import llum
from hd.pix import Canvas, Light, W, H, hr
from hd.rooms.comu import _diff, text_width, SHEET, CARD
from hd.rooms.exterior import fbm
from hd640.rooms import bar_rebost_pla_comu as PL
from hd640.rooms.bar_rebost_pla_comu import WOOD, STEELB, SLATE, BRICK, MORTAR, CEMENT, CRATE_Y, CRATE_R, BOTTLES
from hd640.tres_d import Camera, Escena, Llum

BOTTOM = 259                                       # la sala acaba aquí (a sota, la barra de verbs)
ZW = 300                                           # la paret del fons
HW = 200                                           # fins on arriba el dibuix pla de les parets
HT = 240                                           # el sostre
XL = 180                                           # al dibuix pla, la cantonada: a l'esquerra, la paret de la porta
XR = 760                                           # on s'acaba la paret del fons (fora de la pantalla)
DESK = (222, 176, 182, 66, 56, 0.3)                # l'escriptori: x, z del centre, ample, fons, alçada, gir
CHAIR = (110, 214)                                 # la cadira (x, z), a l'esquerra de l'escriptori
SHELF = (386, 456, 262, 298, 172)                  # la prestatgeria: x0, x1, z0, z1, alçada
KEG = (444, 228)                                   # el barril
MOP = (30, 262)                                    # la galleda amb la fregona, a la cantonada
BULB_P = (222, 158, 168)                           # la bombeta, penjada del sostre
DRIP = 380                                         # on goteja la canonada (x), entre les caixes i la prestatgeria
CR_W, CR_H, CR_D = 48, 27, 34                      # una caixa de cervesa


def _w(fx):
    """Una x del dibuix pla de la paret del fons → la x del món."""
    return fx - XL


def _wz(fx):
    """Una x del dibuix pla de la paret de la porta → la z del món."""
    return ZW - XL + fx


def _y(fy):
    """Una y del dibuix pla (el terra, a 200) → l'alçada del món."""
    return HW - fy


DOOR = (_wz(PL.DOOR[0] - 5), _wz(PL.DOOR[2] + 5), 0, _y(PL.DOOR[1] - 5))     # z0, z1, y0, y1 (amb el marc)
# les caixes: (x, z del centre, fila, gir, groga?)
CRATES = [(246, ZW - 20, 0, 0.04, True), (298, ZW - 22, 0, -0.03, False), (350, ZW - 19, 0, 0.06, True),
          (272, ZW - 21, 1, 0.08, False), (326, ZW - 19, 1, -0.05, True), (300, ZW - 20, 2, 0.02, True)]
TOVALLONS = (364, ZW - 22, CR_H + 6, 0.1)          # la capsa de tovallons, damunt la de la dreta

CAM = Camera(pos=(420, 200, -240), yaw=-0.36, pitch=0.2, f=470, centre=(320, 104))

LIGHT = Light(ambient=0.0, vignette=None, floor_fade=None)  # (la llum és la del món: la de l'Escena)
TEXL = Light(ambient=0.2, vignette=None, floor_fade=None)   # el dibuix pla de les textures, sense vinyeta
LLUMS = [Llum(BULB_P, 330, 1.9, power=1.4),                                         # la bombeta
         Llum((6, 6, (DOOR[0] + DOOR[1]) / 2), 70, 0.9, power=2.0)]                 # la llum del bar per sota la porta


# ─── Les textures: el dibuix pla de sempre ───────────────────────────────────

def _llenc(transparent=False):
    return Canvas(light=TEXL, transparent=transparent)


@functools.lru_cache(maxsize=None)
def _paret():
    """Les dues parets planes, de cara: el maó, la canonada, la porta, el penjador, el quadre elèctric, el calendari,
    el suro i el «PROHIBIT FUMAR»."""
    cv = _llenc()
    PL.wall(cv)
    PL.fusebox(cv)
    PL.hooks(cv)
    PL.door(cv)
    PL.calendar(cv)
    PL.corkboard(cv)
    PL.no_smoking(cv)
    return cv.img


@functools.lru_cache(maxsize=None)
def _paret_buida():
    cv = _llenc()
    PL.wall(cv)
    return cv.img


def _objectes(obert=False):
    """L'escriptori, el que hi ha damunt, la cadira, la prestatgeria, el barril, la fregona i la bombeta, dibuixats
    plans sobre transparent (en surten els retalls)."""
    cv = _llenc(transparent=True)
    PL.shelves(cv)
    PL.chair(cv)
    PL.desk(cv)
    if obert:
        cv.rect(261, 160, 336, 181, SLATE, 0.3)                           # el forat del calaix tret
        cv.darken(261, 160, 336, 164, 0.6)
    PL.desk_things(cv)
    PL.keg_and_mop(cv)
    PL.bulb(cv)
    return cv.img


def _calaix():
    """El calaix tret (el davant, amb el pany en verd)."""
    cv = _llenc(transparent=True)
    PL.drawer(cv, open_=True)
    return cv.img


def _caixes():
    cv = _llenc(transparent=True)
    PL.crate(cv, 10, 20, CRATE_Y)
    PL.crate(cv, 70, 20, CRATE_R)
    w = text_width('TOVALLONS')
    cv2 = _llenc(transparent=True)
    PL.crates(cv2)                                                         # (la capsa de tovallons)
    img = cv.img
    img.paste(cv2.img.crop((530 - w // 2 - 4, 123, 530 + w // 2 + 5, 166)), (130, 10))
    return img, (130, 10, 130 + w + 9, 53)


DESK_FRONT = (210, 155, 391, 212)
DRAWER = (261, 160, 337, 182)
DRAWER_OPEN = (261, 168, 337, 196)
SHELF_CROP = (563, 30, 636, 206)
CHAIR_BOX = (164, 126, 216, 226)
KEG_BOX = (578, 199, 617, 251)
MOP_BOX = (116, 126, 153, 241)
BULB_BOX = (309, 24, 326, 43)
# damunt l'escriptori: (retall, x local, z local)
COSES = [((220, 113, 261, 153), -64, 14), ((262, 124, 283, 153), -30, 8), ((283, 139, 309, 153), -4, -10),
         ((310, 138, 331, 153), 22, -4), ((339, 124, 367, 153), 50, 16), ((369, 129, 382, 153), 74, 4)]


@functools.lru_cache(maxsize=None)
def _textures(obert=False):
    cx, cbox = _caixes()
    return {'paret': _paret(), 'buida': _paret_buida(), 'obj': _objectes(obert), 'calaix': _calaix(),
            'caixes': cx, 'tovallons': cbox}


# ─── Les superfícies ────────────────────────────────────────────────────────

def _mao(lvl0, seed=3):
    """Maó emblanquinat en coordenades del món: on el dibuix pla no arriba."""
    def L(s, t, P):
        row = int(t // 9)
        off = 12 if row % 2 else 0
        bx = int((s + off) // 24)
        if t % 9 > 8 or (s + off) % 24 < 1:
            return lvl0 - 0.6
        v = lvl0 + 0.4 + (hr(bx, row, seed) - 0.5) * 0.7 + (1.0 if hr(int(s) // 12, int(t) // 8, 7) > 0.55 else 0)
        if t % 9 < 1:
            v += 0.35
        return v
    return L


def _ciment(s, t, P):
    """El ciment del terra en coordenades del món: taques, juntes de dilatació cada 160 i serradures."""
    x, z = P[0], P[2]
    if x % 160 < 1.0 or z % 160 < 1.0:
        return 1.6
    v = 3.0 + (fbm(x / 70, z / 50, 2) - 0.5) * 0.9 + (hr(int(x // 4), int(z // 3), 2) - 0.5) * 0.4
    for cx, cz, rx, rz in ((150, 120, 30, 14), (330, 90, 44, 18), (420, 200, 20, 10)):
        d = ((x - cx) / rx) ** 2 + ((z - cz) / rz) ** 2
        if d < 1:
            v -= 1.0 * (1 - d)                                                    # taques d'oli i de cervesa
    if hr(int(x), int(z), 71) > 0.996:
        v += 1.2                                                                  # serradures
    return v


def _llum_porta(s, t):
    """La claror del bar que entra per sota la porta i s'escampa pel terra (s des de la paret, t al llarg)."""
    z0, z1 = DOOR[0] + 5, DOOR[1] - 5
    if s > 40:
        return 0.0
    k = max(0.0, 1 - abs(t - (z1 - z0) / 2) / ((z1 - z0) / 2 + s * 0.6))
    return 0.55 * k * (1 - s / 40) ** 1.6


def _escriptori_P(lx, y, lz):
    cx, cz, w, d, h, a = DESK
    c, s = math.cos(a), math.sin(a)
    return (cx + lx * c - lz * s, y, cz + lx * s + lz * c)


def escena(cv, tex, estat=frozenset()):
    """Tota la sala, de lluny a prop. `estat`: 'obert' (el calaix tret), 'recepta' (la servilleta, a dins).
    → l'Escena (qui ha pintat què)."""
    e = Escena(cv, CAM, LLUMS, ambient=-0.7)
    zn = CAM.pos[2] + 60
    paret, ob = tex['paret'], tex['obj']
    # la paret de la porta (x = 0): de prop, maó; cap a la cantonada, el dibuix pla (x 0..180)
    e.quad('paret_esq_prop', (0, HW, zn), (0, HW, ZW - XL), (0, 0, ZW - XL), (0, 0, zn), ramp=BRICK, lvl=_mao(2.4))
    e.quad('paret_esq', (0, HW, ZW - XL), (0, HW, ZW), (0, 0, ZW), (0, 0, ZW - XL), tex=(paret, (0, 0, XL, HW)))
    # la paret del fons: el dibuix pla (x 180..640) i, a la dreta, més paret
    e.quad('paret_fons', (0, HW, ZW), (W - XL, HW, ZW), (W - XL, 0, ZW), (0, 0, ZW), tex=(paret, (XL, 0, W, HW)))
    e.quad('paret_fons', (W - XL, HW, ZW), (XR, HW, ZW), (XR, 0, ZW), (W - XL, 0, ZW),
           tex=(tex['buida'], (0, 0, XR - W + XL, HW)))
    # per sobre del dibuix pla (de 200 al sostre), més maó, i el sostre, fosc
    e.quad('paret_esq_prop', (0, HT, zn), (0, HT, ZW), (0, HW, ZW), (0, HW, zn), ramp=BRICK, lvl=_mao(2.0, seed=9))
    e.quad('paret_fons', (0, HT, ZW), (XR, HT, ZW), (XR, HW, ZW), (0, HW, ZW), ramp=BRICK, lvl=_mao(2.0, seed=11))
    e.quad('sostre', (0, HT, zn), (XR, HT, zn), (XR, HT, ZW), (0, HT, ZW), ramp=MORTAR, lvl=0.6, dues_cares=True)
    # el terra, i la llum del bar per sota la porta
    e.quad('terra', (0, 0, ZW), (XR, 0, ZW), (XR, 0, zn), (0, 0, zn), ramp=CEMENT, lvl=_ciment)
    z0, z1 = DOOR[0] + 5, DOOR[1] - 5
    e.claror((0, 0.4, z1), (0, 0.4, z0), (40, 0.4, z0), (40, 0.4, z1), (255, 210, 130),
             lambda s, t: _llum_porta(t, (z1 - z0) - s))
    e.quad('ratlla', (0.4, 0.5, z1), (0.4, 0.5, z0), (2.4, 0.5, z0), (2.4, 0.5, z1), ramp=[(255, 224, 150)], lvl=0.0,
           dues_cares=True)
    # la reixa del desguàs, al mig
    gx, gz = 250, 92
    e.quad('terra', (gx - 14, 0.4, gz + 5), (gx + 14, 0.4, gz + 5), (gx + 14, 0.4, gz - 5), (gx - 14, 0.4, gz - 5),
           ramp=STEELB, lvl=lambda s, t, P: 3.0 if int(s) % 3 == 0 else 0.4)
    # la claror de la bombeta al terra, i la foscor dels racons
    bx, by, bz = BULB_P
    e.claror((bx - 200, 0.3, bz + 130), (bx + 200, 0.3, bz + 130), (bx + 200, 0.3, bz - 200), (bx - 200, 0.3, bz - 200),
             (255, 210, 140), lambda s, t: 0.16 * max(0.0, 1 - math.hypot(s - 200, (t - 130) * 1.1) / 200))
    e.foscor('racons', (0, 0.5, ZW), (XR, 0.5, ZW), (XR, 0.5, zn), (0, 0.5, zn),
             lambda s, t: max(0.6 * max(0.0, 1 - t / 36), 0.5 * max(0.0, 1 - s / 30)))
    e.foscor('cantonada', (0, HW, ZW - 0.5), (70, HW, ZW - 0.5), (70, 0, ZW - 0.5), (0, 0, ZW - 0.5),
             lambda s, t: 0.5 * max(0.0, 1 - s / 70))
    e.foscor('cantonada2', (0.5, HW, ZW - 70), (0.5, HW, ZW), (0.5, 0, ZW), (0.5, 0, ZW - 70),
             lambda s, t: 0.5 * max(0.0, 1 - (70 - s) / 70))
    e.foscor('sostre_fosc', (0, HT - 0.5, ZW - 0.6), (XR, HT - 0.5, ZW - 0.6), (XR, 0, ZW - 0.6), (0, 0, ZW - 0.6),
             lambda s, t: 0.55 * max(0.0, 1 - t / 100))
    e.foscor('sostre_fosc', (0.6, HT - 0.5, zn), (0.6, HT - 0.5, ZW), (0.6, 0, ZW), (0.6, 0, zn),
             lambda s, t: 0.55 * max(0.0, 1 - t / 100))
    # la galleda amb la fregona, a la cantonada
    mx, mz = MOP
    _dret(e, 'fregona', ob, MOP_BOX, (mx, 0, mz), 235)
    # la prestatgeria, contra la paret (el davant, el dibuix pla), amb la seva ombra
    sx0, sx1, sz0, sz1, sh = SHELF
    e.foscor('ombra_prestatgeria', (sx0 - 6, 0.6, sz1), (sx1 + 8, 0.6, sz1), (sx1 + 8, 0.6, sz0 - 14), (sx0 - 6, 0.6, sz0 - 14),
             lambda s, t: 0.5 * min(1.0, max(0.0, (sz1 - sz0 + 14 - t) / 14)))
    e.caixa('prestatgeria', sx0, sx1, 0, sh, sz0, sz1, STEELB, 1.2,
            cares={'davant': {'tex': (ob, SHELF_CROP)}, 'dalt': {'ramp': STEELB, 'lvl': 3.4},
                   'esquerra': {'ramp': STEELB, 'lvl': lambda s, t, P: 3.0 if int(t) % 42 < 2 or s < 2 or s > sz1 - sz0 - 2
                                else 0.4}})
    # les caixes de cervesa, apilades contra la paret: el davant (el dibuix pla), la tapa amb els colls i les xapes
    cimg, tbox = tex['caixes'], tex['tovallons']
    e.foscor('ombra_caixes', (220, 0.6, ZW), (380, 0.6, ZW), (380, 0.6, ZW - 52), (220, 0.6, ZW - 52),
             lambda s, t: 0.55 * min(1.0, max(0.0, (52 - t) / 18)))

    def colls(s, t, P):
        i, j = int(s // 5.5), int(t // 8)
        cx_, cz_ = s - (i + 0.5) * 5.5, t - (j + 0.5) * 8
        r = math.hypot(cx_, cz_ * 0.8)
        if r < 1.4:
            return 3.4                                                            # la xapa
        if r < 2.4:
            return 1.8
        return 0.4
    for x, z, fila, a, groga in CRATES:
        ramp = CRATE_Y if groga else CRATE_R
        crop = (10, 20, 59, 48) if groga else (70, 20, 119, 48)
        e.caixa_girada('caixes', x, z, CR_W, CR_D, CR_H, a, ramp, 2.0, y0=fila * CR_H,
                       cares={'davant': {'tex': (cimg, crop)}, 'dalt': {'ramp': BOTTLES[1], 'lvl': colls},
                              'esquerra': {'ramp': ramp, 'lvl': lambda s, t, P: 1.6 + (0.8 if int(s) % 7 < 2 else 0)},
                              'dreta': {'ramp': ramp, 'lvl': 1.2}})
    tx, tz, ty, ta = TOVALLONS
    tw = tbox[2] - tbox[0]
    e.caixa_girada('caixes', tx, tz, tw, 30, tbox[3] - tbox[1], ta, CARD, 2.0, y0=ty,
                   cares={'davant': {'tex': (cimg, tbox)}, 'dalt': {'ramp': CARD, 'lvl': lambda s, t, P: 3.2 - (1.0 if abs(t - 15) < 1.5 else 0)},
                          'esquerra': {'ramp': CARD, 'lvl': 1.8}})
    # la canonada que goteja: la taca d'humitat a terra
    e.foscor('gota', (DRIP - 10, 0.6, ZW), (DRIP + 10, 0.6, ZW), (DRIP + 10, 0.6, ZW - 14), (DRIP - 10, 0.6, ZW - 14),
             lambda s, t: 0.35 * max(0.0, 1 - ((s - 10) / 10) ** 2 - (t / 14) ** 2))
    # el barril, davant la prestatgeria
    kx, kz = KEG
    e.foscor('ombra_barril', (kx - 24, 0.6, kz + 18), (kx + 24, 0.6, kz + 18), (kx + 24, 0.6, kz - 20), (kx - 24, 0.6, kz - 20),
             lambda s, t: 0.6 * max(0.0, 1 - ((s - 24) / 22) ** 2 - ((t - 19) / 17) ** 2) * 1.5)
    _dret(e, 'barril', ob, KEG_BOX, (kx, 0, kz), 246)
    # la cadira, a l'esquerra de l'escriptori
    chx, chz = CHAIR
    e.foscor('ombra_cadira', (chx - 22, 0.7, chz + 14), (chx + 22, 0.7, chz + 14), (chx + 22, 0.7, chz - 14),
             (chx - 22, 0.7, chz - 14), lambda s, t: 0.6 * max(0.0, 1 - ((s - 22) / 22) ** 2 - ((t - 14) / 14) ** 2) * 1.6)
    _dret(e, 'cadira', ob, CHAIR_BOX, (chx, 0, chz), 221)
    # l'escriptori, girat: l'ombra, el moble (el frontal amb els calaixos, el dibuix pla) i el que hi ha damunt
    cx, cz, w, d, h, a = DESK
    P = _escriptori_P
    e.foscor('ombra_escriptori', P(-w / 2 - 8, 0.6, d / 2 + 6), P(w / 2 + 8, 0.6, d / 2 + 6), P(w / 2 + 8, 0.6, -d / 2 - 16),
             P(-w / 2 - 8, 0.6, -d / 2 - 16), lambda s, t: 0.55 * min(1.0, max(0.0, t / 14)) * min(1.0, s / 10, (w + 16 - s) / 10))

    def taulell(s, t, P_):
        v = 3.4 + (0.5 if hr(int(s) // 8, int(t), 2) > 0.8 else 0) - (0.6 if hr(int(s), int(t), 3) > 0.97 else 0)
        if 2.4 < math.hypot(s - 82, t - 30) < 3.4:
            v -= 0.8                                                              # la rodona d'un got
        return v
    e.caixa_girada('escriptori', cx, cz, w, d, h, a, WOOD, 2.0,
                   cares={'davant': {'tex': (ob, DESK_FRONT)}, 'dalt': {'ramp': WOOD, 'lvl': taulell},
                          'dreta': {'ramp': WOOD, 'lvl': lambda s, t, P_: 1.6 + (0.6 if t < 4 else 0)
                                    + (hr(int(s) // 3, int(t) // 9, 4) - 0.5) * 0.3},
                          'esquerra': {'ramp': WOOD, 'lvl': 1.4}})
    for box, lx, lz in COSES:
        _dret(e, 'damunt', ob, box, P(lx, h, lz), 151)
    if 'obert' in estat:
        # el calaix tret: el fons (per dins), els costats i el davant amb el pany en verd
        dl0, dl1 = DRAWER[0] - 300.5, DRAWER[2] - 300.5
        y0, y1 = h - (DRAWER[3] - 155), h - (DRAWER[1] - 155)
        dz = 46                                   # (prou tret perquè es vegi per dins des de dalt)
        yt = y1 - 7                               # el cantell de dalt del calaix
        e.quad('calaix', P(dl0, y0 + 2, -d / 2 + 6), P(dl1, y0 + 2, -d / 2 + 6), P(dl1, y0 + 2, -d / 2 - dz),
               P(dl0, y0 + 2, -d / 2 - dz), ramp=CARD, lvl=lambda s, t, P_: 2.4 - (0.9 if t < 8 else 0)
               - (0.6 if s < 3 or s > dl1 - dl0 - 3 else 0))
        for lx_ in (dl0, dl1):                    # els costats
            e.quad('calaix', P(lx_, yt, -d / 2 + 6), P(lx_, yt, -d / 2 - dz), P(lx_, y0, -d / 2 - dz),
                   P(lx_, y0, -d / 2 + 6), ramp=WOOD, lvl=lambda s, t, P_: 2.2 + (1.0 if t < 1.5 else 0), dues_cares=True)
        if 'recepta' in estat:
            rc = P(-12, y0 + 2.6, -d / 2 - 9)
            e.quad('recepta', (rc[0] - 12, rc[1], rc[2] + 4), (rc[0] + 12, rc[1], rc[2] + 5), (rc[0] + 13, rc[1], rc[2] - 4),
                   (rc[0] - 11, rc[1], rc[2] - 5), ramp=SHEET,
                   lvl=lambda s, t, P_: 1.2 if (abs(t - 3) < 0.6 or abs(t - 6) < 0.6) and 3 < s < 21 else 4.6)
        e.quad('calaix', P(dl0, yt, -d / 2 - dz), P(dl1, yt, -d / 2 - dz), P(dl1, y0, -d / 2 - dz),
               P(dl0, y0, -d / 2 - dz), tex=(tex['calaix'], DRAWER_OPEN))
    # la bombeta, penjada del fil
    bx, by, bz = BULB_P
    e.cable('bombeta', [(bx, HT, bz), (bx, by + 9, bz)], SLATE, 1.6, gruix=0.6)
    _dret(e, 'bombeta', ob, BULB_BOX, (bx, by - 7, bz), BULB_BOX[3])
    # primer pla: sacs de sucre en silueta a baix a l'esquerra, caixes i una canonada a la dreta
    FOSC = [(4, 3, 2), (10, 7, 5), (17, 12, 9), (25, 18, 13), (35, 26, 19), (47, 36, 27)]
    for (sx, sz, r, seed) in ((70, 46, 34, 3), (114, 30, 28, 5), (52, 92, 26, 7)):
        e.roca('primer_pla', (sx, 0, sz), r, FOSC, lvl=2.2, llum_dir=(0.6, -0.7), aplana=0.55, seed=seed)
    for cx_, cz_, cw, cd, ch, ca, cy in ((536, 124, 60, 46, 40, -0.25, 0), (532, 128, 52, 40, 34, -0.1, 40)):
        e.caixa_girada('primer_pla', cx_, cz_, cw, cd, ch, ca, FOSC, 1.6, y0=cy,
                       cares={'dalt': {'ramp': FOSC, 'lvl': lambda s, t, P_: 2.8 - (1.2 if abs(s - 26) < 2 else 0)},
                              'davant': {'ramp': FOSC, 'lvl': 1.2}, 'esquerra': {'ramp': FOSC, 'lvl': 2.2}})
    e.tub('primer_pla', (486, 0, 64), (486, HT, 64), 7, FOSC, 1.8, brides=70)
    return e


def _dret(e, sid, img, box, peu, base_y):
    """Un retall del dibuix pla, dret, amb la base (la y `base_y` del dibuix) al punt `peu` del món."""
    e.sprite(sid, img.crop(box), ((box[2] - box[0]) / 2, base_y - box[1]), peu)


# ─── Composició i llum ──────────────────────────────────────────────────────

def _proj(P):
    u, v, _ = CAM.projecta(P)
    return u, v


def _fx():
    bx, by = _proj(BULB_P)
    dx, dy = _proj((0, 4, (DOOR[0] + DOOR[1]) / 2))
    light = [llum.wash(bx, by + 70, 250, (255, 190, 110), k=0.45, air=0.04, squash=1.0),          # la bombeta
             llum.wash(dx, dy, 60, (255, 200, 120), k=0.6, air=0.04, squash=1.6)]                  # la porta
    tone = [llum.grade(contrast=1.12, pivot=40, sat=1.15, lift=(6, 3, 2))]
    bloom = [llum.bloom(thr=200)]
    return light, bloom, tone


def _render(estat=frozenset(), tex=None):
    cv = Canvas(light=LIGHT)
    e = escena(cv, tex or _textures('obert' in estat), estat)
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


@functools.lru_cache(maxsize=None)
def _amb_estat(*estat):
    return _amb_llum(_render(frozenset(estat))[0], bloom=False)


def _decorat(estat, sobre=()):
    """Un decorat: la sala amb aquell estat, menys la sala amb l'estat `sobre` (només el que canvia), amb la llum."""
    def draw(cv):
        cv.img.alpha_composite(_diff(_amb_estat(*estat), _amb_estat(*sobre)))
        cv.P = cv.img.load()
    return draw


PROPS = {'calaix_obert': _decorat(('obert',)), 'recepta_calaix': _decorat(('obert', 'recepta'), ('obert',))}


# ─── Animacions ─────────────────────────────────────────────────────────────

def _empty():
    return Image.new('RGBA', (W, H), (0, 0, 0, 0))


def _px(img, e, ids, x, y, col):
    """Un píxel d'una animació, només on es veu la paret o el terra (el que hi ha davant el tapa)."""
    x, y = int(round(x)), int(round(y))
    if 0 <= x < W and 0 <= y < BOTTOM and e.ids[e.amo[y * W + x]] in ids:
        img.putpixel((x, y), tuple(col) + (255,))


def _frames():
    """L'arna dona voltes a la bombeta (un vuit), amb les ales que baten."""
    base, e = _base()
    bx, by = _proj((BULB_P[0], BULB_P[1] - 3, BULB_P[2]))
    k = CAM.escala(BULB_P)
    out = []
    for i in range(16):
        img = base.copy()
        a = i / 16 * 2 * math.pi
        mx, my = bx + round(math.cos(a) * 15 * k), by + round(math.sin(a * 2) * 5 * k) + 3
        up = i % 2
        wing = (90, 80, 70) if up else (150, 140, 120)
        for (dx, dy, c) in ((0, 0, (40, 34, 30)), (0, 1, (60, 50, 44)), (-1, -up, wing), (1, -up, wing)) + \
                (((-2, 0, wing), (2, 0, wing)) if not up else ()):
            img.putpixel((int(mx + dx), int(my + dy)), c + (255,))
        out.append(_diff(_amb_llum(img), _base_llum()))
    return out


def _frames_gota():
    """La canonada del sostre goteja: la gota s'infla, cau arran de paret i esquitxa el terra."""
    base, e = _base()
    ids = {'paret_fons', 'terra', 'gota', 'racons', 'sostre_fosc'}
    top = HW - 16                                                   # la canonada (al dibuix pla, y 11..15)
    seq = [('n', 0)] * 3 + [('f', 1)] * 4 + [('f', 2)] * 3 + [('f', 3)] * 2
    y, v = float(top), 2.0
    while y > 2:
        seq.append(('c', y))
        y, v = y - v, v + 4.0
    seq += [('s', 0), ('s', 1), ('s', 2)] + [('n', 0)] * 4
    W1 = [(30, 40, 50), (90, 110, 120), (150, 170, 180), (200, 214, 220)]
    out = []
    for kind, q in seq:
        if kind == 'n':
            out.append(_empty())
            continue
        img = base.copy()
        if kind == 'f':
            for j in range(q):
                u, vv = _proj((DRIP, top - j, ZW - 2))
                _px(img, e, ids, u, vv, W1[3 - min(j, 2)])
        elif kind == 'c':
            for j, c in enumerate((W1[3], W1[2], W1[1], W1[0])):
                u, vv = _proj((DRIP, q + j * 1.4, ZW - 2))
                _px(img, e, ids, u, vv, c)
        else:
            u, vv = _proj((DRIP, 0, ZW - 4))
            _px(img, e, ids, u, vv, W1[3])
            r = 1 + q * 2
            for d in (-1, 1):
                _px(img, e, ids, u + d * (r + 1), vv - (2 - q), W1[2])
                _px(img, e, ids, u + d * r, vv + 1 - (2 - q), W1[1])
        out.append(_diff(_amb_llum(img), _base_llum()))
    return out


def _frames_passos():
    """Algú passa pel bar, a l'altra banda de la porta: l'ombra dels peus talla la ratlla de llum de sota (i la claror
    que entra pel terra)."""
    base, e = _base()
    z0, z1 = DOOR[0] + 5, DOOR[1] - 5
    # els píxels de la ratlla i de la claror, amb la z del món on toquen
    pts = []
    for zz in range(int(z0), int(z1) + 1):
        for s in range(0, 30):
            u, v = _proj((s * 0.8 + 0.6, 0, zz))
            pts.append((int(u), int(v), zz, s))
    out = []
    for i in range(28):
        if i >= 14:
            out.append(_empty())
            continue
        img = base.copy()
        P = img.load()
        x = 28 + i * 6 - PL.DOOR[0]                                  # d'esquerra a dreta, dos peus
        feet = [(x, x + 5), (x + 12 - (5 if i % 2 else 0), x + 17 - (5 if i % 2 else 0))]
        fet = set()
        for u, v, zz, s in pts:
            if (u, v) in fet or not (0 <= u < W and 0 <= v < BOTTOM):
                continue
            if e.ids[e.amo[v * W + u]] not in ('ratlla', 'terra', 'racons'):
                continue
            fz = zz - z0
            if any(a - s * 0.3 <= fz <= b + s * 0.3 for a, b in feet):
                c = P[u, v]
                k = 0.25 if s < 2 else 0.6 + s * 0.012
                P[u, v] = (int(c[0] * k), int(c[1] * k), int(c[2] * k), 255)
                fet.add((u, v))
        out.append(_diff(_amb_llum(img), _base_llum()))
    return out


ANIMS = {'arna': {'frames': _frames, 'frameDuration': 70},
         'gota': {'frames': _frames_gota, 'frameDuration': 90},
         'passos': {'frames': _frames_passos, 'frameDuration': 120}}


# ─── Capes del davant ───────────────────────────────────────────────────────

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
    {'id': 'davant_escriptori', 'mask': _amo({'escriptori', 'damunt'}), 'baseline': _p(DESK[0], DESK[1])[1],
     'zIndex': 20, 'props': ('calaix_obert', 'recepta_calaix')},          # (el calaix tret, per sobre de l'escriptori)
    {'id': 'davant_cadira', 'mask': _amo({'cadira'}), 'baseline': _p(CHAIR[0], CHAIR[1])[1], 'zIndex': 20},
    {'id': 'davant_barril', 'mask': _amo({'barril'}), 'baseline': _p(KEG[0], KEG[1] - 6)[1], 'zIndex': 20},
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
        if CAM.projecta((260, 0, z))[1] > v:
            lo = z
        else:
            hi = z
    return CAM.escala((260, 0, (lo + hi) / 2))


def _v_escala(k):
    lo, hi = 0.0, float(BOTTOM)
    for _ in range(50):
        m = (lo + hi) / 2
        if _escala_a(m) < k:
            lo = m
        else:
            hi = m
    return (lo + hi) / 2


def _retalla_v(poly, vmax):
    out = []
    for (ax, ay), (bx, by) in zip(poly, poly[1:] + poly[:1]):
        if ay <= vmax:
            out.append((ax, ay))
        if (ay <= vmax) != (by <= vmax):
            k = (vmax - ay) / (by - ay)
            out.append((round(ax + (bx - ax) * k), round(vmax)))
    return out


# El terra on es camina (al món): de la porta fins davant les caixes i el barril, i per darrere l'escriptori; el
# de més a prop (on un personatge faria més d'1,2) queda per al primer pla. L'escriptori i la cadira, forats.
WALK_MON = [(16, 150), (16, 252), (60, 252), (92, 262), (214, 262), (214, 244), (380, 244), (420, 212), (470, 200),
            (470, 60), (150, 40), (16, 100)]
_WALK = _retalla_v([_p(x, z) for x, z in WALK_MON], _v_escala(1.2))
_V_FONS = min(v for _, v in _WALK)
_V_PROP = max(v for _, v in _WALK)


def _forat_escriptori():
    w, d = DESK[2], DESK[3]
    return [_p(*(lambda P: (P[0], P[2]))(_escriptori_P(lx, 0, lz))) for lx, lz in
            ((-w / 2 - 6, -d / 2 - 6), (w / 2 + 6, -d / 2 - 6), (w / 2 + 6, d / 2 + 6), (-w / 2 - 6, d / 2 + 6))]


_DL0, _DL1 = DRAWER[0] - 300.5, DRAWER[2] - 300.5
_DY0, _DY1 = DESK[4] - (DRAWER[3] - 155), DESK[4] - (DRAWER[1] - 155)

GEOMETRIA = {
    'things': {
        'porta': {'rect': _rect_mon((0, DOOR[3], DOOR[0]), (0, 0, DOOR[1])), 'walk': _p(34, (DOOR[0] + DOOR[1]) / 2)},
        'calaix': {'rect': _rect_mon(*[_escriptori_P(lx, y, -DESK[3] / 2) for lx in (_DL0, _DL1) for y in (_DY0, _DY1)]),
                   'walk': _p(*(lambda P: (P[0], P[2] - 60))(_escriptori_P(0, 0, -DESK[3] / 2)))},
        'caixes': {'rect': _rect_mon((222, 3 * CR_H + 8, ZW - 38), (380, 0, ZW - 38), (380, 3 * CR_H, ZW)),
                   'walk': _p(300, 236)},
    },
    'spawns': {'vet': _p(46, 170)},
    'walkable': _WALK,
    'forats': [_forat_escriptori()],
    'floorSquash': 0.45,
    # L'ombra de contacte: la bombeta, a sobre (el punt del terra just a sota); curta.
    'characterShadow': {'enabled': True, 'color': '#0c0806', 'alpha': 0.5, 'squash': 0.42, 'core': 0.6,
                        'light': {'x': _p(BULB_P[0], BULB_P[2])[0], 'y': _p(BULB_P[0], BULB_P[2])[1], 'stretch': 0.7,
                                  'reach': 150}},
    'regions': [{'id': 'perspectiva', 'active': True, 'scaleEnabled': True, 'scaleWalkSpeed': True,
                 'scaleTop': round(_escala_a(_V_FONS - 2), 3), 'scaleBottom': round(_escala_a(_V_PROP + 2), 3),
                 'points': [(0, _V_FONS - 2), (W - 1, _V_FONS - 2), (W - 1, _V_PROP + 2), (0, _V_PROP + 2)]}],
    'characterLights': {
        'ambient': '#7a6a5c',                                                          # el magatzem, fosc i càlid
        'lights': [
            {'x': _p(BULB_P[0], BULB_P[2], BULB_P[1])[0], 'y': _p(BULB_P[0], BULB_P[2], BULB_P[1])[1], 'radius': 260,
             'color': '#ffc878', 'intensity': 1.1},                                    # la bombeta
            {'x': _p(4, (DOOR[0] + DOOR[1]) / 2, 4)[0], 'y': _p(4, (DOOR[0] + DOOR[1]) / 2, 4)[1], 'radius': 60,
             'color': '#ffd28c', 'intensity': 0.6},                                    # la porta
        ],
    },
}
