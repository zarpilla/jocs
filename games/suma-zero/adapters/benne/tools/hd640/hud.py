#!/usr/bin/env python3
"""
Suma Zero: la interfície sense barra de verbs (tàctil). Substitueix la barra del joc original.

Escriu directament al projecte Benne (suma-zero/src/game):

  guis/verbs/verbs.gui.json + assets/images/guis/verbs/   el HUD: es diu `verbs` perquè el pont compartit
                                                           (adapters/benne/runtime) la mostra i l'amaga, i hi
                                                           busca el botó «Canvia»
  guis/accions/accions.gui.json + assets/.../accions/     el menú d'accions (mantenir premut o clic dret)

Els scripts (`verbs.gui.ts`, `hud.ts`, `accions.gui.ts`) són compartits (adapters/benne/tactil/guis) i els copia
`npm run benne:sync`: els ids i les mides dels controls han de ser els que esperen (els mateixos que el hud.py
d'Aigua Verne). L'estil és el de la barra (hd640/gui.py): la consola d'hacker, amb plàstic blau marí, tecles
fosques, pantalletes amb cantoneres de visor, la línia de llum verd blavós i l'accent magenta. El botó «Canvia» és
el de la barra (mitja Iri i mitja Vet): ja mostra totes dues, i les cares de sobre (CaraIri, CaraVet) són buides.

    python3 adapters/benne/tools/hd640/hud.py

Compte: `gui_rest.py` torna a fer la barra de verbs: no l'executis en aquest joc.
"""
import json
import math
import sys
from pathlib import Path

from PIL import Image

TOOLS = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(TOOLS))

import hd640  # noqa: E402,F401
from hd.pix import Canvas, mix  # noqa: E402
from hd.gui import SLATE, TEAL, MAG, TEXT, TEXT_HOVER, TEXT_OUTLINE, VERB_LINE, dark  # noqa: E402
import hd640.gui as vg  # noqa: E402
from hd640.gui import body, key, well, led, light_line, slits, arrow  # noqa: E402
from hd640.gui_rest import write_sheet, key_image, GAME  # noqa: E402

W, H = 640, 288                         # l'alçada mínima (20:9); la pantalla pot ser més alta (pantalla.py)
FRANJA = 260                            # a sota, la franja: la frase
FONT, BOLD = 'suma-regular', 'suma-negreta'

# ─── Disposició (ha de coincidir amb adapters/benne/tactil/guis: hud.ts i accions.gui.ts) ─────

M = 4                                   # marge de la pantalla
CANVIA = (M, M)                         # 57×43 (el de la barra)
MENU_BTN = (W - M - 25, M)              # 25×25
BOTO = 32                               # els botons de baix (inventari, punts), a les cantonades
PUNTS = (M, H - M - BOTO)
BOSSA = (W - M - BOTO, H - M - BOTO)
SLOT_W, SLOT_H, GAP, COLS = 65, 36, 4, 7
SAFATA = (52, FRANJA - 46, 532, 44)     # x, y, amplada, alçada: just a sobre de la franja
FLETXA_W = 13
# Pantalla alta (un monitor, fins a 360): la franja de sota l'escena (de 260 avall) és la consola, amb tot el HUD
# i l'inventari sempre a la vista. Coordenades a 360 d'alt.
H_MAX = 360
TAULER = (0, FRANJA, W, H_MAX - FRANJA)          # 640×100
COLS2, ROWS2 = 7, 2                     # 7 per fila: el tauler té a l'esquerra «Canvia», el menú i els punts
SAFATA2_W, SAFATA2_H = 520, 82
SAFATA2 = (94, H_MAX - 4 - SAFATA2_H)           # de la columna de l'esquerra (fins a x = 67) a la dreta
# Tauler baix (una finestra de navegador, d'uns 320–350 d'alt): una sola fila de 6, amb les fletxes als costats.
SAFATA3_W, SAFATA3_H = 529, 44
SAFATA3_X = 100                         # de la columna de l'esquerra (fins a x = 90) a la dreta
PETIT = 25                              # els punts petits del tauler baix (al costat de «Canvia», sota el menú)
KEY_W, KEY_H = 104, 22                  # botons del menú d'accions
ACCIONS_MAX = 6


def plate(w, h, hover=False, on=False):
    """Un botó quadrat: una tecla de la consola; amb hover, més clara; encès, la ratlla magenta a sota."""
    cv = Canvas(w, h, transparent=True)
    key(cv, 0, 0, w - 2, h - 2, face=5.2 if (hover or on) else 4.4, skirt=3)
    if on:
        for x in range(5, w - 7):
            cv.put(x, h - 7, MAG, 4.0, lit=0)
            cv.put(x, h - 6, MAG, 2.4, lit=0)
    return cv


def bossa_icon(cv, hover):
    """L'inventari: una carpeta de fitxers en traç de llum (verd blavós; magenta en hover), amb un full a dins."""
    ramp = MAG if hover else TEAL
    k = cv.w / 32
    q = lambda v: round(v * k)                                          # noqa: E731  (dibuixat a 32 px)
    x0, x1, y0, y1 = q(7), q(24), q(10), q(22)
    for x in range(x0 + 1, x1):                                         # el full que sobresurt
        cv.put(x, y0 - 2, SLATE, 9.0, lit=0)
    cv.vline(x0 + 1, y0 - 2, y0, SLATE, 9.0, lit=0)
    cv.vline(x1 - 1, y0 - 2, y0, SLATE, 9.0, lit=0)
    cv.hline(x0, x0 + q(6), y0 - 3, ramp, 5.0, lit=0)                   # la pestanya
    cv.line(x0 + q(6), y0 - 3, x0 + q(8), y0, ramp, 5.0, lit=0)
    cv.hline(x0, x1, y0, ramp, 5.4, lit=0)                              # la carpeta
    cv.hline(x0, x1, y1, ramp, 4.4, lit=0)
    cv.vline(x0, y0 - 3, y1, ramp, 5.0, lit=0)
    cv.vline(x1, y0, y1, ramp, 4.4, lit=0)
    for y in range(y0 + 1, y1):
        for x in range(x0 + 1, x1):
            cv.put(x, y, ramp, 1.4 if (x + y) % 2 else 1.0, lit=0)
    cv.put((x0 + x1) // 2, (y0 + y1) // 2, MAG if not hover else TEAL, 5.6, lit=0)
    if hover:
        cv.glow(cv.w / 2, cv.h / 2, 12, ramp[4], 0.3)


def punts_icon(cv, hover):
    """L'escàner: una pantalleta rodona amb l'agulla i tres punts magenta, «què es pot tocar aquí?»."""
    cx = cy = cv.w // 2 - 1
    r = cv.w * 0.29
    for yy in range(cy - int(r) - 1, cy + int(r) + 2):
        for xx in range(cx - int(r) - 1, cx + int(r) + 2):
            d = math.hypot(xx - cx, yy - cy)
            if d <= r:
                c = mix(SLATE[1], TEAL[1], max(0, 1 - d / r) * 0.8 + (0.3 if hover else 0))
                if (yy - cy) % 2:
                    c = mix(c, SLATE[0], 0.4)
                cv.flat(xx, yy, c)
    cv.ring(cx, cy, r, TEAL, 4.4, lit=0, step=1)
    cv.ring(cx, cy, r * 0.55, TEAL, 2.6, lit=0, step=4)
    cv.line(cx, cy, cx + round(r * 0.7), cy - round(r * 0.5), TEAL, 5.4, lit=0)
    for (px, py) in ((cx - 4, cy - 3), (cx + 3, cy + 2), (cx - 1, cy + 5)):
        cv.disc(px, py, 1.4, 1.4, MAG, 4.4, lit=0)
        cv.put(px, py, MAG, 6.0, lit=0)
    if hover:
        cv.glow(cx, cy, 12, TEAL[4], 0.3)


def boto(icon, hover=False, on=False, mida=BOTO):
    cv = plate(mida, mida, hover, on)
    icon(cv, hover or on)
    return cv.img


def fletxa(up, hover):
    cv = Canvas(FLETXA_W, SLOT_H, transparent=True)
    arrow(cv, FLETXA_W // 2 - 1, SLOT_H // 2, up, hover, length=16)
    return cv.img


def menu_btn():
    """El botó del menú de la barra (una tecla amb tres ratlles de llum), retallat."""
    mx, my, ms = vg.MENU
    cv = Canvas(W, vg.BH, transparent=True)
    vg.menu_layer(cv)
    return cv.img.crop((mx, my, mx + ms, my + ms))


def panel(w, h, top=3.0):
    """Una placa de la consola: el cos fosc amb la trama de punts, vora clara a dalt i a l'esquerra."""
    cv = Canvas(w, h, transparent=True)
    body(cv, 0, 0, w - 1, h - 1, top=top)
    cv.hline(0, w - 1, 0, SLATE, 5.4, lit=0)
    cv.vline(0, 0, h - 1, SLATE, 4.6, lit=0)
    cv.hline(0, w - 1, h - 1, SLATE, 0.8, lit=0)
    cv.vline(w - 1, 0, h - 1, SLATE, 1.2, lit=0)
    for (cx, cy) in ((0, 0), (w - 1, 0), (0, h - 1), (w - 1, h - 1)):
        cv.P[cx, cy] = (0, 0, 0, 0)
    return cv


def canal(cv, x, y):
    """El canal enfonsat d'una fletxa (com els de la barra)."""
    well(cv, x, y, x + FLETXA_W - 1, y + SLOT_H - 1, face=1.0, brackets=False)


def safata_xy():
    sx, sy, sw, sh = SAFATA
    inner = COLS * SLOT_W + (COLS - 1) * GAP
    fx0 = sx + (sw - inner - 2 * FLETXA_W - 2 * 6) // 2       # fletxa d'amunt
    slots_x = fx0 + FLETXA_W + 6
    fx1 = slots_x + inner + 6                                  # fletxa d'avall
    return fx0, slots_x, fx1, sy + (sh - SLOT_H) // 2


def safata():
    """La safata de l'inventari: una placa amb les pantalletes de les caselles i, als costats, les fletxes."""
    sx, sy, sw, sh = SAFATA
    cv = panel(sw, sh)
    light_line(cv, 1, sw - 2, 1, mag=(4, 40))
    fx0, slots_x, fx1, top = safata_xy()
    for i in range(COLS):
        x0 = slots_x - sx + i * (SLOT_W + GAP)
        well(cv, x0, top - sy, x0 + SLOT_W - 1, top - sy + SLOT_H - 1)
    for x in (fx0 - sx, fx1 - sx):
        canal(cv, x, top - sy)
    return cv.img


def safata2_xy():
    """La safata gran (2 files de 6): x de les caselles, y de dalt, x de les fletxes (una sobre l'altra, a la dreta)."""
    sx, sy = SAFATA2
    inner_w = COLS2 * SLOT_W + (COLS2 - 1) * GAP
    inner_h = ROWS2 * SLOT_H + (ROWS2 - 1) * GAP
    slots_x = sx + (SAFATA2_W - inner_w - FLETXA_W - 6) // 2
    top = sy + (SAFATA2_H - inner_h) // 2
    return slots_x, top, slots_x + inner_w + 6


def safata2():
    """La safata gran de la consola: les pantalletes de 2×6 caselles i, a la dreta, els dos canals de les fletxes."""
    sx, sy = SAFATA2
    cv = Canvas(SAFATA2_W, SAFATA2_H, transparent=True)
    slots_x, top, fx = safata2_xy()
    for r in range(ROWS2):
        y0 = top - sy + r * (SLOT_H + GAP)
        for i in range(COLS2):
            x0 = slots_x - sx + i * (SLOT_W + GAP)
            well(cv, x0, y0, x0 + SLOT_W - 1, y0 + SLOT_H - 1)
        canal(cv, fx - sx, y0)
    return cv.img


def safata3_xy():
    """La safata d'una fila del tauler baix: x de la fletxa d'amunt, de les caselles i de la d'avall."""
    inner = COLS2 * SLOT_W + (COLS2 - 1) * GAP
    fx0 = SAFATA3_X + (SAFATA3_W - inner - 2 * FLETXA_W - 12) // 2
    slots_x = fx0 + FLETXA_W + 6
    return fx0, slots_x, slots_x + inner + 6


def safata3():
    """La safata d'una fila (6 caselles) del tauler baix, amb les fletxes als costats."""
    cv = Canvas(SAFATA3_W, SAFATA3_H, transparent=True)
    fx0, slots_x, fx1 = safata3_xy()
    top = (SAFATA3_H - SLOT_H) // 2
    for i in range(COLS2):
        x0 = slots_x - SAFATA3_X + i * (SLOT_W + GAP)
        well(cv, x0, top, x0 + SLOT_W - 1, top + SLOT_H - 1)
    for x in (fx0 - SAFATA3_X, fx1 - SAFATA3_X):
        canal(cv, x, top)
    return cv.img


def tauler():
    """La consola de la franja de sota l'escena: la franja de la frase, la línia de llum i el cos amb la trama de punts
    (com la barra, sense tecles ni juntes: a sobre hi van «Canvia», el menú, els punts i l'inventari)."""
    _, _, tw, th = TAULER
    cv = Canvas(tw, th, transparent=True)
    for y in range(0, vg.STRIP_H + 1):                          # la franja de la frase: una barra d'estat fosca
        for x in range(tw):
            cv.put(x, y, SLATE, 0.6 + (0.5 if y == 0 else 0), lit=0)
    body(cv, 0, vg.BODY_Y, tw - 1, th - 1)
    light_line(cv, 0, tw - 1, vg.LINE_Y, mag=(8, 53))
    for x in range(tw):
        dark(cv, x, vg.BODY_Y, 0.5)
        dark(cv, x, vg.BODY_Y + 1, 0.2)
        cv.put(x, th - 1, SLATE, 0.8, lit=0)
    for y in range(vg.BODY_Y, th - 1):
        cv.put(0, y, SLATE, 4.2, lit=0)
        cv.put(tw - 1, y, SLATE, 1.2, lit=0)
    return cv.img


def buit():
    return Image.new('RGBA', (1, 1), (0, 0, 0, 0))


def text_outline():
    return {'enabled': True, 'color': TEXT_OUTLINE, 'sides': 'allSides'}


# ─── El HUD (`verbs`) ──────────────────────────────────────────────────────

def build_hud():
    cw, ch = vg.CANVIA[2], vg.CANVIA[3]
    ms = vg.MENU[2]
    frames = [
        (vg.canvia_image(False), 'CanviaBtn'), (vg.canvia_image(True), 'CanviaBtn-hover'), (menu_btn(), 'MenuBtn'),
        (boto(bossa_icon), 'BossaBtn'), (boto(bossa_icon, hover=True), 'BossaBtn-hover'),
        (boto(bossa_icon, on=True), 'BossaBtn-on'),
        (boto(punts_icon), 'PuntsBtn'), (boto(punts_icon, hover=True), 'PuntsBtn-hover'),
        (boto(punts_icon, mida=PETIT), 'PuntsPetitBtn'), (boto(punts_icon, hover=True, mida=PETIT), 'PuntsPetitBtn-hover'),
        (safata(), 'Safata'),
        (fletxa(True, False), 'UpBtn'), (fletxa(True, True), 'UpBtn-hover'),
        (fletxa(False, False), 'DownBtn'), (fletxa(False, True), 'DownBtn-hover'),
        (buit(), 'CaraIri'), (buit(), 'CaraVet'),
        (tauler(), 'Tauler'), (safata2(), 'Safata2'), (safata3(), 'Safata3'),
    ]
    sheet_dir = GAME / 'assets/images/guis/verbs'
    write_sheet(sheet_dir, 'verbs', [(im, tag, (0, 0), im.size) for im, tag in frames])

    fx0, slots_x, fx1, top = safata_xy()

    def button(cid, xy, w, h, tag, states=None, visible=True):
        c = {'type': 'button', 'id': cid, 'x': xy[0], 'y': xy[1], 'width': w, 'height': h, 'backgroundAnchor': 'top-left',
             'text': '', 'font': BOLD, 'fontSize': 8, 'textColor': TEXT, 'textAlign': 'center', 'textOffsetX': 0,
             'textOffsetY': 0, 'backgroundTag': tag}
        if states:
            c['states'] = states
        if not visible:
            c['visible'] = False
        return c

    slots2_x, top2, fx2 = safata2_xy()
    s3_fx0, s3_slots, s3_fx1 = safata3_xy()
    s3_top = H - 4 - SAFATA3_H + (SAFATA3_H - SLOT_H) // 2
    d = H_MAX - H                                              # el tauler, dissenyat a 360 i enganxat a baix
    controls = [
        # la consola de la franja (pantalla alta): a sota de tot
        {'type': 'image', 'id': 'Tauler', 'x': TAULER[0], 'y': TAULER[1], 'tag': 'Tauler', 'backgroundAnchor': 'top-left',
         'visible': False, 'clickable': False},
        # la frase: el nom del que hi ha sota el dit o el ratolí, o «Usa X amb...»
        {'type': 'text', 'id': 'verbLineText', 'x': W // 2, 'y': FRANJA + 9, 'text': '', 'font': FONT, 'fontSize': 8,
         'color': VERB_LINE, 'align': 'center', 'textOutline': text_outline(), 'zIndex': 5},
        button('CanviaBtn', CANVIA, cw, ch, 'CanviaBtn', {'hover': 'CanviaBtn-hover'}),
        {'type': 'image', 'id': 'CaraIri', 'x': CANVIA[0], 'y': CANVIA[1], 'tag': 'CaraIri', 'backgroundAnchor': 'top-left',
         'visible': False, 'clickable': False},
        {'type': 'image', 'id': 'CaraVet', 'x': CANVIA[0], 'y': CANVIA[1], 'tag': 'CaraVet', 'backgroundAnchor': 'top-left',
         'visible': False, 'clickable': False},
        button('MenuBtn', MENU_BTN, ms, ms, 'MenuBtn'),
        button('PuntsBtn', PUNTS, BOTO, BOTO, 'PuntsBtn', {'hover': 'PuntsBtn-hover'}),
        # els punts petits del tauler baix (hud.ts els posa i els mostra)
        button('PuntsPetitBtn', PUNTS, PETIT, PETIT, 'PuntsPetitBtn', {'hover': 'PuntsPetitBtn-hover'}, visible=False),
        button('BossaBtn', BOSSA, BOTO, BOTO, 'BossaBtn', {'hover': 'BossaBtn-hover'}),
        # la safata, plegada: verbs.gui.ts la desplega amb el botó de l'inventari
        {'type': 'image', 'id': 'Safata', 'x': SAFATA[0], 'y': SAFATA[1], 'tag': 'Safata', 'backgroundAnchor': 'top-left',
         'visible': False},
        {'type': 'inventoryPanel', 'id': 'inventoryPanel', 'x': slots_x, 'y': top, 'rows': 1, 'cols': COLS,
         'slotWidth': SLOT_W, 'slotHeight': SLOT_H, 'showEmptySlots': True, 'spacingX': GAP, 'spacingY': GAP,
         'scrollDirection': 'vertical', 'backButton': 'upBtn', 'forwardButton': 'downBtn', 'visible': False},
        button('upBtn', (fx0, top), FLETXA_W, SLOT_H, 'UpBtn', {'hover': 'UpBtn-hover'}, visible=False),
        button('downBtn', (fx1, top), FLETXA_W, SLOT_H, 'DownBtn', {'hover': 'DownBtn-hover'}, visible=False),
        # la safata gran de la consola (pantalla alta), sempre oberta
        {'type': 'image', 'id': 'Safata2', 'x': SAFATA2[0], 'y': SAFATA2[1] - d, 'tag': 'Safata2',
         'backgroundAnchor': 'top-left', 'visible': False, 'anchorY': 'bottom'},
        {'type': 'inventoryPanel', 'id': 'inventoryPanel2', 'x': slots2_x, 'y': top2 - d, 'rows': ROWS2, 'cols': COLS2,
         'slotWidth': SLOT_W, 'slotHeight': SLOT_H, 'showEmptySlots': True, 'spacingX': GAP, 'spacingY': GAP,
         'scrollDirection': 'vertical', 'backButton': 'upBtn2', 'forwardButton': 'downBtn2', 'visible': False,
         'anchorY': 'bottom'},
        {**button('upBtn2', (fx2, top2 - d), FLETXA_W, SLOT_H, 'UpBtn', {'hover': 'UpBtn-hover'}, visible=False),
         'anchorY': 'bottom'},
        {**button('downBtn2', (fx2, top2 - d + SLOT_H + GAP), FLETXA_W, SLOT_H, 'DownBtn', {'hover': 'DownBtn-hover'},
                  visible=False), 'anchorY': 'bottom'},
        # la safata d'una fila del tauler baix (a 4 px de baix de tot)
        {'type': 'image', 'id': 'Safata3', 'x': SAFATA3_X, 'y': H - 4 - SAFATA3_H, 'tag': 'Safata3',
         'backgroundAnchor': 'top-left', 'visible': False, 'anchorY': 'bottom'},
        {'type': 'inventoryPanel', 'id': 'inventoryPanel3', 'x': s3_slots, 'y': s3_top, 'rows': 1, 'cols': COLS2,
         'slotWidth': SLOT_W, 'slotHeight': SLOT_H, 'showEmptySlots': True, 'spacingX': GAP, 'spacingY': GAP,
         'scrollDirection': 'vertical', 'backButton': 'upBtn3', 'forwardButton': 'downBtn3', 'visible': False,
         'anchorY': 'bottom'},
        {**button('upBtn3', (s3_fx0, s3_top), FLETXA_W, SLOT_H, 'UpBtn', {'hover': 'UpBtn-hover'}, visible=False),
         'anchorY': 'bottom'},
        {**button('downBtn3', (s3_fx1, s3_top), FLETXA_W, SLOT_H, 'DownBtn', {'hover': 'DownBtn-hover'}, visible=False),
         'anchorY': 'bottom'},
    ]
    # Pantalla adaptable (dissenyada a 288 d'alt): el que és a baix va enganxat a baix.
    for c in controls:
        if c['id'] in ('verbLineText', 'PuntsBtn', 'BossaBtn', 'Safata', 'inventoryPanel', 'upBtn', 'downBtn'):
            c['anchorY'] = 'bottom'
    gui = {'id': 'verbs', 'name': 'HUD', 'description': 'Suma Zero: sense barra de verbs [hd640/hud.py]',
           'visible': True, 'display': {'aseprite': True}, 'controls': controls}
    out = GAME / 'guis/verbs/verbs.gui.json'
    out.write_text(json.dumps(gui, indent=2, ensure_ascii=False) + '\n')


# ─── El menú d'accions (`accions`) ─────────────────────────────────────────

def build_accions():
    items = []
    for st in ('', '-hover', '-pressed'):
        im = key_image(KEY_W, KEY_H, st)
        items.append((im, f'Accio{st}', (0, 0), im.size))
    write_sheet(GAME / 'assets/images/guis/accions', 'accions', items)
    controls = [
        # tot el fons: tocar fora del menú el tanca (accions.gui.ts el fa mig transparent)
        {'type': 'button', 'id': 'fons', 'x': 0, 'y': 0, 'width': W, 'height': H, 'backgroundAnchor': 'top-left',
         'text': '', 'font': FONT, 'fontSize': 8, 'textColor': '#ffffff', 'backgroundTag': '',
         'backgroundColor': '#000000', 'backgroundColorStates': {'hover': '#000000', 'pressed': '#000000'}, 'zIndex': 1,
         'anchorY': 'stretch'},
        {'type': 'text', 'id': 'titol', 'x': W // 2, 'y': 100, 'text': '', 'font': BOLD, 'fontSize': 8,
         'color': TEXT_HOVER, 'align': 'center', 'textOutline': text_outline(), 'zIndex': 3},
    ]
    for i in range(ACCIONS_MAX):
        controls.append({
            'type': 'button', 'id': f'accio{i}', 'x': 0, 'y': 0, 'width': KEY_W, 'height': KEY_H,
            'backgroundAnchor': 'top-left', 'text': '', 'font': BOLD, 'fontSize': 8, 'textColor': TEXT,
            'textAlign': 'center', 'textOffsetX': 0, 'textOffsetY': 0, 'backgroundTag': 'Accio',
            'states': {'hover': 'Accio-hover', 'pressed': 'Accio-pressed'}, 'textColorStates': {'hover': TEXT_HOVER},
            'textOutline': {'enabled': True, 'color': TEXT_OUTLINE, 'sides': 'bottomRight'}, 'zIndex': 2,
            'visible': False,
        })
    for i in range(ACCIONS_MAX):                 # el text de cada botó (el d'un botó no es pot canviar des de l'script)
        controls.append({'type': 'text', 'id': f'text{i}', 'x': 0, 'y': 0, 'text': '', 'font': BOLD, 'fontSize': 8,
                         'color': TEXT, 'align': 'center', 'zIndex': 3, 'visible': False,
                         'textOutline': {'enabled': True, 'color': TEXT_OUTLINE, 'sides': 'bottomRight'}})
    gui = {'id': 'accions', 'name': 'Accions', 'description': "Suma Zero: el menú d'accions [hd640/hud.py]",
           'visible': False, 'display': {'aseprite': True}, 'modal': True, 'zIndex': 90, 'controls': controls}
    d = GAME / 'guis/accions'
    d.mkdir(parents=True, exist_ok=True)
    (d / 'accions.gui.json').write_text(json.dumps(gui, indent=2, ensure_ascii=False) + '\n')


if __name__ == '__main__':
    build_hud()
    build_accions()
    print(f'✔ HUD i menú d\'accions a {GAME}')
