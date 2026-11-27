"""
El menjador de l'Arenga. EN 3D (hd640/tres_d.py), a 1×.

Una càmera una mica alta, des de la banda de l'aparador, que mira de biaix la cantonada de proa a l'esquerra:
  - a la paret de l'esquerra, en escorç, la **porta estanca de popa** (COBERTA), la **porta de vaivé de la cuina** i
    el **passaplats** (amb la boca del tub de veu);
  - a la paret del fons, el **rellotge** i el baròmetre, el **pòster** de la Cimera dels Oceans, dos **ulls de bou**,
    les tasses penjades i, a la dreta, la **porta del passadís**, oberta: s'hi veu el passadís il·luminat, de debò
    (amb la fulla estanca oberta cap a la sala, en escorç);
  - la **taula llarga**, separada de la paret, amb la barana de mar i les coses de damunt; darrere, la **banqueta**
    capitonada (qui hi seu, a l'Escena 8, queda darrere la taula); l'**aparador** amb el bullidor;
  - dos tamborets fora de lloc, girats; el sostre baix amb les quadernes que fugen i les canonades;
  - primer pla: la canonada contra incendis i les safates de cables, molt a prop, i un pilar de quaderna a la dreta.

Tot el detall ve del dibuix pla de sempre (menjador_pla_comu.py), projectat. Els decorats (`ulls_dia`: la claror del
mar que entra pels ulls de bou en diagonal) es fan amb l'escena en un altre estat i en surt la diferència.

El món: x a la dreta (0 = la paret de la cuina), y amunt (0 = el terra), z cap al fons (300 = la paret del pòster);
1 unitat = 1 píxel de sala a la distància on un personatge fa ≈110 px (escala 1).
"""
import functools
import math

import hd640  # noqa: F401  (abans de cap hd.rooms: posa la llibreria a 640×360)
from PIL import Image

from hd.pix import Canvas, Light, W, H, hr
from hd.rooms.arenga import CAB, DARK, WHITEP, REDP, YELL, BRASS, glow
from hd.rooms.comu import _diff
from hd.rooms.exterior import fbm
from hd.rooms.principal import CREAM, TEAK, LINO, DOORP, NIGHT, wear, porthole, day_porthole, second_hand, in_door
from hd.rooms.menjador import VINYL, STEEL, MUGS
from hd640.rooms import menjador_pla_comu as PL
from hd640.rooms.laboratori_pla_comu import lamp, door_frame
from hd640.tres_d import Camera, Escena, Llum

BOTTOM = 259                                       # la sala acaba aquí (a sota, la barra de verbs)
ZW = 300                                           # la paret del fons
HW = PL.FLOOR_Y - PL.CEIL_H                        # l'alçada de les parets (179: el sostre baix d'un vaixell)
XL = 212                                           # al dibuix pla, la cantonada: a l'esquerra, la paret de la cuina
XR = 480                                           # la paret de la dreta
SOCOL = PL.FLOOR_Y - 171                           # l'alçada del sòcol de teca
TAULA = (70, 270, 196, 240, 50)                    # la taula: x0, x1, z del davant, z del darrere, alçada
BANC = (58, 282, 262, 300)                         # la banqueta: x0, x1, z0, z1
APA = (506 - XL, 571 - XL, 272, 46)         # l'aparador: x0, x1, z del davant, alçada
TAMB = ((318, 160, 0.5), (130, -6, -0.35))         # els tamborets: x, z, gir
LAMPS = ((112, 214), (240, 214), (110, 110), (340, 110))  # els llums del sostre (x, z)
SEIENTS = (92, 128, 164, 200, 236, 262)            # on seuen, a l'Escena 8 (x; z = SEU_Z)
SEU_Z = 254


def _w(fx):
    """Una x del dibuix pla de la paret del fons → la x del món."""
    return fx - XL


def _wz(fx):
    """Una x del dibuix pla de la paret de la cuina → la z del món."""
    return ZW - XL + fx


def _y(fy):
    """Una y del dibuix pla (el terra, a FLOOR_Y) → l'alçada del món."""
    return PL.FLOOR_Y - fy


D_PASS = (_w(PL.D_PASS[0]), _w(PL.D_PASS[2]), _y(PL.D_PASS[1]))          # la porta del passadís: x0, x1, alt
D_POPA = (_wz(PL.D_POPA[0]), _wz(PL.D_POPA[2]), _y(PL.D_POPA[1]))
D_CUINA = (_wz(PL.D_CUINA[0]), _wz(PL.D_CUINA[2]), _y(PL.D_CUINA[1]))
HATCH = (_wz(144), _wz(208), _y(160), _y(101))                         # el passaplats: z0, z1, y0, y1
POSTER = (_w(PL.POSTER[0]), _w(PL.POSTER[2]), _y(PL.POSTER[3]), _y(PL.POSTER[1]))

CAM = Camera(pos=(390, 160, -250), yaw=-0.36, pitch=0.16, f=470, centre=(320, 100))

LIGHT = Light(ambient=0.0, vignette=None, floor_fade=None)  # (la llum és la del món: la de l'Escena)
LLUMS = [Llum((x, HW - 14, z), 240, 1.6, power=1.4) for x, z in LAMPS] + [
    Llum((6, 100, (HATCH[0] + HATCH[1]) / 2), 110, 1.0, power=1.6),        # la cuina, pel passaplats
    Llum(((D_PASS[0] + D_PASS[1]) / 2, 120, ZW + 10), 120, 1.0, power=1.6),  # el passadís
]
TEX_LIGHT = Light(ambient=-0.15, vignette=None, floor_fade=None)

FOSC = [(4, 3, 3), (9, 7, 6), (15, 12, 10), (22, 18, 15), (31, 26, 21), (42, 35, 28)]


# ─── Les textures: el dibuix pla de sempre ───────────────────────────────────

def _passadis_pla(cv):
    """La porta del passadís sense l'obertura (que serà un forat: el passadís és en 3D) ni la fulla."""
    x0, y0, x1, y1 = PL.D_PASS
    door_frame(cv, x0, y0, x1, y1)
    PL.sill(cv, x0, x1, y1, h=7)
    PL.sign_box(cv, x0 + 4, 64, 'PASSADÍS', WHITEP, 4.2, (24, 28, 30))


def _paret(dia=False, tasses=True, dx=None, segons=None, mar=None):
    """Les dues parets planes, de cara (sense la banqueta, la taula ni l'aparador, que són en 3D)."""
    cv = Canvas(light=TEX_LIGHT)
    PL.wall(cv)
    wear(cv, 0, 40, W - 1, 168, 32, seed=2, k=0.22)
    PL.door_popa(cv)
    PL.door_cuina(cv)
    PL.passaplats(cv)
    _passadis_pla(cv)
    for i, (px, py) in enumerate(PL.PORTS):
        porthole(cv, px, py, PL.PORT_R, rim=4, seed=i + 1,
                 fn=None if mar is None else _ull_mar(px, py, PL.PORT_R, i + 1, mar))
    PL.poster(cv)
    PL.clocks(cv)
    if segons is not None:
        second_hand(cv, PL.CLOCK[0], PL.CLOCK[1], segons, r=6)
    # el prestatge, el penjador i les tasses de damunt l'aparador (la resta de l'aparador és en 3D)
    PL._MUGS['on'] = False
    try:
        sb = Canvas(light=TEX_LIGHT, transparent=True)
        PL.sideboard(sb)
    finally:
        PL._MUGS['on'] = True
    cv.img.alpha_composite(sb.img.crop((0, 0, W, 121)), (0, 0))
    cv.P = cv.img.load()
    if tasses:
        PL.hanging_mugs(cv, dx)
    if dia:
        for i, (px, py) in enumerate(PL.PORTS):
            day_porthole(cv, px, py, PL.PORT_R, seed=i + 1)
        day_porthole(cv, 39, 115, 9)
    # l'obertura del passadís, transparent: s'hi veu el passadís de debò
    x0, y0, x1, y1 = PL.D_PASS
    P = cv.P
    for y in range(y0, y1 - 7):
        for x in range(x0, x1 + 1):
            if in_door(x, y, x0, y0, x1, y1, 11):
                P[x, y] = (0, 0, 0, 0)
    return cv.img


@functools.lru_cache(maxsize=None)
def _paret_base():
    return _paret()


def _mobles():
    """El davant de la taula, la banqueta i l'aparador, i el bullidor, dibuixats plans sobre transparent."""
    cv = Canvas(light=TEX_LIGHT, transparent=True)
    PL.bench(cv)
    PL.sideboard(cv)
    PL.table(cv)
    th = Canvas(light=TEX_LIGHT, transparent=True)
    PL.table_things(th)
    return cv.img, th.img


@functools.lru_cache(maxsize=None)
def _mobles_base():
    return _mobles()


TAULA_TEX = (197, PL.T_FRONT, 197 + 228, PL.T_FOOT + 1)          # tres plafons del faldó de la taula
BANC_TEX = (PL.T_X0 + 6, 134, PL.T_X1 - 6, PL.FLOOR_Y)           # el respatller de la banqueta
APA_TEX = (506, 149, 572, PL.FLOOR_Y)                             # el davant de l'aparador (amb la barana)
BULL_TEX = (512, 119, 570, 150)                                   # el bullidor i les tasses, damunt l'aparador
TETERA_TEX = (330, 149, 359, 167)


def _lampada():
    cv = Canvas(light=TEX_LIGHT, transparent=True)
    lamp(cv, 30, 10)
    return cv.img.crop((18, 5, 43, 20)), (12, 1)


# ─── Les superfícies ────────────────────────────────────────────────────────

def _planxa(lvl0, pw=96, ph=60, seed=11):
    """Planxa pintada de crema (on el dibuix pla no arriba): quadernes amb reblons, en coordenades del món."""
    def L(s, t, P):
        val = lvl0 + (hr(int(s // 3), int(t // 5), seed) - 0.5) * 0.25 + (fbm(s / 40, t / 30, seed) - 0.5) * 0.5
        d = s % pw
        if d < 5:
            val += 0.9 if d < 1 else 0.5 if d < 2 else -0.6 if d >= 4 else 0.1
            if d < 4 and 2 <= d < 3 and int(t) % 14 == 0:
                val += 1.0
        if abs(t - 118) < 1:
            val -= 1.1
        return val
    return L


def _socol(s, t, P):
    """El sòcol de teca (de llistons, com al dibuix pla), en coordenades del món."""
    v = 3.0 + (hr(int(s // 6), int(t // 8), 2) - 0.5) * 0.6
    if int(t) % 8 == 0 or int(s + 9 * (t // 8)) % 31 == 0:
        v -= 0.8
    if t < 2:
        v += 1.4
    return v


def _paret_proc(e, sid, P0, P1, P2, P3, seed):
    """Una paret procedural (planxa crema a dalt, sòcol de teca a baix), de P0 (dalt esq.) a P2 (baix dreta)."""
    k = (HW - SOCOL) / HW

    def at(A, B):
        return tuple(A[i] + (B[i] - A[i]) * k for i in range(3))
    M3, M2 = at(P0, P3), at(P1, P2)
    e.quad(sid, P0, P1, M2, M3, ramp=CREAM, lvl=_planxa(4.4, seed=seed))
    e.quad(sid, M3, M2, P2, P3, ramp=TEAK, lvl=_socol)


def _terra(s, t, P):
    """Linòleum de rajoles a escacs suaus, en coordenades del món: les juntes fugen i s'empetiteixen."""
    x, z = P[0], P[2]
    tile = 34
    gx, gz = math.floor(x / tile), math.floor(z / tile)
    v = 3.0 + (hr(int(x // 4), int(z // 4), 2) - 0.5) * 0.45 + (fbm(x / 80, z / 50, 5) - 0.5) * 0.6
    if (gx + gz) % 2:
        v += 0.5
    if x % tile < 1.0 or z % tile < 1.0:
        v -= 0.9
    # gastat pel mig, on es trepitja
    v -= 0.4 * max(0.0, 1 - abs(z - 140) / 80) * max(0.0, 1 - abs(x - 230) / 200)
    return v


def _brillo(s, t):
    """El reflex dels llums al linòleum encerat: un bassal sota cadascun."""
    k = 0.0
    for lx, lz in LAMPS:
        d = math.hypot(s - lx, (ZW - t) - lz)
        k = max(k, 0.26 * max(0.0, 1 - d / 70) ** 1.5)
    return k


def _mar(e, y, dins=None):
    """La claror del mar que entra pels dos ulls de bou (de dia) i cau en diagonal cap a la dreta i endavant."""
    for fx, fy in PL.PORTS:
        ux = _w(fx)

        def fn(s, t, ux=ux):
            x, z = ux - 40 + s + t * 0.294, ZW - 10 - t * 0.956
            if dins and not dins(x, z):
                return 0.0
            return 0.4 * max(0.0, 1 - abs(s - 40) / 24) * min(1.0, t / 30) * max(0.0, 1 - t / 260)
        e.claror((ux - 40, y, ZW - 10), (ux + 40, y, ZW - 10), (ux + 120, y, ZW - 270), (ux + 40, y, ZW - 270),
                 (200, 230, 255), fn)


def escena(cv, tex, estat=frozenset()):
    """Tota la sala, de lluny a prop. `estat`: 'dia' (els ulls de bou, de dia). → l'Escena (qui ha pintat què)."""
    e = Escena(cv, CAM, LLUMS, ambient=-0.5)
    zn = CAM.pos[2] + 60
    paret = tex['paret']
    mob, coses = tex['mobles']
    # el passadís, a través de la porta oberta: el linòleum, la paret crema amb el passamans i un llum
    px0, px1, ph = D_PASS
    zp = ZW + 110
    e.quad('passadis', (px0 - 30, 0, zp), (px1 + 40, 0, zp), (px1 + 40, 0, ZW), (px0 - 30, 0, ZW), ramp=LINO,
           lvl=lambda s, t, P: 3.4 - (0.9 if P[2] % 30 < 1 else 0))
    e.quad('passadis', (px0 - 30, HW, zp), (px1 + 40, HW, zp), (px1 + 40, 0, zp), (px0 - 30, 0, zp), ramp=CREAM,
           lvl=lambda s, t, P: 4.4 - abs(s - 60) / 40 - (1.2 if abs(t - 60) < 2 else 0)
           + (1.6 if abs(t - 22) < 1 and 30 < s < 100 else 0))
    e.quad('passadis', (px0 - 4, HW, ZW), (px0 - 4, HW, zp), (px0 - 4, 0, zp), (px0 - 4, 0, ZW), ramp=CREAM,
           lvl=lambda s, t, P: 3.8 - (1.4 if abs(t - 35) < 2 else 0) - (1.0 if t > HW - 30 else 0))
    e.quad('passadis', (px1 + 4, HW, zp), (px1 + 4, HW, ZW), (px1 + 4, 0, ZW), (px1 + 4, 0, zp), ramp=CREAM,
           lvl=lambda s, t, P: 3.0 - (1.4 if abs(t - 35) < 2 else 0) - (1.0 if t > HW - 30 else 0))
    e.quad('passadis', (px0 - 30, HW, ZW), (px1 + 40, HW, ZW), (px1 + 40, HW, zp), (px0 - 30, HW, zp), ramp=CREAM,
           lvl=2.0, dues_cares=True)
    # el sostre, baix i fosc
    e.quad('sostre', (0, HW, zn), (XR, HW, zn), (XR, HW, ZW), (0, HW, ZW), ramp=CREAM,
           lvl=lambda s, t, P: 2.2 + (fbm(s / 50, t / 40, 3) - 0.5) * 0.6, dues_cares=True)
    # la paret de la cuina (x = 0): de prop, planxa; cap a la cantonada, el dibuix pla (x 0..212)
    _paret_proc(e, 'paret_esq_prop', (0, HW, zn), (0, HW, ZW - XL), (0, 0, ZW - XL), (0, 0, zn), 12)
    e.quad('paret_esq', (0, HW, ZW - XL), (0, HW, ZW), (0, 0, ZW), (0, 0, ZW - XL),
           tex=(paret, (0, PL.CEIL_H, XL, PL.FLOOR_Y)))
    # la paret del fons (z = 300): el dibuix pla (x 212..640) i, a la dreta, més planxa
    e.quad('paret_fons', (0, HW, ZW), (W - XL, HW, ZW), (W - XL, 0, ZW), (0, 0, ZW),
           tex=(paret, (XL, PL.CEIL_H, W, PL.FLOOR_Y)))
    _paret_proc(e, 'paret_fons_dreta', (W - XL, HW, ZW), (XR, HW, ZW), (XR, 0, ZW), (W - XL, 0, ZW), 13)
    # la paret de la dreta (x = XR), en escorç: planxa, amb el salvavides
    _paret_proc(e, 'paret_dreta', (XR, HW, ZW), (XR, HW, zn), (XR, 0, zn), (XR, 0, ZW), 14)
    # el terra
    e.quad('terra', (0, 0, ZW), (XR, 0, ZW), (XR, 0, zn), (0, 0, zn), ramp=LINO, lvl=_terra)
    e.claror((0, 0.3, ZW), (XR, 0.3, ZW), (XR, 0.3, zn), (0, 0.3, zn), (255, 214, 150), _brillo)
    # la claror càlida de la cuina, pel passaplats, i la del passadís, pel terra
    hz = (HATCH[0] + HATCH[1]) / 2
    e.claror((0, 0.4, hz + 50), (110, 0.4, hz + 60), (110, 0.4, hz - 60), (0, 0.4, hz - 50), (255, 190, 110),
             lambda s, t: 0.22 * max(0.0, 1 - s / 110) * max(0.0, math.sin(math.pi * t / 110)))
    pc = (px0 + px1) / 2
    e.claror((pc - 50, 0.4, ZW), (pc + 50, 0.4, ZW), (pc + 80, 0.4, ZW - 130), (pc - 80, 0.4, ZW - 130),
             (255, 210, 150), lambda s, t: 0.26 * max(0.0, 1 - abs(s - 50 - t * 0.23) / (30 + t * 0.25)) * max(0.0, 1 - t / 130))
    if 'dia' in estat:
        _mar(e, 0.5)
    # la foscor dels racons
    e.foscor('racons', (0, 0.5, ZW), (XR, 0.5, ZW), (XR, 0.5, zn), (0, 0.5, zn),
             lambda s, t: max(0.6 * max(0.0, 1 - t / 24), 0.5 * max(0.0, 1 - s / 22), 0.5 * max(0.0, 1 - (XR - s) / 22)))
    e.foscor('cantonada', (0, HW, ZW - 0.5), (50, HW, ZW - 0.5), (50, 0, ZW - 0.5), (0, 0, ZW - 0.5),
             lambda s, t: 0.5 * max(0.0, 1 - s / 50))
    e.foscor('cantonada2', (0.5, HW, ZW - 50), (0.5, HW, ZW), (0.5, 0, ZW), (0.5, 0, ZW - 50),
             lambda s, t: 0.5 * max(0.0, 1 - (50 - s) / 50))
    e.foscor('sostre_fosc', (0, HW - 0.5, ZW - 0.6), (XR, HW - 0.5, ZW - 0.6), (XR, 0, ZW - 0.6), (0, 0, ZW - 0.6),
             lambda s, t: 0.4 * max(0.0, 1 - t / 40))
    # les quadernes del sostre, que fugen, i les canonades de damunt la banqueta
    for bx in (63, 159, 255, 351, 447):
        e.caixa('sostre', bx - 2, bx + 6, HW - 8, HW, 120, ZW, CREAM, 3.0,
                cares={'sota': {'ramp': CREAM, 'lvl': 2.4}, 'esquerra': {'ramp': CREAM, 'lvl': 3.4},
                       'dreta': {'ramp': CREAM, 'lvl': 1.6}})
    e.tub('canonades', (0, HW - 4, ZW - 5), (XR, HW - 4, ZW - 5), 3, REDP, 3.4, brides=96)
    e.tub('canonades', (0, HW - 4, ZW - 14), (XR, HW - 4, ZW - 14), 2, WHITEP, 3.4)
    # la banqueta: el seient i el respatller (el dibuix pla)
    bx0, bx1, bz0, bz1 = BANC
    e.caixa('banc', bx0, bx1, 0, 66, bz1 - 9, bz1 - 0.5, VINYL, 2.6,
            cares={'davant': {'tex': (mob, BANC_TEX)}, 'dalt': {'ramp': TEAK, 'lvl': 4.2},
                   'dreta': {'ramp': VINYL, 'lvl': 2.0}, 'esquerra': {'ramp': VINYL, 'lvl': 2.4}})
    e.caixa('banc', bx0, bx1, 0, 26, bz0, bz1 - 9, VINYL, 2.4,
            cares={'dalt': {'ramp': VINYL, 'lvl': lambda s, t, P: 3.6 - (1.4 if s % 56 < 1.5 else 0)},
                   'davant': {'ramp': VINYL, 'lvl': lambda s, t, P: 2.2 - (1.0 if t > 20 else 0)},
                   'dreta': {'ramp': VINYL, 'lvl': 1.8}})
    # l'aparador: el davant (el dibuix pla), la tapa, el costat; i el bullidor i les tasses, drets al damunt
    ax0, ax1, az, ah = APA
    e.foscor('ombra_apa', (ax0 - 6, 0.6, ZW), (ax1 + 6, 0.6, ZW), (ax1 + 6, 0.6, az - 14), (ax0 - 6, 0.6, az - 14),
             lambda s, t: 0.5 * min(1.0, max(0.0, (ZW - az + 14 - t) / 14)))
    e.caixa('aparador', ax0, ax1, 0, ah + 4, az, ZW - 0.5, TEAK, 3.0,
            cares={'davant': {'tex': (mob, APA_TEX)}, 'dalt': {'ramp': TEAK, 'lvl': 4.6},
                   'esquerra': {'ramp': TEAK, 'lvl': 2.4}, 'dreta': {'ramp': TEAK, 'lvl': 2.0}})
    e.sprite('bullidor', mob.crop(BULL_TEX), ((BULL_TEX[2] - BULL_TEX[0]) / 2 + 2, BULL_TEX[3] - BULL_TEX[1] - 1),
             ((ax0 + ax1) / 2, ah, az + 14))
    # la taula: el faldó (el dibuix pla), la tapa amb la barana de mar, i les coses de damunt
    x0, x1, zf, zb, th = TAULA
    e.foscor('ombra_taula', (x0 - 10, 0.6, zb + 10), (x1 + 14, 0.6, zb + 10), (x1 + 14, 0.6, zf - 22),
             (x0 - 10, 0.6, zf - 22), lambda s, t: 0.55 * min(1.0, max(0.0, (zb - zf + 32 - t) / 18))
             * min(1.0, s / 10, (x1 - x0 + 24 - s) / 10))
    e.caixa('taula', x0, x1, 0, th, zf, zb, TEAK, 2.6,
            cares={'davant': {'tex': (mob, TAULA_TEX)},
                   'dalt': {'ramp': TEAK, 'lvl': lambda s, t, P: 4.0 + (fbm(s / 30, t / 6, 7) - 0.5) * 0.7
                            + (0.5 if hr(int(s // 7), int(t // 2), 7) > 0.9 else 0) - (0.8 if s < 2 or t < 2 else 0)},
                   'dreta': {'ramp': TEAK, 'lvl': lambda s, t, P: 2.2 - (1.0 if s % 22 < 1.5 or t > th - 6 else 0)},
                   'esquerra': {'ramp': TEAK, 'lvl': 2.8}})
    for zz in (zb - 1.5,):                                      # la barana de mar (al darrere i als costats)
        e.caixa('taula', x0 + 2, x1 - 2, th, th + 3, zz - 1.5, zz + 0.5, TEAK, 3.6, cares={'dalt': {'ramp': TEAK, 'lvl': 5.0}})
    for xx in (x0 + 1, x1 - 1):
        e.caixa('taula', xx - 1, xx + 1, th, th + 3, zf + 2, zb - 2, TEAK, 3.6, cares={'dalt': {'ramp': TEAK, 'lvl': 5.0}})
    if 'dia' in estat:
        _mar(e, th + 0.4, lambda x, z: x0 <= x <= x1 and zf <= z <= zb)
    # damunt la taula: les tasses de te, la tetera, la carta nàutica, la baralla i el cendrer
    for i, (mx, mz) in enumerate(((84, 210), (122, 226), (176, 214), (214, 222), (246, 208), (258, 228))):
        m = MUGS[i % 4]
        e.caixa('coses', mx - 3, mx + 3, th, th + 8, mz - 3, mz + 3, m, 2.8,
                cares={'dalt': {'ramp': [(20, 10, 6), (40, 22, 12), (70, 40, 20)], 'lvl': 1.4},
                       'dreta': {'ramp': m, 'lvl': 1.8}})
    e.quad('coses', (98, th + 0.3, 214), (122, th + 0.3, 210), (124, th + 0.3, 200), (100, th + 0.3, 203),
           ramp=[(60, 70, 60), (140, 150, 130), (200, 206, 186), (230, 232, 214)],
           lvl=lambda s, t, P: 2.8 - (1.2 if abs(s - 12) < 0.7 else 0) + (0.6 if abs(t - 5) < 0.6 else 0))
    for k in range(4):
        e.quad('coses', *[(196 + k * 4 + dx, th + 0.3 + k * 0.2, 205 + dz) for dx, dz in ((0, 5), (5, 5), (5, 0), (0, 0))],
               ramp=WHITEP, lvl=4.4)
    e.caixa('coses', 250, 256, th, th + 2, 233, 237, STEEL, 3.4)
    e.sprite('coses', coses.crop(TETERA_TEX), ((TETERA_TEX[2] - TETERA_TEX[0]) / 2, TETERA_TEX[3] - TETERA_TEX[1] - 1),
             (160, th, 224))
    # els llums del sostre
    img, peu = _lampada()
    for lx, lz in LAMPS:
        e.sprite('llums', img, peu, (lx, HW, lz), escala_img=1.3)
    # els tamborets, fora de lloc i girats
    for k, (sx, sz, a) in enumerate(TAMB):
        e.foscor('ombra_tamb', (sx - 18, 0.7, sz + 16), (sx + 22, 0.7, sz + 16), (sx + 22, 0.7, sz - 18),
                 (sx - 18, 0.7, sz - 18), lambda s, t: 0.6 * max(0.0, 1 - ((s - 20) / 18) ** 2 - ((t - 17) / 15) ** 2) * 1.5)
        c, s_ = math.cos(a), math.sin(a)
        for lx, lz in ((-8, -8), (8, -8), (8, 8), (-8, 8)):
            e.caixa_girada('tamboret', sx + lx * c - lz * s_, sz + lx * s_ + lz * c, 2.4, 2.4, 28, a, STEEL, 3.0)
        e.caixa_girada('tamboret', sx, sz, 16, 16, 2, a, STEEL, 3.4, y0=10)
        e.caixa_girada('tamboret', sx, sz, 24, 24, 6, a, VINYL, 2.8, y0=28,
                       cares={'dalt': {'ramp': VINYL, 'lvl': lambda s, t, P: 4.0 - math.hypot(s - 12, t - 12) * 0.08},
                              'davant': {'ramp': VINYL, 'lvl': 2.2}, 'dreta': {'ramp': VINYL, 'lvl': 1.8},
                              'esquerra': {'ramp': VINYL, 'lvl': 2.6}})
    # la fulla estanca del passadís, oberta cap a la sala (en escorç)
    e.quad('fulla', (px1 + 3, ph - 6, ZW - 2), (px1 + 3, ph - 6, ZW - 50), (px1 + 3, 7, ZW - 50), (px1 + 3, 7, ZW - 2),
           ramp=DOORP, dues_cares=True,
           lvl=lambda s, t, P: 3.0 - (1.0 if s < 3 or s > 45 or t < 3 or t > ph - 16 else 0)
           + (0.8 if (abs(s - 8) < 2 or abs(s - 40) < 2) and (abs(t - 22) < 5 or abs(t - ph + 40) < 5) else 0))
    e.caixa('fulla', px1 + 3, px1 + 6, 7, ph - 6, ZW - 50, ZW - 47, DOORP, 2.0)
    # el salvavides, penjat a la paret de la dreta
    e.quad('salvavides', (XR - 0.5, 128, 150), (XR - 0.5, 128, 110), (XR - 0.5, 88, 110), (XR - 0.5, 88, 150),
           ramp=REDP, forma=lambda s, t: 9 < math.hypot(s - 20, t - 20) < 20,
           lvl=lambda s, t, P: (5.2 if int((math.atan2(t - 20, s - 20) + 3.1416) / 0.785) % 2 else 3.4)
           - abs(math.hypot(s - 20, t - 20) - 14.5) * 0.15)
    # primer pla: la canonada contra incendis i la safata de cables, molt a prop, i un pilar de quaderna a la dreta
    e.tub('primer_pla', (-60, HW - 6, -70), (XR + 60, HW - 6, -70), 9, FOSC, 2.4, brides=110)
    e.caixa_girada('primer_pla', 70, -70, 70, 50, 44, 0.3, FOSC, 1.6,
                   cares={'dalt': {'ramp': FOSC, 'lvl': lambda s, t, P: 3.0 - (1.2 if abs(s - 32) < 2 else 0)},
                          'davant': {'ramp': FOSC, 'lvl': lambda s, t, P: 1.4 + (1.0 if 10 < s < 30 and 12 < t < 22 else 0)},
                          'dreta': {'ramp': FOSC, 'lvl': 2.2}})
    e.caixa('primer_pla', 444, 462, 0, HW, 30, 46, FOSC, 2.0,
            cares={'esquerra': {'ramp': FOSC, 'lvl': lambda s, t, P: 2.8 - (1.4 if s < 2 else 0)
                                + (1.6 if int(t) % 14 < 2 and 6 < s < 14 else 0)},
                   'davant': {'ramp': FOSC, 'lvl': 1.2}})
    return e


# ─── Composició ─────────────────────────────────────────────────────────────

@functools.lru_cache(maxsize=None)
def _textures():
    return {'paret': _paret_base(), 'mobles': _mobles_base()}


def _proj(P):
    u, v, _ = CAM.projecta(P)
    return u, v


def _brills(cv):
    """El resplendor dels llums (a la pantalla, damunt l'escena)."""
    for lx, lz in LAMPS:
        u, v = _proj((lx, HW - 10, lz))
        k = CAM.escala((lx, HW, lz))
        glow(cv, round(u), round(v), round(40 * k), (255, 214, 140), 0.32)
        glow(cv, round(u), round(v), round(12 * k), (255, 240, 200), 0.5)


def _render(estat=frozenset(), tex=None):
    cv = Canvas(light=LIGHT)
    e = escena(cv, tex or _textures(), estat)
    _brills(cv)
    cv.rect(0, BOTTOM + 1, W - 1, H - 1, [(0, 0, 0)], 0, lit=0)    # la barra de verbs: negre
    return cv.img, e


@functools.lru_cache(maxsize=None)
def _base():
    return _render()


def bg(cv):
    cv.img.paste(_base()[0])
    cv.P = cv.img.load()


def ulls_dia(cv):
    """Escenes 2 i 3, de dia: els ulls de bou clars i la claror del mar que entra en diagonal."""
    tex = {'paret': _paret(dia=True), 'mobles': _mobles_base()}
    img, _ = _render(frozenset({'dia'}), tex)
    cv.img.alpha_composite(_diff(img, _base()[0]))
    cv.P = cv.img.load()


TELEFON = (229, 122)                               # a la pantalla: el peu del telèfon, damunt la taula (≈ (108, 50, 203))


def telefon(cv):
    """Acte 3, la reunió: el telèfon de satèl·lit de la Nadia, dret contra la tetera davant la Capitana, en
    videotrucada: la pantalla encesa i, a dins, la Hedda Lind que somriu (cabell ros curt, jaqueta fosca).
    Només es mostra amb indicacions d'escena (`{"prop": "telefon"}` al diàleg `reunio`)."""
    from PIL import ImageDraw
    d = ImageDraw.Draw(cv.img)
    cx, y1 = TELEFON
    x0, x1, y0 = cx - 11, cx + 11, y1 - 19
    d.ellipse((x0 - 1, y1 - 1, x1 + 2, y1 + 2), fill=(20, 12, 8, 110))           # l'ombra a la taula
    d.rectangle((x1 - 3, y0 - 6, x1 - 2, y0), fill=(30, 30, 32, 255))             # l'antena, curta i gruixuda
    d.rectangle((x0, y0, x1, y1), fill=(34, 36, 38, 255))                         # la carcassa de goma
    d.rectangle((x0, y1 - 1, x1, y1), fill=(22, 22, 24, 255))
    sx0, sy0, sx1, sy1 = x0 + 2, y0 + 2, x1 - 2, y1 - 3                           # la pantalla
    for y in range(sy0, sy1 + 1):                                                 # el fons: una oficina clara
        k = (y - sy0) / max(1, sy1 - sy0)
        d.line((sx0, y, sx1, y), fill=(round(150 - 40 * k), round(178 - 40 * k), round(196 - 30 * k), 255))
    fx, fy = cx, sy0 + 6
    d.polygon([(fx - 8, sy1), (fx + 8, sy1), (fx + 5, fy + 5), (fx - 5, fy + 5)], fill=(28, 30, 44, 255))  # jaqueta
    d.polygon([(fx - 2, fy + 5), (fx + 2, fy + 5), (fx, fy + 9)], fill=(230, 230, 236, 255))              # camisa
    d.rectangle((fx - 5, fy - 5, fx + 5, fy + 3), fill=(222, 196, 120, 255))      # el cabell ros, en melena curta
    d.ellipse((fx - 3, fy - 3, fx + 3, fy + 5), fill=(238, 198, 172, 255))        # la cara
    d.rectangle((fx - 4, fy - 5, fx + 4, fy - 3), fill=(222, 196, 120, 255))      # el serrell
    d.point([(fx - 2, fy), (fx + 2, fy)], fill=(40, 30, 30, 255))                 # els ulls
    d.line((fx - 1, fy + 3, fx + 1, fy + 3), fill=(186, 96, 92, 255))             # el somriure
    d.point([(fx - 2, fy + 2), (fx + 2, fy + 2)], fill=(186, 96, 92, 255))
    d.point([(sx0, sy0), (sx0 + 1, sy0)], fill=(235, 245, 255, 255))              # la lluentor del vidre
    cv.P = cv.img.load()


PROPS = {'ulls_dia': ulls_dia, 'telefon': telefon}


# ─── Animacions ─────────────────────────────────────────────────────────────

def _fotograma(capes):
    img = _base()[0].copy()
    for c in capes:
        img.alpha_composite(c)
    return _diff(img, _base()[0])


def _frames_rellotge():
    """L'agulla dels segons del rellotge (un fotograma per segon), projectada per la paret."""
    _, e = _base()
    return [_fotograma([e.capa(_paret(segons=s), {'paret_fons'})]) for s in range(60)]


def _ull_mar(cx, cy, r, seed, t):
    """El que es veu per l'ull de bou en el moment `t` (0..1) del balanceig: l'horitzó que puja i baixa amb el
    vaixell, i les crestes de les onades que corren (el mateix mar de nit de principal.night_sea)."""
    a = 2 * math.pi * t

    def fn(cv, x, y):
        hz = cy + r * 0.15 + 1.6 * math.sin(a + seed * 0.4)
        if y < hz:
            cl = hr(int((x + seed * 7) // 4), int(y // 2), seed)
            v = 2.6 + (hz - y) / (r * 2) + (0.8 if cl > 0.72 else 0)
            if hz - y < 1.5:
                v = 4.4                                            # (la línia clara de l'horitzó)
        else:
            v = 1.8 - (y - hz) / (r * 1.6)
            if math.sin(x * 0.7 + y * 2.3 + seed - a * 2) > 0.8:
                v += 2.6
        cv.put(x, y, NIGHT, v, lit=0.1)
    return fn


def _frames_mar():
    """El mar pels ulls de bou (de nit): l'horitzó es gronxa amb el balanceig i les onades corren."""
    img0, e = _base()
    quiet = img0.copy()
    quiet.alpha_composite(e.capa(_paret(), {'paret_fons'}))
    out = []
    for i in range(12):                                            # (només els vidres: la resta, com el fons)
        img = img0.copy()
        img.alpha_composite(e.capa(_paret(mar=i / 12), {'paret_fons'}))
        out.append(_diff(img, quiet))
    return out


def _frames_tasses():
    """Les tasses penjades es gronxen amb el balanceig, cadascuna una mica endarrerida respecte de l'anterior."""
    _, e = _base()
    nues = e.capa(_paret(tasses=False), {'paret_fons'})
    out = []
    for i in range(24):
        t = 2 * math.pi * i / 24
        dx = [round(1.7 * math.sin(t - k * 0.35)) for k in range(5)]
        out.append(_fotograma([nues, e.capa(_paret(dx=dx), {'paret_fons'})]))
    return out


ANIMS = {'rellotge': {'frames': _frames_rellotge, 'frameDuration': 1000},
         'tasses': {'frames': _frames_tasses, 'frameDuration': 160},
         'mar': {'frames': _frames_mar, 'frameDuration': 240}}


def _amo(ids):
    def mask(x, y):
        _, e = _base()
        return e.ids[e.amo[y * e.cv.w + x]] in ids
    return mask


def _p(x, z, y=0.0):
    u, v, _ = CAM.projecta((x, y, z))
    return round(u), round(v)


# Capes del davant: la taula (qui seu a la banqueta hi queda darrere, de cintura en avall), els tamborets i el
# primer pla (sempre davant).
FRONT = [
    {'id': 'davant', 'mask': _amo({'taula', 'coses'}), 'baseline': _p((TAULA[0] + TAULA[1]) / 2, TAULA[2])[1],
     'zIndex': 20, 'variants': ('ulls_dia',), 'props': ('telefon',)},   # el telèfon, damunt la taula i davant dels qui seuen
    {'id': 'davant_tamboret', 'mask': _amo({'tamboret'}), 'baseline': _p(TAMB[0][0], TAMB[0][1])[1], 'zIndex': 20, 'variants': ('ulls_dia',)},
    {'id': 'davant_primer_pla', 'mask': _amo({'primer_pla'}), 'baseline': 999, 'zIndex': 20, 'variants': ('ulls_dia',)},
]


# ─── Geometria (coordenades de sala, projectades) ────────────────────────────

def _rect_mon(*Ps):
    pts = [CAM.projecta(P) for P in Ps]
    return (max(0, round(min(p[0] for p in pts))), max(0, round(min(p[1] for p in pts))),
            min(W - 1, round(max(p[0] for p in pts))), min(BOTTOM, round(max(p[1] for p in pts))))


# El terra on es camina (al món): davant la taula, fins a les portes de l'esquerra i el passaplats (pel costat de la
# taula) i fins a la porta del passadís (entre l'aparador i la paret de la dreta).
WALK_MON = [(14, 40), (14, 286), (54, 286), (60, 184), (290, 180), (290, 262), (360, 262), (362, 296), (424, 296),
            (440, 140), (440, 20)]


def _escala_a(v):
    """L'escala d'un personatge amb els peus a la y de pantalla `v` (al terra, la profunditat només depèn de v)."""
    lo, hi = 1.0, 3000.0
    for _ in range(60):
        z = (lo + hi) / 2
        if CAM.projecta((260, 0, z))[1] > v:
            lo = z
        else:
            hi = z
    return CAM.escala((260, 0, (lo + hi) / 2))


def _talla(poly, vmax):
    """El polígon (de pantalla) retallat per sota de `vmax`: on un personatge passaria de l'escala màxima."""
    out = []
    for (ax, ay), (bx, by) in zip(poly, poly[1:] + poly[:1]):
        if ay <= vmax:
            out.append((ax, ay))
        if (ay <= vmax) != (by <= vmax):
            k = (vmax - ay) / (by - ay)
            out.append((round(ax + (bx - ax) * k), vmax))
    return out


def _v_escala(k):
    """La y de pantalla on un personatge fa l'escala `k`."""
    lo, hi = 0.0, float(BOTTOM)
    for _ in range(40):
        m = (lo + hi) / 2
        if _escala_a(m) < k:
            lo = m
        else:
            hi = m
    return int(lo)


ESCALA_MAX = 1.2
_WALK = _talla([_p(x, z) for x, z in WALK_MON], _v_escala(ESCALA_MAX))
_V_FONS, _V_PROP = min(v for _, v in _WALK), max(v for _, v in _WALK)
_V_SEU = _p(160, SEU_Z)[1]
_V_TOP = min(_V_FONS, _V_SEU) - 4

GEOMETRIA = {
    'things': {
        'porta_popa': {'rect': _rect_mon((0, D_POPA[2], D_POPA[0]), (0, 0, D_POPA[1])), 'walk': _p(30, (D_POPA[0] + D_POPA[1]) / 2)},
        'porta_cuina': {'rect': _rect_mon((0, D_CUINA[2], D_CUINA[0]), (0, 0, D_CUINA[1])),
                        'walk': _p(30, (D_CUINA[0] + D_CUINA[1]) / 2)},
        'passaplats': {'rect': _rect_mon((0, HATCH[3], HATCH[0]), (0, HATCH[2], HATCH[1])), 'walk': _p(34, 262)},
        'poster': {'rect': _rect_mon((POSTER[0], POSTER[3], ZW), (POSTER[1], POSTER[2], ZW)), 'walk': _p(170, 182)},
        'taula': {'rect': _rect_mon(*[(x, y, z) for x in (TAULA[0], TAULA[1]) for z in (TAULA[2], TAULA[3])
                                      for y in (0, TAULA[4] + 4)]), 'walk': _p(170, 182)},
        'porta_passadis': {'rect': _rect_mon((D_PASS[0] - 4, D_PASS[2] + 4, ZW), (D_PASS[1] + 4, 0, ZW)),
                           'walk': _p((D_PASS[0] + D_PASS[1]) / 2, 288)},
    },
    'spawns': {'iri': _p(350, 140), 'vet': _p(40, 150),
               **{c: _p(x, SEU_Z) for c, x in zip(('capitana', 'bastida', 'marcel', 'tomas', 'juana', 'nadia'), SEIENTS)},
               'lind': (TELEFON[0], TELEFON[1] + 12)},            # la veu de la Lind surt del telèfon (el text, just a sobre)
    'walkable': _WALK,
    'floorSquash': 0.4,
    # L'ombra de contacte: la llum dominant són els llums de damunt la taula; curta.
    'characterShadow': {'enabled': True, 'color': '#120a06', 'alpha': 0.42, 'squash': 0.4, 'core': 0.6,
                        'light': {'x': _p(176, 214)[0], 'y': _p(176, 214)[1], 'stretch': 0.5, 'reach': 160}},
    'regions': [{'id': 'perspectiva', 'active': True, 'scaleEnabled': True, 'scaleWalkSpeed': True,
                 'scaleTop': round(_escala_a(_V_TOP), 3), 'scaleBottom': round(_escala_a(_V_PROP + 2), 3),
                 'points': [(0, _V_TOP), (W - 1, _V_TOP), (W - 1, _V_PROP + 2), (0, _V_PROP + 2)]}],
    'characterLights': {
        'ambient': '#a89880',
        'lights': [
            *[{'x': _p(x, z, HW - 14)[0], 'y': _p(x, z, HW - 14)[1], 'radius': 200, 'color': '#ffd28c',
               'intensity': 0.7} for x, z in LAMPS],
            {'x': _p(0, (HATCH[0] + HATCH[1]) / 2, 100)[0], 'y': _p(0, (HATCH[0] + HATCH[1]) / 2, 100)[1],
             'radius': 120, 'color': '#ffb46e', 'intensity': 0.6},
            {'x': _p(0, 160, 120)[0], 'y': _p(0, 160, 120)[1], 'radius': 200, 'color': '#c8e6ff', 'intensity': 0.6,
             'whenPropVisible': 'ulls_dia'},
        ],
    },
}
