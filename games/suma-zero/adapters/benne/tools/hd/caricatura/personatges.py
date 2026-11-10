"""
Proposta A (caricatura), guardada per a un altre joc: personatges en pixel art caricaturesc (cartoon.py).

Mides fixes del joc (README): una persona fa **64 px** dels peus a dalt del cap, amb el **cap gran**
(uns 26 px, dues cinquenes parts de l'alçada). Fotograma de 48×68, peus a (24, 65).
Direccions: D (de cara), L (de perfil, mirant a l'esquerra; Benne fa el mirall per a R), U (d'esquena).
"""
import math

from hd.caricatura.cartoon import Fig

FW, FH = 48, 68
FEET = (24, 65)


# ─── Peces comunes ─────────────────────────────────────────────────────────

def leg(f, hip, foot, w, mat):
    """Cama com un quadrilàter de l'amplada `w` entre el maluc i el turmell."""
    (hx, hy), (fx, fy) = hip, foot
    a = math.atan2(fy - hy, fx - hx)
    ox, oy = -math.sin(a) * w / 2, math.cos(a) * w / 2
    f.poly([(hx - ox, hy - oy), (hx + ox, hy + oy), (fx + ox, fy + oy), (fx - ox, fy - oy)], mat)


def walk_phase(walk):
    """Fase del cicle de 6 fotogrames (0..2π), o None si està quieta."""
    return None if walk is None else walk / 6 * 2 * math.pi


# ─── Iri ───────────────────────────────────────────────────────────────────
# 24 anys, hacker. Dessuadora verd petroli amb caputxa, auriculars vermells grossos que no es treu
# mai, cabell negre esbullat amb serrell, texans i bambes blanques. Una mica encorbada.

def iri(facing, walk=None, talk=False, blink=False, auricular=2):
    """`auricular`: 2 (els dos), 1 (només el dret: l'esquerre és d'en Diu), 'mossegat' (l'esquerre amb forats)."""
    f = Fig(FW, FH)
    ph = walk_phase(walk)
    bob = 0 if ph is None else -round(abs(math.sin(ph)))
    if facing == 'L':
        _iri_side(f, ph, bob, talk, blink, auricular)
    else:
        _iri_front(f, facing == 'U', ph, bob, talk, blink, auricular)
    return f.render()


def _iri_front(f, back, ph, bob, talk, blink, auricular):
    # cames i bambes (sense balanceig)
    s = 0 if ph is None else math.sin(ph)
    lift_l, lift_r = (max(0, s) * 3, max(0, -s) * 3) if ph is not None else (0, 0)
    for x, lift in ((20, lift_l), (28, lift_r)):
        top = 47
        bottom = 61 - round(lift)
        f.rect(x - 2, top, x + 2, bottom, 'texans')
        f.ell(x - (0.5 if x < 24 else -0.5), bottom + 2.5, 4.5, 2.6, 'bamba')
        f.rect(x - 4, bottom + 4, x + 4, bottom + 4, 'bamba_sola', shade=False, light=False, tone=2)
    f.dy = bob
    # braços (darrere del cos a l'esquena, davant a la cara: els pinto abans i el cos els tapa una mica)
    sw = 0 if ph is None else round(math.sin(ph) * 2)
    for side, x0, d in ((-1, 14, sw), (1, 34, -sw)):
        sx = 17 if side < 0 else 31
        f.poly([(sx - 2, 31), (sx + 2, 31), (x0 + side * 1 + 1, 45 + d), (x0 + side * 1 - 2, 45 + d)], 'iri_dessuadora')
        f.ell(x0 + side * 0.5, 47 + d, 2.6, 2.6, 'pell')
    # cos: dessuadora ampla, amb la butxaca de cangur i el cordó de la caputxa
    f.poly([(17, 30), (31, 30), (33, 37), (32, 49), (16, 49), (15, 37)], 'iri_dessuadora')
    f.rect(16, 47, 32, 49, 'iri_dessuadora', tone=1)                       # cintura elàstica
    if not back:
        f.line(19, 41, 29, 41, 'iri_dessuadora', tone=1)                   # butxaca
        f.line(19, 41, 18, 46, 'iri_dessuadora', tone=1)
        f.line(29, 41, 30, 46, 'iri_dessuadora', tone=1)
        f.ell(24, 31, 6.5, 2.5, 'iri_dessuadora', line=True)               # coll de la caputxa
        f.px([(22, 32), (22, 33), (22, 34), (26, 32), (26, 33), (26, 34), (26, 35)], 'cable_gris', tone=2)  # cordons
    else:
        f.poly([(17, 30), (31, 30), (30, 40), (24, 43), (18, 40)], 'iri_dessuadora', line=True)  # caputxa a l'esquena
        f.line(20, 37, 24, 40, 'iri_dessuadora', tone=1)
        f.line(28, 37, 24, 40, 'iri_dessuadora', tone=1)
    # cap
    f.ell(24, 16.5, 13, 14, 'pell')
    if not back:
        # orelles tapades pels auriculars; cara
        ey = 18
        for ex in (19, 29):
            if blink:
                f.line(ex - 2, ey, ex + 2, ey, 'pell', tone=0)
            else:
                f.ell(ex + 0.5, ey, 3.2, 4, 'blanc_ull', shade=False, line=True)
                f.px([(ex, ey), (ex + 1, ey), (ex, ey + 1), (ex + 1, ey + 1)], 'pupil·la', tone=1)
                f.px([(ex, ey)], 'blanc_ull', tone=3)
        f.line(16, 13, 21, 12, 'cabell_negre', tone=1)                      # celles (preocupades)
        f.line(27, 12, 32, 13, 'cabell_negre', tone=1)
        f.px([(17, 23), (18, 23), (30, 23), (31, 23)], 'pell', tone=1)      # ulleres de no dormir
        f.px([(24, 21), (24, 22), (25, 22)], 'pell', tone=1)                # nas
        if talk:
            f.ell(24.5, 25.5, 2.5, 1.8, 'boca', shade=False, light=False, outline=False)
            f.px([(24, 26), (25, 26)], 'llengua', tone=2)
        else:
            f.line(22, 25, 26, 25, 'boca', tone=1)
            f.px([(27, 24)], 'boca', tone=1)                                # mig somriure nerviós
        f.px([(16, 25), (17, 25), (31, 25), (32, 25)], 'pell_rosa', tone=2)  # galtes
    # cabell negre esbullat: un casc amb puntes que surten de la silueta i un serrell tort
    if back:
        f.ell(24, 14, 13.5, 13.5, 'cabell_negre', line=True)
        f.poly([(12, 17), (36, 17), (35, 27), (30, 30), (24, 28), (18, 30), (13, 27)], 'cabell_negre')
    else:
        f.ell(24, 9, 13.5, 8, 'cabell_negre', line=True)
        f.poly([(11, 8), (16, 8), (15, 16), (12, 22), (10, 14)], 'cabell_negre', line=True)
        f.poly([(37, 8), (32, 8), (33, 16), (36, 22), (38, 14)], 'cabell_negre', line=True)
        # serrell: tres flocs que tapen mig front, un de més llarg sobre la cella dreta
        f.poly([(14, 10), (20, 11), (17, 15)], 'cabell_negre', line=True)
        f.poly([(18, 10), (26, 11), (22, 16)], 'cabell_negre', line=True)
        f.poly([(24, 10), (34, 10), (31, 15), (29, 12), (27, 14)], 'cabell_negre', line=True)
    # puntes rebels a dalt
    for pts in ([(14, 5), (12, 0), (18, 3)], [(19, 3), (20, -2), (24, 2)], [(26, 2), (31, -1), (30, 4)], [(31, 4), (37, 2), (34, 7)]):
        f.poly(pts, 'cabell_negre')
    # auriculars: diadema i dues copes
    for i in range(15):
        a = math.pi * i / 14
        f.px([(round(24 - math.cos(a) * 14), round(14 - math.sin(a) * 13))], 'negre_suau', tone=2)
    cups = []
    if auricular == 2 or back:
        cups = [10, 38]
    elif auricular == 1:
        cups = [38]
    else:
        cups = [10, 38]
    for cx in cups:
        f.ell(cx, 18, 3.4, 5, 'auricular', line=True)
        f.px([(cx, 15), (cx, 16)], 'auricular', tone=3)
    if auricular == 'mossegat' and not back:
        f.px([(9, 16), (11, 19), (9, 21)], 'negre_suau', tone=0)          # forats de dent
    f.dy = 0


def _iri_side(f, ph, bob, talk, blink, auricular):
    hip = (24, 47)
    s = 0 if ph is None else math.sin(ph)
    swing = s * 6
    # cama del fons, després la del davant
    for d, mat_tone in ((-1, True), (1, False)):
        fx = hip[0] + d * swing
        fy = 61 - (max(0, d * math.cos(ph)) * 2 if ph is not None else 0)
        leg(f, hip, (fx, fy), 6, 'texans')
        f.ell(fx - 2, fy + 2.5, 5, 2.6, 'bamba')
        f.rect(round(fx) - 7, round(fy) + 4, round(fx) + 2, round(fy) + 4, 'bamba_sola', shade=False, light=False, tone=2)
    f.dy = bob
    # cos de perfil, una mica encorbat cap endavant
    f.poly([(20, 30), (29, 30), (31, 37), (30, 49), (18, 49), (18, 37)], 'iri_dessuadora')
    f.rect(18, 47, 30, 49, 'iri_dessuadora', tone=1)
    f.poly([(26, 28), (32, 29), (33, 37), (28, 35)], 'iri_dessuadora', line=True)   # caputxa a l'esquena
    # braç del davant, que balanceja
    hx = 24 - s * 4
    f.poly([(22, 32), (27, 32), (hx + 2, 45), (hx - 2, 45)], 'iri_dessuadora', line=True)
    f.ell(hx, 47, 2.6, 2.6, 'pell')
    # cap (de perfil: el nas cap a l'esquerra)
    f.ell(24, 16.5, 12, 14, 'pell')
    f.poly([(13, 17), (9, 21), (13, 23)], 'pell')                               # nas
    if blink:
        f.line(15, 18, 18, 18, 'pell', tone=0)
    else:
        f.ell(17.5, 18, 2.8, 3.8, 'blanc_ull', shade=False, line=True)
        f.px([(15, 18), (15, 19), (16, 18), (16, 19)], 'pupil·la', tone=1)
    f.line(15, 13, 20, 12, 'cabell_negre', tone=1)
    f.px([(19, 23), (20, 23)], 'pell', tone=1)
    if talk:
        f.ell(15.5, 25.5, 2, 1.6, 'boca', shade=False, light=False, outline=False)
    else:
        f.line(14, 25, 17, 25, 'boca', tone=1)
    f.px([(19, 25), (20, 25)], 'pell_rosa', tone=2)
    # cabell: de la clatellera al serrell
    f.ell(28, 11, 11, 9.5, 'cabell_negre', line=True)
    f.poly([(28, 14), (38, 12), (37, 25), (32, 30), (29, 25)], 'cabell_negre', line=True)
    f.poly([(14, 8), (20, 4), (26, 7), (23, 10), (20, 9), (17, 13), (13, 11)], 'cabell_negre', line=True)
    for pts in ([(17, 4), (17, -1), (22, 2)], [(23, 2), (27, -2), (28, 3)], [(30, 3), (36, 1), (34, 6)], [(36, 8), (41, 8), (37, 12)]):
        f.poly(pts, 'cabell_negre')
    # auriculars: la copa del costat i la diadema
    for i in range(11):
        a = math.pi * (0.15 + 0.7 * i / 10)
        f.px([(round(28 + math.cos(a) * 3), round(14 - math.sin(a) * 13))], 'negre_suau', tone=2)
    if auricular != 1:
        f.ell(28, 18, 4, 5.2, 'auricular', line=True)
        f.px([(27, 16), (27, 17)], 'auricular', tone=3)
        if auricular == 'mossegat':
            f.px([(29, 17), (27, 20)], 'negre_suau', tone=0)
    else:
        f.ell(28, 18, 2, 2.5, 'pell', line=True)                              # l'orella, sense auricular
    f.dy = 0


# ─── Diu, el gat ───────────────────────────────────────────────────────────
# Gat gris tigrat amb pitet blanc, assegut, ulls verds enormes. Intocable. Fotograma de 28×24.

GW, GH = 28, 24


def diu(cua=0, parpelleja=False, boca=False, mira='D'):
    """Assegut de cara. `cua`: fase de la cua (0..3)."""
    f = Fig(GW, GH)
    # cua que es mou
    tx = [20, 22, 23, 22][cua % 4]
    f.poly([(17, 21), (20, 20), (tx + 3, 14), (tx + 2, 10), (tx, 12), (tx + 1, 15)], 'gat')
    # cos assegut
    f.ell(13, 17, 7.5, 6.5, 'gat')
    f.ell(13, 18, 3.5, 4.5, 'gat_clar', shade=False)                           # pitet
    f.ell(9, 22, 2.5, 1.5, 'gat_clar')                                       # potes
    f.ell(16, 22, 2.5, 1.5, 'gat_clar')
    # cap gran
    f.ell(13, 8, 7.5, 6.5, 'gat')
    f.poly([(6, 5), (7, -1), (11, 3)], 'gat', line=True)                     # orelles
    f.poly([(20, 5), (19, -1), (15, 3)], 'gat', line=True)
    f.px([(8, 2), (8, 3), (18, 2), (18, 3)], 'rosa_nas', tone=1)
    f.px([(11, 3), (13, 2), (15, 3)], 'gat', tone=1)                          # ratlles del front
    for ex in (10, 16):
        if parpelleja:
            f.line(ex - 1, 8, ex + 1, 8, 'gat', tone=0)
        else:
            f.ell(ex + 0.5, 8, 2.2, 2.4, 'gat_ull', shade=False, line=True)
            px = ex + (0 if mira == 'D' else (-1 if mira == 'L' else 1))
            f.px([(px, 7), (px, 8), (px, 9)], 'pupil·la', tone=0)
    f.px([(13, 11)], 'rosa_nas', tone=2)
    if boca:
        f.px([(12, 12), (13, 13), (14, 12)], 'boca', tone=1)
    else:
        f.px([(12, 12), (14, 12)], 'gat', tone=0)
    f.px([(5, 10), (6, 11), (21, 10), (20, 11)], 'gat_clar', tone=3)          # bigotis
    return f.render()
