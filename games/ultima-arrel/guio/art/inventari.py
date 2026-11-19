#!/usr/bin/env python3
"""
L'Última Arrel — làmina de revisió de les icones d'inventari (hd640/items.py), ×3.

Cada icona (65×36, la mida real de la casella) damunt d'una casella fosca com les del HUD, amb el nom a sota.
Ús: python3 inventari.py  →  inventari.png
"""
import sys
from pathlib import Path

from PIL import Image, ImageDraw

HERE = Path(__file__).resolve().parent
TOOLS = HERE.parents[1] / 'adapters/benne/tools'
sys.path.insert(0, str(TOOLS))
from pixels import nearest  # noqa: E402
from hd640 import items  # noqa: E402

S, COLS, GAP = 3, 5, 6
FONS = (58, 40, 26)
CASELLA = (24, 18, 14)
VORA = (86, 62, 40)


def main():
    ids = list(items.ICONS)
    rows = -(-len(ids) // COLS)
    cw, ch = items.W + GAP, items.H + GAP + 12
    out = Image.new('RGBA', (COLS * cw + GAP, rows * ch + GAP), FONS + (255,))
    d = ImageDraw.Draw(out)
    for i, iid in enumerate(ids):
        x, y = GAP + (i % COLS) * cw, GAP + (i // COLS) * ch
        d.rectangle([x - 1, y - 1, x + items.W, y + items.H], fill=VORA)
        d.rectangle([x, y, x + items.W - 1, y + items.H - 1], fill=CASELLA)
        out.alpha_composite(items.render(iid), (x, y))
    big = nearest(out, (out.width * S, out.height * S))
    d = ImageDraw.Draw(big)
    for i, iid in enumerate(ids):
        x, y = GAP + (i % COLS) * cw, GAP + (i // COLS) * ch + items.H + 2
        d.text((x * S, y * S), iid, fill=(240, 228, 200))
    big.save(HERE / 'inventari.png')
    print('inventari.png', big.size)


if __name__ == '__main__':
    main()
