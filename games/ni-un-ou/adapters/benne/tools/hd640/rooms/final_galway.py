"""
Els finals (cinemàtica): la terrassa d'un bar del port de Galway a trenc d'alba. EN 3D (hd640/tres_d.py), a 1×.
El dibuix pla de sempre és a final_galway_pla_comu.py (en surten la tele i el seu noticiari, el tendal, la tetera
i els scones, i la gavina).

La càmera és a la terrassa, a l'altura d'una persona alta, sense mirar avall, i girada cap a la dreta: la barana, el
moll i l'Arenga fugen en diagonal cap a la dreta, i el sol que surt a l'esquerra, darrere el far, fa un camí de llum
per l'aigua fins al moll. Contrast d'escala: la tele, el pal del tendal i el test de bruc, grossos i a prop, a
l'esquerra; l'Arenga, amarrada en 3/4 (el costat, el mirall de popa i la superestructura amb les seves cares) a la
dreta; el far i la barqueta, petits, a l'horitzó de l'esquerra.
  - primer pla: el tendal vist des de sota (les ratlles fugen) amb els festons a contrallum, el pal de l'esquerra, el
    test de bruc a la cantonada de baix i una cadira de bistrot buida a baix a la dreta, tots foscos;
  - la taula llarga (dues taules ajuntades, una mica girades l'una respecte de l'altra) en diagonal, amb les tasses,
    la tetera, els scones, el diari i el sucrer; darrere, les cadires de vímet on seu la colla; les ombres de la
    taula i de les cadires, llargues, cap a la dreta i cap a nosaltres (el sol és baix, a l'esquerra);
  - la barana de ferro amb volutes, el moll de carreus amb les bites, els caps d'amarratge, el fanal encara encès,
    unes nanses i la gavina.
Props: `tele_apagada`. ANIMS: `tele`, `badia`, `vapor`. FRONT: la taula tapa les cames de qui seu al darrere (el
sobre en queda fora: en Diu s'hi enfila). Ningú no camina: els spawns són on seu o és cadascú.
"""
import hd640  # noqa: F401  (abans que cap hd.rooms: posa la llibreria a 640×360)

import functools
import math

from hd.pix import Light, Canvas, W, H, hr, mix, IRON
from hd.rooms.comu import _diff
from hd.rooms.exterior import arenga, fbm, smooth, sheer, STEELX, ROPE, HULLN, REDH
from hd640.rooms import final_galway_pla_comu as PL
from hd640.rooms.final_galway_pla_comu import (DAWN, SHORE, STONE, WOOD, AWN, CREAM, TABLER, CUPR, HEATHER, LEAF,
                                               GOLDLIT)
from hd640.tres_d import Camera, Escena, Llum

# ─── La càmera i el món ─────────────────────────────────────────────────────
# x a la dreta, y amunt, z cap al fons; 1 unitat ≈ 1,55 cm (una persona, 110). El terra de la terrassa és y = 0.
YAW = 0.30
_D, _LAT = 400.0, 10.0                      # el centre de la taula: a 475 de la càmera, una mica a la dreta
CAM = Camera(pos=(-(_D * math.sin(YAW) + _LAT * math.cos(YAW)), 125,
                  -(_D * math.cos(YAW) - _LAT * math.sin(YAW))), yaw=YAW, pitch=0.0, f=420, centre=(320, 128))
HOR = 128                                   # (pitch 0: l'horitzó és la y del centre)
LIGHT = Light(ambient=0.0, vignette=None, floor_fade=None)

U = 65.0                                    # unitats per metre
RAIL_Z, RAIL_H, RAIL_X = 170.0, 70.0, (-1400.0, 960.0)
QUAY_Y, QUAY_Z = -30.0, 1370.0               # el moll: més baix que la terrassa; la vora
SEA_Y = -130.0
SHIP_X, SHIP_Z = 120.0, 1405.0               # la popa (m = 0) i el costat de l'Arenga que mira cap a nosaltres
BEAM = 4.2                                  # mitja mànega (m)
AW_Y, AW_Z = 262.0, 90.0                    # el tendal: alçada i la vora dels festons
TAULA_H, TAULA_Z = 48.0, (-46.0, -10.0)     # la taula llarga: alçada i fondària (z del davant i del darrere)
TAULES = ((-150.0, 0.0, 0.025), (0.0, 150.0, -0.02))   # x0, x1 i el gir de cadascuna
SEU_Z = 8.0                                 # on són els peus de qui seu darrere la taula
SEIENTS = {'capitana': -122.0, 'nadia': -62.0, 'marcel': -2.0, 'tomas': 58.0}
IRI, VET = (-167.0, -6.0), (178.0, -92.0)
DIU = (116.0, -28.0)                        # en Diu, dret damunt la taula, a la punta de la dreta (ningú al darrere)
TV_C, TV_W, TV_H, TV_D = (-202.0, 174.0, 43.0), 76.0, 49.0, 12.0
TV_ANG = 0.32                               # la tele, girada cap a la colla (i cap a nosaltres)
SUN = (150, HOR - 3)                        # el sol que surt (en pantalla), darrere el far

LLUMS = [Llum((-60000.0, 2600.0, 60000.0), 1e7, 1.5, power=1.0),     # el sol, baix, a l'esquerra i al fons
         Llum((-520.0, 150.0, -760.0), 1000.0, 1.3, power=1.2),      # la finestra del bar, darrere nostre
         Llum((TV_C[0] + 20, TV_C[1] - 10, TV_C[2] + 20), 130.0, 0.7, power=1.8)]   # la tele
AMBIENT = -0.6


def _p(x, z, y=0.0):
    u, v, _ = CAM.projecta((x, y, z))
    return round(u), round(v)


def _escala_a(v):
    """L'escala d'un personatge amb els peus a la y `v` de pantalla, al terra de la terrassa (pitch 0: exacta)."""
    return (v - HOR) / CAM.pos[1]


# ─── El cel, la riba i el sol (en pantalla: és tot molt lluny) ─────────────────

def _cel(cv):
    K = 4 / 3
    for y in range(0, HOR + 1):
        t = y / HOR
        v = y / K
        for x in range(W):
            u = x / K
            sol = max(0.0, 1 - math.hypot((x - SUN[0]) / 260, (y - SUN[1]) / 90))
            lvl = 0.6 + 8.0 * t ** 1.7 + 2.2 * sol ** 2
            c = fbm(u / 90, v / 10, 51)
            k = smooth(0.58, 0.72, c) * (0.3 + 0.7 * smooth(0.1, 0.6, t))
            if k > 0:
                up = fbm(u / 90, (v + 1.5) / 10, 51)
                under = max(0.0, smooth(0.58, 0.72, c) - smooth(0.58, 0.72, up))   # la vora de sota: el sol de cara
                body = 2.6 + 3.0 * t + (4.2 + 3 * sol) * under + (fbm(u / 12, v / 4, 59) - 0.5) * 0.6
                lvl = lvl * (1 - k) + body * k
            cv.put(x, y, DAWN, lvl, lit=0)
    # la lluna, que se'n va, a ponent (a la dreta, alta, mig tapada pel tendal)
    mx, my = 520, 26
    cv.disc(mx, my, 4, 4, [(150, 152, 176), (180, 182, 200), (210, 210, 220), (234, 232, 236)],
            lambda nx, ny: 2.6 - nx * 1.2 - ny * 0.3, lit=0)
    cv.flat(mx - 1, my - 1, (176, 178, 196))
    cv.glow(mx, my, 10, (200, 200, 220), 0.2)
    # el sol que surt: el disc mig amagat darrere els turons, i el halo
    cv.glow(SUN[0], SUN[1], 70, (255, 210, 160), 0.45)
    cv.disc(SUN[0], SUN[1], 7, 7, [(255, 226, 170), (255, 240, 206), (255, 250, 236)],
            lambda nx, ny: 2.0 - ny, lit=0)
    cv.glow(SUN[0], SUN[1], 22, (255, 236, 200), 0.6)


def _turons(cv):
    """L'altra riba de la badia: turons baixos, amb els cims tocats de rosa, cases blanques i el far."""
    K = 4 / 3
    for x in range(W):
        u = x / K
        alt = (3 + 6 * fbm(u / 60, 0.5, 52) + 3 * fbm(u / 18, 1.5, 53)) * K
        alt *= 0.45 + 0.55 * smooth(40, 260, abs(x - SUN[0]))      # davant el sol, més baixos: el sol hi treu el cap
        top = HOR - alt
        for y in range(int(top), HOR + 1):
            lvl = 2.2 - (y - top) * 0.06 + (1.6 if y - top < 1.5 else 0)
            lvl += 1.2 * max(0.0, 1 - abs(x - SUN[0]) / 120)      # a contrallum, la boira s'encén
            if (y - top) > 3 and hr(x // 3, y // 2, 60) > 0.93:
                lvl += 0.6
            cv.put(x, y, SHORE, lvl, lit=0)
    for i, hx in enumerate((34, 46, 232, 246, 262, 300)):
        hy = HOR - 1
        cv.rect(hx, hy - 3, hx + 4, hy, SHORE, 4.0, lit=0)
        cv.poly([(hx - 1, hy - 3), (hx + 2, hy - 5), (hx + 5, hy - 3)], SHORE, 1.4, lit=0)
        if hr(i, 61) > 0.5:
            cv.flat(hx + 2, hy - 1, (255, 214, 140))
    # el far, a la punta de l'esquerra: torre blanca a contrallum, el llum encara encès i el feix que s'esvaeix
    fx, fy = 92, HOR - 15
    cv.rect(fx - 1, fy, fx + 1, HOR - 1, CREAM, lambda x, y: 3.0 - (x - fx + 1) * 0.6, lit=0)
    cv.hline(fx - 1, fx + 1, fy + 5, [(110, 30, 30), (160, 50, 44)], 1.0, lit=0)
    cv.rect(fx - 1, fy - 2, fx + 1, fy - 1, [(255, 230, 170)], 0, lit=0)
    cv.flat(fx, fy - 3, (40, 30, 30))
    cv.glow(fx, fy - 1, 5, (255, 220, 160), 0.6)
    for i in range(28):
        x = fx + 3 + i
        if hr(x, fy, 62) < 0.5 * (1 - i / 28):
            cv.flat(x, fy - 1, mix(cv.get(x, fy - 1)[:3], (255, 230, 180), 0.35))


def _barqueta(cv):
    """Una barqueta de pesca, lluny, a la badia de l'esquerra (a contrallum, gairebé negra)."""
    bx, by = 196, HOR + 7
    DK = [(30, 26, 44), (46, 40, 60), (70, 62, 84), (110, 96, 116)]
    cv.poly([(bx - 1, by - 2), (bx + 13, by - 2), (bx + 11, by + 1), (bx + 1, by + 1)], DK, 1.4, lit=0)
    cv.rect(bx + 4, by - 6, bx + 7, by - 3, DK, 1.0, lit=0)
    cv.vline(bx + 9, by - 12, by - 3, DK, 1.6, lit=0)
    cv.flat(bx + 9, by - 13, (255, 236, 200))
    for k in range(3):
        cv.hline(bx + k, bx + 12 - k, by + 2 + k, DK, 2.4 - k * 0.6, lit=0)


# ─── L'aigua de la badia (al món) ─────────────────────────────────────────────

_FASE = [0.0]


def _aigua(s, t, P):
    x, z = P[0], P[2]
    u, v, _ = CAM.projecta(P)
    d = max(0.0, v - HOR)
    row = max(0.0, HOR - d * 1.6)                                  # el reflex del cel
    lvl = 0.6 + 8.0 * (row / HOR) ** 1.7 - 1.0
    n = fbm(x / (90 + z * 0.02) + _FASE[0], z / 30, 54)
    lvl += (n - 0.5) * 2.4 * (0.5 + 0.5 * smooth(0, 40, d))
    # el camí de llum del sol: més ample com més a prop, trencat per les ones
    w = 6 + d * 2.2
    k = max(0.0, 1 - abs(u - SUN[0] - (v - HOR) * 0.25) / w)
    if k > 0:
        g = fbm(x / 40 + _FASE[0] * 1.7, z / 14, 55)
        lvl += k * (3.4 if g > 0.52 else 1.0) * (1 - smooth(20, 80, d) * 0.6)
    return lvl


# ─── Textures ─────────────────────────────────────────────────────────────────

S_ARENGA = 20                                                # píxels per metre del perfil pla
_AX, _AY = 40, 380                                           # popa i flotació al dibuix pla


@functools.lru_cache(maxsize=None)
def _perfil():
    """L'Arenga de perfil (el dibuix de sempre, sense res al voltant), font de les cares del costat."""
    cv = Canvas(w=_AX * 2 + int(41 * S_ARENGA), h=_AY + 2, transparent=True)
    arenga(cv, _AX, _AY, S_ARENGA, 'dawn', facing=1, crane=False, zodiac=False)
    return cv.img


def _pr(m0, h1, m1, h0):
    """Un retall del perfil: de m0 a m1 (m de la popa) i de h0 a h1 (m sobre la flotació)."""
    return (_AX + m0 * S_ARENGA, _AY - h1 * S_ARENGA, _AX + m1 * S_ARENGA, _AY - h0 * S_ARENGA)


@functools.lru_cache(maxsize=None)
def _pla():
    """El dibuix pla de la terrassa (a 1×), per retallar-ne la tetera, els scones i la gavina."""
    cv = Canvas(light=PL.LIGHT, transparent=True)
    PL.table(cv)
    cv2 = Canvas(light=PL.LIGHT, transparent=True)
    PL.quay(cv2)
    return cv.img, cv2.img


def _tele(frame=0, apagada=False):
    cv = Canvas(light=PL.LIGHT)
    PL.tv_frame(cv)
    PL.tv_news(cv, frame)
    if apagada:
        PL.tele_apagada(cv)
    return cv.img


TV_CROP = (PL.TV[0], PL.TV[1], PL.TV[2] + 1, PL.TV[3] + 1)


@functools.lru_cache(maxsize=None)
def _lona(w, h, festons):
    """La lona del tendal (1 px = 1 unitat): ratlles verdes i crema de 42; amb `festons`, la vora retallada."""
    cv = Canvas(w + 1, h + 1, transparent=True)
    sw = 42
    for x in range(w + 1):
        stripe = (x // sw) % 2
        R = AWN if stripe else CREAM
        u = (x % sw) / sw
        bot = h - 7 + int(7 * math.sin(u * math.pi)) if festons else h
        for y in range(0, bot + 1):
            lvl = 2.6 - (y / max(1, h)) * 0.6 + (0 if stripe else 0.6) + (0.5 if x % sw == 0 else 0)
            if festons and y >= bot - 1:
                lvl -= 1.2
            cv.put(x, y, R, lvl, lit=0)
        if festons and x % 3 == 0:                                   # el serrell
            cv.put(x, bot + 1, R, 1.0 + (0 if stripe else 0.6), lit=0)
    return cv.img


@functools.lru_cache(maxsize=None)
def _barana(w):
    """La barana de ferro (1 px = 1 unitat, RAIL_H d'alt): passamà, sòcol, barrots i una voluta de cada tres."""
    h = int(RAIL_H)
    cv = Canvas(w + 1, h + 1, transparent=True)
    cv.rect(0, 0, w, 5, IRON, 3.2, lit=0)
    cv.hline(0, w, 0, IRON, 5.0, lit=0)
    cv.hline(0, w, 5, IRON, 1.4, lit=0)
    cv.rect(0, h - 7, w, h - 3, IRON, 2.4, lit=0)
    cv.hline(0, w, h - 7, IRON, 3.6, lit=0)
    for x in range(6, w, 22):
        cv.rect(x, 6, x + 1, h - 7, IRON, 2.6, lit=0)
        cv.vline(x, 6, h - 7, IRON, 3.4, lit=0)
    for x in range(17, w - 12, 66):
        cy = 26
        for a in range(0, 340, 8):
            r = 3 + a / 60
            for dr in (0, 0.8):
                cv.put(x + 3 + round(math.cos(math.radians(a)) * (r + dr)),
                       cy + round(math.sin(math.radians(a)) * (r + dr) * 1.2), IRON, 3.0, lit=0)
    return cv.img


# ─── L'escena ────────────────────────────────────────────────────────────────

def _sh(m, h, w=-BEAM):
    """Un punt de l'Arenga (m de la popa, h sobre la flotació, w de través; tot en metres) al món."""
    return (SHIP_X + m * U, SEA_Y + h * U, SHIP_Z + (w + BEAM) * U)


def _arenga(e):
    img = _perfil()
    TOP = 5.1
    # el costat del buc (fins a 33 m) i l'amura (de 33 m a la roda, que es tanca cap al mig)
    e.quad('vaixell', _sh(0, TOP), _sh(33, TOP), _sh(33, -1), _sh(0, -1), tex=(img, _pr(0, TOP, 33, -1)),
           forma=lambda s, t: TOP - t / U <= sheer(s / U) + 0.02)
    e.quad('vaixell', _sh(33, TOP), _sh(40.9, TOP, 0), _sh(40.9, -1, 0), _sh(33, -1), tex=(img, _pr(33, TOP, 40.9, -1)),
           forma=lambda s, t: TOP - t / U <= sheer(33 + s / U * 7.9 / math.hypot(7.9, BEAM)) + 0.12)
    # el mirall de popa (es veu de biaix: la càmera és més a l'esquerra que la popa), amb el nom
    e.quad('popa', _sh(0, 3.4, BEAM), _sh(0, 3.4), _sh(0, -1), _sh(0, -1, BEAM), ramp=HULLN,
           lvl=lambda s, t, P: (6.0 if t < 0.35 * U else 5.0) - (2.4 if t > 2.9 * U else 0) +
           (1.4 if 0.6 * U < t < 1.1 * U else 0) * (1 if 0.12 < (s / U) % 1.0 < 0.8 and 1.2 < s / U < 7.2 else 0))
    e.quad('popa', _sh(0, 2.95, BEAM), _sh(0, 2.95), _sh(0, 2.45), _sh(0, 2.45, BEAM), ramp=REDH, lvl=4.6)
    # la coberta (es veu de molt arran: una llenca entre la regala de prop i la de lluny)
    e.quad('vaixell', _sh(0, 3.35, BEAM), _sh(40, 3.35 + 1.6, 0.3), _sh(40, 3.35 + 1.6, -0.3), _sh(0, 3.35),
           ramp=STEELX, lvl=lambda s, t, P: 5.0 + (0.6 if int(s / 40) % 2 else 0))
    # la superestructura: la caseta, el pont i la xemeneia, amb les cares de popa i de dalt
    for m0, m1, h0, h1, w, crop in ((13, 31.5, 3.3, 6.15, 3.0, _pr(13, 6.15, 31.5, 3.3)),
                                    (20.6, 31.4, 6.1, 8.85, 2.4, _pr(20.6, 8.85, 31.4, 6.1)),
                                    (16.2, 19.6, 6.1, 9.6, 1.0, _pr(16.2, 9.6, 19.6, 6.1))):
        e.quad('vaixell', _sh(m0, h1, BEAM - w), _sh(m0, h1, -w), _sh(m0, h0, -w), _sh(m0, h0, BEAM - w), ramp=HULLN,
               lvl=lambda s, t, P: 6.6 - (0.8 if t < 4 else 0))
        e.quad('vaixell', _sh(m0, h1, -w), _sh(m1, h1, -w), _sh(m1, h0, -w), _sh(m0, h0, -w), tex=(img, crop))
        e.quad('vaixell', _sh(m0, h1, BEAM - w), _sh(m1, h1, BEAM - w), _sh(m1, h1, -w), _sh(m0, h1, -w), ramp=HULLN,
               lvl=5.0)
    # el pal amb la creueta i el radar, daurats pel primer sol; els estais
    SUN_ = [(120, 70, 30), (190, 120, 50), (240, 176, 96), (255, 220, 160), (255, 244, 214)]
    e.tub('pal', _sh(27, 8.8, -0.2), _sh(27, 16, -0.2), 0.12 * U, SUN_, 2.4, llum_dir=(-1.0, 0.2))
    e.cable('pal', [_sh(25.5, 13.5, -0.2), _sh(28.5, 13.5, -0.2)], SUN_, 3.0, gruix=0.12 * U)
    e.cable('pal', [_sh(25.8, 11.6, -0.2), _sh(28.2, 11.6, -0.2)], SUN_, 2.4, gruix=0.16 * U)
    e.cable('pal', [_sh(36.5, sheer(36.5), -0.5), _sh(36.5, 9.6, -0.5)], STEELX, 4.0, gruix=0.1 * U)
    e.cable('pal', [_sh(27, 15.6, -0.2), _sh(40.4, sheer(40.2) + 0.2, 0)], STEELX, 2.8, gruix=0.04 * U)
    e.cable('pal', [_sh(27, 15.6, -0.2), _sh(2, 7.6, 0)], STEELX, 2.8, gruix=0.04 * U)
    # la grua de popa, amb la zòdiac penjada
    e.tub('grua', _sh(3.2, sheer(3), -0.8), _sh(3.2, 5.8, -0.8), 0.14 * U, STEELX, 5.0)
    e.cable('grua', [_sh(3.2, 5.8, -0.8), _sh(0.2, 7.6, -0.8)], [(60, 46, 10), (130, 100, 20), (200, 160, 40),
                                                                 (236, 200, 80)], 2.6, gruix=0.12 * U)
    e.cable('grua', [_sh(0.4, 7.5, -0.8), _sh(0.4, 5.6, -0.8)], STEELX, 3.0, gruix=0.03 * U)
    e.tub('grua', _sh(-1.4, 5.1, -0.8), _sh(2.2, 5.1, -0.8), 0.3 * U, [(30, 30, 34), (52, 52, 56), (80, 80, 82),
                                                                       (110, 110, 110)], 2.4)


def _moll(e):
    x0, x1 = -2000.0, 5000.0

    def pedra(s, t, P):
        x, z = P[0], P[2]
        row = int(z // 45)
        lvl = 3.8 + (hr(int((x + row * 37) // 90), row, 55) - 0.5) * 0.6 + (fbm(x / 70, z / 50, 56) - 0.5) * 0.6
        if z % 45 < 4 or (x + row * 37) % 90 < 4:
            lvl -= 0.9 * (1 - smooth(300, 900, z - RAIL_Z))            # les juntes, que es perden de lluny
        if z > QUAY_Z - 14:
            lvl += 1.4                                                  # la vora, de pedra més clara
        return lvl
    e.quad('moll', (x0, QUAY_Y, QUAY_Z), (x1, QUAY_Y, QUAY_Z), (x1, QUAY_Y, RAIL_Z), (x0, QUAY_Y, RAIL_Z),
           ramp=STONE, lvl=pedra)
    # el primer sol, rasant, tenyeix el moll de rosa (més com més lluny: a prop, l'ombra de la terrassa)
    e.claror((x0, QUAY_Y + 0.3, QUAY_Z), (x1, QUAY_Y + 0.3, QUAY_Z), (x1, QUAY_Y + 0.3, RAIL_Z), (x0, QUAY_Y + 0.3, RAIL_Z),
             (236, 180, 160), lambda s, t: 0.28 * smooth(200, 900, QUAY_Z - RAIL_Z - t))
    # l'ombra de l'Arenga no arriba al moll (el sol és darrere); la de la terrassa sí, cap a nosaltres
    # bites amb els caps d'amarratge
    for bx in (420.0, 2300.0):
        e.tub('bita', (bx, QUAY_Y, QUAY_Z - 22), (bx, QUAY_Y + 24, QUAY_Z - 22), 9, IRON, 3.0)
        e.tub('bita', (bx, QUAY_Y + 24, QUAY_Z - 22), (bx, QUAY_Y + 28, QUAY_Z - 22), 13, IRON, 3.6)
    e.cable('cap', [_sh(2, sheer(2) - 0.5), (200.0, 40.0, QUAY_Z - 10), (420.0, QUAY_Y + 22, QUAY_Z - 22)], ROPE, 3.0,
            gruix=4)
    e.cable('cap', [_sh(36, sheer(36) - 0.5), (2200.0, 60.0, QUAY_Z - 4), (2300.0, QUAY_Y + 22, QUAY_Z - 22)], ROPE,
            3.0, gruix=4)
    # unes nanses apilades i un rotlle de corda, a mig moll
    for k, (nx, nz, a) in enumerate(((760.0, 520.0, 0.3), (800.0, 470.0, -0.2), (780.0, 495.0, 0.1))):
        y0 = QUAY_Y + (34 if k == 2 else 0)
        e.caixa_girada('nansa', nx, nz, 60, 40, 34, a, [(20, 30, 40), (34, 50, 64), (52, 74, 90), (80, 104, 116)], 2.4,
                       y0=y0, cares={'dalt': {'ramp': ROPE, 'lvl': lambda s, t, P: 2.6 + (1.2 if int(s / 5 + t / 5) % 2 else 0)}})
    e.foscor('ombra_nanses', (840.0, QUAY_Y + 0.4, 560.0), (980.0, QUAY_Y + 0.4, 560.0), (980.0, QUAY_Y + 0.4, 430.0),
             (840.0, QUAY_Y + 0.4, 430.0), lambda s, t: 0.5 * min(1.0, s / 30, (140 - s) / 30, t / 20))
    # el fanal, encara encès
    lx, lz = 1250.0, 820.0
    e.tub('fanal', (lx, QUAY_Y, lz), (lx, QUAY_Y + 260, lz), 4, IRON, 2.6)
    e.caixa('fanal', lx - 10, lx + 10, QUAY_Y + 260, QUAY_Y + 290, lz - 10, lz + 10, [(160, 120, 60), (240, 200, 120),
                                                                                    (255, 236, 190)], 1.6)
    e.caixa('fanal', lx - 13, lx + 13, QUAY_Y + 290, QUAY_Y + 296, lz - 13, lz + 13, IRON, 3.0)


def _terrassa(e):
    x0, x1 = RAIL_X

    def fusta(s, t, P):
        x, z = P[0], P[2]
        plank = int(z // 16)
        lvl = 3.6 + (hr(plank, int((x + plank * 53) // 260), 56) - 0.5) * 0.7 + (fbm(x / 60, z / 8, 57) - 0.5) * 0.6
        if z % 16 < 1.6:
            lvl -= 1.6 * (1 - smooth(-200, 160, z) * 0.5)
        elif (x + plank * 53) % 260 < 2:
            lvl -= 1.2
        return lvl
    e.quad('terra', (x0, 0, RAIL_Z), (x1, 0, RAIL_Z), (x1, 0, -600), (x0, 0, -600), ramp=WOOD, lvl=fusta)
    # la vora de la tarima, a la dreta, i el moll que continua
    e.quad('terra', (x1, 0, RAIL_Z), (x1, 0, -600), (x1, QUAY_Y, -600), (x1, QUAY_Y, RAIL_Z), ramp=WOOD, lvl=1.6)
    # la claror càlida del bar, darrere nostre, pel terra de l'esquerra
    e.claror((x0, 0.3, 60), (200, 0.3, 60), (200, 0.3, -600), (x0, 0.3, -600), GOLDLIT,
             lambda s, t: 0.32 * max(0.0, 1 - math.hypot((s - 900) / 900, (t - 660) / 420)))


def _barana_mon(e):
    x0, x1 = RAIL_X
    L = int(x1 - x0)
    e.quad('barana', (x0, RAIL_H, RAIL_Z), (x1, RAIL_H, RAIL_Z), (x1, 0, RAIL_Z), (x0, 0, RAIL_Z),
           tex=(_barana(L), (0, 0, L, RAIL_H)))
    # el test de bruc a la punta de la dreta
    _test(e, x1 - 40, RAIL_Z - 30, 0.0, fosc=False)


def _test(e, cx, cz, ang, fosc):
    """Un test llarg de fusta amb bruc florit."""
    lv = -0.8 if fosc else 3.0
    e.caixa_girada('test', cx, cz, 90, 34, 34, ang, WOOD, lv,
                   cares={'davant': {'ramp': WOOD, 'lvl': lambda s, t, P: lv - 0.4 + (0.8 if int(s) % 16 < 2 else 0)},
                          'dalt': {'ramp': [(14, 10, 8), (24, 18, 14), (36, 26, 20)], 'lvl': 1.0}})
    for i in range(70):
        a = (hr(i, int(cx)) - 0.5) * 84
        b = (hr(i, int(cx) + 1) - 0.5) * 28
        P = (cx + a * math.cos(ang) - b * math.sin(ang), 34, cz + a * math.sin(ang) + b * math.cos(ang))
        h = 6 + hr(i, 3) * 22 * (1 - abs(a) / 60)
        e.cable('test', [P, (P[0] + (hr(i, 5) - 0.5) * 6, 34 + h, P[2])], LEAF, -0.4 if fosc else 2.2, gruix=2.4)
        e.cable('test', [(P[0], 34 + h * 0.6, P[2]), (P[0] + (hr(i, 6) - 0.5) * 4, 34 + h + 2, P[2])], HEATHER,
                0.2 + hr(i, 4) if fosc else 2.6 + hr(i, 4), gruix=3.0)


def _l(lx, lz, y=0.0, ang=0.0, cx=0.0):
    """Un punt de la taula (lx al llarg des de `cx`, lz cap al fons des del centre de la taula) → el món."""
    zc = (TAULA_Z[0] + TAULA_Z[1]) / 2
    c, s = math.cos(ang), math.sin(ang)
    return (cx + lx * c - lz * s, y, zc + lx * s + lz * c)


def _cadira(e, cx, cz, ang, fosc=False, sid='cadira'):
    """Una cadira de bistrot: seient rodó de vímet, respatller corbat de vímet amb el marc de ferro i quatre potes."""
    WICK = [(30, 20, 12), (60, 40, 24), (110, 80, 48), (160, 120, 76), (196, 160, 110)]
    lv = -1.2 if fosc else 2.6
    c, s = math.cos(ang), math.sin(ang)

    def P(lx, y, lz):
        return (cx + lx * c - lz * s, y, cz + lx * s + lz * c)
    for lx, lz in ((-13, -12), (13, -12), (-12, 12), (12, 12)):
        e.cable(sid, [P(lx * 1.15, 0, lz * 1.15), P(lx, 29, lz)], IRON, lv, gruix=2.0)
    e.quad(sid, P(-15, 30, 15), P(15, 30, 15), P(15, 30, -15), P(-15, 30, -15), ramp=WICK,
           lvl=lambda s_, t, Q: lv + 0.6 + (0.8 if (int(s_) + int(t)) % 3 == 0 else 0),
           forma=lambda s_, t: (s_ - 15) ** 2 + (t - 15) ** 2 <= 225)
    e.cable(sid, [P(-15, 30, -14), P(-15, 30, 14)], IRON, lv + 0.6, gruix=1.6)
    # el respatller: dos panys girats (fa corba), amb el vímet
    for a0, a1 in ((-15, 0), (0, 15)):
        za, zb = 14 - abs(a0) * 0.2, 14 - abs(a1) * 0.2
        e.quad(sid, P(a0, 62, za), P(a1, 62, zb), P(a1, 38, zb), P(a0, 38, za), ramp=WICK,
               lvl=lambda s_, t, Q: lv + 0.4 + (1.0 if (int(s_ * 1.5) + int(t * 1.5)) % 3 == 0 else 0) - t * 0.02,
               dues_cares=True)
    e.cable(sid, [P(-15, 62, 11), P(0, 63, 14), P(15, 62, 11)], IRON, lv + 0.8, gruix=2.4)
    for lx in (-15, 15):
        e.cable(sid, [P(lx, 30, 11), P(lx, 62, 11)], IRON, lv + 0.4, gruix=2.0)


CUPS = (-130.0, -76.0, -14.0, 44.0, 88.0)


def _taula(e):
    """La taula llarga: dues taules ajuntades, cadascuna una mica girada, amb el que hi ha damunt."""
    zc = (TAULA_Z[0] + TAULA_Z[1]) / 2
    D = TAULA_Z[1] - TAULA_Z[0]
    for x0, x1, a in TAULES:
        cx = (x0 + x1) / 2
        w = x1 - x0

        def P(lx, y, lz, a=a, cx=cx):
            return _l(lx, lz, y, a, cx)
        for lx in (-w / 2 + 6, w / 2 - 6):
            for lz in (-D / 2 + 5, D / 2 - 5):
                Q = P(lx, 0, lz)
                e.caixa('taula', Q[0] - 1.5, Q[0] + 1.5, 0, TAULA_H - 3, Q[2] - 1.5, Q[2] + 1.5, TABLER, 2.6)
        # el sobre: la cara de dalt (fora de la capa del davant: en Diu s'hi enfila) i el cantell
        e.quad('taula_dalt', P(-w / 2, TAULA_H, D / 2), P(w / 2, TAULA_H, D / 2), P(w / 2, TAULA_H, -D / 2),
               P(-w / 2, TAULA_H, -D / 2), ramp=WOOD,
               lvl=lambda s, t, Q: 5.0 + (hr(int(s // 7), int(t // 2), 58) - 0.5) * 0.6 - (1.0 if s % 75 < 1 else 0))
        e.quad('taula', P(-w / 2, TAULA_H, -D / 2), P(w / 2, TAULA_H, -D / 2), P(w / 2, TAULA_H - 4, -D / 2),
               P(-w / 2, TAULA_H - 4, -D / 2), ramp=WOOD, lvl=lambda s, t, Q: 4.4 - t * 0.5)
        e.quad('taula', P(-w / 2, TAULA_H, D / 2), P(-w / 2, TAULA_H, -D / 2), P(-w / 2, TAULA_H - 4, -D / 2),
               P(-w / 2, TAULA_H - 4, D / 2), ramp=WOOD, lvl=5.2)
    img, _ = _pla()
    # tasses amb el plat i la cullereta
    for i, lx in enumerate(CUPS):
        Q = _l(lx, -4 + (i % 2) * 6, TAULA_H + 0.4)
        e.quad('damunt', (Q[0] - 7, Q[1], Q[2] + 6), (Q[0] + 7, Q[1], Q[2] + 6), (Q[0] + 7, Q[1], Q[2] - 6),
               (Q[0] - 7, Q[1], Q[2] - 6), ramp=CUPR, lvl=3.6, forma=lambda s, t: ((s - 7) / 7) ** 2 + ((t - 6) / 6) ** 2 <= 1)
        e.tub('damunt', Q, (Q[0], Q[1] + 8, Q[2]), 4.2, CUPR, 3.0, llum_dir=(-1.0, 0.3))
        e.quad('damunt', (Q[0] - 3.4, Q[1] + 8.2, Q[2] + 3.4), (Q[0] + 3.4, Q[1] + 8.2, Q[2] + 3.4),
               (Q[0] + 3.4, Q[1] + 8.2, Q[2] - 3.4), (Q[0] - 3.4, Q[1] + 8.2, Q[2] - 3.4), ramp=[(40, 22, 10), (70, 40, 20)],
               lvl=0.8, forma=lambda s, t: (s - 3.4) ** 2 + (t - 3.4) ** 2 <= 11)
        e.cable('damunt', [(Q[0] + 4, Q[1] + 6, Q[2] - 1), (Q[0] + 6.5, Q[1] + 4, Q[2] - 1)], CUPR, 2.6, gruix=1.4)
        e.cable('damunt', [(Q[0] - 8, Q[1] + 0.3, Q[2] - 4), (Q[0] - 12, Q[1] + 0.3, Q[2] - 7)], STEELX, 5.0, gruix=0.8)
    # la tetera i els scones (els dibuixos plans, drets damunt la taula)
    e.sprite('damunt', img.crop((294, PL.TOP - 22, 326, PL.TOP - 3)), (309 - 294, 18), _l(-46, 2, TAULA_H))
    e.sprite('damunt', img.crop((240, PL.TOP - 10, 266, PL.TOP)), (13, 9), _l(-104, -2, TAULA_H))
    # el diari plegat i el sucrer
    Q = _l(10, -2, TAULA_H + 0.3, 0.2)
    e.quad('damunt', (Q[0] - 16, Q[1], Q[2] + 11), (Q[0] + 16, Q[1], Q[2] + 13), (Q[0] + 18, Q[1], Q[2] - 9),
           (Q[0] - 14, Q[1], Q[2] - 11), ramp=CREAM,
           lvl=lambda s, t, P: 4.6 - (2.2 if (int(t) % 4 == 0 and 3 < s % 16 < 13) else 0) - (2.6 if 2 < s < 12 and 3 < t < 9 else 0))
    Q = _l(66, 6, TAULA_H)
    e.tub('damunt', Q, (Q[0], Q[1] + 7, Q[2]), 4.0, CUPR, 3.0, llum_dir=(-1.0, 0.3))
    e.cable('damunt', [(Q[0] + 1, Q[1] + 7, Q[2]), (Q[0] + 4, Q[1] + 13, Q[2] - 2)], STEELX, 5.0, gruix=1.0)


def _ombres(e):
    """Les ombres llargues del sol baix (de l'esquerra i del fons): cap a la dreta i cap a nosaltres."""
    sx, sz = 0.85, -0.55                                     # cap on cau l'ombra, per unitat d'alçada
    zc = (TAULA_Z[0] + TAULA_Z[1]) / 2
    L = TAULA_H * 2.4
    e.foscor('ombra', (-150 + L * sx * 0.2, 0.4, TAULA_Z[1] + 4), (150 + L * sx, 0.4, TAULA_Z[1] + 4),
             (150 + L * sx, 0.4, zc + L * sz - 10), (-150 + L * sx * 0.2, 0.4, zc + L * sz - 10),
             lambda s, t: 0.42 * min(1.0, s / 30, t / 12))
    for x in SEIENTS.values():
        e.foscor('ombra', (x - 10, 0.4, 50), (x + 110, 0.4, 50), (x + 110, 0.4, -40), (x - 10, 0.4, -40),
                 lambda s, t: 0.36 * max(0.0, 1 - abs((t - 45) - (s - 20) * 0.55) / 18) * min(1.0, s / 15, (120 - s) / 40))
    # la barana fa ratlles d'ombra pel terra de la terrassa (el sol la travessa)
    x0, x1 = RAIL_X
    e.foscor('ombra', (x0, 0.4, RAIL_Z), (x1, 0.4, RAIL_Z), (x1, 0.4, RAIL_Z - 120), (x0, 0.4, RAIL_Z - 120),
             lambda s, t: (0.32 if (s - t * 1.5) % 15 < 3.5 else 0.0) * (1 - t / 120) + 0.18 * max(0.0, 1 - t / 30))


def _tendal(e):
    """El tendal, vist des de sota: la lona a contrallum (les ratlles fugen), els festons de la vora i els pals."""
    x0, x1 = RAIL_X[0], RAIL_X[1] - 300
    L = int(x1 - x0)
    lona = _lona(L, 700, False)
    e.quad('tendal', (x0, AW_Y, -660), (x1, AW_Y, -660), (x1, AW_Y, AW_Z), (x0, AW_Y, AW_Z), tex=(lona, (0, 0, L, 700)),
           dues_cares=True, ombra=lambda s, t: 0.55)
    fest = _lona(L, 24, True)
    e.quad('tendal', (x0, AW_Y, AW_Z), (x1, AW_Y, AW_Z), (x1, AW_Y - 24, AW_Z), (x0, AW_Y - 24, AW_Z),
           tex=(fest, (0, 0, L, 24)), dues_cares=True, ombra=lambda s, t: 0.25)
    e.cable('tendal', [(x0, AW_Y - 2, AW_Z), (x1, AW_Y - 2, AW_Z)], IRON, 2.0, gruix=2.4)
    # els pals: el de l'esquerra, a prop i fosc, i el de la dreta, al fons
    for px, pz in ((-420.0, AW_Z - 4), (x1 - 4, AW_Z - 4)):
        e.tub('pal_tendal', (px, 0, pz), (px, AW_Y, pz), 3.2, IRON, 1.6, llum_dir=(-1.0, 0.2))
        e.caixa('pal_tendal', px - 6, px + 6, 0, 3, pz - 6, pz + 6, IRON, 1.4)


def _tele_mon(e, tex):
    """La tele penjada del tendal, girada cap a la colla: la pantalla és el dibuix pla; la caixa, de plàstic fosc."""
    cx, cy, cz = TV_C
    c, s = math.cos(TV_ANG), math.sin(TV_ANG)

    def P(lx, y, lz):
        return (cx + lx * c - lz * s, cy + y, cz + lx * s + lz * c)
    w, h, d = TV_W / 2, TV_H / 2, TV_D
    # el braç fins al tendal
    e.tub('tele_caixa', P(0, h, d * 0.6), P(0, AW_Y - cy, d * 0.6), 2.0, IRON, 2.4)
    e.caixa_girada('tele_caixa', P(0, 0, d / 2 + 2)[0], P(0, 0, d / 2 + 2)[2], 30, 6, 6, TV_ANG, IRON, 2.0, y0=cy + h)
    e.caixa_girada('tele_caixa', P(0, 0, d / 2)[0], P(0, 0, d / 2)[2], TV_W, d, TV_H, TV_ANG, TABLER, 1.4, y0=cy - h,
                   cares={'dalt': {'ramp': TABLER, 'lvl': 2.6}, 'esquerra': {'ramp': TABLER, 'lvl': 1.2},
                          'davant': {'ramp': TABLER, 'lvl': 1.4}})
    e.quad('tele', P(-w, h, -0.6), P(w, h, -0.6), P(w, -h, -0.6), P(-w, -h, -0.6), tex=(tex, TV_CROP))
    # el cable, que baixa fent panxa fins al pal del tendal
    e.cable('tele_caixa', [P(w - 6, -h, d * 0.5), (-330.0, 120.0, 0.0), (-415.0, 150.0, AW_Z - 4)],
            [(8, 8, 10), (20, 20, 24), (36, 36, 42)], 1.6, gruix=1.4)


def _primer_pla(e):
    """El test de bruc de la cantonada de baix a l'esquerra i una cadira buida a la dreta, a contrallum."""
    _test(e, -219.0, -142.0, 0.25, fosc=True)
    _cadira(e, 62.0, -240.0, -0.5, fosc=True, sid='cadira_davant')


def escena(cv, tex=None, estat=frozenset()):
    _FASE[0] = 0.0
    tex = tex or _tele()
    _cel(cv)
    _turons(cv)
    e = Escena(cv, CAM, LLUMS, ambient=AMBIENT)
    e.quad('mar', (-90000, SEA_Y, 90000), (90000, SEA_Y, 90000), (90000, SEA_Y, 200), (-90000, SEA_Y, 200),
           ramp=DAWN, lvl=_aigua)
    _barqueta(cv)
    _arenga(e)
    _moll(e)
    _terrassa(e)
    _ombres(e)
    _barana_mon(e)
    _, moll_img = _pla()
    e.sprite('gavina', moll_img.crop((472, PL.QUAY - 18, 486, PL.QUAY - 7)), (6, 10), (420.0, QUAY_Y + 28, QUAY_Z - 22))
    for x, z in ((SEIENTS['capitana'] - 2, SEU_Z + 30), (SEIENTS['nadia'], SEU_Z + 32), (SEIENTS['marcel'] + 2, SEU_Z + 30),
                 (SEIENTS['tomas'], SEU_Z + 31)):
        _cadira(e, x, z, 0.06 * (hr(int(x), 3) - 0.5) + 0.0)
    _taula(e)
    _tele_mon(e, tex)
    _tendal(e)
    _primer_pla(e)
    return e


# ─── Composició ─────────────────────────────────────────────────────────────

@functools.lru_cache(maxsize=None)
def _base():
    cv = Canvas(light=LIGHT)
    e = escena(cv)
    return cv.img.copy(), e


def bg(cv):
    cv.img.paste(_base()[0])
    cv.P = cv.img.load()


def tele_apagada(cv):
    _, e = _base()
    cv.img.alpha_composite(_diff(_amb_capa(e.capa(_tele(apagada=True), {'tele'})), _base()[0]))
    cv.P = cv.img.load()


def _amb_capa(capa):
    img = _base()[0].copy()
    img.alpha_composite(capa)
    return img


PROPS = {'tele_apagada': tele_apagada}


def _frames():
    _, e = _base()
    return [_diff(_amb_capa(e.capa(_tele(i), {'tele'})), _base()[0]) for i in range(8)]


# L'aigua de la badia: el soroll corre de costat; els darrers BAY_FADE fotogrames es fonen amb el principi perquè el
# bucle no salti. Només es toquen els píxels on es veu l'aigua.
BAY_N, BAY_FADE, BAY_STEP = 12, 4, 0.09


def _mar(fase):
    cv = Canvas(light=LIGHT)
    _FASE[0] = fase
    e = Escena(cv, CAM, LLUMS, ambient=AMBIENT)
    e.retalls = _caixa_mar()
    e.quad('mar', (-90000, SEA_Y, 90000), (90000, SEA_Y, 90000), (90000, SEA_Y, 200), (-90000, SEA_Y, 200),
           ramp=DAWN, lvl=_aigua)
    _FASE[0] = 0.0
    return cv.img


@functools.lru_cache(maxsize=None)
def _caixa_mar():
    """On es veu l'aigua (u0, v0, u1, v1): l'animació només hi repinta."""
    _, e = _base()
    idx = e.ids.index('mar')
    ys = [i // e.cv.w for i, a in enumerate(e.amo) if a == idx]
    xs = [i % e.cv.w for i, a in enumerate(e.amo) if a == idx]
    return (min(xs), min(ys), max(xs) + 1, max(ys) + 1)


def _frames_badia():
    base, e = _base()
    idx = e.ids.index('mar')
    Wc = e.cv.w
    obert = [(i % Wc, i // Wc) for i, a in enumerate(e.amo) if a == idx]
    frames = []
    for i in range(BAY_N):
        a, b = _mar(i * BAY_STEP).load(), _mar((i - BAY_N) * BAY_STEP).load()
        w = max(0, i - (BAY_N - BAY_FADE)) / BAY_FADE
        out = base.copy()
        o = out.load()
        for X, Y in obert:
            o[X, Y] = b[X, Y] if hr(X, Y, 91) < w else a[X, Y]
        _barqueta_sobre(out, base)
        frames.append(_diff(out, base))
    return frames


def _barqueta_sobre(out, base):
    """La barqueta i el sol es pinten damunt l'aigua: es tornen a posar com al fons."""
    bx, by = 196, HOR + 7
    o, b = out.load(), base.load()
    for Y in range(by - 14, by + 6):
        for X in range(bx - 2, bx + 16):
            o[X, Y] = b[X, Y]


# El vapor: tres bufs per tassa (i el broc de la tetera) que pugen, es tremolen i s'esvaeixen.
STEAM_N = 32


def _punts_vapor():
    pts = []
    for i, lx in enumerate(CUPS):
        Q = _l(lx, -4 + (i % 2) * 6, TAULA_H + 9)
        u, v, _ = CAM.projecta(Q)
        pts.append((u, v, CAM.escala(Q)))
    Q = _l(-34, 2, TAULA_H + 14)
    u, v, _ = CAM.projecta(Q)
    pts.append((u, v, CAM.escala(Q)))
    return pts


def _frames_vapor():
    base, _ = _base()
    frames = []
    for i in range(STEAM_N):
        cv = Canvas(light=LIGHT, img=base.copy())
        for j, (sx, sy, k) in enumerate(_punts_vapor()):
            for n in range(3):
                t = (i / STEAM_N + n / 3 + hr(j, 92)) % 1.0
                x = sx + math.sin(t * 5 + j * 1.7) * (0.7 + 2.7 * t) * k
                y = sy - t * 19 * k
                a = 0.45 * (1 - t) ** 1.2
                pts = ((0, 0), (1, 0), (0, -1), (1, -1)) if t < 0.4 else ((0, 0), (0, -1)) if t < 0.7 else ((0, 0),)
                for dx, dy in pts:
                    px, py = round(x + dx), round(y + dy)
                    if 0 <= px < W and 0 <= py < H:
                        cv.flat(px, py, mix(cv.get(px, py)[:3], (236, 232, 226), a))
        frames.append(_diff(cv.img, base))
    return frames


ANIMS = {'tele': {'frames': _frames, 'frameDuration': 220},
         'badia': {'frames': _frames_badia, 'frameDuration': 240},
         'vapor': {'frames': _frames_vapor, 'frameDuration': 150}}


# ─── Capes del davant i geometria ──────────────────────────────────────────

def _amo(ids):
    def mask(x, y):
        _, e = _base()
        return e.ids[e.amo[y * e.cv.w + x]] in ids
    return mask


_SEU = {c: _p(x, SEU_Z) for c, x in SEIENTS.items()}
# la taula (el cantell, les potes i el que hi ha damunt) tapa les cames de qui seu al darrere; la línia base, entre els
# peus dels de darrere i els de l'Iri i la Vet, que són davant
_BASE_TAULA = max(v for _, v in _SEU.values()) + 2
_DIU = _p(DIU[0], DIU[1], TAULA_H)


def _dins(poly, x, y):
    n, c = len(poly), False
    for i in range(n):
        (xa, ya), (xb, yb) = poly[i], poly[(i + 1) % n]
        if (ya > y) != (yb > y) and x < xa + (y - ya) * (xb - xa) / (yb - ya):
            c = not c
    return c


def _envolupant(pts):
    pts = sorted(set(pts))

    def creu(o, a, b):
        return (a[0] - o[0]) * (b[1] - o[1]) - (a[1] - o[1]) * (b[0] - o[0])
    lo, hi = [], []
    for q in pts:
        while len(lo) >= 2 and creu(lo[-2], lo[-1], q) <= 0:
            lo.pop()
        lo.append(q)
    for q in reversed(pts):
        while len(hi) >= 2 and creu(hi[-2], hi[-1], q) <= 0:
            hi.pop()
        hi.append(q)
    return lo[:-1] + hi[:-1]


def _caixes_taula():
    """La silueta de cada taula a la pantalla (el sobre, el cantell, les potes i el que queda a sota)."""
    D = TAULA_Z[1] - TAULA_Z[0]
    out = []
    for x0, x1, a in TAULES:
        cx, w = (x0 + x1) / 2, x1 - x0
        pts = []
        for lx in (-w / 2, w / 2):
            for lz in (-D / 2, D / 2):
                for y in (0.0, TAULA_H):
                    u, v, _ = CAM.projecta(_l(lx, lz, y, a, cx))
                    pts.append((u, v))
        out.append(_envolupant(pts))
    return out


_TAULES_PANT = _caixes_taula()


def _mascara_taula(x, y):
    """Tot el que és la taula a la pantalla (i el que s'hi veu per sota: les cames de qui seu darrere no hi surten),
    més el que hi ha damunt; menys el tros del sobre on trepitja en Diu."""
    if abs(x - _DIU[0]) <= 22 and _DIU[1] - 40 <= y <= _DIU[1] + 2:
        return False
    if any(_dins(p, x + 0.5, y + 0.5) for p in _TAULES_PANT):
        return True
    _, e = _base()
    return e.ids[e.amo[y * e.cv.w + x]] == 'damunt'


FRONT = [{'id': 'davant', 'mask': _mascara_taula, 'baseline': _BASE_TAULA, 'zIndex': 20},
         {'id': 'davant_primer_pla', 'mask': _amo({'test', 'cadira_davant', 'pal_tendal', 'tendal', 'tele', 'tele_caixa'}),
          'baseline': 999, 'zIndex': 21}]

_V_FONS = min(v for _, v in _SEU.values()) - 8

GEOMETRIA = {
    'things': {},
    'spawns': {**_SEU, 'iri': _p(*IRI), 'vet': _p(*VET), 'diu': _DIU},
    'walkable': [_p(IRI[0] - 20, IRI[1] - 10), _p(VET[0] + 20, VET[1] - 10), _p(VET[0] + 20, VET[1] + 10),
                 _p(IRI[0] - 20, IRI[1] + 10)],
    'floorSquash': 0.3,
    # el sol baix, a l'esquerra i al fons: les ombres cauen cap a la dreta i cap a nosaltres
    'characterShadow': {'enabled': True, 'color': '#1a1420', 'alpha': 0.4, 'squash': 0.3, 'core': 0.6,
                        'light': {'x': 1, 'y': 0.35, 'direction': True, 'stretch': 0.9}},
    'regions': [
        {'id': 'perspectiva', 'active': True, 'scaleEnabled': True, 'scaleWalkSpeed': True,
         'scaleTop': round(_escala_a(_V_FONS), 3), 'scaleBottom': round(_escala_a(H - 1), 3),
         'points': [(0, _V_FONS), (W - 1, _V_FONS), (W - 1, H - 1), (0, H - 1)]},
        # en Diu, damunt la taula: l'escala de la taula, no la del terra que hi ha a sota a la pantalla
        {'id': 'diu', 'active': True, 'scaleEnabled': True,
         'scaleTop': round(CAM.escala((DIU[0], TAULA_H, DIU[1])), 3),
         'scaleBottom': round(CAM.escala((DIU[0], TAULA_H, DIU[1])), 3),
         'points': [(_DIU[0] - 30, _DIU[1] - 12), (_DIU[0] + 30, _DIU[1] - 12), (_DIU[0] + 30, _DIU[1] + 4),
                    (_DIU[0] - 30, _DIU[1] + 4)]},
    ],
    'characterLights': {
        'ambient': '#b8b4c8',                                       # l'alba, freda
        'lights': [
            {'x': 0, 'y': 120, 'radius': 520, 'color': '#ffcf9a', 'intensity': 0.7},          # el sol, a l'esquerra
            {'x': 40, 'y': 360, 'radius': 360, 'color': '#ffc070', 'intensity': 0.5},         # la finestra del bar
        ],
    },
}
