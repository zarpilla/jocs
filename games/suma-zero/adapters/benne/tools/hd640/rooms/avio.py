"""
L'avió a 640×360 (cinemàtica, final de l'Acte 1): la cabina del vol BCMU-07 mentre s'enlaira a l'alba. EN 3D
(hd640/tres_d.py), a 1×.

La càmera és a la cuina de davant, una mica alta, i mira el passadís de biaix cap a l'esquerra:
  - el **passadís** fuig cap a la cuina del fons (la cortina il·luminada): la moqueta, la tira de llumetes del terra
    i la tira de llum del sostre són les línies que porten l'ull;
  - a l'esquerra, la **paret de les finestretes** en escorç (l'alba a fora: el que es mou), els compartiments de dalt
    i els **seients** de dues places que fugen fila a fila; a la dreta, l'altre bloc de seients, que surt del quadre;
  - primer pla: a l'esquerra, la fila de seients de davant de tot, fosca i tallada per la vora; a la dreta, la
    mampara de la cuina de davant, en silueta; el seient buit de la primera fila de la dreta, gran, amb tres cares;
  - la gent, cada una a l'escala de la seva fila: el **tècnic** de la granota taronja dorm amb la gorra a la cara i
    el cap contra la finestreta (la fila més a prop), l'**Iri** amb els auriculars al seient del passadís, la
    **Rius** dreta al passadís amb l'armilla reflectant i la tauleta, mirant-la, i la **Vet** a la fila de darrere
    amb l'acreditació nova penjada al coll (la més lluny); els asseguts, de cara (en 3/4), i els respatllers de la
    fila de davant els tapen les cames;
  - la llum: el sol de l'alba entra rasant per les finestretes i fa taques i raigs en diagonal pel passadís.
Animació: `enlairament` (12 fotogrames): els llums de la pista corren enrere i un núvol travessa cada finestreta.
Els personatges són els de hd640.draw_characters.person, posats com a sprites.

El món: x a la dreta (0 = la paret de l'esquerra), y amunt (0 = el terra), z cap a la cua de l'avió; 1 unitat =
1 píxel de sala a la distància on un personatge fa ≈111 px (escala 1).
"""
import functools
import math

import hd640  # noqa: F401  (abans que cap hd.rooms: posa la llibreria a 640×360)
from hd640 import llum
from PIL import Image

from hd.pix import Light, Canvas, hr
from hd.rooms.comu import obox, _diff, PLASTIC, SHEET
from hd.rooms.aeroport_terminal import DAWN, CHROME
from hd.rooms.exterior import fbm
from hd.characters import M, ORANGE, BOOT, TROUSER, SKIN_VET, SKIN_FOSCA, SKIN_RUDDY, HAIR_BROWN
from hd640.draw_characters import person
from hd640.tres_d import Camera, Escena, Llum
from hd import personatges as P

NF = 12                # fotogrames de l'enlairament

CABIN = [(26, 20, 18), (46, 36, 32), (70, 58, 50), (98, 84, 72), (128, 112, 96), (158, 142, 122), (186, 170, 148), (212, 198, 176), (234, 224, 204)]
GOLDB = [(50, 32, 6), (110, 76, 16), (176, 128, 34), (220, 176, 70), (246, 220, 140)]
SEAT = [(6, 10, 26), (12, 20, 46), (20, 32, 70), (32, 48, 96), (48, 68, 124), (70, 92, 150)]
CARPETP = [(6, 8, 20), (12, 16, 36), (20, 26, 56), (30, 40, 80), (44, 56, 104)]
GROUND = [(14, 16, 14), (26, 30, 24), (40, 44, 34), (56, 60, 46)]
BELT = [(10, 12, 18), (24, 28, 38), (44, 50, 64), (70, 78, 94)]
HIVIS = M((60, 70, 6), (120, 140, 10), (180, 210, 20), (220, 244, 60), (244, 255, 140), dith=0.0)
CAPB = [(20, 40, 90), (40, 70, 140), (70, 110, 180), (110, 150, 210)]
FOSC = [(3, 3, 8), (7, 7, 14), (12, 12, 22), (18, 18, 30), (26, 26, 40), (36, 36, 52)]
CURTAIN = [(40, 30, 40), (80, 60, 70), (130, 100, 100), (180, 150, 136), (226, 200, 170), (250, 236, 210)]

# ─── El món ──────────────────────────────────────────────────────────────────

XW = 250                                   # la paret de la dreta (la de l'esquerra és a x = 0)
HC = 156                                   # el sostre, al mig
Z0, ZB = -220, 640                         # on comença la cabina (darrere la càmera) i la cuina del fons
DADO = 34                                  # el sòcol de sota les finestretes
WTOP = (12, 112)                           # el cap de dalt del panell de les finestretes (x, y)
BIN_X = 64                                 # el davant dels compartiments de l'esquerra (la dreta, simètrica)
BIN_Y = (112, 140)
SEAT_L = (6, 96)                           # el bloc de seients de l'esquerra (dues places)
SEAT_R = (154, 244)
PITCH = 66                                 # d'una fila a l'altra
ROWS = [8 + PITCH * k for k in range(-2, 10)]  # la z del davant del coixí de cada fila
WIN_T = 36                                 # el centre de les finestretes, al llarg del panell (des de baix)
WIN_RX, WIN_RY = 10, 15                    # al panell (el pla de la textura): unitats del món


def win_z(k):
    """La z del centre de la finestreta de la fila k (una mica per darrere del respatller)."""
    return ROWS[k] + 28


CAM = Camera(pos=(134, 146, -110), yaw=-0.3, pitch=0.3, f=340, centre=(320, 96))

# Qui seu on: (fila, x del centre del seient)
R0 = 2                                     # (ROWS[R0] és la primera fila de davant la càmera)
TECNIC = (R0 + 1, SEAT_L[0] + 22)            # al seient de la finestreta, amb el cap contra el vidre
IRI = (R0 + 2, SEAT_L[1] - 22)
VET = (R0 + 3, SEAT_L[1] - 22)
RIUS = (126, ROWS[R0 + 2] + 44)                # dreta al passadís, entre la fila de l'Iri i la de la Vet

LIGHT = Light(ambient=0.0, vignette=None, floor_fade=None)   # (la llum és la del món: la de l'Escena)

SOL = (1.0, -0.62, -0.55)                 # el sol de l'alba: entra per l'esquerra, baixa i ve cap a la càmera


# ─── Les textures planes ─────────────────────────────────────────────────────

FLAT_W, FLAT_H = ZB - Z0, 79              # el panell de les finestretes, pla (x = z - Z0, y = des de dalt)
_PANEL_LEN = math.hypot(WTOP[0], WTOP[1] - DADO)


def _win_c(k):
    return win_z(k) - Z0, FLAT_H - WIN_T


def window(cv, cx, cy, frame=0, glass_only=False, persiana=False):
    """Una finestreta ovalada (al pla del panell): a fora, l'alba i la pista que s'allunya (l'avió s'enlaira).
    `glass_only`: només el vidre (per als fotogrames; el marc no canvia)."""
    rx, ry = WIN_RX, WIN_RY
    if not glass_only:
        cv.disc(cx, cy, rx + 6, ry + 6, CABIN, lambda nx, ny: 6.4 - ny * 0.6 - nx * 0.3, lit=0)     # el marc
        cv.disc(cx, cy, rx + 3, ry + 3, CABIN, lambda nx, ny: 3.2 + nx * 0.5 + ny * 0.3, lit=0)     # el gruix
    tilt = -0.18                                       # l'avió aixeca el morro
    for y in range(int(cy - ry), int(cy + ry) + 1):
        for x in range(int(cx - rx), int(cx + rx) + 1):
            nx, ny = (x - cx) / rx, (y - cy) / ry
            if nx * nx + ny * ny > 1:
                continue
            hy = cy + 5 + (x - cx) * tilt                # l'horitzó, inclinat
            if y < hy:
                lvl = 3.0 + (y - (cy - ry)) / 5.0
                if hy - y < 2:                           # la ratlla de claror just sobre l'horitzó
                    lvl += 1.0
                cv.put(x, y, DAWN, lvl, lit=0)
            else:
                d = y - hy
                if int(x + frame * 4 + d * 4) % 10 == 0 and d < 8:
                    cv.flat(x, y, (255, 214, 140) if d < 4 else (220, 170, 100))     # els llums de la pista
                elif d < 1.2 and (x * 7 + frame) % 5 == 0:
                    cv.flat(x, y, (210, 160, 110))        # la ciutat llunyana
                else:
                    cv.put(x, y, GROUND, 1.4 + d * 0.11, lit=0)
    # el núvol que passa
    ncx = cx - rx - 10 + (frame * 3) % (2 * rx + 20)
    for k in range(9):
        for j in (-1, 0, 1):
            if (j == -1 and not 2 <= k <= 5) or (j == 1 and k in (0, 8)):
                continue
            x, y = int(ncx + k), int(cy - 7 + j)
            if (x - cx) ** 2 / rx ** 2 + (y - cy) ** 2 / ry ** 2 < 0.8:
                cv.put(x, y, DAWN, 8.0 - j * 0.7, lit=0)
    for k in range(4):                                  # el reflex al vidre
        cv.tint(cx - rx + 3 + k, cy - ry + 6 + k * 2, cx - rx + 3 + k, cy - ry + 7 + k * 2, (255, 255, 255), 0.2)
    if persiana and not glass_only:                     # la persiana, mig abaixada
        cv.disc(cx, cy - ry + 5, rx - 1, 5, CABIN, 6.4, lit=0)
        cv.hline(cx - 4, cx + 4, cy - ry + 9, CABIN, 3.6, lit=0)


def _persiana(k):
    return k in (2, 6)


def _panell(frame=0, glass_only=False):
    """El panell de les finestretes, pla: plàstic clar, la franja daurada a sota i les finestretes."""
    cv = Canvas(FLAT_W, FLAT_H, light=Light(ambient=0.0, vignette=None, floor_fade=None), transparent=glass_only)
    if not glass_only:
        for y in range(FLAT_H):
            for x in range(FLAT_W):
                cv.put(x, y, CABIN, 6.2 - y / FLAT_H * 0.8 + (hr(x // 3, y // 3) - 0.5) * 0.25, lit=0)
        cv.rect(0, FLAT_H - 10, FLAT_W - 1, FLAT_H - 7, GOLDB, 2.6, lit=0)     # la franja daurada (el banc)
        cv.hline(0, FLAT_W - 1, FLAT_H - 10, GOLDB, 3.6, lit=0)
        cv.hline(0, FLAT_W - 1, FLAT_H - 6, CABIN, 3.0, lit=0)
        for k in range(len(ROWS)):                        # les juntes dels plafons
            x = int(win_z(k) - Z0 - PITCH / 2)
            cv.vline(x, 0, FLAT_H - 11, CABIN, 4.2, lit=0)
            cv.vline(x + 1, 0, FLAT_H - 11, CABIN, 7.0, lit=0)
    for k in range(len(ROWS)):
        cx, cy = _win_c(k)
        window(cv, cx, cy, frame, glass_only, persiana=_persiana(k))
    return cv.img


@functools.lru_cache(maxsize=None)
def _panell_base():
    return _panell()


# ─── La gent ─────────────────────────────────────────────────────────────────

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
RIUS_SPEC = {'skin': SKIN_FOSCA, 'legs': TROUSER, 'top': HIVIS,
             'sleeve': M((20, 20, 26), (40, 40, 50), (62, 62, 74), (88, 88, 100), (116, 116, 128)),
             'shoes': BOOT, 'thin': 1, 'hooks': {'hair': P.hair_cap(HAIR_BROWN)}}

HIP, KNEE, SHIN = 72, 6, 26               # assegut, de cara: el tors fins al maluc, la falda i les canyelles
SEATED_FEET = HIP + KNEE + SHIN - 5       # (la fila dels peus a la figura asseguda)


def seated_front(spec, facing='DL'):
    """Algú assegut, de cara (en 3/4): el tors de la figura dreta, una falda curta (les cuixes vénen cap a la càmera)
    i les canyelles. (El dibuix d'assegut de hd.characters només és de perfil.)"""
    fig = person(spec, facing)
    out = Image.new('RGBA', (fig.width + 4, HIP + KNEE + SHIN), (0, 0, 0, 0))
    out.alpha_composite(fig.crop((0, 0, fig.width, HIP)), (2, 0))
    lap = fig.crop((0, HIP - 2, fig.width, HIP + KNEE - 2))
    out.alpha_composite(lap, (1, HIP))
    out.alpha_composite(lap, (3, HIP))                # (les cuixes, una mica més amples: vénen cap a nosaltres)
    out.alpha_composite(fig.crop((0, fig.height - SHIN - 5, fig.width, fig.height - 5)), (2, HIP + KNEE))
    # la vora de la falda, una mica més fosca (l'ombra de les cuixes damunt les canyelles)
    px = out.load()
    for x in range(out.width):
        c = px[x, HIP + KNEE]
        if c[3]:
            px[x, HIP + KNEE] = (c[0] * 6 // 10, c[1] * 6 // 10, c[2] * 6 // 10, 255)
    return out


def _cap_on_face(img):
    """La gorra del tècnic, tirada damunt la cara: dorm."""
    from hd.pix import Canvas as C1
    cv = C1(img.width, img.height, img=img)
    cx, cy = 34, 17
    cv.disc(cx, cy, 11, 7, CAPB, lambda nx, ny: 2.4 - ny * 1.2 - nx * 0.4, lit=0)
    cv.rect(cx - 11, cy + 5, cx + 10, cy + 8, CAPB, 0.7, lit=0)            # la visera, damunt els ulls
    cv.hline(cx - 11, cx + 10, cy + 5, CAPB, 2.0, lit=0)
    cv.hline(cx - 10, cx + 9, cy + 9, [(40, 24, 20)], 0, lit=0)            # l'ombra de la visera
    cv.flat(cx, cy - 7, CAPB[3])
    cv.rect(cx - 2, cy + 13, cx + 1, cy + 14, [(70, 30, 30)], 0, lit=0)    # la boca oberta: ronca
    return cv.img


def _badge(img):
    """L'acreditació nova de la Vet, a la falda: la foto, la ratlla vermella i la pinça."""
    from hd.pix import Canvas as C1
    cv = C1(img.width, img.height, img=img)
    x, y = 31, 44
    cv.line(x + 1, y, 28, 36, [(200, 40, 40)], 0, lit=0)               # el cordó, penjat del coll
    cv.line(x + 7, y, 39, 36, [(200, 40, 40)], 0, lit=0)
    obox(cv, x, y, x + 9, y + 6, SHEET, 5.0, lit=0)
    cv.rect(x + 1, y + 1, x + 3, y + 3, [(150, 90, 70)], 0, lit=0)
    cv.hline(x + 5, x + 7, y + 2, [(120, 120, 130)], 0, lit=0)
    cv.hline(x + 1, x + 8, y + 5, [(220, 40, 40)], 0, lit=0)
    return cv.img


def _tauleta(img):
    """La tauleta de la subcontracta, a les mans de la Rius, que brilla."""
    from hd.pix import Canvas as C1
    cv = C1(img.width, img.height, img=img)
    tx, ty = 34, 58
    obox(cv, tx, ty, tx + 10, ty + 13, PLASTIC, 1.6, lit=0)
    cv.rect(tx + 2, ty + 2, tx + 8, ty + 11, [(60, 140, 200), (120, 200, 240)], 0.6, lit=0)
    for k in range(3):
        cv.hline(tx + 3, tx + 7 - (k % 2) * 2, ty + 4 + k * 3, [(200, 240, 255)], 0, lit=0)
    return cv.img


@functools.lru_cache(maxsize=None)
def _figures():
    return {
        'tecnic': _cap_on_face(seated_front(SPECS['tecnic'], 'D')).rotate(7, resample=Image.Resampling.NEAREST,
                                                                          center=(34, 90)),
        'iri': seated_front(SPECS['iri'], 'DL'),
        'vet': _badge(seated_front(SPECS['vet'], 'DL')),
        'rius': _tauleta(person(RIUS_SPEC, 'DL')),
    }


# ─── L'escena ────────────────────────────────────────────────────────────────

def _moqueta(s, t, P):
    x, z = P[0], P[2]
    if SEAT_L[1] < x < SEAT_R[0]:                       # el passadís: el motiu daurat del banc
        if (int(z // 9) + int(x // 12)) % 5 == 0 and int(z) % 9 < 2:
            return 4.2
    return 2.2 + (hr(int(x // 2), int(z // 2), 3) - 0.5) * 0.6 + (fbm(x / 50, z / 50, 2) - 0.5) * 0.5


def _sol_a_terra(x, z):
    """Quanta llum del sol (0..1) arriba a un punt del terra del passadís: es remunta el raig fins a la paret de
    l'esquerra i es mira si hi ha una finestreta (sense persiana)."""
    t = x / SOL[0]
    y, zz = -SOL[1] * t, z - SOL[2] * t
    # al panell de les finestretes: l'alçada → la t del pla
    if not DADO < y < WTOP[1]:
        return 0.0
    tt = (y - DADO) / (WTOP[1] - DADO) * _PANEL_LEN
    for k in range(len(ROWS)):
        if _persiana(k):
            continue
        dz, dt = (zz - win_z(k)) / WIN_RX, (tt - WIN_T) / WIN_RY
        d2 = dz * dz + dt * dt
        if d2 < 1.0:
            return (1.0 - d2) ** 1.6                   # (la vora, suau: amb un tall net semblava un forat)
    return 0.0


def _seient(e, sid, x0, x1, zf, ramp=SEAT, dark=False, cinturo=True):
    """Un bloc de seients (dues places) amb el davant del coixí a zf: les potes, el coixí, el respatller amb el
    tapet daurat del reposacaps, els braços i els cinturons."""
    R = FOSC if dark else ramp
    G = FOSC if dark else GOLDB
    Cr = FOSC if dark else CHROME
    n = 2
    w = (x1 - x0) / n
    e.foscor(sid + '_ombra', (x0 - 4, 0.5, zf + 46), (x1 + 4, 0.5, zf + 46), (x1 + 4, 0.5, zf - 8), (x0 - 4, 0.5, zf - 8),
             lambda s, t: 0.55 * max(0.0, 1 - abs(t - 30) / 30))
    for lx in (x0 + 8, x1 - 8):                                      # les potes i la barra
        e.caixa(sid, lx - 2, lx + 2, 0, 18, zf + 10, zf + 14, Cr, 2.4)
    e.caixa(sid, x0 + 6, x1 - 6, 4, 7, zf + 10, zf + 13, Cr, 2.0)
    e.caixa(sid, x0, x1, 18, 28, zf, zf + 36, R, 2.6,                # el coixí
            cares={'dalt': {'ramp': R, 'lvl': lambda s, t, P: 3.4 - (1.2 if abs(s % w - w / 2) > w / 2 - 1.5 else 0)
                            - t * 0.02},
                   'davant': {'ramp': R, 'lvl': lambda s, t, P: 2.0 - (0.8 if abs(s % w - w / 2) > w / 2 - 1.5 else 0)}})
    e.caixa(sid, x0, x1, 18, 74, zf + 34, zf + 42, R, 2.4,           # el respatller
            cares={'davant': {'ramp': R, 'lvl': lambda s, t, P: (3.0 - (1.2 if abs(s % w - w / 2) > w / 2 - 1.5 else 0)
                                                                 - (0.6 if int(t) % 7 == 0 and t > 18 else 0)
                                                                 - t * 0.012)},
                   'dalt': {'ramp': R, 'lvl': 3.6}})
    for k in range(n):                                               # el tapet daurat de cada reposacaps, amb el logo
        cx = x0 + w * k + w / 2
        e.quad(sid, (cx - 9, 72, zf + 33.6), (cx + 9, 72, zf + 33.6), (cx + 9, 61, zf + 33.6), (cx - 9, 61, zf + 33.6),
               ramp=G, lvl=lambda s, t, P: 3.4 - (1.6 if 6 < s < 12 and 3 < t < 8 else 0) - (0.8 if t > 10 else 0))
        if cinturo and not dark:                                     # el cinturó, damunt el coixí
            e.cable(sid, [(cx - 14, 28.5, zf + 30), (cx - 10, 28.5, zf + 18), (cx - 4, 28.5, zf + 12)], BELT, 2.0, gruix=2)
            e.caixa(sid, cx - 4, cx + 1, 28, 29.5, zf + 10, zf + 14, CHROME, 4.0)
    for k in range(n + 1):                                           # els braços
        ax = x0 + w * k
        e.caixa(sid, ax - 2.5, ax + 2.5, 28, 44, zf + 4, zf + 36, Cr, 2.6,
                cares={'dalt': {'ramp': Cr, 'lvl': 3.8}, 'davant': {'ramp': Cr, 'lvl': 2.2}})


def escena(cv, tex):
    e = Escena(cv, CAM, [Llum((125, HC - 6, z), 180, 1.0, power=1.4) for z in range(0, ZB, 160)]
               + [Llum((10, 64, win_z(k)), 110, 1.3, power=1.6) for k in range(len(ROWS)) if not _persiana(k)]
               + [Llum((125, 80, ZB - 10), 200, 1.6, power=1.3)], ambient=-0.3)
    zn = CAM.pos[2] - 10
    panell = tex['panell']
    # la cuina del fons: la cortina il·luminada i el rètol de sortida
    e.quad('fons', (0, HC, ZB), (XW, HC, ZB), (XW, 0, ZB), (0, 0, ZB), ramp=CABIN, lvl=5.2)
    e.quad('cortina', (96, 124, ZB - 1), (154, 124, ZB - 1), (154, 0, ZB - 1), (96, 0, ZB - 1), ramp=CURTAIN,
           lvl=lambda s, t, P: 4.4 + 0.7 * math.sin(s / 2.6) - t * 0.008)
    e.quad('sortida', (112, 142, ZB - 1), (138, 142, ZB - 1), (138, 132, ZB - 1), (112, 132, ZB - 1),
           ramp=[(10, 60, 30), (40, 160, 80), (140, 250, 170)], lvl=lambda s, t, P: 2.0 if 2 < s < 24 and 2 < t < 8 else 1.0)
    # el sostre: dos plafons inclinats amb la tira de llum al mig, i les juntes de cada fila
    for xa, xb, ya in ((BIN_X, 125, BIN_Y[1]), (125, XW - BIN_X, HC)):
        yb = HC if xa == BIN_X else BIN_Y[1]
        e.quad('sostre', (xa, ya, ZB), (xb, yb, ZB), (xb, yb, zn), (xa, ya, zn), ramp=CABIN, dues_cares=True,
               lvl=lambda s, t, P: (7.4 if abs(P[0] - 125) < 3 else 4.0 + (P[1] - BIN_Y[1]) / 16 * 0.8)
               - (1.4 if (P[2] - 8) % PITCH < 1.4 else 0) + (hr(int(P[0] // 4), int(P[2] // 4)) - 0.5) * 0.3)
    # les parets: el sòcol, el panell de les finestretes (inclinat) i el compartiment de dalt
    e.quad('socol_e', (0, DADO, zn), (0, DADO, ZB), (0, 0, ZB), (0, 0, zn), ramp=CABIN, lvl=lambda s, t, P: 4.6 - t * 0.012)
    e.quad('panell_e', (WTOP[0], WTOP[1], Z0), (WTOP[0], WTOP[1], ZB), (0, DADO, ZB), (0, DADO, Z0),
           tex=(panell, (0, 0, FLAT_W, FLAT_H)))
    e.quad('socol_d', (XW, DADO, ZB), (XW, DADO, zn), (XW, 0, zn), (XW, 0, ZB), ramp=CABIN, lvl=4.2)
    e.quad('panell_d', (XW - WTOP[0], WTOP[1], ZB), (XW - WTOP[0], WTOP[1], Z0), (XW, DADO, Z0), (XW, DADO, ZB),
           tex=(panell.transpose(Image.FLIP_LEFT_RIGHT), (0, 0, FLAT_W, FLAT_H)))
    for side in (0, 1):
        bx0, bx1 = (WTOP[0], BIN_X) if side == 0 else (XW - BIN_X, XW - WTOP[0])
        fx = BIN_X if side == 0 else XW - BIN_X

        def bins(s, t, P, side=side):
            z = P[2] - 8 + PITCH / 2
            v = 5.4 + t * 0.03
            if z % PITCH < 1.5:
                return 2.6                                               # la junta entre dues tapes
            if abs(z % PITCH - PITCH / 2) < 5 and 27 < t < 30:
                return 3.0 if abs(z % PITCH - PITCH / 2) > 4 or t < 28 else 6.6  # la tanca
            if t > 33:
                return 4.4
            return v
        e.quad('bins', (bx0, BIN_Y[0], ZB), (bx1, BIN_Y[0], ZB), (bx1, BIN_Y[0], zn), (bx0, BIN_Y[0], zn), ramp=CABIN,
               lvl=lambda s, t, P: 3.4 - (0.8 if (P[2] - 8) % PITCH < 2 else 0) - (1.4 if abs((P[2] - 30) % PITCH) < 3
                                                                                   and abs(P[0] - (BIN_X - 14 if P[0] < 125 else XW - BIN_X + 14)) < 3 else 0),
               dues_cares=True)
        if side == 0:
            e.quad('bins', (fx, BIN_Y[1], zn), (fx, BIN_Y[1], ZB), (fx, BIN_Y[0], ZB), (fx, BIN_Y[0], zn), ramp=CABIN, lvl=bins)
        else:
            e.quad('bins', (fx, BIN_Y[1], ZB), (fx, BIN_Y[1], zn), (fx, BIN_Y[0], zn), (fx, BIN_Y[0], ZB), ramp=CABIN, lvl=bins)
    # els llums de lectura sota els compartiments (un d'encès a la fila de l'Iri)
    for k in range(len(ROWS)):
        z = ROWS[k] + 22
        on = k == IRI[0]
        e.quad('lectura', (BIN_X - 22, BIN_Y[0] - 0.4, z + 3), (BIN_X - 16, BIN_Y[0] - 0.4, z + 3),
               (BIN_X - 16, BIN_Y[0] - 0.4, z - 3), (BIN_X - 22, BIN_Y[0] - 0.4, z - 3),
               ramp=[(60, 56, 50), (250, 240, 200)] if on else CABIN, lvl=1.0 if on else 2.0, dues_cares=True)
    # el terra: la moqueta, i la tira de llumetes del passadís (la línia que porta l'ull fins a la cuina)
    e.quad('terra', (0, 0, ZB), (XW, 0, ZB), (XW, 0, zn), (0, 0, zn), ramp=CARPETP, lvl=_moqueta)
    for side_x in (SEAT_L[1] + 3, SEAT_R[0] - 3):
        for z in range(0, ZB, 22):
            e.quad('llumetes', (side_x - 1, 0.3, z + 1.5), (side_x + 1, 0.3, z + 1.5), (side_x + 1, 0.3, z - 1.5),
                   (side_x - 1, 0.3, z - 1.5), ramp=[(120, 90, 50), (250, 226, 160)], lvl=1.2)
    # el sol al passadís: les taques de cada finestreta, estirades en diagonal
    e.claror((SEAT_L[1], 0.4, ZB), (XW, 0.4, ZB), (XW, 0.4, zn), (SEAT_L[1], 0.4, zn), (255, 186, 130),
             lambda s, t: 0.42 * _sol_a_terra(SEAT_L[1] + s, ZB - t))
    # la foscor dels racons: sota els seients i al peu de les parets
    e.foscor('racons', (0, 0.5, ZB), (XW, 0.5, ZB), (XW, 0.5, zn), (0, 0.5, zn),
             lambda s, t: max(0.6 * max(0.0, 1 - s / 30), 0.6 * max(0.0, 1 - (XW - s) / 30)))
    # els seients i la gent, de lluny a prop (les files de darrere la càmera, fosques: el primer pla de l'esquerra)
    figs = tex['figures']
    for k in range(len(ROWS) - 1, -1, -1):
        zf = ROWS[k]
        if k >= R0:
            _seient(e, 'seients', SEAT_R[0], SEAT_R[1], zf)
        _seient(e, 'seients', SEAT_L[0], SEAT_L[1], zf, dark=(k < R0))
        for who, (row, x) in (('tecnic', TECNIC), ('iri', IRI), ('vet', VET)):
            if row == k:
                fig = figs[who]
                e.sprite(who, fig, (fig.width / 2, SEATED_FEET), (x, 0, zf - 4))
                for ax in (x - 22, x + 22):                              # els braços, per davant de qui seu
                    e.caixa('seients', ax - 2.5, ax + 2.5, 28, 44, zf + 4, zf + 14, CHROME, 2.6,
                            cares={'dalt': {'ramp': CHROME, 'lvl': 3.8}, 'davant': {'ramp': CHROME, 'lvl': 2.2}})
        if k == R0 + 2:                                                  # la Rius, dreta al passadís
            fig = figs['rius']
            e.foscor('ombra_rius', (RIUS[0] - 18, 0.5, RIUS[1] + 10), (RIUS[0] + 26, 0.5, RIUS[1] + 10),
                     (RIUS[0] + 26, 0.5, RIUS[1] - 30), (RIUS[0] - 18, 0.5, RIUS[1] - 30),
                     lambda s, t: 0.5 * max(0.0, 1 - ((s - 16) / 16) ** 2 - ((t - 14) / 16) ** 2) * 1.5)
            e.sprite('rius', fig, (34, 111), (RIUS[0], 0, RIUS[1]))
    # primer pla: la mampara de la cuina de davant, a la dreta, amb la cortina recollida
    e.quad('primer_pla', (178, HC, -14), (XW, HC, -14), (XW, 0, -14), (178, 0, -14), ramp=FOSC,
           lvl=lambda s, t, P: 2.0 + 0.9 * math.sin(s / 2.4 + t / 40) - (1.2 if s < 2 else 0) - t * 0.006)
    return e


# ─── Composició i llum ──────────────────────────────────────────────────────

def _proj(P):
    u, v, _ = CAM.projecta(P)
    return u, v


def _panell_P(k, dt=0.0):
    """El punt del món del centre de la finestreta k (al panell de l'esquerra)."""
    t = (WIN_T + dt) / _PANEL_LEN
    return (WTOP[0] * t, DADO + (WTOP[1] - DADO) * t, win_z(k))


def _raigs():
    """Els raigs de sol que entren per les finestretes (de prop) i baixen fins al terra del passadís."""
    out = []
    for k in range(R0, R0 + 5):
        if _persiana(k):
            continue
        A = _panell_P(k)
        pts = []
        for dz in (-WIN_RX * 0.8, WIN_RX * 0.8):
            Pa = (A[0], A[1], A[2] + dz)
            t = Pa[1] / -SOL[1]
            pts.append((Pa, (Pa[0] + SOL[0] * t, 0.0, Pa[2] + SOL[2] * t)))
        out.append([_proj(pts[0][0]), _proj(pts[1][0]), _proj(pts[1][1]), _proj(pts[0][1])])
    return out


def _fx():
    light = []
    for k in range(R0 - 1, R0 + 7):
        if _persiana(k):
            continue
        wx, wy = _proj(_panell_P(k))
        light.append(llum.wash(wx, wy, 70, (255, 140, 100), k=0.35, air=0.015, squash=0.9))
    cx, cy = _proj((125, 70, ZB - 20))
    light.append(llum.wash(cx, cy, 60, (255, 230, 190), k=0.3, air=0.02))
    for pts in _raigs():
        light.append(llum.haze(pts, (255, 180, 120), k=0.07, blur=4))
    tone = [llum.grade(contrast=1.12, pivot=70, sat=1.15, lift=(6, 2, 10))]
    bloom = [llum.bloom(thr=215, radii=((3, 0.4), (10, 0.25)))]
    return light, bloom, tone


@functools.lru_cache(maxsize=None)
def _textures():
    return {'panell': _panell_base(), 'figures': _figures()}


def _render(tex=None):
    cv = Canvas(light=LIGHT)
    e = escena(cv, tex or _textures())
    return cv.img, e


@functools.lru_cache(maxsize=None)
def _base():
    return _render()


def _amb_llum(img, bloom=True):
    light, bl, tone = _fx()
    return llum.apply(img, light + (bl if bloom else []) + tone)


@functools.lru_cache(maxsize=None)
def _base_llum():
    return _amb_llum(_base()[0])


def bg(cv):
    cv.img.paste(_base_llum())
    cv.P = cv.img.load()


PROPS = {}


def _frames():
    _, e = _base()
    out = []
    for i in range(NF):
        flat = _panell(frame=i, glass_only=True)
        capes = [e.capa(flat, {'panell_e'}), e.capa(flat.transpose(Image.FLIP_LEFT_RIGHT), {'panell_d'})]
        img = _base()[0].copy()
        for c in capes:
            img.alpha_composite(c)
        out.append(_diff(_amb_llum(img), _base_llum()))
    return out


ANIMS = {'enlairament': {'frames': _frames, 'frameDuration': 120}}

GEOMETRIA = {
    'things': {},
    'spawns': {},
    'walkable': [(200, 253), (267, 253), (267, 261), (200, 261)],
}
