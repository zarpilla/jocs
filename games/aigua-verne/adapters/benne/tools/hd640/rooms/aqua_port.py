"""
Aigua Verne — `aqua_port` (L), Escena 3: el port d'Aqua, un planeta que era mar. EN 3D (hd640/tres_d.py), a 1×.

Som dalt del moll de pedra, blanc de sal, amb la càmera girada cap a la dreta: la vora del moll (la vorada de
coronament) fuig en diagonal cap al fons a la dreta, i a l'altra banda del buit l'escullera fuig cap a l'horitzó,
on hi ha el far: dos punts de fuga. On hi havia l'aigua del port, ara hi ha un forat: l'escullera s'enfonsa per sota de
la vora i el fons del mar sec (la plana de sal, amb la barca encallada al peu de l'escullera i els mercants lluny) només
es veu de lluny. A la cara de l'escullera, les ratlles de sal de l'aigua de cada any i l'**escala del port**, que baixa
graó a graó i s'acaba a l'aire. Al moll: la **grua** vella (el pedestal, la caseta girada amb tres cares, la ploma de
gelosia que surt cap a l'esquerra per damunt del buit, per davant del far) amb la **cistella** penjada sobre el forat;
norais, caixes de peix, el rètol PROHIBIT BANYAR-SE i el **panell del preu**, girat. A l'esquerra, la **Cantimplora**
(el model canònic de cantimplora_comu.py), aparcada de biaix: la popa amb els motors cap a la vora del moll, i el buc
panxut (el nom, la matrícula, els dipòsits) que ve cap a la càmera i surt del quadre per l'esquerra (el primer pla de
l'esquerra); la porta de la bodega oberta i encesa, i la **rampa** estesa fins al moll. A baix a la dreta, un norai i
una corda en primer pla. La **Canonada**, a l'horitzó.

Es passa per darrere de la grua (el moll continua entre el pedestal i la vora), de les caixes, del panell, del rètol, de
la rampa i de la popa de la nau.

Llum freda de migdia: el sol alt, una mica darrere a la dreta: ombres curtes cap endavant i a l'esquerra (també la de
la nau); la nau, barrejada amb el blanc fred del cel i la sal (`to`).

El detall (la caseta de la grua, la cistella, el far, la barca, els vaixells, el rètol i el
panell) ve del port pla de sempre (aqua_port_pla_comu.py), dibuixat de cara i projectat.
Decorat: `grua_arreglada` (llum verd a la cabina, projectat per la cara de la caseta). ANIMS: `calitja` (l'horitzó
tremola), `pols` (pols de sal), `llum_canonada` (el llum vermell del cim).

El món: x a la dreta, y amunt (0 = el moll), z endavant; 1 unitat = 1 px a la distància on un personatge fa la seva
mida normal (z = 500, en la direcció de la mirada). Al moll, l'escala d'un personatge és (v − HOR) / 140, exacta.
"""
import functools
import math

import hd640  # noqa: F401  (abans que cap hd.rooms: posa la llibreria a 640×360)

from hd.pix import Canvas, Light, W, H, hr
from hd.rooms.exterior import fbm, smooth
from hd640.rooms import aqua_port_pla_comu as PL
from hd640.rooms.aqua_comu import (RH, SALT, SAND, STONEA, ALGA, WOODG, PAINTW, RUSTA, OCHRE, STEELA, BLACKT, ROPEA,
                                   cel, canonada, canonada_llum, panell, calitja_frames, pols_frames, _voronoi)
from hd640.rooms.cantimplora_comu import Cantimplora
from hd640.tres_d import Camera, Escena, Llum

BOTTOM = RH - 1                                    # la sala acaba aquí (a sota, la barra de verbs)
HOR = 92                                           # l'horitzó (la càmera no mira avall: les verticals, verticals)
CAM = Camera(pos=(0, 140, 0), yaw=0.3, pitch=0.0, f=500, centre=(320, HOR))

LIGHT = Light(ambient=0.0, vignette=None, floor_fade=None)
LLUMS = [Llum((3000, 20000, 5000), 1e6, 2.0, power=1.0)]    # el sol, alt, darrere a la dreta
AMBIENT = -1.3

ZE = 760.0                                         # la vora del moll (al llarg de x)
D = 600.0                                          # el fons del mar, per sota del moll
TOPW = 200.0                                       # el cim de l'escullera (més alt que el moll)
# L'escullera, a l'altra banda del buit: la cara de dins va de N (fora del quadre, a la dreta) a la punta T, i fuig
# cap a l'esquerra; és prou lluny perquè se'n vegi el peu, al fons del mar, per damunt de la vora del moll.
ESC_N, ESC_T = (4800.0, 1800.0), (1730.0, 5220.0)
_EL = math.hypot(ESC_T[0] - ESC_N[0], ESC_T[1] - ESC_N[1])
ESC_D = ((ESC_T[0] - ESC_N[0]) / _EL, 0.0, (ESC_T[1] - ESC_N[1]) / _EL)   # al llarg de la cara (cap a la punta)
ESC_NN = (ESC_D[2], 0.0, -ESC_D[0])                # la normal de la cara (cap a la càmera)
ESC_ANG = math.atan2(ESC_D[2], ESC_D[0])
GRUA = (330.0, 600.0)                             # l'eix del pedestal de la grua (x, z)
PED_R, PED_H = 24.0, 118.0
CAS_ANG = -0.5                                     # la caseta, girada: el davant (la cabina) mira cap a la càmera
TIP = (250.0, 270.0, 1000.0)                       # la punta de la ploma, damunt el buit (cap a l'esquerra)
CIST_Y = 150.0                                     # l'alçada del ganxo de la cistella
CAIXES = (150.0, 560.0)                            # les caixes de peix (x, z)
RETOL = (470.0, 712.0)
PANELL = (590.0, 630.0)                            # el panell del preu (x, z), girat cap al moll
PANELL_ANG = -0.75
NORAIS = ((-10.0, ZE - 14), (700.0, ZE - 14))
NORAI_PROP = (395.0, 372.0)                        # el norai del primer pla, a baix a la dreta
# La Cantimplora (el model canònic, cantimplora_comu): aparcada a l'esquerra, de biaix, amb la popa (els motors) cap
# a la vora del moll i la proa que ve cap a la càmera i surt del quadre per l'esquerra; la porta, a babord (el costat
# que es veu), amb la rampa estesa fins al moll. (Les potes de l'altre costat, a popa, queden amagades darrere el buc.)
NAU = Cantimplora(popa=(-8.0, 731.0), rumb=math.radians(210), porta='babord')
PORTA_L, RAMPA_OUT, NR = NAU.PORTA_L, NAU.RAMPA_OUT, NAU.NR
SOL = (0.146, 0.973, 0.243)                        # cap al sol (el de LLUMS): ombres cap endavant i a l'esquerra
TO = ((214, 226, 242), 0.14)                       # la llum freda d'Aqua (el cel blanc, la sal): la nau s'hi barreja
VAIXELLS = ((-300.0, 9000.0, 1), (-2600.0, 15000.0, 2))
VELERO = (60.0, 6200.0)


def _esc(s, y=0.0, n=0.0):
    """Un punt de la cara de l'escullera: `s` unitats des de N cap a la punta, a l'alçada `y`, `n` cap enfora."""
    return (ESC_N[0] + ESC_D[0] * s + ESC_NN[0] * n, y, ESC_N[1] + ESC_D[2] * s + ESC_NN[2] * n)


BARCA = _esc(_EL - 200, -D, 340)                   # la barca encallada, al peu de l'escullera
STAIR = [(_EL - 2300 + i * 70, TOPW - 4 - i * 38) for i in range(13)]   # els graons (s, y del trepig), de dalt a baix

QUAY = PL.QUAY
WETST = PL.WETST
BOX = [(30, 50, 70), (46, 74, 98), (66, 100, 126), (92, 128, 152), (124, 158, 178), (166, 192, 206)]


def _add(a, b, k=1.0):
    return (a[0] + b[0] * k, a[1] + b[1] * k, a[2] + b[2] * k)


def _uv(P):
    u, v, _ = CAM.projecta(P)
    return u, v


CAN_U = round(_uv((6000.0, 0.0, 40000.0))[0])     # la Canonada, a l'horitzó
CAN_LY = 18


# ─── Les textures: el port pla de sempre ─────────────────────────────────────

def _pla(fn, C=Canvas):
    cv = C(light=PL.LIGHT, transparent=True)
    fn(cv)
    return cv.img


@functools.lru_cache(maxsize=None)
def _textures():
    return {
        'caseta': _pla(PL.caseta),
        'cistella': _pla(PL.cistella),
        'far': _pla(PL.far),
        'barca': _pla(PL.barca),
        'vaixell1': _pla(lambda cv: PL.vaixell_lluny(cv, 100, 100, 0.95, 0.07, 1)),
        'vaixell2': _pla(lambda cv: PL.vaixell_lluny(cv, 100, 100, 0.5, -0.03, 2)),
        'velero': _pla(lambda cv: PL.velero(cv, 100, 100)),
        'retol': _pla(lambda cv: PL.retol(cv, 100, 100)),
        'panell': _pla(lambda cv: panell(cv, 100, 100)),
    }


# ─── El fons (en pantalla): el cel, l'illa, la Canonada ─────────────────────────

def fons(cv):
    cel(cv, HOR)
    for y in range(HOR + 1, RH):                                   # (sota l'horitzó, la calitja; el fons ho tapa)
        for x in range(W):
            cv.put(x, y, SALT, 6.4, lit=0)
    # l'illa que ara és una muntanya: una mesa blavosa a l'horitzó
    for x in range(150, 236):
        u = (x - 150) / 86
        top = HOR - 1 - 8 * smooth(0, 0.2, u) * (1 - smooth(0.75, 1, u)) - 2 * fbm(x / 9, 0.3, 4)
        for y in range(int(top), HOR + 1):
            lvl = 4.4 + (0.6 if y - top < 1.2 else 0) - (0.5 if int(y - top) % 3 == 2 else 0)
            cv.put(x, y, PL.SKYA, lvl + (fbm(x / 6, y / 2, 5) - 0.5) * 0.6, lit=0)
    canonada(cv, CAN_U, HOR, w0=1.8, w1=3.8, light_y=CAN_LY)


# ─── Les superfícies ────────────────────────────────────────────────────────

def _fons_mar(s, t, P):
    """El fons del mar sec: la plana de sal (crostes poligonals, taques de fang, rierols secs) i, al peu de
    l'escullera, sorra amb ondulacions. Tot en coordenades del món: s'empetiteix sol cap a l'horitzó."""
    x, z = P[0], P[2]
    far = smooth(9000, 30000, z)
    lvl = 5.6
    mud = fbm(x / 900 + 3, z / 1800, 12)
    lvl -= smooth(0.52, 0.72, mud) * 1.6
    riu = abs(fbm(x / 1500 + 7, z / 5000, 7) - 0.5)
    if riu < 0.016:
        lvl -= 1.3 * (1 - far)
    edge, cid = _voronoi(x / 160, z / 110, 3)
    near = 1 - far
    if edge < 0.06:
        lvl += 0.9 * near
    elif edge < 0.12:
        lvl -= 0.6 * near
    lvl += (hr(*cid, 3) - 0.5) * 0.6 * near
    # la sorra al peu de l'escullera
    dn = (x - ESC_N[0]) * ESC_NN[0] + (z - ESC_N[1]) * ESC_NN[2]  # la distància a la cara de l'escullera
    sorra = 1 - smooth(150, 600, dn)
    if sorra > 0:
        rip = math.sin(dn / 30 + fbm(x / 80, z / 120, 31) * 5)
        ls = 5.4 + (0.8 if rip > 0.7 else -0.7 if rip < -0.5 else 0) + (fbm(x / 60, z / 40, 30) - 0.5) * 0.8
        lvl = lvl * (1 - sorra) + ls * sorra
    return lvl


def _escullera(s, t, P):
    """La cara de dins de l'escullera: carreus grans (s = z, t = des del cim), les algues seques a baix, i les ratlles
    de sal de l'aigua de cada any, cada vegada més avall."""
    y = P[1]
    row = int(t // 34)
    off = 40 if row % 2 else 0
    col = int((s + off) // 80)
    fr, fc = (t % 34) / 34, ((s + off) % 80) / 80
    lvl = 4.4 + (hr(row, col, 7) - 0.5) * 0.9 + (fbm(s / 60, t / 40, 8) - 0.5) * 0.8
    joint = fr < 0.09 or fc < 0.035
    if joint:
        lvl -= 1.4
    elif fr < 0.2:
        lvl += 0.5                                                 # el cantell de dalt de cada carreu
    alg = -170 + (fbm(s / 90, 0.5, 13) - 0.5) * 60
    if y < alg:
        a = min(1.0, (alg - y) / 400)
        spot = fbm(s / 30, t / 22, 12)
        if spot > 0.58 + a * 0.1:
            return (ALGA, 2.4 + (spot - 0.58) * 4 - (1.0 if joint else 0))
        return (WETST, lvl - 0.8 - a * 0.6)
    for m in (40, -60, -150, -230, -300, -360):                    # les marques de l'aigua
        d = y - m + (fbm(s / 40, m, 14) - 0.5) * 8
        if abs(d) < 2.2 and fbm(s / 20, m / 7, 15) > 0.4:
            return (SALT, 7.0 if y > alg else 6.0)
        if -6 < d < -2.2 and hr(int(s) // 6, int(m), 1) < 0.3:
            return (SALT, 5.0)
    return (STONEA, lvl)


def _moll(s, t, P):
    """El terra del moll: lloses grans de calcària clara, a timba, amb sal a les juntes i taques de sal seca."""
    x, z = P[0], P[2]
    row = math.floor(z / 64)
    off = 50 if row % 2 else 0
    col = math.floor((x + off) / 100)
    lz, lx = z - row * 64, (x + off) - col * 100
    lvl = 6.0 + (hr(row, col, 40) - 0.5) * 0.9 + (fbm(x / 160, z / 60, 41) - 0.5) * 0.6
    if lz < 1.6 or lx < 1.6:
        if fbm(x / 20, z / 20, 42) > 0.6:
            return 7.6                                             # sal a la junta
        return 3.0
    if lz > 61:
        lvl += 0.7                                                 # el cantell de cada llosa, al sol
    salt = fbm(x / 110, z / 70, 43)
    if salt > 0.64:
        lvl += 1.0 + (0.8 if hr(int(x), int(z), 44) > 0.9 else 0)
    # la sal acumulada contra la vorada
    lvl += 1.4 * smooth(ZE - 70, ZE - 26, z) * (0.6 + 0.4 * fbm(x / 30, 0.5, 52))
    # esquerdes
    c = abs(fbm(x / 70 + 5, z / 50, 45) - 0.5)
    if c < 0.012:
        lvl -= 2.2
    return lvl


def cilindre(e, sid, cx, cz, r, y0, y1, ramp, lvl, n=24, r1=None):
    """Un cilindre vertical (o un tronc de con, amb `r1` a dalt): les facetes que es veuen. `lvl(angle, y, P)`."""
    r1 = r if r1 is None else r1
    for i in range(n):
        a0, a1 = 2 * math.pi * i / n, 2 * math.pi * (i + 1) / n
        e.quad(sid, (cx + r1 * math.cos(a0), y1, cz + r1 * math.sin(a0)), (cx + r1 * math.cos(a1), y1, cz + r1 * math.sin(a1)),
               (cx + r * math.cos(a1), y0, cz + r * math.sin(a1)), (cx + r * math.cos(a0), y0, cz + r * math.sin(a0)),
               ramp=ramp, lvl=lambda s, t, P: lvl(math.atan2(P[2] - cz, P[0] - cx), P[1], P))


def _ombra(e, cx, cz, rx, rz, k=0.55, dx=-0.35, dz=-0.25, y=0.3):
    """Una ombra curta (el sol és alt): una el·lipse al terra, una mica cap endavant i a l'esquerra."""
    cx, cz = cx + dx * rx, cz + dz * rz
    e.foscor('ombra', (cx - rx, y, cz + rz), (cx + rx, y, cz + rz), (cx + rx, y, cz - rz), (cx - rx, y, cz - rz),
             lambda s, t: k * min(1.0, 1.8 * max(0.0, 1 - ((s - rx) / rx) ** 2 - ((t - rz) / rz) ** 2)))


# ─── Les peces ──────────────────────────────────────────────────────────────

def escullera(e, tex):
    e.retalls = (0, 0, W, 206)                                     # (per sota, el moll ho tapa tot)
    # el fons del mar
    e.quad('fons_mar', (-80000, -D, 40000), (80000, -D, 40000), (80000, -D, ZE), (-80000, -D, ZE), ramp=SALT,
           lvl=_fons_mar)
    # l'ombra de l'escullera al seu peu (és a contrallum: la cara mira cap a nosaltres)
    e.foscor('ombra', _esc(0, -D + 0.5), _esc(_EL, -D + 0.5), _esc(_EL, -D + 0.5, 220), _esc(0, -D + 0.5, 320),
             lambda s, t: 0.5 * (1 - smooth(0.3, 1.0, t / 300)))
    # els vaixells lluny i la barca, a la plana
    for (x, z, k) in VAIXELLS:
        e.sprite('vaixells', tex[f'vaixell{k}'], (135 if k == 1 else 118, 109), (x, -D, z),
                 escala_img=25.0 if k == 1 else 30.0)
    e.sprite('vaixells', tex['velero'], (118, 106), (VELERO[0], -D, VELERO[1]), escala_img=7.0)
    # la calitja: el fons es confon amb el cel
    e.claror((-80000, -D + 0.2, 40000), (80000, -D + 0.2, 40000), (80000, -D + 0.2, ZE), (-80000, -D + 0.2, ZE),
             (226, 234, 242), lambda s, t: 0.15 + 0.6 * smooth(2000, 30000, 40000 - t))
    # la paret de l'escullera (la cara de dins) i el parapet
    e.quad('escullera', _esc(0, TOPW), _esc(_EL, TOPW), _esc(_EL, -D), _esc(0, -D), ramp=ESC, lvl=ESC.lvl(_escullera),
           dues_cares=True)
    mid = _esc(_EL / 2, 0, -150)
    e.caixa_girada('escullera', mid[0], mid[2], _EL + 10, 312, 16, ESC_ANG, STONEA, 5.6, y0=TOPW,
                   cares={'davant': {'ramp': STONEA, 'lvl': lambda s, t, P: 6.2 - (1.4 if s % 140 < 8 else 0)}})
    e.sprite('vaixells', tex['barca'], (424, 196), BARCA, escala_img=6.0)   # (davant la paret)
    # la calitja del forat: com més avall, més blavosa
    e.claror(_esc(0, TOPW, 0.5), _esc(_EL, TOPW, 0.5), _esc(_EL, -D, 0.5), _esc(0, -D, 0.5), (214, 226, 238),
             lambda s, t: 0.15 + 0.3 * smooth(80, D + TOPW, t))
    # l'escala del port: graons que surten de la paret i baixen fins a l'aire; la barana de ferro rovellat
    for i, (sp, y) in enumerate(STAIR):
        last = i == len(STAIR) - 1
        c = _esc(sp, 0, 30 if not last else 18)
        e.caixa_girada('escala', c[0], c[2], 70, 60 if not last else 36, 22, ESC_ANG + math.pi, STONEA, 4.2,
                       y0=y - 22, cares={'dalt': {'ramp': STONEA, 'lvl': 7.2}, 'davant': {'ramp': STONEA, 'lvl': 3.2},
                                         'darrere': {'ramp': STONEA, 'lvl': 3.2},
                                         'esquerra': {'ramp': STONEA, 'lvl': 4.0}, 'dreta': {'ramp': STONEA, 'lvl': 4.0}})
        e.foscor('ombra', _esc(sp - 35, y - 22, 0.6), _esc(sp + 45, y - 22, 0.6), _esc(sp + 45, y - 90, 0.6),
                 _esc(sp - 35, y - 90, 0.6), lambda s, t: 0.5 * max(0.0, 1 - t / 68))
    for i in range(0, len(STAIR) - 1, 2):
        sp, y = STAIR[i]
        e.cable('escala', [_esc(sp, y, 54), _esc(sp, y + 50, 54)], RUSTA, 3.0, gruix=3.0)
    rail = [_esc(sp, y + 50, 54) for sp, y in STAIR[:-2]]
    sp, y = STAIR[-2]
    rail.append(_esc(sp + 60, y + 4, 60))                          # l'últim tros, doblegat cap avall
    e.cable('escala', rail, RUSTA, 3.8, gruix=3.4)
    # el far, a la punta
    e.sprite('far', tex['far'], (344, 98), _esc(_EL - 90, TOPW + 16, -140), escala_img=8.0)
    e.retalls = None


class _Rampes:
    """Diverses rampes en una (per a una superfície procedural que canvia de material): el nivell 100·k + 50 + l és el
    nivell l de la rampa k (el dither i la llum del món hi continuen sumant)."""

    def __init__(self, *ramps):
        self.r = ramps

    def __len__(self):
        return 100 * len(self.r)

    def __getitem__(self, i):
        k, j = divmod(i, 100)
        ramp = self.r[min(k, len(self.r) - 1)]
        return ramp[max(0, min(len(ramp) - 1, j - 50))]

    def lvl(self, fn):
        idx = {id(r): k for k, r in enumerate(self.r)}

        def L(s, t, P):
            ramp, l = fn(s, t, P)
            return 100 * idx[id(ramp)] + 50 + l
        return L


ESC = _Rampes(STONEA, WETST, ALGA, SALT)


def moll(e):
    zn = 300
    e.quad('moll', (-3000, 0, ZE - 24), (3000, 0, ZE - 24), (3000, 0, zn), (-3000, 0, zn), ramp=QUAY, lvl=_moll)
    # la vorada de coronament: blocs llargs, amb el cantell contra el buit
    e.caixa('vorada', -3000, 3000, 0, 7, ZE - 24, ZE, QUAY, 7.0,
            cares={'dalt': {'ramp': QUAY, 'lvl': lambda s, t, P: 8.0 - (2.4 if (P[0] + 3000) % 120 < 2 else 0)
                            + (fbm(P[0] / 30, 0.5, 51) - 0.5) * 0.6},
                   'davant': {'ramp': QUAY, 'lvl': lambda s, t, P: 5.0 - (2.0 if (P[0] + 3000) % 120 < 2 else 0)}})


def norai(e, sid, x, z, k=1.0, corda=None, y=7.0):
    _ombra(e, x, z, 16 * k, 12 * k, 0.6, y=y + 0.3)
    cilindre(e, sid, x, z, 8 * k, y, y + 18 * k, STEELA, lambda a, yy, P: 3.4 + math.cos(a + 0.6) * 1.2, n=14)
    cilindre(e, sid, x, z, 13 * k, y + 18 * k, y + 24 * k, STEELA, lambda a, yy, P: 3.8 + math.cos(a + 0.6) * 1.2, n=16)
    e.quad(sid, (x - 13 * k, y + 24 * k, z + 13 * k), (x + 13 * k, y + 24 * k, z + 13 * k),
           (x + 13 * k, y + 24 * k, z - 13 * k), (x - 13 * k, y + 24 * k, z - 13 * k), ramp=STEELA, lvl=5.4,
           forma=lambda s, t: (s - 13 * k) ** 2 + (t - 13 * k) ** 2 < (13 * k) ** 2)
    for j in range(2):                                             # dues voltes de corda
        cilindre(e, sid, x, z, 9.5 * k, y + (4 + j * 5) * k, y + (8 + j * 5) * k, ROPEA,
                 lambda a, yy, P: 3.4 + math.cos(a + 0.6) * 1.0, n=14)
    if corda:
        e.cable(sid, [(x + 8 * k, y + 8 * k, z), *corda], ROPEA, 3.4, gruix=2.4 * k)


def caixes(e):
    cx, cz = CAIXES
    _ombra(e, cx, cz, 44, 30, 0.6)
    for k, (dx, dz, ang, n) in enumerate(((0, 0, 0.2, 3), (44, 18, -0.15, 2), (-30, -40, 0.5, 1))):
        for j in range(n):
            def dalt(s, t, P, j=j, n=n):
                if j < n - 1:
                    return 3.0
                return 6.6 + (hr(int(s) // 3, int(t) // 3, 9) - 0.5) * 0.8 if 3 < s < 37 and 3 < t < 23 else 4.2
            e.caixa_girada('caixes', cx + dx, cz + dz, 40, 26, 18, ang, BOX, 3.2, y0=j * 18,
                           cares={'dalt': {'ramp': SALT if j == n - 1 else BOX, 'lvl': dalt},
                                  'davant': {'ramp': BOX, 'lvl': lambda s, t, P: 3.0 + (0.8 if t < 2 else 0)
                                             - (1.4 if int(s) % 8 < 2 and 4 < t < 14 else 0)},
                                  'esquerra': {'ramp': BOX, 'lvl': 2.0}, 'dreta': {'ramp': BOX, 'lvl': 3.6}})


def retol(e, tex):
    x, z = RETOL
    _ombra(e, x, z, 26, 12, 0.5)
    e.caixa('retol', x - 2, x + 2, 0, 52, z - 2, z + 2, STEELA, 3.0)
    tb = (math.cos(-0.25), 0, math.sin(-0.25))
    c = (x, 52, z - 3)
    hw, hh = 38 * 1.3 / 2, 16 * 1.3
    e.quad('retol', _add(_add(c, tb, -hw), (0, hh, 0)), _add(_add(c, tb, hw), (0, hh, 0)), _add(c, tb, hw),
           _add(c, tb, -hw), tex=(tex['retol'], (100, 100, 138, 116)))


def panell_preu(e, tex):
    x, z = PANELL
    _ombra(e, x, z, 40, 18, 0.5)
    tb = (math.cos(PANELL_ANG), 0, math.sin(PANELL_ANG))
    for k in (-22, 22):
        p = _add((x, 0, z), tb, k)
        e.caixa('panell', p[0] - 2.5, p[0] + 2.5, 0, 70, p[2] - 2.5, p[2] + 2.5, STEELA, 2.8)
    hw, hh = 48 * 1.35 / 2, 24 * 1.35
    c = (x, 70, z - 3)
    e.quad('panell', _add(_add(c, tb, -hw), (0, hh, 0)), _add(_add(c, tb, hw), (0, hh, 0)), _add(c, tb, hw),
           _add(c, tb, -hw), tex=(tex['panell'], (99, 99, 147, 123)))
    # el darrere del panell (es veu de biaix per l'altre costat)
    n = (tb[2], 0, -tb[0])
    c2 = _add(c, n, 4)
    e.quad('panell', _add(_add(c2, tb, hw), (0, hh, 0)), _add(_add(c2, tb, -hw), (0, hh, 0)), _add(c2, tb, -hw),
           _add(c2, tb, hw), ramp=STEELA, lvl=2.6)


def _cas(lx, y, lz):
    """Un punt de la caseta de la grua (coordenades locals: x al llarg del davant, z cap enrere) al món."""
    c, s_ = math.cos(CAS_ANG), math.sin(CAS_ANG)
    return (GRUA[0] + lx * c - lz * s_, y, GRUA[1] + lx * s_ + lz * c)


CAS_W, CAS_D, CAS_H = 120.0, 64.0, 70.0
CAS_Y0 = PED_H + 8


def grua(e, tex):
    gx, gz = GRUA
    _ombra(e, gx, gz, 46, 30, 0.6)

    def pedestal(a, y, P):
        seg = y % 30
        lvl = 3.4 + math.cos(a + 0.7) * 1.4 + (fbm(a * 3, y / 14, 70) - 0.5) * 0.6
        if seg < 1.5:
            lvl -= 1.2
        elif seg < 3:
            lvl += 0.6
        elif 5 < seg < 7 and (a * 20) % 1 < 0.35:
            lvl += 1.2                                             # reblons
        if hr(int(a * 12), 80) > 0.72 and 3 < seg < 3 + 20 * hr(int(a * 12), int(y // 30), 81):
            return lvl - 1.4                                       # regalims d'òxid
        return lvl
    e.caixa('grua', gx - 36, gx + 36, 0, 5, gz - 36, gz + 36, STEELA, 3.8, cares={'dalt': {'ramp': STEELA, 'lvl': 5.2}})
    cilindre(e, 'grua', gx, gz, PED_R + 8, 5, PED_H, OCHRE, pedestal, r1=PED_R)
    cilindre(e, 'grua', gx, gz, PED_R + 4, PED_H, PED_H + 8, STEELA, lambda a, y, P: 3.6 + math.cos(a + 0.7) * 1.2)
    # la caseta: el davant (la cabina) amb el dibuix pla; el costat, el darrere i la teulada, planxa ocre
    x0, y0, x1, y1 = PL.CAB
    a, b = CAS_W / 2, CAS_D / 2
    Y0, Y1 = CAS_Y0, CAS_Y0 + CAS_H
    planxa = lambda base: (lambda s, t, P: base - (1.2 if s % 26 < 1.5 else 0) + (fbm(s / 20, t / 14, 71) - 0.5) * 0.6
                           - (0.8 if t > CAS_H - 6 and hr(int(s), 90) > 0.5 else 0))
    # el contrapès de formigó, a la cua (darrere)
    e.caixa_girada('grua', *_cas(-a + 18, 0, b + 18)[::2], 44, 30, 46, CAS_ANG, STONEA, 4.4, y0=Y0 + 12,
                   cares={'dalt': {'ramp': STONEA, 'lvl': 6.4}, 'davant': {'ramp': STONEA, 'lvl': 3.8},
                          'esquerra': {'ramp': STONEA, 'lvl': 3.0}})
    for nom, P0, P1, P2, P3, lv in (
            ('esquerra', _cas(-a, Y1, b), _cas(-a, Y1, -b), _cas(-a, Y0, -b), _cas(-a, Y0, b), 3.2),
            ('dreta', _cas(a, Y1, -b), _cas(a, Y1, b), _cas(a, Y0, b), _cas(a, Y0, -b), 3.6)):
        e.quad('grua', P0, P1, P2, P3, ramp=OCHRE, lvl=planxa(lv))
    e.quad('grua_caseta', _cas(-a, Y1 + 5, -b), _cas(a, Y1 + 5, -b), _cas(a, Y0, -b), _cas(-a, Y0, -b),
           tex=(tex['caseta'], (x0 - 1, y0 - 5, x1 + 1, y1 + 1)))
    e.quad('grua', _cas(-a - 4, Y1 + 5, b + 4), _cas(a + 4, Y1 + 5, b + 4), _cas(a + 4, Y1 + 5, -b - 4),
           _cas(-a - 4, Y1 + 5, -b - 4), ramp=OCHRE, lvl=lambda s, t, P: 5.4 - (1.0 if s % 30 < 1.5 else 0))
    # la ploma de gelosia: del peu (davant la caseta, a baix a l'esquerra) fins a la punta, damunt el buit
    foot = _cas(-a + 10, Y0 + 14, -b - 6)
    n = 14
    dx, dy, dz = TIP[0] - foot[0], TIP[1] - foot[1], TIP[2] - foot[2]
    L = math.sqrt(dx * dx + dy * dy + dz * dz)
    side = _norm2((dz, 0, -dx))                                    # horitzontal i perpendicular a la ploma
    for sgn, lv in ((1, 3.2), (-1, 4.4)):
        e.cable('grua', [_add(foot, side, 9 * sgn), _add(TIP, side, 3 * sgn)], OCHRE, lv, gruix=3.0)
        e.cable('grua', [_add(_add(foot, side, 9 * sgn), (0, 10, 0)), _add(_add(TIP, side, 3 * sgn), (0, 3, 0))],
                OCHRE, lv + 0.6, gruix=2.4)
    for i in range(n):
        t0, t1 = i / n, (i + 1) / n
        w0, w1 = 9 - 6 * t0, 9 - 6 * t1
        A = _add(_add(foot, (dx, dy, dz), t0), side, w0 * (1 if i % 2 else -1))
        B = _add(_add(foot, (dx, dy, dz), t1), side, w1 * (-1 if i % 2 else 1))
        e.cable('grua', [A, B], OCHRE, 3.6, gruix=1.6)
        e.cable('grua', [_add(A, (0, 10 * (1 - t0 * 0.7), 0)), _add(B, (0, 10 * (1 - t1 * 0.7), 0))], OCHRE, 4.0,
                gruix=1.4)
    # l'A de damunt la caseta i els tirants
    apex = _cas(0, Y1 + 60, 0)
    for lx in (-a + 24, a - 24):
        e.cable('grua', [_cas(lx, Y1 + 5, 0), apex], STEELA, 3.6, gruix=2.4)
    e.cable('grua', [apex, TIP], STEELA, 3.0, gruix=1.6)
    e.cable('grua', [apex, _cas(-a + 18, Y0 + 58, b + 18)], STEELA, 3.0, gruix=1.6)
    e.tub('grua', _add(TIP, side, -5), _add(TIP, side, 5), 6, STEELA, 3.6)
    # el cable de la cistella
    e.cable('grua', [(TIP[0], TIP[1] - 4, TIP[2]), (TIP[0], CIST_Y + 2, TIP[2])], STEELA, 3.6, gruix=1.2)


def _norm2(v):
    n = math.sqrt(v[0] ** 2 + v[1] ** 2 + v[2] ** 2) or 1
    return (v[0] / n, v[1] / n, v[2] / n)


def cistella(e, tex):
    x0, y0, x1, y1 = PL.BASKET
    hx, hy = PL.CRANE_TIP[0] + 3, y0 - 18
    e.sprite('cistella', tex['cistella'], (hx, hy), (TIP[0], CIST_Y, TIP[2]), escala_img=1.6)


def cantimplora(e):
    """La Cantimplora canònica, amb la porta oberta i encesa, la rampa estesa fins al moll i l'ombra del sol alt; tota
    la nau, barrejada amb la llum freda d'Aqua."""
    NAU.dibuixa(e, ombra={'sol': SOL, 'k': 0.5}, to=TO)


def primer_pla(e):
    """El norai de baix a la dreta, amb la corda que serpenteja, molt a prop: fosc, tallat pel quadre."""
    x, z = NORAI_PROP
    norai(e, 'primer_pla', x, z, k=1.5, y=0.0,
          corda=[(x - 30, 1.5, z + 6), (x - 60, 1.5, z - 20), (x - 46, 1.5, z - 50)])
    for j, (dx, dz, ang) in enumerate(((84, 6, 0.3), (92, 10, 0.25), (150, -10, -0.2))):
        e.caixa_girada('primer_pla', x + dx, z + dz, 52, 34, 24, ang, BOX, 1.2, y0=(24 if j == 1 else 0),
                       cares={'dalt': {'ramp': BOX, 'lvl': 2.2}, 'davant': {'ramp': BOX, 'lvl': lambda s, t, P:
                              1.0 - (0.8 if int(s) % 10 < 3 and 5 < t < 19 else 0)}})


# ─── Composició ─────────────────────────────────────────────────────────────

def escena(cv, tex):
    e = Escena(cv, CAM, LLUMS, ambient=AMBIENT)
    fons(cv)
    escullera(e, tex)
    cistella(e, tex)
    moll(e)
    for k, (x, z) in enumerate(NORAIS):
        norai(e, 'norai', x, z, corda=[(x + 20, 8, ZE + 2), (x + 26, -30, ZE + 6)] if k == 1 else None)
    cantimplora(e)                                                 # (la nau té el seu z-buffer: abans del que és davant)
    panell_preu(e, tex)
    retol(e, tex)
    caixes(e)
    grua(e, tex)
    primer_pla(e)
    NAU.resplendor(cv, k=0.7)                                      # la claror càlida de la porta i del finestral
    return e


@functools.lru_cache(maxsize=None)
def _base():
    cv = Canvas(light=LIGHT)
    e = escena(cv, _textures())
    cv.rect(0, BOTTOM + 1, W - 1, H - 1, [(0, 0, 0)], 0, lit=0)    # la barra de verbs: negre
    return cv.img, e


def bg(cv):
    img, _ = _base()
    cv.img.paste(img)
    cv.P = cv.img.load()


PILOT = _uv((GRUA[0] + (PED_R + 3) * math.sin(CAS_ANG), PED_H - 30, GRUA[1] - (PED_R + 3) * math.cos(CAS_ANG)))


def grua_arreglada(cv):
    """La grua arreglada: el finestral de la cabina amb el llum verd del quadre, projectat per la cara de la caseta, i
    el pilot verd del pedestal."""
    _, e = _base()
    flat = Canvas(light=PL.LIGHT, transparent=True)
    PL.grua_arreglada(flat)
    cv.img.alpha_composite(e.capa(flat.img, {'grua_caseta'}))
    u, v = PILOT
    cv.flat(u, v, (170, 250, 190))
    for dx, dy in ((-1, 0), (1, 0), (0, -1), (0, 1)):
        cv.P[int(u) + dx, int(v) + dy] = (70, 200, 100, 170)


PROPS = {'grua_arreglada': grua_arreglada}


# ─── Animacions ────────────────────────────────────────────────────────────

def _frames_calitja():
    x1 = round(_uv(_esc(_EL, TOPW))[0]) - 2
    return calitja_frames(_base()[0], 0, x1, HOR - 3, HOR + 6, n=8, amp=1.0)


def _frames_pols():
    return pols_frames(24, 26, (0, 170, W - 1, RH - 6), seed=5, C=Canvas)


def _frames_llum():
    on = canonada_llum(CAN_U, CAN_LY, True, Canvas)
    off = Canvas(transparent=True).img
    return [on, on, off, off, off, off, off, off]


ANIMS = {'calitja': {'frames': _frames_calitja, 'frameDuration': 160},
         'pols': {'frames': _frames_pols, 'frameDuration': 110},
         'llum_canonada': {'frames': _frames_llum, 'frameDuration': 250}}


def _amo(ids, menys=None):
    """La màscara d'una capa del davant: els píxels de les superfícies `ids` (sense la caixa de pantalla `menys`)."""
    def mask(x, y):
        _, e = _base()
        if menys and menys[0] <= x <= menys[2] and menys[1] <= y <= menys[3]:
            return False
        return e.ids[e.amo[y * e.cv.w + x]] in ids
    return mask


def _v(x, z):
    return CAM.projecta((x, 0, z))[1]


_PU, _PV = int(PILOT[0]), int(PILOT[1])

# Capes del davant: el personatge hi passa per darrere si té els peus més amunt (més lluny) que la seva base.
# (A la de la grua no hi va el pilot del pedestal ni la caseta: són el decorat `grua_arreglada`, que va per sota.)
FRONT = [
    {'id': 'davant_grua', 'mask': _amo({'grua'}, (_PU - 2, _PV - 2, _PU + 2, _PV + 2)),
     'baseline': round(_v(*GRUA)), 'zIndex': 20},
    {'id': 'davant_nau', 'mask': _amo({'nau', 'porta', 'cabina_finestres'}),
     'baseline': round(_v(*NAU.terra(0, NR + 10))), 'zIndex': 20},
    {'id': 'davant_rampa', 'mask': _amo({'rampa'}),
     'baseline': round(_v(*NAU.terra(sum(PORTA_L) / 2, RAMPA_OUT * 0.75))), 'zIndex': 20},
    {'id': 'davant_caixes', 'mask': _amo({'caixes'}), 'baseline': round(_v(CAIXES[0], CAIXES[1] - 20)), 'zIndex': 20},
    {'id': 'davant_panell', 'mask': _amo({'panell'}), 'baseline': round(_v(*PANELL)), 'zIndex': 20},
    {'id': 'davant_retol', 'mask': _amo({'retol'}), 'baseline': round(_v(*RETOL)), 'zIndex': 20},
    {'id': 'davant', 'mask': _amo({'primer_pla'}), 'baseline': 999, 'zIndex': 20},
]


# ─── Geometria (coordenades de sala, projectades) ─────────────────────────────

def _p(x, z, y=0.0):
    u, v, _ = CAM.projecta((x, y, z))
    return round(u), round(v)


def _rect(*Ps):
    pts = [CAM.projecta(P) for P in Ps]
    return (max(0, round(min(p[0] for p in pts))), max(0, round(min(p[1] for p in pts))),
            min(W - 1, round(max(p[0] for p in pts))), min(BOTTOM, round(max(p[1] for p in pts))))


def _caixa_rect(sid):
    _, e = _base()
    b = e.caixes[sid]
    return (max(0, round(b[0])), max(0, round(b[1])), min(W - 1, round(b[2])), min(BOTTOM, round(b[3])))


def _cercle(cx, cz, r, n=10):
    return [_p(cx + r * math.cos(2 * math.pi * i / n), cz + r * math.sin(2 * math.pi * i / n)) for i in range(n)]


def _x_u(u, z):
    """La x del món que cau a la columna `u` de la pantalla, a la fondària z del món (a terra)."""
    k = (u - CAM.centre[0]) / CAM.f
    return z * (CAM._sy + k * CAM._cy) / (CAM._cy - k * CAM._sy)


def _retalla(poli, dins, tall):
    """Sutherland–Hodgman: retalla un polígon de pantalla amb un semiplà (`dins(p)`, `tall(a, b)` → el punt de tall)."""
    out = []
    for i, p in enumerate(poli):
        q = poli[i - 1]
        if dins(p):
            if not dins(q):
                out.append(tall(q, p))
            out.append(p)
        elif dins(q):
            out.append(tall(q, p))
    return out


def _tall_v(v0):
    return lambda a, b: (a[0] + (b[0] - a[0]) * (v0 - a[1]) / (b[1] - a[1]), v0)


def _tall_u(u0):
    return lambda a, b: (u0, a[1] + (b[1] - a[1]) * (u0 - a[0]) / (b[0] - a[0]))


# El terra on es camina (al món): el moll, del costat de la nau (sense les potes) i el peu de la rampa fins a la dreta,
# per davant i per darrere de la grua, fins a 34 unitats de la vora; a baix, la vora de la sala; a la dreta, sense el
# primer pla. Es projecta i es retalla amb la pantalla.
_ZB = ZE - 34                                                       # el fons on es camina
_V_BAIX = 251
_SL = sum(PORTA_L) / 2
WALK_MON = [NAU.terra(PORTA_L[1] + 140, 128), NAU.terra(PORTA_L[1] + 6, 128),
            NAU.terra(PORTA_L[1] + 6, RAMPA_OUT + 6), NAU.terra(PORTA_L[0] - 6, RAMPA_OUT + 6),
            NAU.terra(PORTA_L[0] - 6, 128), NAU.terra(-30, 128), NAU.terra(-110, 112), (NAU.terra(-110, 112)[0] + 40, _ZB),
            (_x_u(639, _ZB), _ZB)]
_W = [CAM.projecta((x, 0, z))[:2] for x, z in WALK_MON] + [(639, 222), (575, 236), (540, 262)]
_W = _retalla(_W, lambda p: p[1] <= _V_BAIX, _tall_v(_V_BAIX))
_W = _retalla(_W, lambda p: p[0] >= 0, _tall_u(0))
_WALK = []
for u, v in _W:
    q = (min(639, max(0, round(u))), round(v))
    if not _WALK or _WALK[-1] != q:
        _WALK.append(q)
_V_FONS, _V_PROP = min(v for _, v in _WALK), max(v for _, v in _WALK)
_SPAWN = _p(*NAU.terra(_SL, RAMPA_OUT + 22))
_RAMPA = NAU.rampa_cantons()

GEOMETRIA = {
    'things': {
        'rampa': {'rect': _rect(NAU.buc(PORTA_L[0] - 6, NAU.PORTA_T[1] + 0.06), NAU.buc(PORTA_L[1] + 6, NAU.PORTA_T[1] + 0.06),
                                *_RAMPA),
                  'walk': _SPAWN},
        'escala_port': {'rect': _rect(_esc(STAIR[0][0] - 40, TOPW + 50), _esc(STAIR[-1][0] + 40, STAIR[-1][1] - 30, 60)),
                        'walk': _p(560, ZE - 54)},
        'grua': {'rect': _rect((GRUA[0] - PED_R - 8, 0, GRUA[1] - PED_R), (GRUA[0] + PED_R + 8, 0, GRUA[1] - PED_R),
                               _cas(-CAS_W / 2, CAS_Y0 + CAS_H + 5, -CAS_D / 2), _cas(CAS_W / 2, CAS_Y0 + CAS_H + 5, -CAS_D / 2),
                               _cas(-CAS_W / 2, CAS_Y0, CAS_D / 2)),
                 'walk': _p(GRUA[0] + 30, GRUA[1] - 70)},
        'cistella': {'rect': _rect((TIP[0] - 22, CIST_Y + 4, TIP[2]), (TIP[0] + 22, CIST_Y - 52, TIP[2])),
                     'walk': _p(TIP[0] - 10, ZE - 54)},
        'vaixells': {'rect': _rect(_add(BARCA, ESC_D, -360), _add(_add(BARCA, ESC_D, 340), (0, 280, 0))),
                     'walk': _p(420, ZE - 54)},
        'panell_preu': {'rect': _rect(_add((PANELL[0], 70 + 24 * 1.35, PANELL[1]), (math.cos(PANELL_ANG), 0, math.sin(PANELL_ANG)), -34),
                                      _add((PANELL[0], 70, PANELL[1]), (math.cos(PANELL_ANG), 0, math.sin(PANELL_ANG)), 34)),
                        'walk': _p(PANELL[0] - 40, PANELL[1] - 80)},
        'canonada': {'rect': (CAN_U - 6, 0, CAN_U + 6, HOR - 1), 'walk': _p(GRUA[0] - 90, GRUA[1] + 20)},
    },
    'spawns': {'iri': _p(*NAU.terra(_SL - 40, RAMPA_OUT + 50)), 'vet': _p(*NAU.terra(_SL - 95, RAMPA_OUT + 40))},
    'walkable': _WALK,
    'forats': [_cercle(GRUA[0], GRUA[1], PED_R + 22, 10), _cercle(CAIXES[0], CAIXES[1], 50, 8),
               _cercle(PANELL[0], PANELL[1], 22, 6), _cercle(RETOL[0], RETOL[1], 10, 6)],
    # (la càmera, a 140, mira el moll a ≈500-750 de fons: el terra es veu aixafat)
    'floorSquash': 0.25,
    'characterShadow': {'enabled': True, 'color': '#2a3040', 'alpha': 0.4, 'squash': 0.26, 'core': 0.6,
                        'light': {'x': -0.5, 'y': 0.35, 'direction': True, 'stretch': 0.3}},
    'regions': [{'id': 'perspectiva', 'active': True, 'scaleEnabled': True, 'scaleWalkSpeed': True,
                 'scaleTop': round((_V_FONS - 2 - HOR) / CAM.pos[1], 3),
                 'scaleBottom': round((_V_PROP + 2 - HOR) / CAM.pos[1], 3),
                 'points': [(0, _V_FONS - 2), (W - 1, _V_FONS - 2), (W - 1, _V_PROP + 2), (0, _V_PROP + 2)]}],
}
