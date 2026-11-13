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
from escala import RESOLUCIO  # noqa: E402
if RESOLUCIO == 640:
    import hd640  # noqa: E402,F401  (posa hd.pix a 640×360 abans de cap sala)
import room_designs  # noqa: E402
from room_designs import DESIGNS, C  # noqa: E402
from draw_items import icon  # noqa: E402
from escala import DESIGN_H, box, n as scaled, pt  # noqa: E402
from hd.pix import W as HD_W, H as HD_H  # noqa: E402
from hd.render import has_hd, load as load_hd, render as render_hd, render_anims as render_hd_anims, front as render_hd_front  # noqa: E402

# La casella de l'inventari: la de la plantilla 9-verb (36×20) passada a la resolució del joc.
from draw_items import W as INV_W, H as INV_H  # noqa: E402

PALETTE = {
    # Iri: el pis i els ordinadors (càlid, nit, pantalles)
    'iri': {'wall': (92, 62, 44), 'wall2': (108, 74, 52), 'floor': (52, 36, 26), 'line': (230, 170, 100), 'text': (255, 226, 180), 'door': (40, 26, 18)},
    # Vet: el bar de carretera i el carrer (neó, fòrmica, groc)
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


MAX_SHEET_W = 4096  # textures més amples no carreguen a moltes GPU (el fons surt negre)


def sheet_cols(frames, frame_w):
    """Fotogrames per fila: tots en una fila mentre el full no passi de MAX_SHEET_W."""
    return max(1, min(frames, MAX_SHEET_W // frame_w))


def paste_grid(frames, frame_w, frame_h):
    """Full d'imatges en graella (d'esquerra a dreta i de dalt a baix)."""
    cols = sheet_cols(len(frames), frame_w)
    rows = (len(frames) + cols - 1) // cols
    sheet = Image.new('RGBA', (frame_w * cols, frame_h * rows), (0, 0, 0, 0))
    for i, f in enumerate(frames):
        sheet.paste(f, ((i % cols) * frame_w, (i // cols) * frame_h))
    return sheet


def aseprite_sheet(name, frames, tags, frame_w, frame_h, spans=None):
    """JSON en format d'exportació d'Aseprite (hash), com els de les plantilles de Benne.
    `spans` (opcional): {etiqueta: nombre de fotogrames} per a les etiquetes animades.
    Els fotogrames van en graella (vegeu sheet_cols)."""
    spans = spans or {}
    cols = sheet_cols(frames, frame_w)
    rows = (frames + cols - 1) // cols
    ranges, i = [], 0
    for tag in tags:
        n = spans.get(tag, 1)
        ranges.append((tag, i, i + n - 1))
        i += n
    return {
        'frames': {
            f'{name} {i}.aseprite': {
                'frame': {'x': (i % cols) * frame_w, 'y': (i // cols) * frame_h, 'w': frame_w, 'h': frame_h},
                'rotated': False, 'trimmed': False,
                'spriteSourceSize': {'x': 0, 'y': 0, 'w': frame_w, 'h': frame_h},
                'sourceSize': {'w': frame_w, 'h': frame_h}, 'duration': 100,
            }
            for i in range(frames)
        },
        'meta': {
            'app': 'https://www.aseprite.org/', 'version': 'provisional (draw_placeholders.py)',
            'image': f'{name}.png', 'format': 'RGBA8888',
            'size': {'w': cols * frame_w, 'h': rows * frame_h}, 'scale': '1',
            'frameTags': [{'name': tag, 'from': a, 'to': b, 'direction': 'forward', 'color': '#000000ff'} for tag, a, b in ranges],
            'layers': [], 'slices': [],
        },
    }


def packed_sheet(name, frames, tags, frame_w, frame_h, spans=None):
    """
    Com paste_grid + aseprite_sheet, però el full és molt més petit: cada fotograma es retalla a la part que té
    píxels (`trimmed`, amb `spriteSourceSize`: Benne el torna a posar al seu lloc) i els fotogrames iguals (p. ex. els
    buits de les pauses d'una animació) comparteixen el mateix tros del full. Sense això, a 640×360 els fulls de les
    sales amb moltes animacions passaven de 8192 px, que moltes GPU no carreguen (el fons surt negre).
    """
    spans = spans or {}
    uniques, index_of, ref = [], {}, []
    for f in frames:
        bbox = f.getchannel('A').getbbox() or (0, 0, 1, 1)
        crop = f.crop(bbox)
        key = (bbox, crop.tobytes())
        if key not in index_of:
            index_of[key] = len(uniques)
            uniques.append((bbox, crop))
        ref.append(index_of[key])
    # Prestatges: dels més alts als més baixos, d'esquerra a dreta, fins a MAX_SHEET_W.
    order = sorted(range(len(uniques)), key=lambda i: -uniques[i][1].height)
    place, x, y, shelf_h, width = {}, 0, 0, 0, 0
    for i in order:
        cw, ch = uniques[i][1].size
        if x + cw > MAX_SHEET_W:
            x, y, shelf_h = 0, y + shelf_h, 0
        place[i] = (x, y)
        x += cw
        shelf_h = max(shelf_h, ch)
        width = max(width, x)
    height = y + shelf_h
    sheet = Image.new('RGBA', (width, height), (0, 0, 0, 0))
    for i, (bbox, crop) in enumerate(uniques):
        sheet.paste(crop, place[i])
    ranges, i = [], 0
    for tag in tags:
        n = spans.get(tag, 1)
        ranges.append((tag, i, i + n - 1))
        i += n
    out_frames = {}
    for k, u in enumerate(ref):
        (bx0, by0, bx1, by1), crop = uniques[u]
        px, py = place[u]
        out_frames[f'{name} {k}.aseprite'] = {
            'frame': {'x': px, 'y': py, 'w': bx1 - bx0, 'h': by1 - by0},
            'rotated': False, 'trimmed': (bx0, by0, bx1, by1) != (0, 0, frame_w, frame_h),
            'spriteSourceSize': {'x': bx0, 'y': by0, 'w': bx1 - bx0, 'h': by1 - by0},
            'sourceSize': {'w': frame_w, 'h': frame_h}, 'duration': 100,
        }
    meta = {
        'frames': out_frames,
        'meta': {
            'app': 'https://www.aseprite.org/', 'version': 'provisional (draw_placeholders.py, retallat)',
            'image': f'{name}.png', 'format': 'RGBA8888',
            'size': {'w': width, 'h': height}, 'scale': '1',
            'frameTags': [{'name': tag, 'from': a, 'to': b, 'direction': 'forward', 'color': '#000000ff'} for tag, a, b in ranges],
            'layers': [], 'slices': [],
        },
    }
    return sheet, meta


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
    sheet = paste_grid(frames, w, h)
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

    hd = (w, h) == (HD_W, HD_H) and has_hd(name)  # art HD (hd/rooms/<sala>.py), si n'hi ha
    if hd:
        bg, hd_props = render_hd(name)
        hd_anims = render_hd_anims(name)
    else:
        bg = Image.new('RGBA', (w, h), (0, 0, 0, 255))
        design['bg'](C(bg))
        # Art provisional: el nom de cada cosa clicable, a sobre, perquè es pugui jugar sense dubtes.
        if LABELS['font'] and design.get('etiquetes', True):
            names = {hs['id']: hs.get('description') or hs['id'] for hs in room.get('hotspots', []) + room.get('props', [])}
            for tid, t in design['things'].items():
                if tid not in names or tid in design.get('sense_etiqueta', ()):
                    continue
                x0, y0, x1, _ = box(*t['rect'], k)
                LABELS['font'].draw_centered(bg, (x0 + x1) / 2, max(1, y0 - 9), names[tid], (255, 240, 200), x1 - x0 + 40)
    frames, tags = [bg], ['BG']
    for prop in room['props']:
        if prop['id'] == 'BG' or (hd and (prop['id'] in hd_anims or prop['id'] == 'davant')):
            continue
        frame = Image.new('RGBA', (w, h), (0, 0, 0, 0))
        if hd:
            if prop['id'] in hd_props:
                frame = hd_props[prop['id']]
        else:
            draw = design['props'].get(prop['id'])
            if draw:
                draw(C(frame))
        frames.append(frame)
        tags.append(prop.get('tag', prop['id']))

    # Animacions de fons (hd ANIMS): decorat no clicable i sempre visible, amb una etiqueta de
    # diversos fotogrames, en bucle si l'animació no diu `'loop': False` (llavors es queda a l'últim).
    # Si la sala encara no el té, s'hi afegeix (amb el `zIndex` de l'animació, si en té). Amb `'prop': <id>`,
    # l'animació no és un prop nou sinó una altra etiqueta d'aquell prop (un script o una indicació d'escena
    # la hi posa: p. ex. els trossos de la zòdiac al pròleg de Ni un ou).
    spans = {}
    defs = getattr(load_hd(name), 'ANIMS', {}) if hd else {}
    for aid, (anim_frames, ms) in (hd_anims.items() if hd else []):
        frames.extend(anim_frames)
        tags.append(aid)
        spans[aid] = len(anim_frames)
        owner = defs.get(aid, {}).get('prop')
        if owner:
            prop = next((p for p in room['props'] if p['id'] == owner), None)
            if prop is not None:
                prop.setdefault('animations', {})[aid] = {'loop': defs[aid].get('loop', True), 'frameDuration': ms}
            continue
        prop = next((p for p in room['props'] if p['id'] == aid), None)
        if prop is None:
            prop = {'id': aid, 'tag': aid, 'zIndex': defs.get(aid, {}).get('zIndex', 1), 'visible': True, 'alpha': 1,
                    'clickable': False}
            room['props'].append(prop)
        extra = {k: v for k, v in prop.get('animations', {}).items() if defs.get(k, {}).get('prop') == aid}
        prop['animations'] = {aid: {'loop': defs.get(aid, {}).get('loop', True), 'frameDuration': ms}, **extra}
        # Si un hotspot té el mateix id, el prop necessita un altre nom a BenneScript.
        if 'scriptName' not in prop and any(h['id'] == aid for h in room.get('hotspots', [])):
            head, *rest = aid.split('_')
            prop['scriptName'] = head + ''.join(s.capitalize() for s in rest) + 'Anim'

    # Capa del davant (hd FRONT): un retall del fons que tapa els personatges que hi ha darrere.
    fr = render_hd_front(name, bg) if hd else None
    if fr:
        img, f = fr
        frames.append(img)
        tags.append('davant')
        prop = next((p for p in room['props'] if p['id'] == 'davant'), None)
        if prop is None:
            prop = {'id': 'davant', 'tag': 'davant', 'visible': True, 'alpha': 1, 'clickable': False}
            room['props'].append(prop)
        prop['animations'] = {'davant': {}}
        # Els props de damunt la barra, un nivell per sobre: amb el mateix zIndex el motor desempata
        # per id i la capa «davant» podria tapar-los (p. ex. «comandament_barra» < «davant»).
        z = f.get('zIndex', 20)
        for p in room['props']:
            if p is prop:
                p['zIndex'], p['baseline'] = z, f['baseline']
            elif p['id'] in f.get('props', ()):
                p['zIndex'], p['baseline'] = z + 1, f['baseline']

    sheet, meta = packed_sheet(name, frames, tags, w, h, spans)
    sheet.save(dir_ / f'{name}.png')
    (dir_ / f'{name}.json').write_text(json.dumps(meta, indent=2) + '\n')
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
    fw, fh = INV_W, INV_H  # la casella de l'inventari
    items = req['items']
    labels = short_labels(items)
    frames = []
    for it in items:
        drawn = icon(it['id'])
        if drawn is not None:
            frames.append(drawn)
            continue
        hue = int(hashlib.md5(it['id'].encode()).hexdigest()[:6], 16)
        color = (80 + hue % 150, 80 + (hue >> 8) % 150, 80 + (hue >> 16) % 150)
        frame = Image.new('RGBA', (fw, fh), (0, 0, 0, 0))
        ImageDraw.Draw(frame).rounded_rectangle([1, 1, fw - 2, fh - 2], radius=3, fill=color + (255,), outline=(255, 255, 255, 255))
        label = small.fit(it['label'] if small.width(it['label']) <= fw - 4 else labels[it['id']], fw - 4)
        small.draw_centered(frame, fw / 2, 5, label, (255, 255, 255), fw)
        frames.append(frame)
    sheet = paste_grid(frames, fw, fh)
    sheet.save(dir_ / 'inventory.png')
    (dir_ / 'inventory.json').write_text(json.dumps(aseprite_sheet('inventory', len(items), [it['id'] for it in items], fw, fh), indent=2) + '\n')
    (dir_ / '.provisional').write_text("Art provisional: esborra aquest fitxer quan el PNG sigui definitiu.\n")
    print(f'✔ art provisional: inventari ({len(items)} objectes)')


def switch_button_image(hover=False):
    """El botó «Canvia» (43×32): l'ull de bou buit de hd/gui.py. Les cares hi van a sobre, en dos controls
    `image` (`CaraIri`, `CaraVet`) que verbs.gui.ts mostra segons qui juga."""
    from hd.gui import canvia_button
    return canvia_button(hover=hover)


def add_switch_button(game_dir: Path):
    """
    La casella del botó «Canvia» a la barra de verbs: dos fotogrames (normal i hover) amb la imatge
    de `switch_button_image`. Es redibuixa mentre hi hagi la marca `.canvia-provisional`.
    """
    d = game_dir / 'assets/images/guis/verbs'
    sheet_path, json_path, marca = d / 'verbs.png', d / 'verbs.json', d / '.canvia-provisional'
    if not json_path.exists():
        return
    meta = json.loads(json_path.read_text())
    tags = meta['meta']['frameTags']
    existents = {t['name']: t['from'] for t in tags}
    if 'CanviaBtn' in existents and not marca.exists():
        return
    frames = meta['frames']
    keys = list(frames)
    first = frames[keys[0]]['frame']
    fw, fh = first['w'], first['h']
    sheet = Image.open(sheet_path).convert('RGBA')
    cols = max(1, sheet.width // fw)
    nous = [t for t in ('CanviaBtn', 'CanviaBtn-hover') if t not in existents]
    rows = (len(keys) + len(nous) + cols - 1) // cols
    if rows * fh > sheet.height:
        bigger = Image.new('RGBA', (sheet.width, rows * fh), (0, 0, 0, 0))
        bigger.paste(sheet, (0, 0))
        sheet = bigger
    base = keys[0].rsplit(' ', 1)[0]
    duration = frames[keys[0]].get('duration', 100)
    n = len(keys)
    for tag in ('CanviaBtn', 'CanviaBtn-hover'):
        if tag in existents:
            idx = existents[tag]
        else:
            idx = n
            n += 1
            tags.append({'name': tag, 'from': idx, 'to': idx, 'direction': 'forward', 'color': '#000000ff'})
        x, y = (idx % cols) * fw, (idx // cols) * fh
        frames[f'{base} {idx}.aseprite'] = {
            'frame': {'x': x, 'y': y, 'w': fw, 'h': fh}, 'rotated': False, 'trimmed': False,
            'spriteSourceSize': {'x': 0, 'y': 0, 'w': fw, 'h': fh}, 'sourceSize': {'w': fw, 'h': fh}, 'duration': duration,
        }
        frame = Image.new('RGBA', (fw, fh), (0, 0, 0, 0))
        frame.paste(switch_button_image(hover=tag.endswith('hover')), (3, 211))
        sheet.paste(frame, (x, y))
    meta['meta']['size'] = {'w': sheet.width, 'h': sheet.height}
    sheet.save(sheet_path)
    json_path.write_text(json.dumps(meta, indent=2) + '\n')
    marca.write_text("Botó «Canvia» provisional (draw_placeholders.py): esborra aquest fitxer quan el dibuix sigui definitiu.\n")
    print('✔ barra de verbs: botó «Canvia»')


def draw_cover_gui(game_dir: Path):
    """Els botons de la portada (GUI `portada`), a pantalla completa: placa fosca amb vora verd blavós i cantons
    retallats; en passar-hi per sobre, més clara i amb la vora verda. Es redibuixen mentre hi hagi la marca
    `.generat` (si algú hi posa art fet a mà, n'ha d'esborrar la marca)."""
    gui = game_dir / 'guis/portada/portada.gui.json'
    d = game_dir / 'assets/images/guis/portada'
    hand_made = (d / 'portada.png').exists() and not (d / '.provisional').exists() and not (d / '.generat').exists()
    if not gui.exists() or hand_made:
        return
    d.mkdir(parents=True, exist_ok=True)
    buttons = [ctl for ctl in json.loads(gui.read_text())['controls'] if ctl.get('type') == 'button']
    res = json.loads((game_dir / 'game-config.json').read_text()).get('resolution', {})
    w, h = res.get('width', 480), res.get('height', 270)
    frames, tags = [], []
    for b in buttons:
        for tag, fill, vora, llum in ((b['id'], (10, 16, 34, 225), (16, 120, 118), (20, 70, 80)),
                                      (f"{b['id']}-hover", (16, 34, 58, 240), (40, 192, 116), (60, 150, 120))):
            f = Image.new('RGBA', (w, h), (0, 0, 0, 0))
            x0, y0 = b['x'], b['y']
            x1, y1 = x0 + b['width'] - 1, y0 + b['height'] - 1
            dr = ImageDraw.Draw(f)
            dr.rectangle([x0 + 1, y0 + 1, x1 - 1, y1 - 1], fill=fill)
            dr.line([(x0 + 2, y0), (x1 - 2, y0)], fill=vora + (255,))           # la vora, amb els cantons retallats
            dr.line([(x0 + 2, y1), (x1 - 2, y1)], fill=vora + (255,))
            dr.line([(x0, y0 + 2), (x0, y1 - 2)], fill=vora + (255,))
            dr.line([(x1, y0 + 2), (x1, y1 - 2)], fill=vora + (255,))
            for (cx, cy) in ((x0 + 1, y0 + 1), (x1 - 1, y0 + 1), (x0 + 1, y1 - 1), (x1 - 1, y1 - 1)):
                f.putpixel((cx, cy), vora + (255,))
            dr.line([(x0 + 3, y0 + 2), (x1 - 3, y0 + 2)], fill=llum + (255,))   # la llum de dalt
            for k in (6, 10):                                                     # dues ratlletes a cada costat
                f.putpixel((x0 + k, y0 + b['height'] // 2), vora + (255,))
                f.putpixel((x1 - k, y0 + b['height'] // 2), vora + (255,))
            frames.append(f)
            tags.append(tag)
    sheet = paste_grid(frames, w, h)
    sheet.save(d / 'portada.png')
    (d / 'portada.json').write_text(json.dumps(aseprite_sheet('portada', len(frames), tags, w, h), indent=2) + '\n')
    (d / '.provisional').unlink(missing_ok=True)
    (d / '.generat').write_text('Botons generats per draw_placeholders.py (draw_cover_gui): esborra aquesta marca si hi poses art fet a mà.\n')
    print('✔ portada: caselles dels botons')


LABELS = {'font': None}


def main(game_dir: Path):
    draw_cover_gui(game_dir)
    add_switch_button(game_dir)
    fonts = game_dir / 'assets/fonts'
    font = BitmapFont(fonts / 'aiguaverne-negreta.xml')
    small = BitmapFont(fonts / 'aiguaverne-regular.xml')
    LABELS['font'] = small
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
