"""
L'oficina de facturació de l'aeroport (Escena 3, l'Iri, a dins de la porta de personal). EN 3D (hd640/tres_d.py),
a 1×.

Una càmera alta que mira de biaix la cantonada del fons a la dreta (l'estudi de l'Iri, al revés):
  - a la paret del fons, el **rellotge** de les sis menys vint, el **pòster** de la companyia i, arran de la
    cantonada, la **finestra** amb la persiana: l'alba hi entra en ratlles que baixen en diagonal per la moqueta;
  - a la paret de la dreta, en escorç, la **porta** de sortida (al passadís de servei), amb el rètol verd;
  - el **taulell** de facturació, separat de la paret i girat, amb volum: el **terminal** de fòsfor verd (una caixa,
    amb el pòsit), la **impressora** làser, el telèfon, el tampó, la tassa i el **ventilador**; la torre a terra i
    la cadira de rodes al davant (s'hi passa per darrere);
  - els tres **arxivadors** grisos contra la paret del fons, amb les carpetes i la planta morta a sobre;
  - primer pla: la font d'aigua en silueta a l'esquerra, caixes d'arxiu a baix a la dreta i un fluorescent que penja.

Tot el detall ve del dibuix pla de sempre (aeroport_oficina_pla_comu.py), projectat. Els decorats (la llista, la
impressora que imprimeix, les acreditacions) tornen a pintar la sala amb el dibuix pla canviat, i en surt la
diferència; les animacions (el ventilador, la persiana i el rellotge) es projecten per la mateixa superfície.

El món: x a la dreta (600 = la paret de la porta), y amunt (0 = el terra), z cap al fons (300 = la paret del fons);
1 unitat = 1 píxel de sala a la distància on un personatge fa ≈111 px (escala 1).
"""
import functools
import math

import hd640  # noqa: F401  (abans de cap hd.rooms: posa la llibreria a 640×360)
from hd.pix import Canvas, Light, W, H, hr
from hd.rooms.comu import _diff, SHEET, PLASTIC
from hd.rooms.exterior import fbm
from hd640.rooms import aeroport_oficina_pla_comu as PL
from hd640.rooms.aeroport_oficina_pla_comu import (PANEL, CARPET, BEIGE, CABINET, CHROME, BLUE, SLATE, DOOR, YELS,
                                                   REDB)
from hd640.tres_d import Camera, Escena, Llum

BOTTOM = 259                                       # la sala acaba aquí (a sota, la barra de verbs)
ZW = 300                                           # la paret del fons
HW = 200                                           # l'alçada de les parets (el dibuix pla fa 200 fins al terra)
XR = 600                                           # la paret de la dreta (la de la porta)
XC = 525                                           # al dibuix pla, la cantonada: a la dreta, la paret de la porta
XL = -260                                          # on s'acaba la paret del fons a l'esquerra (fora de la pantalla)
DESK = (338, 196, 300, 66, 46, 0.24)               # el taulell: x i z del centre, ample, fons, alçada, gir
CAB = (96, 186, 40)                                # els arxivadors: x0, x1, fons (contra la paret del fons)
CHAIR = (270, 128)                                 # els peus de la cadira (x, z)
TOWER = (166, 150)                                 # la torre, a terra a l'esquerra del taulell (x, z)
MK = 1.15                                          # el monitor, una mica més gros que al dibuix pla (es llegeix)


def _w(fx):
    """Una x del dibuix pla de la paret del fons → la x del món."""
    return fx - XC + XR


def _wz(fx):
    """Una x del dibuix pla de la paret de la porta → la z del món."""
    return ZW - (fx - XC)


def _y(fy):
    """Una y del dibuix pla (el terra, a 200) → l'alçada del món."""
    return HW - fy


WIN = (_w(PL.WINDOW[0]), _w(PL.WINDOW[2]), _y(PL.WINDOW[3]), _y(PL.WINDOW[1]))      # x0, x1, y0, y1
DOOR_W = (_wz(600), _wz(533), 0, _y(67))                                           # z0, z1, y0, y1 (la fulla)
CLOCK_W = (_w(PL.CLOCK[0]), _y(PL.CLOCK[1]))

CAM = Camera(pos=(XR - 420, 190, -260), yaw=0.36, pitch=0.16, f=440, centre=(320, 90))

LIGHT = Light(ambient=0.0, vignette=None, floor_fade=None)  # (la llum és la del món: la de l'Escena)
TEX_LIGHT = Light(ambient=-0.1, vignette=None, floor_fade=None)   # el dibuix pla de les textures, sense vinyeta
TEX_LIGHT.point(480, 70, r=110, k=0.7, squash=1.2, power=2.0)      # l'alba, a la paret de la finestra

LLUMS = [Llum((250, 196, 150), 330, 1.5, power=1.3),               # els fluorescents
         Llum((470, 196, 200), 300, 1.3, power=1.3),
         Llum(((WIN[0] + WIN[1]) / 2, 130, ZW - 8), 260, 1.3, power=1.5),   # l'alba per la finestra
         Llum((300, 70, 150), 60, 0.5, power=2.0)]                 # la pantalla del terminal


# ─── Les textures: el dibuix pla de sempre ───────────────────────────────────

def _paret(sway=0.0, segons=None):
    """Les dues parets planes, de cara: el plafó, el rellotge, el pòster, la finestra i la porta."""
    cv = Canvas(light=TEX_LIGHT)
    PL.wall(cv)
    PL.window(cv, sway)
    PL.clock(cv)
    PL.poster(cv)
    PL.door(cv)
    if segons is not None:
        cx, cy = PL.CLOCK
        a = segons / 60 * 2 * math.pi
        cv.line(cx - round(math.sin(a) * 3), cy + round(math.cos(a) * 3), cx + round(math.sin(a) * 11),
                cy - round(math.cos(a) * 11), [(190, 36, 36)], 0, lit=0)
        cv.flat(cx, cy, (200, 40, 40))
    return cv.img


def _peces(llista=False, impressora='parada', fan=0):
    """Els mobles i les coses del taulell, plans sobre transparent, cadascun al seu llenç (se'n treuen retalls)."""
    out = {}
    for nom, fn in (('taulell', PL.desk), ('terminal', lambda cv: PL.terminal(cv, llista)),
                    ('impressora', lambda cv: PL.printer(cv, impressora)), ('coses', PL.desk_things),
                    ('cadira', PL.chair), ('arxivadors', PL.cabinets)):
        cv = Canvas(light=TEX_LIGHT, transparent=True)
        fn(cv)
        out[nom] = cv.img
    cv = Canvas(light=TEX_LIGHT, transparent=True)          # el ventilador, amb les aspes del fotograma
    fx, fy = PL.FAN
    t = PL.DESK_TOP - 4
    cv.rect(fx - 1, fy + 8, fx, t, CHROME, 3.0)
    PL.fan_blades(cv, fan)
    cv.disc(fx, t, 7, 1.6, CHROME, 2.6)
    out['ventilador'] = cv.img
    return out


DESK_BOX = (117, 163, 444, 209)                    # el davant del taulell, al dibuix pla
MON_BOX = (157, 112, 244, 157)                     # el monitor (sense el peu)
POSIT_BOX = (240, 114, 255, 130)
PRINT_BOX = (341, 131, 409, 161)                   # el davant de la impressora
PHONE_BOX = (254, 135, 336, 171)                   # el telèfon, el tampó i les etiquetes
MUG_BOX = (414, 149, 431, 160)
FAN_BOX = (422, 123, 449, 162)
CHAIR_BOX = (272, 147, 331, 226)
TOWER_BOX = (128, 171, 150, 206)
CAB_BOX = (27, 93, 115, 201)                       # els tres arxivadors, de cara
CAB_TOP = (28, 60, 112, 94)                        # les carpetes i la planta, a sobre


@functools.lru_cache(maxsize=None)
def _textures(llista=False, impressora='parada'):
    return {'paret': _paret(), **_peces(llista, impressora)}


# ─── Les superfícies ────────────────────────────────────────────────────────

def _plafo(seed=3):
    """El plafó de melamina beix en coordenades del món (s, t des del cantó de dalt): on el dibuix pla no arriba."""
    def L(s, t, P):
        if s % 64 < 1:
            return 2.4
        v = 4.2 + (hr(int(s // 64), seed) - 0.5) * 0.4 + (hr(int(s // 2), int(t // 2), 6) - 0.5) * 0.25
        if t < 8:
            v = 5.4 - t * 0.15                                       # el fals sostre
        elif t > HW - 5:
            return 1.6 if t > HW - 4 else 2.6                        # el sòcol de goma
        return v
    return L


def _moqueta(s, t, P):
    """La moqueta blava de lloses, en coordenades del món: el gra i les juntes (més fins al fons) i el camí gastat de
    la porta."""
    x, z = P[0], P[2]
    v = 3.0 + (fbm(x / 26, z / 18, 5) - 0.5) * 0.6 + (hr(int(x / 3), int(z / 3), 2) - 0.5) * 0.35
    if x % 50 < 0.8 or z % 50 < 0.8:
        v -= 0.6                                                                  # les juntes de les lloses
    elif int(x // 50 + z // 50) % 2:
        v += 0.25                                                                 # (el pèl, a l'altra banda)
    v += max(0.0, 1 - math.hypot((x - 500) / 60, (z - 200) / 70)) * 0.7      # el camí de la porta
    v += max(0.0, 1 - math.hypot((x - CHAIR[0]) / 40, (z - CHAIR[1]) / 30)) * 0.8   # sota la cadira
    return v


def _llum_alba(x, z):
    """Quanta alba (0..1) arriba a un punt del terra: la línia que puja cap a la finestra (cap al fons, a la dreta i
    amunt); les lamel·les de la persiana la tallen en ratlles."""
    t = (ZW - z) / 1.0
    xw, yw = x + 0.42 * t, 0.62 * t
    x0, x1, y0, y1 = WIN
    if not (x0 + 2 < xw < x1 - 2 and y0 + 2 < yw < y1 - 2):
        return 0.0
    fy = HW - yw                                       # la y del dibuix pla, a la finestra
    if (fy - PL.WINDOW[1]) % 7 < 4:
        return 0.0                                     # una lamel·la
    if abs(xw - _w(460)) < 1.5 or abs(xw - _w(497)) < 1.5:
        return 0.0                                     # els cordons
    return 0.34 * min(1.0, (xw - x0) / 20, (x1 - xw) / 20)


def _D(lx, y, lz):
    """Un punt del taulell (x, z des del centre, sense girar) → el món."""
    cx, cz, _, _, _, a = DESK
    return (cx + lx * math.cos(a) - lz * math.sin(a), y, cz + lx * math.sin(a) + lz * math.cos(a))


def escena(cv, tex, estat=frozenset()):
    """Tota la sala, de lluny a prop. → l'Escena (qui ha pintat què)."""
    e = Escena(cv, CAM, LLUMS, ambient=-0.15)
    zn = CAM.pos[2] + 60
    paret = tex['paret']
    # el sostre
    e.quad('sostre', (XL, HW, ZW), (XR, HW, ZW), (XR, HW, zn), (XL, HW, zn), ramp=PANEL, lvl=3.0, dues_cares=True)
    # la paret del fons: el dibuix pla fins a la cantonada; a l'esquerra, plafó
    x0w = _w(0)
    e.quad('paret_fons_esq', (XL, HW, ZW), (x0w, HW, ZW), (x0w, 0, ZW), (XL, 0, ZW), ramp=PANEL, lvl=_plafo())
    e.quad('paret_fons', (x0w, HW, ZW), (XR, HW, ZW), (XR, 0, ZW), (x0w, 0, ZW), tex=(paret, (0, 0, XC, HW)))
    # la paret de la porta (x = 600): el dibuix pla des de la cantonada; de prop, plafó
    zp = _wz(W)
    e.quad('paret_dreta', (XR, HW, ZW), (XR, HW, zp), (XR, 0, zp), (XR, 0, ZW), tex=(paret, (XC, 0, W, HW)))
    e.quad('paret_dreta_prop', (XR, HW, zp), (XR, HW, zn), (XR, 0, zn), (XR, 0, zp), ramp=PANEL, lvl=_plafo(5))
    # el terra, la llum dels fluorescents i l'alba en ratlles
    e.quad('terra', (XL, 0, ZW), (XR, 0, ZW), (XR, 0, zn), (XL, 0, zn), ramp=CARPET, lvl=_moqueta)
    e.claror((150, 0.3, ZW), (560, 0.3, ZW), (560, 0.3, 40), (150, 0.3, 40), (200, 220, 255),
             lambda s, t: 0.10 * max(0.0, 1 - math.hypot(s - 200, (t - 110) * 1.3) / 230))
    e.claror((300, 0.4, ZW), (XR, 0.4, ZW), (XR, 0.4, -60), (300, 0.4, -60), (255, 190, 150),
             lambda s, t: _llum_alba(300 + s, ZW - t))
    # la foscor dels racons i del sostre
    e.foscor('racons', (XL, 0.5, ZW), (XR, 0.5, ZW), (XR, 0.5, zn), (XL, 0.5, zn),
             lambda s, t: max(0.5 * max(0.0, 1 - t / 26), 0.45 * max(0.0, 1 - (XR - XL - s) / 24)))
    e.foscor('cantonada', (XR - 50, HW, ZW - 0.5), (XR, HW, ZW - 0.5), (XR, 0, ZW - 0.5), (XR - 50, 0, ZW - 0.5),
             lambda s, t: 0.4 * max(0.0, 1 - (50 - s) / 50))
    e.foscor('cantonada2', (XR - 0.5, HW, ZW), (XR - 0.5, HW, ZW - 50), (XR - 0.5, 0, ZW - 50), (XR - 0.5, 0, ZW),
             lambda s, t: 0.4 * max(0.0, 1 - s / 50))
    # els arxivadors, contra la paret del fons, amb les carpetes i la planta morta a sobre
    ax0, ax1, ad = CAB
    ah = CAB_BOX[3] - CAB_BOX[1]
    e.foscor('ombra_arxivadors', (ax0 - 6, 0.6, ZW), (ax1 + 14, 0.6, ZW), (ax1 + 14, 0.6, ZW - ad - 18),
             (ax0 - 6, 0.6, ZW - ad - 18), lambda s, t: 0.55 * min(1.0, max(0.0, (ad + 18 - t) / 16)))
    e.caixa('arxivadors', ax0, ax1, 0, ah, ZW - 1 - ad, ZW - 1, CABINET, 2.4,
            cares={'davant': {'tex': (tex['arxivadors'], CAB_BOX)}, 'dalt': {'ramp': CABINET, 'lvl': 3.6},
                   'dreta': {'ramp': CABINET, 'lvl': lambda s, t, P: 2.0 - (0.8 if int(t) % 25 == 0 else 0)}})
    e.sprite('arxivadors', tex['arxivadors'].crop(CAB_TOP), (0, CAB_TOP[3] - CAB_TOP[1] - 1),
             (ax0 + 1, ah, ZW - 1 - ad + 10))
    # el cable de la torre i el de la impressora, per la moqueta
    e.cable('cables', [(TOWER[0] + 4, 0.8, TOWER[1] + 8), (TOWER[0] - 10, 0.8, TOWER[1] + 40), (150, 0.8, 270),
                       (130, 0.8, ZW - 2)], SLATE, 2.6, gruix=1.8)
    # el taulell, girat: el davant (el dibuix pla), la tapa i el costat
    cx, cz, dw, dd, dh, da = DESK
    sh = [_D(-dw / 2 - 8, 0.6, dd / 2 + 6), _D(dw / 2 + 14, 0.6, dd / 2 + 6), _D(dw / 2 + 14, 0.6, -dd / 2 - 18),
          _D(-dw / 2 - 8, 0.6, -dd / 2 - 18)]
    e.foscor('ombra_taulell', *sh, lambda s, t: 0.55 * min(1.0, max(0.0, (dd + 24 - t) / 14)) * min(1.0, s / 10))
    tt = tex['taulell']
    e.caixa_girada('taulell', cx, cz, dw, dd, dh, da, CABINET, 2.0,
                   cares={'davant': {'tex': (tt, DESK_BOX)},
                          'dalt': {'ramp': BEIGE, 'lvl': lambda s, t, P: 4.0 + (hr(int(s // 3), int(t), 22) - 0.5) * 0.2
                                   - (0.8 if t > dd - 2 else 0)},
                          'esquerra': {'ramp': CABINET, 'lvl': lambda s, t, P: 1.6 if t > 6 else 3.0},
                          'dreta': {'ramp': CABINET, 'lvl': lambda s, t, P: 1.4 if t > 6 else 2.8}})
    # la torre, a terra a l'esquerra del taulell
    tx, tz = TOWER
    e.foscor('ombra_torre', (tx - 14, 0.7, tz + 26), (tx + 18, 0.7, tz + 26), (tx + 18, 0.7, tz - 6),
             (tx - 14, 0.7, tz - 6), lambda s, t: 0.5 * max(0.0, 1 - ((s - 16) / 16) ** 2 - ((t - 16) / 16) ** 2) * 1.5)
    e.caixa_girada('torre', tx, tz, TOWER_BOX[2] - TOWER_BOX[0], 40, TOWER_BOX[3] - TOWER_BOX[1], da, BEIGE, 2.4,
                   cares={'davant': {'tex': (tex['terminal'], TOWER_BOX)}, 'dalt': {'ramp': BEIGE, 'lvl': 3.8},
                          'esquerra': {'ramp': BEIGE, 'lvl': 2.6}})
    # damunt el taulell: el terminal (una caixa: el davant és el monitor del dibuix pla), el teclat, el telèfon,
    # el tampó, la tassa, el ventilador i la impressora
    mw, mh = (MON_BOX[2] - MON_BOX[0]) * MK, (MON_BOX[3] - MON_BOX[1]) * MK
    mx, mz = -dw / 2 + 74, 6
    e.caixa_girada('terminal', *_D(mx, 0, mz + 8)[::2], 30, 26, 4, da, BEIGE, 3.0, y0=dh)          # el peu
    e.caixa_girada('terminal', *_D(mx, 0, mz + 22)[::2], mw - 20, 28, mh - 10, da, BEIGE, 2.4, y0=dh + 6,
                   cares={'dalt': {'ramp': BEIGE, 'lvl': 3.6}})                                    # el cul del tub
    e.caixa_girada('terminal', *_D(mx, 0, mz)[::2], mw, 18, mh, da, BEIGE, 2.8, y0=dh + 4,
                   cares={'davant': {'tex': (tex['terminal'], MON_BOX)}, 'dalt': {'ramp': BEIGE, 'lvl': 4.2},
                          'esquerra': {'ramp': BEIGE, 'lvl': 3.0}})
    # el pòsit, enganxat al cantó del marc
    pw = (POSIT_BOX[2] - POSIT_BOX[0]) * MK
    ph = (POSIT_BOX[3] - POSIT_BOX[1]) * MK
    py = dh + 4 + mh - (POSIT_BOX[1] - MON_BOX[1]) * MK
    e.quad('terminal', _D(mx + mw / 2 - 4, py, mz - 9.6), _D(mx + mw / 2 - 4 + pw, py, mz - 9.6),
           _D(mx + mw / 2 - 4 + pw, py - ph, mz - 9.6), _D(mx + mw / 2 - 4, py - ph, mz - 9.6),
           tex=(tex['terminal'], POSIT_BOX))
    e.caixa_girada('teclat', *_D(mx, 0, -22)[::2], 92, 18, 3, da, BEIGE, 3.0, y0=dh,
                   cares={'dalt': {'ramp': BEIGE, 'lvl': lambda s, t, P: 2.4 if int(s) % 4 == 0 or int(t) % 4 == 0 else 3.8}})
    e.sprite('coses', tex['coses'].crop(PHONE_BOX), (14, PL.DESK_TOP - 4 - PHONE_BOX[1]), _D(-dw / 2 + 168, dh, -6))
    e.sprite('coses', tex['coses'].crop(MUG_BOX), (6, MUG_BOX[3] - MUG_BOX[1] - 1), _D(dw / 2 - 52, dh, -16))
    pw_, ph_ = PRINT_BOX[2] - PRINT_BOX[0], PRINT_BOX[3] - PRINT_BOX[1]
    px_, pz_ = dw / 2 - 98, 4
    e.caixa_girada('impressora', *_D(px_, 0, pz_)[::2], pw_, 44, ph_, da, BEIGE, 2.8, y0=dh,
                   cares={'davant': {'tex': (tex['impressora'], PRINT_BOX)},
                          'dalt': {'ramp': BEIGE, 'lvl': lambda s, t, P: 4.4 - (1.2 if 30 < t < 33 else 0)},
                          'esquerra': {'ramp': BEIGE, 'lvl': 3.0}})
    e.caixa_girada('impressora', *_D(px_, 0, pz_ + 12)[::2], pw_ - 16, 16, 5, da, BEIGE, 3.0, y0=dh + ph_)
    e.caixa_girada('impressora', *_D(px_, 0, pz_ + 14)[::2], pw_ - 24, 14, 2, da, SHEET, 5.0, y0=dh + ph_ + 5,
                   cares={'dalt': {'ramp': SHEET, 'lvl': 5.2}})
    e.sprite('ventilador', tex['ventilador'].crop(FAN_BOX), (PL.FAN[0] - FAN_BOX[0], PL.DESK_TOP - 4 - FAN_BOX[1]),
             _D(dw / 2 - 22, dh, 6))
    # la cadira de rodes, davant el terminal (el dibuix pla, dret), amb la seva ombra
    chx, chz = CHAIR
    e.foscor('ombra_cadira', (chx - 24, 0.7, chz + 16), (chx + 24, 0.7, chz + 16), (chx + 24, 0.7, chz - 16),
             (chx - 24, 0.7, chz - 16), lambda s, t: 0.6 * max(0.0, 1 - ((s - 24) / 24) ** 2 - ((t - 16) / 16) ** 2) * 1.6)
    e.sprite('cadira', tex['cadira'].crop(CHAIR_BOX), (301 - CHAIR_BOX[0], 221 - CHAIR_BOX[1]), (chx, 0, chz))
    # primer pla: la font d'aigua en silueta a l'esquerra, caixes d'arxiu a baix a la dreta i el fluorescent que penja
    FOSC = [(3, 4, 8), (8, 10, 16), (14, 16, 24), (21, 24, 33), (30, 34, 44), (40, 45, 56)]
    e.caixa_girada('primer_pla', 112, 30, 38, 38, 92, -0.3, FOSC, 1.4,
                   cares={'dalt': {'ramp': FOSC, 'lvl': 2.6}, 'davant': {'ramp': FOSC, 'lvl': 1.8},
                          'dreta': {'ramp': FOSC, 'lvl': 2.2}})
    e.tub('primer_pla', (112, 92, 30), (112, 134, 30), 13, [(4, 8, 16), (8, 18, 34), (14, 32, 54), (24, 50, 76),
                                                          (40, 74, 104)], 1.0, llum_dir=(0.6, -0.8))   # la garrafa
    e.tub('primer_pla', (112, 134, 30), (112, 140, 30), 5, FOSC, 1.6)
    for cx_, cz_, w, d, h, a, y0 in ((612, 56, 72, 54, 42, -0.3, 0), (616, 60, 56, 44, 34, -0.12, 42),
                                     (538, 4, 58, 44, 36, 0.2, 0)):
        e.caixa_girada('primer_pla', cx_, cz_, w, d, h, a, FOSC, 1.6, y0=y0,
                       cares={'dalt': {'ramp': FOSC, 'lvl': lambda s, t, P: 2.8 - (1.0 if abs(t - 12) < 3 else 0)},
                              'davant': {'ramp': FOSC, 'lvl': lambda s, t, P: 1.2 + (0.8 if abs(s - 20) < 6 and abs(t - 10) < 3 else 0)},
                              'esquerra': {'ramp': FOSC, 'lvl': 2.0}})
    return e


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


def _decorat(**kw):
    """Un decorat: la sala amb el dibuix pla canviat, menys la de sempre (només el que canvia)."""
    def draw(cv):
        img, _ = _render(tex=_textures(**kw))
        cv.img.alpha_composite(_diff(img, _base()[0]))
        cv.P = cv.img.load()
    return draw


PROPS = {
    'llista_feta': _decorat(llista=True),
    'imprimint': _decorat(impressora='imprimint'),
    'acreditacions_llestes': _decorat(impressora='llestes'),
}


# ─── Animacions ─────────────────────────────────────────────────────────────

def _sprite_capa(e, sid, img, peu_img, peu, escala_img=1.0):
    """Un fotograma d'un dibuix pla dret (un sprite de l'escena), on aquell sprite és el que es veu."""
    from PIL import Image
    from pixels import nearest
    k = e.cam.escala(peu) * escala_img
    u, v, _ = e.cam.projecta(peu)
    w, h = max(1, round(img.width * k)), max(1, round(img.height * k))
    im = nearest(img, (w, h)) if k >= 1 else img.resize((w, h), Image.Resampling.BOX)
    ox, oy = round(u - peu_img[0] * k), round(v - peu_img[1] * k)
    out = Image.new('RGBA', (e.cv.w, e.cv.h), (0, 0, 0, 0))
    src, dst, W_ = im.load(), out.load(), e.cv.w
    ids = {i for i, s in enumerate(e.ids) if s == sid}
    for y in range(h):
        Y = oy + y
        if not 0 <= Y < e.cv.h:
            continue
        for x in range(w):
            X = ox + x
            if 0 <= X < W_ and e.amo[Y * W_ + X] in ids and src[x, y][3] >= 128:
                dst[X, Y] = src[x, y]
    return out


def _fotograma(capes):
    """El fons amb unes capes damunt, menys el fons."""
    img, _ = _base()
    img = img.copy()
    for c in capes:
        img.alpha_composite(c)
    return _diff(img, _base()[0])


def _frames():
    """El ventilador: les aspes giren."""
    _, e = _base()
    dw, dh = DESK[2], DESK[4]
    out = []
    for i in range(1, 9):
        fan = _peces(fan=i * math.tau / 1.1 / 8)['ventilador'].crop(FAN_BOX)
        out.append(_fotograma([_sprite_capa(e, 'ventilador', fan, (PL.FAN[0] - FAN_BOX[0], PL.DESK_TOP - 4 - FAN_BOX[1]),
                                            _D(dw / 2 - 22, dh, 6))]))
    return out


def _frames_persiana():
    """El corrent del ventilador gronxa una mica el cordill i les lamel·les de baix de la persiana."""
    _, e = _base()
    base = _paret()
    return [_fotograma([e.capa(_diff(_paret(sway=math.sin(i * math.tau / 10)), base), {'paret_fons'})])
            for i in range(10)]


def _frames_segons():
    """El rellotge té la pila gastada: l'agulla dels segons prova d'avançar i torna enrere."""
    _, e = _base()
    base = _paret()
    out = [_fotograma([e.capa(_diff(_paret(segons=s), base), {'paret_fons'})]) for s in (15, 16)]
    return [out[0]] * 4 + [out[1]]


ANIMS = {'ventilador': {'frames': _frames, 'frameDuration': 70},
         'persiana': {'frames': _frames_persiana, 'frameDuration': 180},
         'segons': {'frames': _frames_segons, 'frameDuration': 200}}


# ─── Capes del davant ───────────────────────────────────────────────────────

def _amo(ids):
    def mask(x, y):
        _, e = _base()
        return e.ids[e.amo[y * e.cv.w + x]] in ids
    return mask


def _p(x, z, y=0.0):
    u, v, _ = CAM.projecta((x, y, z))
    return round(u), round(v)


# El primer pla (sempre davant) i la cadira (s'hi passa per darrere).
FRONT = [
    {'id': 'davant', 'mask': _amo({'primer_pla'}), 'baseline': 999, 'zIndex': 20},
    {'id': 'davant_cadira', 'mask': _amo({'cadira'}), 'baseline': _p(CHAIR[0], CHAIR[1] - 8)[1], 'zIndex': 20},
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
        if CAM.projecta((XR - 300, 0, z))[1] > v:
            lo = z
        else:
            hi = z
    return CAM.escala((XR - 300, 0, (lo + hi) / 2))


def _cantons(cx, cz, w, d, a, y0, y1):
    c, s = math.cos(a), math.sin(a)
    return [(cx + lx * c - lz * s, y, cz + lx * s + lz * c) for lx in (-w / 2, w / 2) for lz in (-d / 2, d / 2)
            for y in (y0, y1)]


# El terra on es camina (al món): davant el taulell i el passadís de la dreta cap a la porta; no s'acosta tant a la
# càmera que el personatge passi d'≈1,2.
WALK_MON = [(214, 102), (300, 70), (440, 50), (560, 62), (590, 100), (590, 292), (520, 292), (486, 270), (503, 202),
            (494, 189), (212, 116)]
_WALK = [_p(x, z) for x, z in WALK_MON]
_V_FONS, _V_PROP = min(v for _, v in _WALK), max(v for _, v in _WALK)


def _caixa_d(lx, lz, w, d, y0, y1):
    """Els cantons d'una caixa del taulell (centre en coordenades del taulell)."""
    return [_D(lx + a, y, lz + b) for a in (-w / 2, w / 2) for b in (-d / 2, d / 2) for y in (y0, y1)]


_MW, _MH = (MON_BOX[2] - MON_BOX[0]) * MK, (MON_BOX[3] - MON_BOX[1]) * MK
_PW, _PH = PRINT_BOX[2] - PRINT_BOX[0], PRINT_BOX[3] - PRINT_BOX[1]

GEOMETRIA = {
    'things': {
        'terminal': {'rect': _rect_mon(*_caixa_d(-DESK[2] / 2 + 74, 6, _MW, 18, DESK[4], DESK[4] + 4 + _MH)),
                     'walk': _p(*_D(-DESK[2] / 2 + 100, 0, -DESK[3] / 2 - 22)[::2])},
        'impressora': {'rect': _rect_mon(*_caixa_d(DESK[2] / 2 - 98, 4, _PW, 44, DESK[4], DESK[4] + _PH + 8)),
                       'walk': _p(*_D(DESK[2] / 2 - 98, 0, -DESK[3] / 2 - 22)[::2])},
        'porta': {'rect': _rect_mon((XR, 0, _wz(605)), (XR, _y(62), _wz(528))), 'walk': _p(566, 256)},
    },
    'spawns': {'iri': _p(560, 262)},
    'walkable': _WALK,
    'floorSquash': 0.42,                           # (la càmera, picada: el terra es veu aixafat)
    # L'ombra de contacte: la llum dominant són els fluorescents, a sobre del taulell; curta.
    'characterShadow': {'enabled': True, 'color': '#0a0c18', 'alpha': 0.42, 'squash': 0.4, 'core': 0.6,
                        'light': {'x': _p(420, 170)[0], 'y': _p(420, 170)[1], 'stretch': 0.45, 'reach': 160}},
    'regions': [{'id': 'perspectiva', 'active': True, 'scaleEnabled': True, 'scaleWalkSpeed': True,
                 'scaleTop': round(_escala_a(_V_FONS - 2), 3), 'scaleBottom': round(_escala_a(_V_PROP + 2), 3),
                 'points': [(0, _V_FONS - 2), (W - 1, _V_FONS - 2), (W - 1, _V_PROP + 2), (0, _V_PROP + 2)]}],
    # la llum de la sala sobre els personatges, en temps d'execució
    'characterLights': {
        'ambient': '#a8aab4',                                                           # fluorescent fred
        'lights': [
            {'x': _p(360, 180, 150)[0], 'y': _p(360, 180, 150)[1], 'radius': 300, 'color': '#e6f0ff',
             'intensity': 0.6},                                                         # els fluorescents
            {'x': _p((WIN[0] + WIN[1]) / 2, ZW, 130)[0], 'y': _p((WIN[0] + WIN[1]) / 2, ZW, 130)[1],
             'radius': 220, 'color': '#ffb48c', 'intensity': 0.7},                      # l'alba per la finestra
            {'x': _p(*_D(-DESK[2] / 2 + 74, 0, -4)[::2], DESK[4] + 30)[0],
             'y': _p(*_D(-DESK[2] / 2 + 74, 0, -4)[::2], DESK[4] + 30)[1], 'radius': 90, 'color': '#6ee68c',
             'intensity': 0.5},                                                         # la pantalla verda
        ],
    },
}
