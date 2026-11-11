"""
Art de Ferro-9 a 640×360 (×4/3 del de 480×270 de hd/). Es fa servir quan escala.RESOLUCIO = 640.

Importar `hd640` abans que cap `hd.rooms.*` posa la llibreria de dibuix a 640×360: pix.W/H, la mida per defecte de
Canvas i pix.K (disseny de 352×198 → 640×360, perquè R()/Pt() donin píxels de 640). Les sales són a
hd640/rooms/<sala>.py, amb la mateixa forma que les de hd/rooms (LIGHT, bg, PROPS, ANIMS); la geometria continua a
room_designs.py (en coordenades de 352×198), i a 640 s'escala sola. Vegeu preview.py.
"""
import hd.pix as pix

W, H = 640, 360
BAR_Y = 260          # 195 × 4/3: comença la franja de la frase i la barra de verbs
pix.W, pix.H = W, H
pix.K = W / 352
pix.Canvas.__init__.__defaults__ = (W, H, None, False, None)
