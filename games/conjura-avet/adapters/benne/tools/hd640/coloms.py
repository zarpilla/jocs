"""
Coloms que volen en rodó (al voltant d'un campanar), per a les animacions de fons de les sales.

Cada colom fa una el·lipse en pantalla (centre, radis, fase i sentit); a la meitat de darrere només es pinta on
`darrere(x, y)` és cert (el cel: el campanar el tapa), i a la de davant, on `davant(x, y)` és cert. Bat les ales a
cada fotograma, i a la meitat de darrere és una mica més petit.
"""
import math

from PIL import Image

PLOMA = (58, 62, 74)          # el gris blavós del colom
PIT = (128, 132, 144)         # el pit i el ventre, més clars


def frames(w, h, vols, darrere, davant, n=32):
    """vols: [(cu, cv, rx, ry, fase, sentit)] → n fotogrames RGBA de w×h, en bucle."""
    out = []
    for i in range(n):
        im = Image.new('RGBA', (w, h), (0, 0, 0, 0))
        P = im.load()
        for k, (cu, cv, rx, ry, fase, sentit) in enumerate(vols):
            a = 2 * math.pi * (i / n * sentit + fase)
            x = cu + rx * math.cos(a)
            y = cv + ry * math.sin(a)
            endavant = math.sin(a) > 0                 # la meitat de baix de l'el·lipse és la de davant
            vola_dreta = (-math.sin(a) * sentit) > 0
            ok = davant if endavant else darrere
            amunt = (i + k) % 2 == 0                   # les ales: amunt i avall, alternant
            gran = endavant
            _colom(P, w, h, int(round(x)), int(round(y)), vola_dreta, amunt, gran, ok)
        out.append(im)
    return out


def _colom(P, w, h, x, y, dreta, amunt, gran, ok):
    s = 1 if dreta else -1
    px = [((0, 0), PIT), ((s, 0), PLOMA), ((-s, 0), PLOMA), ((2 * s, -1 if gran else 0), PLOMA)]
    if gran:
        px.append(((-2 * s, 0), PLOMA))
    ala = -1 if amunt else 1
    px += [((0, ala), PLOMA), ((-s, ala), PLOMA)]
    if gran:
        px += [((0, 2 * ala), PLOMA), ((s, ala), PLOMA)]
    for (dx, dy), col in px:
        X, Y = x + dx, y + dy
        if 0 <= X < w and 0 <= Y < h and ok(X, Y):
            P[X, Y] = (*col, 255)
