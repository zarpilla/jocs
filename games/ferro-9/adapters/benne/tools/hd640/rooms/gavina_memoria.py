"""
Sala de la Memòria (La Gavina, Vet). EN 3D (hd640/tres_d.py), a 1×.

El museu de propaganda de la corporació. Una càmera alta, a la dreta, mira de biaix la cantonada del fons a
l'esquerra:
  - a la paret de l'esquerra, en escorç, la **porta de sortida** cap al passadís, amb el rètol verd;
  - a la paret del fons, la **foto del torn de nit**, el **mapa de La Gavina** (la pantalla), el rètol del sostre i
    el carril dels focus;
  - al mig de la sala, separat de tot, el **sòcol** de l'holograma i l'**holograma del Director** fent de guia: llum
    cian que se suma al que hi ha darrere (s'hi passa per darrere del sòcol);
  - la **vitrina**, girada, amb el pedestal, la caixa de vidre i el buit de la clau anglesa; l'**expositor de
    fullets**, girat, prop de la cantonada de la dreta;
  - el terra de resina polida, amb els bassals dels focus i la claror de l'holograma;
  - primer pla: el cordó de vellut entre dos pals daurats, a baix a l'esquerra, i la columna fosca de la dreta.

El detall de les parets, del sòcol, de la vitrina i dels fullets ve del dibuix pla de sempre
(gavina_memoria_pla_comu.py), projectat; els decorats, la diferència amb la sala de sempre.

El món: x a la dreta (0 = la paret de la porta), y amunt (0 = el terra), z cap al fons (300 = la paret del fons);
1 unitat = 1 píxel de sala a la distància on un personatge fa ≈110 px (escala 1).
"""
import functools
import math

import numpy as np
from PIL import Image

import hd640  # noqa: F401  (posa la llibreria de dibuix a 640×360)
from hd.pix import Canvas, Light, W, H, STEEL, CYAN, WARN, PAPER, IRON, GOLD  # noqa: F401
from hd.rooms.gavina_memoria import MUSE, RESIN, FRAME, VELVET, HOLO  # noqa: F401
from hd640.rooms import gavina_memoria_pla_comu as PL
from hd640.rooms.gavina_passadis_pla_comu import FLOOR_Y, hr, diff
from hd640.tres_d import Camera, Escena, Llum

BOTTOM = 259                                       # la sala acaba aquí (a sota, la barra de verbs)
ZW = 300                                           # la paret del fons
HW = FLOOR_Y                                       # l'alçada de les parets
XC = 110                                           # al dibuix pla, la cantonada (a l'esquerra, la paret de la porta)
XR = 900                                           # on s'acaba la paret del fons (fora de la pantalla)
HOLO_P = (PL.HX - XC, 196)                         # el sòcol de l'holograma (x, z): davant del seu lloc a la paret
VITRINA = (404, 196, 0.38)                         # la vitrina: x, z, gir
FULLETS = (500, 262, 0.62)                         # l'expositor de fullets: x, z, gir


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
HOLO_C = (HOLO_P[0], 100, HOLO_P[1])
SPOT_F = (_w(173), 150, ZW - 30)                   # el focus de la foto
SPOT_V = (VITRINA[0], 150, VITRINA[1])             # el focus de la vitrina
LLUMS = [Llum(HOLO_C, 260, 1.8, power=1.4), Llum(SPOT_F, 200, 1.4, power=1.5), Llum(SPOT_V, 200, 1.5, power=1.5),
         Llum((_w(292), 90, ZW - 20), 120, 0.6)]


class _Canvas(Canvas):
    S = 1                                          # (tres_d: píxels reals per píxel de sala)


# ─── Les textures: el dibuix pla de sempre ───────────────────────────────────

def _llum_pla():
    """La llum del dibuix pla, sense la vinyeta ni l'enfosquiment de baix (la llum és la de l'escena)."""
    l = Light(ambient=0.4, vignette=None, floor_fade=None)
    l.points = list(PL.LIGHT.points)
    l.extra = list(PL.LIGHT.extra)
    return l


@functools.lru_cache(maxsize=None)
def _pla(t=0.0, mira=False):
    """El dibuix pla sencer (amb l'holograma, la vitrina i els fullets, que en surten com a retalls)."""
    cv = Canvas(light=_llum_pla())
    PL.bg(cv, mira=mira, t=t)
    return cv.img


@functools.lru_cache(maxsize=None)
def _paret(t=0.0, mira=False):
    """Les parets, de cara: la porta, la foto, el mapa, el rètol i els focus; on hi havia l'holograma, la vitrina i
    els fullets (que ara són al mig de la sala), la paret de plafons."""
    img = _pla(t, mira).copy()
    nua = Canvas(light=_llum_pla())
    PL.museum_wall(nua, 0, W - 1)
    src, dst = nua.img.load(), img.load()
    for x0, x1 in ((360, 456), (468, 552), (562, 628)):
        for y in range(36, FLOOR_Y):
            for x in range(x0, x1):
                dst[x, y] = src[x, y]
    return img


@functools.lru_cache(maxsize=None)
def _nua():
    cv = Canvas(light=Light(ambient=0.4, vignette=None, floor_fade=None))
    PL.museum_wall(cv, 0, W - 1)
    return cv.img


@functools.lru_cache(maxsize=None)
def _socol(nota=False):
    """El sòcol de l'holograma, sobre transparent (amb la placa descargolada i el paper, si cal)."""
    cv = Canvas(light=_llum_pla(), transparent=True)
    PL._socol(cv, 0.0)
    if nota:
        PL.socol(cv)
    return cv.img


SOCOL_BOX = (366, 178, 452, 214)
FOOT = (PL.HX, PL.SY1)                             # (al dibuix pla: el peu del sòcol, al mig)


def _holo(t=0.0):
    """L'holograma del Director i el raig del projector, sobre negre: es suma a l'escena (és llum)."""
    cv = Canvas(light=_llum_pla())
    ph = 2 * math.pi * t
    kc = 0.22 * (1 + 0.15 * math.sin(ph * 2) + 0.06 * math.sin(ph * 5))
    cone = lambda x, y: max(0.0, 1 - abs(x - PL.HX) / (11 + (195 - y) * 0.26)) if y < 195 else 0  # noqa: E731
    cv.tint(363, 53, 453, 195, (140, 230, 255), lambda x, y: kc * cone(x, y))
    f = (t * 2) % 1
    env = math.sin(math.pi * f)
    if env > 0.02:
        yb = 192 - f * 133
        cv.tint(363, yb - 7, 453, yb + 7, (170, 240, 255), lambda x, y: 0.2 * env * (1 - abs(y - yb) / 8) * cone(x, y))
    glow = cv.glow
    cv.glow = lambda *a, **k: None                                        # (sense la vora brillant del pla: retallada)
    PL._director(cv, t)
    cv.glow = glow
    p = 0.6 * math.sin(4 * math.pi * t)                                   # l'emissor del sòcol batega
    cv.disc(PL.HX, PL.SY0 + 4, 27, 4, HOLO, lambda nx, ny: 3.6 + p - (nx * nx + ny * ny) * 1.5, 0)
    cv.glow(PL.HX, PL.SY0 + 3, 32, (150, 235, 255), 0.4)
    return cv.img.crop(HOLO_BOX)


HOLO_BOX = (340, 40, 476, 206)


@functools.lru_cache(maxsize=None)
def _vitrina_tex(placa=True):
    """El pedestal de la vitrina (el davant) i el vellut de dins, de cara, amb la placa del robot si hi és."""
    cv = Canvas(light=_llum_pla())
    PL.bg(cv)
    if placa:
        PL.placa_robot(cv)
    return cv.img


PED_BOX = (478, 161, 541, 204)                     # el davant del pedestal (amb la placa de la peça)
VEL_BOX = (478, 144, 541, 160)                     # el vellut, amb el buit de la clau (i el de la placa)
FUL_BOX = (570, 132, 619, 185)                     # l'expositor de fullets (la capçalera i les butxaques)


# ─── Les superfícies ────────────────────────────────────────────────────────

def _terra(s, t, P):
    """La resina polida, en rajoles grans: juntes fines i un brill que s'esvaeix."""
    x, z = P[0], P[2]
    ui, vi = math.floor(x / 80), math.floor(z / 80)
    fu, fv = x - ui * 80, z - vi * 80
    v = 3.0 + (hr(ui, vi, 7) - 0.5) * 0.25
    if fu < 1.0 or fv < 1.0:
        return 1.4
    if fu < 2.2 or fv < 2.2:
        v += 0.2
    return v


FOSC = [(4, 4, 8), (8, 8, 14), (13, 13, 20), (19, 19, 28), (27, 27, 38), (37, 37, 50)]


def _sprite_alfa(e, img, peu_img, peu, mask=None, base=None):
    """Un dibuix pla dret que es **suma** a l'escena (llum: l'holograma), escalat a la seva distància; `mask`: on
    es pot sumar (no al que hi ha davant). Torna la imatge de la suma (RGBA, negre on no hi ha res)."""
    k = e.cam.escala(peu)
    u, v, _ = e.cam.projecta(peu)
    w, h = max(1, round(img.width * k)), max(1, round(img.height * k))
    im = img.convert('RGB').resize((w, h), Image.Resampling.BOX)
    ox, oy = round(u - peu_img[0] * k), round(v - peu_img[1] * k)
    add = Image.new('RGB', (e.cv.w, e.cv.h), (0, 0, 0))
    add.paste(im, (ox, oy))
    a = np.asarray(add, dtype=np.int32)
    if mask is not None:
        a = a * mask[..., None]
    return a


def escena(cv, tex, estat=frozenset()):
    """Tota la sala, de lluny a prop. `estat`: els decorats que hi són ('nota', 'placa', 'mira'). → l'Escena."""
    e = Escena(cv, CAM, LLUMS, ambient=-0.2)
    zn = CAM.pos[2] + 60
    paret, nua = tex['paret'], tex['nua']
    # ── les parets ──
    e.quad('sostre', (0, HW, zn), (XR, HW, zn), (XR, HW, ZW), (0, HW, ZW), ramp=MUSE, lvl=1.0, dues_cares=True)
    zc = ZW - XC
    e.quad('paret_esq_prop', (0, HW, zn), (0, HW, zc), (0, 0, zc), (0, 0, zn), tex=(nua, (W - (zc - zn), 0, W, HW)))
    e.quad('paret_esq', (0, HW, zc), (0, HW, ZW), (0, 0, ZW), (0, 0, zc), tex=(paret, (0, 0, XC, HW)))
    e.quad('paret_fons', (0, HW, ZW), (_w(W), HW, ZW), (_w(W), 0, ZW), (0, 0, ZW), tex=(paret, (XC, 0, W, HW)))
    e.quad('paret_fons_lluny', (_w(W), HW, ZW), (XR, HW, ZW), (XR, 0, ZW), (_w(W), 0, ZW),
           tex=(nua, (0, 0, XR - _w(W), HW)))
    # ── el terra polit: les rajoles, els bassals dels focus i la claror cian de l'holograma ──
    e.quad('terra', (0, 0, ZW), (XR, 0, ZW), (XR, 0, zn), (0, 0, zn), ramp=RESIN, lvl=_terra)
    hx, hz = HOLO_P
    e.claror((hx - 170, 0.4, hz + 110), (hx + 170, 0.4, hz + 110), (hx + 170, 0.4, hz - 170), (hx - 170, 0.4, hz - 170),
             (110, 220, 255), lambda s, t: 0.34 * max(0.0, 1 - math.hypot((s - 170) / 160, (t - 110) / 150)) ** 1.4)
    for (sx, _, sz), k in ((SPOT_F, 0.18), (SPOT_V, 0.2)):
        e.claror((sx - 80, 0.5, sz + 30), (sx + 80, 0.5, sz + 30), (sx + 80, 0.5, sz - 90), (sx - 80, 0.5, sz - 90),
                 (255, 240, 214), lambda s, t, k=k: k * max(0.0, 1 - math.hypot((s - 80) / 70, (t - 40) / 70)) ** 1.3)
    # el reflex de la paret al terra polit (una franja clara que s'esvaeix)
    e.claror((0, 0.6, ZW), (XR, 0.6, ZW), (XR, 0.6, ZW - 40), (0, 0.6, ZW - 40), (150, 160, 180),
             lambda s, t: 0.16 * max(0.0, 1 - t / 40) * (0.6 + 0.4 * (int(s + XC - 5) % 64 > 2)))
    e.foscor('racons', (0, 0.5, ZW), (XR, 0.5, ZW), (XR, 0.5, zn), (0, 0.5, zn),
             lambda s, t: max(0.45 * max(0.0, 1 - t / 16), 0.45 * max(0.0, 1 - s / 18)))
    e.foscor('sostre_fosc', (0, HW - 0.5, ZW - 0.6), (XR, HW - 0.5, ZW - 0.6), (XR, 0, ZW - 0.6), (0, 0, ZW - 0.6),
             lambda s, t: 0.3 * max(0.0, 1 - t / 30))
    # ── l'expositor de fullets, girat, amb les potes ──
    fx, fz, fa = FULLETS
    fw = FUL_BOX[2] - FUL_BOX[0]
    e.foscor('ombra_fullets', (fx - 34, 0.6, fz + 20), (fx + 34, 0.6, fz + 20), (fx + 34, 0.6, fz - 26),
             (fx - 34, 0.6, fz - 26), lambda s, t: 0.5 * max(0.0, 1 - ((s - 34) / 32) ** 2 - ((t - 22) / 20) ** 2) * 1.4)
    c, s_ = math.cos(fa), math.sin(fa)
    for lx in (-fw / 2 + 6, fw / 2 - 6):
        e.caixa_girada('fullets', fx + lx * c, fz + lx * s_, 3, 3, _y(185), fa, STEEL, 2.6)
    e.caixa_girada('fullets', fx, fz, fw, 6, FUL_BOX[3] - FUL_BOX[1], fa, STEEL, 1.6, y0=_y(185),
                   cares={'davant': {'tex': (tex['pla'], FUL_BOX)}, 'dalt': {'ramp': STEEL, 'lvl': 3.6}})
    e.caixa_girada('fullets', fx, fz, fw - 6, 14, 3, fa, STEEL, 2.4)
    # ── la vitrina, girada: el pedestal, el vellut, la caixa de vidre amb la tapa il·luminada ──
    vx, vz, va = VITRINA
    pw, ph = PED_BOX[2] - PED_BOX[0], PED_BOX[3] - PED_BOX[1]
    e.foscor('ombra_vitrina', (vx - 50, 0.6, vz + 40), (vx + 50, 0.6, vz + 40), (vx + 50, 0.6, vz - 40),
             (vx - 50, 0.6, vz - 40), lambda s, t: 0.55 * max(0.0, 1 - ((s - 50) / 46) ** 2 - ((t - 40) / 36) ** 2) * 1.5)
    vt = tex['vitrina_placa'] if 'placa' in estat else tex['vitrina']
    e.caixa_girada('vitrina', vx, vz, pw, 40, ph, va, MUSE, 3.0,
                   cares={'davant': {'tex': (vt, PED_BOX)}, 'dalt': {'tex': (vt, VEL_BOX)},
                          'esquerra': {'ramp': MUSE, 'lvl': 3.6}, 'dreta': {'ramp': MUSE, 'lvl': 2.2}})
    gh = 40
    c, s_ = math.cos(va), math.sin(va)

    def Pv(lx, y, lz):
        return (vx + lx * c - lz * s_, y, vz + lx * s_ + lz * c)
    a, b = pw / 2, 20
    for lx, lz in ((-a, b), (a, b), (-a, -b), (a, -b)):                   # els muntants d'acer
        P = Pv(lx, 0, lz)
        e.caixa_girada('vitrina', P[0], P[2], 2, 2, gh, va, STEEL, 4.0, y0=ph)
    e.caixa_girada('vitrina', vx, vz, pw + 2, 42, 4, va, STEEL, 4.2, y0=ph + gh,
                   cares={'sota': {'ramp': [(200, 190, 160), (255, 245, 220)], 'lvl': 1.0}})
    for P0, P1, P2, P3 in ((Pv(-a, ph + gh, -b), Pv(a, ph + gh, -b), Pv(a, ph, -b), Pv(-a, ph, -b)),
                           (Pv(a, ph + gh, -b), Pv(a, ph + gh, b), Pv(a, ph, b), Pv(a, ph, -b))):
        e.claror(P0, P1, P2, P3, (190, 220, 235),
                 lambda s, t: 0.16 + (0.3 if 6 < (s + t * 0.8) % 46 < 9 else 0))   # el vidre, amb els reflexos
    # ── el sòcol de l'holograma (el dibuix pla, dret), amb la seva ombra ──
    e.foscor('ombra_socol', (hx - 50, 0.6, hz + 34), (hx + 50, 0.6, hz + 34), (hx + 50, 0.6, hz - 34),
             (hx - 50, 0.6, hz - 34), lambda s, t: 0.5 * max(0.0, 1 - ((s - 50) / 46) ** 2 - ((t - 34) / 30) ** 2) * 1.4)
    soc = tex['socol_nota'] if 'nota' in estat else tex['socol']
    e.sprite('socol', soc.crop(SOCOL_BOX), (FOOT[0] - SOCOL_BOX[0], FOOT[1] - SOCOL_BOX[1]), (hx, 0, hz))
    # ── primer pla: el cordó de vellut entre dos pals daurats i la columna fosca de la dreta ──
    for px, pz in ((40, -14), (196, -30)):
        e.caixa('primer_pla', px - 2.5, px + 2.5, 0, 62, pz - 2.5, pz + 2.5, GOLD, 2.6,
                cares={'esquerra': {'ramp': GOLD, 'lvl': 3.6}, 'dreta': {'ramp': GOLD, 'lvl': 1.6}})
        e.caixa('primer_pla', px - 5, px + 5, 62, 68, pz - 5, pz + 5, GOLD, 3.4)
        e.caixa('primer_pla', px - 8, px + 8, 0, 3, pz - 8, pz + 8, GOLD, 2.0)
    e.cable('primer_pla', [(40, 58, -14), (90, 40, -19), (140, 38, -24), (196, 58, -30)], VELVET, 2.4, gruix=3.4)
    e.caixa('primer_pla', 396, 436, 0, HW, -90, -56, FOSC, 1.6,
            cares={'esquerra': {'ramp': FOSC, 'lvl': lambda s, t, P: 2.2 - (1.0 if int(P[1]) % 60 < 3 else 0)},
                   'davant': {'ramp': FOSC, 'lvl': lambda s, t, P: 1.2 + (0.6 if s < 3 else 0)}})
    return e


# ─── Composició ─────────────────────────────────────────────────────────────

def _tex(t=0.0, mira=False):
    return {'paret': _paret(t, mira), 'nua': _nua(), 'pla': _pla(), 'socol': _socol(), 'socol_nota': _socol(True),
            'vitrina': _vitrina_tex(False), 'vitrina_placa': _vitrina_tex(True)}


@functools.lru_cache(maxsize=None)
def _escena(*estat):
    """La sala sense l'holograma (que es suma després): imatge i Escena."""
    cv = _Canvas(light=LIGHT)
    e = escena(cv, _tex(mira='mira' in estat), frozenset(estat))
    cv.rect(0, BOTTOM + 1, W - 1, H - 1, [(0, 0, 0)], 0, lit=0)    # la barra de verbs: negre
    return cv.img, e


@functools.lru_cache(maxsize=None)
def _mascara():
    """On es pot sumar l'holograma: arreu menys el primer pla (que hi és davant)."""
    _, e = _escena('placa')
    ids = np.frombuffer(e.amo, dtype=np.uint16).reshape(e.cv.h, e.cv.w)
    fp = [i for i, s in enumerate(e.ids) if s == 'primer_pla']
    m = ~np.isin(ids, fp)
    m[BOTTOM + 1:] = False
    return m.astype(np.int32)


def _amb_holo(img, t=0.0):
    _, e = _escena('placa')
    add = _sprite_alfa(e, _holo(t), (FOOT[0] - HOLO_BOX[0], FOOT[1] - HOLO_BOX[1]), (HOLO_P[0], 0, HOLO_P[1]),
                       mask=_mascara())
    a = np.asarray(img, dtype=np.int32).copy()
    a[..., :3] = np.clip(a[..., :3] + add, 0, 255)
    return Image.fromarray(a.astype(np.uint8), 'RGBA')


@functools.lru_cache(maxsize=None)
def _estat(*estat):
    return _amb_holo(_escena(*estat)[0])


def _base():
    """La sala de sempre: amb la placa del robot a la vitrina (el decorat `placa_robot` és la placa)."""
    return _estat('placa'), _escena('placa')[1]


@functools.lru_cache(maxsize=None)
def _sense_placa():
    return _estat()


def bg(cv):
    cv.img.paste(_sense_placa())
    cv.P = cv.img.load()


def _decorat(*estat):
    def draw(cv):
        cv.img.alpha_composite(diff(_estat(*sorted(estat)), _sense_placa()))
        cv.P = cv.img.load()
    return draw


PROPS = {'socol': _decorat('nota'), 'foto_mira': _decorat('mira'), 'placa_robot': _decorat('placa')}


# ─── Animació de fons: l'holograma tremola i el raig respira; al mapa, la ruta avança i l'estrella parpelleja ──

def _relleu(img, c0, ct):
    """On la capa del moment `ct` canvia respecte de la de l'inici `c0`, el fons escalat pel mateix factor."""
    a0, at = np.asarray(c0, dtype=np.float32), np.asarray(ct, dtype=np.float32)
    m = (np.abs(at[..., :3] - a0[..., :3]).sum(-1) > 0) & (at[..., 3] > 0) & (a0[..., 3] > 0)
    if not m.any():
        return img
    out = np.asarray(img, dtype=np.float32).copy()
    k = at[..., :3] / np.maximum(a0[..., :3], 8.0)
    out[..., :3][m] = np.clip(out[..., :3][m] * k[m], 0, 255)
    return Image.fromarray(out.astype(np.uint8), 'RGBA')


def _ambient_frames(n=24):
    img0, e = _escena()
    base = _sense_placa()
    parets = {'paret_esq', 'paret_fons'}
    c0 = e.capa(_paret(0.0), parets)
    out = []
    for i in range(n):
        t = i / n
        fr = _amb_holo(_relleu(img0, c0, e.capa(_paret(t), parets)), t)
        out.append(diff(fr, base))
    return out


ANIMS = {'ambient': {'frames': _ambient_frames, 'frameDuration': 120}}


# ─── Capes del davant ───────────────────────────────────────────────────────

def _amo(ids):
    def mask(x, y):
        _, e = _escena()
        return e.ids[e.amo[y * e.cv.w + x]] in ids
    return mask


def _p(x, z, y=0.0):
    u, v, _ = CAM.projecta((x, y, z))
    return round(u), round(v)


# El primer pla (sempre davant), el sòcol, la vitrina i els fullets (qui hi passa per darrere, hi queda darrere).
FRONT = [
    {'id': 'davant', 'mask': _amo({'primer_pla'}), 'baseline': 999, 'zIndex': 20},
    {'id': 'davant_socol', 'mask': _amo({'socol'}), 'baseline': _p(HOLO_P[0], HOLO_P[1] - 10)[1], 'zIndex': 20,
     'props': ('socol',)},
    {'id': 'davant_vitrina', 'mask': _amo({'vitrina'}), 'baseline': _p(VITRINA[0], VITRINA[1] - 12)[1], 'zIndex': 20,
     'props': ('placa_robot',)},
    {'id': 'davant_fullets', 'mask': _amo({'fullets'}), 'baseline': _p(FULLETS[0], FULLETS[1] - 4)[1], 'zIndex': 20},
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
WALK_MON = [(16, _z_a(16, _VP)), (16, 286), (540, 286), (540, _z_a(540, _VP))]
_WALK = [_p(x, z) for x, z in WALK_MON]
_V_FONS, _V_PROP = min(v for _, v in _WALK), max(v for _, v in _WALK)


def _forat(cx, cz, w, d, ang, m=8):
    c, s_ = math.cos(ang), math.sin(ang)
    return [_p(cx + lx * c - lz * s_, cz + lx * s_ + lz * c)
            for lx, lz in ((-w / 2 - m, -d / 2 - m), (w / 2 + m, -d / 2 - m), (w / 2 + m, d / 2 + m - 2), (-w / 2 - m, d / 2 + m - 2))]


def _sprite_rect(peu, peu_img, box, fbox):
    """El rectangle de pantalla d'un tros (`fbox`, al dibuix pla) d'un dibuix dret (retall `box`, peu `peu_img`)."""
    k = CAM.escala(peu)
    u, v, _ = CAM.projecta(peu)
    ox, oy = u - peu_img[0] * k, v - peu_img[1] * k
    return (round(ox + (fbox[0] - box[0]) * k), round(oy + (fbox[1] - box[1]) * k),
            round(ox + (fbox[2] - box[0]) * k), round(oy + (fbox[3] - box[1]) * k))


_HP = ((HOLO_P[0], 0, HOLO_P[1]), (FOOT[0] - HOLO_BOX[0], FOOT[1] - HOLO_BOX[1]), HOLO_BOX)


def _caixa_rect(cx, cz, w, d, h, ang, y0=0.0):
    c, s_ = math.cos(ang), math.sin(ang)
    return _rect_mon(*[(cx + lx * c - lz * s_, y, cz + lx * s_ + lz * c)
                       for lx in (-w / 2, w / 2) for lz in (-d / 2, d / 2) for y in (y0, y0 + h)])


GEOMETRIA = {
    'things': {
        'porta_passadis': {'rect': _rect_mon((0, _y(75), _wz(10)), (0, 0, _wz(87))), 'walk': _p(32, _wz(50))},
        'foto': {'rect': _rect_mon((_w(120), _y(47), ZW), (_w(226), _y(135), ZW)), 'walk': _p(_w(173), 262)},
        'mapa': {'rect': _rect_mon((_w(232), _y(40), ZW), (_w(354), _y(136), ZW)), 'walk': _p(_w(293), 262)},
        'holograma': {'rect': _sprite_rect(*_HP, (366, 58, 452, 188)), 'walk': _p(HOLO_P[0] - 10, HOLO_P[1] - 60)},
        'socol': {'rect': _sprite_rect(*_HP, (372, 188, 444, 210)), 'walk': _p(HOLO_P[0] - 10, HOLO_P[1] - 60)},
        'vitrina': {'rect': _caixa_rect(VITRINA[0], VITRINA[1], 64, 42, 88, VITRINA[2]),
                    'walk': _p(VITRINA[0] - 30, VITRINA[1] - 64)},
        'fullets': {'rect': _caixa_rect(FULLETS[0], FULLETS[1], 50, 10, 74, FULLETS[2]),
                    'walk': _p(FULLETS[0] - 40, FULLETS[1] - 52)},
    },
    'spawns': {'vet': _p(60, 170), 'cargol_vell': _p(180, 150)},
    'walkable': _WALK,
    'forats': [_forat(HOLO_P[0], HOLO_P[1], 66, 30, 0.0, m=6), _forat(VITRINA[0], VITRINA[1], 64, 42, VITRINA[2], m=6),
               _forat(FULLETS[0], FULLETS[1], 50, 14, FULLETS[2], m=6)],
    'floorSquash': 0.42,
    # L'ombra de contacte: la llum dominant és l'holograma, al mig de la sala.
    'characterShadow': {'enabled': True, 'color': '#060812', 'alpha': 0.4, 'squash': 0.4, 'core': 0.6,
                        'light': {'x': _p(*HOLO_P)[0], 'y': _p(*HOLO_P)[1], 'stretch': 0.7, 'reach': 200}},
    'regions': [{'id': 'perspectiva', 'active': True, 'scaleEnabled': True, 'scaleWalkSpeed': True,
                 'scaleTop': round(_escala_a(_V_FONS - 2), 3), 'scaleBottom': round(_escala_a(_V_PROP + 2), 3),
                 'points': [(0, _V_FONS - 2), (W - 1, _V_FONS - 2), (W - 1, _V_PROP + 2), (0, _V_PROP + 2)]}],
    'characterLights': {
        'ambient': '#8e94a8',
        'lights': [
            {'x': _p(HOLO_P[0], HOLO_P[1], 100)[0], 'y': _p(HOLO_P[0], HOLO_P[1], 100)[1], 'radius': 220,
             'color': '#78dcff', 'intensity': 1.1},                                     # l'holograma
            {'x': _p(SPOT_F[0], SPOT_F[2], SPOT_F[1])[0], 'y': _p(SPOT_F[0], SPOT_F[2], SPOT_F[1])[1], 'radius': 170,
             'color': '#fff0d6', 'intensity': 0.6},                                     # el focus de la foto
            {'x': _p(SPOT_V[0], SPOT_V[2], SPOT_V[1])[0], 'y': _p(SPOT_V[0], SPOT_V[2], SPOT_V[1])[1], 'radius': 170,
             'color': '#fff0d6', 'intensity': 0.6},                                     # el focus de la vitrina
        ],
    },
}
