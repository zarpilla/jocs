#!/usr/bin/env python3
"""
Interfície del joc en pixel art HD: barra de verbs, quadre d'opcions de diàleg i el fons
9-slice dels menús (menú del joc, desa, carrega, configuració i text en pantalla).

Genera els fulls d'Aseprite (PNG + JSON) amb la mateixa estructura que les plantilles de Benne
(mateixos fotogrames, mides i etiquetes), i només hi canvia el dibuix. Estil: planxa de metall
blau-pissarra, neutra entre la fàbrica (1900) i La Gavina, amb reblons i un fil de llautó discret.

Ús (idempotent: es pot tornar a executar sempre que es vulgui):

    python3 adapters/benne/tools/hd/gui.py suma-zero/src/game

  - verbs.png/.json: fotograma 0 (captura de referència de la plantilla) es conserva tal qual;
    1-6 (fons, fletxes, menú) es dibuixen aquí; 7-8 (botó «Canvia») surten de
    `switch_button_image()` de draw_placeholders.py, igual que fa `add_switch_button()`
    (que, si es torna a executar, hi posa exactament el mateix).
  - dialog.png/.json: fotograma 0 es conserva; 1 (fons), 2-3 (fletxes) i 4 (pic) es dibuixen.
  - display-text, game-menu, save-menu, load-menu: el 9-slice de 30×20 (el JSON no es toca).
  - settings-menu: només el 9-slice del fotograma 0 (caselles i lliscadors es queden).
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
# Metall blau-pissarra (fosc → clar) i llautó apagat.
SLATE = [(7, 9, 14), (12, 15, 22), (18, 22, 31), (25, 30, 41), (33, 39, 52), (43, 50, 65), (55, 63, 80),
         (70, 79, 97), (90, 100, 118), (118, 128, 146), (156, 166, 180)]
BRASS = [(30, 22, 14), (58, 40, 22), (92, 66, 34), (130, 96, 48), (168, 128, 64), (202, 162, 88),
         (230, 200, 130), (248, 232, 186)]

# Colors del text (els posa el motor): els fa servir la previsualització i es poden copiar als .gui.json.
TEXT = '#9fb0c2'        # verb en repòs: acer clar
TEXT_HOVER = '#f2c66d'  # verb sota el ratolí: llautó encès
TEXT_OUTLINE = '#07090e'
VERB_LINE = '#c8d3de'   # la frase «Ves a ...»

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


# ─── Peces ──────────────────────────────────────────────────────────────────

def body(cv, x0, y0, x1, y1, top=3.75, fall=0.011):
    """Planxa de metall raspallat: una mica més clara a dalt, amb vetes horitzontals suaus.
    (Nivell n + 0.5 = to pla; la resta es trama.)"""
    for y in range(y0, y1 + 1):
        vy = top - (y - y0) * fall + (hr(901, y) - 0.5) * 0.12
        for x in range(x0, x1 + 1):
            cv.put(x, y, SLATE, vy + (0.25 if hr(902, x // 31, y) > 0.93 else 0), lit=0)


def plate(cv, x0, y0, x1, y1, face=4.5, flat=False):
    """Placa en relleu (llum de dalt a l'esquerra): bisell clar a dalt/esquerra, fosc a baix/dreta."""
    h = max(1, y1 - y0)
    for y in range(y0, y1 + 1):
        for x in range(x0, x1 + 1):
            v = face + (0 if flat else 0.45 - 0.75 * (y - y0) / h)
            if y == y0:
                v = face + 3
            elif x == x0:
                v = face + 2
            elif y == y1:
                v = face - 3
            elif x == x1:
                v = face - 2
            elif y == y0 + 1:
                v = face + 1
            cv.put(x, y, SLATE, v, lit=0)
    cv.put(x1, y0, SLATE, face + 0.6, lit=0)
    cv.put(x0, y1, SLATE, face - 0.8, lit=0)
    # ombra de contacte a sota i a la dreta
    for x in range(x0 + 1, x1 + 2):
        dark(cv, x, y1 + 1, 0.5)
    for y in range(y0 + 1, y1 + 1):
        dark(cv, x1 + 1, y, 0.3)


def well(cv, x0, y0, x1, y1, face=1.6):
    """Casella enfonsada: ombra a dalt/esquerra, llavi clar a baix/dreta, fons fosc amb reflex de baix."""
    h = max(1, y1 - y0)
    for y in range(y0, y1 + 1):
        for x in range(x0, x1 + 1):
            v = face + 0.7 * (y - y0) / h
            if y == y0 or x == x0:
                v = 0.2
            elif y == y1:
                v = face + 3.4
            elif x == x1:
                v = face + 2.6
            elif y == y0 + 1 or x == x0 + 1:
                v = face - 0.7
            cv.put(x, y, SLATE, v, lit=0)
    cv.put(x1, y0, SLATE, face + 0.6, lit=0)
    cv.put(x0, y1, SLATE, face + 0.6, lit=0)


def dark(cv, x, y, k):
    if 0 <= x < cv.w and 0 <= y < cv.h:
        o = cv.P[x, y]
        if o[3]:
            cv.P[x, y] = mix(o, SLATE[0], k) + (o[3],)


def rivet(cv, x, y, ramp=SLATE, base=7.5):
    """Rebló de 3×3 amb llum de dalt a l'esquerra i ombra a baix a la dreta."""
    for dx, dy, v in ((1, 0, base + 2), (0, 1, base + 1), (1, 1, base), (2, 1, base - 2), (1, 2, base - 3)):
        cv.put(x + dx, y + dy, ramp, v, lit=0)
    dark(cv, x + 2, y + 2, 0.7)
    dark(cv, x + 3, y + 1, 0.35)
    dark(cv, x + 1, y + 3, 0.35)


def slits(cv, x0, x1, ys):
    """Reixeta de ventilació: ranures horitzontals amb vora clara a sota."""
    for y in ys:
        for x in range(x0, x1 + 1):
            end = x in (x0, x1)
            cv.put(x, y, SLATE, 0.3 if not end else 1.2, lit=0)
            cv.put(x, y + 1, SLATE, 5.0 if not end else 4.2, lit=0)


def brass_trim(cv, x0, x1, y):
    """Fil de llautó: dues línies (llum a dalt), amb brillantor que varia una mica."""
    for x in range(x0, x1 + 1):
        g = 0.35 * (hr(903, x // 9) - 0.5)
        cv.put(x, y, BRASS, 3.6 + g, lit=0)
        cv.put(x, y + 1, BRASS, 1.7 + g, lit=0)


def arrow(cv, cx, cy, up, hover, length=13):
    """Fletxa amb volum: cap de 4 files i tija; costat esquerre clar, dret fosc. (cx = columna esquerra del centre)"""
    ramp = BRASS if hover else SLATE
    lit, mid, shd, top = ((6.5, 5.5, 3.5, 7.5) if hover else (8.5, 7.5, 5.5, 9.5))
    rows = []
    for i, w in enumerate((2, 4, 6, 8)):
        rows.append((cx - w // 2 + 1, cx + w // 2, i))
    for i in range(4, length):
        rows.append((cx - 1, cx + 2, i))
    y0 = cy - length // 2
    pts = []
    for a, b, i in rows:
        y = y0 + i if up else y0 + length - 1 - i
        for x in range(a, b + 1):
            pts.append((x, y))
            left = x <= cx
            v = lit if left else mid
            if i == 3 and x not in range(cx - 1, cx + 3):
                v = shd       # vora de sota del cap
            if i >= 4 and x == cx + 2:
                v = shd
            if (up and i == 0) or x == a and i < 3:
                v = top
            if not up and i == 0:
                v = mid
            cv.put(x, y, ramp, v, lit=0)
    s = set(pts)
    for x, y in pts:   # ombra projectada a baix a la dreta
        if (x + 1, y + 1) not in s:
            dark(cv, x + 1, y + 1, 0.55)
    if hover:
        cv.glow(cx + 0.5, cy, 9, BRASS[4], 0.35)


# ─── Barra de verbs ─────────────────────────────────────────────────────────

def verbs_bg():
    cv = Canvas(FW, FH, transparent=True)
    # franja de la frase («Ves a ...»)
    for y in range(195, 207):
        for x in range(FW):
            cv.put(x, y, SLATE, 0.35 + (0.4 if y == 206 else 0), lit=0)
    body(cv, 0, 209, FW - 1, 269)
    brass_trim(cv, 0, FW - 1, 207)
    for x in range(FW):
        dark(cv, x, 209, 0.45)
        cv.put(x, 269, SLATE, 1.4, lit=0)
    for y in range(209, 269):
        cv.put(0, y, SLATE, 4.6, lit=0)
        cv.put(FW - 1, y, SLATE, 1.6, lit=0)
    # juntes entre seccions (ranura fosca + vora clara)
    for sx in (47, 238, 458):
        for y in range(210, 268):
            cv.put(sx, y, SLATE, 0.6, lit=0)
            cv.put(sx + 1, y, SLATE, 5.0, lit=0)
    # botó «Canvia»: ombra al voltant (la imatge és opaca i el tapa)
    x, y, w, h = CANVIA
    for xx in range(x - 1, x + w + 1):
        dark(cv, xx, y - 1, 0.5)
        dark(cv, xx, y + h, 0.6)
    for yy in range(y, y + h):
        dark(cv, x - 1, yy, 0.5)
        dark(cv, x + w, yy, 0.6)
    # zona lliure sota «Canvia», a l'esquerra del menú: reixeta i reblons
    slits(cv, 6, 21, (251, 255, 259))
    rivet(cv, 6, 263)
    rivet(cv, 19, 263)
    # verbs
    for vx, vy, vw in VERBS:
        plate(cv, vx, vy, vx + vw - 1, vy + VERB_H - 1)
    # fletxes: canals enfonsats
    for ax, ay in ARROWS.values():
        well(cv, ax, ay, ax + 9, ay + 26, face=1.4)
    # inventari
    for sx, sy in slots():
        well(cv, sx, sy, sx + SLOT_W - 1, sy + SLOT_H - 1)
    # dreta: reblons i reixeta
    rivet(cv, 467, 212)
    rivet(cv, 467, 262)
    slits(cv, 463, 474, range(222, 256, 5))
    return cv.img


def verbs_arrow(which, hover):
    cv = Canvas(FW, FH, transparent=True)
    ax, ay = ARROWS[which]
    if hover:   # el canal s'encén una mica (el fons hi és a sota; aquí només hi ha el reflex)
        for y in range(ay + 2, ay + 26):
            for x in range(ax + 2, ax + 9):
                d = abs(y - (ay + 13.5)) / 13
                if 0.55 * (1 - d) > 0.12 + 0.6 * ((x * 5 + y * 3) % 7) / 7:
                    cv.flat(x, y, mix(SLATE[2], BRASS[2], 0.6))
    arrow(cv, ax + 4, ay + 13, which == 'up', hover, length=15)
    return cv.img


def menu_button():
    cv = Canvas(FW, FH, transparent=True)
    x, y, s = MENU
    # plaqueta en relleu amb tres línies (menú)
    tmp = Canvas(FW, FH)
    body(tmp, x, y, x + s, y + s)
    cv.img.paste(tmp.img.crop((x, y, x + s + 1, y + s + 1)), (x, y))
    cv.P = cv.img.load()
    plate(cv, x, y, x + s - 1, y + s - 1, face=4.6)
    for ly in (y + 5, y + 9, y + 13):
        for lx in range(x + 4, x + s - 4):
            cv.put(lx, ly - 1, SLATE, 2.0, lit=0)
            cv.put(lx, ly, SLATE, 8.6 if lx < x + s - 6 else 7.6, lit=0)
            cv.put(lx, ly + 1, SLATE, 3.0, lit=0)
    # treu el que sobresurt (ombra) fora dels 19×19
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
    body(cv, 0, 197, FW - 1, 269, top=3.3)
    brass_trim(cv, 0, FW - 1, 195)
    for x in range(FW):
        dark(cv, x, 197, 0.45)
        cv.put(x, 269, SLATE, 1.4, lit=0)
    for y in range(197, 269):
        cv.put(0, y, SLATE, 4.6, lit=0)
        cv.put(FW - 1, y, SLATE, 1.6, lit=0)
    # panell de text enfonsat
    well(cv, 15, 200, 474, 266, face=1.0)
    for ax, ay in DLG_ARROWS.values():
        well(cv, ax, ay, ax + 8, ay + 24, face=1.4)
    rivet(cv, 5, 199)
    rivet(cv, 5, 233)
    return cv.img


def dialog_arrow(which):
    cv = Canvas(FW, FH, transparent=True)
    ax, ay = DLG_ARROWS[which]
    arrow(cv, ax + 3, ay + 12, which == 'up', False, length=13)
    ox, oy = DLG_ORIGIN[which]
    return cv.img.crop((ox, oy, ox + 22, oy + 44))


def dialog_bullet():
    cv = Canvas(44, 22, transparent=True)
    # botó de llautó rodó (6×6)
    rows = ['.abb.', 'abccd', 'bccdd', 'bcdde', '.dde.']
    lv = {'a': 6.6, 'b': 5.6, 'c': 4.6, 'd': 3.4, 'e': 2.2}
    for j, r in enumerate(rows):
        for i, ch in enumerate(r):
            if ch in lv:
                cv.put(19 + i, 8 + j, BRASS, lv[ch], lit=0)
    for x, y in ((24, 10), (24, 11), (24, 12), (22, 13), (23, 13), (20, 13), (21, 13)):
        cv.flat(x, y, (6, 8, 12))
    cv.flat(24, 13, (6, 8, 12))
    return cv.img


# ─── 9-slice dels menús ─────────────────────────────────────────────────────

def nine_slice():
    """30×20: vores de 7 px (s'estiren en una direcció) i centre pla (s'estira en totes dues)."""
    img = Image.new('RGBA', (30, 20), (0, 0, 0, 0))
    P = img.load()
    face = SLATE[2]
    # anells des de fora: contorn, llautó clar, llautó fosc, ranura, bisell, cara
    ring = [SLATE[0], BRASS[4], BRASS[2], SLATE[0], SLATE[5], SLATE[3]]
    ring_bottom = [SLATE[0], BRASS[2], BRASS[1], SLATE[0], SLATE[1], SLATE[2]]
    for y in range(20):
        for x in range(30):
            d = min(x, y, 29 - x, 19 - y)
            if d < len(ring):
                lo = (19 - y == d) or (29 - x == d)
                col = (ring_bottom if lo else ring)[d]
            else:
                col = face
            P[x, y] = col + (255,)
    # cantonades arrodonides
    for x, y in ((0, 0), (29, 0), (0, 19), (29, 19)):
        P[x, y] = (0, 0, 0, 0)
    # reblons de llautó a les cantonades (dins els 7×7)
    for cx, cy in ((2, 2), (25, 2), (2, 15), (25, 15)):
        for dx, dy, c in ((1, 0, BRASS[6]), (0, 1, BRASS[5]), (1, 1, BRASS[4]), (2, 1, BRASS[2]), (1, 2, BRASS[1])):
            P[cx + dx, cy + dy] = c + (255,)
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


def main(game):
    build_verbs(game)
    build_dialog(game)
    build_menus(game)
    print('✔ interfície HD: verbs, diàleg i menús')


if __name__ == '__main__':
    main(Path(sys.argv[1]).resolve())
