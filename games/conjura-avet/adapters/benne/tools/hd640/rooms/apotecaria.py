"""
La Conjura de l'Avet — `apotecaria`, l'apotecaria del monestir (acte 2, Vet). Vespre. Sala «de prop». EN 3D, a 1×.

La sala de la Gueraula: espelmes (ANIMS `espelmes`, la flama que tremola) i la llar de carbó, càlid i amb racons
foscos. La càmera és a la cantonada de davant a la dreta i mira cap a la cantonada del fons a l'esquerra, una mica
avall:
  - a la paret del fons, els **prestatges** fins al sostre plens de flascons, pots i capses; al prestatge de l'abast,
    els quatre flascons amb etiqueta (`flasco_menta`, `flasco_ruda`, `flasco_salvia`, `flasco_sense_nom`, aquest amb
    l'etiqueta en blanc) i, al seu costat, el pot de pedra de l'**atramentum**; a la dreta, la **porta** del claustre;
  - a la paret de l'esquerra, la **llar** amb el carbó encès i la campana;
  - al mig, la **taula** girada (pergamins, el xarop verd, una espelma, la gerra de **mel**, un prop); damunt, a la
    biga, els **manats** d'herbes penjats, amb el **cardo** (un prop: un cap espinós i sec);
  - el **morter** gran de pedra, a terra; la **pell_ovella** en un tamboret, a la dreta;
  - primer pla: les gerres de fang de la dreta, a contrallum (FRONT), i la taula, que tapa qui hi passa per darrere.

Decorats: `cardo_agafat` (el cordill buit a la biga) i `mel_agafada` (la rodona enganxosa a la taula).

El món: x a la dreta (0 = la paret de l'esquerra), y amunt, z cap al fons (260 = la paret del fons).
"""
import functools
import math

import numpy as np
from PIL import Image

from hd.pix import Canvas, Light
from hd640.tres_d import Camera, Escena, Llum
from hd640.rooms.claustre_comu import (
    ajusta_geometria,
    W, H, RH, GRES, BLANC, LLOSA, FUSTA, FERRO, FOC, LLI, NEGRE, COURE, FANG, PEDRA, VIDREV, VIDREA, HERBA, PERGAMI,
    nz, hr, smooth, diferencia, sense_hud, fosc_hud, mascara_amo, escala_v, v_escala, mur_pedra, lletres, ample)

CAM = Camera(pos=(280, 140, -240), yaw=-0.26, pitch=0.15, f=400, centre=(320, 110))
XW, ZW, HW = 420, 260, 170
LIGHT = Light(ambient=0.0, vignette=None, floor_fade=None)

PREST = (16, 324, 34)                              # x0, x1, fondària (contra la paret del fons)
LLEIXES = [0, 22, 58, 92, 124, 150]                # l'alçada de cada lleixa
# els quatre flascons de l'abast (a la lleixa de 58): x del mig (a la textura dels prestatges), color, rètol
FLASCONS = {
    'flasco_menta': (120, ((14, 50, 26), (28, 86, 44), (50, 130, 68), (90, 176, 104), (170, 226, 180)), 'MENTA'),
    'flasco_ruda': (150, ((40, 46, 10), (70, 80, 18), (110, 120, 30), (150, 160, 52), (210, 216, 120)), 'RUDA'),
    'flasco_salvia': (180, ((34, 42, 40), (60, 72, 66), (92, 108, 98), (130, 146, 132), (190, 204, 190)), 'SÀLVIA'),
    'flasco_sense_nom': (210, ((48, 26, 10), (86, 48, 16), (130, 78, 24), (176, 116, 40), (226, 176, 96)), ''),
}
ATRAMENTUM = (244, 58)                             # x del mig (món), lleixa (la de l'abast, al costat dels flascons)
PORTA = (348, 404, 124)                            # x0, x1, alçada (paret del fons)
LLAR = (70, 170, 54, 40)                           # z0, z1 (paret de l'esquerra), alçada de la boca, fondària
TAULA = (196, 118, 138, 64, 50, 0.22)              # cx, cz, ample, fons, alçada, gir
MEL = (52, -12)                                    # on és la gerra de mel, a la taula (x, z de la taula)
BIGA = (150, 152)                                  # la biga dels manats: z, y (de x = 0 a XW)
MANATS = [44, 76, 108, 140, 172, 204, 236]         # x de cada manat
CARDO = 2                                          # quin dels manats és el cardo
MORTER = (330, 196, 20, 34)                        # x, z, radi, alçada
TAMBORET = (370, 96, 18, 30)                       # x, z, radi, alçada
GERRES = [(36, -46, 26, 70), (84, -84, 20, 54)]    # el primer pla (a l'esquerra): x, z, radi, alçada


def _llums():
    tx, tz = TAULA[:2]
    return [Llum((tx + 20, TAULA[4] + 30, tz), 300, 2.2, power=1.3),                  # l'espelma de la taula
            Llum((LLAR[2] - 10 + 30, 30, (LLAR[0] + LLAR[1]) / 2), 280, 2.0, power=1.2),  # la llar
            Llum((PORTA[0] + 20, 90, ZW - 40), 200, 0.6, power=1.4),                 # la porta (fresca)
            Llum((60, 110, ZW - 50), 200, 1.0, power=1.4)]                           # l'espelma del prestatge


# ─── Dibuixos plans ──────────────────────────────────────────────────────────

def _flasco(cv, cx, ybase, h, ramp, rètol='', seed=0, forma=0):
    """Un flascó de vidre (o un pot) dret: el cos, el coll, el tap de suro, i l'etiqueta de pergamí."""
    r = h * (0.32 if forma == 0 else 0.42 if forma == 1 else 0.26)
    cos_h = h * (0.62 if forma != 2 else 0.8)
    for y in range(int(ybase - cos_h), int(ybase) + 1):
        t = (ybase - y) / cos_h
        half = r * (1 - (t - 0.55) ** 2 * 0.9 if forma == 0 else 1.0 if forma == 2 else 1 - t * 0.2)
        half = max(1.5, half)
        for x in range(int(cx - half), int(cx + half) + 1):
            nx = (x - cx) / half
            lvl = 2.4 - nx * 0.8 + (1.6 if -0.6 < nx < -0.35 and t > 0.3 else 0)
            cv.put(x, y, list(ramp), lvl, lit=0)
    # el coll i el tap
    cw = max(1.5, r * 0.36)
    cv.rect(cx - cw, ybase - h + 4, cx + cw, ybase - cos_h, list(ramp), 2.6, lit=0)
    cv.rect(cx - cw - 0.5, ybase - h, cx + cw + 0.5, ybase - h + 3, FANG, 4.6, lit=0)
    if rètol is not None:
        ew = r * 1.5
        ey = ybase - cos_h * 0.55
        cv.rect(cx - ew / 2, ey - 4, cx + ew / 2, ey + 4, PERGAMI, 4.4, lit=0)
        if rètol:
            # unes ratlles fosques (la lletra no es llegiria): una per síl·laba
            for k in range(min(3, len(rètol) // 2)):
                cv.rect(cx - ew / 2 + 2 + k * (ew - 4) / 3, ey - 1, cx - ew / 2 + 1 + (k + 1) * (ew - 4) / 3, ey,
                        FUSTA, 1.0, lit=0)


def _prestatges():
    """Els prestatges vistos de cara (x de la textura = x del món − PREST[0]; y = HW − alçada): lleixes de fusta
    fosca plenes de flascons de tots els colors, pots de fang, capses i llibres, i els quatre de l'abast."""
    w = PREST[1] - PREST[0]
    cv = Canvas(w, HW, transparent=True)
    # el fons (la paret de dins dels prestatges: fusta fosca)
    for y in range(HW):
        for x in range(w):
            cv.put(x, y, FUSTA, 1.2 + (nz(x / 3, y / 20, 3) - 0.5) * 0.5, lit=0)
    rams = [VIDREV, VIDREA, FANG, [(30, 30, 50), (50, 50, 80), (80, 80, 120), (120, 120, 160), (180, 180, 210)],
            [(60, 20, 30), (100, 34, 44), (140, 60, 64), (180, 100, 96), (220, 160, 150)], PEDRA]
    for i, (y0, y1) in enumerate(zip(LLEIXES, LLEIXES[1:] + [HW])):
        base = HW - y0
        top = HW - y1
        cv.rect(0, base - 3, w - 1, base, FUSTA, 3.6, lit=0)                # la lleixa
        cv.rect(0, base - 3, w - 1, base - 3, FUSTA, 5.0, lit=0)
        if y0 == 58:
            # la lleixa de l'abast: els quatre flascons grans, i pots petits als costats
            for nom, (cx, ramp, rt) in FLASCONS.items():
                _flasco(cv, cx - PREST[0], base - 4, 26, ramp, rt, forma=0 if nom != 'flasco_sense_nom' else 1)
            xs = [x for x in range(6, 90, 14)] + [x for x in range(220, w - 8, 13)]
        else:
            xs = list(range(5 + (i * 7) % 11, w - 6, 11 + i % 3))
        for k, x in enumerate(xs):
            if y0 == ATRAMENTUM[1] and abs(x + PREST[0] - ATRAMENTUM[0]) < 16:
                continue
            hgt = min(base - top - 6, 10 + int(hr(k, i, 5) * 14))
            if hgt < 6:
                continue
            kind = int(hr(k, i, 7) * 6)
            if kind == 5:                       # llibres o capses
                cv.rect(x - 4, base - 3 - hgt, x + 4, base - 4, [(40, 20, 14), (70, 36, 22), (110, 60, 34)],
                        1.0 + hr(k, i) * 1.5, lit=0)
            else:
                _flasco(cv, x, base - 4, hgt, rams[kind], None, forma=kind % 3)
        # i alguna espelma consumida
    # l'atramentum: un pot de pedra gros, al costat dels quatre flascons, amb l'etiqueta grossa
    ax = ATRAMENTUM[0] - PREST[0]
    base = HW - ATRAMENTUM[1] - 4
    for y in range(base - 18, base + 1):
        t = (base - y) / 18
        half = 9 - abs(t - 0.5) * 4
        for x in range(int(ax - half), int(ax + half) + 1):
            cv.put(x, y, PEDRA, 4.2 - (x - ax) / half * 1.2, lit=0)
    cv.rect(ax - 6, base - 21, ax + 6, base - 18, PEDRA, 2.6, lit=0)
    cv.rect(ax - 8, base - 12, ax + 8, base - 6, PERGAMI, 4.6, lit=0)
    cv.rect(ax - 6, base - 10, ax + 6, base - 9, NEGRE, 1.0, lit=0)        # «ATRAMENTUM»
    cv.rect(ax - 6, base - 8, ax + 3, base - 8, NEGRE, 1.4, lit=0)
    return cv.img


def _paret_fons():
    cv = Canvas(XW, HW)
    mur_pedra(cv, 0, 0, XW, HW, 3.4, 23, gres=0.3)
    # la porta (tancada, de fusta, amb un ram de sàlvia penjat)
    x0, x1, ph = PORTA
    r = (x1 - x0) / 2
    cx, ya = (x0 + x1) / 2, HW - ph + r
    for y in range(int(HW - ph - 8), HW):
        for x in range(int(x0 - 8), int(x1 + 9)):
            d = math.hypot(x - cx, y - ya) if y < ya else abs(x - cx)
            if d <= r:
                lvl = 2.6 + (0.5 if int(x - x0) % 9 == 0 else 0) - (0.7 if int(x - x0) % 9 == 8 else 0)
                cv.put(x, y, FUSTA, lvl + (nz(x / 3, y / 14, 4) - 0.5) * 0.6, lit=0)
            elif d <= r + 7:
                a = int((math.atan2(y - ya, x - cx) + math.pi) * 5)
                cv.put(x, y, GRES, 4.4 + (a % 2) * 0.6 - (1.2 if d - r < 1.3 else 0), lit=0)
    for fy in (HW - ph * 0.3, HW - ph * 0.68):
        cv.rect(x0 + 2, fy, x0 + r * 1.3, fy + 2, FERRO, 2.6, lit=0)
    cv.disc(x1 - 8, HW - ph * 0.48, 2.2, 2.2, FERRO, 4.0, lit=0)
    return cv.img


def _paret_esq():
    """La paret de l'esquerra vista de cara: (ZW + 300) × HW (x = z + 300): la pedra i, damunt la llar, la campana
    ennegrida pel fum."""
    w = ZW + 300
    cv = Canvas(w, HW)
    mur_pedra(cv, 0, 0, w, HW, 3.2, 29, gres=0.3)
    z0, z1 = LLAR[0], LLAR[1]
    for y in range(HW):
        for x in range(z0 + 300 - 20, z1 + 300 + 20):
            t = 1 - y / HW
            k = max(0.0, 1 - abs(x - (z0 + z1) / 2 - 300) / ((z1 - z0) / 2 + 20)) * (0.3 + t * 0.4)
            o = cv.P[x, y]
            m = 1 - min(0.8, k)
            cv.P[x, y] = (int(o[0] * m), int(o[1] * m), int(o[2] * m), 255)
    return cv.img


def _taula_dalt(mel=True, marca=False):
    """La tapa de la taula vista de dalt (138×64): pergamins, el xarop, les plomes, la gerra de mel (o la rodona)."""
    w, d = 138, 64
    cv = Canvas(w, d)
    for y in range(d):
        for x in range(w):
            cv.put(x, y, FUSTA, 3.8 + (nz(x / 14, y / 2, 41) - 0.5) * 0.8 - (1.0 if y % 16 == 0 else 0), lit=0)
    for k, (px, py, pw, ph, ang) in enumerate(((10, 8, 30, 22, 0.1), (36, 26, 34, 26, -0.15), (70, 6, 26, 20, 0.2))):
        c, s = math.cos(ang), math.sin(ang)
        for yy in range(-ph // 2, ph // 2):
            for xx in range(-pw // 2, pw // 2):
                X, Y = px + pw / 2 + xx * c - yy * s, py + ph / 2 + xx * s + yy * c
                lvl = 4.4 - abs(yy) / ph * 0.6 - (0.9 if (yy + ph // 2) % 4 == 2 and abs(xx) < pw // 2 - 3 else 0)
                cv.put(X, Y, PERGAMI, lvl, lit=0)
    if marca:
        # la rodona enganxosa de mel (on era la gerra) i un regalim
        mx, my = w / 2 + MEL[0], d / 2 - MEL[1]
        cv.disc(mx, my, 9, 9, [(120, 70, 16), (170, 110, 26), (214, 150, 40), (240, 196, 90)],
                lambda nx, ny: 2.2 - ny if math.hypot(nx, ny) > 0.6 else -9, lit=0)
        cv.disc(mx + 3, my + 12, 2.6, 4.5, [(120, 70, 16), (170, 110, 26), (214, 150, 40), (240, 196, 90)], 2.6, lit=0)
    return cv.img


def _manat_img(seed, cardo=False):
    """Un manat d'herbes penjat cap per avall (18×44): les tiges lligades a dalt i les fulles seques; el cardo, un cap
    espinós i sec, violaci i gris."""
    w, h = 22, 46
    cv = Canvas(w, h, transparent=True)
    cx = w / 2
    cv.line(cx, 0, cx, 6, LLI, 2.4, lit=0)                                  # el cordill
    cv.rect(cx - 2, 6, cx + 2, 8, LLI, 3.0, lit=0)
    if cardo:
        for k in range(5):
            cv.line(cx - 2 + k, 8, cx - 4 + k * 2, 26, HERBA, 2.6, lit=0)
        # el cap espinós
        cv.disc(cx, 32, 7, 7, [(40, 30, 44), (70, 54, 78), (104, 84, 112), (140, 120, 140), (180, 168, 170)],
                lambda nx, ny: 2.4 - ny * 1.0 - nx * 0.5, lit=0)
        for a in range(0, 360, 24):
            x0, y0 = cx + math.cos(math.radians(a)) * 6, 32 + math.sin(math.radians(a)) * 6
            x1, y1 = cx + math.cos(math.radians(a)) * 10, 32 + math.sin(math.radians(a)) * 10
            cv.line(x0, y0, x1, y1, HERBA, 4.8, lit=0)
        for a in range(200, 341, 28):                                       # la corona de fulles seques, a sobre
            cv.line(cx, 25, cx + math.cos(math.radians(a)) * 9, 25 + math.sin(math.radians(a)) * 5, HERBA, 3.4, lit=0)
        return cv.img
    rng = np.random.default_rng(seed)
    for k in range(14):
        x1 = cx + (rng.random() - 0.5) * 16
        y1 = 26 + rng.random() * 18
        cv.line(cx + (rng.random() - 0.5) * 3, 8, x1, y1, HERBA, 2.0 + rng.random() * 1.5, lit=0)
        cv.disc(x1, y1 - 2, 2.2, 3.2, HERBA, 2.8 + rng.random() * 1.6 - (seed % 3) * 0.4, lit=0)
    return cv.img


def _cordill_img():
    cv = Canvas(22, 14, transparent=True)
    cv.line(11, 0, 11, 6, LLI, 2.4, lit=0)
    cv.rect(9, 6, 13, 8, LLI, 3.0, lit=0)
    cv.line(11, 8, 12, 12, LLI, 2.0, lit=0)
    return cv.img


def _gerra_mel_img():
    """La gerra de mel (16×22): fang vidriat, amb la boca tapada amb un drap lligat."""
    cv = Canvas(18, 24, transparent=True)
    for y in range(6, 23):
        t = (y - 6) / 16
        half = 6 + math.sin(t * math.pi) * 2.6
        for x in range(int(9 - half), int(9 + half) + 1):
            cv.put(x, y, [(70, 40, 16), (110, 66, 22), (150, 96, 34), (190, 134, 54), (226, 180, 96)],
                   3.0 - (x - 9) / half * 1.2 + (1.2 if -0.6 < (x - 9) / half < -0.35 else 0), lit=0)
    cv.rect(3, 2, 15, 6, LLI, 4.0, lit=0)
    cv.rect(4, 6, 14, 7, FUSTA, 2.0, lit=0)
    cv.rect(6, 13, 12, 17, PERGAMI, 4.6, lit=0)
    return cv.img


def _xarop_img():
    cv = Canvas(10, 20, transparent=True)
    _flasco(cv, 5, 19, 18, VIDREV, None, forma=0)
    return cv.img


def _espelma_img(h=12):
    cv = Canvas(8, h + 8, transparent=True)
    cv.rect(2, 7, 5, h + 6, [(150, 140, 110), (200, 190, 160), (236, 228, 200)], 1.4, lit=0)
    cv.disc(3.5, h + 7, 3.5, 1.4, FERRO, 3.0, lit=0)
    return cv.img


# ─── L'escena ────────────────────────────────────────────────────────────────

def _terra_fn(s, t, P):
    x, z = P[0], P[2]
    fila = int((z + 600) // 34)
    off = (fila % 2) * 20
    peca = int((x + off + 600) // 40)
    lvl = 2.8 + (hr(peca & 255, fila & 255, 51) - 0.5) * 0.9 + (nz(x / 6, z / 6, 52) - 0.5) * 0.5
    if (z + 600) % 34 < 1.4 or (x + off + 600) % 40 < 1.4:
        lvl -= 1.2
    return lvl


def _sostre_fn(s, t, P):
    return 1.6 + (nz(P[0] / 4, P[2] / 30, 53) - 0.5) * 0.5


@functools.lru_cache(maxsize=None)
def _textures():
    return _paret_fons(), _paret_esq(), _prestatges()


def _girat(cx, cz, ang):
    c, s = math.cos(ang), math.sin(ang)
    return lambda lx, lz: (cx + lx * c - lz * s, cz + lx * s + lz * c)


def _cilindre(e, sid, cx, cz, r, y0, y1, ramp, lvl, llum=215, n=18):
    for i in range(n):
        a0, a1 = math.pi * 2 * i / n, math.pi * 2 * (i + 1) / n
        sh = math.cos((a0 + a1) / 2 - math.radians(llum)) * 1.4
        P0 = (cx + math.cos(a0) * r, y1, cz + math.sin(a0) * r)
        P1 = (cx + math.cos(a1) * r, y1, cz + math.sin(a1) * r)
        e.quad(sid, P1, P0, (P0[0], y0, P0[2]), (P1[0], y0, P1[2]), ramp=ramp,
               lvl=(lambda s, t, P, l=lvl + sh: l - (0.6 if P[1] < y0 + 3 else 0)))


def _disc(e, sid, cx, cz, r, y, ramp, lvl):
    e.quad(sid, (cx - r, y, cz + r), (cx + r, y, cz + r), (cx + r, y, cz - r), (cx - r, y, cz - r), ramp=ramp,
           lvl=lambda s, t, P: (lvl(s, t, P) if callable(lvl) else lvl),
           forma=lambda s, t: math.hypot(s - r, t - r) <= r, dues_cares=True)


def escena(cv, cardo=False, mel=False, cardo_agafat=False, mel_agafada=False):
    fons, esq, prest = _textures()
    e = Escena(cv, CAM, _llums(), ambient=-0.6)
    e.quad('sostre', (-100, HW, -300), (XW + 200, HW, -300), (XW + 200, HW, ZW), (-100, HW, ZW), ramp=FUSTA,
           lvl=_sostre_fn, dues_cares=True)
    e.quad('paret_fons', (0, HW, ZW), (XW, HW, ZW), (XW, 0, ZW), (0, 0, ZW), tex=(fons, (0, 0, XW, HW)))
    e.quad('paret_esq', (0, HW, -300), (0, HW, ZW), (0, 0, ZW), (0, 0, -300), tex=(esq, (0, 0, ZW + 300, HW)))
    e.quad('paret_dreta', (XW, HW, ZW), (XW, HW, -300), (XW, 0, -300), (XW, 0, ZW), ramp=PEDRA, lvl=2.0)
    e.quad('terra', (0, 0, ZW), (XW, 0, ZW), (XW, 0, -300), (0, 0, -300), ramp=LLOSA, lvl=_terra_fn)
    # les bigues del sostre
    for z in range(-60, ZW, 64):
        e.caixa('sostre', -100, XW, HW - 12, HW, z, z + 12, FUSTA, 1.4,
                cares={'sota': {'ramp': FUSTA, 'lvl': 2.0}, 'davant': {'ramp': FUSTA, 'lvl': 2.4}})
    e.foscor('ombra_fons', (0, 0.2, ZW), (XW, 0.2, ZW), (XW, 0.2, ZW - 30), (0, 0.2, ZW - 30),
             lambda s, t: 0.45 * (1 - t / 30))
    e.foscor('ombra_esq', (0, 0.2, ZW), (24, 0.2, ZW), (24, 0.2, -200), (0, 0.2, -200), lambda s, t: 0.4 * (1 - s / 24))
    # els prestatges: el moble (els costats i dalt) i la cara de davant amb tot el que hi ha
    p0, p1, pd = PREST
    e.caixa('prestatges', p0 - 4, p1 + 4, 0, HW - 2, ZW - pd, ZW, FUSTA, 2.2,
            cares={'davant': {'tex': (prest, (0, 0, p1 - p0, HW))}, 'dreta': {'ramp': FUSTA, 'lvl': 2.6},
                   'esquerra': {'ramp': FUSTA, 'lvl': 1.6}})
    # l'espelma del prestatge (a la lleixa de 92, a l'esquerra)
    e.sprite('espelmes', _espelma_img(10), (4, 17), (60, 92, ZW - pd - 1))
    # la llar, a la paret de l'esquerra: una boca de pedra amb el carbó encès, i la campana
    z0, z1, hb, fd = LLAR
    e.caixa('llar', 0, fd, 0, 14, z0, z1, PEDRA, 3.4, cares={'dalt': {'ramp': PEDRA, 'lvl': 3.0},
                                                            'dreta': {'ramp': PEDRA, 'lvl': 3.6}})
    # el carbó: brases (vermell fosc i taronja)
    e.quad('llar', (2, 14.2, z1 - 4), (fd - 4, 14.2, z1 - 4), (fd - 4, 14.2, z0 + 4), (2, 14.2, z0 + 4), ramp=FOC,
           lvl=lambda s, t, P: 1.2 + (2.6 if nz(P[0] / 3, P[2] / 3, 7) > 0.55 else 0.4) - s / fd * 0.8)
    for zz in (z0, z1):
        e.caixa('llar', 0, fd, 14, hb, zz - 6, zz, PEDRA, 3.0, cares={'dreta': {'ramp': PEDRA, 'lvl': 3.4}})
    # la campana (un tronc de piràmide de guix ennegrit)
    e.quad('llar', (fd + 8, hb + 4, z0 - 12), (fd + 8, hb + 4, z1 + 6), (0, HW, z1 + 2), (0, HW, z0 - 8),
           ramp=PEDRA, lvl=lambda s, t, P: 1.4 + (nz(P[1] / 6, P[2] / 6, 71) - 0.5) * 0.6, dues_cares=True)
    e.caixa('llar', 0, fd + 10, hb, hb + 6, z0 - 12, z1 + 6, FUSTA, 2.6)
    # la taula, girada: les potes, la tapa amb els pergamins
    cx, cz, tw, td, th, ang = TAULA
    g = _girat(cx, cz, ang)
    e.foscor('ombra_taula', *[(g(lx, lz)[0], 0.2, g(lx, lz)[1]) for lx, lz in
                              ((-tw / 2 - 6, td / 2 + 6), (tw / 2 + 14, td / 2 + 6), (tw / 2 + 14, -td / 2 - 14),
                               (-tw / 2 - 6, -td / 2 - 14))], lambda s, t: 0.5)
    for lx in (-tw / 2 + 6, tw / 2 - 6):
        for lz in (-td / 2 + 5, td / 2 - 5):
            X, Z = g(lx, lz)
            e.caixa('taula', X - 3, X + 3, 0, th - 4, Z - 3, Z + 3, FUSTA, 2.4)
    e.caixa_girada('taula', cx, cz - td / 2 + 5, tw - 12, 2, 10, ang, FUSTA, 2.0, y0=th - 14)
    e.caixa_girada('taula', cx, cz, tw, td, 4, ang, FUSTA, 3.0, y0=th - 4,
                   cares={'dalt': {'tex': (_taula_dalt(marca=mel_agafada), (0, 0, 138, 64))},
                          'davant': {'ramp': FUSTA, 'lvl': 2.6}})
    # damunt la taula: el xarop, l'espelma i (prop) la gerra de mel
    X, Z = g(-36, 8)
    e.sprite('taula', _xarop_img(), (5, 19), (X, th, Z))
    X, Z = g(20, -14)
    e.sprite('espelmes', _espelma_img(14), (4, 21), (X, th, Z))
    if mel:
        X, Z = g(*MEL)
        e.sprite('mel', _gerra_mel_img(), (9, 23), (X, th, Z))
    # el morter gran, a terra
    mx, mz, mr, mh = MORTER
    e.foscor('ombra_morter', (mx - 30, 0.2, mz + 20), (mx + 30, 0.2, mz + 20), (mx + 30, 0.2, mz - 34), (mx - 30, 0.2, mz - 34),
             lambda s, t: 0.5 * max(0.0, 1 - math.hypot((s - 30) / 26, (t - 30) / 24)))
    _cilindre(e, 'morter', mx, mz, mr, 0, mh, PEDRA, 3.4)
    _disc(e, 'morter', mx, mz, mr, mh, PEDRA, 4.4)
    _disc(e, 'morter', mx, mz, mr - 5, mh - 0.5, PEDRA, 1.2)
    e.cable('morter', [(mx - 4, mh - 6, mz), (mx + 6, mh + 16, mz - 4), (mx + 12, mh + 30, mz - 6)], FUSTA, 4.0, gruix=4.0)
    # el tamboret amb la pell d'ovella
    sx, sz, sr, sh = TAMBORET
    for a in (0.6, 2.7, 4.7):
        X, Z = sx + math.cos(a) * sr * 0.6, sz + math.sin(a) * sr * 0.6
        e.caixa('pell_ovella', X - 2, X + 2, 0, sh, Z - 2, Z + 2, FUSTA, 2.4)
    _disc(e, 'pell_ovella', sx, sz, sr, sh, FUSTA, 3.0)
    pell = [(90, 84, 70), (130, 122, 100), (168, 160, 134), (200, 194, 168), (226, 222, 200)]
    _disc(e, 'pell_ovella', sx, sz, sr + 5, sh + 2,
          pell, lambda s, t, P: 2.6 + (1.0 if nz(P[0] / 1.6, P[2] / 1.6, 61) > 0.5 else 0))
    _cilindre(e, 'pell_ovella', sx, sz, sr + 5, sh - 10, sh + 2, pell, 2.4)
    # la biga dels manats, i els manats penjats (el cardo, un prop)
    bz, by = BIGA
    e.caixa('biga', -100, XW, by, by + 10, bz - 5, bz + 5, FUSTA, 2.2,
            cares={'sota': {'ramp': FUSTA, 'lvl': 1.6}, 'davant': {'ramp': FUSTA, 'lvl': 2.6}})
    for k, x in enumerate(MANATS):
        if k == CARDO:
            if cardo:
                e.sprite('cardo', _manat_img(k, cardo=True), (11, 0), (x, by, bz))
            if cardo_agafat:
                e.sprite('cardo', _cordill_img(), (11, 0), (x, by, bz))
            continue
        e.sprite('manats', _manat_img(k * 5 + 1), (11, 0), (x, by, bz))
    # la porta: una mica de claror freda pel terra
    x0, x1, _ = PORTA
    e.claror((x0, 0.3, ZW), (x1, 0.3, ZW), (x1 - 10, 0.3, ZW - 60), (x0 - 30, 0.3, ZW - 60), (110, 120, 150),
             lambda s, t: 0.18 * (1 - t / 60))
    # el bassal càlid de l'espelma de la taula i el de la llar
    e.claror((cx - 120, 0.3, cz + 90), (cx + 120, 0.3, cz + 90), (cx + 120, 0.3, cz - 120), (cx - 120, 0.3, cz - 120),
             (255, 190, 110), lambda s, t: 0.25 * max(0.0, 1 - math.hypot((s - 120) / 120, (t - 120) / 110)))
    e.claror((0, 0.3, z1 + 60), (130, 0.3, z1 + 60), (130, 0.3, z0 - 60), (0, 0.3, z0 - 60), (255, 120, 50),
             lambda s, t: 0.32 * max(0.0, 1 - math.hypot(s / 130, (t - (z1 - z0 + 120) / 2) / 110)))
    # el primer pla: les gerres de fang de la dreta
    for k, (x, z, r, h) in enumerate(GERRES):
        _gerra(e, 'davant', x, z, r, h)
    e.silueta({'davant'}, k=0.45, col=(14, 8, 8))
    return e


def _gerra(e, sid, x, z, r, h):
    """Una gerra de fang grossa (bombada), de discs apilats."""
    n = 14
    for i in range(n):
        y0, y1 = h * i / n, h * (i + 1) / n
        t = (i + 0.5) / n
        rr = r * (0.62 + math.sin(t * math.pi) * 0.38 if t < 0.85 else 0.55)
        _cilindre(e, sid, x, z, rr, y0, y1, FANG, 3.0 - abs(t - 0.6), n=14)
    _disc(e, sid, x, z, r * 0.55, h, FANG, 3.6)
    _disc(e, sid, x, z, r * 0.42, h + 0.2, NEGRE, 0.6)


# ─── Fons, props, animacions ─────────────────────────────────────────────────

@functools.lru_cache(maxsize=None)
def _render(**k):
    cv = Canvas(W, H, light=LIGHT)
    e = escena(cv, **k)
    _calid(cv)
    return fosc_hud(cv.img), e


def _calid(cv):
    """Tota la sala cap al càlid de les espelmes, i els racons més foscos."""
    a = np.asarray(cv.img).astype(np.float32)
    a[..., :3] *= np.array([1.05, 0.94, 0.80], np.float32)
    cv.img.paste(Image.fromarray(a.clip(0, 255).astype(np.uint8), 'RGBA'))
    cv.P = cv.img.load()


def _base():
    return _render()[0]


def bg(cv):
    cv.img.paste(_base())
    cv.P = cv.img.load()


@functools.lru_cache(maxsize=None)
def _MASK(ids):
    return mascara_amo(_render()[1], set(ids))


def _decorat(**k):
    def draw(pc):
        d = np.asarray(diferencia(_render(**k)[0], _base())).copy()
        d[_MASK(('davant',)).array] = 0
        pc.img.alpha_composite(sense_hud(Image.fromarray(d, 'RGBA')))
        pc.P = pc.img.load()
    return draw


PROPS = {
    'cardo': _decorat(cardo=True),
    'mel': _decorat(mel=True),
    'cardo_agafat': _decorat(cardo_agafat=True),
    'mel_agafada': _decorat(mel_agafada=True),
}


def _espelmes_frames():
    """Les flames de les espelmes (la de la taula i la del prestatge) i la claror de les brases, que tremolen."""
    cx, cz, tw, td, th, ang = TAULA
    X, Z = _girat(cx, cz, ang)(20, -14)
    punts = [((X, th + 15, Z), 1.0), ((60, 92 + 11, ZW - PREST[2] - 1), 0.8)]
    out = []
    z0, z1, hb, fd = LLAR
    for i in range(6):
        cv = Canvas(W, H, transparent=True)
        for (P, k) in punts:
            u, v, _ = CAM.projecta(P)
            s = CAM.escala(P) * k
            alt = (3.4 + math.sin(i * 1.9) * 0.8 + hr(i, 3) * 0.6) * s
            dx = math.sin(i * 2.3) * 0.6
            cv.glow(u, v - alt * 0.4, 14 * s, (255, 200, 120), 0.35 + 0.1 * math.sin(i))
            for j in range(int(alt) + 2):
                t = j / max(1, alt)
                wdt = max(0.5, (1 - t) * 1.4 * s)
                for ddx in np.arange(-wdt, wdt + 0.01, 0.5):
                    cv.put(u + dx * t + ddx, v - j, FOC, 6.2 - t * 2.6 - abs(ddx) / wdt * 1.2, lit=0)
        # les brases de la llar, que bateguen
        for k in range(14):
            P = (4 + hr(k, 1) * (fd - 10), 15, z0 + 6 + hr(k, 2) * (z1 - z0 - 12))
            u, v, _ = CAM.projecta(P)
            if (k + i) % 3 == 0:
                cv.flat(u, v, (255, 170, 60))
                cv.flat(u + 1, v, (230, 110, 40))
        # (l'espelma no ha de pintar damunt el primer pla)
        a = np.asarray(cv.img).copy()
        a[_MASK(('davant',)).array] = 0
        a[RH:] = 0
        out.append(Image.fromarray(a, 'RGBA'))
    return out


ANIMS = {'espelmes': {'frames': _espelmes_frames, 'frameDuration': 140}}


# ─── Capes del davant ───────────────────────────────────────────────────────

def _p(x, z, y=0.0):
    u, v, _ = CAM.projecta((x, y, z))
    return round(u), round(v)


def _v_taula():
    """La línia base de la taula: el cantó de davant que queda més al fons."""
    cx, cz, tw, td, th, ang = TAULA
    g = _girat(cx, cz, ang)
    return min(_p(*g(lx, -td / 2))[1] for lx in (-tw / 2, tw / 2))


FRONT = [
    {'id': 'davant_taula', 'mask': lambda x, y: _MASK(('taula', 'espelmes'))(x, y) and y > 60, 'baseline': _v_taula(),
     'zIndex': 20, 'props': ('mel', 'mel_agafada')},
    {'id': 'davant', 'mask': lambda x, y: _MASK(('davant',))(x, y), 'baseline': 999, 'zIndex': 22},
]


# ─── Geometria ───────────────────────────────────────────────────────────────

def _rect(*Ps):
    pts = [CAM.projecta(P) for P in Ps]
    return (max(0, round(min(p[0] for p in pts))), max(0, round(min(p[1] for p in pts))),
            min(W - 1, round(max(p[0] for p in pts))), min(RH - 1, round(max(p[1] for p in pts))))


def _sota(cx, cz, w, d, ang, marge=8):
    g = _girat(cx, cz, ang)
    return [_p(*g(lx, lz)) for lx, lz in ((-w / 2 - marge, -d / 2 - marge), (w / 2 + marge, -d / 2 - marge),
                                          (w / 2 + marge, d / 2 + marge), (-w / 2 - marge, d / 2 + marge))]


_VN = v_escala(CAM, 1.18)


def _a_v(x, v):
    lo, hi = -400.0, ZW
    for _ in range(50):
        z = (lo + hi) / 2
        if CAM.projecta((x, 0, z))[1] > v:
            lo = z
        else:
            hi = z
    return _p(x, (lo + hi) / 2)


_WALK = [_p(LLAR[3] + 10, LLAR[1] + 30), _p(14, ZW - PREST[2] - 30), _p(PREST[1] + 8, ZW - PREST[2] - 10),
         _p(PORTA[0] - 4, ZW - 6), _p(PORTA[1] + 4, ZW - 6), _p(XW - 14, ZW - 20), _a_v(XW - 14, _VN),
         _a_v(LLAR[3] + 10, _VN)]
_VS = [v for _, v in _WALK]

_cx, _cz, _tw, _td, _th, _ang = TAULA
_tp = []
for _lx in (-_tw / 2, _tw / 2):
    for _lz in (-_td / 2, _td / 2):
        _X, _Z = _girat(_cx, _cz, _ang)(_lx, _lz)
        _tp += [(_X, 0, _Z), (_X, _th, _Z)]


_MEL = _girat(_cx, _cz, _ang)(*MEL)


def _prest_rect(xc, y0, y1, half=12):
    z = ZW - PREST[2]
    return _rect((xc - half, y1, z), (xc + half, y0, z))


def _manat_rect(x, alt=44):
    return _rect((x - 10, BIGA[1], BIGA[0]), (x + 10, BIGA[1] - alt, BIGA[0]))


GEOMETRIA = {
    'things': {
        'prestatges': {'rect': _rect((262, HW - 24, ZW - PREST[2]), (PREST[1], 0, ZW - PREST[2])),
                       'walk': _p(290, ZW - PREST[2] - 34)},
        **{nom: {'rect': _prest_rect(cx, 58, 88, 12), 'walk': _p(cx, ZW - PREST[2] - 30)}
           for nom, (cx, _, _) in FLASCONS.items()},
        'atramentum': {'rect': _prest_rect(ATRAMENTUM[0], ATRAMENTUM[1], ATRAMENTUM[1] + 22, 12),
                       'walk': _p(ATRAMENTUM[0], ZW - PREST[2] - 30)},
        'manats': {'rect': _rect((MANATS[3] - 12, BIGA[1] + 4, BIGA[0]), (MANATS[-1] + 12, BIGA[1] - 44, BIGA[0])),
                   'walk': _p(220, BIGA[0] - 70)},
        'cardo': {'rect': _manat_rect(MANATS[CARDO]), 'walk': _p(MANATS[CARDO] + 10, BIGA[0] - 60)},
        'pell_ovella': {'rect': _rect((TAMBORET[0] - 26, TAMBORET[3] + 4, TAMBORET[1]),
                                      (TAMBORET[0] + 26, 0, TAMBORET[1])), 'walk': _p(TAMBORET[0] - 40, TAMBORET[1] + 20)},
        'mel': {'rect': _rect((_MEL[0] - 10, _th + 26, _MEL[1]), (_MEL[0] + 10, _th, _MEL[1])),
                'walk': _p(_cx + 70, _cz - 40)},
        'llar': {'rect': _rect((0, LLAR[2] + 8, LLAR[0] - 10), (LLAR[3], 0, LLAR[1] + 6), (0, 0, LLAR[1])),
                 'walk': _p(LLAR[3] + 30, (LLAR[0] + LLAR[1]) / 2)},
        'morter': {'rect': _rect((MORTER[0] - MORTER[2], MORTER[3] + 30, MORTER[1]), (MORTER[0] + MORTER[2], 0, MORTER[1])),
                   'walk': _p(MORTER[0] - 34, MORTER[1] - 30)},
        'taula': {'rect': _rect(*_tp), 'walk': _p(_cx, _cz - _td / 2 - 30)},
        'porta': {'rect': _rect((PORTA[0], PORTA[2], ZW), (PORTA[1], 0, ZW)), 'walk': _p((PORTA[0] + PORTA[1]) / 2, ZW - 14)},
    },
    'spawns': {'vet': _p((PORTA[0] + PORTA[1]) / 2, ZW - 40), 'gueraula': _p(110, 120)},
    'walkable': _WALK,
    'forats': [_sota(_cx, _cz, _tw, _td, _ang, marge=6),
               _sota(MORTER[0], MORTER[1], 2 * MORTER[2], 2 * MORTER[2], 0, marge=4),
               _sota(TAMBORET[0], TAMBORET[1], 2 * TAMBORET[2] + 10, 2 * TAMBORET[2] + 10, 0, marge=4)],
    'floorSquash': 0.38,
    # La llum dominant: l'espelma de la taula (l'ombra, rodona, cap enfora de la taula).
    'characterShadow': {'enabled': True, 'color': '#140c0a', 'alpha': 0.42, 'squash': 0.38, 'core': 0.6,
                        'light': {'x': _p(_cx + 20, _cz)[0], 'y': _p(_cx + 20, _cz)[1], 'stretch': 0.55, 'reach': 200}},
    'characterLights': {
        'ambient': '#6e6058',
        'lights': [
            {'x': _p(_cx + 20, _cz, 40)[0], 'y': _p(_cx + 20, _cz, 40)[1], 'radius': 260, 'color': '#ffc47a',
             'intensity': 0.45},
            {'x': _p(LLAR[3], (LLAR[0] + LLAR[1]) / 2, 30)[0], 'y': _p(LLAR[3], (LLAR[0] + LLAR[1]) / 2, 30)[1],
             'radius': 240, 'color': '#ff8a40', 'intensity': 0.4},
            {'x': _p(PORTA[0] + 30, ZW - 20, 60)[0], 'y': _p(PORTA[0] + 30, ZW - 20, 60)[1], 'radius': 160,
             'color': '#a8b4d0', 'intensity': 0.2},
        ],
    },
    'regions': [{'id': 'perspectiva', 'active': True, 'scaleEnabled': True, 'scaleWalkSpeed': True,
                 'scaleTop': escala_v(CAM, min(_VS)), 'scaleBottom': escala_v(CAM, max(_VS)),
                 'points': [(0, min(_VS)), (W - 1, min(_VS)), (W - 1, max(_VS)), (0, max(_VS))]}],
}

ajusta_geometria(GEOMETRIA)
