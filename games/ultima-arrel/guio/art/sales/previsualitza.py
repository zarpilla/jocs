#!/usr/bin/env python3
"""
Previsualització ×2 d'una sala d'art definitiu (hd640/rooms/<sala>.py), com es veurà al joc: el fons, els props que
es demanen, els personatges als seus `spawns` a l'escala de la regió de perspectiva (amb els fulls provisionals de
placeholder-art) i la capa del davant (FRONT) a sobre. Retalla l'escena (fins a y = 260) si la sala té HUD.

Ús: python3 previsualitza.py <sala> [--props id,id] [--sencera] [--debug]
Surt: guio/art/sales/<sala>.png (o <sala>-debug.png, amb les zones clicables i el terra on es camina)
"""
import json
import sys
from pathlib import Path

from PIL import Image, ImageDraw

HERE = Path(__file__).resolve().parent
TOOLS = HERE.parents[2] / 'adapters/benne/tools'
sys.path.insert(0, str(TOOLS))
sys.path.insert(0, str(TOOLS / 'hd'))
from pixels import nearest  # noqa: E402
import render  # noqa: E402


def sprite(cid):
    art = TOOLS.parent / 'placeholder-art' / cid
    if not (art / f'{cid}.png').exists():
        return None, None
    sheet = json.loads((art / f'{cid}.json').read_text())
    ch = json.loads((art / f'{cid}.character.json').read_text())
    tags = {t['name']: t['from'] for t in sheet['meta']['frameTags']}
    f = list(sheet['frames'].values())[tags.get('IdleDL', tags.get('IdleD', 0))]['frame']
    img = Image.open(art / f'{cid}.png').convert('RGBA').crop((f['x'], f['y'], f['x'] + f['w'], f['y'] + f['h']))
    return img, ch['feet']


def escala(geo, y):
    for r in geo.get('regions', []):
        ys = [p[1] for p in r['points']]
        if r.get('scaleEnabled') and min(ys) <= y <= max(ys):
            t = (y - min(ys)) / max(1, max(ys) - min(ys))
            return r['scaleTop'] + (r['scaleBottom'] - r['scaleTop']) * t
    return 1.0


def main():
    name = sys.argv[1]
    props = []
    if '--props' in sys.argv:
        props = sys.argv[sys.argv.index('--props') + 1].split(',')
    mod = render.load(name)
    bg, pr = render.render(name)
    img = bg.copy()
    for pid in props:
        img.alpha_composite(pr[pid])
    geo = getattr(mod, 'GEOMETRIA', {})
    fronts = render.fronts(name, bg)
    chars = []
    for cid, (x, y) in geo.get('spawns', {}).items():
        spr, feet = sprite(cid)
        if spr is None:
            continue
        s = escala(geo, y)
        w, h = max(1, round(spr.width * s)), max(1, round(spr.height * s))
        chars.append((y, cid, spr.resize((w, h), Image.BOX), round(feet['x'] * s), round(feet['y'] * s), x))
    chars.sort()
    # els personatges, i les capes del davant segons la seva línia base
    for y, cid, spr, fx, fy, x in chars:
        img.alpha_composite(spr, (x - fx, y - fy))
    for fimg, f, _ in fronts:
        if f['baseline'] >= 999:
            img.alpha_composite(fimg)
        else:
            # la capa tapa els que tenen els peus més amunt (més al fons) que la seva línia base
            cover = Image.new('RGBA', img.size, (0, 0, 0, 0))
            cover.alpha_composite(fimg)
            redo = img.copy()
            redo.alpha_composite(cover)
            for y, cid, spr, fx, fy, x in chars:
                if y > f['baseline']:
                    redo.alpha_composite(spr, (x - fx, y - fy))
            img = redo
    for _, cid, spr, fx, fy, x in chars:
        bb = spr.getbbox() or (0, 0, 0, 0)
        print(f'{cid}: {bb[3] - bb[1]} px '
              f'(escala {escala(geo, _):.2f}, peus a y = {_})')
    full = '--sencera' in sys.argv
    if not full:
        img = img.crop((0, 0, 640, 260))
    if '--debug' in sys.argv:
        big = nearest(img, (img.width * 2, img.height * 2))
        d = ImageDraw.Draw(big)
        if geo.get('walkable'):
            d.polygon([(x * 2, y * 2) for x, y in geo['walkable']], outline=(0, 255, 0))
        for tid, t in geo.get('things', {}).items():
            x0, y0, x1, y1 = t['rect']
            d.rectangle([x0 * 2, y0 * 2, x1 * 2 + 1, y1 * 2 + 1], outline=(255, 0, 255))
            d.text((x0 * 2 + 2, y0 * 2 + 2), tid, fill=(255, 255, 0))
            wx, wy = t['walk']
            d.ellipse([wx * 2 - 3, wy * 2 - 3, wx * 2 + 3, wy * 2 + 3], outline=(0, 255, 255))
        big.save(HERE / f'{name}-debug.png')
        print(HERE / f'{name}-debug.png')
    else:
        nearest(img, (img.width * 2, img.height * 2)).save(HERE / f'{name}.png')
        print(HERE / f'{name}.png')


if __name__ == '__main__':
    main()
