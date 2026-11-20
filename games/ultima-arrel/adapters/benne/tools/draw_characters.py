#!/usr/bin/env python3
"""
Els fulls dels personatges de L'Última Arrel, amb el format que espera Benne (full d'Aseprite PNG + JSON amb
etiquetes, i el .character.json). El dibuix és a hd/arrel.py; aquí només es munten els fulls.

Una sola mida, a 1× (com les sales en 3D): cada personatge es dibuixa a la seva alçada (guio/fitxes-sales.md), no
s'escala. A les sales «de lluny», la Iri fa ≈68 px, la Vet ≈60, l'àvia ≈78, la Senyora Pla i la Txell ≈85,
l'Espora ≈35, les fades ≈32 (més la cresta) i els gripaus ≈34-39.

La Vet té, a més, una **mida gran** (prefix `Gran`: GranIdleD, GranWalkL...; hd/gran.py), redibuixada a ×1,5 per a la
caseta d'obra i el campament de les Fades (es van pintar per a personatges de 97 px). Va al mateix full, en files a
sota, amb fotogrames que són els d'1× escalats (`sizeVariants: {"Gran": 1.5}` al .character.json; la roba `Gran`
amb `inRoom` a game/data/characters.json la tria a aquestes sales).

Animacions (L, D, U; Benne fa el mirall per a R):
  - **persones** (iri, vet, avia, pla, txell): IdleL/D/U/DL/UL (4: respira), WalkL/D/U/DL/UL (6), TalkL/D/U/DL/UL (2),
    BlinkD/L/DL i LookD/DL (les micro-accions de quan són quietes; `idleActions`). El 3/4 (DL, UL; DR i UR són el
    mirall), perquè les sales tenen la càmera arran de terra i una mica de biaix.
  - **l'Espora**: IdleL/D/U (4: respira), WalkL/D/U (6: passes curtes; al pròleg torna a casa), TalkL/D/U (2: la
    barba i la mà amunt), BlinkD/L (darrere les ulleres).
  - **les fades** (urtica, pica, card): IdleL/D/U (4: les ales baten i el cos sura), TalkL/D/U (4), BlinkD/L.
  - **els gripaus** (bufo, gripau): IdleL/D/U (4: la gola s'infla), TalkL/D/U (2), BlinkD/L.
Els fotogrames es retallen al que ocupa el personatge (tots els d'un full, la mateixa capsa), i els peus, el punt
de parlar i el col·lisionador es calculen a partir del dibuix.

Surt a adapters/benne/placeholder-art/<id>/ (d'on el copia `npm run benne:sync` mentre el personatge porti la marca
`.provisional`). Amb `--installa`, també el copia ja al projecte Benne (el full a assets/images/characters/<id>/ i
els camps del sprite al .character.json), com faria el sync.

Ús (des d'aquesta carpeta):
    python3 draw_characters.py [--installa] [id ...]
La làmina de revisió: python3 ../../../guio/art/personatges.py
"""
import json
import math
import sys
from pathlib import Path

from PIL import Image

sys.path.insert(0, str(Path(__file__).resolve().parent))
from hd import arrel as A  # noqa: E402
from hd import gran as G  # noqa: E402

OUT = Path(__file__).resolve().parent.parent / 'placeholder-art'
GAME = Path(__file__).resolve().parents[3] / 'ultima-arrel/src/game'
CLEAR = (0, 0, 0, 0)
SPRITE_FIELDS = ['walkSpeed', 'walkToPoint', 'talkPoint', 'feet', 'collider', 'animations', 'clickable', 'display',
                 'artScale', 'idleActions', 'sizeVariants']

# La mida gran (hd/gran.py): la Vet, a la caseta d'obra i al campament de les Fades (les sales que es van pintar per a
# personatges de 97 px). Etiquetes amb el prefix `Gran` (GranIdleD, GranWalkL...), al mateix full.
GRAN = 'Gran'
AMB_GRAN = {'vet'}

# La respiració (Idle de quatre fotogrames): no es mou cap píxel de la silueta; només la clariana del pit puja i baixa
# (+5 %, +10 %, +5 %). A 1×, moure el cos 1 px amunt o avall semblava arronsar les espatlles.
RESPIRA = (0.0, 0.05, 0.10, 0.05)
IDLE_MS = 650                                   # cada fotograma: un cicle de 2,6 s (en repòs, sense pressa)


# ─── Fulls ──────────────────────────────────────────────────────────────────

def durations(tags, walk=(90, 100), talk=140, idle=IDLE_MS):
    anims = {}
    for t, _ in tags:
        a = {'loop': True}
        if 'Blink' in t or 'Look' in t:                 # micro-accions: un sol cop i torna a l'Idle
            a = {'loop': False, 'frameDuration': 75 if 'Blink' in t else 260}
        elif 'Walk' in t:
            a['frameDuration'] = walk[0] if t.endswith('L') else walk[1]
        elif 'Talk' in t:
            a['frameDuration'] = talk
        elif 'Idle' in t:
            a['frameDuration'] = idle
        anims[t] = a
    return anims


def retalla(tags, feet, marge=1):
    """Retalla tots els fotogrames a la capsa que ocupen tots plegats (amb `marge`); torna els tags i els peus nous.
    Per sota, fins als peus (i el que en surti)."""
    box = None
    for _, imgs in tags:
        for im in imgs:
            b = im.getbbox()
            if b:
                box = b if box is None else (min(box[0], b[0]), min(box[1], b[1]), max(box[2], b[2]), max(box[3], b[3]))
    w, h = tags[0][1][0].size
    y0 = max(0, box[1] - marge)
    y1 = min(h, max(box[3], feet[1] + 1) + marge)
    # d'ample, simètric respecte dels peus: quan Benne en fa el mirall (R), el personatge no fa cap salt
    fx = feet[0]
    half = max(fx - (box[0] - marge), (box[2] - 1 + marge) - fx)
    W = 2 * half + 1

    def cut(im):
        out = Image.new('RGBA', (W, y1 - y0), CLEAR)
        out.paste(im.crop((0, y0, w, y1)), (half - fx, 0))
        return out
    out = [(n, [cut(im) for im in imgs]) for n, imgs in tags]
    return out, (half, feet[1] - y0)


def collider(img, feet):
    """Un hexàgon a la mida de la figura (el fotograma IdleD), una mica més estret que la silueta."""
    x0, y0, x1, y1 = img.getbbox()
    xm, ym = (x0 + x1) / 2, (y0 + y1) / 2
    dx = (x1 - x0) * 0.32
    pts = [(xm - dx * 0.8, y0 + 1), (xm + dx * 0.8, y0 + 1), (xm + dx, ym), (xm + dx * 0.8, feet[1]),
           (xm - dx * 0.8, feet[1]), (xm - dx, ym)]
    return {'points': [{'x': round(x), 'y': round(y)} for x, y in pts]}


def retalla_gran(gran, crop, w, h):
    """Retalla les figures grans al fotograma d'1× escalat: `crop` = (x0, y0), la cantonada d'1× dins la figura gran
    (ja entera, gràcies a `sub`); w×h, el fotograma d'1×. Comprova que no en surti res."""
    W, H = math.ceil(w * G.K), math.ceil(h * G.K)
    x0, y0 = crop
    out = []
    for name, imgs in gran:
        cut = []
        for im in imgs:
            b = im.getbbox()
            assert b[0] >= x0 and b[1] >= y0 and b[2] <= x0 + W and b[3] <= y0 + H, (name, b, (x0, y0, W, H))
            cut.append(im.crop((x0, y0, x0 + W, y0 + H)))
        out.append((name, cut))
    return out


def gran_sub(feet_in, feet):
    """La cantonada del fotograma d'1× dins el dibuix sense retallar, a ×K: (desplaçament `sub`, cantonada entera)."""
    x0, y0 = feet_in[0] - feet[0], feet_in[1] - feet[1]
    X, Y = x0 * G.K, y0 * G.K
    sub = (math.ceil(X) - X, math.ceil(Y) - Y)
    return sub, (math.ceil(X), math.ceil(Y))


def write(cid, tags, feet, extra, gran=None):
    """tags: [(nom, [imatges])]. Escriu <id>.png, <id>.json (Aseprite) i <id>.character.json a placeholder-art.
    `gran(sub)` → les etiquetes de la mida gran sense retallar (hd/gran.py): van al mateix full, en files a sota, amb
    fotogrames 1,5 vegades més grans (`sizeVariants` al .character.json)."""
    feet_in = feet
    tags, feet = retalla(tags, feet)
    w, h = tags[0][1][0].size
    blocs = [tags]
    if gran:
        sub, crop = gran_sub(feet_in, feet)
        blocs.append(retalla_gran(gran(sub), crop, w, h))
    # cada mida, en files pròpies (una textura no pot fer més de 4096 d'ample)
    places, y = [], 0
    for bloc in blocs:
        frames = [img for _, imgs in bloc for img in imgs]
        fw, fh = frames[0].size
        rows = -(-len(frames) // (4096 // fw))
        cols = -(-len(frames) // rows)
        places += [(img, (i % cols) * fw, y + (i // cols) * fh) for i, img in enumerate(frames)]
        y += rows * fh
    sheet = Image.new('RGBA', (max(x + img.width for img, x, _ in places), y), CLEAR)
    for img, x, yy in places:
        sheet.paste(img, (x, yy))
    d = OUT / cid
    d.mkdir(parents=True, exist_ok=True)
    sheet.save(d / f'{cid}.png')
    frame_tags, i = [], 0
    for name, imgs in (t for bloc in blocs for t in bloc):
        frame_tags.append({'name': name, 'from': i, 'to': i + len(imgs) - 1, 'direction': 'forward', 'color': '#000000ff'})
        i += len(imgs)
    meta = {
        'frames': {f'{cid} {n}.aseprite': {
            'frame': {'x': x, 'y': yy, 'w': img.width, 'h': img.height}, 'rotated': False, 'trimmed': False,
            'spriteSourceSize': {'x': 0, 'y': 0, 'w': img.width, 'h': img.height},
            'sourceSize': {'w': img.width, 'h': img.height}, 'duration': 100,
        } for n, (img, x, yy) in enumerate(places)},
        'meta': {'app': 'https://www.aseprite.org/', 'version': 'draw_characters.py', 'image': f'{cid}.png',
                 'format': 'RGBA8888', 'size': {'w': sheet.width, 'h': sheet.height}, 'scale': '1',
                 'frameTags': frame_tags, 'layers': [], 'slices': []},
    }
    frames = [img for _, imgs in tags for img in imgs]
    tags = [t for bloc in blocs for t in bloc]
    (d / f'{cid}.json').write_text(json.dumps(meta, indent=2) + '\n')
    idle = dict(tags).get('IdleD', frames)[0]
    fx, fy = feet
    character = {
        'id': cid, 'name': cid, 'description': '', 'clickable': True, 'display': {'aseprite': True},
        'walkSpeed': extra.pop('walkSpeed'),
        'walkToPoint': {'x': fx + extra.pop('davant', 22), 'y': fy},
        'talkPoint': {'x': fx, 'y': -2},
        'feet': {'x': fx, 'y': fy},
        'collider': collider(idle, feet),
        **extra,
    }
    (d / f'{cid}.character.json').write_text(json.dumps(character, indent=2) + '\n')
    print(f'✔ {cid}: {len(places)} fotogrames ({w}×{h}{" i grans" if gran else ""}), {len(tags)} etiquetes, '
          f'peus a {feet}')
    return tags


def installa(cid):
    """Com el sync: el full a assets/images/characters/<id>/ i els camps del sprite al .character.json del projecte
    (la resta del .character.json, com el nom o el color de la veu, no es toca)."""
    src = OUT / cid
    path = GAME / 'characters' / cid / f'{cid}.character.json'
    if not path.exists():
        print(f'  (no hi ha {path.relative_to(GAME)}: el farà el sync)')
        return
    art = GAME / 'assets/images/characters' / cid
    art.mkdir(parents=True, exist_ok=True)
    (art / f'{cid}.png').write_bytes((src / f'{cid}.png').read_bytes())
    (art / f'{cid}.json').write_text((src / f'{cid}.json').read_text())
    sprite = json.loads((src / f'{cid}.character.json').read_text())
    current = json.loads(path.read_text())
    for k in SPRITE_FIELDS:
        if k in sprite:
            current[k] = sprite[k]
        else:
            current.pop(k, None)
    current['defaultVerb'] = sprite.get('defaultVerb', current.get('defaultVerb'))
    path.write_text(json.dumps(current, indent=2, ensure_ascii=False) + '\n')
    print(f'  → instal·lat al projecte ({art.relative_to(GAME.parents[2])})')


# ─── Persones ───────────────────────────────────────────────────────────────

DIRS = ('L', 'D', 'U', 'DL', 'UL')
PERSONA_FEET = (25, 83 + A.PAD)


def person_tags(spec, dirs=DIRS, figura=A.figura, respira=A.respira, prefix=''):
    """Les etiquetes d'una persona; amb `figura` i `respira` de hd/gran.py (i `prefix`), les de la mida gran."""
    out = []
    for f in dirs:
        base = figura(spec, f)
        out.append((f'Idle{f}', [respira(base, spec, k) for k in RESPIRA]))
    for f in dirs:
        out.append((f'Walk{f}', [figura(spec, f, walk=k) for k in range(6)]))
    for f in dirs:
        out.append((f'Talk{f}', [figura(spec, f), figura(spec, f, talk=True)]))
    # micro-accions de quan és quiet (idleActions del motor): parpellejar i mirar al voltant (on es veu la cara)
    for f in dirs:
        if f in ('D', 'L', 'DL'):
            out.append((f'Blink{f}', [figura({**spec, 'closed': True}, f)] * 2))
    for f in dirs:
        if f in ('D', 'DL'):
            out.append((f'Look{f}', [figura({**spec, 'mira': m}, f) for m in (-1, -1, -1, 0, 1, 1, 1, 0)]))
    return [(prefix + n, imgs) for n, imgs in out]


def gran_tags(spec):
    """`gran(sub)` per a `write`: les mateixes etiquetes a ×1,5, amb el prefix `Gran`."""
    def make(sub):
        return person_tags(spec, figura=lambda s, f, **kw: G.figura(s, f, sub=sub, **kw),
                           respira=lambda img, s, k: G.respira(img, s, k, sub=sub), prefix=GRAN)
    return make


def persona(cid, spec, walk_speed, verb, walk=(90, 100)):
    tags = person_tags(spec)
    gran = gran_tags(spec) if cid in AMB_GRAN else None
    names = tags + ([(GRAN + n, imgs) for n, imgs in tags] if gran else [])
    extra = {
        'walkSpeed': walk_speed, 'animations': durations(names, walk=walk), 'defaultVerb': verb,
        # quan és quiet, de tant en tant parpelleja i, si fa estona, mira al voltant (el motor salta la que no hi és)
        'idleActions': [{'animation': 'Blink', 'every': [3, 8]}, {'animation': 'Look', 'every': [9, 18], 'after': 6}],
    }
    if gran:
        extra['sizeVariants'] = {GRAN: G.K}
    return write(cid, tags, PERSONA_FEET, extra, gran=gran)


# ─── Criatures ──────────────────────────────────────────────────────────────

def criatura(cid, draw, feet, idle, talk, idle_ms, talk_ms, verb, davant, walk_speed=60, camina=False,
             walk_ms=(110, 120)):
    """`draw(facing, talk=, closed=, k=)` → imatge. `idle`: els k de l'Idle; `talk`: [(talk, k)] de la Talk.
    `camina`: també WalkL/D/U, de sis fotogrames (`draw(facing, walk=0..5)`)."""
    tags = []
    for f in 'LDU':
        tags.append((f'Idle{f}', [draw(f, k=k) for k in idle]))
    if camina:
        for f in 'LDU':
            tags.append((f'Walk{f}', [draw(f, walk=w) for w in range(6)]))
    for f in 'LDU':
        tags.append((f'Talk{f}', [draw(f, talk=t and f != 'U', k=k) for t, k in talk]))
    for f in 'DL':
        tags.append((f'Blink{f}', [draw(f, closed=True, k=idle[0])] * 2))
    return write(cid, tags, feet, {
        'walkSpeed': walk_speed, 'davant': davant, 'defaultVerb': verb,
        'animations': durations(tags, walk=walk_ms, talk=talk_ms, idle=idle_ms),
        'idleActions': [{'animation': 'Blink', 'every': [3, 7]}],
    })


def espora_draw(f, talk=False, closed=False, k=0, walk=None):
    img = A.espora(f, talk=talk, closed=closed, walk=walk)
    if walk is None:
        return A.espora_respira(img, RESPIRA[k])
    if walk % 3 == 0:                                   # quan les cames es creuen, puja un píxel: va fent tentines
        out = Image.new('RGBA', img.size, CLEAR)
        out.paste(img.crop((0, 1, img.width, img.height)), (0, 0))
        return out
    return img


def fada_draw(qui):
    return lambda f, talk=False, closed=False, k=0: A.fada(qui, f, talk=talk, closed=closed, k=k)


def gripau_draw(qui):
    return lambda f, talk=False, closed=False, k=0: A.gripau(qui, f, talk=talk, closed=closed, k=k)


# ─── Tot el repartiment ─────────────────────────────────────────────────────

def repartiment():
    """{id: funció que escriu el full}."""
    return {
        'iri': lambda: persona('iri', A.IRI, 108, 'look'),
        'vet': lambda: persona('vet', A.VET, 104, 'look', walk=(80, 90)),
        'avia': lambda: persona('avia', A.AVIA, 70, 'talkTo', walk=(110, 120)),
        'pla': lambda: persona('pla', A.PLA, 116, 'talkTo'),
        'txell': lambda: persona('txell', A.TXELL, 116, 'talkTo'),
        'espora': lambda: criatura('espora', espora_draw, A.ESPORA_FEET, (0, 1, 2, 3), [(False, 0), (True, 0)],
                                   IDLE_MS, 150, 'talkTo', 20, walk_speed=48, camina=True),
        'urtica': lambda: criatura('urtica', fada_draw('urtica'), A.FADA_FEET, (0, 1, 2, 3),
                                   [(True, 0), (False, 1), (True, 2), (False, 3)], 110, 110, 'talkTo', 22),
        'pica': lambda: criatura('pica', fada_draw('pica'), A.FADA_FEET, (1, 2, 3, 0),
                                 [(True, 0), (False, 1), (True, 2), (False, 3)], 120, 110, 'look', 22),
        'card': lambda: criatura('card', fada_draw('card'), A.FADA_FEET, (2, 3, 0, 1),
                                 [(True, 0), (False, 1), (True, 2), (False, 3)], 115, 110, 'look', 22),
        'bufo': lambda: criatura('bufo', gripau_draw('bufo'), A.GRIPAU_FEET, (0, 1, 2, 1), [(False, 0), (True, 0)],
                                 420, 180, 'talkTo', 26),
        'gripau': lambda: criatura('gripau', gripau_draw('gripau'), A.GRIPAU_FEET, (0, 1, 2, 1),
                                   [(False, 0), (True, 0)], 380, 170, 'talkTo', 26),
    }


def main(argv):
    inst = '--installa' in argv
    argv = [a for a in argv if a != '--installa']
    tots = repartiment()
    ids = argv or list(tots)
    for cid in ids:
        tots[cid]()
        if inst:
            installa(cid)


if __name__ == '__main__':
    main(sys.argv[1:])
