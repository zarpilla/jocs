"""
Prova de densitat: art a 1280×720 (2× el de 640×360). No el fa servir el joc ni el sync.

`Canvas2x` pinta a 1280×720 però rep coordenades de sala de 640×360, de manera que el codi de les sales de
hd640/rooms hi funciona sense tocar-lo: les formes (discos, polígons, línies), els degradats, el dither, la llum i
els efectes es calculen a la resolució real; `px()` pinta un sol píxel real (per al detall fet a mà).
Vegeu hd1280/pis_estudi.py.
"""
