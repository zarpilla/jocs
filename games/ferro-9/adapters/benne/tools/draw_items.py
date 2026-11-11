#!/usr/bin/env python3
"""
Icones dels objectes d'inventari de Ferro-9, en pixel art HD: es dibuixen píxel a píxel a la mida
real de la casella de l'inventari de Benne (49×27), amb volum i contorn fosc selectiu. El dibuix de
cada objecte és a hd/items.py.

draw_placeholders.py les fa servir quan dibuixa el full d'inventari; els objectes que no tenen
icona aquí continuen sortint com una caixa amb el nom.

Ús directe (vista prèvia ampliada): python3 draw_items.py <sortida.png>
"""
import sys
from pathlib import Path

from PIL import Image

sys.path.insert(0, str(Path(__file__).resolve().parent))
from escala import RESOLUCIO  # noqa: E402
if RESOLUCIO == 640:
    from hd640 import items  # noqa: E402   (65×36)
else:
    from hd import items  # noqa: E402

W, H = items.W, items.H   # la casella (49×27 a 480; 65×36 a 640)

ICONS = items.ICONS


def icon(item_id):
    """Imatge RGBA de l'objecte a la mida de la casella, o None si encara no en té."""
    return items.render(item_id)


if __name__ == '__main__':
    scale, cols = 4, 5
    ids = list(ICONS)
    rows = (len(ids) + cols - 1) // cols
    out = Image.new('RGBA', (cols * (W + 4) * scale, rows * (H + 4) * scale), (14, 17, 24, 255))
    for i, iid in enumerate(ids):
        img = icon(iid).resize((W * scale, H * scale), Image.NEAREST)
        out.alpha_composite(img, ((i % cols) * (W + 4) * scale + 2 * scale, (i // cols) * (H + 4) * scale + 2 * scale))
    out.save(sys.argv[1] if len(sys.argv) > 1 else 'items.png')
