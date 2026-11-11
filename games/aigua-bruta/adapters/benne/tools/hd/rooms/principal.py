"""
Peces comunes de les sales de la coberta principal de l'Arenga (passadís, menjador, cuina, infermeria): planxa
pintada de color crema amb reblons, passamans i sòcol de fusta, sostre blanc amb baos i tubs, linòleum en
perspectiva amb la brillantor dels llums, llums de sostre càlids, portes de vaixell (cantons rodons, llindar alt,
palanques), ulls de bou amb el mar de nit, plaques amb el nom i la boca del tub de veu de llautó.
Mateix estil que la sala de mostra (guio/art/mostra/sala_maquines.py).
"""
import math

from hd.pix import W, H, hr, mix, B4, RUST
from hd.rooms.arenga import (CAB, DARK, WHITEP, REDP, YELL, BRASS, WARM, FLOOR_Y, BOTTOM,
                             box, rrect, bolt, hpipe, vpipe, glow)
from hd.rooms.comu import text, text_width

# ─── Rampes (fosc → clar) ───────────────────────────────────────────────────
CREAM = [(14, 12, 10), (28, 24, 20), (46, 40, 33), (68, 60, 49), (94, 84, 68), (122, 110, 89), (150, 137, 111),
         (178, 164, 134), (202, 189, 156), (222, 211, 178), (238, 230, 202)]
TEAK = [(16, 8, 6), (30, 15, 9), (48, 26, 14), (70, 40, 20), (94, 56, 28), (120, 74, 38), (148, 96, 50),
        (176, 122, 68), (204, 152, 92)]
LINO = [(12, 6, 6), (24, 11, 10), (40, 18, 15), (58, 27, 21), (78, 38, 28), (100, 50, 35), (124, 64, 44),
        (148, 80, 55), (172, 100, 70)]
DOORP = [(10, 12, 12), (20, 24, 24), (34, 40, 39), (50, 58, 56), (68, 79, 75), (90, 102, 96), (114, 127, 118),
         (142, 154, 142), (172, 182, 168)]                    # verd de porta, pintat
NIGHT = [(2, 4, 10), (5, 9, 18), (9, 15, 28), (14, 22, 40), (21, 31, 54), (31, 43, 70), (46, 60, 90)]
LAMP = [(120, 90, 40), (200, 160, 80), (250, 220, 150), (255, 246, 220)]
WOODP = [(20, 12, 8), (38, 22, 14), (58, 34, 20), (80, 50, 28), (104, 66, 38), (130, 86, 50), (158, 108, 66),
         (186, 134, 86)]

CEIL_H = 18


# ─── Paret, sostre i terra ─────────────────────────────────────────────────

def wall(cv, x0=0, x1=W - 1, ramp=CREAM, lvl=4.6, frames=72, frame0=-10, seam=64, dado=128, rail=108, seed=0):
    """Planxa pintada de crema: quadernes amb reblons, una soldadura, passamans i sòcol de fusta."""
    for y in range(CEIL_H, FLOOR_Y):
        for x in range(x0, x1 + 1):
            v = lvl + (hr(x // 3, y // 5, seed) - 0.5) * 0.25
            cv.put(x, y, ramp, v)
    if frames:
        for fx in range(frame0, x1 + 1, frames):
            for x in range(max(x0, fx), min(x1, fx + 4) + 1):
                d = x - fx
                for y in range(CEIL_H, dado or FLOOR_Y):
                    cv.put(x, y, ramp, lvl + (0.9 if d == 0 else 0.4 if d == 1 else -0.5 if d >= 3 else 0.1))
            for y in range(CEIL_H + 8, (dado or FLOOR_Y) - 4, 11):
                if x0 <= fx + 2 <= x1:
                    bolt(cv, fx + 2, y, ramp, lvl + 0.2)
    if seam:
        for x in range(x0, x1 + 1):
            cv.put(x, seam, ramp, lvl - 1.1)
            cv.put(x, seam + 1, ramp, lvl + 0.7 if hr(x // 2, seam) > 0.3 else lvl + 0.1)
    if dado:
        # sòcol: taulons de fusta envernissada
        for y in range(dado, FLOOR_Y):
            for x in range(x0, x1 + 1):
                plank = (x + 7 * ((y - dado) // 6)) % 23
                v = 3.0 + (hr(x // 5, (y - dado) // 6, seed) - 0.5) * 0.6 - (0.9 if plank == 0 else 0)
                if (y - dado) % 6 == 0:
                    v -= 0.8
                cv.put(x, y, TEAK, v)
        cv.hline(x0, x1, dado, TEAK, 4.6)
        cv.hline(x0, x1, dado + 1, TEAK, 3.8)
        cv.hline(x0, x1, FLOOR_Y - 1, TEAK, 1.4)
    if rail:
        handrail(cv, x0, x1, rail)


def handrail(cv, x0, x1, y):
    """El passamans de fusta, amb els suports de llautó."""
    hpipe(cv, x0, x1, y, 2, TEAK, 3.8)
    for x in range(x0 + 14, x1, 56):
        cv.rect(x, y + 3, x + 1, y + 6, BRASS, 3.2)
        cv.rect(x - 1, y + 6, x + 2, y + 7, BRASS, 2.6)


def ceiling(cv, x0=0, x1=W - 1, beams=72, beam0=-10, pipes=True):
    """Sostre pintat de blanc: baos, una safata de cables i dos tubs (aigua dolça i contra incendis)."""
    for y in range(0, CEIL_H + 1):
        for x in range(x0, x1 + 1):
            cv.put(x, y, CREAM, 3.0 + y * 0.04)
    for bx in range(beam0, x1 + 1, beams):
        if bx + 8 >= x0:
            box(cv, max(x0, bx - 2), 0, min(x1, bx + 7), CEIL_H + 2, CREAM, 3.6, grad=0.6)
    cv.hline(x0, x1, 4, CAB, 2.6)
    cv.hline(x0, x1, 8, CAB, 1.8)
    for x in range(x0, x1 + 1, 6):
        cv.vline(x, 4, 8, CAB, 2.2)
    for x in range(x0, x1 + 1):
        if hr(x // 9, 4) > 0.4:
            cv.flat(x, 6, [(40, 36, 30), (70, 50, 34), (110, 40, 34), (30, 40, 60)][int(hr(x // 11, 5) * 4)])
    if pipes:
        hpipe(cv, x0, x1, 12, 2, REDP, 3.6, bands=range(x0 + 30, x1, 90), band_ramp=WHITEP)     # contra incendis
        hpipe(cv, x0, x1, 16, 1, WHITEP, 3.4, bands=range(x0 + 60, x1, 90), band_ramp=[(10, 30, 70), (20, 60, 130), (60, 110, 190), (130, 170, 230)])
    cv.hline(x0, x1, CEIL_H + 1, CREAM, 2.2)                  # l'ombra del sostre a la paret


def lamp(cv, lx, ly=CEIL_H + 2):
    """Llum de sostre de vaixell: plafó ovalat amb gàbia, encès."""
    box(cv, lx - 8, ly - 3, lx + 8, ly, CAB, 3.4)
    cv.disc(lx, ly + 3, 7, 4, LAMP, 2.6, lit=0)
    cv.hline(lx - 7, lx + 7, ly + 3, CAB, 2.4, lit=0)
    for gx in (-4, 0, 4):
        cv.vline(lx + gx, ly + 1, ly + 7, CAB, 2.4, lit=0)


def lamp_glow(cv, lx, ly=CEIL_H + 2, k=1.0):
    glow(cv, lx, ly + 4, 36, WARM, 0.5 * k)
    glow(cv, lx, ly + 4, 12, (255, 240, 200), 0.6 * k)


def lino(cv, ramp=LINO, lvl=3.2, x0=0, x1=W - 1, y0=FLOOR_Y, y1=BOTTOM + 11, vp=(240, 30), tile=None, check=0.0,
         seed=0):
    """Linòleum en perspectiva: tires (o rajoles, amb `tile`) i taques. → màscara del terra."""
    mask = [[False] * W for _ in range(H)]
    for y in range(y0, min(H, y1 + 1)):
        d = y - vp[1]
        v = 2600 / d
        for x in range(x0, x1 + 1):
            u = vp[0] + (x - vp[0]) * 150 / d
            u2 = vp[0] + (x + 1 - vp[0]) * 150 / d
            lv = lvl + (hr(int(u // 3), int(v * 2), seed) - 0.5) * 0.45
            if tile:
                if check and (int(u // tile) + int(v * 2.0)) % 2:
                    lv += check
                if int(u // tile) != int(u2 // tile):
                    lv -= 0.9
                elif int(v * 2.0) != int(2600 / (d + 1) * 2.0):
                    lv -= 0.7
            else:
                if int(u // 60) != int(u2 // 60):
                    lv -= 1.0
            cv.put(x, y, ramp, lv)
            mask[y][x] = True
    cv.hline(x0, x1, y0, ramp, lvl - 1.6)                     # on la paret toca a terra
    return mask


def shine(cv, mask, lamps, col=WARM, k=1.0, refl=0.22):
    """Terra encerat: el reflex (tou) de la paret i la brillantor dels llums, un con que s'eixampla cap a baix."""
    src = cv.img.copy().load()
    for y in range(FLOOR_Y + 1, BOTTOM + 11):
        depth = (y - FLOOR_Y) / (BOTTOM - FLOOR_Y)
        sy = 2 * FLOOR_Y - y
        for x in range(W):
            if not mask[y][x]:
                continue
            c = cv.get(x, y)[:3]
            kk = refl * max(0.0, 1 - depth * 1.6)
            if kk > 0 and 0 <= sy < H:
                c = mix(c, src[x, sy][:3], kk)
            for lx in lamps:
                t = depth
                wdt = 4 + t * 10
                g = math.exp(-((x - lx) / wdt) ** 2) * (1 - t * 0.7) * k
                if g > 0.05:
                    if g * 0.9 > B4[y & 3][x & 3]:
                        c = mix(c, col, min(0.5, 0.18 + g * 0.3))
                    else:
                        c = mix(c, col, g * 0.15)
            cv.flat(x, y, c)


def unmask(mask, cv, x0, y0, x1, y1, before):
    """Treu del terra els píxels que ha pintat un objecte (comparant amb una còpia d'abans)."""
    a, b = before.load(), cv.img.load()
    for y in range(max(0, y0), min(H, y1 + 1)):
        for x in range(max(0, x0), min(W, x1 + 1)):
            if a[x, y] != b[x, y]:
                mask[y][x] = False


def floor_shadow(cv, cx, cy, rx, ry, k=0.6):
    """Ombra suau a terra."""
    cv.darken(cx - rx, cy - ry, cx + rx, cy + ry,
              lambda x, y: k * max(0.0, 1 - ((x - cx) / rx) ** 2 - ((y - cy) / ry) ** 2) * 1.6)


def foot_shadow(cv, x0, x1, y, depth=6, k=0.7):
    """Ombra al peu d'un moble arrambat a la paret."""
    cv.darken(x0, y, x1, y + depth, lambda x, yy: k * (1 - (yy - y) / (depth + 1)))


# ─── Portes ────────────────────────────────────────────────────────────────

def in_door(x, y, x0, y0, x1, y1, r=8):
    """Si (x, y) és dins l'obertura (cantons rodons a dalt)."""
    if not (x0 <= x <= x1 and y0 <= y <= y1):
        return False
    dx = max(x0 + r - x, 0, x - (x1 - r))
    dy = max(y0 + r - y, 0)
    return dx * dx + dy * dy <= r * r


def door_frame(cv, x0, y0, x1, y1, ramp=CREAM, lvl=5.2, r=8):
    """Marc d'una porta de vaixell (cantons rodons a dalt), de 3 px, amb ombra a sota de la llinda."""
    for t in range(3):
        for y in range(y0 - t, y1 + 1):
            for x in range(x0 - t, x1 + t + 1):
                if in_door(x, y, x0 - t, y0 - t, x1 + t, y1 + 1, r + t) and not in_door(x, y, x0 - t + 1, y0 - t + 1, x1 + t - 1, y1 + 1, r + t - 1):
                    cv.put(x, y, ramp, lvl - t * 0.8 + (0.6 if y < y0 + r else 0))
    cv.darken(x0 - 4, y1 + 1, x1 + 4, y1 + 3, 0.5)


def sill(cv, x0, x1, y1, ramp=DOORP, lvl=3.0, h=5):
    """El llindar alt de les portes de vaixell (per si entra aigua)."""
    cv.rect(x0, y1 - h, x1, y1, ramp, lvl)
    cv.hline(x0, x1, y1 - h, ramp, lvl + 1.6)
    cv.hline(x0, x1, y1, ramp, lvl - 1.4)


def leaf(cv, x0, y0, x1, y1, ramp=DOORP, lvl=3.6, r=7, handle='right', dogs=False, louvre=True, window=None, seed=0):
    """Fulla tancada: planxa pintada amb plafó, maneta, reixeta de ventilació a baix; `dogs`: palanques
    estanques; `window`: (cx, cy, r, fn) per a un ull de bou."""
    rrect(cv, x0, y0, x1, y1, r, ramp, lambda x, y: lvl - (y - y0) * 0.008 + (hr(x // 4, y // 7, seed) - 0.5) * 0.15)
    rrect(cv, x0 + 4, y0 + 4, x1 - 4, y1 - 4, max(2, r - 3), ramp, lambda x, y: lvl + 0.3 - (y - y0) * 0.008)
    cv.hline(x0 + 6, x1 - 6, y0 + 4, ramp, lvl + 1.3)
    cv.hline(x0 + 6, x1 - 6, y1 - 4, ramp, lvl - 1.1)
    cv.vline(x1 - 4, y0 + 8, y1 - 6, ramp, lvl - 0.8)
    cv.vline(x0 + 4, y0 + 8, y1 - 6, ramp, lvl + 0.8)
    cv.vline(x1, y0 + r, y1, ramp, lvl - 1.6)
    hx = x1 - 9 if handle == 'right' else x0 + 5
    my = (y0 + y1) // 2 + 4
    if dogs:
        for dy in (y0 + 12, my - 4, y1 - 20):
            box(cv, hx + 1, dy, hx + 4, dy + 9, CAB, 3.8)
            cv.put(hx + 2, dy + 1, CAB, 5.6)
        ox = x0 + 4 if handle == 'right' else x1 - 8
        for dy in (y0 + 12, y1 - 20):
            box(cv, ox, dy, ox + 3, dy + 7, CAB, 3.2)
    else:
        # maneta de palanca, de llautó
        box(cv, hx, my - 4, hx + 3, my + 5, BRASS, 2.6)
        cv.rect(hx - 6 if handle == 'right' else hx + 1, my - 1, hx + 2 if handle == 'right' else hx + 9, my, BRASS, 4.2)
        cv.hline(hx - 6 if handle == 'right' else hx + 1, hx + 2 if handle == 'right' else hx + 9, my + 1, BRASS, 1.6)
        cv.put(hx + 1, my + 3, DARK, 0.4)
    if louvre:
        lx0, lx1 = (x0 + x1) // 2 - 8, (x0 + x1) // 2 + 8
        box(cv, lx0, y1 - 18, lx1, y1 - 8, ramp, lvl - 0.4)
        for y in range(y1 - 16, y1 - 9, 2):
            cv.hline(lx0 + 2, lx1 - 2, y, ramp, lvl - 1.8)
            cv.hline(lx0 + 2, lx1 - 2, y + 1, ramp, lvl + 0.8)
    if window:
        cx, cy, wr, fn = window
        porthole(cv, cx, cy, wr, fn, rim=2)


def plaque(cv, cx, y, label, ramp=BRASS, lvl=3.6, ink=(34, 22, 12), cross=False):
    """Placa amb el nom (lletres de 5 px), centrada a `cx`. `cross`: creu vermella al davant."""
    w = text_width(label) + (8 if cross else 0)
    x0 = cx - (w + 6) // 2
    x1 = x0 + w + 5
    box(cv, x0, y, x1, y + 9, ramp, lvl)
    cv.hline(x0 + 1, x1 - 1, y + 1, ramp, lvl + 1.0)
    tx = x0 + 3
    if cross:
        cv.rect(tx + 2, y + 2, tx + 3, y + 7, REDP, 4.0, lit=0.4)
        cv.rect(tx, y + 4, tx + 5, y + 5, REDP, 4.0, lit=0.4)
        tx += 8
    text(cv, label, tx, y + 3, None, 0, flat=ink)
    for bx in (x0 + 1, x1 - 1):
        cv.put(bx, y + 4, ramp, lvl - 1.4)
    return x0, x1


# ─── Ulls de bou i mar de nit ───────────────────────────────────────────────

def night_sea(cv, x, y, cx, cy, r, seed=0):
    """El que es veu per un ull de bou de nit: cel de febrer amb núvols, l'horitzó i el mar fosc."""
    hz = cy + r * 0.15
    if y < hz:
        cl = hr(int((x + seed * 7) // 4), int(y // 2), seed)
        v = 2.0 + (hz - y) / (r * 2) + (0.8 if cl > 0.72 else 0)
        cv.put(x, y, NIGHT, v, lit=0.1)
    else:
        v = 1.6 - (y - hz) / (r * 1.6)
        if math.sin(x * 0.7 + y * 2.3 + seed) > 0.85:
            v += 1.6
        cv.put(x, y, NIGHT, v, lit=0.1)


def porthole(cv, cx, cy, r, fn=None, rim=3, ramp=BRASS, seed=0):
    """Ull de bou de llautó amb cargols i el vidre (fn(cv, x, y) pinta el que es veu a través)."""
    for y in range(cy - r - rim - 1, cy + r + rim + 2):
        for x in range(cx - r - rim - 1, cx + r + rim + 2):
            d = math.hypot(x - cx, y - cy)
            if d <= r:
                if fn:
                    fn(cv, x, y)
                else:
                    night_sea(cv, x, y, cx, cy, r, seed)
            elif d <= r + rim:
                nx, ny = (x - cx) / d, (y - cy) / d
                cv.put(x, y, ramp, 3.2 - nx * 0.9 - ny * 1.1 + (0.6 if d < r + 1 else 0))
    for a in range(30, 360, 60):
        bolt(cv, cx + round(math.cos(math.radians(a)) * (r + rim / 2)),
             cy + round(math.sin(math.radians(a)) * (r + rim / 2)), ramp, 3.6)
    # reflex al vidre
    for i in range(-r // 2, r // 3):
        cv.flat(cx - r // 3 + i, cy - r // 2 - i // 2, mix(cv.get(cx - r // 3 + i, cy - r // 2 - i // 2), (200, 210, 230), 0.35))


DAYSKY = [(92, 98, 104), (116, 122, 128), (140, 146, 150), (162, 168, 170), (184, 188, 190), (206, 208, 208),
          (226, 228, 226)]
DAYSEA = [(46, 54, 60), (62, 72, 78), (80, 90, 96), (100, 110, 114), (122, 130, 134), (150, 156, 158),
          (184, 188, 188)]


def day_sea(cv, x, y, cx, cy, r, seed=0):
    """El que es veu per un ull de bou de dia: cel gris pàl·lid de febrer i el mar gris, amb ratlles d'onada."""
    hz = cy + r * 0.15
    if y < hz:
        cl = hr(int((x + seed * 7) // 5), int(y // 2), seed)
        v = 4.2 + (y - (cy - r)) / (r * 2.2) * 1.4 - (0.7 if cl > 0.75 else 0)
        cv.put(x, y, DAYSKY, v, lit=0.08)
    else:
        v = 4.4 - (y - hz) / (r * 0.9)
        if math.sin(x * 0.7 + y * 2.3 + seed) > 0.8:
            v += 1.2
        cv.put(x, y, DAYSEA, v, lit=0.08)


def day_porthole(cv, cx, cy, r, seed=0):
    """Només el vidre d'un ull de bou (amb el seu reflex), de dia: per a un prop `ulls_dia` damunt de porthole()."""
    for y in range(cy - r, cy + r + 1):
        for x in range(cx - r, cx + r + 1):
            if math.hypot(x - cx, y - cy) <= r:
                day_sea(cv, x, y, cx, cy, r, seed)
    for i in range(-r // 2, r // 3):
        x, y = cx - r // 3 + i, cy - r // 2 - i // 2
        cv.flat(x, y, mix(cv.get(x, y), (236, 240, 244), 0.35))


# ─── Rellotge ───────────────────────────────────────────────────────────────

def second_hand(cv, cx, cy, s, r=4):
    """L'agulla vermella dels segons d'un rellotge de paret (s = 0..59)."""
    a = math.radians(s * 6)
    for d in range(1, r + 1):
        cv.flat(round(cx + math.sin(a) * d), round(cy - math.cos(a) * d), (196, 40, 32))
    cv.flat(cx, cy, (90, 70, 40))


# ─── Tub de veu ─────────────────────────────────────────────────────────────

def voice_tube(cv, cx, y, top=0, label=True):
    """La boca del tub de veu: tub de llautó que baixa del sostre, colze, campana amb tapa i cadeneta."""
    vpipe(cv, cx, top, y - 4, 2, BRASS, 3.0)
    for by in range(top + 26, y - 8, 40):
        box(cv, cx - 3, by, cx + 3, by + 2, CAB, 3.4)
    cv.disc(cx, y, 4, 4, BRASS, lambda nx, ny: 3.4 - nx * 1.2 - ny * 1.0)
    cv.disc(cx, y + 4, 7, 6, BRASS, lambda nx, ny: 3.7 - nx * 1.3 - ny * 1.2)
    cv.disc(cx, y + 4, 5, 4, BRASS, lambda nx, ny: 1.4 + nx * 0.6 + ny * 0.8)
    cv.disc(cx, y + 4, 3, 2, DARK, 0.6)
    for i, yy in enumerate(range(y + 11, y + 18)):
        cv.put(cx + 4 + (i % 2), yy, BRASS, 3.0)
    cv.disc(cx + 6, y + 20, 3, 2, BRASS, 3.8)
    if label:
        box(cv, cx - 7, y + 24, cx + 7, y + 27, BRASS, 3.0)
        for x in range(cx - 5, cx + 6, 2):
            cv.put(x, y + 25, BRASS, 1.4)


# ─── Petites coses ─────────────────────────────────────────────────────────

def extinguisher(cv, x, y):
    """Extintor vermell penjat a la paret (x, y: cantó de dalt a l'esquerra), amb el suport."""
    box(cv, x - 1, y + 6, x + 10, y + 9, CAB, 3.0)
    for yy in range(y + 4, y + 30):
        for xx in range(x, x + 10):
            u = (xx - x - 4.5) / 5
            cv.put(xx, yy, REDP, 3.6 + 1.3 * (-0.3 - u) - 0.7 * u * u)
    cv.disc(x + 4.5, y + 4, 4.5, 2, REDP, 4.2)
    box(cv, x + 2, y, x + 7, y + 3, CAB, 3.4)
    cv.line(x + 7, y + 1, x + 12, y + 3, CAB, 3.0)
    cv.vline(x + 12, y + 3, y + 22, CAB, 2.2)
    box(cv, x + 2, y + 12, x + 7, y + 18, WHITEP, 4.0)


def sign_box(cv, x0, y0, s, ramp=WHITEP, lvl=4.2, ink=(24, 28, 30), pad=2):
    """Un rètol petit de planxa amb lletres."""
    w = text_width(s)
    box(cv, x0, y0, x0 + w + pad * 2 + 1, y0 + 6 + pad * 2, ramp, lvl)
    text(cv, s, x0 + pad + 1, y0 + pad + 2, None, 0, flat=ink)
    return w + pad * 2 + 2


def wear(cv, x0, y0, x1, y1, n, seed=0, k=0.35):
    """Taquetes de desgast i ratlletes de rovell (subtils) a la pintura."""
    for i in range(n):
        x = x0 + int(hr(i, 1, seed) * (x1 - x0))
        y = y0 + int(hr(i, 2, seed) * (y1 - y0))
        ln = 2 + int(hr(i, 3, seed) * 7)
        for yy in range(y, min(y1, y + ln)):
            kk = k * (1 - (yy - y) / ln)
            if kk > B4[yy & 3][x & 3] * 0.6:
                cv.flat(x, yy, mix(cv.get(x, yy), RUST[3], kk))
