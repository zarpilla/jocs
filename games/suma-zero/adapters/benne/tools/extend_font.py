#!/usr/bin/env python3
"""
Afegeix a una font de mapa de bits (format BMFont XML + PNG, el que fa servir Benne)
els caràcters catalans que li falten: à è é í ï ò ó ú ü ç · « » — i les majúscules.

Les lletres noves es componen amb els píxels de la mateixa font (lletra base + accent),
així mantenen l'estil. Les accents es dibuixen a les files buides de sobre la lletra,
com el punt de la "i". No toca els caràcters que la font ja té.

Ús: python3 extend_font.py <font.xml> [<font.xml> ...]
Necessita Pillow (pip install pillow).
"""
import re
import sys
from pathlib import Path

from PIL import Image

# caràcter → (lletra base, accent)
COMPOSE = {
    'à': ('a', 'grave'), 'è': ('e', 'grave'), 'é': ('e', 'acute'), 'í': ('i', 'acute'), 'ï': ('i', 'diaeresis'),
    'ò': ('o', 'grave'), 'ó': ('o', 'acute'), 'ú': ('u', 'acute'), 'ü': ('u', 'diaeresis'), 'ç': ('c', 'cedilla'),
    'À': ('A', 'grave'), 'È': ('E', 'grave'), 'É': ('E', 'acute'), 'Í': ('I', 'acute'), 'Ï': ('I', 'diaeresis'),
    'Ò': ('O', 'grave'), 'Ó': ('O', 'acute'), 'Ú': ('U', 'acute'), 'Ü': ('U', 'diaeresis'), 'Ç': ('C', 'cedilla'),
}
SPECIAL = ['·', '«', '»', '—']

ATTRS = ('x', 'y', 'width', 'height', 'xoffset', 'yoffset', 'xadvance', 'page', 'chnl')


def parse_chars(xml):
    chars = {}
    for line in re.findall(r'<char [^>]*/>', xml):
        attrs = dict(re.findall(r'(\w+)="(-?\d+)"', line))
        chars[int(attrs['id'])] = {k: int(attrs[k]) for k in ATTRS}
    return chars


def crop(atlas, g):
    return atlas.crop((g['x'], g['y'], g['x'] + g['width'], g['y'] + g['height']))


def ink_bbox(img):
    return img.getchannel('A').point(lambda a: 255 if a > 128 else 0).getbbox()


def ink_color(img):
    for yy in range(img.height):
        for xx in range(img.width):
            px = img.getpixel((xx, yy))
            if px[3] > 128:
                return px
    return (255, 255, 255, 255)


def put(img, x, y, color):
    if 0 <= x < img.width and 0 <= y < img.height:
        img.putpixel((x, y), color)


def compose(atlas, chars, base, accent, x_top, cap_top):
    g = chars[ord(base)]
    img = crop(atlas, g).copy()
    box = ink_bbox(img)
    if box is None:
        return None
    color = ink_color(img)
    left, top, right, bottom = box
    lower = base.islower()

    # La "i" perd el punt: tot el que hi ha per sobre de l'alçada de la "x".
    if base == 'i':
        for yy in range(0, x_top):
            for xx in range(img.width):
                img.putpixel((xx, yy), (0, 0, 0, 0))
        left, top, right, bottom = ink_bbox(img)

    cx = (left + right - 1) // 2
    pad = 0
    if accent in ('acute', 'grave', 'diaeresis'):
        ref = x_top if lower else cap_top
        r0, r1 = ref - 3, ref - 2          # dues files, i una de buida abans de la lletra
        if accent == 'diaeresis':
            r0 = r1
        pad = max(0, -r0)
        if pad:
            grown = Image.new('RGBA', (img.width, img.height + pad), (0, 0, 0, 0))
            grown.paste(img, (0, pad))
            img = grown
            r0 += pad
            r1 += pad
        if accent == 'acute':
            for xx in (cx + 1, cx + 2):
                put(img, xx, r0, color)
            for xx in (cx, cx + 1):
                put(img, xx, r1, color)
        elif accent == 'grave':
            for xx in (cx - 1, cx):
                put(img, xx, r0, color)
            for xx in (cx, cx + 1):
                put(img, xx, r1, color)
        else:
            put(img, left, r1, color)
            put(img, right - 1, r1, color)
    elif accent == 'cedilla':
        if bottom + 2 > img.height:
            grown = Image.new('RGBA', (img.width, bottom + 2), (0, 0, 0, 0))
            grown.paste(img, (0, 0))
            img = grown
        put(img, cx, bottom, color)
        put(img, cx - 1, bottom + 1, color)
        put(img, cx, bottom + 1, color)
    out = dict(g)
    out['yoffset'] = g['yoffset'] - pad
    return img, out


def special(atlas, chars, ch, x_top):
    dot = chars[ord('.')]
    dot_img = crop(atlas, dot)
    color = ink_color(dot_img)
    if ch == '·':
        box = ink_bbox(dot_img)
        img = Image.new('RGBA', dot_img.size, (0, 0, 0, 0))
        img.paste(dot_img.crop(box), (box[0], box[1] - 2))
        return img, dict(dot)
    if ch in '«»':
        img = Image.new('RGBA', (9, dot_img.height), (0, 0, 0, 0))
        rows = [x_top + 1, x_top + 2, x_top + 3]
        xs = [(3, 6), (2, 5), (3, 6)] if ch == '«' else [(2, 5), (3, 6), (2, 5)]
        for yy, (a, b) in zip(rows, xs):
            put(img, a, yy, color)
            put(img, b, yy, color)
        return img, {**dot, 'width': 9, 'xadvance': 7}
    if ch == '—':
        dash = chars[ord('-')]
        dimg = crop(atlas, dash)
        box = ink_bbox(dimg)
        img = Image.new('RGBA', (12, dimg.height), (0, 0, 0, 0))
        for yy in range(box[1], box[3]):
            for xx in range(2, 11):
                put(img, xx, yy, color)
        return img, {**dash, 'width': 12, 'xadvance': 10}
    return None


def extend(xml_path: Path):
    xml = xml_path.read_text(encoding='utf-8')
    chars = parse_chars(xml)
    page = re.search(r'<page id="0" file="([^"]+)"', xml).group(1)
    png_path = xml_path.parent / page
    atlas = Image.open(png_path).convert('RGBA')

    x_top = ink_bbox(crop(atlas, chars[ord('x')]))[1]
    cap_top = ink_bbox(crop(atlas, chars[ord('E')]))[1]

    new = []
    for ch, (base, accent) in COMPOSE.items():
        if ord(ch) in chars or ord(base) not in chars:
            continue
        made = compose(atlas, chars, base, accent, x_top, cap_top)
        if made:
            new.append((ch, *made))
    for ch in SPECIAL:
        if ord(ch) in chars:
            continue
        made = special(atlas, chars, ch, x_top)
        if made:
            new.append((ch, *made))
    if not new:
        print(f'· {xml_path.name}: ja té tots els caràcters')
        return

    # Les lletres noves van en files noves, sota l'atles original.
    row_h = max(img.height for _, img, _ in new) + 1
    per_row = max(1, atlas.width // (max(img.width for _, img, _ in new) + 1))
    rows = (len(new) + per_row - 1) // per_row
    grown = Image.new('RGBA', (atlas.width, atlas.height + rows * row_h + 1), (255, 255, 255, 0))
    grown.paste(atlas, (0, 0))
    x, y = 0, atlas.height + 1
    lines = []
    for ch, img, g in new:
        if x + img.width > grown.width:
            x, y = 0, y + row_h
        grown.paste(img, (x, y))
        attrs = {**g, 'x': x, 'y': y, 'width': img.width, 'height': img.height}
        lines.append('    <char id="%d" %s/>' % (ord(ch), ' '.join(f'{k}="{attrs[k]}"' for k in ATTRS)))
        x += img.width + 1
    grown.save(png_path)

    xml = re.sub(r'scaleH="\d+"', f'scaleH="{grown.height}"', xml)
    count = len(chars) + len(new)
    xml = re.sub(r'<chars count="\d+">', f'<chars count="{count}">', xml)
    xml = xml.replace('</chars>', '\n'.join(lines) + '\n  </chars>', 1)
    xml_path.write_text(xml, encoding='utf-8')
    print(f'✔ {xml_path.name}: +{len(new)} caràcters ({"".join(c for c, _, _ in new)})')


if __name__ == '__main__':
    for arg in sys.argv[1:]:
        extend(Path(arg))
