"""
Cambra de ressonància (Iri). EN 3D (hd640/tres_d.py), a 1×.

Una càmera alta que mira de biaix la cantonada del fons a l'esquerra. Les coses van, d'esquerra a dreta, com al pròleg
(porta, consola, cambra), amb aire entre elles:
  - a la paret de l'esquerra, en escorç i ben endavant, la **porta de ferro** de la sala de calderes, amb el foc a
    l'espiell, i l'avís de reglament;
  - la **consola** de fusta, recta contra la paret del fons, prop de la cantonada, amb el sobre inclinat (el botó, la
    palanca), el llum d'alarma i els rellotges al davant; la campana a la paret, al damunt;
  - al fons, a la dreta de la consola, la **cambra** de vidre gruixut sobre la plataforma de les franges de perill, amb volum (els
    muntants, la caixa de dalt amb els aïlladors i els cables que pugen al sostre);
  - a la paret del fons, la **reixa** del conducte de servei (la sortida pel fons), el rètol de perill, la canonada
    de coure amb la vàlvula i el manòmetre, la pissarra; el pilar de ferro i la galleda de sorra;
  - al mig, a la dreta, unes caixes de recanvis amb una bobina de coure (s'hi passa per darrere);
  - primer pla: un pilar de ferro tallat per la vora dreta i un rotlle de cable i caixes en silueta a l'esquerra.

Tot el detall ve del dibuix pla de sempre (fabrica_cambra_pla_comu.py, per trossos: `bg(cv, parts=...)`),
projectat; l'animació (el camp, els arcs, els llums de senyal, el foc i les agulles) és el mateix dibuix pla a cada
moment, projectat per les mateixes superfícies.

El món: x a la dreta (0 = la paret de la porta), y amunt (0 = el terra), z cap al fons (300 = la paret del fons);
1 unitat = 1 píxel de sala a la distància on un personatge fa ≈110 px (escala 1).
"""
import functools
import math

import hd640  # noqa: F401  (abans de cap hd.rooms: posa la llibreria a 640×360)
import hd.pix as pix
from hd.pix import Light, W, H, hr, WALNUT, IRON, COPPER, RED, WARN, SIL, MANILA, PAPER
from hd.rooms.exterior import fbm
from hd640.rooms import fabrica_cambra_pla_comu as PL
from hd640.rooms.fabrica_cambra_pla_comu import STONE, FE9
from hd.rooms.fabrica_magatzem import WOOD2
from hd640.tres_d import Camera, Escena, Llum

BOTTOM = 259                                       # la sala acaba aquí (a sota, la barra de verbs)
ZW = 300                                           # la paret del fons
FY = PL.FLOOR_Y                                    # el terra, al dibuix pla
TOPY = 13                                          # dalt de la paret al dibuix pla (la biga; a dalt, el sostre)
HW = FY - TOPY                                     # l'alçada de les parets
XL = 124                                           # al dibuix pla, la cantonada: a l'esquerra, la paret de la porta
XR = 760                                           # on s'acaba la paret del fons (fora de la pantalla)
OFF = 70                                           # el dibuix pla de la paret del fons comença aquí (abans, maó)
DZ = 80                                            # la porta, avançada: la paret de la porta acaba DZ abans
DARK = [(4, 3, 5), (9, 7, 10), (15, 12, 15), (22, 18, 21), (31, 25, 28), (42, 34, 36)]


class Canvas(pix.Canvas):
    """El llenç de Ferro-9, a 1× (tres_d en vol saber l'escala)."""
    S = 1


def _w(fx):
    """Una x del dibuix pla de la paret del fons → la x del món."""
    return fx - XL + OFF


def _wz(fx):
    """Una x del dibuix pla de la paret de la porta → la z del món."""
    return ZW - XL - DZ + fx


def _y(fy):
    """Una y del dibuix pla (el terra, a FY) → l'alçada del món."""
    return FY - fy


CONSOLE = (92, 274, 124, 40, 0.0)                # la consola: x, z del centre, ample, fons, gir
CON_H, CON_TOP = 66, 88                            # l'alçada del davant i la del sobre inclinat (al darrere)
CHAMBER = (_w(265), _w(425), 236, 292)             # la plataforma de la cambra: x0, x1, z0, z1
DRUM = (470, 168)                                  # les caixes de recanvis (x, z)
PIPE = (_w(543), ZW - 7)                           # la canonada de coure (x, z)
PILLAR_B = (_w(603), ZW - 10)                      # el pilar del fons
BUCKET = (585, 262)                                # la galleda de sorra
LAMP1 = (CONSOLE[0] + 14, 150, CONSOLE[1] - 6)      # les làmpades (la bombeta)
LAMP2 = (_w(PL.LAMP2[0]), 156, ZW - 40)
CORE = ((CHAMBER[0] + CHAMBER[1]) / 2, 100, 262)   # el centre del camp
GATE = (0, _y(115), _wz(44))                       # l'espiell de la porta (el foc)

CAM = Camera(pos=(470, 200, -290), yaw=-0.36, pitch=0.20, f=450, centre=(320, 88))

LIGHT = Light(ambient=0.0, vignette=None, floor_fade=None)  # (la llum és la del món: la de l'Escena)
LLUMS = [Llum(LAMP1, 260, 2.4, power=1.5),
         Llum(LAMP2, 200, 1.6, power=1.5),
         Llum((CORE[0], CORE[1], CORE[2] - 50), 200, 1.2, power=1.4),
         Llum((8, GATE[1], GATE[2]), 90, 1.0, power=2.0)]

# ─── Les textures: el dibuix pla de sempre ───────────────────────────────────

TEXL = PL.Baked(Light(ambient=0.5, vignette=None, floor_fade=None))   # (llum plana: la de la sala la posa l'Escena)
WALL_PARTS = ('sostre', 'paret', 'porta', 'avis', 'campana', 'reixa', 'perill', 'pissarra')


def _pla(parts, t=0.0, transparent=False, extra=None):
    cv = Canvas(light=TEXL, transparent=transparent)
    PL.bg(cv, t=t, parts=parts)
    if extra:
        extra(cv)
    return cv.img


@functools.lru_cache(maxsize=None)
def _paret(llimada=False):
    """Les dues parets planes, de cara: maó, la porta, l'avís, la campana, la reixa, el rètol i la pissarra."""
    return _pla(WALL_PARTS, extra=PL.reixa_llimada if llimada else None)


@functools.lru_cache(maxsize=None)
def _mao():
    """Només el maó i el sostre (per a la paret de prop i la del fons de més enllà)."""
    return _pla(('sostre', 'paret'))


@functools.lru_cache(maxsize=None)
def _consola(boto=False):
    return _pla(('consola', 'alarma'), transparent=True, extra=PL.boto if boto else None)


@functools.lru_cache(maxsize=None)
def _cambra():
    return _pla(('cambra',), transparent=True)


@functools.lru_cache(maxsize=None)
def _coses():
    """La canonada amb la vàlvula i el manòmetre, les làmpades i la galleda (en surten els sprites)."""
    return _pla(('canonada', 'lampades', 'galleda'), transparent=True)


@functools.lru_cache(maxsize=None)
def _palanca(quina):
    cv = Canvas(light=TEXL, transparent=True)
    {'alcada': PL.palanca_alcada, 'baixada': PL.palanca_baixada}[quina](cv)
    return cv.img


CON_FRONT = (119, 139, 244, 205)                   # la consola, al dibuix pla: el davant
CON_SLOPE = (119, 112, 244, 139)                   # el sobre inclinat (amb el botó i el quadrant de la palanca)
BEACON_BOX = (126, 92, 147, 118)                   # el llum d'alarma
LEVER_BOX = (176, 60, 248, 133)                    # la palanca (alçada o baixada)
GLASS_BOX = (265, 27, 426, 188)                    # la cambra: la caixa de dalt, els muntants i el vidre
VALVE_BOX = (532, 117, 555, 140)                   # el volant de la vàlvula
GAUGE_BOX = (549, 86, 568, 106)                    # el manòmetre
LAMP_BOX = (PL.LAMP1[0] - 16, PL.LAMP1[1] - 12, PL.LAMP1[0] + 17, PL.LAMP1[1] + 6)


# ─── Les superfícies ────────────────────────────────────────────────────────

def _terra(s, t, P):
    """Lloses de pedra de 60 × 46 a trencajunt, en coordenades del món: juntes, esquerdes, gra i brutícia."""
    x, z = P[0], P[2]
    row = math.floor(z / 46)
    u = x / 60 + (0.5 if row % 2 else 0)
    col = math.floor(u)
    fx, fz = (u - col) * 60, z - row * 46
    if fx < 1.2 or fz < 1.2:
        return 1.0
    v = 2.0 + (hr(col, row, 1) - 0.5) * 0.6 + (fbm(x / 30, z / 20, 3) - 0.5) * 0.5
    if fx < 2.4 or fz < 2.4:
        v += 0.3
    if hr(col, row, 4) > 0.75 and abs(fx / 60 - (0.2 + fz / 46 * 0.6)) * 60 < 0.8:
        v = 1.2                                                                  # una esquerda en diagonal
    if fbm(x / 40, z / 30, 8) > 0.7:
        v -= 0.6                                                                 # sutge i oli
    return v


def _ferro(lvl0, seed=1, reblons=None):
    """Planxa de ferro amb gra i, si cal, una filera de reblons cada `reblons` unitats."""
    def L(s, t, P):
        v = lvl0 + (hr(int(s // 3), int(t // 3), seed) - 0.5) * 0.25
        if reblons and s % reblons < 1.6 and int(t) % 13 < 2:
            v += 1.6
        return v
    return L


def _cantons(cx, cz, w, d, ang):
    c, s_ = math.cos(ang), math.sin(ang)
    return [(cx + lx * c - lz * s_, cz + lx * s_ + lz * c) for lx, lz in ((-w / 2, -d / 2), (w / 2, -d / 2),
                                                                          (w / 2, d / 2), (-w / 2, d / 2))]


def _ombra(e, sid, cx, cz, rx, rz, k=0.55, dx=-6, dz=6):
    cx, cz = cx + dx, cz + dz
    e.foscor(sid, (cx - rx, 0.6, cz + rz), (cx + rx, 0.6, cz + rz), (cx + rx, 0.6, cz - rz), (cx - rx, 0.6, cz - rz),
             lambda s, t: k * min(1.0, max(0.0, 1 - ((s - rx) / rx) ** 2 - ((t - rz) / rz) ** 2) * 1.8))


def _con(lx, y, lz):
    """Un punt de la consola (coordenades locals: lx d'esquerra a dreta, lz cap al darrere) al món."""
    cx, cz, _, _, ang = CONSOLE
    c, s_ = math.cos(ang), math.sin(ang)
    return (cx + lx * c - lz * s_, y, cz + lx * s_ + lz * c)


def _lx(fx):
    """Una x del dibuix pla de la consola → la x local de la consola."""
    return fx - (CON_FRONT[0] + CON_FRONT[2]) / 2


PIVOT = _con(_lx(PL.PIVOT[0]), CON_H + 8, 2)       # l'eix de la palanca, al sobre inclinat


def escena(cv, tex, estat=frozenset()):
    """Tota la sala, de lluny a prop. `estat`: els decorats que hi són ('palanca_alcada', 'palanca_baixada').
    → l'Escena (qui ha pintat què)."""
    e = Escena(cv, CAM, LLUMS, ambient=-0.5)
    zn = CAM.pos[2] + 60
    paret, con, cam, coses, mao = tex['paret'], tex['consola'], tex['cambra'], tex['coses'], tex['mao']
    # el sostre: fosc, amb les bigues
    e.quad('sostre', (0, HW, zn), (XR, HW, zn), (XR, HW, ZW), (0, HW, ZW), ramp=IRON, dues_cares=True,
           lvl=lambda s, t, P: 0.5 + (1.4 if P[2] % 80 < 7 else 0) - (0.5 if P[2] % 80 > 76 else 0))
    # la paret de la porta (x = 0): de prop, maó; cap a la cantonada, el dibuix pla (x 0..124)
    z0, z1 = _wz(0), _wz(XL)
    e.quad('paret_esq_prop', (0, HW, zn), (0, HW, z0), (0, 0, z0), (0, 0, zn),
           tex=(mao, (W - (z0 - zn), TOPY, W, FY)))
    e.quad('paret_esq', (0, HW, z0), (0, HW, z1), (0, 0, z1), (0, 0, z0), tex=(paret, (0, TOPY, XL, FY)))
    if DZ:
        e.quad('paret_esq_cantonada', (0, HW, z1), (0, HW, ZW), (0, 0, ZW), (0, 0, z1), tex=(mao, (0, TOPY, DZ, FY)))
    # la paret del fons (z = 300): maó a la cantonada, el dibuix pla (x 124..640) i, a la dreta, més maó
    if OFF:
        e.quad('paret_fons_esq', (0, HW, ZW), (OFF, HW, ZW), (OFF, 0, ZW), (0, 0, ZW), tex=(mao, (W - OFF, TOPY, W, FY)))
    x1 = _w(W)
    e.quad('paret_fons', (OFF, HW, ZW), (x1, HW, ZW), (x1, 0, ZW), (OFF, 0, ZW), tex=(paret, (XL, TOPY, W, FY)))
    e.quad('paret_fons_dreta', (x1, HW, ZW), (XR, HW, ZW), (XR, 0, ZW), (x1, 0, ZW),
           tex=(mao, (0, TOPY, XR - x1, FY)))
    # el terra de lloses
    e.quad('terra', (0, 0, ZW), (XR, 0, ZW), (XR, 0, zn), (0, 0, zn), ramp=STONE, lvl=_terra)
    # la llum: el foc de l'espiell, el camp violeta davant la cambra i els bassals sota les làmpades
    e.claror((0, 0.3, GATE[2] + 70), (90, 0.3, GATE[2] + 70), (90, 0.3, GATE[2] - 70), (0, 0.3, GATE[2] - 70),
             (255, 130, 60), lambda s, t: 0.20 * max(0.0, 1 - math.hypot(s / 90, (t - 70) / 70)) ** 1.2)
    cx0, cx1, cz0, cz1 = CHAMBER
    e.claror((cx0 - 100, 0.3, cz0), (cx1 + 100, 0.3, cz0), (cx1 + 100, 0.3, cz0 - 170), (cx0 - 100, 0.3, cz0 - 170),
             (150, 120, 240), lambda s, t: 0.30 * max(0.0, 1 - math.hypot((s - (cx1 - cx0) / 2 - 100) / 170, t / 150)) ** 1.2)
    for L, k in ((LAMP1, 0.24), (LAMP2, 0.16)):
        e.claror((L[0] - 120, 0.3, L[2] + 90), (L[0] + 120, 0.3, L[2] + 90), (L[0] + 120, 0.3, L[2] - 150),
                 (L[0] - 120, 0.3, L[2] - 150), (255, 200, 130),
                 lambda s, t, k=k: k * max(0.0, 1 - math.hypot((s - 120) / 120, (t - 100) / 120)) ** 1.4)
    # la foscor dels racons
    e.foscor('racons', (0, 0.5, ZW), (XR, 0.5, ZW), (XR, 0.5, zn), (0, 0.5, zn),
             lambda s, t: max(0.55 * max(0.0, 1 - t / 24), 0.45 * max(0.0, 1 - s / 20)))
    e.foscor('cantonada', (0, HW, ZW - 0.5), (70, HW, ZW - 0.5), (70, 0, ZW - 0.5), (0, 0, ZW - 0.5),
             lambda s, t: 0.5 * max(0.0, 1 - s / 70))
    e.foscor('cantonada2', (0.5, HW, ZW - 70), (0.5, HW, ZW), (0.5, 0, ZW), (0.5, 0, ZW - 70),
             lambda s, t: 0.5 * max(0.0, 1 - (70 - s) / 70))
    e.foscor('sostre_fosc', (0, HW - 0.5, ZW - 0.6), (XR, HW - 0.5, ZW - 0.6), (XR, 0, ZW - 0.6), (0, 0, ZW - 0.6),
             lambda s, t: 0.45 * max(0.0, 1 - t / 40))
    e.foscor('sostre_fosc2', (0.6, HW - 0.5, zn), (0.6, HW - 0.5, ZW), (0.6, 0, ZW), (0.6, 0, zn),
             lambda s, t: 0.45 * max(0.0, 1 - t / 40))
    # rovell i escòria a peu de paret
    for k in range(22):
        x, z = 10 + hr(k, 1) * 600, ZW - 3 - hr(k, 2) * 20
        if not (cx0 - 6 < x < cx1 + 6):
            e.caixa('brossa', x, x + 2 + hr(k, 3) * 4, 0, 1.2, z, z + 2 + hr(k, 5) * 3, IRON, 2.6 + hr(k, 4))
    # ── la cambra: la plataforma amb les franges, el graó, la caixa de vidre amb els muntants i la de dalt
    _ombra(e, 'ombra_cambra', (cx0 + cx1) / 2, (cz0 + cz1) / 2, (cx1 - cx0) / 2 + 14, (cz1 - cz0) / 2 + 10, 0.5, dx=-4, dz=-4)

    e.caixa('cambra', cx0, cx1, 0, 17, cz0, cz1, IRON, 2.0,
            cares={'davant': {'ramp': IRON, 'lvl': lambda s, t, P: 2.0 - t * 0.04 + (1.8 if t < 1.2 else 0)
                              - (1.0 if t > 15.5 else 0) + (1.6 if int(s) % 16 == 5 and 13 < t < 15 else 0)},
                   'dalt': {'ramp': IRON, 'lvl': _ferro(2.6, 3)},
                   'dreta': {'ramp': IRON, 'lvl': _ferro(1.4, 4)}, 'esquerra': {'ramp': IRON, 'lvl': _ferro(1.8, 4)}})
    # les franges de perill, grogues i negres, a la cara de davant de la plataforma
    e.quad('cambra', (cx0 + 4, 11, cz0 - 0.4), (cx1 - 4, 11, cz0 - 0.4), (cx1 - 4, 5, cz0 - 0.4), (cx0 + 4, 5, cz0 - 0.4),
           ramp=WARN, lvl=lambda s, t, P: 2.6 - (0.9 if hr(int(s), int(t), 4) > 0.9 else 0),
           forma=lambda s, t: int((s + t) // 7) % 2 == 0)
    e.caixa('cambra', _w(301), _w(389), 0, 7, cz0 - 9, cz0, IRON, 3.0,
            cares={'dalt': {'ramp': IRON, 'lvl': lambda s, t, P: 3.4 - (2.0 if (int(s) + int(t)) % 4 == 0 else 0)}})
    gz0, gz1 = cz0 + 8, cz1 - 6
    e.caixa('cambra', cx0, cx1, 17, 17 + (188 - 27), gz0, gz1, IRON, 2.0,
            cares={'davant': {'tex': (cam, GLASS_BOX)}, 'dalt': {'ramp': IRON, 'lvl': _ferro(2.8, 5, reblons=11)},
                   'dreta': {'ramp': IRON, 'lvl': _ferro(1.2, 6, reblons=13)},
                   'esquerra': {'ramp': IRON, 'lvl': _ferro(1.6, 6, reblons=13)}})
    top = 17 + 161
    for fx in (280, 296, 395, 411):                                               # els aïlladors i els cables al sostre
        x = _w(fx)
        for j in range(3):
            e.caixa('cambra', x - 3.5 + j * 0.5, x + 3.5 - j * 0.5, top + j * 3, top + j * 3 + 2.4, gz0 + 10 - 3, gz0 + 10 + 3,
                    PAPER, 3.4 - j * 0.3)
        e.cable('cambra', [(x, top + 9, gz0 + 10), (x + 2, HW - 20, gz0 + 16), (x + 4, HW, gz0 + 26)], SIL, 1.6, gruix=1.6)
    # els cables de la consola a la cambra, per terra
    for i, (lv, dz) in enumerate(((1.6, 0), (1.2, 6), (1.4, 12))):
        a = _con(CONSOLE[2] / 2 - 4, 20 - i * 5, -8 + dz * 0.5)
        e.cable('cables', [a, (a[0] + 12, 0.8, a[2] - 4 - dz), (cx0 - 26, 0.8, cz0 - 10 - dz), (cx0 + 6, 0.8, cz0 - 2)],
                [(8, 6, 12), (22, 16, 24), (40, 34, 40), (70, 62, 66)], lv, gruix=2.4)
    # ── la consola, girada: el davant (rellotges), el sobre inclinat, el llum d'alarma
    ccx, ccz, cw, cd, ca = CONSOLE
    _ombra(e, 'ombra_consola', ccx, ccz, cw * 0.62, cd * 1.1, 0.55, dx=-6, dz=8)
    e.caixa_girada('consola', ccx, ccz, cw, cd, CON_H, ca, WALNUT, 2.0,
                   cares={'davant': {'tex': (con, CON_FRONT)},
                          'dalt': {'ramp': WALNUT, 'lvl': 2.6},
                          'esquerra': {'ramp': WALNUT, 'lvl': lambda s, t, P: 1.8 + (0.25 if int(s + math.sin(t / 9) * 2) % 7 == 0 else 0)},
                          'dreta': {'ramp': WALNUT, 'lvl': lambda s, t, P: 1.2 + (0.25 if int(s + math.sin(t / 9) * 2) % 7 == 0 else 0)}})
    bz = cd / 2 - 6                                                               # el muntant del darrere del sobre
    e.caixa_girada('consola', *_con(0, 0, bz + 3)[::2], cw, 6, CON_TOP - CON_H, ca, WALNUT, 2.2, y0=CON_H,
                   cares={'dalt': {'ramp': WALNUT, 'lvl': 3.4}})
    hw = cw / 2
    e.quad('consola', _con(-hw, CON_TOP, bz), _con(hw, CON_TOP, bz), _con(hw, CON_H, -cd / 2), _con(-hw, CON_H, -cd / 2),
           tex=(con, CON_SLOPE))
    for side, lv in ((-hw, 2.0), (hw, 1.2)):                                       # els costats del sobre (triangles)
        L = bz + cd / 2
        e.quad('consola', _con(side, CON_TOP, -cd / 2), _con(side, CON_TOP, bz), _con(side, CON_H, bz), _con(side, CON_H, -cd / 2),
               ramp=WALNUT, lvl=lv, dues_cares=True, forma=lambda s, t, L=L: t >= (CON_TOP - CON_H) * (1 - s / L))
    e.sprite('consola', con.crop(BEACON_BOX), (PL.BEACON[0] - BEACON_BOX[0], 117 - BEACON_BOX[1]), _con(_lx(136), CON_TOP, bz + 1))
    for q in ('alcada', 'baixada'):
        if f'palanca_{q}' in estat:
            img = _palanca(q)
            e.sprite('palanca', img.crop(LEVER_BOX), (PL.PIVOT[0] - LEVER_BOX[0], PL.PIVOT[1] - LEVER_BOX[1]), PIVOT)
    # la canonada de coure, amb la vàlvula i el manòmetre
    px_, pz_ = PIPE
    e.tub('canonada', (px_, 0, pz_), (px_, HW, pz_), 4.5, COPPER, 2.4, llum_dir=(-0.8, 0.2))
    e.sprite('canonada', coses.crop(VALVE_BOX), (543 - VALVE_BOX[0], 128 - VALVE_BOX[1]), (px_, _y(128), pz_ - 6))
    e.cable('canonada', [(px_ + 4, _y(96.5), pz_ - 1), (px_ + 12, _y(96.5), pz_ - 1)], COPPER, 3.0, gruix=2.0)
    e.sprite('canonada', coses.crop(GAUGE_BOX), (559 - GAUGE_BOX[0], 96 - GAUGE_BOX[1]), (px_ + 16, _y(96), pz_ - 1))
    # el pilar del fons i la galleda de sorra
    e.tub('pilar', (PILLAR_B[0], 0, PILLAR_B[1]), (PILLAR_B[0], HW, PILLAR_B[1]), 7, IRON, 2.2, llum_dir=(-0.8, 0.3))
    e.caixa('pilar', PILLAR_B[0] - 10, PILLAR_B[0] + 10, 0, 16, PILLAR_B[1] - 10, PILLAR_B[1] + 8, IRON, 2.4,
            cares={'dalt': {'ramp': IRON, 'lvl': 3.6}})
    bx, bz_ = BUCKET
    _ombra(e, 'ombra_galleda', bx, bz_, 16, 12, 0.6, dx=-4, dz=0)
    for y0 in range(0, 28, 2):
        e.tub('galleda', (bx, y0, bz_), (bx, y0 + 2, bz_), 9 - y0 * 0.06, RED, 1.6 if y0 in (8, 20) else 2.6,
              llum_dir=(-0.8, 0.2))
    e.quad('galleda', (bx - 9, 28.3, bz_ + 9), (bx + 9, 28.3, bz_ + 9), (bx + 9, 28.3, bz_ - 9), (bx - 9, 28.3, bz_ - 9),
           ramp=MANILA, forma=lambda s, t: (s - 9) ** 2 + (t - 9) ** 2 < 70,
           lvl=lambda s, t, P: 2.4 + (hr(int(s), int(t), 7) - 0.5) * 0.8 - (1.2 if (s - 9) ** 2 + (t - 9) ** 2 > 52 else 0))
    # les làmpades industrials que pengen
    for L in (LAMP1, LAMP2):
        e.cable('lampades', [(L[0], HW, L[2]), (L[0], L[1] + 12, L[2])], SIL, 1.2, gruix=1.0)
        e.sprite('lampades', coses.crop(LAMP_BOX), (PL.LAMP1[0] - LAMP_BOX[0], PL.LAMP1[1] + 3 - LAMP_BOX[1]), L)
    # les caixes de recanvis, al mig a la dreta: bobines de coure noves i una de ferro-9 al damunt
    dx_, dz_ = DRUM
    _ombra(e, 'ombra_caixes', dx_, dz_, 40, 30, 0.6, dx=-8, dz=6)

    def cara(lab):
        def L(s, t, P):
            v = 2.8 - (1.4 if int(t) % 9 == 8 else 0) + (hr(int(s // 3), int(t // 9), 5) - 0.5) * 0.4
            if lab and 6 < s < 30 and 8 < t < 16:
                return 0.6 if (int(s) % 6 < 4 and 10 < t < 14) else 3.6                 # l'etiqueta, amb el número
            return v
        return L
    for cx, cz, w, d, h, a, y0, lab in ((dx_, dz_, 44, 34, 30, -0.5, 0, True), (dx_ + 2, dz_ + 1, 32, 26, 22, -0.3, 30, False),
                                        (dx_ + 40, dz_ + 16, 30, 26, 24, -0.1, 0, False)):
        e.caixa_girada('caixes', cx, cz, w, d, h, a, WOOD2, 2.0, y0=y0,
                       cares={'dalt': {'ramp': WOOD2, 'lvl': lambda s, t, P: 3.4 - (1.2 if int(s) % 9 == 0 else 0)},
                              'davant': {'ramp': WOOD2, 'lvl': cara(lab)},
                              'dreta': {'ramp': WOOD2, 'lvl': lambda s, t, P: 1.8 - (0.8 if int(t) % 9 == 8 else 0)},
                              'esquerra': {'ramp': WOOD2, 'lvl': 2.4}})
    for y, lv in ((52.3, 1.6), (54.3, 2.4), (56.3, 3.2)):                          # un rotlle de fil de coure, ajagut
        e.quad('caixes', (dx_ - 8, y, dz_ + 11), (dx_ + 12, y, dz_ + 11), (dx_ + 12, y, dz_ - 9), (dx_ - 8, y, dz_ - 9),
               ramp=COPPER, forma=lambda s, t: 16 < (s - 10) ** 2 + (t - 10) ** 2 < 90,
               lvl=lambda s, t, P, lv=lv: lv + (0.9 if int(math.atan2(t - 10, s - 10) * 9) % 2 else 0))
    e.cable('caixes', [(dx_ - 10, 8, dz_ - 18), (dx_ - 30, 1, dz_ - 32), (dx_ - 70, 0.8, dz_ - 22),
                       (dx_ - 110, 0.8, dz_ - 40)], SIL, 1.8, gruix=3.0)
    # primer pla: un pilar de ferro a la dreta, un rotlle de cable i caixes en silueta a l'esquerra
    for cx, cz, w, d, h, a, y0 in ((-6, 30, 74, 56, 46, 0.25, 0), (70, -4, 52, 40, 26, -0.2, 0)):
        e.caixa_girada('primer_pla', cx, cz, w, d, h, a, DARK, 1.6, y0=y0,
                       cares={'dalt': {'ramp': DARK, 'lvl': lambda s, t, P: 3.0 - (1.2 if int(s) % 12 == 0 else 0)},
                              'davant': {'ramp': DARK, 'lvl': lambda s, t, P: 1.2 + (0.6 if int(t) % 10 == 0 else 0)},
                              'dreta': {'ramp': DARK, 'lvl': 2.0}})
    e.roca('primer_pla', (120, 0, -60), 32, DARK, lvl=2.2, llum_dir=(-0.7, -0.6), aplana=0.45, seed=9)   # el rotlle
    e.tub('primer_pla', (640, 0, 40), (640, HW, 40), 10, DARK, 2.0, llum_dir=(-0.8, 0.3))
    return e


# ─── Composició i llum ──────────────────────────────────────────────────────

def _proj(P):
    u, v, _ = CAM.projecta(P)
    return u, v


@functools.lru_cache(maxsize=None)
def _textures():
    return {'paret': _paret(), 'consola': _consola(), 'cambra': _cambra(), 'coses': _coses(), 'mao': _mao()}


def _fx(cv):
    """Les lluïssors (les làmpades, el camp de la cambra, el foc de l'espiell), damunt de l'escena."""
    for L, k in ((LAMP1, 0.5), (LAMP2, 0.45)):
        u, v = _proj((L[0], L[1] - 4, L[2]))
        cv.glow(u, v + 2, 40, (255, 220, 150), k)
    u, v = _proj(CORE)
    cv.glow(u, v, 70, (150, 110, 240), 0.32)
    u2, v2 = _proj((CORE[0], 6, CHAMBER[2] - 20))
    cv.glow(u2, v2, 70, (150, 120, 240), 0.12)
    gu, gv = _proj(GATE)
    cv.glow(gu, gv, 26, (255, 150, 70), 0.3)
    lu, lv = _proj(LAMP1)
    cv.tint(0, 0, W - 1, BOTTOM, (255, 200, 130),
            lambda x, y: 0.10 * max(0.0, 1 - math.hypot(x - lu, (y - lv) * 1.1) / 160))


def _render(estat=frozenset(), tex=None):
    cv = Canvas(light=LIGHT)
    e = escena(cv, tex or _textures(), estat)
    pre = cv.img.copy()
    _fx(cv)
    cv.rect(0, BOTTOM + 1, W - 1, H - 1, [(0, 0, 0)], 0, lit=0)    # la barra de verbs: negre
    return cv.img, e, pre


@functools.lru_cache(maxsize=None)
def _base():
    return _render()


def bg(cv):
    cv.img.paste(_base()[0])
    cv.P = cv.img.load()


def _diff(img, base):
    """Els píxels d'`img` que no són iguals a `base` (la resta, transparent)."""
    from PIL import Image, ImageChops
    d = ImageChops.difference(base.convert('RGB'), img.convert('RGB')).convert('L').point(lambda v: 255 if v else 0)
    out = Image.new('RGBA', img.size, (0, 0, 0, 0))
    out.paste(img, (0, 0), d)
    return out


def _decorat(*estat, tex=None):
    """Un decorat: la sala amb aquell estat (o amb unes altres textures), menys la de sempre."""
    def draw(cv):
        img = _render(frozenset(estat), tex() if tex else None)[0]
        cv.img.alpha_composite(_diff(img, _base()[0]))
        cv.P = cv.img.load()
    return draw


# ─── La finestra de fase: el vidre que baixa i el que hi ha a dins ───────────
#
# El vidre de davant de la cambra és un vidre de guillotina: quan l'Iri arma el camp, baixa de dalt de tot fins a la
# plataforma (l'animació `vidre_baixa`, a la línia de l'accident) i s'hi queda (el decorat `vidre_baixat`, mentre el
# camp és armat per ella). A dins, damunt la plataforma, el que hi ha posat (`clau_cambra`: la clau anglesa).

_GZ0 = CHAMBER[2] + 8                               # la cara de davant de la caixa de vidre (z)
_GY0, _GY1 = 17, 17 + (188 - 27)                    # de la plataforma a la caixa de dalt (y)


def _quad_pantalla(x0, x1, y0, y1, z):
    return [tuple(round(c) for c in CAM.projecta(P)[:2]) for P in ((x0, y1, z), (x1, y1, z), (x1, y0, z), (x0, y0, z))]


def _vidre(cv, frac=1.0, flash=0.0):
    """El vidre de guillotina, baixat fins a `frac` (0: tot amunt, amagat a la caixa de dalt; 1: a baix de tot).
    `flash`: la llum del camp que s'encén en tancar-se."""
    from PIL import Image, ImageDraw
    if frac <= 0:
        return
    cx0, cx1 = CHAMBER[0] + 3, CHAMBER[1] - 3
    yb = _GY1 - (_GY1 - _GY0) * frac                # la vora de baix del vidre
    capa = Image.new('RGBA', cv.img.size, (0, 0, 0, 0))
    d = ImageDraw.Draw(capa)
    d.polygon(_quad_pantalla(cx0, cx1, yb, _GY1, _GZ0 - 1), fill=(170, 205, 255, 70 + round(90 * flash)))
    for k in range(4):                              # reflexos en diagonal
        a = cx0 + (cx1 - cx0) * (0.12 + 0.24 * k)
        y_a, y_b = _GY1 - 6, max(yb + 4, _GY1 - 6 - 70)
        if y_b >= y_a:
            continue
        p0 = CAM.projecta((a, y_a, _GZ0 - 1.5))[:2]
        p1 = CAM.projecta((a + 26, y_b, _GZ0 - 1.5))[:2]
        d.line([tuple(map(round, p0)), tuple(map(round, p1))], fill=(235, 245, 255, 110), width=2 if k % 2 else 1)
    # el travesser de baix del vidre (acer), que és el que es veu baixar
    d.polygon(_quad_pantalla(cx0 - 2, cx1 + 2, yb, yb + 5, _GZ0 - 2), fill=(62, 68, 84, 255))
    d.line([tuple(map(round, CAM.projecta((cx0 - 2, yb + 5, _GZ0 - 2))[:2])),
            tuple(map(round, CAM.projecta((cx1 + 2, yb + 5, _GZ0 - 2))[:2]))], fill=(150, 160, 182, 255), width=1)
    cv.img.alpha_composite(capa)
    if flash:
        u, v = _proj(CORE)
        cv.glow(u, v, 90, (200, 170, 255), 0.5 * flash)
    cv.P = cv.img.load()


def _clau_dins(cv):
    """La clau anglesa, estirada damunt la plataforma de la cambra (la icona de l'inventari, a mida de sala)."""
    from PIL import Image
    from hd640 import items as IT
    ic = IT.render('clau_anglesa')
    k = CAM.escala(((CHAMBER[0] + CHAMBER[1]) / 2, _GY0, (_GZ0 + CHAMBER[3]) / 2)) * 0.7
    ic = ic.resize((max(1, round(ic.width * k)), max(1, round(ic.height * k))), Image.NEAREST)
    u, v, _ = CAM.projecta(((CHAMBER[0] + CHAMBER[1]) / 2, _GY0, (_GZ0 + CHAMBER[3]) / 2))
    cv.img.alpha_composite(ic, (round(u - ic.width / 2), round(v - ic.height + 2)))
    cv.P = cv.img.load()


def _buit():
    from PIL import Image
    return [Image.new('RGBA', (W, H), (0, 0, 0, 0))]


def _frames_vidre_baixa(n=8):
    """El vidre que baixa de cop (s'accelera), un cop sec a baix i la llum del camp que s'hi encén."""
    from PIL import Image
    out = []
    for i in range(1, n + 1):
        cv = Canvas(light=LIGHT, img=Image.new('RGBA', (W, H), (0, 0, 0, 0)))
        _vidre(cv, (i / n) ** 1.6)
        out.append(cv.img)
    for f in (1.0, 0.6, 0.3, 0.0):
        cv = Canvas(light=LIGHT, img=Image.new('RGBA', (W, H), (0, 0, 0, 0)))
        _vidre(cv, 1.0, flash=f)
        out.append(cv.img)
    return out


PROPS = {
    'vidre_baixat': _vidre,
    'clau_cambra': _clau_dins,
    'boto': _decorat(tex=lambda: {**_textures(), 'consola': _consola(boto=True)}),
    'reixa_llimada': _decorat(tex=lambda: {**_textures(), 'paret': _paret(llimada=True)}),
    'palanca_alcada': _decorat('palanca_alcada'),
    'palanca_baixada': _decorat('palanca_baixada'),
}


# ─── Animació: el camp, els arcs, els llums de senyal, el foc i les agulles ───

def _frames(n=24):
    """El dibuix pla a cada moment del cicle, projectat per les mateixes superfícies, menys el fons."""
    base, e, pre = _base()
    out = []
    for i in range(n):
        t = i / n
        img = pre.copy()
        if i:                                    # (només el que canvia al dibuix pla: la resta conserva les ombres)
            img.alpha_composite(e.capa(PL.frame_diff(_paret(), _pla(WALL_PARTS, t)), {'paret_esq', 'paret_fons'}))
            img.alpha_composite(e.capa(PL.frame_diff(_consola(), _pla(('consola', 'alarma'), t, transparent=True)),
                                       {'consola'}))
            img.alpha_composite(e.capa(PL.frame_diff(_cambra(), _pla(('cambra',), t, transparent=True)), {'cambra'}))
        cv = Canvas(light=LIGHT, img=img)
        _fx(cv)
        cv.rect(0, BOTTOM + 1, W - 1, H - 1, [(0, 0, 0)], 0, lit=0)
        out.append(_diff(cv.img, base))
    return out


ANIMS = {
    'ambient': {'frames': _frames, 'frameDuration': 120},
    # la finestra de fase (vegeu `_vidre`): un prop buit, i l'animació que s'hi posa a la línia de l'accident
    'fase_cambra': {'frames': _buit, 'frameDuration': 1000, 'loop': False, 'zIndex': 4},
    'vidre_baixa': {'frames': _frames_vidre_baixa, 'frameDuration': 70, 'loop': False, 'prop': 'fase_cambra'},
}


def _amo(ids):
    def mask(x, y):
        e = _base()[1]
        return e.ids[e.amo[y * e.cv.w + x]] in ids
    return mask


def _p(x, z, y=0.0):
    u, v, _ = CAM.projecta((x, y, z))
    return round(u), round(v)


def _base_de(cx, cz, w, d, ang):
    return max(_p(x, z)[1] for x, z in _cantons(cx, cz, w, d, ang))


def _llesques(ids, cx, cz, w, d, ang, n, props=None):
    """Les capes del davant d'un moble girat: la vora de davant i la de darrere fan diagonal a la pantalla, i una
    sola línia base no deixaria passar per davant d'una punta i per darrere de l'altra. Es talla en `n` franges
    verticals de pantalla, cadascuna amb la seva línia base (entre la vora de darrere i la de davant del terra que
    l'envolta, en aquella franja). `props`: {id del decorat: la x de pantalla on és} (va a la franja que toca)."""
    c, s_ = math.cos(ang), math.sin(ang)

    def vora(lz):
        return [_p(cx + lx * c - lz * s_, cz + lx * s_ + lz * c) for lx in [-(w / 2) + w * k / 60 for k in range(61)]]
    davant, darrere = vora(-d / 2), vora(d / 2)
    us = [u for u, _ in davant + darrere]
    u0, u1 = min(us), max(us)
    talls = [u0 + (u1 - u0) * k / n for k in range(n + 1)]
    talls[0], talls[-1] = -1, W + 1
    out = []
    for k in range(n):
        a, b = talls[k], talls[k + 1]
        dv = [v for u, v in davant if a <= u < b] or [max(v for _, v in davant)]
        bv = [v for u, v in darrere if a <= u < b] or [min(v for _, v in darrere)]
        lay = {'id': f'davant_{ids[0]}_{k + 1}', 'baseline': round((min(dv) + max(bv)) / 2), 'zIndex': 20,
               'mask': (lambda a, b: lambda x, y: a <= x < b and _amo(set(ids))(x, y))(a, b)}
        ps = tuple(p for p, u in (props or {}).items() if a <= u < b)
        if ps:
            lay['props'] = ps
        out.append(lay)
    return out


_U_PALANCA = round(CAM.projecta(PIVOT)[0])
_U_BOTO = round(CAM.projecta(_con(_lx(170), CON_TOP - 6, -6))[0])

# Capes del davant: el primer pla (sempre davant), la consola (amb la palanca i el botó) i les caixes de recanvis,
# aquestes dues en franges.
FRONT = [{'id': 'davant', 'mask': _amo({'primer_pla'}), 'baseline': 999, 'zIndex': 20}] \
    + _llesques(('consola', 'palanca'), *CONSOLE[:2], CONSOLE[2] + 12, CONSOLE[3] + 12, CONSOLE[4], 3,
                props={'boto': _U_BOTO, 'palanca_alcada': _U_PALANCA, 'palanca_baixada': _U_PALANCA}) \
    + _llesques(('caixes',), DRUM[0] + 14, DRUM[1] + 6, 82, 56, -0.3, 3)


# ─── Geometria (coordenades de sala, projectades) ────────────────────────────

def _rect_mon(*Ps):
    pts = [CAM.projecta(P) for P in Ps]
    return (max(0, round(min(p[0] for p in pts))), max(0, round(min(p[1] for p in pts))),
            min(W - 1, round(max(p[0] for p in pts))), min(BOTTOM, round(max(p[1] for p in pts))))


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


# El terra on es camina (al món): de la porta a la galleda, davant la consola i la plataforma i fins a la reixa.
WALK_MON = [(14, 96), (14, 236), (CHAMBER[0] - 6, 236), (CHAMBER[0] - 6, 222), (CHAMBER[1] + 4, 222),
            (CHAMBER[1] + 4, 286), (BUCKET[0] - 20, 286), (BUCKET[0] - 20, 240), (BUCKET[0] + 20, 215),
            (BUCKET[0] + 20, 110), (480, 62), (320, 4), (200, -36), (130, -30), (100, 30), (50, 80)]
_WALK = [_p(x, z) for x, z in WALK_MON]
_V_FONS, _V_PROP = min(v for _, v in _WALK), max(v for _, v in _WALK)
_FORAT_CONSOLA = [_p(x, z) for x, z in _cantons(*CONSOLE[:2], CONSOLE[2] + 12, CONSOLE[3] + 12, CONSOLE[4])]
_FORAT_CAIXES = [_p(x, z) for x, z in _cantons(DRUM[0] + 14, DRUM[1] + 6, 82, 56, -0.3)]

_DOOR = (_wz(8), _wz(79), _y(204), _y(81))
_GRILLE = (_w(PL.GRILLE[0]), _w(PL.GRILLE[2]), _y(PL.GRILLE[3]), _y(PL.GRILLE[1]))
_BOTO = (_lx(152), _lx(187))
_cx0, _cx1, _cz0, _cz1 = CHAMBER

GEOMETRIA = {
    'things': {
        'porta': {'rect': _rect_mon((0, _DOOR[3], _DOOR[0]), (0, _DOOR[2], _DOOR[1])), 'walk': _p(26, _DOOR[0] + 30)},
        'palanca': {'rect': _rect_mon(*[(PIVOT[0] + dx, PIVOT[1] + dy, PIVOT[2] + dz) for dx in (-14, 14)
                                        for dy in (-4, 44) for dz in (-6, 6)]),
                    'walk': _p(*_con(_lx(222), 0, -CONSOLE[3] / 2 - 34)[::2])},
        'cambra': {'rect': _rect_mon((_cx0, 17 + 161 + 12, _cz0 + 8), (_cx1, 0, _cz0 - 9), (_cx1, 17 + 161, _cz1)),
                   'walk': _p((_cx0 + _cx1) / 2, _cz0 - 30)},
        'boto': {'rect': _rect_mon(_con(_BOTO[0], CON_TOP + 4, 0), _con(_BOTO[1], CON_H - 2, -CONSOLE[3] / 2),
                                   _con(_BOTO[0], CON_H - 2, -CONSOLE[3] / 2), _con(_BOTO[1], CON_TOP + 4, 0)),
                 'walk': _p(*_con(_lx(170), 0, -CONSOLE[3] / 2 - 34)[::2])},
        'reixa': {'rect': _rect_mon((_GRILLE[0], _GRILLE[3], ZW), (_GRILLE[1], _GRILLE[2], ZW)),
                  'walk': _p((_GRILLE[0] + _GRILLE[1]) / 2, ZW - 24)},
    },
    'spawns': {'iri': _p(330, 170)},
    'walkable': _WALK,
    'forats': [_FORAT_CONSOLA, _FORAT_CAIXES],
    'floorSquash': 0.42,                           # (la càmera, picada: el terra es veu aixafat)
    # L'ombra de contacte: la llum dominant és la làmpada de damunt la consola.
    'characterShadow': {'enabled': True, 'color': '#0c0810', 'alpha': 0.45, 'squash': 0.4, 'core': 0.6,
                        'light': {'x': _p(LAMP1[0], LAMP1[2])[0], 'y': _p(LAMP1[0], LAMP1[2])[1], 'stretch': 0.7,
                                  'reach': 170}},
    'regions': [{'id': 'perspectiva', 'active': True, 'scaleEnabled': True, 'scaleWalkSpeed': True,
                 'scaleTop': round(_escala_a(_V_FONS - 2), 3), 'scaleBottom': round(_escala_a(_V_PROP + 2), 3),
                 'points': [(0, _V_FONS - 2), (W - 1, _V_FONS - 2), (W - 1, _V_PROP + 2), (0, _V_PROP + 2)]}],
    # la llum de la sala sobre els personatges, en temps d'execució
    'characterLights': {
        'ambient': '#7c7084',
        'lights': [
            {'x': _p(LAMP1[0], LAMP1[2], LAMP1[1])[0], 'y': _p(LAMP1[0], LAMP1[2], LAMP1[1])[1], 'radius': 230,
             'color': '#ffd396', 'intensity': 0.9},                                     # la làmpada de la consola
            {'x': _p(LAMP2[0], LAMP2[2], LAMP2[1])[0], 'y': _p(LAMP2[0], LAMP2[2], LAMP2[1])[1], 'radius': 180,
             'color': '#ffd396', 'intensity': 0.6},                                     # la de la pissarra
            {'x': _p(CORE[0], CORE[2], CORE[1])[0], 'y': _p(CORE[0], CORE[2], CORE[1])[1], 'radius': 220,
             'color': '#9a78f0', 'intensity': 0.9},                                     # el camp de la cambra
        ],
    },
}
