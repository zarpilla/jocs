#!/usr/bin/env python3
"""
Prova de resolució: la barra de verbs a 640×360 (la franja de y=260 a 359, 640×100), redibuixada.

Mateix estil que hd/gui.py (planxa blau marí amb reblons, la corda trenada, plaques de verb, caselles amb
cantoneres de llautó, l'ull de bou del botó «Canvia»), amb la geometria ×4/3 arrodonida a mà, i els textos
amb la font de mapa de bits de 640 (hd640/font.py: majúscules de 9 px, minúscules de 6, negreta de traç
de 2 px), que és la que caldria per a les GUI a 640.

    from hd640.gui import verb_bar
    img = verb_bar()                                  # Image RGBA 640×100, per enganxar a (0, 260)
    img = verb_bar({'hover': 'look', 'line': 'Mira el panell'})

Provisional: les icones d'inventari i la cara de l'ull de bou són les de 480 ampliades ×4/3.

`python3 hd640/gui.py <sortida.png>` munta la comparativa: la barra de 480 (×4, amb els textos amb la font
del joc) sobre la de 640 (×3), totes dues a 1920 d'ample.
"""
import json
import math
import sys
from pathlib import Path

from PIL import Image

TOOLS = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(TOOLS))

import hd640  # noqa: E402,F401  (posa la llibreria a 640×360)
from hd.pix import Canvas, hr  # noqa: E402
from hd.gui import (NAVYB, ROPE, BRASS, HOT, GLASS, TEXT, TEXT_HOVER, TEXT_OUTLINE, VERB_LINE,  # noqa: E402
                    box, dark, rivet, plate, corners, well, arrow)

GAME = TOOLS.parents[2] / 'aigua-bruta/src/game'
W, Y0, BH = 640, 260, 100          # la barra: 640×100, a partir de y=260 de la pantalla

# ─── Geometria (coordenades dins la barra, y=0 és la y=260 de la pantalla) ──
STRIP_H = 13                       # franja fosca de la frase (195..204 a 480 → 0..12)
ROPE_Y = 13                        # corda trenada, 4 px
VERB_H = 21
VERB_COLS = ((65, 73), (141, 99), (244, 73))          # (x, amplada)
VERB_ROWS = (21, 47, 73)
VERB_IDS = (('give', 'pickUp', 'use'), ('open', 'talkTo', 'push'), ('close', 'look', 'pull'))
VERB_TEXT = {'give': 'Dona', 'pickUp': 'Agafa', 'use': 'Usa', 'open': 'Obre', 'talkTo': 'Parla',
             'push': 'Empeny', 'close': 'Tanca', 'look': 'Mira', 'pull': 'Estira'}
INV_X, INV_Y, SLOT_W, SLOT_H, GAP = 336, 20, 65, 36, 4
ARROWS = {'up': (320, 20), 'down': (320, 60)}          # 13×36
MENU = (36, 69, 25)
CANVIA = (4, 21, 57, 43)
PORT = (32, 42)                                         # centre de l'ull de bou
SEAMS = (62, 614)


def slots():
    for r in range(2):
        for c in range(4):
            yield INV_X + c * (SLOT_W + GAP), INV_Y + r * (SLOT_H + GAP)


# ─── Font de 640 (FONT640): és a hd640/font.py ─────────────────────────────
from hd640.font import font640, text_width, draw_text as _draw_text  # noqa: E402


def draw_text(img, glyphs, s, x, y, color, outline=TEXT_OUTLINE, space=4):
    """Text de mapa de bits a (x, y) (dalt de la línia), amb la vora de baix a la dreta com al joc."""
    _draw_text(img, glyphs, s, x, y, color, outline=outline, space=space)


# ─── Peces ─────────────────────────────────────────────────────────────────

def body(cv, y0, y1):
    for y in range(y0, y1 + 1):
        for x in range(W):
            cv.put(x, y, NAVYB, 3.0 - (y - y0) * 0.009 + (hr(x // 4, y // 5) - 0.5) * 0.3, lit=0)
    # escates de pintura i rovell, ara que hi ha píxels per fer-ho
    for i in range(70):
        x, y = int(hr(i, 1) * W), int(y0 + 6 + hr(i, 2) * (y1 - y0 - 8))
        cv.put(x, y, NAVYB, 4.6, lit=0)
        if hr(i, 3) > 0.7:
            cv.put(x, y + 1, [(40, 22, 16), (80, 44, 26), (120, 70, 36)], 1.0, lit=0)


def rope(cv, y):
    """Corda trenada de 4 px, amb els cordons en diagonal."""
    for x in range(W):
        for dy in range(4):
            ph = (x + dy * 2) % 8
            cv.put(x, y + dy, ROPE, 3.6 - abs(ph - 3.5) * 0.5 - dy * 0.25, lit=0)
            if ph == 0:
                cv.put(x, y + dy, ROPE, 1.0, lit=0)
    for x in range(W):
        dark(cv, x, y + 4, 0.5)
        if x % 3 == 0:
            dark(cv, x, y + 5, 0.25)


def seam(cv, x, y0, y1):
    for y in range(y0, y1 + 1):
        cv.put(x, y, NAVYB, 1.0, lit=0)
        cv.put(x + 1, y, NAVYB, 4.2, lit=0)
    for y in range(y0 + 5, y1 - 2, 12):
        rivet(cv, x - 3, y)
        rivet(cv, x + 4, y + 6)


def big_rivet(cv, x, y, lvl=5.4):
    """Rebló de 2×2 amb ombra (a 480 n'era un punt)."""
    cv.put(x, y, NAVYB, lvl + 1.2, lit=0)
    cv.put(x + 1, y, NAVYB, lvl, lit=0)
    cv.put(x, y + 1, NAVYB, lvl - 0.4, lit=0)
    cv.put(x + 1, y + 1, NAVYB, lvl - 1.6, lit=0)
    cv.put(x + 2, y + 2, NAVYB, 0.6, lit=0)


def verb_plate(cv, x0, y0, x1, y1, face=4.4):
    """Placa de verb: la de 480 amb bisell de 2 px i reblons de 2×2."""
    plate(cv, x0, y0, x1, y1, face, rivets=False)
    cv.hline(x0 + 2, x1 - 2, y0 + 2, NAVYB, face + 0.5, lit=0)
    cv.vline(x0 + 1, y0 + 2, y1 - 2, NAVYB, face + 0.6, lit=0)
    cv.hline(x0 + 2, x1 - 1, y1 - 1, NAVYB, face - 0.9, lit=0)
    for bx, by in ((x0 + 3, y0 + 3), (x1 - 4, y0 + 3), (x0 + 3, y1 - 4), (x1 - 4, y1 - 4)):
        cv.put(bx, by, NAVYB, face + 2.4, lit=0)
        cv.put(bx + 1, by + 1, NAVYB, face - 1.4, lit=0)


def menu_button(cv):
    x, y, s = MENU
    box(cv, x, y, x + s - 1, y + s - 1, NAVYB, 4.0)
    cv.hline(x + 1, x + s - 2, y + 1, NAVYB, 5.0, lit=0)
    for yy in (y + 6, y + 11, y + 16):
        cv.hline(x + 5, x + s - 7, yy, ROPE, 3.8, lit=0)
        cv.hline(x + 5, x + s - 7, yy + 1, ROPE, 2.6, lit=0)
        cv.hline(x + 6, x + s - 6, yy + 2, NAVYB, 1.6, lit=0)


def porthole(cv, hover=False):
    x, y, w, h = CANVIA
    box(cv, x, y, x + w - 1, y + h - 1, NAVYB, 4.2 if hover else 3.6)
    cv.hline(x + 1, x + w - 2, y + 1, NAVYB, 5.0 if hover else 4.6, lit=0)
    for bx, by in ((x + 3, y + 3), (x + w - 5, y + 3), (x + 3, y + h - 5), (x + w - 5, y + h - 5)):
        big_rivet(cv, bx, by, 5.6)
    cx, cy = PORT
    lift = 0.8 if hover else 0.0
    cv.disc(cx + 0.5, cy + 0.8, 18.5, 18.5, NAVYB, 1.0, lit=0)
    cv.disc(cx, cy, 17.5, 17.5, BRASS, lambda nx, ny: 3.6 + lift - nx - ny * 1.2, lit=0)
    cv.disc(cx, cy, 14.5, 14.5, BRASS, lambda nx, ny: 2.2 + lift + nx + ny * 1.2, lit=0)
    cv.disc(cx, cy, 13.5, 13.5, GLASS, lambda nx, ny: 1.4 + (0.6 if hover else 0) - ny, lit=0)
    for a in range(0, 360, 60):
        bx = cx + round(math.cos(math.radians(a + 30)) * 16)
        by = cy + round(math.sin(math.radians(a + 30)) * 16)
        cv.put(bx, by, BRASS, 5.6 + lift, lit=0)
        cv.put(bx - 1, by, BRASS, 4.4 + lift, lit=0)
        cv.put(bx + 1, by + 1, BRASS, 0.6, lit=0)


def face(who='vet'):
    """La cara de l'altra protagonista dins el vidre (provisional: la de 480 ampliada ×4/3)."""
    from hd.gui import face_porthole
    f = face_porthole(who)
    return f.resize((round(f.width * 4 / 3), round(f.height * 4 / 3)), Image.NEAREST)


def inv_icons(ids):
    """Icones d'inventari (provisional: les de 480, 49×27, ampliades ×4/3 a 65×36)."""
    d = GAME / 'assets/images/inventory'
    meta = json.loads((d / 'inventory.json').read_text())
    sheet = Image.open(d / 'inventory.png').convert('RGBA')
    frames = list(meta['frames'].values())
    tags = {t['name']: t['from'] for t in meta['meta']['frameTags']}
    out = []
    for i in ids:
        f = frames[tags[i]]['frame']
        ic = sheet.crop((f['x'], f['y'], f['x'] + f['w'], f['y'] + f['h']))
        out.append(ic.resize((SLOT_W, SLOT_H), Image.NEAREST))
    return out


# ─── La barra ──────────────────────────────────────────────────────────────

def background():
    cv = Canvas(W, BH, transparent=True)
    cv.rect(0, 0, W - 1, STRIP_H - 1, NAVYB, 0.6, lit=0)
    body(cv, ROPE_Y, BH - 1)
    rope(cv, ROPE_Y)
    for x in range(10, W, 53):
        big_rivet(cv, x, BH - 6, 4.4)
    for sx in SEAMS:
        seam(cv, sx, 20, BH - 4)
    # la plaqueta de llautó de la dreta, amb tres cargols de cap pla
    box(cv, 621, 25, 632, 93, BRASS, 1.6)
    cv.vline(622, 26, 92, BRASS, 2.6, lit=0)
    for yy in (31, 59, 87):
        cv.disc(626.5, yy, 2.2, 2.2, BRASS, lambda nx, ny: 4.4 - nx - ny, lit=0)
        cv.line(625, yy + 1, 628, yy - 2, BRASS, 0.8, lit=0)
    big_rivet(cv, 9, 70)
    big_rivet(cv, 9, 84)
    for row, vy in zip(VERB_IDS, VERB_ROWS):
        for (vx, vw), _vid in zip(VERB_COLS, row):
            verb_plate(cv, vx, vy, vx + vw - 1, vy + VERB_H - 1)
    for ax, ay in ARROWS.values():
        box(cv, ax, ay, ax + 12, ay + 35, NAVYB, 4.0)
        cv.hline(ax + 1, ax + 11, ay + 1, NAVYB, 5.0, lit=0)
    for sx, sy in slots():
        well(cv, sx, sy, sx + SLOT_W - 1, sy + SLOT_H - 1, brass=False)
        corners(cv, sx + 1, sy + 1, sx + SLOT_W - 2, sy + SLOT_H - 2, n=6)
        for cx, cy in ((sx + 3, sy + 3), (sx + SLOT_W - 4, sy + 3), (sx + 3, sy + SLOT_H - 4), (sx + SLOT_W - 4, sy + SLOT_H - 4)):
            cv.put(cx, cy, BRASS, 4.6, lit=0)                            # el cargol de la cantonera
    menu_button(cv)
    return cv


def verb_bar(state=None):
    """La barra completa (640×100). state: {'hover': id de verb o 'up'/'down'/'canvia', 'line': frase,
    'inv': [ids d'objecte], 'face': 'iri'|'vet'}."""
    st = {'hover': None, 'line': 'Usa la cisalla amb el cable', 'inv': ('walkie', 'cisalla', 'mostra7'),
          'face': 'vet'}
    st.update(state or {})
    cv = background()
    for which, (ax, ay) in ARROWS.items():
        hot = st['hover'] == which
        if hot:
            box(cv, ax, ay, ax + 12, ay + 35, NAVYB, 4.8)
        arrow(cv, ax + 6, ay + 18, which == 'up', hot, length=15)
    porthole(cv, st['hover'] == 'canvia')
    img = cv.img
    f = face(st['face'])
    img.alpha_composite(f, (PORT[0] - f.width // 2, PORT[1] - f.height // 2 - 1))
    for ic, (sx, sy) in zip(inv_icons(st['inv']), slots()):
        img.alpha_composite(ic, (sx, sy))
    bold, reg = font640(True), font640(False)
    for row, vy in zip(VERB_IDS, VERB_ROWS):
        for (vx, vw), vid in zip(VERB_COLS, row):
            s = VERB_TEXT[vid]
            tw = text_width(bold, s, 4)
            draw_text(img, bold, s, vx + (vw - tw) // 2, vy + 2, TEXT_HOVER if st['hover'] == vid else TEXT)
    tw = text_width(reg, st['line'], 4)
    draw_text(img, reg, st['line'], (W - tw) // 2, -2, VERB_LINE, outline=None)
    return img


# ─── Comparativa amb la de 480 ─────────────────────────────────────────────

def bar480(line='Usa la cisalla amb el cable', inv=('walkie', 'cisalla', 'mostra7'), hover=None):
    """La barra de 480 (fotogrames de hd/gui.py + textos amb la font del joc), retallada a 480×75."""
    from hd import gui as g
    sys.path.insert(0, str(TOOLS.parents[2] / 'tools/font'))
    import aigua_font as af
    img = Image.new('RGBA', (480, 270), (0, 0, 0, 0))
    for layer in (g.verbs_bg(), g.verbs_arrow('up', hover == 'up'), g.verbs_arrow('down', hover == 'down'),
                  g.menu_button(), g.canvia(False), g.face_frame('vet')):
        img.alpha_composite(layer)
    d = GAME / 'assets/images/inventory'
    meta = json.loads((d / 'inventory.json').read_text())
    sheet = Image.open(d / 'inventory.png').convert('RGBA')
    frames = list(meta['frames'].values())
    tags = {t['name']: t['from'] for t in meta['meta']['frameTags']}
    for i, (sx, sy) in zip(inv, g.slots()):
        f = frames[tags[i]]['frame']
        img.alpha_composite(sheet.crop((f['x'], f['y'], f['x'] + f['w'], f['y'] + f['h'])), (sx, sy))
    bold, reg = af.all_glyphs(True), af.all_glyphs(False)
    ids = ('give', 'pickUp', 'use', 'open', 'talkTo', 'push', 'close', 'look', 'pull')
    for (vx, vy, vw), vid in zip(g.VERBS, (ids[0], ids[1], ids[2], ids[3], ids[4], ids[5], ids[6], ids[7], ids[8])):
        s = VERB_TEXT[vid]
        tw = text_width(bold, s, af.SPACE_ADVANCE)
        draw_text(img, bold, s, vx + (vw - tw) // 2, vy + 2, TEXT_HOVER if hover == vid else TEXT, space=af.SPACE_ADVANCE)
    tw = text_width(reg, line, af.SPACE_ADVANCE)
    draw_text(img, reg, line, 240 - tw // 2, 192, VERB_LINE, outline=None, space=af.SPACE_ADVANCE)
    return img.crop((0, 195, 480, 270))


def main():
    out = Path(sys.argv[1]) if len(sys.argv) > 1 else Path('barra_640.png')
    from PIL import ImageDraw
    a = bar480(hover='look').resize((1920, 300), Image.NEAREST)
    b = verb_bar({'hover': 'look'}).resize((1920, 300), Image.NEAREST)
    gap = 40
    o = Image.new('RGB', (1920, 300 * 2 + gap * 2), (30, 30, 30))
    d = ImageDraw.Draw(o)
    d.text((8, 10), 'ACTUAL 480x270: barra 480x75, x4', fill=(255, 255, 255))
    o.paste(a, (0, gap))
    d.text((8, gap + 300 + 10), 'PROVA 640x360: barra 640x100, x3', fill=(255, 255, 255))
    o.paste(b, (0, gap * 2 + 300))
    o.save(out)
    verb_bar().save(out.with_name(out.stem + '_sola.png'))
    print(f'✔ {out}')


if __name__ == '__main__':
    main()
