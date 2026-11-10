"""
Pròleg 2: la cel·la 9 de nit. La Vet dorm a la llitera de baix (en Mos, a la de dalt) i el panell
rovellat vibra i treu llum cian per les juntes. Llums: el panell, la Terra a la finestreta, el cor
de la MARE, tènue.
"""
import math

from hd.pix import Light, W, H, hr, ramp, CYAN, NAVY, SKIN, PAPER, GRAY, ORANGE, STEEL, RUST
from hd.rooms.gavina_cella import bg as cella_bg, COVER, p_escarabat, p_safata, GRIME, MATT, ambient_frames

LIGHT = Light(ambient=-0.9, vignette=(90, 50), floor_fade=(190, 30))
LIGHT.point(261, 102, r=170, k=3.4, squash=0.9, power=1.8)          # el panell que vibra
LIGHT.point(336, 50, r=90, k=1.3)                                    # la Terra a la finestreta
LIGHT.point(176, 30, r=50, k=0.8)                                    # el cor de la MARE

BLANKET = ramp((8, 10, 24), (18, 22, 46), (30, 36, 70), (46, 54, 96), (70, 80, 124), n=7)


def bg(cv, t=0.0):
    """`t` (0..1): moment del cicle de l'animació de fons (t = 0 és el fons quiet)."""
    tt = t                                   # (dins la funció, `t` es fa servir per a altres coses)
    ph = 2 * math.pi * tt
    cella_bg(cv, night=True, t=tt)
    # el sopar i el Senyor Bigotis, de nit
    p_safata(cv)
    p_escarabat(cv)

    # ─── La Vet dorm a la llitera de baix ─────────────────────────────────────
    # manta: un bony llarg del cos, dels peus (esquerra) a les espatlles
    for x in range(382, 446):
        u = (x - 382) / 63
        top = 124 - math.sin(u * math.pi * 0.95) * 3 - (2 if 0.55 < u < 0.8 else 0)
        for y in range(round(top), 136):
            lvl = 3.0 - (y - top) * 0.12 + math.sin(x / 4.0 + y / 6.0) * 0.4
            if y == round(top):
                lvl += 1.6
            elif y == round(top) + 1:
                lvl += 0.7
            cv.put(x, y, BLANKET, lvl)
    # el braç fora de la manta, amb la màniga taronja de la granota
    for x in range(424, 441):
        cv.put(x, 127, ORANGE, 2.6)
        cv.put(x, 128, ORANGE, 1.8)
    cv.rect(441, 127, 443, 128, SKIN, 2.0)
    # el cap: cabell platí sobre el coixí, la cara de perfil, girada cap a nosaltres
    cv.disc(453, 120, 7, 5, PAPER, lambda nx, ny: 4.2 - nx * 0.9 - ny * 1.2)
    cv.disc(449, 124, 4, 3.2, SKIN, lambda nx, ny: 3.0 - nx * 0.6 - ny * 0.8)
    for x in range(446, 452):
        cv.put(x, 122, PAPER, 4.6)                                      # serrell
    cv.put(447, 124, SKIN, 0.4)                                       # ull tancat
    cv.put(448, 124, SKIN, 0.4)
    cv.put(446, 126, SKIN, 1.2)

    # ─── En Mos, a la de dalt: un bony i el cap pelat ─────────────────────────
    cv.disc(446, 71, 4.6, 3.8, SKIN, lambda nx, ny: 3.4 - nx * 0.8 - ny)
    cv.put(444, 69, SKIN, 4.6)
    for y in range(70, 75):
        cv.put(450, y, GRAY, 3.6)
        cv.put(451, y, GRAY, 2.8)

    # ─── El panell vibra i fa llum ────────────────────────────────────────────
    x0, y0, x1, y1 = COVER
    # la llum de les juntes polsa: ones que corren al voltant de la tapa (0 a t = 0)
    pulse = math.sin(ph * 3)

    def shimmer(x, y):
        f = (x + y) / 9.0
        return 0.9 * (math.sin(ph * 2 - f) - math.sin(-f)) + 0.5 * pulse
    # llum cian per les juntes de la tapa
    for x in range(x0 - 1, x1 + 2):
        for y in (y0 - 1, y1 + 1):
            cv.put(x, y, CYAN, 4.4 + hr(x, y, 3) * 0.8 + shimmer(x, y), 0)
    for y in range(y0 - 1, y1 + 2):
        for x in (x0 - 1, x1 + 1):
            cv.put(x, y, CYAN, 4.4 + hr(x, y, 4) * 0.8 + shimmer(x, y), 0)
    # la tapa tremola: una imatge fantasma desplaçada, en cian
    cv.tint(x0, y0, x1, y1, (120, 220, 255), 0.08 * (1 + 0.6 * pulse))
    jit = 1 if math.sin(ph * 5) > 0.55 else 0                            # el fantasma salta un píxel
    for x in range(x0 + 1, x1 + 2):
        if (x + jit) % 2:
            cv.put(x, y0 - 2, CYAN, 3.2, 0)
    # ones de vibració a banda i banda
    # (les ones s'allunyen del panell: en surt una de nova a cada pas i l'última s'esvaeix)
    wu = (tt * 3) % 1
    for side in (-1, 1):
        bx = (x0 - 6) if side < 0 else (x1 + 6)
        for k in range(4 if wu else 3):
            p = k + wu
            fade = 1.0 if p <= 2 else 3 - p
            cx = bx + side * round(p * 5)
            for t in range(-7 - round(p * 2), 8 + round(p * 2)):
                xx = cx + side * round(abs(t) ** 2 / (14 + p * 6))
                if fade >= 1 or hr(xx, 102 + t, 31) < fade:
                    cv.put(xx, 102 + t, CYAN, 4.2 - p * 0.9, 0)
    # pols que cau del panell
    for i in range(14):
        v = 1 + (i % 2)                                                  # dues velocitats
        px = x0 + hr(i, 5) * (x1 - x0) + (math.sin(ph * 2 + i) - math.sin(i)) * 0.8
        py = y1 + 3 + (hr(i, 6) * 30 + tt * 30 * v) % 30
        cv.put(px, py, CYAN, 3.0 - (py - y1) / 20, 0)
    cv.glow(261, 102, 64, (90, 200, 255), 0.35)
    # i el halo polsa (barreja suau, sense quadrets, perquè el tramat no bulli)
    hk = 0.09 * (1 - math.cos(ph * 3)) / 2
    if hk:
        cv.tint(200, 45, 322, 159, (110, 215, 255), lambda x, y: hk * max(0, 1 - math.hypot(x - 261, y - 102) / 56))

    # llum cian al terra, davant del panell
    cv.tint(170, 158, 360, 204, (80, 180, 240),
            lambda x, y: max(0, 1 - math.hypot((x - 261) / 90, (y - 165) / 22)) * 0.25 * (1 + 0.25 * pulse))

    # ─── Nit: tot més fred ────────────────────────────────────────────────────
    cv.tint(0, 0, W - 1, H - 1, (10, 16, 46), lambda x, y: 0.25 * min(1, math.hypot(x - 261, y - 102) / 140))


def _ambient_frames(n=24):
    return ambient_frames(bg, LIGHT, n)


ANIMS = {'ambient': {'frames': _ambient_frames, 'frameDuration': 125}}

PROPS = {}
