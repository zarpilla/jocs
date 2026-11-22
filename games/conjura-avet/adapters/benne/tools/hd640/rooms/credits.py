"""
La Conjura de l'Avet — els crèdits (cinemàtica del final, pantalla sencera de 640×360). EN 3D, a 1×: el pla de la
portada (avet_pla_comu.py: el carrer de `mur_avet` amb més cel), de nit, a la primavera.

Una nit clara i tranquil·la: la lluna i les estrelles; l'absis amb les finestres enceses; el mur arreglat, l'arbre
florit de l'hort, les rodanxes de l'avet apilades i, al costat de les arrels velles (amb molsa), el plançó d'avet
amb la cinta, el segell vermell i la post d'«AVET». Herba i flors al primer pla.
ANIMS: `estels` (les estrelles fan pampallugues) i `cuques` (cuques de llum entre l'herba i el plançó).
"""
import functools
import math

import numpy as np
from PIL import Image

import hd640  # noqa: F401
from hd640.rooms import avet_comu as A
from hd640.rooms import avet_pla_comu as PL
from hd640.rooms.avet_comu import Estat, W, H, diff

LIGHT = None
CAM = PL.CAM_CINE
ESTAT = Estat(llum='nit', arbre='cap', forat='vell', mur='arreglat', branques='cap', cam=CAM, h=H,
              extres=('lluna', 'florit', 'rodanxes', 'forat_gran', 'planco', 'segell_planco', 'rotul', 'abeurador',
                      'herbes'))


def _base():
    return A.render(ESTAT)


def bg(cv):
    cv.img.paste(_base()[0])
    cv.P = cv.img.load()


PROPS = {}


@functools.lru_cache(maxsize=None)
def _estels(n=12):
    """Algunes estrelles (les del fons) s'apaguen i s'encenen a estones."""
    img, v = _base()
    a = np.asarray(img)
    sky = np.zeros((H, W), bool)
    sky[:v.h] = v.own == v.idx('cel')
    lum = a[..., :3].astype(int).sum(-1)
    ys, xs = np.nonzero(sky & (lum > 380))
    rng = np.random.default_rng(3)
    fase = rng.integers(0, n, len(ys))
    frames = []
    for i in range(n):
        f = np.zeros((H, W, 4), np.uint8)
        off = (fase == i) | (fase == (i + 1) % n)
        f[ys[off], xs[off]] = (*np.array((40, 50, 90)), 255)
        frames.append(Image.fromarray(f, 'RGBA'))
    return frames


@functools.lru_cache(maxsize=None)
def _cuques(n=16):
    """Cuques de llum: punts grocs i verds que s'encenen i s'apaguen, sobre l'herba del primer pla i al voltant del
    plançó."""
    rng = np.random.default_rng(9)
    punts = []
    for _ in range(14):
        P = np.array((rng.uniform(-330, -60), rng.uniform(6, 50), rng.uniform(420, 640)))
        punts.append((P, rng.integers(0, n), rng.uniform(-0.6, 0.6)))
    frames = []
    for i in range(n):
        f = np.zeros((H, W, 4), np.uint8)
        for P, ph, dx in punts:
            k = 0.5 - 0.5 * math.cos(2 * math.pi * (i - ph) / n)
            if k < 0.3:
                continue
            u, vv, _ = CAM.projecta(tuple(P + np.array((dx * i * 2, math.sin(i + ph) * 2, 0))))
            X, Y = int(u), int(vv)
            if 1 <= X < W - 1 and 1 <= Y < H - 1:
                f[Y, X] = (230, 255, 140, int(255 * k))
                for ddx, ddy in ((1, 0), (-1, 0), (0, 1), (0, -1)):
                    f[Y + ddy, X + ddx] = (180, 230, 90, int(110 * k))
        frames.append(Image.fromarray(f, 'RGBA'))
    return frames


ANIMS = {
    'estels': {'frames': lambda: list(_estels()), 'frameDuration': 300, 'zIndex': 1},
    'cuques': {'frames': lambda: list(_cuques()), 'frameDuration': 160, 'zIndex': 2},
}

GEOMETRIA = {'things': {}, 'spawns': {}, 'walkable': [(200, 253), (267, 253), (267, 261), (200, 261)]}
