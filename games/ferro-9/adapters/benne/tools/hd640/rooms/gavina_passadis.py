"""
Passadís del mòdul C (La Gavina, Vet). EN 3D (hd640/tres_d.py), a 1×.

Una càmera alta, a la dreta, que mira de biaix la cantonada del fons a l'esquerra:
  - a la paret de l'esquerra, en escorç, la **porta de la cel·la 9** (la de la Vet), amb el pany M-3;
  - a la paret del fons, l'aplic de reixa, l'intèrfon, la caixa de la mànega i, al mig, la **boca del passadís**:
    un passadís de debò que s'enfonsa, amb les portes de les cel·les 10 i 11, la canonada, els fluorescents del
    sostre i, al fons, la **porta de l'hangar** amb el pilot vermell; la línia groga hi porta l'ull;
  - a la dreta del fons, el **cartell del reciclatge**, la **càmera**, la **porta de la Sala de la Memòria** i el
    cartell vell, mig arrencat;
  - el **contenidor de reciclatge**, separat de la paret i girat (s'hi passa per darrere);
  - primer pla: el pilar d'acer de la dreta i la safata de cables que penja del sostre, en silueta.

El detall de les parets ve del dibuix pla de sempre (gavina_passadis_pla_comu.py), projectat; el passadís, el terra i
el contenidor són en 3D. La rajola (decorat) es dibuixa en 3D i en surt la diferència.

El món: x a la dreta (0 = la paret de la cel·la), y amunt (0 = el terra), z cap al fons (300 = la paret del fons);
1 unitat = 1 píxel de sala a la distància on un personatge fa ≈110 px (escala 1).
"""
import functools
import math

import numpy as np

from PIL import Image

import hd640  # noqa: F401  (posa la llibreria de dibuix a 640×360)
from hd.pix import Canvas, Light, W, H, STEEL, CYAN, WARN, ORANGE, PAPER, IRON, SPACE, GRAY, RED  # noqa: F401
from hd640.rooms import gavina_passadis_pla_comu as PL
from hd640.rooms.gavina_passadis_pla_comu import (HULL, DECK, LAMPW, ALARM, SIGN, CORPG, PILOT, hr, text, text_w,
                                                  smile, rivet, hazard, diff)
from hd640.tres_d import Camera, Escena, Llum

BOTTOM = 259                                       # la sala acaba aquí (a sota, la barra de verbs)
ZW = 300                                           # la paret del fons
HW = PL.FLOOR_Y                                    # l'alçada de les parets (el dibuix pla fa 205 fins al terra)
XC = PL.OPEN_X0                                    # al dibuix pla, la cantonada (a l'esquerra, la paret de la cel·la)
XR = 900                                           # on s'acaba la paret del fons (fora de la pantalla)
OX0, OX1 = 0, PL.OPEN_X1 - PL.OPEN_X0             # el passadís (x del món): la paret de la cel·la hi continua
OH = HW - PL.OPEN_TOP                              # l'alçada del passadís
ZF = 820                                           # la paret del fons del passadís (la porta de l'hangar)
LEN = ZF - ZW
DOOR = (26, 126, 64)                               # la porta de l'hangar, al pla del fons: x0, x1, y de dalt (pla)
DOOR_X = OX0 + (DOOR[0] + DOOR[1]) / 2             # x del món de la porta (i de la línia groga)
CELLS = ((110, '10'), (300, '11'))                 # les portes de les cel·les del passadís (x del pla = z − ZW)
TUBES = (380, 500, 620, 740)                       # els fluorescents del sostre del passadís (z)
BIN = (404, 176, 52, 34, 62, 0.42)                 # el contenidor de reciclatge: x, z, ample, fons, alt, gir
PLATE = 60                                         # les planxes del terra
TILE = (120, 180, 120, 180)                         # la rajola solta: x0, x1, z0, z1


def _w(fx):
    """Una x del dibuix pla de la paret del fons (a la dreta del passadís) → la x del món."""
    return fx - XC


def _wz(fx):
    """Una x del dibuix pla de la paret de la cel·la → la z del món."""
    return ZW - XC + fx


def _y(fy):
    """Una y del dibuix pla (el terra, a 205) → l'alçada del món."""
    return HW - fy


CAM = Camera(pos=(320, 185, -260), yaw=-0.22, pitch=0.16, f=440, centre=(320, 100))

LIGHT = Light(ambient=0.3, vignette=None, floor_fade=None)  # (la llum és la del món: la de l'Escena)
LAMP_C = (10, _y(35), _wz(139))                    # l'aplic de reixa, al costat de la cel·la
STRIP_C = (_w(499), _y(40), ZW - 10)               # la tira de llum sobre el cartell
PILOT_C = (DOOR_X, _y(48), ZF - 8)                 # el pilot vermell de la porta de l'hangar
LLUMS = ([Llum(LAMP_C, 260, 1.8, power=1.4), Llum(STRIP_C, 240, 1.5, power=1.4),
          Llum(PILOT_C, 200, 1.6, power=1.5)]
         + [Llum(((OX0 + OX1) / 2, OH - 6, z), 170, 1.1, power=1.5) for z in TUBES])


# ─── Les textures: el dibuix pla de sempre ───────────────────────────────────

def _llum_pla():
    """La llum del dibuix pla, sense la vinyeta, ni l'enfosquiment de baix, ni els bassals del terra."""
    l = Light(ambient=0.5, vignette=None, floor_fade=None)
    l.points = list(PL.LIGHT.points)
    return l


@functools.lru_cache(maxsize=None)
def _paret(t=0.0, arrencat=False):
    """Les parets del vestíbul, de cara: la cel·la 9, l'intèrfon, la mànega, la llinda, el cartell, la càmera i la
    porta de la Sala de la Memòria (el passadís pla del mig no es fa servir)."""
    cv = Canvas(light=_llum_pla())
    PL.bg(cv, t, arrencat=arrencat)
    return cv.img


def _sostre_pla(cv, x0, x1):
    """La biga del sostre i la safata de cables (com al dibuix pla), entre x0 i x1."""
    cv.rect(x0, 0, x1, 12, HULL, lambda x, y: 0.8 + (0.6 if y in (9, 10) else 0) + (hr(x // 32, 3) - 0.5) * 0.2)
    cv.hline(x0, x1, 13, HULL, 3.4)
    cv.hline(x0, x1, 14, HULL, 1.8)
    cv.hline(x0, x1, 15, HULL, 1.0)
    for x in range(x0, x1 + 1):
        cv.put(x, 18, IRON, 3.2)
        cv.put(x, 19, IRON, 2.6)
        cv.put(x, 20, IRON, 1.6)
        if x % 12 == 0:
            cv.vline(x, 16, 20, IRON, 3.0)


@functools.lru_cache(maxsize=None)
def _nua():
    """La paret d'acer nua (amb la biga i la safata): per als trossos on el dibuix pla no arriba."""
    cv = Canvas(light=Light(ambient=0.5, vignette=None, floor_fade=None))
    PL.wall(cv, 0, W - 1, seed=5)
    _sostre_pla(cv, 0, W - 1)
    # un extintor i un rètol d'evacuació, perquè la paret de prop no sigui buida
    cv.rect(300, 120, 312, 168, RED, lambda x, y: 3.2 - (x - 300) * 0.12 + (0.8 if x == 300 else 0))
    cv.rect(302, 112, 309, 119, IRON, 2.6)
    cv.rect(296, 116, 302, 118, IRON, 2.0)
    cv.rect(302, 132, 310, 146, PAPER, 3.6, 0.3)
    cv.rect(420, 60, 470, 74, PILOT, 1.4, 0)
    text(cv, 424, 64, 'EVACUACIÓ', PILOT, 3.6, 0)
    return cv.img


def _porta_cella(cv, x0, num, y_top=77):
    """Una porta de cel·la del passadís, de cara (com la de la 9, més senzilla), a partir de x0."""
    x1 = x0 + 60
    cv.rect(x0 - 5, y_top - 8, x1 + 5, PL.WALL_B, HULL, lambda x, y: 1.0 if x in (x0 - 5, x1 + 5) else 3.0)
    for y in range(y_top, HW):
        for x in range(x0, x1 + 1):
            u = (x - x0) / (x1 - x0)
            lvl = 2.2 + math.sin(u * math.pi) * 0.5 - u * 0.4 + (hr(x // 3, y // 4, 12) - 0.5) * 0.12
            if (y - y_top) in (45, 93):
                lvl -= 1.2
            if y > 176:
                lvl -= (y - 176) / 28 * 0.9
            cv.put(x, y, HULL, lvl)
    wx0, wx1 = x0 + 16, x1 - 16
    cv.rect(wx0 - 2, 89, wx1 + 2, 113, HULL, 1.0)
    cv.rect(wx0, 91, wx1, 111, SPACE, lambda x, y: 1.2 + (y - 91) / 26, 0)
    for x in range(wx0 + 3, wx1, 5):
        cv.vline(x, 91, 111, HULL, 3.6)
        cv.vline(x + 1, 91, 111, HULL, 1.8)
    cv.rect(x0 + 18, 166, x1 - 18, 175, HULL, lambda x, y: 1.0 if y == 175 else (3.8 if y == 166 else 2.6))
    # el pany, amb el pilot cian
    cv.rect(x0 + 4, 133, x0 + 12, 150, HULL, lambda x, y: 4.0 if x == x0 + 4 else 3.0)
    cv.rect(x0 + 6, 137, x0 + 10, 140, CYAN, 3.6, 0)
    # el número, gros (es veu en escorç)
    tw = text_w(num) * 2
    cv.rect(x0 + 30 - tw // 2 - 4, 58, x0 + 30 + tw // 2 + 4, 76, SIGN, lambda x, y: 4.0 - (y - 58) * 0.08, 0.4)
    xx = x0 + 30 - tw // 2
    for ch in num:
        for j, row in enumerate(PL.FONT7[ch]):
            for i, c in enumerate(row):
                if c == '#':
                    cv.rect(xx + i * 2, 60 + j * 2, xx + i * 2 + 1, 61 + j * 2, HULL, 0.6, 0)
        xx += (len(PL.FONT7[ch][0]) + 1) * 2


@functools.lru_cache(maxsize=None)
def _passadis_esq():
    """La paret esquerra del passadís (x del pla = z − ZW): planxes, el passamà i les portes de les cel·les 10 i 11."""
    cv = Canvas(LEN, H, light=Light(ambient=0.3, vignette=None, floor_fade=None))
    PL.wall(cv, 0, LEN - 1, y0=PL.OPEN_TOP, seed=2)
    for x0, num in CELLS:
        _porta_cella(cv, x0, num)
    return cv.img


@functools.lru_cache(maxsize=None)
def _passadis_dre():
    """La paret dreta del passadís (x del pla = ZF − z): planxes i passamà (la canonada és en 3D)."""
    cv = Canvas(LEN, H, light=Light(ambient=0.3, vignette=None, floor_fade=None))
    PL.wall(cv, 0, LEN - 1, y0=PL.OPEN_TOP, seed=6)
    return cv.img


@functools.lru_cache(maxsize=None)
def _fons(t=0.0):
    """La paret del fons del passadís (x del pla = x del món − OX0): la porta de l'hangar, amb les franges, el
    rètol taronja i el pilot vermell, que polsa amb `t`."""
    al = math.sin(2 * math.pi * t * 2)
    w = OX1 - OX0
    cv = Canvas(w, H, light=Light(ambient=0.3, vignette=None, floor_fade=None))
    PL.wall(cv, 0, w - 1, y0=PL.OPEN_TOP, seed=4)
    x0, x1, top = DOOR
    mid = (x0 + x1) / 2
    cv.rect(x0 - 5, top - 5, x1 + 5, PL.WALL_B, HULL, lambda x, y: 0.4 if x < x0 - 2 or x > x1 + 2 or y < top - 2 else 1.2, 0)
    for y in range(top, HW):
        for x in range(x0, x1 + 1):
            lvl = 2.2 - abs(x - mid) / 60 + (0.8 if x in (x0, round(mid) + 1) else 0) - (0.9 if x == round(mid) else 0)
            if (y - top) % 18 == 0:
                lvl -= 0.4                                               # les costelles de la porta
            cv.put(x, y, HULL, lvl, 0.3)
    hazard(cv, x0, top + 24, x1, top + 34, lit=0.2, lvl=3.0, w=6)
    cv.rect(x0 + 8, top + 50, x0 + 22, top + 60, ORANGE, lambda x, y: 3.2 - (y - top - 50) * 0.1, 0)   # el rètol
    text(cv, x0 + 10, top + 52, 'H', HULL, 0.6, 0)
    for hx in (round(mid) - 6, round(mid) + 4):
        cv.rect(hx, top + 72, hx + 2, top + 90, HULL, 3.0, 0.3)                                # les nanses
    # el pilot vermell, sobre la porta
    cy = top - 16
    cv.rect(round(mid) - 12, cy - 6, round(mid) + 12, cy + 6, HULL, 1.2, 0)
    cv.rect(round(mid) - 10, cy - 4, round(mid) + 10, cy + 4, ALARM, lambda x, y: 4.2 + 0.9 * al - abs(y - cy) * 0.2, 0)
    for x in range(round(mid) - 9, round(mid) + 10, 4):
        cv.vline(x, cy - 4, cy + 4, ALARM, 2.6 + 0.6 * al, 0)
    cv.glow(mid, cy, 40, (255, 70, 60), 0.45 + 0.2 * al)
    cv.tint(0, PL.OPEN_TOP, w - 1, HW, (255, 60, 50),
            lambda x, y: 0.3 * (1 + 0.3 * al) * max(0.0, 1 - math.hypot(x - mid, (y - cy) * 1.1) / 120) ** 2)
    return cv.img


@functools.lru_cache(maxsize=None)
def _contenidor():
    """El davant del contenidor de reciclatge: verd de la corporació, el somriure i el rètol."""
    cv = Canvas(120, 80, light=Light(ambient=0.3, vignette=None, floor_fade=None))
    bw, bh = BIN[2], BIN[4]
    cv.rect(0, 0, bw - 1, bh - 1, CORPG, lambda x, y: 2.6 - y * 0.012 + (hr(x // 3, y // 3, 4) - 0.5) * 0.2)
    cv.hline(0, bw - 1, 0, CORPG, 4.0)
    cv.hline(0, bw - 1, bh - 1, CORPG, 0.8)
    cv.rect(4, 8, bw - 5, 22, SIGN, 4.2, 0)
    text(cv, 7, 12, 'PAPER', CORPG, 1.0, 0)
    smile(cv, bw - 13, 15, 5, lit=0, lvl=3.8)
    smile(cv, bw // 2, 42, 11, lit=0, lvl=3.4)
    for x in range(3, bw - 3):                                         # rascades i brutícia de baix
        if hr(x, 9) > 0.8:
            cv.vline(x, bh - 10 + int(hr(x, 3) * 6), bh - 2, CORPG, 1.4)
    return cv.img


# ─── Les superfícies ────────────────────────────────────────────────────────

def _terra(s, t, P):
    """Les planxes d'acer del terra, en coordenades del món: costures, la trama antilliscant i els cargols."""
    x, z = P[0], P[2]
    ui, vi = math.floor(x / PLATE), math.floor(z / PLATE)
    fu, fv = x - ui * PLATE, z - vi * PLATE
    v = 2.6 + (hr(ui, vi, 31) - 0.5) * 0.5
    if (int(x * 0.5) + int(z * 0.5)) % 4 == 0 and (int(x * 0.5) - int(z * 0.5)) % 6 < 2:
        v += 0.35                                                       # la trama de rombets
    if hr(ui, vi, int(x) // 6, 5) > 0.985:
        v -= 0.4
    if fu < 1.0 or fv < 1.0:
        return 0.5                                                      # la costura
    if fu < 2.2 or fv > PLATE - 1.6:
        v += 0.5                                                        # el cantell il·luminat
    elif fu > PLATE - 1.8 or fv < 2.2:
        v -= 0.5
    if (4 < fu < 6.5 or PLATE - 6.5 < fu < PLATE - 4) and (4 < fv < 6.5 or PLATE - 6.5 < fv < PLATE - 4):
        v += 1.4                                                        # els cargols
    return v


def _groc(s, t, P):
    """La línia groga de guia, gastada on trepitja tothom."""
    x, z = P[0], P[2]
    v = 3.0 - (0.5 if abs(x - DOOR_X) > 4.5 else 0)
    if hr(int(x) // 2, int(z) // 3, 33) > 0.84 and z < ZW:
        v -= 1.0
    if math.floor(z / PLATE) * PLATE + 1.0 > z:
        v = 1.0
    return v


def _sostre(s, t, P):
    z = P[2]
    v = 1.0 + (hr(int(P[0]) // 53, int(z) // 60, 2) - 0.5) * 0.3
    if z % 60 < 3:
        v -= 0.6                                                        # les costelles del sostre
    elif z % 60 < 5:
        v += 0.4
    return v


def _caixa_tex(e, sid, cx, cz, w, d, h, ang, ramp, lvl, front=None, y0=0.0, cares=None):
    c = {'dalt': {'ramp': ramp, 'lvl': lvl + 0.8}, 'esquerra': {'ramp': ramp, 'lvl': lvl - 0.6},
         'dreta': {'ramp': ramp, 'lvl': lvl - 0.9}}
    if front is not None:
        c['davant'] = {'tex': front}
    c.update(cares or {})
    e.caixa_girada(sid, cx, cz, w, d, h, ang, ramp, lvl, y0=y0, cares=c)


FOSC = [(4, 5, 8), (8, 10, 14), (13, 15, 20), (19, 22, 28), (27, 30, 38), (37, 41, 50)]


def escena(cv, tex, estat=frozenset()):
    """Tota la sala, de lluny a prop. `estat`: els decorats que hi són ('rajola'). → l'Escena."""
    e = Escena(cv, CAM, LLUMS, ambient=-0.2)
    zn = CAM.pos[2] + 60
    paret, nua = tex['paret'], tex['nua']
    # ── el passadís (de lluny a prop) ──
    e.quad('passadis_fons', (OX0, OH, ZF), (OX1, OH, ZF), (OX1, 0, ZF), (OX0, 0, ZF),
           tex=(tex['fons'], (0, PL.OPEN_TOP, OX1 - OX0, HW)))
    e.quad('passadis_sostre', (OX0, OH, ZF), (OX1, OH, ZF), (OX1, OH, ZW), (OX0, OH, ZW), ramp=HULL, lvl=_sostre,
           dues_cares=True)
    e.quad('passadis_esq', (OX0, OH, ZW), (OX0, OH, ZF), (OX0, 0, ZF), (OX0, 0, ZW),
           tex=(tex['esq'], (0, PL.OPEN_TOP, LEN, HW)))
    e.quad('passadis_dre', (OX1, OH, ZF), (OX1, OH, ZW), (OX1, 0, ZW), (OX1, 0, ZF),
           tex=(tex['dre'], (0, PL.OPEN_TOP, LEN, HW)))
    e.quad('passadis_terra', (OX0, 0, ZF), (OX1, 0, ZF), (OX1, 0, ZW), (OX0, 0, ZW), ramp=DECK,
           lvl=_terra)
    e.quad('passadis_terra', (DOOR_X - 6, 0.2, ZF), (DOOR_X + 6, 0.2, ZF), (DOOR_X + 6, 0.2, ZW),
           (DOOR_X - 6, 0.2, ZW), ramp=WARN, lvl=_groc)
    # la canonada de la paret dreta, amb les abraçadores, i els fluorescents
    e.tub('passadis_canonada', (6, 158, ZF), (6, 158, ZW), 4, IRON, 2.6, brides=70, llum_dir=(0.6, 1.0))
    for k, z in enumerate(TUBES):
        e.caixa(f'tub_{k}', (OX0 + OX1) / 2 - 46, (OX0 + OX1) / 2 + 46, OH - 4, OH, z - 3, z + 3, LAMPW, 4.4,
                cares={'sota': {'ramp': LAMPW, 'lvl': 5.0}, 'davant': {'ramp': HULL, 'lvl': 1.6}})
    # els bassals dels fluorescents i la claror vermella del pilot, al terra del passadís
    e.claror((OX0, 0.4, ZF), (OX1, 0.4, ZF), (OX1, 0.4, ZW), (OX0, 0.4, ZW), (190, 225, 255),
             lambda s, t: 0.16 * max(math.exp(-((ZF - t - z) / 40) ** 2) for z in TUBES)
             * max(0.0, 1 - abs(s - (OX1 - OX0) / 2) / 130))
    e.claror((OX0, 0.5, ZF), (OX1, 0.5, ZF), (OX1, 0.5, ZF - 200), (OX0, 0.5, ZF - 200), (255, 60, 50),
             lambda s, t: 0.32 * max(0.0, 1 - t / 200) ** 1.5)
    e.foscor('passadis_racons', (OX0, 0.6, ZF), (OX1, 0.6, ZF), (OX1, 0.6, ZW), (OX0, 0.6, ZW),
             lambda s, t: 0.5 * max(0.0, 1 - min(s, OX1 - OX0 - s) / 16))
    # ── el vestíbul ──
    e.quad('sostre', (0, HW, zn), (XR, HW, zn), (XR, HW, ZW), (0, HW, ZW), ramp=HULL, lvl=_sostre, dues_cares=True)
    # la paret de la cel·la (x = 0): de prop, la paret nua; cap a la boca del passadís, el dibuix pla (x 0..200)
    zc = ZW - XC
    e.quad('paret_esq_prop', (0, HW, zn), (0, HW, zc), (0, 0, zc), (0, 0, zn), tex=(nua, (W - (zc - zn), 0, W, HW)))
    e.quad('paret_esq', (0, HW, zc), (0, HW, ZW), (0, 0, ZW), (0, 0, zc), tex=(paret, (0, 0, XC, HW)))
    # la paret del fons (z = 300): la llinda de la boca del passadís, el dibuix pla a la dreta i, més enllà, nua
    e.quad('llinda', (OX0, HW, ZW), (OX1, HW, ZW), (OX1, OH, ZW), (OX0, OH, ZW),
           tex=(paret, (PL.OPEN_X0, 0, PL.OPEN_X1 + 1, PL.OPEN_TOP)))
    e.quad('paret_fons_dreta', (OX1, HW, ZW), (_w(W), HW, ZW), (_w(W), 0, ZW), (OX1, 0, ZW),
           tex=(paret, (PL.OPEN_X1 + 1, 0, W, HW)))
    e.quad('paret_fons_lluny', (_w(W), HW, ZW), (XR, HW, ZW), (XR, 0, ZW), (_w(W), 0, ZW),
           tex=(nua, (0, 0, XR - _w(W), HW)))
    # la canonada de la paret de la cel·la, que s'enfonsa pel passadís
    e.tub('canonada', (6, 158, ZW), (6, 158, zn + 30), 4, IRON, 2.6, brides=70, llum_dir=(0.6, 1.0))
    # el terra
    e.quad('terra', (0, 0, ZW), (XR, 0, ZW), (XR, 0, zn), (0, 0, zn), ramp=DECK,
           lvl=_terra)
    e.quad('terra', (DOOR_X - 6, 0.2, ZW), (DOOR_X + 6, 0.2, ZW), (DOOR_X + 6, 0.2, zn), (DOOR_X - 6, 0.2, zn),
           ramp=WARN, lvl=_groc)
    # la rajola solta (decorat): el forat, la planxa aixecada pel cantó de davant i el paper que treu el cap
    if 'rajola' in estat:
        x0, x1, z0, z1 = TILE
        e.quad('rajola', (x0, 0.3, z1), (x1, 0.3, z1), (x1, 0.3, z0), (x0, 0.3, z0), ramp=DECK,
               lvl=lambda s, t, P: 0.2 + (0.4 if t > 50 else 0))
        lift = lambda s, t, P: _terra(s, t, (P[0] - 2, 0, P[2] - 2)) + 1.4                # noqa: E731
        e.quad('rajola', (x0, 1.0, z1), (x1, 1.0, z1), (x1 + 1, 13.0, z0 + 3), (x0 + 1, 13.0, z0 + 3), ramp=DECK,
               lvl=lift, dues_cares=True)                                                 # la planxa, aixecada
        e.quad('rajola', (x0 + 1, 13.0, z0 + 3), (x1 + 1, 13.0, z0 + 3), (x1 + 1, 10.0, z0 + 3), (x0 + 1, 10.0, z0 + 3),
               ramp=DECK, lvl=4.4, dues_cares=True)                                       # el cantell de davant
        e.quad('rajola', (x0 + 14, 5.0, z0 + 14), (x0 + 30, 5.0, z0 + 14), (x0 + 30, 0.6, z0 + 4),
               (x0 + 14, 0.6, z0 + 4), ramp=PAPER, lvl=lambda s, t, P: 4.6 - (1.8 if 4 < t < 5 and s > 3 else 0),
               dues_cares=True)                                                           # el paper doblegat
        for cx_, cz_ in ((x1 + 10, z0 - 6), (x1 + 4, z0 - 12)):
            e.caixa('rajola', cx_ - 1.5, cx_ + 1.5, 0, 1.5, cz_ - 1.5, cz_ + 1.5, DECK, 5.0)   # cargols fora de lloc
    # la llum: els bassals de l'aplic i de la tira, la del passadís que s'aboca al vestíbul
    for (lx, _, _), k in ((LAMP_C, 0.22), (STRIP_C, 0.2)):
        e.claror((lx - 130, 0.4, ZW), (lx + 130, 0.4, ZW), (lx + 130, 0.4, ZW - 200), (lx - 130, 0.4, ZW - 200),
                 (200, 230, 255), lambda s, t, k=k: k * max(0.0, 1 - math.hypot((s - 130) / 110, (t - 20) / 150)) ** 1.3)
    e.claror((OX0, 0.5, ZW), (OX1, 0.5, ZW), (OX1 + 40, 0.5, ZW - 120), (OX0 - 40, 0.5, ZW - 120), (255, 90, 70),
             lambda s, t: 0.12 * max(0.0, 1 - t / 120) * max(0.0, math.sin(math.pi * min(1.0, s / (224 + t * 0.66)))))
    # la foscor dels racons i del peu de les parets
    e.foscor('racons', (0, 0.5, ZW), (XR, 0.5, ZW), (XR, 0.5, zn), (0, 0.5, zn),
             lambda s, t: 0.0 if OX0 < s < OX1 and t < 3 else max(0.55 * max(0.0, 1 - t / 22), 0.5 * max(0.0, 1 - s / 22)))
    e.foscor('sostre_fosc', (0, HW - 0.5, ZW - 0.6), (XR, HW - 0.5, ZW - 0.6), (XR, 0, ZW - 0.6), (0, 0, ZW - 0.6),
             lambda s, t: 0.0 if s < OX1 else 0.4 * max(0.0, 1 - t / 40))
    # els cables pel terra, de la paret de la cel·la cap al passadís (trenquen la línia de la paret)
    e.cable('cables', [(3, 0.8, 0), (16, 0.8, 70), (5, 0.8, 140), (24, 0.8, 250), (12, 0.8, ZW + 60)],
            [(4, 4, 8), (20, 20, 28), (40, 40, 52), (70, 70, 84)], 2.0, gruix=2.4)
    # una caixa d'eines i una galleda arran de paret, a la dreta del passadís
    e.caixa_girada('trastos', OX1 + 34, ZW - 18, 34, 18, 16, -0.12, STEEL, 2.2,
                   cares={'davant': {'ramp': RED, 'lvl': lambda s, t, P: 2.6 - (1.2 if abs(t - 5) < 0.8 else 0)},
                          'dalt': {'ramp': RED, 'lvl': 3.4}})
    # el contenidor de reciclatge, separat i girat, amb la seva ombra
    bx, bz, bw, bd, bh, ba = BIN
    e.foscor('ombra_contenidor', (bx - 50, 0.6, bz + 40), (bx + 40, 0.6, bz + 40), (bx + 40, 0.6, bz - 30),
             (bx - 50, 0.6, bz - 30), lambda s, t: 0.6 * max(0.0, 1 - ((s - 48) / 46) ** 2 - ((t - 32) / 34) ** 2) * 1.5)
    _caixa_tex(e, 'contenidor', bx, bz, bw, bd, bh, ba, CORPG, 2.0, front=(tex['contenidor'], (0, 0, bw, bh)),
               cares={'dalt': {'ramp': HULL, 'lvl': lambda s, t, P: 2.2 if 4 < s < bw - 4 and 4 < t < bd - 4 else 3.6}})
    e.quad('contenidor', *[(bx + dx, bh + 0.5, bz + dz) for dx, dz in ((-8, 10), (8, 8), (8, -2), (-8, 0))],
           ramp=PAPER, lvl=4.0)                                         # un full que sobresurt per la boca
    # primer pla: el pilar d'acer de la dreta, la safata de cables i els cables que pengen del sostre
    e.caixa('primer_pla', 396, 436, 0, HW, -90, -56, FOSC, 1.6,
            cares={'esquerra': {'ramp': FOSC, 'lvl': lambda s, t, P: 2.4 - (1.0 if int(P[1]) % 50 < 3 else 0)},
                   'davant': {'ramp': FOSC, 'lvl': lambda s, t, P: 1.2 + (0.6 if s < 3 else 0)}})
    e.caixa('primer_pla', 250, 700, 190, 196, -40, -10, FOSC, 1.4,
            cares={'sota': {'ramp': FOSC, 'lvl': lambda s, t, P: 1.0 + (1.4 if int(P[0]) % 16 < 2 else 0)},
                   'davant': {'ramp': FOSC, 'lvl': 2.2}})
    e.cable('primer_pla', [(250, 190, -24), (200, 178, -24), (150, 186, -20), (90, 200, -16)], FOSC, 2.0, gruix=3.0)
    return e


# ─── Composició ─────────────────────────────────────────────────────────────

def _tex(t=0.0, estat=frozenset()):
    return {'paret': _paret(t, arrencat='cartell_arrencat' in estat), 'nua': _nua(), 'esq': _passadis_esq(), 'dre': _passadis_dre(), 'fons': _fons(t),
            'contenidor': _contenidor()}


class _Canvas(Canvas):
    S = 1                                          # (tres_d: píxels reals per píxel de sala)


def _render(estat=frozenset()):
    cv = _Canvas(light=LIGHT)
    e = escena(cv, _tex(estat=estat), estat)
    cv.rect(0, BOTTOM + 1, W - 1, H - 1, [(0, 0, 0)], 0, lit=0)    # la barra de verbs: negre
    return cv.img, e


@functools.lru_cache(maxsize=None)
def _base():
    return _render()


def bg(cv):
    cv.img.paste(_base()[0])
    cv.P = cv.img.load()


def _decorat(*estat):
    """Un decorat: la sala amb aquell estat, menys la de sempre (només el que canvia)."""
    def draw(cv):
        img, _ = _render(frozenset(estat))
        cv.img.alpha_composite(diff(img, _base()[0]))
        cv.P = cv.img.load()
    return draw


PROPS = {'rajola': _decorat('rajola'), 'cartell_arrencat': _decorat('cartell_arrencat')}


# ─── Animació de fons ───────────────────────────────────────────────────────
# El pilot vermell del fons polsa, un fluorescent del passadís parpelleja, la tira del cartell fa dues pampallugues,
# el LED de la càmera i el cursor de l'intèrfon: el dibuix pla de cada moment, projectat per les mateixes parets.

def _relleu(img, c0, ct):
    """On la capa del moment `ct` canvia respecte de la de l'inici `c0`, el fons escalat pel mateix factor (així
    es conserven les ombres i les clarors que l'escena hi ha posat al damunt)."""
    a0, at = np.asarray(c0, dtype=np.float32), np.asarray(ct, dtype=np.float32)
    m = (np.abs(at[..., :3] - a0[..., :3]).sum(-1) > 0) & (at[..., 3] > 0) & (a0[..., 3] > 0)
    if not m.any():
        return img
    out = np.asarray(img, dtype=np.float32).copy()
    k = at[..., :3] / np.maximum(a0[..., :3], 8.0)
    out[..., :3][m] = np.clip(out[..., :3][m] * k[m], 0, 255)
    return Image.fromarray(out.astype(np.uint8), 'RGBA')


def _ambient_frames(n=24):
    base, e = _base()
    parets = {'paret_esq', 'llinda', 'paret_fons_dreta'}
    p0, f0 = e.capa(_paret(0.0), parets), e.capa(_fons(0.0), {'passadis_fons'})
    tub = np.frombuffer(e.amo, dtype=np.uint16).reshape(e.cv.h, e.cv.w) == e.ids.index('tub_1')
    out = []
    for i in range(n):
        t = i / n
        img = _relleu(base, p0, e.capa(_paret(t), parets))
        img = _relleu(img, f0, e.capa(_fons(t), {'passadis_fons'}))
        if 0.40 <= t < 0.44:                                            # un tub del passadís parpelleja
            a = np.asarray(img).copy()
            a[..., :3][tub] //= 3
            img = Image.fromarray(a, 'RGBA')
        out.append(diff(img, base))
    return out


ANIMS = {'ambient': {'frames': _ambient_frames, 'frameDuration': 125}}


# ─── Capes del davant ───────────────────────────────────────────────────────

def _amo(ids):
    def mask(x, y):
        _, e = _base()
        return e.ids[e.amo[y * e.cv.w + x]] in ids
    return mask


def _p(x, z, y=0.0):
    u, v, _ = CAM.projecta((x, y, z))
    return round(u), round(v)


# El primer pla (sempre davant), el contenidor i la paret del fons a la dreta del passadís (qui hi entra, hi queda
# darrere).
FRONT = [
    {'id': 'davant', 'mask': _amo({'primer_pla'}), 'baseline': 999, 'zIndex': 20},
    {'id': 'davant_contenidor', 'mask': _amo({'contenidor'}), 'baseline': _p(BIN[0], BIN[1] - 6)[1], 'zIndex': 20},
    # (el cartell arrencat és en aquesta paret: el decorat va just a sobre de la capa, o la capa el taparia)
    {'id': 'davant_boca', 'mask': _amo({'paret_fons_dreta', 'trastos'}), 'baseline': _p(OX1, ZW + 4)[1],
     'zIndex': 20, 'props': ('cartell_arrencat',)},
]


# ─── Geometria (coordenades de sala, projectades) ────────────────────────────

def _rect_mon(*Ps):
    pts = [CAM.projecta(P) for P in Ps]
    return (max(0, round(min(p[0] for p in pts))), max(0, round(min(p[1] for p in pts))),
            min(W - 1, round(max(p[0] for p in pts))), min(BOTTOM, round(max(p[1] for p in pts))))


ZC = 470                                           # fins on es camina pel passadís (més enllà, massa petit)
# El terra on es camina (al món): el vestíbul, sense el contenidor ni els trastos, i el passadís fins a ZC.
def _z_a(x, v):
    """La z del terra que cau a la y de pantalla `v`, a la x del món `x`."""
    lo, hi = CAM.pos[2] + 20, 4000.0
    for _ in range(60):
        z = (lo + hi) / 2
        if CAM.projecta((x, 0, z))[1] > v:
            lo = z
        else:
            hi = z
    return (lo + hi) / 2


def _v_escala(k):
    """La y de pantalla on un personatge fa escala k."""
    lo, hi = 0.0, float(BOTTOM)
    for _ in range(50):
        v = (lo + hi) / 2
        if _escala_a(v) > k:
            hi = v
        else:
            lo = v
    return (lo + hi) / 2




def _escala_a(v):
    """L'escala d'un personatge amb els peus a la y de pantalla `v` (al terra, la profunditat només depèn de v)."""
    lo, hi = 1.0, 4000.0
    for _ in range(60):
        z = (lo + hi) / 2
        if CAM.projecta((200, 0, z))[1] > v:
            lo = z
        else:
            hi = z
    return CAM.escala((200, 0, (lo + hi) / 2))


_VP = min(_v_escala(1.2), BOTTOM - 4)               # el límit de prop: escala 1,2
# El terra on es camina (al món): el vestíbul (sense el contenidor ni els trastos) i el passadís fins a ZC; per
# davant, fins on el personatge fa 1,2.
WALK_MON = [(16, _z_a(16, _VP)), (16, ZC), (OX1 - 14, ZC), (OX1 - 12, 288), (OX1 + 10, 266), (OX1 + 60, 266),
            (OX1 + 66, 286), (520, 286), (520, _z_a(520, _VP))]
_WALK = [_p(x, z) for x, z in WALK_MON]
_V_FONS, _V_PROP = min(v for _, v in _WALK), max(v for _, v in _WALK)


def _forat_contenidor():
    bx, bz, bw, bd, _, ba = BIN
    c, s_ = math.cos(ba), math.sin(ba)
    return [_p(bx + lx * c - lz * s_, bz + lx * s_ + lz * c)
            for lx, lz in ((-bw / 2 - 8, -bd / 2 - 8), (bw / 2 + 8, -bd / 2 - 8), (bw / 2 + 8, bd / 2 + 6), (-bw / 2 - 8, bd / 2 + 6))]


GEOMETRIA = {
    'things': {
        'porta_cella': {'rect': _rect_mon((0, _y(61), _wz(10)), (0, 0, _wz(89))), 'walk': _p(34, _wz(50))},
        'cartell': {'rect': _rect_mon((_w(432), _y(50), ZW), (_w(568), _y(102), ZW)), 'walk': _p(_w(495), 250)},
        'camera_vigilancia': {'rect': _rect_mon((_w(545), _y(12), ZW), (_w(597), _y(48), ZW)), 'walk': _p(_w(560), 250)},
        'porta_hangar': {'rect': _rect_mon((OX0 + DOOR[0] - 4, _y(DOOR[2] - 22), ZF), (OX0 + DOOR[1] + 4, 0, ZF)),
                         'walk': _p(DOOR_X, ZC - 8)},
        'porta_memoria': {'rect': _rect_mon((_w(472), _y(101), ZW), (_w(539), 0, ZW)), 'walk': _p(_w(505), 274)},
        'rajola': {'rect': _rect_mon((TILE[0] - 2, 0, TILE[3] + 2), (TILE[1] + 10, 12, TILE[2] - 14)),
                   'walk': _p(TILE[1] + 30, TILE[2] - 10)},
    },
    'spawns': {'vet': _p(60, 130), 'guardia': _p(330, 240)},
    'walkable': _WALK,
    'forats': [_forat_contenidor()],
    'floorSquash': 0.42,                           # (la càmera, picada: el terra es veu aixafat)
    # L'ombra de contacte: la llum dominant és l'aplic de reixa (el punt del terra sota l'aplic); curta i cap avall.
    'characterShadow': {'enabled': True, 'color': '#06080e', 'alpha': 0.45, 'squash': 0.4, 'core': 0.6,
                        'light': {'x': _p(LAMP_C[0] + 30, LAMP_C[2])[0], 'y': _p(LAMP_C[0] + 30, LAMP_C[2])[1], 'stretch': 0.6,
                                  'reach': 170}},
    'regions': [{'id': 'perspectiva', 'active': True, 'scaleEnabled': True, 'scaleWalkSpeed': True,
                 'scaleTop': round(_escala_a(_V_FONS - 2), 3), 'scaleBottom': round(_escala_a(_V_PROP + 2), 3),
                 'points': [(0, _V_FONS - 2), (W - 1, _V_FONS - 2), (W - 1, _V_PROP + 2), (0, _V_PROP + 2)]}],
    # la llum de la sala sobre els personatges, en temps d'execució
    'characterLights': {
        'ambient': '#8a94aa',                                                           # acer fred
        'lights': [
            {'x': _p(LAMP_C[0], LAMP_C[2], LAMP_C[1])[0], 'y': _p(LAMP_C[0], LAMP_C[2], LAMP_C[1])[1], 'radius': 240,
             'color': '#d2e6ff', 'intensity': 0.8},                                     # l'aplic
            {'x': _p(STRIP_C[0], ZW - 10, STRIP_C[1])[0], 'y': _p(STRIP_C[0], ZW - 10, STRIP_C[1])[1], 'radius': 220,
             'color': '#dcebff', 'intensity': 0.7},                                     # la tira del cartell
            {'x': _p(DOOR_X, ZF - 20, 100)[0], 'y': _p(DOOR_X, ZF - 20, 100)[1], 'radius': 150,
             'color': '#ff4a3c', 'intensity': 0.9},                                     # el pilot vermell
        ],
    },
}
