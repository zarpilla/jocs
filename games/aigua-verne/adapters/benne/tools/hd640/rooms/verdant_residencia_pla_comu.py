"""
El despatx d'estiu del Magnat PLA, vist de cara (com era abans de passar-lo a 3D): ara és la font de les textures
de verdant_residencia.py, que en projecta la paret (la porta, el quadre, els apliques, el finestral), el davant de
l'arxivador i de la calaixera, el trofeu, el gerro i el telèfon. (`bg` encara dibuixa el despatx pla sencer.)

El despatx d'estiu del Magnat, a la residència de Verdant: tot blanc i or, net com una sala d'exposició on no viu
ningú. Parets blanques amb motllures daurades, el terra de marbre blanc amb vetes d'or i una catifa amb la gota.
A l'esquerra, la **porta** (blanca, plafons d'or) que torna al jardí; l'**arxivador** blanc amb tres calaixos
etiquetats «DEUTORS», «DRETS» i «PEIXOS» (i, a dalt, un trofeu: una gota d'or); el **quadre** enorme del Magnat
(vestit blanc, cabell blanc enrere, somriure de dents perfectes) amb en Dividend (petit, blanc, pentinat, amb
banyador de ratlles) damunt un coixí de vellut; a sota, la **calaixera** de laca blanca amb potes d'or, un gerro de
flors de plàstic i un telèfon daurat; la **paperera daurada**; i el **finestral** al jardí, amb cortines blanques.
"""
import hd640  # noqa: F401  (abans que cap hd.rooms: posa la llibreria a 640×360)

import math

from hd.pix import Canvas, Light, W, H, hr, mix
from hd.rooms.arenga import box
from hd.rooms.comu import text, text_width
from hd.rooms.exterior import fbm
from hd640.rooms.verdant_comu import (SKYV, CLOUDV, TURF, WHITEV, MARBLE, GOLDV, MAGENTA, SHEDG, BLUEG, FLOWERS,
                                      gota, flor, arbre_rodo, ombra)

# A 1× (hd.pix.Canvas): és la font de les textures de verdant_residencia.py (la sala en 3D), que és a 1×.

RH = 260
FLOOR_Y = 216
CEIL_Y = 16
DOOR = (24, 92, 90, FLOOR_Y)
ARX = (108, 100, 164, FLOOR_Y)
PAINT = (184, 20, 358, 138)            # el marc del quadre (per fora)
CALAIX = (206, 170, 336, FLOOR_Y)
PAPER = (362, 218)                     # la paperera: centre de la base
WIN = (430, 30, 606, FLOOR_Y - 2)      # el vidre del finestral

# rampes del quadre
VELVET = [(20, 10, 30), (36, 18, 52), (54, 28, 78), (76, 40, 104), (100, 56, 130), (130, 80, 156)]
REDV = [(40, 6, 14), (74, 12, 24), (112, 20, 34), (150, 34, 44), (186, 56, 60), (220, 96, 90)]
SKINV = [(90, 54, 44), (140, 92, 74), (186, 132, 108), (222, 172, 146), (242, 206, 184), (252, 232, 218)]
SUITV = [(110, 112, 130), (156, 158, 174), (196, 198, 210), (226, 228, 236), (244, 245, 250), (255, 255, 255)]
STRIPE = [(10, 30, 80), (20, 60, 150), (40, 100, 210), (100, 160, 240)]

LIGHT = Light(ambient=0.9, vignette=(80, 30), floor_fade=None)
LIGHT.point(520, 110, r=420, k=1.5, squash=0.9, power=1.3)        # el sol que entra pel finestral
LIGHT.point(176, 70, r=90, k=0.7, power=1.6)                      # els apliques
LIGHT.point(372, 70, r=90, k=0.7, power=1.6)


# ─── Paret, sostre, terra ──────────────────────────────────────────────────

def paret(cv):
    """Blanc pur amb plafons de motllura daurada, un sòcol alt i una cornisa d'or."""
    cv.rect(0, 0, W - 1, FLOOR_Y - 1, WHITEV, lambda x, y: 3.7 + (fbm(x / 60, y / 40, 201) - 0.5) * 0.3)
    # el sostre i la cornisa
    cv.rect(0, 0, W - 1, CEIL_Y - 6, WHITEV, lambda x, y: 5.0 - y * 0.05)
    cv.rect(0, CEIL_Y - 5, W - 1, CEIL_Y, GOLDV, lambda x, y: 4.8 - (y - CEIL_Y + 5) * 0.5 +
            (0.8 if (x // 3) % 2 and y == CEIL_Y - 2 else 0))
    cv.hline(0, W - 1, CEIL_Y + 1, WHITEV, 2.6)
    # el sòcol i el passamà daurat
    cv.rect(0, FLOOR_Y - 14, W - 1, FLOOR_Y - 1, WHITEV, lambda x, y: 4.8 - (y - FLOOR_Y + 14) * 0.04)
    cv.hline(0, W - 1, FLOOR_Y - 15, GOLDV, 4.8)
    cv.hline(0, W - 1, FLOOR_Y - 14, GOLDV, 3.2)
    cv.hline(0, W - 1, 150, GOLDV, 4.4)
    cv.hline(0, W - 1, 151, WHITEV, 2.8)
    # els plafons, a sobre i a sota del passamà
    for x0, x1 in ((98, 174), (172, 372), (370, 420), (612, 640)):
        for y0, y1 in ((CEIL_Y + 8, 142), (158, FLOOR_Y - 22)):
            for x in range(x0 + 4, x1 - 3):
                cv.put(x, y0, GOLDV, 4.0)
                cv.put(x, y1, WHITEV, 2.8)
            for y in range(y0, y1 + 1):
                cv.put(x0 + 4, y, GOLDV, 4.0)
                cv.put(x1 - 4, y, WHITEV, 3.0)
    # les pilastres
    for px in (96, 418):
        cv.rect(px - 5, CEIL_Y + 1, px + 5, FLOOR_Y - 1, WHITEV, lambda x, y, px=px: 5.0 - (x - px) * 0.18 -
                (0.9 if (x - px) % 4 == 0 else 0))
        cv.rect(px - 7, CEIL_Y + 1, px + 7, CEIL_Y + 6, GOLDV, lambda x, y: 4.8 - (y - CEIL_Y) * 0.3)
        cv.rect(px - 7, FLOOR_Y - 6, px + 7, FLOOR_Y - 1, GOLDV, 3.8)


def terra(cv):
    """Marbre blanc amb vetes d'or, polit fins a fer mirall."""
    for y in range(FLOOR_Y, RH):
        t = (y - FLOOR_Y) / (RH - FLOOR_Y)
        for x in range(W):
            v = fbm(x / 70 + y / 30, y / 9, 211, octaves=2)
            lvl = 4.3 - t * 0.5 + (fbm(x / 40, y / 10, 213) - 0.5) * 0.5
            # les lloses, en perspectiva
            vx = (x - 320) / (1 + t * 0.8)
            if abs(vx % 64) < 0.8 or (y - FLOOR_Y) in (9, 23):
                lvl -= 1.4
            if abs(v - 0.5) < 0.006:
                cv.put(x, y, GOLDV, 4.0)
                continue
            if abs(v - 0.6) < 0.006:
                lvl -= 0.9
            cv.put(x, y, MARBLE, lvl)
    # el reflex del finestral al terra
    cv.tint(WIN[0] - 60, FLOOR_Y + 1, WIN[2], RH - 1, (255, 255, 255),
            lambda x, y: 0.35 if WIN[0] - (y - FLOOR_Y) * 1.6 <= x <= WIN[2] - (y - FLOOR_Y) * 1.6 and
            (x + y) % 2 == 0 else 0)
    cv.darken(0, FLOOR_Y, W - 1, FLOOR_Y + 2, lambda x, y: 0.4 - (y - FLOOR_Y) * 0.15)


def catifa(cv):
    """Catifa blanca de pèl, amb la sanefa d'or i la gota de Verne al mig."""
    cx, cy, rx, ry = 300, 241, 104, 12
    cv.disc(cx, cy + 1, rx + 1, ry + 1, MARBLE, 2.0)
    cv.disc(cx, cy, rx, ry, WHITEV, lambda nx, ny: 5.0 - ny * 0.6 + (hr(int(nx * 80), int(ny * 30)) - 0.5) * 0.8)
    for a in range(0, 360, 1):
        ra = math.radians(a)
        cv.put(cx + math.cos(ra) * (rx - 6), cy + math.sin(ra) * (ry - 2), GOLDV, 4.4)
        cv.put(cx + math.cos(ra) * (rx - 8), cy + math.sin(ra) * (ry - 3), GOLDV, 3.4)
    # la gota, aplanada per la perspectiva
    cv.disc(cx, cy + 1, 7, 3.4, BLUEG, lambda nx, ny: 2.6 - nx * 0.6 - ny * 0.4)
    cv.poly([(cx - 4, cy - 1), (cx, cy - 6), (cx + 4, cy - 1)], BLUEG, 2.6)
    cv.flat(cx - 3, cy, BLUEG[4])


# ─── La porta ──────────────────────────────────────────────────────────────

def porta(cv):
    x0, y0, x1, y1 = DOOR
    cx = (x0 + x1) // 2
    # l'arquitrau d'or i el frontó petit
    cv.rect(x0 - 6, y0 - 6, x1 + 6, y1, GOLDV, lambda x, y: 4.6 - (x - x0) * 0.01 - (1.0 if x > cx else 0) * 0.4)
    cv.rect(x0 - 4, y0 - 4, x1 + 4, y1, WHITEV, 4.6)
    cv.poly([(x0 - 10, y0 - 8), (cx, y0 - 22), (x1 + 10, y0 - 8)], WHITEV, lambda x, y: 5.4 - (y - y0 + 22) * 0.06)
    cv.line(x0 - 10, y0 - 8, cx, y0 - 22, GOLDV, 5.0)
    cv.line(cx, y0 - 22, x1 + 10, y0 - 8, GOLDV, 4.0)
    cv.rect(x0 - 10, y0 - 8, x1 + 10, y0 - 6, GOLDV, lambda x, y: 4.8 - (y - y0 + 8) * 0.8)
    gota(cv, cx, y0 - 13, 0.6)
    # les dues fulles, amb plafons i motllures d'or
    for fx0, fx1 in ((x0, cx - 1), (cx + 1, x1)):
        box(cv, fx0, y0, fx1, y1 - 1, WHITEV, 4.8 - (0.4 if fx0 > cx else 0))
        for py0, py1 in ((y0 + 8, y0 + 56), (y0 + 66, y1 - 10)):
            px0, px1 = fx0 + 6, fx1 - 6
            cv.rect(px0, py0, px1, py1, WHITEV, 4.4)
            cv.hline(px0, px1, py0, GOLDV, 4.6)
            cv.vline(px0, py0, py1, GOLDV, 4.2)
            cv.hline(px0, px1, py1, GOLDV, 3.0)
            cv.vline(px1, py0, py1, GOLDV, 3.0)
    cv.vline(cx, y0, y1 - 1, GOLDV, 2.4)
    for hx in (cx - 5, cx + 4):                                          # les manetes
        cv.rect(hx, 152, hx + 1, 160, GOLDV, lambda x, y: 5.2 - (x - hx) * 1.0)
        cv.disc(hx + 0.5, 151, 2, 1.6, GOLDV, 5.0)


# ─── L'arxivador ───────────────────────────────────────────────────────────

def arxivador(cv):
    x0, y0, x1, y1 = ARX
    ombra(cv, x1 + 3, y1 + 2, 10, 2, 0.4)
    box(cv, x0, y0, x1, y1 - 1, WHITEV, 4.6, grad=0.5)
    cv.rect(x0 - 2, y0 - 3, x1 + 2, y0, GOLDV, lambda x, y: 5.0 - (y - y0 + 3) * 0.6)
    cv.rect(x0 + 2, y1 - 5, x1 - 2, y1 - 1, GOLDV, 3.6)
    labels = ('DEUTORS', 'DRETS', 'PEIXOS')
    dh = (y1 - 8 - (y0 + 4)) / 3
    for i, lab in enumerate(labels):
        dy0 = round(y0 + 4 + i * dh)
        dy1 = round(y0 + 4 + (i + 1) * dh) - 3
        box(cv, x0 + 4, dy0, x1 - 4, dy1, WHITEV, 4.8)
        cv.hline(x0 + 4, x1 - 4, dy1 + 1, WHITEV, 2.2)
        # el portaetiquetes d'or amb la targeta
        lw = text_width(lab) + 6
        lx = (x0 + x1) // 2 - lw // 2
        box(cv, lx - 1, dy0 + 5, lx + lw + 1, dy0 + 14, GOLDV, 4.2)
        cv.rect(lx + 1, dy0 + 7, lx + lw - 1, dy0 + 12, [(220, 214, 196), (244, 240, 228), (255, 253, 246)], 1.6, lit=0)
        text(cv, lab, lx + 3, dy0 + 8, None, 0, flat=(30, 30, 40))
        # la nansa
        cv.rect((x0 + x1) // 2 - 8, dy0 + 19, (x0 + x1) // 2 + 8, dy0 + 21, GOLDV,
                lambda x, y: 5.0 - (y - dy0 - 19) * 0.8)
        cv.vline((x0 + x1) // 2 - 8, dy0 + 17, dy0 + 19, GOLDV, 3.6)
        cv.vline((x0 + x1) // 2 + 8, dy0 + 17, dy0 + 19, GOLDV, 3.6)
    # el trofeu: una gota d'or massís en un pedestal, «AIGUA VERNE»
    tx = (x0 + x1) // 2
    cv.rect(tx - 10, y0 - 10, tx + 10, y0 - 4, [(10, 10, 14), (24, 24, 30), (40, 40, 48), (60, 60, 70)], 2.0)
    cv.hline(tx - 10, tx + 10, y0 - 10, [(40, 40, 48), (80, 80, 90)], 1.0)
    cv.rect(tx - 7, y0 - 8, tx + 7, y0 - 6, GOLDV, 3.6)
    for y in range(y0 - 36, y0 - 10):
        t = (y - y0 + 36) / 26
        w = 7.4 * math.sin(min(math.pi / 2, t * 2.4)) if t < 0.66 else 7.4 * math.sqrt(max(0.0, 1 - ((t - 0.66) / 0.36) ** 2))
        for x in range(round(tx - w), round(tx + w) + 1):
            u = (x - tx) / max(1.0, w)
            cv.put(x, y, GOLDV, 4.2 - u * 1.6 - (t - 0.6) * 1.2)
    cv.vline(tx - 3, y0 - 24, y0 - 20, GOLDV, 6.4, lit=0)
    cv.flat(tx - 2, y0 - 26, GOLDV[6])


# ─── El quadre ─────────────────────────────────────────────────────────────

def quadre(cv):
    """El retrat oficial: el Magnat, dempeus, i en Dividend damunt un coixí de vellut. Pintura a l'oli, amb el
    fons de cortinatge morat i un cel de posta d'anunci; el marc d'or recarregat i la placa."""
    X0, Y0, X1, Y1 = PAINT
    ombra(cv, (X0 + X1) / 2 + 6, Y1 + 5, (X1 - X0) / 2, 3, 0.25)
    # el marc: motllura d'or amb perles i rosasses als cantons
    for y in range(Y0, Y1 + 1):
        for x in range(X0, X1 + 1):
            d = min(x - X0, X1 - x, y - Y0, Y1 - y)
            if d < 9:
                lvl = 4.4 - abs(d - 4) * 0.4 + (0.8 if (x + y) % 4 == 0 and d in (2, 6) else 0)
                if d == 0 or d == 8:
                    lvl = 2.6
                cv.put(x, y, GOLDV, lvl - (0.6 if (x > X1 - 9 or y > Y1 - 9) else 0))
    for cx, cy in ((X0 + 4, Y0 + 4), (X1 - 4, Y0 + 4), (X0 + 4, Y1 - 4), (X1 - 4, Y1 - 4)):
        cv.disc(cx, cy, 5, 5, GOLDV, lambda nx, ny: 5.0 - nx - ny)
        cv.disc(cx, cy, 2, 2, GOLDV, 2.6)
    # la tela
    x0, y0, x1, y1 = X0 + 9, Y0 + 9, X1 - 9, Y1 - 9
    for y in range(y0, y1 + 1):
        for x in range(x0, x1 + 1):
            u = (x - x0) / (x1 - x0)
            if u < 0.62:                                                  # el cortinatge de vellut
                fold = math.sin(x * 0.32 + math.sin(y * 0.05) * 2)
                cv.put(x, y, VELVET, 2.4 + fold * 1.0 + (y - y0) * -0.006, lit=0.3)
            else:                                                         # el cel de posta, i el mar (d'Aqua!)
                t = (y - y0) / (y1 - y0)
                if t < 0.62:
                    cv.put(x, y, [(120, 80, 120), (190, 110, 120), (240, 160, 120), (255, 210, 150), (255, 236, 200)],
                           3.6 - t * 3.6 + (fbm(x / 10, y / 4, 221) - 0.5) * 0.8, lit=0.3)
                else:
                    cv.put(x, y, BLUEG, 2.6 - (t - 0.62) * 3 + (0.8 if (x + y * 3) % 9 == 0 else 0), lit=0.3)
    # la columna clàssica, a la dreta
    cv.rect(x1 - 18, y0, x1 - 8, y1, WHITEV, lambda x, y: 4.6 - (x - x1 + 18) * 0.2 - (0.8 if (x - x1) % 3 == 0 else 0),
            lit=0.3)
    figures(cv)
    # vernís: una pàtina càlida i la brillantor del vidre de museu
    cv.tint(x0, y0, x1, y1, (255, 236, 190), 0.08)
    for i in range(30):
        x, y = x0 + 20 + i, y0 + 4 + i // 2
        cv.flat(x, y, mix(cv.get(x, y), (255, 255, 255), 0.2))
    # la placa
    pw = text_width('A. VERNE I DIVIDEND') + 8
    pcx = (X0 + X1) // 2
    box(cv, pcx - pw // 2, Y1 - 6, pcx + pw // 2, Y1 + 3, GOLDV, 4.6)
    text(cv, 'A. VERNE I DIVIDEND', pcx - pw // 2 + 4, Y1 - 4, None, 0, flat=(80, 52, 20))


def figures(cv):
    """El Magnat i en Dividend, pintats en una capa a part: així se'ls pot posar el contorn fosc de la pintura."""
    fig = Canvas(light=LIGHT, transparent=True)
    mx, hx, hy = 246, 246, 50
    LT = 0.3                                                              # dins del quadre, la llum de la sala pesa poc
    # el braç esquerre (el nostre), arran del cos, amb la mà a la butxaca
    cv_ = fig
    cv_.poly([(mx - 27, 71), (mx - 19, 76), (mx - 21, 128), (mx - 34, 128), (mx - 34, 84)], SUITV,
             lambda x, y: 4.6 - (y - 71) * 0.008 + (0.6 if x < mx - 31 else 0), lit=LT)
    # el cos: espatlles, tors, i la llum de l'esquerra
    body = [(mx - 25, 72), (mx - 9, 66), (mx + 9, 66), (mx + 25, 72), (mx + 26, 129), (mx - 22, 129)]
    cv_.poly(body, SUITV, lambda x, y: 4.0 - (x - mx) * 0.045 - (0.6 if (x - mx + y // 2) % 17 == 0 and y > 100 else 0),
             lit=LT)
    cv_.line(mx - 20, 78, mx - 21, 127, SUITV, 1.8, lit=LT)                # on el braç toca el cos
    # les solapes, la camisa, la corbata d'or, el mocador
    cv_.poly([(mx - 9, 66), (mx - 1, 94), (mx - 8, 104), (mx - 15, 78)], SUITV, 4.8, lit=LT)
    cv_.poly([(mx + 9, 66), (mx + 1, 94), (mx + 8, 104), (mx + 15, 78)], SUITV, 2.8, lit=LT)
    cv_.line(mx - 9, 66, mx - 15, 78, SUITV, 2.2, lit=LT)
    cv_.line(mx - 15, 78, mx - 8, 104, SUITV, 2.2, lit=LT)
    cv_.line(mx + 15, 78, mx + 8, 104, SUITV, 1.6, lit=LT)
    cv_.poly([(mx - 6, 66), (mx + 6, 66), (mx, 92)], SUITV, 5.8, lit=LT)
    cv_.poly([(mx - 2, 70), (mx + 2, 70), (mx + 3, 88), (mx, 92), (mx - 3, 88)], GOLDV,
             lambda x, y: 4.6 - (x - mx) * 0.4, lit=LT)
    cv_.rect(mx - 2, 67, mx + 2, 70, GOLDV, lambda x, y: 5.2 - (x - mx) * 0.3, lit=LT)
    cv_.poly([(mx + 13, 85), (mx + 20, 84), (mx + 20, 88), (mx + 13, 89)], GOLDV, 4.8, lit=LT)
    cv_.poly([(mx + 14, 84), (mx + 16, 81), (mx + 18, 84)], GOLDV, 5.4, lit=LT)
    for by in (108, 120):
        cv_.disc(mx, by, 1.3, 1.3, GOLDV, 4.8, lit=LT)
    # el braç dret, cap al gos: el braç, el colze, l'avantbraç, el puny i la mà damunt el clatell
    cv_.poly([(mx + 20, 70), (mx + 27, 72), (mx + 37, 98), (mx + 29, 104), (mx + 22, 90)], SUITV,
             lambda x, y: 3.2 - (y - 70) * 0.01, lit=LT)
    cv_.poly([(mx + 30, 97), (mx + 51, 92), (mx + 52, 99), (mx + 34, 106)], SUITV,
             lambda x, y: 3.6 - (y - 92) * 0.12, lit=LT)
    cv_.rect(mx + 50, 92, mx + 52, 99, SUITV, 5.6, lit=LT)                  # el puny de la camisa
    cv_.flat(mx + 51, 95, GOLDV[5])                                        # el botó de puny
    cv_.disc(mx + 56, 95, 4, 3, SKINV, lambda nx, ny: 3.8 - nx * 0.6 - ny * 0.8, lit=LT)
    for k in range(4):                                                     # els dits i les ungles polides
        cv_.put(mx + 57 + k, 97 - (k % 2), SKINV, 4.4, lit=LT)
        cv_.flat(mx + 58 + k, 96 - (k % 2), (255, 236, 230)) if k % 2 == 0 else None
    cv_.disc(mx + 54, 97, 1.2, 1.0, GOLDV, 5.4, lit=LT)                    # l'anell
    # el coll i el cap
    cv_.rect(hx - 4, 58, hx + 4, 67, SKINV, lambda x, y: 3.2 - (x - hx) * 0.15 - (0.8 if y < 62 else 0), lit=LT)
    cv_.disc(hx, hy, 8.5, 11.5, SKINV, lambda nx, ny: 3.8 - nx * 1.0 - ny * 0.2 - max(0.0, ny - 0.6) * 1.6, lit=LT)
    cv_.disc(hx - 9, hy + 1, 1.6, 3, SKINV, 3.0, lit=LT)
    cv_.disc(hx + 9, hy + 1, 1.6, 3, SKINV, 2.2, lit=LT)
    # el cabell blanc, enrere amb gomina, i els polsos
    for y in range(hy - 14, hy - 2):
        for x in range(hx - 10, hx + 11):
            dx_, dy_ = (x - hx) / 10, (y - hy + 2) / 12
            if dx_ * dx_ + dy_ * dy_ <= 1 and y < hy - 7 + abs(x - hx) * 0.5:
                comb = 1.2 if (x - hx + (y - hy) // 2) % 3 == 0 else 0
                cv_.put(x, y, SUITV, 4.6 - dx_ * 0.8 + comb - (hy - 8 - y) * 0.04, lit=LT)
    for y in range(hy - 6, hy + 3):
        cv_.put(hx - 9, y, SUITV, 4.4, lit=LT)
        cv_.put(hx + 9, y, SUITV, 3.4, lit=LT)
    # la cara
    for side in (-1, 1):
        cv_.hline(hx + side * 2, hx + side * 5, hy - 4 - (1 if side * 3 == 3 else 0) * 0, SUITV, 4.6, lit=LT)
        cv_.put(hx + side * 5, hy - 3, SUITV, 3.6, lit=LT)
        cv_.flat(hx + side * 3, hy - 1, (30, 26, 40))
        cv_.flat(hx + side * 4, hy - 1, (30, 26, 40) if side < 0 else (60, 70, 100))
        cv_.put(hx + side * 3, hy, SKINV, 2.0, lit=LT)                    # la bossa de l'ull
    cv_.line(hx + 1, hy - 1, hx + 1, hy + 4, SKINV, 2.4, lit=LT)          # el nas, llarg
    cv_.put(hx, hy + 5, SKINV, 1.8, lit=LT)
    cv_.put(hx + 2, hy + 5, SKINV, 1.8, lit=LT)
    cv_.line(hx - 5, hy + 4, hx - 6, hy + 7, SKINV, 2.4, lit=LT)          # els plecs del somriure
    cv_.line(hx + 5, hy + 4, hx + 6, hy + 7, SKINV, 2.0, lit=LT)
    cv_.hline(hx - 4, hx + 4, hy + 7, [(90, 30, 34)], 0, lit=0)           # la boca
    cv_.put(hx - 5, hy + 6, [(90, 30, 34)], 0, lit=0)
    cv_.put(hx + 5, hy + 6, [(90, 30, 34)], 0, lit=0)
    cv_.hline(hx - 3, hx + 3, hy + 8, [(255, 255, 255)], 0, lit=0)        # les dents, massa blanques
    cv_.hline(hx - 2, hx + 2, hy + 9, SKINV, 2.0, lit=LT)
    cv_.flat(hx + 1, hy + 8, (255, 255, 255))
    # en Dividend, damunt el coixí de vellut vermell, en una tauleta d'or
    dx, dy = 310, 104
    cv_.rect(dx - 14, 120, dx + 14, 129, GOLDV, lambda x, y: 4.2 - (x - dx) * 0.06, lit=LT)
    cv_.hline(dx - 16, dx + 16, 120, GOLDV, 5.0, lit=LT)
    cv_.disc(dx, 117, 18, 5, REDV, lambda nx, ny: 3.6 - ny * 1.4 - nx * 0.4, lit=LT)
    for tx in (dx - 18, dx + 18):
        cv_.vline(tx, 117, 121, GOLDV, 4.6, lit=LT)
        cv_.disc(tx, 123, 1.4, 1.8, GOLDV, 4.6, lit=LT)
    cv_.disc(dx, 106, 8.5, 8.5, SUITV, lambda nx, ny: 4.6 - nx * 0.8 - ny * 0.3 +
             (0.8 if (int(nx * 6) + int(ny * 6)) % 3 == 0 else 0), lit=LT)
    for y in range(106, 115):                                             # el banyador de ratlles, blau i blanc
        for x in range(dx - 9, dx + 10):
            if ((x - dx) / 9) ** 2 + ((y - 106) / 9) ** 2 <= 1 and (y - 106) // 2 % 2 == 0:
                cv_.put(x, y, STRIPE, 2.6 - (x - dx) * 0.08, lit=LT)
    cv_.disc(dx - 5, 114, 3, 2, SUITV, 4.6, lit=LT)                        # les potes del davant
    cv_.disc(dx + 5, 114, 3, 2, SUITV, 3.8, lit=LT)
    cv_.disc(dx + 1, 92, 7, 6, SUITV, lambda nx, ny: 4.8 - nx * 0.6 - ny * 0.6, lit=LT)
    cv_.disc(dx - 6, 95, 2.4, 4.4, SUITV, 3.6, lit=LT)                      # les orelles caigudes
    cv_.disc(dx + 8, 95, 2.4, 4.4, SUITV, 3.0, lit=LT)
    cv_.disc(dx + 1, 87, 4, 2.6, SUITV, 5.4, lit=LT)                        # el tupè pentinat
    cv_.disc(dx + 1, 84.5, 2, 1.2, MAGENTA, 3.0, lit=LT)                    # el llacet
    cv_.flat(dx - 2, 91, (20, 16, 20))
    cv_.flat(dx + 3, 91, (20, 16, 20))
    cv_.flat(dx + 1, 94, (20, 16, 20))
    cv_.flat(dx + 1, 96, (230, 110, 130))                                   # la llengua
    # la mà del Magnat, damunt del gos (va per sobre)
    cv_.disc(mx + 58, 95, 4, 2.6, SKINV, lambda nx, ny: 4.0 - nx * 0.6 - ny * 0.8, lit=LT)
    # el contorn fosc, de pintura, al voltant de les figures
    # (en píxels reals: el contorn fa un píxel de sala de gruix, cv.S píxels reals)
    F = fig.img.load()
    k = cv.S
    near = [(d, 0) for d in range(-k, k + 1) if d] + [(0, d) for d in range(-k, k + 1) if d]
    for X, Y, _, _ in cv.pixels(PAINT[0] + 9, PAINT[1] + 9, PAINT[2] - 9, PAINT[3] - 9):
        if F[X, Y][3]:
            continue
        if any(F[X + ddx, Y + ddy][3] for ddx, ddy in near):
            cv.P[X, Y] = mix(cv.P[X, Y], (26, 14, 36), 0.75) + (255,)
    cv.img.alpha_composite(fig.img)
    cv.P = cv.img.load()


def apliques(cv):
    for ax in (176, 372):
        cv.rect(ax - 2, 76, ax + 2, 84, GOLDV, lambda x, y: 4.6 - (x - ax) * 0.3)
        cv.line(ax, 80, ax - 6, 72, GOLDV, 4.2)
        cv.line(ax, 80, ax + 6, 72, GOLDV, 3.4)
        for sx in (ax - 6, ax + 6):
            cv.rect(sx - 1, 66, sx + 1, 71, WHITEV, 5.6, lit=0)
            cv.flat(sx, 64, (255, 230, 150))
            cv.flat(sx, 65, (255, 200, 100))
            cv.glow(sx, 65, 10, (255, 230, 170), 0.35)


# ─── La calaixera i la paperera ────────────────────────────────────────────

def calaixera(cv):
    x0, y0, x1, y1 = CALAIX
    ombra(cv, (x0 + x1) / 2 + 4, y1 + 2, (x1 - x0) / 2 + 2, 3, 0.4)
    top = y0
    # el sobre de marbre i el cos de laca blanca, panxut
    cv.rect(x0 - 3, top, x1 + 3, top + 4, MARBLE, lambda x, y: 5.6 if y == top else 4.2)
    cv.hline(x0 - 3, x1 + 3, top + 5, GOLDV, 3.4)
    for y in range(top + 6, y1 - 8):
        bulge = math.sin((y - top - 6) / (y1 - 14 - top) * math.pi) * 3
        for x in range(int(x0 - bulge), int(x1 + bulge) + 1):
            u = (x - x0) / (x1 - x0)
            cv.put(x, y, WHITEV, 4.8 - u * 0.8 + (0.8 if u < 0.06 else 0))
    for row in range(2):
        ry0 = top + 9 + row * 17
        for col in range(2):
            cx0 = x0 + 4 + col * ((x1 - x0) // 2)
            cx1 = cx0 + (x1 - x0) // 2 - 8
            for x in range(cx0, cx1 + 1):
                cv.put(x, ry0, GOLDV, 4.2)
                cv.put(x, ry0 + 13, GOLDV, 3.0)
            for y in range(ry0, ry0 + 14):
                cv.put(cx0, y, GOLDV, 4.0)
                cv.put(cx1, y, GOLDV, 3.0)
            kx = (cx0 + cx1) // 2
            cv.disc(kx, ry0 + 7, 2, 2, GOLDV, lambda nx, ny: 5.0 - nx - ny)
    # les potes corbes d'or
    for lx, side in ((x0 + 2, -1), (x1 - 2, 1)):
        for k in range(9):
            cv.put(lx + side * (k * 0.35), y1 - 8 + k, GOLDV, 4.4 - k * 0.1)
            cv.put(lx + side * (k * 0.35) - side, y1 - 8 + k, GOLDV, 3.0)
    cv.poly([(x0 + 20, y1 - 8), (x1 - 20, y1 - 8), ((x0 + x1) // 2 + 6, y1 - 4), ((x0 + x1) // 2 - 6, y1 - 4)],
            GOLDV, 4.0)
    # a sobre: el gerro amb flors de plàstic i el telèfon d'or
    vx = x0 + 16
    cv.poly([(vx - 6, top - 1), (vx + 6, top - 1), (vx + 4, top - 14), (vx + 7, top - 20), (vx - 7, top - 20),
             (vx - 4, top - 14)], WHITEV, lambda x, y: 5.0 - (x - vx) * 0.2)
    cv.hline(vx - 7, vx + 7, top - 20, GOLDV, 4.6)
    for i, (fx, fy) in enumerate(((vx - 8, top - 26), (vx, top - 29), (vx + 8, top - 25), (vx - 4, top - 23),
                                  (vx + 5, top - 22))):
        cv.line(vx + (fx - vx) * 0.3, top - 20, fx, fy, TURF, 4.0)
        flor(cv, fx, fy, FLOWERS[i % 5], size=3)
    px = x1 - 30                                                          # el telèfon d'or, de disc
    cv.poly([(px - 12, top - 1), (px + 12, top - 1), (px + 9, top - 10), (px - 9, top - 10)], GOLDV,
            lambda x, y: 4.2 - (x - px) * 0.05 + (y - top) * 0.05)
    cv.disc(px, top - 5, 4, 3, WHITEV, 4.6)
    cv.ring(px, top - 5, 3, GOLDV, 3.0, step=45)
    cv.poly([(px - 14, top - 13), (px + 14, top - 13), (px + 12, top - 10), (px - 12, top - 10)], GOLDV, 4.8)
    cv.disc(px - 13, top - 13, 3, 2.4, GOLDV, 4.4)
    cv.disc(px + 13, top - 13, 3, 2.4, GOLDV, 3.6)


def paperera(cv):
    """La paperera daurada: un cilindre d'or amb anelles i, a dins, papers arrugats."""
    cx, by = PAPER
    ombra(cv, cx + 5, by + 2, 13, 2.4, 0.5)
    h, rt, rb = 26, 10, 8
    for y in range(by - h, by + 1):
        t = (y - by + h) / h
        r = rt + (rb - rt) * t
        for x in range(int(cx - r), int(cx + r) + 1):
            u = (x - cx) / r
            lvl = 4.2 - u * 1.6 - u * u * 1.2
            if (y - by + h) in (3, h - 3):
                lvl += 1.0
            if 0.2 < (u + 1) / 2 < 0.3:
                lvl += 1.2
            cv.put(x, y, GOLDV, lvl)
    cv.disc(cx, by - h, rt, 2.6, GOLDV, lambda nx, ny: 5.2 if ny < -0.1 else 2.0)
    cv.disc(cx, by - h + 0.5, rt - 1.5, 1.6, GOLDV, 1.4)
    # els papers arrugats que sobresurten
    for px, py, r in ((cx - 3, by - h - 2, 3.4), (cx + 3, by - h - 3, 3.0)):
        cv.disc(px, py, r, r * 0.8, MARBLE, lambda nx, ny: 4.6 - nx - ny + (0.8 if hr(int(nx * 4), int(ny * 4)) > 0.6 else 0))
    cv.line(cx - 5, by - h - 3, cx - 1, by - h - 1, MARBLE, 2.4)
    gota(cv, cx - 1, by - 13, 0.6)


# ─── El finestral ──────────────────────────────────────────────────────────

def finestral(cv):
    """El finestral al jardí: cel d'anunci, gespa a franges, el parterre, un arbre de piruleta i, al fons, el
    cobert verd d'en Nil. Marc d'or, cortines blanques recollides amb borles."""
    x0, y0, x1, y1 = WIN
    hz = 132
    for y in range(y0, y1 + 1):
        for x in range(x0, x1 + 1):
            if y < hz:
                cv.put(x, y, SKYV, 2.0 + (y - y0) / (hz - y0) * 4.4, lit=0)
            else:
                band = int(math.floor(math.atan2(x - 520, y - 100) * 7 + 50)) % 2
                cv.put(x, y, TURF, 4.0 + (0.8 if band else 0) + (0.6 if hr(x, y, 7) > 0.9 else 0), lit=0)
    # núvols de catàleg
    for ncx, ncy, s in ((470, 58, 0.8), (566, 44, 1.0)):
        for ddx, ddy, r in ((-14, 2, 8), (-4, -5, 10), (8, -2, 9), (17, 3, 6)):
            cv.disc(ncx + ddx * s, ncy + ddy * s, r * s, r * s * 0.85, CLOUDV, lambda nx, ny: 4.4 - ny * 1.4, lit=0)
        cv.rect(ncx - 20 * s, ncy + 5 * s, ncx + 22 * s, ncy + 7 * s, CLOUDV, 2.6, lit=0)
    # la bardissa i el cobert, petit, al fons (de fusta: l'únic que no brilla)
    cv.rect(x0, hz - 10, x1, hz, TURF, lambda x, y: 3.0 + (0.8 if y == hz - 10 else 0), lit=0)
    sx = 556
    cv.poly([(sx - 16, hz - 4), (sx, hz - 22), (sx + 16, hz - 4)], [(80, 40, 30), (120, 70, 50), (150, 100, 70)], 1.4, lit=0)
    cv.rect(sx - 13, hz - 6, sx + 13, hz + 4, SHEDG, lambda x, y: 3.0 - (1.0 if (x - sx) % 4 == 0 else 0), lit=0)
    cv.rect(sx - 3, hz - 4, sx + 3, hz + 4, SHEDG, 1.4, lit=0)
    arbre_rodo(cv, 476, 150, 10, lit=0)
    arbre_rodo(cv, 596, 146, 7, lit=0)
    # el parterre de flors, a baix
    for i in range(70):
        fx = x0 + 6 + hr(i, 1) * (x1 - x0 - 12)
        fy = 176 + hr(i, 2) * 30
        flor(cv, round(fx), round(fy), FLOWERS[i % 5], size=2, lit=0)
    # el vidre: reflexos en diagonal
    for X, Y, x, y in cv.pixels(x0, y0, x1, y1):                            # (píxel a píxel, a la resolució real)
        d = (x - x0) + (y - y0) * 0.5
        if 20 < d % 90 < 26 or 32 < d % 90 < 34:
            cv.P[X, Y] = mix(cv.P[X, Y], (255, 255, 255), 0.35) + (255,)
    # el marc d'or i els muntants
    for mx in (x0 + (x1 - x0) // 3, x0 + 2 * (x1 - x0) // 3):
        cv.rect(mx - 1, y0, mx + 1, y1, GOLDV, lambda x, y, mx=mx: 4.8 - (x - mx) * 0.8)
    cv.rect(x0, 100, x1, 102, GOLDV, lambda x, y: 4.8 - (y - 100) * 0.8)
    for xa, ya, xb, yb in ((x0 - 5, y0 - 5, x1 + 5, y0 - 1), (x0 - 5, y1 + 1, x1 + 5, y1 + 3),
                           (x0 - 5, y0, x0 - 1, y1), (x1 + 1, y0, x1 + 5, y1)):
        cv.rect(xa, ya, xb, yb, GOLDV, lambda x, y: 4.4 + (0.6 if (x + y) % 5 == 0 else 0))
    # les cortines: plecs blancs, recollides amb borles d'or
    for side in (-1, 1):
        edge = x0 - 8 if side < 0 else x1 + 8
        for y in range(y0 - 8, y1 + 3):
            t = (y - y0 + 8) / (y1 - y0 + 11)
            pinch = 1 - 0.55 * math.exp(-((t - 0.55) / 0.12) ** 2)
            w = 30 * pinch + 6
            for k in range(int(w)):
                x = edge + k if side < 0 else edge - k
                fold = math.sin(k * 0.9 * (1 / pinch) + 0.5) * 0.9
                cv.put(x, y, WHITEV, 4.6 + fold - (k / w) * 0.6)
        ty = y0 + (y1 - y0) * 0.55
        tx = edge + 12 if side < 0 else edge - 12
        cv.rect(tx - 8, ty - 1, tx + 8, ty + 1, GOLDV, 4.6)
        cv.disc(tx + side * -9, ty + 4, 2, 3, GOLDV, 4.2)
        cv.vline(round(tx + side * -9), ty + 7, ty + 12, GOLDV, 3.6)
    # la galeria de dalt (el bambalina)
    cv.rect(x0 - 14, y0 - 12, x1 + 14, y0 - 2, WHITEV, lambda x, y: 5.0 - (y - y0 + 12) * 0.08 +
            (0.8 if (x // 8) % 2 else 0) * (y > y0 - 6))
    cv.hline(x0 - 14, x1 + 14, y0 - 12, GOLDV, 4.8)
    cv.hline(x0 - 14, x1 + 14, y0 - 2, GOLDV, 3.4)


# ─── Muntatge ───────────────────────────────────────────────────────────────

def bg(cv):
    paret(cv)
    terra(cv)
    catifa(cv)
    porta(cv)
    arxivador(cv)
    quadre(cv)
    apliques(cv)
    calaixera(cv)
    paperera(cv)
    finestral(cv)
    for y in range(RH, H):
        for x in range(W):
            cv.flat(x, y, (0, 0, 0))
