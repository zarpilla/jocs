#!/usr/bin/env python3
"""
Interfície del joc en pixel art HD: barra de verbs, quadre d'opcions de diàleg i el fons
9-slice dels menús (menú del joc, desa, carrega, configuració i text en pantalla).

Genera els fulls d'Aseprite (PNG + JSON) amb la mateixa estructura que les plantilles de Benne
(mateixos fotogrames, mides i etiquetes), i només hi canvia el dibuix. Estil de Suma Zero: una consola
d'hacker, amb els colors de la portada. Els verbs són tecles d'un teclat fosc; l'inventari, pantalletes
amb línies d'escaneig i cantoneres de visor; la barra es tanca amb una línia de llum verd blavós, i el
magenta és l'accent (el que tens sota el ratolí).

Ús (idempotent: es pot tornar a executar sempre que es vulgui):

    python3 adapters/benne/tools/hd/gui.py suma-zero/src/game

  - verbs.png/.json: fotograma 0 (captura de referència de la plantilla) es conserva tal qual;
    1-6 (fons, fletxes, menú) es dibuixen aquí; 7-8 (botó «Canvia») surten de
    `switch_button_image()` de draw_placeholders.py, igual que fa `add_switch_button()`
    (que, si es torna a executar, hi posa exactament el mateix).
  - dialog.png/.json: fotograma 0 es conserva; 1 (fons), 2-3 (fletxes) i 4 (indicador) es dibuixen.
  - display-text, game-menu, save-menu, load-menu: el 9-slice de 30×20 (el JSON no es toca).
  - settings-menu: només el 9-slice del fotograma 0 (caselles i lliscadors es queden).
  - els colors del text dels .gui.json (verbs, frase, opcions de diàleg) es posen als d'aquí.
"""
import json
import sys
from pathlib import Path

from PIL import Image

TOOLS = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(TOOLS))
from hd.pix import Canvas, hr, mix  # noqa: E402

FW, FH = 480, 270

# ─── Paleta ─────────────────────────────────────────────────────────────────
# Blau marí gairebé negre (el cos de la consola), verd blavós (la llum) i magenta (l'accent).
SLATE = [(3, 4, 10), (6, 8, 16), (9, 12, 23), (13, 17, 31), (18, 23, 40), (24, 31, 52), (32, 41, 66),
         (44, 55, 84), (60, 74, 106), (84, 100, 134), (120, 138, 170)]
TEAL = [(4, 26, 30), (6, 48, 52), (10, 78, 80), (18, 116, 112), (36, 160, 148), (80, 210, 190),
        (160, 245, 226), (230, 255, 248)]
MAG = [(40, 6, 30), (84, 14, 64), (140, 26, 104), (200, 50, 150), (240, 100, 196), (255, 170, 228),
       (255, 228, 246)]
BRASS = MAG   # (compatibilitat: abans era el llautó de Ferro-9; ara l'accent és el magenta)

# Colors del text (els posa el motor): es copien als .gui.json (vegeu `apply_text_colors`).
TEXT = '#4fd3bf'        # verb en repòs: verd blavós
TEXT_HOVER = '#ff78d2'  # verb sota el ratolí: magenta
TEXT_OUTLINE = '#03040a'
VERB_LINE = '#bfeee4'   # la frase «Ves a ...»
OPTION = '#d6f5ee'      # opcions de diàleg
OPTION_HOVER = '#ff78d2'

# ─── Geometria (de verbs.gui.json / dialog.gui.json; no es mou res) ─────────
VERBS = [(49, 211, 55), (106, 211, 74), (183, 211, 55), (49, 230, 55), (106, 230, 74), (183, 230, 55),
         (49, 250, 55), (106, 250, 74), (183, 250, 55)]   # (x, y, amplada); alçada 16
VERB_H = 16
INV_X, INV_Y, SLOT_W, SLOT_H, GAP = 252, 210, 49, 27, 3
ARROWS = {'up': (240, 210), 'down': (240, 240)}           # 10×27
MENU = (27, 247, 19)
CANVIA = (3, 211, 43, 32)


def slots():
    for r in range(2):
        for c in range(4):
            yield INV_X + c * (SLOT_W + GAP), INV_Y + r * (SLOT_H + GAP)


# ─── Peces ─────────────────────────────────────────────────────────────────

def body(cv, x0, y0, x1, y1, top=3.2, fall=0.012):
    """El cos de la consola: plàstic fosc mat, amb una trama de punts molt fluixa (com una placa)."""
    for y in range(y0, y1 + 1):
        vy = top - (y - y0) * fall
        for x in range(x0, x1 + 1):
            v = vy + (0.35 if (x % 6 == 0 and y % 6 == 0) else 0) + (hr(902, x // 3, y // 3) - 0.5) * 0.15
            cv.put(x, y, SLATE, v, lit=0)


def key(cv, x0, y0, x1, y1, face=4.4, skirt=2):
    """Una tecla: la cara (amb vora clara a dalt), cantons arrodonits, el faldó fosc a sota i l'ombra."""
    fy1 = y1 - skirt
    for y in range(y0, y1 + 1):
        for x in range(x0, x1 + 1):
            corner = (x in (x0, x1)) and (y in (y0, y1, fy1))
            if corner:
                continue
            if y > fy1:                                   # el faldó
                v = face - 2.4 + (0.4 if x == x0 + 1 else 0)
            elif y == y0:
                v = face + 2.2
            elif x == x0:
                v = face + 1.2
            elif x == x1:
                v = face - 1.0
            elif y == fy1:
                v = face - 0.8
            else:
                v = face + 0.3 - 0.6 * (y - y0) / max(1, fy1 - y0)
            cv.put(x, y, SLATE, v, lit=0)
    for x in range(x0 + 1, x1 + 1):                       # ombra de contacte
        dark(cv, x, y1 + 1, 0.55)
    for y in range(y0 + 1, y1 + 1):
        dark(cv, x1 + 1, y, 0.35)


def plate(cv, x0, y0, x1, y1, face=4.4, flat=False):
    key(cv, x0, y0, x1, y1, face)


def well(cv, x0, y0, x1, y1, face=1.2, brackets=True):
    """Una pantalleta enfonsada: fons gairebé negre, línies d'escaneig, llavi clar a baix i cantoneres de visor."""
    for y in range(y0, y1 + 1):
        for x in range(x0, x1 + 1):
            v = face + (0.35 if (y - y0) % 2 == 0 else 0)
            if y == y0 or x == x0:
                v = 0.0
            elif y == y1:
                v = face + 3.0
            elif x == x1:
                v = face + 2.2
            cv.put(x, y, SLATE, v, lit=0)
    # un reflex de vidre, en diagonal, al cantó de dalt a l'esquerra
    for k in range(5):
        for t in range(3):
            x, y = x0 + 3 + k + t, y0 + 2 + t
            if x < x1 - 1 and y < y1 - 1 and k < 4:
                cv.put(x, y, SLATE, face + 1.6, lit=0)
    if brackets:
        L = 4
        for (cx, cy, dx, dy) in ((x0 + 2, y0 + 2, 1, 1), (x1 - 2, y0 + 2, -1, 1), (x0 + 2, y1 - 2, 1, -1), (x1 - 2, y1 - 2, -1, -1)):
            for i in range(L):
                cv.put(cx + dx * i, cy, TEAL, 2.4 if i else 3.2, lit=0)
                cv.put(cx, cy + dy * i, TEAL, 2.4 if i else 3.2, lit=0)


def dark(cv, x, y, k):
    if 0 <= x < cv.w and 0 <= y < cv.h:
        o = cv.P[x, y]
        if o[3]:
            cv.P[x, y] = mix(o, SLATE[0], k) + (o[3],)


def led(cv, x, y, ramp, on=True):
    """Un LED de 2×2 amb el seu halo."""
    for dx, dy, v in ((0, 0, 6), (1, 0, 5), (0, 1, 5), (1, 1, 4)):
        cv.put(x + dx, y + dy, ramp, v if on else 1.2, lit=0)
    if on:
        cv.glow(x + 1, y + 1, 5, ramp[4], 0.35)


def rivet(cv, x, y, ramp=TEAL, base=4.0):
    led(cv, x, y, ramp)


def slits(cv, x0, x1, ys):
    """Reixeta de ventilació: ranures horitzontals amb vora clara a sota."""
    for y in ys:
        for x in range(x0, x1 + 1):
            end = x in (x0, x1)
            cv.put(x, y, SLATE, 0.2 if not end else 1.0, lit=0)
            cv.put(x, y + 1, SLATE, 4.6 if not end else 3.8, lit=0)


def light_line(cv, x0, x1, y):
    """La línia de llum que separa l'escena de la consola: verd blavós, amb polsos de dades i un tram magenta."""
    for x in range(x0, x1 + 1):
        pulse = (x // 3) % 23 == 0 or (x // 2) % 37 == 0
        v = 4.6 + (1.2 if pulse else 0) + (hr(903, x // 7) - 0.5) * 0.4
        ramp = MAG if 6 <= x <= 40 else TEAL
        cv.put(x, y, ramp, v, lit=0)
        cv.put(x, y + 1, ramp, 2.0, lit=0)
        cv.put(x, y - 1, ramp, 1.2, lit=0)


brass_trim = light_line


def arrow(cv, cx, cy, up, hover, length=13):
    """Fletxa de llum (verd blavós; magenta i amb halo en hover). (cx = columna esquerra del centre)"""
    ramp = MAG if hover else TEAL
    rows = []
    for i, w in enumerate((2, 4, 6, 8)):
        rows.append((cx - w // 2 + 1, cx + w // 2, i))
    for i in range(4, length):
        rows.append((cx, cx + 1, i))
    y0 = cy - length // 2
    for a, b, i in rows:
        y = y0 + i if up else y0 + length - 1 - i
        for x in range(a, b + 1):
            v = 5.4 if x <= cx else 4.4
            if i == 0:
                v = 6.2
            cv.put(x, y, ramp, v, lit=0)
    if hover:
        cv.glow(cx + 0.5, cy, 10, ramp[4], 0.4)


# ─── Barra de verbs ─────────────────────────────────────────────────────────

def verbs_bg():
    cv = Canvas(FW, FH, transparent=True)
    # franja de la frase («Ves a ...»): una barra d'estat fosca
    for y in range(195, 207):
        for x in range(FW):
            cv.put(x, y, SLATE, 0.6 + (0.5 if y == 195 else 0), lit=0)
    body(cv, 0, 209, FW - 1, 269)
    light_line(cv, 0, FW - 1, 207)
    for x in range(FW):
        dark(cv, x, 209, 0.5)
        cv.put(x, 269, SLATE, 0.8, lit=0)
    for y in range(209, 269):
        cv.put(0, y, SLATE, 4.2, lit=0)
        cv.put(FW - 1, y, SLATE, 1.2, lit=0)
    # juntes entre seccions: una ranura fosca amb un fil de llum molt fluix
    for sx in (47, 238, 458):
        for y in range(212, 266):
            cv.put(sx, y, SLATE, 0.3, lit=0)
            cv.put(sx + 1, y, TEAL, 1.2 if (y // 4) % 3 else 2.0, lit=0)
    # botó «Canvia»: ombra al voltant (la imatge és opaca i el tapa)
    x, y, w, h = CANVIA
    for xx in range(x - 1, x + w + 1):
        dark(cv, xx, y - 1, 0.5)
        dark(cv, xx, y + h, 0.6)
    for yy in range(y, y + h):
        dark(cv, x - 1, yy, 0.5)
        dark(cv, x + w, yy, 0.6)
    # sota «Canvia», a l'esquerra del menú: tres LEDs d'estat (connexió, auricular, gravant) i una reixeta
    led(cv, 7, 250, TEAL)
    led(cv, 13, 250, MAG)
    led(cv, 19, 250, TEAL, on=False)
    slits(cv, 6, 21, (256, 260, 264))
    # verbs: tecles
    for vx, vy, vw in VERBS:
        key(cv, vx, vy, vx + vw - 1, vy + VERB_H - 1)
    # fletxes: canals enfonsats
    for ax, ay in ARROWS.values():
        well(cv, ax, ay, ax + 9, ay + 26, face=1.0, brackets=False)
    # inventari: pantalletes
    for sx, sy in slots():
        well(cv, sx, sy, sx + SLOT_W - 1, sy + SLOT_H - 1)
    # dreta: un vúmetre de LEDs i la reixeta
    for k in range(8):
        on = k < 5
        led(cv, 466, 258 - k * 6, MAG if k >= 6 else TEAL, on=on)
    slits(cv, 463, 474, (212, 216))
    return cv.img


def verbs_arrow(which, hover):
    cv = Canvas(FW, FH, transparent=True)
    ax, ay = ARROWS[which]
    if hover:   # el canal s'encén (el fons hi és a sota; aquí només hi ha la claror)
        for y in range(ay + 2, ay + 26):
            for x in range(ax + 2, ax + 9):
                d = abs(y - (ay + 13.5)) / 13
                if 0.55 * (1 - d) > 0.12 + 0.6 * ((x * 5 + y * 3) % 7) / 7:
                    cv.flat(x, y, mix(SLATE[2], MAG[2], 0.5))
    arrow(cv, ax + 4, ay + 13, which == 'up', hover, length=15)
    return cv.img


def menu_button():
    cv = Canvas(FW, FH, transparent=True)
    x, y, s = MENU
    tmp = Canvas(FW, FH)
    body(tmp, x, y, x + s, y + s)
    cv.img.paste(tmp.img.crop((x, y, x + s + 1, y + s + 1)), (x, y))
    cv.P = cv.img.load()
    key(cv, x, y, x + s - 1, y + s - 1, face=4.6)
    for ly in (y + 4, y + 8, y + 12):
        for lx in range(x + 4, x + s - 4):
            cv.put(lx, ly, TEAL, 5.0 if lx < x + s - 6 else 4.0, lit=0)
    out = Image.new('RGBA', (FW, FH), (0, 0, 0, 0))
    out.paste(cv.img.crop((x, y, x + s, y + s)), (x, y))
    return out


def canvia(hover):
    from draw_placeholders import switch_button_image
    out = Image.new('RGBA', (FW, FH), (0, 0, 0, 0))
    out.paste(switch_button_image(hover=hover), (CANVIA[0], CANVIA[1]))
    return out


# ─── Diàleg ─────────────────────────────────────────────────────────────────

DLG_ARROWS = {'up': (3, 205), 'down': (3, 240)}   # canals de 9×25 (botons de 10×25)
DLG_ORIGIN = {'up': (-1, 200), 'down': (-1, 221)}  # on el motor posa el (0, 0) del fotograma retallat


def dialog_bg():
    cv = Canvas(FW, FH, transparent=True)
    body(cv, 0, 197, FW - 1, 269, top=3.0)
    light_line(cv, 0, FW - 1, 195)
    for x in range(FW):
        dark(cv, x, 197, 0.5)
        cv.put(x, 269, SLATE, 0.8, lit=0)
    for y in range(197, 269):
        cv.put(0, y, SLATE, 4.2, lit=0)
        cv.put(FW - 1, y, SLATE, 1.2, lit=0)
    # la pantalla de les opcions
    well(cv, 15, 200, 474, 266, face=0.8)
    for ax, ay in DLG_ARROWS.values():
        well(cv, ax, ay, ax + 8, ay + 24, face=1.0, brackets=False)
    led(cv, 5, 199, TEAL)
    led(cv, 5, 233, MAG)
    return cv.img


def dialog_arrow(which):
    cv = Canvas(FW, FH, transparent=True)
    ax, ay = DLG_ARROWS[which]
    arrow(cv, ax + 3, ay + 12, which == 'up', False, length=13)
    ox, oy = DLG_ORIGIN[which]
    return cv.img.crop((ox, oy, ox + 22, oy + 44))


def dialog_bullet():
    """L'indicador de cada opció: un «>» de terminal, verd blavós."""
    cv = Canvas(44, 22, transparent=True)
    for (x, y, v) in ((19, 8, 5.4), (20, 9, 5.4), (21, 10, 6.0), (20, 11, 4.6), (19, 12, 4.6), (22, 10, 3.0)):
        cv.put(x, y, TEAL, v, lit=0)
    return cv.img


# ─── 9-slice dels menús ─────────────────────────────────────────────────────

def nine_slice():
    """30×20: vores de 7 px (s'estiren en una direcció) i centre pla (s'estira en totes dues).
    Un panell fosc amb vora de llum verd blavós i un punt magenta a cada cantó."""
    img = Image.new('RGBA', (30, 20), (0, 0, 0, 0))
    P = img.load()
    face = SLATE[2]
    ring = [SLATE[0], TEAL[4], TEAL[2], SLATE[0], SLATE[4], SLATE[3]]
    ring_bottom = [SLATE[0], TEAL[3], TEAL[1], SLATE[0], SLATE[1], SLATE[2]]
    for y in range(20):
        for x in range(30):
            d = min(x, y, 29 - x, 19 - y)
            if d < len(ring):
                lo = (19 - y == d) or (29 - x == d)
                col = (ring_bottom if lo else ring)[d]
            else:
                col = face
            P[x, y] = col + (255,)
    for x, y in ((0, 0), (29, 0), (0, 19), (29, 19)):
        P[x, y] = (0, 0, 0, 0)
    for cx, cy in ((3, 3), (26, 3), (3, 16), (26, 16)):
        P[cx, cy] = MAG[4] + (255,)
    return img


# ─── Fulls ──────────────────────────────────────────────────────────────────

def frame_json(name, i, x, y, w, h, trimmed=False, src=(0, 0), size=(FW, FH)):
    return {f'{name} {i}.aseprite': {
        'frame': {'x': x, 'y': y, 'w': w, 'h': h}, 'rotated': False, 'trimmed': trimmed,
        'spriteSourceSize': {'x': src[0], 'y': src[1], 'w': w, 'h': h},
        'sourceSize': {'w': size[0], 'h': size[1]}, 'duration': 100}}


def write_sheet(d, name, sheet, frames, tags, old_meta):
    meta = {
        'app': 'https://www.aseprite.org/', 'version': (old_meta or {}).get('version', 'hd/gui.py'),
        'image': f'{name}.png', 'format': 'RGBA8888', 'size': {'w': sheet.width, 'h': sheet.height}, 'scale': '1',
        'frameTags': [{'name': t, 'from': i, 'to': i, 'direction': 'forward', 'color': '#000000ff'} for t, i in tags],
        'layers': (old_meta or {}).get('layers', []), 'slices': [],
    }
    sheet.save(d / f'{name}.png')
    (d / f'{name}.json').write_text(json.dumps({'frames': frames, 'meta': meta}, indent=2) + '\n')


def old(d, name):
    j = d / f'{name}.json'
    p = d / f'{name}.png'
    return (json.loads(j.read_text())['meta'] if j.exists() else None,
            Image.open(p).convert('RGBA') if p.exists() else None)


def build_verbs(game):
    d = game / 'assets/images/guis/verbs'
    meta, prev = old(d, 'verbs')
    sheet = Image.new('RGBA', (FW * 3, FH * 3), (0, 0, 0, 0))
    if prev is not None:   # fotograma 0: captura de referència de la plantilla, es conserva
        sheet.paste(prev.crop((0, 0, FW, FH)), (0, 0))
    imgs = [None, verbs_bg(), verbs_arrow('up', False), verbs_arrow('down', False), menu_button(),
            verbs_arrow('up', True), verbs_arrow('down', True), canvia(False), canvia(True)]
    tags = ['VerbsBG', 'UpBtn', 'DownBtn', 'MenuBtn', 'UpBtn-hover', 'DownBtn-hover', 'CanviaBtn', 'CanviaBtn-hover']
    frames = {}
    for i, im in enumerate(imgs):
        x, y = (i % 3) * FW, (i // 3) * FH
        if im is not None:
            sheet.paste(im, (x, y))
        frames.update(frame_json('verbs', i, x, y, FW, FH))
    write_sheet(d, 'verbs', sheet, frames, [(t, i + 1) for i, t in enumerate(tags)], meta)
    return sheet


def build_dialog(game):
    d = game / 'assets/images/guis/dialog'
    meta, prev = old(d, 'dialog')
    sheet = Image.new('RGBA', (960, 284), (0, 0, 0, 0))
    if prev is not None:
        sheet.paste(prev.crop((0, 0, 480, 284)), (0, 0))
    bg = Image.new('RGBA', (480, 109), (0, 0, 0, 0))
    bg.paste(dialog_bg().crop((0, 175, 480, 270)), (0, 0))
    sheet.paste(bg, (480, 0))
    sheet.paste(dialog_arrow('up'), (480, 109))
    sheet.paste(dialog_arrow('down'), (502, 109))
    sheet.paste(dialog_bullet(), (524, 109))
    frames = {}
    frames.update(frame_json('dialog', 0, 0, 0, 480, 284, True, (0, 0)))
    frames.update(frame_json('dialog', 1, 480, 0, 480, 109, True, (0, 175)))
    frames.update(frame_json('dialog', 2, 480, 109, 22, 44, True, (0, 196)))
    frames.update(frame_json('dialog', 3, 502, 109, 22, 44, True, (0, 218)))
    frames.update(frame_json('dialog', 4, 524, 109, 44, 22, True, (0, 196)))
    write_sheet(d, 'dialog', sheet, frames, [('VerbsBG', 1), ('UpBtn', 2), ('DownBtn', 3), ('Bullet', 4)], meta)
    return sheet


def build_menus(game):
    ns = nine_slice()
    base = game / 'assets/images/guis'
    for g in ('display-text', 'game-menu', 'save-menu', 'load-menu'):
        p = base / g / f'{g}.png'
        if p.exists():
            img = Image.new('RGBA', (32, 32), (0, 0, 0, 0))
            img.paste(ns, (0, 0))
            img.save(p)
    p = base / 'settings-menu/settings-menu.png'
    if p.exists():
        img = Image.open(p).convert('RGBA')
        img.paste(Image.new('RGBA', (70, 20), (0, 0, 0, 0)), (0, 0))
        img.paste(ns, (0, 0))
        img.save(p)


def apply_text_colors(game):
    """Els colors del text dels botons de verbs, de la frase i de les opcions de diàleg."""
    guis = game / 'guis'
    vp = guis / 'verbs/verbs.gui.json'
    if vp.exists():
        d = json.loads(vp.read_text())
        for c in d.get('controls', []):
            if c.get('type') == 'button' and c.get('text') and c.get('font') == 'suma-negreta':
                c['textColor'] = TEXT
                c['textColorStates'] = {'hover': TEXT_HOVER}
                c['textOutline'] = {'enabled': True, 'color': TEXT_OUTLINE, 'sides': 'bottomRight'}
            if c.get('id') == 'verbLineText':
                c['color'] = VERB_LINE
        vp.write_text(json.dumps(d, indent=2, ensure_ascii=False) + '\n')
    dp = guis / 'dialog/dialog.gui.json'
    if dp.exists():
        d = json.loads(dp.read_text())
        for c in d.get('controls', []):
            if c.get('id') == 'Dialog-Option':
                c['textColor'] = OPTION
                c['textColorStates'] = {'hover': OPTION_HOVER}
        dp.write_text(json.dumps(d, indent=2, ensure_ascii=False) + '\n')


def main(game):
    build_verbs(game)
    build_dialog(game)
    build_menus(game)
    apply_text_colors(game)
    print('✔ interfície HD: verbs, diàleg i menús')


if __name__ == '__main__':
    main(Path(sys.argv[1]).resolve())
