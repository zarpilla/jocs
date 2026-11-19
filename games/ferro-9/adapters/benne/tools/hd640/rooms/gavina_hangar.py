"""
Moll de l'hangar de La Gavina (Acte 2, Vet). EN 3D (hd640/tres_d.py), a 1×.

El moll de càrrega de la fàbrica cent vint anys després, tapat de planxes d'acer. Una càmera alta, a la dreta, mira
de biaix la cantonada del fons a l'esquerra:
  - a la paret de l'esquerra, en escorç, la **porta del passadís** (C), el cartell del somriure i la boca de
    l'**escala** que baixa a l'arxiu (amb la reixa i la cadena);
  - a la cantonada, el **conducte** rovellat, que baixa del sostre i corre arran de terra cap a la comporta;
  - el **pilar 7** de la fàbrica, dret i separat de la paret (s'hi passa per darrere);
  - a la paret del fons, la **comporta** del moll, encallada i rovellada, amb la balisa taronja; oberta (decorat),
    la badia fonda amb la **llançadora** vella dins;
  - al terra, les planxes estriades, les quatre **reixes** de desguàs i la franja de perill davant la comporta;
  - la **caixa de recanvis**, girada (s'hi passa per darrere); primer pla: la biga de la dreta, una cadena amb el
    ganxo i unes caixes en silueta.

El detall de les parets ve del dibuix pla de sempre (gavina_hangar_pla_comu.py) sense el pilar, projectat; el pilar
i la llançadora són el dibuix pla dret (sprites); la resta, en 3D. Decorats: la diferència amb la sala de sempre.

El món: x a la dreta (0 = la paret de la porta), y amunt (0 = el terra), z cap al fons (300 = la paret del fons);
1 unitat = 1 píxel de sala a la distància on un personatge fa ≈110 px (escala 1).
"""
import functools
import math

import numpy as np
from PIL import Image

import hd640  # noqa: F401  (posa la llibreria de dibuix a 640×360)
from hd.pix import Canvas, Light, W, H, STEEL, PANEL, ORANGE, CYAN, WARN, RUST, IRON, PAPER, MANILA, WALNUT, SIL, SPACE  # noqa: F401
from hd.rooms.gavina_hangar import WATER, DUST
from hd640.rooms import gavina_hangar_pla_comu as PL
from hd640.rooms.fabrica_moll_pla_comu import pillar, carved_mark, shuttle, text, hr
from hd640.rooms.gavina_passadis_pla_comu import diff
from hd640.tres_d import Camera, Escena, Llum

BOTTOM = 259                                       # la sala acaba aquí (a sota, la barra de verbs)
ZW = 300                                           # la paret del fons
FLOOR_Y = PL.FLOOR_Y                               # el terra del dibuix pla
HW = FLOOR_Y                                       # l'alçada de les parets
XC = 100                                           # al dibuix pla, la cantonada (a l'esquerra, la paret de la porta)
XR = 900                                           # on s'acaba la paret del fons (fora de la pantalla)
CX0, CX1, CTOP = 290, 630, 40                      # la fulla de la comporta, al dibuix pla
BAY_Z = 540                                        # el fons de la badia
PILAR = (160, 200)                                  # el pilar 7 (x, z)
CAIXA = (440, 150, 56, 34, 30, -0.34)              # la caixa de recanvis: x, z, ample, fons, alt, gir
GRATES = [(26, 104, 104, 144), (110, 188, 140, 180), (270, 348, 196, 236), (330, 408, 70, 110)]   # x0, x1, z0, z1
SHUTTLE_Z = 410


def _w(fx):
    """Una x del dibuix pla de la paret del fons → la x del món."""
    return fx - XC


def _wz(fx):
    """Una x del dibuix pla de la paret de la porta → la z del món."""
    return ZW - XC + fx


def _y(fy):
    """Una y del dibuix pla (el terra, a 205) → l'alçada del món."""
    return HW - fy


CAM = Camera(pos=(320, 185, -260), yaw=-0.22, pitch=0.16, f=440, centre=(320, 100))

LIGHT = Light(ambient=0.0, vignette=None, floor_fade=None)  # (la llum és la del món: la de l'Escena)
LAMP_L = (_w(PL.LAMPS[0]), _y(46), ZW - 22)        # el fluorescent esquerre
LAMP_R = (_w(PL.LAMPS[1]), _y(46), ZW - 22)        # el fluorescent dret
BALISA = (_w(296), _y(27), ZW - 8)
LLUMS = [Llum(LAMP_L, 260, 1.7, power=1.4), Llum(LAMP_R, 300, 1.7, power=1.4), Llum(BALISA, 160, 0.8, power=1.5),
         Llum((8, _y(128), _wz(93)), 80, 0.6)]


class _Canvas(Canvas):
    S = 1                                          # (tres_d: píxels reals per píxel de sala)


# ─── Les textures: el dibuix pla de sempre ───────────────────────────────────

def _llum_pla():
    """La llum del dibuix pla, sense la vinyeta ni l'enfosquiment de baix (la llum és la de l'escena)."""
    l = Light(ambient=0.5, vignette=None, floor_fade=None)
    l.points = list(PL.LIGHT.points)
    return l


def _sense_pilar(cv, t):
    """El dibuix pla del moll... sense el pilar (que ara és dret, al mig de la sala): la paret de darrere."""
    x0, x1 = PL.PILAR_CX - 19, PL.PILAR_CX + 19
    PL.wall_panels(cv, x0, x1, 32, FLOOR_Y - 1)
    cv.darken(x0, 32, x1, 40, lambda x, y: (41 - y) / 8)
    cv.rect(x0, 28, x1, 31, STEEL, lambda x, y: 2.8 - (y - 28) * 0.6)
    cv.rect(x0, FLOOR_Y - 7, x1, FLOOR_Y - 1, STEEL, lambda x, y: 1.6 + (1.2 if y == FLOOR_Y - 7 else 0)
            - (0.6 if x % 53 == 0 else 0))
    LV = [1.6, 3.0, 3.8, 3.4, 3.0, 2.6, 2.2, 1.8, 1.4, 1.0, 0.6]
    for yy in range(187, 202):                                    # el conducte, arran de terra cap a la comporta
        lv = LV[min(10, round((yy - 187) / 14 * 10))]
        for xx in range(x0, x1 + 1):
            cv.put(xx, yy, RUST, lv + (hr(xx // 3, yy) - 0.5) * 0.5)
    cv.rect(260, 186, 263, 202, RUST, lambda a, b: 3.2 - (b - 186) * 0.12)       # una brida
    cv.tint(x0, 0, x1, FLOOR_Y, (40, 70, 110), 0.10)
    cv.tint(x0, 0, x1, 136, (255, 140, 60), lambda x, y: max(0, 0.16 * (1 - math.hypot(x - 296, y - 29) / 107)))


@functools.lru_cache(maxsize=None)
def _paret(t=0.0, aigua=False):
    """Les parets del moll, de cara: la porta, el cartell, l'escala, el conducte, la comporta, els fluorescents i la
    balisa (el pilar, no). `aigua`: l'escala plena d'aigua i el raig del conducte rebentat."""
    cv = Canvas(light=_llum_pla())
    PL.bg(cv, t)
    _sense_pilar(cv, t)
    if aigua:
        for y in range(141, FLOOR_Y):                             # l'escala, plena fins dalt
            for x in range(107, 178):
                cv.put(x, y, WATER, 1.4 + (y - 141) * 0.015 + (1.4 if y == 141 else 0) + (0.8 if (x + y * 3) % 14 == 0 else 0), 0)
        for x in range(W):                                        # la vora d'aigua a la paret
            if x % 3:
                cv.put(x, FLOOR_Y - 1, WATER, 5.0, 0)
    return cv.img


@functools.lru_cache(maxsize=None)
def _nua():
    """La paret d'acer nua, amb la biga i la safata: per als trossos on el dibuix pla no arriba."""
    cv = Canvas(light=Light(ambient=0.5, vignette=None, floor_fade=None))
    beam = [3.6, 3.2, 3.0, 2.2, 1.8, 1.8, 1.8, 1.6, 1.4, 1.0, 0.6]
    cv.rect(0, 0, W - 1, 16, PANEL, lambda x, y: 0.4 + (0.6 if x % 53 == 1 else 0), 0.4)
    cv.rect(0, 17, W - 1, 27, PANEL, lambda x, y: beam[y - 17] + (hr(x // 4, y, 2) - 0.5) * 0.4)
    cv.rect(0, 28, W - 1, 31, STEEL, lambda x, y: 2.8 - (y - 28) * 0.6)
    PL.wall_panels(cv, 0, W - 1, 32, FLOOR_Y - 1)
    cv.darken(0, 32, W - 1, 40, lambda x, y: (41 - y) / 8)
    cv.rect(0, FLOOR_Y - 7, W - 1, FLOOR_Y - 1, STEEL, lambda x, y: 1.6 + (1.2 if y == FLOOR_Y - 7 else 0)
            - (0.6 if x % 53 == 0 else 0))
    for x in range(W):                                            # rovell que surt per sota la pintura
        if hr(x // 5, 77) > 0.7:
            cv.put(x, 24 + (x % 2), RUST, 2.2)
    text(cv, 300, 120, 'MOLL L-2', WARN, 2.0, 0.6)
    # un armari elèctric amb el rètol de perill, un extintor i una mànega enrotllada (la paret de prop)
    cv.rect(380, 70, 440, 170, STEEL, lambda x, y: 2.4 - (x - 380) * 0.01 + (1.0 if x == 380 or y == 70 else 0)
            - (1.0 if x == 440 or y == 170 else 0))
    cv.vline(410, 72, 168, STEEL, 0.8)
    for hy in (110, 130):
        cv.rect(404, hy, 406, hy + 8, STEEL, 4.0)
        cv.rect(414, hy, 416, hy + 8, STEEL, 4.0)
    cv.poly([(395, 96), (410, 78), (425, 96)], WARN, 3.4, 0.4)
    cv.vline(410, 84, 91, STEEL, 0.4)
    cv.put(410, 93, STEEL, 0.4)
    cv.rect(500, 120, 512, 168, ORANGE, lambda x, y: 2.6 - (x - 500) * 0.1 + (0.8 if x == 500 else 0))
    cv.rect(502, 112, 509, 119, IRON, 2.6)
    cv.rect(502, 134, 510, 146, PAPER, 3.2, 0.3)
    cv.disc(580, 120, 22, 22, ORANGE, lambda nx, ny: 2.2 - nx * 0.6 - ny * 0.4 + (0.8 if int((nx * nx + ny * ny) * 9) % 2 else 0))
    cv.disc(580, 120, 7, 7, STEEL, 1.4)
    cv.rect(556, 90, 604, 96, STEEL, 2.6)
    cv.tint(0, 0, W - 1, H - 1, (40, 70, 110), 0.10)
    return cv.img


@functools.lru_cache(maxsize=None)
def _pilar(marca=False):
    """El pilar 7, de cara, sobre transparent (amb la marca de l'Iri, si hi és)."""
    cv = Canvas(light=_llum_pla(), transparent=True)
    pillar(cv, PL.PILAR_CX, 28, FLOOR_Y - 1, aged=True)
    for y in range(48, 55):                                       # l'abraçadora de la presó, amb els cables
        for x in range(PL.PILAR_CX - 12, PL.PILAR_CX + 13):
            cv.put(x, y, STEEL, 3.0 - (x - PL.PILAR_CX) * 0.11 + (1 if y == 48 else 0) - (1 if y == 54 else 0))
    if marca:
        carved_mark(cv, PL.PILAR_CX - 7, 107, aged=True)
    return cv.img


PILAR_BOX = (PL.PILAR_CX - 16, 28, PL.PILAR_CX + 17, FLOOR_Y)


@functools.lru_cache(maxsize=None)
def _llancadora(porta=False):
    """La llançadora vella, de perfil, sobre transparent (amb la porta oberta, si cal) i l'etiqueta dels forats."""
    cv = Canvas(light=_llum_pla(), transparent=True)
    shuttle(cv, 333, 133, aged=True)
    cv.rect(469, 157, 480, 164, PAPER, 3.6, 0.6)
    cv.hline(471, 478, 159, RUST, 1.4, 0.5)
    cv.hline(471, 476, 161, RUST, 1.4, 0.5)
    if porta:
        PL.p_porta_llancadora(cv)
    return cv.img


SHUTTLE_BOX = (330, 78, 514, 198)
SHUTTLE_FOOT = (422, 196)                          # (al dibuix pla: entre les dues potes, a terra)


@functools.lru_cache(maxsize=None)
def _badia_fons():
    """El fons de la badia (x del pla = x del món − 100): la porta exterior amb la finestreta a l'espai."""
    w = CX1 - CX0
    cv = Canvas(w, H, light=Light(ambient=0.3, vignette=None, floor_fade=None))
    for y in range(CTOP, FLOOR_Y):
        for x in range(w):
            cv.put(x, y, STEEL, 0.9 + (0.4 if x % 53 == 0 else 0) + (hr(x // 53, y // 44) - 0.5) * 0.3
                   + (0.3 if (y - CTOP) % 44 == 1 else 0), 0)
    dx0, dx1, dy0 = 150, 300, 70
    cv.rect(dx0, dy0, dx1, FLOOR_Y - 1, STEEL, lambda x, y: 1.6 + (0.8 if x == dx0 or y == dy0 else 0), 0)
    mid = (dx0 + dx1) // 2
    cv.vline(mid, dy0 + 2, FLOOR_Y - 1, STEEL, 0.4, 0)
    cv.vline(mid + 1, dy0 + 2, FLOOR_Y - 1, STEEL, 2.0, 0)
    wx0, wx1, wy0, wy1 = mid - 26, mid + 26, 86, 120
    cv.rect(wx0 - 2, wy0 - 2, wx1 + 2, wy1 + 2, SIL, 0.5, 0)
    for y in range(wy0, wy1 + 1):
        for x in range(wx0, wx1 + 1):
            cv.put(x, y, SPACE, 1.2 + (y - wy0) * 0.05, 0)
    for k in range(14):
        cv.flat(wx0 + 2 + int(hr(k, 1) * (wx1 - wx0 - 4)), wy0 + 2 + int(hr(k, 2) * (wy1 - wy0 - 4)),
                (220, 226, 255) if k % 3 else (160, 170, 220))
    for y in range(FLOOR_Y - 24, FLOOR_Y):
        for x in range(dx0 + 2, dx1 - 1):
            yel = ((x + y) // 7) % 2 == 0
            cv.put(x, y, WARN if yel else STEEL, (1.8 if yel else 0.4), 0)
    return cv.img


# ─── Les superfícies ────────────────────────────────────────────────────────

PLATE = 64


def _terra(s, t, P):
    """Planxes d'acer estriades, en coordenades del món: costures, estries en diagonal i alguna taca."""
    x, z = P[0], P[2]
    ui, vi = math.floor(x / PLATE), math.floor(z / 52)
    fu, fv = x - ui * PLATE, z - vi * 52
    v = 2.0 + (hr(ui, vi, 2) - 0.5) * 0.5
    a, b = int(x * 0.7 + z * 0.7), int(x * 0.7 - z * 0.7)
    if a % 7 == 0 or b % 7 == 0:
        v += 0.45                                                       # les estries
    if fu < 1.2 or fv < 1.2:
        return 0.6                                                      # la costura
    if fu < 2.4:
        v += 0.3
    if hr(int(x) // 9, int(z) // 7, 11) > 0.97:
        v -= 0.6                                                        # taques d'oli
    return v


def _reixa(s, t, P):
    """Una reixa de desguàs: barrots que fugen cap al fons, el marc i la foscor de sota."""
    if s < 3 or t < 3 or s > 75 or t > 37:
        return 3.6 - (1.0 if s < 1 or t < 1 else 0)
    if int(s) % 6 < 2:
        return 3.0 - (0.8 if int(s) % 6 == 1 else 0)
    return 0.1


def _franja(s, t, P):
    yel = int((P[0] - P[2]) // 10) % 2 == 0
    return (3.0 if yel else 0.5) - (0.8 if hr(int(P[0]) // 3, int(P[2]) // 2, 15) > 0.86 else 0)


FOSC = [(4, 5, 8), (8, 10, 14), (13, 15, 20), (19, 22, 28), (27, 30, 38), (37, 41, 50)]


def escena(cv, tex, estat=frozenset()):
    """Tot el moll, de lluny a prop. `estat`: els decorats que hi són ('oberta', 'porta', 'aigua', 'caixa',
    'marca', 'nota'). → l'Escena."""
    llums = LLUMS + ([Llum(((_w(CX0) + _w(CX1)) / 2, 120, 420), 260, 0.6)] if 'oberta' in estat else [])
    e = Escena(cv, CAM, llums, ambient=-0.2)
    zn = CAM.pos[2] + 60
    paret, nua = tex['paret'], tex['nua']
    bx0, bx1, by = _w(CX0), _w(CX1), _y(CTOP)
    # ── la badia (darrere la comporta oberta) ──
    if 'oberta' in estat:
        e.quad('badia', (bx0, by, BAY_Z), (bx1, by, BAY_Z), (bx1, 0, BAY_Z), (bx0, 0, BAY_Z),
               tex=(tex['badia'], (0, CTOP, CX1 - CX0, FLOOR_Y)))
        panells = lambda s, t, P: 0.9 + (0.5 if int(P[2]) % 53 < 2 else 0) + (hr(int(P[2]) // 53, int(t) // 44) - 0.5) * 0.3  # noqa: E731
        e.quad('badia', (bx0, by, ZW), (bx0, by, BAY_Z), (bx0, 0, BAY_Z), (bx0, 0, ZW), ramp=STEEL, lvl=panells)
        e.quad('badia', (bx1, by, BAY_Z), (bx1, by, ZW), (bx1, 0, ZW), (bx1, 0, BAY_Z), ramp=STEEL, lvl=panells)
        e.quad('badia', (bx0, by, BAY_Z), (bx1, by, BAY_Z), (bx1, by, ZW), (bx0, by, ZW), ramp=STEEL, lvl=0.6,
               dues_cares=True)
        e.quad('badia', (bx0, 0, BAY_Z), (bx1, 0, BAY_Z), (bx1, 0, ZW), (bx0, 0, ZW), ramp=STEEL,
               lvl=lambda s, t, P: _terra(s, t, P) - 0.5)
        e.claror((bx0, 0.4, BAY_Z), (bx1, 0.4, BAY_Z), (bx1, 0.4, ZW), (bx0, 0.4, ZW), (200, 230, 255),
                 lambda s, t: 0.14 * max(0.0, 1 - math.hypot((s - 170) / 160, (t - 120) / 140)))
        # el pòrtic de manteniment, la llançadora i la mànega del conducte
        for gx in (bx0 + 26, bx1 - 26):
            e.caixa('badia', gx - 3, gx + 3, 0, by - 8, BAY_Z - 70, BAY_Z - 64, STEEL, 2.4)
        e.caixa('badia', bx0 + 20, bx1 - 20, by - 14, by - 8, BAY_Z - 70, BAY_Z - 64, STEEL, 2.8)
        e.foscor('badia', (SHUTTLE_X - 110, 0.6, SHUTTLE_Z + 40), (SHUTTLE_X + 110, 0.6, SHUTTLE_Z + 40),
                 (SHUTTLE_X + 110, 0.6, SHUTTLE_Z - 40), (SHUTTLE_X - 110, 0.6, SHUTTLE_Z - 40),
                 lambda s, t: 0.6 * max(0.0, 1 - ((s - 110) / 110) ** 2 - ((t - 40) / 40) ** 2) * 1.4)
        lla = tex['llancadora_porta'] if 'porta' in estat else tex['llancadora']
        e.sprite('llancadora', lla.crop(SHUTTLE_BOX), (SHUTTLE_FOOT[0] - SHUTTLE_BOX[0], SHUTTLE_FOOT[1] - SHUTTLE_BOX[1]),
                 (SHUTTLE_X, 0, SHUTTLE_Z))
        e.cable('badia', [(bx0 + 4, 6, ZW - 6), (bx0 + 40, 1, ZW + 30), (SHUTTLE_X - 30, 1, SHUTTLE_Z - 30),
                          (SHUTTLE_X + 10, 30, SHUTTLE_Z - 4)], RUST, 2.6, gruix=3.0)
        for k in range(40):                                       # pols a l'aire, a la llum
            P = (bx0 + 20 + hr(k, 1) * (bx1 - bx0 - 40), 20 + hr(k, 2) * 120, ZW + 20 + hr(k, 3) * 200)
            u, v, _ = CAM.projecta(P)
            if 0 <= u < W and 0 <= v < BOTTOM and e.ids[e.amo[int(v) * W + int(u)]] == 'badia':
                cv.put(int(u), int(v), DUST, 3.0, 0)
        # la comporta plegada a dalt
        e.caixa('badia', bx0, bx1, by - 30, by, ZW + 1, ZW + 22, STEEL, 2.2,
                cares={'davant': {'ramp': RUST, 'lvl': lambda s, t, P: 2.0 + (1.0 if int(t) % 8 < 2 else 0)
                                  - (0.8 if hr(int(s) // 4, int(t) // 3, 2) > 0.7 else 0)},
                       'sota': {'ramp': WARN, 'lvl': lambda s, t, P: 3.0 if int(s + t) // 8 % 2 == 0 else 0.4}})
    # ── les parets ──
    e.quad('sostre', (0, HW, zn), (XR, HW, zn), (XR, HW, ZW), (0, HW, ZW), ramp=PANEL,
           lvl=lambda s, t, P: 0.6 + (0.6 if int(P[0]) % 53 < 2 else 0), dues_cares=True)
    zc = ZW - XC
    e.quad('paret_esq_prop', (0, HW, zn), (0, HW, zc), (0, 0, zc), (0, 0, zn), tex=(nua, (W - (zc - zn), 0, W, HW)))
    e.quad('paret_esq', (0, HW, zc), (0, HW, ZW), (0, 0, ZW), (0, 0, zc), tex=(paret, (0, 0, XC, HW)))
    e.quad('paret_fons', (0, HW, ZW), (bx0, HW, ZW), (bx0, 0, ZW), (0, 0, ZW), tex=(paret, (XC, 0, CX0, HW)))
    e.quad('llinda', (bx0, HW, ZW), (bx1, HW, ZW), (bx1, by, ZW), (bx0, by, ZW), tex=(paret, (CX0, 0, CX1, CTOP)))
    if 'oberta' not in estat:
        e.quad('comporta', (bx0, by, ZW), (bx1, by, ZW), (bx1, 0, ZW), (bx0, 0, ZW), tex=(paret, (CX0, CTOP, CX1, HW)))
    e.quad('paret_fons', (bx1, HW, ZW), (_w(W), HW, ZW), (_w(W), 0, ZW), (bx1, 0, ZW), tex=(paret, (CX1, 0, W, HW)))
    e.quad('paret_fons_lluny', (_w(W), HW, ZW), (XR, HW, ZW), (XR, 0, ZW), (_w(W), 0, ZW),
           tex=(nua, (0, 0, XR - _w(W), HW)))
    # ── el terra: planxes, la franja de perill davant la comporta i les reixes ──
    e.quad('terra', (0, 0, ZW), (XR, 0, ZW), (XR, 0, zn), (0, 0, zn), ramp=STEEL, lvl=_terra)
    e.quad('franja', (bx0 - 6, 0.2, ZW - 6), (bx1 + 6, 0.2, ZW - 6), (bx1 + 6, 0.2, ZW - 20), (bx0 - 6, 0.2, ZW - 20),
           ramp=WARN, lvl=_franja)
    for k, (gx0, gx1, gz0, gz1) in enumerate(GRATES):
        e.quad(f'reixa_{k}', (gx0, 0.3, gz1), (gx1, 0.3, gz1), (gx1, 0.3, gz0), (gx0, 0.3, gz0), ramp=STEEL,
               lvl=_reixa)
    # l'aigua (decorat): el moll inundat, amb ones i els reflexos dels fluorescents i de la balisa
    if 'aigua' in estat:
        e.claror((0, 1.0, ZW), (XR, 1.0, ZW), (XR, 1.0, zn), (0, 1.0, zn), (16, 46, 62),
                 lambda s, t: 0.62 + 0.08 * math.sin(s / 9.0 + t * 0.7))
        for lx, k in ((LAMP_L[0] + 40, 0.5), (LAMP_R[0], 0.5), (BALISA[0], 0.3)):
            e.claror((lx - 40, 1.2, ZW), (lx + 40, 1.2, ZW), (lx + 40, 1.2, zn), (lx - 40, 1.2, zn), (170, 220, 240),
                     lambda s, t, k=k: k * max(0.0, 1 - abs(s - 40) / 40) * (1 if int(t / 3 + s / 9) % 4 == 0 else 0)
                     * max(0.0, 1 - (ZW - t) / 260) if t > 0 else 0)
        e.claror((0, 1.2, ZW), (XR, 1.2, ZW), (XR, 1.2, zn), (0, 1.2, zn), (110, 170, 200),
                 lambda s, t: 0.35 if math.sin(s / 7.0 + t * 0.9) > 0.93 else 0.0)
    # la foscor dels racons
    e.foscor('racons', (0, 0.5, ZW), (XR, 0.5, ZW), (XR, 0.5, zn), (0, 0.5, zn),
             lambda s, t: 0.0 if bx0 < s < bx1 and 'oberta' in estat and t < 2
             else max(0.5 * max(0.0, 1 - t / 22), 0.5 * max(0.0, 1 - s / 22)))
    e.foscor('sostre_fosc', (0, HW - 0.5, ZW - 0.6), (XR, HW - 0.5, ZW - 0.6), (XR, 0, ZW - 0.6), (0, 0, ZW - 0.6),
             lambda s, t: 0.0 if 'oberta' in estat and bx0 < s < bx1 and t > HW - by else 0.35 * max(0.0, 1 - t / 40))
    # el bassal de llum dels fluorescents
    for (lx, _, lz), k in ((LAMP_L, 0.18), (LAMP_R, 0.2)):
        e.claror((lx - 150, 0.6, lz + 10), (lx + 150, 0.6, lz + 10), (lx + 150, 0.6, lz - 220), (lx - 150, 0.6, lz - 220),
                 (200, 230, 255), lambda s, t, k=k: k * max(0.0, 1 - math.hypot((s - 150) / 130, (t - 40) / 170)) ** 1.3)
    e.claror((BALISA[0] - 80, 0.6, ZW), (BALISA[0] + 80, 0.6, ZW), (BALISA[0] + 80, 0.6, ZW - 90),
             (BALISA[0] - 80, 0.6, ZW - 90), (255, 140, 60), lambda s, t: 0.12 * max(0.0, 1 - math.hypot((s - 80) / 80, t / 90)))
    # el raig del conducte rebentat (amb l'aigua)
    if 'aigua' in estat:
        px = _w(PL.PIPE_X + 7)
        for k in range(4):
            e.cable('raig', [(px - 2, 42 - k, ZW - 12), (px - 14 - k * 2, 30, ZW - 16), (px - 24 - k * 3, 2, ZW - 22)],
                    WATER, 6.4 - k * 0.6, gruix=1.4)
    # la caixa que sura (decorat): de fusta, «ARXIU -1», mig enfonsada davant l'escala
    if 'caixa' in estat:
        cz = ZW - 30
        e.caixa_girada('caixa_flotant', _w(135), cz, 44, 30, 15, 0.25, WALNUT, 2.2, y0=0.5,
                       cares={'davant': {'tex': (tex['caixa'], (0, 8, 45, 23))},
                              'dalt': {'ramp': WALNUT, 'lvl': lambda s, t, P: 3.4 - (0.6 if int(s) % 8 == 7 else 0)}})
        e.claror((_w(105), 1.4, cz + 30), (_w(165), 1.4, cz + 30), (_w(165), 1.4, cz - 30), (_w(105), 1.4, cz - 30), (150, 210, 230),
                 lambda s, t: 0.5 if 0.85 < math.hypot((s - 30) / 26, (t - 30) / 22) < 1.0 else 0.0)
    # ── el pilar 7, dret i separat de la paret, amb la seva ombra ──
    px_, pz_ = PILAR
    e.foscor('ombra_pilar', (px_ - 30, 0.7, pz_ + 50), (px_ + 30, 0.7, pz_ + 50), (px_ + 30, 0.7, pz_ - 20),
             (px_ - 30, 0.7, pz_ - 20), lambda s, t: 0.6 * max(0.0, 1 - ((s - 30) / 20) ** 2 - ((t - 22) / 40) ** 2) * 1.5)
    pil = tex['pilar_marca'] if 'marca' in estat else tex['pilar']
    e.sprite('pilar', pil.crop(PILAR_BOX), (PL.PILAR_CX - PILAR_BOX[0], FLOOR_Y - PILAR_BOX[1] - 1), (px_, 0, pz_))
    # ── la caixa de recanvis, girada, amb la nota (decorat) ──
    cx_, cz_, cw, cd, ch, ca = CAIXA
    e.foscor('ombra_caixa', (cx_ - 46, 0.6, cz_ + 34), (cx_ + 46, 0.6, cz_ + 34), (cx_ + 46, 0.6, cz_ - 30),
             (cx_ - 46, 0.6, cz_ - 30), lambda s, t: 0.6 * max(0.0, 1 - ((s - 44) / 42) ** 2 - ((t - 32) / 30) ** 2) * 1.5)
    e.caixa_girada('caixa_recanvis', cx_, cz_, cw, cd, ch, ca, WALNUT, 2.2,
                   cares={'davant': {'tex': (tex['recanvis'], (0, 0, cw, ch))},
                          'dalt': {'ramp': WALNUT, 'lvl': lambda s, t, P: 3.4 - (0.8 if int(s) % 9 == 8 else 0)},
                          'esquerra': {'ramp': WALNUT, 'lvl': lambda s, t, P: 1.6 - (0.6 if int(t) % 8 == 7 else 0)},
                          'dreta': {'ramp': WALNUT, 'lvl': 1.3}})
    if 'nota' in estat:
        c, s_ = math.cos(ca), math.sin(ca)

        def Pc(lx, y, lz):
            return (cx_ + lx * c - lz * s_, y, cz_ + lx * s_ + lz * c)
        e.quad('caixa_recanvis', Pc(8, ch + 0.4, -cd / 2 + 10), Pc(20, ch + 0.4, -cd / 2 + 10), Pc(20, ch + 0.4, -cd / 2 - 4),
               Pc(8, ch + 0.4, -cd / 2 - 4), ramp=PAPER, lvl=lambda s, t, P: 4.4 - (1.6 if abs(t - 7) < 0.7 else 0))
    for k, (sx, sz) in enumerate(((cx_ - 40, cz_ - 26), (cx_ - 30, cz_ - 34))):
        e.caixa('cargols', sx - 2, sx + 2, 0, 2, sz - 2, sz + 2, STEEL, 3.6 - k)
    # ── primer pla: la biga de la dreta, la cadena amb el ganxo i caixes en silueta ──
    e.caixa('primer_pla', 396, 436, 0, HW, -90, -56, FOSC, 1.6,
            cares={'esquerra': {'ramp': FOSC, 'lvl': lambda s, t, P: 2.4 - (1.0 if int(P[1]) % 50 < 3 else 0)},
                   'davant': {'ramp': FOSC, 'lvl': lambda s, t, P: 1.2 + (0.6 if s < 3 else 0)}})
    e.caixa('primer_pla', 150, 700, 190, 198, -60, -36, FOSC, 1.4,
            cares={'sota': {'ramp': FOSC, 'lvl': 1.2}, 'davant': {'ramp': FOSC, 'lvl': 2.0}})
    for k in range(12):                                            # la cadena, baula a baula, i el ganxo
        y = 190 - k * 6
        e.caixa('primer_pla', 386 - (k % 2), 388 + (k % 2), y - 5, y, -46 + (k % 2), -44 - (k % 2), FOSC, 2.2 + (k % 2) * 0.6)
    e.cable('primer_pla', [(387, 118, -45), (382, 108, -45), (386, 102, -45), (394, 106, -45), (392, 114, -45)], FOSC, 2.4,
            gruix=3.2)
    for cx, cz, w, d, h, a, y0 in ((10, -30, 60, 44, 40, 0.25, 0), (2, -26, 44, 34, 24, 0.1, 40)):
        e.caixa_girada('primer_pla', cx, cz, w, d, h, a, FOSC, 1.6, y0=y0,
                       cares={'dalt': {'ramp': FOSC, 'lvl': 2.8}, 'davant': {'ramp': FOSC, 'lvl': 1.2},
                              'dreta': {'ramp': FOSC, 'lvl': 2.0}})
    return e


SHUTTLE_X = (_w(CX0) + _w(CX1)) / 2 + 10


@functools.lru_cache(maxsize=None)
def _caixa_flotant_tex():
    cv = Canvas(60, 30, light=Light(ambient=0.3, vignette=None, floor_fade=None))
    for y in range(23):
        for x in range(45):
            lvl = 2.6 + (hr(x // 5, 3) - 0.5) * 0.4 - (0.6 if y % 8 == 7 else 0)
            cv.put(x, y, WALNUT, lvl)
    cv.rect(5, 6, 40, 14, MANILA, 2.8)
    xe = text(cv, 7, 7, 'ARXIU', [(40, 30, 24), (60, 44, 30)], 0.4, 0)
    text(cv, xe + 3, 7, '-1', [(140, 30, 30)], 0, 0)
    return cv.img


@functools.lru_cache(maxsize=None)
def _recanvis_tex():
    cw, ch = CAIXA[2], CAIXA[4]
    cv = Canvas(80, 40, light=Light(ambient=0.3, vignette=None, floor_fade=None))
    for y in range(ch):
        for x in range(cw):
            lvl = 2.6 + (hr(x // 7, 9) - 0.5) * 0.4 - (0.6 if y % 8 == 7 else 0) + (0.2 if y % 8 == 0 else 0)
            if y < 4:
                lvl = 3.6 - y * 0.2
            if x in (0, cw - 1):
                lvl = 1.4 if x == cw - 1 else 3.4
            cv.put(x, y, WALNUT, lvl)
    cv.hline(0, cw - 1, 4, WALNUT, 0.8)
    cv.rect(8, 9, 44, 18, MANILA, 2.4)
    text(cv, 10, 10, 'RECAN', [(40, 30, 24), (60, 44, 30)], 0.4, 0)
    for x, y in ((3, 20), (44, 8), (28, 24), (6, 9)):
        cv.put(x, y, RUST, 3.0)
    return cv.img


# ─── Composició ─────────────────────────────────────────────────────────────

def _tex(t=0.0, aigua=False):
    return {'paret': _paret(t, aigua), 'nua': _nua(), 'pilar': _pilar(), 'pilar_marca': _pilar(True),
            'llancadora': _llancadora(), 'llancadora_porta': _llancadora(True), 'badia': _badia_fons(),
            'caixa': _caixa_flotant_tex(), 'recanvis': _recanvis_tex()}


def _render(estat=frozenset()):
    cv = _Canvas(light=LIGHT)
    e = escena(cv, _tex(aigua='aigua' in estat), estat)
    cv.rect(0, BOTTOM + 1, W - 1, H - 1, [(0, 0, 0)], 0, lit=0)    # la barra de verbs: negre
    return cv.img, e


@functools.lru_cache(maxsize=None)
def _estat(*estat):
    return _render(frozenset(estat))


def _base():
    return _estat()


def bg(cv):
    cv.img.paste(_base()[0])
    cv.P = cv.img.load()


def _decorat(estat, sobre=()):
    """Un decorat: la sala amb `estat` (i el que ja hi ha a sota, `sobre`), menys la sala amb `sobre`."""
    def draw(cv):
        img, _ = _estat(*sorted(set(estat) | set(sobre)))
        cv.img.alpha_composite(diff(img, _estat(*sorted(sobre))[0]))
        cv.P = cv.img.load()
    return draw


PROPS = {
    'llancadora': _decorat(('oberta',)),
    'porta_llancadora': _decorat(('porta',), ('oberta',)),
    'aigua': _decorat(('aigua',)),
    'caixa_flotant': _decorat(('caixa',), ('aigua',)),
    'marca_pilar': _decorat(('marca',)),
    'caixa_recanvis': _decorat(('nota',)),
}


# ─── Animació de fons: la balisa gira, el fluorescent esquerre fa figa i regalima el conducte ─────

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
    parets = {'paret_esq', 'paret_fons', 'llinda', 'comporta'}
    c0 = e.capa(_paret(0.0), parets)
    out = []
    for i in range(n):
        out.append(diff(_relleu(base, c0, e.capa(_paret(i / n), parets)), base))
    return out


ANIMS = {'ambient': {'frames': _ambient_frames, 'frameDuration': 120}}


# ─── Capes del davant ───────────────────────────────────────────────────────

def _amo(ids):
    def mask(x, y):
        _, e = _base()
        return e.ids[e.amo[y * e.cv.w + x]] in ids
    return mask


def _p(x, z, y=0.0):
    u, v, _ = CAM.projecta((x, y, z))
    return round(u), round(v)


# El primer pla (sempre davant), el pilar 7 i la caixa de recanvis (qui hi passa per darrere, hi queda darrere).
FRONT = [
    {'id': 'davant', 'mask': _amo({'primer_pla'}), 'baseline': 999, 'zIndex': 20},
    {'id': 'davant_pilar', 'mask': _amo({'pilar'}), 'baseline': _p(PILAR[0], PILAR[1] - 6)[1], 'zIndex': 20,
     'props': ('marca_pilar',)},
    {'id': 'davant_caixa', 'mask': _amo({'caixa_recanvis'}), 'baseline': _p(CAIXA[0], CAIXA[1] - 8)[1], 'zIndex': 20,
     'props': ('caixa_recanvis',)},
]


# ─── Geometria (coordenades de sala, projectades) ────────────────────────────

def _rect_mon(*Ps):
    pts = [CAM.projecta(P) for P in Ps]
    return (max(0, round(min(p[0] for p in pts))), max(0, round(min(p[1] for p in pts))),
            min(W - 1, round(max(p[0] for p in pts))), min(BOTTOM, round(max(p[1] for p in pts))))


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


_VP = min(_v_escala(1.2), BOTTOM - 4)               # el límit de prop: escala 1,2
# El terra on es camina (al món): fins a la franja de la comporta; per davant, fins on el personatge fa 1,2.
WALK_MON = [(16, _z_a(16, _VP)), (16, 284), (520, 284), (520, _z_a(520, _VP))]
_WALK = [_p(x, z) for x, z in WALK_MON]
_V_FONS, _V_PROP = min(v for _, v in _WALK), max(v for _, v in _WALK)


def _forat(cx, cz, w, d, ang, m=8):
    c, s_ = math.cos(ang), math.sin(ang)
    return [_p(cx + lx * c - lz * s_, cz + lx * s_ + lz * c)
            for lx, lz in ((-w / 2 - m, -d / 2 - m), (w / 2 + m, -d / 2 - m), (w / 2 + m, d / 2 + m - 2), (-w / 2 - m, d / 2 + m - 2))]


def _sprite_rect(peu, peu_img, box, fbox):
    """El rectangle de pantalla d'un tros (`fbox`, al dibuix pla) d'un sprite dret (retall `box`, peu `peu_img`)."""
    k = CAM.escala(peu)
    u, v, _ = CAM.projecta(peu)
    ox, oy = u - peu_img[0] * k, v - peu_img[1] * k
    return (round(ox + (fbox[0] - box[0]) * k), round(oy + (fbox[1] - box[1]) * k),
            round(ox + (fbox[2] - box[0]) * k), round(oy + (fbox[3] - box[1]) * k))


_SH = ((SHUTTLE_X, 0, SHUTTLE_Z), (SHUTTLE_FOOT[0] - SHUTTLE_BOX[0], SHUTTLE_FOOT[1] - SHUTTLE_BOX[1]), SHUTTLE_BOX)
_PL = (PILAR[0], 0, PILAR[1])


def _grate_rect(k):
    gx0, gx1, gz0, gz1 = GRATES[k]
    return _rect_mon((gx0, 0, gz1), (gx1, 0, gz1), (gx1, 0, gz0), (gx0, 0, gz0))


GEOMETRIA = {
    'things': {
        'porta_passadis': {'rect': _rect_mon((0, _y(59), _wz(9)), (0, 0, _wz(88))), 'walk': _p(32, _wz(48))},
        'comporta': {'rect': _rect_mon((_w(CX0) - 6, _y(CTOP - 6), ZW), (_w(CX1) + 6, 0, ZW)),
                     'walk': _p((_w(CX0) + _w(CX1)) / 2, 262)},
        'pilar': {'rect': _sprite_rect(_PL, (PL.PILAR_CX - PILAR_BOX[0], FLOOR_Y - PILAR_BOX[1] - 1), PILAR_BOX,
                                       (PL.PILAR_CX - 13, 28, PL.PILAR_CX + 13, FLOOR_Y)),
                  'walk': _p(PILAR[0] + 40, PILAR[1] - 40)},
        'placa_terra': {'rect': _grate_rect(1), 'walk': _p((GRATES[1][0] + GRATES[1][1]) / 2, GRATES[1][2] - 16)},
        'llancadora': {'rect': _sprite_rect(*_SH, (333, 80, 511, 197)), 'walk': _p(SHUTTLE_X - 40, 270)},
        'pany': {'rect': _sprite_rect(*_SH, (405, 116, 435, 150)), 'walk': _p(SHUTTLE_X - 10, 270)},
        'conducte': {'rect': _rect_mon((_w(PL.PIPE_X) - 2, _y(30), ZW), (_w(PL.PIPE_X + PL.PIPE_W) + 4, 0, ZW)),
                     'walk': _p(40, 262)},
        'escala': {'rect': _rect_mon((_w(101), _y(134), ZW), (_w(183), 0, ZW)), 'walk': _p(_w(142), 266)},
        'caixa_flotant': {'rect': _rect_mon(*[(_w(135) + dx, y, ZW - 30 + dz) for dx in (-26, 26) for dz in (-20, 20)
                                              for y in (0, 18)]), 'walk': _p(_w(135) + 10, ZW - 64)},
        'sortida_conducte': {'rect': _grate_rect(0), 'walk': _p((GRATES[0][0] + GRATES[0][1]) / 2 + 20, GRATES[0][2] - 14)},
        'caixa_recanvis': {'rect': _rect_mon(*[(CAIXA[0] + dx, y, CAIXA[1] + dz) for dx in (-32, 32) for dz in (-24, 24)
                                               for y in (0, CAIXA[4] + 4)]),
                           'walk': _p(CAIXA[0] - 40, CAIXA[1] - 40)},
    },
    'spawns': {'vet': _p(90, 160)},
    'walkable': _WALK,
    'forats': [_forat(CAIXA[0], CAIXA[1], CAIXA[2], CAIXA[3], CAIXA[5]), _forat(PILAR[0], PILAR[1], 26, 26, 0.0, m=4)],
    'floorSquash': 0.42,
    # L'ombra de contacte: la llum dominant és el fluorescent dret, sobre el mig del moll.
    'characterShadow': {'enabled': True, 'color': '#06080e', 'alpha': 0.45, 'squash': 0.4, 'core': 0.6,
                        'light': {'x': _p(LAMP_R[0], LAMP_R[2] - 40)[0], 'y': _p(LAMP_R[0], LAMP_R[2] - 40)[1],
                                  'stretch': 0.6, 'reach': 180}},
    'regions': [{'id': 'perspectiva', 'active': True, 'scaleEnabled': True, 'scaleWalkSpeed': True,
                 'scaleTop': round(_escala_a(_V_FONS - 2), 3), 'scaleBottom': round(_escala_a(_V_PROP + 2), 3),
                 'points': [(0, _V_FONS - 2), (W - 1, _V_FONS - 2), (W - 1, _V_PROP + 2), (0, _V_PROP + 2)]}],
    'characterLights': {
        'ambient': '#8a96ac',                                                           # acer fred
        'lights': [
            {'x': _p(LAMP_L[0], LAMP_L[2], LAMP_L[1])[0], 'y': _p(LAMP_L[0], LAMP_L[2], LAMP_L[1])[1], 'radius': 240,
             'color': '#d2ecff', 'intensity': 0.8},                                     # el fluorescent esquerre
            {'x': _p(LAMP_R[0], LAMP_R[2], LAMP_R[1])[0], 'y': _p(LAMP_R[0], LAMP_R[2], LAMP_R[1])[1], 'radius': 260,
             'color': '#d2ecff', 'intensity': 0.8},                                     # el fluorescent dret
            {'x': _p(BALISA[0], BALISA[2], BALISA[1])[0], 'y': _p(BALISA[0], BALISA[2], BALISA[1])[1], 'radius': 150,
             'color': '#ff9640', 'intensity': 0.6},                                     # la balisa
        ],
    },
}
