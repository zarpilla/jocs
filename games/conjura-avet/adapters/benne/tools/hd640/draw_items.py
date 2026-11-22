#!/usr/bin/env python3
"""
Icones d'inventari de La Conjura de l'Avet a 640×360 (65×36, hd640/items.py): una icona per objecte (<id>.png) i el full
de l'inventari (inventory.png + inventory.json, com el que escriu draw_placeholders.py), en l'ordre del full del
joc o, si encara no hi ha projecte Benne, en l'ordre de hd640/items.ICONS.

Ús (des de tools/): python3 hd640/draw_items.py [carpeta]   (per defecte, hd640/inventory/)
Al projecte Benne: python3 hd640/draw_items.py ../../../conjura-avet/src/game/assets/images/inventory
(el sync el refà igual amb draw_placeholders.py mentre hi hagi la marca `.provisional`).
La làmina de revisió: python3 ../../../guio/art/inventari.py
"""
import json
import sys
from pathlib import Path

TOOLS = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(TOOLS))

from hd640 import items  # noqa: E402
from draw_placeholders import aseprite_sheet, paste_grid  # noqa: E402

GAME_INV = TOOLS.parents[2] / 'conjura-avet/src/game/assets/images/inventory/inventory.json'


def main():
    out = Path(sys.argv[1]) if len(sys.argv) > 1 else Path(__file__).resolve().parent / 'inventory'
    out.mkdir(parents=True, exist_ok=True)
    if GAME_INV.exists():
        order = [t['name'] for t in json.loads(GAME_INV.read_text())['meta']['frameTags']]
        order = [i for i in order if i in items.ICONS]
        order += [i for i in items.ICONS if i not in order]      # els objectes nous, al final
    else:
        order = list(items.ICONS)
    frames = []
    for iid in order:
        img = items.render(iid)
        img.save(out / f'{iid}.png')
        frames.append(img)
    paste_grid(frames, items.W, items.H).save(out / 'inventory.png')
    (out / 'inventory.json').write_text(json.dumps(aseprite_sheet('inventory', len(order), order, items.W, items.H),
                                                   indent=2) + '\n')
    print(f'✔ {len(order)} icones a {out}')


if __name__ == '__main__':
    main()
