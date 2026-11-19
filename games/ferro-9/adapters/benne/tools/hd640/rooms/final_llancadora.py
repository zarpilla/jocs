"""
Final · La fugida (i el de l'Estació d'Orís): la llançadora vella travessa la nit. EN 3D (hd640/tres_d.py), a 1×;
el dibuix pla d'abans és a final_llancadora_pla_comu.py (en surten la Terra de nit, el sol i les rampes).

Un pla de cinema, com la referència del vaixell i la plataforma (docs/referencies/cinematica-vaixell-plataforma.png):
  - la llançadora, grossa i a prop, a baix a la dreta, en 3/4: ve cap a nosaltres de biaix, amb el morro de coure
    girat cap a la dreta. Se'n veu el costat (la finestreta amb la Vet i la llum de la cabina, la porta, el tub de
    ferro-9 nou al ventre, el rètol «L-1»), el llom i les tres aletes de la cua. És un cos de revolució de facetes
    (`nau`), amb les planxes, els reblons, els pedaços i el rovell en coordenades de la nau: s'empetiteixen cap a la
    cua. La il·lumina el sol per darrere (el contorn del llom, encès) i la Terra per sota (blava);
  - La Gavina, petita i lluny, a dalt a l'esquerra, també girada (un pla del món amb el dibuix de sempre), just
    damunt de la vora de la Terra on surt el sol: hi queda a contrallum;
  - l'estela blava, del motor fins a La Gavina: s'aprima i s'esvaeix amb la distància, i porta l'ull de la nau a
    l'estació que deixen enrere;
  - la Terra de nit (les ciutats enceses) ocupa el cantó de baix a l'esquerra, amb la vora inclinada.
El quadre del text del narrador va al mig (≈145..495 × 140..240): la nau i l'estació en queden fora.

`nau(e, ...)` es fa servir també a final_estacio (la llançadora aterrada al moll).
Pantalla sencera (sense barra de verbs). Animació: `ambient` (les estrelles i les ciutats, el sol, la flama i
l'estela que bateguen, els llums de La Gavina).
"""
import hd640  # noqa: F401  (abans que cap hd.rooms: posa la llibreria a 640×360)

import math
import random
from functools import lru_cache

import numpy as np
from PIL import Image

from hd.pix import Canvas, Light, B4, W, H, hr, mix, COPPER, RUST, TEAL, PAPER
import hd640.rooms.final_llancadora_pla_comu as pla
from hd640.rooms.proleg_gavina_pla_comu import espai, gavina, vinyeta
from hd.rooms.fabrica_moll import OLDHULL, F9
from hd640.tres_d import Camera, Escena, Llum, _cross, _norm, _sub, _dot

LIGHT = Light(ambient=0.0, vignette=None, floor_fade=None)
CABIN, FLAME = pla.CABIN, pla.FLAME
TAU = 2 * math.pi

# ─── La Terra (el casquet de nit, a baix a l'esquerra, amb la vora inclinada) ─
# (el dibuix pla la calcula amb aquests valors del mòdul: es posen abans de dibuixar-la)
pla.EX, pla.EY, pla.ER = 40, 930, 720
pla.SX = 128                                       # el sol surt per la vora, sota La Gavina
_s = (0.15, 0.40, -0.90)
_l = math.sqrt(sum(c * c for c in _s))
pla.SUN = tuple(c / _l for c in _s)

# ─── La càmera i el món ─────────────────────────────────────────────────────
CAM = Camera(pos=(0.0, 0.0, 0.0), yaw=0.0, pitch=0.0, f=420, centre=(320, 170))
NOSE = (150.0, -66.0, 238.0)                       # el morro de la llançadora
_d = (0.70, -0.06, -0.71)
_l = math.sqrt(sum(c * c for c in _d))
AXIS = tuple(c / _l for c in _d)                   # de la cua cap al morro
ROLL = 0.18                                        # (la nau, una mica escorada: es veu més el llom)
GAV = (-4300.0, 1250.0, 9000.0)                    # La Gavina, el centre
GAV_W = 2300.0                                     # l'envergadura al món
GAV_YAW = 0.62                                     # girada: l'ala dreta fuig
SUNW = (-30000.0, 9000.0, 90000.0)                 # el sol, darrere La Gavina

LEN, RAD = 200.0, 25.0


# ─── La llançadora en 3D ────────────────────────────────────────────────────

def radi(u, L=LEN, R=RAD):
    """El perfil (el mateix del dibuix pla): el morro arrodonit i la popa que s'estreny."""
    s = u / L
    if s < 0.24:
        return R * math.sqrt(max(0.0, 1 - ((0.24 - s) / 0.24) ** 2)) ** 0.9
    if s > 0.86:
        return R * (1 - (s - 0.86) / 0.14 * 0.3)
    return R


class Nau:
    """La llançadora: el morro a `nose`, l'eix `axis` (cua → morro), escorada `roll` radiants. Coordenades de la nau:
    u (des del morro cap a la cua), φ (al voltant: 0 = el costat del dibuix pla, π/2 = el ventre) i r."""

    def __init__(self, nose, axis, roll=0.0, L=LEN, R=RAD, espill=False, k=1.0):
        self.N, self.d, self.L, self.R, self.espill, self.k = nose, axis, L, R, espill, k
        up = (0.0, 1.0, 0.0)
        side = _norm(_cross(up, axis))                   # el costat del dibuix pla (el morro a la dreta)
        upp = _norm(_cross(axis, side))
        if espill:                                       # (o el de l'altra banda: el dibuix, a l'inrevés)
            side = (-side[0], -side[1], -side[2])
        c, s = math.cos(roll), math.sin(roll)
        self.side = tuple(side[i] * c + upp[i] * s for i in range(3))
        self.up = tuple(upp[i] * c - side[i] * s for i in range(3))

    def p(self, u, phi, r=None):
        r = (radi(u, self.L, self.R) if r is None else r) * self.k
        cp, sp = math.cos(phi), math.sin(phi)
        return tuple(self.N[i] - self.d[i] * u * self.k + r * (cp * self.side[i] - sp * self.up[i]) for i in range(3))

    def eix(self, u):
        return tuple(self.N[i] - self.d[i] * u * self.k for i in range(3))


_RNG = random.Random(9)
PATCHES = [(_RNG.uniform(0.28, 0.8) * LEN, _RNG.uniform(-2.6, 2.6), _RNG.randint(8, 15), _RNG.uniform(0.25, 0.4))
           for _ in range(9)]                            # pedaços: u, φ, llarg, ample (en radiants)


def _casc(u, phi, r):
    """El nivell del casc (sense la llum del món) i la rampa: planxes, reblons, pedaços, rovell, morro de coure."""
    s = u / LEN
    arc = phi * RAD
    lvl = 3.2 + (hr(int(u) // 23, int(phi * 4) + 9, 11) - 0.5) * 0.5 + (hr(int(u) // 4, int(arc) // 3, 12) - 0.5) * 0.35
    rmp = OLDHULL
    if s > 0.2:
        if u % 23 < 1.1:
            lvl -= 1.3
            if round(arc) % 5 == 0:
                lvl += 2.6                                # els reblons
        elif u % 23 < 2.2:
            lvl += 0.4
        if (phi * 4 / math.pi) % 1 < 0.05:
            lvl -= 0.9                                    # les juntes de llarg
    for pu, pp, pl, pw in PATCHES:
        if pu <= u <= pu + pl and abs(phi - pp) < pw / 2:
            lvl += 0.5
            if u - pu < 1 or pu + pl - u < 1 or abs(abs(phi - pp) - pw / 2) < 0.04:
                lvl -= 1.3
    rr = hr(int(u), 31)
    if rr > 0.92 and 0.2 < s < 0.85 and math.sin(phi) > -0.2 + hr(int(u), 32) * 0.5:
        rmp, lvl = RUST, 1.8 + (hr(int(u), int(arc), 34) - 0.5) * 1.0       # regalims de rovell
    if s < 0.06:
        rmp, lvl = COPPER, 3.0 + math.cos(phi + 0.6) * 0.6
        if hr(int(u) // 2, int(arc) // 3, 4) > 0.9 and hr(int(u), int(arc), 5) > 0.35:
            rmp, lvl = TEAL, 2.2 + hr(int(u), int(arc), 6)
    if 0.86 < s < 0.885:
        rmp, lvl = COPPER, 2.8 + (0.8 if s < 0.865 else 0)
    return rmp, lvl


@lru_cache(maxsize=None)
def _decals(retol=True, vet=True):
    """El costat del dibuix pla, sense el casc: la finestreta amb la Vet, la porta, el pany, el tub de ferro-9 i el
    rètol (la nau de pla, horitzontal, amb el morro a (NX, NY))."""
    nx0, ny0, ang0 = pla.NX, pla.NY, pla.ANG
    pla.NX, pla.NY, pla.ANG = 300, 120, 0.0
    cv = Canvas(transparent=True)
    pla.llancadora(cv)
    pla.NX, pla.NY, pla.ANG = nx0, ny0, ang0
    if not vet:                                             # (la Vet ja n'ha baixat: la cabina, buida)
        cv.disc(267, 113, 8.3, 8.3, CABIN, lambda nx, ny: 3.2 - ny * 1.8 - math.hypot(nx - 0.3, ny + 0.4) * 1.2, 0)
        for k in range(4):
            cv.flat(261 + k, 111 - k, (255, 236, 200) if k not in (1, 2) else (255, 250, 230))
    a = np.array(cv.img)
    keep = np.zeros(a.shape[:2], bool)
    NX, NY = 300, 120
    boxes = ((20, 46, -20, 6), (54, 96, -22, 23), (94, 174, 13, 24)) + (((115, 133, -19, -10),) if retol else ())
    for (u0, u1, v0, v1) in boxes:
        keep[NY + v0:NY + v1 + 1, NX - u1:NX - u0 + 1] = True
    a[~keep] = 0
    return a, NX, NY


TW = int(TAU * RAD) + 2                                     # la textura desplegada: x = (φ + π)·RAD, y = u


@lru_cache(maxsize=None)
def textura(retol=True, vet=True):
    """El casc desplegat (procedural, en coordenades de la nau) amb les calcomanies del costat del dibuix pla."""
    img = Image.new('RGBA', (TW, int(LEN) + 2), (0, 0, 0, 0))
    P = img.load()
    dec, NX, NY = _decals(retol, vet)
    for u in range(int(LEN) + 2):
        r = radi(min(u + 0.5, LEN))
        for x in range(TW):
            phi = x / RAD - math.pi
            rmp, lvl = _casc(u + 0.5, phi, r)
            col = rmp[max(0, min(len(rmp) - 1, math.floor(lvl + B4[u & 3][x & 3] - 0.5)))]
            if abs(phi) < math.pi / 2:
                v = r * math.sin(phi)
                c = dec[int(round(NY + v)), NX - u]
                if c[3] > 128:
                    col = tuple(int(q) for q in c[:3])
            P[x, u] = col + (255,)
    return img


def nau(e, nv, sid='nau', M=32, cua=True, ombra_cilindre=0.22, vet=True):
    """Dibuixa la llançadora `nv` (una Nau) a l'Escena `e`: el casc de facetes amb la textura desplegada, la tapa de
    popa, la tobera i les tres aletes."""
    L = nv.L
    us = [0.02, 0.6, 1.5, 3, 5, 8, 11.5, 15.5, 20, 25, 30, 36, 42, 48] + \
        [48 + k * (172 - 48) / 12 for k in range(1, 13)] + [180, 190, L]
    tex = textura(not nv.espill, vet)
    dphi = TAU / M
    for i in range(len(us) - 1):
        ua, ub = us[i], us[i + 1]
        for j in range(M):
            pa = -math.pi + j * dphi
            pb = pa + dphi
            k = max(0.0, min(0.7, ombra_cilindre + 0.32 * math.sin(pa + dphi / 2)))   # el volum del cilindre
            if nv.espill:                                  # (el sistema de la nau és a l'inrevés: es giren els cantons)
                e.quad(sid, nv.p(ua, pb), nv.p(ua, pa), nv.p(ub, pa), nv.p(ub, pb),
                       tex=(tex, ((pb + math.pi) * RAD, ua, (pa + math.pi) * RAD, ub)), ombra=lambda s, t, k=k: k)
            else:
                e.quad(sid, nv.p(ua, pa), nv.p(ua, pb), nv.p(ub, pb), nv.p(ub, pa),
                       tex=(tex, ((pa + math.pi) * RAD, ua, (pb + math.pi) * RAD, ub)), ombra=lambda s, t, k=k: k)
    # la tapa de popa (un disc fosc) i la tobera
    rc = radi(L, L, nv.R)
    for j in range(M):
        pa = -math.pi + j * dphi
        e.quad(sid, nv.eix(L), nv.eix(L), nv.p(L, pa + dphi, rc), nv.p(L, pa, rc), ramp=OLDHULL, lvl=1.4,
               dues_cares=True)
    if cua:
        A, B = nv.eix(L - 2), nv.eix(L + 13)
        e.tub(sid, A, B, 8.0 * nv.k, OLDHULL, 1.6, llum_dir=(-0.6, -1.0))
    # les tres aletes: dalt i les dues de sota, a 120°
    for phi in (-math.pi / 2, math.pi / 6, 5 * math.pi / 6):
        r0 = radi(L - 43, L, nv.R) - 1
        P0 = nv.p(L - 45, phi, r0)
        P1 = nv.p(L + 3, phi, r0)
        P3 = nv.p(L - 45, phi, r0 + 23)
        P2 = nv.p(L + 3, phi, r0 + 23)

        def forma(s, t, k=nv.k):
            s, t = s / k, t / k
            return s >= t * 1.6 and s <= 48 - t * 0.25

        def lvl_a(s, t, Pw, k=nv.k):
            s, t = s / k, t / k
            v = 3.2 + (hr(int(s) // 4, int(t) // 3, 8) - 0.5) * 0.5
            if t > 21:
                v = 2.6                                   # la vora de coure
            if abs(s - t * 1.6) < 1.2:
                v += 1.4                                  # el cantell d'atac
            return v
        e.quad(sid + '_aleta', P0, P1, P2, P3, ramp=OLDHULL, lvl=lvl_a, forma=forma, dues_cares=True)


# ─── El món: els llums ──────────────────────────────────────────────────────

LLUMS = [Llum(SUNW, 1e7, 7.0, power=1.0),                       # el sol, darrere: el contorn
         Llum((200.0, -6000.0, 900.0), 1e5, 2.6, power=1.0)]     # la Terra, per sota
AMBIENT = -4.0


def _nau_obj():
    return Nau(NOSE, AXIS, ROLL)


@lru_cache(maxsize=None)
def _nau_capa():
    """La llançadora sola (RGBA) i qui ha pintat cada píxel."""
    cv = Canvas(transparent=True)
    cv.S = 1
    e = Escena(cv, CAM, LLUMS, ambient=AMBIENT)
    nv = _nau_obj()
    nau(e, nv)
    # la Terra, blava, per sota; el sol, càlid, al contorn de dalt (es mira cap a on mira cada píxel en pantalla)
    a = np.array(cv.img).astype(np.int32)
    m = a[..., 3] > 0
    up = np.zeros_like(m)
    up[1:] = m[:-1]
    top = m & ~up                                                 # el contorn de dalt
    lf = np.zeros_like(m)
    lf[:, 1:] = m[:, :-1]
    left = m & ~lf
    ys = np.arange(H)[:, None]
    blue = np.clip((ys - 200) / 120.0, 0, 1) * 0.22
    rgb = a[..., :3].astype(np.float64)
    rgb = rgb + (np.array((70, 120, 220)) - rgb) * (blue[..., None] * m[..., None])
    for mk, k in ((top, 0.6), (left, 0.35)):
        rgb[mk] = rgb[mk] + (np.array((255, 214, 170)) - rgb[mk]) * k
    a[..., :3] = np.clip(rgb, 0, 255)
    img = Image.fromarray(a.astype(np.uint8), 'RGBA')
    return img, e


def _proj(P):
    u, v, _ = CAM.projecta(P)
    return u, v


def finestra_xy():
    nv = _nau_obj()
    return _proj(nv.p(33, -0.28))


# ─── La Gavina ──────────────────────────────────────────────────────────────

@lru_cache(maxsize=32)
def _gavina_tex(t=0.0):
    cv = Canvas(transparent=True)
    gavina(cv, 320, 180, 0.62, t=t)
    box = cv.img.getbbox()
    return cv.img, box


def gavina_3d(cv, t=0.0):
    """La Gavina, un pla del món girat GAV_YAW: el dibuix de sempre, en escorç."""
    img, (x0, y0, x1, y1) = _gavina_tex(t)
    w, h = x1 - x0, y1 - y0
    hw, hh = GAV_W / 2, GAV_W * h / w / 2
    c, s = math.cos(GAV_YAW), math.sin(GAV_YAW)
    gx, gy, gz = GAV

    def P(lx, ly):
        return (gx + lx * c, gy + ly, gz + lx * s)
    e = Escena(cv, CAM, [], ambient=0.0)
    e.quad('gavina', P(-hw, hh), P(hw, hh), P(hw, -hh), P(-hw, -hh), tex=(img, (x0, y0, x1, y1)), dues_cares=True)


# ─── L'estela i la flama ────────────────────────────────────────────────────

def _blend(cv, x, y, col, a):
    x, y = int(round(x)), int(round(y))
    if 0 <= x < W and 0 <= y < H and a > 0.01:
        cv.flat(x, y, mix(cv.get(x, y), col, min(1.0, a)))


def estela(cv, t=0.0):
    """L'estela, de la popa fins a La Gavina: surt seguint l'eix de la nau i es corba cap a l'estació (una corba de
    Bézier al món); més ampla i més viva a prop, i s'esvaeix de lluny."""
    nv = _nau_obj()
    A = nv.eix(LEN + 30)
    C = nv.eix(LEN + 900)
    B = (GAV[0] + 250, GAV[1] - 330, GAV[2])
    n = 1400
    for i in range(n):
        k = i / n                                                 # 0 a la nau, 1 a l'estació
        q = k ** 2.0                                              # (es reparteix per la pantalla, no pel món)
        P = tuple((1 - q) ** 2 * A[j] + 2 * (1 - q) * q * C[j] + q * q * B[j] for j in range(3))
        u, v, z = CAM.projecta(P)
        r = max(0.6, 6.0 * CAM.f / z)
        pulse = 0.8 + 0.2 * math.sin(TAU * (2 * t - k * 3))
        a = (1 - k * 0.85) ** 1.2 * 0.5 * pulse
        if hr(i, 3) > 0.97 - k * 0.5:
            continue
        for dy in range(-int(r), int(r) + 1):
            f = 1 - abs(dy) / (r + 0.5)
            _blend(cv, u, v + dy, (110, 170, 240) if f < 0.6 else (170, 210, 255), a * f)


def flama(cv, t=0.0):
    """El plomall blau del motor: s'allunya de nosaltres i s'aprima; amb diamants de xoc que corren."""
    nv = _nau_obj()
    FL = 240
    for k in range(FL, -1, -1):                                   # del lluny al prop
        q = k / FL
        P = nv.eix(LEN + 12 + k)
        u, v, z = CAM.projecta(P)
        sc = CAM.f / z
        half = (9.0 * (1 - q) ** 0.7 + 1.4 * math.sin(q * 9 - TAU * 2 * t) * (1 - q)) * (1 + 0.08 * math.sin(TAU * 3 * t))
        R = max(0.8, half * sc)
        core = 0.9 * max(0.0, math.cos(q * 30 - TAU * 4 * t)) * (1 - q)
        for yy in range(int(v - R - 3), int(v + R + 4)):
            for xx in range(int(u - R - 3), int(u + R + 4)):
                d = math.hypot(xx - u, yy - v)
                if d > R + 3:
                    continue
                c = max(0.0, 1 - d / R)
                lvl = c * 6.2 * (1 - q) ** 0.8 + (1 - q) * 1.6 + core * c
                if d > R:
                    lvl = (1 - (d - R) / 3) * 1.4 * (1 - q)
                if 0 <= xx < W and 0 <= yy < H and lvl > 0.4 + B4[yy & 3][xx & 3] * 0.6:
                    if lvl > 1.0 or cv.get(xx, yy)[2] < 120:
                        cv.put(xx, yy, FLAME, lvl, 0)
    cx, cy = _proj(nv.eix(LEN + 20))
    cv.glow(int(cx), int(cy), 64, (80, 150, 255), 0.45 + 0.07 * math.sin(TAU * 3 * t))
    cv.glow(int(cx), int(cy), 20, (200, 236, 255), 0.65)


def llums_nau(cv, t=0.0):
    """La llum càlida de la finestreta i el llum de posició de l'aleta de dalt (fa pampallugues)."""
    fx, fy = finestra_xy()
    cv.glow(int(fx), int(fy), 22, (255, 170, 90), 0.35)
    nv = _nau_obj()
    lx, ly = _proj(nv.p(LEN - 2, -math.pi / 2, radi(LEN - 43) + 22))
    on = not (0.40 <= t % 0.5 < 0.47)
    if on:
        cv.flat(int(lx), int(ly), (255, 90, 70))
        cv.flat(int(lx) + 1, int(ly), (220, 50, 46))
        cv.glow(int(lx), int(ly), 9, (255, 70, 60), 0.6)


# ─── Composició ────────────────────────────────────────────────────────────

def scene(cv, t=0.0):
    cv.S = 1
    pla._T = t % 1.0
    espai(cv, seed=21)
    pla.titil(cv)
    pla.terra_nit(cv)
    pla.sol(cv)
    gavina_3d(cv, t)
    estela(cv, t)
    flama(cv, t)
    cv.img.alpha_composite(_nau_capa()[0])
    cv.P = cv.img.load()
    llums_nau(cv, t)
    vinyeta(cv, 0.45)
    pla._T = 0.0


@lru_cache(maxsize=None)
def _base():
    cv = Canvas(light=LIGHT)
    scene(cv)
    return cv.img.copy()


def bg(cv, t=0.0):
    if t:
        scene(cv, t)
        return
    cv.img.paste(_base())
    cv.P = cv.img.load()


PROPS = {}


def _ambient_frames(n=16):
    B = np.asarray(_base())
    frames = []
    for i in range(n):
        cv = Canvas(light=LIGHT)
        scene(cv, t=i / n)
        A = np.array(cv.img)
        A[~(A != B).any(axis=2)] = 0
        frames.append(Image.fromarray(A, 'RGBA'))
    return frames


ANIMS = {'ambient': {'frames': _ambient_frames, 'frameDuration': 110}}
