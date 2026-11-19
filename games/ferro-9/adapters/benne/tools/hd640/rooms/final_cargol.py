"""
Final 3 · «Correspondència», EN PLA DE CINEMA (hd640/tres_d.py, a 1×): el moll de l'Estació d'Orís per damunt de
l'espatlla de la Vet.

- **Contrast d'escala:** el braç i la mà de la Vet, a tocar de la càmera, entren per baix a la dreta; en Cargol, vell
  i rovellat, és al pla mitjà a l'esquerra i allarga la pinça amb la carta plegada mil vegades; la directora jove,
  petita i lluny, s'ho mira al final del finestral, a la dreta.
- **3/4:** la càmera mira de biaix el finestral: la paret de vidre fuig cap a la dreta, amb els muntants (tres cares),
  l'ampit i les jardineres en escorç; el rètol «ESTACIÓ D'ORÍS» de bombetes, gran a l'esquerra, s'empetiteix cap
  al fons.
- **Línies que guien l'ull:** l'ampit, les jardineres i les juntes del terra fugen cap a la directora; el braç de la
  Vet i el d'en Cargol es troben a la carta.
- **Llum:** el sol entra pel finestral, de cara i des de l'esquerra: raigs a l'aire, clapes al terra partides pels
  muntants, i l'ombra llarga d'en Cargol cap a nosaltres; la Terra, enorme, pel vidre. El fons, amb una mica de
  boirina (desenfocat); en Cargol, la carta i la mà, nítids.

El quadre de text va al mig (≈145..495 × 150..225): la carta, la cara d'en Cargol i la mà en queden per sota, el
rètol per sobre. Les figures (en Cargol, la carta, la mà) són les del dibuix pla de sempre (final_cargol_pla_comu.py).

El món: x a la dreta, y amunt (0 = el terra), z endavant (la càmera a l'origen); 1 unitat = 1 píxel a la distància on
un personatge fa la seva mida (≈110 px).
"""
import hd640  # noqa: F401  (abans que cap hd.*: posa la llibreria de dibuix a 640×360)

import math
import random
from functools import lru_cache

import numpy as np
from PIL import Image, ImageDraw

from hd.pix import Canvas, Light, W, H, hr, mix
from hd640.rooms.proleg_gavina_pla_comu import espai, terra
from hd640.rooms.final_estacio_pla_comu import WALLW, DECK, MINT, POT, bulb_sign, planter, text5_width, _person
from hd640.rooms.final_cargol_pla_comu import cargol_gran, letter, vet_hand, S as CARGOL_S
from hd640.tres_d import Camera, Escena, Llum

hr = lru_cache(maxsize=1 << 19)(hr)

LIGHT = Light(ambient=0.0, vignette=None, floor_fade=None)       # (la llum és la del món: la de l'Escena)

CAM = Camera(pos=(0, 76, 0), yaw=0.40, pitch=0.0, f=420, centre=(320, 160))

ZW = 520                         # el pla del finestral
XA, XB = -420, 1500              # on comença i on s'acaba (fora de quadre)
SILL, TOP = 30, 215              # l'ampit i el travesser de dalt del vidre
SIGN0, SIGN1 = 215, 285          # la franja del rètol
CEIL = 400
MULL = [-150 + 250 * i for i in range(8)]       # els muntants (x del centre)
MW, MD = 24, 20                  # l'ample i el gruix d'un muntant
SUN = (-0.42, 0.52, 1.0)         # cap on és el sol (des de qualsevol punt de dins)
_n = math.sqrt(sum(c * c for c in SUN))
SUN = tuple(c / _n for c in SUN)
EARTH = (520, 330, 250)          # la Terra pel vidre (en pantalla)
HAZE = (214, 222, 236)

ROBOT = (2.3, 151.0)             # en Cargol: x, z dels peus (de les erugues)
ROBOT_FEET = (108, 240)          # els peus al fotograma de cargol_gran
DIRECTORA = (650.0, 470.0)
PILAR = (-52.0, 132.0)           # el pilar 7 (rovellat i repintat), en primer pla
PILARR = [(18, 10, 10), (34, 18, 16), (56, 28, 22), (82, 40, 28), (110, 56, 36), (140, 76, 48)]

LLUMS = [Llum((-400, 420, 1100), 2200, 0.6, power=1.0),           # el sol, darrere el vidre
         Llum((1200, 120, 900), 1600, 0.4, power=1.2)]            # la Terra, blava


# ─── El fons: el cel i la Terra (en pantalla: és infinitament lluny) ────────

@lru_cache(maxsize=None)
def _cel():
    sky = Canvas()
    espai(sky, 0, W - 1, seed=23)
    terra(sky, *EARTH)
    return sky.img


# ─── Les textures planes ────────────────────────────────────────────────────

SIGN_K = 7
SIGN_TXT = "ESTACIÓ D'ORÍS"
SIGN_X = -150                    # on comença el rètol (x del món)


@lru_cache(maxsize=None)
def _retol():
    """La franja del rètol de cara (640 × 70): panell blanc, la ratlla menta i les lletres de bombetes."""
    cv = Canvas(640, SIGN1 - SIGN0)
    h = SIGN1 - SIGN0
    for y in range(h):                                                # (la fila 0 és la de dalt)
        for x in range(640):
            lvl = 5.4 - y * 0.012 + (hr(x // 90, 2) - 0.5) * 0.3
            if y == 0:
                lvl = 7.0
            elif y >= h - 2:
                lvl = 2.0 if y == h - 1 else 3.0                      # la vora de sota, a l'ombra
            cv.put(x, y, WALLW, lvl, 0)
    for x in range(640):
        cv.put(x, 4, MINT, 4.6, 0)
        cv.put(x, 5, MINT, 3.4, 0)
    w = text5_width(SIGN_TXT, SIGN_K)
    bulb_sign(cv, SIGN_TXT, (640 - w) // 2, 16, SIGN_K, glow=False)
    return cv.img


@lru_cache(maxsize=None)
def _jardinera(seed, n):
    """Les plantes d'una jardinera, dibuixades de cara (n × 90): en surt la textura del pla de les plantes."""
    cv = Canvas(n, 110, transparent=True)
    planter(cv, 4, n - 4, 92, seed=seed, tall=56)
    return cv.img


# ─── L'escena ───────────────────────────────────────────────────────────────

def _sol_terra(x, z):
    """0..1: com de ple de sol és el punt (x, 0, z) del terra (el raig cap al sol passa pel vidre?)."""
    t = (ZW - z) / SUN[2]
    hy, hx = SUN[1] * t, x + SUN[0] * t
    if not (SILL + 2 < hy < TOP - 2):
        return 0.0
    k = min(1.0, (hy - SILL) / 14, (TOP - hy) / 14)
    for m in MULL:
        d = abs(hx - m) - MW / 2
        if d < 0:
            return 0.0
        k = min(k, d / 10)
    return max(0.0, k)


def _terra(s, t, P):
    x, z = P[0], P[2]
    u, v = (x - XA) % 64, z % 64
    lvl = 2.1 + (hr(int((x - XA) // 64), int(z // 64), 3) - 0.5) * 0.35 + (hr(int(x) // 2, int(z) // 2, 4) - 0.5) * 0.2
    if u < 1.6 or v < 1.6:
        lvl -= 1.2
    elif u < 3.2 or v < 3.2:
        lvl += 0.3
    lvl -= 0.9 * max(0.0, 1 - (ZW - z) / 60)                       # a peu de la paret, a contrallum
    sun = _sol_terra(x, z)
    if sun > 0:
        lvl += 2.0 * sun
    lvl -= 1.0 * max(0.0, 1 - (z - 60) / 220)                     # a prop, a l'ombra (la Vet, el sostre)
    return lvl


def _paret_baixa(s, t, P):
    y = P[1]
    lvl = 3.6 - (SILL - y) * 0.01 + (hr(int(P[0]) // 120, 5) - 0.5) * 0.3
    if int(P[0] - XA) % 120 < 2:
        lvl -= 1.0
    return lvl


def escena(cv):
    """Paret, vidre, rètol, terra, jardineres i la directora (el fons, sense en Cargol). → l'Escena."""
    cv.img.paste(_cel())
    cv.P = cv.img.load()
    cv.S = 1                                                    # (el Canvas d'1× de Ferro-9 no ho diu)
    e = Escena(cv, CAM, LLUMS, ambient=0.0)
    # el sostre i la paret de dalt, per sobre del rètol
    e.quad('sostre', (XA, CEIL, -60), (XB, CEIL, -60), (XB, CEIL, ZW), (XA, CEIL, ZW), ramp=WALLW,
           lvl=lambda s, t, P: 2.4 + (0.6 if (P[2] % 140) < 6 else 0) - 0.4 * (P[2] < 200))
    e.quad('paret', (XA, CEIL, ZW), (XB, CEIL, ZW), (XB, SIGN1, ZW), (XA, SIGN1, ZW), ramp=WALLW,
           lvl=lambda s, t, P: 3.4 - (CEIL - P[1]) * 0.004)
    # el rètol: la textura de cara, i a la dreta el panell llis
    x1 = SIGN_X + 640
    e.quad('retol', (SIGN_X, SIGN1, ZW - 2), (x1, SIGN1, ZW - 2), (x1, SIGN0, ZW - 2), (SIGN_X, SIGN0, ZW - 2),
           tex=(_retol(), (0, 0, 640, SIGN1 - SIGN0)))
    for xa, xb in ((XA, SIGN_X), (x1, XB)):
        e.quad('retol_panell', (xa, SIGN1, ZW - 2), (xb, SIGN1, ZW - 2), (xb, SIGN0, ZW - 2), (xa, SIGN0, ZW - 2),
               ramp=WALLW, lvl=lambda s, t, P: 7.0 if P[1] > SIGN1 - 1.2 else 5.2 if P[1] > SIGN0 + 2 else 2.4)
    # la paret de sota l'ampit, amb la ratlla menta
    e.quad('paret_baixa', (XA, SILL, ZW), (XB, SILL, ZW), (XB, 0, ZW), (XA, 0, ZW), ramp=WALLW, lvl=_paret_baixa)
    e.quad('socol', (XA, 9, ZW - 1), (XB, 9, ZW - 1), (XB, 6, ZW - 1), (XA, 6, ZW - 1), ramp=MINT, lvl=4.0)
    # el vidre: un tel clar i reflexos en diagonal, damunt del cel
    e.claror((XA, TOP, ZW), (XB, TOP, ZW), (XB, SILL, ZW), (XA, SILL, ZW), (200, 230, 255),
             lambda s, t: 0.12 if ((s * 0.7 + t) % 260) < 34 else 0.04)
    # el terra
    e.quad('terra', (XA, 0, ZW), (XB, 0, ZW), (XB, 0, -40), (XA, 0, -40), ramp=DECK, lvl=_terra)
    # l'ampit (un caire que sobresurt) i el travesser de dalt
    e.caixa('ampit', XA, XB, SILL - 4, SILL, ZW - 16, ZW, WALLW, 4.0,
            cares={'dalt': {'ramp': WALLW, 'lvl': 6.4}, 'davant': {'ramp': WALLW, 'lvl': 3.4}})
    e.caixa('travesser', XA, XB, TOP - 6, TOP, ZW - 12, ZW, WALLW, 3.0,
            cares={'sota': {'ramp': WALLW, 'lvl': 2.2}, 'davant': {'ramp': WALLW, 'lvl': 3.2}})
    # els muntants: tres cares (el costat de l'esquerra, de cara al sol, encès)
    for m in MULL:
        e.caixa('muntant', m - MW / 2, m + MW / 2, 0, SIGN0, ZW - MD, ZW, WALLW, 3.0,
                cares={'davant': {'ramp': WALLW, 'lvl': lambda s, t, P: 3.4 - (0.8 if s > MW - 3 else 0)},
                       'esquerra': {'ramp': WALLW, 'lvl': 5.6}, 'dreta': {'ramp': WALLW, 'lvl': 2.2}})
    # les jardineres: la caixa i, al darrere, el pla de les plantes
    for (xa, xb, seed) in ((-140, 340, 4), (420, 1100, 6)):
        img = _jardinera(seed, int(xb - xa))
        e.quad('plantes', (xa, SILL + 70, ZW - 26), (xb, SILL + 70, ZW - 26), (xb, SILL - 20, ZW - 26),
               (xa, SILL - 20, ZW - 26), tex=(img, (0, 0, img.width, 90)))
        e.caixa('jardinera', xa, xb, 0, 22, ZW - 44, ZW - 16, WALLW, 3.6,
                cares={'dalt': {'ramp': POT, 'lvl': lambda s, t, P: 1.0 + (0.6 if hr(int(s), int(t), 2) > 0.6 else 0)},
                       'davant': {'ramp': WALLW, 'lvl': lambda s, t, P: 4.4 - t * 0.08 - (1.0 if abs(t - 9) < 1 else 0)},
                       'esquerra': {'ramp': WALLW, 'lvl': 5.4}, 'dreta': {'ramp': WALLW, 'lvl': 2.4}})
    # la foscor a peu de la paret i als racons del sostre
    e.foscor('ombra', (XA, 0.3, ZW - 16), (XB, 0.3, ZW - 16), (XB, 0.3, ZW - 110), (XA, 0.3, ZW - 110),
             lambda s, t: 0.35 * (1 - t / 94))
    # el pilar 7, a tocar de la càmera a l'esquerra: fosc, tallat per la vora
    e.caixa('pilar', PILAR[0] - 22, PILAR[0] + 22, 0, CEIL, PILAR[1] - 22, PILAR[1] + 22, PILARR, 1.4,
            cares={'davant': {'ramp': PILARR, 'lvl': lambda s, t, P: 1.6 + (0.6 if abs(P[1] - 120) < 6 else 0)
                              + (hr(int(s) // 3, int(t) // 5, 7) - 0.5) * 0.4},
                   'dreta': {'ramp': PILARR, 'lvl': lambda s, t, P: 0.8 + (hr(int(s) // 3, int(t) // 5, 8) - 0.5) * 0.4}})
    # la directora jove, al fons a la dreta, que s'ho mira
    dx, dz = DIRECTORA
    e.foscor('ombra', (dx - 14, 0.3, dz + 4), (dx + 14, 0.3, dz + 4), (dx + 50, 0.3, dz - 60), (dx + 22, 0.3, dz - 60),
             lambda s, t: 0.45 * (1 - t / 64))
    e.sprite('directora', _person('DIRECTORA_JOVE', 'L'), (34, 111), (dx, 0, dz))
    return e


def _haze(img, k=0.13):
    """La boirina del desenfocament: tot el fons una mica cap a HAZE."""
    A = np.asarray(img).astype(float)
    A[..., :3] += (np.array(HAZE, float) - A[..., :3]) * k
    return Image.fromarray(A.clip(0, 255).astype(np.uint8), 'RGBA').copy()


def _ombra_robot(e):
    """L'ombra llarga d'en Cargol, cap a nosaltres i cap a la dreta (el sol és darrere el vidre, a l'esquerra)."""
    x, z = ROBOT
    L = 78 * math.hypot(SUN[0], SUN[2]) / SUN[1]                  # la llargada: l'alçada × cotangent del sol
    ux, uz = -SUN[0] / math.hypot(SUN[0], SUN[2]), -SUN[2] / math.hypot(SUN[0], SUN[2])
    px, pz = -uz, ux                                              # de través
    w = 34
    e.foscor('ombra', (x - px * w + ux * L, 0.4, z - pz * w + uz * L), (x + px * w + ux * L, 0.4, z + pz * w + uz * L),
             (x + px * w, 0.4, z + pz * w), (x - px * w, 0.4, z - pz * w),
             lambda s, t: 0.55 * min(1.0, t / 8) * (0.55 + 0.45 * t / L) * min(1.0, s / 10, (2 * w - s) / 10))
    e.foscor('ombra', (x - 50, 0.4, z + 26), (x + 50, 0.4, z + 26), (x + 50, 0.4, z - 26), (x - 50, 0.4, z - 26),
             lambda s, t: 0.7 * max(0.0, 1 - math.hypot((s - 50) / 50, (t - 26) / 26)) * 1.4)


@lru_cache(maxsize=None)
def _fons():
    """El fons quiet: l'escena, la boirina i l'ombra d'en Cargol."""
    cv = Canvas(light=LIGHT)
    e = escena(cv)
    cv.img = _haze(cv.img)
    cv.P = cv.img.load()
    e.cv = cv
    _ombra_robot(e)
    return cv.img


# ─── Els raigs de sol a l'aire ───────────────────────────────────────────────

@lru_cache(maxsize=None)
def _raigs_mascara():
    """Per a cada vidre (entre dos muntants), el volum del raig projectat: (alfa base, H×W)."""
    out = []
    for a, b in zip(MULL, MULL[1:]):
        xa, xb = a + MW / 2 + 4, b - MW / 2 - 4
        pts = []
        for x in (xa, xb):
            for y in (SILL + 4, TOP - 4):
                P = (x, y, ZW - 1)
                t = y / SUN[1]                                     # fins al terra, en sentit contrari al sol
                Q = (x - SUN[0] * t, 0, ZW - 1 - SUN[2] * t)
                for R in (P, Q):
                    u, v, _ = CAM.projecta(R)
                    pts.append((u, v))
        # l'envolupant convexa
        pts = sorted(set(pts))

        def cross(o, a_, b_):
            return (a_[0] - o[0]) * (b_[1] - o[1]) - (a_[1] - o[1]) * (b_[0] - o[0])
        lo, hi = [], []
        for p in pts:
            while len(lo) >= 2 and cross(lo[-2], lo[-1], p) <= 0:
                lo.pop()
            lo.append(p)
        for p in reversed(pts):
            while len(hi) >= 2 and cross(hi[-2], hi[-1], p) <= 0:
                hi.pop()
            hi.append(p)
        hull = lo[:-1] + hi[:-1]
        m = Image.new('L', (W, H), 0)
        ImageDraw.Draw(m).polygon(hull, fill=255)
        out.append(np.asarray(m, float) / 255)
    return out


def _raigs(img, T):
    A = np.asarray(img).astype(float)
    yy = np.arange(H, dtype=float)[:, None]
    a = np.zeros((H, W))
    for j, m in enumerate(_raigs_mascara()):
        pulse = 1 + 0.5 * math.sin(2 * math.pi * (T * (1 + j % 2)) + j * 1.7)
        a += m * 0.06 * pulse * np.clip((yy - 150) / 160, 0, 1) ** 1.5
    a = np.minimum(a, 0.3)
    A[..., :3] += (np.array((255, 228, 170), float) - A[..., :3]) * a[..., None]
    return Image.fromarray(A.clip(0, 255).astype(np.uint8), 'RGBA').copy()


# ─── En Cargol, la carta, la mà ─────────────────────────────────────────────

def _cargol_pt(ix, iy):
    """Un punt del fotograma de cargol_gran → píxel de la pantalla (on cau, ja posat a l'escena)."""
    x, z = ROBOT
    u, v, _ = CAM.projecta((x, 0, z))
    k = CAM.escala((x, 0, z)) / CARGOL_S
    return u + (ix - ROBOT_FEET[0]) * k, v + (iy - ROBOT_FEET[1]) * k, k


def bg(cv, t=0.0):
    T = t % 1
    img = _raigs(_fons(), T)
    cv.img.paste(img)
    cv.P = cv.img.load()
    # la carta, a la pinça (la pinça, que es pinta després, l'agafa per la cantonada)
    wx, wy, k = _cargol_pt(57.5 * CARGOL_S * 4 / 3, 37.5 * CARGOL_S * 4 / 3)
    flutter = 1 if math.sin(2 * math.pi * 3 * T) > 0.8 else 0
    lw, lh = round(45 * 0.9), round(32 * 0.9)
    letter(cv, int(wx + 14 * k), int(wy - 14 * k) + flutter, w=lw, h=lh)
    # en Cargol (parpelleja un cop per bucle)
    blink = 2 if 0.555 <= T < 0.6 else (1 if 0.49 <= T < 0.68 else 0)
    cv.S = 1
    e = Escena(cv, CAM, LLUMS)
    x, z = ROBOT
    e.sprite('cargol', cargol_gran(blink), ROBOT_FEET, (x, 0, z), escala_img=1 / CARGOL_S)
    # el sol, de contrallum: una vora de llum a l'esquerra d'en Cargol
    _vora(cv, 'cargol', e)
    # la llum càlida dels ulls i la de la carta
    ex, ey, _ = _cargol_pt(27 * CARGOL_S * 4 / 3, 33.4 * CARGOL_S * 4 / 3)
    cv.glow(ex, ey, 28, (255, 210, 120), 0.18)
    cv.glow(wx + 30 * k + 14, wy - 2, 34, (255, 236, 190), 0.25)
    breath = math.sin(math.pi * T) ** 2
    if breath > 0.02:
        for ax, ay in ((17.0, 9.5), (35.9, 8.5)):
            gx, gy, _ = _cargol_pt(ax * CARGOL_S * 4 / 3, ay * CARGOL_S * 4 / 3)
            cv.glow(gx, gy, 13, (255, 214, 110), 0.45 * breath)
    # la mà de la Vet, a tocar de la càmera
    hand = vet_hand()
    hx, hy = int(wx + 14 * k + lw + 30 - 50), int(wy - 14 * k + 8 - 66)
    cv.img.alpha_composite(hand, (hx, hy))
    cv.P = cv.img.load()
    # pols que brilla als raigs de sol, al voltant de la carta
    rnd = random.Random(17)
    mv = random.Random(18)
    for _ in range(60):
        x_, y_ = rnd.gauss(wx + 40, 90), rnd.gauss(wy - 40, 70)
        ph1, ph2, m = mv.uniform(0, 6.3), mv.uniform(0, 6.3), mv.choice((1, 2, 3))
        x_ += 4 * (math.sin(2 * math.pi * T + ph1) - math.sin(ph1))
        y_ += 7 * (math.cos(2 * math.pi * T + ph2) - math.cos(ph2))
        if 0 <= x_ < W and 0 <= y_ < H:
            b = rnd.random()
            tw = 1 - 0.8 * math.sin(math.pi * m * T) ** 2
            cv.flat(x_, y_, mix(cv.get(x_, y_), (255, 240, 200), (0.5 + b * 0.5) * tw))
            if b > 0.85:
                cv.glow(x_, y_, 5, (255, 230, 170), 0.5)
    _vinyeta(cv)


def _vora(cv, sid, e):
    """El contrallum: els píxels de la vora de l'esquerra i de dalt de la figura, més clars i càlids."""
    idx = e.ids.index(sid)
    amo, P = e.amo, cv.P
    for y in range(1, H):
        for x in range(1, W):
            if amo[y * W + x] == idx and (amo[y * W + x - 1] != idx or amo[(y - 1) * W + x] != idx):
                if amo[y * W + x - 1] != idx and x > 0:
                    P[x, y] = mix(P[x, y], (255, 226, 170), 0.45) + (255,)
                else:
                    P[x, y] = mix(P[x, y], (255, 226, 170), 0.25) + (255,)


def _vinyeta(cv):
    A = np.asarray(cv.img).astype(float)
    yy, xx = np.mgrid[0:H, 0:W].astype(float)
    a = np.maximum(0.0, np.hypot((xx - 330) / 380, (yy - 180) / 230) - 0.72) * 1.2
    A[..., :3] *= np.clip(1 - a, 0, 1)[..., None]
    cv.img.paste(Image.fromarray(A.clip(0, 255).astype(np.uint8), 'RGBA'))
    cv.P = cv.img.load()


PROPS = {}


@lru_cache(maxsize=None)
def _base():
    cv = Canvas(light=LIGHT)
    bg(cv)
    return cv.img


def _ambient_frames(n=16):
    """Fotogrames de l'animació de fons: només els píxels que canvien respecte del fons quiet."""
    B = np.asarray(_base())
    frames = []
    for i in range(n):
        cv = Canvas(light=LIGHT)
        bg(cv, t=i / n)
        A = np.array(cv.img)
        A[~(A[..., :3] != B[..., :3]).any(axis=2)] = 0
        frames.append(Image.fromarray(A, 'RGBA'))
    return frames


ANIMS = {'ambient': {'frames': _ambient_frames, 'frameDuration': 110}}
