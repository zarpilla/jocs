"""
L'avió (cinemàtica, final de l'Acte 1): la cabina del vol BCMU-07, vista de costat, mentre s'enlaira a l'alba.
Art definitiu:
  - la cabina: compartiments de dalt, finestretes ovalades (a fora, la pista i l'alba que passen: l'animació),
    seients de tela blava amb el logotip del banc als reposacaps;
  - la Rius, dreta al passadís amb l'armilla reflectant i la tauleta, mirant les noves;
  - l'Iri asseguda davant d'ella, i la Vet al seient del darrere, ja amb el vestit d'auditora;
  - un tècnic de debò, amb granota taronja, dorm amb la gorra a la cara.
"""
import math

from PIL import Image

from hd.pix import Light, Canvas, W, H, hr
from hd.rooms.comu import obox, outline, text, text_width, _diff, PLASTIC, SHEET, CARD, GRAYC
from hd.rooms.bar_sala import STEELB, SLATE
from hd.rooms.pis_cuina import outline_poly
from hd.rooms.aeroport_terminal import DAWN, CHROME, YELS, BLUE
from hd.characters import person, M, ORANGE, BOOT, TROUSER, SKIN_VET, SKIN_FOSCA, SKIN_RUDDY, HAIR_BROWN, HAIR_COPPER
from hd import personatges as P

FLOOR = 226            # el terra de la cabina (on recolzen els peus)
ROWS = (52, 140, 228, 316, 404, 492)
SEATED = {140: 'tecnic', 228: 'iri', 316: 'vet'}
RIUS_X = 184

CABIN = [(26, 20, 18), (46, 36, 32), (70, 58, 50), (98, 84, 72), (128, 112, 96), (158, 142, 122), (186, 170, 148), (212, 198, 176), (234, 224, 204)]
GOLDB = [(50, 32, 6), (110, 76, 16), (176, 128, 34), (220, 176, 70), (246, 220, 140)]
SEAT = [(6, 10, 26), (12, 20, 46), (20, 32, 70), (32, 48, 96), (48, 68, 124), (70, 92, 150)]
CARPETP = [(6, 8, 20), (12, 16, 36), (20, 26, 56), (30, 40, 80), (44, 56, 104)]
GROUND = [(14, 16, 14), (26, 30, 24), (40, 44, 34), (56, 60, 46)]
HIVIS = M((60, 70, 6), (120, 140, 10), (180, 210, 20), (220, 244, 60), (244, 255, 140), dith=0.0)

LIGHT = Light(ambient=0.0, vignette=(50, 30), floor_fade=(206, 30))
for _x in ROWS:
    LIGHT.point(_x - 20, FLOOR - 74, r=60, k=0.7, squash=1.0, power=2.0)      # la claror de cada finestreta
LIGHT.point(240, 10, r=260, k=1.4, squash=0.9, power=1.4)              # els llums de cabina


# ─── La cabina ─────────────────────────────────────────────────────────────

def cabin(cv):
    """Paret de plàstic clar, corbada a dalt; compartiments; una franja blava amb el logotip."""
    bins = FLOOR - 126
    for y in range(0, FLOOR):
        for x in range(W):
            if y < bins:                                   # el sostre, corbat i en penombra
                lvl = 3.8 + y / bins * 1.6
            else:
                lvl = 5.6 - max(0, (y - bins - 60) / 80)
            cv.put(x, y, CABIN, lvl + (hr(x // 3, y // 3) - 0.5) * 0.25)
    for x in range(0, W, 2):                               # la tira de llum del sostre
        cv.put(x, bins - 30, [(200, 200, 190), (250, 246, 230)], 1)
    cv.tint(0, bins - 40, W - 1, bins - 20, (250, 240, 210), lambda x, y: 0.12 * max(0, 1 - abs(y - bins + 30) / 10))
    # juntes dels plafons del sostre i les sortides d'aire
    for x0 in range(8, W, 96):
        cv.line(x0, 0, x0 + 6, bins - 1, CABIN, 1.8)
        for k in range(3):
            cv.disc(x0 + 40 + k * 10, bins - 12, 2.4, 1.4, CHROME, lambda nx, ny: 2.4 - ny)
            cv.flat(x0 + 40 + k * 10, bins - 12, (30, 30, 34))
    # els compartiments de dalt
    for x0 in range(-40, W, 96):
        obox(cv, x0 + 2, bins, x0 + 94, bins + 32, CABIN, 6.0, top=0.6)
        cv.rect(x0 + 4, bins + 26, x0 + 92, bins + 30, CABIN, 4.4)
        obox(cv, x0 + 40, bins + 24, x0 + 56, bins + 27, CHROME, 3.6)
        cv.flat(x0 + 20, bins + 34, (250, 240, 200))               # llums de lectura
        cv.flat(x0 + 28, bins + 34, (90, 90, 90))
    sx = 200
    obox(cv, sx, bins + 35, sx + 20, bins + 41, SLATE, 1.4)
    cv.rect(sx + 4, bins + 37, sx + 6, bins + 39, [(250, 230, 120)], 0, lit=0)   # el senyal de cinturons, encès
    cv.rect(sx + 12, bins + 37, sx + 16, bins + 39, [(250, 230, 120)], 0, lit=0)
    cv.glow(sx + 10, bins + 38, 10, (250, 220, 120), 0.3)
    # la franja daurada (els colors del banc) sota les finestretes
    cv.rect(0, FLOOR - 52, W - 1, FLOOR - 50, GOLDB, 2.6)
    cv.hline(0, W - 1, FLOOR - 49, CABIN, 3.0)
    cv.rect(0, FLOOR - 4, W - 1, FLOOR - 1, CABIN, 3.0)
    # el terra: moqueta
    for y in range(FLOOR, H):
        for x in range(W):
            motif = ((x // 6 + (y - FLOOR) // 3) % 5 == 0) and (y - FLOOR) % 3 == 1
            if motif:
                cv.put(x, y, GOLDB, 1.4 - (y - FLOOR) / 40)
            else:
                cv.put(x, y, CARPETP, 2.6 + (hr(x, y, 3) - 0.5) * 0.5 - (y - FLOOR) / 50)
    cv.hline(0, W - 1, FLOOR, CARPETP, 0.4)
    # el passadís: una tira de llumetes al terra
    for x in range(8, W, 16):
        cv.flat(x, FLOOR + 3, (250, 230, 160))


def window(cv, cx, frame=0):
    """Una finestreta ovalada: a fora, l'alba i la pista que s'allunya (l'avió s'enlaira)."""
    rx, ry = 10, 14
    cy = FLOOR - 76
    cv.disc(cx, cy, rx + 5, ry + 5, CABIN, lambda nx, ny: 6.0 - ny * 0.6 - nx * 0.3)     # el marc de plàstic, arrodonit
    cv.ring(cx, cy, rx + 5.5, CABIN, 2.6, step=3) if rx == ry else None
    cv.disc(cx, cy, rx + 2, ry + 2, CABIN, 3.0)
    tilt = -0.18                                       # l'avió aixeca el morro
    for y in range(int(cy - ry), int(cy + ry) + 1):
        for x in range(int(cx - rx), int(cx + rx) + 1):
            nx, ny = (x - cx) / rx, (y - cy) / ry
            if nx * nx + ny * ny > 1:
                continue
            hy = cy + 4 + (x - cx) * tilt                # l'horitzó, inclinat
            if y < hy:
                cv.put(x, y, DAWN, 2.0 + (y - (cy - ry)) / 4.5, lit=0)
            else:
                d = y - hy
                v = 1.4 + d * 0.15
                # els llums de la pista, que passen enrere
                if int(x + frame * 5 + d * 3) % 9 == 0 and d < 6:
                    cv.flat(x, y, (250, 210, 130))
                else:
                    cv.put(x, y, GROUND, v, lit=0)
    # el núvol que passa
    ncx = cx - rx + (frame * 4) % (2 * rx + 10) - 5
    for k in range(5):
        x = int(ncx + k)
        y = cy - 6 + (k % 2)
        if (x - cx) ** 2 / rx ** 2 + (y - cy) ** 2 / ry ** 2 < 0.8:
            cv.put(x, y, DAWN, 7.0, lit=0)
    cv.ring(cx, cy, 11, CABIN, 3.6, step=6)
    # la persiana, mig abaixada a una de cada dues
    if (cx // 96) % 2 == 1:
        cv.disc(cx, cy - ry + 3, rx - 1, 3, CABIN, 6.4)


def dawn_spill(cv):
    """L'alba entra per les finestretes i tenyeix la paret de rosa i taronja."""
    for x0 in ROWS:
        cx, cy = x0 - 20, FLOOR - 76
        cv.tint(cx - 40, cy - 30, cx + 40, FLOOR, (255, 170, 120),
                lambda x, y, cx=cx, cy=cy: 0.42 * max(0, 1 - math.hypot((x - cx - 6) / 38, (y - cy - 14) / 50)))


def seat_back(cv, x):
    """El respatller (darrere de qui seu: a la dreta), el coixí i el peu."""
    hip = FLOOR - 19
    back = [(x + 6, hip - 38), (x + 14, hip - 40), (x + 16, hip + 2), (x + 6, hip + 2)]
    cv.poly(back, SEAT, lambda xx, yy: 3.0 + (0.8 if xx < x + 9 else 0) - (yy - hip + 40) * 0.01)
    outline_poly(cv, back, SEAT)
    obox(cv, x + 5, hip - 42, x + 15, hip - 30, GOLDB, 3.2)               # el tapet del reposacaps, daurat
    cv.rect(x + 8, hip - 38, x + 12, hip - 36, SEAT, 1.6)
    cushion = [(x - 16, hip), (x + 14, hip), (x + 14, hip + 6), (x - 14, hip + 7)]
    cv.poly(cushion, SEAT, lambda xx, yy: 3.6 - (yy - hip) * 0.2)
    outline_poly(cv, cushion, SEAT)
    cv.rect(x - 4, hip + 7, x + 6, FLOOR, CHROME, 2.4)                    # el peu
    cv.darken(x - 18, FLOOR + 1, x + 16, FLOOR + 3, 0.5)


def armrest(cv, x):
    """El braç del seient (per davant de qui seu)."""
    hip = FLOOR - 19
    obox(cv, x - 10, hip - 8, x + 12, hip - 5, CHROME, 3.0)
    cv.rect(x + 10, hip - 5, x + 12, hip + 4, CHROME, 2.6)


# ─── La gent ───────────────────────────────────────────────────────────────

def _iri_spec():
    spec = dict(P.IRI)
    hooks = dict(spec['hooks'])
    hair = hooks['hair']
    hooks['hair'] = lambda fg, p, s: (hair(fg, p, s), P.iri_phones(fg, p, s))
    hooks.pop('over', None)
    spec['hooks'] = hooks
    return spec


SPECS = {
    'iri': _iri_spec(),
    'vet': P.VET_ROBA['Auditora'][0],
    'tecnic': {'skin': SKIN_RUDDY, 'legs': ORANGE, 'top': ORANGE, 'shoes': BOOT, 'stoop': 2,
               'hooks': {'hair': P.hair_cap(HAIR_BROWN)}},
}
RIUS = {'skin': SKIN_FOSCA, 'legs': TROUSER, 'top': HIVIS, 'sleeve': M((20, 20, 26), (40, 40, 50), (62, 62, 74), (88, 88, 100), (116, 116, 128)),
        'shoes': BOOT, 'thin': 1, 'hooks': {'hair': P.hair_cap(HAIR_BROWN, fringe=1.4)}}


def seated(cv, who, x):
    """Algú assegut, de perfil cap a l'esquerra (cap a la Rius), amb els peus a terra."""
    spec = dict(SPECS[who], seated=49)
    fig = person(spec, 'L')
    # els peus del dibuix d'assegut queden a la fila 68: hi posem el terra
    cv.img.alpha_composite(fig, (x - 26, FLOOR - 68))


def sleeper_cap(cv, x):
    """La gorra del tècnic, tirada damunt la cara."""
    hy = FLOOR - 68 + 15
    cv.disc(x - 3, hy, 6, 4, [(20, 40, 90), (40, 70, 140), (70, 110, 180)], lambda nx, ny: 1.6 - ny)
    cv.rect(x - 11, hy + 1, x - 4, hy + 2, [(20, 40, 90), (40, 70, 140)], 1.0)


def badge_in_hand(cv):
    """L'acreditació nova de la Vet, damunt la falda."""
    x, y = 316 - 16, FLOOR - 37
    obox(cv, x, y, x + 8, y + 5, SHEET, 5.0)
    cv.rect(x + 1, y + 1, x + 3, y + 3, [(150, 90, 70)], 0, lit=0)
    cv.rect(x + 1, y + 4, x + 7, y + 4, [(220, 40, 40)], 0, lit=0)


def rius(cv):
    """La Rius, dreta al passadís, girada cap a les noves, amb la tauleta de la subcontracta."""
    fig = person(RIUS, 'L').transpose(Image.FLIP_LEFT_RIGHT)
    cv.img.alpha_composite(fig, (RIUS_X - 24, FLOOR + 6 - 83))
    tx, ty = RIUS_X + 6, FLOOR + 6 - 36
    obox(cv, tx, ty, tx + 9, ty + 12, PLASTIC, 1.6)
    cv.rect(tx + 2, ty + 2, tx + 7, ty + 10, [(60, 140, 200), (120, 200, 240)], 0.6, lit=0)


def bg(cv, frame=0):
    cabin(cv)
    for x in ROWS:
        window(cv, x - 20, frame)
    dawn_spill(cv)
    for x in ROWS:
        seat_back(cv, x)
        if x in SEATED:
            seated(cv, SEATED[x], x)
            if SEATED[x] == 'tecnic':
                sleeper_cap(cv, x)
        armrest(cv, x)
    badge_in_hand(cv)
    rius(cv)


PROPS = {}


def _frames():
    base = Canvas(light=LIGHT)
    bg(base)
    frames = []
    for i in range(8):
        cv = Canvas(light=LIGHT, img=base.img.copy())
        for x in ROWS:
            window(cv, x - 20, i)
        frames.append(_diff(cv.img, base.img))
    return frames


ANIMS = {'enlairament': {'frames': _frames, 'frameDuration': 120}}
