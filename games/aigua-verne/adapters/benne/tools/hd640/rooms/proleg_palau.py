"""
Aigua Verne — `proleg_palau` (P, cinemàtica): el despatx del Magnat Verne, al palau orbital. EN 3D
(hd640/tres_d.py), a 1×, amb un enquadrament de cinema.

S'hi grava un anunci: llum perfecta. La càmera és darrere l'equip de rodatge, a l'altura del pit i girada cap a la
cantonada de la dreta:
  - primer pla: la càmera d'anunci al trípode, a contrallum i tallada per la vora de l'esquerra, mirant la taula;
  - la taula blanca del Magnat, girada (se'n veuen el davant amb la gota, el costat i el sobre), amb la cadira alta
    al darrere — en Verne s'hi posa darrere (FRONT);
  - el focus d'estudi, encès, que fa un raig de llum en diagonal fins a la taula (decorat `focus_apagat`);
  - la paret de vidre, de terra a sostre, amb els muntants d'or que fugen: l'espai, Terra-2 enorme a baix a
    l'esquerra i un dipòsit orbital (ANIMS `estrelles`);
  - el panell del preu, penjat del sostre (decorats `preu46` i `preu48`);
  - a la dreta, contra la paret de marbre, l'aquari dels trenta-tres peixos platejats, amb tres cares (ANIMS
    `peixos`);
  - a terra, a la dreta, el tros de vidre: s'hi veu, molt avall, la piscina central buida (en Dividend s'hi està
    al costat).
Dues franges negres (la de dalt i la barra de sota) fan de pantalla de cinema.

El detall ve del despatx pla de sempre (proleg_palau_pla_comu.py), dibuixat de cara i projectat.

El món: x a la dreta, y amunt (0 = el terra), z cap al fons (420 = la paret de vidre); 1 unitat = 1 píxel de sala a
la distància on un personatge fa 100 px (escala 1).
"""
import functools
import math

import hd640  # noqa: F401  (abans de cap hd.rooms: posa la llibreria a 640×360)
from hd.pix import Canvas, Light, W, H, hr
from hd.rooms.comu import _diff
from hd640.rooms import proleg_palau_pla_comu as PL
from hd640.rooms.palau_comu import (MARB, ORP, TURQ, CROM, NEGRE, AIGUA, espai, terra2, diposit,
                                    vena, panell_valor, estrelles_frames, aigua_aquari, peixos)
from hd640.tres_d import Camera, Escena, Llum, llum_personatges

BOTTOM = 259                                       # la sala acaba aquí (a sota, negre)
BARRA = 18                                         # la franja negra de dalt (cinema)
ZG = 420                                           # la paret de vidre
XM = 700                                           # la paret de marbre de la dreta
HC = 250                                           # el sostre
TAULA = (300, 214, -0.42, 176, 66, 54)             # la taula: x, z del centre, gir, llarg, fons, alçada
CADIRA = (318, 274)
FOCUS = (120, 196, 158)                            # el peu del focus (x, z) i l'alçada del cap
CAMD = (64, 40)                                    # el trípode de la càmera d'anunci (x, z): primer pla
AQ = (604, 690, 262, 330, 46, 168)                 # l'aquari: x0, x1, z0, z1, y del vidre (de baix a dalt)
PANELL = (470, 330, 160)                           # el panell del preu: x, z del centre, y de baix
POU = (420, 520, 104, 170)                         # el tros de vidre del terra: x0, x1, z0, z1
POU_FONS = -420                                    # la piscina, a sota (y del fons)

CAM = Camera(pos=(190, 150, -250), yaw=0.2, pitch=0.08, f=430, centre=(318, 118))

_ST = {'focus': True}

LIGHT = Light(ambient=0.0, vignette=None, floor_fade=None)


def _llums():
    ll = [Llum((300, 230, 200), 420, 1.2, power=1.1),               # la llum perfecta de l'anunci (rebots)
          Llum((646, 120, 240), 160, 1.4, power=1.5),               # la llum blava de l'aquari
          Llum((200, 160, 500), 600, 0.7, power=1.0)]               # el resplendor de Terra-2, pel vidre
    if _ST['focus']:
        ll.append(Llum((300, 120, 214), 160, 2.0, power=1.4))      # el focus, sobre la taula
    return ll


# ─── Les textures: el despatx pla de sempre ─────────────────────────────────

@functools.lru_cache(maxsize=None)
def _espai():
    """El que es veu pel vidre (un pla molt gran al fons): l'espai, Terra-2 enorme a baix a l'esquerra i el dipòsit.
    → (imatge, estrelles brillants)."""
    w, h = 900, 412
    cv = Canvas(w, h, light=None)
    bright = espai(cv, 0, 0, w - 1, h - 1, seed=17, dens=1.4)
    terra2(cv, 196, 492, 336, seed=5, sun=(0.7, -0.5), mask=lambda x, y: 0 <= x < w and 0 <= y < h)
    diposit(cv, 540, 150, 0.6)
    return cv.img, tuple(bright)


@functools.lru_cache(maxsize=None)
def _pla():
    """Les peces planes, a les coordenades de sempre: la cadira, la taula, el panell i la càmera d'anunci."""
    cv = Canvas(light=PL.LIGHT, transparent=True)
    PL.cadira(cv)
    PL.taula(cv)
    PL.panell(cv)
    PL.camera(cv)
    return cv.img


def _aquari_pla(t=0.0):
    x0, y0, x1, y1 = PL.AQ
    cv = Canvas(light=PL.LIGHT)
    aigua_aquari(cv, x0, y0, x1, y1, t)
    peixos(cv, x0, y0, x1, y1, t)
    PL.vidre_aquari(cv)
    return cv.img


# ─── Les superfícies ────────────────────────────────────────────────────────

def _marbre(base=6.0, tile=60, seed=5, gold=2):
    """Lloses de marbre blanc amb venes i una línia d'or cada `gold` lloses (s, t: coordenades del pla)."""
    def L(s, t, P):
        iu, iv = math.floor(s / tile), math.floor(t / tile)
        v = base + (hr(iu, iv, seed) - 0.5) * 0.5 - vena(s * 0.7, t * 1.2, seed + iu * 3 + iv) * 1.6
        eu, ev = s % tile < 1.1, t % tile < 1.1
        if eu or ev:
            return v - 1.4
        return v
    return L


def _terra(s, t, P):
    x, z = P[0], P[2]
    tile = 64
    iu, iv = math.floor(x / tile), math.floor(z / tile)
    v = 6.0 + (hr(iu, iv, 5) - 0.5) * 0.5 - vena(x * 0.7, z * 1.4, 5 + iu * 3 + iv) * 1.8
    return v


def _or_terra(e):
    """Les línies d'or del terra, cada dues lloses (es pinten a part: en una altra rampa)."""
    for k in range(-6, 14):
        x = k * 128
        e.quad('terra', (x - 1.6, 0.2, ZG), (x + 1.6, 0.2, ZG), (x + 1.6, 0.2, -200), (x - 1.6, 0.2, -200), ramp=ORP, lvl=4.6,
               forma=lambda s, t, x=x: not _al_pou(x, ZG - t))
    for k in range(-2, 4):
        z = k * 128
        e.quad('terra', (-400, 0.2, z + 1.6), (XM, 0.2, z + 1.6), (XM, 0.2, z - 1.6), (-400, 0.2, z - 1.6), ramp=ORP, lvl=4.2,
               forma=lambda s, t, z=z: not _al_pou(s - 400, z))


def _al_pou(x, z, m=6):
    x0, x1, z0, z1 = POU
    return x0 - m < x < x1 + m and z0 - m < z < z1 + m


def escena(cv, tex):
    e = Escena(cv, CAM, _llums(), ambient=0.0)
    zn = CAM.pos[2] + 60
    esp, _ = tex['espai']
    # ── l'espai, molt al fons (es veu pel vidre) ──
    ZE = 1500
    e.quad('espai', (-1300, 700, ZE), (2200, 700, ZE), (2200, -900, ZE), (-1300, -900, ZE),
           tex=(esp, (0, 0, esp.width, esp.height)))
    # ── la piscina central, a sota del tros de vidre del terra ──
    x0, x1, z0, z1 = POU
    yb = POU_FONS

    def rajola(s, t, P, base=3.4):
        return base + (0.9 if s % 14 < 1.2 or t % 14 < 1.2 else 0) + (hr(int(s // 14), int(t // 14), 4) - 0.5) * 0.4
    e.quad('pou', (x0 - 200, yb, z1 + 200), (x1 + 200, yb, z1 + 200), (x1 + 200, yb, z0 - 200), (x0 - 200, yb, z0 - 200),
           ramp=TURQ, lvl=lambda s, t, P: rajola(s, t, P, 3.6) - (2.2 if abs(P[0] - 470) < 3 else 0))
    e.quad('pou', (x0, 0, z1), (x1, 0, z1), (x1, yb, z1), (x0, yb, z1), ramp=TURQ, dues_cares=True,
           lvl=lambda s, t, P: rajola(s, t, P, 2.6) + t / 260)
    e.quad('pou', (x1, 0, z0), (x1, 0, z1), (x1, yb, z1), (x1, yb, z0), ramp=TURQ, dues_cares=True,
           lvl=lambda s, t, P: rajola(s, t, P, 2.0) + t / 300)
    for k in range(5):                                            # l'escala cromada de la piscina, a la paret
        yy = -260 - k * 28
        e.caixa('pou', 486, 506, yy - 2, yy, z1 - 12, z1 - 1, CROM, 5.4)
    e.caixa('pou', 484, 487, yb, -230, z1 - 12, z1 - 9, CROM, 5.6)
    e.caixa('pou', 505, 508, yb, -230, z1 - 12, z1 - 9, CROM, 4.2)
    # ── la paret de vidre (z = ZG): els muntants i el travesser d'or, i el sòcol; i el sostre ──
    e.quad('sostre', (-600, HC, zn), (XM, HC, zn), (XM, HC, ZG), (-600, HC, ZG), ramp=MARB, dues_cares=True,
           lvl=lambda s, t, P: 4.6 - (1.4 if P[0] % 128 < 2 or P[2] % 128 < 2 else 0))
    for k in range(-5, 7):
        x = k * 112 + 20
        e.caixa('vidre', x - 3, x + 3, 0, HC, ZG - 3, ZG + 3, ORP, 4.2,
                cares={'davant': {'ramp': ORP, 'lvl': lambda s, t, P: 4.6 + (1.2 if s < 1.5 else -1.0 if s > 4.5 else 0)},
                       'esquerra': {'ramp': ORP, 'lvl': 5.4}, 'dreta': {'ramp': ORP, 'lvl': 3.0}})
    e.caixa('vidre', -600, XM, 168, 172, ZG - 3, ZG + 3, ORP, 4.6,
            cares={'davant': {'ramp': ORP, 'lvl': lambda s, t, P: 5.0 - t * 0.6}})
    e.caixa('vidre', -600, XM, 0, 10, ZG - 6, ZG, MARB, 6.0,
            cares={'davant': {'ramp': MARB, 'lvl': lambda s, t, P: 6.2 - t * 0.12}, 'dalt': {'ramp': ORP, 'lvl': 5.0}})
    e.caixa('vidre', -600, XM, HC - 8, HC, ZG - 6, ZG, MARB, 5.0,
            cares={'davant': {'ramp': ORP, 'lvl': lambda s, t, P: 4.6 - t * 0.3}})
    # el reflex del vidre: franges diagonals molt suaus
    e.claror((-600, HC, ZG - 0.5), (XM, HC, ZG - 0.5), (XM, 0, ZG - 0.5), (-600, 0, ZG - 0.5), (190, 200, 220),
             lambda s, t: 0.08 if 20 < (s + t * 0.7) % 300 < 70 else 0.03 if 90 < (s + t * 0.7) % 300 < 100 else 0)
    # ── la paret de marbre de la dreta (x = XM) ──
    e.quad('marbre', (XM, HC, -200), (XM, HC, ZG), (XM, 0, ZG), (XM, 0, -200), ramp=MARB, dues_cares=True,
           lvl=_marbre(5.4))
    # ── el terra de marbre, amb el forat del tros de vidre ──
    e.quad('terra', (-600, 0, ZG), (XM, 0, ZG), (XM, 0, zn), (-600, 0, zn), ramp=MARB, lvl=_terra,
           forma=lambda s, t: not _al_pou(s - 600, ZG - t, 0))
    _or_terra(e)
    e.foscor('racons', (-600, 0.5, ZG), (XM, 0.5, ZG), (XM, 0.5, zn), (-600, 0.5, zn),
             lambda s, t: max(0.3 * max(0.0, 1 - t / 30), 0.35 * max(0.0, 1 - (XM + 600 - s) / 40)))
    # el marc d'or del tros de vidre, i el vidre (reflexos)
    for a, b, c, d in ((x0 - 5, x1 + 5, z1, z1 + 5), (x0 - 5, x1 + 5, z0 - 5, z0), (x0 - 5, x0, z0, z1),
                       (x1, x1 + 5, z0, z1)):
        e.caixa('pou_marc', a, b, -1, 1.2, c, d, ORP, 4.6, cares={'dalt': {'ramp': ORP, 'lvl': 5.2}})
    e.claror((x0, 0.3, z1), (x1, 0.3, z1), (x1, 0.3, z0), (x0, 0.3, z0), (230, 255, 250),
             lambda s, t: 0.28 if 10 < (s + t * 1.2) % 50 < 16 else 0.06)
    # ── l'aquari, contra la paret de marbre: el peu, el vidre (tres cares), el marc d'or ──
    _aquari(e, tex)
    # ── la cadira i la taula ──
    tx, tz, ang, tl, tf, th = TAULA
    e.foscor('ombra', (tx - 130, 0.6, tz + 70), (tx + 110, 0.6, tz + 70), (tx + 110, 0.6, tz - 70),
             (tx - 130, 0.6, tz - 70), lambda s, t: 0.4 * max(0.0, 1 - ((s - 130) / 120) ** 2 - ((t - 70) / 62) ** 2) * 1.6)
    pla = tex['pla']
    e.sprite('cadira', pla.crop((248, 92, 304, 178)), (28, 84), (CADIRA[0], 0, CADIRA[1]))
    _taula(e, tex)
    # ── el panell del preu, penjat del sostre ──
    px, pz, py = PANELL
    p0, pyy, pw, ph = PL.PANEL
    for dx in (-30, 30):
        e.cable('panell', [(px + dx, HC, pz), (px + dx, py + 52, pz)], CROM, 4.4, gruix=0.7)
    e.caixa('panell', px - 48, px + 48, py, py + 52, pz, pz + 6, NEGRE, 1.6,
            cares={'davant': {'tex': (pla, (p0 - 3, pyy - 3, p0 + pw + 3, pyy + ph + 3))},
                   'dalt': {'ramp': ORP, 'lvl': 5.4}, 'esquerra': {'ramp': ORP, 'lvl': 4.0}})
    # ── el focus d'estudi i el seu raig ──
    _focus(e)
    # ── primer pla: la càmera d'anunci al trípode, a contrallum ──
    _camera_anunci(e, tex)
    return e


def _aquari(e, tex):
    x0, x1, z0, z1, y0, y1 = AQ
    e.foscor('ombra', (x0 - 30, 0.6, z1), (x1, 0.6, z1), (x1, 0.6, z0 - 26), (x0 - 30, 0.6, z0 - 26),
             lambda s, t: 0.35 * min(1.0, min(s, t) / 16))
    e.caixa('aquari', x0 - 4, x1, 0, y0, z0 - 4, z1, MARB, 5.6,
            cares={'davant': {'ramp': MARB, 'lvl': lambda s, t, P: 5.8 - (1.4 if t < 3 or t > y0 - 3 else 0)
                              - (2.4 if 18 < s < 70 and 14 < t < 28 else 0)},
                   'esquerra': {'ramp': MARB, 'lvl': lambda s, t, P: 4.6 - (1.2 if t < 3 or t > y0 - 3 else 0)}})
    e.quad('aquari', (x0 + 14, y0 - 12, z0 - 4.4), (x1 - 18, y0 - 12, z0 - 4.4), (x1 - 18, y0 - 26, z0 - 4.4),
           (x0 + 14, y0 - 26, z0 - 4.4), ramp=ORP, lvl=lambda s, t, P: 4.8 - t * 0.08)          # la placa AQUA
    aq = tex['aquari']
    ax0, ay0, ax1, ay1 = PL.AQ
    e.quad('aquari_costat', (x0, y1, z1), (x0, y1, z0), (x0, y0, z0), (x0, y0, z1), ramp=AIGUA,
           lvl=lambda s, t, P: 4.4 - t * 0.016 + (0.8 if 6 < (s - t * 0.35) % 60 < 10 else 0))
    e.quad('aquari_davant', (x0, y1, z0), (x1, y1, z0), (x1, y0, z0), (x0, y0, z0), tex=(aq, (ax0, ay0, ax1, ay1)))
    e.caixa('aquari', x0 - 4, x1, y1, y1 + 10, z0 - 4, z1, ORP, 4.0,
            cares={'davant': {'ramp': ORP, 'lvl': lambda s, t, P: 5.2 - t * 0.2},
                   'esquerra': {'ramp': ORP, 'lvl': lambda s, t, P: 3.6 - t * 0.2}, 'dalt': {'ramp': ORP, 'lvl': 5.0}})
    for x, z in ((x0 - 2, z0 - 2), (x1 - 2, z0 - 2), (x0 - 2, z1 - 4)):
        e.caixa('aquari', x - 2, x + 2, y0, y1, z - 2, z + 2, ORP, 4.6)
    e.claror((x0 - 60, 0.4, z0 - 2), (x1, 0.4, z0 - 2), (x1, 0.4, z0 - 90), (x0 - 60, 0.4, z0 - 90), (120, 200, 255),
             lambda s, t: 0.18 * max(0.0, 1 - t / 90) * min(1.0, s / 40))


def _taula(e, tex):
    tx, tz, ang, tl, tf, th = TAULA
    pla = tex['pla']
    x0, x1, yb, yf, yg = PL.DESK
    # el cos (una mica entrat) i el sobre lacat amb el cantell d'or
    e.caixa_girada('taula', tx, tz + 4, tl - 18, tf - 14, th - 4, ang, MARB, 5.0,
                   cares={'davant': {'tex': (pla, (x0 + 10, yf + 4, x1 - 10, yg))},
                          'esquerra': {'ramp': MARB, 'lvl': lambda s, t, P: 4.0 - (1.0 if P[1] < 4 else 0)},
                          'dreta': {'ramp': MARB, 'lvl': 3.4}})
    e.caixa_girada('taula', tx, tz, tl, tf, 4, ang, ORP, 4.4, y0=th - 4,
                   cares={'davant': {'ramp': ORP, 'lvl': lambda s, t, P: 5.4 - t * 0.6},
                          'esquerra': {'ramp': ORP, 'lvl': 4.0},
                          'dalt': {'ramp': MARB, 'lvl': lambda s, t, P: 7.0 - t * 0.02}})
    c, s_ = math.cos(ang), math.sin(ang)

    def P(lx, y, lz):
        return (tx + lx * c - lz * s_, y, tz + lx * s_ + lz * c)
    # damunt: l'interfon de la Sra. Pell, la carpeta granat i el portaploma d'or
    e.caixa_girada('taula', *P(-60, 0, 8)[::2], 18, 12, 6, ang, NEGRE, 2.0, y0=th + 0.1,
                   cares={'dalt': {'ramp': NEGRE, 'lvl': lambda s, t, P: 2.6 + (3.0 if s > 14 and t < 4 else 0)}})
    gr = [(60, 20, 30), (100, 36, 48), (140, 60, 70)]
    e.caixa_girada('taula', *P(30, 0, 6)[::2], 34, 24, 1.5, ang + 0.15, gr, 1.4, y0=th + 0.1)
    e.cable('taula', [P(66, th, -4), P(66, th + 10, -4), P(70, th + 18, -2)], ORP, 4.6, gruix=2.0)


def _focus(e):
    fx, fz, fh = FOCUS
    tx, tz = TAULA[0], TAULA[1]
    for a in (0.3, 2.4, 4.4):                                     # el trípode
        e.cable('focus', [(fx, fh - 30, fz), (fx + math.cos(a) * 34, 0.5, fz + math.sin(a) * 34)], CROM, 4.6, gruix=1.4)
    e.cable('focus', [(fx, fh - 30, fz), (fx, fh - 4, fz)], CROM, 5.2, gruix=2.2)
    # el cap: un cilindre negre que mira cap a la taula
    d = (tx - fx, 60 - fh, tz - fz)
    n = math.sqrt(sum(k * k for k in d))
    d = tuple(k / n for k in d)
    A = (fx - d[0] * 14, fh - d[1] * 14, fz - d[2] * 14)
    B = (fx + d[0] * 12, fh + d[1] * 12, fz + d[2] * 12)
    e.tub('focus', A, B, 11, NEGRE, 2.0, llum_dir=(-0.6, 1.0))


def _raig(cv, e):
    """El raig del focus: una banda de llum càlida que va del cap del focus fins a la taula (en pantalla), i la taca
    de llum al sobre. Només on es veu el que hi ha darrere (no damunt la càmera del primer pla)."""
    fx, fz, fh = FOCUS
    tx, tz, ang, tl, tf, th = TAULA
    a = e.cam.projecta((fx, fh, fz))
    b = e.cam.projecta((tx, th, tz))
    ax, ay = b[0] - a[0], b[1] - a[1]
    L = math.hypot(ax, ay)
    P = cv.P
    prim = {i for i, sid in enumerate(e.ids) if sid in ('primer_pla', 'focus')}
    for y in range(BARRA, BOTTOM + 1):
        for x in range(0, W):
            if e.amo[y * cv.w + x] in prim:
                continue
            px, py = x - a[0], y - a[1]
            t = (px * ax + py * ay) / (L * L)
            if t < 0.08 or t > 1.25:
                continue
            perp = abs(px * ay - py * ax) / L
            w = 5 + t * 44
            if perp < w:
                k = 0.22 * (1 - perp / w) ** 0.7 * min(1.0, t * 5) * (1 - max(0.0, t - 1) * 4)
                o = P[x, y]
                P[x, y] = (int(o[0] + (255 - o[0]) * k), int(o[1] + (248 - o[1]) * k), int(o[2] + (220 - o[2]) * k), 255)
    # la cara del focus, encesa
    c = e.cam.projecta((fx + (tx - fx) * 0.02, fh - 1, fz + (tz - fz) * 0.02))
    cv.glow(c[0] + 2, c[1] + 1, 16, (255, 250, 220), 0.6)


def _camera_anunci(e, tex):
    cx, cz = CAMD
    top = 118
    for a in (1.3, 3.0, 5.0):
        e.cable('primer_pla', [(cx, top - 10, cz), (cx + math.cos(a) * 46, 0.5, cz + math.sin(a) * 46)], CROM, 2.0,
                gruix=2.6)
    e.cable('primer_pla', [(cx, top - 10, cz), (cx, top, cz)], CROM, 2.4, gruix=4)
    pla = tex['pla']
    ccx, ccy = PL.CAMERA
    e.sprite('primer_pla', _fosc(pla.crop((ccx - 32, ccy - 20, ccx + 36, ccy + 16))), (34, 34), (cx, top - 4, cz))


def _fosc(img, k=0.55):
    """Un dibuix pla a contrallum (més fosc i fred): per al primer pla."""
    px = img.load()
    out = img.copy()
    po = out.load()
    for y in range(img.height):
        for x in range(img.width):
            r, g, b, a = px[x, y]
            if a:
                po[x, y] = (int(r * k * 0.9), int(g * k * 0.95), int(b * k), a)
    return out


# ─── Composició ────────────────────────────────────────────────────────────

@functools.lru_cache(maxsize=None)
def _textures():
    return {'espai': _espai(), 'pla': _pla(), 'aquari': _aquari_pla(0.0)}


def _render():
    cv = Canvas(light=LIGHT)
    e = escena(cv, _textures())
    if _ST['focus']:
        _raig(cv, e)
    _vinyeta(cv)
    cv.rect(0, 0, W - 1, BARRA - 1, [(0, 0, 0)], 0, lit=0)        # les franges de cinema
    cv.rect(0, BOTTOM + 1, W - 1, H - 1, [(0, 0, 0)], 0, lit=0)
    return cv.img, e


def _vinyeta(cv, k=0.42):
    """Enfosqueix les cantonades del quadre (sobretot les de baix): el pla de cinema."""
    cx, cy = W / 2, (BARRA + BOTTOM) / 2 - 20
    P = cv.P
    for y in range(BARRA, BOTTOM + 1):
        for x in range(W):
            d = ((x - cx) / (W * 0.62)) ** 2 + ((y - cy) / ((BOTTOM - BARRA) * 0.78)) ** 2
            if d <= 0.55:
                continue
            m = 1 - min(k, (d - 0.55) * 0.6)
            o = P[x, y]
            P[x, y] = (int(o[0] * m), int(o[1] * m), int(o[2] * m), 255)


@functools.lru_cache(maxsize=None)
def _base():
    return _render()


@functools.lru_cache(maxsize=None)
def _apagat():
    _ST['focus'] = False
    try:
        img, _ = _render()
    finally:
        _ST['focus'] = True
    return _diff(img, _base()[0])


def bg(cv):
    img, _ = _base()
    cv.img.paste(img)
    cv.P = cv.img.load()


def focus_apagat(cv):
    """El focus apagat: sense raig ni llum a la taula."""
    cv.img.alpha_composite(_apagat())


def _preu(valor):
    def fn(cv):
        _, e = _base()
        p = Canvas(light=PL.LIGHT, transparent=True)
        x0, y0, w, h = PL.PANEL
        panell_valor(p, x0, y0, w, h, valor, amunt=True)
        cv.img.alpha_composite(e.capa(p.img, {'panell'}))
    return fn


PROPS = {'preu46': _preu(46), 'preu48': _preu(48), 'focus_apagat': focus_apagat}


def _frames_peixos(n=24):
    _, e = _base()
    a0 = _textures()['aquari']
    return [e.capa(_diff(_aquari_pla(i / n), a0), {'aquari_davant'}) for i in range(n)]


def _frames_estrelles():
    _, e = _base()
    img, bright = _textures()['espai']
    return [e.capa(f, {'espai'}) for f in estrelles_frames(img, list(bright), n=10, seed=2)]


ANIMS = {'peixos': {'frames': _frames_peixos, 'frameDuration': 140},
         'estrelles': {'frames': _frames_estrelles, 'frameDuration': 300}}


def _amo(ids):
    def mask(x, y):
        _, e = _base()
        return e.ids[e.amo[y * e.cv.w + x]] in ids
    return mask


# ─── Geometria (coordenades de sala, projectades) ────────────────────────────

def _p(x, z, y=0.0):
    u, v, _ = CAM.projecta((x, y, z))
    return round(u), round(v)


def _escala_a(v):
    lo, hi = 1.0, 3000.0
    for _ in range(60):
        z = (lo + hi) / 2
        if CAM.projecta((340, 0, z))[1] > v:
            lo = z
        else:
            hi = z
    return CAM.escala((340, 0, (lo + hi) / 2))


def _vpeu(x, z):
    return CAM.projecta((x, 0, z))[1]


def _taula_front():
    """La y de pantalla del cantó de davant de la taula (la base de la capa del davant)."""
    tx, tz, ang, tl, tf, th = TAULA
    c, s_ = math.cos(ang), math.sin(ang)
    return max(_vpeu(tx + lx * c - lz * s_, tz + lx * s_ + lz * c) for lx in (-tl / 2, tl / 2) for lz in (-tf / 2,))


# en Verne, darrere la taula; en Dividend, al costat del tros de vidre
_VERNE = _p(CADIRA[0] - 6, CADIRA[1] - 30)
_DIVIDEND = _p(POU[0] - 30, (POU[2] + POU[3]) / 2 - 10)

FRONT = [
    {'id': 'davant', 'mask': _amo({'taula'}), 'baseline': round(_taula_front()), 'zIndex': 20},
    {'id': 'davant_camera', 'mask': _amo({'primer_pla'}), 'baseline': 999, 'zIndex': 20},
]

# (cinemàtica: no s'hi camina, però el terra i l'escala diuen la mida dels personatges on són)
_V_FONS, _V_PROP = round(_vpeu(300, 380)), BOTTOM - 2
_WALK = [(0, _V_FONS), (W - 1, _V_FONS), (W - 1, _V_PROP), (0, _V_PROP)]

GEOMETRIA = {
    'things': {},                       # cinemàtica: res per clicar
    'spawns': {'verne': _VERNE, 'dividend': _DIVIDEND},
    'walkable': _WALK,
    'floorSquash': 0.35,
    'characterShadow': {'enabled': True, 'color': '#3a3040', 'alpha': 0.35, 'squash': 0.35, 'core': 0.6,
                        'light': {'x': _p(FOCUS[0], FOCUS[1])[0], 'y': _p(FOCUS[0], FOCUS[1])[1], 'stretch': 0.7,
                                  'reach': 160}},
    'regions': [{'id': 'perspectiva', 'active': True, 'scaleEnabled': True, 'scaleWalkSpeed': True,
                 'scaleTop': round(_escala_a(_V_FONS - 2), 3), 'scaleBottom': round(_escala_a(_V_PROP + 2), 3),
                 'points': [(0, round(_V_FONS) - 2), (W - 1, round(_V_FONS) - 2), (W - 1, round(_V_PROP) + 2),
                            (0, round(_V_PROP) + 2)]}],
    # La llum de la sala sobre els personatges (characterLights del motor): el despatx de l'anunci: la llum perfecta
    # de plató, l'aquari, Terra-2 pel vidre i el focus.
    'characterLights': {
        'ambient': '#b8b4c0',
        'lights': [
            # l'anunci, l'aquari, Terra-2 pel vidre i el focus, que s'apaga quan es veu el decorat `focus_apagat`
            *[llum_personatges(CAM, l.pos, l.r, c, k, **x) for l, c, k, x in
              zip(_llums(), ('#fff4e8', '#78d0ff', '#ffd8a8', '#fff8e8'), (0.25, 0.35, 0.2, 0.35),
                  ({}, {}, {}, {'whenPropHidden': 'focus_apagat'}))],
        ],
    },
}
