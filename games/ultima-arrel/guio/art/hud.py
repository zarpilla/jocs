#!/usr/bin/env python3
"""
L'Última Arrel — làmina de revisió del HUD (adapters/benne/tools/hd640/hud.py), ×3, sense tocar el projecte Benne.

A dalt, el botó de la pista (la lupa: normal, hover i pressed) i els altres botons (menú, punts, bossa) damunt
d'un tros de bosc fosc; a sota, la safata de l'inventari amb unes quantes icones i el tauler de la franja.
Ús: python3 hud.py  →  hud.png
"""
import sys
from pathlib import Path

from PIL import Image, ImageDraw

HERE = Path(__file__).resolve().parent
TOOLS = HERE.parents[1] / 'adapters/benne/tools'
sys.path.insert(0, str(TOOLS))
sys.path.insert(0, str(TOOLS / 'hd640'))
from pixels import nearest  # noqa: E402
import hud as H  # noqa: E402
from hd640 import items  # noqa: E402

S = 3


def main():
    cw, ch = H.vg.CANVIA[2], H.CANVIA_H
    mx, my, ms = H.vg.MENU
    peces = [H.lupa_boto(cw, ch), H.lupa_boto(cw, ch, hover=True), H.lupa_boto(cw, ch, pressed=True),
             H.crop_bar(H.vg.menu_button, mx, my, ms, ms), H.boto(H.punts_icon), H.boto(H.punts_icon, hover=True),
             H.boto(H.bossa_icon), H.boto(H.bossa_icon, hover=True)]
    safata = H.safata()
    tauler = H.tauler()
    W = max(tauler.width, safata.width) + 16
    Ht = 8 + ch + 12 + safata.height + 12 + tauler.height + 8
    out = Image.new('RGBA', (W, Ht), (34, 40, 26, 255))
    d = ImageDraw.Draw(out)
    for y in range(Ht):                                       # un fons de bosc, fosc i càlid
        d.line([(0, y), (W, y)], fill=(30 + y // 12, 36 + y // 16, 22))
    x = 8
    for p in peces:
        out.alpha_composite(p, (x, 8))
        x += p.width + 10
    y = 8 + ch + 12
    out.alpha_composite(safata, (8, y))
    fx0, slots_x, fx1, top = H.safata_xy()
    sx, sy = H.SAFATA[0], H.SAFATA[1]
    for i, iid in enumerate(['walkie', 'lupa', 'llibreta', 'pila_llimona', 'fil_saba', 'pot_melmelada', 'xiulet']):
        out.alpha_composite(items.render(iid), (8 + slots_x - sx + i * (H.SLOT_W + H.GAP), y + top - sy))
    out.alpha_composite(H.fletxa(True, False), (8 + fx0 - sx, y + top - sy))
    out.alpha_composite(H.fletxa(False, True), (8 + fx1 - sx, y + top - sy))
    y += safata.height + 12
    out.alpha_composite(tauler, (8, y))
    out.alpha_composite(H.lupa_boto(cw, ch), (8 + 6, y + 10))
    nearest(out, (W * S, Ht * S)).save(HERE / 'hud.png')
    print('hud.png', (W * S, Ht * S))


if __name__ == '__main__':
    main()
