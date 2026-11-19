"""
La Cantimplora vista de fora: **el model 3D canònic** (una sola nau per a tot el joc). EN 3D (hd640/tres_d.py).

Una nau cisterna panxuda, oliva i taronja, rovellada (guio/fitxes-sales.md): el buc de revolució (la popa
arrodonida, el ventre gros, la proa que s'afua), de planxa oliva reblonada amb la franja taronja de seguretat, els
regalims de rovell, el nom CANTIMPLORA i la matrícula T2-0447 amb plantilla (als dos costats) i els ulls de bou; nou
dipòsits rodons al llom (cúpules crema amb la faixa taronja, en tres files de tres); dos motors a popa (amb el sutge
a les toveres); a proa, el finestral del pont (encès o apagat) i un pal curt amb el llum de navegació vermell; sis
potes d'aterratge amb peus (no toca a terra); la porta de la bodega al costat, una mica a popa del mig, amb el marc
de banda de perill, la llum càlida de dins i la rampa de planxa estriada baixada fins a terra.

Les unitats del model: una persona fa 83 d'alt (l'escala «de lluny» de les sales en 3D d'Aigua Verne, on 1 unitat del
món = 1 px a la distància on el personatge fa la seva mida normal). La nau fa ≈462 d'eslora, ≈184 de diàmetre al
ventre i ≈250 d'alt amb els dipòsits; la porta, ≈110 d'alt (≈1,3 persones). **No l'escaleu respecte de la gent**:
poseu-la més a prop o més lluny. Si el món de la sala té una altra unitat (una persona hi fa `h` unitats), passeu
`escala=h / 83`.

Ús
--
    from hd640.rooms.cantimplora_comu import Cantimplora
    NAU = Cantimplora(popa=(250, 650), rumb=math.radians(125), porta='babord')
    ...
    e = Escena(cv, CAM, LLUMS, ambient=AMBIENT)
    ... el terra, el que hi ha darrere de la nau ...
    NAU.dibuixa(e, ombra={'sol': (0.55, 1.0, -0.1)})       # (el terra ja ha de ser pintat: l'ombra hi va a sobre)
    ... el que hi ha davant de la nau ...
    NAU.resplendor(cv)                                     # (opcional) la claror del finestral i de la porta
    NAU.llum_nav(cv, encès=True)                           # (opcional) el llum vermell; o a una ANIM

La col·locació (`Cantimplora(...)`):
  - `popa=(x, z)`: el punt del terra just sota l'eix, on comença el cilindre del buc (la cúpula de popa en surt 28
    unitats enrere; els motors, ≈70);
  - `rumb`: l'angle (radians) de la direcció popa → proa al pla del terra: D = (cos rumb, 0, sin rumb) (0 = cap a +x,
    π/2 = cap al fons, −π/2 = cap a la càmera);
  - `porta='babord'|'estribord'`: el costat de la porta i la rampa (babord = a l'esquerra mirant cap a proa). El
    costat que es veu ha de ser el de la porta si la sala la vol veure; el nom i la matrícula són als dos costats;
  - `escala`: unitats del món per unitat del model (1 si una persona fa 83 al món de la sala);
  - `trams=None` o una tupla de llargades de l'eix, p. ex. (0, 80, 160, 240, 320, 400): el buc (i el que hi va
    enganxat) es reparteix en sids `nau0`, `nau1`... segons on cau al llarg de l'eix, per fer-ne capes del davant per
    trams (vegeu port_terra2). Sense trams, tot és `nau`.

`dibuixa(e, porta_oberta=True, rampa=None, llums=True, ombra=None, motors=True)`:
  - `porta_oberta`: la porta oberta (la bodega a dins, encesa si `llums`) o tancada (planxa);
  - `rampa`: la rampa baixada fins a terra (per defecte, si la porta és oberta);
  - `llums`: el finestral i la bodega encesos (càlids) o apagats (la portada i el pròleg l'apaguen); també la claror
    que es vessa per la rampa i el terra;
  - `ombra`: None, o {'sol': (x, y, z)} (la direcció cap al sol: com més baixa la y, més llarga l'ombra) o
    {'llum': (x, y, z)} (un llum puntual), amb 'k' (la foscor, 0,5 per defecte) i 'esvaeix' (unitats del món: l'ombra
    s'aclareix fins a la meitat a aquesta distància de la nau; per a les ombres llargues de la posta);
  - `motors`: els dos motors de popa;
  - `to`: (color, k) barreja tota la nau cap a un color (la llum de la sala: la posta, la boira, la nit).
  La nau es pinta amb un z-buffer propi (es pot mirar des de qualsevol costat: de popa, de dalt, de proa); el que s'hi
  pinti després queda davant. → l'Escena.

Els sids (a `e.amo` / `e.ids`, per a les capes del davant i per tapar el que passa per darrere):
  `nau` (o `nau0`.. amb trams: el buc, els dipòsits, els motors, les potes, el pal), `porta` (l'interior de la porta
  o la porta tancada), `cabina_finestres` (els vidres del finestral), `rampa` (la rampa, els pistons i les baranes).
  `sids_tram(k)` → els sids que cauen al tram k (inclou `porta` i `cabina_finestres` si hi són).
  `NAU.zb` (després de dibuixar): la profunditat (z de càmera) de cada píxel de la nau (array, 1e9 si no és nau), i
  `NAU.tapa(X, Y, z)` → si la nau tapa un punt a la profunditat z en aquell píxel (per a figures dibuixades a mà
  damunt del fons, com al pròleg).

Punts del model, al món (x, y, z):
  `RAMPA_DALT` (el llindar de la porta, al mig), `RAMPA_PEU` (el peu de la rampa a terra, al mig), `PORTA` (el mig
  de la porta), `CABINA` (el mig del finestral, del costat de la porta), `LLUM_NAV` (el llum de navegació, dalt del
  pal), `TOVERES` (els dos broquets dels motors: [el del costat de la porta, l'altre]), `CENTRE` (el centre del buc).
  `rampa_cantons()` → (dalt a, dalt b, baix b, baix a) (a = cap a popa).
  `p(l, c, y)` → un punt del model: `l` al llarg de l'eix (0 = popa, 400 = on comença la cúpula de proa), `c` cap al
  costat de la porta (negatiu: l'altre costat), `y` amunt. `terra(l, c)` → (x, z) del terra. `buc(l, th, dr=0)` → un
  punt del buc del costat de la porta (th: 0 = el costat, π/2 = dalt, −π/2 = sota).
  `xy(cam, P)` → (u, v) de pantalla, arrodonit. `caixa(cam, quina, marge)` → (u0, v0, u1, v1) de pantalla de
  'cabina', 'llum_nav', 'porta' (la porta, la rampa i la claror del terra), 'toveres' o 'nau'.
Constants del model: `LS, NL, LB` (la cúpula de popa, el cilindre, la cúpula de proa), `NR` (el radi al ventre),
`NY` (l'alçada de l'eix), `PORTA_L`, `PORTA_T` (la porta: llargades i angles), `RAMPA_OUT` (on toca a terra la rampa,
des de l'eix), `POTES_L`, `TANCS`; `nau_r(l)` (el perfil). Tot en unitats del model (×`escala` al món).

Les pantalles d'animació (el llum de navegació, la brasa dels motors) es pinten a part: `llum_nav(cv, encès)`,
`brasa(cv, encesa)`, `resplendor(cv)` (fan servir la càmera de l'últim `dibuixa`, o `cam=`).
"""
import functools
import math
from array import array

import hd640  # noqa: F401  (posa la llibreria de dibuix a 640×360)

from hd.pix import Canvas, hr, B4
from hd.rooms.comu import text, text_width
from hd.rooms.exterior import _s

_hr = functools.lru_cache(maxsize=None)(hr)          # (el soroll de la llibreria tornaria a sembrar a cada crida)


def vnoise(u, v, seed=0):
    x0, y0 = math.floor(u), math.floor(v)
    fx, fy = _s(u - x0), _s(v - y0)
    a, b = _hr(x0, y0, seed), _hr(x0 + 1, y0, seed)
    c, d = _hr(x0, y0 + 1, seed), _hr(x0 + 1, y0 + 1, seed)
    return a + (b - a) * fx + (c - a) * fy + (a - b - c + d) * fx * fy


def fbm(u, v, seed=0, octaves=3):
    s, amp, tot = 0.0, 1.0, 0.0
    for o in range(octaves):
        s += vnoise(u * 2 ** o, v * 2 ** o, seed + o * 17) * amp
        tot += amp
        amp *= 0.5
    return s / tot

# ─── Colors (fosc → clar) ───────────────────────────────────────────────────
OLIVE = [(22, 26, 14), (36, 42, 22), (52, 60, 32), (70, 80, 44), (90, 102, 58), (112, 124, 74), (138, 150, 96),
         (166, 176, 122)]
ORANGE = [(48, 16, 10), (92, 32, 14), (140, 54, 18), (190, 84, 26), (230, 122, 40), (250, 168, 80),
          (255, 210, 140)]
WARN = [(40, 28, 6), (90, 64, 10), (150, 110, 16), (210, 160, 30), (246, 206, 70), (255, 240, 160)]
IRONR = [(20, 16, 16), (36, 30, 28), (54, 46, 42), (76, 66, 60), (100, 90, 82), (128, 118, 108), (160, 150, 138)]
RUSTT = [(30, 14, 12), (58, 26, 18), (92, 42, 24), (128, 62, 32), (164, 88, 44), (196, 122, 64), (220, 156, 96)]
BLACKT = [(10, 10, 12), (22, 22, 24), (36, 36, 38), (54, 54, 56), (76, 76, 78)]
TANKC = [(46, 40, 30), (78, 70, 52), (112, 104, 80), (146, 138, 108), (178, 170, 136), (206, 198, 164),
         (230, 224, 196), (246, 242, 222)]
WARM = [(60, 30, 10), (120, 70, 24), (190, 120, 50), (240, 180, 90), (255, 226, 160)]
DARKIN = [(8, 6, 6), (16, 12, 12), (26, 20, 20), (38, 30, 28)]
WIN_ON = [(120, 70, 30), (200, 140, 60), (255, 210, 130), (255, 240, 200)]
WIN_OFF = [(16, 18, 24), (24, 26, 32), (34, 38, 46), (44, 48, 56), (64, 70, 80)]

# ─── El model (unitats: una persona fa 83) ──────────────────────────────────
LS, NL, LB = 28.0, 400.0, 34.0           # la cúpula de popa, el cilindre (amb la proa que s'afua), la cúpula de proa
NR = 92.0                                # el radi al ventre
NY = 112.0                               # l'alçada de l'eix (el ventre queda a 20 de terra)
PORTA_L = (104.0, 160.0)                 # la porta de la bodega, al llarg de l'eix (una mica a popa del mig)
PORTA_T = (-0.62, 0.68)                  # (angles del costat: 0 = el costat, π/2 = dalt) → ≈110 d'alt
RAMPA_OUT = 200.0                        # on toca a terra la rampa (des de l'eix)
POTES_L = (35.0, 225.0, 365.0)
TANCS = [(l, c) for l in (95.0, 190.0, 285.0) for c in (-56.0, 0.0, 56.0)]   # els nou dipòsits: (l, costat)
R_TANC = 31.0
PAL_L = NL - 20                          # el pal del llum de navegació
FINESTRAL = (NL - 64, NL + LB, 0.56, 0.82)   # l0, l1, th0, th1
MOTORS = ((40.0, -6.0), (-40.0, -6.0))   # (c, y respecte de l'eix): el del costat de la porta i l'altre
MOTOR_L = (-6.0, -LS - 44.0)             # d'on surten (dins la popa) fins al broquet
MOTOR_R = 15.0

TEX_H = int(math.pi * NR) + 1            # el buc desenrotllat, un costat: x = l + LS, y = (π/2 − th)·NR (dalt a y 0)
TEX_W = int(LS + NL + LB) + 1


def nau_r(l):
    """El radi del buc al llarg de l'eix: la popa arrodonida (una cúpula), panxut al mig i la proa que s'afua."""
    if l < 0:
        return NR * 0.72 * math.sqrt(max(0.0, 1 - (l / LS) ** 2))
    if l > NL:
        return NR * 0.5 * math.sqrt(max(0.0, 1 - ((l - NL) / LB) ** 2))
    r = NR * (0.72 + 0.28 * math.sin(min(1.0, l / 60) * math.pi / 2))
    if l > NL - 110:
        r *= 1 - 0.5 * ((l - (NL - 110)) / 110) ** 1.5
    return r


def _ty(th):
    return (math.pi / 2 - th) * NR


# ─── La textura del buc ─────────────────────────────────────────────────────

def _text_gran(cv, s, x, y, col, k, mirror=False, ky=None):
    """Text de la font petita, ampliat k vegades (pintat amb plantilla, gastat). `mirror`: per a un costat que es veu
    amb la proa a l'esquerra (la textura va de popa a proa)."""
    ky = ky or k
    tw = text_width(s)
    t = Canvas(tw + 2, 9, transparent=True)
    text(t, s, 0, 1, BLACKT, 1.0, lit=0, flat=(255, 255, 255))
    src = t.img.load()
    for yy in range(9):
        for xx in range(tw + 2):
            if src[xx, yy][3]:
                for dy in range(ky):
                    for dx in range(k):
                        X = x + (tw * k - 1 - (xx * k + dx) if mirror else xx * k + dx)
                        if _hr(X, y + yy * ky + dy, 77) > 0.12:
                            cv.flat(X, y + yy * ky + dy, col)


@functools.lru_cache(maxsize=None)
def _planxa(costat_porta, mirror):
    """Un costat del buc, sense la porta ni el finestral: plaques oliva amb reblons, la franja taronja, regalims de
    rovell, el sutge de popa, el nom i la matrícula, els ulls de bou."""
    cv = Canvas(TEX_W, TEX_H, light=None)
    seed = 3 if costat_porta else 9
    for y in range(TEX_H):
        th = math.pi / 2 - y / NR
        for x in range(TEX_W):
            pv = y / 26
            plate_r = int(pv)
            px = x + (plate_r % 2) * 22
            plate_c = px // 44
            seam = (pv % 1) < 0.05 or px % 44 == 0
            lvl = 3.7 + (_hr(plate_c, plate_r, seed) - 0.5) * 0.7 + (vnoise(x / 30, y / 10, 8 + seed) - 0.5) * 0.6
            ramp = OLIVE
            if -0.36 < th < -0.22:
                ramp, lvl = ORANGE, lvl - 0.5                                 # la franja de seguretat
            if fbm(x / 3, y / 22, 21 + seed) > 0.68 and th < 0.7:
                ramp, lvl = RUSTT, lvl - 0.2                                  # regalims de rovell
            dome = x < LS - 2 or x > LS + NL + 2                              # (a les cúpules, sense plaques:
            if dome:                                                          # a la punta farien radis)
                lvl = 3.7 + (vnoise(x / 12, 3.0, 8 + seed) - 0.5) * 0.5 - (1.0 if x in (int(LS / 2),) else 0)
            elif seam:
                lvl -= 1.0
            elif px % 44 in (3, 41) and y % 4 == 0:
                lvl += 1.0                                                    # els reblons
            if x < LS + 8:                                                    # el sutge dels motors, a popa
                d = math.hypot((x - 4) / (LS + 10), (th + 0.07) / 0.75)
                lvl -= 2.6 * max(0.0, 1 - d) * (0.6 + 0.6 * fbm(x / 4, y / 6, 5))
            cv.put(x, y, ramp, lvl, lit=0)
    # el nom, amb plantilla (crema), i la matrícula; els ulls de bou
    _text_gran(cv, 'CANTIMPLORA', int(LS + 166), int(_ty(0.27)), (226, 220, 190), 3, mirror=mirror, ky=4)
    _text_gran(cv, 'T2-0447', int(LS + 12), int(_ty(0.27)), (210, 204, 172), 3, mirror=mirror, ky=4)
    for l in (200.0, 236.0, 272.0, 308.0):
        cy = _ty(0.56)
        cv.disc(l + LS, cy, 6, 6, IRONR, lambda nx, ny: 3.6 + nx - ny, lit=0)
        cv.disc(l + LS, cy, 4, 4, BLACKT, lambda nx, ny: 1.6 - ny, lit=0)
        cv.flat(l + LS - 1, int(cy) - 2, (226, 214, 180))
    return cv.img


# els tipus de cada texel (per als sids): 0 = el buc, 1 = la porta, 2 = el finestral
@functools.lru_cache(maxsize=None)
def _textura(costat_porta, mirror, porta_oberta, llums):
    img = _planxa(costat_porta, mirror).copy()
    cv = Canvas(img=img, light=None)
    kind = bytearray(TEX_W * TEX_H)
    # el finestral del pont, a proa (els dos costats): els vidres i els muntants
    l0, l1, t0, t1 = FINESTRAL
    for x in range(int(l0 + LS), min(TEX_W, int(l1 + LS) + 1)):
        for y in range(int(_ty(t1)), int(_ty(t0)) + 1):
            glass = (x - int(l0 + LS)) % 16 not in (0, 1, 2)
            if glass:
                yy = y - _ty(t1)
                if llums:
                    lvl = 2.0 + (0.9 if yy < 4 else 0) - (0.5 if (x + y) % 5 == 0 else 0)
                    cv.put(x, y, WIN_ON, lvl, lit=0)
                else:
                    cv.put(x, y, WIN_OFF, 1.4 + (2.0 if 2 < (x - yy) % 16 < 5 else 0), lit=0)   # un reflex
                kind[y * TEX_W + x] = 2
            else:
                cv.put(x, y, IRONR, 2.6, lit=0)
        for y in (int(_ty(t1)) - 1, int(_ty(t0)) + 1):
            cv.put(x, y, IRONR, 1.4, lit=0)
    if costat_porta:
        x0, x1 = PORTA_L[0] + LS, PORTA_L[1] + LS
        y0, y1 = _ty(PORTA_T[1]), _ty(PORTA_T[0])
        for y in range(int(y0), int(y1) + 1):
            for x in range(int(x0), int(x1) + 1):
                if porta_oberta:
                    d = math.hypot((x - (x0 + x1) / 2) / 28, (y - y0 - 22) / 52)
                    if llums:
                        cv.put(x, y, WARM, 2.6 - d * 1.6 + (y - y0) * 0.004, lit=0)
                    else:
                        cv.put(x, y, DARKIN, 2.0 - d * 1.4, lit=0)
                else:                                                         # tancada: planxa amb nervis
                    cv.put(x, y, OLIVE, 3.0 + (0.8 if (y - y0) % 18 < 2 else 0) - (1.2 if x in (int(x0), int(x1)) else 0),
                           lit=0)
                kind[y * TEX_W + x] = 1
        if porta_oberta:                                                      # a dins: els barrils i els llums
            ramp_in = WARM if llums else DARKIN
            cv.rect(x0 + 6, y0 + 44, x0 + 20, y1, BLACKT, lambda x, y: 1.0 + (0.6 if x % 4 == 0 else 0), lit=0)
            cv.disc(x1 - 12, y1 - 18, 10, 16, ramp_in, lambda nx, ny: 0.4 + nx * 0.6, lit=0)
            if llums:
                for kx in (x0 + 12, x1 - 12):
                    cv.disc(kx, y0 + 5, 1.6, 1.6, WARM, 4.6, lit=0)
        for y in range(int(y0) - 5, int(y1) + 1):                             # el marc de banda de perill
            for x in range(int(x0) - 5, int(x1) + 6):
                if x0 <= x <= x1 and y >= y0:
                    continue
                on = (y + x) // 4 % 2
                cv.put(x, y, WARN if on else BLACKT, 3.4 if on else 2.0, lit=0)
    return img, bytes(kind)


# ─── La nau ─────────────────────────────────────────────────────────────────

def _add(a, b, k=1.0):
    return (a[0] + b[0] * k, a[1] + b[1] * k, a[2] + b[2] * k)


def _sub(a, b):
    return (a[0] - b[0], a[1] - b[1], a[2] - b[2])


def _dot(a, b):
    return a[0] * b[0] + a[1] * b[1] + a[2] * b[2]


def _norm(a):
    n = math.sqrt(_dot(a, a)) or 1.0
    return (a[0] / n, a[1] / n, a[2] / n)


def _cross(a, b):
    return (a[1] * b[2] - a[2] * b[1], a[2] * b[0] - a[0] * b[2], a[0] * b[1] - a[1] * b[0])


class Cantimplora:
    LS, NL, LB, NR, NY = LS, NL, LB, NR, NY
    PORTA_L, PORTA_T, RAMPA_OUT, POTES_L, TANCS = PORTA_L, PORTA_T, RAMPA_OUT, POTES_L, TANCS

    def __init__(self, popa, rumb, porta='babord', escala=1.0, trams=None, sid='nau'):
        assert porta in ('babord', 'estribord')
        self.popa, self.rumb, self.porta, self.esc, self.trams, self.sid = popa, rumb, porta, escala, trams, sid
        self.D = (math.cos(rumb), 0.0, math.sin(rumb))                       # de popa a proa
        bab = (-self.D[2], 0.0, self.D[0])                                   # babord: a l'esquerra mirant a proa
        self.cs = 1 if porta == 'babord' else -1
        self.N = (bab[0] * self.cs, 0.0, bab[2] * self.cs)                   # el costat de la porta
        self.ang = math.atan2(self.D[2], self.D[0])
        self.zb = None
        self.cam = None
        mig = sum(PORTA_L) / 2
        self.RAMPA_DALT = self.buc(mig, PORTA_T[0], 2)
        self.RAMPA_PEU = self.p(mig, RAMPA_OUT + 4, 0)
        self.PORTA = self.buc(mig, sum(PORTA_T) / 2, 0)
        self.CABINA = self.buc((FINESTRAL[0] + FINESTRAL[1]) / 2 - 16, (FINESTRAL[2] + FINESTRAL[3]) / 2, 0)
        self.LLUM_NAV = self.p(PAL_L, 0, NY + nau_r(PAL_L) + 40)
        self.TOVERES = [self.p(MOTOR_L[1], c, NY + y) for c, y in MOTORS]
        self.CENTRE = self.p(NL / 2, 0, NY)

    # ── punts ──
    def p(self, l, c, y):
        """Un punt del model al món: `l` al llarg de l'eix, `c` cap al costat de la porta, `y` amunt."""
        k = self.esc
        return (self.popa[0] + (self.D[0] * l + self.N[0] * c) * k, y * k, self.popa[1] + (self.D[2] * l + self.N[2] * c) * k)

    def terra(self, l, c):
        P = self.p(l, c, 0)
        return (P[0], P[2])

    def buc(self, l, th, dr=0.0):
        """Un punt del buc del costat de la porta (th: 0 = el costat, π/2 = dalt; amb th > π/2, l'altre costat)."""
        r = nau_r(l) + dr
        return self.p(l, r * math.cos(th), NY + r * math.sin(th))

    def rampa_cantons(self):
        la, lb = PORTA_L[0] + 3, PORTA_L[1] - 3
        return (self.buc(la, PORTA_T[0], 1), self.buc(lb, PORTA_T[0], 1),
                self.p(lb, RAMPA_OUT, 0.5), self.p(la, RAMPA_OUT, 0.5))

    def tram(self, l):
        if not self.trams:
            return self.sid
        T = self.trams
        for k, (a, b) in enumerate(zip(T, T[1:])):
            if a <= l < b:
                return f'{self.sid}{k}'
        return f'{self.sid}0' if l < T[0] else f'{self.sid}{len(T) - 2}'

    def sids_tram(self, k):
        s = {f'{self.sid}{k}'}
        if self.tram(sum(PORTA_L) / 2) == f'{self.sid}{k}':
            s.add('porta')
        if self.tram(min(NL - 1, FINESTRAL[0] + 30)) == f'{self.sid}{k}':
            s.add('cabina_finestres')
        return s

    def xy(self, cam, P):
        u, v, _ = cam.projecta(P)
        return round(u), round(v)

    def caixa(self, cam, quina, marge=0):
        """La caixa de pantalla (u0, v0, u1, v1) d'una part: 'cabina', 'llum_nav', 'porta', 'toveres' o 'nau'."""
        if quina == 'cabina':
            l0, l1, t0, t1 = FINESTRAL
            pts = [self.buc(l, t, 0) for l in (l0, (l0 + l1) / 2, l1 - 6, l1 - 1) for t in (t0, t1, math.pi / 2)]
        elif quina == 'llum_nav':
            pts = [self.LLUM_NAV]
        elif quina == 'porta':
            la, lb = PORTA_L[0] - 6, PORTA_L[1] + 6
            pts = [self.buc(l, t, 0) for l in (la, lb) for t in (PORTA_T[0] - 0.1, PORTA_T[1] + 0.08)]
            pts += list(self.rampa_cantons())
            pts += [self.p(PORTA_L[0] - 40, RAMPA_OUT + 80, 0), self.p(PORTA_L[1] + 40, RAMPA_OUT + 80, 0)]
        elif quina == 'toveres':
            pts = list(self.TOVERES)
        else:
            pts = [self.p(l, c, y) for l in (-LS - 50, NL / 2, NL + LB) for c in (-RAMPA_OUT, RAMPA_OUT)
                   for y in (0, NY + NR + 2 * R_TANC)]
        pr = [cam.projecta(P) for P in pts]
        return (int(min(p[0] for p in pr)) - marge, int(min(p[1] for p in pr)) - marge,
                int(max(p[0] for p in pr)) + 1 + marge, int(max(p[1] for p in pr)) + 1 + marge)

    def tapa(self, X, Y, z):
        """Si la nau (l'últim `dibuixa`) tapa, al píxel (X, Y), una cosa a la profunditat de càmera z."""
        if self.zb is None:
            return False
        i = Y * self._w + X
        return 0 <= X < self._w and 0 <= Y < self._h and self.zb[i] < z

    # ── dibuix ──
    def dibuixa(self, e, porta_oberta=True, rampa=None, llums=True, ombra=None, motors=True, to=None):
        if rampa is None:
            rampa = porta_oberta
        self.cam = cam = e.cam
        cv = e.cv
        self._w, self._h = cv.w, cv.h
        self._e = e
        self.zb = array('f', [1e9]) * (cv.w * cv.h)
        self._bbox = {}
        # el pas de mostreig (unitats del model): ≈0,55 px a la part més propera de la nau
        kmax = max(cam.escala(P) for P in (self.p(l, c, y) for l in (-LS - 40, NL / 2, NL + LB)
                                            for c in (-NR, NR, RAMPA_OUT) for y in (0, NY, NY + NR + 60)))
        self.pas = min(1.0, 0.55 / (kmax * self.esc))
        if ombra:
            self._ombra(e, ombra, rampa)
        self._buc(e, porta_oberta, llums)
        for l, c in TANCS:
            self._tanc(e, l, c)
        for l in POTES_L:
            for costat in (1, -1):
                self._pota(e, l, costat)
        if motors:
            for c, y in MOTORS:
                self._motor(e, c, y)
        # el pal del llum de navegació
        B = self.p(PAL_L, 0, NY + nau_r(PAL_L) - 4)
        self._tub(e, self.tram(PAL_L), B, self.LLUM_NAV, 2.0, lambda t, P: (IRONR, 2.6))
        if rampa:
            self._rampa(e, llums and porta_oberta)
        if to is not None:                                                   # el to de la sala (la posta, la boira)
            col, kt = to
            P_, zb, W_ = cv.P, self.zb, cv.w
            for i, z in enumerate(zb):
                if z < 1e9:
                    X, Y = i % W_, i // W_
                    o = P_[X, Y]
                    P_[X, Y] = (int(o[0] + (col[0] - o[0]) * kt), int(o[1] + (col[1] - o[1]) * kt),
                                int(o[2] + (col[2] - o[2]) * kt), o[3])
        for sid, b in self._bbox.items():
            o = e.caixes.get(sid)
            e.caixes[sid] = b if o is None else (min(o[0], b[0]), min(o[1], b[1]), max(o[2], b[2]), max(o[3], b[3]))
        return e

    def _escriu(self, X, Y, z, idx, sid, col=None, ramp=None, lvl=0.0):
        i = Y * self._w + X
        if z >= self.zb[i]:
            return
        self.zb[i] = z
        if col is not None:
            self._e.cv.P[X, Y] = col
        else:
            self._e.cv.put(X, Y, ramp, lvl, lit=0)
        self._e.amo[i] = idx
        b = self._bbox.get(sid)
        self._bbox[sid] = (X, Y, X, Y) if b is None else (min(b[0], X), min(b[1], Y), max(b[2], X), max(b[3], Y))

    def _proj(self):
        """La projecció de la càmera, desplegada (per als bucles de mostreig)."""
        c = self.cam
        return (c.pos, c._cy, c._sy, c._cp, c._sp, c.f, c.centre[0], c.centre[1])

    def _buc(self, e, porta_oberta, llums):
        """El buc, mostrejat prou dens (≈2 mostres per píxel): la textura de cada costat, la llum per cada punt, la
        panxa a l'ombra."""
        texs = {}
        for costat in (1, -1):                                               # 1: el costat de la porta
            mirror = (costat * self.cs) > 0                                  # babord: la proa es veu a l'esquerra
            img, kind = _textura(costat > 0, mirror, porta_oberta, llums)
            texs[costat] = (img.load(), kind)
        (px_, py_, pz_), cy, sy, cp, sp, f, cu, cvv = self._proj()
        W_, H_ = self._w, self._h
        ull = self.cam.pos
        D, N, k = self.D, self.N, self.esc
        idx_k = {}
        idx_porta, idx_fin = e._idx_de('porta'), e._idx_de('cabina_finestres')
        zb, amo, P_ = self.zb, e.amo, e.cv.P
        llum_cache = {}
        pas = self.pas
        l = -LS
        bb = {}
        while l <= NL + LB:
            r = nau_r(l)
            dr = nau_r(l + 0.5) - nau_r(l - 0.5)
            sidl = self.tram(max(0.0, min(NL - 1, l)))
            if sidl not in idx_k:
                idx_k[sidl] = e._idx_de(sidl)
            ik = idx_k[sidl]
            cx, cz = self.popa[0] + D[0] * l * k, self.popa[1] + D[2] * l * k
            cyy = NY * k
            dph = pas / max(3.0, r)
            TX = min(TEX_W - 1, max(0, int(l + LS)))
            ph = -math.pi / 2
            while ph < 3 * math.pi / 2:
                ct, st = math.cos(ph), math.sin(ph)
                erx, ery, erz = N[0] * ct, st, N[2] * ct
                Px, Py, Pz = cx + erx * r * k, cyy + ery * r * k, cz + erz * r * k
                nx, ny, nz = erx - D[0] * dr, ery, erz - D[2] * dr
                if nx * (ull[0] - Px) + ny * (ull[1] - Py) + nz * (ull[2] - Pz) > 0:
                    dx, dy, dz = Px - px_, Py - py_, Pz - pz_
                    x1 = dx * cy - dz * sy
                    z1 = dx * sy + dz * cy
                    y2 = dy * cp + z1 * sp
                    z2 = -dy * sp + z1 * cp
                    if z2 > 1:
                        X, Y = int(cu + f * x1 / z2), int(cvv - f * y2 / z2)
                        if 0 <= X < W_ and 0 <= Y < H_ and z2 < zb[Y * W_ + X]:
                            costat = 1 if ct >= 0 else -1
                            th = ph if costat > 0 else math.pi - ph
                            src, kind = texs[costat]
                            ty = min(TEX_H - 1, max(0, int((math.pi / 2 - th) * NR)))
                            col = src[TX, ty]
                            kd = kind[ty * TEX_W + TX]
                            key = (int(l / 10), int(ph * 10))
                            lv = llum_cache.get(key)
                            if lv is None:
                                nn = math.sqrt(nx * nx + ny * ny + nz * nz) or 1
                                lv = llum_cache[key] = e.llum((Px, Py, Pz), (nx / nn, ny / nn, nz / nn))
                            kk = 1.0 + lv * 0.18
                            if kd != 2:
                                kk *= 1 - 0.5 * max(0.0, -st) ** 1.3 + 0.08 * max(0.0, st) ** 3
                            kk += (B4[Y & 3][X & 3] - 0.5) * 0.06
                            i = Y * W_ + X
                            zb[i] = z2
                            P_[X, Y] = (min(255, int(col[0] * kk)), min(255, int(col[1] * kk)), min(255, int(col[2] * kk)),
                                        255)
                            sid = 'porta' if kd == 1 else 'cabina_finestres' if kd == 2 else sidl
                            amo[i] = idx_porta if kd == 1 else idx_fin if kd == 2 else ik
                            b = bb.get(sid)
                            bb[sid] = (X, Y, X, Y) if b is None else (min(b[0], X), min(b[1], Y), max(b[2], X),
                                                                      max(b[3], Y))
                ph += dph
            l += max(0.02, pas / math.sqrt(1 + dr * dr))                      # (a les cúpules, més dens)
        for sid, b in bb.items():
            o = self._bbox.get(sid)
            self._bbox[sid] = b if o is None else (min(o[0], b[0]), min(o[1], b[1]), max(o[2], b[2]), max(o[3], b[3]))

    def _mostres(self, e, sid, punts):
        """Pinta mostres (P, n, ramp, lvl) amb el z-buffer de la nau (les que es veuen d'esquena no es pinten)."""
        (px_, py_, pz_), cy, sy, cp, sp, f, cu, cvv = self._proj()
        idx = e._idx_de(sid)
        W_, H_ = self._w, self._h
        ull = self.cam.pos
        for P, n, ramp, lvl in punts:
            if n is not None and _dot(n, _sub(ull, P)) <= 0:
                continue
            dx, dy, dz = P[0] - px_, P[1] - py_, P[2] - pz_
            x1 = dx * cy - dz * sy
            z1 = dx * sy + dz * cy
            y2 = dy * cp + z1 * sp
            z2 = -dy * sp + z1 * cp
            if z2 <= 1:
                continue
            X, Y = int(cu + f * x1 / z2), int(cvv - f * y2 / z2)
            if 0 <= X < W_ and 0 <= Y < H_:
                self._escriu(X, Y, z2, idx, sid, ramp=ramp, lvl=lvl)

    def _tanc(self, e, l, c):
        """Un dipòsit rodó al llom: una esfera crema amb la faixa taronja, la tapa i regalims de rovell."""
        r = nau_r(l)
        k = self.esc
        R = R_TANC
        yc = NY + math.sqrt(max(0.0, r * r - c * c)) + 0.3 * R
        C = self.p(l, c, yc)
        D, N, up = self.D, self.N, (0.0, 1.0, 0.0)
        pas = self.pas
        seed = int(l + c)
        cache = {}

        def gen():
            a = -0.5
            while a <= math.pi / 2:
                ca, sa = math.cos(a), math.sin(a)
                db = pas / max(0.5, R * ca)
                b = 0.0
                while b < 2 * math.pi:
                    n = (ca * (math.cos(b) * D[0] + math.sin(b) * N[0]), sa, ca * (math.cos(b) * D[2] + math.sin(b) * N[2]))
                    P = (C[0] + n[0] * R * k, C[1] + n[1] * R * k, C[2] + n[2] * R * k)
                    key = (int(a * 10), int(b * 10))
                    lv = cache.get(key)
                    if lv is None:
                        lv = cache[key] = e.llum(P, n)
                    if abs(sa + 0.02) < 0.11:
                        yield P, n, ORANGE, 3.6 + lv
                    elif sa > 0.96:
                        yield P, n, IRONR, 4.0 + lv                                   # la tapa
                    elif sa < 0.2 and fbm(b * R / 3, a * R / 8, seed) > 0.66:
                        yield P, n, RUSTT, 3.6 + lv                                   # regalims de rovell
                    else:
                        seam = (b * R) % 30 < 1.2
                        yield P, n, TANKC, 4.4 + lv - (0.9 if seam else 0) + sa * 0.4
                    b += db
                a += pas / R
        self._mostres(e, self.tram(l), gen())

    def _tub(self, e, sid, A, B, r, colfn, tapa=False):
        """Un cilindre de A a B (món), de radi r (model): `colfn(t, P)` → (ramp, lvl) (t: 0..1 de A a B)."""
        k = self.esc
        ax = _sub(B, A)
        L = math.sqrt(_dot(ax, ax))
        if L < 1e-6:
            return
        u = (ax[0] / L, ax[1] / L, ax[2] / L)
        a = (0.0, 1.0, 0.0) if abs(u[1]) < 0.9 else (1.0, 0.0, 0.0)
        e1 = _norm(_cross(u, a))
        e2 = _cross(u, e1)
        pas = self.pas * k
        rr = r * k
        cache = {}

        def gen():
            s = 0.0
            while s <= L:
                t = s / L
                da = pas / max(0.4, rr)
                ang = 0.0
                while ang < 2 * math.pi:
                    n = _add(_add((0, 0, 0), e1, math.cos(ang)), e2, math.sin(ang))
                    P = (A[0] + u[0] * s + n[0] * rr, A[1] + u[1] * s + n[1] * rr, A[2] + u[2] * s + n[2] * rr)
                    ramp, lvl = colfn(t, P)
                    key = (int(s / 6), int(ang * 4))
                    lv = cache.get(key)
                    if lv is None:
                        lv = cache[key] = e.llum(P, n)
                    yield P, n, ramp, lvl + lv
                    ang += da
                s += pas
            if tapa:
                rho = 0.0
                while rho <= rr:
                    da = pas / max(0.4, rho)
                    ang = 0.0
                    while ang < 2 * math.pi:
                        P = _add(_add(B, e1, math.cos(ang) * rho), e2, math.sin(ang) * rho)
                        ramp, lvl = tapa(rho / rr, P)
                        yield P, u, ramp, lvl
                        ang += da
                    rho += pas
        self._mostres(e, sid, gen())

    def _pota(self, e, l, costat):
        """Una pota d'aterratge: la cama (amb el genoll), el tirant, el peu i el pistó de perill."""
        sid = self.tram(l)
        cs = costat
        hip = self.p(l, cs * nau_r(l) * math.cos(0.95), NY - nau_r(l) * math.sin(0.95) + 2)
        knee = self.p(l + 4, cs * 92, 28)
        foot = self.p(l + 8, cs * 104, 7)
        brace = self.p(l - 10, cs * nau_r(l) * math.cos(1.35), NY - nau_r(l) * math.sin(1.35) + 2)

        def ferro(t, P):
            return IRONR, 3.0
        self._tub(e, sid, hip, knee, 4.6, ferro)
        self._tub(e, sid, knee, foot, 4.2, ferro)
        self._tub(e, sid, brace, knee, 2.6, lambda t, P: (IRONR, 2.4))
        F = self.p(l + 8, cs * 104, 0)
        self._tub(e, sid, _add(F, (0, 1, 0), 15 * self.esc), _add(F, (0, 1, 0), 5 * self.esc), 6.5,
                  lambda t, P: (WARN, 3.2) if (P[1] / self.esc) % 6 < 3 else (BLACKT, 2.4))   # el pistó, de perill
        self._tub(e, sid, _add(F, (0, 1, 0), 5 * self.esc), F, 15.0, lambda t, P: (IRONR, 2.8),
                  tapa=lambda q, P: (IRONR, 4.0 - q * 0.6))                                  # el peu

    def _motor(self, e, c, y):
        """Un motor de popa: un tub d'acer que surt de la cúpula de popa, la tovera eixamplada i el sutge al voltant
        del broquet."""
        A = self.p(MOTOR_L[0], c, NY + y)
        B = self.p(MOTOR_L[1], c, NY + y)

        def col(t, P):
            soot = max(0.0, (t - 0.55) / 0.45)
            ring = (t * 50) % 12 < 1.4
            return IRONR, 3.4 - soot * 2.4 - (1.0 if ring else 0)
        self._tub(e, self.tram(0), A, B, MOTOR_R, col)
        Bf = self.p(MOTOR_L[1] + 6, c, NY + y)
        self._tub(e, self.tram(0), Bf, B, MOTOR_R * 1.18, lambda t, P: (IRONR, 1.6 - t * 0.6),
                  tapa=lambda q, P: (BLACKT, 0.2 + q * 1.4))

    def _rampa(self, e, encesa):
        """La rampa de planxa estriada, baixada fins a terra, amb les baranes de perill i els pistons."""
        sa, sb, fb, fa = self.rampa_cantons()
        e1, e3 = _sub(sb, sa), _sub(fa, sa)
        L1, L3 = math.sqrt(_dot(e1, e1)), math.sqrt(_dot(e3, e3))
        n = _norm(_cross(e1, e3))
        if _dot(n, _sub(self.cam.pos, sa)) < 0:
            n = (-n[0], -n[1], -n[2])
        k = self.esc
        pas = self.pas * k

        def gen():
            t = 0.0
            while t <= L3:
                s = 0.0
                while s <= L1:
                    P = _add(_add(sa, e1, s / L1), e3, t / L3)
                    sm, tm = s / k, t / k
                    ridge = ((sm + tm) % 9 < 1.4) or ((sm - tm) % 9 < 1.4)
                    lvl = 3.4 + tm * 0.004 - (1.0 if ridge else 0) + (fbm(sm / 6, tm / 6, 4) - 0.5) * 0.6 \
                        - (1.4 if sm < 3 or sm > L1 / k - 3 else 0)
                    yield P, None, IRONR, lvl + e.llum(P, n)
                    s += pas
                t += pas
        self._mostres(e, 'rampa', gen())
        up = (0.0, 1.0, 0.0)
        for a, f, l in ((sa, fa, PORTA_L[0]), (sb, fb, PORTA_L[1])):
            self._tub(e, 'rampa', _add(a, up, 3 * k), _add(f, up, 3 * k), 2.2,
                      lambda t, P: (WARN, 3.6) if int(t * 14) % 2 else (BLACKT, 2.2))      # les baranes de perill
            m = self.buc(l, -0.95, 1)
            mid = ((a[0] + f[0]) / 2, (a[1] + f[1]) / 2 - 3 * k, (a[2] + f[2]) / 2)
            self._tub(e, 'rampa', m, mid, 2.6, lambda t, P: (IRONR, 3.4 if t > 0.5 else 2.4))   # els pistons
        if encesa:
            # la llum de dins, que es vessa per la rampa i pel terra
            e.claror(sa, sb, fb, fa, (255, 214, 150), lambda s, t: 0.3 * max(0.0, 1 - t / L3))
            g0, g1 = self.p(PORTA_L[0] - 10, RAMPA_OUT - 4, 0.2), self.p(PORTA_L[1] + 10, RAMPA_OUT - 4, 0.2)
            g2, g3 = self.p(PORTA_L[1] + 30, RAMPA_OUT + 74, 0.2), self.p(PORTA_L[0] - 30, RAMPA_OUT + 74, 0.2)
            W1 = (PORTA_L[1] - PORTA_L[0] + 60) * k
            e.claror(g3, g2, g1, g0, (255, 210, 140),
                     lambda s, t: 0.2 * max(0.0, t / (78 * k)) * max(0.0, 1 - abs(s - W1 / 2) / (W1 * 0.8)))

    # ── l'ombra ──
    def _ombra(self, e, om, rampa):
        k_ = om.get('k', 0.5)
        esv = om.get('esvaeix')
        if 'sol' in om:
            Ls = _norm(om['sol'])

            def aterra(P):
                t = P[1] / max(0.02, Ls[1])
                return (P[0] - Ls[0] * t, P[2] - Ls[2] * t)
        else:
            Lp = om['llum']

            def aterra(P):
                h = max(1.0, Lp[1] - P[1])
                t = Lp[1] / h
                return (Lp[0] + (P[0] - Lp[0]) * t, Lp[2] + (P[2] - Lp[2]) * t)
        pts = []
        for i in range(25):
            l = -LS + (NL + LS + LB) * i / 24
            r = nau_r(l)
            for j in range(16):
                ph = 2 * math.pi * j / 16
                pts.append(self.p(l, r * math.cos(ph), NY + r * math.sin(ph)))
        for l, c in TANCS:
            pts.append(self.p(l, c, NY + math.sqrt(max(0.0, nau_r(l) ** 2 - c * c)) + 1.3 * R_TANC))
        for c, y in MOTORS:
            pts.append(self.p(MOTOR_L[1], c, NY + y))
        pts.append(self.LLUM_NAV)
        polis = [[aterra(P) for P in pts]]
        if rampa:
            polis.append([aterra(P) for P in self.rampa_cantons()])
        for l in POTES_L:                                                    # les potes
            for cs in (1, -1):
                polis.append([aterra(self.p(l + dl, cs * c, y)) for dl in (-5, 5) for c, y in
                              ((nau_r(l) * 0.6, NY - nau_r(l) * 0.8), (92, 28), (104, 0))])
        eix = (self.p(-LS, 0, 0), self.p(NL + LB, 0, 0))
        for q in polis:
            self._fosc_poligon(e, _convex(q), k_, esv, eix)
        for l in POTES_L:                                                    # el contacte dels peus
            for cs in (1, -1):
                F = self.p(l + 8, cs * 104, 0)
                self._fosc_poligon(e, _convex([(F[0] + 19 * self.esc * math.cos(a), F[2] + 19 * self.esc * math.sin(a))
                                               for a in [i * math.pi / 6 for i in range(12)]]), 0.35, None, eix)

    def _fosc_poligon(self, e, poli, k, esv, eix):
        """Enfosqueix el terra dins un polígon convex del món (x, z), amb les vores esvaïdes."""
        cam = self.cam
        scr = []
        for x, z in poli:
            if cam.vista((x, 0, z))[2] < 2:
                return
            u, v, _ = cam.projecta((x, 0, z))
            scr.append((u, v))
        if len(scr) < 3:
            return
        P = e.cv.P
        edges = list(zip(scr, scr[1:] + scr[:1]))
        (ax, az), (bx, bz) = (eix[0][0], eix[0][2]), (eix[1][0], eix[1][2])
        for X, Y in e._scan(scr):
            xc, yc = X + 0.5, Y + 0.5
            dmin = 1e9
            for (x0, y0), (x1, y1) in edges:
                ex, ey = x1 - x0, y1 - y0
                ln = math.hypot(ex, ey) or 1
                dmin = min(dmin, abs((xc - x0) * ey - (yc - y0) * ex) / ln)
            kk = k * min(1.0, dmin / 2.5)
            if esv:
                g = _terra_de(cam, xc, yc)
                if g is not None:
                    dx, dz = bx - ax, bz - az
                    q = max(0.0, min(1.0, ((g[0] - ax) * dx + (g[1] - az) * dz) / (dx * dx + dz * dz)))
                    d = math.hypot(g[0] - ax - dx * q, g[1] - az - dz * q)
                    kk *= max(0.5, 1 - 0.5 * d / esv)
            if kk <= 0:
                continue
            if kk < 0.5 and kk * 2 < B4[Y & 3][X & 3]:
                continue
            o = P[X, Y]
            m = 1 - min(0.85, kk)
            P[X, Y] = (int(o[0] * m), int(o[1] * m), int(o[2] * m), o[3])

    # ── en pantalla (després de l'escena) ──
    def resplendor(self, cv, cam=None, k=1.0):
        """La claror del finestral i de la porta (oberta i encesa), en pantalla."""
        cam = cam or self.cam
        u, v = self.xy(cam, self.CABINA)
        cv.glow(u, v, max(4, round(70 * cam.escala(self.CABINA) * self.esc)), (255, 200, 120), 0.3 * k)
        u, v = self.xy(cam, self.PORTA)
        cv.glow(u, v, max(4, round(56 * cam.escala(self.PORTA) * self.esc)), (255, 190, 110), 0.35 * k)

    def llum_nav(self, cv, encès=True, cam=None, apagat=False):
        """El llum de navegació, vermell (encès: amb el halo; `apagat`: la nau sense corrent)."""
        cam = cam or self.cam
        u, v = self.xy(cam, self.LLUM_NAV)
        cv.flat(u, v, (255, 80, 60) if encès else (60, 22, 22) if apagat else (120, 30, 30))
        if encès:
            cv.glow(u, v, 5, (255, 80, 60), 0.6)

    def brasa(self, cv, encesa=True, cam=None):
        """La brasa dels broquets dels motors (o el sutge fred)."""
        cam = cam or self.cam
        for P in self.TOVERES:
            u, v = self.xy(cam, P)
            if 0 <= u < cv.w and 0 <= v < cv.h:
                cv.flat(u, v, (255, 140, 60) if encesa else (60, 46, 44))


def _convex(pts):
    """L'envolupant convexa (x, z), en sentit antihorari."""
    pts = sorted(set(pts))
    if len(pts) < 3:
        return pts

    def cr(o, a, b):
        return (a[0] - o[0]) * (b[1] - o[1]) - (a[1] - o[1]) * (b[0] - o[0])
    lo, hi = [], []
    for p in pts:
        while len(lo) >= 2 and cr(lo[-2], lo[-1], p) <= 0:
            lo.pop()
        lo.append(p)
    for p in reversed(pts):
        while len(hi) >= 2 and cr(hi[-2], hi[-1], p) <= 0:
            hi.pop()
        hi.append(p)
    return lo[:-1] + hi[:-1]


def _terra_de(cam, u, v):
    """El punt del terra (x, z) que es veu al píxel (u, v), o None (el cel)."""
    x1, y2, z2 = (u - cam.centre[0]) / cam.f, -(v - cam.centre[1]) / cam.f, 1.0
    dy = y2 * cam._cp - z2 * cam._sp
    z1 = y2 * cam._sp + z2 * cam._cp
    dx = x1 * cam._cy + z1 * cam._sy
    dz = -x1 * cam._sy + z1 * cam._cy
    if dy >= -1e-6:
        return None
    t = -cam.pos[1] / dy
    return cam.pos[0] + dx * t, cam.pos[2] + dz * t
