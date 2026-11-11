#!/usr/bin/env python3
"""
La barra de verbs de Ferro-9 a 640×360 (la franja de y=260 a 359, 640×100), redibuixada.

Mateix estil que hd/gui.py (planxa de metall blau-pissarra raspallat, plaques de verb en relleu, caselles
enfonsades, reblons, reixetes i el fil de llautó que separa l'escena de la barra), amb la geometria ×4/3
arrodonida a mà, i els textos amb la font de 640 (hd640/font.py). Els píxels de més van al detall: bisells de
2 px, vetes del raspallat, reblons de 4×4 amb el seu reflex, el fil de llautó de 3 files amb la brillantor
que corre, i la trama perforada del fons de les caselles. El botó «Canvia» (mitja Iri i mitja Vet, la
fàbrica de maó i el cel d'estrelles, com draw_placeholders.switch_button_image) es dibuixa aquí a 57×43.

    from hd640.gui import verb_bar
    img = verb_bar()                                  # Image RGBA 640×100, per enganxar a (0, 260)
    img = verb_bar({'hover': 'look', 'line': 'Mira el segell'})

Les peces (fons, fletxes, menú, «Canvia») són funcions separades: hd640/gui_rest.py les posa en fotogrames
de pantalla per al full verbs.png. No cal el projecte Benne.

`python3 hd640/gui.py <sortida.png>` munta la comparativa: la barra de 480 (×4, amb els textos amb la font
del joc) sobre la de 640 (×3), totes dues a 1920 d'ample.
"""
import json
import sys
from pathlib import Path

from PIL import Image, ImageDraw

TOOLS = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(TOOLS))

import hd640  # noqa: E402,F401  (posa la llibreria a 640×360)
import hd.items as items480  # noqa: E402
from hd.pix import Canvas, hr, mix  # noqa: E402
from hd.gui import SLATE, BRASS, TEXT, TEXT_HOVER, TEXT_OUTLINE, VERB_LINE, dark  # noqa: E402
from hd640.font import font640, text_width, draw_text as _draw_text  # noqa: E402

W, Y0, BH = 640, 260, 100          # la barra: 640×100, a partir de y=260 de la pantalla
HERE = Path(__file__).resolve().parent
ART = TOOLS.parent / 'placeholder-art'

# ─── Geometria (coordenades dins la barra, y=0 és la y=260 de la pantalla) ──
STRIP_H = 16                       # franja de la frase (195..206 a 480 → 0..15)
TRIM_Y = 16                        # el fil de llautó (207..208 a 480): 3 files
BODY_Y = 19                        # la planxa (209 a 480)
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
SEAMS = (62, 317, 611)

SAMPLE_LINE = 'Usa la clau anglesa amb la caixa d\'eines'
SAMPLE_INV = ('clau_anglesa', 'formulari_27b', 'segell')


def slots():
    for r in range(2):
        for c in range(4):
            yield INV_X + c * (SLOT_W + GAP), INV_Y + r * (SLOT_H + GAP)


def draw_text(img, glyphs, s, x, y, color, outline=TEXT_OUTLINE, space=4):
    """Text de mapa de bits a (x, y) (dalt de la línia), amb la vora de baix a la dreta com al joc."""
    _draw_text(img, glyphs, s, x, y, color, outline=outline, space=space)


# ─── Peces ─────────────────────────────────────────────────────────────────

def body(cv, x0, y0, x1, y1, top=3.75, fall=0.0083):
    """Planxa de metall raspallat: més clara a dalt, amb vetes horitzontals (trams de 41 px que brillen una mica
    més, com a 480 els de 31) i un gra fi de raspallat que a 480 no hi cabia."""
    for y in range(y0, y1 + 1):
        vy = top - (y - y0) * fall + (hr(901, y) - 0.5) * 0.12
        for x in range(x0, x1 + 1):
            streak = 0.25 if hr(902, x // 41, y) > 0.93 else 0
            grain = 0.1 if hr(904, x // 3, y) > 0.86 else 0
            cv.put(x, y, SLATE, vy + streak + grain, lit=0)


def plate(cv, x0, y0, x1, y1, face=4.5):
    """Placa en relleu (llum de dalt a l'esquerra): bisell de 2 px clar a dalt i a l'esquerra, fosc a baix i a la
    dreta, cara amb un degradat suau i el raspallat; ombra de contacte a sota i a la dreta."""
    h = max(1, y1 - y0)
    for y in range(y0, y1 + 1):
        brush = (hr(905, y, x0) - 0.5) * 0.18
        for x in range(x0, x1 + 1):
            v = face + 0.45 - 0.75 * (y - y0) / h + brush
            if y == y0:
                v = face + 3
            elif x == x0:
                v = face + 2
            elif y == y1:
                v = face - 3
            elif x == x1:
                v = face - 2
            elif y == y0 + 1:
                v = face + 1.4
            elif x == x0 + 1:
                v = face + 0.9
            elif y == y1 - 1:
                v = face - 1.0
            elif x == x1 - 1:
                v = face - 0.6
            cv.put(x, y, SLATE, v, lit=0)
    cv.put(x1, y0, SLATE, face + 0.6, lit=0)
    cv.put(x0, y1, SLATE, face - 0.8, lit=0)
    for x in range(x0 + 1, x1 + 2):                       # ombra de contacte
        dark(cv, x, y1 + 1, 0.5)
    for y in range(y0 + 1, y1 + 1):
        dark(cv, x1 + 1, y, 0.3)


def well(cv, x0, y0, x1, y1, face=1.6, mesh=True):
    """Casella enfonsada: ombra de 2 px a dalt i a l'esquerra, llavi clar a baix i a la dreta, fons fosc amb el
    reflex de baix i (mesh) la trama perforada de la planxa."""
    h = max(1, y1 - y0)
    for y in range(y0, y1 + 1):
        for x in range(x0, x1 + 1):
            v = face + 0.7 * (y - y0) / h
            if mesh and (x - x0) % 4 == 2 and (y - y0) % 4 == 2:
                v -= 0.6                                  # forat de la trama
            elif mesh and (x - x0) % 4 == 3 and (y - y0) % 4 == 3:
                v += 0.3                                  # i la vora clara del forat, a baix a la dreta
            if y == y0 or x == x0:
                v = 0.2
            elif y == y1:
                v = face + 3.4
            elif x == x1:
                v = face + 2.6
            elif y == y0 + 1 or x == x0 + 1:
                v = face - 0.7
            elif y == y1 - 1:
                v = face + 1.4
            cv.put(x, y, SLATE, v, lit=0)
    cv.put(x1, y0, SLATE, face + 0.6, lit=0)
    cv.put(x0, y1, SLATE, face + 0.6, lit=0)


def rivet(cv, x, y, ramp=SLATE, base=7.5):
    """Rebló de 4×4 (a 480, 3×3): cap rodó amb el reflex a dalt a l'esquerra i ombra a baix a la dreta."""
    for dx, dy, v in ((1, 0, base + 1.5), (2, 0, base + 0.5), (0, 1, base + 1), (1, 1, base + 2.4), (2, 1, base + 0.6),
                      (3, 1, base - 1.6), (0, 2, base - 0.4), (1, 2, base), (2, 2, base - 1.2), (3, 2, base - 2.6),
                      (1, 3, base - 2.8), (2, 3, base - 3.2)):
        cv.put(x + dx, y + dy, ramp, v, lit=0)
    for dx, dy, k in ((3, 3, 0.7), (4, 2, 0.35), (4, 3, 0.45), (2, 4, 0.35), (3, 4, 0.45)):
        dark(cv, x + dx, y + dy, k)


def slits(cv, x0, x1, ys):
    """Reixeta de ventilació: ranures de 2 px fosques amb la vora clara a sota."""
    for y in ys:
        for x in range(x0, x1 + 1):
            end = x in (x0, x1)
            cv.put(x, y, SLATE, 0.2 if not end else 1.2, lit=0)
            cv.put(x, y + 1, SLATE, 0.8 if not end else 1.6, lit=0)
            cv.put(x, y + 2, SLATE, 5.0 if not end else 4.2, lit=0)


def brass_trim(cv, x0, x1, y):
    """El fil de llautó: tres línies (llum a dalt), amb una brillantor que varia per trams i alguns punts de reflex."""
    for x in range(x0, x1 + 1):
        g = 0.35 * (hr(903, x // 12) - 0.5)
        spark = 0.9 if hr(906, x // 2) > 0.97 else 0
        cv.put(x, y, BRASS, 4.4 + g + spark, lit=0)
        cv.put(x, y + 1, BRASS, 3.2 + g, lit=0)
        cv.put(x, y + 2, BRASS, 1.6 + g, lit=0)


def arrow(cv, cx, cy, up, hover, length=20, head=6, stem=2):
    """Fletxa amb volum: cap de `head` files (d'1 a 2·head-1 px; 6 a la barra) i tija de 2·stem+1; costat esquerre
    clar, dret fosc, i ombra projectada a baix a la dreta. cx = columna central."""
    ramp = BRASS if hover else SLATE
    lit, mid, shd, top = ((6.5, 5.5, 3.5, 7.5) if hover else (8.5, 7.5, 5.5, 9.5))
    rows = [(cx - i, cx + i, i) for i in range(head)]
    rows += [(cx - stem, cx + stem, i) for i in range(head, length)]
    y0 = cy - length // 2
    pts = []
    for a, b, i in rows:
        y = y0 + i if up else y0 + length - 1 - i
        for x in range(a, b + 1):
            pts.append((x, y))
            v = lit if x <= cx else mid
            if i == head - 1 and not (cx - stem <= x <= cx + stem):
                v = shd                                   # la vora de sota del cap
            if i >= head and x == cx + stem:
                v = shd
            if x == a and i < head - 1:
                v = top
            if up and i == 0:
                v = top
            if not up and i == 0:
                v = mid
            cv.put(x, y, ramp, v, lit=0)
    s = set(pts)
    for x, y in pts:
        if (x + 1, y + 1) not in s:
            dark(cv, x + 1, y + 1, 0.55)
    if hover:
        cv.glow(cx, cy, 12, BRASS[4], 0.35)


# ─── La barra ──────────────────────────────────────────────────────────────

def background():
    """El fons de la barra (VerbsBG): tot menys les fletxes, el menú i el botó «Canvia» (fotogrames a part)."""
    cv = Canvas(W, BH, transparent=True)
    for y in range(0, STRIP_H):                           # franja de la frase («Ves a ...»)
        for x in range(W):
            cv.put(x, y, SLATE, 0.35 + (0.4 if y == STRIP_H - 1 else 0), lit=0)
    body(cv, 0, BODY_Y, W - 1, BH - 1)
    brass_trim(cv, 0, W - 1, TRIM_Y)
    for x in range(W):
        dark(cv, x, BODY_Y, 0.45)
        dark(cv, x, BODY_Y + 1, 0.15)
        cv.put(x, BH - 1, SLATE, 1.4, lit=0)
    for y in range(BODY_Y, BH - 1):
        cv.put(0, y, SLATE, 4.6, lit=0)
        cv.put(W - 1, y, SLATE, 1.6, lit=0)
    for sx in SEAMS:                                      # juntes entre seccions: ranura fosca + vora clara
        for y in range(BODY_Y + 1, BH - 2):
            dark(cv, sx - 1, y, 0.2)
            cv.put(sx, y, SLATE, 0.6, lit=0)
            cv.put(sx + 1, y, SLATE, 5.0, lit=0)
    x, y, w, h = CANVIA                                   # «Canvia»: ombra al voltant (la imatge és opaca)
    for xx in range(x - 1, x + w + 1):
        dark(cv, xx, y - 1, 0.5)
        dark(cv, xx, y + h, 0.6)
        dark(cv, xx, y + h + 1, 0.25)
    for yy in range(y, y + h):
        dark(cv, x - 1, yy, 0.5)
        dark(cv, x + w, yy, 0.6)
    slits(cv, 8, 28, (75, 80, 85))                        # sota «Canvia», a l'esquerra del menú
    rivet(cv, 8, 91)
    rivet(cv, 25, 91)
    for row, vy in zip(VERB_IDS, VERB_ROWS):              # verbs
        for (vx, vw), _vid in zip(VERB_COLS, row):
            plate(cv, vx, vy, vx + vw - 1, vy + VERB_H - 1)
    for ax, ay in ARROWS.values():                        # fletxes: canals enfonsats
        well(cv, ax, ay, ax + 12, ay + 35, face=1.4, mesh=False)
    for sx, sy in slots():                                # inventari
        well(cv, sx, sy, sx + SLOT_W - 1, sy + SLOT_H - 1)
    rivet(cv, 623, 23)                                    # dreta: reblons i reixeta
    rivet(cv, 623, 89)
    slits(cv, 617, 632, (36, 43, 49, 56, 63, 69, 76))
    return cv


def arrow_layer(cv, which, hover):
    """La fletxa d'un canal (i, en hover, la claror de llautó del canal), sobre `cv` (coordenades de la barra)."""
    ax, ay = ARROWS[which]
    if hover:
        for y in range(ay + 2, ay + 35):
            for x in range(ax + 2, ax + 12):
                d = abs(y - (ay + 18)) / 17
                if 0.55 * (1 - d) > 0.12 + 0.6 * ((x * 5 + y * 3) % 7) / 7:
                    cv.flat(x, y, mix(SLATE[2], BRASS[2], 0.6))
    arrow(cv, ax + 6, ay + 18, which == 'up', hover)


def menu_layer(cv):
    """El botó del menú: plaqueta en relleu de 25×25 amb tres ratlles gravades (sobre un tros de planxa, opac)."""
    x, y, s = MENU
    body(cv, x, y, x + s - 1, y + s - 1)
    plate(cv, x, y, x + s - 2, y + s - 2, face=4.6)
    for ly in (y + 7, y + 12, y + 17):
        for lx in range(x + 5, x + s - 6):
            cv.put(lx, ly - 1, SLATE, 2.0, lit=0)
            cv.put(lx, ly, SLATE, 8.6 if lx < x + s - 9 else 7.6, lit=0)
            cv.put(lx, ly + 1, SLATE, 3.0, lit=0)


# ─── «Canvia» ──────────────────────────────────────────────────────────────

PORTRAIT = {'vet': 15, 'iri': 16}       # columna on comença el retall de 35×39 al fotograma de 640 (65×116)
_FACES = {}


def character_frame(who):
    """El fotograma IdleD del personatge a 640 (65×116): de hd640/characters/<who> si ja hi és; si no, el de
    placeholder-art ampliat ×4/3 (provisional: només si encara no hi ha els personatges de 640)."""
    d = HERE / 'characters' / who
    provisional = not (d / f'{who}.json').exists()
    if provisional:
        d = ART / who
    sheet = json.loads((d / f'{who}.json').read_text())
    tag = next(t['from'] for t in sheet['meta']['frameTags'] if t['name'] == 'IdleD')
    fr = list(sheet['frames'].values())[tag]['frame']
    src = Image.open(d / f'{who}.png').convert('RGBA').crop((fr['x'], fr['y'], fr['x'] + fr['w'], fr['y'] + fr['h']))
    if src.height < 100:                                  # (placeholder-art encara és de 480)
        src = src.resize((65, 116), Image.NEAREST)
    return src, provisional


def portrait(who):
    """El retrat (35×39) del personatge de 640, de cara (a 480: 26×29)."""
    if who not in _FACES:
        src, _ = character_frame(who)
        x0 = PORTRAIT[who]
        _FACES[who] = src.crop((x0, 4, x0 + 35, 43))
    return _FACES[who]


def canvia_image(hover=False):
    """El botó «Canvia» a 57×43 (a 480, 43×32): mitja Iri i mitja Vet partides en diagonal; darrere, la fàbrica
    (paret de maó) i el present (cel de nit amb estrelles), separats per un fil de llautó. Marc de metall pissarra
    amb bisell de 2 px; en hover, tot una mica més clar i el bisell de llautó encès."""
    w, h = CANVIA[2], CANVIA[3]
    passat = Image.new('RGBA', (w, h), (96, 52, 36, 255))
    pd = ImageDraw.Draw(passat)
    for y in range(0, h, 5):                              # maons de 13×5, a trencajunt
        pd.line([(0, y), (w, y)], fill=(70, 36, 26, 255))
        for x in range((y // 5) % 2 * 7, w, 13):
            pd.line([(x, y), (x, y + 4)], fill=(70, 36, 26, 255))
        for x in range((y // 5) % 2 * 7 + 1, w, 13):      # la cara de dalt de cada maó, una mica més clara
            pd.line([(x, y + 1), (x + 10, y + 1)], fill=(112, 62, 42, 255))
    for i in range(28):                                   # porus del maó
        x, y = int(hr(950, i) * w), int(hr(951, i) * h)
        if passat.getpixel((x, y))[:3] == (96, 52, 36):
            passat.putpixel((x, y), (84, 44, 30, 255))
    present = Image.new('RGBA', (w, h), (20, 28, 58, 255))
    for y in range(h):                                    # el cel, una mica més clar a baix
        for x in range(w):
            if y > h - 12 and (x * 7 + y * 3) % 5 < (y - (h - 12)) // 3:
                present.putpixel((x, y), (28, 38, 74, 255))
    for x, y in ((40, 5), (49, 12), (44, 33), (53, 27), (35, 19), (52, 39), (47, 4)):
        present.putpixel((x, y), (230, 230, 255, 255))
    for x, y in ((45, 20), (38, 30)):                     # dues estrelles grosses, en creu
        for dx, dy in ((0, 0), (1, 0), (-1, 0), (0, 1), (0, -1)):
            present.putpixel((x + dx, y + dy), (230, 230, 255, 255) if (dx, dy) == (0, 0) else (120, 130, 190, 255))
    tall = Image.new('L', (w, h), 0)
    ImageDraw.Draw(tall).polygon([(0, 0), (35, 0), (23, h), (0, h)], fill=255)
    out = present.copy()
    out.paste(passat, (0, 0), tall)
    cara = Image.new('RGBA', (35, 39), (0, 0, 0, 0))
    meitat = Image.new('L', (35, 39), 0)
    ImageDraw.Draw(meitat).polygon([(0, 0), (23, 0), (11, 39), (0, 39)], fill=255)
    cara.paste(portrait('vet'), (0, 0))
    cara.paste(portrait('iri'), (0, 0), meitat)
    out.alpha_composite(cara, (12, 4))
    d = ImageDraw.Draw(out)
    d.line([(35, 0), (23, h - 1)], fill=(230, 200, 130, 255))
    d.line([(36, 0), (24, h - 1)], fill=(150, 112, 60, 255))
    if hover:
        out = Image.blend(out, Image.new('RGBA', (w, h), (255, 240, 210, 255)), 0.12)
    d = ImageDraw.Draw(out)
    fosc = (7, 9, 14, 255)
    clar, mig, ombra = ((BRASS[7] + (255,), BRASS[5] + (255,), BRASS[3] + (255,)) if hover else
                        (SLATE[9] + (255,), SLATE[7] + (255,), SLATE[3] + (255,)))
    d.rectangle([0, 0, w - 1, h - 1], outline=fosc)
    d.line([(1, 1), (w - 2, 1)], fill=clar)
    d.line([(1, 1), (1, h - 2)], fill=clar)
    d.line([(2, 2), (w - 3, 2)], fill=mig)
    d.line([(2, 2), (2, h - 3)], fill=mig)
    d.line([(1, h - 2), (w - 2, h - 2)], fill=ombra)
    d.line([(w - 2, 2), (w - 2, h - 2)], fill=ombra)
    for x, y in ((0, 0), (w - 1, 0), (0, h - 1), (w - 1, h - 1)):
        out.putpixel((x, y), (0, 0, 0, 0))
    return out


def canvia_layer(cv, hover=False):
    cv.img.alpha_composite(canvia_image(hover), (CANVIA[0], CANVIA[1]))


# ─── Icones d'inventari ────────────────────────────────────────────────────

def inv_icons(ids):
    """Icones d'inventari de 640 (65×36): les de hd640/items.py si ja hi són; si no, les de 480 ampliades."""
    try:
        from hd640 import items as items640
        return [items640.render(i) for i in ids]
    except ImportError:
        out = []
        for i in ids:
            ic = items480.render(i)
            out.append(ic.resize((SLOT_W, SLOT_H), Image.NEAREST) if ic is not None else None)
        return out


# ─── La barra completa ─────────────────────────────────────────────────────

def verb_bar(state=None):
    """La barra completa (640×100). state: {'hover': id de verb o 'up'/'down'/'canvia', 'line': frase,
    'inv': [ids d'objecte]}."""
    st = {'hover': None, 'line': SAMPLE_LINE, 'inv': SAMPLE_INV}
    st.update(state or {})
    cv = background()
    for which in ARROWS:
        arrow_layer(cv, which, st['hover'] == which)
    menu_layer(cv)
    canvia_layer(cv, st['hover'] == 'canvia')
    img = cv.img
    for ic, (sx, sy) in zip(inv_icons(st['inv']), slots()):
        if ic is not None:
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

def bar480(line=SAMPLE_LINE, inv=SAMPLE_INV, hover=None):
    """La barra de 480 (els fotogrames de hd/gui.py, el «Canvia» de draw_placeholders, les icones de hd/items.py
    i els textos amb la font del joc), retallada a 480×75."""
    from hd import gui as g
    sys.path.insert(0, str(TOOLS.parents[2] / 'tools/font'))
    import ferro_font as ff
    img = Image.new('RGBA', (480, 270), (0, 0, 0, 0))
    layers = [g.verbs_bg(), g.verbs_arrow('up', hover == 'up'), g.verbs_arrow('down', hover == 'down'), g.menu_button()]
    try:
        layers.append(g.canvia(hover == 'canvia'))
    except Exception:                                     # (si placeholder-art ja és de 640)
        pass
    for layer in layers:
        img.alpha_composite(layer)
    for i, (sx, sy) in zip(inv, g.slots()):
        ic = items480.render(i)
        if ic is not None:
            img.alpha_composite(ic, (sx, sy))
    bold, reg = ff.all_glyphs(True), ff.all_glyphs(False)
    ids = ('give', 'pickUp', 'use', 'open', 'talkTo', 'push', 'close', 'look', 'pull')
    for (vx, vy, vw), vid in zip(g.VERBS, ids):
        s = VERB_TEXT[vid]
        tw = text_width(bold, s, ff.SPACE_ADVANCE)
        draw_text(img, bold, s, vx + (vw - tw) // 2, vy + 2, TEXT_HOVER if hover == vid else TEXT, space=ff.SPACE_ADVANCE)
    tw = text_width(reg, line, ff.SPACE_ADVANCE)
    draw_text(img, reg, line, 240 - tw // 2, 192, VERB_LINE, outline=None, space=ff.SPACE_ADVANCE)
    return img.crop((0, 195, 480, 270))


def main():
    out = Path(sys.argv[1]) if len(sys.argv) > 1 else Path('barra_640.png')
    out.parent.mkdir(parents=True, exist_ok=True)
    gap = 40
    o = Image.new('RGB', (1920, (300 + gap) * 4), (30, 30, 30))
    d = ImageDraw.Draw(o)
    for k, hover in enumerate(('look', 'canvia')):
        a = bar480(hover=hover).resize((1920, 300), Image.NEAREST)
        b = verb_bar({'hover': hover}).resize((1920, 300), Image.NEAREST)
        y = k * 2 * (300 + gap)
        d.text((8, y + 10), f'ACTUAL 480x270: barra 480x75, x4 (hover: {hover})', fill=(255, 255, 255))
        o.paste(a, (0, y + gap))
        d.text((8, y + gap + 300 + 10), f'640x360: barra 640x100, x3 (hover: {hover})', fill=(255, 255, 255))
        o.paste(b, (0, y + gap * 2 + 300))
    o.save(out)
    verb_bar().save(out.with_name(out.stem + '_sola.png'))
    _, prov = character_frame('iri')
    print(f'✔ {out}' + ('  (cares del «Canvia»: placeholder-art de 480 ×4/3, provisional)' if prov else ''))


if __name__ == '__main__':
    main()
