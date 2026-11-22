#!/usr/bin/env python3
"""
La Conjura de l'Avet — làmina de revisió del HUD (adapters/benne/tools/hd640/hud.py), ×3, sense tocar el projecte
Benne.

A dalt, el botó «Canvia» (normal, hover i pressed; amb la cara de la Iri, la de la Vet i la lupa de la pista a la
finestra) i els altres botons (menú, punts, bossa) damunt d'un mur de pedra fosc; a sota, la safata de l'inventari
amb unes quantes icones i el tauler de la franja.
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
    finestra = [H.retrat('iri'), H.retrat('vet'), H.lupa_mini()]
    placa = [H.placa_boto(cw, ch), H.placa_boto(cw, ch, hover=True), H.placa_boto(cw, ch, pressed=True)]
    peces = [H.crop_bar(H.vg.menu_button, mx, my, ms, ms), H.boto(H.punts_icon), H.boto(H.punts_icon, hover=True),
             H.boto(H.bossa_icon), H.boto(H.bossa_icon, hover=True), H.boto(H.bossa_icon, on=True)]
    safata = H.safata()
    tauler = H.tauler()
    W = max(tauler.width, safata.width) + 16
    Ht = 8 + ch + 12 + safata.height + 12 + tauler.height + 8
    out = Image.new('RGBA', (W, Ht), (40, 36, 32, 255))
    d = ImageDraw.Draw(out)
    for y in range(Ht):                                       # un mur de pedra fosc, a la llum d'una espelma
        d.line([(0, y), (W, y)], fill=(44 - y // 14, 38 - y // 16, 32 - y // 18))
    x = 8
    port = (H.vg.PORT[0] - H.vg.CANVIA[0], (ch - 1) // 2)
    for i, p in enumerate(placa):
        out.alpha_composite(p, (x, 8))
        f = finestra[i]
        out.alpha_composite(f, (x + port[0] - f.width // 2, 8 + port[1] - f.height // 2 - 1))
        x += p.width + 10
    for p in peces:
        out.alpha_composite(p, (x, 8))
        x += p.width + 10
    y = 8 + ch + 12
    out.alpha_composite(safata, (8, y))
    fx0, slots_x, fx1, top = H.safata_xy()
    sx, sy = H.SAFATA[0], H.SAFATA[1]
    for i, iid in enumerate(['destral', 'cera', 'salconduit', 'tauleta', 'habits', 'claus', 'carta_emma']):
        out.alpha_composite(items.render(iid), (8 + slots_x - sx + i * (H.SLOT_W + H.GAP), y + top - sy))
    out.alpha_composite(H.fletxa(True, False), (8 + fx0 - sx, y + top - sy))
    out.alpha_composite(H.fletxa(False, True), (8 + fx1 - sx, y + top - sy))
    y += safata.height + 12
    out.alpha_composite(tauler, (8, y))
    nearest(out, (W * S, Ht * S)).save(HERE / 'hud.png')
    print('hud.png', (W * S, Ht * S))


if __name__ == '__main__':
    main()
