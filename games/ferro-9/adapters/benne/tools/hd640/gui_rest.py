#!/usr/bin/env python3
"""
La interfície de Ferro-9 a 640×360, menys el dibuix de la barra de verbs (que és a hd640/gui.py).

Redibuixa, amb el mateix estil que la barra de 640 (planxa de metall blau-pissarra amb reblons i el fil de
llautó), els fulls de totes les GUI del joc i en fa els .gui.json a 640, sense tocar el joc:

  hd640/guis/<gui>/<gui>.png + .json      el full (mateixes etiquetes i 9-slice que el del joc)
  hd640/guis/<gui>/<gui>.gui.json         la GUI a 640: mateixos controls, ids, etiquetes, textos i comportament;
                                          posicions i mides ×4/3, ajustades a mà on cal; mateixes fonts (les de
                                          hd640/font.py, que s'exporten amb els mateixos noms), fontSize 8
  hd640/guis/cursor/cursor.png + .json    el punter, un terç més gran (43×43)
  hd640/guis/game-config.640.json         el que canvia a game-config.json (resolució, llista d'opcions)

GUI: verbs (la barra en fotogrames, com verbs.png, amb el botó «Canvia»), dialog, display-text, game-menu (amb
els botons de tools/menu_gui.py: btn-mig, btn-ample i el separador), save-menu, load-menu, settings-menu,
portada (els botons de draw_placeholders.draw_cover_gui) i speaking-text (sense full). L'historial no: el torna a
fer l'adaptador (joc.ts) a 640, amb el full del game-menu nou.

    python3 hd640/gui_rest.py [carpeta de comparatives]

Llegeix els .gui.json actuals del joc (ferro-9/src/game/guis) per escalar-los. Amb una carpeta, també hi munta
les comparatives (cada GUI a 480 ×4 i a 640 ×3, amb textos) i una pantalla completa de mostra.
"""
import copy
import json
import math
import sys
from pathlib import Path

from PIL import Image, ImageDraw

TOOLS = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(TOOLS))

import hd640  # noqa: E402,F401  (posa la llibreria a 640×360)
import hd640.gui as vg  # noqa: E402
from hd.pix import Canvas, hr  # noqa: E402
from hd.gui import SLATE, BRASS, TEXT_OUTLINE, dark  # noqa: E402
from hd640.gui import body, well, rivet, brass_trim, arrow  # noqa: E402
from hd640.font import font640, text_width as tw640, draw_text as dt640, LINE_H as LH640  # noqa: E402

sys.path.insert(0, str(TOOLS.parents[2] / 'tools'))
from pixels import nearest  # noqa: E402
import menu_gui  # noqa: E402  (els colors dels botons del menú del joc)

W, H = 640, 360
K = 4 / 3
GAME = TOOLS.parents[2] / 'ferro-9/src/game'
OUT = Path(__file__).resolve().parent / 'guis'
SKIP = ('historial',)                     # el fa joc.ts


def s(v):
    return int(math.floor(v * K + 0.5)) if v >= 0 else -int(math.floor(-v * K + 0.5))


# ─── Fulls (format d'Aseprite, com hd/gui.py) ──────────────────────────────

def write_sheet(gdir, name, items, cols=None, slices=None, base=None):
    """items: [(img, tag, src_xy, source_size)]. Empaqueta en files (com els fulls del joc) i escriu png + json."""
    gdir.mkdir(parents=True, exist_ok=True)
    base = base or name
    placed, x, y, row_h, width = [], 0, 0, 0, 0
    maxw = max(1920, max(im.width for im, *_ in items))
    for i, (im, tag, src, size) in enumerate(items):
        if (cols and i and i % cols == 0) or x + im.width > maxw:
            x, y, row_h = 0, y + row_h, 0
        placed.append((x, y))
        x += im.width
        row_h = max(row_h, im.height)
        width = max(width, x)
    sheet = Image.new('RGBA', (width, y + row_h), (0, 0, 0, 0))
    frames, tags = {}, []
    for i, ((im, tag, src, size), (px, py)) in enumerate(zip(items, placed)):
        sheet.paste(im, (px, py))
        frames[f'{base} {i}.aseprite'] = {
            'frame': {'x': px, 'y': py, 'w': im.width, 'h': im.height}, 'rotated': False,
            'trimmed': src != (0, 0) or size != im.size,
            'spriteSourceSize': {'x': src[0], 'y': src[1], 'w': im.width, 'h': im.height},
            'sourceSize': {'w': size[0], 'h': size[1]}, 'duration': 100}
        if tag:
            tags.append({'name': tag, 'from': i, 'to': i, 'direction': 'forward', 'color': '#000000ff'})
    meta = {'app': 'https://www.aseprite.org/', 'version': 'hd640/gui_rest.py', 'image': f'{name}.png',
            'format': 'RGBA8888', 'size': {'w': sheet.width, 'h': sheet.height}, 'scale': '1',
            'frameTags': tags, 'layers': [], 'slices': slices or []}
    sheet.save(gdir / f'{name}.png')
    (gdir / f'{name}.json').write_text(json.dumps({'frames': frames, 'meta': meta}, indent=1) + '\n')


# ─── 9-slice dels menús ─────────────────────────────────────────────────────

NS_W, NS_H, NS_B = 40, 26, 9        # 40×26, vores de 9 (a 480: 30×20, vores de 7)


def nine_slice():
    """El marc dels menús (com hd/gui.nine_slice, a 640): contorn fosc, doble fil de llautó (clar i fosc, ara de
    3 files), ranura, bisell de pissarra i cara plana; cantons arrodonits i un rebló de llautó de 4×4 a cada
    cantó."""
    img = Image.new('RGBA', (NS_W, NS_H), (0, 0, 0, 0))
    P = img.load()
    face = SLATE[2]
    ring = [SLATE[0], BRASS[5], BRASS[4], BRASS[2], SLATE[0], SLATE[5], SLATE[4], SLATE[3]]
    ring_lo = [SLATE[0], BRASS[3], BRASS[2], BRASS[1], SLATE[0], SLATE[1], SLATE[1], SLATE[2]]
    for y in range(NS_H):
        for x in range(NS_W):
            d = min(x, y, NS_W - 1 - x, NS_H - 1 - y)
            if d < len(ring):
                lo = (NS_H - 1 - y == d) or (NS_W - 1 - x == d)
                col = (ring_lo if lo else ring)[d]
            else:
                col = face                                # el centre s'estira: pla
            P[x, y] = col + (255,)
    for cx, cy in ((0, 0), (NS_W - 1, 0), (0, NS_H - 1), (NS_W - 1, NS_H - 1)):   # cantons arrodonits
        P[cx, cy] = (0, 0, 0, 0)
        P[abs(cx - 1), cy] = SLATE[0] + (255,)
        P[cx, abs(cy - 1)] = SLATE[0] + (255,)
    # reblons de llautó a les cantonades (dins els 9×9): cap rodó amb el reflex a dalt a l'esquerra
    for cx, cy in ((2, 2), (NS_W - 6, 2), (2, NS_H - 6), (NS_W - 6, NS_H - 6)):
        for dx, dy, c in ((1, 0, BRASS[6]), (2, 0, BRASS[5]), (0, 1, BRASS[5]), (1, 1, BRASS[7]), (2, 1, BRASS[5]),
                          (3, 1, BRASS[3]), (0, 2, BRASS[4]), (1, 2, BRASS[4]), (2, 2, BRASS[3]), (3, 2, BRASS[2]),
                          (1, 3, BRASS[2]), (2, 3, BRASS[1])):
            P[cx + dx, cy + dy] = c + (255,)
    return img


def nine_slices(frame=0):
    b, mw, mh = NS_B, NS_W - 2 * NS_B, NS_H - 2 * NS_B
    rects = {'TopLeft': (0, 0, b, b), 'TopMid': (b, 0, mw, b), 'TopRight': (b + mw, 0, b, b),
             'MidLeft': (0, b, b, mh), 'Mid': (b, b, mw, mh), 'MidRight': (b + mw, b, b, mh),
             'BottomLeft': (0, b + mh, b, b), 'BottomMid': (b, b + mh, mw, b), 'BottomRight': (b + mw, b + mh, b, b)}
    return [{'name': n, 'color': '#0000ffff', 'keys': [{'frame': frame, 'bounds': {'x': x, 'y': y, 'w': w, 'h': h}}]}
            for n, (x, y, w, h) in rects.items()]


# ─── Botons del menú del joc (tools/menu_gui.py, a 640) ────────────────────

BTN = {'mig': (91, 27), 'ample': (185, 27)}       # a 480: 68×20 i 139×20


def menu_button(w, h, estat):
    """Placa de botó (com menu_gui.boto): vora d'1 px amb els cantons retallats, bisell de 2 px (llum a dalt i a
    l'esquerra; al revés quan està premut), una ratlla fina sota la llum, el raspallat de la planxa i un cargol
    de 2×2 a cada cantonada (a 480, un punt); en hover, els amples porten les fletxetes daurades."""
    vora, placa, llum, ombra, cargol = menu_gui.ESTATS[estat]
    im = Image.new('RGBA', (w, h), (0, 0, 0, 0))
    d = ImageDraw.Draw(im)
    d.rectangle([1, 0, w - 2, h - 1], fill=vora)
    d.rectangle([0, 1, w - 1, h - 2], fill=vora)
    d.rectangle([1, 1, w - 2, h - 2], fill=placa)
    mig = tuple((a + b) // 2 for a, b in zip(llum, placa))
    P = im.load()
    for y in range(3, h - 3):                                     # el raspallat: vetes horitzontals molt fluixes
        if hr(907, y, w) > 0.6:
            t = 0.18 if estat != 'pressed' else 0.12
            for x in range(3, w - 3):
                if hr(908, x // 13, y) > 0.35:
                    P[x, y] = tuple(round(a + (b - a) * t) for a, b in zip(placa, llum)) + (255,)
    d.line([2, 1, w - 3, 1], fill=llum)
    d.line([2, 2, w - 3, 2], fill=llum)
    d.line([1, 2, 1, h - 3], fill=llum)
    d.line([2, 3, 2, h - 4], fill=mig)
    d.line([3, 3, w - 4, 3], fill=mig)
    d.line([2, h - 2, w - 3, h - 2], fill=ombra)
    d.line([3, h - 3, w - 3, h - 3], fill=ombra)
    d.line([w - 2, 2, w - 2, h - 3], fill=ombra)
    d.line([w - 3, 3, w - 3, h - 4], fill=ombra)
    for x, y in ((4, 4), (w - 6, 4), (4, h - 6), (w - 6, h - 6)):  # cargols de 2×2, amb el reflex
        P[x, y] = tuple(min(255, c + 40) for c in cargol) + (255,)
        P[x + 1, y] = cargol + (255,)
        P[x, y + 1] = cargol + (255,)
        P[x + 1, y + 1] = tuple(c * 2 // 3 for c in cargol) + (255,)
    if estat == 'hover' and w > 100:                              # fletxetes daurades a banda i banda
        cy = h // 2 - 1
        for dx in range(4):
            d.line([7 + dx, cy - 3 + dx, 7 + dx, cy + 3 - dx], fill=menu_gui.OR_BRILL)
            d.line([w - 8 - dx, cy - 3 + dx, w - 8 - dx, cy + 3 - dx], fill=menu_gui.OR_BRILL)
        d.point((7, cy - 3), fill=menu_gui.OR_CLAR)
        d.point((w - 8, cy - 3), fill=menu_gui.OR_CLAR)
    return im


def separador(w=147, h=4):
    """El separador de sota el títol (menu_gui.separador, a 640): fil de llautó de 2 files que s'encén cap al mig
    i un rombe de 4×4."""
    im = Image.new('RGBA', (w, h), (0, 0, 0, 0))
    d = ImageDraw.Draw(im)
    mig = w // 2
    for y, k in ((1, 0), (2, 1)):
        fosc = menu_gui.OR_FOSC if not k else (60, 42, 22)
        d.line([5, y, w - 6, y], fill=fosc)
        d.line([21, y, w - 22, y], fill=menu_gui.OR if not k else menu_gui.OR_FOSC)
        d.line([mig - 24, y, mig + 24, y], fill=menu_gui.OR_CLAR if not k else menu_gui.OR)
    d.line([mig - 1, 0, mig + 1, 0], fill=menu_gui.OR_BRILL)
    d.line([mig - 4, 1, mig + 4, 1], fill=menu_gui.OR_BRILL)
    d.line([mig - 4, 2, mig + 4, 2], fill=menu_gui.OR_CLAR)
    d.line([mig - 1, 3, mig + 1, 3], fill=menu_gui.OR)
    return im


# ─── Caselles i lliscadors (settings-menu) ──────────────────────────────────

CELL = (93, 27)                                    # els fotogrames del full de les opcions (70×20 a 480)
BOX_C = {'': (19, 34, 67), 'hover': (26, 70, 107), 'disabled': (99, 99, 99)}   # colors del joc
CHECK = (16, 144, 142)


def _bright(c, k):
    return tuple(max(0, min(255, round(v * k))) for v in c)


def checkbox(state):
    """Casella de 16×16 (a 480, 12×12) per a un control de 21×21: vora d'1 px amb el color del joc i, a dins, un
    filet de bisell (fosc a dalt, clar a baix); marcada, la «v» verd blavós de traç de 2 px."""
    im = Image.new('RGBA', CELL, (0, 0, 0, 0))
    P = im.load()
    key = 'disabled' if 'disabled' in state else ('hover' if 'hover' in state else '')
    c = BOX_C[key]
    n = 16
    for i in range(n):
        for (x, y) in ((i, 0), (i, n - 1), (0, i), (n - 1, i)):
            P[x, y] = c + (255,)
    for i in range(1, n - 1):                                     # el bisell de dins, mig transparent
        P[i, 1] = _bright(c, 0.55) + (150,)
        P[1, i] = _bright(c, 0.55) + (150,)
        P[i, n - 2] = _bright(c, 1.3) + (110,)
        P[n - 2, i] = _bright(c, 1.3) + (110,)
    if 'checked' in state:
        ink = c if key == 'disabled' else CHECK
        hi = _bright(ink, 1.35) if key != 'disabled' else ink
        stroke = [(3, 8), (4, 9), (5, 10), (6, 11), (7, 12), (8, 11), (8, 10), (9, 9), (9, 8), (10, 7), (10, 6),
                  (11, 5), (11, 4), (12, 3)]
        for x, y in stroke:
            P[x, y] = hi + (255,)
            P[x + 1, y] = ink + (255,)
            P[x, y + 1] = ink + (255,)
    return im


def slider_handle(state):
    """El cursor del lliscador: 4×15 amb els caps arrodonits (a 480, 3×11); en hover, la ratlla del mig verd
    blavós."""
    im = Image.new('RGBA', CELL, (0, 0, 0, 0))
    P = im.load()
    c = BOX_C['disabled'] if state == 'disabled' else BOX_C['hover']
    for y in range(15):
        for x in range(4):
            if y in (0, 14) and x in (0, 3):
                continue
            v = c
            if x == 0:
                v = _bright(c, 1.25)
            elif x == 3:
                v = _bright(c, 0.7)
            if state == 'hover' and x in (1, 2) and 0 < y < 14:
                v = CHECK if x == 1 else _bright(CHECK, 0.8)
            P[x, y] = v + (255,)
    return im


def slider_track(disabled):
    """El carril: 93×4 (a 480, 70×3), amb els caps arrodonits i el filet de llum a sota."""
    im = Image.new('RGBA', CELL, (0, 0, 0, 0))
    P = im.load()
    c = BOX_C['disabled'] if disabled else BOX_C['']
    for x in range(CELL[0]):
        for y in range(5, 9):
            if (x in (0, CELL[0] - 1)) and y in (5, 8):
                continue
            v = _bright(c, 0.75) if y == 5 else (_bright(c, 1.35) if y == 8 else c)
            P[x, y] = v + (255,)
    return im


# ─── Barra de verbs, en fotogrames (com verbs.png) ─────────────────────────

def _bar_frame(draw):
    """Un fotograma de pantalla (640×360) amb el que `draw(cv)` pinta a la barra (coordenades de la barra)."""
    cv = Canvas(W, vg.BH, transparent=True)
    draw(cv)
    out = Image.new('RGBA', (W, H), (0, 0, 0, 0))
    out.paste(cv.img, (0, vg.Y0))
    return out


def build_verbs():
    bg = Image.new('RGBA', (W, H), (0, 0, 0, 0))
    bg.paste(vg.background().img, (0, vg.Y0))
    ref = Image.new('RGBA', (W, H), (0, 0, 0, 0))     # fotograma 0: referència (la barra sencera, amb textos)
    ref.paste(vg.verb_bar({'inv': ()}), (0, vg.Y0))
    frames = [(ref, None), (bg, 'VerbsBG'),
              (_bar_frame(lambda cv: vg.arrow_layer(cv, 'up', False)), 'UpBtn'),
              (_bar_frame(lambda cv: vg.arrow_layer(cv, 'down', False)), 'DownBtn'),
              (_bar_frame(vg.menu_layer), 'MenuBtn'),
              (_bar_frame(lambda cv: vg.arrow_layer(cv, 'up', True)), 'UpBtn-hover'),
              (_bar_frame(lambda cv: vg.arrow_layer(cv, 'down', True)), 'DownBtn-hover'),
              (_bar_frame(lambda cv: vg.canvia_layer(cv, False)), 'CanviaBtn'),
              (_bar_frame(lambda cv: vg.canvia_layer(cv, True)), 'CanviaBtn-hover')]
    write_sheet(OUT / 'verbs', 'verbs', [(im, t, (0, 0), (W, H)) for im, t in frames], cols=3)

    gui = scaled_gui('verbs')
    y0 = vg.Y0
    verb_ids = {'give': 'GiveBtn', 'pickUp': 'PickUpBtn', 'use': 'UseBtn', 'open': 'OpenBtn', 'talkTo': 'TalkToBtn',
                'push': 'PushBtn', 'close': 'CloseBtn', 'look': 'LookAtBtn', 'pull': 'PullBtn'}
    pos = {}
    for row, vy in zip(vg.VERB_IDS, vg.VERB_ROWS):
        for (vx, vw), vid in zip(vg.VERB_COLS, row):
            pos[verb_ids[vid]] = (vx, y0 + vy, vw, vg.VERB_H)
    for which, cid in (('up', 'upBtn'), ('down', 'downBtn')):
        ax, ay = vg.ARROWS[which]
        pos[cid] = (ax, y0 + ay, 13, 36)
    cx, cy, cw, ch = vg.CANVIA
    pos['CanviaBtn'] = (cx, y0 + cy, cw, ch)
    mx, my, ms = vg.MENU
    pos['MenuBtn'] = (mx, y0 + my, ms, ms)
    for c in gui['controls']:
        if c['id'] in pos:
            c['x'], c['y'], c['width'], c['height'] = pos[c['id']]
        if c['id'] == 'inventoryPanel':
            c.update({'x': vg.INV_X, 'y': y0 + vg.INV_Y, 'slotWidth': vg.SLOT_W, 'slotHeight': vg.SLOT_H,
                      'spacingX': vg.GAP, 'spacingY': vg.GAP})
        if c['id'] == 'verbLineText':
            c['x'], c['y'] = W // 2, y0 - 2             # el text, centrat a la franja de 16 (a 480: 192)
    save_gui('verbs', gui)


# ─── Diàleg ─────────────────────────────────────────────────────────────────

DLG_TRIM = 260                                    # el fil de llautó (195 a 480); la planxa comença a 263
DLG_ARROWS = {'up': (4, 273), 'down': (4, 320)}   # canals de 12×33 i botons de 13×33 (a 480: 9×25, 10×25)
DLG_ORIGIN = {'up': (-1, 266), 'down': (-1, 295)}  # on el motor posa el (0, 0) del fotograma retallat
DLG_CROP = (29, 59)                               # 22×44 a 480
DLG_TOP = 233                                     # on comença el fotograma del fons (175 a 480)


def dialog_bg():
    cv = Canvas(W, H, transparent=True)
    body(cv, 0, DLG_TRIM + 3, W - 1, H - 1, top=3.3)
    brass_trim(cv, 0, W - 1, DLG_TRIM)
    for x in range(W):
        dark(cv, x, DLG_TRIM + 3, 0.45)
        dark(cv, x, DLG_TRIM + 4, 0.15)
        cv.put(x, H - 1, SLATE, 1.4, lit=0)
    for y in range(DLG_TRIM + 3, H - 1):
        cv.put(0, y, SLATE, 4.6, lit=0)
        cv.put(W - 1, y, SLATE, 1.6, lit=0)
    well(cv, 20, 267, 632, 355, face=1.0)            # el panell de les opcions
    for ax, ay in DLG_ARROWS.values():
        well(cv, ax, ay, ax + 11, ay + 32, face=1.4, mesh=False)
    rivet(cv, 7, 265)
    rivet(cv, 7, 310)
    return cv.img


def dialog_arrow(which):
    cv = Canvas(W, H, transparent=True)
    ax, ay = DLG_ARROWS[which]
    arrow(cv, ax + 6, ay + 16, which == 'up', False, length=17, head=5, stem=1)
    ox, oy = DLG_ORIGIN[which]
    full = Image.new('RGBA', (W + 2, H), (0, 0, 0, 0))
    full.paste(cv.img, (1, 0))
    return full.crop((ox + 1, oy, ox + 1 + DLG_CROP[0], oy + DLG_CROP[1]))


def dialog_bullet():
    """L'indicador de cada opció: el botó de llautó rodó (7×7; a 480, 5×5), amb el reflex i l'ombra."""
    cv = Canvas(59, 29, transparent=True)
    rows = ['..abb..', '.abbcc.', 'abbccdd', 'bbccdde', 'bccddee', '.cddee.', '..dee..']
    lv = {'a': 6.8, 'b': 5.8, 'c': 4.8, 'd': 3.6, 'e': 2.4}
    x0, y0 = 25, 10
    for j, r in enumerate(rows):
        for i, ch in enumerate(r):
            if ch in lv:
                cv.put(x0 + i, y0 + j, BRASS, lv[ch], lit=0)
    cv.put(x0 + 2, y0 + 1, BRASS, 7.4, lit=0)                    # el punt de llum
    shadow = [(x0 + 7, y0 + 2), (x0 + 7, y0 + 3), (x0 + 7, y0 + 4), (x0 + 6, y0 + 5), (x0 + 5, y0 + 6), (x0 + 4, y0 + 7),
              (x0 + 3, y0 + 7), (x0 + 2, y0 + 7), (x0 + 6, y0 + 6), (x0 + 5, y0 + 7), (x0 + 7, y0 + 5)]
    for x, y in shadow:
        cv.flat(x, y, (6, 8, 12))
    return cv.img


def build_dialog():
    full = dialog_bg()
    ref = full.copy()                                         # fotograma 0: referència (el fons, amb les fletxes)
    for which in ('up', 'down'):
        ref.alpha_composite(dialog_arrow(which), (DLG_ORIGIN[which][0] + 1, DLG_ORIGIN[which][1]))
    bg = full.crop((0, DLG_TOP, W, H))
    items = [(ref, None, (0, 0), (W, H)),
             (bg, 'VerbsBG', (0, DLG_TOP), (W, H)),
             (dialog_arrow('up'), 'UpBtn', (0, 261), (W, H)),
             (dialog_arrow('down'), 'DownBtn', (0, 291), (W, H)),
             (dialog_bullet(), 'Bullet', (0, 261), (W, H))]
    write_sheet(OUT / 'dialog', 'dialog', items)
    gui = scaled_gui('dialog')
    for c in gui['controls']:
        for which, cid in (('up', 'scrollUp'), ('down', 'scrollDown')):
            if c['id'] == cid:
                x, y = DLG_ARROWS[which]
                ox, oy = DLG_ORIGIN[which]
                c.update(x=x, y=y, width=13, height=33, backgroundOffsetX=ox - x, backgroundOffsetY=oy - y)
        if c['id'] == 'Option-Grid':
            c.update(x=21, y=269, width=607, height=25, colWidths=[19, 588])
        if c['id'] == 'Dialog-Option':
            c.update(width=588, height=25)
    save_gui('dialog', gui)


# ─── Menús ──────────────────────────────────────────────────────────────────

MENU_GUIS = ('display-text', 'game-menu', 'save-menu', 'load-menu', 'settings-menu')


def build_menus():
    ns = (nine_slice(), '9-slice-BG', (0, 0), (NS_W, NS_H))
    for name in MENU_GUIS:
        gui = scaled_gui(name)
        for c in gui['controls']:
            tag = str(c.get('backgroundTag', ''))
            if c.get('type') == 'button' and tag.startswith('btn-'):
                c['width'], c['height'] = BTN[tag.split('-')[1]]
            if c.get('type') == 'checkbox':
                c['width'] = c['height'] = 21
            if c.get('type') == 'slider':
                c['height'] = 20
        if name == 'settings-menu':
            pad = Image.new('RGBA', CELL, (0, 0, 0, 0))
            pad.paste(ns[0], (0, 0))
            items = [(pad, '9-slice-BG', (0, 0), CELL)]
            for st in ('checkbox', 'checkbox-hover', 'checkbox-checked', 'checkbox-checked-hover', 'checkbox-disabled',
                       'checkbox-checked-disabled'):
                items.append((checkbox(st), st, (0, 0), CELL))
            items += [(slider_handle(''), 'slider-handle', (0, 0), CELL),
                      (slider_handle('hover'), 'slider-handle-hover', (0, 0), CELL),
                      (slider_track(False), 'slider-track', (0, 0), CELL),
                      (slider_handle('disabled'), 'slider-handle-disabled', (0, 0), CELL),
                      (slider_track(True), 'slider-track-disabled', (0, 0), CELL)]
            write_sheet(OUT / name, name, items, cols=4, slices=nine_slices())
        elif name == 'game-menu':
            items = [ns]
            for mida, (w, h) in BTN.items():
                for estat in menu_gui.ESTATS:
                    tag = f'btn-{mida}' if estat == 'normal' else f'btn-{mida}-{estat}'
                    items.append((menu_button(w, h, estat), tag, (0, 0), (w, h)))
            sep = separador()
            items.append((sep, 'separador', (0, 0), sep.size))
            write_sheet(OUT / name, name, items, cols=1, slices=nine_slices())
        else:
            write_sheet(OUT / name, name, [ns], slices=nine_slices())
        save_gui(name, gui)


# ─── Portada ────────────────────────────────────────────────────────────────

def cover_button(x0, y0, w, h, hover):
    """Els botons de la portada (com draw_placeholders.draw_cover_gui, amb els mateixos colors, a 640): placa blava
    mig transparent amb la vora d'1 px, els cantons retallats, bisell (llum a dalt, ombra a baix) i un rebló de
    llautó a cada banda; en hover, més clara i amb la vora verda."""
    img = Image.new('RGBA', (W, H), (0, 0, 0, 0))
    d = ImageDraw.Draw(img)
    fill, vora = ((40, 96, 140), (150, 230, 190)) if hover else ((26, 70, 107), (60, 110, 150))
    x1, y1 = x0 + w - 1, y0 + h - 1
    d.rectangle([x0 + 1, y0 + 1, x1 - 1, y1 - 1], fill=fill + (235,))
    d.line([(x0 + 2, y0), (x1 - 2, y0)], fill=vora + (255,))
    d.line([(x0 + 2, y1), (x1 - 2, y1)], fill=vora + (255,))
    d.line([(x0, y0 + 2), (x0, y1 - 2)], fill=vora + (255,))
    d.line([(x1, y0 + 2), (x1, y1 - 2)], fill=vora + (255,))
    for cx, cy in ((x0 + 1, y0 + 1), (x1 - 1, y0 + 1), (x0 + 1, y1 - 1), (x1 - 1, y1 - 1)):
        img.putpixel((cx, cy), vora + (255,))
    llum, ombra = _bright(fill, 1.3), _bright(fill, 0.7)
    d.line([(x0 + 2, y0 + 1), (x1 - 2, y0 + 1)], fill=llum + (240,))
    d.line([(x0 + 1, y0 + 2), (x0 + 1, y1 - 2)], fill=llum + (240,))
    d.line([(x0 + 2, y1 - 1), (x1 - 2, y1 - 1)], fill=ombra + (240,))
    d.line([(x1 - 1, y0 + 2), (x1 - 1, y1 - 2)], fill=ombra + (240,))
    cy = y0 + h // 2 - 1
    for rx in (x0 + 5, x1 - 7):                                   # reblons de llautó, 3×3
        for dx, dy, c in ((0, 0, BRASS[6]), (1, 0, BRASS[5]), (0, 1, BRASS[5]), (1, 1, BRASS[4]), (2, 1, BRASS[2]),
                          (1, 2, BRASS[2]), (2, 2, BRASS[1])):
            img.putpixel((rx + dx, cy + dy), c + (255,))
    return img


def build_portada():
    gui = scaled_gui('portada')
    items = []
    for c in gui['controls']:
        if c.get('type') != 'button':
            continue
        c['x'], c['width'], c['height'] = (W - 200) // 2, 200, 29
        for hover in (False, True):
            tag = c['id'] + ('-hover' if hover else '')
            items.append((cover_button(c['x'], c['y'], c['width'], c['height'], hover), tag, (0, 0), (W, H)))
    write_sheet(OUT / 'portada', 'portada', items, cols=6)
    save_gui('portada', gui)


# ─── Punter ─────────────────────────────────────────────────────────────────

def cursor_frame(gap, arm=5):
    """Creu blanca d'1 px amb ombra fosca a baix a la dreta, centrada a (21, 21) d'un fotograma de 43×43
    (la de 480: 32×32, centrada a (15, 15), braços de 4)."""
    img = Image.new('RGBA', (43, 43), (0, 0, 0, 0))
    P = img.load()
    c = 21
    white, shade = (250, 255, 255, 255), (5, 9, 20, 255)
    pts = []
    for i in range(gap, gap + arm):
        pts += [(c + i, c), (c - i, c), (c, c + i), (c, c - i)]
    for x, y in pts:
        if not P[x + 1, y + 1][3]:
            P[x + 1, y + 1] = shade
    for x, y in pts:
        P[x, y] = white
    return img


def build_cursor():
    """Els mateixos fotogrames i etiquetes que el punter del joc (Idle; Active de 4 fotogrames que van de la creu
    oberta a la tancada), un terç més grans: forats de 3, 4 i 1 px (a 480: 2, 3 i 1) i braços de 5 (a 480: 4)."""
    f0, f2, f4 = cursor_frame(3), cursor_frame(4), cursor_frame(1)
    d = OUT / 'cursor'
    d.mkdir(parents=True, exist_ok=True)
    sheet = Image.new('RGBA', (86, 86), (0, 0, 0, 0))
    sheet.paste(f0, (0, 0))
    sheet.paste(f2, (43, 0))
    sheet.paste(f4, (0, 43))
    src = json.loads((GAME / 'assets/images/cursor/cursor.json').read_text())
    for f in src['frames'].values():
        for k in ('x', 'y'):
            f['frame'][k] = f['frame'][k] // 32 * 43
        for k in ('w', 'h'):
            f['frame'][k] = 43
        f['spriteSourceSize'] = {'x': 0, 'y': 0, 'w': 43, 'h': 43}
        f['sourceSize'] = {'w': 43, 'h': 43}
    src['meta']['size'] = {'w': 86, 'h': 86}
    src['meta']['image'] = 'cursor.png'
    src['meta']['version'] = 'hd640/gui_rest.py'
    sheet.save(d / 'cursor.png')
    (d / 'cursor.json').write_text(json.dumps(src, indent=1) + '\n')


# ─── .gui.json: ×4/3 ────────────────────────────────────────────────────────

SCALE_KEYS = {'x', 'y', 'width', 'height', 'wordWrapWidth', 'rowPadding', 'textOffsetX', 'textOffsetY', 'slotWidth',
              'slotHeight', 'spacingX', 'spacingY', 'offsetX', 'offsetY', 'backgroundOffsetX', 'backgroundOffsetY'}
SCALE_LISTS = {'colWidths', 'rowHeights'}


def _scale(o):
    if isinstance(o, dict):
        for k, v in o.items():
            if k in SCALE_KEYS and isinstance(v, (int, float)) and not isinstance(v, bool):
                o[k] = s(v)
            elif k in SCALE_LISTS and isinstance(v, list):
                o[k] = [s(x) for x in v]
            else:
                _scale(v)
    elif isinstance(o, list):
        for v in o:
            _scale(v)


def scaled_gui(name):
    gui = copy.deepcopy(json.loads((GAME / 'guis' / name / f'{name}.gui.json').read_text()))
    _scale(gui)
    return gui


def save_gui(name, gui):
    d = OUT / name
    d.mkdir(parents=True, exist_ok=True)
    (d / f'{name}.gui.json').write_text(json.dumps(gui, indent=2, ensure_ascii=False) + '\n')


def build_jsons_only():
    save_gui('speaking-text', scaled_gui('speaking-text'))
    cfg = {'resolution': {'width': W, 'height': H},
           'dialog': {'choiceOptionsViewportHeightPx': s(63)},
           '_nota': 'Només el que canvia respecte de game-config.json del joc (hd640/gui_rest.py).'}
    (OUT / 'game-config.640.json').write_text(json.dumps(cfg, indent=2, ensure_ascii=False) + '\n')


# ─── Comprovació: els mateixos controls, ids i etiquetes que el joc ────────

def check():
    """Compara cada .gui.json de 640 amb el del joc: mateixos controls (id i tipus, en el mateix ordre), mateixes
    claus i textos, i totes les etiquetes que fan servir existeixen al full de 640. Retorna la llista de problemes."""
    probs = []
    for gp in sorted((GAME / 'guis').glob('*/*.gui.json')):
        name = gp.parent.name
        if name in SKIP:
            continue
        a = json.loads(gp.read_text())
        bp = OUT / name / f'{name}.gui.json'
        if not bp.exists():
            probs.append(f'{name}: no hi és')
            continue
        b = json.loads(bp.read_text())
        if {k: v for k, v in a.items() if k != 'controls'} != {k: v for k, v in b.items() if k != 'controls'}:
            probs.append(f'{name}: capçalera diferent')
        ia = [(c['id'], c['type']) for c in a['controls']]
        ib = [(c['id'], c['type']) for c in b['controls']]
        if ia != ib:
            probs.append(f'{name}: controls {ia} != {ib}')
        for ca, cb in zip(a['controls'], b['controls']):
            if set(ca) ^ set(cb):
                probs.append(f'{name}.{ca["id"]}: claus {set(ca) ^ set(cb)}')
            for k in ('text', 'font', 'fontSize', 'tag', 'backgroundTag', 'states', 'placeholder', 'align', 'zIndex'):
                if ca.get(k) != cb.get(k):
                    probs.append(f'{name}.{ca["id"]}: {k} {ca.get(k)!r} -> {cb.get(k)!r}')
        js = OUT / name / f'{name}.json'
        if js.exists():
            have = {t['name'] for t in json.loads(js.read_text())['meta']['frameTags']}
            old = {t['name'] for t in json.loads((GAME / 'assets/images/guis' / name / f'{name}.json').read_text())['meta']['frameTags']}
            for c in b['controls']:
                used = [c.get('tag'), c.get('backgroundTag'), c.get('trackTag'), c.get('handleTag')]
                for v in (c.get('states') or {}).values():
                    used += list(v.values()) if isinstance(v, dict) else [v]
                for t in used:
                    if t and t not in have:
                        probs.append(f'{name}.{c["id"]}: etiqueta {t} no és al full')
            if old - have:
                probs.append(f'{name}: etiquetes perdudes {old - have}')
    return probs


# ─── Comparatives: una GUI muntada amb textos (simulació senzilla del motor) ─

def load_sheet(png, js):
    sheet = Image.open(png).convert('RGBA')
    d = json.loads(Path(js).read_text())
    frames = list(d['frames'].values())
    by_tag = {}
    for t in d['meta']['frameTags']:
        f = frames[t['from']]
        fr = f['frame']
        by_tag[t['name']] = (sheet.crop((fr['x'], fr['y'], fr['x'] + fr['w'], fr['y'] + fr['h'])),
                             (f['spriteSourceSize']['x'], f['spriteSourceSize']['y']))
    return by_tag, d['meta'].get('slices', [])


def nine(img, slices, w, h):
    b = {sl['name']: sl['keys'][0]['bounds'] for sl in slices}
    out = Image.new('RGBA', (w, h), (0, 0, 0, 0))
    tl, br = b['TopLeft'], b['BottomRight']
    L, T, R, B = tl['w'], tl['h'], br['w'], br['h']
    cols = [(b['TopLeft']['x'], L, 0, L), (b['TopMid']['x'], b['TopMid']['w'], L, w - L - R), (br['x'], R, w - R, R)]
    rows = [(b['TopLeft']['y'], T, 0, T), (b['MidLeft']['y'], b['MidLeft']['h'], T, h - T - B), (br['y'], B, h - B, B)]
    for sx, sw, dx, dw in cols:
        for sy, sh, dy, dh in rows:
            if dw > 0 and dh > 0:
                out.paste(nearest(img.crop((sx, sy, sx + sw, sy + sh)), (dw, dh)), (dx, dy))
    return out


class Fonts:
    def __init__(self, res):
        if res == 640:
            self.reg, self.bold, self.space, self.lh = font640(False), font640(True), 4, LH640
        else:
            sys.path.insert(0, str(TOOLS.parents[2] / 'tools/font'))
            import ferro_font as ff
            self.reg, self.bold, self.space, self.lh = ff.all_glyphs(False), ff.all_glyphs(True), ff.SPACE_ADVANCE, 12

    def g(self, font):
        return self.bold if 'negreta' in (font or '') else self.reg

    def _ok(self, font, s_):
        g = self.g(font)
        return ''.join(c for c in s_ if c == ' ' or c in g)

    def width(self, font, s_):
        return tw640(self.g(font), self._ok(font, s_), self.space)

    def draw(self, img, font, s_, x, y, color, outline=TEXT_OUTLINE):
        dt640(img, self.g(font), self._ok(font, s_), x, y, color, outline=outline, space=self.space)

    def wrap(self, font, s_, width):
        lines, cur = [], ''
        for w_ in s_.split(' '):
            t = (cur + ' ' + w_).strip()
            if cur and self.width(font, t) > width:
                lines.append(cur)
                cur = w_
            else:
                cur = t
        return lines + [cur]


SAMPLE = {
    'dialog': ['On és el formulari 27-B?', 'Qui ha segellat això per triplicat, capatàs?',
               '«Intel·ligència» no és la paraula. Adéu.'],
    'display-text': 'La biga de Ferro-9 no s\'ha doblegat. Ni amb la pressió de la premsa.',
    'speaking-text': 'Ja hi som. Ara només cal que el capatàs no s\'adoni de res.',
    'list': ['Torn de nit — la fàbrica', 'Abans de la reeducació', 'Ç·l·l: proves «d\'accents»'],
}
COLORS = {'iri': '#f0a050', 'vet': '#60d8d8'}


def render_gui(name, res, backdrop, hover_ids=('load', 'save-btn', 'load-btn', 'comenca')):
    """La GUI `name` a la resolució `res` (480: la del joc; 640: la de hd640/guis), sobre `backdrop`."""
    if res == 640:
        gdir = OUT / name
        gpath = gdir / f'{name}.gui.json'
    else:
        gdir = GAME / 'assets/images/guis' / name
        gpath = GAME / 'guis' / name / f'{name}.gui.json'
    gui = json.loads(gpath.read_text())
    tags, slices = ({}, [])
    if (gdir / f'{name}.png').exists():
        tags, slices = load_sheet(gdir / f'{name}.png', gdir / f'{name}.json')
    ns_img = tags.get('9-slice-BG', (None,))[0]
    F = Fonts(res)
    img = backdrop.copy()
    if gui.get('modal') or name in ('display-text',):
        img.alpha_composite(Image.new('RGBA', img.size, (0, 0, 0, 90)))
    grids = {c['id']: c for c in gui['controls'] if c.get('type') == 'grid'}

    def place(c, w, h):
        gp = c.get('gridPlacement')
        if not gp:
            if c.get('backgroundAnchor') == 'center':
                return c['x'] - w // 2, c['y'] - h // 2
            return c['x'], c['y']
        g = grids[gp['gridControlId']]
        rows, cols = g.get('rows', 1), g.get('columns', 1)
        cws = g.get('colWidths') or [g.get('width', 0) // cols] * cols
        rh = g['height'] / rows
        cx = g['x'] + sum(cws[:gp.get('col', 0)])
        cy = g['y'] + rh * gp.get('row', 0)
        cw = cws[gp.get('col', 0)]
        al = gp.get('align', 'top-left')
        x = cx + (cw - w) / 2 if al in ('center', 'top-center') else (cx + cw - w if 'right' in al else cx)
        y = cy + (rh - h) / 2 if al.startswith('center') else cy
        return round(x + gp.get('offsetX', 0)), round(y + gp.get('offsetY', 0))

    def paste_tag(tag, x, y):
        if tag in tags:
            img.alpha_composite(tags[tag][0], (int(x), int(y)))

    controls = sorted(gui['controls'], key=lambda c: c.get('zIndex', 60 if c.get('id') == 'Dialog-Option' else 0))
    for c in controls:
        t = c.get('type')
        if c.get('visible') is False and t != 'image':
            continue
        if t == 'image':
            if c.get('tag') == 'Bullet':
                continue
            if c.get('tag') in tags:
                im, src = tags[c['tag']]
                if c.get('backgroundAnchor') == 'screen' or (c['x'], c['y']) == (0, 0):
                    img.alpha_composite(im, src)
                else:
                    img.alpha_composite(im, (c['x'], c['y']))
        elif t == 'nineSliceImage' and ns_img is not None:
            x, y = place(c, c['width'], c['height'])
            img.alpha_composite(nine(ns_img, slices, c['width'], c['height']), (x, y))
        elif t == 'button':
            if name == 'dialog' and c['id'] == 'Dialog-Option':
                g = grids['Option-Grid']
                for i, s_ in enumerate(SAMPLE['dialog']):
                    y = g['y'] + i * c['height']
                    col = '#f2c66d' if i == 1 else c.get('textColor', '#ffffff')
                    if 'Bullet' in tags:
                        b, _ = tags['Bullet']
                        cx0 = g['x'] + g['colWidths'][0] / 2
                        img.alpha_composite(b, (round(cx0 - b.width / 2), round(y + c['height'] / 2 - b.height / 2)))
                    F.draw(img, c['font'], s_, g['x'] + g['colWidths'][0], y + (c['height'] - F.lh) // 2, col)
                continue
            x, y = place(c, c['width'], c['height'])
            hover = c['id'] in hover_ids
            if c.get('backgroundTag'):
                tag = c['backgroundTag']
                if hover and (c.get('states') or {}).get('hover') in tags:
                    tag = c['states']['hover']
                if c.get('backgroundAnchor') == 'screen':
                    if tag in tags:
                        im, src = tags[tag]
                        img.alpha_composite(im, src)
                else:
                    paste_tag(tag, x + c.get('backgroundOffsetX', 0), y + c.get('backgroundOffsetY', 0))
            elif c.get('backgroundColor'):
                bc = (c.get('backgroundColorStates') or {}).get('hover') if hover else None
                ImageDraw.Draw(img).rectangle([x, y, x + c['width'] - 1, y + c['height'] - 1],
                                              fill=bc or c['backgroundColor'])
            if c.get('text') and c.get('font') and c.get('text') != 'Button':
                tw = F.width(c['font'], c['text'])
                col = (c.get('textColorStates') or {}).get('hover', c.get('textColor')) if hover else c.get('textColor')
                oc = (c.get('textOutline') or {}).get('color', TEXT_OUTLINE)
                F.draw(img, c['font'], c['text'], x + (c['width'] - tw) // 2 + c.get('textOffsetX', 0),
                       y + (c['height'] - F.lh) // 2 + c.get('textOffsetY', 0) + (1 if res == 640 else 0), col or '#fff', oc)
        elif t == 'text':
            s_ = c.get('text') or ''
            if name in ('display-text', 'speaking-text'):
                s_ = SAMPLE[name]
            if c['id'] == 'version':
                s_ = 'v1.4.2'
            if not s_:
                continue
            lines = F.wrap(c['font'], s_, c['wordWrapWidth']) if c.get('wordWrapWidth') else [s_]
            col = c.get('color') or '#ffffff'
            if name == 'speaking-text':
                col = COLORS['vet']
            for i, ln in enumerate(lines):
                w_ = F.width(c['font'], ln)
                if c.get('gridPlacement'):
                    x, y = place(c, w_, F.lh)
                else:
                    x, y = c['x'], c['y']
                    al = c.get('align', 'left')
                    x = x - w_ // 2 if al == 'center' else (x - w_ if al == 'right' else x)
                F.draw(img, c['font'], ln, x, y + i * F.lh, col, (c.get('textOutline') or {}).get('color', TEXT_OUTLINE))
        elif t == 'checkbox':
            x, y = place(c, c['width'], c['height'])
            paste_tag('checkbox-checked' if c.get('checked') else 'checkbox', x, y)
        elif t == 'slider':
            x, y = place(c, c['width'], c['height'])
            if 'slider-track' in tags:
                tr = tags['slider-track'][0]
                img.alpha_composite(nearest(tr, (c['width'], tr.height)), (x, y))
                frac = (c.get('defaultValue', 1) - c.get('min', 0)) / max(1e-6, c.get('max', 1) - c.get('min', 0))
                hw = 4 if res == 640 else 3
                paste_tag('slider-handle', x + round(frac * (c['width'] - hw)), y)
        elif t == 'listBox':
            x, y = place(c, c['width'], c['height'])
            rh = F.lh + 2 * c.get('rowPadding', 0)
            d = ImageDraw.Draw(img)
            for i in range(c.get('rowCount', c['height'] // rh)):
                bgc = c.get('selectedBackgroundColor') if i == 1 else c.get('normalBackgroundColor', '#222222')
                d.rectangle([x, y + i * rh, x + c['width'] - 1, y + (i + 1) * rh - 2], fill=bgc)
                if i < len(SAMPLE['list']):
                    F.draw(img, c['font'], SAMPLE['list'][i], x + 3, y + i * rh + c.get('rowPadding', 0),
                           c.get('selectedTextColor', '#fff') if i == 1 else c.get('textColor', '#fff'))
        elif t == 'textInput':
            x, y = place(c, c['width'], c['height'])
            d = ImageDraw.Draw(img)
            d.rectangle([x, y, x + c['width'] - 1, y + c['height'] - 1], fill=c.get('backgroundColor', '#222222'),
                        outline=c.get('focusedOutlineColor', '#a0a0a0'))
            F.draw(img, c['font'], 'La meva partida', x + 3, y + (c['height'] - F.lh) // 2, c.get('color', '#fff'))
    return img


def backdrops():
    """Fons de mostra (480 i 640): una nau de fàbrica de colors de sala (maó, ferro i finestrals), sense barra."""
    out = {}
    for res, (w, h) in ((480, (480, 270)), (640, (640, 360))):
        img = Image.new('RGBA', (w, h), (0, 0, 0, 255))
        d = ImageDraw.Draw(img)
        k = w / 480
        for y in range(h):
            t = y / h
            d.line([(0, y), (w, y)], fill=(int(70 + 30 * t), int(42 + 18 * t), int(32 + 10 * t), 255))
        for i, x0 in enumerate((30, 150, 270, 390)):
            d.rectangle([x0 * k, 30 * k, (x0 + 60) * k, 120 * k], fill=(150, 170, 180, 255))
            for gx in range(1, 3):
                d.line([((x0 + gx * 20) * k, 30 * k), ((x0 + gx * 20) * k, 120 * k)], fill=(40, 34, 36, 255), width=max(1, int(2 * k)))
            d.line([(x0 * k, 75 * k), ((x0 + 60) * k, 75 * k)], fill=(40, 34, 36, 255), width=max(1, int(2 * k)))
        d.rectangle([0, 150 * k, w, 195 * k], fill=(54, 46, 44, 255))
        for x in range(0, w, int(40 * k)):
            d.rectangle([x, 20 * k, x + 8 * k, 160 * k], fill=(60, 64, 72, 255))
        out[res] = img
    return out


def with_bar(res, b, hover='look'):
    b = b.copy()
    if res == 640:
        b.alpha_composite(vg.verb_bar({'hover': hover, 'line': 'Mira el segell'}), (0, vg.Y0))
    else:
        b.alpha_composite(vg.bar480(line='Mira el segell', hover=hover), (0, 195))
    return b


def full_screens(out_dir, back):
    """Pantalla completa de mostra: la sala, la barra amb l'inventari, i a sobre el text de la Vet i el menú del
    joc; a part, la mateixa sala amb el diàleg obert."""
    shots = {}
    for res in (480, 640):
        b = with_bar(res, back[res])
        a = render_gui('speaking-text', res, b)
        a = render_gui('game-menu', res, a)
        shots[(res, 'menu')] = a
        shots[(res, 'joc')] = render_gui('speaking-text', res, b)
        shots[(res, 'dialog')] = render_gui('dialog', res, back[res])
    for kind in ('joc', 'menu', 'dialog'):
        a = nearest(shots[(480, kind)], (1920, 1080))
        b = nearest(shots[(640, kind)], (1920, 1080))
        pair = Image.new('RGB', (1920 * 2 + 40, 1080 + 40), (30, 30, 30))
        pair.paste(a, (0, 40))
        pair.paste(b, (1960, 40))
        d = ImageDraw.Draw(pair)
        d.text((8, 12), f'pantalla ({kind}): 480x270 (x4)', fill=(255, 255, 255))
        d.text((1968, 12), f'pantalla ({kind}): 640x360 (x3)', fill=(255, 255, 255))
        pair.save(out_dir / f'pantalla_{kind}.png')
        nearest(shots[(640, kind)], (1920, 1080)).save(out_dir / f'pantalla_{kind}_640.png')


def contact(out_dir):
    out_dir = Path(out_dir)
    out_dir.mkdir(parents=True, exist_ok=True)
    back = backdrops()
    names = ('verbs', 'dialog', 'display-text', 'speaking-text', 'game-menu', 'save-menu', 'load-menu', 'settings-menu',
             'portada')
    for n in names:
        if n == 'verbs':
            a, b = with_bar(480, back[480]), with_bar(640, back[640])
        else:
            a, b = render_gui(n, 480, back[480]), render_gui(n, 640, back[640])
        a, b = nearest(a, (1920, 1080)), nearest(b, (1920, 1080))
        pair = Image.new('RGB', (1920 * 2 + 40, 1080 + 40), (30, 30, 30))
        pair.paste(a, (0, 40))
        pair.paste(b, (1960, 40))
        d = ImageDraw.Draw(pair)
        d.text((8, 12), f'{n}: ACTUAL 480x270 (x4)', fill=(255, 255, 255))
        d.text((1968, 12), f'{n}: 640x360 (x3)', fill=(255, 255, 255))
        pair.save(out_dir / f'gui_{n}_640.png')
    full_screens(out_dir, back)
    # els fulls, de prop: botons del menú, caselles i lliscadors, 9-slice, cursor (480 ×8 a dalt, 640 ×6 a baix)
    sheets = []
    for name in ('game-menu', 'settings-menu', 'dialog'):
        a = Image.open(GAME / f'assets/images/guis/{name}/{name}.png').convert('RGBA')
        b = Image.open(OUT / f'{name}/{name}.png').convert('RGBA')
        if name == 'dialog':
            a, b = a.crop((480, 109, 568, 153)), b.crop((640, 0, b.width, 59)) if b.width > 640 else b
        sheets.append((name, a, b))
    for name, a, b in sheets:
        A = nearest(a, (a.width * 8, a.height * 8))
        B = nearest(b, (b.width * 6, b.height * 6))
        o = Image.new('RGB', (max(A.width, B.width) + 20, A.height + B.height + 60), (120, 124, 130))
        o.paste(A, (10, 20), A)
        o.paste(B, (10, A.height + 50), B)
        o.save(out_dir / f'full_{name}.png')
    cur = Image.new('RGB', (1000, 300), (120, 130, 140))
    c480 = nearest(Image.open(GAME / 'assets/images/cursor/cursor.png').convert('RGBA'), (256, 256))
    c640 = nearest(Image.open(OUT / 'cursor/cursor.png').convert('RGBA'), (258, 258))
    cur.paste(c480, (40, 20), c480)
    cur.paste(c640, (400, 20), c640)
    cur.save(out_dir / 'gui_cursor_640.png')


def main():
    build_verbs()
    build_dialog()
    build_menus()
    build_portada()
    build_cursor()
    build_jsons_only()
    print(f'✔ GUI de 640 a {OUT}')
    _, prov = vg.character_frame('iri')
    if prov:
        print('  ⚠ «Canvia»: encara no hi ha hd640/characters/iri i vet; cares de placeholder-art (480) ×4/3')
    probs = check()
    for p in probs:
        print('  ⚠', p)
    if not probs:
        print('✔ mateixos controls, ids, claus, textos i etiquetes que les GUI del joc')
    if len(sys.argv) > 1:
        contact(sys.argv[1])
        print(f'✔ comparatives a {sys.argv[1]}')


if __name__ == '__main__':
    main()
