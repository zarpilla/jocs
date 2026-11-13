"""
Peces comunes del palau orbital del Magnat Verne (pròleg, galeria, saló, servei i sala de control).

Blanc i or, vidre, l'espai negre per les finestres (amb Terra-2 i un dels dipòsits orbitals: un cilindre blanc amb
la gota blava de Verne), les piscines buides de rajola turquesa amb escales cromades i l'aquari dels trenta-tres
peixos platejats. Aquí hi ha les rampes, l'espai, el planeta, el dipòsit, el marbre, les columnes, les piscines,
l'aquari (amb els peixos que neden), el panell del preu i la lletra petita.
"""
import math

import hd640  # noqa: F401  (posa la llibreria de dibuix a 640×360)
from hd640 import W, H
from hd.pix import Canvas, hr, mix, B4, GOLD  # noqa: F401
from hd.rooms.comu import _diff, text, text_width  # noqa: F401
from hd.rooms.exterior import fbm, smooth  # noqa: F401

RH = 260                    # la sala acaba aquí; a sota, la barra de verbs (negre)

# ─── Rampes (fosc → clar) ───────────────────────────────────────────────────
# El marbre blanc del palau: lleugerament càlid, amb ombres gris perla.
MARB = [(46, 44, 50), (78, 76, 82), (112, 108, 112), (146, 142, 142), (176, 172, 168), (200, 196, 190),
        (220, 216, 208), (236, 232, 224), (248, 246, 238), (255, 254, 250)]
# L'or (llautó polit): de bru a groc pàl·lid.
ORP = [(40, 24, 12), (78, 50, 20), (120, 82, 28), (164, 120, 40), (204, 160, 58), (232, 196, 92),
       (248, 226, 150), (255, 246, 210)]
# La rajola turquesa de les piscines (buides): de verd-blau fosc a aigua clara.
TURQ = [(8, 34, 44), (12, 56, 66), (18, 84, 92), (28, 114, 118), (44, 146, 144), (72, 180, 172),
        (118, 212, 200), (176, 238, 226), (226, 252, 244)]
# L'aigua (piscines plenes, l'aquari): blau més profund.
AIGUA = [(6, 22, 48), (10, 40, 80), (16, 64, 112), (26, 94, 144), (44, 128, 176), (74, 164, 204),
         (124, 202, 230), (190, 236, 250), (240, 252, 255)]
# El crom: freds, molt de contrast.
CROM = [(20, 24, 32), (44, 50, 62), (76, 84, 98), (114, 124, 138), (156, 166, 178), (198, 206, 214),
        (232, 238, 242), (255, 255, 255)]
# L'espai: negre blavós.
ESPAI = [(1, 1, 5), (3, 3, 10), (6, 6, 17), (10, 10, 26), (16, 15, 36), (24, 20, 46), (34, 26, 56)]
# Terra-2 des de l'espai: pols ocre (el costat fosc, gairebé negre).
OCRE = [(14, 8, 8), (34, 20, 14), (62, 38, 22), (98, 64, 34), (136, 94, 50), (172, 126, 70), (202, 160, 98),
        (226, 192, 132), (242, 222, 172)]
# El blanc del dipòsit orbital i de les màquines de Verne (blanc fred).
BLANC = [(40, 46, 58), (72, 80, 94), (110, 118, 132), (150, 156, 168), (186, 190, 200), (214, 218, 226),
         (234, 236, 242), (250, 251, 254)]
# La gota de Verne.
BLAU = [(8, 22, 60), (14, 44, 110), (26, 76, 170), (54, 122, 222), (120, 180, 248), (196, 228, 255)]
# Els peixos platejats.
PLATA = [(60, 70, 84), (112, 124, 138), (168, 178, 188), (214, 222, 228), (246, 250, 252)]
# El vidre fosc dels finestrals (l'espai a través d'un vidre amb reflexos).
NEGRE = [(8, 8, 10), (18, 18, 22), (30, 30, 36), (46, 46, 54), (66, 66, 76)]
LED = [(30, 6, 4), (90, 20, 10), (180, 60, 20), (250, 128, 40), (255, 204, 130)]
VERMELL = [(30, 4, 6), (70, 10, 12), (120, 18, 18), (170, 30, 26), (214, 56, 40), (244, 110, 84), (255, 180, 150)]
VERD = [(4, 24, 10), (8, 60, 24), (20, 120, 50), (50, 190, 90), (140, 250, 170), (220, 255, 230)]
# El gris del servei (parets llises, funcional).
GRIS = [(18, 20, 24), (32, 34, 40), (48, 50, 56), (66, 68, 74), (86, 88, 94), (108, 110, 114), (130, 132, 134),
        (154, 156, 156), (180, 182, 180), (206, 208, 204)]
# Vellut granat (cadires, cortines).
GRANAT = [(20, 4, 10), (42, 8, 18), (70, 14, 28), (102, 22, 38), (136, 34, 50), (170, 54, 66), (200, 86, 92)]

STAR_W = (236, 240, 255)


# ─── Lletres ────────────────────────────────────────────────────────────────

def lletres(cv, s, x, y, col, mirror=False):
    """Text amb la lletra petita de 5 px (comu.text), d'un color pla."""
    return text(cv, s, x, y, None, 0, flat=col, mirror=mirror)


def lletres_c(cv, s, cx, y, col):
    """Text centrat a cx."""
    return lletres(cv, s, cx - text_width(s) // 2, y, col)


def lletres_grans(cv, s, x, y, col, k=2):
    """La lletra petita ampliada ×k (números grans de les pantalles)."""
    tmp = Canvas(text_width(s) + 2, 10, transparent=True)
    text(tmp, s, 0, 3, None, 0, flat=(255, 255, 255))
    P = tmp.img.load()
    for j in range(10):
        for i in range(tmp.w):
            if P[i, j][3]:
                for dy in range(k):
                    for dx in range(k):
                        cv.flat(x + i * k + dx, y + (j - 3) * k + dy, col)
    return tmp.w * k


def triangle(cv, x, y, h, col, amunt=True):
    """▲ o ▼ de h files, amb la punta a (x, y) o a (x, y + h - 1)."""
    for j in range(h):
        w = j if amunt else h - 1 - j
        for i in range(-w, w + 1):
            cv.flat(x + i, y + j, col)


# ─── La gota de Verne ───────────────────────────────────────────────────────

def gota(cv, cx, cy, h, lit=0):
    """La gota blava de Verne: una gota de h píxels d'alt, amb la punta a dalt i un reflex blanc."""
    r = h * 0.36
    by = cy + h / 2 - r                      # centre de la panxa
    top = cy - h / 2
    for y in range(int(top), int(cy + h / 2) + 1):
        for x in range(int(cx - r - 1), int(cx + r + 2)):
            dy = y + 0.5 - by
            if dy >= 0:
                inside = math.hypot(x + 0.5 - cx, dy) <= r
            else:
                t = (y + 0.5 - top) / max(1.0, by - top)
                inside = abs(x + 0.5 - cx) <= r * math.sqrt(max(0.0, t)) * (0.6 + 0.4 * t)
            if inside:
                u = (x + 0.5 - cx) / r
                cv.put(x, y, BLAU, 3.2 - u * 1.2 + (y - by) / max(1, h) * -0.6, lit=lit)
    if h >= 7:
        cv.flat(int(cx - r * 0.45), int(by - r * 0.2), BLAU[5])
        if h >= 12:
            cv.flat(int(cx - r * 0.45), int(by - r * 0.2) + 1, BLAU[4])
            cv.flat(int(cx - r * 0.45) + 1, int(by - r * 0.55), BLAU[4])


# ─── L'espai ────────────────────────────────────────────────────────────────

def espai(cv, x0, y0, x1, y1, seed=1, mask=None, dens=1.0, neb=(0.3, 0.6)):
    """Negre estrellat (amb una nebulosa molt fosca) dins el rectangle (i dins `mask(x, y)` si n'hi ha).
    → llista d'estrelles brillants [(x, y)] (per fer-les parpellejar)."""
    bright = []
    for y in range(y0, y1 + 1):
        for x in range(x0, x1 + 1):
            if mask and not mask(x, y):
                continue
            n = fbm(x / 90, y / 60, seed)
            band = max(0.0, 1 - abs((y - y0) - (x - x0) * 0.25 - (y1 - y0) * neb[1]) / 70)
            lvl = 0.6 + 2.8 * smooth(0.45, 0.8, n) * neb[0] * 3 * band + (fbm(x / 20, y / 14, seed + 4) - 0.5) * 0.5
            cv.put(x, y, ESPAI, lvl, lit=0)
            r = hr(x, y, seed + 77)
            if r > 1 - 0.0045 * dens:
                k = hr(x, y, seed + 5)
                cv.flat(x, y, STAR_W if k > 0.7 else (150, 160, 196) if k > 0.3 else (96, 96, 130))
                if r > 1 - 0.0005 * dens:
                    bright.append((x, y))
    for x, y in bright:                       # les brillants, amb creu
        for dx, dy in ((1, 0), (-1, 0), (0, 1), (0, -1)):
            if (not mask or mask(x + dx, y + dy)) and x0 <= x + dx <= x1 and y0 <= y + dy <= y1:
                cv.flat(x + dx, y + dy, (110, 118, 160))
    return bright


def estrelles_frames(base, bright, n=8, seed=3):
    """Fotogrames (diferència respecte del fons) amb unes quantes estrelles brillants que parpellegen."""
    frames = []
    for i in range(n):
        cv = Canvas(img=base.copy())
        for k, (x, y) in enumerate(bright):
            ph = (hr(k, seed) * n + i) % n
            if ph < 1:                                          # s'apaga
                for dx, dy in ((0, 0), (1, 0), (-1, 0), (0, 1), (0, -1)):
                    cv.flat(x + dx, y + dy, (40, 40, 70) if (dx or dy) else (130, 136, 170))
            elif ph < 2:                                        # brilla més
                for dx, dy in ((2, 0), (-2, 0), (0, 2), (0, -2)):
                    cv.flat(x + dx, y + dy, (80, 86, 130))
                for dx, dy in ((1, 0), (-1, 0), (0, 1), (0, -1)):
                    cv.flat(x + dx, y + dy, (190, 196, 230))
        frames.append(_diff(cv.img, base))
    return frames


def terra2(cv, cx, cy, r, mask=None, sun=(0.75, -0.35), seed=7):
    """Terra-2 des de l'òrbita: una bola ocre de pols, sense núvols, amb el sol a la dreta i una vora d'atmosfera
    groguenca. La meitat de l'esquerra, de nit (amb quatre llums de ciutat)."""
    lx, ly = sun
    lz = math.sqrt(max(0.0, 1 - lx * lx - ly * ly))
    for y in range(int(cy - r - 3), int(cy + r + 4)):
        for x in range(int(cx - r - 3), int(cx + r + 4)):
            if mask and not mask(x, y):
                continue
            nx, ny = (x + 0.5 - cx) / r, (y + 0.5 - cy) / r
            d2 = nx * nx + ny * ny
            if d2 > 1:
                d = math.sqrt(d2)
                if d < 1 + 3.0 / r:                                         # l'atmosfera
                    lit_rim = max(0.0, (nx * lx + ny * ly) / d)
                    if lit_rim > 0.15:
                        o = cv.get(x, y)
                        a = (1 - (d - 1) * r / 3.0) * lit_rim * 0.8
                        if a > B4[y & 3][x & 3] * 0.6:
                            cv.flat(x, y, mix(o, (230, 200, 140), min(1.0, a)))
                continue
            nz = math.sqrt(1 - d2)
            dif = nx * lx + ny * ly + nz * lz
            # coordenades de la superfície (gira una mica perquè els continents no quedin centrats)
            lon = math.atan2(nx, nz) * 1.4 + 0.6
            lat = math.asin(max(-1.0, min(1.0, ny)))
            land = fbm(lon * 1.8, lat * 2.6, seed, octaves=4)
            cracks = abs(fbm(lon * 5, lat * 6, seed + 9) - 0.5)
            lvl = 4.6 + (land - 0.5) * 3.2 - (0.9 if cracks < 0.03 else 0)
            lvl += 0.5 * math.cos(lat * 9 + land * 3) * 0.4                 # bandes de pols
            if abs(lat) > 1.25:
                lvl += 1.6                                                   # el pol, de sal
            light = smooth(-0.18, 0.5, dif)
            v = 0.3 + (lvl - 0.6) * light + 0.8 * max(0.0, dif) ** 6        # brillantor al punt del sol
            cv.put(x, y, OCRE, v, lit=0)
            if light < 0.08 and land > 0.52 and hr(x // 2, y // 2, seed) > 0.93:
                cv.flat(x, y, (250, 190, 110))                               # llums de ciutat, a la nit
            # la vora il·luminada, més clara (l'atmosfera per dins)
            if d2 > (1 - 2.2 / r) ** 2 and dif > 0.1:
                o = cv.get(x, y)
                cv.flat(x, y, mix(o, (246, 222, 170), 0.45))


def diposit(cv, x, y, s=1.0, lit=0):
    """Un dipòsit orbital de Verne: un cilindre blanc horitzontal (x, y = centre), amb tapes rodones, una franja
    blava amb la gota, panells solars i llums de posició. `s`: escala (1 = 120 px de llarg)."""
    L, R = 60 * s, 17 * s
    # panells solars (darrere): dues ales a dalt i a baix
    for sgn in (-1, 1):
        y0 = y + sgn * (R + 3 * s)
        y1 = y + sgn * (R + 22 * s)
        cv.line(x, y0, x, y + sgn * (R + 5 * s), BLANC, 2.4, lit=lit)
        for px_ in (x - 34 * s, x + 6 * s):
            a, b = sorted((y + sgn * (R + 6 * s), y1))
            cv.rect(px_, a, px_ + 28 * s, b, BLAU, lambda xx, yy: 0.9 + (1.1 if (int((xx - px_) / (4 * s)) + int((yy - a) / (4 * s))) % 2 else 0.4)
                    - (1.0 if (xx - px_) % max(2, int(4 * s)) == 0 or (yy - a) % max(2, int(4 * s)) == 0 else 0), lit=lit)
    # el cos
    for yy in range(int(y - R), int(y + R) + 1):
        v = (yy - y) / R
        for xx in range(int(x - L), int(x + L) + 1):
            u = (xx - x) / L
            band = int((xx - x + L) / (16 * s)) % 1 == 0 and (xx - x + L) % (16 * s) < 1
            lvl = 5.4 - v * 2.0 - v * v * 2.2 - (1.2 if band else 0) + (0.4 if -0.55 < v < -0.4 else 0)
            cv.put(xx, yy, BLANC, lvl, lit=lit)
    # les tapes (el·lipses) i el moll d'atracada
    for sgn in (-1, 1):
        ex = x + sgn * L
        cv.disc(ex, y, 6 * s, R, BLANC, lambda nx, ny: (3.0 if sgn < 0 else 4.4) - ny * 1.6 - abs(nx) * 0.6, lit=lit)
        cv.rect(ex + sgn * 5 * s - (0 if sgn > 0 else 4 * s), y - 4 * s, ex + sgn * 5 * s + (4 * s if sgn > 0 else 0), y + 4 * s,
                CROM, 3.6, lit=lit)
    # la franja blava amb la gota
    bx0, bx1 = x - 14 * s, x + 14 * s
    for yy in range(int(y - R), int(y + R) + 1):
        v = (yy - y) / R
        for xx in range(int(bx0), int(bx1) + 1):
            cv.put(xx, yy, BLAU, 2.8 - v * 1.4 - v * v * 1.4, lit=lit)
    cv.disc(x, y - 1 * s, 8 * s, 10 * s, BLANC, lambda nx, ny: 6.0 - ny * 0.6, lit=lit)
    gota(cv, x, y - 1 * s, max(5, int(15 * s)), lit=lit)
    # llums de posició
    cv.flat(int(x - L - 6 * s), int(y), (255, 70, 60))
    cv.flat(int(x + L + 6 * s), int(y), (90, 255, 120))


# ─── Marbre, or i columnes ──────────────────────────────────────────────────

def vena(x, y, seed=3):
    """Venes del marbre: 0 (res) .. 1 (al mig d'una vena)."""
    n = fbm(x / 70 + fbm(x / 30, y / 30, seed + 1) * 1.2, y / 46, seed, octaves=3)
    return max(0.0, 1 - abs(n - 0.5) / 0.018)


def terra_marbre(cv, y0, y1, vp=(320, -60), base=6.2, tile=56, gold_every=2, x0=0, x1=W - 1, refl=None, seed=5):
    """Terra de lloses de marbre blanc en perspectiva (punt de fuga vp), amb juntes fines, venes grises i una
    línia d'or cada `gold_every` lloses. `refl(x, y)` → nivells de reflex (opcional, p. ex. finestrals foscos)."""
    vx, vy = vp
    for y in range(y0, y1 + 1):
        d = y - vy
        v = 9000 / d
        vn = 9000 / (d + 1)
        for x in range(x0, x1 + 1):
            u = vx + (x - vx) * 260 / d
            u2 = vx + (x + 1 - vx) * 260 / d
            iu, iv = math.floor(u / tile), math.floor(v / tile * 2.2)
            lvl = base + (hr(iu, iv, seed) - 0.5) * 0.5
            vv = vena(u * 0.7, v * 3.0, seed + iu * 3 + iv)
            lvl -= vv * 1.8
            edge_u = math.floor(u2 / tile) != iu
            edge_v = math.floor(vn / tile * 2.2) != iv
            if refl:
                lvl += refl(x, y)
            if edge_u or edge_v:
                gold = (iu % gold_every == 0 and edge_u) or (iv % gold_every == 0 and edge_v)
                if gold:
                    cv.put(x, y, ORP, 4.4 + (0.6 if edge_v else 0))
                    continue
                lvl -= 1.3
            cv.put(x, y, MARB, lvl)


def columna(cv, x, y0, y1, r=9, base_h=10, cap_h=12, lvl=5.6):
    """Una columna blanca acanalada amb capitell i base daurats. x = centre."""
    for y in range(y0 + cap_h, y1 - base_h + 1):
        for xx in range(x - r, x + r + 1):
            u = (xx - x) / (r + 0.5)
            flute = (xx - x + r) % 4 == 0
            cv.put(xx, y, MARB, lvl + 1.6 * (0.3 - u) - 1.4 * u * u - (0.9 if flute else 0))
    # capitell: tres motllures d'or i un àbac blanc
    for k, (w, h, ramp, lv) in enumerate(((r + 5, 3, MARB, lvl + 0.8), (r + 3, 3, ORP, 4.6), (r + 2, 2, ORP, 3.6),
                                          (r + 1, 4, ORP, 5.0))):
        yy = y0 + sum(hh for _, hh, _, _ in ((r + 5, 3, 0, 0), (r + 3, 3, 0, 0), (r + 2, 2, 0, 0))[:k])
        for y in range(yy, yy + h):
            for xx in range(x - w, x + w + 1):
                u = (xx - x) / (w + 0.5)
                cv.put(xx, y, ramp, lv + 1.2 * (0.3 - u) - (1.0 if y == yy + h - 1 else 0) + (0.8 if y == yy else 0))
    # volutes
    for sgn in (-1, 1):
        cv.disc(x + sgn * (r + 2), y0 + 5, 2.2, 2.2, ORP, lambda nx, ny: 4.4 - ny, lit=1)
        cv.put(x + sgn * (r + 2), y0 + 5, ORP, 2.0)
    # base: plint blanc i tor d'or
    for k, (w, h, ramp, lv) in enumerate(((r + 2, 2, ORP, 4.4), (r + 3, 3, ORP, 3.8), (r + 5, base_h - 5, MARB, lvl))):
        yy = y1 - base_h + 1 + sum(hh for hh in (2, 3)[:k])
        for y in range(yy, yy + h):
            for xx in range(x - w, x + w + 1):
                u = (xx - x) / (w + 0.5)
                cv.put(xx, y, ramp, lv + 1.2 * (0.3 - u) + (0.8 if y == yy else 0) - (0.8 if y == yy + h - 1 else 0))


def motllura(cv, x0, x1, y, ramp=ORP, lvl=4.4, h=3):
    """Una motllura horitzontal (filet d'or): clar a dalt, fosc a baix."""
    for k in range(h):
        cv.hline(x0, x1, y + k, ramp, lvl + (1.2 if k == 0 else -1.2 if k == h - 1 else 0))


def marc_or(cv, x0, y0, x1, y1, t=3, lvl=4.4):
    """Marc d'or bisellat (llum a dalt i a l'esquerra)."""
    for k in range(t):
        cv.hline(x0 + k, x1 - k, y0 + k, ORP, lvl + 1.0 - k * 0.5)
        cv.vline(x0 + k, y0 + k, y1 - k, ORP, lvl + 0.6 - k * 0.5)
        cv.hline(x0 + k, x1 - k, y1 - k, ORP, lvl - 1.4 + k * 0.4)
        cv.vline(x1 - k, y0 + k, y1 - k, ORP, lvl - 1.0 + k * 0.4)


def vidre(cv, x0, y0, x1, y1, k=0.22, seed=0):
    """Reflexos en diagonal sobre un vidre fosc (ja pintat)."""
    for y in range(y0, y1 + 1):
        for x in range(x0, x1 + 1):
            s = (x - x0) + (y - y0) * 0.6 + seed
            band = (s % 140)
            a = k if 10 < band < 34 else k * 0.5 if 40 < band < 46 else 0
            if a and a > B4[y & 3][x & 3] * 0.9:
                o = cv.get(x, y)
                cv.flat(x, y, mix(o, (190, 200, 220), a))


# ─── Piscines ───────────────────────────────────────────────────────────────

def piscina(cv, top, bot, depth, plena=False, lvl=4.6, tile=6, seed=0, vora=2):
    """Una piscina en perspectiva vista de dalt: top = (xa, xb, y) la vora del fons, bot = (xa, xb, y) la vora
    del davant (més ample). `depth`: quants píxels baixa la paret del fons. Buida: es veu la paret del fons
    (rajola), les parets dels costats i el fons de rajola turquesa amb una franja fosca al mig.
    Plena: aigua blava amb reflexos (la línia de l'aigua a dos dits de la vora)."""
    (ta, tb, ty), (ba, bb, by) = top, bot

    def xa(y):
        return ta + (ba - ta) * (y - ty) / max(1, by - ty)

    def xb(y):
        return tb + (bb - tb) * (y - ty) / max(1, by - ty)
    # vora de pedra blanca (coronament)
    for y in range(ty - vora, by + vora + 1):
        for x in range(int(xa(y)) - vora - 1, int(xb(y)) + vora + 2):
            cv.put(x, y, MARB, 6.6 + (0.8 if y < ty else 0) - (1.0 if y > by else 0))
    for y in range(ty, by + 1):
        a, b = xa(y), xb(y)
        for x in range(int(math.ceil(a)), int(b) + 1):
            if plena:
                t = (y - ty) / max(1, by - ty)
                w = math.sin(x * 0.35 + y * 1.3 + seed) + math.sin(x * 0.11 - y * 0.7 + seed * 2)
                v = 3.6 + t * 1.2 + (1.6 if w > 1.5 else 0.6 if w > 1.1 else 0) - (0.8 if y < ty + 2 else 0)
                cv.put(x, y, AIGUA, v)
                continue
            # paret del fons: de ty a ty + depth (rajola, en ombra)
            if y < ty + depth:
                jy = (y - ty) % max(2, tile // 2) == 0
                jx = int((x - a) / tile) != int((x + 1 - a) / tile)
                v = lvl - 1.5 + (0.8 if jy or jx else 0)
                if y == ty + depth - 1:
                    v -= 0.8
                cv.put(x, y, TURQ, v)
                continue
            # parets dels costats: triangles que s'eixamplen cap al davant
            fy = (y - ty - depth) / max(1, by - ty - depth)
            side = (b - a) * 0.06 * (1 - fy) + 1.5
            if x < a + side:
                cv.put(x, y, TURQ, lvl + 0.6 - (0.9 if (y - ty) % 3 == 0 else 0))
                continue
            if x > b - side:
                cv.put(x, y, TURQ, lvl - 1.6 - (0.9 if (y - ty) % 3 == 0 else 0))
                continue
            # el fons, de rajola en perspectiva (junta blanca), amb la franja fosca de nedar al mig
            u = (x - a) / max(1, b - a)
            ph = max(1.5, tile * 0.45 * (0.6 + 0.4 * fy))
            gx = int(u * (b - a) / tile)
            gy = int((y - ty - depth) / ph)
            v = lvl + 0.1 + fy * 0.9 + (hr(gx, gy, seed) - 0.5) * 0.35
            if int(u * (b - a) / tile) != int((u * (b - a) + 1) / tile) or int((y - ty - depth + 1) / ph) != gy:
                v += 0.9
            if abs(x - (a + b) / 2) < max(0.6, (b - a) * 0.009):
                v = 1.0 + fy * 0.6                                            # la franja del mig
            if y == ty + depth:
                v -= 1.0                                                     # l'ombra de la paret del fons
            cv.put(x, y, TURQ, v)


def escaleta(cv, x, y, h, s=1.0):
    """L'escala cromada d'una piscina: dos passamans corbats que surten de la vora i baixen dins."""
    for dx in (0, int(7 * s)):
        xx = x + dx
        for k in range(int(5 * s)):                     # el corbat de dalt
            cv.put(xx + (k if k < 2 * s else 2 * s), y - int(4 * s) + k, CROM, 6.0 - k * 0.3)
        cv.vline(xx, y - int(4 * s), y + h, CROM, 5.4)
        cv.vline(xx + 1, y - int(4 * s) + 1, y + h, CROM, 3.0)
    for k in range(1, int(h / (4 * s)) + 1):
        cv.hline(x + 1, x + int(7 * s) - 1, y + int(k * 4 * s), CROM, 4.6)


# ─── L'aquari ───────────────────────────────────────────────────────────────

def _peixos(n=33, seed=12):
    """Les trajectòries dels peixos: (y relativa 0..1, velocitat, fase, mida)."""
    out = []
    for i in range(n):
        out.append((0.08 + 0.84 * hr(i, seed), 0.6 + hr(i, seed + 1) * 0.9, hr(i, seed + 2),
                    1 if hr(i, seed + 3) > 0.35 else 0, 1 if hr(i, seed + 4) > 0.5 else -1))
    return out


PEIXOS = _peixos()


def aigua_aquari(cv, x0, y0, x1, y1, t=0.0):
    """L'aigua de l'aquari (blava, clara a dalt), amb raigs de llum, sorra i algues; sense peixos."""
    for y in range(y0, y1 + 1):
        fy = (y - y0) / max(1, y1 - y0)
        for x in range(x0, x1 + 1):
            ray = math.sin((x - y * 0.35) * 0.18 + 1.0) * math.sin((x - y * 0.35) * 0.05)
            v = 5.0 - fy * 2.2 + (0.7 if ray > 0.55 else 0)
            cv.put(x, y, AIGUA, v, lit=0)
    # la superfície (una línia clara) i la sorra blanca d'Aqua al fons
    cv.hline(x0, x1, y0, AIGUA, 7.4, lit=0)
    cv.hline(x0, x1, y0 + 1, AIGUA, 6.2, lit=0)
    for x in range(x0, x1 + 1):
        hh = 4 + int(2 * math.sin(x * 0.12) + hr(x // 3, 1) * 1.5)
        for y in range(y1 - hh, y1 + 1):
            cv.put(x, y, MARB, 5.0 - (y1 - y) * 0.1 + (hr(x, y) - 0.5) * 1.2, lit=0)
    # algues (poques: l'aquari és un aparador, no un mar)
    for ax, ah in ((x0 + 6, 22), (x0 + 11, 15), (x1 - 8, 26), (x1 - 13, 12)):
        for k in range(ah):
            sway = math.sin(k * 0.3 + t * 2 * math.pi + ax) * 1.2 * k / ah
            cv.put(ax + sway, y1 - 4 - k, [(8, 40, 30), (16, 80, 54), (40, 130, 80), (90, 180, 110)], 2.0 + (k % 3 == 0), lit=0)
    # bombolles
    for k in range(5):
        bx = x0 + 4 + int(hr(k, 9) * (x1 - x0 - 8))
        by = y1 - 6 - int(((t + hr(k, 10)) % 1.0) * (y1 - y0 - 10))
        cv.flat(bx, by, (200, 236, 250))


def peix(cv, x, y, dir_, big, sh=0):
    """Un peix platejat de 6×3 (o 5×3), mirant cap a `dir_` (1 dreta, −1 esquerra)."""
    body = ['.aab.', 'abccd', '.aab.'] if not big else ['..aab.', 'abbccd', '..aab.']
    if dir_ < 0:
        body = [r[::-1] for r in body]
    leg = {'a': PLATA[1], 'b': PLATA[2], 'c': PLATA[3 + sh], 'd': PLATA[2]}
    for j, row in enumerate(body):
        for i, ch in enumerate(row):
            if ch in leg:
                cv.flat(x + i, y + j, leg[ch])
    # la cua
    tx = x - 1 if dir_ > 0 else x + len(body[0])
    cv.flat(tx, y, PLATA[1])
    cv.flat(tx, y + 2, PLATA[1])
    # l'ull
    cv.flat(x + (len(body[0]) - 2 if dir_ > 0 else 1), y + 1, (20, 26, 40))


def peixos(cv, x0, y0, x1, y1, t=0.0):
    """Els trenta-tres peixos en el temps t (0..1, cíclic): neden d'una banda a l'altra i giren."""
    w = x1 - x0 - 10
    for i, (fy, sp, ph, big, d0) in enumerate(PEIXOS):
        s = (ph + t * sp * (1 if i % 3 else 2)) % 1.0
        # anar i tornar: triangle 0..1..0
        pos = s * 2 if s < 0.5 else 2 - s * 2
        dir_ = 1 if s < 0.5 else -1
        if d0 < 0:
            pos, dir_ = 1 - pos, -dir_
        x = x0 + 3 + int(pos * w)
        y = y0 + 5 + int(fy * (y1 - y0 - 16) + math.sin((t * 4 + ph) * 2 * math.pi) * 1.2)
        peix(cv, x, y, dir_, big, sh=1 if (i + int(t * 16)) % 7 == 0 else 0)


def aquari_frames(base, rect, n=24, draw_glass=None):
    """Fotogrames dels peixos (diferència respecte del fons) per a un aquari de rect (x0, y0, x1, y1).
    `draw_glass(cv)`: torna a pintar els reflexos del vidre al damunt."""
    x0, y0, x1, y1 = rect
    frames = []
    for i in range(n):
        t = i / n
        cv = Canvas(img=base.copy())
        aigua_aquari(cv, x0, y0, x1, y1, t)
        peixos(cv, x0, y0, x1, y1, t)
        if draw_glass:
            draw_glass(cv)
        frames.append(_diff(cv.img, base))
    return frames


# ─── El panell del preu ─────────────────────────────────────────────────────

def panell_preu(cv, x0, y0, w=58, h=26, valor=None, amunt=True, lit=0):
    """El panell negre de Verne: «VERNE» amb la gota i, si hi ha valor, el preu en taronja amb ▲/▼."""
    cv.rect(x0 - 2, y0 - 2, x0 + w + 1, y0 + h + 1, ORP, 3.6, lit=lit)
    cv.hline(x0 - 2, x0 + w + 1, y0 - 2, ORP, 5.4, lit=lit)
    cv.hline(x0 - 2, x0 + w + 1, y0 + h + 1, ORP, 2.0, lit=lit)
    cv.rect(x0, y0, x0 + w - 1, y0 + h - 1, NEGRE, 0.9, lit=0)
    gota(cv, x0 + 6, y0 + 6, 8)
    lletres(cv, 'VERNE', x0 + 12, y0 + 4, (210, 220, 236))
    if valor is not None:
        panell_valor(cv, x0, y0, w, h, valor, amunt)


def panell_valor(cv, x0, y0, w, h, valor, amunt=True):
    """Només el número del panell (per als decorats preu46 / preu48): esborra la zona i hi escriu."""
    cv.rect(x0 + 2, y0 + 11, x0 + w - 3, y0 + h - 3, NEGRE, 0.9, lit=0)
    s = str(valor)
    tw = lletres_grans(cv, s, x0 + 8, y0 + 13, LED[3])
    triangle(cv, x0 + 8 + tw + 5, y0 + 14 if amunt else y0 + 14, 5, LED[3] if amunt else (120, 220, 140), amunt)
    lletres(cv, 'C', x0 + w - 9, y0 + 18, LED[2])


# ─── Altres ─────────────────────────────────────────────────────────────────

def ombra(cv, cx, cy, rx, ry, k=0.6):
    """Ombra suau (sense trama) en forma d'el·lipse, més fosca al mig."""
    def a(x, y):
        d = ((x - cx) / rx) ** 2 + ((y - cy) / ry) ** 2
        return k * (1 - d) ** 0.6 if d < 1 else 0
    cv.darken(cx - rx - 1, cy - ry - 1, cx + rx + 1, cy + ry + 1, a, dither=False)


def negre_barra(cv):
    """De y = 260 a baix: negre (la barra de verbs hi va al damunt)."""
    for y in range(RH, H):
        for x in range(W):
            cv.flat(x, y, (0, 0, 0))


def diff_estat(estat, clau, bg, light):
    """Prop que és la diferència entre el fons amb `estat[clau]` canviat i el fons normal."""
    base = Canvas(light=light)
    bg(base)
    old = estat[clau]
    estat[clau] = not old
    try:
        alt = Canvas(light=light)
        bg(alt)
    finally:
        estat[clau] = old
    return _diff(alt.img, base.img)
