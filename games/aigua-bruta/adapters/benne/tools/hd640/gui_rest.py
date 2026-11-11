#!/usr/bin/env python3
"""
Prova de resolució: la resta de la interfície a 640×360 (la barra de verbs és a hd640/gui.py).

Redibuixa, amb el mateix estil que la barra de 640 (planxa blau marí, corda trenada, reblons de 2×2, llautó),
els fulls de totes les GUI del joc i en proposa els .gui.json a 640, sense tocar el joc:

  hd640/guis/<gui>/<gui>.png + .json      el full (mateixos noms d'etiqueta i 9-slice que el del joc)
  hd640/guis/<gui>/<gui>.gui.json         la GUI a 640: posicions i mides ×4/3, ajustades on cal; botons
                                          `key-WxH` amb la mida nova; fonts amb el mateix nom (les de
                                          hd640/font.py, que s'exporten amb aquests noms), fontSize 8
  hd640/guis/cursor/cursor.png + .json    el punter, un terç més gran (43×43)
  hd640/guis/game-config.640.json         el que canvia a game-config.json (resolució, llista d'opcions)

GUI: verbs (la barra exportada en fotogrames, com verbs.png), dialog, display-text, game-menu, save-menu,
load-menu, settings-menu, portada, speaking-text i historial (aquestes dues no tenen full: només json).

    python3 hd640/gui_rest.py [carpeta de comparatives]

També munta les comparatives (cada GUI a 480 ×4 i a 640 ×3, amb textos) a la carpeta que es digui.
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
from hd.pix import Canvas, hr, mix  # noqa: E402
from hd.gui import (NAVYB, ROPE, BRASS, HOT, TEXT, TEXT_HOVER, TEXT_OUTLINE, VERB_LINE, OPTION, OPTION_HOVER,  # noqa: E402
                    TITLE, LABEL, DISABLED, box, dark, corners, well, arrow)
import hd640.gui as vg  # noqa: E402
from hd640.font import font640, text_width as tw640, draw_text as dt640, LINE_H as LH640  # noqa: E402

W, H = 640, 360
K = 4 / 3
GAME = TOOLS.parents[2] / 'aigua-bruta/src/game'
OUT = Path(__file__).resolve().parent / 'guis'
GREY = [(40, 40, 44), (70, 70, 74), (99, 99, 99), (130, 130, 132), (160, 160, 160)]


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
    """Planxa blau marí amb marc de llautó bisellat (3 px), filet fosc, i un rebló de 2×2 a cada cantó."""
    img = Image.new('RGBA', (NS_W, NS_H), (0, 0, 0, 0))
    P = img.load()
    ring = [NAVYB[0], BRASS[5], BRASS[4], BRASS[3], NAVYB[0], NAVYB[7], NAVYB[5], NAVYB[4], NAVYB[4]]
    ring_lo = [NAVYB[0], BRASS[3], BRASS[2], BRASS[1], NAVYB[0], NAVYB[2], NAVYB[3], NAVYB[3], NAVYB[3]]
    for y in range(NS_H):
        for x in range(NS_W):
            d = min(x, y, NS_W - 1 - x, NS_H - 1 - y)
            if d < len(ring):
                lo = (NS_H - 1 - y == d) or (NS_W - 1 - x == d)
                col = (ring_lo if lo else ring)[d]
            else:
                col = NAVYB[3]                        # la planxa: plana (el centre s'estira, un gra hi faria dibuix)
            P[x, y] = col + (255,)
    for cx, cy in ((0, 0), (NS_W - 1, 0), (0, NS_H - 1), (NS_W - 1, NS_H - 1)):   # cantons arrodonits
        for dx in range(2):
            for dy in range(2 - dx):
                P[abs(cx - dx), abs(cy - dy)] = (0, 0, 0, 0)
    for cx, cy in ((5, 5), (NS_W - 7, 5), (5, NS_H - 7), (NS_W - 7, NS_H - 7)):
        P[cx, cy] = NAVYB[8] + (255,)
        P[cx + 1, cy] = NAVYB[7] + (255,)
        P[cx, cy + 1] = NAVYB[6] + (255,)
        P[cx + 1, cy + 1] = NAVYB[5] + (255,)
        P[cx + 2, cy + 2] = NAVYB[0] + (255,)
    return img


def nine_slices(frame=0):
    b, mw, mh = NS_B, NS_W - 2 * NS_B, NS_H - 2 * NS_B
    rects = {'TopLeft': (0, 0, b, b), 'TopMid': (b, 0, mw, b), 'TopRight': (b + mw, 0, b, b),
             'MidLeft': (0, b, b, mh), 'Mid': (b, b, mw, mh), 'MidRight': (b + mw, b, b, mh),
             'BottomLeft': (0, b + mh, b, b), 'BottomMid': (b, b + mh, mw, b), 'BottomRight': (b + mw, b + mh, b, b)}
    return [{'name': n, 'color': '#0000ffff', 'keys': [{'frame': frame, 'bounds': {'x': x, 'y': y, 'w': w, 'h': h}}]}
            for n, (x, y, w, h) in rects.items()]


KEY_FACE = {'': 4.4, '-hover': 5.2, '-pressed': 3.6, '-disabled': 3.0}


def key_image(w, h, state):
    """Placa de botó de menú a 640: bisell de 2 px, reblons de 2×2; en hover, cantoneres de llautó de 2 px."""
    face = KEY_FACE[state]
    cv = Canvas(w, h, transparent=True)
    box(cv, 0, 0, w - 1, h - 1, NAVYB, face)
    if state == '-pressed':
        cv.hline(1, w - 2, 1, NAVYB, face - 1.4, lit=0)
        cv.hline(1, w - 2, 2, NAVYB, face - 0.8, lit=0)
        cv.vline(1, 1, h - 2, NAVYB, face - 1.2, lit=0)
        return cv.img
    cv.hline(1, w - 2, 1, NAVYB, face + 1.0, lit=0)
    cv.hline(2, w - 3, 2, NAVYB, face + 0.5, lit=0)
    cv.vline(1, 2, h - 3, NAVYB, face + 0.6, lit=0)
    cv.hline(2, w - 2, h - 2, NAVYB, face - 0.9, lit=0)
    if state == '-disabled':
        return cv.img
    for bx, by in ((3, 4), (w - 5, 4), (3, h - 6), (w - 5, h - 6)):
        cv.put(bx, by, NAVYB, face + 2.4, lit=0)
        cv.put(bx + 1, by + 1, NAVYB, face - 1.4, lit=0)
    if state == '-hover':
        corners(cv, 1, 1, w - 2, h - 2, n=5)
        corners(cv, 2, 2, w - 3, h - 3, n=3)
    return cv.img


def key_items(sizes):
    items = []
    for (w, h) in sizes:
        for st in ('', '-hover', '-pressed', '-disabled'):
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
    keep = vg.menu_button
    vg.menu_button = lambda cv: None                 # el fons sense el botó del menú (que va a part)
    try:
        bg = vg.background()
    finally:
        vg.menu_button = keep
    full_bg = Image.new('RGBA', (W, H), (0, 0, 0, 0))
    full_bg.paste(bg.img, (0, vg.Y0))

    def arrow_frame(which, hot):
        def d(cv):
            ax, ay = vg.ARROWS[which]
            if hot:
                box(cv, ax, ay, ax + 12, ay + 35, NAVYB, 4.8)
            arrow(cv, ax + 6, ay + 18, which == 'up', hot, length=15)
        return _bar_frame(d)

    def face_frame(who):
        out = Image.new('RGBA', (W, H), (0, 0, 0, 0))
        f = vg.face(who)
        out.alpha_composite(f, (vg.PORT[0] - f.width // 2, vg.Y0 + vg.PORT[1] - f.height // 2 - 1))
        return out

    ref = Image.new('RGBA', (W, H), (0, 0, 0, 0))     # fotograma 0: referència (la barra sencera, amb textos)
    ref.paste(vg.verb_bar(), (0, vg.Y0))
    frames = [(ref, None), (full_bg, 'VerbsBG'), (arrow_frame('up', False), 'UpBtn'), (arrow_frame('down', False), 'DownBtn'),
              (_bar_frame(vg.menu_button), 'MenuBtn'), (arrow_frame('up', True), 'UpBtn-hover'),
              (arrow_frame('down', True), 'DownBtn-hover'), (_bar_frame(lambda cv: vg.porthole(cv, False)), 'CanviaBtn'),
              (_bar_frame(lambda cv: vg.porthole(cv, True)), 'CanviaBtn-hover'), (face_frame('iri'), 'CaraIri'),
              (face_frame('vet'), 'CaraVet')]
    write_sheet(OUT / 'verbs', 'verbs', [(im, t, (0, 0), (W, H)) for im, t in frames], cols=3)

    gui = scaled_gui('verbs')
    y0 = vg.Y0
    verb_ids = {'give': 'GiveBtn', 'pickUp': 'PickUpBtn', 'use': 'UseBtn', 'open': 'OpenBtn', 'talkTo': 'TalkToBtn',
                'push': 'PushBtn', 'close': 'CloseBtn', 'look': 'LookAtBtn', 'pull': 'PullBtn'}
    pos = {}
    for row, vy in zip(vg.VERB_IDS, vg.VERB_ROWS):
        for (vx, vw), vid in zip(vg.VERB_COLS, row):
            pos[verb_ids[vid]] = (vx, y0 + vy, vw, vg.VERB_H)
    pos['upBtn'] = (*_add(vg.ARROWS['up'], y0), 13, 36)
    pos['downBtn'] = (*_add(vg.ARROWS['down'], y0), 13, 36)
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


def _add(xy, dy):
    return xy[0], xy[1] + dy


# ─── Diàleg ─────────────────────────────────────────────────────────────────

DLG_TOP = 260                                     # 195 × 4/3
DLG_ARROWS = {'up': (4, 273), 'down': (4, 320)}   # botons de 13×33 (a 480: 10×25)
DLG_ORIGIN = {'up': (-1, 267), 'down': (-1, 295)}
DLG_CROP = (29, 59)                               # 22×44 a 480


def dialog_bg():
    cv = Canvas(W, H, transparent=True)
    vg.body(cv, DLG_TOP, H - 1)
    vg.rope(cv, DLG_TOP)
    well(cv, 20, 267, 632, 355, face=1.2, brass=False)
    corners(cv, 21, 268, 631, 354, n=6)
    corners(cv, 22, 269, 630, 353, n=3)
    for ax, ay in DLG_ARROWS.values():
        box(cv, ax, ay, ax + 11, ay + 32, NAVYB, 4.0)
        cv.hline(ax + 1, ax + 10, ay + 1, NAVYB, 5.0, lit=0)
    for x, y in ((8, 309), (635, 270), (635, 349), (8, 352)):
        vg.big_rivet(cv, x, y)
    return cv.img


def dialog_arrow(which):
    cv = Canvas(W, H, transparent=True)
    ax, ay = DLG_ARROWS[which]
    arrow(cv, ax + 5, ay + 16, which == 'up', False, length=15)
    ox, oy = DLG_ORIGIN[which]
    full = Image.new('RGBA', (W + 2, H), (0, 0, 0, 0))
    full.paste(cv.img, (1, 0))
    return full.crop((ox + 1, oy, ox + 1 + DLG_CROP[0], oy + DLG_CROP[1]))


def dialog_bullet():
    """L'indicador de cada opció: un triangle de llautó amb volum (a 480, 3 px; aquí 5)."""
    cv = Canvas(59, 29, transparent=True)
    for i in range(9):
        half = 4 - abs(i - 4)
        for j in range(half + 1):
            v = 5.4 - j * 0.5 if i < 4 else (4.4 - j * 0.6 if i == 4 else 3.4 - j * 0.4)
            cv.put(25 + j, 10 + i, BRASS, v, lit=0)
    cv.put(25, 10, BRASS, 6.0, lit=0)
    return cv.img


def build_dialog():
    bgfull = dialog_bg()
    ref = bgfull.copy()                                       # fotograma 0: referència
    ref.paste(Image.new('RGBA', (W, 24), (0, 0, 0, 0)), (0, 0))
    bg = Image.new('RGBA', (W, 145), (0, 0, 0, 0))
    bg.paste(bgfull.crop((0, 233, W, H)), (0, 0))
    items = [(ref, None, (0, 0), (W, 379)),
             (bg, 'VerbsBG', (0, 233), (W, H)),
             (dialog_arrow('up'), 'UpBtn', (0, 261), (W, H)),
             (dialog_arrow('down'), 'DownBtn', (0, 291), (W, H)),
             (dialog_bullet(), 'Bullet', (0, 261), (W, H))]
    write_sheet(OUT / 'dialog', 'dialog', items)
    gui = scaled_gui('dialog')
    for c in gui['controls']:
        if c['id'] == 'scrollUp':
            c.update(x=DLG_ARROWS['up'][0], y=DLG_ARROWS['up'][1], width=13, height=33)
        if c['id'] == 'scrollDown':
            c.update(x=DLG_ARROWS['down'][0], y=DLG_ARROWS['down'][1], width=13, height=33)
        if c['id'] == 'Option-Grid':
            c.update(x=22, y=270, width=607, height=25)
        if c['id'] == 'Dialog-Option':
            c.update(width=589, height=25)
    save_gui('dialog', gui)


# ─── Menús ──────────────────────────────────────────────────────────────────

def checkbox(state):
    """Casella de 16×16 dins un fotograma de 93×27: vora de 2 px; marcada, una «v» de llautó de 2 px."""
    img = Canvas(93, 27, transparent=True)
    hover, checked, off = 'hover' in state, 'checked' in state, 'disabled' in state
    ring = GREY if off else (BRASS if hover else NAVYB)
    lv = 2.4 if off else (3.6 if hover else 5.0)
    for y in range(16):
        for x in range(16):
            d = min(x, y, 15 - x, 15 - y)
            if d < 2 and not ((x in (0, 15)) and (y in (0, 15))):
                img.put(x, y, ring, lv + (0.8 if d == 0 and (x == 0 or y == 0) else 0) - (0.6 if d == 1 else 0), lit=0)
    if checked:
        ink = GREY if off else BRASS
        pts = [(3, 8), (4, 9), (5, 10), (6, 11), (7, 10), (8, 9), (9, 8), (10, 7), (11, 6), (12, 5), (12, 4)]
        for i, (x, y) in enumerate(pts):
            v = (3.0 if off else (5.8 if hover else 5.2)) - (0.2 if i > 6 else 0)
            img.put(x, y, ink, v, lit=0)
            img.put(x, y + 1, ink, v - 1.4, lit=0)
    return img.img


def slider_handle(state):
    cv = Canvas(93, 27, transparent=True)
    ramp, lv = (GREY, 2.6) if state == 'disabled' else (BRASS, 4.4 if state == 'hover' else 3.6)
    for y in range(15):
        for x in range(4):
            v = lv + (1.0 if x == 0 else 0.4 if x == 1 else -0.6 if x == 3 else 0) + (0.6 if y == 0 else -0.8 if y == 14 else 0)
            if (y in (0, 14)) and x in (0, 3):
                continue
            cv.put(x, y, ramp, v, lit=0)
    for y in (6, 8):
        cv.put(1, y, ramp, lv - 1.6, lit=0)
        cv.put(2, y, ramp, lv - 1.2, lit=0)
    return cv.img


def slider_track(disabled):
    cv = Canvas(93, 27, transparent=True)
    ramp = GREY if disabled else NAVYB
    base = 2.4 if disabled else 3.0
    cv.hline(1, 91, 5, ramp, base - 1.0, lit=0)
    cv.hline(0, 92, 6, ramp, base, lit=0)
    cv.hline(0, 92, 7, ramp, base + 0.6, lit=0)
    cv.hline(1, 91, 8, ramp, base + 1.4 if not disabled else base, lit=0)
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
            pad = Image.new('RGBA', (93, 27), (0, 0, 0, 0))
            pad.paste(ns[0], (0, 0))
            items = [(pad, '9-slice-BG', (0, 0), (93, 27))]
            for st in ('checkbox', 'checkbox-hover', 'checkbox-checked', 'checkbox-checked-hover', 'checkbox-disabled',
                       'checkbox-checked-disabled'):
                items.append((checkbox(st), st, (0, 0), (93, 27)))
            items += [(slider_handle(''), 'slider-handle', (0, 0), (93, 27)),
                      (slider_handle('hover'), 'slider-handle-hover', (0, 0), (93, 27)),
                      (slider_track(False), 'slider-track', (0, 0), (93, 27)),
                      (slider_handle('disabled'), 'slider-handle-disabled', (0, 0), (93, 27)),
                      (slider_track(True), 'slider-track-disabled', (0, 0), (93, 27))]
            items += key_items(sizes)
            write_sheet(OUT / name, name, items, cols=4, slices=nine_slices())
        else:
            write_sheet(OUT / name, name, [ns] + key_items(sizes), slices=nine_slices(), base='display-text')
        save_gui(name, gui)


# ─── Portada ────────────────────────────────────────────────────────────────

def cover_button(x0, y0, w, h, hover):
    """Placa fosca, mig transparent, amb vora de llautó verdós (la del joc és verd blavós), cantons retallats,
    filet de llum a dalt i dues ratlletes a cada costat; en hover, més clara i amb la vora encesa."""
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
    d.line([(x0 + 3, y0 + 1), (x1 - 3, y0 + 1)], fill=vora2 + (255,))   # segon filet, la vora fa 2 px
    d.line([(x0 + 1, y0 + 3), (x0 + 1, y1 - 3)], fill=vora2 + (255,))
    d.line([(x0 + 3, y1 - 1), (x1 - 3, y1 - 1)], fill=(4, 8, 16, 255))
    d.line([(x1 - 1, y0 + 3), (x1 - 1, y1 - 3)], fill=(4, 8, 16, 255))
    d.line([(x0 + 4, y0 + 3), (x1 - 4, y0 + 3)], fill=llum + (255,))
    for k in (8, 13):
        for side in (x0 + k, x1 - k):
            for dy in (-1, 0, 1):
                img.putpixel((side, y0 + h // 2 + dy), vora + (255 if dy == 0 else 140,))
    if hover:
        for k in (3, 4):
            img.putpixel((x0 + k + 15, y0 + h // 2), HOT[4] + (255,))
            img.putpixel((x1 - k - 15, y0 + h // 2), HOT[4] + (255,))
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
        c['states'] = {'hover': c['id'] + '-hover'}
    write_sheet(OUT / 'portada', 'portada', items, cols=6)
    save_gui('portada', gui)


# ─── Punter ─────────────────────────────────────────────────────────────────

def cursor_frame(gap, arm=5):
    """Creu blanca d'1 px amb ombra fosca a baix a la dreta, centrada a (21, 21) d'un fotograma de 43×43."""
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
    f0, f2, f4 = cursor_frame(3), cursor_frame(5), cursor_frame(0, 6)
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
    gui['description'] = (gui.get('description') or '') + ' [640×360: hd640/gui_rest.py]'
    return gui


def save_gui(name, gui):
    d = OUT / name
    d.mkdir(parents=True, exist_ok=True)
    (d / f'{name}.gui.json').write_text(json.dumps(gui, indent=2, ensure_ascii=False) + '\n')


def build_jsons_only():
    for name in ('speaking-text', 'historial'):
        save_gui(name, scaled_gui(name))
    cfg = {'resolution': {'width': W, 'height': H},
           'dialog': {'choiceOptionsViewportHeightPx': s(63)},
           '_nota': 'Només el que canvia respecte de game-config.json del joc (hd640/gui_rest.py).'}
    (OUT / 'game-config.640.json').write_text(json.dumps(cfg, indent=2, ensure_ascii=False) + '\n')


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
            self.tw, self.dt = tw640, dt640
        else:
            sys.path.insert(0, str(TOOLS.parents[2] / 'tools/font'))
            import aigua_font as af
            self.reg, self.bold, self.space, self.lh = af.all_glyphs(False), af.all_glyphs(True), af.SPACE_ADVANCE, 12
            self.tw, self.dt = tw640, dt640

    def g(self, font):
        return self.bold if 'negreta' in (font or '') else self.reg

    def width(self, font, s_):
        return self.tw(self.g(font), s_, self.space)

    def draw(self, img, font, s_, x, y, color, outline=TEXT_OUTLINE):
        self.dt(img, self.g(font), s_, x, y, color, outline=outline, space=self.space)

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
    'dialog': ['Què hi feies, a la sala de màquines, a les tres?', 'Has vist algú amb una cisalla?',
               '«Mostra 7», diu l\'etiqueta. Per què és tan important?'],
    'display-text': 'La brida està tallada. Algú ha volgut que la bomba no xuclés.',
    'speaking-text': 'Si l\'Ernest diu que és vella, és vella. Port Hallen.',
    'list': ['Escena 3 — la sala de ràdio', 'Abans de baixar al pallol', 'Ç·l·l: proves «d\'accents»'],
}


def render_gui(name, res, backdrop):
    """La GUI `name` a la resolució `res` (480: la del joc; 640: la de hd640/guis), sobre `backdrop`."""
    if res == 640:
        Wr, Hr = W, H
        gdir = OUT / name
        gpath = gdir / f'{name}.gui.json'
    else:
        Wr, Hr = 480, 270
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
    opt_n = [0]

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
    # el menú del joc fa servir una graella sense gridPlacement: la simulem en files (2 botons petits per fila)
    if name == 'game-menu':
        g = grids['menu-layout']
        rh = g['height'] / g['rows']
        row, col = 1, 0
        for c in controls:
            if c.get('type') == 'button':
                if c['width'] > g['width'] // 2 and col:
                    row, col = row + 1, 0
                c['_xy'] = (g['x'] + col * (g['width'] - c['width']), round(g['y'] + rh * row + (rh - c['height']) / 2))
                if c['width'] > g['width'] // 2 or col:
                    row, col = row + 1, 0
                else:
                    col = 1
            if c.get('id') == 'title':
                c['_xy'] = (g['x'] + (g['width'] - F.width(c['font'], c['text'])) // 2, g['y'] + 2)
    for c in controls:
        t = c.get('type')
        if c.get('visible') is False and t != 'image':
            continue
        if t == 'image':
            if c.get('tag') in ('CaraIri', 'CaraVet', 'Bullet'):
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
                        img.alpha_composite(b, (g['x'] - b.width // 2 + 2, y + c['height'] // 2 - b.height // 2))
                    F.draw(img, c['font'], s_, g['x'] + 8, y + (c['height'] - F.lh) // 2, col)
                continue
            x, y = c.get('_xy') or place(c, c['width'], c['height'])
            if c.get('backgroundTag'):
                if c.get('backgroundAnchor') == 'screen':
                    if c['backgroundTag'] in tags:
                        im, src = tags[c['backgroundTag']]
                        hover = name == 'portada' and c['id'] == 'comenca'
                        if hover and c['backgroundTag'] + '-hover' in tags:
                            im, src = tags[c['backgroundTag'] + '-hover']
                        img.alpha_composite(im, src)
                elif name == 'dialog':                     # el motor posa el fotograma retallat al seu origen
                    org = {480: {'scrollUp': (-1, 200), 'scrollDown': (-1, 221)},
                           640: {'scrollUp': DLG_ORIGIN['up'], 'scrollDown': DLG_ORIGIN['down']}}[res]
                    paste_tag(c['backgroundTag'], *org[c['id']])
                else:
                    hover = c['id'] in ('load', 'save-btn', 'load-btn')
                    paste_tag(c['backgroundTag'] + ('-hover' if hover else ''), x, y)
            if c.get('text') and c.get('font') and name != 'historial':
                tw = F.width(c['font'], c['text'])
                hover = c['id'] in ('load', 'save-btn', 'load-btn', 'comenca')
                col = TEXT_HOVER if hover else (c.get('textColor') or TEXT)
                F.draw(img, c['font'], c['text'], x + (c['width'] - tw) // 2 + c.get('textOffsetX', 0),
                       y + (c['height'] - F.lh) // 2 + c.get('textOffsetY', 0) + (1 if res == 640 else 0), col)
        elif t == 'text':
            s_ = c.get('text') or ''
            if name == 'display-text':
                s_ = SAMPLE['display-text']
            if name == 'speaking-text':
                s_ = SAMPLE['speaking-text']
            if name == 'portada' and c['id'] == 'version':
                s_ = 'v0.0.0'
            if name == 'historial':
                s_ = {'titol': 'Historial', 'noms': 'Vet:', 'linies': '      Has vist algú amb una cisalla?',
                      'peu': 'Clic per tornar'}.get(c['id'], s_)
            if not s_:
                continue
            lines = F.wrap(c['font'], s_, c['wordWrapWidth']) if c.get('wordWrapWidth') else [s_]
            col = c.get('color') or LABEL
            if name == 'speaking-text':
                col = '#7fd8e6'
            for i, ln in enumerate(lines):
                w_ = F.width(c['font'], ln)
                if c.get('_xy'):
                    x, y = c['_xy']
                elif c.get('gridPlacement'):
                    x, y = place(c, w_, F.lh)
                else:
                    x, y = c['x'], c['y']
                    al = c.get('align', 'left')
                    x = x - w_ // 2 if al == 'center' else (x - w_ if al == 'right' else x)
                F.draw(img, c['font'], ln, x, y + i * F.lh, col)
        elif t == 'checkbox':
            x, y = place(c, c['width'], c['height'])
            paste_tag('checkbox-checked' if c.get('checked') else 'checkbox', x, y)
        elif t == 'slider':
            x, y = place(c, c['width'], c['height'])
            if 'slider-track' in tags:
                tr = tags['slider-track'][0]
                img.alpha_composite(tr.crop((0, 0, min(tr.width, c['width']), tr.height)).resize((c['width'], tr.height), Image.NEAREST), (x, y))
                frac = (c.get('defaultValue', 1) - c.get('min', 0)) / max(1e-6, c.get('max', 1) - c.get('min', 0))
                paste_tag('slider-handle', x + round(frac * (c['width'] - 4)), y)
        elif t == 'listBox':
            x, y = place(c, c['width'], c['height'])
            rh = F.lh + 2 * c.get('rowPadding', 0)
            d = ImageDraw.Draw(img)
            for i in range(c['height'] // rh):
                bgc = c.get('selectedBackgroundColor') if i == 1 else c.get('normalBackgroundColor', '#0d1526')
                d.rectangle([x, y + i * rh, x + c['width'] - 1, y + (i + 1) * rh - 2], fill=bgc)
                if i < len(SAMPLE['list']):
                    F.draw(img, c['font'], SAMPLE['list'][i], x + 3, y + i * rh + c.get('rowPadding', 0),
                           c.get('selectedTextColor', '#fff') if i == 1 else c.get('textColor', LABEL))
        elif t == 'textInput':
            x, y = place(c, c['width'], c['height'])
            d = ImageDraw.Draw(img)
            d.rectangle([x, y, x + c['width'] - 1, y + c['height'] - 1], fill=c.get('backgroundColor', '#090f1c'),
                        outline=c.get('focusedOutlineColor', '#e8c260'))
            F.draw(img, c['font'], 'La meva partida', x + 3, y + (c['height'] - F.lh) // 2, c.get('color', LABEL))
    return img


def contact(out_dir):
    out_dir = Path(out_dir)
    out_dir.mkdir(parents=True, exist_ok=True)
    back480 = Image.open(out_dir / 'laboratori_480.png').convert('RGBA').resize((480, 270), Image.NEAREST)
    back640 = Image.open(out_dir / 'laboratori_640.png').convert('RGBA').resize((640, 360), Image.NEAREST)
    names = ('dialog', 'display-text', 'speaking-text', 'game-menu', 'save-menu', 'load-menu', 'settings-menu',
             'portada', 'historial')
    rows = []
    for n in names:
        a = render_gui(n, 480, back480).resize((1920, 1080), Image.NEAREST)
        b = render_gui(n, 640, back640).resize((1920, 1080), Image.NEAREST)
        pair = Image.new('RGB', (1920 * 2 + 40, 1080 + 40), (30, 30, 30))
        pair.paste(a, (0, 40))
        pair.paste(b, (1960, 40))
        d = ImageDraw.Draw(pair)
        d.text((8, 12), f'{n}: ACTUAL 480x270 (x4)', fill=(255, 255, 255))
        d.text((1968, 12), f'{n}: PROVA 640x360 (x3)', fill=(255, 255, 255))
        pair.save(out_dir / f'gui_{n}_640.png')
        rows.append(pair.resize((pair.width // 2, pair.height // 2), Image.NEAREST))
    sheet = Image.new('RGB', (rows[0].width, sum(r.height for r in rows)), (30, 30, 30))
    y = 0
    for r in rows:
        sheet.paste(r, (0, y))
        y += r.height
    sheet.save(out_dir / 'guis_640.png')
    # el punter
    cur = Image.new('RGB', (1920, 300), (120, 130, 140))
    c480 = Image.open(GAME / 'assets/images/cursor/cursor.png').convert('RGBA')
    c640 = Image.open(OUT / 'cursor/cursor.png').convert('RGBA')
    cur.paste(c480.resize((256, 256), Image.NEAREST), (40, 20), c480.resize((256, 256), Image.NEAREST))
    cur.paste(c640.resize((258, 258), Image.NEAREST), (400, 20), c640.resize((258, 258), Image.NEAREST))
    cur.save(out_dir / 'gui_cursor_640.png')


def main():
    build_verbs()
    build_dialog()
    build_menus()
    build_portada()
    build_cursor()
    build_jsons_only()
    print(f'✔ GUI de 640 a {OUT}')
    if len(sys.argv) > 1:
        contact(sys.argv[1])
        print(f'✔ comparatives a {sys.argv[1]}')


if __name__ == '__main__':
    main()
