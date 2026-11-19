#!/usr/bin/env python3
"""
L'Última Arrel (com Aigua Verne): la pantalla s'adapta a l'aparell, de 640×288 (un mòbil, 20:9) a 640×360 (un monitor, 16:9).

L'alçada la tria el motor en arrencar (`resolution.minHeight`, la posa adapters/benne/joc.ts). Aquest script hi
prepara les sales i les GUI:

  - GUI: estan dissenyades a 288. La primera vegada, els controls pugen (els menús 36 px, centrats; el diàleg i el
    text del narrador 72 px, a baix; la portada 64) i porten la marca [288]; i cada vegada, `anchorY` diu on van
    quan la pantalla és més alta (els menús al mig, el diàleg i la portada a baix).
  - Sales: l'art és de 640×360, però la majoria només és pintat fins a y = 260 (la resta era sota la barra de
    verbs): la càmera en mostra 640×288 des de dalt, i en un monitor a sota hi ha la franja del HUD. Les pintades
    fins a baix (la portada, cinemàtiques, i les que s'allarguin) es veuen senceres en un monitor, i en un mòbil la
    càmera se'n queda una part (`viewAnchorY`; CAMERA_Y diu quina).

Es pot tornar a executar.

    python3 adapters/benne/tools/hd640/pantalla.py
"""
import json
import sys
from pathlib import Path

from PIL import Image

TOOLS = Path(__file__).resolve().parent.parent
GAME = TOOLS.parents[2] / 'ultima-arrel/src/game'
W, H, H0 = 640, 288, 360
MARCA = '[288]'

# GUI → quant puja (a 288), i on s'enganxa si la pantalla és més alta
PUJA = {
    'dialog': (H0 - H, 'bottom'), 'display-text': (H0 - H, 'bottom'),
    'game-menu': ((H0 - H) // 2, 'center'), 'load-menu': ((H0 - H) // 2, 'center'),
    'save-menu': ((H0 - H) // 2, 'center'), 'settings-menu': ((H0 - H) // 2, 'center'),
    'portada': (64, 'bottom'),
}
# sales pintades fins a baix: què en mostra la càmera en un mòbil (y de dalt; per defecte, el mig)
MIG = (H0 - H) // 2
# el títol de la portada és a dalt de tot
CAMERA_Y = {'portada': 12}


def puja_gui(name, dy, anchor):
    path = GAME / 'guis' / name / f'{name}.gui.json'
    if not path.exists():
        return
    gui = json.loads(path.read_text())
    if MARCA not in (gui.get('description') or ''):
        for c in gui['controls']:
            if 'gridPlacement' in c:
                continue                                   # va amb la seva graella
            if name == 'portada' and c.get('id') == 'version':
                c['y'] = H - (H0 - c['y'])                 # a la mateixa distància de baix que abans
            elif 'y' in c:
                c['y'] -= dy
            if c.get('backgroundAnchor') == 'screen':
                c['backgroundOffsetY'] = c.get('backgroundOffsetY', 0) - dy
        gui['description'] = (gui.get('description') or '') + f' {MARCA}'
        print(f'  GUI {name}: puja {dy} px')
    gui['anchorY'] = anchor
    path.write_text(json.dumps(gui, indent=2, ensure_ascii=False) + '\n')


def pintada_fins_a_baix(room, s=1):
    """Si el fons de la sala té alguna cosa pintada a sota de y = 270 (no és negre). `s`: l'artScale del full."""
    d = GAME / 'assets/images/rooms' / room
    js, png = d / f'{room}.json', d / f'{room}.png'
    if not js.exists() or not png.exists():
        return False
    sheet = json.loads(js.read_text())
    tags = {t['name']: t['from'] for t in sheet['meta']['frameTags']}
    fr = list(sheet['frames'].values())[tags.get('BG', 0)]
    f, src = fr['frame'], fr['spriteSourceSize']
    y0 = 270 * s - src['y']
    if y0 >= f['h']:
        return False
    img = Image.open(png).convert('L').crop((f['x'], f['y'] + max(0, y0), f['x'] + f['w'], f['y'] + f['h']))
    hist = img.histogram()
    bright = sum(n for v, n in enumerate(hist) if v > 24)
    return bright > 0.05 * img.width * img.height


def sales():
    for path in sorted((GAME / 'rooms').glob('*/*.room.json')):
        room = path.parent.name
        data = json.loads(path.read_text())
        before = (data.get('scrollBounds'), data.get('viewAnchorY'))
        if pintada_fins_a_baix(room, data.get('artScale', 1)):
            data['scrollBounds'] = {'x': 0, 'y': 0, 'width': data['size']['width'], 'height': H0}
            data['viewAnchorY'] = round(CAMERA_Y.get(room, MIG) / (H0 - H), 3)
            que = f'sencera en un monitor; en un mòbil, des de y={CAMERA_Y.get(room, MIG)}'
        else:
            data['scrollBounds'] = {'x': 0, 'y': 0, 'width': data['size']['width'], 'height': H}
            data.pop('viewAnchorY', None)
            que = f"{data['size']['width']}×{H} des de dalt"
        if (data.get('scrollBounds'), data.get('viewAnchorY')) != before:
            path.write_text(json.dumps(data, indent=2, ensure_ascii=False) + '\n')
            print(f'  sala {room}: {que}')


if __name__ == '__main__':
    for name, (dy, anchor) in PUJA.items():
        puja_gui(name, dy, anchor)
    sales()
    print(f'✔ Pantalla de {W}×{H} a {W}×{H0}')
    sys.exit(0)
