#!/usr/bin/env python3
"""
Dibuixa els sprites provisionals dels personatges de Ferro-9, en pixel art, amb el format
que espera Benne (full d'Aseprite PNG + JSON amb etiquetes, i el .character.json):

  iri      enginyera del torn de nit (passat): granota de treball, monyo, ulleres al front
  vet      presonera de la cel·la 9 (present): granota de presó, cabell curt punxegut
  cargol   robot de manteniment amb closca de cargol, ulls a les antenes, erugues
  capatas  el capatàs Pruna, adormit a la cadira, amb el segell a les mans (i sense)
  bruc     presoner vell i prim, maquillat
  mare     l'altaveu en forma de cor de la IA (normalment invisible)

Les protagonistes tenen Idle/Walk/Talk en tres direccions (L, D, U; Benne fa el mirall per a R).
Surt a adapters/benne/placeholder-art/<id>/. Ús: python3 draw_characters.py
"""
import json
from pathlib import Path

from PIL import Image

OUT = Path(__file__).resolve().parent.parent / 'placeholder-art'
OUTLINE = (34, 24, 30, 255)
CLEAR = (0, 0, 0, 0)


def rgba(c):
    return c if len(c) == 4 else (*c, 255)


class Canvas:
    def __init__(self, w, h):
        self.img = Image.new('RGBA', (w, h), CLEAR)
        self.w, self.h = w, h

    def px(self, x, y, c):
        if 0 <= x < self.w and 0 <= y < self.h:
            self.img.putpixel((x, y), rgba(c))

    def rect(self, x0, y0, x1, y1, c):
        for y in range(y0, y1 + 1):
            for x in range(x0, x1 + 1):
                self.px(x, y, c)

    def ellipse(self, cx, cy, rx, ry, c):
        for y in range(int(cy - ry), int(cy + ry) + 1):
            for x in range(int(cx - rx), int(cx + rx) + 1):
                if ((x - cx) / (rx + 0.3)) ** 2 + ((y - cy) / (ry + 0.3)) ** 2 <= 1:
                    self.px(x, y, c)

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

IRI = {
    'skin': (226, 176, 134), 'skin2': (196, 142, 106), 'hair': (78, 44, 30), 'hair2': (54, 30, 22),
    'top': (178, 88, 44), 'top2': (140, 64, 32), 'sleeve': (236, 224, 196), 'legs': (178, 88, 44), 'legs2': (140, 64, 32),
    'shoes': (62, 42, 30), 'belt': (82, 56, 34), 'style': 'iri', 'eyes': (40, 30, 30),
}
VET = {
    'skin': (156, 104, 76), 'skin2': (124, 80, 58), 'hair': (64, 196, 196), 'hair2': (38, 140, 152),
    'top': (150, 172, 194), 'top2': (110, 132, 154), 'sleeve': (150, 172, 194), 'legs': (150, 172, 194), 'legs2': (110, 132, 154),
    'shoes': (232, 232, 232), 'belt': None, 'style': 'vet', 'eyes': (30, 24, 30),
}
BRUC = {
    'skin': (214, 170, 140), 'skin2': (184, 138, 110), 'hair': (206, 206, 214), 'hair2': (160, 160, 170),
    'top': (150, 172, 194), 'top2': (110, 132, 154), 'sleeve': (150, 172, 194), 'legs': (150, 172, 194), 'legs2': (110, 132, 154),
    'shoes': (90, 90, 96), 'belt': None, 'style': 'bruc', 'eyes': (20, 16, 24),
}


def person(p, facing, walk=None, talk=False, thin=False):
    """Una persona de peu, 36×64, peus a (18, 61). `walk`: fotograma 0-5 del cicle."""
    c = Canvas(36, 64)
    bob = [0, -1, 0, 0, -1, 0][walk] if walk is not None else 0
    narrow = 1 if thin else 0

    # Cames i peus
    if facing == 'L':
        swing = [-3, -1, 1, 3, 1, -1][walk] if walk is not None else 0
        for leg, off, shade in ((0, -swing, p['legs2']), (1, swing, p['legs'])):
            x = 16 + off
            c.rect(x, 42, x + 3, 57, shade)
            c.rect(x - 2, 58, x + 3, 61, p['shoes'])
    else:
        lift_l = [0, 2, 1, 0, 0, 0][walk] if walk is not None else 0
        lift_r = [0, 0, 0, 0, 2, 1][walk] if walk is not None else 0
        c.rect(13 + narrow, 42, 16, 57 - lift_l, p['legs'])
        c.rect(19, 42, 22 - narrow, 57 - lift_r, p['legs'])
        c.rect(13 + narrow, 58 - lift_l, 16, 61 - lift_l, p['shoes'])
        c.rect(19, 58 - lift_r, 22 - narrow, 61 - lift_r, p['shoes'])
        if p['shoes'] == (232, 232, 232):  # sabatilles: sola fosca
            c.rect(13 + narrow, 61 - lift_l, 16, 61 - lift_l, (90, 90, 96))
            c.rect(19, 61 - lift_r, 22 - narrow, 61 - lift_r, (90, 90, 96))

    y0 = bob
    # Malucs i tors (una mica més estret a les espatlles: silueta femenina a l'Iri i la Vet)
    if facing == 'L':
        c.rect(14, 22 + y0, 21, 41 + y0, p['top'])
        c.rect(19, 22 + y0, 21, 41 + y0, p['top2'])
    else:
        c.rect(13 + narrow, 22 + y0, 22 - narrow, 37 + y0, p['top'])
        c.rect(12 + narrow, 37 + y0, 23 - narrow, 41 + y0, p['legs'])
        c.rect(21 - narrow, 22 + y0, 22 - narrow, 41 + y0, p['top2'])

    # Detalls de la roba
    if p['style'] == 'iri' and facing != 'U':
        if facing == 'D':
            c.rect(14, 22 + y0, 15, 27 + y0, p['sleeve'])        # camisa sota els tirants
            c.rect(20, 22 + y0, 21, 27 + y0, p['sleeve'])
            c.rect(16, 24 + y0, 19, 27 + y0, p['top2'])          # pitet de la granota
        c.rect(13 if facing == 'D' else 14, 33 + y0, 22 if facing == 'D' else 21, 34 + y0, p['belt'])  # cinturó d'eines
        c.rect(20 if facing == 'D' else 15, 34 + y0, 22 if facing == 'D' else 17, 37 + y0, (110, 78, 46))  # bossa
        c.px(21 if facing == 'D' else 16, 35 + y0, (200, 200, 210))  # mànec d'una eina
    if p['style'] in ('vet', 'bruc') and facing == 'D':
        c.rect(19, 25 + y0, 22 - narrow, 28 + y0, (236, 236, 236))  # pegat amb el número
        c.px(20, 26 + y0, (40, 40, 60))
        c.px(21 - narrow, 27 + y0, (40, 40, 60))
        c.rect(17, 22 + y0, 18, 23 + y0, p['skin'])  # coll en V

    # Braços
    arm_top, arm_bot = 23 + y0, 37 + y0
    if facing == 'L':
        swing = [-2, -1, 0, 2, 1, 0][walk] if walk is not None else 0
        ax = 17 + swing
        sleeve_end = 29 + y0 if p['style'] == 'iri' else arm_bot
        c.rect(ax, arm_top, ax + 2, sleeve_end, p['sleeve'] if p['style'] == 'iri' else p['top2'])
        c.rect(ax, sleeve_end + 1, ax + 2, arm_bot, p['skin'])
        c.rect(ax, arm_bot + 1, ax + 2, arm_bot + 2, p['skin2'])
    else:
        sw = [0, 1, 0, 0, -1, 0][walk] if walk is not None else 0
        for ax, s in ((10 + narrow, sw), (23 - narrow, -sw)):
            sleeve_end = 29 + y0 if p['style'] == 'iri' else arm_bot
            c.rect(ax, arm_top + s, ax + 2, sleeve_end + s, p['sleeve'] if p['style'] == 'iri' else p['top2'])
            c.rect(ax, sleeve_end + 1 + s, ax + 2, arm_bot + s, p['skin'])
            c.rect(ax, arm_bot + 1 + s, ax + 2, arm_bot + 2 + s, p['skin2'])

    # Coll i cap
    c.rect(16, 19 + y0, 19, 21 + y0, p['skin2'])
    hx = 17.5 if facing != 'L' else 17
    c.ellipse(hx, 12 + y0, 5, 6.5, p['skin'])
    if facing == 'L':
        c.px(11, 13 + y0, p['skin'])                         # nas
        c.px(12, 13 + y0, p['skin'])
    hair(c, p, facing, y0)

    # Cara
    eye = p['eyes']
    if facing == 'D':
        c.px(15, 12 + y0, eye)
        c.px(20, 12 + y0, eye)
        if p['style'] in ('iri', 'vet'):                      # pestanyes
            c.px(14, 11 + y0, eye)
            c.px(21, 11 + y0, eye)
        if p['style'] == 'bruc':                              # llapis d'ulls i barba blanca
            for x in (14, 16, 19, 21):
                c.px(x, 12 + y0, (60, 30, 70))
            c.rect(14, 16 + y0, 21, 18 + y0, p['hair'])
        mouth = (120, 50, 50)
        if talk:
            c.rect(17, 15 + y0, 18, 16 + y0, (90, 30, 30))
        else:
            c.rect(17, 16 + y0, 18, 16 + y0, mouth)
    elif facing == 'L':
        c.px(14, 12 + y0, eye)
        if p['style'] in ('iri', 'vet'):
            c.px(13, 11 + y0, eye)
        if p['style'] == 'bruc':
            c.px(13, 12 + y0, (60, 30, 70))
            c.rect(13, 16 + y0, 17, 18 + y0, p['hair'])
        c.rect(13, 16 + y0, 14, 16 + (1 if talk else 0) + y0, (90, 30, 30) if talk else (120, 50, 50))

    c.outline()
    return c.img


def hair(c, p, facing, y0):
    h, h2 = p['hair'], p['hair2']
    if p['style'] == 'iri':
        if facing == 'U':
            c.ellipse(17.5, 11 + y0, 5.5, 6.5, h)
            c.ellipse(17.5, 4 + y0, 2.5, 2.5, h2)                # monyo
            c.rect(12, 9 + y0, 23, 9 + y0, (200, 160, 60))     # cinta de les ulleres
        else:
            c.rect(12, 5 + y0, 23, 8 + y0, h)
            c.rect(12, 9 + y0, 13, 15 + y0, h)
            if facing == 'D':
                c.rect(22, 9 + y0, 23, 15 + y0, h)
                c.ellipse(17.5, 3 + y0, 2.5, 2.5, h2)              # monyo dalt
                c.rect(13, 8 + y0, 22, 8 + y0, (200, 160, 60))     # ulleres al front
                c.rect(14, 7 + y0, 16, 8 + y0, (130, 206, 224))
                c.rect(19, 7 + y0, 21, 8 + y0, (130, 206, 224))
            else:
                c.rect(18, 9 + y0, 23, 15 + y0, h)
                c.ellipse(22, 5 + y0, 2.5, 2.5, h2)                # monyo darrere
                c.rect(12, 8 + y0, 18, 8 + y0, (200, 160, 60))
                c.rect(12, 7 + y0, 14, 8 + y0, (130, 206, 224))
    elif p['style'] == 'vet':
        top = 5 + y0
        c.rect(12, top, 23, top + 3, h)
        for x in (13, 16, 19, 22):                             # punxes
            c.px(x, top - 1, h)
            c.px(x + 1, top - 2, h)
        if facing == 'U':
            c.ellipse(17.5, 11 + y0, 5.5, 6.5, h2)               # clatell rapat
            c.rect(12, top, 23, top + 3, h)
        else:
            c.rect(12, top + 4, 12, top + 7, h2)                # laterals rapats
            if facing == 'D':
                c.rect(23, top + 4, 23, top + 7, h2)
                c.rect(14, top + 4, 17, top + 4, h)              # serrell
            else:
                c.rect(19, top + 4, 23, top + 8, h2)
    else:  # bruc: calb, cabells blancs als costats
        if facing == 'U':
            c.ellipse(17.5, 12 + y0, 5.5, 6, h2)
            c.ellipse(17.5, 9 + y0, 4, 3.5, p['skin'])
        else:
            c.rect(12, 9 + y0, 13, 14 + y0, h)
            if facing == 'D':
                c.rect(22, 9 + y0, 23, 14 + y0, h)
            else:
                c.rect(18, 8 + y0, 23, 15 + y0, h)


# ─── Cargol (robot) ─────────────────────────────────────────────────────────

BRASS, BRASS2, BRASS3 = (206, 160, 70), (164, 120, 48), (120, 84, 34)
STEEL, STEEL2 = (186, 196, 206), (140, 150, 162)


def cargol(facing, blink=False, talk=False):
    c = Canvas(40, 46)
    lamp = (120, 240, 170) if not blink else (60, 120, 90)
    if talk:
        lamp = (190, 255, 210)
    # Erugues
    c.rect(7, 37, 32, 44, (70, 70, 78))
    for x in range(9, 32, 4):
        c.ellipse(x, 41, 1.5, 1.5, (40, 40, 46))
    # Closca de cargol (a l'esquena): espiral de llautó
    sx = {'D': 20, 'L': 25, 'U': 20}[facing]
    r = 12 if facing != 'D' else 11
    c.ellipse(sx, 22, r, r, BRASS)
    c.ellipse(sx, 22, r - 3, r - 3, BRASS2)
    c.ellipse(sx + 1, 21, r - 6, r - 6, BRASS)
    c.ellipse(sx + 1, 21, 2, 2, BRASS3)
    if facing != 'U':
        # Cos de metall al davant
        bx0 = 11 if facing == 'D' else 8
        c.rect(bx0, 18, bx0 + 17 - (3 if facing == 'L' else 0), 37, STEEL)
        c.rect(bx0, 33, bx0 + 17 - (3 if facing == 'L' else 0), 37, STEEL2)
        # Pantalla-cara
        fx = 14 if facing == 'D' else 9
        c.rect(fx, 22, fx + 11 - (4 if facing == 'L' else 0), 29, (36, 44, 56))
        c.rect(fx + 2, 25, fx + 3, 26, lamp)
        if facing == 'D':
            c.rect(fx + 8, 25, fx + 9, 26, lamp)
        # Reixeta de la boca
        gy = 28 if not talk else 27
        for x in range(fx + 2, fx + (10 if facing == 'D' else 6), 2):
            c.px(x, gy, (150, 160, 170))
        # Braç amb clau anglesa
        ax = 30 if facing == 'D' else 6
        c.rect(ax, 25, ax + 1, 32, STEEL2)
        c.rect(ax - 1, 33, ax + 2, 34, (200, 200, 210))
    # Antenes amb ulls (com un cargol)
    stalks = [(15, 24)] if facing == 'L' else [(14, 25)]
    if facing == 'L':
        stalks = [(10, 14)]
    for x0, x1 in [stalks[0]] if facing == 'L' else [(14, 14), (25, 25)]:
        top = 6 if not talk else 5
        for y in range(top + 2, 19):
            c.px(x0, y, STEEL2)
        c.ellipse(x0, top, 2, 2, lamp)
        c.px(x0, top, (255, 255, 255))
    c.outline()
    return c.img


# ─── El capatàs Pruna, adormit ──────────────────────────────────────────────

def capatas(breath=0, with_seal=True, talk=False, zz=0):
    c = Canvas(48, 60)
    wood, wood2 = (122, 82, 50), (92, 60, 36)
    shirt, shirt2 = (222, 214, 196), (190, 180, 160)
    trousers = (84, 74, 70)
    skin, skin2 = (230, 170, 140), (200, 140, 112)
    # Cadira (respatller darrere, seient, potes)
    c.rect(9, 14, 36, 40, wood2)
    c.rect(11, 16, 34, 38, wood)
    c.rect(7, 40, 38, 43, wood)
    for x in (8, 36):
        c.rect(x, 44, x + 2, 58, wood2)
    # Cames (assegut: cuixes endavant, canyelles avall)
    c.rect(12, 40, 21, 45, trousers)
    c.rect(24, 40, 33, 45, trousers)
    c.rect(13, 46, 19, 54, trousers)
    c.rect(26, 46, 32, 54, trousers)
    c.rect(12, 55, 20, 58, (50, 36, 28))
    c.rect(25, 55, 33, 58, (50, 36, 28))
    # Panxa i tors (respira)
    c.ellipse(22.5, 32, 11 + breath, 9 + breath * 0.5, shirt)
    c.rect(13, 20, 32, 30, shirt)
    c.rect(28, 20, 32, 38, shirt2)
    c.rect(16, 20, 17, 40, (120, 40, 40))   # tirants
    c.rect(28, 20, 29, 40, (120, 40, 40))
    c.rect(17, 41, 28, 42, (60, 46, 36))    # cinturó
    # Braços creuats sobre la panxa
    c.rect(12, 30, 33, 34, shirt2)
    c.rect(18, 31, 27, 34, skin)
    if with_seal:
        c.rect(20, 25, 22, 31, (180, 44, 44))      # mànec vermell del segell
        c.ellipse(21, 24, 2, 1.5, (180, 44, 44))
        c.rect(18, 32, 25, 34, (110, 74, 40))      # base de fusta
    # Cap, decantat i amb la gorra sobre els ulls
    c.rect(20, 17, 25, 19, skin2)
    c.ellipse(23, 12, 6, 6.5, skin)
    c.rect(16, 4, 30, 9, (96, 96, 104))            # gorra
    c.rect(14, 9, 29, 10, (70, 70, 78))            # visera
    c.rect(19, 12, 21, 12, (60, 40, 40))           # ulls tancats
    c.rect(25, 12, 27, 12, (60, 40, 40))
    c.rect(19, 15, 28, 16, (70, 48, 40))           # bigoti
    if talk:
        c.rect(22, 17, 24, 18, (90, 30, 30))
    else:
        c.px(23, 17, (90, 30, 30))                 # roncant
    # Zetes
    if zz:
        for i in range(zz):
            x, y = 33 + i * 4, 8 - i * 4
            for (dx, dy) in ((0, 0), (1, 0), (2, 0), (1, 1), (0, 2), (1, 2), (2, 2)):
                c.px(x + dx, y + dy, (255, 255, 255))
    c.outline()
    return c.img


def mare(glow=False):
    c = Canvas(16, 16)
    pink = (255, 120, 180) if not glow else (255, 170, 210)
    c.ellipse(5, 6, 3.5, 3.5, pink)
    c.ellipse(10, 6, 3.5, 3.5, pink)
    for y in range(7, 14):
        w = 13 - y
        c.rect(7.5 - w if False else int(7.5 - w), y, int(7.5 + w), y, pink)
    for x in (5, 7, 9):
        c.px(x, 7, (120, 40, 80))
    c.outline()
    return c.img


# ─── Fulls i definicions ────────────────────────────────────────────────────

def write(cid, tags, size, extra):
    """tags: [(nom, [imatges])]. Escriu <id>.png, <id>.json (Aseprite) i <id>.character.json."""
    w, h = size
    frames = [img for _, imgs in tags for img in imgs]
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
    standing('bruc', BRUC, thin=True)

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
    main()
