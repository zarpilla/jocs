"""
El pati de la granja (Escena 1), a Terra-2, un matí de secada. Sala «de lluny» (persones de ≈83 px), ampla (1280: la
càmera segueix el personatge). EN 3D (hd640/tres_d.py), a 1×.

Una càmera alta (picat lleuger), amb l'horitzó a y = 110: la masia del pare, girada, ensenya la façana (cap al pati) i la
paret del costat, amb el teulat; l'olivera morta davant la paret; el pou, vist una mica des de dalt (la boca el·líptica,
la politja, la galleda); la bomba de Verne, un cub blanc amb tres cares i el tub que s'hi corba; la tanca que neix
darrere la bomba i fuig en diagonal cap al fons a la dreta; el panell del preu, gros, a la vora de la rasa; la
Canonada a l'horitzó, entre dunes; el camí del graner, que s'enfila cap al fons a la dreta fins al graner; la
carretera del port, que surt per la dreta; i unes roques fosques en primer pla. Les esquerdes del terra són grans a
prop i petites al fons; els camps tenen solcs que fugen cap a l'horitzó.

El detall (la façana de la masia, la bomba, l'olivera, el graner, el panell, el pal del port) ve del pati pla de
sempre (granja_estreta_comu.py), dibuixat de cara i projectat. PROPS: `precinte` (la porta del graner tancada amb el
cadenat de Verne i el paper groc). ANIMS: `pols` (la pols arran de terra) i
`llum_canonada`.

El món: x a la dreta (0 = la càmera), y amunt, z endavant; 1 unitat = 1 px a la distància on un personatge fa la seva
mida normal (z = 500). Al terra, l'escala d'un personatge és (v − 110) / 140, exacta.
"""
import functools
import math

import hd640  # noqa: F401  (posa la llibreria de dibuix a 640×360)

from hd.pix import Canvas, Light, H, hr
from hd.rooms.exterior import fbm, smooth
from hd640.rooms import granja_estreta_comu as G
from hd640.rooms.terra2_comu import (
    RH, EARTH, ADOBE, STONE, TILE, GREYW, WHITEP, BLACKT, GRASS, IRONR, HILL, PLANK, RUSTT,
    dust_sky, canonada, cracks, dust_wind_frames, llum_canonada_frames, BLUE, _diff)
from hd.rooms.comu import text
from hd640.tres_d import Camera, Escena, Llum

ROOM_W = 1280
HOR = 110                                          # l'horitzó (la càmera no mira avall: les verticals, verticals)
CAM = Camera(pos=(0, 140, 0), yaw=0.0, pitch=0.0, f=500, centre=(640, HOR))
CAN_U = 440                                        # la Canonada, a l'horitzó (x de pantalla)
SUN = (1010, 26)

LIGHT = Light(ambient=0.0, vignette=None, floor_fade=None)
LLUMS = [Llum((6000, 5000, 2000), 1e6, 2.0, power=1.0)]   # el sol, a dalt a la dreta (ombres cap a l'esquerra)
AMBIENT = -1.1

# La masia: girada 15°, la façana mira cap al pati
TH = math.radians(15)
NF = (math.sin(TH), 0.0, -math.cos(TH))            # la normal de la façana
TF = (math.cos(TH), 0.0, math.sin(TH))             # al llarg de la façana, d'esquerra a dreta
R = (-470.0, 0.0, 560.0)                           # el cantó de baix a la dreta de la façana
FW, FD = 208.0, 170.0                              # l'amplada de la façana i la fondària de la casa
LC = (R[0] - FW * TF[0], 0.0, R[2] - FW * TF[2])   # el cantó de l'esquerra
BK = (-NF[0] * FD, 0.0, -NF[2] * FD)              # cap enrere

POU = (-395.0, 650.0)                              # el centre del pou (x, z)
POU_R, POU_H = 26.0, 30.0
BOMBA = (-330.0, 730.0)
ARBRE = (-480.0, 700.0)
GRANER_X, GRANER_Z = 738.0, 1290.0                 # la porta del graner (el centre) i la façana
PORT = (740.0, 600.0)
SENYAL_PORT = (-55.0, 0, 610.0)                     # el pal «PORT →» que es veu des del pou (x, y, z)
PANELL = (-210.0, 1050.0)                         # (a una distància on el rètol es llegeix)
PANELL_HW, PANELL_HH = 68, 29                      # mitja amplada i mitja alçada: ≈ la mida del dibuix pla
TANCA0, TANCA1 = (-250.0, 790.0), (1000.0, 3300.0)
RASA_C, RASA_K = -38.0, -0.4                       # la rasa: x = RASA_C + RASA_K·z (fuig cap a la Canonada)
CAMI = ((100.0, 835.0), (GRANER_X, 1272.0))        # el camí del graner
CARRETERA = ((735.0, 583.0), 1.02)                 # la carretera del port: un punt i x/z cap a l'horitzó


def _add(a, b, k=1.0):
    return (a[0] + b[0] * k, a[1] + b[1] * k, a[2] + b[2] * k)


def _up(P, h):
    return (P[0], P[1] + h, P[2])


# El tub de la bomba al pou (punts del món): surt del costat de la bomba, fa un arc i es fica al pou.
TUB = [(BOMBA[0] - 10, 26, BOMBA[1] - 4), (BOMBA[0] - 22, 34, BOMBA[1] - 24), (POU[0] + 18, 36, POU[1] + 30),
       (POU[0] + 12, 33, POU[1] + 18), (POU[0] + 11, 26, POU[1] + 16)]


# ─── Les textures: el pati pla de sempre ─────────────────────────────────────

def _pla(fn):
    cv = Canvas(light=G.LIGHT, transparent=True)
    fn(cv)
    return cv.img


@functools.lru_cache(maxsize=None)
def _textures():
    return {
        'masia': _pla(G.masia),
        'bomba': _pla(G.bomba),
        'arbre': _pla(lambda cv: G.arbre(cv)),
        'graner': _pla(G.graner),
        'panell': _pla(G.panel),
        'cami': _pla(G.cami),
    }


# ─── El fons (en pantalla): el cel, les dunes, la Canonada ─────────────────────

def fons(cv):
    dust_sky(cv, HOR, sun=SUN)
    for x in range(ROOM_W):                                        # dunes: dues capes, amb desnivells
        h1 = HOR - 3 - 16 * fbm(x / 170, 0.3, 7) - 6 * fbm(x / 40, 0.9, 8)
        h2 = HOR - 1 - 7 * fbm(x / 70, 1.7, 9)
        for y in range(int(h1), HOR + 5):
            cv.put(x, y, HILL, 4.6 - (y - h1) * 0.04 + (fbm(x / 30, y / 6, 4) - 0.5) * 0.6, lit=0)
        for y in range(int(h2), HOR + 5):
            cv.put(x, y, HILL, 3.4 + (fbm(x / 8, y / 4, 3) - 0.5) * 0.8 - (y - h2) * 0.05, lit=0)
    canonada(cv, CAN_U, HOR + 1, haze=(230, 214, 180))


# ─── El terra (en el món) ────────────────────────────────────────────────────

def _dist_seg(x, z, A, B):
    dx, dz = B[0] - A[0], B[1] - A[1]
    u = max(0.0, min(1.0, ((x - A[0]) * dx + (z - A[1]) * dz) / (dx * dx + dz * dz)))
    return math.hypot(x - A[0] - dx * u, z - A[1] - dz * u), u


def _terra(s, t, P):
    x, z = P[0], P[2]
    # el pati: fang sec, clivellat (les cel·les són del món: grans a prop, petites al fons)
    far = smooth(700, 1800, z)
    c = cracks(int(x), int(z * 0.6), cell=22)
    lvl = 4.4 + (fbm(x / 60, z / 40, 17) - 0.5) * 1.2
    if c < 1.6 * (1 - far * 0.8):
        lvl -= 2.2 * (1 - far)
    elif c < 3.0:
        lvl += 0.5 * (1 - far)
    ramp_field = smooth(860, 980, z + (fbm(x / 40, 0, 5) - 0.5) * 80)
    # els camps: solcs que fugen cap a l'horitzó
    if ramp_field > 0:
        fur = math.sin(x / 9.0 * math.pi)
        lf = 4.0 + fur * 0.35 * (1 - smooth(950, 1700, z)) + (fbm(x / 80, z / 200, 11) - 0.5) * 1.0
        lvl = lvl * (1 - ramp_field) + lf * ramp_field
    # el camí del graner (i el tros que hi porta des del pati): terra trepitjada, amb les roderes
    for (A, B, hw) in ((CAMI[0], CAMI[1], 24.0), ((CAMI[0][0] - 260, 840.0), CAMI[0], 22.0)):
        d, _ = _dist_seg(x, z, A, B)
        if d < hw:
            rut = abs(d / hw - 0.45) < 0.12
            lvl = 5.6 + (hr(int(x) // 3, int(z) // 3) - 0.5) * 0.6 - (0.9 if rut else 0)
    # la carretera del port
    (rx, rz), k = CARRETERA
    if z > rz - 120:
        d = abs(x - (rx + k * (z - rz))) / math.sqrt(1 + k * k)
        hw = 26.0
        if d < hw:
            rut = abs(d / hw - 0.5) < 0.12
            lvl = 5.8 + (hr(int(x) // 3, int(z) // 4) - 0.5) * 0.6 - (0.8 if rut else 0)
    # la rasa del tub de Verne, tapada de pressa, fins a la Canonada
    if z > BOMBA[1] - 6:
        d = abs(x - (RASA_C + RASA_K * z)) / math.sqrt(1 + RASA_K * RASA_K)
        if d < 4.0:
            lvl = 5.4 + (hr(int(x), int(z), 8) - 0.5) * 1.6
        elif d < 5.5:
            lvl = 2.8
    return lvl


# ─── Les peces ──────────────────────────────────────────────────────────────

def cilindre(e, sid, cx, cz, r, y0, y1, ramp, lvl, n=32):
    """Un cilindre vertical: les facetes que es veuen. `lvl(angle, y, P)`."""
    for i in range(n):
        a0, a1 = 2 * math.pi * i / n, 2 * math.pi * (i + 1) / n
        p0 = (cx + r * math.cos(a0), cz + r * math.sin(a0))
        p1 = (cx + r * math.cos(a1), cz + r * math.sin(a1))
        e.quad(sid, (p0[0], y1, p0[1]), (p1[0], y1, p1[1]), (p1[0], y0, p1[1]), (p0[0], y0, p0[1]), ramp=ramp,
               lvl=lambda s, t, P: lvl(math.atan2(P[2] - cz, P[0] - cx), P[1], P))


def masia(e, tex):
    # el teulat: el vessant de la dreta (el de l'esquerra no es veu), de teules, amb el ràfec
    apex = _up(((LC[0] + R[0]) / 2, 0, (LC[2] + R[2]) / 2), 150)
    eave = _add(_up(R, 99), TF, 8)
    e.quad('masia', apex, _add(apex, BK), _add(eave, BK), eave, ramp=TILE, dues_cares=True,
           lvl=lambda s, t, P: 3.4 - (1.6 if s % 7 < 1.6 else 0) - (1.0 if t % 9 < 1.4 else 0) + t * 0.01
           + (fbm(s / 20, t / 10, 3) - 0.5) * 0.8)

    # la paret del costat (la de la dreta), amb el sòcol de pedra i un finestró
    def paret(s, t, P):
        y = P[1]
        if y < 12:
            return 3.0 + (0.8 if (int(s) // 9 + int(y) // 4) % 2 else 0) - (1.4 if s % 9 < 1 or y % 4 < 0.8 else 0)
        if 64 < s < 86 and 40 < y < 66:
            return 3.0 - (1.6 if (y % 4) < 1 else 0) - (1.2 if abs(s - 75) < 0.8 else 0)
        v = 3.6 + (fbm(s / 14, y / 10, 21) - 0.5) * 1.4
        if fbm(s / 22, y / 16, 61) > 0.68 and 20 < y < 90:
            v = 3.0 + (hr(int(s) // 9, int(y) // 5) - 0.5) - (1.8 if y % 5 < 1 else 0)
        return v
    e.quad('masia', _up(R, 102), _add(_up(R, 102), BK), _add(R, BK), R, ramp=ADOBE, lvl=paret)
    # sota el ràfec, la paret a l'ombra
    e.foscor('masia_ombra', _up(R, 102), _add(_up(R, 102), BK), _add(_up(R, 92), BK), _up(R, 92), lambda s, t: 0.5)
    # la façana: el dibuix pla (x 0..208, de y 26 a 186; la base, a y 184)
    e.quad('masia', _up(LC, 158), _up(R, 158), _up(R, -2), _up(LC, -2), tex=(tex['masia'], (0, 26, FW, 186)))


def pou(e):
    cx, cz = POU

    def pedra(a, y, P):
        row = int(y // 6)
        colf = a * 5 + (0.5 if row % 2 else 0)
        v = 3.4 + (hr(row, round(colf)) - 0.5) * 1.0
        if y % 6 < 1 or abs(colf - round(colf)) < 0.09:
            v -= 1.8
        return v
    cilindre(e, 'pou', cx, cz, POU_R, 0, POU_H, STONE, pedra)
    # la boca: la vora de pedra i el forat negre (vist des de dalt: una el·lipse)
    r, ri = POU_R, POU_R - 5
    sq = ((cx - r, POU_H, cz + r), (cx + r, POU_H, cz + r), (cx + r, POU_H, cz - r), (cx - r, POU_H, cz - r))
    e.quad('pou_vora', *sq, ramp=STONE,
           lvl=lambda s, t, P: 5.0 - (1.6 if abs(math.atan2(P[2] - cz, P[0] - cx) * 4 % 1) < 0.12 else 0),
           forma=lambda s, t: ri * ri <= (s - r) ** 2 + (t - r) ** 2 <= r * r)
    e.quad('pou_vora', *sq, ramp=BLACKT, lvl=lambda s, t, P: 0.2 + (t / (2 * r)) * 1.4,
           forma=lambda s, t: (s - r) ** 2 + (t - r) ** 2 < ri * ri)
    # els pals, la biga, la politja, la corda i la galleda
    for px in (cx - 22, cx + 22):
        e.caixa('pou_pals', px - 2, px + 2, POU_H, 74, cz - 2, cz + 2, GREYW, 3.2)
    e.caixa('pou_pals', cx - 27, cx + 27, 74, 78, cz - 3, cz + 3, GREYW, 3.6)
    e.tub('pou_pals', (cx, 67, cz - 3), (cx, 67, cz + 3), 5, IRONR, 2.6)
    e.cable('pou_pals', [(cx - 5, 67, cz), (cx - 5, POU_H + 2, cz)], PLANK, 3.4, gruix=0.8)
    e.cable('pou_pals', [(cx + 5, 67, cz), (cx + 5, 54, cz)], PLANK, 3.4, gruix=0.8)
    cilindre(e, 'pou_pals', cx + 5, cz, 6, 42, 54, IRONR, lambda a, y, P: 3.0 - (1.2 if abs(y - 49) < 0.8 else 0), n=12)


def bomba(e, tex):
    bx, bz = BOMBA
    # la bomba de Verne: blanca i neta; el davant, el dibuix pla (BX0..BX1, BY0..BY1)
    e.caixa_girada('bomba', bx, bz, 28, 16, 36, -0.15, WHITEP, 3.2,
                   cares={'davant': {'tex': (tex['bomba'], (G.BX0, G.BY0, G.BX1 + 1, G.BY1 + 1))},
                          'dalt': {'ramp': WHITEP, 'lvl': 5.4}, 'dreta': {'ramp': WHITEP, 'lvl': 3.0},
                          'esquerra': {'ramp': WHITEP, 'lvl': 2.4}})
    # el tub, blanc i nou, que fa un arc i es fica al pou: per trams, cadascun a la seva capa del davant (amb la línia
    # base de la seva profunditat), perquè qui es posa entre el pou i la bomba en tingui una part davant i una darrere
    for k, (A, B) in enumerate(zip(TUB, TUB[1:])):
        e.cable(f'tub{k}', [A, B], WHITEP, 4.6, gruix=3.0)


def tanca(e):
    (x0, z0), (x1, z1) = TANCA0, TANCA1
    n = int(math.hypot(x1 - x0, z1 - z0) // 44)
    tops = []
    for i in range(n + 1):
        u = i / n
        x, z = x0 + (x1 - x0) * u, z0 + (z1 - z0) * u
        lean = (hr(i, 3) - 0.5) * 3
        e.caixa('tanca', x - 1.5, x + 1.5, 0, 26 + lean, z - 1.5, z + 1.5, GREYW, 3.4)
        tops.append((x, z))
    for h in (10, 20):
        for (xa, za), (xb, zb) in zip(tops, tops[1:]):
            e.cable('tanca', [(xa, h, za), ((xa + xb) / 2, h - 1.4, (za + zb) / 2), (xb, h, zb)], GREYW, 4.0, gruix=0.9)


def panell(e, tex):
    """El panell del preu, gros, a la vora de la rasa, girat cap al pati."""
    cx, cz = PANELL
    tb = (math.cos(0.35), 0, math.sin(0.35))
    c = (cx, 62 + PANELL_HH, cz)
    hw, hh = PANELL_HW, PANELL_HH
    for k in (-40, 40):
        p = _add((cx, 0, cz), tb, k)
        e.caixa('panell', p[0] - 3, p[0] + 3, 0, 62, p[2] - 3, p[2] + 3, IRONR, 2.6)
    x0, y0 = G.PANEL
    e.quad('panell', _up(_add(c, tb, -hw), hh), _up(_add(c, tb, hw), hh), _up(_add(c, tb, hw), -hh),
           _up(_add(c, tb, -hw), -hh), tex=(tex['panell'], (x0 - 1, y0 - 1, x0 + 59, y0 + 25)))
    # La marca, AIGUA VERNE, s'ha de llegir: deformada amb el panell, les lletres de 3×5 es dentarien. Es torna a
    # pintar la franja (amb el seu color, projectada) i s'hi escriu el text pla, en píxels de pantalla, sense
    # deformar (el panell fa l'escorç; les lletres, rectes).
    def mon(fx, fy):
        return _up(_add(c, tb, -hw + (fx - (x0 - 1)) * 2 * hw / 60), hh - (fy - (y0 - 1)) * 2 * hh / 26)
    cv = e.cv
    franja = [CAM.projecta(mon(fx, fy))[:2] for fx, fy in ((x0 + 8, y0), (x0 + 58, y0), (x0 + 58, y0 + 8),
                                                            (x0 + 8, y0 + 8))]
    fu, fv, _ = CAM.projecta(mon(x0 + 56, y0 + 1))
    col = cv.P[int(fu), int(fv)][:3]
    for X, Y in e._scan(franja):
        cv.flat(X, Y, col)
    u, v, _ = CAM.projecta(mon(x0 + 9, y0 + 4.5))
    text(cv, 'AIGUA VERNE', round(u), round(v) - 2, None, 0, flat=BLUE[1])


def graner(e, tex):
    gx, gz = GRANER_X, GRANER_Z
    left, right = gx - (558 - 436), gx + (640 - 558)
    wall = gx - (558 - 472)                                        # la paret de l'esquerra (al pla, x = 472)
    # la paret del costat (la de l'esquerra), de taulons, a l'ombra, sota el ràfec
    e.quad('graner', (wall, 92, gz + 130), (wall, 92, gz + 1), (wall, 0, gz + 1), (wall, 0, gz + 130), ramp=GREYW,
           lvl=lambda s, t, P: 2.4 - (1.6 if (130 - s) % 8 < 1 else 0) + (fbm(s / 6, P[1] / 18, 41) - 0.5) * 1.0)
    e.quad('graner', (wall - 4, 98, gz + 134), (wall - 4, 98, gz + 1), (wall + 26, 120, gz + 1),
           (wall + 26, 120, gz + 134), ramp=RUSTT, lvl=lambda s, t, P: 2.8 + (0.8 if s % 5 < 2 else -0.4),
           dues_cares=True)
    e.quad('graner', (left, 128, gz), (right, 128, gz), (right, -2, gz), (left, -2, gz),
           tex=(tex['graner'], (436, 62, 640, 192)))


def roques(e):
    for (x, z, r, seed) in ((-92, 492, 34, 1), (-34, 472, 20, 2), (28, 500, 14, 3), (-150, 470, 12, 4)):
        e.roca('primer_pla', (x, 0, z), r, STONE, 1.6, seed=seed)
    for k, (x, z) in enumerate(((-128, 486), (8, 486), (52, 506))):          # herba seca entre les roques
        for j in range(5):
            a = 1.2 + (j - 2) * 0.22
            e.cable('primer_pla', [(x + j * 2, 0, z), (x + j * 2 + math.cos(a) * 10, math.sin(a) * 12 + hr(k, j) * 4, z)],
                    GRASS, 2.6, gruix=0.9)


def ombres(e):
    """Ombres curtes cap a l'esquerra (el sol és a dalt a la dreta)."""
    def ellipse(cx, cz, rx, rz, k=0.55):
        e.foscor('ombra', (cx - rx, 0.3, cz + rz), (cx + rx, 0.3, cz + rz), (cx + rx, 0.3, cz - rz),
                 (cx - rx, 0.3, cz - rz),
                 lambda s, t: k * min(1.0, 1.8 * max(0.0, 1 - ((s - rx) / rx) ** 2 - ((t - rz) / rz) ** 2)))
    ellipse(POU[0] - 22, POU[1] - 6, 40, 26)
    ellipse(BOMBA[0] - 16, BOMBA[1] - 4, 22, 14)
    ellipse(ARBRE[0] - 26, ARBRE[1] - 4, 34, 14, 0.4)
    ellipse(PANELL[0] - 30, PANELL[1] - 8, 66, 22, 0.4)
    ellipse(GRANER_X - 130, GRANER_Z + 40, 60, 80, 0.5)
    ellipse(-112, 492, 40, 16, 0.6)


def abeurador(e):
    e.foscor('ombra', (340, 0.3, 790), (420, 0.3, 790), (420, 0.3, 740), (340, 0.3, 740),
             lambda s, t: 0.5 * max(0.0, 1 - ((s - 40) / 40) ** 2 - ((t - 25) / 25) ** 2) * 1.6)
    e.caixa_girada('abeurador', 384, 768, 60, 16, 14, 0.3, STONE, 3.2,
                   cares={'dalt': {'ramp': STONE, 'lvl': lambda s, t, P: 0.8 if 3 < s < 57 and 3 < t < 13 else 5.0}})


# ─── Composició ─────────────────────────────────────────────────────────────

def escena(cv, tex, panell_terra=False):
    e = Escena(cv, CAM, LLUMS, ambient=AMBIENT)
    fons(cv)
    zn = 300
    e.quad('terra', (-80000, 0, 20000), (80000, 0, 20000), (80000, 0, zn), (-80000, 0, zn), ramp=EARTH, lvl=_terra)
    e.claror((-80000, 0.2, 20000), (80000, 0.2, 20000), (80000, 0.2, 900), (-80000, 0.2, 900), (232, 210, 170),
             lambda s, t: 0.6 * smooth(1400, 12000, 20000 - t))           # la calitja: el fons es confon amb el cel
    ombres(e)
    # de lluny a prop
    graner(e, tex)
    panell(e, tex)
    tanca(e)
    abeurador(e)
    bomba(e, tex)
    if panell_terra:
        panell_bomba_terra(e)
    e.sprite('arbre', tex['arbre'], (232, 188), (ARBRE[0], 0, ARBRE[1]), escala_img=1.5)
    pou(e)
    masia(e, tex)
    e.sprite('pal_port', tex['cami'], (621, 202), (PORT[0] - 20, 0, PORT[1] - 30))
    # un altre pal del port, a la vora de la tanca, que es veu des del pou: el camí continua cap a la dreta (tasca 073)
    e.sprite('senyal_port', tex['cami'], (621, 202), SENYAL_PORT)
    roques(e)
    return e


@functools.lru_cache(maxsize=None)
def _base():
    cv = Canvas(ROOM_W, light=LIGHT)
    e = escena(cv, _textures())
    for y in range(RH, H):                                         # sota la sala: negre
        for x in range(ROOM_W):
            cv.flat(x, y, (0, 0, 0))
    return cv.img, e


def bg(cv):
    img, _ = _base()
    cv.img.paste(img)
    cv.P = cv.img.load()


def precinte(cv):
    """Des de l'Escena 5, fins que s'obre: la porta del graner tancada, amb el cadenat de Verne (la ranura i el llum
    vermell) i el paper groc del precinte. El graner pla tancat, menys l'obert, projectat per la façana."""
    _, e = _base()
    obert = _textures()['graner']
    tancat = _pla(lambda c: G.graner(c, tancat=True))
    cv.img.alpha_composite(e.capa(G._diff(tancat, obert), {'graner'}))


def panell_bomba_terra(e):
    """El panell del davant de la bomba, desmuntat i deixat a terra al davant a l'esquerra (els cargols al costat)."""
    bx, bz = BOMBA
    x0, x1, z0, z1 = bx - 34, bx - 10, bz - 44, bz - 18
    e.quad('panell_terra', (x0, 0.6, z1), (x1, 0.6, z1 + 2), (x1, 0.6, z0 + 2), (x0, 0.6, z0), ramp=WHITEP,
           lvl=lambda s, t, P: 4.6 - (0.9 if s < 1.2 or t < 1.2 else 0))
    for k, (cx, cz) in enumerate(((bx - 6, bz - 20), (bx - 4, bz - 24), (bx - 8, bz - 26))):     # els cargols
        e.quad(f'cargol{k}', (cx, 0.8, cz + 1), (cx + 1.5, 0.8, cz + 1), (cx + 1.5, 0.8, cz), (cx, 0.8, cz),
               ramp=IRONR, lvl=2.4)


def bomba_oberta(cv):
    """Des que la Vet en treu els cargols (`bomba_llegida`): el panell a terra i, a la bomba, el forat amb el motor i
    l'etiqueta «7.788» (el dibuix pla obert, projectat per la cara del davant)."""
    base, _ = _base()
    tex = dict(_textures())
    tex['bomba'] = _pla(lambda c: (G.bomba(c), G.bomba_oberta(c)))
    c2 = Canvas(ROOM_W, light=LIGHT)
    escena(c2, tex, panell_terra=True)
    for y in range(RH, H):
        for x in range(ROOM_W):
            c2.flat(x, y, (0, 0, 0))
    cv.img.alpha_composite(_diff(c2.img, base))


PROPS = {'precinte': precinte, 'bomba_oberta': bomba_oberta}


def _frames_pols():
    return dust_wind_frames(_base()[0], 150, 258, n=64, step=10, k=0.55)


def _frames_llum():
    return llum_canonada_frames(CAN_U, s=1, w=ROOM_W)


ANIMS = {'pols': {'frames': _frames_pols, 'frameDuration': 110},
         'llum_canonada': {'frames': _frames_llum, 'frameDuration': 220}}


def _amo(ids):
    def mask(x, y):
        _, e = _base()
        return e.ids[e.amo[y * e.cv.w + x]] in ids
    return mask


def _v(z):
    return HOR + CAM.f * CAM.pos[1] / z


# Capes del davant: el personatge hi passa per darrere si té els peus més amunt (més lluny) que la seva base.
FRONT = [
    # el pou: el cilindre, i també els pals, la biga i la politja (si no, qui hi és darrere sembla que sigui a dins)
    {'id': 'davant_pou', 'mask': _amo({'pou', 'pou_pals'}), 'baseline': round(_v(POU[1])), 'zIndex': 20},
    {'id': 'davant_bomba', 'mask': _amo({'bomba'}), 'baseline': round(_v(BOMBA[1])), 'zIndex': 20,
     'props': ('bomba_oberta',)},          # (la bomba oberta, a la capa de la bomba: si no, la tancada la taparia)
    # els trams del tub, cadascun amb la profunditat del seu mig
    *[{'id': f'davant_tub{k}', 'mask': _amo({f'tub{k}'}), 'baseline': round(_v((A[2] + B[2]) / 2)), 'zIndex': 20}
      for k, (A, B) in enumerate(zip(TUB, TUB[1:]))],
    {'id': 'davant_arbre', 'mask': _amo({'arbre'}), 'baseline': round(_v(ARBRE[1])), 'zIndex': 20},
    {'id': 'davant', 'mask': _amo({'primer_pla', 'pal_port'}), 'baseline': 999, 'zIndex': 20},
]


# ─── Geometria (coordenades de sala, projectades) ─────────────────────────────

def _p(x, z, y=0.0):
    u, v, _ = CAM.projecta((x, y, z))
    return round(u), round(v)


def _rect(*Ps):
    pts = [CAM.projecta(P) for P in Ps]
    return (max(0, round(min(p[0] for p in pts))), max(0, round(min(p[1] for p in pts))),
            min(ROOM_W - 1, round(max(p[0] for p in pts))), min(RH - 1, round(max(p[1] for p in pts))))


def _facana(fx, fy):
    """Un punt del dibuix pla de la façana (x 0..208, y amb la base a 184) al món."""
    return (LC[0] + TF[0] * fx, 184 - fy, LC[2] + TF[2] * fx)


def _cercle(cx, cz, r, n=10):
    return [_p(cx + r * math.cos(2 * math.pi * i / n), cz + r * math.sin(2 * math.pi * i / n)) for i in range(n)]


_K_ARBRE = 1.5 * CAM.escala((ARBRE[0], 0, ARBRE[1]))
_AU, _AV = _p(*ARBRE)
_PORTA = _facana(103, 184)

# El terra on es camina (al món): el pati davant la casa i el pou, el camí del graner, i fins a la carretera del port;
# no arriba a les roques del primer pla. Forats: el pou, la bomba i la soca de l'olivera (s'hi pot passar per darrere).
def _davant_casa():
    """La vora del terra davant la façana i al llarg de la paret del costat (a 12 unitats de la casa)."""
    m = 12
    nr = (TF[0], TF[2])
    a = (LC[0] + NF[0] * m, LC[2] + NF[2] * m)                     # davant del cantó de l'esquerra
    b = (R[0] + NF[0] * m + nr[0] * m, R[2] + NF[2] * m + nr[1] * m)   # davant del cantó de la dreta
    c = (R[0] + BK[0] + nr[0] * m, R[2] + BK[2] + nr[1] * m)           # al final de la paret del costat
    # (la façana, de l'esquerra cap a la dreta, retallada on surt de pantalla per l'esquerra)
    zl = 475.0
    k = (zl - a[1]) / (b[1] - a[1]) if b[1] != a[1] else 0.0
    a = (a[0] + (b[0] - a[0]) * max(0.0, k), max(a[1], zl)) if a[1] < zl else a
    return [a, b, c]


_C = _davant_casa()
WALK_MON = ([(-640, 475)] + [(round(x), round(z)) for x, z in _C] +
            [(round(_C[2][0]) + 6, 800), (round(POU[0]) - 40, 800), (round(TANCA0[0]) - 20, 782),
             (-120, 830), (88, 853), (726, 1288), (750, 1252), (112, 817), (300, 735), (720, 735),
             (770, 610), (606, 475), (56, 475), (56, 548), (-142, 548), (-142, 475)])
_WALK = [_p(x, z) for x, z in WALK_MON]
_V_FONS, _V_PROP = min(v for _, v in _WALK), max(v for _, v in _WALK)

GEOMETRIA = {
    'things': {
        'porta_casa': {'rect': _rect(_facana(78, 104), _facana(128, 185)),
                       'walk': _p(_PORTA[0] + NF[0] * 26, _PORTA[2] + NF[2] * 26)},
        # tot el graner (de lluny, la porta sola és massa petita per encertar-la)
        'porta_graner': {'rect': _rect((GRANER_X - 140, 120, GRANER_Z), (GRANER_X + 84, 0, GRANER_Z)),
                         'walk': _p(GRANER_X, 1272)},
        'cami_port': {'rect': (1240, 196, ROOM_W - 1, 258), 'walk': _p(760, 640)},
        'senyal_port': {'rect': _rect((SENYAL_PORT[0] - 22, 40, SENYAL_PORT[2]), (SENYAL_PORT[0] + 22, 0, SENYAL_PORT[2])),
                        'walk': _p(SENYAL_PORT[0] - 10, SENYAL_PORT[2] + 40)},
        'pou': {'rect': _rect((POU[0] - 28, 80, POU[1] - 26), (POU[0] + 28, 0, POU[1] - 26)),
                'walk': _p(POU[0] + 10, POU[1] - 50)},
        'bomba': {'rect': _rect((BOMBA[0] - 18, 40, BOMBA[1] - 8), (BOMBA[0] + 18, 0, BOMBA[1] - 8)),
                  'walk': _p(BOMBA[0] + 30, BOMBA[1] - 6)},   # al costat: de perfil, no d'esquena (tasca 078)
        'canonada': {'rect': (CAN_U - 7, 0, CAN_U + 7, HOR - 1), 'walk': _p(-200, 760)},
        'panell_preu': {'rect': _rect((PANELL[0] - PANELL_HW, 62 + 2 * PANELL_HH, PANELL[1] - 22),
                                      (PANELL[0] + PANELL_HW, 0, PANELL[1] + 22)),
                        'walk': _p(-300, 760)},
        'arbre': {'rect': (round(_AU - 52 * _K_ARBRE), round(_AV - 90 * _K_ARBRE), round(_AU + 58 * _K_ARBRE), _AV),
                  'walk': _p(ARBRE[0] + 40, ARBRE[1] - 40)},
        'tanca': {'rect': _rect((TANCA0[0], 28, TANCA0[1]), (TANCA0[0] + 340, 0, TANCA0[1] + 600)),
                  'walk': _p(-240, 770)},
    },
    # (en Diu, a la vora del pou, entre els dos pals: així no en queda cap davant seu)
    'spawns': {'iri': (384, 242), 'vet': (442, 236), 'diu': _p(POU[0] + 8, POU[1] - POU_R + 2, POU_H)},
    'walkable': _WALK,
    # L'ombra de contacte dels personatges: el sol és a dalt a la dreta, l'ombra cau cap a l'esquerra i una mica cap
    # endavant (com les dels objectes); aixafada com el terra que veu la càmera a la distància del pati (140 / 500).
    # La càmera aixafa el terra: 140 d'alçada a ≈550 de fons (on es camina) → 0,25. Les direccions, sobre el terra.
    'floorSquash': 0.25,
    'characterShadow': {'enabled': True, 'color': '#2a1a10', 'alpha': 0.42, 'squash': 0.28, 'core': 0.6,
                        'light': {'x': -1, 'y': 0.12, 'direction': True, 'stretch': 0.7}},
    'forats': [_cercle(POU[0], POU[1], POU_R + 8), _cercle(BOMBA[0], BOMBA[1], 20, 8), _cercle(ARBRE[0], ARBRE[1], 10, 6)],
    'regions': [{'id': 'perspectiva', 'active': True, 'scaleEnabled': True, 'scaleWalkSpeed': True,
                 'scaleTop': round((_V_FONS - 2 - HOR) / CAM.pos[1], 3),
                 'scaleBottom': round((_V_PROP + 2 - HOR) / CAM.pos[1], 3),
                 'points': [(0, _V_FONS - 2), (ROOM_W - 1, _V_FONS - 2), (ROOM_W - 1, _V_PROP + 2),
                            (0, _V_PROP + 2)]}],
    # La llum de la sala sobre els personatges (characterLights del motor): el pati al ple sol del desert: neutra i
    # una mica càlida, el sol a dalt a la dreta.
    'characterLights': {
        'ambient': '#fbefe0',
        'lights': [
            {'x': ROOM_W + 200, 'y': -300, 'radius': 1600, 'color': '#fff2d8', 'intensity': 0.15},  # el sol: una mica més de llum, i càlida
        ],
    },
}
