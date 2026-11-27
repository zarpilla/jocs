#!/usr/bin/env python3
"""
Dibuixa els sprites provisionals dels personatges, en pixel art, amb el format que espera Benne
(full d'Aseprite PNG + JSON amb etiquetes, i el .character.json).

Les protagonistes tenen Idle/Walk/Talk en tres direccions (L, D, U; Benne fa el mirall per a R).
El dibuix és a hd/characters.py; aquí només es munten els fulls.
Surt a adapters/benne/placeholder-art/<id>/. Ús: python3 draw_characters.py
"""
import json
import math
import sys
from pathlib import Path

from PIL import Image

sys.path.insert(0, str(Path(__file__).resolve().parent))
from escala import SCALE, box, pt  # noqa: E402
from hd.characters import person as hd_person  # noqa: E402
from hd import personatges  # noqa: E402

OUT = Path(__file__).resolve().parent.parent / 'placeholder-art'
OUTLINE = (34, 24, 30, 255)
CLEAR = (0, 0, 0, 0)


def rgba(c):
    return c if len(c) == 4 else (*c, 255)


class Canvas:
    """(El fan servir draw_items.py.) Llenç amb coordenades de disseny (les de sempre, p. ex. 36×64) que es rasteritza a l'escala
    del joc: rectangles i el·lipses es tornen a rasteritzar a la mida real, i el contorn és d'un píxel real."""

    def __init__(self, w, h, k=SCALE):
        self.k = k
        self.w, self.h = round(w * k), round(h * k)
        self.img = Image.new('RGBA', (self.w, self.h), CLEAR)

    def rpx(self, x, y, c):
        """Un píxel real (per als detalls que només caben a la resolució gran)."""
        if 0 <= x < self.w and 0 <= y < self.h:
            self.img.putpixel((x, y), rgba(c))

    def rrect(self, x0, y0, x1, y1, c):
        for y in range(max(0, y0), min(self.h - 1, y1) + 1):
            for x in range(max(0, x0), min(self.w - 1, x1) + 1):
                self.img.putpixel((x, y), rgba(c))

    def px(self, x, y, c):
        self.rect(x, y, x, y, c)

    def rect(self, x0, y0, x1, y1, c):
        self.rrect(*box(x0, y0, x1, y1, self.k), c)

    def ellipse(self, cx, cy, rx, ry, c):
        k = self.k
        for y in range(max(0, int((cy - ry - 1) * k)), min(self.h, int((cy + ry + 2) * k))):
            for x in range(max(0, int((cx - rx - 1) * k)), min(self.w, int((cx + rx + 2) * k))):
                lx, ly = (x + 0.5) / k - 0.5, (y + 0.5) / k - 0.5
                if ((lx - cx) / (rx + 0.3)) ** 2 + ((ly - cy) / (ry + 0.3)) ** 2 <= 1:
                    self.img.putpixel((x, y), rgba(c))

    def outline(self):
        """Contorn fosc d'un píxel al voltant de tot el que s'ha dibuixat (llegibilitat sobre qualsevol fons)."""
        src = self.img.copy()
        for y in range(self.h):
            for x in range(self.w):
                if src.getpixel((x, y))[3] == 0:
                    for dx, dy in ((1, 0), (-1, 0), (0, 1), (0, -1)):
                        nx, ny = x + dx, y + dy
                        if 0 <= nx < self.w and 0 <= ny < self.h and src.getpixel((nx, ny))[3] > 0 and src.getpixel((nx, ny)) != rgba(OUTLINE):
                            self.img.putpixel((x, y), OUTLINE)
                            break


# ─── Persones ───────────────────────────────────────────────────────────────

def person(p, facing, walk=None, talk=False, thin=False):
    """Una persona de 49×87 (36×64 de disseny), peus a (25, 83)."""
    return hd_person(p, facing, walk=walk, talk=talk)


# ─── Fulls i definicions ────────────────────────────────────────────────────

def scaled_extra(extra):
    """Punts i velocitats del .character.json, de coordenades de disseny a píxels reals."""
    out = dict(extra)
    out['walkSpeed'] = round(extra['walkSpeed'] * SCALE)
    for key in ('walkToPoint', 'talkPoint', 'feet'):
        x, y = pt(extra[key]['x'], extra[key]['y'])
        out[key] = {'x': x, 'y': y}
    out['collider'] = {'points': [dict(zip('xy', pt(p['x'], p['y']))) for p in extra['collider']['points']]}
    return out


# ─── Quan són quiets: respiració i micro-accions (com a Aigua Verne) ────────

# La respiració (Idle de quatre fotogrames): no es mou cap píxel de la silueta; només la clariana del pit puja i baixa
# (+5 %, +10 %, +5 %). A 1×, moure el cos 1 px amunt o avall semblava que arronsessin les espatlles. Files de disseny
# (figura de 49×87): el pit, sota el coll.
RESPIRA_DE, RESPIRA_FINS = 30, 41
RESPIRA_X = (13, 36)
RESPIRA = (0.0, 0.05, 0.10, 0.05)
IDLE_MS = 650                                   # cada fotograma: un cicle de 2,6 s
# Les direccions dels fulls: L, D, U i el 3/4 (DL de cara, UL d'esquena); R, DR i UR són el mirall.
DIRS = ('L', 'D', 'U', 'DL', 'UL')
# Quan és quiet, de tant en tant parpelleja i, si fa estona, mira al voltant (el motor salta la que no hi és).
IDLE_ACTIONS = [{'animation': 'Blink', 'every': [3, 8]}, {'animation': 'Look', 'every': [9, 18], 'after': 6}]

_EXTRA = {}                                     # el que s'afegeix a l'especificació (ulls tancats, mirada)


def _amb(extra, fn):
    """Crida `fn()` amb `extra` afegit a l'especificació de qualsevol persona que es dibuixi."""
    _EXTRA.clear()
    _EXTRA.update(extra)
    try:
        return fn()
    finally:
        _EXTRA.clear()


def _person_amb_extra():
    """hd.characters.person, amb `_EXTRA` dins l'especificació (els dibuixos de hd640 la criden pel mòdul)."""
    import hd.characters as C
    if getattr(C.person, '_amb_extra', False):
        return
    orig = C.person

    def person(spec, *a, **kw):
        return orig({**spec, **_EXTRA} if _EXTRA else spec, *a, **kw)
    person._amb_extra = True
    C.person = person


def respira(img, k):
    """`img` (la persona sola, 49×87 de disseny a `sc` px per px) amb el pit un `k` més clar, més a dalt que a baix."""
    if not k:
        return img
    sc = img.width / 49
    y0, y1 = round(RESPIRA_DE * sc), round(RESPIRA_FINS * sc)
    out = img.copy()
    P_ = out.load()
    for y in range(y0, y1):
        f = 1 + k * (1 - (y - y0) / (y1 - y0))
        for x in range(round(RESPIRA_X[0] * sc), round(RESPIRA_X[1] * sc)):
            r, g, b, a = P_[x, y]
            if a:
                P_[x, y] = (min(255, int(r * f)), min(255, int(g * f)), min(255, int(b * f)), a)
    return out


def quiet_tags(d, pre='', dirs=DIRS, pit=True, walk=True):
    """Idle (4: respira), Walk (6), Talk (2), Blink i Look per a `d(f, walk=None, talk=False)`. `pit`: si la
    clariana del pit és on toca (no ho és en un fotograma més gran, com el d'en Ballester)."""
    _person_amb_extra()
    out = []
    for f in dirs:
        base = d(f)
        out.append((f'{pre}Idle{f}', [respira(base, k) if pit else base for k in RESPIRA]))
    if walk:
        for f in dirs:
            out.append((f'{pre}Walk{f}', [d(f, walk=k) for k in range(6)]))
    for f in dirs:
        out.append((f'{pre}Talk{f}', [d(f, talk=False), d(f, talk=True)]))
    for f in dirs:
        if f in ('D', 'L', 'DL'):                          # parpellejar: on es veu la cara
            out.append((f'{pre}Blink{f}', [_amb({'closed': True}, lambda f=f: d(f))] * 2))
    for f in dirs:
        if f in ('D', 'DL'):                               # mirar al voltant: els ulls i la cara, a un costat i a l'altre
            out.append((f'{pre}Look{f}', [_amb({'mira': m}, lambda f=f: d(f)) for m in (-1, -1, -1, 0, 1, 1, 1, 0)]))
    return out


def durations(tags, walk=(90, 100), talk=140, extra=None):
    anims = {}
    for t, _ in tags:
        a = {'loop': True}
        if 'Blink' in t or 'Look' in t:                    # micro-accions: un sol cop i torna a l'Idle
            a = {'loop': False, 'frameDuration': 75 if 'Blink' in t else 260}
        elif 'Agafa' in t:                                 # el gest: un sol cop (el runtime el treu en acabar)
            a = {'loop': False, 'frameDuration': AGAFA_MS}
        elif 'Walk' in t:
            a['frameDuration'] = walk[0] if t.endswith('L') else walk[1]
        elif 'Talk' in t:
            a['frameDuration'] = talk
        elif 'Idle' in t:
            a['frameDuration'] = IDLE_MS
        for k, v in (extra or {}).items():
            if t == k:
                a['frameDuration'] = v
        anims[t] = a
    return anims


def write(cid, tags, size, extra):
    """tags: [(nom, [imatges])]. Escriu <id>.png, <id>.json (Aseprite) i <id>.character.json."""
    frames = [img for _, imgs in tags for img in imgs]
    extra = scaled_extra(extra)
    # en graella: una sola fila de molts fotogrames passaria de l'amplada màxima d'una textura (4096). Cada mida de
    # fotograma (la normal; la de lluny, `sizeVariants`) va en files pròpies, una sota l'altra.
    pos, y, sw = [None] * len(frames), 0, 0
    for size in dict.fromkeys(img.size for img in frames):
        w, h = size
        idx = [i for i, img in enumerate(frames) if img.size == size]
        cols = min(len(idx), 4096 // w)
        for n, i in enumerate(idx):
            pos[i] = ((n % cols) * w, y + (n // cols) * h)
        y += h * -(-len(idx) // cols)
        sw = max(sw, w * cols)
    sheet = Image.new('RGBA', (sw, y), CLEAR)
    for i, img in enumerate(frames):
        sheet.paste(img, pos[i])
    d = OUT / cid
    d.mkdir(parents=True, exist_ok=True)
    sheet.save(d / f'{cid}.png')
    frame_tags, i = [], 0
    for name, imgs in tags:
        frame_tags.append({'name': name, 'from': i, 'to': i + len(imgs) - 1, 'direction': 'forward', 'color': '#000000ff'})
        i += len(imgs)
    meta = {
        'frames': {f'{cid} {n}.aseprite': {
            'frame': {'x': pos[n][0], 'y': pos[n][1], 'w': frames[n].width, 'h': frames[n].height}, 'rotated': False,
            'trimmed': False, 'spriteSourceSize': {'x': 0, 'y': 0, 'w': frames[n].width, 'h': frames[n].height},
            'sourceSize': {'w': frames[n].width, 'h': frames[n].height}, 'duration': 100,
        } for n in range(len(frames))},
        'meta': {'app': 'https://www.aseprite.org/', 'version': 'provisional (draw_characters.py)', 'image': f'{cid}.png',
                 'format': 'RGBA8888', 'size': {'w': sheet.width, 'h': sheet.height}, 'scale': '1',
                 'frameTags': frame_tags, 'layers': [], 'slices': []},
    }
    (d / f'{cid}.json').write_text(json.dumps(meta, indent=2) + '\n')
    character = {
        'id': cid, 'name': cid, 'description': '', 'clickable': True, 'display': {'aseprite': True},
        **extra,
    }
    (d / f'{cid}.character.json').write_text(json.dumps(character, indent=2) + '\n')
    print(f'✔ {cid}: {len(frames)} fotogrames, {", ".join(t for t, _ in tags)}')


def walker(cid, p):
    tags = []
    for f in 'LDU':
        tags.append((f'Idle{f}', [person(p, f)]))
    for f in 'LDU':
        tags.append((f'Walk{f}', [person(p, f, walk=k) for k in range(6)]))
    for f in 'LDU':
        tags.append((f'Talk{f}', [person(p, f, talk=False), person(p, f, talk=True)]))
    anims = {t: {'loop': True} for t, _ in tags}
    for f in 'LDU':
        anims[f'Walk{f}']['frameDuration'] = 90 if f == 'L' else 80
        anims[f'Talk{f}']['frameDuration'] = 140
    write(cid, tags, (36, 64), {
        'walkSpeed': 84, 'walkToPoint': {'x': 40, 'y': 61}, 'talkPoint': {'x': 18, 'y': -2}, 'feet': {'x': 18, 'y': 61},
        'collider': {'points': [{'x': 11, 'y': 2}, {'x': 25, 'y': 2}, {'x': 27, 'y': 40}, {'x': 24, 'y': 63}, {'x': 11, 'y': 63}, {'x': 8, 'y': 40}]},
        'animations': anims, 'defaultVerb': 'look',
    })


def standing(cid, p, thin=False):
    tags = []
    for f in 'DLU':
        tags.append((f'Idle{f}', [person(p, f, thin=thin)]))
        tags.append((f'Talk{f}', [person(p, f, thin=thin), person(p, f, talk=True, thin=thin)]))
    anims = {t: {'loop': True, **({'frameDuration': 140} if t.startswith('Talk') else {})} for t, _ in tags}
    write(cid, tags, (36, 64), {
        'walkSpeed': 60, 'walkToPoint': {'x': 44, 'y': 61}, 'talkPoint': {'x': 18, 'y': -2}, 'feet': {'x': 18, 'y': 61},
        'collider': {'points': [{'x': 11, 'y': 2}, {'x': 25, 'y': 2}, {'x': 27, 'y': 40}, {'x': 24, 'y': 63}, {'x': 11, 'y': 63}, {'x': 8, 'y': 40}]},
        'animations': anims, 'defaultVerb': 'talkTo',
    })


# De lluny (prefix `Lluny`): la figura dibuixada directament a LLUNY de la mida (no encongida; la cara és la petita,
# de píxel solt, la del nen), en fotogrames propis de LLUNY × la mida (el mateix cantó de dalt a l'esquerra, els peus
# a `feet` × LLUNY) i `sizeVariants: {Lluny: LLUNY}` al .character.json: el motor la mostra a escala/LLUNY i el
# collider, el talkPoint, l'ombra i la velocitat es comporten com amb el full normal. Ho dibuixa
# hd640/draw_characters.py (`DE_LLUNY`: dibuixa amb `fn()` a ×K×LLUNY). A bcmu_contenidor la Vet va de 0,40 a 0,80:
# a 0,66, el full de lluny es mostra entre 0,6 i 1,2 (a 0,56 —la mida de 480— s'hauria d'ampliar fins a 1,43).
LLUNY = 0.66
DE_LLUNY = None

# El gest `Agafa` (tasca 005): allarga el braç cap a la cosa i el torna a recollir. El fa sol el runtime comú
# (adapters/benne/runtime) quan la protagonista agafa, fa servir o dona alguna cosa, si el full en té per a la roba
# que porta. Quant s'estira el braç a cada fotograma (0: penjant, 1: estirat del tot).
AGAFA = (0.45, 0.85, 1.0, 1.0, 0.5)
AGAFA_MS = 100


def _cap(a, b, t):
    return (a[0] + (b[0] - a[0]) * t, a[1] + (b[1] - a[1]) * t)


def agafa(t):
    """La postura del gest `Agafa`, estirat `t` (vegeu AGAFA): de perfil, el braç del davant endavant, gairebé
    horitzontal, amb la mà a l'alçada de la cintura; de cara, la mà de la dreta (de la imatge) ve endavant, davant del
    cos; d'esquena, el braç puja endavant cap a la cosa."""
    def pose(p):
        if p.f == 'L':
            sx, sy = p.shoulder
            a0, b0 = 3, 8                                   # el braç quiet (Pose._side)
            a, bend = a0 + (62 - a0) * t, b0 + (14 - b0) * t
            ra, rb = math.radians(a), math.radians(a + bend)
            el = (sx - math.sin(ra) * 10.5, sy + math.cos(ra) * 10.5)
            wr = (el[0] - math.sin(rb) * 9.5, el[1] + math.cos(rb) * 9.5)
            p.arms[0] = ((sx, sy), el, wr)
            return
        sx, sy = p.sh[1]
        if p.f == 'U':
            p.elbow[1] = _cap(p.elbow[1], (sx + 3.0, sy + 4), t)
            p.wrist[1] = _cap(p.wrist[1], (sx + 1.5, sy - 6), t)
        else:
            p.elbow[1] = _cap(p.elbow[1], (sx + 2.2, sy + 8.5), t)
            p.wrist[1] = _cap(p.wrist[1], (sx - 3.5, sy + 12.5), t)
    return pose


def agafa_tags(d, pre='', dirs=DIRS):
    """El gest `Agafa` en totes les direccions del full, per a `d(f, walk=None, talk=False)`."""
    _person_amb_extra()
    return [(f'{pre}Agafa{f}', [_amb({'pose': agafa(t)}, lambda f=f: d(f)) for t in AGAFA]) for f in dirs]


def protagonist(cid, draw, feet=(25, 83), outfits=('',), lluny=(), amb_agafa=None):
    """Protagonista de Suma Zero (hd/personatges.py): 49×87, peus a (25, 83), com a Ferro-9.
    `outfits`: les robes (prefix de les etiquetes: `BarIdleD`...); `draw(f, walk, talk, roba)` les dibuixa.
    `lluny`: les robes que també es dibuixen de lluny (etiquetes `Lluny<roba>IdleD`...; vegeu LLUNY).
    `amb_agafa`: les robes que tenen el gest `Agafa` (per defecte, totes)."""
    tags = []
    for o in outfits:
        d = (lambda f, walk=None, talk=False: draw(f, walk=walk, talk=talk)) if not o else \
            (lambda f, walk=None, talk=False, o=o: draw(f, walk=walk, talk=talk, roba=o))
        tags += quiet_tags(d, o)
        if amb_agafa is None or o in amb_agafa:
            tags += agafa_tags(d, o)
    for o in lluny if DE_LLUNY else ():
        # la respiració (respira) es fa a la figura petita: la clariana del pit és la seva
        d = (lambda f, walk=None, talk=False, o=o: DE_LLUNY(lambda: draw(f, walk=walk, talk=talk, roba=o)))
        tags += quiet_tags(d, f'Lluny{o}')
    anims = durations(tags, walk=(90, 100))
    w, h = tags[0][1][0].size
    fx, fy = feet
    variants = {'sizeVariants': {'Lluny': LLUNY}} if lluny and DE_LLUNY else {}
    write(cid, tags, (w, h), {**variants,
        'walkSpeed': 110, 'walkToPoint': {'x': fx + 18, 'y': fy}, 'talkPoint': {'x': fx, 'y': -2}, 'feet': {'x': fx, 'y': fy},
        'collider': {'points': [{'x': 15, 'y': 2}, {'x': 35, 'y': 2}, {'x': 37, 'y': 50}, {'x': 33, 'y': 85}, {'x': 16, 'y': 85}, {'x': 12, 'y': 50}]},
        'animations': anims, 'defaultVerb': 'look', 'idleActions': IDLE_ACTIONS,
    })


def vet(f, walk=None, talk=False, roba=''):
    """La Vet amb una de les seves robes; `…Ulleres` hi afegeix les ulleres."""
    ulleres = roba.endswith('Ulleres')
    return personatges.vet(f, walk=walk, talk=talk, roba=roba.removesuffix('Ulleres'), ulleres=ulleres)


VET_OUTFITS = tuple(personatges.VET_ROBA) + tuple(f'{o}Ulleres' for o in personatges.VET_ULLERES)
# Les robes de la Vet de lluny (vegeu LLUNY): a bcmu_contenidor, la d'auditora (amb ulleres o sense) i, després de
# l'escapada, la de casa (les regles `outfit` de game/data/characters.json).
VET_LLUNY = ('', 'Auditora', 'AuditoraUlleres')
# Les robes de la Vet amb el gest `Agafa` (tasca 005): les que surten més, la de casa (l'Acte 1 al pis) i la
# d'auditora (els actes 2 i 3, al BCMU). La franel·la (el bar) i la bomber (l'aeroport) no en tenen: el runtime
# s'hi salta el gest.
VET_AGAFA = ('', 'Auditora', 'AuditoraUlleres')


def secundari(cid):
    """Un secundari (hd/personatges.py, NPCS): Idle i Talk en D, L i U, i Walk si no és assegut (en
    Soler deixa la porta per buscar el nen: sense Walk, Benne el faria lliscar de cara)."""
    seated = personatges.NPCS[cid].get('seated') is not None
    dirs = ('D', 'L', 'U') if seated else DIRS
    tags = quiet_tags(lambda f, walk=None, talk=False: personatges.npc(cid, f, walk=walk, talk=talk), dirs=dirs,
                      pit=cid != 'nen', walk=not seated)
    if cid == 'marcel':                                       # roba «Taula»: al bar del final, de cara
        for f in 'DLU':
            tags.append((f'TaulaIdle{f}', [personatges.marcel_taula(f)]))
            tags.append((f'TaulaTalk{f}', [personatges.marcel_taula(f), personatges.marcel_taula(f, talk=True)]))
    anims = durations(tags, walk=(90, 80))
    # assegut, amb les cames endavant: qui hi parla s'hi atura una mica més enllà dels genolls
    walk_to = {'x': 66, 'y': 90} if seated else {'x': 44, 'y': 83}
    write(cid, tags, (49, 87), {
        'walkSpeed': 70, 'walkToPoint': walk_to, 'talkPoint': {'x': 25, 'y': -2}, 'feet': {'x': 25, 'y': 83},
        'collider': {'points': [{'x': 15, 'y': 2}, {'x': 35, 'y': 2}, {'x': 37, 'y': 50}, {'x': 33, 'y': 85}, {'x': 16, 'y': 85}, {'x': 12, 'y': 50}]},
        'animations': anims, 'defaultVerb': 'talkTo', 'idleActions': IDLE_ACTIONS,
    })


def gat(cid='diu'):
    """En Diu: assegut de cara (un gat no es gira per ningú). Animacions d'aspecte: Caixa, Auricular, Pizza, i dormint:
    CaixaDorm, PizzaDorm, Dorm. A l'Escena 1 es mou (indicacions d'escena a pis_estudi): WalkL (de perfil; Benne en fa
    el mirall), Mossega<Cable> (va fins al cable, el mossega i se'l mira) i Salta (dins la caixa, que és a l'esquerra).
    Tot va al fotograma gran (personatges.DW×DH, els peus al mig), perquè el mirall i el salt hi càpiguen."""
    P_ = personatges
    G = P_.diu_gran
    idle = [G(P_.diu(cua=k % 4, parpelleja=(k == 7))) for k in range(8)]
    talk = [G(P_.diu(cua=0)), G(P_.diu(cua=1))]
    tags = []
    for f in 'DLU':
        tags.append((f'Idle{f}', idle))
        tags.append((f'Talk{f}', talk))
    for estat in ('caixa', 'auricular', 'pizza'):
        tags.append((estat.capitalize(), [G(P_.diu_estat(estat, cua=k % 4)) for k in range(4)]))
    # Escena 2: dorm dins el que li han donat (l'auricular ja l'ha tornat)
    for estat, tag in (('caixa', 'CaixaDorm'), ('pizza', 'PizzaDorm'), (None, 'Dorm')):
        tags.append((tag, [G(P_.diu_estat(estat, cua=k, dorm=True)) for k in range(4)]))
    tags.append(('WalkL', [P_.diu_camina(k) for k in range(6)]))
    for cable in P_.CABLES:
        tags.append((f'Mossega{cable.capitalize()}', [P_.diu_mossega(k, cable) for k in range(6)]))
    tags.append(('Salta', [P_.diu_salta(k) for k in range(9)]))
    dur = {'WalkL': (110, True), 'Salta': (130, False)}
    anims = {}
    for t, _ in tags:
        ms, loop = dur.get(t, (300 if t.startswith('Idle') else 500 if t.endswith('Dorm') else 160, True))
        if t.startswith('Mossega'):
            ms, loop = 200, False                     # una vegada, i es queda amb el cable a la boca
        anims[t] = {'loop': loop, 'frameDuration': ms}
    dx, dy = P_.DIU_PAD
    pt = lambda x, y: {'x': x + dx, 'y': y + dy}
    write(cid, tags, (P_.DW, P_.DH), {
        'walkSpeed': 60, 'walkToPoint': pt(36, 25), 'talkPoint': pt(13, -2), 'feet': pt(13, 25),
        'collider': {'points': [pt(4, 0), pt(28, 0), pt(28, 25), pt(4, 25)]},
        'animations': anims, 'defaultVerb': 'look',
    })


def secundari2(cid):
    """Un secundari de l'Acte 2 (hd/personatges.py, NPCS2): Idle, Talk i Walk en D, L i U (sense Walk, Benne el
    faria lliscar quan un `stage` el fa caminar), i una etiqueta per a cada variant d'estat (`appearance` a
    characters.json), de cara, amb la boca que es mou."""
    variants = personatges.NPCS2[cid]
    tags = quiet_tags(lambda f, walk=None, talk=False: personatges.npc2(cid, f, walk=walk, talk=talk),
                      pit=cid not in personatges.BIG)
    for v in variants:
        if v:
            tags.append((v, [personatges.npc2(cid, 'D', variant=v)] * 3 + [personatges.npc2(cid, 'D', variant=v, talk=True)]))
    anims = durations(tags, walk=(90, 80), extra={v: 400 for v in variants if v})
    w, h = tags[0][1][0].size
    fx, fy = personatges.big2_feet(cid) if cid in personatges.BIG else (25, 83)
    dx = fx - 25
    write(cid, tags, (w, h), {
        'walkSpeed': 70, 'walkToPoint': {'x': 44 + dx, 'y': fy}, 'talkPoint': {'x': fx, 'y': -2}, 'feet': {'x': fx, 'y': fy},
        'collider': {'points': [{'x': 15 + dx, 'y': 2}, {'x': 35 + dx, 'y': 2}, {'x': 37 + dx, 'y': 50}, {'x': 33 + dx, 'y': fy + 2},
                                {'x': 16 + dx, 'y': fy + 2}, {'x': 12 + dx, 'y': 50}]},
        'animations': anims, 'defaultVerb': 'talkTo', 'idleActions': IDLE_ACTIONS,
    })


def robot(cid='neta'):
    """NETA-3: Idle (el llum de l'antena parpelleja i els raspalls giren) i Talk en D, L i U; 'Descansa' i 'Molles';
    i la roba «Davantal» (el bar del final)."""
    N = personatges.neta
    tags = []
    for f in 'DLU':
        tags.append((f'Idle{f}', [N(f, k=k) for k in range(8)]))
        tags.append((f'Talk{f}', [N(f, k=0), N(f, talk=True, k=1)]))
        tags.append((f'Walk{f}', [N(f, k=k) for k in range(8)]))   # fa la volta: rodola amb els raspalls girant
    tags.append(('Descansa', [N('D', estat='descansa', k=k) for k in range(2)]))
    tags.append(('Molles', [N('D', estat='molles', k=k) for k in range(4)]))
    for f in 'DLU':                                           # roba «Davantal»: serveix al bar del final
        tags.append((f'DavantalIdle{f}', [N(f, k=k, davantal=True) for k in range(8)]))
        tags.append((f'DavantalTalk{f}', [N(f, k=0, davantal=True), N(f, talk=True, k=1, davantal=True)]))
    dur = {'Descansa': 900, 'Molles': 220}
    anims = {t: {'loop': True, 'frameDuration': dur.get(t, 160 if 'Talk' in t else 180)} for t, _ in tags}
    write(cid, tags, (personatges.NW, personatges.NH), {
        'walkSpeed': 50, 'walkToPoint': {'x': 44, 'y': 42}, 'talkPoint': {'x': 20, 'y': -2}, 'feet': {'x': 20, 'y': 42},
        'collider': {'points': [{'x': 6, 'y': 4}, {'x': 34, 'y': 4}, {'x': 36, 'y': 43}, {'x': 4, 'y': 43}]},
        'animations': anims, 'defaultVerb': 'talkTo',
    })


def main():
    """Els personatges de Suma Zero amb art definitiu (els altres surten amb la plantilla de Benne)."""
    protagonist('iri', personatges.iri, outfits=('', 'SenseAuriculars'))
    protagonist('vet', vet, outfits=VET_OUTFITS, lluny=VET_LLUNY, amb_agafa=VET_AGAFA)
    gat('diu')
    for cid in personatges.NPCS:
        secundari(cid)
    for cid in personatges.NPCS2:
        secundari2(cid)
    robot('neta')


if __name__ == '__main__':
    from escala import RESOLUCIO
    if RESOLUCIO == 640:
        # A 640×360 les figures les dibuixa hd640/draw_characters.py (×4/3), al mateix lloc.
        import runpy
        sys.argv = [sys.argv[0], str(OUT)]
        runpy.run_path(str(Path(__file__).resolve().parent / 'hd640' / 'draw_characters.py'), run_name='__main__')
    else:
        main()
