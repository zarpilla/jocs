#!/usr/bin/env python3
"""
`npm run profunditat` (des de games/<joc>/): revisa a cada sala el que fa que els personatges hi semblin a dins i no
enganxats al damunt (docs/guia-art-profunditat.md). Llegeix els `.room.json` del projecte Benne i no toca res.

Per a cada sala jugable (amb zona caminable i algun personatge que es veu), comprova:

  - **llum**: la sala té `characterLights` (o una regió `tintEnabled`); sense, el personatge té els mateixos colors a
    tot arreu. També avisa de claus que el motor no coneix (una clau mal escrita, i el llum queda sempre encès).
  - **ombra**: `characterShadow`, i si té el punt de llum (`light`), que la gira i l'allarga.
  - **escala**: la que tindria el personatge a cada punt de la zona caminable (com el motor: l'última regió activa
    amb `scaleEnabled` que conté els peus; fora de tota regió, 1). No la de la vora de la regió, que pot anar més
    avall d'on es camina. Avisa si passa d'ESCALA_MAX (els fulls són a 1×: ampliats, es pixelen), si baixa
    d'ESCALA_MIN (la cara es comença a perdre: mireu-ho a la pantalla) o si l'escala canvia però la velocitat no
    (`scaleWalkSpeed`). Si la protagonista de la sala hi porta una mida de full pròpia (una roba, `outfit` amb `inRoom`
    a game/data/characters.json, que és una mida de `sizeVariants` al seu .character.json; p. ex. `Gran`, ×1,5), el
    motor la mostra a l'escala ÷ la de la mida: els límits es comproven amb aquesta.
  - **capes**: alguna capa amb línia base que no sigui la del primer pla (999), perquè el personatge pugui passar per
    darrere d'alguna cosa.

Les sales amb personatges però sense profunditat (cinemàtiques, veus) surten a part, perquè es comprovi que és a
propòsit. La portada, els crèdits i les sales sense personatges no surten.

  python3 tools/profunditat.py [<joc> ...] [--tot]

Sense `<joc>`, el de la carpeta des d'on s'executa (o tots, des de l'arrel del repo). Amb `--tot`, també les sales
que no tenen cap avís. Torna 1 si hi ha cap avís.
"""
import argparse
import json
import sys
from pathlib import Path

ARREL = Path(__file__).resolve().parent.parent
ESCALA_MAX = 1.25
ESCALA_MIN = 0.4
PAS = 2  # px entre els punts de la zona caminable que es mostregen

CLAUS_LLUM = {'x', 'y', 'radius', 'color', 'intensity', 'squash', 'power', 'whenPropVisible', 'whenPropHidden'}
CLAUS_LLUMS = {'ambient', 'lights', 'topSample'}


def dins(px, py, pts):
    """Punt dins el polígon (parell-senar), com el motor."""
    c = False
    j = len(pts) - 1
    for i in range(len(pts)):
        xi, yi, xj, yj = pts[i]['x'], pts[i]['y'], pts[j]['x'], pts[j]['y']
        if (yi > py) != (yj > py) and px < (xj - xi) * (py - yi) / (yj - yi) + xi:
            c = not c
        j = i
    return c


def escala_regio(r, y):
    ys = [p['y'] for p in r['points']]
    top, bot = r.get('scaleTop', 1), r.get('scaleBottom', 1)
    span = max(ys) - min(ys)
    if span <= 1e-6:
        return (top + bot) / 2
    t = max(0.0, min(1.0, (y - min(ys)) / span))
    return top + t * (bot - top)


def punts_caminables(sala):
    for pol in (sala.get('walkable') or {}).get('polygons', []):
        if pol.get('active', True) is False or len(pol.get('points', [])) < 3:
            continue
        pts = pol['points']
        x0, x1 = min(p['x'] for p in pts), max(p['x'] for p in pts)
        y0, y1 = min(p['y'] for p in pts), max(p['y'] for p in pts)
        forats = [h.get('points', h) for h in pol.get('holes', []) or []]
        for y in range(int(y0), int(y1) + 1, PAS):
            for x in range(int(x0), int(x1) + 1, PAS):
                if dins(x, y, pts) and not any(len(h) >= 3 and dins(x, y, h) for h in forats):
                    yield x, y


def escales(sala):
    """[(escala, velocitat_escalada)] a cada punt caminable."""
    regs = [r for r in sala.get('regions', []) if r.get('active', True) and r.get('scaleEnabled')]
    out = []
    for x, y in punts_caminables(sala):
        guanya = None
        for r in regs:
            if dins(x, y, r['points']):
                guanya = r
        out.append((1.0, True) if guanya is None else (escala_regio(guanya, y), bool(guanya.get('scaleWalkSpeed'))))
    return out


def es_veu(c):
    d = c.get('definition', '')
    return '-veu' in d or '_veu' in d


def _sales_de(cond):
    """Les sales que una condició (`if` de narrative-core) esmenta amb `inRoom`."""
    if isinstance(cond, list):
        return {r for c in cond for r in _sales_de(c)}
    if not isinstance(cond, dict):
        return set()
    out = set()
    for k, v in cond.items():
        if k == 'inRoom':
            out |= set(v if isinstance(v, list) else [v])
        else:
            out |= _sales_de(v)
    return out


def mida_full(joc, sala_id):
    """(prefix, escala) de la mida de full que porta a la sala la seva protagonista (`outfit` amb `inRoom` que és una
    mida de `sizeVariants`), o (None, 1)."""
    dades = ARREL / 'games' / joc / 'game' / 'data'
    try:
        prot = json.loads((dades / 'rooms' / f'{sala_id}.json').read_text()).get('protagonist')
        roba = json.loads((dades / 'characters.json').read_text()).get(prot, {}).get('outfit', [])
        fitxa = ARREL / 'games' / joc / joc / 'src/game/characters' / prot / f'{prot}.character.json'
        mides = json.loads(fitxa.read_text()).get('sizeVariants') or {}
    except (OSError, ValueError, AttributeError, TypeError):
        return None, 1.0
    for regla in roba:
        if sala_id in _sales_de(regla.get('if')):
            nom = regla.get('name', '')
            prefix = max((m for m in mides if nom.startswith(m)), key=len, default=None)
            return (prefix, float(mides[prefix])) if prefix else (None, 1.0)
    return None, 1.0


def revisa(sala, mida=(None, 1.0)):
    """(avisos, notes, resum) d'una sala; None si no s'hi veu ningú. `mida`: la de `mida_full`."""
    pers = [c for c in sala.get('characters', []) if not es_veu(c)]
    if not pers:
        return None
    esc = escales(sala)
    if len(esc) < 20 or not any(r.get('scaleEnabled') for r in sala.get('regions', [])) and \
            not sala.get('characterShadow'):
        return 'cinematica'
    avisos, notes = [], []
    cl = sala.get('characterLights')
    if not cl and not any(r.get('tintEnabled') for r in sala.get('regions', [])):
        avisos.append('sense llum als personatges (characterLights)')
    if cl:
        dolentes = set(cl) - CLAUS_LLUMS
        for l in cl.get('lights', []):
            dolentes |= set(l) - CLAUS_LLUM
        if dolentes:
            avisos.append(f"characterLights amb claus que el motor no coneix: {', '.join(sorted(dolentes))}")
    sh = sala.get('characterShadow')
    if not sh or sh.get('enabled') is False:
        avisos.append('sense ombra de contacte (characterShadow)')
    elif not sh.get('light'):
        notes.append('ombra sense punt de llum (light)')
    lo, hi = min(e for e, _ in esc), max(e for e, _ in esc)
    rang = f'{lo:.2f}–{hi:.2f}'
    if mida[0]:                                     # amb una mida de full pròpia, el motor la mostra a l'escala ÷ k
        lo, hi = lo / mida[1], hi / mida[1]
        rang += f' (full {mida[0]} ×{mida[1]:g}: {lo:.2f}–{hi:.2f})'
    if hi > ESCALA_MAX:
        avisos.append(f'escala fins a {hi:.2f} on es camina (màx. ≈{ESCALA_MAX})')
    if lo < ESCALA_MIN:
        avisos.append(f'escala fins a {lo:.2f} on es camina: mireu si es llegeix la cara')
    if hi - lo > 0.05 and any(not v for e, v in esc if abs(e - 1) > 1e-6):
        avisos.append("l'escala canvia però la velocitat no (scaleWalkSpeed)")
    capes = [p for p in sala.get('props', []) if p.get('baseline') is not None]
    if not any(p['baseline'] != 999 for p in capes):
        notes.append('cap capa amb línia base al mig: no es passa per darrere de res')
    llum = 'sí' if cl else '-'
    return avisos, notes, f'escala {rang}  llum {llum}  ombra {"sí" if sh else "-"}  capes {len(capes)}'


def jocs(args):
    if args:
        return args
    cwd = Path.cwd().resolve()
    for p in [cwd, *cwd.parents]:
        if p.parent == ARREL / 'games':
            return [p.name]
    return sorted(p.name for p in (ARREL / 'games').iterdir() if (p / p.name / 'src/game/rooms').is_dir())


def main():
    ap = argparse.ArgumentParser(description=__doc__.split('\n\n')[0])
    ap.add_argument('jocs', nargs='*')
    ap.add_argument('--tot', action='store_true', help='també les sales sense avisos')
    a = ap.parse_args()
    total = 0
    for joc in jocs(a.jocs):
        sales = sorted((ARREL / 'games' / joc / joc / 'src/game/rooms').glob('*/*.room.json'))
        if not sales:
            print(f'{joc}: no hi ha sales a games/{joc}/{joc}/src/game/rooms', file=sys.stderr)
            continue
        print(f'== {joc}')
        cine = []
        for f in sales:
            r = revisa(json.loads(f.read_text()), mida_full(joc, f.parent.name))
            if r is None:
                continue
            if r == 'cinematica':
                cine.append(f.parent.name)
                continue
            avisos, notes, resum = r
            total += len(avisos)
            if avisos or notes or a.tot:
                print(f'  {f.parent.name:26} {resum}')
                for s in avisos:
                    print(f'    ! {s}')
                for s in notes:
                    print(f'    · {s}')
        if cine:
            print(f"  sense profunditat (cinemàtiques? comproveu-ho): {', '.join(cine)}")
    print(f'\n{total} avisos' if total else '\nCap avís.')
    return 1 if total else 0


if __name__ == '__main__':
    sys.exit(main())
