"""
El dipòsit d'aigua 2 de l'Arenga (Escena 7). EN 3D (hd640/tres_d.py), a 1×.

Una càmera alta, a tocar del sostre, que mira avall cap a la cantonada del fons a la dreta:
  - la paret del fons (el dibuix pla de sempre, projectat): l'epoxi blanc esquerdat i rovellat, la marca de l'aigua
    antiga, els reforços verticals i el **cartell** de 1984 «AIGUA NO POTABLE»;
  - l'**escala** de mà, en volum, que puja per la llum fins al **registre** del sostre (obert, des del rebost);
  - a la paret de la dreta, en escorç, els tubs; davant, separada de la paret, la carcassa del **filtre** (un cilindre
    d'acer amb la tapa de cargols, la placa FILTRE i el manòmetre), amb els tubs que hi entren i en surten;
  - a terra, la planxa soldada amb llot i el bassal on es reflecteix el registre;
  - primer pla: un tub gros que passa arran de terra i un reforç fosc a l'esquerra.
La llum: el feix que baixa del registre (pols a l'aire) i la taca de llum a terra; la resta, penombra freda.

El món: x a la dreta (0 = la paret de l'esquerra), y amunt (0 = el fons del dipòsit), z cap al fons (300 = la paret del
fons); 1 unitat = 1 píxel de sala a la distància on un personatge fa ≈110 px (escala 1).
"""
import functools
import math

import hd640  # noqa: F401  (abans de cap hd.rooms: posa la llibreria a 640×360)
from PIL import Image

from hd.pix import Canvas, Light, W, H, hr, mix, RUST, B4
from hd.rooms.arenga import DARK, WHITEP, BRASS, WARM
from hd.rooms.comu import _diff
from hd.rooms.exterior import fbm
from hd640.rooms import diposit2_pla_comu as PL
from hd640.rooms.diposit2_pla_comu import EPOXY, BOTTOMR, WATER, STEELF
from hd640.tres_d import Camera, Escena, Llum

BOTTOM = 259                                       # la sala acaba aquí (a sota, la barra de verbs)
ZW = 300                                           # la paret del fons
XR = 600                                           # la paret de la dreta
FY = PL.FLOOR_Y                                    # al dibuix pla, el terra (203)
CEIL = PL.CEIL                                     # al dibuix pla, on comença la paret (32)
HT = FY - CEIL                                     # l'alçada del dibuix pla de la paret (171)
HW = 236                                           # l'alçada del sostre
FX0 = 20                                           # al dibuix pla, la x que va a la x = 0 del món
REG = (300, ZW - 30)                               # el registre del sostre (x, z)
LAD = (288, 312, ZW - 12)                          # l'escala: x dels muntants, z
FIL = (528, 196, 25)                               # el filtre: x, z, radi
FIL_Y = (22, 78)                                   # el cos del filtre: de, a (alçada)
PUD = (318, 186, 116, 40)                          # el bassal: x, z, mitja amplada, mitja fondària
DRIP = (372, 192)                                  # on cau la gota (x, z)
_PH = {'t': 0.0}
SIGN_PLA = (73, 95, 206, 143)                      # el cartell, al dibuix pla
_SK = 1.2                                          # (al món, més gros que al pla: a 0,85 d'escala no es llegia)
_SC = ((SIGN_PLA[0] + SIGN_PLA[2]) / 2 - FX0, FY - (SIGN_PLA[1] + SIGN_PLA[3]) / 2 + 6)
SIGN = (_SC[0] - (SIGN_PLA[2] - SIGN_PLA[0]) * _SK / 2, _SC[0] + (SIGN_PLA[2] - SIGN_PLA[0]) * _SK / 2,
        _SC[1] - (SIGN_PLA[3] - SIGN_PLA[1]) * _SK / 2, _SC[1] + (SIGN_PLA[3] - SIGN_PLA[1]) * _SK / 2)   # x0, x1, y0, y1

CAM = Camera(pos=(200, 180, -220), yaw=0.18, pitch=0.13, f=420, centre=(320, 50))

LIGHT = Light(ambient=0.0, vignette=None, floor_fade=None)  # (la llum és la del món: la de l'Escena)
TL = Light(ambient=-0.2, vignette=None, floor_fade=None)     # la llum de les textures
LLUMS = [Llum((REG[0], HW - 6, REG[1]), 360, 2.6, power=1.4),          # el registre
         Llum((REG[0], 20, REG[1] - 50), 170, 1.2, power=1.6)]         # la taca de llum a terra, que rebota


def _cone(y):
    """El feix de llum del registre a l'alçada y: (x del centre, z del centre, mitja amplada)."""
    t = (HW - y) / HW
    return REG[0] + t * 6, REG[1] - t * 46, 26 + t * 66


# ─── Les textures ────────────────────────────────────────────────────────────

@functools.lru_cache(maxsize=None)
def _paret():
    """La paret de sempre (l'epoxi, les marques, el rovell) amb el cartell, de cara."""
    cv = Canvas(light=TL)
    PL.walls(cv)
    PL.sign(cv)
    return cv.img


@functools.lru_cache(maxsize=None)
def _filtre_pla():
    """La carcassa del filtre plana (en surten la placa i el manòmetre), sobre transparent."""
    cv = Canvas(light=TL, transparent=True)
    PL.filter_housing(cv)
    return cv.img


PLACA = (431, 152, 460, 163)                        # la placa FILTRE, al dibuix pla
MANO = (473, 150, 488, 174)                         # el manòmetre (amb el tub)
PW, PD = 2 * PUD[2], 2 * PUD[3]


def _bassal(ph=0.0):
    """El bassal vist des de dalt (una unitat del món per píxel): aigua fosca, la llum del registre reflectida (una
    franja que ve cap a la càmera) i les ones. Transparent fora de l'el·lipse."""
    img = Image.new('RGBA', (PW, PD), (0, 0, 0, 0))
    P = img.load()
    rx = REG[0] - (PUD[0] - PUD[2])                                   # on cau el reflex, a la textura
    for y in range(PD):
        for x in range(PW):
            e = ((x - PUD[2]) / (PUD[2] - 4 + hr(y // 3, 1) * 6)) ** 2 + ((y - PUD[3]) / PUD[3]) ** 2
            if e > 1:
                continue
            t = y / PD                                                # 0 = el cantó del fons (y de la textura = t)
            lv = 2.2 + (hr(x // 3, y // 2, 4) - 0.5) * 0.4
            c = WATER[max(0, min(len(WATER) - 1, int(lv + B4[y & 3][x & 3] - 0.5)))]
            wob = math.sin(y * 0.7 + ph) * 2.2
            half = 14 - t * 6
            d = abs(x - rx - wob + (t - 0.3) * 30)
            if d < half and (y % 2 == 0 or d < 5):
                c = mix(c, WARM, 0.55 * (1 - d / half))               # el registre, reflectit
            if math.sin(x * 0.2 + y * 0.9 - ph) > 0.93:
                c = mix(c, (120, 150, 140), 0.25)                     # les ones
            if e > 0.82:
                c = mix(c, (70, 88, 84), 0.3)                         # la vora mullada, més clara
            P[x, y] = tuple(c[:3]) + (255,)
    return img


# ─── Les superfícies ────────────────────────────────────────────────────────

def _epoxi(lvl0, seed, marca=True, reforc=99):
    """L'epoxi procedural (on el dibuix pla no arriba): els reforços, les soldadures, la marca de l'aigua i el rovell.
    s, t: unitats del món des del cantó de dalt; `P`: el punt (per saber l'alçada)."""
    def L(s, t, P):
        y = P[1]
        v = lvl0 + (hr(int(s) // 4, int(t) // 6, seed) - 0.5) * 0.4 + (fbm(s / 40, t / 30, seed) - 0.5) * 0.6
        d = (s + 4) % reforc
        if d < 9:
            v += 1.0 if d < 1 else 0.5 if d < 4 else -0.4 if d >= 7 else 0
        elif d < 14:
            v -= 0.5
        if abs(y - 62) < 1 or abs(y - 124) < 1:
            v -= 1.2
        if marca and y < 120:
            v -= 0.5 + (120 - y) / 120 * 0.5                          # la brutícia de l'aigua antiga
            if abs(y - 120 - math.sin(s * 0.05) * 1.6) < 1.2:
                v -= 1.0
        if hr(int(s) // 2, 9, seed) > 0.92 and (t % 70) < 30 * hr(int(s) // 2, 8, seed):
            v -= 0.6                                                   # regalims de rovell
        return v
    return L


def _terra(s, t, P):
    """El fons del dipòsit: planxes amb el cordó de soldadura, llot i taques d'aigua."""
    x, z = P[0], P[2]
    v = 2.4 + (hr(int(x) // 4, int(z) // 3, 12) - 0.5) * 0.4 + (fbm(x / 60, z / 40, 7) - 0.5) * 1.0
    if x % 120 < 1.5 or z % 96 < 1.5:
        v = 1.0
    elif x % 120 < 3 or z % 96 < 3:
        v += 0.9                                                       # el cordó
    if hr(int(x) // 6, int(z) // 3, 13) > 0.94:
        v -= 0.8                                                       # llot
    return v


def cilindre(e, sid, cx, cz, r, y0, y1, ramp, lvl, n=24):
    """Un cilindre dret: les cares del voltant (les que es veuen) i la tapa. `lvl(a, s, t, P)`."""
    for k in range(n):
        a0, a1 = 2 * math.pi * k / n, 2 * math.pi * (k + 1) / n
        P0 = (cx + r * math.cos(a0), y1, cz + r * math.sin(a0))
        P1 = (cx + r * math.cos(a1), y1, cz + r * math.sin(a1))
        e.quad(sid, P0, P1, (P1[0], y0, P1[2]), (P0[0], y0, P0[2]), ramp=ramp,
               lvl=lambda s, t, P, a=(a0 + a1) / 2: lvl(a, s, t, P))
    e.quad(sid, (cx - r, y1, cz + r), (cx + r, y1, cz + r), (cx + r, y1, cz - r), (cx - r, y1, cz - r), ramp=ramp,
           lvl=lambda s, t, P: lvl(None, s, t, P) + 0.6, forma=lambda s, t: (s - r) ** 2 + (t - r) ** 2 < r * r)


def escena(cv, tex, estat=frozenset()):
    """Tota la sala, de lluny a prop. → l'Escena (qui ha pintat què)."""
    e = Escena(cv, CAM, LLUMS, ambient=-0.3)
    zn = CAM.pos[2] + 40
    paret = tex['paret']
    # la paret del fons: l'epoxi de dalt (sense la marca), i el dibuix pla (x 20..620 → 0..600)
    e.quad('paret_fons_dalt', (-40, HW, ZW), (XR, HW, ZW), (XR, HT, ZW), (-40, HT, ZW), ramp=EPOXY,
           lvl=_epoxi(3.2, 31, marca=False))
    e.quad('paret_fons', (0, HT, ZW), (XR, HT, ZW), (XR, 0, ZW), (0, 0, ZW), tex=(paret, (FX0, CEIL, FX0 + XR, FY)))
    # el cartell, una mica més gros que al pla (perquè es llegeixi a aquesta distància), amb la seva ombra
    sx0, sx1, sy0, sy1 = SIGN
    e.foscor('ombra_cartell', (sx0 + 2, sy1 - 3, ZW - 0.6), (sx1 + 5, sy1 - 3, ZW - 0.6), (sx1 + 5, sy0 - 4, ZW - 0.6),
             (sx0 + 2, sy0 - 4, ZW - 0.6), lambda s, t: 0.45)
    e.quad('cartell', (sx0, sy1, ZW - 1.5), (sx1, sy1, ZW - 1.5), (sx1, sy0, ZW - 1.5), (sx0, sy0, ZW - 1.5),
           tex=(paret, SIGN_PLA))
    # la paret de l'esquerra (x = 0) i la de la dreta (x = 600), en escorç
    e.quad('paret_esq', (0, HW, zn), (0, HW, ZW), (0, 0, ZW), (0, 0, zn), ramp=EPOXY, lvl=_epoxi(2.8, 33))
    e.quad('paret_dreta_dalt', (XR, HW, ZW), (XR, HW, zn), (XR, HT, zn), (XR, HT, ZW), ramp=EPOXY,
           lvl=_epoxi(3.0, 34, marca=False))
    e.quad('paret_dreta', (XR, HT, ZW), (XR, HT, ZW - 300), (XR, 0, ZW - 300), (XR, 0, ZW),
           tex=(paret, (330, CEIL, 630, FY)))
    e.quad('paret_dreta_prop', (XR, HT, ZW - 300), (XR, HT, zn), (XR, 0, zn), (XR, 0, ZW - 300), ramp=EPOXY,
           lvl=_epoxi(2.8, 35))
    # el terra
    e.quad('terra', (0, 0, ZW), (XR, 0, ZW), (XR, 0, zn), (0, 0, zn), ramp=BOTTOMR, lvl=_terra)
    # el bassal (textura des de dalt, que l'animació torna a projectar)
    px, pz, prx, prz = PUD
    e.quad('bassal', (px - prx, 0.3, pz + prz), (px + prx, 0.3, pz + prz), (px + prx, 0.3, pz - prz),
           (px - prx, 0.3, pz - prz), tex=(tex['bassal'], (0, 0, PW, PD), 1))
    # la taca de llum del registre, a terra i a la paret del fons; la foscor dels racons
    cx, cz, hw = _cone(0)
    e.claror((cx - 160, 0.5, cz + 120), (cx + 160, 0.5, cz + 120), (cx + 160, 0.5, cz - 120), (cx - 160, 0.5, cz - 120),
             (255, 220, 150), lambda s, t: 0.4 * max(0.0, 1 - math.hypot(s - 160, (t - 120) * 1.15) / 150) ** 1.3)
    e.claror((REG[0] - 140, HW, ZW - 0.4), (REG[0] + 140, HW, ZW - 0.4), (REG[0] + 140, 0, ZW - 0.4),
             (REG[0] - 140, 0, ZW - 0.4), (255, 214, 150),
             lambda s, t: 0.3 * max(0.0, 1 - abs(s - 140) / (36 + t * 0.4)) * max(0.0, 1 - t / 300))
    e.foscor('racons', (0, 0.5, ZW), (XR, 0.5, ZW), (XR, 0.5, zn), (0, 0.5, zn),
             lambda s, t: max(0.6 * max(0.0, 1 - t / 34), 0.6 * max(0.0, 1 - s / 34), 0.6 * max(0.0, 1 - (XR - s) / 34)))
    e.foscor('racons_v', (0.5, HW, ZW - 70), (0.5, HW, ZW), (0.5, 0, ZW), (0.5, 0, ZW - 70),
             lambda s, t: 0.5 * max(0.0, 1 - (70 - s) / 70))
    e.foscor('racons_v2', (XR - 70, HW, ZW - 0.5), (XR, HW, ZW - 0.5), (XR, 0, ZW - 0.5), (XR - 70, 0, ZW - 0.5),
             lambda s, t: 0.5 * max(0.0, 1 - (70 - s) / 70))
    e.foscor('sostre_fosc', (-40, HW, ZW - 0.6), (XR, HW, ZW - 0.6), (XR, 0, ZW - 0.6), (-40, 0, ZW - 0.6),
             lambda s, t: 0.5 * max(0.0, 1 - t / 70) * (0 if abs(s - 40 - REG[0]) < 50 else 1))
    # l'escala de mà, del registre a terra: dos muntants, els graons i les grapes a la paret
    x0, x1, lz = LAD
    e.foscor('ombra_escala', (x0 - 10, 0.6, ZW), (x1 + 16, 0.6, ZW), (x1 + 16, 0.6, lz - 10), (x0 - 10, 0.6, lz - 10),
             lambda s, t: 0.5)
    for y in range(13, HW + 20, 13):
        e.caixa('escala', x0 + 2, x1 - 2, y - 1, y + 1, lz - 1.2, lz + 1.2, STEELF, 3.6,
                cares={'dalt': {'ramp': STEELF, 'lvl': 5.0}})
    for xx in (x0, x1 - 3):
        e.caixa('escala', xx, xx + 3, 0, HW + 30, lz - 1.5, lz + 1.5, STEELF, 3.2,
                cares={'esquerra': {'ramp': STEELF, 'lvl': 4.0}, 'davant': {'ramp': STEELF, 'lvl': 3.4}})
        for y in (60, 150):
            e.caixa('escala', xx, xx + 3, y, y + 3, lz + 1.5, ZW, STEELF, 2.4)
    # el filtre: els tubs, el peu, el cos (un cilindre), la tapa amb els cargols, la placa i el manòmetre
    fx, fz, fr = FIL
    y0, y1 = FIL_Y
    e.foscor('ombra_filtre', (fx - 60, 0.6, fz + 40), (fx + 30, 0.6, fz + 40), (fx + 30, 0.6, fz - 50), (fx - 60, 0.6, fz - 50),
             lambda s, t: 0.6 * max(0.0, 1 - ((s - 52) / 40) ** 2 - ((t - 46) / 36) ** 2) * 1.5)
    e.tub('tubs', (fx, 98, ZW), (fx, 98, fz + fr - 4), 5, STEELF, 3.0, brides=40)                 # l'entrada
    e.tub('tubs', (fx, 98, ZW - 2), (fx, HW + 10, ZW - 2), 5, STEELF, 2.8, brides=60)
    e.tub('tubs', (XR, 44, fz), (fx + fr - 4, 44, fz), 5, STEELF, 3.0, brides=36)                  # la sortida
    e.tub('tubs', (XR - 3, 44, fz - 30), (XR - 3, 0, fz - 30), 5, STEELF, 2.6)
    e.caixa('filtre', fx - 16, fx + 16, 0, y0, fz - 16, fz + 16, STEELF, 2.4,
            cares={'dalt': {'ramp': STEELF, 'lvl': 3.4}})
    e.caixa('filtre', fx - fr - 4, fx + fr + 4, 0, 4, fz - fr - 4, fz + fr + 4, STEELF, 2.0)

    def cos(a, s, t, P):
        v = 3.0 - (0.9 if abs(P[1] - 40) < 0.8 or abs(P[1] - 62) < 0.8 else 0)
        if a is not None and hr(int(a * 20), int(P[1]) // 3, 8) > 0.9 and P[1] > 30:
            v -= 0.6                                                   # el rovell que regalima de la tapa
        return v
    cilindre(e, 'filtre', fx, fz, fr, y0, y1, STEELF, cos)
    cilindre(e, 'filtre', fx + 1, fz, fr + 4, y1, y1 + 5, STEELF, lambda a, s, t, P: 3.8)
    for k in range(12):
        a = 2 * math.pi * k / 12
        bx, bz = fx + 1 + math.cos(a) * (fr + 1.5), fz + math.sin(a) * (fr + 1.5)
        e.caixa('filtre', bx - 1.2, bx + 1.2, y1 + 5, y1 + 7, bz - 1.2, bz + 1.2, STEELF, 4.6)
    e.caixa('filtre', fx - 5, fx + 7, y1 + 9, y1 + 13, fz - 2, fz + 2, STEELF, 4.4)                # la maneta
    for xx in (fx - 3, fx + 5):
        e.caixa('filtre', xx - 1, xx + 1, y1 + 5, y1 + 9, fz - 1, fz + 1, STEELF, 3.0)
    ang = math.atan2(CAM.pos[2] - fz, CAM.pos[0] - fx)                                                 # cap a la càmera
    nx, nz = math.cos(ang), math.sin(ang)
    tx, tz = -nz, nx
    pw, ph = (PLACA[2] - PLACA[0]) / 2, PLACA[3] - PLACA[1]
    c = (fx + nx * (fr + 0.6), 55, fz + nz * (fr + 0.6))
    e.quad('filtre', (c[0] - tx * pw, c[1] + ph / 2, c[2] - tz * pw), (c[0] + tx * pw, c[1] + ph / 2, c[2] + tz * pw),
           (c[0] + tx * pw, c[1] - ph / 2, c[2] + tz * pw), (c[0] - tx * pw, c[1] - ph / 2, c[2] - tz * pw),
           tex=(tex['filtre'], PLACA))
    mp = (fx + nx * (fr + 3) - tx * (fr + 6), 32, fz + nz * (fr + 3) - tz * (fr + 6))
    e.sprite('filtre', tex['filtre'].crop(MANO), (480 - MANO[0], MANO[3] - MANO[1]), mp)
    # primer pla: un tub gros que passa arran de terra i un reforç fosc a l'esquerra
    FOSC = [(4, 5, 6), (8, 10, 11), (14, 16, 17), (22, 25, 26), (32, 36, 36), (46, 50, 50)]
    e.tub('primer_pla', (-60, 12, 14), (XR + 60, 12, 14), 12, FOSC, 2.6, brides=110)
    e.caixa('primer_pla', 92, 112, 0, HW, 20, 40, FOSC, 1.6,
            cares={'dreta': {'ramp': FOSC, 'lvl': lambda s, t, P: 2.6 + (1.4 if int(t) % 16 == 0 else 0)},
                   'davant': {'ramp': FOSC, 'lvl': lambda s, t, P: 1.4 + (1.6 if s > 18 else 0)}})
    # molt a prop de la càmera, a les dues cantonades de baix: una biga en I del buc (a la dreta) i una canonada
    # vertical gruixuda amb brides (a l'esquerra), en silueta; només un fil de llum a la vora que mira el focus
    bx, bz = 400, -56
    vora = {'ramp': FOSC, 'lvl': lambda s, t, P: 1.4 + (3.6 if s < 1.5 else 0)}
    e.caixa('primer_pla', bx - 11, bx + 11, 0, HW + 60, bz - 3, bz + 3, FOSC, 1.0, cares={'esquerra': vora})
    e.caixa('primer_pla', bx - 3, bx + 3, 0, HW + 60, bz + 3, bz + 30, FOSC, 1.2, cares={'esquerra': vora})
    e.caixa('primer_pla', bx - 11, bx + 11, 0, HW + 60, bz + 30, bz + 36, FOSC, 1.0, cares={'esquerra': vora})
    for y in range(20, HW, 46):                                     # els reblons
        e.caixa('primer_pla', bx - 8, bx + 8, y, y + 3, bz - 4.5, bz - 3, FOSC, 2.0)
    e.tub('primer_pla', (122, -10, -64), (122, HW + 60, -64), 11, FOSC, 2.6, brides=52, llum_dir=(1.0, 0.4))
    e.silueta({'primer_pla'}, 0.12, col=(2, 3, 4))
    return e


# ─── Composició ────────────────────────────────────────────────────────────

def _proj(P):
    u, v, _ = CAM.projecta(P)
    return u, v


@functools.lru_cache(maxsize=None)
def _textures():
    return {'paret': _paret(), 'filtre': _filtre_pla(), 'bassal': _bassal()}


def _beam(cv):
    """El feix de llum del registre (pols a l'aire), en pantalla: un trapezi entre el sostre i el terra."""
    rows = []
    for k in range(0, 41):
        y = HW * (1 - k / 40)
        cx, cz, hw = _cone(y)
        u, v = _proj((cx, y, cz))
        rows.append((v, u, hw * CAM.escala((cx, y, cz))))
    for (va, ua, wa), (vb, ub, wb) in zip(rows, rows[1:]):
        for Y in range(max(0, int(va)), min(BOTTOM, int(vb) + 1)):
            f = (Y - va) / max(1e-3, vb - va)
            uc, w = ua + (ub - ua) * f, wa + (wb - wa) * f
            for X in range(max(0, int(uc - w)), min(W, int(uc + w) + 1)):
                b = max(0.0, 1 - abs(X - uc) / w) ** 1.4
                k = 0.24 * b * (1 - Y / 400)
                if hr(X, Y, 55) > 0.996:
                    k = 0.55                                           # pols suspesa
                if k > 0.02:
                    cv.flat(X, Y, mix(cv.get(X, Y), (255, 228, 170), k))


def _render(estat=frozenset(), tex=None):
    cv = Canvas(light=LIGHT)
    e = escena(cv, tex or _textures(), estat)
    _beam(cv)
    u, v = _proj((REG[0], HW, REG[1]))
    cv.glow(u, max(v, -10), 70, WARM, 0.45)
    cv.rect(0, BOTTOM + 1, W - 1, H - 1, [(0, 0, 0)], 0, lit=0)    # la barra de verbs: negre
    return cv.img, e


@functools.lru_cache(maxsize=None)
def _base():
    return _render()


def bg(cv):
    cv.img.paste(_base()[0])
    cv.P = cv.img.load()


PROPS = {}


# ─── Animacions ─────────────────────────────────────────────────────────────

def _frames_gota():
    """Una gota que es forma al sostre, cau al bassal i hi fa una rodoneta."""
    img, _ = _base()
    gx, gz = DRIP
    seq = [('f', 0), ('f', 1), ('f', 2), ('f', 3)] + [('c', k / 7) for k in range(1, 8)] \
        + [('r', 2), ('r', 4), ('r', 6), ('r', 8)] + [('n', 0)] * 30
    frames = []
    for kind, v in seq:
        cv = Canvas(light=LIGHT, img=img.copy())
        if kind == 'f':                                     # es forma (si el sostre es veu: si no, al cantó de dalt)
            u, y0 = _proj((gx, HW, gz))
            u, y0 = round(u), max(0, round(y0))
            for k in range(v + 1):
                cv.flat(u, y0 + k, (150, 180, 180) if k < v else (200, 220, 220))
        elif kind == 'c':                                   # cau, cada cop més de pressa
            u, y = _proj((gx, HW * (1 - v * v), gz))
            u, y = round(u), round(y)
            if 1 <= y < BOTTOM - 1:
                cv.flat(u, y, (190, 210, 210))
                cv.flat(u, y + 1, (160, 186, 186))
                cv.flat(u, y - 1, (110, 140, 140))
        elif kind == 'r':                                   # rodoneta
            for a in range(0, 360, 12):
                u, y = _proj((gx + math.cos(math.radians(a)) * v * 1.4, 0.3, gz + math.sin(math.radians(a)) * v * 1.4))
                x, y = round(u), round(y)
                cv.flat(x, y, mix(cv.get(x, y), (160, 190, 180), 0.5 - v * 0.04))
        frames.append(_diff(cv.img, img))
    return frames


def _frames_bassal():
    """L'aigua del bassal: el reflex del registre ondula i les ratlles de llum corren (bucle de 12)."""
    img, e = _base()
    frames = []
    for i in range(12):
        out = img.copy()
        out.alpha_composite(e.capa(_bassal(2 * math.pi * i / 12), {'bassal'}))
        frames.append(_diff(out, img))
    return frames


def _frames_pols():
    """Motes de pols que suren lentament dins el feix del registre i fan pampallugues."""
    img, _ = _base()
    n, motes = 48, []
    for k in range(40):
        y = 6 + hr(k, 1, 88) * (HW - 12)
        cx, cz, hw = _cone(y)
        P = (cx + (hr(k, 2, 88) - 0.5) * hw * 1.4, y, cz + (hr(k, 7, 88) - 0.5) * hw)
        u, v = _proj(P)
        s = CAM.escala(P)
        motes.append((u, v, (3 + hr(k, 3, 88) * 7) * s, (4 + hr(k, 4, 88) * 8) * s, hr(k, 5, 88) * 6.283,
                      1 + int(hr(k, 6, 88) * 2), _proj((cx, y, cz))[0], hw * s))
    frames = []
    for i in range(n):
        cv = Canvas(light=LIGHT, img=img.copy())
        a = 2 * math.pi * i / n
        for (x0, y0, ax, ay, ph, sp, ccx, hw) in motes:
            x = round(x0 + math.sin(a * sp + ph) * ax)
            y = round(y0 + math.sin(a + ph * 1.7) * ay)
            b = max(0.0, 1 - abs(x - ccx) / hw)
            tw = 0.5 + 0.5 * math.sin(a * 3 + ph * 2)
            if b > 0.15 and tw > 0.25 and 0 <= x < W and 0 <= y < BOTTOM:
                cv.flat(x, y, mix(cv.get(x, y), (255, 236, 190), min(0.75, 0.35 + b * 0.5 * tw)))
        frames.append(_diff(cv.img, img))
    return frames


ANIMS = {'gota': {'frames': _frames_gota, 'frameDuration': 90},
         'bassal': {'frames': _frames_bassal, 'frameDuration': 200},
         'pols': {'frames': _frames_pols, 'frameDuration': 130}}


# ─── Capes del davant ─────────────────────────────────────────────────────

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
    {'id': 'davant_filtre', 'mask': _amo({'filtre'}), 'baseline': _p(FIL[0], FIL[1])[1], 'zIndex': 20},
]


# ─── Geometria (coordenades de sala, projectades) ────────────────────────────

def _rect_mon(*Ps):
    pts = [CAM.projecta(P) for P in Ps]
    return (max(0, round(min(p[0] for p in pts))), max(0, round(min(p[1] for p in pts))),
            min(W - 1, round(max(p[0] for p in pts))), min(BOTTOM, round(max(p[1] for p in pts))))


def _escala_a(v):
    lo, hi = 1.0, 3000.0
    for _ in range(60):
        z = (lo + hi) / 2
        if CAM.projecta((300, 0, z))[1] > v:
            lo = z
        else:
            hi = z
    return CAM.escala((300, 0, (lo + hi) / 2))


def _z_v(x, v):
    lo, hi = -100.0, 2000.0
    for _ in range(50):
        z = (lo + hi) / 2
        if CAM.projecta((x, 0, z))[1] > v:
            lo = z
        else:
            hi = z
    return round((lo + hi) / 2)


V_PROP = 214                                       # on es camina més a prop (escala ≈1,2)
WALK_MON = ([(16, 284), (LAD[0] - 8, 284), (LAD[0] - 8, 276), (LAD[1] + 8, 276), (LAD[1] + 8, 284), (482, 284),
             (482, 242), (584, 242)]
            + [(x, _z_v(x, V_PROP)) for x in (584, 460, 330, 200)] + [(16, _z_v(16, V_PROP))])
_WALK = [_p(x, z) for x, z in WALK_MON]
_V_FONS, _V_PROP = min(v for _, v in _WALK), max(v for _, v in _WALK)
_FORATS = [[_p(FIL[0] + math.cos(a) * (FIL[2] + 12), FIL[1] + math.sin(a) * (FIL[2] + 10))
            for a in [k * math.pi / 5 for k in range(10)]]]

GEOMETRIA = {
    'things': {
        'registre': {'rect': _rect_mon((LAD[0] - 10, 0, LAD[2]), (LAD[1] + 10, HW, LAD[2]), (REG[0], HW, REG[1] - 30)),
                     'walk': _p(LAD[1] + 34, LAD[2] - 22)},    # (a la dreta de l'escala: davant, la tapava)
        'filtre': {'rect': _rect_mon(*[(FIL[0] + dx, y, FIL[1] + dz) for dx in (-FIL[2] - 6, FIL[2] + 6)
                                       for dz in (-FIL[2] - 6, FIL[2] + 6) for y in (0, FIL_Y[1] + 14)]),
                   'walk': _p(FIL[0] - 50, FIL[1] - 40)},
        'cartell': {'rect': _rect_mon((SIGN[0] - 2, SIGN[3] + 2, ZW), (SIGN[1] + 2, SIGN[2] - 2, ZW)),
                    'walk': _p((SIGN[0] + SIGN[1]) / 2, ZW - 30)},
    },
    'spawns': {'iri': _p(REG[0] - 96, 236), 'vet': _p(REG[0] + 110, 240)},
    'walkable': _WALK,
    'forats': _FORATS,
    'floorSquash': 0.42,
    # L'ombra de contacte: la llum dominant és la del registre (la taca de terra a sota).
    'characterShadow': {'enabled': True, 'color': '#06080a', 'alpha': 0.48, 'squash': 0.4, 'core': 0.6,
                        'light': {'x': _p(_cone(0)[0], _cone(0)[1])[0], 'y': _p(_cone(0)[0], _cone(0)[1])[1],
                                  'stretch': 0.8, 'reach': 150}},
    'regions': [{'id': 'perspectiva', 'active': True, 'scaleEnabled': True, 'scaleWalkSpeed': True,
                 'scaleTop': round(_escala_a(_V_FONS - 2), 3), 'scaleBottom': round(_escala_a(_V_PROP + 2), 3),
                 'points': [(0, _V_FONS - 2), (W - 1, _V_FONS - 2), (W - 1, _V_PROP + 2), (0, _V_PROP + 2)]}],
    'characterLights': {
        'ambient': '#6a7472',                                                           # penombra freda
        'lights': [{'x': _p(REG[0], REG[1] - 40, HW - 40)[0], 'y': _p(REG[0], REG[1] - 40, HW - 40)[1],
                    'radius': 260, 'color': '#ffe0a0', 'intensity': 1.1}],
    },
}
