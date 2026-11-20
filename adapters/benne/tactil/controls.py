"""
La targeta «Com es juga» de la interfície tàctil (GUI `controls`): com es juga amb el dit o amb el ratolí, on es
demana una pista, amb el ratolí la casella per girar-ne els botons, i el botó «D'acord». S'obre des de les opcions («Controls»: el runtime és
tactil/runtime/controls.ts); el script és tactil/guis/controls/controls.gui.ts.

Compartit: el crida el hud.py de cada joc amb les seves peces (el panell de 9 trossos, la casella i la tecla de
gui_rest.py, les fonts i els colors), així la targeta té l'estil de cada joc. Les icones (el dit, el ratolí) es
dibuixen aquí, amb els colors que li passa el joc; la dels punts és la del HUD, i la de la pista, la que el joc hi posi (el botó del menú o el de la pista).

    from controls import build_controls          # (amb adapters/benne/tactil al sys.path)
    build_controls(GAME, write_sheet=..., ...)
"""
import json
from pathlib import Path

from PIL import Image, ImageDraw

W, H = 640, 288                 # l'alçada mínima (la GUI va centrada si la pantalla és més alta)
PANELL = (120, 12, 400, 264)    # x, y, amplada, alçada
FILES = 4                       # tocar, mantenir premut, l'inventari i els punts, la pista
ICONA = 32
KEY = (91, 27)


# ─── Icones (32×32, art de píxels amb tres colors: tinta, accent, ombra) ─────

def _ma(d, ink, shadow, x0=0, y0=0):
    """Una mà que assenyala avall amb l'índex (el dit, a dalt: la mà, a sota)."""
    # l'índex
    d.rounded_rectangle((x0 + 12, y0 + 3, x0 + 17, y0 + 17), radius=2, fill=ink, outline=shadow)
    # el palmell i els altres dits plegats
    d.rounded_rectangle((x0 + 9, y0 + 14, x0 + 23, y0 + 27), radius=3, fill=ink, outline=shadow)
    for x in (17, 20):
        d.line((x0 + x, y0 + 15, x0 + x, y0 + 19), fill=shadow)
    d.line((x0 + 11, y0 + 24, x0 + 21, y0 + 24), fill=shadow)


def icona_dit_toc(ink, accent, shadow):
    im = Image.new('RGBA', (ICONA, ICONA), (0, 0, 0, 0))
    d = ImageDraw.Draw(im)
    d.arc((5, 0, 24, 8), 200, 340, fill=accent, width=1)          # l'onada del toc
    d.arc((8, 1, 21, 6), 200, 340, fill=accent, width=1)
    _ma(d, ink, shadow, y0=3)
    return im


def icona_dit_premut(ink, accent, shadow):
    im = Image.new('RGBA', (ICONA, ICONA), (0, 0, 0, 0))
    d = ImageDraw.Draw(im)
    _ma(d, ink, shadow, x0=-4, y0=3)
    # el rellotget: mantenir premut
    d.ellipse((19, 1, 31, 13), fill=shadow, outline=accent)
    d.line((25, 4, 25, 7), fill=accent)
    d.line((25, 7, 28, 9), fill=accent)
    return im


def icona_ratoli(boto, ink, accent, shadow):
    """Un ratolí amb el botó `boto` ('esq' o 'dret') encès."""
    im = Image.new('RGBA', (ICONA, ICONA), (0, 0, 0, 0))
    d = ImageDraw.Draw(im)
    d.rounded_rectangle((8, 3, 23, 29), radius=7, fill=ink, outline=shadow)
    if boto == 'esq':
        d.rounded_rectangle((9, 4, 15, 13), radius=3, fill=accent)
    else:
        d.rounded_rectangle((16, 4, 22, 13), radius=3, fill=accent)
    d.line((8, 14, 23, 14), fill=shadow)
    d.line((15, 4, 15, 14), fill=shadow)
    d.line((15, 0, 15, 3), fill=shadow)                          # el cable
    return im


def _centrada(im):
    """La icona, centrada en un quadrat de 32×32 (com les altres)."""
    out = Image.new('RGBA', (ICONA, ICONA), (0, 0, 0, 0))
    out.paste(im, ((ICONA - im.width) // 2, (ICONA - im.height) // 2), im)
    return out


# ─── La GUI ──────────────────────────────────────────────────────────────────

def build_controls(game, *, write_sheet, nine_slice, nine_slices, checkbox, key_image, punts, pista,
                   font, bold, text, title, outline, hover, ink, accent, shadow):
    """Escriu guis/controls/controls.gui.json i assets/images/guis/controls/ al projecte Benne `game`.

    - write_sheet, nine_slice, nine_slices, checkbox, key_image: les de hd640/gui_rest.py del joc;
    - punts: la icona dels punts del HUD (32×32);
    - pista: la icona de la quarta fila, on es demana una pista (fins a 32×32; va centrada);
    - font, bold: les fonts; text, title, outline, hover: colors del text (com a les opcions);
    - ink, accent, shadow: colors RGB(A) de les icones.
    """
    pad = Image.new('RGBA', (93, 27), (0, 0, 0, 0))
    pad.paste(nine_slice(), (0, 0))
    items = [(pad, '9-slice-BG', (0, 0), (93, 27))]
    for st in ('checkbox', 'checkbox-hover', 'checkbox-checked', 'checkbox-checked-hover'):
        items.append((checkbox(st), st, (0, 0), (93, 27)))
    kw, kh = KEY
    for st in ('', '-hover', '-pressed'):
        im = key_image(kw, kh, st)
        items.append((im, f'key-{kw}x{kh}{st}', (0, 0), im.size))
    icones = {
        'dit0': icona_dit_toc(ink, accent, shadow), 'dit1': icona_dit_premut(ink, accent, shadow),
        'ratoli0': icona_ratoli('esq', ink, accent, shadow), 'ratoli1': icona_ratoli('dret', ink, accent, shadow),
        'punts': punts, 'pista': _centrada(pista),
    }
    for tag, im in icones.items():
        items.append((im, tag, (0, 0), im.size))
    out = Path(game)
    write_sheet(out / 'assets/images/guis/controls', 'controls', items, cols=4, slices=nine_slices())

    px, py, pw, ph = PANELL
    controls = [
        # tot el fons (fosc, mig transparent): la targeta tapa el joc; tocar fora no la tanca (cal «D'acord»)
        {'type': 'button', 'id': 'fons', 'x': 0, 'y': 0, 'width': W, 'height': H, 'backgroundAnchor': 'top-left',
         'text': '', 'font': font, 'fontSize': 8, 'textColor': '#ffffff', 'backgroundTag': '',
         'backgroundColor': '#000000', 'backgroundColorStates': {'hover': '#000000', 'pressed': '#000000'},
         'zIndex': 1, 'anchorY': 'stretch'},
        {'type': 'nineSliceImage', 'id': 'panell', 'x': px, 'y': py, 'width': pw, 'height': ph, 'tag': '9-slice-BG',
         'sliceNames': {'topLeft': 'TopLeft', 'topCenter': 'TopMid', 'topRight': 'TopRight', 'middleLeft': 'MidLeft',
                        'center': 'Mid', 'middleRight': 'MidRight', 'bottomLeft': 'BottomLeft',
                        'bottomCenter': 'BottomMid', 'bottomRight': 'BottomRight'}, 'zIndex': 2},
        {'type': 'text', 'id': 'titol', 'x': W // 2, 'y': py + 12, 'text': '', 'font': bold, 'fontSize': 8,
         'color': title, 'align': 'center', 'zIndex': 3},
    ]
    y0, pas = py + 36, 40
    for i in range(FILES):
        y = y0 + i * pas
        # les icones de les dues maneres (el script mostra les d'ara); la tercera (els punts) i la quarta (la pista)
        # són de totes dues
        for manera in ('dit', 'ratoli'):
            tag = {2: 'punts', 3: 'pista'}.get(i, f'{manera}{i}')
            controls.append({'type': 'image', 'id': f'{manera}{i}', 'x': px + 22, 'y': y - 4, 'tag': tag,
                             'backgroundAnchor': 'top-left', 'clickable': False, 'visible': False, 'zIndex': 3})
        controls.append({'type': 'text', 'id': f'text{i}', 'x': px + 66, 'y': y, 'text': '', 'font': font,
                         'fontSize': 8, 'color': text, 'align': 'left', 'wordWrapWidth': pw - 66 - 22, 'zIndex': 3,
                         'textOutline': {'enabled': True, 'color': outline, 'sides': 'bottomRight'}})
    yb = py + ph - 40
    # amb el ratolí: girar els botons ara mateix (el script només ho mostra amb el ratolí), en una fila sencera
    yi = yb - 30
    controls += [
        {'type': 'checkbox', 'id': 'intercanvia', 'x': px + 22, 'y': yi + 4, 'width': 21, 'height': 21,
         'backgroundAnchor': 'top-left', 'tag': 'checkbox',
         'states': {'uncheckedHover': 'checkbox-hover', 'checked': 'checkbox-checked',
                    'checkedHover': 'checkbox-checked-hover'}, 'checked': False, 'visible': False, 'zIndex': 3},
        {'type': 'text', 'id': 'intercanviaText', 'x': px + 48, 'y': yi + 6, 'text': '', 'font': font, 'fontSize': 8,
         'color': text, 'align': 'left', 'visible': False, 'zIndex': 3},
        {'type': 'button', 'id': 'dacord', 'x': px + pw - 22 - kw, 'y': yb, 'width': kw, 'height': kh,
         'backgroundAnchor': 'top-left', 'text': '', 'font': font, 'fontSize': 8, 'textColor': text,
         'textAlign': 'center', 'textOffsetX': 0, 'textOffsetY': -2, 'backgroundTag': f'key-{kw}x{kh}',
         'states': {'hover': f'key-{kw}x{kh}-hover', 'pressed': f'key-{kw}x{kh}-pressed'},
         'textColorStates': {'hover': hover, 'pressed': hover},
         'textOutline': {'enabled': True, 'color': outline, 'sides': 'bottomRight'}, 'zIndex': 3},
    ]
    gui = {'id': 'controls', 'name': 'Controls',
           'description': 'Com es juga: el dit o el ratolí (adapters/benne/tactil/controls.py)',
           'visible': False, 'display': {'aseprite': True}, 'modal': True, 'zIndex': 115, 'anchorY': 'center',
           'controls': controls}
    d = out / 'guis/controls'
    d.mkdir(parents=True, exist_ok=True)
    (d / 'controls.gui.json').write_text(json.dumps(gui, indent=2, ensure_ascii=False) + '\n')
