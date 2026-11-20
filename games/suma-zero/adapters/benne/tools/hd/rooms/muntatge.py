"""
El muntatge del virus (cinemàtica, Acte 3): ROBIN HOOD 2.0 buida tots els comptes del món al «compte pont» i
paga la primera ronda, 12 € per persona. Una sola imatge per a totes les frases: una paret de sis pantalles,
com les de la sala de seguretat, cadascuna amb una vinyeta i el comptador en verd de terminal:
  - Mònaco: un iot blanc a la badia i un milionari a la coberta mirant el mòbil;
  - Nova York: gratacels a l'alba (allà són les cinc i quart) i la gràfica del fons que cau en picat;
  - Ginebra: un despatx amb el llac i el raig d'aigua; l'home de la corbata i la secretària, 12 € cadascun;
  - el bar La Propina: en Tomàs abaixa la persiana amb el ganxo;
  - un caixer automàtic: una àvia amb bastó davant de la pantalla i un cambrer que espera el sou;
  - el mapa del món, de punts, amb totes les línies que van a parar al compte pont.
A dalt, la capçalera «ROBIN HOOD 2.0» (verd de terminal) i el rellotge a les 11:15 (cian).
A baix hi va el quadre de text: tot el que importa és per sobre de y≈198.
Animació: el cursor i els dos punts del rellotge parpellegen; els comptadors fan pampallugues.
"""
import math

from PIL import Image
from pixels import nearest

from hd.pix import Light, Canvas, W, H, B4, hr, mix
from hd.rooms.comu import obox, outline, text, text_width, _diff
from hd.rooms.pis_cuina import outline_poly

LIGHT = Light(ambient=0.0, vignette=None, floor_fade=None)

BEZEL = [(4, 5, 8), (10, 12, 16), (18, 20, 26), (28, 30, 38), (40, 44, 54), (56, 60, 72)]
TERM = [(2, 14, 8), (6, 40, 20), (14, 90, 44), (30, 160, 80), (80, 230, 130), (190, 255, 210)]
CYANT = [(4, 20, 30), (10, 50, 70), (30, 110, 140), (70, 190, 220), (150, 240, 255), (230, 255, 255)]
GREEN_T = (90, 240, 140)
CYAN_T = (130, 236, 255)

PANELS = [(8, 32, 159, 111), (164, 32, 315, 111), (320, 32, 471, 111),
          (8, 116, 159, 195), (164, 116, 315, 195), (320, 116, 471, 195)]
LABEL_H = 10


# ─── Eines ─────────────────────────────────────────────────────────────────

def big_text(cv, s, x, y, col, k=2):
    """Text de la font petita, ampliat k vegades (píxels grossos)."""
    tmp = Canvas(w=text_width(s) + 2, h=10, transparent=True)
    text(tmp, s, 0, 3, [col], 0, lit=0, flat=col)
    img = nearest(tmp.img, (tmp.img.width * k, tmp.img.height * k))
    cv.img.alpha_composite(img, (x, y - 3 * k))
    return text_width(s) * k


def grad(cv, x0, y0, x1, y1, top, bot):
    """Degradat vertical entre dos colors, amb dithering."""
    for y in range(y0, y1 + 1):
        t = (y - y0) / max(1, y1 - y0)
        for x in range(x0, x1 + 1):
            tt = min(1, max(0, t + (B4[y & 3][x & 3] - 0.5) * 0.12))
            cv.flat(x, y, mix(top, bot, tt))


def fill(cv, x0, y0, x1, y1, col):
    for y in range(int(y0), int(y1) + 1):
        for x in range(int(x0), int(x1) + 1):
            cv.flat(x, y, col)


def fpoly(cv, pts, col):
    cv.poly(pts, [col], 0, lit=0)


def sil(cv, x, y, h, col=(8, 10, 14), tie=None, bun=False, skirt=False):
    """Una silueta de persona dreta (peus a (x, y), alçada h)."""
    hw = max(2, round(h * 0.13))
    head = max(2, round(h * 0.11))
    fill(cv, x - hw, y - round(h * 0.78), x + hw, y - round(h * 0.42), col)                  # el tors
    if skirt:
        fpoly(cv, [(x - hw, y - round(h * 0.42)), (x + hw, y - round(h * 0.42)), (x + hw + 2, y - round(h * 0.18)), (x - hw - 2, y - round(h * 0.18))], col)
        fill(cv, x - hw + 1, y - round(h * 0.18), x - 1, y, col)
        fill(cv, x + 1, y - round(h * 0.18), x + hw - 1, y, col)
    else:
        fill(cv, x - hw, y - round(h * 0.42), x - 1, y, col)
        fill(cv, x + 1, y - round(h * 0.42), x + hw, y, col)
    cv.disc(x, y - round(h * 0.78) - head, head, head, [col], 0, lit=0)
    if bun:
        cv.disc(x + 1, y - round(h * 0.78) - head * 2 - 1, head * 0.6, head * 0.6, [col], 0, lit=0)
    if tie:
        cv.vline(x, y - round(h * 0.76), y - round(h * 0.55), [tie], 0, lit=0)
        cv.flat(x - 1, y - round(h * 0.77), (220, 220, 226))
        cv.flat(x + 1, y - round(h * 0.77), (220, 220, 226))


def scanlines(cv, x0, y0, x1, y1):
    for y in range(y0, y1 + 1, 2):
        cv.tint(x0, y, x1, y, (0, 0, 0), 0.16)
    cv.tint(x0, y0, x1, y1, (160, 255, 230), lambda x, y: 0.07 if (x - x0) + (y - y0) < 26 else 0)   # el reflex


def label(cv, i, name, amount, blink=0):
    """La barra de sota de cada pantalla: el lloc en gris i la xifra en verd de terminal."""
    x0, y0, x1, y1 = PANELS[i]
    fill(cv, x0, y1 - LABEL_H, x1, y1, (4, 10, 8))
    cv.hline(x0, x1, y1 - LABEL_H, TERM, 2.0, lit=0)
    text(cv, name, x0 + 3, y1 - 7, None, 0, lit=0, flat=(150, 170, 160))
    col = GREEN_T if not (blink and (i + blink) % 3 == 0) else (40, 140, 80)
    w = text_width(amount)
    text(cv, amount, x1 - 3 - w, y1 - 7, None, 0, lit=0, flat=col)
    cv.glow(x1 - 3 - w // 2, y1 - 5, w // 2 + 4, (60, 220, 120), 0.18)


def tag(cv, cx, y, s):
    """Una etiqueta verda flotant (els 12 € de cadascú)."""
    w = text_width(s)
    fill(cv, cx - w // 2 - 3, y - 2, cx + w - w // 2 + 2, y + 6, (4, 20, 10))
    outline(cv, cx - w // 2 - 3, y - 2, cx + w - w // 2 + 2, y + 6, [(40, 170, 90)])
    text(cv, s, cx - w // 2, y, None, 0, lit=0, flat=GREEN_T)


# ─── Les sis vinyetes ──────────────────────────────────────────────────────

def monaco(cv, x0, y0, x1, y1):
    """Mònaco: la badia, els edificis pastel a la roca i un iot blanc; el milionari mira el mòbil."""
    sea = y0 + 38
    grad(cv, x0, y0, x1, sea, (90, 170, 230), (200, 226, 240))
    # la roca amb els edificis de colors
    for x in range(x0, x0 + 70):
        h = sea - 18 - int(10 * math.sin((x - x0) / 22)) - int(hr(x // 6, 2) * 4)
        for y in range(h, sea + 1):
            cv.flat(x, y, (120, 110, 90) if (x + y) % 5 else (100, 92, 76))
    for k in range(9):
        bx = x0 + 3 + k * 7
        by = sea - 22 - int(10 * math.sin((bx - x0) / 22)) + int(hr(k, 3) * 6)
        col = [(240, 220, 190), (236, 190, 160), (250, 240, 220), (230, 200, 120)][k % 4]
        fill(cv, bx, by, bx + 5, sea - 4, col)
        for wy in range(by + 2, sea - 5, 3):
            cv.flat(bx + 2, wy, (80, 90, 110))
        cv.hline(bx, bx + 5, by, [(170, 80, 60)], 0, lit=0)
    # el mar, amb ratlles de llum
    for y in range(sea + 1, y1 + 1):
        for x in range(x0, x1 + 1):
            c = mix((40, 110, 170), (20, 60, 120), (y - sea) / max(1, y1 - sea))
            if hr(x // 4, y, 6) > 0.86:
                c = (190, 230, 250)
            cv.flat(x, y, c)
    # el iot: buc blanc, dues cobertes, vidres fumats
    hx0, hx1, hy = x0 + 56, x1 - 10, y0 + 50
    fpoly(cv, [(hx0, hy - 6), (hx1 + 6, hy - 8), (hx1, hy + 2), (hx0 + 8, hy + 2)], (244, 246, 248))
    cv.hline(hx0 + 2, hx1 + 3, hy - 2, [(30, 50, 90)], 0, lit=0)
    fpoly(cv, [(hx0 + 14, hy - 6), (hx1 - 10, hy - 6), (hx1 - 16, hy - 13), (hx0 + 20, hy - 13)], (232, 236, 240))
    fill(cv, hx0 + 22, hy - 11, hx1 - 18, hy - 8, (40, 60, 80))
    fpoly(cv, [(hx0 + 26, hy - 13), (hx1 - 22, hy - 13), (hx1 - 28, hy - 18), (hx0 + 32, hy - 18)], (226, 230, 236))
    fill(cv, hx0 + 34, hy - 17, hx1 - 30, hy - 15, (40, 60, 80))
    cv.vline(hx1 - 30, hy - 26, hy - 18, [(200, 200, 210)], 0, lit=0)          # l'antena
    for x in range(hx0 + 6, hx1 + 2):                                           # el reflex al mar
        if (x // 2) % 2:
            cv.flat(x, hy + 3 + (x % 3), (150, 190, 220))
    # el milionari a la coberta de popa, mirant el mòbil (que brilla)
    mx = hx0 + 26
    sil(cv, mx, hy - 6, 18, col=(14, 14, 20))
    cv.flat(mx + 2, hy - 19, (170, 255, 210))
    cv.glow(mx + 2, hy - 19, 5, (120, 255, 180), 0.6)
    tag(cv, mx + 2, hy - 34, '12,00 €')


def nova_york(cv, x0, y0, x1, y1):
    """Nova York a les cinc del matí: gratacels contra l'alba i la gràfica del fons que s'enfonsa."""
    grad(cv, x0, y0, x1, y1, (50, 40, 90), (240, 150, 110))
    rng = 0
    x = x0
    while x < x1:
        w = 8 + int(hr(rng, 1) * 12)
        h = 24 + int(hr(rng, 2) * 36)
        if rng == 4:
            h = 62                                                              # la torre del fons
        col = mix((24, 26, 44), (40, 40, 64), hr(rng, 3))
        fill(cv, x, y1 - h, min(x1, x + w), y1, col)
        if rng == 4:                                                            # l'agulla i el rètol daurat
            cv.vline(x + w // 2, y1 - h - 8, y1 - h, [(120, 120, 150)], 0, lit=0)
            text(cv, 'FUND', x + 1, y1 - h + 3, None, 0, lit=0, flat=(230, 190, 90))
        for wy in range(y1 - h + 10, y1 - 2, 3):
            for wx in range(x + 1, min(x1, x + w) - 1, 2):
                if hr(wx, wy, 5) > 0.7:
                    cv.flat(wx, wy, (250, 210, 140))
        x += w + 1
        rng += 1
    # la gràfica: verda que puja i, de cop, vermella fins a terra
    pts = [(x0 + 6, y0 + 40), (x0 + 30, y0 + 34), (x0 + 50, y0 + 28), (x0 + 70, y0 + 22), (x0 + 90, y0 + 14), (x0 + 96, y0 + 12)]
    for a, b in zip(pts, pts[1:]):
        for dy in (0, 1):
            cv.line(a[0], a[1] + dy, b[0], b[1] + dy, [(90, 240, 140)], 0, lit=0)
    for dy in (0, 1):
        cv.line(x0 + 96, y0 + 12 + dy, x0 + 106, y1 - 4 + dy, [(250, 60, 60)], 0, lit=0)
        cv.line(x0 + 97, y0 + 12 + dy, x0 + 107, y1 - 4 + dy, [(250, 60, 60)], 0, lit=0)
    cv.glow(x0 + 104, y0 + 40, 12, (255, 60, 60), 0.3)
    # el cartell: el fons, amb el sou d'un becari
    tag(cv, x0 + 122, y0 + 8, 'SOU DE BECARI')


def ginebra(cv, x0, y0, x1, y1):
    """Ginebra: un despatx amb vistes al llac; l'home de la corbata i la secretària, empatats."""
    fill(cv, x0, y0, x1, y1, (200, 196, 186))                                  # la paret del despatx
    wx0, wy0, wx1, wy1 = x0 + 8, y0 + 4, x1 - 8, y0 + 46                        # el finestral
    grad(cv, wx0, wy0, wx1, wy0 + 20, (120, 170, 220), (200, 220, 236))
    for x in range(wx0, wx1 + 1):                                               # les muntanyes
        h = wy0 + 16 + int(4 * math.sin(x / 14)) + int(hr(x // 5, 9) * 2)
        for y in range(h, wy0 + 24):
            cv.flat(x, y, (130, 150, 170) if y > h + 1 else (236, 240, 246))
    grad(cv, wx0, wy0 + 24, wx1, wy1, (60, 120, 170), (40, 90, 140))           # el llac
    jx = wx0 + 26                                                               # el raig d'aigua
    for y in range(wy0 + 6, wy0 + 25):
        wd = (y - wy0 - 6) // 6
        for x in range(jx - wd, jx + wd + 1):
            cv.flat(x, y, (240, 246, 255) if hr(x, y) > 0.3 else (200, 220, 240))
    for mx in range(wx0, wx1 + 1, 28):                                          # els muntants
        cv.vline(mx, wy0, wy1, [(70, 70, 76)], 0, lit=0)
    outline(cv, wx0, wy0, wx1, wy1, [(60, 60, 66)])
    # el terra i la taula
    fill(cv, x0, y0 + 47, x1, y1, (90, 70, 56))
    fill(cv, x0 + 66, y0 + 46, x1 - 10, y0 + 49, (60, 36, 26))
    # l'home de la corbata i la secretària (amb carpeta), de peu, un al costat de l'altre
    sil(cv, x0 + 46, y1, 34, col=(16, 18, 30), tie=(200, 40, 50))
    sil(cv, x0 + 106, y1, 30, col=(30, 22, 30), bun=True, skirt=True)
    fill(cv, x0 + 110, y1 - 20, x0 + 114, y1 - 14, (230, 220, 190))
    tag(cv, x0 + 46, y0 + 6, '12,00 €')
    tag(cv, x0 + 106, y0 + 10, '12,00 €')
    for yy in (y0 + 8, y0 + 9, y0 + 12, y0 + 13):                              # el signe igual
        cv.hline(x0 + 72, x0 + 80, yy, [GREEN_T], 0, lit=0)


def propina(cv, x0, y0, x1, y1):
    """El bar La Propina: en Tomàs abaixa la persiana metàl·lica amb el ganxo, a mig camí."""
    grad(cv, x0, y0, x1, y0 + 14, (150, 180, 210), (200, 210, 220))           # una mica de cel
    fill(cv, x0, y0 + 10, x1, y1, (150, 120, 96))                              # la façana d'arrebossat
    for k in range(40):
        cv.flat(x0 + int(hr(k, 1) * (x1 - x0)), y0 + 12 + int(hr(k, 2) * 50), (130, 104, 84))
    # el rètol
    fill(cv, x0 + 20, y0 + 14, x1 - 20, y0 + 24, (40, 20, 18))
    s = 'LA PROPINA'
    text(cv, s, (x0 + x1) // 2 - text_width(s) // 2, y0 + 17, None, 0, lit=0, flat=(255, 190, 90))
    cv.glow((x0 + x1) // 2, y0 + 19, 30, (255, 170, 80), 0.18)
    # l'aparador: a baix encara es veu el bar per dins, a dalt ja tapa la persiana
    sx0, sx1, sy0, sy1 = x0 + 14, x1 - 40, y0 + 28, y1
    fill(cv, sx0, sy0, sx1, sy1, (60, 40, 30))
    for k in range(5):                                                          # ampolles i taburets
        cv.rect(sx0 + 6 + k * 14, sy0 + 26, sx0 + 8 + k * 14, sy0 + 32, [(120, 160, 90)], 0, lit=0)
    fill(cv, sx0 + 2, sy0 + 34, sx1 - 2, sy0 + 36, (110, 70, 40))
    cv.glow((sx0 + sx1) // 2, sy0 + 30, 26, (255, 190, 110), 0.25)
    half = sy0 + 22
    for y in range(sy0, half + 1):                                              # la persiana ondulada
        c = (170, 172, 176) if y % 3 else (110, 112, 118)
        for x in range(sx0, sx1 + 1):
            cv.flat(x, y, c)
    fill(cv, sx0, half, sx1, half + 1, (60, 60, 66))
    for gx in (sx0 + 12, sx1 - 14):                                             # els grafits de sempre
        cv.line(gx, sy0 + 6, gx + 8, sy0 + 12, [(220, 60, 120)], 0, lit=0)
    # la porta, a la dreta
    fill(cv, x1 - 34, y0 + 30, x1 - 16, y1, (80, 50, 34))
    # en Tomàs, d'esquena, estirant el ganxo
    tx = sx1 - 16
    sil(cv, tx, y1, 30, col=(24, 20, 22))
    cv.line(tx + 3, y1 - 26, tx + 1, half + 1, [(40, 40, 46)], 0, lit=0)
    fill(cv, tx - 4, y1 - 25, tx - 3, y1 - 17, (240, 236, 226))               # el davantal, de reüll
    tag(cv, x0 + 30, y0 + 2, 'TANCAT')


def caixer(cv, x0, y0, x1, y1):
    """Un caixer automàtic al carrer: l'àvia amb bastó davant la pantalla i un cambrer que espera el sou."""
    fill(cv, x0, y0, x1, y1, (110, 104, 96))
    for y in range(y0, y1, 8):                                                  # les filades de pedra
        cv.hline(x0, x1, y, [(90, 84, 78)], 0, lit=0)
    # el caixer encastat
    ax0, ay0, ax1, ay1 = x0 + 40, y0 + 6, x0 + 92, y1 - 2
    fill(cv, ax0, ay0, ax1, ay1, (40, 44, 52))
    fill(cv, ax0, ay0, ax1, ay0 + 6, (30, 60, 120))
    text(cv, 'CAIXER', ax0 + 14, ay0 + 1, None, 0, lit=0, flat=(240, 240, 250))
    fill(cv, ax0 + 8, ay0 + 10, ax1 - 8, ay0 + 30, (6, 30, 16))               # la pantalla, en verd
    text(cv, 'SALDO', ax0 + 10, ay0 + 13, None, 0, lit=0, flat=(70, 200, 120))
    big_text(cv, '12€', ax0 + 12, ay0 + 20, GREEN_T, 2)
    cv.glow((ax0 + ax1) // 2, ay0 + 20, 26, (80, 255, 150), 0.25)
    fill(cv, ax0 + 10, ay0 + 34, ax1 - 10, ay0 + 44, (70, 76, 86))            # el teclat
    for r in range(3):
        for c in range(4):
            cv.flat(ax0 + 13 + c * 8, ay0 + 36 + r * 3, (180, 184, 190))
    fill(cv, ax0 + 12, ay0 + 48, ax1 - 12, ay0 + 49, (10, 10, 14))            # la boca dels bitllets
    # l'àvia: monyo, bossa i bastó
    gx = ax0 + 22
    sil(cv, gx, y1, 26, col=(150, 120, 140), bun=True, skirt=True)
    cv.disc(gx, y1 - 26, 2.2, 2.2, [(220, 220, 226)], 0, lit=0)                   # els cabells blancs
    cv.line(gx + 6, y1 - 12, gx + 8, y1, [(70, 50, 30)], 0, lit=0)
    fill(cv, gx - 7, y1 - 14, gx - 4, y1 - 10, (90, 30, 40))
    # el cambrer: armilla negra, camisa blanca, safata sota el braç, mirant el rellotge
    wx = x1 - 22
    sil(cv, wx, y1, 32, col=(16, 16, 20))
    fill(cv, wx - 1, y1 - 24, wx + 1, y1 - 16, (236, 236, 236))
    cv.disc(wx + 7, y1 - 18, 5, 1.4, [(180, 184, 190)], 0, lit=0)
    cv.flat(wx - 5, y1 - 15, (240, 220, 120))
    tag(cv, wx - 8, y0 + 5, 'SOU: 12 €')


# Continents, en coordenades del mapa (0..1): (cx, cy, rx, ry)
LAND = [(0.20, 0.30, 0.12, 0.15), (0.28, 0.16, 0.08, 0.07), (0.30, 0.66, 0.06, 0.16), (0.27, 0.48, 0.03, 0.05),
        (0.50, 0.24, 0.05, 0.07), (0.52, 0.56, 0.08, 0.16), (0.56, 0.42, 0.06, 0.05), (0.70, 0.27, 0.17, 0.12),
        (0.66, 0.46, 0.03, 0.07), (0.76, 0.48, 0.04, 0.05), (0.84, 0.72, 0.06, 0.06), (0.36, 0.10, 0.04, 0.04)]
CITIES = [(0.25, 0.32), (0.18, 0.28), (0.31, 0.66), (0.50, 0.24), (0.47, 0.28), (0.53, 0.56), (0.70, 0.30),
          (0.78, 0.34), (0.66, 0.46), (0.84, 0.72), (0.58, 0.40), (0.30, 0.50), (0.75, 0.50), (0.13, 0.26)]


def mapa(cv, x0, y0, x1, y1):
    """El mapa del món de punts verds: de cada ciutat surt una línia cap al compte pont, al mig."""
    fill(cv, x0, y0, x1, y1, (2, 10, 12))
    mw, mh = x1 - x0, y1 - y0
    for y in range(y0 + 1, y1, 2):
        for x in range(x0 + 1, x1, 2):
            u, v = (x - x0) / mw, (y - y0) / mh
            land = any(((u - cx) / rx) ** 2 + ((v - cy) / ry) ** 2 < 1 for cx, cy, rx, ry in LAND)
            cv.flat(x, y, (50, 170, 96) if land else (6, 22, 24))
    zx, zy = x0 + mw // 2, y0 + mh // 2 + 4
    for cx, cy in CITIES:
        px, py = x0 + round(cx * mw), y0 + round(cy * mh)
        n = max(abs(zx - px), abs(zy - py), 1)
        for k in range(n + 1):                                                  # línia de punts cap al centre
            if k % 2 == 0:
                cv.flat(round(px + (zx - px) * k / n), round(py + (zy - py) * k / n), (70, 200, 230))
        cv.flat(px, py, (200, 255, 255))
    # el compte pont: un cercle que ho xucla tot
    cv.disc(zx, zy, 7, 7, CYANT, lambda nx, ny: 2.0 + (1 - math.hypot(nx, ny)) * 3, lit=0)
    cv.ring(zx, zy, 9, CYANT, 4.0, lit=0, step=10)
    big_text(cv, '0', zx - 2, zy - 4, (4, 20, 30), 1)
    cv.glow(zx, zy, 22, (100, 230, 255), 0.35)
    s = 'COMPTE PONT'
    fill(cv, zx - text_width(s) // 2 - 2, zy + 11, zx + text_width(s) // 2 + 2, zy + 17, (2, 10, 12))
    text(cv, s, zx - text_width(s) // 2, zy + 12, None, 0, lit=0, flat=CYAN_T)


# ─── La paret de pantalles ─────────────────────────────────────────────────

def backdrop(cv):
    """El fons: una sala fosca amb la reixeta tènue d'un terminal i la claror verda que cau cap avall."""
    for y in range(H):
        for x in range(W):
            grid = (x % 12 == 0 or y % 12 == 0)
            cv.put(x, y, BEZEL, 1.0 + (0.6 if grid else 0) - max(0, (y - 200) / 60), lit=0)
    cv.tint(0, 196, W - 1, H - 1, (20, 120, 70), lambda x, y: 0.12 * max(0, 1 - (y - 196) / 50))


def header(cv, cursor=True, colon=True):
    """La capçalera: «ROBIN HOOD 2.0» en verd de terminal, el pagament i el rellotge a les 11:15."""
    fill(cv, 4, 3, W - 5, 27, (2, 8, 6))
    outline(cv, 4, 3, W - 5, 27, [(30, 110, 60)])
    w = big_text(cv, 'ROBIN HOOD 2.0', 10, 7, GREEN_T, 2)
    if cursor:
        fill(cv, 10 + w + 4, 7, 10 + w + 9, 16, GREEN_T)
    cv.glow(10 + w // 2, 12, 80, (60, 255, 140), 0.12)
    text(cv, 'TOTS ELS COMPTES - COMPTE PONT', 10, 20, None, 0, lit=0, flat=(70, 190, 110))
    s = 'PAGAMENT 1: 12,00 € PER PERSONA'
    big_x = 196
    text(cv, s, big_x, 9, None, 0, lit=0, flat=GREEN_T)
    # una barra de progrés plena
    fill(cv, big_x, 17, big_x + text_width(s), 21, (6, 30, 16))
    fill(cv, big_x + 1, 18, big_x + text_width(s) - 1, 20, (60, 210, 120))
    # el rellotge
    fill(cv, 392, 5, W - 8, 25, (2, 12, 18))
    outline(cv, 392, 5, W - 8, 25, [(30, 110, 140)])
    clock = '11:15' if colon else '11 15'
    cw = text_width(clock) * 3
    big_text(cv, clock, 392 + (W - 8 - 392 - cw) // 2 + 1, 8, CYAN_T, 3)
    cv.glow(432, 15, 34, (100, 220, 255), 0.2)


VIEWS = [(monaco, 'MÒNACO', '12,00 €'), (nova_york, 'NOVA YORK', '12,00 €'), (ginebra, 'GINEBRA', '12,00 €'),
         (propina, 'BAR LA PROPINA', '12,00 €'), (caixer, 'CAIXER', '12,00 €'), (mapa, 'EL MÓN', '8.200.000.000 X 12 €')]


def screens(cv, blink=0):
    for i, (fn, name, amount) in enumerate(VIEWS):
        x0, y0, x1, y1 = PANELS[i]
        obox(cv, x0 - 3, y0 - 3, x1 + 3, y1 + 3, BEZEL, 3.0, lit=0)
        fn(cv, x0, y0, x1, y1 - LABEL_H - 1)
        scanlines(cv, x0, y0, x1, y1 - LABEL_H - 1)
        label(cv, i, name, amount, blink)
        outline(cv, x0 - 1, y0 - 1, x1 + 1, y1 + 1, [(0, 0, 0)])
        cv.flat(x1 - 3, y0 + 2, (240, 40, 36))                                  # el punt vermell de directe
    # la claror de les pantalles cap avall
    cv.tint(0, 198, W - 1, 214, (40, 200, 160), lambda x, y: 0.12 * (1 - (y - 198) / 16))


def bg(cv, t=0):
    backdrop(cv)
    header(cv, cursor=t % 2 == 0, colon=t % 4 < 2)
    screens(cv, blink=t)


PROPS = {}


def _frames():
    base = Canvas(light=LIGHT)
    bg(base)
    frames = []
    for t in range(4):
        cv = Canvas(light=LIGHT)
        bg(cv, t)
        frames.append(_diff(cv.img, base.img))
    return frames


ANIMS = {'pantalles': {'frames': _frames, 'frameDuration': 400}}
