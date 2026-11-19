"""
Aigua Verne — el fons dels crèdits (pantalla sencera de 640×360, sense barra de verbs). A 1×; la Cantimplora, EN 3D
(el model canònic de cantimplora_comu.py, amb hd640/tres_d.py).

El sistema de Vesper de nit, en un pla de cinema: **contrast d'escala**. Terra-2, enorme i a prop, treu el cap pel
cantó de baix a la dreta (tallat pel quadre), amb el front de tempesta damunt i la pluja; l'estrella, Vesper, treu el
cap pel cantó de dalt a l'esquerra i il·lumina la falç de tots els planetes per aquell costat. Lluny, petits: Aqua i
Ferrum (també amb núvols de pluja) a dalt, i Verdant a l'esquerra, net i brillant, amb el palau orbital (un punt
daurat). La Cantimplora, petita, en 3/4 (de proa i d'estribord, una mica des de dalt: els dipòsits del llom), torna
cap a Terra-2 amb la brasa dels motors encesa; l'estela fa una corba des de Verdant fins a la nau: és la línia que
porta l'ull de Verdant a Terra-2, per sota del text.

El mig de la pantalla (≈140..500 × 120..250, on el joc posa la caixa del text dels crèdits) queda fosc i net: només
estrelles i la nebulosa, molt fluixa.

ANIMS: `pluja` (els fils de pluja damunt dels núvols dels tres planetes), `estrelles` (algunes estrelles que fan
pampallugues) i `motors` (la brasa dels motors que batega i les espurnes que corren per l'estela).
"""
import hd640  # noqa: F401  (abans de cap hd.rooms: posa la llibreria a 640×360)

import functools
import math

from hd.pix import Canvas, Light, W, H, hr, mix
from hd.rooms.comu import _diff
from hd.rooms.exterior import fbm, smooth
from hd640.rooms.cantimplora_comu import Cantimplora
from hd640.tres_d import Camera, Escena, Llum

STAR = (-46, -58)                        # Vesper, fora de la pantalla per dalt a l'esquerra
STAR_R = 128
LIGHT = Light(ambient=0.0, vignette=None, floor_fade=None)

_ANIM = {'pluja': None, 'estrelles': None}

SPACE = [(2, 2, 8), (5, 4, 14), (9, 7, 22), (14, 10, 30), (22, 14, 38), (34, 20, 44), (52, 28, 48),
         (76, 38, 48)]
T2 = [(20, 12, 10), (46, 30, 20), (82, 56, 36), (122, 88, 56), (160, 120, 78), (196, 154, 104), (226, 190, 140),
      (244, 220, 176)]
AQ = [(10, 18, 30), (24, 42, 64), (48, 78, 104), (86, 120, 146), (132, 164, 184), (180, 204, 218), (220, 234, 240),
      (246, 250, 252)]
FE = [(12, 8, 8), (30, 18, 16), (56, 32, 26), (86, 50, 36), (116, 70, 48), (148, 94, 64), (176, 122, 86),
      (204, 154, 116)]
VE = [(4, 30, 10), (8, 60, 18), (14, 100, 28), (24, 144, 40), (50, 190, 56), (110, 230, 90), (190, 255, 160),
      (240, 255, 230)]
CLOUD = [(30, 32, 40), (54, 58, 68), (84, 88, 98), (118, 122, 130), (156, 160, 166), (196, 198, 202),
         (228, 230, 232)]

# nom, centre, radi, rampa, pluja?
PLANETS = (
    ('verdant', (62, 236), 11, VE, False),
    ('aqua', (402, 54), 15, AQ, True),
    ('ferrum', (566, 112), 21, FE, True),
    ('terra2', (660, 528), 296, T2, True),         # a prop: només en treu el cap la falç de dalt a l'esquerra
)
TEXT_BOX = (140, 120, 500, 250)                    # on el joc posa el text dels crèdits: fosc i net


def _dins_text(x, y, marge=0):
    x0, y0, x1, y1 = TEXT_BOX
    return x0 - marge <= x <= x1 + marge and y0 - marge <= y <= y1 + marge


def space(cv, tw=None):
    for y in range(H):
        for x in range(W):
            d = math.hypot(x - STAR[0], y - STAR[1])
            lvl = 0.5 + 3.4 * max(0.0, 1 - d / 430) ** 2.4
            neb = fbm(x / 120 + 3, y / 64, 91)
            k = 1.5 * (0.35 + 0.65 * max(0.0, 1 - d / 640))
            if _dins_text(x, y, 30):                                     # la nebulosa, més fluixa darrere el text
                k *= 0.45
            lvl += smooth(0.52, 0.82, neb) * k
            cv.put(x, y, SPACE, lvl, lit=0)
            if hr(x, y, 92) > 0.9968:
                b = hr(x, y, 93)
                col = (220, 224, 240) if b > 0.7 else (140, 140, 170) if b > 0.3 else (90, 86, 120)
                if tw is not None and hr(x, y, 94 + tw) > 0.85:
                    col = (60, 56, 80)
                cv.flat(x, y, col)
                if b > 0.94:
                    for dx, dy in ((1, 0), (-1, 0), (0, 1), (0, -1)):
                        cv.flat(x + dx, y + dy, mix(cv.get(x + dx, y + dy), (130, 130, 170), 0.5))
    # Vesper: la claror de l'estrella que treu el cap pel cantó
    cv.glow(STAR[0] + 40, STAR[1] + 40, 230, (255, 150, 70), 0.36)
    cv.glow(STAR[0] + 30, STAR[1] + 30, 150, (255, 210, 140), 0.5)
    sr = STAR_R
    ramp = [(200, 80, 20), (240, 130, 40), (255, 180, 80), (255, 220, 150), (255, 246, 220)]
    for y in range(0, STAR[1] + sr + 1):
        for x in range(0, STAR[0] + sr + 1):
            d = math.hypot(x - STAR[0], y - STAR[1])
            if d <= sr:
                cv.put(x, y, ramp, 4.2 - (d / sr) ** 3 * 3.0 + (fbm(x / 8, y / 8, 95) - 0.5) * 0.8, lit=0)
    # les òrbites: arcs de punts molt febles al voltant de l'estrella (no passen per darrere del text)
    for _, (px, py), _, _, _ in PLANETS[:3]:
        R = math.hypot(px - STAR[0], py - STAR[1])
        n = int(R * 2)
        for a in range(n):
            ang = a / n * math.pi / 2
            x, y = STAR[0] + math.cos(ang) * R, STAR[1] + math.sin(ang) * R
            if 0 <= x < W and 0 <= y < H and int(ang * R) % 7 == 0 and not _dins_text(x, y, 16):
                cv.flat(x, y, mix(cv.get(x, y), (90, 70, 110), 0.45))


def planet(cv, name, c, r, ramp, rain, drops=None):
    cx, cy = c
    lx, ly = STAR[0] - cx, STAR[1] - cy
    ln = math.hypot(lx, ly)
    lx, ly = lx / ln * 0.98, ly / ln * 0.98
    lz = 0.2
    seed = sum(map(ord, name))
    big = r > 60
    for y in range(max(0, int(cy - r - 3)), min(H, int(cy + r + 4))):
        for x in range(max(0, int(cx - r - 3)), min(W, int(cx + r + 4))):
            nx, ny = (x - cx) / r, (y - cy) / r
            d2 = nx * nx + ny * ny
            if d2 > 1:
                # l'atmosfera: una vora fina del costat de la llum (més ampla a la gran)
                at = 1.06 if big else 1.18
                if d2 < at and (nx * lx + ny * ly) > 0.0:
                    cv.flat(x, y, mix(cv.get(x, y), ramp[6 if big else 5],
                                      (0.55 if big else 0.35) * (at - d2) / (at - 1) * min(1.0, (nx * lx + ny * ly) * 2)))
                continue
            nz = math.sqrt(1 - d2)
            lam = max(0.0, nx * lx + ny * ly + nz * lz)
            u, v = nx / (nz + 0.6), ny / (nz + 0.6)
            n = fbm(u * 2.4 + 5, v * 2.4, seed)
            lvl = 0.7 + lam * 5.6 + (n - 0.5) * (2.2 if name != 'verdant' else 1.2) * (0.3 + lam)
            if big:
                lvl += (fbm(u * 14, v * 14, seed + 7) - 0.5) * 0.8 * (0.3 + lam)      # el relleu, de prop
                lvl -= (1 - nz) ** 3 * 0.8                                           # la vora, una mica més fosca
            if name == 'verdant':
                lvl += 0.6 if (int((u + 3) * 6) % 2) else 0                          # els camps, en ratlles perfectes
            cv.put(x, y, ramp, lvl, lit=0)
            if rain:
                # un front de tempesta: una banda espessa de núvols grisos que gira, i cúmuls arrodonits
                band = math.exp(-((v - 0.15 * math.sin(u * 3)) * 1.6) ** 2)
                cl = fbm(u * 2.0, v * 3.0, seed + 1) * 0.7 + band * 0.45
                if big:                                              # de prop: les vores dels cúmuls, esfilagarsades
                    cl += (fbm(u * 9, v * 12, seed + 5) - 0.5) * 0.28
                k = smooth(0.56, 0.66, cl) if big else smooth(0.5, 0.62, cl)
                if k > hr(x, y, seed) * 0.9 + 0.05:
                    bump = fbm(u * 7, v * 7, seed + 2) + (fbm(u * 26, v * 26, seed + 4) - 0.5) * (0.9 if big else 0)
                    cvl = 0.6 + lam * 4.4 + (bump - 0.5) * (3.4 if big else 2.0) - (1 - k) * (1.6 if big else 0.8)
                    cv.put(x, y, CLOUD, cvl, lit=0)
                    # la pluja: fils inclinats, de color blau pàl·lid, que baixen sota els núvols
                    if drops is not None and k > 0.7 and lam > 0.05:
                        step = 9 if big else 7
                        ph = (y - drops * (3 if big else 2) + int(x * 0.5)) % step
                        if ph == 0 and hr(x, (y - drops * 2) // step, seed + 3) > 0.45:
                            cv.flat(x, y, (176, 204, 236))
                            cv.flat(x + 1, y + 1, (110, 140, 190))
                            if big:
                                cv.flat(x + 2, y + 2, (90, 112, 160))
    if name == 'verdant':
        # massa brillant: el reflex
        hx, hy = cx + lx * r * 0.45, cy + ly * r * 0.45
        cv.flat(hx, hy, (255, 255, 255))
        cv.flat(hx + 1, hy, (220, 255, 220))
        cv.flat(hx, hy - 1, (220, 255, 220))
        # el palau orbital: un punt daurat amb una creu de llum
        px, py = cx + r + 8, cy - r + 1
        cv.flat(px, py, (255, 230, 140))
        for dx, dy in ((1, 0), (-1, 0), (0, 1), (0, -1)):
            cv.flat(px + dx, py + dy, (170, 140, 70))


# ─── La Cantimplora (el model canònic) ─────────────────────────────────────────
# La càmera mira endavant (+z); la nau és a 3.600 unitats, per sota de la càmera (es veu una mica des de dalt), i va
# cap a la dreta i cap a la càmera, cap a Terra-2: es veu la proa i el costat d'estribord.

CAM = Camera(pos=(0, 1150, 0), yaw=0.0, pitch=0.0, f=400, centre=(320, 180))
NAU_C = (60.0, 3600.0)                               # el mig del buc (x, z)
NAU_A = -0.74                                        # el rumb: cap a la dreta i cap a la càmera
_D = (math.cos(NAU_A), math.sin(NAU_A))
NAU = Cantimplora(popa=(NAU_C[0] - _D[0] * 200, NAU_C[1] - _D[1] * 200), rumb=NAU_A, porta='estribord')
LLUMS = [Llum((-1.4e6, 1.1e6, 1.5e5), 1e8, 2.3, power=1.0),          # Vesper, a dalt a l'esquerra
         Llum((2.5e5, -3.0e5, -1.0e5), 1e8, 0.5, power=1.0)]          # el reflex de Terra-2, a baix a la dreta
AMBIENT = -1.1
ESTELA_FI = (52, 252)                                # on es perd l'estela: a tocar de Verdant


def cantimplora(cv):
    e = Escena(cv, CAM, LLUMS, ambient=AMBIENT)
    NAU.dibuixa(e, porta_oberta=False, rampa=False, llums=True, to=((16, 18, 46), 0.22))
    NAU.resplendor(cv, cam=CAM, k=0.6)
    return e


def _toveres():
    pts = [NAU.xy(CAM, P) for P in NAU.TOVERES]
    return pts


def _estela_punts():
    """La corba de l'estela (en pantalla), dels motors cap enrere fins a Verdant: (x, y, t), t = 0 a la nau."""
    (ax, ay), (bx, by) = _toveres()
    x0, y0 = (ax + bx) / 2, (ay + by) / 2
    # surt cap enrere seguint l'eix de la nau i fa corba cap a Verdant, per sota del text
    cx, cy = NAU.xy(CAM, NAU.p(-1500, 0, 112))
    cy += 34                                                     # (la corba: baixa i torna a pujar cap a Verdant)
    x2, y2 = ESTELA_FI
    pts = []
    n = 900
    for i in range(n + 1):
        t = i / n
        x = (1 - t) ** 2 * x0 + 2 * (1 - t) * t * cx + t * t * x2
        y = (1 - t) ** 2 * y0 + 2 * (1 - t) * t * cy + t * t * y2
        pts.append((x, y, t))
    return pts


def estela(cv, fase=None):
    """L'estela dels motors: calenta i gruixuda a tocar de la nau, i cada cop més prima, freda i trencada enrere.
    `fase`: les espurnes que hi corren (l'animació)."""
    nau = set()
    zb = NAU.zb
    for i, z in enumerate(zb):
        if z < 1e9:
            nau.add(i)
    for x, y, t in _estela_punts():
        X, Y = int(x), int(y)
        if not (0 <= X < W and 0 <= Y < H) or Y * W + X in nau:
            continue
        a = (1 - t) ** 1.6
        if t > 0.35 and hr(X, Y, 96) > a * 1.6 + 0.25:
            continue
        col = mix((120, 140, 200), (255, 170, 90), max(0.0, 1 - t * 2.2))
        w = 1.4 * (1 - t) ** 2 + 0.2
        for dy in range(-int(w), int(w) + 1):
            if Y + dy < 0 or Y + dy >= H or (Y + dy) * W + X in nau:
                continue
            k = (0.75 * a + 0.12) * (1 - abs(dy) / (w + 1)) * (1.0 if dy == 0 else 0.6)
            cv.flat(X, Y + dy, mix(cv.get(X, Y + dy), col, k))
        if fase is not None and t < 0.7:
            # les espurnes: punts que corren enrere per l'estela
            if int(t * 900 - fase * 9) % 37 == 0:
                cv.flat(X, Y, mix((255, 230, 170), (170, 190, 240), t))


def motors(cv, fase=None):
    """La brasa dels motors: un punt calent a cada broquet i la claror, que batega."""
    k = 1.0 if fase is None else 0.75 + 0.25 * math.sin(fase * math.pi / 3)
    for u, v in _toveres():
        cv.glow(u, v, 5 + 2 * k, (255, 150, 70), 0.55 * k)
        cv.glow(u, v, 2.5, (255, 220, 160), 0.6 * k)
    NAU.brasa(cv, encesa=True, cam=CAM)


# ─── Composició ────────────────────────────────────────────────────────────

def bg(cv):
    space(cv, _ANIM['estrelles'])
    for name, c, r, ramp, rain in PLANETS:
        planet(cv, name, c, r, ramp, rain, _ANIM['pluja'])
    cantimplora(cv)
    estela(cv)
    motors(cv)


@functools.lru_cache(maxsize=None)
def _base_img():
    cv = Canvas(light=LIGHT)
    bg(cv)
    return cv.img.copy()


def _frames_estrelles(n):
    """Només les estrelles canvien: es redibuixa l'espai, i només compta on el fons de sempre és espai (no un
    planeta, la nau o l'estela)."""
    base = _base_img()
    ref = Canvas(light=LIGHT)
    space(ref, None)
    R, B = ref.img.load(), base.load()
    res = []
    for f in range(n):
        cv = Canvas(light=LIGHT)
        space(cv, f)
        A = cv.img.load()
        for y in range(H):
            for x in range(W):
                if B[x, y] != R[x, y]:
                    A[x, y] = B[x, y]
        res.append(_diff(cv.img, base))
    return res


def _frames_pluja(n):
    base = _base_img()
    out = []
    for f in range(n):
        _ANIM['pluja'] = f
        try:
            cv = Canvas(light=LIGHT, img=base.copy())
            for name, c, r, ramp, rain in PLANETS:
                if rain:
                    planet(cv, name, c, r, ramp, rain, f)
            cantimplora(cv)                              # (la nau i l'estela, per davant de Terra-2)
            estela(cv)
            motors(cv)
        finally:
            _ANIM['pluja'] = None
        out.append(_diff(cv.img, base))
    return out


def _frames_motors(n):
    base = _base_img()
    out = []
    for f in range(n):
        cv = Canvas(light=LIGHT, img=base.copy())
        estela(cv, f)
        motors(cv, f)
        out.append(_diff(cv.img, base))
    return out


PROPS = {}

ANIMS = {
    'pluja': {'frames': lambda: _frames_pluja(7), 'frameDuration': 110},
    'estrelles': {'frames': lambda: _frames_estrelles(6), 'frameDuration': 400},
    'motors': {'frames': lambda: _frames_motors(6), 'frameDuration': 120},
}

GEOMETRIA = {'things': {}, 'spawns': {}}
