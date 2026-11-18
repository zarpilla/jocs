"""
Aigua Verne — el despatx del Magnat (pròleg), dibuixat de cara (pla): les peces d'on `proleg_palau.py` (la
cinemàtica en 3D) treu les textures (la taula, la cadira, el focus, la càmera, l'aquari, el panell...).
"""
import functools
import math

import hd640  # noqa: F401  (abans de cap hd.rooms: posa la llibreria a 640×360)
from hd.pix import Canvas, Light, hr, mix
from hd640.rooms.palau_comu import (MARB, ORP, TURQ, CROM, NEGRE, BLANC, VERMELL, RH, _diff, lletres, lletres_c,
                                    espai, terra2, diposit, gota, terra_marbre, motllura, marc_or, vidre, piscina,
                                    escaleta, aigua_aquari, peixos, ombra, negre_barra, panell_preu, panell_valor,
                                    estrelles_frames, fbm)


PERSONA = 100
CEIL = 10
GLASS_Y1 = 196               # on el vidre toca el terra
DESK = (196, 352, 172, 182, 236)   # x0, x1, y del sobre (darrere), y del cantell, y de terra
LAMP = (62, 74)              # el cap del focus
CAMERA = (142, 150)          # el cos de la càmera
AQ = (520, 92, 604, 184)     # el vidre de l'aquari
AQ_FOOT = 232
PANEL = (404, 26, 64, 30)    # el panell del preu: x0, y0, w, h
POOL_TOP = (424, 516, 214)   # el tros de vidre del terra: vora del fons
POOL_BOT = (412, 532, 244)   # vora del davant

_ST = {'focus': True, 'fish_t': 0.0}

LIGHT = Light(ambient=0.25, vignette=(60, 12), floor_fade=(244, 30))
LIGHT.point(300, 120, r=260, k=0.9, squash=1.2, power=1.4)       # la llum perfecta de l'anunci (rebots)
LIGHT.point(562, 140, r=90, k=0.5, power=1.8)                     # la llum blava de l'aquari


# ─── La paret de vidre ──────────────────────────────────────────────────────

MULLS = (8, 120, 232, 344, 456, 568, 632)


def paret_vidre(cv):
    # sostre blanc amb un filet d'or
    cv.rect(0, 0, 639, CEIL, MARB, lambda x, y: 5.0 + y * 0.05)
    motllura(cv, 0, 639, CEIL - 2, h=3)
    # l'espai, Terra-2 (enorme) i el dipòsit
    bright = espai(cv, 0, CEIL + 1, 639, GLASS_Y1 - 1, seed=17, dens=1.2)
    terra2(cv, 170, 410, 290, mask=lambda x, y: y < GLASS_Y1, seed=5, sun=(0.7, -0.5))
    dep = type(cv)(transparent=True)
    diposit(dep, 300, 44, 0.62)
    D = dep.img.load()
    for X, Y, _, _ in cv.pixels(200, CEIL + 1, 399, GLASS_Y1 - 1):                         # (píxels reals)
        if D[X, Y][3]:
            cv.P[X, Y] = D[X, Y][:3] + (255,)
    vidre(cv, 0, CEIL + 1, 639, GLASS_Y1 - 1, k=0.12, seed=40)
    # els muntants d'or i el travesser
    for x in MULLS:
        cv.rect(x - 2, CEIL + 1, x + 2, GLASS_Y1, ORP, lambda xx, yy: 4.4 + (1.2 if xx == x - 2 else -1.0 if xx == x + 2 else 0))
    cv.rect(0, 150, 639, 152, ORP, lambda x, y: 4.6 - (y - 150) * 0.8)
    # el peu del vidre (un sòcol de marbre)
    cv.rect(0, GLASS_Y1 - 6, 639, GLASS_Y1, MARB, lambda x, y: 6.0 - (y - GLASS_Y1 + 6) * 0.3)
    motllura(cv, 0, 639, GLASS_Y1 - 7, h=2)
    return bright


# ─── El focus i la càmera ───────────────────────────────────────────────────

def raig(cv):
    """El raig del focus: una banda de llum càlida que va del focus fins a la taula, i la taca a la taula."""
    lx, ly = LAMP
    tx, ty = 290, 182
    ax, ay = tx - lx, ty - ly
    L = math.hypot(ax, ay)
    for y in range(ly - 10, 240):
        for x in range(lx, 400):
            px, py = x - lx, y - ly
            t = (px * ax + py * ay) / (L * L)
            if t < 0.05 or t > 1.15:
                continue
            perp = abs(px * ay - py * ax) / L
            w = 6 + t * 60
            if perp < w:
                a = 0.24 * (1 - perp / w) ** 0.7 * min(1.0, t * 6) * (1 - max(0.0, t - 1) * 6)
                o = cv.get(x, y)
                cv.flat(x, y, mix(o, (255, 248, 220), a))
    # la taca de llum damunt la taula i a terra
    cv.glow(tx, ty - 4, 70, (255, 250, 230), 0.32)


def focus(cv):
    lx, ly = LAMP
    # el trípode del focus
    for dx in (-18, 0, 18):
        cv.line(lx - 6, ly + 30, lx - 6 + dx, 236, CROM, 3.6 if dx < 0 else 5.0)
    cv.rect(lx - 7, ly + 6, lx - 5, ly + 34, CROM, lambda x, y: 5.4 - (x - lx + 7))
    # el cap: un cilindre negre inclinat cap a la taula, amb les aletes (portes de llum)
    ang = math.atan2(182 - ly, 290 - lx)
    ca, sa = math.cos(ang), math.sin(ang)
    for t in range(-14, 10):
        for s in range(-10, 11):
            x = lx + t * ca - s * sa
            y = ly + t * sa + s * ca
            cv.put(x, y, NEGRE, 2.2 - s * 0.12 + (0.8 if s < -7 else 0))
            cv.put(x + 0.5, y, NEGRE, 2.2 - s * 0.12 + (0.8 if s < -7 else 0))
    # la cara del focus
    fx, fy = lx + 10 * ca, ly + 10 * sa
    for s in range(-9, 10):
        for k in range(2):
            x = fx + k * ca - s * sa
            y = fy + k * sa + s * ca
            if _ST['focus']:
                cv.flat(x, y, (255, 252, 230) if abs(s) < 7 else (250, 220, 150))
            else:
                cv.flat(x, y, (40, 40, 46) if abs(s) < 7 else (70, 70, 76))
    # les aletes
    for sgn in (-1, 1):
        x0, y0 = fx - sgn * 10 * sa, fy + sgn * 10 * ca
        cv.line(x0, y0, x0 + 9 * ca - sgn * 5 * sa, y0 + 9 * sa + sgn * 5 * ca, NEGRE, 3.0)
    if _ST['focus']:
        cv.glow(fx + 3, fy + 2, 22, (255, 250, 220), 0.6)
    # el cable fins a terra
    for k in range(40):
        t = k / 39
        cv.put(lx - 6 + t * 30, 236 - math.sin(t * math.pi) * -2, NEGRE, 1.4)


def camera(cv):
    """La càmera d'anunci: trípode, cos negre, objectiu cap a la taula, el visor i el llum de gravar."""
    cx, cy = CAMERA
    for dx in (-22, 0, 22):
        cv.line(cx, cy + 14, cx + dx, 244, CROM, 3.4 if dx < 0 else 5.2)
        cv.line(cx + 1, cy + 14, cx + dx + 1, 244, CROM, 2.2)
    cv.rect(cx - 2, cy + 8, cx + 2, cy + 16, CROM, 4.4)
    # el cos
    cv.rect(cx - 22, cy - 10, cx + 14, cy + 8, NEGRE, lambda x, y: 2.4 - (y - cy + 10) * 0.08 + (0.8 if y == cy - 10 else 0))
    cv.rect(cx - 18, cy - 18, cx - 2, cy - 11, NEGRE, 2.0)                        # la nansa
    cv.rect(cx - 16, cy - 16, cx - 4, cy - 13, NEGRE, 0.4)
    # l'objectiu
    for x in range(cx + 14, cx + 32):
        r = 6 + (x - cx - 14) * 0.2
        for y in range(int(cy - r), int(cy + r) + 1):
            cv.put(x, y, NEGRE, 2.8 - (y - cy) / r * 1.2 + (1.0 if (x - cx) % 6 == 0 else 0))
    cv.disc(cx + 32, cy, 3, 9, CROM, lambda nx, ny: 2.0 + nx * 2 - ny)
    cv.disc(cx + 32, cy, 1.5, 6, [(20, 30, 60), (50, 70, 140), (120, 160, 230)], lambda nx, ny: 1.2 - ny, lit=0)
    # el visor (a l'esquerra) i el llum vermell
    cv.rect(cx - 30, cy - 8, cx - 22, cy + 2, NEGRE, 1.6)
    cv.disc(cx + 8, cy - 7, 1.6, 1.6, VERMELL, 5.0, lit=0)
    cv.glow(cx + 8, cy - 7, 6, (255, 60, 50), 0.6)
    lletres(cv, 'VERNE', cx - 18, cy - 3, (90, 96, 110))


# ─── Taula, cadira, panell ──────────────────────────────────────────────────

def cadira(cv):
    """La cadira alta de pell blanca, darrere la taula."""
    cx = 276
    top = 102
    for y in range(top, 176):
        w = 22 + min(0, y - top - 10) * 0.0 - max(0, (y - 150)) * 0.12
        for x in range(int(cx - w), int(cx + w) + 1):
            u = (x - cx) / w
            # el capitonat: canals verticals i botons
            chan = (x - cx + 32) % 11 == 0 and y > top + 8
            button = (x - cx + 32) % 11 == 5 and (y - top) % 14 == 7
            v = 6.0 - u * 1.4 - u * u * 1.6 - (1.0 if chan else 0) - (1.4 if button else 0)
            cv.put(x, y, MARB, v)
    cv.disc(cx, top + 2, 22, 9, MARB, lambda nx, ny: 6.8 - ny * 0.8 - nx * 0.8)
    for y in range(top + 4, 176):                                         # el ribet d'or
        cv.put(cx - 23, y, ORP, 4.4)
        cv.put(cx + 23, y, ORP, 3.0)
    for a in range(180, 361, 4):
        cv.put(cx + math.cos(math.radians(a)) * 23, top + 2 + math.sin(math.radians(a)) * 10, ORP, 4.8)


def taula(cv):
    x0, x1, yb, yf, yg = DESK
    ombra(cv, (x0 + x1) // 2, yg + 2, (x1 - x0) // 2 + 12, 5, 0.6)
    # el sobre: una llosa blanca lacada, amb el cantell d'or
    cv.poly([(x0 + 8, yb), (x1 - 8, yb), (x1, yf), (x0, yf)], MARB, lambda x, y: 7.2 - (y - yb) * 0.08)
    cv.rect(x0, yf, x1, yf + 3, ORP, lambda x, y: 5.2 - (y - yf) * 0.6)
    # el cos (un bloc blanc fins a terra, una mica entrat), amb la gota de Verne
    cv.rect(x0 + 10, yf + 4, x1 - 10, yg, MARB, lambda x, y: 5.8 - (y - yf) * 0.012 - (1.0 if x > x1 - 14 else 0))
    cv.rect(x0 + 10, yg - 3, x1 - 10, yg, MARB, 3.4)
    cv.disc((x0 + x1) // 2, yf + 26, 12, 12, ORP, lambda nx, ny: 4.6 - ny - nx * 0.4)
    cv.disc((x0 + x1) // 2, yf + 26, 10, 10, MARB, 6.6)
    gota(cv, (x0 + x1) // 2, yf + 26, 15, lit=1)
    lletres_c(cv, 'VERNE S.A.', (x0 + x1) // 2, yf + 42, (120, 82, 28))
    # damunt: l'interfon de la Sra. Pell, un portaploma d'or i una carpeta
    cv.rect(x0 + 18, yb + 1, x0 + 34, yf - 2, NEGRE, lambda x, y: 2.4 - (y - yb) * 0.1)
    cv.disc(x0 + 30, yb + 3, 1.2, 1.2, [(60, 200, 90), (140, 255, 170)], 1.0, lit=0)
    cv.rect(x1 - 30, yb - 6, x1 - 26, yb + 4, ORP, lambda x, y: 4.6 - (x - x1 + 30) * 0.4)
    cv.line(x1 - 28, yb - 6, x1 - 24, yb - 14, NEGRE, 2.0)
    cv.poly([(x1 - 70, yb + 2), (x1 - 40, yb + 2), (x1 - 38, yf - 2), (x1 - 72, yf - 2)], [(60, 20, 30), (100, 36, 48), (140, 60, 70)], 1.4)


def panell(cv):
    x0, y0, w, h = PANEL
    for x in (x0 + 10, x0 + w - 11):                                     # els cables del sostre
        cv.vline(x, CEIL + 1, y0 - 3, CROM, 4.0)
    panell_preu(cv, x0, y0, w, h)
    # sense número: el panell en espera (uns guions)
    for k in range(3):
        cv.hline(x0 + 10 + k * 8, x0 + 15 + k * 8, y0 + 19, [(60, 20, 10), (120, 40, 14)], 1.0, lit=0)


# ─── El terra i la piscina de sota ──────────────────────────────────────────

def terra(cv):
    terra_marbre(cv, GLASS_Y1 + 1, RH - 1, vp=(320, 0), base=6.2, tile=60)
    # el tros de vidre: s'hi veu la piscina central, buida, molt avall
    (ta, tb, ty), (ba, bb, by) = POOL_TOP, POOL_BOT
    # el marc d'or
    for y in range(ty - 3, by + 4):
        f = (y - ty) / (by - ty)
        a, b = ta + (ba - ta) * f, tb + (bb - tb) * f
        for x in range(int(a) - 4, int(b) + 5):
            cv.put(x, y, ORP, 4.4 + (1.0 if y < ty else -0.8 if y > by else 0))
    # a sota: la piscina vista de dalt, a sis metres (petita), amb les parets que baixen
    for y in range(ty, by + 1):
        f = (y - ty) / (by - ty)
        a, b = ta + (ba - ta) * f, tb + (bb - tb) * f
        for x in range(int(math.ceil(a)), int(b) + 1):
            u = (x - a) / (b - a)
            # el fons de la piscina, sis metres avall: rajola gran amb junta clara i la franja fosca
            gx = (x - 472) * 0.9
            gy = (y - 229) * 1.6
            lvl = 3.6 + (0.9 if gx % 9 < 1 or gy % 9 < 1 else 0) + (hr(int(gx // 9), int(gy // 9), 4) - 0.5) * 0.4
            if abs(x - 484 - (y - 229) * 0.1) < 2.5:
                lvl = 1.2
            # l'ombra que fa el marc a dins (fondària), més fosca a dalt i a l'esquerra
            dt, dl = (y - ty), (x - a)
            if dt < 8:
                lvl -= (8 - dt) * 0.35
            if dl < 6:
                lvl -= (6 - dl) * 0.3
            cv.put(x, y, TURQ, lvl, lit=0.3)
    # l'escala cromada de la piscina, vista de dalt (al fons, a la dreta)
    for k in range(4):
        cv.hline(500, 506, 222 + k * 5, CROM, 5.6, lit=0.3)
    cv.vline(499, 218, 240, CROM, 6.2, lit=0.3)
    cv.vline(507, 218, 240, CROM, 4.4, lit=0.3)
    # el vidre: reflexos
    for y in range(ty, by + 1):
        f = (y - ty) / (by - ty)
        a, b = ta + (ba - ta) * f, tb + (bb - tb) * f
        for x in range(int(math.ceil(a)), int(b) + 1):
            if 8 < (x - a + (by - y) * 1.2) % 50 < 14:
                cv.flat(x, y, mix(cv.get(x, y), (230, 255, 250), 0.25))


# ─── L'aquari ───────────────────────────────────────────────────────────────

def vidre_aquari(cv):
    x0, y0, x1, y1 = AQ
    for y in range(y0 + 2, y1):
        for x in range(x0, x1 + 1):
            s = (x - x0) * 1.0 - (y - y0) * 0.35
            if 6 < s % 70 < 10 or 14 < s % 70 < 15:
                cv.flat(x, y, mix(cv.get(x, y), (230, 248, 255), 0.35))


def aquari(cv):
    x0, y0, x1, y1 = AQ
    ombra(cv, (x0 + x1) // 2, AQ_FOOT + 2, (x1 - x0) // 2 + 10, 4, 0.6)
    cv.rect(x0 - 4, y1 + 1, x1 + 4, AQ_FOOT, MARB, lambda x, y: 5.6 - (x - x0) * 0.02 - (1.2 if y == AQ_FOOT else 0))
    motllura(cv, x0 - 5, x1 + 5, y1 + 1, h=3)
    motllura(cv, x0 - 6, x1 + 6, AQ_FOOT - 3, h=3, lvl=3.8)
    px0, px1, py0, py1 = x0 + 14, x1 - 14, y1 + 12, y1 + 24
    cv.rect(px0, py0, px1, py1, ORP, lambda x, y: 4.8 - (y - py0) * 0.08)
    marc_or(cv, px0, py0, px1, py1, t=1, lvl=4.0)
    lletres_c(cv, 'AQUA', (px0 + px1) // 2, py0 + 4, (70, 40, 14))
    aigua_aquari(cv, x0, y0, x1, y1, _ST['fish_t'])
    peixos(cv, x0, y0, x1, y1, _ST['fish_t'])
    vidre_aquari(cv)
    for x in (x0 - 3, x1 + 1):
        cv.rect(x, y0 - 8, x + 2, y1, ORP, lambda xx, yy: 4.6 + (1.0 if xx == x else -0.8 if xx == x + 2 else 0))
    cv.rect(x0 - 5, y0 - 10, x1 + 5, y0 - 1, ORP, lambda x, y: 4.0 - (y - y0 + 10) * 0.1)
    motllura(cv, x0 - 6, x1 + 6, y0 - 12, h=3, lvl=5.0)
    cv.glow((x0 + x1) // 2, (y0 + y1) // 2, 64, (120, 200, 255), 0.18)
