"""
El graner de la granja (Escena 1 i 2). Sala «de prop» (persones de ≈100 px). EN 3D (hd640/tres_d.py), a 1×.

Una càmera a l'altura del pit, una mica girada cap a la dreta i mirant un pèl avall, dins el graner de taulons: a
l'esquerra, la paret del banc de llavors fuig cap al fons, amb els prestatges de sacs en files que s'empetiteixen; al
fons, la paret del portal gran, obert al pati (fora, el sol, els camps amb els solcs que fugen i la Canonada a
l'horitzó), amb les fulles obertes cap endins; a la dreta, la paret del fons i la del costat fan l'angle, amb el banc de
treball i la caixa d'eines vermella. Al mig, separat de les parets i girat, el tractor de l'avi (el Brau 40) en 3/4:
el morro amb la graella i els fars, el costat (el dibuix de perfil de sempre) i el capó vist des de dalt. Les bigues
del sostre fugen cap al fons; un pilar i una biga, a contrallum, fan de primer pla. Feixos de sol baixen en diagonal
per les escletxes del sostre, i la llum del portal s'estira pel terra (palla escampada, més grossa a prop). Es passa per
darrere del tractor.

Tot el detall ve del graner pla de sempre (granja_graner_pla_comu.py): les parets de taulons, el banc de llavors, el
tractor, les eines i els decorats (`reg`, `tractor_obert`, `sacs_tres`, `sac_quart`) es dibuixen de cara i es
projecten. ANIMS: `pols` (les volves de pols dins els feixos de sol i a la llum del portal).

El món: x a la dreta (0 = la paret de les llavors), y amunt (0 = el terra), z cap al fons (330 = la paret del portal);
1 unitat = 1 píxel de sala a la distància on un personatge fa 100 px (escala 1).
"""
import functools
import math

import hd640  # noqa: F401  (posa la llibreria de dibuix a 640×360)
from PIL import Image

from hd.pix import Canvas, Light, W, hr, mix, B4
from hd.rooms.exterior import fbm, smooth
from hd640.rooms import granja_graner_pla_comu as PL
from hd640.rooms.terra2_comu import (SKY, HILL, FIELD, EARTH, COL, GREYW, BLACKT, IRONR, STRAW, PAPER, text, text_width,
                                     motes_frames, _diff)
from hd640.tres_d import Camera, Escena, Llum, llum_personatges

WOOD, DIRT, TRED = PL.WOOD, PL.DIRT, PL.TRED

BOTTOM = 259                                       # la sala acaba aquí (a sota, la barra de verbs)
ZW = 330                                           # la paret del portal (el fons)
XR = 640                                           # la paret de la dreta
HW = 215                                           # el sostre
FY = PL.FLOOR_Y                                    # al dibuix pla, on la paret toca a terra (y del món = FY − y pla)
OFF = 156                                          # a la paret del fons, x del món = x del pla − OFF
DOOR = (PL.DOOR[0] - OFF, PL.DOOR[2] - OFF, 194)  # el portal: x0, x1 i l'alçada (més alt que al pla: es veu el cel)
SHELF = (34, 6, ZW - 2)                            # el banc de llavors: el gruix (x) i de z0 a z1
SHELF_H = FY - 30                                  # (al pla, de y 30 a terra)
TRAC = (400.0, 200.0, 0.6)                         # el tractor: el centre (x, z) i el gir (el morro, cap a l'esquerra)
TRAC_B = 22                                        # mig ample del capó
BANC = (586, XR, 226, 322, 30)                     # el banc de treball: x0, x1, z0, z1 i l'alçada
BALES = ((166, 226, 290, 326, 0, 28), (172, 220, 294, 324, 28, 52))
PILAR = (536, 560, 4, 28)                          # el pilar del primer pla (x0, x1, z0, z1)
SUN = (255, 222, 160)

CAM = Camera(pos=(270, 155, -270), yaw=0.06, pitch=0.06, f=360, centre=(320, 80))

LIGHT = Light(ambient=0.0, vignette=None, floor_fade=None)     # (la llum és la del món: la de l'Escena)
FLAT = Light(ambient=0.0, vignette=None, floor_fade=None)      # (els dibuixos plans, sense la llum de la sala plana)
DOOR_C = ((DOOR[0] + DOOR[1]) / 2, 0.0, ZW)        # el llindar del portal, al mig
LLUMS = [
    Llum((DOOR_C[0], 70, ZW + 50), 520, 2.6, power=1.3),        # el sol del portal
    Llum((240, 30, 200), 150, 1.0, power=1.6),                   # la llum del portal, estirada pel terra
    Llum((300, 230, 230), 300, 0.6, power=1.4),                  # la claror de les escletxes del sostre
]
AMBIENT = -1.3

# Els feixos de sol: (el forat del sostre (x, z), la taca a terra (x, z), el gruix a dalt i a baix)
DIR = (-0.42, -1.0, -0.26)                         # cap on baixen (des de dalt a la dreta, cap a l'esquerra i endavant)
FORATS = [(330, 290, 5, 15), (470, 324, 4, 12), (566, 214, 6, 17), (196, 150, 4, 12)]   # (el 2n cau darrere el tractor)


def _feixos():
    out = []
    for x, z, ra, rb in FORATS:
        A = (x, HW, z)
        k = HW / -DIR[1]
        out.append((A, (x + DIR[0] * k, 0.0, z + DIR[2] * k), ra, rb))
    return out


FEIXOS = _feixos()


# ─── Els dibuixos plans (textures) ───────────────────────────────────────────

def _pla(fn, transparent=False):
    cv = Canvas(light=FLAT, transparent=transparent)
    fn(cv)
    return cv.img


@functools.lru_cache(maxsize=None)
def _textures():
    def fons(cv):
        PL.walls(cv)
        PL.clutter(cv, bales=False)

    def dreta(cv):
        PL.walls(cv)
        PL.workbench(cv)

    return {
        'fons': _pla(fons),
        'dreta': _pla(dreta),
        'llavors': _pla(lambda cv: PL.seeds(cv, retol=False), True),
        'retol': _retol(),
        'llavors2': _pla(lambda cv: PL.seeds(cv, retol=False), True),
        'tractor': _pla(PL.tractor, True),
        'caixa': _pla(PL.caixa_eines),
    }


def _retol():
    """El rètol del banc de llavors, pintat a mà en una post (a part: penjat de cara, que es llegeixi)."""
    cv = Canvas(52, 13, light=None)
    cv.rect(0, 0, 51, 12, PAPER, lambda x, y: 4.0 + (fbm(x / 4, y / 4, 8) - 0.5) * 0.8 - (1.4 if y in (0, 12) else 0), lit=0)
    s = 'LLAVORS'
    text(cv, s, 26 - text_width(s) // 2, 3, BLACKT, 1.0, lit=0, flat=(70, 40, 30))
    return cv.img


@functools.lru_cache(maxsize=None)
def _tractor_obert():
    def fn(cv):
        PL.tractor(cv)
        PL.tractor_obert(cv)
    return _pla(fn, True)


# ─── Peces ──────────────────────────────────────────────────────────────────

def _T(lx, y, lz):
    """Del sistema del tractor (x al llarg, el morro a −x; z de costat, −z cap a la càmera) al món."""
    cx, cz, a = TRAC
    c, s = math.cos(a), math.sin(a)
    return (cx + lx * c - lz * s, y, cz + lx * s + lz * c)


def _taulons(lvl0, seed, ample=13, horitzontal=False):
    """Taulons verticals (o horitzontals) en coordenades del món, amb les juntes i els nusos."""
    def L(s, t, P):
        u = t if horitzontal else s
        p = int(u // ample)
        e = u % ample
        v = lvl0 + (hr(p, seed) - 0.5) * 1.0 + (fbm((s if horitzontal else u) / 5, (t if not horitzontal else u) / 30, p) - 0.5) * 0.9
        if e < 1.0:
            v -= 1.6
        elif e < 2.0:
            v += 0.5
        return v
    return L


def _palla(s, t, P):
    """El terra de terra batuda, amb la palla escampada: brins grossos a prop i menuts al fons (són del món)."""
    x, z = P[0], P[2]
    v = 2.8 + (fbm(x / 60, z / 30, 31) - 0.5) * 1.2 + (hr(int(x) // 2, int(z) // 2, 4) - 0.5) * 0.5
    C = 9.0
    ix, iz = int(x // C), int(z // C)
    for jx in (ix - 1, ix, ix + 1):
        for jz in (iz - 1, iz, iz + 1):
            if hr(jx, jz, 21) > 0.62:
                continue
            cx, cz = (jx + hr(jx, jz, 22)) * C, (jz + hr(jx, jz, 23)) * C
            a = hr(jx, jz, 24) * math.pi
            hl = 2.0 + hr(jx, jz, 25) * 3.0
            dx, dz = math.cos(a), math.sin(a)
            px, pz = x - cx, z - cz
            u = max(-hl, min(hl, px * dx + pz * dz))
            if math.hypot(px - u * dx, pz - u * dz) < 0.55:
                return 4.4 + hr(jx, jz, 26) * 1.6
    return v


def exterior(e):
    """Fora del portal: el cel de pols, els turons, la Canonada, els camps amb els solcs que fugen, la tanca."""
    zf = 6000
    e.quad('fora', (-9000, 2600, zf), (9000, 2600, zf), (9000, -10, zf), (-9000, -10, zf), ramp=SKY,
           lvl=lambda s, t, P: 7.4 - P[1] / 2600 * 2.4 + (fbm(P[0] / 900, P[1] / 300, 31) - 0.5) * 0.6)
    e.quad('fora', (-9000, 220, zf - 10), (9000, 220, zf - 10), (9000, -10, zf - 10), (-9000, -10, zf - 10), ramp=HILL,
           lvl=6.6, forma=lambda s, t: 230 - t < 120 + 90 * fbm(s / 1400, 0.3, 7))
    e.quad('fora', (-1560, 1500, zf - 20), (-1490, 1500, zf - 20), (-1490, 0, zf - 20), (-1560, 0, zf - 20), ramp=COL,
           lvl=lambda s, t, P: 6.2 if t % 60 > 6 else 7.4)

    def camp(s, t, P):
        x, z = P[0], P[2]
        if z < ZW + 110:
            return 7.2 + (hr(int(x) // 2, int(z) // 2) - 0.5) * 0.8 - (1.6 if hr(int(x) // 5, int(z) // 3) > 0.9 else 0)
        fur = math.sin(x / 10.0 * math.pi) * (1 - smooth(900, 3000, z))
        return 6.6 + fur * 0.5 + (fbm(x / 80, z / 200, 11) - 0.5) * 0.8
    e.quad('fora', (-9000, 0, zf - 30), (9000, 0, zf - 30), (9000, 0, ZW), (-9000, 0, ZW), ramp=FIELD, lvl=camp)
    for k in range(-6, 10):                                         # la tanca del pati, a contrallum
        x = k * 36 + 10
        e.caixa('fora', x - 1.5, x + 1.5, 0, 30, ZW + 240, ZW + 243, GREYW, 3.6)
    e.quad('fora', (-300, 22, ZW + 240), (400, 22, ZW + 240), (400, 18, ZW + 240), (-300, 18, ZW + 240), ramp=GREYW,
           lvl=4.0)


def portal(e):
    x0, x1, h = DOOR
    # el marc: els muntants i la llinda
    e.caixa('portal', x0 - 7, x0, 0, h + 7, ZW - 8, ZW, WOOD, 3.4)
    e.caixa('portal', x1, x1 + 7, 0, h + 7, ZW - 8, ZW, WOOD, 3.4)
    e.caixa('portal', x0 - 7, x1 + 7, h, h + 7, ZW - 8, ZW, WOOD, 3.6)
    # les dues fulles, obertes cap endins (la de l'esquerra gairebé contra el banc de llavors)
    for hx, ang, sgn in ((x0 - 7, 1.25, 1), (x1 + 7, 1.1, -1)):
        w = (x1 - x0) / 2
        dx, dz = sgn * math.cos(ang) * w, -math.sin(ang) * w
        A, B = (hx, h, ZW - 4), (hx + dx, h, ZW - 4 + dz)
        lv = (lambda s, t, P: 2.6 - (1.6 if s % 9 < 1 else 0) + (fbm(s / 4, t / 20, 2) - 0.5) * 0.8
              + (1.2 if abs(t - 20) < 2.5 or abs(t - h + 24) < 2.5 or abs(t - (20 + (h - 44) * s / w)) < 2.0 else 0))
        P = (A, B, (B[0], 0, B[2]), (A[0], 0, A[2])) if sgn < 0 else (B, A, (A[0], 0, A[2]), (B[0], 0, B[2]))
        e.quad('portal_fulla', *P, ramp=WOOD, lvl=lv, dues_cares=True)


def llavors(e, tex):
    """El banc de llavors, contra la paret de l'esquerra: dos trams del dibuix pla (el del fons, amb el rètol)."""
    gx, z0, z1 = SHELF
    zm = (z0 + z1) / 2
    e.caixa('llavors', 0, gx, SHELF_H, SHELF_H + 4, z0, z1, WOOD, 3.0)
    for (za, zb), im in (((z0, zm), tex['llavors2']), ((zm, z1), tex['llavors'])):
        e.quad('llavors', (gx, SHELF_H, za), (gx, SHELF_H, zb), (gx, 0, zb), (gx, 0, za),
               tex=(im, (14, 30, 177, FY)))
    # el rètol, una post penjada de la biga damunt el banc, girada cap a la sala
    a = 0.55
    za, ya = 196, SHELF_H + 30
    dx, dz = math.sin(a) * 84, math.cos(a) * 84
    for k in (0.15, 0.85):
        e.cable('llavors', [(gx - 2 + dx * k, ya, za + dz * k), (gx - 2 + dx * k, HW - 12, za + dz * k)], IRONR, 2.0,
                gruix=0.6)
    e.quad('llavors', (gx - 2, ya, za), (gx - 2 + dx, ya, za + dz), (gx - 2 + dx, ya - 21, za + dz), (gx - 2, ya - 21, za),
           tex=(tex['retol'], (0, 0, 52, 13)), dues_cares=True)
    e.foscor('ombra_llavors', (gx, 0.5, z1), (gx + 40, 0.5, z1), (gx + 40, 0.5, z0), (gx, 0.5, z0),
             lambda s, t: 0.6 * max(0.0, 1 - s / 40))


def bales(e):
    def palla(s, t, P):
        return 3.4 + (fbm(s / 2.5, t / 1.6, 5) - 0.5) * 1.8 - (1.4 if abs(s % 20 - 10) < 0.8 else 0)
    for x0, x1, z0, z1, y0, y1 in BALES:
        e.caixa('bales', x0, x1, y0, y1, z0, z1, STRAW, 3.2,
                cares={'davant': {'ramp': STRAW, 'lvl': palla},
                       'dalt': {'ramp': STRAW, 'lvl': lambda s, t, P: 4.4 + (fbm(s / 2, t / 2, 9) - 0.5) * 1.6},
                       'dreta': {'ramp': STRAW, 'lvl': lambda s, t, P: palla(s, t, P) - 1.0}})


def banc(e, tex):
    x0, x1, z0, z1, h = BANC
    e.foscor('ombra_banc', (x0 - 20, 0.5, z1), (x1, 0.5, z1), (x1, 0.5, z0 - 10), (x0 - 20, 0.5, z0 - 10),
             lambda s, t: 0.55 * min(1.0, s / 20))
    for lx, lz in ((x0 + 3, z0 + 3), (x0 + 3, z1 - 3)):
        e.caixa('banc', lx - 2.5, lx + 2.5, 0, h - 4, lz - 2.5, lz + 2.5, WOOD, 2.8)
    e.caixa('banc', x0, x1, h - 4, h, z0, z1, WOOD, 3.6, cares={'dalt': {'ramp': WOOD, 'lvl': 4.4}})
    # la caixa d'eines, damunt: el davant amb el dibuix pla
    cx, cz = 610, 262
    e.caixa('caixa_eines', cx - 19, cx + 19, h, h + 15, cz - 8, cz + 8, TRED, 3.4,
            cares={'davant': {'tex': (tex['caixa'], (588, 162, 627, 178))},
                   'dalt': {'ramp': TRED, 'lvl': lambda s, t, P: 4.6 - (1.4 if abs(t - 8) < 0.8 else 0)},
                   'esquerra': {'ramp': TRED, 'lvl': 2.6}})
    e.cable('caixa_eines', [(cx - 8, h + 15, cz), (cx - 6, h + 21, cz), (cx + 6, h + 21, cz), (cx + 8, h + 15, cz)],
            IRONR, 3.6, gruix=1.0)


def roda(e, sid, lx, lz, r, amp, tex_pla, fx, fy, cara=True):
    """Una roda del tractor: el pneumàtic (un cilindre de facetes) i, si `cara`, la cara de fora (el dibuix pla)."""
    n = 28
    for i in range(n):
        a0, a1 = 2 * math.pi * i / n, 2 * math.pi * (i + 1) / n
        p0 = (lx + r * math.cos(a0), r + r * math.sin(a0))
        p1 = (lx + r * math.cos(a1), r + r * math.sin(a1))
        lug = i % 2
        e.quad(sid, _T(p0[0], p0[1], lz - amp), _T(p1[0], p1[1], lz - amp), _T(p1[0], p1[1], lz),
               _T(p0[0], p0[1], lz), ramp=PL.TYRE, lvl=1.8 + lug * 1.0 - math.sin(a0) * 0.8)
    if cara is None:                                # (la cara de dins d'una roda de l'altra banda: fosca)
        e.quad(sid, _T(lx - r, 2 * r, lz - amp), _T(lx + r, 2 * r, lz - amp), _T(lx + r, 0, lz - amp),
               _T(lx - r, 0, lz - amp), ramp=PL.TYRE, lvl=lambda s, t, P: 1.0 + (0.8 if abs(math.hypot(s - r, t - r) - r * 0.6) < 2 else 0),
               forma=lambda s, t: (s - r) ** 2 + (t - r) ** 2 <= r * r)
    elif cara:
        e.quad(sid, _T(lx - r, 2 * r, lz - amp), _T(lx + r, 2 * r, lz - amp), _T(lx + r, 0, lz - amp),
               _T(lx - r, 0, lz - amp), tex=(tex_pla, (fx - r, fy - r, fx + r, fy + r)),
               forma=lambda s, t: (s - r) ** 2 + (t - r) ** 2 <= r * r)


def tractor(e, tex, obert=False):
    """El Brau 40 en 3/4: el morro (la graella i els fars) i el capó vist des de dalt són volums; el costat és el
    dibuix pla de perfil, retallat, al pla del costat; les rodes, cilindres."""
    img = _tractor_obert() if obert else tex['tractor']
    rx, ry, rr = PL.RW
    fx, fy, fr = PL.FW
    G = PL.TR_GROUND
    X0 = 470                                        # (al pla, el centre del tractor)
    b = TRAC_B
    hx0, hx1, ht, hb = fx - 22 - X0, rx - 34 - X0, G - 150, G - 192
    # l'ombra a terra: cap endavant i a la dreta (la llum ve del portal)
    pts = [_T(-110, 0.4, 70), _T(110, 0.4, 70), _T(110, 0.4, -60), _T(-110, 0.4, -60)]
    e.foscor('ombra_tractor', *pts, lambda s, t: 0.62 * max(0.0, 1 - ((s - 110) / 112) ** 2 - ((t - 60) / 66) ** 2) * 1.8)
    # les rodes de l'altra banda (es veuen per sota i per darrere)
    roda(e, 'tractor', rx - X0, b + 30, rr, 16, img, rx, ry, cara=None)
    roda(e, 'tractor', fx - X0, b + 14, fr, 8, img, fx, fy, cara=None)
    # el xassís i el motor, foscos, per sota
    e.caixa_girada('tractor', *_T(-10, 0, 0)[::2], 150, 2 * b - 8, 14, TRAC[2], PL.ENG, 1.8, y0=G - 204)
    # el capó: la tapa (vista des de dalt) i el morro amb la graella i els fars
    def tapa(s, t, P):
        v = 4.2 + (fbm(s / 10, t / 10, 12) - 0.5) * 0.7 - (1.4 if abs(s - 34) < 0.8 else 0)
        return v
    if not obert:
        e.quad('tractor', _T(hx0 + 4, ht, b), _T(hx1, ht, b), _T(hx1, ht, -b), _T(hx0 + 4, ht, -b),
               ramp=TRED, lvl=tapa)

    def graella(s, t, P):
        if (s - 7) ** 2 + (t - 12) ** 2 < 16 or (s - 2 * b + 7) ** 2 + (t - 12) ** 2 < 16:
            return 7.0                                                 # els fars
        if 5 < s < 2 * b - 5 and 18 < t < ht - hb - 3:
            return 1.4 + (1.6 if t % 3 < 1.2 else 0)                   # la graella
        return 3.4 + (fbm(s / 6, t / 6, 77) - 0.5) * 0.8
    e.quad('tractor', _T(hx0, ht - 4, b), _T(hx0, ht - 4, -b), _T(hx0, hb + 2, -b), _T(hx0, hb + 2, b),
           ramp=TRED, lvl=graella)
    e.quad('tractor', _T(hx0, ht - 4, b), _T(hx0, ht - 4, -b), _T(hx0 + 4, ht, -b), _T(hx0 + 4, ht, b),
           ramp=TRED, lvl=4.6, dues_cares=True)
    # el tauler i el seient, amb volum (darrere el capó)
    e.caixa_girada('tractor', *_T(hx1 + 6, 0, 0)[::2], 12, 2 * b, 10, TRAC[2], TRED, 3.2, y0=ht - 2)
    # el pneumàtic de les rodes d'aquesta banda (la cara, al dibuix pla)
    roda(e, 'tractor', fx - X0, -b + 2, fr, 8, img, fx, fy, cara=False)
    roda(e, 'tractor', rx - X0, -b + 6, rr, 14, img, rx, ry, cara=False)
    # el costat: el dibuix pla de perfil, retallat (el que és transparent no es pinta)
    x0, x1, y0, y1 = 376, 572, 100, G + 1
    e.quad('tractor', _T(x0 - X0, G - y0, -b), _T(x1 - X0, G - y0, -b), _T(x1 - X0, G - y1, -b), _T(x0 - X0, G - y1, -b),
           tex=(img, (x0, y0, x1, y1)))
    # les cares de les rodes, que sobresurten del costat
    roda(e, 'tractor', rx - X0, -b + 6 - 14, rr, 0.01, img, rx, ry)
    roda(e, 'tractor', fx - X0, -b + 2 - 8, fr, 0.01, img, fx, fy)


TRAC_CAIXA = ((-90, 92), (0, 118), (-34, 64))      # el tractor, en el seu sistema (_T): lx, y, lz (per a la profunditat)


def _prof_tractor(u, v):
    """La profunditat (la z de la càmera) on el raig del píxel de sala (u, v) entra a la caixa del tractor, o None."""
    cam = CAM
    x, y = (u - cam.centre[0]) / cam.f, -(v - cam.centre[1]) / cam.f    # la direcció, a l'espai de la càmera (z = 1)
    z1 = y * cam._sp + cam._cp
    d = (x * cam._cy + z1 * cam._sy, y * cam._cp - cam._sp, -x * cam._sy + z1 * cam._cy)
    cx, cz, a = TRAC
    c, s_ = math.cos(a), math.sin(a)
    ox, oz = cam.pos[0] - cx, cam.pos[2] - cz
    o = (ox * c + oz * s_, cam.pos[1], -ox * s_ + oz * c)              # al sistema del tractor
    dl = (d[0] * c + d[2] * s_, d[1], -d[0] * s_ + d[2] * c)
    t0, t1 = 0.0, 1e9
    for k, (lo, hi) in enumerate(TRAC_CAIXA):
        if abs(dl[k]) < 1e-9:
            if not lo <= o[k] <= hi:
                return None
            continue
        ta, tb = (lo - o[k]) / dl[k], (hi - o[k]) / dl[k]
        t0, t1 = max(t0, min(ta, tb)), min(t1, max(ta, tb))
    return t0 if t0 <= t1 else None                                    # (amb z = 1 a la direcció, t és la profunditat)


def feixos(e, mapa):
    """Els feixos de sol que baixen per les escletxes del sostre: es barregen amb el que hi ha (amb dither) i deixen la
    densitat a `mapa` (per a la pols). On hi ha el tractor, el tros de feix que en queda darrere no es pinta (el
    tractor el tapa), ni la taca de sol a terra."""
    S = e.S
    w, h = e.cv.w, e.cv.h
    acc = [0.0] * (w * h)
    trac = {i for i, sid in enumerate(e.ids) if sid == 'tractor'}
    prof = {}

    def tapat(X, Y, z):
        if e.amo[Y * w + X] not in trac:
            return False
        if (X, Y) not in prof:
            prof[X, Y] = _prof_tractor((X + 0.5) / S, (Y + 0.5) / S)
        p = prof[X, Y]
        return p is not None and z > p
    for A, B, ra, rb in FEIXOS:
        n = 160
        for i in range(n + 1):
            t = i / n
            P = (A[0] + (B[0] - A[0]) * t, A[1] + (B[1] - A[1]) * t, A[2] + (B[2] - A[2]) * t)
            u, v, zp = e.cam.projecta(P)
            R = (ra + (rb - ra) * t) * e.cam.escala(P)
            for Y in range(int((v - R) * S), int((v + R) * S) + 2):
                for X in range(int((u - R) * S), int((u + R) * S) + 2):
                    if 0 <= X < w and 0 <= Y < min(h, BOTTOM * S):
                        d = math.hypot(X / S - u, Y / S - v) / max(0.5, R)
                        if d < 1 and not tapat(X, Y, zp):
                            k = (1 - d * d) * (0.55 + 0.45 * t) * (1 - max(0.0, t - 0.93) / 0.07)
                            acc[Y * w + X] = max(acc[Y * w + X], k)
    P_ = e.cv.P
    for Y in range(min(h, BOTTOM * S)):
        for X in range(w):
            k = acc[Y * w + X]
            if k <= 0:
                continue
            mapa[Y * w + X] = k
            kk = 0.32 * k
            if kk > B4[Y & 3][X & 3] * 0.25:
                P_[X, Y] = mix(P_[X, Y], SUN, kk + 0.05) + (255,)
    # les taques a terra (el terra que el tractor tapa no es veu: es torna a posar el tractor)
    P_ = e.cv.P
    desa = {(X, Y): P_[X, Y] for Y in range(h) for X in range(w) if e.amo[Y * w + X] in trac}
    for A, B, ra, rb in FEIXOS:
        r = rb * 1.6
        e.claror((B[0] - r, 0.6, B[2] + r), (B[0] + r, 0.6, B[2] + r), (B[0] + r, 0.6, B[2] - r), (B[0] - r, 0.6, B[2] - r),
                 SUN, lambda s, t, r=r: 0.4 * max(0.0, 1 - ((s - r) / r) ** 2 - ((t - r) / r / 0.8) ** 2) * 1.6)
    for (X, Y), col in desa.items():
        P_[X, Y] = col


def primer_pla(e):
    x0, x1, z0, z1 = PILAR
    e.caixa('primer_pla', x0, x1, 0, HW, z0, z1, WOOD, 1.0,
            cares={'davant': {'ramp': WOOD, 'lvl': lambda s, t, P: 1.0 + (fbm(s / 3, t / 40, 6) - 0.5) * 0.8
                              + (0.8 if s > x1 - x0 - 3 else 0)},
                   'esquerra': {'ramp': WOOD, 'lvl': lambda s, t, P: 1.6 + (fbm(s / 3, t / 40, 7) - 0.5) * 0.8}})
    # la biga del davant, de banda a banda, i el tornapuntes del pilar
    e.caixa('primer_pla', -200, XR + 200, HW - 20, HW - 6, z0 + 2, z1 - 2, WOOD, 1.2,
            cares={'sota': {'ramp': WOOD, 'lvl': 0.6}, 'davant': {'ramp': WOOD, 'lvl': 1.2}})
    for k in range(8):
        t0, t1 = k / 8, (k + 1) / 8
        A = (x0 - 70 * t0, HW - 70 + 56 * t0, (z0 + z1) / 2)
        B = (x0 - 70 * t1, HW - 70 + 56 * t1, (z0 + z1) / 2)
        e.caixa('primer_pla', min(A[0], B[0]) - 4, max(A[0], B[0]) + 4, min(A[1], B[1]) - 4, max(A[1], B[1]) + 4,
                z0 + 5, z1 - 5, WOOD, 1.2)


def escena(cv, tex, obert=False, mapa=None):
    """Tota la sala, de lluny a prop. → l'Escena (qui ha pintat què)."""
    e = Escena(cv, CAM, LLUMS, ambient=AMBIENT)
    zn = CAM.pos[2] + 60
    exterior(e)
    # el sostre: les taules, i les bigues que fugen cap al fons
    e.quad('sostre', (-200, HW, zn), (XR + 200, HW, zn), (XR + 200, HW, ZW), (-200, HW, ZW), ramp=WOOD,
           lvl=_taulons(1.4, 3, ample=11), dues_cares=True)
    for A, B, ra, rb in FEIXOS:                                     # els forats, per on entra el sol
        e.quad('sostre', (A[0] - 4, HW - 0.5, A[2] + 3), (A[0] + 4, HW - 0.5, A[2] + 3), (A[0] + 4, HW - 0.5, A[2] - 3),
               (A[0] - 4, HW - 0.5, A[2] - 3), ramp=SKY, lvl=7.0, dues_cares=True)
    # la paret del fons (el portal: un forat a la textura) i la de l'esquerra, de taulons
    x0, x1, h = DOOR
    e.quad('paret_fons', (0, HW, ZW), (W - OFF, HW, ZW), (W - OFF, 0, ZW), (0, 0, ZW),
           tex=(tex['fons'], (OFF, FY - HW, W, FY)),
           forma=lambda s, t: not (x0 <= s <= x1 and t >= HW - h))
    e.quad('paret_fons', (W - OFF, HW, ZW), (XR, HW, ZW), (XR, 0, ZW), (W - OFF, 0, ZW),
           tex=(tex['dreta'], (0, FY - HW, XR - W + OFF, FY)))
    e.quad('paret_esq', (0, HW, zn), (0, HW, ZW), (0, 0, ZW), (0, 0, zn),
           tex=(tex['dreta'], (0, FY - HW, 400, FY)))
    e.quad('paret_dreta', (XR, HW, ZW), (XR, HW, zn), (XR, 0, zn), (XR, 0, ZW),
           tex=(tex['dreta'], (W, FY - HW, W - (ZW - zn) * 0.8, FY)))
    for z in range(int(zn) + 40, ZW, 70):                          # les bigues del sostre, que fugen cap al fons
        e.caixa('sostre', -10, XR + 10, HW - 12, HW, z, z + 9, WOOD, 2.0,
                cares={'sota': {'ramp': WOOD, 'lvl': 1.4}, 'davant': {'ramp': WOOD, 'lvl': 2.4}})
    for x in (150, 330, 510):
        e.caixa('sostre', x - 5, x + 5, HW - 22, HW - 12, zn, ZW, WOOD, 2.0,
                cares={'sota': {'ramp': WOOD, 'lvl': 1.2}, 'esquerra': {'ramp': WOOD, 'lvl': 2.2},
                       'dreta': {'ramp': WOOD, 'lvl': 1.6}})
    # el terra
    e.quad('terra', (-200, 0, ZW), (XR + 200, 0, ZW), (XR + 200, 0, zn), (-200, 0, zn), ramp=DIRT, lvl=_palla)
    # la foscor dels racons
    e.foscor('racons', (0, 0.5, ZW), (XR, 0.5, ZW), (XR, 0.5, zn), (0, 0.5, zn),
             lambda s, t: max(0.55 * max(0.0, 1 - t / 30), 0.6 * max(0.0, 1 - (XR - s) / 60),
                              0.45 * max(0.0, 1 - (t - (ZW - zn) + 160) / 160) if t > ZW - zn - 160 else 0))
    e.foscor('cantonada', (XR - 50, HW, ZW - 0.5), (XR, HW, ZW - 0.5), (XR, 0, ZW - 0.5), (XR - 50, 0, ZW - 0.5),
             lambda s, t: 0.5 * max(0.0, s / 50))
    # la llum del portal: entra i s'estira pel terra, cap endavant i a la dreta
    e.claror((x0, 0.4, ZW), (x1, 0.4, ZW), (x1 + 210, 0.4, ZW - 300), (x0 + 120, 0.4, ZW - 300), SUN,
             lambda s, t: 0.62 * max(0.0, 1 - t / 300) ** 1.1 * min(1.0, s / 10, (x1 - x0 - s + 4) / 10 + 0.4 * t / 300))
    portal(e)
    llavors(e, tex)
    bales(e)
    banc(e, tex)
    tractor(e, tex, obert)
    feixos(e, mapa if mapa is not None else [0.0] * (cv.w * cv.h))
    primer_pla(e)
    return e


# ─── Composició ────────────────────────────────────────────────────────────

_MAPA = []


@functools.lru_cache(maxsize=None)
def _base():
    cv = Canvas(light=LIGHT)
    mapa = [0.0] * (cv.w * cv.h)
    e = escena(cv, _textures(), mapa=mapa)
    _MAPA.append(mapa)
    cv.rect(0, BOTTOM + 1, W - 1, cv.h - 1, [(0, 0, 0)], 0, lit=0)    # la barra de verbs: negre
    return cv.img, e


def bg(cv):
    img, _ = _base()
    cv.img.paste(img)
    cv.P = cv.img.load()


# ─── Props ──────────────────────────────────────────────────────────────────

def _flat(fn):
    cv = Canvas(light=FLAT, transparent=True)
    fn(cv)
    return cv.img


def reg(cv):
    """El reg gota a gota, penjat del clau de la paret del fons (el dibuix pla, projectat)."""
    _, e = _base()
    cv.img.alpha_composite(e.capa(_flat(lambda c: PL.reg(c)), {'paret_fons'}))


def tractor_obert(cv):
    """El capó aixecat: la sala tornada a dibuixar amb el capó obert, i només el que canvia."""
    base, _ = _base()
    c2 = Canvas(light=LIGHT)
    escena(c2, _textures(), obert=True)
    c2.rect(0, BOTTOM + 1, W - 1, c2.h - 1, [(0, 0, 0)], 0, lit=0)
    cv.img.alpha_composite(_diff(c2.img, base))


def _sacs(sacs):
    """Sacs drets a terra (dibuixats plans, posats a escala on toquen); els tapa el que tenen davant."""
    def fn(cv):
        _, e = _base()
        for k, (x, z, w, h) in enumerate(sacs):
            sc = Canvas(light=FLAT, transparent=True)
            PL._sack(sc, 40, 60, w, h, k + 3, lvl=3.6)
            img = sc.img.crop((0, 0, 80, 64))
            P = (x, 0, z)
            kk = CAM.escala(P)
            u, v, _ = CAM.projecta(P)
            ww, hh = max(1, round(80 * kk)), max(1, round(64 * kk))
            from pixels import nearest
            im = nearest(img, (ww, hh)) if kk >= 1 else img.resize((ww, hh), Image.Resampling.BOX)
            ox, oy = round(u - 40 * kk), round(v - 60 * kk)
            # l'ombra, cap endavant i a la dreta
            sh = Image.new('RGBA', cv.img.size, (0, 0, 0, 0))
            sp = sh.load()
            for Y in range(round(v - 3 * kk), round(v + 4 * kk)):
                for X in range(round(u - w * 0.6 * kk), round(u + w * 0.9 * kk)):
                    dx, dy = (X - u - w * 0.15 * kk) / (w * 0.75 * kk), (Y - v - 0.5 * kk) / (3.5 * kk)
                    if dx * dx + dy * dy < 1 and 0 <= X < cv.img.width and 0 <= Y < BOTTOM:
                        sp[X, Y] = (16, 10, 6, 130)
            cv.img.alpha_composite(sh)
            src, dst = im.load(), cv.img.load()
            for yy in range(hh):
                for xx in range(ww):
                    c = src[xx, yy]
                    X, Y = ox + xx, oy + yy
                    if c[3] >= 128 and 0 <= X < cv.img.width and 0 <= Y < BOTTOM:
                        if e.ids[e.amo[Y * e.cv.w + X]] in ('primer_pla', 'portal_fulla'):
                            continue
                        dst[X, Y] = c
    return fn


PROPS = {
    'reg': reg,
    'tractor_obert': tractor_obert,
    'sacs_tres': _sacs([(64, 150, 26, 30), (58, 118, 28, 33), (70, 88, 26, 29)]),
    'sac_quart': _sacs([(112, 192, 26, 30)]),
}


# ─── Animacions ─────────────────────────────────────────────────────────────

def _frames_pols():
    base, e = _base()
    mapa = _MAPA[0]
    w = e.cv.w
    porta = _porta_terra()

    def where(x, y):
        x, y = int(x), int(y)
        if not (0 <= x < w and 0 <= y < BOTTOM):
            return 0.0
        return max(mapa[y * w + x], 0.5 if porta(x, y) else 0.0)
    return motes_frames(base, where, n=48, count=80, seed=5)


def _porta_terra():
    """La pols que aixeca la llum del portal: un tros d'aire baix damunt la llum del terra (en pantalla)."""
    x0, x1, _ = DOOR
    q = [CAM.projecta(P)[:2] for P in ((x0, 30, ZW - 10), (x1, 30, ZW - 10), (x1 + 120, 10, ZW - 170),
                                       (x0 + 70, 10, ZW - 170))]

    def dins(x, y):
        sg = None
        for (ax, ay), (bx, by) in zip(q, q[1:] + q[:1]):
            c = (bx - ax) * (y - ay) - (by - ay) * (x - ax)
            if c != 0:
                if sg is None:
                    sg = c > 0
                elif (c > 0) != sg:
                    return False
        return True
    return dins


ANIMS = {'pols': {'frames': _frames_pols, 'frameDuration': 140}}


# ─── Capes del davant ──────────────────────────────────────────────────────

def _amo(ids):
    def mask(x, y):
        _, e = _base()
        return e.ids[e.amo[y * e.cv.w + x]] in ids
    return mask


def _p(x, z, y=0.0):
    u, v, _ = CAM.projecta((x, y, z))
    return round(u), round(v)


FRONT = [
    # el tractor: qui hi passa per darrere (entre el tractor i la paret del fons) en queda tapat
    # (el capó obert, un decorat, va a la mateixa capa: si no, la capa, retallada del fons amb el capó tancat, el taparia)
    {'id': 'davant_tractor', 'mask': _amo({'tractor'}), 'baseline': _p(TRAC[0], TRAC[1])[1], 'zIndex': 20,
     'props': ('tractor_obert',)},
    {'id': 'davant', 'mask': _amo({'primer_pla'}), 'baseline': 999, 'zIndex': 20},
]


# ─── Geometria (coordenades de sala, projectades) ────────────────────────────

def _rect_mon(*Ps):
    pts = [CAM.projecta(P) for P in Ps]
    return (max(0, round(min(p[0] for p in pts))), max(0, round(min(p[1] for p in pts))),
            min(W - 1, round(max(p[0] for p in pts))), min(BOTTOM, round(max(p[1] for p in pts))))


# El terra on es camina (al món): davant el banc de llavors, fins al llindar del portal, al voltant de les bales i del
# banc de treball, i per darrere del tractor (que és un forat).
WALK_MON = [(44, 40), (520, 40), (590, 120), (578, 214), (580, 222), (520, 316), (232, 316), (232, 284),
            (160, 284), (150, 326), (44, 326)]
_WALK = [_p(x, z) for x, z in WALK_MON]
_V_FONS, _V_PROP = min(v for _, v in _WALK), max(v for _, v in _WALK)
_TRAC_FORAT = [_p(*_T(lx, 0, lz)[::2]) for lx, lz in ((-96, -34), (96, -40), (100, 46), (-92, 34))]


def _escala_a(v):
    """L'escala d'un personatge amb els peus a la y de pantalla `v` (al terra, la profunditat només depèn de v)."""
    lo, hi = -200.0, 3000.0
    for _ in range(60):
        z = (lo + hi) / 2
        if CAM.projecta((300, 0, z))[1] > v:
            lo = z
        else:
            hi = z
    return CAM.escala((300, 0, (lo + hi) / 2))


_REG = ((306 - OFF, FY - 94), (358 - OFF, FY - 148))

GEOMETRIA = {
    'things': {
        'porta': {'rect': _rect_mon((DOOR[0] - 7, DOOR[2] + 7, ZW), (DOOR[1] + 7, 0, ZW)),
                  'walk': _p(DOOR_C[0], ZW - 12)},
        'tractor': {'rect': _rect_mon(*[_T(lx, y, lz) for lx in (-100, 104) for y in (0, 120) for lz in (-40, 40)]),
                    'walk': _p(*_T(-10, 0, -78)[::2])},
        'llavors': {'rect': _rect_mon((SHELF[0], SHELF_H + 4, SHELF[1] + 40), (SHELF[0], 0, SHELF[2])),
                    'walk': _p(70, 160)},
        'reg': {'rect': _rect_mon((_REG[0][0], _REG[0][1], ZW), (_REG[1][0], _REG[1][1], ZW)),
                'walk': _p(176, 270)},
        'caixa_eines': {'rect': _rect_mon((588, BANC[4] + 26, 252), (632, BANC[4], 272)),
                        'walk': _p(560, 236)},
    },
    'spawns': {'iri': _p(180, 140), 'vet': _p(290, 110)},
    'walkable': _WALK,
    'forats': [_TRAC_FORAT],
    # (la càmera, a 1,65 m, poc picada: a ≈430 de fons on es camina, 165 / 430)
    'floorSquash': 0.38,
    # L'ombra de contacte: la llum dominant és el portal (el punt del terra al llindar); l'ombra cau cap endavant i
    # cap a la dreta.
    'characterShadow': {'enabled': True, 'color': '#1a1008', 'alpha': 0.4, 'squash': 0.38, 'core': 0.6,
                        'light': {'x': _p(DOOR_C[0], ZW)[0], 'y': _p(DOOR_C[0], ZW)[1], 'stretch': 0.8,
                                  'reach': 160}},
    'regions': [{'id': 'perspectiva', 'active': True, 'scaleEnabled': True, 'scaleWalkSpeed': True,
                 'scaleTop': round(_escala_a(_V_FONS - 2), 3), 'scaleBottom': round(_escala_a(_V_PROP + 2), 3),
                 'points': [(0, _V_FONS - 2), (W - 1, _V_FONS - 2), (W - 1, _V_PROP + 2), (0, _V_PROP + 2)]}],
    # La llum de la sala sobre els personatges (characterLights del motor): el graner fosc: el sol del portal i la
    # claror de les escletxes.
    'characterLights': {
        'ambient': '#76685a',
        'lights': [
            llum_personatges(CAM, LLUMS[0].pos, LLUMS[0].r, '#ffdca0', 0.7),  # el sol del portal
            llum_personatges(CAM, LLUMS[1].pos, LLUMS[1].r, '#ffd090', 0.3),  # el portal, pel terra
            llum_personatges(CAM, LLUMS[2].pos, LLUMS[2].r, '#ffe0b0', 0.2),  # les escletxes del sostre
        ],
    },
}
