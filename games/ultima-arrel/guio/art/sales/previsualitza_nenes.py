#!/usr/bin/env python3
"""
L'Última Arrel — previsualització ×2 d'una sala d'art definitiu (hd640/rooms/<sala>.py) amb personatges de mostra
(la centraleta i el campament de les fades).

Munta el fons, els decorats que es diguin, els personatges a `spawns` (a l'escala de les regions de la sala, com fa
el motor) i el primer pla (`FRONT`) per sobre. Els personatges són els de les mostres d'estil: l'Iri i la Vet de
art/mostra/nenes.py, l'Espora de art/mostra/centraleta.py i unes fades esquemàtiques (≈28 px a escala 1), fins que
hi hagi els fulls de debò. A escala 1, l'Iri fa ≈97 px i la Vet ≈90 (a les sales de lluny, ≈0,7: 68 i 62 px).
(previsualitza.py fa el mateix amb els fulls provisionals de placeholder-art.)

Ús: python3 previsualitza_nenes.py <sala> [<nom> <decorat,decorat...>] ...
    python3 previsualitza_nenes.py centraleta  →  centraleta.png (sense decorats)
    python3 previsualitza_nenes.py centraleta centraleta-encesa radar_ences,xarxa_encesa
"""
import importlib
import subprocess
import sys
import tempfile
from pathlib import Path

from PIL import Image

HERE = Path(__file__).resolve().parent
TOOLS = HERE.parents[2] / 'adapters/benne/tools'
MOSTRA = HERE.parent / 'mostra'
sys.path.insert(0, str(TOOLS))

import hd640  # noqa: E402,F401
from pixels import nearest  # noqa: E402

ALT = {'iri': 97, 'vet': 90}                       # alçada a escala 1 (px)
CARA = {'iri': 'R', 'vet': 'R'}
FADES = ('urtica', 'pica', 'card')
SPRITES_PY = r'''
import sys, nenes, centraleta
from bosc import Canvas
out = sys.argv[1]
for spec, q in ((nenes.IRI, 'iri'), (nenes.VET, 'vet')):
    for f in ('D', 'R', 'L', 'DL'):
        nenes.nena(spec, f, q).save(f'{out}/{q}_{f}.png')
cv = Canvas(40, 50, transparent=True)
centraleta.espora(cv, 20, 46)
cv.img.save(f'{out}/espora.png')
'''


def _sprites(tmp):
    """Les figures de mostra (amb la llibreria de Ni un ou, en un altre procés: no es barreja amb la d'aquí)."""
    subprocess.run([sys.executable, '-c', SPRITES_PY, tmp], cwd=MOSTRA, check=True)


def fada(qui):
    """Una fada d'ortiga esquemàtica (≈28 px a escala 1): botes, jaqueta de cuir d'escarabat, cresta de card, ales."""
    jaq, cresta = {'urtica': ((40, 70, 40), (190, 120, 220)), 'pica': ((90, 50, 30), (240, 170, 60)),
                   'card': ((40, 40, 80), (120, 220, 200))}[qui]
    im = Image.new('RGBA', (30, 32), (0, 0, 0, 0))
    P = im.load()

    def px(x, y, c, a=255):
        if 0 <= x < 30 and 0 <= y < 32:
            P[x, y] = tuple(c) + (a,)
    for y in range(9, 22):                                     # les ales, translúcides, darrere
        for x in range(2, 28):
            dx = abs(x - 15)
            if 4 < dx < 14 and abs(y - 13 + dx * 0.25) < 4 - dx * 0.15:
                px(x, y, (190, 230, 240) if (x + y) % 5 else (230, 200, 150), 170)
    for y in range(26, 31):                                    # les cames i les botes
        for x in (12, 13, 16, 17):
            px(x, y, (20, 16, 18) if y > 28 else (50, 40, 36))
    for y in range(15, 26):                                    # la jaqueta
        w = 3 + (y - 15) * 0.3
        for x in range(int(15 - w), int(15 + w) + 1):
            k = 1.0 - (x - 15 + w) / (2 * w) * 0.5
            px(x, y, tuple(int(c * (0.7 + 0.6 * k)) for c in jaq))
    for y in range(8, 15):                                     # el cap
        for x in range(12, 19):
            if (x - 15) ** 2 + (y - 11.5) ** 2 <= 11:
                px(x, y, (226, 176, 140) if x < 17 else (190, 140, 110))
    px(14, 11, (20, 20, 24))
    px(17, 11, (20, 20, 24))
    for y in range(0, 9):                                      # la cresta de pelussa de card
        for x in range(12, 19):
            if abs(x - 15) <= 2 + y * 0.2 and (x * 7 + y * 3) % 4:
                px(x, y, tuple(min(255, int(c * (0.8 + 0.05 * y))) for c in cresta))
    return im


def _escala(regions, x, y):
    """Com el motor: l'última regió amb escala que conté els peus, lineal entre la y de dalt i la de baix."""
    s = 1.0
    for r in regions:
        xs, ys = [p[0] for p in r['points']], [p[1] for p in r['points']]
        if not (min(xs) <= x <= max(xs) and min(ys) <= y <= max(ys)):
            continue
        if r.get('scaleEnabled'):
            t = (y - min(ys)) / max(1e-6, max(ys) - min(ys))
            s = r['scaleTop'] + t * (r['scaleBottom'] - r['scaleTop'])
    return s


def _redimensiona(img, k):
    w, h = max(1, round(img.width * k)), max(1, round(img.height * k))
    return nearest(img, (w, h)) if k >= 1 else img.resize((w, h), Image.Resampling.BOX)


def munta(sala, decorats, tmp):
    M = importlib.import_module(f'hd640.rooms.{sala}')
    from hd.pix import Canvas
    cv = Canvas(light=getattr(M, 'LIGHT', None))
    M.bg(cv)
    img = cv.img
    for d in decorats:
        pc = Canvas(light=getattr(M, 'LIGHT', None), transparent=True)
        M.PROPS[d](pc)
        img.alpha_composite(pc.img)
    geo = M.GEOMETRIA
    gent = []
    for cid, (x, y) in geo['spawns'].items():
        s = _escala(geo.get('regions', []), x, y)
        if cid in ALT:
            spr = Image.open(f'{tmp}/{cid}_{CARA.get(cid, "D")}.png').convert('RGBA')
            bb = spr.getbbox()
            k = ALT[cid] * s / (bb[3] - bb[1])
            spr, feet = _redimensiona(spr, k), (round(25 * k), round(84 * k))
        elif cid == 'espora':
            k = 35 / 40                                        # ≈35 px a la sala (la meitat de l'Iri)
            spr = _redimensiona(Image.open(f'{tmp}/espora.png').convert('RGBA'), k)
            feet = (round(20 * k), round(47 * k))
        else:
            spr, feet = _redimensiona(fada(cid), s), (round(15 * s), round(31 * s))
        gent.append((y, spr, (x - feet[0], y - feet[1]), s, cid))
    for y, spr, pos, s, cid in sorted(gent, key=lambda g: g[0]):
        sh = Image.new('RGBA', img.size, (0, 0, 0, 0))         # l'ombra de contacte
        sp = sh.load()
        cx = pos[0] + spr.width / 2
        rx, ry = 11 * s * (0.5 if cid in FADES + ('espora',) else 1), 3 * s
        for yy in range(int(y - ry), int(y + ry) + 1):
            for xx in range(int(cx - rx), int(cx + rx) + 1):
                if ((xx - cx) / rx) ** 2 + ((yy - y) / ry) ** 2 <= 1 and 0 <= xx < img.width and 0 <= yy < img.height:
                    sp[xx, yy] = (0, 0, 0, 90)
        img.alpha_composite(sh)
        img.alpha_composite(spr, pos)
        bb = spr.getbbox()
        print(f'  {cid}: peus {y}, escala {s:.2f}, {bb[3] - bb[1]} px')
    # el primer pla, per damunt de tot
    base = Canvas(light=getattr(M, 'LIGHT', None))
    M.bg(base)
    src, dst = base.img.load(), img.load()
    for fr in (M.FRONT if isinstance(M.FRONT, (list, tuple)) else [M.FRONT]):
        if fr.get('baseline', 999) < 999:
            continue
        for yy in range(260):
            for xx in range(640):
                if fr['mask'](xx, yy):
                    dst[xx, yy] = src[xx, yy]
    return img.crop((0, 0, 640, 260))


def main(argv):
    sala = argv[0]
    feines = [(sala, [])]
    rest = argv[1:]
    while len(rest) >= 2:
        feines.append((rest[0], [d for d in rest[1].split(',') if d]))
        rest = rest[2:]
    with tempfile.TemporaryDirectory() as tmp:
        _sprites(tmp)
        for nom, decorats in feines:
            print(nom, decorats)
            img = munta(sala, decorats, tmp)
            nearest(img, (img.width * 2, img.height * 2)).save(HERE / f'{nom}.png')


if __name__ == '__main__':
    main(sys.argv[1:])
