#!/usr/bin/env python3
"""
`npm run full-sales` (des de games/<joc>/): un full amb totes les sales del joc, tal com són al projecte Benne.

Cada sala es composa amb el fons i els props visibles en començar (el primer fotograma, per ordre de zIndex), sense
personatges, a 1×. De les pantalles, només el fons: els props els mou el guió. Primer les **pantalles** (la portada i les cinemàtiques) i després les **sales**, en l'ordre en què
s'hi arriba des de la portada (seguint el contingut de `game/data`). Els crèdits i els postcrèdits no hi surten.
Les sales s'escapcen a y = 260, on s'acaba el que es veu (la resta queda sota el tauler o els botons).

  python3 tools/full_sales.py [<joc>] [--sortida <fitxer.png>] [--tot]

Sense `<joc>`, el de la carpeta des d'on s'executa. Sense `--sortida`, va a la carpeta `referencia/` del repo de la
web (`../malaherbasoft/referencia/<joc>-sales.png`) si existeix, o a `games/<joc>/<joc>-sales.png`. Amb `--tot`, també
els crèdits i els postcrèdits.
"""
import argparse
import json
import re
from collections import deque
from pathlib import Path

from PIL import Image, ImageDraw, ImageFont

ARREL = Path(__file__).resolve().parent.parent
WEB = ARREL.parent / 'malaherbasoft'

COLUMNES = 4
AMPLE = 2680        # 4 sales de 640 per fila
MARGE = 24
ESPAI = 24          # entre sales d'una fila
FONS = (22, 20, 26)
C_TITOL = (240, 230, 214)
C_SECCIO = (170, 150, 120)
C_PEU = (200, 195, 185)
COL = 640           # amplada d'una columna: les sales amples n'ocupen més d'una
ALT_SALA = 260      # les sales es veuen fins aquí (la resta és sota el tauler o els botons)
OMET = {'credits', 'postcredits'}


def font(mida, negreta=False):
    nom = 'DejaVuSans-Bold.ttf' if negreta else 'DejaVuSans.ttf'
    try:
        return ImageFont.truetype(f'/usr/share/fonts/truetype/dejavu/{nom}', mida)
    except OSError:
        return ImageFont.load_default(mida)


def joc_actual(arg):
    if arg:
        return arg
    cwd = Path.cwd().resolve()
    jocs = ARREL / 'games'
    if jocs in cwd.parents:
        return cwd.relative_to(jocs).parts[0]
    raise SystemExit('De quin joc? Executa-ho des de games/<joc>/ o passa el nom.')


def titol(joc_dir):
    game = json.loads((joc_dir / 'game/data/game.json').read_text())
    textos = {}
    for f in (joc_dir / 'game/locales' / game['defaultLocale']).glob('*.json'):
        textos.update(json.loads(f.read_text()))
    return game, textos.get(game.get('title', ''), joc_dir.name)


def ordre(joc_dir, game, sales):
    """Les sales en l'ordre en què s'hi arriba: des de la portada, el pròleg i l'inici, seguint qualsevol menció
    d'una sala al contingut d'una altra (sortides, goTo, finals). Les que no s'hi troben, al final."""
    dades = joc_dir / 'game/data'
    text = {s: (dades / 'rooms' / f'{s}.json').read_text() if (dades / 'rooms' / f'{s}.json').exists() else ''
            for s in sales}
    patro = re.compile(r'"(' + '|'.join(map(re.escape, sorted(sales, key=len, reverse=True))) + r')"')
    llavors = [game.get('cover'), game.get('intro')] + [v.get('room') for v in (game.get('start') or {}).values()]
    vist, cua, sortida = set(), deque(s for s in llavors if s in sales), []
    while cua:
        s = cua.popleft()
        if s in vist:
            continue
        vist.add(s)
        sortida.append(s)
        cua.extend(m for m in patro.findall(text[s]) if m not in vist)
    return sortida + sorted(set(sales) - vist)


def full_de_sala(dir_sala):
    """{tag: imatge del primer fotograma, a la mida de la sala}."""
    jsons = [f for f in dir_sala.glob('*.json')]
    tags = {}
    for j in jsons:
        d = json.loads(j.read_text())
        img = Image.open(dir_sala / d['meta']['image']).convert('RGBA')
        frames = list(d['frames'].values()) if isinstance(d['frames'], dict) else d['frames']
        for t in d['meta'].get('frameTags', []):
            tags[t['name']] = (img, frames[t['from']])
    return tags


def composa(benne, sala, amb_props):
    room = json.loads((benne / 'rooms' / sala / f'{sala}.room.json').read_text())
    w, h = room['size']['width'], room['size']['height']
    tags = full_de_sala(benne / 'assets/images/rooms' / sala)
    lienzo = Image.new('RGBA', (w, h), (0, 0, 0, 255))
    props = sorted(enumerate(room.get('props', [])), key=lambda ip: (ip[1].get('zIndex', 0), ip[0]))
    for _, p in props:
        if not p.get('visible', True) or (not amb_props and p.get('tag') != 'BG' and p.get('id') != 'BG'):
            continue
        tag = next(iter(p.get('animations') or {}), None) or p.get('tag')
        if tag not in tags:
            tag = p.get('tag')
        if tag not in tags:
            continue
        img, f = tags[tag]
        r, o = f['frame'], f['spriteSourceSize']
        tros = img.crop((r['x'], r['y'], r['x'] + r['w'], r['y'] + r['h']))
        alpha = p.get('alpha', 1)
        if alpha < 1:
            tros.putalpha(tros.getchannel('A').point(lambda a: int(a * alpha)))
        lienzo.alpha_composite(tros, (o['x'], o['y']))
    rgb = lienzo.convert('RGB')
    if rgb.height >= 720:  # art a 2× (els jocs d'abans)
        rgb = rgb.resize((rgb.width // 2, rgb.height // 2), Image.LANCZOS)
    if amb_props and rgb.height > ALT_SALA:
        rgb = rgb.crop((0, 0, rgb.width, ALT_SALA))
    return room.get('name') or sala, rgb


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('joc', nargs='?')
    ap.add_argument('--sortida')
    ap.add_argument('--tot', action='store_true')
    args = ap.parse_args()

    joc = joc_actual(args.joc)
    joc_dir = ARREL / 'games' / joc
    benne = joc_dir / joc / 'src/game'
    game, nom_joc = titol(joc_dir)

    sales = [d.name for d in sorted((benne / 'rooms').iterdir()) if (d / f'{d.name}.room.json').exists()]
    if not args.tot:
        sales = [s for s in sales if s not in OMET]
    dades = joc_dir / 'game/data/rooms'

    def es_pantalla(s):
        f = dades / f'{s}.json'
        return s == game.get('cover') or (f.exists() and 'cutscene' in json.loads(f.read_text()))

    seccions = {'PANTALLES': [], 'SALES': []}
    for s in ordre(joc_dir, game, sales):
        pantalla = es_pantalla(s)
        nom, img = composa(benne, s, amb_props=not pantalla)
        if s == game.get('cover'):
            nom = nom_joc
        seccions['PANTALLES' if pantalla else 'SALES'].append((f'{nom}  ·  {s}', img))

    f_titol, f_seccio, f_peu = font(56, True), font(26, True), font(22)
    peu_h = 12 + 26

    # Primer es col·loca tot, i després es pinta.
    posicions, y = [], 112
    for seccio, llista in seccions.items():
        if not llista:
            continue
        posicions.append(('seccio', seccio, (MARGE, y)))
        y += 40
        col, alt_fila = 0, 0
        for peu, img in llista:
            ample = -(-img.width // COL)
            if col and col + ample > COLUMNES:
                y += alt_fila + peu_h + 26
                col, alt_fila = 0, 0
            posicions.append(('sala', (peu, img), (MARGE + col * (COL + ESPAI), y)))
            col += ample
            alt_fila = max(alt_fila, img.height)
        y += alt_fila + peu_h + 40
    full = Image.new('RGB', (AMPLE, y), FONS)
    dib = ImageDraw.Draw(full)
    dib.text((MARGE, 24), f'{nom_joc} — sales', font=f_titol, fill=C_TITOL)
    for tipus, cosa, (x, yy) in posicions:
        if tipus == 'seccio':
            dib.text((x, yy), cosa, font=f_seccio, fill=C_SECCIO)
        else:
            peu, img = cosa
            full.paste(img, (x, yy))
            dib.text((x, yy + img.height + 10), peu, font=f_peu, fill=C_PEU)

    if args.sortida:
        sortida = Path(args.sortida)
    elif (WEB / 'referencia').is_dir():
        sortida = WEB / 'referencia' / f'{joc}-sales.png'
    else:
        sortida = joc_dir / f'{joc}-sales.png'
    full.save(sortida, optimize=True)
    n = sum(len(v) for v in seccions.values())
    print(f'{sortida}  ({n} sales, {full.width}×{full.height})')


if __name__ == '__main__':
    main()
