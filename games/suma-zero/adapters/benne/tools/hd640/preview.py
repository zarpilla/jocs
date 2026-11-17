#!/usr/bin/env python3
"""
Previsualització animada d'una sala de Suma Zero, a 480×270 (hd/rooms) o a 640×360 (hd640/rooms), per comparar-les.

  python3 hd640/preview.py --res 640 laboratori sortida/laboratori_640 --layers "mar,nevera,bombolla,portatil,nota,@"

`--layers`: les capes per sobre del fons, de darrere a davant. Cada id és una animació (ANIMS) o un prop (PROPS);
`@` són els personatges (GEOMETRIA['spawns']); si la sala té capa del davant (FRONT), qui té els peus per sobre
de la `baseline` queda darrere. Surt <prefix>.gif a pantalla de 1920×1080 (480 ×4, 640 ×3), amb la barra de
verbs amb textos (la de 480 la reprodueix hd640/gui.bar480), i <prefix>.png (el primer fotograma).
A 640 els personatges són els de hd640/characters/ (hd640/draw_characters.py) i la barra, hd640/gui.verb_bar.
"""
import argparse
import importlib
import json
import sys
from pathlib import Path

from PIL import Image

TOOLS = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(TOOLS))
from pixels import nearest  # noqa: E402
ART = TOOLS.parent / 'placeholder-art'


def sprite(cid, art):
    sheet = json.loads((art / cid / f'{cid}.json').read_text())
    ch = json.loads((art / cid / f'{cid}.character.json').read_text())
    tags = {t['name']: t['from'] for t in sheet['meta']['frameTags']}
    f = list(sheet['frames'].values())[tags.get('IdleD', 0)]['frame']
    img = Image.open(art / cid / f'{cid}.png').convert('RGBA').crop((f['x'], f['y'], f['x'] + f['w'], f['y'] + f['h']))
    return img, (ch['feet']['x'], ch['feet']['y']), ch.get('artScale', 1)


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
        W, H, bar_y, scale, art = hd640.W, hd640.H, hd640.BAR_Y, 3, Path(hd640.__file__).parent / 'characters'
        mod = importlib.import_module(f'hd640.rooms.{a.sala}')
        from hd.pix import Canvas
        Canvas = getattr(mod, 'Canvas', Canvas)          # Canvas2x a les sales amb ART_SCALE = 2
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
        W, H, bar_y, scale, art = 480, 270, 195, 4, ART
        import escala
        escala.RESOLUCIO = 480          # el render de 480 (hd/rooms), encara que el joc sigui a 640
        from hd.render import render, render_anims, load
        mod = load(a.sala)
        bg, props = render(a.sala)
        anims = render_anims(a.sala)

    # art a 2× (ART_SCALE): tot es compon a la mida de l'art, i el GIF surt a 1280×720
    s = getattr(mod, 'ART_SCALE', 1) if a.res == '640' else 1
    if s != 1:
        W, H, bar_y, scale = W * s, H * s, bar_y * s, max(1, scale // s)
    geo = getattr(mod, 'GEOMETRIA', None)
    if geo is None:                     # les sales de 480 tenen la geometria a room_designs.py
        from room_designs import DESIGNS
        geo = DESIGNS.get(a.sala, {})
    spawns = geo.get('spawns', {})
    layers = [x.strip() for x in a.layers.split(',') if x.strip()]
    for lid in layers:
        if lid != '@' and lid not in anims and lid not in props:
            sys.exit(f'capa desconeguda: {lid}')
    # la barra, amb els textos (s'importa després de dibuixar la sala: importar hd640 posa pix a 640)
    # (si encara no hi ha hd640/gui.py, una franja fosca)
    try:
        import hd640.gui as gui
        bar = gui.verb_bar() if a.res == '640' else gui.bar480()
    except (ImportError, AttributeError):
        bar = Image.new('RGBA', (W, H - bar_y), (8, 10, 18, 255))
    if s != 1:
        bar = bar.transform((bar.width * s, bar.height * s), Image.Transform.EXTENT, (0, 0, bar.width, bar.height),
                            Image.Resampling.NEAREST)
    chars = []
    for cid, (x, y) in spawns.items():
        if (art / cid / f'{cid}.png').exists():
            spr, (fx, fy), k = sprite(cid, art)
            if s != k:                                   # el full del personatge (a ×k) a la mida de la sala (×s)
                spr = nearest(spr, (spr.width * s // k, spr.height * s // k))
            chars.append((y, spr, ((x - fx) * s, (y - fy) * s)))
    chars.sort(key=lambda c: c[0])
    # la llum de la sala sobre els personatges (characterLights del motor), amb els props visibles de --layers
    cl = (geo or {}).get('characterLights')
    if cl and s != 1:
        cl = {**cl, 'lights': [{**l, 'x': l['x'] * s, 'y': l['y'] * s, 'radius': l['radius'] * s} for l in cl['lights']]}
    if cl and a.res == '640':
        from hd640.llum import light_character
        chars = [(y, light_character(spr, pos, cl, set(layers)), pos) for y, spr, pos in chars]
    front = None
    if getattr(mod, 'FRONT', None):
        f = mod.FRONT
        front = Image.new('RGBA', bg.size, (0, 0, 0, 0))
        src, dst = bg.load(), front.load()
        for y in range(H):
            for x in range(W):
                if f['mask'](x // s, y // s):
                    dst[x, y] = src[x, y]
        front = (front, f['baseline'])

    frames = []
    n = max(1, round(a.seconds * 1000 / a.ms))
    for i in range(n):
        t = i * a.ms
        im = bg.copy()
        for lid in layers:
            if lid == '@':
                for behind in (True, False):
                    for y, spr, pos in chars:
                        if front is None or (y <= front[1]) == behind:  # (y: els peus, en píxels de sala)
                            im.alpha_composite(spr, pos)
                    if behind and front:
                        im.alpha_composite(front[0])
            elif lid in anims:
                fr, ms = anims[lid]
                im.alpha_composite(fr[(t // ms) % len(fr)])
            else:
                im.alpha_composite(props[lid])
        im.paste(bar, (0, bar_y))
        frames.append(nearest(im, (W * scale, H * scale)).convert('RGB'))
    out = Path(a.out)
    out.parent.mkdir(parents=True, exist_ok=True)
    frames[0].save(out.with_suffix('.png'))
    frames[0].save(out.with_suffix('.gif'), save_all=True, append_images=frames[1:], duration=a.ms, loop=0)
    print(f'✔ {out}.gif ({n} fotogrames)')


if __name__ == '__main__':
    main()
