"""
Dalt del pal de l'Arenga, a les tres de la matinada de l'Escena 9, amb vent. EN 3D (hd640/tres_d.py), a 1×.

Una càmera alta (a l'altura dels ulls, damunt la plataforma) que mira avall (picat) i cap a proa, girada cap a babord:
  - la **plataforma** de reixa, en diagonal, amb el sòcol de planxa i les **baranes** (la del fons i la de l'esquerra,
    que fuig cap a nosaltres): **a través de la reixa** es veu, molt avall, el que hi ha a sota: la coberta de proa de
    l'Arenga amb els seus llums i l'escuma de la roda, i el mar (es calcula raig a raig: «no miris avall»);
  - a l'esquerra, per damunt de la barana, el **mar**, que fuig fins a l'horitzó, amb les onades de la roda;
  - el **pal**, blanc, que puja fins a fora del quadre (el focus de la creueta, a dalt, il·lumina la plataforma), amb
    els graons, el rètol «ARNÈS» i la canaleta dels cables;
  - l'**antena** del satèl·lit (la cúpula, el collar amb el nus Bastida i la caixa del motor) al mig;
  - la boca de l'**escala**, al davant a la dreta: el forat a la reixa amb el marc groc, els esglaons i la tapa aixecada;
  - la **bandera** de Mar Obert, a l'asta de la cantonada del fons, i el salvavides a la barana;
  - primer pla: els puntals de la barana de l'esquerra, a prop i foscos, i l'obenc que baixa en diagonal.

Decorat `fosc` (el generador parat: el focus i els llums d'allà baix, apagats). ANIMS: `vent` (la bandera i les ratxes
d'esquitxos) i `mar` (les onades d'allà baix, també a través de la reixa).

El món: x a la dreta, y amunt (0 = la plataforma), z endavant (cap a proa); la coberta de l'Arenga és a y = −DH.
"""
import functools
import math

import hd640  # noqa: F401  (abans de cap hd.rooms: posa la llibreria a 640×360)
from hd.pix import Canvas, Light, W, H, hr, mix, B4
from hd.rooms.arenga import CAB, DARK, YELL
from hd.rooms.comu import _diff
from hd.rooms.exterior import fbm, smooth, NSEA, DECKX, ROPE, GLOW_WARM, REDH
from hd640.rooms import pal_pla_comu as PL
from hd640.rooms.coberta_popa_pla_comu import night_sky
from hd640.rooms.coberta_popa import _raig, mar, cilindre, frames_mar, _ombra
from hd640.tres_d import Camera, Escena, Llum

BOTTOM = 259
HOR = 80                                           # l'horitzó
PITCH = 0.32
CAM = Camera(pos=(330, 165, 60), yaw=-0.35, pitch=PITCH, f=400, centre=(320, HOR + 400 * math.tan(PITCH)))
K = 1.2
DH = 520                                           # la coberta de l'Arenga, sota la plataforma
SEA = -DH - 230
XL, XR, ZF, ZB = 0, 560, 200, 600                  # la plataforma (reixa): x i z
RAIL_H = round((PL.FLOOR_Y - PL.RAIL_TOP) * K)     # la barana (≈ 1 m)
MAST = (430, 540)                                  # el pal (x, z)
MAST_R = 12
ANT = (210, 500)                                   # l'antena
ESCALA = (285, 365, 468, 508)                      # la boca de l'escala: x0, x1, z0, z1
ASTA = (XL + 6, ZB - 6)                            # l'asta de la bandera, a la cantonada del fons
SHIP_X = MAST[0]                                   # l'eix de l'Arenga, sota el pal
ZC, ZR, XB = 1000, 1720, 400                       # l'Arenga: on s'aprima, la roda i mitja mànega
MOON = (150, 30)
LAMP_P = (MAST[0] - 30, 300, MAST[1] - 60)         # el focus de la creueta (fora del quadre), que mira avall

LIGHT = Light(ambient=0.0, vignette=None, floor_fade=None)
MASTW, GRATE, DOME = PL.MASTW, PL.GRATE, PL.DOME


def _llums(llums=True):
    out = [Llum((-6000, 6000, 9000), 1e6, 0.7, power=1.0)]           # la lluna
    if llums:
        out.append(Llum(LAMP_P, 420, 3.0, power=1.4))
    return out


# ─── Les textures (el dibuix pla) ─────────────────────────────────────────────

def _pla(fn, amb=0.6):
    cv = Canvas(light=Light(ambient=amb, vignette=None, floor_fade=None), transparent=True)
    fn(cv)
    return cv.img


ANT_BOX = (PL.ANT_X - 46, 78, PL.ANT_X + 48, PL.FLOOR_Y + 4)       # l'antena: la cúpula, el collar, el nus, el peu
SIGN_BOX = (PL.MAST_X - 15, 106, PL.MAST_X + 16, 125)               # el rètol «ARNÈS»
BUOY_BOX = (595 - 14, 148, 595 + 15, 176)                            # el salvavides (i el cap)


@functools.lru_cache(maxsize=None)
def _textures():
    def antena(cv):
        PL.antenna(cv)
        PL.knot(cv)
    return {
        'antena': _pla(antena),
        'pal': _pla(lambda cv: PL.mast(cv)),
        'boia': _pla(lambda cv: PL.lifebuoy(cv, 595, 163)),
    }


def _bandera(t):
    """La bandera (el dibuix pla), sola."""
    return _pla(lambda cv: PL.flag(cv, t), amb=0.2)


FLAG_BOX = (PL.FLAG_HX - PL.FLAG_W - 4, PL.FLAG_TOP - 8, PL.FLAG_HX + 8, PL.FLAG_TOP + PL.FLAG_H + 44)
FLAG_TOP_Y = 230                                   # on és el puny de la bandera, a l'asta


# ─── El cel i el que hi ha a sota (en pantalla, raig a raig) ─────────────────

def _cel(cv):
    night_sky(cv, 0, HOR, MOON, seed=9, clouds=0.62)
    for y in range(5, HOR - 4):                                      # ratxes de núvol esfilagarsat (vent)
        for x in range(W):
            n = fbm(x / 0.75 / 110 + y / 0.75 / 9, y / 0.75 / 3.2, 31)
            if n > 0.66:
                cv.flat(x, y, mix(cv.get(x, y), (70, 80, 102), min(0.45, (n - 0.66) * 2.4)))


def _bx(z):
    if z <= ZC:
        return XB
    t = min(1.0, (z - ZC) / (ZR - ZC))
    return XB * (1 - t ** 1.7)


HULLW = [(8, 10, 14), (16, 19, 25), (27, 31, 38), (41, 45, 52), (60, 63, 68), (84, 86, 88), (112, 112, 108),
         (146, 144, 134)]
DECK_LAMPS = ((SHIP_X - 150, 1250), (SHIP_X + 170, 1420))


def _escuma(x, z, phase):
    """L'escuma de la roda: dos braços que surten de la proa cap enrere i cap enfora."""
    dz = ZR - z
    if dz < -10:
        return 0.0
    ax = abs(x - SHIP_X)
    w = 6 + dz * 0.02
    k = 0.0
    for off in (0.0, 30.0):
        arm = abs(ax - (_bx(z) + 8 + dz * 0.22 + off))
        k = max(k, max(0.0, 1 - arm / w) * (1 - smooth(200, 2600, dz)) * (0.9 if off == 0 else 0.4))
    n = fbm(x / 30 + phase * 0.6, z / 40, 77)
    return max(0.0, k * (0.4 + 1.2 * (n - 0.3)))


def avall(cv, phase=0.0, llums=True, v0=None):
    """El que es veu cap avall: el mar (amb les onades del món) i, damunt, l'Arenga (la coberta de proa, la borda, el
    casc i l'escuma de la roda). Es pinta a tot arreu sota l'horitzó (la reixa i les baranes ja ho tapen)."""
    mar(cv, CAM, SEA, False, phase, v0=v0, v1=BOTTOM, glint_u=MOON[0], seed=4, wind=0.9)
    hor = HOR
    for v in range(max(int(hor) + 1, v0 or 0), BOTTOM + 1):
        for u in range(W):
            D = _raig(CAM, u + 0.5, v + 0.5, -DH)
            if D is None:
                continue
            x, z = D[0], D[2]
            if z < ZR and abs(x - SHIP_X) < _bx(z):
                # la coberta de proa, d'aquí a 10 m avall: fosca, amb els llums de coberta i la borda blanca
                edge = _bx(z) - abs(x - SHIP_X)
                if edge < 10:
                    lvl = 4.6 - edge * 0.05
                    cv.put(u, v, HULLW, lvl, lit=0)
                    continue
                lvl = 1.6 + (hr(int(x) // 12, int(z) // 40, 3) - 0.5) * 0.5
                if llums:
                    for lx, lz in DECK_LAMPS:
                        d = math.hypot((x - lx) / 140, (z - lz) / 140)
                        if d < 1:
                            lvl += 2.4 * (1 - d) ** 1.6
                            if d < 0.06:
                                lvl = 7.0
                if abs(x - SHIP_X) < 6 and ZR - 40 < z < ZR - 10:
                    lvl = 6.0 if llums else 3.0                     # el llum de navegació, a la roda
                cv.put(u, v, DECKX, lvl, lit=0)
                continue
            S = _raig(CAM, u + 0.5, v + 0.5, SEA)
            if S is None:
                continue
            sx, sz = S[0], S[2]
            if sz < ZR + 20 and abs(sx - SHIP_X) < _bx(sz) + 4:
                # el raig toca el costat del casc abans que el mar: la planxa blanca i la línia vermella
                cv.put(u, v, HULLW, 3.0 + (hr(u, v // 2) - 0.5) * 0.4, lit=0)
                continue
            k = _escuma(sx, sz, phase)
            if k > 0.08 + (B4[v & 3][u & 3] - 0.5) * 0.2:
                cv.flat(u, v, mix(cv.get(u, v), (170, 186, 190), min(0.7, k)))
    # la boira: tot el que és molt avall, més fosc i blavós
    for v in range(max(int(hor) + 40, v0 or 0), BOTTOM + 1):
        k = min(0.3, (v - hor - 40) / 400)
        for u in range(W):
            cv.flat(u, v, mix(cv.get(u, v), (20, 26, 36), k))


# ─── La plataforma ───────────────────────────────────────────────────────────

def _reixa(s, t):
    """La reixa: platines cada 9 (al llarg de z) i travessers cada 30; la resta, forat (es veu el que hi ha a sota)."""
    x, z = XL + s, ZB - t
    x0, x1, z0, z1 = ESCALA
    if x0 - 3 < x < x1 + 3 and z0 - 3 < z < z1 + 3:
        return False
    return (x % 9) < 2.6 or (z % 30) < 2.2 or s < 6 or s > (XR - XL) - 6 or t < 6


def _reixa_lvl(s, t, P):
    x, z = P[0], P[2]
    if (x % 9) < 2.6 and (z % 30) < 2.2:
        return 4.6
    if (x % 9) < 2.6:
        return 3.9 + (0.4 if (x % 9) < 1.0 else 0) + (hr(int(x) // 9, int(z) // 6, 81) - 0.5) * 0.3
    if s < 6 or s > (XR - XL) - 6 or t < 6:
        return 3.4
    return 3.1


def plataforma(e):
    e.quad('reixa', (XL, 0, ZB), (XR, 0, ZB), (XR, 0, ZF), (XL, 0, ZF), ramp=GRATE, lvl=_reixa_lvl, forma=_reixa)
    # el sòcol de planxa a les vores (el de l'esquerra i el del fons)
    e.quad('reixa', (XL, 9, ZF), (XL, 9, ZB), (XL, 0, ZB), (XL, 0, ZF), ramp=MASTW, lvl=3.0, dues_cares=True)
    e.quad('reixa', (XL, 9, ZB), (XR, 9, ZB), (XR, 0, ZB), (XL, 0, ZB), ramp=MASTW,
           lvl=lambda s, t, P: 3.4 - t * 0.1, dues_cares=True)


def _tub_h(e, sid, A, B, r, lvl):
    e.tub(sid, A, B, r, MASTW, lvl, llum_dir=(-0.3, 1.0))


def baranes(e, near_sid='primer_pla'):
    """La barana del fons i la de l'esquerra: puntals i tres tubs. Els puntals de prop de l'esquerra fan de primer pla."""
    hs = (RAIL_H, RAIL_H * 0.62, RAIL_H * 0.3)
    for h, r, lv in zip(hs, (2.6, 2.0, 2.0), (5.0, 4.4, 4.0)):
        _tub_h(e, 'barana', (XL, h, ZB), (XR, h, ZB), r, lv)
    for x in range(XL + 4, XR, 70):
        e.tub('barana', (x, 0, ZB), (x, RAIL_H + 2, ZB), 2.6, MASTW, 4.4, llum_dir=(-0.3, 1.0))
    # la de l'esquerra: els trams de prop, foscos (primer pla)
    zs = list(range(ZB, ZF - 1, -80))
    for k, z in enumerate(zs):
        sid = 'barana' if z > 420 else near_sid
        e.tub(sid, (XL, 0, z), (XL, RAIL_H + 2, z), 2.6, MASTW if sid == 'barana' else PL.GRATE, 4.4 if sid == 'barana' else 2.0,
              llum_dir=(-0.3, 1.0))
    for h, r, lv in zip(hs, (2.6, 2.0, 2.0), (5.0, 4.4, 4.0)):
        _tub_h(e, 'barana', (XL, h, ZB), (XL, h, 420), r, lv)
        e.tub(near_sid, (XL, h, 420), (XL, h, ZF - 40), r, PL.GRATE, lv - 2.4, llum_dir=(-0.3, 1.0))


def pal(e, tex, llums=True):
    mx, mz = MAST
    cilindre(e, 'pal', mx, mz, MAST_R, -40, 700, MASTW,
             lambda a, y, P: 4.6 + 1.6 * math.cos(a - 2.6) - (0.6 if (int(y) % 98) < 4 else 0)
             + (hr(int(a * 9), int(y) // 6) - 0.5) * 0.25, n=20)
    for y in (60, 158):                                              # les juntes amb brida
        cilindre(e, 'pal', mx, mz, MAST_R + 3, y, y + 5, MASTW, lambda a, y_, P: 4.6 + 1.2 * math.cos(a - 2.6), n=20)
    # els graons (U de rodó), al costat que mira cap a nosaltres
    for y in range(14, 700, 15):
        a0 = math.radians(215)
        p = (mx + (MAST_R + 1) * math.cos(a0), y, mz + (MAST_R + 1) * math.sin(a0))
        q = (mx + (MAST_R + 7) * math.cos(a0), y, mz + (MAST_R + 7) * math.sin(a0))
        e.cable('pal', [p, q, (q[0] + 4, y, q[2] - 6), (p[0] + 4, y, p[2] - 6)], MASTW, 5.0, gruix=1.2)
    # la canaleta dels cables
    a1 = math.radians(300)
    cx, cz = mx + (MAST_R + 2) * math.cos(a1), mz + (MAST_R + 2) * math.sin(a1)
    e.caixa('pal', cx - 2, cx + 2, 0, 700, cz - 2, cz + 2, CAB, 2.4)
    # el rètol «ARNÈS», amb les brides
    sb = SIGN_BOX
    e.sprite('pal', tex['pal'].crop(sb), ((sb[2] - sb[0]) / 2, sb[3] - sb[1]), (mx + 12, 100, mz - MAST_R - 1), escala_img=K)


def antena(e, tex):
    ax, az = ANT
    _ombra(e, ax, az, 40, 18, 0.5, dx=-18, dz=-10)
    b = ANT_BOX
    e.sprite('antena', tex['antena'].crop(b), (PL.ANT_X - b[0], PL.FLOOR_Y + 3 - b[1]), (ax, 0, az), escala_img=K)
    # el cap del nus, tens fins a la barana del fons
    e.cable('antena', [(ax + 32, (PL.FLOOR_Y - 139) * K, az - 4), (ax + 120, RAIL_H * 0.8, ZB)], ROPE, 3.4, gruix=1.4)


def escala(e, llums=True):
    """La boca de l'escala: el forat (fosc, amb el vermell de nit del pont al fons), els esglaons, el marc groc, la tapa
    de reixa aixecada contra el pal i els passamans."""
    x0, x1, z0, z1 = ESCALA
    e.quad('escala', (x0, -0.5, z1), (x1, -0.5, z1), (x1, -0.5, z0), (x0, -0.5, z0), ramp=DARK,
           lvl=lambda s, t, P: 0.6 + t * 0.03 + (1.6 * max(0.0, 1 - math.hypot(s - (x1 - x0) / 2, t - (z1 - z0) * 0.7) / 40)
                                                  if llums else 0))
    for k in range(3):                                               # els esglaons, avall
        z = z1 - 10 - k * 12
        e.quad('escala', (x0 + 22, -6 - k * 9, z + 2), (x1 - 22, -6 - k * 9, z + 2), (x1 - 22, -6 - k * 9, z - 2),
               (x0 + 22, -6 - k * 9, z - 2), ramp=MASTW, lvl=2.6 - k * 0.5)
    for (ax, az), (bx, bz) in (((x0, z1), (x1, z1)), ((x1, z1), (x1, z0)), ((x1, z0), (x0, z0)), ((x0, z0), (x0, z1))):
        e.caixa('escala', min(ax, bx) - 2, max(ax, bx) + 2, 0, 2, min(az, bz) - 2, max(az, bz) + 2, YELL, 3.4)
    # la tapa, aixecada (inclinada cap al fons)
    lid = ((x0 + 6, 46, z1 + 14), (x1 - 6, 46, z1 + 14), (x1 - 6, 1, z1 + 2), (x0 + 6, 1, z1 + 2))
    e.quad('escala', *lid, ramp=GRATE, dues_cares=True,
           lvl=lambda s, t, P: (3.6 if (int(s) % 5 < 1 or int(t) % 5 < 1) else 1.2) if not (5 < t < 11) else
           (3.6 if (int(s + t) // 4) % 2 else 1.0))
    e.quad('escala', (x0 + 6, 46, z1 + 14), (x1 - 6, 46, z1 + 14), (x1 - 6, 40, z1 + 12.4), (x0 + 6, 40, z1 + 12.4),
           ramp=YELL, lvl=lambda s, t, P: 3.6 if (int(s) // 4) % 2 else 0.6, dues_cares=True)
    for hx in (x0 + 10, x1 - 10):                                    # els passamans
        e.cable('escala', [(hx, -10, z0 + 6), (hx, 34, z0 + 6), (hx + (4 if hx < x1 - 20 else -4), 40, z0 + 12),
                           (hx, 34, z0 + 18), (hx, 0, z0 + 18)], MASTW, 4.8, gruix=1.6)


def bandera(e, t=0.0):
    """L'asta de la cantonada del fons, amb la bandera de Mar Obert que bat cap a l'esquerra."""
    ax, az = ASTA
    e.tub('asta', (ax, 0, az), (ax, FLAG_TOP_Y + 14, az), 1.8, MASTW, 4.6, llum_dir=(-0.3, 1.0))
    img = _bandera(t).crop(FLAG_BOX)
    e.sprite('bandera', img, (PL.FLAG_HX - FLAG_BOX[0], PL.FLAG_TOP - FLAG_BOX[1]), (ax, FLAG_TOP_Y, az),
             escala_img=K)


def obenc(e):
    """L'obenc: un cable que baixa del cap del pal cap a la borda de l'Arenga, en diagonal per davant."""
    e.cable('primer_pla', [(MAST[0] - 40, 520, MAST[1] - 10), (XL - 60, 150, 330), (XL - 160, -200, 120)], PL.GRATE, 2.0,
            gruix=2.0)


def boia(e, tex):
    b = BUOY_BOX
    e.sprite('barana', tex['boia'].crop(b), ((b[2] - b[0]) / 2, 0), (XL + 300, RAIL_H, ZB + 2), escala_img=K)


# ─── Composició ─────────────────────────────────────────────────────────────

def escena(cv, llums=True, flag_t=0.0, bandera_on=True):
    tex = _textures()
    _cel(cv)
    avall(cv, 0.0, llums)
    e = Escena(cv, CAM, _llums(llums), ambient=-0.3 if llums else -0.9)
    plataforma(e)
    if llums:                                                        # el bassal del focus, a la reixa
        lx, ly, lz = LAMP_P
        e.claror((XL, 0.4, ZB), (XR, 0.4, ZB), (XR, 0.4, ZF), (XL, 0.4, ZF), (255, 210, 140),
                 lambda s, t: 0.22 * max(0.0, 1 - math.hypot((XL + s - lx) / 260, (ZB - t - lz) / 200)) ** 1.4)
    if bandera_on:
        bandera(e, flag_t)
    else:
        e.tub('asta', (ASTA[0], 0, ASTA[1]), (ASTA[0], FLAG_TOP_Y + 14, ASTA[1]), 1.8, MASTW, 4.6, llum_dir=(-0.3, 1.0))
    baranes(e)
    boia(e, tex)
    antena(e, tex)
    escala(e, llums)
    pal(e, tex, llums)
    obenc(e)
    return e


def _render(llums=True, flag_t=0.0, bandera_on=True):
    cv = Canvas(light=LIGHT)
    e = escena(cv, llums, flag_t, bandera_on)
    cv.rect(0, BOTTOM + 1, W - 1, H - 1, [(0, 0, 0)], 0, lit=0)
    return cv.img, e


@functools.lru_cache(maxsize=None)
def _base():
    return _render()


def bg(cv):
    cv.img.paste(_base()[0])
    cv.P = cv.img.load()


# ─── Animacions ─────────────────────────────────────────────────────────────

@functools.lru_cache(maxsize=None)
def _sense_bandera():
    return _render(bandera_on=False)


def _flag_capa(t):
    """La bandera al temps t, on es veu (on no hi ha res davant: el cel, el mar d'allà baix)."""
    from PIL import Image
    clean, ec = _sense_bandera()
    cv = Canvas(light=LIGHT, transparent=True)
    e = Escena(cv, CAM, [])
    ax, az = ASTA
    img = _bandera(t).crop(FLAG_BOX)
    e.sprite('bandera', img, (PL.FLAG_HX - FLAG_BOX[0], PL.FLAG_TOP - FLAG_BOX[1]), (ax, FLAG_TOP_Y, az), escala_img=K)
    out = Image.new('RGBA', (W, H), (0, 0, 0, 0))
    src, dst = cv.img.load(), out.load()
    for y in range(BOTTOM):
        for x in range(W):
            c = src[x, y]
            if c[3] and ec.ids[ec.amo[y * W + x]] in ('', 'asta'):
                dst[x, y] = c
    return out


def _frames_vent():
    """La bandera que bat i ratxes d'esquitxos que travessen la pantalla."""
    base, _ = _base()
    clean, _ = _sense_bandera()
    frames = []
    n = 8
    for i in range(n):
        out = clean.copy()
        out.alpha_composite(_flag_capa(i * (2 * math.pi / 1.4) / n))
        cv = Canvas(light=LIGHT, img=out)
        for k in range(6):                                           # ratxes d'esquitxos, molt ràpides
            sx = (W + 53) - ((i * 81 + k * 129) % (W + 107))
            sy = 40 + int(hr(k, 3) * 200)
            ln = 8 + int(hr(k, 4) * 11)
            for j in range(ln):
                x = sx + j
                if 0 <= x < W and sy + j // 5 < BOTTOM:
                    cv.flat(x, sy + j // 5, mix(cv.get(x, sy + j // 5), (180, 196, 206), 0.35 * (1 - j / ln)))
        frames.append(_diff(cv.img, base))
    return frames


def _punts_avall():
    _, e = _base()
    return [(x, y) for y in range(HOR + 1, BOTTOM) for x in range(W) if e.amo[y * W + x] == 0]


def _frames_mar():
    base, _ = _base()
    return frames_mar(base, _punts_avall(), lambda cv, ph: avall(cv, ph * 6, True, v0=HOR))


ANIMS = {'vent': {'frames': _frames_vent, 'frameDuration': 110},
         'mar': {'frames': _frames_mar, 'frameDuration': 260}}


# ─── El generador parat (Escena 9) ─────────────────────────────────────────

def fosc(cv):
    """Decorat `fosc`: el focus i els llums d'allà baix, apagats. On hi ha animacions (la bandera, el mar d'allà baix)
    és una capa negra semitransparent, perquè es continuïn movent; la resta, el dibuix a les fosques."""
    base, e = _base()
    dark, _ = _render(llums=False)
    pb, pd, o = base.load(), dark.load(), cv.P
    anim = set(_punts_avall())
    x0, y0 = CAM.projecta((ASTA[0] - 120, FLAG_TOP_Y + 30, ASTA[1]))[:2]
    x1, y1 = CAM.projecta((ASTA[0] + 20, FLAG_TOP_Y - 60, ASTA[1]))[:2]
    for y in range(BOTTOM):
        for x in range(W):
            if (x, y) in anim or (x0 - 10 <= x <= x1 + 10 and y0 - 10 <= y <= y1 + 10 and e.amo[y * W + x] == 0):
                lb = sum(pb[x, y][:3]) + 1
                a = max(0.0, min(1.0, 1 - sum(pd[x, y][:3]) / lb))
                if a > 0.02:
                    o[x, y] = (0, 0, 0, int(a * 255))
            elif pd[x, y] != pb[x, y]:
                o[x, y] = pd[x, y]


PROPS = {'fosc': fosc}


# ─── Geometria ───────────────────────────────────────────────────────────────

def _p(x, z, y=0.0):
    u, v, _ = CAM.projecta((x, y, z))
    return round(u), round(v)


def _rect_mon(*Ps):
    pts = [CAM.projecta(P) for P in Ps]
    return (max(0, round(min(p[0] for p in pts))), max(0, round(min(p[1] for p in pts))),
            min(W - 1, round(max(p[0] for p in pts))), min(BOTTOM, round(max(p[1] for p in pts))))


def _amo(ids):
    def mask(x, y):
        _, e = _base()
        return e.ids[e.amo[y * e.cv.w + x]] in ids
    return mask


def _escala_a(v):
    """L'escala d'un personatge amb els peus a la y de pantalla `v` (al terra; amb picat, també només depèn de v)."""
    P = _raig(CAM, 320, v, 0)
    return CAM.escala(P)


FRONT = [
    {'id': 'davant', 'mask': _amo({'primer_pla'}), 'baseline': 999, 'zIndex': 20, 'variants': ('fosc',)},
    {'id': 'davant_antena', 'mask': _amo({'antena'}), 'baseline': _p(ANT[0], ANT[1] - 14)[1], 'zIndex': 20, 'variants': ('fosc',)},
    {'id': 'davant_pal', 'mask': _amo({'pal'}), 'baseline': _p(MAST[0], MAST[1] - MAST_R)[1], 'zIndex': 20, 'variants': ('fosc',)},
]

V_PROP = 257
_NL, _NR = _raig(CAM, 0, V_PROP, 0), _raig(CAM, W - 1, V_PROP, 0)
WALK_MON = [(XL + 30, ZB - 30), (XR - 40, ZB - 30), (_NR[0], _NR[2]), (max(XL + 30, _NL[0]), _NL[2])]
if _NL[0] < XL + 30:                               # (la barana de l'esquerra talla la vora de baix)
    WALK_MON[3] = (XL + 30, _raig(CAM, 0, V_PROP, 0)[2])
_WALK = [(min(W - 1, max(0, u)), min(V_PROP, v)) for u, v in (_p(x, z) for x, z in WALK_MON)]
_V_FONS, _V_PROP = min(v for _, v in _WALK), max(v for _, v in _WALK)


def _cercle(cx, cz, r, n=10):
    return [_p(cx + r * math.cos(2 * math.pi * i / n), cz + r * math.sin(2 * math.pi * i / n)) for i in range(n)]


x0_, x1_, z0_, z1_ = ESCALA
_FORATS = [_cercle(ANT[0], ANT[1], 34, 10), _cercle(MAST[0], MAST[1], MAST_R + 18, 8),
           [_p(x0_ - 10, z0_ - 10), _p(x1_ + 10, z0_ - 10), _p(x1_ + 10, z1_ + 18), _p(x0_ - 10, z1_ + 18)]]

GEOMETRIA = {
    'things': {
        'escala': {'rect': _rect_mon((x0_, 0, z0_), (x1_, 0, z0_), (x0_, 48, z1_ + 14), (x1_, 48, z1_ + 14)),
                   'walk': _p(x0_ - 20, z0_ - 14)},
        'antena': {'rect': _rect_mon((ANT[0] - 50, 0, ANT[1]), (ANT[0] + 50, 0, ANT[1]),
                                     (ANT[0] - 50, (PL.FLOOR_Y - 80) * K, ANT[1])),
                   'walk': _p(ANT[0] + 30, ANT[1] - 70)},
        'mar': {'rect': (0, HOR + 6, _p(XL, ZB, RAIL_H)[0] - 6, BOTTOM - 40), 'walk': _p(XL + 40, 470)},
    },
    'spawns': {'iri': _p(240, 450), 'vet': _p(140, 470), 'marcel': _p(490, ZB - 34)},
    'walkable': _WALK,
    'forats': _FORATS,
    'floorSquash': 0.45,
    # L'ombra de contacte: el focus de la creueta, a dalt i una mica al fons: curta i cap al davant.
    'characterShadow': {'enabled': True, 'color': '#06080c', 'alpha': 0.45, 'squash': 0.42, 'core': 0.6,
                        'light': {'x': _p(LAMP_P[0], LAMP_P[2])[0], 'y': _p(LAMP_P[0], LAMP_P[2])[1], 'stretch': 0.5,
                                  'reach': 160}},
    'regions': [{'id': 'perspectiva', 'active': True, 'scaleEnabled': True, 'scaleWalkSpeed': True,
                 'scaleTop': round(_escala_a(_V_FONS - 2), 3), 'scaleBottom': round(_escala_a(_V_PROP + 2), 3),
                 'points': [(0, _V_FONS - 2), (W - 1, _V_FONS - 2), (W - 1, _V_PROP + 2), (0, _V_PROP + 2)]}],
    'characterLights': {
        'ambient': '#7c8aa8',
        'lights': [{'x': _p(LAMP_P[0], LAMP_P[2], 120)[0], 'y': _p(LAMP_P[0], LAMP_P[2], 120)[1], 'radius': 260,
                    'color': '#ffd28c', 'intensity': 0.8, 'whenPropHidden': 'fosc'}],
    },
}
