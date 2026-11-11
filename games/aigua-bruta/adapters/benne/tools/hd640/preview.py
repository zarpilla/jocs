#!/usr/bin/env python3
"""
Previsualització animada d'una sala, a 480×270 (hd/rooms) o a 640×360 (hd640/rooms), per comparar-les.

  python3 hd640/preview.py --res 640 laboratori sortida/laboratori_640 --layers "mar,nevera,bombolla,portatil,nota,@"

`--layers`: les capes per sobre del fons, de darrere a davant. Cada id és una animació (ANIMS) o un prop (PROPS);
`@` són els personatges (GEOMETRIA['spawns']). Surt <prefix>.gif a pantalla de 1920×1080 (480 ×4, 640 ×3),
amb la barra de verbs, i <prefix>.png (el primer fotograma).
"""
import argparse
import importlib
import json
import sys
from pathlib import Path

from PIL import Image

TOOLS = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(TOOLS))
VERBS = TOOLS.parents[2] / 'aigua-bruta/src/game/assets/images/guis/verbs/verbs.png'
ART = TOOLS.parent / 'placeholder-art'


def sprite(cid, k):
    sheet = json.loads((ART / cid / f'{cid}.json').read_text())
    ch = json.loads((ART / cid / f'{cid}.character.json').read_text())
    tags = {t['name']: t['from'] for t in sheet['meta']['frameTags']}
    f = list(sheet['frames'].values())[tags.get('IdleD', 0)]['frame']
    img = Image.open(ART / cid / f'{cid}.png').convert('RGBA').crop((f['x'], f['y'], f['x'] + f['w'], f['y'] + f['h']))
    if k != 1:
        img = img.resize((round(img.width * k), round(img.height * k)), Image.NEAREST)
    return img, (round(ch['feet']['x'] * k), round(ch['feet']['y'] * k))


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('--res', choices=('480', '640'), required=True)
    ap.add_argument('sala')
    ap.add_argument('out')
    ap.add_argument('--layers', default='')
    ap.add_argument('--ms', type=int, default=120, help='durada de cada fotograma del GIF')
    ap.add_argument('--seconds', type=float, default=6)
    a = ap.parse_args()

    if a.res == '640':
        import hd640
        W, H, bar_y, k, scale = hd640.W, hd640.H, hd640.BAR_Y, 4 / 3, 3
        mod = importlib.import_module(f'hd640.rooms.{a.sala}')
        from hd.pix import Canvas
        light = getattr(mod, 'LIGHT', None)
        bg = Canvas(light=light)
        mod.bg(bg)
        bg = bg.img
        props = {}
        for pid, fn in getattr(mod, 'PROPS', {}).items():
            pc = Canvas(light=light, transparent=True)
            fn(pc)
            props[pid] = pc.img
        anims = {aid: (an['frames'](), an.get('frameDuration', 150)) for aid, an in getattr(mod, 'ANIMS', {}).items()}
    else:
        W, H, bar_y, k, scale = 480, 270, 195, 1, 4
        from hd.render import render, render_anims, load
        mod = load(a.sala)
        bg, props = render(a.sala)
        anims = render_anims(a.sala)

    spawns = mod.GEOMETRIA['spawns']
    layers = [x.strip() for x in a.layers.split(',') if x.strip()]
    for lid in layers:
        if lid != '@' and lid not in anims and lid not in props:
            sys.exit(f'capa desconeguda: {lid}')
    bar = Image.open(VERBS).convert('RGBA').crop((0, 195, 480, 270))
    if k != 1:
        bar = bar.resize((W, H - bar_y), Image.NEAREST)
    chars = []
    for cid, (x, y) in spawns.items():
        if (ART / cid / f'{cid}.png').exists():
            spr, (fx, fy) = sprite(cid, k)
            chars.append((y, spr, (x - fx, y - fy)))
    chars.sort(key=lambda c: c[0])

    frames = []
    n = max(1, round(a.seconds * 1000 / a.ms))
    for i in range(n):
        t = i * a.ms
        im = bg.copy()
        for lid in layers:
            if lid == '@':
                for _, spr, pos in chars:
                    im.alpha_composite(spr, pos)
            elif lid in anims:
                fr, ms = anims[lid]
                im.alpha_composite(fr[(t // ms) % len(fr)])
            else:
                im.alpha_composite(props[lid])
        im.paste(bar, (0, bar_y))
        frames.append(im.resize((W * scale, H * scale), Image.NEAREST).convert('RGB'))
    out = Path(a.out)
    out.parent.mkdir(parents=True, exist_ok=True)
    frames[0].save(out.with_suffix('.png'))
    frames[0].save(out.with_suffix('.gif'), save_all=True, append_images=frames[1:], duration=a.ms, loop=0)
    print(f'✔ {out}.gif ({n} fotogrames)')


if __name__ == '__main__':
    main()
