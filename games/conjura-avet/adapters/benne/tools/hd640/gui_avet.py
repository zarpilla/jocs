#!/usr/bin/env python3
"""
La Conjura de l'Avet: les altres GUI del joc (menú, desar, carregar, opcions, diàleg, display-text, speaking-text,
historial i els botons de la portada) amb la paleta del HUD (hd640/hud.py): fusta fosca, pedra amb l'escacat, el
vermell de la cera com a accent, llautó i pergamí.

Fa el mateix que hd640/gui_rest.py + el pas `guis()` de hd640/aplica.py, però:
  - amb la paleta canviada només dins d'aquest procés (la posa hud.py en importar-lo; aquí s'hi afegeixen els colors
    dels textos, dels camps i de les llistes, el fons del diàleg i els botons de la portada, que gui_rest.py té
    escrits a mà amb els colors d'Aigua Verne);
  - sense la barra de verbs ni el punter (el HUD és de hud.py; el punter no canvia);
  - a partir d'una còpia dels .gui.json del projecte amb el pas de pantalla.py desfet (la marca [288]: els controls
    tornen a la posició de 360), perquè pantalla.py el torni a fer bé després.

Escriu a hd640/guis/<gui>/ (com gui_rest.py) i ho copia al projecte Benne (conjura-avet/src/game). Després:

    python3 hd640/gui_avet.py && python3 hd640/hud.py && python3 hd640/pantalla.py

(hud.py deixa buits els textos de la targeta «Com es juga»: els torna a posar el sync.)
"""
import json
import os
import shutil
import sys
import tempfile
from pathlib import Path

from PIL import Image, ImageDraw

HERE = Path(__file__).resolve().parent
TOOLS = HERE.parent
GAME = TOOLS.parents[2] / 'conjura-avet/src/game'
GUIS = ('dialog', 'display-text', 'game-menu', 'save-menu', 'load-menu', 'settings-menu', 'portada', 'speaking-text',
        'historial')
MARQUES = ('.provisional', '.generat', '.canvia-provisional')


def desfes_pantalla(tmp):
    """Els .gui.json de la còpia, com eren abans de pantalla.py (a 360, sense la marca [288])."""
    sys.path.insert(0, str(HERE))
    import pantalla as pt
    for name, (dy, _anchor) in pt.PUJA.items():
        p = tmp / 'guis' / name / f'{name}.gui.json'
        if not p.exists():
            continue
        gui = json.loads(p.read_text())
        desc = gui.get('description') or ''
        if pt.MARCA not in desc:
            continue
        for c in gui['controls']:
            if 'gridPlacement' in c:
                continue
            if name == 'portada' and c.get('id') == 'version':
                c['y'] = pt.H0 - (pt.H - c['y'])
            elif 'y' in c:
                c['y'] += dy
            if c.get('backgroundAnchor') == 'screen':
                c['backgroundOffsetY'] = c.get('backgroundOffsetY', 0) + dy
        gui['description'] = desc.replace(f' {pt.MARCA}', '').replace(pt.MARCA, '')
        gui.pop('anchorY', None)
        p.write_text(json.dumps(gui, indent=2, ensure_ascii=False) + '\n')


def main():
    tmp = Path(tempfile.mkdtemp(prefix='gui_avet_'))
    shutil.copytree(GAME / 'guis', tmp / 'guis')
    shutil.copy2(GAME / 'game-config.json', tmp / 'game-config.json')
    desfes_pantalla(tmp)
    os.environ['BENNE_GAME'] = str(tmp)
    sys.path.insert(0, str(TOOLS))

    import hd640.hud as hud                    # posa la paleta del HUD a hd640/gui.py i hd640/gui_rest.py
    import hd640.gui_rest as gr
    import hd640.gui as vg
    from hd.pix import Canvas, hr

    FUSTA, CERA, LLAUTO, NEGRE = hud.FUSTA, hud.CERA, hud.LLAUTO, hud.NEGRE_B
    gr.TEXT_HOVER = gr.OPTION_HOVER = hud.TEXT_HOVER
    gr.TITLE = hud.TITLE
    gr.DISABLED = '#6c6152'

    def menu_colors(c):
        """Els textos, els camps i les llistes dels menús: pergamí, títols de llautó, files de fusta fosca (la
        seleccionada, de cera fosca)."""
        t = c.get('type')
        if t == 'text':
            c['color'] = gr.TITLE if c.get('id') == 'title' else gr.LABEL
        if t == 'textInput':
            c.update({'backgroundColor': '#120d0a', 'hoverBackgroundColor': '#1d1510', 'color': gr.LABEL,
                      'outlineColor': '#5a4630', 'focusedOutlineColor': '#c9973e', 'caretColor': gr.TEXT_HOVER,
                      'placeholder': 'Nom de la partida...'})
        if t == 'listBox':
            c.update({'normalBackgroundColor': '#140f0b', 'hoverBackgroundColor': '#261c14',
                      'selectedBackgroundColor': '#5c1a14', 'textColor': gr.LABEL, 'selectedTextColor': '#fff4dc',
                      'placeholderTextColor': gr.DISABLED})

    def taulons(cv, y0, y1):
        """Fusta fosca en taulons horitzontals, amb la veta i les juntes."""
        for y in range(y0, y1 + 1):
            junta = (y - y0) % 17 == 16
            for x in range(gr.W):
                v = 3.0 + (hr(x // 6, y // 2, 4) - 0.5) * 0.5 + (hr(x // 31, (y - y0) // 17, 3) - 0.5) * 0.5
                cv.put(x, y, FUSTA, 1.2 if junta else v, lit=0)
        for i in range(40):                                                 # els nusos i les vetes fosques
            x, y = int(hr(i, 1) * gr.W), int(y0 + 6 + hr(i, 2) * (y1 - y0 - 8))
            for k in range(4 + int(hr(i, 3) * 8)):
                cv.put(x + k, y, FUSTA, 2.2, lit=0)

    def dialog_bg():
        """El diàleg: taulons de fusta fosca, la franja de pedra escacada a dalt i el quadre de les opcions enfonsat,
        fosc, amb cantoneres de llautó."""
        cv = Canvas(gr.W, gr.H, transparent=True)
        taulons(cv, gr.DLG_TOP, gr.H - 1)
        hud.escacat(cv, 0, gr.W - 1, gr.DLG_TOP, 4)
        gr.well(cv, 20, 267, 632, 355, face=1.2, brass=False)
        cv.hline(21, 631, 268, NEGRE, 1.0, lit=0)
        cv.vline(21, 268, 354, NEGRE, 1.0, lit=0)
        cv.rect(22, 269, 630, 353, FUSTA, 1.0, lit=0)
        gr.corners(cv, 24, 271, 628, 351, n=8, ramp=LLAUTO, lvl=3.4)
        for ax, ay in gr.DLG_ARROWS.values():
            gr.box(cv, ax, ay, ax + 11, ay + 32, FUSTA, 4.2)
            cv.hline(ax + 1, ax + 10, ay + 1, FUSTA, 5.2, lit=0)
        for x, y in ((8, 309), (635, 270), (635, 349), (8, 352)):
            vg.big_rivet(cv, x, y)
        return cv.img

    def cover_button(x0, y0, w, h, hover):
        """Botó de la portada: una placa de fusta fosca, gairebé opaca, amb la vora de llautó (2 px), cantons
        retallats, filet de llum a dalt i dues ratlletes a cada costat; en hover, la vora es torna vermell de cera
        i s'encenen dos punts de llum d'espelma."""
        img = Image.new('RGBA', (gr.W, gr.H), (0, 0, 0, 0))
        d = ImageDraw.Draw(img)
        x1, y1 = x0 + w - 1, y0 + h - 1
        fill = FUSTA[4] + (242,) if hover else FUSTA[3] + (232,)
        vora = CERA[4] if hover else LLAUTO[3]
        vora2 = CERA[2] if hover else LLAUTO[1]
        llum = FUSTA[6] if hover else FUSTA[5]
        d.rectangle([x0 + 2, y0 + 2, x1 - 2, y1 - 2], fill=fill)
        for a, b in (((x0 + 3, y0), (x1 - 3, y0)), ((x0 + 3, y1), (x1 - 3, y1)), ((x0, y0 + 3), (x0, y1 - 3)),
                     ((x1, y0 + 3), (x1, y1 - 3))):
            d.line([a, b], fill=vora + (255,))
        for (cx, cy, sx, sy) in ((x0, y0, 1, 1), (x1, y0, -1, 1), (x0, y1, 1, -1), (x1, y1, -1, -1)):
            img.putpixel((cx + sx, cy + 2 * sy), vora + (255,))
            img.putpixel((cx + 2 * sx, cy + sy), vora + (255,))
        d.line([(x0 + 3, y0 + 1), (x1 - 3, y0 + 1)], fill=vora2 + (255,))
        d.line([(x0 + 1, y0 + 3), (x0 + 1, y1 - 3)], fill=vora2 + (255,))
        d.line([(x0 + 3, y1 - 1), (x1 - 3, y1 - 1)], fill=NEGRE[0] + (255,))
        d.line([(x1 - 1, y0 + 3), (x1 - 1, y1 - 3)], fill=NEGRE[0] + (255,))
        d.line([(x0 + 4, y0 + 3), (x1 - 4, y0 + 3)], fill=llum + (255,))
        for k in (8, 13):
            for side in (x0 + k, x1 - k):
                for dy in (-1, 0, 1):
                    img.putpixel((side, y0 + h // 2 + dy), vora + (255 if dy == 0 else 140,))
        if hover:
            for k in (3, 4):
                img.putpixel((x0 + k + 15, y0 + h // 2), hud.LLUM[7] + (255,))
                img.putpixel((x1 - k - 15, y0 + h // 2), hud.LLUM[7] + (255,))
        return img

    nine_slice = gr.nine_slice

    def marc_llauto():
        """El marc dels menús, de llautó (el vermell de la cera queda per al que s'assenyala)."""
        gr.TARONJA = LLAUTO
        try:
            return nine_slice()
        finally:
            gr.TARONJA = CERA

    gr.menu_colors, gr.dialog_bg, gr.cover_button, gr.nine_slice = menu_colors, dialog_bg, cover_button, marc_llauto
    gr.build_dialog()
    gr.build_menus()
    gr.build_portada()
    gr.build_jsons_only()
    hist = gr.OUT / 'historial/historial.gui.json'
    if hist.exists():                                                     # els dos colors escrits a mà
        gui = json.loads(hist.read_text())
        for c in gui['controls']:
            if c.get('id') == 'fons':
                c['backgroundColor'] = '#0c0907'
            if c.get('id') == 'peu':
                c['color'] = '#8a7e66'
        hist.write_text(json.dumps(gui, indent=2, ensure_ascii=False) + '\n')

    # el pas guis() d'aplica.py, només amb aquestes GUI
    for name in GUIS:
        src = gr.OUT / name
        if not src.is_dir():
            continue
        art = GAME / 'assets/images/guis' / name
        for f in src.iterdir():
            if f.name.endswith('.gui.json'):
                shutil.copy2(f, GAME / 'guis' / name / f.name)
            elif f.suffix in ('.png', '.json'):
                art.mkdir(parents=True, exist_ok=True)
                shutil.copy2(f, art / f.name)
        if art.exists():
            for m in MARQUES:
                (art / m).unlink(missing_ok=True)
            (art / f'{name}.aseprite').unlink(missing_ok=True)
        print(f'  {name}')
    shutil.rmtree(tmp, ignore_errors=True)
    print(f'✔ GUI amb la paleta del HUD a {GAME}. Ara: python3 hd640/hud.py && python3 hd640/pantalla.py')


if __name__ == '__main__':
    main()
