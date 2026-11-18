"""
Els crèdits (cinemàtica del final), a 640×360. EN 3D, a 1×: la mateixa Ginebra de nit del pròleg
(proleg_ginebra.py), des de la mateixa vora del llac, perquè el joc acabi on va començar.
  - el llac, les muntanyes, el raig d'aigua, el fanal i les branques, i la seu del BCMU en contrapicat, com al pròleg;
  - però la pantalla gegant de la façana ja no fa l'anunci del Director: està apagada (només hi queda el reflex
    de la lluna), amb un rètol de «FORA DE SERVEI», i a la torre hi ha menys finestres enceses (avui tothom ha
    plegat a l'hora);
  - el raig d'aigua, els reflexos i el llum de l'antena es mouen com al pròleg.
Animació: `nit`. El dibuix pla de la pantalla apagada és a credits_pla_comu.py.
"""
import hd640  # noqa: F401  (abans que cap hd.rooms: posa la llibreria a 640×360)

from hd640.rooms import proleg_ginebra as pr

LIGHT = pr.LIGHT
VARIANT = 'crèdits'


def bg(cv):
    cv.img.paste(pr.base_llum(VARIANT))
    cv.P = cv.img.load()


PROPS = {}

ANIMS = {'nit': {'frames': lambda: pr.nit_frames(VARIANT), 'frameDuration': 260}}

GEOMETRIA = {'things': {}, 'spawns': {}, 'walkable': [(200, 253), (267, 253), (267, 261), (200, 261)]}
