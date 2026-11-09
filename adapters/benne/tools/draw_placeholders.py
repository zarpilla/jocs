#!/usr/bin/env python3
"""
Dibuixa l'art provisional que demana `npm run benne:sync` (fitxers de .benne-provisional/):

  - per a cada sala nova: un full d'Aseprite (PNG + JSON) amb el fons i un fotograma per a
    cada prop condicional, amb caixes etiquetades on hi ha cada cosa;
  - el full d'objectes d'inventari: la icona de draw_items.py, o una caixa amb el nom si encara no en té.

Només redibuixa el que encara és provisional (marca `.provisional` o PNG inexistent): si un
artista substitueix el PNG i esborra la marca, no es toca mai més.

Ús: python3 draw_placeholders.py <src/game del projecte Benne>
Necessita Pillow (pip install pillow).
"""
import hashlib
import json
import re
import sys
from pathlib import Path

from PIL import Image, ImageDraw

sys.path.insert(0, str(Path(__file__).resolve().parent))
import room_designs  # noqa: E402
from room_designs import DESIGNS, C  # noqa: E402
from draw_items import icon  # noqa: E402
from escala import DESIGN_H, box, n as scaled, pt  # noqa: E402

PALETTE = {
    # passat: fàbrica de ferro-9 (calent, rovell, vapor)
    'iri': {'wall': (92, 62, 44), 'wall2': (108, 74, 52), 'floor': (52, 36, 26), 'line': (230, 170, 100), 'text': (255, 226, 180), 'door': (40, 26, 18)},
    # present: presó orbital (fred, metall, llum blanca)
    'vet': {'wall': (40, 52, 68), 'wall2': (50, 64, 82), 'floor': (24, 30, 40), 'line': (120, 200, 230), 'text': (210, 240, 255), 'door': (16, 20, 28)},
    '': {'wall': (60, 60, 60), 'wall2': (70, 70, 70), 'floor': (35, 35, 35), 'line': (200, 200, 200), 'text': (240, 240, 240), 'door': (20, 20, 20)},
}


class BitmapFont:
    """Font BMFont (XML + PNG) com les de Benne, per escriure les etiquetes amb el mateix estil."""

    def __init__(self, xml_path: Path):
        xml = xml_path.read_text(encoding='utf-8')
        self.chars = {}
        for line in re.findall(r'<char [^>]*/>', xml):
            a = {k: int(v) for k, v in re.findall(r'(\w+)="(-?\d+)"', line)}
            self.chars[a['id']] = a
        page = re.search(r'<page id="0" file="([^"]+)"', xml).group(1)
        self.atlas = Image.open(xml_path.parent / page).convert('RGBA')
        self.line_height = int(re.search(r'lineHeight="(\d+)"', xml).group(1))

    def width(self, text):
        return sum(self.chars.get(ord(c), {'xadvance': 5})['xadvance'] for c in text)

    def wrap(self, text, max_w):
        lines, cur = [], ''
        for word in text.split():
            test = f'{cur} {word}'.strip()
            if cur and self.width(test) > max_w:
                lines.append(cur)
                cur = word
            else:
                cur = test
        return lines + ([cur] if cur else [])

    def draw(self, img, x, y, text, color):
        for c in text:
            g = self.chars.get(ord(c))
            if not g:
                x += 5
                continue
            glyph = self.atlas.crop((g['x'], g['y'], g['x'] + g['width'], g['y'] + g['height']))
            tinted = Image.new('RGBA', glyph.size, color + (255,))
            tinted.putalpha(glyph.getchannel('A'))
            img.alpha_composite(tinted, (x + g['xoffset'], y + g['yoffset']))
            x += g['xadvance']

    def fit(self, text, max_w):
        while text and self.width(text) > max_w:
            text = text[:-1]
        return text

    def draw_centered(self, img, cx, y, text, color, max_w, shadow=(0, 0, 0)):
        for i, line in enumerate(self.wrap(text, max_w)):
            # Dins la imatge, encara que la cosa sigui a la vora.
            x = int(min(max(cx - self.width(line) / 2, 2), img.width - 2 - self.width(line)))
            yy = y + i * self.line_height
            self.draw(img, x + 1, yy + 1, line, shadow)
            self.draw(img, x, yy, line, color)


def aseprite_sheet(name, frames, tags, frame_w, frame_h):
    """JSON en format d'exportació d'Aseprite (hash), com els de les plantilles de Benne."""
    return {
        'frames': {
            f'{name} {i}.aseprite': {
                'frame': {'x': i * frame_w, 'y': 0, 'w': frame_w, 'h': frame_h},
                'rotated': False, 'trimmed': False,
                'spriteSourceSize': {'x': 0, 'y': 0, 'w': frame_w, 'h': frame_h},
                'sourceSize': {'w': frame_w, 'h': frame_h}, 'duration': 100,
            }
            for i in range(frames)
        },
        'meta': {
            'app': 'https://www.aseprite.org/', 'version': 'provisional (draw_placeholders.py)',
            'image': f'{name}.png', 'format': 'RGBA8888',
            'size': {'w': frames * frame_w, 'h': frame_h}, 'scale': '1',
            'frameTags': [{'name': tag, 'from': i, 'to': i, 'direction': 'forward', 'color': '#000000ff'} for i, tag in enumerate(tags)],
            'layers': [], 'slices': [],
        },
    }


def draw_room(dir_: Path, req, font, small):
    name = dir_.name
    w, h = req['width'], req['height']
    pal = PALETTE.get(req.get('era', ''), PALETTE[''])

    bg = Image.new('RGBA', (w, h), (0, 0, 0, 255))
    d = ImageDraw.Draw(bg)
    d.rectangle([0, 0, w, req['floorTop']], fill=pal['wall'])
    for x in range(0, w, 32):  # panells de paret
        d.rectangle([x, 8, x + 30, req['floorTop'] - 6], fill=pal['wall2'])
    d.rectangle([0, req['floorTop'], w, h], fill=pal['floor'])
    d.line([0, req['floorTop'], w, req['floorTop']], fill=pal['line'])
    font.draw(bg, 4, 2, req['title'].upper(), pal['text'])
    small.draw(bg, w - small.width('PROVISIONAL') - 4, 2, 'PROVISIONAL', pal['line'])

    prop_frames, prop_tags = [], []
    for b in req['boxes']:
        x0, y0, x1, y1 = b['x'], b['y'], b['x'] + b['w'], b['y'] + b['h']
        cx = (x0 + x1) / 2
        if b['kind'] == 'exit':
            d.rectangle([x0, y0, x1, y1], fill=pal['door'], outline=pal['line'])
            small.draw_centered(bg, cx, y0 + 6, b['label'], pal['text'], b['w'] + 10)
        elif b['kind'] == 'hotspot':
            d.rectangle([x0, y0, x1, y1], outline=pal['line'])
            small.draw_centered(bg, cx, y0 + 4, b['label'], pal['text'], b['w'] + 8)
        else:
            # Prop condicional: va en un fotograma a part, perquè es pugui amagar.
            frame = Image.new('RGBA', (w, h), (0, 0, 0, 0))
            fd = ImageDraw.Draw(frame)
            fd.rectangle([x0, y0, x1, y1], fill=pal['line'] + (90,), outline=pal['text'])
            small.draw_centered(frame, cx, y0 + 4, b['label'], pal['text'], b['w'] + 8)
            prop_frames.append(frame)
            prop_tags.append(b['id'])

    frames = [bg] + prop_frames
    sheet = Image.new('RGBA', (w * len(frames), h), (0, 0, 0, 0))
    for i, f in enumerate(frames):
        sheet.paste(f, (i * w, 0))
    sheet.save(dir_ / f'{name}.png')
    (dir_ / f'{name}.json').write_text(json.dumps(aseprite_sheet(name, len(frames), ['BG'] + prop_tags, w, h), indent=2) + '\n')
    (dir_ / '.provisional').write_text('Art provisional: esborra aquest fitxer quan el PNG sigui definitiu.\n')
    print(f'✔ art provisional: rooms/{name} ({len(prop_tags)} props condicionals)')


def short_labels(items):
    """Una paraula per objecte que el distingeixi dels altres: «clau anglesa» → «anglesa»."""
    words = {it['id']: it['label'].split() for it in items}
    firsts = [w[0].lower() for w in words.values() if w]
    out = {}
    for it in items:
        w = words[it['id']] or [it['id']]
        out[it['id']] = w[0] if firsts.count(w[0].lower()) == 1 else w[-1]
    return out


def draw_designed(dir_: Path, game_dir: Path, design):
    """Sala amb disseny propi: fons en pixel art + props, i la geometria de Benne a joc."""
    name = dir_.name
    room_path = game_dir / 'rooms' / name / f'{name}.room.json'
    room = json.loads(room_path.read_text())
    w, h = room['size']['width'], room['size']['height']
    k = room_designs.K = h / DESIGN_H  # el disseny és en coordenades de 352×198

    bg = Image.new('RGBA', (w, h), (0, 0, 0, 255))
    design['bg'](C(bg))
    frames, tags = [bg], ['BG']
    for prop in room['props']:
        if prop['id'] == 'BG':
            continue
        frame = Image.new('RGBA', (w, h), (0, 0, 0, 0))
        draw = design['props'].get(prop['id'])
        if draw:
            draw(C(frame))
        frames.append(frame)
        tags.append(prop.get('tag', prop['id']))

    sheet = Image.new('RGBA', (w * len(frames), h), (0, 0, 0, 0))
    for i, f in enumerate(frames):
        sheet.paste(f, (i * w, 0))
    sheet.save(dir_ / f'{name}.png')
    (dir_ / f'{name}.json').write_text(json.dumps(aseprite_sheet(name, len(frames), tags, w, h), indent=2) + '\n')
    (dir_ / '.provisional').write_text('Art provisional: esborra aquest fitxer quan el PNG sigui definitiu.\n')

    # Geometria: el que es pot clicar ha de coincidir amb el que es veu.
    def poly(r):
        x0, y0, x1, y1 = box(*r, k)
        return [{'x': x0, 'y': y0}, {'x': x1, 'y': y0}, {'x': x1, 'y': y1}, {'x': x0, 'y': y1}]

    def xy(x, y):
        x, y = pt(x, y, k)
        return {'x': x, 'y': y}

    things = design['things']
    for hs in room['hotspots']:
        t = things.get(hs['id'])
        if t:
            hs['points'] = poly(t['rect'])
            hs['walkToPoint'] = xy(*t['walk'])
            hs['lookAtPoint'] = xy((t['rect'][0] + t['rect'][2]) // 2, t['rect'][3])
    for prop in room['props']:
        t = things.get(prop['id'])
        if t:
            prop['collider'] = {'points': poly(t['rect'])}
            prop['walkToPoint'] = xy(*t['walk'])
            prop['lookAtPoint'] = xy((t['rect'][0] + t['rect'][2]) // 2, t['rect'][3])
    for ch in room['characters']:
        cid = ch['definition'].split('/')[0]
        if cid in design['spawns']:
            ch['x'], ch['y'] = pt(*design['spawns'][cid], k)
    room['walkable']['polygons'][0]['points'] = [xy(x, y) for x, y in design['walkable']]
    room_path.write_text(json.dumps(room, indent=2, ensure_ascii=False) + '\n')
    print(f'✔ escena provisional: rooms/{name}')


def draw_inventory(dir_: Path, req, small):
    fw, fh = scaled(36), scaled(20)  # la casella de l'inventari
    items = req['items']
    labels = short_labels(items)
    sheet = Image.new('RGBA', (fw * len(items), fh), (0, 0, 0, 0))
    for i, it in enumerate(items):
        drawn = icon(it['id'])
        if drawn is not None:
            sheet.paste(drawn, (i * fw, 0))
            continue
        hue = int(hashlib.md5(it['id'].encode()).hexdigest()[:6], 16)
        color = (80 + hue % 150, 80 + (hue >> 8) % 150, 80 + (hue >> 16) % 150)
        frame = Image.new('RGBA', (fw, fh), (0, 0, 0, 0))
        ImageDraw.Draw(frame).rounded_rectangle([1, 1, fw - 2, fh - 2], radius=3, fill=color + (255,), outline=(255, 255, 255, 255))
        label = small.fit(it['label'] if small.width(it['label']) <= fw - 4 else labels[it['id']], fw - 4)
        small.draw_centered(frame, fw / 2, 5, label, (255, 255, 255), fw)
        sheet.paste(frame, (i * fw, 0))
    sheet.save(dir_ / 'inventory.png')
    (dir_ / 'inventory.json').write_text(json.dumps(aseprite_sheet('inventory', len(items), [it['id'] for it in items], fw, fh), indent=2) + '\n')
    (dir_ / '.provisional').write_text("Art provisional: esborra aquest fitxer quan el PNG sigui definitiu.\n")
    print(f'✔ art provisional: inventari ({len(items)} objectes)')


def add_switch_button(game_dir: Path):
    """La casella del botó «Canvia» a la barra de verbs: dos fotogrames més (normal i hover)."""
    d = game_dir / 'assets/images/guis/verbs'
    sheet_path, json_path = d / 'verbs.png', d / 'verbs.json'
    if not json_path.exists():
        return
    meta = json.loads(json_path.read_text())
    tags = meta['meta']['frameTags']
    if any(t['name'] == 'CanviaBtn' for t in tags):
        return
    frames = meta['frames']
    keys = list(frames)
    first = frames[keys[0]]['frame']
    fw, fh = first['w'], first['h']
    sheet = Image.open(sheet_path).convert('RGBA')
    cols = max(1, sheet.width // fw)
    n = len(keys)
    rows = (n + 2 + cols - 1) // cols
    if rows * fh > sheet.height:
        bigger = Image.new('RGBA', (sheet.width, rows * fh), (0, 0, 0, 0))
        bigger.paste(sheet, (0, 0))
        sheet = bigger
    base = keys[0].rsplit(' ', 1)[0]
    duration = frames[keys[0]].get('duration', 100)
    for i, (tag, fill) in enumerate((('CanviaBtn', (26, 70, 107)), ('CanviaBtn-hover', (40, 96, 140)))):
        idx = n + i
        x, y = (idx % cols) * fw, (idx // cols) * fh
        frame = Image.new('RGBA', (fw, fh), (0, 0, 0, 0))
        ImageDraw.Draw(frame).rectangle([3, 211, 45, 242], fill=fill + (255,))
        sheet.paste(frame, (x, y))
        frames[f'{base} {idx}.aseprite'] = {
            'frame': {'x': x, 'y': y, 'w': fw, 'h': fh}, 'rotated': False, 'trimmed': False,
            'spriteSourceSize': {'x': 0, 'y': 0, 'w': fw, 'h': fh}, 'sourceSize': {'w': fw, 'h': fh}, 'duration': duration,
        }
        tags.append({'name': tag, 'from': idx, 'to': idx, 'direction': 'forward', 'color': '#000000ff'})
    meta['meta']['size'] = {'w': sheet.width, 'h': sheet.height}
    sheet.save(sheet_path)
    json_path.write_text(json.dumps(meta, indent=2) + '\n')
    print('✔ barra de verbs: casella del botó «Canvia»')


def main(game_dir: Path):
    add_switch_button(game_dir)
    fonts = game_dir / 'assets/fonts'
    font = BitmapFont(fonts / 'lucasarts-scumm-solid.xml')
    small = BitmapFont(fonts / 'lucasfont-alternate.xml')
    requests = game_dir / '../../.benne-provisional'
    for req_path in sorted((requests / 'rooms').glob('*.json')):
        dir_ = game_dir / 'assets/images/rooms' / req_path.stem
        dir_.mkdir(parents=True, exist_ok=True)
        if (dir_ / f'{dir_.name}.png').exists() and not (dir_ / '.provisional').exists():
            continue
        if dir_.name in DESIGNS:
            draw_designed(dir_, game_dir, DESIGNS[dir_.name])
        else:
            draw_room(dir_, json.loads(req_path.read_text()), font, small)
    inv = game_dir / 'assets/images/inventory'
    req_path = requests / 'inventory.json'
    if req_path.exists() and (not (inv / 'inventory.png').exists() or (inv / '.provisional').exists()):
        draw_inventory(inv, json.loads(req_path.read_text()), small)


if __name__ == '__main__':
    main(Path(sys.argv[1]))
