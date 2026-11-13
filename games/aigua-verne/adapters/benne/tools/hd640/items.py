"""
Icones d'inventari d'Aigua Verne a 640×360: 65×36 (la casella de la barra de verbs, hd640/gui.py), dibuixades
píxel a píxel amb el sistema de hd/items.py (Ic: volum amb llum de dalt a l'esquerra, rampes per material i el
contorn fosc selectiu dels personatges).

Els objectes es veuen damunt les pantalletes verdes de fòsfor de la barra (negre verdós): cada icona ha de tenir
prou contrast i una silueta clara. Els papers, cadascun del seu color (groguenc, blanc, rosa de calcar...), per
distingir-los d'una ullada.

No toca hd/items.py: en reaprofita els materials i les eines i només canvia la mida del llenç.
Ho fan servir draw_items.py / draw_placeholders.py (inventari del joc) i hd640/draw_items.py (full de prova).
"""
import math

from hd.characters import Fig
from hd.pix import hr
from hd.items import (Ic, paper, torn, FONT, M, PAP_W, PAP_F, PAP_C, PAP_O, GRAPH, INKB, INKG, STAMP, SEPIA,
                      ACER, IRON, CLOTH, DARK, BLK, LCD, LED, GOLDK, REDP, PAPV, VELV, WOOD, WATER, BLUEC,
                      CORPG, LIME, GRIP, CABLE)

W, H = 65, 36

# ─── Materials propis ───────────────────────────────────────────────────────
WEB = M((12, 14, 8), (24, 28, 14), (40, 46, 24), (60, 68, 36), (84, 92, 52), (112, 118, 74))      # cinta oliva
OLIV = M((14, 16, 8), (30, 34, 18), (50, 56, 30), (72, 80, 44), (98, 106, 62), (130, 136, 88), (170, 174, 128))  # planxa
SAFE = M((56, 16, 6), (110, 38, 10), (176, 70, 16), (226, 106, 24), (250, 150, 56), (255, 200, 130))  # taronja
VAC = M((40, 8, 12), (86, 16, 20), (142, 30, 30), (196, 54, 42), (232, 96, 74), (250, 152, 130))      # plàstic d'aspirador
BAGP = M((60, 66, 76), (104, 112, 122), (150, 158, 166), (196, 202, 208), (232, 236, 240))           # hèlix (plàstic)
BURL = M((34, 24, 14), (68, 52, 30), (108, 86, 54), (146, 120, 78), (182, 156, 106), (214, 192, 142),
         (236, 220, 178))                                                                        # tela de sac
ALU = M((34, 38, 46), (72, 78, 90), (114, 120, 132), (156, 162, 172), (196, 200, 208), (226, 230, 236),
        (248, 250, 252))                                                                          # paper d'alumini
CERAM = M((58, 54, 58), (106, 102, 100), (154, 150, 144), (196, 192, 184), (226, 224, 216), (246, 244, 238))
ZINC = M((24, 28, 32), (44, 50, 56), (70, 78, 84), (100, 108, 114), (134, 142, 146), (170, 176, 178),
         (206, 210, 210), (236, 238, 236))                                                         # zinc
WAX = M((40, 6, 10), (84, 12, 18), (136, 22, 26), (182, 38, 36), (220, 74, 60), (244, 128, 106))    # cera de segell
SAND = M((92, 88, 78), (140, 136, 124), (184, 180, 168), (216, 212, 200), (238, 236, 226), (252, 250, 244))
MOULD = M((26, 20, 16), (48, 38, 30), (76, 62, 46), (106, 88, 64), (136, 114, 84), (166, 142, 108))  # sorra de fosa
HAM = M((58, 12, 22), (104, 26, 38), (154, 48, 58), (196, 80, 84), (224, 120, 118), (244, 168, 160))
FAT = M((120, 92, 92), (176, 150, 146), (216, 198, 190), (238, 228, 220), (252, 246, 240))
PAPR = M((70, 40, 50), (132, 98, 106), (190, 160, 166), (226, 206, 208), (244, 232, 232), (252, 246, 246))  # rosa de calcar
OIL = M((60, 34, 6), (120, 76, 10), (186, 128, 24), (232, 180, 60), (252, 224, 130))                # oli
CARD = M((70, 74, 86), (124, 128, 140), (174, 178, 188), (214, 216, 222), (238, 240, 244), (252, 252, 254))
AQUAB = M((8, 26, 60), (16, 52, 112), (30, 90, 168), (64, 136, 214), (130, 190, 240), (210, 236, 252))  # el blau d'Aqua
RUB = M((8, 8, 10), (20, 20, 24), (36, 36, 42), (56, 56, 62), (82, 82, 88), (114, 114, 120), (150, 150, 154))   # goma
PEARL = M((90, 84, 96), (150, 146, 156), (206, 202, 208), (236, 234, 238), (255, 255, 255))

# Lletres de 4×6 per a les xifres grosses
FONT46 = {
    '7': ('####', '...#', '..#.', '..#.', '.#..', '.#..'),
    '8': ('.##.', '#..#', '.##.', '#..#', '#..#', '.##.'),
    '.': ('.', '.', '.', '.', '.', '#'),
}


class Ic640(Ic):
    """Llenç d'una icona de 640: el mateix Ic, a 65×36."""

    def __init__(self):
        Fig.__init__(self, W, H)


def text_w(s, font=FONT, sp=1):
    return sum(len(font[c][0]) + sp for c in s) - sp


def ctext(f, cx, y, s, mat, lvl, font=FONT):
    """Text centrat a cx."""
    f.text(round(cx - text_w(s, font) / 2), y, s, mat, lvl, font=font)


def weave(f, S, mat, d=-0.45, step=3):
    """Textura de tela: un quadriculat fluix que enfosqueix un fil de cada `step`."""
    for (x, y) in S:
        if (x % step == 0) or (y % step == 0 and hr(x, y, 4) > 0.3):
            f.shade(x, y, d, only=mat)


# ─── Comunicació ────────────────────────────────────────────────────────────

def comunicador(f):
    """El comunicador de canell: corretja de cinta oliva amb la sivella, la caixa de planxa amb cargols, la
    pantalleta verda (una ona de veu), dos botons taronja i l'antena curta."""
    for (x0, x1) in ((3, 20), (44, 61)):                                  # la corretja, a banda i banda
        S = f.R(x0, 13, x1, 23)
        f.drop(S)
        f.fill(S, WEB, lambda x, y: 3.2 - (y - 13) * 0.08, rim=(0.6, -1.0))
        for x in range(x0, x1 + 1, 2):
            f.shade(x, 14, 0.6)
            f.shade(x, 22, -0.6)
    for x in (8, 13):                                                     # els forats
        f.px(x, 18, DARK, 0.6)
    f.rect(52, 12, 55, 24, ACER, 4.6, rim=(0.6, -1.2))                    # la sivella
    f.rect(53, 14, 54, 22, WEB, 2.6)
    S = f.R(19, 5, 45, 31) - {(19, 5), (45, 5), (19, 31), (45, 31), (20, 5), (19, 6), (44, 5), (45, 6)}
    f.drop(S, -1.6)
    f.fill(S, OLIV, lambda x, y: 3.8 - (x - 19) * 0.03 - (y - 5) * 0.04, rim=(0.8, -1.4))
    f.rect(22, 8, 42, 25, DARK, 1.0)                                      # el marc de la pantalla
    f.rect(23, 9, 41, 24, LCD, lambda x, y: 2.4 - (y - 9) * 0.06 - (0.5 if y % 2 else 0))
    for x in range(24, 41):                                              # l'ona de veu
        y = 16.5 + math.sin((x - 24) * 0.9) * (1 + 3.5 * math.sin((x - 24) / 16 * math.pi))
        f.px(x, round(y), LCD, 4.4)
    f.px(24, 10, LCD, 4.0)                                                # el reflex del vidre
    f.px(25, 10, LCD, 3.6)
    f.px(24, 11, LCD, 3.6)
    for x in (24, 30):                                                    # els botons
        f.rect(x, 27, x + 4, 28, SAFE, 3.6, rim=(0.6, -1.0))
    f.px(40, 27, LED, 3.0)                                                # el pilot
    for (x, y) in ((21, 7), (43, 7), (21, 29), (43, 29)):                 # cargols
        f.px(x, y, ACER, 5.0)
    f.limb((43, 5), (47, 1), 1.0, 0.8, BLK, 3.2, amp=1.4)                 # l'antena


def mosca(f):
    """La Mosca: el dron de la Vet fet amb un aspirador. El cos és el dipòsit vermell de l'aspirador, amb el
    raspall al morro; quatre braços de tub corrugat i quatre hèlixs que giren (borroses), l'ull de càmera."""
    rot = ((11, 8), (53, 8), (9, 25), (55, 25))
    for (rx, ry) in rot:                                                  # els braços (tub corrugat)
        f.limb((32, 17), (rx, ry + 2), 1.6, 1.4, BLK, 3.2, amp=1.6)
    for k, (rx, ry) in enumerate(rot):
        for t in range(0, 20, 3):
            x = 32 + (rx - 32) * t / 20
            y = 17 + (ry + 2 - 17) * t / 20
            f.shade(x, y, -0.8)
    for (rx, ry) in rot:                                                  # els motors i les hèlixs
        f.rect(rx - 1, ry, rx + 1, ry + 3, ACER, 3.6, rim=(0.6, -1.0))
        S = f.E(rx, ry - 1, 9, 1.6)
        for (x, y) in S:
            if hr(x, y, 8) > 0.25:
                f.px(x, y, BAGP, 3.0 + (1.0 if abs(x - rx) > 5 else 0) - (y - ry + 1) * 0.6)
        f.px(rx, ry - 1, DARK, 0.8)
    S = f.ell(32, 18, 10, 7.5, VAC, 3.2, amp=2.0)                         # el dipòsit de l'aspirador
    f.shine(S, 0.86, 1.4)
    for x in range(23, 42):                                               # la junta del dipòsit
        f.shade(x, 18 + round(((x - 32) / 10) ** 2 * 3), -1.2)
    f.rect(26, 24, 38, 27, BLK, 2.8, rim=(0.6, -1.0))                     # el raspall, al morro
    for x in range(26, 39, 2):
        f.px(x, 28, CLOTH, 2.6)
    f.fill(f.E(32, 14, 3, 2.6), DARK, 1.0, rim=None)                      # l'ull de la càmera
    f.fill(f.E(32, 14, 1.6, 1.4), BLUEC, 3.6, rim=None)
    f.px(31, 13, BLUEC, 5.4)
    f.px(39, 12, LED, 3.2)                                                # el pilot vermell


# ─── Eines ──────────────────────────────────────────────────────────────────

def _flor(f, cx, cy, lvl=5.6):
    """Una punta de flor vista de cara (5×5): sis lòbuls i el forat del mig."""
    for (dx, dy) in ((-1, -2), (1, -2), (-2, -1), (-1, -1), (0, -1), (1, -1), (2, -1), (-1, 0), (1, 0),
                     (-2, 1), (-1, 1), (0, 1), (1, 1), (2, 1), (-1, 2), (1, 2), (0, -2), (0, 2)):
        f.px(cx + dx, cy + dy, ACER, lvl + 1.0 - (dx + dy) * 0.35)
    f.px(cx, cy, DARK, 0.6)


def punta_flor(f):
    """L'estoig de puntes de tornavís de cap de flor: capsa de llauna vermella oberta, la tapa amb l'etiqueta i
    cinc puntes d'acer dretes, cadascuna amb la flor de sis lòbuls a dalt."""
    L = f.P([(10, 3), (54, 3), (56, 13), (8, 13)])                        # la tapa, oberta enrere
    f.drop(L)
    f.fill(L, REDP, lambda x, y: 2.6 + (y - 3) * 0.08, rim=(0.6, -1.0))
    f.rect(22, 5, 42, 11, PAP_C, 4.0, rim=(0.4, -0.8))                    # l'etiqueta, amb una flor
    _flor(f, 27, 8, 0.6)
    f.rect(31, 7, 39, 7, INKG, 1.6)
    f.rect(31, 9, 37, 9, INKG, 2.2)
    B = f.R(8, 17, 56, 32)                                                # la capsa
    f.drop(B, -1.6)
    f.fill(B, REDP, lambda x, y: 3.4 - (y - 17) * 0.06, rim=(0.8, -1.4))
    f.rect(10, 18, 54, 21, DARK, 1.2)                                     # la gomaescuma
    for i in range(5):                                                    # les puntes
        x = 15 + i * 8.5
        f.rect(x - 1, 15, x + 1, 21, ACER, lambda xx, yy, x=x: 4.8 - (xx - x) * 1.2, rim=None)
        f.rect(x - 1, 17, x + 1, 17, ACER, 2.4)
        _flor(f, x, 12)
    f.rect(10, 26, 54, 26, REDP, 2.2)                                     # el plec de la llauna
    f.rect(10, 27, 54, 27, REDP, 4.2)
    for x in range(12, 53, 7):                                            # rovell a la vora
        if hr(x, 3) > 0.5:
            f.px(x, 31, (110, 54, 26), 0)


def _tornavis(f, flor=False):
    """El tornavís vell: mànec de fusta gastada amb cinta aïllant, la virolla, la tija i la punta."""
    f.limb((4, 31), (23, 21), 3.8, 4.4, WOOD, 3.8, amp=2.0)               # el mànec
    for t in (0.2, 0.35, 0.5):                                            # les estries
        x, y = 4 + 19 * t, 31 - 10 * t
        f.line(x - 1, y - 2.5, x + 1.5, y + 2.5, WOOD, 2.2)
    for t in (0.66, 0.74):                                                # la cinta aïllant
        x, y = 4 + 19 * t, 31 - 10 * t
        for d in range(-4, 5):
            f.px(x + d * 0.45, y + d * 0.9, BLK, 2.6 if d < 0 else 1.6)
    for (x, y) in ((8, 27), (15, 25)):                                    # la fusta pelada
        f.px(x, y, WOOD, 5.6)
    f.limb((23, 21), (28, 18), 2.6, 2.3, ACER, 4.6, amp=2.0)              # la virolla
    f.limb((28, 18), (51, 8), 1.6, 1.5, ACER, 4.4, amp=2.6)               # la tija
    for t in (0.3, 0.6):
        f.px(28 + 23 * t, 18 - 10 * t - 1, ACER, 6.8)
    if flor:
        f.limb((50, 8), (54, 6), 2.4, 2.6, ACER, 4.8, amp=2.0)            # el portapuntes
        cx, cy = 57, 5                                                    # la punta de flor, de cara
        for k in range(6):
            a = math.radians(k * 60 + 15)
            f.fill(f.E(cx + math.cos(a) * 2.6, cy + math.sin(a) * 2.6, 1.5, 1.5), ACER,
                   6.0 - math.sin(a) * 1.4 - math.cos(a) * 0.8, rim=None)
        f.fill(f.E(cx, cy, 1.6, 1.6), ACER, 4.6, rim=None)
        f.px(cx, cy, DARK, 0.6)
    else:
        f.fill(f.P([(49, 7), (57, 2), (59, 5), (52, 11)]), ACER, 5.4, rim=(0.8, -1.4))   # la pala
        f.px(57, 3, ACER, 7.0)


def tornavis(f):
    """El tornavís vell, de pala."""
    _tornavis(f)


def tornavis_flor(f):
    """El tornavís amb la punta de cap de flor posada."""
    _tornavis(f, flor=True)


def clau_anglesa(f):
    """La clau anglesa grossa: mànec d'acer amb el forat, el cap amb les dues mandíbules obertes i el cargol
    sens fi moleteat."""
    f.limb((5, 32), (40, 16), 3.0, 3.6, ACER, 4.2, amp=2.4)              # el mànec
    for t in (0.35, 0.55):                                               # la marca en relleu
        x, y = 5 + 35 * t, 32 - 16 * t
        f.shade(x, y - 1, 1.2)
    f.fill(f.E(8, 30.5, 1.6, 1.3), DARK, 0.6, rim=None)                   # el forat
    S = f.E(46, 13, 10, 9)                                                # el cap
    c, d, n = (47, 12), (0.72, -0.69), (0.69, 0.72)                       # la boca: cap amunt a la dreta
    J = f.P([(c[0] - n[0] * 3, c[1] - n[1] * 3), (c[0] + n[0] * 3, c[1] + n[1] * 3),
             (c[0] + n[0] * 3 + d[0] * 16, c[1] + n[1] * 3 + d[1] * 16),
             (c[0] - n[0] * 3 + d[0] * 16, c[1] - n[1] * 3 + d[1] * 16)])
    S -= J
    S -= f.P([(54, 21), (60, 15), (60, 24)])                              # el cap, que no sigui rodó
    f.drop(S)
    f.fill(S, ACER, lambda x, y: 5.0 - (x - 36) * 0.06 - (y - 4) * 0.12, rim=(0.8, -1.6))
    for (x, y) in S:                                                      # la cara de dins de les mandíbules
        if (x - 1, y) in J or (x, y - 1) in J:
            f.px(x, y, ACER, 2.4)
    S = f.R(38, 18, 47, 23)                                               # el cargol sens fi
    f.fill(S, ACER, lambda x, y: 4.2 - (y - 18) * 0.4, rim=None)
    for x in range(38, 48, 2):
        f.rect(x, 18, x, 23, ACER, 2.0)
    f.px(41, 7, ACER, 7.2)


def oli(f):
    """La llauna d'oli: cos vermell amb l'etiqueta i una gota d'oli dibuixada, el con de dalt, la nansa, el
    polsador i el broc llarg amb una gota a la punta."""
    f.ring(10, 20, 5, 7, ACER, 3.2, th=1.6)                               # la nansa
    S = f.lathe(16, 32, lambda y: (12, 32), REDP, 3.2, amp=2.2)           # el cos
    f.shine(S, 0.78, 1.2)
    f.rect(12, 32, 32, 32, REDP, 1.4)
    f.rect(14, 21, 30, 28, PAP_C, 4.0, rim=(0.4, -1.0))                   # l'etiqueta
    for (dx, dy, v) in ((0, -2, 3.2), (-1, -1, 3.0), (0, -1, 3.6), (-1, 0, 2.8), (0, 0, 3.4), (1, 0, 2.6),
                        (0, 1, 2.4)):
        f.px(18 + dx, 24 + dy, OIL, v)                                    # la gota
    f.rect(21, 23, 28, 23, INKG, 1.4)
    f.rect(21, 25, 26, 25, INKG, 2.2)
    f.lathe(9, 15, lambda y: (22 - (y - 9) * 1.6, 22 + (y - 9) * 1.6), ACER, 4.0, amp=2.0)   # el con
    f.rect(12, 15, 32, 15, ACER, 2.4)
    f.rect(19, 5, 21, 9, ACER, 4.4, rim=(0.6, -1.0))                      # el polsador
    f.limb((24, 10), (56, 3), 1.6, 0.8, ACER, 4.4, amp=2.0)               # el broc
    f.fill(f.E(58, 6, 1.2, 1.8), OIL, 3.4, rim=(0.6, -0.8))               # la gota
    f.px(58, 5, OIL, 4.6)


def injector(f):
    """L'injector del tractor: peça de llautó petita, amb el cos rodó, la femella hexagonal, el broc d'acer, la
    presa de gasoil de dalt i el connector negre del darrere. Una mica de brutícia de gasoil."""
    f.rect(6, 14, 13, 22, BLK, 3.0, rim=(0.6, -1.0))                      # el connector
    f.rect(4, 16, 5, 20, BLK, 2.0)
    for y in (16, 18, 20):
        f.px(9, y, GOLDK, 4.0)
    f.hcyl(13, 42, 18, 5.4, GOLDK, 3.4)                                   # el cos
    for x in range(14, 22, 2):                                            # la rosca
        for y in range(13, 24):
            f.shade(x, y, -0.8)
    S = f.R(25, 10, 32, 26)                                               # la femella
    f.drop(S)
    f.fill(S, GOLDK, lambda x, y: 4.0 - abs(y - 15) * 0.15, rim=(0.8, -1.4))
    f.rect(25, 18, 32, 18, GOLDK, 2.4)
    f.lathe(4, 10, lambda y: (35, 39), GOLDK, 3.4, amp=2.0)               # la presa de dalt
    f.fill(f.E(37, 4, 2, 1), DARK, 0.8, rim=None)
    f.limb((42, 18), (56, 18), 3.0, 1.2, ACER, 4.4, amp=2.2)              # el broc
    f.px(57, 18, DARK, 0.6)
    for (x, y) in ((16, 22), (36, 21), (40, 14), (22, 23)):               # gasoil
        f.px(x, y, (70, 50, 20), 0)


def fusible(f, apanyat=False):
    """El fusible de ceràmica: cos blanc amb la xifra, els caps d'acer i les pestanyes, i la socarrimada del mig.
    Si és `apanyat`, el cos embolicat amb paper de plata."""
    for x0, x1 in ((7, 12), (51, 56)):                                    # les pestanyes
        f.rect(x0, 16, x1, 20, ACER, 4.4, rim=(0.6, -1.2))
    f.fill(f.E(9, 18, 0.9, 0.9), DARK, 0.6, rim=None)
    f.fill(f.E(54, 18, 0.9, 0.9), DARK, 0.6, rim=None)
    f.hcyl(19, 44, 18, 6.0, CERAM, 3.6)                                   # el cos de ceràmica
    for x0, x1 in ((12, 18), (45, 51)):                                   # els caps
        f.hcyl(x0, x1, 18, 7.0, ACER, 4.2)
        f.rect(x0, 11, x0, 25, ACER, 2.4)
    if not apanyat:
        f.text(24, 15, '10A', INKG, 1.2)
        for (x, y) in ((36, 19), (37, 20), (38, 19), (37, 18), (39, 21), (36, 21)):   # socarrimat
            f.px(x, y, (60, 40, 30), 0)
        f.px(37, 19, (30, 20, 18), 0)
        return
    _foil(f, f.P([(15, 12), (27, 10), (40, 13), (49, 11), (50, 24), (38, 27), (24, 25), (14, 26)]), seed=5)
    f.px(52, 11, IRON, 4.0)


def _foil(f, S, seed=0, n=14):
    """Paper d'alumini arrugat: cel·les (facetes) amb inclinacions a l'atzar i arestes que brillen."""
    xs, ys = [p[0] for p in S], [p[1] for p in S]
    pts = [(min(xs) + hr(seed, i, 1) * (max(xs) - min(xs)), min(ys) + hr(seed, i, 2) * (max(ys) - min(ys)))
           for i in range(n)]
    lv = [2.4 + hr(seed, i, 3) * 3.0 for i in range(n)]

    def cell(x, y):
        return min(range(n), key=lambda i: (x - pts[i][0]) ** 2 + (y - pts[i][1]) ** 2)

    c = {p: cell(*p) for p in S}
    f.drop(S)
    for (x, y), k in c.items():
        l = lv[k] - (y - min(ys)) * 0.04
        if c.get((x + 1, y), k) != k or c.get((x, y + 1), k) != k:
            l += 1.8 if hr(x, y, seed) > 0.4 else -1.2                    # arestes
        if (x + 1, y) not in S or (x, y + 1) not in S:
            l -= 1.2
        f.px(x, y, ALU, l)


def fusible_apanyat(f):
    """El fusible fos, embolicat amb paper de plata perquè torni a fer contacte."""
    fusible(f, apanyat=True)


def paper_plata(f):
    """Un tros de paper d'alumini arrugat, amb les facetes i les arestes que brillen."""
    S = f.P([(10, 10), (22, 4), (36, 7), (50, 3), (57, 13), (54, 26), (44, 32), (28, 29), (14, 32), (7, 21)])
    _foil(f, S, seed=2, n=18)


# ─── Papers ─────────────────────────────────────────────────────────────────

def escriptura(f):
    """L'escriptura antiga de la granja: pergamí groguenc de vores gastades, la caplletra vermella, la
    cal·ligrafia, i el segell de cera vermella amb les dues cintes."""
    S = torn(f.R(12, 2, 52, 33), 'lrb', seed=3, depth=1)
    paper(f, S, PAP_O, 4.0, w=40, h=31)
    for (x, y) in S:                                                      # taques de vell
        if hr(x // 3, y // 3, 7) > 0.85:
            f.shade(x, y, -0.6)
    f.fill(f.R(15, 5, 19, 10), STAMP, 2.8, rim=(0.6, -0.8))               # la caplletra
    f.rect(16, 6, 18, 6, PAP_O, 4.6)
    f.rect(17, 7, 17, 9, PAP_O, 4.6)
    for y in (6, 9):
        f.scrib(21, 48, y, SEPIA, 1.2, seed=y, dens=0.9, tall=0.3)
    for y in (12, 15, 18, 21):
        f.scrib(15, 48, y, SEPIA, 1.4, seed=y + 4, dens=0.85, tall=0.3)
    f.limb((40, 28), (36, 35), 1.6, 1.4, BLUEC, 3.0, amp=1.4)             # les cintes
    f.limb((42, 28), (46, 35), 1.6, 1.4, BLUEC, 2.6, amp=1.4)
    S = f.E(41, 26, 5.2, 4.8)                                             # el segell
    f.drop(S, -1.6)
    f.fill(S, WAX, lambda x, y: 3.4 - (x - 36) * 0.08 - (y - 21) * 0.1, rim=(0.8, -1.4))
    f.ring(41, 26, 3, 2.8, WAX, 2.0, th=0.8)
    f.px(41, 26, WAX, 1.8)
    f.px(39, 23, WAX, 5.2)


def contracte_7788(f):
    """El contracte de Verne: paper groguenc, la xifra «7.788» grossa a dalt i, a sota, lletra petita i més
    lletra petita, amb un asterisc i una signatura."""
    S = f.R(15, 1, 49, 34) - {(49, 1), (48, 1), (49, 2)}
    paper(f, S, PAP_O, 4.4, w=35, h=34)
    f.px(48, 2, PAP_O, 2.6)
    f.fill(f.P([(18, 3), (21, 3), (19.5, 6)]) | {(19, 6), (20, 6)}, AQUAB, 3.2, rim=None)   # la gota de Verne
    f.rect(23, 4, 40, 4, INKG, 1.6)
    ctext(f, 32, 8, '7.788', INKG, 0.4, font=FONT46)
    f.px(44, 8, INKG, 0.6)                                                # l'asterisc
    for y in range(17, 31):                                               # la lletra petita
        if y % 2:
            f.scrib(18, 46, y, INKG, 2.2, seed=y, dens=0.95, tall=0)
    f.line(36, 32, 45, 31, INKB, 1.4)                                     # la signatura
    f.line(38, 31, 41, 33, INKB, 1.4)


def albara(f):
    """L'albarà: una còpia de calcar rosa, amb la capçalera, la taula de quantitats i una signatura gran."""
    S = f.R(16, 2, 48, 34)
    paper(f, S, PAPR, 4.2, w=33, h=33)
    f.rect(17, 3, 47, 7, PAPR, 2.4)                                       # la capçalera
    f.rect(19, 5, 32, 5, PAPR, 5.0)
    f.rect(41, 4, 45, 6, PAPR, 4.4)
    f.rect(18, 9, 46, 9, INKG, 2.0)
    for y in range(11, 24, 3):                                            # les files
        f.scrib(19, 34, y, INKB, 1.8, seed=y, dens=0.7, tall=0)
        f.scrib(40, 45, y, INKB, 1.8, seed=y + 3, dens=0.9, tall=0)
        f.rect(18, y + 1, 46, y + 1, PAPR, 3.4)
    f.rect(37, 10, 37, 24, PAPR, 2.6)
    for i in range(22):                                                   # la signatura
        x = 21 + i
        y = 29 + math.sin(i * 0.9) * 2.2 - i * 0.08
        f.px(x, round(y), INKB, 1.0)
    f.line(22, 31, 44, 30, INKB, 1.6)


def carta_juana(f):
    """La carta de la Juana: un sobre blanc blavós vist pel darrere, amb la solapa i el segell blau d'Aqua (una
    ona), i lletra a llapis d'en Bru escrita de través."""
    S = f.R(8, 6, 56, 31)
    paper(f, S, PAPV, 4.4, w=49, h=26)
    for x in range(8, 57):                                                # la solapa
        y = 6 + (x - 8) * 11 / 24 if x <= 32 else 6 + (56 - x) * 11 / 24
        f.px(x, round(y), PAPV, 2.4)
        f.px(x, round(y) + 1, PAPV, 3.4)
    for (a, b) in (((8, 31), (26, 18)), ((56, 31), (38, 18))):
        f.line(a[0], a[1], b[0], b[1], PAPV, 3.2)
    for y in (22, 25, 28):                                                # la lletra d'en Bru
        f.scrib(12, 26 if y == 22 else 30, y, GRAPH, 1.0, seed=y + 40, dens=0.9, tall=0.3)
        f.scrib(36, 52, y, GRAPH, 1.0, seed=y + 50, dens=0.9, tall=0.3)
    S = f.E(32, 17, 4.6, 4.2)                                             # el segell d'Aqua
    f.drop(S)
    f.fill(S, AQUAB, lambda x, y: 3.2 - (x - 28) * 0.06 - (y - 13) * 0.08, rim=(0.8, -1.2))
    for x in range(29, 36):                                               # l'ona
        f.px(x, 17 + round(math.sin((x - 29) * 1.1)), AQUAB, 5.0)
    f.px(30, 14, AQUAB, 5.4)


def carta_banc(f):
    """La carta del Banc de Vesper: paper blanc fred, capçalera «BANC DE VESPER» amb la columna del banc,
    paràgrafs mecanografiats, un segell vermell i la signatura."""
    S = f.R(13, 1, 51, 34)
    paper(f, S, PAP_W, 4.4, w=39, h=34)
    f.rect(16, 4, 18, 9, INKG, 0.8)                                      # la columna del logotip
    f.rect(15, 3, 19, 3, INKG, 0.8)
    f.rect(15, 10, 19, 10, INKG, 0.8)
    f.text(22, 3, 'BANC DE', BLUEC, 1.2)
    f.text(22, 9, 'VESPER', BLUEC, 1.2)
    f.rect(15, 15, 49, 15, BLUEC, 2.4)
    for y in (18, 20, 22, 24, 26):
        f.scrib(16, 48 if y < 26 else 34, y, INKG, 1.8, seed=y + 7, dens=0.95, tall=0)
    f.stamp(42, 29, r=4, lvl=2.6, seed=3)
    f.line(17, 31, 30, 30, INKB, 1.4)


def invitacio(f):
    """La invitació a la Gran Subhasta de l'Aigua: targeta daurada amb una sanefa de doble filet, «GRAN»,
    «SUBHASTA» i la gota blava amb «AIGUA», i la brillantor de l'or."""
    S = f.R(6, 4, 58, 31)
    f.drop(S, -1.6)
    f.fill(S, GOLDK, lambda x, y: 3.6 - (x - 6) * 0.02 - (y - 4) * 0.03, rim=(1.0, -1.6))
    for (x0, y0, x1, y1, l) in ((8, 6, 56, 29, 1.6), (10, 8, 54, 27, 2.2)):    # la sanefa
        f.rect(x0, y0, x1, y0, GOLDK, l)
        f.rect(x0, y1, x1, y1, GOLDK, l)
        f.rect(x0, y0, x0, y1, GOLDK, l)
        f.rect(x1, y0, x1, y1, GOLDK, l)
    for (x, y) in ((8, 6), (56, 6), (8, 29), (56, 29)):
        f.px(x, y, GOLDK, 5.4)
    ctext(f, 32, 10, 'GRAN', SEPIA, 0.4)
    ctext(f, 32, 16, 'SUBHASTA', SEPIA, 0.2)
    f.fill(f.P([(22, 21), (24, 21), (23, 22)]) | f.E(23, 24, 1.5, 1.5), AQUAB, 3.2, rim=None)   # la gota
    f.px(22, 23, AQUAB, 5.0)
    f.text(27, 22, 'AIGUA', AQUAB, 2.0)
    for i in range(8):                                                    # la brillantor, al cantó
        f.shade(50 + i, 27 - i * 2.4, 1.6)
        f.shade(51 + i, 27 - i * 2.4, 1.0)


def contracte_capitana(f):
    """El contracte de préstec de la Capitana: paper blanc trencat, molta lletra, i a baix la casella
    «ÀNIMA (opcional)» marcada amb una creu de bolígraf, i la signatura."""
    S = f.R(15, 1, 49, 34)
    paper(f, S, PAP_F, 4.4, w=35, h=34)
    f.fill(f.P([(18, 3), (21, 3), (19.5, 6)]) | {(19, 6), (20, 6)}, AQUAB, 3.2, rim=None)   # la gota de Verne
    f.rect(23, 4, 44, 4, INKG, 1.4)
    for y in range(8, 20, 2):
        f.scrib(18, 46, y, INKG, 2.2, seed=y + 20, dens=0.95, tall=0)
    f.rect(17, 22, 23, 28, INKG, 1.0)                                     # la casella
    f.rect(18, 23, 22, 27, PAP_F, 5.0)
    for i in range(5):                                                    # la creu
        f.px(18 + i, 23 + i, INKB, 0.6)
        f.px(22 - i, 23 + i, INKB, 0.6)
    f.text(26, 23, 'ANIMA', INKG, 0.4)
    f.px(27, 21, INKG, 0.4)                                               # l'accent de l'À
    f.line(25, 31, 46, 30, INKB, 1.4)                                     # la signatura
    f.line(28, 32, 31, 29, INKB, 1.4)


def nota_lia(f):
    """La nota de la Lia: un paperet petit arrencat d'una llibreta, mig doblegat, escrit a mà amb tinta blava
    i una fletxa dibuixada."""
    S = torn(f.P([(21, 7), (44, 5), (46, 29), (20, 31)]), 't', seed=9, depth=1)
    paper(f, S, PAP_C, 4.2, w=26, h=26)
    for x in range(20, 47):                                               # el plec
        f.shade(x, 18 + (x - 20) * -0.05, -0.8)
    for y in (11, 14, 22, 25):
        f.scrib(24, 41 if y != 25 else 34, y, INKB, 1.6, seed=y + 60, dens=0.85, tall=0.3)
    for i in range(6):                                                    # la fletxa
        f.px(35 + i, 27 - i * 0.4, INKB, 1.4)
    f.px(40, 24, INKB, 1.4)
    f.px(41, 26, INKB, 1.4)


# ─── Llavors, sorra, fosa ───────────────────────────────────────────────────

def _sac(f, cx, by, w, h, seed, tag=True, shade=0.0):
    """Un sac de tela lligat: la panxa, el coll lligat amb cordill, el floc de tela de dalt i l'etiqueta."""
    rx, top = w / 2, by - h
    S = f.P([(cx - rx * 0.62, top + 6), (cx + rx * 0.62, top + 6), (cx + rx, by - h * 0.45), (cx + rx * 0.9, by - 1),
             (cx + rx * 0.6, by), (cx - rx * 0.6, by), (cx - rx * 0.9, by - 1), (cx - rx, by - h * 0.45)])
    f.drop(S)
    f.fill(S, BURL, lambda x, y: 3.4 + shade - (x - cx) / rx * 0.9 - (y - top) * 0.02 - abs(x - cx) / rx * 0.5,
           rim=(0.6, -1.2))
    weave(f, S, BURL)
    T = f.P([(cx - 2.5, top + 4), (cx - 5, top), (cx, top + 2), (cx + 5, top - 0.5), (cx + 2.5, top + 4)])
    f.fill(T, BURL, 4.2 + shade, rim=(0.6, -1.0))                         # el floc
    f.rect(cx - 3, top + 4, cx + 3, top + 6, CLOTH, 3.6 + shade, rim=(0.6, -1.2))   # el lligall
    for i in range(3):                                                    # els plecs de la panxa
        x = cx - rx * 0.4 + i * rx * 0.4
        f.line(x, top + 8, x + (i - 1) * 2, top + 12, BURL, 2.4 + shade)
    if tag:
        f.line(cx + 3, top + 5, cx + rx * 0.5, top + 10, CLOTH, 3.0)
        S = f.R(cx + rx * 0.5 - 2, top + 10, cx + rx * 0.5 + 3, top + 14)
        f.fill(S, PAP_C, 4.4, rim=(0.4, -1.0))
        f.scrib(cx + rx * 0.5 - 1, cx + rx * 0.5 + 2, top + 12, GRAPH, 1.4, seed=seed, dens=0.9, tall=0)


def sacs_llavors(f):
    """Els tres sacs de llavors del pare, lligats junts amb una corda."""
    _sac(f, 32, 26, 20, 23, seed=1, tag=False, shade=-0.4)
    _sac(f, 16, 33, 20, 22, seed=2)
    _sac(f, 48, 33, 20, 22, seed=3)
    for x in range(6, 59):                                                # la corda que els lliga
        y = 24 + math.sin(x / 9) * 0.8
        f.px(x, round(y), CLOTH, 3.6 if x % 3 else 2.2)
        f.px(x, round(y) + 1, CLOTH, 2.0)


def sac_llavors(f):
    """Un sac de llavors, amb l'etiqueta escrita a mà."""
    _sac(f, 32, 34, 28, 31, seed=7)


def sorra(f):
    """Un saquet de sorra blanca d'Aqua, obert: la boca amb la sorra fins a dalt i un pilonet vessat."""
    S = f.P([(19, 10), (43, 10), (47, 22), (45, 33), (17, 33), (15, 22)])
    f.drop(S)
    f.fill(S, CLOTH, lambda x, y: 3.6 - (x - 31) * 0.05 - (y - 10) * 0.02, rim=(0.6, -1.2))
    weave(f, S, CLOTH, d=-0.35)
    f.fill(f.E(31, 10, 12.5, 3.2), CLOTH, 2.0, rim=None)                  # la boca, amb la vora girada
    f.fill(f.E(31, 9.5, 11, 2.6), SAND, lambda x, y: 4.2 - (x - 31) * 0.04 + (hr(x, y) - 0.5) * 0.8, rim=None)
    f.fill(f.E(30, 8, 6, 2), SAND, 4.8, rim=None)                         # el pilonet de dalt
    f.line(19, 13, 43, 13, CLOTH, 2.0)
    S = f.ell(52, 31, 9, 3.4, SAND, 3.6, amp=1.6)                         # la sorra vessada
    for (x, y) in S:
        if hr(x, y, 3) > 0.8:
            f.shade(x, y, 1.0)
    for (x, y) in ((61, 33), (58, 29), (44, 34)):
        f.px(x, y, SAND, 4.0)


def motlle(f):
    """El motlle de fosa d'en Bru: la caixa de ferro (el marc) plena de sorra de fosa, amb tres forats en forma
    de clau, el canal de colada i les dues guies; la cara de davant a l'ombra."""
    top = f.R(4, 4, 60, 25)
    front = f.R(4, 26, 60, 32)
    f.drop(top | front, -1.6)
    f.fill(front, IRON, lambda x, y: 2.6 - (y - 26) * 0.1, rim=(0.0, -1.0))
    f.fill(top, IRON, 4.6, rim=(0.8, -1.2))                               # el marc de ferro
    f.rect(4, 26, 60, 26, IRON, 5.4)
    sand = f.R(7, 7, 57, 22)
    f.fill(sand, MOULD, lambda x, y: 4.4 - (x - 7) * 0.01 + (hr(x, y, 2) - 0.5) * 0.7, rim=None)
    f.rect(7, 7, 57, 7, MOULD, 2.0)                                       # l'ombra del marc
    f.rect(7, 7, 7, 22, MOULD, 2.4)
    for y in (9, 15, 21):                                                 # les tres claus
        cav = f.E(14, y - 0.5, 3.6, 2.8) - f.E(14, y - 0.5, 1.2, 0.8)       # l'ull
        cav |= f.R(17, y - 1, 46, y)                                      # la tija
        cav |= f.R(39, y + 1, 41, y + 2) | f.R(44, y + 1, 46, y + 2)      # el paletó
        cav = {(x, yy) for (x, yy) in cav if 8 <= yy <= 22}
        for (x, yy) in cav:
            if (x, yy - 1) not in cav:
                f.px(x, yy, MOULD, 0.2)                                   # la paret de dalt, a l'ombra
            elif (x, yy + 1) not in cav:
                f.px(x, yy, MOULD, 2.6)                                   # la de baix, a la llum
            else:
                f.px(x, yy, MOULD, 1.0)
    f.fill(f.E(53, 14, 2.2, 5.5), MOULD, 1.0, rim=None)                   # el canal de colada
    for x in range(51, 56):
        f.px(x, 9, MOULD, 0.2)
    for (cx, cy) in ((10, 20), (53, 4.5)):                                # les guies
        f.px(cx, cy, DARK, 0.6)
    for (x, y) in ((5, 5), (59, 5), (5, 24), (59, 24)):                   # els cargols del marc
        f.px(x, y, IRON, 6.6)


def claus(f):
    """Les tres claus de les vàlvules: ferro fos, grosses i aspres, penjades d'una anella."""
    f.ring(10, 12, 6, 6, ACER, 4.4, th=1.8)                               # l'anella
    keys = (((17, 9), (56, 6), 4.0), ((17, 15), (57, 17), 3.4), ((15, 21), (52, 30), 2.8))
    for (bx, by), (ex, ey), lv in keys:
        f.ring(bx + 3, by, 3.4, 3.2, IRON, lv + 0.4, th=2.0)              # l'ull
        f.limb((bx + 6, by), (ex, ey), 1.6, 1.6, IRON, lv, amp=2.2)       # la tija
        dx, dy = ex - bx - 6, ey - by
        L = math.hypot(dx, dy)
        nx, ny = -dy / L, dx / L                                          # el paletó, cap avall
        for t in (0.82, 0.92):
            for d in range(2, 6):
                f.px(bx + 6 + dx * t + nx * d * (1 if ny > 0 else -1), by + dy * t + abs(ny) * d, IRON, lv - 0.6)
        for i in range(6):                                                # la rugositat del ferro fos
            t = hr(bx, i, 3)
            f.shade(bx + 6 + dx * t, by + dy * t, -0.8)
    f.px(6, 9, ACER, 6.4)


def corretja(f):
    """La corretja de goma: una anella negra plana, amb les estries de dins i la marca blanca impresa."""
    cx, cy, rx, ry = 32, 18, 27, 14
    outer = f.E(cx, cy, rx, ry)
    inner = f.E(cx, cy + 1.5, rx - 5.5, ry - 5)
    S = outer - inner
    f.drop(S)
    f.fill(S, RUB, lambda x, y: 4.0 - (y - (cy - ry)) / (2 * ry) * 2.0, rim=(1.4, -1.2))
    for (x, y) in S:                                                      # les estries
        r = math.hypot((x - cx) / rx, (y - cy) / ry)
        if 0.86 < r < 0.9:
            f.shade(x, y, -1.2)
        if r > 0.96 and y < cy:
            f.shade(x, y, 1.0)
    for (x, y) in inner:                                                  # la cara de dins, a l'ombra
        if (x, y - 1) in S and y > cy:
            f.px(x, y, RUB, 1.6)
    f.text(26, 28, 'A-38', CARD, 4.4)


def filtre(f):
    """El filtre de cafetera de tela: la mitja de cotó tacada de cafè, l'anella de filferro i el mànec retorçat."""
    for i in range(30):                                                   # el mànec
        x = 34 + i * 0.85
        y = 9 - i * 0.18
        f.px(x, round(y), ACER, 4.6 if i % 2 else 2.8)
        f.px(x, round(y) + 1, ACER, 2.4 if i % 2 else 3.6)
    S = f.P([(10, 10), (34, 10), (30, 22), (25, 31), (21, 33), (17, 31), (13, 22)])   # la mitja
    f.drop(S)
    f.fill(S, CLOTH, lambda x, y: 4.0 - (x - 10) * 0.06 - (y - 10) * 0.02, rim=(0.6, -1.2))
    for (x, y) in S:                                                      # les taques de cafè
        if y > 18 and hr(x // 2, y // 2, 4) > 0.5 - (y - 18) * 0.03:
            f.px(x, y, SEPIA, 2.6 - (y - 18) * 0.06)
    for i in range(3):                                                    # els plecs
        f.line(15 + i * 6, 12, 18 + i * 2, 28, CLOTH, 2.6)
    f.ring(22, 10, 12.5, 3.2, ACER, 4.4, th=1.4)                          # l'anella
    for x in range(12, 33, 3):
        f.px(x, 13, ACER, 5.4)


def _rotllo(f, goters=False):
    """El rotllo de tub negre de reg gota a gota: quatre voltes que es tapen (cadascuna amb la seva llum a dalt i
    l'ombra de la del davant) i el cap que penja."""
    for k in range(4):
        cx, cy = 23 + k * 3.4, 14 + k * 1.8
        pix = {}
        for i in range(160):
            a = 2 * math.pi * i / 160
            for dr in (-0.9, -0.1, 0.7):
                x, y = round(cx + (18 + dr) * math.cos(a)), round(cy + (11 + dr * 0.8) * math.sin(a))
                pix[(x, y)] = (a, dr)
        for (x, y), (a, dr) in pix.items():
            lit = -math.sin(a) * 0.9 - math.cos(a) * 0.4                 # llum de dalt a l'esquerra
            f.px(x, y, RUB, 2.9 + lit * 1.0 - abs(dr) * 0.6 + (1.4 if dr < -0.5 and lit > 0.3 else 0))
    f.limb((47, 27), (56, 31), 1.5, 1.5, RUB, 3.0, amp=1.6)               # el cap
    f.limb((56, 31), (60, 28), 1.5, 1.5, RUB, 3.4, amp=1.6)
    f.fill(f.E(60.5, 27.5, 1.2, 1.2), DARK, 0.4, rim=None)
    if goters:
        for a in (200, 235, 270, 305, 340, 25, 60, 110, 150):            # els goters, verds
            x = 33.2 + 18 * math.cos(math.radians(a))
            y = 19.4 + 11 * math.sin(math.radians(a))
            f.fill(f.E(x, y, 1.3, 1.3), LIME, 4.0, rim=(0.6, -1.0))
        f.fill(f.E(61, 33, 0.9, 1.3), WATER, 3.0, rim=None)               # una gota
        f.px(61, 32, WATER, 3.8)


def reg(f):
    """El rotllo de tub negre de reg gota a gota."""
    _rotllo(f)


def reg_foradat(f):
    """El rotllo de tub de reg, ara amb els goters clavats."""
    _rotllo(f, goters=True)


def agulla(f):
    """L'agulla de cosir grossa amb el fil vermell enfilat, que fa una volta i cau."""
    f.limb((10, 32), (52, 6), 0.9, 1.2, ACER, 5.0, amp=2.0)               # l'agulla
    f.px(10, 32, ACER, 3.0)
    f.px(49, 8, DARK, 0.6)                                                # l'ull
    f.px(50, 7, DARK, 0.6)
    pts = [(50, 7), (55, 4), (59, 9), (56, 17), (48, 22), (44, 30), (49, 34), (56, 31)]
    for (a, b) in zip(pts, pts[1:]):                                      # el fil
        n = int(max(abs(b[0] - a[0]), abs(b[1] - a[1]))) * 2 + 1
        for i in range(n):
            t = i / n
            f.px(a[0] + (b[0] - a[0]) * t, a[1] + (b[1] - a[1]) * t, GRIP, 3.6 if a[1] < b[1] else 3.0)
    f.px(50, 6, ACER, 7.0)


def _galleda(f, plena=False):
    """La galleda de zinc: el cos de con, els dos cèrcols, la vora enrotllada, les orelles i la nansa de
    filferro; buida (l'interior fosc) o plena (l'aigua amb el reflex)."""
    cx = 32

    def r(y):
        return 15 - (y - 10) * 4 / 22
    for i in range(41):                                                   # la nansa
        a = math.pi * (1 + i / 40)
        f.px(cx + 16 * math.cos(a), 11 + 10 * math.sin(a), ACER, 4.0 if i < 20 else 3.0)
    S = f.lathe(10, 32, lambda y: (cx - r(y), cx + r(y)), ZINC, 4.2, amp=2.4)
    f.shine(S, 0.8, 1.2)
    for y in (16, 26):                                                    # els cèrcols
        f.rect(cx - r(y), y, cx + r(y), y, ZINC, 6.0)
        f.rect(cx - r(y), y + 1, cx + r(y), y + 1, ZINC, 2.4)
    for (x, y) in S:                                                      # el zinc, tacat
        if hr(x // 2, y // 2, 6) > 0.86:
            f.shade(x, y, -0.8)
    f.fill(f.E(cx, 33, 11, 1.2), ZINC, 2.0, rim=None)
    f.fill(f.E(cx, 10, 15, 3.6), ZINC, 5.0, rim=None)                     # la vora
    if plena:
        f.fill(f.E(cx, 10.4, 13.6, 2.6), WATER, lambda x, y: 2.0 + (x - cx) * 0.03, rim=None)
        for x in range(cx - 8, cx - 1):
            f.px(x, 10, WATER, 3.8)
        f.px(cx + 4, 11, WATER, 3.6)
        f.fill(f.E(cx + 9, 6, 0.9, 1.2), WATER, 3.0, rim=None)            # una esquitxada
    else:
        f.fill(f.E(cx, 10.4, 13.6, 2.6), ZINC, lambda x, y: 0.8 + (y - 8) * 0.4, rim=None)
    for x in (cx - 15, cx + 15):                                          # les orelles
        f.fill(f.E(x, 12, 1.4, 1.6), ZINC, 4.6, rim=(0.4, -1.0))


def galleda(f):
    """La galleda de zinc, buida."""
    _galleda(f)


def galleda_plena(f):
    """La galleda de zinc, plena d'aigua."""
    _galleda(f, plena=True)


# ─── El palau ───────────────────────────────────────────────────────────────

def pernil(f):
    """Una llesca de pernil: carn vermella amb el marbrejat, la cansalada blanca a la vora de dalt, un plec i la
    brillantor."""
    S = f.E(24, 20, 19, 11) | f.E(42, 16, 18, 10) | f.E(34, 22, 16, 9)
    f.drop(S, -1.6)
    f.fill(S, HAM, lambda x, y: 3.0 - (y - 6) * 0.03 + math.sin((x + y * 0.5) / 6) * 0.5, rim=(0.6, -1.4))
    for (x, y) in S:                                                      # la cansalada
        if (x, y - 3) not in S and y < 22:
            f.px(x, y, FAT, 3.6 if (x, y - 1) not in S else (2.8 if (x, y - 2) not in S else 2.0))
    for k in range(3):                                                    # el marbrejat
        for i in range(14):
            x = 18 + k * 12 + i
            y = 15 + k * 3 + math.sin(i / 2.2 + k) * 1.5
            if hr(x, k, 5) > 0.25:
                f.px(x, y, FAT, 1.6)
    for x in range(14, 50):                                               # el plec
        f.shade(x, 25 + math.sin(x / 7) * 1.5, -0.8)
    for i in range(6):                                                    # la brillantor
        f.shade(14 + i * 2, 22 - i, 1.4)


def _vestit(f, agulla=False):
    """El vestit de vellut granat, plegat: les espatlles, les solapes amb la camisa blanca i el corbatí, els
    botons daurats i la butxaca; a sobre, la corona feta d'un engranatge daurat. Si és arreglat, una agulla de cap
    clavada a la solapa i una costura nova de fil daurat."""
    S = f.P([(5, 18), (13, 13), (49, 13), (58, 18), (58, 34), (5, 34)])    # la jaqueta plegada
    f.drop(S, -1.6)
    f.fill(S, VELV, lambda x, y: 3.6 - (y - 13) * 0.05 + (hr(x, y, 9) - 0.5) * 0.8, rim=(0.8, -1.4))
    f.fill(f.P([(25, 13), (37, 13), (31, 24)]), PAP_W, 4.4, rim=(0.0, -1.0))   # la camisa
    f.fill(f.R(29, 15, 33, 17) - {(31, 15), (31, 17)}, BLK, 2.0, rim=None)     # el corbatí
    for side in (-1, 1):                                                  # les solapes
        L = f.P([(31 + side * 6, 13), (31 + side * 9, 13), (31 + side * 6, 21), (31, 26), (31 + side * 1, 24)])
        f.fill(L, VELV, 4.6 if side < 0 else 3.4, rim=(0.6, -1.0))
    for y in (28, 32):                                                    # els botons
        f.fill(f.E(31, y, 1.1, 1.1), GOLDK, 4.4, rim=None)
        f.px(30, y - 1, GOLDK, 5.6)
    f.rect(11, 25, 20, 25, VELV, 1.4)                                     # la butxaca
    f.rect(13, 23, 16, 24, GOLDK, 4.2)                                    # el mocador
    # la corona d'engranatge
    band = f.R(41, 8, 59, 13)
    for k in range(5):
        x = 42 + k * 4
        band |= f.R(x, 4, x + 1, 7)
    f.drop(band, -1.6)
    f.fill(band, GOLDK, lambda x, y: 4.4 - (y - 4) * 0.12 - (x - 41) * 0.03, rim=(0.8, -1.4))
    for k in range(5):
        f.px(42 + k * 4, 4, GOLDK, 6.0)
    f.fill(f.E(50, 10.5, 1.8, 1.6), AQUAB, 3.4, rim=None)                 # la pedra blava
    f.px(49, 10, AQUAB, 5.4)
    for x in range(42, 59, 3):
        f.px(x, 12, GOLDK, 2.2)
    if agulla:
        for i in range(9):                                                # la costura nova
            if i % 2 == 0:
                f.px(41 + i * 1.6, 30, GOLDK, 4.6)
        f.line(21, 16, 27, 22, ACER, 5.6)                                 # l'agulla de cap
        f.fill(f.E(20, 15, 2.0, 2.0), PEARL, 3.4, rim=(0.6, -1.0))
        f.px(19, 14, PEARL, 4.8)


def vestit(f):
    """El vestit de vellut granat, plegat, amb la corona d'engranatge."""
    _vestit(f)


def vestit_arreglat(f):
    """El vestit de vellut arreglat: una agulla de cap i una costura nova."""
    _vestit(f, agulla=True)


def targeta(f):
    """La targeta d'accés del palau: plàstic blanc, xip daurat, l'emblema del palau (un anell orbital daurat),
    la franja daurada de baix i la ranura per penjar-la."""
    S = f.R(9, 6, 55, 30) - {(9, 6), (55, 6), (9, 30), (55, 30)}
    f.drop(S, -1.6)
    f.fill(S, CARD, lambda x, y: 4.6 - (x - 9) * 0.015 - (y - 6) * 0.02, rim=(0.6, -1.4))
    f.rect(12, 9, 16, 9, CARD, 1.6)                                       # la ranura
    S = f.R(14, 14, 21, 20)                                               # el xip
    f.fill(S, GOLDK, 4.0, rim=(0.6, -1.0))
    for (x0, y0, x1, y1) in ((14, 17, 21, 17), (17, 14, 17, 20)):
        f.rect(x0, y0, x1, y1, GOLDK, 2.4)
    f.ring(45, 13, 6, 2.2, GOLDK, 3.6, th=1.0)                            # l'emblema
    f.fill(f.E(45, 13, 2, 2), GOLDK, 4.6, rim=(0.6, -1.0))
    f.rect(26, 15, 38, 15, INKG, 2.6)
    f.rect(26, 18, 34, 18, INKG, 3.0)
    f.rect(10, 25, 54, 27, GOLDK, lambda x, y: 4.2 - (y - 25) * 0.5)      # la franja
    for i in range(6):                                                    # la brillantor del plàstic
        f.shade(48 + i, 29 - i * 3, 0.8)


ICONS = {fn.__name__: fn for fn in (
    comunicador, mosca, punta_flor, tornavis, tornavis_flor, escriptura, contracte_7788, sacs_llavors, sac_llavors,
    albara, oli, clau_anglesa, injector, fusible, paper_plata, fusible_apanyat, carta_juana, sorra, motlle, claus,
    corretja, filtre, reg, agulla, reg_foradat, galleda, galleda_plena, carta_banc, invitacio, contracte_capitana,
    pernil, vestit, vestit_arreglat, targeta, nota_lia,
)}


def render(item_id):
    """Imatge RGBA de 65×36 de l'objecte, o None si no en té."""
    fn = ICONS.get(item_id)
    if fn is None:
        return None
    f = Ic640()
    fn(f)
    return f.render()
