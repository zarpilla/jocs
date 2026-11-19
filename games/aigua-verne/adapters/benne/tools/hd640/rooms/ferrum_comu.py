"""
Aigua Verne — peces comunes de les sales de Ferrum (el carrer, el sindicat, la fosa i la plaça dels postcrèdits).

Ferrum és un planeta miner: maó ennegrit de sutge, ferro i rovell, carbó, i un cel de fum taronja-grisenc. Aquí hi
ha les rampes del planeta, el cel de fum, l'horitzó (escombreres, el castellet de la mina, xemeneies i la Canonada),
les parets de maó, les llambordes, el panell del preu, la font de Verne, els comptadors d'aigua i els miners de fons
(figures petites, no clicables: la canalla del piquet, la cua dels postcrèdits).
"""
import hd640  # noqa: F401  (abans que cap hd.rooms: posa la llibreria a 640×360)

import math

from PIL import Image

from hd.pix import Canvas, W, H, hr, mix, B4
from hd.rooms.comu import text, text_width
from hd.rooms.exterior import fbm, vnoise, smooth

RH = 260                           # la sala (la barra de verbs va de 260 a 359)

# ─── Rampes (fosc → clar) ───────────────────────────────────────────────────
SMOG = [(34, 28, 30), (50, 40, 40), (68, 54, 50), (90, 70, 60), (112, 86, 68), (136, 102, 76), (160, 118, 82),
        (184, 136, 90), (206, 156, 100), (226, 180, 120), (242, 206, 148)]
HAZE = [(70, 60, 58), (92, 80, 74), (116, 100, 88), (140, 120, 102), (164, 140, 114), (186, 160, 126)]
SLAGF = [(22, 18, 20), (34, 28, 30), (48, 40, 40), (64, 52, 50), (82, 66, 60)]
SOOT = [(16, 10, 12), (28, 16, 16), (44, 24, 22), (62, 34, 28), (82, 46, 34), (104, 60, 42), (128, 76, 52),
        (152, 96, 64), (176, 118, 80)]
MORTAR = [(20, 16, 16), (34, 28, 26), (52, 44, 40), (72, 62, 56), (94, 84, 74), (118, 106, 92)]
COB = [(14, 12, 14), (24, 20, 22), (36, 30, 32), (50, 42, 42), (66, 56, 54), (84, 72, 66), (104, 90, 80),
       (126, 110, 96), (148, 130, 112)]
COAL = [(6, 6, 8), (14, 14, 16), (24, 24, 28), (38, 38, 42), (56, 56, 60), (80, 80, 84)]
IRONF = [(12, 12, 16), (22, 22, 28), (34, 34, 40), (48, 48, 54), (64, 62, 68), (84, 80, 84), (108, 102, 104),
         (136, 128, 126), (168, 160, 154)]
RUSTF = [(26, 12, 10), (48, 22, 14), (74, 34, 20), (102, 48, 26), (132, 64, 32), (160, 84, 42), (186, 108, 58),
         (208, 136, 80)]
TIN = [(30, 32, 34), (50, 54, 56), (74, 78, 80), (100, 104, 104), (128, 132, 130), (156, 160, 156), (184, 186, 180),
       (210, 210, 204)]
PLANKF = [(20, 14, 12), (36, 24, 18), (54, 36, 26), (74, 50, 34), (96, 66, 44), (120, 84, 56), (144, 104, 70),
          (168, 126, 88)]
WHITEV = [(72, 78, 90), (110, 116, 128), (150, 154, 164), (186, 188, 196), (214, 216, 222), (234, 235, 240),
          (248, 248, 252), (255, 255, 255)]
BLUEV = [(10, 30, 70), (20, 60, 130), (40, 100, 190), (90, 160, 230), (170, 210, 250)]
REDV = [(40, 6, 8), (90, 14, 16), (150, 24, 24), (210, 44, 36), (250, 96, 76), (255, 170, 150)]
BLACKT = [(8, 8, 10), (18, 18, 20), (30, 30, 32), (46, 46, 48), (66, 66, 68)]
LED = [(30, 6, 4), (90, 20, 10), (180, 50, 20), (250, 120, 40), (255, 200, 120)]
FIREF = [(60, 10, 8), (120, 24, 10), (180, 52, 14), (226, 96, 24), (250, 150, 50), (255, 206, 110), (255, 244, 200)]
GLOWF = [(70, 20, 10), (130, 44, 14), (190, 84, 24), (236, 132, 40), (255, 186, 80), (255, 230, 160)]
CLOTH = [(60, 54, 46), (100, 92, 78), (140, 130, 110), (178, 168, 144), (210, 200, 176), (232, 224, 202)]
REDP = [(40, 8, 10), (76, 14, 16), (116, 24, 22), (156, 38, 30), (190, 58, 40), (220, 90, 60)]
WATER = [(20, 40, 60), (36, 70, 100), (60, 110, 150), (100, 160, 200), (160, 210, 236), (226, 246, 255)]
SKINF = [(52, 30, 24), (86, 52, 38), (124, 80, 56), (160, 110, 78), (196, 146, 108), (224, 182, 142)]
JACK = [(14, 16, 20), (26, 28, 34), (40, 44, 50), (56, 60, 66), (76, 80, 84), (100, 102, 104)]
DENIM = [(12, 16, 26), (20, 28, 42), (32, 42, 60), (46, 58, 80), (64, 78, 100)]
HELM = [(40, 30, 6), (90, 66, 12), (150, 112, 24), (206, 160, 40), (240, 204, 90), (255, 236, 160)]
WARMG = (255, 170, 80)


# ─── Lletres i signes que no té la font petita ──────────────────────────────

def tri(cv, x, y, col, up=True):
    """▲ (o ▼) de 5×3, amb el cantó de dalt a l'esquerra a (x, y)."""
    for j in range(3):
        w = j if up else 2 - j
        for i in range(-w, w + 1):
            cv.flat(x + 2 + i, y + 1 + j, col)
    return 5


def colon(cv, x, y, col):
    """₡ (el crèdit): una C amb dues ratlles."""
    for yy, row in enumerate(('0110', '1000', '1000', '1000', '0110')):
        for i, b in enumerate(row):
            if b == '1':
                cv.flat(x + i, y + yy, col)
    for yy in range(-1, 6):
        if yy in (-1, 5) or yy % 2 == 0:
            cv.flat(x + 1, y + yy, col)
    return 4


QGLYPH = ('010', '101', '101', '101', '011')


def qtext(cv, s, x, y, ramp, lvl, lit=1.0, flat=None):
    """Com `text`, però amb una Q que es llegeix (la de la font petita sembla una E a mida de pancarta)."""
    cx = x
    for ch in s:
        if ch == 'Q':
            for j, row in enumerate(QGLYPH):
                for i, b in enumerate(row):
                    if b == '1':
                        cv.flat(cx + i, y + j, flat) if flat else cv.put(cx + i, y + j, ramp, lvl, lit)
            cv.flat(cx + 3, y + 5, flat) if flat else cv.put(cx + 3, y + 5, ramp, lvl, lit)
            cx += 4
        else:
            cx += text(cv, ch, cx, y, ramp, lvl, lit, flat=flat) + 1
    return cx - x - 1


# ─── El cel de fum i l'horitzó ──────────────────────────────────────────────

def smog_sky(cv, hor, sun=(150, 58), seed=3, x0=0, x1=W - 1, bright=0.0):
    """Cel de fum: bandes de sutge que s'arrosseguen, més clar i taronja a l'horitzó; un sol apagat."""
    for y in range(0, hor + 1):
        t = y / hor
        for x in range(x0, x1 + 1):
            d = math.hypot(x - sun[0], (y - sun[1]) * 1.4)
            band = fbm(x / 120 + y / 60, y / 9, seed)
            wisp = fbm(x / 40 - y / 30, y / 4, seed + 5)
            lvl = 1.4 + 6.2 * t ** 1.3 + 2.6 * max(0.0, 1 - d / 190) ** 2 + bright
            lvl += (band - 0.5) * 2.2 + (wisp - 0.5) * 0.8
            cv.put(x, y, SMOG, lvl, lit=0)
    cv.glow(sun[0], sun[1], 26, (255, 214, 150), 0.6)
    cv.disc(sun[0], sun[1], 9, 9, SMOG, lambda nx, ny: 9.4 - (fbm(nx * 2, ny * 3, seed + 9) - 0.5) * 3, lit=0)
    # una bandada de fum que passa per davant del sol
    for x in range(sun[0] - 30, sun[0] + 34):
        for y in range(sun[1] - 2, sun[1] + 5):
            f = fbm(x / 14, y / 3, seed + 11)
            if f > 0.52:
                cv.put(x, y, SMOG, 5.2 + (y - sun[1]) * 0.2, lit=0)


def canonada(cv, x, hor, top=0):
    """La Canonada: una columna blanca de l'horitzó fins més amunt del cel, entelada pel fum."""
    for y in range(top, hor):
        w = 2.0 + 2.6 * (y / hor)
        for xx in range(int(x - w), int(x + w) + 1):
            u = (xx - x) / max(1.0, w)
            lvl = 3.4 - u * 1.4 + (0.9 if y % 13 == 0 else 0) - (0.6 if y % 13 == 1 else 0)
            cv.put(xx, y, WHITEV, lvl, lit=0)
    cv.tint(x - 6, 0, x + 6, hor, (150, 112, 86), lambda xx, yy: 0.55 - 0.3 * yy / hor)   # el fum
    cv.rect(x - 9, hor - 6, x + 9, hor, WHITEV, 1.6, lit=0)                              # l'estació
    cv.rect(x - 9, hor - 7, x + 9, hor - 7, WHITEV, 3.0, lit=0)
    cv.tint(x - 9, hor - 7, x + 9, hor, (120, 90, 70), 0.4)
    cv.flat(x, 30, (240, 50, 40))
    cv.glow(x, 30, 4, (255, 90, 60), 0.5)


def headframe(cv, x, base, h=58, ramp=SLAGF):
    """El castellet de la mina: dues potes en A, la roda de dalt i el puntal."""
    top = base - h
    for k in range(2):
        cv.line(x - 12 + k, base, x - 2 + k, top, ramp, 2.4)
        cv.line(x + 10 + k, base, x + 2 + k, top, ramp, 2.4)
    for yy in range(top + 8, base, 9):                                                  # travessers en creu
        f = (yy - top) / h
        cv.line(x - 2 - 10 * f, yy, x + 2 + 8 * f, yy + 9, ramp, 2.0)
        cv.line(x + 2 + 8 * f, yy, x - 2 - 10 * f, yy + 9, ramp, 2.0)
    cv.line(x + 11, base, x + 28, top + 14, ramp, 2.4)                                  # el puntal
    cv.ring(x, top + 1, 6, ramp, 2.8, step=4)
    cv.ring(x, top + 1, 5, ramp, 2.8, step=6)
    cv.rect(x - 1, top, x + 1, top + 2, ramp, 3.4)
    cv.line(x + 4, top + 1, x + 28, top + 14, ramp, 1.6)                                # el cable


def chimney(cv, x, base, top, w=4, ramp=SLAGF, lvl=2.0):
    for y in range(top, base + 1):
        for xx in range(x - w, x + w + 1):
            cv.put(xx, y, ramp, lvl - (xx - x) / max(1, w) * 0.6 + (0.6 if (y - top) % 9 == 0 else 0))
    cv.rect(x - w - 1, top, x + w + 1, top + 2, ramp, lvl + 0.8)


def far_skyline(cv, hor, x0=0, x1=W - 1, seed=7, headframes=(), chimneys=()):
    """L'horitzó de Ferrum: escombreres (piles de carbonissa), el castellet i xemeneies, tot en silueta."""
    for x in range(x0, x1 + 1):
        h1 = hor - 4 - 26 * fbm(x / 70, 0.3, seed) ** 1.6
        h2 = hor - 2 - 10 * fbm(x / 34, 1.7, seed + 2)
        for y in range(int(h1), hor + 1):
            cv.put(x, y, HAZE, 2.6 - (y - h1) * 0.02 + (fbm(x / 10, y / 5, seed + 3) - 0.5) * 0.6, lit=0)
        for y in range(int(h2), hor + 1):
            cv.put(x, y, SLAGF, 3.2 + (fbm(x / 6, y / 3, seed + 4) - 0.5) * 1.0, lit=0)
    for hx, hb, hh in headframes:
        headframe(cv, hx, hb, hh, HAZE)
    for cx, cb, ct, cw in chimneys:
        chimney(cv, cx, cb, ct, cw, HAZE, 1.6)


# ─── Maó, finestres, llambordes ─────────────────────────────────────────────

def brick_lvl(x, y, x0=0, y0=0, bw=11, bh=4, base=3.4, seed=1, soot=None):
    """Nivell d'un píxel d'una paret de maó (fila desplaçada, morter fosc, cada maó una mica diferent)."""
    row = (y - y0) // bh
    off = (bw // 2) if row % 2 else 0
    col = (x - x0 + off) // bw
    mort = (y - y0) % bh == bh - 1 or (x - x0 + off) % bw == bw - 1
    v = base + (hr(row, col, seed) - 0.5) * 1.4 + (fbm(x / 18, y / 12, seed) - 0.5) * 1.2
    if hr(row, col, seed + 1) > 0.94:
        v -= 1.4                                                                       # un maó cremat
    if mort:
        v -= 1.8
    elif (y - y0) % bh == 0:
        v += 0.5                                                                       # el cantell de dalt
    if soot:
        v -= soot(x, y)
    return v


def brick_wall(cv, x0, y0, x1, y1, base=3.4, seed=1, soot=None, bw=11, bh=4, ramp=SOOT):
    cv.rect(x0, y0, x1, y1, ramp, lambda x, y: brick_lvl(x, y, x0, y0, bw, bh, base, seed, soot))


def soot_top(y_top, depth=40, k=2.0, seed=2):
    """El sutge: més negre a dalt, amb regalims que baixen."""
    def f(x, y):
        streak = fbm(x / 5, 0.5, seed) ** 2 * 1.6
        return k * max(0.0, 1 - (y - y_top) / (depth * (0.5 + streak))) + (fbm(x / 30, y / 20, seed + 1) - 0.5) * 0.8
    return f


def window(cv, x0, y0, w, h, lit=False, seed=0, ramp=SOOT):
    """Finestra de casa minera: llinda de pedra, vidres bruts (o encesos, càlids), ampit."""
    cv.rect(x0 - 2, y0 - 3, x0 + w + 1, y0 - 1, MORTAR, 3.6)                            # la llinda
    for y in range(y0, y0 + h):
        for x in range(x0, x0 + w):
            bar = (x - x0) == w // 2 or (y - y0) == h // 2
            if bar:
                cv.put(x, y, PLANKF, 2.0)
            elif lit:
                cv.put(x, y, GLOWF, 2.6 + (fbm(x / 4, y / 4, seed) - 0.5) * 1.6 - (y - y0) / h * 0.8, lit=0)
            else:
                cv.put(x, y, BLACKT, 1.0 + (0.8 if (x - x0 + y - y0) % 7 == 0 else 0) + (y - y0) / h * 0.8)
    cv.rect(x0 - 3, y0 + h, x0 + w + 2, y0 + h + 1, MORTAR, 3.2)                        # l'ampit
    if lit:
        cv.glow(x0 + w / 2, y0 + h / 2, max(w, h), WARMG, 0.25)


def cobbles(cv, y0, y1, x0=0, x1=W - 1, seed=5, base=3.0, vp=(320, 120)):
    """Llambordes amb pols de carbó: les files s'eixamplen cap a baix (perspectiva)."""
    for y in range(y0, y1 + 1):
        t = (y - y0) / max(1, y1 - y0)
        rh = 3 + t * 5                                                                  # alçada d'una fila
        acc = 0.0
        # fila per integració aproximada de l'alçada
        row = int(math.log(1 + (y - y0) / 3.0) * 4.2)
        frac = (math.log(1 + (y - y0) / 3.0) * 4.2) % 1
        cw = 6 + t * 10
        for x in range(x0, x1 + 1):
            px = (x - vp[0]) / (0.6 + t) + vp[0]                                         # fuga cap al centre
            off = (cw / 2) if row % 2 else 0
            cx = int((px + off + 1000) // cw)
            fx = ((px + off + 1000) % cw) / cw
            edge = frac < 0.14 or fx < 0.1
            v = base + t * 0.8 + (hr(row, cx, seed) - 0.5) * 1.2 + (0.6 if frac < 0.4 and not edge else 0)
            v += (fbm(x / 50, y / 14, seed + 1) - 0.5) * 1.4                             # pols de carbó a clapes
            if edge:
                v -= 1.8
            cv.put(x, y, COB, v)


# ─── El panell del preu ─────────────────────────────────────────────────────

def panell(cv, x0, y0, line1, line2, w=None, up=True, post=None, logo=True):
    """El panell de Verne: pantalla negra, la gota blava, lletres taronja. line2 pot dur '₡' i acaba amb ▲."""
    tw = max(text_width(line1) + (9 if logo else 0), text_width(line2.replace('₡', 'CC')) + 8)
    w = w or tw + 8
    h = 19
    if post:
        cv.rect(x0 + w // 2 - 1, y0 + h, x0 + w // 2 + 1, post, IRONF, lambda x, y: 3.4 - (x - x0 - w // 2 + 1) * 0.8)
    cv.rect(x0 - 1, y0 - 1, x0 + w, y0 + h, IRONF, 2.0)
    cv.rect(x0, y0, x0 + w - 1, y0 + h - 1, BLACKT, 1.0, lit=0)
    cv.rect(x0, y0, x0 + w - 1, y0, BLACKT, 3.0, lit=0)
    x = x0 + 4
    if logo:
        cv.disc(x + 2, y0 + 7, 2, 3, BLUEV, 3.0, lit=0)                                 # la gota de Verne
        cv.flat(x + 2, y0 + 3, BLUEV[3])
        x += 7
    text(cv, line1, x, y0 + 3, None, 0, flat=(210, 220, 236))
    x = x0 + 4 + (w - 8 - text_width(line2.replace('₡', 'CC')) - 6) // 2
    for ch in line2:
        if ch == '₡':
            x += colon(cv, x, y0 + 11, LED[3]) + 1
        elif ch == '▲':
            x += tri(cv, x, y0 + 11, LED[3], up) + 1
        elif ch == '▼':
            x += tri(cv, x, y0 + 11, LED[3], False) + 1
        else:
            x += text(cv, ch, x, y0 + 11, None, 0, flat=LED[3]) + 1
    cv.glow(x0 + w / 2, y0 + 14, w * 0.6, (250, 120, 40), 0.12)
    return w


# ─── La font de Verne ───────────────────────────────────────────────────────

def font_verne(cv, x, base, lector=True, tapat=False):
    """La font de Verne: un pilar blanc amb la gota, una pica, el broc i el lector de targetes vermell.
    `x`: el centre; `base`: on toca a terra. `tapat`: el lector tapat amb un tros de cartró (postcrèdits)."""
    # la pica (de pedra artificial blanca)
    cv.disc(x, base - 14, 22, 5, WHITEV, lambda nx, ny: 4.6 - nx * 0.8 - ny * 0.6)
    cv.rect(x - 22, base - 14, x + 22, base - 3, WHITEV, lambda xx, y: 4.0 - (xx - x) / 22 * 1.4 -
            (0.8 if y == base - 3 else 0))
    cv.disc(x, base - 3, 22, 3, WHITEV, lambda nx, ny: 3.0 - nx * 1.2 if ny > 0 else 3.6 - nx)
    cv.disc(x, base - 14, 19, 3.6, WHITEV, lambda nx, ny: 2.0 + ny * 1.6)               # dins la pica
    # el pilar
    px0, px1, top = x - 9, x + 9, base - 70
    cv.rect(px0, top, px1, base - 15, WHITEV, lambda xx, y: 5.2 - (xx - px0) * 0.12 + (1.0 if xx == px0 + 1 else 0) -
            (1.6 if xx == px1 else 0))
    cv.disc(x, top, 9, 4, WHITEV, lambda nx, ny: 5.8 - nx * 0.8 - ny * 0.4)            # la cúpula
    cv.disc(x - 1, top + 22, 3, 4, BLUEV, lambda nx, ny: 3.0 - nx - ny * 0.6, lit=0)    # la gota
    cv.flat(x - 1, top + 17, BLUEV[3])
    cv.rect(px0 + 2, top + 30, px1 - 2, top + 31, BLUEV, 1.6, lit=0)                    # la franja
    # el broc
    by = base - 38
    cv.disc(x, by, 3.5, 2, TIN, lambda nx, ny: 5.6 - ny * 1.6 - nx * 0.6)               # la volandera
    cv.rect(x - 1, by, x + 1, by + 6, TIN, lambda xx, y: 6.2 - (xx - x + 1) * 1.2)     # el broc, cap avall
    cv.rect(x - 2, by + 6, x + 2, by + 7, TIN, lambda xx, y: 5.0 - (xx - x) * 0.6)
    cv.flat(x, by + 8, (40, 40, 44))
    # el lector de targetes (vermell), al costat
    lx, ly = px1 - 6, top + 8
    if lector:
        cv.rect(lx, ly, lx + 9, ly + 13, REDV, lambda xx, y: 3.4 - (xx - lx) * 0.1 + (1.0 if y == ly else 0))
        cv.rect(lx + 2, ly + 2, lx + 7, ly + 5, BLACKT, 1.4, lit=0)                      # la pantalleta
        cv.flat(lx + 3, ly + 3, (255, 60, 40))
        cv.rect(lx + 2, ly + 8, lx + 7, ly + 8, BLACKT, 0.4, lit=0)                      # la ranura
        cv.flat(lx + 8, ly + 11, (255, 70, 50))
        cv.glow(lx + 8, ly + 11, 3, (255, 60, 40), 0.4)
        if tapat:
            cv.rect(lx - 1, ly + 1, lx + 10, ly + 10, PLANKF, lambda xx, y: 5.2 + (hr(xx, y) - 0.5) * 0.8)
            cv.line(lx - 2, ly + 2, lx + 11, ly + 1, CLOTH, 4.0)                          # cinta
            cv.line(lx - 2, ly + 9, lx + 11, ly + 10, CLOTH, 4.0)
    return x, base - 29                                                                  # on surt l'aigua


# ─── Comptadors d'aigua (els de Verne, arrencats de les cases) ──────────────

def comptador(cv, cx, cy, r=4, ang=0.0, seed=0):
    """Un comptador d'aigua: cos de llautó/ferro, l'esfera blanca, i els dos ràcords."""
    ca, sa = math.cos(ang), math.sin(ang)
    for k in (-1, 1):                                                                   # els ràcords
        for d in range(r + 1, r + 4):
            cv.put(cx + ca * d * k, cy + sa * d * k, RUSTF, 3.6 - (d - r) * 0.4)
            cv.put(cx + ca * d * k - sa, cy + sa * d * k + ca, RUSTF, 2.4)
    cv.disc(cx, cy, r + 1, r + 1, IRONF, lambda nx, ny: 4.4 - nx - ny * 1.2)
    cv.disc(cx, cy, r - 1, r - 1, WHITEV, lambda nx, ny: 3.8 - ny * 0.6)
    cv.disc(cx, cy, 0.8, 0.8, BLUEV, 2.6, lit=0)
    a = hr(seed, 4) * 6.28
    cv.line(cx, cy, cx + math.cos(a) * (r - 1), cy + math.sin(a) * (r - 1), REDV, 2.6, lit=0)


def pila_comptadors(cv, x0, x1, base, h, seed=3):
    """Una pila de comptadors arrencats, amb trossos de tub i algun ràcord solt."""
    cx = (x0 + x1) / 2
    hw = (x1 - x0) / 2
    pts = []
    for i in range(140):
        u = hr(i, seed) * 2 - 1
        top = base - h * (1 - abs(u) ** 1.6)
        v = hr(i, seed + 1)
        y = base - (base - top) * v ** 0.7
        pts.append((cx + u * hw, y, i))
    pts.sort(key=lambda p: p[1])
    # l'ombra i el munt de dessota (fosc)
    cv.disc(cx, base, hw + 4, 4, COAL, 1.6)
    for x, y, i in pts:
        if hr(i, seed + 2) < 0.12:
            a = hr(i, seed + 3) * 3.14
            for d in range(-7, 8):
                cv.put(x + math.cos(a) * d, y + math.sin(a) * d * 0.5, IRONF, 3.6)
                cv.put(x + math.cos(a) * d, y + math.sin(a) * d * 0.5 + 1, IRONF, 2.0)
        else:
            comptador(cv, x, y, r=3 + (1 if hr(i, seed + 4) > 0.6 else 0), ang=hr(i, seed + 5) * 3.14, seed=i)


# ─── Miners de fons (figures petites, part del fons) ────────────────────────

def _row(cv, y, xa, xb, ramp, lvl_fn):
    for x in range(int(round(xa)), int(round(xb)) + 1):
        cv.put(x, y, ramp, lvl_fn(x, y))


def miner(cv, x, yf, h=80, facing=-1, var=0, kid=False, seated=False, lamp=True, hold=None, light_from=-1,
          casc=None, cua=False):
    """Una figura de fons (de perfil o de tres quarts): casc, jaqueta de treball, pantalons i botes.
    `facing`: -1 mira a l'esquerra, 1 a la dreta. `light_from`: d'on li ve la llum (-1 esquerra, 1 dreta).
    `casc`: si duu casc (per defecte, els grans sí i la canalla a vegades); `cua`: cabell llarg recollit en una cua.
    No és un sprite: es dibuixa al fons (no es mou ni es clica)."""
    s = h / 80.0
    jack = (JACK, DENIM, RUSTF, PLANKF)[var % 4]
    trous = (DENIM, JACK, COAL, DENIM)[(var // 2) % 4]
    skin = SKINF
    hair_c = (COAL, PLANKF, RUSTF, IRONF)[var % 4]

    def L(xx, yy, base, cx, half):
        # llum lateral: més clar pel costat d'on ve la llum, contorn fosc als cantells
        u = (xx - cx) / max(1.0, half)
        return base + u * light_from * 0.9

    head_r = 6.2 * s
    if seated:
        hip_y = yf - 14 * s
        knee_x = x + facing * 14 * s
        # cames: cuixa horitzontal fins al genoll, canyella cap avall
        for yy in range(int(hip_y - 4 * s), int(hip_y + 2 * s) + 1):
            a, b = sorted((x - facing * 3 * s, knee_x))
            _row(cv, yy, a, b, trous, lambda xx, y_: 2.4 + (0.8 if yy < hip_y - 2 * s else 0))
        for yy in range(int(hip_y - 3 * s), int(yf - 3 * s) + 1):
            _row(cv, yy, knee_x - 3 * s, knee_x + 2 * s, trous, lambda xx, y_: L(xx, y_, 2.2, knee_x, 3 * s))
        for yy in range(int(yf - 3 * s), int(yf) + 1):                                 # bota
            _row(cv, yy, knee_x - 3 * s + min(0, facing) * 3 * s, knee_x + 3 * s + max(0, facing) * 2 * s, COAL,
                 lambda xx, y_: 2.0 + (0.8 if yy == int(yf - 3 * s) else 0))
        sh_y = hip_y - 26 * s
    else:
        hip_y = yf - 38 * s
        # cames, una lleugerament avançada
        for k, dx in ((0, -3.2 * s), (1, 3.2 * s)):
            lx = x + dx + (facing * 1.5 * s if k else 0)
            for yy in range(int(hip_y), int(yf - 3 * s) + 1):
                t = (yy - hip_y) / (yf - hip_y)
                hw = 3.6 * s - t * 0.6 * s
                _row(cv, yy, lx - hw, lx + hw, trous,
                     lambda xx, y_: L(xx, y_, 2.4 - k * 0.6 + (0.8 if abs(y_ - (hip_y + 20 * s)) < 1 else 0), lx, hw))
            for yy in range(int(yf - 4 * s), int(yf) + 1):                             # botes
                a = lx - 3.4 * s + min(0, facing) * 2.4 * s
                b = lx + 3.4 * s + max(0, facing) * 2.4 * s
                _row(cv, yy, a, b, COAL, lambda xx, y_: 2.2 + (1.0 if yy == int(yf - 4 * s) else 0) - k * 0.4)
        sh_y = hip_y - 28 * s
    # el tors (jaqueta), una mica corbat endavant
    for yy in range(int(sh_y), int(hip_y) + 2):
        t = (yy - sh_y) / max(1.0, hip_y - sh_y)
        hw = (8.0 - 1.4 * t) * s
        cx = x + facing * (1.2 - t * 1.2) * s
        _row(cv, yy, cx - hw, cx + hw, jack,
             lambda xx, y_: L(xx, y_, 3.0 - t * 0.4 + (0.8 if t < 0.08 else 0) - (0.6 if abs(xx - cx) > hw - 1 else 0),
                              cx, hw))
    # bandes reflectants de la jaqueta (els miners en duen)
    if not kid and var % 2 == 0:
        yy = int(sh_y + (hip_y - sh_y) * 0.62)
        cx = x + facing * 0.4 * s
        _row(cv, yy, cx - 7 * s, cx + 7 * s, HELM, lambda xx, y_: 3.2 + (xx - cx) / (7 * s) * light_from * 0.6)
    # el braç (de davant), penjant o portant alguna cosa
    ax = x + facing * 2 * s - light_from * 0.0
    for yy in range(int(sh_y + 2 * s), int(sh_y + 22 * s)):
        t = (yy - sh_y) / (22 * s)
        bx = ax + facing * t * 3 * s
        _row(cv, yy, bx - 2.4 * s, bx + 2.4 * s, jack, lambda xx, y_: 2.2 + light_from * (xx - bx) * 0.2)
    hx, hy = ax + facing * 3 * s, sh_y + 23 * s
    cv.disc(hx, hy, 2.0 * s, 2.0 * s, skin, 3.0)
    if hold == 'bidon':                                                                  # una garrafa buida
        cv.rect(hx - 4 * s, hy, hx + 4 * s, hy + 11 * s, WHITEV, lambda xx, y_: 3.6 + light_from * (xx - hx) * 0.2)
        cv.rect(hx - 1 * s, hy - 2 * s, hx + 1 * s, hy, BLUEV, 2.6)
    elif hold == 'got':
        cv.rect(hx - 1.5 * s, hy - 4 * s, hx + 1.5 * s, hy, TIN, 4.0)
    # el coll i el cap
    neck_y = sh_y - 2 * s
    cv.rect(x - 2 * s + facing * s, neck_y, x + 2 * s + facing * s, sh_y + 1, skin, 2.4)
    hcx, hcy = x + facing * 1.6 * s, sh_y - head_r - 1 * s
    cv.disc(hcx, hcy, head_r * 0.92, head_r, skin, lambda nx, ny: 3.6 + nx * light_from * 0.7 - ny * 0.3)
    cv.disc(hcx - facing * 3.6 * s, hcy + 0.2 * s, head_r * 0.42, head_r * 0.72, hair_c,
            lambda nx, ny: 2.4 + nx * light_from * 0.5)                                 # el clatell, de cabell
    if cua:
        for k in range(int(9 * s)):
            cv.put(hcx - facing * (5.2 * s + k * 0.25), hcy + 2 * s + k, hair_c, 2.6 - k * 0.05)
            cv.put(hcx - facing * (6.2 * s + k * 0.25), hcy + 2 * s + k, hair_c, 1.8)
    cv.put(hcx + facing * head_r * 0.9, hcy + 1 * s, skin, 3.4)                         # el nas
    cv.put(hcx + facing * head_r * 0.45, hcy - 0.5 * s, COAL, 0.6)                      # l'ull
    if casc is None:
        casc = not kid or var % 2
    if casc:
        # el casc amb el llum (els nens, el casc del pare, massa gran)
        cy = hcy - head_r * 0.35
        for yy in range(int(cy - head_r * 0.85), int(cy + 1)):
            t = (yy - (cy - head_r * 0.85)) / (head_r * 0.85)
            hw = head_r * (0.55 + 0.5 * math.sqrt(max(0.0, t)))
            _row(cv, yy, hcx - hw, hcx + hw, HELM, lambda xx, y_: 3.6 - t * 0.6 + (xx - hcx) / hw * light_from * 0.8)
        _row(cv, int(cy + 1), hcx - head_r * 1.25, hcx + head_r * 1.25, HELM, lambda xx, y_: 2.4)
        if lamp:
            lx = hcx + facing * head_r * 0.95
            cv.rect(lx - s, cy - 3 * s, lx + s, cy - 0.5 * s, TIN, 4.4)
            cv.flat(lx + facing * s, cy - 2 * s, (255, 236, 170) if hold != 'off' else (90, 90, 80))
    else:
        # cabell
        cv.disc(hcx - facing * s, hcy - head_r * 0.45, head_r, head_r * 0.6, hair_c, lambda nx, ny: 2.4 - ny * 0.4)


# ─── Fum (animacions) ───────────────────────────────────────────────────────

def smoke_frames(base, sources, n=24, ramp=None, bounds=None):
    """Fotogrames de fum que puja i s'escampa amb el vent (cap a la dreta). `sources`: [(x, y, amplada, alçada)].
    Retorna imatges RGBA transparents amb només els píxels del fum."""
    ramp = ramp or HAZE
    s = base.width // W                                     # píxels reals per píxel de sala (l'art pot ser a 2×)
    frames = []
    for f in range(n):
        img = Image.new('RGBA', base.size, (0, 0, 0, 0))
        P = img.load()
        S = base.load()
        ph = f / n
        for sx, sy, sw, sh in sources:
            for Y in range(max(0, int(sy - sh)) * s, (int(sy) + 1) * s):
                y = (Y + 0.5) / s - 0.5                                                # coordenada de sala
                t = (sy - y) / sh                                                      # 0 a la boca, 1 a dalt
                if t > 1:                                                              # (a 2×, la fila de dalt de tot)
                    continue
                drift = t * t * sh * 0.9
                for X in range(int(sx - sw - 4) * s, int(sx + sw + drift + 10) * s):
                    if not (0 <= X < W * s and 0 <= Y < RH * s):
                        continue
                    x = (X + 0.5) / s - 0.5
                    u = (x - sx - drift) / (sw * (1 + t * 2.2))
                    if abs(u) > 1.3:
                        continue
                    dens = (1 - t) ** 1.2 * max(0.0, 1 - u * u)
                    n_ = fbm((x - drift * 0.3) / 7, (y + ph * sh) / 6, int(sx) % 97)
                    dens *= 0.5 + n_ * 1.1
                    if dens > 0.32 + B4[Y & 3][X & 3] * 0.5:
                        o = S[X, Y]
                        k = min(0.85, dens)
                        col = mix(ramp[min(len(ramp) - 1, int(2 + n_ * 3))], o[:3], 1 - k)
                        P[X, Y] = col + (255,)
        frames.append(img)
    return frames


# ─── La nau de la fosa (fosa_forn i fosa_colada) ────────────────────────────

NAVE_FLOOR = 198                  # on la paret del fons toca a terra


def nave_wall(cv, x0, x1, top=30, seed=1, windows=(), pilasters=()):
    """La paret del fons de la nau: maó negre de sutge, pilastres, finestrals d'arc alts i bruts."""
    brick_wall(cv, x0, top, x1, NAVE_FLOOR, base=2.4, seed=seed, bw=12, bh=4,
               soot=lambda x, y: 1.2 * max(0.0, 1 - (y - top) / 90) + (fbm(x / 40, y / 30, seed + 1) - 0.5) * 1.0)
    for px in pilasters:
        brick_wall(cv, px - 9, top, px + 9, NAVE_FLOOR, base=2.8, seed=seed + px, bw=6, bh=4)
        cv.rect(px - 9, top, px - 8, NAVE_FLOOR, SOOT, 3.6)
        cv.rect(px + 8, top, px + 9, NAVE_FLOOR, COAL, 1.0)
        cv.rect(px - 11, 92, px + 11, 96, MORTAR, lambda x, y: 3.4 - (y - 92) * 0.5)   # la mènsula del carril
    for wx, ww in windows:
        wy0, wy1 = 46, 104
        for y in range(wy0 - ww // 2, wy1):
            for x in range(wx - 3, wx + ww + 3):
                cx = wx + ww / 2
                r = math.hypot(x - cx, y - wy0)
                if y < wy0 and r > ww / 2 + 3:
                    continue
                inside = (y >= wy0 and wx <= x < wx + ww) or (y < wy0 and r <= ww / 2)
                if not inside:
                    cv.put(x, y, MORTAR, 2.6 + (hr(int(math.atan2(y - wy0, x - cx) * 6), 2) - 0.5) * 1.0)
                    continue
                bar = (x - wx) % 8 == 7 or (y - wy0) % 10 == 9
                broken = hr((x - wx) // 8, (y - wy0 + 40) // 10, wx) > 0.84
                if bar:
                    cv.put(x, y, COAL, 1.2, lit=0)
                elif broken:
                    cv.put(x, y, SMOG, 6.0 + (fbm(x / 5, y / 5, wx) - 0.5) * 2, lit=0)
                else:
                    cv.put(x, y, SMOG, 3.6 + (y - wy0) * 0.02 + (fbm(x / 4, y / 6, wx + 1) - 0.5) * 2.4, lit=0)
        cv.rect(wx - 4, wy1, wx + ww + 3, wy1 + 2, MORTAR, 3.0)


def light_shafts(cv, shafts, k=0.22, col=(200, 150, 110), y1=NAVE_FLOOR + 30):
    """Raigs de llum (de les finestres) a través de l'aire polsós, inclinats: tint a quadres, molt suau."""
    for wx, ww, dx in shafts:
        def f(x, y, wx=wx, ww=ww, dx=dx):
            t = (y - 104) / (y1 - 104)
            if not 0 <= t <= 1:                                     # (a 2×, y pot passar una mica de y1)
                return 0
            c = wx + dx * t
            u = (x - c) / ww
            if 0 <= u <= 1:
                return k * (1 - t) ** 1.2 * (0.6 + 0.8 * fbm(x / 12, y / 30, wx))
            return 0
        cv.tint(0, 104, W - 1, y1, col, f)


def trusses(cv, y0=0, chord=30, seed=1):
    """Les encavallades de ferro del sostre, en silueta contra la foscor de dalt."""
    cv.rect(0, y0, W - 1, chord, COAL, lambda x, y: 0.8 + y * 0.03 + (fbm(x / 30, y / 8, seed) - 0.5) * 0.8, lit=0)
    for y in (chord, chord + 1):
        cv.rect(0, y, W - 1, y, IRONF, 2.6 - (y - chord) * 1.2)
    for x0 in range(-40, W + 40, 80):
        for x in range(x0, x0 + 80, 10):                                                 # diagonals
            cv.line(x, chord, x + 10, y0 + 6, IRONF, 1.6)
            cv.line(x + 10, y0 + 6, x + 10, chord, IRONF, 1.2)
        cv.rect(x0 - 1, y0, x0 + 1, chord, IRONF, 2.2)
    cv.rect(0, y0 + 5, W - 1, y0 + 6, IRONF, 1.8)


def crane_rail(cv, y=86):
    """El carril del pont grua, recolzat a les mènsules de les pilastres."""
    cv.rect(0, y, W - 1, y + 6, IRONF, lambda x, yy: 3.0 - (yy - y) * 0.3 + (0.8 if yy == y else 0) -
            (1.0 if x % 24 == 0 else 0))
    cv.rect(0, y + 7, W - 1, y + 7, COAL, 0.6)


def foundry_floor(cv, y0=NAVE_FLOOR, y1=RH - 1, seed=9, plates=()):
    """Terra de la fosa: sorra negra trepitjada, plaques de ferro, escòria i taques."""
    for y in range(y0, y1 + 1):
        t = (y - y0) / max(1, y1 - y0)
        for x in range(W):
            v = 2.0 + t * 1.0 + (fbm(x / 22, y / 7, seed) - 0.5) * 1.6 + (hr(x, y, seed) - 0.5) * 0.6
            cv.put(x, y, COB, v)
    for px0, py0, px1, py1 in plates:
        for y in range(py0, py1 + 1):
            for x in range(px0, px1 + 1):
                edge = x in (px0, px1) or y in (py0, py1)
                v = 3.0 + (fbm(x / 6, y / 4, seed + 2) - 0.5) * 1.4 + (0.8 if (x + y * 2) % 9 == 0 else 0)
                cv.put(x, y, IRONF, v - (1.6 if edge else 0))
    for i in range(70):                                                                 # escòria i grava
        x = hr(i, seed + 3) * W
        y = y0 + 4 + hr(i, seed + 4) * (y1 - y0 - 4)
        cv.disc(x, y, 1 + hr(i, 5) * 1.6, 1, SLAGF, lambda nx, ny: 3.4 - ny * 1.6)


def miner_c(cv, *a, **kw):
    """`miner` amb contorn fosc d'1 px de sala (l'estil de tot el joc), perquè la figura es llegeixi sobre el fons."""
    k = cv.S                                                # el contorn: un píxel de sala (k píxels reals)
    tmp = type(cv)(cv.w // k, cv.h // k, light=cv.light, transparent=True)
    miner(tmp, *a, **kw)
    bb = tmp.img.getbbox()
    if not bb:
        return
    T, D = tmp.img.load(), cv.img.load()
    x0, y0, x1, y1 = bb
    near = [(d, 0) for d in range(-k, k + 1) if d] + [(0, d) for d in range(-k, k + 1) if d]
    out = []
    for y in range(max(0, y0 - k), min(cv.h, y1 + k)):
        for x in range(max(0, x0 - k), min(cv.w, x1 + k)):
            if T[x, y][3]:
                continue
            if any(0 <= x + dx < cv.w and 0 <= y + dy < cv.h and T[x + dx, y + dy][3] for dx, dy in near):
                out.append((x, y))
    for x, y in out:
        o = D[x, y]
        T[x, y] = tuple(int(c * 0.35) for c in o[:3]) + (255,)
    cv.img.alpha_composite(tmp.img)


# ─── La llum càlida del capvespre: les finestres enceses i els fanals ─────────
# Separen els plans: la claror taronja de les finestres cau a les llambordes de davant de cada casa, i els fanals
# fan una bassa de llum a terra i un con tènue a l'aire.
CALIDA = (255, 168, 76)


def finestres_enceses(img, box, minim=10, junta=3):
    """Les finestres enceses d'un dibuix pla (els vidres de GLOWF clars) dins `box`: [(x0, y0, x1, y1)] en píxels del
    pla. Els vidres d'una mateixa finestra (separats pels muntants, a menys de `junta` píxels) fan una sola finestra."""
    x0, y0, x1, y1 = box
    P = img.load()
    on = set()
    for y in range(max(0, y0), min(img.height, y1)):
        for x in range(max(0, x0), min(img.width, x1)):
            r, g, b, a = P[x, y]
            if a and r >= 150 and g >= 60 and r - b >= 80:
                on.add((x, y))
    caixes = []
    while on:
        pila = [on.pop()]
        xs, ys = [], []
        while pila:
            x, y = pila.pop()
            xs.append(x)
            ys.append(y)
            for dx in (-1, 0, 1):
                for dy in (-1, 0, 1):
                    n = (x + dx, y + dy)
                    if n in on:
                        on.remove(n)
                        pila.append(n)
        caixes.append([min(xs), min(ys), max(xs) + 1, max(ys) + 1, len(xs)])
    fet = True
    while fet:                                                      # ajunta els vidres de la mateixa finestra
        fet = False
        for i in range(len(caixes)):
            for j in range(i + 1, len(caixes)):
                a, b = caixes[i], caixes[j]
                if (a[0] - junta <= b[2] and b[0] - junta <= a[2] and a[1] - junta <= b[3] and b[1] - junta <= a[3]):
                    caixes[i] = [min(a[0], b[0]), min(a[1], b[1]), max(a[2], b[2]), max(a[3], b[3]), a[4] + b[4]]
                    del caixes[j]
                    fet = True
                    break
            if fet:
                break
    return [tuple(c[:4]) for c in caixes if c[4] >= minim]


def llum_finestra(e, xa, xb, ya, yb, z, dx=0.0, dz=0.9, col=CALIDA, k=0.5, halo=True):
    """La claror d'una finestra encesa (x de `xa` a `xb`, alçada de `ya` a `yb`, a la façana z = `z`, que mira cap a
    −z) a les llambordes de davant: la finestra projectada pels raigs del llum de dins, que baixen (`dx`, `dz` per
    unitat d'alçada de la finestra), esvaïda a les vores i més tènue com més amunt és la finestra. `halo`: una mica
    de resplendor a la mateixa finestra."""
    n0 = 6 + 0.18 * ya                                              # (el llum de dins és a cada pis: no gaire lluny)
    n1 = n0 + (yb - ya) * dz
    P0 = (xa + n0 * dx, 0.4, z - n0)
    P1 = (xb + n0 * dx, 0.4, z - n0)
    P2 = (xb + n1 * dx, 0.4, z - n1)
    P3 = (xa + n1 * dx, 0.4, z - n1)
    w = xb - xa
    L3 = math.hypot((n1 - n0) * dx, n1 - n0)
    kk = k * max(0.35, 1 - ya / 260)

    def fn(s, t):
        es = min(1.0, s / 5, (w - s) / 5)
        et = min(1.0, t / 3, (L3 - t) / 9)
        return kk * max(0.0, es) * max(0.0, et)
    e.claror(P0, P1, P2, P3, col, fn)
    if halo:
        u, v, _ = e.cam.projecta(((xa + xb) / 2, (ya + yb) / 2, z - 2))
        r = max(4.0, e.cam.escala(((xa + xb) / 2, 0, z)) * max(w, yb - ya) * 0.9)
        e.cv.glow(u, v, r, (255, 190, 110), 0.22)


def _convex(pts):
    pts = sorted(set(pts))
    if len(pts) < 3:
        return pts

    def cross(o, a, b):
        return (a[0] - o[0]) * (b[1] - o[1]) - (a[1] - o[1]) * (b[0] - o[0])
    lo, up = [], []
    for p in pts:
        while len(lo) >= 2 and cross(lo[-2], lo[-1], p) <= 0:
            lo.pop()
        lo.append(p)
    for p in reversed(pts):
        while len(up) >= 2 and cross(up[-2], up[-1], p) <= 0:
            up.pop()
        up.append(p)
    return lo[:-1] + up[:-1]


def bassa_fanal(e, x, z, r=120, col=CALIDA, k=0.5):
    """La bassa de llum d'un fanal a les llambordes (centrada a x, z del terra, de radi `r`)."""
    e.claror((x - r, 0.5, z + r), (x + r, 0.5, z + r), (x + r, 0.5, z - r), (x - r, 0.5, z - r), col,
             lambda s, t: k * max(0.0, 1 - math.hypot(s - r, t - r) / r) ** 1.2)


def con_fanal(e, cap, r=90, col=(255, 200, 130), k=0.2, salta=(), terra=None):
    """El con de llum d'un fanal (de `cap`, el llum, fins a un cercle de radi `r` a terra, sota el llum o a `terra`
    = (x, z): en diagonal), a la pantalla: una claror tènue i tramada, més forta a prop del llum i al mig; no toca els
    sids de `salta` (el primer pla)."""
    cam, cv = e.cam, e.cv
    au, av, _ = cam.projecta(cap)
    x, _, z = cap
    if terra:
        x, z = terra
    gu, gv, _ = cam.projecta((x, 0, z))
    pts = [(au, av)] + [cam.projecta((x + r * math.cos(a), 0, z + r * math.sin(a)))[:2]
                        for a in [i * math.pi / 12 for i in range(24)]]
    poly = _convex([(round(p[0], 2), round(p[1], 2)) for p in pts])
    rx = max(1.0, max(abs(p[0] - gu) for p in pts[1:]))
    salta = {i for i, sid in enumerate(e.ids) if sid in salta}
    P = cv.P
    for X, Y in e._scan(poly):
        if e.amo[Y * cv.w + X] in salta:
            continue
        d = max(0.0, min(1.0, (Y + 0.5 - av) / max(1.0, gv - av)))
        half = 2 + rx * d
        q = abs(X + 0.5 - (au + (gu - au) * d)) / half
        if q >= 1:
            continue
        a = k * (1 - 0.55 * d) * (1 - q * q)
        if a < 0.25 and a * 4 < B4[Y & 3][X & 3]:
            continue
        o = P[X, Y]
        P[X, Y] = mix(o, col, min(1.0, a)) + (o[3],)
    cv.glow(au, av, 14, (255, 220, 160), 0.9)
    cv.glow(au, av, 5, (255, 248, 220), 1.0)


def fanal_paret(e, sid, x, y, z, ramp_ferro, ramp_llum):
    """Un fanal de paret (de ferro, amb el braç) a la façana z = `z` (que mira cap a −z), a l'alçada `y`: → el punt
    del llum (per a la bassa i el con)."""
    e.caixa(sid, x - 3, x + 3, y + 6, y + 9, z - 22, z, ramp_ferro, 1.8)                # el braç
    e.caixa(sid, x - 4, x + 4, y - 14, y + 12, z - 1.5, z, ramp_ferro, 1.4)             # la placa
    e.caixa(sid, x - 7, x + 7, y + 2, y + 6, z - 29, z - 15, ramp_ferro, 2.0)           # el barret
    e.caixa(sid, x - 5, x + 5, y - 10, y + 2, z - 27, z - 17, ramp_llum, 4.6,          # el vidre, encès
            cares={'davant': {'ramp': ramp_llum, 'lvl': 4.8}, 'esquerra': {'ramp': ramp_llum, 'lvl': 4.2},
                   'dreta': {'ramp': ramp_llum, 'lvl': 4.2}})
    return (x, y - 4, z - 22)
