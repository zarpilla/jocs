"""
Aigua Verne — `proleg_terra2` (L, cinemàtica): el primer pla del pròleg, Terra-2 de lluny.

És el mateix pla que la portada, sense el títol: «Comença» esvaeix el títol i hi entra amb un tall net. Cada frase
de rooms/proleg_terra2.json engega el seu tros d'animació amb una indicació d'escena (`{"prop": "pou", "anim":
"pou_on"}`), de fons i sense detall. Tot passa fora del quadre del text del narrador (el centre de la pantalla):

  - `pou_on` (bucle): la bomba de Verne del pou cabeceja, i a cada cabotada un glop d'aigua blava corre per la
    canonada de terra fins a la base de la Canonada;
  - `canonada_puja` (un cop) i `canonada_on` (bucle): l'aigua puja per la Canonada a polsos fins al dipòsit
    orbital, que s'il·lumina de blau cada vegada que n'arriba un;
  - `nau_apaga` (un cop): la Cantimplora tus pels motors, la cabina parpelleja i s'apaga, i després la rampa;
  - `germanes_surten` (un cop): l'Iri (coure i marró) i la Vet (monyo negre i blau) baixen per la rampa i se'n
    van pel corriol cap a la posta, cada cop més petites, fins que la pols se les empassa. En Diu surt a la
    rampa, s'hi asseu i les mira marxar.

Cada capa és la diferència amb el fons (portada.diff): com a la portada, es dibuixa sobre una còpia del fons.
"""
import functools
import json
import math
from pathlib import Path

import hd640  # noqa: F401  (abans de cap hd.rooms: posa la llibreria a 640×360)
from PIL import Image

from hd.pix import Canvas, Light, W, H, hr, mix
import hd640.rooms.portada as portada
from hd640.rooms.portada import CAN_X, HOR, TANK, CAM

# Art a 1×, com la portada (en 3D).

LIGHT = Light(ambient=0.0, vignette=None, floor_fade=None)
ZT = 0.1                                   # segons per fotograma de les animacions del pròleg


def bg(cv):
    portada.bg(cv)


@functools.lru_cache(maxsize=None)
def _variant(**kw):
    cv = Canvas(light=LIGHT)
    portada.scene(cv, **kw)
    return cv.img.copy()


def _base():
    return portada.base_img()


def _empty():
    return [Canvas(light=LIGHT, transparent=True).img]


def _canvas(img=None):
    return Canvas(light=LIGHT, img=(img or _base()).copy())


def _blend(cv, x, y, col, a):
    x, y = int(round(x)), int(round(y))
    if 0 <= x < cv.w // cv.S and 0 <= y < cv.h // cv.S and a > 0.02:
        cv.flat(x, y, mix(cv.get(x, y), col, min(1.0, a)))


def _ease(t):
    t = max(0.0, min(1.0, t))
    return t * t * (3 - 2 * t)


# ─── La bomba del pou ───────────────────────────────────────────────────────

POU_N = 15                                  # una cabotada (1,5 s)
BLUE = (70, 150, 255)
BLUE_HI = (190, 226, 255)


def _pou_frame(f):
    cv = _canvas(_variant(pump=False))
    portada.bomba_verne(cv, (0.25 + f / POU_N) % 1.0)
    # el glop d'aigua per la canonada de terra, que s'alenteix de lluny
    u = 1 - (1 - f / POU_N) ** 1.4
    x, y = portada.pipe_xy(u)
    cv.glow(round(x), round(y), 7 - round(3 * u), (80, 160, 255), 0.6)
    for j in range(6):
        bx, by = portada.pipe_xy(max(0.0, u - j * 0.012))
        _blend(cv, bx, by, BLUE_HI if j < 2 else BLUE, 0.95 - j * 0.12)
        _blend(cv, bx, by + 1, BLUE, 0.6 - j * 0.08)
    return portada.diff(cv.img)


# ─── La Canonada ────────────────────────────────────────────────────────────
# Un pols surt de la base cada 1,5 s i triga 3 s a arribar al dipòsit (de lluny va més a poc a poc); quan hi
# arriba, el dipòsit fa una claror blava. `canonada_puja` comença sense cap pols (els primers 3 s) i acaba just on
# comença el bucle `canonada_on`.

C_GAP, C_TRIP, C_FLASH = 1.5, 3.0, 1.0
C_Y0, C_Y1 = TANK[1] + 8, HOR - 7


def _pulse(cv, age):
    k = 1 - (1 - age / C_TRIP) ** 1.5
    yc = C_Y1 - (C_Y1 - C_Y0) * k
    s = (yc - C_Y0) / (C_Y1 - C_Y0)                 # 1 a baix, 0 dalt
    w = 1.0 + 2.0 * (yc - (TANK[1] + 6)) / (HOR - 6 - TANK[1] - 6)
    bh = 4 + 8 * s
    cv.glow(CAN_X, round(yc), round(6 + 8 * s), (80, 160, 255), 0.55)
    for y in range(int(yc - bh), int(yc + bh) + 1):
        a = min(1.0, 1.3 * (1 - abs(y - yc) / (bh + 0.5)))
        for x in range(int(CAN_X - w), int(CAN_X + w) + 1):
            _blend(cv, x, y, BLUE_HI if x < CAN_X or abs(y - yc) < 1 else BLUE, a)


def _flash(cv, age):
    k = (1 - age / C_FLASH) ** 1.3
    cv.glow(TANK[0], TANK[1], 40, (110, 180, 255), 0.7 * k)
    cv.glow(TANK[0] - 11, TANK[1] + 1, 12, (170, 220, 255), 0.8 * k)
    cv.glow(CAN_X, TANK[1] + 9, 7, (150, 210, 255), 0.8 * k)


def _canonada_frame(t):
    cv = _canvas()
    starts = [i * C_GAP for i in range(int(t / C_GAP) + 1)]
    for s0 in starts:
        age = t - s0
        if age < C_TRIP:
            _pulse(cv, age)
        elif age < C_TRIP + C_FLASH:
            _flash(cv, age - C_TRIP)
    return portada.diff(cv.img)


def _canonada_puja():
    return [_canonada_frame(i * ZT) for i in range(round(C_TRIP / ZT))]


def _canonada_on():
    return [_canonada_frame(C_TRIP + i * ZT) for i in range(round(C_GAP / ZT))]


# ─── La Cantimplora s'apaga ─────────────────────────────────────────────────

CABIN, NAV, RAMP, EXHAUST = portada.CABIN, portada.NAV, portada.RAMP, portada.EXHAUST
COUGHS = (0.2, 1.0, 1.8)
N_APAGA = 44                               # fins que s'ha esvaït el fum de l'última tos
SMOKE = (118, 106, 104)


def _paste(img, src, box):
    """Copia la caixa `box` (coordenades de sala) de `src` a `img` (a la mida de l'art: S píxels per píxel de sala)."""
    s = img.width // W
    x0, y0, x1, y1 = (v * s for v in box)
    img.paste(src.crop((x0, y0, x1 + s, y1 + s)), (x0, y0))


def _puff(cv, age, seed, big):
    life = 2.4 if big else 1.6
    if not 0 <= age < life:
        return
    q = age / life
    for j in range(6 if big else 4):
        bx = EXHAUST[0] - 1 - age * (6 + j) - j * 1.2 + hr(j, seed) * 2
        by = EXHAUST[1] - age * (4 + 1.5 * j) - hr(j, seed + 1) * 2
        r = (2.0 + age * (3.4 if big else 2.4)) * (0.7 + 0.5 * hr(j, seed + 2))
        alpha = (1.0 if big else 0.8) * (1 - q) ** 1.1
        for y in range(int(by - r), int(by + r) + 1):
            for x in range(int(bx - r), int(bx + r) + 1):
                d = math.hypot(x - bx, y - by) / max(0.5, r)
                if d < 1:
                    k = alpha * (1 - d * d)
                    if hr(x, y, seed, int(age * 10)) < k * 1.6:
                        _blend(cv, x, y, SMOKE if hr(x, y, seed + 3) > 0.3 else (70, 62, 64), 0.6 + 0.4 * k)


def _nau_frame(t):
    dark = _variant(ship_off=True)
    img = _base().copy()
    cabin_on = t < 0.9 or 1.1 <= t < 1.3
    ramp_on = t < 2.5 or 2.6 <= t < 2.7
    nav_on = t < 0.9
    if not cabin_on:
        _paste(img, dark, CABIN)
    if not nav_on:
        _paste(img, dark, NAV)
    if not ramp_on:
        _paste(img, dark, RAMP)
    cv = Canvas(light=LIGHT, img=img)
    flare = any(0 <= t - c < 0.2 for c in COUGHS)
    if flare:
        cv.flat(*EXHAUST, (255, 220, 150))
        cv.glow(*EXHAUST, 4, (255, 150, 60), 0.5)
    elif t >= COUGHS[-1]:
        cv.flat(*EXHAUST, (60, 46, 44))
    for i, c in enumerate(COUGHS):
        _puff(cv, t - c, 90 + i, big=i == len(COUGHS) - 1)
    return portada.diff(cv.img, force=() if nav_on else (NAV,))


def _nau_apaga():
    return [_nau_frame(i * ZT) for i in range(N_APAGA)]


# ─── L'Iri i la Vet se'n van ────────────────────────────────────────────────
# Baixen per la rampa de la comporta (de cara, en 3/4) i agafen el corriol cap a la posta (d'esquena, en 3/4): els
# seus sprites «de lluny», a l'escala que toca a cada distància, a contrallum (gairebé siluetes, amb la vora encesa) i
# amb l'ombra llarga cap a la càmera. Qui passa per darrere de la nau, del primer pla o de la canonada, hi queda tapat.

DUSK_SIL = (26, 18, 24)
ART = Path(__file__).resolve().parents[2].parent / 'placeholder-art'
WALK = {'iri': 0.3, 'vet': 1.1}            # quan comença a baixar cadascuna
RAMP_T = 1.0                               # el que triguen a baixar la rampa
V_PATH = 0.13                              # (el corriol ja va més a poc a poc de lluny: vegeu portada._path_pts)
SHIP_Z = portada.SHIP_C[1]
TAPA_NAU = {'nau', 'cabina_finestres', 'porta', 'rampa'}
TAPA_SEMPRE = {'primer_pla', 'canonada'}


@functools.lru_cache(maxsize=None)
def _sheet(cid, tag):
    """→ ([fotogrames RGBA], peus (x, y)) d'una etiqueta del full d'un personatge."""
    meta = json.loads((ART / cid / f'{cid}.json').read_text())
    feet = json.loads((ART / cid / f'{cid}.character.json').read_text())['feet']
    sheet = Image.open(ART / cid / f'{cid}.png').convert('RGBA')
    frames = list(meta['frames'].values())
    t = next(t for t in meta['meta']['frameTags'] if t['name'] == tag)
    out = []
    for i in range(t['from'], t['to'] + 1):
        f = frames[i]['frame']
        out.append(sheet.crop((f['x'], f['y'], f['x'] + f['w'], f['y'] + f['h'])))
    return out, (feet['x'], feet['y'])


@functools.lru_cache(maxsize=None)
def _path_u():
    us, u = [0.0], 0.0
    while u < 1.0:
        u += V_PATH * ZT
        us.append(min(1.0, u))
    return us


def _lerp3(A, B, k):
    return tuple(a + (b - a) * k for a, b in zip(A, B))


def _where(who, t):
    """→ (punt del món, etiqueta, fotograma, alfa) o None si encara no ha sortit / ja no hi és."""
    tau = t - WALK[who]
    if tau < 0:
        return None
    side = (-6, 0, -4) if who == 'vet' else (0, 0, 0)
    step = int(tau / ZT)
    if tau < RAMP_T:
        P = _lerp3(portada.RAMP_TOP_P, portada.RAMP_FOOT_P, tau / RAMP_T)
        return _lerp3(P, (P[0] + side[0], P[1], P[2] + side[2]), 1.0), 'LlunyWalkDL', step, min(1.0, tau / 0.3)
    us = _path_u()
    i = int((tau - RAMP_T) / ZT)
    if i >= len(us):
        return None
    u = us[i]
    x, z = portada.path_mon(u)
    alpha = 1.0 if u < 0.8 else max(0.0, 1 - (u - 0.8) / 0.2)            # la pols se les empassa
    if alpha <= 0.05:
        return None
    k = min(1.0, u * 8)
    return (x + side[0] * k, 0.0, z + side[2] * k), 'LlunyWalkUL', step, alpha


def _tapat(X, Y, z):
    """Si el píxel (X, Y) de la pantalla és d'alguna cosa que hi ha davant d'un personatge a la profunditat z."""
    e = portada.base_escena()
    if not (0 <= X < W and 0 <= Y < H):
        return True
    sid = e.ids[e.amo[Y * e.cv.w + X]]
    return sid in TAPA_SEMPRE or (sid in TAPA_NAU and z > SHIP_Z - 40)


def _figura(cv, cid, P, tag, step, alpha, silueta=0.42):
    frames, (fx, fy) = _sheet(cid, tag)
    img = frames[step % len(frames)]
    k = CAM.escala(P)
    u, v, z = CAM.projecta(P)
    w, h = max(1, round(img.width * k)), max(1, round(img.height * k))
    im = img.resize((w, h), Image.Resampling.BOX)
    ox, oy = round(u - fx * k), round(v - fy * k)
    # l'ombra llarga, cap a la càmera i a la dreta (el sol és darrere, a l'esquerra)
    L = max(2, round(44 * k))
    for j in range(L):
        sx, sy = u + j * 0.62, v + j * 0.26
        rw = max(1.0, 9 * k * (1 - j / L * 0.4))
        for dx in range(int(-rw), int(rw) + 1):
            X, Y = round(sx + dx), round(sy)
            if not _tapat(X, Y, z):
                _blend(cv, X, Y, (20, 12, 14), 0.32 * alpha * (1 - j / L))
    src = im.load()
    for y in range(h):
        first = True
        for x in range(w):
            r, g, b, a = src[x, y]
            if a < 100:
                continue
            X, Y = ox + x, oy + y
            if _tapat(X, Y, z):
                first = False
                continue
            col = mix((r, g, b), DUSK_SIL, silueta)
            if first:                                                       # la vora que encén la posta
                col = mix(col, (255, 190, 120), 0.45)
                first = False
            _blend(cv, X, Y, col, alpha)


DIU_OUT, DIU_SIT = 3.0, 4.4
DIU_SPOT_P = portada.ship_p((portada.HATCH[0] + portada.HATCH[1]) / 2 + 22, 0, -portada.SHIP_R - portada.RAMP_LEN + 4)


def _diu(cv, t):
    """En Diu surt a la comporta, baixa la rampa i s'asseu al peu, mirant cap on se'n van (la cua que va i ve)."""
    if t < DIU_OUT:
        return
    k = _ease((t - DIU_OUT) / (DIU_SIT - DIU_OUT))
    if k < 1:
        P = _lerp3(portada.RAMP_TOP_P, DIU_SPOT_P, k)
        _figura(cv, 'diu', P, 'LlunyWalkL', int(t / ZT), min(1.0, (t - DIU_OUT) / 0.3), silueta=0.3)
    else:
        _figura(cv, 'diu', DIU_SPOT_P, 'LlunyIdleL', int(t / ZT / 2), 1.0, silueta=0.3)


def _germanes_frame(t):
    cv = _canvas(_variant(ship_off=True))
    people = [(w, _where(w, t)) for w in ('iri', 'vet')]
    people = [(w, s) for w, s in people if s]
    for w, (P, tag, step, alpha) in sorted(people, key=lambda p: -p[1][0][2]):   # de lluny a prop
        _figura(cv, w, P, tag, step, alpha)
    _diu(cv, t)
    # la nau ja és apagada (la capa «nau» de sota): aquí només hi van elles i en Diu
    return portada.diff(cv.img, base=_variant(ship_off=True))


def _germanes_surten():
    n = round((max(WALK.values()) + RAMP_T) / ZT) + len(_path_u()) + 5     # fins que la pols se les ha empassat
    return [_germanes_frame(i * ZT) for i in range(n)]


PROPS = {}

ANIMS = {
    'pols': portada.POLS,
    'llums': portada.LLUMS,
    'pou': {'frames': _empty, 'frameDuration': 1000, 'loop': False, 'zIndex': 2},
    'pou_on': {'frames': lambda: [_pou_frame(f) for f in range(POU_N)], 'frameDuration': round(ZT * 1000),
               'prop': 'pou'},
    'canonada': {'frames': _empty, 'frameDuration': 1000, 'loop': False, 'zIndex': 2},
    'canonada_puja': {'frames': _canonada_puja, 'frameDuration': round(ZT * 1000), 'loop': False,
                      'prop': 'canonada'},
    'canonada_on': {'frames': _canonada_on, 'frameDuration': round(ZT * 1000), 'prop': 'canonada'},
    'nau': {'frames': _empty, 'frameDuration': 1000, 'loop': False, 'zIndex': 2},
    'nau_apaga': {'frames': _nau_apaga, 'frameDuration': round(ZT * 1000), 'loop': False, 'prop': 'nau'},
    'germanes': {'frames': _empty, 'frameDuration': 1000, 'loop': False, 'zIndex': 3},
    'germanes_surten': {'frames': _germanes_surten, 'frameDuration': round(ZT * 1000), 'loop': False,
                        'prop': 'germanes'},
}

GEOMETRIA = {'things': {}, 'spawns': {}}
