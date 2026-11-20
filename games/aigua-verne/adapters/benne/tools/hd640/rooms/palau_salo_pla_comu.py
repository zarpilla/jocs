"""
El dibuix pla del saló de la subhasta (palau_salo), d'on surten les textures de la sala en 3D: la paret del fons amb
els dos finestrals a l'espai, la pantalla gegant i les cortines de vellut (i els gràfics del preu, els decorats
`grafic_*`), les cadires daurades amb els inversors asseguts vistos d'esquena, les copes de cava, la glaçonera i la
safata d'argent. Tot de cara, com sempre, a 1× (en píxels de sala del dibuix pla de 640×360 d'abans), i palau_salo.py
ho projecta.
"""
import math

import hd640  # noqa: F401  (abans de cap hd.rooms: posa la llibreria a 640×360)
from hd.pix import Canvas, Light, hr, mix
from hd.rooms.comu import text_width
from hd640.rooms.palau_comu import (MARB, ORP, CROM, NEGRE, GRANAT, PLATA, lletres, lletres_c, lletres_grans,
                                    triangle, terra2, diposit, gota, motllura, marc_or, vidre)
from hd640.rooms.palau_galeria_pla_comu import espai, soroll

WALL_TOP = 12
FLOOR_BACK = 150             # on el terra tocava la paret del fons (al dibuix pla)
SCR = (212, 24, 428, 116)    # la pantalla (el vidre)
STAGE_Y = 134                # on les cortines arriben a l'escenari
WINS = ((84, 30, 152, 118), (488, 30, 556, 118))

LLUM_PLA = Light(ambient=0.15, vignette=None, floor_fade=None)
LLUM_PLA.point(320, 90, r=200, k=0.7, squash=1.2, power=1.6)       # la pantalla

SCREEN_BG = [(4, 8, 20), (8, 14, 34), (12, 22, 50), (18, 32, 70), (28, 46, 94)]


def paret_fons(cv):
    n = soroll(640, 200, 40, 2)
    cv.rect(60, WALL_TOP + 1, 580, FLOOR_BACK, MARB, lambda x, y: 4.8 + (n[y, x] - 0.5) * 0.6)
    # plafons de marbre amb filet d'or (entre finestrals i pantalla)
    for x0, x1 in ((66, 78), (160, 176), (464, 480), (562, 574)):
        marc_or(cv, x0, 26, x1, 136, t=1, lvl=3.6)
    motllura(cv, 60, 580, FLOOR_BACK - 8, MARB, 5.6, h=2)
    cv.rect(60, FLOOR_BACK - 6, 580, FLOOR_BACK, MARB, lambda x, y: 3.6 - (y - FLOOR_BACK + 6) * 0.1)
    motllura(cv, 60, 580, FLOOR_BACK - 6, ORP, 4.0, h=1)


def finestrals(cv):
    bright = []
    for i, (x0, y0, x1, y1) in enumerate(WINS):
        bright += espai(cv, x0, y0, x1, y1, seed=21 + i)
        if i == 0:
            terra2(cv, x0 + 6, y1 + 30, 58, mask=lambda x, y: x0 <= x <= x1 and y0 <= y <= y1, seed=3)
        else:
            dep = type(cv)(transparent=True)
            diposit(dep, 524, 62, 0.34)
            D = dep.img.load()
            for X, Y, _, _ in cv.pixels(x0, y0, x1, y1):                                  # (píxels reals)
                if D[X, Y][3]:
                    cv.P[X, Y] = D[X, Y][:3] + (255,)
        vidre(cv, x0, y0, x1, y1, k=0.12, seed=x0)
        cv.hline(x0, x1, y0 + 30, ORP, 3.4)
        cv.vline((x0 + x1) // 2, y0, y1, ORP, 3.4)
        marc_or(cv, x0 - 3, y0 - 3, x1 + 3, y1 + 3, t=3, lvl=4.4)
        cv.rect(x0 - 5, y1 + 4, x1 + 5, y1 + 6, MARB, lambda x, y: 6.6 - (y - y1 - 4))
    return bright


# ─── Pantalla, cortines i escenari ──────────────────────────────────────────

def pantalla(cv):
    x0, y0, x1, y1 = SCR
    # el bastidor: negre, amb un filet d'or
    cv.rect(x0 - 6, y0 - 6, x1 + 6, y1 + 6, NEGRE, lambda x, y: 1.6 - (y - y0) * 0.004, lit=0)
    marc_or(cv, x0 - 8, y0 - 8, x1 + 8, y1 + 8, t=2, lvl=4.6)
    cv.rect(x0, y0, x1, y1, SCREEN_BG, lambda x, y: 1.4 + (y - y0) / (y1 - y0) * 1.4, lit=0)
    # base: el títol de la subhasta i la gota gran
    # (els rètols, a ×2: a 1×, en escorç i a l'altra punta del saló, la lletra petita no es llegeix)
    gota(cv, (x0 + x1) // 2, y0 + 19, 24)
    _grans_c(cv, 'GRAN SUBHASTA DE L\'AIGUA', (x0 + x1) // 2, y0 + 38, (220, 230, 246))
    _grans_c(cv, 'VERNE S.A.', (x0 + x1) // 2, y0 + 54, (120, 160, 220))
    _grans_c(cv, 'DEU ANYS D\'AIGUA DE VESPER', (x0 + x1) // 2, y0 + 72, (110, 132, 176))
    _scan(cv)


def _grans_c(cv, s, cx, y, col):
    """Text a ×2, centrat a cx."""
    return lletres_grans(cv, s, cx - text_width(s), y, col)


def _scan(cv):
    """Línies d'escombrat suaus (una pantalla gegant de debò) i una lluentor a la cantonada."""
    x0, y0, x1, y1 = SCR
    for y in range(y0, y1 + 1, 3):
        for x in range(x0, x1 + 1):
            o = cv.get(x, y)
            if o[3]:
                cv.flat(x, y, tuple(int(c * 0.86) for c in o[:3]))
    for y in range(y0, y0 + 26):
        for x in range(x1 - 40 + (y - y0), x1 - 30 + (y - y0)):
            if x <= x1:
                o = cv.get(x, y)
                if o[3]:
                    cv.flat(x, y, mix(o, (200, 220, 255), 0.08))


def cortines(cv):
    """Dues cortines de vellut granat, recollides amb cordons d'or, i la galeria de dalt."""
    for side in (0, 1):
        xa, xb = (176, 210) if side == 0 else (430, 464)
        for y in range(WALL_TOP + 1, STAGE_Y + 1):
            # es recull a l'alçada del cordó
            pinch = max(0.0, 1 - abs(y - 92) / 40) * 10
            a = xa + (pinch if side == 0 else 0)
            b = xb - (pinch if side == 1 else 0)
            for x in range(int(a), int(b) + 1):
                u = (x - a) / max(1, b - a)
                fold = math.sin(u * math.pi * 5 + (0.4 if side else 0))
                v = 3.2 + fold * 1.4 + (0.6 if y > 92 else 0) - (1.0 if side == 1 and u > 0.8 else 0)
                cv.put(x, y, GRANAT, v)
        cx = xa + 10 if side == 0 else xb - 10
        cv.disc(cx, 92, 4, 3, ORP, lambda nx, ny: 5 - ny * 1.5)              # el cordó
        for k in range(10):
            cv.put(cx + (k % 2), 95 + k, ORP, 4.6 - k * 0.2)
        cv.rect(cx - 2, 104, cx + 2, 110, ORP, lambda x, y: 4.4 - (y - 104) * 0.2)
    # la galeria (bambolina) per sobre de la pantalla
    for y in range(WALL_TOP + 1, WALL_TOP + 9):
        for x in range(170, 471):
            scallop = (y - WALL_TOP) > 5 + 2 * math.cos((x - 170) / 37 * 2 * math.pi)
            if not scallop:
                cv.put(x, y, GRANAT, 3.6 + math.sin((x - 170) / 37 * 2 * math.pi) * 0.8)
    motllura(cv, 170, 470, WALL_TOP + 1, ORP, 4.6, h=2)


# ─── Cadires i inversors ────────────────────────────────────────────────────

INV = [(30, 30, 40), (40, 40, 52), (56, 54, 66), (80, 76, 86)]
# la roba i el cabell dels inversors: foscos, però no tots iguals
ROBA = ([(14, 16, 28), (22, 26, 44), (34, 40, 64), (56, 64, 94)],          # blau marí
        [(20, 20, 22), (32, 32, 36), (48, 48, 54), (72, 72, 80)],          # gris marengo
        [(30, 10, 16), (50, 16, 26), (76, 26, 38), (110, 44, 54)],         # granat
        [(18, 26, 22), (28, 40, 34), (42, 58, 48), (64, 82, 68)])          # verd ampolla
CABELL = ([(14, 12, 12), (26, 22, 20), (40, 34, 30), (60, 52, 44)],
          [(70, 70, 74), (110, 110, 112), (150, 150, 150), (196, 196, 192)],
          [(40, 24, 14), (70, 44, 24), (100, 66, 36), (136, 96, 56)],
          [(150, 140, 120), (196, 186, 160), (226, 218, 196), (246, 240, 224)])


def cadira(cv, x, yfloor, s=1.0, ocupada=True, seed=0):
    """Una cadira daurada vista de darrere i, si està ocupada, un inversor assegut (silueta)."""
    h = int(40 * s)
    w = int(14 * s)
    top = yfloor - h
    # potes
    for lx in (x - w // 2, x + w // 2):
        cv.vline(lx, yfloor - int(16 * s), yfloor, ORP, 3.4)
    if ocupada:
        # l'inversor: espatlles, coll i cap (de vegades, un barret o un monyo)
        sh = yfloor - int(48 * s)
        kind = int(hr(seed, 3) * 7)
        roba = ROBA[int(hr(seed, 5) * 4)]
        cab = CABELL[int(hr(seed, 6) * 4)]
        cv.disc(x, sh + int(10 * s), 9.5 * s, int(10 * s), roba,
                lambda nx, ny: 1.2 - nx * 0.5 + (1.0 if ny < -0.75 else 0), lit=0.4)
        hx = x + int((hr(seed, 4) - 0.5) * 3)
        hy = sh - int(6 * s)
        cv.rect(hx - 2, hy + int(3 * s), hx + 2, sh + 2, [(40, 26, 24), (70, 46, 40), (110, 76, 62)], 0.8, lit=0)
        cv.disc(hx, hy, 5.0 * s, 6.0 * s, cab, lambda nx, ny: 1.4 - nx * 0.5 + (1.0 if ny < -0.6 else 0), lit=0.4)
        if kind == 0:                                                # barret de copa
            cv.rect(hx - int(5 * s), hy - int(15 * s), hx + int(5 * s), hy - int(5 * s), INV, 0.8, lit=0)
            cv.hline(hx - int(7 * s), hx + int(7 * s), hy - int(5 * s), INV, 1.6, lit=0)
            cv.hline(hx - int(5 * s), hx + int(5 * s), hy - int(7 * s), GRANAT, 3.0, lit=0)
        elif kind == 1:                                              # monyo
            cv.disc(hx, hy - int(6 * s), 3.2 * s, 3.0 * s, cab, 1.8, lit=0)
        elif kind == 2:                                              # collar de perles
            cv.hline(hx - 3, hx + 3, sh + 1, PLATA, 3.4, lit=0)
        elif kind == 3:                                              # calb, amb la llum al crani
            cv.disc(hx, hy, 4.8 * s, 5.8 * s, [(60, 40, 34), (100, 68, 56), (150, 110, 90), (196, 156, 130)],
                    lambda nx, ny: 1.2 - nx * 0.6 + (1.4 if ny < -0.5 and nx < 0.2 else 0), lit=0.3)
        # la llum de la pantalla, a la vora de dalt del cap
        cv.hline(hx - 1, hx + 1, hy - int(6 * s), cab, 3.0, lit=0)
    # el respatller: marc d'or amb barrots, i el seient
    cv.rect(x - w // 2, top, x + w // 2, top + 1, ORP, 5.0)
    cv.disc(x, top, w // 2, 2, ORP, lambda nx, ny: 5.4 - ny * 1.4)
    for k in range(-w // 2, w // 2 + 1, max(2, int(3 * s))):
        cv.vline(x + k, top + 1, top + int(18 * s), ORP, 4.0 if k < 0 else 3.2)
    cv.vline(x - w // 2, top, top + int(20 * s), ORP, 5.0)
    cv.vline(x + w // 2, top, top + int(20 * s), ORP, 3.0)
    cv.rect(x - w // 2 - 1, top + int(18 * s), x + w // 2 + 1, top + int(21 * s), GRANAT, lambda xx, yy: 4.0 - (yy - top) * 0.05)


# ─── La taula del cava ──────────────────────────────────────────────────────

def copa(cv, x, y, s=1.0, plena=True):
    """Una copa de cava (flauta): peu, tija i calze amb el cava daurat."""
    cv.hline(x - 2, x + 2, y, CROM, 5.0)
    cv.vline(x, y - 4, y - 1, CROM, 6.0)
    for k in range(7):
        cv.put(x - 1, y - 5 - k, CROM, 6.4)
        cv.put(x + 1, y - 5 - k, CROM, 4.6)
        cv.put(x, y - 5 - k, ORP if plena and k < 5 else CROM, 5.8 if plena else 6.6)
    if plena:
        cv.flat(x, y - 9, (255, 250, 220))


def safata(cv, cx, cy):
    """La safata d'argent, a la punta de la taula, amb tres copes plenes (aquí hi deixarà les claus l'Iri)."""
    cv.disc(cx, cy, 14, 3.4, CROM, lambda nx, ny: 6.4 - ny * 1.6 - nx * 0.6)
    cv.disc(cx, cy - 0.5, 11.5, 2.2, CROM, lambda nx, ny: 4.6 + ny * 0.8)
    for dx in (-6, 0, 6):
        copa(cv, cx + dx, cy - 1 + (1 if dx == 0 else 0))


# ─── Gràfics de la pantalla ─────────────────────────────────────────────────

SERIE = [40, 41, 43, 44, 46, 48, 52, 60, 66, 75, 88, 100, 112]
# El preu a cada pas de la subhasta (guio: «La subhasta»): cada dipòsit fa baixar el preu segons el gel que té (T2 10,
# Ferrum 16, Aqua 55), i la palanca de la RESERVA el deixa a 29. La línia fa el camí de l'ordre en què s'han obert les
# vàlvules: hi ha un fotograma per a cada ordre (vegeu ORDRES).
CAU = {'t2': 10, 'ferrum': 16, 'aqua': 55}
RESERVA = 29


def _ordres():
    """Tots els ordres possibles de vàlvules obertes: (), ('t2',), ('t2', 'ferrum'), ... (1 + 3 + 6 + 6)."""
    from itertools import permutations
    return [()] + [o for k in (1, 2, 3) for o in permutations(CAU, k)]


ORDRES = _ordres()


def cami(ordre, reserva=False):
    """Els preus després de cada vàlvula de l'`ordre` (i de la reserva)."""
    out, p = [], SERIE[-1]
    for v in ordre:
        p -= CAU[v]
        out.append(p)
    return out + ([RESERVA] if reserva else [])


def nom_grafic(ordre, reserva=False):
    """L'id del decorat: `grafic_112` (cap vàlvula), `grafic_aqua_t2`, `grafic_t2_ferrum_aqua_reserva`..."""
    return 'grafic_' + ('_'.join(ordre) + ('_reserva' if reserva else '') if ordre else str(SERIE[-1]))


def grafic(cv, ordre=(), reserva=False):
    """La pantalla amb el gràfic del preu: eixos, la línia (el camí de les vàlvules de l'`ordre`, i la reserva), la
    ratlla del LLINDAR a 30 i el número (l'últim preu)."""
    caiguda = cami(ordre, reserva)
    n = (caiguda or SERIE)[-1]
    x0, y0, x1, y1 = SCR
    cv.rect(x0, y0, x1, y1, SCREEN_BG, lambda x, y: 1.2 + (y - y0) / (y1 - y0) * 1.0, lit=0)
    gx0, gx1, gy0, gy1 = x0 + 16, x1 - 74, y0 + 10, y1 - 22

    def Y(v):
        return gy1 - (v / 120) * (gy1 - gy0)
    # la graella i els eixos
    for v in (0, 30, 60, 90, 120):
        for x in range(gx0, gx1 + 1, 3):
            cv.flat(x, int(Y(v)), (24, 40, 70))
        lletres(cv, str(v), x0 + 3, int(Y(v)) - 2, (90, 110, 150))
    cv.vline(gx0, gy0, gy1, SCREEN_BG, 4.0, lit=0)
    cv.hline(gx0, gx1, gy1, SCREEN_BG, 4.0, lit=0)
    # la ratlla del LLINDAR DEL BANC, a 30
    yl = int(Y(30))
    for x in range(gx0, x1 - 3):
        if (x // 4) % 2 == 0:
            cv.flat(x, yl, (230, 50, 40))
            cv.flat(x, yl + 1, (150, 26, 24))
    lletres_grans(cv, 'LLINDAR DEL BANC', x0 + 4, y1 - 16, (236, 80, 64))      # (els rètols, a ×2: vegeu pantalla)
    # la línia del preu
    vals = SERIE + caiguda
    m = len(SERIE) + 4
    pts = [(gx0 + 2 + i * (gx1 - gx0 - 4) / (m - 1), Y(v)) for i, v in enumerate(vals)]
    baixa = n != 112
    col = (250, 150, 50)
    for (xa, ya), (xb, yb) in zip(pts, pts[1:]):
        drop = yb > ya
        c = (240, 70, 56) if drop else col
        steps = int(max(abs(xb - xa), abs(yb - ya))) + 1
        for k in range(steps + 1):
            t = k / steps
            x, y = round(xa + (xb - xa) * t), round(ya + (yb - ya) * t)
            cv.flat(x, y, c)
            cv.flat(x, y + 1, tuple(v // 2 for v in c))
    lx, ly = pts[-1]
    cv.disc(lx, ly, 2, 2, [(255, 255, 255)], 0, lit=0)
    # el número gran, amb ▲ o ▼
    s = str(n)
    numc = (250, 150, 50) if not baixa else (240, 70, 56) if n < 30 else (255, 200, 120)
    tw = lletres_grans(cv, s, x1 - 62, y0 + 18, numc, k=3)
    lletres(cv, 'C', x1 - 62 + tw + 2, y0 + 30, numc)
    triangle(cv, x1 - 40, y0 + 44, 7, numc if not baixa else (240, 70, 56), amunt=not baixa)
    lletres_grans(cv, 'PER LITRE', x1 - 70, y0 + 54, (140, 160, 200))
    if n == 29:
        lletres_grans(cv, 'EXECUCIÓ', x1 - 70, y0 + 67, (240, 70, 56))
        lletres_grans(cv, 'DEL BANC', x1 - 70, y0 + 79, (240, 70, 56))
    elif n == 31:
        lletres_grans(cv, 'PER POC', x1 - 70, y0 + 68, (200, 180, 120))
    _scan(cv)


# ─── Peces dretes (sprites), retallades ─────────────────────────────────────

def cadira_img(seed, ocupada=True):
    """Una cadira daurada vista d'esquena, amb (o sense) un inversor assegut. → (imatge, peu)."""
    cv = Canvas(40, 80, light=None, transparent=True)
    cadira(cv, 20, 76, 1.0, ocupada, seed)
    return cv.img, (20, 76)


def copes_img():
    """La piràmide de copes de cava i la glaçonera d'argent amb dues ampolles. → (imatge, peu)."""
    cv = Canvas(70, 70, light=None, transparent=True)
    yt = 66
    for row, n in enumerate((5, 4, 3, 2, 1)):
        for i in range(n):
            copa(cv, 24 + i * 6 - n * 3 + 3, yt - 1 - row * 11)
    bx = 56
    for dx, h in ((-3, 26), (4, 24)):
        cv.rect(bx + dx - 2, yt - h, bx + dx + 2, yt - 8, [(10, 30, 16), (20, 50, 28), (34, 80, 44), (60, 120, 70)],
                lambda x, y: 2.0 - (x - bx - dx) * 0.4)
        cv.rect(bx + dx - 1, yt - 4 - h, bx + dx + 1, yt - h, ORP, 5.0)
    cv.poly([(bx - 9, yt - 14), (bx + 9, yt - 14), (bx + 7, yt - 1), (bx - 7, yt - 1)], CROM,
            lambda x, y: 6.0 - (x - bx + 9) * 0.22)
    cv.hline(bx - 10, bx + 10, yt - 15, CROM, 7.0)
    return cv.img, (35, yt)


def safata_img():
    cv = Canvas(34, 20, light=None, transparent=True)
    safata(cv, 17, 15)
    return cv.img, (17, 16)


def martell_img():
    """El martell de la subhasta: el mànec de fusta fosca i el cap d'or, damunt la base rodona. → (imatge, peu)."""
    cv = Canvas(24, 16, light=None, transparent=True)
    yf = 14
    cv.disc(10, yf - 1, 6, 2, ORP, 3.2)
    cv.line(3, yf - 4, 17, yf - 8, [(30, 16, 10), (60, 34, 20), (96, 56, 32), (140, 90, 50)], 2.4)
    cv.rect(14, yf - 12, 20, yf - 5, ORP, lambda x, y: 5.0 - (x - 14) * 0.3)
    cv.hline(14, 20, yf - 12, ORP, 6.4)
    return cv.img, (10, yf)


def paret_fons_pla():
    """La paret del fons sencera (en un llenç de 640×360, com abans): marbre, finestrals, pantalla i cortines.
    → (imatge, estrelles brillants)."""
    cv = Canvas(light=LLUM_PLA)
    paret_fons(cv)
    bright = finestrals(cv)
    pantalla(cv)
    cortines(cv)
    return cv.img, bright
