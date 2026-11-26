"""
Magatzem d'eines (Iri), el regne del Cargol. EN 3D (hd640/tres_d.py), a 1×.

Una càmera alta que mira de biaix la cantonada del fons a l'esquerra (com l'estudi de Suma Zero):
  - a la paret de l'esquerra, en escorç, les dues **portes** (la de les calderes i la del despatx, amb el vidre
    glaçat), el rètol de les normes i el **ganxo del plomall**;
  - a la paret del fons, la gran **prestatgeria** de material inventariat, separada de la paret i amb volum (el
    costat, la tapa), amb la bombeta que hi penja al davant; el **tauler d'eines**; la **taquilla de la Mira**;
  - el **banc de treball**, separat de la paret i girat, amb el cargol de banc, el registre obert, la safata de
    cargols i la llauna d'oli; el llum d'esmalt verd que hi penja; la **caixa d'eines** (decorat) a terra, al costat;
  - al mig, una pila de caixes i un bidó de ferro-9 (s'hi passa per darrere);
  - primer pla: caixes en silueta a baix a l'esquerra, un pilar de ferro a la dreta i una cadena que penja.

Tot el detall ve del dibuix pla de sempre (fabrica_magatzem_pla_comu.py, per trossos: `room(cv, parts)`),
projectat; els decorats es dibuixen en 3D (o en la textura) i en surt la diferència.

El món: x a la dreta (0 = la paret de les portes), y amunt (0 = el terra), z cap al fons (300 = la paret del fons);
1 unitat = 1 píxel de sala a la distància on un personatge fa ≈110 px (escala 1).
"""
import functools
import math

import hd640  # noqa: F401  (abans de cap hd.rooms: posa la llibreria a 640×360)
import hd.pix as pix
from hd.pix import Light, W, H, hr, FLOOR, IRON, RED, PAPER, GREEN
from hd.rooms.exterior import fbm
from hd.rooms.fabrica_magatzem import F9, WOOD2
from hd640.rooms import fabrica_magatzem_pla_comu as PL
from hd640.rooms.fabrica_despatx_pla_comu import dust
from hd640.tres_d import Camera, Escena, Llum

BOTTOM = 259                                       # la sala acaba aquí (a sota, la barra de verbs)
ZW = 300                                           # la paret del fons
FY = PL.FLOOR_Y                                    # el terra, al dibuix pla
TOPY = 19                                          # on comença el maó, al dibuix pla (a dalt hi ha el sostre)
HW = FY - TOPY                                     # l'alçada de les parets
XL = 190                                           # al dibuix pla, la cantonada: a l'esquerra, la paret de les portes
XR = 700                                           # on s'acaba la paret del fons (fora de la pantalla)

SHELF = (14, 240, 262, 294, 176)                   # la prestatgeria: x0, x1, z0, z1, alçada
BENCH = (330, 226, 158, 42, 60, -0.35)              # el banc: x, z del centre, ample, fons, alt, gir
LOCKER = (412, 452, 270, 298, 134)                 # la taquilla: x0, x1, z0, z1, alçada
TOOLBOX = (266, 192, 68, 30, 32, -0.35)             # la caixa d'eines (decorat): x, z, ample, fons, alt, gir
STACK = (176, 146)                                 # la pila de caixes del mig (x, z)
PILLAR = (500, 72)                                 # el pilar del primer pla
DARK = [(4, 3, 4), (9, 6, 7), (15, 10, 10), (22, 15, 14), (31, 21, 18), (42, 29, 24)]


class Canvas(pix.Canvas):
    """El llenç de Ferro-9, a 1× (tres_d en vol saber l'escala)."""
    S = 1


def _w(fx):
    """Una x del dibuix pla de la paret del fons → la x del món."""
    return fx - XL


def _wz(fx):
    """Una x del dibuix pla de la paret de les portes → la z del món."""
    return ZW - XL + fx


def _y(fy):
    """Una y del dibuix pla (el terra, a FY) → l'alçada del món."""
    return FY - fy


CAM = Camera(pos=(420, 205, -230), yaw=-0.36, pitch=0.21, f=450, centre=(320, 90))

LIGHT = Light(ambient=0.0, vignette=None, floor_fade=None)  # (la llum és la del món: la de l'Escena)
LAMP = (BENCH[0] + 4, 128, BENCH[1] + 4)                    # el llum penjant del banc (la bombeta)
BULB = (_w(PL.BULB_X), 186, SHELF[2] - 10)                  # la bombeta de la prestatgeria
LLUMS = [Llum(LAMP, 260, 2.6, power=1.5),
         Llum(BULB, 240, 1.8, power=1.6),
         Llum((6, _y(110), _wz(116)), 70, 0.8, power=2.0)]

# ─── Les textures: el dibuix pla de sempre ───────────────────────────────────

TEXL = Light(ambient=0.5, vignette=None, floor_fade=None)   # (llum plana: la de la sala la posa l'Escena)


def _pla(parts, transparent=False):
    cv = Canvas(light=TEXL, transparent=transparent)
    PL.room(cv, parts)
    return cv.img


@functools.lru_cache(maxsize=None)
def _paret():
    """Les dues parets planes, de cara: maó, l'arrimador, les portes, el rètol, el ganxo i el tauler d'eines."""
    return _pla(('paret', 'portes', 'tauler'))


@functools.lru_cache(maxsize=None)
def _mobles():
    """La prestatgeria, el banc, el llum i la taquilla, plans sobre transparent (en surten els retalls)."""
    return _pla(('prestatgeria', 'banc', 'llum', 'taquilla'), transparent=True)


@functools.lru_cache(maxsize=None)
def _plomall_pla():
    cv = Canvas(light=TEXL, transparent=True)
    PL.plomall(cv)
    return cv.img


@functools.lru_cache(maxsize=None)
def _caixa_pla():
    cv = Canvas(light=TEXL, transparent=True)
    PL.caixa_eines(cv)
    return cv.img


SHELF_BOX = (203, 29, 430, 201)                    # la prestatgeria, al dibuix pla
BULB_BOX = (306, 0, 327, 26)                       # la bombeta
LAMP_BOX = (PL.LAMP_X - 18, 88, PL.LAMP_X + 19, 110)   # el llum del banc (sense el fil)
VICE_BOX = (436, 127, 477, 148)                    # el cargol de banc
CAN_BOX = (566, 126, 585, 148)                     # la llauna d'oli
LOCKER_BOX = (595, 73, 633, 209)                   # la taquilla
PLOM_BOX = (144, 86, 186, 188)                     # el plomall
PLOM_PEU = (5, _y(87), _wz(164))                   # on penja (el ganxo)
TB_BOX = (483, 216, 554, 249)                      # la caixa d'eines: el davant
TOOLS_BOX = (485, 189, 541, 217)                   # les eines que en sobresurten


# ─── Les superfícies ────────────────────────────────────────────────────────

def _terra(s, t, P):
    """Taulons gastats que fugen cap al fons, en coordenades del món: juntes, testes, claus i taques d'oli."""
    x, z = P[0], P[2]
    pl = math.floor(x / 24)
    fr = x - pl * 24
    seg = math.floor((z + hr(pl, 7) * 150) / 150)
    v = 2.1 + (hr(pl, seg) - 0.5) * 0.8 + (fbm(x / 50, z / 18, 4) - 0.5) * 0.6
    v += 0.15 * math.sin(x * 0.5 + hr(pl, seg, 3) * 9 + z * 0.02)                   # la veta
    if fr < 1.0:
        return 0.6
    if (z + hr(pl, 7) * 150) % 150 < 1.2:
        return 0.8
    if fr < 2.0:
        v += 0.3
    if fbm(x / 26, z / 20, 9) > 0.68:
        v -= 0.7                                                                   # taques d'oli
    return v


def _fusta(lvl0, seed=2, veta=6):
    def L(s, t, P):
        return lvl0 + (hr(int(s // veta), seed) - 0.5) * 0.4 + 0.15 * math.sin(s * 0.9 + t * 0.05 + seed)
    return L


def _dins(x, z, poly):
    sg = 0
    for (ax, az), (bx, bz) in zip(poly, poly[1:] + poly[:1]):
        c = (bx - ax) * (z - az) - (bz - az) * (x - ax)
        if c and sg and (c > 0) != (sg > 0):
            return False
        sg = sg or c
    return True


def _cantons(cx, cz, w, d, ang):
    c, s_ = math.cos(ang), math.sin(ang)
    return [(cx + lx * c - lz * s_, cz + lx * s_ + lz * c) for lx, lz in ((-w / 2, -d / 2), (w / 2, -d / 2),
                                                                          (w / 2, d / 2), (-w / 2, d / 2))]


def _ombra(e, sid, cx, cz, rx, rz, k=0.55, dx=-6, dz=6):
    """Una ombra suau al terra, una mica desplaçada (lluny del llum del banc)."""
    cx, cz = cx + dx, cz + dz
    e.foscor(sid, (cx - rx, 0.6, cz + rz), (cx + rx, 0.6, cz + rz), (cx + rx, 0.6, cz - rz), (cx - rx, 0.6, cz - rz),
             lambda s, t: k * min(1.0, max(0.0, 1 - ((s - rx) / rx) ** 2 - ((t - rz) / rz) ** 2) * 1.8))


def escena(cv, tex, estat=frozenset()):
    """Tota la sala, de lluny a prop. `estat`: els decorats que hi són ('plomall', 'caixa_eines'). → l'Escena."""
    e = Escena(cv, CAM, LLUMS, ambient=-0.5)
    zn = CAM.pos[2] + 60
    paret, mob = tex['paret'], tex['mobles']
    # el sostre: fosc, amb les bigues que fugen cap al fons
    e.quad('sostre', (0, HW, zn), (XR, HW, zn), (XR, HW, ZW), (0, HW, ZW), ramp=IRON, dues_cares=True,
           lvl=lambda s, t, P: 0.6 + (1.4 if P[0] % 90 < 8 else 0) - (0.6 if P[0] % 90 > 86 else 0))
    # la paret de les portes (x = 0): de prop, maó; cap a la cantonada, el dibuix pla (x 0..190)
    e.quad('paret_esq_prop', (0, HW, zn), (0, HW, ZW - XL), (0, 0, ZW - XL), (0, 0, zn),
           tex=(paret, (W - 200, TOPY, W - 10, FY)))
    e.quad('paret_esq', (0, HW, ZW - XL), (0, HW, ZW), (0, 0, ZW), (0, 0, ZW - XL), tex=(paret, (0, TOPY, XL, FY)))
    # la paret del fons (z = 300): el dibuix pla (x 190..640) i, a la dreta, més maó
    e.quad('paret_fons', (0, HW, ZW), (W - XL, HW, ZW), (W - XL, 0, ZW), (0, 0, ZW), tex=(paret, (XL, TOPY, W, FY)))
    e.quad('paret_fons_dreta', (W - XL, HW, ZW), (XR, HW, ZW), (XR, 0, ZW), (W - XL, 0, ZW),
           tex=(paret, (XL, TOPY, XL + XR - (W - XL), FY)))
    # el terra
    e.quad('terra', (0, 0, ZW), (XR, 0, ZW), (XR, 0, zn), (0, 0, zn), ramp=FLOOR, lvl=_terra)
    # la llum: el bassal sota el llum del banc, la claror de la bombeta i el reflex del vidre del despatx
    e.claror((LAMP[0] - 160, 0.3, ZW), (LAMP[0] + 160, 0.3, ZW), (LAMP[0] + 160, 0.3, LAMP[2] - 200),
             (LAMP[0] - 160, 0.3, LAMP[2] - 200), (255, 196, 120),
             lambda s, t: 0.30 * max(0.0, 1 - math.hypot(s - 160, (t - (ZW - LAMP[2])) * 1.1) / 150) ** 1.3)
    e.claror((BULB[0] - 130, 0.3, ZW), (BULB[0] + 130, 0.3, ZW), (BULB[0] + 130, 0.3, ZW - 200),
             (BULB[0] - 130, 0.3, ZW - 200), (255, 190, 110),
             lambda s, t: 0.18 * max(0.0, 1 - math.hypot(s - 130, (t - 50) * 1.2) / 130) ** 1.4)
    e.claror((0, 0.4, _wz(150)), (60, 0.4, _wz(150)), (60, 0.4, _wz(84)), (0, 0.4, _wz(84)), (240, 200, 130),
             lambda s, t: 0.16 * max(0.0, 1 - s / 60) * max(0.0, 1 - abs(t - 33) / 33))
    # la foscor dels racons
    e.foscor('racons', (0, 0.5, ZW), (XR, 0.5, ZW), (XR, 0.5, zn), (0, 0.5, zn),
             lambda s, t: max(0.55 * max(0.0, 1 - t / 26), 0.45 * max(0.0, 1 - s / 22)))
    e.foscor('cantonada', (0, HW, ZW - 0.5), (70, HW, ZW - 0.5), (70, 0, ZW - 0.5), (0, 0, ZW - 0.5),
             lambda s, t: 0.5 * max(0.0, 1 - s / 70))
    e.foscor('cantonada2', (0.5, HW, ZW - 70), (0.5, HW, ZW), (0.5, 0, ZW), (0.5, 0, ZW - 70),
             lambda s, t: 0.5 * max(0.0, 1 - (70 - s) / 70))
    e.foscor('sostre_fosc', (0, HW - 0.5, ZW - 0.6), (XR, HW - 0.5, ZW - 0.6), (XR, 0, ZW - 0.6), (0, 0, ZW - 0.6),
             lambda s, t: 0.5 * max(0.0, 1 - t / 50))
    e.foscor('sostre_fosc2', (0.6, HW - 0.5, zn), (0.6, HW - 0.5, ZW), (0.6, 0, ZW), (0.6, 0, zn),
             lambda s, t: 0.5 * max(0.0, 1 - t / 50))
    # serradures, cargols perduts i un drap a peu de paret (la línia paret-terra no és neta)
    for k in range(26):
        x, z = 20 + hr(k, 1) * 600, ZW - 4 - hr(k, 2) * 24
        e.caixa('brossa', x, x + 2 + hr(k, 3) * 3, 0, 1.2, z, z + 2, F9 if k % 3 else WOOD2, 3.0 + hr(k, 4))
    e.cable('brossa', [(4, 0.8, _wz(70)), (14, 0.8, _wz(95)), (8, 0.8, _wz(118))],
            [(30, 20, 20), (60, 40, 34), (100, 74, 56), (140, 110, 84)], 2.2, gruix=4.0)       # un drap
    # el plomall (decorat), penjat del ganxo: dret, de cara (a la paret en escorç no es llegiria)
    if 'plomall' in estat:
        e.sprite('plomall', _plomall_pla().crop(PLOM_BOX), (164 - PLOM_BOX[0], 87 - PLOM_BOX[1]), PLOM_PEU)
    # la prestatgeria: el davant és el dibuix pla; el costat i la tapa, de fusta; separada de la paret
    sx0, sx1, sz0, sz1, sh = SHELF
    e.foscor('ombra_prest', (sx0 - 4, 0.6, ZW), (sx1 + 16, 0.6, ZW), (sx1 + 16, 0.6, sz0 - 14), (sx0 - 4, 0.6, sz0 - 14),
             lambda s, t: 0.55 * min(1.0, max(0.0, (ZW - sz0 + 14 - t) / 16)) * min(1.0, (sx1 - sx0 + 20 - s) / 16))

    def costat(s, t, P):                                                       # el costat: muntants i lleixes
        fy = SHELF_BOX[1] + t / sh * (SHELF_BOX[3] - SHELF_BOX[1])
        if s < 4 or s > sz1 - sz0 - 4:
            return 2.2 - (0.5 if s > 4 else 0)
        if any(abs(fy - y - 2) < 2.5 for y in (29, 63, 97, 132, 167, 198)):
            return 2.6
        return 0.5 + (hr(int(s // 5), int(fy // 34), 3) - 0.5) * 0.6
    e.caixa('prestatgeria', sx0, sx1, 0, sh, sz0, sz1, WOOD2, 2.0,
            cares={'davant': {'tex': (mob, SHELF_BOX)}, 'dreta': {'ramp': WOOD2, 'lvl': costat},
                   'esquerra': {'ramp': WOOD2, 'lvl': costat},
                   'dalt': {'ramp': WOOD2, 'lvl': _fusta(2.8, 4)}})
    # dalt de la prestatgeria, caixes oblidades
    e.caixa_girada('prestatgeria', sx0 + 40, (sz0 + sz1) / 2, 34, 24, 16, 0.12, WOOD2, 2.2, y0=sh,
                   cares={'dalt': {'ramp': WOOD2, 'lvl': 3.0}})
    e.caixa_girada('prestatgeria', sx1 - 50, (sz0 + sz1) / 2, 26, 20, 12, -0.2, PAPER, 1.6, y0=sh)
    # la bombeta que penja davant la prestatgeria
    e.cable('bombeta', [(BULB[0], HW, BULB[2] + 4), (BULB[0], BULB[1] + 14, BULB[2])], IRON, 1.6, gruix=1.2)
    e.sprite('bombeta', mob.crop(BULB_BOX), (PL.BULB_X - BULB_BOX[0], 13 - BULB_BOX[1]), (BULB[0], BULB[1] + 10, BULB[2]))
    # la taquilla de la Mira
    lx0, lx1, lz0, lz1, lh = LOCKER
    _ombra(e, 'ombra_taquilla', (lx0 + lx1) / 2, (lz0 + lz1) / 2, 30, 22, 0.55, dx=10, dz=-2)
    e.caixa('taquilla', lx0, lx1, 0, lh, lz0, lz1, GREEN, 2.0,
            cares={'davant': {'tex': (mob, LOCKER_BOX)}, 'dalt': {'ramp': GREEN, 'lvl': 3.4},
                   'esquerra': {'ramp': GREEN, 'lvl': lambda s, t, P: 1.6 + (0.8 if int(t) % 40 < 2 else 0)},
                   'dreta': {'ramp': GREEN, 'lvl': lambda s, t, P: 1.0 + (0.8 if int(t) % 40 < 2 else 0)}})
    # el banc de treball, girat: el tauler gruixut, les potes, el travesser i el prestatge de sota
    bx, bz, bw, bd, bh, ba = BENCH
    _ombra(e, 'ombra_banc', bx, bz, bw * 0.62, bd * 1.3, 0.6, dx=-10, dz=4)
    c, s_ = math.cos(ba), math.sin(ba)

    def Pb(lx, y, lz):
        return (bx + lx * c - lz * s_, y, bz + lx * s_ + lz * c)

    def bloc(sid, lx, lz, w, d, h, y0, ramp, lvl, cares=None):
        cx_, _, cz_ = Pb(lx, 0, lz)
        e.caixa_girada(sid, cx_, cz_, w, d, h, ba, ramp, lvl, y0=y0, cares=cares)
    for lx in (-bw / 2 + 6, bw / 2 - 8):
        for lz in (-bd / 2 + 4, bd / 2 - 4):
            bloc('banc', lx, lz, 5, 5, bh - 6, 0, WOOD2, 2.4,
                 cares={'davant': {'ramp': WOOD2, 'lvl': 3.0}, 'esquerra': {'ramp': WOOD2, 'lvl': 2.2},
                        'dreta': {'ramp': WOOD2, 'lvl': 1.4}})
    bloc('banc', 0, 0, bw - 12, bd - 8, 3, 14, WOOD2, 2.2, cares={'dalt': {'ramp': WOOD2, 'lvl': _fusta(2.6, 5)}})
    bloc('banc', -20, 0, 22, 18, 20, 17, IRON, 2.4,                                   # el bidó d'oli, a sota
         cares={'davant': {'ramp': IRON, 'lvl': lambda s, t, P: 1.8 if 6 < t < 12 and 3 < s < 19 else 2.6},
                'dalt': {'ramp': IRON, 'lvl': 3.4}})
    bloc('banc', 26, 2, 26, 16, 5, 17, PAPER, 2.0)                                    # els draps
    bloc('banc', 0, 0, bw, bd, 7, bh - 7, WOOD2, 2.6,
         cares={'dalt': {'ramp': WOOD2, 'lvl': lambda s, t, P: 3.2 + (hr(int(s // 22), 31) - 0.5) * 0.5
                         - (0.9 if s % 22 < 0.8 else 0) - (0.8 if fbm(s / 9, t / 7, 5) > 0.7 else 0)},
                'davant': {'ramp': WOOD2, 'lvl': lambda s, t, P: 3.4 - t * 0.25 - (0.8 if s % 22 < 0.8 else 0)},
                'esquerra': {'ramp': WOOD2, 'lvl': 2.4}, 'dreta': {'ramp': WOOD2, 'lvl': 1.6}})
    # damunt del banc: el registre obert, la safata de cargols, el cargol de banc i la llauna d'oli
    top = bh + 0.4
    e.quad('banc_coses', Pb(18, top, 6), Pb(52, top, 6), Pb(52, top, -10), Pb(18, top, -10), ramp=PAPER,
           lvl=lambda s, t, P: 4.2 - (1.4 if abs(s - 17) < 0.8 else 0) - (1.6 if int(t) % 4 == 0 and 2 < s % 17 < 15 else 0))
    e.cable('banc_coses', [Pb(46, top + 1, -12), Pb(54, top + 1, -16)], RED, 2.8, gruix=1.2)        # el llapis
    bloc('banc_coses', -14, 2, 26, 12, 3, bh, IRON, 2.4,
         cares={'dalt': {'ramp': F9, 'lvl': lambda s, t, P: 3.0 + hr(int(s), int(t), 2) * 2.0}})
    va, vb = Pb(-bw / 2 + 18, bh, -bd / 2 + 6), Pb(bw / 2 - 12, bh, 0)
    e.sprite('banc_coses', mob.crop(VICE_BOX), (462 - VICE_BOX[0], 147 - VICE_BOX[1]),
             va, escala_img=0.9)
    e.sprite('banc_coses', mob.crop(CAN_BOX), (572 - CAN_BOX[0], 147 - CAN_BOX[1]), vb, escala_img=0.9)
    # el llum d'esmalt que penja damunt del banc
    e.cable('llum', [(LAMP[0], HW, LAMP[2]), (LAMP[0], LAMP[1] + 14, LAMP[2])], IRON, 1.6, gruix=1.0)
    e.sprite('llum', mob.crop(LAMP_BOX), (PL.LAMP_X - LAMP_BOX[0], 106 - LAMP_BOX[1]), LAMP)
    # la caixa d'eines (decorat), a terra al costat del banc
    if 'caixa_eines' in estat:
        tx, tz, tw, td, th, ta = TOOLBOX
        _ombra(e, 'ombra_caixa', tx, tz, tw * 0.6, td * 0.9, 0.6, dx=-8, dz=4)
        ct, st_ = math.cos(ta), math.sin(ta)
        e.caixa_girada('caixa_eines', tx, tz, tw, td, th, ta, RED, 2.0,
                       cares={'davant': {'tex': (tex['caixa'], TB_BOX)},
                              'dalt': {'ramp': RED, 'lvl': lambda s, t, P: 2.6 - (0.9 if int(t) % 10 == 0 else 0)},
                              'dreta': {'ramp': RED, 'lvl': lambda s, t, P: 1.4 - (0.8 if int(t) % 11 == 10 else 0)},
                              'esquerra': {'ramp': RED, 'lvl': 1.8}})
        e.sprite('caixa_eines', tex['caixa'].crop(TOOLS_BOX), ((TOOLS_BOX[2] - TOOLS_BOX[0]) / 2, TOOLS_BOX[3] - TOOLS_BOX[1] - 1),
                 (tx - 2 * st_, th, tz + 2 * ct))
    # la pila de caixes i el bidó del mig
    px_, pz_ = STACK
    _ombra(e, 'ombra_pila', px_ + 8, pz_, 46, 30, 0.6, dx=-10, dz=6)

    def tapa(s, t, P):
        return 3.8 - (1.4 if int(s) % 9 == 0 else 0) + (hr(int(s // 9), 4) - 0.5) * 0.4

    def cara_caixa(lab):
        def L(s, t, P):
            v = 3.0 - (1.4 if int(t) % 9 == 8 else 0) + (hr(int(s // 3), int(t // 9), 5) - 0.5) * 0.4
            if s < 1.5 or s > 100 or t < 1.5:
                v += 0.8                                                               # el cantell
            if lab and 8 < s < 22 and 5 < t < 12:
                return 4.4 - (1.6 if int(t) == 8 and s < 19 else 0)                    # l'etiqueta d'inventari
            return v
        return L
    for cx, cz, w, d, h, a, y0, lab in ((px_, pz_, 44, 36, 34, -0.18, 0, True), (px_ + 4, pz_ + 2, 34, 28, 26, 0.12, 34, True),
                                        (px_ - 36, pz_ - 22, 30, 26, 22, 0.45, 0, False)):
        e.caixa_girada('pila', cx, cz, w, d, h, a, WOOD2, 2.0, y0=y0,
                       cares={'dalt': {'ramp': WOOD2, 'lvl': tapa}, 'davant': {'ramp': WOOD2, 'lvl': cara_caixa(lab)},
                              'dreta': {'ramp': WOOD2, 'lvl': lambda s, t, P: 2.0 - (0.9 if int(t) % 9 == 8 else 0)},
                              'esquerra': {'ramp': WOOD2, 'lvl': 2.4}})
    for y0_ in range(0, 40, 2):                                                     # el bidó, de xapa amb cèrcols
        e.tub('pila', (px_ + 40, y0_, pz_ - 12), (px_ + 40, y0_ + 2, pz_ - 12), 13, IRON,
              2.6 if y0_ in (12, 26) else 1.8, llum_dir=(0.8, 0.2))
    e.quad('pila', (px_ + 28, 40.5, pz_), (px_ + 52, 40.5, pz_), (px_ + 52, 40.5, pz_ - 24), (px_ + 28, 40.5, pz_ - 24),
           ramp=F9, forma=lambda s, t: (s - 12) ** 2 + (t - 12) ** 2 < 140,
           lvl=lambda s, t, P: 3.0 + hr(int(s), int(t), 7) * 2.0 - ((s - 12) ** 2 + (t - 12) ** 2) / 140)  # les barres de ferro-9
    # primer pla: caixes en silueta a baix a l'esquerra, el pilar de ferro a la dreta i una cadena que penja
    for cx, cz, w, d, h, a, y0 in ((-6, 30, 74, 56, 52, 0.25, 0), (-10, 36, 54, 44, 30, 0.1, 52), (70, -4, 52, 40, 30, -0.2, 0)):
        e.caixa_girada('primer_pla', cx, cz, w, d, h, a, DARK, 1.6, y0=y0,
                       cares={'dalt': {'ramp': DARK, 'lvl': lambda s, t, P: 3.0 - (1.2 if int(s) % 12 == 0 else 0)},
                              'davant': {'ramp': DARK, 'lvl': lambda s, t, P: 1.2 + (0.6 if int(t) % 10 == 0 else 0)},
                              'dreta': {'ramp': DARK, 'lvl': 2.0}})
    e.roca('primer_pla', (352, 0, 62), 34, DARK, lvl=2.2, llum_dir=(-0.7, -0.6), aplana=0.55, seed=6)   # un sac de llimadures
    e.tub('primer_pla', (PILLAR[0], 0, PILLAR[1]), (PILLAR[0], HW, PILLAR[1]), 9, DARK, 2.0, brides=46, llum_dir=(-0.8, 0.3))
    e.cable('primer_pla', [(430, HW, 40), (434, 150, 40), (430, 112, 42)], DARK, 2.6, gruix=2.4)
    e.cable('primer_pla', [(446, HW, 44), (442, 160, 44), (444, 130, 43)], DARK, 2.0, gruix=2.4)
    return e


# ─── Composició i llum ──────────────────────────────────────────────────────

def _proj(P):
    u, v, _ = CAM.projecta(P)
    return u, v


@functools.lru_cache(maxsize=None)
def _textures():
    return {'paret': _paret(), 'mobles': _mobles(), 'caixa': _caixa_pla()}


def _fx(cv):
    """Les lluïssors de les bombetes i l'escalfor del llum, damunt de l'escena (com al dibuix pla)."""
    lu, lv = _proj((LAMP[0], LAMP[1] - 2, LAMP[2]))
    bu, bv = _proj((BULB[0], BULB[1] + 4, BULB[2]))
    cv.glow(lu, lv + 4, 50, (255, 226, 150), 0.42)
    cv.glow(bu, bv, 44, (255, 226, 160), 0.45)
    cv.tint(0, 0, W - 1, BOTTOM, (255, 190, 110),
            lambda x, y: max(0, 1 - math.hypot(x - lu, (y - lv - 20) * 0.9) / 220) ** 2 * 0.16
            + max(0, 1 - math.hypot(x - bu, (y - bv - 10) * 0.9) / 190) ** 2 * 0.12)


def _render(estat=frozenset(), tex=None):
    cv = Canvas(light=LIGHT)
    e = escena(cv, tex or _textures(), estat)
    _fx(cv)
    cv.rect(0, BOTTOM + 1, W - 1, H - 1, [(0, 0, 0)], 0, lit=0)    # la barra de verbs: negre
    return cv.img, e


@functools.lru_cache(maxsize=None)
def _base():
    return _render()


def bg(cv):
    cv.img.paste(_base()[0])
    cv.P = cv.img.load()


def _diff(img, base):
    """Els píxels d'`img` que no són iguals a `base` (la resta, transparent)."""
    from PIL import Image, ImageChops
    d = ImageChops.difference(base.convert('RGB'), img.convert('RGB')).convert('L').point(lambda v: 255 if v else 0)
    out = Image.new('RGBA', img.size, (0, 0, 0, 0))
    out.paste(img, (0, 0), d)
    return out


def _decorat(*estat):
    """Un decorat: la sala amb aquell estat, menys la de sempre (només el que canvia)."""
    def draw(cv):
        img, _ = _render(frozenset(estat))
        cv.img.alpha_composite(_diff(img, _base()[0]))
        cv.P = cv.img.load()
    return draw


PROPS = {'plomall': _decorat('plomall'), 'caixa_eines': _decorat('caixa_eines')}


# ─── Animació: la pols a la llum de les bombetes i una arna que volta el llum ───

def _moth(cv, tt, cx, cy, k):
    ph = 2 * math.pi * tt
    x = round(cx + 20 * k * math.sin(ph) + 5 * k * math.sin(ph * 3 + 1.1))
    y = round(cy + 7 * k * math.sin(ph * 2 + 0.5) + 3 * k * math.cos(ph * 5))
    up = math.sin(ph * 11) > 0
    lit_side = math.cos(ph) < 0
    wing = (196, 176, 140) if lit_side else (120, 100, 80)
    wing2 = (150, 132, 104) if lit_side else (92, 76, 62)
    body = (58, 46, 40)
    cv.flat(x, y, body)
    cv.flat(x, y + 1, body)
    if up:
        for d, col in ((1, wing), (2, wing2)):
            cv.flat(x - d, y - d, col); cv.flat(x + d, y - d, col)
    else:
        cv.flat(x - 1, y, wing); cv.flat(x + 1, y, wing)
        cv.flat(x - 2, y + 1, wing2); cv.flat(x + 2, y + 1, wing2)


def _frames(n=24):
    base, _ = _base()
    lu, lv = _proj(LAMP)
    bu, bv = _proj(BULB)
    k = CAM.escala(LAMP)
    _, tv = _proj((LAMP[0], BENCH[4], LAMP[2]))

    def cone(x, y):
        if not lv + 4 <= y <= tv:
            return 0.0
        half = 12 * k + (y - lv) * 0.8
        return max(0.0, min(1.0, (1 - abs(x - lu) / half) * 2.2)) * (1 - (y - lv) / max(1, tv - lv))

    def halo(x, y):
        return max(0.0, 1 - math.hypot(x - bu, (y - bv) * 1.2) / 50) ** 0.8
    out = []
    for i in range(n):
        tt = i / n
        cv = Canvas(light=LIGHT, img=base.copy())
        dust(cv, tt, 20, 31, (lu - 34, lv + 4, lu + 34, tv), (255, 236, 190), 0.7, cone, fall=(3, 7), wander=2.7)
        dust(cv, tt, 18, 32, (bu - 40, bv - 4, bu + 40, bv + 44), (255, 232, 180), 0.6, halo, fall=(-3, 7), wander=2.7)
        _moth(cv, tt, lu, lv - 8 * k, k)
        out.append(_diff(cv.img, base))
    return out


ANIMS = {'ambient': {'frames': _frames, 'frameDuration': 130}}


def _amo(ids):
    def mask(x, y):
        _, e = _base()
        return e.ids[e.amo[y * e.cv.w + x]] in ids
    return mask


def _p(x, z, y=0.0):
    u, v, _ = CAM.projecta((x, y, z))
    return round(u), round(v)


def _base_de(cx, cz, w, d, ang):
    """La y de pantalla del cantó de davant d'una caixa girada (la seva línia base)."""
    return max(_p(x, z)[1] for x, z in _cantons(cx, cz, w, d, ang))


def _llesques(ids, cx, cz, w, d, ang, n, props=(), prop_u=None):
    """Les capes del davant d'un moble llarg i girat: la vora de davant i la de darrere fan diagonal a la pantalla,
    i una sola línia base no deixaria passar per davant d'una punta i per darrere de l'altra. Es talla en `n`
    franges verticals de pantalla, cadascuna amb la seva línia base (entre la vora de darrere i la de davant del
    terra que l'envolta, en aquella franja). Els `props` van a la franja on cau `prop_u`."""
    c, s_ = math.cos(ang), math.sin(ang)

    def vora(lz):
        return [_p(cx + lx * c - lz * s_, cz + lx * s_ + lz * c)
                for lx in [-(w / 2) + w * k / 60 for k in range(61)]]
    davant, darrere = vora(-d / 2), vora(d / 2)
    us = [u for u, _ in davant + darrere]
    u0, u1 = min(us), max(us)
    talls = [u0 + (u1 - u0) * k / n for k in range(n + 1)]
    talls[0], talls[-1] = -1, W + 1
    out = []
    for k in range(n):
        a, b = talls[k], talls[k + 1]
        dv = [v for u, v in davant if a <= u < b] or [max(v for _, v in davant)]
        bv = [v for u, v in darrere if a <= u < b] or [min(v for _, v in darrere)]
        base = round((min(dv) + max(bv)) / 2)
        lay = {'id': f'davant_{ids[0]}_{k + 1}', 'baseline': base, 'zIndex': 20,
               'mask': (lambda a, b: lambda x, y: a <= x < b and _amo(set(ids))(x, y))(a, b)}
        if prop_u is not None and a <= prop_u < b:
            lay['props'] = tuple(props)
        out.append(lay)
    return out


# Capes del davant: el primer pla (sempre davant), la pila de caixes i el banc (en franges, amb la caixa d'eines).
FRONT = [
    {'id': 'davant', 'mask': _amo({'primer_pla'}), 'baseline': 999, 'zIndex': 20},
    {'id': 'davant_pila', 'mask': _amo({'pila'}), 'baseline': _base_de(STACK[0], STACK[1], 60, 40, 0.0) - 8, 'zIndex': 20},
] + _llesques(('banc', 'banc_coses', 'llum'), BENCH[0], BENCH[1], BENCH[2] + 12, BENCH[3] + 12, BENCH[5], 3,
              props=('caixa_eines',), prop_u=_p(TOOLBOX[0], TOOLBOX[1])[0])


# ─── Geometria (coordenades de sala, projectades) ────────────────────────────

def _rect_mon(*Ps):
    pts = [CAM.projecta(P) for P in Ps]
    return (max(0, round(min(p[0] for p in pts))), max(0, round(min(p[1] for p in pts))),
            min(W - 1, round(max(p[0] for p in pts))), min(BOTTOM, round(max(p[1] for p in pts))))


def _escala_a(v):
    """L'escala d'un personatge amb els peus a la y de pantalla `v` (al terra, la profunditat només depèn de v)."""
    lo, hi = 1.0, 3000.0
    for _ in range(60):
        z = (lo + hi) / 2
        if CAM.projecta((260, 0, z))[1] > v:
            lo = z
        else:
            hi = z
    return CAM.escala((260, 0, (lo + hi) / 2))


# El terra on es camina (al món): des de les portes fins a la taquilla, davant la prestatgeria i el banc.
WALK_MON = [(14, 252), (14, 110), (70, 62), (200, 62), (262, 84), (330, 110), (400, 136), (480, 166), (500, 190),
            (500, 262), (406, 262), (406, 292), (246, 292), (246, 254)]
_WALK = [_p(x, z) for x, z in WALK_MON]
_V_FONS, _V_PROP = min(v for _, v in _WALK), max(v for _, v in _WALK)
# La pila de caixes del mig: no es trepitja, però s'hi pot fer la volta.
_FORAT = [_p(x, z) for x, z in ((STACK[0] - 60, STACK[1] + 20), (STACK[0] + 58, STACK[1] + 22),
                                 (STACK[0] + 58, STACK[1] - 42), (STACK[0] - 60, STACK[1] - 46))]
# El banc: tampoc es trepitja; s'hi passa per davant i per darrere (cap a la taquilla).
_FORAT_BANC = [_p(x, z) for x, z in _cantons(BENCH[0], BENCH[1], BENCH[2] + 12, BENCH[3] + 12, BENCH[5])]

def _rect_sprite(peu, box, ref):
    """El rectangle de pantalla d'un sprite dret: `box` al dibuix pla, `ref` = el punt del dibuix que toca a `peu`."""
    k = CAM.escala(peu)
    u, v, _ = CAM.projecta(peu)
    return (round(u - (ref[0] - box[0]) * k) - 1, round(v - (ref[1] - box[1]) * k) - 1,
            round(u + (box[2] - ref[0]) * k) + 1, round(v + (box[3] - ref[1]) * k) + 1)


_DOOR_C = (_wz(11), _wz(77), _y(207), _y(87))
_DOOR_D = (_wz(87), _wz(146), _y(208), _y(80))

GEOMETRIA = {
    'things': {
        'porta_calderes': {'rect': _rect_mon((0, _DOOR_C[3], _DOOR_C[0]), (0, _DOOR_C[2], _DOOR_C[1])), 'walk': _p(26, 158)},
        'porta_despatx': {'rect': _rect_mon((0, _DOOR_D[3], _DOOR_D[0]), (0, _DOOR_D[2], _DOOR_D[1])), 'walk': _p(26, 230)},
        'plomall': {'rect': _rect_sprite(PLOM_PEU, PLOM_BOX, (164, 80)), 'walk': _p(30, 248)},
        'prestatges': {'rect': _rect_mon((SHELF[0], SHELF[4], SHELF[2]), (SHELF[1], 0, SHELF[2]), (SHELF[1], SHELF[4], SHELF[3])),
                       'walk': _p(170, 244)},
        'caixa_eines': {'rect': _rect_mon(*[(x, y, z) for x, z in _cantons(*TOOLBOX[:4], TOOLBOX[5]) for y in (0, TOOLBOX[4] + 20)]),
                        'walk': _p(TOOLBOX[0] + 4, TOOLBOX[1] - 52)},
    },
    'spawns': {'iri': _p(70, 150), 'cargol': _p(196, 238), 'mira': _p(440, 230)},
    'walkable': _WALK,
    'forats': [_FORAT, _FORAT_BANC],
    'floorSquash': 0.42,                           # (la càmera, picada: el terra es veu aixafat)
    # L'ombra de contacte: la llum dominant és el llum penjant del banc.
    'characterShadow': {'enabled': True, 'color': '#120806', 'alpha': 0.45, 'squash': 0.4, 'core': 0.6,
                        'light': {'x': _p(LAMP[0], LAMP[2])[0], 'y': _p(LAMP[0], LAMP[2])[1], 'stretch': 0.7,
                                  'reach': 160}},
    'regions': [{'id': 'perspectiva', 'active': True, 'scaleEnabled': True, 'scaleWalkSpeed': True,
                 'scaleTop': round(_escala_a(_V_FONS - 2), 3), 'scaleBottom': round(_escala_a(_V_PROP + 2), 3),
                 'points': [(0, _V_FONS - 2), (W - 1, _V_FONS - 2), (W - 1, _V_PROP + 2), (0, _V_PROP + 2)]}],
    # la llum de la sala sobre els personatges, en temps d'execució
    'characterLights': {
        'ambient': '#8a7468',                                                           # magatzem fosc, càlid
        'lights': [
            {'x': _p(LAMP[0], LAMP[2], LAMP[1])[0], 'y': _p(LAMP[0], LAMP[2], LAMP[1])[1], 'radius': 230,
             'color': '#ffd08c', 'intensity': 1.0},                                     # el llum del banc
            {'x': _p(BULB[0], BULB[2], BULB[1])[0], 'y': _p(BULB[0], BULB[2], BULB[1])[1], 'radius': 210,
             'color': '#ffc880', 'intensity': 0.8},                                     # la bombeta
        ],
    },
}

# Coses per mirar (tasca 065): rectangles de pantalla i el punt on s'hi va.
GEOMETRIA['things'].update({
    'taquilla': {'rect': (472, 60, 522, 185), 'walk': (455, 200)},
    'tauler_inventari': {'rect': (357, 40, 457, 105), 'walk': (400, 200)},
    'banc': {'rect': (362, 118, 472, 200), 'walk': (400, 210)},
    'retol': {'rect': (62, 17, 155, 45), 'walk': GEOMETRIA['things']['porta_calderes']['walk']},
})
