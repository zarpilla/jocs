#!/usr/bin/env python3
"""
L'Última Arrel — previsualització ×2 de les sales de dia (`toll_gripaus`, `caseta_obra`, `zona_zero`), amb els
personatges als seus `spawns`, a l'escala de la regió de perspectiva, i les capes del davant (FRONT) per sobre de qui
hi té darrere. (La de la casa, per a les altres sales, és previsualitza.py.)

L'Iri i la Vet són les figures de mostra (guio/art/mostra/nenes.py, desades abans com a PNG a la carpeta --nenes:
iri_DL.png, vet_DL.png) a ≈97 i ≈90 px a escala 1; la resta, els provisionals de placeholder-art reduïts a una mida
aproximada a escala 1 (adults ≈118 px, l'àvia ≈108, gripaus ≈44, fades ≈28). Només per mirar com es llegeix la sala.

Ús: python3 previsualitza_dia.py <sala> [props,separats,per,comes | -] [sufix] --nenes <carpeta>
  → <sala>[-sufix].png (640×260, ×2)
"""
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
TOOLS = HERE.parents[2] / 'adapters/benne/tools'
sys.path.insert(0, str(TOOLS))

import hd640  # noqa: E402,F401
from PIL import Image  # noqa: E402
from pixels import nearest  # noqa: E402
from hd import render as R  # noqa: E402

ALT = {'iri': 97, 'vet': 90, 'pla': 118, 'txell': 116, 'avia': 108, 'bufo': 44, 'gripau': 40, 'urtica': 28}


def dins(p, poly):
    x, y = p
    c = False
    for (xa, ya), (xb, yb) in zip(poly, poly[1:] + poly[:1]):
        if (ya > y) != (yb > y) and x < xa + (y - ya) * (xb - xa) / (yb - ya):
            c = not c
    return c


def escala(geo, p):
    s = 1.0
    for r in geo.get('regions', []):
        if r.get('scaleEnabled') and dins(p, [tuple(q) for q in r['points']]):
            ys = [q[1] for q in r['points']]
            t = max(0.0, min(1.0, (p[1] - min(ys)) / max(1e-6, max(ys) - min(ys))))
            s = r['scaleTop'] + t * (r['scaleBottom'] - r['scaleTop'])
    return s


def figura(cid, nenes):
    """→ (imatge a escala 1, peus)."""
    if cid in ('iri', 'vet'):
        img = Image.open(nenes / f'{cid}_DL.png').convert('RGBA')
        feet = (25, 83)
    else:
        img, f = R._sprite(cid)
        if img is None:
            return None, None
        feet = (f['x'], f['y'])
    bb = img.getbbox()
    k = ALT.get(cid, 110) / (bb[3] - bb[1])
    w, h = max(1, round(img.width * k)), max(1, round(img.height * k))
    im = nearest(img, (w, h)) if k >= 1 else img.resize((w, h), Image.Resampling.BOX)
    return im, (round(feet[0] * k), round(feet[1] * k))


def main():
    args = list(sys.argv[1:])
    i = args.index('--nenes')
    nenes = Path(args[i + 1])
    del args[i:i + 2]
    sala = args[0]
    ids = None if len(args) < 2 or args[1] == '-' else [p for p in args[1].split(',') if p]
    sufix = f'-{args[2]}' if len(args) > 2 else ''
    mod = R.load(sala)
    bg, props = R.render(sala)
    full = bg.copy()
    for pid, p in props.items():
        if ids is None or pid in ids:
            full.alpha_composite(p)
    for aid, (frames, ms) in R._render_anims(sala).items():
        full.alpha_composite(frames[len(frames) // 3])
    geo = mod.GEOMETRIA
    fr = R.fronts(sala, full)
    fets = set()
    for cid, (x, y) in sorted(geo['spawns'].items(), key=lambda kv: kv[1][1]):
        for j, (fimg, f, _) in enumerate(fr):                 # les capes que aquest personatge té darrere
            if j not in fets and f.get('baseline', 999) < y:
                full.alpha_composite(fimg)
                fets.add(j)
        img, (fx, fy) = figura(cid, nenes)
        if img is None:
            continue
        s = escala(geo, (x, y))
        w, h = max(1, round(img.width * s)), max(1, round(img.height * s))
        im = img.resize((w, h), Image.Resampling.BOX) if s < 1 else nearest(img, (w, h))
        full.alpha_composite(im, (round(x - fx * s), round(y - fy * s)))
    for j, (img, f, _) in enumerate(fr):
        if j not in fets:
            full.alpha_composite(img)
    nearest(full.crop((0, 0, 640, 260)), (1280, 520)).save(HERE / f'{sala}{sufix}.png')
    print(HERE / f'{sala}{sufix}.png')


if __name__ == '__main__':
    main()
