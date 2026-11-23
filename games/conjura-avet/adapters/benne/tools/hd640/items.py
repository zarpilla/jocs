"""
Icones d'inventari de La Conjura de l'Avet a 640×360: 65×36 (la casella de l'inventari del HUD, hd640/hud.py),
dibuixades píxel a píxel amb el sistema de hd/items.py (Ic: volum amb llum de dalt a l'esquerra, rampes per material
i el contorn fosc, `CONTORN_FOSC`, que les retalla sobre la casella).

Els objectes es veuen damunt les caselles de fusta fosca del HUD: cada icona ha de tenir prou contrast i una silueta
clara. Paleta del monestir medieval: cuir, fusta, ferro, terrissa, llana, pergamí, resina d'avet (ambre) i el verd
fosc de l'avet. L'únic **vermell viu** és la cera dels segells (el tros de cera i el salconduit segellat): que l'ull
el trobi sempre. La tinta és de ferro i gal·les (marró negrós), no blava.

No toca hd/items.py: en reaprofita els materials i les eines i només canvia la mida del llenç.
Ho fan servir draw_items.py / draw_placeholders.py (inventari del joc) i hd640/draw_items.py (full i làmina).
"""
import math

from hd.characters import Fig
from hd.pix import hr
from hd.items import Ic, M, WOOD, PALE, IRON, ACER, BRASS

W, H = 65, 36

# ─── Materials (fosc → clar) ────────────────────────────────────────────────
TAN = M((30, 16, 10), (60, 34, 20), (98, 60, 34), (138, 92, 54), (176, 126, 80), (208, 164, 112), (232, 198, 150))   # cuir dels guants
TERRA = M((34, 14, 10), (70, 30, 18), (110, 52, 30), (150, 78, 44), (186, 108, 64), (214, 142, 92), (236, 180, 132))  # terrissa
VIDRAT = M((14, 22, 12), (30, 44, 22), (52, 70, 34), (80, 98, 46), (112, 128, 62), (150, 162, 92), (196, 204, 140))  # terrissa vidrada, verd d'oli
RESINA = M((36, 14, 4), (84, 36, 6), (142, 72, 10), (198, 116, 18), (236, 166, 46), (254, 212, 104), (255, 242, 196))
CERA = M((40, 4, 8), (92, 8, 14), (150, 16, 20), (204, 30, 28), (238, 60, 44), (255, 116, 92), (255, 186, 164))   # l'únic vermell viu
CANEM = M((40, 30, 16), (78, 62, 36), (120, 100, 62), (162, 140, 92), (198, 178, 126), (228, 212, 166))
SAC = M((30, 22, 12), (60, 46, 26), (96, 76, 46), (132, 108, 68), (166, 140, 94), (196, 172, 126))
BOIX = M((50, 36, 14), (98, 76, 30), (150, 120, 52), (196, 166, 80), (226, 202, 116), (246, 232, 164))
NOU = M((22, 14, 8), (46, 30, 16), (76, 52, 28), (110, 80, 44), (146, 112, 66), (182, 148, 98))
LLANA_B = M((70, 64, 60), (120, 114, 104), (166, 160, 146), (204, 198, 182), (230, 226, 212), (246, 244, 234), (255, 255, 250))
LLANA_N = M((6, 6, 8), (14, 13, 16), (26, 24, 28), (40, 37, 42), (58, 54, 60), (80, 76, 82), (108, 104, 108))
AVET = M((6, 20, 14), (12, 36, 24), (20, 56, 36), (32, 80, 50), (50, 108, 66), (80, 140, 90), (124, 176, 122))
FULLA = M((10, 28, 10), (22, 52, 18), (38, 82, 28), (62, 116, 42), (96, 152, 64), (146, 192, 106))
TERRA_N = M((14, 10, 8), (32, 22, 16), (54, 38, 26), (78, 56, 38), (104, 78, 54))   # terra de l'arrel
MEL = M((60, 28, 4), (116, 64, 8), (178, 112, 16), (222, 160, 36), (246, 204, 84), (255, 236, 160), (255, 250, 220))
CARBO = M((4, 4, 6), (12, 12, 14), (24, 23, 26), (38, 37, 42), (58, 56, 62), (86, 84, 92), (120, 118, 128))
PLOM = M((18, 20, 26), (36, 40, 48), (58, 64, 74), (84, 90, 100), (112, 118, 128), (144, 150, 158), (182, 188, 194))
PERG = M((52, 36, 22), (104, 80, 52), (156, 128, 88), (198, 172, 126), (226, 206, 162), (244, 232, 196), (255, 250, 228))
TINTA = M((16, 10, 8), (36, 24, 18), (58, 40, 28), (86, 62, 44))                    # ferro i gal·les
PEDRA = M((26, 24, 22), (50, 46, 42), (78, 72, 66), (108, 100, 92), (140, 132, 120), (172, 164, 150), (204, 198, 184))
CAPAR = M((6, 30, 34), (14, 62, 70), (30, 104, 110), (60, 150, 150), (120, 200, 190), (200, 240, 230))   # vidriol verd-blau
MENTA = M((6, 30, 14), (14, 60, 28), (30, 100, 50), (60, 150, 80), (110, 196, 120), (190, 236, 190))
VIDRE = M((24, 34, 30), (52, 70, 62), (88, 112, 100), (130, 156, 142), (180, 204, 190), (232, 246, 236))
ARREL = M((40, 28, 18), (80, 60, 40), (124, 100, 70), (168, 144, 106), (206, 186, 148), (232, 220, 190))
FLOR = M((90, 60, 76), (150, 112, 130), (204, 170, 186), (236, 214, 224), (252, 244, 248))
CERA_T = M((14, 16, 8), (28, 32, 14), (44, 50, 22), (64, 70, 32), (88, 94, 46), (116, 120, 64))   # la cera fosca de la tauleta
PLOMA = M((60, 58, 56), (116, 112, 106), (168, 164, 154), (206, 202, 190), (232, 230, 220), (248, 248, 242), (255, 255, 255))


class Ic640(Ic):
    """Llenç d'una icona de 640: el mateix Ic, a 65×36."""

    def __init__(self):
        Fig.__init__(self, W, H)


def sparkle(f, x, y, mat, lvl, r=2):
    """Una espurna en creu (el que brilla)."""
    f.px(x, y, mat, lvl + 1.0)
    for d in range(1, r + 1):
        for dx, dy in ((d, 0), (-d, 0), (0, d), (0, -d)):
            f.px(x + dx, y + dy, mat, lvl - d * 0.6)


def lletra(f, x0, x1, y0, y1, mat=TINTA, lvl=1.4, seed=0, pas=3, dens=0.82):
    """Ratlles d'escriptura a mà (lletra gòtica, menuda), de y0 a y1 cada `pas` píxels."""
    for k, y in enumerate(range(y0, y1 + 1, pas)):
        f.scrib(x0 + (1 if k == 0 else 0), x1 - int(hr(seed, k) * 4), y, mat, lvl, seed=seed + k * 7, dens=dens, tall=0.3)


def segell(f, cx, cy, r=5.5, base=3.6, mat=CERA):
    """Un segell de cera: el disc gruixut, la vora aixafada irregular, l'empremta (anella i creu) i el reflex."""
    pts = []
    for i in range(14):
        a = i / 14 * math.tau
        rr = r + (hr(int(cx), i, 3) - 0.5) * 1.6
        pts.append((cx + math.cos(a) * rr, cy + math.sin(a) * rr * 0.92))
    S = Ic.P(pts)
    f.drop(S, -1.6)
    f.ell(cx, cy, r + 0.6, (r + 0.6) * 0.92, mat, base, amp=1.8, cont=(0.2, 1.0),
          clip=lambda x, y: (x, y) in S)
    f.ring(cx, cy, r * 0.62, r * 0.58, mat, base - 1.4)
    for d in range(-2, 3):
        f.px(cx + d, cy, mat, base - 1.2)
        f.px(cx, cy + d, mat, base - 1.2)
    f.px(cx + 1, cy + 1, mat, base + 1.0)
    f.px(cx - r * 0.5, cy - r * 0.55, mat, base + 2.6)
    f.px(cx - r * 0.5 + 1, cy - r * 0.55, mat, base + 1.6)


def gota_resina(f, cx, cy, rx=4.0, ry=3.4):
    """Una gota de resina d'ambre, brillant."""
    pix = f.ell(cx, cy, rx, ry, RESINA, 3.6, amp=2.2, cont=(0.2, 1.0))
    for (x, y) in pix:
        if (x - cx + rx * 0.4) ** 2 + (y - cy + ry * 0.4) ** 2 < 1.6:
            f.shade(x, y, 2.0)
    return pix


# ─── El bosc i la feina de l'Iri ───────────────────────────────────────────

def _guant(f, ox, oy, lvl, flip=False):
    """Un guant de llenyatera, de palmell: el puny ample, el palmell i quatre dits gruixuts i el polze."""
    s = -1 if flip else 1
    P = lambda x, y: (ox + x * s, oy + y)                                  # noqa: E731
    f.limb(P(0, 22), P(0, 13), 7.0, 6.2, TAN, lvl - 0.4, amp=1.8, cont=(0.2, 0.9))   # el puny
    f.ell(*P(1, 8), 6.4, 6.2, TAN, lvl, amp=1.8, cont=(0.2, 0.9))           # el palmell
    for i, (dx, ln) in enumerate(((-4.2, 7), (-1.4, 8), (1.4, 8), (4.0, 6.5))):
        f.limb(P(dx, 5), P(dx * 1.15, 5 - ln), 1.5, 1.4, TAN, lvl + 0.2 - i * 0.1, amp=1.6, cont=(0.2, 0.8))
    f.limb(P(6, 9), P(10, 4), 1.7, 1.5, TAN, lvl - 0.2, amp=1.6, cont=(0.2, 0.8))   # el polze
    for x in range(-6, 7):                                                  # la costura del puny
        if x % 2 == 0:
            f.px(*P(x, 15), TAN, lvl - 1.8)
    f.px(*P(-3, 18), TAN, lvl + 1.4)


def guants(f):
    """Els guants de llenyatera: dos guants de cuir gruixut, l'un damunt de l'altre."""
    _guant(f, 40, 10, 3.0, flip=True)
    _guant(f, 25, 9, 3.6)


def destral(f):
    """La destral de l'Iri: el mànec de freixe en diagonal i el cap de ferro amb el tall esmolat que brilla."""
    f.limb((14, 33), (44, 5), 1.9, 1.6, PALE, 3.2, amp=1.8, cont=(0.2, 0.8))
    for t in (0.25, 0.5, 0.75):                                             # la veta del mànec
        f.shade(14 + 30 * t, 33 - 28 * t, -0.8)
    S = Ic.P([(38, 4), (46, 1), (48, 4), (57, 2), (60, 9), (58, 17), (51, 14), (46, 12), (40, 11)])
    f.drop(S, -1.6)
    f.fill(S, IRON, lambda x, y: 3.6 - (y - 1) * 0.08 + (x - 38) * 0.04, rim=(0.8, -1.4))
    for y in range(3, 17):                                                  # el tall, esmolat
        for x in range(54, 61):
            if (x, y) in S and (x + 2, y) not in S:
                f.px(x, y, ACER, 7.0 - abs(y - 9) * 0.25)
    f.limb((44, 5), (46, 2), 1.4, 1.4, PALE, 3.8, amp=1.0)                  # el cap del mànec, que treu
    sparkle(f, 58, 5, ACER, 7.2)


def olla(f):
    """L'olla del dinar: terrissa panxuda, la vora vidrada, dues nanses i una tapa de fusta."""
    def edges(y):
        t = (y - 8) / 25
        if t < 0 or t > 1:
            return None
        w = 11 + 8 * math.sin(math.pi * (0.25 + 0.7 * t))
        return (32 - w, 32 + w)
    S = set()
    pix = f.lathe(8, 33, edges, TERRA, 3.4, amp=2.2, cont=(0.2, 1.0))
    S.update(pix)
    f.drop(S, -1.4)
    for y in range(9, 32):                                                  # les marques del torn
        if y % 4 == 0:
            for x in range(14, 51):
                f.shade(x, y, -0.5, only=TERRA)
    f.ell(32, 8, 13.0, 2.6, VIDRAT, 3.4, amp=1.6, cont=(0.2, 0.8))         # la vora vidrada
    f.ell(32, 6.4, 11.0, 2.2, WOOD, 4.0, amp=1.4, cont=(0.2, 0.8))         # la tapa
    f.limb((32, 5), (32, 3), 1.6, 1.4, WOOD, 4.4, amp=1.2)
    for sx in (-1, 1):                                                      # les nanses
        cx = 32 + sx * 20
        for a in range(0, 181, 15):
            r = math.radians(a)
            f.px(cx + sx * math.sin(r) * 3.4, 12 + math.cos(r) * -3.6 + 3.6, TERRA, 3.6 if sx < 0 else 2.6)
            f.px(cx + sx * math.sin(r) * 2.4, 12 + math.cos(r) * -2.6 + 3.6, TERRA, 2.4 if sx < 0 else 1.6)


def _pot_fusta(f, cx=30, top=12, bot=33, rx=10):
    """Un potet de fusta de doelles amb dos cercles de ferro."""
    pix = f.lathe(top, bot, lambda y: (cx - rx, cx + rx), WOOD, 3.6, amp=2.0, cont=(0.2, 1.0))
    f.drop(set(pix), -1.4)
    for x in range(cx - rx + 3, cx + rx, 4):                               # les doelles
        for y in range(top + 1, bot):
            f.shade(x, y, -1.0, only=WOOD)
    for y in (top + 4, bot - 4):                                            # els cercles
        f.hcyl(cx - rx, cx + rx, y, 0.9, IRON, 3.4, amp=1.4)
    return pix


def pot_resina(f):
    """El pot de resina: un potet de fusta ple de resina d'ambre que vessa per la vora i regalima, amb el bastó."""
    _pot_fusta(f)
    f.limb((36, 12), (50, 1), 1.2, 1.0, PALE, 3.4, amp=1.4, cont=(0.2, 0.8))   # el bastó
    f.ell(30, 12, 10.6, 3.2, RESINA, 3.4, amp=2.2, cont=(0.2, 0.9))         # la resina, plena
    for (x, y0, n) in ((22, 13, 7), (27, 14, 4), (37, 13, 10)):             # els regalims
        f.limb((x, y0), (x, y0 + n), 1.3, 1.0, RESINA, 4.0, amp=1.8)
        f.ell(x, y0 + n + 0.6, 1.5, 1.5, RESINA, 4.2, amp=1.8)
    f.limb((36, 12), (39, 9), 1.4, 1.2, RESINA, 4.4, amp=1.6)              # la resina enganxada al bastó
    sparkle(f, 26, 10, RESINA, 5.4)


def pegot(f):
    """Un pegot de resina embolicat en una fulla (de castanyer, dentada): la fulla oberta i la bola d'ambre."""
    a = math.radians(-12)
    for i in range(34):                                                     # la fulla, dentada
        t = i / 33
        w = 9.0 * math.sin(math.pi * t) ** 0.8
        for s in range(-int(w), int(w) + 1):
            dent = (i % 3 == 0 and abs(s) == int(w))
            x = 15 + math.cos(a) * t * 36 - math.sin(a) * s
            y = 20 + math.sin(a) * t * 36 + math.cos(a) * s
            f.px(x, y, FULLA, (2.6 if s > 0 else 3.4) + (0.8 if dent else 0) - (1.2 if s == 0 else 0)
                 - (0.9 if (i % 5 == 0 and s != 0 and abs(s) < w - 1) else 0))
    f.limb((15, 20), (9, 21), 0.7, 0.7, FULLA, 2.0)                         # el pecíol
    gota_resina(f, 31, 16, 8.0, 6.4)                                        # la bola de resina
    f.ell(37, 20, 2.6, 2.0, RESINA, 3.2, amp=1.6)
    sparkle(f, 27, 12, RESINA, 5.6)


def cera(f):
    """Un tros de cera vermella: un segell trencat per la meitat (l'empremta partida), amb les esquerdes i les
    engrunes. El vermell viu de la cera: el que l'ull ha de trobar."""
    cx, cy, r = 30, 18, 12
    S = {(x, y) for (x, y) in Ic.E(cx, cy, r, r * 0.9)
         if y - cy < 3 + (x - cx) * 0.35 + (1.4 if (x // 2) % 2 else 0)}   # el trencament, en ziga-zaga
    f.drop(S, -1.8, 1, 2)
    pix = f.ell(cx, cy, r, r * 0.9, CERA, 3.6, amp=2.0, cont=(0.2, 1.0), clip=lambda x, y: (x, y) in S)
    for (x, y) in S:                                                        # el gruix, al tall
        if (x, y + 1) not in S:
            f.px(x, y + 1, CERA, 1.4)
            f.px(x, y + 2, CERA, 1.0)
    f.ring(cx, cy, r * 0.66, r * 0.6, CERA, 2.4)                            # l'empremta: l'anella
    for k in range(-5, 6):                                                  # i una creu amb el llaç
        if (cx + k, cy - 2) in S:
            f.px(cx + k, cy - 2, CERA, 2.2)
    for k in range(-7, 3):
        if (cx, cy + k) in S:
            f.px(cx, cy + k, CERA, 2.2)
    f.ring(cx, cy - 6, 2.0, 1.6, CERA, 2.4)
    f.line(cx - 6, cy - 8, cx - 3, cy + 1, CERA, 2.0)                       # una esquerda
    f.ell(48, 27, 2.4, 1.8, CERA, 3.4, amp=1.6, cont=(0.2, 1.0))            # les engrunes
    f.ell(53, 24, 1.6, 1.3, CERA, 3.2, amp=1.4, cont=(0.2, 1.0))
    for (x, y) in pix:
        if (x - cx + 6) ** 2 + (y - cy + 6) ** 2 < 5:
            f.shade(x, y, 1.6)
    sparkle(f, 23, 11, CERA, 5.6)


def canem(f):
    """Un cabdell de fil de cànem: la bola amb les voltes del fil creuades i el cap que penja."""
    cx, cy, r = 30, 18, 13
    pix = f.ell(cx, cy, r, r * 0.95, CANEM, 3.4, amp=2.2, cont=(0.2, 1.0))
    for k, ang in enumerate((-35, 25, 80)):                                 # les voltes, en tres direccions
        a = math.radians(ang)
        for off in range(-11, 12, 3):
            for t in range(-14, 15):
                x = cx + math.cos(a) * t - math.sin(a) * off
                y = cy + math.sin(a) * t + math.cos(a) * off
                if (round(x), round(y)) in pix and (t + off + k) % 2 == 0:
                    f.shade(x, y, -0.9 if k != 1 else 0.6)
    pts = [(42, 24), (47, 28), (52, 30), (56, 27), (59, 30), (61, 33)]      # el cap del fil
    for (a, b) in zip(pts, pts[1:]):
        f.line(a[0], a[1], b[0], b[1], CANEM, 3.8)
    for (x, y) in pix:
        if (x - cx + 5) ** 2 + (y - cy + 6) ** 2 < 8:
            f.shade(x, y, 0.8)


def salabre(f):
    """El salabre d'en Joanet: un cèrcol de vímet amb la xarxa que fa bossa i el mànec llarg."""
    f.limb((4, 33), (30, 16), 1.6, 1.4, PALE, 3.4, amp=1.6, cont=(0.2, 0.8))   # el mànec
    cx, cy, rx, ry = 44, 13, 15, 8
    for y in range(int(cy), 35):                                            # la bossa de xarxa, a sota
        w = rx * math.sqrt(max(0.0, 1 - ((y - cy) / 21) ** 2))
        for x in range(int(cx - w), int(cx + w) + 1):
            if (x + y) % 4 == 0 or (x - y) % 4 == 0:
                f.px(x, y, CANEM, 3.2 - (y - cy) * 0.06)
    for y in range(int(cy - ry), int(cy + ry) + 1):                         # la boca, a través del cèrcol
        for x in range(cx - rx, cx + rx + 1):
            if ((x - cx) / rx) ** 2 + ((y - cy) / ry) ** 2 < 0.8 and ((x + y) % 4 == 0 or (x - y) % 4 == 0):
                f.px(x, y, CANEM, 2.2)
    for a in range(0, 360, 3):                                              # el cèrcol
        r = math.radians(a)
        x, y = cx + math.cos(r) * rx, cy + math.sin(r) * ry
        lvl = 3.6 - math.cos(r) * 0.6 - math.sin(r) * 0.8
        f.px(x, y, WOOD, lvl + 1.0)
        f.px(x, y + 1, WOOD, lvl)
    f.limb((28, 17), (31, 15), 1.8, 1.8, CANEM, 3.4, amp=1.2)               # el lligall


def serra(f):
    """La serra del pare: la fulla d'acer amb les dents, el mànec de boix amb tres osques i, embolicada al mànec,
    una tira de pergamí amb una creu i un llaç."""
    S = Ic.P([(24, 9), (61, 12), (61, 18), (24, 22)])                       # la fulla
    f.drop(S, -1.4)
    f.fill(S, ACER, lambda x, y: 4.6 - (y - 9) * 0.12 + (x - 24) * 0.02, rim=(0.8, -1.2))
    for x in range(25, 61, 2):                                              # les dents
        yb = 22 - (x - 24) * 4 / 37
        f.px(x, yb + 1, ACER, 3.0)
    f.px(58, 14, ACER, 1.6)                                                 # el forat de la punta
    f.limb((5, 18), (25, 15), 4.8, 4.2, BOIX, 3.6, amp=2.0, cont=(0.2, 0.9))  # el mànec
    for x in (9, 12, 15):                                                   # les tres osques
        f.line(x, 12, x + 1, 15, BOIX, 1.2)
    T = Ic.P([(16, 11), (22, 10), (23, 21), (17, 22)])                      # la tira de pergamí, embolicada
    f.fill(T, PERG, lambda x, y: 4.6 - (x - 16) * 0.12, rim=(0.6, -1.2))
    f.line(19, 13, 19, 19, TINTA, 1.0)                                      # la creu
    f.line(17, 15, 21, 15, TINTA, 1.0)
    f.ring(19.5, 18.5, 1.6, 1.4, TINTA, 1.2)                                # el llaç
    f.limb((26, 15), (26, 16), 2.6, 2.6, IRON, 3.6, amp=1.2)                # el rebló
    sparkle(f, 40, 12, ACER, 7.0)


def clofolles(f):
    """El sac de nous: un sac de canemàs lligat de dalt i, vessades davant, nous amb clofolla verda i negra."""
    S = Ic.P([(14, 33), (12, 22), (16, 12), (22, 8), (32, 8), (36, 12), (40, 22), (38, 33)])
    f.drop(S, -1.4)
    f.fill(S, SAC, lambda x, y: 3.6 - (x - 12) * 0.05 + (0.5 if (x + y * 2) % 4 == 0 else 0), rim=(0.6, -1.2))
    f.limb((20, 9), (34, 9), 1.4, 1.4, CANEM, 3.0, amp=1.2)                 # el lligall
    for (x, y) in ((18, 4), (22, 2), (26, 3), (30, 2), (34, 4)):            # la boca, arrugada
        f.limb((x, y), (27, 8), 1.4, 1.0, SAC, 3.4, amp=1.4)
    for (cx, cy, r, verd) in ((44, 28, 5.0, False), (53, 26, 4.6, True), (48, 20, 4.4, False), (58, 31, 4.0, False),
                              (38, 31, 4.2, True)):
        mat = FULLA if verd else NOU
        pix = f.ell(cx, cy, r, r * 0.92, mat, 3.2 if verd else 3.6, amp=2.0, cont=(0.2, 1.0))
        if not verd:
            for (x, y) in pix:                                              # les arrugues de la closca
                if (x * 3 + y * 5) % 6 == 0:
                    f.shade(x, y, -1.0)
            f.line(cx, cy - r + 1, cx, cy + r - 1, NOU, 1.6)
        else:
            f.px(cx - 1, cy - 2, FULLA, 4.8)
            for (x, y) in pix:                                              # les taques negres de tint
                if hr(x, y, 4) > 0.82:
                    f.px(x, y, NOU, 1.0)


def _habit(f, mat, lvl, cx=32, top=3, bot=33, curt=False, caputxa=True):
    """Un hàbit (o una túnica) estès: la caputxa, les mànigues amples obertes en creu, el cos que s'eixampla
    cap avall, el cordó a la cintura i els plecs. Amb `curt`, el baix tallat a tisora i cosit amb cànem."""
    sh = top + 6                                                            # les espatlles
    S = Ic.P([(cx - 6, sh - 1), (cx - 12, sh), (cx - 21, sh + 9), (cx - 24, sh + 16), (cx - 17, sh + 18),
              (cx - 12, sh + 10), (cx - 14, bot), (cx + 14, bot), (cx + 12, sh + 10), (cx + 17, sh + 18),
              (cx + 24, sh + 16), (cx + 21, sh + 9), (cx + 12, sh), (cx + 6, sh - 1)])
    f.drop(S, -1.6, 1, 2)
    f.fill(S, mat, lambda x, y: lvl - (x - cx) * 0.025 - (y - top) * 0.025, rim=(0.6, -1.4))
    for sx in (-1, 1):                                                      # el sotabraç i la boca de la mànega
        f.line(cx + sx * 12, sh + 10, cx + sx * 12, sh + 4, mat, lvl - 1.6)
        f.line(cx + sx * 17, sh + 17, cx + sx * 23, sh + 15, mat, lvl - 2.2)
    for (x0, x1) in ((cx - 7, cx - 10), (cx - 2, cx - 3), (cx + 4, cx + 5), (cx + 8, cx + 11)):   # els plecs
        f.line(x0, sh + 13, x1, bot - 1, mat, lvl - 1.4)
        f.line(x0 + 1, sh + 13, x1 + 1, bot - 1, mat, lvl + 0.6)
    f.rect(cx - 12, sh + 11, cx + 12, sh + 12, CANEM if mat is LLANA_N else LLANA_N, 3.4)   # el cordó
    f.limb((cx + 4, sh + 12), (cx + 5, sh + 19), 0.7, 0.7, CANEM if mat is LLANA_N else LLANA_N, 3.0, amp=0.6)
    if caputxa:                                                             # la caputxa, tirada enrere
        f.ell(cx, sh - 0.4, 6.0, 3.0, mat, lvl - 0.4, amp=1.6, cont=(0.2, 0.9))
        f.ell(cx, sh - 0.2, 3.4, 1.6, mat, lvl - 3.0, amp=0.6)
    if curt:                                                                # la vora tallada i el fil que la cus
        for x in range(cx - 14, cx + 15):
            if x % 3 == 0:
                f.px(x, bot - 2, CANEM, 4.0)
            if x % 2:
                f.px(x, bot + 1, mat, lvl - 1.0)


def tuniques(f):
    """Dues túniques de novici: llana blanca, gegants (no caben al quadre), l'una damunt de l'altra."""
    _habit(f, LLANA_B, 3.4, cx=37, top=0, bot=35)
    _habit(f, LLANA_B, 4.4, cx=28, top=1, bot=35)


def habits(f):
    """Dos hàbits negres de monjo, que encara fumegen (dues voleies de fum que s'enfilen) i fan un pam de més."""
    _habit(f, LLANA_N, 3.6, cx=36, top=1, bot=35)
    _habit(f, LLANA_N, 4.6, cx=27, top=2, bot=35)
    for k, x0 in enumerate((48, 55)):                                       # el fum
        for i in range(12):
            y = 13 - i * 1.0
            x = x0 + math.sin(i * 0.8 + k) * 2.2
            if y >= 0:
                f.px(x, y, PEDRA, 5.2 - i * 0.18)
                if i % 2 == 0:
                    f.px(x + 1, y, PEDRA, 4.6 - i * 0.2)
    for (x, y) in ((18, 31), (19, 32), (33, 33)):                           # els socarrims
        f.px(x, y, CARBO, 0.6)


def habits_curts(f):
    """Els hàbits escurçats a la mida: més baixos, amb la vora tallada a tisora i un fil de cànem que la cus."""
    _habit(f, LLANA_N, 3.6, cx=37, top=4, bot=29, curt=True)
    _habit(f, LLANA_N, 4.6, cx=27, top=6, bot=31, curt=True)


def tisores(f):
    """Les tisores de bugadera: tisores de molla, d'una peça de ferro (dues fulles que s'uneixen en un llaç)."""
    for (a, b, r, lvl) in (((10, 24), (24, 22), 1.6, 3.4), ((10, 12), (24, 15), 1.6, 3.8)):
        f.limb(a, b, r, r, IRON, lvl, amp=1.6, cont=(0.2, 0.8))             # els braços
    for a in range(-90, 91, 6):                                             # el llaç de la molla, a l'esquerra
        r = math.radians(a)
        f.limb((10 - math.cos(r) * 6, 18 + math.sin(r) * 6), (10 - math.cos(r) * 6, 18 + math.sin(r) * 6),
               1.5, 1.5, IRON, 3.6 - math.sin(r) * 0.6, amp=1.0)
    for (pts, lvl) in (([(23, 13), (60, 17), (58, 19), (23, 18)], 5.2), ([(23, 19), (58, 19), (60, 21), (23, 25)], 4.0)):
        S = Ic.P(pts)
        f.drop(S, -1.4)
        f.fill(S, ACER, lambda x, y, l=lvl: l - (x - 23) * 0.03, rim=(0.8, -1.2))
    f.line(24, 19, 58, 19, ACER, 1.4)                                       # el tall entre les fulles
    sparkle(f, 44, 15, ACER, 7.0)


def alzina(f):
    """La llenya d'alzina: quatre troncs partits, lligats amb un vencill. Fusta densa, l'escorça clivellada i la
    testa amb els anells."""
    for (cy, x0, x1, ox) in ((26, 8, 50, 0), (19, 12, 54, 2), (25, 18, 58, 4), (14, 14, 52, -1)):
        pix = f.hcyl(x0, x1, cy, 4.4, WOOD, 3.0, amp=2.2)
        for (x, y) in pix:                                                  # l'escorça clivellada
            if hr(x // 3, y, 9) > 0.7:
                f.shade(x, y, -1.0)
        f.ell(x1, cy, 2.2, 4.6, PALE, 3.8, amp=1.4, cont=(0.2, 0.8))       # la testa
        f.ring(x1, cy, 1.1, 2.6, PALE, 2.6)
        f.px(x1, cy, PALE, 2.2)
    for x in (24, 40):                                                      # el vencill
        for y in range(9, 32):
            f.px(x + (y % 3 == 0), y, FULLA, 2.4 + (0.8 if y % 2 else 0))


def retalls(f):
    """Retalls de llana negra, dels hàbits escurçats: tres tires de vores crues, una damunt l'altra."""
    for k, (pts, lvl) in enumerate((([(8, 22), (36, 18), (38, 26), (10, 30)], 3.8),
                                    ([(26, 8), (56, 12), (54, 21), (24, 17)], 4.4),
                                    ([(20, 20), (50, 22), (52, 31), (18, 29)], 5.0))):
        S = Ic.P(pts)
        S = {(x, y) for (x, y) in S if hr(x, y, k) > 0.08}                  # la vora crua, deshilada
        f.drop(S, -1.6, 1, 2)
        f.fill(S, LLANA_N, lambda x, y, l=lvl: l + (0.6 if (x + y) % 3 == 0 else 0), rim=(0.6, -1.4))
    for (x, y) in ((53, 31), (55, 30), (57, 32), (16, 33)):                 # els fils solts
        f.px(x, y, LLANA_N, 3.6)


# ─── Els pots d'apotecari ───────────────────────────────────────────────────

def _albarello(f, cx=30, top=7, bot=33, rx=11):
    """Un pot d'apotecari (albarello): cos de terrissa vidrada, la cintura estreta, una faixa de terrissa nua amb
    unes ratlles i el coll curt."""
    def edges(y):
        if y < top + 3:
            return (cx - rx + 3, cx + rx - 3)                               # el coll
        t = (y - top - 3) / (bot - top - 3)
        w = rx - 2.0 * math.sin(math.pi * t)
        return (cx - w, cx + w)
    pix = f.lathe(top, bot, edges, VIDRAT, 3.4, amp=2.4, cont=(0.2, 1.0))
    f.drop(set(pix), -1.4)
    for (x, y) in pix:                                                      # la faixa, al mig
        if top + 12 <= y <= top + 17:
            l = f.buf[y][x][1]
            f.px(x, y, TERRA, l + 1.2)
    for x in range(cx - rx + 2, cx + rx - 1, 3):                            # el dibuix de la faixa
        f.px(x, top + 14, TINTA, 1.6)
        f.px(x + 1, top + 15, TINTA, 1.6)
    f.ell(cx, top + 3, rx - 1.0, 2.2, VIDRAT, 3.6, amp=1.4)                 # l'espatlla
    return pix


def _tap(f, cx=30, y=5, rx=8):
    """El tap: un disc de suro/cuir lligat amb cordill."""
    f.ell(cx, y + 1, rx, 3.0, TAN, 3.4, amp=1.6, cont=(0.2, 0.9))
    f.rect(cx - rx, y + 3, cx + rx, y + 3, CANEM, 3.6)
    f.px(cx + rx + 1, y + 4, CANEM, 3.2); f.px(cx + rx + 1, y + 5, CANEM, 3.0)


def pot_apotecari(f):
    """El pot d'apotecari de la Gueraula, buit, amb el tap."""
    _albarello(f)
    _tap(f)


def pot_cartes(f):
    """El pot amb les cartes a dins: el tap aixecat i dos rotllets de pergamí (un de clar, un d'enfosquit amb carbó)
    que treuen el cap."""
    _albarello(f)
    f.ell(30, 9.5, 8, 2.0, NOU, 0.8, amp=0.4)                               # la boca, fosca
    f.limb((27, 10), (25, 1), 2.2, 2.0, PERG, 4.0, amp=1.6, cont=(0.2, 0.8))
    f.ell(25, 1.2, 2.0, 1.0, PERG, 2.4, amp=0.6)
    f.limb((32, 10), (35, 2), 2.0, 1.8, CARBO, 4.2, amp=1.6, cont=(0.2, 0.8))
    f.ell(35, 2.2, 1.8, 0.9, CARBO, 5.0, amp=0.6)
    f.ell(50, 26, 7.0, 2.6, TAN, 3.4, amp=1.6, cont=(0.2, 0.9))             # el tap, a terra
    f.ell(50, 25, 6.0, 1.8, TAN, 4.0, amp=1.2)


def pot_segellat(f):
    """El pot segellat: el tap cobert de resina d'ambre que regalima pel coll."""
    _albarello(f)
    _tap(f)
    f.ell(30, 6, 9.0, 3.6, RESINA, 3.6, amp=2.2, cont=(0.2, 1.0))
    for (x, n) in ((22, 5), (27, 3), (34, 6), (38, 4)):
        f.limb((x, 8), (x, 8 + n), 1.2, 1.0, RESINA, 4.0, amp=1.6)
    sparkle(f, 26, 4, RESINA, 5.6)


# ─── El plançó, la pala, el cofre ───────────────────────────────────────────

def planco(f):
    """El plançó d'avet: un avet petit com un braç, amb el pa de terra de l'arrel embolicat amb arpillera."""
    f.ell(32, 29, 9, 5.6, SAC, 3.4, amp=2.0, cont=(0.2, 1.0))               # el pa de terra
    f.ell(32, 25, 8, 1.8, TERRA_N, 2.6, amp=1.0)
    f.limb((32, 26), (32, 1), 1.2, 0.6, NOU, 3.0, amp=1.2)                  # el tronquet
    for k in range(6):                                                      # els pisos de branques
        y = 22 - k * 4
        w = 13 - k * 2
        for s in (-1, 1):
            for i in range(w):
                x = 32 + s * i
                yy = y + i * 0.35
                f.px(x, yy, AVET, 3.8 - i * 0.08 + (0.6 if s < 0 else -0.3))
                f.px(x, yy - 1, AVET, 4.4 - i * 0.08 + (0.6 if s < 0 else -0.3))
                if i % 2 == 0:
                    f.px(x, yy + 1, AVET, 2.4)
    f.px(32, 0, AVET, 5.6)
    f.limb((28, 27), (36, 27), 0.8, 0.8, CANEM, 3.6, amp=0.8)               # el cordill


def pala(f):
    """La pala d'en Sunifred: mànec net com una ploma, la fulla de fusta amb la vora de ferro."""
    f.limb((6, 32), (34, 12), 1.6, 1.6, PALE, 4.0, amp=1.8, cont=(0.2, 0.8))
    f.limb((4, 33), (9, 30), 2.4, 2.4, PALE, 3.8, amp=1.6, cont=(0.2, 0.8))   # el puny
    ux, uy = 28 / math.hypot(28, 20), -20 / math.hypot(28, 20)             # la direcció del mànec
    nx, ny = -uy, ux
    pt = lambda u, v: (33 + ux * u + nx * v, 13 + uy * u + ny * v)          # noqa: E731  (u: al llarg; v: de través)
    S = Ic.P([pt(0, -4), pt(4, -8), pt(22, -8), pt(25, -6), pt(25, 6), pt(22, 8), pt(4, 8), pt(0, 4)])
    f.drop(S, -1.6)
    f.fill(S, WOOD, lambda x, y: 4.2 - (y - 2) * 0.05 + (x - 33) * 0.01, rim=(0.8, -1.4))
    for v in range(-8, 9):                                                  # la vora de ferro, a la punta
        for u in (23, 24, 25):
            f.px(*pt(u, v), IRON, 5.0 - (u - 23) * 0.6)
    f.line(*pt(3, 0), *pt(20, 0), WOOD, 3.0)                                 # el nervi del mig
    sparkle(f, *pt(24, -5), ACER, 6.6)


def cofre(f):
    """El cofre de plom de l'Emma: una capseta grisa-blavosa amb la tapa, les vores rebatudes i la balda."""
    S = Ic.R(14, 13, 50, 32)
    f.drop(S, -1.6, 1, 2)
    f.fill(S, PLOM, lambda x, y: 3.6 - (x - 14) * 0.02 - (y - 13) * 0.02, rim=(0.8, -1.4))
    T = Ic.P([(13, 13), (18, 5), (46, 5), (51, 13)])                        # la tapa, en escorç
    f.fill(T, PLOM, lambda x, y: 4.8 - (y - 5) * 0.08, rim=(0.8, -1.0))
    f.rect(13, 13, 51, 14, PLOM, 2.4)
    for x in (17, 47):                                                      # els cantoners
        f.rect(x - 2, 15, x, 31, PLOM, 4.6)
    f.rect(29, 11, 35, 20, PLOM, 5.2, rim=(0.6, -1.2))                      # la balda
    f.ell(32, 17, 1.4, 1.6, CARBO, 1.0, amp=0.4)
    for (x, y) in ((22, 22), (40, 26), (26, 28)):                           # els cops al plom
        f.shade(x, y, -1.0); f.shade(x + 1, y, 0.8)
    f.scrib(22, 42, 24, PLOM, 2.2, seed=5, dens=0.6)                        # una inscripció, gastada


# ─── Les coses de la Vet (escrivana) ────────────────────────────────────────

def tauleta(f):
    """La tauleta de cera: un marc de fusta amb la cera fosca, ratllada amb lletres, i l'estilet al costat."""
    S = Ic.R(10, 5, 46, 32)
    f.drop(S, -1.6, 2, 1)
    f.fill(S, WOOD, lambda x, y: 4.2 - (x - 10) * 0.02 - (y - 5) * 0.02, rim=(0.8, -1.4))
    f.rect(14, 9, 42, 28, CERA_T, lambda x, y: 3.0 - (x - 14) * 0.02, rim=(-1.4, 0.8))   # la cera, enfonsada
    for k, y in enumerate(range(12, 27, 3)):                                # les lletres gravades (clares)
        f.scrib(16, 40 - int(hr(k, 2) * 6), y, CERA_T, 5.0, seed=k * 3, dens=0.8, tall=0.25)
    for y in (12, 25):                                                      # els forats del cordó
        f.px(11, y, CARBO, 1.0)
    f.limb((52, 32), (58, 4), 1.2, 0.8, BRASS, 4.0, amp=1.6, cont=(0.2, 0.8))   # l'estilet
    f.limb((57, 6), (58.5, 2), 2.0, 1.6, BRASS, 4.4, amp=1.4)               # la paleta d'esborrar


def carbonet(f):
    """Un carbonet de salze: un bastonet negre, amb l'escorça a trossos i la punta gastada, i la pols al voltant."""
    pix = f.limb((10, 26), (52, 10), 3.0, 2.6, CARBO, 4.2, amp=2.2, cont=(0.2, 0.9))
    for (x, y) in pix:                                                      # l'escorça, encara
        if hr(x // 2, y, 5) > 0.75:
            f.shade(x, y, 1.2)
    for k in range(4):
        x = 52 + k
        f.line(x, 10 - 2.4 + k * 0.6, x, 10 + 2.4 - k * 0.6, CARBO, 3.8 - k * 0.3)
    f.ell(52, 10, 1.6, 2.6, CARBO, 5.4, amp=1.2)                            # la testa
    for (x, y) in ((44, 22), (48, 25), (39, 27), (55, 21), (51, 28)):       # la pols
        f.px(x, y, CARBO, 4.4)


def pergamins(f):
    """Pergamins en blanc: una pila de retalls, cadascun d'un to i un tall, i el de dalt amb el cantó doblegat."""
    for k, (pts, lvl) in enumerate((([(12, 14), (44, 10), (48, 30), (14, 33)], 3.2),
                                    ([(18, 8), (50, 7), (52, 27), (19, 29)], 3.8),
                                    ([(14, 5), (44, 3), (46, 25), (15, 26)], 4.6))):
        S = Ic.P(pts)
        f.drop(S, -1.6, 1, 2)
        f.fill(S, PERG, lambda x, y, l=lvl: l - (x - 14) * 0.015 - (y - 3) * 0.015, rim=(0.6, -1.2))
    C = Ic.P([(38, 26), (46, 25), (45, 18)])                                # el cantó doblegat
    f.fill(C, PERG, 3.0, rim=(0.6, -1.0))
    for (x, y) in ((20, 10), (33, 15), (25, 20), (40, 9)):                  # les taques de la pell
        f.shade(x, y, -0.7); f.shade(x + 1, y, -0.5)


def ploma(f):
    """Una ploma d'oca, ben tallada: les barbes blanques, el canó i la punta tacada de tinta."""
    a0, b0 = (8, 33), (58, 3)
    f.limb(a0, b0, 0.7, 0.9, PLOMA, 4.6, amp=1.2)                           # el canó
    L = math.hypot(b0[0] - a0[0], b0[1] - a0[1])
    ux, uy = (b0[0] - a0[0]) / L, (b0[1] - a0[1]) / L
    nx, ny = -uy, ux
    for i in range(int(L)):
        t = i / L
        if t < 0.28:
            continue
        w = 6.0 * math.sin(math.pi * (t - 0.28) / 0.72) ** 0.7
        for s in range(-int(w * 0.7), int(w) + 1):
            x = a0[0] + ux * i + nx * s - ux * abs(s) * 0.6
            y = a0[1] + uy * i + ny * s - uy * abs(s) * 0.6
            lvl = (4.8 if s < 0 else 3.6) - abs(s) * 0.15 - (1.0 if (i + s) % 5 == 0 and s != 0 else 0)
            f.px(x, y, PLOMA, lvl)
    for k in range(4):                                                      # la punta, tallada i tacada
        f.px(a0[0] - 1 + k * ux, a0[1] - k * 0.5, TINTA, 1.6)
    f.limb((9, 32), (12, 30), 0.8, 0.6, TINTA, 2.0, amp=0.6)


def rascador(f):
    """El rascador d'escrivana: un ganivet de fulla curta i corba, amb el mànec d'os."""
    f.limb((8, 26), (28, 18), 2.8, 2.4, PLOMA, 3.6, amp=1.8, cont=(0.2, 0.9))   # el mànec d'os
    for x in (13, 18, 23):
        f.shade(x, 24 - (x - 8) * 0.4, -1.0)
    f.limb((28, 18), (31, 17), 3.0, 3.0, BRASS, 3.8, amp=1.4)               # la virolla
    S = set()
    for i in range(28):                                                     # la fulla, en mitja lluna
        t = i / 27
        x = 31 + t * 26
        yc = 17 - t * 8 - math.sin(t * math.pi) * 2
        w = 4.0 * (1 - t) ** 0.6 + 0.6
        for s in range(-int(w), 1):
            S.add((round(x), round(yc + s - 0.4 * math.sin(t * math.pi) * 3)))
            S.add((round(x), round(yc + s + 1)))
    f.drop(S, -1.4)
    f.fill(S, ACER, lambda x, y: 5.0 - (x - 31) * 0.03, rim=(0.8, -1.4))
    sparkle(f, 47, 10, ACER, 7.0)


def mocador(f):
    """Un mocador blanc de lli, plegat en triangle, amb una vora de fil i una punta que voleia."""
    S = Ic.P([(8, 8), (56, 6), (34, 32)])
    f.drop(S, -1.6, 1, 2)
    f.fill(S, LLANA_B, lambda x, y: 5.0 - (y - 6) * 0.04 - (x - 8) * 0.01, rim=(0.6, -1.4))
    f.line(15, 10, 33, 29, LLANA_B, 3.6)                                    # el plec
    f.line(16, 10, 34, 29, LLANA_B, 5.4)
    for x in range(10, 55, 2):                                              # la vora de fil, a dalt
        f.px(x, 7 + (x - 8) * -2 / 48 + 1, CANEM, 3.6)
    T = Ic.P([(48, 7), (60, 4), (58, 12)])                                  # la punta
    f.fill(T, LLANA_B, 3.8, rim=(0.6, -1.0))


def cardo(f):
    """Un cap de cardó sec: la pinya ovalada plena de ganxos, la corona de bràctees i la tija."""
    f.limb((32, 34), (32, 22), 1.2, 1.4, ARREL, 3.0, amp=1.2)               # la tija
    for s in (-1, 1):                                                       # les bràctees, sota el cap
        for k in range(3):
            f.limb((32, 23), (32 + s * (10 + k * 2), 26 - k * 5), 0.9, 0.4, ARREL, 3.4 - k * 0.3, amp=0.8)
    pix = f.ell(32, 13, 8, 11, ARREL, 3.4, amp=2.2, cont=(0.2, 1.0))         # el cap
    for (x, y) in pix:                                                      # els ganxos, en espiral
        if (x * 2 + y * 3) % 5 == 0:
            f.shade(x, y, -1.4)
        elif (x * 2 + y * 3) % 5 == 2:
            f.shade(x, y, 0.8)
    for a in range(0, 360, 30):                                             # les punxes de la vora
        r = math.radians(a)
        f.px(32 + math.cos(r) * 9.2, 13 + math.sin(r) * 12.0, ARREL, 3.6)


def llana(f):
    """Llana negra cardada: un floc esponjós, fet de boletes que s'esfilagarsen."""
    for (cx, cy, r) in ((22, 20, 8), (34, 16, 9), (45, 20, 8), (30, 26, 7), (40, 26, 6.5), (16, 25, 5)):
        pix = f.ell(cx, cy, r, r * 0.85, LLANA_N, 4.6, amp=2.4, cont=(0.2, 0.9))
        for (x, y) in pix:
            if hr(x, y, 2) > 0.7:
                f.shade(x, y, 0.9)
    for (x, y, dx) in ((12, 22, -3), (52, 18, 4), (36, 6, 1), (50, 28, 4)):  # els fils que s'escapen
        for i in range(4):
            f.px(x + dx * i / 3, y - (i % 2), LLANA_N, 3.6)


def _barba(f, cx, cy, lvl):
    """Una barba postissa: la forma de U amb el forat de la boca i els rínxols."""
    pts = []
    for i in range(21):
        a = math.radians(180 + i * 9)
        pts.append((cx + math.cos(a) * 9, cy - 4 - math.sin(a) * 12))
    S = Ic.P([(cx - 9, cy - 6)] + pts[::-1] + [(cx + 9, cy - 6)])
    S |= Ic.R(cx - 9, cy - 7, cx + 9, cy - 4)
    S -= Ic.E(cx, cy - 4, 3.6, 2.0)                                         # la boca
    f.drop(S, -1.6, 1, 2)
    f.fill(S, LLANA_N, lambda x, y: lvl + (0.9 if hr(x, y, 6) > 0.72 else 0) - (y - cy) * 0.04, rim=(0.6, -1.4))
    for (x, y) in S:                                                        # els rínxols
        if (x + y * 2) % 7 == 0:
            f.shade(x, y, -1.0)
    for x in (cx - 10, cx + 10):                                            # la resina del revers, a les puntes
        f.ell(x, cy - 6, 1.4, 1.2, RESINA, 4.0, amp=1.4)


def barbes(f):
    """Dues barbes postisses de llana negra, amb resina al revers."""
    _barba(f, 44, 21, 3.4)
    _barba(f, 22, 22, 4.0)


def mel(f):
    """La gerra de mel del monestir: terrissa amb vidrat de mel, el broc i la mel que hi regalima."""
    def edges(y):
        if y < 8:
            return (25, 39)
        t = (y - 8) / 25
        w = 9 + 6 * math.sin(math.pi * (0.2 + 0.75 * t))
        return (32 - w, 32 + w)
    pix = f.lathe(4, 33, edges, TERRA, 3.4, amp=2.2, cont=(0.2, 1.0))
    f.drop(set(pix), -1.4)
    f.ell(32, 4.4, 7.4, 1.8, NOU, 0.8, amp=0.4)                             # la boca
    f.ell(32, 4.2, 6.0, 1.0, MEL, 3.6, amp=0.8)                             # la mel, a dins
    for (x, y0, n) in ((27, 5, 9), (34, 5, 5), (37, 6, 12)):                # els regalims
        f.limb((x, y0), (x, y0 + n), 1.2, 1.0, MEL, 4.2, amp=1.8)
        f.ell(x, y0 + n + 0.6, 1.5, 1.5, MEL, 4.4, amp=1.8)
    for a in range(-80, 81, 10):                                            # la nansa
        r = math.radians(a)
        f.px(47 + math.cos(r) * 4, 17 + math.sin(r) * 7, TERRA, 3.4)
        f.px(47 + math.cos(r) * 3, 17 + math.sin(r) * 6, TERRA, 2.4)
    f.limb((22, 6), (19, 3), 1.6, 1.0, TERRA, 3.8, amp=1.2)                 # el broc
    sparkle(f, 36, 14, MEL, 5.4)


def carbo(f):
    """Un grapat de carbó de la llar: trossos negres, de cares planes que brillen una mica."""
    for k, (cx, cy, r) in enumerate(((24, 24, 7), (38, 25, 8), (31, 15, 7), (46, 17, 5.5), (17, 30, 4.5),
                                     (49, 29, 4.2))):
        pts = []
        for i in range(6):
            a = i / 6 * math.tau + hr(k, i) * 0.6
            rr = r * (0.75 + hr(k, i, 3) * 0.4)
            pts.append((cx + math.cos(a) * rr, cy + math.sin(a) * rr * 0.8))
        S = Ic.P(pts)
        f.drop(S, -1.6, 1, 2)
        f.fill(S, CARBO, lambda x, y, cx=cx, cy=cy: 3.8 + (1.6 if (x - cx) + (y - cy) * 1.4 < -1 else 0)
               - (0.8 if (x - cx) > 2 else 0), rim=(1.2, -1.0))


def unguent(f):
    """L'ungüent de celles: un potet de terrissa obert, ple d'una pasta negra lluent (mel i carbó)."""
    def edges(y):
        return (20, 44) if y > 14 else (19, 45)
    pix = f.lathe(12, 32, edges, TERRA, 3.6, amp=2.2, cont=(0.2, 1.0))
    f.drop(set(pix), -1.4)
    f.ell(32, 13, 13, 3.4, TERRA, 4.4, amp=1.4, cont=(0.2, 0.9))           # la vora
    f.ell(32, 13, 11, 2.6, CARBO, 3.0, amp=1.6)                              # la pasta
    f.ell(30, 10, 7, 3.4, CARBO, 3.4, amp=2.2, cont=(0.2, 0.9))             # el pilot, remenat
    f.px(27, 8, CARBO, 6.2); f.px(28, 8, CARBO, 5.4); f.px(33, 9, CARBO, 5.0)
    f.px(42, 12, MEL, 4.0); f.px(41, 13, MEL, 3.2)                          # un fil de mel
    f.limb((44, 12), (56, 2), 1.0, 0.8, PALE, 3.6, amp=1.2, cont=(0.2, 0.8))   # l'espàtula
    f.ell(44, 12.4, 1.8, 1.2, CARBO, 3.2, amp=1.0)


def valeriana(f):
    """Arrel de valeriana: un manoll d'arrels clares i fibroses, amb la terra, lligat, i les fulles tallades."""
    f.ell(18, 18, 6, 5, TERRA_N, 3.0, amp=1.6, cont=(0.2, 0.9))             # la soca, amb terra
    for k in range(9):                                                      # les arrels, que s'escampen
        a = math.radians(-26 + k * 6.5)
        n = 30 + hr(k, 4) * 12
        pts = [(20 + math.cos(a) * t + math.sin(t * 0.4 + k) * 1.2, 18 + math.sin(a) * t) for t in range(0, int(n))]
        for i, (x, y) in enumerate(pts):
            f.px(x, y, ARREL, 4.0 - i * 0.04 - (k % 3) * 0.4)
    f.limb((22, 16), (22, 21), 1.6, 1.6, CANEM, 3.6, amp=1.0)               # el lligall
    for (a, b) in (((14, 15), (6, 4)), ((16, 14), (12, 2)), ((13, 17), (3, 12))):   # les fulles tallades
        f.limb(a, b, 1.0, 1.6, FULLA, 3.2, amp=1.4)
    for (x, y) in ((6, 3), (12, 1), (4, 11)):                               # una flor, encara
        f.ell(x, y, 1.6, 1.4, FLOR, 3.4, amp=1.0)


def caparros(f):
    """El caparrós: un potet de pedra amb el cristall verd-blau del vidriol, que fa negra la tinta."""
    def edges(y):
        t = (y - 14) / 19
        w = 12 - 2 * t
        return (32 - w, 32 + w)
    pix = f.lathe(14, 33, edges, PEDRA, 3.6, amp=2.2, cont=(0.2, 1.0))
    f.drop(set(pix), -1.4)
    for (x, y) in pix:                                                      # el gra de la pedra
        if hr(x, y, 8) > 0.82:
            f.shade(x, y, -0.8)
    f.ell(32, 14, 12.4, 3.2, PEDRA, 4.4, amp=1.4, cont=(0.2, 0.9))          # la vora
    f.ell(32, 14, 10.4, 2.4, PEDRA, 1.4, amp=0.6)
    for k, (cx, cy, r) in enumerate(((27, 11, 4.0), (34, 9, 5.0), (39, 12, 3.4), (31, 6, 3.2))):   # els cristalls
        pts = [(cx, cy - r * 1.2), (cx + r, cy - r * 0.2), (cx + r * 0.6, cy + r * 0.9), (cx - r * 0.7, cy + r * 0.9),
               (cx - r, cy - r * 0.1)]
        S = Ic.P(pts)
        f.fill(S, CAPAR, lambda x, y, cx=cx: 3.4 + (1.4 if x < cx else -0.4), rim=(1.0, -1.2))
    sparkle(f, 32, 5, CAPAR, 5.0)


# ─── El salconduit (tres estats) ────────────────────────────────────────────

def _salconduit(f):
    """El salconduit: un pergamí escrit, amb la plica (el plec de baix) i el lloc del segell a la dreta."""
    S = Ic.P([(6, 5), (56, 3), (57, 31), (7, 33)])
    f.drop(S, -1.6, 1, 2)
    f.fill(S, PERG, lambda x, y: 4.6 - (x - 6) * 0.015 - (y - 3) * 0.02, rim=(0.6, -1.4))
    f.rect(8, 26, 55, 26, PERG, 2.8)                                        # la plica
    f.rect(8, 27, 55, 27, PERG, 5.0)
    f.text(10, 6, 'E', TINTA, 1.2, font={'E': ('###.', '#...', '###.', '#...', '####')})   # la caplletra
    lletra(f, 15, 52, 7, 12, seed=3, dens=0.7)
    lletra(f, 10, 52, 15, 18, seed=9, dens=0.7)
    lletra(f, 10, 38, 21, 23, seed=13, dens=0.7)
    f.limb((47, 28), (48, 34), 0.8, 0.8, CANEM, 3.4, amp=0.6)               # el cordill del segell


def salconduit_brut(f):
    """El salconduit sense segell: on hi va el segell, només el cordill i la marca buida."""
    _salconduit(f)
    f.ring(46, 20, 4.4, 4.0, PERG, 2.6)


def salconduit_resina(f):
    """El salconduit amb una gota de resina on hi va el segell."""
    _salconduit(f)
    gota_resina(f, 46, 20, 4.4, 3.8)
    f.limb((46, 23), (46, 26), 1.0, 0.8, RESINA, 3.8, amp=1.4)
    sparkle(f, 44, 18, RESINA, 5.6, r=1)


def salconduit(f):
    """El salconduit segellat amb la cera vermella de l'Emma (el vermell viu)."""
    _salconduit(f)
    segell(f, 46, 21, 6.0)


# ─── El xarop, les claus, les cartes ────────────────────────────────────────

def xarop(f):
    """El xarop de menta: una ampolleta de vidre verdós amb el xarop verd, el tap de suro i una fulla de menta."""
    def edges(y):
        if y < 10:
            return (28, 36)
        t = (y - 10) / 23
        w = 4 + 8 * min(1.0, t * 2.2)
        return (32 - w, 32 + w)
    pix = f.lathe(5, 33, edges, VIDRE, 3.4, amp=2.0, cont=(0.2, 1.0))
    f.drop(set(pix), -1.4)
    for (x, y) in pix:                                                      # el xarop, fins a mitja panxa
        if y > 17:
            f.px(x, y, MENTA, f.buf[y][x][1])
    for y in range(12, 31):                                                 # el reflex del vidre
        f.px(24 if y > 16 else 29, y, VIDRE, 5.4)
    f.limb((32, 5), (32, 1), 3.0, 2.6, TAN, 3.8, amp=1.4, cont=(0.2, 0.8))  # el tap
    a = math.radians(-20)                                                   # la fulla de menta, dentada
    for i in range(16):
        t = i / 15
        w = 4.0 * math.sin(math.pi * t)
        for s in range(-int(w), int(w) + 1):
            dent = (i % 2 == 0 and abs(s) == int(w))
            x = 46 + math.cos(a) * t * 15 - math.sin(a) * s
            y = 28 + math.sin(a) * t * 15 + math.cos(a) * s
            f.px(x, y, FULLA, (3.0 if s > 0 else 4.0) + (0.6 if dent else 0) - (1.2 if s == 0 else 0))


def _clau(f, a, b, lvl, dents=2):
    """Una clau grossa de ferro: l'anella, la canya i el paletó amb les dents."""
    (ax, ay), (bx, by) = a, b
    L = math.hypot(bx - ax, by - ay)
    ux, uy = (bx - ax) / L, (by - ay) / L
    for k in range(0, 360, 12):                                             # l'anella
        r = math.radians(k)
        x, y = ax - ux * 3 + math.cos(r) * 3.6, ay - uy * 3 + math.sin(r) * 3.6
        f.limb((x, y), (x, y), 1.0, 1.0, IRON, lvl - math.sin(r) * 0.8 - math.cos(r) * 0.4, amp=0.8)
    f.limb((ax + ux * 1, ay + uy * 1), (bx, by), 1.2, 1.1, IRON, lvl, amp=1.6, cont=(0.2, 0.8))
    nx, ny = -uy, ux
    for d in range(dents):                                                  # el paletó
        for s in range(1, 5):
            x = bx - ux * (1 + d * 3) + nx * s
            y = by - uy * (1 + d * 3) + ny * s
            f.px(x, y, IRON, lvl + 0.6 - s * 0.2)
            f.px(x - ux, y - uy, IRON, lvl - 0.6)


def claus(f):
    """El manat de claus d'en Sunifred: un anell gros de ferro i tres claus que en pengen, en ventall."""
    for k in range(0, 360, 8):                                              # l'anell
        r = math.radians(k)
        f.limb((14 + math.cos(r) * 7, 12 + math.sin(r) * 6), (14 + math.cos(r) * 7, 12 + math.sin(r) * 6),
               1.1, 1.1, IRON, 4.8 - math.sin(r) * 0.8 - math.cos(r) * 0.6, amp=0.8)
    _clau(f, (20, 16), (40, 33), 4.4, dents=2)
    _clau(f, (21, 12), (58, 18), 3.8, dents=3)
    _clau(f, (20, 9), (50, 2), 5.0, dents=2)
    sparkle(f, 10, 7, ACER, 6.4, r=1)


def carta_calcada(f):
    """La carta calcada: un pergamí enfosquit de carbonet, i les lletres que en surten clares (el calc)."""
    S = Ic.P([(10, 4), (52, 3), (54, 32), (9, 33)])
    f.drop(S, -1.6, 1, 2)
    f.fill(S, PERG, lambda x, y: 4.4 - (x - 9) * 0.015, rim=(0.6, -1.4))
    for (x, y) in S:                                                        # el carbó, fregat en diagonal
        vora = min(x - 12, 51 - x, y - 5, 30 - y)
        if vora >= 0 or (vora == -1 and hr(x, y, 11) > 0.5):
            cover = math.sin((x + y * 0.6) * 0.18) ** 2
            f.px(x, y, CARBO, 4.6 + cover * 1.0 - (0.5 if (x + y) % 5 == 0 else 0))
    for k, y in enumerate(range(9, 28, 3)):                                 # les lletres, clares
        f.scrib(14, 48 - int(hr(k, 5) * 7), y, PERG, 4.8, seed=k * 5 + 1, dens=0.75, tall=0.3)
    f.ell(18, 31, 3.4, 1.6, CARBO, 3.0, amp=0.8)                            # una ditada


def carta_emma(f):
    """La carta de l'Emma: mig pergamí tallat en ziga-zaga (una carta partida, de la qual cadascú en guarda una
    meitat), amb la lletra de l'Emma."""
    S = set()
    for (x, y) in Ic.P([(8, 4), (50, 3), (50, 33), (9, 33)]):
        zz = 50 - abs(((y - 3) % 8) - 4) * 2.2 - 4                          # el tall, en dents de serra
        if x <= zz:
            S.add((x, y))
    f.drop(S, -1.6, 1, 2)
    f.fill(S, PERG, lambda x, y: 4.6 - (x - 8) * 0.02 - (y - 3) * 0.015, rim=(0.6, -1.4))
    f.text(11, 6, 'E', TINTA, 1.2, font={'E': ('###.', '#...', '###.', '#...', '####')})
    lletra(f, 16, 42, 7, 13, seed=21, dens=0.7)
    lletra(f, 11, 40, 16, 29, seed=27, dens=0.7)
    for (x, y) in S:                                                        # el tall, una mica més fosc
        if (x + 1, y) not in S:
            f.px(x, y, PERG, 2.4)


ICONS = {fn.__name__: fn for fn in (
    guants, destral, olla, pot_resina, pegot, cera, canem, salabre, serra, clofolles, tuniques, habits, habits_curts,
    tisores, alzina, retalls, pot_apotecari, pot_cartes, pot_segellat, planco, pala, cofre,
    tauleta, carbonet, pergamins, ploma, rascador, mocador, cardo, llana, barbes, mel, carbo, unguent, valeriana,
    caparros, salconduit_brut, salconduit_resina, salconduit, xarop, claus, carta_calcada, carta_emma,
)}


def render(item_id):
    """Imatge RGBA de 65×36 de l'objecte, o None si no en té."""
    fn = ICONS.get(item_id)
    if fn is None:
        return None
    f = Ic640()
    fn(f)
    return f.render()
