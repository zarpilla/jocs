"""
El rebost de l'Arenga (a la coberta de sota, porta amb porta amb la sala de màquines). EN 3D (hd640/tres_d.py), a 1×.

Un magatzem estret de planxa verda, vist des de la banda de la paret de babord, mirant de biaix la cantonada de
les prestatgeries (al revés que la cuina i el menjador):
  - a la paret del fons, la **porta estanca** oberta cap a la sala de màquines (el motor, a l'altra banda), el tub
    del dipòsit 2 amb la vàlvula vermella, el calendari del 2019 i el **muntacàrregues** («250 KG», la safata);
  - a la paret de la dreta, en escorç, les **prestatgeries** de queviures, de la cantonada fins a prop de la
    càmera: les de més a prop fan de primer pla (el ratolí treu el cap d'entre els sacs d'arròs);
  - el **congelador** d'arcó, separat de la paret i una mica girat; el **tamboret** del cuiner d'abans;
  - a terra, el **registre** del dipòsit 2 (`rascades`: el pany forçat; `registre_obert`: la tapa aixecada, el forat
    i l'escala);
  - dos llums de gàbia càlids, amb la pols que sura a la llum.

Tot el detall ve del dibuix pla de sempre (rebost_pla_comu.py), projectat.

El món: x a la dreta (XR = la paret de les prestatgeries), y amunt (0 = el terra), z cap al fons (300 = la paret
del muntacàrregues); 1 unitat = 1 píxel de sala a la distància on un personatge fa ≈110 px (escala 1).
"""
import functools
import math

import hd640  # noqa: F401  (abans de cap hd.rooms: posa la llibreria a 640×360)
from PIL import Image

from hd.pix import Canvas, Light, W, H, hr, mix
from hd.rooms.arenga import WALL, DECK, CAB, REDP, SEAG, DARK, WHITEP, box, bolt, hpipe, vpipe, glow
from hd.rooms.comu import _diff
from hd.rooms.exterior import fbm
from hd640.rooms import rebost_pla_comu as PL
from hd640.rooms.rebost_pla_comu import FLOOR_Y, LAMP, WOOD, BLUEP, REG
from hd640.rooms.sala_maquines_pla_comu import ceiling
from hd640.tres_d import Camera, Escena, Llum
from hd640.safata import OBJECTES as OBJECTES_SAFATA

BOTTOM = 259                                       # la sala acaba aquí (a sota, la barra de verbs)
CT = 27                                            # al dibuix pla, on comença la paret (a dalt, el sostre)
ZW = 300                                           # la paret del fons
HW = FLOOR_Y - CT                                  # l'alçada de les parets (176)
XC = 370                                           # al dibuix pla, la cantonada: a la dreta, les prestatgeries
XR = 480                                           # la paret de la dreta (la de les prestatgeries)
PREST = (381, 627)                                 # les prestatgeries, al pla
PR_D = 34                                          # el fons de les prestatgeries
FOSC = [(3, 4, 4), (6, 9, 8), (10, 15, 13), (16, 22, 19), (23, 31, 27), (32, 42, 36)]
TEX_LIGHT = Light(ambient=-0.15, vignette=None, floor_fade=None)
LIGHT = Light(ambient=0.0, vignette=None, floor_fade=None)  # (la llum és la del món: la de l'Escena)


def _w(fx):
    """Una x del dibuix pla de la paret del fons → la x del món."""
    return fx + XR - XC


def _wz(fx):
    """Una x del dibuix pla de les prestatgeries → la z del món (la cantonada al fons, cap a la càmera)."""
    return ZW - (fx - XC)


def _y(fy):
    """Una y del dibuix pla (el terra, a FLOOR_Y) → l'alçada del món."""
    return FLOOR_Y - fy


D_MAQ = (_w(19), _w(72), _y(88))                                        # la porta de màquines: x0, x1, alt
MUNTA = (_w(PL.MUNTA[0] - 5), _w(PL.MUNTA[2] + 5), _y(PL.MUNTA[3] + 5), _y(PL.MUNTA[1] - 16))
SAFATA = (_w(PL.MUNTA[0] - 2), _w(PL.MUNTA[2] + 2), _y(PL.MUNTA[3] + 1), _y(PL.MUNTA[3] - 20))
CONG = (_w(190), 262, 98, 40, _y(155), 0.16)                             # el congelador: x, z, ample, fons, alt, gir
TAMB = (_w(117), 252)
REGM = (_w(150) - 60, _w(150) + 50, 150, 206)                           # el registre: x0, x1, z0, z1
LAMPS = ((_w(200), 210), (_w(330), 150))

CAM = Camera(pos=(90, 160, -250), yaw=0.36, pitch=0.16, f=470, centre=(320, 100))

LLUMS = [Llum((x, HW - 16, z), 250, 1.9, power=1.4) for x, z in LAMPS] + [
    Llum(((D_MAQ[0] + D_MAQ[1]) / 2, 80, ZW + 10), 90, 0.6, power=1.8),    # la sala de màquines
]


# ─── Les textures: el dibuix pla de sempre ───────────────────────────────────

def _sala(cv):
    """La paret de planxa, la canonada d'aigua dolça i el tub del dipòsit 2 amb la vàlvula (rebost_pla_comu.room,
    sense els llums de gàbia, que són en 3D)."""
    PL.plate_wall(cv, seed=11)
    ceiling(cv)
    hpipe(cv, 80, W - 1, 40, 3, SEAG, 3.0, bands=range(107, W, 93), band_ramp=WHITEP)       # aigua dolça
    for x in range(107, W, 93):
        for i in range(3):
            cv.vline(x + 4 + i, 40 - 2 + i, 40 + 2 - i, SEAG, 1.2)
    for x in range(120, W, 93):
        cv.vline(x, 34, 46, CAB, 2.0)
        cv.vline(x + 1, 34, 46, CAB, 3.4)
    vpipe(cv, 88, 40, FLOOR_Y + 3, 3, SEAG, 2.8, bands=(80, 160), band_ramp=WHITEP)
    hpipe(cv, 80, 88, 40, 3, SEAG, 3.0)
    cv.disc(88, 40, 4, 4, SEAG, lambda nx, ny: 3.2 - nx - ny)
    box(cv, 84, 120, 92, 127, SEAG, 3.4)
    for a in range(0, 360, 6):
        for rr, lv in ((6, 4.2), (5, 2.8)):
            cv.put(88 + round(math.cos(math.radians(a)) * rr), 116 + round(math.sin(math.radians(a)) * rr),
                   REDP, lv + (0.8 if 180 < a < 300 else -0.4 if a < 90 else 0))
    for a in (90, 210, 330):
        for t in range(2, 5):
            cv.put(88 + round(math.cos(math.radians(a)) * t), 116 + round(math.sin(math.radians(a)) * t), REDP, 3.0)
    cv.disc(88, 116, 1.5, 1.5, CAB, 4.4)


def _paret(safata=False, item=None, tancat=False):
    """La paret plana, de cara: la porta, el tub, el calendari i el muntacàrregues (el congelador, en 3D)."""
    cv = Canvas(light=TEX_LIGHT)
    _sala(cv)
    PL.door(cv)
    PL.dumbwaiter(cv)
    a = Canvas(light=TEX_LIGHT, transparent=True)
    PL.freezer_and_calendar(a)
    cv.img.alpha_composite(a.img.crop((0, 0, W, 150)), (0, 0))       # (només el calendari)
    cv.P = cv.img.load()
    if safata:
        PL.safata(cv)
    if item:
        PL.objecte(cv, item)
    if tancat:
        PL.porta_tancada(cv)
    return cv.img


@functools.lru_cache(maxsize=None)
def _paret_base():
    return _paret()


@functools.lru_cache(maxsize=None)
def _prestatges():
    """Les prestatgeries, sobre transparent (entre els muntants es veu la paret de darrere)."""
    cv = Canvas(light=TEX_LIGHT, transparent=True)
    PL.shelves(cv)
    return cv.img


@functools.lru_cache(maxsize=None)
def _mobles():
    """El congelador, el tamboret i el registre, sobre transparent."""
    cv = Canvas(light=TEX_LIGHT, transparent=True)
    PL.freezer_and_calendar(cv)
    PL.stool(cv)
    return cv.img


def _registre(rascades=False):
    cv = Canvas(light=TEX_LIGHT, transparent=True)
    PL.registre(cv)
    if rascades:
        PL.rascades(cv)
    return cv.img


@functools.lru_cache(maxsize=None)
def _registre_base():
    return _registre()


CONG_TEX = (144, 160, 238, FLOOR_Y + 4)
TAMB_TEX = (98, 158, 137, FLOOR_Y + 9)
REG_TEX = (REG[0], REG[1] - 2, REG[2] + 1, REG[3] + 1)


def _llum_gabia():
    cv = Canvas(light=TEX_LIGHT, transparent=True)
    PL.cage_lamp(cv, 30, ly=12, top=4)
    return cv.img.crop((20, 4, 41, 23)), (10, 0)


# ─── Les superfícies ────────────────────────────────────────────────────────

def _planxa(lvl0, seed=11):
    """Planxa verda pintada (on el dibuix pla no arriba): quadernes amb reblons, soldadures, en coordenades del món."""
    def L(s, t, P):
        val = lvl0 + (hr(int(s // 3), int(t // 5), seed) - 0.5) * 0.35 + (fbm(s / 40, t / 30, seed) - 0.5) * 0.5
        d = s % 85
        if d < 7:
            val += 0.4 + (0.9 if d < 1 else 0.5 if d < 2 else -0.3 if d >= 6 else 0.1)
            if 2.5 <= d < 4 and int(t) % 16 == 0:
                val += 1.0
        for sy in (58, 122):
            if abs(t - sy) < 1:
                val -= 1.3
        if t > HW - 24:
            val -= 0.9
        return val
    return L


def _terra(s, t, P):
    """Xapa estriada vista des de dalt, amb les juntes de les planxes: s'empetiteix cap al fons."""
    x, z = P[0], P[2]
    gx, gz = int(x // 6), int(z // 6)
    lx, lz = x - (gx + 0.5) * 6, z - (gz + 0.5) * 6
    d = (lx + lz) if (gx + gz) % 2 else (lx - lz)
    stud = abs(d) < 0.9 and abs(lx - lz if (gx + gz) % 2 else lx + lz) < 4.0
    v = 2.5 + (fbm(x / 70, z / 40, 9) - 0.5) * 1.0 + (0.9 if stud else 0)
    if x % 101 < 1.2 or z % 80 < 1.2:
        v -= 1.6
    return v


def escena(cv, tex, estat=frozenset()):
    """Tota la sala, de lluny a prop. `estat`: 'obert' (el registre obert). → l'Escena (qui ha pintat què)."""
    e = Escena(cv, CAM, LLUMS, ambient=-0.45)
    zn = CAM.pos[2] + 60
    paret, prest, mob, reg = tex['paret'], tex['prestatges'], tex['mobles'], tex['registre']
    # el sostre, fosc, amb les safates de cables
    e.quad('sostre', (0, HW, zn), (XR, HW, zn), (XR, HW, ZW), (0, HW, ZW), ramp=DARK,
           lvl=lambda s, t, P: 2.0 + (1.2 if P[0] % 85 < 12 else 0), dues_cares=True)
    # la paret de babord (x = 0), la del fons (el dibuix pla, de x 0 a 370) i la de les prestatgeries (x = XR)
    e.quad('paret_esq', (0, HW, zn), (0, HW, ZW), (0, 0, ZW), (0, 0, zn), ramp=WALL, lvl=_planxa(3.0, 12))
    e.quad('paret_fons_esq', (0, HW, ZW), (XR - XC, HW, ZW), (XR - XC, 0, ZW), (0, 0, ZW), ramp=WALL, lvl=_planxa(3.1, 13))
    e.quad('paret_fons', (XR - XC, HW, ZW), (XR, HW, ZW), (XR, 0, ZW), (XR - XC, 0, ZW), tex=(paret, (0, CT, XC, FLOOR_Y)))
    e.quad('paret_dreta', (XR, HW, ZW), (XR, HW, zn), (XR, 0, zn), (XR, 0, ZW), ramp=WALL, lvl=_planxa(2.8, 14))
    # el terra
    e.quad('terra', (0, 0, ZW), (XR, 0, ZW), (XR, 0, zn), (0, 0, zn), ramp=DECK, lvl=_terra)
    for lx, lz in LAMPS:                                            # els bassals de llum sota els llums de gàbia
        e.claror((lx - 90, 0.3, lz + 90), (lx + 90, 0.3, lz + 90), (lx + 90, 0.3, lz - 90), (lx - 90, 0.3, lz - 90),
                 (255, 214, 150), lambda s, t: 0.22 * max(0.0, 1 - math.hypot(s - 90, t - 90) / 90) ** 1.4)
    # el registre del dipòsit 2, a terra
    r0, r1, rz0, rz1 = REGM
    if 'obert' in estat:
        e.quad('registre', (r0 + 6, 0.4, rz1 - 4), (r1 - 6, 0.4, rz1 - 4), (r1 - 6, 0.4, rz0 + 4), (r0 + 6, 0.4, rz0 + 4),
               ramp=DARK, lvl=lambda s, t, P: 0.6 + (1.6 if hr(int(s // 3), int(t // 2), 5) > 0.93 else 0))
        cx = (r0 + r1) / 2
        for lx in (cx - 12, cx + 12):                               # l'escala, que baixa i es perd
            e.caixa('registre', lx - 1, lx + 1, 0.5, 14, rz1 - 8, rz1 - 6, CAB, 4.4)
        for k in range(4):
            e.quad('registre', (cx - 12, 0.6, rz1 - 9 - k * 9), (cx + 12, 0.6, rz1 - 9 - k * 9),
                   (cx + 12, 0.6, rz1 - 11 - k * 9), (cx - 12, 0.6, rz1 - 11 - k * 9), ramp=CAB, lvl=4.4 - k * 0.9)
        e.quad('registre', (r0 + 6, 56, rz1 + 2), (r1 - 6, 56, rz1 + 2), (r1 - 6, 0.5, rz1 - 2), (r0 + 6, 0.5, rz1 - 2),
               ramp=CAB, dues_cares=True,
               lvl=lambda s, t, P: 3.6 - (1.4 if s < 3 or s > r1 - r0 - 15 or t < 3 else 0)
               + (hr(int(s // 2), int(t // 2), 4) - 0.5) * 0.6 - (1.0 if hr(int(s // 3), int(t // 3), 7) > 0.85 else 0))
    else:
        e.quad('registre', (r0, 0.4, rz1), (r1, 0.4, rz1), (r1, 0.4, rz0), (r0, 0.4, rz0), tex=(reg, REG_TEX))
    # la foscor dels racons
    e.foscor('racons', (0, 0.5, ZW), (XR, 0.5, ZW), (XR, 0.5, zn), (0, 0.5, zn),
             lambda s, t: max(0.6 * max(0.0, 1 - t / 24), 0.5 * max(0.0, 1 - s / 22), 0.6 * max(0.0, 1 - (XR - PR_D - s) / 30)))
    e.foscor('cantonada', (XR - 60, HW, ZW - 0.5), (XR, HW, ZW - 0.5), (XR, 0, ZW - 0.5), (XR - 60, 0, ZW - 0.5),
             lambda s, t: 0.55 * max(0.0, s / 60) ** 2)
    e.foscor('sostre_fosc', (0, HW - 0.5, ZW - 0.6), (XR, HW - 0.5, ZW - 0.6), (XR, 0, ZW - 0.6), (0, 0, ZW - 0.6),
             lambda s, t: 0.45 * max(0.0, 1 - t / 40))
    # les quadernes del sostre, que fugen
    for bx in (_w(-11 + 85 * k) for k in range(-1, 5)):
        if 0 < bx < XR:
            e.caixa('sostre', bx - 3, bx + 11, HW - 10, HW, 120, ZW, WALL, 2.6,
                    cares={'sota': {'ramp': WALL, 'lvl': 2.0}, 'esquerra': {'ramp': WALL, 'lvl': 2.8},
                           'dreta': {'ramp': WALL, 'lvl': 1.4}})
    # les prestatgeries, contra la paret de la dreta: el davant (el dibuix pla) i el costat del fons
    e.foscor('ombres', (XR - PR_D - 14, 0.6, ZW), (XR, 0.6, ZW), (XR, 0.6, _wz(PREST[1]) - 6), (XR - PR_D - 14, 0.6, _wz(PREST[1]) - 6),
             lambda s, t: 0.5 * min(1.0, max(0.0, s / 14)))
    e.quad('prestatges', (XR - PR_D, _y(53), _wz(PREST[0])), (XR - PR_D, _y(53), _wz(PREST[1])),
           (XR - PR_D, _y(FLOOR_Y + 4), _wz(PREST[1])), (XR - PR_D, _y(FLOOR_Y + 4), _wz(PREST[0])),
           tex=(prest, (PREST[0], 53, PREST[1], FLOOR_Y + 4)))
    for lv in (85, 125, 165, FLOOR_Y - 3):                          # els prestatges, amb fons
        e.caixa('prestatges', XR - PR_D, XR, _y(lv + 4), _y(lv), _wz(PREST[1]), _wz(PREST[0]), [(18, 20, 22), (34, 38, 42),
                (54, 60, 64), (78, 84, 88), (104, 110, 112), (134, 140, 140)], 3.6,
                cares={'dalt': {'ramp': [(18, 20, 22), (34, 38, 42), (54, 60, 64), (78, 84, 88), (104, 110, 112)], 'lvl': 2.6},
                       'esquerra': {'ramp': [(18, 20, 22), (34, 38, 42), (54, 60, 64), (78, 84, 88), (104, 110, 112),
                                             (134, 140, 140)], 'lvl': 4.4}})
    # el congelador d'arcó, separat de la paret i una mica girat
    cx_, cz_, cw, cd, ch, ca = CONG
    e.foscor('ombres', (cx_ - 60, 0.6, cz_ + 36), (cx_ + 60, 0.6, cz_ + 36), (cx_ + 60, 0.6, cz_ - 34),
             (cx_ - 60, 0.6, cz_ - 34), lambda s, t: 0.6 * max(0.0, 1 - ((s - 60) / 58) ** 2 - ((t - 35) / 30) ** 2) * 1.5)
    e.caixa_girada('congelador', cx_, cz_, cw, cd, ch, ca, WHITEP, 3.0,
                   cares={'davant': {'tex': (mob, CONG_TEX)},
                          'dalt': {'ramp': WHITEP, 'lvl': lambda s, t, P: 4.4 - (1.6 if abs(t - cd + 3) < 0.8 else 0)
                                   + (fbm(s / 20, t / 10, 4) - 0.5) * 0.4},
                          'esquerra': {'ramp': WHITEP, 'lvl': lambda s, t, P: 3.4 - (1.6 if t > ch - 6 else 0)},
                          'dreta': {'ramp': WHITEP, 'lvl': 2.4}})
    # el tamboret del cuiner d'abans, amb la llauna-cendrer
    tx, tz = TAMB
    e.foscor('ombres', (tx - 22, 0.6, tz + 16), (tx + 22, 0.6, tz + 16), (tx + 22, 0.6, tz - 16), (tx - 22, 0.6, tz - 16),
             lambda s, t: 0.6 * max(0.0, 1 - ((s - 22) / 20) ** 2 - ((t - 16) / 14) ** 2) * 1.5)
    e.sprite('tamboret', mob.crop(TAMB_TEX), (117 - TAMB_TEX[0], FLOOR_Y + 8 - TAMB_TEX[1]), (tx, 0, tz))
    # els llums de gàbia
    img, peu = _llum_gabia()
    for lx, lz in LAMPS:
        e.sprite('llums', img, peu, (lx, HW, lz), escala_img=1.3)
    # primer pla: sacs i caixes en silueta a baix a l'esquerra, la canonada i les safates de cables del sostre
    e.tub('primer_pla', (-60, HW - 8, -70), (XR + 60, HW - 8, -70), 9, FOSC, 2.4, brides=110)
    e.caixa_girada('primer_pla', 70, 40, 64, 48, 46, -0.25, FOSC, 1.6,
                   cares={'dalt': {'ramp': FOSC, 'lvl': lambda s, t, P: 3.0 - (1.2 if abs(s - 30) < 2 else 0)},
                          'davant': {'ramp': FOSC, 'lvl': 1.4}, 'dreta': {'ramp': FOSC, 'lvl': 2.2}})
    e.caixa('primer_pla', 0, 18, 0, HW, 46, 62, FOSC, 2.0,
            cares={'dreta': {'ramp': FOSC, 'lvl': lambda s, t, P: 2.8 - (1.4 if s < 2 else 0)
                             + (1.6 if int(t) % 16 < 2 and 6 < s < 14 else 0)},
                   'davant': {'ramp': FOSC, 'lvl': 1.2}})
    return e


# ─── Composició ─────────────────────────────────────────────────────────────

@functools.lru_cache(maxsize=None)
def _textures():
    return {'paret': _paret_base(), 'prestatges': _prestatges(), 'mobles': _mobles(), 'registre': _registre_base()}


def _proj(P):
    u, v, _ = CAM.projecta(P)
    return u, v


def _brills(cv):
    for lx, lz in LAMPS:
        u, v = _proj((lx, HW - 12, lz))
        k = CAM.escala((lx, HW, lz))
        glow(cv, round(u), round(v), round(44 * k), (255, 214, 140), 0.4)
        glow(cv, round(u), round(v), round(14 * k), (255, 240, 200), 0.55)


def _render(estat=frozenset(), tex=None):
    cv = Canvas(light=LIGHT)
    e = escena(cv, tex or _textures(), estat)
    _brills(cv)
    cv.rect(0, BOTTOM + 1, W - 1, H - 1, [(0, 0, 0)], 0, lit=0)    # la barra de verbs: negre
    return cv.img, e


@functools.lru_cache(maxsize=None)
def _base():
    return _render()


def bg(cv):
    cv.img.paste(_base()[0])
    cv.P = cv.img.load()


def _fotograma(capes):
    img = _base()[0].copy()
    for c in capes:
        img.alpha_composite(c)
    return _diff(img, _base()[0])


def safata(cv):
    _, e = _base()
    cv.img.alpha_composite(_fotograma([e.capa(_paret(safata=True), {'paret_fons'})]))
    cv.P = cv.img.load()


def rascades(cv):
    _, e = _base()
    cv.img.alpha_composite(_fotograma([e.capa(_registre(rascades=True), {'registre'})]))
    cv.P = cv.img.load()


def registre_obert(cv):
    img, _ = _render(frozenset({'obert'}))
    cv.img.alpha_composite(_diff(img, _base()[0]))
    cv.P = cv.img.load()


def _safata_amb(item):
    def prop(cv):
        _, e = _base()
        cv.img.alpha_composite(_fotograma([e.capa(_paret(safata=True, item=item), {'paret_fons'})]))
        cv.P = cv.img.load()
    return prop


def munta_tancat(cv):
    """El muntacàrregues en marxa: la portella baixada (es mostra un moment en enviar-hi una cosa)."""
    _, e = _base()
    cv.img.alpha_composite(_fotograma([e.capa(_paret(tancat=True), {'paret_fons'})]))
    cv.P = cv.img.load()


PROPS = {'safata': safata, 'munta_tancat': munta_tancat, 'rascades': rascades, 'registre_obert': registre_obert,
         **{f'safata_{item}': _safata_amb(item) for item in OBJECTES_SAFATA}}


# ─── Animacions ─────────────────────────────────────────────────────────────

def _frames_pols():
    """Pols que sura a la llum dels dos llums de gàbia (cada mota fa un llaç tancat: el bucle no salta)."""
    base = _base()[0]
    motes = []
    for li, (lx, lz) in enumerate(LAMPS):
        for k in range(22):
            motes.append((lx + (hr(k, li, 1) - 0.5) * 120, HW - 30 - hr(k, li, 2) * 110, lz + (hr(k, li, 7) - 0.5) * 100,
                          8 + hr(k, li, 3) * 13, 5 + hr(k, li, 4) * 11, hr(k, li, 5), 1 + int(hr(k, li, 6) * 2), lx, lz))
    n = 48
    out = []
    for i in range(n):
        img = base.copy()
        P = img.load()
        t = i / n
        for (cx, cy, cz, ax, ay, ph, fx, lx, lz) in motes:
            a = 2 * math.pi * (t + ph)
            Pw = (cx + ax * math.sin(fx * a), cy + ay * math.sin(a + ph * 3), cz)
            near = max(0.0, 1 - math.hypot(Pw[0] - lx, Pw[1] - HW, Pw[2] - lz) / 170)
            alpha = near * (0.5 + 0.5 * (0.5 + 0.5 * math.sin(a * 2 + ph * 7)))
            u, v, _ = CAM.projecta(Pw)
            x, y = round(u), round(v)
            if alpha > 0.08 and 0 <= x < W and 0 <= y <= BOTTOM:
                P[x, y] = mix(P[x, y][:3], (255, 236, 196), alpha) + (255,)
        out.append(_diff(img, base))
    return out


def _frames_ratoli():
    """Un ratolí treu el cap d'entre els sacs d'arròs, olora i s'hi torna a amagar (projectat per la prestatgeria)."""
    _, e = _base()
    vuit = Image.new('RGBA', (W, H), (0, 0, 0, 0))
    out, cache = [], {}
    for fr in PL._frames_ratoli():
        key = fr.tobytes()
        if key not in cache:
            cache[key] = _fotograma([e.capa(fr, {'prestatges'})]) if fr.getbbox() else vuit
        out.append(cache[key])
    return out


ANIMS = {'pols': {'frames': _frames_pols, 'frameDuration': 130},
         'ratoli': {'frames': _frames_ratoli, 'frameDuration': 110}}


def _amo(ids):
    def mask(x, y):
        _, e = _base()
        return e.ids[e.amo[y * e.cv.w + x]] in ids
    return mask


def _p(x, z, y=0.0):
    u, v, _ = CAM.projecta((x, y, z))
    return round(u), round(v)


# Capes del davant: el congelador i el tamboret (s'hi passa per darrere), el primer pla (sempre davant).
FRONT = [
    {'id': 'davant_congelador', 'mask': _amo({'congelador'}), 'baseline': _p(CONG[0], CONG[1] - CONG[3] / 2)[1], 'zIndex': 20, 'variants': ('registre_obert',)},
    {'id': 'davant_tamboret', 'mask': _amo({'tamboret'}), 'baseline': _p(TAMB[0], TAMB[1])[1], 'zIndex': 20, 'variants': ('registre_obert',)},
    {'id': 'davant_primer_pla', 'mask': _amo({'primer_pla'}), 'baseline': 999, 'zIndex': 20, 'variants': ('registre_obert',)},
]


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
        if CAM.projecta((200, 0, z))[1] > v:
            lo = z
        else:
            hi = z
    return CAM.escala((200, 0, (lo + hi) / 2))


def _talla(poly, vmax):
    """El polígon (de pantalla) retallat per sota de `vmax`: on un personatge passaria de l'escala màxima."""
    out = []
    for (ax, ay), (bx, by) in zip(poly, poly[1:] + poly[:1]):
        if ay <= vmax:
            out.append((ax, ay))
        if (ay <= vmax) != (by <= vmax):
            k = (vmax - ay) / (by - ay)
            out.append((round(ax + (bx - ax) * k), vmax))
    return out


def _v_escala(k):
    lo, hi = 0.0, float(BOTTOM)
    for _ in range(40):
        m = (lo + hi) / 2
        if _escala_a(m) < k:
            lo = m
        else:
            hi = m
    return int(lo)


# El terra on es camina (al món): de la porta de màquines a les prestatgeries; el congelador, un forat.
WALL_Z = ZW - 10
WALK_MON = [(20, 20), (20, WALL_Z), (D_MAQ[1] + 30, WALL_Z), (D_MAQ[1] + 30, 274), (XR - PR_D - 8, 274),
            (XR - PR_D - 8, 20)]
ESCALA_MAX = 1.2
_WALK = _talla([_p(x, z) for x, z in WALK_MON], _v_escala(ESCALA_MAX))
_V_FONS, _V_PROP = min(v for _, v in _WALK), max(v for _, v in _WALK)
_c, _s = math.cos(CONG[5]), math.sin(CONG[5])
_FORAT = [_p(CONG[0] + lx * _c - lz * _s, CONG[1] + lx * _s + lz * _c)
          for lx, lz in ((-CONG[2] / 2 - 4, -CONG[3] / 2 - 3), (CONG[2] / 2 + 4, -CONG[3] / 2 - 3),
                         (CONG[2] / 2 + 4, CONG[3] / 2 + 3), (-CONG[2] / 2 - 4, CONG[3] / 2 + 3))]

GEOMETRIA = {
    'things': {
        'porta': {'rect': _rect_mon((D_MAQ[0] - 12, D_MAQ[2] + 6, ZW), (D_MAQ[1] + 4, 0, ZW)),
                  'walk': _p((D_MAQ[0] + D_MAQ[1]) / 2, WALL_Z - 4)},
        'munta': {'rect': _rect_mon((MUNTA[0], MUNTA[3], ZW), (MUNTA[1], SAFATA[3] + 1, ZW)),
                  'walk': _p((MUNTA[0] + MUNTA[1]) / 2, 266)},
        'safata': {'rect': _rect_mon((SAFATA[0], SAFATA[3], ZW), (SAFATA[1], SAFATA[2], ZW)),
                   'walk': _p((MUNTA[0] + MUNTA[1]) / 2, 266)},
        'prestatges': {'rect': _rect_mon((XR - PR_D, _y(53), _wz(PREST[0])), (XR - PR_D, 0, _wz(PREST[0])),
                                         (XR - PR_D, _y(53), 150), (XR - PR_D, 0, 150)),
                       'walk': _p(XR - PR_D - 16, 200)},
        'registre': {'rect': _rect_mon((REGM[0], 0, REGM[2]), (REGM[1], 0, REGM[2]), (REGM[0], 0, REGM[3]),
                                       (REGM[1], 0, REGM[3])), 'walk': _p(REGM[1] + 16, (REGM[2] + REGM[3]) / 2)},
    },
    'spawns': {'iri': _p(300, 170), 'vet': _p(360, 130)},
    'walkable': _WALK,
    'forats': [_FORAT],
    'floorSquash': 0.4,
    # L'ombra de contacte: la llum dominant és el llum de gàbia del fons.
    'characterShadow': {'enabled': True, 'color': '#06100c', 'alpha': 0.45, 'squash': 0.4, 'core': 0.6,
                        'light': {'x': _p(*LAMPS[0])[0], 'y': _p(*LAMPS[0])[1], 'stretch': 0.6, 'reach': 160}},
    'regions': [{'id': 'perspectiva', 'active': True, 'scaleEnabled': True, 'scaleWalkSpeed': True,
                 'scaleTop': round(_escala_a(_V_FONS - 2), 3), 'scaleBottom': round(_escala_a(_V_PROP + 2), 3),
                 'points': [(0, _V_FONS - 2), (W - 1, _V_FONS - 2), (W - 1, _V_PROP + 2), (0, _V_PROP + 2)]}],
    'characterLights': {
        'ambient': '#7c9488',
        'lights': [{'x': _p(x, z, HW - 16)[0], 'y': _p(x, z, HW - 16)[1], 'radius': 220, 'color': '#ffd28c',
                    'intensity': 0.8} for x, z in LAMPS],
    },
}
