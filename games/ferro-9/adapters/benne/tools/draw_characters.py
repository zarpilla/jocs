#!/usr/bin/env python3
"""
Dibuixa els sprites provisionals dels personatges de Ferro-9, en pixel art, amb el format
que espera Benne (full d'Aseprite PNG + JSON amb etiquetes, i el .character.json):

  iri      enginyera del torn de nit (passat): bata blanca oberta, trena fosca, ulleres al front
  vet      presonera de la cel·la 9 (present): granota de presó taronja, bob platí
  cargol   robot de manteniment amb closca de cargol, ulls a les antenes, erugues
  capatas  el capatàs Tul, adormit a la cadira, amb el segell a les mans (i sense)
  mos      presoner vell i prim, maquillat: granota taronja descolorida
  mare     l'altaveu en forma de cor de la IA (normalment invisible)

  directora, sic, mira, guardia: secundaris de peu (Idle/Talk en D, L, U)

Les protagonistes tenen Idle/Walk/Talk en tres direccions (L, D, U; Benne fa el mirall per a R).
El dibuix és a hd/characters.py (pixel art a la mida real, amb volum i llum); aquí només es munten
els fulls. Els punts del .character.json continuen en coordenades de disseny (escalats amb escala.py).
Surt a adapters/benne/placeholder-art/<id>/. Ús: python3 draw_characters.py
"""
import json
import sys
from pathlib import Path

from PIL import Image

sys.path.insert(0, str(Path(__file__).resolve().parent))
from escala import SCALE, box, pt  # noqa: E402
from hd.characters import (IRI, VET, MOS, DIRECTORA, SIC, MIRA, GUARDIA,  # noqa: E402
                           person as hd_person, cargol, capatas, mare)

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
    sheet = Image.new('RGBA', (w * len(frames), h), CLEAR)
    for i, img in enumerate(frames):
        sheet.paste(img, (i * w, 0))
    d = OUT / cid
    d.mkdir(parents=True, exist_ok=True)
    sheet.save(d / f'{cid}.png')
    frame_tags, i = [], 0
    for name, imgs in tags:
        frame_tags.append({'name': name, 'from': i, 'to': i + len(imgs) - 1, 'direction': 'forward', 'color': '#000000ff'})
        i += len(imgs)
    meta = {
        'frames': {f'{cid} {n}.aseprite': {
            'frame': {'x': n * w, 'y': 0, 'w': w, 'h': h}, 'rotated': False, 'trimmed': False,
            'spriteSourceSize': {'x': 0, 'y': 0, 'w': w, 'h': h}, 'sourceSize': {'w': w, 'h': h}, 'duration': 100,
        } for n in range(len(frames))},
        'meta': {'app': 'https://www.aseprite.org/', 'version': 'provisional (draw_characters.py)', 'image': f'{cid}.png',
                 'format': 'RGBA8888', 'size': {'w': sheet.width, 'h': h}, 'scale': '1',
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


def main():
    walker('iri', IRI)
    walker('vet', VET)
    standing('mos', MOS, thin=True)
    standing('directora', DIRECTORA)
    standing('sic', SIC)
    standing('mira', MIRA)
    standing('guardia', GUARDIA)

    tags = []
    for f in 'DLU':
        tags.append((f'Idle{f}', [cargol(f), cargol(f), cargol(f), cargol(f, blink=True)]))
        tags.append((f'Talk{f}', [cargol(f, talk=False), cargol(f, talk=True)]))
    write('cargol', tags, (40, 46), {
        'walkSpeed': 50, 'walkToPoint': {'x': 46, 'y': 44}, 'talkPoint': {'x': 20, 'y': 0}, 'feet': {'x': 20, 'y': 44},
        'collider': {'points': [{'x': 6, 'y': 4}, {'x': 34, 'y': 4}, {'x': 34, 'y': 45}, {'x': 6, 'y': 45}]},
        'animations': {t: {'loop': True, 'frameDuration': 250 if t.startswith('Idle') else 140} for t, _ in tags},
        'defaultVerb': 'talkTo',
    })

    tags = []
    for f in 'DLU':
        tags.append((f'Idle{f}', [cargol(f, old=True), cargol(f, old=True), cargol(f, old=True), cargol(f, blink=True, old=True)]))
        tags.append((f'Talk{f}', [cargol(f, old=True, talk=False), cargol(f, old=True, talk=True)]))
    write('cargol_vell', tags, (40, 46), {
        'walkSpeed': 50, 'walkToPoint': {'x': 46, 'y': 44}, 'talkPoint': {'x': 20, 'y': 0}, 'feet': {'x': 20, 'y': 44},
        'collider': {'points': [{'x': 6, 'y': 4}, {'x': 34, 'y': 4}, {'x': 34, 'y': 45}, {'x': 6, 'y': 45}]},
        'animations': {t: {'loop': True, 'frameDuration': 250 if t.startswith('Idle') else 140} for t, _ in tags},
        'defaultVerb': 'talkTo',
    })

    snore = [capatas(0, zz=0), capatas(1, zz=1), capatas(1, zz=2), capatas(0, zz=3)]
    snore_empty = [capatas(0, False, zz=0), capatas(1, False, zz=1), capatas(1, False, zz=2), capatas(0, False, zz=3)]
    talk = [capatas(0, talk=True), capatas(0)]
    tags = [('IdleD', snore), ('TalkD', talk), ('IdleL', snore), ('TalkL', talk), ('IdleU', snore), ('TalkU', talk),
            ('DormSenseSegell', snore_empty)]
    write('capatas', tags, (48, 60), {
        'walkSpeed': 40, 'walkToPoint': {'x': 52, 'y': 58}, 'talkPoint': {'x': 24, 'y': 0}, 'feet': {'x': 24, 'y': 58},
        'collider': {'points': [{'x': 8, 'y': 4}, {'x': 38, 'y': 4}, {'x': 38, 'y': 59}, {'x': 8, 'y': 59}]},
        'animations': {t: {'loop': True, 'frameDuration': 600 if t != 'TalkD' and not t.startswith('Talk') else 160} for t, _ in tags},
        'defaultVerb': 'look',
    })

    tags = [(t, [mare(), mare(glow=True)]) for t in ('IdleD', 'TalkD', 'IdleL', 'TalkL', 'IdleU', 'TalkU')]
    write('mare', tags, (16, 16), {
        'walkSpeed': 1, 'walkToPoint': {'x': 0, 'y': 30}, 'talkPoint': {'x': 8, 'y': -2}, 'feet': {'x': 8, 'y': 15},
        'clickable': False, 'collider': {'points': [{'x': 0, 'y': 0}, {'x': 15, 'y': 0}, {'x': 15, 'y': 15}, {'x': 0, 'y': 15}]},
        'animations': {t: {'loop': True, 'frameDuration': 300} for t, _ in tags}, 'defaultVerb': 'talkTo',
    })


if __name__ == '__main__':
    from escala import RESOLUCIO
    if RESOLUCIO == 640:
        # A 640×360 les figures les dibuixa hd640/draw_characters.py (×4/3), al mateix lloc.
        import runpy
        sys.argv = [sys.argv[0], str(OUT)]
        runpy.run_path(str(Path(__file__).resolve().parent / 'hd640' / 'draw_characters.py'), run_name='__main__')
    else:
        main()
