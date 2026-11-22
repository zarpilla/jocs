"""
Personatges de La Conjura de l'Avet (any 1017, Sant Joan de les Abadesses; guio/guio.md, «Protagonistes» i
«Secundaris»; guio/pla.md, «Direcció d'art»: roba de l'any 1000, la dels Beatus i del Tapís de la Creació).

Totes les persones es dibuixen a la seva mida, a 1× (com les sales en 3D), amb el sistema de figures amb volum de
hd/characters.py (`person`, el de les adultes d'Aigua Verne) i les proporcions de hd/arrel.py (`figura`, FigY: la
mateixa figura amb el tronc i les cames més llargs o més curts). El contorn és el selectiu de `Fig.render` (la vora
del costat, enfosquida), sense negre.

  - **La Iri** (20 anys, llenyatera, ≈84 px): gonella curta d'ocre, davantal de cuir, guants, destral al cinyell,
    calces verdes i el cabell castany fosc recollit en un monyo alt, lligat amb una tira de cuir.
  - **La Vet** (18 anys, escrivana, ≈78 px, més prima): gonella llarga de blau de pastell apagat, camisa de lli al coll,
    la tauleta de cera i la ploma al cinyell, i el cabell rogenc fosc en dues trenes llargues per davant.
  - **La roba `Monjo`** de totes dues: un hàbit benedictí negre massa gran (a la Vet li arrossega), la caputxa fins al
    nas, la barba de llana negra i el cordó.
  - **Els secundaris**: l'abadessa Ingilberga, la germana Gueraula, el jutge Ponç, l'escrivà Sunifred, el saig Bonfill,
    en Ramon, la Sança, en Joanet, l'Ermessenda i els canonges Gombau i Arnulf. L'únic vermell viu és el de la cera
    dels segells que porta en Ponç penjats del cinyell.

La cara de la Iri i de la Vet és la de sempre (la de Suma Zero), píxel a píxel.

Ho fa servir draw_characters.py (els fulls de Benne). Vegeu també guio/art/personatges.py (la làmina de revisió).
"""
import math

import hd.characters as C
from hd.characters import (M, SKIN_IRI, SKIN_VET, SKIN_FOSCA, SKIN_PALE, SKIN_OLD, SKIN_RUDDY, BOOT, EYE_W, LIP,
                           MOUTH)
from hd.arrel import Prop, FigY, figura, respira, hooks, skirt, smile, CX  # noqa: F401  (figura i respira: draw_characters)
from hd.pix import mix

# ═══════════════════════════════════════════════════════════════════════════
#  Materials
# ═══════════════════════════════════════════════════════════════════════════

# pells (les de la Iri i la Vet, les de sempre)
SKIN_TAN = M((50, 24, 28), (92, 50, 44), (138, 86, 62), (178, 124, 86), (208, 160, 114), (232, 196, 152))
SKIN_OLIVA = M((46, 26, 26), (84, 52, 42), (126, 86, 60), (164, 120, 82), (196, 154, 108), (222, 188, 140))

# la Iri
OCRE = M((36, 24, 12), (68, 46, 20), (104, 74, 32), (140, 104, 46), (172, 134, 64), (200, 166, 96), dith=0.0)
CALCES = M((12, 18, 12), (24, 34, 22), (38, 52, 32), (54, 72, 44), (74, 94, 60), (98, 118, 80), dith=0.0)
CUIR = M((22, 12, 8), (42, 24, 14), (66, 40, 24), (94, 60, 36), (122, 82, 50), (150, 108, 70), dith=0.0)
GUANT = M((34, 20, 12), (64, 40, 22), (98, 64, 36), (132, 92, 54), (164, 124, 78), (190, 156, 108))
HAIR_IRI = M((10, 6, 6), (24, 14, 10), (42, 26, 18), (62, 40, 26), (86, 58, 38), (114, 82, 56))
FREIXE = M((54, 40, 26), (98, 76, 50), (146, 116, 80), (186, 156, 112), (216, 192, 146), (236, 220, 180))
FUSTA = M((20, 12, 8), (40, 24, 14), (66, 42, 24), (96, 64, 36), (128, 90, 54), (160, 122, 78))
ACER = M((20, 22, 28), (44, 48, 56), (76, 82, 90), (114, 120, 126), (158, 164, 168), (206, 210, 210))

# la Vet
PASTELL = M((12, 16, 28), (24, 32, 52), (38, 52, 78), (56, 74, 104), (78, 98, 130), (106, 126, 156), dith=0.0)
LLI = M((64, 58, 52), (112, 104, 92), (160, 152, 134), (200, 192, 172), (228, 222, 202), (246, 242, 226))
HAIR_VET = M((14, 6, 6), (32, 14, 10), (54, 24, 16), (80, 38, 24), (108, 56, 34), (138, 80, 50))
CERA_T = M((40, 30, 6), (80, 62, 14), (124, 98, 26), (164, 134, 44), (196, 168, 70))        # cera de la tauleta
PLOMA = M((90, 86, 84), (150, 146, 140), (200, 196, 188), (236, 232, 224), (252, 250, 244))

# l'hàbit negre (monges, monjos, canonges) i la toca
NEGRE = M((6, 6, 10), (14, 14, 20), (24, 24, 32), (36, 36, 46), (52, 52, 64), (72, 72, 86), dith=0.0)
TOCA = M((70, 70, 84), (120, 120, 130), (170, 168, 170), (208, 204, 198), (232, 228, 220), (248, 246, 238))
LLANA_N = M((14, 12, 14), (30, 28, 30), (48, 46, 48), (68, 66, 66), (90, 88, 86))           # la barba de llana
CORDO = M((50, 40, 28), (96, 82, 60), (146, 130, 100), (190, 176, 140), (222, 210, 176))
LLAUTO = M((40, 24, 16), (84, 54, 22), (138, 96, 34), (190, 144, 54), (230, 192, 90), (252, 234, 160))

# en Ponç
BLAU_P = M((8, 12, 26), (16, 24, 46), (26, 38, 70), (40, 56, 96), (58, 78, 124), (84, 104, 150), dith=0.0)
CAPA = M((20, 12, 10), (40, 24, 18), (64, 40, 28), (90, 58, 40), (118, 80, 56), (146, 106, 76), dith=0.0)
PELL_F = M((40, 34, 30), (78, 70, 62), (120, 110, 98), (160, 150, 134), (196, 188, 170))   # pell de la capa
GORRA = M((20, 8, 12), (38, 14, 22), (60, 24, 34), (84, 36, 46), (108, 52, 60))
SEGELL = M((60, 6, 8), (120, 14, 16), (190, 28, 26), (232, 60, 46), (252, 112, 90))        # l'únic vermell viu
HAIR_GRIS = M((40, 40, 46), (74, 74, 80), (110, 110, 114), (146, 146, 148), (182, 182, 182), (214, 214, 212))

# en Sunifred
GRIS_E = M((12, 12, 14), (24, 24, 28), (38, 38, 44), (54, 54, 62), (74, 74, 82), (98, 98, 106), dith=0.0)
BANYA = M((40, 28, 16), (84, 62, 36), (130, 100, 62), (176, 144, 98), (214, 188, 140))     # el tinter de banya
HAIR_CAST = M((14, 8, 6), (30, 18, 12), (50, 32, 20), (72, 48, 30), (98, 68, 44), (126, 92, 62))

# en Bonfill
PERPUNT = M((30, 22, 14), (58, 44, 26), (90, 70, 42), (122, 98, 60), (152, 126, 80), (180, 156, 104), dith=0.0)
CALCES_B = M((16, 14, 12), (30, 26, 22), (48, 42, 34), (68, 60, 48), (90, 80, 64))
FERRO = M((16, 18, 22), (36, 40, 46), (64, 68, 76), (98, 102, 108), (138, 142, 146), (184, 186, 188))
HAIR_PALLA = M((50, 36, 14), (96, 74, 34), (146, 116, 60), (190, 158, 92), (222, 196, 130), (244, 228, 172))

# en Ramon
BURELL = M((22, 16, 12), (42, 32, 24), (66, 52, 38), (92, 74, 54), (120, 98, 72), (148, 126, 96), dith=0.0)
CALCES_R = M((14, 14, 14), (28, 26, 24), (44, 40, 36), (62, 58, 50), (84, 78, 68))
HAIR_RAMON = M((26, 22, 20), (50, 44, 40), (80, 72, 64), (112, 104, 94), (146, 138, 126), (178, 172, 160))

# la Sança
ROGENC = M((34, 14, 10), (64, 28, 18), (98, 46, 28), (130, 66, 40), (160, 90, 56), (186, 118, 78), dith=0.0)
FARINA = M((70, 64, 58), (116, 110, 100), (160, 154, 142), (196, 190, 178), (220, 214, 202), (238, 234, 224))
MOCADOR = M((12, 16, 30), (24, 32, 56), (40, 52, 84), (60, 76, 110), (86, 102, 136), (118, 132, 160))   # indi
COFIA = M((52, 26, 26), (96, 52, 48), (140, 84, 74), (180, 118, 102), (208, 150, 130), (228, 180, 160))   # rosat esvaït

# en Joanet
RIU = M((18, 24, 28), (34, 44, 50), (54, 68, 74), (78, 94, 98), (104, 120, 122), (134, 148, 146), dith=0.0)
PALLA = M((70, 50, 16), (130, 96, 34), (184, 146, 64), (218, 186, 100), (240, 216, 140), (252, 240, 190))
HAIR_JOANET = M((8, 6, 6), (20, 14, 12), (36, 26, 20), (54, 40, 30), (76, 58, 44), (100, 80, 62))

# l'Ermessenda
VERD_M = M((14, 20, 14), (28, 38, 26), (44, 58, 40), (62, 80, 56), (84, 104, 74), (110, 130, 98), dith=0.0)
HAIR_ENF = M((44, 36, 32), (80, 68, 60), (118, 104, 92), (156, 144, 130), (190, 180, 166), (220, 212, 200))

# els canonges
HAIR_GOMBAU = M((20, 18, 18), (40, 36, 36), (62, 58, 56), (88, 84, 80), (118, 114, 108), (150, 146, 140))
HAIR_ARNULF = M((34, 12, 8), (68, 28, 16), (106, 48, 26), (144, 72, 40), (178, 102, 60), (206, 136, 90))
SABATA_N = M((8, 6, 6), (18, 14, 14), (32, 26, 24), (50, 42, 38), (72, 62, 56))


# ═══════════════════════════════════════════════════════════════════════════
#  Ajudes
# ═══════════════════════════════════════════════════════════════════════════

def _real(fg, x, y):
    """Coordenada de disseny → píxel real de la figura (FigY)."""
    X, Y = fg._m(x, y)
    return int(round(X)), int(round(Y))


def retinta(fg, x0, y0, x1, y1, de, a, dl=0.0):
    """Dins el rectangle de disseny (x0, y0)-(x1, y1), els píxels del material `de` passen a ser de `a`."""
    X0, Y0 = fg._m(x0, y0)
    X1, Y1 = fg._m(x1, y1)
    for Y in range(math.floor(min(Y0, Y1)), math.ceil(max(Y0, Y1)) + 1):
        for X in range(math.floor(min(X0, X1)), math.ceil(max(X0, X1)) + 1):
            if 0 <= X < fg.w and 0 <= Y < fg.h and fg.buf[Y][X] and fg.buf[Y][X][0] is de:
                fg.buf[Y][X] = (a, fg.buf[Y][X][1] + dl)


def faixa(fg, y, mats, mat, lvl, gruix=2, x0=None, x1=None):
    """Una faixa (el cinyell) a la fila de disseny `y`: els píxels dels materials `mats` passen a `mat`."""
    for k in range(gruix):
        _, Y = _real(fg, CX, y + k)
        if not 0 <= Y < fg.h:
            continue
        for X in range(fg.w):
            if x0 is not None and not (x0 <= X <= x1):
                continue
            v = fg.buf[Y][X]
            if v and v[0] in mats:
                u = (X - CX) / 9.0
                fg.buf[Y][X] = (mat, lvl - 0.5 * k - 0.4 * u)


def tapa_cara(fg, p, y0, y1, mat, lvl, S):
    """Tapa la cara (pell i ulls) de les files de disseny y0..y1 (relatives al cap) amb `mat`: la caputxa."""
    hx, hy = p.head
    for yd in range(math.floor(hy + y0), math.ceil(hy + y1) + 1):
        _, Y = _real(fg, hx, yd)
        if not 0 <= Y < fg.h:
            continue
        for X in range(fg.w):
            v = fg.buf[Y][X]
            if v and (v[0] is S or not isinstance(v[0], C.Mat)):
                fg.buf[Y][X] = (mat, lvl - 0.6)


def tapa_fora(fg, p, dins, y0, y1, mat, lvl, S):
    """Com `tapa_cara`, però només fora de l'obertura `dins(x, y)` (coordenades de disseny): les orelles i el coll
    que sortirien de la caputxa."""
    hx, hy = p.head
    for yd in range(math.floor(hy + y0), math.ceil(hy + y1) + 1):
        _, Y = _real(fg, hx, yd)
        if not 0 <= Y < fg.h:
            continue
        for X in range(fg.w):
            v = fg.buf[Y][X]
            if v and (v[0] is S or not isinstance(v[0], C.Mat)) and not dins(*fg._d(X, Y)):
                fg.buf[Y][X] = (mat, lvl - 0.6)


def boca(fg, p, spec):
    """La boca de cara, tornada a pintar damunt la barba."""
    hx, hy = p.head
    ey = int(hy + 0.5)
    nx, my = int(hx), ey + 5
    lip = spec.get('lip', LIP)
    if p.talk:
        for x in (nx - 1, nx, nx + 1):
            fg.px(x, my, MOUTH, 0)
        fg.px(nx, my + 1, MOUTH, 0)
    else:
        fg.px(nx - 1, my, mix(lip, MOUTH, 0.4), 0)
        fg.px(nx, my, mix(lip, MOUTH, 0.6), 0)
        fg.px(nx + 1, my, mix(lip, MOUTH, 0.4), 0)


def boca_perfil(fg, p, spec):
    hx, hy = p.head
    ey = int(hy + 0.5)
    mx, my = int(hx - 5.5), ey + 5
    if p.talk:
        fg.px(mx, my, MOUTH, 0); fg.px(mx + 1, my, MOUTH, 0); fg.px(mx + 1, my + 1, MOUTH, 0)
    else:
        fg.px(mx, my, mix(spec.get('lip', LIP), MOUTH, 0.5), 0); fg.px(mx + 1, my, MOUTH, 0)


def q_head(p):
    """En 3/4 (DL), on és la cara (desplaçada dins el cap): per als ganxos `face_q`."""
    hx, hy = p.head
    k, dx = C._q_dx(hy, p.q)
    return (CX + (hx - CX) * k + dx + C.Q_DX_CARA, hy)


def en_q(fn):
    """Un ganxo de cara (de la figura de cara) per a `face_q`: el torna a pintar a la cara desplaçada del 3/4."""
    def hook(fg, p, spec):
        saved, f = p.head, p.f
        p.head = q_head(p)
        p.f = 'D'
        try:
            fn(fg, p, spec)
        finally:
            p.head, p.f = saved, f
    return hook


def _brins(x, y):
    return 0.4 * math.sin(x * 1.6 + y * 0.3)


def _llana(x, y):
    return -0.8 if (int(x * 1.3) + int(y * 1.1)) % 3 == 0 else 0.3 * math.sin(x * 2.3 + y * 1.7)


def cabell(H, fg, p, front=-3.0, curve=3.6, sides=5.6, side_len=2.4, back=7.8, lvlfn=_brins, nuca=0.0):
    """Un cabell curt: la closca de cabell de cara, de perfil i d'esquena. `front`: on talla el front (relatiu al cap);
    `sides`: a partir d'on cauen pels costats; `side_len`: fins on baixen (relatiu al cap); `nuca`: com de llarg és
    per darrere."""
    hx, hy = p.head
    if p.f == 'D':
        fg.ell(hx, hy - 1.6, 7.4, 7.2, H, 2.6, amp=1.6, cont=(0.2, 0.8), lvlfn=lvlfn,
               clip=lambda x, y: y <= hy + front + ((x - hx) / 7.0) ** 2 * curve or
               (abs(x - hx) > sides and y <= hy + side_len))
    elif p.f == 'L':
        fg.ell(hx + 0.8, hy - 1.6, 7.4, 7.0 + nuca * 0.3, H, 2.6, amp=1.6, cont=(0.2, 0.8), lvlfn=lvlfn,
               clip=lambda x, y: (x >= hx - 1.5 or y <= hy + front - 1.4) and
               not (x < hx + 2.4 and y > hy - 1.0) and y <= hy + side_len + nuca + 2)
    else:
        fg.ell(hx, hy - 0.8, 7.4, 7.8 + nuca * 0.3, H, 2.6, amp=1.6, cont=(0.2, 0.8), lvlfn=lvlfn)


def barba(H, curta=False, llana=False, baixa=0.0):
    """Barba (de cara, de perfil; d'esquena no es veu), i la boca tornada a pintar a sobre. `llana`: la de llana
    dels monjos, arrissada."""
    def hook(fg, p, spec):
        hx, hy = p.head
        ey = int(hy + 0.5)
        lv = _llana if llana else (lambda x, y: 0.5 * math.sin(x * 2.1 + y * 1.3))  # noqa: E731
        ry = 3.4 if curta else 4.6
        if p.f == 'D':
            fg.ell(hx, hy + 5.4 + baixa, 6.4, ry, H, 2.4, amp=1.2, clip=lambda x, y: y >= hy + 2.6 + baixa,
                   lvlfn=lv, cont=(0.0, 0.6))
            for sx in (-1, 1):
                fg.ell(hx + sx * 6.0, hy + 1.6 + baixa, 1.4, 2.8, H, 2.2 if sx < 0 else 1.7, amp=0.8)
            fg.ell(hx - 1.7, ey + 3.5, 2.0, 0.9, H, 2.8, amp=0.8)                       # el bigoti
            fg.ell(hx + 1.7, ey + 3.5, 2.0, 0.9, H, 2.4, amp=0.8)
            if p.q is None:                                 # (en 3/4, la boca la torna a pintar la cara girada)
                boca(fg, p, spec)
        elif p.f == 'L':
            low = 8.6 if not curta else 7.6
            fg.poly([(hx + 2.6, hy + 0.6), (hx + 2.4, hy + 5.6), (hx - 1.0, hy + low), (hx - 5.6, hy + low - 0.6),
                     (hx - 6.6, hy + 5.6), (hx - 3.0, hy + 4.6), (hx - 0.4, hy + 2.4)], H, 2.2, lvlfn=lv)
            fg.px(hx - 5.5, ey + 3.4, H, 3.0); fg.px(hx - 4.5, ey + 3.4, H, 2.6)
            boca_perfil(fg, p, spec)
    return hook


def davantal(mat, y0, y1, w0, w1, lvl=2.8, lvlfn=None, tirants=True, mat_t=None):
    """Un davantal (ganxo `torso`): un pany de y0 a y1 (de disseny, sense el balanceig), de mitja amplada w0 a dalt i
    w1 a baix; de perfil, una peça prima davant del cos; d'esquena, el llaç."""
    mat_t = mat_t or mat

    def hook(fg, p, spec):
        b = p.bob
        if p.f == 'D':
            lift = getattr(p, 'lift', [0, 0])
            sway = (lift[1] - lift[0]) * 0.25
            pts = [(24.5 - w0, y0 + b), (24.5 + w0, y0 + b), (24.5 + w1 + sway, y1 + b), (24.5 - w1 + sway, y1 + b)]
            fg.poly(pts, mat, lvl, amp=1.0, cont=(0.0, 0.7), lvlfn=lvlfn,
                    normal=lambda x, y: (max(-1, min(1, (x - 24.5) / 9)), 0.0, 0.8))
            for y in range(int(y0 + 3), int(y1)):
                fg.shade(24.5 + (y - y0) * 0.05 * w1, y + b, -0.5, mat)
            if tirants:
                fg.line(24.5 - w0, y0 + b, 21.0, 29.0 + b, mat_t, lvl - 0.4)
                fg.line(24.5 + w0, y0 + b, 28.0, 29.0 + b, mat_t, lvl - 0.8)
        elif p.f == 'L':
            xs = [leg[1][0] for leg in p.legs]
            front = min(min(xs) - 3.0, 19.0)
            pts = [(19.0, y0 + b), (21.2, y0 + b), (min(21.0, front + 3.0), y1 + b), (front - 0.6, y1 + b)]
            fg.poly(pts, mat, lvl + 0.3, amp=1.0, cont=(0.0, 0.7), lvlfn=lvlfn)
            if tirants:
                fg.line(21.0, y0 + b, 23.6, 28.6 + b, mat_t, lvl - 0.4)
        else:
            fg.ell(24.5, 45.6 + b, 2.0, 1.2, mat_t, lvl, amp=0.6)
            fg.line(24.5, 46 + b, 23.4, 50 + b, mat_t, lvl - 0.4)
            fg.line(24.5, 46 + b, 26.0, 50.6 + b, mat_t, lvl - 0.7)
    return hook


def cinyell(mat=CUIR, y=45.0, lvl=2.4, mats=None):
    """El cinyell (ganxo `torso`, després de la gonella): una faixa de cuir a la cintura."""
    def hook(fg, p, spec):
        ms = mats or (spec['top'], spec.get('robe', spec['top']))
        faixa(fg, y + p.bob, ms, mat, lvl)
    return hook


def bracos_nus(fg, p, spec, i):
    """Les mànigues arremangades: un plec de roba al colze (els avantbraços, de pell: `forearm`)."""
    if p.f == 'L':
        if i != 0:
            return
        s, e, w = p.arms[0]
    else:
        e = p.elbow[i]
    fg.ell(e[0], e[1] - 0.6, 3.0, 1.6, spec.get('sleeve', spec['top']), 2.4 - 0.4 * i, amp=1.0, cont=(0.0, 0.6))


def guants(mat):
    """Els guants: la mà (de pell) passa a ser de cuir, amb el puny. De perfil, també la mà del fons."""
    def arm(fg, p, spec, i):
        S = spec['skin']
        w = p.arms[0][2] if p.f == 'L' else p.wrist[i]
        if p.f == 'L' and i != 0:
            return
        retinta(fg, w[0] - 3.0, w[1] - 0.8, w[0] + 3.0, w[1] + 5.2, S, mat)
        fg.ell(w[0] - (0.3 if p.f == 'L' else 0), w[1] + 0.3, 2.7, 1.2, mat, 2.4 - 0.4 * i, amp=0.8)

    def fons(fg, p, spec):
        if p.f == 'L':
            w = p.arms[1][2]
            retinta(fg, w[0] - 3.0, w[1] - 0.8, w[0] + 3.0, w[1] + 5.2, spec['skin'], mat, -0.3)
    return arm, fons


# ═══════════════════════════════════════════════════════════════════════════
#  La Iri (20 anys, llenyatera)
# ═══════════════════════════════════════════════════════════════════════════

IRI_PROP = Prop(tronc=1.0, cames=1.06, ample=1.0)


def iri_hair(fg, p, spec):
    """Castany fosc, estirat cap enrere (sense serrell) i recollit en un monyo alt, lligat amb una tira de cuir; un
    floc solt al costat de la cara."""
    hx, hy = p.head
    H = HAIR_IRI
    if p.f == 'D':
        cabell(H, fg, p, front=-3.6, curve=4.4, sides=5.8, side_len=1.0)
        for y in range(int(hy - 8), int(hy - 4)):                               # la ratlla, de biaix
            fg.shade(hx - 1.5, y, -0.9, H)
        fg.ell(hx + 0.4, hy - 9.4, 3.8, 3.0, H, 2.8, amp=1.4, cont=(0.2, 0.8), lvlfn=_brins)   # el monyo
        for x in range(int(hx - 2), int(hx + 3)):                               # la tira de cuir
            fg.px(x, hy - 7.4, CUIR, 3.0 - (x - hx) * 0.2)
        fg.px(hx - 6.2, hy + 2.0, H, 2.0); fg.px(hx - 6.4, hy + 3.0, H, 1.8)     # el floc solt
        fg.px(hx - 6.2, hy + 4.0, H, 1.6)
    elif p.f == 'L':
        cabell(H, fg, p, front=-3.6, side_len=1.0)
        sw = 0.0 if p.walk is None else 0.4 * math.sin(2 * math.pi * p.walk / 6)
        fg.ell(hx + 3.6 + sw, hy - 8.4, 3.6, 3.2, H, 2.6, amp=1.4, cont=(0.2, 0.8), lvlfn=_brins)
        fg.line(hx + 1.6, hy - 6.4, hx + 3.0, hy - 5.4, CUIR, 3.0)
    else:
        cabell(H, fg, p)
        fg.ell(hx, hy - 8.4, 4.0, 3.2, H, 2.6, amp=1.4, cont=(0.2, 0.8), lvlfn=_brins)
        for x in range(int(hx - 2), int(hx + 3)):
            fg.px(x, hy - 6.0, CUIR, 2.6)
        for y in range(int(hy - 5), int(hy + 5)):                               # el recollit, al clatell
            fg.shade(hx, y, -0.6, H)


def destral(fg, p, spec):
    """La destral, ficada al cinyell: el mànec de freixe (clar) avall i el ferro a dalt, a l'alçada del cinyell. De
    cara i d'esquena va damunt de tot (ganxo `over`), de perfil sota el braç del davant (ganxo `torso`)."""
    b = p.bob
    if p.f == 'D':
        fg.limb((29.4, 43.0 + b), (31.2, 59.0 + b), 0.9, 0.9, FREIXE, 3.0, cont=(0.0, 0.8))
        fg.poly([(27.0, 41.0 + b), (29.6, 42.0 + b), (32.4, 40.6 + b), (33.4, 45.6 + b), (30.0, 45.0 + b),
                 (27.0, 44.2 + b)], ACER, 3.2, amp=0.8, cont=(0.0, 0.8))
        fg.line(32.6, 41.0 + b, 33.0, 45.0 + b, ACER, 5.4)                            # el tall, que brilla
    elif p.f == 'U':
        fg.limb((19.6, 43.0 + b), (17.8, 59.0 + b), 0.9, 0.9, FREIXE, 2.4, cont=(0.0, 0.8))
        fg.poly([(22.0, 41.0 + b), (19.4, 42.0 + b), (16.6, 40.6 + b), (15.6, 45.6 + b), (19.0, 45.0 + b),
                 (22.0, 44.2 + b)], ACER, 2.8, amp=0.8, cont=(0.0, 0.8))


def destral_perfil(fg, p, spec):
    """De perfil, la destral al maluc (sota el braç del davant)."""
    if p.f != 'L':
        return
    b = p.bob
    fg.limb((27.6, 44.0 + b), (31.0, 59.0 + b), 0.9, 0.9, FREIXE, 2.8, cont=(0.0, 0.8))
    fg.poly([(24.6, 40.8 + b), (28.4, 42.0 + b), (29.4, 45.8 + b), (25.2, 45.6 + b)], ACER, 3.0, amp=0.8,
            cont=(0.0, 0.8))
    fg.line(24.8, 41.2 + b, 25.2, 45.4 + b, ACER, 5.2)


def iri_collar(fg, p, spec):
    """El coll de la camisa de lli, per sota de la gonella."""
    b = p.bob
    if p.f == 'D':
        fg.ell(24.5, 28.6 + b, 3.8, 1.4, LLI, 3.2, amp=0.8)
    elif p.f == 'L':
        fg.ell(24.0, 28.4 + b, 2.6, 1.2, LLI, 3.0, amp=0.8)


IRI_GUANTS, IRI_GUANTS_FONS = guants(GUANT)

IRI = {
    'skin': SKIN_IRI, 'legs': CALCES, 'top': OCRE, 'shoes': BOOT, 'lashes': True, 'thin': 0.2,
    'iris': (52, 38, 30), 'brow': (24, 16, 22),   # la cara de la Iri, la de sempre
    'prop': IRI_PROP,
    'forearm': SKIN_IRI,                          # les mànigues arremangades: els braços forts, i els guants
    'hooks': {'hair': iri_hair, 'collar': iri_collar, 'arm': hooks(bracos_nus, IRI_GUANTS), 'over': destral,
              'torso': hooks(skirt(OCRE, 63, 2.4, top=44), cinyell(CUIR, 44.0),
                             davantal(CUIR, 33, 61, 4.6, 6.2, lvl=2.6, mat_t=CUIR), destral_perfil,
                             IRI_GUANTS_FONS)},
}


# ═══════════════════════════════════════════════════════════════════════════
#  La Vet (18 anys, escrivana)
# ═══════════════════════════════════════════════════════════════════════════

VET_PROP = Prop(tronc=0.98, cames=0.98, ample=0.92)


def _trena(fg, x0, y0, x1, y1, H, base, n=6):
    for k in range(n):
        t = k / (n - 1)
        fg.ell(x0 + (x1 - x0) * t, y0 + (y1 - y0) * t, 1.5 - 0.2 * t, 1.3, H, base - 0.15 * k, amp=0.9)
        if k % 2:
            fg.shade(x0 + (x1 - x0) * t + 0.5, y0 + (y1 - y0) * t, -0.8, H)


def vet_hair(fg, p, spec):
    """Rogenc fosc, ratlla al mig, i dues trenes llargues que li cauen per davant de les espatlles, lligades amb un
    cordill de lli."""
    hx, hy = p.head
    H = HAIR_VET
    sw = 0.0 if p.walk is None else 0.6 * math.sin(2 * math.pi * p.walk / 6)
    if p.f == 'D':
        cabell(H, fg, p, front=-2.6, curve=4.0, sides=5.4, side_len=3.0)
        for y in range(int(hy - 8), int(hy - 3)):                               # la ratlla al mig
            fg.shade(hx, y, -1.0, H)
        for sx in (-1, 1):
            _trena(fg, hx + sx * 6.4, hy + 4.0, hx + sx * 6.0 + sw * 0.3, hy + 18.0, H, 2.6 if sx < 0 else 2.2)
            fg.px(hx + sx * 6.0 + sw * 0.3, hy + 19.4, LLI, 3.2)
            fg.px(hx + sx * 6.0 + sw * 0.3, hy + 20.4, H, 2.0)
    elif p.f == 'L':
        cabell(H, fg, p, front=-2.6, side_len=3.0)
        _trena(fg, hx + 2.4, hy + 4.4, hx + 0.6 + sw, hy + 17.0, H, 2.4)
        fg.px(hx + 0.6 + sw, hy + 18.4, LLI, 3.0)
    else:
        cabell(H, fg, p, nuca=1.0)
        for y in range(int(hy - 8), int(hy + 4)):
            fg.shade(hx, y, -0.9, H)
        for sx in (-1, 1):                                                       # les trenes, que van cap endavant
            fg.ell(hx + sx * 6.6, hy + 5.6, 1.6, 2.4, H, 2.0, amp=0.8)


def vet_collar(fg, p, spec):
    """La camisa de lli, al coll de la gonella."""
    b = p.bob
    if p.f == 'D':
        fg.ell(24.5, 28.8 + b, 4.4, 1.6, LLI, 3.4, amp=0.8)
        fg.px(24.5, 30.0 + b, LLI, 2.4)
    elif p.f == 'L':
        fg.ell(23.8, 28.6 + b, 2.8, 1.3, LLI, 3.2, amp=0.8)


def tauleta(fg, p, spec):
    """La tauleta de cera (marc de fusta, cera groguenca) i la ploma, al cinyell."""
    b = p.bob
    if p.f == 'D':
        fg.line(30.0, 45.0 + b, 31.0, 48.0 + b, CUIR, 2.0)                       # el cordill
        fg.poly([(28.8, 47.6 + b), (33.6, 47.6 + b), (33.6, 54.6 + b), (28.8, 54.6 + b)], FUSTA, 2.8, amp=0.6,
                cont=(0.0, 0.8))
        fg.poly([(29.8, 48.6 + b), (32.6, 48.6 + b), (32.6, 53.6 + b), (29.8, 53.6 + b)], CERA_T, 2.6)
        fg.line(30.2, 50.0 + b, 32.0, 50.0 + b, CERA_T, 1.2)                     # les ratlles escrites
        fg.line(30.2, 52.0 + b, 31.4, 52.0 + b, CERA_T, 1.2)
        fg.line(19.2, 47.0 + b, 17.4, 39.6 + b, PLOMA, 3.4)                       # la ploma
        fg.line(18.4, 46.0 + b, 16.8, 40.6 + b, PLOMA, 2.6)
        fg.px(19.4, 47.6 + b, BANYA, 2.4)
    elif p.f == 'L':
        fg.poly([(25.4, 46.6 + b), (29.6, 46.6 + b), (29.6, 53.4 + b), (25.4, 53.4 + b)], FUSTA, 2.4, amp=0.6,
                cont=(0.0, 0.8))
        fg.poly([(26.2, 47.6 + b), (28.8, 47.6 + b), (28.8, 52.4 + b), (26.2, 52.4 + b)], CERA_T, 2.4)
        fg.line(26.6, 49.0 + b, 28.4, 49.0 + b, CERA_T, 1.2)
        fg.line(21.2, 46.0 + b, 19.6, 39.4 + b, PLOMA, 3.4)
    else:
        fg.poly([(15.4, 47.6 + b), (20.2, 47.6 + b), (20.2, 54.6 + b), (15.4, 54.6 + b)], FUSTA, 2.2, amp=0.6,
                cont=(0.0, 0.8))


VET = {
    'skin': SKIN_VET, 'legs': PASTELL, 'top': PASTELL, 'shoes': BOOT, 'lashes': True, 'thin': 0.8,
    'iris': (60, 36, 26), 'brow': (26, 14, 14), 'lip': (150, 40, 52),   # la cara de la Vet, la de sempre
    'prop': VET_PROP,
    'hooks': {'hair': vet_hair, 'collar': vet_collar,
              'torso': hooks(skirt(PASTELL, 80, 3.0, top=44), cinyell(CUIR, 44.0), tauleta)},
}


# ═══════════════════════════════════════════════════════════════════════════
#  La roba `Monjo`: l'hàbit negre massa gran, la caputxa fins al nas i la barba de llana
# ═══════════════════════════════════════════════════════════════════════════

def caputxa(mat=NEGRE, r=8.6, barba_llana=True):
    """La caputxa (fins al nas) i la barba de llana negra. Ganxo `hair`; en 3/4, `face_q` torna a tapar els ulls.
    La caputxa és punxeguda, amb la vora de l'obertura més clara (un plec de roba), i deixa veure el nas i les galtes;
    a sota, la barba de llana (més grisa que l'hàbit, arrissada)."""
    def obert(hx, hy, side, g=0.0):
        cx = hx - 3.4 if side else hx
        rx = 4.4 if side else 5.0
        return lambda x, y: ((x - cx) / (rx + g)) ** 2 + ((y - hy - 6.6) / (5.2 + g)) ** 2 <= 1

    def hook(fg, p, spec):
        hx, hy = p.head
        S = spec['skin']
        lv = lambda x, y: 0.35 * math.sin(x * 0.9 + y * 0.5)  # noqa: E731
        side = p.f == 'L'
        if barba_llana and p.f in ('D', 'L'):
            barba(LLANA_N, curta=True, llana=True, baixa=1.4)(fg, p, spec)
        if p.f in ('D', 'L'):
            cx = hx + (1.6 if side else 0.0)
            ob, ob1 = obert(hx, hy, side), obert(hx, hy, side, 1.3)
            fg.ell(cx, hy - 2.0, r - 0.4, r + 1.4, mat, 2.6, amp=1.6, cont=(0.2, 0.8), lvlfn=lv,
                   clip=lambda x, y: not ob(x, y))
            fg.ell(cx, hy - 2.0, r - 0.4, r + 1.4, mat, 4.4, amp=1.0,
                   clip=lambda x, y: ob1(x, y) and not ob(x, y) and y < hy + 8)            # la vora
            fg.ell(cx + (2.6 if side else 0.0), hy - 10.4, 2.2, 2.4, mat, 2.8, amp=1.0, cont=(0.2, 0.8))  # la punta
            if p.q is None:
                tapa_fora(fg, p, ob, -5.0, 12.0, mat, 1.8, S)
            for x in range(int(hx - 6), int(hx + 6)):                              # l'ombra de la vora, a la cara
                fg.shade(x, hy + 2.0, -1.0, S)
        else:
            fg.ell(hx, hy - 1.4, r - 0.4, r + 1.6, mat, 2.6, amp=1.5, cont=(0.2, 0.8), lvlfn=lv)
            fg.ell(hx, hy - 10.4, 2.2, 2.4, mat, 2.6, amp=1.0, cont=(0.2, 0.8))
            for y in range(int(hy - 7), int(hy + 7)):                              # la costura
                fg.shade(hx, y, -0.7, mat)

    def face_q(fg, p, spec):
        saved = p.head
        p.head = q_head(p)
        tapa_cara(fg, p, -4.0, 1.4, mat, 3.0, spec['skin'])
        p.head = saved
    return hook, face_q


def capull(mat=NEGRE):
    """La caputxa, plegada per sobre de les espatlles (ganxo `collar`)."""
    def hook(fg, p, spec):
        b = p.bob
        hx, hy = p.head
        if p.f == 'L':
            fg.poly([(hx - 2.0, hy + 2), (hx + 7.0, hy + 1), (32.0, 30 + b), (21.0, 30 + b)], mat, 2.0, amp=0.6)
            fg.ell(27.6, 29.6 + b, 6.0, 3.6, mat, 2.4, amp=1.2, cont=(0.2, 0.8))
        else:
            fg.poly([(hx - 7.0, hy + 2), (hx + 7.0, hy + 2), (hx + 9.0, 30 + b), (hx - 9.0, 30 + b)], mat, 1.6,
                    amp=0.6)
            fg.ell(24.5, 29.4 + b, 9.6, 3.6, mat, 2.6 if p.f == 'D' else 2.8, amp=1.2, cont=(0.2, 0.8))
    return hook


def manigues(mat, puny=3.0):
    """Les mànigues amples de l'hàbit, que tapen mitja mà (ganxo `arm`)."""
    def hook(fg, p, spec, i):
        if p.f == 'L':
            if i != 0:
                return
            w = p.arms[0][2]
            fg.ell(w[0] - 0.2, w[1] + 0.6, puny, 2.0, mat, 2.4, amp=1.0, cont=(0.0, 0.8))
        else:
            w = p.wrist[i]
            fg.ell(w[0], w[1] + 0.4, puny, 2.0, mat, 2.4 - 0.5 * i, amp=1.0, cont=(0.0, 0.8))
    return hook


def cordo(y=45.0, penja=True):
    """El cordó de l'hàbit, amb el cap que penja (ganxo `torso`)."""
    def hook(fg, p, spec):
        b = p.bob
        faixa(fg, y + b, (spec['top'], NEGRE, GRIS_E), CORDO, 2.6, gruix=1)
        if not penja:
            return
        if p.f == 'D':
            fg.line(21.0, y + 1 + b, 20.4, y + 10 + b, CORDO, 2.2)
            fg.px(20.4, y + 10.6 + b, CORDO, 3.0)
        elif p.f == 'L':
            fg.line(20.6, y + 1 + b, 20.0, y + 9 + b, CORDO, 2.2)
    return hook


def monjo(base, bot=81, flare=3.6, r=8.6, prop=None):
    """La roba `Monjo` sobre una protagonista: la mateixa cara, l'hàbit negre (de la seva mida, una mica gran)."""
    cap, cap_q = caputxa(NEGRE, r=r)
    return {
        **{k: v for k, v in base.items() if k in ('skin', 'lashes', 'iris', 'brow', 'lip', 'prop')},
        'legs': NEGRE, 'top': NEGRE, 'shoes': SABATA_N, 'thin': -0.4,
        'lip': (90, 44, 44),                                # (la boca, entre la llana de la barba)
        **({'prop': prop} if prop else {}),
        'hooks': {'hair': cap, 'face_q': cap_q, 'collar': capull(NEGRE), 'arm': manigues(NEGRE, 3.2),
                  'torso': hooks(skirt(NEGRE, bot, flare, top=44), cordo(45.0))},
    }


IRI_MONJO = monjo(IRI, bot=81, flare=3.6, prop=Prop(tronc=1.02, cames=1.08, ample=1.04))
VET_MONJO = monjo(VET, bot=83, flare=5.0, r=8.8, prop=Prop(tronc=0.98, cames=0.98, ample=1.0))


# ═══════════════════════════════════════════════════════════════════════════
#  Les monges: l'abadessa Ingilberga i la germana Gueraula
# ═══════════════════════════════════════════════════════════════════════════

def toca(vel=NEGRE, blanc=TOCA):
    """La toca blanca que emmarca la cara i el vel negre (ganxos `hair_back`, `collar` i `hair`)."""
    def darrere(fg, p, spec):
        hx, hy = p.head
        b = p.bob
        if p.f == 'D':
            fg.poly([(hx - 7.6, hy - 2), (hx + 7.6, hy - 2), (hx + 9.6, 33 + b), (hx - 9.6, 33 + b)], vel, 1.6,
                    amp=0.6)
        elif p.f == 'L':
            fg.poly([(hx + 1.0, hy - 6), (hx + 7.6, hy - 2), (hx + 9.8, 38 + b), (hx + 3.0, 36 + b)], vel, 2.0,
                    amp=0.6, cont=(0.0, 0.8))

    def coll(fg, p, spec):
        hx, hy = p.head
        b = p.bob
        if p.f == 'D':
            fg.ell(hx, hy + 8.4, 6.6, 4.0, blanc, 3.6, amp=0.6, cont=(0.0, 0.5))     # el barbuquejo, sota la cara
        elif p.f == 'L':
            fg.ell(hx - 0.6, hy + 8.4, 5.2, 4.0, blanc, 3.6, amp=0.6, cont=(0.0, 0.5))
        if p.f in ('D', 'L'):
            return
        fg.poly([(hx - 8.6, hy - 2), (hx + 8.6, hy - 2), (hx + 10.4, 38 + b), (hx - 10.4, 38 + b)], vel, 2.2,
                amp=0.8, cont=(0.0, 0.8))

    def cap(fg, p, spec):
        hx, hy = p.head
        b = p.bob
        if p.f == 'D':
            fg.ell(hx, hy - 0.6, 7.8, 8.2, blanc, 3.2, amp=1.2,
                   clip=lambda x, y: y <= hy - 3.6 or abs(x - hx) > 5.0)
            fg.ell(hx, hy - 2.0, 8.8, 7.8, vel, 2.4, amp=1.5, cont=(0.2, 0.8),
                   clip=lambda x, y: y <= hy - 5.0 + ((x - hx) / 8.0) ** 2 * 2.0 or abs(x - hx) > 7.4)
            for sx in (-1, 1):                                                       # el vel, que cau
                fg.poly([(hx + sx * 7.4, hy - 4), (hx + sx * 9.0, hy - 3), (hx + sx * 9.8, 32 + b),
                         (hx + sx * 7.4, 31 + b)], vel, 2.0 if sx < 0 else 1.6, amp=0.6, cont=(0.0, 0.8))
        elif p.f == 'L':
            fg.ell(hx + 0.4, hy - 0.6, 7.2, 8.0, blanc, 3.2, amp=1.2,
                   clip=lambda x, y: y <= hy - 3.6 or x >= hx - 0.6)
            fg.ell(hx + 1.6, hy - 2.0, 8.0, 7.6, vel, 2.4, amp=1.5, cont=(0.2, 0.8),
                   clip=lambda x, y: y <= hy - 4.6 or x >= hx + 2.0)
        else:
            fg.ell(hx, hy - 1.0, 8.8, 9.6, vel, 2.4, amp=1.5, cont=(0.2, 0.8))
            for y in range(int(hy), 30 + b):
                fg.shade(hx - 3, y, -0.6, vel)
                fg.shade(hx + 3, y, -0.6, vel)
    return darrere, coll, cap


def somriu(fg, p, spec):
    """El somriure (hd/arrel.py, `smile`), només de cara i abans de girar (en 3/4, `face_q`)."""
    if p.f == 'D' and p.q is None:
        smile(fg, p, spec)


def nomes_cara(fn):
    """Un ganxo de cara que només es pinta de cara (en 3/4 es fa amb `face_q`, després de girar)."""
    def hook(fg, p, spec):
        if p.f == 'L' or (p.f == 'D' and p.q is None):
            fn(fg, p, spec)
    return hook


def creu(fg, p, spec):
    """La creu petita, penjada al pit."""
    if p.f != 'D':
        return
    b = p.bob
    fg.line(22.0, 30.0 + b, 24.5, 34.0 + b, CORDO, 1.6)
    fg.line(27.0, 30.0 + b, 24.5, 34.0 + b, CORDO, 1.4)
    for y in range(34, 39):
        fg.px(24.5, y + b, LLAUTO, 3.4 - (y - 34) * 0.2)
    fg.px(23.5, 35.0 + b, LLAUTO, 3.2)
    fg.px(25.5, 35.0 + b, LLAUTO, 2.6)


ING_TOCA = toca()

INGILBERGA = {
    'skin': SKIN_OLD, 'legs': NEGRE, 'top': NEGRE, 'shoes': SABATA_N, 'thin': 0.6,
    'iris': (70, 74, 80), 'brow': (110, 100, 100), 'lip': (140, 84, 86), 'brow_dy': 0,
    'prop': Prop(tronc=1.02, cames=1.06, ample=0.94),
    'hooks': {'hair_back': ING_TOCA[0], 'collar': ING_TOCA[1], 'hair': ING_TOCA[2], 'over': creu,
              'arm': manigues(NEGRE, 2.8), 'torso': hooks(skirt(NEGRE, 81, 2.4, top=44), cordo(45.0, penja=False))},
}


TAQUES = [(21.4, 38, (40, 110, 50)), (27.0, 41, (150, 120, 30)), (23.0, 47, (100, 50, 110)),
          (28.4, 52, (40, 110, 50)), (20.6, 55, (130, 70, 30)), (25.6, 58, (60, 90, 140))]


def taques(fg, p, spec):
    if p.f != 'D':
        if p.f == 'L':
            fg.px(18.6, 46 + p.bob, (40, 110, 50), 0)
            fg.px(18.0, 53 + p.bob, (100, 50, 110), 0)
        return
    for x, y, c in TAQUES:
        v = fg.get(x, y + p.bob)
        if v and v[0] is LLI:
            fg.px(x, y + p.bob, c, 0)
            v2 = fg.get(x + 1, y + p.bob)
            if v2 and v2[0] is LLI:
                fg.px(x + 1, y + p.bob, mix(c, (220, 214, 196), 0.4), 0)


GUE_TOCA = toca()

GUERAULA = {
    'skin': SKIN_RUDDY, 'legs': NEGRE, 'top': NEGRE, 'shoes': SABATA_N, 'thin': -1.0,
    'forearm': SKIN_RUDDY, 'iris': (60, 70, 40), 'brow': (70, 44, 30), 'lip': (160, 70, 70),
    'prop': Prop(tronc=1.0, cames=1.04, ample=1.14),
    'hooks': {'hair_back': GUE_TOCA[0], 'collar': GUE_TOCA[1], 'hair': hooks(GUE_TOCA[2], somriu),
              'face_q': en_q(smile), 'arm': bracos_nus,
              'torso': hooks(skirt(NEGRE, 81, 3.0, top=44), davantal(LLI, 34, 66, 5.4, 7.4, lvl=3.0), taques)},
}


# ═══════════════════════════════════════════════════════════════════════════
#  El jutge Ponç (el del comte, ~55 anys, pedant)
# ═══════════════════════════════════════════════════════════════════════════

def gorra(mat, alt=5.0, ample=6.6):
    """Una gorra rodona de feltre, de cilindre baix (ganxo `hair`, després del cabell)."""
    def hook(fg, p, spec):
        hx, hy = p.head
        dx = 0.8 if p.f == 'L' else 0.0
        top, bot = hy - 4.4 - alt, hy - 3.4
        fg.poly([(hx + dx - ample, bot), (hx + dx + ample, bot), (hx + dx + ample - 0.6, top),
                 (hx + dx - ample + 0.6, top)], mat, 2.6, amp=1.2, cont=(0.2, 0.8),
                normal=lambda x, y: (max(-1, min(1, (x - hx - dx) / ample)), -0.2, 0.9))
        fg.ell(hx + dx, top, ample - 0.6, 1.2, mat, 3.4, amp=0.6)
        for x in range(int(hx + dx - ample), int(hx + dx + ample) + 1):            # la vora, girada
            fg.px(x, bot, mat, 1.6)
    return hook


def capa(mat=CAPA, pell=PELL_F):
    """La capa: per darrere del cos (de cara i de perfil), damunt l'esquena (d'esquena), amb el coll de pell."""
    def darrere(fg, p, spec):
        b = p.bob
        if p.f == 'D':
            fg.poly([(14.0, 29 + b), (35.0, 29 + b), (37.6, 76 + b), (11.4, 76 + b)], mat, 1.6, amp=0.8,
                    cont=(0.0, 0.8))
        elif p.f == 'L':
            sw = 0.0 if p.walk is None else 1.4 * abs(math.sin(2 * math.pi * p.walk / 6))
            fg.poly([(24.0, 28 + b), (31.6, 29 + b), (35.6 + sw, 76 + b), (27.0, 76 + b)], mat, 2.2, amp=0.8,
                    cont=(0.0, 0.8))

    def sobre(fg, p, spec):
        b = p.bob
        if p.f == 'U':
            fg.poly([(15.0, 29 + b), (34.0, 29 + b), (36.6, 76 + b), (12.4, 76 + b)], mat, 2.4, amp=1.0,
                    cont=(0.0, 0.8), normal=lambda x, y: (max(-1, min(1, (x - 24.5) / 12)), 0.0, 0.9))
            for fx in (19.5, 29.5):
                for y in range(40, 76):
                    fg.shade(fx + (y - 40) * 0.05 * (1 if fx > 24 else -1), y + b, -0.7, mat)

    def coll(fg, p, spec):
        b = p.bob
        if p.f == 'L':
            fg.ell(27.0, 29.0 + b, 5.4, 2.6, pell, 2.6, amp=1.0, cont=(0.2, 0.8), lvlfn=_llana)
        else:
            fg.ell(24.5, 29.0 + b, 9.8, 2.8, pell, 2.8, amp=1.0, cont=(0.2, 0.8), lvlfn=_llana)
            if p.f == 'D':
                fg.ell(24.5, 31.0 + b, 1.2, 1.2, LLAUTO, 3.6, amp=0.6)                 # el fermall
    return darrere, sobre, coll


def segells(fg, p, spec):
    """Els segells de cera vermella, penjats del cinyell amb cordills: l'únic vermell viu del joc."""
    b = p.bob
    if p.f == 'D':
        for x, l in ((20.6, 7.0), (23.0, 9.0), (28.4, 6.0)):
            fg.line(x, 47.0 + b, x + 0.2, 47.0 + l + b, CORDO, 1.8)
            fg.ell(x + 0.2, 48.6 + l + b, 1.5, 1.5, SEGELL, 2.8, amp=1.0)
    elif p.f == 'L':
        for x, l in ((20.6, 7.0), (23.0, 9.0)):
            fg.line(x, 47.0 + b, x + 0.2, 47.0 + l + b, CORDO, 1.8)
            fg.ell(x + 0.2, 48.6 + l + b, 1.4, 1.5, SEGELL, 2.8, amp=1.0)


PONC_CAPA = capa()

PONC = {
    'skin': SKIN_OLD, 'legs': BLAU_P, 'top': BLAU_P, 'shoes': SABATA_N, 'thin': 0.6,
    'iris': (60, 50, 40), 'brow': (150, 146, 146), 'lip': (140, 80, 80), 'brow_dy': -1,
    'prop': Prop(tronc=1.04, cames=1.12, ample=0.94),
    'hooks': {'hair_back': PONC_CAPA[0], 'collar': PONC_CAPA[2], 'over': PONC_CAPA[1],
              'hair': hooks(lambda fg, p, s: cabell(HAIR_GRIS, fg, p, front=-4.6, curve=1.0, sides=5.2,
                                                    side_len=3.0, nuca=1.0), gorra(GORRA)),
              'torso': hooks(skirt(BLAU_P, 81, 2.0, top=44), cinyell(CUIR, 45.0), segells)},
}


# ═══════════════════════════════════════════════════════════════════════════
#  L'escrivà Sunifred (~35 anys, mans netíssimes)
# ═══════════════════════════════════════════════════════════════════════════

def tinter(fg, p, spec):
    """El tinter de banya i les plomes, al cinyell."""
    b = p.bob
    if p.f == 'D':
        fg.limb((30.6, 46.0 + b), (31.6, 51.4 + b), 1.4, 0.8, BANYA, 3.0, cont=(0.0, 0.8))
        fg.px(30.4, 45.6 + b, LLAUTO, 3.4)
        fg.line(18.8, 46.0 + b, 17.0, 38.6 + b, PLOMA, 3.4)
        fg.line(20.0, 46.0 + b, 19.4, 39.0 + b, PLOMA, 2.8)
        fg.px(17.0, 38.6 + b, (30, 30, 40), 0)
    elif p.f == 'L':
        fg.limb((26.6, 46.0 + b), (27.4, 51.2 + b), 1.4, 0.8, BANYA, 2.8, cont=(0.0, 0.8))
        fg.line(21.0, 46.0 + b, 19.4, 39.0 + b, PLOMA, 3.4)


def punys_lli(fg, p, spec, i):
    """Els punys de la camisa de lli (blancs) i les mans netes."""
    if p.f == 'L':
        if i != 0:
            return
        w = p.arms[0][2]
    else:
        w = p.wrist[i]
    fg.ell(w[0], w[1] + 0.2, 2.6, 1.0, LLI, 3.4 - 0.5 * i, amp=0.6)


SUNIFRED = {
    'skin': SKIN_PALE, 'legs': GRIS_E, 'top': GRIS_E, 'shoes': SABATA_N, 'thin': 0.6,
    'iris': (70, 90, 110), 'brow': (60, 40, 30), 'lip': (156, 86, 86),
    'prop': Prop(tronc=1.0, cames=1.06, ample=0.94),
    'hooks': {'collar': vet_collar, 'arm': punys_lli,
              'hair': hooks(lambda fg, p, s: cabell(HAIR_CAST, fg, p, front=-2.2, curve=0.6, sides=5.4,
                                                    side_len=1.6, nuca=0.6), somriu),
              'face_q': en_q(smile),
              'torso': hooks(skirt(GRIS_E, 80, 2.0, top=44), cinyell(CUIR, 45.0), tinter)},
}


DORM = (0, 0, 1, 1)                     # quant puja el cos a cada fotograma de la DormD (en px de disseny)


def sunifred_dorm(k=0):
    """En Sunifred adormit a la taula de la cuina, de cara (etiqueta `DormD`): inclinat endavant, els braços plegats
    damunt la taula i el cap de costat sobre els braços, els ulls closos. `k`: el fotograma (0-3): el cos puja una
    mica (DORM) i, als dos darrers, ronca amb la boca oberta. Les cames (la taula les tapa) són les de sempre."""
    spec = SUNIFRED
    S = spec['skin']
    fg = type('FigP', (FigY,), {'prop': spec['prop']})(49, 87)
    # de cintura avall, com dret (la taula ho tapa)
    for x0 in (21.0, 28.0):
        C.shoe_front(fg, (x0, 80.0), SABATA_N, 2.2)
    skirt(GRIS_E, 80, 2.0, top=50)(fg, type('P', (), {'bob': 0, 'f': 'D', 'thin': 0.6, 'lift': [0, 0]})(), spec)
    fg.oy = -DORM[k]
    # el tronc, inclinat cap a la càmera: més curt, les espatlles més avall i més amples, arquejat
    fg.lathe(34, 54, lambda y: (24.5 - 10.2 + max(0, 37 - y) * 0.9, 24.5 + 10.2 - max(0, 37 - y) * 0.9), GRIS_E, 2.6,
             amp=1.6)
    for y in range(37, 52):                                                         # l'esquena arquejada: més llum a dalt
        fg.shade(24.5, y, 0.4 if y < 42 else 0.0, GRIS_E)
    # els braços plegats damunt la taula: els de dalt cap avall i endavant, els avantbraços de través
    for sx, dl in ((-1, 0.0), (1, -0.5)):
        fg.limb((24.5 + sx * 9.0, 37.5), (24.5 + sx * 11.4, 47.0), 3.0, 2.7, GRIS_E, 2.6 + dl, cont=(0.3, 1.0))
    fg.limb((13.6, 49.0), (31.0, 50.6), 2.7, 2.5, GRIS_E, 2.5, cont=(0.3, 1.0))      # l'avantbraç de sota
    fg.limb((35.4, 48.4), (19.0, 47.6), 2.7, 2.5, GRIS_E, 2.8, cont=(0.3, 1.0))      # el de sobre
    for x, y, l in ((31.8, 51.0, 2.4), (18.0, 47.8, 2.8)):                          # els punys i les mans
        fg.ell(x, y, 1.2, 2.2, LLI, 3.2, amp=0.6)
        fg.ell(x + (1.8 if x > 25 else -1.8), y, 1.8, 2.0, S, l, amp=1.2)
    # el cap, de costat sobre els braços (la galta dreta avall): més ample que alt, una mica girat
    hx, hy = 26.0, 42.4
    fg.ell(hx, hy, 7.4, 6.2, S, 3.0, amp=1.5)
    fg.ell(hx + 2.0, hy + 2.8, 4.6, 3.2, S, 3.0, amp=1.4)                            # la galta i la barbeta
    fg.ell(hx - 6.0, hy - 0.4, 1.6, 1.4, S, 2.6, amp=1.0)                            # l'orella de dalt
    # el cabell: la closca, cap a dalt a l'esquerra (el cap ajagut)
    fg.ell(hx - 1.6, hy - 2.0, 7.2, 5.6, HAIR_CAST, 2.6, amp=1.6, cont=(0.2, 0.8), lvlfn=_brins,
           clip=lambda x, y: (x - hx) * 0.45 + (y - hy) < -1.2 or x < hx - 5.0)
    # la cara: els ulls closos (dues ratlles de biaix), les celles, el nas, la boca
    eye, brow = (34, 22, 30), spec['brow']
    for x0, y0 in ((hx - 1.0, hy + 0.4), (hx + 3.6, hy + 1.8)):
        fg.px(x0, y0, eye, 0)
        fg.px(x0 + 1, y0 + 0.4, eye, 0)
        fg.px(x0 + 0.2, y0 - 2.2, brow, 0)
        fg.px(x0 + 1.2, y0 - 1.8, brow, 0)
    fg.shade(hx + 2.4, hy + 3.0, -1.0, S)                                           # el nas
    fg.shade(hx + 2.8, hy + 3.8, -1.2, S)
    if k >= 2:                                                                      # ronca: la boca oberta
        fg.px(hx + 4.4, hy + 5.0, MOUTH, 0)
        fg.px(hx + 5.2, hy + 5.2, MOUTH, 0)
        fg.px(hx + 4.8, hy + 5.8, MOUTH, 0)
    else:
        fg.px(hx + 4.4, hy + 5.0, mix(spec['lip'], MOUTH, 0.5), 0)
        fg.px(hx + 5.2, hy + 5.2, spec['lip'], 0)
    return fg.render()


# ═══════════════════════════════════════════════════════════════════════════
#  El saig Bonfill (~30 anys, curt de gambals)
# ═══════════════════════════════════════════════════════════════════════════

def pespunts(fg, p, spec):
    """Els pespunts del perpunt: una ratlla fosca cada tres files, del coll a la vora."""
    for y in range(30, 62, 3):
        _, Y = _real(fg, CX, y + p.bob)
        if 0 <= Y < fg.h:
            for X in range(fg.w):
                v = fg.buf[Y][X]
                if v and v[0] is PERPUNT:
                    fg.buf[Y][X] = (PERPUNT, v[1] - 0.7)


def cervellera(fg, p, spec):
    """La cervellera de ferro (un casquet) i el cabell de palla, esbullat, que en surt per sota."""
    hx, hy = p.head
    dx = 0.8 if p.f == 'L' else 0.0
    if p.f == 'D':
        for sx in (-1, 1):
            fg.ell(hx + sx * 6.2, hy - 0.6, 1.8, 2.6, HAIR_PALLA, 2.6 if sx < 0 else 2.0, amp=0.8, lvlfn=_brins)
        for x in (-4, -2, 1, 3):
            fg.px(hx + x, hy - 3.0, HAIR_PALLA, 2.8)
    elif p.f == 'L':
        fg.ell(hx + 3.6, hy + 0.6, 3.6, 3.4, HAIR_PALLA, 2.4, amp=1.0, lvlfn=_brins)
    else:
        fg.ell(hx, hy + 0.4, 7.2, 4.4, HAIR_PALLA, 2.4, amp=1.0, lvlfn=_brins, clip=lambda x, y: y >= hy - 2)
    fg.ell(hx + dx, hy - 3.6, 7.6, 6.0, FERRO, 2.8, amp=1.8, cont=(0.2, 0.8), clip=lambda x, y: y <= hy - 3.0)
    for x in range(int(hx + dx - 7), int(hx + dx + 8)):
        fg.px(x, hy - 3.0, FERRO, 1.8)
    if p.f == 'D':
        fg.px(hx - 3, hy - 7.0, FERRO, 5.0)


def llanca(fg, p, spec, i):
    """La llança, dreta, a la mà (la de la dreta de la pantalla de cara; la del davant de perfil)."""
    if p.f == 'L':
        if i != 0:
            return
        w = p.arms[0][2]
        x = w[0] - 0.6
    else:
        if i != 1:
            return
        w = p.wrist[1]
        x = w[0] + 0.2
    top = max(0.6, 0.4 + (w[1] - 50.5) * 0.6)
    fg.limb((x, top + 5.0), (x, w[1] + 14.0), 0.7, 0.7, FUSTA, 2.8, cont=(0.0, 0.5))
    fg.poly([(x, top - 1.0), (x + 1.4, top + 2.6), (x + 0.8, top + 5.4), (x - 0.8, top + 5.4), (x - 1.4, top + 2.6)],
            ACER, 3.2, amp=0.8, cont=(0.0, 0.6))
    fg.ell(x, w[1] + 2.0, 2.1, 2.3, spec['skin'], 2.6 - 0.4 * (p.f == 'U'), amp=1.2)


BONFILL = {
    'skin': SKIN_RUDDY, 'legs': CALCES_B, 'top': PERPUNT, 'shoes': BOOT, 'thin': -0.6,
    'iris': (70, 90, 110), 'brow': (150, 120, 60), 'lip': (160, 80, 74), 'brow_dy': -1,
    'prop': Prop(tronc=1.06, cames=1.12, ample=1.06),
    'hooks': {'hair': cervellera, 'arm': llanca,
              'torso': hooks(skirt(PERPUNT, 62, 2.4, top=44), pespunts, cinyell(CUIR, 46.0))},
}


# ═══════════════════════════════════════════════════════════════════════════
#  En Ramon (el pare, llenyataire, ~50 anys, corpulent)
# ═══════════════════════════════════════════════════════════════════════════

RAMON = {
    'skin': SKIN_RUDDY, 'legs': CALCES_R, 'top': BURELL, 'shoes': BOOT, 'thin': -1.0,
    'iris': (52, 38, 30), 'brow': (70, 62, 56), 'lip': (150, 80, 74), 'stoop': 1,
    'prop': Prop(tronc=1.08, cames=1.12, ample=1.12),
    'hooks': {'hair': hooks(lambda fg, p, s: cabell(HAIR_RAMON, fg, p, front=-4.0, curve=1.6, sides=5.6,
                                                    side_len=2.0, nuca=1.0), barba(HAIR_RAMON)),
              'collar': iri_collar,
              'torso': hooks(skirt(BURELL, 64, 2.6, top=44), cinyell(CUIR, 45.0))},
}


# ═══════════════════════════════════════════════════════════════════════════
#  La Sança (la fornera, ~45 anys, braços forts)
# ═══════════════════════════════════════════════════════════════════════════

def mocador(mat, cabell_mat=None, nus=True, vora=False, lvlfn=None):
    """El mocador lligat al cap (el nus darrere), i el cabell que en surt per sota. `vora`: amb la vora girada (una
    ratlla més fosca) i un floc de cabell al front."""
    def hook(fg, p, spec):
        hx, hy = p.head
        if vora and cabell_mat and p.f == 'D':
            fg.ell(hx - 1.0, hy - 3.0, 4.0, 1.4, cabell_mat, 2.6, amp=0.8)
        if p.f == 'D':
            if cabell_mat:
                for sx in (-1, 1):
                    fg.ell(hx + sx * 6.2, hy + 0.4, 1.6, 2.6, cabell_mat, 2.4 if sx < 0 else 1.9, amp=0.8)
            fg.ell(hx, hy - 1.8, 8.0, 7.4, mat, 2.8, amp=1.5, cont=(0.2, 0.8), lvlfn=lvlfn,
                   clip=lambda x, y: y <= hy - 3.6 - (0.6 if vora else 0) + ((x - hx) / 7.4) ** 2 * 3.0)
            for x in range(int(hx - 6), int(hx + 7)):
                fg.px(x, hy - 3.6 + ((x - hx) / 7.4) ** 2 * 3.0 - (0.6 if vora else 0), mat, 1.4 if vora else 1.8)
        elif p.f == 'L':
            if cabell_mat:
                fg.ell(hx + 4.0, hy + 2.2, 2.2, 2.0, cabell_mat, 2.2, amp=0.8)
            fg.ell(hx + 1.0, hy - 1.8, 7.8, 7.2, mat, 2.8, amp=1.5, cont=(0.2, 0.8), lvlfn=lvlfn,
                   clip=lambda x, y: (y <= hy - 3.0 or x >= hx + 3.0) and y <= hy + 2.0)
            if nus:
                fg.ell(hx + 8.2, hy - 0.4, 2.0, 1.8, mat, 2.4, amp=1.0, cont=(0.2, 0.8))
                fg.line(hx + 8.6, hy + 1.0, hx + 9.6, hy + 4.0, mat, 2.0)
        else:
            fg.ell(hx, hy - 1.0, 8.0, 8.2, mat, 2.6, amp=1.5, cont=(0.2, 0.8), lvlfn=lvlfn,
                   clip=lambda x, y: y <= hy + 3.0)
            if nus:
                fg.ell(hx, hy + 3.6, 2.2, 1.6, mat, 2.4, amp=1.0, cont=(0.2, 0.8))
                fg.line(hx - 0.6, hy + 4.4, hx - 1.6, hy + 8.0, mat, 2.0)
                fg.line(hx + 0.6, hy + 4.4, hx + 1.4, hy + 7.6, mat, 1.8)
    return hook


def _enfarinat(x, y):
    return 0.6 if (int(x * 1.7) + int(y * 2.3)) % 5 == 0 else 0.0


def farina_braços(fg, p, spec):
    """Una mica de farina als avantbraços."""
    if p.f == 'D':
        for w in p.wrist:
            fg.shade(w[0], w[1] - 2, 0.8, spec['skin'])
            fg.shade(w[0] + 1, w[1] - 4, 0.6, spec['skin'])


SANCA = {
    'skin': SKIN_FOSCA, 'legs': ROGENC, 'top': ROGENC, 'shoes': BOOT, 'thin': -0.8, 'forearm': SKIN_FOSCA,
    'iris': (40, 26, 20), 'brow': (30, 20, 18), 'lip': (130, 60, 60), 'brow_dy': 1,
    'prop': Prop(tronc=1.02, cames=1.06, ample=1.1),
    'hooks': {'hair': mocador(MOCADOR, HAIR_JOANET, vora=True), 'arm': bracos_nus, 'over': farina_braços,
              'torso': hooks(skirt(ROGENC, 80, 2.6, top=44),
                             davantal(FARINA, 40, 72, 6.0, 7.6, lvl=2.4, lvlfn=_enfarinat, tirants=False),
                             cinyell(LLI, 40.0, 3.4, mats=(ROGENC, FARINA)))},
}


# ═══════════════════════════════════════════════════════════════════════════
#  En Joanet (pescador d'anguiles, ~30 anys, mandrós)
# ═══════════════════════════════════════════════════════════════════════════

def _palla(x, y):
    return 0.5 if (int(x) + int(y)) % 2 == 0 else -0.3


def barret_pescador(fg, p, spec):
    """El barret de palla del riu: copa baixa i ala caiguda; el cabell negre que en surt; els ulls mig closos."""
    hx, hy = p.head
    dx = 0.8 if p.f == 'L' else 0.0
    if p.f == 'D':
        for sx in (-1, 1):
            fg.ell(hx + sx * 6.2, hy + 0.6, 1.6, 2.4, HAIR_JOANET, 2.4 if sx < 0 else 1.9, amp=0.8)
    elif p.f == 'L':
        fg.ell(hx + 3.8, hy + 1.0, 3.0, 3.0, HAIR_JOANET, 2.2, amp=0.8)
    else:
        fg.ell(hx, hy + 0.6, 7.0, 4.0, HAIR_JOANET, 2.2, amp=0.8, clip=lambda x, y: y >= hy - 1)
    fg.ell(hx + dx, hy - 5.0, 6.4, 3.8, PALLA, 2.6, amp=1.4, cont=(0.2, 0.9), lvlfn=_palla)
    fg.ell(hx + dx, hy - 3.6, 6.8, 1.0, CUIR, 2.2, amp=0.8)
    fg.ell(hx + dx, hy - 2.6, 11.4, 2.6, PALLA, 2.4, amp=1.0, cont=(0.2, 0.9), lvlfn=_palla,
           clip=lambda x, y: y >= hy - 3.6 or abs(x - hx - dx) > 6.2)
    for x in range(int(hx + dx - 11), int(hx + dx + 12)):                          # l'ala, caiguda pels costats
        if abs(x - hx - dx) > 8:
            fg.px(x, hy - 0.6, PALLA, 1.8)


def parpelles(fg, p, spec):
    """Els ulls mig closos (la parpella, a sobre de l'iris)."""
    if p.f == 'U' or spec.get('closed'):
        return
    hx, hy = p.head
    ey = int(hy + 0.5)
    S = spec['skin']
    if p.f == 'D':
        for x0 in (int(hx - 3.5), int(hx + 2.5)):
            fg.px(x0, ey - 1, S, 2.0)
            fg.px(x0 + 1, ey - 1, S, 2.0)
            for x in (x0, x0 + 1):
                v = fg.get(x, ey)
                if v and v[0] == EYE_W:
                    fg.px(x, ey, mix(EYE_W, (150, 110, 100), 0.5), 0)
        for x0 in (int(hx - 3.5), int(hx + 2.5)):
            fg.px(x0, ey - 1, (60, 34, 34), 0)
            fg.px(x0 + 1, ey - 1, (60, 34, 34), 0)
    else:
        ex = int(hx - 3.5)
        fg.px(ex, ey - 1, (60, 34, 34), 0)
        fg.px(ex - 1, ey - 1, (60, 34, 34), 0)


JOANET = {
    'skin': SKIN_TAN, 'legs': SKIN_TAN, 'top': RIU, 'shoes': SKIN_TAN, 'thin': 0.4, 'shoe_lvl': 2.4,
    'iris': (40, 30, 24), 'brow': (20, 14, 12), 'lip': (140, 70, 64), 'brow_dy': 1,
    'prop': Prop(tronc=1.04, cames=1.1, ample=0.96), 'stoop': 1,
    'hooks': {'hair': hooks(nomes_cara(parpelles), barret_pescador), 'face_q': en_q(parpelles), 'collar': iri_collar,
              'torso': hooks(skirt(RIU, 64, 2.0, top=44), cinyell(CORDO, 45.0, 2.6))},
}


# ═══════════════════════════════════════════════════════════════════════════
#  L'Ermessenda (la molinera, ~40 anys, enfarinada fins a les celles)
# ═══════════════════════════════════════════════════════════════════════════

def farina_cara(fg, p, spec):
    """La farina a la cara: unes clapes més clares al front i a les galtes."""
    if p.f == 'U':
        return
    hx, hy = p.head
    S = spec['skin']
    if p.f == 'D':
        for x, y in ((-3, -3), (-2, -3), (2, -3), (-5, 3), (-4, 4), (4, 3), (1, 7), (2, 6)):
            fg.shade(hx + x, hy + y, 1.2, S)
    else:
        for x, y in ((-3, -3), (-2, 3), (-1, 4), (-4, 7)):
            fg.shade(hx + x, hy + y, 1.2, S)


ERMESSENDA = {
    'skin': SKIN_OLIVA, 'legs': VERD_M, 'top': VERD_M, 'shoes': BOOT, 'thin': 0.2, 'forearm': SKIN_OLIVA,
    'iris': (50, 60, 40), 'brow': (230, 226, 214), 'lip': (140, 70, 66), 'brow_dy': -1,
    'prop': Prop(tronc=1.0, cames=1.02, ample=1.0),
    'hooks': {'hair': hooks(mocador(COFIA, HAIR_ENF, vora=True, lvlfn=_enfarinat), nomes_cara(farina_cara)), 'face_q': en_q(farina_cara),
              'arm': bracos_nus,
              'torso': hooks(skirt(VERD_M, 80, 2.4, top=44, lvlfn=_enfarinat),
                             davantal(FARINA, 33, 70, 5.0, 7.0, lvl=2.4, lvlfn=_enfarinat),
                             cinyell(CUIR, 44.0, 2.4, mats=(VERD_M, FARINA)))},
}


# ═══════════════════════════════════════════════════════════════════════════
#  Els canonges de Besalú: Gombau i Arnulf
# ═══════════════════════════════════════════════════════════════════════════

def tonsura(H):
    """La tonsura: la corona de cabell al voltant del cap i la closca pelada."""
    def hook(fg, p, spec):
        hx, hy = p.head
        if p.f == 'D':
            fg.ell(hx, hy - 1.6, 7.4, 7.2, H, 2.6, amp=1.6, cont=(0.2, 0.8), lvlfn=_brins,
                   clip=lambda x, y: (hy - 6.0 <= y <= hy - 3.4) or (abs(x - hx) > 5.8 and hy - 6 <= y <= hy + 1.4))
        elif p.f == 'L':
            fg.ell(hx + 0.8, hy - 1.6, 7.4, 7.0, H, 2.6, amp=1.6, cont=(0.2, 0.8), lvlfn=_brins,
                   clip=lambda x, y: (y >= hy - 5.4 and (x >= hx - 0.4 or y <= hy - 3.6)) and
                   not (x < hx + 2.6 and y > hy - 1.0) and y <= hy + 3)
        else:
            fg.ell(hx, hy - 0.8, 7.4, 7.8, H, 2.6, amp=1.6, cont=(0.2, 0.8), lvlfn=_brins,
                   clip=lambda x, y: y >= hy - 4.6 + ((x - hx) / 7) ** 2 * -1.0)
    return hook


def canonge(skin, H, prop, iris, brow, lip, thin=0.0, extra=None):
    return {
        'skin': skin, 'legs': NEGRE, 'top': NEGRE, 'shoes': SABATA_N, 'thin': thin,
        'iris': iris, 'brow': brow, 'lip': lip, 'prop': prop,
        'hooks': {'hair': hooks(tonsura(H), *(extra or [])), 'collar': vet_collar, 'arm': manigues(NEGRE, 2.8),
                  'torso': hooks(skirt(NEGRE, 81, 2.2, top=44), cordo(45.0, penja=False))},
    }


GOMBAU = canonge(SKIN_RUDDY, HAIR_GOMBAU, Prop(tronc=1.0, cames=1.06, ample=1.1), (50, 40, 34), (40, 36, 36),
                 (150, 76, 74), thin=-0.8)
GOMBAU['blush'] = True
ARNULF = canonge(SKIN_PALE, HAIR_ARNULF, Prop(tronc=1.06, cames=1.14, ample=0.9), (70, 100, 80), (120, 60, 34),
                 (150, 90, 90), thin=0.8)
ARNULF['brow_dy'] = -1


# ═══════════════════════════════════════════════════════════════════════════
#  Tot el repartiment
# ═══════════════════════════════════════════════════════════════════════════

# {id: {prefix de la roba: spec}}
PERSONES = {
    'iri': {'': IRI, 'Monjo': IRI_MONJO},
    'vet': {'': VET, 'Monjo': VET_MONJO},
    'ingilberga': {'': INGILBERGA},
    'gueraula': {'': GUERAULA},
    'ponc': {'': PONC},
    'sunifred': {'': SUNIFRED},
    'bonfill': {'': BONFILL},
    'ramon': {'': RAMON},
    'sanca': {'': SANCA},
    'joanet': {'': JOANET},
    'ermessenda': {'': ERMESSENDA},
    'gombau': {'': GOMBAU},
    'arnulf': {'': ARNULF},
}
