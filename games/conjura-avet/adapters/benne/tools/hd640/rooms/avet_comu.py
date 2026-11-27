"""
La Conjura de l'Avet — el dibuix comú de l'avet caigut contra l'absis de Sant Joan (sales `mur_avet`, `judici`,
`epileg`, `portada`, `proleg` i `credits`). EN 3D, a 1×.

Una càmera de lluny, arran de carrer (a 2,2 m, l'horitzó a y = 128: una mica contrapicada, el que és alt queda
alt), mirant el carrer de cara. El món: x a la dreta, y amunt, z cap al fons; 1 unitat = 1 px a la distància on un
personatge fa la seva mida (z = F); un metre són ≈52 unitats.

  - **L'absis**, a la dreta, en 3/4: el semicilindre de gres rosat amb el sòcol, les arcuacions cegues de baix, la
    imposta, les arcades de dalt amb columnes i capitells i tres finestres, la cornisa amb dents de serra i la
    teulada cònica; darrere, el mur de llevant del creuer amb el frontó, les arcuacions llombardes i l'òcul, i a la
    dreta el mur del monestir amb la porta (`porta_monestir`).
  - **El mur de l'hort**, de pedra seca, de l'esquerra fins a l'absis; amb el portell del camí del riu a l'esquerra
    (`cami_riu`) i esbotzat on l'avet hi ha caigut al damunt.
  - **L'avet**, ajagut: les arrels aixecades a l'esquerra (una paret de terra més alta que l'Iri, amb les arrels
    arrencades i, a baix, dues arrels tallades de serra: la cara plana i clara), el forat al davant, i el tronc que
    travessa la sala en diagonal, de dalt a l'esquerra cap al mig, damunt el mur, amb la capçada a l'hort fins
    gairebé a tocar l'absis. És la cosa més gran del joc.
  - **El carrer**, de terra trepitjada i pedres, amb bassals, i les branques escampades davant les arrels.
  - Al fons: l'hort, les cases de Sant Joan, el campanar del monestir i les muntanyes.

L'escena es pinta amb un traçador de raigs en numpy (cada superfície és analítica: el pla del terra, els murs, el
cilindre i el con de l'absis, el disc de les arrels) i l'avet amb «taques» de branca ordenades de lluny a prop, tot
amb una memòria de profunditat: així les branques passen per davant i per darrere del mur. Cada píxel recorda qui
l'ha pintat (`Vista.ids`, `Vista.own`), per a les capes del davant i la geometria.

Els estats (`Estat`): la llum (`pluja`, `sol`, `primavera`, `nit`, `llamp`), l'avet (`ajagut`, `dret`, `cap`, o un
angle de caiguda), les branques del carrer (`pas`, `apartades`, `cap`), el mur (`esbotzat`, `sencer`, `arreglat`) i
les coses de cada sala (el faristol, la cera, el poble...). `render(estat)` → imatge RGBA de 640×360 (l'escena fins
a `vista.h`).
"""
import functools
import math
from dataclasses import dataclass, field, replace

import numpy as np
from PIL import Image

import hd640  # noqa: F401  (posa la llibreria de dibuix a 640×360)
from hd.pix import B4
from hd640.tres_d import Camera

W, H = 640, 360
RH = 260                    # l'escena es pinta fins aquí (a sota, el HUD)
F = 440.0
CAMY = 115.0
HOR = 128.0
CAM = Camera(pos=(0.0, CAMY, 0.0), yaw=0.0, pitch=0.0, f=F, centre=(320.0, HOR))
M = 52.0                    # unitats per metre

_B4 = np.array(B4)


# ─── Rampes (fosc → clar) ────────────────────────────────────────────────────

def _r(*cols):
    return np.array(cols, dtype=np.float64)


GRES = _r((46, 26, 30), (72, 40, 42), (102, 60, 54), (132, 82, 68), (160, 104, 84), (186, 128, 102),
          (208, 152, 122), (226, 178, 148), (240, 204, 178))
OCRE = _r((50, 34, 28), (80, 56, 40), (112, 80, 54), (144, 106, 70), (172, 132, 88), (198, 158, 110),
          (220, 186, 138), (236, 210, 168))
TEULA = _r((40, 20, 18), (66, 32, 26), (96, 46, 32), (128, 64, 40), (158, 86, 52), (184, 110, 68),
           (206, 138, 90))
PEDRA = _r((36, 34, 34), (58, 54, 50), (82, 76, 68), (108, 100, 88), (134, 124, 108), (160, 150, 130),
           (186, 176, 156), (210, 202, 182))
TERRA = _r((24, 18, 16), (40, 30, 24), (58, 44, 32), (78, 60, 42), (100, 78, 54), (122, 98, 68),
           (146, 120, 86), (170, 144, 106))
FANG = _r((18, 14, 12), (30, 22, 18), (44, 34, 26), (60, 46, 34), (78, 60, 44), (98, 78, 58))
AVET = _r((6, 14, 14), (10, 22, 20), (14, 32, 26), (20, 44, 32), (28, 58, 40), (38, 74, 48),
          (52, 92, 58), (72, 112, 70), (98, 134, 84))
ESCORÇA = _r((16, 10, 10), (28, 18, 16), (42, 28, 22), (58, 40, 30), (76, 54, 38), (96, 70, 48),
             (118, 88, 60))
ARREL = _r((30, 24, 20), (50, 40, 32), (74, 60, 46), (100, 82, 62), (128, 106, 80), (156, 132, 102))
TALL = _r((96, 62, 36), (138, 96, 56), (176, 132, 82), (206, 166, 110), (228, 196, 142), (242, 220, 176))
RESINA = _r((90, 44, 10), (150, 84, 16), (204, 132, 30), (240, 184, 70), (255, 226, 140))
FUSTA = _r((20, 12, 10), (36, 22, 16), (54, 34, 22), (74, 48, 30), (96, 64, 40), (120, 82, 52),
           (146, 104, 68))
CERA = _r((40, 4, 8), (90, 8, 14), (150, 16, 20), (200, 34, 30), (236, 70, 56), (255, 140, 120))
PERGAMI = _r((70, 60, 50), (120, 104, 84), (168, 150, 120), (206, 190, 156), (232, 220, 188),
             (248, 242, 220))
HERBA = _r((14, 24, 14), (22, 38, 20), (32, 54, 26), (46, 72, 32), (64, 92, 40), (88, 114, 50),
           (116, 138, 64), (148, 164, 86))
MOLSA = _r((20, 30, 14), (36, 50, 20), (56, 72, 28), (80, 96, 38), (108, 122, 52), (140, 150, 72))
FOSC = _r((4, 4, 8), (10, 10, 16), (18, 18, 26))


# ─── Soroll vectoritzat ──────────────────────────────────────────────────────

def _hash(ix, iy, seed):
    h = (ix.astype(np.int64) * 374761393 + iy.astype(np.int64) * 668265263 + seed * 1442695041) & 0xFFFFFFFF
    h = ((h ^ (h >> 13)) * 1274126177) & 0xFFFFFFFF
    return ((h ^ (h >> 16)) & 0xFFFF) / 65535.0


def hnp(x, y, seed=0):
    """Soroll blanc determinista (0..1) per a enters (arrays)."""
    return _hash(np.asarray(x), np.asarray(y), seed)


def vnoise(u, v, seed=0):
    u, v = np.asarray(u, dtype=np.float64), np.asarray(v, dtype=np.float64)
    x0, y0 = np.floor(u), np.floor(v)
    fx, fy = u - x0, v - y0
    fx, fy = fx * fx * (3 - 2 * fx), fy * fy * (3 - 2 * fy)
    a, b = _hash(x0, y0, seed), _hash(x0 + 1, y0, seed)
    c, d = _hash(x0, y0 + 1, seed), _hash(x0 + 1, y0 + 1, seed)
    return a + (b - a) * fx + (c - a) * fy + (a - b - c + d) * fx * fy


def fbm(u, v, seed=0, octaves=3):
    s, amp, tot = 0.0, 1.0, 0.0
    for o in range(octaves):
        s = s + vnoise(np.asarray(u) * 2 ** o, np.asarray(v) * 2 ** o, seed + o * 17) * amp
        tot += amp
        amp *= 0.5
    return s / tot


def smooth(a, b, t):
    t = np.clip((np.asarray(t, dtype=np.float64) - a) / (b - a), 0, 1)
    return t * t * (3 - 2 * t)


def _n(v):
    v = np.asarray(v, dtype=np.float64)
    return v / np.linalg.norm(v)


# ─── La vista: raigs, profunditat, qui ha pintat cada píxel ──────────────────

class Vista:
    """Un llenç de `h` files per a la càmera `cam`: els raigs de cada píxel, el color (en nivells de rampa ja triats,
    RGB), la profunditat (z de càmera) i l'amo de cada píxel."""

    def __init__(self, cam=CAM, h=RH, w=W):
        self.cam, self.h, self.w = cam, h, w
        X, Y = np.meshgrid(np.arange(w), np.arange(h))
        self.X, self.Y = X, Y
        xc = (X + 0.5 - cam.centre[0]) / cam.f
        yc = -(Y + 0.5 - cam.centre[1]) / cam.f
        # de l'espai de càmera al món (la inversa de Camera.vista), amb z de càmera = 1
        cp, sp, cy, sy = cam._cp, cam._sp, cam._cy, cam._sy
        dy = yc * cp - 1.0 * sp
        z1 = yc * sp + 1.0 * cp
        dx = xc * cy + z1 * sy
        dz = -xc * sy + z1 * cy
        self.D = np.stack([dx, dy, dz], axis=-1)            # (h, w, 3): P = O + t·D, amb t = z de càmera
        self.O = np.array(cam.pos, dtype=np.float64)
        self.col = np.zeros((h, w, 3), np.float64)
        self.z = np.full((h, w), np.inf)
        self.own = np.zeros((h, w), np.int32)
        self.ids = ['']
        self.bayer = _B4[Y & 3, X & 3]
        self.emissiu = np.zeros((h, w), bool)          # els llums: no els toca el color de la nit

    def idx(self, sid):
        if sid not in self.ids:
            self.ids.append(sid)
        return self.ids.index(sid)

    def punt(self, t):
        return self.O + self.D * t[..., None]

    def pinta(self, m, t, rgb, sid, prof=True):
        """Pinta els píxels de `m` que són més a prop que el que hi ha (rgb: (h, w, 3) o (N, 3) per a m)."""
        if prof:
            m = m & (t < self.z)
        if not m.any():
            return m
        self.col[m] = rgb[m] if rgb.ndim == 3 else rgb
        self.z[m] = t[m] if np.ndim(t) else t
        self.own[m] = self.idx(sid)
        return m

    def to(self, ramp, lvl, m=None):
        """Nivell → color de la rampa, amb el tramat de Bayer (com hd.pix.Canvas.put)."""
        b = self.bayer if m is None else self.bayer[m]
        i = np.clip(np.floor(lvl + b - 0.5), 0, len(ramp) - 1).astype(int)
        return ramp[i]

    def imatge(self):
        a = np.zeros((H, self.w, 4), np.uint8)
        a[:self.h, :, :3] = np.clip(self.col, 0, 255).astype(np.uint8)
        a[:self.h, :, 3] = 255
        a[self.h:, :, 3] = 255
        return Image.fromarray(a, 'RGBA')

    def mascara(self, sids):
        ids = [i for i, s in enumerate(self.ids) if s in sids]
        return np.isin(self.own, ids)


# ─── Interseccions (vectoritzades) ───────────────────────────────────────────

def x_pla_y(v, h):
    """El pla horitzontal y = h: → t (inf on no hi arriba)."""
    dy = v.D[..., 1]
    with np.errstate(divide='ignore', invalid='ignore'):
        t = (h - v.O[1]) / dy
    return np.where(t > 0.5, t, np.inf)


def x_pla(v, P0, n):
    n = np.asarray(n, dtype=np.float64)
    den = v.D @ n
    with np.errstate(divide='ignore', invalid='ignore'):
        t = (np.asarray(P0) - v.O) @ n / den
    return np.where((t > 0.5) & (den < 0), t, np.inf)       # només la cara que mira la càmera


def x_cilindre(v, c, R):
    """Cilindre vertical d'eix (c[0], c[1]) (x, z) i radi R: la cara de fora més propera."""
    Dx, Dz = v.D[..., 0], v.D[..., 2]
    ox, oz = v.O[0] - c[0], v.O[2] - c[1]
    a = Dx * Dx + Dz * Dz
    b = 2 * (Dx * ox + Dz * oz)
    cc = ox * ox + oz * oz - R * R
    disc = b * b - 4 * a * cc
    with np.errstate(invalid='ignore'):
        t = (-b - np.sqrt(disc)) / (2 * a)
    return np.where((disc > 0) & (t > 0.5), t, np.inf)


def x_con(v, c, R, y0, ya):
    """Con vertical (la teulada de l'absis): radi R a y0, l'àpex a ya. → t de la cara de fora."""
    k = R / (ya - y0)
    Dx, Dy, Dz = v.D[..., 0], v.D[..., 1], v.D[..., 2]
    ox, oz, oy = v.O[0] - c[0], v.O[2] - c[1], ya - v.O[1]
    a = Dx * Dx + Dz * Dz - k * k * Dy * Dy
    b = 2 * (Dx * ox + Dz * oz + k * k * Dy * oy)
    cc = ox * ox + oz * oz - k * k * oy * oy
    disc = b * b - 4 * a * cc
    with np.errstate(invalid='ignore', divide='ignore'):
        s = np.sqrt(disc)
        t1, t2 = (-b - s) / (2 * a), (-b + s) / (2 * a)
    best = np.full(t1.shape, np.inf)
    for t in (t2, t1):
        y = v.O[1] + Dy * t
        ok = (disc > 0) & (t > 0.5) & (y >= y0) & (y <= ya)
        best = np.where(ok & (t < best), t, best)
    return best


# ─── La llum ────────────────────────────────────────────────────────────────

@dataclass(frozen=True)
class Estat:
    llum: str = 'pluja'             # pluja | sol | primavera | nit | llamp
    arbre: object = 'ajagut'        # ajagut | dret | cap (l'epíleg: rodanxes) | un angle de caiguda (radians, 0 = dret)
    branques: str = 'pas'           # pas | apartades | cap
    mur: str = 'esbotzat'           # esbotzat | sencer | arreglat
    cera: bool = False              # el punt vermell al fons del forat
    cera_agafada: bool = False      # el fang remenat on era
    faristol: bool = False
    ordre: bool = False
    branca_trencada: bool = False
    forat: str = 'forat'            # forat (les arrels acabades d'arrencar) | vell (l'epíleg) | cap (l'avet dret)
    extres: tuple = ()              # coses de cada sala: ('rodanxes', 'carretilla', 'forat_nou', ...)
    cam: object = None              # una altra càmera (les cinemàtiques)
    h: int = RH


SOL_DIR = _n((0.82, 0.50, 0.24))
LLUNA = (118, 58, 11)                   # la lluna dels crèdits (a la pantalla): x, y, radi        # el sol del matí, a la dreta i darrere l'absis
PLUJA_DIR = _n((-0.35, 0.80, -0.45))    # la llum blanca del cel tapat, de dalt i una mica del davant
NIT_DIR = _n((-0.5, 0.6, -0.3))
LLAMP_DIR = _n((-0.2, 0.9, 0.3))


def _llum(e, n, P=None, vis=None):
    """Nivells que suma la llum a una superfície de normal n (…, 3)."""
    ny = n[..., 1]
    if e.llum == 'pluja':
        return -0.4 + 0.9 * (0.5 + 0.5 * ny) + 0.55 * np.clip(n @ PLUJA_DIR, 0, None)
    if e.llum in ('sol', 'primavera'):
        d = np.clip(n @ SOL_DIR, 0, None)
        if vis is not None:
            d = d * vis
        return -0.75 + 1.1 * (0.5 + 0.5 * ny) + 0.25 * (0.5 - 0.5 * ny) + 2.7 * d
    if e.llum == 'nit':
        return -1.8 + 0.6 * (0.5 + 0.5 * ny) + 0.6 * np.clip(n @ NIT_DIR, 0, None)
    if e.llum == 'llamp':
        return -0.4 + 0.8 * (0.5 + 0.5 * ny) + 1.6 * np.clip(n @ LLAMP_DIR, 0, None)
    return 0.0


# ─── La geometria del lloc ───────────────────────────────────────────────────

# L'absis: el semicilindre i el mur de llevant (el creuer) que mira el carrer, girat 40°
ABS_C = (430.0, 1200.0)
ABS_R = 195.0
ABS_TH = math.radians(40)
NW = np.array((-math.cos(ABS_TH), 0.0, -math.sin(ABS_TH)))          # la normal del mur de llevant
TW = np.array((math.sin(ABS_TH), 0.0, -math.cos(ABS_TH)))           # al llarg del mur, cap a la dreta
ABS_Y = {'socol': 14, 'imposta': 140, 'imposta2': 148, 'cornisa': 262, 'teulada': 276, 'apex': 346}
MUR_E = (-360.0, 820.0)                 # el mur de llevant, de t0 a t1 (al llarg de TW)
GABLE = (346.0, 440.0)                  # el frontó: les vores i el cim
MONESTIR_T = 140.0                      # a partir d'aquí el mur del monestir (més baix)
PORTA_T = 300.0                         # la porta del monestir (al llarg de TW)

# El mur de l'hort: de l'esquerra fins al flanc de l'absis
MUR_A, MUR_B = np.array((-1300.0, 0.0, 945.0)), np.array((248.0, 0.0, 1118.0))
MUR_H, MUR_G = 96.0, 26.0
MUR_T = _n(MUR_B - MUR_A)
MUR_N = np.array((MUR_T[2], 0.0, -MUR_T[0]))                         # la cara del carrer (mira la càmera)
MUR_L = float(np.linalg.norm(MUR_B - MUR_A))
PORTELL = (650.0, 735.0)                # el portell del camí del riu (al llarg del mur, des de MUR_A)
TRENCAT = (1240.0, 1420.0)              # on l'avet l'ha esbotzat

# L'avet: el pla de les arrels i el tronc
ARREL_C = np.array((-262.0, 104.0, 668.0))      # el centre del pla de les arrels (i el peu del tronc)
ARREL_R = 114.0
TRONC_D = _n((0.68, 0.0, 0.73))                   # cap on va el tronc (a terra)
TRONC_L = 1320.0
CAPCADA_S0 = 150.0                              # la capçada comença aquí (al tronc)
ARREL_N = _n(-TRONC_D + 0.75 * _n(np.array(CAM.pos) * np.array((1, 0, 1)) - ARREL_C * np.array((1, 0, 1))))
FORAT_C = np.array((-318.0, 0.0, 606.0))         # el centre del forat (davant les arrels)
FORAT_R = (112.0, 62.0)                          # mig llarg (al llarg de les arrels) i mig ample
FORAT_U = _n(np.cross(ARREL_N, (0, 1, 0)))       # al llarg de les arrels, a terra
CERA_P = np.array((-300.0, 0.0, 606.0))

FARISTOL = np.array((46.0, 0.0, 505.0))


def tronc_y(s):
    """L'alçada de l'eix del tronc a la distància s del peu: surt del centre de les arrels, s'aguanta damunt el mur
    i la punta descansa sobre les branques aixafades."""
    s = np.asarray(s, dtype=np.float64)
    return np.where(s < 560, ARREL_C[1] + (128 - ARREL_C[1]) * np.clip(s / 560, 0, 1) ** 0.7,
                    128 - (s - 560) / (TRONC_L - 560) * 66)


def tronc_r(s):
    return 30 * np.clip(1 - np.asarray(s) / TRONC_L, 0, 1) ** 0.75 + 2.5


# ─── El cel i el fons ────────────────────────────────────────────────────────

def cel(v, e):
    Y, X = v.Y.astype(np.float64), v.X.astype(np.float64)
    h = v.cam.centre[1]
    t = np.clip(Y / max(1.0, h + 10), 0, 1)
    if e.llum == 'pluja':
        c0, c1 = np.array((206, 208, 210)), np.array((236, 236, 232))
        rgb = c0 + (c1 - c0) * t[..., None] ** 0.8
        n = fbm(X / 90, Y / 22, 5, 4)
        rgb = rgb - (n[..., None] - 0.5) * 22 * (1 - t[..., None] * 0.6)
    elif e.llum in ('sol', 'primavera'):
        c0, c1 = np.array((62, 120, 196)), np.array((176, 208, 230))
        if e.llum == 'primavera':
            c0, c1 = np.array((84, 140, 210)), np.array((196, 220, 232))
        rgb = c0 + (c1 - c0) * t[..., None] ** 1.3
        n = fbm(X / 120, Y / 18, 9, 4)
        k = smooth(0.58, 0.72, n) * (0.4 + 0.6 * t)
        nub = np.array((238, 240, 240)) - (1 - smooth(0.6, 0.8, fbm(X / 30, (Y + 3) / 8, 3)))[..., None] * 30
        rgb = rgb * (1 - k[..., None]) + nub * k[..., None]
    elif e.llum == 'llamp':
        # els núvols de tempesta encesos per dins: blau de pissarra, no el cel de dia
        c0, c1 = np.array((70, 76, 112)), np.array((132, 140, 176))
        rgb = c0 + (c1 - c0) * t[..., None]
        n = fbm(X / 70, Y / 20, 7, 4)
        rgb = rgb - (n[..., None] - 0.5) * 110
    elif 'lluna' in e.extres:   # nit clara de primavera
        c0, c1 = np.array((8, 12, 30)), np.array((40, 52, 86))
        rgb = c0 + (c1 - c0) * t[..., None] ** 1.4
        est = (hnp(X, Y, 91) > 0.9965) & (Y < h - 20)
        est2 = (hnp(X // 2, Y // 2, 93) > 0.9985) & (Y < h - 30)
        rgb = np.where(est[..., None], np.array((200, 206, 230.0)), rgb)
        rgb = np.where(est2[..., None], np.array((150, 160, 196.0)), rgb)
        mx, my, mr = LLUNA
        d = np.hypot(X - mx, Y - my)
        rgb = rgb + (np.clip(1 - d / 90, 0, 1) ** 2)[..., None] * np.array((40, 46, 60.0))
        lluna = d < mr
        fase = np.hypot(X - mx - 4, Y - my + 2) < mr * 0.92
        lv = 1 - 0.15 * fbm(X / 3, Y / 3, 95, 2)
        rgb = np.where((lluna & ~fase)[..., None], np.array((238, 232, 206.0)) * lv[..., None], rgb)
        rgb = np.where((lluna & fase)[..., None], np.array((30, 36, 64.0)), rgb)
    else:   # nit de tempesta
        c0, c1 = np.array((10, 12, 26)), np.array((40, 46, 70))
        rgb = c0 + (c1 - c0) * t[..., None]
        n = fbm(X / 70, Y / 20, 7, 4)
        rgb = rgb + (n[..., None] - 0.45) * np.array((30, 34, 46))
    m = np.ones((v.h, v.w), bool)
    v.pinta(m, np.full((v.h, v.w), 1e9), rgb, 'cel')


def _boira(e):
    """(color de l'aire, distància a la qual el fons ja és mig boira)."""
    return {'pluja': (np.array((222, 224, 224)), 2600.0), 'sol': (np.array((176, 204, 226)), 9000.0),
            'primavera': (np.array((190, 214, 228)), 9000.0), 'nit': (np.array((30, 36, 56)), 3500.0),
            'llamp': (np.array((196, 204, 226)), 3500.0)}[e.llum]


def fons(v, e):
    """Les muntanyes i les cases de Sant Joan, lluny; el campanar del monestir."""
    X, Y = v.X.astype(np.float64), v.Y.astype(np.float64)
    hor = v.cam.centre[1]
    aire, _ = _boira(e)
    # dues serralades
    for (zdist, alt, fq, seed, k, ramp) in ((14000.0, 1900.0, 260.0, 3, 0.75, PEDRA), (7000.0, 700.0, 140.0, 5, 0.55, HERBA)):
        sc = v.cam.f / zdist
        top = hor - (v.cam.pos[1] * -1 + alt * (0.35 + 0.65 * fbm(X / fq, 0.3, seed, 4))) * sc
        top = hor - (alt * (0.35 + 0.65 * fbm(X / fq, 0.3, seed, 4)) - v.cam.pos[1]) * sc
        m = Y >= top
        lvl = 3.4 + (fbm(X / 18, Y / 9, seed + 2, 3) - 0.5) * 1.6 - (Y - top) * 0.02
        rgb = v.to(ramp, lvl)
        rgb = rgb * (1 - k) + aire * k
        v.pinta(m, np.full(m.shape, zdist), rgb, 'muntanyes')
    # les cases del poble, a l'esquerra (darrere el mur i l'hort), i el monestir a la dreta
    rng = np.random.default_rng(11)
    cases = []
    x = -3600.0
    while x < 2600:
        w = rng.uniform(140, 300)
        cases.append((x, rng.uniform(2300, 3300), w, rng.uniform(190, 330), rng.uniform(-0.5, 0.5)))
        x += w * rng.uniform(0.8, 1.1)
    for (cx, cz, w, hh, rot) in sorted(cases, key=lambda c: -c[1]):
        _casa(v, e, cx, cz, w, hh, rot)
    _campanar(v, e)


def _casa(v, e, cx, cz, w, hh, rot):
    """Una casa llunyana: la façana (un pla de cara, una mica girat) amb la teulada i una finestra fosca."""
    n = _n((math.sin(rot) * 0.4, 0, -1))
    t = x_pla(v, (cx, 0, cz), n)
    P = v.punt(np.where(np.isinf(t), 0, t))
    tang = np.array((-n[2], 0, n[0]))
    s = (P - np.array((cx, 0, cz))) @ tang
    y = P[..., 1]
    roof = hh + (w / 2 - np.abs(s)) * 0.32
    m = np.isfinite(t) & (np.abs(s) < w / 2) & (y > 0) & (y < roof)
    tex = fbm(s / 30, y / 20, int(cx) & 255, 2)
    lvl = 3.6 + (tex - 0.5) * 1.2
    win = (np.abs(((s + w) % 70) - 35) < 7) & (np.abs(y - hh * 0.6) < 14)
    lvl = np.where(win, 1.0, lvl)
    teula = y > hh - 6
    rgb = np.where(teula[..., None], v.to(TEULA, lvl - 0.6 + 0 * y), v.to(OCRE, lvl + _llum(e, np.broadcast_to(n, P.shape))))
    aire, dist = _boira(e)
    k = np.clip(t / (t + dist), 0, 0.9)[..., None]
    rgb = rgb * (1 - k) + aire * k
    v.pinta(m, t, rgb, 'cases')


def _campanar(v, e):
    """El campanar del monestir, darrere l'absis a la dreta: una torre quadrada amb finestres geminades."""
    c = np.array((820.0, 0.0, 2350.0))
    hw, top = 120.0, 760.0
    for n in (_n((-1, 0, -0.35)), _n((0.35, 0, -1))):
        P0 = c + n * hw
        t = x_pla(v, P0, n)
        P = v.punt(np.where(np.isinf(t), 0, t))
        tang = np.array((-n[2], 0, n[0]))
        s = (P - P0) @ tang
        y = P[..., 1]
        m = np.isfinite(t) & (np.abs(s) < hw) & (y > 0) & (y < top + (hw - np.abs(s)) * 0.3)
        row = np.floor(y / 22)
        bl = ((s + (row % 2) * 20) % 40 < 2) | (y % 22 < 2)
        lvl = 3.8 + (hnp(np.floor((s + 400 + (row % 2) * 20) / 40), row, 3) - 0.5) * 0.9 - bl * 0.8
        for wy in (520.0, 640.0):
            fin = (np.abs(np.abs(s) - 34) < 16) & (y > wy) & (y < wy + 70 - np.maximum(0, (np.abs(np.abs(s) - 34)) ** 2 / 16))
            lvl = np.where(fin, 0.6, lvl)
        teu = y > top - 4
        lvl = lvl + _llum(e, np.broadcast_to(n, P.shape))
        rgb = np.where(teu[..., None], v.to(TEULA, lvl - 0.5), v.to(GRES, lvl - 0.4))
        aire, dist = _boira(e)
        k = np.clip(t / (t + dist) * 1.1, 0, 0.9)[..., None]
        rgb = rgb * (1 - k) + aire * k
        v.pinta(m, t, rgb, 'campanar')


# ─── El terra ───────────────────────────────────────────────────────────────

def _bassals(x, z):
    """Els bassals del carrer (0..1, on > 0.5 és aigua), al món."""
    n = fbm(x / 64, z / 40, 21, 3) * 0.8 + 0.2 * fbm(x / 18, z / 12, 23, 2)
    return n


def _rodera(x, z):
    """La distància (al món) a la rodera més propera: dues, a 34 unitats, que van de la plaça a la porta."""
    # el camí: z = 430 + 0.19·(x + 700) (puja cap al fons a la dreta), amb una mica d'ondulació
    zc = 430 + 0.19 * (x + 700) + 14 * np.sin(x / 160)
    d = np.minimum(np.abs(z - zc - 17), np.abs(z - zc + 17))
    return np.where((x > -900) & (x < 520), d, 99.0)


def terra(v, e):
    t = x_pla_y(v, 0.0)
    P = v.punt(np.where(np.isinf(t), 0, t))
    x, z = P[..., 0], P[..., 2]
    m = np.isfinite(t) & (z < 30000)
    # terra trepitjada, amb pedres que surten (cel·les del món: grans a prop, petites al fons)
    cell = 26.0
    gx, gz = np.floor(x / cell), np.floor(z / cell)
    jx = hnp(gx, gz, 4) * 0.7 + 0.15
    jz = hnp(gx, gz, 5) * 0.7 + 0.15
    dx, dz = x / cell - gx - jx, z / cell - gz - jz
    dd = np.sqrt(dx * dx + dz * dz)
    pedra = (dd < 0.18 + hnp(gx, gz, 6) * 0.22) & (hnp(gx, gz, 7) > 0.45)
    far = smooth(900, 3000, z)
    lvl = 3.1 + (fbm(x / 60, z / 40, 17) - 0.5) * 1.6 + (fbm(x / 12, z / 9, 19, 2) - 0.5) * 1.0 * (1 - far)
    lvl = lvl + (hnp(np.floor(x / 3), np.floor(z / 3), 20) - 0.5) * 0.7 * (1 - far)        # el gra de la terra
    lvl = np.where(pedra & (far < 0.9), 4.3 + (0.18 - dd) * 5 - (dz > 0.08) * 1.1, lvl)
    # les roderes dels carros: de la plaça (a l'esquerra) cap a la porta del monestir, en diagonal
    rod = _rodera(x, z)
    lvl = np.where(rod < 5, lvl - 1.0 + rod * 0.08, np.where(rod < 9, lvl + 0.5, lvl))
    # les roderes del carrer: de l'esquerra a la porta del monestir, i el camí del riu cap al portell
    ramp_id = np.zeros(t.shape, int)                         # 0 terra, 1 herba, 2 fang
    # l'hort, darrere el mur: herba i solcs
    rel = (P - MUR_A) @ MUR_N
    hort = rel < -MUR_G
    solc = np.sin(((P - MUR_A) @ MUR_T) / 18) > 0.3
    lvl = np.where(hort, 3.0 + solc * 0.8 + (fbm(x / 30, z / 30, 31) - 0.5) * 1.4, lvl)
    ramp_id = np.where(hort, 1, ramp_id)
    # el camí del riu: surt pel portell i se'n va cap al fons a l'esquerra, entre els horts
    pc = MUR_A + MUR_T * ((PORTELL[0] + PORTELL[1]) / 2)
    dcami = np.array((-0.55, 0.0, 1.0))
    dcami = dcami / np.linalg.norm(dcami)
    rel_c = P - pc
    along = rel_c @ dcami
    perp = np.abs(rel_c @ np.array((dcami[2], 0, -dcami[0])))
    cami = (along > -40) & (along < 2600) & (perp < 34 - along * 0.004 + vnoise(along / 60, 0.5, 33) * 8)
    lvl = np.where(cami, 3.4 + (fbm(x / 20, z / 20, 35) - 0.5) * 1.2 - (perp > 24) * 0.6, lvl)
    ramp_id = np.where(cami, 0, ramp_id)
    # el peu del mur, l'absis i les arrels: herba i fang (els racons)
    voraabs = np.hypot(x - ABS_C[0], z - ABS_C[1]) - ABS_R
    herbeta = ((voraabs < 26) | ((rel > 0) & (rel < 34))) & (fbm(x / 14, z / 14, 41) > 0.42)
    if e.llum != 'nit':
        lvl = np.where(herbeta & ~hort, 3.4 + (fbm(x / 6, z / 6, 43) - 0.5) * 2, lvl)
        ramp_id = np.where(herbeta & ~hort, 1, ramp_id)
    # llum, ombra
    nrm = np.broadcast_to(np.array((0.0, 1.0, 0.0)), P.shape)
    vis = ombra_sol(P, e) if e.llum in ('sol', 'primavera') else None
    L = _llum(e, nrm, P, vis)
    if e.llum in ('pluja', 'nit', 'llamp'):
        L = L - 0.5                                          # la terra mullada, més fosca
    # foscor als racons: al peu del mur, de l'absis i de les arrels
    ao = 0.9 * np.exp(-np.maximum(voraabs, 0) / 26) + 0.8 * np.exp(-np.abs(rel) / 30) * (rel > 0)
    lvl = lvl + L - ao
    rgb = np.where((ramp_id == 1)[..., None], v.to(HERBA, lvl - 0.4), v.to(TERRA, lvl))
    # el forat de les arrels
    if e.forat != 'cap':
        rgb, lvl = _forat(v, e, P, rgb, lvl)
    # bassals: el cel s'hi reflecteix (el reflex de la resta, després: `reflexos`)
    aigua = np.zeros(t.shape, bool)
    if e.llum in ('pluja', 'sol', 'llamp', 'nit') and 'lluna' not in e.extres:
        b = _bassals(x, z)
        lim = {'pluja': 0.585, 'sol': 0.62, 'llamp': 0.585, 'nit': 0.585}[e.llum]
        rod = _rodera(x, z)
        aigua = ((b > lim) | ((rod < 4.5) & (b > lim - 0.12))) & ~hort & (voraabs > 20) & (rel > 30) & (z < 2200) & _fora_forat(P)
    aire, dist = _boira(e)
    k = np.clip((t - 900) / (t - 900 + dist * 1.6), 0, 0.85)[..., None] * (t > 900)[..., None]
    rgb = rgb * (1 - k) + aire * k
    v.pinta(m, t, rgb, 'terra')
    v.aigua = aigua & m
    v.terra_t = t


def _fora_forat(P):
    d = P - FORAT_C
    a, b = d @ FORAT_U, d @ np.cross(FORAT_U, (0, 1, 0))
    return (a / (FORAT_R[0] + 30)) ** 2 + (b / (FORAT_R[1] + 30)) ** 2 > 1


def _forat(v, e, P, rgb, lvl):
    """El forat que han deixat les arrels en aixecar-se: terra remoguda al voltant, fang i aigua al fons."""
    d = P - FORAT_C
    a, b = d @ FORAT_U, d @ np.cross(FORAT_U, (0, 1, 0))
    r = np.sqrt((a / FORAT_R[0]) ** 2 + (b / FORAT_R[1]) ** 2)
    vora = (r < 1.35) & (r >= 1.0)
    dins = r < 1.0
    if e.forat == 'vell':
        # l'epíleg: el forat vell, tapat (la soca hi ha tornat a caure), amb clapes d'herba de vora irregular
        l2 = 3.0 + (fbm(a / 6, b / 5, 61) - 0.5) * 2.4 + (hnp(np.floor(a / 3), np.floor(b / 3), 63) - 0.5) * 1.2
        sel = (r < 0.75 + (fbm(a / 14, b / 10, 65) - 0.5) * 0.9) & (fbm(a / 9, b / 7, 67) > 0.36)
        rgb = np.where(sel[..., None], v.to(HERBA, l2 + _llum(e, np.array((0, 1, 0.0))) * 0.7), rgb)
        return rgb, lvl
    L = _llum(e, np.array((0, 1, 0.0)))
    # la vora: terra remoguda, grumolls clars i foscos
    lv = 3.6 + (fbm(a / 8, b / 6, 51) - 0.5) * 2.4 + (1.35 - r) * 0.8 + L
    rgb = np.where(vora[..., None], v.to(TERRA, lv), rgb)
    # dins: la paret del forat (la del fons, il·luminada; la del davant no es veu) i el fang del fons
    fons_ = r < 0.55
    paret = dins & ~fons_
    lp = 2.2 + (b < 0) * 1.0 + (fbm(a / 6, b / 4, 53) - 0.5) * 1.6 - (1 - r) * 1.2 + L * 0.6
    rgb = np.where(paret[..., None], v.to(TERRA, lp), rgb)
    lf = 0.8 + (fbm(a / 9, b / 7, 55) - 0.5) * 1.2 + L * 0.4
    rgb = np.where(fons_[..., None], v.to(FANG, lf + 1.2), rgb)
    if e.llum in ('pluja', 'nit', 'llamp'):
        bas = r < 0.36                                       # un bassal fangós al fons
        rgb = np.where(bas[..., None], v.to(FANG, 3.4 + (fbm(a / 5, b / 3, 57) - 0.5) * 1.4), rgb)
    return rgb, lvl


# ─── Les ombres del sol ──────────────────────────────────────────────────────

def _dins(P, e):
    """Si un punt del món és dins d'alguna cosa que fa ombra (per al sol)."""
    x, y, z = P[..., 0], P[..., 1], P[..., 2]
    inside = np.zeros(x.shape, bool)
    # l'absis i l'església
    inside |= (np.hypot(x - ABS_C[0], z - ABS_C[1]) < ABS_R) & (y < ABS_Y['cornisa'] + (ABS_Y['apex'] - ABS_Y['cornisa']) * 0.6)
    C = np.array((ABS_C[0], 0, ABS_C[1]))
    rel_n, rel_t = (P - C) @ NW, (P - C) @ TW
    alt = np.where(rel_t < MONESTIR_T, GABLE[0] + np.maximum(0, 1 - np.abs(rel_t) / 380) * (GABLE[1] - GABLE[0]), 300)
    inside |= (rel_n < 0) & (rel_n > -1400) & (rel_t > MUR_E[0]) & (rel_t < MUR_E[1] + 600) & (y < alt)
    # el mur de l'hort
    if e.mur != 'cap':
        s = (P - MUR_A) @ MUR_T
        nn = (P - MUR_A) @ MUR_N
        trenc = (s > TRENCAT[0]) & (s < TRENCAT[1]) & (e.mur == 'esbotzat')
        port = (s > PORTELL[0]) & (s < PORTELL[1])
        inside |= (np.abs(nn + MUR_G / 2) < MUR_G / 2) & (s > 0) & (s < MUR_L) & (y < MUR_H) & ~trenc & ~port
    # l'avet ajagut (el tronc i la capçada, amb forats: la llum hi passa a clapes)
    if e.arbre == 'ajagut':
        rel = P - ARREL_C * np.array((1, 0, 1))
        s = rel @ TRONC_D
        perp = rel - np.outer(s.ravel(), TRONC_D).reshape(rel.shape)
        dy = y - tronc_y(s)
        rr = np.sqrt((perp * perp).sum(-1) - perp[..., 1] ** 2 + dy * dy)
        inside |= (s > 0) & (s < TRONC_L) & (rr < tronc_r(s))
        env = _capcada_r(s) * (0.75 + 0.35 * vnoise(s / 40, np.arctan2(dy, perp[..., 0]) * 3, 71))
        cl = vnoise(x / 22, (y + z) / 22, 73) > 0.34
        inside |= (s > CAPCADA_S0 - 20) & (s < TRONC_L) & (rr < env) & (y > 0) & cl
        # el pla de les arrels
        q = P - ARREL_C
        inside |= (np.abs(q @ ARREL_N) < 16) & (np.sqrt((q * q).sum(-1)) < ARREL_R)
    if 'abeurador' in e.extres:
        c, hx, hz, hy, rot = ABEURADOR
        q = P - c
        cr, sr = math.cos(rot), math.sin(rot)
        qa, qb = q[..., 0] * cr + q[..., 2] * sr, -q[..., 0] * sr + q[..., 2] * cr
        inside |= (np.abs(qa) < hx) & (np.abs(qb) < hz) & (y < 2 * hy)
    if e.faristol:
        q = P - FARISTOL
        inside |= (np.abs(q[..., 0]) < 18) & (np.abs(q[..., 2]) < 14) & (y < 72) & ((y > 52) | (np.hypot(q[..., 0], q[..., 2]) < 5))
    return inside


def ombra_sol(P, e, passos=40, lluny=2600.0):
    """Visibilitat del sol (0..1) des de cada punt P (…, 3): es camina cap al sol i es mira si s'entra en alguna cosa."""
    shp = P.shape[:-1]
    flat = P.reshape(-1, 3)
    vis = np.ones(flat.shape[0])
    alive = np.ones(flat.shape[0], bool)
    for i in range(1, passos + 1):
        d = (i / passos) ** 1.6 * lluny + 3
        Q = flat[alive] + SOL_DIR * d
        hit = _dins(Q, e)
        idx = np.nonzero(alive)[0][hit]
        vis[idx] = 0.0
        alive[idx] = False
        if not alive.any():
            break
    return vis.reshape(shp)


# ─── L'absis ────────────────────────────────────────────────────────────────

def absis(v, e):
    C3 = np.array((ABS_C[0], 0, ABS_C[1]))
    mullat = -0.55 if e.llum in ('pluja', 'nit', 'llamp') else 0.0
    # el mur de llevant (el creuer) i el del monestir, a la dreta
    t = x_pla(v, C3, NW)
    P = v.punt(np.where(np.isinf(t), 0, t))
    s = (P - C3) @ TW
    y = P[..., 1]
    gab = np.where(s < MONESTIR_T, GABLE[0] + np.maximum(0, 1 - np.abs(s) / 380) * (GABLE[1] - GABLE[0]), 300)
    m = np.isfinite(t) & (s > MUR_E[0]) & (s < MUR_E[1]) & (y > 0) & (y < gab)
    lvl = _carreus(s, y, 26, 15, 81) + mullat
    # les arcuacions llombardes sota el frontó, l'òcul i la cornisa del monestir
    vores = gab - y
    arc_s = (s + 1000) % 34
    arc = (vores > 8) & (vores < 30) & (s < MONESTIR_T) & (np.hypot(arc_s - 17, np.maximum(0, (vores - 22))) < 14)
    lvl = np.where(arc & ((vores - 22) > -6), lvl - 1.4 * ((vores - 22) > 0) - 0.6, lvl)
    lvl = np.where((vores < 8) & (s < MONESTIR_T), lvl + 0.7 - (vores < 3) * 1.6, lvl)
    ocul = np.hypot(s - 0, y - 386) / 22
    lvl = np.where(ocul < 1, np.where(ocul < 0.62, 0.4, lvl + 1.4 - ocul * 1.2), lvl)
    # la porta del monestir, amb l'arc de dovelles
    pd = np.hypot(s - PORTA_T, np.maximum(0, y - 86))
    porta = (pd < 34) & (y < 120)
    lvl = np.where(porta, np.where(pd < 26, 0.9 + (np.abs(s - PORTA_T) % 9 < 1) * -0.6 + (y < 3) * 0.6,
                                   lvl + 0.8 - (np.arctan2(y - 86, s - PORTA_T) * 6 % 1 < 0.15) * 1.4), lvl)
    # la teulada del monestir (a la dreta, més baixa)
    lvl = lvl + _llum(e, np.broadcast_to(NW, P.shape), P, ombra_sol(P, e) if e.llum in ('sol', 'primavera') else None)
    lvl = lvl - 1.2 * np.exp(-y / 30)                       # el peu, a l'ombra
    rgb = v.to(GRES, lvl)
    if e.llum == 'nit':
        oc = ocul < 0.62
        rgb = np.where(oc[..., None], v.to(CALIU, 3.0 - ocul * 2), rgb)
        # la porta del monestir, entreoberta: una ratlla de llum
        ratlla = (np.abs(s - PORTA_T - 3) < 2.2) & (y < 112) & (pd < 26)
        rgb = np.where(ratlla[..., None], v.to(CALIU, 3.6 - y / 80), rgb)
    pint = v.pinta(m, t, rgb, 'absis_mur')
    if e.llum == 'nit':
        v.emissiu |= pint & (oc | ratlla)
    # el semicilindre
    t = x_cilindre(v, ABS_C, ABS_R)
    P = v.punt(np.where(np.isinf(t), 0, t))
    y = P[..., 1]
    a = np.arctan2(P[..., 2] - ABS_C[1], P[..., 0] - ABS_C[0])
    a0 = math.atan2(NW[2], NW[0])
    da = (a - a0 + math.pi) % (2 * math.pi) - math.pi
    m = np.isfinite(t) & (np.abs(da) < math.pi / 2 + 0.02) & (y > 0) & (y < ABS_Y['teulada'])
    nrm = np.stack([np.cos(a), np.zeros_like(a), np.sin(a)], -1)
    s = da * ABS_R                                           # la distància al llarg del mur (0 al mig)
    lvl = _carreus(s, y, 24, 14, 83) + _absis_relleu(s, y)
    if e.llum in ('pluja', 'llamp', 'nit', 'sol'):
        # els regalims de l'aigua, foscos, que baixen de la cornisa
        reg = vnoise(s / 5.0, y / 140.0, 87) > 0.66
        lvl = lvl - reg * smooth(0, 200, y) * (0.7 if e.llum != 'sol' else 0.35)
    vis = ombra_sol(P, e) if e.llum in ('sol', 'primavera') else None
    lvl = lvl + _llum(e, nrm, P, vis) + mullat - 1.2 * np.exp(-y / 24)
    rgb = v.to(GRES, lvl)
    if e.llum == 'nit':
        # de nit, les monges resen matines: les finestres de l'absis, enceses
        fin = _finestres(s, y)
        rgb = np.where(fin[..., None], v.to(CALIU, 3.2 + (y - ABS_Y['imposta2']) / 60 + (hnp(v.X, v.Y // 2, 7) - 0.5)), rgb)
        # i la llum que en surt, a la pedra del voltant
        halo = _halo_finestres(s, y)
        rgb = rgb + halo[..., None] * np.array((60, 30, 6.0))
    pint = v.pinta(m, t, rgb, 'absis')
    if e.llum == 'nit':
        v.emissiu |= pint & fin
    # la teulada cònica, de teules
    t = x_con(v, ABS_C, ABS_R + 10, ABS_Y['teulada'], ABS_Y['apex'])
    P = v.punt(np.where(np.isinf(t), 0, t))
    a = np.arctan2(P[..., 2] - ABS_C[1], P[..., 0] - ABS_C[0])
    da = (a - a0 + math.pi) % (2 * math.pi) - math.pi
    m = np.isfinite(t) & (np.abs(da) < math.pi / 2)
    k = (ABS_R + 10) / (ABS_Y['apex'] - ABS_Y['teulada'])
    nrm = np.stack([np.cos(a), np.full(a.shape, k), np.sin(a)], -1)
    nrm = nrm / np.linalg.norm(nrm, axis=-1, keepdims=True)
    yy = P[..., 1] - ABS_Y['teulada']
    canal = (da * 40) % 1
    lvl = 3.2 + (canal < 0.45) * 0.9 - (canal < 0.08) * 1.4 - (yy % 9 < 1.4) * 0.7 + (fbm(da * 30, yy / 8, 91) - 0.5) * 0.8
    vis = ombra_sol(P, e) if e.llum in ('sol', 'primavera') else None
    lvl = lvl + _llum(e, nrm, P, vis) + mullat * 0.6
    v.pinta(m, t, v.to(TEULA, lvl), 'absis_teulada')


def _carreus(s, y, bw, bh, seed):
    """Carreus de gres: filades de `bh`, peces de ≈`bw`, cada una amb el seu to (rosat o ocre) i les juntes."""
    row = np.floor(y / bh)
    off = hnp(row, 0 * row, seed) * bw
    col = np.floor((s + off + 2000) / bw)
    tone = hnp(col, row, seed + 1)
    jy = (y % bh) < 1.1
    jx = ((s + off + 2000) % bw) < 1.1
    lvl = 4.1 + (tone - 0.5) * 1.1 + (fbm(s / 9, y / 7, seed + 2, 2) - 0.5) * 0.7
    return lvl - (jy | jx) * 0.9 + ((y % bh) > bh - 2.5) * 0.3


CALIU = _r((60, 20, 6), (120, 50, 14), (190, 96, 30), (236, 150, 60), (255, 206, 120), (255, 240, 190))


def _finestres(s, y):
    """Les tres finestres de l'absis (el vidre: on es veu la llum de dins)."""
    Y = ABS_Y
    pas2 = ABS_R * math.pi / 5
    k2 = (s + ABS_R * math.pi / 2) % pas2 - pas2 / 2
    arc2 = Y['cornisa'] - 46
    nwin = np.floor((s + ABS_R * math.pi / 2) / pas2)
    return ((np.abs(k2) < 6) & (y > Y['imposta2'] + 30) & ((y < arc2 - 8) | (np.hypot(k2, y - (arc2 - 8)) < 6))
            & (nwin % 2 == 1))


def _halo_finestres(s, y):
    Y = ABS_Y
    pas2 = ABS_R * math.pi / 5
    k2 = (s + ABS_R * math.pi / 2) % pas2 - pas2 / 2
    nwin = np.floor((s + ABS_R * math.pi / 2) / pas2)
    cy = (Y['imposta2'] + 30 + Y['cornisa'] - 54) / 2
    d = np.hypot(k2 / 1.0, (y - cy) / 2.2)
    return np.where(nwin % 2 == 1, np.clip(1 - d / 34, 0, 1) ** 2, 0)


def _absis_relleu(s, y):
    """Les arcuacions de l'absis (en nivells que se sumen): el sòcol, les arcades cegues de baix, la imposta, les
    arcades de dalt amb les columnes, les finestres i la cornisa."""
    out = np.zeros(s.shape)
    Y = ABS_Y
    # el sòcol
    out += np.where(y < Y['socol'], 0.6 - (y > Y['socol'] - 3) * 1.0, 0)
    # registre de baix: 7 arcs cecs (al semicilindre en caben ≈5 de cara)
    pas = ABS_R * math.pi / 7
    k = (s + ABS_R * math.pi / 2) % pas - pas / 2
    low = (y > Y['socol']) & (y < Y['imposta'])
    arc_y = Y['imposta'] - 32
    rec = np.abs(k) < pas / 2 - 7
    rec &= (y < arc_y) | (np.hypot(k, y - arc_y) < pas / 2 - 7)
    vora = ~rec & ((np.abs(k) < pas / 2 - 3) & ((y < arc_y) | (np.hypot(k, y - arc_y) < pas / 2 - 3)))
    out += np.where(low & rec, -0.9 - 1.3 * smooth(arc_y - 10, arc_y + 26, y) * (k < 0), 0)
    out += np.where(low & vora, 0.7, 0)
    # la imposta (una motllura)
    imp = (y >= Y['imposta']) & (y < Y['imposta2'])
    out += np.where(imp, 0.9 - (y < Y['imposta'] + 2) * 1.5, 0)
    # registre de dalt: 5 arcades grans amb columnes
    pas2 = ABS_R * math.pi / 5
    k2 = (s + ABS_R * math.pi / 2) % pas2 - pas2 / 2
    up = (y > Y['imposta2']) & (y < Y['cornisa'])
    arc2 = Y['cornisa'] - 46
    rec2 = (np.abs(k2) < pas2 / 2 - 9) & ((y < arc2) | (np.hypot(k2, y - arc2) < pas2 / 2 - 9))
    vora2 = ~rec2 & (np.abs(k2) < pas2 / 2 - 4) & ((y < arc2) | (np.hypot(k2, y - arc2) < pas2 / 2 - 4))
    out += np.where(up & rec2, -0.5 - 1.2 * smooth(arc2 - 6, arc2 + 30, y) * (k2 < 0), 0)
    out += np.where(up & vora2, 0.8 - (k2 > 0) * 0.3, 0)
    # les columnes adossades (entre les arcades), amb el capitell fosc
    col = np.abs(np.abs(k2) - (pas2 / 2 - 2)) < 3.2
    capit = (y > arc2 - 14) & (y < arc2)
    out += np.where(up & col & ~capit, 1.2 - (np.abs(k2) > pas2 / 2 - 1) * 1.4, 0)
    out += np.where(up & col & capit, -0.2 + ((y - arc2) % 4 < 1.5) * -0.8, 0)
    # les finestres: estretes, amb arc de mig punt, a les arcades 1, 2 i 3
    nwin = np.floor((s + ABS_R * math.pi / 2) / pas2)
    fin = (np.abs(k2) < 6) & (y > Y['imposta2'] + 30) & ((y < arc2 - 8) | (np.hypot(k2, y - (arc2 - 8)) < 6)) & (nwin % 2 == 1)
    out += np.where(up & fin, -3.6, 0)
    finv = (np.abs(k2) < 9) & ~fin & (y > Y['imposta2'] + 27) & ((y < arc2 - 8) | (np.hypot(k2, y - (arc2 - 8)) < 9)) & (nwin % 2 == 1)
    out += np.where(up & finv, -0.9 * (k2 < 0) + 0.5 * (k2 > 0), 0)
    # la cornisa: el fris d'arquets i les dents de serra
    cor = (y >= Y['cornisa']) & (y < Y['teulada'])
    dent = ((s + 400) % 8 < 4) & (y > Y['cornisa'] + 6)
    out += np.where(cor, 0.7 + dent * 0.8 - (y < Y['cornisa'] + 3) * 1.4 - (~dent & (y > Y['cornisa'] + 6)) * 0.8, 0)
    return out


# ─── El mur de l'hort ───────────────────────────────────────────────────────

def mur(v, e):
    if e.mur == 'cap':
        return
    mullat = -0.5 if e.llum in ('pluja', 'nit', 'llamp') else 0.0
    nou = e.mur == 'arreglat'

    def forat(s):
        trenc = (s > TRENCAT[0]) & (s < TRENCAT[1]) & (e.mur == 'esbotzat')
        return trenc | ((s > PORTELL[0]) & (s < PORTELL[1]))

    def alt(s):
        """L'alçada del mur a cada punt: a les vores del trencat, esmicolat."""
        h = MUR_H + (vnoise(s / 30, 0.5, 101) - 0.5) * 6
        if e.mur == 'esbotzat':
            for a, b in (TRENCAT,):
                dd = np.minimum(np.abs(s - a), np.abs(s - b))
                h = np.where(dd < 60, h - (60 - dd) * 0.9 * vnoise(s / 7, 0.2, 103), h)
        dd = np.minimum(np.abs(s - PORTELL[0]), np.abs(s - PORTELL[1]))
        return np.where(dd < 8, h + 10, h)
    # la cara del carrer
    t = x_pla(v, MUR_A, MUR_N)
    P = v.punt(np.where(np.isinf(t), 0, t))
    s = (P - MUR_A) @ MUR_T
    y = P[..., 1]
    m = np.isfinite(t) & (s > 0) & (s < MUR_L) & (y > 0) & (y < alt(s)) & ~forat(s)
    lvl = _pedres(s, y, 83) + mullat
    if nou:
        tros = (s > TRENCAT[0] - 10) & (s < TRENCAT[1] + 10)
        lvl = np.where(tros, lvl + 0.9, lvl)
    vis = ombra_sol(P, e) if e.llum in ('sol', 'primavera') else None
    lvl = lvl + _llum(e, np.broadcast_to(MUR_N, P.shape), P, vis) - 1.0 * np.exp(-y / 18)
    rgb = v.to(PEDRA, lvl)
    rgb = np.where((nou & (s > TRENCAT[0] - 10) & (s < TRENCAT[1] + 10))[..., None], v.to(OCRE, lvl + 0.4), rgb)
    v.pinta(m, t, rgb, 'mur')
    # el capçal (la part de dalt), vist des de sota no es veu; els cantells del portell i del trencat
    for (s0, dirn) in ((PORTELL[0], 1), (PORTELL[1], -1)) + (((TRENCAT[0], 1), (TRENCAT[1], -1)) if e.mur == 'esbotzat' else ()):
        n = MUR_T * dirn
        P0 = MUR_A + MUR_T * s0
        t = x_pla(v, P0, n)
        P = v.punt(np.where(np.isinf(t), 0, t))
        q = (P - P0) @ -MUR_N
        y = P[..., 1]
        m = np.isfinite(t) & (q > 0) & (q < MUR_G) & (y > 0) & (y < alt(np.full(y.shape, s0 + dirn * 2.0)))
        lvl = _pedres(q + 300, y, 85) - 0.4 + mullat + _llum(e, np.broadcast_to(n, P.shape))
        v.pinta(m, t, v.to(PEDRA, lvl), 'mur')
    if e.mur == 'esbotzat':
        _runa(v, e)


def _pedres(s, y, seed):
    """Pedra seca: filades irregulars de pedres de mides diferents, amb les juntes fosques."""
    row_h = 13.0
    row = np.floor((y + vnoise(s / 40, 0.5, seed) * 4) / row_h)
    ln = 18 + hnp(row, 0 * row, seed) * 14
    off = hnp(row, 1 + 0 * row, seed) * 30
    col = np.floor((s + off) / ln)
    fx = ((s + off) / ln) % 1
    fy = ((y + vnoise(s / 40, 0.5, seed) * 4) / row_h) % 1
    tone = hnp(col, row, seed + 3)
    edge = np.minimum(np.minimum(fx, 1 - fx) * ln, np.minimum(fy, 1 - fy) * row_h)
    lvl = 3.6 + (tone - 0.5) * 1.6 + (fy < 0.35) * 0.4
    return np.where(edge < 1.3, 1.6, lvl - (edge < 2.4) * 0.5)


def _runa(v, e):
    """Les pedres caigudes del mur esbotzat, a banda i banda del trencat."""
    rng = np.random.default_rng(5)
    rocs = []
    for _ in range(46):
        s = rng.uniform(TRENCAT[0] - 60, TRENCAT[1] + 60)
        side = rng.uniform(-50, 70)
        P = MUR_A + MUR_T * s + MUR_N * side
        rocs.append((P, rng.uniform(7, 14)))
    rocs.sort(key=lambda r: -CAM.vista(tuple(r[0]))[2])
    for P, r in rocs:
        roc(v, e, P, r, PEDRA, 'runa', seed=int(r * 100))


def roc(v, e, P, r, ramp, sid, seed=1, lvl0=3.4, aplana=0.7):
    """Una pedra (o una mata): un bony assegut a terra, pintat a la seva profunditat."""
    cam = v.cam
    u, vv, z = cam.projecta(tuple(P))
    k = cam.f / z
    R = r * k
    if R < 0.6:
        return
    x0, x1 = int(u - R - 2), int(u + R + 2)
    y0, y1 = int(vv - R * aplana * 1.6 - 2), int(vv + 1)
    x0, y0, x1, y1 = max(0, x0), max(0, y0), min(v.w - 1, x1), min(v.h - 1, y1)
    if x0 > x1 or y0 > y1:
        return
    X, Y = np.meshgrid(np.arange(x0, x1 + 1), np.arange(y0, y1 + 1))
    dx, dy = (X + 0.5 - u) / R, (Y + 0.5 - vv) / (R * aplana * 1.6)
    ang = np.arctan2(dy, dx)
    vora = 1 + (vnoise(np.cos(ang) * 2 + seed, np.sin(ang) * 2, seed) - 0.5) * 0.5
    d2 = dx * dx + dy * dy
    m = d2 < vora * vora
    nz = np.sqrt(np.clip(1 - d2 / (vora * vora), 0, 1))
    nrm = np.stack([dx, -dy, nz * 0 - 0.6 * nz], -1)
    nrm = nrm / (np.linalg.norm(nrm, axis=-1, keepdims=True) + 1e-9)
    lv = lvl0 + nz * 0.6 + (vnoise(X / 2.5, Y / 2.0, seed + 3) - 0.5) * 1.0 + _llum(e, nrm)
    lv = np.where(dy > -0.15, lv - 0.9, lv)
    sub = (slice(y0, y1 + 1), slice(x0, x1 + 1))
    tz = np.full(m.shape, z - r * 0.3)
    mm = m & (tz < v.z[sub])
    if e.llum in ('pluja', 'nit', 'llamp'):
        lv = lv - 0.5
    b = v.bayer[sub]
    i = np.clip(np.floor(lv + b - 0.5), 0, len(ramp) - 1).astype(int)
    v.col[sub][mm] = ramp[i][mm]
    v.z[sub][mm] = tz[mm]
    v.own[sub][mm] = v.idx(sid)


# ─── L'avet ─────────────────────────────────────────────────────────────────

def _capcada_r(s):
    """El radi de la capçada a la distància s del peu: cònica, ampla a baix i punxeguda a la punta."""
    s = np.asarray(s, dtype=np.float64)
    u = np.clip((s - CAPCADA_S0) / (TRONC_L - CAPCADA_S0), 0, 1)
    return np.where(s < CAPCADA_S0 - 20, 0, 34 + 320 * (1 - u) ** 1.25 * smooth(CAPCADA_S0 - 50, CAPCADA_S0 + 60, s))


def _base_arbre(angle):
    """Els eixos de l'avet: per a l'ajagut, el tronc a terra cap a TRONC_D; per a l'avet dret o que cau, l'eix
    girat `angle` radians des de la vertical cap a TRONC_D, al voltant del peu (el punt on es trenca a terra)."""
    if angle is None:
        return None
    peu = FORAT_C + np.array((0, 0, 0)) + TRONC_D * 30
    ax = _n(np.cos(angle) * np.array((0, 1.0, 0)) + np.sin(angle) * TRONC_D)
    return peu, ax


@functools.lru_cache(maxsize=None)
def _taques_arbre(mode, seed=7):
    """Les taques de l'avet, en coordenades locals: s al llarg del tronc i la posició perpendicular (a, b) en els
    dos eixos que el creuen (a: horitzontal, cap a l'hort; b: amunt). → [(mena, s, a, b, radi, f)], amb f la
    fracció de la branca (0 a tocar del tronc, 1 a la punta)."""
    rng = np.random.default_rng(seed)
    out = []
    for s in np.arange(0, TRONC_L, 3.0):
        out.append(('tronc', s, 0.0, 0.0, float(tronc_r(s)), 0.0))
    # cap a la càmera (en a, b): les branques d'aquest costat són trencades i curtes (es veu el tronc)
    cam_a, cam_b = -0.75, 0.1
    s = CAPCADA_S0
    while s < TRONC_L - 6:
        R = float(_capcada_r(s))
        nb = 8 + int(rng.integers(0, 3))
        ph = rng.uniform(0, 2 * math.pi)
        for j in range(nb):
            phi = ph + 2 * math.pi * j / nb + rng.uniform(-0.3, 0.3)
            ca, cb = math.cos(phi), math.sin(phi)
            lean = rng.uniform(0.05, 0.45)
            L = R * rng.uniform(0.55, 1.05)
            if ca * cam_a + cb * cam_b > 0.45:
                L *= rng.uniform(0.25, 0.5)
            if rng.uniform() < 0.12:
                continue                                   # una branca que falta
            npts = max(2, int(L / 5))
            for i in range(1, npts + 1):
                f = i / npts
                d = f * L
                ss = s + d * lean + rng.uniform(-2, 2)
                a = ca * d
                b = cb * d - (f * f) * L * 0.18             # pengen una mica (el pes)
                r = 6.5 + 4.0 * (1 - f) * min(1.0, R / 110)
                if rng.uniform() < 0.88:
                    out.append(('fulla', ss, a, b, r, f))
                if f < 0.92 and rng.uniform() < 0.8:
                    for sg in (-1, 1):
                        dd = rng.uniform(8, 16) * (1 - f * 0.5)
                        out.append(('fulla', ss + rng.uniform(2, 7), a - cb * dd * sg + ca * 3,
                                    b + ca * dd * sg + cb * 3 - 2, r * 0.62, min(1.0, f + 0.15)))
        s += rng.uniform(24, 32)
    return out


def avet(v, e, sid='avet', angle=None, nomes=None):
    """L'avet: ajagut (e.arbre == 'ajagut') o dret o caient (`angle` des de la vertical). `nomes`: un filtre de les
    taques (s → bool), per pintar-ne només un tros."""
    cam = v.cam
    taques = _taques_arbre('avet')
    if angle is None:
        base = ARREL_C * np.array((1, 1, 1))
        ax = TRONC_D
        e1 = _n(np.cross(ax, (0, 1, 0)))              # horitzontal, perpendicular al tronc
        e2 = np.array((0.0, 1.0, 0.0))
        yfn = tronc_y
        # el tronc ajagut no és recte: segueix tronc_y
    else:
        base, ax = _base_arbre(angle)
        e1 = _n(np.cross(ax, (0, 0, 1.0))) if abs(ax[2]) < 0.99 else np.array((1.0, 0, 0))
        e2 = _n(np.cross(e1, ax))
        yfn = None
    pts, rad, lv0, nrm, kind = [], [], [], [], []
    for (k, s, a, b, r, f) in taques:
        if nomes is not None and not nomes(s):
            continue
        if yfn is not None:
            c = ARREL_C * np.array((1, 0, 1)) + TRONC_D * s
            c = np.array((c[0], float(yfn(s)), c[2]))
            Pw = c + e1 * a + e2 * b
        else:
            c = base + ax * s
            Pw = c + e1 * a + e2 * b
        if Pw[1] < 3:                                   # les branques de sota, aixafades contra terra
            if k == 'tronc':
                continue
            Pw = np.array((Pw[0], 3 + abs(Pw[1]) * 0.12, Pw[2]))
            r *= 0.8
        pts.append(Pw)
        rad.append(r)
        if k == 'tronc':
            nrm.append(np.zeros(3))
            lv0.append(-1.0)
        else:
            dv = Pw - c
            nn = np.linalg.norm(dv)
            nrm.append(dv / nn if nn > 1e-6 else np.array((0, 1.0, 0)))
            lv0.append(f)
        kind.append(k)
    if not pts:
        return
    pts = np.array(pts)
    rad = np.array(rad)
    nrm = np.array(nrm)
    lv0 = np.array(lv0)
    # projecció
    rel = pts - v.O
    xc = rel @ np.array((cam._cy, 0, -cam._sy))
    z1 = rel @ np.array((cam._sy, 0, cam._cy))
    yc = rel[:, 1] * cam._cp + z1 * cam._sp
    zc = -rel[:, 1] * cam._sp + z1 * cam._cp
    ok = zc > 5
    u = cam.centre[0] + cam.f * xc / np.where(ok, zc, 1)
    vv = cam.centre[1] - cam.f * yc / np.where(ok, zc, 1)
    R = rad * cam.f / np.where(ok, zc, 1)
    order = np.argsort(-zc)
    # la llum de cada taca: el costat que mira el cel, més clar; les de dins, més fosques; el sol, amb ombra
    if e.llum in ('sol', 'primavera'):
        vis = ombra_sol(pts + nrm * 10, replace(e, arbre='cap'), passos=24, lluny=2000)
        selfsh = np.clip(nrm @ SOL_DIR * 1.4 + 0.3, 0, 1)
        vis = vis * selfsh
    else:
        vis = None
    Lt = _llum(e, np.where(np.linalg.norm(nrm, axis=1, keepdims=True) > 0, nrm, np.array((0, 1.0, 0))), None, vis)
    idx = v.idx(sid)
    tronc_idx = v.idx(sid + '_tronc')
    for i in order:
        if not ok[i] or R[i] < 0.4:
            continue
        ui, vi, Ri = u[i], vv[i], max(0.7, R[i])
        fulla = kind[i] == 'fulla'
        ry = Ri * (0.62 if fulla else 1.0)
        x0, x1 = int(ui - Ri - 1), int(ui + Ri + 1)
        y0, y1 = int(vi - ry - 1), int(vi + ry + 1)
        x0, y0, x1, y1 = max(0, x0), max(0, y0), min(v.w - 1, x1), min(v.h - 1, y1)
        if x0 > x1 or y0 > y1:
            continue
        sub = (slice(y0, y1 + 1), slice(x0, x1 + 1))
        X, Y = v.X[sub], v.Y[sub]
        dx, dy = (X + 0.5 - ui) / Ri, (Y + 0.5 - vi) / ry
        d2 = dx * dx + dy * dy
        if fulla:
            # una fronda: vora estripada, la part de dalt més clara (les agulles noves), la de sota fosca
            nz = hnp(X, Y, 9 + i % 5)
            m = d2 < 0.75 + 0.5 * nz
            lv = 2.0 + lv0[i] * 2.3 + Lt[i] - dy * 1.2 + (nz - 0.5) * 1.4
            ramp = AVET
        else:
            m = d2 < 1.0
            # escorça: llum de dalt, solcs al llarg
            lv = 2.8 - dy * 1.4 + (hnp(X, Y // 2, 11) - 0.5) * 0.9 + (Lt[i] if np.ndim(Lt) else 0) * 0.6
            ramp = ESCORÇA
        tz = zc[i] - Ri * 0.0
        mm = m & (tz < v.z[sub])
        if not mm.any():
            continue
        b = v.bayer[sub]
        ii = np.clip(np.floor(lv + b - 0.5), 0, len(ramp) - 1).astype(int)
        v.col[sub][mm] = ramp[ii][mm]
        v.z[sub][mm] = tz
        v.own[sub][mm] = idx if fulla else tronc_idx


def arrels(v, e, sid='arrels'):
    """El pla de les arrels, aixecat: una paret de terra amb arrels arrencades, pedres, i a baix a l'esquerra dues
    arrels gruixudes tallades de serra (la cara plana i clara)."""
    n = ARREL_N
    up = np.array((0, 1.0, 0))
    ex = _n(np.cross(up, n))                       # cap a la dreta, al pla
    def _vora(ang):
        return ARREL_R * (0.80 + 0.36 * vnoise(np.cos(ang) * 3.2 + 3, np.sin(ang) * 3.2, 111)
                          + 0.14 * vnoise(np.cos(ang) * 14, np.sin(ang) * 14, 112))
    # el gruix del pla (la terra que s'ha aixecat fa un metre): un disc una mica més enrere, més fosc
    t = x_pla(v, ARREL_C - n * 34, n)
    P = v.punt(np.where(np.isinf(t), 0, t))
    q = P - (ARREL_C - n * 34)
    a, b = q @ ex, q @ up
    ang = np.arctan2(b, a)
    m = np.isfinite(t) & (np.hypot(a, b) < _vora(ang) * 0.96) & (P[..., 1] > -2)
    lg = 1.6 + (fbm(a / 7, b / 5, 109) - 0.5) * 1.6 + (b / ARREL_R) * 0.8 + _llum(e, np.broadcast_to(-ex, P.shape)) * 0.6
    v.pinta(m, t, v.to(TERRA, lg), sid)
    t = x_pla(v, ARREL_C, n)
    P = v.punt(np.where(np.isinf(t), 0, t))
    q = P - ARREL_C
    a, b = q @ ex, q @ up
    ang = np.arctan2(b, a)
    rr = np.hypot(a, b)
    vora = _vora(ang)
    m = np.isfinite(t) & (rr < vora) & (P[..., 1] > -2)
    vell = e.forat == 'vell'
    # la terra: grumolls (clars a dalt, ombra a sota), algunes pedres, i les arrels que la travessen
    gr = fbm(a / 9, b / 7, 113, 3)
    gr2 = fbm(a / 4, b / 3.5, 114, 2)
    lvl = 3.2 + (gr - 0.5) * 2.4 + (gr2 - 0.5) * 1.4 - (rr / ARREL_R) ** 2 * 0.8 + (b / ARREL_R) * 0.5
    lvl = lvl + np.clip(fbm(a / 9, (b + 3) / 7, 113, 3) - gr, -0.2, 0.2) * -6     # el relleu dels grumolls
    vena = np.abs(vnoise(a / 26 + np.cos(ang) * 2, b / 26 + np.sin(ang) * 2, 115) - 0.5) < 0.035
    vena2 = np.abs(vnoise(a / 11, b / 11, 116) - 0.5) < 0.03
    lvl = np.where((vena | vena2) & (rr > 16), lvl - 1.5, lvl)
    lvl = np.where(vena & (rr > 16) & (np.abs(vnoise(a / 26 + np.cos(ang) * 2, (b + 2) / 26 + np.sin(ang) * 2, 115) - 0.5) < 0.035), lvl + 0.4, lvl)
    pd = (vnoise(a / 6, b / 6, 117) > 0.8) & (gr2 > 0.5)
    lvl = lvl + _llum(e, np.broadcast_to(n, P.shape))
    if e.llum in ('pluja', 'nit', 'llamp'):
        lvl = lvl - 0.3
        lvl = lvl + (hnp(v.X, v.Y, 118) > 0.985) * 2.2 * (b > -40)       # la terra mullada, que brilla
    lvl = lvl - smooth(0.8, 1.0, rr / vora) * 0.9                          # la vora, ombrejada
    rgb = np.where(pd[..., None], v.to(PEDRA, lvl + 0.9), v.to(TERRA, lvl))
    # la vora de dalt: l'herba que hi havia a la superfície, ara de costat
    herba = rr > vora - 6
    rgb = np.where((herba & (b > -10))[..., None], v.to(HERBA, lvl + 0.6), rgb)
    if vell:
        mol = fbm(a / 10, b / 10, 119) > 0.5
        rgb = np.where(mol[..., None], v.to(MOLSA, lvl + 0.4), rgb)
    v.pinta(m, t, rgb, sid)
    # la vora: les arrels gruixudes que surten del disc, arrencades, i s'obren enfora (més enllà de la silueta: és
    # el que fa que es llegeixi com una soca arrencada i no com una roca); cada una, amb dos o tres trams i
    # arreletes que se'n separen
    rng = np.random.default_rng(13)
    arrs = []
    for j in range(34):
        th = 2 * math.pi * j / 34 + rng.uniform(-0.1, 0.1)
        if math.sin(th) < -0.5:
            continue                                   # (les de sota són sota terra)
        r0 = ARREL_R * rng.uniform(0.5, 0.8)
        L = rng.uniform(46, 96) if math.sin(th) < 0.5 else rng.uniform(30, 64)
        rd = ex * math.cos(th) + up * math.sin(th)
        p0 = ARREL_C + rd * r0 + n * 4
        mid = p0 + rd * L * 0.55 + n * rng.uniform(6, 20)
        cau = up * rng.uniform(6, 26) if math.sin(th) < 0.3 else up * rng.uniform(-6, 10)
        p1 = mid + rd * L * 0.45 - cau + n * rng.uniform(0, 10)
        g = rng.uniform(3.0, 6.0)
        arrs.append((p0, mid, g))
        arrs.append((mid, p1, g * 0.55))
        for _ in range(int(rng.integers(1, 3))):     # les arreletes
            f = rng.uniform(0.3, 0.9)
            q0 = p0 + (mid - p0) * f
            dq = _n(rd + ex * rng.uniform(-0.8, 0.8) + up * rng.uniform(-0.6, 0.6))
            arrs.append((q0, q0 + dq * rng.uniform(12, 28) + n * rng.uniform(0, 8), g * 0.35))
    arrs.sort(key=lambda q: -v.cam.vista(tuple(q[1]))[2])
    for p0, p1, g in arrs:
        _arrel(v, e, p0, p1, g, sid, ramp=ARREL)
    # les arreletes que pengen de la vora de baix, fins al forat
    for j in range(12):
        th = -math.pi / 2 + (j - 5.5) * 0.17 + rng.uniform(-0.05, 0.05)
        rd = ex * math.cos(th) + up * math.sin(th)
        p0 = ARREL_C + rd * ARREL_R * 0.7 + n * 6
        p1 = p0 + n * rng.uniform(6, 20) - up * rng.uniform(4, 16) + ex * rng.uniform(-6, 6)
        if p1[1] > 1:
            _arrel(v, e, p0, p1, rng.uniform(1.4, 2.6), sid, ramp=ARREL)
    # les dues arrels tallades de serra (a baix a l'esquerra): el tall, una el·lipse clara amb els anells
    for (aa, bb, rad, sortida) in ((-50.0, -44.0, 14.0, 30.0), (-10.0, -66.0, 10.0, 22.0), (-78.0, -12.0, 7.0, 16.0)):
        c0 = ARREL_C + ex * aa + up * bb
        c1 = c0 + n * sortida + up * 2
        _arrel(v, e, c0, c1, rad, sid, cap=False)
        _tall(v, e, c1, n, rad, sid + '_tall')


def _arrel(v, e, p0, p1, g, sid, cap=True, ramp=ESCORÇA):
    """Una arrel: un tub que es va aprimant de p0 a p1 (gruix g), amb l'escorça fosca."""
    cam = v.cam
    n = 24
    for k in range(n, -1, -1):
        f = k / n
        P = p0 + (p1 - p0) * f
        u, vv, z = cam.projecta(tuple(P))
        r = (g * (1 - f * 0.6 if cap else 1)) * cam.f / z
        x0, x1, y0, y1 = int(u - r - 1), int(u + r + 1), int(vv - r - 1), int(vv + r + 1)
        x0, y0, x1, y1 = max(0, x0), max(0, y0), min(v.w - 1, x1), min(v.h - 1, y1)
        if x0 > x1 or y0 > y1:
            continue
        sub = (slice(y0, y1 + 1), slice(x0, x1 + 1))
        dx, dy = (v.X[sub] + 0.5 - u) / max(r, 0.6), (v.Y[sub] + 0.5 - vv) / max(r, 0.6)
        m = (dx * dx + dy * dy < 1) & (z < v.z[sub])
        lv = 2.6 - dy * 1.3 - dx * 0.3 + _llum(e, np.array((0, 1.0, 0))) * 0.5
        lv = lv + (hnp(v.X[sub], v.Y[sub], 21) - 0.5) * 0.6
        ii = np.clip(np.floor(lv + v.bayer[sub] - 0.5), 0, len(ramp) - 1).astype(int)
        v.col[sub][m] = ramp[ii][m]
        v.z[sub][m] = z
        v.own[sub][m] = v.idx(sid)


def _tall(v, e, c, n, rad, sid):
    """El tall net de la serra: un disc de fusta clara, pla, amb els anells i la vora d'escorça."""
    up = np.array((0, 1.0, 0))
    ex = _n(np.cross(up, n))
    t = x_pla(v, c, n)
    P = v.punt(np.where(np.isinf(t), 0, t))
    q = P - c
    a, b = q @ ex, q @ up
    rr = np.hypot(a, b)
    m = np.isfinite(t) & (rr < rad)
    anell = (rr * 0.9 + vnoise(a / 4, b / 4, 131) * 1.4) % 2.6 < 0.7
    lvl = 2.8 + (anell * -1.0) + (rr > rad - 2.2) * -2.6 + _llum(e, np.broadcast_to(n, P.shape)) * (1.0 if e.llum == 'nit' else 0.5) + 0.4
    rgb = np.where((rr > rad - 2.2)[..., None], v.to(ESCORÇA, lvl + 2.4), v.to(TALL, lvl))
    v.pinta(m & (t < v.z + 6), np.minimum(t, v.z), rgb, sid, prof=False)


# ─── Les branques del carrer ────────────────────────────────────────────────

def branca(v, e, P0, P1, mida, sid, seed=1, lv=0.0):
    """Una branca d'avet tirada a terra (o penjant): la tija i les frondes a banda i banda, de lluny a prop."""
    cam = v.cam
    rng = np.random.default_rng(seed)
    d = P1 - P0
    L = float(np.linalg.norm(d))
    dirn = d / L
    side = _n(np.cross(dirn, (0, 1, 0))) if abs(dirn[1]) < 0.95 else np.array((1.0, 0, 0))
    taques = []
    for i in range(int(L / 4) + 1):
        f = i / max(1, int(L / 4))
        c = P0 + d * f
        taques.append((c + np.array((0, 5.0, 0)), 2.6 * (1 - f * 0.5), 'tija', f))
        if f > 0.12 and i % 2 == 0:
            w = mida * (1 - f * 0.65)
            for sg in (-1, 1):
                for k in range(1, 4):
                    alt_ = (4 - k) * 4.5 + rng.uniform(0, 7) + 2
                    p = c + side * sg * w * k / 3 + dirn * w * k / 3 * 0.4 + np.array((0, alt_, 0))
                    taques.append((p, 6.5 * (1 - k * 0.12), 'fulla', f))
                    if k == 1 and rng.uniform() < 0.6:          # una fronda que s'aixeca (la branca no és plana)
                        taques.append((c + np.array((0, 16 + rng.uniform(0, 10), 0)) + dirn * 4, 6.0, 'fulla', f))
    taques.sort(key=lambda tq: (tq[2] == 'tija', -cam.vista(tuple(tq[0]))[2]))
    idx = v.idx(sid)
    for c, r, k, f in taques:
        u, vv, z = cam.projecta(tuple(c))
        R = max(0.6, r * cam.f / z)
        ry = R * (0.6 if k == 'fulla' else 1.0)
        x0, x1, y0, y1 = int(u - R - 1), int(u + R + 1), int(vv - ry - 1), int(vv + ry + 1)
        x0, y0, x1, y1 = max(0, x0), max(0, y0), min(v.w - 1, x1), min(v.h - 1, y1)
        if x0 > x1 or y0 > y1:
            continue
        sub = (slice(y0, y1 + 1), slice(x0, x1 + 1))
        X, Y = v.X[sub], v.Y[sub]
        dx, dy = (X + 0.5 - u) / R, (Y + 0.5 - vv) / ry
        nz = hnp(X, Y, 31 + seed % 7)
        if k == 'fulla':
            m = dx * dx + dy * dy < 0.7 + 0.5 * nz
            lvv = 3.2 + lv - dy * 1.0 + (nz - 0.5) * 1.3 + _llum(e, np.array((0, 1.0, 0))) - f * 0.4
            ramp = AVET
        else:
            m = dx * dx + dy * dy < 1
            lvv = 3.4 + lv - dy * 1.2 + _llum(e, np.array((0, 1.0, 0))) * 0.5
            ramp = ESCORÇA
            z = z - 8                                   # (la tija, damunt de les frondes)
        mm = m & (z < v.z[sub])
        ii = np.clip(np.floor(lvv + v.bayer[sub] - 0.5), 0, len(ramp) - 1).astype(int)
        v.col[sub][mm] = ramp[ii][mm]
        v.z[sub][mm] = z
        v.own[sub][mm] = idx


# Les branques que tapen el pas cap a les arrels (estat 'pas'), i on van quan s'aparten
BRANQUES_PAS = [((-470, 590), (-300, 545), 34), ((-170, 610), (-330, 560), 30), ((-420, 680), (-250, 600), 38),
                ((-240, 700), (-200, 575), 28), ((-520, 640), (-400, 560), 26), ((-120, 660), (-260, 590), 26),
                ((-360, 640), (-330, 540), 22)]
BRANQUES_APARTADES = [((-640, 600), (-520, 570), 30), ((-660, 660), (-540, 600), 34), ((-610, 560), (-500, 548), 24),
                      ((-60, 690), (-120, 600), 30), ((-10, 700), (-90, 640), 28), ((-120, 720), (-150, 640), 26)]
# Branques escampades que sempre hi són (pel carrer, cap al fons i el portell)
BRANQUES_FONS = [((-700, 880), (-560, 800), 30), ((-500, 860), (-420, 760), 26), ((-90, 900), (-20, 820), 30),
                 ((60, 960), (150, 880), 28), ((-780, 760), (-660, 720), 24)]
# La branca esqueixada que regalima resina: penja del tronc fins a terra
BRANCA_TRENCADA = (np.array((-150.0, 112.0, 742.0)), np.array((-92.0, 3.0, 650.0)))


def branques(v, e):
    for (a, b, w) in BRANQUES_FONS:
        branca(v, e, np.array((a[0], 3.0, a[1])), np.array((b[0], 5.0, b[1])), w, 'branques_fons', seed=int(a[0]) & 255, lv=-0.3)
    if e.branques == 'pas':
        llista, sid = BRANQUES_PAS, 'branques'
    elif e.branques == 'apartades':
        llista, sid = BRANQUES_APARTADES, 'branques'
    else:
        return
    for k, (a, b, w) in enumerate(sorted(llista, key=lambda q: -(q[0][1] + q[1][1]))):
        branca(v, e, np.array((a[0], 4.0 + k % 3 * 3, a[1])), np.array((b[0], 8.0 + k % 2 * 6, b[1])), w, sid,
               seed=100 + k)


def branca_trencada(v, e):
    """La branca esqueixada: penja del tronc, amb l'estella clara on s'ha trencat i les gotes de resina (ambre)."""
    P0, P1 = BRANCA_TRENCADA
    _barra(v, e, P0, P1, 3.2, ESCORÇA, 3.8, 'branca_trencada')
    branca(v, e, P0 + (P1 - P0) * 0.15, P1, 34, 'branca_trencada', seed=77, lv=0.6)
    cam = v.cam
    # l'esqueix: fusta clara a la base, i la resina que regalima
    for k, (dx, dy, dz, r, ramp, l0) in enumerate(((0, 0, 0, 7, TALL, 4.2), (2, -9, -2, 3, RESINA, 3.2),
                                                   (-1, -17, -3, 2.6, RESINA, 3.6), (3, -24, -2, 2.2, RESINA, 4.0),
                                                   (0, -32, -4, 1.8, RESINA, 3.4))):
        P = P0 + np.array((dx, dy, dz))
        u, vv, z = cam.projecta(tuple(P))
        R = max(0.8, r * cam.f / z)
        x0, x1, y0, y1 = int(u - R - 1), int(u + R + 1), int(vv - R * 1.3 - 1), int(vv + R * 1.3 + 1)
        sub = (slice(max(0, y0), y1 + 1), slice(max(0, x0), x1 + 1))
        X, Y = v.X[sub], v.Y[sub]
        dxx, dyy = (X + 0.5 - u) / R, (Y + 0.5 - vv) / (R * 1.3)
        m = dxx * dxx + dyy * dyy < 1
        lv = l0 - dyy * 0.8 - dxx * 0.4
        lv = np.where((dxx < -0.2) & (dyy < -0.2), lv + 1.2, lv)
        ii = np.clip(np.floor(lv + v.bayer[sub] - 0.5), 0, len(ramp) - 1).astype(int)
        v.col[sub][m] = ramp[ii][m]
        v.z[sub][m] = z - 4
        v.own[sub][m] = v.idx('branca_trencada')


# ─── El faristol, l'ordre, la cera ──────────────────────────────────────────

def _caixa(v, e, c, hx, hy, hz, ramp, lvl, sid, rot=0.0):
    """Una caixa (per al faristol): les tres cares que es veuen, cadascuna amb la seva llum."""
    cr, sr = math.cos(rot), math.sin(rot)
    ux, uz = np.array((cr, 0, sr)), np.array((-sr, 0, cr))
    uy = np.array((0, 1.0, 0))
    for n, half, e1, e2, h1, h2 in ((-uz, hz, ux, uy, hx, hy), (-ux, hx, uz, uy, hz, hy), (ux, hx, uz, uy, hz, hy),
                                     (uy, hy, ux, uz, hx, hz)):
        P0 = c + n * half
        t = x_pla(v, P0, n)
        P = v.punt(np.where(np.isinf(t), 0, t))
        q = P - P0
        m = np.isfinite(t) & (np.abs(q @ e1) < h1) & (np.abs(q @ e2) < h2)
        if not m.any():
            continue
        q1, q2 = q @ e1, q @ e2
        lv = lvl + _llum(e, np.broadcast_to(n, P.shape)) + (fbm(q1 / 6, q2 / 5, 41, 2) - 0.5) * 1.4
        lv = lv + (np.abs(q2) > h2 - 2.5) * 0.9 - (np.abs(q1) > h1 - 2) * 0.6 - (q2 < -h2 + 3) * 0.8
        v.pinta(m, t, v.to(ramp, lv), sid)


def faristol(v, e, sid='faristol'):
    """El faristol de viatge del jutge: un peu de tres potes, la columna i el tauler inclinat."""
    c = FARISTOL
    # les tres potes
    for k in range(3):
        a = math.pi / 2 + 2 * math.pi * k / 3 + 0.3
        p0 = c + np.array((math.cos(a) * 20, 0, math.sin(a) * 20))
        p1 = c + np.array((0, 26, 0))
        _barra(v, e, p0, p1, 2.2, FUSTA, 3.0, sid)
    _barra(v, e, c + np.array((0, 22, 0)), c + np.array((0, 58, 0)), 3.0, FUSTA, 3.2, sid)
    # el tauler: inclinat cap a la càmera (el costat de dalt més lluny)
    tilt = math.radians(32)
    n = _n((0.25, math.cos(tilt), -math.sin(tilt)))
    ctr = c + np.array((0, 64, 0))
    ex = _n(np.cross((0, 1.0, 0), n))
    ey = _n(np.cross(n, ex))
    for (cara, off, lvl, ramp) in (('dalt', 0.0, 4.2, FUSTA),):
        t = x_pla(v, ctr, n)
        P = v.punt(np.where(np.isinf(t), 0, t))
        q = P - ctr
        a, b = q @ ex, q @ ey
        m = np.isfinite(t) & (np.abs(a) < 24) & (np.abs(b) < 15)
        vora = (np.abs(a) > 21.5) | (np.abs(b) > 12.5)
        lv = lvl + _llum(e, np.broadcast_to(n, P.shape)) + vora * 0.8 + (hnp(v.X // 2, v.Y, 43) - 0.5) * 0.6
        v.pinta(m, t, v.to(ramp, lv), sid)
    # el cantell de davant del tauler (el llistó on s'aguanta el pergamí)
    _barra(v, e, ctr - ex * 24 - ey * 15, ctr + ex * 24 - ey * 15, 2.0, FUSTA, 2.6, sid)
    v.faristol_pla = (ctr, n, ex, ey)


def ordre(v, e, sid='ordre'):
    """L'ordre del jutge damunt el faristol: un pergamí amb el text en ratlles, el segell vermell i el signe."""
    if not hasattr(v, 'faristol_pla'):
        return
    ctr, n, ex, ey = v.faristol_pla
    c = ctr + n * 0.8
    t = x_pla(v, c, n)
    P = v.punt(np.where(np.isinf(t), 0, t))
    q = P - c
    a, b = q @ ex, q @ ey
    m = np.isfinite(t) & (np.abs(a + 1) < 15) & (b > -13) & (b < 12)
    ratlla = ((b % 3.2) < 1.0) & (np.abs(a + 1) < 12) & (b > -6) & (b < 9)
    lv = 4.4 + _llum(e, np.broadcast_to(n, P.shape)) * 0.7 - ratlla * 1.6 + (hnp(v.X, v.Y, 45) - 0.5) * 0.4
    rgb = v.to(PERGAMI, lv)
    segell = np.hypot(a - 7, b + 9) < 4.5
    rgb = np.where(segell[..., None], v.to(CERA, 3.4 + (np.hypot(a - 6, b + 8) < 2) * 1.2), rgb)
    v.pinta(m & (t <= v.z + 2), np.minimum(t, v.z), rgb, sid, prof=False)


def _barra(v, e, p0, p1, g, ramp, lvl, sid):
    cam = v.cam
    n = max(2, int(np.linalg.norm(p1 - p0) / 1.5))
    for k in range(n, -1, -1):
        P = p0 + (p1 - p0) * k / n
        u, vv, z = cam.projecta(tuple(P))
        r = max(0.55, g * cam.f / z)
        x0, x1, y0, y1 = int(u - r), int(u + r), int(vv - r), int(vv + r)
        sub = (slice(max(0, y0), max(0, y1) + 1), slice(max(0, x0), max(0, x1) + 1))
        X, Y = v.X[sub], v.Y[sub]
        dx = (X + 0.5 - u) / r
        dy = (Y + 0.5 - vv) / r
        m = (dx * dx + dy * dy <= 1.2) & (z < v.z[sub])
        lv = lvl - dx * 0.9 + _llum(e, np.array((0, 1.0, 0))) * 0.4
        ii = np.clip(np.floor(lv + v.bayer[sub] - 0.5), 0, len(ramp) - 1).astype(int)
        v.col[sub][m] = ramp[ii][m]
        v.z[sub][m] = z
        v.own[sub][m] = v.idx(sid)


# El tros de segell: una gota de cera aixafada de 7×4 píxels, amb la vora de baix fosca (l'ombra al fang) i una
# lluentor a dalt, perquè es llegeixi com una cosa i no com un punt de soroll. Els dígits són l'índex de la rampa.
_CERA_DIBUIX = ("  455  ",
                " 34543 ",
                "2344432",
                " 01110 ")
# On era: el fang remenat i la marca dels dits, de la mateixa mida.
_CERA_AGAFADA = (" 2 3 2 ",
                 "1032301",
                 " 01210 ")


def _taca(v, cam, dibuix, ramp, z, sid):
    """Pinta un dibuix petit (`dibuix`, files de dígits) centrat al punt de la cera."""
    u, vv, zc = cam.projecta(tuple(CERA_P))
    h, w = len(dibuix), len(dibuix[0])
    for fy, fila in enumerate(dibuix):
        for fx, c in enumerate(fila):
            if c == ' ':
                continue
            X, Y = int(u) + fx - w // 2, int(vv) + fy - (h - 2)
            if 0 <= X < v.w and 0 <= Y < v.h:
                v.col[Y, X] = ramp[int(c)]
                if z:
                    v.z[Y, X] = zc - 2
                v.own[Y, X] = v.idx(sid)


def cera(v, e, sid='cera'):
    """El tros de cera vermella al fang del fons del forat: petit, però que l'ull el trobi."""
    _taca(v, v.cam, _CERA_DIBUIX, CERA, True, sid)


def cera_agafada(v, e, sid='cera_agafada'):
    """On era la cera: el fang remenat (la marca dels dits)."""
    _taca(v, v.cam, _CERA_AGAFADA, FANG, False, sid)


# ─── L'abeurador i el primer pla ────────────────────────────────────────────

ABEURADOR = (np.array((262.0, 0.0, 566.0)), 40.0, 16.0, 17.0, 0.42)   # centre, mig llarg, mig ample, mig alt, gir


def abeurador(v, e, sid='abeurador'):
    """L'abeurador de pedra, girat, a la dreta del carrer: les tres cares, l'aigua a dins (plena de pluja)."""
    c, hx, hz, hy, rot = ABEURADOR
    ramp = PEDRA
    _caixa(v, e, c + np.array((0, hy, 0)), hx, hy, hz, ramp, 2.7 - (0.4 if e.llum in ('pluja', 'nit', 'llamp') else 0), sid, rot)
    # l'aigua: un rectangle a dins de la cara de dalt
    cr, sr = math.cos(rot), math.sin(rot)
    ux, uz = np.array((cr, 0, sr)), np.array((-sr, 0, cr))
    P0 = c + np.array((0, 2 * hy - 3, 0))
    t = x_pla(v, P0, np.array((0, 1.0, 0)))
    P = v.punt(np.where(np.isinf(t), 0, t))
    q = P - P0
    m = np.isfinite(t) & (np.abs(q @ ux) < hx - 4) & (np.abs(q @ uz) < hz - 4)
    rgb = v.to(_r((14, 16, 18), (26, 30, 34), (44, 50, 56), (120, 128, 134), (196, 200, 204)), np.full(t.shape, 1.2) + (hnp(v.X // 3, v.Y, 51) > 0.88) * 2.2)
    if e.llum in ('sol', 'primavera'):
        rgb = v.to(_r((20, 40, 70), (40, 80, 120), (110, 160, 200), (220, 236, 246)), np.full(t.shape, 1.4) + (hnp(v.X // 4, v.Y, 53) > 0.8) * 2)
    v.pinta(m & (t < v.z + 3), t - 3, rgb, sid, prof=False)


PRIMER_PLA = [((-330.0, 0.0, 396.0), (-176.0, 20.0, 384.0), 64.0), ((-300.0, 0.0, 420.0), (-226.0, 8.0, 396.0), 40.0)]


def primer_pla(v, e, sid='primer_pla'):
    """Una branca grossa que el vent ha llançat fins aquí, a baix a l'esquerra, tallada per la vora: en silueta."""
    for k, (a, b, w) in enumerate(PRIMER_PLA):
        branca(v, e, np.array(a), np.array(b), w, sid, seed=300 + k, lv=-1.6)
    roc(v, e, np.array((-262.0, 0.0, 392.0)), 22, PEDRA, sid, seed=7, lvl0=2.2)


# ─── El cofre ───────────────────────────────────────────────────────────────

def _cofre_lloc():
    up = np.array((0, 1.0, 0))
    ex = _n(np.cross(up, ARREL_N))
    c = ARREL_C + ex * 34 - up * 64 + ARREL_N * 14
    return c, math.atan2(ARREL_N[0], -ARREL_N[2])


COFRE, COFRE_ROT = _cofre_lloc()


def segell_xy(cam=CAM):
    """On és el segell del cofre a la pantalla (u, v)."""
    cr, sr = math.cos(COFRE_ROT), math.sin(COFRE_ROT)
    front = np.array((sr, 0, -cr))
    u, vv, _ = cam.projecta(tuple(COFRE + np.array((0, 9, 0)) + front * 9.5))
    return u, vv


def cofre(v, e, sid='cofre'):
    """El cofre que les arrels han tret de terra: fusta fosca amb cèrcols de ferro, i el segell de cera vermella
    al davant (l'únic vermell viu: no el toca la foscor de la nit)."""
    cr, sr = math.cos(COFRE_ROT), math.sin(COFRE_ROT)
    ux, uz = np.array((cr, 0, sr)), np.array((-sr, 0, cr))
    _caixa(v, e, COFRE + np.array((0, 8, 0)), 14, 8, 9, FUSTA, 3.0, sid, COFRE_ROT)
    # la tapa, bombada (una caixa més petita a sobre)
    _caixa(v, e, COFRE + np.array((0, 18, 0)), 14.5, 2.5, 9.5, FUSTA, 3.6, sid, COFRE_ROT)
    # els cèrcols de ferro
    for dx in (-9, 9):
        P0 = COFRE + ux * dx - uz * 9.6
        _barra(v, e, P0, P0 + np.array((0, 20, 0)), 1.0, IRON8, 2.2, sid)
    u, vv = segell_xy(v.cam)
    k = v.cam.f / v.cam.vista(tuple(COFRE))[2]
    r = max(1.6, 4.2 * k)
    X, Y = v.X, v.Y
    d = np.hypot(X + 0.5 - u, (Y + 0.5 - vv) * 1.1)
    m = (d < r) & (v.own == v.idx(sid))
    lv = 3.4 - (Y + 0.5 - vv) / r * 0.9 + (d < r * 0.45) * 0.8
    rgb = v.to(CERA, lv)
    v.col[m] = rgb[m]
    v.emissiu |= m


IRON8 = _r((14, 14, 20), (26, 26, 34), (40, 40, 50), (58, 58, 68), (82, 80, 90), (110, 108, 116))


def brillantor(img_base, u, vv, k, col=(255, 40, 30), r=26.0, h=360):
    """Una lluïssor (additiva) al voltant d'un punt de la pantalla, d'intensitat k: → capa RGBA."""
    X, Y = np.meshgrid(np.arange(W), np.arange(H))
    d = np.hypot(X + 0.5 - u, (Y + 0.5 - vv) * 1.15)
    a = np.clip(1 - d / r, 0, 1) ** 2 * k
    base = np.asarray(img_base.convert('RGBA')).astype(np.float64)
    out = base.copy()
    out[..., :3] = np.clip(base[..., :3] + a[..., None] * np.array(col, float), 0, 255)
    out[Y >= h] = base[Y >= h]
    return Image.fromarray(out.astype(np.uint8), 'RGBA')


# ─── L'epíleg: la primavera ─────────────────────────────────────────────────

FORAT_NOU = np.array((-150.0, 0.0, 646.0))
CARRETILLA = (np.array((-36.0, 0.0, 612.0)), -0.35)
RODANXES = np.array((170.0, 0.0, 900.0))
ROTUL = np.array((-112.0, 0.0, 630.0))
FLORIT = np.array((-110.0, 0.0, 1420.0))          # l'arbre florit de l'hort, on hi havia l'avet
PLANCO = FORAT_NOU + np.array((0, 0, 0.0))


def soca(v, e):
    """El que queda del tronc enganxat a les arrels: un tros de soca tallat (la cara del tall mira enrere)."""
    for s_ in np.arange(70, -1, -3.0):
        c = ARREL_C + TRONC_D * s_ * np.array((1, 0, 1))
        _arrel(v, e, c, c + TRONC_D * 3, float(tronc_r(s_)), 'soca', cap=False)


SOCA_C = np.array((-296.0, 0.0, 640.0))          # l'epíleg: on ha tornat a caure el pla de les arrels
SOCA_R = 30.0


def soca_vella(v, e, sid='arrels'):
    """L'epíleg: tallat el tronc, el pla de les arrels ha tornat a caure al forat. Hi queda la soca, serrada de
    biaix, amb les arrels gruixudes que s'estenen per terra i s'hi enfonsen, i molsa a les parts on no toca el sol."""
    rng = np.random.default_rng(29)
    c = SOCA_C
    # les arrels: de la soca cap enfora, arran de terra, i que es colguen
    arrs = []
    for j in range(9):
        th = 2 * math.pi * j / 9 + rng.uniform(-0.25, 0.25)
        d = np.array((math.cos(th), 0.0, math.sin(th)))
        L = rng.uniform(46, 84)
        g = rng.uniform(8, 12)
        p0 = c + d * SOCA_R * 0.6 + np.array((0, 16.0, 0))
        p1 = c + d * (SOCA_R + L * 0.45) + np.array((0, 6.0, 0)) + np.cross(d, (0, 1, 0)) * rng.uniform(-8, 8)
        p2 = c + d * (SOCA_R + L) + np.array((0, -3.0, 0)) + np.cross(d, (0, 1, 0)) * rng.uniform(-14, 14)
        arrs += [(p0, p1, g, True), (p1, p2, g * 0.55, True)]
    arrs.sort(key=lambda q: -v.cam.vista(tuple(q[1]))[2])
    for p0, p1, g, cap in arrs:
        _arrel(v, e, p0, p1, g, sid, cap=cap)
    # la soca: un tub vertical, ample a baix, i el tall de serra de biaix (mira la càmera i el sol)
    alt = 40.0
    n_tall = _n((0.2, 1.0, -0.28))
    top = c + np.array((0, alt, 0))
    t = x_cilindre(v, (c[0], c[2]), SOCA_R)
    P = v.punt(np.where(np.isinf(t), 0, t))
    sota = (P - top) @ n_tall < 0                                  # per sota del tall de serra
    m = np.isfinite(t) & (P[..., 1] > -2) & sota
    q = P - c
    nrm = q * np.array((1, 0, 1.0)) / SOCA_R
    ang = np.arctan2(q[..., 2], q[..., 0])
    solc = np.abs(np.sin(ang * 7 + vnoise(ang * 3, P[..., 1] / 30, 149) * 3)) < 0.28     # les esquerdes de l'escorça
    lv = 2.4 + _llum(e, nrm) * 0.6 - solc * 1.2 + (fbm(ang * 6, P[..., 1] / 9, 147) - 0.5) * 1.2
    lv = lv - smooth(14, 0, P[..., 1]) * 0.8                       # el peu, fosc
    v.pinta(m, t, v.to(ESCORÇA, lv), sid)
    # el tall de dalt: la fusta de l'hivern, una mica enfosquida i esquerdada, amb els anells i l'escorça
    t = x_pla(v, top, n_tall)
    P = v.punt(np.where(np.isinf(t), 0, t))
    q = P - c
    rr = np.hypot(q[..., 0], q[..., 2])
    m = np.isfinite(t) & (rr < SOCA_R)
    anell = (rr * 0.8 + vnoise(q[..., 0] / 5, q[..., 2] / 5, 159) * 1.6) % 3.2 < 0.8
    esquerda = np.abs(vnoise(np.arctan2(q[..., 2], q[..., 0]) * 2, 0.5, 161) - 0.5) < 0.03
    lv = 3.0 - anell * 0.7 - esquerda * (rr > 6) * 1.6 + _llum(e, n_tall) * 0.4 + (fbm(q[..., 0] / 6, q[..., 2] / 6, 163) - 0.5) * 0.8
    vora = rr > SOCA_R - 3
    rgb = np.where(vora[..., None], v.to(ESCORÇA, lv + 0.6), v.to(TALL, lv))
    gris = rgb.mean(-1, keepdims=True)
    rgb = np.where(vora[..., None], rgb, rgb * 0.8 + gris * 0.2)
    v.pinta(m, t, rgb, sid + '_tall')
    # la molsa i l'herba que hi ha crescut: clapes verdes a l'escorça (no al tall)
    m = v.own == v.idx(sid)
    if m.any():
        lum = v.col[m].sum(-1) / 3
        X, Y = v.X[m], v.Y[m]
        clapa = (fbm(X / 5.0, Y / 4.0, 151) > 0.58) | (fbm(X / 3.0, Y / 3.0, 153) > 0.7)
        lvl = 1.2 + lum / 26 + (hnp(X, Y, 155) - 0.5) * 0.8
        verd = v.to(MOLSA, lvl, m)
        col = v.col[m]
        col[clapa] = verd[clapa]
        v.col[m] = col
    # la terra que va tornar al forat, amb herbes al voltant de la soca
    for k, (dx, dz, r) in enumerate(((-58, -22, 14), (46, -30, 11), (-20, -46, 9), (70, 8, 10))):
        roc(v, e, c + np.array((dx, 0, dz)), r, HERBA, sid + '_herba', seed=157 + k, lvl0=3.2, aplana=0.55)


def rodanxes(v, e, sid='rodanxes'):
    """El tronc de l'avet tallat a rodanxes, apilades en piràmide amb el tall de cara (fusta clara i anells)."""
    n = np.array((0, 0, -1.0))
    pila = [(-46, 0), (0, 0), (46, 0), (-23, 1), (23, 1), (0, 2)]
    r = 22.0
    for (dx, fila) in pila:
        c = RODANXES + np.array((dx, r + fila * (2 * r - 6), -fila * 4.0))
        # la closca (l'escorça del costat, una mica més enrere)
        _arrel(v, e, c + np.array((0, 0, 30)), c + np.array((0, 0, 2)), r, sid, cap=False)
        _tall(v, e, c, n, r, sid)


def forat_nou(v, e, gran=False, sid='forat_nou'):
    """El forat nou per al plançó, al costat de les arrels velles: petit (marcat amb la pala) o eixamplat."""
    rx, rz = (34.0, 20.0) if gran else (18.0, 11.0)
    t = x_pla_y(v, 0.3)
    P = v.punt(np.where(np.isinf(t), 0, t))
    d = P - FORAT_NOU
    r = np.sqrt((d[..., 0] / rx) ** 2 + (d[..., 2] / rz) ** 2)
    m = np.isfinite(t) & (r < 1.5)
    lv = np.where(r < 1, 1.0 + (d[..., 2] > 0) * 1.4 - (1 - r) * 0.6, 3.8 + (fbm(d[..., 0] / 5, d[..., 2] / 4, 141) - 0.5) * 1.8)
    lv = lv + _llum(e, np.array((0, 1.0, 0))) * 0.6
    v.pinta(m & (t <= v.z + 1), t - 0.5, v.to(TERRA, lv), sid, prof=False)
    if gran:
        # el munt de terra tret, al costat
        roc(v, e, FORAT_NOU + np.array((44.0, 0, 6)), 16, TERRA, sid, seed=143, lvl0=3.6, aplana=0.5)
        roc(v, e, FORAT_NOU + np.array((52.0, 0, -6)), 11, TERRA, sid, seed=145, lvl0=3.8, aplana=0.5)


def arbret(v, e, base, h, sid, seed=3):
    """Un avet petit (el plançó): el tronc prim i els pisos de branques en con, de lluny a prop."""
    rng = np.random.default_rng(seed)
    taques = []
    for y in np.arange(0, h, 2.0):
        taques.append((base + np.array((0, y, 0)), 1.6, 'tronc', 0))
    y = h * 0.18
    while y < h:
        R = (h - y) / h * h * 0.32 + 2
        for k in range(9):
            a = rng.uniform(0, 2 * math.pi)
            for f in (0.35, 0.7, 1.0):
                P = base + np.array((math.cos(a) * R * f, y - R * f * 0.25, math.sin(a) * R * f))
                taques.append((P, 3.2 * (1.1 - f * 0.4), 'fulla', f))
        y += rng.uniform(5, 8)
    taques.sort(key=lambda q: -v.cam.vista(tuple(q[0]))[2])
    idx = v.idx(sid)
    for P, r, k, f in taques:
        u, vv, z = v.cam.projecta(tuple(P))
        R = max(0.6, r * v.cam.f / z)
        x0, x1, y0, y1 = int(u - R - 1), int(u + R + 1), int(vv - R - 1), int(vv + R + 1)
        sub = (slice(max(0, y0), max(0, y1) + 1), slice(max(0, x0), max(0, x1) + 1))
        X, Y = v.X[sub], v.Y[sub]
        dx, dy = (X + 0.5 - u) / R, (Y + 0.5 - vv) / (R * 0.7)
        m = (dx * dx + dy * dy < 1) & (z < v.z[sub])
        ramp = AVET if k == 'fulla' else ESCORÇA
        lv = (3.4 + f * 1.6 - dy * 0.9 if k == 'fulla' else 3.0) + _llum(e, np.array((0, 1.0, 0)))
        ii = np.clip(np.floor(lv + v.bayer[sub] - 0.5), 0, len(ramp) - 1).astype(int)
        v.col[sub][m] = ramp[ii][m]
        v.z[sub][m] = z
        v.own[sub][m] = idx


def carretilla(v, e, sid='carretilla'):
    """La civera de fusta amb el plançó (l'identificador continua sent `carretilla`; al 1017 no n'hi havia, de
    carretilles): dos braços llargs que sobresurten per davant i per darrere, el pla de posts al mig i quatre
    peus curts; a dins, el pa de terra embolicat amb sac i l'avet petit."""
    c, rot = CARRETILLA
    cr, sr = math.cos(rot), math.sin(rot)
    ux, uz = np.array((cr, 0, sr)), np.array((-sr, 0, cr))
    y_b = 15.0                                         # l'alçada dels braços
    # els peus (de darrere a davant, perquè els de davant tapin)
    for sg in (1, -1):
        for dx in (-22, 22):
            _barra(v, e, c + ux * dx + uz * 12 * sg, c + ux * dx + uz * 12 * sg + np.array((0, y_b, 0)), 1.5, FUSTA, 2.8, sid)
    # el braç de darrere, el pla de posts i el travesser, i el braç de davant
    _barra(v, e, c - ux * 60 + uz * 13 + np.array((0, y_b, 0)), c + ux * 60 + uz * 13 + np.array((0, y_b, 0)), 1.7, FUSTA, 3.2, sid)
    _caixa(v, e, c + np.array((0, y_b + 2, 0)), 28, 2, 12, FUSTA, 3.6, sid, rot)
    for dx in (-18, -6, 6, 18):                         # les juntes de les posts
        _barra(v, e, c + ux * dx + uz * 12 + np.array((0, y_b + 4.2, 0)), c + ux * dx - uz * 12 + np.array((0, y_b + 4.2, 0)), 0.5, FUSTA, 1.6, sid)
    _barra(v, e, c - ux * 60 - uz * 13 + np.array((0, y_b, 0)), c + ux * 60 - uz * 13 + np.array((0, y_b, 0)), 1.7, FUSTA, 3.4, sid)
    # el pa de terra amb sac, i el plançó (sense, si ja l'han agafat: només hi queda una mica de terra)
    if 'carretilla_buida' in e.extres:
        roc(v, e, c + np.array((0, y_b + 6, 0)), 9, TERRA, sid, seed=153, lvl0=3.0, aplana=0.4)
        return
    roc(v, e, c + np.array((0, y_b + 10, 0)), 12, _r((60, 44, 28), (100, 76, 48), (140, 110, 72), (176, 146, 100), (204, 178, 128)), sid, seed=151, lvl0=3.0, aplana=0.8)
    arbret(v, e, c + np.array((0, y_b + 16, 0)), 52, sid, seed=5)


def planco(v, e, sid='planco_plantat'):
    """El plançó plantat al forat, amb la cinta blanca lligada al tronc."""
    arbret(v, e, PLANCO + np.array((0, 1.0, 0)), 62, sid, seed=5)
    # la cinta (blanca) al tronc
    u, vv, z = v.cam.projecta(tuple(PLANCO + np.array((0, 20, -2))))
    k = v.cam.f / z
    for dx in range(-2, 3):
        for dy in range(0, 2):
            X, Y = int(u) + dx, int(vv) + dy
            if 0 <= X < v.w and 0 <= Y < v.h:
                v.col[Y, X] = (236, 232, 220)
                v.own[Y, X] = v.idx(sid)
    for dx, dy in ((2, 2), (3, 3), (2, 4)):
        X, Y = int(u) + dx, int(vv) + dy
        v.col[Y, X] = (220, 214, 200)
        v.own[Y, X] = v.idx(sid)


def segell_planco(v, e, sid='segell_planco'):
    """El segell vermell del jutge a la cinta del plançó."""
    u, vv, z = v.cam.projecta(tuple(PLANCO + np.array((0, 20, -2))))
    for dx, dy, c in ((3, 1, 3), (4, 1, 4), (3, 2, 2), (4, 2, 3), (3, 0, 4)):
        X, Y = int(u) + dx, int(vv) + dy
        v.col[Y, X] = CERA[c]
        v.own[Y, X] = v.idx(sid)


LLETRES_ROTUL = {'A': ['010', '101', '111', '101', '101'], 'V': ['101', '101', '101', '101', '010'],
                 'E': ['111', '100', '110', '100', '111'], 'T': ['111', '010', '010', '010', '010']}


def rotul(v, e, sid='rotul_clavat'):
    """El tros de fusta amb «AVET», clavat al costat del plançó: el pal, la post, i les lletres (fosques sobre clar,
    rectes: la post és gairebé de cara)."""
    _barra(v, e, ROTUL, ROTUL + np.array((0, 30, 0)), 1.8, FUSTA, 3.2, sid)
    c = ROTUL + np.array((0, 34, -2))
    n = np.array((0.0, 0, -1))
    ex, ey = np.array((1.0, 0, 0)), np.array((0, 1.0, 0))
    t = x_pla(v, c, n)
    P = v.punt(np.where(np.isinf(t), 0, t))
    q = P - c
    a, b = q @ ex, q @ ey
    m = np.isfinite(t) & (np.abs(a) < 17) & (np.abs(b) < 8)
    lv = 4.6 + _llum(e, np.broadcast_to(n, P.shape)) * 0.5 - (np.abs(b) > 6.5) * 1.2 + (hnp(v.X // 3, v.Y, 61) - 0.5) * 0.6
    v.pinta(m, t, v.to(FUSTA, lv), sid)
    # les lletres
    u, vv, z = v.cam.projecta(tuple(c))
    x0, y0 = round(u) - 7, round(vv) - 2
    for i, ch in enumerate('AVET'):
        for fy, row in enumerate(LLETRES_ROTUL[ch]):
            for fx, bit in enumerate(row):
                if bit == '1':
                    X, Y = x0 + i * 4 + fx, y0 + fy
                    v.col[Y, X] = (40, 24, 16)
                    v.own[Y, X] = v.idx(sid)


def florit(v, e, sid='florit'):
    """Un arbre florit a l'hort, darrere el mur (on hi havia l'avet): un castanyer d'Índia, com el de la foto de
    l'absis: el tronc i les branques, la capçada de fulles verdes en grumolls i les flors blanques (en espelmes)."""
    rng = np.random.default_rng(17)
    base = FLORIT
    _arrel(v, e, base, base + np.array((6, 150, 0)), 15, sid, cap=False)
    for k in range(5):
        a = -0.9 + k * 0.45
        _arrel(v, e, base + np.array((6, 130, 0)), base + np.array((math.sin(a) * 140, 210 + math.cos(a) * 60, rng.uniform(-30, 30))), 6, sid)
    # grumolls de fulles: cada un, una bola amb llum de dalt a la dreta
    grums = []
    for _ in range(70):
        a, r = rng.uniform(0, 2 * math.pi), rng.uniform(0, 1) ** 0.6
        c = base + np.array((math.cos(a) * r * 230, 250 + math.sin(a) * r * 95 + rng.normal(0, 14), rng.uniform(-90, 90)))
        grums.append((c, rng.uniform(34, 52)))
    grums.sort(key=lambda q: -v.cam.vista(tuple(q[0]))[2])
    FL = _r((60, 80, 40), (100, 120, 60), (170, 180, 140), (226, 220, 210), (246, 236, 236), (255, 250, 250))
    for c, rad in grums:
        taques = []
        for _ in range(26):
            d = rng.normal(0, 1, 3)
            d = d / np.linalg.norm(d)
            P = c + d * rad * rng.uniform(0.5, 1.0)
            taques.append((P, d, rng.uniform() < 0.33 and d[1] > -0.2))
        taques.sort(key=lambda q: -v.cam.vista(tuple(q[0]))[2])
        for P, d, flor in taques:
            u, vv, z = v.cam.projecta(tuple(P))
            R = max(0.8, (5.0 if flor else 9.0) * v.cam.f / z)
            ry = R * (1.6 if flor else 0.7)
            sub = (slice(max(0, int(vv - ry)), max(0, int(vv + ry)) + 1), slice(max(0, int(u - R)), max(0, int(u + R)) + 1))
            X, Y = v.X[sub], v.Y[sub]
            dx, dy = (X + 0.5 - u) / R, (Y + 0.5 - vv) / ry
            m = (dx * dx + dy * dy < 0.7 + 0.4 * hnp(X, Y, 71)) & (z < v.z[sub])
            luz = float(np.clip(d @ SOL_DIR, 0, 1))
            if flor:
                lv = 3.6 + luz * 1.6 - dy * 0.6 + (hnp(X, Y, 73) - 0.5) * 1.0
                ramp = FL
            else:
                lv = 3.4 + luz * 2.2 - dy * 0.8 + (hnp(X, Y, 77) - 0.5) * 1.4 + d[1] * 0.8
                ramp = HERBA
            ii = np.clip(np.floor(lv + v.bayer[sub] - 0.5), 0, len(ramp) - 1).astype(int)
            col = ramp[ii]
            if flor:
                rosa = hnp(X, Y, 75) > 0.8
                col = np.where(rosa[..., None], col * np.array((1.0, 0.84, 0.86)), col)
            v.col[sub][m] = col[m]
            v.z[sub][m] = z
            v.own[sub][m] = v.idx(sid)


def herbes(v, e, sid='primer_pla'):
    """El primer pla de primavera: mates d'herba i flors grogues i blanques a baix a l'esquerra, tallades per la vora."""
    rng = np.random.default_rng(23)
    for _ in range(60):
        x, z = rng.uniform(-330, -170), rng.uniform(386, 430)
        roc(v, e, np.array((x, 0, z)), rng.uniform(5, 11), HERBA, sid, seed=int(x * 7) & 255, lvl0=3.2, aplana=1.1)
    for _ in range(40):
        x, z = rng.uniform(-320, -180), rng.uniform(380, 420)
        u, vv, zz = v.cam.projecta((x, rng.uniform(6, 14), z))
        X, Y = int(u), int(vv)
        if 0 <= X < v.w - 1 and 0 <= Y < v.h - 1:
            c = (236, 206, 70) if rng.uniform() < 0.6 else (240, 238, 226)
            for dx, dy in ((0, 0), (1, 0), (0, 1), (1, 1)):
                v.col[Y + dy, X + dx] = c
                v.own[Y + dy, X + dx] = v.idx(sid)
    roc(v, e, np.array((-262.0, 0.0, 392.0)), 22, PEDRA, sid, seed=7, lvl0=2.8)


# ─── El reflex dels bassals, la pluja ────────────────────────────────────────

def reflexos(v, e):
    """Als bassals, el que hi ha a sobre, girat: es camina pel raig reflectit en pantalla fins que troba alguna cosa
    a la profunditat que toca (com un reflex en espai de pantalla), i si no, el cel."""
    m = getattr(v, 'aigua', None)
    if m is None:
        return
    m = m & (v.own == v.idx('terra'))                    # (només on el terra és el que es veu)
    if not m.any():
        return
    ys, xs = np.nonzero(m)
    t = v.terra_t[ys, xs]
    cam = v.cam
    hor = cam.centre[1]
    col0 = v.col.copy()
    zbuf = v.z
    out = np.zeros((len(ys), 3))
    found = np.zeros(len(ys), bool)
    em = np.zeros(len(ys), bool)
    # el raig reflectit: des del punt del bassal (a terra), amb la mateixa inclinació però cap amunt
    k = cam.pos[1] / t                                       # pendent del raig
    for zz in np.linspace(1.02, 6.0, 64):
        zo = t * zz                                          # la profunditat que provem
        hh = k * (zo - t)                                    # l'alçada del raig reflectit allà
        vo = hor - cam.f * (hh - cam.pos[1]) / zo
        ok = ~found & (vo >= 0) & (vo < v.h)
        vi = np.clip(vo.astype(int), 0, v.h - 1)
        hit = ok & (zbuf[vi, xs] <= zo * 1.02) & (zbuf[vi, xs] > t * 1.01)
        out[hit] = col0[vi[hit], xs[hit]]
        em[hit] = v.emissiu[vi[hit], xs[hit]]
        found |= hit
        above = ~found & (vo < 0)
        found |= above
    # el que no ha trobat res: el cel (la fila de dalt de tot de la columna)
    sky = ~found | (out.sum(-1) == 0)
    out[sky] = col0[0, xs[sky]] if e.llum != 'nit' else col0[2, xs[sky]]
    aigua = {'pluja': (np.array((96, 102, 108)), 0.84), 'sol': (np.array((40, 70, 110)), 0.8),
             'llamp': (np.array((120, 130, 160)), 0.7), 'nit': (np.array((10, 14, 24)), 0.6),
             'primavera': (np.array((40, 70, 110)), 0.75)}[e.llum]
    rgb = out * aigua[1] + aigua[0] * (1 - aigua[1])
    # una mica d'ona: les files del bassal, alternes, una mica més fosques
    rgb = rgb * (1 - 0.06 * ((ys + (xs // 7)) % 3 == 0))[:, None]
    v.col[ys, xs] = rgb
    v.emissiu[ys[em], xs[em]] = True


def pluja_frames(v_h=RH, n=8, dens=520, seed=3, llarg=(5, 9), inc=0.35, col=(214, 220, 224), alpha=150,
                 ones=None):
    """Fotogrames de pluja en diagonal (transparents), en bucle: cada gota baixa i torna a dalt."""
    rng = np.random.default_rng(seed)
    gotes = [(rng.uniform(-60, W), rng.uniform(0, v_h), rng.integers(llarg[0], llarg[1] + 1), rng.uniform(0.6, 1.0))
             for _ in range(dens)]
    frames = []
    for i in range(n):
        a = np.zeros((H, W, 4), np.uint8)
        for (x, y, L, br) in gotes:
            yy = (y + i * v_h / n * 1.0) % v_h
            xx = x + yy * inc
            for j in range(L):
                X, Y = int(xx + j * inc), int(yy + j)
                if 0 <= X < W and 0 <= Y < v_h:
                    a[Y, X] = (*col, int(alpha * br * (0.5 + 0.5 * j / L)))
        if ones is not None:
            for (x, y, ph) in ones:
                r = ((i + ph) % n) / n * 4 + 1
                for th in np.linspace(0, 2 * math.pi, 18):
                    X, Y = int(x + math.cos(th) * r), int(y + math.sin(th) * r * 0.35)
                    if 0 <= X < W and 0 <= Y < v_h:
                        a[Y, X] = (*col, int(120 * (1 - (r - 1) / 4)))
        frames.append(Image.fromarray(a, 'RGBA'))
    return frames


def ones_bassals(v, n=40, seed=5):
    """Punts dels bassals on cauen gotes (per a les ones de la pluja)."""
    m = getattr(v, 'aigua', None)
    if m is None:
        return []
    m = m & (v.own == v.idx('terra'))
    if not m.any():
        return []
    ys, xs = np.nonzero(m)
    rng = np.random.default_rng(seed)
    sel = rng.choice(len(ys), size=min(n, len(ys)), replace=False)
    return [(int(xs[i]), int(ys[i]), int(rng.integers(0, 8))) for i in sel]


# ─── La gent de fons ────────────────────────────────────────────────────────

ROBES = [(96, 74, 54), (70, 62, 58), (120, 96, 66), (88, 58, 46), (110, 100, 84), (64, 70, 60), (132, 110, 80),
         (78, 54, 40), (100, 84, 70), (58, 52, 50)]
MOCADORS = [(214, 204, 180), (182, 170, 150), (150, 120, 90), (196, 186, 166)]
PELL = [(214, 168, 132), (190, 140, 106), (226, 186, 150), (168, 120, 90)]


def figura(v, e, P, alt=86.0, roba=(96, 74, 54), cap='nu', seed=1, sid='poble', mira=0.0, monja=False, nen=False,
           ample=1.0):
    """Una persona de fons, de l'any mil, a la seva profunditat: la túnica llarga, el cap (nu, amb mocador o amb
    caputxa), les mans; o una monja (hàbit negre, toca blanca). Dibuixada de cara, sense animar. `ample`: l'amplada
    (i el cap) respecte de l'alçada; > 1 per a una figura ajupida, que fa menys alçada però la mateixa amplada."""
    cam = v.cam
    rng = np.random.default_rng(seed)
    u, vv, z = cam.projecta(tuple(P))
    k = cam.f / z
    if nen:
        alt *= 0.62
    h = alt * k
    if h < 6:
        return
    w = h * 0.25 * ample
    X0, X1 = int(u - w * 1.3 - 2), int(u + w * 1.3 + 2)
    Y0, Y1 = int(vv - h - 2), int(vv + 1)
    sub = (slice(max(0, Y0), min(v.h, Y1 + 1)), slice(max(0, X0), min(v.w, X1 + 1)))
    X, Y = v.X[sub] + 0.5, v.Y[sub] + 0.5
    fy = (vv - Y) / h                                   # 0 als peus, 1 al cap
    fx = (X - u) / w                                    # -1..1 a l'amplada de les espatlles
    sk = np.array(PELL[seed % len(PELL)], float)
    if monja:
        roba = (34, 30, 34)
    rb = np.array(roba, float)
    out = np.zeros(X.shape + (3,))
    m = np.zeros(X.shape, bool)
    # la túnica: de les espatlles (fy 0.82) fins als peus, eixamplant-se
    esp = 1 - 0.18 * ample                               # les espatlles (0,82 dreta)
    half = 0.74 + (esp - fy) * 0.42 / ample
    half = half * np.sqrt(np.clip(1 - ((fy - (esp - 0.16 * ample)) / (0.17 * ample)).clip(0, None) ** 2, 0, 1))      # les espatlles, rodones
    half = half + 0.05 * (np.abs(fy - 0.35) < 0.3) * np.sin(seed + fy * 9)                  # (cada roba cau diferent)
    tun = (fy > 0.0) & (fy < esp) & (np.abs(fx) < half)
    sh = np.clip(0.75 + 0.35 * (-fx) * 0.5 + 0.15 * (fy - 0.4), 0.45, 1.2)
    # les arrugues verticals
    sh = sh - 0.08 * (np.abs(((fx + 1) * 2.2) % 1 - 0.5) < 0.12) * (fy < 0.6)
    out = np.where(tun[..., None], rb * sh[..., None], out)
    m |= tun
    # el cinturó
    cint = tun & (np.abs(fy - 0.5) < 0.025)
    out = np.where(cint[..., None], rb * 0.5, out)
    # les mans, juntes davant o al costat
    ma = (np.abs(fy - 0.47) < 0.035) & (np.abs(fx - 0.05 * mira) < 0.28)
    out = np.where((ma & tun)[..., None], sk * 0.85, out)
    # el cap
    hc = 1 - 0.1 * ample
    cap_r = 0.09 * ample
    dcap = np.hypot(fx * w / h, fy - hc)
    head = dcap < cap_r
    m |= head
    cara = np.where((fx * w / h) * (1 if mira >= 0 else -1) > 0.01, 0.82, 1.0)
    out = np.where(head[..., None], sk * cara[..., None], out)
    if monja:
        toca = (dcap < cap_r * 1.35) & ~((dcap < cap_r * 0.8) & (fy < hc + 0.03))
        out = np.where(toca[..., None], np.array((40, 36, 40.0)), out)
        cinta = (dcap < cap_r * 1.0) & (fy > hc + 0.02) & (fy < hc + 0.05)
        out = np.where(cinta[..., None], np.array((222, 220, 210.0)), out)
        bavet = (np.abs(fx) < 0.55) & (fy > 0.72) & (fy < 0.83)
        out = np.where(bavet[..., None], np.array((220, 218, 206.0)), out)
        m |= toca
    elif cap == 'mocador':
        mc = np.array(MOCADORS[seed % len(MOCADORS)], float)
        moc = (dcap < cap_r * 1.2) & ~((dcap < cap_r * 0.78) & (fy < hc + 0.02))
        out = np.where(moc[..., None], mc, out)
        m |= moc
    elif cap == 'caputxa':
        cp = (dcap < cap_r * 1.3) & ~((dcap < cap_r * 0.72) & (fy < hc + 0.0))
        out = np.where(cp[..., None], rb * 0.8, out)
        m |= cp
    else:
        pel = (dcap < cap_r) & (fy > hc + 0.03)
        out = np.where(pel[..., None], np.array((70, 50, 36.0)) * (0.7 + 0.3 * (seed % 3)), out)
    # la llum de la sala
    L = float(_llum(e, np.array((0, 1.0, 0))))
    if e.llum in ('sol', 'primavera'):
        side = np.where(fx > 0.2, 1.12, 0.86)
        out = out * side[..., None]
    k_ll = {'pluja': 0.78, 'sol': 1.0, 'primavera': 1.0, 'nit': 0.32, 'llamp': 0.9}[e.llum]
    out = out * k_ll
    # les vores, una mica més fosques (sense halo: la vora del costat, enfosquida)
    tz = np.full(m.shape, z)
    mm = m & (tz < v.z[sub])
    v.col[sub][mm] = out[mm]
    v.z[sub][mm] = z
    v.own[sub][mm] = v.idx(sid)


def gent(v, e, llista, sid):
    """Pinta una llista de figures (x, z, opcions), de lluny a prop."""
    for (x, z, opt) in sorted(llista, key=lambda q: -q[1]):
        figura(v, e, np.array((x, 0.0, z)), sid=sid, **opt)


# ─── Els acabats ────────────────────────────────────────────────────────────

def grading(v, e):
    """El color de cada llum: la pluja, freda i grisa; el sol, net i càlid; la nit, blava i fosca."""
    c = v.col
    llums = v.col[v.emissiu].copy()
    lum = c @ np.array((0.3, 0.59, 0.11))
    if e.llum == 'pluja':
        c = c * 0.72 + lum[..., None] * 0.28
        c = c * np.array((0.96, 0.99, 1.02))
    elif e.llum == 'sol':
        c = c * np.array((1.04, 1.0, 0.94))
    elif e.llum == 'primavera':
        c = c * np.array((1.02, 1.03, 0.95))
    elif e.llum == 'nit':
        c = c * 0.62 + lum[..., None] * 0.16
        c = c * np.array((0.66, 0.76, 1.12))
    elif e.llum == 'llamp':
        c = c * 0.7 + lum[..., None] * 0.35
        c = c * np.array((0.92, 0.98, 1.16))
    c[v.emissiu] = llums
    v.col = np.clip(c, 0, 255)


# ─── L'escena sencera ───────────────────────────────────────────────────────

def escena(e, extra=None):
    """→ la Vista amb tot pintat segons l'estat (sense els acabats)."""
    v = Vista(e.cam or CAM, e.h)
    cel(v, e)
    fons(v, e)
    terra(v, e)
    absis(v, e)
    mur(v, e)
    if e.arbre == 'ajagut':
        avet(v, e)
        arrels(v, e)
    elif e.arbre == 'dret':
        avet(v, e, angle=0.0)
    elif isinstance(e.arbre, float):
        avet(v, e, angle=e.arbre)
    branques(v, e)
    if e.branca_trencada:
        branca_trencada(v, e)
    if e.faristol:
        faristol(v, e)
        if e.ordre:
            ordre(v, e)
    if e.cera:
        cera(v, e)
    if e.cera_agafada:
        cera_agafada(v, e)
    if 'florit' in e.extres:
        florit(v, e)
    if e.arbre == 'cap' and e.forat == 'vell':
        soca_vella(v, e)
    if 'rodanxes' in e.extres:
        rodanxes(v, e)
    if 'forat_nou' in e.extres or 'forat_gran' in e.extres:
        forat_nou(v, e, gran='forat_gran' in e.extres)
    if 'carretilla' in e.extres:
        carretilla(v, e)
    if 'planco' in e.extres:
        planco(v, e)
    if 'segell_planco' in e.extres:
        segell_planco(v, e)
    if 'rotul' in e.extres:
        rotul(v, e)
    if 'cofre' in e.extres:
        cofre(v, e)
    if 'abeurador' in e.extres:
        abeurador(v, e)
    if 'primer_pla' in e.extres:
        primer_pla(v, e)
    if 'herbes' in e.extres:
        herbes(v, e)
    if extra:
        extra(v, e)
    reflexos(v, e)
    grading(v, e)
    return v


@functools.lru_cache(maxsize=None)
def render(e, extra=None):
    """→ (imatge RGBA 640×360, Vista)."""
    v = escena(e, extra)
    return v.imatge(), v


def diff(img, base):
    """Només el que canvia (la resta, transparent)."""
    a, b = np.asarray(img.convert('RGBA')), np.asarray(base.convert('RGBA'))
    keep = (a != b).any(axis=2)
    return Image.fromarray(np.where(keep[..., None], a, 0).astype(np.uint8), 'RGBA')


# ─── Geometria ──────────────────────────────────────────────────────────────

def p(x, z, y=0.0, cam=CAM):
    """Un punt del món → (u, v) de sala."""
    u, vv, _ = cam.projecta((x, y, z))
    return round(u), round(vv)


def escala(z, cam=CAM):
    return cam.f / z


def rect_mascara(v, sids, marge=0):
    """El rectangle (x0, y0, x1, y1) que ocupen els píxels de `sids`."""
    m = v.mascara(sids)
    ys, xs = np.nonzero(m)
    if not len(xs):
        return None
    return (max(0, xs.min() - marge), max(0, ys.min() - marge), min(W - 1, xs.max() + marge),
            min(v.h - 1, ys.max() + marge))


def z_de_v(vy, cam=CAM):
    """La profunditat del terra que es veu a la fila vy."""
    return cam.f * cam.pos[1] / (vy - cam.centre[1])
