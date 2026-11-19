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
    # les bombes: les bancades en 3D, la bomba (el dibuix pla) dreta damunt i la sortida que puja i torna a la paret
    for cx, body, tag in PUMPS:
        x = _w(cx)
        _foscor_el(e, 'ombra_bombes', x - 4, PZ - 2, 44, 22, 0.55)
        e.foscor('ombra_bombes', (x - 70, 0.6, PZ + 4), (x + 10, 0.6, PZ + 4), (x - 10, 0.6, PZ - 50),
                 (x - 90, 0.6, PZ - 50), lambda s, t: 0.3 * max(0.0, 1 - abs(t - 27) / 27) * max(0.0, 1 - abs(s - 40) / 40))
        e.caixa('bombes', x - 33, x + 33, 0, 12, PZ - 16, PZ + 16, CAB, 2.8,
                cares={'dalt': {'ramp': CAB, 'lvl': lambda s, t, P: 3.4 + (1.2 if (abs(s - 5) < 1.2 or abs(s - 61) < 1.2) and abs(t - 16) < 8 and int(t) % 8 < 2 else 0)},
                       'davant': {'ramp': CAB, 'lvl': lambda s, t, P: 2.6 + (1.0 if t < 1.2 else 0)}})
        bx = _pump_box(cx)
        e.sprite('bombes', bom.crop(bx), (cx - bx[0], PL.FLOOR_Y + 3 - 11 - bx[1]), (x, 12, PZ))
        ox = x + 40
        e.tub('bombes', (ox, _y(PL.FLOOR_Y + 3 - 27), PZ), (ox, _y(59), PZ), 5, body, 2.8, brides=46)
        e.tub('bombes', (ox, _y(59), PZ), (ox, _y(59), ZW - 2), 5, body, 3.0)
        e.caixa('bombes', ox - 6, ox + 6, _y(134), _y(122), PZ - 6, PZ + 6, body, 3.0)
        e.tub('bombes', (x + 19, _y(PL.FLOOR_Y + 3 - 27), PZ), (ox, _y(PL.FLOOR_Y + 3 - 27), PZ), 5, body, 3.0)
        e.cable('bombes', [(x + 23, _y(PL.FLOOR_Y + 3 - 114), PZ - 2), (x + 23, HW - 30, PZ + 6), (x + 23, HW - 4, ZW - 6)],
                CAB, 2.4, gruix=1.6)
    # el llibre i la llanterna (els props)
    if 'llibre' in estat:
        _llibre(e)
    if 'llanterna' in estat:
        _llanterna(e)
    _primer_pla(e)
    return e


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
    return {'paret': _paret_base(), 'llisa': _llisa(), 'bombes': _bombes()}


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


FRONT = [
    {'id': 'davant', 'mask': _amo({'primer_pla'}), 'baseline': 999, 'zIndex': 20},
    {'id': 'davant_bombes', 'mask': _amo({'bombes'}), 'baseline': _p(_w(501), PZ - 18)[1], 'zIndex': 20,
     'props': ('llanterna',)},                     # (la llum de la llanterna a la bancada de la bomba vermella)
]

V_PROP = 250
WALK_MON = ([(10, 60), (10, ZW - 12), (_w(285), ZW - 12), (_w(285), ZW - 22), (_w(380), PZ - 26), (XR - 10, PZ - 26)]
            + [(x, _z_a_v(x, V_PROP)) for x in (XR - 10, 340, 280, 200, 120, 60)] + [(10, _z_a_v(10, V_PROP))])
_WALK = [_p(x, z) for x, z in WALK_MON]
_V_FONS, _V_PROP = min(v for _, v in _WALK), max(v for _, v in _WALK)
_PW = (_w(380), _w(640))

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
