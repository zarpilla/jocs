"""
El bar La Propina (Escena 2), dilluns de nit. EN 3D (hd640/tres_d.py), a 1×.

Una càmera alta, a l'esquerra, que mira de biaix la cantonada del fons a la dreta:
  - a la paret del fons, el **rètol** del lema d'en Tomàs («AVUI NO ES FIA, DEMÀ SÍ»), les **lleixes** amb les
    ampolles i el mirall, la **porta del rebost** (a l'esquerra, al final d'un passadís entre la barra i la paret),
    la foto signada i la bufanda; la **tele** en un suport, amb volum, i el **pernil** penjat;
  - a la paret de la dreta (la façana), en escorç: l'**aparador** amb el neó «LA PROPINA» del revés (en entra la
    llum magenta en diagonal pel terra), el **telèfon** de paret i la **porta del carrer**, amb els fars dels
    camions;
  - la **barra** separada de la paret, amb tres cares (el frontal de plafons, la tapa de fòrmica i el cap de
    l'esquerra), la barana de llautó, el taulell del darrere amb la cafetera, la cervesera i la caixa;
  - els **tamborets** de skai davant la barra i l'**escurabutxaques** una mica girat, al costat del rebost;
  - primer pla: una taula i dues cadires en silueta a baix, i el pilar de la dreta.
Qui és darrere la barra (en Tomàs) hi queda tapat de cintura en avall (FRONT, la barra a trossos: cada tros amb la
seva línia base, perquè la barra fuig).

Tot el detall ve del dibuix pla de sempre (bar_sala_pla_comu.py), projectat; els decorats (el clauer, el
comandament, la tele de la comissària, el rebost tancat) són l'escena amb un estat, menys la de sempre. Damunt de
tot, la llum de Suma Zero (hd640/llum.py). El bar del final (final_bar.py) en reaprofita l'escena, de dia.

El món: x a la dreta (600 = la façana), y amunt (0 = el terra), z cap al fons (330 = la paret del fons);
1 unitat = 1 píxel de sala a la distància on un personatge fa ≈111 px (escala 1).
"""
import functools
import math

import hd640  # noqa: F401  (abans de cap hd.rooms: posa la llibreria a 640×360)
from hd640 import llum
from hd.pix import Canvas, Light, W, H, hr
from hd.rooms.comu import _diff, text, PLASTIC, SKY, CITY, SHEET, CARD
from hd.rooms.exterior import fbm
from hd640.rooms import bar_sala_pla_comu as PL
from hd640.rooms.bar_sala_pla_comu import WALLY, WOOD, FORMICA, STEELB, BRASS, TERRAZ, SLATE
from hd640.tres_d import Camera, Escena, Llum

BOTTOM = 259                                       # la sala acaba aquí (a sota, la barra de verbs)
ZW = 330                                           # la paret del fons
XR = 600                                           # la façana (la paret de la dreta)
HW = 200                                           # fins on arriba el dibuix pla de les parets
HT = 250                                           # el sostre
XL = -260                                          # on s'acaba la paret del fons per l'esquerra (fora de pantalla)
TX0 = -40                                          # la x del món on comença la textura de la paret del fons
DXF = 76                                           # el dibuix pla, dins la textura, va 76 px a la dreta
OFF = TX0 + DXF                                    # una x del dibuix pla → la x del món: + 36
BAR = (205, 500, 220, 250, 66)                     # la barra: x0, x1, z del davant, z del darrere, alçada
BACK = (232, 566, 300, 328, 52)                    # el taulell del darrere: x0, x1, z0, z1, alçada
SLOT = (166, 296, 40, 34, 78, 0.38)                # l'escurabutxaques: x, z del centre, ample, fons, alt, gir
STOOLS = (240, 312, 384, 456)                      # els tamborets (x), davant la barra
STOOL_Z = 200
HAM = (588, 304)                                   # el pernil (x, z), penjat del sostre
PILAR = (505, -65)                                 # el pilar del primer pla (x, z)
# la façana: on cau cada cosa del dibuix pla (x del dibuix → z = ZW - x)
F_WIN = 20                                         # l'aparador: x del dibuix 20..103
F_PHONE = 108                                      # el retall del telèfon (el telèfon, a 132..156)
F_DOOR = 226                                       # la porta del carrer: 226..296
DOOR_W = 70


def _w(fx):
    """Una x del dibuix pla de sempre (la paret del fons) → la x del món."""
    return fx + OFF


def _y(fy):
    """Una y del dibuix pla (el terra, a 200) → l'alçada del món."""
    return HW - fy


def _fz(fx):
    """Una x del dibuix de la façana → la z del món."""
    return ZW - fx


TV = (_w(435), _w(539), _y(115), _y(53), ZW - 16, ZW - 4)   # x0, x1, y0, y1, z del davant, z del darrere
SIGN = (_w(PL.SIGN[0]), _w(PL.SIGN[2]), _y(PL.SIGN[3]), _y(PL.SIGN[1]))
REBOST = (_w(PL.DOOR[0]), _w(PL.DOOR[2]), 0, _y(PL.DOOR[1]))
WINZ = (_fz(F_WIN + PL.WIN[2] - PL.WIN[0]), _fz(F_WIN), _y(PL.WIN[3]), _y(PL.WIN[1]))   # z0, z1, y0, y1
PHONE = (_fz(F_PHONE + 48), _fz(F_PHONE + 24), _y(131), _y(93))
DOORZ = (_fz(F_DOOR + DOOR_W), _fz(F_DOOR), 0, _y(64))

CAM = Camera(pos=(150, 230, -330), yaw=0.36, pitch=0.2, f=540, centre=(320, 90))

LIGHT = Light(ambient=0.0, vignette=None, floor_fade=None)  # (la llum és la del món: la de l'Escena)
TEXL = Light(ambient=0.5, vignette=None, floor_fade=None)   # el dibuix pla de les textures, sense vinyeta

FLUO = ((BAR[0] + BAR[1]) / 2, 196, (BAR[2] + BAR[3]) / 2 + 6)          # el fluorescent, damunt la barra
TV_C = ((TV[0] + TV[1]) / 2, (TV[2] + TV[3]) / 2, TV[4] - 10)
SLOT_C = (SLOT[0], 50, SLOT[1] - 30)
WIN_C = (XR - 10, (WINZ[2] + WINZ[3]) / 2, (WINZ[0] + WINZ[1]) / 2)
LLUMS = [Llum(FLUO, 320, 1.7, power=1.3),                         # el fluorescent
         Llum(TV_C, 150, 1.0, power=1.8),                          # la tele
         Llum(SLOT_C, 90, 0.9, power=1.8),                         # l'escurabutxaques
         Llum(WIN_C, 220, 0.9, power=1.6)]                         # el neó de l'aparador


# ─── Les textures: el dibuix pla de sempre ───────────────────────────────────

def _llenc(transparent=False):
    return Canvas(light=TEXL, transparent=transparent)


def _paret_fons(rebost_tancat=False, extra=None):
    """La paret del fons, de cara: el guix, l'arrimador, el rètol, les lleixes, la foto, la bufanda i la porta del
    rebost, tal com eren al pla però 76 px més a la dreta (per fer lloc a la cantonada)."""
    F = _llenc()
    PL.wall(F)
    PL.sign(F)
    PL.shelves(F)
    PL.wall_stuff(F)
    PL.rebost_door(F)
    if rebost_tancat:
        PL.rebost_tancat(F)
    if extra:
        extra(F)
    else:                                          # el suport de la tele, a la paret (la tele és una caixa)
        F.rect(480, 43, 493, 53, STEELB, 2.4)
        F.hline(480, 493, 43, STEELB, 3.6)
    T = _llenc()
    PL.wall(T)
    T.img.paste(F.img.crop((0, 0, W - DXF, PL.FLOOR_Y + 1)), (DXF, 0))
    return T.img


@functools.lru_cache(maxsize=None)
def _paret_buida():
    cv = _llenc()
    PL.wall(cv)
    return cv.img


def _finestra(flick=0, dia=False):
    """L'aparador sol (el retall del dibuix pla), de nit o de dia."""
    cv = _llenc()
    PL.wall(cv)
    if dia:
        from hd640.rooms.final_bar_pla_comu import window_day
        window_day(cv)
    else:
        PL.window(cv, flick)
    x0, y0, x1, y1 = PL.WIN
    return cv.img.crop((x0 - 1, y0 - 1, x1 + 2, y1 + 2))


def porta_carrer(cv, x0, frame=0, dia=False):
    """La porta del carrer, sencera (al pla en sortia la meitat): vidre amb marc d'alumini, i fora, de nit, la
    carretera amb els fars dels camions que passen; de dia, el pàrquing i un arbre."""
    from hd.rooms.final_bar import DAYSKY, ASPH, HILL
    x1, y0, y1 = x0 + DOOR_W, 64, PL.FLOOR_Y
    gy = y0 + 67
    for y in range(y0, y1 + 1):
        for x in range(x0, x1 + 1):
            if dia:
                if y < gy:
                    cv.put(x, y, DAYSKY, 2.4 + (y - y0) / 35, lit=0)
                else:
                    cv.put(x, y, ASPH, 2.0 + (0.6 if (x + y * 3) % 23 == 0 else 0), lit=0)
            elif y < gy:
                cv.put(x, y, SKY, 0.6 + (y - y0) / 53 + (0.6 if hr(x, y, 41) > 0.995 else 0), lit=0)
            else:
                cv.put(x, y, CITY, 1.0 + (0.6 if y == gy else 0), lit=0)
    if dia:
        cv.hline(x0, x1, gy + 10, [(240, 230, 200)], 0, lit=0)                  # la ratlla del pàrquing
        for tx in (x0 + 22, x0 + 52):                                            # dos arbres
            cv.vline(tx, gy - 30, gy, WOOD, 3.0, lit=0)
            cv.vline(tx + 1, gy - 30, gy, WOOD, 2.0, lit=0)
            cv.disc(tx, gy - 42, 12, 15, HILL, lambda nx, ny: 2.6 - ny + (hr(int(nx * 7), int(ny * 7)) - 0.5), lit=0)
    else:
        cv.hline(x0, x1, gy + 4, CITY, 3.0, lit=0)                               # la bionda
        for gx in range(x0 + 2, x1, 7):
            cv.vline(gx, gy + 4, gy + 7, CITY, 2.4, lit=0)
        fx = x0 + 3 + (frame * 5) % 80                                           # un camió que passa
        if fx < x1 - 1:
            cv.hline(fx, min(x1, fx + 5), gy + 12, [(250, 230, 180)], 0, lit=0)
            cv.glow(fx + 2, gy + 12, 10, (250, 220, 160), 0.5)
            if fx - 14 > x0 + 2:
                cv.flat(fx - 14, gy + 9, (230, 120, 40))
                cv.flat(fx - 13, gy + 9, (230, 120, 40))
    for (a, b, c, d) in ((x0, y0, x1, y0 + 3), (x0, y0, x0 + 3, y1), (x1 - 3, y0, x1, y1), (x0, 144, x1, 148)):
        cv.rect(a, b, c, d, STEELB, 3.4 if not dia else 3.8)
    cv.hline(x0, x1, y0, STEELB, 4.6)
    cv.vline(x0 + 3, y0 + 3, y1, STEELB, 1.6)
    cv.rect(x0 + 8, 128, x0 + 21, 133, [(10, 30, 60), (30, 80, 150), (200, 220, 240)], 1.6, lit=0)   # l'adhesiu VISA
    cv.hline(x0 + 9, x0 + 20, 131, [(200, 160, 40)], 0, lit=0)
    cv.rect(x1 - 9, 120, x1 - 7, 168, STEELB, lambda x, y: 5.0 if x == x1 - 9 else 3.4)    # la nansa
    text(cv, 'TIBAR', x0 + 26, 156, STEELB, 0, lit=0, flat=(200, 200, 210) if not dia else (60, 60, 70))
    cv.darken(x0 - 4, y0, x0 - 1, y1, 0.4)


def _facana(flick=0, frame=0, dia=False):
    """La paret de la dreta, de cara (la façana, vista de dins): l'aparador, el telèfon i la porta del carrer."""
    cv = _llenc()
    PL.wall(cv)
    cv.img.paste(_finestra(flick, dia), (F_WIN - 1, PL.WIN[1] - 1))
    ph = _llenc()
    PL.wall(ph)
    PL.phone(ph)
    cv.img.paste(ph.img.crop((552, 90, 604, 172)), (F_PHONE, 90))
    porta_carrer(cv, F_DOOR, frame, dia)
    return cv.img


def _tele(frame=0, bassols=False):
    """La tele (el davant), dibuixada plana: el futbol o la comissària Bassols."""
    cv = _llenc()
    PL.tv(cv, frame)
    if bassols:
        PL.tele_bassols(cv)
    return cv.img


TV_CROP = (435, 53, 540, 116)


def _escurabutxaques(frame=0):
    cv = _llenc(transparent=True)
    PL.slot_machine(cv, frame)
    return cv.img


SLOT_CROP = (91, 125, 132, 204)


def _objectes():
    """Les coses dretes, dibuixades planes sobre transparent: el taulell del darrere (la cafetera, la cervesera, la
    caixa), el que hi ha damunt la barra i el pernil."""
    cv = _llenc(transparent=True)
    PL.back_counter(cv)
    PL.bar(cv)                                     # (en surten el pot, el tovalloner, la tassa i l'ampolla)
    PL.ham(cv)
    return cv.img


GAGGIA = (258, 104, 330, 150)                      # la cafetera, amb les tasses de dalt i el vaporitzador
CERVESERA = (223, 112, 242, 150)
CAIXA = (468, 115, 524, 150)
POT = (298, 123, 318, 152)
TOVALLONER = (407, 132, 425, 151)
CAFE = (182, 143, 202, 154)
AMPOLLA = (538, 130, 550, 151)
PERNIL = (555, 0, 583, 71)


@functools.lru_cache(maxsize=None)
def _textures(rebost_tancat=False, bassols=False):
    return {'fons': _paret_fons(rebost_tancat), 'facana': _facana(), 'buida': _paret_buida(), 'tele': _tele(bassols=bassols),
            'escura': _escurabutxaques(), 'obj': _objectes()}


# ─── Les superfícies ────────────────────────────────────────────────────────

def _guix(lvl0, seed=3):
    """El guix groguenc de dalt de les parets (de l'alçada 200 al sostre), més fosc a dalt (el fum)."""
    def L(s, t, P):
        n = (hr(int(s) // 4, int(t) // 4, seed) - 0.5) * 0.3 + (hr(int(s) // 17, int(t) // 13, 5) - 0.5) * 0.5
        return lvl0 + n - max(0.0, (40 - t) / 40) * 0.6
    return L


def terratzo(s, t, P):
    """El terratzo gris, en coordenades del món: rajoles de 40, juntes, i les pedretes (més menudes al fons)."""
    x, z = P[0], P[2]
    if x % 40 < 0.9 or z % 40 < 0.9:
        return 1.2
    chip = hr(int(x * 1.3), int(z * 1.3), 3)
    v = 2.8 + (hr(int(x // 40), int(z // 40)) - 0.5) * 0.4 + (fbm(x / 90, z / 60, 4) - 0.5) * 0.5
    if chip > 0.94:
        v += 1.3
    elif chip < 0.05:
        v -= 1.1
    elif chip > 0.9:
        v += 0.5
    return v


def _plafons(s, t, P):
    """El frontal de la barra (s al llarg, t des de dalt): plafons de fusta de 53 amb la motllura."""
    x0, x1, zf, zb, h = BAR
    panel = s % 53
    if panel < 2:
        return 1.2
    v = 2.6 + (0.8 if panel < 6 else 0) - (0.6 if panel > 48 else 0) + (hr(int(s) // 2, int(t) // 8) - 0.5) * 0.4 \
        + math.sin(t * 0.7 + s * 0.05 + hr(int(s // 53), 3) * 9) * 0.15
    a, b = 9, 46
    if a <= panel <= b and 12 <= t <= 30:
        if panel < a + 1.2 or t < 13.2:
            return 3.6
        if panel > b - 1.2 or t > 28.8:
            return 1.0
    if t > h - 6:
        v -= 0.8                                   # el sòcol, fosc
    return v


def _formica(s, t, P):
    v = 3.6 + (0.6 if (int(s * 3) + int(t)) % 23 == 0 else 0) + 0.6 * max(0.0, 1 - abs(P[0] - FLUO[0]) / 90)
    for i in range(6):                                                         # les rodones dels gots
        rx = 20 + hr(i, 51) * (BAR[1] - BAR[0] - 40)
        d = math.hypot(s - rx, (t - 14) * 1.0)
        if 2.4 < d < 3.4:
            v -= 0.7
    return v


def escena(cv, tex, estat=frozenset(), dia=False, llums=None, cam=None, primer_pla=True, damunt=None):
    """Tota la sala, de lluny a prop. `estat`: els decorats ('tap', 'comandament', 'rebost_tancat'). `dia`: la
    llum de la tarda; `cam`, `primer_pla`, `damunt` (el que hi ha damunt la barra) i les claus 'tv_box', 'tv_crop' i
    'pernil' de `tex`: el bar del final. → l'Escena (qui ha pintat què)."""
    cam = cam or CAM
    e = Escena(cv, cam, llums if llums is not None else LLUMS, ambient=-0.45 if not dia else -0.05)
    zn = cam.pos[2] + 60
    fons, facana, ob = tex['fons'], tex['facana'], tex['obj']
    # la paret del fons (z = ZW): la textura (x -40..600) i, a l'esquerra, més paret; i el guix de dalt
    e.quad('paret_fons', (XL, HW, ZW), (TX0, HW, ZW), (TX0, 0, ZW), (XL, 0, ZW), tex=(tex['buida'], (0, 0, TX0 - XL, HW)))
    e.quad('paret_fons', (TX0, HW, ZW), (XR, HW, ZW), (XR, 0, ZW), (TX0, 0, ZW), tex=(fons, (0, 0, XR - TX0, HW)))
    e.quad('guix', (XL, HT, ZW), (XR, HT, ZW), (XR, HW, ZW), (XL, HW, ZW), ramp=WALLY, lvl=_guix(2.3))
    # la façana (x = XR), de la cantonada cap a la càmera
    e.quad('facana', (XR, HW, ZW), (XR, HW, zn), (XR, 0, zn), (XR, 0, ZW), tex=(facana, (0, 0, ZW - zn, HW)))
    e.quad('guix', (XR, HT, ZW), (XR, HT, zn), (XR, HW, zn), (XR, HW, ZW), ramp=WALLY, lvl=_guix(2.1, seed=5))
    # el terra
    e.quad('terra', (XL, 0, ZW), (XR, 0, ZW), (XR, 0, zn), (XL, 0, zn), ramp=TERRAZ, lvl=terratzo)
    # la llum: el fluorescent damunt la barra, el neó de l'aparador en diagonal, i (si en Tomàs hi és) la ratlla
    # de llum de sota la porta del rebost
    if not dia:
        e.claror((BAR[0] - 60, 0.3, BAR[2]), (BAR[1] + 60, 0.3, BAR[2]), (BAR[1] + 60, 0.3, BAR[2] - 170),
                 (BAR[0] - 60, 0.3, BAR[2] - 170), (230, 220, 160),
                 lambda s, t: 0.13 * max(0.0, 1 - abs(s - 207) / 207) * max(0.0, 1 - t / 170))
        e.claror((XR - 330, 0.4, ZW), (XR, 0.4, ZW), (XR, 0.4, 60), (XR - 330, 0.4, 60), (255, 90, 200),
                 lambda s, t: _llum_neo(XR - 330 + s, ZW - t))
    if 'rebost_tancat' in estat:
        rx = (REBOST[0] + REBOST[1]) / 2
        e.claror((rx - 40, 0.5, ZW), (rx + 40, 0.5, ZW), (rx + 40, 0.5, ZW - 40), (rx - 40, 0.5, ZW - 40), (255, 210, 130),
                 lambda s, t: 0.5 * max(0.0, 1 - abs(s - 40) / 34) * max(0.0, 1 - t / 30))
    # tovallons, escuradents i pipes pel terra (sobretot davant la barra)
    for i in range(26):
        x = 120 + hr(i, 11) * 420
        z = 70 + hr(i, 12) * 140
        k = hr(i, 13)
        if k > 0.45:
            e.quad('terra', (x - 3, 0.6, z + 2), (x + 3, 0.6, z + 3), (x + 4, 0.6, z - 2), (x - 3, 0.6, z - 3), ramp=SHEET,
                   lvl=lambda s, t, P: 4.0 - t * 0.3 - (0.8 if abs(s - 3) < 0.6 else 0))
        elif k > 0.2:
            e.quad('terra', (x, 0.6, z + 0.6), (x + 6, 0.6, z + 1.6), (x + 6, 0.6, z + 0.6), (x, 0.6, z - 0.4), ramp=CARD,
                   lvl=4.0)
    # la foscor dels racons i de dalt de les parets
    e.foscor('racons', (XL, 0.5, ZW), (XR, 0.5, ZW), (XR, 0.5, zn), (XL, 0.5, zn),
             lambda s, t: max(0.55 * max(0.0, 1 - t / 30), 0.5 * max(0.0, 1 - (XR - XL - s) / 30)))
    e.foscor('cantonada', (XR - 70, HT, ZW - 0.5), (XR, HT, ZW - 0.5), (XR, 0, ZW - 0.5), (XR - 70, 0, ZW - 0.5),
             lambda s, t: 0.5 * max(0.0, 1 - (70 - s) / 70))
    e.foscor('sostre_fosc', (XL, HT - 0.5, ZW - 0.6), (XR, HT - 0.5, ZW - 0.6), (XR, 0, ZW - 0.6), (XL, 0, ZW - 0.6),
             lambda s, t: 0.5 * max(0.0, 1 - t / 90))
    e.foscor('sostre_fosc', (XR - 0.6, HT - 0.5, ZW), (XR - 0.6, HT - 0.5, zn), (XR - 0.6, 0, zn), (XR - 0.6, 0, ZW),
             lambda s, t: 0.5 * max(0.0, 1 - t / 90))
    # el taulell del darrere (la cafetera, la cervesera i la caixa, dretes), arran de les lleixes
    bx0, bx1, bz0, bz1, bh = BACK
    e.caixa('taulell', bx0, bx1, 0, bh, bz0, bz1, WOOD, 2.2,
            cares={'dalt': {'ramp': STEELB, 'lvl': lambda s, t, P: 3.6 + (0.6 if int(s) % 9 == 0 else 0)},
                   'davant': {'ramp': WOOD, 'lvl': lambda s, t, P: 1.6 + (0.8 if int(s) % 40 < 2 else 0)
                              + (hr(int(s) // 3, int(t) // 9) - 0.5) * 0.3},
                   'esquerra': {'ramp': WOOD, 'lvl': 1.4}})
    for box, x in ((GAGGIA, _w(258) + 36), (CERVESERA, _w(232)), (CAIXA, _w(496))):
        _dret(e, 'taulell', ob, box, (x, bh, (bz0 + bz1) / 2), box[3])
    # la tele, en el suport: una caixa amb la pantalla al davant
    tx0, tx1, ty0, ty1, tz0, tz1 = tex.get('tv_box', TV)
    e.caixa('tele', tx0, tx1, ty0, ty1, tz0, tz1, PLASTIC, 1.4,
            cares={'davant': {'tex': (tex['tele'], tex.get('tv_crop', TV_CROP))}, 'dalt': {'ramp': PLASTIC, 'lvl': 2.6},
                   'esquerra': {'ramp': PLASTIC, 'lvl': 1.8}})
    # l'escurabutxaques, girat, al costat del rebost
    sx, sz, sw, sd, sh, sa = SLOT
    e.foscor('ombra_escura', (sx - 30, 0.6, sz + 26), (sx + 30, 0.6, sz + 26), (sx + 30, 0.6, sz - 30),
             (sx - 30, 0.6, sz - 30), lambda s, t: 0.55 * max(0.0, 1 - ((s - 30) / 30) ** 2 - ((t - 28) / 26) ** 2) * 1.4)
    e.caixa_girada('escurabutxaques', sx, sz, sw, sd, sh, sa, PL.FORMICA, 2.0,
                   cares={'davant': {'tex': (tex['escura'], SLOT_CROP)},
                          'dalt': {'ramp': PL.FORMICA, 'lvl': 2.8}, 'esquerra': {'ramp': PL.FORMICA, 'lvl': 1.6},
                          'dreta': {'ramp': PL.FORMICA, 'lvl': 1.2}})
    # la barra: l'ombra, el frontal de plafons, la tapa de fòrmica amb el cantell d'alumini i la barana de llautó
    x0, x1, zf, zb, h = BAR
    e.foscor('ombra_barra', (x0 - 6, 0.6, zb), (x1 + 8, 0.6, zb), (x1 + 8, 0.6, zf - 22), (x0 - 6, 0.6, zf - 22),
             lambda s, t: 0.55 * min(1.0, max(0.0, (zb - zf + 22 - t) / 22)))
    e.caixa('barra', x0, x1, 0, h - 5, zf, zb, WOOD, 2.0,
            cares={'davant': {'ramp': WOOD, 'lvl': _plafons},
                   'esquerra': {'ramp': WOOD, 'lvl': lambda s, t, P: 1.6 + (0.6 if s % 15 < 1.5 else 0)}})
    e.caixa('barra', x0 - 4, x1 + 4, h - 5, h, zf - 5, zb, FORMICA, 3.0,
            cares={'dalt': {'ramp': FORMICA, 'lvl': _formica},
                   'davant': {'ramp': STEELB, 'lvl': lambda s, t, P: 4.6 - t * 0.5},
                   'esquerra': {'ramp': STEELB, 'lvl': 3.4}})
    e.tub('barana', (x0 + 6, 10, zf - 9), (x1 - 6, 10, zf - 9), 1.6, BRASS, 3.0)
    for bx in range(x0 + 30, x1, 80):
        e.caixa('barana', bx - 0.8, bx + 0.8, 0, 10, zf - 10, zf - 8, BRASS, 2.4)
        e.caixa('barana', bx - 0.8, bx + 0.8, 9, 11, zf - 9, zf, BRASS, 2.4)
    # damunt la barra: el pot de les propines, el tovalloner, el cafè d'en Marcel i l'ampolla buida
    zt = zf + 10
    for box, x in ((CAFE, _w(192)), (POT, _w(308)), (TOVALLONER, _w(416)), (AMPOLLA, _w(544))):
        _dret(e, 'damunt', ob, box, (min(x, x1 - 10), h, zt), box[3] - 2)
    if damunt:
        damunt(e)
    if 'tap' in estat:
        _tap(e)
    if 'comandament' in estat:
        _comandament(e)
    # el fluorescent, penjat del sostre damunt la barra
    fx, fy, fz = FLUO
    for dx in (-100, 100):
        e.cable('fluorescent', [(fx + dx, HT, fz), (fx + dx, fy + 4, fz)], STEELB, 2.0, gruix=0.8)
    e.caixa('fluorescent', fx - 104, fx + 104, fy + 2, fy + 6, fz - 5, fz + 5, STEELB, 2.6)
    TUBE = [(120, 110, 70), (220, 210, 150), (255, 248, 210), (255, 255, 240)]
    e.tub('fluorescent', (fx - 100, fy, fz - 2), (fx + 100, fy, fz - 2), 1.6, TUBE, 3.0 if not dia else 1.2)
    # el pernil, penjat del sostre a la cantonada
    if tex.get('pernil', True):
        hx, hz = HAM
        e.cable('pernil', [(hx, HT, hz), (hx, 200 - 12, hz)], SLATE, 1.6, gruix=0.8)
        _dret(e, 'pernil', ob, PERNIL, (hx, 200 - PERNIL[3] + PERNIL[1], hz), PERNIL[3])
    # els tamborets, davant la barra: volums (la base, la columna, el reposapeus i el seient de skai), amb l'ombra
    for k, sx_ in enumerate(STOOLS):
        _tamboret(e, sx_, STOOL_Z, k)
    if primer_pla:
        _primer_pla(e)
    return e


def _primer_pla(e):
    """Primer pla: una taula i dues cadires en silueta a baix a l'esquerra, el pilar a la dreta."""
    FOSC = [(5, 3, 3), (11, 7, 6), (18, 12, 10), (26, 18, 14), (36, 26, 20), (48, 36, 28)]
    tx, tz = 92, 26
    e.caixa_girada('primer_pla', tx, tz, 70, 70, 4, 0.2, FOSC, 2.4, y0=66,
                   cares={'dalt': {'ramp': FOSC, 'lvl': lambda s, t, P: 2.4 + (fbm(s / 20, t / 20, 2) - 0.5) * 0.6
                                   + (2.0 if t > 66 or s > 66 else 0)
                                   - (1.4 if math.hypot(s - 30, t - 34) < 7 else 0)},     # el cantell, i un cendrer
                          'davant': {'ramp': FOSC, 'lvl': 3.6}, 'dreta': {'ramp': FOSC, 'lvl': 3.0}})
    e.tub('primer_pla', (tx, 0, tz), (tx, 66, tz), 3.4, FOSC, 1.8)
    for cx, cz, a in ((tx + 46, tz - 30, 0.5), (tx - 20, tz + 52, -0.3)):
        e.caixa_girada('primer_pla', cx, cz, 34, 34, 4, a, FOSC, 2.0, y0=40)
        c_, s_ = math.cos(a), math.sin(a)
        for lx, lz in ((-15, -15), (15, -15), (-15, 15), (15, 15)):
            px_, pz_ = cx + lx * c_ - lz * s_, cz + lx * s_ + lz * c_
            e.caixa('primer_pla', px_ - 1.5, px_ + 1.5, 0, 40, pz_ - 1.5, pz_ + 1.5, FOSC, 1.4)
        e.caixa_girada('primer_pla', cx - 16 * s_, cz + 16 * c_, 34, 3, 40, a, FOSC, 1.6, y0=44)     # el respatller
    px_, pz_ = PILAR
    e.caixa('primer_pla', px_ - 16, px_ + 16, 0, HT, pz_ - 16, pz_ + 16, FOSC, 1.6,
            cares={'davant': {'ramp': FOSC, 'lvl': lambda s, t, P: 1.4 + (0.6 if s < 3 else 0)},
                   'esquerra': {'ramp': FOSC, 'lvl': lambda s, t, P: 2.2 + (hr(int(s) // 3, int(t) // 5) - 0.5) * 0.4}})


def _disc(e, sid, cx, cz, r, y, ramp, lvl):
    """Un disc horitzontal (de cara amunt) de radi `r` a l'alçada `y`: `lvl(dx, dz)` des del centre."""
    e.quad(sid, (cx - r, y, cz + r), (cx + r, y, cz + r), (cx + r, y, cz - r), (cx - r, y, cz - r), ramp=ramp,
           lvl=lambda s, t, P: lvl(s - r, r - t), forma=lambda s, t: (s - r) ** 2 + (t - r) ** 2 <= r * r)


def _cilindre(e, sid, cx, cz, r, y0, y1, ramp, lvl, n=20, gir=0.0):
    """Un cilindre dret (el costat, a cares: la llum del món hi cau cara per cara). `lvl(a, t)`: a = l'angle de la
    cara, t = l'alçada des de baix. La tapa, a part (_disc)."""
    for i in range(n):
        a0, a1 = gir + 2 * math.pi * i / n, gir + 2 * math.pi * (i + 1) / n
        P0 = (cx + r * math.cos(a0), y1, cz + r * math.sin(a0))
        P1 = (cx + r * math.cos(a1), y1, cz + r * math.sin(a1))
        am = (a0 + a1) / 2
        e.quad(sid, P0, P1, (P1[0], y0, P1[2]), (P0[0], y0, P0[2]), ramp=ramp,
               lvl=lambda s, t, P, am=am: lvl(am, y1 - y0 - t))


SKAI = [(26, 4, 8), (54, 10, 14), (92, 18, 22), (136, 28, 30), (180, 46, 42), (216, 84, 66), (244, 140, 110)]


def _tamboret(e, x, z, k):
    """Un tamboret de bar: la base rodona, la columna cromada, el reposapeus en anella amb tres radis, el plat de
    sota i el seient de skai vermell amb el ribet. `k`: cadascun una mica diferent (el gir, el desgast, l'alçada) i el
    tercer, amb el seient esquinçat i cinta americana."""
    sid = 'tamborets'
    gir = (0.4, 1.3, 2.1, 0.9)[k % 4]
    dl = (0.0, -0.25, 0.15, -0.1)[k % 4]                  # el desgast: uns més mats que d'altres
    hs = (54, 53, 55, 53.5)[k % 4]                         # el seient (dalt)
    fx = FLUO[0]
    # l'ombra: el seient la fa una mica cap a fora del fluorescent i cap a la càmera; i la base, a terra, de contacte
    ox, oz = x + (x - fx) * 0.1, z - 5
    e.foscor('ombra_tamboret', (ox - 20, 0.7, oz + 20), (ox + 20, 0.7, oz + 20), (ox + 20, 0.7, oz - 20),
             (ox - 20, 0.7, oz - 20), lambda s, t: 0.5 * max(0.0, 1 - ((s - 20) ** 2 + (t - 20) ** 2) / 400) * 1.5)
    e.foscor('ombra_tamboret', (x - 15, 0.8, z + 15), (x + 15, 0.8, z + 15), (x + 15, 0.8, z - 15), (x - 15, 0.8, z - 15),
             lambda s, t: 0.7 * max(0.0, 1 - ((s - 15) ** 2 + (t - 15) ** 2) / 225) * 2)
    # la base: un plat baix i bombat
    _cilindre(e, sid, x, z, 12, 0, 2.2, STEELB, lambda a, t: 2.0 + dl - math.sin(a) * 0.6, gir=gir)
    _disc(e, sid, x, z, 12, 2.2, STEELB,
          lambda dx, dz: 3.4 + dl + (1.6 if -4 < dx < -1 and 1 < dz < 5 else 0) - math.hypot(dx, dz) * 0.07)
    # el reposapeus (l'anella i els radis): la meitat del fons abans de la columna, la del davant després
    yr, rr = 20 + (k % 2), 10
    pts = [(x + rr * math.cos(gir + i * math.pi / 8), yr, z + rr * math.sin(gir + i * math.pi / 8)) for i in range(17)]
    radis = [(x + rr * math.cos(gir + i * 2 * math.pi / 3), yr, z + rr * math.sin(gir + i * 2 * math.pi / 3))
             for i in range(3)]
    seg = list(zip(pts, pts[1:])) + [((x, yr, z), R) for R in radis]
    lluny = [s_ for s_ in seg if (s_[0][2] + s_[1][2]) / 2 >= z]
    a_prop = [s_ for s_ in seg if (s_[0][2] + s_[1][2]) / 2 < z]
    for A, B_ in sorted(lluny, key=lambda s_: -(s_[0][2] + s_[1][2])):
        e.tub(sid, A, B_, 1.0, STEELB, 3.2 + dl)
    e.tub(sid, (x, 2, z), (x, hs - 8, z), 1.7, STEELB, 3.0 + dl)          # la columna
    for A, B_ in sorted(a_prop, key=lambda s_: -(s_[0][2] + s_[1][2])):
        e.tub(sid, A, B_, 1.0, STEELB, 3.6 + dl)
    # el plat de sota el seient i el seient: el costat (amb el ribet a dalt i a baix) i la tapa
    _cilindre(e, sid, x, z, 7, hs - 9, hs - 6, STEELB, lambda a, t: 2.2 + dl - math.sin(a) * 0.5, n=12, gir=gir)
    _cilindre(e, sid, x, z, 15, hs - 6, hs, SKAI,
              lambda a, t: 2.4 + dl - math.sin(a) * 0.5 + (0.9 if t > 5.2 else 0) - (0.9 if t < 0.8 else 0)
              + (0.3 if int(a * 6) % 5 == 0 else 0), gir=gir)

    def seient(dx, dz):
        d = math.hypot(dx, dz)
        v = 3.4 + dl - d * 0.04 - dz * 0.02                  # bombat: més clar al mig
        if d > 13.4:
            v += 0.8                                         # el ribet
        if math.hypot(dx + 5, dz - 6) < 2.6:
            v += 1.6                                         # el reflex del skai
        if k == 2:                                           # l'esquinç (la cinta hi va damunt)
            u, w = dx * math.cos(gir) + dz * math.sin(gir), -dx * math.sin(gir) + dz * math.cos(gir)
            if 0 < u < 11 and abs(w) < 0.5:
                return 0.6
        return v
    _disc(e, sid, x, z, 15, hs, SKAI, seient)
    if k == 2:                                                # dues tires de cinta americana, en creu sobre l'esquinç
        tape = [(60, 60, 64), (110, 110, 116), (160, 160, 166), (196, 196, 200)]
        c, s = math.cos(gir), math.sin(gir)
        for u0, w0 in ((3, 0.4), (8, -0.3)):
            P = [(x + u * c - w * s, hs + 0.3, z + u * s + w * c) for u, w in
                 ((u0 - 1.3, w0 - 3.2), (u0 + 1.3, w0 - 3.2), (u0 + 1.3, w0 + 3.2), (u0 - 1.3, w0 + 3.2))]
            e.quad(sid, P[0], P[1], P[2], P[3], ramp=tape, lvl=lambda s_, t, P_: 3.0 + (0.8 if t < 0.8 else 0),
                   dues_cares=True)


def _dret(e, sid, img, box, peu, base_y):
    """Un retall del dibuix pla, dret, amb la base (la y `base_y` del dibuix) al punt `peu` del món."""
    e.sprite(sid, img.crop(box), ((box[2] - box[0]) / 2, base_y - box[1]), peu)


def _llum_neo(x, z):
    """Quanta llum del neó (0..1) arriba al terra: la taca que entra per l'aparador, en diagonal cap a l'esquerra i
    cap a la càmera."""
    z0, z1, _, _ = WINZ
    d = XR - x                                     # la distància a la façana
    zc = z - (-0.55 * d)                           # la llum va cap a la càmera a mesura que s'allunya de la paret
    if not (z0 + 4 < zc < z1 - 4):
        return 0.0
    if abs(zc - (z0 + z1) / 2) < 2:
        return 0.0                                 # el muntant del mig
    return max(0.0, 1 - d / 300) * 0.38


def _tap(e):
    """El clauer d'en Tomàs damunt la barra: el tap de la cervesera amb l'anella i dues claus."""
    cv = _llenc(transparent=True)
    PL.tap_barra(cv)
    e.sprite('tap', cv.img.crop((335, 143, 358, 160)), (8, 14), TAP_P)


def _comandament(e):
    """El comandament de la tele, damunt la barra, una mica girat."""
    x, z = COM_P[0], COM_P[2]
    e.caixa_girada('comandament', x, z, 24, 7, 2.4, 0.18, PLASTIC, 1.8, y0=BAR[4],
                   cares={'dalt': {'ramp': PLASTIC, 'lvl': lambda s, t, P: 1.0 if (int(s) % 3 == 0 and 1 < t < 6 and s > 6)
                                   else (3.4 if s < 3 else 2.4)}})


TAP_P = (_w(343) - 20, BAR[4], BAR[2] + 9)
COM_P = (_w(388) - 4, BAR[4], BAR[2] + 12)


# ─── Composició i llum ──────────────────────────────────────────────────────

def _proj(P):
    u, v, _ = CAM.projecta(P)
    return u, v


def _fx():
    fx, fy = _proj(FLUO)
    tx, ty = _proj(TV_C)
    sx, sy = _proj(SLOT_C)
    wx, wy = _proj(WIN_C)
    light = [llum.wash(fx, fy + 110, 250, (255, 220, 140), k=0.35, air=0.02, squash=1.2),       # el fluorescent
             llum.wash(tx, ty, 90, (90, 150, 230), k=0.8, air=0.05),                          # la tele
             llum.wash(sx, sy, 60, (200, 110, 240), k=0.8, air=0.05),                         # l'escurabutxaques
             llum.wash(wx, wy, 120, (255, 90, 200), k=0.8, air=0.06, squash=0.7)]             # el neó
    tone = [llum.grade(contrast=1.1, pivot=50, sat=1.15, lift=(6, 3, 6))]
    s0, s1 = _proj((SIGN[0], SIGN[3] + 4, ZW)), _proj((SIGN[1], SIGN[2] - 4, ZW))
    bloom = [llum.bloom(thr=175, mask=lambda x, y: 1 - 0.9 * ((x > s0[0]) & (x < s1[0]) & (y > s0[1]) & (y < s1[1])))]
    return light, bloom, tone


def _render(estat=frozenset(), tex=None):
    cv = Canvas(light=LIGHT)
    e = escena(cv, tex or _textures(), estat)
    cv.rect(0, BOTTOM + 1, W - 1, H - 1, [(0, 0, 0)], 0, lit=0)    # la barra de verbs: negre
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


def _decorat(*estat, tex=None):
    """Un decorat: la sala amb aquell estat, menys la de sempre (només el que canvia), amb la llum."""
    def draw(cv):
        img, _ = _render(frozenset(estat), tex)
        out = _diff(_amb_llum(img, bloom=False), _amb_llum(_base()[0], bloom=False))
        cv.img.alpha_composite(out)
        cv.P = cv.img.load()
    return draw


PROPS = {
    'tap_barra': _decorat('tap'),
    'comandament_barra': _decorat('comandament'),
    'tele_bassols': lambda cv: _decorat(tex=_textures(bassols=True))(cv),
    'rebost_tancat': lambda cv: _decorat('rebost_tancat', tex=_textures(rebost_tancat=True))(cv),
}


# ─── Animació ───────────────────────────────────────────────────────────────

def _fotograma(capes):
    """El fons amb unes capes damunt, amb la llum, menys el fons amb la llum."""
    img, _ = _base()
    img = img.copy()
    for c in capes:
        img.alpha_composite(c)
    return _diff(_amb_llum(img), _base_llum())


def _frames():
    """16 fotogrames: el neó fa un mal contacte (dos cops), el futbol, l'escurabutxaques i els camions."""
    _, e = _base()
    out = []
    for i in range(16):
        capes = [e.capa(_facana(flick=1 if i in (10, 12) else 0, frame=i), {'facana'}),
                 e.capa(_tele(i), {'tele'}),
                 e.capa(_escurabutxaques(i), {'escurabutxaques'})]
        out.append(_fotograma(capes))
    return out


ANIMS = {'bar': {'frames': _frames, 'frameDuration': 220}}


# ─── Capes del davant ───────────────────────────────────────────────────────

def _amo(ids, u0=0, u1=W):
    def mask(x, y):
        if not u0 <= x < u1:
            return False
        _, e = _base()
        return e.ids[e.amo[y * e.cv.w + x]] in ids
    return mask


def _p(x, z, y=0.0):
    u, v, _ = CAM.projecta((x, y, z))
    return round(u), round(v)


def _davant_barra():
    """La barra (amb el que hi ha damunt i els tamborets), a trossos: la línia base de cada tros és on el frontal
    toca a terra a la dreta del tros (la barra fuig: a l'esquerra és més avall)."""
    x0, x1, zf, zb, h = BAR
    ids = {'barra', 'barana', 'damunt', 'tamborets'}
    out = []
    talls = [0] + [_p(x, zf)[0] for x in range(x0 + 60, x1, 60)] + [W]
    for n, (ua, ub) in enumerate(zip(talls, talls[1:])):
        # el punt del frontal (a terra) més amunt de la pantalla dins el tros
        xs = [x for x in range(x0 - 4, x1 + 5, 2) if ua <= _p(x, zf - 5)[0] < ub]
        base = min(_p(x, zf - 5)[1] for x in xs) if xs else _p(x0, zf - 5)[1]
        f = {'id': f'davant_barra{n + 1}', 'mask': _amo(ids, ua, ub), 'baseline': base, 'zIndex': 20}
        out.append(f)
    tu = _p(TAP_P[0], TAP_P[2])[0]
    for f, (ua, ub) in zip(out, zip(talls, talls[1:])):
        if ua <= tu < ub:
            f['props'] = ('tap_barra', 'comandament_barra')
    return out


FRONT = [{'id': 'davant', 'mask': _amo({'primer_pla'}), 'baseline': 999, 'zIndex': 20},
         {'id': 'davant_escura', 'mask': _amo({'escurabutxaques'}), 'baseline': _p(SLOT[0], SLOT[1] - 14)[1],
          'zIndex': 20}] + _davant_barra()


# ─── Geometria (coordenades de sala, projectades) ────────────────────────────

def _rect_mon(*Ps):
    pts = [CAM.projecta(P) for P in Ps]
    return (max(0, round(min(p[0] for p in pts))), max(0, round(min(p[1] for p in pts))),
            min(W - 1, round(max(p[0] for p in pts))), min(BOTTOM, round(max(p[1] for p in pts))))


def _escala_a(v):
    """L'escala d'un personatge amb els peus a la y de pantalla `v` (al terra, la profunditat només depèn de v)."""
    lo, hi = 1.0, 4000.0
    for _ in range(60):
        z = (lo + hi) / 2
        if CAM.projecta((300, 0, z))[1] > v:
            lo = z
        else:
            hi = z
    return CAM.escala((300, 0, (lo + hi) / 2))


def _v_escala(k):
    """La y de pantalla on un personatge fa escala `k`."""
    lo, hi = 0.0, float(BOTTOM)
    for _ in range(50):
        m = (lo + hi) / 2
        if _escala_a(m) < k:
            lo = m
        else:
            hi = m
    return (lo + hi) / 2


def _retalla_v(poly, vmax):
    """El polígon de pantalla `poly` sense el que queda per sota de la y `vmax`."""
    out = []
    for (ax, ay), (bx, by) in zip(poly, poly[1:] + poly[:1]):
        if ay <= vmax:
            out.append((ax, ay))
        if (ay <= vmax) != (by <= vmax):
            k = (vmax - ay) / (by - ay)
            out.append((round(ax + (bx - ax) * k), round(vmax)))
    return out


# El terra on es camina (al món): davant els tamborets, el passadís del rebost (entre l'escurabutxaques i la paret)
# i, a la dreta, fins a la porta del carrer; el de més a prop (on un personatge faria més d'1,2) queda per al primer
# pla.
WALK_MON = [(56, 318), (128, 318), (136, 270), (190, 236), (226, 186), (486, 186), (520, 230), (588, 230),
            (588, -60), (40, -60)]
V_MAX = _v_escala(1.2)
_WALK = _retalla_v([_p(x, z) for x, z in WALK_MON], V_MAX)
_V_FONS = min(v for _, v in _WALK)
_V_TOMAS = _p(360, 276)[1]


GEOMETRIA = {
    'things': {
        'porta': {'rect': _rect_mon((XR, DOORZ[3], DOORZ[0]), (XR, 0, DOORZ[1])), 'walk': _p(570, 70)},
        'porta_rebost': {'rect': _rect_mon((REBOST[0], REBOST[3], ZW), (REBOST[1], 0, ZW)),
                         'walk': _p((REBOST[0] + REBOST[1]) / 2, ZW - 22)},
        'retol': {'rect': _rect_mon((SIGN[0], SIGN[3], ZW), (SIGN[1], SIGN[2], ZW)), 'walk': _p((SIGN[0] + SIGN[1]) / 2, 176)},
        'tele': {'rect': _rect_mon((TV[0], TV[3], TV[4]), (TV[1], TV[2], TV[4]), (TV[1], TV[2], TV[5])),
                 'walk': _p((TV[0] + TV[1]) / 2 - 10, 176)},
        'telefon': {'rect': _rect_mon((XR, PHONE[3], PHONE[0]), (XR, PHONE[2], PHONE[1])), 'walk': _p(570, 186)},
        'tap_barra': {'rect': _rect_mon(*[(TAP_P[0] + dx, BAR[4] + dy, TAP_P[2] + dz) for dx in (-12, 12)
                                          for dz in (-8, 8) for dy in (0, 10)]),
                      'walk': _p(TAP_P[0], 180)},
        'comandament_barra': {'rect': _rect_mon(*[(COM_P[0] + dx, BAR[4] + dy, COM_P[2] + dz) for dx in (-16, 16)
                                                  for dz in (-8, 8) for dy in (0, 8)]),
                              'walk': _p(COM_P[0], 180)},
    },
    'spawns': {'marcel': _p(STOOLS[0] - 30, STOOL_Z + 8),   # dret a la punta de la barra, abans del primer tamboret
                'tomas': _p(372, 276), 'vet': _p(330, 120)},
    'walkable': _WALK,
    'floorSquash': 0.42,
    # L'ombra de contacte: la llum dominant és el fluorescent (el punt del terra just a sota).
    'characterShadow': {'enabled': True, 'color': '#100a06', 'alpha': 0.45, 'squash': 0.4, 'core': 0.6,
                        'light': {'x': _p(FLUO[0], FLUO[2])[0], 'y': _p(FLUO[0], FLUO[2])[1], 'stretch': 0.6,
                                  'reach': 180}},
    'regions': [{'id': 'perspectiva', 'active': True, 'scaleEnabled': True, 'scaleWalkSpeed': True,
                 'scaleTop': round(_escala_a(_V_TOMAS - 6), 3), 'scaleBottom': round(_escala_a(BOTTOM), 3),
                 'points': [(0, _V_TOMAS - 6), (W - 1, _V_TOMAS - 6), (W - 1, BOTTOM), (0, BOTTOM)]}],
    'characterLights': {
        'ambient': '#a89c88',                                                          # el bar, groguenc
        'lights': [
            {'x': _p(FLUO[0], FLUO[2], FLUO[1])[0], 'y': _p(FLUO[0], FLUO[2], FLUO[1])[1], 'radius': 300,
             'color': '#ffe6a0', 'intensity': 0.9},                                    # el fluorescent
            {'x': _p(TV_C[0], TV_C[2], TV_C[1])[0], 'y': _p(TV_C[0], TV_C[2], TV_C[1])[1], 'radius': 110,
             'color': '#5a96e6', 'intensity': 0.7},                                    # la tele
            {'x': _p(SLOT_C[0], SLOT_C[2], SLOT_C[1])[0], 'y': _p(SLOT_C[0], SLOT_C[2], SLOT_C[1])[1], 'radius': 80,
             'color': '#c86ef0', 'intensity': 0.7},                                    # l'escurabutxaques
            {'x': _p(WIN_C[0], WIN_C[2], WIN_C[1])[0], 'y': _p(WIN_C[0], WIN_C[2], WIN_C[1])[1], 'radius': 160,
             'color': '#ff5ac8', 'intensity': 0.7},                                    # el neó
        ],
    },
}

# Coses per mirar (tasca 012): rectangles de pantalla; s'hi va pel punt d'una cosa del costat.
GEOMETRIA['things'].update({
    'escurabutxaques': {'rect': (117, 115, 163, 190), 'walk': GEOMETRIA['things']['porta_rebost']['walk']},
    'foto': {'rect': (103, 85, 123, 108), 'walk': GEOMETRIA['things']['porta_rebost']['walk']},
    'bufanda': {'rect': (125, 73, 180, 92), 'walk': GEOMETRIA['things']['porta_rebost']['walk']},
    'cafetera': {'rect': (250, 95, 295, 122), 'walk': GEOMETRIA['things']['retol']['walk']},
})
