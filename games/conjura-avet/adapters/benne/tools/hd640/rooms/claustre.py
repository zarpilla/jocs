"""
La Conjura de l'Avet — `claustre`, el claustre del monestir (actes 1, 2 i 4). Sala «de prop». EN 3D (tres_d), a 1×.

Tarda, després de la pluja: el cel blanc, la gespa molla, les lloses de la galeria amb bassals, i les gotes que cauen
de les teulades (ANIMS `gotes`). La càmera és **dins la galeria**, a prop del mur de dins, i mira al llarg de la
galeria, una mica cap a l'esquerra (cap a la gespa) i avall:
  - a l'esquerra, l'arcada: l'ampit de pedra i les **columnes** primes i fosques amb els capitells, i els arcs
    apuntats; les dues de més a prop, en primer pla (FRONT), tallades per la vora;
  - a través dels arcs, la **gespa**, la **pica** de pedra al mig, la galeria del davant (arcs de mig punt, blanc
    trencat, teula) i, al fons, el **campanar**;
  - a dalt, el sostre de fusta amb les bigues que fugen;
  - a la dreta, el mur de dins (arrebossat blanc, sòcol de gres): la **porta_monestir** (a prop), el **banc** de
    pedra de l'abadessa, la **porta_bugaderia** i la **porta_apotecaria**; al fons de la galeria, la
    **porta_capitular** tancada, amb el paper de l'inspecció i el segell vermell del jutge.

Decorats a pantalla completa: `llum_capvespre` (acte 2: el cel blau fosc, la gespa blava, llums d'oli a les
columnes) i `llum_mati` (acte 4: sol net, les ombres de les columnes en diagonal pel terra). El `morter` de la
Gueraula és un prop (damunt el banc).

El món: x a la dreta (0 = la cara de dins de l'ampit), y amunt (0 = el terra), z cap al fons (420 = la paret del
fons de la galeria); 1 unitat = 1 px de sala a l'escala 1 dels personatges (l'Iri hi fa 84 px).
"""
import functools
import math

import numpy as np
from PIL import Image

from hd.pix import Canvas, Light
from hd640.tres_d import Camera, Escena, Llum
from hd640.rooms.claustre_comu import (
    ajusta_geometria,
    W, H, RH, GRES, BLANC, COLUMNA, LLOSA, FUSTA, TEULA, GESPA, CELB, FERRO, CERA, PERGAMI, FOC, nz, fbm, hr, smooth,
    diferencia, sense_hud, fosc_hud, mascara_amo, retalla, escala_v, lletres, ample)

CAM = Camera(pos=(70, 128, -330), yaw=-0.14, pitch=0.06, f=410, centre=(326, 104))

XI = 240                                          # el mur de dins de la galeria
ZF = 420                                          # la paret del fons de la galeria
ZN = -420                                         # (la galeria continua darrere la càmera)
AMPIT = (-16, 0, 34)                              # l'ampit: x0, x1, alçada
COLS = [-250 + 90 * k for k in range(8)]          # les columnes (z), damunt l'ampit, a x = -8
XC = -8
FUST = (34, 40, 118, 128)                         # basa (y0, y1), fust fins a y2, capitell fins a y3
APEX = 156                                        # la clau dels arcs
MUR_ARC = 178                                     # dalt del mur de l'arcada (comença el sostre)
SOSTRE_I = 214                                    # el sostre, al mur de dins
HF = 214                                          # l'alçada de les façanes del davant (amb el pis de dalt)
GX0, GZ0, GZ1 = -440, -420, 400                   # la gespa: x0 (la galeria de l'esquerra), z0, z1 (la del fons)
PICA = (-200, 120)                                # la pica (x, z)
CAMPANAR = (-600, -530, 560, 630, 320)            # x0, x1, z0, z1, alçada
BANC = (208, 240, 0, 20, 70, 150)                 # x0, x1, y0, y1, z0, z1 (el banc de pedra, contra el mur)
P_MONESTIR = (-24, 44, 132)                       # porta: z0, z1, alçada (al mur de dins)
P_BUGADERIA = (184, 246, 116)
P_APOTECARIA = (176, 222, 104)                 # x0, x1, alçada (a la paret del fons)
P_CAPITULAR = (40, 132, 140)                      # x0, x1, alçada (a la paret del fons)
MORTER = (224, 128)                               # x, z (damunt el banc)

LIGHT = Light(ambient=0.0, vignette=None, floor_fade=None)


# ─── Els modes de llum ──────────────────────────────────────────────────────

class Mode:
    """La llum de cada moment: `tarda` (la base, després de la pluja), `capvespre` (acte 2), `mati` (acte 4)."""

    def __init__(self, nom):
        self.nom = nom
        if nom == 'capvespre':
            self.cel = [(18, 22, 44), (26, 32, 62), (40, 48, 84), (60, 66, 104), (90, 86, 118), (130, 110, 126)]
            self.gespa = [(10, 22, 30), (16, 34, 44), (24, 48, 60), (32, 62, 76), (42, 78, 92), (54, 94, 106),
                          (70, 110, 120), (90, 128, 134)]
            self.ambient, self.k_tex = -1.3, 0.62
            self.llums = [Llum((-260, 260, 100), 900, 0.6, power=1.0)]
        elif nom == 'mati':
            self.cel = [(96, 142, 196), (118, 160, 208), (140, 178, 218), (164, 196, 228), (190, 214, 236),
                        (214, 230, 242)]
            self.gespa = [(14, 30, 10), (22, 46, 14), (32, 66, 18), (46, 88, 22), (64, 112, 28), (86, 136, 36),
                          (112, 160, 48), (146, 184, 70)]
            self.ambient, self.k_tex = 0.3, 1.08
            self.llums = [Llum((-320, 380, -60), 1100, 2.2, power=0.8)]
        else:
            self.cel = CELB
            self.gespa = GESPA
            self.ambient, self.k_tex = -0.2, 0.92
            self.llums = [Llum((-260, 320, 60), 1000, 1.6, power=0.9)]


# ─── Els dibuixos plans (textures) ───────────────────────────────────────────

def _arrebossat(cv, x0, y0, x1, y1, base, seed, ramp=BLANC):
    """Una paret arrebossada (blanc trencat), amb taques d'humitat i el desgast."""
    for y in range(y0, y1):
        for x in range(x0, x1):
            n = fbm(x / 26, y / 20, seed)
            lvl = base + (n - 0.5) * 1.1 + (nz(x / 4, y / 4, seed + 3) - 0.5) * 0.35
            cv.put(x, y, ramp, lvl, lit=0)


def _carreus(cv, x0, y0, x1, y1, base, seed, hc=14, wc=30, ramp=GRES):
    """Carreus de gres (rosat i ocre): filades de `hc`, peces de `wc`, juntes fosques."""
    for y in range(y0, y1):
        fila = (y - y0) // hc
        for x in range(x0, x1):
            off = (fila % 2) * wc // 2
            peca = (x - x0 + off) // wc
            lvl = base + (hr(peca & 255, fila & 255, seed) - 0.5) * 1.2 + (nz(x / 5, y / 5, seed) - 0.5) * 0.6
            if (y - y0) % hc == 0 or (x - x0 + off) % wc == 0:
                lvl -= 1.4
            cv.put(x, y, ramp, lvl, lit=0)


def _arc_mig_punt(cx, y_imposta, r):
    """→ fn(x, y): dins l'obertura d'un arc de mig punt de centre cx, que arrenca a y_imposta (cap avall, obert)."""
    def dins(x, y):
        if abs(x - cx) > r:
            return False
        if y >= y_imposta:
            return True
        return math.hypot(x - cx, y - y_imposta) <= r
    return dins


def _facana_galeria(w, h, pas, seed, arcs=True, finestres=True):
    """La façana d'una galeria del davant (vista de cara): l'ampit de gres, les columnetes i els arcs de mig punt
    (dins, l'ombra de la galeria i alguna porta), el mur blanc a sobre, el ràfec i la teulada (a dalt de tot, la
    paret del pis de dalt, amb finestres). w×h; y = h − alçada."""
    cv = Canvas(w, h)
    sol = h                                       # el terra
    ampit, imposta, r = 30, 96, pas * 0.4
    teula0, teula1 = h - 146, h - 168
    # el pis de dalt (el que sobresurt per damunt la teulada)
    _carreus(cv, 0, 0, w, teula1, 3.6, seed + 1, hc=12, wc=26)
    if finestres:
        for k, fx in enumerate(range(30, w - 20, 74)):
            if hr(k, seed, 3) < 0.7:
                cv.rect(fx, teula1 - 44, fx + 12, teula1 - 22, FUSTA, 1.2, lit=0)
                cv.rect(fx - 1, teula1 - 45, fx + 13, teula1 - 45, GRES, 6.0, lit=0)
    # la teulada (de cara: filades de teula)
    for y in range(teula1, teula0):
        for x in range(w):
            t = (y - teula1) / max(1, teula0 - teula1)
            lvl = 3.4 + t * 1.0 + (0.6 if (x + (y // 4) * 6) % 12 < 6 else -0.2) - (1.0 if y % 4 == 0 else 0)
            lvl += (hr(x // 6, y // 4, seed) - 0.5) * 0.8
            cv.put(x, y, TEULA, lvl, lit=0)
    cv.rect(0, teula0, w - 1, teula0 + 2, TEULA, 1.4, lit=0)         # el ràfec (l'ombra)
    # el mur blanc de l'arcada
    _arrebossat(cv, 0, teula0 + 3, w, sol, 5.6, seed + 2)
    # els arcs: dins, l'ombra de la galeria
    if arcs:
        for k, cx in enumerate(np.arange(pas / 2, w, pas)):
            dins = _arc_mig_punt(cx, h - imposta, r)
            for y in range(int(h - imposta - r - 1), h - ampit):
                for x in range(int(cx - r - 1), int(cx + r + 2)):
                    if 0 <= x < w and dins(x, y):
                        prof = (y - (h - imposta - r)) / (r + imposta - ampit)
                        lvl = 1.6 + prof * 0.8 + (nz(x / 6, y / 6, seed) - 0.5) * 0.4
                        cv.put(x, y, BLANC, lvl, lit=0)
            # una porta o una finestra al fons de la galeria, a vegades
            if hr(k, seed, 9) < 0.4:
                cv.rect(cx - 7, h - ampit - 52, cx + 7, h - ampit - 1, FUSTA, 1.4, lit=0)
            # la columneta (fosca) entre arc i arc, amb el capitell
            xc = cx + pas / 2
            if xc < w - 2:
                cv.rect(xc - 2, h - imposta + 6, xc + 2, h - ampit, COLUMNA, lambda x, y: 2.6 - (x - xc) * 0.3, lit=0)
                cv.rect(xc - 5, h - imposta, xc + 5, h - imposta + 5, COLUMNA, 3.2, lit=0)
                cv.rect(xc - 4, h - ampit - 4, xc + 4, h - ampit, COLUMNA, 3.0, lit=0)
            # la rosca de l'arc (una mica més clara)
            for a in range(0, 181, 2):
                x = cx + math.cos(math.radians(a)) * (r + 1)
                y = h - imposta - math.sin(math.radians(a)) * (r + 1)
                cv.put(x, y, GRES, 6.4, lit=0)
    # l'ampit de gres
    _carreus(cv, 0, h - ampit, w, sol, 4.6, seed + 5, hc=11, wc=24)
    cv.rect(0, h - ampit, w - 1, h - ampit + 1, GRES, 6.4, lit=0)
    return cv.img


def _mur_dins():
    """El mur de dins de la galeria, vist de cara: (ZF − ZN) × 240 (x = ZF − z, y = 240 − alçada). L'arrebossat blanc
    amb el sòcol de gres, i les portes: la del monestir (de fusta, amb ferros), la de la bugaderia i la de
    l'apotecaria (més petites), i un rètol de pedra damunt la del monestir."""
    w, h = ZF - ZN, 240
    cv = Canvas(w, h)
    _arrebossat(cv, 0, 0, w, h, 5.0, 21)
    _carreus(cv, 0, h - 26, w, h, 4.0, 22, hc=13, wc=34)
    for z0, z1, ph, fosca in (P_MONESTIR + (0,), P_BUGADERIA + (1,)):
        x0, x1 = ZF - z1, ZF - z0
        # el marc de gres, amb arc de mig punt
        r = (x1 - x0) / 2
        cx, ya = (x0 + x1) / 2, h - ph + r
        for y in range(int(h - ph - 8), h):
            for x in range(int(x0 - 8), int(x1 + 9)):
                d = math.hypot(x - cx, y - ya) if y < ya else abs(x - cx)
                if d <= r + 7:
                    if d <= r:
                        # la porta: posts de fusta i ferros
                        lvl = 2.6 - fosca * 0.4 + (0.5 if int(x - x0) % 9 == 0 else 0) - (0.7 if int(x - x0) % 9 == 8 else 0)
                        lvl += (nz(x / 3, y / 14, 5) - 0.5) * 0.6
                        cv.put(x, y, FUSTA, lvl, lit=0)
                    else:
                        cv.put(x, y, GRES, 5.0 + (hr(int(math.atan2(y - ya, x - cx) * 5) & 255, 3) - 0.5) * 0.8
                               - (1.2 if d - r < 1.2 else 0), lit=0)
        for fy in (h - ph * 0.35, h - ph * 0.7):                    # les frontisses
            cv.rect(x0 + 1, fy, x0 + r * 1.2, fy + 2, FERRO, 2.6, lit=0)
        cv.disc(x1 - 7, h - ph * 0.45, 2.2, 2.2, FERRO, 4.0, lit=0)  # la baula
    # un forat a la paret per a una llàntia (fosc), entre portes
    for z in (80, 290):
        x = ZF - z
        cv.rect(x - 5, h - 150, x + 5, h - 136, BLANC, 2.4, lit=0)
    # taques d'humitat a baix (la pluja)
    for y in range(h - 60, h - 26):
        for x in range(w):
            if fbm(x / 30, y / 10, 31) > 0.62 - (y - (h - 60)) / 34 * 0.12:
                cv.P[x, y] = tuple(int(c * 0.84) for c in cv.P[x, y][:3]) + (255,)
    return cv.img


def _paret_fons():
    """La paret del fons de la galeria (x 0..XI, y = 240 − alçada): la porta de la sala capitular, tancada, amb el
    paper de l'inspecció clavat i el segell vermell del jutge damunt la clau."""
    w, h = XI, 240
    cv = Canvas(w, h)
    _arrebossat(cv, 0, 0, w, h, 4.6, 41)
    _carreus(cv, 0, h - 26, w, h, 3.8, 42, hc=13, wc=34)
    x0, x1, ph = P_CAPITULAR
    r = (x1 - x0) / 2
    cx, ya = (x0 + x1) / 2, h - ph + r
    for y in range(int(h - ph - 10), h):
        for x in range(int(x0 - 10), int(x1 + 11)):
            d = math.hypot(x - cx, y - ya) if y < ya else abs(x - cx)
            if d <= r + 9:
                if d <= r:
                    lvl = 2.4 + (0.5 if int(x - x0) % 12 == 0 else 0) - (0.8 if int(x - x0) % 12 == 11 else 0)
                    lvl += (nz(x / 3, y / 16, 6) - 0.5) * 0.6
                    if abs(x - cx) < 1:
                        lvl = 0.6                                          # les dues fulles
                    cv.put(x, y, FUSTA, lvl, lit=0)
                else:
                    # les dovelles de l'arc, alternades
                    a = int((math.atan2(y - ya, x - cx) + math.pi) * 6)
                    cv.put(x, y, GRES, 4.4 + (a % 2) * 0.8 - (1.2 if d - r < 1.2 else 0), lit=0)
    # la porta de l'apotecaria (més petita, d'una fulla, amb un ram d'herbes penjat al costat)
    q0, q1, qh = P_APOTECARIA
    qr = (q1 - q0) / 2
    qx, qy = (q0 + q1) / 2, h - qh + qr
    for y in range(int(h - qh - 7), h):
        for x in range(int(q0 - 7), int(q1 + 8)):
            d = math.hypot(x - qx, y - qy) if y < qy else abs(x - qx)
            if d <= qr + 6:
                if d <= qr:
                    lvl = 2.2 + (0.5 if int(x - q0) % 8 == 0 else 0) - (0.7 if int(x - q0) % 8 == 7 else 0)
                    cv.put(x, y, FUSTA, lvl + (nz(x / 3, y / 14, 8) - 0.5) * 0.6, lit=0)
                else:
                    cv.put(x, y, GRES, 4.8 - (1.2 if d - qr < 1.2 else 0), lit=0)
    cv.disc(q0 + 6, h - qh * 0.45, 2, 2, FERRO, 4.0, lit=0)
    for k in range(7):                                                   # el ram de sàlvia
        cv.line(q1 + 12, h - qh + 30, q1 + 9 + k, h - qh + 46 + (k % 3) * 2, [(40, 60, 34), (70, 96, 56), (110, 130, 84)],
                1.2 + (k % 2), lit=0)
    cv.rect(q1 + 10, h - qh + 28, q1 + 14, h - qh + 31, FUSTA, 3.0, lit=0)
    for fy in (h - ph * 0.25, h - ph * 0.6):
        cv.rect(x0 + 2, fy, cx - 4, fy + 2, FERRO, 2.6, lit=0)
        cv.rect(cx + 4, fy, x1 - 2, fy + 2, FERRO, 2.6, lit=0)
    # el paper de l'inspecció i el segell
    px0, py0 = cx - 18, h - ph * 0.62
    cv.rect(px0, py0, px0 + 36, py0 + 30, PERGAMI, lambda x, y: 4.6 - (y - py0) * 0.02, lit=0)
    for k, ly in enumerate(range(int(py0) + 4, int(py0) + 24, 4)):
        cv.rect(px0 + 4, ly, px0 + 31 - (k * 5) % 11, ly, FUSTA, 1.0, lit=0)
    cv.disc(cx, py0 + 31, 4.5, 4.5, CERA, lambda nx, ny: 3.4 - ny * 0.8 - nx * 0.6, lit=0)   # el segell vermell
    cv.rect(cx - 1, py0 + 34, cx + 1, py0 + 40, CERA, 2.4, lit=0)                          # la cinta
    # la cadena a les baules
    for k in range(9):
        cv.disc(cx - 8 + k * 2, h - ph * 0.42 + (k - 4) ** 2 * 0.25, 1.2, 1.2, FERRO, 4.0 if k % 2 else 3.0, lit=0)
    return cv.img


def _arcada():
    """El mur de l'arcada vist des de dins (x = ZF − z, y = MUR_ARC − alçada; de y = FUST[3] fins a MUR_ARC), amb
    els arcs apuntats transparents entre columna i columna."""
    w, h = ZF - ZN, MUR_ARC - FUST[3]
    cv = Canvas(w, h, transparent=True)
    _arrebossat(cv, 0, 0, w, h, 5.2, 51)
    P = cv.P
    zs = COLS + [ZF]
    for za, zb in zip([ZN] + zs, zs):
        if zb - za > 120:                           # (darrere la càmera: no cal)
            za = zb - 90
        cx = ZF - (za + zb) / 2
        half = (zb - za) / 2 - 5
        # arc apuntat: dos arcs de radi R amb el centre a l'altre costat
        R = half * 1.6
        hcl = APEX - FUST[3]
        for y in range(h):
            alt = MUR_ARC - y - FUST[3]                # alçada damunt el capitell
            for x in range(int(cx - half - 1), int(cx + half + 2)):
                if not 0 <= x < w:
                    continue
                dx = abs(x - cx)
                # l'alçada de l'intradós a aquella distància del mig
                cxx = half - R                          # el centre del cercle (al costat contrari)
                yy = math.sqrt(max(0.0, R * R - (dx - cxx) ** 2)) - math.sqrt(max(0.0, R * R - (half - cxx) ** 2))
                lim = yy * hcl / max(1e-3, math.sqrt(R * R - cxx * cxx) - math.sqrt(max(0.0, R * R - (half - cxx) ** 2)))
                if dx <= half and alt <= lim:
                    P[x, y] = (0, 0, 0, 0)
                elif dx <= half + 6 and alt <= lim + 7:
                    # la rosca de l'arc: dovelles de gres
                    a = int(math.atan2(alt, x - cx) * 9)
                    lvl = 4.6 + (a % 2) * 0.5 - (1.2 if alt > lim + 5.5 or dx > half + 4.5 else 0)
                    cv.put(x, y, GRES, lvl, lit=0)
    return cv.img


def _sostre_fn(s, t, P):
    """El sostre de fusta: les posts (al llarg de x) i les bigues que creuen (cada 44 de z)."""
    x, z = P[0], P[2]
    lvl = 2.6 + (nz(x / 30, z / 6, 61) - 0.5) * 0.6
    if (z + 1000) % 44 < 7:
        lvl += 1.2 if (z + 1000) % 44 < 2 else 0.5
    elif int(z + 1000) % 11 == 0:
        lvl -= 0.8
    return lvl


def _terra_fn(s, t, P):
    """Les lloses de la galeria: grans, desiguals, gastades al mig; molles i més clares (el cel) a prop de l'arcada."""
    x, z = P[0], P[2]
    fila = int((z + 1000) // 46)
    off = (fila % 3) * 23
    peca = int((x + off + 1000) // 70)
    lvl = 3.4 + (hr(peca & 255, fila & 255, 71) - 0.5) * 1.0 + (nz(x / 9, z / 9, 72) - 0.5) * 0.5
    if (z + 1000) % 46 < 1.6 or (x + off + 1000) % 70 < 1.6:
        lvl -= 1.3
    return lvl


def _gespa_fn(mode):
    def fn(s, t, P):
        x, z = P[0], P[2]
        lvl = 3.4 + (fbm(x / 40, z / 40, 81) - 0.5) * 1.2 + (nz(x / 2.5, z / 1.5, 82) - 0.5) * 0.9
        # el camí de lloses que va a la pica
        if abs(z - PICA[1]) < 10 and x > PICA[0]:
            lvl -= 0.4
        return lvl
    return fn


# ─── L'escena ────────────────────────────────────────────────────────────────

def _cel(cv, mode):
    for y in range(RH):
        for x in range(W):
            t = y / 200
            n = fbm(x / 90, y / 30, 91)
            cv.put(x, y, mode.cel, 4.6 - t * 1.2 + (n - 0.5) * 1.6, lit=0)


@functools.lru_cache(maxsize=None)
def _textures():
    return (_facana_galeria(-16 - GX0, HF, 84, 101), _facana_galeria(GZ1 - GZ0, HF, 84, 111),
            _mur_dins(), _paret_fons(), _arcada())


def _pica_img(mode):
    """La pica de pedra (dibuix pla, 74×40): un bol ample de vores gruixudes, amb l'aigua de la pluja a dins."""
    w, h = 76, 42
    cv = Canvas(w, h, transparent=True)
    cx = w / 2
    for y in range(10, h):
        t = (y - 10) / (h - 10)
        half = 36 - t * t * 14
        for x in range(int(cx - half), int(cx + half) + 1):
            nx = (x - cx) / half
            cv.put(x, y, LLOSA, 4.0 - nx * 1.4 - t * 1.0 + (nz(x / 3, y / 3, 3) - 0.5) * 0.9, lit=0)
    cv.disc(cx, 10, 36, 8, LLOSA, lambda nx, ny: 6.0 - nx * 0.6, lit=0)             # la vora
    aigua = [(30, 34, 40), (60, 66, 74), (100, 106, 112), (150, 156, 160)] if mode.nom != 'capvespre' else \
        [(10, 14, 26), (20, 26, 44), (36, 44, 66), (60, 70, 96)]
    cv.disc(cx, 10, 30, 5.5, aigua, lambda nx, ny: 1.4 - ny * 1.2 + (0.8 if abs(nx + 0.3) < 0.1 else 0), lit=0)
    return cv.img


def _morter_img():
    """El morter de la Gueraula (de pedra fosca, amb la mà de fusta), 20×18."""
    cv = Canvas(22, 22, transparent=True)
    for y in range(8, 21):
        t = (y - 8) / 12
        half = 9 - t * 3
        for x in range(int(11 - half), int(11 + half) + 1):
            cv.put(x, y, FERRO, 4.2 - (x - 11) / half * 1.2 - t, lit=0)
    cv.disc(11, 8, 9, 3, FERRO, lambda nx, ny: 2.0 + ny, lit=0)
    cv.disc(11, 8, 7, 2, [(40, 60, 30), (60, 90, 40), (90, 120, 56)], 1.2, lit=0)  # les herbes picades
    cv.line(13, 7, 19, 0, FUSTA, 6.0, lit=0)
    cv.line(14, 7, 20, 0, FUSTA, 4.4, lit=0)
    return cv.img


def _llantia_img(on):
    """Una llàntia d'oli penjada d'un clau a la columna (12×18): el plat de fang, el bec i la flama."""
    cv = Canvas(14, 20, transparent=True)
    cv.line(7, 0, 7, 8, FERRO, 2.0, lit=0)
    cv.disc(7, 12, 6, 3, [(70, 40, 24), (110, 66, 36), (150, 96, 52)], lambda nx, ny: 1.4 - ny, lit=0)
    if on:
        cv.disc(11, 8, 1.6, 3.2, FOC, lambda nx, ny: 5.6 - ny * 1.4, lit=0)
    return cv.img


def escena(cv, mode, morter=False):
    tex_fons, tex_esq, mur, paret, arcada = _textures()
    e = Escena(cv, CAM, mode.llums, ambient=mode.ambient)
    _cel(cv, mode)
    # el campanar (al fons, darrere la galeria del fons)
    x0, x1, z0, z1, hc = CAMPANAR

    def camp_fn(s, t, P):
        x, y, z = P
        fila = int(y // 12)
        peca = int((x + z + (fila % 2) * 12) // 24)
        lvl = 3.4 + (hr(peca & 255, fila & 255, 5) - 0.5) * 1.0
        if y % 12 < 1.4:
            lvl -= 1.0
        # les obertures del campanar (dos arcs per cara), a dalt
        u = (x - x0) if abs(z - z0) < 1 else (z - z0)
        if hc - 70 < y < hc - 22:
            for c in (22, 58):
                if abs(u - c) < 9 and (y < hc - 31 or abs(u - c) < math.sqrt(max(0.0, 81 - (y - (hc - 31)) ** 2))):
                    return 0.2
        if y > hc - 8:
            lvl += 0.6
        return lvl
    e.caixa('campanar', x0, x1, 0, hc, z0, z1, GRES, 3.4,
            cares={'davant': {'ramp': GRES, 'lvl': camp_fn}, 'dreta': {'ramp': GRES, 'lvl': lambda s, t, P: camp_fn(s, t, P) - 1.0},
                   'dalt': {'ramp': TEULA, 'lvl': 3.0}})
    # el teulat del campanar (piràmide baixa)
    cx, cz = (x0 + x1) / 2, (z0 + z1) / 2
    e.quad('campanar', (x0 - 6, hc, z0 - 6), (x1 + 6, hc, z0 - 6), (cx + 1, hc + 34, cz), (cx - 1, hc + 34, cz),
           ramp=TEULA, lvl=3.6, dues_cares=True)
    e.quad('campanar', (x1 + 6, hc, z0 - 6), (x1 + 6, hc, z1 + 6), (cx, hc + 34, cz + 1), (cx, hc + 34, cz - 1),
           ramp=TEULA, lvl=2.6, dues_cares=True)
    # les galeries del davant: la del fons (z = GZ1) i la de l'esquerra (x = GX0)
    e.quad('galeria_fons', (GX0, HF, GZ1), (-16, HF, GZ1), (-16, 0, GZ1), (GX0, 0, GZ1),
           tex=(tex_fons, (0, 0, -16 - GX0, HF)))
    e.quad('galeria_esq', (GX0, HF, GZ0), (GX0, HF, GZ1), (GX0, 0, GZ1), (GX0, 0, GZ0),
           tex=(tex_esq, (0, 0, GZ1 - GZ0, HF)))
    # la gespa
    e.quad('gespa', (GX0, -1, GZ1), (-16, -1, GZ1), (-16, -1, GZ0), (GX0, -1, GZ0), ramp=mode.gespa,
           lvl=_gespa_fn(mode))
    # la vora de lloses de la gespa (al peu de les galeries) i el rotllo de lloses de la pica
    px, pz = PICA
    e.quad('gespa', (px - 60, -0.6, pz + 40), (px + 60, -0.6, pz + 40), (px + 60, -0.6, pz - 40), (px - 60, -0.6, pz - 40),
           ramp=LLOSA, lvl=lambda s, t, P: 4.0 + (nz(P[0] / 5, P[2] / 5, 3) - 0.5) * 0.8
           - (1.0 if int(math.degrees(math.atan2(P[2] - pz, P[0] - px))) % 30 < 3 else 0),
           forma=lambda s, t: math.hypot((s - 60) / 60, (t - 40) / 40) <= 1)
    e.foscor('ombra_pica', (px - 50, -0.4, pz + 20), (px + 70, -0.4, pz + 20), (px + 70, -0.4, pz - 30),
             (px - 50, -0.4, pz - 30), lambda s, t: 0.4 * max(0.0, 1 - math.hypot((s - 66) / 52, (t - 28) / 20)))
    e.sprite('pica', _pica_img(mode), (38, 41), (px, 0, pz), escala_img=1.2)
    # el sostre de fusta de la galeria
    e.quad('sostre', (-16, MUR_ARC, ZF), (XI, SOSTRE_I, ZF), (XI, SOSTRE_I, ZN), (-16, MUR_ARC, ZN), ramp=FUSTA,
           lvl=_sostre_fn, dues_cares=True)
    # la paret del fons i el mur de dins
    e.quad('paret_fons', (0, 240, ZF), (XI, 240, ZF), (XI, 0, ZF), (0, 0, ZF), tex=(paret, (0, 0, XI, 240)))
    e.quad('mur_dins', (XI, 240, ZF), (XI, 240, ZN), (XI, 0, ZN), (XI, 0, ZF), tex=(mur, (0, 0, ZF - ZN, 240)))
    # el terra de la galeria
    e.quad('terra', (0, 0, ZF), (XI, 0, ZF), (XI, 0, ZN), (0, 0, ZN), ramp=LLOSA, lvl=_terra_fn)
    # el banc de pedra, contra el mur
    bx0, bx1, by0, by1, bz0, bz1 = BANC
    e.foscor('ombra_banc', (bx0 - 16, 0.3, bz1 + 4), (XI, 0.3, bz1 + 4), (XI, 0.3, bz0 - 10), (bx0 - 16, 0.3, bz0 - 10),
             lambda s, t: 0.5 * smooth(0, 16, s))
    e.caixa('banc', bx0, bx1, by0, by1, bz0, bz1, GRES, 3.6,
            cares={'dalt': {'ramp': GRES, 'lvl': lambda s, t, P: 5.0 + (nz(P[0] / 4, P[2] / 6, 9) - 0.5) * 0.8},
                   'esquerra': {'ramp': GRES, 'lvl': lambda s, t, P: 3.4 - (1.0 if int(P[2]) % 34 < 2 else 0)},
                   'davant': {'ramp': GRES, 'lvl': 2.6}})
    if morter:
        e.sprite('morter', _morter_img(), (11, 20), (MORTER[0], by1, MORTER[1]))
    # l'ombra als racons (el terra amb el mur, amb l'ampit) i l'aigua de la pluja al costat de l'arcada
    e.foscor('ombra_mur', (XI - 22, 0.2, ZF), (XI, 0.2, ZF), (XI, 0.2, ZN), (XI - 22, 0.2, ZN),
             lambda s, t: 0.35 * smooth(0, 22, s))
    e.foscor('ombra_fons', (0, 0.2, ZF), (XI, 0.2, ZF), (XI, 0.2, ZF - 30), (0, 0.2, ZF - 30),
             lambda s, t: 0.35 * (1 - t / 30))
    if mode.nom != 'capvespre':
        llum_cel = (226, 230, 232) if mode.nom == 'tarda' else (250, 236, 200)
        e.claror((0, 0.3, ZF), (40, 0.3, ZF), (40, 0.3, ZN), (0, 0.3, ZN), llum_cel,
                 lambda s, t: (0.28 if mode.nom == 'tarda' else 0.18) * (1 - s / 40)
                 * (1.0 if fbm(s / 8, t / 12, 7) > 0.45 else 0.35))
    # l'ampit
    a0, a1, ah = AMPIT
    e.caixa('ampit', a0, a1, 0, ah, ZN, ZF, GRES, 3.6,
            cares={'dalt': {'ramp': GRES, 'lvl': lambda s, t, P: 5.2 + (nz(P[2] / 8, P[0] / 3, 11) - 0.5) * 0.8},
                   'dreta': {'ramp': GRES, 'lvl': lambda s, t, P: 3.4 + (hr(int(P[2] + 1000) // 32 & 255, int(P[1]) // 12, 4) - 0.5) * 0.9
                             - (1.2 if (P[2] + 1000) % 32 < 1.5 or P[1] % 12 < 1 else 0)}})
    # el mur de l'arcada (amb els arcs apuntats), amb una segona pell més fosca darrere: el gruix de l'arc
    y3 = FUST[3]
    e.quad('arcada_gruix', (-16, MUR_ARC, ZN), (-16, MUR_ARC, ZF), (-16, y3, ZF), (-16, y3, ZN),
           tex=(arcada, (ZF - ZN, 0, 0, MUR_ARC - y3)), ombra=lambda s, t: 0.35, dues_cares=True)
    e.quad('arcada', (0, MUR_ARC, ZF), (0, MUR_ARC, ZN), (0, y3, ZN), (0, y3, ZF), tex=(arcada, (0, 0, ZF - ZN, MUR_ARC - y3)),
           dues_cares=True)
    # les columnes: la basa, el fust prim i fosc, el capitell
    for z in COLS:
        sid = 'columna_davant' if z < -100 else 'columna'
        b0, b1, f2, c3 = FUST
        e.caixa(sid, XC - 6, XC + 6, b0, b1, z - 6, z + 6, COLUMNA, 3.0,
                cares={'dalt': {'ramp': COLUMNA, 'lvl': 4.2}, 'dreta': {'ramp': COLUMNA, 'lvl': 3.0},
                       'davant': {'ramp': COLUMNA, 'lvl': 2.2}})
        e.tub(sid, (XC, b1, z), (XC, f2, z), 3.6, COLUMNA, 2.6, llum_dir=(-0.8, -0.2))
        e.caixa(sid, XC - 5, XC + 5, f2 - 3, f2, z - 5, z + 5, COLUMNA, 3.6)     # l'astràgal
        e.caixa(sid, XC - 5, XC + 5, f2, f2 + 4, z - 5, z + 5, COLUMNA, 3.0)
        e.caixa(sid, XC - 7, XC + 7, f2 + 4, c3, z - 7, z + 7, COLUMNA, 3.0,
                cares={'dreta': {'ramp': COLUMNA, 'lvl': lambda s, t, P: 3.0 + (1.6 if nz(P[1] / 1.6, P[2] / 1.6, 5) > 0.55 else 0)
                                 - (0.8 if P[1] < FUST[2] + 6 else 0)},
                       'davant': {'ramp': COLUMNA, 'lvl': lambda s, t, P: 2.2 + (1.4 if nz(P[1] / 1.6, P[0] / 1.6, 6) > 0.55 else 0)},
                       'sota': {'ramp': COLUMNA, 'lvl': 1.0}})
    return e


@functools.lru_cache(maxsize=None)
def _render(nom='tarda', morter=False):
    mode = Mode(nom)
    cv = Canvas(W, H, light=LIGHT)
    e = escena(cv, mode, morter)
    if nom == 'capvespre':
        _llum_oli(cv, e)
    elif nom == 'mati':
        _sol_mati(cv, e)
    img = fosc_hud(cv.img)
    return img, e


def _llum_oli(cv, e):
    """El capvespre: tota l'escena cap al blau fosc, i les llànties d'oli de les columnes, amb un bassal càlid al
    voltant de cada una (a l'ampit, el terra i els capitells)."""
    a = np.asarray(cv.img.convert('RGBA')).astype(np.float32)
    yy, xx = np.mgrid[0:H, 0:W]
    fosc = np.ones((H, W), np.float32)
    llums = [z for z in COLS if -100 < z < ZF]
    for z in llums:
        u, v, _ = CAM.projecta((XC + 10, FUST[2] - 14, z))
        s = CAM.escala((XC, 0, z))
        r = 120 * s
        d = np.hypot((xx - u) / r, (yy - v) / (r * 0.9))
        fosc *= 1 - np.clip(1 - d, 0, 1) ** 1.3 * min(1.0, 0.55 + s * 0.4)
    k = (1 - fosc)[..., None]
    nit = np.array([0.40, 0.45, 0.64], np.float32)
    calid = np.array([1.10, 0.86, 0.58], np.float32)
    a[..., :3] = a[..., :3] * (nit * (1 - k) + calid * k)
    cv.img.paste(Image.fromarray(a.clip(0, 255).astype(np.uint8), 'RGBA'))
    cv.P = cv.img.load()
    for z in llums:
        e.sprite('llantia', _llantia_img(True), (7, 0), (XC + 10, FUST[2] - 10, z), escala_img=1.0)


def _sol_mati(cv, e):
    """El sol del matí entra per l'esquerra, per sobre la gespa: les ombres de les columnes cauen en diagonal pel terra
    de la galeria i pugen pel mur de dins; entre columna i columna, el terra s'encén."""
    d = (0.55, -0.62, 0.56)                           # la direcció del sol (cap on va la llum)

    def a_terra(P):
        t = -P[1] / d[1]
        return (P[0] + d[0] * t, P[2] + d[2] * t)

    # la claror entre les ombres (pel terra de la galeria) i les ombres de les columnes
    for x0, x1 in ((0, XI),):
        e.claror((x0, 0.25, ZF), (x1, 0.25, ZF), (x1, 0.25, ZN), (x0, 0.25, ZN), (255, 236, 196),
                 lambda s, t: 0.32 * smooth(XI, XI - 160, s))
    for z in COLS:
        ax, az = a_terra((XC, FUST[2], z))
        bx, bz = a_terra((XC, 0, z))
        # una franja estreta del peu de la columna fins on cau la seva ombra
        e.foscor('ombra_col', (bx - 5, 0.3, bz + 5), (ax - 5, 0.3, az + 5), (ax + 5, 0.3, az - 5), (bx + 5, 0.3, bz - 5),
                 lambda s, t: 0.42)
    a = np.asarray(cv.img.convert('RGBA')).astype(np.float32)
    a[..., :3] *= np.array([1.06, 1.02, 0.94], np.float32)
    cv.img.paste(Image.fromarray(a.clip(0, 255).astype(np.uint8), 'RGBA'))
    cv.P = cv.img.load()


# ─── Fons, props, animacions ─────────────────────────────────────────────────

def _base():
    return _render()[0]


def bg(cv):
    cv.img.paste(_base())
    cv.P = cv.img.load()


@functools.lru_cache(maxsize=None)
def _MASK_DAVANT():
    return mascara_amo(_render()[1], {'columna_davant'})


def _decorat(nom):
    def draw(pc):
        d = diferencia(_render(nom)[0], _base())
        pc.img.alpha_composite(sense_hud(d))
        pc.P = pc.img.load()
    return draw


def _prop_morter(pc):
    d = diferencia(_render('tarda', True)[0], _base())
    pc.img.alpha_composite(sense_hud(d))
    pc.P = pc.img.load()


PROPS = {
    'morter': _prop_morter,
    'llum_capvespre': _decorat('capvespre'),
    'llum_mati': _decorat('mati'),
}


def _frames_gotes():
    """Les gotes que cauen dels ràfecs (el de la nostra galeria, davant els arcs, i el de la galeria del fons), i les
    rodones que fan als bassals de la gespa. Només es veuen on hi ha gespa, cel o les galeries del davant."""
    _, e = _render()
    m = mascara_amo(e, {'gespa', 'galeria_fons', 'galeria_esq', 'pica', 'campanar', ''}).array
    n = 10
    out = []
    # les fonts de les gotes: el ràfec de la nostra galeria (x = -22, y = 214) i el de la galeria del fons
    fonts = [((-24, 188, z), 188) for z in range(-200, 400, 23)] + [((x, 146, GZ1 - 8), 146) for x in range(-420, -20, 31)]
    for i in range(n):
        im = Image.new('RGBA', (W, H), (0, 0, 0, 0))
        P = im.load()
        for k, (P0, y0) in enumerate(fonts):
            fase = (i + hr(k & 255, 7) * n) % n / n
            y = y0 - fase * y0
            u, v, _ = CAM.projecta((P0[0], y, P0[2]))
            s = CAM.escala(P0)
            ll = max(2, int(5 * s))
            for j in range(ll):
                X, Y = int(u), int(v - j)
                if 0 <= X < W and 0 <= Y < RH and m[Y, X]:
                    a = 200 - j * 120 // ll
                    P[X, Y] = (230, 236, 240, a)
            if fase > 0.85:                       # l'esquitx a terra
                ug, vg, _ = CAM.projecta((P0[0], 0, P0[2]))
                for dx in (-2, 2):
                    X, Y = int(ug + dx * s), int(vg - 1)
                    if 0 <= X < W and 0 <= Y < RH and m[Y, X]:
                        P[X, Y] = (220, 228, 232, 160)
        out.append(im)
    return out


ANIMS = {'gotes': {'frames': _frames_gotes, 'frameDuration': 110}}


# ─── Capes del davant ───────────────────────────────────────────────────────

FRONT = [
    # les columnes de més a prop i el tros d'arcada de sobre: sempre per davant
    {'id': 'davant', 'mask': lambda x, y: _MASK_DAVANT()(x, y), 'baseline': 999, 'zIndex': 22,
     'variants': ('llum_capvespre', 'llum_mati')},
]


# ─── Geometria ───────────────────────────────────────────────────────────────

def _p(x, z, y=0.0):
    u, v, _ = CAM.projecta((x, y, z))
    return round(u), round(v)


def _rect(*Ps):
    pts = [CAM.projecta(P) for P in Ps]
    return (max(0, round(min(p[0] for p in pts))), max(0, round(min(p[1] for p in pts))),
            min(W - 1, round(max(p[0] for p in pts))), min(RH - 1, round(max(p[1] for p in pts))))


def _walk():
    """El terra on es camina: la galeria, de l'ampit al banc i al mur, des d'on l'Iri fa ≈1,2 fins a ≈0,72."""
    zn, zf = _z_escala(1.16), _z_escala(0.72)
    pts = [(14, zf), (XI - 10, zf), (XI - 10, BANC[5] + 10), (BANC[0] - 10, BANC[5] + 10), (BANC[0] - 10, BANC[4] - 10),
           (XI - 10, BANC[4] - 10), (XI - 10, zn), (14, zn)]
    return [_p(x, z) for x, z in pts]


def _z_escala(k):
    """La z (al mig de la galeria) on un personatge fa l'escala k."""
    lo, hi = -300.0, ZF
    for _ in range(50):
        z = (lo + hi) / 2
        if CAM.escala((120, 0, z)) > k:
            lo = z
        else:
            hi = z
    return (lo + hi) / 2


_WALK = _walk()
_VS = [v for _, v in _WALK]

_T = {
    'galeria': _rect((0, MUR_ARC, 260), (XI, SOSTRE_I, 380)),
    'pica': _rect((PICA[0] - 40, 40, PICA[1]), (PICA[0] + 40, 0, PICA[1])),
    'gespa': _rect((-60, 0, -40), (-60, 0, 140), (-300, 0, 20)),
    'campanar': _rect((CAMPANAR[0], CAMPANAR[4] + 30, CAMPANAR[2]), (CAMPANAR[1], 200, CAMPANAR[2])),
    'banc': _rect((BANC[0], BANC[3], BANC[4]), (BANC[1], 0, BANC[5]), (BANC[0], 0, BANC[4])),
    'morter': _rect((MORTER[0] - 10, BANC[3] + 20, MORTER[1]), (MORTER[0] + 10, BANC[3], MORTER[1])),
    'porta_monestir': _rect((XI, P_MONESTIR[2], P_MONESTIR[0]), (XI, 0, P_MONESTIR[1])),
    'porta_bugaderia': _rect((XI, P_BUGADERIA[2], P_BUGADERIA[0]), (XI, 0, P_BUGADERIA[1])),
    'porta_apotecaria': _rect((P_APOTECARIA[0], P_APOTECARIA[2], ZF), (P_APOTECARIA[1], 0, ZF)),
    'porta_capitular': _rect((P_CAPITULAR[0], P_CAPITULAR[2], ZF), (P_CAPITULAR[1], 0, ZF)),
}

GEOMETRIA = {
    'things': {
        'galeria': {'rect': _T['galeria'], 'walk': _p(100, 200)},
        'pica': {'rect': _T['pica'], 'walk': _p(20, 140)},
        'gespa': {'rect': _T['gespa'], 'walk': _p(20, 120)},
        'campanar': {'rect': _T['campanar'], 'walk': _p(30, 220)},
        'banc': {'rect': _T['banc'], 'walk': _p(BANC[0] - 26, (BANC[4] + BANC[5]) / 2)},
        'morter': {'rect': _T['morter'], 'walk': _p(BANC[0] - 26, MORTER[1])},
        'porta_monestir': {'rect': _T['porta_monestir'], 'walk': _p(XI - 24, (P_MONESTIR[0] + P_MONESTIR[1]) / 2)},
        'porta_bugaderia': {'rect': _T['porta_bugaderia'], 'walk': _p(XI - 22, (P_BUGADERIA[0] + P_BUGADERIA[1]) / 2)},
        'porta_apotecaria': {'rect': _T['porta_apotecaria'], 'walk': _p((P_APOTECARIA[0] + P_APOTECARIA[1]) / 2, ZF - 70)},
        'porta_capitular': {'rect': _T['porta_capitular'], 'walk': _p((P_CAPITULAR[0] + P_CAPITULAR[1]) / 2, ZF - 70)},
    },
    'spawns': {'iri': _p(140, 60), 'vet': _p(80, 90), 'ingilberga': _p(BANC[0] - 18, 132),
               'gueraula': _p(BANC[0] - 26, 182)},
    'walkable': _WALK,
    'floorSquash': 0.4,
    # La llum dominant ve de la gespa (el cel blanc, a l'esquerra): l'ombra cau cap a la dreta i una mica endavant.
    'characterShadow': {'enabled': True, 'color': '#24242c', 'alpha': 0.36, 'squash': 0.4, 'core': 0.6,
                        'light': {'x': 1, 'y': 0.15, 'direction': True, 'stretch': 0.35}},
    'characterLights': {
        'ambient': '#9ca2ac',
        'lights': [
            # el cel de la gespa, a l'esquerra (fred i clar)
            {'x': _p(-60, 120, 90)[0], 'y': _p(-60, 120, 90)[1], 'radius': 420, 'color': '#d6dce4', 'intensity': 0.35,
             'whenPropHidden': 'llum_capvespre'},
            # les llànties d'oli de l'acte 2 (càlides)
            *({'x': _p(XC + 14, z, 60)[0], 'y': _p(XC + 14, z, 60)[1], 'radius': 150, 'color': '#ffb060',
               'intensity': 0.4, 'whenPropVisible': 'llum_capvespre'} for z in (10, 100, 190, 280)),
            # el sol del matí (acte 4)
            {'x': _p(-200, 60, 120)[0], 'y': _p(-200, 60, 120)[1], 'radius': 520, 'color': '#ffe2b0',
             'intensity': 0.35, 'whenPropVisible': 'llum_mati'},
        ],
    },
    'regions': [{'id': 'perspectiva', 'active': True, 'scaleEnabled': True, 'scaleWalkSpeed': True,
                 'scaleTop': escala_v(CAM, min(_VS)), 'scaleBottom': escala_v(CAM, max(_VS)),
                 'points': [(0, min(_VS)), (W - 1, min(_VS)), (W - 1, max(_VS)), (0, max(_VS))]}],
}

ajusta_geometria(GEOMETRIA)
