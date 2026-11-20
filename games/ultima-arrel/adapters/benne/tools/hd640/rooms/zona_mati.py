"""
L'Última Arrel — `zona_mati`, la Zona Zero una hora abans (Escena 6a, Vet). Dilluns, Festa Major, les nou del matí.
Sala «de lluny».

És l'art de `zona_zero` (el mateix clar, l'escenari, la pantalla sobre la bastida, els sensors, l'altaveu i la
formigonera), però encara sense el públic:

  - no hi ha les dues files de gent (ni la capa del davant de la fila de davant);
  - el càmera de la TV Comarca té la càmera **al trípode**, amb el rètol «TV7» (és el que la Vet ha de veure per
    convèncer la Txell); el decorat `camera_espatlla` és el de la presentació: la càmera a l'espatlla, sense trípode;
  - a l'esquerra, l'àvia munta la **parada de melmelada**: una taula de taulons amb pots i un rètol;
  - el decorat `caseta_paper`: la caseta de paper que la Vet fa amb el fullet del Kit del Petit Guardabosc, dalt de
    tot de la pantalla, just a sobre dels sensors (l'amagatall de les fades).
"""
import functools

from hd.pix import Canvas
import hd640.rooms.zona_zero as Z
from hd640.rooms._comu_dia import (W, H, RH, lletres, ample, ombra, persona, diferencia, mascara, IRONK, PLANK, CREAM,
                                   PLASTIC, NEON, STEEL, REDL, CLAY)

LIGHT = Z.LIGHT
CAMERA = (628, 242)                                # els peus del càmera (com a la presentació)
TRIPODE = (606, 244)                               # el peu del trípode, davant del càmera
PARADA = (96, 202)                                 # la parada de l'àvia: el mig de la taula, a terra
CASETA = (548, 21)                                 # la caseta de paper: el mig de la base, damunt el marc de la pantalla


def camera_tripode(cv):
    """El càmera, dret, amb les mans buides, i la càmera de la TV damunt el trípode, davant seu: el rètol «TV7»."""
    x, y = CAMERA
    persona(cv, x, y, 84, 33, cara=1, polsera=False)
    ombra(cv, x + 10, y + 1, 12, 2.2, k=0.7)
    tx, ty = TRIPODE
    for dx in (-9, 0, 8):                                                                     # les tres potes
        cv.line(tx, ty - 30, tx + dx, ty - (2 if dx == 0 else 0), STEEL, 2.6, lit=0.3)
    ombra(cv, tx + 6, ty + 1, 10, 1.8, k=0.6)
    cv.rect(tx - 10, ty - 40, tx + 8, ty - 30, IRONK, lambda xx, yy: 2.0 + (xx - tx + 10) * 0.03, lit=0.3)
    cv.disc(tx - 11, ty - 35, 3, 4, IRONK, 3.2, lit=0)                                         # l'objectiu
    cv.flat(tx - 12, ty - 36, (160, 200, 240))
    cv.flat(tx + 7, ty - 39, (240, 40, 30))                                                    # gravant
    lletres(cv, 'TV7', tx - 7, ty - 38, (230, 230, 230))


def parada(cv):
    """La parada de melmelada de l'àvia, a mig muntar: una taula de taulons, uns quants pots i el rètol."""
    x, y = PARADA
    ombra(cv, x + 8, y + 1, 30, 2.4, k=0.6)
    for lx in (x - 24, x + 22):                                                                 # les potes
        cv.rect(lx, y - 14, lx + 2, y, PLANK, 2.4, lit=0.6)
    cv.rect(x - 28, y - 18, x + 28, y - 14, PLANK, lambda xx, yy: 4.2 - (yy - y + 18) * 0.5, lit=0.6)
    for k, px in enumerate(range(x - 22, x + 20, 8)):                                          # els pots
        cv.rect(px, y - 25, px + 5, y - 19, [(60, 10, 20), (110, 20, 34), (160, 40, 50), (200, 80, 80)],
                lambda xx, yy, px=px: 2.6 - (xx - px) * 0.2, lit=0.5)
        cv.rect(px, y - 27, px + 5, y - 26, CREAM if k % 2 else REDL, 3.6, lit=0.5)            # la tapa
    t = 'MELMELADA'
    w = ample(t)
    cv.rect(x - w // 2 - 3, y - 40, x + w // 2 + 3, y - 31, CREAM, 4.6, lit=0.4)                # el rètol
    for sx in (x - w // 2 - 1, x + w // 2):
        cv.rect(sx, y - 31, sx + 1, y - 26, PLANK, 2.0, lit=0.4)
    lletres(cv, t, x - w // 2, y - 38, (150, 40, 50))


def caseta_paper(cv):
    """La caseta de paper (el fullet de NaturaPlus doblegat en tres), dalt de la pantalla: blanca, amb la fulla verda
    fluor del logotip a fora, i a la porta, fosca, una cresta de fada que treu el cap."""
    cx, by = CASETA
    for yy in range(by - 10, by + 1):
        half = (yy - (by - 10)) * 0.9
        for xx in range(int(cx - half), int(cx + half) + 1):
            esquerra = xx < cx
            cv.put(xx, yy, PLASTIC, (5.2 if esquerra else 4.0) - (yy - by + 10) * 0.08, lit=0.4)
    for yy in range(by - 10, by + 1):                                                           # el plec del mig
        cv.put(cx, yy, PLASTIC, 2.8, lit=0.4)
    cv.disc(cx - 4, by - 4, 1.6, 1.4, NEON, 3.6, lit=0)                                         # el logotip
    cv.rect(cx + 2, by - 4, cx + 4, by, IRONK, 0.8, lit=0)                                      # la porta
    cv.flat(cx + 3, by - 5, (200, 210, 140))                                                    # una cresta de fada
    cv.flat(cx + 3, by - 6, (230, 236, 170))
    ombra(cv, cx + 3, by + 1, 9, 1, k=0.5)


@functools.lru_cache(maxsize=None)
def _render(espatlla=False, caseta=False):
    """La Zona Zero a les nou: com `zona_zero._base`, sense el públic, amb la parada de l'àvia i el càmera amb el
    trípode (o, amb `espatlla`, amb la càmera a l'espatlla, com a la presentació). → (fons, primer pla)."""
    cv = Canvas(W, H, light=LIGHT)
    Z.cel(cv)
    Z.bosc_fons(cv)
    Z.terra(cv)
    Z.formigonera(cv)
    Z.arbres_vora(cv)
    Z.branques(cv)
    Z.pantalla(cv)
    Z.soques(cv)
    Z.gespa(cv)
    Z.escenari(cv)
    Z.sensors(cv)
    Z.altaveu(cv)
    Z.bassal(cv)
    parada(cv)
    if espatlla:
        Z.camera(cv)
    else:
        camera_tripode(cv)
    if caseta:
        caseta_paper(cv)
    for y in range(RH, H):
        for x in range(W):
            cv.flat(x, y, (0, 0, 0))
    pp = Canvas(W, H, light=LIGHT, transparent=True)
    Z.primer_pla(pp)
    for y in range(RH, H):
        for x in range(W):
            pp.P[x, y] = (0, 0, 0, 0)
    cv.img.alpha_composite(pp.img)
    return cv.img, pp.img


def _base():
    return _render()[0]


def bg(cv):
    cv.img.paste(_base())
    cv.P = cv.img.load()


def _decorat(**estat):
    def draw(cv):
        img = _render(**estat)[0]
        d = diferencia(img, _base())
        # el primer pla és una capa a part: el decorat no l'ha de tapar
        m = mascara(_render()[1])
        a = d.load()
        for y in range(H):
            for x in range(W):
                if m(x, y):
                    a[x, y] = (0, 0, 0, 0)
        cv.img.alpha_composite(d)
        cv.P = cv.img.load()
    return draw


PROPS = {'camera_espatlla': _decorat(espatlla=True), 'caseta_paper': _decorat(caseta=True)}

ANIMS = {'formigonera': Z.ANIMS['formigonera']}

FRONT = [{'id': 'davant', 'mask': lambda x, y: mascara(_render()[1])(x, y), 'baseline': 999, 'zIndex': 22}]


# ─── Geometria ───────────────────────────────────────────────────────────────

_things = {k: v for k, v in Z.GEOMETRIA['things'].items() if k != 'public'}
_things['bastida'] = {'rect': (382, 112, 402, 180), 'walk': (392, 220)}
_things['parada'] = {'rect': (66, 160, 126, 204), 'walk': (100, 240)}

GEOMETRIA = {
    **Z.GEOMETRIA,
    'things': _things,
    'spawns': {'vet': (150, 244), 'avia': (132, 214), 'txell': (566, 240), 'urtica': Z.GEOMETRIA['spawns']['urtica'],
               'iri': (4, 246)},
}
