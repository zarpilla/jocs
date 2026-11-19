"""
Final «Correspondència», l'última imatge, EN PLA DE CINEMA (hd640/tres_d.py, a 1×): la cambra de ressonància vella,
al present, vista de baix i de biaix, com un monument. El Cargol l'ha reparada durant cent vint anys (cargols nous, una
bobina tornada a enrotllar, el formulari 27-B enganxat al muntant i les ratlles dels dies a les parets), i torna a
brillar amb la llum de fase. A dins, damunt la base, una nota plegada en tenda: «Hola, V.».

- **Contrapicat i 3/4:** la càmera és baixa, davant a l'esquerra: de la cambra se'n veuen el davant (el vidre amb
  les tres bobines en fila, que s'empetiteixen), el costat de ferro rovellat i la caixa de dalt per sota; la caixa
  surt de quadre per dalt, gran.
- **Contrast d'escala:** la màquina enorme, i al peu, petita i encesa, la nota (el punt d'interès, a sota del quadre
  de text).
- **Primer pla fosc:** a baix a l'esquerra, la caixa d'eines del Cargol, amb una clau anglesa i una bobina de fil de
  coure, en silueta; cables que pengen de la caixa de dalt cap a la paret.
- **Línies que guien l'ull:** la base amb les franges de perill i les juntes del terra fugen cap a la nota; les dues
  parets de maó amb les ratlles fan la cantonada al fons, a la dreta.
- **Llum:** el camp violeta de dins (gairebé l'única) pinta les parets i el terra, i la nota fa una llum blanca i
  càlida; vinyeta forta, un pla íntim.

Tot el detall ve del dibuix pla de sempre (final_nota_pla_comu.py): els muntants, la caixa de dalt, la base, les
bobines i el camp hi són textures o figures dretes. L'animació (`ambient`) reprojecta el camp que crepita, les
partícules que pugen, les guspires i la nota que fa llum polsant.

El món: x a la dreta (0 = el mig de la cambra), y amunt (0 = el terra), z endavant (0 = el vidre); 1 unitat = 1 píxel
del dibuix pla (la cambra fa 318 d'alt, un personatge ≈110).
"""
import math
from functools import lru_cache

import hd640  # noqa: F401  (posa la llibreria de dibuix a 640×360)
import numpy as np
from PIL import Image

from hd.pix import Canvas, Light, W, H, mix, GOLD, COPPER, IRON, STEEL, WALNUT
from hd640.rooms import final_nota_pla_comu as PL
from hd640.rooms.final_nota_pla_comu import (FE9, FIELD, hr, frame_diff, PAPERW, HAND, INK, GX0, GX1, GY0, GY1, COILS,
                                             vnoise)
from hd640.tres_d import Camera, Escena, Llum

LIGHT = Light(ambient=0.0, vignette=None, floor_fade=None)       # (la llum és la del món: la de l'Escena)

CAM = Camera(pos=(-215, 70, -255), yaw=0.62, pitch=-0.13, f=360, centre=(320, 200))

FX = 320                         # la x del dibuix pla que cau a x = 0
FY = 318                         # la y del dibuix pla que cau a y = 0 (el peu de la base)
Z_BOB = 62                       # el pla de les bobines
Z_FONS = 118                     # el fons de la cambra (el camp)
ZB, XR = 300, 430                # la paret del fons i la de la dreta
NOTA = (6.0, 33.0, 14.0)         # la nota: centre de la base de la tenda
NOTA_ANG = -0.30                 # girada (el cantó de la dreta, enrere)
NOTA_W, NOTA_H, NOTA_D = 58, 27, 13
VIOLET = (130, 90, 220)

LLUMS = [Llum((0, 160, Z_BOB), 700, 2.4, power=1.3),               # el camp
         Llum((NOTA[0], 52, NOTA[2] - 10), 170, 1.6, power=1.6)]    # la nota


def _x(fx):
    return fx - FX


def _y(fy):
    return FY - fy


# ─── Les textures planes ────────────────────────────────────────────────────

@lru_cache(maxsize=None)
def _cambra_plana():
    """La cambra de sempre, de cara (el dibuix pla): d'aquí surten els muntants, la caixa de dalt i la base."""
    cv = Canvas(light=PL.LIGHT)
    PL.chamber(cv, 0.0)
    return cv.img


def _camp(t=0.0):
    """El camp de dins (només el camp, sense bobines): els dos fils que crepiten i els arcs."""
    TAU = 2 * math.pi
    cv = Canvas(light=PL.LIGHT)
    CX, CY = PL.CX, PL.CY
    for y in range(GY0, GY1 + 1):
        for x in range(GX0, GX1 + 1):
            d = math.hypot((x - CX) / 1.2, (y - CY) * 0.75) / 147
            lvl = 4.6 - d * 3.6
            for j, gx in enumerate(((COILS[0] + COILS[1]) / 2, (COILS[1] + COILS[2]) / 2)):
                sg = 1 if j == 0 else -1
                w = (gx + math.sin(y / 9.33 + gx + sg * TAU * t) * 5.33
                     + math.sin(y / 3.07 + gx * 2 - sg * TAU * 3 * t) * 1.33)
                if abs(x - w) < 1.3 and GY0 + 19 < y < GY1 - 24:
                    lvl += 2.4 + 0.9 * max(0.0, math.sin(y / 14.7 - sg * TAU * 2 * t + j)) ** 3
                elif abs(x - w) < 6.7:
                    lvl += 0.8 * (1 - abs(x - w) / 6.7)
            lvl += 0.4 * (math.sin(x / 12.0 + y / 17.3 + TAU * t) * math.sin(y / 9.33 - x / 22.7 - TAU * 2 * t))
            cv.put(x, y, FIELD, lvl, 0)
    for gx in ((COILS[0] + COILS[1]) / 2, (COILS[1] + COILS[2]) / 2):
        cv.glow(gx, 160, 45, (200, 170, 255), 0.5 + 0.1 * math.sin(TAU * (2 * t + gx / 53)))
    cv.glow(CX, CY, 160, (150, 110, 240), 0.35)
    return cv.img


@lru_cache(maxsize=None)
def _camp0():
    return _camp(0.0)


@lru_cache(maxsize=None)
def _bobines():
    """Les tres bobines de sempre, dibuixades soles sobre transparent (la de la dreta, la nova del Cargol)."""
    cv = Canvas(light=PL.LIGHT, transparent=True)
    for k, cx in enumerate(COILS):
        new = k == 2
        for y in range(64, 259):
            for x in range(cx - 17, cx + 19):
                s = (x - cx) / 18
                band = (y - 64) % 28
                if band in (24, 25, 26, 27):
                    if abs(s) < 0.6:
                        cv.put(x, y, FE9, 5.4 - s * 2.6 - (1.4 if band == 27 else 0), 0.3)
                    continue
                if abs(s) > 0.88 and s < 0 and band not in (0, 23):
                    cv.put(x, y, FIELD, 5.6, 0)                          # la vora encesa pel camp (el del mig)
                    continue
                lv = 3.4 - s * 1.6 - s * s * 1.6 + (y % 2) * 0.5 - (1.0 if band in (0, 23) else 0)
                if not new:
                    lv -= 0.4
                    if hr(x // 3, y // 4, k) > 0.9:
                        lv -= 1.2
                    elif hr(x // 2, y // 3, k + 7) > 0.96:
                        cv.put(x, y, COPPER, 1.6, 0.4)
                        continue
                else:
                    lv += 0.4
                cv.put(x, y, COPPER, lv, 0.4)
        for yy in (61, 259):
            cv.rect(cx - 20, yy, cx + 20, yy + 3, FE9, lambda x, y: 5.6 - (x - cx) / 8.0 - (y - yy) * 0.45, 0.3)
        cv.rect(cx - 3, 45, cx + 1, 60, FE9, lambda x, y: 5.4 - (x - cx) * 0.5, 0.3)
        if new:
            for i in range(13):
                cv.put(cx + 17 + (i % 2), 67 + i * 4, COPPER, 6.0, 0)
                cv.put(cx + 18 - (i % 2), 69 + i * 4, COPPER, 4.6, 0)
            for y in (147, 148, 149):
                cv.hline(cx - 17, cx + 17, y, IRON, 4.6 - (y - 147) * 1.4, 0.4)
            cv.put(cx + 18, 150, IRON, 4.0, 0.4)
            cv.put(cx + 19, 151, IRON, 3.0, 0.4)
    return cv.img


@lru_cache(maxsize=None)
def _paret():
    """El maó de les parets amb les ratlles dels dies (640 × 317), sense la llum de la cambra (aquí és la del món)."""
    lt = Light(ambient=0.3, vignette=None, floor_fade=None)
    cv = Canvas(light=lt)
    PL.walls(cv)
    for (x0, y0, rows, per, seed) in ((20, 120, 13, 7, 2), (150, 150, 11, 6, 3), (300, 112, 14, 8, 1),
                                      (470, 140, 12, 7, 4)):
        PL.tallies(cv, x0, y0, rows, per, seed=seed)
    return cv.img.crop((0, 0, 640, 317))


@lru_cache(maxsize=None)
def _nota_plana():
    """La cara de davant de la nota, de cara (58 × 27): paper, «Hola, V.» a mà, unes ratlles i «-I.»."""
    cv = Canvas(NOTA_W, NOTA_H, light=Light(ambient=0.0))
    for y in range(NOTA_H):
        for x in range(NOTA_W):
            lvl = 5.4 - y / 30 + (hr(x // 2, y // 3, 17) - 0.5) * 0.25
            if y == 0:
                lvl = 6.6                                                # el plec, encès
            cv.put(x, y, PAPERW, lvl, 0)

    def write(s_, x0, y0):
        x = x0
        for ch in s_:
            g = HAND[ch]
            for j, row in enumerate(g):
                for i, c in enumerate(row):
                    if c == '#':
                        cv.flat(x + i, y0 + j, INK)
            x += len(g[0]) + 1
    write('Hola, V.', 6, 3)
    for k, ln in enumerate((38, 26)):
        for i in range(ln):
            if hr(i, k, 21) > 0.25:
                cv.flat(6 + i, 13 + k * 5 + (1 if hr(i, k, 22) > 0.8 else 0), mix(INK, (200, 190, 200), 0.45))
    write('-I.', 42, 18)
    return cv.img


# ─── L'escena ───────────────────────────────────────────────────────────────

def _terra(s, t, P):
    x, z = P[0], P[2]
    lvl = 1.5 + (0.6 if (x + 1000) % 32 < 1.2 else 0) + (hr(int(x) // 32, int(z) // 96, 3) - 0.5) * 0.3
    if (z + 1000) % 96 < 1.2:
        lvl -= 0.6
    lvl += (hr(int(x) // 3, int(z) // 3, 5) - 0.5) * 0.25
    return lvl


def _ferro(base, seed):
    """Ferro rovellat en clapes (les cares procedurals: costats i tapes)."""
    def fn(s, t, P):
        rr = vnoise(s, t, 12, seed) * 0.75 + vnoise(s, t, 4, seed + 1) * 0.25
        return base + (rr - 0.5) * 0.8 - (0.9 if rr > 0.68 else 0)
    return fn


def _planxa(base, seed):
    """Les planxes de ferro dels costats: juntes, reblons, clapes de rovell i regalims."""
    def fn(s, t, P):
        lvl = _ferro(base, seed)(s, t, P)
        u, v = s % 62, t % 70
        if u < 1.5 or v < 1.5:
            return lvl - 1.2
        if u < 3:
            return lvl + 0.6
        if (abs(u - 6) < 1.2 or abs(v - 6) < 1.2) and (int(s) + int(t)) % 11 < 2:
            return lvl + 1.8                                         # un rebló
        if hr(int(s) // 3, 0, seed) > 0.85 and hr(int(s) // 3, int(t) // 9, seed + 2) > 0.3:
            return lvl - 0.6                                         # regalims
        return lvl
    return fn


def _rot(cx, cz, ang, lx, y, lz):
    c, s_ = math.cos(ang), math.sin(ang)
    return (cx + lx * c - lz * s_, y, cz + lx * s_ + lz * c)


def escena(cv):
    cv.S = 1                                                         # (el Canvas d'1× de Ferro-9 no ho diu)
    e = Escena(cv, CAM, LLUMS, ambient=-0.2)
    plana = _cambra_plana()
    paret = _paret()
    # les parets: la del fons i la de la dreta (la cantonada, al fons a la dreta), amb les ratlles dels dies
    for x in range(-900, XR, 640):                                    # (la textura, en peces de 640)
        x1 = min(XR, x + 640)
        e.quad('paret', (x, 460, ZB), (x1, 460, ZB), (x1, 0, ZB), (x, 0, ZB), tex=(paret, (0, 0, x1 - x, 317)))
    for z in range(ZB, -500, -640):
        z1 = max(-500, z - 640)
        e.quad('paret', (XR, 460, z), (XR, 460, z1), (XR, 0, z1), (XR, 0, z), tex=(paret, (0, 0, z - z1, 317)))
    # el terra: la coberta de la presó, fosca
    e.quad('terra', (-900, 0, ZB), (XR, 0, ZB), (XR, 0, -600), (-900, 0, -600), ramp=STEEL, lvl=_terra)
    # la foscor als racons i a peu de les parets
    e.foscor('ombra', (-900, 0.3, ZB), (XR, 0.3, ZB), (XR, 0.3, ZB - 120), (-900, 0.3, ZB - 120),
             lambda s, t: 0.5 * (1 - t / 120))
    e.foscor('ombra', (XR - 120, 0.3, ZB), (XR, 0.3, ZB), (XR, 0.3, -500), (XR - 120, 0.3, -500),
             lambda s, t: 0.5 * (s / 120))
    # els cables apedaçats, de la caixa de dalt a les parets
    for (A, M, B, g) in (((-150, 300, 20), (-300, 170, 140), (-520, 230, ZB), 3.0),
                         ((-140, 290, 60), (-260, 210, 200), (-380, 280, ZB), 2.4),
                         ((150, 300, 40), (290, 190, 160), (XR, 250, 200), 3.0)):
        e.cable('cable', [A, M, B], IRON, 1.6, gruix=g)
    # el fons de la cambra: el camp (el dibuix pla, al pla del fons)
    e.quad('camp', (_x(GX0), _y(GY0), Z_FONS), (_x(GX1), _y(GY0), Z_FONS), (_x(GX1), _y(GY1), Z_FONS),
           (_x(GX0), _y(GY1), Z_FONS), tex=(_camp0(), (GX0, GY0, GX1, GY1)))
    # els anells de llautó de dalt i de baix (on van les bobines)
    for yy in (53, 261):
        e.caixa('anell', _x(GX0 + 4), _x(GX1 - 4), _y(yy + 7), _y(yy), 8, Z_FONS - 2, GOLD, 3.4,
                cares={'dalt': {'ramp': GOLD, 'lvl': lambda s, t, P: 4.4 - (0.6 if vnoise(s, t, 6, 31) > 0.72 else 0)},
                       'sota': {'ramp': GOLD, 'lvl': 1.4}, 'davant': {'ramp': GOLD, 'lvl': 3.6},
                       'esquerra': {'ramp': GOLD, 'lvl': 3.0}})
    # les bobines: cilindres drets (de qualsevol banda es veuen igual: figures dretes)
    bob = _bobines()
    for cx in reversed(COILS):                                        # (de lluny a prop)
        img = bob.crop((cx - 21, 44, cx + 22, 264))
        e.sprite('bobina', img, (21, 264 - 44 - 4), (_x(cx), _y(263), Z_BOB))
    # els muntants: el davant, el dibuix pla; el costat, ferro rovellat
    # (el de l'esquerra fa tot el costat de la cambra; el de la dreta és prim, i darrere hi ha la planxa del costat)
    e.caixa('costat', _x(GX1 + 30), _x(GX1 + 35), _y(303), _y(21), 14, Z_FONS + 4, IRON, 0.8,
            cares={'esquerra': {'ramp': FIELD, 'lvl': lambda s, t, P: 1.6 - abs(P[1] - 160) / 120
                                + (hr(int(s) // 4, int(t) // 4, 51) - 0.5) * 0.5}})
    for x0, z1 in ((GX0 - 35, Z_FONS + 4), (GX1 + 1, 16)):
        e.caixa('muntant', _x(x0), _x(x0 + 35), _y(303), _y(21), -6, z1, IRON, 2.2,
                cares={'davant': {'tex': (plana, (x0, 21, x0 + 35, 303))},
                       'esquerra': {'ramp': IRON, 'lvl': _planxa(1.3, 41)},
                       'dreta': {'ramp': IRON, 'lvl': _ferro(1.2, 43)}})
    # la caixa de dalt: el davant (la placa de llautó), els costats i la panxa, de ferro
    e.caixa('caixa', _x(GX0 - 40), _x(GX1 + 40), _y(37), FY + 2, -12, Z_FONS + 8, IRON, 2.0,
            cares={'davant': {'tex': (plana, (GX0 - 40, 0, GX1 + 40, 37))},
                   'sota': {'ramp': IRON, 'lvl': lambda s, t, P: 1.0 + 1.6 * max(0.0, 1 - t / 60)},
                   'esquerra': {'ramp': IRON, 'lvl': _planxa(1.6, 47)}})
    # la base: el davant (les franges de perill i la plaqueta), la tapa i el costat
    e.caixa('base', _x(GX0 - 45), _x(GX1 + 45), 0, _y(285), -24, Z_FONS + 10, IRON, 2.0,
            cares={'davant': {'tex': (plana, (GX0 - 45, 285, GX1 + 45, 318))},
                   'dalt': {'ramp': IRON, 'lvl': lambda s, t, P: 2.0 + (1.0 if t > Z_FONS + 30 else 0)
                            + (hr(int(s) // 3, int(t) // 3, 9) - 0.5) * 0.3},
                   'esquerra': {'ramp': IRON, 'lvl': _planxa(1.2, 49)}})
    # el vidre: un tel fred i els reflexos en diagonal, damunt de tot el de dins
    e.claror((_x(GX0), _y(GY0), -2), (_x(GX1), _y(GY0), -2), (_x(GX1), _y(GY1), -2), (_x(GX0), _y(GY1), -2),
             (236, 244, 255), lambda s, t: 0.16 if 19 <= (s + t * 0.55) % 220 <= 32 else
             (0.10 if 40 <= (s + t * 0.55) % 220 <= 43 else 0.03))
    # la nota: una tenda de paper damunt la base (la cara de davant, amb la lletra; la de darrere, en penombra)
    nx, ny, nz = NOTA
    a, b, d = NOTA_W / 2, NOTA_H, NOTA_D
    R = lambda lx, y, lz: _rot(nx, nz, NOTA_ANG, lx, y, lz)  # noqa: E731
    e.foscor('ombra', R(-a - 6, ny + 0.3, d + 6), R(a + 10, ny + 0.3, d + 6), R(a + 10, ny + 0.3, -d - 3),
             R(-a - 6, ny + 0.3, -d - 3), lambda s, t: 0.5)
    e.quad('nota_darrere', R(a, ny + b * 0.95, 0), R(-a, ny + b * 0.95, 0), R(-a + 2, ny, d), R(a + 2, ny, d),
           ramp=PAPERW, lvl=2.6, dues_cares=True)
    e.quad('nota', R(-a, ny + b * 0.95, 0), R(a, ny + b * 0.95, 0), R(a - 2, ny, -d), R(-a - 2, ny, -d),
           tex=(_nota_plana(), (0, 0, NOTA_W, NOTA_H)))
    # el primer pla: la caixa d'eines del Cargol, una bobina de fil de coure i una clau anglesa, en silueta
    tx, tz = -240, -20
    e.caixa_girada('eines', tx, tz, 92, 46, 44, 0.5, WALNUT, 0.8,
                   cares={'dalt': {'ramp': WALNUT, 'lvl': 1.2}, 'davant': {'ramp': WALNUT, 'lvl': 0.6},
                          'dreta': {'ramp': WALNUT, 'lvl': 1.0}})
    e.caixa_girada('eines', tx + 4, tz + 2, 70, 30, 6, 0.5, IRON, 1.0, y0=44)       # la nansa
    e.cable('eines', [(tx - 30, 48, tz - 14), (tx + 40, 47, tz + 26)], STEEL, 1.4, gruix=5)
    return e


# ─── La llum de la cambra, en pantalla ──────────────────────────────────────

def _proj(P):
    u, v, _ = CAM.projecta(P)
    return u, v


C_SCR = _proj((0, 160, Z_BOB))                                       # el centre del camp, a la pantalla
N_SCR = _proj((NOTA[0], NOTA[1] + 14, NOTA[2]))                      # la nota


def _llum_pantalla(img):
    """El violeta del camp sobre tot el que l'envolta, la claror càlida de la nota i la vinyeta forta."""
    A = np.asarray(img).astype(float)
    yy, xx = np.mgrid[0:H, 0:W].astype(float)
    k = 0.32 * np.maximum(0.0, 1 - np.hypot((xx - C_SCR[0]) / 420, (yy - C_SCR[1]) / 300))
    A[..., :3] += (np.array(VIOLET, float) - A[..., :3]) * k[..., None]
    k = 0.2 * np.maximum(0.0, 1 - np.hypot((xx - N_SCR[0]) / 130, (yy - N_SCR[1] - 20) / 50))
    A[..., :3] += (np.array((255, 230, 200), float) - A[..., :3]) * k[..., None]
    q = np.hypot((xx - 330) / 400, (yy - 200) / 260)
    A[..., :3] *= np.clip(1 - np.maximum(0.0, q - 0.55) * 1.4, 0, 1)[..., None]
    return Image.fromarray(A.clip(0, 255).astype(np.uint8), 'RGBA').copy()


@lru_cache(maxsize=None)
def _fons():
    cv = Canvas(light=LIGHT)
    e = escena(cv)
    return cv.img.copy(), e


def _dins(e, x, y):
    """El píxel és de dins la cambra (el camp o les bobines)?"""
    if not (0 <= x < W and 0 <= y < H):
        return False
    return e.ids[e.amo[int(y) * W + int(x)]] in ('camp', 'bobina', 'anell')


def bg(cv, t=0.0):
    TAU = 2 * math.pi
    base, e = _fons()
    img = base.copy()
    if t:
        img.alpha_composite(e.capa(_camp(t), sids=('camp',)))
    cv.img.paste(img)
    cv.P = cv.img.load()
    # la lluïssor del camp entre les bobines i la de la nota, que pulsa
    for gx in ((COILS[0] + COILS[1]) / 2, (COILS[1] + COILS[2]) / 2):
        u, v = _proj((_x(gx), 160, Z_BOB + 10))
        cv.glow(u, v, 40, (200, 170, 255), 0.3 + 0.08 * math.sin(TAU * (2 * t + gx / 53)))
    pulse = math.sin(TAU * t)
    nx, ny = N_SCR
    cv.glow(nx, ny, 70, (255, 236, 214), 0.45 + 0.12 * pulse)
    cv.glow(nx, ny, 32, (255, 250, 236), 0.28 + 0.1 * pulse)
    # guspires al voltant de la nota, que parpellegen
    for i in range(29):
        a = hr(i, 1) * math.pi * 2
        r = 21 + hr(i, 2) * 53
        x, y = round(nx + math.cos(a) * r * 1.2), round(ny - 6 + math.sin(a) * r * 0.55)
        tw = 0.5 + 0.5 * math.sin(TAU * ((1 + i % 3) * t + hr(i, 4)))
        if tw > 0.15 and _dins(e, x, y):
            cv.flat(x, y, mix(cv.P[x, y], (255, 244, 255), 0.8 * tw))
            if hr(i, 3) > 0.6:
                for dx, dy in ((1, 0), (-1, 0), (0, 1), (0, -1)):
                    if _dins(e, x + dx, y + dy):
                        cv.flat(x + dx, y + dy, mix(cv.P[x + dx, y + dy], (255, 236, 255), 0.35 * tw))
    # partícules del camp que pugen (al pla de les bobines)
    for i in range(80):
        f = (t * (1 + int(hr(i, 14) * 2)) + hr(i, 15)) % 1
        fx = GX0 + 5 + int(hr(i, 11) * (GX1 - GX0 - 10)) + round(math.sin(TAU * f + i) * 2)
        fy = GY0 + 5 + int(hr(i, 12) * (GY1 - GY0 - 10)) - round(f * (19 + hr(i, 16) * 21))
        a = math.sin(math.pi * f)
        if fy < GY0 + 3 or a < 0.12:
            continue
        x, y = (round(c) for c in _proj((_x(fx), _y(fy), Z_BOB - 20)))
        if _dins(e, x, y):
            cv.flat(x, y, mix(cv.P[x, y], (230, 214, 255), 0.75 * a))
            if hr(i, 13) > 0.6 and _dins(e, x, y + 1):
                cv.flat(x, y + 1, mix(cv.P[x, y + 1], (200, 180, 255), 0.4 * a))
    cv.img.paste(_llum_pantalla(cv.img))
    cv.P = cv.img.load()


PROPS = {}


# ─── Animació de fons ──────────────────────────────────────────────────────
# El camp crepita i els dos fils d'energia s'ondulen en sentits contraris (el camp pla de cada moment, reprojectat), les
# partícules pugen i s'esvaeixen, les guspires parpellegen i la nota fa llum polsant. Cada fotograma només té els
# píxels que canvien respecte del fons quiet (t = 0).

@lru_cache(maxsize=None)
def _base():
    cv = Canvas(light=LIGHT)
    bg(cv)
    return cv.img


def _ambient_frames(n=24):
    base = _base()
    frames = []
    for i in range(n):
        cv = Canvas(light=LIGHT)
        bg(cv, t=i / n)
        frames.append(frame_diff(base, cv.img))
    return frames


ANIMS = {'ambient': {'frames': _ambient_frames, 'frameDuration': 120}}
