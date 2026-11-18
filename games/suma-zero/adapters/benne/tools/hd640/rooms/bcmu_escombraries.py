"""
La sala d'escombraries del tercer pis del BCMU (Escenes 5 i 6, l'Iri). EN 3D (hd640/tres_d.py), a 1×.
On van jubilar el Llibre Major.

Una càmera alta, a la dreta, que mira de biaix la cantonada del fons a l'esquerra:
  - a la paret de l'esquerra, en escorç, la **porta** del passadís (xapa grisa, la finestreta de vidre armat);
  - a la paret del fons: el rellotge aturat, el rètol CONFIDENCIAL, el **conducte** d'escombraries amb la comporta,
    l'**estació del tub** de 1958 i el **panell** de NETA-3; formigó gris amb regalims i la franja verda d'hospital;
  - **EL LLIBRE MAJOR**: el mainframe gris de 1984, separat de la paret i girat, amb tres cares (el frontal del dibuix
    pla amb la pantalla de fòsfor verd, el costat amb les reixetes i la tapa amb pols) i la lleixa del teclat que
    sobresurt; la seva claror verda al terra;
  - a la cantonada, les **bosses** de paper triturat, panxudes, una d'esventrada amb el confeti escampat;
  - a la dreta, la base de càrrega de NETA-3 a terra i les caixes d'arxiu apilades (s'hi passa per darrere);
  - primer pla: un contenidor de rodes en silueta a baix a l'esquerra i una canonada grossa que fuig pel sostre.

Tot el detall de les parets i del frontal del Llibre Major ve del dibuix pla de sempre
(bcmu_escombraries_pla_comu.py), projectat. Damunt de tot, la llum de Suma Zero (hd640/llum.py): el fluorescent
brut, el verd de la pantalla, el bloom i la corba de to.

El món: x a la dreta (0 = la paret de la porta), y amunt (0 = el terra), z cap al fons (300 = la paret del fons);
1 unitat = 1 píxel de sala a la distància on un personatge fa ≈111 px (escala 1).
"""
import functools
import math

import hd640  # noqa: F401  (abans de cap hd.rooms: posa la llibreria a 640×360)
from hd640 import llum
from hd.pix import Canvas, Light, W, H, hr
from hd.rooms.comu import _diff, outline, SHEET, CARD
from hd.rooms.exterior import fbm
from hd640.rooms import bcmu_escombraries_pla_comu as PL
from hd640.rooms.bcmu_escombraries_pla_comu import MAIN, BEIGE, BAG, STRIPE, DROP, CONCB, SLATE
from hd640.tres_d import Camera, Escena, Llum

BOTTOM = 259                                       # la sala acaba aquí (a sota, la barra de verbs)
ZW = 300                                           # la paret del fons
HW = PL.FLOOR_Y                                    # l'alçada de les parets: 200 (el dibuix pla sencer)
XC = 100                                           # al dibuix pla, la cantonada: a l'esquerra, la paret de la porta
LL = 640                                           # l'amplada de la paret llisa (fora del dibuix pla)
XR = W - XC + LL                                   # on s'acaba la paret del fons, a la dreta (fora de la pantalla)
LEDGER = (284, 236, 139, 70, -0.32)                # el Llibre Major: x, z del centre, ample, fons, gir
LBOX = (315, 48, 454, PL.FLOOR_Y)                  # el frontal del Llibre Major, al dibuix pla
LH = PL.FLOOR_Y - LBOX[1]                          # l'alçada del Llibre Major: 152
SHELF = (PL.FLOOR_Y - 153, PL.FLOOR_Y - 141, 16)   # la lleixa del teclat: y de sota, y de dalt, quant sobresurt
BOXES = (466, 200, 0.42)                           # les caixes d'arxiu: x, z, gir
CAIXES = ((0, 0, 0, 0.0), (44, 22, 0, 0.18), (3, 4, 29, -0.16))  # les caixes: dx, dz, y de sota, gir de més
DOCK = (476, 528, 266, 296)                        # la base de càrrega de NETA-3: x0, x1, z0, z1
BIN = (46, 58)                                     # el contenidor del primer pla (x, z)
STAIN = (196, 274)                                 # la taca d'humitat on cau la gota (x, z)


def _w(fx):
    """Una x del dibuix pla de la paret del fons → la x del món."""
    return fx - XC


def _wz(fx):
    """Una x del dibuix pla de la paret de la porta → la z del món."""
    return ZW - XC + fx


def _y(fy):
    """Una y del dibuix pla (el terra, a 200) → l'alçada del món."""
    return PL.FLOOR_Y - fy


def _fw(fx, fy):
    if fx < XC:
        return (0, _y(fy), _wz(fx))
    return (_w(fx), _y(fy), ZW)


def _llibre(lx, y, lz):
    """Un punt del Llibre Major (lx, lz des del centre, abans de girar) → el món."""
    cx, cz, _, _, ang = LEDGER
    c, s_ = math.cos(ang), math.sin(ang)
    return (cx + lx * c - lz * s_, y, cz + lx * s_ + lz * c)


def _llibre_pla(fx, fy):
    """Un punt del dibuix pla del frontal del Llibre Major → el punt del món (al frontal girat)."""
    return _llibre(fx - (LBOX[0] + LBOX[2]) / 2, _y(fy), -LEDGER[3] / 2)


CAM = Camera(pos=(380, 185, -230), yaw=-0.28, pitch=0.18, f=480, centre=(320, 104))

LIGHT = Light(ambient=0.0, vignette=None, floor_fade=None)  # (la llum és la del món: la de l'Escena)
TUBE_C = (_w(PL.TUBE[0]), _y(10), ZW - 6)          # el fluorescent brut
SCREEN_C = _llibre_pla((PL.SCREEN[0] + PL.SCREEN[2]) / 2, (PL.SCREEN[1] + PL.SCREEN[3]) / 2)
SCREEN_L = (SCREEN_C[0] - 12, SCREEN_C[1], SCREEN_C[2] - 30)    # la llum de la pantalla, una mica al davant
PANEL_C = (_w(542), _y(110), ZW - 6)
LLUMS = [Llum(TUBE_C, 330, 2.0, power=1.5),                       # el fluorescent
         Llum(SCREEN_L, 240, 1.8, power=1.6),                     # la pantalla del Llibre Major
         Llum(PANEL_C, 60, 0.5, power=2.0)]                       # el panell de NETA-3


# ─── Les textures: el dibuix pla de sempre ───────────────────────────────────

LIGHT_TEX = Light(ambient=-0.5, vignette=None, floor_fade=None)
LIGHT_TEX.point(PL.TUBE[0], PL.TUBE[1] + 5, r=293, k=2.0, squash=0.9, power=1.5)
LIGHT_TEX.point(384, 93, r=200, k=1.4, squash=1.1, power=1.8)
LIGHT_TEX.point(547, 123, r=53, k=0.5, squash=1.0, power=2.0)


def _endoll(cv):
    """L'endoll de la paret on va el cable del Llibre Major."""
    cv.rect(279, 151, 287, 159, SLATE, 3.0)
    outline(cv, 279, 151, 287, 159, SLATE)


def _paret(tube=1.0):
    """Les parets planes, de cara, sense el Llibre Major, les bosses ni les caixes: la porta, el rellotge, el rètol,
    el conducte, el tub i el panell."""
    cv = Canvas(light=LIGHT_TEX)
    PL.wall(cv)
    PL.ceiling(cv, tube)
    PL.door(cv)
    PL.wall_bits(cv)
    PL.chute(cv)
    PL.tub_station(cv, 469, 80, 496, 147, vell=True)
    PL.neta_panel(cv)
    _endoll(cv)
    cv.tint(167, 27, 507, 200, (60, 255, 140), lambda x, y: 0.06 * PL.green_cast(x, y))
    return cv.img


@functools.lru_cache(maxsize=None)
def _paret_base():
    return _paret()


@functools.lru_cache(maxsize=None)
def _llisa():
    cv = Canvas(light=LIGHT_TEX)
    PL.wall(cv)
    PL.ceiling(cv, 0.0)
    return cv.img


def _llibre_img(frame=0, cursor=True):
    """El Llibre Major pla, de cara, sobre transparent (el frontal)."""
    cv = Canvas(light=LIGHT_TEX, transparent=True)
    PL.ledger(cv)
    if frame:
        PL.leds(cv, frame=frame)
    if not cursor:
        cx, cy = PL.CURSOR
        cv.rect(cx, cy, cx + 3, cy + 5, PL.SCREENB, 1.4, lit=0)
    return cv.img


@functools.lru_cache(maxsize=None)
def _llibre_base():
    return _llibre_img()


@functools.lru_cache(maxsize=None)
def _textures():
    return {'paret': _paret_base(), 'llisa': _llisa(), 'llibre': _llibre_base()}


# ─── Les superfícies ────────────────────────────────────────────────────────

def _ciment(s, t, P):
    """Ciment amb taques i lloses (en coordenades del món: les juntes s'empetiteixen cap al fons)."""
    x, z = P[0], P[2]
    if (x + 7) % 90 < 1.0 or z % 80 < 1.0:
        return 2.4                                                    # les juntes de dilatació
    n = (fbm(x / 50, z / 30, 5) - 0.5) * 0.9 + (hr(int(x // 3), int(z // 2), 7) - 0.5) * 0.4
    v = 3.4 + n
    for cx, cz, rx, rz in ((STAIN[0], STAIN[1], 34, 14), (430, 160, 46, 20), (90, 140, 26, 12)):
        d = ((x - cx) / rx) ** 2 + ((z - cz) / rz) ** 2
        if d < 1:
            v -= 0.9 * (1 - d) ** 0.5                                 # les taques d'humitat i d'oli
    return v


def _bosses(e):
    """Les bosses de paper triturat a la cantonada: panxudes, amb el nus, una d'esventrada i el confeti."""
    for k, (x, z, r, a) in enumerate(((22, 268, 22, 0.75), (60, 286, 20, 0.8), (98, 288, 18, 0.85), (36, 236, 19, 0.8),
                                      (74, 258, 25, 0.75), (28, 286, 14, 0.9), (54, 272, 15, 1.0))):
        y0 = 26 if k >= 5 else 0                                      # dues, a sobre de les altres
        e.foscor('ombra_bosses', (x - r - 6, 0.6, z + r), (x + r + 10, 0.6, z + r), (x + r + 10, 0.6, z - r - 8),
                 (x - r - 6, 0.6, z - r - 8), lambda s, t, r=r: 0.6 * max(0.0, 1 - ((s - r - 6) / (r + 6)) ** 2
                                                                      - ((t - r - 4) / (r + 4)) ** 2) * 1.5)
        e.roca('bosses', (x, y0, z), r, BAG, lvl=1.7, llum_dir=(0.6, -0.7), aplana=a, seed=k * 3 + 1)
        top = y0 + r * a * 1.6
        e.tub('bosses', (x, top - 2, z), (x - 2, top + 6, z), 2.0, BAG, 2.8)
        e.tub('bosses', (x - 2, top + 6, z), (x - 6, top + 10, z), 1.0, BAG, 3.2)
    # el confeti de la bossa esventrada, escampat cap a la llum
    for i in range(70):
        cx = 78 + (hr(i, 51) - 0.3) * 70
        cz = 230 - hr(i, 52) ** 0.7 * 60 + (hr(i, 55) - 0.5) * 20
        L = 1.2 + hr(i, 53) * 1.8
        a = hr(i, 54) * math.pi
        dx, dz = math.cos(a) * L, math.sin(a) * L
        e.quad('confeti', (cx, 0.7, cz + 0.6), (cx + dx, 0.7, cz + dz + 0.6), (cx + dx, 0.7, cz + dz), (cx, 0.7, cz),
               ramp=SHEET, lvl=3.6 + hr(i, 56), dues_cares=True)


def escena(cv, tex, estat=frozenset()):
    """Tota la sala, de lluny a prop. → l'Escena (qui ha pintat què)."""
    e = Escena(cv, CAM, LLUMS, ambient=-0.9)
    zn = CAM.pos[2] + 60
    paret, llisa, llibre = tex['paret'], tex['llisa'], tex['llibre']
    # el sostre (gairebé no es veu)
    e.quad('sostre', (0, HW, zn), (XR, HW, zn), (XR, HW, ZW), (0, HW, ZW), ramp=CONCB, lvl=1.2, dues_cares=True)
    # la paret de la porta (x = 0): el dibuix pla (x 0..100) a tocar de la cantonada; cap a la càmera, formigó
    e.quad('paret_esq_prop', (0, HW, ZW - XC - LL), (0, HW, ZW - XC), (0, 0, ZW - XC), (0, 0, ZW - XC - LL),
           tex=(llisa, (0, 0, LL, PL.FLOOR_Y)))
    e.quad('paret_esq', (0, HW, ZW - XC), (0, HW, ZW), (0, 0, ZW), (0, 0, ZW - XC), tex=(paret, (0, 0, XC, PL.FLOOR_Y)))
    # la paret del fons (z = 300): el dibuix pla (x 100..640) i, a la dreta, més formigó
    e.quad('paret_fons', (0, HW, ZW), (W - XC, HW, ZW), (W - XC, 0, ZW), (0, 0, ZW), tex=(paret, (XC, 0, W, PL.FLOOR_Y)))
    e.quad('paret_fons_dreta', (W - XC, HW, ZW), (XR, HW, ZW), (XR, 0, ZW), (W - XC, 0, ZW), tex=(llisa, (0, 0, LL, PL.FLOOR_Y)))
    # el terra, la reixa del desguàs i la claror verda de la pantalla
    e.quad('terra', (0, 0, ZW), (XR, 0, ZW), (XR, 0, zn), (0, 0, zn), ramp=CONCB, lvl=_ciment)
    gx, gz = 178, 196
    e.quad('desguas', (gx - 14, 0.4, gz + 6), (gx + 14, 0.4, gz + 6), (gx + 14, 0.4, gz - 6), (gx - 14, 0.4, gz - 6),
           ramp=SLATE, lvl=lambda s, t, P: 2.8 if int(s) % 4 == 0 else 0.4,
           forma=lambda s, t: ((s - 14) / 14) ** 2 + ((t - 6) / 6) ** 2 < 1)
    e.claror((STAIN[0] - 4, 0.5, STAIN[1] + 2), (STAIN[0] + 4, 0.5, STAIN[1] + 2), (STAIN[0] + 4, 0.5, STAIN[1] - 2),
             (STAIN[0] - 4, 0.5, STAIN[1] - 2), (200, 220, 230), lambda s, t: 0.35)              # la brillantor de l'aigua
    sx, _, sz = SCREEN_L
    e.claror((sx - 170, 0.4, ZW), (sx + 170, 0.4, ZW), (sx + 170, 0.4, sz - 190), (sx - 170, 0.4, sz - 190),
             (60, 255, 140), lambda s, t: 0.16 * max(0.0, 1 - abs(s - 170) / 170) * max(0.0, 1 - abs(t - (ZW - sz) - 40) / 150))
    # la foscor dels racons i del sostre
    e.foscor('racons', (0, 0.5, ZW), (XR, 0.5, ZW), (XR, 0.5, zn), (0, 0.5, zn),
             lambda s, t: max(0.55 * max(0.0, 1 - t / 28), 0.5 * max(0.0, 1 - s / 30)))
    e.foscor('cantonada', (0, HW, ZW - 0.5), (70, HW, ZW - 0.5), (70, 0, ZW - 0.5), (0, 0, ZW - 0.5),
             lambda s, t: 0.5 * max(0.0, 1 - s / 70))
    e.foscor('cantonada2', (0.5, HW, ZW - 70), (0.5, HW, ZW), (0.5, 0, ZW), (0.5, 0, ZW - 70),
             lambda s, t: 0.5 * max(0.0, 1 - (70 - s) / 70))
    e.foscor('sostre_fosc', (0, HW - 0.5, ZW - 0.6), (XR, HW - 0.5, ZW - 0.6), (XR, 0, ZW - 0.6), (0, 0, ZW - 0.6),
             lambda s, t: 0.3 * max(0.0, 1 - t / 30))
    # la base de càrrega de NETA-3: la placa de franges i el pal dels contactes, i el cable que baixa del panell
    dx0, dx1, dz0, dz1 = DOCK
    e.foscor('ombra_base', (dx0 - 4, 0.5, dz1 + 2), (dx1 + 6, 0.5, dz1 + 2), (dx1 + 6, 0.5, dz0 - 6), (dx0 - 4, 0.5, dz0 - 6),
             lambda s, t: 0.5 * max(0.0, 1 - abs(s - (dx1 - dx0 + 10) / 2) / ((dx1 - dx0 + 10) / 2)) * min(1.0, t / 6))
    e.caixa('base', dx0, dx1, 0, 2.5, dz0, dz1, STRIPE, 1.4,
            cares={'dalt': {'ramp': STRIPE, 'lvl': lambda s, t, P: 2.6 if int((P[0] + P[2]) // 6) % 2 else 0.4},
                   'davant': {'ramp': STRIPE, 'lvl': 1.0}})
    px_ = (dx0 + dx1) / 2
    e.caixa('base', px_ - 9, px_ + 9, 2.5, 20, dz1 - 8, dz1, PL.MAIN, 3.0,
            cares={'davant': {'ramp': PL.MAIN, 'lvl': lambda s, t, P: 1.6 if 3 < s < 5 or 12 < s < 14 else 3.2}})
    e.cable('cables', [(_w(557), _y(147), ZW - 1), (_w(562), 20, ZW - 2), (_w(566), 0.8, ZW - 6), (px_ - 4, 0.8, dz1 - 2)],
            SLATE, 1.6, gruix=2.0)
    # el cable gruixut del Llibre Major, de l'endoll de la paret al costat del moble
    e.cable('cables', [(_w(283), _y(156), ZW - 1), (_w(280), 6, ZW - 3), (_w(280) + 4, 0.8, ZW - 14),
                       _llibre(-60, 0.8, 30)], SLATE, 1.6, gruix=3.0)
    # les bosses de paper triturat, a la cantonada
    _bosses(e)
    # EL LLIBRE MAJOR: separat de la paret i girat; el frontal del dibuix pla, el costat amb reixetes, la tapa amb pols
    cx, cz, lw, ld, ang = LEDGER
    c, s_ = math.cos(ang), math.sin(ang)
    e.foscor('ombra_llibre', _llibre(-lw / 2 - 10, 0.6, ld / 2 + 10), _llibre(lw / 2 + 16, 0.6, ld / 2 + 10),
             _llibre(lw / 2 + 16, 0.6, -ld / 2 - 22), _llibre(-lw / 2 - 10, 0.6, -ld / 2 - 22),
             lambda s, t: 0.65 * min(1.0, max(0.0, min(s, lw + 26 - s) / 14)) * min(1.0, max(0.0, (ld + 32 - t) / 16 + 0.3)))

    def costat(s, t, P):
        v = 2.0 + (fbm(s / 20, t / 30, 3) - 0.5) * 0.4
        if 20 < t < 70 and 10 < s < ld - 10 and int(t) % 4 < 2:
            v = 0.8 if int(t) % 4 == 0 else 3.0                      # les reixetes de ventilació
        if t > LH - 7:
            v = 1.0                                                   # el sòcol
        return v

    def tapa(s, t, P):
        v = 4.2 + (fbm(s / 14, t / 9, 5) - 0.5) * 0.6
        if hr(int(s), int(t), 61) > 0.93:
            v -= 0.8                                                  # la pols
        return v
    e.caixa_girada('llibre', cx, cz, lw, ld, LH, ang, MAIN, 2.6,
                   cares={'davant': {'tex': (llibre, LBOX)}, 'dalt': {'ramp': MAIN, 'lvl': tapa},
                          'dreta': {'ramp': MAIN, 'lvl': costat}, 'esquerra': {'ramp': MAIN, 'lvl': costat}})
    # la lleixa del teclat, que sobresurt del frontal: les tecles beix, el teclat numèric i la tecla vermella
    y0, y1, pr = SHELF
    sc = _llibre(0, 0, -ld / 2 - pr / 2)

    def tecles(s, t, P):
        if s < 2 or s > lw + 4 or t < 1.5:
            return 3.4
        row, col = int((t - 2) // 3), int((s - 6) // 4)
        if 0 <= row < 4 and 0 <= col < 26 and (s - 6) % 4 < 3 and (t - 2) % 3 < 2:
            if row == 3 and 7 <= col <= 17:
                return 5.4 if (t - 2) % 3 < 1 else 4.6                # la barra d'espai
            return 5.2 if (t - 2) % 3 < 1 else 4.4
        if lw - 20 < s < lw - 6 and 2 < t < 12:
            return 2.6 if (int(s) % 4 < 3 and int(t) % 3 < 2) else 1.6  # el teclat numèric
        return 2.6
    e.caixa_girada('llibre', sc[0], sc[2], lw + 6, pr, y1 - y0, ang, BEIGE, 2.4, y0=y0,
                   cares={'dalt': {'ramp': BEIGE, 'lvl': tecles}, 'davant': {'ramp': BEIGE, 'lvl': 2.6},
                          'dreta': {'ramp': BEIGE, 'lvl': 2.0}})
    kr = _llibre(lw / 2 - 16, y1 + 0.4, -ld / 2 - pr + 5)
    e.caixa_girada('llibre', kr[0], kr[2], 11, 3, 1.0, ang, PL.REDL, 2.2, y0=y1)
    # les caixes d'arxiu apilades, a la dreta, una mica girades cadascuna
    bx, bz, ba = BOXES
    e.foscor('ombra_caixes', (bx - 50, 0.6, bz + 40), (bx + 60, 0.6, bz + 40), (bx + 60, 0.6, bz - 44), (bx - 50, 0.6, bz - 44),
             lambda s, t: 0.6 * max(0.0, 1 - ((s - 55) / 52) ** 2 - ((t - 42) / 40) ** 2) * 1.5)

    def etiqueta(s, t, P):
        if 16 < s < 38 and 8 < t < 20:
            return 4.2 if not (11 < t < 12 or 14 < t < 15 or 17 < t < 18) or s > 34 else 1.4
        if s < 1 or t < 4:
            return 2.4                                                # la tapa
        if 4 < s < 10 and t > 21:
            return 1.2                                                # la nansa
        return 3.0 + (fbm(s / 12, t / 8, 9) - 0.5) * 0.4
    for k, (dx, dz, y0b, a) in enumerate(CAIXES):
        e.caixa_girada('caixes', bx + dx, bz + dz, 53, 36, 29, ba + a, CARD, 2.6, y0=y0b,
                       cares={'davant': {'ramp': CARD, 'lvl': etiqueta}, 'dalt': {'ramp': CARD, 'lvl': 3.4},
                              'esquerra': {'ramp': CARD, 'lvl': 2.0}, 'dreta': {'ramp': CARD, 'lvl': 1.8}})
    # primer pla: el contenidor de rodes en silueta (a baix a l'esquerra) i la canonada grossa que fuig pel sostre
    FOSC = [(3, 4, 4), (7, 9, 9), (12, 15, 14), (18, 22, 21), (26, 31, 30), (36, 42, 40)]
    jx, jz = BIN
    e.caixa_girada('primer_pla', jx, jz, 66, 52, 76, 0.22, FOSC, 1.4, y0=8,
                   cares={'dalt': {'ramp': FOSC, 'lvl': lambda s, t, P: 2.6 + (0.8 if t < 3 else 0)},
                          'davant': {'ramp': FOSC, 'lvl': lambda s, t, P: 1.4 + (0.8 if t < 4 else 0) - (0.6 if 30 < t < 33 else 0)},
                          'dreta': {'ramp': FOSC, 'lvl': lambda s, t, P: 2.0 + (0.8 if t < 4 else 0)}})
    for wx, wz in ((jx - 24, jz - 18), (jx + 28, jz - 10)):
        e.tub('primer_pla', (wx, 4, wz - 3), (wx, 4, wz + 3), 4.5, FOSC, 1.6)
    e.tub('primer_pla', (10, HW - 10, -300), (10, HW - 10, ZW - 4), 10, FOSC, 2.0, brides=70)
    e.tub('primer_pla', (30, HW - 6, -300), (30, HW - 6, ZW - 4), 5, FOSC, 1.6, brides=110)
    return e


# ─── Composició i llum ──────────────────────────────────────────────────────

def _proj(P):
    u, v, _ = CAM.projecta(P)
    return u, v


def _fx():
    tx, ty = _proj(TUBE_C)
    sx, sy = _proj(SCREEN_C)
    light = [llum.wash(tx, ty + 30, 260, (215, 230, 200), k=0.35, air=0.03, squash=0.9),      # el fluorescent brut
             llum.wash(sx, sy + 10, 220, (70, 255, 140), k=0.7, air=0.05, squash=1.0)]        # la pantalla, verda
    tone = [llum.grade(contrast=1.1, pivot=45, sat=1.15, lift=(2, 6, 4))]
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


def _amb_llum(img, bloom=True):
    light, bl, tone = _fx()
    return llum.apply(img, light + (bl if bloom else []) + tone)


@functools.lru_cache(maxsize=None)
def _base_llum():
    return _amb_llum(_base()[0])


def bg(cv):
    cv.img.paste(_base_llum())
    cv.P = cv.img.load()


def _fotograma(capes=(), post=None):
    """El fons amb unes capes damunt (i `post(cv)`, un retoc en pantalla), amb la llum, menys el fons amb la llum."""
    img, _ = _base()
    img = img.copy()
    for c in capes:
        img.alpha_composite(c)
    if post:
        cv = Canvas(light=LIGHT, img=img)
        post(cv)
        img = cv.img
    return _diff(_amb_llum(img), _base_llum())


PROPS = {}


# ─── Els llums del Llibre Major i el cursor ────────────────────────────────

def _frames():
    _, e = _base()
    out = []
    for i in range(12):
        out.append(_fotograma([e.capa(_llibre_img(frame=i + 1, cursor=i % 4 < 2), {'llibre'})]))
    return out


ANIMS = {'llibre': {'frames': _frames, 'frameDuration': 260}}


# ─── El fluorescent que fa figa i la gota de la canonada ───────────────────

def _frames_fluorescent():
    """El fluorescent brut aguanta una estona i de cop tartamudeja: s'apaga, torna, mig s'apaga i torna."""
    _, e = _base()
    empty = _diff(_base_llum(), _base_llum())
    tx, ty = _proj(TUBE_C)
    dims = {}
    frames = []
    for t in (1,) * 14 + (0.0, 1, 0.0, 0.6, 1, 0.6):
        if t == 1:
            frames.append(empty)
            continue
        if t not in dims:
            k = 0.3 if t == 0 else 0.15

            def fosc(cv, k=k):
                for Y in range(0, BOTTOM):
                    for X in range(0, W):
                        d = math.hypot((X - tx) / 260, (Y - ty) / 200)
                        if d < 1:
                            o = cv.P[X, Y]
                            m = 1 - k * (1 - d) ** 1.5
                            cv.P[X, Y] = (round(o[0] * m), round(o[1] * m), round(o[2] * m), o[3])
            dims[t] = _fotograma([e.capa(_paret(tube=t), {'paret_fons', 'paret_esq'})], post=fosc)
        frames.append(dims[t])
    return frames


DRIP = (_w(289), _y(34), ZW - 3)                   # sota la canonada vella; cau a la taca d'humitat del terra


def _frames_gota():
    """Una gota es forma sota la canonada vella, s'allarga, cau i esquitxa la taca d'humitat."""
    empty = _diff(_base_llum(), _base_llum())
    top = _proj(DRIP)
    floor = _proj((DRIP[0], 0, DRIP[2] - 4))
    k = CAM.escala(DRIP)
    X = round(top[0])
    frames = [empty] * 6

    def gota(h):
        def post(cv):
            cv.vline(X, round(top[1]), round(top[1]) + h - 1, DROP, 1)
            if h >= 3:
                cv.put(X - 1, round(top[1]) + h - 2, DROP, 0.6)
                cv.put(X + 1, round(top[1]) + h - 2, DROP, 0.6)
            cv.flat(X, round(top[1]) + h - 1, DROP[2])
        return post
    for h in (1, 1, 2, 2, 3, 4):
        frames.append(_fotograma(post=gota(h)))
    # la caiguda, cada cop més ràpida (la fracció del camí fins a terra i la llargada de l'estela)
    for f, ln in ((0.03, 3), (0.08, 3), (0.16, 4), (0.27, 5), (0.41, 6), (0.58, 7), (0.78, 8), (0.97, 6)):
        y = round(top[1] + (floor[1] - top[1]) * f)

        def post(cv, y=y, ln=ln):
            cv.vline(X, y - ln + 1, y - 1, DROP, 0.6)
            cv.flat(X, y, DROP[2])
        frames.append(_fotograma(post=post))
    # l'esquitx: unes gotetes que salten i una rodoneta a la taca
    fy = round(floor[1])
    for j in range(4):
        def post(cv, j=j):
            if j < 3:
                hop = (2, 3, 1)[j]
                for sgn in (-1, 1):
                    cv.flat(X + sgn * (1 + j), fy - hop, DROP[1] if j < 2 else DROP[0])
                if j == 1:
                    cv.flat(X, fy - 4, DROP[2])
            r = (2 + j * 2) * k
            for a in range(0, 360, 8):
                cv.put(round(X + math.cos(math.radians(a)) * r), round(fy + math.sin(math.radians(a)) * r * 0.3),
                       DROP, 1.0 - j * 0.3)
        frames.append(_fotograma(post=post))
    frames += [empty] * 2
    return frames


ANIMS['fluorescent'] = {'frames': _frames_fluorescent, 'frameDuration': 110}
ANIMS['gota'] = {'frames': _frames_gota, 'frameDuration': 100}


# ─── Capes del davant ───────────────────────────────────────────────────────

def _amo(ids):
    def mask(x, y):
        _, e = _base()
        return e.ids[e.amo[y * e.cv.w + x]] in ids
    return mask


def _p(x, z, y=0.0):
    u, v, _ = CAM.projecta((x, y, z))
    return round(u), round(v)


def _peus_caixes(marge=0):
    """Els cantons de les caixes de terra, al món (x, z), amb un marge."""
    bx, bz, ba = BOXES
    out = []
    for dx, dz, y0b, a in CAIXES:
        if y0b:
            continue
        c, s_ = math.cos(ba + a), math.sin(ba + a)
        for lx, lz in ((-26.5 - marge, -18 - marge), (26.5 + marge, -18 - marge), (26.5 + marge, 18 + marge),
                       (-26.5 - marge, 18 + marge)):
            out.append((bx + dx + lx * c - lz * s_, bz + dz + lx * s_ + lz * c))
    return out


def _baseline_caixes():
    return max(_p(x, z)[1] for x, z in _peus_caixes()) - 4


def _forat_caixes():
    """La petjada de les caixes (l'envolupant convexa, a la pantalla): no s'hi pot trepitjar."""
    pts = sorted(set(_p(x, z) for x, z in _peus_caixes(6)))
    def creu(o, a, b):
        return (a[0] - o[0]) * (b[1] - o[1]) - (a[1] - o[1]) * (b[0] - o[0])
    lo, hi = [], []
    for p in pts:
        while len(lo) >= 2 and creu(lo[-2], lo[-1], p) <= 0:
            lo.pop()
        lo.append(p)
    for p in reversed(pts):
        while len(hi) >= 2 and creu(hi[-2], hi[-1], p) <= 0:
            hi.pop()
        hi.append(p)
    return lo[:-1] + hi[:-1]


# El primer pla (sempre davant) i les caixes d'arxiu (qui hi passa per darrere, hi queda darrere).
FRONT = [
    {'id': 'davant', 'mask': _amo({'primer_pla'}), 'baseline': 999, 'zIndex': 20},
    {'id': 'davant_caixes', 'mask': _amo({'caixes'}), 'baseline': _baseline_caixes(), 'zIndex': 20},
]


# ─── Geometria (coordenades de sala, projectades) ────────────────────────────

def _rect_mon(*Ps):
    pts = [CAM.projecta(P) for P in Ps]
    return (max(0, round(min(p[0] for p in pts))), max(0, round(min(p[1] for p in pts))),
            min(W - 1, round(max(p[0] for p in pts))), min(BOTTOM, round(max(p[1] for p in pts))))


def _rect_pla(x0, y0, x1, y1):
    return _rect_mon(*[_fw(x, y) for x in (x0, x1) for y in (y0, y1)] + ([_fw(XC, y0), _fw(XC, y1)] if x0 < XC < x1 else []))


def _talla(poly, a, b, c):
    """Retalla el polígon (de pantalla) pel semiplà a·u + b·v + c ≥ 0."""
    out = []
    for P, Q in zip(poly, poly[1:] + poly[:1]):
        fp, fq = a * P[0] + b * P[1] + c, a * Q[0] + b * Q[1] + c
        if fp >= 0:
            out.append(P)
        if (fp >= 0) != (fq >= 0):
            k = fp / (fp - fq)
            out.append((P[0] + (Q[0] - P[0]) * k, P[1] + (Q[1] - P[1]) * k))
    return out


def _escala_a(v):
    """L'escala d'un personatge amb els peus a la y de pantalla `v` (al terra, la profunditat només depèn de v)."""
    lo, hi = -300.0, 2000.0
    for _ in range(60):
        z = (lo + hi) / 2
        if CAM.projecta((260, 0, z))[1] > v:
            lo = z
        else:
            hi = z
    return CAM.escala((260, 0, (lo + hi) / 2))


def _v_escala(k):
    lo, hi = 0.0, float(BOTTOM)
    for _ in range(40):
        m = (lo + hi) / 2
        if _escala_a(m) < k:
            lo = m
        else:
            hi = m
    return lo


# El terra on es camina (al món): de la porta fins a la base de càrrega, davant les bosses i el Llibre Major (el
# Llibre Major, de rodó, no es pot voltar per darrere); retallat per la pantalla i on passaria d'escala 1,2.
_LL = [_llibre(-LEDGER[2] / 2 - 10, 0, LEDGER[3] / 2 + 30), _llibre(-LEDGER[2] / 2 - 10, 0, -LEDGER[3] / 2 - SHELF[2] - 8),
       _llibre(LEDGER[2] / 2 + 10, 0, -LEDGER[3] / 2 - SHELF[2] - 8), _llibre(LEDGER[2] / 2 + 10, 0, LEDGER[3] / 2 + 6)]
WALK_MON = [(14, 290), (14, 262), (110, 240), (130, 286), (_LL[0][0], 296), (_LL[1][0], _LL[1][2]),
            (_LL[2][0], _LL[2][2]), (_LL[3][0], _LL[3][2]), (_LL[3][0] + 6, 292), (DOCK[0] - 6, 292), (DOCK[0] - 6, 262),
            (560, 250), (600, -100), (BIN[0] + 50, -100), (BIN[0] + 44, BIN[1] + 40), (14, BIN[1] + 50)]
V_MAX = _v_escala(1.2)
_WALK = [_p(x, z) for x, z in WALK_MON]
for _a, _b, _c in ((1, 0, -4), (-1, 0, W - 5), (0, -1, V_MAX)):
    _WALK = _talla(_WALK, _a, _b, _c)
_WALK = [(round(u), round(v)) for u, v in _WALK]
_V_FONS, _V_PROP = min(v for _, v in _WALK), max(v for _, v in _WALK)


def _rect_llibre():
    lw, ld = LEDGER[2], LEDGER[3]
    return _rect_mon(*[_llibre(lx, y, lz) for lx in (-lw / 2, lw / 2) for lz in (-ld / 2 - SHELF[2], ld / 2)
                       for y in (0, LH)])


def _retalla_esq(r, x0):
    return (max(r[0], x0), r[1], r[2], r[3])


def _retalla_dreta(r, x1):
    return (r[0], r[1], min(r[2], x1), r[3])


def _rect_bosses():
    return _rect_mon((4, 0, 300), (4, 60, 300), (120, 0, 296), (120, 40, 296), (10, 0, 212), (100, 30, 230), (60, 60, 280))


GEOMETRIA = {
    'things': {
        'porta': {'rect': _rect_pla(14, 62, 85, 200), 'walk': _p(16, _wz(50))},
        'bosses': {'rect': _retalla_esq(_rect_bosses(), _rect_pla(14, 62, 85, 200)[2] + 1), 'walk': _p(80, 214)},
        'conducte': {'rect': _retalla_dreta(_rect_pla(211, 65, 282, 176), _rect_llibre()[0] - 1), 'walk': _p(_w(246), 262)},
        'llibre': {'rect': _rect_llibre(), 'walk': _p(*[(P[0] - 10, P[2] - 32) for P in [_llibre(0, 0, -LEDGER[3] / 2)]][0])},
        'tub': {'rect': _rect_pla(467, 78, 505, 149), 'walk': _p(_w(483), ZW - 30)},
        'panell': {'rect': _rect_pla(518, 91, 567, 149), 'walk': _p(_w(528), ZW - 26)},
    },
    'spawns': {'iri': _p(60, 180)},
    'walkable': _WALK,
    'forats': [_forat_caixes()],
    'floorSquash': 0.42,
    # L'ombra de contacte: la llum dominant és el fluorescent brut, a dalt a l'esquerra; l'ombra cau cap a la dreta.
    'characterShadow': {'enabled': True, 'color': '#060a08', 'alpha': 0.5, 'squash': 0.4, 'core': 0.6,
                        'light': {'x': _p(TUBE_C[0], TUBE_C[2] - 10)[0], 'y': _p(TUBE_C[0], TUBE_C[2] - 10)[1],
                                  'stretch': 0.7, 'reach': 220}},
    'regions': [{'id': 'perspectiva', 'active': True, 'scaleEnabled': True, 'scaleWalkSpeed': True,
                 'scaleTop': round(_escala_a(_V_FONS - 2), 3), 'scaleBottom': round(_escala_a(_V_PROP + 2), 3),
                 'points': [(0, _V_FONS - 2), (W - 1, _V_FONS - 2), (W - 1, _V_PROP + 2), (0, _V_PROP + 2)]}],
    'characterLights': {
        'ambient': '#8c968c',                                                           # soterrani, gris verdós
        'lights': [
            {'x': _p(TUBE_C[0], TUBE_C[2], TUBE_C[1])[0], 'y': _p(TUBE_C[0], TUBE_C[2], TUBE_C[1])[1], 'radius': 300,
             'color': '#e0ecd0', 'intensity': 0.7},                                     # el fluorescent
            {'x': _p(SCREEN_L[0], SCREEN_L[2], SCREEN_L[1])[0], 'y': _p(SCREEN_L[0], SCREEN_L[2], SCREEN_L[1])[1],
             'radius': 200, 'color': '#50ff8c', 'intensity': 0.8},                      # la pantalla del Llibre Major
        ],
    },
}
