"""
L'Última Arrel — epíleg, segona vinyeta (pantalla sencera de 640×360, sense HUD): «L'Ajuntament va mirar els plànols
de 1923 i va treure el permís d'obres a NaturaPlus. El Registrador Bufó va arxivar el cas amb tres segells.»

El taulell del Registrador, vist de dalt, amb la llum càlida d'un llum de taula (a dalt a l'esquerra): a l'esquerra,
els plànols de 1923 desplegats (paper groguenc, el rierol, les arrels i el roure dibuixats a tinta sèpia); a la dreta,
la carpeta de l'expedient de NaturaPlus amb els **tres segells** vermells de gripau, un al costat de l'altre (l'últim,
encara lluent); i a baix a la dreta, el segell de goma i el tamponet de tinta.
"""
import math

import hd640  # noqa: F401  (abans de cap hd.rooms: posa la llibreria a 640×360)

from hd.pix import Light, W, H
from hd640.rooms.arrel_comu import PLANK, CREAM, REDL, IRONK, fbm, hr, lletres, ample

LIGHT = Light(ambient=0.35, vignette=(80, 30), floor_fade=None)
LIGHT.width = W
LIGHT.point(90, -40, r=620, k=1.3, squash=0.9, power=1.3)

PAPER = [(64, 52, 36), (112, 96, 66), (160, 140, 100), (200, 182, 136), (226, 210, 164), (242, 230, 190)]
SEPIA = [(40, 24, 14), (70, 44, 26), (104, 70, 42), (140, 100, 62)]
MANILA = [(70, 50, 22), (120, 90, 44), (168, 132, 70), (204, 168, 100), (228, 198, 132), (244, 222, 164)]
TINTA = [(36, 6, 8), (90, 14, 16), (150, 24, 24), (196, 40, 34), (226, 70, 52)]

PLANOL = (40, 46, 330, 300)                            # x0, y0, x1, y1
CARPETA = (360, 70, 606, 290)
SEGELLS = [(410, 246), (480, 252), (550, 244)]


def taulell(cv):
    """La fusta del taulell, amb la veta horitzontal."""
    for y in range(H):
        for x in range(W):
            veta = fbm(x / 60, y / 3.5, 3)
            cv.put(x, y, PLANK, 2.6 + (veta - 0.5) * 2.4 + (0.6 if (y % 46) == 0 else 0) * -1, lit=1.0)


def ombra_rect(cv, x0, y0, x1, y1, dx=6, dy=7):
    cv.darken(x0 + dx, y0 + dy, x1 + dx, y1 + dy, 0.55)


def planol(cv):
    """Els plànols de 1923: el paper amb els plecs, el marc, el rierol, les arrels del roure i el títol."""
    x0, y0, x1, y1 = PLANOL
    ombra_rect(cv, x0, y0, x1, y1)
    for y in range(y0, y1):
        for x in range(x0, x1):
            plec = 0.7 if (x - x0) in (96, 97, 194, 195) or (y - y0) == 127 else 0
            cv.put(x, y, PAPER, 4.0 - plec + (fbm(x / 18, y / 18, 6) - 0.5) * 1.0, lit=0.6)
    for x in range(x0 + 8, x1 - 8):                        # el marc
        cv.put(x, y0 + 8, SEPIA, 2.6, lit=0)
        cv.put(x, y1 - 9, SEPIA, 2.6, lit=0)
    for y in range(y0 + 8, y1 - 8):
        cv.put(x0 + 8, y, SEPIA, 2.6, lit=0)
        cv.put(x1 - 9, y, SEPIA, 2.6, lit=0)
    # el rierol, que baixa del turó (a dalt a la dreta) fins al toll (a baix a l'esquerra)
    pts = []
    for i in range(160):
        t = i / 159
        pts.append((x1 - 30 - t * 200 + math.sin(t * 9) * 12, y0 + 30 + t * 170))
    for k, (x, y) in enumerate(pts):
        cv.put(x, y, SEPIA, 2.8, lit=0)
        cv.put(x + 3, y + 1, SEPIA, 2.2, lit=0)
    cv.ring(pts[-1][0] - 8, pts[-1][1] + 10, 16, SEPIA, 2.6, lit=0, step=3)
    # el roure (un cercle de capçada) i les seves arrels, que s'escampen pel paper
    rx, ry = x0 + 90, y0 + 70
    cv.ring(rx, ry, 18, SEPIA, 2.8, lit=0, step=2)
    cv.ring(rx, ry, 4, SEPIA, 3.0, lit=0, step=10)
    for k in range(9):
        a = k / 9 * math.tau + 0.3
        for i in range(70):
            r = 20 + i
            x = rx + math.cos(a + math.sin(i / 9 + k) * 0.25) * r
            y = ry + math.sin(a + math.sin(i / 9 + k) * 0.25) * r * 0.8
            if x0 + 10 < x < x1 - 10 and y0 + 10 < y < y1 - 10 and hr(i, k) < 0.8:
                cv.put(x, y, SEPIA, 2.2, lit=0)
    # les corbes de nivell del turó
    for n in range(3):
        cv.ring(x1 - 44, y0 + 44, 12 + n * 9, SEPIA, 1.8, lit=0, step=4)
    lletres(cv, 'BOSC DE LA COMA', x0 + 18, y1 - 34, None, ramp=SEPIA, lvl=3.0)
    lletres(cv, '1923', x1 - 18 - ample('1923', 2), y1 - 38, None, k=2, ramp=SEPIA, lvl=3.0)


def carpeta(cv):
    """La carpeta de l'expedient: cartolina de color manila, la pestanya, l'etiqueta i els tres segells."""
    x0, y0, x1, y1 = CARPETA
    ombra_rect(cv, x0, y0 - 14, x1, y1)
    cv.rect(x0 + 16, y0 - 14, x0 + 96, y0, MANILA, 3.2, lit=0.6)          # la pestanya
    for y in range(y0, y1):
        for x in range(x0, x1):
            cv.put(x, y, MANILA, 3.6 + (fbm(x / 12, y / 30, 11) - 0.5) * 0.8 - (0.8 if x in (x0, x1 - 1) else 0),
                   lit=0.6)
    # l'etiqueta, amb el títol
    ex0, ey0, ex1, ey1 = x0 + 24, y0 + 24, x1 - 24, y0 + 96
    cv.rect(ex0, ey0, ex1, ey1, PAPER, 4.6, lit=0.4)
    for x in range(ex0, ex1 + 1):
        cv.put(x, ey0, SEPIA, 1.4, lit=0)
        cv.put(x, ey1, SEPIA, 1.4, lit=0)
    cx = (ex0 + ex1) // 2
    for s, y, k in (('EXPEDIENT', ey0 + 10, 2), ('NATURAPLUS', ey0 + 36, 2), ('ARXIVAT', ey0 + 60, 1)):
        lletres(cv, s, cx - ample(s, k) // 2, y, None, k=k, ramp=IRONK, lvl=1.2)
    # les ratlles de mecanografia sota l'etiqueta
    for j in range(3):
        y = ey1 + 12 + j * 9
        for x in range(ex0, ex1 - (j * 23) % 50):
            if hr(x // 4, j) < 0.82:
                cv.put(x, y, IRONK, 2.0, lit=0)
    for i, (sx, sy) in enumerate(SEGELLS):
        segell(cv, sx, sy, 27, mullat=(i == 2), gir=(-0.25, 0.1, 0.3)[i])


def segell(cv, cx, cy, r, mullat=False, gir=0.0):
    """Un segell de goma de gripau: dues anelles, la corona de puntets i el cap del gripau (els dos ulls grossos i
    la boca ampla) al mig. Estampat (amb buits, com la tinta de debò); `mullat`: més viu, encara lluent."""
    lvl = 3.6 if mullat else 2.8

    def tinta(x, y, l=lvl):
        if hr(int(x), int(y), 77) < (0.94 if mullat else 0.82):
            cv.put(x, y, TINTA, l, lit=0)

    for a in range(0, 360, 1):
        ra = math.radians(a)
        for rr in (r, r - 1, r - 6):
            tinta(cx + math.cos(ra) * rr, cy + math.sin(ra) * rr)
    for k in range(18):                                        # la corona de puntets
        a = k / 18 * math.tau + gir
        tinta(cx + math.cos(a) * (r - 3.5), cy + math.sin(a) * (r - 3.5))
    # el cap del gripau
    for y in range(int(cy - 8), int(cy + 12)):
        for x in range(int(cx - 15), int(cx + 16)):
            nx, ny = (x - cx) / 15, (y - cy - 2) / 10
            if nx * nx + ny * ny <= 1:
                tinta(x, y)
    for ex in (-8, 8):                                         # els ulls, que sobresurten
        for y in range(int(cy - 14), int(cy - 3)):
            for x in range(int(cx + ex - 5), int(cx + ex + 6)):
                d = math.hypot(x - cx - ex, y - cy + 8)
                if d <= 5.5:
                    if d > 2.2:
                        tinta(x, y)
    for x in range(int(cx - 10), int(cx + 11)):                # la boca, en blanc (sense tinta)
        y = cy + 5 + (x - cx) ** 2 / 40
        cv.put(x, y, MANILA, 3.4, lit=0.6)
    if mullat:
        cv.glow(cx - r * 0.4, cy - r * 0.4, r * 0.5, (255, 190, 170), 0.25)


def segell_goma(cv):
    """El segell de goma del Registrador (mànec de fusta, base de goma) i el tamponet de tinta vermella."""
    tx, ty = 560, 318
    cv.darken(tx - 34, ty - 14, tx + 40, ty + 26, 0.5)
    cv.rect(tx - 36, ty - 20, tx + 34, ty + 18, IRONK, 2.4, lit=0.6)                 # la capsa del tampó
    cv.rect(tx - 32, ty - 16, tx + 30, ty + 14, TINTA, 2.6, lit=0.3)                 # el feltre, amarat
    bx, by = 470, 320
    cv.disc(bx + 6, by + 8, 26, 12, IRONK, 0.6, lit=0)                               # l'ombra
    cv.disc(bx, by, 22, 10, IRONK, lambda nx, ny: 2.6 - ny, lit=0.6)                 # la base
    cv.rect(bx - 7, by - 30, bx + 7, by - 4, PLANK, lambda x, y: 4.4 - (x - bx) * 0.25, lit=0.8)   # el mànec
    cv.disc(bx, by - 34, 12, 9, PLANK, lambda nx, ny: 5.2 - ny * 1.4 - nx, lit=0.8)  # el pom
    cv.disc(bx - 4, by - 38, 4, 2.4, PLANK, 6.4, lit=0)                              # la lluïssor


def bg(cv):
    taulell(cv)
    planol(cv)
    carpeta(cv)
    segell_goma(cv)
    cv.P = cv.img.load()


PROPS = {}
ANIMS = {}
GEOMETRIA = {'things': {}, 'spawns': {}}
