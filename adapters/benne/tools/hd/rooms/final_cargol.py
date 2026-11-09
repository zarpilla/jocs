"""
Final 3 · «Correspondència»: pla proper al moll de l'Estació d'Orís (final_estacio). En Cargol, vell i rovellat, amb
la placa «CARGOL» que l'Iri li va gravar al pit, allarga la pinça amb una carta plegada mil vegades, groguenca; la
mà de la Vet hi arriba des de fora de quadre. Al fons, el finestral amb la Terra enorme, un tros del rètol i la
directora jove que s'ho mira. El fons és més pàl·lid i suau (desenfocat), perquè el que importa és a primer pla.
Llums: el sol que entra pel finestral (de l'esquerra, càlid), la Terra (blava, per la dreta), els ulls d'en Cargol.
Pantalla sencera (sense barra de verbs).
"""
import math
import random

from hd.pix import Canvas, Light, B4, W, H, hr, mix, ramp, PAPER, MANILA, SIL
from hd.rooms.proleg_gavina import espai, terra, vinyeta
from hd.rooms.final_estacio import (WALLW, DECK, MINT, LEAF, POT, text5_px, text5_width, bulb_sign, gull, planter,
                                    stamp, reflect, shadow, DIRECTORA_JOVE, person)
from hd.characters import (Fig, M, Mat, SCREEN, RUBBER, RUSTY, RUST_BRASS, LAMP_OLD, spiral_lvl, SKIN_VET, ORANGE,
                           INK)

LIGHT = Light(ambient=0.8, vignette=(60, 30), floor_fade=(240, 60))
LIGHT.point(60, 40, r=260, k=1.0)                                  # el sol pel finestral
LIGHT.point(430, 200, r=200, k=0.6)                                # la Terra

FLOOR_Y = 214
WIN = (-10, 66, 490, 204)
MULLIONS = (150, 330)
EARTH = (452, 336, 250)
SIGN_K = 5
HAZE = (214, 222, 236)


# ─── Fons (desenfocat: menys contrast, una boirina clara) ──────────────────

def background(cv, t=0.0):
    T = t                                                         # temps del bucle (t es reutilitza a sota)
    X0, Y0, X1, Y1 = WIN
    # sostre i biga del rètol
    for y in range(0, Y0):
        for x in range(W):
            cv.put(x, y, WALLW, 5.0 - (0.0 if y > 4 else 1.2) + (hr(x // 60, 2) - 0.5) * 0.3, 0.4)
    # el rètol, de prop: «ESTACIÓ D'ORÍS» a escala gran (en surt un tros)
    txt = "ESTACIÓ D'ORÍS"
    w = text5_width(txt, SIGN_K)
    sx0 = 236 - w // 2 - 60
    for y in range(2, 58):
        for x in range(W):
            lvl = 5.6 - (y - 2) * 0.02
            if y == 2:
                lvl = 7.4
            elif y >= 56:
                lvl = 2.0
            cv.put(x, y, WALLW, lvl, 0.3)
    cv.hline(0, W - 1, 54, MINT, 4.6, 0)
    bulb_sign(cv, txt, sx0, 18, SIGN_K, glow=False)
    pts, _ = text5_px(txt, sx0, 18, SIGN_K)
    for x, y, _a in pts[::2]:
        cv.glow(x + 2, y + 2, 11, (255, 220, 150), 0.18)
    cv.darken(0, 58, W - 1, 62, lambda x, y: 0.7 - (y - 58) * 0.18)
    # el finestral: l'espai i la Terra, enorme
    sky = Canvas()
    espai(sky, 0, W - 1, seed=23)
    terra(sky, EARTH[0], EARTH[1], EARTH[2])
    S = sky.P
    for y in range(Y0, Y1 + 1):
        for x in range(W):
            cv.flat(x, y, S[x, y])
    cv.tint(0, Y0, W - 1, Y1, (200, 230, 255), lambda x, y: 0.10 if (x + y * 0.6) % 140 < 16 else 0)
    # muntants i marc
    for mx in MULLIONS:
        for y in range(Y0 - 4, Y1 + 6):
            for x in range(mx - 7, mx + 7):
                u = (x - mx + 7) / 13
                cv.put(x, y, WALLW, 6.6 - u * 3.2 + (0.8 if x == mx - 6 else 0))
    for y in range(Y0 - 4, Y0):
        for x in range(W):
            cv.put(x, y, WALLW, 6.6 - (y - Y0 + 4) * 0.9)
    for y in range(Y1, FLOOR_Y):
        for x in range(W):
            t = (y - Y1) / (FLOOR_Y - Y1)
            cv.put(x, y, WALLW, 7.0 - t * 2.6 if y < Y1 + 3 else 4.2 - t * 0.6)
    cv.hline(0, W - 1, FLOOR_Y - 3, MINT, 4.4)
    cv.hline(0, W - 1, FLOOR_Y - 2, MINT, 3.0)
    cv.hline(0, W - 1, FLOOR_Y - 1, MINT, 1.6)
    # jardineres al peu del finestral
    planter(cv, 6, 140, Y1 - 6, seed=4, tall=30, time=T)
    planter(cv, 340, 476, Y1 - 6, seed=6, tall=34, time=(T * 2) % 1)
    # terra polit
    above = cv.img.copy().load()
    for y in range(FLOOR_Y, H):
        d = y - FLOOR_Y
        for x in range(W):
            u = (x - 240) / (d + 30) * 2.4
            fr = (u - math.floor(u)) * (d + 30) / 2.4
            lvl = 4.0 - d * 0.01 + (hr(math.floor(u), 3) - 0.5) * 0.3
            if fr < 1:
                lvl -= 1.2
            if d in (9, 30):
                lvl -= 1.0
            cv.put(x, y, DECK, lvl)
            sy = FLOOR_Y - 1 - int(d * 1.2)
            k = 0.45 * max(0.0, 1 - d / 46) ** 1.3
            if sy > 0 and fr >= 1:
                cv.flat(x, y, mix(cv.get(x, y), above[x, sy], k))
    # la clapa de sol, càlida, que entra per l'esquerra
    for y in range(FLOOR_Y + 1, H):
        d = y - FLOOR_Y
        for x in range(W):
            for xa, xb in ((-20, 140), (160, 320)):
                a, b = xa + d * 1.0, xb + d * 1.3
                if a < x < b:
                    e = min(x - a, b - x)
                    k = 0.42 * max(0.0, 1 - d / 60) * min(1.0, e / 4)
                    if k > B4[y & 3][x & 3] * 0.3:
                        cv.flat(x, y, mix(cv.get(x, y), (255, 228, 170), k))
    # raigs de sol a l'aire (respiren a poc a poc, cadascun al seu ritme)
    for y in range(Y0, FLOOR_Y):
        ty = (y - Y0) / (FLOOR_Y - Y0)
        for x in range(W):
            for j, (xa, xb) in enumerate(((0, 140), (160, 320))):
                a, b = xa + 10 + ty * 30, xb - 10 + ty * 20
                if a < x < b:
                    pulse = 1 + 0.6 * math.sin(2 * math.pi * (j + 1) * T)
                    cv.flat(x, y, mix(cv.get(x, y), (255, 228, 170), 0.06 * (0.3 + ty) * pulse))
    # la directora jove, al fons a la dreta, que s'ho mira (una mica més lluny: més pàl·lida)
    img = person(DIRECTORA_JOVE, 'L')
    reflect(cv, img, 424, 238, k=0.3)
    shadow(cv, 424, 238, 12, 3, 0.6)
    stamp(cv, img, 424, 238)
    # boirina del desenfocament
    cv.tint(0, 0, W - 1, H - 1, HAZE, lambda x, y: 0.16 if y < FLOOR_Y else 0.16 * max(0.0, 1 - (y - FLOOR_Y) / 40))


# ─── En Cargol, de prop ─────────────────────────────────────────────────────

S = 3.0                                                         # escala respecte del fotograma de joc (55×63)
RUSTD = Mat(RUSTY.c, 0.7)
BRASSD = Mat(RUST_BRASS.c, 0.7)
RUBBERD = Mat(RUBBER.c, 0.5)
LAMPD = Mat(LAMP_OLD.c, 0.5)
SCREEND = Mat(SCREEN.c, 0.6)
PLATE = M((40, 26, 14), (96, 64, 26), (160, 116, 46), (210, 170, 80), (240, 214, 140), (255, 244, 200), dith=0.5)
ENGRAVE = (44, 26, 16)


def rust_lvl(seed, k=1.0):
    """Clapes de rovell i pols: soroll de dues escales."""
    def f(x, y):
        n = hr(x // 4, y // 4, seed) * 0.6 + hr(x // 2, y // 2, seed + 1) * 0.4
        v = 0.0
        if n > 0.72:
            v -= 1.0 * k
        elif n < 0.18:
            v += 0.5 * k
        return v
    return f


def cargol_gran(blink=0):
    """En Cargol vell, de cara, a escala 3: el braç dret (a la dreta de la imatge) allargat amb la pinça oberta,
    l'esquerre avall amb la clau anglesa; la placa amb el nom; els ulls somrient."""
    fw, fh = 230, 200
    fg = Fig(fw, fh)
    s = S
    P = lambda x, y: (x * s, y * s)

    # erugues
    def tracks(x0, x1):
        pts = [(x0 + 2, 50), (x1 - 2, 50), (x1, 53), (x1, 58), (x1 - 2, 60), (x0 + 2, 60), (x0, 58), (x0, 53)]
        fg.poly([P(*p) for p in pts], RUBBERD, 2.4, amp=1.4, normal=lambda x, y: (0, (y / s - 55) / 6, 0.8), cont=(0.3, 0.8),
                lvlfn=lambda x, y: (0.9 if (int(x // 3) % 3 == 0) else 0) if (y < 52 * s or y > 58.4 * s) else 0)
        for wx in (x0 + 2.4, (x0 + x1) / 2, x1 - 2.4):
            fg.ell(wx * s, 55 * s, 1.5 * s, 1.5 * s, RUSTD, 3.0, amp=1.6, lvlfn=rust_lvl(7))
            fg.ell(wx * s, 55 * s, 0.5 * s, 0.5 * s, RUSTD, 4.0, amp=0.6)
        for x in range(int(x0 * s) + 2, int(x1 * s) - 1, 4):                                         # tacs
            fg.shade(x, 50 * s + 1, 1.2, RUBBERD); fg.shade(x, 60 * s - 1, -0.8, RUBBERD)
    tracks(9, 21)
    tracks(33, 45)
    # closca (darrere)
    fg.ell(*P(27, 27), 17 * s, 15.5 * s, BRASSD, 2.8, amp=1.6, cont=(0, 0.8),
           lvlfn=lambda x, y: spiral_lvl(27 * s, 27 * s, 5.0 * s)(x, y) + rust_lvl(3, 1.2)(x, y))
    # cos
    def edges(y):
        yy = y / s
        if yy < 22 or yy > 52:
            return None
        if yy <= 50:
            return ((17 - max(0, 25 - yy) * 1.2) * s, (37 + max(0, 25 - yy) * 1.2) * s)
        return (19 * s, 35 * s)
    fg.lathe(22 * s, 52 * s, edges, RUSTD, 3.0, amp=1.8, cont=(0.2, 1.0), lvlfn=rust_lvl(11))
    # pantalla (la cara)
    fg.poly([P(19, 27.6), P(35, 27.6), P(35.4, 40.2), P(18.6, 40.2)], SCREEND, 1.4, cont=(1.0, -0.8),
            lvlfn=lambda x, y: (0.8 if (x + y) % 23 < 2 else 0) + (0.6 if y < 28.6 * s else 0))
    # ulls que somriuen: arcs encesos
    for ex in (23.2, 30.8):
        cx, cy = ex * s, 33.4 * s
        if blink:                                                  # parpelleig: mig tancats o una ratlla
            for k in range(-7, 8):
                x = cx + k / 7 * 2.3 * s
                y = cy + (0.9 if blink == 2 else 0.2) * s - (0 if blink == 2 else math.cos(k / 7 * 1.25) * 0.6 * s)
                fg.px(x, y, LAMPD, 3.2 - abs(k) / 7 * 0.8)
                if blink == 1:
                    fg.px(x, y + 1, LAMPD, 2.4 - abs(k) / 7 * 0.8)
            continue
        for k in range(-7, 8):
            t = k / 7
            x = cx + t * 2.3 * s
            y = cy - math.cos(t * 1.25) * 1.6 * s + 0.6 * s
            for w in range(3):
                fg.px(x, y + w - 1, LAMPD, 3.6 + (0.8 if w == 0 else 0) - abs(t) * 0.8)
    # boca de reixeta, encesa (parla)
    for x in range(int(22 * s), int(33 * s), 3):
        fg.px(x, 37.6 * s, LAMPD, 2.6)
        fg.px(x + 1, 37.6 * s, LAMPD, 2.2)
        fg.px(x, 38.6 * s, LAMPD, 1.6)
    # junta del coll
    for x in range(int(17.5 * s), int(37 * s)):
        fg.shade(x, 44 * s, -1.4, RUSTD)
        fg.shade(x, 44 * s + 1, -0.6, RUSTD)
        fg.shade(x, 44 * s + 2, 0.8, RUSTD)
    # reblons
    for (x, y) in ((19, 47.5), (35, 47.5), (19.4, 25), (34.6, 25), (19, 42), (35, 42)):
        fg.ell(x * s, y * s, 1.0, 1.0, RUSTD, 4.4, amp=1.2)
    # placa al pit: llautó, amb CARGOL gravat a mà
    px0, py0, px1, py1 = 20.4 * s, 45.6 * s, 33.6 * s, 50.4 * s
    fg.poly([(px0, py0), (px1, py0), (px1, py1), (px0, py1)], PLATE, 3.0, amp=1.0, cont=(0.6, 1.4),
            lvlfn=lambda x, y: (1.0 if y < py0 + 1.5 else 0) - (x - px0) / (px1 - px0) * 0.8)
    # el braç esquerre, avall, amb la clau anglesa
    fg.limb(P(15.5, 31), P(12.4, 39.5), 2.0 * s, 1.7 * s, RUSTD, 2.6, amp=1.6, cont=(0.2, 0.8), lvlfn=rust_lvl(21))
    fg.ell(*P(12.4, 39.5), 2.1 * s, 2.1 * s, RUSTD, 2.6, amp=1.6)
    fg.limb(P(12.4, 39.5), P(13.2, 46), 1.6 * s, 1.4 * s, RUSTD, 2.4, amp=1.6, cont=(0.2, 0.8))
    fg.limb(P(13.0, 45), P(12.6, 53), 0.9 * s, 0.9 * s, RUSTD, 3.6, amp=1.6)                      # clau anglesa
    fg.ell(*P(12.6, 54.2), 2.0 * s, 1.6 * s, RUSTD, 3.2, amp=1.4)
    for k in range(4):
        fg.erase(12.6 * s - 1 + k % 2, 55.4 * s - k // 2)
    fg.ell(*P(13.2, 46), 1.8 * s, 1.5 * s, RUSTD, 2.8, amp=1.4)                                    # la mà que l'agafa
    # el braç dret, allargat cap a la Vet
    sh, el, wr = P(38.5, 31), P(47, 38.5), P(57.5, 37.5)
    fg.ell(*sh, 2.6 * s, 2.6 * s, RUSTD, 2.8, amp=1.6, cont=(0.2, 0.8))
    fg.limb(sh, el, 1.9 * s, 1.7 * s, RUSTD, 2.8, amp=1.6, cont=(0.2, 0.9), lvlfn=rust_lvl(31))
    fg.ell(*el, 2.1 * s, 2.1 * s, RUSTD, 2.6, amp=1.6, cont=(0.2, 0.8))
    fg.limb(el, wr, 1.6 * s, 1.4 * s, RUSTD, 3.0, amp=1.6, cont=(0.2, 0.9), lvlfn=rust_lvl(41))
    fg.ell(*wr, 1.9 * s, 1.9 * s, RUSTD, 2.8, amp=1.6)
    # pinça: dos dits que agafen la carta per la cantonada
    wx, wy = wr
    fg.limb((wx, wy), (wx + 3.8 * s, wy - 2.2 * s), 0.9 * s, 0.6 * s, RUSTD, 3.6, amp=1.6, cont=(0.2, 0.8))
    fg.limb((wx + 3.8 * s, wy - 2.2 * s), (wx + 6.6 * s, wy - 0.5 * s), 0.6 * s, 0.45 * s, RUSTD, 3.8, amp=1.6, cont=(0.2, 0.8))
    fg.limb((wx, wy), (wx + 3.8 * s, wy + 2.2 * s), 0.9 * s, 0.6 * s, RUSTD, 2.6, amp=1.6, cont=(0.2, 0.8))
    fg.limb((wx + 3.8 * s, wy + 2.2 * s), (wx + 6.6 * s, wy + 0.5 * s), 0.6 * s, 0.45 * s, RUSTD, 2.8, amp=1.6, cont=(0.2, 0.8))
    # antenes: l'esquerra una mica tòrcida (de vell)
    def antenna(bx, by, mx, my, tx, ty):
        fg.limb(P(bx, by), P(mx, my), 0.55 * s, 0.5 * s, RUSTD, 3.0, amp=1.6)
        fg.limb(P(mx, my), P(tx, ty + 2), 0.5 * s, 0.45 * s, RUSTD, 3.2, amp=1.6)
        fg.ell(*P(tx + 0.5, ty), 3.0 * s, 3.0 * s, RUSTD, 2.8, amp=1.6, cont=(0, 0.8), lvlfn=rust_lvl(51))
        fg.ell(*P(tx + 0.5, ty), 2.0 * s, 2.0 * s, LAMPD, 2.8, amp=1.4)
        fg.ell(*P(tx - 0.2, ty - 0.7), 0.6 * s, 0.6 * s, LAMPD, 4.6, amp=0.4)
    antenna(21, 22, 20, 15, 16.5, 9.5)
    antenna(33, 22, 34.4, 15, 35.4, 8.5)
    # abonyegadures, un cargol que hi falta i un pedaç reblat
    for (x, y) in ((24, 47), (25, 48), (31, 46.4), (20, 49), (36, 34), (37, 35)):
        fg.shade(x * s, y * s, -1.4)
        fg.shade(x * s + 1, y * s, -1.2)
        fg.shade(x * s, y * s + 1, -1.0)
    for dx, dy in ((0, 0), (1, 0), (0, 1), (1, 1)):
        fg.px(35 * s + dx, 42 * s + dy, INK, 0)                                                  # el cargol que hi falta
    img = fg.render()
    # la placa: el nom gravat i ratlles fines de la lima
    Pi = img.load()
    pts, wtxt = text5_px('CARGOL', 0, 0)
    ox = int((px0 + px1) / 2 - (wtxt + 1) / 2) + 1
    oy = int(py0) + 4
    for x, y, _a in pts:
        Pi[ox + x, oy + y] = ENGRAVE + (255,)
        if Pi[ox + x + 1, oy + y + 1][:3] != ENGRAVE:
            Pi[ox + x + 1, oy + y + 1] = (240, 214, 140, 255)
    return img


# ─── La carta i la mà de la Vet ─────────────────────────────────────────────

LETTER = ramp((60, 42, 28), (118, 90, 56), (170, 140, 92), (208, 180, 126), (230, 208, 156), (244, 228, 184), (252, 244, 214), n=9)


def letter(cv, x0, y0, w=30, h=21, tilt=-0.12):
    """La carta: plegada mil vegades, groguenca, amb les vores gastades i un plec que la travessa."""
    rnd = random.Random(5)
    folds_x = [w * 0.5, w * 0.25, w * 0.75]
    folds_y = [h * 0.5, h * 0.33]
    for j in range(h):
        for i in range(w):
            x = x0 + i + j * tilt * 0.0
            y = y0 + j + i * tilt
            edge = i in (0, w - 1) or j in (0, h - 1)
            if edge and hr(i, j, 3) < 0.25:
                continue                                          # vores menjades
            lvl = 5.2 - j * 0.05 + (hr(i // 3, j // 2, 7) - 0.5) * 0.7 - i * 0.02
            for fx in folds_x:
                if abs(i - fx) < 0.6:
                    lvl -= 1.8
                elif 0.6 <= i - fx < 1.6:
                    lvl += 0.8
            for fy in folds_y:
                if abs(j - fy) < 0.6:
                    lvl -= 1.6
                elif 0.6 <= j - fy < 1.6:
                    lvl += 0.7
            if edge:
                lvl -= 1.0
            if hr(i // 5, j // 4, 13) > 0.85:
                lvl -= 0.9                                        # taques
            cv.put(x, y, LETTER, lvl)
    # escriptura de l'Iri, que es transparenta (unes ratlles de tinta esvaïda)
    for row in range(4, h - 3, 4):
        x = 3
        while x < w - 4:
            ln = rnd.randint(2, 6)
            for k in range(ln):
                if x + k < w - 3 and rnd.random() > 0.2:
                    cv.put(x0 + x + k, y0 + row + (x + k) * tilt, [(150, 120, 104), (176, 146, 120)], 0.6)
            x += ln + rnd.randint(1, 2)
    # la V. del destinatari, ben visible
    for dx, dy in ((0, 0), (0, 1), (1, 2), (2, 3), (3, 2), (4, 1), (4, 0), (6, 3)):
        cv.flat(x0 + w - 11 + dx, round(y0 + 4 + dy + (w - 11 + dx) * tilt), (70, 44, 54))


def vet_hand():
    """Avantbraç i mà de la Vet que entren per baix a la dreta: el palmell obert, cap amunt, per rebre la carta.
    La mà és a (30, 40) del fotograma; el colze queda fora de quadre."""
    fg = Fig(240, 170)
    SK = Mat(SKIN_VET.c, 0.6)
    OR = Mat(ORANGE.c, 0.6)
    # màniga (la granota) i puny arromangat
    fg.limb((300, 230), (118, 104), 22, 17, OR, 2.6, amp=1.8, cont=(0.2, 0.9),
            lvlfn=lambda x, y: (-0.9 if (x * 0.8 + y) % 34 < 3 else 0) + (0.5 if (x * 0.8 + y) % 34 in (3, 4) else 0))
    fg.limb((132, 114), (106, 96), 17.4, 16.4, OR, 3.0, amp=1.8, cont=(0.3, 1.0),
            lvlfn=lambda x, y: -0.8 if abs((x - 120) * 0.6 + (y - 106) * 0.8) < 1.2 else 0)
    # avantbraç
    fg.limb((106, 94), (54, 56), 11.0, 8.6, SK, 2.7, amp=1.8, cont=(0.2, 0.8))
    # palmell, cap amunt i una mica de cantell
    fg.ell(40, 50, 14, 8.6, SK, 3.0, amp=1.6, cont=(0.2, 0.8))
    fg.ell(40, 48, 9.5, 4.0, SK, 2.2, amp=0.8)                                             # el clot del palmell
    # dits, oberts cap a la carta, amb les puntes una mica aixecades
    for k, (y0, ln, lift) in enumerate(((42.5, 17, 2.2), (47, 19, 1.6), (51.5, 18, 1.2), (55.5, 14, 0.8))):
        a = (30, y0)
        m = (30 - ln * 0.6, y0 + 1.2)
        b = (30 - ln, y0 - lift)
        r = 3.0 - k * 0.15
        fg.limb(a, m, r, r - 0.2, SK, 3.0 - k * 0.3, amp=1.6, cont=(0.2, 0.8))
        fg.limb(m, b, r - 0.2, r - 0.6, SK, 3.2 - k * 0.3, amp=1.6, cont=(0.2, 0.8))
        fg.px(b[0] + 1, b[1] - 1.5, SK, 4.4)                                                    # ungla, amb llum
        fg.px(b[0] + 2, b[1] - 1.5, SK, 3.8)
    # polze, a sobre, cap amunt
    fg.limb((44, 42), (34, 34), 4.0, 3.2, SK, 3.2, amp=1.6, cont=(0.2, 0.8))
    fg.limb((34, 34), (26, 32), 3.2, 2.8, SK, 3.4, amp=1.6, cont=(0.2, 0.8))
    return fg.render()


# ─── La pantalla ────────────────────────────────────────────────────────────

CX, CY = 2, 80                    # on va el fotograma d'en Cargol


def bg(cv, t=0.0):
    background(cv, t)
    # parpelleja un cop per bucle (fotogrames a t ≈ 0.5–0.62)
    ph = t % 1
    blink = 2 if 0.555 <= ph < 0.6 else (1 if 0.49 <= ph < 0.68 else 0)
    img = cargol_gran(blink)
    # reflex al terra i ombra
    fy = CY + int(60 * S)
    from PIL import ImageOps
    f = ImageOps.flip(img)
    Pf = f.load()
    for j in range(0, 60):
        y = fy + j
        if y >= H:
            break
        sj = f.height - int(60 * S) - 1 + j
        for i in range(f.width):
            c = Pf[i, sj] if 0 <= sj < f.height else (0, 0, 0, 0)
            x = CX + i
            if c[3] and 0 <= x < W:
                k = 0.3 * max(0.0, 1 - j / 40)
                if k > B4[y & 3][x & 3] * 0.25:
                    cv.flat(x, y, mix(cv.get(x, y), c, k))
    shadow(cv, CX + 27 * S, fy - 1, 60, 5, 0.8)
    cv.img.alpha_composite(img, (CX, CY))
    # la carta a la pinça (la pinça la tapa per la cantonada)
    wx, wy = CX + 57.5 * S, CY + 37.5 * S
    # la carta tremola una mica a la pinça (tres cops per bucle)
    flutter = 1 if math.sin(2 * math.pi * 3 * t) > 0.8 else 0
    letter(cv, int(wx + 15), int(wy - 11) + flutter, w=34, h=24)
    # redibuixa la punta del dit de sobre de la pinça, per davant de la carta
    Pi = img.load()
    for j in range(int(wy - CY - 3.5 * S), int(wy - CY)):
        for i in range(int(wx - CX + 3 * S), min(img.width, int(wx - CX + 8 * S))):
            c = Pi[i, j]
            if c[3]:
                cv.flat(CX + i, CY + j, c)
    # la llum càlida dels ulls i la de la carta
    cv.glow(CX + 27 * S, CY + 33.4 * S, 26, (255, 210, 120), 0.18)
    cv.glow(wx + 26, wy + 4, 30, (255, 236, 190), 0.25)
    # els llums de les antenes respiren (un cop per bucle)
    breath = math.sin(math.pi * t) ** 2
    if breath > 0.02:
        for ax, ay in ((17.0, 9.5), (35.9, 8.5)):
            cv.glow(CX + ax * S, CY + ay * S, 12, (255, 214, 110), 0.45 * breath)
    # la mà de la Vet
    hand = vet_hand()
    hx, hy = int(wx + 64), int(wy - 26)
    cv.img.alpha_composite(hand, (hx, hy))
    # pols que brilla al raig de sol, al voltant de la carta
    rnd = random.Random(17)
    mv = random.Random(18)                                       # (a part, perquè t=0 sigui el fons quiet)
    for _ in range(46):
        x, y = rnd.gauss(wx + 30, 46), rnd.gauss(wy - 10, 34)
        ph1, ph2, m = mv.uniform(0, 6.3), mv.uniform(0, 6.3), mv.choice((1, 2, 3))
        x += 3 * (math.sin(2 * math.pi * t + ph1) - math.sin(ph1))
        y += 5 * (math.cos(2 * math.pi * t + ph2) - math.cos(ph2))
        if 0 <= x < W and 0 <= y < H:
            b = rnd.random()
            tw = 1 - 0.8 * math.sin(math.pi * m * t) ** 2
            cv.flat(x, y, mix(cv.get(x, y), (255, 240, 200), (0.5 + b * 0.5) * tw))
            if b > 0.85:
                cv.glow(x, y, 4, (255, 230, 170), 0.5)
    vinyeta(cv, 0.5)


PROPS = {}


def _ambient_frames(n=16):
    """Fotogrames de l'animació de fons: només els píxels que canvien respecte del fons quiet."""
    base = Canvas(light=LIGHT)
    bg(base)
    frames = []
    for i in range(n):
        cv = Canvas(light=LIGHT)
        bg(cv, t=i / n)
        fr = Canvas(light=LIGHT, transparent=True)
        for y in range(H):
            for x in range(W):
                p = cv.P[x, y]
                if p != base.P[x, y]:
                    fr.P[x, y] = p
        frames.append(fr.img)
    return frames


ANIMS = {'ambient': {'frames': _ambient_frames, 'frameDuration': 110}}
