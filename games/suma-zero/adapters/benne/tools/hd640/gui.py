#!/usr/bin/env python3
"""
La barra de verbs de Suma Zero a 640×360 (la franja de y=260 a 359, 640×100), redibuixada.

Mateix estil que hd/gui.py (la consola d'hacker: plàstic blau marí gairebé negre amb trama de punts, tecles
fosques, pantalletes amb línies d'escaneig i cantoneres de visor, la línia de llum verd blavós amb el tram
magenta, LEDs i reixetes), amb la geometria ×4/3 arrodonida a mà, i els textos amb la font de 640
(hd640/font.py). El botó «Canvia» (mitja Iri i mitja Vet, el passat de maó i el present de nit) es dibuixa
aquí a 57×43, amb les cares dels personatges de 640.

    from hd640.gui import verb_bar
    img = verb_bar()                                  # Image RGBA 640×100, per enganxar a (0, 260)
    img = verb_bar({'hover': 'look', 'line': 'Mira el router'})

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
from pixels import nearest  # noqa: E402

import hd640  # noqa: E402,F401  (posa la llibreria a 640×360)
import hd.items as items480  # noqa: E402  (abans que res no canviï la Fig de hd.characters)
from hd.pix import Canvas, hr, mix  # noqa: E402
from hd.gui import SLATE, TEAL, MAG, TEXT, TEXT_HOVER, TEXT_OUTLINE, VERB_LINE, dark  # noqa: E402
from hd640.font import font640, text_width, draw_text as _draw_text  # noqa: E402

W, Y0, BH = 640, 260, 100          # la barra: 640×100, a partir de y=260 de la pantalla

# ─── Geometria (coordenades dins la barra, y=0 és la y=260 de la pantalla) ──
STRIP_H = 15                       # franja de la frase (195..206 a 480 → 0..14)
LINE_Y = 16                        # la línia de llum (207 a 480): 2 px de nucli, amb halo a dalt i a baix
BODY_Y = 19                        # el cos de la consola (209 a 480)
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


def slots():
    for r in range(2):
        for c in range(4):
            yield INV_X + c * (SLOT_W + GAP), INV_Y + r * (SLOT_H + GAP)


def draw_text(img, glyphs, s, x, y, color, outline=TEXT_OUTLINE, space=4):
    """Text de mapa de bits a (x, y) (dalt de la línia), amb la vora de baix a la dreta com al joc."""
    _draw_text(img, glyphs, s, x, y, color, outline=outline, space=space)


# ─── Peces ─────────────────────────────────────────────────────────────────

def body(cv, x0, y0, x1, y1, top=3.2, fall=0.009):
    """El cos de la consola: plàstic fosc mat, amb la trama de punts (cada 8 px) i un gra de 4 px."""
    for y in range(y0, y1 + 1):
        vy = top - (y - y0) * fall
        for x in range(x0, x1 + 1):
            dot = 0.35 if (x % 8 == 0 and y % 8 == 0) else (0.12 if (x % 8 == 1 and y % 8 == 0) else 0)
            cv.put(x, y, SLATE, vy + dot + (hr(902, x // 4, y // 4) - 0.5) * 0.15, lit=0)


def key(cv, x0, y0, x1, y1, face=4.4, skirt=3):
    """Una tecla: cara amb bisell de 2 px a dalt i 1 a l'esquerra, cantons arrodonits, faldó fosc i ombra."""
    fy1 = y1 - skirt
    cut = {(x0, y0), (x0 + 1, y0), (x0, y0 + 1), (x1, y0), (x1 - 1, y0), (x1, y0 + 1),
           (x0, y1), (x1, y1), (x0, fy1), (x1, fy1)}
    for y in range(y0, y1 + 1):
        for x in range(x0, x1 + 1):
            if (x, y) in cut:
                continue
            if y > fy1:                                   # el faldó
                v = face - 2.4 + (0.4 if x == x0 + 1 else 0) - (0.3 if y == y1 else 0)
            elif y == y0:
                v = face + 2.2
            elif y == y0 + 1:
                v = face + 1.0
            elif x == x0:
                v = face + 1.2
            elif x == x1:
                v = face - 1.0
            elif y == fy1:
                v = face - 0.8
            else:
                v = face + 0.3 - 0.6 * (y - y0) / max(1, fy1 - y0)
            cv.put(x, y, SLATE, v, lit=0)
    for x in range(x0 + 1, x1 + 2):                       # ombra de contacte
        dark(cv, x, y1 + 1, 0.55)
    for y in range(y0 + 2, y1 + 1):
        dark(cv, x1 + 1, y, 0.35)


def well(cv, x0, y0, x1, y1, face=1.2, brackets=True):
    """Pantalleta enfonsada: fons gairebé negre, línies d'escaneig, llavi clar a baix, reflex i cantoneres de visor."""
    for y in range(y0, y1 + 1):
        for x in range(x0, x1 + 1):
            v = face + (0.35 if (y - y0) % 2 == 0 else 0)
            if y == y0 or x == x0:
                v = 0.0
            elif y == y0 + 1 or x == x0 + 1:
                v = face - 0.6
            elif y == y1:
                v = face + 3.0
            elif x == x1:
                v = face + 2.2
            cv.put(x, y, SLATE, v, lit=0)
    # el reflex del vidre, en diagonal, al cantó de dalt a l'esquerra (dues bandes, la segona més fluixa)
    for k in range(7):
        for t in range(4):
            x, y = x0 + 4 + k + t, y0 + 3 + t
            if x < x1 - 2 and y < y1 - 2 and k < 5:
                cv.put(x, y, SLATE, face + 1.6, lit=0)
            if k < 2 and x + 7 < x1 - 2:
                cv.put(x + 7, y, SLATE, face + 1.0, lit=0)
    if brackets:
        L = 6
        for (cx, cy, dx, dy) in ((x0 + 3, y0 + 3, 1, 1), (x1 - 3, y0 + 3, -1, 1), (x0 + 3, y1 - 3, 1, -1), (x1 - 3, y1 - 3, -1, -1)):
            for i in range(L):
                lv = 3.4 if i == 0 else (2.6 if i < L - 1 else 1.8)
                cv.put(cx + dx * i, cy, TEAL, lv, lit=0)
                cv.put(cx, cy + dy * i, TEAL, lv, lit=0)


def led(cv, x, y, ramp, on=True):
    """Un LED de 3×3, arrodonit, amb el punt de llum i el halo."""
    for dx, dy, v in ((1, 0, 5), (0, 1, 5), (1, 1, 6.4), (2, 1, 4.4), (1, 2, 4.2), (0, 0, 3.2), (2, 0, 3.6),
                      (0, 2, 3.4), (2, 2, 3.0)):
        cv.put(x + dx, y + dy, ramp, v if on else v * 0.3, lit=0)
    if on:
        cv.glow(x + 1.5, y + 1.5, 7, ramp[4], 0.32)


def slits(cv, x0, x1, ys):
    """Reixeta de ventilació: ranures de 2 px amb vora clara a sota."""
    for y in ys:
        for x in range(x0, x1 + 1):
            end = x in (x0, x1)
            cv.put(x, y, SLATE, 0.2 if not end else 1.0, lit=0)
            cv.put(x, y + 1, SLATE, 0.6 if not end else 1.4, lit=0)
            cv.put(x, y + 2, SLATE, 4.6 if not end else 3.8, lit=0)


def light_line(cv, x0, x1, y, mag=(8, 53)):
    """La línia de llum que separa l'escena de la consola: nucli de 2 px verd blavós, polsos de dades i el tram
    magenta (l'accent) a l'esquerra, damunt del botó «Canvia»."""
    for x in range(x0, x1 + 1):
        pulse = (x // 4) % 23 == 0 or (x // 3) % 37 == 0
        v = 4.6 + (1.2 if pulse else 0) + (hr(903, x // 9) - 0.5) * 0.4
        ramp = MAG if mag[0] <= x <= mag[1] else TEAL
        cv.put(x, y - 1, ramp, 1.2, lit=0)
        cv.put(x, y, ramp, v + 0.4, lit=0)
        cv.put(x, y + 1, ramp, v - 0.6, lit=0)
        cv.put(x, y + 2, ramp, 2.0, lit=0)
    # dues marques de dades en blanc verdós, més brillants
    for px in (x0 + 197, x0 + 452):
        for dx in range(3):
            if x0 <= px + dx <= x1:
                cv.put(px + dx, y, TEAL, 6.4, lit=0)


def arrow(cv, cx, cy, up, hover, length=20):
    """Fletxa de llum (verd blavós; magenta i amb halo en hover). cx = columna esquerra del centre (traç de 2 px)."""
    ramp = MAG if hover else TEAL
    rows = []
    for i, w in enumerate((2, 4, 6, 8, 10)):
        rows.append((cx - w // 2 + 1, cx + w // 2, i))
    for i in range(5, length):
        rows.append((cx, cx + 1, i))
    y0 = cy - length // 2
    for a, b, i in rows:
        y = y0 + i if up else y0 + length - 1 - i
        for x in range(a, b + 1):
            v = 5.4 if x <= cx else 4.4
            if i == 0:
                v = 6.2
            elif i < 5 and x in (a, b):
                v -= 0.8                                   # la vora de la punta, més fosca: es veu arrodonida
            cv.put(x, y, ramp, v, lit=0)
    if hover:
        cv.glow(cx + 0.5, cy, 13, ramp[4], 0.4)


# ─── La barra ──────────────────────────────────────────────────────────────

def background():
    """El fons de la barra (VerbsBG): tot menys les fletxes, el menú i el botó «Canvia» (fotogrames a part)."""
    cv = Canvas(W, BH, transparent=True)
    # franja de la frase («Ves a ...»): una barra d'estat fosca
    for y in range(0, STRIP_H + 1):
        for x in range(W):
            cv.put(x, y, SLATE, 0.6 + (0.5 if y == 0 else 0), lit=0)
    body(cv, 0, BODY_Y, W - 1, BH - 1)
    light_line(cv, 0, W - 1, LINE_Y)
    for x in range(W):
        dark(cv, x, BODY_Y, 0.5)
        dark(cv, x, BODY_Y + 1, 0.2)
        cv.put(x, BH - 1, SLATE, 0.8, lit=0)
    for y in range(BODY_Y, BH - 1):
        cv.put(0, y, SLATE, 4.2, lit=0)
        cv.put(W - 1, y, SLATE, 1.2, lit=0)
    # juntes entre seccions: una ranura fosca amb un fil de llum molt fluix, a trams
    for sx in SEAMS:
        for y in range(BODY_Y + 4, BH - 4):
            cv.put(sx, y, SLATE, 0.3, lit=0)
            cv.put(sx + 1, y, TEAL, 1.2 if (y // 5) % 3 else 2.0, lit=0)
    # botó «Canvia»: ombra al voltant (la imatge és opaca i el tapa)
    x, y, w, h = CANVIA
    for xx in range(x - 1, x + w + 1):
        dark(cv, xx, y - 1, 0.5)
        dark(cv, xx, y + h, 0.6)
        dark(cv, xx, y + h + 1, 0.3)
    for yy in range(y, y + h):
        dark(cv, x - 1, yy, 0.5)
        dark(cv, x + w, yy, 0.6)
    # sota «Canvia», a l'esquerra del menú: tres LEDs d'estat (connexió, auricular, gravant) i la reixeta
    led(cv, 8, 70, TEAL)
    led(cv, 16, 70, MAG)
    led(cv, 24, 70, TEAL, on=False)
    slits(cv, 8, 29, (80, 86, 92))
    # verbs: tecles
    for row, vy in zip(VERB_IDS, VERB_ROWS):
        for (vx, vw), _vid in zip(VERB_COLS, row):
            key(cv, vx, vy, vx + vw - 1, vy + VERB_H - 1)
    # fletxes: canals enfonsats
    for ax, ay in ARROWS.values():
        well(cv, ax, ay, ax + 12, ay + 35, face=1.0, brackets=False)
    # inventari: pantalletes
    for sx, sy in slots():
        well(cv, sx, sy, sx + SLOT_W - 1, sy + SLOT_H - 1)
    # dreta: un vúmetre de LEDs i la reixeta
    for k in range(8):
        led(cv, 621, 84 - k * 8, MAG if k >= 6 else TEAL, on=k < 5)
    slits(cv, 617, 632, (23, 28))
    return cv


def arrow_layer(cv, which, hover):
    """La fletxa d'un canal (i, en hover, la claror magenta del canal), sobre `cv` (coordenades de la barra)."""
    ax, ay = ARROWS[which]
    if hover:
        for y in range(ay + 2, ay + 35):
            for x in range(ax + 2, ax + 12):
                d = abs(y - (ay + 18)) / 17
                if 0.55 * (1 - d) > 0.12 + 0.6 * ((x * 5 + y * 3) % 7) / 7:
                    cv.flat(x, y, mix(SLATE[2], MAG[2], 0.5))
    arrow(cv, ax + 5, ay + 18, which == 'up', hover)


def menu_layer(cv):
    """El botó del menú: una tecla quadrada amb tres ratlles de llum (sobre un tros de cos, opac)."""
    x, y, s = MENU
    body(cv, x, y, x + s - 1, y + s - 1)
    key(cv, x, y, x + s - 2, y + s - 2, face=4.6, skirt=3)
    for ly in (y + 5, y + 10, y + 15):
        for lx in range(x + 5, x + s - 7):
            cv.put(lx, ly, TEAL, 5.4 if lx < x + s - 9 else 4.2, lit=0)
            cv.put(lx, ly + 1, TEAL, 3.4, lit=0)


# ─── «Canvia» ──────────────────────────────────────────────────────────────

PORTRAIT = {'vet': 15, 'iri': 16}       # columna on comença el retall de 35×39 al fotograma de 640 (65×116)
_FACES = {}


def portrait(who):
    """El retrat (35×39) del personatge de 640, de cara: del full hd640/characters/<who> (IdleD) si ja hi és;
    si no, el dibuixa hd640/draw_characters (sense el «</>» del pit, que surt a sota del retall)."""
    if who in _FACES:
        return _FACES[who]
    d = Path(__file__).resolve().parent / 'characters' / who
    ch = d / f'{who}.character.json'
    escala1 = not ch.exists() or json.loads(ch.read_text()).get('artScale', 1) == 1
    if (d / f'{who}.json').exists() and escala1:     # un full a 2× no serveix per al retrat, que és a 640
        sheet = json.loads((d / f'{who}.json').read_text())
        tag = next(t['from'] for t in sheet['meta']['frameTags'] if t['name'] == 'IdleD')
        fr = list(sheet['frames'].values())[tag]['frame']
        src = Image.open(d / f'{who}.png').convert('RGBA').crop((fr['x'], fr['y'], fr['x'] + fr['w'], fr['y'] + fr['h']))
    else:
        from hd640.draw_characters import install
        P = install()
        logo, P.LOGO = P.LOGO, ()
        try:
            src = getattr(P, who)('D')
        finally:
            P.LOGO = logo
    x0 = PORTRAIT[who]
    _FACES[who] = src.crop((x0, 4, x0 + 35, 43))
    return _FACES[who]


def canvia_image(hover=False, h=None):
    """El botó «Canvia» a 57×43 (a 480, 43×32): mitja Iri i mitja Vet partides en diagonal; darrere, el passat
    (paret de maó) i el present (cel de nit amb estrelles). Marc de la consola: contorn fosc i vora de llum
    verd blavós; en hover, tot una mica més clar i la vora magenta."""
    w, h = CANVIA[2], h or CANVIA[3]
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
    for y in range(h):                                    # el cel, una mica més clar a baix (la ciutat)
        for x in range(w):
            if y > h - 12 and (x * 7 + y * 3) % 5 < (y - (h - 12)) // 3:
                present.putpixel((x, y), (28, 38, 74, 255))
    for x, y in ((40, 5), (49, 12), (44, 33), (53, 27), (35, 19), (52, 39), (47, 4)):
        present.putpixel((x, y), (230, 230, 255, 255))
    for x, y in ((44, 20), (38, 30)):                     # dues estrelles grosses, en creu
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
    out.alpha_composite(cara, (12, 4 + (h - CANVIA[3]) // 2))
    d = ImageDraw.Draw(out)
    d.line([(35, 0), (23, h - 1)], fill=(230, 200, 130, 255))
    d.line([(36, 0), (24, h - 1)], fill=(150, 120, 80, 255))
    if hover:
        out = Image.blend(out, Image.new('RGBA', (w, h), (255, 220, 240, 255)), 0.12)
    d = ImageDraw.Draw(out)
    fosc = (3, 4, 10, 255)
    clar, mig, ombra = (((255, 120, 210, 255), (200, 50, 150, 255), (140, 26, 104, 255)) if hover else
                        ((80, 210, 190, 255), (36, 160, 148, 255), (10, 78, 80, 255)))
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
        return [nearest(items480.render(i), (SLOT_W, SLOT_H)) for i in ids]


# ─── La barra completa ─────────────────────────────────────────────────────

def verb_bar(state=None):
    """La barra completa (640×100). state: {'hover': id de verb o 'up'/'down'/'canvia', 'line': frase,
    'inv': [ids d'objecte]}."""
    st = {'hover': None, 'line': 'Usa el cable de xarxa amb el router', 'inv': ('auriculars', 'cable_xarxa', 'pizza')}
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

def bar480(line='Usa el cable de xarxa amb el router', inv=('auriculars', 'cable_xarxa', 'pizza'), hover=None):
    """La barra de 480 (els fotogrames de hd/gui.py, el «Canvia» de draw_placeholders, les icones de hd/items.py
    i els textos amb la font del joc), retallada a 480×75."""
    from hd import gui as g
    sys.path.insert(0, str(TOOLS.parents[2] / 'tools/font'))
    import suma_font as sf
    img = Image.new('RGBA', (480, 270), (0, 0, 0, 0))
    for layer in (g.verbs_bg(), g.verbs_arrow('up', hover == 'up'), g.verbs_arrow('down', hover == 'down'),
                  g.menu_button(), g.canvia(hover == 'canvia')):
        img.alpha_composite(layer)
    for i, (sx, sy) in zip(inv, g.slots()):
        ic = items480.render(i)
        if ic is not None:
            img.alpha_composite(ic, (sx, sy))
    bold, reg = sf.all_glyphs(True), sf.all_glyphs(False)
    ids = ('give', 'pickUp', 'use', 'open', 'talkTo', 'push', 'close', 'look', 'pull')
    for (vx, vy, vw), vid in zip(g.VERBS, ids):
        s = VERB_TEXT[vid]
        tw = text_width(bold, s, sf.SPACE_ADVANCE)
        draw_text(img, bold, s, vx + (vw - tw) // 2, vy + 2, TEXT_HOVER if hover == vid else TEXT, space=sf.SPACE_ADVANCE)
    tw = text_width(reg, line, sf.SPACE_ADVANCE)
    draw_text(img, reg, line, 240 - tw // 2, 192, VERB_LINE, outline=None, space=sf.SPACE_ADVANCE)
    return img.crop((0, 195, 480, 270))


def main():
    out = Path(sys.argv[1]) if len(sys.argv) > 1 else Path('barra_640.png')
    a = nearest(bar480(hover='look'), (1920, 300))
    b = nearest(verb_bar({'hover': 'look'}), (1920, 300))
    gap = 40
    o = Image.new('RGB', (1920, 300 * 2 + gap * 2), (30, 30, 30))
    d = ImageDraw.Draw(o)
    d.text((8, 10), 'ACTUAL 480x270: barra 480x75, x4', fill=(255, 255, 255))
    o.paste(a, (0, gap))
    d.text((8, gap + 300 + 10), '640x360: barra 640x100, x3', fill=(255, 255, 255))
    o.paste(b, (0, gap * 2 + 300))
    o.save(out)
    verb_bar().save(out.with_name(out.stem + '_sola.png'))
    print(f'✔ {out}')


if __name__ == '__main__':
    main()
