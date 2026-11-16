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
        for f in 'LDU':
            tags.append((f'{o}Idle{f}', [d(f)]))
        for f in 'LDU':
            tags.append((f'{o}Walk{f}', [d(f, walk=k) for k in range(6)]))
        for f in 'LDU':
            tags.append((f'{o}Talk{f}', [d(f, talk=False), d(f, talk=True)]))
    anims = {t: {'loop': True} for t, _ in tags}
    for t in anims:
        if 'Walk' in t:
            anims[t]['frameDuration'] = 90 if t.endswith('L') else 100
        elif 'Talk' in t:
            anims[t]['frameDuration'] = 140
    w, h = tags[0][1][0].size
    fx, fy = feet
    write(cid, tags, (w, h), {
        'walkSpeed': 110, 'walkToPoint': {'x': fx + 18, 'y': fy}, 'talkPoint': {'x': fx, 'y': -2}, 'feet': {'x': fx, 'y': fy},
        'collider': {'points': [{'x': 15, 'y': 2}, {'x': 35, 'y': 2}, {'x': 37, 'y': 50}, {'x': 33, 'y': 85}, {'x': 16, 'y': 85}, {'x': 12, 'y': 50}]},
        'animations': anims, 'defaultVerb': 'look',
    })


def secundari(cid, draw=None, outfits=('',)):
    """Un secundari: Idle, Walk i Talk en D, L i U (amb les robes de `outfits`, com les protagonistes)."""
    draw = draw or (lambda f, walk=None, talk=False, roba='': personatges.npc(cid, f, walk=walk, talk=talk))
    tags = []
    for o in outfits:
        for f in 'DLU':
            tags.append((f'{o}Idle{f}', [draw(f, roba=o)]))
            tags.append((f'{o}Talk{f}', [draw(f, roba=o), draw(f, talk=True, roba=o)]))
            tags.append((f'{o}Walk{f}', [draw(f, walk=k, roba=o) for k in range(6)]))
    if cid in SEUEN:
        # Assegut (de perfil, amb la boca que es mou): `appearance` a characters.json.
        spec = personatges.NPCS.get(cid) or personatges.BASTIDA_ROBA['']
        seu = lambda talk=False: person_seated(spec, talk)
        tags.append(('Seu', [seu(), seu(), seu(), seu(True)]))
    anims = {t: {'loop': True, **({'frameDuration': 140} if 'Talk' in t else
                                  {'frameDuration': 90 if t.endswith('WalkL') else 80} if 'Walk' in t else
                                  {'frameDuration': 500} if t == 'Seu' else {})}
             for t, _ in tags}
    # Els que seuen (`Seu`) surten de perfil, mirant a l'esquerra: qui hi parla se'ls posa al davant,
    # a un metre i mig (≈73 px de disseny), i no pas a l'esquena.
    walk_x = 25 - 73 if cid in SEUEN else 44
    write(cid, tags, (49, 87), {
        'walkSpeed': 70, 'walkToPoint': {'x': walk_x, 'y': 83}, 'talkPoint': {'x': 25, 'y': -2}, 'feet': {'x': 25, 'y': 83},
        'collider': {'points': [{'x': 15, 'y': 2}, {'x': 35, 'y': 2}, {'x': 37, 'y': 50}, {'x': 33, 'y': 85}, {'x': 16, 'y': 85}, {'x': 12, 'y': 50}]},
        'animations': anims, 'defaultVerb': 'talkTo',
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
