"""
L'Última Arrel — `caseta_obra`, la caseta d'obra de NaturaPlus (Escena 5, Vet). Diumenge a la tarda. Sala «de prop».
EN 3D (hd640/tres_d.py), a 1×.

A dins d'un contenidor d'obra blanc (doble: és l'oficina de la Pla), amb llum de fluorescent, freda i plana: tota la
sala és de la paleta de NaturaPlus (blanc de plàstic, gris acer, verd fluor). L'únic càlid és la **porta** oberta del
fons a l'esquerra: a fora, el bosc de tarda, i la claror daurada que entra i s'escampa pel terra.

La càmera és dins, a la cantonada de davant a l'esquerra, i mira cap a la cantonada del fons a la dreta (dos punts de
fuga), una mica avall:
  - a la paret del fons: la **porta** (sortida, que no surt), el **cartell** «LA NATURA, PERÒ MILLOR» amb l'arbre que
    somriu, i la pantalla de la videotrucada (la Pla s'hi posa de cara); al sostre, dos fluorescents;
  - a la paret de la dreta: la finestra amb la persiana i l'endoll de l'**arbre_wifi**, que és a la cantonada (un
    arbret de plàstic en un test, amb llumetes: ANIMS `llumetes`);
  - l'**escriptori**, girat, separat de la paret (papers, el cafè fred, la caixa de polseres de punts);
  - la **maqueta** del Bosc 2.0 en una taula baixa, girada (arbres de plàstic, el tobogan, la botiga d'Aire Pur, el
    ninotet que somriu);
  - a la dreta, l'**altaveu** gran damunt d'una caixa («SONS DEL BOSC — VERSIÓ PRÈMIUM», amb la ruleta de ràdio);
  - primer pla (FRONT): caixes d'ampolles d'«Aire Pur» a l'esquerra i l'arxivador a la dreta, a contrallum.

El món: x a la dreta (0 = la paret de l'esquerra), y amunt (0 = el terra), z cap al fons (300 = la paret del fons);
1 unitat = 1 px de sala a l'escala 1 dels personatges (la Vet hi fa ≈90 px).
"""
import functools
import math
import random

from PIL import Image

from hd.pix import Canvas, Light
from hd640.rooms._comu_dia import (
    W, H, RH, fbm, hr, smooth, lletres, ample, capcada, tronc, diferencia, LEAVES, GREENL, BARK, MOSS, EARTH, LEAF,
    HAZE, PLASTIC, STEEL, NEON, SIGNK, CONE, YELLOWM, REDL, IRONK, CREAM, SCREENB, PLANK, CLOTH)
from hd640.tres_d import Camera, Escena, Llum

CAM = Camera(pos=(190, 150, -230), yaw=0.28, pitch=0.17, f=400, centre=(320, 118))
XW, ZW, HW = 460, 300, 170                        # la paret de la dreta, la del fons, el sostre

LIGHT = Light(ambient=0.0, vignette=None, floor_fade=None)
LLUMS = [Llum((150, 166, 150), 520, 1.3, power=1.0), Llum((330, 166, 210), 420, 1.0, power=1.0)]
AMBIENT = 0.4

# Les rampes de dins (fred i pla)
WALLW = [(70, 76, 88), (104, 110, 122), (140, 146, 158), (172, 178, 188), (198, 204, 212), (218, 222, 228),
         (234, 237, 241), (246, 248, 250)]
VINYL = [(34, 38, 44), (52, 58, 66), (72, 80, 90), (94, 102, 112), (118, 126, 134), (142, 150, 156),
         (168, 174, 178), (196, 200, 204)]
DESK = [(40, 44, 52), (70, 76, 86), (104, 110, 120), (140, 146, 154), (178, 182, 190), (212, 216, 222),
        (236, 238, 242)]
CARDB = [(46, 34, 20), (80, 60, 36), (118, 90, 54), (156, 122, 76), (190, 154, 100), (220, 188, 136)]

DOOR = (26, 96, 140)                              # la porta: x0, x1 (paret del fons), alçada
POSTER = (118, 234, 24, 114)                      # el cartell: x0, x1, y0, y1 (al dibuix pla de la paret del fons)
SCREEN = (262, 372, 40, 104)                      # la pantalla de la videotrucada (idem)
FINESTRA = (96, 176, 40, 100)                     # la finestra de la paret de la dreta: z0, z1 (pla: 300 - z), y0, y1
ARBRE = (430, 270)                                # l'arbre wifi (x, z)
ESCRIPTORI = (150, 178, 132, 56, 50, -0.32)       # cx, cz, ample, fons, alçada, gir
MAQUETA = (318, 92, 126, 76, 36, 0.22)
CAIXA = (420, 140, 46, 54, 34, -0.12)             # la caixa de l'altaveu
ALTAVEU = (420, 140, 48, 30, 64)                  # cx, cz, ample, fons, alçada (damunt la caixa)


# ─── Els dibuixos plans (textures) ───────────────────────────────────────────

def _bosc_fora(cv, x0, x1, y0, y1):
    """El bosc de tarda, a fora (per la porta i la finestra): càlid, amb el sol baix."""
    for y in range(y0, y1):
        for x in range(x0, x1):
            t = (y - y0) / max(1, y1 - y0)
            if t > 0.72:
                cv.put(x, y, EARTH, 5.0 + (fbm(x / 6, y / 3, 3) - 0.5) * 1.6 + (t - 0.72) * 3, lit=0)
            else:
                cv.put(x, y, HAZE, 6.6 - t * 3 + (fbm(x / 9, y / 9, 4) - 0.5) * 1.2, lit=0)
    for k, tx in enumerate(range(x0 + 6, x1, 23)):
        tronc(cv, tx + 5 * fbm(k, 0.3, 2), y0, int(y0 + (y1 - y0) * 0.78), 3 + k % 3, 5 + k % 3, k + 3, base=3.0, lit=0,
              molsa=0.7)
    capcada(cv, x0, x1, y0, int(y0 + (y1 - y0) * 0.55), 9, ramp=LEAVES, ramp2=LEAF, base=4.4, edge=0.4, lit=0,
            sx=10, sy=8)


def _paret_fons():
    """La paret del fons vista de cara: 460×170 (x del món, y = 170 − alçada)."""
    cv = Canvas(XW, HW)
    for y in range(HW):
        for x in range(XW):
            lvl = 5.4 - (1.6 if x % 23 == 0 else 0) + (0.5 if x % 23 == 1 else 0) - (y / HW) * 0.3
            cv.put(x, y, WALLW, lvl, lit=0)
    cv.rect(0, HW - 6, XW - 1, HW - 1, STEEL, 3.0, lit=0)                         # el sòcol
    # la porta oberta: el bosc a fora
    x0, x1, h = DOOR
    _bosc_fora(cv, x0, x1, HW - h, HW - 2)
    cv.rect(x0 - 3, HW - h - 3, x0 - 1, HW - 1, STEEL, 4.0, lit=0)
    cv.rect(x1 + 1, HW - h - 3, x1 + 3, HW - 1, STEEL, 3.4, lit=0)
    cv.rect(x0 - 3, HW - h - 3, x1 + 3, HW - h - 1, STEEL, 4.4, lit=0)
    # el cartell «LA NATURA, PERÒ MILLOR»: paper brillant, l'arbre de plàstic que somriu
    p0, p1, q0, q1 = POSTER
    cv.rect(p0, q0, p1, q1, PLASTIC, 6.2, lit=0)
    cv.rect(p0, q0, p1, q0 + 2, NEON, 3.4, lit=0)
    cv.rect(p0 + 4, q0 + 6, p1 - 4, q0 + 42, [(150, 200, 230), (180, 220, 240), (210, 236, 248)], 1.4, lit=0)
    tx, ty = (p0 + p1) // 2, q0 + 24
    cv.rect(tx - 2, ty + 4, tx + 2, q0 + 42, [(110, 80, 50), (150, 110, 70), (190, 150, 100)], 1.4, lit=0)
    cv.disc(tx, ty - 2, 16, 14, NEON, lambda nx, ny: 3.6 - ny * 0.8 - nx * 0.4, lit=0)
    cv.disc(tx - 6, ty - 5, 1.6, 2, IRONK, 0.6, lit=0)
    cv.disc(tx + 6, ty - 5, 1.6, 2, IRONK, 0.6, lit=0)
    for k in range(-7, 8):
        cv.flat(tx + k, ty + 2 - round(k * k * 0.06), (20, 50, 20))
        cv.flat(tx + k, ty + 3 - round(k * k * 0.06), (20, 50, 20))
    # (lletra de 2 d'ample i 3 d'alt: en escorç, a ≈0,75, encara es llegeix)
    lletres(cv, 'LA NATURA,', p0 + (p1 - p0 - ample('LA NATURA,', 2)) // 2, q0 + 45, (20, 60, 30), k=3, kx=2)
    lletres(cv, 'PERÒ MILLOR', p0 + (p1 - p0 - ample('PERÒ MILLOR', 2)) // 2, q0 + 72, (20, 60, 30), k=3, kx=2)
    cv.disc(p1 - 10, q1 - 6, 3, 3, NEON, 4.0, lit=0)
    # la pantalla de la videotrucada: un senyor de corbata, i la Pla petita a la cantonada
    s0, s1, r0, r1 = SCREEN
    cv.rect(s0 - 3, r0 - 3, s1 + 3, r1 + 3, IRONK, 2.0, lit=0)
    for y in range(r0, r1 + 1):
        for x in range(s0, s1 + 1):
            cv.put(x, y, SCREENB, 3.0 + (y - r0) / (r1 - r0) * 1.0, lit=0)
    hx, hy = (s0 + s1) // 2 - 8, r0 + 28
    cv.rect(hx - 18, hy + 14, hx + 18, r1, CLOTH['gris'], 1.6, lit=0)                  # l'americana
    cv.poly([(hx - 3, hy + 14), (hx + 3, hy + 14), (hx, hy + 30)], PLASTIC, 5.6, lit=0)
    cv.rect(hx - 1, hy + 15, hx + 1, hy + 26, NEON, 3.0, lit=0)                         # la corbata verda
    cv.disc(hx, hy, 9, 11, [(110, 70, 56), (170, 120, 96), (214, 164, 132), (240, 200, 170)],
            lambda nx, ny: 2.4 - nx * 0.6, lit=0)
    cv.disc(hx, hy - 8, 9, 5, CLOTH['gris'], lambda nx, ny: 1.0 if ny < 0.2 else -9, lit=0)
    cv.flat(hx - 3, hy, (30, 20, 20))
    cv.flat(hx + 3, hy, (30, 20, 20))
    cv.rect(hx - 3, hy + 5, hx + 3, hy + 5, [(90, 30, 30)], 0, lit=0)
    cv.rect(s1 - 26, r1 - 20, s1 - 4, r1 - 4, SCREENB, 5.0, lit=0)                     # la finestreta pròpia
    cv.disc(s1 - 15, r1 - 13, 4, 5, [(170, 120, 96), (230, 190, 160)], 1.0, lit=0)
    cv.rect(s1 - 20, r1 - 8, s1 - 10, r1 - 4, PLASTIC, 5.6, lit=0)
    cv.rect(s0 + 3, r0 + 3, s0 + 24, r0 + 7, REDL, 3.4, lit=0)                          # «EN DIRECTE»
    lletres(cv, 'LIVE', s0 + 5, r0 + 3, (255, 240, 240))
    # el rètol de NaturaPlus damunt la pantalla
    lletres(cv, 'NATURAPLUS S.A.', (s0 + s1) // 2 - ample('NATURAPLUS S.A.') // 2, r0 - 14, (60, 140, 60))
    # un rellotge de paret i una pissarra amb el compte enrere
    cv.disc(240, 24, 7, 7, PLASTIC, lambda nx, ny: 6.0 - math.hypot(nx, ny) * 1.6, lit=0)
    cv.line(240, 24, 240, 19, IRONK, 1.0, lit=0)
    cv.line(240, 24, 244, 25, IRONK, 1.0, lit=0)
    cv.rect(392, 40, 452, 92, PLASTIC, 6.4, lit=0)
    cv.rect(391, 39, 453, 39, STEEL, 4.0, lit=0)
    lletres(cv, 'BOSC 2.0', 398, 46, (40, 80, 160))
    lletres(cv, 'DILLUNS:', 398, 56, (40, 40, 50))
    lletres(cv, 'INAUGURA-', 398, 64, (40, 40, 50))
    lletres(cv, 'CIÓ!', 398, 72, (40, 40, 50))
    cv.line(400, 82, 440, 80, REDL, 3.0, lit=0)
    return cv.img


def _paret_dreta():
    """La paret de la dreta vista de cara: 300×170 (x = 300 − z del món, y = 170 − alçada): la finestra amb la
    persiana, i l'endoll de l'arbre wifi (a prop de la cantonada)."""
    cv = Canvas(ZW, HW)
    for y in range(HW):
        for x in range(ZW):
            lvl = 4.8 - (1.6 if x % 23 == 0 else 0) + (0.5 if x % 23 == 1 else 0) - (y / HW) * 0.3
            cv.put(x, y, WALLW, lvl, lit=0)
    cv.rect(0, HW - 6, ZW - 1, HW - 1, STEEL, 3.0, lit=0)
    f0, f1, g0, g1 = FINESTRA
    _bosc_fora(cv, f0, f1, g0, g1)
    for y in range(g0, g1, 5):                                                     # la persiana, mig tancada
        if y < g0 + 34:
            cv.rect(f0, y, f1, y + 3, PLASTIC, 5.0 - (y - g0) * 0.01, lit=0)
    cv.rect(f0 - 3, g0 - 3, f1 + 3, g0 - 1, STEEL, 4.4, lit=0)
    cv.rect(f0 - 3, g1 + 1, f1 + 3, g1 + 3, STEEL, 4.0, lit=0)
    cv.rect(f0 - 3, g0, f0 - 1, g1, STEEL, 3.6, lit=0)
    cv.rect(f1 + 1, g0, f1 + 3, g1, STEEL, 3.6, lit=0)
    # l'endoll, prop de la cantonada (l'arbre wifi hi és endollat)
    cv.rect(22, 142, 32, 152, PLASTIC, 6.0, lit=0)
    cv.flat(25, 147, (40, 40, 44))
    cv.flat(29, 147, (40, 40, 44))
    return cv.img


def _terra_fn(s, t, P):
    """El terra de vinil gris: rajoles de 40, amb les juntes, i una mica de fang de botes cap a la porta."""
    x, z = P[0], P[2]
    lvl = 4.0 + (fbm(x / 60, z / 60, 3) - 0.5) * 0.6
    if x % 40 < 1.2 or z % 40 < 1.2:
        lvl -= 0.9
    if math.hypot(x - 62, z - 290) < 70 and fbm(x / 8, z / 8, 5) > 0.62:
        lvl -= 1.0
    return lvl


def _sostre_fn(s, t, P):
    x, z = P[0], P[2]
    return 3.0 - (0.8 if x % 60 < 2 else 0)


def _escriptori_dalt():
    """La tapa de l'escriptori vista de dalt (132×56): papers, el cafè, la caixa de polseres, un portàtil."""
    w, d = 132, 56
    cv = Canvas(w, d)
    for y in range(d):
        for x in range(w):
            cv.put(x, y, DESK, 5.2 + (fbm(x / 20, y / 20, 2) - 0.5) * 0.4, lit=0)
    rnd = random.Random(3)
    for k in range(6):                                                             # els papers
        px, py = 8 + rnd.random() * 50, 6 + rnd.random() * 30
        cv.rect(px, py, px + 16, py + 20, PLASTIC, 6.4 - k % 2 * 0.4, lit=0)
        for ly in range(int(py) + 3, int(py) + 18, 3):
            cv.rect(px + 2, ly, px + 13 - (ly % 7), ly, STEEL, 4.0, lit=0)
    cv.disc(84, 14, 6, 6, PLASTIC, lambda nx, ny: 6.0 if math.hypot(nx, ny) > 0.7 else 2.0, lit=0)   # el cafè
    cv.disc(84, 14, 4, 4, CARDB, 1.0, lit=0)
    cv.rect(98, 26, 126, 48, CARDB, 4.0, lit=0)                                    # la caixa de polseres
    for k in range(9):
        cv.disc(103 + (k % 3) * 8, 31 + (k // 3) * 6, 3, 2, NEON, lambda nx, ny: 4.6 if math.hypot(nx, ny) > 0.5 else -9,
                lit=0)
    return cv.img


def _maqueta_dalt():
    """La maqueta del Bosc 2.0 vista de dalt (126×76): la gespa fluor, els camins blancs, un llac blau rodó."""
    w, d = 126, 76
    cv = Canvas(w, d)
    for y in range(d):
        for x in range(w):
            cv.put(x, y, NEON, 3.0 + (0.4 if (x + y) % 6 == 0 else 0), lit=0)
    for x in range(w):                                                             # el camí blanc, en S
        yc = d / 2 + math.sin(x / 18) * 12
        for y in range(int(yc - 3), int(yc + 4)):
            cv.put(x, y, PLASTIC, 6.0, lit=0)
    cv.disc(32, 20, 12, 8, SCREENB, lambda nx, ny: 4.6 - ny, lit=0)               # el llac, perfecte
    cv.rect(2, 2, w - 3, 3, PLASTIC, 6.4, lit=0)
    return cv.img


def _sprite_arbret(h, seed, somriu=False):
    """Un arbret de plàstic de la maqueta (o l'arbre wifi, de més gros): tronc marró llis, bola verd fluor."""
    s = h / 30
    w = int(22 * s) + 4
    cv = Canvas(w, h + 2, transparent=True)
    cx = w // 2
    cv.rect(cx - max(1, int(1.5 * s)), int(h * 0.5), cx + max(1, int(1.5 * s)), h, PLANK, 4.4, lit=0)
    cv.disc(cx, h * 0.34, 10 * s, 10 * s, NEON, lambda nx, ny: 4.0 - ny * 1.2 - nx * 0.6, lit=0)
    if somriu:
        cv.flat(cx - 3 * s, h * 0.3, (20, 50, 20))
        cv.flat(cx + 3 * s, h * 0.3, (20, 50, 20))
        for k in range(-3, 4):
            cv.flat(cx + k * s, h * 0.42 - abs(k) * 0.3 * s, (20, 50, 20))
    return cv.img


def _sprite_tobogan():
    cv = Canvas(36, 26, transparent=True)
    for i in range(30):                                                            # la rampa
        x, y = 4 + i, 4 + i * 0.7
        cv.rect(x, y, x, y + 2, YELLOWM, 4.6 - i * 0.03, lit=0)
    cv.rect(3, 4, 4, 25, CONE, 3.4, lit=0)                                         # l'escala
    cv.rect(9, 6, 10, 25, CONE, 3.0, lit=0)
    for y in range(8, 25, 4):
        cv.rect(3, y, 10, y, CONE, 3.8, lit=0)
    return cv.img


def _sprite_botiga():
    cv = Canvas(34, 26, transparent=True)
    cv.rect(2, 8, 31, 25, PLASTIC, lambda x, y: 6.0 - (0.8 if x > 24 else 0), lit=0)
    cv.poly([(0, 9), (16, 1), (33, 9)], NEON, 3.6, lit=0)
    cv.rect(5, 12, 28, 17, NEON, 2.6, lit=0)
    lletres(cv, 'AIRE', 8, 12, (240, 255, 240))
    cv.rect(13, 19, 19, 25, SCREENB, 3.0, lit=0)
    return cv.img


def _sprite_ninot():
    cv = Canvas(10, 18, transparent=True)
    cv.disc(5, 4, 3.4, 3.4, [(200, 150, 110), (240, 196, 160)], 1.0, lit=0)
    cv.flat(4, 4, (20, 20, 20))
    cv.flat(6, 4, (20, 20, 20))
    cv.flat(5, 6, (120, 30, 30))
    cv.rect(2, 8, 8, 13, NEON, 3.4, lit=0)
    cv.rect(3, 14, 4, 17, STEEL, 2.0, lit=0)
    cv.rect(6, 14, 7, 17, STEEL, 2.0, lit=0)
    return cv.img


def _sprite_altaveu():
    """L'altaveu de cara (48×64): negre, dues boques, l'etiqueta i la ruleta de ràdio."""
    w, h = 48, 64
    cv = Canvas(w, h, transparent=True)
    cv.rect(0, 0, w - 1, h - 1, IRONK, lambda x, y: 2.4 - x * 0.02 + (1.0 if y < 2 else 0), lit=0)
    cv.disc(20, 11, 8, 8, IRONK, lambda nx, ny: 0.4 + math.hypot(nx, ny) * 2.2, lit=0)
    cv.disc(20, 11, 3, 3, IRONK, 3.0, lit=0)
    cv.disc(17, 29, 9, 9, IRONK, lambda nx, ny: 0.4 + math.hypot(nx, ny) * 2.2, lit=0)
    cv.disc(17, 29, 3, 3, IRONK, 3.0, lit=0)
    cv.disc(38, 26, 5, 5, STEEL, lambda nx, ny: 5.0 - ny * 1.6 - nx, lit=0)          # la ruleta de ràdio
    cv.line(38, 26, 41, 22, NEON, 4.6, lit=0)
    lletres(cv, 'FM', 35, 33, (200, 200, 200))
    cv.rect(3, 40, 44, 63, CREAM, 4.8, lit=0)                                     # l'etiqueta
    for t, y, c in (('SONS DEL', 42, (30, 30, 34)), ('BOSC', 49, (30, 30, 34)), ('PRÈMIUM', 58, (40, 120, 40))):
        lletres(cv, t, 4 + (40 - ample(t)) // 2, y, c)
    return cv.img


def _sprite_arbre_wifi():
    """L'arbre wifi de prova: un arbret de plàstic en un test blanc, amb les llumetes (apagades al fons)."""
    w, h = 50, 104
    cv = Canvas(w, h, transparent=True)
    cv.poly([(12, 80), (38, 80), (35, 103), (15, 103)], PLASTIC, lambda x, y: 5.8 - (x - 12) * 0.05, lit=0)
    cv.rect(11, 78, 39, 81, PLASTIC, 6.4, lit=0)
    cv.rect(23, 40, 27, 79, PLANK, lambda x, y: 4.6 - (x - 23) * 0.3, lit=0)
    for cx, cy, r in ((25, 34, 20), (14, 46, 11), (36, 44, 12), (25, 14, 13)):
        cv.disc(cx, cy, r, r * 0.9, NEON, lambda nx, ny: 3.4 - ny * 1.0 - nx * 0.6 + (0.5 if (nx * 9) % 2 < 1 else 0), lit=0)
    cv.disc(25, 4, 4, 2, PLASTIC, 6.0, lit=0)                                     # l'antena (un piló blanc)
    cv.rect(24, 0, 26, 4, STEEL, 4.0, lit=0)
    for (x, y) in LLUMETES:
        cv.flat(x, y, (40, 90, 40))
    return cv.img


LLUMETES = [(14, 40), (20, 28), (30, 24), (36, 40), (24, 46), (10, 50), (40, 48), (28, 10), (18, 16), (32, 34),
            (22, 56), (34, 54)]


def _sprite_caixes():
    """Les caixes de cartró d'«Aire Pur» del primer pla, d'esquerra."""
    w, h = 150, 120
    cv = Canvas(w, h, transparent=True)
    for (x0, y0, x1, y1) in ((0, 40, 90, 119), (8, 0, 84, 40), (88, 64, 149, 119)):
        cv.rect(x0, y0, x1, y1, CARDB, lambda x, y: 3.2 - (x - x0) * 0.008 + (0.8 if y < y0 + 3 else 0), lit=0)
        cv.rect(x0 + 6, y0 + 10, x1 - 6, y0 + 22, PLASTIC, 5.0, lit=0)
        lletres(cv, 'AIRE PUR', x0 + 10, y0 + 12, (40, 120, 40), k=2)
    return cv.img


# ─── L'escena ────────────────────────────────────────────────────────────────

def _girat(cx, cz, ang):
    c, s = math.cos(ang), math.sin(ang)
    return lambda lx, lz: (cx + lx * c - lz * s, cz + lx * s + lz * c)


def _peu(cx, cz, lx, lz, ang):
    x, z = _girat(cx, cz, ang)(lx, lz)
    return (x, z)


def escena(cv):
    e = Escena(cv, CAM, LLUMS, ambient=AMBIENT)
    fons, dreta = _paret_fons(), _paret_dreta()
    # les parets, el terra i el sostre
    e.quad('sostre', (0, HW, -200), (XW, HW, -200), (XW, HW, ZW), (0, HW, ZW), ramp=WALLW, lvl=_sostre_fn)
    e.quad('paret_fons', (0, HW, ZW), (XW, HW, ZW), (XW, 0, ZW), (0, 0, ZW), tex=(fons, (0, 0, XW, HW)))
    e.quad('paret_dreta', (XW, HW, ZW), (XW, HW, -200), (XW, 0, -200), (XW, 0, ZW),
           tex=(dreta, (0, 0, ZW, HW)), ombra=lambda s, t: 0.0)
    e.quad('paret_esq', (0, HW, -200), (0, HW, ZW), (0, 0, ZW), (0, 0, -200), ramp=WALLW, lvl=4.0)
    e.quad('terra', (0, 0, ZW), (XW, 0, ZW), (XW, 0, -200), (0, 0, -200), ramp=VINYL, lvl=_terra_fn)
    # la claror càlida de la porta, pel terra (en diagonal cap a la dreta i endavant)
    x0, x1, _ = DOOR
    e.claror((x0 - 10, 0.3, ZW), (x1 + 40, 0.3, ZW), (x1 + 160, 0.3, ZW - 190), (x0 + 50, 0.3, ZW - 190),
             (250, 196, 120), lambda s, t: 0.6 * (1 - t / 190) * smooth(0, 30, s) * smooth(200, 150, s))
    # la porta oberta, que gira cap a dins, a l'esquerra
    ang = 1.15
    hx, hz = x0, ZW
    px, pz = hx - 70 * math.cos(ang), hz - 70 * math.sin(ang)
    e.quad('porta_fulla', (px, DOOR[2], pz), (hx, DOOR[2], hz), (hx, 0, hz), (px, 0, pz), ramp=STEEL,
           lvl=lambda s, t, P: 4.6 - (0.8 if 20 < t < 24 else 0), dues_cares=True)
    # els fluorescents del sostre
    for zc in (90, 210):
        e.caixa('fluor', 120, 340, HW - 4, HW, zc - 6, zc + 6, PLASTIC, 6.4,
                cares={'sota': {'ramp': [(230, 245, 250), (250, 255, 255)], 'lvl': 2.0}})
    # l'ombra als racons (la línia del terra amb les parets)
    e.foscor('ombra_fons', (0, 0.2, ZW), (XW, 0.2, ZW), (XW, 0.2, ZW - 14), (0, 0.2, ZW - 14),
             lambda s, t: 0.35 * (1 - t / 14))
    e.foscor('ombra_dreta', (XW - 14, 0.2, ZW), (XW, 0.2, ZW), (XW, 0.2, -100), (XW - 14, 0.2, -100),
             lambda s, t: 0.35 * (s / 14))
    # l'arbre wifi, a la cantonada, amb el cable a l'endoll
    ax, az = ARBRE
    e.foscor('ombra_arbre', (ax - 20, 0.2, az + 16), (ax + 20, 0.2, az + 16), (ax + 20, 0.2, az - 16), (ax - 20, 0.2, az - 16),
             lambda s, t: 0.5 * max(0.0, 1 - math.hypot(s - 20, t - 16) / 18))
    e.cable('cable', [(ax + 6, 2, az), (XW - 2, 1, az + 6), (XW - 1, 20, ZW - 27)], STEEL, 2.0, gruix=1.2)
    e.sprite('arbre_wifi', _sprite_arbre_wifi(), (25, 103), (ax, 0, az))
    # l'escriptori, girat
    cx, cz, w, d, h, ang = ESCRIPTORI
    e.foscor('ombra_escr', *[(_girat(cx, cz, ang)(lx, lz)[0], 0.2, _girat(cx, cz, ang)(lx, lz)[1])
                             for lx, lz in ((-w / 2 - 4, d / 2 + 4), (w / 2 + 4, d / 2 + 4), (w / 2 + 4, -d / 2 - 8),
                                            (-w / 2 - 4, -d / 2 - 8))], lambda s, t: 0.45)
    for lx in (-w / 2 + 4, w / 2 - 4):                                              # les potes
        for lz in (-d / 2 + 4, d / 2 - 4):
            X, Z = _girat(cx, cz, ang)(lx, lz)
            e.caixa('escriptori', X - 2, X + 2, 0, h - 3, Z - 2, Z + 2, STEEL, 3.4)
    e.caixa_girada('escriptori', cx, cz - d / 2 + 6 + 0, w - 10, 2, h - 14, ang, DESK, 3.6, y0=10)
    e.caixa_girada('escriptori', cx, cz, w, d, 3, ang, DESK, 4.4, y0=h - 3,
                   cares={'dalt': {'tex': (_escriptori_dalt(), (0, 0, 132, 56))}})
    # la cadira, d'esquena a nosaltres
    X, Z = _girat(cx, cz, ang)(10, -d / 2 - 22)
    e.caixa_girada('cadira', X, Z, 36, 34, 4, ang, STEEL, 3.0, y0=30)
    e.caixa_girada('cadira', X, Z - 15, 36, 4, 36, ang, STEEL, 2.6, y0=34)
    e.caixa('cadira', X - 2, X + 2, 0, 30, Z - 2, Z + 2, STEEL, 2.4)
    # la caixa i l'altaveu, a la dreta
    bx, bz, bw, bd, bh, bang = CAIXA
    e.foscor('ombra_caixa', (bx - 30, 0.2, bz + 30), (bx + 30, 0.2, bz + 30), (bx + 30, 0.2, bz - 40), (bx - 30, 0.2, bz - 40),
             lambda s, t: 0.5 * max(0.0, 1 - math.hypot(s - 30, t - 34) / 40))
    e.caixa_girada('caixa', bx, bz, bw, bd, bh, bang, CARDB, 3.4)
    ax_, az_, aw, ad, ah = ALTAVEU
    e.caixa_girada('altaveu', ax_, az_, aw, ad, ah, bang, IRONK, 2.4, y0=bh,
                   cares={'davant': {'tex': (_sprite_altaveu(), (0, 0, 48, 64))}})
    # la maqueta: la taula baixa i el que hi ha a dalt
    mx, mz, mw, md, mh, mang = MAQUETA
    e.foscor('ombra_maq', *[(_girat(mx, mz, mang)(lx, lz)[0], 0.2, _girat(mx, mz, mang)(lx, lz)[1])
                            for lx, lz in ((-mw / 2 - 4, md / 2 + 4), (mw / 2 + 10, md / 2 + 4), (mw / 2 + 10, -md / 2 - 6),
                                           (-mw / 2 - 4, -md / 2 - 6))], lambda s, t: 0.45)
    e.caixa_girada('maqueta', mx, mz, mw, md, mh, mang, PLASTIC, 4.6,
                   cares={'dalt': {'tex': (_maqueta_dalt(), (0, 0, 126, 76))}})
    g = _girat(mx, mz, mang)
    peces = [(_sprite_arbret(22, 1), (-46, 20)), (_sprite_arbret(18, 2), (-30, 26)), (_sprite_arbret(20, 3), (40, 22)),
             (_sprite_arbret(16, 4), (52, 10)), (_sprite_botiga(), (-34, -8)), (_sprite_tobogan(), (20, -4)),
             (_sprite_arbret(24, 5, True), (-8, 16)), (_sprite_ninot(), (6, -20))]
    for img, (lx, lz) in sorted(peces, key=lambda p: -g(*p[1])[1]):
        X, Z = g(lx, lz)
        e.sprite('maqueta', img, (img.width // 2, img.height - 1), (X, mh, Z), escala_img=0.8)
    # el primer pla: les caixes d'Aire Pur (esquerra) i l'arxivador (dreta)
    e.sprite('davant', _sprite_caixes(), (75, 119), (104, 0, 6), escala_img=0.55)
    e.caixa('davant', XW - 60, XW - 2, 0, 120, -110, -40, STEEL, 2.6,
            cares={'esquerra': {'ramp': STEEL, 'lvl': lambda s, t, P: 2.4 - (1.2 if int(P[1]) % 30 < 2 else 0)},
                   'dalt': {'ramp': STEEL, 'lvl': 3.6}})
    e.silueta({'davant'}, k=0.45, col=(20, 22, 30))
    return e


@functools.lru_cache(maxsize=None)
def _base():
    cv = Canvas(W, H, light=LIGHT)
    e = escena(cv)
    for y in range(RH, H):
        for x in range(W):
            cv.flat(x, y, (0, 0, 0))
            e.amo[y * W + x] = 0
    return cv.img, e


def bg(cv):
    img, _ = _base()
    cv.img.paste(img)
    cv.P = cv.img.load()


PROPS = {}


# ─── Animacions ──────────────────────────────────────────────────────────────

def _frames_llumetes():
    """Les llumetes de l'arbre wifi, que parpellegen (verd fluor, blau i blanc), i el piló de l'antena."""
    base, e = _base()
    ax, az = ARBRE
    k = CAM.escala((ax, 0, az))
    u0, v0, _ = CAM.projecta((ax, 0, az))
    ox, oy = u0 - 25 * k, v0 - 103 * k
    cols = [(150, 255, 110), (120, 200, 255), (250, 255, 250)]
    out = []
    for i in range(6):
        cv = Canvas(W, H, transparent=True)
        rnd = random.Random(i * 13)
        for j, (x, y) in enumerate(LLUMETES):
            if (j + i) % 3 == 0 or rnd.random() < 0.3:
                X, Y = ox + x * k, oy + y * k
                c = cols[(j + i) % 3]
                cv.flat(X, Y, c)
                cv.flat(X + 1, Y, tuple(int(v * 0.7) for v in c))
        if i % 2 == 0:
            cv.flat(ox + 25 * k, oy + 1 * k, (150, 255, 110))
        out.append(cv.img)
    return out


ANIMS = {'llumetes': {'frames': _frames_llumetes, 'frameDuration': 260}}


def _amo(ids):
    def mask(x, y):
        _, e = _base()
        return e.ids[e.amo[y * e.cv.w + x]] in ids
    return mask


def _v(z):
    return round(CAM.projecta((200, 0, z))[1])


FRONT = [
    # la maqueta (la taula baixa): qui és al fons hi passa per darrere
    {'id': 'davant_maqueta', 'mask': _amo({'maqueta'}), 'baseline': _v(MAQUETA[1] - MAQUETA[3] / 2), 'zIndex': 20},
    {'id': 'davant_escriptori', 'mask': _amo({'escriptori', 'cadira'}), 'baseline': _v(ESCRIPTORI[1] - ESCRIPTORI[3] / 2 - 20),
     'zIndex': 20},
    {'id': 'davant', 'mask': _amo({'davant'}), 'baseline': 999, 'zIndex': 22},
]


# ─── Geometria ───────────────────────────────────────────────────────────────

def _p(x, z, y=0.0):
    u, v, _ = CAM.projecta((x, y, z))
    return round(u), round(v)


def _rect(*Ps):
    pts = [CAM.projecta(P) for P in Ps]
    return (max(0, round(min(p[0] for p in pts))), max(0, round(min(p[1] for p in pts))),
            min(W - 1, round(max(p[0] for p in pts))), min(RH - 1, round(max(p[1] for p in pts))))


def _caixa_rect(cx, cz, w, d, h, ang, y0=0.0):
    g = _girat(cx, cz, ang)
    pts = []
    for lx in (-w / 2, w / 2):
        for lz in (-d / 2, d / 2):
            X, Z = g(lx, lz)
            pts += [(X, y0, Z), (X, y0 + h, Z)]
    return _rect(*pts)


def _sota(cx, cz, w, d, ang, marge=8):
    """El contorn d'un moble girat a terra (en pantalla), una mica més gros: un forat on no es trepitja."""
    g = _girat(cx, cz, ang)
    return [_p(*g(lx, lz)) for lx, lz in ((-w / 2 - marge, -d / 2 - marge), (w / 2 + marge, -d / 2 - marge),
                                          (w / 2 + marge, d / 2 + marge), (-w / 2 - marge, d / 2 + marge))]


# El punt de terra just sota la llum, per a l'ombra de contacte: entre els dos fluorescents (al món: x, z).
_LLUM_TERRA = (240, 180)


# El terra on es camina (en pantalla): de la porta (al fons a l'esquerra) i la cantonada de l'arbre fins a davant,
# tallat on la Vet arriba a ≈1,25 (més a prop, el terra és del primer pla).
_WALK = [(52, 184), (386, 156), (456, 192), (474, 214), (300, 236), (0, 238), (0, 226)]
_VS = [v for _, v in _WALK]


# Els fulls dels personatges fan l'Iri de 68 px a escala 1 (la sala es va dibuixar pensant en 97): ×97/68. La Vet hi
# porta la mida gran dels fulls (`Gran`, ×1,5: characters.json, `outfit`), que el motor mostra a l'escala ÷ 1,5
# (≈0,67–1,18): els píxels del personatge, com els del decorat.
K_FULLS = 97 / 68


def _escala_v(v):
    """L'escala d'un personatge amb els peus a la fila v (gairebé no depèn de la x: es pren al mig)."""
    lo, hi = 0.0, 600.0
    for _ in range(40):
        z = (lo + hi) / 2
        if CAM.projecta((240, 0, z))[1] > v:
            lo = z
        else:
            hi = z
    return round(CAM.escala((240, 0, (lo + hi) / 2)), 3)

GEOMETRIA = {
    'things': {
        'porta': {'rect': _rect((DOOR[0], DOOR[2], ZW), (DOOR[1], 0, ZW)), 'walk': _p(62, 270)},
        'cartell': {'rect': _rect((POSTER[0], HW - POSTER[2], ZW), (POSTER[1], HW - POSTER[3], ZW)), 'walk': _p(170, 236)},
        'arbre_wifi': {'rect': _rect((ARBRE[0] - 26, 104, ARBRE[1]), (ARBRE[0] + 26, 0, ARBRE[1])), 'walk': _p(356, 250)},   # al costat, no davant: s'ha de veure com s'apaga (242)
        'escriptori': {'rect': _caixa_rect(*ESCRIPTORI), 'walk': _p(196, 120)},
        'maqueta': {'rect': _caixa_rect(*MAQUETA), 'walk': _p(250, 60)},
        'altaveu': {'rect': _caixa_rect(ALTAVEU[0], ALTAVEU[1], ALTAVEU[2], ALTAVEU[3], ALTAVEU[4] + CAIXA[4], CAIXA[5]),
                    'walk': (420, 176)},   # (242) a la dreta de l'arbre Wi-Fi, per darrere la maqueta (l'únic accés): sota la copa no
    },
    'spawns': {'vet': (250, 228), 'pla': _p(318, 232)},  # la Vet, davant de l'escriptori (a l'entrada la taparien les caixes)
    'walkable': _WALK,
    'forats': [_sota(*ESCRIPTORI[:4], ESCRIPTORI[5]), _sota(*MAQUETA[:4], MAQUETA[5]),
               _sota(*CAIXA[:4], CAIXA[5], marge=6)],
    # La llum és de sostre (els fluorescents): l'ombra, rodona i suau, just a sota.
    'floorSquash': 0.35,
    'characterShadow': {'enabled': True, 'color': '#202630', 'alpha': 0.44, 'squash': 0.35, 'core': 0.6,
                        'light': {'x': _p(*_LLUM_TERRA)[0], 'y': _p(*_LLUM_TERRA)[1], 'stretch': 0.45, 'reach': 150}},
    # La llum de la sala sobre els personatges: el fluorescent (l'ambient, fred i pla), els dos tubs del sostre (blanc
    # blavós, de dalt) i la claror càlida de la porta del fons a l'esquerra, que els toca pel costat.
    'characterLights': {
        'ambient': '#b8bcc8',
        'lights': [*({'x': _p(x, z, 90)[0], 'y': _p(x, z, 90)[1], 'radius': 300, 'color': '#e6eeff', 'intensity': 0.2}
                     for (x, _, z) in (L.pos for L in LLUMS)),
                   {'x': _p((DOOR[0] + DOOR[1]) / 2, ZW, 50)[0], 'y': _p((DOOR[0] + DOOR[1]) / 2, ZW, 50)[1],
                    'radius': 230, 'color': '#ffd08a', 'intensity': 0.35}],
    },
    'regions': [{'id': 'perspectiva', 'active': True, 'scaleEnabled': True, 'scaleWalkSpeed': True,
                 'scaleTop': round(_escala_v(min(_VS)) * K_FULLS, 3), 'scaleBottom': round(_escala_v(max(_VS)) * K_FULLS, 3),
                 'points': [(0, min(_VS)), (W - 1, min(_VS)), (W - 1, max(_VS)), (0, max(_VS))]}],
}
