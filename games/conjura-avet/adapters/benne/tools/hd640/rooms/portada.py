"""
La Conjura de l'Avet — la portada (pantalla sencera de 640×360, sense HUD). EN 3D, a 1×: el pla de cinema de
avet_pla_comu.py (el carrer de `mur_avet`, amb més cel), de nit i amb tramuntana.

L'avet ajagut damunt el mur esbotzat, fosc contra el cel de tempesta, amb les arrels aixecades a l'esquerra i, entre
les arrels, el cofre amb el segell vermell; a la dreta, l'absis amb les finestres enceses (les monges resen matines).
  - El títol és la capa `titol` (ANIMS, quieta, per sobre de tot), a dalt, damunt del cel: «Comença» l'esvaeix i el
    pròleg comença al mateix pla.
  - Els botons de la GUI `portada` van a 220..420 × ≈232..300 (a 360): allà hi ha el carrer fosc i mullat.
  - ANIMS: `llamp` (el cel i l'absis s'encenen, rosats; l'avet queda en silueta), `cofre` (el segell batega),
    `pluja` (en diagonal, amb les ones als bassals).
  Ha de quedar bé sense els botons: és la imatge de la web (`python3 hd640/rooms/portada.py` → portada.png).
"""
import functools
import sys
from pathlib import Path

if __name__ == '__main__':
    sys.path.insert(0, str(Path(__file__).resolve().parents[2]))

import hd640  # noqa: F401,E402
from hd640.rooms import avet_pla_comu as PL  # noqa: E402

LIGHT = None


def _base():
    return PL.render(PL.NIT)[0]


def bg(cv):
    cv.img.paste(_base())
    cv.P = cv.img.load()


PROPS = {}


@functools.lru_cache(maxsize=None)
def _titol():
    return PL.titol()


ANIMS = {
    'llamp': {'frames': lambda: PL.llamps(PL.NIT, PL.NIT_LLAMP), 'frameDuration': 110, 'zIndex': 1},
    'cofre': {'frames': lambda: PL.cofre_bategs(_base()), 'frameDuration': 140, 'zIndex': 2},
    'pluja': {'frames': lambda: list(PL.pluja()), 'frameDuration': 80, 'zIndex': 4},
    'titol': {'frames': lambda: [_titol()], 'frameDuration': 1000, 'loop': False, 'zIndex': 6},
}

GEOMETRIA = {'things': {}, 'spawns': {}, 'walkable': [(200, 253), (267, 253), (267, 261), (200, 261)]}


def publica(out=None):
    """La imatge de la web: el fons, un flaix de llamp a mitges, el cofre encès i el títol."""
    img = _base().copy()
    img.alpha_composite(PL.llamps(PL.NIT, PL.NIT_LLAMP)[7])
    img.alpha_composite(PL.cofre_bategs(_base())[5])
    img.alpha_composite(PL.pluja()[2])
    img.alpha_composite(_titol())
    out = out or Path(__file__).resolve().parents[5] / 'conjura-avet' / 'public' / 'portada.png'
    from pixels import nearest
    nearest(img, (img.width * 2, img.height * 2)).save(out)
    print(f'✔ {out}')


if __name__ == '__main__':
    publica(sys.argv[1] if len(sys.argv) > 1 else None)
