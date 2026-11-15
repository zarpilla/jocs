#!/usr/bin/env python3
"""
La interfície de Suma Zero a 640×360, menys el dibuix de la barra de verbs (que és a hd640/gui.py).

Redibuixa, amb el mateix estil que la barra de 640 (la consola d'hacker: plàstic blau marí, tecles fosques,
pantalletes amb cantoneres de visor, llum verd blavós i l'accent magenta), els fulls de totes les GUI del
joc i en fa els .gui.json a 640, sense tocar el joc:

  hd640/guis/<gui>/<gui>.png + .json      el full (mateixos noms d'etiqueta i 9-slice que el del joc)
  hd640/guis/<gui>/<gui>.gui.json         la GUI a 640: mateixos controls, ids, etiquetes i comportament;
                                          posicions i mides ×4/3, ajustades a mà on cal; botons `key-WxH`
                                          amb la mida nova; mateixes fonts (les de hd640/font.py, que
                                          s'exporten amb els mateixos noms), fontSize 8
  hd640/guis/cursor/cursor.png + .json    el punter, un terç més gran (43×43)
  hd640/guis/game-config.640.json         el que canvia a game-config.json (resolució, llista d'opcions)

GUI: verbs (la barra en fotogrames, com verbs.png, amb el botó «Canvia»), dialog, display-text, game-menu,
save-menu, load-menu, settings-menu, portada, speaking-text i historial (aquestes dues no tenen full).

    python3 hd640/gui_rest.py [carpeta de comparatives]

Llegeix els .gui.json actuals del joc (suma-zero/src/game/guis) per escalar-los. Amb una carpeta, també hi
munta les comparatives (cada GUI a 480 ×4 i a 640 ×3, amb textos) i una pantalla completa de mostra.
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
from hd.pix import Canvas, mix  # noqa: E402
from hd.gui import (SLATE, TEAL, MAG, TEXT, TEXT_HOVER, TEXT_OUTLINE, VERB_LINE, OPTION, OPTION_HOVER,  # noqa: E402
                    TITLE, LABEL, dark)
from hd640.gui import body, key, well, led, light_line, arrow  # noqa: E402
from hd640.font import font640, text_width as tw640, draw_text as dt640, LINE_H as LH640  # noqa: E402

W, H = 640, 360
K = 4 / 3
GAME = TOOLS.parents[2] / 'suma-zero/src/game'
OUT = Path(__file__).resolve().parent / 'guis'
GREY = [(30, 34, 44), (52, 58, 72), (74, 86, 112), (100, 110, 130), (130, 138, 156)]


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


# ─── Peces comunes ─────────────────────────────────────────────────────────

NS_W, NS_H, NS_B = 40, 26, 9        # el 9-slice: 40×26, vores de 9 (a 480: 30×20, vores de 7)


def nine_slice():
    """Panell fosc amb vora de llum verd blavós de 2 px, filet fosc i bisell, i un punt magenta de 2×2 a cada cantó."""
    img = Image.new('RGBA', (NS_W, NS_H), (0, 0, 0, 0))
    P = img.load()
    face = SLATE[2]
    ring = [SLATE[0], TEAL[5], TEAL[4], TEAL[2], SLATE[0], SLATE[5], SLATE[4], SLATE[3], SLATE[3]]
    ring_lo = [SLATE[0], TEAL[3], TEAL[2], TEAL[1], SLATE[0], SLATE[1], SLATE[2], SLATE[2], SLATE[2]]
    for y in range(NS_H):
        for x in range(NS_W):
            d = min(x, y, NS_W - 1 - x, NS_H - 1 - y)
            if d < len(ring):
                lo = (NS_H - 1 - y == d) or (NS_W - 1 - x == d)
                col = (ring_lo if lo else ring)[d]
            else:
                col = face                            # el centre s'estira: pla
            P[x, y] = col + (255,)
    for cx, cy in ((0, 0), (NS_W - 1, 0), (0, NS_H - 1), (NS_W - 1, NS_H - 1)):   # cantons arrodonits
        for dx in range(2):
            for dy in range(2 - dx):
                P[abs(cx - dx), abs(cy - dy)] = (0, 0, 0, 0)
    for cx, cy in ((5, 5), (NS_W - 7, 5), (5, NS_H - 7), (NS_W - 7, NS_H - 7)):
        P[cx, cy] = MAG[5] + (255,)
        P[cx + 1, cy] = MAG[4] + (255,)
        P[cx, cy + 1] = MAG[4] + (255,)
        P[cx + 1, cy + 1] = MAG[3] + (255,)
    return img


def nine_slices(frame=0):
    b, mw, mh = NS_B, NS_W - 2 * NS_B, NS_H - 2 * NS_B
    rects = {'TopLeft': (0, 0, b, b), 'TopMid': (b, 0, mw, b), 'TopRight': (b + mw, 0, b, b),
             'MidLeft': (0, b, b, mh), 'Mid': (b, b, mw, mh), 'MidRight': (b + mw, b, b, mh),
             'BottomLeft': (0, b + mh, b, b), 'BottomMid': (b, b + mh, mw, b), 'BottomRight': (b + mw, b + mh, b, b)}
    return [{'name': n, 'color': '#0000ffff', 'keys': [{'frame': frame, 'bounds': {'x': x, 'y': y, 'w': w, 'h': h}}]}
            for n, (x, y, w, h) in rects.items()]


KEY_STATES = (('', 4.4), ('-hover', 5.4), ('-pressed', 3.4), ('-disabled', 3.2))


def key_image(w, h, state):
    """Una tecla de w×h per a un botó de menú (normal, hover, premuda o desactivada), com a hd/gui.py a 640."""
    face = dict(KEY_STATES)[state]
    cv = Canvas(w, h, transparent=True)
    if state == '-pressed':
        key(cv, 0, 1, w - 1, h - 1, face=face, skirt=1)          # enfonsada: més baixa i sense gaire faldó
    else:
        key(cv, 0, 0, w - 1, h - 1, face=face)
    if state == '-hover':                                         # la ratlla magenta sota el text, amb halo
        for x in range(4, w - 4):
            cv.put(x, h - 6, MAG, 3.8 if 6 <= x < w - 6 else 3.0, lit=0)
            cv.put(x, h - 5, MAG, 2.2, lit=0)
    if state == '-disabled':                                      # trama de punts: no es pot prémer
        for y in range(3, h - 4, 2):
            for x in range(2 + (y // 2) % 2, w - 2, 2):
                cv.put(x, y, SLATE, 2.2, lit=0)
    return cv.img


def key_items(sizes):
    items = []
    for (w, h) in sizes:
        for st, _ in KEY_STATES:
            items.append((key_image(w, h, st), f'key-{w}x{h}{st}', (0, 0), (w, h)))
    return items


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
            c['x'], c['y'] = W // 2, y0 - 2
    save_gui('verbs', gui)


# ─── Diàleg ─────────────────────────────────────────────────────────────────

DLG_LINE = 260                                    # la línia de llum (195 a 480); el cos comença a 263
DLG_ARROWS = {'up': (4, 273), 'down': (4, 320)}   # botons de 13×33 (a 480: 10×25 a (3, 205) i (3, 240))
DLG_ORIGIN = {'up': (-1, 266), 'down': (-1, 295)}  # on el motor posa el (0, 0) del fotograma retallat
DLG_CROP = (29, 59)                               # 22×44 a 480
DLG_TOP = 233                                     # on comença el fotograma del fons (175 a 480)


def dialog_bg():
    cv = Canvas(W, H, transparent=True)
    body(cv, 0, DLG_LINE + 3, W - 1, H - 1, top=3.0)
    light_line(cv, 0, W - 1, DLG_LINE + 1)
    for x in range(W):
        dark(cv, x, DLG_LINE + 3, 0.5)
        cv.put(x, H - 1, SLATE, 0.8, lit=0)
    for y in range(DLG_LINE + 3, H - 1):
        cv.put(0, y, SLATE, 4.2, lit=0)
        cv.put(W - 1, y, SLATE, 1.2, lit=0)
    well(cv, 20, 267, 632, 355, face=0.8)              # la pantalla de les opcions
    for ax, ay in DLG_ARROWS.values():
        well(cv, ax, ay, ax + 11, ay + 32, face=1.0, brackets=False)
    led(cv, 7, 266, TEAL)
    led(cv, 7, 310, MAG)
    return cv.img


def dialog_arrow(which):
    cv = Canvas(W, H, transparent=True)
    ax, ay = DLG_ARROWS[which]
    arrow(cv, ax + 5, ay + 16, which == 'up', False, length=18)
    ox, oy = DLG_ORIGIN[which]
    full = Image.new('RGBA', (W + 2, H), (0, 0, 0, 0))
    full.paste(cv.img, (1, 0))
    return full.crop((ox + 1, oy, ox + 1 + DLG_CROP[0], oy + DLG_CROP[1]))


def dialog_bullet():
    """L'indicador de cada opció: un «>» de terminal, verd blavós, de traç de 2 px (a 480, d'1), i el cursor fluix."""
    cv = Canvas(59, 29, transparent=True)
    for i in range(7):
        x = 26 + (3 - abs(i - 3))
        v = 6.0 if i == 3 else (5.4 if i < 3 else 4.6)
        cv.put(x, 11 + i, TEAL, v, lit=0)
        cv.put(x + 1, 11 + i, TEAL, v - 1.0, lit=0)
    cv.put(31, 14, TEAL, 3.0, lit=0)
    cv.put(31, 15, TEAL, 2.6, lit=0)
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

CELL = (93, 27)                                    # els fotogrames del full de les opcions (70×20 a 480)


def checkbox(state):
    """Casella de 21×21: una pantalleta amb vora de llum (verd blavós; magenta en hover; grisa desactivada) i,
    marcada, una «v» de 2 px."""
    cv = Canvas(*CELL, transparent=True)
    hover, checked, off = 'hover' in state, 'checked' in state, 'disabled' in state
    ring = GREY if off else (MAG if hover else TEAL)
    n = 21
    for y in range(n):
        for x in range(n):
            if (x in (0, n - 1)) and (y in (0, n - 1)):
                continue
            d = min(x, y, n - 1 - x, n - 1 - y)
            if d == 0:
                cv.put(x, y, SLATE, 0.2, lit=0)
            elif d == 1:
                lo = y == n - 2 or x == n - 2
                cv.put(x, y, ring, (2.6 if off else 4.4) - (1.2 if lo else 0), lit=0)
            elif d == 2:
                cv.put(x, y, ring, 1.6 if not off else 1.2, lit=0)
            else:
                cv.put(x, y, SLATE, 1.0 + (0.35 if y % 2 == 0 else 0), lit=0)
    if checked:
        ink = GREY if off else (MAG if hover else TEAL)
        pts = [(5, 10), (6, 11), (7, 12), (8, 13), (9, 14), (10, 13), (11, 12), (12, 11), (13, 10), (14, 9),
               (15, 8), (16, 7), (16, 6)]
        for i, (x, y) in enumerate(pts):
            v = (3.0 if off else 5.8) - (0.3 if i > 4 else 0)
            cv.put(x, y, ink, v, lit=0)
            cv.put(x, y + 1, ink, v - 1.2, lit=0)
    return cv.img


def slider_handle(state):
    """El cursor del lliscador: una barreta de llum de 4×18 amb dues ratlles de gra."""
    cv = Canvas(*CELL, transparent=True)
    ramp, lv = (GREY, 2.6) if state == 'disabled' else ((MAG, 4.6) if state == 'hover' else (TEAL, 4.2))
    for y in range(1, 19):
        for x in range(5):
            if (y in (1, 18)) and x in (0, 4):
                continue
            v = lv + (1.0 if x == 0 else 0.4 if x == 1 else -0.8 if x == 4 else 0) + (0.6 if y == 1 else -0.8 if y == 18 else 0)
            cv.put(x, y, ramp, v, lit=0)
    for y in (8, 11):
        for x in (1, 2, 3):
            cv.put(x, y, ramp, lv - 1.6, lit=0)
    if state != 'disabled':
        cv.glow(2.5, 10, 6, ramp[3], 0.25)
    return cv.img


def slider_track(disabled):
    """El carril: una ranura fosca amb el fil de llum verd blavós al mig."""
    cv = Canvas(*CELL, transparent=True)
    for x in range(CELL[0]):
        end = x in (0, CELL[0] - 1)
        cv.put(x, 7, SLATE, 0.2, lit=0)
        cv.put(x, 8, SLATE, 0.6, lit=0)
        cv.put(x, 9, GREY if disabled else TEAL, (1.6 if disabled else 3.4) - (0.8 if end else 0), lit=0)
        cv.put(x, 10, GREY if disabled else TEAL, (1.2 if disabled else 2.0) - (0.6 if end else 0), lit=0)
        cv.put(x, 11, SLATE, 0.8, lit=0)
        cv.put(x, 12, SLATE, 4.0, lit=0)
    return cv.img


MENU_GUIS = ('display-text', 'game-menu', 'save-menu', 'load-menu', 'settings-menu')


def build_menus():
    for name in MENU_GUIS:
        gui = scaled_gui(name)
        sizes = []
        for c in gui['controls']:
            if c.get('type') == 'button' and str(c.get('backgroundTag', '')).startswith('key-'):
                wh = (c['width'], c['height'])
                tag = f'key-{wh[0]}x{wh[1]}'
                c['backgroundTag'] = tag
                c['states'] = {'hover': f'{tag}-hover', 'pressed': f'{tag}-pressed', 'disabled': f'{tag}-disabled'}
                if wh not in sizes:
                    sizes.append(wh)
            if c.get('type') == 'checkbox':
                c['width'] = c['height'] = 21
            if c.get('type') == 'slider':
                c['height'] = 20
        ns = (nine_slice(), '9-slice-BG', (0, 0), (NS_W, NS_H))
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
            items += key_items(sizes)
            write_sheet(OUT / name, name, items, cols=4, slices=nine_slices())
        else:
            write_sheet(OUT / name, name, [ns] + key_items(sizes), slices=nine_slices(), base='display-text')
        save_gui(name, gui)


# ─── Portada ────────────────────────────────────────────────────────────────

def cover_button(x0, y0, w, h, hover):
    """Els botons de la portada (com draw_placeholders.draw_cover_gui, a 640): placa fosca mig transparent, vora
    verd blavós de 2 px amb els cantons retallats, la llum de dalt i dues ratlletes a cada costat; en hover, més
    clara, amb la vora verda i un punt magenta a cada banda."""
    img = Image.new('RGBA', (W, H), (0, 0, 0, 0))
    d = ImageDraw.Draw(img)
    x1, y1 = x0 + w - 1, y0 + h - 1
    fill = (16, 34, 58, 240) if hover else (10, 16, 34, 225)
    vora = (40, 192, 116) if hover else (16, 120, 118)
    vora2 = (24, 120, 96) if hover else (12, 74, 80)
    llum = (60, 150, 120) if hover else (20, 70, 80)
    d.rectangle([x0 + 2, y0 + 2, x1 - 2, y1 - 2], fill=fill)
    d.line([(x0 + 3, y0), (x1 - 3, y0)], fill=vora + (255,))
    d.line([(x0 + 3, y1), (x1 - 3, y1)], fill=vora + (255,))
    d.line([(x0, y0 + 3), (x0, y1 - 3)], fill=vora + (255,))
    d.line([(x1, y0 + 3), (x1, y1 - 3)], fill=vora + (255,))
    for (cx, cy, sx, sy) in ((x0, y0, 1, 1), (x1, y0, -1, 1), (x0, y1, 1, -1), (x1, y1, -1, -1)):
        img.putpixel((cx + sx, cy + 2 * sy), vora + (255,))
        img.putpixel((cx + 2 * sx, cy + sy), vora + (255,))
        img.putpixel((cx + 2 * sx, cy + 2 * sy), vora2 + (255,))
    d.line([(x0 + 3, y0 + 1), (x1 - 3, y0 + 1)], fill=vora2 + (255,))   # segon filet: la vora fa 2 px
    d.line([(x0 + 1, y0 + 3), (x0 + 1, y1 - 3)], fill=vora2 + (255,))
    d.line([(x1 - 1, y0 + 3), (x1 - 1, y1 - 3)], fill=vora2 + (255,))
    d.line([(x0 + 3, y1 - 1), (x1 - 3, y1 - 1)], fill=(4, 8, 16, 255))
    d.line([(x0 + 4, y0 + 3), (x1 - 4, y0 + 3)], fill=llum + (255,))
    for k in (8, 13):
        for side in (x0 + k, x1 - k):
            for dy in (-1, 0, 1):
                img.putpixel((side, y0 + h // 2 + dy), vora + (255 if dy == 0 else 140,))
    if hover:
        for side in (x0 + 18, x1 - 18):
            for dx, dy, c in ((0, 0, MAG[4]), (1, 0, MAG[3]), (0, 1, MAG[3]), (1, 1, MAG[2])):
                img.putpixel((side + dx - (1 if side > x0 + w // 2 else 0), y0 + h // 2 + dy - 1), c + (255,))
    return img


def build_portada():
    gui = scaled_gui('portada')
    items = []
    for c in gui['controls']:
        if c.get('type') == 'text' and c['id'] == 'version':
            c['x'], c['y'] = W - 8, H - 15
        if c.get('type') != 'button':
            continue
        c['x'], c['width'], c['height'] = (W - 200) // 2, 200, 29
        for hover in (False, True):
            tag = c['id'] + ('-hover' if hover else '')
            items.append((cover_button(c['x'], c['y'], c['width'], c['height'], hover), tag, (0, 0), (W, H)))
        c['backgroundTag'] = c['id']
        c['states'] = {'hover': c['id'] + '-hover'}
    write_sheet(OUT / 'portada', 'portada', items, cols=6)
    save_gui('portada', gui)


# ─── Punter ─────────────────────────────────────────────────────────────────

def cursor_frame(gap, arm=5):
    """Creu blanca d'1 px amb ombra fosca a baix a la dreta, centrada a (21, 21) d'un fotograma de 43×43
    (la de 480: 32×32, braços de 4 i forat de 2)."""
    img = Image.new('RGBA', (43, 43), (0, 0, 0, 0))
    P = img.load()
    c = 21
    white, shade = (250, 255, 255, 255), (5, 9, 20, 255)
    pts = []
    for i in range(gap, gap + arm):
        pts += [(c + i, c), (c - i, c), (c, c + i), (c, c - i)]
    if gap == 0:
        pts.append((c, c))
    for x, y in pts:
        for dx, dy in ((1, 0), (0, 1)):
            if not P[x + dx, y + dy][3]:
                P[x + dx, y + dy] = shade
    for x, y in pts:
        P[x, y] = white
    return img


def build_cursor():
    """Els mateixos fotogrames i etiquetes que el punter del joc (Idle; Active de 4 fotogrames que van de la creu
    oberta a la tancada), un terç més grans."""
    f0, f2, f4 = cursor_frame(3), cursor_frame(5), cursor_frame(1, 6)
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
    for name in ('speaking-text', 'historial'):
        gui = scaled_gui(name)
        if name == 'historial':                           # el fons, la pantalla sencera; el peu, a 14×4/3 dels marges
            for c in gui['controls']:
                if c['id'] == 'fons':
                    c['width'], c['height'] = W, H
                if c['id'] == 'peu':
                    c['x'], c['y'] = W - 19, H - 20
        save_gui(name, gui)
    cfg = {'resolution': {'width': W, 'height': H},
           'dialog': {'choiceOptionsViewportHeightPx': s(63)},
           '_nota': 'Només el que canvia respecte de game-config.json del joc (hd640/gui_rest.py).'}
    (OUT / 'game-config.640.json').write_text(json.dumps(cfg, indent=2, ensure_ascii=False) + '\n')


# ─── Comprovació: els mateixos controls, ids i etiquetes que el joc ────────

def check():
    """Compara cada .gui.json de 640 amb el del joc: mateixos controls (id i tipus, en el mateix ordre), mateixes
    claus, i totes les etiquetes que fan servir existeixen al full de 640. Retorna la llista de problemes."""
    probs = []
    for gp in sorted((GAME / 'guis').glob('*/*.gui.json')):
        name = gp.parent.name
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
            lost = {t for t in old if not t.startswith('key-')} - have
            if lost:
                probs.append(f'{name}: etiquetes perdudes {lost}')
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
                out.paste(img.crop((sx, sy, sx + sw, sy + sh)).resize((dw, dh), Image.NEAREST), (dx, dy))
    return out


class Fonts:
    def __init__(self, res):
        if res == 640:
            self.reg, self.bold, self.space, self.lh = font640(False), font640(True), 4, LH640
        else:
            sys.path.insert(0, str(TOOLS.parents[2] / 'tools/font'))
            import suma_font as sf
            self.reg, self.bold, self.space, self.lh = sf.all_glyphs(False), sf.all_glyphs(True), sf.SPACE_ADVANCE, 12

    def g(self, font):
        return self.bold if 'negreta' in (font or '') else self.reg

    def _ok(self, font, s_):
        g = self.g(font)                                  # la font de 480 no té € ni ♪: el motor no els pinta
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
    'dialog': ['Qui ha deixat la porta del servidor oberta?', 'Quant costa un entrepà a Ginebra? 8,50 €?',
               '«Intel·ligent», diu el pany. No ho és gaire.'],
    'display-text': 'El pany intel·ligent de 19,99 € fa un clic. Obert.',
    'speaking-text': 'Ja hi som. Ara només cal que el router no s\'encalli.',
    'list': ['Escena 3 — el banc', 'Abans de pujar al pis', 'Ç·l·l: proves «d\'accents»'],
}


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
        x = cx + (cw - w) / 2 if al == 'center' else (cx + cw - w if 'right' in al else cx)
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
                img.alpha_composite(im, src)
        elif t == 'nineSliceImage' and ns_img is not None:
            x, y = place(c, c['width'], c['height'])
            img.alpha_composite(nine(ns_img, slices, c['width'], c['height']), (x, y))
        elif t == 'button':
            if name == 'dialog' and c['id'] == 'Dialog-Option':
                g = grids['Option-Grid']
                for i, s_ in enumerate(SAMPLE['dialog']):
                    y = g['y'] + i * c['height']
                    col = OPTION_HOVER if i == 1 else OPTION
                    if 'Bullet' in tags:
                        b, _ = tags['Bullet']
                        cx0 = g['x'] + g['colWidths'][0] / 2
                        img.alpha_composite(b, (round(cx0 - b.width / 2), round(y + c['height'] / 2 - b.height / 2)))
                    F.draw(img, c['font'], s_, g['x'] + g['colWidths'][0], y + (c['height'] - F.lh) // 2, col)
                continue
            x, y = place(c, c['width'], c['height'])
            hover = c['id'] in hover_ids
            if c.get('backgroundTag'):
                if c.get('backgroundAnchor') == 'screen':
                    tag = c['backgroundTag']
                    if hover and (c.get('states') or {}).get('hover') in tags:
                        tag = c['states']['hover']
                    if tag in tags:
                        im, src = tags[tag]
                        img.alpha_composite(im, src)
                else:
                    tag = c['backgroundTag']
                    if hover and (c.get('states') or {}).get('hover') in tags:
                        tag = c['states']['hover']
                    paste_tag(tag, x + c.get('backgroundOffsetX', 0), y + c.get('backgroundOffsetY', 0))
            elif c.get('backgroundColor'):
                ImageDraw.Draw(img).rectangle([x, y, x + c['width'] - 1, y + c['height'] - 1], fill=c['backgroundColor'])
            if c.get('text') and c.get('font') and name != 'historial':
                tw = F.width(c['font'], c['text'])
                col = (c.get('textColorStates') or {}).get('hover', TEXT_HOVER) if hover else (c.get('textColor') or TEXT)
                oc = (c.get('textOutline') or {}).get('color', TEXT_OUTLINE)
                F.draw(img, c['font'], c['text'], x + (c['width'] - tw) // 2 + c.get('textOffsetX', 0),
                       y + (c['height'] - F.lh) // 2 + c.get('textOffsetY', 0) + (1 if res == 640 else 0), col, oc)
        elif t == 'text':
            s_ = c.get('text') or ''
            if name in ('display-text', 'speaking-text'):
                s_ = SAMPLE[name]
            if name in ('portada', 'settings-menu') and c['id'] == 'version':
                s_ = 'v1.4.2'
            if name == 'historial':
                s_ = {'titol': 'Historial', 'noms': 'Vet:', 'linies': '     Quant costa un entrepà a Ginebra?',
                      'peu': 'Clic per tornar'}.get(c['id'], s_)
            if not s_:
                continue
            lines = F.wrap(c['font'], s_, c['wordWrapWidth']) if c.get('wordWrapWidth') else [s_]
            col = c.get('color') or LABEL
            if name == 'speaking-text':
                col = '#60d8d8'
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
                img.alpha_composite(tr.crop((0, 0, min(tr.width, c['width']), tr.height)).resize((c['width'], tr.height), Image.NEAREST), (x, y))
                frac = (c.get('defaultValue', 1) - c.get('min', 0)) / max(1e-6, c.get('max', 1) - c.get('min', 0))
                paste_tag('slider-handle', x + round(frac * (c['width'] - 5)), y)
        elif t == 'listBox':
            x, y = place(c, c['width'], c['height'])
            rh = F.lh + 2 * c.get('rowPadding', 0)
            d = ImageDraw.Draw(img)
            for i in range(c['height'] // rh):
                bgc = c.get('selectedBackgroundColor') if i == 1 else c.get('normalBackgroundColor', '#0d1222')
                d.rectangle([x, y + i * rh, x + c['width'] - 1, y + (i + 1) * rh - 2], fill=bgc)
                if i < len(SAMPLE['list']):
                    F.draw(img, c['font'], SAMPLE['list'][i], x + 3, y + i * rh + c.get('rowPadding', 0),
                           c.get('selectedTextColor', '#fff') if i == 1 else c.get('textColor', LABEL))
        elif t == 'textInput':
            x, y = place(c, c['width'], c['height'])
            d = ImageDraw.Draw(img)
            d.rectangle([x, y, x + c['width'] - 1, y + c['height'] - 1], fill=c.get('backgroundColor', '#090c17'),
                        outline=c.get('focusedOutlineColor', '#4fd3bf'))
            F.draw(img, c['font'], 'La meva partida', x + 3, y + (c['height'] - F.lh) // 2, c.get('color', LABEL))
    return img


def backdrops():
    """Fons de mostra (480 i 640): un «carrer de nit» de colors de sala, amb la barra de verbs a sota."""
    out = {}
    for res, (w, h) in ((480, (480, 270)), (640, (640, 360))):
        img = Image.new('RGBA', (w, h), (0, 0, 0, 255))
        d = ImageDraw.Draw(img)
        k = w / 480
        for y in range(h):
            t = y / h
            d.line([(0, y), (w, y)], fill=(int(30 + 40 * t), int(26 + 30 * t), int(60 + 20 * t), 255))
        for i, (x0, x1, top) in enumerate(((20, 120, 60), (140, 230, 90), (250, 380, 40), (400, 470, 100))):
            d.rectangle([x0 * k, top * k, x1 * k, 195 * k], fill=(40 + i * 6, 34, 64, 255))
            for wy in range(int(top * k) + 8, int(180 * k), int(14 * k)):
                for wx in range(int(x0 * k) + 6, int(x1 * k) - 6, int(16 * k)):
                    d.rectangle([wx, wy, wx + 5 * k, wy + 6 * k], fill=(230, 190, 110, 255) if (wx * 7 + wy) % 5 else (70, 70, 110, 255))
        d.rectangle([0, 170 * k, w, 195 * k], fill=(56, 50, 70, 255))
        out[res] = img
    return out


def full_screens(out_dir, back):
    """Pantalla completa de mostra: la sala, la barra amb l'inventari, i a sobre el text d'en Vet, el text en pantalla
    i el menú del joc; a part, la mateixa sala amb el diàleg obert."""
    shots = {}
    for res in (480, 640):
        b = back[res].copy()
        if res == 640:
            b.alpha_composite(vg.verb_bar({'hover': 'look', 'line': 'Mira el router'}), (0, vg.Y0))
        else:
            b.alpha_composite(vg.bar480(line='Mira el router', hover='look'), (0, 195))
        a = render_gui('speaking-text', res, b)
        a = render_gui('game-menu', res, a)
        shots[(res, 'menu')] = a
        shots[(res, 'dialog')] = render_gui('dialog', res, back[res])
    for kind in ('menu', 'dialog'):
        a = shots[(480, kind)].resize((1920, 1080), Image.NEAREST)
        b = shots[(640, kind)].resize((1920, 1080), Image.NEAREST)
        pair = Image.new('RGB', (1920 * 2 + 40, 1080 + 40), (30, 30, 30))
        pair.paste(a, (0, 40))
        pair.paste(b, (1960, 40))
        d = ImageDraw.Draw(pair)
        d.text((8, 12), f'pantalla ({kind}): 480x270 (x4)', fill=(255, 255, 255))
        d.text((1968, 12), f'pantalla ({kind}): 640x360 (x3)', fill=(255, 255, 255))
        pair.save(out_dir / f'pantalla_{kind}.png')
        shots[(640, kind)].resize((1920, 1080), Image.NEAREST).save(out_dir / f'pantalla_{kind}_640.png')


def contact(out_dir):
    out_dir = Path(out_dir)
    out_dir.mkdir(parents=True, exist_ok=True)
    back = backdrops()
    names = ('dialog', 'display-text', 'speaking-text', 'game-menu', 'save-menu', 'load-menu', 'settings-menu',
             'portada', 'historial')
    for n in names:
        a = render_gui(n, 480, back[480]).resize((1920, 1080), Image.NEAREST)
        b = render_gui(n, 640, back[640]).resize((1920, 1080), Image.NEAREST)
        pair = Image.new('RGB', (1920 * 2 + 40, 1080 + 40), (30, 30, 30))
        pair.paste(a, (0, 40))
        pair.paste(b, (1960, 40))
        d = ImageDraw.Draw(pair)
        d.text((8, 12), f'{n}: ACTUAL 480x270 (x4)', fill=(255, 255, 255))
        d.text((1968, 12), f'{n}: 640x360 (x3)', fill=(255, 255, 255))
        pair.save(out_dir / f'gui_{n}_640.png')
    full_screens(out_dir, back)
    cur = Image.new('RGB', (1000, 300), (120, 130, 140))
    c480 = Image.open(GAME / 'assets/images/cursor/cursor.png').convert('RGBA').resize((256, 256), Image.NEAREST)
    c640 = Image.open(OUT / 'cursor/cursor.png').convert('RGBA').resize((258, 258), Image.NEAREST)
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
    probs = check()
    for p in probs:
        print('  ⚠', p)
    if not probs:
        print('✔ mateixos controls, ids, claus i etiquetes que les GUI del joc')
    if len(sys.argv) > 1:
        contact(sys.argv[1])
        print(f'✔ comparatives a {sys.argv[1]}')


if __name__ == '__main__':
    main()
