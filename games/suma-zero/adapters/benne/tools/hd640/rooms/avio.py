"""
L'avió a 640×360 (cinemàtica, final de l'Acte 1; vegeu hd/rooms/avio.py, el de 480×270): la cabina del vol
BCMU-07, vista de costat, mentre s'enlaira a l'alba.
  - la cabina: sostre de plafons amb les sortides d'aire, compartiments de dalt (amb tanca i llums de lectura),
    finestretes ovalades amb el marc i el reflex (a fora, la pista i l'alba que passen: l'animació), seients de
    tela blava amb el logotip del banc al tapet del reposacaps, cinturons i butxaques;
  - la Rius, dreta al passadís amb l'armilla reflectant i la tauleta, mirant les noves;
  - l'Iri asseguda davant d'ella (amb els auriculars), i la Vet al seient del darrere, ja amb el vestit
    d'auditora i l'acreditació nova a la falda;
  - un tècnic de debò, amb granota taronja, dorm amb la gorra a la cara.
Animació: `enlairament` (12 fotogrames): els llums de la pista corren enrere i un núvol travessa cada finestreta.
Els personatges hi són dibuixats amb hd640.draw_characters.person (×4/3).
"""
import hd640  # noqa: F401  (abans que cap hd.rooms: posa la llibreria a 640×360)

import math

from PIL import Image

from hd.pix import Light, Canvas, W, H, hr
from hd.rooms.comu import obox, _diff, PLASTIC, SHEET
from hd.rooms.bar_sala import SLATE
from hd.rooms.pis_cuina import outline_poly
from hd.rooms.aeroport_terminal import DAWN, CHROME
from hd.characters import M, ORANGE, BOOT, TROUSER, SKIN_VET, SKIN_RUDDY, HAIR_BROWN
from hd640.draw_characters import person
from hd import personatges as P

# Art a 2× (1280×720 per a una sala de 640×360): el mateix dibuix, amb les formes, el dither i la llum a la
# resolució real (hd1280/canvas2x.py); el motor el mostra a 1/2 (artScale al .room.json).
ART_SCALE = 2
from hd1280.canvas2x import Canvas2x as Canvas  # noqa: E402,F811
from hd.pix import Canvas as Canvas1x  # noqa: E402,F401  (llenços auxiliars en píxels de sala: figures, textos)

FLOOR = 301            # el terra de la cabina (on recolzen els peus)
ROWS = (69, 187, 304, 421, 539, 656)
SEATED = {187: 'tecnic', 304: 'iri', 421: 'vet'}
RIUS_X = 245
WIN_RX, WIN_RY = 13, 19
WIN_Y = FLOOR - 101
NF = 12                # fotogrames de l'enlairament

CABIN = [(26, 20, 18), (46, 36, 32), (70, 58, 50), (98, 84, 72), (128, 112, 96), (158, 142, 122), (186, 170, 148), (212, 198, 176), (234, 224, 204)]
GOLDB = [(50, 32, 6), (110, 76, 16), (176, 128, 34), (220, 176, 70), (246, 220, 140)]
SEAT = [(6, 10, 26), (12, 20, 46), (20, 32, 70), (32, 48, 96), (48, 68, 124), (70, 92, 150)]
CARPETP = [(6, 8, 20), (12, 16, 36), (20, 26, 56), (30, 40, 80), (44, 56, 104)]
GROUND = [(14, 16, 14), (26, 30, 24), (40, 44, 34), (56, 60, 46)]
BELT = [(10, 12, 18), (24, 28, 38), (44, 50, 64), (70, 78, 94)]
HIVIS = M((60, 70, 6), (120, 140, 10), (180, 210, 20), (220, 244, 60), (244, 255, 140), dith=0.0)
CAPB = [(20, 40, 90), (40, 70, 140), (70, 110, 180), (110, 150, 210)]

LIGHT = Light(ambient=0.0, vignette=(67, 40), floor_fade=(275, 40))
for _x in ROWS:
    LIGHT.point(_x - 27, FLOOR - 99, r=80, k=0.7, squash=1.0, power=2.0)      # la claror de cada finestreta
LIGHT.point(320, 13, r=347, k=1.4, squash=0.9, power=1.4)              # els llums de cabina


# ─── La cabina ─────────────────────────────────────────────────────────────

def cabin(cv):
    """Paret de plàstic clar, corbada a dalt; compartiments; una franja daurada amb el logotip."""
    bins = FLOOR - 168
    for y in range(0, FLOOR):
        for x in range(W):
            if y < bins:                                   # el sostre, corbat i en penombra
                lvl = 3.8 + y / bins * 1.6
            else:
                lvl = 5.6 - max(0, (y - bins - 80) / 107)
            cv.put(x, y, CABIN, lvl + (hr(x // 3, y // 3) - 0.5) * 0.25)
    for x in range(0, W, 2):                               # la tira de llum del sostre
        cv.put(x, bins - 40, [(200, 200, 190), (250, 246, 230)], 1)
    cv.hline(0, W - 1, bins - 39, CABIN, 3.4)
    cv.tint(0, bins - 53, W - 1, bins - 27, (250, 240, 210), lambda x, y: 0.12 * max(0, 1 - abs(y - bins + 40) / 13))
    # juntes dels plafons del sostre (amb el cargol de cada cantó) i les sortides d'aire
    for x0 in range(11, W, 128):
        cv.line(x0, 0, x0 + 8, bins - 1, CABIN, 1.8)
        cv.line(x0 + 1, 0, x0 + 9, bins - 1, CABIN, 4.6)
        for yy in (20, 70, bins - 12):
            xx = x0 + 3 + round(yy / bins * 8)
            cv.put(xx, yy, CABIN, 2.4)
            cv.put(xx + 1, yy - 1, CABIN, 6.4)
        for k in range(3):
            vx, vy = x0 + 53 + k * 13, bins - 16
            cv.disc(vx, vy, 3.4, 2.4, CHROME, lambda nx, ny: 2.4 - ny)
            cv.flat(vx, vy, (30, 30, 34))
            cv.flat(vx + 1, vy, (52, 52, 58))
            cv.put(vx - 1, vy - 2, CHROME, 5.0)
    # els compartiments de dalt: tapa, tanca cromada, i a sota els llums de lectura i el botó de l'hostessa
    for x0 in range(-53, W, 128):
        obox(cv, x0 + 3, bins, x0 + 125, bins + 43, CABIN, 6.0, top=0.6)
        cv.hline(x0 + 5, x0 + 123, bins + 2, CABIN, 7.0)
        cv.rect(x0 + 5, bins + 35, x0 + 123, bins + 40, CABIN, 4.4)
        cv.hline(x0 + 5, x0 + 123, bins + 35, CABIN, 3.6)
        obox(cv, x0 + 53, bins + 31, x0 + 75, bins + 36, CHROME, 3.6)
        cv.hline(x0 + 55, x0 + 73, bins + 32, CHROME, 5.0)
        for lx in (x0 + 27, x0 + 37):                                 # llums de lectura (un encès)
            cv.disc(lx, bins + 45, 2.2, 1.4, CABIN, 3.0)
        cv.flat(x0 + 27, bins + 45, (250, 240, 200))
        cv.flat(x0 + 28, bins + 45, (230, 220, 180))
        cv.glow(x0 + 27, bins + 47, 6, (250, 240, 200), 0.25)
        cv.flat(x0 + 37, bins + 45, (90, 90, 90))
        cv.put(x0 + 45, bins + 45, [(40, 60, 120), (80, 110, 190)], 1)   # el botó de crida
    sx = 222                                                       # entre dues finestretes, que es vegi sencer
    obox(cv, sx, bins + 47, sx + 27, bins + 55, SLATE, 1.4)
    for k, x in enumerate((sx + 5, sx + 16)):                     # el senyal de cinturons i de no fumar, encès
        cv.rect(x, bins + 49, x + (3 if k == 0 else 6), bins + 52, [(250, 230, 120)], 0, lit=0)
    cv.flat(sx + 6, bins + 50, (120, 100, 40))
    cv.hline(sx + 16, sx + 22, bins + 50, [(120, 100, 40)], 0, lit=0)
    cv.glow(sx + 13, bins + 51, 13, (250, 220, 120), 0.3)
    # la franja daurada (els colors del banc) sota les finestretes
    cv.rect(0, FLOOR - 69, W - 1, FLOOR - 67, GOLDB, 2.6)
    cv.hline(0, W - 1, FLOOR - 69, GOLDB, 3.6)
    cv.hline(0, W - 1, FLOOR - 66, CABIN, 3.0)
    cv.rect(0, FLOOR - 5, W - 1, FLOOR - 1, CABIN, 3.0)
    cv.hline(0, W - 1, FLOOR - 5, CABIN, 4.6)
    # el terra: moqueta
    for y in range(FLOOR, H):
        for x in range(W):
            motif = ((x // 8 + (y - FLOOR) // 4) % 5 == 0) and (y - FLOOR) % 4 == 1
            if motif:
                cv.put(x, y, GOLDB, 1.4 - (y - FLOOR) / 53)
            else:
                cv.put(x, y, CARPETP, 2.6 + (hr(x, y, 3) - 0.5) * 0.5 - (y - FLOOR) / 67)
    cv.hline(0, W - 1, FLOOR, CARPETP, 0.4)
    # el passadís: una tira de llumetes al terra
    for x in range(11, W, 21):
        cv.flat(x, FLOOR + 4, (250, 230, 160))
        cv.flat(x + 1, FLOOR + 4, (200, 170, 110))
        cv.glow(x, FLOOR + 4, 4, (250, 220, 150), 0.18)


def window(cv, cx, frame=0, glass_only=False):
    """Una finestreta ovalada: a fora, l'alba i la pista que s'allunya (l'avió s'enlaira).
    `glass_only`: només el vidre (per als fotogrames; el marc no canvia)."""
    rx, ry = WIN_RX, WIN_RY
    cy = WIN_Y
    if not glass_only:
        cv.disc(cx, cy, rx + 7, ry + 7, CABIN, lambda nx, ny: 6.0 - ny * 0.6 - nx * 0.3)     # el marc de plàstic
        cv.disc(cx, cy, rx + 3, ry + 3, CABIN, lambda nx, ny: 3.0 + nx * 0.5 + ny * 0.3)    # el gruix de la paret
    tilt = -0.18                                       # l'avió aixeca el morro
    for y in range(int(cy - ry), int(cy + ry) + 1):
        for x in range(int(cx - rx), int(cx + rx) + 1):
            nx, ny = (x - cx) / rx, (y - cy) / ry
            if nx * nx + ny * ny > 1:
                continue
            hy = cy + 5 + (x - cx) * tilt                # l'horitzó, inclinat
            if y < hy:
                lvl = 2.0 + (y - (cy - ry)) / 6.0
                if hy - y < 2:                           # la ratlla de claror just sobre l'horitzó
                    lvl += 0.8
                cv.put(x, y, DAWN, lvl, lit=0)
            else:
                d = y - hy
                v = 1.4 + d * 0.11
                # els llums de la pista, que passen enrere
                if int(x + frame * 5 + d * 4) % 12 == 0 and d < 8:
                    cv.flat(x, y, (250, 210, 130) if d < 4 else (220, 170, 100))
                elif d < 1.2 and (x * 7 + frame) % 5 == 0:
                    cv.flat(x, y, (200, 150, 110))        # la ciutat llunyana
                else:
                    cv.put(x, y, GROUND, v, lit=0)
    # el núvol que passa (dues fileres, s'esfilagarsa)
    ncx = cx - rx - 11 + (frame * 4) % (2 * rx + 22)
    for k in range(9):
        for j in (-1, 0, 1):
            if (j == -1 and not 2 <= k <= 5) or (j == 1 and k in (0, 8)):
                continue
            x = int(ncx + k)
            y = cy - 8 + j
            if (x - cx) ** 2 / rx ** 2 + (y - cy) ** 2 / ry ** 2 < 0.8:
                cv.put(x, y, DAWN, 7.4 - j * 0.7, lit=0)
    # el reflex al vidre i els punts del marc
    for k in range(4):
        cv.tint(cx - rx + 3 + k, cy - ry + 6 + k * 2, cx - rx + 3 + k, cy - ry + 7 + k * 2, (255, 255, 255), 0.18)
    if not glass_only:
        for a in range(0, 360, 30):
            cv.put(round(cx + math.cos(math.radians(a)) * (rx + 5)), round(cy + math.sin(math.radians(a)) * (ry + 5)), CABIN, 3.8)
    # la persiana, mig abaixada a una de cada dues
    if (cx // 128) % 2 == 1:
        cv.disc(cx, cy - ry + 4, rx - 1, 4, CABIN, 6.4)
        cv.hline(cx - 4, cx + 4, cy - ry + 7, CABIN, 3.6)


def dawn_spill(cv):
    """L'alba entra per les finestretes i tenyeix la paret de rosa i taronja."""
    for x0 in ROWS:
        cx, cy = x0 - 27, WIN_Y
        cv.tint(cx - 53, cy - 40, cx + 53, FLOOR, (255, 170, 120),
                lambda x, y, cx=cx, cy=cy: 0.42 * max(0, 1 - math.hypot((x - cx - 8) / 51, (y - cy - 19) / 67)))


def seat_back(cv, x):
    """El respatller (darrere de qui seu: a la dreta), el coixí, el cinturó i el peu."""
    hip = FLOOR - 25
    back = [(x + 8, hip - 51), (x + 19, hip - 53), (x + 21, hip + 3), (x + 8, hip + 3)]
    cv.poly(back, SEAT, lambda xx, yy: 3.0 + (0.8 if xx < x + 12 else 0) - (yy - hip + 53) * 0.008)
    for yy in range(hip - 44, hip, 6):                                     # les costures de la tela
        cv.hline(x + 10, x + 18, yy, SEAT, 2.2)
    outline_poly(cv, back, SEAT)
    obox(cv, x + 7, hip - 56, x + 20, hip - 40, GOLDB, 3.2)               # el tapet del reposacaps, daurat
    cv.rect(x + 10, hip - 51, x + 17, hip - 46, SEAT, 1.6)               # el logotip del banc
    cv.hline(x + 11, x + 16, hip - 49, GOLDB, 3.4)
    cv.vline(x + 13, hip - 50, hip - 47, GOLDB, 3.4)
    cushion = [(x - 21, hip), (x + 19, hip), (x + 19, hip + 8), (x - 19, hip + 9)]
    cv.poly(cushion, SEAT, lambda xx, yy: 3.6 - (yy - hip) * 0.15)
    cv.hline(x - 19, x + 18, hip + 1, SEAT, 4.4)
    outline_poly(cv, cushion, SEAT)
    cv.rect(x - 5, hip + 9, x + 8, FLOOR, CHROME, 2.4)                    # el peu, amb la barra
    cv.vline(x - 5, hip + 9, FLOOR, CHROME, 3.6)
    cv.hline(x - 12, x + 15, FLOOR - 1, CHROME, 2.0)
    cv.darken(x - 24, FLOOR + 1, x + 21, FLOOR + 4, 0.5)


def belt(cv, x):
    """El cinturó, penjant del coixí, amb la sivella."""
    hip = FLOOR - 25
    cv.vline(x + 15, hip + 5, hip + 14, BELT, 2.0)
    cv.vline(x + 16, hip + 5, hip + 12, BELT, 1.4)
    obox(cv, x + 13, hip + 13, x + 17, hip + 16, CHROME, 4.0)


def armrest(cv, x):
    """El braç del seient (per davant de qui seu)."""
    hip = FLOOR - 25
    obox(cv, x - 13, hip - 11, x + 16, hip - 7, CHROME, 3.0)
    cv.hline(x - 12, x + 15, hip - 10, CHROME, 4.6)
    cv.rect(x + 13, hip - 7, x + 16, hip + 5, CHROME, 2.6)
    cv.put(x - 10, hip - 9, [(40, 40, 46)], 0)                           # el botó del respatller


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
RIUS = {'skin': SKIN_VET, 'legs': TROUSER, 'top': HIVIS, 'sleeve': M((20, 20, 26), (40, 40, 50), (62, 62, 74), (88, 88, 100), (116, 116, 128)),
        'shoes': BOOT, 'thin': 1, 'hooks': {'hair': P.hair_cap(HAIR_BROWN, fringe=1.4)}}


def seated(cv, who, x):
    """Algú assegut, de perfil cap a l'esquerra (cap a la Rius), amb els peus a terra."""
    spec = dict(SPECS[who], seated=49)
    fig = person(spec, 'L')
    # els peus del dibuix d'assegut queden a la fila 90 (la 68 de 480): hi posem el terra
    cv.blit(fig, (x - 35, FLOOR - 90))


def sleeper_cap(cv, x):
    """La gorra del tècnic, tirada damunt la cara, amb el botó de dalt i la visera."""
    hy = FLOOR - 70
    cv.disc(x - 4, hy, 8, 5.4, CAPB, lambda nx, ny: 1.8 - ny)
    cv.hline(x - 9, x + 1, hy + 3, CAPB, 0.6)
    cv.put(x - 4, hy - 5, CAPB, 3.0)
    cv.rect(x - 15, hy + 1, x - 5, hy + 3, CAPB, 1.0)
    cv.hline(x - 15, x - 5, hy + 1, CAPB, 2.0)


def badge_in_hand(cv):
    """L'acreditació nova de la Vet, damunt la falda: la foto, la ratlla vermella i la pinça."""
    x, y = 400, FLOOR - 49
    obox(cv, x, y, x + 11, y + 7, SHEET, 5.0)
    cv.rect(x + 1, y + 1, x + 4, y + 4, [(150, 90, 70)], 0, lit=0)
    cv.flat(x + 2, y + 1, (60, 40, 30))
    cv.hline(x + 6, x + 9, y + 2, [(120, 120, 130)], 0, lit=0)
    cv.hline(x + 6, x + 8, y + 4, [(160, 160, 170)], 0, lit=0)
    cv.hline(x + 1, x + 10, y + 6, [(220, 40, 40)], 0, lit=0)
    cv.rect(x + 4, y - 2, x + 7, y - 1, CHROME, 3.6)


def rius(cv):
    """La Rius, dreta al passadís, girada cap a les noves, amb la tauleta de la subcontracta."""
    fig = person(RIUS, 'L').transpose(Image.FLIP_LEFT_RIGHT)
    cv.blit(fig, (RIUS_X - 32, FLOOR + 8 - 111))
    tx, ty = RIUS_X + 8, FLOOR + 8 - 48
    obox(cv, tx, ty, tx + 12, ty + 16, PLASTIC, 1.6)
    cv.rect(tx + 2, ty + 2, tx + 10, ty + 14, [(60, 140, 200), (120, 200, 240)], 0.6, lit=0)
    for k in range(4):                                                    # la llista de la feina
        cv.hline(tx + 3, tx + 9 - (k % 2) * 2, ty + 4 + k * 3, [(200, 240, 255)], 0, lit=0)
    cv.flat(tx + 6, ty + 15, (90, 90, 100))
    cv.glow(tx + 6, ty + 8, 9, (120, 200, 240), 0.2)


def bg(cv, frame=0):
    cabin(cv)
    for x in ROWS:
        window(cv, x - 27, frame)
    dawn_spill(cv)
    for x in ROWS:
        seat_back(cv, x)
        if x in SEATED:
            seated(cv, SEATED[x], x)
            if SEATED[x] == 'tecnic':
                sleeper_cap(cv, x)
        else:
            belt(cv, x)
        armrest(cv, x)
    badge_in_hand(cv)
    rius(cv)


PROPS = {}


def _frames():
    base = Canvas(light=LIGHT)
    bg(base)
    frames = []
    for i in range(NF):
        cv = Canvas(light=LIGHT, img=base.img.copy())
        for x in ROWS:
            window(cv, x - 27, i, glass_only=True)
        frames.append(_diff(cv.img, base.img))
    return frames


ANIMS = {'enlairament': {'frames': _frames, 'frameDuration': 120}}

GEOMETRIA = {
    'things': {},
    'spawns': {},
    'walkable': [(200, 253), (267, 253), (267, 261), (200, 261)],
}
