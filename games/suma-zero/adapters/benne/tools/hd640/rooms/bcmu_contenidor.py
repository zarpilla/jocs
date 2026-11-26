"""
El carreró de darrere del BCMU (final de l'Acte 3, la Vet), a migdia. EN 3D (hd640/tres_d.py), a 1×.

Una càmera alta, al costat dret del carreró, que mira de biaix cap al fons a l'esquerra:
  - a l'esquerra, la **façana de darrere** del banc (la de 1958) fuig cap al fons: el sòcol de pedra encoixinada, el
    formigó dels pisos, les finestretes amb reixa, la porta de servei blau marí amb el llum i el graó, la placa de
    llautó «BCMU» i l'intèrfon; la **càmera** de vigilància, en un braç, mira la porta;
  - el **conducte** de les escombraries baixa per la paret i fa un colze cap enfora, i acaba amb la cortina de goma
    just damunt del **contenidor** verd, separat de la paret i una mica girat (la tapa mig oberta, el paper triturat
    que en treu el nas): s'hi pot passar per darrere; al costat, la caixa de cartró i les bosses;
  - al fons, la boca del carreró: el **carrer** de Ginebra assolellat, el tramvia que passa, la catenària, i a
    l'altra banda l'altre banc (lletres d'or i l'aparador de rellotges);
  - a la dreta, la paret de l'altra casa, a l'ombra; primer pla: unes bosses i un palet a baix a la dreta, una
    pilona a l'esquerra i els cables que travessen el carreró per dalt.
  - El sol, alt i del carrer, toca la part de dalt de la façana (amb l'ombra de la casa del davant en diagonal) i
    entra pel terra de la boca; el carreró és a l'ombra.

Tot el detall ve del dibuix pla de sempre (bcmu_contenidor_pla_comu.py): la façana, el davant del contenidor i del
conducte, la caixa, l'altre banc i el morro del tramvia es projecten. Animacions: `vent` (el paper triturat i la
cortina de goma, per les mateixes superfícies), `camera` (el llum vermell que parpelleja) i `paperet` (una ràfega
arrossega un full pel carreró).

El món: x a través del carreró (0 = la façana del banc), y amunt (0 = el terra), z cap al fons (ZS = la boca del
carreró); 1 unitat = 1 píxel de sala a la distància on un personatge fa ≈111 px (escala 1).
"""
import functools
import math

import hd640  # noqa: F401  (abans de cap hd.rooms: posa la llibreria a 640×360)
from hd640 import llum
from hd.pix import Canvas, Light, W, H, hr
from hd.rooms.comu import _diff, PLASTIC, SHEET
from hd.rooms.exterior import fbm
from hd640.rooms import bcmu_contenidor_pla_comu as PL
from hd640.rooms.bcmu_contenidor_pla_comu import (STONEW, CONC, ASPH, ZINC, BIN, SHRED, SKYD, FACADE, CARD, BAG,
                                                  PAPER, TRAM)
from hd640.tres_d import Camera, Escena, Llum

BOTTOM = 259                                       # la sala acaba aquí (a sota, la barra de verbs)
KZ = 0.88                                          # unitats del món per píxel del pla, al llarg de la façana
FZ0 = 40                                           # la x del pla que cau a z = 0
ZS = round((PL.STREET_X - FZ0) * KZ)               # la boca del carreró (on s'acaba la façana del banc)
XO = 330                                           # la paret de l'altra casa, a l'altra banda del carreró
HF = 700                                           # l'alçada de les façanes (fora de la pantalla)
NPIS = 5                                           # els pisos de dalt (el dibuix pla del primer, repetit)
TRAM_X = (240, 360)                                # el tram de façana que es repeteix (al dibuix pla: una finestra)
TRAM_F = TRAM_X[1] - TRAM_X[0]
ZV = ZS + 26                                       # la vorera de la boca: fins aquí
ZC = ZV + 170                                      # la calçada (amb les vies): fins aquí
ZF = ZC + 26                                       # l'altra vorera, i la façana de l'altre banc

CAM = Camera(pos=(300, 190, -560), yaw=-0.42, pitch=0.04, f=400, centre=(320, 120))   # de lluny: la persona, petita
LIGHT = Light(ambient=0.0, vignette=None, floor_fade=None)  # (la llum és la del món: la de l'Escena)
TL = Light(ambient=-0.1, vignette=None, floor_fade=None)    # la del dibuix pla de les textures

CONT = (112, 200, 70, 122, 64, -0.95)              # el contenidor: x, z del centre, fons, ample, alçada, gir
CHUTE = (CONT[1] - 17, CONT[1] + 17)               # el conducte: z de les dues cares
LAMP = (4, 128, None)                              # el llum de la porta (x, y; z = el centre de la porta)
CAMV = (6, 176, 150)                               # la càmera de vigilància: on s'agafa a la paret (x, y, z)
BOX = (22, CONT[1] + 110)                          # la caixa de cartró (x, z del centre)
BAGS = ((18, CONT[1] + 144, 1.0), (CONT[0] + 40, CONT[1] - 92, 0.85))   # les bosses (x, z, mida)
PALS = ((90, ZS - 26), (220, ZS - 26))             # les pilones de la boca
PILONA = (60, -150)                                # la pilona de més ençà (x, z)
FIRE = (-150, -40)                                 # l'escala d'incendis, a la façana del banc: z0, z1

SUN = (255, 236, 196)
SHADE = (150, 170, 200)

LLUMS = [Llum((170, 80, ZS - 30), 300, 1.3, power=1.3),               # la claror que entra del carrer
         Llum((LAMP[0] + 8, LAMP[1] - 8, 0), 110, 1.4, power=1.8)]     # (el llum de la porta: la z es posa a escena)


def _z(fx):
    """Una x del dibuix pla de la façana → la z del món."""
    return (fx - FZ0) * KZ


DOOR = (_z(83), _z(141))                           # la porta de servei (amb el marc): z0, z1
LAMP = (LAMP[0], LAMP[1], (DOOR[0] + DOOR[1]) / 2)
LLUMS[1] = Llum((LAMP[0] + 8, LAMP[1] - 8, LAMP[2]), 110, 1.4, power=1.8)


# ─── Les textures: el dibuix pla de sempre ───────────────────────────────────

@functools.lru_cache(maxsize=None)
def _tex_facana():
    """La façana del banc, de cara: el formigó, el sòcol, les finestres, la porta, la placa (sense el conducte, el
    contenidor ni les baixants, que són en 3D)."""
    cv = Canvas(light=TL)
    PL.wall(cv)
    PL.windows(cv)
    PL.service_door(cv)
    PL.plate(cv)
    return cv.img


@functools.lru_cache(maxsize=None)
def _tex_carrer():
    """L'altre banc, sense el tramvia (que és en 3D)."""
    cv = Canvas(light=Light(ambient=0.0, vignette=None, floor_fade=None))
    PL.street(cv, tram=False)
    return cv.img


def _tex_coses(wind=0.0):
    """El davant del contenidor (amb el paper que penja), el del conducte (amb la cortina) i la caixa de cartró."""
    cv = Canvas(light=TL, transparent=True)
    PL.chute(cv, wind)
    PL.container(cv, wind)
    PL.litter(cv)
    return cv.img


@functools.lru_cache(maxsize=None)
def _tex_coses_base():
    return _tex_coses()


CONT_BOX = (322, 152, 458, 217)                    # el davant del contenidor (sota la tapa, amb les rodes)
CHUTE_BOX = (376, 0, 404, 117)                     # el conducte
MOUTH_BOX = (369, 117, 411, 132)                   # la boca
CURTAIN_BOX = (369, 132, 411, 143)                 # la cortina de goma
CARD_BOX = (464, 160, 502, 214)                    # la caixa de cartró
FACADE_BOX = (PL.STREET_X, 29, W, 184)             # l'altre banc (de la cornisa a la vorera)


# ─── Les superfícies ────────────────────────────────────────────────────────

def _asfalt(s, t, P):
    """L'asfalt del carreró, en coordenades del món: gra, taques, esquerdes i el rec de llambordes al mig."""
    x, z = P[0], P[2]
    v = 3.0 + (fbm(x / 40, z / 24, 41) - 0.5) * 0.8 + (hr(int(x) // 2, int(z) // 2, 42) - 0.5) * 0.3
    if 150 <= x <= 172:                                                    # el rec de llambordes
        bx = int((x - 150 + (int(z // 6) % 2) * 4) // 7)
        if (x - 150 + (int(z // 6) % 2) * 4) % 7 < 1 or z % 6 < 1:
            return 2.2
        return 3.4 + (hr(bx, int(z // 6), 5) - 0.5) * 0.6
    crack = abs((x - 240) - math.sin(z / 30) * 14 - (z - 100) * 0.3) < 0.8 and 60 < z < 200
    if crack:
        v -= 1.0
    if fbm(x / 30 + 5, z / 18, 9) > 0.7:                                   # bassals secs, taques
        v -= 0.6
    return v


def _sol_terra(x, z):
    """El sol al terra (0..1): el carrer, i una llengua en diagonal que entra per la boca."""
    if z > ZS:
        return 1.0
    edge = ZS - 30 - (XO - x) * 0.35                                      # l'ombra de la casa del davant, en diagonal
    return max(0.0, min(1.0, (z - edge) / 12))


def _sol_facana(z, y):
    """El sol a la façana del banc (0..1): la part de dalt, sota la línia en diagonal de l'ombra del davant."""
    edge = 210 - (z - 120) * 0.42
    return max(0.0, min(1.0, (y - edge) / 10))


def ombra(e, sid, x, z, rx, rz, k=0.55, dx=-6, dz=-14):
    """Una ombra suau al terra sota una cosa (cap a la càmera i a l'esquerra: el sol ve del carrer)."""
    x, z = x + dx, z + dz
    e.foscor(sid, (x - rx, 0.6, z + rz), (x + rx, 0.6, z + rz), (x + rx, 0.6, z - rz), (x - rx, 0.6, z - rz),
             lambda s, t: k * max(0.0, 1 - ((s - rx) / rx) ** 2 - ((t - rz) / rz) ** 2) * 1.6)


def _local(cx, cz, ang, lx, y, lz):
    c, s_ = math.cos(ang), math.sin(ang)
    return (cx + lx * c - lz * s_, y, cz + lx * s_ + lz * c)


def carrer(e, tex):
    """El carrer de la boca: l'altre banc (i dues façanes al costat), les voreres, la calçada, les vies i el tramvia."""
    fac = tex['carrer']
    fw = (FACADE_BOX[2] - FACADE_BOX[0]) * 2.0
    fh = (FACADE_BOX[3] - FACADE_BOX[1]) * 2.0
    fx0 = 130
    # el cel de migdia, darrere de tot (més clar arran dels terrats)
    e.quad('cel', (-1400, 1400, ZF + 600), (2000, 1400, ZF + 600), (2000, 0, ZF + 600), (-1400, 0, ZF + 600),
           ramp=SKYD, lvl=lambda s, t, P: 1.0 + 3.6 * min(1.0, P[1] / 900) + (hr(int(s) // 40, int(t) // 14, 51) - 0.5) * 0.2)
    # les façanes del costat (estuc, finestres senzilles) i, al mig, l'altre banc
    def estuc(base, seed):
        def L(s, t, P):
            v = base + (hr(int(s) // 3, int(t) // 3, seed) - 0.5) * 0.3
            if t < 10:
                return base + 1.4                                          # la cornisa
            fx, fy = s % 60, (t - 30) % 70
            if 18 < fx < 42 and 10 < fy < 52 and t < 420:
                return 1.4 + (0.8 if fx - 18 < 3 else 0)                   # les finestres
            return v
        return L
    e.quad('carrer', (-600, fh + 150, ZF), (fx0, fh + 150, ZF), (fx0, 0, ZF), (-600, 0, ZF), ramp=FACADE, lvl=estuc(4.0, 3))
    e.quad('carrer', (fx0, fh, ZF), (fx0 + fw, fh, ZF), (fx0 + fw, 0, ZF), (fx0, 0, ZF), tex=(fac, FACADE_BOX))
    e.quad('carrer', (fx0, fh + 120, ZF + 2), (fx0 + fw, fh + 120, ZF + 2), (fx0 + fw, fh, ZF + 2), (fx0, fh, ZF + 2),
           ramp=FACADE, lvl=estuc(4.4, 4))
    e.quad('carrer', (fx0 + fw, fh + 90, ZF), (1200, fh + 90, ZF), (1200, 0, ZF), (fx0 + fw, 0, ZF), ramp=FACADE,
           lvl=estuc(3.6, 5))
    # les voreres i la calçada, al sol
    vorera = lambda s, t, P: 5.4 + (hr(int(P[0]) // 20, int(P[2]) // 20, 3) - 0.5) * 0.4 - (1.6 if P[0] % 20 < 1 else 0)  # noqa: E731
    e.quad('carrer', (-600, 4, ZF), (1200, 4, ZF), (1200, 4, ZC), (-600, 4, ZC), ramp=STONEW, lvl=vorera)
    e.quad('carrer', (-600, 4, ZC), (1200, 4, ZC), (1200, 0, ZC), (-600, 0, ZC), ramp=STONEW, lvl=6.0)

    def calcada(s, t, P):
        z = P[2]
        for rz in (ZV + 60, ZV + 74, ZV + 104, ZV + 118):                 # les vies
            if abs(z - rz) < 1.2:
                return 6.6
            if abs(z - rz) < 2.4:
                return 2.6
        return 4.4 + (hr(int(P[0]) // 2, int(z) // 2, 6) - 0.5) * 0.4
    e.quad('carrer', (-600, 0, ZC), (1200, 0, ZC), (1200, 0, ZV), (-600, 0, ZV), ramp=ASPH, lvl=calcada)
    e.quad('carrer', (-600, 4, ZV), (1200, 4, ZV), (1200, 4, ZS), (-600, 4, ZS), ramp=STONEW, lvl=vorera)
    e.quad('carrer', (-600, 4, ZV), (1200, 4, ZV), (1200, 0, ZV), (-600, 0, ZV), ramp=STONEW, lvl=6.4)
    # el tramvia que passa (el costat: les finestres, la franja blanca, el número) i el pantògraf
    tz0, tz1 = ZV + 52, ZV + 126

    def costat(s, t, P):
        if t < 4:
            return 4.4                                                     # el cantell del sostre
        if 60 < t < 68:
            return 6.0                                                     # la franja blanca
        if 12 < t < 54 and int(s) % 70 > 8:
            return 1.4 + (1.6 if (int(s) % 70) - 8 - (t - 12) * 0.4 in range(4, 12) else 0)   # finestres, reflex
        if 76 < t < 88 and 300 < s < 318:
            return 6.6                                                     # el número de línia (una placa)
        return 3.4 - (0.8 if t > 100 else 0)
    TX = 300                                                               # el morro: el tramvia entra per la dreta

    def morro(s, t, P):
        if t < 4:
            return 4.4
        if 10 < t < 56 and 6 < s < 68:
            return 1.6 + (1.8 if 4 < (s - 6) - (t - 10) * 0.5 < 12 else 0)   # el parabrisa, amb el reflex
        if 60 < t < 68:
            return 6.0
        if 84 < t < 92 and (8 < s < 16 or 58 < s < 66):
            return 7.0                                                     # els fars
        if 70 < t < 80 and 30 < s < 44:
            return 6.6                                                     # el número
        return 3.6
    e.caixa('tramvia', TX, 1400, 8, 124, tz0, tz1, TRAM, 3.0,
            cares={'davant': {'ramp': TRAM, 'lvl': costat}, 'dalt': {'ramp': ZINC, 'lvl': 4.0},
                   'esquerra': {'ramp': TRAM, 'lvl': morro}})
    e.cable('tramvia', [(TX + 60, 124, (tz0 + tz1) / 2), (TX + 40, 150, (tz0 + tz1) / 2), (TX + 70, 170, ZV + 90)],
            ZINC, 2.4, gruix=1.6)
    # la catenària
    for y, dz in ((206, 70), (198, 108)):
        e.cable('carrer', [(-600, y, ZV + dz), (300, y - 2, ZV + dz), (1200, y, ZV + dz)], [(20, 22, 28), (40, 44, 52)],
                1.0, gruix=1.2)


def facana(e, tex):
    """La façana del banc (x = 0) i, a dalt, més pisos; la cantonada de la boca; la paret de l'altra casa."""
    fa = tex['facana']
    zn = CAM.pos[2] + 40
    # la façana: el dibuix pla fins a la cantonada (de la z de la càmera a la boca)
    fx_n = FZ0 + zn / KZ
    za = max(zn, _z(0))
    e.quad('facana', (0, PL.FLOOR_Y, za), (0, PL.FLOOR_Y, ZS), (0, 0, ZS), (0, 0, za),
           tex=(fa, (max(0, fx_n), 0, PL.STREET_X, PL.FLOOR_Y)))
    # els pisos de dalt: les finestres del primer pis, repetides
    for k in range(NPIS):
        y0 = PL.FLOOR_Y + k * (PL.CORNICE - 2)
        e.quad('facana', (0, y0 + PL.CORNICE - 2, za), (0, y0 + PL.CORNICE - 2, ZS), (0, y0, ZS), (0, y0, za),
               tex=(fa, (max(0, fx_n), 0, PL.STREET_X, PL.CORNICE - 2)))
    # més ençà del dibuix pla (la càmera és lluny): un tram de la façana amb una finestra, repetit cap a la càmera
    z1 = za
    while z1 > zn:
        z0 = max(zn, z1 - TRAM_F * KZ)
        f0 = TRAM_X[1] - (z1 - z0) / KZ
        e.quad('facana', (0, PL.FLOOR_Y, z0), (0, PL.FLOOR_Y, z1), (0, 0, z1), (0, 0, z0),
               tex=(fa, (f0, 0, TRAM_X[1], PL.FLOOR_Y)))
        for k in range(NPIS):
            y0 = PL.FLOOR_Y + k * (PL.CORNICE - 2)
            e.quad('facana', (0, y0 + PL.CORNICE - 2, z0), (0, y0 + PL.CORNICE - 2, z1), (0, y0, z1), (0, y0, z0),
                   tex=(fa, (f0, 0, TRAM_X[1], PL.CORNICE - 2)))
        z1 = z0
    # el gruix de la cantonada (es veu el cantell, de pedra)
    e.quad('facana', (0, HF, ZS), (-40, HF, ZS), (-40, 0, ZS), (0, 0, ZS), ramp=STONEW,
           lvl=lambda s, t, P: 4.6 + (0.9 if int(t) % 16 == 0 else 0) + (hr(int(s) // 4, int(t) // 16, 2) - 0.5) * 0.4,
           dues_cares=True)
    # el sol a la part de dalt de la façana i el que rebota del carrer prop de la boca
    e.claror((0.5, HF, zn), (0.5, HF, ZS), (0.5, 0, ZS), (0.5, 0, zn), SUN,
             lambda s, t: 0.42 * _sol_facana(zn + s, HF - t))
    e.claror((0.5, 200, ZS - 120), (0.5, 200, ZS), (0.5, 0, ZS), (0.5, 0, ZS - 120), SUN,
             lambda s, t: 0.12 * max(0.0, s / 120) ** 2)
    # la paret de l'altra casa (x = XO), a l'ombra: arrebossat brut, una porta tancada i una baixant
    def arrebossat(s, t, P):
        z, y = P[2], P[1]
        if 120 < z < 176 and y < 104:                                       # una porta de ferro, tancada
            if y > 100 or z < 123 or z > 173:
                return 1.0
            return 2.2 + (0.8 if int(y) % 10 < 1 else 0) - (0.8 if abs(z - 148) < 0.8 else 0)
        if fbm(z / 60, y / 40, 15) > 0.45:                                  # l'arrebossat
            return 2.8 + (fbm(z / 12, y / 10, 16) - 0.5) * 0.6 - (0.5 if y < 30 else 0)
        row = int(y // 8)                                                   # el maó, on ha caigut
        if y % 8 < 1 or (z + (row % 2) * 12) % 24 < 1:
            return 1.4
        return 2.4 + (hr(int((z + (row % 2) * 12) // 24), row, 17) - 0.5) * 0.7
    BRICKO = [(20, 18, 20), (34, 30, 32), (50, 44, 44), (68, 60, 58), (88, 78, 74), (110, 98, 92), (134, 120, 112)]
    e.quad('altra', (XO, HF, ZS), (XO, HF, zn), (XO, 0, zn), (XO, 0, ZS), ramp=BRICKO, lvl=arrebossat)
    e.quad('altra', (XO, HF, ZS), (XO + 40, HF, ZS), (XO + 40, 0, ZS), (XO, 0, ZS), ramp=CONC, lvl=3.4, dues_cares=True)
    # una baixant, una caixa de comptadors i un llum de paret, apagat
    e.tub('altra', (XO - 6, HF, 300), (XO - 6, 6, 300), 4, ZINC, 2.4, brides=80, llum_dir=(-0.6, 0.6))
    e.caixa('altra', XO - 10, XO, 60, 104, 210, 246, CONC, 3.0,
            cares={'esquerra': {'ramp': CONC, 'lvl': lambda s, t, P: 3.6 - (1.6 if abs(t - 2) < 0.8 or abs(s - 18) < 0.6 else 0)}})
    e.caixa('altra', XO - 12, XO, 150, 160, 100, 112, ZINC, 3.4, cares={'sota': {'ramp': [(200, 200, 190), (240, 236, 220)], 'lvl': 1.0}})
    e.cable('altra', [(XO - 2, 150, 106), (XO - 2, 104, 214)], PLASTIC, 1.2, gruix=1.2)
    e.claror((XO - 0.5, HF, ZS), (XO - 0.5, HF, zn), (XO - 0.5, 0, zn), (XO - 0.5, 0, ZS), SUN,
             lambda s, t: 0.3 * max(0.0, min(1.0, (HF - t - 330 - s * 0.2) / 10)))


def terra(e):
    zn = CAM.pos[2] + 40
    e.quad('terra', (0, 0, ZS), (XO, 0, ZS), (XO, 0, zn), (0, 0, zn), ramp=ASPH, lvl=_asfalt)
    # la vorada sota la façana
    e.caixa('terra', 0, 6, 0, 3, zn, ZS, STONEW, 3.4, cares={'dalt': {'ramp': STONEW, 'lvl': 4.4}})
    # la reixa del desguàs, al rec, i una tapa de registre rodona
    e.quad('terra', (148, 0.3, 140), (174, 0.3, 140), (174, 0.3, 112), (148, 0.3, 112), ramp=ZINC,
           lvl=lambda s, t, P: 0.6 if int(t) % 4 < 2 and 2 < s < 24 else 2.4)
    e.quad('terra', (220, 0.3, 90), (252, 0.3, 90), (252, 0.3, 58), (220, 0.3, 58), ramp=ZINC,
           lvl=lambda s, t, P: 2.4 + (0.8 if int(s) % 4 < 2 else 0) - (1.0 if abs(math.hypot(s - 16, t - 16) - 15) < 1 else 0),
           forma=lambda s, t: math.hypot(s - 16, t - 16) < 16)
    # una llauna aixafada i una burilla
    e.caixa('terra', 200, 206, 0, 2, 186, 190, [(120, 30, 30), (190, 60, 50), (220, 210, 200)], 1.4)
    e.quad('terra', (120, 0.4, 212), (124, 0.4, 212), (124, 0.4, 211), (120, 0.4, 211), ramp=SHRED, lvl=3.0)
    # el sol: la llengua que entra per la boca, i la foscor al peu de les parets
    e.claror((0, 0.5, ZS + 2), (XO, 0.5, ZS + 2), (XO, 0.5, zn), (0, 0.5, zn), SUN,
             lambda s, t: 0.38 * _sol_terra(s, ZS + 2 - t))
    e.foscor('racons', (0, 0.6, ZS), (XO, 0.6, ZS), (XO, 0.6, zn), (0, 0.6, zn),
             lambda s, t: max(0.45 * max(0.0, 1 - s / 30), 0.4 * max(0.0, 1 - (XO - s) / 34)))


def porta(e):
    """El graó de pedra davant la porta de servei."""
    z0, z1 = DOOR
    e.caixa('porta', 0, 14, 0, 6, z0 - 8, z1 + 8, STONEW, 3.6, cares={'dalt': {'ramp': STONEW, 'lvl': 5.0}})
    e.foscor('porta', (0.5, 6, z0 - 8), (16, 0.6, z0 - 8), (16, 0.6, z1 + 8), (0.5, 6, z1 + 8), lambda s, t: 0.3)


def baixants(e):
    """Les baixants de zinc, rodones, amb les abraçadores."""
    for z in (_z(150) - 50, _z(507)):
        e.tub('baixants', (6, HF, z), (6, 8, z), 4, ZINC, 3.2, brides=70, llum_dir=(0.6, 0.6))
        e.caixa('baixants', 1, 12, 0, 10, z - 6, z + 6, ZINC, 2.4)


def camera_vigilancia(e, led=True):
    """La càmera, en un braç, que mira la porta (cap a la càmera de la sala i avall)."""
    x, y, z = CAMV
    e.caixa('camera', 0, 3, y - 8, y + 8, z - 5, z + 5, ZINC, 3.0)
    e.caixa('camera', 3, x + 14, y - 2, y + 1, z - 2, z + 1, ZINC, 2.6)
    # el cos, allargat cap a la porta (cap a -z) i una mica avall
    cx, cy, cz = x + 14, y - 6, z - 4
    e.caixa('camera', cx - 6, cx + 6, cy - 6, cy + 6, cz - 30, cz, SHEET, 4.4,
            cares={'dalt': {'ramp': SHEET, 'lvl': 5.4}, 'davant': {'ramp': PLASTIC, 'lvl': 0.8},
                   'dreta': {'ramp': SHEET, 'lvl': 3.8}})
    e.caixa('camera', cx - 8, cx + 8, cy + 6, cy + 8, cz - 36, cz + 2, SHEET, 5.0)          # la visera
    e.quad('camera', (cx + 6.2, cy + 3, cz - 20), (cx + 6.2, cy + 3, cz - 17), (cx + 6.2, cy, cz - 17),
           (cx + 6.2, cy, cz - 20), ramp=[(90, 24, 24), (240, 40, 36), (255, 130, 110)], lvl=2.0 if led else 0.0)
    e.cable('camera', [(2, y - 8, z), (2, y - 60, z + 2)], PLASTIC, 1.4, gruix=1.4)


def led_pos():
    x, y, z = CAMV
    return (x + 20.2, y - 4.5, z - 22.5)


def conducte(e, tex):
    """El conducte: baixa arran de paret, fa un colze cap enfora i acaba damunt del contenidor."""
    co = tex['coses']
    z0, z1 = CHUTE
    xb, yb = CONT[0] - 22, 92                              # la boca: x de la cara de la paret, y de baix
    ye = 176                                               # on comença el colze
    D = 30                                                 # el fons del conducte
    # el tram vertical, arran de paret
    e.caixa('conducte', 0, D, ye, HF, z0, z1, ZINC, 3.4,
            cares={'dreta': {'tex': (co, (CHUTE_BOX[0], 0, CHUTE_BOX[2], 58))},
                   'davant': {'ramp': ZINC, 'lvl': lambda s, t, P: 2.6 + (1.2 if int(t) % 64 < 2 else 0)}})
    for y in (ye + 60, ye + 160):                          # les abraçadores
        e.caixa('conducte', 0, D + 2, y, y + 4, z0 - 4, z1 + 4, ZINC, 2.6)
    # el colze: un tram inclinat, de (0, ye) a (xb, yb + 20)
    yc = yb + 22
    A0, A1 = (0, ye, z0), (D, ye, z0)
    B0, B1 = (xb, yc, z0), (xb + D, yc, z0)
    e.quad('conducte', (0, ye, z1), (0, ye, z0), (xb, yc, z0), (xb, yc, z1), ramp=ZINC, lvl=2.0)        # (el de sota)
    e.quad('conducte', A0, A1, B1, B0, ramp=ZINC, lvl=lambda s, t, P: 2.8 + (1.2 if abs(t - 30) < 1.5 else 0))
    e.quad('conducte', (D, ye, z0), (D, ye, z1), (xb + D, yc, z1), (xb + D, yc, z0),
           tex=(co, (CHUTE_BOX[0], 58, CHUTE_BOX[2], CHUTE_BOX[3])))
    # la boca, una mica més ampla, i la cortina de goma
    e.caixa('conducte', xb - 3, xb + D + 3, yb, yc, z0 - 3, z1 + 3, ZINC, 3.4,
            cares={'dreta': {'tex': (co, MOUTH_BOX)}, 'davant': {'ramp': ZINC, 'lvl': 3.0},
                   'dalt': {'ramp': ZINC, 'lvl': 4.2}})
    e.quad('cortina', (xb + D + 3.2, yb, z0 - 3), (xb + D + 3.2, yb, z1 + 3), (xb + D + 3.2, yb - 13, z1 + 3),
           (xb + D + 3.2, yb - 13, z0 - 3), tex=(co, CURTAIN_BOX))
    # l'ombra del conducte a la paret
    e.foscor('conducte', (0.5, HF, z1), (0.5, HF, z1 + 14), (0.5, ye - 10, z1 + 14), (0.5, ye - 10, z1),
             lambda s, t: 0.35)


def contenidor(e, tex, obert=False):
    """El contenidor, separat de la paret i una mica girat: el davant del dibuix pla, el costat amb nervis, la tapa
    mig oberta (amb el paper triturat a l'escletxa) i les rodes."""
    cx, cz, d, w, h, a = CONT
    co = tex['coses']
    ombra(e, 'ombres', cx, cz, d * 0.7, w * 0.6, k=0.6)

    def costat(s, t, P):
        v = 3.4 - t * 0.012 + (hr(int(s) // 3, int(t) // 3, 17) - 0.5) * 0.3
        if int(s) % 21 == 11:
            return v + 0.9
        if int(s) % 21 == 12:
            return v - 0.5
        if t < 5:
            return 4.4                                     # el reforç de dalt
        if h - 12 < t:
            return 1.2                                     # la part de sota (les rodes)
        return v
    e.caixa_girada('contenidor', cx, cz, d, w, h, a, BIN, 3.0,
                   cares={'dreta': {'tex': (co, CONT_BOX)}, 'davant': {'ramp': BIN, 'lvl': costat},
                          'darrere': {'ramp': BIN, 'lvl': costat}, 'esquerra': {'ramp': BIN, 'lvl': 2.6},
                          'dalt': {'ramp': SHRED, 'lvl': lambda s, t, P: 1.0 + hr(int(s) // 2, int(t) // 2, 3) * 2.2}})
    # les rodes del costat que es veu
    for lz in (-w / 2 + 14, w / 2 - 14):
        e.tub('contenidor', _local(cx, cz, a, d / 2 - 10, 5, lz - 3), _local(cx, cz, a, d / 2 - 10, 5, lz + 3), 5,
              PLASTIC, 2.0)
    # l'agafador del costat
    P0 = _local(cx, cz, a, -10, h - 10, -w / 2 - 3)
    P1 = _local(cx, cz, a, 10, h - 10, -w / 2 - 3)
    e.quad('contenidor', P0, P1, (P1[0], h - 16, P1[2]), (P0[0], h - 16, P0[2]), ramp=BIN, lvl=4.0)
    # la tapa: frontissa a darrere (cap a la paret), el davant aixecat (o oberta del tot)
    lift = 70 if obert else 8
    L = d + 6
    hx0 = -d / 2 - 2
    ang = math.atan2(lift, L)
    ex, ey = hx0 + L * math.cos(ang), h + L * math.sin(ang)
    Q0 = _local(cx, cz, a, hx0, h + 1, w / 2 + 3)
    Q1 = _local(cx, cz, a, ex, ey + 1, w / 2 + 3)
    Q2 = _local(cx, cz, a, ex, ey + 1, -w / 2 - 3)
    Q3 = _local(cx, cz, a, hx0, h + 1, -w / 2 - 3)

    def tapa(s, t, P):
        v = 4.6 + (hr(int(s) // 4, int(t) // 2, 19) - 0.5) * 0.3
        if s > L - 3:
            return 3.4                                     # el cantell del davant
        if int(t) % 30 < 2:
            return 3.6                                     # els nervis
        return v
    e.quad('contenidor', Q0, Q1, Q2, Q3, ramp=BIN, lvl=tapa, dues_cares=True)
    e.quad('contenidor', Q2, Q1, (Q1[0], Q1[1] - 3, Q1[2]), (Q2[0], Q2[1] - 3, Q2[2]), ramp=BIN, lvl=3.2,
           dues_cares=True)
    for lz in (-w / 2 + 6, w / 2 - 6):                    # els costats de la tapa (triangles foscos de l'escletxa)
        e.quad('contenidor', _local(cx, cz, a, hx0, h + 1, lz), _local(cx, cz, a, ex, ey, lz),
               _local(cx, cz, a, ex, h, lz), _local(cx, cz, a, hx0, h, lz), ramp=BIN, lvl=0.6, dues_cares=True,
               forma=lambda s, t, ex=ex: t < s * (ey - h) / max(1, ex - hx0) + 0.5)


def brossa(e, tex):
    """La caixa de cartró plegada, recolzada a la paret, i les bosses de documents (blau marí, lligades)."""
    bx, bz = BOX
    ombra(e, 'ombres', bx, bz, 20, 26, k=0.5)
    e.caixa_girada('caixa', bx, bz, 14, 42, 56, -0.12, CARD, 3.0,
                   cares={'dreta': {'tex': (tex['coses'], CARD_BOX)}, 'dalt': {'ramp': CARD, 'lvl': 4.0},
                          'davant': {'ramp': CARD, 'lvl': 2.4}})
    for x, z, k in BAGS:
        ombra(e, 'ombres', x, z, 18 * k, 14 * k, k=0.55)
        e.roca('bosses', (x, 0, z), 15 * k, BAG, lvl=2.4, llum_dir=(0.6, -0.5), aplana=0.9, seed=int(z) % 7 + 2)
        e.roca('bosses', (x, 22 * k, z), 4 * k, BAG, lvl=2.6, aplana=1.2, seed=3)


def primer_pla(e):
    """L'escala de gat de la paret del davant, una pilona a l'esquerra, i els cables que travessen el carreró."""
    FOSC = [(4, 5, 8), (9, 11, 16), (15, 18, 25), (22, 26, 34), (31, 36, 46), (42, 48, 60)]
    # l'escala de gat de la paret del davant, tallada per la vora
    # (de lluny, l'escala de gat i la pilona ja no són primer pla: tenen la seva capa, amb la seva línia de base)
    for z in (-6, 26):
        e.tub('escala_gat', (XO - 10, 0, z), (XO - 10, HF, z), 2.6, FOSC, 2.6, llum_dir=(-0.8, 0.3))
    for y in range(14, 400, 22):
        e.cable('escala_gat', [(XO - 10, y, -6), (XO - 10, y, 26)], FOSC, 2.4, gruix=2.0)
    for y in (16, 220):
        e.caixa('escala_gat', XO - 10, XO, y, y + 4, 8, 12, FOSC, 2.0)
    # la pilona
    e.tub('pilona_pp', (PILONA[0], 0, PILONA[1]), (PILONA[0], 70, PILONA[1]), 8, FOSC, 2.4, llum_dir=(0.8, 0.4))
    e.tub('pilona_pp', (PILONA[0], 70, PILONA[1]), (PILONA[0], 76, PILONA[1]), 9, FOSC, 3.2)
    # els cables que travessen el carreró per dalt, penjant
    for y, z0, z1 in ((236, -30, 0), (250, -10, 40)):
        e.cable('primer_pla', [(0, y, z0), (90, y - 50, (2 * z0 + z1) / 3), (200, y - 54, (z0 + 2 * z1) / 3),
                               (XO, y - 8, z1)], FOSC, 1.6, gruix=2.2)


def escala_incendis(e):
    """L'escala d'incendis de la façana del banc: replans de reixa a cada pis, la barana i els trams en ziga-zaga;
    a baix, l'última escala, plegada (no arriba a terra)."""
    FERRO = [(10, 12, 16), (20, 23, 28), (32, 36, 42), (46, 51, 58), (62, 68, 76), (82, 88, 96)]
    z0, z1 = FIRE
    D = 26                                                          # el que surt de la paret
    ys = [PL.FLOOR_Y + 8 + k * (PL.CORNICE - 2) for k in range(NPIS)]
    for k, y in enumerate(ys):
        e.caixa('incendis', 0, D, y - 2, y, z0, z1, FERRO, 2.6,
                cares={'dalt': {'ramp': FERRO, 'lvl': lambda s, t, P: 1.6 if int(s) % 4 == 0 or int(t) % 4 == 0 else 3.0}})
        for yy in (y + 12, y + 24):                                 # la barana
            e.cable('incendis', [(0, yy, z0), (D, yy, z0), (D, yy, z1), (0, yy, z1)], FERRO, 3.0, gruix=1.2)
        for z in range(int(z0), int(z1) + 1, 10):
            e.cable('incendis', [(D, y, z), (D, y + 24, z)], FERRO, 2.6, gruix=1.0)
        if k + 1 < len(ys):                                         # el tram cap al replà de dalt
            a, b = (z0 + 6, z1 - 30) if k % 2 == 0 else (z1 - 6, z0 + 30)
            yb = ys[k + 1]
            for x in (3, D - 3):
                e.cable('incendis', [(x, y, a), (x, yb - 2, b)], FERRO, 2.4, gruix=1.6)
            for j in range(1, 12):
                f = j / 12
                zz, yy = a + (b - a) * f, y + (yb - 2 - y) * f
                e.cable('incendis', [(3, yy, zz), (D - 3, yy, zz)], FERRO, 3.2, gruix=1.2)
    # l'escala plegada, sota el primer replà
    for x in (6, 18):
        e.cable('incendis', [(x, ys[0] - 2, z0 + 10), (x, ys[0] - 70, z0 + 10)], FERRO, 2.4, gruix=1.4)
    for yy in range(int(ys[0]) - 66, int(ys[0]) - 2, 9):
        e.cable('incendis', [(6, yy, z0 + 10), (18, yy, z0 + 10)], FERRO, 3.0, gruix=1.0)


def pilones(e):
    """Dues pilones de ferro a la boca del carreró (s'hi passa per darrere)."""
    for i, (x, z) in enumerate(PALS):
        ombra(e, 'ombres', x, z, 8, 6, k=0.55, dx=-4, dz=-8)
        e.tub(f'pilona{i}', (x, 0, z), (x, 52, z), 4.5, ZINC, 2.2, llum_dir=(0.7, 0.6))
        e.tub(f'pilona{i}', (x, 52, z), (x, 56, z), 5, ZINC, 3.6)


def escena(cv, tex, estat=frozenset()):
    """Tota la sala, de lluny a prop. `estat`: 'obert' (la tapa del contenidor oberta), 'sense_vent' (sense la
    cortina ni el paper que es mouen), 'led_apagat'. → l'Escena (qui ha pintat què)."""
    e = Escena(cv, CAM, LLUMS, ambient=-0.1)
    carrer(e, tex)
    facana(e, tex)
    terra(e)
    porta(e)
    baixants(e)
    escala_incendis(e)
    camera_vigilancia(e, led='led_apagat' not in estat)
    pilones(e)
    brossa(e, tex)
    contenidor(e, tex, obert='obert' in estat)
    conducte(e, tex)
    primer_pla(e)
    return e


# ─── Composició i llum ──────────────────────────────────────────────────────

def _proj(P):
    u, v, _ = CAM.projecta(P)
    return u, v


def _fx():
    bu, bv = _proj((165, 60, ZS + 40))
    lu, lv = _proj((LAMP[0] + 6, LAMP[1] - 6, LAMP[2]))
    light = [llum.wash(bu, bv, 220, (255, 236, 200), k=0.2, air=0.04, squash=0.7),     # la boca, al sol
             llum.wash(lu, lv, 60, (255, 220, 160), k=0.5, air=0.04)]                   # el llum de la porta
    tone = [llum.grade(contrast=1.06, pivot=70, sat=1.08, lift=(4, 6, 10), gamma=1.05)]
    bloom = [llum.bloom(thr=215)]
    return light, bloom, tone


@functools.lru_cache(maxsize=None)
def _textures():
    return {'facana': _tex_facana(), 'carrer': _tex_carrer(), 'coses': _tex_coses_base()}


def _render(estat=frozenset(), tex=None):
    cv = Canvas(light=LIGHT)
    e = escena(cv, tex or _textures(), estat)
    cv.rect(0, BOTTOM + 1, W - 1, H - 1, [(0, 0, 0)], 0, lit=0)    # la barra de verbs: negre
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


# ─── Animacions: el vent, el llum de la càmera i un full que vola ───────────

def _frames_vent():
    """El corrent del carreró mou el paper triturat i la cortina de goma (el dibuix pla del vent, projectat per les
    mateixes superfícies)."""
    img0, e = _base()
    base = _base_llum()
    out = []
    for i in range(12):
        capa = e.capa(_tex_coses(wind=i * math.tau / 12), {'contenidor', 'conducte', 'cortina'})
        img = img0.copy()
        img.alpha_composite(capa)
        out.append(_diff(_amb_llum(img), base))
    return out


def _frames_camera():
    """El llum vermell de la càmera: encès, i un instant apagat."""
    img0, e = _base()
    base = _base_llum()
    u, v = _proj(led_pos())
    img = img0.copy()
    P = img.load()
    for X in range(int(u) - 2, int(u) + 3):
        for Y in range(int(v) - 2, int(v) + 3):
            if 0 <= X < W and 0 <= Y < H and e.ids[e.amo[Y * W + X]] == 'camera':
                r, g, b, a = P[X, Y]
                if r > g + 40:                                             # (només els píxels vermells del llum)
                    P[X, Y] = (70, 22, 22, a)
    off = _diff(_amb_llum(img), base)
    on = _diff(base, base)
    return [on, on, off]


FLY = 54                       # fotogrames que el full és a la vista
REST = 11                      # i fotogrames de calma fins a la ràfega següent


def _frames_paperet():
    """Una ràfega arrossega un full des de la boca del carreró cap a la càmera, fent tombarelles: un quadret de paper
    del món, amb la seva ombra, que es fa gran en apropar-se."""
    _, e = _base()
    base = _base_llum()
    buit = _diff(base, base)
    out = []
    for i in range(FLY + REST):
        if i >= FLY:
            out.append(buit)
            continue
        t = i / (FLY - 1)
        x = 210 - t * 150 + math.sin(t * 7) * 20
        z = ZS + 30 - t * (ZS + 60)
        hop = abs(math.sin(i * 0.41)) * (26 - 14 * t)
        rot = i * 0.7
        cv = Canvas(light=LIGHT, transparent=True)
        e2 = Escena(cv, CAM, [], ambient=0.0)
        sx, sz = 9 * math.cos(rot), 9 * math.sin(rot)
        fl = abs(math.cos(i * 0.9))                                         # com de pla és (1) o de cantell (0)
        # l'ombra al terra
        u0, v0 = _proj((x, 0, z))
        k = CAM.escala((x, 0, z))
        img = base.copy()
        P = img.load()
        for yy in range(int(v0 - 2 * k), int(v0 + 2 * k) + 1):
            for xx in range(int(u0 - 7 * k), int(u0 + 7 * k) + 1):
                if 0 <= xx < W and 0 <= yy <= BOTTOM and ((xx - u0) / (7 * k)) ** 2 + ((yy - v0) / (2.2 * k)) ** 2 < 1:
                    if e.ids[e.amo[yy * W + xx]] in ('terra', 'carrer'):
                        r, g, b, a = P[xx, yy]
                        f = 0.7 if hop < 8 else 0.85
                        P[xx, yy] = (int(r * f), int(g * f), int(b * f), a)
        y = hop + 2
        h = 1 + 11 * fl
        e2.quad('full', (x - sx, y + h, z - sz), (x + sx, y + h, z + sz), (x + sx, y, z + sz), (x - sx, y, z - sz),
                ramp=PAPER, lvl=lambda s, tt, PP: 3.6 - (1.4 if int(tt) % 3 == 1 and 3 < s < 14 else 0),
                dues_cares=True)
        lay = cv.img
        L = lay.load()
        for Y in range(H):
            for X in range(W):
                if L[X, Y][3] and (Y > BOTTOM or e.ids[e.amo[Y * W + X]] == 'primer_pla'):
                    L[X, Y] = (0, 0, 0, 0)
        img.alpha_composite(lay)
        out.append(_diff(img, base))
    return out


ANIMS = {
    'vent': {'frames': _frames_vent, 'frameDuration': 170},
    'camera': {'frames': _frames_camera, 'frameDuration': 450},
    'paperet': {'frames': _frames_paperet, 'frameDuration': 52},
}


# ─── Capes del davant ─────────────────────────────────────────────────────────

def _amo(ids):
    def mask(x, y):
        _, e = _base()
        return e.ids[e.amo[y * e.cv.w + x]] in ids
    return mask


def _p(x, z, y=0.0):
    u, v, _ = CAM.projecta((x, y, z))
    return round(u), round(v)


FRONT = [
    {'id': 'davant', 'mask': _amo({'primer_pla'}), 'baseline': 999, 'zIndex': 20},
    {'id': 'davant_escala', 'mask': _amo({'escala_gat'}), 'baseline': _p(XO - 10, -6)[1], 'zIndex': 20},
    {'id': 'davant_pilona', 'mask': _amo({'pilona_pp'}), 'baseline': _p(*PILONA)[1], 'zIndex': 20},
    {'id': 'davant_contenidor', 'mask': _amo({'contenidor', 'conducte', 'cortina'}),
     'baseline': _p(CONT[0] + 10, CONT[1])[1], 'zIndex': 20},
    *[{'id': f'davant_pilona{i}', 'mask': _amo({f'pilona{i}'}), 'baseline': _p(*p)[1], 'zIndex': 20}
      for i, p in enumerate(PALS)],
]


# ─── Geometria (coordenades de sala, projectades) ────────────────────────────

def _rect_mon(*Ps):
    pts = [CAM.projecta(P) for P in Ps]
    return (max(0, round(min(p[0] for p in pts))), max(0, round(min(p[1] for p in pts))),
            min(W - 1, round(max(p[0] for p in pts))), min(BOTTOM, round(max(p[1] for p in pts))))


def _escala_a(v):
    """L'escala d'un personatge amb els peus a la y de pantalla `v`."""
    lo, hi = -100.0, 4000.0
    for _ in range(60):
        z = (lo + hi) / 2
        if CAM.projecta((165, 0, z))[1] > v:
            lo = z
        else:
            hi = z
    return CAM.escala((165, 0, (lo + hi) / 2))


def _v_a_escala(k):
    lo, hi = 0.0, 600.0
    for _ in range(40):
        v = (lo + hi) / 2
        if _escala_a(v) < k:
            lo = v
        else:
            hi = v
    return int(lo)


def _retalla_v(poly, vmax):
    """El polígon de pantalla retallat per sota de la y `vmax` (on l'escala arriba a ≈1,2)."""
    out = []
    for (ax, ay), (bx, by) in zip(poly, poly[1:] + poly[:1]):
        if ay <= vmax:
            out.append((ax, ay))
        if (ay <= vmax) != (by <= vmax):
            k = (vmax - ay) / (by - ay)
            out.append((round(ax + (bx - ax) * k), vmax))
    return out


# El terra on es camina (al món): el carreró, de la façana (passant per darrere del contenidor) fins a la paret del
# davant, i fins a la vorera de la boca; no arriba a la caixa ni a les bosses de la paret.
V_MAX = min(BOTTOM - 4, _v_a_escala(1.2))
WALK_MON = [(12, -100), (12, BOX[1] - 30), (BOX[0] + 16, BOX[1] - 26), (BOX[0] + 22, BAGS[0][1] + 18),
            (12, BAGS[0][1] + 26), (12, ZS - 6), (XO - 14, ZS - 6), (XO - 14, -100)]
_WALK = _retalla_v([_p(x, z) for x, z in WALK_MON], V_MAX)
_WALK = [(min(W - 1, max(0, u)), v) for u, v in _WALK]
_V_FONS, _V_PROP = min(v for _, v in _WALK), max(v for _, v in _WALK)
_FORAT_CONT = [_p(*_local(CONT[0], CONT[1], CONT[5], lx, 0, lz)[::2]) for lx, lz in
               ((-CONT[2] / 2 - 2, -CONT[3] / 2 - 4), (CONT[2] / 2 + 6, -CONT[3] / 2 - 4),
                (CONT[2] / 2 + 6, CONT[3] / 2 + 4), (-CONT[2] / 2 - 2, CONT[3] / 2 + 4))]
_FORAT_BOSSA = [_p(BAGS[1][0] + 16 * math.cos(k * math.pi / 3), BAGS[1][1] + 12 * math.sin(k * math.pi / 3))
                for k in range(6)]

_CONT_R = _rect_mon(*[_local(CONT[0], CONT[1], CONT[5], lx, y, lz) for lx in (-CONT[2] / 2, CONT[2] / 2)
                      for lz in (-CONT[3] / 2, CONT[3] / 2) for y in (0, CONT[4] + 12)],
                    (CONT[0] - 26, 120, CHUTE[0]), (CONT[0], 120, CHUTE[1]))
_CARRER = _rect_mon((0, 230, ZS), (XO, 230, ZS), (0, 0, ZS), (XO, 0, ZS))
_U_OMBRA = CAM.projecta((165 - 30, 0, 200 - 60))
_U_OMBRA0 = CAM.projecta((165, 0, 200))

GEOMETRIA = {
    'things': {
        'contenidor': {'rect': _CONT_R, 'walk': _p(*_local(CONT[0], CONT[1], CONT[5], CONT[2] / 2 + 40, 0, 0)[::2])},
        # (la sortida comença on acaba el contenidor: si no, se'n menjava la meitat de dalt)
        'carrer': {'rect': (max(_CARRER[0], _CONT_R[2] + 1), _CARRER[1], _CARRER[2], _CARRER[3]), 'walk': _p(165, ZS - 12)},
    },
    'spawns': {'vet': _p(200, 130)},
    'walkable': _WALK,
    'forats': [_FORAT_CONT, _FORAT_BOSSA],
    'floorSquash': 0.38,
    # el sol, alt i del carrer: les ombres de la gent cauen cap a la càmera i una mica a l'esquerra, curtes
    'characterShadow': {'enabled': True, 'color': '#141820', 'alpha': 0.4, 'squash': 0.36, 'core': 0.6,
                        'light': {'x': round(_U_OMBRA[0] - _U_OMBRA0[0], 2), 'y': round(_U_OMBRA[1] - _U_OMBRA0[1], 2),
                                  'direction': True, 'stretch': 0.5}},
    'regions': [{'id': 'perspectiva', 'active': True, 'scaleEnabled': True, 'scaleWalkSpeed': True,
                 'scaleTop': round(_escala_a(_V_FONS - 2), 3), 'scaleBottom': round(_escala_a(_V_PROP + 2), 3),
                 'points': [(0, _V_FONS - 2), (W - 1, _V_FONS - 2), (W - 1, _V_PROP + 2), (0, _V_PROP + 2)]}],
    # la llum de la sala sobre els personatges, en temps d'execució
    'characterLights': {
        'ambient': '#9ca6b8',                                                          # carreró a l'ombra, blavós
        'lights': [
            {'x': _p(165, ZS + 40, 60)[0], 'y': _p(165, ZS + 40, 60)[1], 'radius': 260, 'color': '#ffecc8',
             'intensity': 0.9},                                                        # la boca, al sol
            {'x': _p(LAMP[0], LAMP[2], LAMP[1])[0], 'y': _p(LAMP[0], LAMP[2], LAMP[1])[1], 'radius': 90,
             'color': '#ffdca0', 'intensity': 0.6},                                    # el llum de la porta
        ],
    },
}
