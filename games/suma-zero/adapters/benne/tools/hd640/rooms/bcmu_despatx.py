"""
El despatx del Director (Acte 3, la Vet) a 640×360: la composició de hd/rooms/bcmu_despatx.py ×4/3, dibuixada de nou.
La planta noble del BCMU, Ginebra, les onze i quart:
  - les parets de la planta noble (marbre crema, arrimador de caoba, cornisa i cassetons, com a l'avantdespatx);
    un parquet de llistons encerat i una catifa blau marí amb sanefa d'or;
  - el finestral (la llum de tota la sala): el llac de Ginebra a mig matí, el Jet d'Eau, la riba amb teulades i,
    al fons, els Alps nevats; cortines de vellut blau marí lligades amb cordons d'or;
  - la porta doble de caoba (tornar a l'avantdespatx);
  - un sofà Chesterfield de pell, amb capitonè, i, a sobre, tres diplomes en marcs daurats;
  - el llit d'en Rockefeller (de vellut, amb el coixí) i el globus terraqüi que s'obre i és un bar;
  - la llibreria de llibres de finances que no ha obert ningú, amb el logotip del BCMU;
  - la taula de despatx de caoba amb sobre de pell: la foto d'en Rockefeller amb llacet en un marc de plata,
    el mòbil cap per avall, el portaplomes i la cadira de respatller alt;
  - el retrat a l'oli d'en Rockefeller i, a terra, el seu bol de plata amb el nom gravat.
Animació: `llac` (l'aigua es mou, el Jet d'Eau bufa i el vaixell es gronxa).
"""
import math

import hd640  # noqa: F401  (posa la llibreria de dibuix a 640×360)
from hd.pix import Light, W, H, hr, WALNUT
from hd.rooms.comu import obox, outline
from hd.rooms.pis_cuina import outline_poly
from hd.rooms.bcmu_vestibul import DARKM, DOG
from hd640.rooms.bcmu import MARBLE, BRASS, MAHOG, CARPET, logo
from hd640.rooms.bcmu_avantdespatx import wall, sconce, frame, BANKG, PAPERW

# Art a 2× (1280×720 per a una sala de 640×360): el mateix dibuix, amb les formes, el dither i la llum a la
# resolució real (hd1280/canvas2x.py); el motor el mostra a 1/2 (artScale al .room.json).
ART_SCALE = 2
from hd1280.canvas2x import Canvas2x as Canvas  # noqa: E402,F811
from hd.pix import Canvas as Canvas1x  # noqa: E402,F401  (llenços auxiliars en píxels de sala: figures, textos)

FLOOR_Y = 200
DESK_TOP = 157
DESK = (421, 573)
WIN = (200, 27, 400, 133)

LEATHER = [(18, 6, 8), (40, 12, 14), (66, 20, 22), (94, 32, 30), (124, 46, 40), (156, 68, 56), (190, 100, 80)]
VELVET = [(6, 8, 18), (12, 16, 34), (20, 26, 52), (30, 40, 74), (44, 58, 100), (64, 82, 130)]
SKYD = [(120, 150, 180), (148, 176, 204), (172, 198, 222), (196, 216, 234), (220, 232, 242), (240, 246, 250)]
ALPS = [(70, 86, 110), (92, 110, 134), (118, 136, 160), (150, 166, 186), (214, 224, 236), (246, 250, 252)]
LAKE = [(20, 50, 80), (30, 70, 106), (44, 94, 132), (66, 122, 158), (100, 156, 186), (170, 210, 228), (240, 250, 252)]
ROOF = [(60, 40, 36), (100, 60, 48), (140, 84, 64), (170, 110, 84), (200, 150, 120)]
TOWN = [(80, 84, 90), (120, 122, 126), (160, 160, 158), (196, 194, 186), (226, 222, 212)]
TREE = [(20, 40, 24), (32, 60, 34), (48, 82, 44), (70, 104, 56)]
SILVER = [(30, 32, 40), (60, 64, 74), (100, 104, 114), (146, 150, 158), (190, 194, 200), (226, 230, 234), (252, 252, 255)]
PHONE = [(6, 6, 8), (14, 14, 18), (26, 26, 32), (42, 42, 50), (62, 62, 72), (96, 96, 106)]
BOOKS = [[(40, 14, 14), (80, 26, 24), (120, 40, 34)], [(14, 22, 40), (24, 40, 72), (40, 62, 104)],
         [(18, 36, 22), (30, 60, 36), (50, 88, 54)], [(50, 36, 20), (96, 70, 36), (140, 104, 56)],
         [(30, 14, 30), (60, 30, 54), (90, 50, 80)]]
RIBBON = [(120, 20, 50), (200, 50, 100), (250, 120, 160)]

LIGHT = Light(ambient=0.0, vignette=(80, 40), floor_fade=(253, 40))
LIGHT.point(300, 80, r=387, k=2.4, squash=0.7, power=1.3)            # el finestral
LIGHT.point(300, 233, r=147, k=0.8, squash=2.4, power=1.6)           # el sol a terra
for _sx in (141,):                                                   # l'aplic
    LIGHT.point(_sx, 83, r=67, k=0.7, squash=1.1, power=1.8)


# ─── Terra ─────────────────────────────────────────────────────────────────

def floor(cv):
    """Parquet de llistons encerat, en perspectiva, i una catifa blau marí amb sanefa d'or."""
    for y in range(FLOOR_Y, H):
        dep = (y - FLOOR_Y) / (H - FLOOR_Y)
        v = (y - FLOOR_Y) * 1.7 / (1 + dep * 0.6)
        for x in range(W):
            u = (x - W / 2) / (0.55 + dep * 0.9) + W / 2
            col = int(u // 13)
            fv = v + hr(col, 3) * 53                                    # les juntes, a trencajunts
            seam = (u % 13) < 1.0 or (fv % 53) < 0.8
            grain = math.sin(u * 0.9 + hr(col, 7) * 6) * 0.12             # la veta del roure
            n = (hr(col, int(fv // 53), 4) - 0.5) * 0.7 + (hr(x // 5, y, 5) - 0.5) * 0.25 + grain
            cv.put(x, y, WALNUT, (3.0 if seam else 4.4 + n))
            # la catifa
            if 160 <= u <= 533 and v >= 13:
                ru = min(u - 160, 533 - u)
                rv = v - 13
                edge = min(ru, rv)
                n2 = (hr(x, y, 6) - 0.5) * 0.6
                if edge < 3:
                    cv.put(x, y, BRASS, 2.2 + n2)
                elif edge < 5:
                    cv.put(x, y, VELVET, 2.6 + n2)
                elif edge < 8:
                    cv.put(x, y, BRASS, 3.0 + n2 + (0.4 if edge < 6 else 0))
                else:
                    mot = abs(((u - 171) % 32) - 16) + abs(((rv - 8) % 21) - 10.5) * 1.5 < 4
                    dot = abs(((u - 155) % 32) - 16) + abs(((rv + 2.5) % 21) - 10.5) * 1.5 < 1.5
                    cv.put(x, y, VELVET, (3.4 if mot else (3.0 if dot else 2.4)) + n2)
    cv.darken(0, FLOOR_Y, W - 1, FLOOR_Y + 2, 0.5)
    # el sol del finestral, estirat a terra
    cv.tint(0, FLOOR_Y + 3, W - 1, H - 1, (255, 236, 190),
            lambda x, y: 0.16 * max(0, 1 - abs(x - 300 - (y - 200) * 0.6) / 120) * max(0, 1 - (y - 203) / 69))


# ─── El finestral ──────────────────────────────────────────────────────────

def view(cv, x0, y0, x1, y1, f=None):
    """El llac de Ginebra a mig matí: cel, els Alps, l'altra riba, l'aigua, el Jet d'Eau i les teulades.

    `f`: fotograma de l'animació (0..ANIM_N-1): l'aigua es mou, el Jet d'Eau bufa i el vaixell es gronxa."""
    ph = 0.0 if f is None else f / ANIM_N * 2 * math.pi
    hz = 77                                                           # la línia de l'altra riba
    for y in range(y0, y1 + 1):
        for x in range(x0, x1 + 1):
            if y < hz:
                cv.put(x, y, SKYD, 4.6 - (y - y0) * 0.045 + (hr(x // 4, y // 3, 1) - 0.5) * 0.2, lit=0)
            else:
                d = (y - hz) / (y1 - hz)
                gx = x // 4 if f is None else (x + round(math.sin(ph + y * 0.75) * 2.7)) // 4
                gk = 2 if f is None else 2 + (f // 2 + y) % 3
                glint = 1.2 if (hr(gx, y, gk) > 0.93 and abs(x - 267) < 80) else 0
                cv.put(x, y, LAKE, 3.6 - d * 1.2 + glint + math.sin(x * 0.375 + y * 1.575 - ph) * 0.25, lit=0)
    # uns núvols
    for (cx, cy, rx) in ((235, 40, 19), (259, 36, 13), (247, 43, 11), (355, 45, 21), (379, 41, 12)):
        cv.disc(cx, cy, rx, rx * 0.35, SKYD, lambda nx, ny: 5.4 - ny * 0.8, lit=0)
    # els Alps: dues serralades, la de darrere amb neu
    for x in range(x0, x1 + 1):
        far = (61 - 8 * math.sin((x - x0) * 0.0525) - 5.3 * math.sin((x - x0) * 0.1425 + 1)
               - (5.3 if 315 < x < 349 else 0) * (1 - abs(x - 332) / 17))
        near = 69 - 4 * math.sin((x - x0) * 0.0825 + 2) - 2.7 * math.sin(x * 0.225)
        for y in range(int(far), hz):
            snow = y < far + 4 + 2.7 * math.sin(x * 0.525)
            rock = (hr(x // 2, y, 8) - 0.5) * 0.5
            cv.put(x, y, ALPS, (4.6 if snow else 2.4 + rock) + (0.6 if (x + y) % 7 == 0 and snow else 0)
                   - (0.5 if snow and math.sin(x * 0.4) > 0.6 else 0), lit=0)
        for y in range(int(near), hz):
            cv.put(x, y, ALPS, 1.2 + (y - near) * 0.075 + (hr(x, y // 2, 9) - 0.5) * 0.3, lit=0)
    # l'altra riba: una ratlla verda i casetes
    for x in range(x0, x1 + 1):
        cv.put(x, hz - 1, TREE, 2.0, lit=0)
        cv.put(x, hz, TREE, 1.4, lit=0)
        cv.put(x, hz + 1, LAKE, 2.0, lit=0)                            # l'ombra de la riba a l'aigua
        if hr(x // 2, 9) > 0.6:
            cv.flat(x, hz - 2, TOWN[3])
            if hr(x // 2, 10) > 0.7:
                cv.flat(x, hz - 3, TOWN[4])
    # el Jet d'Eau: un ploma blanca que el vent tomba una mica
    jx, jb, jt = 315, 101, 40
    for y in range(jt, jb + 1):
        t = (jb - y) / (jb - jt)
        cx = jx + t * t * (5.3 + math.sin(ph) * 1.6)
        w = 1.0 + t * 2.1 + (0 if f is None else math.sin(ph * 2 - y * 0.3) * 0.45 * t)
        for x in range(int(cx - w), int(cx + w) + 1):
            cv.put(x, y, SKYD, 5.4 - abs(x - cx) / w * 0.8, lit=0)
    sx = jx + 7 + (0 if f is None else round(math.sin(ph) * 1.6))
    cv.disc(sx, jt + 1 - (0 if f is None else round(math.cos(ph) * 1.3)), 5.3, 4, SKYD, lambda nx, ny: 5.2 - nx * 0.6, lit=0)   # l'esprai de dalt
    for i in range(24):                                               # les gotes que s'endú el vent
        if f is None:
            cv.flat(jx + 8 + int(hr(i, 3) * 11), jt + int(hr(i, 4) * 13), SKYD[4])
        else:
            k = (hr(i, 5) + f / ANIM_N) % 1                           # cada gota cau i s'allunya, en bucle
            cv.flat(sx + 1 + int(hr(i, 3) * 7 + k * 8), jt - 1 + int(hr(i, 4) * 5 + k * 13), SKYD[4])
    cv.hline(jx - 5, jx + 5, jb + 1, LAKE, 5.6, lit=0)                # l'escuma de la base
    cv.hline(jx - 3, jx + 3, jb, LAKE, 6.0, lit=0)
    cv.rect(jx - 11, jb + 2, jx - 5, jb + 3, TOWN, lambda x, y: 3.4 if y == jb + 2 else 2.2, lit=0)   # la punta del moll
    cv.flat(jx - 11, jb + 1, (200, 40, 40))                           # el far vermell del moll
    # un vaixell de rodes
    bx, by = 248, 96 + (0 if f is None or (f // 6) % 2 == 0 else 1)
    cv.rect(bx, by, bx + 19, by + 3, TOWN, lambda x, y: 4.2 if y < by + 2 else 3.0, lit=0)
    cv.hline(bx + 1, bx + 18, by + 3, LAKE, 1.4, lit=0)
    cv.rect(bx + 4, by - 3, bx + 13, by - 1, TOWN, 3.2, lit=0)
    for wx in range(bx + 5, bx + 13, 2):                              # les finestretes
        cv.flat(wx, by - 2, TOWN[0])
    cv.rect(bx + 8, by - 6, bx + 9, by - 4, ROOF, 2.0, lit=0)
    cv.disc(bx + 11, by + 1, 2.4, 2.0, TOWN, 2.0, lit=0)              # la roda
    cv.hline(bx + 20, bx + 29, by + 3, LAKE, 5.0, lit=0)
    cv.hline(bx + 22, bx + 33, by + 4, LAKE, 4.6, lit=0)
    # les teulades de baix (el barri de davant), retallades pel marc
    C = lambda v: max(x0, min(x1, v))
    for i in range(13):
        hx = x0 + i * 17 - 5 + int(hr(i, 7) * 5)
        top = y1 - 11 - int(hr(i, 8) * 8)
        cv.rect(C(hx), top, C(hx + 16), y1, TOWN, lambda x, y, i=i, h=hx: 2.8 + hr(i, 10) * 0.8 - (0.6 if x > h + 12 else 0), lit=0)
        cv.poly([(C(hx - 1), top), (C(hx + 8), top - 7 if x0 <= hx + 8 <= x1 else top - 3), (C(hx + 17), top)], ROOF,
                lambda x, y, i=i, h=hx: 2.6 + hr(i, 11) - (0.7 if x > h + 8 else 0), lit=0)
        for wx in range(hx + 2, hx + 15, 5):
            if x0 <= wx and wx + 1 <= x1:
                cv.rect(wx, top + 4, wx + 1, top + 5, [TOWN[0]], 0, lit=0)
        if hr(i, 12) > 0.6 and hx + 12 <= x1:                         # una xemeneia
            cv.rect(hx + 11, top - 6, hx + 12, top - 3, ROOF, 1.4, lit=0)
    for i in range(8):                                                # uns arbres del passeig
        tx = x0 + 8 + i * 25 + int(hr(i, 12) * 8)
        cv.disc(tx, y1 - 12, 5.3, 4, TREE, lambda nx, ny: 2.6 - ny - nx * 0.3 + (hr(int(nx * 4), int(ny * 4), 13) - 0.5) * 0.5, lit=0)


def window(cv, f=None):
    """El finestral: marc de caoba, travessers, la vista, el reflex del vidre i l'ampit de marbre."""
    x0, y0, x1, y1 = WIN
    view(cv, x0 + 4, y0 + 4, x1 - 4, y1 - 4, f)
    cv.tint(x0 + 4, y0 + 4, x1 - 4, y1 - 4, (255, 255, 255), lambda x, y: 0.16 if (x + y) % 61 < 7 else (0.07 if (x + y) % 61 < 9 else 0.0))
    # el marc i els travessers
    obox(cv, x0, y0, x1, y0 + 4, MAHOG, 4.0)
    obox(cv, x0, y1 - 4, x1, y1, MAHOG, 3.6)
    for mx in (x0, x0 + 67, x0 + 133, x1 - 4):
        cv.rect(mx, y0, mx + 4, y1, MAHOG, lambda x, y, m=mx: 3.8 + (0.8 if x == m else 0) - (0.8 if x == m + 4 else 0))
    cv.rect(x0, 63, x1, 65, MAHOG, lambda x, y: 4.6 if y == 63 else (3.0 if y == 65 else 4.0))
    for mx in (x0 + 67, x0 + 133):                                    # les falleves de llautó
        cv.rect(mx + 1, 96, mx + 3, 99, BRASS, 4.4)
    outline(cv, x0, y0, x1, y1, MAHOG)
    # l'ampit
    cv.rect(x0 - 5, y1 + 1, x1 + 5, y1 + 5, MARBLE, lambda x, y: 6.0 if y == y1 + 1 else (4.0 if y == y1 + 5 else 4.6))
    outline(cv, x0 - 5, y1 + 1, x1 + 5, y1 + 5, MARBLE)
    cv.darken(x0 - 3, y1 + 6, x1 + 3, y1 + 8, 0.4)


def curtain(cv, x0, x1, left):
    """Una cortina de vellut blau marí, lligada amb un cordó d'or a mitja alçada."""
    tie = 139
    for y in range(19, FLOOR_Y + 1):
        # lligada: més estreta al cordó
        pinch = max(0, 1 - abs(y - tie) / 53) * 5.3
        a = x0 + (pinch if left else 0)
        b = x1 - (0 if left else pinch)
        for x in range(int(a), int(b) + 1):
            fold = math.sin((x - x0) * 0.975 + y * 0.015) * 0.9
            sheen = 0.3 if math.sin((x - x0) * 0.975 + y * 0.015) > 0.85 else 0
            cv.put(x, y, VELVET, 3.0 + fold + sheen + (0.6 if (x - a) < 1 else 0) - (0.6 if (b - x) < 1 else 0))
        cv.flat(a, y, VELVET[0])
        cv.flat(b, y, VELVET[0])
    for x in range(x0 + 1, x1, 3):                                    # la vora de baix, que fa bossa a terra
        cv.put(x, FLOOR_Y, VELVET, 3.6)
    cv.rect(x0 + 1, tie - 1, x1 - 1, tie + 1, BRASS, lambda x, y: 5.0 if y == tie - 1 else 3.8)
    cx = x1 + 1 if left else x0 - 1
    cv.line(cx, tie + 1, cx, tie + 11, BRASS, 4.0)                   # la borla
    cv.disc(cx, tie + 13, 2.1, 3.2, BRASS, lambda nx, ny: 4.4 - ny)
    for dx in (-1, 0, 1):                                             # els fils de la borla
        cv.vline(cx + dx, tie + 15, tie + 18, BRASS, 3.4 - abs(dx) * 0.6)


# ─── La porta ──────────────────────────────────────────────────────────────

def door(cv):
    """La porta doble de caoba, des de dins: la mateixa de l'avantdespatx, amb poms de llautó."""
    x0, y0, x1, y1 = 24, 64, 77, FLOOR_Y - 1
    obox(cv, x0 - 5, y0 - 5, x1 + 5, y1, MAHOG, 4.2, top=1.2)
    cv.vline(x0 - 3, y0 - 3, y1, MAHOG, 4.8)
    cv.vline(x1 + 3, y0 - 3, y1, MAHOG, 2.8)
    obox(cv, x0 - 7, 53, x1 + 7, y0 - 5, MAHOG, 4.0, top=1.4)
    cv.hline(x0 - 6, x1 + 6, 56, BRASS, 4.0)
    for lx0, lx1 in ((x0, (x0 + x1) // 2), ((x0 + x1) // 2 + 1, x1)):
        for y in range(y0, y1 + 1):
            for x in range(lx0, lx1 + 1):
                n = (hr(x, y // 8, 51) - 0.5) * 0.3 + math.sin(x * 0.375 + y * 0.0225) * 0.12
                cv.put(x, y, MAHOG, 3.4 + n)
        for (py0, py1) in ((y0 + 7, y0 + 56), (y0 + 64, y1 - 8)):
            a, b = lx0 + 4, lx1 - 4
            cv.rect(a, py0, b, py1, MAHOG, 3.8)
            cv.hline(a, b, py0, MAHOG, 1.4)
            cv.vline(a, py0, py1, MAHOG, 1.6)
            cv.hline(a, b, py1, MAHOG, 5.2)
            cv.vline(b, py0, py1, MAHOG, 5.0)
            cv.rect(a + 3, py0 + 3, b - 3, py1 - 3, MAHOG, 3.1)
            cv.hline(a + 3, b - 3, py0 + 3, MAHOG, 4.6)
            cv.vline(a + 3, py0 + 3, py1 - 3, MAHOG, 4.4)
        outline(cv, lx0, y0, lx1, y1, MAHOG)
    cx = (x0 + x1) // 2
    for px in (cx - 4, cx + 5):
        cv.disc(px, 133, 2.4, 2.4, BRASS, lambda nx, ny: 4.6 - ny - nx * 0.4)
        cv.flat(px - 1, 132, BRASS[6])
    cv.darken(x0 - 5, FLOOR_Y, x1 + 8, FLOOR_Y + 4, 0.45)


# ─── El sofà i els diplomes ────────────────────────────────────────────────

def diplomas(cv):
    """Tres diplomes en marcs daurats: pergamí, lletra petita i un segell vermell."""
    for i, (x0, y0) in enumerate(((104, 59), (133, 51), (163, 59))):
        x1, y1 = x0 + 24, y0 + (32 if i != 1 else 37)
        obox(cv, x0, y0, x1, y1, BRASS, 3.8, top=1.0, side=-1.0)
        cv.hline(x0 + 1, x1 - 1, y0 + 1, BRASS, 5.4)
        cv.rect(x0 + 3, y0 + 3, x1 - 3, y1 - 3, PAPERW, lambda x, y: 4.2 + (0.3 if (x * 3 + y) % 11 == 0 else 0))
        cv.hline(x0 + 7, x1 - 7, y0 + 6, [(60, 40, 30)], 0)            # el títol, en gòtica
        cv.hline(x0 + 8, x1 - 8, y0 + 7, [(110, 84, 64)], 0)
        for k in range(4):
            cv.hline(x0 + 5, x1 - 5 - (k % 2) * 4, y0 + 11 + k * 3, [(150, 140, 126)], 0)
        cv.hline(x1 - 10, x1 - 5, y1 - 6, [(80, 70, 90)], 0)           # la signatura
        sx = (x0 + x1) // 2 - 3
        for dx in (-2, 2):                                            # les cintes i el segell de lacre
            cv.line(sx + dx, y1 - 5, sx + dx * 2, y1 - 2, [(150, 30, 30)], 0)
        cv.sprite(['.aaa.', 'abbba', 'abcba', 'abbba', '.aaa.'], sx - 2, y1 - 10,
                  {'a': (150, 30, 30), 'b': (200, 56, 46), 'c': (150, 30, 30)})
        cv.darken(x1 + 1, y0 + 3, x1 + 3, y1 + 3, 0.5)


def sofa(cv):
    """Un Chesterfield de pell granat: respatller i braços a la mateixa alçada, capitonè, coixins i potes de bola."""
    x0, x1 = 91, 195
    top, seat, base = 147, 172, 195
    # el respatller capitonat: rombes entre botons
    for y in range(top + 3, seat + 1):
        for x in range(x0 + 13, x1 - 12):
            row = (y - top - 3) // 8
            off = 4 if row % 2 else 0
            dx = ((x - x0 + off) % 8) - 4
            dy = ((y - top - 3) % 8) - 4
            d = abs(dx) + abs(dy)
            cv.put(x, y, LEATHER, 4.0 - d * 0.21 - (y - top) * 0.015 + (hr(x, y, 9) - 0.5) * 0.15)
            if d == 0:
                cv.flat(x, y, LEATHER[1])
                cv.flat(x - 1, y - 1, LEATHER[5])                     # el botó, amb la llum
    cv.rect(x0 + 13, top, x1 - 12, top + 3, LEATHER, lambda x, y: 5.0 - (y - top) * 0.5)   # el cantell de dalt, enrotllat
    cv.hline(x0 + 13, x1 - 12, top, LEATHER, 0.6)
    # els coixins
    for k in range(3):
        cx0 = x0 + 13 + k * 27
        cv.rect(cx0, seat - 1, cx0 + 26, seat + 7, LEATHER,
                lambda x, y: 4.4 + (1.0 if y == seat - 1 else (0.5 if y == seat else 0)) - (0.9 if y > seat + 4 else 0))
        outline(cv, cx0, seat - 1, cx0 + 26, seat + 7, LEATHER)
        cv.hline(cx0 + 3, cx0 + 23, seat + 2, LEATHER, 3.8)             # el pes de qui no s'hi asseu
    # la faldilla, amb el filet de claus de llautó
    cv.rect(x0 + 3, seat + 8, x1 - 3, base, LEATHER, lambda x, y: 3.0 - (y - seat) * 0.03)
    for x in range(x0 + 5, x1 - 4, 4):
        cv.flat(x, seat + 9, BRASS[5])
        cv.flat(x + 1, seat + 10, BRASS[2])
    outline(cv, x0 + 3, seat + 8, x1 - 3, base, LEATHER)
    # els braços: a l'alçada del respatller, amb el rotlle de davant
    for ax in (x0, x1 - 13):
        cv.rect(ax, top + 3, ax + 13, base, LEATHER, lambda x, y, a=ax: 3.6 + (0.8 if x < a + 5 else 0) - (y - top) * 0.015)
        for y in range(top + 8, base, 6):
            cv.flat(ax + 7, y, LEATHER[1])
            cv.flat(ax + 6, y - 1, LEATHER[5])
        cv.disc(ax + 6.5, top + 4, 7.3, 4, LEATHER, lambda nx, ny: 5.0 - ny * 1.2 - nx * 0.3)
        cv.ring(ax + 6.5, top + 4, 2.7, LEATHER, 2.4, step=20)
        for y in range(top + 4, base + 1):
            cv.flat(ax, y, LEATHER[0])
            cv.flat(ax + 13, y, LEATHER[0])
    for lx in (x0 + 5, x1 - 7):                                       # les potes de bola
        cv.disc(lx, base + 3, 2.4, 2.4, MAHOG, lambda nx, ny: 4.0 - ny)
    cv.darken(x0 - 3, FLOOR_Y, x1 + 5, FLOOR_Y + 5, 0.5)


# ─── El llit d'en Rockefeller i el globus bar ─────────────────────────────

def dog_bed(cv):
    """Un llit de gos de vellut granat, amb la vora alta i un coixí de seda daurada (i un os de joguina)."""
    cx, x0, x1, y1 = 233, 207, 260, 204
    cv.disc(cx, y1 - 12, 27, 9.3, CARPET, lambda nx, ny: 3.4 - ny * 1.2 + math.sin(nx * 18) * 0.15)   # la vora de darrere, alta
    cv.disc(cx, y1 - 5, 27, 5.9, CARPET, lambda nx, ny: 4.2 - ny * 0.6)        # la de davant
    cv.disc(cx, y1 - 9, 20, 5.3, BRASS, lambda nx, ny: 4.0 - ny * 0.8 + (hr(int(nx * 7), 1) - 0.5) * 0.4)   # el coixí
    cv.disc(cx + 1, y1 - 8, 9.3, 2.1, BRASS, 3.2)                              # el clot d'en Rockefeller
    for k in range(5):                                                         # uns pèls blancs, al clot
        cv.flat(cx - 5 + int(hr(k, 31) * 12), y1 - 9 + int(hr(k, 32) * 3), DOG[5])
    cv.hline(x0 + 5, x1 - 5, y1 - 3, CARPET, 5.0)                              # el ribet
    for (bx, by) in ((cx - 10, y1 - 12), (cx - 4, y1 - 12)):                   # l'os
        cv.disc(bx, by, 1.6, 1.6, PAPERW, 4.6)
    cv.hline(cx - 9, cx - 5, y1 - 12, PAPERW, 4.2)
    cv.darken(x0 + 3, y1 + 1, x1 - 1, y1 + 3, 0.5)


def globe_bar(cv):
    """El globus terraqüi antic sobre un peu de caoba de tres potes: s'obre i és un bar."""
    cx, cy, r = 320, 163, 15
    OCEAN = [(26, 44, 44), (40, 66, 64), (60, 92, 84), (90, 122, 104), (130, 156, 128), (176, 190, 156)]
    LAND = [(60, 40, 20), (100, 72, 36), (146, 110, 60), (190, 156, 96), (224, 198, 140)]
    # el peu: tres potes corbes i el travesser
    for lx in (cx - 15, cx, cx + 15):
        far = lx == cx
        for o in ((0,) if far else (0, 1)):
            cv.line(cx + (lx - cx) // 2 + o, cy + 16, lx + o, FLOOR_Y + 1, MAHOG, (2.4 if far else 3.4) + o * 0.6)
    cv.rect(cx - 12, 189, cx + 12, 190, MAHOG, lambda x, y: 4.2 if y == 189 else 3.0)
    cv.disc(cx, cy + 17, 8, 2.7, MAHOG, 3.8)
    # l'horitzó de fusta (on s'obre)
    cv.disc(cx, cy + 1, r + 4, 4, MAHOG, lambda nx, ny: 4.4 - ny)
    for y in range(cy - r, cy + r + 1):
        for x in range(cx - r, cx + r + 1):
            nx, ny = (x - cx) / r, (y - cy) / r
            if nx * nx + ny * ny <= 1:
                land = math.sin(nx * 4.2 + 1.4) + math.cos(ny * 5 + nx * 2.4) > 0.9 or (nx > 0.2 and abs(ny - 0.2) < 0.25 and nx < 0.6)
                lv = 3.6 - nx * 0.9 - ny * 1.1 - (nx * nx + ny * ny) * 0.6
                grid = abs(ny) < 0.04 or abs(nx / max(0.2, math.sqrt(1 - ny * ny)) - 0.45) < 0.04   # l'equador i un meridià
                cv.put(x, y, LAND if land else OCEAN, lv - (0.5 if grid else 0) + (hr(x, y, 33) - 0.5) * 0.2)
    cv.put(cx - 6, cy - 7, OCEAN, 5.4)                                # la lluïssor del vernís
    cv.put(cx - 5, cy - 7, OCEAN, 4.8)
    cv.disc(cx, cy + 1, r + 4, 1.6, MAHOG, lambda nx, ny: 4.6)          # el cantell de l'horitzó, per davant
    cv.hline(cx - r - 4, cx + r + 4, cy + 3, MAHOG, 2.0)
    for k in range(0, 2 * r + 4):                                      # el meridià de llautó, inclinat
        a = math.radians(200 + k / (2 * r + 3) * 140)
        cv.put(round(cx + math.cos(a) * (r + 2)), round(cy + math.sin(a) * (r + 2)), BRASS, 4.4)
    cv.disc(cx - 4, cy - r - 1, 1.6, 1.6, BRASS, 5.0)
    cv.darken(cx - 17, FLOOR_Y + 1, cx + 17, FLOOR_Y + 4, 0.5)


# ─── La llibreria ──────────────────────────────────────────────────────────

def bookcase(cv):
    """La llibreria de caoba de darrere la taula: llibres de finances relligats, iguals i sense obrir."""
    x0, y0, x1, y1 = 429, 32, 571, 157
    obox(cv, x0 - 4, y0 - 8, x1 + 4, y0, MAHOG, 4.0, top=1.4)
    cv.hline(x0 - 3, x1 + 3, y0 - 4, BRASS, 3.8)
    for x in range(x0 - 3, x1 + 4, 4):                                # les dents de la cornisa
        cv.put(x, y0 - 1, MAHOG, 2.2)
    obox(cv, x0, y0, x1, y1, MAHOG, 2.4)
    for sy in range(y0 + 3, y1 - 8, 25):                              # cinc prestatges
        cv.rect(x0 + 4, sy, x1 - 4, sy + 21, MAHOG, lambda x, y, s=sy: 1.2 - (0.4 if y < s + 3 else 0))
        bx = x0 + 5
        i = 0
        while bx < x1 - 8:
            bw = 4 + int(hr(sy, i, 1) * 3)
            bh = 15 + int(hr(sy, i, 2) * 5)
            if hr(sy, i, 3) > 0.9 and bx < x1 - 21:                    # un forat, o un llibre ajagut
                if hr(sy, i, 5) > 0.5:
                    cv.rect(bx, sy + 18, bx + 13, sy + 21, BOOKS[i % len(BOOKS)], lambda x, y, s=sy: 1.6 + (0.6 if y == s + 18 else 0))
                bx += 8
                i += 1
                continue
            set_ = BOOKS[int(hr(sy, i // 6, 4) * len(BOOKS))]
            cv.rect(bx, sy + 21 - bh, bx + bw - 1, sy + 21, set_, lambda x, y, b=bx, e=bx + bw - 1: 1.4 + (0.8 if x == b else 0) - (0.5 if x == e else 0))
            cv.hline(bx, bx + bw - 1, sy + 23 - bh, BRASS, 3.6)        # els filets daurats del llom
            cv.hline(bx, bx + bw - 1, sy + 17, BRASS, 3.0)
            if bw >= 5:                                               # el tellet amb el títol
                cv.rect(bx + 1, sy + 26 - bh, bx + bw - 2, sy + 27 - bh, [(20, 14, 10)], 0)
            bx += bw
            i += 1
        cv.rect(x0 + 3, sy + 22, x1 - 3, sy + 24, MAHOG, lambda x, y, s=sy: 5.0 if y == s + 22 else (3.0 if y == s + 23 else 2.0))
    for vx in (x0 + 3, x1 - 3):
        cv.vline(vx, y0 + 1, y1 - 1, MAHOG, 4.4)
    logo(cv, (x0 + x1) // 2, y0 - 4, k=0.8, lvl=4.6)                   # el logotip, al frontó


def portrait(cv):
    """El retrat a l'oli d'en Rockefeller, amb llacet, sobre un coixí de vellut."""
    x0, y0, x1, y1 = 587, 40, 632, 104
    frame(cv, x0, y0, x1, y1)
    for y in range(y0 + 5, y1 - 4):
        for x in range(x0 + 5, x1 - 4):
            cv.put(x, y, VELVET, 2.0 + (hr(x // 3, y // 3, 7) - 0.5) * 0.5 + math.sin(x * 0.3) * 0.3 + (y - y0) * 0.008)
    cx = (x0 + x1) // 2
    cv.disc(cx, 88, 15, 5.3, CARPET, lambda nx, ny: 3.8 - ny)         # el coixí
    for s in (-1, 1):                                                 # les borles del coixí
        cv.disc(cx + s * 15, 90, 1.4, 1.8, BRASS, 4.2)
    cv.disc(cx, 77, 10.7, 9.3, DOG, lambda nx, ny: 3.6 - ny * 0.6 + (hr(int(nx * 8), int(ny * 7), 3) - 0.5) * 0.7)
    cv.disc(cx, 63, 8, 7.5, DOG, lambda nx, ny: 4.0 - ny * 0.6 - nx * 0.2 + (hr(int(nx * 7), int(ny * 7), 4) - 0.5) * 0.6)
    for s in (-1, 1):                                                 # les orelles
        cv.disc(cx + s * 8, 66, 3.2, 4.8, DOG, lambda nx, ny: 2.6 + (hr(int(nx * 3), int(ny * 4), 5) - 0.5) * 0.6)
        cv.disc(cx + s * 4, 87, 2.4, 1.4, DOG, 4.2)                    # les potes de davant
    for ex in (cx - 3, cx + 3):                                       # els ulls, amb la lluentor
        cv.flat(ex, 61, (20, 14, 14))
        cv.flat(ex, 62, (20, 14, 14))
        cv.flat(ex - 1, 61, (200, 200, 210))
    cv.rect(cx - 1, 65, cx, 66, [(40, 24, 24)], 0)                    # el nas
    cv.hline(cx - 1, cx + 1, 68, [(120, 70, 70)], 0)
    cv.rect(cx - 3, 55, cx + 3, 56, RIBBON, 1.6)                       # el llacet
    cv.flat(cx - 3, 54, RIBBON[1])
    cv.flat(cx + 3, 54, RIBBON[1])
    cv.flat(cx, 55, RIBBON[0])
    obox(cv, cx - 12, 107, cx + 12, 113, BRASS, 4.6)                   # la placa
    cv.hline(cx - 8, cx + 8, 110, BRASS, 2.4)


# ─── La taula ──────────────────────────────────────────────────────────────

def chair(cv):
    """La cadira del Director: respatller alt de pell capitonada, amb claus de llautó."""
    cx, y0 = 528, 112
    cv.rect(cx - 17, y0 + 4, cx + 17, DESK_TOP - 11, LEATHER, lambda x, y: 3.4 - abs(x - cx) * 0.03 + (0.6 if x < cx - 11 else 0))
    cv.disc(cx, y0 + 5, 17, 5.3, LEATHER, lambda nx, ny: 4.2 - ny)
    for y in range(y0 + 11, DESK_TOP - 11, 8):
        for x in range(cx - 12, cx + 13, 8):
            bx = x + (4 if (y // 8) % 2 else 0)
            cv.flat(bx, y, LEATHER[1])
            cv.flat(bx - 1, y - 1, LEATHER[5])
    for y in range(y0 + 5, DESK_TOP - 11):
        cv.flat(cx - 17, y, LEATHER[0])
        cv.flat(cx + 17, y, LEATHER[0])
    for x in range(cx - 16, cx + 17, 4):
        cv.flat(x, y0 + 7, BRASS[4])


def desk(cv):
    """La taula de despatx de caoba amb sobre de pell verda; el frontal amb el logotip del BCMU."""
    x0, x1 = DESK
    for y in range(DESK_TOP - 12, DESK_TOP + 1):
        for x in range(x0 - 3, x1 + 4):
            cv.put(x, y, MAHOG, 4.4 + (hr(x // 8, y, 61) - 0.5) * 0.3 + (y - DESK_TOP) * 0.045 + math.sin(x * 0.05 + y * 0.6) * 0.08)
    cv.hline(x0 - 3, x1 + 3, DESK_TOP - 12, MAHOG, 5.4)
    cv.rect(x0 - 4, DESK_TOP + 1, x1 + 4, DESK_TOP + 5, MAHOG,
            lambda x, y: 5.6 if y == DESK_TOP + 1 else (2.6 if y == DESK_TOP + 5 else 3.6))
    outline(cv, x0 - 4, DESK_TOP - 12, x1 + 4, DESK_TOP + 5, MAHOG)
    cv.rect(507, DESK_TOP - 9, 536, DESK_TOP - 1, BANKG, lambda x, y: 2.4 + (hr(x, y, 2) - 0.5) * 0.4)
    outline(cv, 507, DESK_TOP - 9, 536, DESK_TOP - 1, BANKG)
    cv.hline(508, 535, DESK_TOP - 1, BRASS, 2.6)
    for k in range(3):                                                # uns papers per signar
        cv.hline(512, 528 - k * 3, DESK_TOP - 7 + k * 2, PAPERW, 4.6)
    cv.line(530, DESK_TOP - 3, 534, DESK_TOP - 6, DARKM, 1.6)          # la ploma, damunt
    # el frontal, amb pilastres i el logotip
    y0, y1 = DESK_TOP + 6, FLOOR_Y + 1
    for y in range(y0, y1 + 1):
        for x in range(x0, x1 + 1):
            cv.put(x, y, MAHOG, 3.0 + (hr(x, y // 5, 63) - 0.5) * 0.3 + math.sin(x * 0.225 + y * 0.03) * 0.1 - (0.8 if x > x1 - 4 else 0))
    outline(cv, x0, y0, x1, y1, MAHOG)
    for px in (x0 + 4, x1 - 12):
        obox(cv, px, y0, px + 8, y1, MAHOG, 4.0)
        cv.vline(px + 3, y0 + 4, y1 - 4, MAHOG, 3.2)                  # l'estria
        cv.vline(px + 5, y0 + 4, y1 - 4, MAHOG, 3.2)
        cv.hline(px + 1, px + 7, y0 + 2, BRASS, 4.0)
        cv.hline(px + 1, px + 7, y1 - 2, BRASS, 3.4)
    obox(cv, x0 + 19, y0 + 4, x1 - 19, y1 - 4, MAHOG, 2.6)
    obox(cv, x0 + 24, y0 + 8, x1 - 24, y1 - 8, MAHOG, 3.4)
    logo(cv, (x0 + x1) // 2, (y0 + y1) // 2, k=2.0, lvl=4.6)
    cv.darken(x0 - 3, FLOOR_Y + 2, x1 + 7, FLOOR_Y + 6, 0.5)


def desk_things(cv):
    """El que hi ha damunt la taula, a part de la foto i el mòbil: el portaplomes de llautó i un llum."""
    # el portaplomes amb dues plomes
    obox(cv, 539, DESK_TOP - 8, 557, DESK_TOP - 3, BRASS, 3.8)
    cv.disc(544, DESK_TOP - 7, 2, 1, [(10, 10, 20)], 0)                # els tinters
    cv.disc(552, DESK_TOP - 7, 2, 1, [(10, 10, 20)], 0)
    cv.line(543, DESK_TOP - 8, 539, DESK_TOP - 19, DARKM, 2.0)
    cv.line(553, DESK_TOP - 8, 557, DESK_TOP - 19, DARKM, 2.0)
    cv.flat(539, DESK_TOP - 19, BRASS[5])
    cv.flat(557, DESK_TOP - 19, BRASS[5])
    # un llum de taula de llautó, apagat (ja hi ha el sol)
    cx = 565
    cv.disc(cx, DESK_TOP - 5, 5.3, 1.9, BRASS, lambda nx, ny: 4.2 - ny)
    cv.vline(cx, DESK_TOP - 27, DESK_TOP - 6, BRASS, 4.4)
    cv.vline(cx + 1, DESK_TOP - 27, DESK_TOP - 6, BRASS, 3.0)
    pts = [(cx - 8, DESK_TOP - 27), (cx - 4, DESK_TOP - 35), (cx + 4, DESK_TOP - 35), (cx + 8, DESK_TOP - 27)]
    cv.poly(pts, BANKG, lambda x, y: 3.6 - (y - (DESK_TOP - 35)) * 0.15 + (0.6 if x == cx - 3 else 0))
    outline_poly(cv, pts, BANKG)
    cv.hline(cx - 8, cx + 8, DESK_TOP - 27, BRASS, 3.6)


def photo(cv):
    """La foto d'en Rockefeller en un marc de plata, dret, amb un llacet de veritat lligat al marc."""
    x0, y0, x1, y1 = 441, 140, 457, 155
    obox(cv, x0, y0, x1, y1, SILVER, 4.2, top=1.0, side=-1.2)
    cv.flat(x0 + 1, y0 + 1, SILVER[6])
    cv.rect(x0 + 3, y0 + 3, x1 - 3, y1 - 3, [(150, 120, 140), (200, 170, 180)], lambda x, y: 0.6 + (0.3 if y < y0 + 6 else 0))
    cv.disc(449, 149.5, 4, 3.5, DOG, lambda nx, ny: 4.0 - ny * 0.6)
    cv.disc(449, 146, 2.9, 2.4, DOG, 4.4)
    cv.flat(448, 146, (30, 20, 20))
    cv.flat(450, 146, (30, 20, 20))
    cv.flat(449, 147, (60, 34, 34))
    cv.flat(449, 144, RIBBON[1])                                      # el llacet petit, a la foto
    # el llacet al cantó de dalt
    cv.sprite(['rr.rr', 'rrkrr', '..k..', '.r.r.', 'r...r'], x0 - 2, y0 - 2, {'r': (RIBBON, 1.6), 'k': (RIBBON, 0.4)})
    cv.flat(x0, y0 + 3, RIBBON[1])
    cv.darken(x1 + 1, y1 - 1, x1 + 3, y1 + 1, 0.5)


def mobil(cv):
    """El mòbil del Director, cap per avall: carcassa negra amb el cantell d'alumini i el mòdul de càmeres."""
    x0, y0, x1, y1 = 481, 149, 500, 156
    cv.darken(x0, y1 + 1, x1 + 1, y1 + 1, 0.7)                        # l'ombra
    pts = [(x0 + 1, y1), (x0 + 2, y0), (x1 - 1, y0), (x1, y1)]
    cv.poly(pts, PHONE, lambda x, y: 2.2 + (y - y0) * 0.15 + (0.6 if x < x0 + 7 else 0))
    for x in range(x0 + 2, x1):                                       # el cantell d'alumini
        cv.put(x, y0, SILVER, 4.4)
    cv.hline(x0 + 1, x1, y1, SILVER, 3.0)
    cv.vline(x0 + 1, y0 + 1, y1 - 1, SILVER, 3.6)
    cv.vline(x1, y0 + 1, y1 - 1, SILVER, 2.6)
    cv.rect(x0 + 3, y0 + 1, x0 + 8, y0 + 4, PHONE, 4.4)               # les càmeres
    cv.flat(x0 + 4, y0 + 2, (10, 10, 20))
    cv.flat(x0 + 7, y0 + 2, (10, 10, 20))
    cv.flat(x0 + 4, y0 + 3, (10, 10, 20))
    cv.flat(x0 + 7, y0 + 3, (240, 230, 200))                          # el flaix
    cv.flat(x0 + 12, y0 + 3, PHONE[5])                                # la poma (un punt)
    cv.flat(x0 + 12, y0 + 2, PHONE[4])


def bowl(cv):
    """El bol de plata d'en Rockefeller, a terra, amb el nom gravat."""
    x0, x1, y0, y1 = 588, 617, 193, 204
    cx = (x0 + x1) / 2
    pts = [(x0, y0 + 1), (x1, y0 + 1), (x1 - 4, y1), (x0 + 4, y1)]
    cv.poly(pts, SILVER, lambda x, y: 4.4 - abs(x - cx + 5) * 0.09 - (y - y0) * 0.09)
    outline_poly(cv, pts, SILVER)
    cv.disc(cx, y0 + 1, (x1 - x0) / 2, 2.9, SILVER, lambda nx, ny: 2.4 + ny * 0.8)   # la boca
    cv.disc(cx, y0 + 2, (x1 - x0) / 2 - 4, 1.6, [(140, 180, 196), (190, 220, 230)], 0.8)   # l'aigua
    cv.hline(x0 + 7, x1 - 7, y0 + 7, SILVER, 2.2)                     # el nom gravat (ratlleta)
    for x in range(x0 + 8, x1 - 7, 3):
        cv.put(x, y0 + 6, SILVER, 2.6)
    cv.vline(x0 + 5, y0 + 4, y0 + 6, SILVER, 6.0)                     # la lluïssor
    cv.darken(x0 + 1, y1 + 1, x1, y1 + 3, 0.5)


# ─── Composició ────────────────────────────────────────────────────────────

def bg(cv, f=None):
    wall(cv)
    floor(cv)
    sconce(cv, 141)
    door(cv)
    diplomas(cv)
    sofa(cv)
    curtain(cv, 187, 203, True)
    curtain(cv, 397, 413, False)
    window(cv, f)
    dog_bed(cv)
    globe_bar(cv)
    bookcase(cv)
    portrait(cv)
    chair(cv)
    desk(cv)
    desk_things(cv)
    photo(cv)
    mobil(cv)
    bowl(cv)


PROPS = {}


# ─── Animació: el llac i el Jet d'Eau ──────────────────────────────────────
# A 640, el doble de fotogrames a la meitat de temps: l'aigua i el Jet d'Eau, més suaus.

ANIM_N = 24


def _frames():
    from hd.rooms.comu import _diff
    base = Canvas(light=LIGHT)
    bg(base)
    frames = []
    for i in range(ANIM_N):
        cv = Canvas(light=LIGHT)
        bg(cv, f=i)
        frames.append(_diff(cv.img, base.img))
    return frames


ANIMS = {'llac': {'frames': _frames, 'frameDuration': 70}}


# ─── Geometria a 640 ───────────────────────────────────────────────────────

GEOMETRIA = {
    'things': {
        'porta': {'rect': (19, 53, 82, 200), 'walk': (51, 248)},
        'finestra': {'rect': (200, 27, 400, 133), 'walk': (301, 248)},
        'foto': {'rect': (438, 137, 459, 156), 'walk': (448, 251)},
        'mobil': {'rect': (480, 148, 501, 157), 'walk': (488, 251)},
        'bol': {'rect': (586, 189, 619, 206), 'walk': (595, 253)},
    },
    'spawns': {'ballester': (115, 248), 'bonfill': (395, 245), 'vet': (240, 261)},
    'walkable': [(19, 236), (621, 236), (632, 271), (8, 271)],
}
