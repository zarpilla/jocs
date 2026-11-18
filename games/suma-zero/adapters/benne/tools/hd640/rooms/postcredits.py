"""
L'escena de després dels crèdits, a 640×360: l'estudi de l'Iri (hd640/rooms/pis_estudi.py), de nit i amb els llums
apagats. Cinemàtica. EN 3D, a 1×: és la mateixa escena de l'estudi (la mateixa càmera, el mateix pla), amb unes
altres textures i una altra llum:
  - tot més fosc i blavós: la llum de la lluna i del fanal entra per la persiana i fa franges a terra (el neó del
    carrer, més blau);
  - la cuina, apagada (el passaplats, fosc, amb el led del forn);
  - les pantalles, encara enceses: les dels costats, amb el salvapantalles d'estrelles; la del mig, un terminal
    negre amb una línia nova, «ROBIN HOOD 3.0?», i el cursor que fa pampallugues; és l'única llum de la sala, i
    deixa a les fosques tot el que és lluny de la taula;
  - el router, amb el cable de xarxa rosegat (els fils de coure a l'aire) i el llum vermell que parpelleja;
  - a terra, al costat del moble del router, un tros de pizza mossegat (en Diu no: els personatges no hi són).
Animació: `cursor` (el cursor del terminal, el led vermell del router i les estrelles del salvapantalles).

L'escena, les textures i les peces són les de pis_estudi (que no es toca); aquí només hi ha el que canvia.
"""
import functools
import math

import hd640  # noqa: F401  (posa la llibreria de dibuix a 640×360)
import numpy as np
from PIL import Image

from hd640 import llum
from hd.pix import Light, Canvas, W, H, hr
from hd.rooms.comu import text, _diff
from hd.rooms.postcredits import MOON, TERM, DIMSCR, CHEESE, SAUCE, CRUST, NETB
from hd640.rooms import pis_estudi as PE
from hd640.rooms import pis_estudi_pla_comu as PL
from hd640.rooms.pis_estudi_pla_comu import DESKB, PORTS
from hd640.tres_d import Llum

LIGHT = Light(ambient=0.0, vignette=None, floor_fade=None)   # (la llum és la del món: la de l'escena de l'estudi)

MAIN = (339, 83, 416, 143)   # la pantalla del mig (interior), al dibuix pla
SIDES = ((275, 99, 328, 147), (427, 99, 480, 147))


# ─── Les textures planes: les de l'estudi, de nit ───────────────────────────

def hatch_dark(cv):
    """El passaplats, amb la cuina apagada."""
    x0, y0, x1, y1 = PL.HATCH
    for y in range(y0 + 3, y1 - 2):
        for x in range(x0 + 3, x1 - 2):
            cv.put(x, y, DIMSCR, 0.6 + (0.4 if y > 107 else 0) + (0.3 if (x - y) % 13 == 0 else 0), lit=0)
    cv.rect(x0 + 3, 106, x1 - 3, 108, DIMSCR, 0.2, lit=0)
    cv.flat(621, 120, (60, 220, 120))                               # el led verd del forn
    cv.flat(622, 120, (40, 160, 90))
    for (a, b, c, d) in ((x0, y0, x1, y0 + 2), (x0, y1 - 2, x1, y1), (x0, y0, x0 + 2, y1), (x1 - 2, y0, x1, y1)):
        cv.rect(a, b, c, d, DESKB, 1.6)


def side_screens(cv, t=0):
    """Les pantalles dels costats, amb un salvapantalles: estrelles fosques (algunes parpellegen amb t)."""
    for (x0, y0, x1, y1) in SIDES:
        sx0, sy0, sx1, sy1 = x0 + 3, y0 + 3, x1 - 3, y1 - 4
        for y in range(sy0, sy1 + 1):
            for x in range(sx0, sx1 + 1):
                cv.put(x, y, DIMSCR, 1.6 + (0.2 if y % 2 else 0), lit=0)
        for i in range(18):
            px, py = sx0 + 1 + int(hr(i, x0) * (sx1 - sx0 - 2)), sy0 + 1 + int(hr(x0, i) * (sy1 - sy0 - 2))
            if hr(i, x0, t) > 0.85:
                cv.flat(px, py, (60, 90, 130))
                continue
            col = (140, 190, 230) if i % 3 else (220, 240, 255)
            cv.flat(px, py, col)
            if i % 5 == 0:                                          # les grosses, en creu
                for dx, dy in ((1, 0), (-1, 0), (0, 1), (0, -1)):
                    cv.flat(px + dx, py + dy, (70, 110, 160))


def question(cv, x, y, col):
    """L'interrogant (la font petita no en té)."""
    for j, row in enumerate(['110', '001', '010', '000', '010']):
        for i, bit in enumerate(row):
            if bit == '1':
                cv.flat(x + i, y + j, col)


def prompt(cv, x, y, col):
    """L'indicador «>»."""
    for dx, dy in ((0, 0), (1, 1), (2, 2), (1, 3), (0, 4)):
        cv.flat(x + dx, y + dy, col)


def terminal(cv):
    """La pantalla del mig, al pla: un terminal negre i la feina vella, gairebé esborrada. (La línia nova s'escriu
    després, a 1:1: vegeu `_linia_nova`.)"""
    sx0, sy0, sx1, sy1 = MAIN
    for y in range(sy0, sy1 + 1):
        for x in range(sx0, sx1 + 1):
            cv.put(x, y, TERM, 1.0 + (0.3 if y % 2 else 0), lit=0)
    dim = (30, 90, 76)
    for k, row in enumerate(range(sy0 + 3, sy0 + 26, 5)):
        n = 16 + int(hr(k, 7) * 40)
        cv.flat(sx0 + 3, row, dim)
        for x in range(sx0 + 7, min(sx1 - 3, sx0 + 7 + n)):
            if hr(x // 4, k) > 0.3 and (x + 1) % 4:
                cv.flat(x, row, dim)


def _mon_a_pantalla(fx, fy):
    """Un punt del dibuix pla dels monitors → on cau a la pantalla (els monitors són un sprite de l'escena)."""
    x0, x1, zf, zb, dh = PE.DESK
    peu = ((x0 + x1) / 2, dh, zb - 12)
    k = PE.CAM.escala(peu)
    u, v, _ = PE.CAM.projecta(peu)
    pw, ph = (PE.MON_BOX[2] - PE.MON_BOX[0]) / 2, PE.MON_BOX[3] - PE.MON_BOX[1] - 1
    return round(u - pw * k) + (fx - PE.MON_BOX[0]) * k, round(v - ph * k) + (fy - PE.MON_BOX[1]) * k


def _linia_nova(img, e, cursor=True):
    """La línia nova del terminal, «> ROBIN HOOD 3.0?», i el cursor, a 1:1 damunt la pantalla del mig (a la mida a
    què es veu el monitor, la lletra del pla es trencaria). Només on es veu el monitor."""
    cv = Canvas(img=img)
    tmp = Canvas(w=80, h=24, transparent=True)
    col = (180, 255, 220)
    prompt(tmp, 0, 3, col)
    w = text(tmp, 'ROBIN HOOD 3.0', 5, 3, TERM, 0, lit=0, flat=col)
    question(tmp, 5 + w + 1, 3, col)
    prompt(tmp, 0, 13, (90, 170, 140))
    if cursor:
        tmp.rect(5, 13, 8, 18, [(150, 250, 210)], 0, lit=0)
    u, v = _mon_a_pantalla(MAIN[0] + 2.5, 109)
    idx = e.ids.index('monitors')
    src = tmp.img.load()
    for j in range(tmp.h):
        for i in range(tmp.w):
            c = src[i, j]
            X, Y = round(u) + i, round(v) + j
            if c[3] and 0 <= X < W and 0 <= Y < H and e.amo[Y * W + X] == idx:
                cv.P[X, Y] = c
    return img


def router_led(cv, led=True):
    """Els leds del router apagats, menys el vermell d'error."""
    for x in PORTS:
        cv.flat(x + 1, 156, (40, 26, 20))
        cv.flat(x + 2, 156, (40, 26, 20))
    cv.flat(530, 156, (255, 60, 50) if led else (70, 20, 20))
    cv.flat(531, 156, (220, 40, 36) if led else (60, 16, 16))


def _paret():
    """Les parets de l'estudi, amb el passaplats a les fosques."""
    cv = Canvas(light=PL.LIGHT)
    PL.wall(cv)
    PL.window(cv, rain=0, neon=True)
    PL.poster(cv)
    PL.hatch(cv)
    PE._presa(cv)
    hatch_dark(cv)
    return cv.img


def _escriptori(t=0):
    """Els monitors (salvapantalles i terminal) i el router (el led vermell) de l'estudi, de nit."""
    img = PE._escriptori()
    cv = Canvas(light=PL.LIGHT, img=img.copy())
    side_screens(cv, t)
    terminal(cv)
    router_led(cv, led=t in (0, 1, 3))
    return cv.img


@functools.lru_cache(maxsize=None)
def _textures(t=0):
    return {'paret': _paret(), 'escriptori': _escriptori(t)}


# ─── L'escena: la de l'estudi, i el que hi ha de nou ────────────────────────

CAB_X, CAB_Z = PE.CAB[0], PE.CAB_Z
PIZZA = (CAB_X + 34, CAB_Z - 66)            # el tros de pizza, a terra, al costat del moble
ESTAT = frozenset({'fibra', 'alimentacio'})


def _pizza(e):
    """Un tros de pizza a terra, mossegat: un triangle de formatge amb la crosta, les rodanxes i la mossegada."""
    px, pz = PIZZA
    L, A = 40.0, 26.0                                                # la llargada i l'amplada de la crosta

    def dins(s, t):
        u = s / L                                                    # 0 = la punta, 1 = la crosta
        if abs(t - A / 2) > A / 2 * u:
            return False
        return math.hypot(s - L * 0.55, t - A * 0.92) > 6.0          # la mossegada
    ang = -0.35
    c, s_ = math.cos(ang), math.sin(ang)

    def P(lx, lz):
        return (px + lx * c - lz * s_, 0.6, pz + lx * s_ + lz * c)

    def lvl(s, t, P_):
        return 2.3 + (hr(int(s // 2), int(t // 2)) - 0.5) * 0.9
    e.foscor('ombra_pizza', P(-2, -3), P(L + 2, -3), P(L + 2, A + 3), P(-2, A + 3),
             lambda s, t: 0.4 if dins(max(0.0, s - 2), max(0.0, t - 3)) else 0.0)
    e.quad('pizza', P(0, A), P(L, A), P(L, 0), P(0, 0), ramp=CHEESE, lvl=lvl, forma=dins, dues_cares=True)
    e.quad('pizza', P(L - 5, A), P(L, A), P(L, 0), P(L - 5, 0), ramp=CRUST,
           lvl=lambda s, t, P_: 1.8 + (0.8 if s > 2.5 else 0), forma=lambda s, t: dins(L - 5 + s, t), dues_cares=True)
    for (lx, lz) in ((16, 12), (25, 7), (27, 17)):                    # les rodanxes de tomàquet i una oliva
        e.quad('pizza', P(lx - 2.4, lz + 2.4), P(lx + 2.4, lz + 2.4), P(lx + 2.4, lz - 2.4), P(lx - 2.4, lz - 2.4),
               ramp=SAUCE, lvl=1.6, forma=lambda s, t: math.hypot(s - 2.4, t - 2.4) < 2.4, dues_cares=True)
    for dx, dz in ((L + 4, 3), (L + 7, 9)):                          # les engrunes
        e.quad('pizza', P(dx, dz + 0.8), P(dx + 1.2, dz + 0.8), P(dx + 1.2, dz), P(dx, dz), ramp=CRUST, lvl=2.4,
               dues_cares=True)


def _cable_rosegat(e):
    """El cable de xarxa, rosegat a mig camí: un tros penja del router i acaba en fils; l'altre, a terra, va cap a la
    torre. Els fils de coure i de colors, a l'aire."""
    cx_, ch = CAB_X, PE.CAB[4]
    rp = (cx_ - 6, ch + 6, CAB_Z - 6)                                # els ports del router
    tall = (cx_ - 26, 1.2, CAB_Z - 36)                               # on el va rosegar
    e.cable('xarxa', [rp, (cx_ - 20, 20, CAB_Z - 18), (cx_ - 24, 6, CAB_Z - 30), tall], NETB, 2.2, gruix=1.8)
    tall2 = (tall[0] - 14, 0.8, tall[2] - 8)
    tx1, tz0 = PE.TOWER[1], PE.TOWER[2]
    e.cable('xarxa', [tall2, (230, 0.8, 228), (130, 0.8, 238), (tx1, 10, tz0 + 6)], NETB, 2.0, gruix=1.8)
    wires = ((230, 150, 70), (90, 200, 90), (250, 160, 60), (110, 150, 240), (240, 240, 240))
    for k, col in enumerate(wires):                                  # els fils, de tots dos caps
        ramp = [tuple(v // 3 for v in col), col]
        a = k * 1.3 - 2.6
        e.cable('xarxa', [tall, (tall[0] - 4 + a, 1.0 + (k % 2) * 2.5, tall[2] - 3 - abs(a))], ramp, 1.0, gruix=0.5)
        e.cable('xarxa', [tall2, (tall2[0] + 4 + a, 0.9 + (k % 3), tall2[2] + 3 + a * 0.6)], ramp, 1.0, gruix=0.5)
    for i in range(6):                                               # trossets de plàstic blau rosegat
        x, z = tall[0] - 8 + hr(i, 3) * 14, tall[2] - 6 + hr(i, 4) * 10
        e.quad('xarxa', (x, 0.7, z + 0.8), (x + 1.2, 0.7, z + 0.8), (x + 1.2, 0.7, z), (x, 0.7, z), ramp=NETB, lvl=2.0,
               dues_cares=True)


def escena(cv, tex):
    e = PE.escena(cv, tex, ESTAT)
    # la llum de la lluna i del fanal: la mateixa persiana que el neó, més blava
    e.claror((0, 0.45, PE.ZW), (360, 0.45, PE.ZW), (360, 0.45, 0), (0, 0.45, 0), (110, 140, 230),
             lambda s, t: 0.8 * PE._llum_neo(s, PE.ZW - t))
    # el led vermell del router: el que hi ha a terra al costat (el cable rosegat, la pizza) se'n veu una mica
    e.llums.append(Llum((CAB_X, PE.CAB[4] + 8, CAB_Z - 20), 110, 1.6, power=1.4))
    _cable_rosegat(e)
    _pizza(e)
    return e


# ─── La nit: llum i corba de to ─────────────────────────────────────────────

def _nit(img):
    """Tot cap al blau fosc, i més fosc com més lluny de les pantalles (els llums de la sala, apagats); menys el que
    brilla (pantalles, leds, el neó): el que fa llum no es toca."""
    a = np.asarray(img.convert('RGBA')).astype(np.float32)
    rgb = a[..., :3]
    lum = rgb.max(axis=2)
    mx, my = PE._proj(PE.MON_C)
    ys, xs = np.mgrid[0:img.height, 0:img.width]
    d = np.hypot((xs - mx) / 1.25, (ys - my - 30)) / 300.0
    fosc = np.clip(0.25 + 0.5 * d, 0.25, 0.75)                     # quant s'enfosqueix (lluny de la taula, més)
    blau = np.stack([rgb[..., 0] * 0.55 + 4, rgb[..., 1] * 0.66 + 8, rgb[..., 2] * 0.92 + 24], axis=2)
    out = rgb + (blau - rgb) * 0.6
    out = out * (1 - fosc[..., None])
    keep = (lum > 150)[..., None]
    out = np.where(keep, rgb, out)
    a[..., :3] = np.clip(out, 0, 255)
    return Image.fromarray(a.astype(np.uint8), 'RGBA')


def _fx(led=True):
    mx, my = PE._proj(PE.MON_C)
    wx, wy = PE._proj((0, (PE.WIN[2] + PE.WIN[3]) / 2, (PE.WIN[0] + PE.WIN[1]) / 2))
    rx, ry = PE._proj((CAB_X, PE.CAB[4] + 10, CAB_Z))
    light = [llum.wash(mx, my + 14, 240, (70, 210, 190), k=1.1, air=0.035, squash=1.1),      # les pantalles
             llum.wash(wx, wy + 20, 150, MOON, k=0.7, air=0.04, squash=0.8)]                  # la lluna, per la finestra
    if led:                                                                                   # el led del router
        light.append(llum.wash(rx, ry, 40, (255, 50, 40), k=1.0, air=0.12))
    tone = [llum.grade(contrast=1.1, pivot=30, sat=1.1, lift=(2, 3, 12))]
    bloom = [llum.bloom(thr=140)]
    return light, bloom, tone


def _amb_llum(img, led=True):
    light, bl, tone = _fx(led)
    return llum.apply(_nit(img), light + bl + tone)


def _render(t=0):
    cv = Canvas(light=LIGHT)
    e = escena(cv, _textures(t))
    _linia_nova(cv.img, e)
    return cv.img, e


@functools.lru_cache(maxsize=None)
def _base():
    return _render()


@functools.lru_cache(maxsize=None)
def _base_llum():
    return _amb_llum(_base()[0])


def bg(cv):
    cv.img.paste(_base_llum())
    cv.P = cv.img.load()


PROPS = {}


def _frames():
    """El cursor, el led i les estrelles: els monitors i el router (sprites de l'escena) amb el pla de cada fotograma."""
    _, e = _base()
    x0, x1, zf, zb, dh = PE.DESK
    mon_peu = ((PE.MON_BOX[2] - PE.MON_BOX[0]) / 2, PE.MON_BOX[3] - PE.MON_BOX[1] - 1)
    rt_peu = ((PE.ROUTER_BOX[2] - PE.ROUTER_BOX[0]) / 2, PE.ROUTER_BOX[3] - PE.ROUTER_BOX[1] - 1)
    out = []
    for i in range(4):
        esc = _escriptori(i)
        img = _base()[0].copy()
        img.alpha_composite(PE._sprite_capa(e, 'monitors', esc.crop(PE.MON_BOX), mon_peu, ((x0 + x1) / 2, dh, zb - 12)))
        img.alpha_composite(PE._sprite_capa(e, 'router', esc.crop(PE.ROUTER_BOX), rt_peu, (CAB_X, PE.CAB[4], CAB_Z)))
        _linia_nova(img, e, cursor=i % 2 == 0)
        out.append(_diff(_amb_llum(img, led=i in (0, 1, 3)), _base_llum()))
    return out


ANIMS = {'cursor': {'frames': _frames, 'frameDuration': 500}}


GEOMETRIA = {
    'things': {},
    'spawns': {},
    'walkable': [(200, 253), (267, 253), (267, 261), (200, 261)],
}
