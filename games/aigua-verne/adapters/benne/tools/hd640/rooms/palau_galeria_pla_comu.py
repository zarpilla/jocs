"""
El dibuix pla de la galeria de les piscines (palau_galeria), d'on surten les textures de la sala en 3D: la paret del
fons amb el finestral a l'espai (Terra-2, el dipòsit, les columnes i els llums d'aranya), la paret de l'esquerra amb la
porta del saló, l'aquari dels trenta-tres peixos (el vidre del davant i el del costat) amb el peu del rètol «LOT 12»,
una columna dreta, un llum d'aranya i l'aigua de les piscines plenes vista des de dalt.

Tot es dibuixa de cara, com sempre, a 1 píxel per unitat del món (1×), i palau_galeria.py ho projecta.
"""
import math

import numpy as np
from PIL import Image

import hd640  # noqa: F401  (abans de cap hd.rooms: posa la llibreria a 640×360)
from hd.pix import Canvas, Light, mix
from hd640.rooms.palau_comu import (MARB, ORP, CROM, AIGUA, ESPAI, STAR_W, lletres_c, terra2,
                                    diposit, columna, motllura, marc_or, vidre, aigua_aquari, peixos)

LLUM_PLA = Light(ambient=0.3, vignette=None, floor_fade=None)


# ─── Soroll ràpid (numpy) ───────────────────────────────────────────────────
# El fbm de la llibreria fa servir un random.Random per punt: en superfícies grans (parets, el terra) era el 90% del
# temps de dibuix. Aquí, el mateix tipus de soroll de valors suau, sencer d'una vegada.

def soroll(w, h, cel, seed=0, octaves=3):
    """Soroll de valors suau (0..1, aprox.) de w × h, amb cel·les de `cel` píxels i `octaves` octaves."""
    rng = np.random.default_rng(seed)
    tot, amp, suma = np.zeros((h, w), np.float32), 1.0, 0.0
    for o in range(octaves):
        c = max(1.0, cel / 2 ** o)
        gw, gh = int(w / c) + 3, int(h / c) + 3
        g = rng.random((gh, gw)).astype(np.float32)
        im = Image.fromarray(g, 'F').resize((int(gw * c), int(gh * c)), Image.Resampling.BICUBIC)
        tot += np.asarray(im)[:h, :w] * amp
        suma += amp
        amp *= 0.5
    return tot / suma


def venes(w, h, seed=3, gruix=0.022):
    """Les venes del marbre (0 = res, 1 = al mig d'una vena), de w × h: el soroll deformat per un altre soroll."""
    n = soroll(w + 80, h + 80, 70, seed, 3)
    dx = (soroll(w, h, 30, seed + 1, 2) - 0.5) * 70
    ys, xs = np.mgrid[0:h, 0:w]
    xi = np.clip((xs + 40 + dx).astype(int), 0, w + 79)
    yi = np.clip((ys * 0.5 + 40 + dx * 0.4).astype(int), 0, h + 79)
    v = n[yi, xi]
    return np.clip(1 - np.abs(v - 0.5) / gruix, 0, 1)


def espai(cv, x0, y0, x1, y1, seed=1, mask=None, dens=1.0):
    """Negre estrellat amb una nebulosa molt fosca (com palau_comu.espai, però amb el soroll ràpid).
    → estrelles brillants [(x, y)]."""
    w, h = x1 - x0 + 1, y1 - y0 + 1
    neb = soroll(w, h, 80, seed, 3)
    fi = soroll(w, h, 18, seed + 4, 2)
    rng = np.random.default_rng(seed + 77)
    r = rng.random((h, w))
    k = rng.random((h, w))
    bright = []
    for j in range(h):
        for i in range(w):
            x, y = x0 + i, y0 + j
            if mask and not mask(x, y):
                continue
            band = max(0.0, 1 - abs(j - i * 0.25 - h * 0.6) / 70)
            n = float(neb[j, i])
            lvl = 0.6 + 2.5 * max(0.0, min(1.0, (n - 0.45) / 0.3)) * band + (float(fi[j, i]) - 0.5) * 0.5
            cv.put(x, y, ESPAI, lvl, lit=0)
            if r[j, i] > 1 - 0.0045 * dens:
                kk = k[j, i]
                cv.flat(x, y, STAR_W if kk > 0.7 else (150, 160, 196) if kk > 0.3 else (96, 96, 130))
                if r[j, i] > 1 - 0.0006 * dens:
                    bright.append((x, y))
    for x, y in bright:
        for dx, dy in ((1, 0), (-1, 0), (0, 1), (0, -1)):
            if (not mask or mask(x + dx, y + dy)) and x0 <= x + dx <= x1 and y0 <= y + dy <= y1:
                cv.flat(x + dx, y + dy, (110, 118, 160))
    return bright

# ─── La paret del fons (z = ZW): el finestral ───────────────────────────────
# El dibuix fa FONS_W × FONS_H; la y del dibuix és YC − y del món (a dalt, el sostre; a baix, la terrassa de dalt).
FONS_W, FONS_H = 900, 186
WIN_Y0, WIN_Y1 = 30, 172                       # els vidres (y del dibuix)
FONS_COLS = (30, 170, 310, 450, 590, 730, 870)  # les columnes adossades (x del dibuix = x del món)
PLANETA = (380, 262, 160)                      # Terra-2: centre i radi (només se'n veu la corba de dalt)
DIPOSIT = (560, 74, 0.72)


def _panes():
    out = []
    for a, b in zip(FONS_COLS, FONS_COLS[1:]):
        out.append((a + 16, b - 16))
    return out


def paret_fons(cv):
    """Marbre, una cornisa d'or i el finestral: l'espai, Terra-2 i el dipòsit entre columnes. → estrelles brillants."""
    n, vv = soroll(FONS_W, FONS_H, 50, 4), venes(FONS_W, FONS_H, 11)
    cv.rect(0, 0, FONS_W - 1, FONS_H - 1, MARB, lambda x, y: 5.4 + (n[y, x] - 0.5) * 0.7 - vv[y, x] * 1.2)
    motllura(cv, 0, FONS_W - 1, 4, h=4, lvl=4.6)
    motllura(cv, 0, FONS_W - 1, 12, MARB, 6.4, h=3)
    motllura(cv, 0, FONS_W - 1, FONS_H - 8, ORP, 4.0, h=3)
    panes = _panes()
    bright = []
    for a, b in panes:
        bright += espai(cv, a, WIN_Y0, b, WIN_Y1, seed=3 + a, dens=1.3)
    cx, cy, r = PLANETA
    terra2(cv, cx, cy, r, mask=lambda x, y: any(a <= x <= b for a, b in panes) and WIN_Y0 <= y <= WIN_Y1)
    dep = Canvas(FONS_W, FONS_H, transparent=True)
    diposit(dep, *DIPOSIT)
    D = dep.img.load()
    for y in range(WIN_Y0, WIN_Y1 + 1):
        for x in range(DIPOSIT[0] - 70, DIPOSIT[0] + 70):
            c = D[x, y]
            if c[3] and any(a <= x <= b for a, b in panes):
                cv.P[x, y] = c[:3] + (255,)
    for a, b in panes:
        vidre(cv, a, WIN_Y0, b, WIN_Y1, k=0.14, seed=a)
        marc_or(cv, a - 3, WIN_Y0 - 3, b + 3, WIN_Y1 + 3, t=3, lvl=4.2)
        cv.hline(a, b, WIN_Y0 + 34, ORP, 3.8)                       # el travesser
        cv.hline(a, b, WIN_Y0 + 35, ORP, 2.4)
        for mx in (a + (b - a) // 3, a + 2 * (b - a) // 3):        # els muntants
            cv.vline(mx, WIN_Y0, WIN_Y1, ORP, 3.6)
            cv.vline(mx + 1, WIN_Y0, WIN_Y1, ORP, 2.2)
    for x in FONS_COLS:
        columna(cv, x, 18, FONS_H - 9, r=9, base_h=12, cap_h=13)
    return bright


# ─── La paret de l'esquerra (x = 0): la porta del saló ──────────────────────
# El dibuix fa ESQ_W × ESQ_H; la x del dibuix és z − ESQ_Z0 del món, la y és YC − y.
ESQ_Z0, ESQ_W, ESQ_H = -300, 860, 270
PORTA = (390, 480, 112)                          # la porta del saló: x0, x1 del dibuix i l'alçada (des de terra)


def paret_esq(cv, porta=PORTA, retol='SALÓ', amplada=ESQ_W, alcada=ESQ_H):
    """Marbre amb plafons d'or, la cornisa, el sòcol i la porta (blanca i or) amb el rètol. També al saló."""
    W_, H_ = amplada, alcada
    n, vv = soroll(W_, H_, 45, 31), venes(W_, H_, 12)
    cv.rect(0, 0, W_ - 1, H_ - 1, MARB, lambda x, y: 4.8 + (n[y, x] - 0.5) * 0.8 - vv[y, x] * 1.2)
    # plafons de marbre amb filet d'or, la cornisa i el sòcol
    for x0 in range(10, W_ - 60, 120):
        if x0 + 100 > porta[0] - 20 and x0 < porta[1] + 20:
            continue
        marc_or(cv, x0, 40, x0 + 96, H_ - 40, t=2, lvl=3.8)
    motllura(cv, 0, W_ - 1, 4, h=4, lvl=4.6)
    motllura(cv, 0, W_ - 1, 12, MARB, 6.4, h=3)
    cv.rect(0, H_ - 14, W_ - 1, H_ - 1, MARB, lambda x, y: 3.6 - (y - H_ + 14) * 0.08)
    motllura(cv, 0, W_ - 1, H_ - 16, ORP, 4.2, h=3)
    # la porta: dues fulles blanques amb plafons, el marc d'or, el frontó i el rètol
    x0, x1, ph = porta
    top = H_ - ph
    cv.rect(x0 - 8, top - 22, x1 + 8, H_ - 1, ORP, lambda x, y: 4.2 - (y - top) * 0.004)
    marc_or(cv, x0 - 8, top - 22, x1 + 8, H_ - 1, t=3, lvl=4.8)
    cv.poly([(x0 - 14, top - 22), (x1 + 14, top - 22), ((x0 + x1) / 2, top - 42)], ORP,
            lambda x, y: 4.6 - (y - top + 42) * 0.03)
    cv.rect(x0 - 16, top - 24, x1 + 16, top - 21, ORP, 5.4)
    mid = (x0 + x1) // 2
    for xa, xb in ((x0, mid - 1), (mid + 1, x1)):
        cv.rect(xa, top, xb, H_ - 2, MARB, lambda x, y: 6.4 - (y - top) * 0.004)
        for ya, yb in ((top + 8, top + ph // 2 - 6), (top + ph // 2 + 4, H_ - 12)):
            marc_or(cv, xa + 6, ya, xb - 6, yb, t=1, lvl=4.2)
            cv.hline(xa + 7, xb - 7, ya + 1, MARB, 7.6)
    cv.vline(mid, top, H_ - 2, MARB, 2.2)
    for hx in (mid - 4, mid + 3):
        cv.rect(hx, top + ph // 2 - 8, hx + 1, top + ph // 2 + 8, ORP, 5.4)
    lletres_c(cv, retol, mid, top - 18, (90, 58, 20))
    # els llums de paret, a banda i banda de la porta
    for lx in (x0 - 36, x1 + 36):
        cv.rect(lx - 3, top + 6, lx + 3, top + 24, ORP, lambda x, y: 4.6 - abs(x - lx) * 0.3)
        cv.disc(lx, top + 2, 6, 7, MARB, lambda nx, ny: 8.6 - ny, lit=0)
        cv.glow(lx, top + 2, 22, (255, 240, 200), 0.35)


# ─── L'aquari ───────────────────────────────────────────────────────────────
AQ_W, AQ_D, AQ_H = 100, 40, 86                  # el vidre: amplada, fondària i alçada
AQ_PEU = 40                                     # l'alçada del peu de marbre
_ST = {'fish_t': 0.0}


def _vidre_aquari(cv, x0, y0, x1, y1):
    for y in range(y0 + 2, y1 + 1):
        for x in range(x0, x1 + 1):
            s = (x - x0) * 1.0 - (y - y0) * 0.35
            if 8 < s % 90 < 13 or 18 < s % 90 < 20:
                cv.flat(x, y, mix(cv.get(x, y), (230, 248, 255), 0.35))


def aquari_vidre(t=0.0, costat=False):
    """El vidre de l'aquari vist de cara (o el del costat, més estret): l'aigua, la sorra, les algues i els peixos."""
    w = AQ_D if costat else AQ_W
    cv = Canvas(w, AQ_H, light=None)
    aigua_aquari(cv, 0, 0, w - 1, AQ_H - 1, t)
    if costat:
        peixos(cv, -30, 0, w + 30, AQ_H - 1, (t + 0.37) % 1.0)
        cv.darken(0, 0, w - 1, AQ_H - 1, 0.25, dither=False)
    else:
        peixos(cv, 0, 0, w - 1, AQ_H - 1, t)
    _vidre_aquari(cv, 0, 0, w - 1, AQ_H - 1)
    for x in (0, w - 1):                                        # els muntants d'or
        cv.vline(x, 0, AQ_H - 1, ORP, 4.6 if x == 0 else 3.4)
    cv.hline(0, w - 1, 0, ORP, 5.4)
    cv.hline(0, w - 1, AQ_H - 1, ORP, 3.2)
    return cv.img


def aquari_peu():
    """El davant del peu de marbre, amb el plafó d'or i el rètol «LOT 12 / DARRERS»."""
    cv = Canvas(AQ_W + 8, AQ_PEU, light=None)
    n = soroll(AQ_W + 8, AQ_PEU, 20, 7)
    cv.rect(0, 0, AQ_W + 7, AQ_PEU - 1, MARB, lambda x, y: 5.8 - y * 0.03 + (n[y, x] - 0.5) * 0.5)
    motllura(cv, 0, AQ_W + 7, 0, h=3, lvl=4.8)
    motllura(cv, 0, AQ_W + 7, AQ_PEU - 4, h=3, lvl=3.6)
    px0, px1, py0, py1 = 22, AQ_W - 14, 9, 30
    cv.rect(px0, py0, px1, py1, ORP, lambda x, y: 5.0 - (y - py0) * 0.08)
    marc_or(cv, px0, py0, px1, py1, t=2, lvl=4.0)
    lletres_c(cv, 'LOT 12', (px0 + px1) // 2, py0 + 4, (60, 34, 12))
    lletres_c(cv, 'DARRERS', (px0 + px1) // 2, py0 + 12, (100, 64, 22))
    return cv.img


# ─── Peces dretes (sprites) ─────────────────────────────────────────────────

def columna_img(h=270, r=14, fosca=0.0):
    """Una columna exempta, blanca i or, de `h` d'alt; `fosca` > 0: en silueta (el primer pla)."""
    w = r * 2 + 14
    cv = Canvas(w, h, light=None, transparent=True)
    columna(cv, w // 2, 0, h - 1, r=r, base_h=18, cap_h=16)
    if fosca:                                                    # en ombra, amb un fil de llum a la vora esquerra
        P = cv.img.load()
        for y in range(h):
            xs = [x for x in range(w) if P[x, y][3]]
            for x in xs:
                c = P[x, y]
                k = 1 - fosca * (0.8 + 0.2 * (x / w))
                if x - xs[0] < 2:
                    k = min(1.0, k + 0.35)
                P[x, y] = (int(c[0] * k), int(c[1] * k * 0.97), int(c[2] * k * 0.95), 255)
    return cv.img, (w // 2, h - 1)


def aranya_img():
    """Un llum d'aranya: la tija d'or, l'anell i els penjolls de vidre que brillen."""
    cv = Canvas(60, 50, light=None, transparent=True)
    x, y1 = 30, 30
    cv.vline(x, 0, y1 - 10, ORP, 4.0)
    cv.disc(x, y1 - 6, 20, 5, ORP, lambda nx, ny: 4.8 - ny * 1.4 - abs(nx) * 0.6)
    cv.disc(x, y1 - 7, 15, 3, ORP, 2.4)
    for k in range(-18, 19, 3):
        h = 8 + int(5 * math.cos(k / 18 * 1.4))
        yy = y1 - 6 + int(5 * math.sqrt(max(0.0, 1 - (k / 20) ** 2)))
        cv.vline(x + k, yy, yy + h, CROM, 5.6 if k % 2 else 4.2)
        cv.flat(x + k, yy + h, (255, 255, 240))
    cv.disc(x, y1 + 8, 4, 5, CROM, lambda nx, ny: 6.0 - nx - ny)
    for k in range(-14, 15, 7):
        cv.disc(x + k, y1 - 10, 1.5, 2.5, MARB, 9.0, lit=0)        # les espelmes
    return cv.img, (30, 0)


# ─── L'aigua de les piscines plenes, vista des de dalt ──────────────────────
# Un mapa del terra (x del món, ZMAP − z del món): cada piscina en retalla el seu tros.
MAPA_W, MAPA_H, ZMAP = 900, 600, 580


def aigua_mapa(rects, frame=0, focus=()):
    """Aigua blava amb ones i reflexos, només dins `rects` = [(x0, z0, x1, z1)] del món (les piscines); els llums
    d'aranya, a `focus` = [(x, z)], hi fan una taca clara. Transparent a la resta."""
    cv = Canvas(MAPA_W, MAPA_H, light=None, transparent=True)
    N = soroll(MAPA_W, MAPA_H, 50, 5)
    ph = frame * 0.8
    for x0, z0, x1, z1 in rects:
        for z in range(int(z0) - 1, int(z1) + 2):
            y = ZMAP - z
            if not 0 <= y < MAPA_H:
                continue
            for x in range(max(0, int(x0) - 1), min(MAPA_W, int(x1) + 2)):
                w = math.sin(x * 0.21 + z * 0.37 + ph) + math.sin(x * 0.07 - z * 0.23 + ph * 1.7)
                v = 3.4 + (N[y, x] - 0.5) * 0.8 + (1.4 if w > 1.55 else 0.6 if w > 1.15 else 0)
                for fx, fz in focus:
                    d = math.hypot(x - fx, (z - fz) * 1.6)
                    if d < 60:
                        v += (1 - d / 60) * 2.2 * (0.6 + 0.4 * math.sin(x * 0.5 + z * 0.9 + ph * 2))
                cv.put(x, y, AIGUA, v, lit=0)
    return cv.img


# ─── Geometria ──────────────────────────────────────────────────────────────

def retalla(poly, x0=2, y0=0, x1=637, y1=257):
    """Sutherland–Hodgman: el polígon (de pantalla) retallat al rectangle (per defecte, la sala on es camina)."""
    def clip(pts, dentro, talla):
        out = []
        for i, P in enumerate(pts):
            Q = pts[i - 1]
            if dentro(P):
                if not dentro(Q):
                    out.append(talla(Q, P))
                out.append(P)
            elif dentro(Q):
                out.append(talla(Q, P))
        return out

    def tx(xc):
        return lambda A, B: (xc, A[1] + (B[1] - A[1]) * (xc - A[0]) / (B[0] - A[0]))

    def ty(yc):
        return lambda A, B: (A[0] + (B[0] - A[0]) * (yc - A[1]) / (B[1] - A[1]), yc)
    pts = [tuple(map(float, p)) for p in poly]
    pts = clip(pts, lambda P: P[0] >= x0, tx(x0))
    pts = clip(pts, lambda P: P[0] <= x1, tx(x1))
    pts = clip(pts, lambda P: P[1] >= y0, ty(y0))
    pts = clip(pts, lambda P: P[1] <= y1, ty(y1))
    out = []
    for x, y in pts:
        q = (round(x), round(y))
        if not out or out[-1] != q:
            out.append(q)
    return out


__all__ = ['FONS_W', 'FONS_H', 'paret_fons', 'paret_esq', 'aquari_vidre', 'aquari_peu', 'columna_img', 'aranya_img',
           'aigua_mapa', 'retalla', 'soroll', 'venes', 'espai']
