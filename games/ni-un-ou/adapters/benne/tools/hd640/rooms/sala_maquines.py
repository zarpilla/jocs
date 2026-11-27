"""
La sala de màquines de l'Arenga. EN 3D (hd640/tres_d.py), a 1×.

Una càmera alta, a la dreta, que mira de biaix la cantonada del fons a l'esquerra:
  - a la paret de l'esquerra, en escorç: la **porta del passadís** (oberta, amb la fulla estanca girada cap a la sala
    i el llum d'emergència vermell), el cartell **MARPOL** i el **tub de veu** (la boca, amb la placa PONT);
  - a la paret del fons: la porta del **rebost** (tancada), el **quadre** (un armari amb volum), l'alarma amb el
    **sensor** desendollat, la vàlvula de **tres vies**, el **separador** (dret, separat de la paret) i la porta del
    **taller** (oberta, amb la fulla girada); damunt del quadre, l'**altell** de reixa amb la barana groga i el
    **generador**;
  - el **motor** principal, separat de la paret, amb les tres cares: el càrter, el bloc, les culates, el col·lector
    folrat (on seu en Diu), la xemeneia que puja al sostre, el turbo i la protecció ratllada del volant;
  - a terra: el forat de la **vàlvula** de presa de mar (amb la planxa recolzada contra la bancada), el registre de
    la **sentina** i la bomba de sentina, una mica girada;
  - primer pla: l'escala de l'escotilla a l'esquerra (s'hi passa per darrere), canonades i una safata de cables
    fosques que travessen per dalt, i dos bidons a baix a la dreta.

Tot el detall ve del dibuix pla de sempre (sala_maquines_pla_comu.py), projectat. Els decorats (l'aigua, el volant
improvisat, la brida, el fosc, la sentina oberta) i les animacions es fan amb la mateixa escena: la diferència amb el
fons, o el dibuix pla projectat per les superfícies.

El món: x a la dreta (0 = la paret del passadís), y amunt (0 = el terra), z cap al fons (300 = la paret del fons);
1 unitat = 1 píxel de sala a la distància on un personatge fa ≈110 px (escala 1).
"""
import functools
import math

import hd640  # noqa: F401  (abans de cap hd.rooms: posa la llibreria a 640×360)
from PIL import Image

from hd.pix import Canvas, Light, W, H, hr, mix
from hd.rooms.arenga import (ENG, ENG_LIGHT, DECK, CAB, LAG, REDP, YELL, SEAG, FUEL, DARK, WHITEP, BRASS,
                             WARM, RED_GLOW, box, bolt, hpipe, vpipe)
from hd.rooms.comu import _diff, text, text_width
from hd.rooms.exterior import fbm
from hd640.rooms import sala_maquines_pla_comu as PL
from hd640.tres_d import Camera, Escena, Llum

BOTTOM = 259                                       # la sala acaba aquí (a sota, la barra de verbs)
ZW = 300                                           # la paret del fons
HW = PL.FLOOR_Y                                    # l'alçada de les parets (el dibuix pla fa 203 fins al terra)
XL = 170                                           # al dibuix pla, la cantonada: a l'esquerra, la paret del passadís
XR = 540                                           # la paret de la dreta (la del taller fa cantonada amb aquesta)
ZN = -260                                          # on s'acaben, cap a la càmera, el terra, el sostre i la paret
EK = 0.86                                          # el motor, una mica més petit que al pla (no tapa el rebost)
EX0 = 52                                           # on comença el motor (x del món del cantó esquerre del volant)
EZ = (196, 262)                                    # el motor: el davant i el darrere (z)
LADDER = (6, 40, 112, 20)                          # l'escala: x0, x1, z del peu, z de dalt (puja cap a la càmera)
PUMP = (318, 206, -0.28)                           # la bomba de sentina: x, z del centre, gir
VALVE = (178, 158)                                 # la vàlvula de presa de mar (x, z de l'eix)
SENT = (62, 120, 128, 162)                         # el registre de la sentina: x0, x1, z0, z1
DRUMS = ((466, 118), (506, 146))                   # els bidons del primer pla (x, z)
LAMPS = ((150, 172), (360, 196))                   # les dues bombetes del sostre (x, z)
MEZZ_H = HW - PL.MEZZ_Y                            # l'alçada del pis de l'altell
MEZZ_D = 46                                        # el fons de l'altell


def _w(fx):
    """Una x del dibuix pla de la paret del fons → la x del món."""
    return fx - XL


def _wz(fx):
    """Una x del dibuix pla de la paret del passadís → la z del món."""
    return ZW - XL + fx


def _y(fy):
    """Una y del dibuix pla (el terra, a 203) → l'alçada del món."""
    return HW - fy


def _ex(fx):
    """Una x del dibuix pla del motor → la x del món."""
    return EX0 + (fx - 163) * EK


def _ey(fy):
    """Una y del dibuix pla del motor → l'alçada del món."""
    return (HW - fy) * EK


CAM = Camera(pos=(330, 185, -170), yaw=-0.22, pitch=0.18, f=360, centre=(318, 96))

LIGHT = Light(ambient=0.0, vignette=None, floor_fade=None)  # (la llum és la del món: la de l'Escena)
TEXL = Light(ambient=0.7, vignette=None, floor_fade=None)  # les textures: llum plana (la fa l'escena)
LLUMS = [Llum((LAMPS[0][0], 176, LAMPS[0][1]), 290, 2.4, power=1.4),
         Llum((LAMPS[1][0], 176, LAMPS[1][1]), 250, 2.2, power=1.4),
         Llum((_w(461), MEZZ_H - 14, ZW - 18), 120, 1.6, power=1.6),        # el llum de sota l'altell
         Llum((6, 124, _wz(45)), 80, 0.8, power=2.0),                       # l'emergència, sobre la porta
         Llum((_w(599), 80, ZW + 30), 120, 0.9, power=1.8)]                 # el fluorescent del taller

FOSC = [(3, 4, 6), (7, 9, 12), (12, 15, 19), (18, 22, 27), (26, 31, 37), (36, 42, 49)]
STEELG = PL.STEELG


# ─── Les textures: el dibuix pla de sempre ───────────────────────────────────

def _canonades(cv):
    """Les canonades de la paret (com les del pla, però de punta a punta: també passen per la paret del passadís)."""
    hpipe(cv, 0, W - 1, 53, 4, SEAG, 3.0, bands=range(17, W, 61), band_ramp=WHITEP)
    hpipe(cv, 0, W - 1, 68, 3, FUEL, 3.0, bands=range(46, W, 61), band_ramp=YELL)
    for x in range(17, W, 61):                            # fletxes del sentit, a les anelles
        for i in range(3):
            cv.vline(x + 4 + i, 53 - 2 + i, 53 + 2 - i, WHITEP, 4.4)
    for x in range(3, W, 64):                             # abraçadores
        cv.vline(x, 47, 59, CAB, 2.0)
        cv.vline(x + 1, 47, 59, CAB, 3.4)
        cv.vline(x, 64, 72, CAB, 2.0)
        cv.vline(x + 1, 64, 72, CAB, 3.4)
    vpipe(cv, 425, 53, HW + 2, 3, SEAG, 2.8, bands=(128, 171), band_ramp=WHITEP)
    cv.disc(425, 57, 4, 4, SEAG, lambda nx, ny: 3.2 - nx - ny)


def _vies(cv):
    """La canonada de la bomba, la vàlvula de tres vies i les plaques (al pla, eren part del separador)."""
    vpipe(cv, 517, 189, HW, 3, CAB, 2.8)
    hpipe(cv, 517, 524, 187, 3, CAB, 3.0)
    vpipe(cv, 517, 109, 181, 3, CAB, 2.6)
    cv.disc(517, 187, 7, 7, REDP, lambda nx, ny: 3.8 - nx - ny)
    cv.line(517, 187, 524, 195, REDP, 4.6)
    cv.line(518, 187, 525, 195, REDP, 3.2)
    cv.disc(517, 187, 2, 2, CAB, 4.4)
    box(cv, 512, 165, 523, 171, WHITEP, 3.0)                          # BORDA (a dalt)
    cv.poly([(517, 166), (520, 170), (514, 170)], DARK, 1.0)


BOCA = 105                                         # el tub de veu, al pla (més cap a la porta que abans: el motor el tapava)


def _tub_veu(cv, x=BOCA):
    """El tub de veu (com el del pla, a `x`): baixa del sostre, la boca de llautó, la cadeneta i la placa PONT."""
    vpipe(cv, x, 27, 139, 3, BRASS, 2.8)
    for y in (45, 99):
        box(cv, x - 4, y, x + 4, y + 3, CAB, 3.2)
    cv.disc(x, 144, 5, 5, BRASS, lambda nx, ny: 3.2 - nx * 1.2 - ny * 1.0)
    cv.disc(x, 149, 9, 8, BRASS, lambda nx, ny: 3.5 - nx * 1.3 - ny * 1.2)
    cv.disc(x, 149, 7, 5, BRASS, lambda nx, ny: 1.2 + nx * 0.6 + ny * 0.8)
    cv.disc(x, 149, 4, 3, DARK, 0.6)
    for i, y in enumerate(range(158, 169)):
        cv.put(x + 6 + (i % 2), y, BRASS, 3.0 if i % 2 else 4.0)
    cv.disc(x + 8, 172, 4, 3, BRASS, lambda nx, ny: 3.8 - nx - ny)
    box(cv, x + 1, 178, x + 23, 186, BRASS, 3.0)
    text(cv, 'PONT', x + 12 - text_width('PONT') // 2, 180, BRASS, 0.8)


def _paret_llisa():
    cv = Canvas(light=TEXL)
    PL.wall(cv)
    PL.ceiling(cv)
    _canonades(cv)
    return cv


@functools.lru_cache(maxsize=None)
def _llisa():
    return _paret_llisa().img


@functools.lru_cache(maxsize=None)
def _paret():
    """Les dues parets planes, de cara: les portes, el tub de veu, el MARPOL, l'alarma i la vàlvula de tres vies."""
    cv = _paret_llisa()
    PL.door_passadis(cv)
    PL.door_rebost(cv)
    PL.door_taller(cv)
    _tub_veu(cv)
    PL.marpol(cv)
    PL.alarm(cv)
    _vies(cv)
    llisa = _llisa()
    for bx in ((0, 84, 18, HW), (622, 80, W, HW)):                  # les fulles obertes: es fan en 3D
        cv.img.paste(llisa.crop(bx), bx[:2])
    cv.P = cv.img.load()
    return cv.img


def _maquines(gen=None, pump=None):
    """El motor, el quadre, el generador, el separador i la bomba, plans sobre transparent (en surten els retalls)."""
    PL._ST.update(gen=gen, pump=pump, wt=0.0)
    try:
        cv = Canvas(light=TEXL, transparent=True)
        PL.engine(cv)
        PL.panel(cv)
        PL.generator(cv)
        PL.separator(cv)
        PL.bilge_pump(cv)
        _cos_valvula(cv)
        PL.lamps(cv)
        box(cv, 453, PL.MEZZ_Y + 6, 469, PL.MEZZ_Y + 9, CAB, 2.8)   # el llum de sota l'altell
        cv.disc(461, PL.MEZZ_Y + 12, 7, 3, [(120, 90, 40), (200, 160, 80), (250, 220, 150), (255, 246, 220)], 2.6,
                lit=0)
        for gx in (-4, 0, 4):
            cv.vline(461 + gx, PL.MEZZ_Y + 10, PL.MEZZ_Y + 14, CAB, 2.2, lit=0)
        return cv.img
    finally:
        PL._ST.update(gen=None, pump=None, wt=0.0)


VX = PL.VX


def _cos_valvula(cv, tancada=False):
    """El cos de la vàlvula de presa de mar (vermell), la tapa i l'eix pelat; `tancada`: amb el volant improvisat."""
    cv.disc(VX, 237, 17, 8, REDP, lambda nx, ny: 3.4 - nx * 1.2 - ny * 1.4)
    for bx in range(VX - 13, VX + 16, 7):
        bolt(cv, bx, 233, REDP, 4.0)
    box(cv, VX - 7, 213, VX + 7, 231, REDP, 3.6)
    cv.hline(VX - 9, VX + 9, 213, REDP, 4.6)
    for bx in (VX - 7, VX + 7):
        bolt(cv, bx, 215, REDP, 4.2)
    vpipe(cv, VX, 188, 213, 1, CAB, 4.6)
    box(cv, VX - 3, 185, VX + 3, 189, CAB, 5.0)
    cv.put(VX, 187, CAB, 2.0)
    if tancada:
        PL.valvula_tancada(cv)


@functools.lru_cache(maxsize=None)
def _maq():
    return _maquines()


@functools.lru_cache(maxsize=None)
def _valvula(tancada=False):
    cv = Canvas(light=TEXL, transparent=True)
    _cos_valvula(cv, tancada)
    return cv.img.crop(VALVE_BOX)


VALVE_BOX = (VX - 34, 180, VX + 34, 246)
GEN_BOX = (436, 30, 557, PL.MEZZ_Y)
SEP_BOX = (524, 110, 567, HW + 4)
PUMP_BOX = (437, 203, 526, 235)
QUADRE_BOX = (429, 111, 495, HW)
LAMP_BOX = (238, 20, 259, 40)
MLAMP_BOX = (452, PL.MEZZ_Y + 5, 471, PL.MEZZ_Y + 16)


# ─── Les superfícies ────────────────────────────────────────────────────────

def _planxa(s, t, P):
    """La planxa estriada del terra, en coordenades del món: planxes de 100 amb les juntes i l'estriat en diagonal,
    que s'esvaeix cap al fons (si no, fa moiré)."""
    x, z = P[0], P[2]
    if x % 100 < 1.2 or z % 100 < 1.2:
        return 1.0
    if x % 100 < 2.4 or z % 100 < 2.4:
        return 3.2
    v = 2.5 + (hr(int(x // 100), int(z // 100), 4) - 0.5) * 0.4 + (fbm(x / 80, z / 50, 6) - 0.5) * 0.6
    fade = max(0.0, 1 - max(0.0, z - 120) / 170)
    a, b = int((x + z) / 5) % 4, int((x - z) / 5) % 4
    if (a == 0 and b in (0, 1)) or (a == 2 and b in (2, 3)):
        v += 0.9 * fade
    elif (a == 1 and b == 1) or (a == 3 and b == 3):
        v -= 0.3 * fade
    oli = fbm(x / 40, z / 26, 11)
    if oli > 0.62:
        v -= (oli - 0.62) * 6                          # taques d'oli velles
    return v


def _sostre(s, t, P):
    """El sostre: les bigues que fugen (cada 60, cap al fons) i les safates de cables al llarg."""
    x, z = P[0], P[2]
    v = 1.0 + (fbm(x / 60, z / 60, 2) - 0.5) * 0.4
    if z % 60 < 8:
        v = 2.6 if z % 60 < 1.5 else 1.8 - (z % 60) * 0.08
    if 40 < x % 170 < 70:
        v = 2.2 if int(z) % 5 else 1.2                 # una safata de cables
        if 46 < x % 170 < 64 and hr(int(z // 6), int(x // 6), 3) > 0.35:
            v = 0.6
    return v


def _reixa(s, t, P):
    """El pis de reixa de l'altell, vist des de dalt."""
    x, z = P[0], P[2]
    if s < 1.5 or t < 1.5:
        return 4.2
    return 1.0 if (int(x) % 4 < 2) != (int(z) % 4 < 2) else 3.0


def _ratlles(s, t, P):
    return 3.6 if ((s + t) // 5) % 2 == 0 else 1.0


def _dins(x, z, poly):
    """Si el punt (x, z) és dins el polígon convex `poly` de punts (x, z)."""
    sg = 0
    for (ax, az), (bx, bz) in zip(poly, poly[1:] + poly[:1]):
        c = (bx - ax) * (z - az) - (bz - az) * (x - ax)
        if c and sg and (c > 0) != (sg > 0):
            return False
        sg = sg or c
    return True


def _el(cx, cz, rx, rz, k):
    """Una foscor el·líptica (s, t des del cantó), per a les ombres sota els mobles."""
    return lambda s, t: k * max(0.0, 1 - ((s - rx) / rx) ** 2 - ((t - rz) / rz) ** 2) * 1.5


def _foscor_el(e, sid, cx, cz, rx, rz, k, y=0.6):
    e.foscor(sid, (cx - rx, y, cz + rz), (cx + rx, y, cz + rz), (cx + rx, y, cz - rz), (cx - rx, y, cz - rz),
             _el(cx, cz, rx, rz, k))


def escena(cv, tex, estat=frozenset()):
    """Tota la sala, de lluny a prop. `estat`: 'tancada' (el volant improvisat a la vàlvula), 'sentina_oberta'.
    → l'Escena (qui ha pintat què)."""
    e = Escena(cv, CAM, LLUMS, ambient=-0.5)
    paret, llisa, maq = tex['paret'], tex['llisa'], tex['maquines']
    # el sostre, baix i fosc, amb les bigues
    e.quad('sostre', (0, HW, ZN), (XR, HW, ZN), (XR, HW, ZW), (0, HW, ZW), ramp=CAB, lvl=_sostre, dues_cares=True)
    # la paret del passadís (x = 0): de prop, planxa llisa; cap a la cantonada, el dibuix pla (x 0..170)
    e.quad('paret_esq_prop', (0, HW, ZN), (0, HW, ZW - XL), (0, 0, ZW - XL), (0, 0, ZN),
           tex=(llisa, (W - 1 - (ZW - XL - ZN), 0, W - 1, HW)))
    e.quad('paret_esq', (0, HW, ZW - XL), (0, HW, ZW), (0, 0, ZW), (0, 0, ZW - XL), tex=(paret, (0, 0, XL, HW)))
    # la paret del fons (z = 300): el dibuix pla (x 170..640) i, a la dreta, més planxa
    e.quad('paret_fons', (0, HW, ZW), (W - XL, HW, ZW), (W - XL, 0, ZW), (0, 0, ZW), tex=(paret, (XL, 0, W, HW)))
    e.quad('paret_fons_dreta', (W - XL, HW, ZW), (XR, HW, ZW), (XR, 0, ZW), (W - XL, 0, ZW),
           tex=(llisa, (0, 0, XR - (W - XL), HW)))
    # la paret de la dreta (x = XR), llisa, que tanca la sala
    e.quad('paret_dreta', (XR, HW, ZW), (XR, HW, ZN), (XR, 0, ZN), (XR, 0, ZW), tex=(llisa, (60, 0, 60 + ZW - ZN, HW)))
    # el terra
    e.quad('terra', (0, 0, ZW), (XR, 0, ZW), (XR, 0, ZN), (0, 0, ZN), ramp=DECK, lvl=_planxa)
    # la llum de les bombetes al terra, i la del taller que entra en diagonal
    for (lx, lz), k in zip(LAMPS, (0.30, 0.26)):
        e.claror((lx - 150, 0.3, lz + 150), (lx + 150, 0.3, lz + 150), (lx + 150, 0.3, lz - 150),
                 (lx - 150, 0.3, lz - 150), WARM,
                 lambda s, t, k=k: k * max(0.0, 1 - math.hypot(s - 150, (t - 150) * 1.1) / 150) ** 1.5)
    tx0, tx1 = _w(576), _w(621)
    e.claror((tx0, 0.4, ZW), (tx1, 0.4, ZW), (tx1 - 50, 0.4, ZW - 130), (tx0 - 70, 0.4, ZW - 130), (200, 230, 215),
             lambda s, t: 0.30 * max(0.0, 1 - t / 130) * max(0.0, 1 - abs(s - 26) / 34))
    # el vermell de l'emergència, a la paret i al terra davant la porta del passadís
    ez = _wz(45)
    e.claror((0.5, HW, ez + 70), (0.5, HW, ez - 70), (0.5, 0, ez - 70), (0.5, 0, ez + 70), RED_GLOW,
             lambda s, t: 0.22 * max(0.0, 1 - math.hypot(s - 70, t - (HW - 79)) / 70))
    e.claror((0, 0.4, ez + 60), (90, 0.4, ez + 60), (90, 0.4, ez - 60), (0, 0.4, ez - 60), RED_GLOW,
             lambda s, t: 0.16 * max(0.0, 1 - math.hypot(s, t - 60) / 80))
    # la foscor dels racons i de la base de les parets
    e.foscor('racons', (0, 0.5, ZW), (XR, 0.5, ZW), (XR, 0.5, ZN), (0, 0.5, ZN),
             lambda s, t: max(0.6 * max(0.0, 1 - t / 34), 0.55 * max(0.0, 1 - s / 30)))
    e.foscor('cantonada', (0, HW, ZW - 0.5), (90, HW, ZW - 0.5), (90, 0, ZW - 0.5), (0, 0, ZW - 0.5),
             lambda s, t: 0.5 * max(0.0, 1 - s / 90))
    e.foscor('cantonada2', (0.5, HW, ZW - 90), (0.5, HW, ZW), (0.5, 0, ZW), (0.5, 0, ZW - 90),
             lambda s, t: 0.5 * max(0.0, 1 - (90 - s) / 90))
    e.foscor('sostre_fosc', (0, HW - 0.5, ZW - 0.6), (XR, HW - 0.5, ZW - 0.6), (XR, 0, ZW - 0.6), (0, 0, ZW - 0.6),
             lambda s, t: 0.5 * max(0.0, 1 - t / 70))
    e.foscor('cantonada3', (XR - 0.5, HW, ZW), (XR - 0.5, HW, ZW - 120), (XR - 0.5, 0, ZW - 120), (XR - 0.5, 0, ZW),
             lambda s, t: 0.45 * max(0.0, 1 - s / 120))
    e.foscor('racons_dreta', (XR - 40, 0.5, ZW), (XR, 0.5, ZW), (XR, 0.5, ZN), (XR - 40, 0.5, ZN),
             lambda s, t: 0.55 * max(0.0, 1 - (40 - s) / 30))
    e.foscor('sostre_fosc2', (0.6, HW - 0.5, ZN), (0.6, HW - 0.5, ZW), (0.6, 0, ZW), (0.6, 0, ZN),
             lambda s, t: 0.5 * max(0.0, 1 - t / 70))
    # sota l'altell, la paret a l'ombra
    mx0, mx1 = _w(429), _w(571)
    e.foscor('altell_ombra', (mx0, MEZZ_H, ZW - 0.7), (mx1, MEZZ_H, ZW - 0.7), (mx1, MEZZ_H - 40, ZW - 0.7),
             (mx0, MEZZ_H - 40, ZW - 0.7), lambda s, t: 0.6 * max(0.0, 1 - t / 30))

    # ── la porta del passadís: la fulla estanca, oberta cap a la sala ──
    dz0, dz1 = _wz(19), _wz(72)
    lf = 52                                                          # l'ample de la fulla
    ang = 1.15                                                       # oberta uns 65° respecte de la paret
    hx, hz = 0, dz0 - 3                                              # la frontissa
    fx_, fz_ = hx + lf * math.sin(ang), hz - lf * math.cos(ang)
    e.foscor('ombra_fulla', (0.5, 0.6, hz), (fx_ + 10, 0.6, hz), (fx_ + 10, 0.6, fz_ - 10), (0.5, 0.6, fz_ - 10),
             lambda s, t: 0.4 * max(0.0, 1 - s / 70))

    def fulla(s, t, P):
        v = 2.8 - s * 0.01
        if 6 < s < lf - 6 and 6 < t < 110:
            v += 0.4
        if (abs(s - 6) < 1 or abs(s - lf + 6) < 1) and 6 < t < 110:
            v -= 0.8
        if abs(s - lf + 9) < 3 and int(t) % 29 < 5 and 10 < t < 110:
            v += 1.0                                                 # les palanques
        return v
    e.quad('fulla_passadis', (hx + 1, 112, hz), (fx_, 112, fz_), (fx_, 0, fz_), (hx + 1, 0, hz), ramp=ENG,
           lvl=fulla, dues_cares=True)
    e.caixa('fulla_passadis', fx_ - 1.5, fx_ + 1.5, 0, 112, fz_ - 1.5, fz_ + 1.5, ENG, 3.6)

    # ── la porta del taller: la fulla, girada cap a la sala ──
    tz = ZW - 2
    th0 = _w(625)
    e.quad('fulla_taller', (th0 + 40, 112, tz - 30), (th0, 112, tz), (th0, 0, tz), (th0 + 40, 0, tz - 30),
           ramp=ENG, lvl=lambda s, t, P: fulla(lf - s * lf / 50, t, P) - 0.4, dues_cares=True)

    # ── l'altell: el pis de reixa, les mènsules, la barana i el generador ──
    mz0 = ZW - MEZZ_D
    _foscor_el(e, 'ombra_quadre', (_w(432) + _w(491)) / 2, ZW - 14, 46, 26, 0.45)
    for mx in (440, 507, 560):                                       # les mènsules, en escaire
        x = _w(mx)
        e.caixa('altell', x - 2, x + 2, MEZZ_H - 24, MEZZ_H - 5, ZW - MEZZ_D + 6, ZW, CAB, 2.2)
    e.caixa('altell', mx0, mx1, MEZZ_H - 5, MEZZ_H, mz0, ZW, CAB, 2.6,
            cares={'dalt': {'ramp': CAB, 'lvl': _reixa}, 'davant': {'ramp': CAB, 'lvl': lambda s, t, P: 3.8 if t < 1.2 else 2.4},
                   'sota': {'ramp': DARK, 'lvl': 1.2}})
    # el generador, dret damunt l'altell, i l'escapament cap al sostre
    gz = ZW - 24
    e.foscor('ombra_generador', (_w(440), MEZZ_H + 0.4, ZW), (_w(552), MEZZ_H + 0.4, ZW), (_w(552), MEZZ_H + 0.4, gz - 16),
             (_w(440), MEZZ_H + 0.4, gz - 16), lambda s, t: 0.5)
    e.sprite('generador', maq.crop(GEN_BOX), (496 - GEN_BOX[0], GEN_BOX[3] - GEN_BOX[1]), (_w(496), MEZZ_H, gz))
    e.tub('generador', (_w(469), MEZZ_H + 54, gz - 2), (_w(469), HW, gz - 2), 3.2, LAG, 2.8, brides=26)
    # la barana groga, al cantó de l'altell
    for k in range(6):
        x = mx0 + 3 + k * (mx1 - mx0 - 6) / 5
        e.caixa('barana', x - 1, x + 1, MEZZ_H, MEZZ_H + 26, mz0 + 1, mz0 + 3, YELL, 3.0)
    for hgt, lv in ((26, 3.6), (14, 3.0)):
        e.caixa('barana', mx0 + 2, mx1 - 2, MEZZ_H + hgt - 1.5, MEZZ_H + hgt, mz0 + 1, mz0 + 3, YELL, lv)
    e.caixa('barana', mx0 + 2, mx1 - 2, MEZZ_H, MEZZ_H + 4, mz0 + 1, mz0 + 2, YELL, 2.4)
    for hgt in (26, 14):                                             # la barana també tanca el costat de l'esquerra
        e.caixa('barana', mx0 + 2, mx0 + 4, MEZZ_H + hgt - 1.5, MEZZ_H + hgt, mz0 + 1, ZW, YELL, 3.0)
    e.caixa('barana', mx0 + 2, mx0 + 4, MEZZ_H, MEZZ_H + 26, ZW - 22, ZW - 20, YELL, 3.0)

    # ── el quadre: un armari amb volum, separat de la paret ──
    qx0, qx1 = _w(QUADRE_BOX[0]), _w(QUADRE_BOX[2])
    e.caixa('quadre', qx0, qx1, 0, _y(QUADRE_BOX[1]), ZW - 26, ZW, CAB, 2.4,
            cares={'davant': {'tex': (maq, QUADRE_BOX)}, 'dalt': {'ramp': CAB, 'lvl': 3.6},
                   'dreta': {'ramp': CAB, 'lvl': 1.8}, 'esquerra': {'ramp': CAB, 'lvl': 2.0}})
    # el llum de sota l'altell
    e.sprite('llum_altell', maq.crop(MLAMP_BOX), ((MLAMP_BOX[2] - MLAMP_BOX[0]) / 2, 0),
             (_w(461), MEZZ_H - 5, ZW - 22))
    # el separador, dret i separat de la paret
    sx = _w(545)
    _foscor_el(e, 'ombra_separador', sx + 6, ZW - 16, 30, 20, 0.5)
    e.sprite('separador', maq.crop(SEP_BOX), (545 - SEP_BOX[0], HW - SEP_BOX[1]), (sx, 0, ZW - 20))

    # ── el motor, separat de la paret ──
    ez0, ez1 = EZ
    _foscor_el(e, 'ombra_motor', (_ex(171) + _ex(352)) / 2 - 8, (ez0 + ez1) / 2 - 6, 116, 52, 0.55)
    # la xemeneia, que puja al sostre
    xz = ez1 - 12
    e.tub('motor', (_ex(344), _ey(93), xz), (_ex(344), HW, xz), 8 * EK, LAG, 3.0, brides=20)
    # la bancada, el càrter, el bloc i les culates (el davant, el dibuix pla)
    def part(x0f, x1f, y0f, y1f, z0, z1, lvl_dalt=3.2, dalt=None):
        e.caixa('motor', _ex(x0f), _ex(x1f), _ey(y1f), _ey(y0f), z0, z1, ENG_LIGHT, 2.4,
                cares={'davant': {'tex': (maq, (x0f, y0f, x1f, y1f))},
                       'dalt': dalt or {'ramp': ENG_LIGHT, 'lvl': lvl_dalt},
                       'dreta': {'ramp': ENG_LIGHT, 'lvl': lambda s, t, P: 1.8 - (0.6 if int(s) % 30 < 2 else 0)},
                       'esquerra': {'ramp': ENG_LIGHT, 'lvl': 2.2}})
    part(171, 353, 187, HW, ez0 - 6, ez1 + 6, 2.6,
         dalt={'ramp': ENG, 'lvl': lambda s, t, P: 2.6 + (1.2 if int(s) % 16 < 2 and int(t) % 12 < 2 else 0)})
    part(181, 342, 133, 187, ez0, ez1)
    part(187, 337, 112, 133, ez0 + 6, ez1 - 6, 3.4)

    def culata(s, t, P):
        return 3.8 + (1.0 if (abs(s - 4) < 1.2 or abs(s - 22) < 1.2) and int(t) % 9 < 2 else 0)
    for i in range(4):
        dx = 191 + i * 36
        part(dx, dx + 32, 96, 112, ez0 + 9, ez1 - 22, dalt={'ramp': ENG_LIGHT, 'lvl': culata})
    # el col·lector d'escapament folrat (on seu en Diu), al darrere de les culates
    e.tub('motor', (_ex(195), _ey(88), xz), (_ex(341), _ey(88), xz), 6.5 * EK, LAG, 3.2, brides=30)
    # el turbo, a la punta
    e.tub('motor', (_ex(337), _ey(120), (ez0 + ez1) / 2 - 10), (_ex(366), _ey(120), (ez0 + ez1) / 2 - 10), 12 * EK,
          ENG_LIGHT, 3.2)
    # la protecció del volant, ratllada groc i negre, amb tres cares
    e.caixa('motor', _ex(163), _ex(181), _ey(195), _ey(133), ez0 + 8, ez1 - 8, YELL, 2.4,
            cares={'davant': {'tex': (maq, (163, 133, 181, 195))}, 'dalt': {'ramp': ENG, 'lvl': 2.6},
                   'esquerra': {'ramp': YELL, 'lvl': _ratlles}})

    # ── a terra: el forat de la vàlvula, la planxa recolzada, la sentina ──
    vx, vz = VALVE
    hx0, hx1, hz0, hz1 = vx - 34, vx + 34, vz - 16, vz + 16
    e.quad('forat', (hx0, 0.2, hz1), (hx1, 0.2, hz1), (hx1, 0.2, hz0), (hx0, 0.2, hz0), ramp=DARK,
           lvl=lambda s, t, P: (0.6 + (1.2 if int(s) % 9 < 2 else 0) * min(1.0, t / 10)
                                + (2.4 if t > 24 and hr(int(s // 3), 1) > 0.5 and int(t) % 6 == 0 else 0)))
    e.foscor('forat', (hx0, 0.3, hz1), (hx1, 0.3, hz1), (hx1, 0.3, hz0), (hx0, 0.3, hz0),
             lambda s, t: 0.5 * max(0.0, 1 - t / 20))
    for (ax, az), (bx, bz) in (((hx0, hz1), (hx1, hz1)), ((hx0, hz0), (hx1, hz0)), ((hx0, hz0), (hx0, hz1)),
                               ((hx1, hz0), (hx1, hz1))):
        e.caixa('forat', min(ax, bx) - 1, max(ax, bx) + 1, 0, 0.8, min(az, bz) - 1, max(az, bz) + 1, DECK, 4.0)
    # la planxa, aixecada i recolzada de cantó contra la bancada
    px0 = hx0 - 62
    e.quad('planxa', (px0, 52, ez0 - 8), (px0 + 34, 52, ez0 - 9), (px0 + 36, 0, ez0 - 26), (px0 + 2, 0, ez0 - 25),
           ramp=DECK, lvl=lambda s, t, P: 5.0 - t * 0.012 + (1.2 if (int(s) + int(t) // 4 * 2) % 4 == 0 and int(t) % 4 == 0 else 0)
           - (1.8 if s < 1 or s > 33 else 0), dues_cares=True)
    _foscor_el(e, 'ombra_planxa', px0 + 22, ez0 - 20, 22, 10, 0.4)
    # el cos de la vàlvula, dins el forat (dret)
    e.sprite('valvula', tex['valvula'], (VX - VALVE_BOX[0], 245 - VALVE_BOX[1]), (vx, -6, vz))
    # el registre de la sentina (vist des de dalt)
    sx0, sx1, sz0, sz1 = SENT
    if 'sentina_oberta' in estat:
        def oli(s, t, P):
            return 1.6 + math.sin(s * 0.5 + t * 0.9) * 0.8 + (2.0 if (int(s * 3) + int(t * 5)) % 23 == 0 else 0)
        e.quad('sentina', (sx0, 0.3, sz1), (sx1, 0.3, sz1), (sx1, 0.3, sz0), (sx0, 0.3, sz0), ramp=DARK, lvl=oli)
        e.foscor('sentina', (sx0, 0.4, sz1), (sx1, 0.4, sz1), (sx1, 0.4, sz0), (sx0, 0.4, sz0),
                 lambda s, t: 0.5 * max(0.0, 1 - t / 14))
        e.claror((sx0, 0.4, sz1), (sx1, 0.4, sz1), (sx1, 0.4, sz0), (sx0, 0.4, sz0), (90, 60, 120),
                 lambda s, t: 0.35 if (int(s * 3) + int(t * 5)) % 11 == 0 else 0)
        # la tapa, aixecada i recolzada a terra, al costat
        e.quad('sentina_tapa', (sx1 + 2, 36, sz1 - 4), (sx1 + 2, 36, sz0 + 4), (sx1 + 22, 0, sz0 + 2),
               (sx1 + 22, 0, sz1 - 2), ramp=DECK, lvl=lambda s, t, P: 3.4 + (1.2 if int(s) % 6 == 0 and t < 3 else 0),
               dues_cares=True)
    else:
        e.quad('sentina', (sx0, 0.3, sz1), (sx1, 0.3, sz1), (sx1, 0.3, sz0), (sx0, 0.3, sz0),
               tex=(tex['sentina'], SENT_TEX))
    # ── la bomba de sentina, una mica girada: la bancada en 3D, la bomba (el dibuix pla) dreta damunt ──
    bx, bz, ba = PUMP
    _foscor_el(e, 'ombra_bomba', bx + 4, bz + 4, 50, 20, 0.55)
    e.foscor('ombra_bomba', (bx - 70, 0.6, bz + 10), (bx + 30, 0.6, bz + 10), (bx + 10, 0.6, bz - 40),
             (bx - 90, 0.6, bz - 40), lambda s, t: 0.35 * max(0.0, 1 - abs(t - 22) / 26) * max(0.0, 1 - abs(s - 55) / 50))
    e.caixa_girada('bomba', bx, bz, 76, 24, 8, ba, CAB, 2.6,
                   cares={'dalt': {'ramp': ENG, 'lvl': lambda s, t, P: 3.2 + (1.2 if (abs(s - 5) < 1.2 or abs(s - 71) < 1.2) and abs(t - 12) < 1.2 else 0)},
                          'davant': {'ramp': CAB, 'lvl': 2.2}, 'dreta': {'ramp': CAB, 'lvl': 1.6}})
    e.sprite('bomba', tex['bomba'], ((PUMP_BOX[2] - PUMP_BOX[0]) / 2 - 2, PUMP_BOX[3] - PUMP_BOX[1]), (bx, 8, bz))
    # la canonada de la bomba, cap a la vàlvula de tres vies de la paret
    c, s_ = math.cos(ba), math.sin(ba)
    ox, oz = bx + 30 * c, bz + 30 * s_
    e.tub('bomba', (ox, 20, oz), (ox, 20, ZW - 30), 3.2, CAB, 2.8)
    e.tub('bomba', (ox, 20, ZW - 30), (_w(517), 20, ZW - 4), 3.2, CAB, 2.8)

    # ── primer pla ──
    _primer_pla(e)
    return e


SENT_TEX = (0, 0, 60, 34)


def _sentina_tex():
    """El registre de la sentina, vist des de dalt (una textura de 60×34 per al terra)."""
    cv = Canvas(light=TEXL)
    x0, y0, x1, y1 = 0, 0, 59, 33
    cv.rect(x0, y0, x1, y1, DECK, 2.0)
    cv.rect(x0 + 3, y0 + 3, x1 - 3, y1 - 3, DECK, 3.4)
    cv.hline(x0, x1, y0, DECK, 4.2)
    cv.vline(x0, y0, y1, DECK, 3.8)
    cv.hline(x0, x1, y1, DECK, 1.0)
    cv.vline(x1, y0, y1, DECK, 1.2)
    for i in range(9):
        t = i / 8
        bolt(cv, round(x0 + 4 + (x1 - x0 - 9) * t), y0 + 2, DECK, 4.2)
        bolt(cv, round(x0 + 4 + (x1 - x0 - 9) * t), y1 - 3, DECK, 4.2)
    for y in (y0 + 10, y0 + 20):
        bolt(cv, x0 + 2, y, DECK, 4.2)
        bolt(cv, x1 - 3, y, DECK, 4.2)
    for hx in (x0 + 8, x1 - 14):                                       # nanses encastades
        cv.rect(hx, y0 + 6, hx + 6, y0 + 8, DARK, 0.8)
        cv.hline(hx, hx + 6, y0 + 9, DECK, 4.6)
    s = 'SENTINA'
    for dx in (0, 1):                                                   # l'estergit, gros (es veu en escorç)
        text(cv, s, (x0 + x1) // 2 - text_width(s) // 2 + dx, y0 + 17, YELL, 2.6)
    return cv.img


def _primer_pla(e):
    """L'escala de l'escotilla (a l'esquerra, de prop), les canonades i la safata de dalt, i dos bidons."""
    x0, x1, zb, zt = LADDER
    # els graons, de dalt a baix (els de dalt són més a prop)
    n = 13
    for i in range(n, 0, -1):
        t = i / (n + 1)
        y = HW * t
        z = zb + (zt - zb) * t
        e.caixa('escala', x0 + 3, x1 - 3, y - 2.5, y, z - 4, z + 4, STEELG, 3.6,
                cares={'dalt': {'ramp': STEELG, 'lvl': lambda s, t_, P: 4.4 if (int(s) + int(t_)) % 3 == 0 else 3.2},
                       'davant': {'ramp': YELL, 'lvl': 3.0}})
    for x in (x0 + 1.5, x1 - 1.5):
        e.tub('escala', (x, 0, zb), (x, HW, zt), 2.6, STEELG, 3.4)
    # el passamà groc, de banda
    e.tub('escala', (x1 + 6, 36, zb - 6), (x1 + 6, HW, zt - 10), 1.6, YELL, 3.2)
    # l'escotilla del sostre, oberta: un forat fosc amb el marc
    e.quad('escala', (x0 - 4, HW - 0.5, zt + 18), (x1 + 6, HW - 0.5, zt + 18), (x1 + 6, HW - 0.5, zt - 40),
           (x0 - 4, HW - 0.5, zt - 40), ramp=DARK, lvl=0.8, dues_cares=True)
    # una canonada grossa que travessa per dalt, de prop, i la safata de cables
    e.tub('primer_pla', (-40, HW - 14, 40), (XR, HW - 14, 40), 8, FOSC, 2.0, brides=90)
    e.caixa('primer_pla', -40, XR, HW - 6, HW - 2, -10, 10, FOSC, 1.6,
            cares={'sota': {'ramp': FOSC, 'lvl': lambda s, t, P: 2.6 if int(s) % 7 < 1 else 1.0}})
    for k, (xx, zz) in enumerate(((60, 0), (500, 6))):              # cables que pengen de la safata
        e.cable('primer_pla', [(xx, HW - 4, zz), (xx + 8, HW - 30 - k * 8, zz + 4), (xx + 3, HW - 44 - k * 12, zz + 8)],
                FOSC, 1.6, gruix=2.2)
    # una canonada vertical a la dreta, de prop
    e.tub('primer_pla', (XR - 14, 0, 30), (XR - 14, HW, 30), 10, FOSC, 1.8, brides=70)
    # els bidons d'oli, a baix a la dreta, i unes caixes a baix a l'esquerra
    BID = [(5, 7, 5), (10, 14, 10), (17, 23, 15), (26, 34, 22), (38, 48, 30), (52, 64, 40)]
    for k, (bx, bz) in enumerate(DRUMS):
        _cilindre(e, 'primer_pla', bx, bz, 19, 58, BID, 2.0, cercles=(8, 29, 50))
    for cx, cz, w, d, h, a, y0 in ((86, 22, 64, 44, 40, 0.35, 0), (80, 26, 44, 32, 26, 0.2, 40)):
        e.caixa_girada('primer_pla', cx, cz, w, d, h, a, FOSC, 1.6, y0=y0,
                       cares={'dalt': {'ramp': FOSC, 'lvl': lambda s, t, P: 2.8 - (1.2 if abs(s - w / 2) < 2 else 0)},
                              'davant': {'ramp': FOSC, 'lvl': 1.2}, 'dreta': {'ramp': FOSC, 'lvl': 2.0}})


def _cilindre(e, sid, cx, cz, r, h, ramp, lvl, y0=0.0, n=16, cercles=()):
    """Un cilindre dret (un bidó): les cares del costat (cada una amb la seva llum) i la tapa rodona."""
    for i in range(n):
        a0, a1 = 2 * math.pi * i / n, 2 * math.pi * (i + 1) / n
        A = (cx + r * math.cos(a0), cz + r * math.sin(a0))
        B = (cx + r * math.cos(a1), cz + r * math.sin(a1))
        e.quad(sid, (A[0], y0 + h, A[1]), (B[0], y0 + h, B[1]), (B[0], y0, B[1]), (A[0], y0, A[1]), ramp=ramp,
               lvl=lambda s, t, P: lvl + (1.0 if any(abs(h - t - c) < 1.5 for c in cercles) else 0)
               + (0.6 if s < 1 else 0))
    e.quad(sid, (cx - r, y0 + h, cz + r), (cx + r, y0 + h, cz + r), (cx + r, y0 + h, cz - r), (cx - r, y0 + h, cz - r),
           ramp=ramp, lvl=lambda s, t, P: lvl + 0.6 + (1.0 if r - 4 < math.hypot(s - r, t - r) < r - 2 else 0)
           + (1.4 if math.hypot(s - r * 1.4, t - r * 0.6) < 2.5 else 0),
           forma=lambda s, t: math.hypot(s - r, t - r) < r)


# ─── Composició ─────────────────────────────────────────────────────────────

def _glows(cv):
    """El resplendor de les bombetes i dels llums d'emergència (en pantalla, damunt l'escena)."""
    for lx, lz in LAMPS:
        u, v, _ = CAM.projecta((lx, HW - 26, lz))
        k = CAM.escala((lx, HW - 26, lz))
        cv.glow(u, v, 50 * k, WARM, 0.5)
        cv.glow(u, v, 16 * k, (255, 240, 200), 0.6)
    u, v, _ = CAM.projecta((_w(461), MEZZ_H - 10, ZW - 22))
    cv.glow(u, v, 28, WARM, 0.45)
    u, v, _ = CAM.projecta((1, _y(79), _wz(45)))
    cv.glow(u, v, 30, RED_GLOW, 0.5)
    for lx, ly in ((599, 60), (396, 64)):                       # el taller i el rebost
        u, v, _ = CAM.projecta((_w(lx), _y(ly), ZW - 1))
        cv.glow(u, v, 20, RED_GLOW, 0.4)


@functools.lru_cache(maxsize=None)
def _textures():
    return {'paret': _paret(), 'llisa': _llisa(), 'maquines': _maq(), 'valvula': _valvula(),
            'sentina': _sentina_tex(), 'bomba': _maq().crop(PUMP_BOX)}


def _render(estat=frozenset(), tex=None):
    cv = Canvas(light=LIGHT)
    e = escena(cv, tex or _textures(), estat)
    _penjolls(e)
    _glows(cv)
    cv.rect(0, BOTTOM + 1, W - 1, H - 1, [(0, 0, 0)], 0, lit=0)    # la barra de verbs: negre
    return cv.img, e


def _penjolls(e):
    """Les bombetes del sostre, penjades (després del primer pla: no les tapa res)."""
    maq = _maq()
    for lx, lz in LAMPS:
        e.cable('bombetes', [(lx, HW, lz), (lx, HW - 14, lz)], CAB, 2.0, gruix=1.4)
        e.sprite('bombetes', maq.crop(LAMP_BOX), ((LAMP_BOX[2] - LAMP_BOX[0]) / 2, 0), (lx, HW - 14, lz))


@functools.lru_cache(maxsize=None)
def _base():
    return _render()


def bg(cv):
    cv.img.paste(_base()[0])
    cv.P = cv.img.load()


# ─── L'aigua ───────────────────────────────────────────────────────────────

AIGUA = {'terra', 'racons', 'forat', 'sentina', 'ombra_motor'}


def _desprojecta(u, v):
    """El punt del terra (y = 0) que es veu al píxel (u, v), o None."""
    c = CAM
    x1, y2, z2 = (u + 0.5 - c.centre[0]) / c.f, -(v + 0.5 - c.centre[1]) / c.f, 1.0
    dy = y2 * c._cp - z2 * c._sp
    z1 = y2 * c._sp + z2 * c._cp
    dx = x1 * c._cy + z1 * c._sy
    dz = -x1 * c._sy + z1 * c._cy
    if dy >= -1e-6:
        return None
    k = -c.pos[1] / dy
    return (c.pos[0] + dx * k, 0.0, c.pos[2] + dz * k), (dx, dy, dz)


def _aigua(img, e, wt=0.0):
    """Dos dits d'aigua al terra: tint fosc i verdós, el reflex de la sala (el raig reflectit, fins a la paret), les
    ones, i les espurnes de les bombetes."""
    out = img.copy()
    P, src = out.load(), img.load()
    terra = {i for i, sid in enumerate(e.ids) if sid in AIGUA}
    WC = (10, 34, 40)
    lamps = [CAM.projecta((lx, 0, lz)) for lx, lz in LAMPS]
    for Y in range(60, BOTTOM + 1):
        for X in range(W):
            if e.amo[Y * W + X] not in terra:
                continue
            r = _desprojecta(X, Y)
            if r is None:
                continue
            (px, _, pz), (dx, dy, dz) = r
            c = mix(src[X, Y][:3], WC, 0.4)
            # el raig reflectit (dy cap amunt), fins a la paret del fons o la del passadís
            kz = (ZW - pz) / dz if dz > 1e-6 else 1e9
            kx = -px / dx if dx < -1e-6 else 1e9
            k = min(kz, kx)
            Q = (px + dx * k, -dy * k, pz + dz * k)
            if Q[1] < HW:
                qu, qv, _ = CAM.projecta(Q)
                qu += math.sin(Y * 0.7 + X * 0.03 + wt) * 1.8
                if 0 <= qu < W and 0 <= qv < BOTTOM:
                    f = 0.5 * max(0.0, 1 - (ZW - pz) / 420)
                    c = mix(c, src[int(qu), int(qv)][:3], f)
            # les ones: unes línies clares que corren (més juntes al fons)
            if (math.sin(px * 0.11 + pz * 0.32 + math.sin(pz * 0.05) * 3 - wt) > 0.94 and hr(int(px // 6), int(pz // 3)) > 0.3):
                c = mix(c, (140, 190, 180), 0.3)
            # l'espurna de les bombetes, estirada cap a la càmera
            for (lu, lv, _), (lx, lz) in zip(lamps, LAMPS):
                du = (X - lu) / (4 + (Y - lv) * 0.12 if Y > lv else 4)
                if abs(du) < 2.2 and Y > lv - 40:
                    g = math.exp(-du * du) * max(0.0, 1 - abs(Y - lv) / 90)
                    seg = hr(X // 3, Y, int(lx), round(wt * 4 / math.pi) % 8)
                    if seg < g * 0.6:
                        c = mix(c, WARM, min(0.7, 0.3 + g * 0.4))
            P[X, Y] = c + (255,)
    for X in range(W):                                                # la línia de l'aigua a la paret
        for Y in range(60, BOTTOM):
            o = e.amo[Y * W + X]
            if o in terra and Y > 0 and e.amo[(Y - 1) * W + X] not in terra and hr(X // 5, 5) > 0.5:
                P[X, Y] = mix(P[X, Y][:3], (150, 190, 180), 0.3) + (255,)
                break
    return out


@functools.lru_cache(maxsize=None)
def _mullat():
    img, e = _base()
    return _aigua(img, e)


def aigua(cv):
    """Dos dits d'aigua a terra (Escena 1, fins que la bomba la buida)."""
    cv.img.alpha_composite(_diff(_mullat(), _base()[0]))
    cv.P = cv.img.load()


# ─── Decorats ──────────────────────────────────────────────────────────────

def _decorat(*estat, tex=None):
    """Un decorat: la sala amb aquell estat, menys la de sempre (només el que canvia)."""
    def draw(cv):
        img, _ = _render(frozenset(estat), tex)
        cv.img.alpha_composite(_diff(img, _base()[0]))
        cv.P = cv.img.load()
    return draw


def valvula_tancada(cv):
    """El travesser de la llitera, posat a l'eix de la vàlvula com a volant."""
    _decorat(tex={**_textures(), 'valvula': _valvula(tancada=True)})(cv)


def brida(cv):
    """La brida blanca que lliga l'interruptor de la bomba a la nansa del quadre (nus Bastida)."""
    flat = Canvas(light=TEXL, transparent=True)
    PL.brida(flat)
    _, e = _base()
    cv.img.alpha_composite(e.capa(flat.img, {'quadre'}))
    cv.P = cv.img.load()


def fosc(cv):
    """El generador parat: tot a les fosques, menys els llums d'emergència vermells."""
    lights = [CAM.projecta(P)[:2] for P in ((1, _y(79), _wz(45)), (_w(599), _y(60), ZW - 1),
                                              (_w(396), _y(64), ZW - 1), (_w(461), MEZZ_H - 10, ZW - 22))]
    P = cv.img.load()
    for X, Y, x, y in cv.pixels():
        r = min(math.hypot(x - lx, (y - ly) * 1.1) for lx, ly in lights)
        red = max(0.0, 1 - r / 93) ** 1.6
        a = 0.74 - 0.4 * red                                      # (també tapa els personatges: no tant)
        col = mix((2, 4, 10), (120, 14, 10), 0.5 * red)
        P[X, Y] = col + (int(255 * a),)
    for lx, ly in lights:
        for X, Y, x, y in cv.pixels(lx - 6, ly - 3, lx + 6, ly + 3):
            if ((x - lx) / 6) ** 2 + ((y - ly) / 3) ** 2 <= 1:
                P[X, Y] = (255, 80 + int(60 * hr(X, Y)), 60, 255)


PROPS = {'aigua': aigua, 'valvula_tancada': valvula_tancada, 'brida': brida, 'fosc': fosc,
         'sentina_oberta': _decorat('sentina_oberta')}


# ─── Animacions ─────────────────────────────────────────────────────────────

def _sprite_capa(e, sid, img, peu_img, peu, escala_img=1.0):
    """Un fotograma d'un dibuix pla dret (un sprite de l'escena), on aquell sprite és el que es veu."""
    from pixels import nearest
    idx = e.ids.index(sid)
    k = e.cam.escala(peu) * escala_img
    u, v, _ = e.cam.projecta(peu)
    w, h = max(1, round(img.width * k)), max(1, round(img.height * k))
    im = nearest(img, (w, h)) if k >= 1 else img.resize((w, h), Image.Resampling.BOX)
    ox, oy = round(u - peu_img[0] * k), round(v - peu_img[1] * k)
    out = Image.new('RGBA', (e.cv.w, e.cv.h), (0, 0, 0, 0))
    src, dst, W_ = im.load(), out.load(), e.cv.w
    for y in range(h):
        Y = oy + y
        if not 0 <= Y < e.cv.h:
            continue
        for x in range(w):
            X = ox + x
            if 0 <= X < W_ and e.amo[Y * W_ + X] == idx and src[x, y][3] >= 128:
                dst[X, Y] = src[x, y]
    return out


def _fotograma(capes):
    img, _ = _base()
    img = img.copy()
    for c in capes:
        img.alpha_composite(c)
    return _diff(img, _base()[0])


def _gen_capa(e, maq):
    return _sprite_capa(e, 'generador', maq.crop(GEN_BOX), (496 - GEN_BOX[0], GEN_BOX[3] - GEN_BOX[1]),
                        (_w(496), MEZZ_H, ZW - 24))


def _sep_capa(e, maq):
    return _sprite_capa(e, 'separador', maq.crop(SEP_BOX), (545 - SEP_BOX[0], HW - SEP_BOX[1]), (_w(545), 0, ZW - 20))


def _frames_separador():
    """El pilot verd del separador parpelleja (treballa, a poc a poc)."""
    _, e = _base()
    cv = Canvas(light=TEXL, img=_maq().copy())
    cv.rect(544, 160, 551, 166, CAB, 2.8)
    cv.flat(547, 163, (20, 60, 30))
    cv.flat(548, 163, (20, 60, 30))
    return [_fotograma([]), _fotograma([_sep_capa(e, cv.img)])]


def _frames_generador():
    """El generador en marxa: les culates vibren, el volant gira i les agulles de l'amperímetre i del manòmetre del
    separador tremolen."""
    _, e = _base()
    out = []
    for i in range(8):
        maq = _maquines(gen=i)
        out.append(_fotograma([_gen_capa(e, maq), _sep_capa(e, maq), e.capa(maq, {'quadre'})]))
    return out


def _frames_bomba():
    """La bomba de sentina en marxa: el motor brunzeix i l'eix gira."""
    _, e = _base()
    bx, bz, _ = PUMP
    out = []
    for i in range(6):
        img = _maquines(pump=i).crop(PUMP_BOX)
        out.append(_fotograma([_sprite_capa(e, 'bomba', img, ((PUMP_BOX[2] - PUMP_BOX[0]) / 2 - 2,
                                                              PUMP_BOX[3] - PUMP_BOX[1]), (bx, 8, bz))]))
    return out


def _frames_aigua():
    """El decorat `aigua`, amb les ones: el reflex es gronxa i les espurnes de les bombetes corren."""
    img, e = _base()
    return [_diff(_aigua(img, e, wt=i * 2 * math.pi / 8), img) for i in range(8)]


ANIMS = {'separador': {'frames': _frames_separador, 'frameDuration': 700},
         'generador_marxa': {'frames': _frames_generador, 'frameDuration': 90},
         'bomba_marxa': {'frames': _frames_bomba, 'frameDuration': 100},
         'aigua': {'frames': _frames_aigua, 'frameDuration': 200}}


# ─── Capes del davant i geometria (coordenades de sala, projectades) ─────────

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
    """L'escala d'un personatge amb els peus a la y de pantalla `v` (al terra, la profunditat només depèn de v)."""
    lo, hi = -200.0, 2000.0
    for _ in range(60):
        z = (lo + hi) / 2
        if CAM.projecta((260, 0, z))[1] > v:
            lo = z
        else:
            hi = z
    return CAM.escala((260, 0, (lo + hi) / 2))


FRONT = [
    # (el fosc, per sobre de tot: si no, les capes del davant quedarien il·luminades amb el generador parat)
    {'id': 'davant', 'mask': _amo({'primer_pla'}), 'baseline': 999, 'zIndex': 20, 'props': ('fosc',)},
    {'id': 'davant_escala', 'mask': _amo({'escala'}), 'baseline': _p(LADDER[0], LADDER[2])[1], 'zIndex': 20},
    {'id': 'davant_motor', 'mask': _amo({'motor', 'planxa'}), 'baseline': _p(_ex(260), EZ[0] - 6)[1], 'zIndex': 20},
    # (el volant improvisat i la bomba en marxa, per sobre de la seva capa: si no, la capa els taparia)
    {'id': 'davant_valvula', 'mask': _amo({'valvula'}), 'baseline': _p(VALVE[0], VALVE[1] - 10)[1], 'zIndex': 20,
     'props': ('valvula_tancada',)},
    {'id': 'davant_bomba', 'mask': _amo({'bomba'}), 'baseline': _p(PUMP[0], PUMP[1] - 12)[1], 'zIndex': 20,
     'props': ('bomba_marxa',)},
]


# El terra on es camina (al món, x, z): de la porta del passadís (a l'esquerra, darrere l'escala) fins al taller,
# pel davant del motor i pel costat fins al rebost.
def _z_a_v(x, v):
    """La z del terra que cau a la y de pantalla `v`, a la x del món `x`."""
    lo, hi = -200.0, 2000.0
    for _ in range(50):
        z = (lo + hi) / 2
        if CAM.projecta((x, 0, z))[1] > v:
            lo = z
        else:
            hi = z
    return (lo + hi) / 2


V_PROP = 252                                       # (a baix, escala ≈1,2: el terra de més a prop és primer pla)
WALK_MON = ([(46, 122), (10, 130), (10, 212), (44, 216), (46, 184), (_ex(353) + 6, 184), (_ex(366) + 8, 200),
             (_ex(366) + 8, 270), (_w(373) - 2, 280), (_w(373) - 2, ZW - 8), (_w(424), ZW - 8), (_w(429) - 2, 266),
             (_w(495) + 2, 266), (_w(500), 254), (_w(570), 254), (_w(576) - 2, ZW - 10), (_w(621) + 2, ZW - 10),
             (_w(625), 262), (XR - 18, 248)]
            + [(x, _z_a_v(x, V_PROP)) for x in (XR - 18, 450, 380, 300, 220, 150, 100)] + [(52, _z_a_v(52, V_PROP))])
_WALK = [_p(x, z) for x, z in WALK_MON]
_V_FONS, _V_PROP = min(v for _, v in _WALK), max(v for _, v in _WALK)


def _forat(x0, x1, z0, z1):
    return [_p(x0, z1), _p(x1, z1), _p(x1, z0), _p(x0, z0)]


def _forat_girat(cx, cz, w, d, a):
    c, s = math.cos(a), math.sin(a)
    pts = [(cx + lx * c - lz * s, cz + lx * s + lz * c) for lx, lz in ((-w / 2, d / 2), (w / 2, d / 2), (w / 2, -d / 2),
                                                                     (-w / 2, -d / 2))]
    return [_p(x, z) for x, z in pts]


_VX, _VZ = VALVE
DIU = (_ex(268), _ey(88) + 5, EZ[1] - 12)          # en Diu, assegut al col·lector folrat
DIU_ = (DIU[0], DIU[2], DIU[1])
def _sense_solapar(things):
    """Els rectangles que se solapen amb un de més amunt (el motor) es retallen: al joc, el de zIndex més alt
    guanya, i la vàlvula (davant del motor) i la porta del rebost (al costat) s'han de poder clicar."""
    m = list(things['motor']['rect'])
    m[3] = min(m[3], things['valvula']['rect'][1] - 1)
    m[2] = min(m[2], things['porta_rebost']['rect'][0] - 1)
    things['motor']['rect'] = tuple(m)
    s_ = list(things['sensor']['rect'])
    s_[0] = max(s_[0], things['quadre']['rect'][2] + 1)
    things['sensor']['rect'] = tuple(s_)
    v = list(things['vies']['rect'])
    v[2] = min(v[2], things['separador']['rect'][0] - 1)
    things['vies']['rect'] = tuple(v)
    return things


GEOMETRIA = {
    'things': _sense_solapar({
        'porta_passadis': {'rect': _rect_mon((0, _y(84), _wz(19) - 4), (0, 0, _wz(72) + 2)), 'walk': _p(26, _wz(46))},
        'boca': {'rect': _rect_mon((0, _y(134), _wz(BOCA - 10)), (0, _y(188), _wz(BOCA + 24))), 'walk': _p(30, _wz(BOCA) - 6)},
        'motor': {'rect': _caixa_mon(_ex(163), _ex(366), 0, _ey(93), EZ[0], EZ[1]), 'walk': _p(_ex(262), EZ[0] - 24)},
        'porta_rebost': {'rect': _rect_mon((_w(373), _y(72), ZW), (_w(419), 0, ZW)), 'walk': _p(_w(396), ZW - 20)},
        'generador': {'rect': _rect_mon((_w(437), _y(37), ZW - 24), (_w(555), MEZZ_H, ZW - 24)),
                      'walk': _p(_w(490), ZW - 46)},
        'quadre': {'rect': _caixa_mon(_w(429), _w(495), 0, _y(111), ZW - 26, ZW), 'walk': _p(_w(461), ZW - 44)},
        'sensor': {'rect': _rect_mon((_w(493), _y(109), ZW), (_w(515), _y(200), ZW)), 'walk': _p(_w(504), ZW - 44)},
        'vies': {'rect': _rect_mon((_w(509), _y(176), ZW), (_w(528), _y(200), ZW)), 'walk': _p(_w(520), ZW - 44)},
        'separador': {'rect': _rect_mon((_w(526), _y(112), ZW - 20), (_w(567), 0, ZW - 20)), 'walk': _p(_w(548), ZW - 44)},
        'porta_taller': {'rect': _rect_mon((_w(571), _y(67), ZW), (_w(639), 0, ZW)), 'walk': _p(_w(599), ZW - 18)},
        'valvula': {'rect': _caixa_mon(_VX - 34, _VX + 34, 0, 62, _VZ - 16, _VZ + 16), 'walk': _p(_VX + 50, _VZ - 6)},
        'sentina': {'rect': _rect_mon((SENT[0], 0, SENT[2] - 6), (SENT[1], 8, SENT[3])), 'walk': _p(SENT[1] + 14, SENT[2] + 6)},
    }),
    'spawns': {'iri': _p(230, 140), 'vet': _p(360, 170), 'bastida': _p(54, LADDER[2] + 8),   # dret al peu de l'escala
               'diu': _p(*DIU_)},
    'walkable': _WALK,
    'forats': [_forat(_VX - 36, _VX + 36, _VZ - 18, _VZ + 18), _forat_girat(PUMP[0], PUMP[1], 82, 30, PUMP[2])],
    'floorSquash': 0.42,
    # L'ombra de contacte: la llum dominant és la bombeta de davant el motor (el punt del terra just a sota).
    'characterShadow': {'enabled': True, 'color': '#04080a', 'alpha': 0.45, 'squash': 0.42, 'core': 0.6,
                        'light': {'x': _p(*LAMPS[0])[0], 'y': _p(*LAMPS[0])[1], 'stretch': 0.7, 'reach': 150}},
    'regions': [{'id': 'perspectiva', 'active': True, 'scaleEnabled': True, 'scaleWalkSpeed': True,
                 'scaleTop': round(_escala_a(_V_FONS - 2), 3), 'scaleBottom': round(_escala_a(_V_PROP + 2), 3),
                 'points': [(0, _V_FONS - 2), (W - 1, _V_FONS - 2), (W - 1, _V_PROP + 2), (0, _V_PROP + 2)]},
                # en Diu, damunt del col·lector del motor (fora del terra): la seva escala, fixa
                {'id': 'diu', 'active': True, 'scaleEnabled': True,
                 'scaleTop': round(CAM.escala(DIU), 3), 'scaleBottom': round(CAM.escala(DIU), 3),
                 'points': [(_p(*DIU_)[0] - 60, _p(*DIU_)[1] - 20), (_p(*DIU_)[0] + 60, _p(*DIU_)[1] - 20),
                            (_p(*DIU_)[0] + 60, _p(*DIU_)[1] + 8), (_p(*DIU_)[0] - 60, _p(*DIU_)[1] + 8)]}],
    # la llum de la sala sobre els personatges, en temps d'execució
    'characterLights': {
        'ambient': '#8a9a98',
        'lights': [
            {'x': _p(*LAMPS[0], 150)[0], 'y': _p(*LAMPS[0], 150)[1], 'radius': 230, 'color': '#ffd68c',
             'intensity': 0.9},
            {'x': _p(*LAMPS[1], 150)[0], 'y': _p(*LAMPS[1], 150)[1], 'radius': 200, 'color': '#ffd68c',
             'intensity': 0.8},
            {'x': _p(2, _wz(45), _y(79))[0], 'y': _p(2, _wz(45), _y(79))[1], 'radius': 110, 'color': '#ff3c28',
             'intensity': 0.7},
        ],
    },
}
