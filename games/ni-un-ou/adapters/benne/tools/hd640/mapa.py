#!/usr/bin/env python3
"""
El plànol d'emergència de l'Arenga (guio/guio.md, «Regles del món · 8»): la GUI `mapa`, a pantalla sencera.

Un full plastificat damunt la planxa fosca, amb les tres cobertes vistes des de dalt (popa a l'esquerra, proa a la
dreta, com al passadís). Cada sala jugable és un botó: el nom a sobre (text de la GUI), un requadre verd en passar-hi
per sobre i, quan ara no s'hi pot anar, una trama grisa a sobre (una imatge a part que el runtime mostra o amaga).
El punt vermell «Sou aquí» i el de l'altra protagonista (I o V) els mou el runtime.

Escriu, al projecte Benne:
  src/game/assets/images/guis/mapa/mapa.png + .json   el full (etiquetes: `planol`, `<id>`, `<id>-hover`, `<id>-off`,
                                                        `aqui`, `altraIri`, `altraVet`)
  src/game/guis/mapa/mapa.gui.json                    la GUI (els botons, amb el nom curt de cada sala dels locales)

El script de la GUI (mapa.gui.ts) el genera games/ni-un-ou/adapters/benne/joc.ts, i la lògica és a
runtime/mapa.ts i runtime/mapa.script.ts. Els ids dels controls ja són en camelCase (`salaSalaMaquines`): Benne
els hi passaria igualment, i així el runtime els troba pel mateix nom.

    python3 hd640/mapa.py [carpeta per a una previsualització]
"""
import json
import sys
from pathlib import Path

from PIL import Image, ImageDraw

TOOLS = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(TOOLS))
from pixels import nearest  # noqa: E402

from hd640.font import font640, draw_text, text_width  # noqa: E402
from hd640.gui_rest import write_sheet  # noqa: E402

JOC = TOOLS.parents[2]
GAME = JOC / 'ni-un-ou/src/game'
LOCALES = JOC / 'game/locales/ca/interficie.json'
W, H = 640, 288                 # Ni un ou: l'alçada mínima de la pantalla adaptable (vegeu Y, a sota)

# ─── Colors (un plànol imprès i plastificat) ────────────────────────────────
BOARD = (6, 10, 20)
PAPER = (236, 236, 226)
PAPER_SHADE = (214, 214, 202)
INK = (40, 40, 38)
ROOM = (248, 247, 240)
CORR = (214, 236, 218)          # els passadissos: rutes d'evacuació
ROUTE = (46, 138, 84)
EXT = (226, 212, 184)           # coberta exterior (fusta)
PLANK = (204, 188, 156)
DECOR = (226, 226, 218)         # el que no és jugable (camarots, tancs)
GREEN = (44, 120, 82)
RED = (200, 52, 44)
HOVER = (186, 226, 196)
HOVER_EDGE = (44, 120, 82)
GREYTXT = (120, 120, 114)

# ─── Geometria ──────────────────────────────────────────────────────────────
# Les sales jugables: (x0, y0, x1, y1). Popa a l'esquerra, proa a la dreta.
SALES = {
    # coberta del pont
    'sala_radio': (248, 54, 320, 98),
    'pont': (320, 54, 432, 98),
    'pal': (442, 62, 470, 90),
    # coberta principal
    'coberta_popa': (50, 128, 118, 226),
    'cuina': (118, 128, 236, 164),
    'menjador': (118, 164, 236, 226),
    'infermeria': (236, 128, 306, 164),
    'laboratori': (306, 128, 376, 164),
    'cabina_capitana': (410, 128, 500, 164),
    'passadis': (236, 164, 500, 188),
    'coberta_proa': (500, 128, 552, 226),
    # coberta inferior
    'rebost': (50, 248, 112, 287),
    'diposit2': (50, 287, 112, 326),
    'sala_maquines': (112, 248, 236, 326),
    'taller': (236, 248, 296, 278),
    'camarot_iri': (296, 248, 356, 278),
    'pallol': (388, 248, 470, 278),
    'passadis_baix': (236, 278, 470, 300),
    'sala_bombes': (236, 300, 322, 326),
    'caixa_cadenes': (498, 264, 548, 310),
}
EXTERIORS = {'coberta_popa', 'coberta_proa', 'pal'}
CORRIDORS = {'passadis', 'passadis_baix'}

# El que no és jugable: (x0, y0, x1, y1, rètol)
DECORS = [
    (376, 128, 410, 164, ''),            # l'escala (amunt i avall)
    (236, 188, 500, 226, 'CAMAROTS'),
    (356, 248, 388, 278, ''),            # l'escala
    (322, 300, 470, 326, 'TANCS DE GASOIL'),
]
STAIRS = [(376, 128, 410, 164), (356, 248, 388, 278)]

# Els cascos de cada coberta (polígons) i el rètol
DECKS = [
    ([(230, 48), (480, 48), (480, 104), (230, 104)], 'COBERTA DEL PONT', (50, 66)),
    ([(46, 124), (540, 124), (612, 177), (540, 230), (46, 230)], 'COBERTA PRINCIPAL', (50, 106)),
    ([(46, 244), (510, 244), (590, 287), (510, 330), (46, 330)], 'COBERTA INFERIOR', (50, 228)),
]

HEADER = (14, 12, 626, 32)
FOOTER_Y = 334
TANCA = (552, 333, 620, 349)
MARK = 9                    # el punt de «sou aquí»

# ─── Ni un ou: el plànol a 288 d'alt ──────────────────────────────────────
# La geometria de dalt és la de l'original (a 360). Aquí s'encongeix en vertical, per trams: la capçalera, cada
# coberta i el peu s'aprimen una mica (≈0,8), i els espais entre cobertes (on van els rètols) es queden prou alts.
# En una pantalla més alta, la GUI va centrada i un fons del color de la planxa omple la resta.
_TRAMS = [(0, 0), (6, 4), (12, 8), (32, 24), (48, 28), (104, 75), (124, 89), (230, 177), (244, 191), (330, 258),
          (334, 262), (349, 277), (360, 288)]


def Y(v):
    """Una y de l'original (360) al plànol de 288."""
    for (a, fa), (b, fb) in zip(_TRAMS, _TRAMS[1:]):
        if v <= b:
            return round(fa + (v - a) * (fb - fa) / (b - a))
    return H


SALES = {k: (x0, Y(y0), x1, Y(y1)) for k, (x0, y0, x1, y1) in SALES.items()}
DECORS = [(x0, Y(y0), x1, Y(y1), label) for x0, y0, x1, y1, label in DECORS]
STAIRS = [(x0, Y(y0), x1, Y(y1)) for x0, y0, x1, y1 in STAIRS]
DECKS = [([(x, Y(y)) for x, y in poly], label, (lx, Y(ly))) for poly, label, (lx, ly) in DECKS]
HEADER = (HEADER[0], Y(HEADER[1]), HEADER[2], Y(HEADER[3]))
FOOTER_Y = Y(FOOTER_Y)
TANCA = (TANCA[0], Y(TANCA[1]), TANCA[2], Y(TANCA[3]))


def camel(sala):
    return 'sala' + ''.join(p.capitalize() for p in sala.split('_'))


# ─── Dibuix ─────────────────────────────────────────────────────────────────

def rect(d, r, fill=None, outline=None, width=1):
    x0, y0, x1, y1 = r
    d.rectangle((x0, y0, x1 - 1, y1 - 1), fill=fill, outline=outline, width=width)


def planks(d, r):
    x0, y0, x1, y1 = r
    for y in range(y0 + 4, y1, 5):
        d.line((x0 + 1, y, x1 - 2, y), fill=PLANK)


def stairs(d, r):
    x0, y0, x1, y1 = r
    n = 5
    for i in range(n + 1):
        x = x0 + 4 + i * (x1 - x0 - 8) // n
        d.line((x, y0 + 5, x, y1 - 6), fill=INK)
    d.line((x0 + 4, (y0 + y1) // 2, x1 - 5, (y0 + y1) // 2), fill=INK)


def route(d, r):
    """Ruta d'evacuació: una línia verda de traços amb fletxes cap a les sortides."""
    x0, y0, x1, y1 = r
    y = (y0 + y1) // 2 + 6
    for x in range(x0 + 6, x1 - 8, 6):
        d.line((x, y, x + 3, y), fill=ROUTE)
    d.polygon([(x1 - 9, y - 3), (x1 - 5, y), (x1 - 9, y + 3)], fill=ROUTE)


def raft(d, x, y):
    d.rounded_rectangle((x, y, x + 12, y + 5), radius=2, fill=RED, outline=INK)


def extinguisher(d, x, y):
    d.rectangle((x, y, x + 3, y + 5), fill=RED)


def text(img, glyphs, s, x, y, color, center=None):
    if center:
        x = center - text_width(glyphs, s) // 2
    draw_text(img, glyphs, s, x, y, color, outline=None)


def planol(noms):
    img = Image.new('RGBA', (W, H), BOARD + (255,))
    d = ImageDraw.Draw(img)
    reg, bold = font640(False), font640(True)
    # el full, amb ombra i cargols
    d.rounded_rectangle((10, 8, W - 9, H - 7), radius=4, fill=PAPER_SHADE)
    d.rounded_rectangle((8, 6, W - 11, H - 9), radius=4, fill=PAPER, outline=INK)
    for x, y in ((14, 10), (W - 17, 10), (14, H - 15), (W - 17, H - 15)):
        d.ellipse((x, y, x + 3, y + 3), fill=(150, 150, 140), outline=INK)
    # la capçalera verda
    rect(d, HEADER, fill=GREEN)
    text(img, bold, "PLÀNOL D'EMERGÈNCIA · ARENGA", 0, HEADER[1] + 1, (236, 246, 238), center=(HEADER[0] + HEADER[2]) // 2)
    text(img, reg, 'POPA', HEADER[0] + 6, HEADER[1] + 1, (200, 230, 210))
    text(img, reg, 'PROA', HEADER[2] - 6 - text_width(reg, 'PROA'), HEADER[1] + 1, (200, 230, 210))
    # les cobertes
    for poly, label, (lx, ly) in DECKS:
        d.polygon(poly, fill=EXT, outline=INK)
        # els taulons de la coberta, només dins el casc
        mask = Image.new('L', (W, H), 0)
        ImageDraw.Draw(mask).polygon(poly, fill=255)
        ImageDraw.Draw(mask).line(poly + [poly[0]], fill=0)
        layer = Image.new('RGBA', (W, H), (0, 0, 0, 0))
        ys = [y for _, y in poly]
        for y in range(min(ys) + 4, max(ys), 5):
            ImageDraw.Draw(layer).line((0, y, W, y), fill=PLANK)
        img.paste(layer, (0, 0), Image.composite(layer.getchannel('A'), mask, mask).point(lambda v: 255 if v > 0 else 0))
        text(img, reg, label, lx, ly, GREYTXT)
    # les sales i el que no és jugable
    for x0, y0, x1, y1, label in DECORS:
        rect(d, (x0, y0, x1, y1), fill=DECOR, outline=INK)
        if label:
            text(img, reg, label, 0, (y0 + y1) // 2 - 9, GREYTXT, center=(x0 + x1) // 2)
    for sala, r in SALES.items():
        if sala in EXTERIORS:
            rect(d, r, fill=EXT, outline=INK)
            planks(d, r)
        elif sala in CORRIDORS:
            rect(d, r, fill=CORR, outline=INK)
            route(d, r)
        else:
            rect(d, r, fill=ROOM, outline=INK)
    for r in STAIRS:
        stairs(d, r)
    # balses salvavides i extintors
    raft(d, 60, Y(132))
    raft(d, 60, Y(216))
    raft(d, 512, Y(134))
    extinguisher(d, 240, Y(182))
    extinguisher(d, 490, Y(182))
    extinguisher(d, 240, Y(294))
    # la llegenda, al peu
    legend_x = 26
    mark(d, legend_x, FOOTER_Y + 3)
    text(img, reg, 'Sou aquí', legend_x + MARK + 4, FOOTER_Y, INK)
    lx = legend_x + MARK + 8 + text_width(reg, 'Sou aquí') + 10
    d.line((lx, FOOTER_Y + 8, lx + 12, FOOTER_Y + 8), fill=ROUTE, width=2)
    text(img, reg, 'Ruta d\'evacuació', lx + 16, FOOTER_Y, INK)
    lx += 16 + text_width(reg, "Ruta d'evacuació") + 10
    raft(d, lx, FOOTER_Y + 6)
    text(img, reg, 'Balsa', lx + 16, FOOTER_Y, INK)
    return img


def mark(d, x, y, fill=RED, letter=None):
    d.ellipse((x, y, x + MARK - 1, y + MARK - 1), fill=fill, outline=INK)
    if letter is None:
        d.rectangle((x + 3, y + 3, x + 5, y + 5), fill=(255, 255, 255))


def tile(r, kind):
    x0, y0, x1, y1 = r
    w, h = x1 - x0, y1 - y0
    im = Image.new('RGBA', (w, h), (0, 0, 0, 0))
    d = ImageDraw.Draw(im)
    if kind == 'hover':
        d.rectangle((1, 1, w - 2, h - 2), fill=HOVER + (255,), outline=HOVER_EDGE + (255,))
        d.rectangle((2, 2, w - 3, h - 3), outline=HOVER_EDGE + (255,))
    elif kind == 'off':
        d.rectangle((1, 1, w - 2, h - 2), fill=PAPER + (170,))
        for k in range(-h, w, 5):
            d.line((k, h - 1, k + h, 0), fill=(150, 150, 142, 255))
    return im


def marker(fill, letter, glyphs):
    im = Image.new('RGBA', (MARK + 2, MARK + 2), (0, 0, 0, 0))
    d = ImageDraw.Draw(im)
    if letter:
        d.ellipse((0, 0, MARK + 1, MARK + 1), fill=fill, outline=INK)
        draw_text(im, glyphs, letter, (MARK + 2 - text_width(glyphs, letter)) // 2, -3, INK, outline=None)
    else:
        mark(d, 1, 1)
    return im


def gui_json(noms):
    controls = [
        # Ni un ou: el fons de la planxa, que omple la pantalla si és més alta que el plànol (anchorY: stretch)
        {'type': 'button', 'id': 'fons', 'x': 0, 'y': 0, 'width': W, 'height': H, 'backgroundAnchor': 'top-left',
         'text': '', 'font': 'niunou-regular', 'fontSize': 8, 'textColor': '#ffffff', 'backgroundTag': '',
         'backgroundColor': '#%02x%02x%02x' % BOARD,
         'backgroundColorStates': {k: '#%02x%02x%02x' % BOARD for k in ('hover', 'pressed', 'disabled')},
         'zIndex': 0, 'anchorY': 'stretch'},
        {'type': 'image', 'id': 'planol', 'x': 0, 'y': 0, 'tag': 'planol', 'backgroundAnchor': 'screen',
         'clickable': False, 'zIndex': 1}]
    for sala, (x0, y0, x1, y1) in SALES.items():
        cid = camel(sala)
        controls.append({
            'type': 'button', 'id': cid, 'x': x0, 'y': y0, 'width': x1 - x0, 'height': y1 - y0,
            'backgroundAnchor': 'top-left', 'text': noms.get(sala, sala), 'font': 'niunou-regular', 'fontSize': 8,
            'textColor': '#282826', 'textAlign': 'center', 'textOffsetX': 0, 'textOffsetY': 0,
            'textColorStates': {'hover': '#1c5a3a', 'pressed': '#1c5a3a'},
            'backgroundTag': sala, 'states': {'hover': f'{sala}-hover', 'pressed': f'{sala}-hover'}, 'zIndex': 2,
        })
        controls.append({'type': 'image', 'id': f'{cid}Off', 'x': x0, 'y': y0, 'tag': f'{sala}-off',
                         'backgroundAnchor': 'top-left', 'clickable': False, 'visible': False, 'zIndex': 3})
    for mid, tag in (('aqui', 'aqui'), ('altraIri', 'altraIri'), ('altraVet', 'altraVet')):
        controls.append({'type': 'image', 'id': mid, 'x': 0, 'y': 0, 'tag': tag, 'backgroundAnchor': 'top-left',
                         'clickable': False, 'visible': False, 'zIndex': 4})
    x0, y0, x1, y1 = TANCA
    controls.append({
        'type': 'text', 'id': 'peu', 'x': 320, 'y': FOOTER_Y, 'text': '', 'font': 'niunou-regular', 'fontSize': 8,
        'color': '#282826', 'align': 'left', 'zIndex': 4})
    controls.append({
        'type': 'button', 'id': 'tanca', 'x': x0, 'y': y0, 'width': x1 - x0, 'height': y1 - y0,
        'backgroundAnchor': 'top-left', 'text': noms.get('@tanca', 'Tanca'), 'font': 'niunou-negreta', 'fontSize': 8,
        'textColor': '#ecf6ee', 'textAlign': 'center', 'textColorStates': {'hover': '#ffffff'}, 'backgroundTag': '',
        'backgroundColor': '#2c7852', 'backgroundColorStates': {'hover': '#3a9a6a', 'pressed': '#1c5a3a',
                                                                 'disabled': '#2c7852'}, 'zIndex': 4})
    return {'id': 'mapa', 'name': 'Mapa',
            'description': "El plànol d'emergència de l'Arenga (games/ni-un-ou/adapters/benne/tools/hd640/mapa.py).",
            'visible': False, 'display': {'aseprite': True}, 'modal': True, 'zIndex': 105, 'anchorY': 'center',
            'controls': controls}


def main():
    loc = json.loads(LOCALES.read_text(encoding='utf-8'))
    noms = {s: loc.get(f'ui.mapa.sala.{s}', s) for s in SALES}
    noms['@tanca'] = loc.get('ui.mapa.tanca', 'Tanca')
    reg = font640(False)
    bg = planol(noms)
    items = [(bg, 'planol', (0, 0), (W, H))]
    for sala, r in SALES.items():
        for kind, tag in (('normal', sala), ('hover', f'{sala}-hover'), ('off', f'{sala}-off')):
            im = tile(r, kind)
            items.append((im, tag, (0, 0), im.size))
    for tag, fill, letter in (('aqui', RED, None), ('altraIri', (242, 178, 92), 'I'), ('altraVet', (127, 216, 230), 'V')):
        im = marker(fill, letter, reg)
        items.append((im, tag, (0, 0), im.size))
    write_sheet(GAME / 'assets/images/guis/mapa', 'mapa', items)
    gdir = GAME / 'guis/mapa'
    gdir.mkdir(parents=True, exist_ok=True)
    (gdir / 'mapa.gui.json').write_text(json.dumps(gui_json(noms), indent=2, ensure_ascii=False) + '\n')
    print(f'✔ {GAME / "assets/images/guis/mapa/mapa.png"} i {gdir / "mapa.gui.json"}')
    if len(sys.argv) > 1:
        preview(bg, noms, Path(sys.argv[1]))


def preview(bg, noms, out):
    """Com es veu: els noms, una sala amb el ratolí a sobre (la cuina), dues de tancades i els punts, ×3."""
    out.mkdir(parents=True, exist_ok=True)
    img = bg.copy()
    reg = font640(False)
    for sala, r in SALES.items():
        if sala == 'cuina':
            img.alpha_composite(tile(r, 'hover'), (r[0], r[1]))
    for sala, (x0, y0, x1, y1) in SALES.items():
        draw_text(img, reg, noms[sala], (x0 + x1) // 2 - text_width(reg, noms[sala]) // 2, (y0 + y1) // 2 - 9,
                  (40, 40, 38), outline=None)
    for sala in ('caixa_cadenes', 'diposit2', 'pal'):
        r = SALES[sala]
        img.alpha_composite(tile(r, 'off'), (r[0], r[1]))
    img.alpha_composite(marker(RED, None, reg), (SALES['infermeria'][0] + 3, SALES['infermeria'][1] + 3))
    img.alpha_composite(marker((242, 178, 92), 'I', reg), (SALES['pallol'][0] + 3, SALES['pallol'][1] + 3))
    d = ImageDraw.Draw(img)
    x0, y0, x1, y1 = TANCA
    d.rectangle((x0, y0, x1 - 1, y1 - 1), fill=(44, 120, 82))
    draw_text(img, font640(True), noms['@tanca'], (x0 + x1) // 2 - text_width(font640(True), noms['@tanca']) // 2, y0 - 2,
              (236, 246, 238), outline=None)
    draw_text(img, reg, 'Clica on vols anar.', 320, FOOTER_Y, (40, 40, 38), outline=None)
    nearest(img, (W * 3, H * 3)).save(out / 'mapa.png')
    print(f'✔ {out / "mapa.png"}')


if __name__ == '__main__':
    main()
