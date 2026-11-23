"""
La porteria (acte 2, de nit; l'Iri, i la Vet hi és). Art definitiu, a 1×.

Un passadís estret de pedra de gres que fuig cap a la dreta, vist una mica des de dalt i de biaix:
  - la paret del fons, de carreus, amb pilastres que s'empetiteixen cap a la dreta; al fons de tot, l'arc fosc
    per on continua el passadís;
  - la **porta de l'ala dels canonges**: de taulons de roure amb bandes de ferro i claus, ficada a l'arc de dovelles,
    i el **forrellat** (una barra de ferro) passat;
  - les dues **torxes** als seus braços de ferro, a banda i banda de la porta (la flama és una animació, `flames`):
    tota la llum de la sala, i els racons foscos;
  - el **banc** de fusta contra la paret, on seu en Bonfill (amb la llança);
  - la **columna** exempta, a la dreta, per amagar-s'hi (capa del davant amb la seva línia base);
  - el **faristol** amb el **llibre de les entrades**, obert, girat cap a la sala (també s'hi passa per darrere);
  - primer pla: el pilar i l'arrencada de l'arc de l'entrada, a l'esquerra, a contrallum.
Decorats: `ninots` (els dos ninots nous al llibre, «fra Tos i fra Silenci») i `porta_oberta` (la porta oberta cap a
l'ala dels canonges; cal que el contingut el tingui).

El món: x a la dreta (al llarg del passadís), y amunt (0 = terra), z endins; 1 unitat = 1 px a escala 1 (l'Iri
hi fa 84). La càmera, alta i girada cap a la dreta: l'escala dels personatges només depèn de la y de pantalla.
"""
import functools
import math

from PIL import Image

import hd640  # noqa: F401  (abans de cap hd.rooms: posa la llibreria a 640×360)

from hd.pix import Canvas, Light, mix
from hd640.rooms.nit_comu import (W, BOTTOM, PEDRA, LLOSA, FUSTA, FERRO, FOC, PERGAMI, TINTA, CERA,
                                  fbm, hr, carreus, lloses, taulons, veta, flama, ombra, hud_negre, sense,
                                  _diff, llum_personatge, rect_de)
from hd640.tres_d import Camera, Escena, Llum

# ─── La càmera i el món ──────────────────────────────────────────────────────
EYE_H, F, CY, YAW = 180, 380, 30, 0.40
CAM = Camera(pos=(-56, EYE_H, 0), yaw=YAW, pitch=0.0, f=F, centre=(320, CY))

ZB = 430                                            # la paret del fons
XE = 1500                                           # on gira el passadís (l'arc fosc del fons)
WALL_H = 420
PILASTRES = (-260, 470, 980)                             # x de l'esquerra de cada pilastra (ample 34, surt 14)
PORTA = (-46, 28, 116)                              # x0, x1, alçada de l'arrencada de l'arc (el punt de dalt: +37)
FORAT = 16                                          # el gruix de l'arc: la fulla és endins
TORXES = ((-84, 122), (70, 122))                   # x, y del braç de cada torxa (a la paret)
BANC = (112, 214, 24, 34)                           # x0, x1, fons, alçada del seient
COLUMNA = (318, 352, 15)                            # x, z, radi
FARISTOL = (-112, 384, 0.6)                        # x, z, angle (girat cap a la sala)
PILAR = (-150, -118, 238, 266)                      # el pilar del primer pla: x0, x1, z0, z1

LIGHT = Light(ambient=0.0, vignette=(60, 30), floor_fade=None)
LIGHT.width = W
NINXOL = (590, 96)                                  # el nínxol del fons amb el llum d'oli: x, y de la base
LLUMS = [Llum((x, y + 26, ZB - 24), 420, 5.2, power=1.25) for x, y in TORXES] + \
        [Llum((NINXOL[0] + 14, NINXOL[1] + 12, ZB - 30), 260, 3.6, power=1.4)]
AMBIENT = -1.6


def _p(x, z, y=0.0):
    u, v, _ = CAM.projecta((x, y, z))
    return round(u), round(v)


def _arc_porta(s, y):
    """Dins l'obertura de la porta? `s` des de la x0 de la porta, `y` del món."""
    x0, x1, ya = PORTA
    r = (x1 - x0) / 2
    if y <= ya:
        return 0 <= s <= x1 - x0
    return (s - r) ** 2 + (y - ya) ** 2 <= r * r


# ─── La paret i el terra ────────────────────────────────────────────────────

def _ninxol(x, y):
    nx, ny = NINXOL
    return nx <= x <= nx + 28 and ny <= y <= ny + 30 + 14 * math.sqrt(max(0.0, 1 - ((x - nx - 14) / 14) ** 2))


def _paret_lvl(s, t, P):
    """Carreus, i al voltant de la porta les dovelles de l'arc (juntes que surten del centre)."""
    x, y = P[0], P[1]
    x0, x1, ya = PORTA
    r = (x1 - x0) / 2
    cx = x0 + r
    d = math.hypot(x - cx, max(0.0, y - ya))
    if y > ya - 2 and r - 1 < d < r + 26:                              # les dovelles
        a = math.atan2(y - ya, x - cx)
        k = int(a / (math.pi / 11))
        fa = a - k * math.pi / 11
        v = 3.4 + (hr(k, 7, 3) - 0.5) * 0.8 + (fbm(x / 6, y / 6, 4) - 0.5) * 0.6
        if fa < 0.03 or d > r + 24.5:
            return v - 1.8
        if d < r + 2.5:
            v += 0.6
        return v
    if y <= ya and (x0 - 18 < x < x0 or x1 < x < x1 + 18):           # els brancals, carreus alts
        k = int(y // 42)
        v = 3.2 + (hr(k, int(x > cx), 5) - 0.5) * 0.7 + (fbm(x / 5, y / 7, 6) - 0.5) * 0.6
        if y - k * 42 < 1.6 or abs(x - x0) < 1.2 or abs(x - x1) < 1.2:
            return v - 1.8
        return v
    v = carreus(x + 900, WALL_H - y, alt=31, ample=(44, 72), seed=3, base=2.5)
    # el sòcol, més fosc i humit, i el fum de les torxes que ha ennegrit la paret per sobre de cada braç
    if y < 20:
        v -= 0.4 * (1 - y / 20)
    for tx, ty in TORXES:
        if y > ty + 30:
            dx = abs(x - tx) / (16 + (y - ty) * 0.25)
            if dx < 1:
                v -= 1.6 * (1 - dx) * min(1.0, (y - ty - 30) / 30)
    return v


def terra(e):
    e.quad('terra', (-700, 0, ZB), (XE + 400, 0, ZB), (XE + 400, 0, 0), (-700, 0, 0), ramp=LLOSA,
           lvl=lambda s, t, P: lloses(P[0], P[2], seed=11, base=2.4))


def porta(e, oberta):
    """La porta, ficada a l'arc: els brancals de dins, la fulla de taulons amb les bandes i els claus, i el forrellat.
    Oberta: la fulla girada cap endins (frontissa a l'esquerra) i, darrere, la foscor de l'ala dels canonges."""
    x0, x1, ya = PORTA
    r = (x1 - x0) / 2
    zf = ZB + FORAT
    top = ya + r
    # el fons de darrere (només es veu amb la porta oberta): un passadís fosc amb una mica de llum al terra
    e.quad('porta_fons', (x0 - 30, top + 20, zf + 160), (x1 + 30, top + 20, zf + 160), (x1 + 30, 0, zf + 160),
           (x0 - 30, 0, zf + 160), ramp=PEDRA, lvl=lambda s, t, P: carreus(s, t, alt=26, seed=9, base=-2.6))
    e.quad('porta_fons', (x0 - 30, 0, zf + 160), (x1 + 30, 0, zf + 160), (x1 + 30, 0, zf), (x0 - 30, 0, zf),
           ramp=LLOSA, lvl=lambda s, t, P: lloses(P[0], P[2], seed=13, base=-0.4 - t / 50))
    # els brancals (la cara de dins de l'obertura): el de l'esquerra mira cap a +x i es veu
    e.quad('porta_brancal', (x0, top, ZB), (x0, top, zf), (x0, 0, zf), (x0, 0, ZB), ramp=PEDRA,
           lvl=lambda s, t, P: carreus(s, t, alt=42, ample=(30, 40), seed=8, base=2.6))
    e.quad('porta_brancal', (x0, 0.4, zf), (x1, 0.4, zf), (x1, 0.4, ZB), (x0, 0.4, ZB), ramp=PEDRA, lvl=2.6)
    # la fulla
    ample = x1 - x0

    def forma(s, t):
        return _arc_porta(s, top - t)
    if oberta:
        a = 1.25                                                        # girada cap endins
        c, sn = math.cos(a), math.sin(a)

        def Q(lx, y):
            return (x0 + lx * c, y, zf + lx * sn)
        e.quad('porta_fulla', Q(0, top), Q(ample, top), Q(ample, 0), Q(0, 0), ramp=FUSTA,
               lvl=lambda s, t, P: taulons(s, t, 15, seed=21, base=2.8), forma=forma, dues_cares=True)
        return
    e.quad('porta_fulla', (x0, top, zf), (x1, top, zf), (x1, 0, zf), (x0, 0, zf), ramp=FUSTA,
           lvl=lambda s, t, P: taulons(s, t, 15, seed=21, base=2.8), forma=forma)
    zb = zf - 0.6
    for yb in (34, 118):                                                # les bandes de ferro, amb els claus
        e.quad('porta_ferro', (x0 + 2, yb + 6, zb), (x1 - 2, yb + 6, zb), (x1 - 2, yb, zb), (x0 + 2, yb, zb), ramp=FERRO,
               lvl=lambda s, t, P: 3.0 + (0.9 if t < 1.2 else 0) + (1.4 if int(s) % 12 in (5, 6) and 1.5 < t < 4.5 else 0)
               + (fbm(s / 3, t, 41) - 0.5) * 0.8)
    for k in range(4):                                                  # els claus de la fulla, en files
        for j in range(6):
            sx = x0 + 9 + j * (ample - 18) / 5
            sy = 70 + k * 12 if k < 2 else 150 + (k - 2) * 12
            if sy > top - 4 or not _arc_porta(sx - x0, sy + 3):
                continue
            e.quad('porta_ferro', (sx - 1.2, sy + 1.2, zb), (sx + 1.2, sy + 1.2, zb), (sx + 1.2, sy - 1.2, zb),
                   (sx - 1.2, sy - 1.2, zb), ramp=FERRO, lvl=lambda s, t, P: 4.6 - s * 0.8)
    # el forrellat: la barra a mitja alçada, el pany i la grapa al brancal de la dreta
    yf = 86
    e.caixa('forrellat', x0 + ample * 0.42, x1 + 10, yf - 2.5, yf + 2.5, zb - 4, zb - 0.6, FERRO, 4.0,
            cares={'dalt': {'ramp': FERRO, 'lvl': 5.6}, 'davant': {'ramp': FERRO, 'lvl': lambda s, t, P: 4.0 - t * 0.6}})
    e.caixa('forrellat', x0 + ample * 0.42 + 6, x0 + ample * 0.42 + 9, yf - 10, yf + 2.5, zb - 5, zb - 3.5, FERRO, 4.2)
    e.caixa('forrellat', x1 + 4, x1 + 12, yf - 7, yf + 7, ZB - 3, ZB, FERRO, 3.2)
    # l'anella de la porta
    e.quad('porta_ferro', (x1 - 22, 104, zb), (x1 - 12, 104, zb), (x1 - 12, 94, zb), (x1 - 22, 94, zb), ramp=FERRO,
           lvl=lambda s, t, P: 4.8 - math.hypot(s - 5, t - 5) * 0.4,
           forma=lambda s, t: 3.4 < math.hypot(s - 5, t - 5) < 5.2)


def paret(e):
    """La paret del fons, amb el forat de la porta, les pilastres i, al fons de tot, el gir del passadís."""
    x0, x1, ya = PORTA

    def forma(s, t):
        return not _arc_porta(s - 700 - x0, WALL_H - t) and not _ninxol(s - 700, WALL_H - t)
    # el nínxol: el fons (endins) i el llum d'oli de terrissa
    nx, ny = NINXOL
    e.quad('ninxol', (nx, ny + 46, ZB + 12), (nx + 28, ny + 46, ZB + 12), (nx + 28, ny, ZB + 12), (nx, ny, ZB + 12),
           ramp=PEDRA, lvl=lambda s, t, P: 4.2 - t * 0.04)
    e.quad('ninxol', (nx, ny + 0.2, ZB + 12), (nx + 28, ny + 0.2, ZB + 12), (nx + 28, ny + 0.2, ZB), (nx, ny + 0.2, ZB),
           ramp=PEDRA, lvl=4.0)
    e.quad('ninxol', (nx, ny + 46, ZB), (nx, ny + 46, ZB + 12), (nx, ny, ZB + 12), (nx, ny, ZB), ramp=PEDRA, lvl=3.0)
    e.caixa('ninxol', nx + 8, nx + 20, ny, ny + 5, ZB + 2, ZB + 8, PEDRA, 2.0,
            cares={'dalt': {'ramp': PEDRA, 'lvl': 1.0}})
    e.quad('paret', (-700, WALL_H, ZB), (XE, WALL_H, ZB), (XE, 0, ZB), (-700, 0, ZB), ramp=PEDRA, lvl=_paret_lvl,
           forma=forma)
    for px in PILASTRES:
        e.caixa('pilastra', px, px + 34, 0, WALL_H, ZB - 14, ZB, PEDRA, 2.6,
                cares={n: {'ramp': PEDRA, 'lvl': (lambda s, t, P, n=n: carreus(s + (40 if n == 'dreta' else 0),
                           t, alt=31, ample=(34, 34), seed=6, base=2.7 - (0.5 if n == 'esquerra' else 0)))}
                       for n in ('davant', 'esquerra', 'dreta')})


def fons_arc(cv):
    """El passadís que continua: l'arc fosc del fons (en pantalla), al cantó de la paret del fons."""
    u0, v0 = _p(XE - 4, ZB - 40)
    u1, v1 = _p(XE - 4, ZB - 150)
    top0 = CAM.projecta((XE, 150, ZB - 40))[1]
    for y in range(int(top0) - 30, int(max(v0, v1)) + 1):
        for x in range(u0, min(W, u1 + 30)):
            t = (x - u0) / max(1, (u1 - u0))
            yb = v0 + (v1 - v0) * t
            yt = top0 + (CAM.projecta((XE, 150, ZB - 150))[1] - top0) * t
            arc = yt - 18 * math.sin(math.pi * max(0.0, min(1.0, t)))
            if 0 <= t <= 1 and arc <= y <= yb:
                cv.put(x, y, PEDRA, 0.4 + (fbm(x / 6, y / 8, 5) - 0.5) * 0.5 + max(0.0, (y - yb + 14) / 14) * 0.5, lit=0)


# ─── Els mobles ─────────────────────────────────────────────────────────────

def banc(e):
    x0, x1, d, h = BANC
    z1 = ZB - 2
    z0 = z1 - d
    e.foscor('ombra', (x0 - 6, 0.3, z1), (x1 + 20, 0.3, z1), (x1 + 20, 0.3, z0 - 10), (x0 - 6, 0.3, z0 - 10),
             lambda s, t: 0.55 * min(1.0, t / 10 + 0.3))
    for lx in (x0 + 8, x1 - 12):                                        # les potes
        e.caixa('banc', lx, lx + 5, 0, h - 5, z0 + 4, z1 - 4, FUSTA, 2.6)
    e.caixa('banc', x0, x1, h - 5, h, z0, z1, FUSTA, 3.0,
            cares={'dalt': {'ramp': FUSTA, 'lvl': lambda s, t, P: veta(s, t, seed=33, base=3.6)},
                   'davant': {'ramp': FUSTA, 'lvl': lambda s, t, P: veta(s, t, seed=34, base=2.8)}})
    # la llança d'en Bonfill, recolzada a la paret al costat del banc
    e.cable('llanca', [(x1 + 12, 0, ZB - 12), (x1 + 4, 112, ZB - 3)], FUSTA, 4.4, gruix=3.0)
    e.cable('llanca', [(x1 + 4, 112, ZB - 3), (x1 + 3.4, 128, ZB - 2.5)], FERRO, 5.6, gruix=4.0)


def columna(e, cv):
    """La columna exempta: base, fust (un cilindre, amb la llum de les torxes de costat) i el capitell, que surt de
    la pantalla per dalt."""
    cx, cz, r = COLUMNA
    e.foscor('ombra', (cx - 6, 0.3, cz + 140), (cx + 34, 0.3, cz + 140), (cx + 28, 0.3, cz - 4), (cx - 10, 0.3, cz - 4),
             lambda s, t: 0.6 * max(0.0, 1 - t / 140) * max(0.0, 1 - abs(s - 20) / 22))
    e.caixa('columna', cx - r - 6, cx + r + 6, 0, 10, cz - r - 6, cz + r + 6, PEDRA, 3.0,
            cares={'dalt': {'ramp': PEDRA, 'lvl': 4.2}})
    e.caixa('columna', cx - r - 3, cx + r + 3, 10, 18, cz - r - 3, cz + r + 3, PEDRA, 3.4,
            cares={'dalt': {'ramp': PEDRA, 'lvl': 4.6}})
    # el fust: la llum ve de l'esquerra (les torxes)
    e.tub('columna', (cx, 18, cz), (cx, WALL_H, cz), r, PEDRA, 2.6, llum_dir=(-1.0, 0.1))


def faristol(e):
    """El faristol: un peu de fusta, el pupitre inclinat i, a sobre, el llibre de les entrades obert."""
    fx, fz, a = FARISTOL
    c, s_ = math.cos(a), math.sin(a)

    def G(lx, y, lz):
        return (fx + lx * c - lz * s_, y, fz + lx * s_ + lz * c)
    e.foscor('ombra', G(-26, 0.3, 30), G(36, 0.3, 30), G(36, 0.3, -20), G(-26, 0.3, -20),
             lambda s, t: 0.5 * max(0.0, 1 - math.hypot(s - 30, t - 26) / 34))
    e.caixa_girada('faristol', fx, fz, 30, 22, 5, a, FUSTA, 2.6)                 # el peu
    e.caixa_girada('faristol', fx, fz, 7, 7, 84, a, FUSTA, 3.0, y0=5)
    # el pupitre: inclinat cap a la sala (el cantó de davant més baix)
    hb, hd = 98, 84
    e.quad('faristol', G(-26, hb, 12), G(26, hb, 12), G(26, hd, -12), G(-26, hd, -12), ramp=FUSTA,
           lvl=lambda s, t, P: veta(s, t, seed=35, base=3.2), dues_cares=True)
    e.quad('faristol', G(-26, hd, -12), G(26, hd, -12), G(26, hd - 4, -12), G(-26, hd - 4, -12), ramp=FUSTA, lvl=2.6)
    # el llibre obert: les dues pàgines (una mica corbades), la tapa que sobresurt
    e.quad('llibre_tapa', G(-24, hb + 0.8, 11), G(24, hb + 0.8, 11), G(24, hd + 0.8, -11), G(-24, hd + 0.8, -11),
           ramp=FUSTA, lvl=1.6)


def _llibre_tex(ninots):
    """Les dues pàgines del llibre de les entrades, de cara (48×22: una unitat per píxel, la mida a què es veu): files
    de noms en tinta (ratlles grises, es llegeixen com a text) i, amb `ninots`, dos ninots a sota de la llista de la
    dreta (fra Tos, amb la boca oberta, i fra Silenci, amb la boca tapada)."""
    cv = Canvas(48, 22)
    for y in range(22):
        for x in range(48):
            v = 3.7 + abs(x - 23.5) / 24 * 0.7 - (1.4 if 23 <= x <= 24 else 0)
            v -= (1.0 if x in (0, 47) or y in (0, 21) else 0)
            cv.put(x, y, PERGAMI, v + (fbm(x / 4, y / 4, 51) - 0.5) * 0.5, lit=0)
    for pg, x0, files in ((0, 3, 5), (1, 27, 2)):
        for k in range(files):
            y = 3 + k * 3
            n = int(10 + hr(k, pg, 7) * 8)
            for i in range(n):
                if hr(k * 40 + i, pg, 8) > 0.3:
                    cv.put(x0 + i, y, TINTA, 2.6, lit=0)
    if ninots:
        for k, bx in enumerate((31, 40)):
            col = TINTA
            cv.put(bx, 10, col, 0.6, lit=0)                                  # el cap
            cv.put(bx - 1, 11, col, 0.6, lit=0)
            cv.put(bx + 1, 11, col, 0.6, lit=0)
            cv.put(bx, 12, col, 0.6, lit=0)
            for j in range(13, 17):
                cv.put(bx, j, col, 0.6, lit=0)                               # el cos
            cv.put(bx - 1, 14, col, 0.6, lit=0)
            cv.put(bx + 1, 14, col, 0.6, lit=0)
            cv.put(bx - 2, 15, col, 0.6, lit=0)
            cv.put(bx + 2, 15 if k == 0 else 12, col, 0.6, lit=0)            # (fra Silenci es tapa la boca)
            cv.put(bx - 1, 17, col, 0.6, lit=0)
            cv.put(bx + 1, 17, col, 0.6, lit=0)
            cv.put(bx - 1, 18, col, 0.6, lit=0)
            cv.put(bx + 1, 18, col, 0.6, lit=0)
            if k == 0:                                                       # la tos: ratlletes que surten de la boca
                cv.put(bx + 2, 10, col, 1.2, lit=0)
                cv.put(bx + 3, 9, col, 1.2, lit=0)
                cv.put(bx + 3, 11, col, 1.2, lit=0)
    return cv.img


def llibre(e, ninots):
    fx, fz, a = FARISTOL
    c, s_ = math.cos(a), math.sin(a)

    def G(lx, y, lz):
        return (fx + lx * c - lz * s_, y, fz + lx * s_ + lz * c)
    hb, hd = 98, 84
    e.quad('llibre', G(-23, hb + 2.2, 10), G(23, hb + 2.2, 10), G(23, hd + 2.2, -10), G(-23, hd + 2.2, -10),
           tex=(_llibre_tex(ninots), (0, 0, 48, 22)), dues_cares=True)


def torxes_suports(e, cv):
    """Els braços de ferro i els pals de les torxes (la flama és a part: `_flames`)."""
    for tx, ty in TORXES:
        e.cable('torxa', [(tx, ty - 20, ZB), (tx, ty - 4, ZB - 16), (tx, ty, ZB - 24)], FERRO, 2.6, gruix=2.4)
        e.cable('torxa', [(tx - 3, ty, ZB - 24), (tx + 3, ty, ZB - 24)], FERRO, 3.4, gruix=3.0)
        e.cable('torxa', [(tx - 1, ty - 18, ZB - 24), (tx, ty + 22, ZB - 24)], FUSTA, 2.4, gruix=4.2)
        e.cable('torxa', [(tx, ty + 18, ZB - 24), (tx, ty + 26, ZB - 24)], FUSTA, 1.2, gruix=6.4)    # la boca cremada


def _flama_torxa(cv, k, fase):
    tx, ty = TORXES[k]
    u, v, _ = CAM.projecta((tx, ty + 26, ZB - 24))
    s = CAM.escala((tx, 0, ZB - 24))
    flama(cv, u, v, 30 * s, 10 * s, fase, seed=k * 2.1)
    for i in range(4):                                                  # guspires que pugen
        f = (fase + hr(i, k, 3)) % 1.0
        gx = u + (hr(i, k, 4) - 0.5) * 10 * s + math.sin(f * 9 + i) * 2
        gy = v - 30 * s - f * 40 * s
        if f < 0.45:
            cv.put(gx, gy, FOC, 6.0 - f * 5, lit=0)


def _llum_oli(cv, fase):
    nx, ny = NINXOL
    u, v, _ = CAM.projecta((nx + 14, ny + 5, ZB + 5))
    flama(cv, u, v, 5, 2.4, fase, seed=4.2, k=1.1)
    cv.glow(u, v - 2, 16, (255, 196, 110), 0.35)


def _resplendors(cv, fase=0.0):
    for k, (tx, ty) in enumerate(TORXES):
        u, v, _ = CAM.projecta((tx, ty + 40, ZB - 24))
        bat = 1 + 0.08 * math.sin(2 * math.pi * fase * 2 + k * 2)
        cv.glow(u, v, 46 * bat, (255, 190, 100), 0.42)


# ─── Primer pla ─────────────────────────────────────────────────────────────

def primer_pla(e):
    """El pilar de l'entrada, a l'esquerra (a contrallum), i l'arc que en surt per dalt."""
    x0, x1, z0, z1 = PILAR
    e.caixa('davant', x0, x1, 0, WALL_H, z0, z1, PEDRA, 2.0,
            cares={'davant': {'ramp': PEDRA, 'lvl': lambda s, t, P: carreus(s, t, alt=34, ample=(62, 62), seed=12,
                                                                            base=1.6)},
                   'dreta': {'ramp': PEDRA, 'lvl': lambda s, t, P: carreus(s, t, alt=34, ample=(50, 50), seed=13,
                                                                           base=2.6)}})
    # l'arc: un intradós que surt del pilar cap a la dreta, per sobre de tot
    n = 14
    for i in range(n):
        a0, a1 = math.pi * i / n / 2, math.pi * (i + 1) / n / 2
        R = 300
        pa = (x1 + R - R * math.cos(a0), 236 + R * 0.5 * math.sin(a0))
        pb = (x1 + R - R * math.cos(a1), 236 + R * 0.5 * math.sin(a1))
        e.quad('davant', (pa[0], pa[1], z1), (pb[0], pb[1], z1), (pb[0], pb[1], z0), (pa[0], pa[1], z0), ramp=PEDRA,
               lvl=lambda s, t, P: carreus(P[0], t, alt=60, ample=(28, 28), seed=14, base=2.2), dues_cares=True)
        e.quad('davant', (pa[0], pa[1] + 70, z0), (pb[0], pb[1] + 70, z0), (pb[0], pb[1], z0), (pa[0], pa[1], z0),
               ramp=PEDRA, lvl=lambda s, t, P: carreus(P[0], P[1], alt=34, seed=15, base=1.6), dues_cares=True)


# ─── Composició ────────────────────────────────────────────────────────────

def escena(cv, estat):
    e = Escena(cv, CAM, LLUMS, ambient=AMBIENT)
    terra(e)
    porta(e, 'oberta' in estat)
    paret(e)
    # les ombres a terra: la foscor del peu de la paret, i el racó del fons
    e.foscor('ombra', (-700, 0.2, ZB), (XE, 0.2, ZB), (XE, 0.2, ZB - 40), (-700, 0.2, ZB - 40),
             lambda s, t: 0.35 * (1 - t / 40))
    e.foscor('ombra', (380, 0.2, ZB), (XE, 0.2, ZB), (XE, 0.2, 0), (380, 0.2, 0),
             lambda s, t: min(0.85, max(0.0, s / 420)))
    torxes_suports(e, cv)
    banc(e)
    faristol(e)
    llibre(e, 'ninots' in estat)
    columna(e, cv)
    primer_pla(e)
    e.silueta({'davant'}, k=0.5, col=(10, 6, 8))
    return e


@functools.lru_cache(maxsize=None)
def _render(estat=frozenset(), fase=0.0):
    """Tota la sala amb un estat ('ninots', 'oberta') i les flames a la `fase` donada."""
    cv = Canvas(light=LIGHT)
    e = escena(cv, estat)
    for k in range(len(TORXES)):
        _flama_torxa(cv, k, fase)
    _resplendors(cv, fase)
    _llum_oli(cv, fase)
    hud_negre(cv)
    for y in range(BOTTOM + 1, cv.h):
        for x in range(W):
            e.amo[y * W + x] = 0
    return cv.img, e


def _base():
    return _render(frozenset())[0]


def bg(cv):
    cv.img.paste(_base())
    cv.P = cv.img.load()


@functools.lru_cache(maxsize=None)
def _davant_img():
    img, e = _render(frozenset())
    out = Image.new('RGBA', img.size, (0, 0, 0, 0))
    src, dst = img.load(), out.load()
    ids = {i for i, s in enumerate(e.ids) if s == 'davant'}
    for y in range(BOTTOM + 1):
        for x in range(W):
            if e.amo[y * W + x] in ids:
                dst[x, y] = src[x, y]
    return out


def _decorat(estat):
    def draw(cv):
        img = _render(frozenset(estat))[0]
        cv.img.alpha_composite(sense(_diff(img, _base()), _davant_img()))
        cv.P = cv.img.load()
    return draw


PROPS = {
    'ninots': _decorat(('ninots',)),
    'porta_oberta': _decorat(('oberta',)),
}


# ─── Animacions ─────────────────────────────────────────────────────────────

def _frames_flames():
    """Les dues flames de les torxes i el seu resplendor, que bateguen (bucle de 12)."""
    base = _base()
    out = []
    n = 12
    for i in range(n):
        cv = Canvas(light=LIGHT, img=base.copy())
        # (es repinta la zona de les flames a partir del fons sense flames)
        for k, (tx, ty) in enumerate(TORXES):
            u, v, _ = CAM.projecta((tx, ty + 26, ZB - 24))
            s = CAM.escala((tx, 0, ZB - 24))
            x0, x1, y0, y1 = int(u - 60 * s), int(u + 60 * s), int(v - 90 * s), int(v + 60 * s)
            clean = _sense_flames().crop((x0, y0, x1, y1))
            cv.img.paste(clean, (x0, y0))
        cv.P = cv.img.load()
        nx, ny = NINXOL
        u, v, _ = CAM.projecta((nx + 14, ny + 5, ZB + 5))
        cv.img.paste(_sense_flames().crop((int(u) - 20, int(v) - 24, int(u) + 20, int(v) + 16)), (int(u) - 20, int(v) - 24))
        cv.P = cv.img.load()
        for k in range(len(TORXES)):
            _flama_torxa(cv, k, i / n)
        _resplendors(cv, i / n)
        _llum_oli(cv, i / n)
        out.append(sense(_diff(cv.img, base), _davant_img()))     # (el primer pla no es toca)
    return out


@functools.lru_cache(maxsize=None)
def _sense_flames():
    cv = Canvas(light=LIGHT)
    escena(cv, frozenset())
    return cv.img


ANIMS = {'flames': {'frames': _frames_flames, 'frameDuration': 90}}


# ─── Capes del davant ─────────────────────────────────────────────────────

def _amo(ids):
    def mask(x, y):
        _, e = _render(frozenset())
        return e.ids[e.amo[y * W + x]] in ids
    return mask


def _v(x, z):
    return _p(x, z)[1]


_FX, _FZ, _FA = FARISTOL
FRONT = [
    # el banc i la llança (contra la paret: hi passa per darrere qui hi és molt a prop)
    {'id': 'davant_banc', 'mask': _amo({'banc', 'llanca'}), 'baseline': _v(BANC[0], ZB - 2 - BANC[2]), 'zIndex': 20},
    {'id': 'davant_faristol', 'mask': _amo({'faristol', 'llibre', 'llibre_tapa'}),
     'baseline': _v(_FX + 11 * math.sin(_FA), _FZ - 11 * math.cos(_FA)), 'zIndex': 20, 'variants': ('ninots',)},
    {'id': 'davant_columna', 'mask': _amo({'columna'}), 'baseline': _v(COLUMNA[0], COLUMNA[1] - COLUMNA[2]),
     'zIndex': 20},
    {'id': 'davant', 'mask': _amo({'davant'}), 'baseline': 999, 'zIndex': 20},
]


# ─── Geometria (coordenades de sala) ─────────────────────────────────────────

def _escala_v(v):
    """L'escala d'un personatge amb els peus a la fila v (pitch 0: només depèn de v)."""
    return round((v - CY) / EYE_H, 3)


def _sota(pts, marge=6):
    return [_p(x, z) for x, z in pts]


def _geometria():
    x0, x1, ya = PORTA
    r = (x1 - x0) / 2
    top = ya + r
    porta_r = rect_de(*(CAM.projecta(P)[:2] for P in ((x0 - 4, top + 4, ZB), (x1 + 14, 0, ZB))))
    bx0, bx1, bd, bh = BANC
    banc_r = rect_de(*(CAM.projecta(P)[:2] for P in ((bx0, bh, ZB - 2 - bd), (bx1, 0, ZB - 2 - bd), (bx1, bh, ZB))))
    cx, cz, cr = COLUMNA
    col_r = rect_de(*(CAM.projecta(P)[:2] for P in ((cx - cr - 6, 0, cz - cr - 6), (cx + cr + 6, 0, cz - cr - 6),
                                                    (cx - cr, 330, cz))))
    torxes = [CAM.projecta((tx, ty + y, ZB - 24))[:2] for tx, ty in TORXES for y in (-20, 56)]
    fx, fz, a = FARISTOL
    c, s_ = math.cos(a), math.sin(a)

    def G(lx, y, lz):
        return CAM.projecta((fx + lx * c - lz * s_, y, fz + lx * s_ + lz * c))[:2]
    llibre_r = rect_de(G(-26, 100, 12), G(26, 100, 12), G(26, 82, -12), G(-26, 82, -12), pad=3)
    # el terra on es camina: del peu de la paret (sense el banc ni la base de la columna) fins on l'Iri fa ≈1,2;
    # a l'esquerra, fins al pilar del primer pla; a la dreta, fins on fa ≈0,7.
    peu = lambda x, dz=22: _p(x, ZB - dz)  # noqa: E731
    walk = [peu(-150), peu(bx0 - 8), _p(bx0 - 8, ZB - bd - 12), _p(bx1 + 16, ZB - bd - 12), peu(bx1 + 16),
            peu(400), (600, 246), (36, 246)]
    walk = [(max(0, min(W - 1, u)), min(246, v)) for u, v in walk]
    vs = [v for _, v in walk]
    forats = [[_p(cx + cr * 1.5 * math.cos(k * math.pi / 4), cz + cr * 1.2 * math.sin(k * math.pi / 4)) for k in range(8)],
              [G2 for G2 in (_p(*_gp(-20, 26)), _p(*_gp(24, 26)), _p(*_gp(24, -18)), _p(*_gp(-20, -18)))]]
    things = {
        'porta_ala': {'rect': porta_r, 'walk': _p((x0 + x1) / 2, ZB - 34)},
        'banc': {'rect': banc_r, 'walk': _p((bx0 + bx1) / 2 - 20, ZB - bd - 30)},
        'columna': {'rect': col_r, 'walk': _p(cx - 40, cz - 30)},
        'torxes': {'rect': rect_de(*torxes, pad=8), 'walk': _p(TORXES[1][0] - 40, ZB - 40)},
        'llibre_entrades': {'rect': llibre_r, 'walk': _p(fx + 34, fz - 34)},
    }
    lt = TORXES[1]
    return {
        'things': things,
        # l'Iri al mig, la Vet (disfressada) un pas darrere seu, i en Bonfill al banc, amb la llança
        'spawns': {'iri': _p(70, 352), 'vet': _p(0, 392), 'bonfill': _p(BANC[0] + 46, ZB - BANC[2] - 26)},
        'walkable': walk,
        'forats': forats,
        'floorSquash': 0.42,
        'regions': [{'id': 'perspectiva', 'active': True, 'scaleEnabled': True, 'scaleWalkSpeed': True,
                     'scaleTop': _escala_v(min(vs) - 2), 'scaleBottom': _escala_v(max(vs) + 2),
                     'points': [(0, min(vs) - 2), (W - 1, min(vs) - 2), (W - 1, max(vs) + 2), (0, max(vs) + 2)]}],
        # L'ombra de contacte: la torxa de la dreta, que és al mig de la sala (l'ombra s'allarga cap a fora).
        'characterShadow': {'enabled': True, 'color': '#0a0506', 'alpha': 0.5, 'squash': 0.4, 'core': 0.6,
                            'light': {'x': _p(lt[0], ZB - 24)[0], 'y': _p(lt[0], ZB - 24)[1], 'stretch': 0.8,
                                      'reach': 200}},
        # La llum sobre els personatges: fosc i càlid, i les dues torxes, taronja.
        'characterLights': {
            'ambient': '#5e4c4c',
            'lights': [llum_personatge(CAM, L.pos, 330, (255, 176, 96), 0.75) for L in LLUMS],
        },
    }


def _gp(lx, lz):
    """Un punt del terra al voltant del faristol (coordenades locals girades) → (x, z) del món."""
    fx, fz, a = FARISTOL
    c, s_ = math.cos(a), math.sin(a)
    return fx + lx * c - lz * s_, fz + lx * s_ + lz * c


GEOMETRIA = _geometria()
