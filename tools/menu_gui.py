#!/usr/bin/env python3
"""
Dibuixa els botons del menú de joc (GUI `game-menu`) dins del seu full d'Aseprite.

El fotograma 0 (el marc 9-slice) no es toca; els botons s'hi afegeixen com a fotogrames nous,
un per mida i estat: `btn-mig`, `btn-mig-hover`, `btn-mig-pressed`, `btn-ample`, … i el
separador de sota el títol (`separador`).

Ús: python3 tools/menu_gui.py   (des de l'arrel del repositori; necessita Pillow)
"""
import json
from pathlib import Path

from PIL import Image, ImageDraw

DIR = Path(__file__).resolve().parent.parent / 'ferro-9/src/game/assets/images/guis/game-menu'

# Paleta del marc (game-menu.png) i un blau de placa una mica més viu.
NEGRE = (7, 9, 14)
OMBRA = (12, 15, 22)
FOSC = (18, 22, 31)
LLUM = (43, 50, 65)
OR_FOSC = (92, 66, 34)
OR = (168, 128, 64)
OR_CLAR = (202, 162, 88)
OR_BRILL = (230, 200, 130)

ESTATS = {
    #           vora      placa        llum         ombra       cargols
    'normal': (NEGRE, (24, 34, 54), (44, 60, 88), (15, 21, 34), OR_FOSC),
    'hover': (OR_CLAR, (34, 56, 88), (62, 88, 126), (20, 34, 56), OR_BRILL),
    'pressed': (OR, (14, 22, 38), (10, 15, 26), (34, 48, 72), OR_CLAR),
}

MIDES = {'mig': (68, 20), 'ample': (139, 20)}


def boto(w, h, estat):
    vora, placa, llum, ombra, cargol = ESTATS[estat]
    im = Image.new('RGBA', (w, h), (0, 0, 0, 0))
    d = ImageDraw.Draw(im)
    # Placa amb les cantonades retallades d'un píxel.
    d.rectangle([1, 0, w - 2, h - 1], fill=vora)
    d.rectangle([0, 1, w - 1, h - 2], fill=vora)
    d.rectangle([1, 1, w - 2, h - 2], fill=placa)
    # Bisell: llum a dalt i a l'esquerra, ombra a baix i a la dreta (al revés quan està premut).
    d.line([2, 1, w - 3, 1], fill=llum)
    d.line([1, 2, 1, h - 3], fill=llum)
    d.line([2, h - 2, w - 3, h - 2], fill=ombra)
    d.line([w - 2, 2, w - 2, h - 3], fill=ombra)
    # Una ratlla fina sota la llum, perquè la placa no sembli plana.
    d.line([3, 2, w - 4, 2], fill=tuple((a + b) // 2 for a, b in zip(llum, placa)))
    # Cargols a les quatre cantonades.
    for x, y in ((3, 3), (w - 4, 3), (3, h - 4), (w - 4, h - 4)):
        d.point((x, y), fill=cargol)
    if estat == 'hover' and w > 100:
        # Fletxetes daurades a banda i banda (als estrets toparien amb el text).
        cy = h // 2 - 1
        for dx in range(3):
            d.line([5 + dx, cy - 2 + dx, 5 + dx, cy + 2 - dx], fill=OR_BRILL)
            d.line([w - 6 - dx, cy - 2 + dx, w - 6 - dx, cy + 2 - dx], fill=OR_BRILL)
    return im


def separador(w=110, h=3):
    im = Image.new('RGBA', (w, h), (0, 0, 0, 0))
    d = ImageDraw.Draw(im)
    mig = w // 2
    d.line([4, 1, w - 5, 1], fill=OR_FOSC)
    d.line([16, 1, w - 17, 1], fill=OR)
    d.line([mig - 18, 1, mig + 17, 1], fill=OR_CLAR)
    # Rombe al mig.
    d.point((mig - 1, 0), fill=OR_BRILL)
    d.point((mig, 0), fill=OR_BRILL)
    d.line([mig - 3, 1, mig + 2, 1], fill=OR_BRILL)
    d.point((mig - 1, 2), fill=OR_BRILL)
    d.point((mig, 2), fill=OR_BRILL)
    return im


def main():
    json_path, png_path = DIR / 'game-menu.json', DIR / 'game-menu.png'
    meta = json.loads(json_path.read_text())
    base = Image.open(png_path).convert('RGBA')
    first_key = next(iter(meta['frames']))
    marc = meta['frames'][first_key]
    fx, fy, fw, fh = (marc['frame'][k] for k in ('x', 'y', 'w', 'h'))
    marc_img = base.crop((fx, fy, fx + fw, fy + fh))

    nous = []
    for mida, (w, h) in MIDES.items():
        for estat in ESTATS:
            tag = f'btn-{mida}' if estat == 'normal' else f'btn-{mida}-{estat}'
            nous.append((tag, boto(w, h, estat)))
    nous.append(('separador', separador()))

    # Full: el marc a dalt a l'esquerra i els fotogrames nous en columna al costat.
    ample = fw + 1 + max(im.width for _, im in nous)
    alt = max(fh, sum(im.height + 1 for _, im in nous))
    full = Image.new('RGBA', (ample, alt), (0, 0, 0, 0))
    full.paste(marc_img, (0, 0))
    frames = {first_key: {**marc, 'frame': {'x': 0, 'y': 0, 'w': fw, 'h': fh}}}
    tags = [t for t in meta['meta']['frameTags'] if t['from'] == 0]
    y = 0
    for i, (tag, im) in enumerate(nous, start=1):
        x = fw + 1
        full.paste(im, (x, y))
        frames[f'game-menu {i}.aseprite'] = {
            'frame': {'x': x, 'y': y, 'w': im.width, 'h': im.height}, 'rotated': False, 'trimmed': False,
            'spriteSourceSize': {'x': 0, 'y': 0, 'w': im.width, 'h': im.height},
            'sourceSize': {'w': im.width, 'h': im.height}, 'duration': 100,
        }
        tags.append({'name': tag, 'from': i, 'to': i, 'direction': 'forward', 'color': '#000000ff'})
        y += im.height + 1

    meta['frames'] = frames
    meta['meta']['frameTags'] = tags
    meta['meta']['image'] = 'game-menu.png'
    meta['meta']['size'] = {'w': ample, 'h': alt}
    full.save(png_path)
    json_path.write_text(json.dumps(meta, indent=2) + '\n')
    print(f'✔ menú: {len(nous)} fotogrames ({", ".join(t for t, _ in nous)})')


if __name__ == '__main__':
    main()
