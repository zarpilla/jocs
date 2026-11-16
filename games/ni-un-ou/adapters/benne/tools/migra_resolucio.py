#!/usr/bin/env python3
"""
Passa un projecte Benne de la resolució de la plantilla 9-verb (352×198) a la del joc (480×270).

`benne:create` ho fa sol en copiar la plantilla. El sync no torna a escriure les GUI ni la geometria
de les sales que ja existeixen, així que això les escala una vegada:

  - game-config.json: la resolució i l'alçada de la llista d'opcions de diàleg;
  - guis/*/*.gui.json: posicions i mides dels controls (no les mides de lletra: les fonts són de
    mapa de bits i només es veuen nítides a múltiples enters);
  - assets/images/guis: els fotogrames de pantalla completa (la barra de verbs, el diàleg);
  - rooms/*/*.room.json: mida, límits de desplaçament, polígons, punts i personatges.

Les imatges de les GUI s'amplien al més proper (×15/11): són provisionals fins que hd/gui.py en
dibuixi les definitives. Ús: python3 migra_resolucio.py <src/game del projecte Benne>
"""
import json
import sys
from pathlib import Path

from PIL import Image

sys.path.insert(0, str(Path(__file__).resolve().parent))
from pixels import nearest  # noqa: E402
from escala import GAME_H, GAME_W  # noqa: E402

DESIGN_W, DESIGN_H = 352, 198   # la resolució de la plantilla 9-verb de Benne
SCALE = GAME_W / DESIGN_W

GUI_KEYS = {'x', 'y', 'width', 'height', 'slotWidth', 'slotHeight', 'spacingX', 'spacingY', 'textOffsetX',
            'textOffsetY', 'backgroundOffsetX', 'backgroundOffsetY', 'wordWrapWidth', 'rowPadding', 'offsetX', 'offsetY'}
ROOM_KEYS = {'x', 'y', 'width', 'height'}


def scale_json(o, keys, lists=()):
    if isinstance(o, dict):
        for k, v in o.items():
            if k in keys and isinstance(v, (int, float)) and not isinstance(v, bool):
                o[k] = round(v * SCALE)
            elif k in lists and isinstance(v, list):
                o[k] = [round(x * SCALE) for x in v]
            else:
                scale_json(v, keys, lists)
    elif isinstance(o, list):
        for v in o:
            scale_json(v, keys, lists)


def load(p):
    return json.loads(p.read_text(encoding='utf-8'))


def save(p, data):
    p.write_text(json.dumps(data, indent=2, ensure_ascii=False) + '\n', encoding='utf-8')


def migrate_gui_image(png: Path):
    meta_path = png.with_suffix('.json')
    meta = load(meta_path)
    frames = meta['frames']
    if not any(f['frame']['w'] == DESIGN_W for f in frames.values()):
        return
    src = Image.open(png).convert('RGBA')
    k = SCALE
    new_w, new_h = round(src.width * k), round(src.height * k)
    out = Image.new('RGBA', (new_w, new_h), (0, 0, 0, 0))
    for f in frames.values():
        r = f['frame']
        x, y, w, h = r['x'], r['y'], r['w'], r['h']
        nx, ny, nw, nh = round(x * k), round(y * k), round(w * k), round(h * k)
        out.paste(nearest(src.crop((x, y, x + w, y + h)), (nw, nh)), (nx, ny))
        f['frame'] = {'x': nx, 'y': ny, 'w': nw, 'h': nh}
        # Fulls retallats: el desplaçament dins la pantalla també s'escala.
        f['spriteSourceSize'] = {key: round(v * k) for key, v in f['spriteSourceSize'].items()}
        f['sourceSize'] = {key: round(v * k) for key, v in f['sourceSize'].items()}
    meta['meta']['size'] = {'w': new_w, 'h': new_h}
    out.save(png)
    save(meta_path, meta)
    print(f'✔ {png.name}: {src.width}×{src.height} → {new_w}×{new_h}')


def main(game: Path):
    config_path = game / 'game-config.json'
    config = load(config_path)
    res = config['resolution']
    if (res['width'], res['height']) == (GAME_W, GAME_H):
        print('Ja és a', GAME_W, '×', GAME_H)
        return
    assert (res['width'], res['height']) == (DESIGN_W, DESIGN_H), res
    config['resolution'] = {'width': GAME_W, 'height': GAME_H}
    dialog = config.get('dialog', {})
    if 'choiceOptionsViewportHeightPx' in dialog:
        dialog['choiceOptionsViewportHeightPx'] = round(dialog['choiceOptionsViewportHeightPx'] * SCALE)
    save(config_path, config)
    print(f'✔ game-config.json: {GAME_W}×{GAME_H}')

    for p in sorted(game.glob('guis/*/*.gui.json')):
        d = load(p)
        scale_json(d.get('controls', []), GUI_KEYS, lists={'colWidths', 'rowHeights'})
        save(p, d)
        print(f'✔ {p.name}')
    for png in sorted(game.glob('assets/images/guis/*/*.png')):
        migrate_gui_image(png)

    for p in sorted(game.glob('rooms/*/*.room.json')):
        d = load(p)
        for key in ('size', 'scrollBounds', 'walkable', 'hotspots', 'points', 'regions', 'props', 'characters'):
            if key in d:
                scale_json(d[key], ROOM_KEYS)
        save(p, d)
        print(f'✔ {p.name}')


if __name__ == '__main__':
    main(Path(sys.argv[1]))
