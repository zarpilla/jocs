"""
La casa del pare, per dins (Escena 1): la cuina i el despatx. Sala «de prop» (persones de ≈100 px). EN 3D
(hd640/tres_d.py), a 1×.

La masia vista des de la porta de l'escala, una mica des de dalt i girada cap a la finestra: tres parets de calç que
fugen. A l'esquerra, la paret de la llar de foc fuig cap a la cantonada: la xemeneia surt de la paret
(els muntants de pedra, la boca fosca amb l'olla i les brases que fan caliu, la lleixa amb els plats i la campana); al
fons, la pica de pedra (un volum, amb la cortineta de quadres), les lleixes dels setanta pots i la caixa de pots a
terra, la porta del pati (la llum s'escola per les juntes), el videotelèfon, el calendari i el quadre de la mare; a la
dreta, la paret del finestró en escorç. La taula del despatx és separada de la paret i girada (se'n veuen el davant
amb els calaixos, el costat i el tauler amb els diaris i la làmpada): s'hi pot passar per darrere. Les bigues del
sostre fugen cap al fons, i el terra de rajola de fang s'empetiteix. Primer pla: a l'esquerra, la barana i l'arrencada
de l'escala de fusta fosca; a la dreta, un segon escriptori ple de papers, vist des de dalt, que tapa qui hi passa per
darrere. La llum daurada del finestró entra en diagonal i creua la sala de dreta a esquerra (el feix amb pols i la
taca a terra); la llar de foc i la porta fan una penombra càlida; foscor als racons i sota els mobles.

Tot el detall ve de la casa plana de sempre (granja_casa_pla_comu.py), dibuixada de cara i projectada. Els decorats
`quadre`, `caixa_forta` i `caixa_oberta` es projecten per la paret del fons; `quadre_apartat` és el quadre recolzat a
terra contra la paret del finestró. ANIMS: `pols` (les volves de pols dins el feix de sol).

El món: x a la dreta (0 = la paret de la llar de foc), y amunt (0 = el terra), z cap al fons (300 = la paret de la
porta); 1 unitat = 1 píxel de sala a la distància on un personatge fa 100 px (escala 1).
"""
import functools
import math

import hd640  # noqa: F401  (abans de cap hd.rooms: posa la llibreria a 640×360)
from PIL import Image

from hd.pix import Canvas, Light, W, H, hr, B4, mix
from hd.rooms.exterior import fbm
from hd640.rooms import granja_casa_pla_comu as PL
from hd640.rooms.terra2_comu import LIME, TERRA, PLANK, STONE, BLACKT, PAPER, CLOTH, motes_frames, _diff
from hd640.tres_d import Camera, Escena, Llum

BOTTOM = 259                                       # la sala acaba aquí (a sota, la barra de verbs)
XR = 420                                           # la paret del finestró (la de la dreta)
ZW = 300                                           # la paret del fons (la de la porta)
HW = 192                                           # l'alçada del dibuix pla de les parets (y 14..206 del pla)
HS = 216                                           # el sostre
FY = PL.FLOOR_Y                                    # (al pla, on la paret toca a terra: y del món = FY − y del pla)
FX = 150                                           # al pla, la cantonada de l'esquerra: x del món = x del pla − FX
LX = 150                                           # quant de la paret de l'esquerra fa el pla (x 0..150 del pla)
RX0 = 530                                          # al pla, on comença la paret del finestró (a la cantonada)
RL = 130                                           # quant de la paret del finestró fa el pla (x 530..660 → z 300..170)
SUN = (255, 214, 150)

CAM = Camera(pos=(190, 160, -190), yaw=0.15, pitch=0.05, f=380, centre=(320, 84))

TL = Light(ambient=0.2, vignette=None, floor_fade=None)   # (les textures, sense la llum del pla: la posa el món)
LIGHT = Light(ambient=0.0, vignette=None, floor_fade=None)
WIN_Z = ZW - ((PL.WIN[0] + PL.WIN[2]) / 2 - RX0)          # el mig del finestró, a la paret de la dreta
WIN_Y = (FY - PL.WIN[3], FY - PL.WIN[1])                  # (de baix a dalt)
LLUMS = [
    Llum((XR - 30, 120, WIN_Z), 340, 2.2, power=1.3),      # el sol del finestró
    Llum((172, 30, ZW - 16), 150, 0.8, power=1.6),         # la llum de les juntes de la porta
    Llum((16, 12, 215), 120, 1.7, power=1.4),              # les brases de la llar de foc
    Llum((200, 400, 150), 600, 0.4, power=1.0),            # una mica de llum de tot arreu
]
AMBIENT = -1.7

# El feix de sol: entra pel finestró (x = XR), baixa cap a l'esquerra i una mica cap endavant.
BEAM_D = (-1.0, -0.5, -0.42)                       # per unitat de x
BEAM_Y = (WIN_Y[0] + 4, WIN_Y[1] - 6)              # l'alçada del finestró (el sol hi entra)
BEAM_Z = (WIN_Z - 20, WIN_Z + 20)

TAULA = (334, 242, 132, 44, 40, 0.3)               # la taula del despatx: centre x, z, ample, fons, alt, gir
TAULA2 = (418, 84, 120, 70, 44, -0.45)             # el segon escriptori, en primer pla a la dreta
PICA = (6, 82, 46, ZW - 28)                        # la pica: x0, x1, alt, davant (z)
CAIXA_POTS = (90, 134, 15, ZW - 18)
BOL = (58, 214)
# La llar de foc, en volum contra la paret de l'esquerra: la xemeneia surt de la paret (z0..z1 i fins a x = LLAR_D),
# la boca entre els muntants, la lleixa al damunt i la campana que s'estreny fins al sostre.
LLAR = (164, 266)                                  # z dels cantons de fora dels muntants
LLAR_D = 30                                        # quant surt de la paret
LLAR_M = 10                                        # el gruix dels muntants
LLAR_H = 96                                        # l'alçada de la boca (la sota de la lleixa)
LLAR_PX = ZW - LX                                  # al pla de l'esquerra, x del pla = z del món − (ZW − LX)
EMBER = [(30, 8, 4), (90, 24, 8), (170, 56, 14), (230, 110, 30), (255, 180, 70), (255, 230, 150)]


def _mon_fons(fx, fy):
    """Un punt del dibuix pla de la paret del fons al món."""
    return (fx - FX, FY - fy, ZW)


# ─── Les textures: la casa plana de sempre ───────────────────────────────────

def _cv():
    return Canvas(light=TL)


def _capa(fn):
    cv = Canvas(light=TL, transparent=True)
    fn(cv)
    return cv.img


@functools.lru_cache(maxsize=None)
def _paret_nua():
    cv = _cv()
    PL.ceiling(cv)
    PL.wall(cv)
    return cv.img


@functools.lru_cache(maxsize=None)
def _textures():
    # la paret del fons: la pica, les lleixes, la porta, el videotelèfon, el calendari i la marca del quadre
    cv = _cv()
    cv.img.paste(_paret_nua())
    cv.P = cv.img.load()
    pots = _capa(PL.jars)
    caixa_pots = pots.crop((0, 186, W, H))
    pots.paste((0, 0, 0, 0), (0, 186, W, H))                       # (la caixa de pots va a terra, en volum)
    cv.img.alpha_composite(pots)
    PL.sink(cv)
    PL.door(cv)
    fil = _capa(PL.wiring)
    fil.paste((0, 0, 0, 0), (300, 0, 340, 60))                     # (la bombeta penja del sostre, en volum)
    cv.img.alpha_composite(fil)
    cv.P = cv.img.load()
    PL.videotelefon(cv)
    PL.calendari(cv)
    PL.mark(cv)
    fons = cv.img
    # la paret de l'esquerra: la llar de foc
    cv = _cv()
    cv.img.paste(_paret_nua())
    cv.P = cv.img.load()
    PL.hearth_boca(cv, LLAR[0] + LLAR_M - LLAR_PX - 4, LLAR[1] - LLAR_M - LLAR_PX + 4)   # (el fons de la boca)
    esq = cv.img
    # la paret de la dreta: el finestró (sense el raig de sol pintat: el fa el món)
    cv = Canvas(W + 40, light=TL)
    cv.img.paste(_paret_nua())
    cv.img.paste(_paret_nua().crop((200, 0, 240, H)), (W, 0))
    cv.P = cv.img.load()
    PL.window(cv)
    dreta = cv.img
    # la taula del despatx (transparent: el davant i, dret, el que hi ha al damunt)
    taula = _capa(PL.desk)
    cpots = Image.new('RGBA', (W, H), (0, 0, 0, 0))
    cpots.paste(caixa_pots, (0, 186))
    return {'fons': fons, 'esq': esq, 'dreta': dreta, 'nua': _paret_nua(), 'taula': taula, 'pots': cpots,
            'bombeta': _capa(PL.wiring).crop((314, 28, 331, 48)), 'bol': _capa(PL.bol).crop((134, 208, 166, 224)),
            'lleixa': _capa(lambda cv: PL.hearth_lleixa(cv, 20, 116))}


# ─── Les superfícies procedurals ─────────────────────────────────────────────

def _terra(s, t, P):
    """Rajola de fang (30 × 30 del món, en files desplaçades): juntes, rajoles més fosques, alguna d'esquerdada, i
    gastada pel mig (on es trepitja)."""
    x, z = P[0], P[2]
    row = int(z // 30)
    xo = x + (15 if row % 2 else 0)
    col = int(xo // 30)
    fu, fv = (xo % 30) / 30, (z % 30) / 30
    v = 3.0 + (hr(col, row, 3) - 0.5) * 1.1 + (fbm(x / 40, z / 30, 21) - 0.5) * 0.7
    if (col + row) % 7 == 0:
        v -= 0.5
    if hr(col, row, 9) > 0.9 and abs(fu - 0.3 - fv * 0.4) < 0.025:
        v -= 1.4                                                   # una rajola esquerdada
    if fu < 0.05 or fv < 0.05:
        v -= 1.6                                                   # les juntes
    elif fu < 0.1 or fv < 0.1:
        v += 0.3
    worn = max(0.0, 1 - abs(z - 200) / 80) * max(0.0, 1 - abs(x - 200) / 180)
    return v + worn * 0.5


def _sostre(s, t, P):
    x = P[0]
    return 1.2 + (fbm(x / 9, P[2] / 30, 3) - 0.5) * 0.8 - (0.7 if x % 23 < 1.2 else 0)


def _fusta(lvl0, seed=1):
    def L(s, t, P):
        return lvl0 + (fbm(s / 30, t / 4, seed) - 0.5) * 0.8 - (0.8 if t % 9 < 0.8 else 0)
    return L


# ─── El feix de sol ─────────────────────────────────────────────────────────

def _feix_font(P):
    """D'on ve el sol que arriba al punt P (y, z al finestró), o None si P és fora del feix."""
    k = XR - P[0]
    if k < 0:
        return None
    return P[1] - BEAM_D[1] * k, P[2] - BEAM_D[2] * k


def _dins_finestro(y, z):
    """Quant hi entra el sol per aquest punt del finestró (0..1), amb les vores suaus."""
    a = min(y - BEAM_Y[0], BEAM_Y[1] - y, z - BEAM_Z[0], BEAM_Z[1] - z)
    return max(0.0, min(1.0, a / 5 + 0.2))


def _taca_sol(x, z):
    """La taca del sol a terra (0..1)."""
    f = _feix_font((x, 0, z))
    return 0.0 if f is None else _dins_finestro(*f)


@functools.lru_cache(maxsize=None)
def _feix_pantalla():
    """La densitat del feix de sol a cada píxel de sala: la llargada del raig de vista dins el feix (analítica: el
    feix és un prisma i, al llarg del raig, les coordenades d'origen són lineals)."""
    out = [[0.0] * W for _ in range(BOTTOM + 1)]
    C = CAM.pos
    cy, sy, cp, sp = CAM._cy, CAM._sy, CAM._cp, CAM._sp
    f, (cu, cv) = CAM.f, CAM.centre
    dx, dy, dz = BEAM_D
    for v in range(BOTTOM + 1):
        for u in range(W):
            # la direcció del raig (de la càmera al món)
            x2, y2, z2 = (u + 0.5 - cu) / f, -(v + 0.5 - cv) / f, 1.0
            y1 = y2 * cp - z2 * sp                                       # (desfà el pitch)
            z1 = y2 * sp + z2 * cp
            rx, rz = x2 * cy + z1 * sy, -x2 * sy + z1 * cy               # (desfà el yaw)
            ry = y1
            # al llarg del raig P = C + t r: k = XR − Px, y0 = Py − dy·k, z0 = Pz − dz·k (tot lineal en t)
            lo, hi = 0.0, 4000.0
            for a0, a1, mn, mx in (
                    (XR - C[0], -rx, 0.0, 1e9),                                         # k ≥ 0
                    (C[1], ry, 0.0, 1e9),                                               # per sobre del terra
                    (C[1] - dy * (XR - C[0]), ry + dy * rx, BEAM_Y[0], BEAM_Y[1]),      # l'alçada al finestró
                    (C[2] - dz * (XR - C[0]), rz + dz * rx, BEAM_Z[0], BEAM_Z[1])):    # l'amplada al finestró
                if abs(a1) < 1e-9:
                    if not (mn <= a0 <= mx):
                        lo, hi = 1.0, 0.0
                        break
                    continue
                t0, t1 = (mn - a0) / a1, (mx - a0) / a1
                if t0 > t1:
                    t0, t1 = t1, t0
                lo, hi = max(lo, t0), min(hi, t1)
                if lo >= hi:
                    break
            if hi > lo:
                n = math.sqrt(rx * rx + ry * ry + rz * rz)
                out[v][u] = (hi - lo) * n
    return out


def feix(x, y):
    """El feix de sol a (x, y) de sala: 0..1."""
    if not (0 <= x < W and 0 <= y <= BOTTOM):
        return 0.0
    return min(1.0, _feix_pantalla()[int(y)][int(x)] / 32)


def _pinta_feix(cv):
    P = cv.P
    for Y in range(BOTTOM + 1):
        for X in range(W):
            b = feix(X, Y)
            if b > 0:
                k = 0.34 * b
                if k > B4[Y & 3][X & 3] * 0.25:
                    P[X, Y] = mix(P[X, Y], SUN, k + 0.04) + (255,)


# ─── Les peces ──────────────────────────────────────────────────────────────

def _ombra(e, cx, cz, rx, rz, k=0.55, dx=0.0, dz=0.0):
    """Una ombra el·líptica a terra, desplaçada (dx, dz) cap on no hi ha la llum."""
    cx, cz = cx + dx, cz + dz
    e.foscor('ombra', (cx - rx, 0.4, cz + rz), (cx + rx, 0.4, cz + rz), (cx + rx, 0.4, cz - rz), (cx - rx, 0.4, cz - rz),
             lambda s, t: k * min(1.0, 1.7 * max(0.0, 1 - ((s - rx) / rx) ** 2 - ((t - rz) / rz) ** 2)))


def parets(e, tex):
    zn = CAM.pos[2] - 100
    TS = 1
    # el sostre i les bigues, que fugen cap al fons
    e.quad('sostre', (0, HS, zn), (XR, HS, zn), (XR, HS, ZW), (0, HS, ZW), ramp=PLANK, lvl=_sostre, dues_cares=True)
    for bx in (34, 112, 190, 268, 346):
        e.caixa('bigues', bx - 6, bx + 6, HS - 12, HS, zn, ZW, PLANK, 2.2,
                cares={'sota': {'ramp': PLANK, 'lvl': _fusta(2.6, bx)}, 'esquerra': {'ramp': PLANK, 'lvl': 1.4},
                       'dreta': {'ramp': PLANK, 'lvl': 1.8}})
    # la paret de l'esquerra: de prop, calç; cap al fons, la llar de foc (x 0..150 del pla)
    nua = tex['nua']
    e.quad('paret_esq_prop', (0, HW, zn), (0, HW, ZW - LX), (0, 0, ZW - LX), (0, 0, zn),
           tex=(nua, (300, 14, 300 + LX, FY), TS))
    e.quad('paret_esq', (0, HW, ZW - LX), (0, HW, ZW), (0, 0, ZW), (0, 0, ZW - LX), tex=(tex['esq'], (0, 14, LX, FY), TS))
    # la paret del fons (x 150..570 del pla)
    e.quad('paret_fons', (0, HW, ZW), (XR, HW, ZW), (XR, 0, ZW), (0, 0, ZW), tex=(tex['fons'], (FX, 14, FX + XR, FY), TS))
    # la paret del finestró (x 530..660 del pla) i, de prop, calç
    e.quad('paret_dreta', (XR, HW, ZW), (XR, HW, ZW - RL), (XR, 0, ZW - RL), (XR, 0, ZW),
           tex=(tex['dreta'], (RX0, 14, RX0 + RL, FY), TS))
    e.quad('paret_dreta_prop', (XR, HW, ZW - RL), (XR, HW, zn), (XR, 0, zn), (XR, 0, ZW - RL),
           tex=(nua, (60, 14, 60 + ZW - RL - zn, FY), TS))
    # el fris de calç entre el dibuix pla i el sostre, amb l'ombra del sostre
    fris = dict(ramp=LIME, lvl=lambda s, t, P: 3.2 + (fbm(s / 30, P[1] / 10, 5) - 0.5) * 1.0 - 1.4 * max(0.0, 1 - t / 8))
    e.quad('fris', (0, HS, zn), (0, HS, ZW), (0, HW, ZW), (0, HW, zn), **fris)
    e.quad('fris', (0, HS, ZW), (XR, HS, ZW), (XR, HW, ZW), (0, HW, ZW), **fris)
    e.quad('fris', (XR, HS, ZW), (XR, HS, zn), (XR, HW, zn), (XR, HW, ZW), **fris)
    # el terra
    e.quad('terra', (0, 0, ZW), (XR, 0, ZW), (XR, 0, zn), (0, 0, zn), ramp=TERRA, lvl=_terra)
    # la llum de fora: les juntes de la porta (un ventall càlid a terra) i la taca del sol del finestró
    dx0, dx1 = PL.DOOR[0] - FX, PL.DOOR[2] - FX
    e.claror((dx0 - 30, 0.3, ZW), (dx1 + 30, 0.3, ZW), (dx1 + 60, 0.3, ZW - 70), (dx0 - 60, 0.3, ZW - 70), SUN,
             lambda s, t: 0.32 * max(0.0, 1 - t / 70) ** 1.5 * max(0.0, 1 - abs(s - 60 - t * 0.43) / (32 + t * 0.6)))
    e.claror((0, 0.3, ZW), (XR, 0.3, ZW), (XR, 0.3, 40), (0, 0.3, 40), SUN,
             lambda s, t: 0.55 * _taca_sol(s, ZW - t))
    # la foscor dels racons
    e.foscor('racons', (0, 0.5, ZW), (XR, 0.5, ZW), (XR, 0.5, zn), (0, 0.5, zn),
             lambda s, t: max(0.5 * max(0.0, 1 - t / 24), 0.5 * max(0.0, 1 - s / 22), 0.5 * max(0.0, 1 - (XR - s) / 22)))
    for x0, s0 in ((0.5, 0), (XR - 0.5, 1)):
        e.foscor('racons', (x0, HW, ZW - 40), (x0, HW, ZW), (x0, 0, ZW), (x0, 0, ZW - 40),
                 lambda s, t: 0.45 * max(0.0, 1 - (40 - s) / 40))
    e.foscor('racons', (0, HW, ZW - 0.5), (40, HW, ZW - 0.5), (40, 0, ZW - 0.5), (0, 0, ZW - 0.5),
             lambda s, t: 0.45 * max(0.0, 1 - s / 40))
    e.foscor('racons', (XR - 40, HW, ZW - 0.5), (XR, HW, ZW - 0.5), (XR, 0, ZW - 0.5), (XR - 40, 0, ZW - 0.5),
             lambda s, t: 0.4 * max(0.0, 1 - (40 - s) / 40))


def _pedra(lvl0, seed=1):
    """Carreus de pedra (en coordenades del món): filades de 12, juntes fosques, cada pedra d'un to."""
    def L(s, t, P):
        y, h = P[1], P[2] + P[0]
        row = int(y // 12)
        col = int((h + (9 if row % 2 else 0)) // 18)
        v = lvl0 + (hr(col, row, seed) - 0.5) * 1.0 + (fbm(h / 10, y / 10, seed) - 0.5) * 0.5
        if y % 12 < 1.2 or (h + (9 if row % 2 else 0)) % 18 < 1.2:
            v -= 1.4
        return v
    return L


def llar(e, tex):
    """La llar de foc: la xemeneia que surt de la paret de l'esquerra. La boca fosca (el fons, del dibuix pla, amb
    l'olla), la llosa i la cendra amb les brases que fan caliu, els muntants de pedra, la lleixa de fusta amb els
    plats i la campana de calç, ennegrida a baix, que s'estreny fins al sostre. Es pinta de lluny a prop."""
    z0, z1 = LLAR
    D, M, H = LLAR_D, LLAR_M, LLAR_H
    zb0, zb1 = z0 + M, z1 - M                                      # la boca
    YL = H + 8                                                     # el damunt de la lleixa
    _ombra(e, D + 8, (z0 + z1) / 2, 18, (z1 - z0) / 2 + 4, 0.4, dx=-2)
    # la llosa de la llar, a terra, que surt una mica més que la xemeneia
    e.caixa('llar', 0, D + 5, 0, 3, z0 - 4, z1 + 4, STONE, 2.8,
            cares={'dalt': {'ramp': STONE, 'lvl': lambda s, t, P: 2.6 + (hr(int(P[0] // 12), int(P[2] // 16), 4) - 0.5)
                            - (1.2 if P[2] % 16 < 1 or P[0] % 12 < 1 else 0)
                            - (1.2 if P[0] < D - 2 and zb0 < P[2] < zb1 else 0)},
                   'dreta': {'ramp': STONE, 'lvl': 2.2}, 'davant': {'ramp': STONE, 'lvl': 2.4}})
    # dins la boca: el sostre fosc (la gola de la xemeneia)
    e.quad('llar', (0, H, zb0), (D - 2, H, zb0), (D - 2, H, zb1), (0, H, zb1), ramp=STONE, lvl=0.4, dues_cares=True)
    # la cendra i les brases: tions creuats i caliu
    e.quad('llar', (2, 3.4, zb0 + 6), (D - 6, 3.4, zb0 + 6), (D - 6, 3.4, zb1 - 6), (2, 3.4, zb1 - 6), ramp=EMBER,
           lvl=lambda s, t, P: (1.2 + (fbm(P[0] / 5, P[2] / 5, 8) - 0.5) * 2.0
                                + (2.6 if fbm(P[0] / 3, P[2] / 3, 9) > 0.62 else 0)),
           forma=lambda s, t: ((s - (D - 8) / 2) / ((D - 8) / 2)) ** 2 + ((t - (zb1 - zb0 - 12) / 2)
                                                                       / ((zb1 - zb0 - 12) / 2)) ** 2 < 1,
           dues_cares=True)
    zm = (zb0 + zb1) / 2
    for (xa, za), (xb, zb_) in (((4, zm - 22), (22, zm + 8)), ((6, zm + 20), (20, zm - 10))):
        e.cable('llar', [(xa, 6, za), (xb, 6, zb_)], BLACKT, 1.4, gruix=5)
        e.cable('llar', [(xa + 1, 7.5, za + 2), (xb - 1, 7.5, zb_ - 2)], EMBER, 3.6, gruix=1.6)
    # unes flametes baixes, que lluen damunt les brases (de cara a la sala)
    for k, (fz, fh, fw) in enumerate(((zm - 12, 13, 7), (zm + 2, 18, 8), (zm + 14, 11, 6))):
        e.quad('llar', (12, 6 + fh, fz - fw), (12, 6 + fh, fz + fw), (12, 6, fz + fw), (12, 6, fz - fw), ramp=EMBER,
               lvl=lambda s, t, P, fh=fh: 2.8 + 2.6 * t / fh,
               forma=lambda s, t, fh=fh, fw=fw, k=k: abs(s - fw) < fw * (t / fh) ** 0.8 * (0.8 + 0.2 * math.sin(t * 1.3 + k)),
               dues_cares=True)
    e.claror((0.6, 60, zb0), (0.6, 60, zb1), (0.6, 0, zb1), (0.6, 0, zb0), (255, 140, 60),
             lambda s, t: 0.3 * max(0.0, 1 - abs(s - (zb1 - zb0) / 2) / ((zb1 - zb0) / 2)) * (t / 60) ** 2)
    # els muntants de pedra (primer el del fons; el de prop tapa una mica la boca)
    for za, zb_, dins in ((zb1, z1, True), (z0, zb0, False)):
        # (el davant del muntant del fons és el costat de dins de la boca: ennegrit pel fum)
        dav = (lambda s, t, P: _pedra(1.6, 6)(s, t, P) - (0.9 if P[1] > 50 else 0)) if dins else _pedra(2.6, 6)
        e.caixa('llar', 0, D, 3, H, za, zb_, STONE, 3.0,
                cares={'dreta': {'ramp': STONE, 'lvl': _pedra(3.4, 5)},
                       'davant': {'ramp': STONE, 'lvl': dav},
                       'darrere': {'ramp': STONE, 'lvl': lambda s, t, P: _pedra(1.6, 7)(s, t, P) - (0.8 if P[1] > 60 else 0)}})
    # la campana: la cara de davant, inclinada, i el costat que mira cap a la càmera; ennegrida a baix pel fum
    xt, zt0, zt1 = 14, z0 + 26, z1 - 22                            # a dalt, al sostre
    calc = dict(ramp=LIME, lvl=lambda s, t, P: 3.4 + (fbm(P[2] / 10, P[1] / 10, 30) - 0.5) * 0.8
                - 1.8 * max(0.0, 1 - (P[1] - YL) / 46) * (0.5 + 0.5 * fbm(P[2] / 8, P[1] / 20, 31)))
    e.quad('llar', (D - 2, YL, z0 + 2), (D - 2, YL, z1 - 2), (xt, HS, zt1), (xt, HS, zt0), dues_cares=True, **calc)
    e.quad('llar', (0, YL, z0 + 2), (D - 2, YL, z0 + 2), (xt, HS, zt0), (0, HS, zt0),
           ramp=LIME, lvl=lambda s, t, P: calc['lvl'](s, t, P) - 0.6, dues_cares=True)
    # la lleixa de fusta, que sobresurt, i el que hi ha al damunt (plats drets, el llum d'oli, una ampolla)
    e.caixa('llar', 0, D + 6, H, YL, z0 - 6, z1 + 6, PLANK, 3.0,
            cares={'dalt': {'ramp': PLANK, 'lvl': _fusta(3.8, 2)}, 'dreta': {'ramp': PLANK, 'lvl': _fusta(2.8, 3)},
                   'davant': {'ramp': PLANK, 'lvl': 2.4}, 'sota': {'ramp': PLANK, 'lvl': 0.8}})
    e.quad('llar', (D - 6, YL + 20, z0 + 2), (D - 6, YL + 20, z1 - 2), (D - 6, YL, z1 - 2), (D - 6, YL, z0 + 2),
           tex=(tex['lleixa'], (20, PL.MANTEL_Y - 24, 116, PL.MANTEL_Y - 4)), dues_cares=True)


def mobles(e, tex):
    llar(e, tex)
    # la pica de pedra: el davant amb la cortineta del dibuix pla; la tapa de marbre amb el clot
    x0, x1, h, zf = PICA
    px0, px1 = x0 + FX, x1 + FX
    _ombra(e, (x0 + x1) / 2, zf - 4, 44, 8, 0.5, dx=-8)
    e.caixa('pica', x0, x1, 0, h, zf, ZW - 1, STONE, 3.0,
            cares={'davant': {'tex': (tex['fons'], (px0, FY - h, px1 + 1, FY))},
                   'dalt': {'ramp': STONE, 'lvl': lambda s, t, P: 5.0 - (2.6 if 18 < s < 58 and 6 < t < 22 else 0)
                            + (0.6 if t > 26 else 0)},
                   'dreta': {'ramp': STONE, 'lvl': 2.6}})
    # la caixa de pots a terra
    cx0, cx1, ch, cz = CAIXA_POTS
    _ombra(e, (cx0 + cx1) / 2, cz - 2, 26, 6, 0.55, dx=-6)
    e.caixa('caixa_pots', cx0, cx1, 0, ch, cz, ZW - 2, PLANK, 3.0,
            cares={'davant': {'tex': (tex['pots'], (cx0 + FX, PL.FLOOR_Y + 4 - ch, cx1 + FX + 1, PL.FLOOR_Y + 5))},
                   'dalt': {'ramp': PLANK, 'lvl': lambda s, t, P: (4.4 if int(s) % 6 < 4 and 2 < t < 14 else 1.0)},
                   'dreta': {'ramp': PLANK, 'lvl': 2.2}})
    # el bol del gos, davant del foc
    bx, bz = BOL
    _ombra(e, bx, bz, 14, 6, 0.6, dx=-4)
    e.sprite('bol', tex['bol'], (16, 12), (bx, 0, bz))
    # la taula del despatx, separada de la paret i girada: el davant (calaixos) del dibuix pla, el tauler de fusta
    cx, cz, w, d, h, ang = TAULA
    X0, X1 = PL.DESK[0], PL.DESK[2]
    _ombra(e, cx, cz, 76, 30, 0.6, dx=-22, dz=-10)
    tap = {'ramp': PLANK, 'lvl': lambda s, t, P: 4.0 + (fbm(s / 24, t / 2, 3) - 0.5) * 0.7 - (1.0 if t < 1.2 else 0)}
    e.caixa_girada('taula', cx, cz, w, d, h, ang, PLANK, 2.6,
                   cares={'davant': {'tex': (tex['taula'], (X0, PL.DESK[1] + 10, X1 + 1, PL.DESK[3] + 1))},
                          'dalt': tap, 'esquerra': {'ramp': PLANK, 'lvl': _fusta(2.2, 4)},
                          'dreta': {'ramp': PLANK, 'lvl': 1.8}})
    # al damunt: les cartes obertes i el que hi ha dret (els diaris, el cabdell, la làmpada)
    c, s_ = math.cos(ang), math.sin(ang)

    def L(lx, lz, y=h):
        return (cx + lx * c - lz * s_, y, cz + lx * s_ + lz * c)
    for k, (lx, lz, pw, pd) in enumerate(((-6, -6, 16, 11), (6, -2, 14, 10), (24, -9, 12, 9))):
        e.quad('taula', L(lx, lz + pd, h + 0.3 + k * 0.1), L(lx + pw, lz + pd, h + 0.3 + k * 0.1),
               L(lx + pw, lz, h + 0.3 + k * 0.1), L(lx, lz, h + 0.3 + k * 0.1), ramp=PAPER,
               lvl=lambda s, t, P: 4.4 - (0.8 if t < 1 else 0))
    dalt = tex['taula'].crop((X0, 118, X1 + 1, PL.DESK[1]))
    e.sprite('taula', dalt, ((X1 - X0) / 2, PL.DESK[1] - 118), L(0, 6, h))
    # la bombeta del sostre (apagada), amb el cable
    bxw, bzw = 200, 214
    e.linia((bxw, HS, bzw), (bxw, 150, bzw), BLACKT, 1.6)
    e.sprite('bombeta', tex['bombeta'], (8.5, 6), (bxw, 150, bzw))


def primer_pla(e):
    """L'escala de fusta fosca que puja cap a l'esquerra, amb la barana (tallada per la vora), i el segon escriptori
    a la dreta, vist des de dalt, ple de papers."""
    fosc = PLANK
    # els graons, que pugen cap a l'esquerra i surten de la pantalla
    for k in range(9):
        x1 = 40 - k * 22
        e.caixa('primer_pla', x1 - 22, x1, 0, 14 * (k + 1), 8, 64, fosc, 1.6,
                cares={'dalt': {'ramp': fosc, 'lvl': 2.6 - (0.8 if k % 2 else 0)},
                       'dreta': {'ramp': fosc, 'lvl': 1.2}, 'davant': {'ramp': fosc, 'lvl': 0.8}})
    # la barana: el pilar de l'arrencada, els balustres i el passamà
    e.caixa('primer_pla', 46, 58, 0, 104, 58, 70, fosc, 1.8,
            cares={'dreta': {'ramp': fosc, 'lvl': lambda s, t, P: 1.8 - (1.0 if t % 30 < 2 else 0)},
                   'davant': {'ramp': fosc, 'lvl': lambda s, t, P: 1.0 + (0.6 if s < 2 else 0)},
                   'dalt': {'ramp': fosc, 'lvl': 2.4}})
    e.caixa('primer_pla', 44, 60, 104, 110, 56, 72, fosc, 2.2)
    for k in range(1, 7):
        bx = 50 - k * 22
        e.caixa('primer_pla', bx - 2.5, bx + 2.5, 14 * k, 14 * k + 84, 62, 67, fosc, 1.4,
                cares={'dreta': {'ramp': fosc, 'lvl': 1.8}, 'davant': {'ramp': fosc, 'lvl': 1.0}})
    e.cable('primer_pla', [(52, 106, 64), (-120, 106 + 172 * 0.64, 64)], fosc, 2.0, gruix=7)
    # el segon escriptori, a la dreta: un tauler gran i fosc, de biaix, amb papers, una pila de llibres i el tinter
    cx, cz, w, d, h, ang = TAULA2
    e.caixa_girada('escriptori', cx, cz, w, d, h, ang, PLANK, 1.6,
                   cares={'dalt': {'ramp': PLANK, 'lvl': lambda s, t, P: 2.8 + (fbm(s / 30, t / 3, 8) - 0.5) * 0.7
                                   - (0.8 if t < 1.5 or s < 1.5 else 0)},
                          'esquerra': {'ramp': PLANK, 'lvl': lambda s, t, P: 1.2 - (0.6 if s % 22 < 1 else 0)},
                          'davant': {'ramp': PLANK, 'lvl': lambda s, t, P: 1.0 + (1.2 if 8 < t < 10 else 0)}})
    c, s_ = math.cos(ang), math.sin(ang)

    def L(lx, lz, y):
        return (cx + lx * c - lz * s_, y, cz + lx * s_ + lz * c)
    papers = ((-52, 10, 22, 16, 0.2), (-40, -8, 20, 15, -0.15), (-18, 6, 24, 17, 0.1), (-30, 20, 18, 13, 0.3),
              (4, -14, 22, 16, 0.05), (10, 12, 20, 14, -0.2))
    for k, (lx, lz, pw, pd, a) in enumerate(papers):
        y = h + 0.3 + k * 0.15
        ca, sa = math.cos(a), math.sin(a)

        def Q(u, v, lx=lx, lz=lz, ca=ca, sa=sa, y=y):
            return L(lx + u * ca - v * sa, lz + u * sa + v * ca, y)
        e.quad('escriptori', Q(0, pd), Q(pw, pd), Q(pw, 0), Q(0, 0), ramp=PAPER,
               lvl=lambda s, t, P, k=k: 3.6 + (k % 3) * 0.3 - (1.4 if 3 < t < pd - 3 and int(t) % 3 == 0 and 3 < s < pw - 3 else 0)
               - (0.8 if t < 0.8 else 0))
    for k in range(4):                                                    # la pila de llibres
        e.caixa_girada('escriptori', L(34, -6, 0)[0], L(34, -6, 0)[2], 26 - k * 2, 18 - k, 5, ang + 0.1 * k,
                       CLOTH if k % 2 else PLANK, 2.4 + k * 0.3, y0=h + k * 5)
    e.caixa_girada('escriptori', L(-6, 24, 0)[0], L(-6, 24, 0)[2], 6, 6, 7, ang, BLACKT, 1.6, y0=h)   # el tinter


def escena(cv, tex, quadre_apartat=None):
    e = Escena(cv, CAM, LLUMS, ambient=AMBIENT)
    parets(e, tex)
    if quadre_apartat is not None:
        # el quadre de la mare, recolzat a terra contra la paret del finestró (sota l'ampit), una mica inclinat
        z0, z1 = WIN_Z + 26, WIN_Z - 20
        img, (fx0, fy0, fx1, fy1) = quadre_apartat
        _ombra(e, XR - 10, (z0 + z1) / 2, 10, 26, 0.6)
        e.quad('quadre_apartat', (XR - 3, 56, z0), (XR - 3, 56, z1), (XR - 14, 0, z1), (XR - 14, 0, z0),
               tex=(img, (fx0, fy0, fx1, fy1)))
    mobles(e, tex)
    primer_pla(e)
    return e


# ─── Composició ────────────────────────────────────────────────────────────

@functools.lru_cache(maxsize=None)
def _base():
    cv = Canvas(light=LIGHT)
    e = escena(cv, _textures())
    _pinta_feix(cv)
    cv.rect(0, BOTTOM + 1, W - 1, H - 1, [(0, 0, 0)], 0, lit=0)    # la barra de verbs: negre
    return cv.img, e


def bg(cv):
    img, _ = _base()
    cv.img.paste(img)
    cv.P = cv.img.load()


def _paret_fons(fn):
    """Un decorat de la paret del fons, dibuixat pla i projectat (tapat pel que hi ha davant)."""
    def prop(cv):
        _, e = _base()
        flat = Canvas(light=TL, transparent=True)
        fn(flat)
        cv.img.alpha_composite(e.capa(flat.img, {'paret_fons'}))
    return prop


def quadre_apartat(cv):
    base, _ = _base()
    flat = Canvas(light=TL, transparent=True)
    PL.quadre_apartat(flat)
    c2 = Canvas(light=LIGHT)
    e = escena(c2, _textures(), quadre_apartat=(flat.img, (572, FY + 6 - 54, 620, FY + 6)))
    _pinta_feix(c2)
    c2.rect(0, BOTTOM + 1, W - 1, H - 1, [(0, 0, 0)], 0, lit=0)
    cv.img.alpha_composite(_diff(c2.img, base))


PROPS = {
    'quadre': _paret_fons(PL.quadre),
    'caixa_forta': _paret_fons(PL.caixa_forta),
    'caixa_oberta': _paret_fons(PL.caixa_oberta),
    'quadre_apartat': quadre_apartat,
}


def _frames_pols():
    return motes_frames(_base()[0], lambda x, y: feix(x, y) * 1.4, n=48, count=60, seed=12)


ANIMS = {'pols': {'frames': _frames_pols, 'frameDuration': 140}}


def _amo(ids):
    def mask(x, y):
        _, e = _base()
        return e.ids[e.amo[y * e.cv.w + x]] in ids
    return mask


# ─── Geometria (coordenades de sala, projectades) ────────────────────────────

def _p(x, z, y=0.0):
    u, v, _ = CAM.projecta((x, y, z))
    return round(u), round(v)


def _rect_mon(*Ps):
    pts = [CAM.projecta(P) for P in Ps]
    return (max(0, round(min(p[0] for p in pts))), max(0, round(min(p[1] for p in pts))),
            min(W - 1, round(max(p[0] for p in pts))), min(BOTTOM, round(max(p[1] for p in pts))))


def _cantons(cx, cz, w, d, ang, marge=0.0):
    c, s_ = math.cos(ang), math.sin(ang)
    a, b = w / 2 + marge, d / 2 + marge
    return [(cx + lx * c - lz * s_, cz + lx * s_ + lz * c) for lx, lz in ((-a, -b), (a, -b), (a, b), (-a, b))]


def _rect_fons(fx0, fy0, fx1, fy1):
    return _rect_mon(_mon_fons(fx0, fy0), _mon_fons(fx1, fy1))


_T = _cantons(*TAULA[:4], TAULA[5])
_T2 = _cantons(*TAULA2[:4], TAULA2[5])


def _v(x, z):
    return CAM.projecta((x, 0, z))[1]


# El terra on es camina (al món): de la llar de foc a la paret del finestró, de davant la pica i la porta fins on
# comencen l'escala i el segon escriptori; la taula és un forat (s'hi fa la volta i s'hi passa per darrere).
_T2_DARRERE = max(_T2, key=lambda p: p[1])                         # el cantó de més al fons del segon escriptori
WALK_MON = [(24, 154), (LLAR_D + 14, LLAR[0] - 10), (LLAR_D + 14, 268), (PICA[1] + 8, 268), (CAIXA_POTS[1] + 8, ZW - 26), (XR - 16, ZW - 14),
            (XR - 16, 132), (round(_T2_DARRERE[0]) + 6, 152), (round(_T2_DARRERE[0]) - 14, 124), (300, 124)]
_WALK = [_p(x, z) for x, z in WALK_MON]
_V_FONS, _V_PROP = min(v for _, v in _WALK), max(v for _, v in _WALK)


def _escala_a(v):
    """L'escala d'un personatge amb els peus a la y de pantalla `v` (al terra, la profunditat només depèn de v)."""
    lo, hi = 1.0, 3000.0
    for _ in range(60):
        z = (lo + hi) / 2
        if CAM.projecta((200, 0, z))[1] > v:
            lo = z
        else:
            hi = z
    return CAM.escala((200, 0, (lo + hi) / 2))


FRONT = [
    {'id': 'davant_taula', 'mask': _amo({'taula'}),
     'baseline': round(sum(_v(x, z) for x, z in sorted(_T, key=lambda p: -p[1])[:2]) / 2), 'zIndex': 20},
    {'id': 'davant_escriptori', 'mask': _amo({'escriptori'}),
     'baseline': round(_v(*_T2_DARRERE)) + 2, 'zIndex': 20},
    {'id': 'davant', 'mask': _amo({'primer_pla'}), 'baseline': 999, 'zIndex': 20},
]

_LUM = CAM.projecta((XR - 10, 0, WIN_Z))

GEOMETRIA = {
    'things': {
        'porta': {'rect': _rect_fons(PL.DOOR[0] - 6, PL.DOOR[1] - 6, PL.DOOR[2] + 6, PL.DOOR[3]),
                  'walk': _p((PL.DOOR[0] + PL.DOOR[2]) / 2 - FX, ZW - 24)},
        'calaix': {'rect': _rect_mon(*[(x, TAULA[4] + 4, z) for x, z in _T], *[(x, 0, z) for x, z in _T]),
                   'walk': _p(TAULA[0] + 12, TAULA[1] - 58)},
        'videotelefon': {'rect': _rect_fons(360, 92, 410, 150), 'walk': _p(238, ZW - 26)},
        'quadre': {'rect': _rect_fons(PL.PIC[0] - 2, PL.PIC[1] - 8, PL.PIC[2] + 2, PL.PIC[3] + 2),
                   'walk': _p(TAULA[0] - 20, TAULA[1] - 62)},
        'caixa_forta': {'rect': _rect_fons(PL.SAFE[0] - 2, PL.SAFE[1] - 2, PL.SAFE[2] + 2, PL.SAFE[3] + 2),
                        'walk': _p(TAULA[0] - 20, TAULA[1] - 62)},
        'bol': {'rect': _rect_mon((BOL[0] - 14, 10, BOL[1]), (BOL[0] + 14, 0, BOL[1])),
                'walk': _p(BOL[0] + 36, BOL[1] - 14)},
        'pots': {'rect': _rect_fons(150, 36, 288, 125), 'walk': _p(112, ZW - 46)},
        'pica': {'rect': _rect_mon((PICA[0], PICA[2] + 24, ZW), (PICA[1], 0, PICA[3])), 'walk': _p(54, ZW - 50)},
    },
    'spawns': {'iri': _p(176, 190), 'vet': _p(250, 160)},
    'walkable': _WALK,
    'forats': [[_p(x, z) for x, z in _cantons(*TAULA[:4], TAULA[5], marge=8)]],
    # La càmera és a 1,65 m i el terra on es camina, a ≈4 m: el terra es veu aixafat.
    'floorSquash': 0.4,
    # L'ombra de contacte: la llum dominant és el sol del finestró (a la dreta): l'ombra cau cap a l'esquerra.
    'characterShadow': {'enabled': True, 'color': '#1e120c', 'alpha': 0.42, 'squash': 0.4, 'core': 0.6,
                        'light': {'x': round(_LUM[0]), 'y': round(_LUM[1]), 'stretch': 0.8, 'reach': 160}},
    'regions': [{'id': 'perspectiva', 'active': True, 'scaleEnabled': True, 'scaleWalkSpeed': True,
                 'scaleTop': round(_escala_a(_V_FONS - 2), 3), 'scaleBottom': round(_escala_a(_V_PROP + 2), 3),
                 'points': [(0, _V_FONS - 2), (W - 1, _V_FONS - 2), (W - 1, _V_PROP + 2), (0, _V_PROP + 2)]}],
}
