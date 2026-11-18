#!/usr/bin/env python3
"""
Dibuixa els sprites dels personatges d'Aigua Verne, amb el format que espera Benne (full d'Aseprite PNG + JSON amb
etiquetes, i el .character.json). El dibuix és a hd/personatges.py; aquí només es munten els fulls.

Dues mides a cada full (guió, «Art: dues mides de càmera»):
  - **de prop** (etiquetes sense prefix: IdleD, WalkL, TalkU...): la figura redibuixada a ×1,2 (≈100 px);
  - **de lluny** (prefix `Lluny`: LlunyIdleD, LlunyWalkL...): la figura a la mida de disseny (≈83 px), enganxada
    dins el mateix fotograma amb els peus al mateix punt (Benne té un sol punt de peus per personatge).
Les robes porten el seu prefix davant: `Gala` / `LlunyGala`, `Brut` / `LlunyBrut`, `Moll` / `LlunyMoll`.

Els fulls són a ART_SCALE = 1, com les sales en 3D (fins al 18-11-2026, a 2×: `artScale: 2` i hd/personatges.FigK2 i
FigL2, que encara hi són). Els punts són a la mida de prop, 59×104.

Tres direccions (L, D, U; Benne fa el mirall per a R), i el 3/4 (DL i UL; DR i UR, el mirall) als personatges que el
porten (`dirs` de `persona`; ara, l'Iri). Una persona: fotograma de 59×104, peus a (30, 100).

Surt a adapters/benne/placeholder-art/<id>/. Ús (des d'aquesta carpeta):
    python3 draw_characters.py [--fitxa fitxa.png] [id ...]
"""
import json
import math
import sys
from pathlib import Path

from PIL import Image

sys.path.insert(0, str(Path(__file__).resolve().parent))
from pixels import nearest  # noqa: E402
from hd import personatges as P  # noqa: E402
from hd.characters import person  # noqa: E402

OUT = Path(__file__).resolve().parent.parent / 'placeholder-art'
ART_SCALE = 1                  # a 1× (com les sales en 3D): els fulls fan la quarta part
P.ART_SCALE = ART_SCALE
CLEAR = (0, 0, 0, 0)
DIRS = 'LDU'


def rnd(v):
    return math.floor(v + 0.5)


def frame_of(w, h, feet):
    """Fotograma gran (×K) i on cauen els peus, a partir del de disseny (w×h, peus `feet`)."""
    W, H = round(w * P.K), round(h * P.K)
    fx, fy = rnd(P.f(feet[0])), rnd(P.f(feet[1]))
    return W, H, (fx, fy), (fx - feet[0], fy - feet[1])


class Mides:
    """Dibuixa un fotograma a les dues mides: `prop(fn)` a ×K, `lluny(fn)` a ×1 enganxat al fotograma gran."""

    def __init__(self, w, h, feet):
        self.W, self.H, self.feet, self.off = frame_of(w, h, feet)

    def prop(self, fn):
        with P.de_prop():
            img = fn()
        assert img.size == (self.W * ART_SCALE, self.H * ART_SCALE), (img.size, self.W, self.H)
        return img

    def lluny(self, fn):
        with P.de_lluny():
            img = fn()
        out = Image.new('RGBA', (self.W * ART_SCALE, self.H * ART_SCALE), CLEAR)
        out.alpha_composite(img, (self.off[0] * ART_SCALE, self.off[1] * ART_SCALE))
        return out

    def pt(self, x, y):
        """Un punt de disseny → del fotograma gran."""
        return {'x': rnd(P.f(x)), 'y': rnd(P.f(y))}


PERSONA = Mides(49, 87, (25, 83))
GAT = Mides(P.GW, P.GH, (13, 25))
GOS = Mides(P.DW, P.DH, (17, 25))


def tags_both(m, make, prefix=''):
    """`make(dibuixa)` torna [(etiqueta, [fn])]; se'n fan les dues mides, primer la de prop i després la de lluny."""
    out = []
    for size, lab in ((m.prop, ''), (m.lluny, 'Lluny')):
        for name, fns in make():
            out.append((f'{lab}{prefix}{name}', [size(fn) for fn in fns]))
    return out


def durations(tags, walk=(90, 90), talk=140, idle=None, extra=None):
    anims = {}
    for t, _ in tags:
        a = {'loop': True}
        base = t.replace('Lluny', '', 1) if t.startswith('Lluny') else t
        if 'Blink' in base or 'Look' in base:           # micro-accions: un sol cop i torna a l'Idle
            a = {'loop': False, 'frameDuration': 75 if 'Blink' in base else 260}
        elif 'Walk' in base:
            a['frameDuration'] = walk[0] if base.endswith('L') else walk[1]
        elif 'Talk' in base:
            a['frameDuration'] = talk
        elif 'Idle' in base and idle:
            a['frameDuration'] = idle
        for k, v in (extra or {}).items():
            if base.endswith(k):
                a['frameDuration'] = v
        anims[t] = a
    return anims


def write(cid, tags, extra):
    """tags: [(nom, [imatges])]. Escriu <id>.png, <id>.json (Aseprite) i <id>.character.json."""
    frames = [img for _, imgs in tags for img in imgs]
    w, h = frames[0].size
    assert all(im.size == (w, h) for im in frames), cid
    # en graella: una sola fila de molts fotogrames passaria de l'amplada màxima d'una textura (4096)
    cols = min(len(frames), 4096 // w)
    rows = -(-len(frames) // cols)
    sheet = Image.new('RGBA', (w * cols, h * rows), CLEAR)
    for i, img in enumerate(frames):
        sheet.paste(img, ((i % cols) * w, (i // cols) * h))
    d = OUT / cid
    d.mkdir(parents=True, exist_ok=True)
    sheet.save(d / f'{cid}.png')
    frame_tags, i = [], 0
    for name, imgs in tags:
        frame_tags.append({'name': name, 'from': i, 'to': i + len(imgs) - 1, 'direction': 'forward', 'color': '#000000ff'})
        i += len(imgs)
    meta = {
        'frames': {f'{cid} {n}.aseprite': {
            'frame': {'x': (n % cols) * w, 'y': (n // cols) * h, 'w': w, 'h': h}, 'rotated': False, 'trimmed': False,
            'spriteSourceSize': {'x': 0, 'y': 0, 'w': w, 'h': h}, 'sourceSize': {'w': w, 'h': h}, 'duration': 100,
        } for n in range(len(frames))},
        'meta': {'app': 'https://www.aseprite.org/', 'version': 'draw_characters.py', 'image': f'{cid}.png',
                 'format': 'RGBA8888', 'size': {'w': sheet.width, 'h': sheet.height}, 'scale': '1',
                 'frameTags': frame_tags, 'layers': [], 'slices': []},
    }
    (d / f'{cid}.json').write_text(json.dumps(meta, indent=2) + '\n')
    character = {
        'id': cid, 'name': cid, 'description': '', 'clickable': True, 'display': {'aseprite': True},
        **extra, **({'artScale': ART_SCALE} if ART_SCALE != 1 else {}),
    }
    (d / f'{cid}.character.json').write_text(json.dumps(character, indent=2) + '\n')
    print(f'✔ {cid}: {len(frames)} fotogrames ({w}×{h}), {len(tags)} etiquetes')
    return tags


# ─── Persones ───────────────────────────────────────────────────────────────

# La respiració (Idle de quatre fotogrames): no es mou cap píxel de la silueta; només la clariana del pit puja i baixa
# (+5 %, +10 %, +5 %). A 1×, moure el cos 1 px amunt o avall era massa: semblava que arronsessin les espatlles o que
# fessin reverències. Files de disseny (figura de 49×87): el pit, sota el coll.
RESPIRA_DE, RESPIRA_FINS = 30, 41
RESPIRA_X = (13, 36)
RESPIRA = (0.0, 0.05, 0.10, 0.05)
IDLE_MS = 650                                   # cada fotograma: un cicle de 2,6 s (en repòs, sense pressa)


def respira(img, k):
    """`img` (la persona sola, 49×87 de disseny a `sc` px per px) amb el pit un `k` més clar, més a dalt que a baix."""
    if not k:
        return img
    sc = img.width / 49
    y0, y1 = round(RESPIRA_DE * sc), round(RESPIRA_FINS * sc)
    out = img.copy()
    P_ = out.load()
    for y in range(y0, y1):
        f = 1 + k * (1 - (y - y0) / (y1 - y0))
        for x in range(round(RESPIRA_X[0] * sc), round(RESPIRA_X[1] * sc)):
            r, g, b, a = P_[x, y]
            if a:
                P_[x, y] = (min(255, int(r * f)), min(255, int(g * f)), min(255, int(b * f)), a)
    return out


def person_tags(spec_of, dirs=DIRS):
    """Idle (4: respira), Walk (6) i Talk (2) en L, D i U (i DL i UL, el 3/4, si `dirs` les porta). `spec_of()` torna
    l'especificació (es crida dins la mida)."""
    dirs = [dirs[i:i + 2] if dirs[i:i + 2] in ('DL', 'UL') else dirs[i] for i in range(len(dirs))] if isinstance(dirs, str) else dirs

    def make():
        out = []
        for f in dirs:
            out.append((f'Idle{f}', [lambda f=f, k=k: respira(person(spec_of(), f), k) for k in RESPIRA]))
        for f in dirs:
            out.append((f'Walk{f}', [lambda f=f, k=k: person(spec_of(), f, walk=k) for k in range(6)]))
        for f in dirs:
            out.append((f'Talk{f}', [lambda f=f: person(spec_of(), f), lambda f=f: person(spec_of(), f, talk=True)]))
        # micro-accions de quan és quiet (idleActions del motor): parpellejar i mirar al voltant (on es veu la cara)
        for f in dirs:
            if f in ('D', 'L', 'DL'):
                out.append((f'Blink{f}', [lambda f=f: person({**spec_of(), 'closed': True}, f)] * 2))
        for f in dirs:
            if f in ('D', 'DL'):
                costat = [lambda f=f, m=m: person({**spec_of(), 'mira': m}, f) for m in (-1, -1, -1, 0, 1, 1, 1, 0)]
                out.append((f'Look{f}', costat))
        return out
    return make


# Qui s'asseu (la Juana a casa seva) mira a l'esquerra: qui hi va a parlar s'atura davant seu, a 1,5 m (uns 90 px
# a les sales de prop), i no a l'esquena.
DAVANT_SEU = -90


def person_extra(walk_speed, verb, anims, seu=False):
    m = PERSONA
    fx, fy = m.feet
    poly = [(15, 2), (35, 2), (37, 50), (33, 85), (16, 85), (12, 50)]
    return {
        'walkSpeed': walk_speed, 'walkToPoint': {'x': fx + (DAVANT_SEU if seu else 22), 'y': fy},
        'talkPoint': {'x': fx, 'y': -2},
        'feet': {'x': fx, 'y': fy}, 'collider': {'points': [m.pt(x, y) for x, y in poly]},
        'animations': anims, 'defaultVerb': verb,
        # quan és quiet, de tant en tant parpelleja i, si fa estona, mira al voltant (el motor salta la que no hi és)
        'idleActions': [{'animation': 'Blink', 'every': [3, 8]}, {'animation': 'Look', 'every': [9, 18], 'after': 6}],
    }


def persona(cid, robes, walk_speed, verb, seu=None, walk=(90, 90), dirs=('L', 'D', 'U')):
    """`robes`: {prefix: spec}. `seu`: una funció (talk) → la figura asseguda (etiquetes Seu i LlunySeu). `dirs`: les
    direccions del full (amb 'DL' i 'UL', el 3/4; R, DR i UR són el mirall)."""
    tags = []
    for o, spec in robes.items():
        tags += tags_both(PERSONA, person_tags(lambda spec=spec: spec, list(dirs)), o)
    if seu:
        tags += tags_both(PERSONA, lambda: [('Seu', [seu, seu, seu, lambda: seu(True)])])
    anims = durations(tags, walk=walk, idle=IDLE_MS, extra={'Seu': 500})
    return write(cid, tags, person_extra(walk_speed, verb, anims, seu=bool(seu)))


# ─── En Diu, en Dividend i en Fidel ──────────────────────────────────────────

def gat():
    """En Diu: assegut, sempre de cara (un gat no es gira per ningú); quan camina, de perfil."""
    def make():
        idle = [lambda k=k: P.diu(cua=k % 4, parpelleja=(k == 7)) for k in range(8)]
        talk = [lambda: P.diu(cua=0), lambda: P.diu(cua=1)]
        walk = [lambda k=k: P.diu_camina(k) for k in range(6)]
        out = []
        for f in DIRS:
            out += [(f'Idle{f}', idle), (f'Talk{f}', talk), (f'Walk{f}', walk)]
        return out
    tags = tags_both(GAT, make)
    anims = durations(tags, walk=(90, 90), talk=160, idle=300)
    fx, fy = GAT.feet
    return write('diu', tags, {
        'walkSpeed': 144, 'walkToPoint': {'x': fx + 28, 'y': fy}, 'talkPoint': {'x': fx, 'y': -2}, 'feet': {'x': fx, 'y': fy},
        'collider': {'points': [GAT.pt(x, y) for x, y in ((4, 0), (28, 0), (28, 25), (4, 25))]},
        'animations': anims, 'defaultVerb': 'look',
    })


def gos():
    """En Dividend: Idle, Walk i Talk (borda) en L, D i U; i la roba `Moll` (xop)."""
    tags = []
    for o, moll in (('', False), ('Moll', True)):
        def make(moll=moll):
            out = []
            for f in DIRS:
                out.append((f'Idle{f}', [lambda f=f: P.dividend(f, moll=moll)]))
            for f in DIRS:
                out.append((f'Walk{f}', [lambda f=f, k=k: P.dividend(f, walk=k, moll=moll) for k in range(6)]))
            for f in DIRS:
                out.append((f'Talk{f}', [lambda f=f: P.dividend(f, moll=moll), lambda f=f: P.dividend(f, talk=True, moll=moll)]))
            return out
        tags += tags_both(GOS, make, o)
    anims = durations(tags, walk=(80, 90), talk=180)
    fx, fy = GOS.feet
    return write('dividend', tags, {
        'walkSpeed': 120, 'walkToPoint': {'x': fx + 26, 'y': fy}, 'talkPoint': {'x': fx, 'y': -2}, 'feet': {'x': fx, 'y': fy},
        'collider': {'points': [GOS.pt(x, y) for x, y in ((3, 1), (31, 1), (31, 25), (3, 25))]},
        'animations': anims, 'defaultVerb': 'look',
    })


def robot():
    """En Fidel: Idle, Walk (llisca) i Talk en L, D i U."""
    def make():
        out = []
        for f in DIRS:
            out.append((f'Idle{f}', [lambda f=f: P.fidel(f)]))
        for f in DIRS:
            out.append((f'Walk{f}', [lambda f=f, k=k: P.fidel(f, walk=k) for k in range(6)]))
        for f in DIRS:
            out.append((f'Talk{f}', [lambda f=f: P.fidel(f), lambda f=f: P.fidel(f, talk=True)]))
        return out
    tags = tags_both(PERSONA, make)
    anims = durations(tags, walk=(110, 110), talk=180)
    return write('fidel', tags, person_extra(84, 'talkTo', anims))


# ─── Tot el repartiment ─────────────────────────────────────────────────────

def repartiment():
    """{id: funció que escriu el full}."""
    out = {
        'iri': lambda: persona('iri', P.IRI_ROBA, 132, 'look', walk=(90, 100), dirs=('L', 'D', 'U', 'DL', 'UL')),
        'vet': lambda: persona('vet', {'': P.VET}, 132, 'look', walk=(90, 100), dirs=('L', 'D', 'U', 'DL', 'UL')),
        'diu': gat,
    }
    for cid in P.NPCS:
        robes = {'': P.NPCS[cid], **{k: v for k, v in P.ROBES.get(cid, {}).items() if k}}
        seu = (lambda talk=False, cid=cid: P.npc_seu(cid, talk)) if cid in P.SEUEN else None
        out[cid] = lambda cid=cid, robes=robes, seu=seu: persona(cid, robes, 84, 'talkTo', seu=seu, walk=(90, 80),
                                                                 dirs=('L', 'D', 'U', 'DL', 'UL'))
    out['dividend'] = gos
    out['fidel'] = robot
    return out


def fitxa(results, path, bg=(170, 160, 130, 255)):
    """Fitxa de comprovació: per a cada personatge (i roba), Idle D/L/U de prop i de lluny, ×2."""
    rows = []
    for cid, tags in results.items():
        t = dict(tags)
        prefixes = sorted({n[:-5] for n in t if n.endswith('IdleD') and not n.startswith('Lluny')}, key=len)
        for pre in prefixes:
            cells = [t[f'{pre}Idle{f}'][0] for f in 'DLU'] + [t[f'{pre}TalkD'][1]]
            cells += [t[f'Lluny{pre}Idle{f}'][0] for f in 'DLU'] + [t[f'Lluny{pre}TalkD'][1]]
            rows.append((f'{cid} {pre}', cells))
        if 'Seu' in t:
            rows.append((f'{cid} Seu', [t['Seu'][0], t['Seu'][3], t['LlunySeu'][0], t['LlunySeu'][3]]))
    cw, ch = 60 * ART_SCALE, 106 * ART_SCALE
    ncol = max(len(c) for _, c in rows)
    per = 2                                           # dues files de la fitxa per columna de la imatge
    half = -(-len(rows) // per)
    sheet = Image.new('RGBA', (cw * ncol * per + 8 * (per - 1), ch * half), bg)
    for r, (name, cells) in enumerate(rows):
        X0 = (r // half) * (cw * ncol + 8)
        y = (r % half) * ch
        for c, im in enumerate(cells):
            x = X0 + c * cw
            sheet.alpha_composite(im, (x + (cw - im.width) // 2, y + ch - im.height - 1))
    if ART_SCALE == 1:
        sheet = nearest(sheet, (sheet.width * 2, sheet.height * 2))
    sheet.save(path)
    print('✔ fitxa:', path)


def main(argv):
    path = None
    if '--fitxa' in argv:
        i = argv.index('--fitxa')
        path = argv[i + 1]
        argv = argv[:i] + argv[i + 2:]
    tots = repartiment()
    ids = argv or list(tots)
    results = {cid: tots[cid]() for cid in ids}
    if path:
        fitxa(results, path)


if __name__ == '__main__':
    main(sys.argv[1:])
