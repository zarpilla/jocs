"""
La cuina de l'Arenga. EN 3D (hd640/tres_d.py), a 1×.

La mateixa càmera que el menjador (una mica alta, des de la banda del marbre d'en Tomàs), que mira de biaix la
cantonada dels fogons:
  - a la paret de l'esquerra, en escorç, la **porta del menjador**, el **muntacàrregues** (amb la safata, quan hi ha
    arribat alguna cosa), el **passaplats** i la **boca del tub de veu**;
  - a la paret del fons, la **cambra freda** (la boira freda s'escapa per sota la porta i s'arrossega pel terra);
  - els **fogons**, amb volum, l'olla gran i la cafetera al damunt (el vapor puja cap a la campana i les olles
    penjades); l'**armari de les olles**, de fusta, separat de la paret (la Vet s'hi amaga: `armari_obert`); el
    **forn**, amb el pa a dins; el **marbre** d'en Tomàs amb la pasta i els pans, el sac de farina i l'ull de bou;
  - al mig, el **taulell de treball** d'acer, girat: s'hi passa per davant i per darrere;
  - primer pla: sacs i caixes en silueta a baix a l'esquerra, la canonada del sostre i un pilar de quaderna.

Tot el detall ve del dibuix pla de sempre (cuina_pla_comu.py), projectat; els fogons i el marbre se separen en la
part de la paret, el moble i el que hi ha al damunt (les versions d'aquí, `_fogons_*` i `_forner_*`).

El món: x a la dreta (0 = la paret del menjador), y amunt (0 = el terra), z cap al fons (300 = la paret dels fogons);
1 unitat = 1 píxel de sala a la distància on un personatge fa ≈110 px (escala 1).
"""
import functools
import math

import hd640  # noqa: F401  (abans de cap hd.rooms: posa la llibreria a 640×360)

from hd.pix import Canvas, Light, W, H, hr, mix
from hd.rooms.arenga import CAB, DARK, WHITEP, REDP, YELL, BRASS, SEAG, box, bolt, hpipe, glow
from hd.rooms.comu import _diff, text
from hd.rooms.exterior import fbm
from hd.rooms.principal import CREAM, TEAK, wear, porthole, day_porthole
from hd.rooms.cuina import STEEL, TILE, QUARRY, FIRE, BREAD, FLOUR, COPPERP, ICE
from hd640.rooms import cuina_pla_comu as PL
from hd640.rooms.cuina_pla_comu import tiles, STOVE, COUNTER_Y, FLOOR_Y, PORT
from hd640.rooms.laboratori_pla_comu import lamp
from hd640.tres_d import Camera, Escena, Llum

BOTTOM = 259                                       # la sala acaba aquí (a sota, la barra de verbs)
ZW = 300                                           # la paret del fons
HW = PL.FLOOR_Y - PL.CEIL_H                        # l'alçada de les parets (179)
XL = 222                                           # al dibuix pla, la cantonada: a l'esquerra, la paret del menjador
XR = 470                                           # la paret de la dreta
FOSC = [(4, 3, 3), (9, 7, 6), (15, 12, 10), (22, 18, 15), (31, 26, 21), (42, 35, 28)]
TEX_LIGHT = Light(ambient=-0.15, vignette=None, floor_fade=None)
LIGHT = Light(ambient=0.0, vignette=None, floor_fade=None)  # (la llum és la del món: la de l'Escena)


def _w(fx):
    """Una x del dibuix pla de la paret del fons → la x del món."""
    return fx - XL


def _wz(fx):
    """Una x del dibuix pla de la paret del menjador → la z del món."""
    return ZW - XL + fx


def _y(fy):
    """Una y del dibuix pla (el terra, a FLOOR_Y) → l'alçada del món."""
    return FLOOR_Y - fy


TOP = COUNTER_Y - 5                                # el sobre dels fogons i del marbre, al pla
FOG = (_w(STOVE[0] - 4), _w(STOVE[1] + 4), ZW - 34, _y(TOP))           # els fogons: x0, x1, z davant, alçada
ARM = (_w(PL.ARMARI[0] - 3), _w(PL.ARMARI[2] + 3), ZW - 32, _y(PL.ARMARI[1]))  # l'armari (sense la cornisa)
FORN = (_w(PL.FORN[0]), _w(PL.FORN[2]), ZW - 36, _y(PL.FORN[1]))
MARB = (_w(560), _w(W), ZW - 40, _y(TOP))                               # el marbre d'en Tomàs
CFR = (_w(PL.CFREDA[0] - 4), _w(PL.CFREDA[2] + 4), _y(PL.CFREDA[1] - 4))  # la cambra freda: x0, x1, alt
ILLA = (196, 146, 96, 44, 54, 0.2)                                      # el taulell del mig: x, z, ample, fons, alt, gir
D_PORTA = (_wz(PL.D_PORTA[0]), _wz(PL.D_PORTA[2]), _y(PL.D_PORTA[1]))
MUNTA = (_wz(PL.MUNTA[0]), _wz(PL.MUNTA[2]), _y(PL.MUNTA[3] + 32), _y(PL.MUNTA[1] - 12))  # z0, z1, y0, y1
CAB_IN = (_wz(PL.CAB_IN[0]), _wz(PL.CAB_IN[2]), _y(PL.CAB_IN[3]), _y(PL.CAB_IN[1]))
BOCA = (_wz(200), _wz(222), _y(139), _y(93))
LAMPS = ((60, 214), (250, 200), (110, 100), (360, 110))

CAM = Camera(pos=(390, 160, -250), yaw=-0.36, pitch=0.16, f=470, centre=(320, 100))

LLUMS = [Llum((x, HW - 14, z), 240, 1.6, power=1.4) for x, z in LAMPS] + [
    Llum(((FOG[0] + FOG[1]) / 2, 104, ZW - 26), 120, 1.2, power=1.6),      # el llum de la campana
    Llum(((FORN[0] + FORN[1]) / 2, 40, FORN[2] - 6), 90, 1.0, power=1.8),   # el vidre del forn
]


# ─── Els fogons i el marbre, separats en paret, moble i el que hi ha al damunt (de cuina_pla_comu) ───

def _fogons_paret(cv):
    """Els fogons, la part de la paret: la rajola amb el greix, la campana i les olles penjades."""
    x0, x1 = STOVE
    top = COUNTER_Y - 5
    tiles(cv, x0 - 3, 53, x1 + 3, top, seed=3)
    for y in range(90, top):                                             # greix a la rajola de sobre els fogons
        for x in range(x0, x1):
            if hr(x // 3, y // 3, 17) > 0.86 - (y - 90) * 0.004:
                cv.flat(x, y, mix(cv.get(x, y), (150, 120, 70), 0.18))
    # la campana, amb el filtre de làmines i el llum
    cv.poly([(x0 - 8, 69), (x1 + 8, 69), (x1 - 3, 53), (x0 + 3, 53)], STEEL, lambda x, y: 4.2 + (y - 53) * 0.05)
    cv.hline(x0 - 6, x1 + 6, 66, STEEL, 5.8)
    cv.rect(x0 + 3, 35, x1 - 3, 52, STEEL, 3.4)
    cv.vline(x0 + 3, 35, 52, STEEL, 4.6)
    cv.vline(x1 - 3, 35, 52, STEEL, 2.4)
    for x in range(x0 + 8, x1 - 5, 5):
        cv.vline(x, 38, 49, STEEL, 2.4)
        cv.vline(x + 1, 38, 49, STEEL, 4.4)
    for bx in (x0 + 5, x1 - 5):
        bolt(cv, bx, 37, STEEL, 4.8)
    cv.hline(x0 - 8, x1 + 8, 69, STEEL, 2.0)
    cv.rect(x0 + 32, 70, x1 - 32, 71, [(160, 140, 90), (255, 240, 190), (255, 252, 236)], 1.6, lit=0)
    glow(cv, (x0 + x1) // 2, 74, 24, (255, 236, 190), 0.4)
    # la barra amb les olles, els cassons i els cullerots penjats
    hpipe(cv, x0 - 3, x1 + 3, 80, 1, STEEL, 4.8)
    for hx in (x0 - 1, x1 + 1):
        cv.vline(hx, 70, 80, STEEL, 3.6)
    hooks = ((x0 + 6, 'pan', 12), (x0 + 24, 'ladle', 0), (x0 + 35, 'pot', 9), (x0 + 53, 'pan', 9),
             (x0 + 68, 'whisk', 0), (x0 + 80, 'pot', 7))
    for hx, kind, r in hooks:
        cv.vline(hx, 81, 85, STEEL, 3.0)
        cv.put(hx + 1, 85, STEEL, 3.0)
        if kind == 'pan':
            cv.vline(hx, 86, 96, STEEL, 3.4)
            cv.vline(hx + 1, 86, 96, STEEL, 2.2)
            ramp = COPPERP if r > 10 else STEEL
            cv.disc(hx, 96 + r, r, r, ramp, lambda nx, ny: 3.8 - nx * 1.2 - ny * 1.0)
            cv.disc(hx, 96 + r, r - 3, r - 3, ramp, lambda nx, ny: 2.6 + nx * 0.6 + ny * 0.6)
            cv.disc(hx - r // 3, 96 + r // 2 + 1, 2, 1, ramp, 6.0)
        elif kind == 'ladle':
            cv.vline(hx, 86, 109, STEEL, 4.6)
            cv.vline(hx + 1, 86, 109, STEEL, 3.0)
            cv.disc(hx, 113, 4, 3.5, STEEL, lambda nx, ny: 4.0 - nx - ny)
            cv.disc(hx - 1, 112, 2, 1, STEEL, 2.2)
        elif kind == 'whisk':
            cv.vline(hx, 86, 96, TEAK, 3.6)
            for dx in (-3, -1, 1, 3):
                for y in range(97, 109):
                    cv.put(hx + round(dx * math.sin((y - 96) / 13 * math.pi)), y, STEEL, 4.6 - abs(dx) * 0.3)
        else:
            cv.line(hx - 5, 86, hx + 5, 86, STEEL, 3.0)
            for y in range(88, 88 + r * 2):
                for x in range(hx - r, hx + r + 1):
                    u = (x - hx) / (r + 0.5)
                    cv.put(x, y, COPPERP, 3.6 + 1.4 * (-0.3 - u) - 0.8 * u * u)
            cv.hline(hx - r, hx + r, 88, COPPERP, 5.0)
            cv.hline(hx - r - 3, hx - r, 91, COPPERP, 3.0)
            cv.hline(hx + r, hx + r + 3, 91, COPPERP, 2.4)



def _fogons_cos(cv):
    """Els fogons, el cos d'acer (el davant) i el sobre amb la barana de mar."""
    x0, x1 = STOVE
    top = COUNTER_Y - 5
    # el cos d'acer: tauler de mànecs, porta del forn petit amb vidre i un calaix
    box(cv, x0, top, x1, FLOOR_Y - 1, STEEL, 3.8, grad=1.0)
    for i, kx in enumerate(range(x0 + 10, x1 - 6, 13)):                 # mànecs
        cv.disc(kx, top + 7, 3, 3, DARK, lambda nx, ny: 2.4 - nx - ny)
        cv.put(kx, top + 5, STEEL, 6.0)
        cv.put(kx + 1, top + 5, STEEL, 5.0)
    box(cv, x0 + 5, top + 14, x1 - 5, FLOOR_Y - 18, STEEL, 3.4)
    hpipe(cv, x0 + 10, x1 - 10, top + 18, 1, STEEL, 6.0)
    for y in range(top + 24, FLOOR_Y - 26):                               # el vidre del forn petit, fosc
        for x in range(x0 + 16, x1 - 16):
            cv.put(x, y, DARK, 1.6 + (0.9 if (x - y) % 23 < 2 else 0), lit=0.3)
    box(cv, x0 + 5, FLOOR_Y - 15, x1 - 5, FLOOR_Y - 5, STEEL, 3.2)
    hpipe(cv, (x0 + x1) // 2 - 9, (x0 + x1) // 2 + 9, FLOOR_Y - 10, 0, STEEL, 5.4)
    # el sobre i la barana de mar
    cv.rect(x0 - 3, top - 4, x1 + 3, top, STEEL, 2.6)
    cv.hline(x0 - 3, x1 + 3, top - 4, STEEL, 5.4)
    for px in (x0 - 3, x0 + 29, x0 + 59, x1 + 3):
        cv.vline(px, top - 16, top - 4, STEEL, 4.4)
        cv.vline(px + 1, top - 16, top - 4, STEEL, 2.6)
    hpipe(cv, x0 - 3, x1 + 3, top - 16, 1, STEEL, 4.6)


def _fogons_olles(cv):
    """L'olla gran i la cafetera, damunt els fogons."""
    x0, x1 = STOVE
    top = COUNTER_Y - 5
    # l'olla gran (amb tapa i nanses) i la cafetera de coure, subjectes amb barres
    ox = 256
    for y in range(top - 29, top - 4):
        for x in range(ox - 15, ox + 16):
            u = (x - ox) / 15.5
            cv.put(x, y, STEEL, 4.6 + 1.6 * (-0.3 - u) - 1.0 * u * u)
    for y in (top - 24, top - 10):                                         # els anells de l'olla
        cv.hline(ox - 14, ox + 14, y, STEEL, 3.2)
    cv.disc(ox, top - 29, 15, 3, STEEL, lambda nx, ny: 5.6 - ny * 0.8)
    cv.disc(ox, top - 29, 12, 2, STEEL, 4.4)
    cv.rect(ox - 3, top - 35, ox + 3, top - 32, DARK, 2.0)               # el pom de la tapa
    cv.hline(ox - 2, ox + 2, top - 35, DARK, 3.4)
    for sx in (-1, 1):
        cv.rect(ox + sx * 15 + min(0, sx * 4), top - 21, ox + sx * 15 + max(0, sx * 4), top - 18, DARK, 1.6)
    cv.hline(ox - 20, ox + 20, top - 12, STEEL, 5.6)                      # la barra que la subjecta
    kx = 299
    cv.disc(kx, top - 12, 9, 8, COPPERP, lambda nx, ny: 3.6 - nx * 1.3 - ny * 1.0)
    cv.disc(kx - 3, top - 15, 2, 2, COPPERP, 6.0)
    cv.line(kx + 8, top - 13, kx + 15, top - 19, COPPERP, 3.4)            # el broc
    cv.line(kx + 8, top - 12, kx + 15, top - 18, COPPERP, 2.0)
    cv.disc(kx, top - 20, 3, 1.5, DARK, 2.0)
    cv.line(kx - 9, top - 14, kx - 13, top - 8, DARK, 1.4)                # la nansa
    cv.line(x0 + 16, top - 11, x0 + 16, top - 6, DARK, 1.0)


def _forner_paret(cv):
    """El marbre d'en Tomàs, la part de la paret: la rajola, les espècies i l'ull de bou."""
    x0, x1 = 563, W - 1
    tiles(cv, x0, 75, x1, COUNTER_Y - 5, seed=4)
    # prestatge d'espècies, amb la barana de mar
    box(cv, x0 + 3, 64, x1, 67, TEAK, 4.0)
    for i, sx in enumerate(range(x0 + 5, x1 - 5, 8)):
        jar = (REDP, YELL, SEAG, TEAK, REDP, YELL, SEAG, TEAK, REDP)[i % 9]
        cv.rect(sx, 54, sx + 4, 63, [(30, 30, 30), (90, 90, 86), (170, 170, 160), (220, 220, 210)], 2.6)
        cv.rect(sx, 58, sx + 4, 63, jar, 3.4)
        cv.vline(sx + 1, 55, 62, [(170, 170, 160), (240, 240, 236)], 1.6)
        cv.hline(sx, sx + 4, 54, DARK, 1.6)
        cv.hline(sx + 1, sx + 3, 60, WHITEP, 4.4)
    hpipe(cv, x0 + 3, x1, 61, 0, TEAK, 4.0)
    porthole(cv, PORT[0], PORT[1], PORT[2], rim=4, seed=3)


def _forner_cos(cv):
    """El moble del marbre (el davant) i el marbre."""
    x0, x1 = 563, W - 1
    box(cv, x0, COUNTER_Y, x1 + 2, FLOOR_Y - 1, STEEL, 3.6, grad=0.8)
    box(cv, x0 + 5, COUNTER_Y + 10, x1 - 5, FLOOR_Y - 6, STEEL, 3.2)
    hpipe(cv, x0 + 14, x0 + 34, COUNTER_Y + 16, 0, STEEL, 5.6)
    MARBLE = [(40, 40, 42), (90, 90, 88), (150, 150, 146), (200, 200, 194), (230, 230, 226)]
    cv.rect(x0 - 3, COUNTER_Y - 5, x1, COUNTER_Y, MARBLE, lambda x, y: 3.4 + (0.5 if math.sin(x * 0.3 + y) > 0.9 else 0))
    cv.hline(x0 - 3, x1, COUNTER_Y - 5, MARBLE, 4.6)
    cv.hline(x0 - 3, x1, COUNTER_Y, MARBLE, 1.4)


def _forner_damunt(cv):
    """Damunt el marbre: la pasta, la farina, els pans a la reixa i el corró."""
    # la pasta, amb farina escampada i la marca dels dits
    cv.disc(587, COUNTER_Y - 9, 12, 5, FLOUR, lambda nx, ny: 3.4 - ny * 1.0 - nx * 0.4)
    for dx in (-4, 0, 4):
        cv.put(587 + dx, COUNTER_Y - 11, FLOUR, 1.8)
    for i in range(46):
        fx = 571 + int(hr(i, 3) * 54)
        fy = COUNTER_Y - 5 + int(hr(i, 4) * 4)
        cv.put(fx, fy, FLOUR, 4.4)
    # pans a refredar en una reixa
    cv.hline(605, 635, COUNTER_Y - 6, STEEL, 4.0)
    for rx in range(606, 635, 4):
        cv.put(rx, COUNTER_Y - 5, STEEL, 2.4)
    for bx in (612, 627):
        cv.disc(bx, COUNTER_Y - 11, 7, 5, BREAD, lambda nx, ny: 3.8 - ny * 1.4 - nx * 0.5)
        cv.line(bx - 3, COUNTER_Y - 14, bx + 2, COUNTER_Y - 15, BREAD, 5.2)
        cv.line(bx - 1, COUNTER_Y - 12, bx + 4, COUNTER_Y - 13, BREAD, 5.0)
    # el corró
    hpipe(cv, 571, 595, COUNTER_Y - 17, 2, TEAK, 4.4)
    for hx in (566, 600):
        hpipe(cv, hx, hx + 4, COUNTER_Y - 17, 1, TEAK, 3.6)


def _sac(cv):
    """El sac de farina, a terra."""
    # el sac de farina, a terra
    cv.poly([(603, FLOOR_Y + 5), (627, FLOOR_Y + 5), (624, FLOOR_Y - 24), (606, FLOOR_Y - 24)], FLOUR,
            lambda x, y: 3.0 - (x - 603) * 0.04)
    cv.hline(605, 625, FLOOR_Y - 24, FLOUR, 2.0)
    for gx in (608, 612, 616, 620):                                       # el lligat de dalt
        cv.put(gx, FLOOR_Y - 26, FLOUR, 2.6)
    text(cv, 'FARINA', 603, FLOOR_Y - 13, None, 0, flat=(110, 60, 30))


# ─── Les textures: el dibuix pla de sempre ───────────────────────────────────

def _paret(dia=False, safata=False):
    """Les dues parets planes, de cara (sense els fogons, l'armari, el forn ni el marbre, que són en 3D)."""
    cv = Canvas(light=TEX_LIGHT)
    PL.wall(cv)
    wear(cv, 0, 40, W - 1, 187, 27, seed=3, k=0.22)
    PL.door(cv)
    PL.dumbwaiter(cv)
    if safata:
        PL.tray(cv)
    PL.hatch(cv)
    PL.voice_tube(cv, 211, 101)
    _fogons_paret(cv)
    PL.cold_room(cv)
    _forner_paret(cv)
    if dia:
        day_porthole(cv, PORT[0], PORT[1], PORT[2], seed=3)
    return cv.img


@functools.lru_cache(maxsize=None)
def _paret_base():
    return _paret()


def _mobles(obert=False, forn=0.0, nomes_forn=False):
    """Els mobles plans, sobre transparent: el davant dels fogons, l'armari, el forn i el marbre."""
    cv = Canvas(light=TEX_LIGHT, transparent=True)
    PL._OVEN_K = forn
    try:
        PL.oven(cv)
    finally:
        PL._OVEN_K = 0.0
    if nomes_forn:
        return cv.img
    _fogons_cos(cv)
    PL.cupboard(cv)
    if obert:
        PL.cupboard_open(cv)
    _forner_cos(cv)
    return cv.img


@functools.lru_cache(maxsize=None)
def _mobles_base():
    return _mobles()


@functools.lru_cache(maxsize=None)
def _damunt():
    """El que va dret damunt els mobles: les olles, el que hi ha damunt l'armari, la pasta i els pans, i el sac."""
    cv = Canvas(light=TEX_LIGHT, transparent=True)
    _fogons_olles(cv)
    _forner_damunt(cv)
    _sac(cv)
    a = Canvas(light=TEX_LIGHT, transparent=True)
    PL.cupboard(a)
    cv.img.alpha_composite(a.img.crop((0, 0, W, PL.ARMARI[1] - 5)), (0, 0))
    return cv.img


FOG_TEX = (STOVE[0] - 4, TOP, STOVE[1] + 4, FLOOR_Y)
OLLES_TEX = (236, TOP - 37, 318, TOP)
ARM_TEX = (PL.ARMARI[0] - 3, PL.ARMARI[1] - 5, PL.ARMARI[2] + 3, FLOOR_Y)
ARM_DALT_TEX = (PL.ARMARI[0] - 2, PL.ARMARI[1] - 20, PL.ARMARI[2] + 2, PL.ARMARI[1] - 5)
FORN_TEX = (PL.FORN[0], PL.FORN[1], PL.FORN[2], FLOOR_Y)
MARB_TEX = (560, TOP, W, FLOOR_Y)
PASTA_TEX = (564, TOP - 20, W, TOP - 4)
SAC_TEX = (601, FLOOR_Y - 27, 629, FLOOR_Y + 6)


def _lampada():
    cv = Canvas(light=TEX_LIGHT, transparent=True)
    lamp(cv, 30, 10)
    return cv.img.crop((18, 5, 43, 20)), (12, 1)


# ─── Les superfícies ────────────────────────────────────────────────────────

def _planxa(lvl0, pw=96, seed=11):
    """Planxa pintada de crema (on el dibuix pla no arriba): quadernes amb reblons, en coordenades del món."""
    def L(s, t, P):
        val = lvl0 + (hr(int(s // 3), int(t // 5), seed) - 0.5) * 0.25 + (fbm(s / 40, t / 30, seed) - 0.5) * 0.5
        d = s % pw
        if d < 5:
            val += 0.9 if d < 1 else 0.5 if d < 2 else -0.6 if d >= 4 else 0.1
            if 2 <= d < 3 and int(t) % 14 == 0:
                val += 1.0
        if abs(t - 118) < 1:
            val -= 1.1
        return val
    return L


def _paret_proc(e, sid, P0, P1, P2, P3, seed):
    """Una paret procedural (planxa crema a dalt, el sòcol d'acer a baix), de P0 (dalt esq.) a P2 (baix dreta)."""
    k = (HW - 6) / HW

    def at(A, B):
        return tuple(A[i] + (B[i] - A[i]) * k for i in range(3))
    M3, M2 = at(P0, P3), at(P1, P2)
    e.quad(sid, P0, P1, M2, M3, ramp=CREAM, lvl=_planxa(4.4, seed=seed))
    e.quad(sid, M3, M2, P2, P3, ramp=STEEL, lvl=lambda s, t, P: 3.4 - t * 0.25 + (1.8 if t < 1 else 0))


def _terra(s, t, P):
    """Rajola de terrissa a escacs suaus, en coordenades del món: les juntes fugen i s'empetiteixen."""
    x, z = P[0], P[2]
    tile = 26
    gx, gz = math.floor(x / tile), math.floor(z / tile)
    v = 3.0 + (hr(int(x // 4), int(z // 4), 3) - 0.5) * 0.5 + (fbm(x / 70, z / 50, 6) - 0.5) * 0.6
    if (gx + gz) % 2:
        v += 0.25
    if x % tile < 1.1 or z % tile < 1.1:
        v -= 1.1
    v -= 0.4 * max(0.0, 1 - abs(z - 200) / 80) * max(0.0, 1 - abs(x - 200) / 200)
    return v


def _brillo(s, t):
    k = 0.0
    for lx, lz in LAMPS:
        d = math.hypot(s - lx, (ZW - t) - lz)
        k = max(k, 0.2 * max(0.0, 1 - d / 70) ** 1.5)
    return k


def escena(cv, tex, estat=frozenset()):
    """Tota la sala, de lluny a prop. `estat`: 'obert' (l'armari obert), 'dia'. → l'Escena (qui ha pintat què)."""
    e = Escena(cv, CAM, LLUMS, ambient=-0.5)
    zn = CAM.pos[2] + 60
    paret, mob, dam = tex['paret'], tex['mobles'], tex['damunt']
    # el sostre, baix i fosc
    e.quad('sostre', (0, HW, zn), (XR, HW, zn), (XR, HW, ZW), (0, HW, ZW), ramp=CREAM,
           lvl=lambda s, t, P: 2.2 + (fbm(s / 50, t / 40, 3) - 0.5) * 0.6, dues_cares=True)
    # les parets: la del menjador (x = 0) en escorç, la dels fogons al fons i la de la dreta
    _paret_proc(e, 'paret_esq_prop', (0, HW, zn), (0, HW, ZW - XL), (0, 0, ZW - XL), (0, 0, zn), 12)
    e.quad('paret_esq', (0, HW, ZW - XL), (0, HW, ZW), (0, 0, ZW), (0, 0, ZW - XL),
           tex=(paret, (0, PL.CEIL_H, XL, FLOOR_Y)))
    e.quad('paret_fons', (0, HW, ZW), (W - XL, HW, ZW), (W - XL, 0, ZW), (0, 0, ZW),
           tex=(paret, (XL, PL.CEIL_H, W, FLOOR_Y)))
    _paret_proc(e, 'paret_fons_dreta', (W - XL, HW, ZW), (XR, HW, ZW), (XR, 0, ZW), (W - XL, 0, ZW), 13)
    _paret_proc(e, 'paret_dreta', (XR, HW, ZW), (XR, HW, zn), (XR, 0, zn), (XR, 0, ZW), 14)
    # el terra, el reflex dels llums, la claror de la campana i la del forn
    e.quad('terra', (0, 0, ZW), (XR, 0, ZW), (XR, 0, zn), (0, 0, zn), ramp=QUARRY, lvl=_terra)
    e.claror((0, 0.3, ZW), (XR, 0.3, ZW), (XR, 0.3, zn), (0, 0.3, zn), (255, 214, 150), _brillo)
    fx = (FORN[0] + FORN[1]) / 2
    e.claror((fx - 70, 0.4, FORN[2]), (fx + 70, 0.4, FORN[2]), (fx + 70, 0.4, FORN[2] - 110),
             (fx - 70, 0.4, FORN[2] - 110), (255, 150, 60),
             lambda s, t: 0.3 * max(0.0, 1 - math.hypot(s - 70, t * 1.2) / 80))
    cx = (CFR[0] + CFR[1]) / 2
    e.claror((cx - 60, 0.4, ZW), (cx + 60, 0.4, ZW), (cx + 60, 0.4, ZW - 60), (cx - 60, 0.4, ZW - 60),
             (190, 220, 240), lambda s, t: 0.2 * max(0.0, 1 - math.hypot(s - 60, t * 1.6) / 64))
    # la catifa de goma davant els fogons
    f0, f1, fz, fh = FOG
    e.quad('catifa', (f0 + 4, 0.5, fz - 6), (f1 - 4, 0.5, fz - 6), (f1 - 4, 0.5, fz - 40), (f0 + 4, 0.5, fz - 40),
           ramp=CAB, lvl=lambda s, t, P: 1.6 + (0.8 if (int(s // 4) + int(t // 3)) % 2 else 0)
           - (1.0 if s < 1.5 or t < 1.5 else 0))
    # la foscor dels racons
    e.foscor('racons', (0, 0.5, ZW), (XR, 0.5, ZW), (XR, 0.5, zn), (0, 0.5, zn),
             lambda s, t: max(0.6 * max(0.0, 1 - t / 24), 0.5 * max(0.0, 1 - s / 22), 0.5 * max(0.0, 1 - (XR - s) / 22)))
    e.foscor('cantonada', (0, HW, ZW - 0.5), (50, HW, ZW - 0.5), (50, 0, ZW - 0.5), (0, 0, ZW - 0.5),
             lambda s, t: 0.45 * max(0.0, 1 - s / 50))
    e.foscor('cantonada2', (0.5, HW, ZW - 50), (0.5, HW, ZW), (0.5, 0, ZW), (0.5, 0, ZW - 50),
             lambda s, t: 0.45 * max(0.0, 1 - (50 - s) / 50))
    e.foscor('sostre_fosc', (0, HW - 0.5, ZW - 0.6), (XR, HW - 0.5, ZW - 0.6), (XR, 0, ZW - 0.6), (0, 0, ZW - 0.6),
             lambda s, t: 0.4 * max(0.0, 1 - t / 40))
    # les quadernes del sostre, que fugen, i les canonades
    for bx in (35, 131, 227, 323, 419):
        e.caixa('sostre', bx - 2, bx + 6, HW - 8, HW, 120, ZW, CREAM, 3.0,
                cares={'sota': {'ramp': CREAM, 'lvl': 2.4}, 'esquerra': {'ramp': CREAM, 'lvl': 3.4},
                       'dreta': {'ramp': CREAM, 'lvl': 1.6}})
    e.tub('canonades', (0, HW - 4, ZW - 5), (XR, HW - 4, ZW - 5), 3, REDP, 3.4, brides=96)
    # els fogons: el cos (el dibuix pla), el sobre, la barana de mar i les olles al damunt
    e.foscor('ombres', (f0 - 6, 0.6, ZW), (f1 + 6, 0.6, ZW), (f1 + 6, 0.6, fz - 14), (f0 - 6, 0.6, fz - 14),
             lambda s, t: 0.5 * min(1.0, max(0.0, (ZW - fz + 14 - t) / 14)))
    e.caixa('fogons', f0, f1, 0, fh, fz, ZW - 0.5, STEEL, 3.0,
            cares={'davant': {'tex': (mob, FOG_TEX)},
                   'dalt': {'ramp': STEEL, 'lvl': lambda s, t, P: 1.4 + (2.4 if any(abs(math.hypot(s - bx, t - 17) - 7) < 1
                                                                                  for bx in (18, 50, 82)) else 0)},
                   'dreta': {'ramp': STEEL, 'lvl': 2.4}})
    for xx in (f0 + 1, f1 - 1):
        e.caixa('fogons', xx - 1, xx + 1, fh, fh + 12, fz + 1, ZW - 2, STEEL, 4.4)
    e.caixa('fogons', f0 + 1, f1 - 1, fh + 11, fh + 13, fz + 1, fz + 3, STEEL, 5.0)
    e.sprite('olles', dam.crop(OLLES_TEX), (256 - OLLES_TEX[0], OLLES_TEX[3] - OLLES_TEX[1] - 1), (_w(256), fh, ZW - 17))
    # l'armari de les olles: separat un pam de la paret, amb el que hi ha damunt
    a0, a1, az, ah = ARM
    e.foscor('ombres', (a0 - 8, 0.6, ZW), (a1 + 8, 0.6, ZW), (a1 + 8, 0.6, az - 16), (a0 - 8, 0.6, az - 16),
             lambda s, t: 0.55 * min(1.0, max(0.0, (ZW - az + 16 - t) / 16)))
    e.caixa('armari', a0, a1, 0, ah + 5, az, ZW - 8, TEAK, 3.0,
            cares={'davant': {'tex': (mob, ARM_TEX)}, 'dalt': {'ramp': TEAK, 'lvl': 4.4},
                   'dreta': {'ramp': TEAK, 'lvl': lambda s, t, P: 2.2 - (0.6 if int(t) % 15 == 0 else 0)},
                   'esquerra': {'ramp': TEAK, 'lvl': 2.6}})
    if 'obert' in estat:                                         # la porta, oberta cap a la sala (en escorç)
        e.quad('armari', (a1 - 3, ah - 3, az), (a1 + 4, ah - 3, az - 50), (a1 + 4, 5, az - 50), (a1 - 3, 5, az),
               ramp=TEAK, dues_cares=True,
               lvl=lambda s, t, P: 3.0 - (1.0 if s < 2 or s > 48 or t < 2 else 0) + (1.4 if 38 < s < 44 and 50 < t < 62 else 0))
    e.sprite('armari', dam.crop(ARM_DALT_TEX), ((ARM_DALT_TEX[2] - ARM_DALT_TEX[0]) / 2, ARM_DALT_TEX[3] - ARM_DALT_TEX[1] - 1),
             ((a0 + a1) / 2, ah + 5, (az + ZW - 8) / 2))
    # el forn
    o0, o1, oz, oh = FORN
    e.foscor('ombres', (o0 - 6, 0.6, ZW), (o1 + 6, 0.6, ZW), (o1 + 6, 0.6, oz - 14), (o0 - 6, 0.6, oz - 14),
             lambda s, t: 0.5 * min(1.0, max(0.0, (ZW - oz + 14 - t) / 14)))
    e.caixa('forn', o0, o1, 0, oh, oz, ZW - 0.5, STEEL, 3.0,
            cares={'davant': {'tex': (mob, FORN_TEX)}, 'dalt': {'ramp': STEEL, 'lvl': 4.0},
                   'esquerra': {'ramp': STEEL, 'lvl': 2.6}, 'dreta': {'ramp': STEEL, 'lvl': 2.0}})
    # el marbre d'en Tomàs, amb la pasta i els pans al damunt, i el sac de farina a terra
    m0, m1, mz, mh = MARB
    e.foscor('ombres', (m0 - 6, 0.6, ZW), (m1 + 6, 0.6, ZW), (m1 + 6, 0.6, mz - 14), (m0 - 6, 0.6, mz - 14),
             lambda s, t: 0.5 * min(1.0, max(0.0, (ZW - mz + 14 - t) / 14)))
    MARBLE = [(40, 40, 42), (90, 90, 88), (150, 150, 146), (200, 200, 194), (230, 230, 226)]
    e.caixa('marbre', m0, m1, 0, mh, mz, ZW - 0.5, STEEL, 3.0,
            cares={'davant': {'tex': (mob, MARB_TEX)},
                   'dalt': {'ramp': MARBLE, 'lvl': lambda s, t, P: 3.4 + (0.6 if math.sin(s * 0.3 + t * 0.7) > 0.92 else 0)
                            + (0.6 if hr(int(s), int(t), 4) > 0.93 else 0)},
                   'esquerra': {'ramp': STEEL, 'lvl': 2.4}})
    e.sprite('marbre', dam.crop(PASTA_TEX), (0, PASTA_TEX[3] - PASTA_TEX[1] - 1), (m0 + 3, mh, mz + 10))
    e.foscor('ombres', (_w(600), 0.6, mz - 2), (_w(632), 0.6, mz - 2), (_w(632), 0.6, mz - 24), (_w(600), 0.6, mz - 24),
             lambda s, t: 0.6 * max(0.0, 1 - ((s - 16) / 16) ** 2 - ((t - 11) / 11) ** 2) * 1.5)
    e.sprite('sac', dam.crop(SAC_TEX), (615 - SAC_TEX[0], FLOOR_Y + 5 - SAC_TEX[1]), (_w(615), 0, mz - 12))
    # el taulell de treball del mig, d'acer i girat: la post de tallar, el ganivet, un bol i unes cebes
    ix, iz, iw, idp, ih, ia = ILLA
    e.foscor('ombra_illa', (ix - 64, 0.7, iz + 40), (ix + 64, 0.7, iz + 40), (ix + 64, 0.7, iz - 40),
             (ix - 64, 0.7, iz - 40), lambda s, t: 0.6 * max(0.0, 1 - ((s - 64) / 58) ** 2 - ((t - 40) / 30) ** 2) * 1.5)
    c, s_ = math.cos(ia), math.sin(ia)

    def Pi(lx, lz):
        return ix + lx * c - lz * s_, iz + lx * s_ + lz * c
    for lx, lz in ((-iw / 2 + 4, -idp / 2 + 4), (iw / 2 - 4, -idp / 2 + 4), (iw / 2 - 4, idp / 2 - 4), (-iw / 2 + 4, idp / 2 - 4)):
        px_, pz_ = Pi(lx, lz)
        e.caixa_girada('illa', px_, pz_, 3, 3, ih - 3, ia, STEEL, 3.4)
    e.caixa_girada('illa', ix, iz, iw - 6, idp - 6, 2, ia, STEEL, 2.6, y0=14,
                   cares={'dalt': {'ramp': STEEL, 'lvl': lambda s, t, P: 2.2 + (1.4 if int(s) % 9 < 1 else 0)}})
    e.caixa_girada('illa', ix, iz, iw, idp, 3, ia, STEEL, 3.4, y0=ih - 3,
                   cares={'dalt': {'ramp': STEEL, 'lvl': lambda s, t, P: 4.4 + (fbm(s / 20, t / 10, 2) - 0.5) * 0.8
                                   - (1.2 if s < 1.5 or t < 1.5 else 0)},
                          'davant': {'ramp': STEEL, 'lvl': 4.8}, 'dreta': {'ramp': STEEL, 'lvl': 3.4}})
    bx_, bz_ = Pi(-18, -4)
    e.caixa_girada('illa', bx_, bz_, 34, 22, 2, ia + 0.1, TEAK, 4.4, y0=ih,
                   cares={'dalt': {'ramp': TEAK, 'lvl': lambda s, t, P: 4.6 - (0.6 if int(s * 2) % 7 == 0 else 0)}})
    kx_, kz_ = Pi(-12, -2)
    e.caixa_girada('illa', kx_, kz_, 18, 2.4, 1, ia + 0.4, STEEL, 6.0, y0=ih + 2)
    for k, (lx, lz) in enumerate(((-26, 4), (-22, -8))):
        ox_, oz_ = Pi(lx, lz)
        e.caixa_girada('illa', ox_, oz_, 5, 5, 4, ia + k, COPPERP, 4.4, y0=ih + 2)
    wx_, wz_ = Pi(24, 2)
    e.caixa_girada('illa', wx_, wz_, 20, 20, 8, ia, WHITEP, 3.6, y0=ih,
                   cares={'dalt': {'ramp': WHITEP, 'lvl': lambda s, t, P: 1.6 if 3 < s < 17 and 3 < t < 17 else 4.6}})
    # els llums del sostre
    img, peu = _lampada()
    for lx, lz in LAMPS:
        e.sprite('llums', img, peu, (lx, HW, lz), escala_img=1.3)
    # primer pla: sacs i caixes en silueta a baix a l'esquerra, la canonada del sostre i un pilar de quaderna
    e.tub('primer_pla', (-60, HW - 6, -70), (XR + 60, HW - 6, -70), 9, FOSC, 2.4, brides=110)
    e.caixa_girada('primer_pla', 70, -70, 70, 50, 40, 0.3, FOSC, 1.6,
                   cares={'dalt': {'ramp': FOSC, 'lvl': lambda s, t, P: 3.0 - (1.2 if abs(s - 32) < 2 else 0)},
                          'davant': {'ramp': FOSC, 'lvl': 1.4}, 'dreta': {'ramp': FOSC, 'lvl': 2.2}})
    e.roca('primer_pla', (150, 0, -60), 30, FOSC, lvl=2.4, llum_dir=(-0.6, -0.6), aplana=0.55, seed=3)    # un sac
    e.caixa('primer_pla', 434, 452, 0, HW, 30, 46, FOSC, 2.0,
            cares={'esquerra': {'ramp': FOSC, 'lvl': lambda s, t, P: 2.8 - (1.4 if s < 2 else 0)
                                + (1.6 if int(t) % 14 < 2 and 6 < s < 14 else 0)},
                   'davant': {'ramp': FOSC, 'lvl': 1.2}})
    return e


# ─── Composició ─────────────────────────────────────────────────────────────

@functools.lru_cache(maxsize=None)
def _textures():
    return {'paret': _paret_base(), 'mobles': _mobles_base(), 'damunt': _damunt()}


def _proj(P):
    u, v, _ = CAM.projecta(P)
    return u, v


def _brills(cv):
    for lx, lz in LAMPS:
        u, v = _proj((lx, HW - 10, lz))
        k = CAM.escala((lx, HW, lz))
        glow(cv, round(u), round(v), round(40 * k), (255, 214, 140), 0.32)
        glow(cv, round(u), round(v), round(12 * k), (255, 240, 200), 0.5)
    u, v = _proj(((FOG[0] + FOG[1]) / 2, 106, ZW - 20))                # el llum de la campana
    glow(cv, round(u), round(v), 20, (255, 236, 190), 0.3)


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
    """La safata a la cabina del muntacàrregues i el pilot verd (projectats per la paret)."""
    _, e = _base()
    cv.img.alpha_composite(_fotograma([e.capa(_paret(safata=True), {'paret_esq'})]))
    cv.P = cv.img.load()


def armari_obert(cv):
    """L'armari obert: a dins, fosc, amb les olles, i la porta oberta cap a la sala."""
    tex = {**_textures(), 'mobles': _mobles(obert=True)}
    img, _ = _render(frozenset({'obert'}), tex)
    cv.img.alpha_composite(_diff(img, _base()[0]))
    cv.P = cv.img.load()


def ulls_dia(cv):
    """Escenes 2 i 3, de dia: l'ull de bou, clar."""
    _, e = _base()
    cv.img.alpha_composite(_fotograma([e.capa(_paret(dia=True), {'paret_fons'})]))
    cv.P = cv.img.load()


PROPS = {'safata': safata, 'armari_obert': armari_obert, 'ulls_dia': ulls_dia}


# ─── Animacions ─────────────────────────────────────────────────────────────

def _bufades(img, punts):
    """Pinta bufades (vapor, boira) a punts del món: [(P, color, alfa, ample en unitats)]."""
    P = img.load()
    for Pw, col, a, amp in punts:
        u, v, _ = CAM.projecta(Pw)
        k = CAM.escala(Pw)
        r = max(1, round(amp * k / 2))
        for dx in range(-r, r + 1):
            for dy in (0, -1):
                xx, yy = round(u) + dx, round(v) + dy
                if 0 <= xx < W and 0 <= yy <= BOTTOM:
                    kk = (1.0 - abs(dx) / (r + 1) * 0.6) * (1.0 if dy == 0 else 0.55)
                    o = P[xx, yy]
                    P[xx, yy] = mix(o[:3], col, min(1.0, a * kk)) + (255,)


def _frames_vapor():
    """El vapor de l'olla gran puja cap a la campana (cada fil torna a sortir quan s'esvaeix)."""
    base = _base()[0]
    ox, lid, z = _w(256), FOG[3] + 36, ZW - 17
    n, wisps = 48, 30
    out = []
    for i in range(n):
        img = base.copy()
        t = i / n
        pts = []
        for p in range(wisps):
            age = (t * 2 + p / wisps) % 1
            x = ox - 4 + (hr(p, 1) - 0.5) * 11 + 3 * math.sin(age * 8 + p * 2.1)
            pts.append(((x, lid + 1 + age * 34, z + (hr(p, 2) - 0.5) * 6), (255, 255, 255),
                        0.9 * (1 - age) * min(1.0, age * 5), 2 + age * 3))
        _bufades(img, pts)
        out.append(_diff(img, base))
    return out


def _frames_forn():
    """El forn encès: la llum de dins tremola una mica."""
    _, e = _base()
    return [_fotograma([e.capa(_mobles(forn=k, nomes_forn=True), {'forn'})])
            for k in (0.0, 0.2, 0.1, 0.3, 0.15, -0.1, 0.05, 0.25, 0.1, -0.05)]


def _frames_fred():
    """Boira freda que s'escapa per sota la porta de la cambra i s'arrossega per terra, cap endavant."""
    base = _base()[0]
    x0, x1 = CFR[0] + 6, CFR[1] - 6
    n, wisps = 48, 34
    out = []
    for i in range(n):
        img = base.copy()
        t = i / n
        pts = []
        for p in range(wisps):
            age = (t + p / wisps) % 1
            sx = x0 + hr(p, 3) * (x1 - x0)
            side = 1 if hr(p, 4) > 0.5 else -1
            x = sx + side * age * 18 + math.sin(age * 6 + p) * 2
            pts.append(((x, 1.0, ZW - 2 - age * 34), (214, 232, 244), 0.8 * (1 - age) * min(1.0, age * 6), 6 + age * 4))
        _bufades(img, pts)
        out.append(_diff(img, base))
    return out


ANIMS = {'vapor': {'frames': _frames_vapor, 'frameDuration': 100},
         'forn': {'frames': _frames_forn, 'frameDuration': 150},
         'fred': {'frames': _frames_fred, 'frameDuration': 110}}


def _amo(ids):
    def mask(x, y):
        _, e = _base()
        return e.ids[e.amo[y * e.cv.w + x]] in ids
    return mask


def _p(x, z, y=0.0):
    u, v, _ = CAM.projecta((x, y, z))
    return round(u), round(v)


# Capes del davant: el taulell del mig (s'hi passa per darrere) i el primer pla (sempre davant).
FRONT = [
    {'id': 'davant_illa', 'mask': _amo({'illa'}), 'baseline': _p(ILLA[0], ILLA[1])[1], 'zIndex': 20, 'variants': ('ulls_dia', 'armari_obert')},
    {'id': 'davant_primer_pla', 'mask': _amo({'primer_pla'}), 'baseline': 999, 'zIndex': 20, 'variants': ('ulls_dia', 'armari_obert')},
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
        if CAM.projecta((260, 0, z))[1] > v:
            lo = z
        else:
            hi = z
    return CAM.escala((260, 0, (lo + hi) / 2))


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


# El terra on es camina (al món): davant els mobles del fons, fins a les portes de l'esquerra; el taulell del mig, un
# forat (s'hi fa la volta).
WALK_MON = [(14, 20), (14, 292), (FOG[0] + 2, 292), (FOG[0] + 2, FOG[2] - 6), (CFR[0] + 2, FOG[2] - 6),
            (CFR[0] + 2, 292), (CFR[1] - 2, 292), (CFR[1] - 2, ARM[2] - 8), (ARM[1] + 6, ARM[2] - 8),
            (ARM[1] + 6, FORN[2] - 6), (MARB[0], FORN[2] - 6), (MARB[0], MARB[2] - 6), (450, MARB[2] - 6), (450, 20)]
ESCALA_MAX = 1.2
_WALK = _talla([_p(x, z) for x, z in WALK_MON], _v_escala(ESCALA_MAX))
_V_FONS, _V_PROP = min(v for _, v in _WALK), max(v for _, v in _WALK)
_c, _s = math.cos(ILLA[5]), math.sin(ILLA[5])
_FORAT = [_p(ILLA[0] + lx * _c - lz * _s, ILLA[1] + lx * _s + lz * _c)
          for lx, lz in ((-ILLA[2] / 2 - 4, -ILLA[3] / 2 - 2), (ILLA[2] / 2 + 4, -ILLA[3] / 2 - 2),
                         (ILLA[2] / 2 + 4, ILLA[3] / 2 + 2), (-ILLA[2] / 2 - 4, ILLA[3] / 2 + 2))]
_ILLA_PTS = [(ILLA[0] + lx * _c - lz * _s, y, ILLA[1] + lx * _s + lz * _c)
             for lx in (-ILLA[2] / 2, ILLA[2] / 2) for lz in (-ILLA[3] / 2, ILLA[3] / 2) for y in (0, ILLA[4])]

GEOMETRIA = {
    'things': {
        'porta': {'rect': _rect_mon((0, D_PORTA[2], D_PORTA[0]), (0, 0, D_PORTA[1])), 'walk': _p(30, (D_PORTA[0] + D_PORTA[1]) / 2)},
        'munta': {'rect': _rect_mon((0, MUNTA[3], MUNTA[0]), (0, MUNTA[2], MUNTA[1])), 'walk': _p(34, (MUNTA[0] + MUNTA[1]) / 2)},
        'safata': {'rect': _rect_mon((0, CAB_IN[2] + 22, CAB_IN[0]), (0, CAB_IN[2], CAB_IN[1])),
                   'walk': _p(34, (MUNTA[0] + MUNTA[1]) / 2)},
        'boca': {'rect': _rect_mon((0, BOCA[3], BOCA[0]), (0, BOCA[2], BOCA[1])), 'walk': _p(30, 270)},
        'cambra_freda': {'rect': _rect_mon((CFR[0], CFR[2], ZW), (CFR[1], 0, ZW)), 'walk': _p((CFR[0] + CFR[1]) / 2, 280)},
        'armari': {'rect': _rect_mon(*[(x, y, z) for x in (ARM[0], ARM[1]) for z in (ARM[2], ZW - 8)
                                       for y in (0, ARM[3] + 20)]), 'walk': _p((ARM[0] + ARM[1]) / 2, ARM[2] - 14)},
        'forn': {'rect': _rect_mon((FORN[0], FORN[3], FORN[2]), (FORN[1], 0, FORN[2])),
                 'walk': _p((FORN[0] + FORN[1]) / 2, FORN[2] - 14)},
    },
    'spawns': {'iri': _p(330, 145), 'vet': _p(60, 150), 'tomas': _p(MARB[0] + 40, MARB[2] - 16),
               'nadia': _p(CFR[1] - 10, 230)},
    'walkable': _WALK,
    'forats': [_FORAT],
    'floorSquash': 0.4,
    # L'ombra de contacte: la llum dominant són els llums del sostre (el del mig); curta.
    'characterShadow': {'enabled': True, 'color': '#120a06', 'alpha': 0.42, 'squash': 0.4, 'core': 0.6,
                        'light': {'x': _p(250, 200)[0], 'y': _p(250, 200)[1], 'stretch': 0.5, 'reach': 160}},
    'regions': [{'id': 'perspectiva', 'active': True, 'scaleEnabled': True, 'scaleWalkSpeed': True,
                 'scaleTop': round(_escala_a(_V_FONS - 2), 3), 'scaleBottom': round(_escala_a(_V_PROP + 2), 3),
                 'points': [(0, _V_FONS - 2), (W - 1, _V_FONS - 2), (W - 1, _V_PROP + 2), (0, _V_PROP + 2)]}],
    'characterLights': {
        'ambient': '#a89880',
        'lights': [
            *[{'x': _p(x, z, HW - 14)[0], 'y': _p(x, z, HW - 14)[1], 'radius': 200, 'color': '#ffd28c',
               'intensity': 0.7} for x, z in LAMPS],
            {'x': _p((FORN[0] + FORN[1]) / 2, FORN[2], 40)[0], 'y': _p((FORN[0] + FORN[1]) / 2, FORN[2], 40)[1],
             'radius': 110, 'color': '#ff9640', 'intensity': 0.6},
            {'x': _p((CFR[0] + CFR[1]) / 2, ZW, 40)[0], 'y': _p((CFR[0] + CFR[1]) / 2, ZW, 40)[1],
             'radius': 90, 'color': '#bedcf0', 'intensity': 0.4},
        ],
    },
}
