#!/usr/bin/env python3
"""
Dibuixa els sprites provisionals dels personatges, en pixel art, amb el format que espera Benne
(full d'Aseprite PNG + JSON amb etiquetes, i el .character.json).

Les protagonistes tenen Idle/Walk/Talk en tres direccions (L, D, U; Benne fa el mirall per a R).
El dibuix és a hd/characters.py; aquí només es munten els fulls.
Surt a adapters/benne/placeholder-art/<id>/. Ús: python3 draw_characters.py
"""
import json
import sys
from pathlib import Path

from PIL import Image

sys.path.insert(0, str(Path(__file__).resolve().parent))
from escala import SCALE, box, pt  # noqa: E402
from hd.characters import person as hd_person  # noqa: E402
from hd import personatges  # noqa: E402

OUT = Path(__file__).resolve().parent.parent / 'placeholder-art'
OUTLINE = (34, 24, 30, 255)
CLEAR = (0, 0, 0, 0)


def rgba(c):
    return c if len(c) == 4 else (*c, 255)


class Canvas:
    """(El fan servir draw_items.py.) Llenç amb coordenades de disseny (les de sempre, p. ex. 36×64) que es rasteritza a l'escala
    del joc: rectangles i el·lipses es tornen a rasteritzar a la mida real, i el contorn és d'un píxel real."""

    def __init__(self, w, h, k=SCALE):
        self.k = k
        self.w, self.h = round(w * k), round(h * k)
        self.img = Image.new('RGBA', (self.w, self.h), CLEAR)

    def rpx(self, x, y, c):
        """Un píxel real (per als detalls que només caben a la resolució gran)."""
        if 0 <= x < self.w and 0 <= y < self.h:
            self.img.putpixel((x, y), rgba(c))

    def rrect(self, x0, y0, x1, y1, c):
        for y in range(max(0, y0), min(self.h - 1, y1) + 1):
            for x in range(max(0, x0), min(self.w - 1, x1) + 1):
                self.img.putpixel((x, y), rgba(c))

    def px(self, x, y, c):
        self.rect(x, y, x, y, c)

    def rect(self, x0, y0, x1, y1, c):
        self.rrect(*box(x0, y0, x1, y1, self.k), c)

    def ellipse(self, cx, cy, rx, ry, c):
        k = self.k
        for y in range(max(0, int((cy - ry - 1) * k)), min(self.h, int((cy + ry + 2) * k))):
            for x in range(max(0, int((cx - rx - 1) * k)), min(self.w, int((cx + rx + 2) * k))):
                lx, ly = (x + 0.5) / k - 0.5, (y + 0.5) / k - 0.5
                if ((lx - cx) / (rx + 0.3)) ** 2 + ((ly - cy) / (ry + 0.3)) ** 2 <= 1:
                    self.img.putpixel((x, y), rgba(c))

    def outline(self):
        """Contorn fosc d'un píxel al voltant de tot el que s'ha dibuixat (llegibilitat sobre qualsevol fons)."""
        src = self.img.copy()
        for y in range(self.h):
            for x in range(self.w):
                if src.getpixel((x, y))[3] == 0:
                    for dx, dy in ((1, 0), (-1, 0), (0, 1), (0, -1)):
                        nx, ny = x + dx, y + dy
                        if 0 <= nx < self.w and 0 <= ny < self.h and src.getpixel((nx, ny))[3] > 0 and src.getpixel((nx, ny)) != rgba(OUTLINE):
                            self.img.putpixel((x, y), OUTLINE)
                            break


# ─── Persones ───────────────────────────────────────────────────────────────

def person(p, facing, walk=None, talk=False, thin=False):
    """Una persona de 49×87 (36×64 de disseny), peus a (25, 83)."""
    return hd_person(p, facing, walk=walk, talk=talk)


# ─── Fulls i definicions ────────────────────────────────────────────────────

def scaled_extra(extra):
    """Punts i velocitats del .character.json, de coordenades de disseny a píxels reals."""
    out = dict(extra)
    out['walkSpeed'] = round(extra['walkSpeed'] * SCALE)
    for key in ('walkToPoint', 'talkPoint', 'feet'):
        x, y = pt(extra[key]['x'], extra[key]['y'])
        out[key] = {'x': x, 'y': y}
    out['collider'] = {'points': [dict(zip('xy', pt(p['x'], p['y']))) for p in extra['collider']['points']]}
    return out


# ─── Quan són quiets: respiració i micro-accions (com a Aigua Verne) ────────

# La respiració (Idle de quatre fotogrames): no es mou cap píxel de la silueta; només la clariana del pit puja i baixa
# (+5 %, +10 %, +5 %). A 1×, moure el cos 1 px amunt o avall semblava que arronsessin les espatlles. Files de disseny
# (figura de 49×87): el pit, sota el coll.
RESPIRA_DE, RESPIRA_FINS = 30, 41
RESPIRA_X = (13, 36)
RESPIRA = (0.0, 0.05, 0.10, 0.05)
IDLE_MS = 650                                   # cada fotograma: un cicle de 2,6 s
# Les direccions dels fulls: L, D, U i el 3/4 (DL de cara, UL d'esquena); R, DR i UR són el mirall.
DIRS = ('L', 'D', 'U', 'DL', 'UL')
# Quan és quiet, de tant en tant parpelleja i, si fa estona, mira al voltant (el motor salta la que no hi és).
IDLE_ACTIONS = [{'animation': 'Blink', 'every': [3, 8]}, {'animation': 'Look', 'every': [9, 18], 'after': 6}]

_EXTRA = {}                                     # el que s'afegeix a l'especificació (ulls tancats, mirada)


def _amb(extra, fn):
    """Crida `fn()` amb `extra` afegit a l'especificació de qualsevol persona que es dibuixi."""
    _EXTRA.clear()
    _EXTRA.update(extra)
    try:
        return fn()
    finally:
        _EXTRA.clear()


def _person_amb_extra():
    """hd.characters.person, amb `_EXTRA` dins l'especificació (els dibuixos de hd640 la criden pel mòdul)."""
    import hd.characters as C
    if getattr(C.person, '_amb_extra', False):
        return
    orig = C.person

    def person(spec, *a, **kw):
        return orig({**spec, **_EXTRA} if _EXTRA else spec, *a, **kw)
    person._amb_extra = True
    C.person = person


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


def quiet_tags(d, pre='', dirs=DIRS, pit=True, walk=True):
    """Idle (4: respira), Walk (6), Talk (2), Blink i Look per a `d(f, walk=None, talk=False)`. `pit`: si la
    clariana del pit és on toca (no ho és en un fotograma més gran, com el d'en Ballester)."""
    _person_amb_extra()
    out = []
    for f in dirs:
        base = d(f)
        out.append((f'{pre}Idle{f}', [respira(base, k) if pit else base for k in RESPIRA]))
    if walk:
        for f in dirs:
            out.append((f'{pre}Walk{f}', [d(f, walk=k) for k in range(6)]))
    for f in dirs:
        out.append((f'{pre}Talk{f}', [d(f, talk=False), d(f, talk=True)]))
    for f in dirs:
        if f in ('D', 'L', 'DL'):                          # parpellejar: on es veu la cara
            out.append((f'{pre}Blink{f}', [_amb({'closed': True}, lambda f=f: d(f))] * 2))
    for f in dirs:
        if f in ('D', 'DL'):                               # mirar al voltant: els ulls i la cara, a un costat i a l'altre
            out.append((f'{pre}Look{f}', [_amb({'mira': m}, lambda f=f: d(f)) for m in (-1, -1, -1, 0, 1, 1, 1, 0)]))
    return out


def durations(tags, walk=(90, 100), talk=140, extra=None):
    anims = {}
    for t, _ in tags:
        a = {'loop': True}
        if 'Blink' in t or 'Look' in t:                    # micro-accions: un sol cop i torna a l'Idle
            a = {'loop': False, 'frameDuration': 75 if 'Blink' in t else 260}
        elif 'Walk' in t:
            a['frameDuration'] = walk[0] if t.endswith('L') else walk[1]
        elif 'Talk' in t:
            a['frameDuration'] = talk
        elif 'Idle' in t:
            a['frameDuration'] = IDLE_MS
        for k, v in (extra or {}).items():
            if t == k:
                a['frameDuration'] = v
        anims[t] = a
    return anims


def write(cid, tags, size, extra):
    """tags: [(nom, [imatges])]. Escriu <id>.png, <id>.json (Aseprite) i <id>.character.json."""
    frames = [img for _, imgs in tags for img in imgs]
    w, h = frames[0].size
    extra = scaled_extra(extra)
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
        'meta': {'app': 'https://www.aseprite.org/', 'version': 'provisional (draw_characters.py)', 'image': f'{cid}.png',
                 'format': 'RGBA8888', 'size': {'w': sheet.width, 'h': sheet.height}, 'scale': '1',
                 'frameTags': frame_tags, 'layers': [], 'slices': []},
    }
    (d / f'{cid}.json').write_text(json.dumps(meta, indent=2) + '\n')
    character = {
        'id': cid, 'name': cid, 'description': '', 'clickable': True, 'display': {'aseprite': True},
        **extra,
    }
    (d / f'{cid}.character.json').write_text(json.dumps(character, indent=2) + '\n')
    print(f'✔ {cid}: {len(frames)} fotogrames, {", ".join(t for t, _ in tags)}')


def walker(cid, p):
    tags = []
    for f in 'LDU':
        tags.append((f'Idle{f}', [person(p, f)]))
    for f in 'LDU':
        tags.append((f'Walk{f}', [person(p, f, walk=k) for k in range(6)]))
    for f in 'LDU':
        tags.append((f'Talk{f}', [person(p, f, talk=False), person(p, f, talk=True)]))
    anims = {t: {'loop': True} for t, _ in tags}
    for f in 'LDU':
        anims[f'Walk{f}']['frameDuration'] = 90 if f == 'L' else 80
        anims[f'Talk{f}']['frameDuration'] = 140
    write(cid, tags, (36, 64), {
        'walkSpeed': 84, 'walkToPoint': {'x': 40, 'y': 61}, 'talkPoint': {'x': 18, 'y': -2}, 'feet': {'x': 18, 'y': 61},
        'collider': {'points': [{'x': 11, 'y': 2}, {'x': 25, 'y': 2}, {'x': 27, 'y': 40}, {'x': 24, 'y': 63}, {'x': 11, 'y': 63}, {'x': 8, 'y': 40}]},
        'animations': anims, 'defaultVerb': 'look',
    })


def standing(cid, p, thin=False):
    tags = []
    for f in 'DLU':
        tags.append((f'Idle{f}', [person(p, f, thin=thin)]))
        tags.append((f'Talk{f}', [person(p, f, thin=thin), person(p, f, talk=True, thin=thin)]))
    anims = {t: {'loop': True, **({'frameDuration': 140} if t.startswith('Talk') else {})} for t, _ in tags}
    write(cid, tags, (36, 64), {
        'walkSpeed': 60, 'walkToPoint': {'x': 44, 'y': 61}, 'talkPoint': {'x': 18, 'y': -2}, 'feet': {'x': 18, 'y': 61},
        'collider': {'points': [{'x': 11, 'y': 2}, {'x': 25, 'y': 2}, {'x': 27, 'y': 40}, {'x': 24, 'y': 63}, {'x': 11, 'y': 63}, {'x': 8, 'y': 40}]},
        'animations': anims, 'defaultVerb': 'talkTo',
    })


def protagonist(cid, draw, feet=(25, 83), outfits=('',)):
    """Protagonista (hd/personatges.py): 49×87, peus a (25, 83), com a Ferro-9.
    `outfits`: les robes (prefix de les etiquetes: `BarIdleD`...); `draw(f, walk, talk, roba)` les dibuixa."""
    tags = []
    for o in outfits:
        d = (lambda f, walk=None, talk=False: draw(f, walk=walk, talk=talk)) if not o else \
            (lambda f, walk=None, talk=False, o=o: draw(f, walk=walk, talk=talk, roba=o))
        tags += quiet_tags(d, o)
    anims = durations(tags, walk=(90, 100))
    w, h = tags[0][1][0].size
    fx, fy = feet
    write(cid, tags, (w, h), {
        'walkSpeed': 110, 'walkToPoint': {'x': fx + 18, 'y': fy}, 'talkPoint': {'x': fx, 'y': -2}, 'feet': {'x': fx, 'y': fy},
        'collider': {'points': [{'x': 15, 'y': 2}, {'x': 35, 'y': 2}, {'x': 37, 'y': 50}, {'x': 33, 'y': 85}, {'x': 16, 'y': 85}, {'x': 12, 'y': 50}]},
        'animations': anims, 'defaultVerb': 'look', 'idleActions': IDLE_ACTIONS,
    })


def secundari(cid, draw=None, outfits=('',)):
    """Un secundari: Idle, Walk i Talk en D, L i U (amb les robes de `outfits`, com les protagonistes)."""
    draw = draw or (lambda f, walk=None, talk=False, roba='': personatges.npc(cid, f, walk=walk, talk=talk))
    tags = []
    for o in outfits:
        tags += quiet_tags(lambda f, walk=None, talk=False, o=o: draw(f, walk=walk, talk=talk, roba=o), o)
    if cid in SEUEN:
        # Assegut (de perfil, amb la boca que es mou): `appearance` a characters.json.
        spec = personatges.NPCS.get(cid) or personatges.BASTIDA_ROBA['']
        seu = lambda talk=False: person_seated(spec, talk)
        tags.append(('Seu', [seu(), seu(), seu(), seu(True)]))
    anims = durations(tags, walk=(90, 80), extra={'Seu': 500})
    # Els que seuen (`Seu`) surten de perfil, mirant a l'esquerra: qui hi parla se'ls posa al davant,
    # a un metre i mig (≈73 px de disseny), i no pas a l'esquena. En Bastida no: a la coberta de popa és dret a la
    # vora, i el punt de l'esquerra queda darrere el bidó (tasca 090); el de per defecte el motor el posa a parlar.
    walk_x = 25 - 73 if cid in SEUEN and cid != 'bastida' else 44
    write(cid, tags, (49, 87), {
        'walkSpeed': 70, 'walkToPoint': {'x': walk_x, 'y': 83}, 'talkPoint': {'x': 25, 'y': -2}, 'feet': {'x': 25, 'y': 83},
        'collider': {'points': [{'x': 15, 'y': 2}, {'x': 35, 'y': 2}, {'x': 37, 'y': 50}, {'x': 33, 'y': 85}, {'x': 16, 'y': 85}, {'x': 12, 'y': 50}]},
        'animations': anims, 'defaultVerb': 'talkTo', 'idleActions': IDLE_ACTIONS,
    })


SEUEN = ('marcel', 'juana', 'bastida')


def person_seated(spec, talk=False):
    from hd.characters import person as hp
    return hp(dict(spec, seated=49), 'L', talk=talk)


def gat(cid='diu'):
    """En Diu: assegut, sempre de cara (un gat no es gira per ningú); quan camina, de perfil."""
    idle = [personatges.diu(cua=k % 4, parpelleja=(k == 7)) for k in range(8)]
    talk = [personatges.diu(cua=0), personatges.diu(cua=1)]
    walk = [personatges.diu_camina(k) for k in range(6)]
    tags = []
    for f in 'DLU':
        tags.append((f'Idle{f}', idle))
        tags.append((f'Talk{f}', talk))
        tags.append((f'Walk{f}', walk))
    anims = {t: {'loop': True, 'frameDuration': 90 if t.startswith('Walk') else 300 if t.startswith('Idle') else 160}
             for t, _ in tags}
    write(cid, tags, (personatges.GW, personatges.GH), {
        'walkSpeed': 120, 'walkToPoint': {'x': 36, 'y': 25}, 'talkPoint': {'x': 13, 'y': -2}, 'feet': {'x': 13, 'y': 25},
        'collider': {'points': [{'x': 4, 'y': 0}, {'x': 28, 'y': 0}, {'x': 28, 'y': 25}, {'x': 4, 'y': 25}]},
        'animations': anims, 'defaultVerb': 'look',
    })


def main():
    """Els personatges de Ni un ou (hd/personatges.py)."""
    protagonist('iri', personatges.iri)
    protagonist('vet', personatges.vet, outfits=tuple(personatges.VET_ROBA))
    secundari('bastida', personatges.bastida, outfits=tuple(personatges.BASTIDA_ROBA))
    for cid in personatges.NPCS:
        secundari(cid)
    gat('diu')


if __name__ == '__main__':
    from escala import RESOLUCIO
    if RESOLUCIO == 640:
        # A 640×360 les figures les dibuixa hd640/draw_characters.py (×4/3), al mateix lloc.
        import runpy
        sys.argv = [sys.argv[0], str(OUT)]
        runpy.run_path(str(Path(__file__).resolve().parent / 'hd640' / 'draw_characters.py'), run_name='__main__')
    else:
        main()
