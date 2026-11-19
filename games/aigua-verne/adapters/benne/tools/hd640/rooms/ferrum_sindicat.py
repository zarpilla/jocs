"""
Aigua Verne — `ferrum_sindicat` (P): el local del sindicat miner de Ferrum (el despatx d'en Bru). EN 3D
(hd640/tres_d.py), a 1×.

Una sala baixa i fumada, vista de biaix i una mica des de dalt: la paret de la **porta** del carrer (amb el penjador de
cascs) fuig cap al fons a l'esquerra, i a la paret del fons hi ha els **cartells** de vagues antigues i la
**pissarra** amb els torns de l'aigua. Davant la paret, separats i girats: el **bagul** de la colla de teatre, obert,
amb la tapa aixecada; la prestatgeria dels **motlles**; l'estufa de ferro colat, amb el tub que puja i se'n va per la
paret. Al mig, la taula llarga de les assemblees, girada, amb els bancs; la bombeta amb pantalla de llauna hi fa un
bassal de llum. Les bigues del sostre fugen cap al fons. Primer pla: el pilar de fusta de la dreta i una cadira, a
l'esquerra, en silueta.

Tot el detall ve del local pla de sempre (ferrum_sindicat_pla_comu.py): la paret, la porta, els cartells, la pissarra,
el bagul, els motlles i l'estufa es dibuixen de cara i es projecten. Decorat (PROPS): `vestit` (a dalt del bagul: es
veu fins que l'Iri l'agafa). ANIMS: `estufa` (el foc de l'estufa, per la reixeta).

El món: x a la dreta (0 = la paret de la porta), y amunt (0 = el terra), z cap al fons (300 = la paret del fons);
1 unitat = 1 píxel de sala on un personatge fa la seva mida normal (escala 1).
"""
import functools
import math

import hd640  # noqa: F401  (abans que cap hd.rooms: posa la llibreria a 640×360)

from hd.pix import Canvas, Light, W, H, hr
from hd.rooms.exterior import fbm
from hd640.rooms import ferrum_sindicat_pla_comu as PL
from hd640.rooms.ferrum_comu import COAL, IRONF, TIN, HELM, brick_lvl
from hd640.tres_d import Camera, Escena, Llum, llum_personatges

BOTTOM = 259
ZW = 300                                           # la paret del fons
HW = 200                                           # l'alçada del sostre (el pla: la paret de y 14 a 214)
FY0, FY1 = 14, 214                                 # la paret, al pla
XL = 124                                           # al pla, la cantonada: a l'esquerra, la paret de la porta
TAULA = (176.0, 170.0, 176.0, 54.0, 62.0, -0.22)   # centre (x, z), llarg, ample, alçada, gir
BAGUL = (346.0, 258.0, 0.32)                       # centre (x, z), gir
MOTLLES = (352.0, 446.0)                           # la prestatgeria, contra la paret del fons (x0, x1)
ESTUFA = (518.0, 226.0)                            # el peu de l'estufa (x, z)
LAMP = (192.0, 146.0)                              # la bombeta, sobre la taula (x, z)

CAM = Camera(pos=(300, 190, -200), yaw=-0.14, pitch=0.17, f=380, centre=(330, 70))

LIGHT = Light(ambient=0.0, vignette=None, floor_fade=None)       # (la llum és la del món: la de l'Escena)
LLUMS = [Llum((LAMP[0], 140, LAMP[1]), 280, 2.6, power=1.2),       # la bombeta
         Llum((ESTUFA[0] - 6, 40, ESTUFA[1] - 20), 130, 1.4, power=1.6),   # el foc de l'estufa
         Llum((10, 120, 232), 120, 0.6, power=1.4)]                 # la claror del vidre de la porta
AMBIENT = -0.15
TEXL = Light(ambient=0.2, vignette=None, floor_fade=None)        # la llum de les textures planes (neutra)


# ─── Les textures: el local pla de sempre ─────────────────────────────────────

def _pla(fn, transparent=True):
    cv = Canvas(light=TEXL, transparent=transparent)
    fn(cv)
    return cv.img


def _paret_pla(cv):
    PL.paret(cv)
    PL.porta(cv)
    PL.cartells(cv)
    PL.pissarra(cv)


@functools.lru_cache(maxsize=None)
def _textures():
    return {
        'paret': _pla(_paret_pla, transparent=False),
        'bagul': _pla(PL.bagul),
        'motlles': _pla(PL.motlles),
        'estufa': _pla(lambda cv: PL.estufa(cv, tub=False)),
        'bombeta': _pla(PL.bombeta),
    }


# ─── Utilitats ──────────────────────────────────────────────────────────────

def _p(x, z, y=0.0):
    u, v, _ = CAM.projecta((x, y, z))
    return round(u), round(v)


def _rect_mon(*Ps):
    pts = [CAM.projecta(P) for P in Ps]
    return (max(0, round(min(p[0] for p in pts))), max(0, round(min(p[1] for p in pts))),
            min(W - 1, round(max(p[0] for p in pts))), min(BOTTOM, round(max(p[1] for p in pts))))


def _fons(fx, fy):
    """Un punt del pla (la paret del fons) al món."""
    return (fx - XL, HW - (fy - FY0), ZW)


def _esq(fx, fy):
    """Un punt del pla (la paret de la porta) al món."""
    return (0, HW - (fy - FY0), ZW - XL + fx)


def _gira(cx, cz, ang, lx, lz):
    c, s = math.cos(ang), math.sin(ang)
    return cx + lx * c - lz * s, cz + lx * s + lz * c


# ─── Les superfícies ────────────────────────────────────────────────────────

def _guix(lvl0=3.4, seed=3):
    """La paret de guix verd on el pla no arriba: es pela i a sota hi ha el maó."""
    def L(s, t, P):
        peel = fbm(s / 26, t / 18, seed)
        if peel > 0.73:
            return brick_lvl(int(s), int(t), 0, 0, 10, 4, 3.4, 5) - 0.6
        v = lvl0 + (fbm(s / 60, t / 40, 4) - 0.5) * 1.4 - 0.8 * fbm(s / 12, t / 50, 6) ** 3 * 3
        return v - max(0.0, 1 - t / 40) * 1.0
    return L


def _arrambador(s, t, P):
    """L'arrambador de fusta (posts verticals) i la motllura de dalt."""
    if P[1] > 55:
        return 4.6 - (P[1] - 55) * 0.6
    return 3.0 - (1.4 if int(s) % 13 == 0 else 0) + (fbm(s / 4, P[1] / 30, 7) - 0.5) * 1.0 - (1.6 if P[1] < 3 else 0)


def paret_proc(e, sid, P0, P1, seed):
    """Un tros de paret procedural (P0 a dalt a l'esquerra, P1 a dalt a la dreta): guix a dalt, arrambador a baix."""
    a0, a1 = (P0[0], 59, P0[2]), (P1[0], 59, P1[2])
    e.quad(sid, P0, P1, a1, a0, ramp=PL.PLASTER, lvl=_guix(3.3, seed))
    e.quad(sid, a0, a1, (P1[0], 0, P1[2]), (P0[0], 0, P0[2]), ramp=PL.WOOD, lvl=_arrambador)


def _taulons(s, t, P):
    """Terra de taulons gastats, en coordenades del món: les juntes amb pols de carbó, gastat on es trepitja."""
    x, z = P[0], P[2]
    plank = int(x // 22)
    joint = x % 22 < 1.2
    cut = (z + hr(plank, 2) * 160) % 160 < 1.2
    v = 3.0 + (hr(plank, 1) - 0.5) * 0.8 + (fbm(x / 40, z / 6, plank) - 0.5) * 0.8
    if joint or cut:
        v -= 1.8
    elif x % 22 < 2.6:
        v += 0.4
    v += max(0.0, 1 - math.hypot(x - 230, (z - 120) * 1.4) / 200) * 0.5          # gastat al mig
    return v


def taula(e):
    cx, cz, L, A, Ht, ang = TAULA
    # l'ombra, sota (la bombeta és just a sobre: l'ombra és rodona, sota mateix)
    a = (L / 2 + 16, A / 2 + 16)
    P0 = _gira(cx, cz, ang, -a[0], a[1])
    P1 = _gira(cx, cz, ang, a[0], a[1])
    P2 = _gira(cx, cz, ang, a[0], -a[1])
    P3 = _gira(cx, cz, ang, -a[0], -a[1])
    e.foscor('ombres', (P0[0], 0.6, P0[1]), (P1[0], 0.6, P1[1]), (P2[0], 0.6, P2[1]), (P3[0], 0.6, P3[1]),
             lambda s, t: 0.6 * min(1.0, min(s, t, 2 * a[0] - s, 2 * a[1] - t) / 18))
    # el banc de darrere i el de davant
    for side in (-1,):                                              # (el banc de darrere, en Bru el té apartat)
        bx, bz = _gira(cx, cz, ang, 0, side * (A / 2 + 16))
        for lx in (-L / 2 + 20, L / 2 - 20):
            px, pz = _gira(bx, bz, ang, lx, 0)
            e.caixa_girada('bancs', px, pz, 6, 18, 34, ang, PL.WOOD, 2.0)
        e.caixa_girada('bancs', bx, bz, L - 20, 20, 5, ang, PL.WOOD, 3.0, y0=34,
                       cares={'dalt': {'ramp': PL.WOOD, 'lvl': lambda s, t, P: 4.2 - (1.0 if t % 10 < 1 else 0)}})
    # les potes i el sobre de taulons
    for lx, lz in ((-L / 2 + 8, -A / 2 + 6), (L / 2 - 8, -A / 2 + 6), (-L / 2 + 8, A / 2 - 6), (L / 2 - 8, A / 2 - 6)):
        px, pz = _gira(cx, cz, ang, lx, lz)
        e.caixa_girada('taula', px, pz, 7, 7, Ht - 6, ang, PL.WOOD, 2.2)
    papers = ((-80, -8, 26, 16), (-50, 6, 20, 14), (40, -6, 28, 18))

    def sobre(s, t, P):
        for px, pz, w, d in papers:
            if abs(s - L / 2 - px) < w / 2 and abs(t - A / 2 - pz) < d / 2:
                return 5.0 - (0.8 if int(t) % 3 == 0 and abs(s - L / 2 - px) < w / 2 - 2 else 0)
        return 3.6 + (fbm(s / 30, t / 3, 61) - 0.5) * 0.8 - (1.0 if t % 11 < 1 else 0)
    e.caixa_girada('taula', cx, cz, L, A, 6, ang, PL.WOOD, 3.0, y0=Ht - 6,
                   cares={'dalt': {'ramp': PL.WOOD, 'lvl': lambda s, t, P: sobre(s, A - t, P)},
                          'davant': {'ramp': PL.WOOD, 'lvl': 2.4}, 'esquerra': {'ramp': PL.WOOD, 'lvl': 2.0},
                          'dreta': {'ramp': PL.WOOD, 'lvl': 1.8}})
    # damunt: dues tasses de llauna, el cendrer i un casc
    for lx, lz in ((-18, 8), (70, -10)):
        px, pz = _gira(cx, cz, ang, lx, lz)
        e.caixa_girada('taula', px, pz, 6, 6, 8, ang, TIN, 4.0, y0=Ht)
    px, pz = _gira(cx, cz, ang, 10, 4)
    e.caixa_girada('taula', px, pz, 12, 12, 2, ang, IRONF, 3.0, y0=Ht)
    px, pz = _gira(cx, cz, ang, 96, 6)
    e.roca('taula_casc', (px, Ht, pz), 9, HELM, 3.4, llum_dir=(-0.6, -0.8), aplana=0.75, seed=4)


def bagul(e, tex):
    """El bagul: una caixa girada amb el davant del pla, la boca (dalt) i la tapa oberta, aixecada cap enrere."""
    x0, x1, base = PL.CHEST
    top = base - 34
    back = top - 8
    lt = back - 36
    cx, cz, ang = BAGUL
    w, d, h = x1 - x0 + 1, 46.0, 34.0
    T = tex['bagul']
    e.foscor('ombres', (cx - 70, 0.6, cz + 40), (cx + 70, 0.6, cz + 40), (cx + 70, 0.6, cz - 40), (cx - 70, 0.6, cz - 40),
             lambda s, t: 0.55 * max(0.0, 1 - ((s - 70) / 62) ** 2 - ((t - 40) / 34) ** 2) * 1.4)
    e.caixa_girada('bagul', cx, cz, w, d, h, ang, PL.TRUNK, 2.6,
                   cares={'davant': {'tex': (T, (x0, top, x1 + 1, base + 1))},
                          'dalt': {'tex': (T, (x0 + 2, back, x1 - 1, top))},
                          'esquerra': {'ramp': PL.TRUNK, 'lvl': lambda s, t, P: 2.4 - (1.2 if t % 11 < 1 else 0)
                                       + (1.2 if abs(t - 5) < 1 or abs(t - 28) < 1 else 0)},
                          'dreta': {'ramp': PL.TRUNK, 'lvl': lambda s, t, P: 2.0 - (1.2 if t % 11 < 1 else 0)}})
    # la tapa, oberta: frontissa a la vora de darrere, aixecada i una mica tirada enrere
    hl = 38.0
    tilt = 0.28
    bL = _gira(cx, cz, ang, -w / 2, d / 2)
    bR = _gira(cx, cz, ang, w / 2, d / 2)
    off = _gira(0, 0, ang, 0, hl * math.sin(tilt))
    e.quad('bagul_tapa', (bL[0] + off[0], h + hl * math.cos(tilt), bL[1] + off[1]),
           (bR[0] + off[0], h + hl * math.cos(tilt), bR[1] + off[1]), (bR[0], h, bR[1]), (bL[0], h, bL[1]),
           tex=(T, (x0 + 2, lt, x1 - 1, back)), dues_cares=True)


def motlles(e, tex):
    x0, x1 = MOTLLES
    d = 34
    e.foscor('ombres', (x0 - 10, 0.6, ZW), (x1 + 30, 0.6, ZW), (x1 + 30, 0.6, ZW - d - 20), (x0 - 10, 0.6, ZW - d - 20),
             lambda s, t: 0.5 * max(0.0, 1 - max(0.0, t - d) / 20) * min(1.0, (x1 + 30 - x0 - s) / 30 + 0.3))
    e.caixa('motlles', x0, x1, 0, 181, ZW - d, ZW - 1, PL.WOOD, 2.4,
            cares={'davant': {'tex': (tex['motlles'], (476, 36, 571, 217))},
                   'esquerra': {'ramp': PL.WOOD, 'lvl': lambda s, t, P: 2.6 - (0.6 if t % 42 < 3 else 0)},
                   'dalt': {'ramp': PL.WOOD, 'lvl': 3.6}})


def estufa(e, tex):
    """L'estufa (el dibuix pla, dret) amb la planxa a terra, i el tub que puja i se'n va per la paret."""
    sx, sz = ESTUFA
    cx, base = PL.STOVE
    e.foscor('ombres', (sx - 50, 0.6, sz + 30), (sx + 40, 0.6, sz + 30), (sx + 40, 0.6, sz - 30), (sx - 50, 0.6, sz - 30),
             lambda s, t: 0.45 * max(0.0, 1 - ((s - 45) / 44) ** 2 - ((t - 30) / 26) ** 2) * 1.4)
    e.sprite('estufa', tex['estufa'].crop((cx - 44, base - 74, cx + 28, base + 6)), (44, 74), (sx, 0, sz))
    top = (sx, 74, sz + 2)
    e.tub('estufa_tub', top, (sx, 168, sz + 2), 4.2, IRONF, 2.8, brides=40)
    e.tub('estufa_tub', (sx, 168, sz + 2), (sx, 168, ZW - 1), 4.2, IRONF, 2.8, brides=30)
    e.foscor('ombres', (sx - 24, 186, ZW - 0.5), (sx + 24, 186, ZW - 0.5), (sx + 24, 150, ZW - 0.5), (sx - 24, 150, ZW - 0.5),
             lambda s, t: 0.5 * max(0.0, 1 - math.hypot(s - 24, t - 18) / 24))     # el sutge on entra a la paret


def sostre(e):
    zn = CAM.pos[2] - 100
    e.quad('sostre', (-50, HW, zn), (W + 200, HW, zn), (W + 200, HW, ZW), (-50, HW, ZW), ramp=PL.WOOD,
           lvl=lambda s, t, P: 1.0 - (0.8 if P[0] % 20 < 1.2 else 0) + (fbm(P[0] / 30, P[2] / 8, 2) - 0.5) * 0.6,
           dues_cares=True)
    for bx in range(30, W + 200, 110):                              # les bigues, que fugen cap al fons
        e.caixa('bigues', bx - 9, bx + 9, HW - 16, HW, zn, ZW, PL.WOOD, 2.2,
                cares={'sota': {'ramp': PL.WOOD, 'lvl': lambda s, t, P: 2.0 + (fbm(s / 4, t / 30, 9) - 0.5) * 0.8},
                       'esquerra': {'ramp': PL.WOOD, 'lvl': 2.8}, 'dreta': {'ramp': PL.WOOD, 'lvl': 1.4}})
    e.caixa('bigues', -50, W + 200, HW - 20, HW, ZW - 14, ZW, PL.WOOD, 2.0,
            cares={'sota': {'ramp': PL.WOOD, 'lvl': 1.6}, 'davant': {'ramp': PL.WOOD, 'lvl': 1.8}})


def bombeta(e, tex):
    lx, lz = LAMP
    e.linia((lx, HW, lz), (lx, 150, lz), COAL, 1.4)
    x, y = PL.LAMP
    e.sprite('bombeta', tex['bombeta'].crop((x - 30, y, x + 30, y + 20)), (30, 0), (lx, 150, lz))


def primer_pla(e):
    # el pilar de fusta, a la dreta, molt a prop (tallat per la vora)
    e.caixa('primer_pla', 432, 456, 0, HW, 26, 50, PL.WOOD, 1.6,
            cares={'esquerra': {'ramp': PL.WOOD, 'lvl': lambda s, t, P: 1.6 + (fbm(s / 3, t / 30, 3) - 0.5) * 1.0
                                + (0.8 if s > 18 else 0)},
                   'davant': {'ramp': PL.WOOD, 'lvl': 1.0}})
    e.caixa('primer_pla', 400, 490, HW - 22, HW, 26, 50, PL.WOOD, 1.2)                       # la sabata del pilar
    # una cadira, a l'esquerra, de biaix: el seient i el respatller
    cx, cz, ang = 96.0, 12.0, 0.5
    for lx, lz in ((-14, -12), (14, -12), (-14, 12), (14, 12)):
        px, pz = _gira(cx, cz, ang, lx, lz)
        e.caixa_girada('primer_pla', px, pz, 4, 4, 44, ang, PL.WOOD, 1.0)
    e.caixa_girada('primer_pla', cx, cz, 34, 32, 4, ang, PL.WOOD, 1.6, y0=44,
                   cares={'dalt': {'ramp': PL.WOOD, 'lvl': 2.4}})
    bx, bz = _gira(cx, cz, ang, 0, 16)
    for lx in (-14, 14):
        px, pz = _gira(bx, bz, ang, lx, 0)
        e.caixa_girada('primer_pla', px, pz, 4, 4, 46, ang, PL.WOOD, 1.0, y0=44)
    e.caixa_girada('primer_pla', bx, bz, 32, 4, 12, ang, PL.WOOD, 1.4, y0=76)
    # el marc de la porta per on mirem, molt a prop a l'esquerra (tallat per la vora), amb la fulla oberta cap a
    # nosaltres i un casc penjat del brancal: tot en silueta
    jx, jz = 166, -60
    e.caixa('primer_pla', jx - 14, jx, 0, HW + 80, jz - 8, jz + 8, PL.WOOD, 1.2,
            cares={'dreta': {'ramp': PL.WOOD, 'lvl': lambda s, t, P: 1.8 + (fbm(s / 2, t / 30, 17) - 0.5) * 0.8
                             + (0.6 if s > 13 else 0)}})
    a_ = 2.2                                                        # la fulla, oberta cap a la càmera
    lx, lz = jx - 14 + math.cos(a_) * 90, jz + math.sin(a_) * -90
    e.quad('primer_pla', (jx - 14, HW + 40, jz), (lx, HW + 40, lz), (lx, 0, lz), (jx - 14, 0, jz), ramp=PL.WOOD,
           dues_cares=True, lvl=lambda s, t, P: 1.0 - (0.6 if s % 18 < 1.5 else 0) + (fbm(s / 4, t / 20, 19) - 0.5) * 0.5)
    e.cable('primer_pla', [(jx + 1, 120, jz - 4), (jx + 6, 118, jz - 4)], IRONF, 2.0, gruix=1.6)
    e.roca('primer_pla', (jx + 10, 100, jz - 4), 11, HELM, 1.6, llum_dir=(0.6, -0.4), aplana=0.7, seed=5)


def escena(cv, tex):
    """Tota la sala, de lluny a prop."""
    e = Escena(cv, CAM, LLUMS, ambient=AMBIENT)
    zn = CAM.pos[2] - 100
    paret = tex['paret']
    # la paret de la porta (x = 0): de prop, guix procedural; cap a la cantonada, el pla (x 0..124)
    paret_proc(e, 'paret_esq_prop', (0, HW, zn), (0, HW, ZW - XL), 8)
    e.quad('paret_esq', (0, HW, ZW - XL), (0, HW, ZW), (0, 0, ZW), (0, 0, ZW - XL), tex=(paret, (0, FY0, XL, FY1)))
    # la paret del fons (z = 300): el pla (x 124..640) i, a la dreta, més guix
    e.quad('paret_fons', (0, HW, ZW), (W - XL, HW, ZW), (W - XL, 0, ZW), (0, 0, ZW), tex=(paret, (XL, FY0, W, FY1)))
    paret_proc(e, 'paret_fons_dreta', (W - XL, HW, ZW), (W + 200, HW, ZW), 9)
    # el terra
    e.quad('terra', (0, 0, ZW), (W + 200, 0, ZW), (W + 200, 0, zn), (0, 0, zn), ramp=PL.FLOORB, lvl=_taulons)
    e.foscor('racons', (0, 0.5, ZW), (W + 200, 0.5, ZW), (W + 200, 0.5, zn), (0, 0.5, zn),
             lambda s, t: max(0.6 * max(0.0, 1 - t / 26), 0.55 * max(0.0, 1 - s / 24)))
    e.foscor('cantonada', (0, HW, ZW - 0.5), (40, HW, ZW - 0.5), (40, 0, ZW - 0.5), (0, 0, ZW - 0.5),
             lambda s, t: 0.5 * max(0.0, 1 - s / 40))
    e.foscor('cantonada', (0.5, HW, ZW - 40), (0.5, HW, ZW), (0.5, 0, ZW), (0.5, 0, ZW - 40),
             lambda s, t: 0.5 * max(0.0, 1 - (40 - s) / 40))
    # la claror freda del vidre de la porta, que s'escampa en diagonal pel terra
    dz0, dz1 = ZW - XL + 26, ZW - XL + 86
    e.claror((0, 0.4, dz1 + 10), (130, 0.4, dz1 + 50), (130, 0.4, dz0 - 60), (0, 0.4, dz0 - 4), (170, 180, 190),
             lambda s, t: 0.28 * max(0.0, 1 - s / 130) ** 1.2 * max(0.0, math.sin(math.pi * min(1.0, t / max(1.0, 70 + 0.8 * s)))))
    # la llum càlida de l'estufa, a terra
    sx, sz = ESTUFA
    e.claror((sx - 90, 0.5, sz + 60), (sx + 60, 0.5, sz + 60), (sx + 60, 0.5, sz - 110), (sx - 90, 0.5, sz - 110),
             (255, 150, 70), lambda s, t: 0.32 * max(0.0, 1 - math.hypot(s - 90, (t - 50) * 0.8) / 100) ** 1.3)
    lx, lz = LAMP
    e.claror((lx - 170, 0.5, lz + 150), (lx + 170, 0.5, lz + 150), (lx + 170, 0.5, lz - 150), (lx - 170, 0.5, lz - 150),
             (255, 214, 150), lambda s, t: 0.22 * max(0.0, 1 - math.hypot(s - 170, (t - 150) * 1.1) / 170) ** 1.2)
    motlles(e, tex)
    sostre(e)
    estufa(e, tex)
    bagul(e, tex)
    taula(e)
    bombeta(e, tex)
    primer_pla(e)
    e.silueta({'primer_pla'}, 0.5)
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


# ─── Decorat: el vestit de reina ───────────────────────────────────────────

def vestit(cv):
    """El vestit de reina, a dalt del bagul: el vestit pla de sempre, projectat pel davant, la boca i la tapa."""
    _, e = _base()
    cv.img.alpha_composite(e.capa(_pla(PL.vestit), {'bagul', 'bagul_tapa'}))


PROPS = {'vestit': vestit}


# ─── Animació: l'estufa ────────────────────────────────────────────────────

def _frames_estufa():
    """El foc de l'estufa, per la reixeta: els fotogrames plans de sempre, posats a l'estufa (a la seva mida)."""
    sx, sz = ESTUFA
    cx, base = PL.STOVE
    out = []
    for fr in PL._frames_estufa():
        cv = Canvas(light=LIGHT, transparent=True)
        e = Escena(cv, CAM)
        e.sprite('foc', fr.crop((cx - 44, base - 74, cx + 28, base + 6)), (44, 74), (sx, 0, sz))
        out.append(cv.img)
    return out


ANIMS = {'estufa': {'frames': _frames_estufa, 'frameDuration': 140}}


# ─── Capes del davant ─────────────────────────────────────────────────────────

def _amo(ids):
    def mask(x, y):
        _, e = _base()
        return e.ids[e.amo[y * e.cv.w + x]] in ids
    return mask


def _v(x, z):
    return round(CAM.projecta((x, 0, z))[1])


_TF = _gira(TAULA[0], TAULA[1], TAULA[5], 0, -TAULA[3] / 2 - 28)       # el davant del banc de davant
_BF = _gira(BAGUL[0], BAGUL[1], BAGUL[2], 0, -23)

FRONT = [
    {'id': 'davant', 'mask': _amo({'primer_pla'}), 'baseline': 999, 'zIndex': 20},
    {'id': 'davant_taula', 'mask': _amo({'taula', 'taula_casc', 'bancs'}), 'baseline': _v(*_TF), 'zIndex': 20},
    {'id': 'davant_bagul', 'mask': _amo({'bagul', 'bagul_tapa'}), 'baseline': _v(*_BF), 'zIndex': 20},
    {'id': 'davant_estufa', 'mask': _amo({'estufa', 'estufa_tub'}), 'baseline': _v(ESTUFA[0], ESTUFA[1] - 8), 'zIndex': 20},
]


# ─── Geometria (coordenades de sala, projectades) ───────────────────────────────

def _escala_a(v):
    lo, hi = 1.0, 4000.0
    for _ in range(60):
        z = (lo + hi) / 2
        if CAM.projecta((260, 0, z))[1] > v:
            lo = z
        else:
            hi = z
    return CAM.escala((260, 0, (lo + hi) / 2))


def _poli(cx, cz, ang, a, b, b2=None):
    b2 = b if b2 is None else b2
    return [_p(*_gira(cx, cz, ang, lx, lz)) for lx, lz in ((-a, -b), (a, -b), (a, b2), (-a, b2))]


# El terra on es camina (al món): de la porta a l'estufa, sense arribar a la cadira ni al pilar del primer pla.
_VMAX = 236                                        # (més avall, la gent faria més d'1,2)
WALK_MON = [(26, 62), (420, 62), (470, 100), (556, 100), (556, 256), (450, 256), (450, 262), (26, 272)]
_WALK = [_p(x, z) for x, z in WALK_MON]
_WALK = [(min(W - 1, max(0, u)), min(_VMAX, v)) for u, v in _WALK]
_V_FONS, _V_PROP = min(v for _, v in _WALK), max(v for _, v in _WALK)
_PORTA = (_esq(20, 82), _esq(92, 214))

GEOMETRIA = {
    'things': {
        'porta': {'rect': _rect_mon(*_PORTA), 'walk': _p(34, (_PORTA[0][2] + _PORTA[1][2]) / 2 - 4)},
        'bagul': {'rect': _rect_mon(*[(x, y, z) for x, z in (_gira(BAGUL[0], BAGUL[1], BAGUL[2], lx, lz)
                                                              for lx in (-48, 48) for lz in (-23, 23)) for y in (0, 72)]),
                  'walk': _p(*_gira(BAGUL[0], BAGUL[1], BAGUL[2], -10, -60))},
        'pissarra': {'rect': _rect_mon(_fons(248, 36), _fons(358, 128)), 'walk': _p(_fons(303, 0)[0], 236)},
        'motlles': {'rect': _rect_mon((MOTLLES[0], 181, ZW - 34), (MOTLLES[1], 0, ZW - 34)),
                    'walk': _p((MOTLLES[0] + MOTLLES[1]) / 2 + 20, ZW - 80)},
        'cartells': {'rect': _rect_mon(_fons(120, 30), _fons(220, 144)), 'walk': _p(_fons(170, 0)[0], 250)},
    },
    'spawns': {'bru': _p(*_gira(TAULA[0], TAULA[1], TAULA[5], 30, TAULA[3] / 2 + 24)),
               'iri': _p(300, 104), 'vet': _p(420, 120)},
    'walkable': _WALK,
    'forats': [_poli(TAULA[0], TAULA[1], TAULA[5], TAULA[2] / 2 + 2, TAULA[3] / 2 + 28, TAULA[3] / 2 + 6),
               _poli(BAGUL[0], BAGUL[1], BAGUL[2], 50, 25),
               _poli(ESTUFA[0] - 8, ESTUFA[1], 0, 30, 22)],
    # la càmera, picada, a ≈1,9 m: el terra es veu aixafat
    'floorSquash': 0.45,
    # la bombeta, sobre la taula: l'ombra de la gent fuig d'allà
    'characterShadow': {'enabled': True, 'color': '#120c0a', 'alpha': 0.42, 'squash': 0.42, 'core': 0.6,
                        'light': {'x': _p(*LAMP)[0], 'y': _p(*LAMP)[1], 'stretch': 0.5, 'reach': 140}},
    'regions': [{'id': 'perspectiva', 'active': True, 'scaleEnabled': True, 'scaleWalkSpeed': True,
                 'scaleTop': round(_escala_a(_V_FONS - 2), 3), 'scaleBottom': round(_escala_a(_V_PROP + 2), 3),
                 'points': [(0, _V_FONS - 2), (W - 1, _V_FONS - 2), (W - 1, _V_PROP + 2), (0, _V_PROP + 2)]}],
    # La llum de la sala sobre els personatges (characterLights del motor): el local del sindicat, fosc i càlid: la
    # bombeta, l'estufa i el vidre de la porta.
    'characterLights': {
        'ambient': '#7a6a5e',
        'lights': [
            llum_personatges(CAM, LLUMS[0].pos, LLUMS[0].r, '#ffd090', 0.55),  # la bombeta
            llum_personatges(CAM, LLUMS[1].pos, LLUMS[1].r, '#ff8840', 0.45, whenPropVisible='estufa'),  # el foc de l'estufa
            llum_personatges(CAM, LLUMS[2].pos, LLUMS[2].r, '#c8d8ff', 0.25),  # el vidre de la porta
        ],
    },
}
