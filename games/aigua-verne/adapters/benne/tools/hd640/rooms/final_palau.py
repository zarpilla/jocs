"""
La cinemàtica final del palau: la galeria de les piscines (palau_galeria.py, en 3D) amb totes les piscines plenes.
La mateixa escena i la mateixa càmera, amb l'aigua a les vint-i-tres piscines; l'animació `aigua` hi fa córrer les
ones i el reflex dels llums d'aranya, projectats per la superfície de l'aigua de cada grup de piscines (el que hi ha
davant, l'aquari, la gandula o les escales cromades, les continua tapant). Sense res per clicar.
"""
import hd640  # noqa: F401

from hd640.rooms import palau_galeria as G

LIGHT = G.LIGHT


def bg(cv):
    img, _ = G._base(True)
    cv.img.paste(img)
    cv.P = cv.img.load()


PROPS = {}

AIGUES = {'aigua_piscines0', 'aigua_piscines1', 'aigua_piscines2', 'aigua_piscina_central'}


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
    # piscina i el Dividend a la dreta, al costat de la gandula
    'spawns': {'iri': G._p(300, 100), 'holm': G._p(392, 96), 'verne': G._p(206, 168), 'dividend': G._p(482, 118)},
}
