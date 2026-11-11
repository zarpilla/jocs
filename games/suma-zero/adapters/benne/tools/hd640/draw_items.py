#!/usr/bin/env python3
"""
Icones d'inventari de Suma Zero a 640×360 (65×36, hd640/items.py), amb la mateixa interfície que draw_items.py
(W, H, ICONS, icon) i el mateix format de sortida: una icona per objecte (<id>.png) i el full de l'inventari
(inventory.png + inventory.json, com el que escriu draw_placeholders.py), en l'ordre del full del joc.

Ús (des de tools/): python3 hd640/draw_items.py [carpeta]   (per defecte, hd640/inventory/)
"""
import json
import sys
from pathlib import Path

TOOLS = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(TOOLS))

import hd640  # noqa: F401,E402
from hd640 import items  # noqa: E402

W, H = items.W, items.H   # la casella (65×36)

ICONS = items.ICONS

GAME_INV = TOOLS.parents[2] / 'suma-zero/src/game/assets/images/inventory/inventory.json'
ITEMS = TOOLS.parents[1] / 'game/data/items.json'


def icon(item_id):
    """Imatge RGBA de l'objecte a la mida de la casella (65×36), o None si encara no en té."""
    return items.render(item_id)


def main():
    from draw_placeholders import aseprite_sheet, paste_grid
    out = Path(sys.argv[1]) if len(sys.argv) > 1 else Path(__file__).resolve().parent / 'inventory'
    out.mkdir(parents=True, exist_ok=True)
    if GAME_INV.exists():
        order = [t['name'] for t in json.loads(GAME_INV.read_text())['meta']['frameTags']]
    else:
        order = [k for k in json.loads(ITEMS.read_text()) if not k.startswith('$')]
    frames = []
    for iid in order:
        img = icon(iid)
        img.save(out / f'{iid}.png')
        frames.append(img)
    paste_grid(frames, W, H).save(out / 'inventory.png')
    (out / 'inventory.json').write_text(json.dumps(aseprite_sheet('inventory', len(order), order, W, H), indent=2) + '\n')
    print(f'✔ {len(order)} icones a {out}')


if __name__ == '__main__':
    main()
