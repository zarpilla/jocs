"""
El final (els tres finals): una setmana després, el bar La Propina, a la tarda. EN 3D (hd640/tres_d.py), a 1×.
Cinemàtica, sense res clicable.

És l'escena del bar de l'Escena 2 (bar_sala.py), amb la mateixa càmera, de dia:
  - per l'aparador i la porta de la façana entra el sol de la tarda, que fa clapes en diagonal pel terra; el neó
    «LA PROPINA», apagat; el pernil ja no hi és (se l'han menjat);
  - una tele nova i més grossa al suport de la paret: la roda de premsa del BCMU, «EL SISTEMA HA RESISTIT» i, a la
    cinta, «CAL MÉS REGULACIÓ»; el cable baixa per la paret fins a un moble baix al costat de la porta, on hi ha la
    regleta (el que mossega en Diu); i la tele apagada (`tele_apagada`), quan l'ha mossegat;
  - gerres de cervesa i cava damunt la barra; i un paper escrit a mà, «TORNEM A ESTAR OBERTS», enganxat amb cinta
    a les estovalles de la taula del mig;
  - la **taula llarga**: tres taules diferents ajuntades, cadascuna una mica girada i amb les seves estovalles
    (quadres, fil, paper), amb gots, ampolles, pa amb tomàquet i el porró. Tothom hi seu al darrere, de cara, i les
    estovalles els tapen les cames (FRONT); a la punta de la dreta, la cistella d'en Diu, damunt d'un tamboret baix;
  - primer pla: la taula i les cadires en silueta i el pilar (els del bar).
Animació: `tele` (el banquer parla i fa que sí, el punt d'«EN DIRECTE» i l'escurabutxaques).
"""
import functools
import math

import hd640  # noqa: F401  (abans de cap hd.rooms: posa la llibreria a 640×360)
from hd640 import llum
from hd.pix import Canvas, Light, W, H, hr
from hd.rooms.comu import _diff, SHEET
from hd640.rooms import bar_sala as B
from hd640.rooms import final_bar_pla_comu as PL
from hd640.rooms.final_bar_pla_comu import (WICKER, BLANKET, TOMATO, BREAD, BEER, CLOTH, VICHY, PAPER, TV as TV_PLA)
from hd640.rooms.bar_sala_pla_comu import WOOD, STEELB, BRASS, PORC, BOTTLES, SLATE, PLASTIC
from hd640.tres_d import Llum

CAM = B.CAM
BOTTOM = B.BOTTOM
ZW, XR = B.ZW, B.XR
LIGHT = Light(ambient=0.0, vignette=None, floor_fade=None)

# la tele nova (al dibuix pla, 429..549 × 29..116), al mateix suport de la paret
TV = (B._w(TV_PLA[0]), B._w(TV_PLA[2]), B._y(TV_PLA[3] + 1), B._y(TV_PLA[1]), ZW - 18, ZW - 4)
TV_CROP = (TV_PLA[0], TV_PLA[1], TV_PLA[2] + 1, TV_PLA[3] + 1)
# la taula llarga: el centre, el gir (gairebé de cara a la càmera: girada respecte de la barra) i les tres taules
TAULA = (370, 95, -0.41)
TAULES = ((-138, -46, 'quadres', 0.03, 0), (-46, 46, 'fil', 0.0, -1), (46, 138, 'paper', -0.04, 0))
T_H, T_D = 48, 40                                  # alçada i fons de les taules
SEIENTS = {'rius': -114, 'ballester': -76, 'marcel': -38, 'iri': 0, 'vet': 38, 'tomas': 76, 'pons': 114}
SEU = 30                                           # els que seuen, darrere la taula (al llarg de la z local)
CISTELLA = (520, 11, 14)                           # el tamboret baix amb la cistella: x, z, alçada
MOBLE = (562, 599, 108, 152, 40)                   # el moble baix al costat de la porta: x0, x1, z0, z1, alt
REGLETA = (577, 118)                               # la regleta, damunt el moble (x, z)
NETA = (226, 112)                                  # la NETA-3, dreta a la punta de l'esquerra, servint


def _l(lx, lz, y=0.0, ang=None, cx=None, cz=None):
    """Un punt en coordenades de la taula (lx al llarg, lz cap al fons) → el món."""
    x0, z0, a = TAULA
    a = a if ang is None else ang
    cx = x0 if cx is None else cx
    cz = z0 if cz is None else cz
    c, s = math.cos(a), math.sin(a)
    return (cx + lx * c - lz * s, y, cz + lx * s + lz * c)


SOL = (1.0, 0.55, 0.5)          # cap on va (des del terra) el raig de sol: cap a la façana, amunt i cap al fons
LLUMS = [Llum(B.FLUO, 280, 0.6, power=1.3),                                 # el fluorescent, encès però sense força
         Llum((XR + 160, 170, 268), 640, 0.9, power=1.0),                   # el sol per l'aparador
         Llum((XR + 160, 110, 70), 640, 0.9, power=1.0),                    # el sol per la porta
         Llum(((TV[0] + TV[1]) / 2, (TV[2] + TV[3]) / 2, TV[4] - 10), 120, 0.6, power=1.8)]   # la tele


# ─── Les textures ───────────────────────────────────────────────────────────

def _suport(F):
    """El braç de la tele nova, a la paret."""
    F.rect(480, 19, 499, 29, STEELB, lambda x, y: 2.8 + (0.8 if x == 480 else 0))
    F.rect(476, 15, 503, 19, STEELB, 3.4)


def _tele(frame=0, apagada=False):
    cv = Canvas(light=B.TEXL)
    PL.tv_frame(cv)
    PL.tv_news(cv, frame)
    if apagada:
        PL.tele_apagada(cv)
    return cv.img


def _paper():
    """«TORNEM A ESTAR OBERTS», sobre transparent."""
    cv = Canvas(light=B.TEXL, transparent=True)
    PL.paper_sign(cv)
    return cv.img


PAPER_CROP = (300, 162, 390, 191)


def _cistella():
    """La cistella d'en Diu, de cara (sense la cadira del pla): vímet, la manta, la porteta de reixa oberta."""
    cv = Canvas(light=B.TEXL, transparent=True)
    cx, by = 573, 228
    for y in range(by - 19, by + 1):
        for x in range(cx - 17, cx + 18):
            nx, ny = (x - cx) / 17, (y - (by - 3)) / 16
            if y > by - 8 or nx * nx + ny * ny <= 1:
                weave = 0.8 if (x // 2 + y // 2) % 2 else -0.2
                cv.put(x, y, WICKER, 3.2 + weave - ny * 0.4 + (0.6 if x < cx - 11 else 0) - (0.8 if x > cx + 12 else 0))
    cv.hline(cx - 17, cx + 17, by - 8, WICKER, 4.6)
    cv.disc(cx - 1, by - 7, 9, 8, [(8, 6, 6), (20, 14, 10), (34, 24, 16)], lambda nx, ny: 0.6 + ny * 0.8)
    cv.poly([(cx - 11, by - 1), (cx + 8, by - 1), (cx + 12, by + 4), (cx - 13, by + 4)], BLANKET,
            lambda x, y: 2.4 + (0.8 if (x + y) % 4 == 0 else 0))
    for k in range(5):
        cv.line(cx + 11 + k * 2, by - 15 + k, cx + 11 + k * 2, by + 1, STEELB, 4.2)
    cv.hline(cx + 11, cx + 19, by - 15, STEELB, 4.6)
    cv.hline(cx + 11, cx + 19, by - 7, STEELB, 3.6)
    for a in range(200, 341, 6):
        cv.put(round(cx + math.cos(math.radians(a)) * 13), round(by - 17 + math.sin(math.radians(a)) * 9), WICKER, 4.2)
        cv.put(round(cx + math.cos(math.radians(a)) * 13), round(by - 16 + math.sin(math.radians(a)) * 9), WICKER, 2.6)
    cv.line(cx - 17, by + 1, cx + 17, by + 1, WICKER, 1.0)
    return cv.img


CIST_CROP = (555, 199, 594, 233)


def _cadira():
    cv = Canvas(light=B.TEXL, transparent=True)
    PL.table_chair(cv, 128, 229)
    return cv.img


CAD_CROP = (115, 199, 142, 262)


def _tela(kind, w, h, faldo=False, dy=0):
    """Unes estovalles, de cara (1 px = 1 unitat): de quadres vermells, de fil blanc o de paper. `faldo`: la caiguda,
    amb els plecs verticals i la vora una mica ondulada; si no, el sobre."""
    cv = Canvas(w + 1, h + 1, light=B.TEXL, transparent=True)
    for y in range(h + 1):
        for x in range(w + 1):
            if faldo:
                fold = math.sin(x * 0.41) * 0.45 + math.sin(x * 0.13 + dy) * 0.25
                if y >= h - (1 if math.sin(x * 0.34 + dy) > 0.6 else 0):
                    continue
                lv = 2.2 + fold - y * 0.02 + (0.8 if y == 0 else 0)
            else:
                lv = 2.4 + (hr(x // 5, y // 4, 6) - 0.5) * 0.3
            if kind != 'quadres':
                lv -= 0.7                                  # (el blanc i el paper, amb el sol, es cremaven)
            if kind == 'quadres':
                a, b = (x // 6) % 2, (y // 5 if faldo else y // 6) % 2
                if a and b:
                    cv.put(x, y, VICHY, lv - 0.8)
                elif a or b:
                    cv.put(x, y, VICHY, lv + 0.6)
                else:
                    cv.put(x, y, CLOTH, lv + 0.6)
            elif kind == 'fil':
                cv.put(x, y, CLOTH, lv + 0.4 + (hr(x // 2, y // 3, 3) - 0.5) * 0.15 + (0.3 if (x * 2 + y) % 11 == 0 else 0))
            else:
                cv.put(x, y, PAPER, lv + (hr(x // 3, y // 2, 4) - 0.5) * 0.3
                       - (1.4 if faldo and y > h - 3 and x % 12 == 0 else 0))
    return cv.img


@functools.lru_cache(maxsize=None)
def _textures(apagada=False):
    t = dict(B._textures())
    t.update({'fons': B._paret_fons(extra=_suport), 'facana': B._facana(dia=True), 'tele': _tele(apagada=apagada),
              'tv_box': TV, 'tv_crop': TV_CROP, 'pernil': False, 'paper': _paper(), 'cistella': _cistella(),
              'cadira': _cadira()})
    for _, _, kind, _, dy in TAULES:
        t['dalt_' + kind] = _tela(kind, 92, T_D)
        t['faldo_' + kind] = _tela(kind, 92, T_H - 4, faldo=True, dy=dy)
        t['cap_' + kind] = _tela(kind, T_D, T_H - 4, faldo=True, dy=dy + 2)
    return t


# ─── L'escena ───────────────────────────────────────────────────────────────

def _sol(x, z, y=0.0):
    """Quanta llum de sol (0..1) arriba a un punt: el raig que en surt cap a la façana passa per l'aparador o per la
    porta?"""
    t = (XR - x) / SOL[0]
    if t <= 0:
        return 0.0
    yw, zw = y + SOL[1] * t, z + SOL[2] * t
    z0, z1, y0, y1 = B.WINZ
    if z0 + 3 < zw < z1 - 3 and y0 + 3 < yw < y1 - 3 and abs(zw - (z0 + z1) / 2) > 2:
        return 0.42 * max(0.0, 1 - t / 520)
    z0, z1, y0, y1 = B.DOORZ
    if z0 + 4 < zw < z1 - 4 and yw < y1 - 4 and not 80 < yw < 85:
        return 0.48 * max(0.0, 1 - t / 520)
    return 0.0


def _damunt_barra(e, tex):
    """Damunt la barra, la festa: gerres de cervesa i cava."""
    x0, x1, zf, zb, h = B.BAR
    for gx in (B._w(238), B._w(256), B._w(451)):                       # les gerres, amb l'escuma
        e.tub('festa', (gx, h, zf + 12), (gx, h + 11, zf + 12), 3.2, BEER, 2.6)
        e.tub('festa', (gx, h + 11, zf + 12), (gx, h + 14, zf + 12), 3.2, [(200, 196, 180), (250, 248, 236)], 1.4)
    cx = B._w(360)
    e.tub('festa', (cx, h, zf + 14), (cx, h + 20, zf + 14), 3.6, BOTTLES[0], 1.6)       # el cava
    e.tub('festa', (cx, h + 20, zf + 14), (cx, h + 30, zf + 14), 1.6, BRASS, 3.0)


def _taula(e, tex):
    """La taula llarga: tres taules ajuntades, cadascuna amb les seves estovalles i una mica girada."""
    x0, z0, a = TAULA
    for lx0, lx1, kind, da, dy in TAULES:
        ang = a + da
        cx_, _, cz_ = _l((lx0 + lx1) / 2, 0)
        w = lx1 - lx0
        h = T_H + dy

        def P(lx, y, lz):
            return _l(lx, lz, y, ang, cx_, cz_)
        # l'ombra i les potes (només en surt la punta per sota les estovalles)
        e.foscor('ombra_taula', P(-w / 2 - 6, 0.6, T_D / 2 + 4), P(w / 2 + 6, 0.6, T_D / 2 + 4),
                 P(w / 2 + 6, 0.6, -T_D / 2 - 10), P(-w / 2 - 6, 0.6, -T_D / 2 - 10),
                 lambda s, t, w=w: 0.5 * min(1.0, t / 8) * min(1.0, s / 8, (w + 12 - s) / 8))
        for lx in (-w / 2 + 4, w / 2 - 4):
            for lz in (-T_D / 2 + 4, T_D / 2 - 4):
                px_, _, pz_ = P(lx, 0, lz)
                e.caixa('taula', px_ - 1.2, px_ + 1.2, 0, 6, pz_ - 1.2, pz_ + 1.2, STEELB if kind == 'paper' else WOOD, 1.6)
        # el sobre i les caigudes de les estovalles (el davant i els caps)
        hm = 5
        dalt = tex['dalt_' + kind]
        e.quad('taula', P(-w / 2, h, T_D / 2), P(w / 2, h, T_D / 2), P(w / 2, h, -T_D / 2), P(-w / 2, h, -T_D / 2),
               tex=(dalt, (0, 0, w, T_D)))
        fal, cap = tex['faldo_' + kind], tex['cap_' + kind]
        e.quad('taula', P(-w / 2, h, -T_D / 2), P(w / 2, h, -T_D / 2), P(w / 2, hm, -T_D / 2), P(-w / 2, hm, -T_D / 2),
               tex=(fal, (0, 0, w, fal.height - 1)))
        e.quad('taula', P(-w / 2, h, T_D / 2), P(-w / 2, h, -T_D / 2), P(-w / 2, hm, -T_D / 2), P(-w / 2, hm, T_D / 2),
               tex=(cap, (0, 0, T_D, cap.height - 1)))
        e.quad('taula', P(w / 2, h, -T_D / 2), P(w / 2, h, T_D / 2), P(w / 2, hm, T_D / 2), P(w / 2, hm, -T_D / 2),
               tex=(cap, (0, 0, T_D, cap.height - 1)))
        if kind == 'fil':                       # «TORNEM A ESTAR OBERTS», enganxat amb cinta a les estovalles
            pw, ph = 84, 27
            e.quad('taula', P(-pw / 2, 40, -T_D / 2 - 0.6), P(pw / 2, 40, -T_D / 2 - 0.6), P(pw / 2, 40 - ph, -T_D / 2 - 0.6),
                   P(-pw / 2, 40 - ph, -T_D / 2 - 0.6), tex=(tex['paper'], PAPER_CROP))
    # damunt: gots, ampolles, plats de pa amb tomàquet, el porró i tovallons
    for i, lx in enumerate((-124, -100, -62, -30, 8, 30, 62, 96, 124)):
        P0 = _l(lx, -6 + (i % 3) * 5, T_H)
        if i in (1, 5):                                                 # pa amb tomàquet
            pc = P0
            e.quad('damunt', (pc[0] - 11, pc[1] + 0.4, pc[2] + 6), (pc[0] + 11, pc[1] + 0.4, pc[2] + 6),
                   (pc[0] + 11, pc[1] + 0.4, pc[2] - 6), (pc[0] - 11, pc[1] + 0.4, pc[2] - 6), ramp=PORC,
                   lvl=lambda s, t, P: 4.2 - t * 0.05, forma=lambda s, t: ((s - 11) / 11) ** 2 + ((t - 6) / 6) ** 2 <= 1)
            for k in range(3):
                bx, bz = pc[0] - 6 + k * 5, pc[2] - 1 + (k % 2) * 2
                e.caixa('damunt', bx - 2, bx + 2, pc[1] + 0.4, pc[1] + 2, bz - 2.5, bz + 2.5, BREAD, 3.0,
                        cares={'dalt': {'ramp': TOMATO, 'lvl': lambda s, t, P: 2.4 + (0.6 if (int(s * 3) + int(t * 2)) % 3 == 0 else 0)}})
        elif i in (2, 6, 8):                                            # ampolles
            r = BOTTLES[(1, 0, 3)[(2, 6, 8).index(i)]]
            e.tub('damunt', P0, (P0[0], P0[1] + 16, P0[2]), 2.6, r, 1.8)
            e.tub('damunt', (P0[0], P0[1] + 16, P0[2]), (P0[0], P0[1] + 22, P0[2]), 1.1, r, 1.8)
        elif i == 4:                                                    # el porró
            e.tub('damunt', P0, (P0[0], P0[1] + 9, P0[2]), 4.4, [(40, 10, 20), (90, 20, 40), (160, 70, 90), (220, 200, 210)], 1.8)
            e.tub('damunt', (P0[0], P0[1] + 9, P0[2]), (P0[0], P0[1] + 17, P0[2]), 1.2, SHEET, 3.0)
            e.tub('damunt', (P0[0] + 2, P0[1] + 6, P0[2]), (P0[0] + 10, P0[1] + 13, P0[2] - 2), 0.8, SHEET, 3.2)
        else:                                                           # gots (de cervesa i d'aigua)
            ramp = BEER if i % 2 else [(70, 80, 90), (130, 150, 160), (190, 210, 220), (236, 244, 250)]
            e.tub('damunt', P0, (P0[0], P0[1] + 9, P0[2]), 2.4, ramp, 2.4)
            e.tub('damunt', (P0[0], P0[1] + 9, P0[2]), (P0[0], P0[1] + 10, P0[2]), 2.4, SHEET, 4.0)
    for lx in (-86, 20, 78):                                            # tovallons
        P0 = _l(lx, -12, T_H + 0.5)
        e.quad('damunt', (P0[0] - 4, P0[1], P0[2] + 3), (P0[0] + 4, P0[1], P0[2] + 4), (P0[0] + 5, P0[1], P0[2] - 3),
               (P0[0] - 3, P0[1], P0[2] - 4), ramp=SHEET, lvl=4.4)


def escena(cv, tex, estat=frozenset()):
    tex = dict(tex)
    e = B.escena(cv, tex, estat, dia=True, llums=LLUMS, primer_pla=False,
                 damunt=lambda e_: _damunt_barra(e_, tex))
    # el sol de la tarda pel terra, en diagonal
    e.claror((B.XL, 0.4, ZW), (XR, 0.4, ZW), (XR, 0.4, CAM.pos[2] + 60), (B.XL, 0.4, CAM.pos[2] + 60), (255, 214, 150),
             lambda s, t: _sol(B.XL + s, ZW - t))
    # el moble baix al costat de la porta, amb la regleta, i el cable de la tele que hi baixa
    mx0, mx1, mz0, mz1, mh = MOBLE
    e.foscor('ombra_moble', (mx0 - 10, 0.6, mz1 + 4), (XR, 0.6, mz1 + 4), (XR, 0.6, mz0 - 12), (mx0 - 10, 0.6, mz0 - 12),
             lambda s, t: 0.5 * min(1.0, s / 10, t / 10))
    e.caixa('moble', mx0, mx1, 0, mh, mz0, mz1, WOOD, 2.4,
            cares={'davant': {'ramp': WOOD, 'lvl': lambda s, t, P: 2.2 + (0.8 if t < 2 else 0) - (0.8 if abs(t - 20) < 1 else 0)},
                   'esquerra': {'ramp': WOOD, 'lvl': lambda s, t, P: 2.8 - (0.8 if abs(t - 20) < 1 else 0)},
                   'dalt': {'ramp': WOOD, 'lvl': 3.6}})
    rx, rz = REGLETA
    e.caixa('moble', rx - 3, rx + 3, mh, mh + 3, rz - 12, rz + 12, PLASTIC, 3.6)
    e.caixa('moble', mx0 + 8, mx0 + 26, mh, mh + 4, mz1 - 22, mz1 - 4, SHEET, 3.4)                # diaris
    tx1, ty0 = TV[1], TV[2]
    e.cable('cable_tele', [(tx1 - 10, ty0, TV[4] + 2), (tx1 - 6, ty0 - 30, ZW - 1), (XR - 4, 30, ZW - 3),
                           (XR - 2, 1, ZW - 20), (XR - 2, 1, mz1 + 6), (mx1 - 2, mh + 1, mz1 - 2), (rx, mh + 2, rz + 8)],
            SLATE, 1.4, gruix=1.2)
    # la cadira de la punta de l'esquerra i la taula llarga
    pc = _l(-162, 14)
    e.sprite('cadira', tex['cadira'].crop(CAD_CROP), (128 - CAD_CROP[0], 261 - CAD_CROP[1]), pc)
    _taula(e, tex)
    # la cistella d'en Diu, damunt un tamboret baix de fusta, a la punta de la dreta
    cx, cz, ch = CISTELLA
    e.foscor('ombra_cistella', (cx - 20, 0.6, cz + 16), (cx + 22, 0.6, cz + 16), (cx + 22, 0.6, cz - 18), (cx - 20, 0.6, cz - 18),
             lambda s, t: 0.5 * max(0.0, 1 - ((s - 21) / 21) ** 2 - ((t - 17) / 17) ** 2) * 1.5)
    e.caixa_girada('tamboret', cx, cz, 34, 30, ch, -0.3, WOOD, 2.4,
                   cares={'dalt': {'ramp': WOOD, 'lvl': lambda s, t, P: 3.4 + (0.5 if int(s) % 8 == 0 else 0)},
                          'davant': {'ramp': WOOD, 'lvl': 2.2}, 'esquerra': {'ramp': WOOD, 'lvl': 2.8}})
    e.sprite('cistella', tex['cistella'].crop(CIST_CROP), (573 - CIST_CROP[0], 232 - CIST_CROP[1]), (cx, ch, cz))
    B._primer_pla(e)
    return e


# ─── Composició i llum ──────────────────────────────────────────────────────

def _proj(P):
    u, v, _ = CAM.projecta(P)
    return u, v


def _fx():
    wx, wy = _proj((XR, 140, (B.WINZ[0] + B.WINZ[1]) / 2))
    dx, dy = _proj((XR, 70, (B.DOORZ[0] + B.DOORZ[1]) / 2))
    tx, ty = _proj(((TV[0] + TV[1]) / 2, (TV[2] + TV[3]) / 2, TV[4]))
    light = [llum.wash(wx, wy + 40, 240, (255, 210, 140), k=0.25, air=0.03, squash=0.8),       # el sol de l'aparador
             llum.wash(dx, dy + 40, 240, (255, 210, 140), k=0.25, air=0.03, squash=0.8),       # i el de la porta
             llum.wash(tx, ty, 90, (90, 140, 220), k=0.4, air=0.03)]                           # la tele
    tone = [llum.grade(contrast=1.06, pivot=70, sat=1.1, lift=(6, 4, 2))]
    s0, s1 = _proj((B.SIGN[0], B.SIGN[3] + 4, ZW)), _proj((B.SIGN[1], B.SIGN[2] - 4, ZW))
    bloom = [llum.bloom(thr=190, mask=lambda x, y: 1 - 0.9 * ((x > s0[0]) & (x < s1[0]) & (y > s0[1]) & (y < s1[1])))]
    return light, bloom, tone


def _render(tex=None):
    cv = Canvas(light=LIGHT)
    e = escena(cv, tex or _textures())
    cv.rect(0, BOTTOM + 1, W - 1, H - 1, [(0, 0, 0)], 0, lit=0)
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


def tele_apagada(cv):
    """La tele, apagada (en Diu ha mossegat el cable): la pantalla negra amb un reflex, projectada a la caixa."""
    _, e = _base()
    capa = e.capa(_tele(apagada=True), {'tele'})
    img = _base()[0].copy()
    img.alpha_composite(capa)
    cv.img.alpha_composite(_diff(_amb_llum(img, bloom=False), _amb_llum(_base()[0], bloom=False)))
    cv.P = cv.img.load()


PROPS = {'tele_apagada': tele_apagada}


def _frames():
    _, e = _base()
    out = []
    for i in range(16):
        img = _base()[0].copy()
        img.alpha_composite(e.capa(_tele(i), {'tele'}))
        img.alpha_composite(e.capa(B._escurabutxaques(i), {'escurabutxaques'}))
        out.append(_diff(_amb_llum(img), _base_llum()))
    return out


ANIMS = {'tele': {'frames': _frames, 'frameDuration': 260}}


# ─── Capes del davant i geometria ───────────────────────────────────────────

def _amo(ids):
    def mask(x, y):
        _, e = _base()
        return e.ids[e.amo[y * e.cv.w + x]] in ids
    return mask


def _p(x, z, y=0.0):
    u, v, _ = CAM.projecta((x, y, z))
    return round(u), round(v)


def _pl(lx, lz, y=0.0):
    P = _l(lx, lz, y)
    return _p(P[0], P[2], P[1])


# La taula (amb el que hi ha damunt) tapa les cames de qui hi seu al darrere: la línia base, el cantell del davant de
# les estovalles a terra (la taula és gairebé de cara a la càmera: una sola línia). La cadira de l'esquerra, també.
_BASE_TAULA = min(_pl(lx, -T_D / 2)[1] for lx in range(-138, 139, 6)) - 2
FRONT = [{'id': 'davant', 'mask': _amo({'taula', 'damunt', 'cadira', 'primer_pla'}), 'baseline': _BASE_TAULA,
          'zIndex': 20}]

_SEU = {c: _pl(lx, SEU) for c, lx in SEIENTS.items()}
_V_FONS = min(v for _, v in _SEU.values()) - 30

GEOMETRIA = {
    'things': {},
    'spawns': {**_SEU, 'neta': _p(*NETA), 'diu': _p(CISTELLA[0], CISTELLA[1], CISTELLA[2])},
    'walkable': [_pl(-130, SEU - 6), _pl(130, SEU - 6), _pl(130, SEU + 6), _pl(-130, SEU + 6)],
    'floorSquash': 0.42,
    # el sol de la tarda entra per la façana (a la dreta): les ombres cauen cap a l'esquerra i una mica endavant
    'characterShadow': {'enabled': True, 'color': '#2a1a10', 'alpha': 0.4, 'squash': 0.4, 'core': 0.6,
                        'light': {'x': -1, 'y': 0.25, 'direction': True, 'stretch': 0.6}},
    'regions': [{'id': 'perspectiva', 'active': True, 'scaleEnabled': True, 'scaleWalkSpeed': True,
                 'scaleTop': round(B._escala_a(_V_FONS), 3), 'scaleBottom': round(B._escala_a(BOTTOM), 3),
                 'points': [(0, _V_FONS), (W - 1, _V_FONS), (W - 1, BOTTOM), (0, BOTTOM)]}],
    'characterLights': {
        'ambient': '#d8ccb8',                                                          # la tarda, càlida
        'lights': [
            {'x': _p(XR, 90, 120)[0], 'y': _p(XR, 90, 120)[1], 'radius': 420, 'color': '#ffd896', 'intensity': 0.8},
            {'x': _p((TV[0] + TV[1]) / 2, TV[4], (TV[2] + TV[3]) / 2)[0],
             'y': _p((TV[0] + TV[1]) / 2, TV[4], (TV[2] + TV[3]) / 2)[1], 'radius': 110, 'color': '#5a8cdc',
             'intensity': 0.5},
        ],
    },
}
