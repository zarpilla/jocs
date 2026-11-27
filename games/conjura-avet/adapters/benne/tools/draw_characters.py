#!/usr/bin/env python3
"""
Els fulls dels personatges de La Conjura de l'Avet, amb el format que espera Benne (full d'Aseprite PNG + JSON amb
etiquetes, i el .character.json). El dibuix és a hd/conjura.py (amb el sistema de les adultes d'Aigua Verne,
hd/characters.py, i les proporcions de hd/arrel.py); aquí només es munten els fulls.

Una sola mida, a 1× (com les sales en 3D): cada personatge es dibuixa a la seva alçada i no s'escala. L'Iri fa
≈84 px, la Vet ≈78 i els adults, 80-90.

Animacions (L, D, U i el 3/4, DL i UL; Benne fa el mirall per a R, DR i UR):
  - **l'Iri i la Vet**: IdleL/D/U/DL/UL (4: respira), WalkL/D/U/DL/UL (6), TalkL/D/U/DL/UL (2), BlinkD/L/DL i
    LookD/DL (les micro-accions de quan són quietes; `idleActions`). I tot això també amb la roba `Monjo` (el
    prefix davant: MonjoIdleD, MonjoWalkL...), que el joc tria amb `outfit` (game/data/characters.json).
  - **els secundaris**: el mateix sense Walk; els que caminen en alguna escena (`CAMINEN`: en Bonfill, en Ramon i els
    canonges), també amb Walk. En Sunifred, a més, `BeuD`, `BadallaD` i `DormD` (beu, badalla i s'adorm a la taula
    de la cuina; `ALTRES`).
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
import sys
from pathlib import Path

from PIL import Image

sys.path.insert(0, str(Path(__file__).resolve().parent))
from hd import arrel as A  # noqa: E402
from hd import conjura as K  # noqa: E402

OUT = Path(__file__).resolve().parent.parent / 'placeholder-art'
GAME = Path(__file__).resolve().parents[3] / 'conjura-avet/src/game'
CLEAR = (0, 0, 0, 0)
SPRITE_FIELDS = ['walkSpeed', 'walkToPoint', 'talkPoint', 'feet', 'collider', 'animations', 'clickable', 'display',
                 'artScale', 'idleActions', 'sizeVariants']   # (com el sync; sizeVariants, per esborrar-lo si hi era)

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
        elif 'Fa' in t and 'Fa' == t[t.index('Fa'):t.index('Fa') + 2] and t.endswith(('L', 'D', 'U')) and 'Walk' not in t:
            a = {'loop': False, 'frameDuration': 90}       # el gest: un sol cop i s'hi queda (l'últim fotograma)
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


def write(cid, tags, feet, extra):
    """tags: [(nom, [imatges])]. Escriu <id>.png, <id>.json (Aseprite) i <id>.character.json a placeholder-art."""
    tags, feet = retalla(tags, feet)
    w, h = tags[0][1][0].size
    frames = [img for _, imgs in tags for img in imgs]
    # en files (una textura no pot fer més de 4096 d'ample)
    rows = -(-len(frames) // (4096 // w))
    cols = -(-len(frames) // rows)
    places = [(img, (i % cols) * w, (i // cols) * h) for i, img in enumerate(frames)]
    sheet = Image.new('RGBA', (cols * w, rows * h), CLEAR)
    for img, x, yy in places:
        sheet.paste(img, (x, yy))
    d = OUT / cid
    d.mkdir(parents=True, exist_ok=True)
    sheet.save(d / f'{cid}.png')
    frame_tags, i = [], 0
    for name, imgs in tags:
        frame_tags.append({'name': name, 'from': i, 'to': i + len(imgs) - 1, 'direction': 'forward', 'color': '#000000ff'})
        i += len(imgs)
    meta = {
        'frames': {f'{cid} {n}.aseprite': {
            'frame': {'x': x, 'y': yy, 'w': w, 'h': h}, 'rotated': False, 'trimmed': False,
            'spriteSourceSize': {'x': 0, 'y': 0, 'w': w, 'h': h}, 'sourceSize': {'w': w, 'h': h}, 'duration': 100,
        } for n, (img, x, yy) in enumerate(places)},
        'meta': {'app': 'https://www.aseprite.org/', 'version': 'draw_characters.py', 'image': f'{cid}.png',
                 'format': 'RGBA8888', 'size': {'w': sheet.width, 'h': sheet.height}, 'scale': '1',
                 'frameTags': frame_tags, 'layers': [], 'slices': []},
    }
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
    print(f'✔ {cid}: {len(frames)} fotogrames ({w}×{h}), {len(tags)} etiquetes, peus a {feet}')
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

# Els secundaris que caminen en alguna escena (`walk` d'un `stage`): també porten Walk.
CAMINEN = {'bonfill', 'ramon', 'gombau', 'arnulf', 'ermessenda'}

# Animacions soltes d'algun personatge (etiqueta: dibuix de cada fotograma, nombre de fotogrames, l'animació de
# Benne): en Sunifred a la cuina, `BeuD` (beu de la copa: un sol cop, i s'hi queda), `BadallaD` (badalla) i `DormD`
# (adormit a la taula: 4 fotogrames lents, el cos puja i baixa i ronca); hd/conjura.sunifred_*.
DORM_MS = 700
ALTRES = {'sunifred': {
    'BeuD': (K.sunifred_beu, K.BEU, {'loop': False, 'frameDuration': 420}),
    'BadallaD': (K.sunifred_badalla, 2, {'loop': False, 'frameDuration': 600}),
    'DormD': (K.sunifred_dorm, len(K.DORM), {'loop': True, 'frameDuration': DORM_MS}),
}}


def person_tags(spec, dirs=DIRS, prefix='', camina=True):
    """Les etiquetes d'una persona (amb el `prefix` de la roba davant)."""
    out = []
    for f in dirs:
        base = K.figura(spec, f)
        out.append((f'Idle{f}', [K.respira(base, spec, k) for k in RESPIRA]))
    if camina:
        for f in dirs:
            out.append((f'Walk{f}', [K.figura(spec, f, walk=k) for k in range(6)]))
    for f in dirs:
        out.append((f'Talk{f}', [K.figura(spec, f), K.figura(spec, f, talk=True)]))
    # micro-accions de quan és quiet (idleActions del motor): parpellejar i mirar al voltant (on es veu la cara)
    for f in dirs:
        if f in ('D', 'L', 'DL'):
            out.append((f'Blink{f}', [K.figura({**spec, 'closed': True}, f)] * 2))
    for f in dirs:
        if f in ('D', 'DL'):
            out.append((f'Look{f}', [K.figura({**spec, 'mira': m}, f) for m in (-1, -1, -1, 0, 1, 1, 1, 0)]))
    return [(prefix + n, imgs) for n, imgs in out]


# El gest `Fa` (de perfil): el braç del davant s'estira endavant i una mica avall (fer anar el salabre, donar, agafar)
# i s'hi queda fins que la indicació d'escena el treu (`"gest": null`) o s'acaben les línies.
GEST_FA = (0.35, 0.7, 1.0, 1.0)
AMB_GEST = ('iri', 'vet')


def _estira(k, abans=None):
    """La postura del gest: el braç del davant (k de 0 a 1), gairebé horitzontal, amb el colze poc doblegat."""
    import math

    def pose(p):
        if abans:
            abans(p)
        if p.f != 'L' or not p.arms:
            return
        a = 3 + (70 - 3) * k
        bend = 8 + (4 - 8) * k
        ra, rb = math.radians(a), math.radians(a + bend)
        sx, sy = p.arms[0][0]
        el = (sx - math.sin(ra) * 10.5, sy + math.cos(ra) * 10.5)
        wr = (el[0] - math.sin(rb) * 9.5, el[1] + math.cos(rb) * 9.5)
        p.arms[0] = ((sx, sy), el, wr)
    return pose


def persona(cid, walk_speed, verb, walk=(90, 100), camina=True):
    """Totes les robes de `cid` (hd/conjura.PERSONES) al mateix full, cadascuna amb el seu prefix."""
    tags = []
    for prefix, spec in K.PERSONES[cid].items():
        tags += person_tags(spec, prefix=prefix, camina=camina)
        if cid in AMB_GEST:
            tags.append((f'{prefix}FaL', [K.figura({**spec, 'pose': _estira(k, spec.get('pose'))}, 'L') for k in GEST_FA]))
    tags += [(n, [fn(k) for k in range(nf)]) for n, (fn, nf, _) in ALTRES.get(cid, {}).items()]
    anims = durations(tags, walk=walk)
    for n, (_, _, anim) in ALTRES.get(cid, {}).items():
        anims[n] = dict(anim)
    extra = {
        'walkSpeed': walk_speed, 'animations': anims, 'defaultVerb': verb,
        # quan és quiet, de tant en tant parpelleja i, si fa estona, mira al voltant (el motor salta la que no hi és)
        'idleActions': [{'animation': 'Blink', 'every': [3, 8]}, {'animation': 'Look', 'every': [9, 18], 'after': 6}],
    }
    return write(cid, tags, PERSONA_FEET, extra)


# ─── Tot el repartiment ─────────────────────────────────────────────────────

def repartiment():
    """{id: funció que escriu el full}."""
    out = {
        'iri': lambda: persona('iri', 120, 'look'),
        'vet': lambda: persona('vet', 112, 'look', walk=(85, 95)),
    }
    for cid in K.PERSONES:
        if cid not in out:
            out[cid] = lambda cid=cid: persona(cid, 96, 'talkTo', walk=(100, 110), camina=cid in CAMINEN)
    return out


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
