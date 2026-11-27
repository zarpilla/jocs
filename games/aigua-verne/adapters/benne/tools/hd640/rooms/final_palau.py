"""
La cinemàtica final del palau: la galeria de les piscines (palau_galeria.py, en 3D), que s'omplen a la pantalla.
La mateixa escena i la mateixa càmera. El fons té les piscines buides, i l'aigua de cada grup de piscines és una capa
(`plena_<grup>`) que el final fa aparèixer d'una en una, en cascada (tasca 142). Quan totes són plenes, l'animació
`aigua` hi fa córrer les ones i el reflex dels llums d'aranya, projectats per la superfície de l'aigua de cada grup
de piscines (el que hi ha davant, l'aquari, la gandula o les escales cromades, les continua tapant). Sense res per
clicar.
"""
import functools
import hd640  # noqa: F401

from hd640.rooms import palau_galeria as G

LIGHT = G.LIGHT
ROOM_W = G.ROOM_W                                  # (la galeria és més ampla que la pantalla)


def bg(cv):
    img, _ = G._base()
    cv.img.paste(img)
    cv.P = cv.img.load()


AIGUES = {'aigua_piscines0', 'aigua_piscines1', 'aigua_piscines2', 'aigua_piscina_central'}
# L'ordre de la cascada: les terrasses del fons cap endavant, i la central (la de la reserva) l'última.
GRUPS = ('piscines0', 'piscines1', 'piscines2', 'piscina_central')


@functools.lru_cache(maxsize=None)
def _capes_plenes():
    """El que canvia en omplir-se les piscines, repartit per grups: cada píxel, al grup de l'aigua que hi ha al
    davant (la superfície, el reflex a la vora). El que no és de cap aigua (els reflexos fora), a la central."""
    from PIL import Image
    full, e = G._base(True)
    d = G._diff(full, G._base()[0])
    capes = {g: Image.new('RGBA', d.size, (0, 0, 0, 0)) for g in GRUPS}
    src, dst, w = d.load(), {g: c.load() for g, c in capes.items()}, e.cv.w
    for y in range(d.height):
        for x in range(d.width):
            px = src[x, y]
            if not px[3]:
                continue
            sid = e.ids[e.amo[y * w + x]]
            g = sid[len('aigua_'):] if sid in AIGUES else 'piscina_central'
            dst[g][x, y] = px
    return capes


def _plena(g):
    def draw(cv):
        cv.img.alpha_composite(_capes_plenes()[g])
    return draw


PROPS = {f'plena_{g}': _plena(g) for g in GRUPS}


def _frames_aigua(n=8):
    _, e = G._base(True)
    return [e.capa(G.aigua_tex(i), AIGUES) for i in range(n)]


ANIMS = {'peixos': G.ANIMS['peixos'],
         'estrelles': G.ANIMS['estrelles'],
         'aigua': {'frames': _frames_aigua, 'frameDuration': 180}}

FRONT = G.FRONT

GEOMETRIA = {
    **{k: v for k, v in G.GEOMETRIA.items() if k not in ('things', 'spawns')},
    'things': {},
    # tots quatre davant la piscina central, la de la reserva: la Iri i en Holm a prop, en Verne a l'esquerra de la
    # piscina i el Dividend a la dreta, al costat de la gandula. La Lia i la Vet, que vénen a buscar la Iri, a la porta
    # del saló (amagades fins que hi entren).
    'spawns': {'iri': G._p(300, 100), 'holm': G._p(392, 96), 'verne': G._p(206, 168), 'dividend': G._p(482, 118),
               'lia': (208, 189), 'vet': (224, 191)},
}
