"""
**El dibuix pla de sempre** (font de les textures de la sala en 3D, fabrica_conducte_revolt.py).

Entre revolt i revolt del conducte de servei (Iri), a 640×360: negre. L'Iri camina a les fosques fins al revolt
següent (o fins on surt), i el pas és només un fos a negre entre revolt i revolt. Hi surten, sobre el negre, les
frases de l'arribada al moll o de quan s'ha perdut. No és una cinemàtica (així la barra de verbs no desapareix i
torna a aparèixer a cada revolt), però no hi ha res per clicar (room_designs.py, `CONDUCTE_REVOLT`).
"""
import hd640  # noqa: F401  (posa la llibreria de dibuix a 640×360)
from hd.pix import W, H


def bg(cv):
    cv.img.paste((0, 0, 0, 255), (0, 0, W, H))


PROPS = {}
