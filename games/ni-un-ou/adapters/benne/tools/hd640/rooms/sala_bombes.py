"""
La sala de bombes de l'Arenga: neta, pintada i callada. EN 3D (hd640/tres_d.py), a 1×.

Una càmera alta, a la dreta, que mira de biaix la cantonada del fons a l'esquerra:
  - a la paret de l'esquerra, en escorç: el **col·lector** de vàlvules (C.I., LL.1, LL.2, LL.3), amb els manòmetres,
    els rètols i el cartell d'ATENCIÓ;
  - a la paret del fons: l'**escala** de mà que puja a l'**escotilla** del sostre (oberta: en baixa la llum del
    passadís, que fa un bassal al terra) i l'armari d'arrencada amb els pilots apagats;
  - les tres **bombes** (la contraincendis vermella i les dues de llast verdes), separades de la paret i dretes damunt
    de les bancades, amb la sortida que puja i torna cap a la paret; davant, la línia groga de seguretat;
  - el terra pintat i brillant (s'hi reflecteix la sala), amb el tollet de la gota;
  - primer pla: la safata de cables per dalt, una canonada a la dreta i unes caixes de recanvis a baix a la dreta.

El detall ve del dibuix pla de sempre (sala_bombes_pla_comu.py), projectat. Els props (el llibre de la Juana i la
llanterna) es fan en 3D a terra, i en surt la diferència amb el fons.

El món: x a la dreta (0 = la paret del col·lector), y amunt (0 = el terra), z cap al fons (300 = la paret del fons);
1 unitat = 1 píxel de sala a la distància on un personatge fa ≈110 px (escala 1).
"""
import functools
import math

import hd640  # noqa: F401  (abans de cap hd.rooms: posa la llibreria a 640×360)

from hd.pix import Canvas, Light, W, H, hr, mix, PAPER
from hd.rooms.arenga import CAB, DARK, WHITEP, YELL, REDP, SEAG, WARM
from hd.rooms.comu import _diff
from hd640.rooms import sala_bombes_pla_comu as PL
from hd640.rooms.sala_bombes_pla_comu import FLOORP, BOOK
from hd640.tres_d import Camera, Escena, Llum

BOTTOM = 259                                       # la sala acaba aquí (a sota, la barra de verbs)
ZW = 300                                           # la paret del fons
HW = PL.FLOOR_Y                                    # l'alçada de les parets (el dibuix pla fa 203 fins al terra)
XL = 262                                           # al dibuix pla, la cantonada: a l'esquerra, la paret del col·lector
XR = 440                                           # la paret de la dreta
ZN = -240
PZ = ZW - 34                                       # les bombes, separades de la paret (z de l'eix)
PUMPS = ((411, REDP, 'C.I.'), (501, SEAG, 'LL1'), (584, SEAG, 'LL2'))
LAMPS = ((150, 150), (300, 200))                   # les dues bombetes del sostre (x, z)
BOOK_P = (126, 150, 0.5)                           # el llibre de la Juana, obert de cara avall (x, z, gir)
TORCH_P = (196, 196, 0.12)                         # la llanterna, a terra apuntant cap a les bombes (x, z, gir)


def _w(fx):
    """Una x del dibuix pla de la paret del fons → la x del món."""
    return fx - XL


def _wz(fx):
    """Una x del dibuix pla de la paret del col·lector → la z del món."""
    return ZW - XL + fx


def _y(fy):
    return HW - fy


CAM = Camera(pos=(330, 180, -150), yaw=-0.26, pitch=0.18, f=350, centre=(318, 108))

LIGHT = Light(ambient=0.0, vignette=None, floor_fade=None)  # (la llum és la del món: la de l'Escena)
TEXL = Light(ambient=0.8, vignette=None, floor_fade=None)  # les textures: llum plana (la fa l'escena)
HATCH = (_w(275), _w(339), ZW - 46, ZW)              # el forat de l'escotilla al sostre: x0, x1, z0, z1
LLUMS = [Llum((LAMPS[0][0], 176, LAMPS[0][1]), 260, 2.2, power=1.4),
         Llum((LAMPS[1][0], 176, LAMPS[1][1]), 260, 2.2, power=1.4),
         Llum(((HATCH[0] + HATCH[1]) / 2, HW + 10, ZW - 20), 170, 1.4, power=1.5)]   # el passadís, per l'escotilla

FOSC = [(3, 5, 5), (7, 10, 10), (12, 16, 16), (18, 23, 22), (26, 32, 30), (36, 43, 40)]
WATER = PL.WATER


# ─── Les textures: el dibuix pla de sempre ───────────────────────────────────

def _paret_llisa():
    cv = Canvas(light=TEXL)
    PL.walls(cv)
    PL.ceiling(cv)
    return cv


@functools.lru_cache(maxsize=None)
def _llisa():
    return _paret_llisa().img


def _paret(jitter=None):
    """Les dues parets planes, de cara: el col·lector (amb els manòmetres), l'escala, l'armari i la canonada de dalt
    de les bombes. `jitter`: el fotograma de les agulles dels manòmetres."""
    cv = _paret_llisa()
    PL.manifold(cv)
    if jitter is not None:
        for k, gx in enumerate(PL.GAUGES):
            PL.gauge_face(cv, gx, PL.GAUGE_Y, PL.gauge_angle(k, jitter[k]))
            cv.put(gx - 3, PL.GAUGE_Y - 4, WHITEP, 5.6)
            cv.put(gx - 4, PL.GAUGE_Y - 3, WHITEP, 5.2)
    PL.panel(cv)
    PL.hatch(cv)
    llisa = _llisa()
    cv.img.paste(llisa.crop((262, 0, 360, 34)), (262, 0))          # (l'escotilla, al sostre: es fa en 3D)
    cv.P = cv.img.load()
    # la canonada de dalt de les bombes, de punta a punta, i les etiquetes
    from hd.rooms.arenga import hpipe
    hpipe(cv, 387, W - 1, 59, 5, SEAG, 3.0, bands=range(400, W, 67), band_ramp=WHITEP)
    for x in (395, 470, 545, 620):
        cv.vline(x, 28, 52, CAB, 2.2)
        cv.vline(x + 1, 28, 52, CAB, 3.4)
    PL._label(cv, 'C.I.', 389, 75, ramp=REDP, lvl=3.6, ink=(240, 230, 220))
    PL._label(cv, 'LLAST 1', 467, 75, ramp=WHITEP, lvl=3.8)
    PL._label(cv, 'LLAST 2', 549, 75, ramp=WHITEP, lvl=3.8)
    return cv.img


@functools.lru_cache(maxsize=None)
def _paret_base():
    return _paret()


@functools.lru_cache(maxsize=None)
def _bombes():
    """Les bombes, planes sobre transparent (en surten els retalls: cadascuna, sense la sortida)."""
    cv = Canvas(light=TEXL, transparent=True)
    for cx, body, tag in PUMPS:
        PL.pump(cv, cx, body, tag)
    PL.cage_lamp(cv, 147)
    return cv.img


def _pump_box(cx):
    return (cx - 42, PL.FLOOR_Y + 3 - 135, cx + 32, PL.FLOOR_Y + 4)


LAMP_BOX = (138, 20, 157, 40)


# ─── Les superfícies ────────────────────────────────────────────────────────

def _terra(s, t, P):
    """El terra pintat: planxes de 128 amb les juntes, net i llis (la brillantor la fa el reflex)."""
    x, z = P[0], P[2]
    if x % 128 < 1.2 or z % 128 < 1.2:
        return 2.0
    if x % 128 < 2.2 or z % 128 < 2.2:
        return 3.4
    return 3.0 + (hr(int(x // 4), int(z // 4), 7) - 0.5) * 0.25 + (hr(int(x // 128), int(z // 128), 3) - 0.5) * 0.3


def _el(rx, rz, k):
    return lambda s, t: k * max(0.0, 1 - ((s - rx) / rx) ** 2 - ((t - rz) / rz) ** 2) * 1.5


def _foscor_el(e, sid, cx, cz, rx, rz, k, y=0.6):
    e.foscor(sid, (cx - rx, y, cz + rz), (cx + rx, y, cz + rz), (cx + rx, y, cz - rz), (cx - rx, y, cz - rz),
             _el(rx, rz, k))


def escena(cv, tex, estat=frozenset()):
    """Tota la sala, de lluny a prop. `estat`: 'llibre', 'llanterna' (els props). → l'Escena."""
    e = Escena(cv, CAM, LLUMS + ([Llum((TORCH_P[0] + 60, 20, TORCH_P[1] + 20), 120, 1.2)] if 'llanterna' in estat
                                 else []), ambient=-0.4)
    paret, llisa, bom = tex['paret'], tex['llisa'], tex['bombes']
    # el sostre, amb l'escotilla oberta (un forat clar: el passadís de dalt)
    hx0, hx1, hz0, hz1 = HATCH

    def sostre(s, t, P):
        x, z = P[0], P[2]
        if hx0 < x < hx1 and hz0 < z < hz1:
            return 5.0 - (0.8 if int(x) % 9 == 0 else 0)
        if hx0 - 6 < x < hx1 + 6 and hz0 - 6 < z < hz1:
            return 4.0 if abs(x - hx0 + 3) < 1 or abs(z - hz0 + 3) < 1 else 3.0
        v = 1.0
        if z % 64 < 8:
            v = 2.4 if z % 64 < 1.5 else 1.6
        return v
    e.quad('sostre', (0, HW, ZN), (XR, HW, ZN), (XR, HW, ZW), (0, HW, ZW), ramp=PL.WALL, lvl=sostre, dues_cares=True)
    # les parets
    e.quad('paret_esq_prop', (0, HW, ZN), (0, HW, ZW - XL), (0, 0, ZW - XL), (0, 0, ZN),
           tex=(llisa, (W - 1 - (ZW - XL - ZN), 0, W - 1, HW)))
    e.quad('paret_esq', (0, HW, ZW - XL), (0, HW, ZW), (0, 0, ZW), (0, 0, ZW - XL), tex=(paret, (0, 0, XL, HW)))
    e.quad('paret_fons', (0, HW, ZW), (XR, HW, ZW), (XR, 0, ZW), (0, 0, ZW), tex=(paret, (XL, 0, XL + XR, HW)))
    e.quad('paret_dreta', (XR, HW, ZW), (XR, HW, ZN), (XR, 0, ZN), (XR, 0, ZW), tex=(llisa, (60, 0, 60 + ZW - ZN, HW)))
    # el terra, i la línia groga davant les bombes
    e.quad('terra', (0, 0, ZW), (XR, 0, ZW), (XR, 0, ZN), (0, 0, ZN), ramp=FLOORP, lvl=_terra)
    lz = PZ - 30
    e.quad('terra', (_w(380), 0.2, lz + 3), (XR, 0.2, lz + 3), (XR, 0.2, lz - 3), (_w(380), 0.2, lz - 3), ramp=YELL,
           lvl=lambda s, t, P: 3.6 - (0.8 if t > 4 else 0), forma=lambda s, t: int(s // 8) % 2 == 0)
    # el bassal de llum de l'escotilla, i el de les bombetes
    e.claror((hx0 - 30, 0.3, ZW), (hx1 + 40, 0.3, ZW), (hx1 + 60, 0.3, ZW - 110), (hx0 - 20, 0.3, ZW - 110),
             (200, 230, 200), lambda s, t: 0.30 * max(0.0, 1 - math.hypot(s - 60, t - 30) / 70))
    for (lx, lz_), k in zip(LAMPS, (0.24, 0.24)):
        e.claror((lx - 130, 0.3, lz_ + 130), (lx + 130, 0.3, lz_ + 130), (lx + 130, 0.3, lz_ - 130),
                 (lx - 130, 0.3, lz_ - 130), WARM,
                 lambda s, t, k=k: k * max(0.0, 1 - math.hypot(s - 130, (t - 130) * 1.1) / 130) ** 1.5)
    # la foscor dels racons
    e.foscor('racons', (0, 0.5, ZW), (XR, 0.5, ZW), (XR, 0.5, ZN), (0, 0.5, ZN),
             lambda s, t: max(0.55 * max(0.0, 1 - t / 30), 0.5 * max(0.0, 1 - s / 26), 0.5 * max(0.0, 1 - (XR - s) / 26)))
    e.foscor('cantonada', (0, HW, ZW - 0.5), (80, HW, ZW - 0.5), (80, 0, ZW - 0.5), (0, 0, ZW - 0.5),
             lambda s, t: 0.45 * max(0.0, 1 - s / 80))
    e.foscor('cantonada2', (0.5, HW, ZW - 80), (0.5, HW, ZW), (0.5, 0, ZW), (0.5, 0, ZW - 80),
             lambda s, t: 0.45 * max(0.0, 1 - (80 - s) / 80))
    e.foscor('cantonada3', (XR - 0.5, HW, ZW), (XR - 0.5, HW, ZW - 100), (XR - 0.5, 0, ZW - 100), (XR - 0.5, 0, ZW),
             lambda s, t: 0.45 * max(0.0, 1 - s / 100))
    e.foscor('sostre_fosc', (0, HW - 0.5, ZW - 0.6), (XR, HW - 0.5, ZW - 0.6), (XR, 0, ZW - 0.6), (0, 0, ZW - 0.6),
             lambda s, t: 0.45 * max(0.0, 1 - t / 60))
    e.foscor('sostre_fosc2', (0.6, HW - 0.5, ZN), (0.6, HW - 0.5, ZW), (0.6, 0, ZW), (0.6, 0, ZN),
             lambda s, t: 0.45 * max(0.0, 1 - t / 60))
    # el tollet de la gota, sota el col·lector
    dz = _wz(PL.DRIP[0])
    e.foscor('tollet', (4, 0.4, dz + 9), (26, 0.4, dz + 9), (26, 0.4, dz - 9), (4, 0.4, dz - 9),
             lambda s, t: 0.3 * max(0.0, 1 - ((s - 11) / 11) ** 2 - ((t - 9) / 9) ** 2) * 2)
    e.claror((4, 0.45, dz + 9), (26, 0.45, dz + 9), (26, 0.45, dz - 9), (4, 0.45, dz - 9), WATER,
             lambda s, t: 0.35 if 0.5 < ((s - 9) / 6) ** 2 + ((t - 9) / 4) ** 2 < 0.9 and s < 11 else 0)
    # l'escala de mà, contra la paret del fons, fins a l'escotilla
    lx0, lx1 = _w(290), _w(323)
    for x in (lx0 - 2, lx1 + 2):
        e.tub('escala', (x, 0, ZW - 14), (x, HW + 4, ZW - 14), 2.2, CAB, 3.6)
        e.caixa('escala', x - 3, x + 3, 0, 1.5, ZW - 18, ZW - 10, CAB, 2.6)
    for y in range(32, HW, 13):
        e.tub('escala', (lx0, HW - y, ZW - 14), (lx1, HW - y, ZW - 14), 1.3, CAB, 3.8)
    # la brazola de l'escotilla, que penja del sostre, i la llum del passadís de dalt, que es veu pel forat
    from hd.rooms.arenga import ENG
    e.caixa('escotilla', hx0 - 7, hx1 + 7, HW - 10, HW, hz0 - 7, ZW, ENG, 3.0,
            cares={'davant': {'ramp': ENG, 'lvl': lambda s, t, P: 3.4 + (1.2 if t < 1.2 else 0) - (0.8 if int(s) % 7 == 0 and 3 < t < 6 else 0)},
                   'sota': {'ramp': PL.WALL, 'lvl': lambda s, t, P: 5.4 if 7 < s < hx1 - hx0 + 7 and t > 7 else 3.0}})
    e.claror((hx0 - 20, HW - 10, ZW - 0.8), (hx1 + 20, HW - 10, ZW - 0.8), (hx1 + 30, 0, ZW - 0.8), (hx0 - 30, 0, ZW - 0.8),
             (200, 230, 200), lambda s, t: 0.22 * max(0.0, 1 - t / 190) * max(0.0, 1 - abs(s - (hx1 - hx0 + 40) / 2) / 60))
    # l'agafamà de l'escotilla
    for x in (hx0 + 2, hx1 - 2):
        e.tub('escala', (x, HW - 22, ZW - 40), (x, HW, ZW - 40), 1.2, [(36, 28, 6), (100, 76, 20), (180, 140, 40),
                                                                    (230, 190, 90)], 2.6)
    # les bombes, en volum (vegeu _bomba): de l'esquerra (més lluny) a la dreta (més a prop de la càmera)
    for cx, body, tag in PUMPS:
        _bomba(e, cx, body, tag, bom, tex['motors'][tag])
    # el llibre i la llanterna (els props)
    if 'llibre' in estat:
        _llibre(e)
    if 'llanterna' in estat:
        _llanterna(e)
    _primer_pla(e)
    return e


# ─── Les bombes, en volum ───────────────────────────────────────────────────
#
# Cada bomba és la del dibuix pla (PL.pump) feta peces: la bancada (el davant, amb els perns, del dibuix pla), la
# voluta (un cilindre el·líptic ajagut, de cara a la sala: la tapa amb el cercle de perns és el dibuix pla), la
# llanterna d'acoblament (una caixa amb la finestra i la protecció groga del dibuix pla al davant), el motor (un
# cilindre vertical de facetes amb les aletes i la placa del nom, desenrotllades a `_motor_pla`), la brida del motor,
# la tapa del ventilador amb la reixeta, la caixa de borns al costat i el cable que puja a la safata. L'aspiració surt
# per l'esquerra i torna enrere fins a la paret; la impulsió surt per la dreta, puja amb la vàlvula de retenció i torna
# a la paret per dalt, al col·lector pintat. La contraincendis és vermella (voluta i canonades) i porta «C.I.».

MOTOR_R = 19.5                                     # el radi del motor (el dibuix pla en fa 39 d'ample)
MOTOR_H = 53                                       # l'alçada del cos del motor, sense la brida
MOTOR_TW = round(2 * math.pi * MOTOR_R)            # el motor desenrotllat: l'amplada de la textura
PLACA = (21, 13, 1.25)                             # la placa del nom: amplada i alçada al dibuix pla, i com s'amplia


def _yb(fy):
    """Una y del dibuix pla de les bombes → la y del món (la bancada fa 12 i el seu cantó de dalt és base_y - 11)."""
    return PL.FLOOR_Y + 4 - fy


@functools.lru_cache(maxsize=None)
def _motor_pla(tag):
    """El motor desenrotllat (la volta sencera, amb el davant al mig): les aletes i la fletxa del sentit de gir; a sota
    (y ≥ MOTOR_H + 4), la placa amb el nom, que va a part (plana). Llum plana: la del món la fa cada faceta."""
    from hd.rooms.arenga import ENG_LIGHT, box
    from hd.rooms.comu import text, text_width
    cv = Canvas(light=TEXL)
    TW, H_ = MOTOR_TW, MOTOR_H
    for y in range(H_):
        for x in range(TW):
            v = 3.3 + (0.35 if x % 4 < 2 else 0) - (0.35 if x % 4 == 3 else 0)
            if y == 0:
                v += 0.6
            elif y >= H_ - 2:
                v -= 0.5
            cv.put(x, y, ENG_LIGHT, v)
    cx = TW // 2
    py = H_ + 4
    box(cv, 0, py, PLACA[0] - 1, py + PLACA[1] - 1, WHITEP, 3.8)
    w = text_width(tag)
    text(cv, tag, PLACA[0] // 2 - w // 2, py + 2, None, 0, flat=PL.INK)
    for x in range(2, PLACA[0] - 2, 2):
        cv.put(x, py + 9, DARK, 1.6)
    cv.line(cx - 8, 44, cx + 6, 44, REDP, 3.6)
    cv.line(cx + 6, 44, cx + 3, 41, REDP, 3.6)
    cv.line(cx + 6, 44, cx + 3, 47, REDP, 3.6)
    return cv.img


def _cara(e, sid, Ps, fora, **kw):
    """Un quad del món amb la cara de fora cap a `fora` (es reordenen els cantons si cal)."""
    P0, P1, P2, P3 = Ps
    a = (P1[0] - P0[0], P1[1] - P0[1], P1[2] - P0[2])
    b = (P3[0] - P0[0], P3[1] - P0[1], P3[2] - P0[2])
    n = (a[1] * b[2] - a[2] * b[1], a[2] * b[0] - a[0] * b[2], a[0] * b[1] - a[1] * b[0])
    if n[0] * fora[0] + n[1] * fora[1] + n[2] * fora[2] < 0:
        P0, P1, P2, P3 = P1, P0, P3, P2
    e.quad(sid, P0, P1, P2, P3, **kw)


def _disc(e, sid, x, y, z, r, ramp, lvl):
    """Una tapa rodona horitzontal (de cara amunt), de radi r."""
    e.quad(sid, (x - r, y, z + r), (x + r, y, z + r), (x + r, y, z - r), (x - r, y, z - r), ramp=ramp, lvl=lvl,
           forma=lambda s, t: (s - r) ** 2 + (t - r) ** 2 <= r * r)


def _cilindre(e, sid, x, z, r, y0, y1, ramp, lvl=3.0, tex=None, n=20, a0=0.0):
    """Un cilindre vertical de facetes (els costats; la tapa, a part). `tex` = (imatge, amplada, alçada): la volta
    sencera desenrotllada, amb el mig de la imatge mirant cap a `a0`."""
    for i in range(n):
        a, b = a0 - math.pi + 2 * math.pi * i / n, a0 - math.pi + 2 * math.pi * (i + 1) / n
        Ps = ((x + r * math.sin(a), y1, z - r * math.cos(a)), (x + r * math.sin(b), y1, z - r * math.cos(b)),
              (x + r * math.sin(b), y0, z - r * math.cos(b)), (x + r * math.sin(a), y0, z - r * math.cos(a)))
        if tex is not None:
            img, tw, th = tex
            e.quad(sid, *Ps, tex=(img, (tw * i / n, 0, tw * (i + 1) / n, th)))
        else:
            e.quad(sid, *Ps, ramp=ramp, lvl=lvl)


def _voluta(e, sid, x, yc, z0, z1, rx, ry, ramp, lvl=3.0, n=18):
    """La voluta: un cilindre el·líptic ajagut al llarg de z (de z0, el davant, a z1), només els costats."""
    for i in range(n):
        a, b = 2 * math.pi * i / n, 2 * math.pi * (i + 1) / n
        m = (a + b) / 2
        Pa = (x + rx * math.cos(a), yc + ry * math.sin(a))
        Pb = (x + rx * math.cos(b), yc + ry * math.sin(b))
        _cara(e, sid, ((Pa[0], Pa[1], z0), (Pb[0], Pb[1], z0), (Pb[0], Pb[1], z1), (Pa[0], Pa[1], z1)),
              (math.cos(m) / rx, math.sin(m) / ry, 0), ramp=ramp,
              lvl=lambda s, t, P, lvl=lvl: lvl + (0.9 if t < 1.6 else 0) - (0.5 if 2.4 < t < 3.6 else 0))


def _bomba(e, cx, body, tag, bom, motor):
    """Una bomba en volum. `cx`: la x del dibuix pla; `bom`: el dibuix pla de les bombes; `motor`: `_motor_pla(tag)`."""
    from hd.rooms.arenga import ENG_LIGHT
    sid = 'bombes'
    x, z = _w(cx), PZ
    base_y = PL.FLOOR_Y + 3
    vy = base_y - 27                               # el centre de la voluta, al dibuix pla
    yv, rx, ry = _yb(vy), 23, 16                   # (la voluta s'assenta a la bancada)
    ly0, ly1 = base_y - 69, base_y - 43            # la llanterna d'acoblament
    my0, my1 = base_y - 128, base_y - 70           # el motor (amb la brida a baix, de 5)
    ym0, ym1 = _yb(my1), _yb(my0)
    ix, ox = x - 32, x + 39                        # l'aspiració (esquerra) i la impulsió (dreta)
    yt = _y(59)                                    # el col·lector pintat de dalt
    # l'ombra a terra (sota la bancada, i la que fa cap enrere a l'esquerra, lluny de les bombetes)
    _foscor_el(e, 'ombra_bombes', x - 2, z - 2, 44, 22, 0.55)
    e.foscor('ombra_bombes', (x - 70, 0.6, z + 4), (x + 10, 0.6, z + 4), (x - 10, 0.6, z - 50),
             (x - 90, 0.6, z - 50), lambda s, t: 0.3 * max(0.0, 1 - abs(t - 27) / 27) * max(0.0, 1 - abs(s - 40) / 40))
    # el que va cap a la paret (de lluny a prop): la impulsió per dalt i l'aspiració per baix, amb les brides de paret
    e.tub(sid, (ox, yt, z), (ox, yt, ZW - 1), 5, body, 3.0)
    e.tub(sid, (ox, yt, ZW - 5), (ox, yt, ZW - 1), 7.5, body, 3.4)
    e.tub(sid, (ix, yv, ZW - 1), (ix, yv, z - 2), 5, body, 2.8, brides=40)
    e.tub(sid, (ix, yv, ZW - 5), (ix, yv, ZW - 1), 8, body, 3.4)
    # la bancada: el davant, amb els perns, del dibuix pla
    e.caixa(sid, x - 33, x + 33, 0, 12, z - 16, z + 16, CAB, 2.8,
            cares={'dalt': {'ramp': CAB, 'lvl': lambda s, t, P: 3.4 + (1.2 if (abs(s - 5) < 1.2 or abs(s - 61) < 1.2) and abs(t - 16) < 8 and int(t) % 8 < 2 else 0)},
                   'davant': {'tex': (bom, (cx - 32, base_y - 11, cx + 33, base_y + 1))},
                   'dreta': {'ramp': CAB, 'lvl': lambda s, t, P: 2.4 + (0.8 if t < 1.2 else 0)}})
    # l'aspiració: el colze i la brida doble, fins a la voluta
    e.tub(sid, (ix, yv, z - 2), (x - rx + 4, yv, z - 2), 5, body, 3.0)
    for bx in (x - 26, ix):
        e.tub(sid, (bx - 1.2, yv, z - 2), (bx + 1.2, yv, z - 2), 8, body, 3.6)
    # la voluta, amb la tapa de davant del dibuix pla (el cercle de perns i el tap de purga)
    _voluta(e, sid, x, yv, z - 12, z + 10, rx, ry, body, 2.8)
    e.quad(sid, (x - rx, yv + ry, z - 12), (x + rx, yv + ry, z - 12), (x + rx, yv - ry, z - 12),
           (x - rx, yv - ry, z - 12), tex=(bom, (cx - 23, vy - 16, cx + 24, vy + 17)),
           forma=lambda s, t: ((s - rx) / rx) ** 2 + ((t - ry) / ry) ** 2 <= 1.0)
    # la llanterna d'acoblament: la finestra amb l'eix i la protecció groga, del dibuix pla
    e.caixa(sid, x - 12, x + 12, _yb(ly1), _yb(ly0), z - 9, z + 9, CAB, 2.8,
            cares={'davant': {'tex': (bom, (cx - 12, ly0, cx + 13, ly1 + 1))},
                   'dreta': {'ramp': CAB, 'lvl': lambda s, t, P: 2.2 + (0.9 if s < 1.2 else 0)}})
    # el motor: la brida, el cos d'aletes (amb la placa i la fletxa) i la tapa del ventilador amb la reixeta
    _cilindre(e, sid, x, z, 21, ym0, ym0 + 5, ENG_LIGHT, 3.0, n=20)
    _disc(e, sid, x, ym0 + 5, z, 21, ENG_LIGHT, lambda s, t, P: 3.8)
    ap = 0.7 * math.atan2(CAM.pos[0] - x, -(CAM.pos[2] - z))   # el davant del motor, girat una mica cap a la càmera
    _cilindre(e, sid, x, z, MOTOR_R, ym0 + 5, ym1, None, tex=(motor, MOTOR_TW, MOTOR_H), n=20, a0=ap)
    # la placa del nom, plana, cargolada al davant del motor
    pw, ph = PLACA[0] * PLACA[2] / 2, PLACA[1] * PLACA[2] / 2
    rr, yc = MOTOR_R + 0.6, ym1 - 26
    C = (x + rr * math.sin(ap), z - rr * math.cos(ap))
    tx, tz = math.cos(ap), math.sin(ap)
    e.quad(sid, (C[0] - tx * pw, yc + ph, C[1] - tz * pw), (C[0] + tx * pw, yc + ph, C[1] + tz * pw),
           (C[0] + tx * pw, yc - ph, C[1] + tz * pw), (C[0] - tx * pw, yc - ph, C[1] - tz * pw),
           tex=(motor, (0, MOTOR_H + 4, PLACA[0], MOTOR_H + 4 + PLACA[1])))
    _disc(e, sid, x, ym1, z, MOTOR_R, ENG_LIGHT, lambda s, t, P: 3.6)
    _cilindre(e, sid, x, z, 17, ym1, ym1 + 4, ENG_LIGHT, 3.4, n=18)
    _disc(e, sid, x, ym1 + 4, z, 17, ENG_LIGHT,
          lambda s, t, P: 2.0 if int(math.hypot(s - 17, t - 17)) % 3 == 0 and math.hypot(s - 17, t - 17) < 14 else 3.9)
    # la caixa de borns, al costat del motor, amb el premsaestopes i el cable que puja a la safata
    e.caixa(sid, x + 16, x + 27, _yb(my0 + 37), _yb(my0 + 17), z - 6, z + 6, ENG_LIGHT, 3.0,
            cares={'dalt': {'ramp': ENG_LIGHT, 'lvl': 4.0}})
    e.caixa(sid, x + 19, x + 24, _yb(my0 + 17), _yb(my0 + 14), z - 2, z + 2, CAB, 3.4)
    e.cable(sid, [(x + 21.5, _yb(my0 + 14), z), (x + 22, HW - 30, z + 6), (x + 22, HW - 4, ZW - 6)], CAB, 2.4, gruix=1.6)
    # la impulsió: surt per la dreta de la voluta, colze, puja (amb la vàlvula de retenció) fins al col·lector
    e.tub(sid, (x + rx - 4, yv, z), (ox, yv, z), 5, body, 3.0)
    e.tub(sid, (ox, yv, z), (ox, yt, z), 5, body, 2.8, brides=46)
    e.caixa(sid, ox - 6, ox + 6, _y(134), _y(122), z - 6, z + 6, body, 3.0)
    e.tub(sid, (ox, yt, z), (ox, yt, z), 5.6, body, 3.2)              # (el colze de dalt)


def _gira(cx, cz, a):
    c, s = math.cos(a), math.sin(a)
    return lambda lx, y, lz: (cx + lx * c - lz * s, y, cz + lx * s + lz * c)


def _llibre(e):
    """El llibre de la Juana, obert de cara avall a terra (fa de teulada), amb el punt de llibre vermell."""
    cx, cz, a = BOOK_P
    P = _gira(cx, cz, a)
    w, d, h = 17, 24, 8
    _foscor_el(e, 'llibre', cx, cz, 22, 16, 0.55, y=0.5)
    e.quad('llibre', P(-w, 1, -d / 2), P(-w, 1, d / 2), P(-w + 3, 0.5, d / 2), P(-w + 3, 0.5, -d / 2), ramp=PAPER,
           lvl=lambda s, t, P_: 3.6 - (1.0 if int(t) % 2 else 0), dues_cares=True)
    e.quad('llibre', P(-w, 1.5, d / 2), P(0, h, d / 2), P(0, h, -d / 2), P(-w, 1.5, -d / 2), ramp=BOOK,
           lvl=lambda s, t, P_: 3.4 + (1.0 if 6 < s < 11 and abs(t - 12) < 2 else 0), dues_cares=True)
    e.quad('llibre', P(0, h, d / 2), P(w, 1.5, d / 2), P(w, 1.5, -d / 2), P(0, h, -d / 2), ramp=BOOK,
           lvl=lambda s, t, P_: 2.4, dues_cares=True)
    e.quad('llibre', P(w - 3, 0.5, d / 2), P(w, 1, d / 2), P(w, 1, -d / 2), P(w - 3, 0.5, -d / 2), ramp=PAPER,
           lvl=3.0, dues_cares=True)
    e.cable('llibre', [P(2, h - 1, -d / 2 + 4), P(6, 2, -d / 2 - 3), P(10, 0.5, -d / 2 - 8)], REDP, 3.6, gruix=1.4)


def _llanterna(e):
    """La llanterna groga, a terra, encesa i apuntant cap a les bombes: el feix pel terra i la taca a la bancada."""
    cx, cz, a = TORCH_P
    P = _gira(cx, cz, a)
    c, s = math.cos(a), math.sin(a)
    # el feix: un con pel terra cap a la bomba vermella
    L = 170
    e.claror(P(12, 0.6, -60), P(12 + L, 0.6, -60), P(12 + L, 0.6, 60), P(12, 0.6, 60), (255, 238, 170),
             lambda s_, t: 0.6 * (1 - s_ / L) ** 0.8 * max(0.0, 1 - (abs(t - 60) / (4 + s_ * 0.33)) ** 2))
    _foscor_el(e, 'llanterna', cx, cz, 18, 7, 0.55, y=0.5)
    e.tub('llanterna', P(-14, 5, 0), P(8, 5, 0), 5, YELL, 3.4)
    e.caixa_girada('llanterna', cx + 11 * c, cz + 11 * s, 7, 14, 13, a, CAB, 3.2, y0=-1.5,
                   cares={'dreta': {'ramp': [(120, 110, 80), (250, 240, 200), (255, 255, 240)], 'lvl': 2.6}})
    e.cable('llanterna', [P(-15, 4, 0), P(-24, 0.6, 4), P(-34, 0.6, -2)], DARK, 2.0, gruix=1.2)


def _primer_pla(e):
    """La safata de cables per dalt i una canonada a la dreta, de prop, i unes caixes de recanvis a baix a la dreta."""
    e.tub('primer_pla', (XR - 12, 0, -30), (XR - 12, HW, -30), 9, FOSC, 1.8, brides=70)
    e.caixa('primer_pla', -40, XR + 40, HW - 6, HW - 2, -10, 8, FOSC, 1.6,
            cares={'sota': {'ramp': FOSC, 'lvl': lambda s, t, P: 2.6 if int(s) % 7 < 1 else 1.0}})
    e.cable('primer_pla', [(300, HW - 4, 0), (308, HW - 30, 4), (303, HW - 44, 8)], FOSC, 1.6, gruix=2.2)
    for cx, cz, w, d, h, a, y0 in ((396, 96, 60, 42, 38, -0.3, 0), (402, 100, 40, 30, 24, -0.15, 38),
                                   (350, 52, 46, 36, 30, 0.2, 0)):
        e.caixa_girada('primer_pla', cx, cz, w, d, h, a, FOSC, 1.6, y0=y0,
                       cares={'dalt': {'ramp': FOSC, 'lvl': lambda s, t, P, w=w: 2.8 - (1.2 if abs(s - w / 2) < 2 else 0)},
                              'davant': {'ramp': FOSC, 'lvl': 1.2}, 'esquerra': {'ramp': FOSC, 'lvl': 2.0}})


# ─── Composició ─────────────────────────────────────────────────────────────

def _desprojecta(u, v):
    """El punt del terra (y = 0) que es veu al píxel (u, v) i la direcció del raig."""
    c = CAM
    x1, y2 = (u + 0.5 - c.centre[0]) / c.f, -(v + 0.5 - c.centre[1]) / c.f
    dy = y2 * c._cp - c._sp
    z1 = y2 * c._sp + c._cp
    dx = x1 * c._cy + z1 * c._sy
    dz = -x1 * c._sy + z1 * c._cy
    if dy >= -1e-6:
        return None
    k = -c.pos[1] / dy
    return (c.pos[0] + dx * k, c.pos[2] + dz * k), (dx, dy, dz)


def _brillantor(cv, e, k=0.22):
    """El terra pintat i brillant: el reflex de la sala (el raig reflectit, fins a una paret), que s'esvaeix."""
    src = cv.img.copy().load()
    P = cv.P
    terra = {i for i, sid in enumerate(e.ids) if sid in ('terra', 'racons', 'tollet', 'ombra_bombes')}
    for Y in range(60, BOTTOM + 1):
        for X in range(W):
            if e.amo[Y * W + X] not in terra:
                continue
            r = _desprojecta(X, Y)
            if r is None:
                continue
            (px, pz), (dx, dy, dz) = r
            ks = [(ZW - pz) / dz if dz > 1e-6 else 1e9, -px / dx if dx < -1e-6 else 1e9,
                  (XR - px) / dx if dx > 1e-6 else 1e9]
            kk = min(ks)
            Q = (px + dx * kk, -dy * kk, pz + dz * kk)
            if Q[1] >= HW:
                continue
            qu, qv, _ = CAM.projecta(Q)
            if 0 <= qu < W and 0 <= qv < BOTTOM:
                f = k * max(0.0, 1 - Q[1] / 90)
                if f > 0:
                    P[X, Y] = mix(P[X, Y][:3], src[int(qu), int(qv)][:3], f) + (255,)


def _glows(cv):
    for lx, lz in LAMPS:
        u, v, _ = CAM.projecta((lx, HW - 26, lz))
        k = CAM.escala((lx, HW - 26, lz))
        cv.glow(u, v, 46 * k, WARM, 0.5)
        cv.glow(u, v, 15 * k, (255, 240, 200), 0.6)
    u, v, _ = CAM.projecta(((HATCH[0] + HATCH[1]) / 2, HW, ZW - 22))
    cv.glow(u, v + 4, 46, (190, 220, 190), 0.4)


def _penjolls(e):
    lamp = _bombes().crop(LAMP_BOX)
    for lx, lz in LAMPS:
        e.cable('bombetes', [(lx, HW, lz), (lx, HW - 14, lz)], CAB, 2.0, gruix=1.4)
        e.sprite('bombetes', lamp, ((LAMP_BOX[2] - LAMP_BOX[0]) / 2, 0), (lx, HW - 14, lz))


@functools.lru_cache(maxsize=None)
def _textures():
    return {'paret': _paret_base(), 'llisa': _llisa(), 'bombes': _bombes(),
            'motors': {tag: _motor_pla(tag) for _, _, tag in PUMPS}}


def _render(estat=frozenset(), tex=None):
    cv = Canvas(light=LIGHT)
    e = escena(cv, tex or _textures(), estat)
    _brillantor(cv, e)
    _penjolls(e)
    _glows(cv)
    cv.rect(0, BOTTOM + 1, W - 1, H - 1, [(0, 0, 0)], 0, lit=0)    # la barra de verbs: negre
    return cv.img, e


@functools.lru_cache(maxsize=None)
def _base():
    return _render()


def bg(cv):
    cv.img.paste(_base()[0])
    cv.P = cv.img.load()


def _decorat(*estat):
    def draw(cv):
        img, _ = _render(frozenset(estat))
        cv.img.alpha_composite(_diff(img, _base()[0]))
        cv.P = cv.img.load()
    return draw


PROPS = {'llibre': _decorat('llibre'), 'llanterna': _decorat('llanterna')}


# ─── Animacions ─────────────────────────────────────────────────────────────

def _frames_manometres():
    """Les agulles dels dos manòmetres tremolen una mica (el motor principal es nota a tot el vaixell)."""
    img, e = _base()
    jitter = (0.0, 0.14, -0.06, 0.1, -0.14, 0.04)
    out = []
    for i, j in enumerate(jitter):
        flat = _paret((j, -jitter[(i + 2) % len(jitter)]))
        frame = img.copy()
        frame.alpha_composite(e.capa(flat, {'paret_esq'}))
        out.append(_diff(frame, img))
    return out


def _frames_gota():
    """Una gota que s'infla sota el tub del col·lector, cau i esquitxa el tollet; després, una estona de res."""
    img, _ = _base()
    dz = _wz(PL.DRIP[0])
    top = (8, _y(PL.DRIP[1]), dz)
    out = []

    def w(fr, P_, k, du=0, dv=0):
        u, v, _ = CAM.projecta(P_)
        X, Y = int(u) + du, int(v) + dv
        if 0 <= X < W and 0 <= Y < BOTTOM:
            fr.putpixel((X, Y), mix(fr.getpixel((X, Y))[:3], WATER, k) + (255,))
    for i in range(20):
        fr = img.copy()
        if 4 <= i <= 8:
            w(fr, top, 0.55 + 0.08 * (i - 4))
            if i >= 6:
                w(fr, top, 0.65 + 0.1 * (i - 6), dv=1)
            if i == 8:
                w(fr, top, 0.8, dv=2)
        elif i in (9, 10):
            yy = top[1] * (0.55 if i == 9 else 0.12)
            for d in range(4 + (i - 9) * 3):
                w(fr, (top[0], yy, dz), 0.9 - d * 0.13, dv=-d)
        elif i == 11:
            w(fr, (top[0], 0, dz), 0.8, dv=-1)
            for du, dv in ((-2, -3), (2, -3), (-4, -1), (4, -1), (0, -4), (-3, -2), (3, -2)):
                w(fr, (top[0], 0, dz), 0.6, du, dv)
        elif i in (12, 13, 14):
            r = 3 + (i - 12) * 2
            for du in range(-r, r + 1):
                if abs(du) >= r - 1:
                    w(fr, (top[0], 0, dz), 0.5 - (i - 12) * 0.15, du, 0)
        out.append(_diff(fr, img))
    return out


ANIMS = {'manometres': {'frames': _frames_manometres, 'frameDuration': 140},
         'gota': {'frames': _frames_gota, 'frameDuration': 110}}


# ─── Capes del davant i geometria ────────────────────────────────────────────

def _amo(ids):
    def mask(x, y):
        _, e = _base()
        return e.ids[e.amo[y * e.cv.w + x]] in ids
    return mask


def _p(x, z, y=0.0):
    u, v, _ = CAM.projecta((x, y, z))
    return round(u), round(v)


def _rect_mon(*Ps):
    pts = [CAM.projecta(P) for P in Ps]
    return (max(0, round(min(p[0] for p in pts))), max(0, round(min(p[1] for p in pts))),
            min(W - 1, round(max(p[0] for p in pts))), min(BOTTOM, round(max(p[1] for p in pts))))


def _caixa_mon(x0, x1, y0, y1, z0, z1):
    return _rect_mon(*[(x, y, z) for x in (x0, x1) for y in (y0, y1) for z in (z0, z1)])


def _escala_a(v):
    lo, hi = -200.0, 2000.0
    for _ in range(60):
        z = (lo + hi) / 2
        if CAM.projecta((200, 0, z))[1] > v:
            lo = z
        else:
            hi = z
    return CAM.escala((200, 0, (lo + hi) / 2))


def _z_a_v(x, v):
    lo, hi = -200.0, 2000.0
    for _ in range(50):
        z = (lo + hi) / 2
        if CAM.projecta((x, 0, z))[1] > v:
            lo = z
        else:
            hi = z
    return (lo + hi) / 2


V_PROP = 250
WALK_MON = ([(10, 60), (10, ZW - 12), (_w(285), ZW - 12), (_w(285), ZW - 22), (_w(380), PZ - 26), (XR - 10, PZ - 26)]
            + [(x, _z_a_v(x, V_PROP)) for x in (XR - 10, 340, 280, 200, 120, 60)] + [(10, _z_a_v(10, V_PROP))])
_WALK = [_p(x, z) for x, z in WALK_MON]
_V_FONS, _V_PROP = min(v for _, v in _WALK), max(v for _, v in _WALK)
_PW = (_w(380), _w(640))

# Les bombes: el terra on es camina no passa mai per darrere de cap peça (s'acaba davant les bancades, i a l'esquerra
# de la vermella hi ha l'aspiració, més enrere), així que el personatge hi és sempre davant. (Abans la línia era a
# PZ - 18 de la bomba del mig, i davant de la vermella, on el terra s'acaba més amunt, el personatge hi quedava darrere.)
FRONT = [
    {'id': 'davant', 'mask': _amo({'primer_pla'}), 'baseline': 999, 'zIndex': 20},
    {'id': 'davant_bombes', 'mask': _amo({'bombes'}), 'baseline': _V_FONS - 1, 'zIndex': 20,
     'props': ('llanterna',)},                     # (la llum de la llanterna a la bancada de la bomba vermella)
]

GEOMETRIA = {
    'things': {
        'escotilla': {'rect': _rect_mon((HATCH[0] - 6, HW, HATCH[2]), (HATCH[1] + 6, 0, ZW - 14)),
                      'walk': _p((HATCH[0] + HATCH[1]) / 2, ZW - 34)},
        'llibre': {'rect': _caixa_mon(BOOK_P[0] - 22, BOOK_P[0] + 22, 0, 10, BOOK_P[1] - 16, BOOK_P[1] + 16),
                   'walk': _p(BOOK_P[0] + 10, BOOK_P[1] - 26)},
        'llanterna': {'rect': _caixa_mon(TORCH_P[0] - 18, TORCH_P[0] + 20, 0, 12, TORCH_P[1] - 10, TORCH_P[1] + 10),
                      'walk': _p(TORCH_P[0] - 6, TORCH_P[1] - 26)},
        'bombes': {'rect': _caixa_mon(_w(411) - 40, _w(584) + 48, 0, _y(59) + 6, PZ - 16, PZ + 16),
                   'walk': _p(_w(501), PZ - 40)},
    },
    'spawns': {'iri': _p(220, 140), 'vet': _p(290, 170), 'bastida': _p(80, 200)},
    'walkable': _WALK,
    'floorSquash': 0.42,
    'characterShadow': {'enabled': True, 'color': '#040a08', 'alpha': 0.42, 'squash': 0.42, 'core': 0.6,
                        'light': {'x': _p(*LAMPS[1])[0], 'y': _p(*LAMPS[1])[1], 'stretch': 0.7, 'reach': 150}},
    'regions': [{'id': 'perspectiva', 'active': True, 'scaleEnabled': True, 'scaleWalkSpeed': True,
                 'scaleTop': round(_escala_a(_V_FONS - 2), 3), 'scaleBottom': round(_escala_a(_V_PROP + 2), 3),
                 'points': [(0, _V_FONS - 2), (W - 1, _V_FONS - 2), (W - 1, _V_PROP + 2), (0, _V_PROP + 2)]}],
    'characterLights': {
        'ambient': '#94a49c',
        'lights': [
            {'x': _p(*LAMPS[0], 150)[0], 'y': _p(*LAMPS[0], 150)[1], 'radius': 220, 'color': '#ffd68c', 'intensity': 0.8},
            {'x': _p(*LAMPS[1], 150)[0], 'y': _p(*LAMPS[1], 150)[1], 'radius': 220, 'color': '#ffd68c', 'intensity': 0.8},
            {'x': _p((HATCH[0] + HATCH[1]) / 2, ZW - 20, 150)[0], 'y': _p((HATCH[0] + HATCH[1]) / 2, ZW - 20, 150)[1],
             'radius': 140, 'color': '#c8e6c8', 'intensity': 0.6},
        ],
    },
}
