#!/usr/bin/env python3
"""
Comparativa de les icones d'inventari de Ferro-9: cada objecte a 480 (49×27, hd/items.py) ampliat ×4 al costat del
de 640 (65×36, hd640/items.py) ampliat ×3, que surten de la mateixa mida (196×108 i 195×108) i es poden comparar
píxel a píxel. Les icones del joc les escriu draw_placeholders.py (a través de draw_items.py) com sempre.

Ús (des de tools/): python3 hd640/draw_items.py [sortida.png] [id ...]   (per defecte, totes a items640.png)
"""
import sys
from pathlib import Path

from PIL import Image, ImageDraw

TOOLS = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(TOOLS))
from pixels import nearest  # noqa: E402

import hd640  # noqa: F401,E402
from hd import items as items480  # noqa: E402
from hd640 import items  # noqa: E402

BG = (14, 17, 24, 255)
CELL = (items480.W * 4 + 8 + items.W * 3, items480.H * 4)   # 480 ×4 | 640 ×3
COLS = 2


def main():
    out = Path(sys.argv[1]) if len(sys.argv) > 1 else Path('items640.png')
    ids = sys.argv[2:] or list(items480.ICONS)
    rows = (len(ids) + COLS - 1) // COLS
    pw, ph = CELL[0] + 24, CELL[1] + 22
    sheet = Image.new('RGBA', (COLS * pw, rows * ph), BG)
    d = ImageDraw.Draw(sheet)
    for i, iid in enumerate(ids):
        x, y = (i % COLS) * pw + 12, (i // COLS) * ph + 16
        d.text((x, y - 13), iid, fill=(200, 200, 210, 255))
        a, b = items480.render(iid), items.render(iid)
        if a is not None:
            sheet.alpha_composite(nearest(a, (items480.W * 4, items480.H * 4)), (x, y))
        if b is not None:
            sheet.alpha_composite(nearest(b, (items.W * 3, items.H * 3)), (x + items480.W * 4 + 8, y))
        else:
            d.text((x + items480.W * 4 + 30, y + 48), '(falta)', fill=(220, 90, 80, 255))
    sheet.save(out)
    print(f'✔ {len(ids)} icones a {out}')


if __name__ == '__main__':
    main()
