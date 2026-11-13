"""
Aigua Verne — `palau_control` (P): la sala de control, sota la piscina central del palau.

  - el sostre és el fons de vidre de la piscina central (buida): bigues d'acer, el vidre, i a través seu la rajola
    turquesa i la claror de la galeria de dalt; una escala cromada que penja;
  - el **tauler** de les vàlvules d'emergència: tres **panys** grans (rètols T2, AQUA, FERRUM), cadascun amb el
    seu rellotge i el seu llum (decorats `obert_t2`, `obert_aqua`, `obert_ferrum`: llum verd, l'agulla al màxim i
    la clau girada); a sobre, les pantalletes amb els tres dipòsits;
  - la **palanca** vermella «RESERVA» davant el tub gruixut de la reserva del Magnat (decorat `reserva_oberta`);
  - l'**ascensor** de servei (a l'esquerra), l'**interfon** i, a la cantonada del sostre, la **càmera** (decorat
    `flors_camera`: flors de plàstic que la tapen).
"""
import functools
import math

import hd640  # noqa: F401  (abans de cap hd.rooms: posa la llibreria a 640×360)
from hd.pix import Canvas, Light, hr, mix
from hd.rooms.arenga import box, bolt, vpipe, hpipe
from hd640.rooms.palau_comu import (GRIS, CROM, BLANC, BLAU, TURQ, VERMELL, VERD, LED, ORP, NEGRE, MARB, RH, _diff,
                                    lletres, lletres_c, gota, ombra, negre_barra, fbm, escaleta, diposit)
from hd640.rooms.palau_servei import PLAST, YELLOW, flor

PERSONA = 100
CEIL_Y = 64                       # on el sostre de vidre toca la paret del fons
FLOOR_Y = 226
VP = (320, 150)
LIFT = (22, 100, 104, FLOOR_Y)
DESK = (150, 100, 470, 214)        # el tauler (x0, y0, x1, y1)
LOCKS = {'t2': (210, 'T2'), 'aqua': (310, 'AQUA'), 'ferrum': (410, 'FERRUM')}
LOCK_Y = 168                      # el centre dels panys
DIAL_Y = 130                      # el centre dels rellotges
LEVER = (528, 156)                # l'eix de la palanca
CAM = (562, 76)
INTER = (128, 146)

# l'acer blau fosc de la sala (més elegant que el servei: és la sala del Magnat)
ACER = [(8, 12, 18), (14, 20, 28), (22, 30, 40), (32, 42, 54), (44, 56, 70), (60, 74, 90), (80, 96, 112),
        (106, 122, 138), (140, 154, 168)]

LIGHT = Light(ambient=-0.2, vignette=(60, 10), floor_fade=(240, 40))
LIGHT.point(320, -20, r=300, k=2.2, squash=0.8, power=1.3)          # la claror que baixa per la piscina
LIGHT.point(310, 150, r=170, k=0.8, squash=1.4, power=1.5)          # el tauler
LIGHT.point(528, 150, r=80, k=0.6, power=1.6)                       # la palanca


# ─── El sostre: el fons de vidre de la piscina ──────────────────────────────

def _ceil_uv(x, y):
    """Coordenades sobre el pla del sostre (u: de costat; v: de profunditat, 0 a dalt de tot)."""
    vx, vy = VP
    d = vy - y
    u = vx + (x - vx) * (vy - 0) / d
    v = (vy / d - 1) * 100
    return u, v


def sostre(cv):
    vx, vy = VP
    for y in range(0, CEIL_Y + 1):
        for x in range(640):
            u, v = _ceil_uv(x, y)
            # bigues: longitudinals cada 128 px (al pla de dalt de tot) i transversals cada 40 unitats de v
            bu = (u + 4) % 128 < 8
            bv = (v + 3) % 40 < 6
            if bu or bv:
                edge = (u + 4) % 128 < 2 or (v + 3) % 40 < 1.4
                cv.put(x, y, ACER, 4.6 + (1.2 if edge else 0) - v * 0.01)
                continue
            # a través del vidre: la rajola de la piscina vista de sota, i la llum de la galeria al mig
            tile = (int(u // 16) + int(v // 9)) % 2
            joint = u % 16 < 1.2 or v % 9 < 0.9
            glow = max(0.0, 1 - abs(u - 320) / 300) * max(0.0, 1 - abs(v - 60) / 90)
            lvl = 3.2 + glow * 2.4 + tile * 0.3 + (1.0 if joint else 0)
            cv.put(x, y, TURQ, lvl, lit=0.3)
            # reflexos del vidre, en diagonal
            if 30 < (u - v * 1.6) % 180 < 44:
                o = cv.get(x, y)
                cv.flat(x, y, mix(o, (220, 255, 250), 0.18))
    # el forat de dalt de la piscina: la galeria, blanca i lluminosa, al fons
    for y in range(0, 22):
        for x in range(232, 409):
            u, v = _ceil_uv(x, y)
            if 250 < u < 390 and v < 22 and not ((u + 4) % 128 < 8 or (v + 3) % 40 < 6):
                cv.put(x, y, MARB, 7.0 - v * 0.05, lit=0)
    cv.glow(320, 8, 70, (240, 255, 250), 0.25)
    # l'escala cromada de la piscina, que es veu penjar per sobre del vidre
    for k in range(5):
        cv.hline(470 + k * 2, 486 + k * 2, 6 + k * 6, CROM, 6.0)
    cv.line(468, 0, 478, 30, CROM, 6.4)
    cv.line(486, 0, 496, 30, CROM, 5.0)
    # la junta amb la paret del fons
    cv.hline(0, 639, CEIL_Y, ACER, 1.4)
    cv.hline(0, 639, CEIL_Y + 1, ACER, 6.0)


# ─── Parets i terra ─────────────────────────────────────────────────────────

def paret(cv):
    for y in range(CEIL_Y + 2, FLOOR_Y):
        for x in range(640):
            seam = (x - 12) % 104
            v = 3.6 + (fbm(x / 70, y / 50, 6) - 0.5) * 0.5 - (y - CEIL_Y) * 0.004
            if seam < 1:
                v -= 1.8
            elif seam < 2:
                v += 0.8
            if (y - CEIL_Y) % 54 == 0:
                v -= 1.2
            cv.put(x, y, ACER, v)
    for x in range(12, 640, 104):
        for y in range(CEIL_Y + 10, FLOOR_Y - 6, 27):
            bolt(cv, x + 4, y, ACER, 4.4)
            bolt(cv, x - 5, y, ACER, 4.4)
    # sòcol i tira de llum turquesa arran de terra
    cv.rect(0, FLOOR_Y - 10, 639, FLOOR_Y - 1, ACER, lambda x, y: 2.2 - (y - FLOOR_Y + 10) * 0.05)
    cv.hline(0, 639, FLOOR_Y - 10, TURQ, 5.0, lit=0)


def terra(cv):
    """Reixa d'acer (graella), en perspectiva."""
    vx, vy = VP
    for y in range(FLOOR_Y, RH):
        d = y - vy
        v = 6000 / d
        for x in range(640):
            u = vx + (x - vx) * 100 / d
            gx = (u * 0.5) % 8 < 1.2
            gy = (v * 4) % 6 < 1.4
            lvl = 2.6 + (y - FLOOR_Y) * 0.02 + (1.2 if gx or gy else 0) + (hr(int(u // 3), int(v * 2)) - 0.5) * 0.3
            cv.put(x, y, ACER, lvl)
    cv.hline(0, 639, FLOOR_Y, ACER, 0.6)


# ─── Ascensor, interfon, càmera ─────────────────────────────────────────────

def ascensor(cv):
    x0, y0, x1, y1 = LIFT
    cv.rect(x0 - 8, y0 - 18, x1 + 8, y1, ACER, lambda x, y: 5.0 - (0.8 if x > x1 else 0))
    box(cv, x0 - 8, y0 - 18, x1 + 8, y0 - 1, ACER, 5.4)
    cv.rect(x0 + 24, y0 - 14, x1 - 24, y0 - 5, NEGRE, 0.6, lit=0)
    lletres_c(cv, 'P-3', (x0 + x1) // 2, y0 - 12, LED[3])
    mid = (x0 + x1) // 2
    for y in range(y0, y1):
        for x in range(x0, x1 + 1):
            refl = 0.8 if 10 < (x - x0 - (y - y0) * 0.3) % 60 < 22 else 0
            v = 3.4 + refl - (y - y0) * 0.006 + (hr(x, y // 9, 5) - 0.5) * 0.25
            if x == mid:
                v = 1.0
            elif x == mid + 1:
                v = 6.0
            cv.put(x, y, CROM, v)
    cv.rect(x0, y1 - 12, x1, y1 - 1, CROM, lambda x, y: 3.0)
    cv.hline(x0, x1, y1 - 12, CROM, 5.6)
    # el botó (aquí no cal targeta per pujar)
    cv.disc(x1 + 14, 150, 4, 4, CROM, lambda nx, ny: 5 - ny)
    cv.disc(x1 + 14, 150, 2, 2, LED, 3.4, lit=0)


def interfon(cv):
    x, y = INTER
    box(cv, x - 10, y - 22, x + 10, y + 22, CROM, 4.4)
    for k in range(6):                                                   # la reixeta de l'altaveu
        cv.hline(x - 6, x + 6, y - 16 + k * 3, NEGRE, 0.8, lit=0)
    cv.disc(x, y + 6, 3, 3, VERMELL, lambda nx, ny: 4.2 - ny, lit=0.3)  # el botó de parlar
    cv.rect(x - 6, y + 13, x + 6, y + 17, NEGRE, 1.2, lit=0)
    lletres_c(cv, 'PARLA', x, y + 25, (110, 130, 150))
    cv.disc(x + 6, y - 19, 1, 1, VERD, 3.4, lit=0)


def camera(cv):
    """La càmera de seguretat, a la cantonada: braç a la paret, cos blanc, objectiu i llum vermell."""
    cx, cy = CAM
    cv.rect(cx + 18, cy - 14, cx + 24, cy + 6, ACER, 4.6)                 # la placa
    cv.line(cx + 18, cy - 4, cx + 8, cy - 2, CROM, 4.8)
    cv.line(cx + 18, cy - 3, cx + 8, cy - 1, CROM, 3.0)
    cv.poly([(cx - 16, cy - 6), (cx + 10, cy - 8), (cx + 12, cy + 2), (cx - 14, cy + 6)], BLANC,
            lambda x, y: 5.4 - (y - cy + 8) * 0.25)
    cv.hline(cx - 14, cx + 10, cy - 8, BLANC, 7.0)
    cv.disc(cx - 16, cy, 4, 5, NEGRE, lambda nx, ny: 1.2 + nx * 0.6)
    cv.disc(cx - 17, cy - 1, 1.6, 1.6, BLAU, 4.0, lit=0)
    cv.disc(cx + 4, cy - 3, 1.2, 1.2, VERMELL, 5.0, lit=0)
    cv.glow(cx + 4, cy - 3, 5, (255, 60, 50), 0.6)


def flors_camera(cv):
    """En Nil hi ha posat flors de plàstic al davant («Feien pols. Les poso aquí.»)."""
    cx, cy = CAM
    # el gerro, falcat al braç
    cv.poly([(cx - 4, cy + 4), (cx + 8, cy + 4), (cx + 6, cy + 16), (cx - 2, cy + 16)], BLANC,
            lambda x, y: 5.6 - (x - cx) * 0.1)
    cv.hline(cx - 5, cx + 9, cy + 3, BLANC, 6.8)
    pts = [(-20, -2, 'r'), (-15, -9, 'y'), (-18, 6, 'm'), (-9, -4, 'o'), (-11, 4, 'b'), (-4, -10, 'r'),
           (-2, -2, 'g'), (-24, 2, 'y'), (2, -6, 'm')]
    for dx, dy, c in pts:
        cv.line(cx + 2, cy + 4, cx + dx, cy + dy, PLAST['g'], 1.8, lit=0.4)
    for k, (dx, dy, c) in enumerate(pts):
        if c == 'g':
            cv.disc(cx + dx, cy + dy, 3, 1.4, PLAST['g'], 2.6, lit=0.4)
        else:
            flor(cv, cx + dx, cy + dy, c, s=1.2)


# ─── El tauler ──────────────────────────────────────────────────────────────

def pantalletes(cv, oberts=()):
    """Tres pantalletes a sobre del tauler, amb els dipòsits orbitals i el nivell."""
    for k, (key, (x, lab)) in enumerate(LOCKS.items()):
        x0, y0, x1, y1 = x - 34, 72, x + 34, 94
        box(cv, x0 - 3, y0 - 3, x1 + 3, y1 + 3, ACER, 4.2)
        cv.rect(x0, y0, x1, y1, [(4, 14, 18), (8, 26, 30), (14, 44, 46), (24, 70, 68)], 1.0, lit=0)
        dep = Canvas(transparent=True)
        diposit(dep, x - 6, y0 + 12, 0.26)
        D = dep.img.load()
        for yy in range(y0 + 1, y1):
            for xx in range(x0 + 1, x1):
                if D[xx, yy][3]:
                    c = D[xx, yy]
                    cv.flat(xx, yy, (c[0] // 3, min(255, c[1] // 2 + 60), min(255, c[2] // 2 + 50)))
        # la barra del nivell (ple: verd; buidant-se: ...)
        open_ = key in oberts
        for j in range(10):
            col = (40, 220, 120) if not open_ or j < 2 else (24, 50, 50)
            cv.rect(x1 - 7, y1 - 4 - j * 2, x1 - 3, y1 - 4 - j * 2, [col], 0, lit=0)
        lletres(cv, lab, x0 + 3, y1 - 7, (120, 220, 190))


def rellotge(cv, cx, cy, frac, r=15):
    """Un manòmetre: esfera blanca, marques, la zona verda al màxim i l'agulla (frac 0..1)."""
    cv.disc(cx, cy, r + 3, r + 3, CROM, lambda nx, ny: 5.0 - ny * 1.6 - nx * 0.6)
    cv.disc(cx, cy, r, r, BLANC, lambda nx, ny: 6.4 - ny * 0.8)
    for k in range(11):
        a = math.radians(210 - k * 24)
        for rr in range(r - 4 if k % 5 == 0 else r - 2, r):
            cv.flat(cx + round(math.cos(a) * rr), cy - round(math.sin(a) * rr), (30, 34, 40))
    for k in range(8, 11):                                               # la zona verda
        a = math.radians(210 - k * 24)
        cv.flat(cx + round(math.cos(a) * (r - 1)), cy - round(math.sin(a) * (r - 1)), (40, 190, 90))
    for k in range(0, 3):                                                # la zona vermella
        a = math.radians(210 - k * 24)
        cv.flat(cx + round(math.cos(a) * (r - 1)), cy - round(math.sin(a) * (r - 1)), (200, 40, 30))
    a = math.radians(210 - frac * 240)
    for t in range(0, r - 2):
        cv.flat(cx + round(math.cos(a) * t), cy - round(math.sin(a) * t), (200, 30, 26))
    cv.disc(cx, cy, 1.6, 1.6, NEGRE, 1.0, lit=0)
    # la lluentor del vidre
    cv.flat(cx - r // 2, cy - r // 2, (255, 255, 255))
    cv.flat(cx - r // 2 + 1, cy - r // 2, (220, 230, 236))


def pany(cv, key, obert=False):
    """Un pany: placa amb el rètol, el manòmetre, el bombí gran (amb la clau si és obert) i el llum."""
    x, lab = LOCKS[key]
    # la placa de llautó del rètol
    cv.rect(x - 24, 108, x + 24, 116, ORP, lambda xx, yy: 4.6 - (yy - 108) * 0.15)
    marc_or_simple(cv, x - 24, 108, x + 24, 116)
    lletres_c(cv, lab, x, 110, (50, 30, 10))
    rellotge(cv, x, DIAL_Y + 4, 0.96 if obert else 0.06)
    # el bombí: un disc de crom gros, amb l'escut negre
    cv.disc(x, LOCK_Y, 14, 14, CROM, lambda nx, ny: 5.4 - ny * 1.8 - nx * 0.8)
    cv.disc(x, LOCK_Y, 10, 10, CROM, lambda nx, ny: 3.2 + ny * 1.4 + nx * 0.6)
    cv.disc(x, LOCK_Y, 6, 6, NEGRE, lambda nx, ny: 1.0 + ny * 0.8)
    if obert:
        # la clau de tres dents (de Ferrum), ficada i girada 90 graus
        cv.rect(x - 2, LOCK_Y - 9, x + 2, LOCK_Y + 9, ORP, lambda xx, yy: 4.6 - (xx - x) * 0.4)
        cv.disc(x, LOCK_Y - 14, 6, 5, ORP, lambda nx, ny: 5.0 - ny * 1.4 - nx * 0.6)
        cv.disc(x, LOCK_Y - 14, 2, 2, ACER, 1.0)
        cv.hline(x - 3, x + 3, LOCK_Y + 9, ORP, 3.2)
        for k in (-8, 8):                                                # les marques: obert
            pass
    else:
        cv.rect(x - 1, LOCK_Y - 4, x + 1, LOCK_Y + 4, NEGRE, 0.2, lit=0)   # la ranura, vertical
    # TANCAT · OBERT
    lletres(cv, 'T', x - 22, LOCK_Y - 2, (200, 80, 60))
    lletres(cv, 'O', x + 19, LOCK_Y - 2, (80, 200, 120))
    # el llum
    col = VERD if obert else VERMELL
    cv.disc(x, LOCK_Y + 26, 5, 5, ACER, 2.0)
    cv.disc(x, LOCK_Y + 26, 3.5, 3.5, col, lambda nx, ny: 4.4 - ny - nx * 0.4, lit=0)
    cv.glow(x, LOCK_Y + 26, 12, (90, 255, 140) if obert else (255, 60, 40), 0.5)


def marc_or_simple(cv, x0, y0, x1, y1):
    cv.hline(x0, x1, y0, ORP, 6.0)
    cv.hline(x0, x1, y1, ORP, 2.4)
    cv.vline(x0, y0, y1, ORP, 5.4)
    cv.vline(x1, y0, y1, ORP, 2.8)


def tauler(cv):
    x0, y0, x1, y1 = DESK
    ombra(cv, (x0 + x1) // 2, FLOOR_Y + 2, (x1 - x0) // 2 + 10, 4, 0.7)
    # el moble: un tauler inclinat a dalt (cap a nosaltres) i un cos fins a terra
    cv.rect(x0, y0, x1, y1, ACER, lambda x, y: 4.0 - (y - y0) * 0.006)
    box(cv, x0, y0, x1, y1, ACER, 4.0)
    box(cv, x0 - 6, y1 - 4, x1 + 6, y1 + 4, ACER, 4.6)                  # el sobre del pupitre
    cv.rect(x0 - 2, y1 + 5, x1 + 2, FLOOR_Y - 1, ACER, lambda x, y: 2.4 - (y - y1) * 0.02)
    cv.hline(x0 - 6, x1 + 6, y1 - 4, CROM, 6.0)
    # botons i palanquetes al pupitre
    for k, x in enumerate(range(x0 + 10, x1 - 6, 14)):
        c = (LED, VERD, BLAU, YELLOW)[k % 4]
        cv.rect(x, y1 - 2, x + 6, y1 + 1, c, 2.6 + (k % 3) * 0.6, lit=0.4)
    # títol del tauler
    cv.rect(x0 + 90, y0 - 3, x1 - 90, y0 + 7, NEGRE, 0.6, lit=0)
    lletres_c(cv, 'VÀLVULES D\'EMERGÈNCIA', (x0 + x1) // 2, y0 + 2, (220, 190, 120))
    # separadors entre panys
    for x in (260, 360):
        cv.vline(x, y0 + 10, y1 - 8, ACER, 2.0)
        cv.vline(x + 1, y0 + 10, y1 - 8, ACER, 5.0)
    for key in LOCKS:
        pany(cv, key, obert=False)


# ─── La reserva ─────────────────────────────────────────────────────────────

def tub_reserva(cv):
    """El tub gruixut de la reserva del Magnat: puja del terra cap al sostre (cap a la piscina central)."""
    px = 606
    vpipe(cv, px, CEIL_Y - 4, FLOOR_Y, 14, BLANC, 4.6, bands=(90, 180), band_ramp=BLAU)
    for y in (CEIL_Y + 6, 140, FLOOR_Y - 12):
        cv.rect(px - 17, y, px + 17, y + 4, CROM, lambda x, yy: 4.6 + (1.0 if yy == y else -0.6))
    gota(cv, px, 112, 14, lit=1)
    lletres_c(cv, 'RESERVA', px, 122, (30, 50, 110))
    lletres_c(cv, 'PRIVADA', px, 128, (30, 50, 110))
    # la vàlvula que va de la palanca al tub
    hpipe(cv, 548, px - 15, LEVER[1] + 30, 4, CROM, 4.2)


def placa_palanca(cv):
    lx, ly = LEVER
    # placa amb franges de perill
    x0, y0, x1, y1 = lx - 20, ly - 56, lx + 20, ly + 44
    for y in range(y0, y1 + 1):
        for x in range(x0, x1 + 1):
            stripe = ((x + y) // 6) % 2
            edge = x - x0 < 4 or x1 - x < 4 or y - y0 < 4 or y1 - y < 4
            if edge:
                cv.put(x, y, YELLOW if stripe else NEGRE, 3.4 if stripe else 1.0)
            else:
                cv.put(x, y, ACER, 3.0)
    box(cv, x0 + 4, y0 + 4, x1 - 4, y1 - 4, ACER, 3.2)
    cv.rect(lx - 18, y0 - 12, lx + 18, y0 - 3, VERMELL, 3.0)
    lletres_c(cv, 'RESERVA', lx, y0 - 10, (255, 240, 220))
    # la guia de la palanca
    cv.rect(lx - 2, ly - 40, lx + 2, ly + 30, NEGRE, 0.6, lit=0)
    lletres(cv, 'TANCAT', lx - 14, y0 + 7, (200, 80, 60))
    lletres(cv, 'OBERT', lx - 10, y1 - 12, (80, 200, 120))


def palanca(cv, oberta=False):
    lx, ly = LEVER
    placa_palanca(cv)
    # el mànec: una barra cromada amb el pom vermell, a dalt (tancada) o a baix (oberta)
    py = ly - 36 if not oberta else ly + 26
    cv.disc(lx, ly, 6, 6, CROM, lambda nx, ny: 5.0 - ny * 1.4)
    cv.line(lx - 1, ly, lx - 1, py, CROM, 6.0)
    cv.line(lx, ly, lx, py, CROM, 4.6)
    cv.line(lx + 1, ly, lx + 1, py, CROM, 3.0)
    cv.disc(lx, py, 8, 7, VERMELL, lambda nx, ny: 4.6 - ny * 1.6 - nx * 0.8)
    cv.flat(lx - 3, py - 3, (255, 200, 180))
    # el llum de la reserva
    col = VERD if oberta else VERMELL
    cv.disc(lx + 28, ly - 50, 4, 4, ACER, 2.0)
    cv.disc(lx + 28, ly - 50, 3, 3, col, 4.4, lit=0)
    cv.glow(lx + 28, ly - 50, 8, (90, 255, 140) if oberta else (255, 60, 40), 0.5)


# ─── Composició ─────────────────────────────────────────────────────────────

def bg(cv):
    sostre(cv)
    paret(cv)
    terra(cv)
    ascensor(cv)
    interfon(cv)
    pantalletes(cv)
    tauler(cv)
    tub_reserva(cv)
    palanca(cv)
    camera(cv)
    negre_barra(cv)


@functools.lru_cache(maxsize=None)
def _base():
    cv = Canvas(light=LIGHT)
    bg(cv)
    return cv.img


def _obert(key):
    def fn(cv):
        pany(cv, key, obert=True)
    return fn


PROPS = {'obert_t2': _obert('t2'), 'obert_aqua': _obert('aqua'), 'obert_ferrum': _obert('ferrum'),
         'reserva_oberta': lambda cv: palanca(cv, oberta=True), 'flors_camera': flors_camera}


ANIMS = {}


# ─── Geometria (640×360) ────────────────────────────────────────────────────

GEOMETRIA = {
    'things': {
        'ascensor': {'rect': (14, 82, 112, FLOOR_Y), 'walk': (64, 240)},
        'interfon': {'rect': (116, 122, 140, 176), 'walk': (130, 240)},
        'pany_t2': {'rect': (162, 102, 258, 200), 'walk': (210, 240)},
        'pany_aqua': {'rect': (262, 102, 358, 200), 'walk': (310, 240)},
        'pany_ferrum': {'rect': (362, 102, 458, 200), 'walk': (410, 240)},
        'palanca': {'rect': (506, 94, 550, 202), 'walk': (528, 242)},
        'camera': {'rect': (540, 62, 590, 92), 'walk': (560, 242)},
    },
    'spawns': {'vet': (300, 248)},
    'walkable': [(6, 234), (634, 234), (634, 257), (6, 257)],
}
