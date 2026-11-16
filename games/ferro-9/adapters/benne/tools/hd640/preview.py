#!/usr/bin/env python3
"""
Previsualització animada d'una sala de Ferro-9, a 480×270 (hd/rooms) o a 640×360 (hd640/rooms), per comparar-les.

  python3 hd640/preview.py --res 640 gavina_cella sortida/cella_640 --layers "fluorescent,panell,@"
  python3 hd640/preview.py --res 640 gavina_cella sortida/cella_640 --debug

`--layers`: les capes per sobre del fons, de darrere a davant. Cada id és una animació (ANIMS) o un prop (PROPS);
`@` són els personatges (els `spawns` de room_designs.py). Sense `--layers`, totes les animacions i `@`.
`--debug` hi dibuixa les zones clicables (`things`), el terra (`walkable`) i els punts on es camina, a escala.
Surt <prefix>.gif a pantalla de 1920×1080 (480 ×4, 640 ×3), amb la barra de verbs, i <prefix>.png (el primer
fotograma). Els personatges: a 640, els de hd640/characters/ si ja hi són (hd640/draw_characters.py), si no els de
placeholder-art/ ampliats ×4/3 (només per orientar-se); a 480, els de placeholder-art/.
"""
import argparse
import importlib
import json
import sys
from pathlib import Path

from PIL import Image, ImageDraw

TOOLS = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(TOOLS))
from pixels import nearest  # noqa: E402
ART = TOOLS.parent / 'placeholder-art'


def sprite(cid, art, k=1.0):
    sheet = json.loads((art / cid / f'{cid}.json').read_text())
    ch = json.loads((art / cid / f'{cid}.character.json').read_text())
    tags = {t['name']: t['from'] for t in sheet['meta']['frameTags']}
    f = list(sheet['frames'].values())[tags.get('IdleD', 0)]['frame']
    img = Image.open(art / cid / f'{cid}.png').convert('RGBA').crop((f['x'], f['y'], f['x'] + f['w'], f['y'] + f['h']))
    fx, fy = ch['feet']['x'], ch['feet']['y']
    if k != 1.0:
        img = nearest(img, (round(img.width * k), round(img.height * k)))
        fx, fy = round(fx * k), round(fy * k)
    return img, (fx, fy)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('--res', choices=('480', '640'), required=True)
    ap.add_argument('sala')
    ap.add_argument('out')
    ap.add_argument('--layers', default=None)
    ap.add_argument('--debug', action='store_true')
    ap.add_argument('--ms', type=int, default=120, help='durada de cada fotograma del GIF')
    ap.add_argument('--seconds', type=float, default=6)
    a = ap.parse_args()

    import escala
    if a.res == '640':
        import hd640
        W, H, bar_y, scale = hd640.W, hd640.H, hd640.BAR_Y, 3
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
        W, H, bar_y, scale = 480, 270, 195, 4
        escala.RESOLUCIO = 480          # el render de 480 (hd/rooms), encara que el joc sigui a 640
        from hd.render import render, render_anims, load
        mod = load(a.sala)
        bg, props = render(a.sala)
        anims = render_anims(a.sala)

    # Disseny (352×198) → píxels de la resolució triada (no pix.R/Pt: importar hd640.gui canvia pix.K)
    kd = W / 352
    R = lambda x0, y0, x1, y1: escala.box(x0, y0, x1, y1, kd)  # noqa: E731
    Pt = lambda x, y: escala.pt(x, y, kd)  # noqa: E731
    from room_designs import DESIGNS
    design = DESIGNS.get(a.sala, {})
    spawns = design.get('spawns', {})
    if a.layers is None:
        layers = list(anims) + ['@']
    else:
        layers = [x.strip() for x in a.layers.split(',') if x.strip()]
    for lid in layers:
        if lid != '@' and lid not in anims and lid not in props:
            sys.exit(f'capa desconeguda: {lid} (animacions: {", ".join(anims)}; props: {", ".join(props)})')
    try:
        import hd640.gui as gui
        bar = gui.verb_bar() if a.res == '640' else gui.bar480()
    except (ImportError, AttributeError):
        bar = Image.new('RGBA', (W, H - bar_y), (8, 10, 18, 255))
    chars = []
    for cid, (x, y) in spawns.items():
        art, k = ART, 1.0
        if a.res == '640':
            own = Path(hd640.__file__).parent / 'characters'
            art, k = (own, 1.0) if (own / cid / f'{cid}.png').exists() else (ART, 4 / 3)
            if art is ART and (ART / cid / f'{cid}.png').exists():
                ch = json.loads((ART / cid / f'{cid}.character.json').read_text())
                k = 1.0 if ch['feet']['y'] > 100 else 4 / 3     # (si placeholder-art ja és de 640)
        if (art / cid / f'{cid}.png').exists():
            spr, (fx, fy) = sprite(cid, art, k)
            px, py = Pt(x, y)
            chars.append((py, spr, (px - fx, py - fy)))
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
        big = nearest(im, (W * scale, H * scale)).convert('RGB')
        if a.debug and design:
            d = ImageDraw.Draw(big)
            if design.get('walkable'):
                d.polygon([(Pt(x, y)[0] * scale + 1, Pt(x, y)[1] * scale + 1) for x, y in design['walkable']], outline=(0, 255, 0))
            for tid, th in design.get('things', {}).items():
                x0, y0, x1, y1 = R(*th['rect'])
                d.rectangle([x0 * scale, y0 * scale, x1 * scale + scale - 1, y1 * scale + scale - 1], outline=(255, 0, 255))
                d.text((x0 * scale + 3, y0 * scale + 3), tid, fill=(255, 255, 0))
                if 'walk' in th:
                    wx, wy = Pt(*th['walk'])
                    d.ellipse([wx * scale - 4, wy * scale - 4, wx * scale + 4, wy * scale + 4], outline=(0, 255, 255))
        frames.append(big)
    out = Path(a.out)
    out.parent.mkdir(parents=True, exist_ok=True)
    frames[0].save(out.with_suffix('.png'))
    frames[0].save(out.with_suffix('.gif'), save_all=True, append_images=frames[1:], duration=a.ms, loop=0)
    print(f'✔ {out}.gif ({n} fotogrames)')


if __name__ == '__main__':
    main()
