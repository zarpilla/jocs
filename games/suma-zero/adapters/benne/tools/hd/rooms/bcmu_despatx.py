"""
El despatx del Director (Acte 3, la Vet), la planta noble del BCMU, Ginebra, les onze i quart. Art definitiu:
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
"""
import math

from hd.pix import Light, W, H, hr, WALNUT
from hd.rooms.comu import obox, outline
from hd.rooms.pis_cuina import outline_poly
from hd.rooms.bcmu import MARBLE, BRASS, MAHOG, CARPET, logo
from hd.rooms.bcmu_vestibul import DARKM, DOG, frame
from hd.rooms.bcmu_avantdespatx import wall, sconce, BANKG, PAPERW

FLOOR_Y = 150
DESK_TOP = 118
DESK = (316, 430)
WIN = (150, 20, 300, 100)

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

LIGHT = Light(ambient=0.0, vignette=(60, 30), floor_fade=(190, 30))
LIGHT.point(225, 60, r=290, k=2.4, squash=0.7, power=1.3)            # el finestral
LIGHT.point(225, 175, r=110, k=0.8, squash=2.4, power=1.6)           # el sol a terra
for _sx in (106,):                                                   # l'aplic
    LIGHT.point(_sx, 62, r=50, k=0.7, squash=1.1, power=1.8)


# ─── Terra ─────────────────────────────────────────────────────────────────

def floor(cv):
    """Parquet de llistons encerat, en perspectiva, i una catifa blau marí amb sanefa d'or."""
    for y in range(FLOOR_Y, H):
        dep = (y - FLOOR_Y) / (H - FLOOR_Y)
        v = (y - FLOOR_Y) * 1.7 / (1 + dep * 0.6)
        for x in range(W):
            u = (x - W / 2) / (0.55 + dep * 0.9) + W / 2
            col = int(u // 10)
            fv = v + hr(col, 3) * 40                                    # les juntes, a trencajunts
            seam = (u % 10) < 0.9 or (fv % 40) < 0.7
            n = (hr(col, int(fv // 40), 4) - 0.5) * 0.7 + (hr(x // 4, y, 5) - 0.5) * 0.25
            cv.put(x, y, WALNUT, (3.0 if seam else 4.4 + n))
            # la catifa
            if 120 <= u <= 400 and v >= 10:
                ru = min(u - 120, 400 - u)
                rv = v - 10
                edge = min(ru, rv)
                n2 = (hr(x, y, 6) - 0.5) * 0.6
                if edge < 2:
                    cv.put(x, y, BRASS, 2.2 + n2)
                elif edge < 4:
                    cv.put(x, y, VELVET, 2.6 + n2)
                elif edge < 6:
                    cv.put(x, y, BRASS, 3.0 + n2)
                else:
                    mot = abs(((u - 128) % 24) - 12) + abs(((rv - 6) % 16) - 8) * 1.5 < 3
                    cv.put(x, y, VELVET, (3.4 if mot else 2.4) + n2)
    cv.darken(0, FLOOR_Y, W - 1, FLOOR_Y + 1, 0.5)
    # el sol del finestral, estirat a terra
    cv.tint(0, FLOOR_Y + 2, W - 1, H - 1, (255, 236, 190),
            lambda x, y: 0.16 * max(0, 1 - abs(x - 225 - (y - 150) * 0.6) / 90) * max(0, 1 - (y - 152) / 52))


# ─── El finestral ──────────────────────────────────────────────────────────

def view(cv, x0, y0, x1, y1):
    """El llac de Ginebra a mig matí: cel, els Alps, l'altra riba, l'aigua, el Jet d'Eau i les teulades."""
    hz = 58                                                           # la línia de l'altra riba
    for y in range(y0, y1 + 1):
        for x in range(x0, x1 + 1):
            if y < hz:
                cv.put(x, y, SKYD, 4.6 - (y - y0) * 0.06 + (hr(x // 3, y // 2, 1) - 0.5) * 0.2, lit=0)
            else:
                d = (y - hz) / (y1 - hz)
                glint = 1.2 if (hr(x // 3, y, 2) > 0.93 and abs(x - 200) < 60) else 0
                cv.put(x, y, LAKE, 3.6 - d * 1.2 + glint + math.sin(x * 0.5 + y * 2.1) * 0.25, lit=0)
    # uns núvols
    for (cx, cy, rx) in ((176, 30, 14), (194, 27, 10), (266, 34, 16), (284, 31, 9)):
        cv.disc(cx, cy, rx, rx * 0.35, SKYD, lambda nx, ny: 5.4 - ny * 0.8, lit=0)
    # els Alps: dues serralades, la de darrere amb neu
    for x in range(x0, x1 + 1):
        far = 46 - 6 * math.sin((x - x0) * 0.07) - 4 * math.sin((x - x0) * 0.19 + 1) - (4 if 236 < x < 262 else 0) * (1 - abs(x - 249) / 13)
        near = 52 - 3 * math.sin((x - x0) * 0.11 + 2) - 2 * math.sin(x * 0.3)
        for y in range(int(far), hz):
            snow = y < far + 3 + 2 * math.sin(x * 0.7)
            cv.put(x, y, ALPS, (4.6 if snow else 2.4) + (0.6 if (x + y) % 7 == 0 and snow else 0), lit=0)
        for y in range(int(near), hz):
            cv.put(x, y, ALPS, 1.2 + (y - near) * 0.1, lit=0)
    # l'altra riba: una ratlla verda i casetes
    for x in range(x0, x1 + 1):
        cv.put(x, hz - 1, TREE, 2.0, lit=0)
        cv.put(x, hz, TREE, 1.4, lit=0)
        if hr(x // 2, 9) > 0.6:
            cv.flat(x, hz - 2, TOWN[3])
    # el Jet d'Eau: un ploma blanca que el vent tomba una mica
    jx, jb, jt = 236, 76, 30
    for y in range(jt, jb + 1):
        t = (jb - y) / (jb - jt)
        cx = jx + t * t * 4
        w = 0.8 + t * 1.6
        for x in range(int(cx - w), int(cx + w) + 1):
            cv.put(x, y, SKYD, 5.4 - abs(x - cx) / w * 0.8, lit=0)
    cv.disc(jx + 5, jt + 1, 4, 3, SKYD, lambda nx, ny: 5.2 - nx * 0.6, lit=0)   # l'esprai de dalt
    for i in range(16):
        cv.flat(jx + 6 + int(hr(i, 3) * 8), jt + int(hr(i, 4) * 10), SKYD[4])
    cv.hline(jx - 4, jx + 4, jb + 1, LAKE, 5.6, lit=0)
    cv.rect(jx - 8, jb + 2, jx - 4, jb + 2, TOWN, 3.0, lit=0)          # la punta del moll
    # un vaixell de rodes
    bx, by = 186, 72
    cv.rect(bx, by, bx + 14, by + 2, TOWN, 4.2, lit=0)
    cv.rect(bx + 3, by - 2, bx + 10, by - 1, TOWN, 3.2, lit=0)
    cv.rect(bx + 6, by - 4, bx + 7, by - 3, ROOF, 2.0, lit=0)
    cv.hline(bx + 15, bx + 22, by + 2, LAKE, 5.0, lit=0)
    # les teulades de baix (el barri de davant)
    for i in range(12):
        hx = x0 + i * 13 - 4 + int(hr(i, 7) * 4)
        top = y1 - 8 - int(hr(i, 8) * 6)
        cv.rect(hx, top, hx + 12, y1, TOWN, 2.8 + hr(i, 10) * 0.8, lit=0)
        cv.poly([(hx - 1, top), (hx + 6, top - 5), (hx + 13, top)], ROOF, 2.6 + hr(i, 11), lit=0)
        for wx in range(hx + 2, hx + 11, 4):
            cv.flat(wx, top + 3, TOWN[0])
    for i in range(8):                                                # uns arbres del passeig
        tx = x0 + 6 + i * 19 + int(hr(i, 12) * 6)
        cv.disc(tx, y1 - 9, 4, 3, TREE, lambda nx, ny: 2.6 - ny, lit=0)


def window(cv):
    """El finestral: marc de caoba, travessers, la vista, el reflex del vidre i l'ampit de marbre."""
    x0, y0, x1, y1 = WIN
    view(cv, x0 + 3, y0 + 3, x1 - 3, y1 - 3)
    cv.tint(x0 + 3, y0 + 3, x1 - 3, y1 - 3, (255, 255, 255), lambda x, y: 0.16 if (x + y) % 46 < 5 else 0.0)
    # el marc i els travessers
    obox(cv, x0, y0, x1, y0 + 3, MAHOG, 4.0)
    obox(cv, x0, y1 - 3, x1, y1, MAHOG, 3.6)
    for mx in (x0, x0 + 50, x0 + 100, x1 - 3):
        cv.rect(mx, y0, mx + 3, y1, MAHOG, lambda x, y, m=mx: 3.8 + (0.8 if x == m else 0) - (0.8 if x == m + 3 else 0))
    cv.rect(x0, 48, x1, 49, MAHOG, 4.4)
    outline(cv, x0, y0, x1, y1, MAHOG)
    # l'ampit
    cv.rect(x0 - 4, y1 + 1, x1 + 4, y1 + 4, MARBLE, lambda x, y: 6.0 if y == y1 + 1 else 4.6)
    outline(cv, x0 - 4, y1 + 1, x1 + 4, y1 + 4, MARBLE)
    cv.darken(x0 - 2, y1 + 5, x1 + 2, y1 + 6, 0.4)


def curtain(cv, x0, x1, left):
    """Una cortina de vellut blau marí, lligada amb un cordó d'or a mitja alçada."""
    tie = 104
    for y in range(14, FLOOR_Y + 1):
        # lligada: més estreta al cordó
        pinch = max(0, 1 - abs(y - tie) / 40) * 4
        a = x0 + (pinch if left else 0)
        b = x1 - (0 if left else pinch)
        for x in range(int(a), int(b) + 1):
            fold = math.sin((x - x0) * 1.3 + y * 0.02) * 0.9
            cv.put(x, y, VELVET, 3.0 + fold + (0.6 if (x - a) < 1 else 0) - (0.6 if (b - x) < 1 else 0))
        cv.flat(a, y, VELVET[0])
        cv.flat(b, y, VELVET[0])
    cv.rect(x0 + 1, tie - 1, x1 - 1, tie + 1, BRASS, 4.4)
    cx = x1 + 1 if left else x0 - 1
    cv.line(cx, tie + 1, cx, tie + 8, BRASS, 4.0)                   # la borla
    cv.disc(cx, tie + 10, 1.6, 2.4, BRASS, lambda nx, ny: 4.4 - ny)


# ─── La porta ──────────────────────────────────────────────────────────────

def door(cv):
    """La porta doble de caoba, des de dins: la mateixa de l'avantdespatx, amb poms de llautó."""
    x0, y0, x1, y1 = 18, 48, 58, FLOOR_Y - 1
    obox(cv, x0 - 4, y0 - 4, x1 + 4, y1, MAHOG, 4.2, top=1.2)
    obox(cv, x0 - 5, 40, x1 + 5, y0 - 4, MAHOG, 4.0, top=1.4)
    cv.hline(x0 - 4, x1 + 4, 42, BRASS, 4.0)
    for lx0, lx1 in ((x0, (x0 + x1) // 2), ((x0 + x1) // 2 + 1, x1)):
        for y in range(y0, y1 + 1):
            for x in range(lx0, lx1 + 1):
                n = (hr(x, y // 6, 51) - 0.5) * 0.3 + math.sin(x * 0.5 + y * 0.03) * 0.12
                cv.put(x, y, MAHOG, 3.4 + n)
        for (py0, py1) in ((y0 + 5, y0 + 42), (y0 + 48, y1 - 6)):
            a, b = lx0 + 3, lx1 - 3
            cv.rect(a, py0, b, py1, MAHOG, 3.8)
            cv.hline(a, b, py0, MAHOG, 1.4)
            cv.vline(a, py0, py1, MAHOG, 1.6)
            cv.hline(a, b, py1, MAHOG, 5.2)
            cv.vline(b, py0, py1, MAHOG, 5.0)
        outline(cv, lx0, y0, lx1, y1, MAHOG)
    cx = (x0 + x1) // 2
    for px in (cx - 3, cx + 4):
        cv.disc(px, 100, 1.8, 1.8, BRASS, lambda nx, ny: 4.6 - ny - nx * 0.4)
    cv.darken(x0 - 4, FLOOR_Y, x1 + 6, FLOOR_Y + 3, 0.45)


# ─── El sofà i els diplomes ────────────────────────────────────────────────

def diplomas(cv):
    """Tres diplomes en marcs daurats: pergamí, lletra petita i un segell vermell."""
    for i, (x0, y0) in enumerate(((78, 44), (100, 38), (122, 44))):
        x1, y1 = x0 + 18, y0 + (24 if i != 1 else 28)
        obox(cv, x0, y0, x1, y1, BRASS, 3.8, top=1.0, side=-1.0)
        cv.rect(x0 + 2, y0 + 2, x1 - 2, y1 - 2, PAPERW, 4.2)
        cv.hline(x0 + 5, x1 - 5, y0 + 5, [(60, 40, 30)], 0)
        for k in range(3):
            cv.hline(x0 + 4, x1 - 4 - (k % 2) * 3, y0 + 9 + k * 3, [(150, 140, 126)], 0)
        sx = (x0 + x1) // 2
        cv.flat(sx - 2, y1 - 2, (150, 30, 30))                          # les cintes i el segell de lacre
        cv.flat(sx + 2, y1 - 2, (150, 30, 30))
        cv.sprite(['.aa.', 'abba', 'abba', '.aa.'], sx - 2, y1 - 7, {'a': (150, 30, 30), 'b': (200, 56, 46)})
        cv.darken(x1 + 1, y0 + 2, x1 + 2, y1 + 2, 0.5)


def sofa(cv):
    """Un Chesterfield de pell granat: respatller i braços a la mateixa alçada, capitonè, coixins i potes de bola."""
    x0, x1 = 68, 146
    top, seat, base = 110, 129, 146
    # el respatller capitonat: rombes entre botons
    for y in range(top + 2, seat + 1):
        for x in range(x0 + 10, x1 - 9):
            row = (y - top - 2) // 6
            off = 3 if row % 2 else 0
            dx = ((x - x0 + off) % 6) - 3
            dy = ((y - top - 2) % 6) - 3
            d = abs(dx) + abs(dy)
            cv.put(x, y, LEATHER, 4.0 - d * 0.28 - (y - top) * 0.02)
            if d == 0:
                cv.flat(x, y, LEATHER[1])
    cv.rect(x0 + 10, top, x1 - 9, top + 2, LEATHER, lambda x, y: 5.0 - (y - top) * 0.6)   # el cantell de dalt, enrotllat
    cv.hline(x0 + 10, x1 - 9, top, LEATHER, 0.6)
    # els coixins
    for k in range(3):
        cx0 = x0 + 10 + k * 20
        cv.rect(cx0, seat - 1, cx0 + 19, seat + 5, LEATHER, lambda x, y: 4.4 + (1.0 if y == seat - 1 else 0) - (0.9 if y > seat + 3 else 0))
        outline(cv, cx0, seat - 1, cx0 + 19, seat + 5, LEATHER)
    # la faldilla, amb el filet de claus de llautó
    cv.rect(x0 + 2, seat + 6, x1 - 2, base, LEATHER, lambda x, y: 3.0 - (y - seat) * 0.04)
    for x in range(x0 + 4, x1 - 3, 3):
        cv.flat(x, seat + 7, BRASS[5] if x % 2 else BRASS[3])
    outline(cv, x0 + 2, seat + 6, x1 - 2, base, LEATHER)
    # els braços: a l'alçada del respatller, amb el rotlle de davant
    for ax in (x0, x1 - 10):
        cv.rect(ax, top + 2, ax + 10, base, LEATHER, lambda x, y, a=ax: 3.6 + (0.8 if x < a + 4 else 0) - (y - top) * 0.02)
        for y in range(top + 6, base, 5):
            cv.flat(ax + 5, y, LEATHER[1])
        cv.disc(ax + 5, top + 3, 5.5, 3, LEATHER, lambda nx, ny: 5.0 - ny * 1.2 - nx * 0.3)
        cv.ring(ax + 5, top + 3, 2, LEATHER, 2.4, step=30)
        for y in range(top + 3, base + 1):
            cv.flat(ax, y, LEATHER[0])
            cv.flat(ax + 10, y, LEATHER[0])
    for lx in (x0 + 4, x1 - 5):                                       # les potes de bola
        cv.disc(lx, base + 2, 1.8, 1.8, MAHOG, lambda nx, ny: 4.0 - ny)
    cv.darken(x0 - 2, FLOOR_Y, x1 + 4, FLOOR_Y + 4, 0.5)


# ─── El llit d'en Rockefeller i el globus bar ─────────────────────────────

def dog_bed(cv):
    """Un llit de gos de vellut granat, amb la vora alta i un coixí de seda daurada (i un os de joguina)."""
    cx, x0, x1, y1 = 175, 155, 195, 153
    cv.disc(cx, y1 - 9, 20, 7, CARPET, lambda nx, ny: 3.4 - ny * 1.2)          # la vora de darrere, alta
    cv.disc(cx, y1 - 4, 20, 4.4, CARPET, lambda nx, ny: 4.2 - ny * 0.6)        # la de davant
    cv.disc(cx, y1 - 7, 15, 4, BRASS, lambda nx, ny: 4.0 - ny * 0.8 + (hr(int(nx * 5), 1) - 0.5) * 0.4)   # el coixí
    cv.disc(cx + 1, y1 - 6, 7, 1.6, BRASS, 3.2)                                # el clot d'en Rockefeller
    cv.hline(x0 + 4, x1 - 4, y1 - 2, CARPET, 5.0)                              # el ribet
    for (bx, by) in ((cx - 7, y1 - 9), (cx - 3, y1 - 9)):                      # l'os
        cv.disc(bx, by, 1.2, 1.2, PAPERW, 4.6)
    cv.hline(cx - 6, cx - 4, y1 - 9, PAPERW, 4.2)
    cv.darken(x0 + 2, y1 + 1, x1 - 1, y1 + 2, 0.5)


def globe_bar(cv):
    """El globus terraqüi antic sobre un peu de caoba de tres potes: s'obre i és un bar."""
    cx, cy, r = 240, 122, 11
    OCEAN = [(26, 44, 44), (40, 66, 64), (60, 92, 84), (90, 122, 104), (130, 156, 128), (176, 190, 156)]
    LAND = [(60, 40, 20), (100, 72, 36), (146, 110, 60), (190, 156, 96), (224, 198, 140)]
    # el peu: tres potes corbes i el travesser
    for lx in (cx - 11, cx, cx + 11):
        cv.line(cx + (lx - cx) // 2, cy + 12, lx, FLOOR_Y + 1, MAHOG, 3.4 if lx != cx else 2.4)
    cv.rect(cx - 9, 142, cx + 9, 143, MAHOG, 3.6)
    cv.disc(cx, cy + 13, 6, 2, MAHOG, 3.8)
    # l'horitzó de fusta (on s'obre)
    cv.disc(cx, cy + 1, r + 3, 3, MAHOG, lambda nx, ny: 4.4 - ny)
    for y in range(cy - r, cy + r + 1):
        for x in range(cx - r, cx + r + 1):
            nx, ny = (x - cx) / r, (y - cy) / r
            if nx * nx + ny * ny <= 1:
                land = math.sin(nx * 4.2 + 1.4) + math.cos(ny * 5 + nx * 2.4) > 0.9 or (nx > 0.2 and abs(ny - 0.2) < 0.25 and nx < 0.6)
                lv = 3.6 - nx * 0.9 - ny * 1.1 - (nx * nx + ny * ny) * 0.6
                cv.put(x, y, LAND if land else OCEAN, lv)
    cv.disc(cx, cy + 1, r + 3, 1.2, MAHOG, lambda nx, ny: 4.6)          # el cantell de l'horitzó, per davant
    cv.hline(cx - r - 3, cx + r + 3, cy + 2, MAHOG, 2.0)
    for k in range(r + 3):                                            # el meridià de llautó, inclinat
        a = math.radians(200 + k / (r + 2) * 140)
        cv.put(round(cx + math.cos(a) * (r + 1.5)), round(cy + math.sin(a) * (r + 1.5)), BRASS, 4.4)
    cv.disc(cx - 3, cy - r - 1, 1.2, 1.2, BRASS, 5.0)
    cv.darken(cx - 13, FLOOR_Y + 1, cx + 13, FLOOR_Y + 3, 0.5)


# ─── La llibreria ──────────────────────────────────────────────────────────

def bookcase(cv):
    """La llibreria de caoba de darrere la taula: llibres de finances relligats, iguals i sense obrir."""
    x0, y0, x1, y1 = 322, 24, 428, 118
    obox(cv, x0 - 3, y0 - 6, x1 + 3, y0, MAHOG, 4.0, top=1.4)
    cv.hline(x0 - 2, x1 + 2, y0 - 3, BRASS, 3.8)
    obox(cv, x0, y0, x1, y1, MAHOG, 2.4)
    for sy in range(y0 + 2, y1 - 6, 19):                              # quatre prestatges
        cv.rect(x0 + 3, sy, x1 - 3, sy + 16, MAHOG, 1.2)
        bx = x0 + 4
        i = 0
        while bx < x1 - 6:
            bw = 3 + int(hr(sy, i, 1) * 2)
            bh = 11 + int(hr(sy, i, 2) * 4)
            if hr(sy, i, 3) > 0.9 and bx < x1 - 16:                    # un forat, o un llibre ajagut
                bx += 6
                i += 1
                continue
            set_ = BOOKS[int(hr(sy, i // 5, 4) * len(BOOKS))]
            cv.rect(bx, sy + 16 - bh, bx + bw - 1, sy + 16, set_, lambda x, y, b=bx: 1.4 + (0.8 if x == b else 0))
            cv.hline(bx, bx + bw - 1, sy + 18 - bh, BRASS, 3.6)
            cv.hline(bx, bx + bw - 1, sy + 13, BRASS, 3.0)
            bx += bw
            i += 1
        cv.rect(x0 + 2, sy + 17, x1 - 2, sy + 18, MAHOG, lambda x, y: 5.0 if y == sy + 17 else 3.0)
    for vx in (x0 + 2, x1 - 2):
        cv.vline(vx, y0 + 1, y1 - 1, MAHOG, 4.4)


def portrait(cv):
    """El retrat a l'oli d'en Rockefeller, amb llacet, sobre un coixí de vellut."""
    x0, y0, x1, y1 = 440, 30, 474, 78
    frame(cv, x0, y0, x1, y1)
    for y in range(y0 + 4, y1 - 3):
        for x in range(x0 + 4, x1 - 3):
            cv.put(x, y, VELVET, 2.0 + (hr(x // 2, y // 2, 7) - 0.5) * 0.5 + math.sin(x * 0.4) * 0.3)
    cx = (x0 + x1) // 2
    cv.disc(cx, 66, 11, 4, CARPET, lambda nx, ny: 3.8 - ny)           # el coixí
    cv.disc(cx, 58, 8, 7, DOG, lambda nx, ny: 3.6 - ny * 0.6 + (hr(int(nx * 6), int(ny * 5), 3) - 0.5) * 0.7)
    cv.disc(cx, 47, 6, 5.6, DOG, lambda nx, ny: 4.0 - ny * 0.6 - nx * 0.2 + (hr(int(nx * 5), int(ny * 5), 4) - 0.5) * 0.6)
    for s in (-1, 1):                                                 # les orelles
        cv.disc(cx + s * 6, 49, 2.4, 3.6, DOG, 2.6)
    cv.flat(cx - 2, 46, (20, 14, 14))
    cv.flat(cx + 2, 46, (20, 14, 14))
    cv.flat(cx, 49, (40, 24, 24))
    cv.rect(cx - 2, 41, cx + 2, 42, RIBBON, 1.6)                       # el llacet
    cv.flat(cx, 41, RIBBON[0])
    obox(cv, cx - 9, 80, cx + 9, 85, BRASS, 4.6)                       # la placa
    cv.hline(cx - 6, cx + 6, 82, BRASS, 2.4)


# ─── La taula ──────────────────────────────────────────────────────────────

def chair(cv):
    """La cadira del Director: respatller alt de pell capitonada, amb claus de llautó."""
    cx, y0 = 396, 84
    cv.rect(cx - 13, y0 + 3, cx + 13, DESK_TOP - 8, LEATHER, lambda x, y: 3.4 - abs(x - cx) * 0.04 + (0.6 if x < cx - 8 else 0))
    cv.disc(cx, y0 + 4, 13, 4, LEATHER, lambda nx, ny: 4.2 - ny)
    for y in range(y0 + 8, DESK_TOP - 8, 6):
        for x in range(cx - 9, cx + 10, 6):
            cv.flat(x + (3 if (y // 6) % 2 else 0), y, LEATHER[1])
    for y in range(y0 + 4, DESK_TOP - 8):
        cv.flat(cx - 13, y, LEATHER[0])
        cv.flat(cx + 13, y, LEATHER[0])
    for x in range(cx - 12, cx + 13, 3):
        cv.flat(x, y0 + 5, BRASS[4])


def desk(cv):
    """La taula de despatx de caoba amb sobre de pell verda; el frontal amb el logotip del BCMU."""
    x0, x1 = DESK
    for y in range(DESK_TOP - 9, DESK_TOP + 1):
        for x in range(x0 - 2, x1 + 3):
            cv.put(x, y, MAHOG, 4.4 + (hr(x // 6, y, 61) - 0.5) * 0.3 + (y - DESK_TOP) * 0.06)
    cv.hline(x0 - 2, x1 + 2, DESK_TOP - 9, MAHOG, 5.4)
    cv.rect(x0 - 3, DESK_TOP + 1, x1 + 3, DESK_TOP + 4, MAHOG, lambda x, y: 5.6 if y == DESK_TOP + 1 else 3.6)
    outline(cv, x0 - 3, DESK_TOP - 9, x1 + 3, DESK_TOP + 4, MAHOG)
    cv.rect(380, DESK_TOP - 7, 402, DESK_TOP - 1, BANKG, lambda x, y: 2.4 + (hr(x, y, 2) - 0.5) * 0.4)
    outline(cv, 380, DESK_TOP - 7, 402, DESK_TOP - 1, BANKG)
    cv.hline(381, 401, DESK_TOP - 1, BRASS, 2.6)
    for k in range(3):                                                # uns papers per signar
        cv.hline(384, 396 - k * 2, DESK_TOP - 5 + k * 2, PAPERW, 4.6)
    # el frontal, amb pilastres i el logotip
    y0, y1 = DESK_TOP + 5, FLOOR_Y + 1
    for y in range(y0, y1 + 1):
        for x in range(x0, x1 + 1):
            cv.put(x, y, MAHOG, 3.0 + (hr(x, y // 4, 63) - 0.5) * 0.3 + math.sin(x * 0.3 + y * 0.04) * 0.1 - (0.8 if x > x1 - 3 else 0))
    outline(cv, x0, y0, x1, y1, MAHOG)
    for px in (x0 + 3, x1 - 9):
        obox(cv, px, y0, px + 6, y1, MAHOG, 4.0)
        cv.hline(px + 1, px + 5, y0 + 2, BRASS, 4.0)
        cv.hline(px + 1, px + 5, y1 - 2, BRASS, 3.4)
    obox(cv, x0 + 14, y0 + 3, x1 - 14, y1 - 3, MAHOG, 2.6)
    obox(cv, x0 + 18, y0 + 6, x1 - 18, y1 - 6, MAHOG, 3.4)
    logo(cv, (x0 + x1) // 2, (y0 + y1) // 2, k=1.5, lvl=4.6)
    cv.darken(x0 - 2, FLOOR_Y + 2, x1 + 5, FLOOR_Y + 5, 0.5)


def desk_things(cv):
    """El que hi ha damunt la taula, a part de la foto i el mòbil: el portaplomes de llautó i un llum."""
    # el portaplomes amb dues plomes
    obox(cv, 404, DESK_TOP - 6, 418, DESK_TOP - 2, BRASS, 3.8)
    cv.line(407, DESK_TOP - 6, 404, DESK_TOP - 14, DARKM, 2.0)
    cv.line(415, DESK_TOP - 6, 418, DESK_TOP - 14, DARKM, 2.0)
    cv.flat(404, DESK_TOP - 14, BRASS[5])
    cv.flat(418, DESK_TOP - 14, BRASS[5])
    # un llum de taula de llautó, apagat (ja hi ha el sol)
    cx = 424
    cv.disc(cx, DESK_TOP - 4, 4, 1.4, BRASS, lambda nx, ny: 4.2 - ny)
    cv.vline(cx, DESK_TOP - 20, DESK_TOP - 5, BRASS, 4.4)
    pts = [(cx - 6, DESK_TOP - 20), (cx - 3, DESK_TOP - 26), (cx + 3, DESK_TOP - 26), (cx + 6, DESK_TOP - 20)]
    cv.poly(pts, BANKG, lambda x, y: 3.6 - (y - (DESK_TOP - 26)) * 0.2)
    outline_poly(cv, pts, BANKG)


def photo(cv):
    """La foto d'en Rockefeller en un marc de plata, dret, amb un llacet de veritat lligat al marc."""
    x0, y0, x1, y1 = 331, 105, 343, 116
    obox(cv, x0, y0, x1, y1, SILVER, 4.2, top=1.0, side=-1.2)
    cv.rect(x0 + 2, y0 + 2, x1 - 2, y1 - 2, [(150, 120, 140), (200, 170, 180)], 0.6)
    cv.disc(337, 111.5, 3, 2.6, DOG, lambda nx, ny: 4.0 - ny * 0.6)
    cv.disc(337, 109, 2.2, 1.8, DOG, 4.4)
    cv.flat(336, 109, (30, 20, 20))
    cv.flat(338, 109, (30, 20, 20))
    # el llacet al cantó de dalt
    cv.sprite(['r.r', '.r.', 'r.r'], x0 - 1, y0 - 1, {'r': (RIBBON, 1.6)})
    cv.flat(x0, y0 + 2, RIBBON[1])
    cv.darken(x1 + 1, y1 - 1, x1 + 2, y1 + 1, 0.5)


def mobil(cv):
    """El mòbil del Director, cap per avall: carcassa negra amb el cantell d'alumini i el mòdul de càmeres."""
    x0, y0, x1, y1 = 361, 112, 375, 117
    cv.darken(x0, y1 + 1, x1 + 1, y1 + 1, 0.7)                        # l'ombra
    pts = [(x0 + 1, y1), (x0 + 2, y0), (x1 - 1, y0), (x1, y1)]
    cv.poly(pts, PHONE, lambda x, y: 2.2 + (y - y0) * 0.2 + (0.6 if x < x0 + 5 else 0))
    for x in range(x0 + 2, x1):                                       # el cantell d'alumini
        cv.put(x, y0, SILVER, 4.4)
    cv.hline(x0 + 1, x1, y1, SILVER, 3.0)
    cv.vline(x0 + 1, y0 + 1, y1 - 1, SILVER, 3.6)
    cv.vline(x1, y0 + 1, y1 - 1, SILVER, 2.6)
    cv.rect(x0 + 3, y0 + 1, x0 + 6, y0 + 3, PHONE, 4.4)               # les càmeres
    cv.flat(x0 + 4, y0 + 2, (10, 10, 20))
    cv.flat(x0 + 6, y0 + 2, (10, 10, 20))
    cv.flat(x0 + 9, y0 + 2, PHONE[5])                                 # la poma (un punt)


def bowl(cv):
    """El bol de plata d'en Rockefeller, a terra, amb el nom gravat."""
    x0, x1, y0, y1 = 441, 463, 145, 153
    cx = (x0 + x1) / 2
    pts = [(x0, y0 + 1), (x1, y0 + 1), (x1 - 3, y1), (x0 + 3, y1)]
    cv.poly(pts, SILVER, lambda x, y: 4.4 - abs(x - cx + 4) * 0.12 - (y - y0) * 0.12)
    outline_poly(cv, pts, SILVER)
    cv.disc(cx, y0 + 1, (x1 - x0) / 2, 2.2, SILVER, lambda nx, ny: 2.4 + ny * 0.8)   # la boca
    cv.disc(cx, y0 + 1.6, (x1 - x0) / 2 - 3, 1.2, [(140, 180, 196), (190, 220, 230)], 0.8)   # l'aigua
    cv.hline(x0 + 5, x1 - 5, y0 + 5, SILVER, 2.2)                     # el nom gravat (ratlleta)
    cv.flat(x0 + 4, y0 + 3, SILVER[6])
    cv.darken(x0 + 1, y1 + 1, x1, y1 + 2, 0.5)


# ─── Composició ────────────────────────────────────────────────────────────

def bg(cv):
    wall(cv)
    floor(cv)
    sconce(cv, 106)
    door(cv)
    diplomas(cv)
    sofa(cv)
    curtain(cv, 140, 152, True)
    curtain(cv, 298, 310, False)
    window(cv)
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
