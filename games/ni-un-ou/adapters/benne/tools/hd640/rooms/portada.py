"""
Ni un ou — la portada (pantalla sencera de 640×360, sense barra de verbs). EN 3D (hd640/tres_d.py), a 1×;
referència: docs/referencies/cinematica-vaixell-plataforma.png.

L'Atlàntic Nord de nit, al Punt 7. Un pla de cinema des de l'aigua, a vuit metres d'alçada:
  - l'**Arenga**, a prop, a l'esquerra i en 3/4 des de popa: el buc gris amb la línia vermella i els ulls de bou
    (el dibuix pla de sempre, projectat), la coberta de popa vista des de dalt, la caseta, el pont, la xemeneia
    amb el cercle de Mar Obert, el pal; la proa apunta a la plataforma. Es gronxa (puja, baixa i escora) amb l'onada;
  - la **grua de popa**, a estribord, amb la zòdiac penjada damunt de l'aigua (la Juana a dins) i en Bastida a la
    borda (capes `zodiac` i `bastida_popa`);
  - la **plataforma**, petita i girada a la dreta, a l'horitzó: les potes en profunditat, el mòdul amb el logotip
    tapat amb cinta americana, la torre amb el llum vermell; els llums de la coberta fan columnes al mar;
  - la **lluna**, a dalt a la dreta, i el seu camí al mar; una **boia** en silueta a primer pla, tallada per la
    vora de baix a la dreta, que fa pampallugues; l'estela curta de l'Arenga surt de baix a l'esquerra cap a la popa.
El mar es calcula al món (onades que s'empetiteixen fins a l'horitzó), i l'Arenga, la plataforma i la boia s'hi
reflecteixen (una segona càmera sota l'aigua, girada).

Els botons de la GUI `portada` van a 220..420 × 224..328 (y de la GUI + 64): allà només hi ha mar.
El títol és la capa `titol` («Comença» l'esvaeix) i el pròleg (proleg_punt7.py) fa servir aquest mateix fons i les
capes d'aquí: la zòdiac que baixa i travessa fins a la plataforma (`z_*`), en Bastida que escriu i la silueta de
la plataforma (`vigia`). Els crèdits (credits.py) en fan servir el mar, el cel i l'Arenga amb una altra càmera.

El món: x a la dreta, y amunt (0 = el mar), z endavant; 1 unitat = 1 metre. La càmera, a l'origen.
"""
import hd640  # noqa: F401  (abans que cap hd.rooms: posa la llibreria a 640×360)

import functools
import json
import math
from pathlib import Path

import numpy as np
from PIL import Image

from hd.pix import Light, Canvas, W, H, hr, mix, B4
from hd.rooms.comu import _diff, text, text_width
from hd.rooms.exterior import (arenga, platform, sheer, NSEA, HULLN, REDH, STEELX, DECKX, GLOW_WARM)
from hd640.rooms.portada_pla_comu import night_sky, title
from hd640.tres_d import Camera, Escena, Llum

LIGHT = Light(ambient=0.0, vignette=None, floor_fade=None)
N = 8                                     # fotogrames del bucle (300 ms): l'onada, el gronxar de l'Arenga


# ─── La càmera i el món ─────────────────────────────────────────────────────

class Pla:
    """Una càmera sobre el mar (sense picat: l'horitzó és a `hor`) i on hi ha cada cosa."""

    def __init__(self, hor, f, h, ship, psi, moon, plat=None, buoy=None):
        self.hor, self.f, self.h = hor, f, h
        self.cam = Camera(pos=(0.0, h, 0.0), yaw=0.0, pitch=0.0, f=f, centre=(320, hor))
        self.mirall = Camera(pos=(0.0, -h, 0.0), yaw=0.0, pitch=0.0, f=f, centre=(320, hor))
        self.ship, self.psi, self.moon, self.plat, self.buoy = ship, psi, moon, plat, buoy

    def p(self, P):
        u, v, _ = self.cam.projecta(P)
        return u, v

    def k(self, P):
        return self.cam.escala(P)


HOR = 165
PLA = Pla(hor=HOR, f=420.0, h=8.0, ship=(-19.0, 44.0), psi=0.52, moon=(592, 62),
          plat=((74.0, 165.0), 0.62), buoy=(17.6, 25.0))
CAM = PLA.cam
TITLE_Y = 21


# ─── Rampes ─────────────────────────────────────────────────────────────────
YELLOW = [(40, 30, 6), (90, 70, 14), (150, 116, 26), (206, 164, 44), (236, 200, 80), (252, 230, 140)]
DECKN = DECKX
SIL = [(2, 3, 6), (4, 6, 10), (7, 10, 16), (11, 15, 22), (16, 21, 30), (24, 30, 40)]
ORANGE = [(40, 12, 6), (84, 26, 10), (140, 48, 16), (196, 80, 26), (232, 118, 44)]
RUBBER = [(10, 10, 12), (18, 18, 22), (30, 30, 36), (46, 46, 52), (66, 66, 72), (90, 90, 94), (118, 118, 120),
          (150, 150, 150)]
LAMPW = (255, 250, 230)
NIGHT_TINT = (0.36, 0.42, 0.58)           # els personatges, de nit: la llum de la lluna i del focus de popa


# ─── El mar (al món, amb numpy) ─────────────────────────────────────────────

def _hash(ix, iy, seed):
    h = (ix.astype(np.int64).astype(np.uint64) * np.uint64(374761393) +
         iy.astype(np.int64).astype(np.uint64) * np.uint64(668265263) + np.uint64(seed * 1442695041 & 0xFFFFFFFF))
    h &= np.uint64(0xFFFFFFFF)
    h = ((h ^ (h >> np.uint64(13))) * np.uint64(1274126177)) & np.uint64(0xFFFFFFFF)
    h ^= h >> np.uint64(16)
    return h.astype(np.float64) / 4294967295.0


def _vn(x, y, seed):
    ix, iy = np.floor(x), np.floor(y)
    fx, fy = x - ix, y - iy
    sx, sy = fx * fx * (3 - 2 * fx), fy * fy * (3 - 2 * fy)
    a, b = _hash(ix, iy, seed), _hash(ix + 1, iy, seed)
    c, d = _hash(ix, iy + 1, seed), _hash(ix + 1, iy + 1, seed)
    return a + (b - a) * sx + (c - a) * sy + (a - b - c + d) * sx * sy


_B4 = np.array(B4)
SWELL = 0.32                              # les crestes, una mica girades: fugen cap a un punt de fuga


def _mon(pla, y0, y1):
    """(X, Z) del mar sota cada píxel de les files y0..y1 (meitat de píxel), i la mida d'un píxel en profunditat."""
    v = np.arange(y0, y1)[:, None] + 0.5
    u = np.arange(W)[None, :] + 0.5
    Z = pla.f * pla.h / np.maximum(v - pla.hor, 0.05)
    X = (u - 320) * Z / pla.f
    return X, np.broadcast_to(Z, X.shape), Z * Z / (pla.f * pla.h)


def mar(pla, phase=0.0, seed=32, calm=1.0, path=(2.4, 0.3), twinkle=0):
    """Els nivells (NSEA) del mar de nit, de l'horitzó a baix → (array de nivells, soroll de les onades, X, Z)."""
    y0 = pla.hor + 1
    X, Z, _ = _mon(pla, y0, H)
    v = np.arange(y0, H)[:, None] + 0.5
    u = np.arange(W)[None, :] + 0.5
    d = (v - pla.hor) + 0 * u
    # Les onades es fan en pantalla, però amb la mida que tindrien al món: l'amplada i el gruix creixen amb la
    # distància a l'horitzó (com més a prop, més grosses) i les crestes es torcen cap a un punt de fuga.
    xs = u + d * math.tan(SWELL) * 0.8
    sx, sy = 3.0 + d * 0.3, 0.6 + d * 0.048
    o1 = _vn((xs + phase * sx * 0.6) / sx, d / sy, seed)
    o2 = _vn((xs * 1.7 - phase * sx * 0.4) / sx, d / (sy * 0.55), seed + 1)
    nn = ((o1 - 0.5) * 0.75 + (o2 - 0.5) * 0.45) / 0.14
    crest = np.clip(1 - np.abs(2 * o2 - 1) * 3.0, 0, 1) ** 2 * (o1 > 0.45)
    far = np.zeros_like(nn)
    lvl = np.broadcast_to(3.9 - np.minimum(0.9, d * 0.006), X.shape).copy()
    lvl += np.clip(nn, -2.2, 2.6) * (0.7 + np.minimum(0.5, d * 0.004)) * calm + np.where(nn > 1.25, 1.1 * calm, 0)
    lvl += crest * 1.6 * calm * np.minimum(1.0, d / 30)
    mx = pla.moon[0]
    m = np.clip(1 - np.abs(u - mx) / ((path[0] + d * path[1]) * 1.33), 0, 1) ** 0.8
    lvl += m * 2.0
    sparkle = _hash(np.floor(u / 2), v, seed + twinkle) > 0.25
    lvl += np.where((nn > 0.4) & sparkle, 4.6 * m, 0)
    # la calitja de l'horitzó
    lvl += np.clip(1 - d / 7, 0, 1) * 0.9
    return lvl, nn, X, Z


def pinta_nivells(cv, lvl, y0, ramp=NSEA):
    """Pinta un array de nivells (files y0..) amb la rampa i el tramat de sempre."""
    h, w = lvl.shape
    ys = (np.arange(y0, y0 + h) & 3)[:, None]
    xs = (np.arange(w) & 3)[None, :]
    idx = np.clip(np.floor(lvl + _B4[ys, xs] - 0.5), 0, len(ramp) - 1).astype(int)
    pal = np.array(ramp, dtype=np.uint8)
    rgb = pal[idx]
    a = np.asarray(cv.img).copy()
    a[y0:y0 + h, :w, :3] = rgb
    a[y0:y0 + h, :w, 3] = 255
    cv.img.paste(Image.fromarray(a, 'RGBA'))
    cv.P = cv.img.load()


# ─── L'Arenga (al món) ──────────────────────────────────────────────────────
# Coordenades de la nau: m de popa (0) a proa (40,8), w cap a estribord, y amunt (0 = la flotació), com el dibuix
# pla de perfil (exterior.arenga, en metres). El costat d'estribord i la caseta en fan servir el dibuix pla.

R = 20                                    # píxels per metre del dibuix pla (la textura)
TS = 2                                    # (es mostreja fent la mitjana de 2×2)
PADX, TOPM, UNDER = 40, 17.0, 0.6


@functools.lru_cache(maxsize=None)
def _perfil():
    cv = Canvas(PADX * 2 + int(41 * R), int((TOPM + UNDER + 1) * R), light=LIGHT, transparent=True)
    arenga(cv, PADX, round(TOPM * R), R, 'night', facing=1, crane=False, zodiac=False, under=UNDER)
    return cv.img


def _tc(m0, y0, m1, y1):
    """El retall del dibuix pla (en unitats de la textura / TS) entre m0..m1 i y0..y1 (metres)."""
    return ((PADX + m0 * R) / TS, (TOPM - y1) * R / TS, (PADX + m1 * R) / TS, (TOPM - y0) * R / TS)


def hb(m):
    """La mitja mànega a l'altura de la borda, a m metres de popa: la popa, una mica més estreta; la proa, afuada."""
    if m < 1.5:
        return 4.0 + 0.3 * m / 1.5
    if m < 23:
        return 4.45
    k = min(1.0, (m - 23) / 17.8)
    return max(0.0, 4.45 * (1 - k ** 1.9))


@functools.lru_cache(maxsize=None)
def _mirall_text():
    """El nom de la popa: «ARENGA», blanc sobre el gris (una textura petita, de 6 px per metre)."""
    k = 6
    cv = Canvas(int(9 * k), int(4 * k), light=LIGHT)
    for y in range(cv.h):
        for x in range(cv.w):
            lvl = 4.6 + (hr(x // 2, y, 81) - 0.5) * 0.3 - (0.5 if y > cv.h - 6 else 0)
            cv.put(x, y, HULLN, lvl, lit=0)
    for x in range(cv.w):                                                # la línia vermella de la borda
        for y in (3, 4):
            cv.put(x, y, REDH, 3.6, lit=0)
        cv.put(x, 0, HULLN, 6.0, lit=0)
    s = 'ARENGA'
    text(cv, s, (cv.w - text_width(s)) // 2, 9, None, 0, flat=(196, 200, 200))
    for i in range(5):                                                   # un regalim de rovell
        x = 10 + int(hr(i, 82) * (cv.w - 20))
        for j in range(3 + int(hr(i, 83) * 6)):
            cv.flat(x, 6 + j, mix(cv.get(x, 6 + j), (110, 60, 36), 0.45))
    return cv.img, k


def ship_T(pla, bob=0.0, roll=0.0, pitch=0.0):
    sx, sz = pla.ship
    s, c = math.sin(pla.psi), math.cos(pla.psi)
    cr, sr = math.cos(roll), math.sin(roll)

    def T(m, w, y):
        w2, y2 = w * cr - y * sr, w * sr + y * cr
        y2 += (m - 20) * pitch + bob
        return (sx + m * s + w2 * c, y2, sz + m * c - w2 * s)
    return T


def _box(e, T, sid, m0, m1, w0, w1, y0, y1, ramp, lvl, cares=None):
    """Una caixa alineada amb la nau: popa (−m), proa (+m), babord (−w), estribord (+w), dalt."""
    F = {
        'proa': ((w1, y1, m1), (w0, y1, m1), (w0, y0, m1), (w1, y0, m1)),
        'babord': ((w0, y1, m1), (w0, y1, m0), (w0, y0, m0), (w0, y0, m1)),
        'estribord': ((w1, y1, m0), (w1, y1, m1), (w1, y0, m1), (w1, y0, m0)),
        'popa': ((w0, y1, m0), (w1, y1, m0), (w1, y0, m0), (w0, y0, m0)),
        'dalt': ((w0, y1, m1), (w1, y1, m1), (w1, y1, m0), (w0, y1, m0)),
    }
    cares = cares or {}
    for nom in ('proa', 'babord', 'estribord', 'popa', 'dalt'):
        pts = [T(m, w, y) for w, y, m in F[nom]]
        e.quad(sid, *pts, **cares.get(nom, {'ramp': ramp, 'lvl': lvl}))


def _sobre_aigua(T, P0, P3):
    """`forma` d'un quad vertical: només el que queda per damunt del mar (la nau es gronxa)."""
    ya, yb = P0[1], P3[1]
    L = math.dist(P0, P3) or 1.0

    def f(s, t):
        return ya + (yb - ya) * t / L >= -0.02
    return f


def _deck_lvl(s, t, P):
    v = 3.0 + (hr(int(P[0] * 2), int(P[2] * 2), 91) - 0.5) * 0.4
    if (t % 1.25) < 0.08:
        v -= 0.8                                       # les juntes de les planxes
    return v


def _caseta_popa(W_, Hh):
    """La cara de popa de la caseta: la porta estanca amb l'ull de bou encès i dos ulls de bou."""
    def f(s, t, P):
        v = 4.2 - t * 0.12 + (hr(int(s * 4), int(t * 4), 92) - 0.5) * 0.25
        dx = s - W_ / 2
        if abs(dx) < 0.48 and t > 0.45:
            v = 2.6 if abs(dx) < 0.4 and t > 0.53 else 4.8                  # la porta
            if abs(dx) < 0.13 and 0.85 < t < 1.12:
                return 8.6                                                  # l'ull de bou de la porta (encès)
        for cx in (W_ / 2 - 1.9, W_ / 2 + 1.9):
            if (s - cx) ** 2 + (t - 1.0) ** 2 < 0.06:
                return 8.4 if cx < W_ / 2 else 2.2
        if abs(dx - 1.1) < 0.35 and abs(t - 1.25) < 0.35 and (s - (W_ / 2 + 1.1)) ** 2 + (t - 1.25) ** 2 > 0.04:
            return 3.4                                                      # un salvavides (fosc, a contrallum)
        return v
    return f


WINR = [(10, 13, 20), (16, 20, 30), (24, 30, 42), (36, 44, 58), (52, 62, 76), (72, 82, 96), (98, 106, 118),
        (130, 136, 144), (190, 140, 60), (240, 200, 110), (255, 236, 180)]          # HULLN amb finestres enceses


def nau(e, T, bastida=None, focus=True):
    """L'Arenga, de lluny a prop per a una càmera a popa i a estribord. `bastida`: (imatge, peu) del sprite que
    va a la borda de popa. → l'Escena (amb `bastida` com a amo dels seus píxels)."""
    img = _perfil()
    # la borda de babord, per dins (es veu per damunt de la coberta)
    ms = [0.4 + i * 1.0 for i in range(41)]
    for m0, m1 in zip(ms, ms[1:]):
        if m1 > 40.3:
            break
        e.quad('nau', T(m1, -hb(m1) + 0.15, sheer(m1)), T(m0, -hb(m0) + 0.15, sheer(m0)),
               T(m0, -hb(m0) + 0.15, sheer(m0) - 0.95), T(m1, -hb(m1) + 0.15, sheer(m1) - 0.95),
               ramp=HULLN, lvl=lambda s, t, P: 3.2 - t * 0.9)
    # la coberta, de proa a popa
    for m0, m1 in reversed(list(zip(ms, ms[1:]))):
        if m1 > 40.3:
            continue
        a0, a1 = hb(m0) - 0.15, hb(m1) - 0.15
        y0d, y1d = sheer(m0) - 0.9, sheer(m1) - 0.9
        e.quad('coberta', T(m1, -a1, y1d), T(m1, a1, y1d), T(m0, a0, y0d), T(m0, -a0, y0d), ramp=DECKN,
               lvl=lambda s, t, P, m1=m1: _deck_lvl(s, (m1 - t), P))
    # el pal de proa
    e.cable('nau', [T(36.5, 0, sheer(36.5) - 0.9), T(36.5, 0, 9.6)], STEELX, 3.6, gruix=0.2)
    # la caseta, el pont i la xemeneia (el costat d'estribord, del dibuix pla)
    sh = sheer(14)
    _box(e, T, 'caseta', 13.0, 31.2, -3.3, 3.3, sh - 0.9, 6.15, HULLN, 4.2, cares={
        'estribord': {'tex': (img, _tc(13.0, sh, 31.2, 6.15), TS)},
        'popa': {'ramp': WINR, 'lvl': _caseta_popa(6.6, 6.15 - sh + 0.9)},
        'dalt': {'ramp': HULLN, 'lvl': lambda s, t, P: 4.8 + (hr(int(s), int(t), 93) - 0.5) * 0.3}})
    _box(e, T, 'pont', 21.0, 31.2, -3.6, 3.6, 6.15, 8.85, HULLN, 4.4, cares={
        'estribord': {'tex': (img, _tc(21.0, 6.15, 31.2, 8.85), TS)},
        'popa': {'ramp': WINR, 'lvl': lambda s, t, P: (8.2 if (s % 1.2 < 0.8 and 0.5 < t < 1.2 and
                                                             hr(int(s / 1.2), 7) > 0.4) else
                                                       2.0 if (s % 1.2 < 0.8 and 0.5 < t < 1.2) else 4.0)},
        'dalt': {'ramp': HULLN, 'lvl': 5.2}})
    # els bots salvavides (cilindres blancs) damunt la caseta, i la barana
    for m in (14.5, 19.8):
        e.tub('nau', T(m, 2.0, 6.55), T(m + 1.4, 2.0, 6.55), 0.4, HULLN, 6.0, llum_dir=(0.6, 1.0))
    e.cable('nau', [T(13.2, 3.2, 7.0), T(20.8, 3.2, 7.0)], HULLN, 4.4, gruix=0.06)
    # el pal: el radar, la creueta i els obencs
    e.cable('nau', [T(27, 0, 8.85), T(27, 0, 16.0)], STEELX, 4.0, gruix=0.24)
    e.cable('nau', [T(27, -1.6, 13.5), T(27, 1.6, 13.5)], STEELX, 4.0, gruix=0.14)
    e.cable('nau', [T(25.6, 0, 11.6), T(28.4, 0, 11.6)], STEELX, 3.6, gruix=0.22)
    for w in (-3.4, 3.4):
        e.cable('nau', [T(27, 0, 15.4), T(27, w, 8.85)], STEELX, 2.6, gruix=0.05)
    _box(e, T, 'xemeneia', 16.2, 19.6, -1.1, 1.1, 6.15, 9.6, HULLN, 4.0, cares={
        'estribord': {'tex': (img, _tc(16.2, 6.15, 19.6, 9.6), TS)},
        'dalt': {'ramp': STEELX, 'lvl': 0.6},
        'popa': {'ramp': HULLN, 'lvl': lambda s, t, P: 1.4 if t < 0.4 else 3.8}})
    # la coberta de popa: el maquinet, l'escotilla
    _box(e, T, 'nau', 9.8, 11.2, -1.2, 1.2, 2.4, 3.3, HULLN, 3.6)
    e.tub('nau', T(10.5, -1.0, 3.6), T(10.5, 1.0, 3.6), 0.35, RUBBER, 3.0, llum_dir=(0.6, 1.0))
    _box(e, T, 'nau', 5.6, 8.0, -1.4, 0.9, 2.4, 2.85, HULLN, 3.4)
    idx = None
    if bastida is not None:
        im, peu_img, scale = bastida
        idx = e.sprite('bastida', im, peu_img, T(4.6, 2.9, 2.4), escala_img=scale)
    # la grua de popa, a estribord, amb el braç (groc) per damunt de l'aigua
    e.tub('nau', T(3.2, 2.8, 2.4), T(3.2, 2.8, 5.8), 0.28, STEELX, 3.4, llum_dir=(0.6, 1.0))
    e.cable('grua', [T(3.2, 2.8, 5.8), T(*CRANE_TIP)], YELLOW, 3.4, gruix=0.32)
    # el costat d'estribord, de proa a popa (el dibuix pla; la proa llançada surt de la textura)
    ms = [0.0] + [0.6 + i * 0.8 for i in range(51)]
    segs = [(a, b) for a, b in zip(ms, ms[1:]) if a < 40.9]
    for m0, m1 in reversed(segs):
        m1 = min(m1, 40.9)
        top = max(sheer(m0), sheer(min(m1, 40.2))) + 0.25
        P0, P1 = T(m0, hb(m0), top), T(m1, hb(m1), top)
        P2, P3 = T(m1, hb(m1), -UNDER), T(m0, hb(m0), -UNDER)
        e.quad('casc', P0, P1, P2, P3, tex=(img, _tc(m0, -UNDER, m1, top), TS), forma=_sobre_aigua(T, P0, P3))
    # el mirall de popa, amb el nom
    tim, k = _mirall_text()
    a = hb(0)
    P0, P1, P2, P3 = T(0, -a, 3.3), T(0, a, 3.3), T(0, a, -UNDER), T(0, -a, -UNDER)
    e.quad('casc', P0, P1, P2, P3, tex=(tim, (0.5 * k, 0, 8.5 * k, (3.3 + UNDER) * k), 1),
           forma=_sobre_aigua(T, P0, P3))
    # l'estai de proa
    e.cable('nau', [T(27, 0, 15.6), T(40.4, 0, sheer(40.2) + 0.2)], STEELX, 2.6, gruix=0.05)
    return idx


CRANE_TIP = (1.2, 6.9, 7.2)               # la punta del braç de la grua (m, w, y: coordenades de la nau)

# Els llums de l'Arenga (coordenades de la nau): color, radi del halo (m), força
SHIP_LIGHTS = [((27, 16.2, 0), LAMPW, 0.9, 0.75), ((36.5, 9.8, 0), LAMPW, 0.7, 0.6),
               ((30.6, 7.2, 3.7), (90, 255, 140), 0.7, 0.7), ((0.05, 3.9, 0.0), LAMPW, 0.6, 0.55),
               ((13.0, 5.7, 1.6), GLOW_WARM, 2.2, 0.35)]


def ship_lights(cv, pla, T, k=1.0):
    for (m, y, w), col, r, a in SHIP_LIGHTS:
        P = T(m, w, y)
        u, v = pla.p(P)
        rr = max(2.5, r * pla.k(P) * 2.2)
        cv.glow(round(u), round(v), rr, col, a * k)
        if r < 1:
            cv.flat(round(u), round(v), mix(col, (255, 255, 255), 0.5))


# ─── La plataforma (al món) ─────────────────────────────────────────────────

PS = 3.0                                  # píxels per metre del dibuix pla de la plataforma (la textura del mòdul)


@functools.lru_cache(maxsize=None)
def _plat_flat():
    cv = Canvas(40 * 3 * 4, 40 * 3 * 4, light=LIGHT, transparent=True)
    k = 12
    platform(cv, 240, 400, k, 'night')
    return cv.img, k


def plat_T(pla):
    (cx, cz), a = pla.plat
    c, s = math.cos(a), math.sin(a)

    def T(lx, y, lz):
        return (cx + lx * c - lz * s, y, cz + lx * s + lz * c)
    return T


def _pbox(e, T, sid, x0, x1, z0, z1, y0, y1, ramp, lvl, cares=None):
    F = {
        'darrere': ((x1, y1, z1), (x0, y1, z1), (x0, y0, z1), (x1, y0, z1)),
        'esquerra': ((x0, y1, z1), (x0, y1, z0), (x0, y0, z0), (x0, y0, z1)),
        'dreta': ((x1, y1, z0), (x1, y1, z1), (x1, y0, z1), (x1, y0, z0)),
        'davant': ((x0, y1, z0), (x1, y1, z0), (x1, y0, z0), (x0, y0, z0)),
        'sota': ((x0, y0, z0), (x1, y0, z0), (x1, y0, z1), (x0, y0, z1)),
        'dalt': ((x0, y1, z1), (x1, y1, z1), (x1, y1, z0), (x0, y1, z0)),
    }
    cares = cares or {}
    for nom in ('darrere', 'sota', 'esquerra', 'dreta', 'dalt', 'davant'):
        e.quad(sid, *[T(*p) for p in F[nom]], **cares.get(nom, {'ramp': ramp, 'lvl': lvl}))


def plataforma(e, pla):
    """La plataforma: quatre potes amb travessers, la coberta, el mòdul (el logotip tapat, del dibuix pla), la
    torre de gelosia amb el llum vermell i la grua."""
    T = plat_T(pla)
    img, k = _plat_flat()

    def tc(a, b, c, d):                    # retall del dibuix pla (x de -a.. metres, y metres)
        return (240 + a * k, 400 - d * k, 240 + c * k, 400 - b * k)
    legs = [(-13, -8), (13, -8), (-13, 8), (13, 8)]
    for lx, lz in sorted(legs, key=lambda q: -pla.cam.vista(T(q[0], 0, q[1]))[2]):
        e.tub('plat', T(lx, -0.5, lz), T(lx, 9.0, lz), 0.9, STEELX, 2.2, llum_dir=(0.7, 0.6))
    for (ax, az), (bx, bz) in (((-13, -8), (13, -8)), ((-13, -8), (-13, 8)), ((13, -8), (13, 8))):
        for y0, y1 in ((2.0, 5.5), (5.5, 9.0)):
            e.cable('plat', [T(ax, y0, az), T(bx, y1, bz)], STEELX, 1.6, gruix=0.35)
            e.cable('plat', [T(ax, y1, az), T(bx, y0, bz)], STEELX, 1.6, gruix=0.35)
    _pbox(e, T, 'plat', -16, 16, -10, 10, 9.0, 11.5, STEELX, 2.4,
          cares={'dalt': {'ramp': STEELX, 'lvl': 3.0}, 'sota': {'ramp': STEELX, 'lvl': 1.0}})
    _pbox(e, T, 'modul', -12, 6, -9.4, -1, 11.5, 18, STEELX, 1.8, cares={
        'davant': {'tex': (img, tuple(q / 4 for q in tc(-12, 11.5, 6, 18)), 4)},
        'dalt': {'ramp': STEELX, 'lvl': 2.8}})
    # la torre de gelosia
    tl = [(8, -6), (12, -6), (12, -2), (8, -2)]
    top = [(9.6, -4.4), (10.4, -4.4), (10.4, -3.6), (9.6, -3.6)]
    for (ax, az), (bx, bz) in zip(tl, top):
        e.cable('plat', [T(ax, 11.5, az), T(bx, 30, bz)], STEELX, 2.6, gruix=0.3)
    for j in range(6):
        ya, yb = 11.5 + j * 3.1, 11.5 + (j + 1) * 3.1
        ka, kb = (ya - 11.5) / 18.5, (yb - 11.5) / 18.5
        for i in range(4):
            a0, a1 = tl[i], tl[(i + 1) % 4]
            b0, b1 = top[i], top[(i + 1) % 4]
            pa = (a0[0] + (b0[0] - a0[0]) * ka, a0[1] + (b0[1] - a0[1]) * ka)
            pb = (a1[0] + (b1[0] - a1[0]) * kb, a1[1] + (b1[1] - a1[1]) * kb)
            e.cable('plat', [T(pa[0], ya, pa[1]), T(pb[0], yb, pb[1])], STEELX, 1.8, gruix=0.18)
    # la grua
    e.cable('plat', [T(-14, 11.5, -8), T(-14, 16, -8)], STEELX, 2.6, gruix=0.6)
    e.cable('plat', [T(-14, 16, -8), T(-22, 23, -12)], YELLOW, 1.8, gruix=0.4)
    e.cable('plat', [T(-22, 23, -12), T(-22, 17, -12)], STEELX, 1.6, gruix=0.12)


PLAT_LIGHTS = [((-15.5, 11.8, -10), GLOW_WARM), ((15.5, 11.8, -10), GLOW_WARM), ((15.5, 11.8, 10), GLOW_WARM),
               ((-3, 11.8, -10), (230, 236, 255))]
PLAT_RED = (10, 30.6, -4)
WATCHER = (1.5, 11.5, -9.6)               # la silueta dels prismàtics, a la barana del davant


def plat_lights(cv, pla, red=True):
    T = plat_T(pla)
    for P, col in PLAT_LIGHTS:
        u, v = pla.p(T(*P))
        cv.glow(round(u), round(v), 6, col, 0.55)
        cv.flat(round(u), round(v), mix(col, (255, 255, 255), 0.4))
    u, v = pla.p(T(*PLAT_RED))
    if red:
        cv.glow(round(u), round(v), 5, (255, 40, 30), 0.85)
        cv.flat(round(u), round(v), (255, 90, 70))
    else:
        cv.flat(round(u), round(v), (110, 24, 22))


def plat_columnes(cv, pla, phase=0):
    """Les columnes de llum dels focus de la coberta al mar, trencades per l'onada."""
    T = plat_T(pla)
    for i, (P, col) in enumerate(PLAT_LIGHTS):
        u, v = pla.p(T(*P))
        _, vw = pla.p(T(P[0], 0, P[2]))
        top = round(2 * pla.hor - v)
        for y in range(round(vw), min(H, top + 30)):
            fade = 1 - (y - vw) / max(1, top + 30 - vw)
            for dx in (-1, 0, 1):
                x = round(u) + dx + round(math.sin(y * 0.9 + phase + i) * 0.8)
                if hr(x, y, phase + i * 7) < 0.45 * fade * (1.0 if dx == 0 else 0.4):
                    cv.flat(x, y, mix(cv.get(x, y), col, 0.5 * fade))


# ─── La boia (primer pla) ───────────────────────────────────────────────────

def boia(e, pla, bob=0.0, tilt=0.0):
    """Una boia de senyalització, a prop i a contrallum: el cos, la gàbia i el llum a dalt."""
    bx, bz = pla.buoy
    ct, st = math.cos(tilt), math.sin(tilt)

    def T(x, y, z):
        return (bx + x * ct - y * st, y * ct + x * st + bob, bz + z)
    e.tub("boia", T(0, -0.4, 0), T(0, 1.4, 0), 1.0, SIL, 2.9, llum_dir=(0.9, 0.4))
    e.tub('boia', T(0, 1.4, 0), T(0, 1.75, 0), 0.6, SIL, 1.6, llum_dir=(0.9, 0.4))
    for ang in (0.4, 2.0, 3.6, 5.2):
        x, z = math.cos(ang) * 0.45, math.sin(ang) * 0.45
        e.cable('boia', [T(x, 1.7, z), T(x * 0.5, 3.4, z * 0.5)], SIL, 2.2, gruix=0.09)
    e.tub('boia', T(0, 3.3, 0), T(0, 3.55, 0), 0.32, SIL, 2.4, llum_dir=(0.9, 0.4))
    e.cable('boia', [T(0, 3.55, 0), T(0, 4.1, 0)], SIL, 1.6, gruix=0.08)
    return T(0, 3.45, 0)


def boia_llum(cv, pla, P, on):
    u, v = pla.p(P)
    if on:
        cv.glow(round(u), round(v), 9, (255, 214, 90), 0.75)
        cv.flat(round(u), round(v), (255, 240, 170))
        cv.flat(round(u) + 1, round(v), (255, 214, 90))
    else:
        cv.flat(round(u), round(v), (90, 70, 24))


# ─── L'escena ───────────────────────────────────────────────────────────────

def gronxa(i):
    """El gronxar de l'Arenga al fotograma i: (puja, escora, capcineja)."""
    a = 2 * math.pi * i / N
    return 0.12 * math.sin(a), 0.010 * math.sin(a - 0.9), 0.0025 * math.sin(a + 0.6)


def _escena(cv, cam, pla, i, coses, bastida=None):
    e = Escena(cv, cam, [Llum((60000.0, 52000.0, 70000.0), 1e7, 1.6, power=1.0),
                         Llum(ship_T(pla)(12.6, 0.0, 5.6), 9.0, 1.6)], ambient=-0.6)
    out = {}
    if 'plat' in coses:
        plataforma(e, pla)
    if 'nau' in coses:
        out['T'] = T = ship_T(pla, *gronxa(i))
        out['bastida'] = nau(e, T, bastida=bastida)
    if 'boia' in coses:
        out['boia'] = boia(e, pla, bob=0.18 * math.sin(2 * math.pi * i / N + 1.7),
                           tilt=0.05 * math.sin(2 * math.pi * i / N + 0.9))
    return e, out


def _reflex(pla, i, coses):
    """El que hi ha damunt del mar vist per la càmera de sota l'aigua, girat: el reflex (RGBA)."""
    cv = Canvas(light=LIGHT, transparent=True)
    _escena(cv, pla.mirall, pla, i, coses)
    if 'nau' in coses:
        ship_lights(cv, pla_mirall(pla), ship_T(pla, *gronxa(i)), 0.7)
    a = np.asarray(cv.img)
    out = np.zeros_like(a)
    for y in range(pla.hor, H):
        sy = 2 * pla.hor - y
        if 0 <= sy < H:
            out[y] = a[sy]
    return out


def pla_mirall(pla):
    """Per dibuixar els halos dels llums a la càmera de sota l'aigua: projecta el punt reflectit (i es gira
    després amb tota la imatge)."""
    class _M:
        def p(self, P):
            u, v = pla.p((P[0], -P[1], P[2]))
            return u, 2 * pla.hor - v

        def k(self, P):
            return pla.k(P)
    return _M()


def _aplica_reflex(cv, ref, pla, i, k=0.42, seed=7):
    """El reflex damunt del mar: ondulat, trencat per les onades, més fluix com més avall."""
    base = np.asarray(cv.img).astype(np.float64)
    ys = np.arange(H)[:, None]
    xs = np.arange(W)[None, :]
    dy = ys - pla.hor
    shift = np.round(np.sin(ys * 0.8 + seed + i * 0.7) * (0.6 + np.abs(dy) * 0.03)).astype(int)
    sx = np.clip(xs + shift, 0, W - 1)
    src = ref[np.broadcast_to(ys, (H, W)), sx].astype(np.float64)
    brk = _hash(np.floor(xs / 3) + 0 * ys, ys + 0 * xs, seed + i)
    keep = (src[..., 3] > 0) & (dy > 0) & (brk > 0.16 + np.minimum(0.5, np.abs(dy) / 300))
    kk = (k * np.maximum(0.25, 1 - dy / 220))[..., None]
    out = base.copy()
    out[..., :3] = np.where(keep[..., None], base[..., :3] * (1 - kk) + src[..., :3] * kk, base[..., :3])
    cv.img.paste(Image.fromarray(out.astype(np.uint8), 'RGBA'))
    cv.P = cv.img.load()


def _espuma(cv, pla, X, Z, nn, i, y0, estela=60.0):
    """L'escuma arran del buc i l'estela curta que surt de popa (al món: s'empetiteix sola)."""
    sx, sz = pla.ship
    s, c = math.sin(pla.psi), math.cos(pla.psi)
    m = (X - sx) * s + (Z - sz) * c
    w = (X - sx) * c - (Z - sz) * s
    hbv = np.vectorize(hb)(np.clip(m, 0, 37.8))
    d = np.abs(w) - hbv
    foam = np.zeros_like(X)
    side = (m > -0.3) & (m < 38.5) & (d > -0.3) & (d < 1.2)
    foam += np.where(side, np.clip(1 - d / 1.2, 0, 1) * 0.8, 0)
    back = -m
    wash = (back > 0) & (back < estela)
    patch = _vn(back / 2.5 + 0 * w, w / 1.2, 77 + i // 2)                 # l'escuma, a clapes
    kw = max(1.0, estela / 60)                                            # (de lluny, més ample)
    width = (1.4 + back * 0.05) * kw
    foam += np.where(wash & (np.abs(w) < width),
                     np.clip(1 - back / estela, 0, 1) ** 1.5 * (1 - np.abs(w) / width) * 1.1 * (patch > 0.35), 0)
    arm = np.abs(np.abs(w) - (hb(0) + back * 0.3))
    foam += np.where(wash & (arm < (0.35 + back * 0.008) * kw),
                     np.clip(1 - back / (estela * 0.67), 0, 1) ** 1.5 * 0.8 * (patch > 0.5), 0)
    foam *= 0.6 + 0.5 * np.clip(nn * 0.3 + 0.5, 0, 1.4)
    rnd = _hash(np.floor(X * 3), np.floor(Z * 3), 300 + i)
    a = np.asarray(cv.img).copy()
    reg = a[y0:]
    fm = (foam > 0.25) & (rnd < foam)
    col = np.array([110, 132, 144])
    reg[fm, :3] = (reg[fm, :3] * 0.45 + col * 0.55).astype(np.uint8)
    cv.img.paste(Image.fromarray(a, 'RGBA'))
    cv.P = cv.img.load()


@functools.lru_cache(maxsize=None)
def cel(pla, seed=31, clouds=0.5):
    cv = Canvas(light=LIGHT)
    night_sky(cv, 0, pla.hor, moon=pla.moon, seed=seed, clouds=clouds)
    return cv.img


def fons(pla, i=0, coses=('plat', 'nau', 'boia'), seed=31, clouds=0.5, calm=1.0, estela=60.0, path=(2.4, 0.3)):
    """Un pla sencer al fotograma i (sense títol ni capes): cel, mar, escuma, reflexos, plataforma, nau, boia i
    llums. (Els crèdits en fan servir un altre `Pla`.)"""
    cv = Canvas(light=LIGHT, img=cel(pla, seed, clouds).copy())
    lvl, nn, X, Z = mar(pla, phase=1.4 * math.sin(2 * math.pi * i / N), seed=seed + 1, twinkle=i, calm=calm,
                        path=path)
    pinta_nivells(cv, lvl, pla.hor + 1)
    if 'nau' in coses:
        _espuma(cv, pla, X, Z, nn, i, pla.hor + 1, estela)
    _aplica_reflex(cv, _reflex(pla, i, coses), pla, i)
    if 'plat' in coses:
        plat_columnes(cv, pla, i)
    e, out = _escena(cv, pla.cam, pla, i, tuple(c for c in coses if c != 'boia'))
    if 'plat' in coses:
        plat_lights(cv, pla, red=(i % 4 != 3))
    if 'nau' in coses:
        ship_lights(cv, pla, out['T'])
    if 'boia' in coses:
        e2, out2 = _escena(cv, pla.cam, pla, i, ('boia',))
        boia_llum(cv, pla, out2['boia'], on=(i % 4) in (0, 1))
    return cv.img


@functools.lru_cache(maxsize=None)
def _fons(i=0):
    return fons(PLA, i)


def bg(cv, frame=0):
    cv.img.paste(_fons(frame))
    cv.P = cv.img.load()


def _frames():
    base = _fons(0)
    return [_diff(_fons(i), base) for i in range(N)]


def _title_frames():
    cv = Canvas(light=LIGHT, transparent=True)
    title(cv)
    return [cv.img]


PROPS = {}


# ─── Els personatges (sprites del joc, a la seva escala, de nit) ────────────

CHARS = Path(__file__).resolve().parents[1] / 'characters'
PERSON_M = 1.78 / 110                     # metres per píxel del full (un personatge fa ≈110 px)


@functools.lru_cache(maxsize=None)
def sprite(nom, tag, flip=False, frame=0):
    d = json.loads((CHARS / nom / f'{nom}.json').read_text())
    sheet = Image.open(CHARS / nom / f'{nom}.png').convert('RGBA')
    t = [t for t in d['meta']['frameTags'] if t['name'] == tag][0]
    fr = list(d['frames'].values())[t['from'] + frame]['frame']
    im = sheet.crop((fr['x'], fr['y'], fr['x'] + fr['w'], fr['y'] + fr['h']))
    if flip:
        im = im.transpose(Image.Transpose.FLIP_LEFT_RIGHT)
    a = np.asarray(im).astype(np.float64)
    a[..., :3] *= np.array(NIGHT_TINT)
    bb = im.getbbox()
    out = Image.fromarray(a.clip(0, 255).astype(np.uint8), 'RGBA')
    return out, ((bb[0] + bb[2]) / 2, bb[3] - 1)


# ─── En Bastida, a popa ─────────────────────────────────────────────────────
# Dret a la borda d'estribord, al costat de la grua, mig amagat per la borda; la brasa de la pipa. Al pròleg, quan
# la Juana ja té la mostra, treu de la butxaca el missatger de satèl·lit, que fa llum blava, i escriu
# («bastida_escriu»). 8 fotogrames de 300 ms, com el mar, perquè es gronxi amb el vaixell.

SCREEN = (150, 226, 255)


def _bastida_img():
    im, peu = sprite('bastida', 'IdleDL', flip=True)
    return im, peu, PERSON_M


def _bastida(i, device=False):
    pla = PLA
    cv = Canvas(light=LIGHT)
    cv.img.paste(_fons(i))
    cv.P = cv.img.load()
    e, out = _escena(cv, pla.cam, pla, i, ('nau',), bastida=_bastida_img())
    idx = out['bastida']
    T = out['T']
    a = np.asarray(cv.img).copy()
    amo = np.frombuffer(e.amo, dtype=np.uint16).reshape(H, W)
    keep = amo == idx
    a[~keep] = 0
    lay = Image.fromarray(a, 'RGBA').copy()
    lc = Canvas(light=LIGHT, img=lay)
    k = pla.k(T(4.6, 2.9, 4.0))
    hx, hy = pla.p(T(4.6, 3.0, 2.4 + 1.55))                        # la boca
    ember = (255, 140, 60) if (i % 4) else (200, 80, 30)
    lc.flat(round(hx + 0.12 * k), round(hy), ember)
    if device:
        dx, dy = pla.p(T(4.4, 3.2, 2.4 + 1.05))                    # les mans, davant del pit
        bright = SCREEN if i % 3 else (220, 245, 255)
        lc.flat(round(dx), round(dy), bright)
        lc.flat(round(dx) + 1, round(dy), (60, 110, 140))
        _aglow(lc, dx, dy, 6, (120, 210, 255), 0.45)
        _aglow(lc, hx, hy, 4, (120, 200, 240), 0.25)
    return lc.img


def _apx(cv, X, Y, col, a):
    """Un píxel (X, Y) semitransparent, si encara és buit (en una capa)."""
    if 0 <= X < cv.w and 0 <= Y < cv.h and a > 0.03 and not cv.P[X, Y][3]:
        cv.P[X, Y] = tuple(col) + (int(255 * min(1.0, a)),)


def _aput(cv, x, y, col, a):
    _apx(cv, int(x), int(y), col, a)


def _aglow(cv, cx, cy, r, col, a0):
    for y in range(int(cy - r), int(cy + r) + 1):
        for x in range(int(cx - r), int(cx + r) + 1):
            d = math.hypot(x - cx, (y - cy) * 1.2) / r
            if d < 1 and 0 <= x < cv.w and 0 <= y < cv.h:
                o = cv.P[x, y]
                a = a0 * (1 - d) ** 2
                if o[3]:
                    cv.P[x, y] = mix(o, col, min(1, a)) + (o[3],)
                else:
                    _apx(cv, x, y, col, a)


BASTIDA = {'frames': lambda: [_bastida(i) for i in range(N)], 'frameDuration': 300, 'zIndex': 2}
BASTIDA_ESCRIU = {'frames': lambda: [_bastida(i, device=True) for i in range(N)], 'frameDuration': 300,
                  'prop': 'bastida_popa'}


# ─── Una pantalla, a la caseta ──────────────────────────────────────────────
# Al pròleg, quan la Juana aixeca el pot, darrere l'ull de bou fosc de la cara de popa de la caseta s'encén una
# pantalla petita, blava, que parpelleja com quan algú hi escriu («pantalla_on»). No s'hi veu ningú: el guió no diu
# qui és. Segueix el gronxar de l'Arenga (8 fotogrames de 300 ms, com el mar).

ULL_FOSC = (13.0, 1.9, 5.15)              # l'ull de bou apagat de la caseta (m, w, y: coordenades de la nau)


def _pantalla(i):
    lc = Canvas(light=LIGHT, transparent=True)
    m, w, y = ULL_FOSC
    T = ship_T(PLA, *gronxa(i))
    px, py = PLA.p(T(m, w, y))
    x, y = round(px), round(py)
    bright = SCREEN if i % 3 else (220, 245, 255)           # el text que hi va sortint
    # (una mica més gran del que tocaria, perquè es vegi que s'encén: tasca 055)
    lc.rect(x, y, x + 1, y + 1, [bright], 0, lit=0)
    lc.flat(x, y + 2, (60, 110, 140))
    lc.flat(x + 1, y + 2, (60, 110, 140))
    _aglow(lc, px, py, 10, (120, 210, 255), 0.7 if i % 2 else 0.5)
    return lc.img


PANTALLA = {'frames': lambda: [Canvas(light=LIGHT, transparent=True).img], 'frameDuration': 1000, 'loop': False,
            'zIndex': 2}
PANTALLA_ON = {'frames': lambda: [_pantalla(i) for i in range(N)], 'frameDuration': 300, 'prop': 'pantalla'}


# ─── La zòdiac ──────────────────────────────────────────────────────────────
# A la portada penja de la grua amb la Juana a dins («zodiac», en bucle). Al pròleg, cada tros comença amb una
# frase (vegeu rooms/proleg_punt7.json) i es queda a l'últim fotograma: la grua la baixa («z_baixa»), va a poc a poc
# cap a la plataforma («z_travessa»), i la Juana treu la mostra a contrallum («z_mostra») i hi escriu («z_escriu»).
# Els temps són d'una sola història contínua; cada tros n'és una finestra (CLIPS). Ara és al món: a prop de popa és
# gran, i s'empetiteix mentre s'allunya cap a la plataforma.

ZT = 0.15                                 # segons per fotograma
Z_LOWER = (0.3, 5.3)
Z_TOUCH = 5.3
Z_HOOK = (5.8, 7.3)
Z_MOTOR = 10.0
# La travessa, curta (tasca 055: eren 17 s sense cap text): 7 s.
Z_MOVE = (10.5, 17.5)
Z_LANTERN = 18.8
Z_DIP = (19.3, 20.5)
Z_SCOOP = (20.5, 21.1)
Z_RAISE = (21.1, 22.6)
Z_WRITE = (30.0, 30.5, 32.2)              # abaixa el pot fins al pit, hi escriu, i el deixa allà
CLIPS = {'z_baixa': (0.0, 10.0), 'z_travessa': (10.0, 18.5), 'z_mostra': (18.5, 30.0), 'z_escriu': (30.0, 33.0)}

WIRE = [(6, 8, 12), (20, 24, 30), (42, 48, 56), (78, 84, 90)]
FOAMC = (110, 130, 145)
LAMPC = (255, 236, 180)
JARC = (206, 200, 172)
Z_HANG = 2.2                              # l'altura de la zòdiac penjada (la quilla, sobre el mar)
# On s'atura: davant de la plataforma (al món), però més a prop de la càmera que la plataforma, perquè la Juana i el
# que fa (el pot, el retolador, la llanterna) es llegeixin (tasca 055: a (36, 98) feia uns 4 px per metre; aquí, 6).
Z_END = (28.0, 72.0)


def _ease(t):
    t = max(0.0, min(1.0, t))
    return t * t * (3 - 2 * t)


def _seg(t, ab):
    return _ease((t - ab[0]) / (ab[1] - ab[0]))


def _zpath(k):
    """El camí de la zòdiac (al món, x, z): de sota la grua fins a davant de la plataforma, amb una mica de corba."""
    T = ship_T(PLA)
    ax, _, az = T(CRANE_TIP[0], CRANE_TIP[1], 0)
    bx, bz = Z_END
    cx, cz = ax + 22, az + 6                                   # primer s'aparta del vaixell
    u = 1 - k
    return (u * u * ax + 2 * u * k * cx + k * k * bx, u * u * az + 2 * u * k * cz + k * k * bz)


def _zstate(t, i_bob, sway_t=None):
    """→ (x, y de la quilla, z, rumb, a l'aigua?, motor?)"""
    psi = PLA.psi
    if t < Z_TOUCH:
        T = ship_T(PLA, *gronxa(i_bob))
        k = _seg(t, Z_LOWER)
        x, _, z = T(*CRANE_TIP)
        y = (Z_HANG + gronxa(i_bob)[0]) * (1 - k)
        st = t if sway_t is None else sway_t
        sway = 0.14 * math.sin(st * 2 * math.pi / 2.4) * (1 - k)
        s, c = math.sin(psi), math.cos(psi)
        return x + sway * s, y, z + sway * c, psi, False, False
    k = _seg(t, Z_MOVE)
    x, z = _zpath(k)
    ka = min(k, 0.97)
    (xa, za), (xb, zb) = _zpath(ka), _zpath(ka + 0.03)
    head = psi + (math.atan2(xb - xa, zb - za) - psi) * _ease(k * 5)
    d = t - Z_TOUCH
    wave = 0.12 * math.exp(-d * 2) * math.sin(d * 8) + 0.05 * math.sin(t * 2.4)
    motor = Z_MOTOR <= t < Z_MOVE[1] + 0.3
    return x, wave, z, head, True, motor


@functools.lru_cache(maxsize=None)
def _juana():
    im, peu = sprite('juana', 'Seu', flip=True)
    return im, peu


def _zodiac(e, x, y, z, head, t, motor):
    """La zòdiac al món: els flotadors (gris fosc amb la franja taronja), el fons, el motor i la Juana asseguda.
    → (punt de les espatlles de la Juana, punt del cap)"""
    s, c = math.sin(head), math.cos(head)

    def P(lm, lw, ly):                                         # lm: cap a proa, lw: a estribord
        return (x + lm * s + lw * c, y + ly, z + lm * c - lw * s)
    L, Bm, r = 4.2, 0.85, 0.24
    # el flotador de babord (el de més enllà), el fons, el de proa i el d'estribord
    e.tub('zodiac', P(-L / 2, -Bm, r), P(L / 2 - 0.5, -Bm, r), r, RUBBER, 3.6, llum_dir=(0.8, 0.8))
    e.quad('zodiac', P(L / 2 - 0.6, -Bm, 0.12), P(L / 2 - 0.6, Bm, 0.12), P(-L / 2, Bm, 0.12), P(-L / 2, -Bm, 0.12),
           ramp=RUBBER, lvl=1.6, dues_cares=True)
    e.tub('zodiac', P(L / 2 - 0.5, -Bm, r), P(L / 2, 0, r + 0.1), r, RUBBER, 4.0, llum_dir=(0.8, 0.8))
    e.tub('zodiac', P(L / 2, 0, r + 0.1), P(L / 2 - 0.5, Bm, r), r, RUBBER, 4.2, llum_dir=(0.8, 0.8))
    # el motor fora borda, a popa (tremola quan va)
    sh = 0.03 if motor and int(t / ZT) % 2 else 0.0
    mx0 = -L / 2 - 0.15
    e.quad('zodiac', P(mx0, -0.22, 0.95 + sh), P(mx0, 0.22, 0.95 + sh), P(mx0, 0.22, 0.3 + sh), P(mx0, -0.22, 0.3 + sh),
           ramp=RUBBER, lvl=2.4, dues_cares=True)
    e.cable('zodiac', [P(mx0 - 0.05, 0, 0.35), P(mx0 - 0.05, 0, -0.3)], RUBBER, 1.6, gruix=0.1)
    # la Juana, asseguda a popa, al costat del motor
    im, peu = _juana()
    e.sprite('juana', im, peu, P(-L / 2 + 1.0, 0.1, 0.12), escala_img=PERSON_M)
    e.tub('zodiac', P(-L / 2, Bm, r), P(L / 2 - 0.5, Bm, r), r, RUBBER, 4.6, llum_dir=(0.8, 0.8))
    e.cable('zodiac', [P(-L / 2 + 0.2, Bm + r * 0.7, r + 0.05), P(L / 2 - 0.6, Bm + r * 0.7, r + 0.05)], ORANGE, 3.2,
            gruix=0.09)
    return P(-L / 2 + 1.0, 0.1, 1.05), P(-L / 2 + 1.0, 0.1, 1.38), P


def _ring(cv, pla, cx, cz, r, a, seed):
    for ang in range(0, 360, 2):
        if hr(ang, seed) > 0.4:
            u, v = pla.p((cx + math.cos(math.radians(ang)) * r, 0, cz + math.sin(math.radians(ang)) * r))
            _aput(cv, round(u), round(v), FOAMC, a)


def _sample(cv, t, jx, top, wl, k):
    """La mostra: la llanterna, la mà a l'aigua i el pot enlaire a contrallum (a la distància on passa, els píxels
    són d'uns 25 cm)."""
    if t < Z_LANTERN:
        return
    on = t - Z_LANTERN > 0.3 or int((t - Z_LANTERN) / ZT) % 2
    lx, ly = jx - 1, top - 1
    hand = None
    if t >= Z_DIP[0]:
        if t < Z_DIP[1]:
            kk = _seg(t, Z_DIP)
            hand = (jx + 2 + round(2 * kk), round(top - 1 + (wl + 1 - (top - 1)) * kk))
        elif t < Z_RAISE[0]:
            hand = (jx + 4, wl + 1)
        elif t < Z_WRITE[0]:
            kk = _seg(t, Z_RAISE)
            hand = (jx + 4 - round(kk), round(wl + 1 + (top - 5 - (wl + 1)) * kk))
        else:
            kk = _seg(t, Z_WRITE[:2])
            hand = (jx + 3, round(top - 5 + 4 * kk))
        cv.line(jx + 1, top + 1, hand[0], hand[1], [(40, 46, 40), (62, 70, 62)], 1.0, lit=0)
        cv.line(jx + 1, top + 2, hand[0], hand[1] + 1, [(40, 46, 40), (62, 70, 62)], 1.0, lit=0)
        if t >= Z_SCOOP[1] and hand[1] < wl:
            # el pot: més gros del que tocaria (3×4 px), perquè es llegeixi a la distància: vidre pàl·lid, la tapa fosca
            # i el fang gris a sota
            hx, hy = hand[0], hand[1]
            for dx in range(-1, 2):
                for dy in range(1, 5):
                    cv.flat(hx + dx, hy - dy, (120, 116, 96) if dy <= 2 else JARC)
                cv.flat(hx + dx, hy - 5, (60, 60, 64))
        if Z_WRITE[1] <= t < Z_WRITE[2]:                                      # el retolador, que va i ve pel pot
            mx = hand[0] - 2 + int(t / ZT) % 3
            cv.flat(mx, hand[1] - 3, (16, 16, 20))
            cv.flat(mx + 1, hand[1] - 4, (16, 16, 20))
            cv.flat(mx + 2, hand[1] - 5, (230, 230, 236))                    # la punta blanca del retolador
    if on:
        cv.flat(lx, ly, LAMPC)
        _aglow(cv, lx, ly, 6, LAMPC, 0.5)
        for j in range(1, 6):                                                # el reflex a l'aigua
            if hr(j, int(t / 0.3)) > 0.3:
                _aput(cv, lx + round((hr(j, 7) - 0.5) * 4), wl + 1 + j, (200, 170, 110), 0.5 - j * 0.07)
        if hand and t >= Z_RAISE[1] - 0.3:
            _aglow(cv, hand[0], hand[1] - 2, 6, (255, 206, 120), 0.45)


def _zframe(t, i_bob=0, sway_t=None):
    pla = PLA
    cv = Canvas(light=LIGHT, transparent=True)
    x, y, z, head, water, motor = _zstate(t, i_bob, sway_t)
    if water:
        d = t - Z_TOUCH
        if d < 2.5:
            _ring(cv, pla, x, z, 1.8 + d * 1.6, 0.7 * (1 - d / 2.5), 1)
            _ring(cv, pla, x, z, 1.2 + d * 1.1, 0.5 * (1 - d / 2.5), 2)
        if motor:                                                           # l'estela: una V darrere
            s, c = math.sin(head), math.cos(head)
            for j in range(1, 60):
                back = j * 0.35
                spread = 0.5 + back * 0.32
                for side in (-1, 1):
                    if hr(j, side, int(t / ZT)) > 0.45:
                        px = x - s * (2.1 + back) + c * side * spread
                        pz = z - c * (2.1 + back) - s * side * spread
                        u, v = pla.p((px, 0, pz))
                        _aput(cv, round(u), round(v), FOAMC, 0.75 * (1 - j / 60))
                if hr(j, 9, int(t / ZT)) > 0.5:
                    u, v = pla.p((x - s * (2.3 + back), 0, z - c * (2.3 + back)))
                    _aput(cv, round(u), round(v), (150, 170, 180), 0.6 * (1 - j / 60))
    # el cable de la grua i el ganxo
    T = ship_T(pla, *gronxa(i_bob))
    tx, ty, tz = T(*CRANE_TIP)
    tip = pla.p((tx, ty, tz))
    if t < Z_HOOK[0]:
        hookP = (x, y + 2.6, z)
    else:
        k = _seg(t, Z_HOOK)
        hookP = (x + (tx - x) * k, 2.6 + (ty - 0.8 - 2.6) * k, z + (tz - z) * k)
    hk = pla.p(hookP)
    cv.line(tip[0], tip[1], hk[0], hk[1], WIRE, 2.4, lit=0)
    cv.put(hk[0], hk[1] + 1, WIRE, 3.4, lit=0)
    # la zòdiac (al món, en una escena pròpia)
    e = Escena(cv, pla.cam, [Llum((60000.0, 52000.0, 70000.0), 1e7, 1.6, power=1.0),
                             Llum(T(12.6, 2.0, 5.6), 16.0, 2.4)], ambient=-0.3)
    _, head_p, P = _zodiac(e, x, y, z, head, t, motor)
    if t < Z_HOOK[0]:                                                       # les eslingues
        for lm in (-1.7, 1.6):
            for lw in (-0.7, 0.7):
                a = pla.p(P(lm, lw, 0.45))
                cv.line(hk[0], hk[1] + 1, a[0], a[1], WIRE, 1.8, lit=0)
    if Z_MOTOR <= t < Z_MOTOR + 1.6:                                        # el motor arrenca: una bufada de fum
        a = t - Z_MOTOR
        mu, mv = pla.p(P(-2.4, 0, 1.0))
        kk = pla.k(P(0, 0, 0)) / 9
        for j in range(7):
            _aput(cv, mu - round(a * 5 * kk) + (j % 3) - 1, mv - round(a * 7 * kk) - j // 3, (90, 94, 104),
                  0.6 * (1 - a / 1.6))
    jx, top = pla.p(head_p)
    _, wl = pla.p(P(0, 0.9, 0))
    _sample(cv, t, round(jx), round(top), round(wl), pla.k(head_p))
    return cv.img


def _wait_frames():
    """A la portada: penja de la grua i es gronxa amb el vaixell (8 fotogrames de 300 ms, com el mar)."""
    return [_zframe(0.0, i, sway_t=i * 0.3) for i in range(N)]


def _clip(name):
    a, b = CLIPS[name]
    return lambda: [_zframe(a + j * ZT, int((a + j * ZT) / 0.3) % N) for j in range(round((b - a) / ZT) + 1)]


ZODIAC_ESPERA = {'frames': _wait_frames, 'frameDuration': 300, 'zIndex': 2}
ZODIAC_CLIPS = {name: {'frames': _clip(name), 'frameDuration': round(ZT * 1000), 'loop': False, 'prop': 'zodiac'}
                for name in CLIPS}


# ─── La silueta de la plataforma ────────────────────────────────────────────
# Al pròleg, quan la narració la diu, s'encén el focus de la plataforma i retalla la silueta dels prismàtics
# («vigia_on», amb un parpelleig de fluorescent). Fins llavors la capa és buida («vigia»). A la distància de la
# plataforma una persona faria 4 px: es dibuixa una mica més grossa, perquè es llegeixi.

def _watcher_layer():
    pla = PLA
    cv = Canvas(light=LIGHT, transparent=True)
    T = plat_T(pla)
    fx, fy = pla.p(T(*WATCHER))
    fx, fy = round(fx), round(fy)
    h = 7
    ink = [(4, 5, 8)]
    # el focus de darrere, que la retalla
    cv.rect(fx + 3, fy - h - 2, fx + 5, fy - h, [(255, 250, 230)], 0, lit=0)
    _aglow(cv, fx + 4, fy - h - 1, h * 2 + 6, (220, 226, 255), 0.5)
    cv.rect(fx - 1, fy - h, fx + 1, fy - 1, ink, 0, lit=0)
    cv.rect(fx - 2, fy - h + 2, fx + 2, fy - h // 2, ink, 0, lit=0)
    cv.disc(fx, fy - h - 1, 1.6, 1.6, ink, 0, lit=0)
    cv.rect(fx - 4, fy - h, fx - 2, fy - h + 1, ink, 0, lit=0)        # els prismàtics
    cv.flat(fx - 4, fy - h, (180, 200, 220))
    return cv.img


def _watcher_frames():
    on = _watcher_layer()
    off = Canvas(light=LIGHT, transparent=True).img
    return [on if k else off for k in (1, 0, 0, 1, 0, 1, 1, 0, 1, 1, 1, 1)]


VIGIA = {'frames': lambda: [Canvas(light=LIGHT, transparent=True).img], 'frameDuration': 1000, 'loop': False,
         'zIndex': 2}
VIGIA_ON = {'frames': _watcher_frames, 'frameDuration': 90, 'loop': False, 'prop': 'vigia'}


# ─── El logotip tapat ───────────────────────────────────────────────────────
# Al pròleg, quan la Juana mira la plataforma (proleg.9), l'enfoca amb la llanterna: un feix de llum va de la zòdiac al
# mòdul, i s'hi veu el logotip de la companyia tapat amb dues tires de cinta americana en creu («logo_on»; tasca 055).
# A la distància de la plataforma el mòdul fa 25 px: el rètol es dibuixa més gros (14×9), com la silueta, perquè es
# llegeixi. Fins llavors, la capa és buida («logo»).

LOGO_C = (-8.0, 14.6, -9.4)               # el mig del rètol, al davant del mòdul (a l'esquerra de la silueta)
LOGO_W, LOGO_H = 14, 9


def _llanterna():
    """On és la llanterna de la Juana quan la zòdiac ja s'ha aturat (en píxels)."""
    x, y, z, head, _, _ = _zstate(CLIPS['z_escriu'][1], 0)
    s, c = math.sin(head), math.cos(head)
    u, v = PLA.p((x - 1.1 * s + 0.1 * c, y + 1.38, z - 1.1 * c - 0.1 * s))
    return round(u) - 1, round(v) - 1


def _logo_layer(k):
    """El feix de la llanterna i el rètol il·luminat; `k` (0–1): quanta llum (el parpelleig)."""
    pla = PLA
    cv = Canvas(light=LIGHT, transparent=True)
    lx, ly = _llanterna()
    cx, cy = (round(q) for q in pla.p(plat_T(pla)(*LOGO_C)))
    x0, y0 = cx - LOGO_W // 2, cy - LOGO_H // 2
    x1, y1 = x0 + LOGO_W - 1, y0 + LOGO_H - 1
    # el rètol: la planxa clara, il·luminada, i el logotip (una gota taronja dins un cercle)
    plate = mix((150, 146, 132), (255, 236, 180), 0.3 * k)
    cv.rect(x0, y0, x1, y1, [plate], 0, lit=0)
    cv.rect(x0, y0, x1, y0, [mix(plate, (255, 255, 255), 0.25)], 0, lit=0)
    cv.disc(cx, cy, 3.2, 3.2, [(196, 80, 26)], 0, lit=0)
    cv.disc(cx, cy + 0.5, 1.6, 1.8, [(240, 150, 60)], 0, lit=0)
    # la cinta americana: dues tires grises en creu, d'un racó a l'altre
    for (ax, ay, bx, by) in ((x0, y0 + 1, x1, y1 - 1), (x0, y1 - 1, x1, y0 + 1)):
        cv.line(ax, ay, bx, by, [(184, 186, 190)], 0, lit=0)
        cv.line(ax, ay + 1, bx, by + 1, [(150, 152, 158)], 0, lit=0)
    # el feix: un triangle de llum de la llanterna fins als dos costats del rètol, més fluix com més lluny
    P = cv.img.load()
    cv.P = P
    ax, ay, bx, by = x0 - 1, y0 - 1, x0 - 1, y1 + 1
    def costat(px, py, qx, qy, rx, ry):
        return (qx - px) * (ry - py) - (qy - py) * (rx - px)
    for yy in range(min(ly, ay) - 1, max(ly, by) + 2):
        for xx in range(min(lx, ax), max(lx, x1) + 1):
            d1, d2, d3 = costat(lx, ly, ax, ay, xx, yy), costat(ax, ay, x1 + 1, y0 - 1, xx, yy), costat(x1 + 1, y1 + 1, lx, ly, xx, yy)
            if (d1 >= 0 and d2 >= 0 and d3 >= 0) or (d1 <= 0 and d2 <= 0 and d3 <= 0):
                f = math.hypot(xx - lx, yy - ly) / max(1.0, math.hypot(cx - lx, cy - ly))
                _aput(cv, xx, yy, (255, 226, 160), (0.32 - 0.18 * f) * k)
    _aglow(cv, lx, ly, 5, LAMPC, 0.55 * k)
    return cv.img


def _logo_frames():
    return [_logo_layer(k) for k in (0.4, 1.0, 0.7, 1.0, 1.0, 0.85, 1.0, 1.0)]


LOGO = {'frames': lambda: [Canvas(light=LIGHT, transparent=True).img], 'frameDuration': 1000, 'loop': False,
        'zIndex': 2}
LOGO_ON = {'frames': _logo_frames, 'frameDuration': 120, 'loop': False, 'prop': 'logo'}


ANIMS = {
    'mar': {'frames': _frames, 'frameDuration': 300},
    'zodiac': ZODIAC_ESPERA,
    'bastida_popa': BASTIDA,       # «bastida» sol xocaria amb la seva veu (el personatge) a BenneScript
    'titol': {'frames': _title_frames, 'frameDuration': 1000, 'loop': False, 'zIndex': 3},
}

GEOMETRIA = {'things': {}, 'spawns': {}}
