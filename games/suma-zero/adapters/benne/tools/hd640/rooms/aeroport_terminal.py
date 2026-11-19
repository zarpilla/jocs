"""
La terminal de l'aeroport (Escena 3, la Vet, dimarts de matinada). EN 3D (hd640/tres_d.py), a 1×.

Una càmera alta que mira de biaix la cantonada del fons a l'esquerra (com a l'estudi i a la cuina):
  - a la paret de l'esquerra, en escorç, la **porta de personal** que vigila en Soler, el panell de sortides i el
    rètol «FACTURACIÓ»; davant, separat de la paret (els empleats hi passen per darrere), el **taulell de
    facturació** amb volum (la tapa, el frontal blau amb el logotip i el pòsit, els monitors) i el pal de la cua;
  - a la paret del fons, la **vidriera** gran (fora, l'alba sobre la pista, la cua de l'avió i l'Ortega fumant a la
    zona de fumadors), amb la **fila de seients** al davant, una mica girada; la garita d'**objectes perduts** (el
    rètol i el taulell groc que sobresurten: l'empleat hi és darrere), la planta i la **màquina de cafè**;
  - la **taula alta** de la cafeteria, rodona i separada (les ulleres a sobre): s'hi passa per darrere;
  - el terra de rajola polida, en coordenades del món, amb el reflex rosat de l'alba i el dels fluorescents;
  - primer pla: un pilar de formigó i un carro de maletes, en silueta.

El detall ve del dibuix pla de sempre (aeroport_terminal_pla_comu.py), projectat; els decorats (les ulleres, el
maletí, la cigarreta que s'escurça) i les animacions (el fum, el panell, la màquina de cafè) també. Damunt, una passada
de llum de Suma Zero (hd640/llum.py): els fluorescents freds, l'alba i la màquina de cafè.

El món: x a la dreta (0 = la paret de la porta de personal), y amunt (0 = el terra), z cap al fons (300 = la
vidriera); 1 unitat = 1 píxel de sala a la distància on un personatge fa ≈111 px (escala 1).
"""
import functools
import math

import hd640  # noqa: F401  (abans de cap hd.rooms: posa la llibreria a 640×360)
from hd640 import llum
from hd.pix import Canvas, Light, W, H, hr
from hd.rooms.comu import _diff, SHEET
from hd640.rooms import aeroport_terminal_pla_comu as PL
from hd640.rooms.aeroport_terminal_pla_comu import (CONC, TILE, DESK, BLUE, YELS, CHROME, VEND, SLATE,
                                                    BOARD_BOX, CAFE)
from hd640.tres_d import Camera, Escena, Llum

BOTTOM = 259                                       # la sala acaba aquí (a sota, la barra de verbs)
ZW = 300                                           # la paret del fons (la vidriera)
HW = 200                                           # l'alçada del dibuix pla de les parets (fins al terra)
XL = 215                                           # al dibuix pla, fins aquí és la paret de l'esquerra
XR = 1100                                          # on s'acaba la paret del fons per la dreta (fora de la pantalla)
ROOM_W = 960                                       # més ampla que la pantalla: la càmera la recorre
PARALLAX = 1.25                                    # el primer pla es mou un 25% més de pressa que la sala
SIGN_BOX = (10, 10, 190, 30)                       # (al dibuix pla de l'atrezzo) el rètol de les portes
AD_BOX = (10, 40, 130, 140)                        #   el panell publicitari
PHONE_BOX = (10, 150, 96, 200)                     #   els telèfons
WIN2 = (470, 720, 30, 160)                         # la segona vidriera, a la paret del fons: x0, x1, y0, y1
SEATS2 = (600, 270, -0.06)                         # la segona fila de seients: x, z del centre, gir
SIGN = (590, 166, 220)                             # el rètol penjat: x del centre, y de baix, z
AD_Z = (-50, 20)                                   # el panell, a la paret de l'esquerra: z0, z1
PHONE_Z = -130                                     # els telèfons, a la paret de l'esquerra: z del primer
DAWN_T = [(10, 12, 18), (18, 20, 30), (30, 28, 50), (60, 54, 104), (100, 76, 120), (150, 100, 126), (200, 130, 120),
          (236, 170, 120), (252, 210, 150)]          # la pista (fosca) i el cel de l'alba
DESK3 = (46, 72, 124, 250, 61)                     # el taulell de facturació: x0, x1, z0, z1, alt
SEATS = (150, 272, 0.12)                           # la fila de seients: x, z del centre, gir
TAULA = (372, 196, 26, 66)                         # la taula alta: x, z, radi, alçada
POST = (104, 110)                                  # el pal de la cua (x, z)


def _y(fy):
    """Una y del dibuix pla (el terra, a 200) → l'alçada del món."""
    return HW - fy


def _wz(fx):
    """Una x del dibuix pla de la paret de l'esquerra → la z del món."""
    return ZW - XL + fx


def _wx(fx):
    """Una x del dibuix pla de la paret del fons → la x del món."""
    return fx - XL


WIN = (_wx(227), _wx(413), _y(149), _y(35))        # la vidriera: x0, x1, y0, y1
STAFF = (_wz(8), _wz(38), 0, _y(50))               # la porta de personal: z0, z1, y0, y1
GARITA = (_wx(440), _wx(568), 30)                  # la garita: x0, x1, quant sobresurt el taulell
GAR_TOP = _y(149)                                  # l'alçada del taulell de la garita
CAFE3 = (_wx(CAFE[0]), _wx(CAFE[2] + 1), 40)       # la màquina de cafè: x0, x1, fons

CAM = Camera(pos=(440, 205, -300), yaw=-0.36, pitch=0.17, f=450, centre=(ROOM_W // 2, 92))

LIGHT = Light(ambient=0.0, vignette=None, floor_fade=None)  # (la llum és la del món: la de l'Escena)
TEXL = Light(ambient=-0.1, vignette=None, floor_fade=None)   # la dels dibuixos plans (les textures): neutra
FLUOS = [(120, 196, 230), (330, 196, 230), (120, 196, 70), (330, 196, 70)]
LLUMS = [Llum(p, 260, 0.9, power=1.2) for p in FLUOS] + \
        [Llum(((WIN[0] + WIN[1]) / 2, 80, ZW - 10), 260, 1.3, power=1.3),               # l'alba, per la vidriera
         Llum(((CAFE3[0] + CAFE3[1]) / 2, 90, ZW - 44), 90, 1.0, power=1.6)]              # la màquina de cafè


# ─── Les textures: el dibuix pla de sempre ───────────────────────────────────

def _parets(cig='sencera', fum=None, panell=False, maleti=False):
    """Les dues parets, de cara (el dibuix pla): formigó, el panell, la porta de personal i el rètol de facturació
    (l'esquerra); la vidriera amb l'Ortega a fora i la garita d'objectes perduts sense el taulell (el fons).
    `fum`: el fotograma del fum i el llum de l'avió; `panell`: la fletxeta encesa; `maleti`: el maletí al prestatge."""
    cv = Canvas(light=TEXL)
    PL.wall(cv)
    PL.departures(cv)
    PL.outside(cv)
    PL.ortega(cv, cig)
    PL.window_frame(cv)
    PL.staff_door(cv)
    _rètol(cv)
    lf = PL.lost_counter
    PL.lost_counter = lambda c: None                    # (el taulell de la garita és en 3D)
    try:
        PL.lost_found(cv)
    finally:
        PL.lost_counter = lf
    if maleti:
        PL.maleti(cv)
    if fum is not None:
        _fum(cv, fum)
    if panell:
        x0, y0 = BOARD_BOX[:2]
        ax, ay = x0 + 58 + PL.text_width('BCMU-07') + 4, y0 + 6
        for k in range(4):
            cv.vline(ax + k, ay - k, ay + k, [(255, 220, 120)], 0, lit=0)
        cv.glow(ax + 1, ay, 7, (250, 180, 60), 0.3)
    return cv.img


def _rètol(cv):
    """El rètol «FACTURACIÓ», penjat de la paret (al pla era dins el taulell)."""
    from hd640.rooms.bcmu_passadis_pla_comu import text2      # la font a 2×: a 1×, en escorç, no es llegia
    w = 2 * PL.text_width('FACTURACIÓ') + 1
    PL.obox(cv, 123 - w // 2 - 6, 51, 123 + w // 2 + 6, 77, BLUE, 3.0)   # (alt: l’accent de la Ó)
    cv.hline(123 - w // 2 - 4, 123 + w // 2 + 4, 53, BLUE, 3.8)
    text2(cv, "FACTURACIÓ", 123 - w // 2, 63, (240, 244, 250))
    cv.vline(107, 44, 51, PL.STEELB, 2.4)
    cv.vline(139, 44, 51, PL.STEELB, 2.4)


def _fum(cv, i):
    """El fum de la cigarreta de l'Ortega i el llum anticol·lisió de l'avió (fotograma i de 10)."""
    for k in range(6):
        t = (i + k * 5 / 3) % 10
        sx = PL.CIG[0] + PL.CIG_LEN['sencera'] - 3 + round(math.sin((t + k) * 0.9) * 2.7 + t * 0.45)
        sy = round(PL.CIG[1] - 4 - t * 2.7)
        if sy > 40:
            w = 1 if t < 5 else 2
            cv.tint(sx, sy, sx + w, sy, (220, 220, 230), 0.45 - t * 0.04)
    cv.flat(*PL.TAIL_LED, (255, 60, 60) if i % 5 == 0 else (90, 30, 40))
    if i % 5 == 0:
        cv.glow(*PL.TAIL_LED, 5, (255, 60, 60), 0.6)


def _coses(ulleres=False, boto=None):
    """Els mobles i les coses, dibuixats plans sobre transparent (en surten els retalls)."""
    cv = Canvas(light=TEXL, transparent=True)
    PL.checkin(cv)
    PL.lost_counter(cv)
    PL.maquina(cv)
    if ulleres:
        PL.ulleres(cv)
    if boto is not None and boto < 9:                    # un botó de la màquina de cafè, encès
        x0, y0 = CAFE[:2]
        bx, by = x0 + 8 + (boto % 3) * 9, y0 + 61 + (boto // 3) * 8
        cv.rect(bx, by, bx + 5, by + 4, [(150, 110, 80), (230, 190, 140), (255, 236, 200)],
                lambda x, y: 2.0 - (y - by) * 0.25, lit=0)
    return cv.img


def _planta():
    """La planta de plàstic, al racó entre la garita i la cafeteria (al pla, dins `cafe`)."""
    cv = Canvas(light=TEXL, transparent=True)
    PL.obox(cv, 571, 176, 584, PL.FLOOR_Y + 2, CONC, 3.4)
    cv.hline(572, 583, 177, SLATE, 1.0)
    for i in range(9):
        a = -1.25 + i * 0.31
        L = 15 + (i % 3) * 3
        cv.line(577, 176, 577 + round(math.sin(a) * L * 0.65), 176 - round(math.cos(a) * L), PL.PLANT, 2.6 + (i % 2))
    return cv.img.crop((564, 158, 591, 203))


def _maleti():
    cv = Canvas(light=TEXL, transparent=True)
    PL.maleti(cv)
    return cv.img


def _ulleres():
    cv = Canvas(light=TEXL, transparent=True)
    PL.ulleres(cv)
    return cv.img.crop((580, 170, 615, 182))


@functools.lru_cache(maxsize=None)
def _textures():
    return {'parets': _parets(), 'coses': _coses(), 'atrezzo': _atrezzo_tex()}


@functools.lru_cache(maxsize=None)
def _atrezzo_tex():
    """El que omple els extrems de la terminal (la sala és més ampla que la pantalla), dibuixat pla: el rètol de les
    portes d'embarcament, el panell publicitari del banc i els telèfons de la paret."""
    from hd.rooms.comu import obox, text, text_width
    from hd.rooms.bcmu import NAVYB
    from hd640.rooms.bcmu import logo
    cv = Canvas(light=TEXL, transparent=True)
    # el rètol que penja: «PORTES B1-B14» i la fletxa
    x0, y0, x1, y1 = SIGN_BOX
    obox(cv, x0, y0, x1, y1, BLUE, 3.0)
    cv.hline(x0 + 2, x1 - 2, y0 + 2, BLUE, 3.8)
    t = 'PORTES B1-B14'
    text(cv, t, x0 + 8, y0 + 7, [(240, 244, 250)], 0, flat=(240, 244, 250))
    ax = x0 + 14 + text_width(t)
    for k in range(7):
        cv.hline(ax + k, ax + 12 - k, (y0 + y1) // 2 - 6 + k, [(250, 210, 80)], 0, lit=0)
        cv.hline(ax + k, ax + 12 - k, (y0 + y1) // 2 + 6 - k, [(250, 210, 80)], 0, lit=0)
    cv.rect(ax - 8, (y0 + y1) // 2 - 1, ax + 4, (y0 + y1) // 2 + 1, [(250, 210, 80)], 0, lit=0)
    # el panell publicitari, encès: el logotip del banc i el lema
    x0, y0, x1, y1 = AD_BOX
    obox(cv, x0, y0, x1, y1, CHROME, 3.0)
    cv.rect(x0 + 3, y0 + 3, x1 - 3, y1 - 3, NAVYB, lambda x, y: 3.0 + 1.6 * (1 - abs(y - (y0 + y1) / 2) / ((y1 - y0) / 2)), lit=0)
    logo(cv, (x0 + x1) // 2, y0 + 30, k=3, lvl=4.4, lit=0.0)
    for t, yy in (('BCMU', y0 + 56), ('EL FUTUR', y0 + 72), ('ÉS TEU', y0 + 84)):
        text(cv, t, (x0 + x1) // 2 - text_width(t) // 2, yy, [(250, 220, 130)], 0, flat=(250, 220, 130))
    # tres telèfons de paret: la caixa, l'auricular, el teclat
    x0, y0, x1, y1 = PHONE_BOX
    for k in range(3):
        px = x0 + k * 30
        obox(cv, px, y0, px + 26, y1, [(30, 32, 38), (60, 64, 72), (100, 106, 116), (150, 156, 166), (200, 206, 214)], 2.4)
        cv.rect(px + 3, y0 + 4, px + 8, y0 + 34, [(10, 10, 12), (30, 30, 34), (60, 60, 66)], 1.4)            # l'auricular
        for r in range(4):
            for c in range(3):
                cv.rect(px + 11 + c * 4, y0 + 10 + r * 5, px + 13 + c * 4, y0 + 12 + r * 5, CHROME, 4.0)
        cv.rect(px + 11, y0 + 3, px + 23, y0 + 7, [(20, 60, 30), (60, 200, 90)], 1.0, lit=0)               # la pantalleta
    return cv.img


# ─── Les superfícies ────────────────────────────────────────────────────────

def _formigo(lvl0, seed=3):
    """Els plafons de formigó, en coordenades del món (on el dibuix pla no arriba): juntes cada 80 × 48, la franja
    blava a mitja alçada i el sòcol."""
    def L(s, t, P):
        y = HW - t
        if 72 <= y <= 77:
            return None
        seam = (int(s) % 80 == 0) or (int(t) % 48 == 47 and t > 13)
        if t > HW - 7:
            return 2.4 if t > HW - 1 else 3.2
        if seam:
            return lvl0 - 1.8
        return lvl0 + (hr(int(s) // 2, int(t) // 2, seed) - 0.5) * 0.3 + (hr(int(s) // 80, int(t) // 48, seed + 3) - 0.5) * 0.4
    return L


def _paret_proc(e, sid, P0, P1, P2, P3, seed):
    """Una paret de formigó procedural amb la franja blava (dues passades: el formigó i la franja)."""
    f = _formigo(4.0, seed)
    e.quad(sid, P0, P1, P2, P3, ramp=CONC, lvl=lambda s, t, P: f(s, t, P) or 4.0)
    L = math.dist(P0, P1)
    a = [P0[i] + (P3[i] - P0[i]) * (HW - 77) / HW for i in range(3)]
    b = [P1[i] + (P2[i] - P1[i]) * (HW - 77) / HW for i in range(3)]
    c = [P1[i] + (P2[i] - P1[i]) * (HW - 72) / HW for i in range(3)]
    d = [P0[i] + (P3[i] - P0[i]) * (HW - 72) / HW for i in range(3)]
    e.quad(sid, tuple(a), tuple(b), tuple(c), tuple(d), ramp=BLUE, lvl=lambda s, t, P: 3.4 if t < 1 else 2.6)
    return L


def _terra(s, t, P):
    """La rajola polida: peces de 48 × 27 que fugen cap al fons, amb juntes i una mica de taca."""
    x, z = P[0], P[2]
    if (x + 1000) % 48 < 1.0 or (z + 1000) % 36 < 1.0:
        return 2.6
    n = (hr(int((x + 1000) // 48), int((z + 1000) // 36), 2) - 0.5) * 0.4
    return 3.6 + n + (hr(int(x), int(z), 9) - 0.5) * 0.3


FOSC = [(4, 5, 8), (8, 10, 14), (14, 16, 22), (20, 24, 32), (28, 32, 42), (38, 42, 54)]


def _en_caixa(cx, cz, ang):
    c, s_ = math.cos(ang), math.sin(ang)

    def P(lx, y, lz):
        return (cx + lx * c - lz * s_, y, cz + lx * s_ + lz * c)
    return P


def _ombra(e, sid, cx, cz, rx, rz, k=0.5):
    e.foscor(sid, (cx - rx, 0.6, cz + rz), (cx + rx, 0.6, cz + rz), (cx + rx, 0.6, cz - rz), (cx - rx, 0.6, cz - rz),
             lambda s, t: k * min(1.0, max(0.0, 1 - ((s - rx) / rx) ** 2 - ((t - rz) / rz) ** 2) * 1.6))


def _seients(e, sid, seats, diari=False):
    """Una fila de cinc seients de plàstic blau, amb la barra i els peus de cromat (i el diari, si de cas)."""
    sx, sz, sa = seats
    P = _en_caixa(sx, sz, sa)
    _ombra(e, 'ombra_' + sid, sx, sz + 2, 92, 16, 0.5)
    e.caixa_girada(sid, *_xz(P(0, 0, 4)), 164, 4, 3, sa, CHROME, 3.6, y0=15)                 # la barra
    for lx in (-72, 0, 72):
        q = P(lx, 0, 4)
        e.caixa(sid, q[0] - 1, q[0] + 1, 0, 15, q[2] - 1, q[2] + 1, CHROME, 3.0)
    for i in range(5):
        lx = -64 + i * 32
        e.caixa_girada(sid, *_xz(P(lx, 0, 9)), 28, 4, 22, sa, BLUE, 2.4, y0=22,
                       cares={'davant': {'ramp': BLUE, 'lvl': lambda s, t, P_: 2.6 + (0.8 if t < 3 else 0)
                                         + (0.3 if (int(s) + int(t)) % 5 == 0 else 0)}})
        e.caixa_girada(sid, *_xz(P(lx, 0, 0)), 28, 18, 5, sa, BLUE, 2.8, y0=17,
                       cares={'dalt': {'ramp': BLUE, 'lvl': lambda s, t, P_: 3.4 - t * 0.04}})
        if i < 4:
            q = P(lx + 16, 0, 0)
            e.caixa(sid, q[0] - 1.2, q[0] + 1.2, 22, 30, q[2] - 6, q[2] + 6, CHROME, 3.6)
    if diari:
        e.quad(sid, P(-8, 22.4, 5), P(10, 22.4, 4), P(10, 22.4, -4), P(-8, 22.4, -3), ramp=SHEET,
               lvl=lambda s, t, P_: 4.2 - (1.4 if int(t) % 3 == 0 and 2 < s < 15 else 0))              # el diari


def atrezzo(e, tex):
    """Els extrems de la terminal: a la paret de l'esquerra, el panell del banc i els telèfons; a la paret del fons,
    a la dreta, la segona vidriera (l'alba sobre la pista), la segona fila de seients i el rètol de les portes."""
    at = tex['atrezzo']
    # el panell publicitari, a la paret de l'esquerra, de cara al passadís (i la seva claror a la paret)
    za, zb = AD_Z
    e.caixa('panell', 0, 6, 70, 150, za, zb, CHROME, 2.6, cares={'dreta': {'tex': (at, AD_BOX)}})
    # els telèfons
    zp = PHONE_Z
    e.caixa('telefons', 0, 7, 70, 116, zp, zp + (PHONE_BOX[2] - PHONE_BOX[0]) * 0.55, SLATE, 2.2,
            cares={'dreta': {'tex': (at, PHONE_BOX)}})
    # la segona vidriera: el cel de l'alba, la pista amb les llums i els travessers
    x0, x1, y0, y1 = WIN2
    hor = y0 + 34
    def vidre(s, t, P_):
        y = y1 - t
        if (int(s) % 62) < 3 or t < 3 or t > (y1 - y0) - 3:
            return -9                                                 # (els travessers: es pinten a part)
        if y < hor:
            k = 1.0 if (y > hor - 6 and int(s * 0.7) % 23 == 0) else 0.0      # les llums de la pista
            return 0.6 + 0.5 * (y - y0) / 34 + k * 7
        return 8.0 - 6.4 * min(1.0, (y - hor) / (y1 - hor)) ** 0.8 + (hr(int(s) // 9, int(t) // 3, 41) - 0.5) * 0.2
    e.quad('vidriera2', (x0, y1, ZW - 0.3), (x1, y1, ZW - 0.3), (x1, y0, ZW - 0.3), (x0, y0, ZW - 0.3),
           ramp=DAWN_T, lvl=lambda s, t, P_: max(0.0, vidre(s, t, P_)))
    e.quad('vidriera2', (x0, y1, ZW - 0.4), (x1, y1, ZW - 0.4), (x1, y0, ZW - 0.4), (x0, y0, ZW - 0.4), ramp=CHROME,
           lvl=3.2, forma=lambda s, t: (int(s) % 62) < 3 or t < 3 or t > (y1 - y0) - 3)
    # la segona fila de seients
    _seients(e, 'seients2', SEATS2)
    # el rètol de les portes, penjat del sostre amb dos cables
    cx, cy, cz = SIGN
    w, h = (SIGN_BOX[2] - SIGN_BOX[0]) * 0.55, (SIGN_BOX[3] - SIGN_BOX[1]) * 0.55
    e.caixa('retol', cx - w / 2, cx + w / 2, cy, cy + h, cz - 2, cz + 2, BLUE, 2.4, cares={'davant': {'tex': (at, SIGN_BOX)}})
    for dx in (-w / 2 + 8, w / 2 - 8):
        e.cable('retol', [(cx + dx, cy + h, cz), (cx + dx, HW + 40, cz)], CHROME, 2.6, gruix=1.0)


def escena(cv, tex, estat=frozenset()):
    """Tota la sala, de lluny a prop. `estat`: els decorats que hi són ('ulleres'). → l'Escena."""
    e = Escena(cv, CAM, LLUMS, ambient=-0.6)
    zn = CAM.pos[2] + 60
    parets, coses = tex['parets'], tex['coses']
    # la paret de l'esquerra (x = 0): de prop, formigó; cap a la cantonada, el dibuix pla (x 0..215)
    _paret_proc(e, 'paret_esq_prop', (0, HW, zn), (0, HW, ZW - XL), (0, 0, ZW - XL), (0, 0, zn), 5)
    e.quad('paret_esq', (0, HW, ZW - XL), (0, HW, ZW), (0, 0, ZW), (0, 0, ZW - XL), tex=(parets, (0, 0, XL, HW)))
    # la paret del fons (z = 300): el dibuix pla (x 215..640) i, a la dreta, més formigó
    e.quad('paret_fons', (0, HW, ZW), (W - XL, HW, ZW), (W - XL, 0, ZW), (0, 0, ZW), tex=(parets, (XL, 0, W, HW)))
    _paret_proc(e, 'paret_fons_dreta', (W - XL, HW, ZW), (XR, HW, ZW), (XR, 0, ZW), (W - XL, 0, ZW), 7)
    # el terra polit, amb el reflex de l'alba davant la vidriera, el dels fluorescents i el de la màquina de cafè
    e.quad('terra', (0, 0, ZW), (XR, 0, ZW), (XR, 0, zn), (0, 0, zn), ramp=TILE, lvl=_terra)
    x0, x1 = WIN[0], WIN[1]
    e.claror((x0 - 10, 0.3, ZW), (x1 + 10, 0.3, ZW), (x1 + 60, 0.3, ZW - 150), (x0 - 40, 0.3, ZW - 150), (220, 150, 160),
             lambda s, t: 0.3 * max(0.0, 1 - t / 150) * (0.6 + 0.4 * math.sin(s / 9.0) ** 2))
    for fx, _, fz in FLUOS:
        e.claror((fx - 40, 0.35, fz + 12), (fx + 40, 0.35, fz + 12), (fx + 40, 0.35, fz - 12), (fx - 40, 0.35, fz - 12),
                 (220, 236, 255), lambda s, t: 0.18 * max(0.0, 1 - abs(t - 12) / 12) * max(0.0, 1 - abs(s - 40) / 40))
    cx0, cx1, cd = CAFE3
    e.claror((cx0 - 30, 0.4, ZW - cd), (cx1 + 30, 0.4, ZW - cd), (cx1 + 30, 0.4, ZW - cd - 70), (cx0 - 30, 0.4, ZW - cd - 70),
             (230, 90, 70), lambda s, t: 0.22 * max(0.0, 1 - t / 70) * max(0.0, 1 - abs(s - 51) / 52))
    # la foscor dels racons
    e.foscor('racons', (0, 0.5, ZW), (XR, 0.5, ZW), (XR, 0.5, zn), (0, 0.5, zn),
             lambda s, t: max(0.35 * max(0.0, 1 - t / 24), 0.35 * max(0.0, 1 - s / 30)))
    e.foscor('cantonada', (0, HW, ZW - 0.5), (60, HW, ZW - 0.5), (60, 0, ZW - 0.5), (0, 0, ZW - 0.5),
             lambda s, t: 0.4 * max(0.0, 1 - s / 60) ** 2)
    e.foscor('cantonada', (0.5, HW, ZW - 60), (0.5, HW, ZW), (0.5, 0, ZW), (0.5, 0, ZW - 60),
             lambda s, t: 0.4 * max(0.0, s / 60) ** 2)
    # la garita: el taulell groc que sobresurt de la paret, els muntants i el sostre amb el rètol (el dibuix pla)
    gx0, gx1, gd = GARITA
    _ombra(e, 'ombra_garita', (gx0 + gx1) / 2, ZW - gd / 2 - 4, (gx1 - gx0) / 2 + 8, gd / 2 + 10, 0.5)
    e.caixa('garita', gx0 + 2, gx1 - 2, 0, GAR_TOP - 5, ZW - gd, ZW, YELS, 1.8,
            cares={'davant': {'tex': (coses, (440, 155, 569, 201))}, 'esquerra': {'ramp': YELS, 'lvl': 1.4}})
    e.caixa('garita', gx0, gx1, GAR_TOP - 5, GAR_TOP, ZW - gd - 3, ZW, DESK, 5.0,
            cares={'dalt': {'ramp': DESK, 'lvl': 4.2}, 'davant': {'ramp': DESK, 'lvl': lambda s, t, P_: 5.0 - t * 0.5}})
    e.sprite('garita', coses.crop((452, 142, 467, 150)), (7, 7), (_wx(459), GAR_TOP, ZW - gd + 6))       # el timbre
    e.quad('garita', (_wx(531), GAR_TOP + 0.3, ZW - gd + 18), (_wx(555), GAR_TOP + 0.3, ZW - gd + 18),
           (_wx(555), GAR_TOP + 0.3, ZW - gd + 4), (_wx(531), GAR_TOP + 0.3, ZW - gd + 4), ramp=SHEET,
           lvl=lambda s, t, P_: 4.6 - (1.6 if int(t) % 4 == 0 and 3 < s < 20 else 0))                   # el formulari
    for fx in (gx0, gx1 - 3):
        e.caixa('garita', fx, fx + 3, GAR_TOP, _y(93), ZW - gd, ZW, CHROME, 3.4)
    e.caixa('garita', gx0 - 2, gx1 + 2, _y(93), _y(76), ZW - gd - 4, ZW, YELS, 3.0,
            cares={'davant': {'tex': (parets, (440, 77, 569, 94))}, 'dalt': {'ramp': YELS, 'lvl': 2.6},
                   'esquerra': {'ramp': YELS, 'lvl': 2.4}})
    # la planta, al racó entre la garita i la cafeteria
    e.sprite('planta', _planta(), (13, 44), (_wx(577), 0, ZW - 12))
    # la màquina de cafè, que sobresurt de la paret
    e.caixa('cafe', cx0, cx1, 0, _y(CAFE[1]), ZW - cd, ZW, VEND, 2.4,
            cares={'davant': {'tex': (coses, (CAFE[0], CAFE[1], CAFE[2] + 1, CAFE[3] + 1))},
                   'dalt': {'ramp': VEND, 'lvl': 3.0}, 'esquerra': {'ramp': VEND, 'lvl': 1.8}})
    # la fila de seients, davant la vidriera, una mica girada (amb el diari)
    _seients(e, 'seients', SEATS, diari=True)
    # el taulell de facturació, separat de la paret de l'esquerra: el frontal blau (el dibuix pla), la tapa i els
    # monitors (de cara al passadís)
    dx0, dx1, dz0, dz1, dh = DESK3
    _ombra(e, 'ombra_taulell', dx1 + 4, (dz0 + dz1) / 2, 14, (dz1 - dz0) / 2 + 8, 0.5)
    e.caixa('taulell', dx0, dx1, 0, dh - 6, dz0, dz1, BLUE, 2.2,
            cares={'dreta': {'tex': (coses, (40, 146, 206, 201))},
                   'davant': {'ramp': BLUE, 'lvl': lambda s, t, P_: 1.8 + (0.4 if int(s) % 13 == 0 else 0)}})
    e.caixa('taulell', dx0 - 2, dx1 + 5, dh - 6, dh, dz0 - 4, dz1 + 4, DESK, 5.0,
            cares={'dreta': {'ramp': DESK, 'lvl': lambda s, t, P_: 6.0 - t * 0.4},
                   'dalt': {'ramp': DESK, 'lvl': lambda s, t, P_: 5.4 - s * 0.02}})
    for k, mx in enumerate((67, 144)):
        mz = dz0 + (dz1 - dz0) * (0.22 + 0.5 * k)
        e.sprite('monitors', coses.crop((mx - 1, 111, mx + 31, 140)), (15.5, 28), (dx0 + 8, dh, mz))
    # el pal de la cua, amb la cinta blava fins al taulell
    px, pz = POST
    _ombra(e, 'ombra_pal', px, pz, 8, 6, 0.5)
    _disc(e, 'pal', px, pz, 6, 1.5, CHROME, 3.0)
    e.tub('pal', (px, 2, pz), (px, 44, pz), 1.3, CHROME, 3.6)
    e.cable('pal', [(px, 38, pz), (px - 12, 36, pz + 10), (dx1 + 1, 38, pz + 22)], BLUE, 3.2, gruix=2.0)
    # la taula alta, rodona (el got a sobre; les ulleres, un decorat)
    tx, tz, tr, th = TAULA
    _ombra(e, 'ombra_taula', tx + 6, tz + 4, tr * 0.8, tr * 0.6, 0.45)
    _disc(e, 'taula', tx, tz, 12, 2.0, CHROME, 3.0)
    e.tub('taula', (tx, 2, tz), (tx, th - 2, tz), 1.6, CHROME, 3.4)
    e.quad('taula', (tx - tr, th, tz + tr), (tx + tr, th, tz + tr), (tx + tr, th, tz - tr), (tx - tr, th, tz - tr),
           ramp=CHROME, lvl=lambda s, t, P_: 3.6 - t * 0.012 - (1.4 if math.hypot(s - tr, t - tr) > tr - 1.5 else 0),
           forma=lambda s, t: math.hypot(s - tr, t - tr) < tr)
    e.caixa('taula', tx + 12, tx + 18, th, th + 9, tz + 4, tz + 10, [(30, 20, 18), (120, 110, 104), (200, 196, 188),
                                                                    (240, 236, 230)], 2.8,
            cares={'dalt': {'ramp': [(20, 12, 6), (70, 40, 20)], 'lvl': 1.0}})                            # el got
    if 'ulleres' in estat:
        e.quad('ulleres', (tx - 16, th + 0.4, tz + 2), (tx + 12, th + 0.4, tz + 2), (tx + 12, th + 0.4, tz - 8),
               (tx - 16, th + 0.4, tz - 8), tex=(_ulleres(), (0, 0, 35, 12)))
    atrezzo(e, tex)
    if 'sense_primer_pla' in estat:
        return e
    # primer pla: un pilar de formigó i un carro de maletes, en silueta
    e.caixa('primer_pla', 440, 486, 0, 400, -50, -6, FOSC, 2.0,
            cares={'esquerra': {'ramp': FOSC, 'lvl': lambda s, t, P_: 2.8 - (1.0 if int(t) % 48 == 0 else 0)},
                   'davant': {'ramp': FOSC, 'lvl': 1.6}})
    _carro(e, 'primer_pla', 90, -70, 0.6)
    return e


def _disc(e, sid, x, z, r, y, ramp, lvl):
    """Un disc pla i horitzontal a l'alçada `y` (la base d'un pal o d'una taula), amb el cantell fosc."""
    e.quad(sid, (x - r, y, z + r), (x + r, y, z + r), (x + r, y, z - r), (x - r, y, z - r), ramp=ramp,
           lvl=lambda s, t, P_: lvl + 0.8 - t / r * 0.4 - (1.6 if math.hypot(s - r, t - r) > r - 1.2 else 0),
           forma=lambda s, t: math.hypot(s - r, t - r) < r)


def _xz(p):
    return p[0], p[2]


def _carro(e, sid, cx, cz, ang):
    """Un carro de maletes, amb una maleta i una bossa a sobre (en silueta)."""
    P = _en_caixa(cx, cz, ang)
    e.caixa_girada(sid, cx, cz, 70, 40, 3, ang, FOSC, 2.6, y0=10)
    for lx in (-30, 30):
        for lz in (-16, 16):
            q = P(lx, 0, lz)
            e.caixa(sid, q[0] - 3, q[0] + 3, 0, 10, q[2] - 3, q[2] + 3, FOSC, 1.4)
    for lz in (-17, 17):
        q = P(32, 0, lz)
        e.caixa(sid, q[0] - 1.5, q[0] + 1.5, 10, 70, q[2] - 1.5, q[2] + 1.5, FOSC, 2.4)
    q = P(32, 0, 0)
    e.caixa_girada(sid, q[0], q[2], 4, 40, 4, ang, FOSC, 3.0, y0=66)
    q = P(-6, 0, 0)
    e.caixa_girada(sid, q[0], q[2], 52, 34, 24, ang, FOSC, 2.2, y0=13,
                   cares={'dalt': {'ramp': FOSC, 'lvl': 3.0}})
    q = P(-12, 0, 2)
    e.caixa_girada(sid, q[0], q[2], 30, 24, 14, ang + 0.3, FOSC, 2.6, y0=37,
                   cares={'dalt': {'ramp': FOSC, 'lvl': 3.4}})


# ─── Composició i llum ──────────────────────────────────────────────────────

def _proj(P):
    u, v, _ = CAM.projecta(P)
    return u, v


def _fx():
    wx, wy = _proj(((WIN[0] + WIN[1]) / 2, 40, ZW))
    cx, cy = _proj(((CAFE3[0] + CAFE3[1]) / 2, 90, ZW - CAFE3[2]))
    light = [llum.wash(wx, wy + 60, 220, (220, 150, 160), k=0.5, air=0.05, squash=0.7),       # l'alba, rosada
             llum.wash(cx, cy, 120, (255, 110, 90), k=0.7, air=0.08, squash=0.8),              # la màquina de cafè
             llum.wash(320, -40, 420, (200, 220, 255), k=0.35, air=0.03, squash=0.7)]          # els fluorescents
    tone = [llum.grade(contrast=1.08, pivot=50, sat=1.1, lift=(2, 4, 10))]
    bloom = [llum.bloom(thr=200, radii=((3, 0.4), (12, 0.25), (32, 0.12)))]
    return light, bloom, tone


def _render(estat=frozenset(), tex=None):
    cv = Canvas(ROOM_W, light=LIGHT)
    e = escena(cv, tex or _textures(), estat)
    cv.rect(0, BOTTOM + 1, ROOM_W - 1, H - 1, [(0, 0, 0)], 0, lit=0)    # la barra de verbs: negre
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


@functools.lru_cache(maxsize=None)
def _fons_llum():
    """El fons de la sala sense el primer pla (que és una capa a part, amb parallax)."""
    return _amb_llum(_render(estat=frozenset({'sense_primer_pla'}))[0])


def bg(cv):
    cv.img.paste(_fons_llum())
    cv.P = cv.img.load()


def _capa_primer_pla():
    """El primer pla, amb la llum, retallat de la sala sencera (la capa del davant que fa parallax)."""
    from PIL import Image
    full, (_, e) = _base_llum(), _base()
    out = Image.new('RGBA', full.size, (0, 0, 0, 0))
    src, dst, ids, amo, w = full.load(), out.load(), e.ids, e.amo, e.cv.w
    for y in range(BOTTOM + 1):
        for x in range(full.width):
            if ids[amo[y * w + x]] == 'primer_pla':
                dst[x, y] = src[x, y]
    return out


def _fotograma(capes):
    """El fons amb unes capes damunt, amb la llum, menys el fons amb la llum."""
    img, _ = _base()
    img = img.copy()
    for c in capes:
        img.alpha_composite(c)
    return _diff(_amb_llum(img), _base_llum())


def _decorat(*estat):
    """Un decorat: la sala amb aquell estat, menys la de sempre (només el que canvia), amb la llum."""
    def draw(cv):
        img, _ = _render(frozenset(estat))
        out = _diff(_amb_llum(img, bloom=False), _amb_llum(_base()[0], bloom=False))
        cv.img.alpha_composite(out)
        cv.P = cv.img.load()
    return draw


def _capa(sids, flat):
    """Un decorat dibuixat pla i projectat per les superfícies `sids` (on són les que es veuen)."""
    def draw(cv):
        _, e = _base()
        cv.img.alpha_composite(_fotograma([e.capa(flat(), sids)]))
        cv.P = cv.img.load()
    return draw


PROPS = {
    'maleti': _capa({'paret_fons'}, _maleti),
    'ulleres': _decorat('ulleres'),
    'cigarreta_mitja': _capa({'paret_fons'}, lambda: _parets(cig='mitja')),
    'cigarreta_curta': _capa({'paret_fons'}, lambda: _parets(cig='curta')),
}


# ─── Animacions ─────────────────────────────────────────────────────────────

def _frames():
    """El fum de la cigarreta de l'Ortega i el llum anticol·lisió de l'avió."""
    _, e = _base()
    return [_fotograma([e.capa(_parets(fum=i), {'paret_fons'})]) for i in range(10)]


def _frames_panell():
    """El llumet d'«embarcant» del BCMU-07, al panell de sortides: encès, apagat."""
    _, e = _base()
    return [_fotograma([e.capa(_parets(panell=True), {'paret_esq'})]), _diff(_base_llum(), _base_llum())]


def _frames_cafe():
    """La màquina de cafè, esperant clients: els botons s'il·luminen d'un en un i després descansen."""
    _, e = _base()
    buit = _diff(_base_llum(), _base_llum())
    return [_fotograma([e.capa(_coses(boto=i), {'cafe'})]) if i < 9 else buit for i in range(12)]


ANIMS = {'terminal': {'frames': _frames, 'frameDuration': 160},
         'panell': {'frames': _frames_panell, 'frameDuration': 650},
         'cafe': {'frames': _frames_cafe, 'frameDuration': 260}}


def _amo(ids):
    def mask(x, y):
        _, e = _base()
        return e.ids[e.amo[y * e.cv.w + x]] in ids
    return mask


def _p(x, z, y=0.0):
    u, v, _ = CAM.projecta((x, y, z))
    return round(u), round(v)


EMPLEAT = (GARITA[0] + 25, ZW - 10)                    # l'empleat, darrere el taulell de la garita (x, z)
ZG = ZW - GARITA[2] - 8                                 # davant la garita, on s'hi para la gent (z)

# Capes del davant: el primer pla (sempre davant), la garita (l'empleat hi és darrere; qui hi és davant, la tapa) i
# la taula alta (s'hi passa per darrere).
FRONT = [
    # el primer pla: una capa a part (el fons no el porta) que es mou més de pressa que la sala; alineada a mig recorregut
    {'id': 'davant', 'mask': _amo({'primer_pla'}), 'image': _capa_primer_pla, 'baseline': 999, 'zIndex': 20,
     'parallaxDepth': PARALLAX, 'x': round((PARALLAX - 1) * (ROOM_W - W) / 2 / PARALLAX)},
    {'id': 'davant_seients2', 'mask': _amo({'seients2'}), 'baseline': _p(SEATS2[0], SEATS2[1] - 16)[1], 'zIndex': 20},
    # (la línia base, la de la vora més llunyana d'on es pot parar la gent davant la garita: l'empleat queda més amunt)
    {'id': 'davant_garita', 'mask': _amo({'garita'}), 'baseline': _p(GARITA[0], ZG)[1] + 1, 'zIndex': 20},
    {'id': 'davant_taula', 'mask': _amo({'taula'}), 'baseline': _p(TAULA[0], TAULA[1] - 6)[1], 'zIndex': 20},
]


# ─── Geometria (coordenades de sala, projectades) ────────────────────────────

def _rect_mon(*Ps):
    pts = [CAM.projecta(P) for P in Ps]
    return (max(0, round(min(p[0] for p in pts))), max(0, round(min(p[1] for p in pts))),
            min(ROOM_W - 1, round(max(p[0] for p in pts))), min(BOTTOM, round(max(p[1] for p in pts))))


# El terra on es camina (al món): de la porta de personal (pel passadís de darrere el taulell) a la cafeteria, davant
# el taulell, els seients i la garita, i per darrere de la taula alta; el davant, fins on l'escala arriba a ≈1,2.
WALK_MON = [(8, 40), (8, 136), (40, 136), (40, 112), (82, 110), (82, 252), (232, 258), (240, ZG), (346, ZG),
            (352, 250), (440, 248), (470, 236), (530, 240), (780, 240), (780, -60), (60, -60), (60, 20)]


def _talla(poly, a, b, c):
    """Retalla el polígon (de pantalla) pel semiplà a·u + b·v + c ≥ 0."""
    out = []
    for P, Q in zip(poly, poly[1:] + poly[:1]):
        fp, fq = a * P[0] + b * P[1] + c, a * Q[0] + b * Q[1] + c
        if fp >= 0:
            out.append(P)
        if (fp >= 0) != (fq >= 0):
            k = fp / (fp - fq)
            out.append((P[0] + (Q[0] - P[0]) * k, P[1] + (Q[1] - P[1]) * k))
    return out
def _escala_a(v):
    """L'escala d'un personatge amb els peus a la y de pantalla `v` (al terra, la profunditat només depèn de v)."""
    lo, hi = -200.0, 2000.0
    for _ in range(60):
        z = (lo + hi) / 2
        if CAM.projecta((260, 0, z))[1] > v:
            lo = z
        else:
            hi = z
    return CAM.escala((260, 0, (lo + hi) / 2))


def _v_escala(k):
    """La y de pantalla on un personatge fa escala `k`."""
    lo, hi = 0.0, float(BOTTOM)
    for _ in range(40):
        m = (lo + hi) / 2
        if _escala_a(m) < k:
            lo = m
        else:
            hi = m
    return lo


# (retallat per on un personatge passaria d'escala 1,2 i per les vores de la sala)
_WALK = [_p(x, z) for x, z in WALK_MON]
for _a, _b, _c in ((1, 0, -4), (-1, 0, ROOM_W - 5), (0, -1, min(BOTTOM - 4, _v_escala(1.2)))):
    _WALK = _talla(_WALK, _a, _b, _c)
_WALK = [(round(u), round(v)) for u, v in _WALK]
_V_FONS, _V_PROP = min(v for _, v in _WALK), max(v for _, v in _WALK)

_TR = TAULA

GEOMETRIA = {
    'things': {
        'taulell': {'rect': _rect_mon((DESK3[0], DESK3[4], DESK3[2] - 4), (DESK3[1] + 5, 0, DESK3[2] - 4),
                                      (DESK3[1] + 5, 0, DESK3[3] + 4), (DESK3[0], DESK3[4] + 30, DESK3[3])),
                    'walk': _p(DESK3[1] + 26, (DESK3[2] + DESK3[3]) / 2)},
        'vidriera': {'rect': _rect_mon((WIN[0], WIN[3], ZW), (WIN[1], WIN[2], ZW)),
                     'walk': _p((WIN[0] + WIN[1]) / 2 + 30, 240)},
        'maleti': {'rect': _rect_mon((_wx(523), _y(112), ZW), (_wx(558), _y(142), ZW)),
                   'walk': _p(_wx(540), ZG)},
        'ulleres': {'rect': _rect_mon((_TR[0] - 18, _TR[3] + 10, _TR[1] + 4), (_TR[0] + 14, _TR[3] - 2, _TR[1] - 10)),
                    'walk': _p(_TR[0] - 34, _TR[1] - 22)},
    },
    'spawns': {'vet': _p(250, 150), 'soler': _p(22, 112), 'empleat': _p(*EMPLEAT), 'nen': _p(196, 226)},
    'walkable': _WALK,
    'floorSquash': 0.42,                           # (la càmera, picada: el terra es veu aixafat)
    # L'ombra de contacte: la llum dominant és l'alba de la vidriera (el peu de la vidriera); allargada cap enfora.
    'characterShadow': {'enabled': True, 'color': '#0a0e18', 'alpha': 0.4, 'squash': 0.4, 'core': 0.6,
                        'light': {'x': _p((WIN[0] + WIN[1]) / 2, ZW)[0], 'y': _p((WIN[0] + WIN[1]) / 2, ZW)[1],
                                  'stretch': 0.7, 'reach': 200}},
    'regions': [{'id': 'perspectiva', 'active': True, 'scaleEnabled': True, 'scaleWalkSpeed': True,
                 'scaleTop': round(_escala_a(_V_FONS - 2), 3), 'scaleBottom': round(_escala_a(_V_PROP + 2), 3),
                 'points': [(0, _V_FONS - 2), (ROOM_W - 1, _V_FONS - 2), (ROOM_W - 1, _V_PROP + 2), (0, _V_PROP + 2)]}],
    # la llum de la sala sobre els personatges, en temps d'execució
    'characterLights': {
        'ambient': '#a4acbc',                                                           # fluorescents, freds
        'lights': [
            {'x': _p((WIN[0] + WIN[1]) / 2, ZW, 80)[0], 'y': _p((WIN[0] + WIN[1]) / 2, ZW, 80)[1], 'radius': 260,
             'color': '#e0a0a0', 'intensity': 0.6},                                     # l'alba
            {'x': _p((CAFE3[0] + CAFE3[1]) / 2, ZW - CAFE3[2], 90)[0],
             'y': _p((CAFE3[0] + CAFE3[1]) / 2, ZW - CAFE3[2], 90)[1], 'radius': 120,
             'color': '#ff6e5a', 'intensity': 0.7},                                     # la màquina de cafè
        ],
    },
}
