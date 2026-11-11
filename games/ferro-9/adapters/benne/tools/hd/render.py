#!/usr/bin/env python3
"""
Dibuixa una sala HD (hd/rooms/<sala>.py) i en fa previsualitzacions per revisar-la.

Cada mòdul de sala defineix:
  LIGHT              Light de la sala (també s'aplica als props)
  bg(cv)             dibuixa el fons en un Canvas opac de 480×270
  PROPS              {id: fn(cv)}: cada prop condicional, en un Canvas transparent a part
  ANIMS (opcional)   {id: {'frames': fn() → [imatges RGBA], 'frameDuration': ms}}: animacions de fons
                     en bucle (decorat no clicable, sempre visible); cada fotograma porta només el que
                     canvia respecte del fons

La geometria (zones clicables, punts on es camina, terra) continua a room_designs.py: el dibuix ha
de coincidir amb `things` (vegeu pix.R per passar-los a píxels reals).

Ús: python3 render.py <sala> [carpeta de sortida]
Surt: <sala>.png (fons), <sala>_x3.png (part visible ×3), <sala>_props_x3.png (amb tots els props),
      <sala>_debug_x3.png (zones clicables, terra i personatges a escala).
"""
import importlib
import json
import sys
from pathlib import Path

from PIL import Image, ImageDraw

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE.parent))

from escala import RESOLUCIO  # noqa: E402
if RESOLUCIO == 640:
    import hd640  # noqa: E402,F401  (posa hd.pix a 640×360 abans de cap sala)
from hd.pix import Canvas, W, H, R, Pt  # noqa: E402

VISIBLE_H = round(205 * H / 270)  # per sota hi ha la barra de verbs
# Les sales: hd640/rooms a 640×360, hd/rooms a 480×270 (escala.RESOLUCIO).
PKG = 'hd640' if RESOLUCIO == 640 else 'hd'
ROOMS = HERE.parent / PKG / 'rooms'


def load(name):
    return importlib.import_module(f'{PKG}.rooms.{name}')


def has_hd(name):
    return (ROOMS / f'{name}.py').exists()


def render(name, prop_ids=None):
    """→ (fons RGBA, {id: fotograma RGBA})."""
    mod = load(name)
    light = getattr(mod, 'LIGHT', None)
    cv = Canvas(light=light)
    mod.bg(cv)
    props = {}
    for pid, fn in getattr(mod, 'PROPS', {}).items():
        if prop_ids is not None and pid not in prop_ids:
            continue
        pc = Canvas(light=light, transparent=True)
        fn(pc)
        props[pid] = pc.img
    return cv.img, props


def _render_anims(name):
    mod = load(name)
    return {aid: (a['frames'](), a.get('frameDuration', 150)) for aid, a in getattr(mod, 'ANIMS', {}).items()}


# ─── Memòria cau de les animacions ─────────────────────────────────────────
# Una animació són molts renders de la sala sencera (segons cadascun). Es desa a hd/.cache amb una
# clau que depèn de tot el codi de hd/: si no ha canviat res, el sync la reaprofita.
CACHE = HERE / '.cache'


def _code_key(name):
    """Hash del codi que dibuixa la sala: pix.py (i hd640/__init__.py) i els mòduls que fa servir (vegeu _deps)."""
    import hashlib
    tools = HERE.parent
    files = [HERE / 'pix.py', tools / 'hd640' / '__init__.py'] + sorted(_deps(name))
    h = hashlib.sha256()
    for f in files:
        if f.exists():
            h.update(f.relative_to(tools).as_posix().encode())
            h.update(f.read_bytes())
    return h.hexdigest()[:16]


def _deps(name):
    """Fitxers que fa servir una sala (imports al principi o dins funcions), mirant el codi: sales de hd/rooms i de
    hd640/rooms, i també els mòduls de dibuix de gent (hd/characters.py, hd640/draw_characters.py)."""
    import re
    tools = HERE.parent
    seen, todo = set(), [ROOMS / f'{name}.py']
    while todo:
        f = todo.pop()
        if f in seen or not f.exists():
            continue
        seen.add(f)
        src = f.read_text()
        for pkg, mod in re.findall(r'\b(hd640|hd)\.rooms\.(\w+)', src):
            todo.append(tools / pkg / 'rooms' / f'{mod}.py')
        for pkg, mod in re.findall(r'\b(hd640|hd)\.(characters|draw_characters|items)\b', src):
            todo.append(tools / pkg / f'{mod}.py')
        if re.search(r'from hd import characters', src):
            todo.append(tools / 'hd' / 'characters.py')
    return seen


def render_anims(name):
    """→ {id: (fotogrames RGBA, durada de cada fotograma en ms)} (amb memòria cau)."""
    d = CACHE / f'{name}-{_code_key(name)}'
    meta = d / 'anims.json'
    if meta.exists():
        info = json.loads(meta.read_text())
        return {aid: ([Image.open(d / f'{aid}_{i}.png').convert('RGBA') for i in range(a['n'])], a['ms'])
                for aid, a in info.items()}
    anims = _render_anims(name)
    if anims:
        for old in CACHE.glob(f'{name}-*'):
            for f in old.iterdir():
                f.unlink()
            old.rmdir()
        d.mkdir(parents=True, exist_ok=True)
        for aid, (frames, ms) in anims.items():
            for i, f in enumerate(frames):
                f.save(d / f'{aid}_{i}.png')
        meta.write_text(json.dumps({aid: {'n': len(fr), 'ms': ms} for aid, (fr, ms) in anims.items()}))
    return anims


def _sprite(cid):
    art = HERE.parent.parent / 'placeholder-art' / cid
    if not (art / f'{cid}.png').exists():
        return None, None
    sheet = json.loads((art / f'{cid}.json').read_text())
    ch = json.loads((art / f'{cid}.character.json').read_text())
    tags = {t['name']: t['from'] for t in sheet['meta']['frameTags']}
    idx = tags.get('IdleD', 0)
    f = list(sheet['frames'].values())[idx]['frame']
    img = Image.open(art / f'{cid}.png').convert('RGBA').crop((f['x'], f['y'], f['x'] + f['w'], f['y'] + f['h']))
    return img, ch['feet']


def main():
    name = sys.argv[1]
    out = Path(sys.argv[2]) if len(sys.argv) > 2 else Path('.')
    out.mkdir(parents=True, exist_ok=True)
    bg, props = render(name)
    bg.save(out / f'{name}.png')

    def x3(img, path):
        img.crop((0, 0, W, VISIBLE_H)).resize((W * 3, VISIBLE_H * 3), Image.NEAREST).save(path)

    x3(bg, out / f'{name}_x3.png')
    full = bg.copy()
    for p in props.values():
        full.alpha_composite(p)
    if props:
        x3(full, out / f'{name}_props_x3.png')
        sheet = Image.new('RGBA', (W, H * len(props)), (255, 0, 255, 255))
        for i, (pid, p) in enumerate(props.items()):
            sheet.alpha_composite(p, (0, i * H))
        sheet.save(out / f'{name}_props_sheet.png')

    for aid, (frames, ms) in render_anims(name).items():
        gif = []
        for f in frames:
            im = bg.copy()
            im.alpha_composite(f)
            gif.append(im.crop((0, 0, W, VISIBLE_H)).resize((W * 2, VISIBLE_H * 2), Image.NEAREST).convert('RGB'))
        gif[0].save(out / f'{name}_{aid}.gif', save_all=True, append_images=gif[1:], duration=ms, loop=0)

    # Depuració: zones, terra, personatges
    sys.path.insert(0, str(HERE.parent))
    from room_designs import DESIGNS
    dbg = full.copy()
    design = DESIGNS.get(name)
    if design:
        for cid, (x, y) in design['spawns'].items():
            spr, feet = _sprite(cid)
            if spr:
                fx, fy = Pt(x, y)
                dbg.alpha_composite(spr, (fx - feet['x'], fy - feet['y']))
    big = dbg.resize((W * 3, H * 3), Image.NEAREST)
    d = ImageDraw.Draw(big)
    if design:
        d.polygon([(Pt(x, y)[0] * 3 + 1, Pt(x, y)[1] * 3 + 1) for x, y in design['walkable']], outline=(0, 255, 0))
        for tid, t in design['things'].items():
            x0, y0, x1, y1 = R(*t['rect'])
            d.rectangle([x0 * 3, y0 * 3, x1 * 3 + 2, y1 * 3 + 2], outline=(255, 0, 255))
            d.text((x0 * 3 + 2, y0 * 3 + 2), tid, fill=(255, 255, 0))
            wx, wy = Pt(*t['walk'])
            d.ellipse([wx * 3 - 3, wy * 3 - 3, wx * 3 + 3, wy * 3 + 3], outline=(0, 255, 255))
    big.crop((0, 0, W * 3, VISIBLE_H * 3)).save(out / f'{name}_debug_x3.png')
    print(f'✔ {name}: {out}/{name}_x3.png (+ props, debug)')


if __name__ == '__main__':
    main()
