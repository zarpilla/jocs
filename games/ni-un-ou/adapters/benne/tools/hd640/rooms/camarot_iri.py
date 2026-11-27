"""
El camarot de l'Iri (Escena 1, les 3:40 de la matinada). EN 3D (hd640/tres_d.py), a 1×.

El més petit del vaixell, al costat de les màquines. Una càmera alta que mira de biaix la cantonada del fons a
l'esquerra:
  - a la paret de l'esquerra, en escorç, la **llitera** feta com un llit d'hospital (un volum: el costat amb els
    calaixos, la manta estirada vista des de dalt, el coixí, els plafons del capçal i dels peus), el llum de lectura i el **prestatge** amb el multímetre, la llauna, els manuals, les claus fixes i
    el **got** d'aigua torçat (cada cosa dreta al seu lloc del prestatge, que fuig);
  - a la cantonada, la **tauleta** de planxa amb el despertador (3:40) i, a la paret, l'endoll amb el **carregador**
    mossegat (el cable cau damunt la tauleta);
  - a la paret del fons, el **pòster** del dièsel, l'**ull de bou** (amb la **maceta** penjada a sota), la granota
    penjada i la **porta** entreoberta: la fulla gira cap a dins i es veu el passadís il·luminat, que fa una falca de
    llum verdosa pel terra;
  - al mig del terra, la **motxilla** d'en Diu, girada (s'hi passa per darrere), i l'espina de sardina;
  - primer pla: el bao del sostre i les safates de cables a dalt, un tub que baixa a la dreta i una galleda.

Tot el detall ve del dibuix pla de sempre (camarot_iri_pla_comu.py), projectat; els decorats (`ulls_dia`, `maceta`)
i l'animació (`mar`) es dibuixen plans i es projecten per la paret del fons.

El món: x a la dreta (0 = la paret de la llitera), y amunt (0 = el terra), z cap al fons (260 = la paret del fons);
1 unitat = 1 píxel de sala a la distància on un personatge fa ≈110 px (escala 1).
"""
import functools
import math

import hd640  # noqa: F401  (abans de cap hd.rooms: posa la llibreria a 640×360)
from PIL import Image

from hd.pix import Canvas, Light, W, H, hr, mix, WALNUT
from hd.rooms.arenga import WALL, CAB, DARK, WHITEP, YELL, SEAG, BRASS, DECK, ENG, rrect, box
from hd.rooms.exterior import fbm
from hd640.rooms import sota
from hd640.rooms import camarot_iri_pla_comu as PL
from hd640.rooms.camarot_iri_pla_comu import PAINT, LINO, BLANKET, SHEET, OLIVE, RUG, CURT
from hd640.tres_d import Camera, Escena, Llum

BOTTOM = 259                                       # la sala acaba aquí (a sota, la barra de verbs)
FY = PL.FLOOR_Y                                    # al dibuix pla, el terra (203)
FY0 = 23                                           # al dibuix pla, on comença la paret (a dalt, el sostre pintat)
HW = FY - FY0                                      # l'alçada de les parets (180)
ZW = 260                                           # la paret del fons
XL = 175                                           # al dibuix pla, la cantonada: a l'esquerra, la paret de la llitera
XR = W - XL                                        # on s'acaba la paret del fons: la paret de la dreta (465)
ZOFF = 27                                          # la paret de la llitera: z = x del dibuix pla + ZOFF
BD = 52                                            # el fons de la llitera (x)
TAU = (60, 100, ZW - 34, ZW, 38)                     # la tauleta: x0, x1, z0, z1, alçada
MOTX = (214, 132, 46, 26, 42, 0.42)                # la motxilla: x, z del centre, ample, fons, alt, gir
GALLEDA = (420, 20)                                # la caixa de fusta de primer pla (x, z)


def _y(fy, base=FY):
    """Una y del dibuix pla → l'alçada del món (`base`: on toca el terra al dibuix pla; la llitera és més endavant)."""
    return base - fy


def _wz(fx):
    """Una x del dibuix pla de la paret de la llitera → la z del món."""
    return fx + ZOFF


def _w(fx):
    """Una x del dibuix pla de la paret del fons → la x del món."""
    return fx - XL


DOOR = (_w(PL.DOOR[0]), _w(PL.DOOR[2]), _y(PL.DOOR[1]))          # la porta: x0, x1, alçada (306, 370, 120)
PORT = (_w(PL.PORT[0]), _y(PL.PORT[1]))                           # l'ull de bou: x, y del centre
LDX = 20                                                          # el llum, corregut cap als peus (que el capçal no el tapi)
LAMP = (14, _y(128), _wz(59 + LDX))                               # el llum de lectura (al món)
FULLA = 1.05                                                      # quant s'obre la fulla de la porta (radians)

CAM = Camera(pos=(370, 150, -230), yaw=-0.34, pitch=0.12, f=400, centre=(330, 100))

LIGHT = Light(ambient=0.0, vignette=None, floor_fade=None)  # (la llum és la del món: la de l'Escena)
LLUMS = [Llum(LAMP, 330, 2.3, power=1.3),                                       # el llum de lectura
         Llum(((DOOR[0] + DOOR[1]) / 2, 100, ZW + 26), 230, 2.4, power=1.4),   # el passadís, per la porta
         Llum((PORT[0], PORT[1], ZW - 6), 70, 0.4, power=2.0)]                 # l'ull de bou (gairebé res)

# la llum de les textures: la del dibuix pla, sense la vinyeta (les vores del pla ara són al mig de la sala)
TEX_LIGHT = Light(ambient=-0.45, vignette=None, floor_fade=None)
TEX_LIGHT.points = list(PL.LIGHT.points)

FOSC = [(3, 4, 5), (7, 9, 10), (12, 15, 16), (18, 22, 22), (26, 31, 30), (36, 42, 40)]
CORD = [(60, 60, 58), (150, 150, 146), (214, 214, 206), (240, 240, 232)]


# ─── Les textures: el dibuix pla de sempre ───────────────────────────────────

@functools.lru_cache(maxsize=None)
def _llitera_pla():
    """La llitera i el prestatge, plans sobre transparent (en surten els retalls)."""
    cv = Canvas(light=TEX_LIGHT, transparent=True)
    PL.bunk(cv)
    return cv.img


@functools.lru_cache(maxsize=None)
def _prestatge_pla():
    cv = Canvas(light=TEX_LIGHT, transparent=True)
    PL.shelf(cv)
    return cv.img


@functools.lru_cache(maxsize=None)
def _tauleta_pla():
    cv = Canvas(light=TEX_LIGHT, transparent=True)
    PL.locker(cv)
    return cv.img


@functools.lru_cache(maxsize=None)
def _motxilla_pla():
    cv = Canvas(light=TEX_LIGHT, transparent=True)
    PL.backpack(cv)
    return cv.img


def _fulla(cv):
    """La fulla de la porta, de cara (per dins): planxa pintada amb dos plafons, la reixeta, la maneta i el número."""
    x0, y0, x1, y1 = PL.DOOR
    rrect(cv, x0, y0, x1, y1 - 1, 7, PAINT, lambda x, y: 3.4 - (y - y0) * 0.004)
    rrect(cv, x0 + 7, y0 + 9, x1 - 7, y0 + 58, 4, PAINT, 3.9)
    cv.hline(x0 + 9, x1 - 9, y0 + 9, PAINT, 5.0)
    cv.vline(x1 - 7, y0 + 12, y0 + 56, PAINT, 2.4)
    rrect(cv, x0 + 7, y1 - 38, x1 - 7, y1 - 7, 4, PAINT, 3.7)
    for i in range(7):                                                # la reixeta de ventilació
        cv.hline(x0 + 12, x1 - 12, y1 - 33 + i * 4, PAINT, 1.4)
        cv.hline(x0 + 12, x1 - 12, y1 - 32 + i * 4, PAINT, 4.2)
    box(cv, x1 - 13, 139, x1 - 9, 149, BRASS, 3.6)                    # la maneta, a la vora lliure
    cv.hline(x1 - 20, x1 - 10, 141, BRASS, 4.6)
    cv.hline(x1 - 20, x1 - 10, 142, BRASS, 2.6)
    box(cv, x0 + 25, y0 + 16, x0 + 39, y0 + 24, BRASS, 3.6)           # el número del camarot
    from hd.rooms.comu import text
    text(cv, '4', x0 + 31, y0 + 18, None, 0, flat=(60, 40, 16))
    cv.vline(x0, y0 + 6, y1 - 2, PAINT, 1.4)                          # la vora de les frontisses


def _paret(dia=False, maceta=False, vidre=None):
    """Les parets planes, de cara: la planxa, el pòster, l'ull de bou, la granota, el marc de la porta (l'obertura,
    transparent), l'endoll amb el carregador i, a la paret de la llitera, el llum de lectura."""
    cv = Canvas(light=TEX_LIGHT)
    PL.walls(cv)
    PL.poster(cv)
    PL.porthole(cv)
    PL.overalls(cv)
    x0, y0, x1, y1 = PL.DOOR
    sota.door_frame(cv, x0, y0, x1, y1, ramp=PAINT, lvl=4.6, r=8)
    t = _tauleta_pla()
    cv.img.alpha_composite(t.crop((236, 147, 259, 166)), (236, 147))   # l'endoll i el carregador
    b = _llitera_pla()
    cv.img.alpha_composite(b.crop((30, 120, 69, 142)), (30 + LDX, 120))  # el llum de lectura i l'interruptor
    cv.P = cv.img.load()
    cv.glow(59 + LDX, 128, 30, (255, 214, 140), 0.45)
    if dia:
        PL.ulls_dia(cv)
    if vidre is not None:
        PL.porthole_glass(cv, vidre)
    if maceta:
        PL.maceta(cv)
    P = cv.P
    for y in range(y0 - 1, y1 + 1):                                     # l'obertura de la porta, buida
        for x in range(x0, x1 + 1):
            if sota.in_door(x, y, x0, y0, x1, y1, 8):
                P[x, y] = (0, 0, 0, 0)
    return cv


@functools.lru_cache(maxsize=None)
def _paret_base():
    return _paret().img


@functools.lru_cache(maxsize=None)
def _paret_nua():
    """La planxa sola (per a les parets de més a prop i la de la dreta)."""
    cv = Canvas(light=Light(ambient=-0.3, vignette=None, floor_fade=None))
    sota.plate_wall(cv, 0, W - 1, ramp=PAINT, lvl=3.6, frames=128, frame0=-5, seams=(77,), socle=184, rust=10, seed=5)
    return cv.img


@functools.lru_cache(maxsize=None)
def _fulla_pla():
    cv = Canvas(light=TEX_LIGHT, transparent=True)
    _fulla(cv)
    return cv.img


# ─── Les superfícies ────────────────────────────────────────────────────────

def _terra(s, t, P):
    """Linòleum de rajoles de 44 (en coordenades del món: s'empetiteixen cap al fons), gastat i amb rascades."""
    x, z = P[0], P[2]
    v = 3.0 + (fbm(x / 50, z / 40, 5) - 0.5) * 0.7 + (hr(int(x // 44), int(z // 44), 3) - 0.5) * 0.4
    if x % 44 < 1.0 or z % 44 < 1.0:
        return 1.6
    if (x % 44) < 2.0 or (z % 44) < 2.0:
        v += 0.4
    if hr(int(x // 3), int(z // 2), 6) > 0.992:
        v += 0.8                                                   # rascades
    return v


def _catifa(s, t, P):
    """La catifa de ratlles, vella, amb el serrell als caps."""
    if t < 3 or t > 147:
        return 3.4 if int(s) % 3 == 0 else 1.6                     # el serrell
    if s < 1.5 or s > 74:
        return 1.4
    band = int(t // 5) % 3
    v = 2.6 + (1.0 if band == 0 else 0.4 if band == 1 and int(s // 2) % 2 else 0)
    return v - (0.7 if hr(int(s // 3), int(t // 2), 9) > 0.86 else 0) + (fbm(s / 20, t / 30, 2) - 0.5) * 0.6


def _blanket(s, t, P):
    """La manta, ben estirada (llit d'hospital), vista des de dalt: el llençol girat al capçal i arrugues llargues."""
    if t < 18:
        return 3.4 + (fbm(s / 6, t / 4, 2) - 0.5) * 0.5          # (el coixí hi va a sobre)
    if t < 36:
        return 3.9 - (0.8 if t > 34 else 0)                       # el llençol girat
    v = 3.0 + (fbm(s / 30, t / 18, 4) - 0.5) * 0.5
    if int(t + s * 0.6) % 28 < 1.2 and 8 < s < 46:
        v -= 0.6                                                  # les arrugues estirades
    if s > BD - 4:
        v -= 0.6                                                  # la vora plegada
    return v


def escena(cv, tex, estat=frozenset()):
    """Tota la sala, de lluny a prop. → l'Escena (qui ha pintat què)."""
    e = Escena(cv, CAM, LLUMS, ambient=-0.35)
    zn = CAM.pos[2] + 40
    paret, nua = tex['paret'], tex['nua']
    dx0, dx1, dh = DOOR
    dmid = (dx0 + dx1) / 2
    # el passadís, a l'altra banda de la porta: la paret de davant, il·luminada, el terra i el sostre
    ZP = ZW + 46
    e.quad('passadis', (dx0 - 70, 150, ZP), (dx1 + 70, 150, ZP), (dx1 + 70, 0, ZP), (dx0 - 70, 0, ZP), ramp=WALL,
           lvl=lambda s, t, P: 4.0 - abs(P[0] - dmid) / 60 + (0.6 if 52 < t < 55 else 0)
           - (0.9 if int(P[0]) % 40 < 2 else 0) - (1.2 if t > 130 else 0))
    e.quad('passadis', (dx0 - 70, 0, ZP), (dx1 + 70, 0, ZP), (dx1 + 70, 0, ZW), (dx0 - 70, 0, ZW), ramp=DECK,
           lvl=lambda s, t, P: 3.6 - abs(P[0] - dmid) / 50 + (0.8 if (int(P[0]) + int(P[2])) % 4 == 0 else 0))
    e.tub('passadis', (dx1 - 10, 0, ZP - 5), (dx1 - 10, 150, ZP - 5), 3, SEAG, 3.4, brides=60)
    # el sostre, fosc, amb els baos i les safates
    e.quad('sostre', (0, HW, zn), (XR, HW, zn), (XR, HW, ZW), (0, HW, ZW), ramp=PAINT,
           lvl=lambda s, t, P: 1.4 - (0.6 if int(P[0]) % 64 < 1.5 else 0) + (fbm(P[0] / 60, P[2] / 60, 8) - 0.5) * 0.5,
           dues_cares=True)
    for bz in (70, 165):
        e.caixa('sostre', 0, XR, HW - 12, HW, bz - 7, bz + 7, PAINT, 2.0,
                cares={'sota': {'ramp': PAINT, 'lvl': 1.6}, 'davant': {'ramp': PAINT, 'lvl': 2.6}})
    # la paret de la llitera (x = 0): de prop, planxa; després, el dibuix pla (x 0..230) i, a la cantonada, planxa
    e.quad('paret_esq_prop', (0, HW, zn), (0, HW, _wz(0)), (0, 0, _wz(0)), (0, 0, zn), tex=(nua, (0, FY0, 300, FY)))
    e.quad('paret_esq', (0, HW, _wz(0)), (0, HW, _wz(230)), (0, 0, _wz(230)), (0, 0, _wz(0)),
           tex=(paret, (0, FY0, 230, FY)))
    e.quad('paret_esq_cant', (0, HW, _wz(230)), (0, HW, ZW), (0, 0, ZW), (0, 0, _wz(230)),
           tex=(nua, (300, FY0, 345, FY)))
    # la paret del fons (z = 260): el dibuix pla (x 175..640), amb la porta oberta
    e.quad('paret_fons', (0, HW, ZW), (XR, HW, ZW), (XR, 0, ZW), (0, 0, ZW), tex=(paret, (XL, FY0, W, FY)))
    # la paret de la dreta (x = 465), de cara a la sala
    e.quad('paret_dreta', (XR, HW, ZW), (XR, HW, zn), (XR, 0, zn), (XR, 0, ZW), tex=(nua, (40, FY0, 640, FY)))
    # el terra, i la catifa davant la llitera (una mica girada)
    e.quad('terra', (0, 0, ZW), (XR, 0, ZW), (XR, 0, zn), (0, 0, zn), ramp=LINO, lvl=_terra)
    ca, cz0 = 0.06, 40
    e.quad('catifa', (BD + 8 + 150 * ca, 0.3, cz0 + 150), (BD + 84 + 150 * ca, 0.3, cz0 + 150 - 76 * ca),
           (BD + 84, 0.3, cz0 - 76 * ca), (BD + 8, 0.3, cz0), ramp=RUG, lvl=_catifa)
    # la llum: el llum de lectura fa un bassal càlid, i el passadís, una falca verdosa que entra en diagonal
    e.claror((0, 0.4, ZW), (XR, 0.4, ZW), (XR, 0.4, zn), (0, 0.4, zn), (255, 200, 120),
             lambda s, t: 0.22 * max(0.0, 1 - math.hypot(s - LAMP[0] - 40, (ZW - t) - LAMP[2] - 10) / 210))

    def falca(s, t):
        x, z = s, ZW - t
        d = ZW - z                                                # quant s'allunya de la porta
        if d < 0:
            return 0.0
        a, b = dmid - 8 - d * 0.62, dx1 + 2 - d * 0.18           # s'obre i es tomba cap a l'esquerra
        if not a < x < b:
            return 0.0
        return 0.34 * max(0.0, 1 - d / 190) * min(1.0, (x - a) / 10, (b - x) / 6)
    e.claror((0, 0.5, ZW), (XR, 0.5, ZW), (XR, 0.5, ZW - 220), (0, 0.5, ZW - 220), (150, 176, 140), falca)
    # la foscor dels racons
    e.foscor('racons', (0, 0.6, ZW), (XR, 0.6, ZW), (XR, 0.6, zn), (0, 0.6, zn),
             lambda s, t: max(0.5 * max(0.0, 1 - t / 26), 0.45 * max(0.0, 1 - (XR - s) / 30)))
    e.foscor('cantonada', (0, HW, ZW - 0.5), (60, HW, ZW - 0.5), (60, 0, ZW - 0.5), (0, 0, ZW - 0.5),
             lambda s, t: 0.5 * max(0.0, 1 - s / 60))
    e.foscor('sostre_fosc', (0, HW - 0.5, ZW - 0.6), (XR, HW - 0.5, ZW - 0.6), (XR, 0, ZW - 0.6), (0, 0, ZW - 0.6),
             lambda s, t: 0.5 * max(0.0, 1 - t / 46))
    e.foscor('sostre_fosc', (0.5, HW - 0.5, zn), (0.5, HW - 0.5, ZW), (0.5, 0, ZW), (0.5, 0, zn),
             lambda s, t: 0.45 * max(0.0, 1 - t / 40))
    # el tub d'aigua de mar, a dalt de la paret del fons, i la safata de cables a dalt de la paret de la llitera
    e.tub('tubs', (-4, HW - 12, ZW - 7), (XR + 4, HW - 12, ZW - 7), 4.5, SEAG, 3.0, brides=93)
    e.caixa('tubs', 4, 22, HW - 24, HW - 20, zn, ZW - 12, CAB, 2.0, cares={'dalt': {'ramp': CAB, 'lvl': 2.6}})
    for k, col in enumerate(([(20, 20, 24), (40, 36, 30), (70, 50, 34)], [(40, 12, 10), (110, 40, 34), (160, 70, 50)],
                             [(12, 20, 40), (30, 50, 80), (60, 90, 130)])):
        e.cable('tubs', [(8 + k * 5, HW - 19, zn + 20), (8 + k * 5, HW - 19, ZW - 14)], col, 1.8, gruix=2.0)
    # la tauleta (calaixera de planxa), a la cantonada, amb el despertador i el cable mossegat
    tx0, tx1, tz0, tz1, th = TAU
    tau = tex['tauleta']
    e.foscor('ombra_tauleta', (tx0, 0.6, tz1), (tx1 + 10, 0.6, tz1), (tx1 + 10, 0.6, tz0 - 12), (tx0, 0.6, tz0 - 12),
             lambda s, t: 0.5 * min(1.0, max(0.0, (tz1 - tz0 + 12 - t) / 12)))
    e.caixa('tauleta', tx0, tx1, 0, th, tz0, tz1, PAINT, 2.6,
            cares={'davant': {'tex': (tau, (235, 173, 276, 212))}, 'dalt': {'ramp': PAINT, 'lvl': 4.0},
                   'dreta': {'ramp': PAINT, 'lvl': 2.2}})
    e.sprite('tauleta', tau.crop((252, 161, 274, 174)), (11, 12.5), (26, th, tz0 + 12))
    e.cable('cable', [(_w(245), th + 5, ZW - 1), (_w(245), th + 1, ZW - 4), (_w(243), th + 0.6, ZW - 14),
                      (_w(238), th + 0.6, ZW - 22)], CORD, 2.2, gruix=1.2)
    for a, b in ((8, 14), (18, 22)):
        e.cable('cable', [(a, th + 0.6, tz0 + 6), (b, th + 0.6, tz0 + 8)], CORD, 2.0, gruix=1.0)
    e.quad('cable', (_w(238) - 1, th + 0.7, ZW - 21), (_w(238) + 1, th + 0.7, ZW - 21), (_w(238) + 1, th + 0.7, ZW - 23),
           (_w(238) - 1, th + 0.7, ZW - 23), ramp=BRASS, lvl=4.6)
    # la llitera: el costat amb els calaixos, la manta (des de dalt), el coixí, i els plafons
    bed, bot = tex['llitera'], 211
    e.foscor('ombra_llitera', (0, 0.6, _wz(19)), (BD + 18, 0.6, _wz(19)), (BD + 18, 0.6, _wz(229)), (0, 0.6, _wz(229)),
             lambda s, t: 0.55 * min(1.0, max(0.0, (BD + 18 - s) / 18)))
    # els plafons del capçal i dels peus: prims, un marc amb el plafó enfonsat, poc més alts que el matalàs.
    # (Sense z-buffer: el dels peus, abans del llit, que el matalàs li tapa la cara de davant; el del capçal, després.)
    def plafo(w, h, m=4):
        def lvl(s, t, P):
            if s < m or s > w - m or t < m or t > h - m:                      # el marc
                return 3.9 - (0.5 if t > h - 2 else 0)
            if t < m + 1.2 or s < m + 1.2:                                    # l'ombra del marc dins el plafó
                return 1.7
            if t > h - m - 1.2 or s > w - m - 1.2:                            # la llum al cantell de baix
                return 3.6
            return 2.7 + (fbm(s / 6, t / 18, 3) - 0.5) * 0.5                 # el plafó, amb la veta
        return lvl
    top = _y(157, bot)

    def plafo_caixa(z0, h):
        e.caixa('llitera', 0, BD + 2, 0, h, z0, z0 + 3, WALNUT, 3.0,
                cares={'dreta': {'ramp': WALNUT, 'lvl': 2.6}, 'dalt': {'ramp': WALNUT, 'lvl': 4.6},
                       'davant': {'ramp': WALNUT, 'lvl': plafo(BD + 2, h)}})
    plafo_caixa(_wz(219), top + 14)
    e.caixa('llitera', 0, BD, 0, _y(176, bot), _wz(29), _wz(219), WALNUT, 2.6,
            cares={'dreta': {'tex': (bed, (29, 176, 220, 212))}, 'dalt': {'ramp': WALNUT, 'lvl': 3.6}})
    e.caixa('llitera', 0, BD - 2, _y(176, bot), _y(157, bot), _wz(29), _wz(219), BLANKET, 3.0,
            cares={'dreta': {'tex': (bed, (29, 158, 220, 177))}, 'dalt': {'ramp': BLANKET, 'lvl': _blanket}})
    e.caixa_girada('llitera', 24, _wz(48), 38, 20, 9, 0.05, SHEET, 3.0, y0=top,
                   cares={'dalt': {'ramp': SHEET, 'lvl': lambda s, t, P: 4.2 - abs(t - 10) * 0.08
                                   - (0.8 if abs(s - 18) < 6 and abs(t - 9) < 3 else 0)},
                          'dreta': {'ramp': SHEET, 'lvl': 3.4}, 'davant': {'ramp': SHEET, 'lvl': 2.8}})
    plafo_caixa(_wz(26), top + 20)
    # el prestatge de damunt la llitera (a la paret, fuig): el tauler, la barana i cada cosa dreta al seu lloc
    sh = _prestatge_pla()
    sy = _y(109)
    e.caixa('prestatge', 0, 22, sy - 6, sy, _wz(80), _wz(216), WALNUT, 3.2,
            cares={'dalt': {'ramp': WALNUT, 'lvl': 4.0}, 'dreta': {'ramp': WALNUT, 'lvl': 3.4}})
    for fx in (88, 208):
        e.caixa('prestatge', 0, 16, sy - 16, sy - 6, _wz(fx), _wz(fx + 3), CAB, 2.8)
    for (a, b, y0, y1) in ((88, 105, 87, 109), (112, 134, 92, 109), (141, 164, 83, 109)):
        e.sprite('prestatge', sh.crop((a, y0, b, y1)), ((b - a) / 2, y1 - y0), (9, sy, _wz((a + b) / 2)))
    e.sprite('got', sh.crop((202, 93, 213, 109)), (5.5, 16), (9, sy, _wz(207)))
    e.tub('prestatge', (22, sy + 8, _wz(80)), (22, sy + 8, _wz(216)), 1.0, BRASS, 3.6)
    for fx in (81, 147, 215):
        e.caixa('prestatge', 21, 23, sy, sy + 8, _wz(fx), _wz(fx) + 1.5, BRASS, 3.0)
    for i, fx in enumerate((171, 179, 187, 195)):
        ln = 11 + i * 3
        e.sprite('prestatge', sh.crop((fx - 3, 103, fx + 4, 104 + ln + 4)), (3, 0), (22, sy + 8, _wz(fx)))
    # la motxilla d'en Diu, girada al mig del terra (oberta de dalt), i l'espina de sardina
    mx, mz, mw, md, mh, ma = MOTX
    mo = tex['motxilla']
    e.foscor('ombra_motxilla', (mx - 40, 0.6, mz + 30), (mx + 40, 0.6, mz + 30), (mx + 40, 0.6, mz - 30),
             (mx - 40, 0.6, mz - 30), lambda s, t: 0.6 * max(0.0, 1 - ((s - 44) / 36) ** 2 - ((t - 26) / 26) ** 2) * 1.5)

    def boca(s, t, P):
        if ((s - mw / 2) / (mw / 2 - 4)) ** 2 + ((t - md / 2) / (md / 2 - 3)) ** 2 < 1:
            return 0.4                                                  # la boca oberta, fosca
        return 3.0
    e.caixa_girada('motxilla', mx, mz, mw, md, mh, ma, OLIVE, 2.4,
                   cares={'davant': {'tex': (mo, (299, 165, 350, 210))}, 'dalt': {'ramp': OLIVE, 'lvl': boca},
                          'esquerra': {'ramp': OLIVE, 'lvl': lambda s, t, P: 2.0 - (0.6 if int(t) % 7 == 0 else 0)},
                          'dreta': {'ramp': OLIVE, 'lvl': lambda s, t, P: 1.8 - (0.6 if int(t) % 7 == 0 else 0)}})
    c_, s_ = math.cos(ma), math.sin(ma)

    def Pm(lx, y, lz):
        return (mx + lx * c_ - lz * s_, y, mz + lx * s_ + lz * c_)
    e.quad('motxilla', Pm(-mw / 2 + 4, mh + 9, md / 2 + 8), Pm(mw / 2 - 4, mh + 9, md / 2 + 8), Pm(mw / 2 - 4, mh, md / 2),
           Pm(-mw / 2 + 4, mh, md / 2), ramp=OLIVE, lvl=2.6, dues_cares=True)               # la tapa, caiguda enrere
    e.quad('espina', (mx + 34, 0.4, mz - 22), (mx + 48, 0.4, mz - 26), (mx + 48, 0.4, mz - 30), (mx + 34, 0.4, mz - 26),
           tex=(mo, (355, 205, 369, 213)))
    # la porta: la fulla, oberta cap a dins (frontisses a l'esquerra), i la seva ombra
    fu = tex['fulla']
    fw = dx1 - dx0
    fx_, fz_ = dx0 + fw * math.cos(FULLA), ZW - fw * math.sin(FULLA)
    e.foscor('ombra_fulla', (dx0, 0.7, ZW), (fx_ + 6, 0.7, fz_ + 4), (fx_ - 14, 0.7, fz_ - 4), (dx0 - 20, 0.7, ZW - 6),
             lambda s, t: 0.45)
    e.quad('fulla', (dx0, dh, ZW), (fx_, dh, fz_), (fx_, 0, fz_), (dx0, 0, ZW), tex=(fu, (PL.DOOR[0], PL.DOOR[1],
                                                                                        PL.DOOR[2] + 1, FY)),
           dues_cares=True)
    e.quad('fulla', (fx_, dh, fz_), (fx_ + 2.4 * math.sin(FULLA), dh, fz_ + 2.4 * math.cos(FULLA)),
           (fx_ + 2.4 * math.sin(FULLA), 0, fz_ + 2.4 * math.cos(FULLA)), (fx_, 0, fz_), ramp=PAINT, lvl=4.6,
           dues_cares=True)                                                                  # el cantell
    # primer pla: el bao del sostre i la safata, un tub que baixa a la dreta, una galleda i cables que pengen
    e.caixa('primer_pla', -80, XR + 40, HW - 16, HW, 22, 38, FOSC, 1.6,
            cares={'sota': {'ramp': FOSC, 'lvl': 1.2}, 'davant': {'ramp': FOSC, 'lvl': 2.2}})
    e.tub('primer_pla', (XR - 22, 0, 46), (XR - 22, HW, 46), 7, FOSC, 2.2, brides=62)
    # la cadira plegable, de cara a la llitera (la roba de l'Iri al respatller)
    cx, cz, ca = 70, -24, -0.5
    cc, cs = math.cos(ca), math.sin(ca)

    def Pc(lx, y, lz):
        return (cx + lx * cc - lz * cs, y, cz + lx * cs + lz * cc)
    for lx, lz in ((-15, -15), (15, -15), (-15, 15), (15, 15)):
        e.tub('primer_pla', Pc(lx, 0, lz), Pc(lx * 0.9, 40, lz * 0.9), 1.6, FOSC, 2.0)
    e.caixa_girada('primer_pla', cx, cz, 36, 34, 4, ca, FOSC, 2.4, y0=40,
                   cares={'dalt': {'ramp': FOSC, 'lvl': 3.0}})
    e.quad('primer_pla', Pc(-18, 92, 17), Pc(18, 92, 17), Pc(18, 44, 17), Pc(-18, 44, 17), ramp=FOSC,
           lvl=lambda s, t, P: 2.2 - (1.2 if 6 < t < 42 and 4 < s < 32 and int(t) % 9 < 6 else 0), dues_cares=True)
    e.quad('primer_pla', Pc(-14, 94, 15), Pc(10, 96, 16), Pc(14, 60, 19), Pc(-16, 66, 18), ramp=PL.OVERALL,
           lvl=lambda s, t, P: 1.6 + (fbm(s / 8, t / 10, 3) - 0.5) * 1.2, dues_cares=True)
    gx, gz = GALLEDA
    e.caixa_girada('primer_pla', gx, gz, 56, 40, 34, 0.32, FOSC, 1.8,
                   cares={'dalt': {'ramp': FOSC, 'lvl': lambda s, t, P: 2.8 - (1.4 if int(s) % 14 < 1.5 else 0)},
                          'davant': {'ramp': FOSC, 'lvl': lambda s, t, P: 1.6 - (0.8 if int(t) % 11 < 1.5 else 0)},
                          'esquerra': {'ramp': FOSC, 'lvl': lambda s, t, P: 2.2 - (0.8 if int(t) % 11 < 1.5 else 0)}})
    return e


# ─── Composició ─────────────────────────────────────────────────────────────

def _proj(P):
    u, v, _ = CAM.projecta(P)
    return u, v


@functools.lru_cache(maxsize=None)
def _textures():
    return {'paret': _paret_base(), 'nua': _paret_nua(), 'tauleta': _tauleta_pla(), 'llitera': _llitera_pla(),
            'motxilla': _motxilla_pla(), 'fulla': _fulla_pla()}


def _post(img):
    """El halo del llum de lectura i la claror del passadís, damunt l'escena."""
    cv = Canvas(light=LIGHT, img=img.copy())
    lx, ly = _proj((LAMP[0] + 4, LAMP[1] - 4, LAMP[2]))
    cv.glow(lx, ly, 46, (255, 214, 140), 0.5)
    cv.glow(lx, ly, 14, (255, 240, 200), 0.6)
    dx, dy = _proj(((DOOR[0] + DOOR[1]) / 2 + 12, 70, ZW + 10))
    cv.glow(dx, dy, 44, (170, 190, 150), 0.28)
    cx, cy = _proj((TAU[1] - 14, TAU[4] + 5, TAU[2] + 12))
    cv.glow(cx, cy, 10, (255, 60, 40), 0.3)                       # el despertador
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


def _capa_paret(cv_paret):
    """Un dibuix de la paret (amb un decorat) projectat per la paret del fons: només el que canvia del dibuix pla."""
    from hd.rooms.comu import _diff
    _, e = _base()
    img = _base()[0].copy()
    img.alpha_composite(e.capa(_diff(cv_paret.img, _paret_base()), {'paret_fons'}))
    return sota.fast_diff(_post(img), _base_llum())


def _ulls_dia(cv):
    cv.img.alpha_composite(_capa_paret(_paret(dia=True)))
    cv.P = cv.img.load()


def _maceta(cv):
    cv.img.alpha_composite(_capa_paret(_paret(maceta=True)))
    cv.P = cv.img.load()


PROPS = {'ulls_dia': _ulls_dia, 'maceta': _maceta}


def _frames_mar():
    """L'ull de bou de nit: onades i esquitxos (el vidre, projectat per la paret del fons)."""
    return [_capa_paret(_paret(vidre=i / 8)) for i in range(8)]


ANIMS = {'mar': {'frames': _frames_mar, 'frameDuration': 160}}


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
    lo, hi = -200.0, 2000.0
    for _ in range(60):
        z = (lo + hi) / 2
        if CAM.projecta((200, 0, z))[1] > v:
            lo = z
        else:
            hi = z
    return CAM.escala((200, 0, (lo + hi) / 2))


def _cantons_motxilla(marge):
    mx, mz, mw, md, _, ma = MOTX
    c, s = math.cos(ma), math.sin(ma)
    a, b = mw / 2 + marge, md / 2 + marge
    return [(mx + lx * c - lz * s, mz + lx * s + lz * c) for lx, lz in ((-a, -b), (a, -b), (a, b), (-a, b))]


# Capes del davant: el primer pla (sempre davant) i la motxilla (qui hi passa per darrere, hi queda darrere).
_MOTX_BASE = max(_p(x, z)[1] for x, z in _cantons_motxilla(0)) - 4
FRONT = [
    {'id': 'davant', 'mask': _amo({'primer_pla'}), 'baseline': 999, 'zIndex': 20},
    {'id': 'davant_motxilla', 'mask': _amo({'motxilla'}), 'baseline': _MOTX_BASE, 'zIndex': 20},
]

# El terra on es camina (al món): davant la llitera, fins a la paret del fons, amb la volta a la fulla de la porta;
# el davant, on el personatge arriba a 1,2 (més a prop, el terra és primer pla).
WALK_MON = [(BD + 14, 30), (BD + 14, ZW - 52), (TAU[1] + 14, ZW - 30), (DOOR[0] - 10, ZW - 30),
            (DOOR[0] + 10, ZW - 64), (DOOR[0] + 36, ZW - 64), (DOOR[0] + 50, ZW - 26), (XR - 26, ZW - 26),
            (XR - 26, 150), (250, 76), (150, 48)]
_WALK = [_p(x, z) for x, z in WALK_MON]
_V_FONS, _V_PROP = min(v for _, v in _WALK), max(v for _, v in _WALK)


def _cantons(x0, x1, y0, y1, z0, z1):
    return [(x, y, z) for x in (x0, x1) for y in (y0, y1) for z in (z0, z1)]


_bot = 211
GEOMETRIA = {
    'things': {
        'porta': {'rect': _rect_mon((DOOR[0], DOOR[2] + 4, ZW), (DOOR[1] + 4, 0, ZW),
                                    (DOOR[0] + (DOOR[1] - DOOR[0]) * math.cos(FULLA), 0,
                                     ZW - (DOOR[1] - DOOR[0]) * math.sin(FULLA))),
                  'walk': _p(DOOR[1] - 8, ZW - 34)},
        'carregador': {'rect': _rect_mon(*_cantons(0, TAU[1], 0, _y(147), TAU[2], ZW)), 'walk': _p(TAU[1] + 26, ZW - 46)},
        'got': {'rect': _rect_mon((4, _y(92), _wz(200)), (14, _y(110), _wz(214))), 'walk': _p(BD + 30, ZW - 70)},
        'maceta': {'rect': _rect_mon((_w(398), _y(136), ZW), (_w(428), _y(190), ZW)), 'walk': _p(_w(413), ZW - 40)},
        'llitera': {'rect': _rect_mon(*_cantons(0, BD + 4, 0, _y(130, _bot), _wz(19), _wz(190))),
                    'walk': _p(BD + 22, _wz(120))},
        'motxilla': {'rect': _rect_mon(*[(x, y, z) for x, z in _cantons_motxilla(0) for y in (0, MOTX[4] + 10)]),
                     'walk': _p(MOTX[0] - 40, MOTX[1] - 30)},
        'ull_de_bou': {'rect': _rect_mon((PORT[0] - 30, PORT[1] + 28, ZW), (PORT[0] + 30, PORT[1] - 30, ZW)),
                       'walk': _p(PORT[0], ZW - 40)},
        # Coses per mirar de la paret (vegeu camarot_iri_pla_comu: poster, overalls) i el llum de lectura.
        'poster': {'rect': _rect_mon((_w(285), _y(45), ZW), (_w(368), _y(131), ZW)), 'walk': _p(_w(326), ZW - 40)},
        'granota': {'rect': _rect_mon((_w(447), _y(72), ZW), (_w(496), _y(190), ZW)), 'walk': _p(_w(472), ZW - 40)},
        'protectors': {'rect': _rect_mon((_w(497), _y(74), ZW), (_w(526), _y(100), ZW)), 'walk': _p(_w(505), ZW - 40)},
        'llum': {'rect': _rect_mon((LAMP[0], LAMP[1] - 12, LAMP[2] - 12), (LAMP[0] + 8, LAMP[1] + 8, LAMP[2] + 12)),
                 'walk': _p(BD + 30, LAMP[2])},
    },
    'spawns': {'iri': _p(150, 120), 'vet': _p(300, 110), 'diu': _p(MOTX[0] + 40, MOTX[1] + 4)},
    'walkable': _WALK,
    'forats': [[_p(x, z) for x, z in _cantons_motxilla(6)]],
    'floorSquash': 0.42,                           # (la càmera, picada: el terra es veu aixafat)
    # L'ombra de contacte: la llum dominant és el llum de lectura (el punt del terra a sota); cap a la dreta i al fons.
    'characterShadow': {'enabled': True, 'color': '#06080a', 'alpha': 0.45, 'squash': 0.4, 'core': 0.6,
                        'light': {'x': _p(LAMP[0] + 20, LAMP[2])[0], 'y': _p(LAMP[0] + 20, LAMP[2])[1],
                                  'stretch': 0.7, 'reach': 170}},
    'regions': [{'id': 'perspectiva', 'active': True, 'scaleEnabled': True, 'scaleWalkSpeed': True,
                 'scaleTop': round(_escala_a(_V_FONS - 2), 3), 'scaleBottom': round(_escala_a(_V_PROP + 2), 3),
                 'points': [(0, _V_FONS - 2), (W - 1, _V_FONS - 2), (W - 1, _V_PROP + 2), (0, _V_PROP + 2)]}],
    # la llum de la sala sobre els personatges, en temps d'execució
    'characterLights': {
        'ambient': '#7c8a86',                                                           # camarot fosc, verdós
        'lights': [
            {'x': _p(LAMP[0], LAMP[2], LAMP[1])[0], 'y': _p(LAMP[0], LAMP[2], LAMP[1])[1], 'radius': 300,
             'color': '#ffd68c', 'intensity': 1.1},                                     # el llum de lectura
            {'x': _p((DOOR[0] + DOOR[1]) / 2, ZW, 80)[0], 'y': _p((DOOR[0] + DOOR[1]) / 2, ZW, 80)[1], 'radius': 200,
             'color': '#aabe96', 'intensity': 0.8},                                     # el passadís
        ],
    },
}

# Coses per mirar (tasca 061), en píxels de pantalla: la cadira plegable de l'esquerra.
GEOMETRIA['things'].update({
    'cadira': {'rect': (20, 122, 78, 250), 'walk': (125, 205)},
})
