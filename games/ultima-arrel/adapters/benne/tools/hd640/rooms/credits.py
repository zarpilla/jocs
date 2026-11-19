"""
L'Última Arrel — els crèdits (pantalla sencera de 640×360, sense HUD): el bosc obert de nit, amb tot el turquesa
encès. És la vora del bosc de `bosc_obert` (vora_comu.py, mode 'nit'), sense ningú: la taula amb les tasses, la
porta oberta amb la llum turquesa, el fanalet, els bolets i els filaments de la xarxa a tota força, i la lluna a la
dreta, on hi havia el cartell. La càmera mostra més cel i més capçada que a la sala (oy = +60): el cel de la dreta
queda net per al text.

ANIMS: `cuques` (cuques de llum i espores que pugen i parpellegen).
"""
import hd640  # noqa: F401
from hd640.rooms.vora_comu import Mode, llum, escena, espores_frames

OY = 60
M = Mode('nit')
LIGHT = llum(M)


def bg(cv):
    cv.img.paste(escena('nit', OY)[0])
    cv.P = cv.img.load()


PROPS = {}


def _cuques():
    return espores_frames(OY, n=32, seed=11, count=30, area=(10, 630, 140, 300), k=1.0)


ANIMS = {'cuques': {'frames': _cuques, 'frameDuration': 140}}

GEOMETRIA = {'things': {}, 'spawns': {}}
