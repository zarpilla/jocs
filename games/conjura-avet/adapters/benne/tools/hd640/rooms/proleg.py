"""
La Conjura de l'Avet — el pròleg (cinemàtica, pantalla sencera de 640×360). EN 3D, a 1×: el mateix pla de la
portada (avet_pla_comu.py), però abans que caigui l'avet: la nit de tramuntana de Sant Joan de les Abadesses, novembre del 1017.

El fons és el carrer sense l'avet (el mur sencer). Les capes, que anima el contingut amb `stage`:
  - `avet_dret`: l'avet dret, enorme, fosc contra el cel, que es gronxa amb el vent (en bucle);
  - `fanal` → `fanal_arriba`: algú encaputxat arriba pel carrer amb un fanal i el deixa a terra, al peu de l'avet;
  - `figura` → `figura_serra`: s'ajup a les arrels, serra (el costat del vent), s'aixeca i se'n va;
  - `avet_cau` → `cau`: l'avet cau damunt el mur i l'esbotza; les arrels s'aixequen (amb la sacsejada, `shake`);
  - `cofre_brilla` → `brilla`: entre les arrels, el segell vermell d'un cofre s'encén;
  - `ma` → `agafa`: l'encaputxat torna de la foscor, agafa el cofre (el segell l'encén de vermell) i se l'endú.
Per codi: `llamp` (el cel i l'absis s'encenen; el que hi ha a les capes de damunt queda en silueta) i `pluja`.
Les durades de les animacions són les del `hold` del contingut (fanal 2,5 s, figura 2,8, cau 1,6, brilla 2,2,
agafa 2,6). L'últim pla (l'avet ajagut) és el de la portada, i el joc continua a `mur_avet` amb la mateixa càmera.
"""
import functools
import math

import numpy as np
from PIL import Image

import hd640  # noqa: F401
from hd640.rooms import avet_comu as A
from hd640.rooms import avet_pla_comu as PL
from hd640.rooms.avet_comu import Estat, W, H, diff

LIGHT = None
CAM = PL.CAM_CINE
BASE = PL.NIT_ABANS


def _base():
    return PL.render(BASE)


def bg(cv):
    cv.img.paste(_base()[0])
    cv.P = cv.img.load()


PROPS = {}
BUIT = lambda: [Image.new('RGBA', (W, H), (0, 0, 0, 0))]  # noqa: E731


def _arbre(angle):
    return Estat(llum='nit', arbre=float(angle), forat='cap', mur='sencer', branques='cap', cam=CAM, h=H,
                 extres=('primer_pla',))


CAIGUT = Estat(llum='nit', cam=CAM, h=H, extres=('primer_pla',))
CAIGUT_COFRE = Estat(llum='nit', cam=CAM, h=H, extres=('cofre', 'primer_pla'))


@functools.lru_cache(maxsize=None)
def _dret_frames():
    return [diff(PL.render(_arbre(a))[0], _base()[0]) for a in (0.0, 0.008, 0.016, 0.02, 0.014, 0.005, -0.004, -0.002)]


@functools.lru_cache(maxsize=None)
def _cau_frames():
    angles = (0.04, 0.12, 0.27, 0.5, 0.8, 1.12, 1.38)
    out = [diff(PL.render(_arbre(a))[0], _base()[0]) for a in angles]
    out.append(diff(PL.render(CAIGUT)[0], _base()[0]))
    return out


def _mascara_arbre():
    """On hi ha l'avet (dret o caigut): la llum del fanal no s'hi posa (les capes de l'avet ja hi són)."""
    a = np.asarray(_dret_frames()[0])[..., 3] > 0
    b = np.asarray(_cau_frames()[-1])[..., 3] > 0
    return a | b


# El camí de l'encaputxat: arriba pel carrer de l'esquerra fins al peu de l'avet (de costat, a la mateixa
# distància de la càmera: no creix ni s'encongeix), deixa el fanal a terra, s'ajup al costat del vent de les arrels,
# serra, s'aixeca i se'n torna per on ha vingut.
CAMI = [np.array((-470.0, 0, 566.0)), np.array((-336.0, 0, 586.0))]
FANAL_TERRA = np.array((-356.0, 8.0, 572.0))
AJUP = np.array((-304.0, 0, 598.0))


def _figura_frame(P, fanal=None, ajupit=0.0, serra=None, llum=None):
    """Un fotograma: la figura (i el fanal) damunt del fons, i la llum del fanal (fora de l'avet)."""
    _, v = _base()
    c = PL._copia(v)
    PL.encaputxat(c, BASE, P, ajupit=ajupit, serra=serra, fanal=fanal) if P is not None else None
    if P is None and fanal is not None:
        PL.fanalet(c, fanal)
    img = c.imatge()
    if llum is not None:
        lit = PL.llum_fanal(_base()[0], llum)
        a, b = np.asarray(img).copy(), np.asarray(lit)
        mod = (np.asarray(diff(lit, _base()[0]))[..., 3] > 0) & ~_mascara_arbre()
        mod &= ~np.isin(np.pad(c.own, ((0, H - c.h), (0, 0))), [c.idx('figura'), c.idx('fanal')])
        a[mod] = b[mod]
        img = Image.fromarray(a, 'RGBA')
    return diff(img, _base()[0])


@functools.lru_cache(maxsize=None)
def _fanal_frames():
    """10 fotogrames (2,5 s): l'encaputxat arriba amb el fanal; a l'últim, el fanal ja és a terra."""
    out = []
    for i in range(9):
        t = i / 8
        P = CAMI[0] + (CAMI[1] - CAMI[0]) * t
        bob = math.sin(i * 1.7) * 1.5
        f = P + np.array((-12, 38 + bob, -6))
        out.append(_figura_frame(P, fanal=f, llum=f))
    out.append(_figura_frame(None, fanal=FANAL_TERRA, llum=FANAL_TERRA))
    return out


@functools.lru_cache(maxsize=None)
def _fanal_quiet():
    return _fanal_frames()[-1]


@functools.lru_cache(maxsize=None)
def _figura_frames():
    """14 fotogrames (2,8 s): de CAMI[1] s'ajup al costat de les arrels, serra, s'aixeca i se'n va (l'últim, buit).
    (El fanal i la seva llum són a la capa `fanal`, que es queda.)"""
    out = []
    ll = _fanal_quiet()

    def nomes_figura(img):
        a, b = np.asarray(img).copy(), np.asarray(ll)
        a[(b[..., 3] > 0) & (np.abs(a.astype(int) - b.astype(int)).sum(-1) == 0)] = 0
        return Image.fromarray(a, 'RGBA')
    seq = [(CAMI[1], 0.0, None), (AJUP, 0.5, None)] + [(AJUP, 1.0, ph) for ph in (0, 1.6, 3.1, 4.7, 0, 1.6, 3.1, 4.7)]
    seq += [(AJUP, 0.4, None), (CAMI[1], 0.0, None), (CAMI[1] + (CAMI[0] - CAMI[1]) * 0.35, 0.0, None)]
    for P, aj, ph in seq:
        out.append(nomes_figura(_figura_frame(P, ajupit=aj, serra=ph, llum=FANAL_TERRA)))
    out.append(BUIT()[0])
    return out


BRILLA = (0.0, 0.15, 0.35, 0.6, 0.85, 0.6, 0.8, 0.62, 0.85, 0.6, 0.8)     # 11 fotogrames (2,2 s)


@functools.lru_cache(maxsize=None)
def _brilla_frames():
    """El cofre, que ja hi era, s'encén: la lluïssor vermella puja i batega una estona."""
    sense, _ = PL.render(CAIGUT)
    amb, _ = PL.render(CAIGUT_COFRE)
    u, vv = A.segell_xy(CAM)
    return [diff(A.brillantor(amb, u, vv, k, r=30), sense) for k in BRILLA]


# L'encaputxat torna per agafar el cofre: surt de la foscor de l'esquerra, s'atura davant les arrels, allarga el braç,
# agafa el cofre (la lluïssor s'apaga) i se l'endú per on ha vingut. A la mateixa mida que quan serrava.
MA_P = np.array((-338.0, 0, 640.0))          # on s'atura, davant el cofre
MA_FORA = np.array((-480.0, 0, 640.0))       # d'on ve i on se'n va (fora de pla, a l'esquerra)


@functools.lru_cache(maxsize=None)
def _ma_frames():
    """13 fotogrames (2,6 s). Cada fotograma pinta tota la zona (el que hi ha sense el cofre, amb el fanal; la
    figura, el braç i el cofre on el porta la mà)."""
    sense, v_sense = PL.render(CAIGUT)
    amb, _ = PL.render(CAIGUT_COFRE)
    sota = Image.alpha_composite(sense.copy(), _fanal_quiet())         # el que hi ha sota la capa: el fanal hi és
    encès_ = Image.alpha_composite(Image.alpha_composite(amb.copy(), _fanal_quiet()), _brilla_frames()[-1])
    u, vv = A.segell_xy(CAM)
    cam = CAM
    # el retall del cofre (on difereix del fons sense cofre)
    dif = np.asarray(diff(amb, sense))
    ys, xs = np.nonzero(dif[..., 3] > 0)
    sel = (np.abs(xs - u) < 30) & (np.abs(ys - vv) < 30)
    ys, xs = ys[sel], xs[sel]
    cofre_px = np.asarray(amb)[ys, xs]
    zona = np.zeros((H, W), bool)
    zona[max(0, int(vv) - 60):int(vv) + 70, 0:int(u) + 40] = True
    # (posició, braç 0..1 o None, porta el cofre, la lluïssor encara hi és)
    seq = [(0.0, None, False), (0.4, None, False), (0.75, None, False), (1.0, None, False),
           (1.0, 0.5, False), (1.0, 1.0, False), (1.0, 1.0, False),
           (1.0, 0.6, True), (1.0, 0.25, True), (0.7, 0.25, True), (0.4, 0.25, True), (0.1, 0.25, True), None]
    out = []
    for pas in seq:
        if pas is None:
            a = np.asarray(sota).copy()
            out.append(Image.fromarray(np.where(zona[..., None], a, 0).astype(np.uint8), 'RGBA'))
            continue
        f, braç, porta = pas
        P = MA_FORA + (MA_P - MA_FORA) * f
        c = PL._copia(v_sense)
        PL.encaputxat(c, BASE, P)
        fig = np.zeros((H, W), bool)
        fig[:c.h] = c.own == c.idx('figura')
        img = np.asarray(c.imatge())
        a = np.asarray(sota if porta else encès_).copy()
        a[fig] = img[fig]
        k = cam.f / cam.vista(tuple(P))[2]
        # la lluïssor vermella del segell a la figura (el costat del cofre), mentre no l'agafa
        Y, X = np.nonzero(fig)
        if not porta:
            uf = cam.projecta(tuple(P))[0]
            d = np.hypot(X - u, (Y - vv) * 1.2)
            vermell = np.clip(1 - d / 40, 0, 1) ** 1.5 * np.clip((X - uf) / 6 + 0.3, 0, 1)    # només el costat del cofre
            a[Y, X, 0] = np.clip(a[Y, X, 0] + vermell * 120, 0, 255)
            a[Y, X, 1] = np.clip(a[Y, X, 1] + vermell * 22, 0, 255)
            a[Y, X, 2] = np.clip(a[Y, X, 2] + vermell * 18, 0, 255)
        # el braç: de l'espatlla cap al cofre (o, quan el porta, arran del cos)
        espatlla = np.array(cam.projecta(tuple(P + np.array((8.0, 68, -4)))))[:2]
        if braç is not None:
            objectiu = np.array((u, vv + 2)) if not porta else np.array(cam.projecta(tuple(P + np.array((16.0, 40, -8)))))[:2]
            mà = espatlla + (objectiu - espatlla) * braç if not porta else objectiu + (np.array((u, vv + 2)) - objectiu) * (braç - 0.25) / 0.75
        else:
            mà = None
        if porta:
            dx, dy = int(round(mà[0] - u)), int(round(mà[1] - vv - 2))
            ok = (ys + dy >= 0) & (ys + dy < H) & (xs + dx >= 0) & (xs + dx < W)
            a[ys[ok] + dy, xs[ok] + dx] = cofre_px[ok]
        if mà is not None:
            n = 24
            r0 = max(1.6, 4.5 * k)
            for i in range(n + 1):
                p = espatlla + (mà - espatlla) * i / n
                r = r0 * (1 - 0.25 * i / n)
                yy, xx = np.ogrid[0:H, 0:W]
                disc = (xx + 0.5 - p[0]) ** 2 + (yy + 0.5 - p[1]) ** 2 < r * r
                ll = 0 if porta else np.clip(1 - np.hypot(p[0] - u, p[1] - vv) / 40, 0, 1) * 90
                a[disc, :3] = (int(12 + ll), 10, 16)
                a[disc, 3] = 255
            mx, my = int(mà[0]), int(mà[1])
            for (dx, dy) in ((0, 0), (1, 0), (0, -1), (1, -1), (-1, 0), (0, 1)):
                X_, Y_ = mx + dx, my + dy
                if 0 <= X_ < W and 0 <= Y_ < H:
                    a[Y_, X_, :3] = (196, 120, 110) if not porta else ((150, 128, 114) if (dx + dy) % 2 else (120, 100, 90))
        out.append(Image.fromarray(np.where(zona[..., None], a, 0).astype(np.uint8), 'RGBA'))
    return out


# L'ordre compta: cada capa abans de les seves etiquetes (draw_placeholders les hi afegeix).
ANIMS = {
    'llamp': {'frames': lambda: PL.llamps(PL.NIT_ABANS, PL.NIT_ABANS_LLAMP), 'frameDuration': 110, 'zIndex': 1},
    'avet_dret': {'frames': lambda: list(_dret_frames()), 'frameDuration': 260, 'zIndex': 2},
    'avet_cau': {'frames': BUIT, 'frameDuration': 1000, 'loop': False, 'zIndex': 2},
    'cau': {'frames': lambda: list(_cau_frames()), 'frameDuration': 200, 'loop': False, 'prop': 'avet_cau'},
    'fanal': {'frames': BUIT, 'frameDuration': 1000, 'loop': False, 'zIndex': 4},
    'fanal_arriba': {'frames': lambda: list(_fanal_frames()), 'frameDuration': 250, 'loop': False, 'prop': 'fanal'},
    'figura': {'frames': BUIT, 'frameDuration': 1000, 'loop': False, 'zIndex': 4},
    'figura_serra': {'frames': lambda: list(_figura_frames()), 'frameDuration': 200, 'loop': False, 'prop': 'figura'},
    'cofre_brilla': {'frames': BUIT, 'frameDuration': 1000, 'loop': False, 'zIndex': 5},
    'brilla': {'frames': lambda: list(_brilla_frames()), 'frameDuration': 200, 'loop': False, 'prop': 'cofre_brilla'},
    'ma': {'frames': BUIT, 'frameDuration': 1000, 'loop': False, 'zIndex': 6},
    'agafa': {'frames': lambda: list(_ma_frames()), 'frameDuration': 200, 'loop': False, 'prop': 'ma'},
    'pluja': {'frames': lambda: list(PL.pluja(5)), 'frameDuration': 80, 'zIndex': 8},
}

GEOMETRIA = {'things': {}, 'spawns': {}, 'walkable': [(200, 253), (267, 253), (267, 261), (200, 261)]}
