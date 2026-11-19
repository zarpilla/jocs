"""
**El dibuix pla de sempre** (font de les textures de la sala en 3D, proleg_punt7.py).

Prova a 640×360: el pròleg (vegeu hd/rooms/proleg_punt7.py, el de 480×270). Cinemàtica a pantalla sencera,
sense res clicable: l'Atlàntic Nord de nit, al Punt 7, a les tres de la matinada.

És el mateix pla que la portada, sense el títol: «Comença» esvaeix el títol i hi entra. La zòdiac hi fa la seva
història a trossos, de fons i sense detall (vegeu `portada.CLIPS`): cada frase de rooms/proleg_punt7.json engega
el seu tros amb una indicació d'escena (`{"prop": "zodiac", "anim": "z_baixa"}`). Al final s'encén el focus de la
silueta de la plataforma («vigia_on») i en Bastida, a popa, treu el missatger i escriu («bastida_escriu»).
"""
import hd640  # noqa: F401  (abans que cap hd.rooms: posa la llibreria a 640×360)

from hd.pix import Light
import hd640.rooms.portada_pla_comu as portada

from hd.pix import Canvas  # noqa: E402,F811  (a 1×: és la font de les textures de la sala en 3D)
Canvas1x = Canvas

LIGHT = Light(ambient=0.0, vignette=None, floor_fade=None)


def bg(cv, frame=0):
    portada.bg(cv, frame)


PROPS = {}

ANIMS = {
    'mar': {'frames': portada._frames, 'frameDuration': 300},
    'zodiac': portada.ZODIAC_ESPERA,
    **portada.ZODIAC_CLIPS,
    'bastida_popa': portada.BASTIDA,
    'bastida_escriu': portada.BASTIDA_ESCRIU,
    'vigia': portada.VIGIA,
    'vigia_on': portada.VIGIA_ON,
}

# Les veus (personatges invisibles): en Bastida a popa, la Juana a la zòdiac (es mou amb `at` quan arriba).
