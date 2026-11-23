#!/usr/bin/env python3
"""
La Conjura de l'Avet — làmina de revisió dels personatges, a escala relativa (tots a 1×, tal com surten al joc) i ×3.

Llegeix els fulls de Benne que fa adapters/benne/tools/draw_characters.py (placeholder-art/<id>/). A dalt, tots de
cara (l'IdleD), amb l'Iri i la Vet també amb la roba `Monjo`; a sota, el detall de cada un: l'Idle de cara, de perfil,
d'esquena i en 3/4, el Talk de cara, dels que caminen, tres passes de perfil i, d'en Sunifred, la DormD; tots amb els peus a la mateixa línia
de terra. A sota de cada un, el nom i l'alçada en píxels.

Ús: python3 personatges.py  →  personatges.png
"""
import json
import sys
from pathlib import Path

from PIL import Image, ImageDraw

HERE = Path(__file__).resolve().parent
TOOLS = HERE.parents[1] / 'adapters/benne/tools'
ART = TOOLS.parent / 'placeholder-art'
sys.path.insert(0, str(TOOLS))
from pixels import nearest  # noqa: E402

# (id, roba)
ORDRE = [('iri', ''), ('iri', 'Monjo'), ('vet', ''), ('vet', 'Monjo'), ('ingilberga', ''), ('gueraula', ''),
         ('ponc', ''), ('sunifred', ''), ('bonfill', ''), ('ramon', ''), ('sanca', ''), ('joanet', ''),
         ('ermessenda', ''), ('gombau', ''), ('arnulf', '')]
NOMS = {'iri': 'Iri', 'vet': 'Vet', 'ingilberga': 'Ingilberga', 'gueraula': 'Gueraula', 'ponc': 'Ponç',
        'sunifred': 'Sunifred', 'bonfill': 'Bonfill', 'ramon': 'Ramon', 'sanca': 'Sança', 'joanet': 'Joanet',
        'ermessenda': 'Ermessenda', 'gombau': 'Gombau', 'arnulf': 'Arnulf'}
S = 3
FONS = (86, 74, 52)
TERRA = (60, 46, 30)


def full(cid):
    meta = json.loads((ART / cid / f'{cid}.json').read_text())
    sheet = Image.open(ART / cid / f'{cid}.png').convert('RGBA')
    ch = json.loads((ART / cid / f'{cid}.character.json').read_text())
    frames = list(meta['frames'].values())
    tags = {t['name']: [frames[i]['frame'] for i in range(t['from'], t['to'] + 1)] for t in meta['meta']['frameTags']}

    def get(tag, i=0):
        if tag not in tags:
            return None
        r = tags[tag][min(i, len(tags[tag]) - 1)]
        return sheet.crop((r['x'], r['y'], r['x'] + r['w'], r['y'] + r['h']))
    return get, (ch['feet']['x'], ch['feet']['y'])


def alcada(img):
    b = img.getbbox()
    return b[3] - b[1] if b else 0


def main():
    cols = []
    fulls = {}
    for cid, roba in ORDRE:
        if cid not in fulls:
            fulls[cid] = full(cid)
        get, feet = fulls[cid]
        cel = [get(f'{roba}IdleD'), get(f'{roba}IdleL'), get(f'{roba}IdleU'), get(f'{roba}IdleDL'),
               get(f'{roba}TalkD', 1)]
        for i in (1, 3, 5):
            cel.append(get(f'{roba}WalkL', i))
        cel += [get(f'{roba}DormD', 0), get(f'{roba}DormD', 2)]      # en Sunifred, adormit (i roncant)
        nom = NOMS[cid] + (f' ({roba.lower()})' if roba else '')
        cols.append((nom, [c for c in cel if c is not None], feet, alcada(get(f'{roba}IdleD'))))
    gap = 3
    # a dalt, la fila de tots plegats (l'Idle de cara, a escala); a sota, el detall de cada un, tres per fila
    files = [[(nom, [cel[0]], feet, h) for nom, cel, feet, h in cols]]
    files += [cols[i:i + 3] for i in range(0, len(cols), 3)]
    amples = [sum(max(sum(c.width for c in cel) + gap * (len(cel) - 1), 16 if n == 0 else 0) + 16
                  for _, cel, _, _ in fila) for n, fila in enumerate(files)]
    W = max(amples) + 12
    alt = [max(f[2][1] for f in fila) for fila in files]
    H = sum(a + 22 for a in alt) + 6
    out = Image.new('RGBA', (W, H), FONS + (255,))
    d = ImageDraw.Draw(out)
    y = 4
    labels = []
    for n, (fila, a) in enumerate(zip(files, alt)):
        ground = y + a
        d.rectangle([0, ground, W, ground + 1], fill=TERRA)
        x = 8
        for nom, cel, feet, h in fila:
            x0 = x
            for c in cel:
                out.alpha_composite(c, (x, ground - feet[1]))
                x += c.width + gap
            labels.append((x0, ground + 4 + (8 if n == 0 and len(labels) % 2 else 0),
                           f'{nom.split(" ")[0]} {h}' if n == 0 else f'{nom}: {h} px'))
            x += 16 - gap
        y = ground + 22
    big = nearest(out, (W * S, H * S))
    d = ImageDraw.Draw(big)
    for lx, ly, text in labels:
        d.text((lx * S + 1, ly * S + 1), text, fill=(20, 14, 10))
        d.text((lx * S, ly * S), text, fill=(240, 228, 200))
    big.save(HERE / 'personatges.png')
    print('personatges.png', big.size)


if __name__ == '__main__':
    main()
