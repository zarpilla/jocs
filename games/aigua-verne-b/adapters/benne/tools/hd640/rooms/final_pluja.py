"""
Cinemàtica final: el pati de la granja tres setmanes després, **plovent**. Sala «de lluny» (persones de ≈83 px).

És granja_pati.py dibuixat amb draw(cv, wet=True): el cel tapat i gris, la terra fosca i xopa, els bassals que
reflecteixen el cel, brots verds als solcs i al test, un brot a l'olivera, el pou ple fins a dalt, la bomba de
Verne apagada amb el cartell del banc («BANC DE VESPER»), el panell de la carretera amb el preu nou (AIGUA VESPER
▼, sense xifres). A la porta, la cadira de boga del pare (en Quim hi seu, amb el paraigua tancat).
Props (decorats): `barril_pou` (l'últim barril de la Cantimplora, al costat del pou) i `caixa_ferrum` (la caixa de
fusta amb el segell de Ferrum). ANIMS: `pluja` (la pluja, els esquitxos i els cercles als bassals i al pou).
"""
import math

import hd640  # noqa: F401  (posa la llibreria de dibuix a 640×360)
from PIL import Image

from hd.pix import Canvas, Light, W, H, hr, mix
from hd.rooms.exterior import fbm
from hd640.rooms.terra2_comu import (
    RH, OLIVE, ORANGE, RUSTT, IRONR, PLANK, BLACKT, WATER, text, text_width, shadow)
from hd640.rooms import granja_pati as G

LIGHT = Light(ambient=0.2, vignette=(70, 22), floor_fade=None)
LIGHT.point(320, -120, r=700, k=0.7, power=1.0)          # la llum del cel tapat, que ve de tot arreu


def bg(cv):
    G.draw(cv, wet=True)
    G.cadira(cv)


# ─── Props ──────────────────────────────────────────────────────────────────

WOODF = [(30, 22, 16), (48, 36, 24), (70, 52, 34), (94, 72, 46), (118, 92, 60), (142, 114, 76), (164, 136, 94)]


def barril_pou(cv):
    """L'últim barril de la Cantimplora, al costat del pou: oliva, amb les cèrcols i la franja taronja, el
    rètol de la Vet («NO. PER SI DE CAS.») mig desenganxat, i xop."""
    cx, base, rx, h = 254, 214, 12, 34
    shadow(cv, cx - 2, base + 1, rx + 3, 3, 0.5)
    for y in range(base - h, base + 1):
        bulge = 1 + 0.08 * math.sin((y - base + h) / h * math.pi)
        w = rx * bulge
        for x in range(int(cx - w), int(cx + w) + 1):
            u = (x - cx) / w
            hoop = (y - base + h) in (3, 4, h - 4, h - 3)
            band = h // 2 - 3 <= (y - base + h) <= h // 2 + 1
            lvl = 3.4 + u * 1.2 - abs(u) ** 4 * 1.6 + (0.9 if hoop else 0)
            ramp = ORANGE if band else OLIVE
            if fbm(x / 3, y / 8, 9) > 0.7:
                ramp = RUSTT
            cv.put(x, y, ramp, lvl - (0.6 if band else 0))
        if (y - base + h) % 5 == 0:                                         # la pluja hi regalima
            cv.put(cx + int(rx * 0.5), y, OLIVE, 5.2)
    cv.disc(cx, base - h, rx, 3, OLIVE, lambda nx, ny: 3.0 + nx * 0.6 - ny * 0.4)
    cv.disc(cx, base - h, rx - 2, 2, WATER, lambda nx, ny: 3.6 - ny, lit=0)   # aigua a la tapa
    cv.disc(cx + 5, base - h, 1.6, 1, IRONR, 4.0)                            # el tap
    # el rètol de la Vet, mig desenganxat
    cv.poly([(cx - 9, base - 22), (cx + 3, base - 23), (cx + 4, base - 15), (cx - 8, base - 13)],
            [(150, 140, 120), (196, 188, 166), (226, 220, 200)], 1.6)
    for k in range(3):
        cv.line(cx - 7, base - 21 + k * 2.4, cx + 1, base - 22 + k * 2.4, BLACKT, 1.2)


def caixa_ferrum(cv):
    """La caixa de fusta que arriba de Ferrum: taules clavades, el segell de Ferrum cremat (l'engranatge i el
    martell) i, al damunt, la nota d'en Bru («Per si de cas.») sota una pedra."""
    x0, x1, base, h = 380, 416, 228, 22
    top = base - h
    shadow(cv, (x0 + x1) // 2 - 3, base + 1, 22, 3, 0.55)
    cv.poly([(x0, top), (x1, top), (x1 - 4, top - 6), (x0 - 4, top - 6)], WOODF,
            lambda x, y: 4.0 - (1.4 if (y - top) % 3 == 0 else 0))               # la tapa
    cv.poly([(x0 - 4, top - 6), (x0, top), (x0, base), (x0 - 4, base - 5)], WOODF, 1.8)   # el costat
    cv.rect(x0, top, x1, base, WOODF, lambda x, y: 3.2 - (1.6 if (y - top) % 7 == 0 else 0) +
            (fbm(x / 4, y / 9, 7) - 0.5) * 0.8)
    for sx in (x0 + 1, x1 - 1):
        cv.rect(sx, top, sx, base, WOODF, 4.2)
    cv.line(x0 + 1, top + 1, x1 - 1, base - 1, WOODF, 4.0)                  # la creu de reforç
    # el segell cremat: un engranatge amb un martell
    cx, cy = (x0 + x1) // 2, top + 11
    for a in range(0, 360, 30):
        ar = math.radians(a)
        cv.put(cx + math.cos(ar) * 6, cy + math.sin(ar) * 5, BLACKT, 1.6)
    cv.ring(cx, cy, 4, BLACKT, 1.4, step=20)
    cv.line(cx - 2, cy + 2, cx + 2, cy - 2, BLACKT, 1.0)
    cv.rect(cx + 1, cy - 3, cx + 3, cy - 2, BLACKT, 1.0)
    text(cv, 'FERRUM', cx - text_width('FERRUM') // 2, base - 6, BLACKT, 1.0, lit=0, flat=(40, 28, 20))
    # la nota d'en Bru, sota una pedra
    cv.poly([(x0 + 8, top - 3), (x0 + 20, top - 4), (x0 + 22, top - 1), (x0 + 9, top)],
            [(150, 140, 120), (196, 188, 166), (226, 220, 200)], 1.8)
    cv.disc(x0 + 15, top - 4, 3, 2, [(60, 56, 50), (90, 84, 76), (120, 114, 104)], lambda nx, ny: 1.6 + nx - ny)


PROPS = {'barril_pou': barril_pou, 'caixa_ferrum': caixa_ferrum}


# ─── Animacions ─────────────────────────────────────────────────────────────

_BASE = []


def _base():
    if not _BASE:
        cv = Canvas(light=LIGHT)
        bg(cv)
        _BASE.append(cv.img)
    return _BASE[0]


RAIN_N, RAIN_V, RAIN_P = 20, 13, 260          # fotogrames, píxels per fotograma, període (20 × 13 = 260)
SLANT = 0.22                                  # la pluja cau una mica inclinada (el vent ve de la dreta)


def _frames_pluja():
    """La pluja que cau, els esquitxos a terra i els cercles als bassals i al pou. Cada gota és sempre a la
    mateixa recta inclinada; quan arriba a baix torna a dalt, i en 20 fotogrames tot torna on era."""
    src = _base().load()
    drops = []
    for k in range(420):
        x0 = hr(k, 1) * (W + 60)
        y0 = hr(k, 2) * RAIN_P
        ln = 6 + int(hr(k, 3) * 5)
        near = hr(k, 4) > 0.8                                                # les gotes de més a prop: més llargues
        drops.append((x0, y0, ln + (4 if near else 0), near))
    # els cercles: a l'atzar dins els bassals i al pou, cadascun amb el seu fotograma d'inici
    rings = []
    k = 0
    while len(rings) < 46 and k < 4000:
        k += 1
        x, y = hr(k, 11) * W, 186 + hr(k, 12) * 72
        if G.puddle(x, y) > 0.45:
            rings.append((x, y, int(hr(k, 13) * RAIN_N)))
    for j in range(6):                                                       # el pou, ple fins a dalt
        rings.append((G.WX - 14 + hr(j, 21) * 28, G.WTOP + 3 + hr(j, 22) * 3, int(hr(j, 23) * RAIN_N)))
    splashes = [(hr(k, 31) * W, 196 + hr(k, 32) * 62, int(hr(k, 33) * RAIN_N)) for k in range(70)]
    frames = []
    for i in range(RAIN_N):
        img = Image.new('RGBA', (W, H), (0, 0, 0, 0))
        p = img.load()

        def put(x, y, col, a):
            x, y = int(x), int(y)
            if 0 <= x < W and 0 <= y < RH:
                p[x, y] = mix(src[x, y], col, a) + (255,)
        for x0, y0, ln, near in drops:
            yy = (y0 + i * RAIN_V) % RAIN_P
            for t in range(ln):
                y = yy + t
                x = x0 - SLANT * y
                a = (0.25 + 0.35 * t / ln) * (1.3 if near else 1.0)
                put(x, y, (214, 222, 230), min(0.8, a))
        for x, y, s in rings:                                                 # els cercles creixen 4 fotogrames
            age = (i - s) % RAIN_N
            if age < 4:
                r = 1 + age * 1.6
                for a in range(0, 360, 20 if age < 2 else 12):
                    ar = math.radians(a)
                    put(x + math.cos(ar) * r, y + math.sin(ar) * r * 0.35, (220, 226, 230), 0.5 - age * 0.1)
        for x, y, s in splashes:                                              # els esquitxos, 2 fotogrames
            age = (i - s) % RAIN_N
            if age == 0:
                put(x, y, (200, 206, 210), 0.5)
                put(x - 1, y - 1, (200, 206, 210), 0.45)
                put(x + 1, y - 1, (200, 206, 210), 0.45)
            elif age == 1:
                put(x - 2, y - 1, (200, 206, 210), 0.3)
                put(x + 2, y - 1, (200, 206, 210), 0.3)
        frames.append(img)
    return frames


ANIMS = {'pluja': {'frames': _frames_pluja, 'frameDuration': 70}}


# ─── Geometria (coordenades de 640×360) ─────────────────────────────────────

GEOMETRIA = {
    'things': {},
    'spawns': {'iri': (330, 238), 'vet': (284, 230), 'quim': (133, 197), 'diu': (470, 236)},
    'walkable': G.GEOMETRIA['walkable'],
}
