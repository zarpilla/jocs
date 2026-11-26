"""
L'Última Arrel — el pròleg (640×360). Cinemàtica a pantalla sencera, sense res clicable.

És el mateix pla que la portada (portada.py: el roure de la porta petita al capvespre, i a sota el tall del terra amb
la Xarxa Miceli), sense el títol: «Comença» esvaeix el títol i s'hi passa amb un tall net. L'Espora torna a casa: entra
per la dreta, s'atura a mirar el cartell del Bosc 2.0, va fins a la porta del roure i hi entra (la porta s'obre, amb la
llum càlida de la centraleta a dins, i es torna a tancar). Després, el rètol de temps i la vora del bosc.

  - PROPS `porta_oberta`: la porta oberta (porta_oberta de vora_comu, amb la llum càlida del capvespre). El guió
    (rooms/proleg_roure.json) l'amaga en començar i la mostra un moment quan l'Espora entra.
  - ANIMS `pols`: els polsos de llum pels fils de sota terra, com a la portada.
"""
import numpy as np
from PIL import Image

import hd640  # noqa: F401  (abans que cap hd.rooms: posa la llibreria a 640×360)
from hd.rooms.comu import _diff
from hd640.rooms.vora_comu import EARTH, Mode, Llenc, porta_oberta
import hd640.rooms.portada as portada

LIGHT = portada.LIGHT
OY = portada.OY


# La Xarxa Miceli, tallada (tasca 040): passat CUT_X, els fils principals que van cap al nord (la tanca, a la dreta)
# s'apaguen, i al tall hi ha la terra remoguda. Els polsos de llum s'hi aturen.
CUT_X = 468
FILS_TALLATS = (2, 3, 6, 8)


def _tall_xarxa(img):
    a = np.asarray(img.convert('RGBA')).astype(np.float32)
    h, w = a.shape[:2]
    mask = np.zeros((h, w), np.float32)
    for k in FILS_TALLATS:
        p = portada.FILS[k]
        for i in range(400):
            x, y = portada._bez(p, i / 400)
            if x <= CUT_X:
                continue
            X, Y = int(x), int(y) + OY
            for dy in range(-9, 10):
                for dx in range(-9, 10):
                    if 0 <= X + dx < w and 0 <= Y + dy < h:
                        v = max(0.0, 1 - (dx * dx + dy * dy) ** 0.5 / 9.5)
                        mask[Y + dy, X + dx] = max(mask[Y + dy, X + dx], v)
    rgb = a[..., :3]
    lum = rgb.mean(axis=2, keepdims=True)
    # el turquesa apagat: sense color, més fosc (com un fil mort)
    mort = lum * np.array([0.5, 0.45, 0.42]) * 0.7
    turq = np.clip((rgb[..., 1:2] + rgb[..., 2:3]) / 2 - rgb[..., 0:1], 0, 255) / 255
    k = (mask[..., None] * np.clip(turq * 3.0, 0, 1))
    a[..., :3] = rgb * (1 - k) + mort * k
    out = Image.fromarray(a.astype(np.uint8), 'RGBA').copy()
    # el tall: terra remoguda i els caps dels fils esfilagarsats, foscos
    cv = Llenc(OY, LIGHT, img=out)
    for k in FILS_TALLATS:
        p = portada.FILS[k]
        t = next(i / 400 for i in range(400) if portada._bez(p, i / 400)[0] > CUT_X)
        x, y = portada._bez(p, t)
        cv.disc(x + 2, y, 6, 4, EARTH, 1.4, lit=0)
        for j in range(4):                                       # els caps esfilagarsats
            cv.flat(x - 3 - j, y - 1 + (j % 3) - 1, (60, 120, 116) if j < 2 else (40, 70, 70))
    return cv.img


def bg(cv):
    portada.bg(cv)
    cv.img = _tall_xarxa(cv.img)
    cv.P = cv.img.load()


def _pols_tallats():
    """Els polsos de la portada, que s'aturen al tall: passat CUT_X (sota el terra) no n'hi arriba cap."""
    frames = []
    for f in portada._pols_frames():
        a = np.asarray(f).copy()
        a[portada.CUT + OY:, CUT_X:, 3] = 0
        frames.append(Image.fromarray(a, 'RGBA'))
    return frames


def _prop(fn):
    """Un prop: el que canvia en dibuixar-lo damunt del fons de la portada, i res més."""
    def draw(pc):
        base = portada._fons()
        cv = Llenc(OY, LIGHT, img=base.copy())
        fn(cv)
        d = _diff(cv.img, base)
        pc.img.alpha_composite(Image.fromarray(np.asarray(d).copy(), 'RGBA'))
        pc.P = pc.img.load()
    return draw


PROPS = {
    # la llum de dins, càlida com la de la centraleta del tall (la portada té el fanalet turquesa)
    'porta_oberta': _prop(lambda cv: porta_oberta(cv, Mode('capvespre'))),
}

ANIMS = {
    'pols': {**portada.ANIMS['pols'], 'frames': _pols_tallats},
}

# L'Espora camina per l'herba de davant del roure (la porta: x 205..239, el graó a y ≈ 200 de pantalla). Entra de fora
# de la pantalla, per la dreta (el guió el posa a x = 654).
WALK = [(150, 196), (639, 196), (639, 213), (150, 213)]

GEOMETRIA = {
    'things': {},
    'spawns': {'espora': (600, 207)},
    'walkable': WALK,
    # el sol es pon a l'esquerra, entre els troncs: les ombres, llargues, cap a la dreta (com a la vora del bosc)
    'characterShadow': {'enabled': True, 'color': '#1c0e14', 'alpha': 0.42, 'squash': 0.28, 'core': 0.6,
                        'light': {'x': 1, 'y': 0.08, 'direction': True, 'stretch': 1.0}},
    'characterLights': {
        'ambient': '#9c8c98',
        'lights': [{'x': 40, 'y': 150, 'radius': 520, 'color': '#ffa868', 'intensity': 0.6},
                   {'x': 251, 'y': 158, 'radius': 60, 'color': '#5ee6e0', 'intensity': 0.35}],
    },
}
