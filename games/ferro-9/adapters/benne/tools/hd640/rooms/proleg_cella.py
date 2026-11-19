"""
Pròleg 2 · La cel·la 9 de nit, a 640×360 (pantalla sencera). EN 3D (hd640/tres_d.py), a 1×; el dibuix pla de
sempre és a proleg_cella_pla_comu.py i les parets surten de gavina_cella_pla_comu.py.

Un pla de cinema baix, des del capçal de la llitera: la Vet dorm a prop, al pis de baix (en Mos, al de dalt), i la
paret del fons fuig cap a l'esquerra fins a la porta. Al mig, el panell rovellat vibra i treu llum cian per les
juntes: és l'única llum (amb la Terra a la finestreta i el cor tènue de la MARE), i fa un bassal al terra i ombres
llargues de la llitera.
  - primer pla: el pal de la llitera i el capçal, a contrallum, tallats per la vora de la dreta;
  - la llitera, separada de la paret, amb tres cares: el costat (el dibuix pla, amb la Vet i en Mos), els
    matalassos per dalt i el capçal; el terra de planxes que s'empetiteixen cap a la porta; el sostre;
  - l'animació de la paret (el panell, les ones, la pols, els halos, el cor, la Terra, el LED) és la del dibuix pla,
    projectada per la mateixa paret; `vet_desperta` hi obre els ulls de la Vet (al costat de la llitera).

El món: x a la dreta (les x del dibuix pla de la paret del fons), y amunt (0 = el terra), z endavant (0 = la paret
del fons); 1 unitat = 1 píxel del dibuix pla.
"""
import hd640  # noqa: F401  (abans que cap hd.rooms: posa la llibreria a 640×360)

import math
from functools import lru_cache

from PIL import Image

from hd.pix import Canvas, Light, W, H, hr, STEEL
from hd.rooms.gavina_cella import DECK, MATT
from hd640.rooms import gavina_cella_pla_comu as PL
from hd640.rooms import proleg_cella_pla_comu as PC
from hd640.tres_d import Camera, Escena, Llum

LIGHT = Light(ambient=0.0, vignette=None, floor_fade=None)   # (la llum és la del món; la del dibuix pla, a PC.LIGHT)

FY = PL.FLOOR_Y                          # al dibuix pla, la línia paret-terra
HW = FY                                  # l'alçada de la cel·la
BD = 48                                  # el fons de la llitera (del costat fins a la paret)
BF = 231                                 # al dibuix pla, on toquen a terra els pals del davant de la llitera
BX0, BX1 = 486, 640                      # el retall del costat de la llitera (x del dibuix pla)
XR = 668                                 # la paret de la dreta
PCX, PCY = PC.PCX, PC.PCY                # el centre del panell (dibuix pla)


def _y(fy):
    return FY - fy


def _yb(fy):
    """Una y del dibuix pla del costat de la llitera → alçada del món (els pals toquen a terra a BF)."""
    return BF - fy


def _mira(pos, cap, f, centre):
    d = [cap[i] - pos[i] for i in range(3)]
    return Camera(pos=pos, yaw=math.atan2(d[0], d[2]), pitch=math.atan2(-d[1], math.hypot(d[0], d[2])), f=f,
                  centre=centre)


CAM = _mira((640.0, 100.0, -250.0), (380.0, 72.0, 0.0), 400.0, (270, 172))
PANEL_P = (PCX, _y(PCY), 0.0)            # el panell, al món


# ─── Les textures (el dibuix pla) ───────────────────────────────────────────

def _paret_quieta(cv):
    """La paret del fons sense la llitera (la llitera és en 3D): el sostre, les planxes, la porta, el panell..."""
    PL._ceiling(cv)
    PL._wall(cv)
    PL._door(cv)
    PL.text(cv, 'MODUL C', 101, 59, STEEL, 0.9, worn=0.2)
    PL._panel(cv)
    PL._crack(cv)
    PL.vent_hole(cv)
    PL.vent_grille(cv, *PL.VENT)
    PL.bunk_wall(cv)
    PL._camera(cv)


PARET = PL.Ambient(PC.LIGHT, _paret_quieta, PC._dyn, PC._post)


@lru_cache(maxsize=None)
def _tex_paret():
    cv = Canvas(light=PC.LIGHT)
    PARET.draw(cv, 0.0)
    return cv.img


@lru_cache(maxsize=None)
def _tex_llitera():
    """La llitera de costat, amb la Vet i en Mos, sobre transparent (amb la nit)."""
    cv = Canvas(light=PC.LIGHT, transparent=True)
    marques = PL.bunk_wall
    PL.bunk_wall = lambda c: None                    # (les ratlles i la foto són a la paret, no a la llitera)
    try:
        PL._bunk(cv)
    finally:
        PL.bunk_wall = marques
    PC._sleepers(cv)
    P = cv.P
    for y in range(H):
        for x in range(W):
            o = P[x, y]
            if o[3]:
                P[x, y] = PC._post(x, y, o)
    return cv.img


@lru_cache(maxsize=None)
def _tex_terra(nom):
    cv = Canvas(light=PC.LIGHT, transparent=True)
    {'safata': PL.p_safata, 'escarabat': PL.p_escarabat}[nom](cv)
    box = cv.img.getbbox()
    return cv.img.crop(box), box


# ─── Procedurals ────────────────────────────────────────────────────────────

def _planxes(s, t, P):
    """El terra: planxes de 40×30 amb el relleu antilliscant i reblons als cantons."""
    x, z = P[0], -P[2]
    cx, cz = int(math.floor(x / 40)), int(math.floor(z / 30))
    fx, fz = x - cx * 40, z - cz * 30
    lv = 1.6 + (hr(cx, cz, 4) - 0.5) * 0.4
    if fx < 0.9 or fz < 0.9:
        return 0.2
    if fx < 2 or fz < 2:
        lv += 0.5
    if (fx < 4 or fx > 36) and (fz < 4 or fz > 26) and ((fx - 2.6) ** 2 < 1.2 or (fx - 37.4) ** 2 < 1.2):
        lv += 1.4                                                    # reblons
    elif hr(cx, cz, 9) > 0.5 and int(fz / 2.4) % 2 == 0 and (fx + int(fz / 2.4) * 2) % 5 < 1.6:
        lv += 0.3                                                    # les llàgrimes
    return lv


def _placa_paret(s, t, P, seed=5):
    """Les parets dels costats: planxes de 70×56 amb juntes i reblons."""
    cx, cy = int(s / 70), int(t / 56)
    fx, fy = s % 70, t % 56
    lv = 1.8 + (hr(cx, cy, seed) - 0.5) * 0.5 - t * 0.003
    if fx < 1.2 or fy < 1.2:
        return 0.4
    if fx < 2.4 or fy < 2.4:
        lv += 0.6
    if (fx % 14) < 1.4 and (fy < 5 or fy > 51):
        lv += 1.2
    return lv


def _sostre(s, t, P):
    lv = 1.0 + (hr(int(P[0] / 53), 3) - 0.5) * 0.3
    if int(-P[2] / 60) != int((-P[2] - 2) / 60):
        lv += 1.0                                                    # les bigues del sostre
    return lv


# ─── L'escena ───────────────────────────────────────────────────────────────

LLUMS = [Llum((PCX, _y(PCY), -16), 420, 2.6, power=1.6),            # el panell que vibra (fred)
         Llum((448, _y(67), -14), 160, 0.9),                         # la Terra a la finestreta
         Llum((235, _y(40), -10), 90, 0.6)]                          # el cor de la MARE


def escena(cv):
    e = Escena(cv, CAM, llums=LLUMS, ambient=-0.6)
    # el sostre, les parets dels costats i el terra
    e.quad('sostre', (-200, HW, 0), (XR, HW, 0), (XR, HW, -500), (-200, HW, -500), ramp=STEEL, lvl=_sostre)
    e.quad('paret_e', (0, HW, -500), (0, HW, 0), (0, 0, 0), (0, 0, -500), ramp=STEEL, lvl=_placa_paret)
    e.quad('paret_d', (XR, HW, 0), (XR, HW, -500), (XR, 0, -500), (XR, 0, 0), ramp=STEEL,
           lvl=lambda s, t, P: _placa_paret(s, t, P, 6) - 0.4)
    e.quad('terra', (-200, 0, 0), (XR, 0, 0), (XR, 0, -500), (-200, 0, -500), ramp=DECK, lvl=_planxes)
    # la paret del fons: el dibuix pla (sense la llitera)
    e.quad('paret', (0, HW, 0), (XR, HW, 0), (XR, 0, 0), (0, 0, 0), tex=(_tex_paret(), (0, 0, XR, FY)))
    # la foscor del racó i sota la llitera
    e.foscor('ombra', (0, 0.1, 0), (XR, 0.1, 0), (XR, 0.1, -60), (0, 0.1, -60), lambda s, t: 0.5 * (1 - t / 60))
    e.foscor('ombra', (470, 0.1, 0), (XR, 0.1, 0), (XR, 0.1, -BD - 18), (470, 0.1, -BD - 18),
             lambda s, t: 0.75 * min(1.0, s / 24) * min(1.0, (BD + 18 - t) / 14))
    # l'ombra llarga de la llitera, cap a la càmera i a la dreta (el panell és a l'esquerra)
    e.foscor('ombra', (500, 0.1, -BD), (XR, 0.1, -BD), (XR + 120, 0.1, -BD - 160), (560, 0.1, -BD - 160),
             lambda s, t: 0.45 * (1 - t / 170) * min(1.0, s / 30))
    # el bassal de llum cian del panell, al terra
    e.claror((PCX - 160, 0.2, 0), (PCX + 160, 0.2, 0), (PCX + 160, 0.2, -170), (PCX - 160, 0.2, -170),
             (80, 180, 240), lambda s, t: 0.32 * max(0.0, 1 - math.hypot((s - 160) / 150, t / 150)) ** 1.3)
    # la safata del sopar i el Senyor Bigotis, drets al terra
    img, box = _tex_terra('escarabat')
    e.sprite('escarabat', img, (176 - box[0], 226 - box[1]), (176, 0, -60))
    img, box = _tex_terra('safata')
    e.sprite('safata', img, (450 - box[0], 246 - box[1]), (300, 0, -120))
    # la llitera: els matalassos (per dalt i pel capçal), els pals i el costat (el dibuix pla)
    for top in (169, 103):
        y1 = _yb(top)
        e.caixa('llitera', 497, 627, y1 - 11, y1, -BD + 2, -2, MATT, 2.6,
                cares={'dalt': {'ramp': MATT, 'lvl': lambda s, t, P: 2.4 + (0.3 if int(s / 5) % 2 else 0)},
                       'dreta': {'ramp': MATT, 'lvl': lambda s, t, P: 2.2 - t * 0.04}})
    for x in (501, 631):
        e.caixa('llitera', x, x + 3, 0, _yb(88), -4, -1, STEEL, 2.0)
    e.quad('llitera', (BX0, _yb(78), -BD), (BX1, _yb(78), -BD), (BX1, 0, -BD), (BX0, 0, -BD),
           tex=(_tex_llitera(), (BX0, 78, BX1, BF)))
    # el pal de la dreta, gruixut: el primer pla
    e.caixa('pal', PL.FR, PL.FR + 5, 0, _yb(83), -BD - 5, -BD, STEEL, 1.6,
            cares={'dreta': {'ramp': STEEL, 'lvl': 1.0}})
    return e


@lru_cache(maxsize=None)
def _escena():
    cv = Canvas(light=LIGHT)
    cv.S = 1
    e = escena(cv)
    return cv.img.copy(), e


def _vinyeta(cv):
    import numpy as np
    A = np.array(cv.img).astype(float)
    yy, xx = np.mgrid[0:H, 0:W].astype(float)
    d = np.hypot((xx - 300) / 360, (yy - 170) / 210)
    k = 1 - 0.55 * np.clip(d - 0.55, 0, 1) ** 1.4
    A[..., :3] *= k[..., None]
    cv.img.paste(Image.fromarray(A.astype('uint8'), 'RGBA'))
    cv.P = cv.img.load()


@lru_cache(maxsize=None)
def _base():
    img, _ = _escena()
    cv = Canvas(light=LIGHT, img=img.copy())
    _vinyeta(cv)
    return cv.img


def bg(cv, t=0.0):
    cv.img.paste(_base())
    cv.P = cv.img.load()


def _projecta(flat, sids):
    """Una capa del dibuix pla (de la paret o de la llitera) projectada per la sala, amb la vinyeta."""
    _, e = _escena()
    out = e.capa(flat, sids=sids)
    # la vinyeta, la mateixa que al fons
    import numpy as np
    A = np.array(out).astype(float)
    yy, xx = np.mgrid[0:H, 0:W].astype(float)
    d = np.hypot((xx - 300) / 360, (yy - 170) / 210)
    k = 1 - 0.55 * np.clip(d - 0.55, 0, 1) ** 1.4
    A[..., :3] *= k[..., None]
    return Image.fromarray(A.astype('uint8'), 'RGBA')


def _ambient_frames(n=24):
    """La paret del dibuix pla al llarg del cicle (només el que canvia), projectada."""
    return [_projecta(f, {'paret'}) for f in PARET.frames(n)]


# ─── La Vet obre els ulls (capa del pròleg) ──────────────────────────────────
# A la segona sacsejada de la paret, la Vet es desperta: obre els ulls, parpelleja un cop i es queda mirant
# («vet_desperta», sense bucle). Fins llavors, la capa és buida («vet_ulls»). Els ulls es dibuixen al costat pla de
# la llitera i es projecten.

def _ulls_frames():
    from hd640.rooms.fabrica_cambra_pla_comu import frame_diff
    base = _tex_llitera()

    def layer(state):
        if state is None:
            return Canvas(transparent=True).img
        cv = Canvas(light=PC.LIGHT, img=base.copy())
        cv.P = cv.img.load()
        PC.ulls_vet(cv, mig=state == 'mig')
        return _projecta(frame_diff(base, cv.img), {'llitera'})
    closed, half, opened = layer(None), layer('mig'), layer('obert')
    # (fotogrames de 150 ms) tancats, a mig obrir, oberts... un parpelleig... oberts
    return [closed, closed, half, opened, opened, opened, opened, opened, closed, half, opened]


ANIMS = {
    'ambient': {'frames': _ambient_frames, 'frameDuration': 125},
    'vet_ulls': {'frames': lambda: [Canvas(transparent=True).img], 'frameDuration': 1000, 'loop': False, 'zIndex': 2},
    'vet_desperta': {'frames': _ulls_frames, 'frameDuration': 150, 'loop': False, 'prop': 'vet_ulls'},
}

PROPS = {}
