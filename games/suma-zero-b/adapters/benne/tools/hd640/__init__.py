"""
Prova de resolució: art a 640×360 (×4/3 de l'actual). No el fa servir el joc ni el sync.

Importar `hd640` abans que cap `hd.rooms.*` posa la llibreria de dibuix a 640×360: pix.W/H i la mida per
defecte de Canvas. Les sales són a hd640/rooms/<sala>.py, amb la mateixa forma que les de hd/rooms
(LIGHT, bg, PROPS, ANIMS, GEOMETRIA en coordenades de 640×360). Vegeu preview.py.
"""
import hd.pix as pix

W, H = 640, 360
BAR_Y = 260          # 195 × 4/3: comença la franja de la frase i la barra de verbs
pix.W, pix.H = W, H
pix.K = W / 480
pix.Canvas.__init__.__defaults__ = (W, H, None, False, None)
