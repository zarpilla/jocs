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

  directora, sic, mira, guardia: secundaris de peu (Idle/Talk en D, L, U; la directora i en Sic, també Walk)

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
    """Una persona de 49×87 (36×64 de disseny), peus a (25, 83). (Amb `_EXTRA`: els ulls tancats o la mirada.)"""
    return hd_person({**p, **_EXTRA} if _EXTRA else p, facing, walk=walk, talk=talk)


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
        elif t.startswith('Fa'):                           # el gest: un sol cop i s'hi queda (l'últim fotograma)
            a = {'loop': False, 'frameDuration': 90}
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


# El gest `Fa` (de perfil): el braç del davant s'estira endavant (donar, agafar, fer anar una cosa) i s'hi queda fins
# que la indicació d'escena el treu (`"gest": null`) o s'acaben les línies.
GEST_FA = (0.35, 0.7, 1.0, 1.0)


def walker(cid, p):
    tags = quiet_tags(lambda f, walk=None, talk=False: person(p, f, walk=walk, talk=talk))
    for f in ('L', 'U'):
        tags.append((f'Fa{f}', [_amb({'estira': k}, lambda f=f: person(p, f)) for k in GEST_FA]))
    write(cid, tags, (36, 64), {
        'walkSpeed': 84, 'walkToPoint': {'x': 40, 'y': 61}, 'talkPoint': {'x': 18, 'y': -2}, 'feet': {'x': 18, 'y': 61},
        'collider': {'points': [{'x': 11, 'y': 2}, {'x': 25, 'y': 2}, {'x': 27, 'y': 40}, {'x': 24, 'y': 63}, {'x': 11, 'y': 63}, {'x': 8, 'y': 40}]},
        'animations': durations(tags, walk=(90, 80)), 'defaultVerb': 'look', 'idleActions': IDLE_ACTIONS,
    })


def standing(cid, p, thin=False, walks=False):
    """Un secundari de peu: Idle i Talk en D, L i U; amb `walks`, també Walk i el 3/4 (qui camina en un `stage`:
    sense Walk, Benne el faria lliscar)."""
    tags = quiet_tags(lambda f, walk=None, talk=False: person(p, f, walk=walk, talk=talk, thin=thin),
                      dirs=DIRS if walks else ('D', 'L', 'U'), walk=walks)
    write(cid, tags, (36, 64), {
        'walkSpeed': 60, 'walkToPoint': {'x': 44, 'y': 61}, 'talkPoint': {'x': 18, 'y': -2}, 'feet': {'x': 18, 'y': 61},
        'collider': {'points': [{'x': 11, 'y': 2}, {'x': 25, 'y': 2}, {'x': 27, 'y': 40}, {'x': 24, 'y': 63}, {'x': 11, 'y': 63}, {'x': 8, 'y': 40}]},
        'animations': durations(tags, walk=(90, 80)), 'defaultVerb': 'talkTo', 'idleActions': IDLE_ACTIONS,
    })


def main():
    walker('iri', IRI)
    walker('vet', VET)
    standing('mos', MOS, thin=True)
    standing('directora', DIRECTORA, walks=True)
    standing('sic', SIC, walks=True)
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
