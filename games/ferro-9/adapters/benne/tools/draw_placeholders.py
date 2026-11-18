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
from hd.render import has_hd, room_w, load as load_hd, render as render_hd, render_anims as render_hd_anims, fronts as render_hd_fronts  # noqa: E402

# La casella de l'inventari: la de la plantilla 9-verb (36×20) passada a la resolució del joc (49×27, 65×36).
from draw_items import W as INV_W, H as INV_H  # noqa: E402

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
    if design.get('px'):
        k = 1                             # la GEOMETRIA d'una sala en 3D (hd640/rooms/<sala>.py) ja és en píxels de sala

    hd = h == HD_H and has_hd(name)               # art HD (hd/rooms/<sala>.py), si n'hi ha
    if hd and w != room_w(name):
        # Una sala més ampla que la pantalla (ROOM_W al mòdul de la sala): la càmera la recorre seguint el personatge.
        w = room['size']['width'] = room_w(name)
        room.setdefault('scrollBounds', {'x': 0, 'y': 0, 'height': h})['width'] = w
    hd = hd and (w == HD_W or w == room_w(name))
    if hd:
        bg, hd_props = render_hd(name)
        hd_anims = render_hd_anims(name)
    else:
        bg = Image.new('RGBA', (w, h), (0, 0, 0, 255))
        design['bg'](C(bg))
    frames, tags = [bg], ['BG']
    for prop in room['props']:
        if prop['id'] == 'BG' or (hd and (prop['id'] in hd_anims or prop['id'] == 'davant' or prop['id'].startswith('davant_'))):
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
    # la hi posa: p. ex. els trossos de les capes del pròleg).
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

    # Capes del davant (hd FRONT): retalls del fons que tapen els personatges que hi ha darrere. Amb diverses capes,
    # cadascuna un zIndex més amunt segons la seva línia base (de lluny a prop): el motor ordena les capes pel zIndex i
    # després pel nom, i si aquest ordre no és el de la profunditat el personatge queda darrere de totes.
    fronts = sorted(render_hd_fronts(name, bg) if hd else [], key=lambda fr: fr[1]['baseline'])
    for rank, (img, f, fid) in enumerate(fronts):
        f = {**f, 'zIndex': f.get('zIndex', 20) + (rank if len(fronts) > 1 else 0)}
        frames.append(img)
        tags.append(fid)
        prop = next((p for p in room['props'] if p['id'] == fid), None)
        if prop is None:
            prop = {'id': fid, 'tag': fid, 'visible': True, 'alpha': 1, 'clickable': False}
            room['props'].append(prop)
        prop['animations'] = {fid: {}}
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
    # Forats del terra (GEOMETRIA['forats']): on no es pot trepitjar però sí passar-hi pel voltant (i per darrere).
    room['walkable']['polygons'][0]['holes'] = [{'id': f'forat-{n + 1}', 'active': True, 'points': [xy(x, y) for x, y in f]}
                                                for n, f in enumerate(design.get('forats', []))]
    # Regions d'escala de perspectiva (GEOMETRIA['regions']): els personatges es fan petits quan s'allunyen.
    if design.get('regions'):
        room['regions'] = [{**{k: v for k, v in r.items() if k != 'points'}, 'points': [xy(x, y) for x, y in r['points']]}
                           for r in design['regions']]
    # La llum de la sala sobre els personatges (en temps d'execució: characterLights del motor).
    if design.get('characterLights'):
        cl = json.loads(json.dumps(design['characterLights']))
        for light in cl.get('lights', []):
            light['x'], light['y'] = pt(light['x'], light['y'], k)
            light['radius'] = pt(light['radius'], 0, k)[0] - pt(0, 0, k)[0]
        room['characterLights'] = cl
    # L'ombra de contacte sota els personatges (characterShadow del motor); la llum, en coordenades del disseny.
    if design.get('characterShadow'):
        cs = json.loads(json.dumps(design['characterShadow']))
        light = cs.get('light')
        if light and not light.get('direction'):
            light['x'], light['y'] = pt(light['x'], light['y'], k)
        if light and 'reach' in light:
            light['reach'] = pt(light['reach'], 0, k)[0] - pt(0, 0, k)[0]
        room['characterShadow'] = cs
    else:
        room.pop('characterShadow', None)
    # Quant aixafa la càmera el terra (floorSquash del motor): les direccions de caminar es trien sobre el terra.
    if design.get('floorSquash'):
        room['floorSquash'] = design['floorSquash']
    else:
        room.pop('floorSquash', None)
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
    """El botó «Canvia»: mitja Iri i mitja Vet, partides en diagonal entre la fàbrica i les estrelles."""
    art = Path(__file__).resolve().parent.parent / 'placeholder-art'

    def retrat(cid, x0):
        sh = json.loads((art / cid / f'{cid}.json').read_text())
        img = Image.open(art / cid / f'{cid}.png').convert('RGBA')
        tag = next(t['from'] for t in sh['meta']['frameTags'] if t['name'] == 'IdleD')
        f = list(sh['frames'].values())[tag]['frame']
        return img.crop((f['x'] + x0, f['y'] + 3, f['x'] + x0 + 26, f['y'] + 32))

    w, h = 43, 32
    passat = Image.new('RGBA', (w, h), (96, 52, 36, 255))
    pd = ImageDraw.Draw(passat)
    for y in range(0, h, 4):
        pd.line([(0, y), (w, y)], fill=(70, 36, 26, 255))
        for x in range((y // 4) % 2 * 5, w, 10):
            pd.line([(x, y), (x, y + 3)], fill=(70, 36, 26, 255))
    present = Image.new('RGBA', (w, h), (20, 28, 58, 255))
    for x, y in ((30, 4), (37, 9), (33, 25), (40, 20), (26, 14), (39, 29)):
        present.putpixel((x, y), (230, 230, 255, 255))
    tall = Image.new('L', (w, h), 0)
    ImageDraw.Draw(tall).polygon([(0, 0), (26, 0), (17, h), (0, h)], fill=255)
    out = present.copy()
    out.paste(passat, (0, 0), tall)
    cara = Image.new('RGBA', (26, 29), (0, 0, 0, 0))
    meitat = Image.new('L', (26, 29), 0)
    ImageDraw.Draw(meitat).polygon([(0, 0), (17, 0), (8, 29), (0, 29)], fill=255)
    cara.paste(retrat('vet', 11), (0, 0))
    cara.paste(retrat('iri', 12), (0, 0), meitat)
    out.alpha_composite(cara, (9, 3))
    d = ImageDraw.Draw(out)
    d.line([(26, 0), (17, h - 1)], fill=(230, 200, 130, 255))
    if hover:
        out = Image.blend(out, Image.new('RGBA', (w, h), (255, 240, 210, 255)), 0.12)
    # Marc de metall pissarra com la barra de verbs (hd/gui.py): contorn fosc i bisell amb llum de dalt;
    # en hover, el bisell és de llautó encès.
    d = ImageDraw.Draw(out)
    fosc = (7, 9, 14, 255)
    clar, ombra = (((248, 232, 186, 255), (168, 128, 64, 255)) if hover else ((118, 128, 146, 255), (25, 30, 41, 255)))
    d.rectangle([0, 0, w - 1, h - 1], outline=fosc)
    d.line([(1, 1), (w - 2, 1)], fill=clar)
    d.line([(1, 1), (1, h - 2)], fill=clar)
    d.line([(1, h - 2), (w - 2, h - 2)], fill=ombra)
    d.line([(w - 2, 2), (w - 2, h - 2)], fill=ombra)
    for x, y in ((0, 0), (w - 1, 0), (0, h - 1), (w - 1, h - 1)):
        out.putpixel((x, y), (0, 0, 0, 0))
    return out


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
    """Les caselles dels botons de la portada (GUI `portada`): normal i hover, a pantalla completa."""
    gui = game_dir / 'guis/portada/portada.gui.json'
    d = game_dir / 'assets/images/guis/portada'
    if not gui.exists() or ((d / 'portada.png').exists() and not (d / '.provisional').exists()):
        return
    d.mkdir(parents=True, exist_ok=True)
    buttons = [ctl for ctl in json.loads(gui.read_text())['controls'] if ctl.get('type') == 'button']
    res = json.loads((game_dir / 'game-config.json').read_text()).get('resolution', {})
    w, h = res.get('width', 480), res.get('height', 270)
    frames, tags = [], []
    for b in buttons:
        for tag, fill, vora in ((b['id'], (26, 70, 107), (60, 110, 150)), (f"{b['id']}-hover", (40, 96, 140), (150, 230, 190))):
            f = Image.new('RGBA', (w, h), (0, 0, 0, 0))
            box = [b['x'], b['y'], b['x'] + b['width'] - 1, b['y'] + b['height'] - 1]
            ImageDraw.Draw(f).rectangle(box, fill=fill + (235,), outline=vora + (255,))
            frames.append(f)
            tags.append(tag)
    sheet = paste_grid(frames, w, h)
    sheet.save(d / 'portada.png')
    (d / 'portada.json').write_text(json.dumps(aseprite_sheet('portada', len(frames), tags, w, h), indent=2) + '\n')
    (d / '.provisional').write_text('Art provisional: esborra aquest fitxer quan el PNG sigui definitiu.\n')
    print('✔ portada: caselles dels botons')


def main(game_dir: Path):
    draw_cover_gui(game_dir)
    add_switch_button(game_dir)
    fonts = game_dir / 'assets/fonts'
    font = BitmapFont(fonts / 'ferro-negreta.xml')
    small = BitmapFont(fonts / 'ferro-regular.xml')
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
