"""
El racó de servei de l'aeroport (Escena 3, l'Iri, davant la porta de personal). EN 3D (hd640/tres_d.py), a 1×.

Una càmera alta que mira de biaix la cantonada del fons a l'esquerra, com l'estudi de l'Iri:
  - a la paret de l'esquerra, en escorç, el **vidre** cap a la terminal: a l'altra banda hi ha la terminal de debò
    (el terra de rajola més avall, els seients blaus, el rètol d'objectes perduts i la vidriera de l'alba), i
    mentre vigila, l'**agent Soler** dret darrere el vidre (decorat `soler_vidre`); a sota, el radiador;
  - a la paret del fons, la **porta de personal** amb la franja vermella i el **teclat** (el llum: vermell,
    `alarma` o verd; amb `porta_oberta`, la fulla girada cap endins i l'oficina il·luminada), l'extintor, el senyal
    de sortida i el tauler de torns; les **taquilles** amb volum;
  - el **carro de la neteja**, separat de la paret i girat (s'hi passa per darrere), i el senyal de terra mullat
    amb el bassal;
  - el **fluorescent** que penja del sostre (`fluorescent`: parpelleja), i a dalt, la canonada dels bombers i la
    safata de cables que fugen per les dues parets;
  - primer pla: una canonada vertical i una d'horitzontal en silueta, i una paperera i caixes a baix a l'esquerra.

Tot el detall ve del dibuix pla de sempre (aeroport_personal_pla_comu.py), projectat. Els decorats tornen a pintar la
sala amb aquell estat, i en surt la diferència.

El món: x a la dreta (0 = la paret del vidre), y amunt (0 = el terra), z cap al fons (300 = la paret del fons);
1 unitat = 1 píxel de sala a la distància on un personatge fa ≈111 px (escala 1).
"""
import functools
import math

from PIL import Image

import hd640  # noqa: F401  (abans de cap hd.rooms: posa la llibreria a 640×360)
from hd.pix import Canvas, Light, W, H, hr
from hd.rooms.comu import _diff, outline, SHEET
from hd.rooms.exterior import fbm
from hd.personatges import NPCS
from hd640.draw_characters import person
from hd640.rooms import aeroport_personal_pla_comu as PL
from hd640.rooms.aeroport_personal_pla_comu import (BLOCK, LINO, CONC, TILE, CHROME, DOOR, REDB, YELS, TROLLEY,
                                                    SLATE, BLUE, CARD)
from hd640.tres_d import Camera, Escena, Llum

BOTTOM = 259                                       # la sala acaba aquí (a sota, la barra de verbs)
ZW = 300                                           # la paret del fons
HW = 200                                           # l'alçada de les parets (el dibuix pla fa 200 fins al terra)
XL = 250                                           # al dibuix pla, la cantonada: a l'esquerra, la paret del vidre
XR = 780                                           # on s'acaba la paret del fons (fora de la pantalla)
TROL = (262, 214, 84, 36, 0.42)                    # el carro: x, z del centre, ample, fons, gir
CONE = (82, 168)                                   # el senyal de terra mullat (x, z)
LAMP = (220, 184, 140)                             # el fluorescent que penja: x, y, z del centre
TERM_Y = -14                                       # el terra de la terminal, una mica més avall
TERM_X = -250                                      # la paret del fons de la terminal
SOLER = (-62, 196)                                 # en Soler, dret a la terminal (x, z)


def _w(fx):
    """Una x del dibuix pla de la paret del fons → la x del món."""
    return fx - XL


def _wz(fx):
    """Una x del dibuix pla de la paret del vidre → la z del món."""
    return ZW - XL + fx


def _y(fy):
    """Una y del dibuix pla (el terra, a 200) → l'alçada del món."""
    return HW - fy


GLASS = (_wz(PL.GLASS[0]), _wz(PL.GLASS[2]), _y(PL.GLASS[3]), _y(PL.GLASS[1]))      # z0, z1, y0, y1
DOOR_W = (_w(PL.DOOR_BOX[0]), _w(PL.DOOR_BOX[2]), 0, _y(PL.DOOR_BOX[1]))           # x0, x1, y0, y1
KEYPAD = (_w(PL.KEYPAD[0]), _w(PL.KEYPAD[2]), _y(PL.KEYPAD[3]), _y(PL.KEYPAD[1]))
LOCK_BOX = (547, 67, 633, 201)                     # les taquilles, de cara, al dibuix pla
LOCK_D = 40

CAM = Camera(pos=(420, 190, -260), yaw=-0.36, pitch=0.16, f=440, centre=(320, 90))

LIGHT = Light(ambient=0.0, vignette=None, floor_fade=None)  # (la llum és la del món: la de l'Escena)
TEX_LIGHT = Light(ambient=0.1, vignette=None, floor_fade=None)    # el dibuix pla de les textures, sense vinyeta
TEX_LIGHT.point(315, 148, r=35, k=0.4, squash=1.0, power=2.0)    # el llum del teclat

LLUMS = [Llum((LAMP[0], LAMP[1] - 6, LAMP[2]), 340, 2.0, power=1.3),       # el fluorescent
         Llum((-40, 120, (GLASS[0] + GLASS[1]) / 2), 260, 0.9, power=1.5),   # la claror de la terminal pel vidre
         Llum((KEYPAD[0] + 16, 70, ZW - 6), 40, 0.4, power=2.0)]            # el llum del teclat


# ─── Les textures: el dibuix pla de sempre ───────────────────────────────────

def _forat(cv, box):
    """Buida (transparent) un rectangle del dibuix pla: s'hi veurà el que hi ha darrere."""
    x0, y0, x1, y1 = box
    for y in range(y0, y1 + 1):
        for x in range(x0, x1 + 1):
            cv.P[x, y] = (0, 0, 0, 0)


def _marc_vidre(cv):
    """El marc d'alumini del vidre (sense el vidre: és un forat) i l'ampit."""
    x0, y0, x1, y1 = PL.GLASS
    for (a, b, c, d) in ((x0, y0, x1, y0 + 3), (x0, y1 - 3, x1, y1), (x0, y0, x0 + 3, y1), (x1 - 3, y0, x1, y1),
                         (132, y0, 135, y1)):
        cv.rect(a, b, c, d, CHROME, lambda x, y, a=a, b=b: 3.2 + (0.8 if x == a or y == b else 0))
    outline(cv, x0 - 1, y0 - 1, x1 + 1, y1 + 1, BLOCK)
    cv.rect(x0 - 4, y1 + 1, x1 + 4, y1 + 4, CHROME, lambda x, y: 4.0 + (0.8 if y == y1 + 1 else 0))
    cv.darken(x0 - 4, y1 + 5, x1 + 4, y1 + 6, 0.5)


def _paret(led='vermell', oberta=False):
    """Les dues parets planes, de cara: el bloc verd amb les canonades de dalt, el vidre (un forat), el radiador,
    l'extintor, el senyal de sortida, la porta (o el forat de la porta oberta), el teclat i el tauler de torns."""
    cv = Canvas(light=TEX_LIGHT)
    tube, PL.tube = PL.tube, lambda cv, on=True: None             # (el fluorescent penja del sostre: és en 3D)
    try:
        PL.wall(cv)
    finally:
        PL.tube = tube
    x0, y0, x1, y1 = PL.GLASS
    _marc_vidre(cv)
    _forat(cv, (x0 + 4, y0 + 4, 131, y1 - 4))
    _forat(cv, (136, y0 + 4, x1 - 4, y1 - 4))
    PL.radiator(cv)
    PL.extinguisher(cv)
    PL.emergency_sign(cv)
    if oberta:
        dx0, dy0, dx1, dy1 = PL.DOOR_BOX
        PL.obox(cv, dx0 - 5, dy0 - 5, dx1 + 5, dy1, CHROME, 2.6)
        _forat(cv, (dx0, dy0, dx1, dy1))
    else:
        PL.door(cv)
    PL.keypad(cv, 'verd' if oberta else led)
    if led == 'alarma':
        cv.glow(PL.LED[0], PL.LED[1], 61, (255, 40, 30), 0.55)
        cv.disc(PL.LED[0], PL.LED[1], 4, 3.2, [(255, 120, 90)], 0, lit=0)
        cv.flat(PL.LED[0] - 1, PL.LED[1] - 1, (255, 220, 200))
    PL.notice_board(cv)
    return cv.img


def _vista(avio=None):
    """La terminal, de cara (el que es veia pel vidre): la vidriera de l'alba, el rètol i els seients.
    `avio`: el fotograma dels llums de l'avió que s'acosta (None: no hi és)."""
    cv = Canvas(light=TEX_LIGHT)
    PL.terminal_view(cv)
    if avio is not None:
        cv.rect(54, 62, 56, 64, [(250, 240, 220)], 0, lit=0)                       # el far d'aterratge
        cv.glow(55, 63, 4, (255, 236, 200), 0.4)
        if avio in (0, 5):
            cv.rect(57, 60, 58, 61, [(255, 70, 60)], 0, lit=0)                      # el llum anticol·lisió
        if avio == 2:
            cv.rect(49, 63, 50, 64, [(255, 255, 255)], 0, lit=0)                    # els flaixos de les puntes d'ala
            cv.rect(60, 63, 61, 64, [(255, 255, 255)], 0, lit=0)
    return cv.img


def _peces():
    """Les taquilles, el carro, el senyal groc i la porta oberta, plans (se'n treuen retalls)."""
    out = {}
    for nom, fn in (('taquilles', PL.lockers), ('carro', PL.trolley), ('con', PL.wet_floor)):
        cv = Canvas(light=TEX_LIGHT, transparent=True)
        fn(cv)
        out[nom] = cv.img
    cv = Canvas(light=TEX_LIGHT)
    _oficina(cv)
    out['oficina'] = cv.img
    return out


def _oficina(cv):
    """L'oficina, a l'altra banda de la porta oberta (el que es veia a `porta_oberta` del dibuix pla, sense la fulla):
    la llum fluorescent, un arxivador i un racó del pòster de la companyia."""
    x0, y0, x1, y1 = PL.DOOR_BOX
    for y in range(y0, y1 + 1):
        for x in range(x0, x1 + 1):
            cv.put(x, y, CONC if y < 160 else TILE, (4.2 if y < 160 else 4.4) - (y - y0) * 0.006 + (hr(x, y, 17) - 0.5) * 0.2)
    cv.rect(x0, 159, x1, 160, CONC, 2.2)
    PL.obox(cv, 341, 93, 368, 187, PL.DESK, 3.0)
    for k in range(3):
        PL.obox(cv, 344, 97 + k * 30, 365, 123 + k * 30, PL.DESK, 3.4, top=0.6)
        cv.rect(349, 104 + k * 30, 360, 105 + k * 30, CHROME, 4.0)
    cv.darken(341, 188, 370, 190, 0.5)
    PL.obox(cv, 376, 90, 398, 118, [(40, 36, 30), (110, 104, 90), (190, 184, 166)], 1.8)   # un racó del pòster
    cv.rect(378, 92, 396, 108, BLUE, 2.8)
    cv.rect(337, 64, 400, 65, [(230, 244, 255)], 0, lit=0)
    cv.glow(368, 67, 30, (220, 236, 255), 0.3)


BAG_BOX = (446, 135, 482, 172)                     # la bossa groga, penjada del carro
SPRAY_BOX = (487, 149, 508, 172)                   # els dos esprais
BUCKET_BOX = (508, 180, 526, 201)                  # la galleda blava
CONE_BOX = (126, 206, 153, 250)                    # el senyal de terra mullat
VIEW_TOP = 98                                      # al dibuix pla de la terminal: on comença el seu terra


@functools.lru_cache(maxsize=None)
def _textures(led='vermell', oberta=False):
    return {'paret': _paret(led, oberta), 'vista': _vista(), **_peces()}


@functools.lru_cache(maxsize=None)
def _soler():
    return person(NPCS['soler'], 'D')


# ─── Les superfícies ────────────────────────────────────────────────────────

def _bloc(lvl0=4.2, seed=3):
    """Bloc de formigó pintat de verd en coordenades del món (s, t des del cantó de dalt): on el dibuix pla no
    arriba (la paret de prop i la de més enllà de les taquilles)."""
    def L(s, t, P):
        if t < 9:
            return 2.6                                                   # el sostre
        if t < 23:
            return 2.2 + (0.8 if t < 10 else 0)                          # l'ombra de la safata i la canonada
        row = int(t // 13.3)
        off = 20 if row % 2 else 0
        if t % 13.3 < 1 or (s + off) % 40 < 1:
            v = 2.8
        else:
            v = lvl0 + (hr(int((s + off) // 40), row, seed) - 0.5) * 0.3 + (hr(int(s // 2), int(t // 2), 5) - 0.5) * 0.3
        if t > 157:
            v -= 0.9
        if t > HW - 5:
            v = 2.0 if t > HW - 4 else 3.0                               # el sòcol de linòleum
        return v
    return L



def _lino(s, t, P):
    """El linòleum gris, en coordenades del món: les juntes de les lloses que fugen, el camí gastat de la porta i les
    rascades de les rodes."""
    x, z = P[0], P[2]
    v = 3.2 + (fbm(x / 40, z / 30, 4) - 0.5) * 0.5 + (hr(int(x / 2), int(z / 2), 4) - 0.5) * 0.3
    if x % 60 < 1.0 or z % 60 < 1.0:
        v -= 0.9
    v += max(0.0, 1 - math.hypot((x - (DOOR_W[0] + DOOR_W[1]) / 2) / 70, (z - ZW + 30) / 110)) * 0.8
    i = int(x // 50) * 7 + int(z // 24)
    if hr(i, 9) > 0.8 and abs((z % 24) - 12) < 0.7 and (x % 50) < 10 + hr(i, 3) * 26:
        v -= 1.0                                                         # una rascada
    return v


def _dins_vidre(z, y):
    z0, z1, y0, y1 = GLASS
    return z0 + 4 < z < z1 - 4 and y0 + 4 < y < y1 - 4


def escena(cv, tex, estat=frozenset()):
    """Tota la sala, de lluny a prop. `estat`: 'soler', 'oberta', 'apagat'. → l'Escena (qui ha pintat què)."""
    e = Escena(cv, CAM, LLUMS, ambient=-0.3)
    zn = CAM.pos[2] + 60
    paret = tex['paret']
    gz0, gz1, gy0, gy1 = GLASS
    # ── a l'altra banda del vidre: la terminal ──
    tz0, tz1 = gz0 - 120, gz1 + 300
    e.quad('terminal', (TERM_X, 400, tz0), (TERM_X, 400, tz1), (TERM_X, TERM_Y, tz1), (TERM_X, TERM_Y, tz0),
           ramp=CONC, lvl=lambda s, t, P: 3.6 + (hr(int(s // 80), 1) - 0.5) * 0.3 - (0.6 if s % 80 < 1.5 else 0))
    vw = PL.GLASS[2] - PL.GLASS[0]
    vk = 1.8                                                              # la vista, gairebé el doble de gran
    vh = (VIEW_TOP - PL.GLASS[1]) * vk
    vz = (gz0 + gz1) / 2 + 230                                           # (el que es veu pel vidre, de biaix)
    e.quad('vista', (TERM_X + 1, TERM_Y + vh, vz - vw * vk / 2), (TERM_X + 1, TERM_Y + vh, vz + vw * vk / 2),
           (TERM_X + 1, TERM_Y, vz + vw * vk / 2), (TERM_X + 1, TERM_Y, vz - vw * vk / 2),
           tex=(tex['vista'], (PL.GLASS[0], PL.GLASS[1], PL.GLASS[2], VIEW_TOP)))

    def rajola(s, t, P):
        x, z = P[0], P[2]
        v = 4.2 + (fbm(x / 50, z / 50, 7) - 0.5) * 0.4 + (TERM_X - x) / -200 * 0.0
        if x % 48 < 1.2 or z % 48 < 1.2:
            v -= 0.9
        return v
    e.quad('terminal', (TERM_X, TERM_Y, tz1), (-1, TERM_Y, tz1), (-1, TERM_Y, tz0), (TERM_X, TERM_Y, tz0),
           ramp=TILE, lvl=rajola)
    # els seients blaus de la terminal, en fila, i en Soler
    for k in range(3):
        sz = vz - 150 + k * 92
        e.caixa('terminal', TERM_X + 70, TERM_X + 104, TERM_Y, TERM_Y + 18, sz, sz + 80, BLUE, 3.0,
                cares={'dalt': {'ramp': BLUE, 'lvl': lambda s, t, P: 3.6 - (1.0 if int(t) % 20 < 2 else 0)},
                       'dreta': {'ramp': BLUE, 'lvl': 2.6}})
        e.caixa('terminal', TERM_X + 96, TERM_X + 104, TERM_Y + 18, TERM_Y + 44, sz, sz + 80, BLUE, 2.4)
    if 'soler' in estat:
        sx, sz = SOLER
        e.sprite('soler', _soler(), (34, 111), (sx, TERM_Y, sz))
    # ── el sostre i les parets ──
    # (el sostre arriba fins a la càmera: si no, a dalt de la pantalla quedava una franja negra)
    zc = CAM.pos[2] + 4
    e.quad('sostre', (0, HW, zc), (XR, HW, zc), (XR, HW, ZW), (0, HW, ZW), ramp=CONC, lvl=2.6, dues_cares=True)
    # la paret del vidre (x = 0): de prop, bloc; cap a la cantonada, el dibuix pla (amb el forat del vidre)
    e.quad('paret_esq_prop', (0, HW, zn), (0, HW, ZW - XL), (0, 0, ZW - XL), (0, 0, zn), ramp=BLOCK, lvl=_bloc())
    e.quad('paret_esq', (0, HW, ZW - XL), (0, HW, ZW), (0, 0, ZW), (0, 0, ZW - XL), tex=(paret, (0, 0, XL, HW)))
    # el vidre: els reflexos del passadís, en diagonal, per damunt de la terminal
    e.claror((0.5, gy1 - 4, gz0 + 4), (0.5, gy1 - 4, gz1 - 4), (0.5, gy0 + 4, gz1 - 4), (0.5, gy0 + 4, gz0 + 4),
             (200, 230, 220), lambda s, t: 0.16 if (s + t * 0.9) % 70 < 8 else (0.10 if (s + t * 0.9) % 70 < 12 else 0.06))
    # la paret del fons (z = 300): el dibuix pla (x 250..640) i, a la dreta, més bloc
    if 'oberta' in estat:
        dx0, dx1, _, dy1 = DOOR_W
        # l'oficina, a l'altra banda de la porta: el dibuix pla de la porta oberta, una mica endins, i el seu terra
        e.quad('oficina', (dx0 - 90, dy1 + 20, ZW + 70), (dx1 + 10, dy1 + 20, ZW + 70), (dx1 + 10, 0, ZW + 70),
               (dx0 - 90, 0, ZW + 70), tex=(tex['oficina'], PL.DOOR_BOX))
        e.quad('oficina', (dx0 - 90, 0.2, ZW + 70), (dx1 + 10, 0.2, ZW + 70), (dx1 + 10, 0.2, ZW), (dx0 - 90, 0.2, ZW),
               ramp=TILE, lvl=lambda s, t, P: 3.4 - (0.8 if int(s) % 40 == 0 else 0))
        # la fulla, oberta cap endins (les frontisses, a la dreta)
        a = 1.15
        fx, fz = dx1 - (dx1 - dx0) * math.cos(a), ZW + (dx1 - dx0) * math.sin(a)
        e.quad('porta', (fx, dy1, fz), (dx1, dy1, ZW), (dx1, 0, ZW), (fx, 0, fz), ramp=DOOR,
               lvl=lambda s, t, P: 3.4 + s * 0.012 + (0.8 if abs(t - 70) < 2 else 0), dues_cares=True)
        e.claror((dx0, 0.3, ZW), (dx1, 0.3, ZW), (dx1 + 40, 0.3, ZW - 90), (dx0 - 30, 0.3, ZW - 90), (230, 240, 255),
                 lambda s, t: 0.22 * max(0.0, 1 - t / 90))
    e.quad('paret_fons', (0, HW, ZW), (W - XL, HW, ZW), (W - XL, 0, ZW), (0, 0, ZW), tex=(paret, (XL, 0, W, HW)))
    e.quad('paret_fons_dreta', (W - XL, HW, ZW), (XR, HW, ZW), (XR, 0, ZW), (W - XL, 0, ZW), ramp=BLOCK,
           lvl=_bloc(seed=5))
    # l'armari de la mànega d'incendis, a la paret de més enllà de les taquilles
    hx = W - XL + 40
    e.caixa('bie', hx, hx + 46, 70, 128, ZW - 10, ZW - 0.5, REDB, 2.6,
            cares={'davant': {'ramp': REDB, 'lvl': lambda s, t, P: 3.4 if s < 2 or t < 2 or s > 44 or t > 56 else
                              (1.4 if 6 < s < 40 and 6 < t < 46 and abs(math.hypot(s - 23, t - 26) - 13) < 3 else 2.4)}})
    e.caixa('bie', hx + 8, hx + 38, 132, 140, ZW - 1.5, ZW - 0.5, [(200, 200, 196), (240, 240, 236)], 1.4)
    # la canonada dels bombers i la safata de cables, a dalt, que continuen per la paret de prop i la de la dreta
    for pts in (((1.5, HW - 19.5, zn), (1.5, HW - 19.5, ZW - XL)), ((W - XL, HW - 19.5, ZW - 1.5), (XR, HW - 19.5, ZW - 1.5))):
        e.tub('canonada', *pts, 2.2, REDB, 2.6, brides=107, llum_dir=(0.2, -1.0))
    # la claror del fluorescent a la paret i el terra
    e.quad('terra', (0, 0, ZW), (XR, 0, ZW), (XR, 0, zn), (0, 0, zn), ramp=LINO, lvl=_lino)
    lx, ly, lz = LAMP
    if 'apagat' not in estat:
        e.claror((lx - 200, 0.3, lz + 200), (lx + 200, 0.3, lz + 200), (lx + 200, 0.3, lz - 200), (lx - 200, 0.3, lz - 200),
                 (220, 236, 255), lambda s, t: 0.10 * max(0.0, 1 - math.hypot(s - 200, t - 200) / 200))
    # la claror de la terminal, que entra pel vidre i s'estira pel terra
    e.claror((0, 0.4, gz1), (200, 0.4, gz1 + 60), (200, 0.4, gz0 - 40), (0, 0.4, gz0), (190, 200, 230),
             lambda s, t: 0.12 * max(0.0, 1 - s / 200) * min(1.0, t / 30, (gz1 - gz0 - t) / 30 + 1))
    # la foscor dels racons
    e.foscor('racons', (0, 0.5, ZW), (XR, 0.5, ZW), (XR, 0.5, zn), (0, 0.5, zn),
             lambda s, t: max(0.55 * max(0.0, 1 - t / 26), 0.45 * max(0.0, 1 - s / 22)))
    e.foscor('cantonada', (0, HW, ZW - 0.5), (60, HW, ZW - 0.5), (60, 0, ZW - 0.5), (0, 0, ZW - 0.5),
             lambda s, t: 0.5 * max(0.0, 1 - s / 60))
    e.foscor('cantonada2', (0.5, HW, ZW - 60), (0.5, HW, ZW), (0.5, 0, ZW), (0.5, 0, ZW - 60),
             lambda s, t: 0.5 * max(0.0, 1 - (60 - s) / 60))
    # les taquilles, contra la paret del fons
    tx0 = _w(LOCK_BOX[0])
    tx1 = _w(LOCK_BOX[2])
    th = LOCK_BOX[3] - LOCK_BOX[1]
    e.foscor('ombra_taquilles', (tx0 - 14, 0.6, ZW), (tx1 + 4, 0.6, ZW), (tx1 + 4, 0.6, ZW - LOCK_D - 16),
             (tx0 - 14, 0.6, ZW - LOCK_D - 16), lambda s, t: 0.55 * min(1.0, max(0.0, (LOCK_D + 16 - t) / 16)))
    e.caixa('taquilles', tx0, tx1, 0, th, ZW - 1 - LOCK_D, ZW - 1, [(20, 30, 40), (34, 50, 64), (52, 74, 92),
                                                                  (74, 100, 120), (100, 128, 150), (140, 166, 184)], 2.4,
            cares={'davant': {'tex': (tex['taquilles'], LOCK_BOX)},
                   'dalt': {'ramp': CONC, 'lvl': lambda s, t, P: 2.8 + (fbm(s / 10, t / 8, 3) - 0.5) * 0.8},
                   'esquerra': {'ramp': [(20, 30, 40), (34, 50, 64), (52, 74, 92), (74, 100, 120)],
                                'lvl': lambda s, t, P: 2.0 - (0.6 if int(t) % 30 == 0 else 0)}})
    # el senyal de terra mullat, amb el bassal (el reflex del fluorescent)
    cx, cz = CONE
    e.claror((cx - 50, 0.5, cz + 22), (cx + 40, 0.5, cz + 22), (cx + 40, 0.5, cz - 22), (cx - 50, 0.5, cz - 22),
             (150, 170, 190), lambda s, t: 0.16 if ((s - 50) / 44) ** 2 + ((t - 22) / 20) ** 2 < 1 else 0)
    e.claror((cx - 30, 0.6, cz + 6), (cx - 6, 0.6, cz + 6), (cx - 6, 0.6, cz - 2), (cx - 30, 0.6, cz - 2),
             (200, 220, 240), lambda s, t: 0.35 if abs(t - 4) < 2 else 0)
    e.foscor('ombra_con', (cx - 14, 0.7, cz + 10), (cx + 14, 0.7, cz + 10), (cx + 14, 0.7, cz - 10), (cx - 14, 0.7, cz - 10),
             lambda s, t: 0.5 * max(0.0, 1 - ((s - 14) / 14) ** 2 - ((t - 10) / 10) ** 2) * 1.5)
    e.sprite('con', tex['con'].crop(CONE_BOX), (PL_CONE_X - CONE_BOX[0], 249 - CONE_BOX[1]), (cx, 0, cz))
    # el carro de la neteja, girat: dos prestatges, les potes, les rodes, la galleda, la bossa, els esprais i la fregona
    rx, rz, rw, rd, ra = TROL
    c_, s_ = math.cos(ra), math.sin(ra)

    def R(lx, y, lz):
        return (rx + lx * c_ - lz * s_, y, rz + lx * s_ + lz * c_)
    e.foscor('ombra_carro', R(-rw / 2 - 10, 0.6, rd / 2 + 8), R(rw / 2 + 6, 0.6, rd / 2 + 8), R(rw / 2 + 6, 0.6, -rd / 2 - 12),
             R(-rw / 2 - 10, 0.6, -rd / 2 - 12),
             lambda s, t: 0.55 * max(0.0, 1 - ((s - rw / 2 - 8) / (rw / 2 + 8)) ** 2 - ((t - rd / 2 - 10) / (rd / 2 + 10)) ** 2) * 1.6)
    for qx in (-rw / 2 + 3, rw / 2 - 3):
        for qz in (-rd / 2 + 3, rd / 2 - 3):
            e.caixa_girada('carro', *R(qx, 0, qz)[::2], 4, 4, 4, ra, SLATE, 1.6)                        # les rodes
            e.caixa_girada('carro', *R(qx, 0, qz)[::2], 2, 2, 44, ra, CHROME, 3.0, y0=4)               # les potes
    e.caixa_girada('carro', rx, rz, rw, rd, 3, ra, TROLLEY, 2.6, y0=14)                                 # a baix
    e.caixa_girada('carro', *R(rw / 2 - 16, 0, 0)[::2], 22, 22, 20, ra, TROLLEY, 2.6, y0=17,
                   cares={'dalt': {'ramp': [(30, 36, 50), (60, 70, 90), (110, 120, 140)], 'lvl': 1.2}})   # la galleda
    e.caixa_girada('carro', rx, rz, rw, rd, 5, ra, TROLLEY, 3.0, y0=44,
                   cares={'dalt': {'ramp': TROLLEY, 'lvl': 3.6}, 'davant': {'ramp': TROLLEY, 'lvl': 2.6}})   # a dalt
    e.sprite('carro', tex['carro'].crop(SPRAY_BOX), (0, SPRAY_BOX[3] - SPRAY_BOX[1] - 1), R(-4, 49, 4))
    e.cable('carro', [R(rw / 2 - 12, 34, 2), R(rw / 2 - 6, 70, 6), R(rw / 2 - 1, 92, 10)], CARD, 3.0, gruix=2.0)  # la fregona
    e.sprite('carro', tex['carro'].crop(BAG_BOX), (18, 0), R(-rw / 2 - 2, 48, -rd / 2))               # la bossa
    # el fluorescent que penja del sostre
    on = [(200, 214, 228), (232, 244, 255), (250, 252, 255)]
    off = [(70, 76, 86), (100, 108, 118), (120, 130, 140)]
    tub = {'ramp': off if 'apagat' in estat else on, 'lvl': lambda s, t, P: 1.6 if 1.5 < t < 6 else 0.4}
    e.caixa('fluorescent', lx - 60, lx + 60, ly - 5, ly + 3, lz - 6, lz + 6, CHROME, 2.0,
            cares={'sota': tub, 'davant': tub, 'dalt': {'ramp': CHROME, 'lvl': 1.4}})
    for xx in (lx - 50, lx + 50):
        e.cable('fluorescent', [(xx, HW, lz), (xx, ly + 2, lz)], CHROME, 2.0, gruix=0.8)
    # primer pla: una canonada vertical a la dreta i una d'horitzontal a dalt, i una paperera i caixes a l'esquerra
    FOSC = [(3, 5, 5), (7, 10, 10), (12, 17, 16), (18, 25, 23), (26, 34, 31), (36, 45, 41)]
    e.tub('primer_pla', (486, 0, 22), (486, HW, 22), 7, FOSC, 1.8, brides=60)
    e.tub('primer_pla', (-10, HW - 4, 6), (520, HW - 4, 6), 6, FOSC, 1.6, brides=90, llum_dir=(0.0, -1.0))
    for cx_, cz_, w, d, h, a, y0 in ((-6, 60, 64, 52, 40, 0.3, 0), (-4, 64, 46, 38, 30, 0.1, 40)):
        e.caixa_girada('primer_pla', cx_, cz_, w, d, h, a, FOSC, 1.6, y0=y0,
                       cares={'dalt': {'ramp': FOSC, 'lvl': lambda s, t, P: 3.0 - (1.2 if abs(s - 24) < 2 else 0)},
                              'davant': {'ramp': FOSC, 'lvl': 1.2}, 'dreta': {'ramp': FOSC, 'lvl': 2.0}})
    e.caixa_girada('primer_pla', 74, 14, 30, 30, 40, -0.2, FOSC, 1.4,
                   cares={'dalt': {'ramp': FOSC, 'lvl': lambda s, t, P: 0.6 if 3 < s < 27 and 3 < t < 27 else 2.6},
                          'davant': {'ramp': FOSC, 'lvl': lambda s, t, P: 1.4 + (0.6 if int(s) % 5 == 0 else 0)}})
    return e


PL_CONE_X = 139


# ─── Composició ─────────────────────────────────────────────────────────────

def _render(estat=frozenset(), tex=None):
    cv = Canvas(light=LIGHT)
    e = escena(cv, tex or _textures(), estat)
    cv.rect(0, BOTTOM + 1, W - 1, H - 1, [(0, 0, 0)], 0, lit=0)    # la barra de verbs: negre
    return cv.img, e


@functools.lru_cache(maxsize=None)
def _base():
    return _render()


def bg(cv):
    cv.img.paste(_base()[0])
    cv.P = cv.img.load()


def _decorat(*estat, **kw):
    """Un decorat: la sala amb aquell estat (i el dibuix pla canviat), menys la de sempre (només el que canvia)."""
    def draw(cv):
        img, _ = _render(frozenset(estat), _textures(**kw))
        cv.img.alpha_composite(_diff(img, _base()[0]))
        cv.P = cv.img.load()
    return draw


PROPS = {
    'soler_vidre': _decorat('soler'),
    'porta_oberta': _decorat('oberta', oberta=True),
    'alarma': _decorat(led='alarma'),
}


# ─── Animacions ─────────────────────────────────────────────────────────────

def _fotograma(capes):
    """El fons amb unes capes damunt, menys el fons."""
    img, _ = _base()
    img = img.copy()
    for c in capes:
        img.alpha_composite(c)
    return _diff(img, _base()[0])


@functools.lru_cache(maxsize=None)
def _apagat():
    """El fluorescent apagat: el tub fosc i, al voltant, la sala una mica més fosca (només a prop del llum)."""
    import numpy as np
    on = np.asarray(_base()[0]).astype(float)
    off = np.asarray(_render(frozenset({'apagat'}))[0]).astype(float)
    u, v, _ = CAM.projecta(LAMP)
    yy, xx = np.mgrid[0:H, 0:W]
    k = np.clip(1 - np.hypot((xx - u) / 260, (yy - v) / 200), 0, 1)[..., None] * 0.35
    dark = on * (1 - k)
    _, e = _base()
    lamp = np.array([e.ids[i] == 'fluorescent' for i in e.amo], bool).reshape(H, W)
    dark[lamp] = off[lamp]
    return Image.fromarray(dark.astype('uint8'), 'RGBA')


def _frames():
    """El fluorescent parpelleja: apagat (5, 7, 12) i mig encès, només els extrems (6, 13)."""
    import numpy as np
    base = _base()[0]
    off = _apagat()
    full = _diff(off, base)
    # mig encès: els extrems del tub encara fan llum
    half = np.asarray(off).copy()
    on = np.asarray(base)
    _, e = _base()
    u0 = CAM.projecta((LAMP[0] - 60, LAMP[1], LAMP[2]))[0]
    u1 = CAM.projecta((LAMP[0] + 60, LAMP[1], LAMP[2]))[0]
    lamp = np.array([e.ids[i] == 'fluorescent' for i in e.amo], bool).reshape(H, W)
    xx = np.mgrid[0:H, 0:W][1]
    ends = lamp & ((xx < u0 + (u1 - u0) * 0.08) | (xx > u1 - (u1 - u0) * 0.08))
    half[ends] = on[ends]
    mig = _diff(Image.fromarray(half, 'RGBA'), base)
    buit = _diff(base, base)
    return [full if i in (5, 7, 12) else mig if i in (6, 13) else buit for i in range(16)]


def _frames_avio():
    """Per la vidriera del fons de la terminal, un avió que s'acosta de cara: el far fix i el llum vermell que
    parpelleja."""
    _, e = _base()
    base = _vista()
    return [_fotograma([e.capa(_diff(_vista(avio=i), base), {'vista'})]) for i in range(10)]


ANIMS = {'fluorescent': {'frames': _frames, 'frameDuration': 120},
         'avio': {'frames': _frames_avio, 'frameDuration': 140}}


# ─── Capes del davant ───────────────────────────────────────────────────────

def _amo(ids):
    def mask(x, y):
        _, e = _base()
        return e.ids[e.amo[y * e.cv.w + x]] in ids
    return mask


def _p(x, z, y=0.0):
    u, v, _ = CAM.projecta((x, y, z))
    return round(u), round(v)


# El primer pla (sempre davant), el carro i el senyal de terra mullat (qui hi passa per darrere, hi queda darrere).
FRONT = [
    {'id': 'davant', 'mask': _amo({'primer_pla'}), 'baseline': 999, 'zIndex': 20},
    {'id': 'davant_carro', 'mask': _amo({'carro'}), 'baseline': _p(TROL[0], TROL[1] - 12)[1], 'zIndex': 20},
    {'id': 'davant_con', 'mask': _amo({'con'}), 'baseline': _p(CONE[0], CONE[1] - 4)[1], 'zIndex': 20},
]


# ─── Geometria (coordenades de sala, projectades) ────────────────────────────

def _rect_mon(*Ps):
    pts = [CAM.projecta(P) for P in Ps]
    return (max(0, round(min(p[0] for p in pts))), max(0, round(min(p[1] for p in pts))),
            min(W - 1, round(max(p[0] for p in pts))), min(BOTTOM, round(max(p[1] for p in pts))))


def _escala_a(v):
    """L'escala d'un personatge amb els peus a la y de pantalla `v` (al terra, la profunditat només depèn de v)."""
    lo, hi = 1.0, 2000.0
    for _ in range(60):
        z = (lo + hi) / 2
        if CAM.projecta((260, 0, z))[1] > v:
            lo = z
        else:
            hi = z
    return CAM.escala((260, 0, (lo + hi) / 2))


# El terra on es camina (al món): tot el passadís, menys el carro i les taquilles, i sense acostar-se tant a la càmera
# que el personatge passi d'≈1,2.
WALK_MON = [(20, 278), (420, 280), (420, 252), (470, 250), (480, 130), (330, 92), (190, 100), (90, 124), (20, 150)]
_WALK = [_p(x, z) for x, z in WALK_MON]
_V_FONS, _V_PROP = min(v for _, v in _WALK), max(v for _, v in _WALK)

_DX = (DOOR_W[0] + DOOR_W[1]) / 2
GEOMETRIA = {
    'things': {
        'teclat': {'rect': _rect_mon((KEYPAD[0] - 2, KEYPAD[3] + 2, ZW), (KEYPAD[1] + 2, KEYPAD[2] - 2, ZW)),
                   'walk': _p((KEYPAD[0] + KEYPAD[1]) / 2, 262)},
        'porta': {'rect': _rect_mon((DOOR_W[0] - 4, DOOR_W[3] + 5, ZW), (DOOR_W[1] + 4, 0, ZW)),
                  'walk': _p(_DX, 270)},
    },
    'spawns': {'iri': _p(160, 150)},
    'walkable': _WALK,
    'forats': [],
    'floorSquash': 0.42,                           # (la càmera, picada: el terra es veu aixafat)
    # L'ombra de contacte: la llum dominant és el fluorescent que penja; curta, cap a fora del llum.
    'characterShadow': {'enabled': True, 'color': '#081010', 'alpha': 0.42, 'squash': 0.4, 'core': 0.6,
                        'light': {'x': _p(LAMP[0], LAMP[2])[0], 'y': _p(LAMP[0], LAMP[2])[1], 'stretch': 0.6,
                                  'reach': 170}},
    'regions': [{'id': 'perspectiva', 'active': True, 'scaleEnabled': True, 'scaleWalkSpeed': True,
                 'scaleTop': round(_escala_a(_V_FONS - 2), 3), 'scaleBottom': round(_escala_a(_V_PROP + 2), 3),
                 'points': [(0, _V_FONS - 2), (W - 1, _V_FONS - 2), (W - 1, _V_PROP + 2), (0, _V_PROP + 2)]}],
    # la llum de la sala sobre els personatges, en temps d'execució
    'characterLights': {
        'ambient': '#a4b0aa',                                                           # verd d'hospital, fred
        'lights': [
            {'x': _p(LAMP[0], LAMP[2], LAMP[1])[0], 'y': _p(LAMP[0], LAMP[2], LAMP[1])[1], 'radius': 300,
             'color': '#e6f0ff', 'intensity': 0.7},                                     # el fluorescent
            {'x': _p(0, (GLASS[0] + GLASS[1]) / 2, 100)[0], 'y': _p(0, (GLASS[0] + GLASS[1]) / 2, 100)[1],
             'radius': 220, 'color': '#c8c8f0', 'intensity': 0.5},                      # la terminal pel vidre
            {'x': _p(KEYPAD[0] + 16, ZW, 70)[0], 'y': _p(KEYPAD[0] + 16, ZW, 70)[1], 'radius': 60,
             'color': '#ff4a3a', 'intensity': 1.0, 'whenPropVisible': 'alarma'},       # l'alarma del teclat
        ],
    },
}
