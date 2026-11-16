"""
El muntatge del virus a 640×360 (cinemàtica, Acte 3; vegeu hd/rooms/muntatge.py, el de 480×270): ROBIN HOOD 2.0
buida tots els comptes del món al «compte zero» i paga la primera ronda, 12 € per persona. Una sola imatge per
a totes les frases: una paret de sis pantalles, com les de la sala de seguretat, cadascuna amb una vinyeta i el
comptador en verd de terminal:
  - Mònaco: la roca amb els edificis pastel, un iot blanc a la badia i un milionari a la coberta mirant el mòbil;
  - Nova York: gratacels a l'alba (allà són les cinc i quart) i la gràfica del fons que cau en picat;
  - Ginebra: un despatx amb el llac i el raig d'aigua; l'home de la corbata i la secretària, 12 € cadascun;
  - el bar La Propina: en Tomàs abaixa la persiana amb el ganxo;
  - un caixer automàtic: una àvia amb bastó davant de la pantalla i un cambrer que espera el sou;
  - el mapa del món, de punts, amb totes les línies que van a parar al compte zero.
A dalt, la capçalera «ROBIN HOOD 2.0» (verd de terminal) i el rellotge a les 11:15 (cian).
A baix hi va el quadre de text: tot el que importa és per sobre de y≈264.
Animació `pantalles` (8 fotogrames): el cursor i els dos punts del rellotge parpellegen; els comptadors fan
pampallugues; els diners corren per les línies del mapa cap al compte zero.
"""
import hd640  # noqa: F401  (abans que cap hd.rooms: posa la llibreria a 640×360)

import math

from PIL import Image
from pixels import nearest

from hd.pix import Light, Canvas, W, H, B4, hr, mix
from hd.rooms.comu import obox, outline, text, text_width, _diff
from hd.rooms.muntatge import BEZEL, TERM, CYANT, GREEN_T, CYAN_T, LAND, CITIES

LIGHT = Light(ambient=0.0, vignette=None, floor_fade=None)

PANELS = [(11, 43, 212, 148), (219, 43, 420, 148), (427, 43, 628, 148),
          (11, 155, 212, 260), (219, 155, 420, 260), (427, 155, 628, 260)]
LABEL_H = 13
NF = 8                 # fotogrames de l'animació


# ─── Eines ─────────────────────────────────────────────────────────────────

def big_text(cv, s, x, y, col, k=2, bevel=True):
    """Text de la font petita, ampliat k vegades (píxels grossos); `bevel`: cada píxel gros, amb la vora de
    dalt més clara i la de sota més fosca (com els fòsfors d'un terminal)."""
    tmp = Canvas(w=text_width(s) + 2, h=10, transparent=True)
    text(tmp, s, 0, 3, [col], 0, lit=0, flat=col)
    img = nearest(tmp.img, (tmp.img.width * k, tmp.img.height * k))
    if bevel and k >= 3:
        hi, lo = mix(col, (255, 255, 255), 0.35), mix(col, (0, 0, 0), 0.3)
        px = img.load()
        for yy in range(img.height):
            for xx in range(img.width):
                if px[xx, yy][3] and yy % k == 0:
                    px[xx, yy] = hi + (255,)
                elif px[xx, yy][3] and yy % k == k - 1:
                    px[xx, yy] = lo + (255,)
    cv.img.alpha_composite(img, (x, y - 3 * k))
    return text_width(s) * k


def grad(cv, x0, y0, x1, y1, top, bot):
    """Degradat vertical entre dos colors, amb dithering."""
    for y in range(y0, y1 + 1):
        t = (y - y0) / max(1, y1 - y0)
        for x in range(x0, x1 + 1):
            tt = min(1, max(0, t + (B4[y & 3][x & 3] - 0.5) * 0.09))
            cv.flat(x, y, mix(top, bot, tt))


def fill(cv, x0, y0, x1, y1, col):
    for y in range(int(y0), int(y1) + 1):
        for x in range(int(x0), int(x1) + 1):
            cv.flat(x, y, col)


def fpoly(cv, pts, col):
    cv.poly(pts, [col], 0, lit=0)


def sil(cv, x, y, h, col=(8, 10, 14), tie=None, bun=False, skirt=False):
    """Una silueta de persona dreta (peus a (x, y), alçada h): espatlles arrodonides, coll, braços i peus."""
    hw = max(2, round(h * 0.13))
    head = max(2, round(h * 0.11))
    top, hip = y - round(h * 0.78), y - round(h * 0.42)
    fill(cv, x - hw, top, x + hw, hip, col)                                    # el tors
    fill(cv, x - hw - 1, top + 2, x - hw - 1, hip + 2, col)                    # els braços, una mica separats
    fill(cv, x + hw + 1, top + 2, x + hw + 1, hip + 2, col)
    fill(cv, x - 1, top - 2, x + 1, top, col)                                  # el coll
    if skirt:
        fpoly(cv, [(x - hw, hip), (x + hw, hip), (x + hw + 3, y - round(h * 0.18)), (x - hw - 3, y - round(h * 0.18))], col)
        fill(cv, x - hw + 1, y - round(h * 0.18), x - 2, y, col)
        fill(cv, x + 2, y - round(h * 0.18), x + hw - 1, y, col)
    else:
        fill(cv, x - hw, hip, x - 1, y, col)
        fill(cv, x + 1, hip, x + hw, y, col)
    fill(cv, x - hw - 1, y, x - 1, y, col)                                     # les sabates
    fill(cv, x + 1, y, x + hw + 1, y, col)
    cv.disc(x, top - head - 1, head, head + 0.4, [col], 0, lit=0)
    if bun:
        cv.disc(x + 1, top - head * 2 - 2, head * 0.6, head * 0.6, [col], 0, lit=0)
    if tie:
        fill(cv, x - 2, top, x + 2, top + 1, (220, 220, 226))                  # el coll de la camisa
        cv.vline(x, top + 1, y - round(h * 0.55), [tie], 0, lit=0)
        cv.flat(x - 1, top + 2, tie)
        cv.flat(x + 1, top + 2, tie)


def rim(cv, x, y, h, col):
    """El contorn de llum d'una silueta (la claror de la finestra, a la dreta)."""
    hw = max(2, round(h * 0.13))
    cv.vline(x + hw + 1, y - round(h * 0.78) + 2, y - round(h * 0.42) + 2, [col], 0, lit=0)


def scanlines(cv, x0, y0, x1, y1):
    for y in range(y0, y1 + 1, 2):
        cv.tint(x0, y, x1, y, (0, 0, 0), 0.14)
    cv.tint(x0, y0, x1, y1, (160, 255, 230), lambda x, y: 0.07 if (x - x0) + (y - y0) < 35 else 0)   # el reflex
    cv.tint(x0, y0, x1, y1, (0, 0, 0), lambda x, y: 0.16 * max(0, 1 - min(x - x0, x1 - x, y - y0, y1 - y) / 6))


def label(cv, i, name, amount, blink=0):
    """La barra de sota de cada pantalla: el lloc en gris i la xifra en verd de terminal."""
    x0, y0, x1, y1 = PANELS[i]
    fill(cv, x0, y1 - LABEL_H, x1, y1, (4, 10, 8))
    cv.hline(x0, x1, y1 - LABEL_H, TERM, 2.0, lit=0)
    text(cv, name, x0 + 4, y1 - 9, None, 0, lit=0, flat=(150, 170, 160))
    col = GREEN_T if not (blink and (i + blink) % 3 == 0) else (40, 140, 80)
    w = text_width(amount)
    text(cv, amount, x1 - 4 - w, y1 - 9, None, 0, lit=0, flat=col)
    cv.glow(x1 - 4 - w // 2, y1 - 7, w // 2 + 5, (60, 220, 120), 0.18)


def tag(cv, cx, y, s):
    """Una etiqueta verda flotant (els 12 € de cadascú), amb el pal que la penja."""
    w = text_width(s)
    fill(cv, cx - w // 2 - 4, y - 3, cx + w - w // 2 + 3, y + 7, (4, 20, 10))
    outline(cv, cx - w // 2 - 4, y - 3, cx + w - w // 2 + 3, y + 7, [(40, 170, 90)])
    cv.hline(cx - w // 2 - 3, cx + w - w // 2 + 2, y - 2, [(20, 90, 50)], 0, lit=0)
    text(cv, s, cx - w // 2, y, None, 0, lit=0, flat=GREEN_T)


# ─── Les sis vinyetes ──────────────────────────────────────────────────────

def monaco(cv, x0, y0, x1, y1):
    """Mònaco: la badia, els edificis pastel a la roca i un iot blanc; el milionari mira el mòbil."""
    sea = y0 + 51
    grad(cv, x0, y0, x1, sea, (90, 170, 230), (200, 226, 240))
    for k in range(3):                                                          # uns núvols prims
        cx, cy = x0 + 110 + k * 34, y0 + 8 + k * 5
        for i in range(-10, 11):
            cv.flat(cx + i, cy + (1 if abs(i) > 6 else 0), (236, 244, 250) if abs(i) < 8 else (214, 232, 246))
    # la roca amb els edificis de colors
    for x in range(x0, x0 + 93):
        h = sea - 24 - int(13 * math.sin((x - x0) / 29)) - int(hr(x // 4, 2) * 5)
        for y in range(h, sea + 1):
            c = (120, 110, 90) if (x + y) % 5 else (100, 92, 76)
            if hr(x // 3, y // 2, 7) > 0.8:
                c = (140, 128, 104)
            cv.flat(x, y, c)
        cv.flat(x, h, (150, 140, 112))
    for k in range(10):
        bx = x0 + 3 + k * 9
        by = sea - 29 - int(13 * math.sin((bx - x0) / 29)) + int(hr(k, 3) * 8)
        col = [(240, 220, 190), (236, 190, 160), (250, 240, 220), (230, 200, 120)][k % 4]
        fill(cv, bx, by, bx + 7, sea - 5, col)
        cv.vline(bx + 7, by, sea - 5, [mix(col, (60, 50, 50), 0.25)], 0, lit=0)   # la cara a l'ombra
        for wy in range(by + 3, sea - 6, 4):
            cv.flat(bx + 2, wy, (80, 90, 110))
            cv.flat(bx + 5, wy, (80, 90, 110))
            cv.hline(bx + 1, bx + 6, wy + 1, [mix(col, (255, 255, 255), 0.4)], 0, lit=0)   # els balcons
        cv.hline(bx, bx + 7, by, [(170, 80, 60)], 0, lit=0)
        cv.hline(bx + 1, bx + 6, by - 1, [(150, 70, 52)], 0, lit=0)
    fill(cv, x0, sea - 3, x0 + 100, sea, (200, 196, 180))                       # el moll
    cv.hline(x0, x0 + 100, sea - 3, [(230, 226, 214)], 0, lit=0)
    # el mar, amb ratlles de llum
    for y in range(sea + 1, y1 + 1):
        for x in range(x0, x1 + 1):
            c = mix((40, 110, 170), (20, 60, 120), (y - sea) / max(1, y1 - sea))
            if hr(x // 5, y, 6) > 0.86:
                c = (190, 230, 250)
            elif hr(x // 3, y, 8) > 0.9:
                c = mix(c, (120, 180, 220), 0.5)
            cv.flat(x, y, c)
    # el iot: buc blanc, dues cobertes, vidres fumats, ulls de bou
    hx0, hx1, hy = x0 + 75, x1 - 13, y0 + 67
    fpoly(cv, [(hx0, hy - 8), (hx1 + 8, hy - 11), (hx1, hy + 3), (hx0 + 11, hy + 3)], (244, 246, 248))
    cv.line(hx0 + 11, hy + 3, hx1, hy + 3, [(170, 180, 190)], 0, lit=0)
    cv.hline(hx0 + 3, hx1 + 4, hy - 3, [(30, 50, 90)], 0, lit=0)
    for px in range(hx0 + 20, hx1 - 4, 9):
        cv.flat(px, hy - 1, (60, 80, 110))
    fpoly(cv, [(hx0 + 19, hy - 8), (hx1 - 13, hy - 8), (hx1 - 21, hy - 17), (hx0 + 27, hy - 17)], (232, 236, 240))
    fill(cv, hx0 + 29, hy - 15, hx1 - 24, hy - 11, (40, 60, 80))
    cv.hline(hx0 + 30, hx1 - 25, hy - 15, [(110, 140, 170)], 0, lit=0)
    fpoly(cv, [(hx0 + 35, hy - 17), (hx1 - 29, hy - 17), (hx1 - 37, hy - 24), (hx0 + 43, hy - 24)], (226, 230, 236))
    fill(cv, hx0 + 45, hy - 23, hx1 - 40, hy - 20, (40, 60, 80))
    cv.vline(hx1 - 40, hy - 35, hy - 24, [(200, 200, 210)], 0, lit=0)          # l'antena, amb el radar
    cv.hline(hx1 - 43, hx1 - 37, hy - 31, [(200, 200, 210)], 0, lit=0)
    cv.flat(hx1 - 40, hy - 36, (255, 80, 60))
    for x in range(hx0 + 8, hx1 + 3):                                           # el reflex al mar
        if (x // 2) % 2:
            cv.flat(x, hy + 4 + (x % 3), (150, 190, 220))
    # el milionari a la coberta de popa, mirant el mòbil (que brilla)
    mx = hx0 + 35
    sil(cv, mx, hy - 8, 24, col=(14, 14, 20))
    cv.flat(mx + 3, hy - 25, (170, 255, 210))
    cv.flat(mx + 3, hy - 24, (120, 220, 170))
    cv.glow(mx + 3, hy - 25, 7, (120, 255, 180), 0.6)
    tag(cv, mx + 3, hy - 45, '12,00 €')


def nova_york(cv, x0, y0, x1, y1):
    """Nova York a les cinc del matí: gratacels contra l'alba i la gràfica del fons que s'enfonsa."""
    grad(cv, x0, y0, x1, y1, (50, 40, 90), (240, 150, 110))
    for k in range(14):                                                         # les darreres estrelles
        cv.flat(x0 + int(hr(k, 11) * (x1 - x0)), y0 + int(hr(k, 12) * 22), (200, 196, 230))
    rng = 0
    x = x0
    while x < x1:
        w = 11 + int(hr(rng, 1) * 16)
        h = 32 + int(hr(rng, 2) * 48)
        if rng == 4:
            h, w = 83, 22                                                       # la torre del fons
        col = mix((24, 26, 44), (40, 40, 64), hr(rng, 3))
        xe = min(x1, x + w)
        fill(cv, x, y1 - h, xe, y1, col)
        cv.vline(x, y1 - h, y1, [mix(col, (240, 150, 110), 0.25)], 0, lit=0)   # la cara que mira l'alba
        if hr(rng, 4) > 0.5 and rng != 4:                                       # els terrats: dipòsits d'aigua
            cv.rect(x + 3, y1 - h - 3, x + 6, y1 - h - 1, [mix(col, (0, 0, 0), 0.2)], 0, lit=0)
        if rng == 4:                                                            # l'agulla i el rètol daurat
            cv.vline(x + w // 2, max(y0, y1 - h - 11), y1 - h, [(120, 120, 150)], 0, lit=0)
            cv.flat(x + w // 2, max(y0, y1 - h - 12), (255, 80, 60))
            cv.rect(x + 2, y1 - h - 3, x + w - 2, y1 - h - 1, [col], 0, lit=0)
            text(cv, 'FUND', x + 3, y1 - h + 4, None, 0, lit=0, flat=(230, 190, 90))
        for wy in range(y1 - h + 13, y1 - 3, 4):
            for wx in range(x + 2, xe - 1, 3):
                if hr(wx, wy, 5) > 0.7:
                    cv.flat(wx, wy, (250, 210, 140))
                    cv.flat(wx, wy + 1, (200, 160, 110))
        x += w + 1
        rng += 1
    # la gràfica: la reixeta, la verda que puja i, de cop, la vermella fins a terra
    for gy in range(y0 + 12, y1 - 4, 12):
        for gx in range(x0 + 6, x0 + 150, 3):
            cv.tint(gx, gy, gx, gy, (90, 240, 140), 0.25)
    pts = [(x0 + 8, y0 + 53), (x0 + 40, y0 + 45), (x0 + 67, y0 + 37), (x0 + 93, y0 + 29), (x0 + 120, y0 + 19), (x0 + 128, y0 + 16)]
    for a, b in zip(pts, pts[1:]):
        for dy in (0, 1):
            cv.line(a[0], a[1] + dy, b[0], b[1] + dy, [(90, 240, 140)], 0, lit=0)
        cv.flat(a[0], a[1] - 1, (200, 255, 220))
    for dx in (0, 1, 2):
        cv.line(x0 + 128 + dx, y0 + 16, x0 + 141 + dx, y1 - 5, [(250, 60, 60) if dx < 2 else (170, 30, 30)], 0, lit=0)
    cv.glow(x0 + 139, y0 + 53, 16, (255, 60, 60), 0.3)
    # el cartell: el fons, amb el sou d'un becari
    tag(cv, x0 + 163, y0 + 11, 'SOU DE BECARI')


def ginebra(cv, x0, y0, x1, y1):
    """Ginebra: un despatx amb vistes al llac; l'home de la corbata i la secretària, empatats."""
    fill(cv, x0, y0, x1, y1, (200, 196, 186))                                  # la paret del despatx
    for y in range(y0, y1 + 1, 2):
        for x in range(x0, x1 + 1):
            if hr(x, y, 4) > 0.85:
                cv.flat(x, y, (190, 186, 176))
    wx0, wy0, wx1, wy1 = x0 + 11, y0 + 5, x1 - 11, y0 + 61                      # el finestral
    grad(cv, wx0, wy0, wx1, wy0 + 27, (120, 170, 220), (200, 220, 236))
    for x in range(wx0, wx1 + 1):                                               # les muntanyes, nevades
        h = wy0 + 21 + int(5 * math.sin(x / 19)) + int(hr(x // 6, 9) * 3)
        for y in range(h, wy0 + 32):
            cv.flat(x, y, (130, 150, 170) if y > h + 1 else (236, 240, 246))
        if hr(x, 13) > 0.6 and h + 2 < wy0 + 32:
            cv.flat(x, h + 2, (200, 210, 224))
    grad(cv, wx0, wy0 + 32, wx1, wy1, (60, 120, 170), (40, 90, 140))           # el llac
    for x in range(wx0, wx1 + 1, 2):                                            # l'altra riba, amb la ciutat
        cv.flat(x, wy0 + 32, (90, 100, 110))
        if hr(x, 21) > 0.6:
            cv.flat(x, wy0 + 31, (220, 210, 190))
    for x in range(wx0, wx1 + 1):
        for y in range(wy0 + 34, wy1 + 1, 3):
            if hr(x // 4, y, 22) > 0.88:
                cv.flat(x, y, (120, 170, 210))
    jx = wx0 + 35                                                               # el raig d'aigua
    for y in range(wy0 + 8, wy0 + 33):
        wd = (y - wy0 - 8) // 8
        for x in range(jx - wd, jx + wd + 1):
            cv.flat(x, y, (240, 246, 255) if hr(x, y) > 0.3 else (200, 220, 240))
    for k in range(5):                                                          # la polsina de dalt
        cv.flat(jx - 2 + int(hr(k, 31) * 5), wy0 + 6 + int(hr(k, 32) * 3), (226, 236, 250))
    for mx in range(wx0, wx1 + 1, 37):                                          # els muntants
        cv.vline(mx, wy0, wy1, [(70, 70, 76)], 0, lit=0)
        cv.vline(mx + 1, wy0, wy1, [(110, 110, 116)], 0, lit=0)
    outline(cv, wx0, wy0, wx1, wy1, [(60, 60, 66)])
    cv.hline(wx0, wx1, wy1 + 1, [(170, 166, 156)], 0, lit=0)                   # l'ampit
    # el terra (parquet) i la taula
    fill(cv, x0, y0 + 63, x1, y1, (90, 70, 56))
    for y in range(y0 + 65, y1 + 1, 3):
        cv.hline(x0, x1, y, [(80, 62, 50)], 0, lit=0)
    fill(cv, x0 + 88, y0 + 61, x1 - 13, y0 + 65, (60, 36, 26))
    cv.hline(x0 + 88, x1 - 13, y0 + 61, [(96, 62, 44)], 0, lit=0)
    fill(cv, x0 + 92, y0 + 66, x0 + 94, y1, (44, 26, 20))
    fill(cv, x1 - 18, y0 + 66, x1 - 16, y1, (44, 26, 20))
    # la planta del racó
    fill(cv, x1 - 8, y1 - 9, x1 - 2, y1, (150, 90, 60))
    for k in range(7):
        cv.line(x1 - 5, y1 - 9, x1 - 9 + k * 2, y1 - 20 + abs(k - 3) * 2, [(50, 110, 60)], 0, lit=0)
    # l'home de la corbata i la secretària (amb carpeta), de peu, un al costat de l'altre
    sil(cv, x0 + 61, y1, 45, col=(16, 18, 30), tie=(200, 40, 50))
    sil(cv, x0 + 141, y1, 40, col=(30, 22, 30), bun=True, skirt=True)
    fill(cv, x0 + 147, y1 - 27, x0 + 152, y1 - 19, (230, 220, 190))
    cv.vline(x0 + 147, y1 - 27, y1 - 19, [(200, 180, 140)], 0, lit=0)
    tag(cv, x0 + 61, y0 + 8, '12,00 €')
    tag(cv, x0 + 141, y0 + 13, '12,00 €')
    for yy in (y0 + 11, y0 + 12, y0 + 16, y0 + 17):                            # el signe igual
        cv.hline(x0 + 96, x0 + 107, yy, [GREEN_T], 0, lit=0)


def propina(cv, x0, y0, x1, y1):
    """El bar La Propina: en Tomàs abaixa la persiana metàl·lica amb el ganxo, a mig camí."""
    grad(cv, x0, y0, x1, y0 + 19, (150, 180, 210), (200, 210, 220))           # una mica de cel
    fill(cv, x0, y0 + 13, x1, y1, (150, 120, 96))                              # la façana d'arrebossat
    for k in range(70):
        cv.flat(x0 + int(hr(k, 1) * (x1 - x0)), y0 + 16 + int(hr(k, 2) * 70), (130, 104, 84))
    cv.hline(x0, x1, y0 + 13, [(120, 96, 76)], 0, lit=0)                       # la cornisa
    cv.hline(x0, x1, y0 + 14, [(176, 146, 120)], 0, lit=0)
    # el rètol, amb els cargols
    fill(cv, x0 + 27, y0 + 19, x1 - 27, y0 + 32, (40, 20, 18))
    outline(cv, x0 + 27, y0 + 19, x1 - 27, y0 + 32, [(80, 50, 40)])
    for sx in (x0 + 29, x1 - 29):
        cv.flat(sx, y0 + 21, (150, 130, 110))
        cv.flat(sx, y0 + 30, (150, 130, 110))
    s = 'LA PROPINA'
    text(cv, s, (x0 + x1) // 2 - text_width(s) // 2, y0 + 23, None, 0, lit=0, flat=(255, 190, 90))
    cv.glow((x0 + x1) // 2, y0 + 25, 40, (255, 170, 80), 0.18)
    # l'aparador: a baix encara es veu el bar per dins, a dalt ja tapa la persiana
    sx0, sx1, sy0, sy1 = x0 + 19, x1 - 53, y0 + 37, y1
    fill(cv, sx0, sy0, sx1, sy1, (60, 40, 30))
    fill(cv, sx0, sy0 + 31, sx1, sy0 + 32, (90, 60, 40))                       # el prestatge
    for k in range(7):                                                          # ampolles
        bx = sx0 + 6 + k * 14
        cv.rect(bx, sy0 + 34, bx + 2, sy0 + 42, [[(120, 160, 90), (160, 110, 60), (200, 200, 180)][k % 3]], 0, lit=0)
        cv.vline(bx + 1, sy0 + 31, sy0 + 33, [(90, 120, 70)], 0, lit=0)
        cv.flat(bx, sy0 + 35, (230, 240, 210))
    fill(cv, sx0 + 2, sy0 + 45, sx1 - 2, sy0 + 48, (110, 70, 40))              # la barra
    cv.hline(sx0 + 2, sx1 - 2, sy0 + 45, [(150, 100, 60)], 0, lit=0)
    cv.glow((sx0 + sx1) // 2, sy0 + 40, 35, (255, 190, 110), 0.25)
    half = sy0 + 29
    for y in range(sy0, half + 1):                                              # la persiana ondulada
        c = [(184, 186, 190), (170, 172, 176), (150, 152, 158), (110, 112, 118)][y % 4]
        for x in range(sx0, sx1 + 1):
            cv.flat(x, y, c)
    fill(cv, sx0, half, sx1, half + 2, (60, 60, 66))
    cv.hline(sx0, sx1, half + 1, [(120, 120, 128)], 0, lit=0)
    for gx in (sx0 + 16, sx1 - 19):                                             # els grafits de sempre
        cv.line(gx, sy0 + 8, gx + 11, sy0 + 16, [(220, 60, 120)], 0, lit=0)
        cv.line(gx, sy0 + 9, gx + 11, sy0 + 17, [(160, 40, 90)], 0, lit=0)
    cv.line(sx0 + 30, sy0 + 18, sx0 + 38, sy0 + 12, [(60, 160, 220)], 0, lit=0)
    # la porta, a la dreta, amb el vidre i el pom
    fill(cv, x1 - 45, y0 + 40, x1 - 21, y1, (80, 50, 34))
    outline(cv, x1 - 45, y0 + 40, x1 - 21, y1, [(50, 30, 20)])
    fill(cv, x1 - 41, y0 + 44, x1 - 25, y0 + 60, (110, 90, 70))
    cv.flat(x1 - 25, y0 + 70, (220, 190, 110))
    # en Tomàs, d'esquena, estirant el ganxo
    tx = sx1 - 21
    sil(cv, tx, y1, 40, col=(24, 20, 22))
    cv.line(tx + 5, y1 - 33, tx + 1, half + 2, [(40, 40, 46)], 0, lit=0)
    cv.flat(tx + 1, half + 3, (90, 90, 96))
    fill(cv, tx - 5, y1 - 33, tx - 4, y1 - 21, (240, 236, 226))               # el davantal, de reüll
    tag(cv, x0 + 40, y0 + 3, 'TANCAT')


def caixer(cv, x0, y0, x1, y1):
    """Un caixer automàtic al carrer: l'àvia amb bastó davant la pantalla i un cambrer que espera el sou."""
    fill(cv, x0, y0, x1, y1, (110, 104, 96))
    for i, y in enumerate(range(y0, y1, 11)):                                   # les filades de pedra
        cv.hline(x0, x1, y, [(90, 84, 78)], 0, lit=0)
        cv.hline(x0, x1, y + 1, [(124, 118, 108)], 0, lit=0)
        for jx in range(x0 + (i % 2) * 14, x1, 28):
            cv.vline(jx, y + 1, min(y1, y + 10), [(90, 84, 78)], 0, lit=0)
    # el caixer encastat
    ax0, ay0, ax1, ay1 = x0 + 53, y0 + 8, x0 + 123, y1 - 3
    fill(cv, ax0 - 2, ay0 - 2, ax1 + 2, ay1 + 2, (70, 70, 74))
    fill(cv, ax0, ay0, ax1, ay1, (40, 44, 52))
    fill(cv, ax0, ay0, ax1, ay0 + 8, (30, 60, 120))
    s = 'CAIXER'
    text(cv, s, (ax0 + ax1) // 2 - text_width(s) // 2 + 1, ay0 + 2, None, 0, lit=0, flat=(240, 240, 250))
    fill(cv, ax0 + 9, ay0 + 11, ax1 - 9, ay0 + 42, (24, 26, 32))                # el marc de la pantalla
    fill(cv, ax0 + 11, ay0 + 13, ax1 - 11, ay0 + 40, (6, 30, 16))              # la pantalla, en verd
    text(cv, 'SALDO', ax0 + 14, ay0 + 16, None, 0, lit=0, flat=(70, 200, 120))
    big_text(cv, '12€', ax0 + 17, ay0 + 24, GREEN_T, 3)
    cv.glow((ax0 + ax1) // 2, ay0 + 27, 35, (80, 255, 150), 0.25)
    for k in range(3):                                                          # els botons del costat
        cv.hline(ax0 + 5, ax0 + 8, ay0 + 18 + k * 7, [(150, 154, 160)], 0, lit=0)
        cv.hline(ax1 - 8, ax1 - 5, ay0 + 18 + k * 7, [(150, 154, 160)], 0, lit=0)
    fill(cv, ax0 + 13, ay0 + 45, ax1 - 13, ay0 + 59, (70, 76, 86))            # el teclat
    for r in range(3):
        for c in range(4):
            col = (180, 184, 190) if c < 3 else [(200, 60, 50), (220, 200, 60), (60, 170, 80)][r]
            cv.hline(ax0 + 17 + c * 11, ax0 + 19 + c * 11, ay0 + 48 + r * 4, [col], 0, lit=0)
    fill(cv, ax0 + 16, ay0 + 64, ax1 - 16, ay0 + 65, (10, 10, 14))            # la boca dels bitllets
    cv.hline(ax0 + 16, ax1 - 16, ay0 + 66, [(90, 96, 104)], 0, lit=0)
    cv.flat(ax1 - 18, ay0 + 69, (60, 220, 100))                                  # el llumet de la targeta
    # l'àvia: monyo, bossa i bastó
    gx = ax0 + 29
    sil(cv, gx, y1, 35, col=(150, 120, 140), bun=True, skirt=True)
    cv.disc(gx, y1 - 34, 3.2, 3.0, [(220, 220, 226)], 0, lit=0)                # els cabells blancs
    cv.disc(gx + 1, y1 - 37, 2.0, 2.0, [(220, 220, 226)], 0, lit=0)
    cv.line(gx + 7, y1 - 16, gx + 11, y1, [(70, 50, 30)], 0, lit=0)
    cv.hline(gx + 5, gx + 7, y1 - 17, [(70, 50, 30)], 0, lit=0)
    fill(cv, gx - 10, y1 - 19, gx - 5, y1 - 13, (90, 30, 40))
    cv.line(gx - 9, y1 - 19, gx - 6, y1 - 23, [(70, 24, 30)], 0, lit=0)
    # el cambrer: armilla negra, camisa blanca, safata sota el braç, mirant el rellotge
    wx = x1 - 29
    sil(cv, wx, y1, 43, col=(16, 16, 20))
    fill(cv, wx - 1, y1 - 32, wx + 1, y1 - 21, (236, 236, 236))
    cv.flat(wx, y1 - 33, (16, 16, 20))                                          # el corbatí
    cv.hline(wx - 1, wx + 1, y1 - 32, [(16, 16, 20)], 0, lit=0)
    cv.disc(wx + 9, y1 - 24, 7, 1.8, [(180, 184, 190)], 0, lit=0)
    cv.hline(wx + 3, wx + 15, y1 - 25, [(220, 224, 230)], 0, lit=0)
    cv.flat(wx - 7, y1 - 20, (240, 220, 120))
    tag(cv, wx - 11, y0 + 7, 'SOU: 12 €')


def mapa(cv, x0, y0, x1, y1, t=0):
    """El mapa del món de punts verds: de cada ciutat surt una línia cap al compte zero, al mig, i els diners
    hi corren (t)."""
    fill(cv, x0, y0, x1, y1, (2, 10, 12))
    mw, mh = x1 - x0, y1 - y0
    for y in range(y0 + 1, y1, 2):
        for x in range(x0 + 1, x1, 2):
            u, v = (x - x0) / mw, (y - y0) / mh
            land = any(((u - cx) / rx) ** 2 + ((v - cy) / ry) ** 2 < 1 for cx, cy, rx, ry in LAND)
            cv.flat(x, y, (50, 170, 96) if land else (6, 22, 24))
    for gx in range(x0 + 1, x1, 25):                                            # meridians i paral·lels, tènues
        for y in range(y0 + 1, y1, 4):
            cv.flat(gx, y, (14, 40, 40))
    zx, zy = x0 + mw // 2, y0 + mh // 2 + 5
    for cx, cy in CITIES:
        px, py = x0 + round(cx * mw), y0 + round(cy * mh)
        n = max(abs(zx - px), abs(zy - py), 1)
        for k in range(n + 1):                                                  # línia de punts cap al centre
            q = (round(px + (zx - px) * k / n), round(py + (zy - py) * k / n))
            if (k - t) % 4 == 0:
                cv.flat(*q, (170, 250, 255))
            elif k % 2 == 0:
                cv.flat(*q, (50, 160, 190))
        cv.flat(px, py, (200, 255, 255))
        cv.glow(px, py, 3, (150, 255, 255), 0.4)
    # el compte zero: un cercle que ho xucla tot
    cv.disc(zx, zy, 9, 9, CYANT, lambda nx, ny: 2.0 + (1 - math.hypot(nx, ny)) * 3, lit=0)
    cv.ring(zx, zy, 12, CYANT, 4.0, lit=0, step=8)
    big_text(cv, '0', zx - 2, zy - 5, (4, 20, 30), 2, bevel=False)
    cv.glow(zx, zy, 29, (100, 230, 255), 0.35)
    s = 'COMPTE ZERO'
    fill(cv, zx - text_width(s) // 2 - 3, zy + 15, zx + text_width(s) // 2 + 3, zy + 22, (2, 10, 12))
    text(cv, s, zx - text_width(s) // 2, zy + 16, None, 0, lit=0, flat=CYAN_T)


# ─── La paret de pantalles ─────────────────────────────────────────────────

def backdrop(cv):
    """El fons: una sala fosca amb la reixeta tènue d'un terminal i la claror verda que cau cap avall."""
    for y in range(H):
        for x in range(W):
            grid = (x % 16 == 0 or y % 16 == 0)
            cv.put(x, y, BEZEL, 1.0 + (0.6 if grid else 0) - max(0, (y - 267) / 80), lit=0)
    cv.tint(0, 261, W - 1, H - 1, (20, 120, 70), lambda x, y: 0.12 * max(0, 1 - (y - 261) / 67))


def header(cv, cursor=True, colon=True):
    """La capçalera: «ROBIN HOOD 2.0» en verd de terminal, el pagament i el rellotge a les 11:15."""
    fill(cv, 5, 4, W - 6, 36, (2, 8, 6))
    outline(cv, 5, 4, W - 6, 36, [(30, 110, 60)])
    cv.hline(6, W - 7, 5, [(10, 40, 24)], 0, lit=0)
    w = big_text(cv, 'ROBIN HOOD 2.0', 13, 8, GREEN_T, 3)
    if cursor:
        fill(cv, 13 + w + 5, 8, 13 + w + 12, 22, GREEN_T)
    cv.glow(13 + w // 2, 15, 107, (60, 255, 140), 0.12)
    text(cv, 'TOTS ELS COMPTES - COMPTE ZERO', 13, 27, None, 0, lit=0, flat=(70, 190, 110))
    s = 'PAGAMENT 1: 12,00 € PER PERSONA'
    big_x = 261
    text(cv, s, big_x, 12, None, 0, lit=0, flat=GREEN_T)
    # una barra de progrés plena, amb les divisions
    sw = text_width(s)
    fill(cv, big_x, 21, big_x + sw, 27, (6, 30, 16))
    fill(cv, big_x + 1, 22, big_x + sw - 1, 26, (60, 210, 120))
    cv.hline(big_x + 1, big_x + sw - 1, 22, [(130, 250, 170)], 0, lit=0)
    for k in range(big_x + 10, big_x + sw, 10):
        cv.vline(k, 23, 26, [(40, 160, 90)], 0, lit=0)
    # el rellotge
    fill(cv, 523, 7, W - 11, 33, (2, 12, 18))
    outline(cv, 523, 7, W - 11, 33, [(30, 110, 140)])
    clock = '11:15' if colon else '11 15'
    cw = text_width(clock) * 4
    big_text(cv, clock, 523 + (W - 11 - 523 - cw) // 2 + 1, 11, CYAN_T, 4)
    cv.glow(576, 20, 45, (100, 220, 255), 0.2)


VIEWS = [(monaco, 'MÒNACO', '12,00 €'), (nova_york, 'NOVA YORK', '12,00 €'), (ginebra, 'GINEBRA', '12,00 €'),
         (propina, 'BAR LA PROPINA', '12,00 €'), (caixer, 'CAIXER', '12,00 €'), (mapa, 'EL MÓN', '8.200.000.000 X 12 €')]


def screens(cv, blink=0, t=0):
    for i, (fn, name, amount) in enumerate(VIEWS):
        x0, y0, x1, y1 = PANELS[i]
        obox(cv, x0 - 4, y0 - 4, x1 + 4, y1 + 4, BEZEL, 3.0, lit=0)
        for sx, sy in ((x0 - 2, y0 - 2), (x1 + 2, y0 - 2), (x0 - 2, y1 + 2), (x1 + 2, y1 + 2)):   # els cargols
            cv.flat(sx, sy, (70, 74, 86))
        if fn is mapa:
            fn(cv, x0, y0, x1, y1 - LABEL_H - 1, t)
        else:
            fn(cv, x0, y0, x1, y1 - LABEL_H - 1)
        scanlines(cv, x0, y0, x1, y1 - LABEL_H - 1)
        label(cv, i, name, amount, blink)
        outline(cv, x0 - 1, y0 - 1, x1 + 1, y1 + 1, [(0, 0, 0)])
        cv.rect(x1 - 5, y0 + 3, x1 - 4, y0 + 4, [(240, 40, 36)], 0, lit=0)     # el punt vermell de directe
    # la claror de les pantalles cap avall
    cv.tint(0, 264, W - 1, 285, (40, 200, 160), lambda x, y: 0.12 * (1 - (y - 264) / 21))


def bg(cv, t=0):
    """t: fotograma (de 0 a NF-1, cada un de 200 ms)."""
    backdrop(cv)
    header(cv, cursor=(t // 2) % 2 == 0, colon=t % 8 < 4)
    screens(cv, blink=t // 2, t=t)


PROPS = {}


def _frames():
    base = Canvas(light=LIGHT)
    bg(base)
    frames = []
    for t in range(NF):
        cv = Canvas(light=LIGHT)
        bg(cv, t)
        frames.append(_diff(cv.img, base.img))
    return frames


ANIMS = {'pantalles': {'frames': _frames, 'frameDuration': 200}}

GEOMETRIA = {
    'things': {},
    'spawns': {},
    'walkable': [(200, 253), (267, 253), (267, 261), (200, 261)],
}
