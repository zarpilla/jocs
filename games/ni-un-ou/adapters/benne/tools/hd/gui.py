#!/usr/bin/env python3
"""
Interfície del joc en pixel art HD: barra de verbs, quadre d'opcions de diàleg i el fons
9-slice dels menús (menú del joc, desa, carrega, configuració i text en pantalla).

Genera els fulls d'Aseprite (PNG + JSON) amb la mateixa estructura que les plantilles de Benne
(mateixos fotogrames, mides i etiquetes), i només hi canvia el dibuix. Estil de Ni un ou (la maqueta
guio/art/mostra/sala_maquines.py): planxa de vaixell pintada de blau marí, amb reblons; una corda trenada
a dalt; els verbs són plaques de planxa amb text crema (taronja sota el ratolí); les caselles, buits foscos
amb cantoneres de llautó; el botó «Canvia», un ull de bou amb la cara de l'altra protagonista.

Ús (idempotent: es pot tornar a executar sempre que es vulgui):

    python3 adapters/benne/tools/hd/gui.py ni-un-ou/src/game

  - verbs.png/.json: fotograma 0 (captura de referència de la plantilla) es conserva tal qual;
    1-6 (fons, fletxes, menú) i 7-8 (botó «Canvia»: l'ull de bou buit, normal i hover) es dibuixen aquí;
    9-10 (`CaraIri`, `CaraVet`) són les cares que es veuen dins l'ull de bou: dos controls `image` de
    verbs.gui.json que verbs.gui.ts mostra o amaga segons qui juga (es veu la cara de l'altra).
    Es treu la marca `.canvia-provisional`, perquè el sync no hi torni a posar el botó provisional.
  - dialog.png/.json: fotograma 0 es conserva; 1 (fons), 2-3 (fletxes) i 4 (indicador) es dibuixen.
  - display-text, game-menu, save-menu, load-menu: el 9-slice de 30×20 (el JSON no es toca).
  - settings-menu: el 9-slice del fotograma 0; caselles i lliscadors es queden, amb el verd blavós passat a llautó.
  - els botons dels menús: plaques de cada mida (etiquetes `key-…`).
  - els colors del text dels .gui.json (verbs, frase, opcions de diàleg) es posen als d'aquí.
"""
import json
import math
import sys
from pathlib import Path

from PIL import Image

TOOLS = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(TOOLS))
from hd.pix import Canvas, GOLD, hr, mix  # noqa: E402
from hd import personatges  # noqa: E402

FW, FH = 480, 270

# ─── Paleta (la de la maqueta) ──────────────────────────────────────────────
NAVYB = [(3, 6, 12), (6, 10, 20), (9, 15, 28), (13, 21, 38), (18, 29, 50), (25, 39, 64), (34, 51, 80),
         (46, 66, 98), (62, 86, 120)]                       # planxa pintada de blau marí
ROPE = [(40, 28, 16), (86, 64, 38), (140, 110, 70), (196, 166, 116), (232, 210, 166)]   # corda (i fletxes)
BRASS = GOLD                                                # llautó: cantoneres, ull de bou
HOT = [(60, 22, 8), (120, 50, 14), (190, 90, 26), (240, 132, 46), (255, 170, 92), (255, 214, 160)]   # taronja
GLASS = [(6, 14, 22), (10, 24, 36), (18, 40, 56), (30, 60, 80), (52, 88, 108)]       # vidre de l'ull de bou

# Colors del text (els posa el motor): es copien als .gui.json (vegeu `apply_text_colors`).
TEXT = '#e2d6b4'        # verb en repòs: crema
TEXT_HOVER = '#ff963c'  # verb sota el ratolí: taronja
TEXT_OUTLINE = '#03060c'
VERB_LINE = '#cee6de'   # la frase «Ves a ...»
OPTION = '#e2d6b4'      # opcions de diàleg
OPTION_HOVER = '#ff963c'

# ─── Geometria (de verbs.gui.json / dialog.gui.json; no es mou res) ─────────
VERBS = [(49, 211, 55), (106, 211, 74), (183, 211, 55), (49, 230, 55), (106, 230, 74), (183, 230, 55),
         (49, 250, 55), (106, 250, 74), (183, 250, 55)]   # (x, y, amplada); alçada 16
VERB_H = 16
INV_X, INV_Y, SLOT_W, SLOT_H, GAP = 252, 210, 49, 27, 3
ARROWS = {'up': (240, 210), 'down': (240, 240)}           # 10×27
MENU = (27, 247, 19)
CANVIA = (3, 211, 43, 32)
PORT = (24, 227)                                          # centre de l'ull de bou
FACE_AT = (12, 214)                                       # on va la cara (25×26)
STRIP, ROPE_Y = 195, 205                                  # franja de la frase; corda (3 px)


def slots():
    for r in range(2):
        for c in range(4):
            yield INV_X + c * (SLOT_W + GAP), INV_Y + r * (SLOT_H + GAP)


# ─── Peces ─────────────────────────────────────────────────────────────────

def box(cv, x0, y0, x1, y1, ramp, lvl, edge=True):
    """Capsa plana: llum a dalt i a l'esquerra, ombra a baix i a la dreta."""
    cv.rect(x0, y0, x1, y1, ramp, lvl, lit=0)
    if edge:
        cv.hline(x0, x1, y0, ramp, lvl + 1.2, lit=0)
        cv.vline(x0, y0, y1, ramp, lvl + 0.7, lit=0)
        cv.hline(x0, x1, y1, ramp, lvl - 1.4, lit=0)
        cv.vline(x1, y0, y1, ramp, lvl - 1.0, lit=0)


def dark(cv, x, y, k):
    if 0 <= x < cv.w and 0 <= y < cv.h:
        o = cv.P[x, y]
        if o[3]:
            cv.P[x, y] = mix(o, NAVYB[0], k) + (o[3],)


def rivet(cv, x, y, lvl=6.6):
    """Un rebló: punt clar i ombra a baix a la dreta."""
    cv.put(x, y, NAVYB, lvl, lit=0)
    cv.put(x + 1, y + 1, NAVYB, 1.0, lit=0)


def body(cv, y0, y1=FH - 1):
    """La planxa: blau marí amb una mica de textura de pintura vella."""
    for y in range(y0, y1 + 1):
        for x in range(FW):
            cv.put(x, y, NAVYB, 3.0 - (y - y0) * 0.012 + (hr(x // 3, y // 4) - 0.5) * 0.3, lit=0)


def rope(cv, y):
    """Corda trenada de 3 px, de punta a punta."""
    for x in range(FW):
        for dy in range(3):
            ph = (x + dy * 2) % 6
            cv.put(x, y + dy, ROPE, 3.4 - abs(ph - 2.5) * 0.6 - dy * 0.3, lit=0)
    for x in range(FW):
        dark(cv, x, y + 3, 0.5)                              # l'ombra de la corda sobre la planxa


def seam(cv, x, y0, y1):
    """Junta entre dues planxes, amb una filera de reblons."""
    for y in range(y0, y1 + 1):
        cv.put(x, y, NAVYB, 1.0, lit=0)
        cv.put(x + 1, y, NAVYB, 4.2, lit=0)
    for y in range(y0 + 4, y1 - 2, 9):
        rivet(cv, x, y)


def plate(cv, x0, y0, x1, y1, face=4.4, rivets=True):
    """Placa de planxa (un verb, un botó): capsa, filet de llum i quatre reblons."""
    box(cv, x0, y0, x1, y1, NAVYB, face)
    cv.hline(x0 + 1, x1 - 1, y0 + 1, NAVYB, face + 1.0, lit=0)
    if rivets and x1 - x0 >= 12 and y1 - y0 >= 10:
        for bx, by in ((x0 + 2, y0 + 2), (x1 - 2, y0 + 2), (x0 + 2, y1 - 2), (x1 - 2, y1 - 2)):
            cv.put(bx, by, NAVYB, face + 2.2, lit=0)
    for x in range(x0 + 1, x1 + 2):                          # ombra de contacte
        dark(cv, x, y1 + 1, 0.45)
    for y in range(y0 + 1, y1 + 1):
        dark(cv, x1 + 1, y, 0.3)


def corners(cv, x0, y0, x1, y1, n=4):
    """Cantoneres de llautó."""
    for (cx, cy, sx, sy) in ((x0, y0, 1, 1), (x1, y0, -1, 1), (x0, y1, 1, -1), (x1, y1, -1, -1)):
        for i in range(n):
            cv.put(cx + sx * i, cy, BRASS, 4.0 if sy > 0 else 3.2, lit=0)
            cv.put(cx, cy + sy * i, BRASS, 3.4 if sx > 0 else 2.8, lit=0)


def well(cv, x0, y0, x1, y1, face=1.6, brass=True):
    """Un buit fosc (casella, panell d'opcions): vora d'ombra a dalt i cantoneres de llautó."""
    box(cv, x0, y0, x1, y1, NAVYB, face)
    cv.hline(x0 + 1, x1 - 1, y0 + 1, NAVYB, face - 1.0, lit=0)
    if brass:
        corners(cv, x0 + 1, y0 + 1, x1 - 1, y1 - 1)


def arrow(cv, cx, cy, up, hover, length=13):
    """Fletxa de corda (taronja en hover). cx = columna esquerra del centre."""
    ramp = HOT if hover else ROPE
    rows = [(cx - w // 2 + 1, cx + w // 2, i) for i, w in enumerate((2, 4, 6, 8))]
    rows += [(cx, cx + 1, i) for i in range(4, length)]
    y0 = cy - length // 2
    for a, b, i in rows:
        y = y0 + i if up else y0 + length - 1 - i
        for x in range(a, b + 1):
            v = 3.8 if x <= cx else 3.0
            if i == 0:
                v = 4.4
            cv.put(x, y, ramp, v - (0.2 * i if i < 4 else 0.6), lit=0)
    if hover:
        cv.glow(cx + 0.5, cy, 9, HOT[3], 0.3)


# ─── Barra de verbs ─────────────────────────────────────────────────────────

def verbs_bg():
    cv = Canvas(FW, FH, transparent=True)
    cv.rect(0, STRIP, FW - 1, ROPE_Y - 1, NAVYB, 0.6, lit=0)    # franja fosca de la frase
    body(cv, ROPE_Y)
    rope(cv, ROPE_Y)
    for x in range(8, FW, 40):                                  # reblons de la vora de baix
        rivet(cv, x, 266, 5.0)
    seam(cv, 47, 210, 266)
    seam(cv, 461, 210, 266)
    # a la dreta: una plaqueta de llautó amb tres reblons
    box(cv, 466, 214, 474, 262, BRASS, 1.6)
    cv.vline(467, 215, 261, BRASS, 2.6, lit=0)
    for y in (219, 238, 257):
        cv.put(470, y, BRASS, 4.4, lit=0)
        cv.put(471, y + 1, BRASS, 0.4, lit=0)
    # sota «Canvia», a l'esquerra del menú: dos reblons
    rivet(cv, 8, 252)
    rivet(cv, 8, 261)
    # verbs: plaques
    for vx, vy, vw in VERBS:
        plate(cv, vx, vy, vx + vw - 1, vy + VERB_H - 1)
    # fletxes de l'inventari: plaques (la fletxa és al fotograma de cada botó)
    for ax, ay in ARROWS.values():
        box(cv, ax, ay, ax + 9, ay + 26, NAVYB, 4.0)
    # caselles
    for sx, sy in slots():
        well(cv, sx, sy, sx + SLOT_W - 1, sy + SLOT_H - 1)
    return cv.img


def verbs_arrow(which, hover):
    cv = Canvas(FW, FH, transparent=True)
    ax, ay = ARROWS[which]
    if hover:   # la placa s'il·lumina una mica
        box(cv, ax, ay, ax + 9, ay + 26, NAVYB, 4.8)
    arrow(cv, ax + 4, ay + 13, which == 'up', hover, length=11)
    return cv.img


def menu_button():
    cv = Canvas(FW, FH, transparent=True)
    x, y, s = MENU
    box(cv, x, y, x + s - 1, y + s - 1, NAVYB, 4.0)
    cv.hline(x + 1, x + s - 2, y + 1, NAVYB, 5.0, lit=0)
    for yy in (y + 4, y + 9, y + 14):
        cv.hline(x + 4, x + s - 6, yy, ROPE, 3.8, lit=0)
        cv.hline(x + 5, x + s - 5, yy + 1, NAVYB, 1.6, lit=0)
    return cv.img


def porthole(cv, hover=False):
    """L'ull de bou del botó «Canvia»: placa, anella de llautó amb sis cargols i el vidre fosc."""
    x, y, w, h = CANVIA
    box(cv, x, y, x + w - 1, y + h - 1, NAVYB, 4.2 if hover else 3.6)
    cv.hline(x + 1, x + w - 2, y + 1, NAVYB, 5.0 if hover else 4.6, lit=0)
    for bx, by in ((x + 2, y + 2), (x + w - 3, y + 2), (x + 2, y + h - 3), (x + w - 3, y + h - 3)):
        cv.put(bx, by, NAVYB, 6.4, lit=0)
    cx, cy = PORT
    lift = 0.8 if hover else 0.0
    cv.disc(cx + 0.5, cy + 0.5, 14, 14, NAVYB, 1.0, lit=0)                       # ombra de l'anella
    cv.disc(cx, cy, 13, 13, BRASS, lambda nx, ny: 3.6 + lift - nx - ny * 1.2, lit=0)
    cv.disc(cx, cy, 10.5, 10.5, BRASS, lambda nx, ny: 2.2 + lift + nx + ny * 1.2, lit=0)   # bisell cap endins
    cv.disc(cx, cy, 10, 10, GLASS, lambda nx, ny: 1.4 + (0.6 if hover else 0) - ny, lit=0)
    for a in range(0, 360, 60):
        bx = cx + round(math.cos(math.radians(a + 30)) * 11.6)
        by = cy + round(math.sin(math.radians(a + 30)) * 11.6)
        cv.put(bx, by, BRASS, 5.4 + lift, lit=0)
        cv.put(bx + 1, by + 1, BRASS, 0.6, lit=0)
    if hover:
        cv.glow(cx - 6, cy - 7, 8, HOT[4], 0.35)


def canvia(hover):
    cv = Canvas(FW, FH, transparent=True)
    porthole(cv, hover)
    return cv.img


def canvia_button(hover=False):
    """El botó sol (43×32), per a draw_placeholders.py."""
    x, y, w, h = CANVIA
    return canvia(hover).crop((x, y, x + w, y + h))


FACES = {'iri': personatges.iri, 'vet': personatges.vet}


def face_porthole(who):
    """La cara d'una protagonista retallada en rodó, amb un reflex al vidre (25×26)."""
    face = personatges.cara(FACES[who])
    out = Image.new('RGBA', (25, 26), (0, 0, 0, 0))
    src, P = face.load(), out.load()
    for y in range(26):
        for x in range(25):
            if (x - 12) ** 2 + (y - 13) ** 2 <= 10 ** 2 and src[x, y + 2][3]:
                r, g, b, a = src[x, y + 2]
                P[x, y] = (int(r * 0.92), int(g * 0.95), int(b), a)     # darrere el vidre, una mica blavós
    for (x, y) in ((6, 7), (7, 6), (8, 5), (6, 9)):                       # el reflex
        if P[x, y][3]:
            P[x, y] = mix(P[x, y], (210, 230, 240), 0.45) + (255,)
    return out


def face_frame(who):
    out = Image.new('RGBA', (FW, FH), (0, 0, 0, 0))
    out.alpha_composite(face_porthole(who), FACE_AT)
    return out


# ─── Diàleg ─────────────────────────────────────────────────────────────────

DLG_ARROWS = {'up': (3, 205), 'down': (3, 240)}   # canals de 9×25 (botons de 10×25)
DLG_ORIGIN = {'up': (-1, 200), 'down': (-1, 221)}  # on el motor posa el (0, 0) del fotograma retallat


def dialog_bg():
    cv = Canvas(FW, FH, transparent=True)
    body(cv, 195)
    rope(cv, 195)
    well(cv, 15, 200, 474, 266, face=1.2)                     # el panell de les opcions
    for ax, ay in DLG_ARROWS.values():
        box(cv, ax, ay, ax + 8, ay + 24, NAVYB, 4.0)
    rivet(cv, 7, 233)
    rivet(cv, 477, 202)
    rivet(cv, 477, 262)
    return cv.img


def dialog_arrow(which):
    cv = Canvas(FW, FH, transparent=True)
    ax, ay = DLG_ARROWS[which]
    arrow(cv, ax + 3, ay + 12, which == 'up', False, length=11)
    ox, oy = DLG_ORIGIN[which]
    return cv.img.crop((ox, oy, ox + 22, oy + 44))


def dialog_bullet():
    """L'indicador de cada opció: un triangle petit de llautó."""
    cv = Canvas(44, 22, transparent=True)
    for (x, y, v) in ((19, 8, 5.0), (19, 9, 4.6), (20, 9, 5.4), (19, 10, 4.2), (20, 10, 4.6), (21, 10, 5.0),
                      (19, 11, 3.6), (20, 11, 3.4), (19, 12, 3.0)):
        cv.put(x, y, BRASS, v, lit=0)
    return cv.img


# ─── 9-slice dels menús ─────────────────────────────────────────────────────

def nine_slice():
    """30×20: vores de 7 px (s'estiren en una direcció) i centre pla (s'estira en totes dues).
    Planxa blau marí amb marc de llautó i un rebló a cada cantó."""
    img = Image.new('RGBA', (30, 20), (0, 0, 0, 0))
    P = img.load()
    face = NAVYB[3]
    ring = [NAVYB[0], BRASS[5], BRASS[4], NAVYB[0], NAVYB[6], NAVYB[4]]
    ring_bottom = [NAVYB[0], BRASS[3], BRASS[2], NAVYB[0], NAVYB[2], NAVYB[3]]
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
    for cx, cy in ((5, 5), (24, 5), (5, 14), (24, 14)):
        P[cx, cy] = NAVYB[8] + (255,)
        P[cx + 1, cy + 1] = NAVYB[0] + (255,)
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
    sheet = Image.new('RGBA', (FW * 3, FH * 4), (0, 0, 0, 0))
    if prev is not None:   # fotograma 0: captura de referència de la plantilla, es conserva
        sheet.paste(prev.crop((0, 0, FW, FH)), (0, 0))
    imgs = [None, verbs_bg(), verbs_arrow('up', False), verbs_arrow('down', False), menu_button(),
            verbs_arrow('up', True), verbs_arrow('down', True), canvia(False), canvia(True),
            face_frame('iri'), face_frame('vet')]
    tags = ['VerbsBG', 'UpBtn', 'DownBtn', 'MenuBtn', 'UpBtn-hover', 'DownBtn-hover', 'CanviaBtn', 'CanviaBtn-hover',
            'CaraIri', 'CaraVet']
    frames = {}
    for i, im in enumerate(imgs):
        x, y = (i % 3) * FW, (i // 3) * FH
        if im is not None:
            sheet.paste(im, (x, y))
        frames.update(frame_json('verbs', i, x, y, FW, FH))
    write_sheet(d, 'verbs', sheet, frames, [(t, i + 1) for i, t in enumerate(tags)], meta)
    (d / '.canvia-provisional').unlink(missing_ok=True)   # el botó ja és definitiu: el sync no el toca
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
        P = img.load()
        for y in range(img.height):            # casella i lliscadors: el verd blavós de la plantilla, a llautó
            for x in range(img.width):
                if P[x, y][:3] in SETTINGS_RECOLOR:
                    P[x, y] = SETTINGS_RECOLOR[P[x, y][:3]] + (P[x, y][3],)
        img.save(p)


# colors de la plantilla (casella marcada, lliscador) → llautó
SETTINGS_RECOLOR = {(16, 144, 142): BRASS[5], (26, 70, 107): BRASS[3]}


# ─── Botons dels menús: plaques de cada mida ────────────────────────────────

MENUS = ('game-menu', 'save-menu', 'load-menu', 'settings-menu')
KEY_STATES = (('', 4.4), ('-hover', 5.2), ('-pressed', 3.6), ('-disabled', 3.0))
TITLE = '#e8c260'       # títols: llautó
LABEL = TEXT
DISABLED = '#56627a'


def key_image(w, h, state):
    """Una placa de w×h per a un botó de menú (normal, hover, premuda o desactivada)."""
    face = dict(KEY_STATES)[state]
    cv = Canvas(w, h, transparent=True)
    if state == '-pressed':
        box(cv, 0, 0, w - 1, h - 1, NAVYB, face)
        cv.hline(1, w - 2, 1, NAVYB, face - 1.2, lit=0)          # enfonsada: ombra a dalt
        cv.vline(1, 1, h - 2, NAVYB, face - 1.0, lit=0)
    else:
        box(cv, 0, 0, w - 1, h - 1, NAVYB, face)
        cv.hline(1, w - 2, 1, NAVYB, face + 1.0, lit=0)
        if state != '-disabled':
            for bx, by in ((2, 2), (w - 3, 2), (2, h - 3), (w - 3, h - 3)):
                cv.put(bx, by, NAVYB, face + 2.2, lit=0)
    if state == '-hover':
        corners(cv, 1, 1, w - 2, h - 2, n=3)                      # cantoneres de llautó
    return cv.img


def build_menu_keys(game, name):
    """Afegeix al full de la GUI les plaques de les mides dels seus botons i fa que els botons les facin servir.
    Idempotent: les plaques d'abans (etiquetes `key-…`) es treuen i es tornen a fer."""
    gp = game / 'guis' / name / f'{name}.gui.json'
    sd = game / 'assets/images/guis' / name
    jp, pp = sd / f'{name}.json', sd / f'{name}.png'
    if not (gp.exists() and jp.exists() and pp.exists()):
        return
    gui = json.loads(gp.read_text())
    sheet_json = json.loads(jp.read_text())
    sheet = Image.open(pp).convert('RGBA')
    # el que hi havia (sense les plaques d'abans)
    tags = [t for t in sheet_json['meta']['frameTags'] if not t['name'].startswith('key-')]
    keep = max((t['to'] for t in tags), default=-1)
    names = list(sheet_json['frames'])[:keep + 1]
    frames = {k: sheet_json['frames'][k] for k in names}
    bottom = max((f['frame']['y'] + f['frame']['h'] for f in frames.values()), default=0)
    right = max((f['frame']['x'] + f['frame']['w'] for f in frames.values()), default=0)
    sizes = []
    for c in gui.get('controls', []):
        if c.get('type') != 'button':
            continue
        if 'backgroundColor' not in c and not str(c.get('backgroundTag', '')).startswith('key-'):
            continue
        wh = (c['width'], c['height'])
        if wh not in sizes:
            sizes.append(wh)
        tag = f'key-{wh[0]}x{wh[1]}'
        c.pop('backgroundColor', None)
        c.pop('backgroundColorStates', None)
        c['backgroundTag'] = tag
        c['backgroundAnchor'] = 'top-left'
        c['states'] = {'hover': f'{tag}-hover', 'pressed': f'{tag}-pressed', 'disabled': f'{tag}-disabled'}
        c['textColor'] = LABEL
        c['textColorStates'] = {'hover': TEXT_HOVER, 'pressed': TEXT_HOVER, 'disabled': DISABLED}
        c['textOutline'] = {'enabled': True, 'color': TEXT_OUTLINE, 'sides': 'bottomRight'}
    # els textos: títols de llautó, la resta crema
    for c in gui.get('controls', []):
        if c.get('type') == 'text':
            c['color'] = TITLE if c.get('id') == 'title' else LABEL
        if c.get('type') == 'textInput':
            c.update({'backgroundColor': '#090f1c', 'hoverBackgroundColor': '#0d1526', 'color': LABEL,
                      'outlineColor': '#6e4a1e', 'focusedOutlineColor': '#e8c260', 'caretColor': TEXT_HOVER,
                      'placeholder': 'Nom de la partida...'})
        if c.get('type') == 'listBox':
            # les files: buits foscos; la seleccionada, de llautó fosc
            c.update({'normalBackgroundColor': '#0d1526', 'hoverBackgroundColor': '#192840',
                      'selectedBackgroundColor': '#5a3e14', 'textColor': LABEL, 'selectedTextColor': '#ffffff',
                      'placeholderTextColor': DISABLED})
    if not sizes:
        return
    # el full nou: el d'abans (fins on arribava) i, a sota, una fila per a cada mida
    rows_h = sum(h for _, h in sizes)
    width = max(right, max(w for w, _ in sizes) * len(KEY_STATES))
    out = Image.new('RGBA', (width, bottom + rows_h), (0, 0, 0, 0))
    out.paste(sheet.crop((0, 0, right, bottom)), (0, 0))
    base = names[0].rsplit(' ', 1)[0].replace('.aseprite', '') if names else name
    n = len(names)
    y = bottom
    for (w, h) in sizes:
        for k, (suffix, _) in enumerate(KEY_STATES):
            x = k * w
            out.paste(key_image(w, h, suffix), (x, y))
            frames[f'{base} key{n}.aseprite'] = {
                'frame': {'x': x, 'y': y, 'w': w, 'h': h}, 'rotated': False, 'trimmed': False,
                'spriteSourceSize': {'x': 0, 'y': 0, 'w': w, 'h': h}, 'sourceSize': {'w': w, 'h': h}, 'duration': 100}
            tags.append({'name': f'key-{w}x{h}{suffix}', 'from': n, 'to': n, 'direction': 'forward', 'color': '#000000ff'})
            n += 1
        y += h
    sheet_json['frames'] = frames
    sheet_json['meta']['frameTags'] = tags
    sheet_json['meta']['size'] = {'w': out.width, 'h': out.height}
    out.save(pp)
    jp.write_text(json.dumps(sheet_json, indent=1) + '\n')
    gp.write_text(json.dumps(gui, indent=2, ensure_ascii=False) + '\n')


FACE_CONTROLS = ('CaraIri', 'CaraVet')


def apply_text_colors(game):
    """Els colors del text dels botons de verbs, de la frase i de les opcions de diàleg; el hover del botó
    «Canvia» i les dues cares de l'ull de bou (controls `image`, just després del botó)."""
    guis = game / 'guis'
    vp = guis / 'verbs/verbs.gui.json'
    if vp.exists():
        d = json.loads(vp.read_text())
        controls = d.get('controls', [])
        for c in controls:
            if c.get('type') == 'button' and c.get('text') and c.get('font') == 'niunou-negreta':
                c['textColor'] = TEXT
                c['textColorStates'] = {'hover': TEXT_HOVER}
                c['textOutline'] = {'enabled': True, 'color': TEXT_OUTLINE, 'sides': 'bottomRight'}
            if c.get('id') == 'verbLineText':
                c['color'] = VERB_LINE
            if c.get('id') == 'CanviaBtn':
                c['states'] = {'hover': 'CanviaBtn-hover'}
        ids = [c.get('id') for c in controls]
        if 'CanviaBtn' in ids:
            controls[:] = [c for c in controls if c.get('id') not in FACE_CONTROLS]
            at = [c.get('id') for c in controls].index('CanviaBtn') + 1
            for k, cid in enumerate(FACE_CONTROLS):
                controls.insert(at + k, {'type': 'image', 'id': cid, 'x': 0, 'y': 0, 'tag': cid,
                                         'backgroundAnchor': 'screen', 'visible': False,
                                         # Damunt del botó: no han de prendre-li el clic.
                                         'clickable': False})
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
    from escala import RESOLUCIO
    if RESOLUCIO == 640:
        sys.exit('Ni un ou és a 640×360: la GUI la fa hd640/gui_rest.py i la posa al joc hd640/aplica.py.')
    build_verbs(game)
    build_dialog(game)
    build_menus(game)
    apply_text_colors(game)
    for name in MENUS:
        build_menu_keys(game, name)
    print('✔ interfície HD: verbs, diàleg i menús')


if __name__ == '__main__':
    main(Path(sys.argv[1]).resolve())
