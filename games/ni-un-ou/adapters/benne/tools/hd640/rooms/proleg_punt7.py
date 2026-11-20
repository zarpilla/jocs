"""
Ni un ou — el pròleg (640×360). EN 3D, a 1×: cinemàtica a pantalla sencera, sense res clicable. L'Atlàntic Nord
de nit, al Punt 7, a les tres de la matinada.

És el mateix pla que la portada (portada.py: l'Arenga a prop i en 3/4, la plataforma petita a l'horitzó, la boia
en primer pla), sense el títol: «Comença» esvaeix el títol i hi entra. La zòdiac hi fa la seva història a trossos
(vegeu `portada.CLIPS`): cada frase de rooms/proleg_punt7.json engega el seu tros amb una indicació d'escena
(`{"prop": "zodiac", "anim": "z_baixa"}`). Ara és al món: penja gran a popa, la grua la baixa, i travessa en
diagonal (l'estela en V) fins a davant de la plataforma, on es fa petita. Al final s'encén el focus de la silueta de
la plataforma («vigia_on») i, darrere l'ull de bou fosc de la caseta, s'encén una pantalla petita («pantalla_on»):
algú hi escriu, i no es veu qui. En Bastida és a popa tota l'estona: és qui baixa la zòdiac amb la grua.
"""
import hd640  # noqa: F401  (abans que cap hd.rooms: posa la llibreria a 640×360)

import hd640.rooms.portada as portada

LIGHT = portada.LIGHT


def bg(cv, frame=0):
    portada.bg(cv, frame)


PROPS = {}

ANIMS = {
    'mar': {'frames': portada._frames, 'frameDuration': 300},
    'zodiac': portada.ZODIAC_ESPERA,
    **portada.ZODIAC_CLIPS,
    'bastida_popa': portada.BASTIDA,
    'pantalla': portada.PANTALLA,
    'pantalla_on': portada.PANTALLA_ON,
    'vigia': portada.VIGIA,
    'vigia_on': portada.VIGIA_ON,
}

# Les veus (personatges invisibles): en Bastida a la borda de popa, la Juana a la zòdiac penjada (quan arriba a la
# plataforma, el guió la mou a (468, 186): la zòdiac s'atura a (474, 199)).
GEOMETRIA = {
    'things': {},
    'spawns': {'bastida': (192, 200), 'juana': (195, 222)},
}
