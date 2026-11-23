"""
Icones d'inventari de L'Última Arrel a 640×360: 65×36 (la casella de l'inventari del HUD, hd640/hud.py), dibuixades
píxel a píxel amb el sistema de hd/items.py (Ic: volum amb llum de dalt a l'esquerra, rampes per material i el
contorn fosc selectiu dels personatges).

Els objectes es veuen damunt les caselles fosques de fusta del HUD: cada icona ha de tenir prou contrast i una
silueta clara. Paleta del bosc (càlida: fusta, molsa, ocres, llautó) amb el turquesa de la Xarxa Miceli on toca
(la lupa, el fil de saba, la pila que funciona); el que és de NaturaPlus (l'estaca, el kit), blanc de plàstic i verd
fluor.

No toca hd/items.py: en reaprofita els materials i les eines i només canvia la mida del llenç.
Ho fan servir draw_items.py / draw_placeholders.py (inventari del joc) i hd640/draw_items.py (full i làmina).
"""
import math

from hd.characters import Fig
from hd.items import (Ic, FONT, M, PAP_C, GRAPH, INKB, BRASS, COPPER, WOOD, PALE, LEATH, BLK, LED, SUNY, CLOTH,
                      DARK, RED)

W, H = 65, 36

# ─── Materials propis ───────────────────────────────────────────────────────
WALKIE = M((10, 10, 8), (22, 20, 16), (38, 34, 26), (58, 52, 38), (82, 74, 54), (110, 100, 74), (140, 130, 100))  # plàstic marró fosc, vell
CHROME = M((30, 34, 40), (64, 70, 80), (110, 116, 126), (160, 166, 174), (206, 210, 216), (240, 242, 246), (255, 255, 255))
TURQ = M((4, 30, 34), (8, 70, 74), (20, 130, 130), (50, 196, 184), (130, 240, 222), (220, 255, 246))
GLOWD = M((6, 24, 26), (10, 44, 46), (16, 66, 66), (24, 92, 90))                                             # el halo turquesa, fosc
LENSQ = M((10, 34, 40), (22, 70, 80), (44, 120, 128), (90, 180, 184), (170, 232, 230), (236, 255, 252))       # el vidre de la lupa
KRAFT = M((30, 34, 18), (54, 62, 30), (80, 92, 44), (108, 122, 60), (138, 152, 80), (170, 182, 108))        # tapes verd molsa
ELAST = M((40, 10, 8), (90, 22, 16), (150, 40, 26), (200, 70, 40), (236, 110, 70))
LEMON = M((70, 50, 4), (130, 100, 8), (190, 156, 16), (230, 200, 34), (250, 228, 80), (255, 246, 160), (255, 255, 220))
LEAFG = M((10, 30, 10), (22, 56, 18), (38, 88, 28), (62, 124, 42), (96, 160, 64), (150, 200, 110))
ZINC = M((24, 28, 32), (44, 50, 56), (70, 78, 84), (100, 108, 114), (134, 142, 146), (170, 176, 178), (206, 210, 210),
         (236, 238, 236), (255, 255, 255))
ORANGEP = M((60, 20, 6), (120, 44, 10), (190, 80, 20), (236, 124, 40), (252, 176, 90))
NEON = M((10, 50, 10), (30, 110, 20), (70, 190, 40), (140, 250, 80), (220, 255, 170))
PLASTW = M((70, 76, 96), (122, 128, 146), (168, 174, 188), (206, 210, 220), (230, 233, 238), (246, 248, 250), (255, 255, 255))
GLASS = M((30, 44, 50), (60, 84, 92), (100, 130, 138), (150, 178, 184), (200, 222, 226), (240, 250, 252))
JAM = M((24, 2, 10), (50, 6, 20), (84, 12, 32), (122, 22, 44), (160, 40, 60), (196, 74, 86))
GING = M((60, 10, 14), (130, 24, 28), (190, 46, 44), (226, 80, 70))
LABEL = M((70, 58, 40), (128, 112, 82), (180, 164, 126), (216, 204, 166), (238, 230, 200), (250, 246, 228))
STRING = M((60, 44, 26), (110, 88, 58), (160, 136, 96), (206, 186, 142))
STEM = M((14, 34, 14), (26, 60, 24), (44, 92, 36), (68, 128, 52), (100, 160, 76), (144, 196, 110))


class Ic640(Ic):
    """Llenç d'una icona de 640: el mateix Ic, a 65×36."""

    def __init__(self):
        Fig.__init__(self, W, H)


def text_w(s, font=FONT, sp=1):
    return sum(len(font[c][0]) + sp for c in s) - sp


def ctext(f, cx, y, s, mat, lvl, font=FONT):
    """Text centrat a cx."""
    f.text(round(cx - text_w(s, font) / 2), y, s, mat, lvl, font=font)


def sparkle(f, x, y, mat, lvl, r=2):
    """Una espurna en creu (el que brilla)."""
    f.px(x, y, mat, lvl + 1.0)
    for d in range(1, r + 1):
        for dx, dy in ((d, 0), (-d, 0), (0, d), (0, -d)):
            f.px(x + dx, y + dy, mat, lvl - d * 0.6)


# ─── Les coses de l'Iri ────────────────────────────────────────────────────

def walkie(f):
    """El walkie vell de l'avi: plàstic marró fosc gastat, l'antena telescòpica de crom, la roda del canal, la
    reixeta de l'altaveu, el botó vermell de gravar i el pilot turquesa (encès)."""
    for i, (a, b, r) in enumerate((((28, 8), (25, 3), 1.2), ((25, 3), (23, 0), 0.9))):   # l'antena, en dos trams
        f.limb(a, b, r, r, CHROME, 4.0 - i * 0.4, amp=1.8)
    f.px(23, 0, CHROME, 6.0)
    f.limb((37, 6), (37, 9), 1.8, 1.8, WALKIE, 3.6, amp=1.6)                # la roda del canal
    for y in (6, 8):
        f.px(36, y, WALKIE, 5.0)
    S = f.R(24, 8, 41, 34) - {(24, 8), (41, 8), (24, 34), (41, 34), (25, 8), (24, 9), (40, 8), (41, 9)}
    f.drop(S, -1.6)
    f.fill(S, WALKIE, lambda x, y: 3.6 - (x - 24) * 0.06 - (y - 8) * 0.03, rim=(0.9, -1.4))
    f.rect(23, 13, 23, 20, WALKIE, 2.2)                                     # el botó de parlar, al costat
    f.rect(27, 11, 38, 14, BLK, 1.0)                                        # la finestreta del canal: «7»
    f.rect(28, 12, 37, 13, TURQ, lambda x, y: 1.6 - (y - 12) * 0.5)
    f.text(35, 11, '7', TURQ, 4.4, font={'7': ('##', '.#', '.#', '.#')})
    for y in range(17, 30, 2):                                              # la reixeta
        for x in range(27, 39, 2):
            f.px(x, y, BLK, 0.6)
            f.px(x + 1, y + 1, WALKIE, 4.6)
    f.ell(30, 32, 1.8, 1.2, RED, 3.4, amp=1.6)                              # gravar
    f.px(30, 32, CLOTH, 4.4)
    f.px(37, 32, TURQ, 4.8)                                                 # el pilot
    for y in range(10, 32, 5):                                              # les ratllades del plàstic
        f.shade(26 + (y * 7) % 12, y, 0.9)


def lupa(f):
    """La lupa de rellotger de l'avi: el canó negre, l'anella de llautó, el vidre amb un reflex turquesa (hi veu la
    Xarxa Miceli) i el cordó de cuir per penjar-la."""
    for i in range(22):                                                     # el cordó, en un llaç
        t = i / 21
        x = 14 + t * 14 - math.sin(t * math.pi) * 4
        y = 30 - t * 14 - math.sin(t * math.pi * 2) * 5
        f.px(x, y, LEATH, 3.0 + math.sin(t * 6) * 0.6)
    f.ell(39, 19, 10, 11, BLK, 2.4, amp=1.8, cont=(0.2, 1.0))                # el canó, darrere (en escorç)
    f.ell(35, 18, 10, 11, BRASS, 3.4, amp=2.0, cont=(0.3, 1.0))              # l'anella
    pix = f.ell(35, 18, 7.6, 8.6, LENSQ, 2.6, amp=1.8)                      # el vidre
    for (x, y) in pix:
        if (x - 31) ** 2 + (y - 13) ** 2 < 7:
            f.shade(x, y, 2.0)
    for (x, y) in ((37, 22), (39, 20), (35, 24), (40, 23)):                 # els filaments, a dins
        f.px(x, y, TURQ, 4.4)
    f.line(33, 24, 40, 19, TURQ, 3.6)
    f.ell(28, 27, 2.0, 1.6, BRASS, 3.0, amp=1.2)                            # l'anella del cordó
    sparkle(f, 30, 11, LENSQ, 4.8)


def llibreta(f):
    """La llibreta de camp: tapes verd molsa, una goma vermella, l'etiqueta amb un bolet dibuixat i el llapis."""
    S = f.R(17, 3, 41, 32) - {(41, 3), (17, 32)}
    f.drop(S, -1.6, 2, 1)
    f.fill(S, KRAFT, lambda x, y: 3.6 - (x - 17) * 0.03 - (y - 3) * 0.03, rim=(0.8, -1.4))
    f.rect(17, 3, 19, 32, KRAFT, 2.0)                                       # el llom
    f.rect(42, 4, 42, 32, PAP_C, 3.2)                                       # el gruix de les fulles
    f.rect(23, 8, 36, 19, PAP_C, 4.4, rim=(0.4, -1.0))                     # l'etiqueta
    f.ell(29.5, 12.5, 3.6, 2.2, ELAST, 3.0, amp=1.2)                       # el bolet dibuixat
    f.rect(29, 14, 30, 17, PAP_C, 2.6)
    f.px(28, 12, PAP_C, 4.6); f.px(31, 11, PAP_C, 4.6)
    f.scrib(25, 34, 18, GRAPH, 1.4, seed=4)
    f.rect(38, 2, 38, 33, ELAST, 3.2)                                       # la goma
    f.rect(39, 2, 39, 33, ELAST, 2.0)
    f.limb((44, 32), (60, 15), 1.1, 1.1, SUNY, 3.4, amp=1.4)               # el llapis
    f.limb((60, 15), (62, 13), 0.9, 0.5, PALE, 3.4, amp=1.0)
    f.px(62, 13, GRAPH, 1.0)


def centim(f):
    """El cèntim de la sort: una moneda de coure inclinada, amb el «1», el cantell i la llum."""
    f.ell(33.5, 19.6, 10.5, 9.0, COPPER, 1.8, amp=1.0)                      # el cantell
    pix = f.ell(32, 17.6, 10.5, 9.0, COPPER, 3.6, amp=1.6, cont=(0.3, 1.0))
    f.ring(32, 17.6, 8.2, 6.8, COPPER, 2.4)
    f.text(30, 14, '1', COPPER, 5.0)
    for (x, y) in ((31, 19), (32, 19), (33, 19)):
        f.shade(x, y, -1.2)
    for (x, y) in pix:
        if (x - 27) ** 2 + (y - 13) ** 2 < 5:
            f.shade(x, y, 1.6)
    sparkle(f, 26, 11, COPPER, 5.4)


# ─── La pila de llimona ─────────────────────────────────────────────────────

def _llimona(f, cx=31, cy=20, fulla=True):
    """Una llimona, ajaguda: groga, amb els porus, els dos mugrons de les puntes i una fulla."""
    f.ell(cx - 13.0, cy + 0.6, 2.4, 1.8, LEMON, 3.0, amp=1.4)               # els mugrons
    f.ell(cx + 13.0, cy - 0.4, 2.4, 1.8, LEMON, 2.4, amp=1.4)
    pix = f.ell(cx, cy, 13, 10, LEMON, 3.4, amp=2.0, cont=(0.3, 1.0))
    for (x, y) in pix:                                                      # els porus
        if (x * 7 + y * 13) % 11 == 0:
            f.shade(x, y, -0.6)
        if (x - cx + 5) ** 2 + (y - cy + 5) ** 2 < 6:
            f.shade(x, y, 1.0)
    if fulla:
        f.ell(cx + 4, cy - 10.5, 5.0, 2.0, LEAFG, 3.2, amp=1.4, cont=(0.2, 0.8))
        f.line(cx + 1, cy - 10, cx + 8, cy - 11, LEAFG, 2.0)
        f.limb((cx + 1, cy - 9), (cx + 2, cy - 11), 0.7, 0.7, WOOD, 3.0)
    return pix


def llimona(f):
    """La llimona de l'àvia."""
    _llimona(f)


def _clava_centim(f, x=38, y=11):
    """El cèntim clavat a la llimona, de cantell (la meitat a fora)."""
    f.ell(x, y, 2.8, 6.0, COPPER, 3.4, amp=1.4, cont=(0.3, 1.0), clip=lambda px, py: py <= y + 1.4)
    f.px(x - 1, y - 3, COPPER, 5.6)
    for xx in range(x - 2, x + 3):
        f.shade(xx, y + 2, -1.2)


def _clava_cargol(f, x=22, y=12):
    """El cargol clavat a la llimona: el cap i dues voltes de rosca a fora."""
    f.limb((x, y), (x + 1.4, y + 3.6), 1.4, 1.2, ZINC, 4.0, amp=1.6)
    for k in range(2):
        f.px(x - 1 + k * 0.6, y + 0.8 + k * 1.4, ZINC, 2.2)
    f.ell(x - 0.6, y - 1.6, 3.0, 1.4, ZINC, 4.4, amp=1.8, cont=(0.3, 1.0))
    f.line(x - 2, y - 1.6, x + 1, y - 1.6, ZINC, 2.0)
    for xx in range(x - 1, x + 3):
        f.shade(xx, y + 4, -1.2)


def llimona_centim(f):
    _llimona(f, fulla=False)
    _clava_centim(f)


def llimona_cargol(f):
    _llimona(f, fulla=False)
    _clava_cargol(f)


def pila_llimona(f):
    """La pila de llimona: el cèntim i el cargol clavats, el fil de coure que els uneix i l'espurna turquesa."""
    _llimona(f, fulla=False)
    _clava_centim(f)
    _clava_cargol(f)
    pts = [(22, 9), (24, 4), (30, 1), (36, 3), (38, 6)]                     # el fil, en arc
    for (a, b) in zip(pts, pts[1:]):
        f.line(a[0], a[1], b[0], b[1], COPPER, 4.0)
    for (x, y) in ((29, 0), (31, 1), (33, 2)):
        f.px(x, y, COPPER, 5.2)
    sparkle(f, 46, 6, TURQ, 4.6, r=3)
    for (x, y) in ((43, 9), (49, 3), (50, 9)):
        f.px(x, y, TURQ, 3.6)


def cargol(f):
    """El cargol galvanitzat, nou de trinca (brilla massa: és de NaturaPlus): el cap, la rosca i la punta."""
    f.ell(14, 18, 3.4, 8.0, ZINC, 3.6, amp=2.0, cont=(0.3, 1.0))            # el cap, de cantell
    f.ell(16, 18, 2.4, 6.4, ZINC, 4.8, amp=1.6)
    f.rect(14, 17, 18, 18, ZINC, 1.6)                                        # la creu
    pix = f.hcyl(19, 47, 18, 3.0, ZINC, 4.0, amp=2.6)                        # la canya
    for x in range(21, 48, 3):                                              # la rosca
        for dy in range(-3, 4):
            f.px(x + (1 if dy > 0 else 0), 18 + dy, ZINC, 2.0 if dy > 0 else 6.0)
    for k in range(6):                                                      # la punta
        f.line(48 + k, 18 - 3 + k * 0.5, 48 + k, 18 + 3 - k * 0.5, ZINC, 4.4 - k * 0.3)
    sparkle(f, 30, 12, ZINC, 7.0, r=3)
    sparkle(f, 44, 22, ZINC, 6.4)


def estaca(f):
    """L'estaca de topògraf: fusta clara, la punta, el cap pintat de taronja i la cinta de NaturaPlus (verd fluor
    i blanc) lligada."""
    f.limb((10, 25), (50, 11), 2.6, 2.6, PALE, 3.4, amp=1.8, cont=(0.2, 0.8))
    for k in range(6):                                                      # la punta
        x, y = 51 + k, 10.6 - k * 0.35
        f.line(x, y - 2.4 + k * 0.4, x, y + 2.4 - k * 0.4, PALE, 3.0 - k * 0.2)
    f.limb((7, 26), (13, 24), 2.9, 2.9, ORANGEP, 3.6, amp=1.8, cont=(0.2, 0.8))   # el cap, pintat
    for x in range(16, 48, 5):                                              # les veres de la fusta
        f.shade(x, 22 - (x - 16) * 0.35, -0.8)
    for i in range(12):                                                     # la cinta, que penja i voleia
        t = i / 11
        x, y = 22 + t * 10, 22 + t * 10 + math.sin(t * 5) * 1.5
        mat = NEON if (i // 2) % 2 == 0 else PLASTW
        f.rect(x, y, x + 2, y + 1, mat, 3.4 - t)
    f.rect(20, 18, 23, 23, NEON, 3.0)


def fil_saba(f):
    """El fil de saba: un fil de fong que brilla de turquesa, cabdellat, amb el halo fosc al voltant."""
    loops = [(26, 18, 11, 7), (34, 17, 10, 8), (31, 21, 12, 6)]
    for cx, cy, rx, ry in loops:                                            # el halo
        f.ring(cx, cy, rx + 1, ry + 1, GLOWD, 2.0, th=2.2)
    for k, (cx, cy, rx, ry) in enumerate(loops):
        for a in range(0, 360, 4):
            r = math.radians(a + k * 40)
            x, y = cx + math.cos(r) * rx, cy + math.sin(r) * ry
            f.px(x, y, TURQ, 3.4 + math.sin(r) * -0.8 + (1.0 if a % 48 == 0 else 0))
    f.line(43, 20, 54, 28, TURQ, 3.0)                                       # el cap que penja
    f.line(54, 28, 58, 26, TURQ, 3.6)
    for (x, y) in ((20, 10), (45, 9), (57, 30), (14, 25)):
        f.px(x, y, TURQ, 4.6)
    sparkle(f, 36, 10, TURQ, 4.8)


# ─── Les coses de la Vet ────────────────────────────────────────────────────

def _pot(f, ple=True):
    """Un pot de vidre amb la tapa de roba de quadres lligada amb cordill (i, si és ple, melmelada de móres)."""
    S = f.R(22, 9, 42, 33) - {(22, 9), (42, 9), (22, 33), (42, 33), (23, 33), (41, 33)}
    f.drop(S, -1.6, 2, 1)
    f.fill(S, GLASS, lambda x, y: 2.6 - (x - 22) * 0.04, rim=(0.6, -1.0))
    if ple:
        J = f.R(24, 13, 40, 31)
        f.fill(J, JAM, lambda x, y: 2.6 - (x - 24) * 0.06 + (0.5 if (x * 5 + y * 3) % 7 == 0 else 0), rim=(0.4, -0.8))
        f.rect(24, 20, 40, 25, LABEL, lambda x, y: 4.0 - (x - 24) * 0.04, rim=(0.4, -1.0))   # l'etiqueta
        f.scrib(26, 37, 22, INKB, 1.6, seed=11, dens=0.9)
        f.scrib(27, 34, 24, INKB, 1.6, seed=3, dens=0.9, tall=0)
    else:
        for x in range(25, 40):                                             # el que queda al cul
            f.px(x, 31, JAM, 2.6)
        f.px(27, 30, JAM, 2.2); f.px(33, 30, JAM, 2.4)
    for y in range(11, 31):                                                 # els reflexos del vidre
        f.px(24, y, GLASS, 5.0)
        if 14 < y < 22:
            f.px(25, y, GLASS, 4.4)
    f.px(39, 26, GLASS, 4.6); f.px(39, 27, GLASS, 4.0)
    T = f.P([(19, 3), (45, 3), (47, 10), (17, 10)])                         # la tapa de roba
    f.fill(T, GING, lambda x, y: 3.0 if ((x // 3) + (y // 3)) % 2 else 1.8, rim=(0.6, -0.8))
    for (x, y) in T:
        if (x // 3) % 2 and (y // 3) % 2:
            f.px(x, y, LABEL, 4.6)
    for x in (18, 46):                                                      # les puntes que pengen
        f.rect(x, 10, x, 12, GING, 2.4)
    f.rect(20, 9, 44, 9, STRING, 3.2)                                       # el cordill
    f.limb((32, 9), (35, 13), 0.6, 0.6, STRING, 3.0)
    f.limb((32, 9), (29, 13), 0.6, 0.6, STRING, 2.6)


def pot_melmelada(f):
    _pot(f, True)


def pot_buit(f):
    _pot(f, False)


def xiulet(f):
    """El xiulet d'ortiga de les fades: una tija buida, amb el bisell i el forat, i dues fulles d'ortiga lligades."""
    f.hcyl(14, 50, 19, 3.6, STEM, 3.0, amp=2.4)
    for x in range(14, 22):                                                 # el bisell de bufar
        for y in range(15, 23):
            if y < 15 + (x - 14) * 0.5:
                f.erase(x, y)
    f.ell(30, 18, 1.8, 1.4, DARK, 1.0, amp=0.4)                             # el forat
    for x in range(23, 50, 6):                                              # els nusos de la tija
        f.rect(x, 16, x, 22, STEM, 1.8)
    for (cx, cy, ang, sgn) in ((44, 11, -25, 1), (49, 27, 20, -1)):         # les fulles, dentades
        a = math.radians(ang)
        for i in range(14):
            t = i / 13
            w = 3.6 * math.sin(math.pi * t)
            for s in range(-int(w), int(w) + 1):
                dent = (i % 2 == 0 and abs(s) == int(w))
                x = cx + math.cos(a) * (t * 13 - 6) - math.sin(a) * s
                y = cy + math.sin(a) * (t * 13 - 6) + math.cos(a) * s
                f.px(x, y, LEAFG, (2.4 if s * sgn > 0 else 3.4) + (0.8 if dent else 0) - (1.2 if s == 0 else 0))
    f.rect(41, 15, 43, 23, STRING, 3.0)                                     # el lligall


def kit(f):
    """El Kit del Petit Guardabosc de NaturaPlus: una capsa de plàstic blanc amb la franja verd fluor, l'arbre que
    somriu i, en un blíster, una lupa de plàstic (de joguina)."""
    S = f.R(10, 4, 54, 32) - {(10, 4), (54, 4), (10, 32), (54, 32)}
    f.drop(S, -1.6, 2, 1)
    f.fill(S, PLASTW, lambda x, y: 4.6 - (x - 10) * 0.02 - (y - 4) * 0.02, rim=(0.6, -1.4))
    f.rect(11, 5, 53, 10, NEON, lambda x, y: 3.2 - (y - 5) * 0.12)
    ctext(f, 32, 6, 'KIT', PLASTW, 6.0, font={**FONT, 'K': ('#.#', '##.', '#..', '##.', '#.#')})
    f.ell(19, 18, 5.0, 4.4, NEON, 3.0, amp=1.4, cont=(0.2, 0.8))           # l'arbre que somriu
    f.rect(18, 22, 20, 28, WOOD, 3.4)
    f.px(17, 17, DARK, 0.8); f.px(21, 17, DARK, 0.8)
    f.px(17, 19, DARK, 0.8); f.px(18, 20, DARK, 0.8); f.px(19, 20, DARK, 0.8); f.px(20, 20, DARK, 0.8)
    f.px(21, 19, DARK, 0.8)
    B = f.R(29, 13, 51, 29)                                                 # el blíster
    f.fill(B, GLASS, 4.4, rim=(0.8, -1.0))
    f.ell(37, 20, 4.6, 4.6, NEON, 3.4, amp=1.4, cont=(0.2, 0.8))           # la lupa de joguina
    f.ell(37, 20, 3.0, 3.0, GLASS, 4.6, amp=1.0)
    f.limb((40, 23), (47, 27), 1.3, 1.3, NEON, 3.0)
    for y in range(14, 29):
        f.px(30, y, GLASS, 5.6)
    for x in range(12, 27, 3):                                              # la lletra petita
        f.px(x, 30, PLASTW, 2.0)
        f.px(x + 1, 30, PLASTW, 2.0)


def caseta_paper(f):
    """La caseta de paper: el fullet del kit doblegat en tres, com una tenda. Blanc, amb la fulla verd fluor del
    logotip a la cara de l'esquerra (la del sol) i la porta fosca a la de la dreta."""
    cx, top, bot = 32, 6, 29
    T = {(x, y) for y in range(top, bot + 1) for x in range(64)
         if abs(x - cx) <= (y - top) * 0.95}
    f.drop(T, -1.6, 2, 1)
    f.fill(T, PLASTW, lambda x, y: (5.0 if x < cx else 3.6) - (y - top) * 0.03, rim=(0.6, -1.4))
    for y in range(top + 1, bot + 1):                                       # el plec del mig
        f.px(cx, y, PLASTW, 2.6)
    f.ell(24, 21, 3.4, 3.0, NEON, 3.2, amp=1.4, cont=(0.2, 0.8))           # la fulla del logotip
    f.limb((24, 23), (24, 26), 0.8, 0.8, NEON, 2.4)
    D = f.R(36, 21, 40, bot)                                                # la porta
    f.fill(D, BLK, 1.2)
    f.px(38, 20, NEON, 4.0)                                                 # una cresta de fada que treu el cap
    f.px(37, 21, NEON, 3.6)
    for x in range(cx - 20, cx + 21, 4):                                    # la lletra petita del fullet
        if abs(x - cx) > 3:
            f.px(x, bot, PLASTW, 2.2)


ICONS = {fn.__name__: fn for fn in (
    walkie, lupa, llibreta, centim, llimona, llimona_centim, llimona_cargol, pila_llimona, cargol, estaca, fil_saba,
    pot_melmelada, pot_buit, xiulet, kit, caseta_paper,
)}


def render(item_id):
    """Imatge RGBA de 65×36 de l'objecte, o None si no en té."""
    fn = ICONS.get(item_id)
    if fn is None:
        return None
    f = Ic640()
    fn(f)
    return f.render()
