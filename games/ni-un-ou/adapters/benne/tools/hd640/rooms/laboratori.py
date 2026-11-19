"""
El laboratori de l'Arenga. EN 3D (hd640/tres_d.py), a 1×.

Una càmera alta que mira de biaix la cantonada del fons a l'esquerra, amb el sostre baix d'un vaixell:
  - a la paret de l'esquerra, en escorç, la **porta estanca** oberta al passadís (el camí cap al fons), l'**ull de
    bou** i la bata i l'armilla penjades;
  - a la paret del fons, la **carta dels punts de mostreig**, el prestatge de pots i la pica del racó (amb el moble);
  - el **taulell** separat de la paret i una mica girat, amb volum: la lupa binocular, la gradeta, el llibre de
    peixos, el portàtil i la nota a sobre (s'hi passa per darrere);
  - la **nevera de mostres**, girada, amb les tres cares;
  - primer pla: la safata de cables i les canonades del sostre que vénen cap a la càmera, una columna a la dreta i
    uns bidons en silueta a baix a l'esquerra.

Tot el detall ve del dibuix pla de sempre (laboratori_pla_comu.py), projectat; els decorats (el portàtil, la nota,
el laboratori remenat, l'ull de bou de dia) es dibuixen en 3D i en surt la diferència.

El món: x a la dreta (0 = la paret de la porta), y amunt (0 = el terra), z cap al fons (300 = la paret del fons);
1 unitat = 1 píxel de sala a la distància on un personatge fa ≈110 px (escala 1).
"""
import functools
import math

import hd640  # noqa: F401  (abans de cap hd.rooms: posa la llibreria a 640×360)
from PIL import Image

from hd.pix import Canvas, Light, W, H, hr, mix
from hd.rooms.arenga import hpipe, CAB, DARK, WHITEP, REDP, YELL, BRASS
from hd.rooms.comu import _diff
from hd.rooms.exterior import fbm
from hd.rooms.principal import CREAM, TEAK, LINO, day_porthole
from hd.rooms.laboratori import SOCOL, EPOXY, GLASSB, PAPERC, BLUEB
from hd640.rooms import laboratori_pla_comu as PL
from hd640.tres_d import Camera, Escena, Llum

BOTTOM = 259                                       # la sala acaba aquí (a sota, la barra de verbs)
ZW = 300                                           # la paret del fons
FY = PL.FLOOR_Y                                    # al dibuix pla, el terra (203)
HW = FY - PL.CEIL_H                                # l'alçada de les parets: del terra al sostre del dibuix pla (179)
XL = 150                                           # al dibuix pla, la cantonada: a l'esquerra, la paret de la porta
XR = 640                                           # la paret de la dreta
ZN = -260                                          # on s'acaben, cap a la càmera, el terra i les parets
BENCH = (215, 190, 320, 48, 62, 0.06)              # el taulell: x, z del centre, ample, fons, alçada, gir
FRIDGE = (395, 262, 104, 52, 142, -0.18)           # la nevera: x, z del centre, ample, fons, alçada, gir
SINK = (445, 489, 266, 60)                         # el moble de la pica: x0, x1, z del davant, alçada
LAMPS = ((150, 214), (392, 120))                   # els llums del sostre (x, z)


def _w(fx):
    """Una x del dibuix pla de la paret del fons → la x del món."""
    return fx - XL


def _wz(fx):
    """Una x del dibuix pla de la paret de la porta → la z del món."""
    return ZW - XL + fx


def _y(fy):
    """Una y del dibuix pla (el terra, a 203) → l'alçada del món."""
    return FY - fy


DOOR = (_wz(19), _wz(75), _y(88))                  # la porta: z0, z1, alçada
PORT = (_wz(PL.PORT[0]), _y(PL.PORT[1]), PL.PORT[2])   # l'ull de bou: z, y del centre i radi

CAM = Camera(pos=(320, 160, -230), yaw=-0.22, pitch=0.2, f=400, centre=(330, 108))

LIGHT = Light(ambient=0.0, vignette=None, floor_fade=None)  # (la llum és la del món: la de l'Escena)
LLUMS = [Llum((x, HW - 10, z), 260, 1.7, power=1.4) for x, z in LAMPS] + [
    Llum((10, PORT[1], PORT[0]), 120, 0.5, power=1.6)]          # l'ull de bou (la nit, freda)


# ─── Les textures: el dibuix pla de sempre ───────────────────────────────────

def _paret(dia=False, vidre=None):
    """Les dues parets planes, de cara: la porta, l'ull de bou, la bata, la carta, el prestatge i la pica.
    `vidre` = t (0..1): el mar que es mou a l'ull de bou (un fotograma)."""
    cv = Canvas(light=PL.LIGHT)
    PL.wall(cv)
    hpipe(cv, 0, W - 1, 36, 3, BLUEB, 3.4, bands=range(53, W, 85), band_ramp=WHITEP)   # aigua dolça
    for x in range(20, W, 85):
        cv.rect(x, 31, x + 2, 41, CAB, 3.0)
    PL.watertight_door(cv)
    PL.porthole(cv)
    PL.lab_coat(cv)
    PL.sample_chart(cv)
    PL.shelf(cv)
    PL.sink(cv)
    if dia:
        day_porthole(cv, *PL.PORT)
    if vidre is not None:
        PL._glass(cv, vidre, dia)
    return cv.img


@functools.lru_cache(maxsize=None)
def _paret_base(dia=False):
    return _paret(dia)


@functools.lru_cache(maxsize=None)
def _paret_nua():
    """La paret sense res (per a on el dibuix pla no arriba)."""
    cv = Canvas(light=PL.LIGHT)
    PL.wall(cv)
    hpipe(cv, 0, W - 1, 36, 3, BLUEB, 3.4, bands=range(53, W, 85), band_ramp=WHITEP)
    for x in range(20, W, 85):
        cv.rect(x, 31, x + 2, 41, CAB, 3.0)
    return cv.img


@functools.lru_cache(maxsize=None)
def _mobles():
    """El taulell, la nevera, la pica, la lupa i la gradeta, dibuixats plans sobre transparent (en surten els
    retalls)."""
    cv = Canvas(light=PL.LIGHT, transparent=True)
    PL.bench(cv)
    PL.magnifier(cv)
    PL.jar_rack(cv)
    PL.fridge(cv)
    PL.sink(cv)
    return cv.img


def _mobles_nevera(temp='4', pilot=False):
    """La nevera amb el visor i el pilot d'un fotograma (per a l'animació)."""
    cv = Canvas(light=PL.LIGHT, img=_mobles().copy())
    x0, y0 = PL.FRIDGE[:2]
    PL._display(cv, temp)
    if pilot:
        cv.flat(x0 + 8, y0 + 8, (210, 255, 220))
        PL.glow(cv, x0 + 8, y0 + 8, 5, (90, 255, 120), 0.6)
    else:
        cv.flat(x0 + 8, y0 + 8, (40, 140, 70))
    return cv.img


def _portatil_pla(i=None):
    """El portàtil pla (la pantalla de la contrasenya); `i`: el fotograma (el cursor i el llum)."""
    cv = Canvas(light=PL.LIGHT, transparent=True)
    PL.laptop(cv)
    if i is not None:
        if i < 4:
            cv.rect(295, 132, 295, 133, [(30, 50, 80)], 0, lit=0)
        led = 0.5 + 0.5 * math.cos(i / 8 * 2 * math.pi)
        cv.flat(314, 148, mix((20, 60, 34), (90, 255, 120), led))
    return cv.img


@functools.lru_cache(maxsize=None)
def _nota_pla():
    cv = Canvas(light=PL.LIGHT, transparent=True)
    PL.note(cv)
    return cv.img


@functools.lru_cache(maxsize=None)
def _llum_pla():
    cv = Canvas(80, 40, light=PL.LIGHT, transparent=True)
    PL.lamp(cv, 40, 10)
    return cv.img


BENCH_BOX = (139, 151, 459, 213)                   # el davant del taulell, al dibuix pla
FRIDGE_BOX = PL.FRIDGE                             # la nevera
SINK_BOX = (595, 149, 639, 209)                    # el moble de la pica
MAG_BOX = (392, 92, 432, 149)                      # la lupa
RACK_BOX = (350, 122, 397, 149)                    # la gradeta
SCREEN_BOX = (267, 112, 314, 140)                  # la pantalla del portàtil
KEYS_BOX = (262, 141, 320, 150)                    # el teclat del portàtil
NOTE_BOX = (323, 133, 342, 150)


# ─── Les superfícies ────────────────────────────────────────────────────────

def _terra(s, t, P):
    """Linòleum vermell en coordenades del món: tires de 40 que fugen cap al fons, juntes de testa, gastat pel mig."""
    x, z = P[0], P[2]
    tira = math.floor(x / 40)
    v = 3.6 + (hr(tira, 3) - 0.5) * 0.5 + (fbm(x / 70, z / 40, 4) - 0.5) * 0.7
    v += (hr(int(x) // 4, int(z) // 4, 2) - 0.5) * 0.35
    if x % 40 < 1.0:
        return 2.0
    if int(z + hr(tira, 7) * 160) % 160 < 1.0:
        return 2.4
    v += max(0.0, 1 - abs(z - 120) / 110) * max(0.0, 1 - abs(x - 260) / 200) * 0.4
    return v


def _sostre(s, t, P):
    """El sostre de planxa: les bigues cada 96 (fugen cap al fons) i reblons."""
    x = P[0]
    if (x + 13) % 96 < 10:
        return 2.6 + (0.6 if (x + 13) % 96 < 2 else 0)
    return 1.8 + (fbm(x / 50, P[2] / 50, 3) - 0.5) * 0.6 - (0.5 if int(P[2]) % 14 == 0 and int(x) % 6 < 2 else 0)


FOSC = [(4, 3, 3), (9, 7, 6), (15, 12, 10), (22, 18, 15), (31, 26, 21), (42, 35, 28)]


def _bench_P(lx, y, lz):
    """Un punt del taulell: `lx` des de l'esquerra (en x del dibuix pla menys 139), `lz` des del davant."""
    cx, cz, w, d, h, a = BENCH
    c, s_ = math.cos(a), math.sin(a)
    X, Z = lx - w / 2, lz - d / 2
    return (cx + X * c - Z * s_, y, cz + X * s_ + Z * c)


def _bench_fx(fx):
    return fx - BENCH_BOX[0]


def _caixa_banc(e, sid, lx0, lx1, lz0, lz1, y0, y1, ramp, lvl, cares=None):
    """Una caixa damunt (o davant) del taulell, girada com ell."""
    cx, cz = (lx0 + lx1) / 2, (lz0 + lz1) / 2
    P = _bench_P(cx, 0, cz)
    e.caixa_girada(sid, P[0], P[2], lx1 - lx0, lz1 - lz0, y1 - y0, BENCH[5], ramp, lvl, y0=y0, cares=cares)


def escena(cv, tex, estat=frozenset()):
    """Tota la sala, de lluny a prop. `estat`: els decorats que hi són ('portatil', 'nota', 'remenat', 'dia').
    → l'Escena (qui ha pintat què)."""
    e = Escena(cv, CAM, LLUMS, ambient=-0.3)
    paret, nua, mob = tex['paret'], tex['nua'], tex['mobles']
    # el sostre, amb les bigues
    e.quad('sostre', (0, HW, ZN), (XR, HW, ZN), (XR, HW, ZW), (0, HW, ZW), ramp=CREAM, lvl=_sostre, dues_cares=True)
    # la paret de la porta (x = 0): de prop, la paret nua; cap a la cantonada, el dibuix pla (x 0..150)
    e.quad('paret_esq_prop', (0, HW, ZN), (0, HW, ZW - XL), (0, 0, ZW - XL), (0, 0, ZN),
           tex=(nua, (100, PL.CEIL_H, 100 + ZW - XL - ZN, FY)))
    e.quad('paret_esq', (0, HW, ZW - XL), (0, HW, ZW), (0, 0, ZW), (0, 0, ZW - XL), tex=(paret, (0, PL.CEIL_H, XL, FY)))
    # la paret del fons (z = 300): el dibuix pla (x 150..640) i, a la dreta, la paret nua
    e.quad('paret_fons', (0, HW, ZW), (W - XL, HW, ZW), (W - XL, 0, ZW), (0, 0, ZW), tex=(paret, (XL, PL.CEIL_H, W, FY)))
    e.quad('paret_fons_dreta', (W - XL, HW, ZW), (XR, HW, ZW), (XR, 0, ZW), (W - XL, 0, ZW),
           tex=(nua, (46, PL.CEIL_H, 46 + XR - (W - XL), FY)))
    # la paret de la dreta (x = XR)
    e.quad('paret_dreta', (XR, HW, ZW), (XR, HW, ZN), (XR, 0, ZN), (XR, 0, ZW), tex=(nua, (60, PL.CEIL_H, 60 + ZW - ZN, FY)))
    # el terra
    e.quad('terra', (0, 0, ZW), (XR, 0, ZW), (XR, 0, ZN), (0, 0, ZN), ramp=LINO, lvl=_terra)
    # els bassals de llum sota els llums, i el reflex de la porta del passadís
    for lx, lz in LAMPS:
        e.claror((lx - 120, 0.3, lz + 120), (lx + 120, 0.3, lz + 120), (lx + 120, 0.3, lz - 120), (lx - 120, 0.3, lz - 120),
                 (255, 214, 140), lambda s, t: 0.28 * max(0.0, 1 - math.hypot(s - 120, t - 120) / 120) ** 1.3)
    dz0, dz1, dh = DOOR
    e.claror((0, 0.4, dz1 + 10), (90, 0.4, dz1 + 50), (90, 0.4, dz0 - 40), (0, 0.4, dz0 - 4), (230, 200, 140),
             lambda s, t: 0.3 * max(0.0, 1 - s / 90) * max(0.0, math.sin(math.pi * min(1.0, t / max(1.0, 60 + 0.9 * s)))))
    if 'dia' in estat:
        # la claror del mar que entra per l'ull de bou, en diagonal pel terra (cap a la dreta i endavant)
        pz, py, pr = PORT
        e.claror((0, 0.5, pz + 40), (260, 0.5, pz - 40), (260, 0.5, pz - 150), (0, 0.5, pz - 70), (200, 220, 230),
                 lambda s, t: 0.35 * max(0.0, 1 - s / 260) * max(0.0, 1 - abs(t - 55) / 45))
    # la foscor dels racons
    e.foscor('racons', (0, 0.5, ZW), (XR, 0.5, ZW), (XR, 0.5, ZN), (0, 0.5, ZN),
             lambda s, t: max(0.6 * max(0.0, 1 - t / 26), 0.5 * max(0.0, 1 - s / 22), 0.5 * max(0.0, 1 - (XR - s) / 30)))
    e.foscor('cantonada', (0, HW, ZW - 0.5), (60, HW, ZW - 0.5), (60, 0, ZW - 0.5), (0, 0, ZW - 0.5),
             lambda s, t: 0.5 * max(0.0, 1 - s / 60))
    e.foscor('cantonada2', (0.5, HW, ZW - 60), (0.5, HW, ZW), (0.5, 0, ZW), (0.5, 0, ZW - 60),
             lambda s, t: 0.5 * max(0.0, 1 - (60 - s) / 60))
    e.foscor('sostre_fosc', (0, HW - 0.5, ZW - 0.6), (XR, HW - 0.5, ZW - 0.6), (XR, 0, ZW - 0.6), (0, 0, ZW - 0.6),
             lambda s, t: 0.4 * max(0.0, 1 - t / 40))
    # les quadernes de la paret de l'esquerra, de prop: costelles de planxa amb reblons, que fugen
    for z in (ZW - XL - 108 + 96 * k for k in range(-3, 1)):
        if z < ZN + 10:
            continue
        e.caixa('quadernes', 0, 7, 0, HW, z, z + 6, CREAM, 3.6,
                cares={'dreta': {'ramp': CREAM, 'lvl': lambda s, t, P: 4.2 - (1.2 if int(t) % 14 == 0 else 0)},
                       'davant': {'ramp': CREAM, 'lvl': 2.6}})
    # la canonada de l'aigua i la de contra incendis, al sostre, que vénen del fons cap a la càmera (a l'esquerra)
    e.tub('canonades', (16, HW - 8, ZW), (16, HW - 8, ZN + 40), 4, REDP, 3.4, brides=70)
    e.tub('canonades', (30, HW - 6, ZW), (30, HW - 6, ZN + 40), 2.5, WHITEP, 3.2, brides=90)
    # la canonada de la paret del fons, al sostre
    e.tub('canonades', (0, HW - 7, ZW - 6), (XR, HW - 7, ZW - 6), 4, REDP, 3.0, brides=120)
    # els cables pel terra: de la pica cap al taulell i un que travessa cap a la porta
    for ramp, lv, pts in (
            (CAB, 2.4, [(440, 0.8, 290), (420, 0.8, 250), (360, 0.8, 236), (330, 0.8, 200)]),
            (YELL, 2.6, [(60, 0.8, 182), (40, 0.8, 160), (10, 0.8, 150), (6, 0.8, 120)])):
        e.cable('cables', pts, ramp, lv, gruix=2.2)
    # el moble de la pica, contra la paret del fons
    sx0, sx1, sz, sh = SINK
    e.foscor('ombra_pica', (sx0 - 10, 0.6, ZW), (sx1 + 6, 0.6, ZW), (sx1 + 6, 0.6, sz - 16), (sx0 - 10, 0.6, sz - 16),
             lambda s, t: 0.55 * min(1.0, max(0.0, (ZW - sz + 16 - t) / 16)))
    e.caixa('pica', sx0, sx1, 0, sh - 6, sz, ZW, CREAM, 3.6,
            cares={'davant': {'tex': (mob, (SINK_BOX[0], SINK_BOX[1] + 6, SINK_BOX[2], SINK_BOX[3]))},
                   'esquerra': {'ramp': CREAM, 'lvl': 3.0}})
    e.caixa('pica', sx0 - 4, sx1, sh - 6, sh, sz - 4, ZW, WHITEP, 3.6,
            cares={'dalt': {'ramp': WHITEP, 'lvl': lambda s, t, P: 1.4 if 5 < s < 40 and 8 < t < 30 else 4.4},
                   'davant': {'ramp': WHITEP, 'lvl': 3.4}})
    # la nevera, girada: el davant (el dibuix pla) i els costats
    fx, fz, fw, fd, fh, fa = FRIDGE
    e.foscor('ombra_nevera', (fx - 80, 0.6, fz + 40), (fx + 70, 0.6, fz + 40), (fx + 70, 0.6, fz - 50),
             (fx - 80, 0.6, fz - 50), lambda s, t: 0.55 * max(0.0, 1 - ((s - 76) / 76) ** 2 - ((t - 42) / 46) ** 2) * 1.5)
    e.caixa_girada('nevera', fx, fz, fw, fd, fh, fa, WHITEP, 3.4,
                   cares={'davant': {'tex': (mob, FRIDGE_BOX)},
                          'esquerra': {'ramp': WHITEP, 'lvl': lambda s, t, P: 2.6 - (0.8 if t > fh - 8 else 0)
                                       - (0.6 if abs(s - fd / 2) < 0.6 else 0)},
                          'dalt': {'ramp': WHITEP, 'lvl': 4.6}})
    # el taulell, separat de la paret i girat: el davant (el dibuix pla), el costat i la tapa d'epoxi
    bx, bz, bw, bd, bh, ba = BENCH
    e.foscor('ombra_taulell', *[_bench_P(lx, 0.6, lz) for lx, lz in ((-14, bd + 18), (bw + 14, bd + 18), (bw + 14, -12),
                                                                      (-14, -12))],
             lambda s, t: 0.6 * min(1.0, min(s, t, bw + 28 - s, bd + 30 - t) / 14))
    e.caixa_girada('taulell', bx, bz, bw - 6, bd - 6, bh - 4, ba, SOCOL, 1.6,
                   cares={'davant': {'tex': (mob, (BENCH_BOX[0] + 3, BENCH_BOX[1] + 4, BENCH_BOX[2] - 3, BENCH_BOX[3]))},
                          'esquerra': {'ramp': CREAM, 'lvl': lambda s, t, P: 3.6 - (1.4 if t > bh - 10 else 0)
                                       - (0.8 if abs(s - (bd - 6) / 2) < 0.6 else 0)},
                          'dreta': {'ramp': CREAM, 'lvl': 2.8}})

    def epoxi(s, t, P):
        v = 3.2 + (fbm(s / 30, t / 12, 8) - 0.5) * 0.6 + (hr(int(s) // 3, int(t) // 3, 9) - 0.5) * 0.3
        if t < 1.5 or t > bd - 1.5 or s < 1.5 or s > bw - 1.5:
            v += 1.6
        return v
    _caixa_banc(e, 'taulell', 0, bw, -2, bd, bh - 4, bh, EPOXY, 4.2,
                cares={'dalt': {'ramp': EPOXY, 'lvl': epoxi}, 'davant': {'ramp': EPOXY, 'lvl': 4.8},
                       'esquerra': {'ramp': EPOXY, 'lvl': 3.6}, 'dreta': {'ramp': EPOXY, 'lvl': 3.2}})
    # l'ombra del taulell que fa el llum del fons: cap endavant i cap a l'esquerra, pel terra
    sh0, sh1 = _bench_P(0, 0.7, -1), _bench_P(bw, 0.7, -1)
    e.foscor('ombra_taulell2', sh0, sh1, (sh1[0] - 22, 0.7, sh1[2] - 46), (sh0[0] - 22, 0.7, sh0[2] - 46),
             lambda s, t: 0.42 * max(0.0, 1 - t / 50) * min(1.0, s / 20, (bw - s) / 20 + 0.3))
    # damunt del taulell: el llibre de peixos (amb els post-its), la lupa, la gradeta
    bfx = _bench_fx

    def tapa(s, t, P):
        v = 3.2 + t * 0.03
        if 12 < s < 24 and 8 < t < 14:
            v = 4.6 if (int(s) + int(t)) % 3 else 3.6                    # el peix
        return v - (1.4 if s < 2 else 0)
    _caixa_banc(e, 'llibre', bfx(187), bfx(235), 8, 34, bh, bh + 6, PAPERC, 3.6,
                cares={'dalt': {'ramp': BLUEB, 'lvl': tapa}, 'esquerra': {'ramp': BLUEB, 'lvl': 2.4}})
    for k, (fx_, col) in enumerate(((219, YELL), (224, REDP), (228, YELL))):
        _caixa_banc(e, 'llibre', bfx(fx_), bfx(fx_) + 3.5, 26, 27, bh + 6, bh + 11, col, 4.4)
    e.sprite('lupa', mob.crop(MAG_BOX), (408 - MAG_BOX[0], 148 - MAG_BOX[1]), _bench_P(bfx(408), bh, 26))
    e.sprite('gradeta', mob.crop(RACK_BOX), (373 - RACK_BOX[0], 148 - RACK_BOX[1]), _bench_P(bfx(373), bh, 22))
    # una pipeta i un retolador
    e.cable('taulell', [_bench_P(bfx(236), bh + 1, 14), _bench_P(bfx(254), bh + 1, 18)], WHITEP, 4.2, gruix=1.2)
    e.cable('taulell', [_bench_P(bfx(331), bh + 1, 12), _bench_P(bfx(344), bh + 1, 8)], BLUEB, 4.0, gruix=1.4)
    # el portàtil (decorat): la base al taulell i la pantalla una mica tirada enrere
    if 'portatil' in estat:
        pt = tex['portatil']
        l0, l1 = bfx(KEYS_BOX[0]), bfx(KEYS_BOX[2])
        e.quad('portatil', _bench_P(l0, bh + 0.6, 26), _bench_P(l1, bh + 0.6, 26), _bench_P(l1, bh + 0.6, 6),
               _bench_P(l0, bh + 0.6, 6), tex=(pt, KEYS_BOX))
        s0, s1 = bfx(SCREEN_BOX[0]), bfx(SCREEN_BOX[2])
        e.quad('portatil_pantalla', _bench_P(s0, bh + 30, 32), _bench_P(s1, bh + 30, 32), _bench_P(s1, bh + 1, 26),
               _bench_P(s0, bh + 1, 26), tex=(pt, SCREEN_BOX))
        e.claror(_bench_P(s0 - 30, bh + 0.7, 26), _bench_P(s1 + 30, bh + 0.7, 26), _bench_P(s1 + 30, bh + 0.7, 0),
                 _bench_P(s0 - 30, bh + 0.7, 0), (120, 170, 220), lambda s, t: 0.25 * max(0.0, 1 - abs(s - 53) / 53))
    if 'nota' in estat:
        n0, n1 = bfx(NOTE_BOX[0]), bfx(NOTE_BOX[2])
        e.quad('nota', _bench_P(n0, bh + 0.8, 24), _bench_P(n1, bh + 0.8, 24), _bench_P(n1 + 2, bh + 0.8, 6),
               _bench_P(n0 + 2, bh + 0.8, 6), tex=(tex['nota'], NOTE_BOX))
    if 'remenat' in estat:
        _remenat(e, bh)
    # els llums del sostre
    lamp = _llum_pla()
    for lx, lz in LAMPS:
        e.sprite('llums', lamp, (40, 6), (lx, HW - 2, lz))
    # primer pla: una canonada que travessa el sostre, cables que pengen, una columna a la dreta i els bidons a baix
    e.tub('primer_pla', (-40, HW - 6, -70), (XR + 40, HW - 6, -70), 7, FOSC, 2.4, brides=90)
    for k, (xa, xb, cai) in enumerate(((40, 130, 16), (400, 490, 14))):
        pts = [(xa + (xb - xa) * i / 8, HW - 10 - cai * math.sin(math.pi * i / 8), -64 + k * 6) for i in range(9)]
        e.cable('primer_pla', pts, FOSC, 2.0, gruix=2.6)
    e.tub('primer_pla', (445, 0, 12), (445, HW, 12), 8, FOSC, 2.2, brides=56)
    for cx, cz, w, d, h, a in ((34, 14, 46, 36, 30, 0.5), (30, 16, 30, 24, 16, 0.2)):
        e.caixa_girada('primer_pla', cx, cz, w, d, h, a, FOSC, 1.8, y0=0 if h == 30 else 30,
                       cares={'dalt': {'ramp': FOSC, 'lvl': lambda s, t, P: 2.8 - (1.0 if abs(s - 12) < 3 and abs(t - 12) < 3 else 0)},
                              'davant': {'ramp': FOSC, 'lvl': lambda s, t, P: 1.4 + (0.8 if abs(t - 14) < 2 or abs(t - 44) < 2 else 0)},
                              'dreta': {'ramp': FOSC, 'lvl': 2.2}})
    return e


def _remenat(e, bh):
    """Calaixos mal tancats, papers girats per terra i pel taulell, un pot tombat i la porta de l'armari entreoberta."""
    bw = BENCH[2]
    cw = (bw - 6) // 6
    for i in (0, 2, 3, 5):
        l0 = 3 + i * cw + 3
        out = 8 + (i % 2) * 5
        _caixa_banc(e, 'remenat', l0, l0 + cw - 6, -out, 6, bh - 22, bh - 10, CREAM, 4.0,
                    cares={'dalt': {'ramp': DARK, 'lvl': lambda s, t, P: 1.2 + (3.0 if 4 < s < 20 and 2 < t < 6 else 0)},
                           'davant': {'ramp': CREAM, 'lvl': lambda s, t, P: 4.6 + (1.4 if abs(s - (cw - 6) / 2) < 6 and 4 < t < 6 else 0)},
                           'esquerra': {'ramp': CREAM, 'lvl': 3.0}, 'dreta': {'ramp': CREAM, 'lvl': 2.6}})
    # la porta de l'armari de sota, entreoberta
    l0 = 3 + 4 * cw + 3
    a = BENCH[5] - 0.9
    P0 = _bench_P(l0, 0, 2)
    c, s_ = math.cos(a), math.sin(a)
    L = cw - 8
    e.quad('remenat', (P0[0], bh - 26, P0[2]), (P0[0] + L * c, bh - 26, P0[2] + L * s_), (P0[0] + L * c, 4, P0[2] + L * s_),
           (P0[0], 4, P0[2]), ramp=CREAM, lvl=4.4, dues_cares=True)
    # papers pel taulell i per terra, girats
    papers = [(_bench_P(20, bh + 0.7, 18), 0.3), (_bench_P(110, bh + 0.7, 12), -0.4), (_bench_P(210, bh + 0.7, 30), 0.6),
              (_bench_P(296, bh + 0.7, 14), -0.2),
              ((80, 0.7, 150), 0.5), ((150, 0.7, 128), -0.3), ((215, 0.7, 160), 0.9), ((290, 0.7, 138), 0.2),
              ((110, 0.7, 100), -0.7), ((330, 0.7, 120), 0.4)]
    for k, ((px, py, pz), ang) in enumerate(papers):
        c, s_ = math.cos(ang), math.sin(ang)
        pts = [(px + lx * c - lz * s_, py, pz + lx * s_ + lz * c) for lx, lz in ((-9, 6), (9, 6), (9, -6), (-9, -6))]
        e.quad('remenat', *pts, ramp=PAPERC, lvl=lambda s, t, P, k=k: 4.2 - (1.6 if k % 2 and int(t) % 3 == 0 and 3 < s < 15 else 0))
    # el pot tombat i el bassal verd
    _caixa_banc(e, 'remenat', 236, 250, 20, 26, bh, bh + 6, GLASSB, 4.4)
    e.quad('remenat', _bench_P(250, bh + 0.5, 30), _bench_P(268, bh + 0.5, 30), _bench_P(272, bh + 0.5, 14),
           _bench_P(252, bh + 0.5, 14), ramp=[(30, 50, 40), (60, 90, 70), (100, 130, 110)], lvl=1.6)
    e.quad('remenat', (300, 0.6, 140), (334, 0.6, 140), (338, 0.6, 122), (302, 0.6, 118),
           ramp=[(40, 60, 30), (70, 100, 50), (110, 140, 70), (150, 180, 100)],
           lvl=2.2, forma=lambda s, t: (s / 34 - 0.5) ** 2 + (t / 20 - 0.5) ** 2 < 0.22)


# ─── Composició ─────────────────────────────────────────────────────────────

@functools.lru_cache(maxsize=None)
def _textures(dia=False):
    return {'paret': _paret_base(dia), 'nua': _paret_nua(), 'mobles': _mobles(), 'portatil': _portatil_pla(),
            'nota': _nota_pla()}


def _render(estat=frozenset(), tex=None):
    cv = Canvas(light=LIGHT)
    e = escena(cv, tex or _textures('dia' in estat), estat)
    cv.rect(0, BOTTOM + 1, W - 1, H - 1, [(0, 0, 0)], 0, lit=0)    # la barra de verbs: negre
    return cv.img, e


@functools.lru_cache(maxsize=None)
def _base(estat=frozenset()):
    return _render(estat)


def bg(cv):
    cv.img.paste(_base()[0])
    cv.P = cv.img.load()


def _decorat(*estat):
    """Un decorat: la sala amb aquell estat, menys la de sempre (només el que canvia)."""
    def draw(cv):
        img, _ = _base(frozenset(estat))
        cv.img.alpha_composite(_diff(img, _base()[0]))
        cv.P = cv.img.load()
    return draw


PROPS = {
    'portatil': _decorat('portatil'),
    'nota': _decorat('nota'),
    'remenat': _decorat('remenat'),
    'ulls_dia': _decorat('dia'),
}


# ─── Animacions ─────────────────────────────────────────────────────────────

def _sprite_capa(e, sid, img, peu_img, peu, escala_img=1.0):
    """Un fotograma d'un dibuix pla dret (un sprite de l'escena), on aquell sprite és el que es veu."""
    from pixels import nearest
    idx = e.ids.index(sid)
    k = e.cam.escala(peu) * escala_img
    u, v, _ = e.cam.projecta(peu)
    w, h = max(1, round(img.width * k)), max(1, round(img.height * k))
    im = nearest(img, (w, h)) if k >= 1 else img.resize((w, h), Image.Resampling.BOX)
    ox, oy = round(u - peu_img[0] * k), round(v - peu_img[1] * k)
    out = Image.new('RGBA', (e.cv.w, e.cv.h), (0, 0, 0, 0))
    src, dst, W_ = im.load(), out.load(), e.cv.w
    for y in range(h):
        Y = oy + y
        if not 0 <= Y < e.cv.h:
            continue
        for x in range(w):
            X = ox + x
            if 0 <= X < W_ and e.amo[Y * W_ + X] == idx and src[x, y][3] >= 128:
                dst[X, Y] = src[x, y]
    return out


def _fotograma(capes, estat=frozenset()):
    """El fons (amb un estat) amb unes capes damunt, menys el mateix fons."""
    img = _base(estat)[0]
    out = img.copy()
    for c in capes:
        out.alpha_composite(c)
    return _diff(out, img)


def _frames_port(dia):
    estat = frozenset({'dia'}) if dia else frozenset()
    _, e = _base(estat)
    return [_fotograma([e.capa(_paret(dia, vidre=i / 12), {'paret_esq'})], estat) for i in range(12)]


def _frames_portatil():
    """El portàtil sencer (el prop): el cursor que parpelleja i el llum que respira."""
    estat = frozenset({'portatil'})
    img, e = _base(estat)
    cap = _decorat('portatil')
    base = Canvas(light=LIGHT, transparent=True)
    cap(base)
    out = []
    for i in range(8):
        fr = base.img.copy()
        fr.alpha_composite(e.capa(_portatil_pla(i), {'portatil', 'portatil_pantalla'}))
        out.append(fr)
    return out


def _frames_nevera():
    _, e = _base()
    out = []
    for i in range(16):
        fl = _mobles_nevera('3' if 9 <= i <= 12 else '4', pilot=i % 8 < 1)
        out.append(_fotograma([e.capa(fl, {'nevera'})]))
    return out


def _frames_bombolla():
    """El pot del mig de la gradeta: una bombolla puja pel líquid i esclata."""
    _, e = _base()
    jx = PL.RACK[0] + 3 + 2 * 8
    path = [(jx + 3, 137), (jx + 3, 136), (jx + 2, 135), (jx + 2, 134), (jx + 3, 133), (jx + 3, 132), (jx + 2, 131)]
    bh = BENCH[4]
    out = []
    for i in range(18):
        cv = Canvas(light=PL.LIGHT, img=_mobles().copy())
        if i < len(path):
            x, y = path[i]
            cv.flat(x, y, mix(cv.get(x, y)[:3], (230, 246, 240), 0.8))
            cv.flat(x + 1, y, mix(cv.get(x + 1, y)[:3], (210, 230, 224), 0.6))
        elif i == len(path):
            for dx in (-1, 2):
                cv.flat(jx + 2 + dx, 129, (200, 220, 214))
        out.append(_fotograma([_sprite_capa(e, 'gradeta', cv.img.crop(RACK_BOX), (373 - RACK_BOX[0], 148 - RACK_BOX[1]),
                                            _bench_P(_bench_fx(373), bh, 22))]))
    return out


ANIMS = {'mar': {'frames': lambda: _frames_port(False), 'frameDuration': 220},
         'ulls_dia_mar': {'frames': lambda: _frames_port(True), 'frameDuration': 220},
         'portatil': {'frames': _frames_portatil, 'frameDuration': 265},
         'nevera': {'frames': _frames_nevera, 'frameDuration': 250},
         'bombolla': {'frames': _frames_bombolla, 'frameDuration': 140}}


# ─── Capes del davant i geometria (coordenades de sala, projectades) ─────────

def _amo(ids, estat=frozenset()):
    def mask(x, y):
        _, e = _base(estat)
        return e.ids[e.amo[y * e.cv.w + x]] in ids
    return mask


def _p(x, z, y=0.0):
    u, v, _ = CAM.projecta((x, y, z))
    return round(u), round(v)


def _pb(lx, lz, y=0.0):
    P = _bench_P(lx, y, lz)
    return _p(P[0], P[2], y)


# El primer pla tapa sempre; el taulell (amb el que hi ha a sobre) i la nevera, a qui hi passa per darrere.
FRONT = [
    {'id': 'davant', 'mask': _amo({'primer_pla'}), 'baseline': 999, 'zIndex': 30},
    {'id': 'davant_taulell', 'mask': _amo({'taulell', 'llibre', 'lupa', 'gradeta'}),
     'baseline': _pb(BENCH[2] / 2, -2)[1], 'zIndex': 20, 'props': ('portatil', 'nota', 'remenat')},
]


def _rect_mon(*Ps):
    pts = [CAM.projecta(P) for P in Ps]
    return (max(0, round(min(p[0] for p in pts))), max(0, round(min(p[1] for p in pts))),
            min(W - 1, round(max(p[0] for p in pts))), min(BOTTOM, round(max(p[1] for p in pts))))


def _rect_banc(l0, l1, z0, z1, y0, y1):
    return _rect_mon(*[_bench_P(lx, y, lz) for lx in (l0, l1) for lz in (z0, z1) for y in (y0, y1)])


def _fridge_pts():
    fx, fz, fw, fd, fh, fa = FRIDGE
    c, s_ = math.cos(fa), math.sin(fa)
    return [(fx + lx * c - lz * s_, fz + lx * s_ + lz * c) for lx, lz in
            ((-fw / 2, -fd / 2), (fw / 2, -fd / 2), (fw / 2, fd / 2), (-fw / 2, fd / 2))]


# El terra on es camina (al món): de la porta a la pica, davant i darrere del taulell; el taulell és un forat.
_FR = _fridge_pts()
WALK_MON = [(12, ZW - 10), (_FR[3][0] - 8, ZW - 10), (_FR[0][0] - 10, _FR[0][1] - 8), (_FR[1][0] + 2, _FR[1][1] - 12),
            (SINK[0] - 8, SINK[2] - 12), (XR - 40, SINK[2] - 12), (XR - 40, -100), (12, -100)]


def _v_escala(k):
    """La y de pantalla on un personatge fa escala `k` (al terra)."""
    lo, hi = 1.0, 3000.0
    for _ in range(60):
        z = (lo + hi) / 2
        if CAM.escala((260, 0, z)) > k:
            lo = z
        else:
            hi = z
    return CAM.projecta((260, 0, lo))[1]


def _talla(poly, vmax):
    """El polígon de pantalla `poly` tallat per sota de la y `vmax` (on els personatges passarien d'escala 1,2)."""
    out = []
    for (ax, ay), (bx, by) in zip(poly, poly[1:] + poly[:1]):
        if ay <= vmax:
            out.append((ax, ay))
        if (ay <= vmax) != (by <= vmax):
            k = (vmax - ay) / (by - ay)
            out.append((round(ax + (bx - ax) * k), round(vmax)))
    return out


_WALK = _talla([_p(x, z) for x, z in WALK_MON], _v_escala(1.2))
_FORAT = [_pb(lx, lz) for lx, lz in ((-8, BENCH[3] + 6), (BENCH[2] + 8, BENCH[3] + 6), (BENCH[2] + 8, -6), (-8, -6))]
_V_FONS, _V_PROP = min(v for _, v in _WALK), max(v for _, v in _WALK)


def _escala_a(v):
    """L'escala d'un personatge amb els peus a la y de pantalla `v` (al terra, la profunditat només depèn de v)."""
    lo, hi = 1.0, 3000.0
    for _ in range(60):
        z = (lo + hi) / 2
        if CAM.projecta((260, 0, z))[1] > v:
            lo = z
        else:
            hi = z
    return CAM.escala((260, 0, (lo + hi) / 2))


_bfx = _bench_fx
_BH = BENCH[4]

GEOMETRIA = {
    'things': {
        'porta': {'rect': _rect_mon((0, DOOR[2] + 8, DOOR[0] - 8), (0, 0, DOOR[1] + 2)), 'walk': _p(40, (DOOR[0] + DOOR[1]) / 2)},
        'llibre': {'rect': _rect_banc(_bfx(187), _bfx(235), 6, 36, _BH, _BH + 12), 'walk': _pb(_bfx(211), -30)},
        'portatil': {'rect': _rect_banc(_bfx(262), _bfx(320), 4, 34, _BH, _BH + 32), 'walk': _pb(_bfx(291), -30)},
        'nota': {'rect': _rect_banc(_bfx(321), _bfx(345), 2, 26, _BH, _BH + 6), 'walk': _pb(_bfx(331), -30)},
        'taulell': {'rect': _rect_banc(0, BENCH[2], -2, -2, 0, _BH - 4), 'walk': _pb(_bfx(387), -30)},
        'nevera': {'rect': _rect_mon(*[(x, y, z) for x, z in _FR for y in (0, FRIDGE[4])]),
                   'walk': _p(FRIDGE[0] - 30, FRIDGE[1] - 70)},
    },
    'spawns': {'iri': _p(280, 120), 'vet': _p(360, 110), 'juana': _pb(_bfx(240), BENCH[3] + 30)},
    'walkable': _WALK,
    'forats': [_FORAT],
    'floorSquash': 0.42,                           # (la càmera, picada: el terra es veu aixafat)
    # L'ombra de contacte: la llum dominant és el llum del sostre de davant; l'ombra s'allarga cap enfora.
    'characterShadow': {'enabled': True, 'color': '#120806', 'alpha': 0.45, 'squash': 0.4, 'core': 0.6,
                        'light': {'x': _p(*LAMPS[1])[0], 'y': _p(*LAMPS[1])[1], 'stretch': 0.6, 'reach': 160}},
    'regions': [{'id': 'perspectiva', 'active': True, 'scaleEnabled': True, 'scaleWalkSpeed': True,
                 'scaleTop': round(_escala_a(_V_FONS - 2), 3), 'scaleBottom': round(_escala_a(_V_PROP + 2), 3),
                 'points': [(0, _V_FONS - 2), (W - 1, _V_FONS - 2), (W - 1, _V_PROP + 2), (0, _V_PROP + 2)]}],
    # la llum de la sala sobre els personatges, en temps d'execució
    'characterLights': {
        'ambient': '#a89880',
        'lights': [{'x': _p(lx, lz, HW - 10)[0], 'y': _p(lx, lz, HW - 10)[1], 'radius': 220, 'color': '#ffd68c',
                    'intensity': 0.7} for lx, lz in LAMPS],
    },
}
