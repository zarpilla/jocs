"""
Prova de resolució: les peces comunes de les sales de la coberta de sota (hd/rooms/sota.py) a 640×360.

Les mateixes funcions i signatures que a 480, amb els valors per defecte ×4/3 i una mica més de detall (dues
fileres de reblons a les quadernes, cordó a les soldadures, fils de cable a les safates). Les fan servir
hd640/rooms/camarot_iri.py i passadis_baix.py; les altres sales de sota (rebost, taller, pallol, sala de bombes,
caixa de cadenes) les poden importar igual:

    from hd640.rooms import sota
    sota.plate_wall(cv, 0, W - 1, frames=85, seams=(75, 149))
    sota.ceiling(cv)
    mask = sota.checker_floor(cv)

Coordenades: la paret es troba amb el terra a FLOOR_Y = 203 i la barra de verbs comença a BOTTOM = 260.
També hi ha fast_diff(), un _diff (comu) fet amb PIL: per a animacions de sala sencera és molt més ràpid.
"""
import math

import hd640  # noqa: F401  (posa la llibreria de dibuix a 640×360)
from hd.pix import W, H, hr, mix, B4, RUST
from hd.rooms.arenga import (WALL, ENG, DECK, CAB, DARK, WHITEP, YELL, BRASS, WARM,  # noqa: F401
                             box, rrect, bolt, hpipe, vpipe, glow)

FLOOR_Y = 203          # on la paret es troba amb el terra (152 × 4/3)
BOTTOM = 260           # per sota hi ha la franja de la frase i la barra de verbs
LAMP = [(120, 90, 40), (200, 160, 80), (250, 220, 150), (255, 246, 220)]


def plate_wall(cv, x0, x1, ramp=WALL, lvl=3.1, y0=0, y1=FLOOR_Y, frames=85, frame0=-11, seams=(85, 149), socle=179,
               rust=34, seed=0):
    """Paret de planxa pintada: quadernes de 7 px amb dues fileres de reblons, soldadures amb cordó, sòcol gastat
    i ratlles de rovell que baixen de les soldadures. `frames`: separació de les quadernes (0 = sense)."""
    for y in range(y0, y1):
        for x in range(x0, x1 + 1):
            v = lvl + (hr(x // 3, y // 5, seed) - 0.5) * 0.35
            if socle and y >= socle:
                v -= 0.9 + (0.3 if hr(x // 6, y // 3, seed) > 0.8 else 0)
            cv.put(x, y, ramp, v)
    if frames:
        for fx in range(frame0, x1 + 1, frames):
            for x in range(max(x0, fx), min(x1, fx + 7) + 1):
                d = x - fx
                for y in range(max(y0, 27), y1):
                    cv.put(x, y, ramp, lvl + 0.4 + (0.9 if d == 0 else 0.5 if d == 1 else -0.3 if d >= 6 else 0.1)
                           - (0.8 if socle and y >= socle else 0))
            for y in range(max(y0, 37), y1 - 24, 16):
                if x0 <= fx + 2 and fx + 5 <= x1:
                    bolt(cv, fx + 2, y, ramp, lvl + 0.5)
                    bolt(cv, fx + 5, y + 8, ramp, lvl + 0.3)
    for sy in seams:
        for x in range(x0, x1 + 1):
            cv.put(x, sy, ramp, lvl - 1.3)
            cv.put(x, sy + 1, ramp, lvl + 0.8 if (x // 2) % 2 else lvl + 0.3)       # el cordó de la soldadura
    if socle:
        cv.hline(x0, x1, socle, ramp, lvl + 0.9)
        cv.hline(x0, x1, socle + 1, ramp, lvl - 0.9)
    cv.hline(x0, x1, y1 - 1, ramp, lvl - 2.1)
    for i in range(rust):
        x = x0 + int(hr(i, 7, seed) * (x1 - x0))
        ys = [s for s in seams] or [y0 + 40]
        sy = ys[int(hr(i, 8, seed) * len(ys))] + 2
        n = 7 + int(hr(i, 9, seed) * 21)
        for xx in ((x, x + 1) if hr(i, 10, seed) > 0.6 else (x,)):
            for y in range(sy, min(y1 - 2, sy + n)):
                k = 0.5 * (1 - (y - sy) / n)
                if k > B4[y & 3][xx & 3] * 0.6 and x0 <= xx <= x1:
                    cv.flat(xx, y, mix(cv.get(xx, y), RUST[3], k))


def ceiling(cv, x0=0, x1=W - 1, h=25, beams=85, beam0=-11, trays=(7, 17)):
    """Sostre baix: baos, i safates de cables (amb els cables de colors i les brides)."""
    cv.rect(x0, 0, x1, h, DARK, 2.0)
    for bx in range(beam0, x1 + 1, beams):
        if bx + 11 >= x0:
            box(cv, max(x0, bx - 3), 0, min(x1, bx + 11), h + 3, ENG, 1.6, grad=0.6)
            if x0 <= bx - 2 <= x1:
                cv.vline(bx - 2, 1, h + 2, ENG, 2.6)
    for y in trays:
        cv.hline(x0, x1, y, CAB, 2.8)
        cv.hline(x0, x1, y + 5, CAB, 1.6)
        for x in range(x0, x1 + 1, 6):
            cv.vline(x, y, y + 5, CAB, 2.2)
        for k, row in enumerate((y + 2, y + 3)):
            for x in range(x0, x1 + 1):
                if hr(x // 12, y, k) > 0.3:
                    cv.flat(x, row, [(20, 20, 24), (40, 36, 30), (70, 50, 34), (110, 40, 34), (30, 50, 80)]
                            [int(hr(x // 14, y, k + 3) * 5)])
        for x in range(x0 + 30, x1 + 1, 70):
            cv.vline(x, y - 1, y + 6, CAB, 3.6)


def cage_lamp(cv, lx, ly=29, top=21, on=True):
    """Llum de gàbia al sostre (com els de la sala de màquines de 640)."""
    box(cv, lx - 8, top, lx + 8, top + 5, CAB, 3.0)
    cv.put(lx - 6, top + 2, CAB, 4.6)
    cv.put(lx + 6, top + 2, CAB, 4.6)
    cv.disc(lx, ly + 4, 8, 5, LAMP if on else CAB, 2.6 if on else 2.0, lit=0)
    for gx in (-5, 0, 5):
        cv.vline(lx + gx, ly, ly + 9, CAB, 2.2, lit=0)
    cv.hline(lx - 8, lx + 8, ly + 5, CAB, 2.0, lit=0)
    cv.hline(lx - 6, lx + 6, ly + 9, CAB, 1.8, lit=0)


def lamp_glow(cv, lx, ly=29):
    glow(cv, lx, ly + 5, 45, WARM, 0.55)
    glow(cv, lx, ly + 5, 16, (255, 240, 200), 0.6)


def checker_floor(cv, x0=0, x1=W - 1, y0=FLOOR_Y, y1=BOTTOM + 15, vp=(320, 53), ramp=DECK, lvl=2.5, plate=101,
                  seams=(211, 227, 249)):
    """Terra de planxa estriada en perspectiva. → màscara del terra (llista de files de booleans)."""
    mask = [[False] * W for _ in range(H)]
    for y in range(y0, min(H, y1 + 1)):
        d = y - vp[1]
        for x in range(x0, x1 + 1):
            u = vp[0] + (x - vp[0]) * 200 / d
            u2 = vp[0] + (x + 1 - vp[0]) * 200 / d
            v = 4267 / d
            lv = lvl
            if int(u // plate) != int(u2 // plate):
                lv = lvl - 1.5
            elif y in seams:
                lv = lvl - 1.4
            elif y - 1 in seams:
                lv = lvl + 0.8
            else:
                a, b = int(u * 0.5) % 4, int(v * 1.6) % 4
                if (a == 0 and b in (0, 1)) or (a == 2 and b in (2, 3)):
                    lv += 0.9
                elif (a == 1 and b == 1) or (a == 3 and b == 3):
                    lv -= 0.3
            cv.put(x, y, ramp, lv)
            mask[y][x] = True
    return mask


def door_frame(cv, x0, y0, x1, y1, ramp=WALL, lvl=4.4, r=12):
    """El marc d'una porta estanca (cantons rodons a dalt), de 4 px de gruix."""
    for t in range(4):
        for y in range(y0 - t, y1 + 1):
            for x in range(x0 - t, x1 + t + 1):
                dx = max(x0 - t + r - x, 0, x - (x1 + t - r))
                dy = max(y0 - t + r - y, 0)
                inside = dx * dx + dy * dy <= r * r
                inner = x0 - t + 1 <= x <= x1 + t - 1 and y >= y0 - t + 1
                ddx = max(x0 - t + 1 + r - x, 0, x - (x1 + t - 1 - r))
                ddy = max(y0 - t + 1 + r - y, 0)
                if inside and not (inner and ddx * ddx + ddy * ddy <= r * r):
                    cv.put(x, y, ramp, lvl - t * 0.8)


def in_door(x, y, x0, y0, x1, y1, r=12):
    """Si (x, y) és dins l'obertura de la porta (cantons rodons a dalt)."""
    if not (x0 <= x <= x1 and y0 <= y <= y1):
        return False
    dx = max(x0 + r - x, 0, x - (x1 - r))
    dy = max(y0 + r - y, 0)
    return dx * dx + dy * dy <= r * r


def dark_opening(cv, x0, y0, x1, y1, r=12, far_light=True, base=1.6):
    """L'altra banda d'una porta oberta: un passadís fosc que s'allunya, amb un llum llunyà."""
    cx = (x0 + x1) / 2
    for y in range(y0, y1):
        for x in range(x0, x1 + 1):
            if in_door(x, y, x0, y0, x1, y1, r):
                cv.put(x, y, DARK, base - abs(x - cx) / 40 + (0.9 if y > y1 - 27 else 0) - (y - y0) / 160, lit=0.3)
    if far_light:
        cv.disc(cx, y0 + 13, 4, 2, [(80, 70, 50), (160, 140, 100), (210, 196, 150)], 1.6, lit=0)
        glow(cv, cx, y0 + 16, 16, (140, 130, 100), 0.35)


def wt_leaf(cv, x0, y0, x1, y1, ramp=ENG, lvl=3.0, r=11, handle_side='right', dogs=True):
    """La fulla tancada d'una porta estanca: planxa amb un plafó, palanques («dogs») amb cargol, i nansa."""
    rrect(cv, x0, y0, x1, y1, r, ramp, lambda x, y: lvl - (y - y0) * 0.005)
    rrect(cv, x0 + 5, y0 + 5, x1 - 5, y1 - 8, max(3, r - 4), ramp, lambda x, y: lvl + 0.35 - (y - y0) * 0.005)
    cv.hline(x0 + 8, x1 - 8, y0 + 5, ramp, lvl + 1.4)
    cv.hline(x0 + 8, x1 - 8, y1 - 8, ramp, lvl - 1.0)
    cv.vline(x1 - 5, y0 + 11, y1 - 11, ramp, lvl - 0.8)
    cv.vline(x0 + 5, y0 + 11, y1 - 11, ramp, lvl + 0.9)
    hx = x1 - 9 if handle_side == 'right' else x0 + 5
    if dogs:
        for dy in (y0 + 19, (y0 + y1) // 2, y1 - 24):
            box(cv, hx, dy, hx + 4, dy + 11, CAB, 3.8)
            cv.put(hx + 1, dy + 1, CAB, 5.4)
            cv.put(hx + 2, dy + 9, CAB, 1.6)
        ox = x0 + 5 if handle_side == 'right' else x1 - 9
        for dy in (y0 + 19, y1 - 24):
            box(cv, ox, dy, ox + 4, dy + 8, CAB, 3.2)
            cv.put(ox + 2, dy + 4, CAB, 1.4)


def hinge_leaf(cv, x0, y0, x1, y1, ramp=ENG, lvl=2.8):
    """La fulla d'una porta oberta contra la paret, vista de cantó."""
    cv.poly([(x0, y0 + 5), (x1, y0 - 1), (x1, y1 - 3), (x0, y1 - 5)], ramp, lambda x, y: lvl - (x - x0) * 0.05)
    cv.vline(x1, y0, y1 - 3, ramp, lvl + 1.4)
    for y in range(y0 + 13, y1 - 10, 29):
        box(cv, x0 + 2, y, x1 - 2, y + 4, ramp, lvl + 0.8)
        cv.put(x0 + 3, y + 1, ramp, lvl + 2.4)


def sill(cv, x0, x1, y1, ramp=WALL, lvl=2.6):
    """El llindar alt de les portes de vaixell (amb cargols)."""
    cv.rect(x0 + 1, y1 - 8, x1 - 1, y1 - 1, ramp, lvl)
    cv.hline(x0 + 1, x1 - 1, y1 - 8, ramp, lvl + 1.4)
    for x in range(x0 + 4, x1 - 3, 6):
        bolt(cv, x, y1 - 5, ramp, lvl + 0.8)


def vladder(cv, x0, x1, y0, y1, ramp=CAB, lvl=3.2, step=12, rail=3):
    """Escala de mà vertical (dos muntants i graons rodons)."""
    for y in range(y0, y1 + 1, step):
        hpipe(cv, x0 + rail, x1 - rail, y, 1, ramp, lvl)
    vpipe(cv, x0 + 1, y0 - 3, y1, 1, ramp, lvl + 0.3)
    vpipe(cv, x1 - 1, y0 - 3, y1, 1, ramp, lvl - 0.2)


def sign(cv, x0, y0, s, ramp=WHITEP, lvl=4.0, ink=None, pad=3, screws=True):
    """Un rètol (planxa amb lletres de 5 px, i dos cargols si hi cap). → amplada."""
    from hd.rooms.comu import text, text_width
    w = text_width(s)
    x1, y1 = x0 + w + pad * 2 + 1, y0 + 5 + pad * 2
    box(cv, x0, y0, x1, y1, ramp, lvl)
    cv.hline(x0 + 1, x1 - 1, y1 - 1, ramp, lvl - 0.8)
    text(cv, s, x0 + pad + 1, y0 + pad + 1, None, 0, flat=ink or (20, 24, 28))
    if screws and pad >= 3:
        for sx in (x0 + 1, x1 - 1):
            cv.put(sx, (y0 + y1) // 2, ramp, lvl - 2.0)
    return x1 - x0 + 1


def centered_sign(cv, cx, y0, s, **kw):
    """sign() centrat a cx."""
    from hd.rooms.comu import text_width
    pad = kw.get('pad', 3)
    return sign(cv, cx - (text_width(s) + pad * 2 + 2) // 2, y0, s, **kw)


def rust_streaks(cv, x0, y0, x1, y1, n, k=0.5, seed=0, ramp=RUST):
    for i in range(n):
        x = x0 + int(hr(i, 1, seed) * (x1 - x0))
        sy = y0 + int(hr(i, 2, seed) * (y1 - y0) * 0.6)
        ln = 5 + int(hr(i, 3, seed) * 19)
        for y in range(sy, min(y1, sy + ln)):
            kk = k * (1 - (y - sy) / ln)
            if kk > B4[y & 3][x & 3] * 0.6:
                cv.flat(x, y, mix(cv.get(x, y), ramp[3], kk))


def unmask(mask, cv, x0, y0, x1, y1, before):
    """Treu del terra els píxels que ha pintat un objecte (comparant amb una còpia d'abans)."""
    a, b = before.load(), cv.img.load()
    for y in range(max(0, y0), min(H, y1 + 1)):
        for x in range(max(0, x0), min(W, x1 + 1)):
            if a[x, y] != b[x, y]:
                mask[y][x] = False


def floor_shadow(cv, cx, cy, rx, ry, k=0.6):
    """Ombra suau sota d'un objecte a terra."""
    cv.darken(cx - rx, cy - ry, cx + rx, cy + ry,
              lambda x, y: k * max(0.0, 1 - ((x - cx) / rx) ** 2 - ((y - cy) / ry) ** 2) * 1.6)


def fast_diff(frame, base, box=None):
    """Com comu._diff (només els píxels que canvien; la resta, transparent), però amb PIL: per a animacions de
    sala sencera. `box` (x0, y0, x1, y1, exclusiu) limita on es mira; fora, tot transparent."""
    from PIL import Image, ImageChops
    out = Image.new('RGBA', frame.size, (0, 0, 0, 0))
    if box is None:
        box = (0, 0) + frame.size
    a, b = frame.crop(box), base.crop(box)
    m = ImageChops.difference(a, b).convert('L').point(lambda v: 255 if v else 0)
    out.paste(a, box[:2], m)
    return out


def diff_prop(cv, base_fn, draw_fn, light):
    """Per a un prop que canvia la llum: dibuixa el fons, hi afegeix el prop i en deixa només el que canvia."""
    from hd.pix import Canvas
    base = Canvas(light=light)
    base_fn(base)
    var = Canvas(light=light, img=base.img.copy())
    draw_fn(var)
    cv.img.alpha_composite(fast_diff(var.img, base.img))


def math_ring(cx, cy, r, step=24):
    """Punts d'un cercle (per a rodones d'aigua i anelles)."""
    return [(cx + round(math.cos(math.radians(a)) * r), cy + round(math.sin(math.radians(a)) * r))
            for a in range(0, 360, step)]
