#!/usr/bin/env python3
"""
Redibuixa una o més sales d'art definitiu (hd640/rooms/<sala>.py) i n'escriu el full i la geometria al joc, sense
passar pel sync sencer (que redibuixa totes les provisionals) i sense deixar-les marcades com a provisionals.

Ús (des d'aquesta carpeta):  python3 redibuixa_sala.py <sala> [<sala> ...]
"""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import draw_placeholders as D  # noqa: E402
from room_designs import DESIGNS  # noqa: E402

GAME = Path(__file__).resolve().parents[3] / 'ni-un-ou' / 'src' / 'game'


def main(names):
    for name in names:
        if name not in DESIGNS:
            sys.exit(f'{name}: no hi ha hd640/rooms/{name}.py amb GEOMETRIA')
        d = GAME / 'assets' / 'images' / 'rooms' / name
        d.mkdir(parents=True, exist_ok=True)
        D.draw_designed(d, GAME, DESIGNS[name])
        (d / '.provisional').unlink(missing_ok=True)      # (art definitiu: el sync no l'ha de tornar a dibuixar)


if __name__ == '__main__':
    main(sys.argv[1:])
