"""
L'scriptorium (acte 3, mitjanit; la Vet). Art definitiu, a 1×.

La sala dels copistes, vista de biaix cap a la cantonada del fons a l'esquerra i una mica des de dalt:
  - a la paret del fons, els **finestrals** alts i estrets, foscos, amb una mica de lluna blava que entra en feixos
    pel terra; entre els finestrals, la **porta capitular**, ferrada (bandes i claus de ferro): l'arxiu;
  - a la paret de l'esquerra, en escorç, la **porta del passadís** (per on entren; l'Iri hi espera);
  - els **faristols** dels copistes, girats, cadascun amb la seva espelma, el pergamí a mig copiar i el tinter (en
    Gombau i l'Arnulf hi són drets); l'arca amb les **còpies** de l'ordre, apilades;
  - davant a la dreta, el **faristol d'en Sunifred**, buit, amb el **pergamí** en blanc, i al costat, en un canelobre
    de ferro, l'**espelma de les hores**: gruixuda, amb ratlles, i una de vermella (l'únic vermell viu de la sala);
  - primer pla: l'armari dels llibres, a la dreta, i un escambell a baix a l'esquerra, a contrallum.
Decorats: `flama_hores` (la flama de l'espelma de les hores, animada, mentre és sencera), `espelma_retallada` (animat) (l'espelma més curta: la flama ja toca la ratlla vermella; el tros tallat, al plat) i `porta_oberta` (la porta capitular
oberta, i l'arxiu fosc a darrere). Animacions: les flames de les espelmes (`espelmes`).
"""
import functools
import math

from PIL import Image

import hd640  # noqa: F401  (abans de cap hd.rooms: posa la llibreria a 640×360)

from hd.pix import Canvas, Light
from hd640.rooms.nit_comu import (W, BOTTOM, PEDRA, LLOSA, FUSTA, FERRO, CERA, VERMELL, PERGAMI, TINTA, LLUNA,
                                  fbm, hr, carreus, lloses, taulons, veta, flama, hud_negre, sense, _diff,
                                  llum_personatge, rect_de, ombra_terra, marca)
from hd640.tres_d import Camera, Escena, Llum

# ─── La càmera i el món ──────────────────────────────────────────────────────
EYE_H, F, CY, YAW = 180, 380, 30, -0.2
CAM = Camera(pos=(20, EYE_H, 0), yaw=YAW, pitch=0.0, f=F, centre=(320, CY))

ZB = 520                                            # la paret del fons
XL = -330                                           # la paret de l'esquerra
WALL_H = 460
FINESTRALS = ((-250, -206), (-40, 4), (230, 274))   # x0, x1 de cada finestral (paret del fons)
FIN_Y = (104, 196)                                  # l'ampit i l'arrencada de l'arc
CAPITULAR = (70, 152, 118)                          # x0, x1, arrencada de l'arc (porta del fons)
PASSADIS = (360, 432, 112)                          # z0, z1, arrencada de l'arc (porta de la paret de l'esquerra)
# faristols: x, z, angle (girat al voltant de la vertical), si és el d'en Sunifred
FARISTOLS = ((-150, 420, 0.34), (-10, 452, -0.12))
SUNIFRED = (120, 386, -0.42)
ESPELMA = (196, 446)                                # el canelobre de l'espelma de les hores: x, z
ARCA = (-260, 494, 70, 30, 34)                      # l'arca de les còpies: cx, cz, llarg, fons, alt
ARMARI = (156, 196, 236, 268)                       # l'armari del primer pla: x0, x1, z0, z1

LIGHT = Light(ambient=0.0, vignette=(60, 30), floor_fade=None)
LIGHT.width = W
AMBIENT = -2.2


def _girat(cx, cz, a):
    c, s = math.cos(a), math.sin(a)
    return lambda lx, lz, y=0.0: (cx + lx * c - lz * s, y, cz + lx * s + lz * c)


def _espelma_faristol(x, z, a):
    """On és la flama de l'espelma d'un faristol (al braç de l'esquerra, damunt el pupitre)."""
    return _girat(x, z, a)(-24, 8, 86)


HC = 70                                             # l'alçada del plat del canelobre
ALT_ESPELMA = 34                                    # l'espelma de les hores, sencera (unitats)
TALL = 12                                           # el que en talla la Vet
LLUMS = ([Llum(_espelma_faristol(*f), 400, 4.4, power=1.25) for f in FARISTOLS] +
         [Llum(_espelma_faristol(*SUNIFRED[:3]), 400, 4.0, power=1.25),
          Llum((ESPELMA[0], HC + ALT_ESPELMA + 6, ESPELMA[1]), 340, 3.6, power=1.25)])


def _p(x, z, y=0.0):
    u, v, _ = CAM.projecta((x, y, z))
    return round(u), round(v)


def _arc(s, y, ample, ya):
    """Dins una obertura amb arc de mig punt? `s` des del cantó, `y` del món."""
    r = ample / 2
    if y <= ya:
        return 0 <= s <= ample
    return (s - r) ** 2 + (y - ya) ** 2 <= r * r


# ─── Parets, finestrals i portes ────────────────────────────────────────────

def _dovelles(x, y, x0, x1, ya, base):
    """Les dovelles d'un arc (nivell) o None si (x, y) no hi és."""
    r = (x1 - x0) / 2
    cx = x0 + r
    d = math.hypot(x - cx, max(0.0, y - ya))
    if y > ya - 1 and r - 1 < d < r + 16:
        a = math.atan2(y - ya, x - cx)
        k = int(a / (math.pi / 9))
        v = base + 0.8 + (hr(k, int(x0), 3) - 0.5) * 0.6 + (fbm(x / 6, y / 6, 4) - 0.5) * 0.5
        if a - k * math.pi / 9 < 0.04 or d > r + 14.8:
            return v - 1.8
        return v
    return None


def parets(e):
    def fons_lvl(s, t, P):
        x, y = P[0], P[1]
        for x0, x1 in FINESTRALS:
            v = _dovelles(x, y, x0, x1, FIN_Y[1], 2.4)
            if v is not None:
                return v
            if FIN_Y[0] - 8 <= y < FIN_Y[0] and x0 - 8 <= x <= x1 + 8:          # l'ampit
                return 3.6 - (FIN_Y[0] - y) * 0.15
        x0, x1, ya = CAPITULAR
        v = _dovelles(x, y, x0 - 6, x1 + 6, ya, 2.6)
        if v is not None:
            return v
        return carreus(x + 600, WALL_H - y, alt=30, ample=(46, 74), seed=31, base=2.6)

    def forma(s, t):
        x, y = s + XL, WALL_H - t
        if _arc(x - CAPITULAR[0], y, CAPITULAR[1] - CAPITULAR[0], CAPITULAR[2]):
            return False
        return not any(_arc(x - x0, y - FIN_Y[0], x1 - x0, FIN_Y[1] - FIN_Y[0]) and y >= FIN_Y[0]
                       for x0, x1 in FINESTRALS)
    e.quad('paret', (XL, WALL_H, ZB), (700, WALL_H, ZB), (700, 0, ZB), (XL, 0, ZB), ramp=PEDRA, lvl=fons_lvl,
           forma=forma)
    z0, z1, ya = PASSADIS

    def forma_esq(s, t):
        z, y = ZB - s, WALL_H - t
        return not _arc(z - z0, y, z1 - z0, ya)

    def esq_lvl(s, t, P):
        v = _dovelles(P[2], P[1], z0 - 6, z1 + 6, ya, 2.4)
        if v is not None:
            return v
        return carreus(s + 300, t, alt=30, ample=(46, 74), seed=32, base=2.2)
    e.quad('paret_esq', (XL, WALL_H, ZB), (XL, WALL_H, -60), (XL, 0, -60), (XL, 0, ZB), ramp=PEDRA, lvl=esq_lvl,
           forma=forma_esq, dues_cares=True)


def finestrals(e):
    """Dins cada finestral: l'esqueixada (els costats que s'eixamplen cap a dins) i el vidre fosc, blau de lluna."""
    for k, (x0, x1) in enumerate(FINESTRALS):
        ya = FIN_Y[1]
        r = (x1 - x0) / 2
        zf = ZB + 26
        e.quad('finestral', (x0 + 10, ya + r, zf), (x1 - 10, ya + r, zf), (x1 - 10, FIN_Y[0] + 10, zf),
               (x0 + 10, FIN_Y[0] + 10, zf), ramp=LLUNA,
               lvl=lambda s, t, P, k=k: 3.4 - t * 0.012 + (fbm(s / 4, t / 6, 60 + k) - 0.5) * 0.8
               + (1.4 if abs(s - (x1 - x0 - 20) / 2) < 1.2 or int(t) % 22 == 0 else 0) * -1,
               forma=lambda s, t, w=x1 - x0 - 20, h=ya + r - FIN_Y[0] - 10: _arc(s, h - t, w, h - w / 2))
        # l'esqueixada: els costats i l'ampit de dins, inclinats
        e.quad('finestral', (x0, ya, ZB), (x0 + 10, ya, zf), (x0 + 10, FIN_Y[0] + 10, zf), (x0, FIN_Y[0], ZB),
               ramp=PEDRA, lvl=2.6, dues_cares=True)
        e.quad('finestral', (x1 - 10, ya, zf), (x1, ya, ZB), (x1, FIN_Y[0], ZB), (x1 - 10, FIN_Y[0] + 10, zf),
               ramp=PEDRA, lvl=1.6, dues_cares=True)
        e.quad('finestral', (x0, FIN_Y[0], ZB), (x1, FIN_Y[0], ZB), (x1 - 10, FIN_Y[0] + 10, zf),
               (x0 + 10, FIN_Y[0] + 10, zf), ramp=PEDRA, lvl=3.0, dues_cares=True)


def lluna(cv):
    """Els feixos de lluna: entren pels finestrals (la lluna és alta, darrere la paret), baixen cap a nosaltres i fan
    una taca blava a terra, de la forma del finestral."""
    for k, (x0, x1) in enumerate(FINESTRALS):
        d0, d1 = 40, 150                                                # on cau la taca: de l'ampit al cap de l'arc
        taca = [_p(x0 + 10, ZB - d0), _p(x1 - 10, ZB - d0), _p(x1 - 4, ZB - d1), _p(x0 + 16, ZB - d1)]
        fin = [CAM.projecta((x, y, ZB + 20))[:2] for x in (x0 + 10, x1 - 10) for y in (FIN_Y[0] + 10, FIN_Y[1] + 14)]
        _taca(cv, _envolupant(fin + taca), (120, 150, 210), 0.09)
        _taca(cv, taca, (110, 140, 200), 0.2)


def _envolupant(pts):
    """L'envolupant convexa d'uns punts de pantalla (en ordre)."""
    pts = sorted(set((round(x, 1), round(y, 1)) for x, y in pts))

    def cross(o, a, b):
        return (a[0] - o[0]) * (b[1] - o[1]) - (a[1] - o[1]) * (b[0] - o[0])
    lo, hi = [], []
    for p in pts:
        while len(lo) >= 2 and cross(lo[-2], lo[-1], p) <= 0:
            lo.pop()
        lo.append(p)
    for p in reversed(pts):
        while len(hi) >= 2 and cross(hi[-2], hi[-1], p) <= 0:
            hi.pop()
        hi.append(p)
    return lo[:-1] + hi[:-1]


def _taca(cv, poly, col, k):
    ys = [p[1] for p in poly]
    for y in range(int(min(ys)), int(max(ys)) + 1):
        xs = []
        for (xa, ya), (xb, yb) in zip(poly, poly[1:] + poly[:1]):
            if (ya <= y + 0.5 < yb) or (yb <= y + 0.5 < ya):
                xs.append(xa + (y + 0.5 - ya) * (xb - xa) / (yb - ya))
        xs.sort()
        for a, b in zip(xs[::2], xs[1::2]):
            cv.tint(math.ceil(a), y, math.floor(b), y, col, k)


def porta_capitular(e, oberta):
    """La porta del fons: dins l'arc, la fulla de taulons ferrada (bandes, frontisses llargues i claus) i l'anella.
    Oberta: la fulla girada cap endins i, darrere, l'arxiu fosc amb els prestatges i una mica de llum."""
    x0, x1, ya = CAPITULAR
    r = (x1 - x0) / 2
    top = ya + r
    zf = ZB + 14
    # darrere: l'arxiu (prestatges foscos), només es veu amb la porta oberta
    e.quad('arxiu', (x0 - 40, top + 30, zf + 200), (x1 + 40, top + 30, zf + 200), (x1 + 40, 0, zf + 200),
           (x0 - 40, 0, zf + 200), ramp=FUSTA,
           lvl=lambda s, t, P: -1.4 + (1.2 if int(t) % 30 < 3 else 0) + (hr(int(s / 8), int(t / 30), 9) - 0.5) * 1.6)
    e.quad('arxiu', (x0 - 40, 0, zf + 200), (x1 + 40, 0, zf + 200), (x1 + 40, 0, zf), (x0 - 40, 0, zf), ramp=LLOSA,
           lvl=lambda s, t, P: lloses(P[0], P[2], seed=33, base=-0.6))
    e.quad('porta_brancal', (x0, top, ZB), (x0, top, zf), (x0, 0, zf), (x0, 0, ZB), ramp=PEDRA, lvl=2.4)
    e.quad('porta_brancal', (x1, top, zf), (x1, top, ZB), (x1, 0, ZB), (x1, 0, zf), ramp=PEDRA, lvl=2.0)
    ample = x1 - x0

    def forma(s, t):
        return _arc(s, top - t, ample, ya)
    if oberta:
        a = 1.2
        c, sn = math.cos(a), math.sin(a)

        def Q(lx, y):
            return (x1 - lx * c, y, zf + lx * sn)
        e.quad('porta_fulla', Q(ample, top), Q(0, top), Q(0, 0), Q(ample, 0), ramp=FUSTA,
               lvl=lambda s, t, P: taulons(s, t, 14, seed=34, base=2.4), forma=forma, dues_cares=True)
        return
    e.quad('porta_fulla', (x0, top, zf), (x1, top, zf), (x1, 0, zf), (x0, 0, zf), ramp=FUSTA,
           lvl=lambda s, t, P: taulons(s, t, 14, seed=34, base=2.6), forma=forma)
    zb = zf - 0.6

    def ferro(s, t, P):
        return 3.0 + (0.9 if t < 1.0 else 0) + (1.6 if int(s) % 10 in (4, 5) and 1.2 < t < 3.8 else 0)
    for yb in (18, 62, 104):                                            # les frontisses llargues, ben ferrades
        e.quad('porta_ferro', (x0 + 2, yb + 5, zb), (x1 - 2, yb + 5, zb), (x1 - 2, yb, zb), (x0 + 2, yb, zb),
               ramp=FERRO, lvl=ferro)
    for k in range(5):                                                  # els claus
        for j in range(7):
            sx = x0 + 7 + j * (ample - 14) / 6
            sy = 36 + k * 14
            if sy > 140 or not _arc(sx - x0, sy, ample, ya):
                continue
            e.quad('porta_ferro', (sx - 1.2, sy + 1.2, zb), (sx + 1.2, sy + 1.2, zb), (sx + 1.2, sy - 1.2, zb),
                   (sx - 1.2, sy - 1.2, zb), ramp=FERRO, lvl=lambda s, t, P: 4.4 - s * 0.8)
    e.quad('porta_ferro', (x0 + 12, 86, zb), (x0 + 24, 86, zb), (x0 + 24, 74, zb), (x0 + 12, 74, zb), ramp=FERRO,
           lvl=lambda s, t, P: 4.8 - math.hypot(s - 6, t - 6) * 0.4,
           forma=lambda s, t: 4.0 < math.hypot(s - 6, t - 6) < 6.2)
    e.caixa('porta_ferro', x0 + 14, x0 + 22, 84, 96, zb - 2, zb, FERRO, 3.0)        # el pany


def porta_passadis(e):
    """La porta del passadís, a la paret de l'esquerra: oberta (per aquí entren i surten), amb la fulla girada contra
    la paret i un passadís fosc a darrere, amb una mica de llum d'una torxa llunyana."""
    z0, z1, ya = PASSADIS
    r = (z1 - z0) / 2
    top = ya + r
    xf = XL - 16
    e.quad('passadis', (xf - 160, top + 20, z1 + 40), (xf - 160, top + 20, z0 - 40), (xf - 160, 0, z0 - 40),
           (xf - 160, 0, z1 + 40), ramp=PEDRA, lvl=lambda s, t, P: carreus(s, t, alt=24, seed=35, base=0.0),
           dues_cares=True)
    e.quad('passadis', (xf - 160, 0, z1 + 40), (xf - 160, 0, z0 - 40), (xf, 0, z0 - 40), (xf, 0, z1 + 40),
           ramp=LLOSA, lvl=lambda s, t, P: lloses(P[0], P[2], seed=36, base=0.6 + s / 160), dues_cares=True)
    e.quad('passadis', (xf, top, z0), (XL, top, z0), (XL, 0, z0), (xf, 0, z0), ramp=PEDRA, lvl=2.0, dues_cares=True)
    e.quad('passadis', (xf, top, z1), (XL, top, z1), (XL, 0, z1), (xf, 0, z1), ramp=PEDRA, lvl=2.6, dues_cares=True)


def arca(e, cv):
    """L'arca de roure contra la paret, amb les còpies de l'ordre apilades a sobre (pergamins enrotllats i plecs)."""
    cx, cz, ll, fo, h = ARCA
    e.foscor('ombra', (cx - ll / 2 - 4, 0.3, cz + fo / 2), (cx + ll / 2 + 18, 0.3, cz + fo / 2),
             (cx + ll / 2 + 18, 0.3, cz - fo / 2 - 14), (cx - ll / 2 - 4, 0.3, cz - fo / 2 - 14), lambda s, t: 0.5)
    e.caixa('arca', cx - ll / 2, cx + ll / 2, 0, h, cz - fo / 2, cz + fo / 2, FUSTA, 2.8,
            cares={'davant': {'ramp': FUSTA, 'lvl': lambda s, t, P: veta(s, t, seed=37, base=2.8)
                              + (1.4 if 2 < t < 5 or abs(s - ll / 2) < 3 else 0)},
                   'dalt': {'ramp': FUSTA, 'lvl': lambda s, t, P: veta(s, t, seed=38, base=3.4)}})
    for k in range(5):                                                  # els plecs de pergamí, apilats i torts
        y = h + k * 2.4
        dx = (hr(k, 1, 5) - 0.5) * 6
        e.caixa('copies', cx - 22 + dx, cx + 14 + dx, y, y + 2.2, cz - 10, cz + 10, PERGAMI, 3.6 - k * 0.1,
                cares={'dalt': {'ramp': PERGAMI, 'lvl': lambda s, t, P: 4.4 + (-1.4 if int(t) % 3 == 0 and s > 4 else 0)},
                       'davant': {'ramp': PERGAMI, 'lvl': 3.0}})
    for k, (lx, lz) in enumerate(((22, -4), (26, 6), (20, 8))):          # i tres rotlles
        e.cable('copies', [(cx + lx - 2, h + 3 + k * 5, cz + lz - 12), (cx + lx + 2, h + 3 + k * 5, cz + lz + 10)],
                PERGAMI, 3.8, gruix=5.0)
    # el segell vermell d'un dels plecs (l'ordre és segellada)
    u, v, _ = CAM.projecta((cx - 4, h + 12.5, cz - 10))
    cv.disc(u, v, 2.2, 1.6, VERMELL, 4.6, lit=0)


HB, HD = 74, 60                                     # el pupitre: el cantó de darrere i el de davant


def _pagina(blanc, seed):
    """Un full damunt el pupitre (de cara, 40×30 = una unitat per píxel): copiat a mig fer o en blanc."""
    cv = Canvas(40, 30)
    for y in range(30):
        for x in range(40):
            v = 3.9 - (1.0 if x in (0, 39) or y in (0, 29) else 0) + (fbm(x / 4, y / 4, seed) - 0.5) * 0.5
            cv.put(x, y, PERGAMI, v, lit=0)
    if not blanc:
        for k in range(6):
            n = 26 if k < 5 else 12
            for i in range(n):
                if hr(i, k, seed) > 0.25:
                    cv.put(6 + i, 4 + k * 3, TINTA, 2.4, lit=0)
        cv.rect(4, 4, 7, 8, VERMELL, 3.6, lit=0)                        # la caplletra, en vermell
    return cv.img


def faristol(e, cv, x, z, a, sid, blanc=False, seed=0):
    """Un faristol de copista: el peu en creu, el pal, el pupitre inclinat amb el full, el tinter i la ploma, i
    l'espelma al braç de l'esquerra."""
    g = _girat(x, z, a)
    e.foscor('ombra', g(-34, 30, 0.3), g(40, 30, 0.3), g(40, -26, 0.3), g(-34, -26, 0.3),
             lambda s, t: 0.5 * max(0.0, 1 - math.hypot(s - 37, t - 28) / 40))
    e.caixa_girada(sid, x, z, 40, 5, 5, a, FUSTA, 2.4)
    e.caixa_girada(sid, x, z, 5, 36, 5, a, FUSTA, 2.6)
    e.caixa_girada(sid, x, z, 7, 7, 52, a, FUSTA, 3.0, y0=5)
    hb, hd = HB, HD
    e.quad(sid, g(-27, 13, hb), g(27, 13, hb), g(27, -13, hd), g(-27, -13, hd), ramp=FUSTA,
           lvl=lambda s, t, P: veta(s, t, seed=39 + seed, base=3.2), dues_cares=True)
    e.quad(sid, g(-27, -13, hd), g(27, -13, hd), g(27, -13, hd - 5), g(-27, -13, hd - 5), ramp=FUSTA, lvl=2.6)
    e.quad(sid, g(-20, 11, hb + 0.8), g(20, 11, hb + 0.8), g(20, -11, hd + 0.8), g(-20, -11, hd + 0.8),
           tex=(_pagina(blanc, 70 + seed), (0, 0, 40, 30)), dues_cares=True)
    marca(e, sid, lambda: _detalls_faristol(e, cv, x, z, a, sid))


def _detalls_faristol(e, cv, x, z, a, sid):
    """El tinter (una banya) i la ploma, a la dreta del pupitre; el braç de l'espelma i l'espelma, a l'esquerra."""
    g = _girat(x, z, a)
    hb, hd = HB, HD
    X, Y, Z = g(24, 11, hb + 0.5)
    u, v, _ = CAM.projecta((X, Y, Z))
    s = CAM.escala((X, 0, Z))
    cv.disc(u, v - 3 * s, 3 * s, 4 * s, TINTA, lambda nx, ny: 2.0 - nx * 0.8, lit=0)
    cv.line(u + 1, v - 6 * s, u + 7 * s, v - 18 * s, PERGAMI, 4.6, lit=0)
    # el braç de l'espelma i l'espelma
    fx, fy, fz = _espelma_faristol(x, z, a)
    e.cable(sid, [g(-27, 0, hd + 4), g(-24, 8, fy - 13)], FERRO, 3.0, gruix=1.8)
    u, v, _ = CAM.projecta((fx, fy - 13, fz))
    s = CAM.escala((fx, 0, fz))
    cv.disc(u, v, 4 * s, 1.4 * s, FERRO, 3.4, lit=0)
    for j in range(int(12 * s)):
        for i in range(-1, 2):
            cv.put(u + i, v - 1 - j, CERA, 4.4 + i * -0.8, lit=0)


def espelma_hores(e, cv, retallada):
    """El canelobre de ferro i l'espelma de les hores: gruixuda, de cera clara, amb una ratlla per hora (fosques) i
    una de vermella (l'hora de matines). Retallada: més curta, i el tros tallat al plat."""
    x, z = ESPELMA
    hc = HC
    e.foscor('ombra', (x - 14, 0.3, z + 16), (x + 26, 0.3, z + 16), (x + 26, 0.3, z - 20), (x - 14, 0.3, z - 20),
             lambda s, t: 0.5 * max(0.0, 1 - math.hypot(s - 14, t - 18) / 20))
    for k in range(3):                                                  # les tres potes
        a = k * 2 * math.pi / 3 + 0.4
        e.cable('canelobre', [(x + 12 * math.cos(a), 0, z + 12 * math.sin(a)), (x, 16, z)], FERRO, 2.8, gruix=2.0)
    e.cable('canelobre', [(x, 16, z), (x, hc, z)], FERRO, 3.2, gruix=2.6)
    u, v, _ = CAM.projecta((x, hc, z))
    s = CAM.escala((x, 0, z))
    cv.disc(u, v, 10 * s, 3 * s, FERRO, lambda nx, ny: 3.6 - ny * 1.4, lit=0)        # el plat
    alt = ALT_ESPELMA - (TALL if retallada else 0)
    r = 5.0 * s
    top = v - alt * s
    for j in range(int(alt * s)):
        y = v - 1 - j
        hora = (j / s) % 6 < 0.9
        vermella = 19.6 < j / s < 21.4
        for i in range(int(-r), int(r) + 1):
            nx = i / max(1, r)
            lvl = 4.8 - nx * 1.8 + (1.0 if nx < -0.5 else 0)
            if vermella:
                cv.put(u + i, y, VERMELL, lvl, lit=0)
            elif hora:
                cv.put(u + i, y, CERA, lvl - 2.6, lit=0)
            else:
                cv.put(u + i, y, CERA, lvl, lit=0)
    cv.disc(u, top, r, 1.6 * s, CERA, 6.0, lit=0)
    cv.put(u, top - 1, TINTA, 1.0, lit=0)
    if retallada:                                                       # el tros tallat, ajagut al plat
        for j in range(int(TALL * s)):
            for i in range(int(-r * 0.9), int(r * 0.9) + 1):
                cv.put(u + 6 * s + j * 0.9, v - 2 * s + i * 0.5, CERA, 4.2 - i * 0.2, lit=0)


def _flama_espelma(cv, pos, fase, seed, k=1.0):
    u, v, _ = CAM.projecta(pos)
    s = CAM.escala((pos[0], 0, pos[2]))
    flama(cv, u, v, 9 * s * k, 3.6 * s * k, fase, seed=seed, k=1.1)
    cv.glow(u, v - 4 * s, 26 * s * k, (255, 196, 110), 0.38)


def _punts_flama(retallada=False):
    pts = [(_espelma_faristol(*f), 1.0) for f in FARISTOLS] + [(_espelma_faristol(*SUNIFRED), 1.0)]
    x, z = ESPELMA
    alt = ALT_ESPELMA - (TALL if retallada else 0)
    pts.append(((x, HC + alt + 1, z), 1.3))
    return pts


def _flames(cv, fase, retallada=False):
    for k, ((fx, fy, fz), sz) in enumerate(_punts_flama(retallada)):
        _flama_espelma(cv, (fx, fy, fz), (fase + k * 0.31) % 1.0, k * 1.7, sz)


def primer_pla(e, cv):
    """L'armari dels llibres, a la dreta (tallat per la vora), i un escambell a baix a l'esquerra."""
    x0, x1, z0, z1 = ARMARI
    e.caixa('davant', x0, x1, 0, WALL_H, z0, z1, FUSTA, 1.8,
            cares={'esquerra': {'ramp': FUSTA, 'lvl': lambda s, t, P: taulons(s, t, 12, seed=41, base=2.4)
                                - (1.4 if int(P[1]) % 54 < 4 else 0)},
                   'davant': {'ramp': FUSTA, 'lvl': lambda s, t, P: veta(t, s, seed=42, base=1.8)}})
    e.caixa('davant', -150, -118, 0, 30, 226, 254, FUSTA, 2.0,
            cares={'dalt': {'ramp': FUSTA, 'lvl': lambda s, t, P: veta(s, t, seed=43, base=2.8)}})


# ─── Composició ────────────────────────────────────────────────────────────

def escena(cv, estat):
    e = Escena(cv, CAM, LLUMS, ambient=AMBIENT)
    porta_passadis(e)
    e.quad('terra', (XL - 2, 0, ZB), (700, 0, ZB), (700, 0, -60), (XL - 2, 0, -60), ramp=LLOSA,
           lvl=lambda s, t, P: lloses(P[0], P[2], mida=(44, 40), seed=19, base=2.2))
    finestrals(e)
    porta_capitular(e, 'oberta' in estat)
    parets(e)
    lluna(cv)
    e.foscor('ombra', (XL, 0.2, ZB), (700, 0.2, ZB), (700, 0.2, ZB - 50), (XL, 0.2, ZB - 50),
             lambda s, t: 0.35 * (1 - t / 50))
    arca(e, cv)
    faristols = sorted([(f, 'faristols', False, i) for i, f in enumerate(FARISTOLS)] +
                       [(SUNIFRED, 'faristol_sunifred', True, 9)], key=lambda q: -q[0][1])
    for (x, z, a), sid, blanc, seed in faristols:
        faristol(e, cv, x, z, a, sid, blanc=blanc, seed=seed)
    marca(e, 'canelobre', lambda: espelma_hores(e, cv, 'retallada' in estat))
    marca(e, 'davant', lambda: primer_pla(e, cv))
    e.silueta({'davant'}, k=0.5, col=(8, 6, 10))
    return e


@functools.lru_cache(maxsize=None)
def _render(estat=frozenset(), fase=0.0, foc=True):
    cv = Canvas(light=LIGHT)
    e = escena(cv, estat)
    if foc:
        _flames(cv, fase, 'retallada' in estat)
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
    'espelma_retallada': _decorat(('retallada',)),
    'porta_oberta': _decorat(('oberta',)),
}


# ─── Animacions ─────────────────────────────────────────────────────────────

def _frames_espelmes():
    """Les flames de les espelmes dels faristols, en bucle. La de l'espelma de les hores va a part (`flama_hores`
    i `espelma_retallada`), perquè amb l'espelma retallada és més avall."""
    base = _base()
    net = _render(frozenset(), 0.0, False)[0]
    out = []
    n = 12
    pts = _punts_flama()[:-1]
    for i in range(n):
        cv = Canvas(light=LIGHT, img=base.copy())
        for (fx, fy, fz), _ in pts:
            u, v, _ = CAM.projecta((fx, fy, fz))
            box = (int(u) - 30, int(v) - 34, int(u) + 30, int(v) + 22)
            cv.img.paste(net.crop(box), box[:2])
        cv.P = cv.img.load()
        for k, ((fx, fy, fz), sz) in enumerate(pts):
            _flama_espelma(cv, (fx, fy, fz), (i / n + k * 0.31) % 1.0, k * 1.7, sz)
        out.append(sense(_diff(cv.img, base), _davant_img()))
    return out


def _frames_hores(retallada):
    """La flama de l'espelma de les hores, en bucle: sencera (decorat `flama_hores`, mentre els canonges hi són) o
    retallada (l'animació del decorat `espelma_retallada`, que en porta l'espelma més curta)."""
    base = _base()
    estat = frozenset(('retallada',)) if retallada else frozenset()
    fix = _render(estat)[0]
    net = _render(estat, 0.0, False)[0]
    (fx, fy, fz), sz = _punts_flama(retallada)[-1]
    u, v, _ = CAM.projecta((fx, fy, fz))
    box = (int(u) - 34, int(v) - 40, int(u) + 34, int(v) + 24)
    out = []
    n = 12
    k = len(_punts_flama()) - 1
    for i in range(n):
        cv = Canvas(light=LIGHT, img=fix.copy())
        cv.img.paste(net.crop(box), box[:2])
        cv.P = cv.img.load()
        _flama_espelma(cv, (fx, fy, fz), (i / n + k * 0.31) % 1.0, k * 1.7, sz)
        out.append(sense(_diff(cv.img, base), _davant_img()))
    return out


ANIMS = {'espelmes': {'frames': _frames_espelmes, 'frameDuration': 110},
         'flama_hores': {'frames': lambda: _frames_hores(False), 'frameDuration': 110},
         'espelma_retallada': {'frames': lambda: _frames_hores(True), 'frameDuration': 110}}


# ─── Capes del davant ─────────────────────────────────────────────────────

def _amo(ids):
    def mask(x, y):
        _, e = _render(frozenset())
        return e.ids[e.amo[y * W + x]] in ids
    return mask


def _baseline_faristol(x, z, a):
    g = _girat(x, z, a)
    return max(_p(*[g(lx, lz)[k] for k in (0, 2)])[1] for lx, lz in ((-20, 0), (20, 0), (0, -18), (0, 18))) - 4


FRONT = sorted([
    {'id': 'davant_faristol_1', 'mask': None, 'baseline': _baseline_faristol(*FARISTOLS[0]), 'zIndex': 20},
    {'id': 'davant_faristol_2', 'mask': None, 'baseline': _baseline_faristol(*FARISTOLS[1]), 'zIndex': 20},
    {'id': 'davant_sunifred', 'mask': _amo({'faristol_sunifred'}), 'baseline': _baseline_faristol(*SUNIFRED),
     'zIndex': 20},
    {'id': 'davant_espelma', 'mask': _amo({'canelobre'}), 'baseline': _p(*ESPELMA)[1] + 4, 'zIndex': 20,
     'variants': ('espelma_retallada',)},
    {'id': 'davant', 'mask': _amo({'davant'}), 'baseline': 999, 'zIndex': 20},
], key=lambda f: f['baseline'])


def _mask_faristol(k):
    """Els dos faristols dels copistes són de la mateixa superfície: es destrien per la caixa de pantalla."""
    x, z, a = FARISTOLS[k]
    g = _girat(x, z, a)
    pts = [CAM.projecta(g(lx, lz, y))[:2] for lx in (-40, 40) for lz in (-30, 30) for y in (0, 130)]
    x0, y0, x1, y1 = rect_de(*pts)
    m = _amo({'faristols'})
    return lambda xx, yy: x0 <= xx <= x1 and y0 <= yy <= y1 and m(xx, yy)


for _f in FRONT:
    if _f['id'] == 'davant_faristol_1':
        _f['mask'] = _mask_faristol(0)
    elif _f['id'] == 'davant_faristol_2':
        _f['mask'] = _mask_faristol(1)


# ─── Geometria (coordenades de sala) ─────────────────────────────────────────

def _escala_v(v):
    return round((v - CY) / EYE_H, 3)


def _sota(x, z, a, mw=24, md=22):
    g = _girat(x, z, a)
    return [_p(*[g(lx, lz)[k] for k in (0, 2)]) for lx, lz in ((-mw, -md), (mw, -md), (mw, md), (-mw, md))]


def _geometria():
    def caixa_faristol(x, z, a):
        g = _girat(x, z, a)
        return rect_de(*(CAM.projecta(g(lx, lz, y))[:2] for lx in (-27, 27) for lz in (-13, 13) for y in (0, HB + 2)))

    def pagina(x, z, a):
        g = _girat(x, z, a)
        return rect_de(*(CAM.projecta(g(lx, lz, y))[:2] for lx, lz, y in ((-21, 12, HB + 1), (21, 12, HB + 1),
                                                                            (21, -12, HD), (-21, -12, HD))), pad=2)
    f1, f2 = caixa_faristol(*FARISTOLS[0]), caixa_faristol(*FARISTOLS[1])
    faristols_r = (min(f1[0], f2[0]), min(f1[1], f2[1]), max(f1[2], f2[2]), max(f1[3], f2[3]))
    cx, cz, ll, fo, h = ARCA
    copies_r = rect_de(*(CAM.projecta(P)[:2] for P in ((cx - ll / 2, 0, cz - fo / 2), (cx + ll / 2, 0, cz - fo / 2),
                                                       (cx - ll / 2, h + 16, cz + fo / 2),
                                                       (cx + ll / 2, h + 16, cz + fo / 2))), pad=1)
    x0, x1, ya = CAPITULAR
    cap_r = rect_de(*(CAM.projecta(P)[:2] for P in ((x0 - 4, ya + (x1 - x0) / 2 + 6, ZB), (x1 + 4, 0, ZB))))
    fins = [CAM.projecta((x, y, ZB))[:2] for a, b in FINESTRALS for x in (a, b) for y in (FIN_Y[0], FIN_Y[1] + 30)]
    fin_r = rect_de(*fins)
    z0, z1, yp = PASSADIS
    pas_r = rect_de(*(CAM.projecta(P)[:2] for P in ((XL, 0, z0), (XL, 0, z1), (XL, yp + (z1 - z0) / 2 + 4, z0),
                                                    (XL, yp + (z1 - z0) / 2 + 4, z1))))
    ex, ez = ESPELMA
    eu, ev = _p(ex, ez)
    es = CAM.escala((ex, 0, ez))
    esp_r = (round(eu - 12 * es), round(ev - (HC + ALT_ESPELMA + 14) * es), round(eu + 12 * es), round(ev + 2))
    sx, sz, sa = SUNIFRED
    gs = _girat(sx, sz, sa)
    g1 = _girat(*FARISTOLS[0])
    g2 = _girat(*FARISTOLS[1])
    things = {
        'faristols': {'rect': faristols_r, 'walk': _p(*[g2(-10, -60)[k] for k in (0, 2)])},
        'copies': {'rect': copies_r, 'walk': _p(cx + 20, cz - fo / 2 - 40)},
        'faristol_sunifred': {'rect': caixa_faristol(sx, sz, sa), 'walk': _p(*[gs(-10, -46)[k] for k in (0, 2)])},
        'pergami': {'rect': pagina(sx, sz, sa), 'walk': _p(*[gs(-10, -46)[k] for k in (0, 2)])},
        'espelma_hores': {'rect': esp_r, 'walk': _p(ex - 30, ez - 40)},
        'finestrals': {'rect': (fin_r[0], max(0, fin_r[1]), fin_r[2], fin_r[3]), 'walk': _p(-40, ZB - 70)},
        'porta_capitular': {'rect': cap_r, 'walk': _p((x0 + x1) / 2, ZB - 36)},
        'porta_passadis': {'rect': pas_r, 'walk': _p(XL + 30, (z0 + z1) / 2)},
    }
    # el terra on es camina: del peu de les parets fins on la Vet fa ≈1,2; a la dreta, fins a l'armari
    walk = [_p(XL + 14, ZB - 30), _p(240, ZB - 30), _p(ARMARI[0] - 6, ARMARI[3] + 40), _p(ARMARI[0] - 10, 300),
            (560, 246), (120, 246), _p(XL + 14, 250)]
    walk = [(max(0, min(W - 1, u)), min(246, v)) for u, v in walk]
    vs = [v for _, v in walk]
    forats = [_sota(*f) for f in FARISTOLS] + [_sota(*SUNIFRED, mw=24, md=20),
                                              [_p(ex + 14 * math.cos(k * math.pi / 4), ez + 14 * math.sin(k * math.pi / 4))
                                               for k in range(8)]]
    lights = [llum_personatge(CAM, L.pos, 200, (255, 190, 110), 0.55) for L in LLUMS]
    lights.append({**llum_personatge(CAM, (-40, 60, ZB - 90), 260, (130, 160, 230), 0.25)})
    return {
        'things': things,
        # la Vet ve del passadís; en Gombau i l'Arnulf, drets al costat del seu faristol (una mica darrere)
        'spawns': {'vet': _p(XL + 60, 380), 'gombau': _p(*[g1(34, 14)[k] for k in (0, 2)]),
                   'arnulf': _p(*[g2(-36, 12)[k] for k in (0, 2)])},
        'walkable': walk,
        'forats': forats,
        'floorSquash': 0.42,
        'regions': [{'id': 'perspectiva', 'active': True, 'scaleEnabled': True, 'scaleWalkSpeed': True,
                     'scaleTop': _escala_v(min(vs) - 2), 'scaleBottom': _escala_v(max(vs) + 2),
                     'points': [(0, min(vs) - 2), (W - 1, min(vs) - 2), (W - 1, max(vs) + 2), (0, max(vs) + 2)]}],
        # L'ombra de contacte: llums petites i repartides (les espelmes): l'ombra, gairebé rodona; la llum de
        # referència, l'espelma del faristol del mig.
        'characterShadow': {'enabled': True, 'color': '#08060a', 'alpha': 0.48, 'squash': 0.4, 'core': 0.6,
                            'light': {'x': _p(FARISTOLS[1][0], FARISTOLS[1][1])[0],
                                      'y': _p(FARISTOLS[1][0], FARISTOLS[1][1])[1], 'stretch': 0.5, 'reach': 160}},
        'characterLights': {'ambient': '#4a4450', 'lights': lights},
    }


GEOMETRIA = _geometria()
