"""
**El dibuix pla de sempre** de la sala (font de les textures de bcmu_moll.py, que és en 3D).

El moll de càrrega del BCMU (Escena 4b, l'Iri) a 640×360: la composició de hd/rooms/bcmu_moll.py ×4/3, dibuixada
de nou.
  - la part de servei de l'edifici: bloc de formigó pintat, bigues i fluorescents, terra de formigó amb línies
    grogues; la casa només s'hi nota en el rètol blau marí i or «MOLL DE CÀRREGA» i en el logo de les furgonetes;
  - a l'esquerra, la persiana del moll enrotllada: fora, el matí de Ginebra (cel clar, un edifici veí i el llac
    al fons, amb el Jet d'Eau), i dues furgonetes blindades recolzades al moll, de cul, amb el logo del BCMU;
  - al fons, tres tècnics de manteniment de la Rius amb granota, mirant el mòbil (subcontractats d'una
    subcontracta);
  - un toro aparcat amb un palet de caixes a les forques i el llum taronja giratori;
  - el rellotge de fitxar amb el casiller de targetes;
  - la màquina de cafè vella, amb el cop de puny marcat al costat;
  - l'ascensor de servei d'acer, amb el lector de targetes i l'adhesiu «NOMÉS PERSONAL AUTORITZAT».
Animació: `llum_toro` (el llum giratori del toro, i el fluorescent del mig que fa un parpelleig).
"""
import hd640  # noqa: F401  (posa la llibreria de dibuix a 640×360)

import math

from PIL import Image

from hd.pix import Light, Canvas, W, H, hr
from hd.rooms.comu import obox, outline, text, text_width, _diff, PLASTIC, SHEET, RED
from hd.rooms.pis_cuina import outline_poly
from hd.rooms.bcmu_moll import (BLOCKW, FLOORC, STEEL, SKYD, LAKE, HILL, STONE, YELH, FORK, COFFEE, PALLET,  # noqa: F401
                                BOXC, TYRE, OVERALL, CAPM)
from hd.characters import BOOT, SKIN_PALE, SKIN_VET, SKIN_FOSCA, SKIN_RUDDY, HAIR_BROWN, HAIR_COPPER
from hd.personatges import hair_cap
from hd640.rooms.bcmu import CONCB, NAVYB, BRASS, logo
import hd640.draw_characters as DC
import hd.characters as C

Canvas1x = Canvas                                   # (a 1×, com la sala en 3D)

FLOOR_Y = 200

LIGHT = Light(ambient=-0.25, vignette=(67, 40), floor_fade=(256, 37))
LIGHT.point(333, 5, r=267, k=2.2, squash=0.8, power=1.3)             # fluorescent del mig
LIGHT.point(560, 5, r=227, k=1.8, squash=0.8, power=1.4)             # fluorescent de l'ascensor
LIGHT.point(127, 147, r=227, k=1.6, squash=1.0, power=1.5)           # el dia, per la persiana

OPEN = (16, 35, 237, FLOOR_Y)          # el forat de la persiana
BEACON = (365, 123)                    # el llum giratori del toro
TUBES = (280, 507)                     # els dos fluorescents


# ─── Paret, sostre, terra ──────────────────────────────────────────────────

def wall(cv):
    """Bloc de formigó pintat de gris clar; a baix, sòcol fosc i franja de seguretat groga i negra."""
    for y in range(0, FLOOR_Y):
        row = y // 12
        off = 16 if row % 2 else 0
        for x in range(W):
            bx = (x + off) // 32
            joint = (y % 12 == 11) or ((x + off) % 32 == 31)
            n = (hr(x // 2, y // 2, 11) - 0.5) * 0.3 + (hr(bx, row, 3) - 0.5) * 0.25
            pore = 0.5 if hr(x, y, 12) > 0.985 else 0                    # els porus del bloc
            lip = 0.4 if (y % 12 == 0) and not joint else 0              # el cantell de dalt del bloc, una mica més clar
            cv.put(x, y, BLOCKW, (3.0 if joint else 4.3 + n - pore + lip) - (0.6 if y > 171 else 0))
    # algun bloc escantonat
    for i in range(9):
        cx, cy = int(hr(i, 13) * W), 36 + int(hr(i, 14) * 120)
        cy = cy - cy % 12 + 11
        cx = cx - (cx + (16 if (cy // 12) % 2 else 0)) % 32 + 31
        for k in range(3):
            cv.hline(cx - 2 + k, cx + 1, cy - 2 + k, BLOCKW, 3.0)
    # franja de perill a la base de la paret
    for y in range(176, 187):
        for x in range(W):
            stripe = ((x + y) // 8) % 2 == 0
            cv.put(x, y, YELH if stripe else TYRE, (3.0 if stripe else 2.0) + (0.6 if y == 176 else 0)
                   - (hr(x // 3, y, 15) > 0.9) * 1.0)                      # la pintura rascada pels carros
    cv.rect(0, 187, W - 1, FLOOR_Y - 1, CONCB, 2.0)
    cv.hline(0, W - 1, 187, CONCB, 2.8)
    cv.hline(0, W - 1, FLOOR_Y, CONCB, 0.6)


def ceiling(cv):
    """Bigues d'acer i canonades a la vista, amb dos fluorescents."""
    cv.rect(0, 0, W - 1, 11, CONCB, 2.6)
    for x in range(0, W, 107):
        cv.rect(x, 0, x + 7, 19, STEEL, lambda xx, yy, x=x: 3.0 + (1.0 if xx == x + 1 else 0) - (1.0 if xx >= x + 6 else 0))
        cv.hline(x, x + 7, 19, STEEL, 1.2)
        for ry in (3, 15):                                               # reblons de la biga
            cv.put(x + 3, ry, STEEL, 5.0)
    cv.rect(0, 12, W - 1, 15, STEEL, lambda x, y: 3.2 + (1.0 if y == 12 else 0) - (0.8 if y == 15 else 0))
    cv.rect(0, 21, W - 1, 24, NAVYB, lambda x, y: 3.0 + (1.2 if y == 21 else 0) - (0.8 if y == 24 else 0))  # canonada de la casa
    for x in range(40, W, 96):                                           # les abraçadores de la canonada
        cv.rect(x, 19, x + 2, 25, STEEL, lambda xx, yy, x=x: 3.4 + (0.8 if xx == x else 0))
    for fx in TUBES:
        tube(cv, fx)


def tube(cv, x0, on=True):
    """Un fluorescent: la regleta i el tub, de 80 px."""
    for hx in (x0 + 8, x0 + 72):                                         # les cadenetes
        cv.vline(hx, 25, 26, STEEL, 2.4)
    obox(cv, x0 - 3, 27, x0 + 83, 32, STEEL, 3.4)
    col = (236, 246, 255) if on else (120, 128, 136)
    cv.hline(x0, x0 + 80, 31, [col], 0, lit=0)
    cv.hline(x0 + 1, x0 + 79, 30, [tuple(round(c * 0.82) for c in col)], 0, lit=0)
    for ex in (x0, x0 + 80):                                             # els capçals
        cv.put(ex, 30, STEEL, 2.0)
        cv.put(ex, 31, STEEL, 2.0)
    if on:
        cv.glow(x0 + 40, 33, 40, (220, 236, 255), 0.22)


def floor(cv):
    """Formigó amb taques d'oli, junts de dilatació i línies grogues de pas."""
    for y in range(FLOOR_Y + 1, H):
        for x in range(W):
            n = (hr(x // 3, y // 2, 7) - 0.5) * 0.45 + (hr(x, y, 8) - 0.5) * 0.12
            joint = x % 128 == 0
            cv.put(x, y, FLOORC, (2.2 if joint else 3.6 + n))
    for i in range(8):                                                   # taques d'oli
        cx = 53 + int(hr(i, 1) * 533)
        cy = 213 + int(hr(i, 2) * 48)
        cv.darken(cx - 11, cy - 3, cx + 11, cy + 3,
                  lambda x, y, cx=cx, cy=cy: 0.5 * max(0, 1 - math.hypot((x - cx) / 11, (y - cy) / 3.2)))
        cv.put(cx - 3, cy - 1, FLOORC, 5.0)                              # la brillantor de l'oli
    # la vora del moll (davant la persiana): franja groga i negra
    for y in range(FLOOR_Y + 1, FLOOR_Y + 7):
        for x in range(OPEN[0], OPEN[2] + 1):
            stripe = ((x - y) // 7) % 2 == 0
            cv.put(x, y, YELH if stripe else TYRE, (3.4 if stripe else 2.0) - (0.8 if y == FLOOR_Y + 6 else 0))
    # línies grogues del passadís de vianants
    for y in (232, 272):
        cv.rect(0, y, W - 1, y + 2, YELH, lambda x, yy: 3.2 + (0.4 if yy == y else 0) - (0.9 if hr(x // 4, yy, 9) > 0.88 else 0))
    for x in range(267, W, 29):                                          # zebra davant l'ascensor
        cv.poly([(x, 211), (x + 11, 211), (x + 5, 227), (x - 5, 227)], YELH,
                lambda xx, yy: 2.6 - (0.8 if hr(xx // 2, yy // 2, 10) > 0.85 else 0))


# ─── La persiana oberta i les furgonetes ───────────────────────────────────

def outside(cv):
    """Fora: el matí de Ginebra (cel, un edifici de pedra, el llac amb el Jet d'Eau i les muntanyes)."""
    x0, y0, x1, y1 = OPEN
    for y in range(y0, y1 + 1):
        for x in range(x0, x1 + 1):
            cv.put(x, y, SKYD, 5.2 - (y - y0) / 35 + (hr(x // 2, y // 2, 30) - 0.5) * 0.1, lit=0)
    for cx, cy, w in ((60, 52, 30), (190, 46, 22)):                      # uns núvols prims
        for x in range(cx - w, cx + w):
            t = abs(x - cx) / w
            for y in range(cy - round(3 * (1 - t)), cy + 1):
                cv.put(x, y, SKYD, 5.6, lit=0)
    for x in range(x0, x1 + 1):                                          # muntanyes, en dos plans
        h2 = 92 + int(math.sin(x * 0.02 + 1) * 6 + math.sin(x * 0.07) * 2)
        for y in range(h2, 123):
            cv.put(x, y, HILL, 2.4 - (y - h2) / 40, lit=0)
        h = 99 + int(math.sin(x * 0.0375) * 7 + math.sin(x * 0.0975) * 4)
        for y in range(h, 123):
            cv.put(x, y, HILL, 1.6 - (y - h) / 40, lit=0)
    cv.rect(x0, 123, x1, 136, LAKE, lambda x, y: 2.6 + (0.8 if (x + y * 3) % 23 == 0 else 0) - (124 - y) * 0.0, lit=0)
    cv.hline(x0, x1, 123, LAKE, 3.4, lit=0)
    # el Jet d'Eau, al fons del llac
    jx = 134
    for y in range(100, 124):
        cv.put(jx, y, SKYD, 5.4, lit=0)
        if y > 108:
            cv.put(jx + 1, y, SKYD, 4.6, lit=0)
    cv.put(jx + 1, 100, SKYD, 5.0, lit=0)
    cv.put(jx + 2, 101, SKYD, 4.4, lit=0)
    # l'edifici veí, de pedra, amb finestres
    obox(cv, 147, 59, x1, 139, STONE, 3.0, lit=0)
    cv.rect(148, 60, x1 - 1, 62, STONE, 4.0, lit=0)                      # la cornisa
    cv.hline(148, x1 - 1, 63, STONE, 1.6, lit=0)
    for yy in range(70, 139, 17):                                        # les filades de carreus
        cv.hline(148, x1 - 1, yy - 2, STONE, 2.6, lit=0)
    for r in range(4):
        for c in range(5):
            wx, wy = 155 + c * 16, 67 + r * 17
            cv.rect(wx, wy, wx + 8, wy + 11, LAKE, lambda x, y, wx=wx, wy=wy: 1.4 + (1.2 if x - wx + y - wy < 4 else 0), lit=0)
            cv.vline(wx + 4, wy, wy + 11, STONE, 3.0, lit=0)             # el muntant
            cv.hline(wx, wx + 8, wy + 5, STONE, 3.0, lit=0)
            cv.hline(wx - 1, wx + 9, wy + 11, STONE, 4.4, lit=0)         # l'ampit
            if hr(r, c, 31) > 0.75:                                      # alguna persiana mig abaixada
                cv.rect(wx, wy, wx + 8, wy + 4, STONE, 2.0, lit=0)
    # el pati de fora (asfalt)
    for y in range(139, y1 + 1):
        for x in range(x0, x1 + 1):
            cv.put(x, y, FLOORC, 3.2 + (hr(x // 2, y, 4) - 0.5) * 0.4, lit=0)
    cv.hline(x0, x1, 139, FLOORC, 2.0, lit=0)


def shutter(cv):
    """El marc de la persiana i la persiana enrotllada a dalt."""
    x0, y0, x1, y1 = OPEN
    cv.rect(x0 - 8, y0 - 16, x1 + 8, y0 - 1, STEEL, lambda x, y: 3.2 + ((y - y0) % 4 == 0) * 0.8 - ((y - y0) % 4 == 2) * 0.6)  # el rotlle
    outline(cv, x0 - 8, y0 - 16, x1 + 8, y0 - 1, STEEL)
    for y in range(y0, y0 + 7):                                          # les últimes lamel·les penjant
        cv.hline(x0, x1, y, STEEL, 3.8 if y % 2 else 2.4)
    cv.hline(x0, x1, y0 + 7, STEEL, 1.2)
    for hx in (x0 + 70, x1 - 70):                                        # les nanses de la persiana
        cv.rect(hx, y0 + 2, hx + 8, y0 + 4, STEEL, 5.0)
    for sx in (x0 - 8, x1 + 1):                                          # les guies
        cv.rect(sx, y0 - 1, sx + 6, y1, STEEL, lambda x, y, sx=sx: 3.0 + (1.0 if x == sx + 1 else 0) - (0.8 if x >= sx + 6 else 0))
        cv.vline(sx + 3, y0, y1, STEEL, 1.6)                             # la ranura
        for by in range(y0 + 10, y1 - 40, 24):                           # els cargols
            cv.put(sx + 1, by, STEEL, 5.0)
    # bandes de perill a les guies
    for sx in (x0 - 8, x1 + 1):
        for y in range(y1 - 40, y1):
            if (y // 5) % 2 == 0:
                cv.rect(sx + 1, y, sx + 5, y, YELH, 3.2)


def van(cv, x0, y0, x1, y1):
    """Una furgoneta blindada vista de darrere: caixa blau marí, franja d'or, logo, portes i finestretes."""
    mid = (x0 + x1) // 2
    # el sostre i la caixa
    obox(cv, x0, y0, x1, y1 - 19, NAVYB, 3.4, top=1.2, side=-1.0)
    cv.rect(x0 + 1, y0 + 1, x1 - 1, y0 + 4, NAVYB, 4.8)
    cv.hline(x0 + 1, x1 - 1, y0 + 5, NAVYB, 2.6)
    for gx in range(x0 + 8, x1 - 6, 10):                                 # la baca: barres del sostre
        cv.vline(gx, y0 - 2, y0, NAVYB, 3.6)
    cv.hline(x0 + 6, x1 - 6, y0 - 3, NAVYB, 4.2)
    # les dues portes del darrere
    cv.vline(mid, y0 + 8, y1 - 20, NAVYB, 0.6)
    cv.vline(mid + 1, y0 + 8, y1 - 20, NAVYB, 4.0)
    for dx0, dx1 in ((x0 + 4, mid - 3), (mid + 3, x1 - 4)):
        outline(cv, dx0, y0 + 8, dx1, y1 - 24, NAVYB)
        obox(cv, dx0 + 4, y0 + 12, dx1 - 4, y0 + 24, [(10, 14, 22), (30, 40, 56), (70, 90, 110), (130, 150, 168)], 1.6)  # finestreta blindada
        for gy in range(y0 + 14, y0 + 23, 2):                            # la reixa de la finestreta
            for gx in range(dx0 + 6 + (gy // 2) % 2, dx1 - 5, 2):
                cv.put(gx, gy, [(10, 14, 22), (30, 40, 56)], 1.0)
        cv.line(dx0 + 5, y0 + 13, dx0 + 11, y0 + 13, [(200, 220, 230)], 0)
        for hy in (y0 + 30, y1 - 32):                                    # les frontisses blindades
            hx = dx0 + 1 if dx0 < mid else dx1 - 3
            cv.rect(hx, hy, hx + 2, hy + 5, NAVYB, 1.8)
    # la franja d'or i el logo
    cv.rect(x0 + 2, y0 + 32, x1 - 2, y0 + 35, BRASS, lambda x, y: 4.0 + (0.6 if y == y0 + 32 else 0) - (0.8 if y == y0 + 35 else 0))
    cv.disc(mid, y0 + 47, 12, 12, NAVYB, 2.0)
    logo(cv, mid, y0 + 47, k=2.0, lvl=4.4)
    # maneta i pany
    cv.rect(mid - 7, y0 + 63, mid - 3, y0 + 64, [(120, 128, 136), (180, 186, 192), (220, 224, 228)], 2.0)
    cv.rect(mid + 3, y0 + 63, mid + 7, y0 + 64, [(120, 128, 136), (180, 186, 192), (220, 224, 228)], 2.0)
    cv.put(mid - 5, y0 + 67, STEEL, 1.0)                                 # el pany
    # pilots
    for px in (x0 + 1, x1 - 5):
        cv.rect(px, y1 - 35, px + 4, y1 - 24, RED, lambda x, y: 4.0 + (0.8 if y < y1 - 31 else 0))
        cv.hline(px, px + 4, y1 - 29, RED, 2.0)
        cv.glow(px + 2, y1 - 29, 7, (255, 60, 50), 0.3)
    # para-xocs, matrícula i rodes
    cv.rect(x0 - 1, y1 - 19, x1 + 1, y1 - 12, STEEL, lambda x, y: 2.6 + (1.0 if y == y1 - 19 else 0) - (0.6 if y == y1 - 12 else 0))
    obox(cv, mid - 12, y1 - 18, mid + 12, y1 - 12, [(140, 140, 140), (200, 200, 196), (232, 232, 226), (250, 250, 246)], 3.0)
    cv.rect(mid - 11, y1 - 17, mid - 8, y1 - 13, [(200, 30, 30)], 0, lit=0)   # l'escut de Ginebra, vermell
    cv.flat(mid - 10, y1 - 15, (240, 220, 80))
    text(cv, 'GE', mid - 6, y1 - 17, [(30, 30, 40)], 0, flat=(30, 30, 40))
    cv.rect(mid + 1, y1 - 16, mid + 10, y1 - 14, [(60, 60, 70)], 0)
    for wx in (x0 + 3, x1 - 15):
        cv.rect(wx, y1 - 12, wx + 12, y1, TYRE, lambda x, y: 1.6 + (0.8 if y == y1 - 12 else 0) + (0.5 if (x + y) % 4 == 0 else 0))
    cv.darken(x0 - 3, y1, x1 + 3, y1 + 4, 0.6)
    cv.darken(x0 + 4, y1 - 11, x1 - 4, y1, 0.4)


# ─── Els tècnics de la Rius ────────────────────────────────────────────────

def _tecnic(skin, hair, cap=True):
    hk = hair_cap(hair)
    if cap:
        def hook(fg, p, spec):
            hk(fg, p, spec)
            hx, hy = p.head
            fg.ell(hx + (1.0 if p.f == 'L' else 0), hy - 5.6, 7.4, 3.2, CAPM, 2.6, amp=1.6, cont=(0.2, 1.0))
            if p.f == 'L':
                fg.ell(hx - 5.0, hy - 3.4, 4.0, 1.2, CAPM, 1.8, amp=1.0)
        return {'skin': skin, 'legs': OVERALL, 'top': OVERALL, 'shoes': BOOT, 'hooks': {'hair': hook}}
    return {'skin': skin, 'legs': OVERALL, 'top': OVERALL, 'shoes': BOOT, 'hooks': {'hair': hk}}


TECNICS = [
    # (spec, direcció, peus x, mirall)
    (_tecnic(SKIN_RUDDY, HAIR_BROWN), 'U', 253, False),
    (_tecnic(SKIN_PALE, HAIR_COPPER, cap=False), 'L', 273, True),
    (_tecnic(SKIN_FOSCA, HAIR_BROWN), 'L', 295, False),
]
TK = 0.66      # al fons: més petits
FEET_Y = 200


def _small_side_face(fg, p, spec):
    """La cara de perfil a la mida petita: l'ull, la cella, l'orella i la boca, d'un píxel real."""
    hx, hy = p.head
    S = spec['skin']
    f = DC.f
    ex, ey = round(f(hx - 3.0 + fg.ox)), round(f(hy + 0.5 + fg.oy))
    fg.rpx(ex, ey, spec.get('eye', (34, 22, 30)), 0)
    fg.rpx(ex - 1, ey, C.EYE_W, 0)
    fg.rpx(ex - 1, ey - 2, spec.get('brow', (40, 24, 28)), 0)
    fg.rpx(ex, ey - 2, spec.get('brow', (40, 24, 28)), 0)
    fg.ell(int(hx + 2.5) + 0.5, int(hy + 0.5) + 2, 1.4, 2.0, S, 2.6, amp=1.2)
    fg.rshade(round(f(hx + 3.0 + fg.ox)), ey + 2, -1.0, S)
    mx, my = round(f(hx - 5.0 + fg.ox)), round(f(hy + 5.0 + fg.oy))
    fg.rpx(mx, my, spec.get('lip', C.LIP), 0)
    fg.rpx(mx + 1, my, C.mix(spec.get('lip', C.LIP), C.MOUTH, 0.5), 0)


def _person_small(spec, facing):
    """La persona de hd.characters dibuixada directament a ×4/3·TK (no reduïda), amb la cara a la seva mida.
    Torna el fotograma i els peus."""
    old = DC.K
    DC.install()
    face = C.side_face
    DC.K = old * TK
    C.side_face = _small_side_face
    try:
        img = C.person(spec, facing)
        feet = (round(DC.f(25)), round(DC.f(83)))
    finally:
        DC.K = old
        C.side_face = face
    return img, feet


def tecnics(cv):
    layer = Image.new('RGBA', (W, H), (0, 0, 0, 0))
    for spec, f, fx, mirror in TECNICS:
        fig, (px, py) = _person_small(spec, f)
        if mirror:
            fig = fig.transpose(Image.FLIP_LEFT_RIGHT)
            px = fig.width - 1 - px
        layer.alpha_composite(fig, (fx - px, FEET_Y - py))
    # una mica més foscos: són al fons, lluny del fluorescent
    px = layer.load()
    for y in range(H):
        for x in range(W):
            r, g, b, a = px[x, y]
            if a:
                px[x, y] = (int(r * 0.82), int(g * 0.84), int(b * 0.9), a)
    for spec, f, fx, mirror in TECNICS:
        cv.darken(fx - 9, FEET_Y - 1, fx + 9, FEET_Y + 2, 0.5)
    # una caixa d'eines vermella a terra, darrere d'ells
    obox(cv, 235, 191, 248, 200, RED, 3.0)
    cv.hline(236, 247, 194, RED, 1.6)
    cv.rect(239, 187, 244, 188, STEEL, 3.4)
    cv.vline(239, 188, 190, STEEL, 2.6)
    cv.vline(244, 188, 190, STEEL, 2.6)
    cv.blit(layer)
    # els mòbils: rectangles de llum blavosa a les mans
    for mx, my in ((281, 165), (288, 165)):
        cv.rect(mx, my, mx + 1, my + 3, [(170, 220, 255)], 0, lit=0)
        cv.flat(mx, my, (220, 244, 255))
        cv.glow(mx, my + 1, 7, (150, 210, 255), 0.35)


# ─── El toro, el palet i el rellotge de fitxar ─────────────────────────────

def forklift(cv, beacon_on=0):
    """Un toro taronja aparcat de perfil (mirant a l'esquerra), amb un palet de caixes a les forques."""
    # el pal de les forques: dos perfils amb la cadena entre mig
    cv.rect(333, 115, 337, 197, STEEL, lambda x, y: 2.8 + (1.0 if x == 334 else 0) - (0.6 if x == 337 else 0))
    cv.rect(341, 115, 345, 197, STEEL, lambda x, y: 2.6 + (1.0 if x == 342 else 0) - (0.6 if x == 345 else 0))
    for y in range(117, 190, 2):
        cv.put(339, y, STEEL, 1.6 + (y % 4 == 1) * 1.6)
    cv.rect(333, 113, 345, 115, STEEL, 3.6)
    # les forques i el palet
    cv.rect(315, 195, 339, 197, STEEL, lambda x, y: 3.4 + (0.8 if y == 195 else 0))
    obox(cv, 309, 187, 336, 193, PALLET, 3.2)
    for px in (311, 321, 331):                                           # els daus del palet
        cv.rect(px, 190, px + 3, 192, PALLET, 1.8)
    for i, (bx0, by0, bx1, by1) in enumerate(((311, 163, 324, 186), (325, 165, 336, 186), (315, 144, 332, 162))):
        obox(cv, bx0, by0, bx1, by1, BOXC, 3.4 - i * 0.2)
        my = (by0 + by1) // 2
        cv.hline(bx0 + 1, bx1 - 1, my, [(200, 180, 120), (230, 214, 160)], 0.6)   # cinta
        cv.hline(bx0 + 1, bx1 - 1, my + 1, [(200, 180, 120), (230, 214, 160)], 0.2)
        cv.vline(bx1 - 1, by0 + 1, by1 - 1, BOXC, 2.2)
    # una etiqueta d'enviament a la caixa de baix
    cv.rect(314, 177, 320, 182, SHEET, 4.4)
    for k in range(3):
        cv.hline(315, 319 - k, 178 + k * 1, [(60, 60, 70)], 0)
    text(cv, 'BCMU', 316, 149, [(40, 30, 70)], 0, flat=(40, 30, 70))
    # el cos
    body = [(344, 144), (384, 144), (395, 160), (395, 189), (344, 189)]
    cv.poly(body, FORK, lambda x, y: 3.4 + (1.0 if y < 149 else 0) - (x - 344) * 0.015 + (hr(x // 2, y // 2, 40) - 0.5) * 0.15)
    outline_poly(cv, body, FORK)
    cv.line(385, 146, 393, 158, FORK, 5.0)                               # el cantell il·luminat
    cv.hline(346, 383, 176, FORK, 2.0)                                   # la junta del capó
    # la cabina (estructura de protecció i seient)
    for cx in (349, 389):
        cv.rect(cx, 112, cx + 2, 144, PLASTIC, lambda x, y, cx=cx: 2.6 + (0.8 if x == cx else 0))
    cv.rect(349, 109, 392, 113, PLASTIC, lambda x, y: 2.8 + (0.8 if y == 109 else 0))
    for gx in range(354, 389, 6):                                        # la reixa del sostre
        cv.vline(gx, 110, 112, PLASTIC, 1.4)
    obox(cv, 368, 128, 384, 144, PLASTIC, 2.0)                           # el seient
    cv.rect(370, 130, 382, 131, PLASTIC, 3.0)
    cv.line(357, 139, 355, 123, PLASTIC, 2.6)                            # el volant
    cv.rect(349, 121, 360, 123, PLASTIC, lambda x, y: 3.0 + (0.8 if y == 121 else 0))
    cv.line(362, 141, 364, 132, PLASTIC, 3.2)                            # les palanques
    cv.line(365, 141, 367, 133, PLASTIC, 3.2)
    cv.put(364, 131, RED, 4.0)
    cv.put(367, 132, [(240, 200, 60)], 0)
    # el contrapès i les rodes
    obox(cv, 384, 157, 396, 189, FORK, 2.6)
    for gy in range(162, 186, 4):                                        # les ranures del contrapès
        cv.hline(387, 393, gy, FORK, 1.6)
    for wx, r in ((357, 9), (385, 8)):
        cv.disc(wx, 192, r, r, TYRE, lambda nx, ny: 2.2 - ny * 0.6 + (0.4 if abs(nx * nx + ny * ny - 0.6) < 0.08 else 0))
        cv.disc(wx, 192, 3.2, 3.2, STEEL, lambda nx, ny: 4.0 - nx - ny)
        for a in range(0, 360, 90):                                      # les femelles
            cv.put(round(wx + math.cos(math.radians(a + 45)) * 2), round(192 + math.sin(math.radians(a + 45)) * 2), STEEL, 1.6)
    cv.darken(344, 200, 397, 204, 0.55)
    text(cv, 'NO TOCAR', 352, 165, [(40, 20, 6)], 0, flat=(40, 20, 6))
    # el llum giratori
    lx, ly = BEACON
    obox(cv, lx - 4, ly - 1, lx + 4, ly + 3, PLASTIC, 2.4)
    cv.vline(lx, ly + 4, 108, PLASTIC, 2.2)
    beacon(cv, beacon_on)


def beacon(cv, phase):
    """El llum taronja: la cúpula i, segons la fase, la llum que gira (cap a l'esquerra, de cara, a la dreta, d'esquena)."""
    lx, ly = BEACON
    on = phase in (0, 1, 2)
    cv.disc(lx, ly - 5, 4.2, 4.6, FORK, lambda nx, ny: (5.0 if on else 3.4) - ny * 0.6, lit=0)
    cv.hline(lx - 4, lx + 4, ly - 1, FORK, 2.4, lit=0)                   # l'anella de la base
    if on:
        dx = (-1, 0, 1)[phase]
        cv.vline(lx + dx * 2, ly - 8, ly - 3, [(255, 240, 200)], 0, lit=0)   # el mirall de dins, que gira
        cv.flat(lx - 1, ly - 8, (255, 250, 230))
        cv.glow(lx + dx * 13, ly - 5, 21 if phase == 1 else 16, (255, 150, 40), 0.45 if phase == 1 else 0.3)
    else:
        cv.flat(lx - 1, ly - 8, (240, 170, 80))
        cv.vline(lx + 2, ly - 7, ly - 3, FORK, 2.6, lit=0)


def time_clock(cv):
    """El rellotge de fitxar, amb el casiller de targetes al costat."""
    x0, y0 = 421, 45
    WOODC = [(30, 26, 22), (70, 60, 48), (120, 106, 84), (170, 156, 128), (210, 198, 170)]
    obox(cv, x0, y0, x0 + 24, y0 + 35, WOODC, 3.2)
    cv.disc(x0 + 12, y0 + 12, 8, 8, SHEET, lambda nx, ny: 4.8 - ny * 0.4)
    cv.ring(x0 + 12, y0 + 12, 8, SHEET, 1.6, step=8)
    for a in range(0, 360, 30):                                          # les hores
        cv.flat(round(x0 + 12 + math.cos(math.radians(a)) * 6), round(y0 + 12 + math.sin(math.radians(a)) * 6), (60, 60, 66))
    cv.line(x0 + 12, y0 + 12, x0 + 12, y0 + 7, [(20, 20, 30)], 0)
    cv.line(x0 + 12, y0 + 12, x0 + 16, y0 + 13, [(20, 20, 30)], 0)
    cv.line(x0 + 12, y0 + 12, x0 + 9, y0 + 17, RED, 2.6)                # el segonter
    cv.rect(x0 + 5, y0 + 25, x0 + 19, y0 + 28, PLASTIC, 1.0)            # la ranura
    cv.hline(x0 + 5, x0 + 19, y0 + 25, PLASTIC, 0.2)
    cv.disc(x0 + 20, y0 + 31, 1.4, 1.4, [(40, 160, 60), (120, 240, 140)], 1.0, lit=0)   # el pilot verd
    # el casiller
    obox(cv, x0 + 29, y0 - 3, x0 + 59, y0 + 40, [(40, 44, 50), (70, 76, 84), (110, 116, 124), (150, 156, 162)], 2.6)
    for r in range(5):
        for c in range(3):
            cx, cy = x0 + 32 + c * 9, y0 + r * 8
            cv.rect(cx, cy, cx + 7, cy + 5, PLASTIC, 1.2)
            if hr(r, c, 9) > 0.35:
                cv.rect(cx + 1, cy - 3, cx + 6, cy + 4, SHEET, lambda x, y: 4.4 - (0.6 if x == cx + 6 else 0))
                cv.hline(cx + 1, cx + 6, cy - 2, RED if hr(r, c) > 0.5 else [(60, 90, 160)], 0)
                cv.hline(cx + 2, cx + 4, cy, [(120, 120, 128)], 0)       # el nom, a llapis
    text(cv, 'FITXAR', x0 + 29, y0 + 47, [(30, 30, 36)], 0, flat=(36, 36, 42))


# ─── La màquina de cafè ────────────────────────────────────────────────────

def coffee_machine(cv):
    """Una expenedora de cafè dels noranta: marró i crema, una tassa pintada i el cop de puny al costat."""
    x0, y0, x1, y1 = 400, 93, 445, FLOOR_Y
    obox(cv, x0, y0, x1, y1, COFFEE, 3.2, side=-1.2)
    cv.vline(x0 + 1, y0 + 2, y1 - 1, COFFEE, 4.2)
    # el frontal: el rètol il·luminat
    SIGN = [(60, 30, 10), (130, 70, 26), (200, 130, 60), (240, 190, 120), (255, 236, 190)]
    obox(cv, x0 + 4, y0 + 4, x1 - 4, y0 + 35, SIGN, 2.8, lit=0)
    cv.disc(x0 + 20, y0 + 15, 7, 4.6, [(80, 40, 20), (140, 80, 40), (200, 150, 100), (250, 230, 200)], lambda nx, ny: 2.6 - ny, lit=0)
    cv.hline(x0 + 15, x0 + 25, y0 + 13, [(60, 30, 14)], 0, lit=0)       # el cafè, dins la tassa
    cv.rect(x0 + 27, y0 + 12, x0 + 29, y0 + 16, [(80, 40, 20), (200, 150, 100)], 1.0, lit=0)   # la nansa
    cv.disc(x0 + 20, y0 + 20, 9, 1.4, [(80, 40, 20), (200, 150, 100)], 0.6, lit=0)   # el plat
    for i in range(3):                                                   # el vapor
        bx = x0 + 16 + i * 4
        cv.line(bx, y0 + 9, bx + 1, y0 + 7, [(255, 250, 240)], 0, lit=0)
        cv.line(bx + 1, y0 + 7, bx, y0 + 5, [(255, 250, 240)], 0, lit=0)
    text(cv, 'CAFÈ', x0 + 13, y0 + 25, [(60, 20, 6)], 0, lit=0, flat=(70, 26, 8))
    cv.glow(x0 + 22, y0 + 20, 27, (255, 200, 120), 0.2)
    # els botons
    for r in range(4):
        obox(cv, x0 + 5, y0 + 40 + r * 9, x0 + 24, y0 + 46 + r * 9, SHEET, 4.0)
        cv.rect(x0 + 8, y0 + 43 + r * 9, x0 + 17, y0 + 43 + r * 9, PLASTIC, 1.4)
        cv.put(x0 + 21, y0 + 43 + r * 9, [(200, 60, 40)], 0)
    # el moneder i la pantalleta
    obox(cv, x0 + 29, y0 + 40, x1 - 5, y0 + 53, STEEL, 3.6)
    cv.rect(x0 + 32, y0 + 42, x1 - 9, y0 + 46, [(10, 30, 10), (60, 200, 80)], 0.6, lit=0)
    cv.hline(x0 + 33, x0 + 36, y0 + 44, [(90, 230, 110)], 0, lit=0)      # «0.80»
    cv.put(x0 + 37, y0 + 45, [(90, 230, 110)], 0, lit=0)
    cv.hline(x0 + 38, x0 + 40, y0 + 44, [(90, 230, 110)], 0, lit=0)
    cv.rect(x0 + 36, y0 + 49, x1 - 11, y0 + 50, PLASTIC, 0.6)            # la ranura de les monedes
    obox(cv, x0 + 29, y0 + 59, x1 - 5, y0 + 67, STEEL, 3.0)              # el retorn de monedes
    cv.rect(x0 + 32, y0 + 62, x1 - 8, y0 + 65, PLASTIC, 0.8)
    # el forat de la tassa
    obox(cv, x0 + 9, y0 + 80, x1 - 9, y0 + 99, PLASTIC, 0.8)
    cv.rect(x0 + 10, y0 + 81, x1 - 10, y0 + 82, PLASTIC, 0.2)
    cv.rect(x0 + 21, y0 + 83, x0 + 23, y0 + 85, STEEL, 3.0)               # el broc
    for gx in range(x0 + 11, x1 - 10, 2):                                # la reixeta d'escórrer
        cv.put(gx, y0 + 98, STEEL, 2.6)
    cv.rect(x0 + 19, y0 + 90, x0 + 26, y0 + 97, SHEET, lambda x, y: 4.6 - (0.8 if x == x0 + 26 else 0))   # un got oblidat
    cv.hline(x0 + 19, x0 + 26, y0 + 90, SHEET, 5.2)
    # el cop de puny: una abonyegada al costat dret
    cx, cy = x1 - 1, y0 + 64
    for yy in range(cy - 8, cy + 9):
        for xx in range(x1 - 5, x1 + 1):
            d = math.hypot((xx - cx) / 4.6, (yy - cy) / 8)
            if d < 1:
                cv.put(xx, yy, COFFEE, 1.2 + d * 1.6)
    for k in range(4):                                                   # les marques dels nusos
        cv.flat(x1 - 3, cy - 4 + k * 3, COFFEE[1])
        cv.flat(x1 - 2, cy - 4 + k * 3, COFFEE[2])
    # un paperet enganxat: «NO RETORNA CANVI»
    cv.rect(x0 + 6, y0 + 72, x0 + 20, y0 + 77, SHEET, 4.6)
    for k in range(2):
        cv.hline(x0 + 7, x0 + 18 - k * 3, y0 + 73 + k * 2, [(60, 60, 70)], 0)
    cv.darken(x1 + 1, y0 + 3, x1 + 5, y1, 0.45)
    cv.darken(x0 - 1, y1 + 1, x1 + 4, y1 + 4, 0.5)


# ─── L'ascensor de servei ──────────────────────────────────────────────────

def elevator(cv):
    """L'ascensor de servei: marc d'acer, portes rascades, l'indicador de plantes, el lector i l'adhesiu."""
    x0, y0, x1, y1 = 533, 53, 613, FLOOR_Y
    obox(cv, x0, y0, x1, y1, STEEL, 3.0, top=0.8)
    for by in range(y0 + 6, y1, 20):                                     # els cargols del marc
        cv.put(x0 + 2, by, STEEL, 4.6)
        cv.put(x1 - 2, by, STEEL, 2.4)
    # l'indicador de planta
    obox(cv, 547, y0 + 4, 600, y0 + 15, PLASTIC, 0.8)
    for i, ch in enumerate('S0123'):
        col = (255, 120, 40) if ch == 'S' else (90, 70, 50)
        text(cv, ch, 552 + i * 9, y0 + 7, [col], 0, lit=0, flat=col)
    cv.glow(553, y0 + 9, 8, (255, 120, 40), 0.4)
    # les portes
    for dx0, dx1 in ((539, 572), (574, 603)):
        cv.rect(dx0, y0 + 19, dx1, y1, STEEL, lambda x, y, d=dx0: 4.4 + (hr(x, y // 3, 4) - 0.5) * 0.4 + (0.8 if x == d else 0)
                + (0.3 if (x - d) % 9 == 3 else 0))                       # el raspallat de l'acer
        outline(cv, dx0, y0 + 19, dx1, y1, STEEL)
    for i in range(10):                                                  # rascades de carros
        sy = 155 + int(hr(i, 5) * 35)
        sx = 541 + int(hr(i, 6) * 53)
        cv.hline(sx, sx + 8 + int(hr(i, 7) * 8), sy, STEEL, 2.6)
        cv.hline(sx + 1, sx + 7, sy + 1, STEEL, 5.2)
    cv.vline(573, y0 + 19, y1, STEEL, 1.0)
    cv.rect(539, y1 - 3, 603, y1, STEEL, 2.2)                            # el llindar
    # l'adhesiu groc
    obox(cv, 543, 96, 600, 123, YELH, 3.6)
    cv.rect(544, 97, 599, 97, YELH, 4.4)
    for k, word in enumerate(('NOMÉS', 'PERSONAL', 'AUTORITZAT')):
        text(cv, word, 572 - text_width(word) // 2, 100 + k * 8 - (1 if k == 0 else 0), [(30, 20, 0)], 0, flat=(30, 20, 0))
    cv.put(599, 122, YELH, 1.6)                                          # la cantonada que es desenganxa
    cv.put(598, 122, YELH, 4.8)
    # el lector de targetes, al muntant dret
    obox(cv, 604, 117, 612, 144, PLASTIC, 1.6)
    cv.rect(606, 121, 610, 128, [(10, 10, 14), (40, 40, 50)], 0.6)
    cv.hline(606, 610, 121, [(60, 60, 80)], 0)
    cv.disc(608, 136, 1.8, 1.8, [(230, 40, 36)], 0, lit=0)
    cv.flat(607, 135, (255, 160, 150))
    cv.glow(608, 136, 7, (255, 50, 40), 0.4)
    # el botó de crida
    obox(cv, 616, 128, 624, 144, STEEL, 3.4)
    cv.disc(620, 136, 2.2, 2.2, [(140, 140, 150), (200, 200, 210), (240, 240, 246)], lambda nx, ny: 1.4 - ny)
    cv.darken(x1 + 1, y0, x1 + 4, y1, 0.4)


def house_sign(cv):
    """El rètol de la casa: blau marí i or, «MOLL DE CÀRREGA», amb el logo."""
    x0, y0, x1 = 261, 53, 400
    obox(cv, x0, y0, x1, y0 + 19, NAVYB, 3.0)
    cv.rect(x0 + 1, y0 + 1, x1 - 1, y0 + 1, BRASS, 4.4)
    cv.rect(x0 + 1, y0 + 18, x1 - 1, y0 + 18, BRASS, 3.6)
    cv.hline(x0 + 1, x1 - 1, y0 + 2, NAVYB, 4.0)
    logo(cv, x0 + 12, y0 + 10, k=1.2, lvl=4.4)
    s = 'MOLL DE CÀRREGA'
    text(cv, s, x0 + 24 + (x1 - x0 - 24 - text_width(s)) // 2, y0 + 7, BRASS, 5.0)
    for bx in (x0 + 3, x1 - 3):                                          # els cargols
        cv.put(bx, y0 + 10, BRASS, 3.0)
    # l'avís de sota
    s2 = 'ARMILLA OBLIGATÒRIA'
    text(cv, s2, (x0 + x1) // 2 - text_width(s2) // 2, y0 + 28, [(30, 30, 36)], 0, flat=(44, 44, 50))


def crates_right(cv):
    """Caixes apilades entre la màquina i l'ascensor, contra la paret (al fons, sense tapar la Rius)."""
    obox(cv, 496, 152, 528, 176, BOXC, 3.2)
    obox(cv, 501, 131, 525, 151, BOXC, 3.6)
    for bx0, by0, bx1, by1 in ((496, 152, 528, 176), (501, 131, 525, 151)):
        cv.vline(bx1 - 1, by0 + 1, by1 - 1, BOXC, 2.2)
    cv.hline(497, 527, 164, [(200, 180, 120), (230, 214, 160)], 0.6)
    cv.hline(497, 527, 165, [(200, 180, 120), (230, 214, 160)], 0.2)
    text(cv, 'FRÀGIL', 503, 139, [(120, 20, 20)], 0, flat=(140, 30, 26))
    for k in range(3):                                                   # la copa del «fràgil»
        cv.put(512 + k, 146, [(140, 30, 26)], 0)
    cv.put(513, 147, [(140, 30, 26)], 0)
    cv.put(513, 148, [(140, 30, 26)], 0)
    obox(cv, 491, 176, 531, 181, PALLET, 3.0)
    for px in (493, 509, 525):
        cv.rect(px, 179, px + 4, 180, PALLET, 1.8)


def bg(cv, beacon_phase=0, tube_on=True):
    wall(cv)
    ceiling(cv)
    if not tube_on:
        tube(cv, TUBES[0], on=False)
        cv.darken(267, 24, 373, 40, 0.2)
    floor(cv)
    outside(cv)
    van(cv, 141, 101, 227, 200)
    van(cv, 29, 91, 128, 208)
    shutter(cv)
    house_sign(cv)
    tecnics(cv)
    time_clock(cv)
    forklift(cv, beacon_phase)
    coffee_machine(cv)
    crates_right(cv)
    elevator(cv)


PROPS = {}


# ─── El llum giratori del toro ─────────────────────────────────────────────

def _frames():
    base = Canvas(light=LIGHT)
    bg(base)
    frames = []
    for i in range(8):
        cv = Canvas(light=LIGHT)
        bg(cv, beacon_phase=i % 4, tube_on=(i != 5))
        frames.append(_diff(cv.img, base.img))
    return frames


ANIMS = {'llum_toro': {'frames': _frames, 'frameDuration': 180}}
