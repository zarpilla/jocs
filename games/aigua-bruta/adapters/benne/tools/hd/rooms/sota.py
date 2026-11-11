"""
Peces comunes de les sales de la coberta de sota que no són la sala de màquines (camarot de l'Iri, passadís de
baix, pallol, sala de bombes, caixa de cadenes): paret de planxa amb quadernes, sostre amb safates de cables,
terra de planxa estriada, llums de gàbia, portes estanques, escales de mà i escotilles.
Mateix estil que la sala de mostra (guio/art/mostra/sala_maquines.py).
"""
import math

from hd.pix import W, H, hr, mix, B4, RUST
from hd.rooms.arenga import (WALL, ENG, DECK, CAB, DARK, WHITEP, YELL, BRASS, WARM, FLOOR_Y, BOTTOM,
                             box, rrect, bolt, hpipe, vpipe, glow)

LAMP = [(120, 90, 40), (200, 160, 80), (250, 220, 150), (255, 246, 220)]


def plate_wall(cv, x0, x1, ramp=WALL, lvl=3.1, y0=0, y1=FLOOR_Y, frames=64, frame0=-8, seams=(64, 112), socle=134,
               rust=26, seed=0):
    """Paret de planxa pintada: quadernes amb reblons, soldadures, sòcol gastat i ratlles de rovell."""
    for y in range(y0, y1):
        for x in range(x0, x1 + 1):
            v = lvl + (hr(x // 3, y // 5, seed) - 0.5) * 0.35
            if socle and y >= socle:
                v -= 0.9 + (0.3 if hr(x // 6, y // 3, seed) > 0.8 else 0)
            cv.put(x, y, ramp, v)
    if frames:
        for fx in range(frame0, x1 + 1, frames):
            for x in range(max(x0, fx), min(x1, fx + 5) + 1):
                d = x - fx
                for y in range(max(y0, 20), y1):
                    cv.put(x, y, ramp, lvl + 0.4 + (0.9 if d == 0 else 0.5 if d == 1 else -0.3 if d >= 4 else 0.1)
                           - (0.8 if socle and y >= socle else 0))
            for y in range(max(y0, 28), y1 - 18, 12):
                if x0 <= fx + 2 <= x1:
                    bolt(cv, fx + 2, y, ramp, lvl + 0.5)
    for sy in seams:
        for x in range(x0, x1 + 1):
            cv.put(x, sy, ramp, lvl - 1.3)
            cv.put(x, sy + 1, ramp, lvl + 0.8 if hr(x // 2, sy) > 0.3 else lvl + 0.1)
    if socle:
        cv.hline(x0, x1, socle, ramp, lvl + 0.9)
    cv.hline(x0, x1, y1 - 1, ramp, lvl - 2.1)
    for i in range(rust):
        x = x0 + int(hr(i, 7, seed) * (x1 - x0))
        ys = [s for s in seams] or [y0 + 30]
        sy = ys[int(hr(i, 8, seed) * len(ys))] + 2
        n = 5 + int(hr(i, 9, seed) * 16)
        for y in range(sy, min(y1 - 2, sy + n)):
            k = 0.5 * (1 - (y - sy) / n)
            if k > B4[y & 3][x & 3] * 0.6:
                cv.flat(x, y, mix(cv.get(x, y), RUST[3], k))


def ceiling(cv, x0=0, x1=W - 1, h=19, beams=64, beam0=-8, trays=(6, 13)):
    cv.rect(x0, 0, x1, h, DARK, 2.0)
    for bx in range(beam0, x1 + 1, beams):
        if bx + 8 >= x0:
            box(cv, max(x0, bx - 2), 0, min(x1, bx + 8), h + 2, ENG, 1.6, grad=0.6)
    for y in trays:
        cv.hline(x0, x1, y, CAB, 2.8)
        cv.hline(x0, x1, y + 4, CAB, 1.6)
        for x in range(x0, x1 + 1, 5):
            cv.vline(x, y, y + 4, CAB, 2.2)
        for x in range(x0, x1 + 1):
            if hr(x // 9, y) > 0.35:
                cv.flat(x, y + 2, [(20, 20, 24), (40, 36, 30), (70, 50, 34), (110, 40, 34)][int(hr(x // 11, y) * 4)])


def cage_lamp(cv, lx, ly=22, top=16, on=True):
    """Llum de gàbia al sostre (com els de la sala de màquines)."""
    box(cv, lx - 6, top, lx + 6, top + 4, CAB, 3.0)
    cv.disc(lx, ly + 3, 6, 4, LAMP if on else CAB, 2.6 if on else 2.0, lit=0)
    for gx in (-4, 0, 4):
        cv.vline(lx + gx, ly, ly + 7, CAB, 2.2, lit=0)
    cv.hline(lx - 6, lx + 6, ly + 4, CAB, 2.0, lit=0)


def lamp_glow(cv, lx, ly=22):
    glow(cv, lx, ly + 4, 34, WARM, 0.55)
    glow(cv, lx, ly + 4, 12, (255, 240, 200), 0.6)


def checker_floor(cv, x0=0, x1=W - 1, y0=FLOOR_Y, y1=BOTTOM + 11, vp=(240, 40), ramp=DECK, lvl=2.5, plate=76,
                  seams=(158, 170, 187)):
    """Terra de planxa estriada en perspectiva (com la mostra). → màscara del terra."""
    mask = [[False] * W for _ in range(H)]
    for y in range(y0, min(H, y1 + 1)):
        d = y - vp[1]
        for x in range(x0, x1 + 1):
            u = vp[0] + (x - vp[0]) * 150 / d
            u2 = vp[0] + (x + 1 - vp[0]) * 150 / d
            v = 2400 / d
            lv = lvl
            if int(u // plate) != int(u2 // plate):
                lv = lvl - 1.5
            elif y in seams:
                lv = lvl - 1.4
            elif y - 1 in seams:
                lv = lvl + 0.8
            else:
                a, b = int(u * 0.5) % 4, int(v * 1.0) % 4
                if (a == 0 and b in (0, 1)) or (a == 2 and b in (2, 3)):
                    lv += 0.9
            cv.put(x, y, ramp, lv)
            mask[y][x] = True
    return mask


def door_frame(cv, x0, y0, x1, y1, ramp=WALL, lvl=4.2, r=9):
    """El marc d'una porta estanca (cantons rodons a dalt), de 3 px de gruix."""
    for t in range(3):
        for y in range(y0 - t, y1 + 1):
            for x in range(x0 - t, x1 + t + 1):
                dx = max(x0 - t + r - x, 0, x - (x1 + t - r))
                dy = max(y0 - t + r - y, 0)
                inside = dx * dx + dy * dy <= r * r
                inner = x0 - t + 1 <= x <= x1 + t - 1 and y >= y0 - t + 1
                ddx = max(x0 - t + 1 + r - x, 0, x - (x1 + t - 1 - r))
                ddy = max(y0 - t + 1 + r - y, 0)
                if inside and not (inner and ddx * ddx + ddy * ddy <= r * r):
                    cv.put(x, y, ramp, lvl - t * 0.9)


def in_door(x, y, x0, y0, x1, y1, r=9):
    """Si (x, y) és dins l'obertura de la porta (cantons rodons a dalt)."""
    if not (x0 <= x <= x1 and y0 <= y <= y1):
        return False
    dx = max(x0 + r - x, 0, x - (x1 - r))
    dy = max(y0 + r - y, 0)
    return dx * dx + dy * dy <= r * r


def dark_opening(cv, x0, y0, x1, y1, r=9, far_light=True, base=1.6):
    """L'altra banda d'una porta oberta: un passadís fosc amb un llum llunyà."""
    cx = (x0 + x1) / 2
    for y in range(y0, y1):
        for x in range(x0, x1 + 1):
            if in_door(x, y, x0, y0, x1, y1, r):
                cv.put(x, y, DARK, base - abs(x - cx) / 30 + (0.9 if y > y1 - 20 else 0) - (y - y0) / 120, lit=0.3)
    if far_light:
        cv.disc(cx, y0 + 10, 3, 1.5, [(80, 70, 50), (160, 140, 100)], 1.4, lit=0)
        glow(cv, cx, y0 + 12, 12, (140, 130, 100), 0.35)


def wt_leaf(cv, x0, y0, x1, y1, ramp=ENG, lvl=3.0, r=8, handle_side='right', dogs=True):
    """La fulla tancada d'una porta estanca: planxa amb un plafó, palanques («dogs») i nansa."""
    rrect(cv, x0, y0, x1, y1, r, ramp, lambda x, y: lvl - (y - y0) * 0.006)
    rrect(cv, x0 + 4, y0 + 4, x1 - 4, y1 - 6, max(2, r - 3), ramp, lambda x, y: lvl + 0.35 - (y - y0) * 0.006)
    cv.hline(x0 + 6, x1 - 6, y0 + 4, ramp, lvl + 1.4)
    cv.hline(x0 + 6, x1 - 6, y1 - 6, ramp, lvl - 1.0)
    cv.vline(x1 - 4, y0 + 8, y1 - 8, ramp, lvl - 0.8)
    cv.vline(x0 + 4, y0 + 8, y1 - 8, ramp, lvl + 0.9)
    hx = x1 - 7 if handle_side == 'right' else x0 + 4
    if dogs:
        for dy in (y0 + 14, (y0 + y1) // 2, y1 - 18):
            box(cv, hx, dy, hx + 3, dy + 8, CAB, 3.8)
            cv.put(hx + 1, dy + 1, CAB, 5.4)
        ox = x0 + 4 if handle_side == 'right' else x1 - 7
        for dy in (y0 + 14, y1 - 18):
            box(cv, ox, dy, ox + 3, dy + 6, CAB, 3.2)


def hinge_leaf(cv, x0, y0, x1, y1, ramp=ENG, lvl=2.8):
    """La fulla d'una porta oberta contra la paret, vista de cantó."""
    cv.poly([(x0, y0 + 4), (x1, y0 - 1), (x1, y1 - 2), (x0, y1 - 4)], ramp, lambda x, y: lvl - (x - x0) * 0.06)
    for y in range(y0 + 10, y1 - 8, 22):
        box(cv, x0 + 2, y, x1 - 2, y + 3, ramp, lvl + 0.8)


def sill(cv, x0, x1, y1, ramp=WALL, lvl=2.6):
    """El llindar alt de les portes de vaixell."""
    cv.rect(x0 + 1, y1 - 6, x1 - 1, y1 - 1, ramp, lvl)
    cv.hline(x0 + 1, x1 - 1, y1 - 6, ramp, lvl + 1.4)


def vladder(cv, x0, x1, y0, y1, ramp=CAB, lvl=3.2, step=9, rail=2):
    """Escala de mà vertical (dos muntants i graons rodons)."""
    for y in range(y0, y1 + 1, step):
        hpipe(cv, x0 + rail, x1 - rail, y, 1, ramp, lvl)
    vpipe(cv, x0 + 1, y0 - 2, y1, 1, ramp, lvl + 0.3)
    vpipe(cv, x1 - 1, y0 - 2, y1, 1, ramp, lvl - 0.2)


def sign(cv, x0, y0, s, ramp=WHITEP, lvl=4.0, ink=None, pad=2):
    """Un rètol petit (planxa amb lletres de 5 px)."""
    from hd.rooms.comu import text, text_width
    w = text_width(s)
    box(cv, x0, y0, x0 + w + pad * 2 + 1, y0 + 5 + pad * 2, ramp, lvl)
    text(cv, s, x0 + pad + 1, y0 + pad + 1, None, 0, flat=ink or (20, 24, 28))
    return w + pad * 2 + 2


def rust_streaks(cv, x0, y0, x1, y1, n, k=0.5, seed=0, ramp=RUST):
    for i in range(n):
        x = x0 + int(hr(i, 1, seed) * (x1 - x0))
        sy = y0 + int(hr(i, 2, seed) * (y1 - y0) * 0.6)
        ln = 4 + int(hr(i, 3, seed) * 14)
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


def diff_prop(cv, base_fn, draw_fn, light):
    """Per a un prop que canvia la llum: dibuixa el fons, hi afegeix el prop i en deixa només el que canvia."""
    from hd.pix import Canvas
    from hd.rooms.comu import _diff
    base = Canvas(light=light)
    base_fn(base)
    var = Canvas(light=light)
    var.img = base.img.copy()
    var.P = var.img.load()
    draw_fn(var)
    cv.img.alpha_composite(_diff(var.img, base.img))
