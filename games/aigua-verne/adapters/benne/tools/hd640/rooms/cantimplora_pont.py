"""
Aigua Verne — el pont de la Cantimplora (sala de prop, P: persones de ≈100 px). PROVA EN 3D.

La mateixa cabina de sempre, però vista de biaix i una mica des de dalt, amb una càmera (hd640/tres_d.py) en lloc de
dibuixar-la de cara: es veu la cantonada (la paret de l'escala i la ràdio fuig cap al fons), el terra fa de debò
(xapa estriada en perspectiva, amb la llum de les bombetes i la foscor dels racons), la consola és un volum amb la tapa
inclinada, el mapa de navegació és una taula de vidre que es veu des de dalt, i un pilar de la nau tapa la vora de
l'esquerra (primer pla). Els personatges es fan petits quan van cap al fons (una regió d'escala de perspectiva).

Tot el detall ve del pont pla de sempre (pont_pla_comu.py): la paret, el finestral, l'escala, la ràdio, la pantalla,
la consola i els seients es dibuixen de cara com abans i es projecten com a textures. Els decorats (`vista_*`,
`pantalla_verne`) i les animacions (`mapa_llums`, `consola_llums`) també: es dibuixen plans i es projecten per les
mateixes superfícies, tapats pel que hi ha davant.

El món: x a la dreta (0 = la paret de l'escala), y amunt (0 = el terra), z cap al fons (300 = la paret del finestral);
1 unitat = 1 píxel de sala a la distància on un personatge fa 100 px (escala 1).
"""
import functools
import math

import hd640  # noqa: F401  (abans de cap hd.rooms: posa la llibreria a 640×360)
from PIL import Image

from hd.pix import Light, W, H, hr, mix, GOLD
from hd.rooms.comu import _diff, text
from hd.rooms.exterior import fbm
from hd640.rooms import pont_pla_comu as PL
from hd640.rooms.nau_comu import (OLIVE, SAFETY, STEELN, GLASSD, WBLUE, BLACKT, DECKP, WARM, cara_verne, hazard,
                                  stencil)
from hd640.tres_d import Camera, Escena, Llum

# Art a 1× (640×360): amb la perspectiva i la llum, el 2× no compensava el temps de càlcul (vegeu
# docs/guia-art-profunditat.md). Les textures (el pont pla) també són a 1×.
from hd.pix import Canvas  # noqa: E402,F811

BOTTOM = 259                                       # la sala acaba aquí (a sota, la barra de verbs)
ZW = 300                                           # la paret del finestral
HW = 200                                           # l'alçada de les parets (el dibuix pla fa 200 fins al terra)
XL = 146                                           # al dibuix pla, la cantonada: a l'esquerra, la paret de l'escala
CON = (30, 382, 270)                               # la consola: x0, x1 i el davant (z); al pla, x 150..502
SEATS = ((124, 238), (288, 238))                   # els peus dels dos seients (x, z): la pilot i la Capitana
MAPA = (372, 502, 182, 246, 34)                    # la taula del mapa: x0, x1, z0, z1, alçada del vidre
LAMPS = ((116, 262), (298, 262))                   # les dues bombetes (x, z), penjades del sostre
DOOR_Z = (ZW - XL + PL.DOOR[0], ZW - XL + PL.DOOR[2])  # l'escala (la porta), a la paret de l'esquerra

CAM = Camera(pos=(290, 190, -190), yaw=-0.12, pitch=0.16, f=380, centre=(330, 72))

LIGHT = Light(ambient=0.0, vignette=None, floor_fade=None)  # (la llum és la del món: la de l'Escena)
LLUMS = [Llum((x, 182, z), 230, 1.7, power=1.4) for x, z in LAMPS] + [
    Llum((10, 30, 199), 120, 1.2, power=1.6),                    # la llum càlida que puja de la bodega
    Llum((437, 60, 214), 110, 1.0, power=1.8),                   # el vidre del mapa
    Llum((180, 120, 296), 260, 0.5, power=1.2),                  # la claror del finestral
]


# ─── Les textures: el pont pla de sempre ─────────────────────────────────────

@functools.lru_cache(maxsize=None)
def _paret_sense_radio():
    cv = Canvas(light=PL.LIGHT)
    PL.walls(cv)
    PL.paret_detalls(cv)
    PL.finestral(cv)
    PL.escala(cv)
    PL.pantalla(cv)
    return cv.img


@functools.lru_cache(maxsize=None)
def _parets_nues():
    cv = Canvas(light=PL.LIGHT)
    PL.walls(cv)
    return cv.img


def _paret(lights=0):
    cv = Canvas(light=PL.LIGHT, img=_paret_sense_radio().copy())   # (cada fotograma, només la ràdio)
    PL.radio(cv, lights)
    return cv.img


def _consola(lights=0):
    cv = Canvas(light=PL.LIGHT, img=_parets_nues().copy())         # (sota la tapa: no surt de la superfície)
    PL.consola(cv, lights)
    return cv.img


@functools.lru_cache(maxsize=None)
def _seient(i):
    cv = Canvas(light=PL.LIGHT, transparent=True)
    PL.seient(cv, PL.SEATS[i], capitana=i == 1)
    cx = PL.SEATS[i]
    S = cv.S
    return cv.img.crop(((cx - 30) * S, 138 * S, (cx + 30) * S, 230 * S)), (30, 225 - 138)


@functools.lru_cache(maxsize=None)
def _bombeta():
    cv = Canvas(light=PL.LIGHT, transparent=True)
    PL.bulb(cv, 40, 40, cable=0)
    return cv.img.crop((0, 0, 80 * cv.S, 60 * cv.S)), (40, 40)


# ─── El mapa de navegació, vist des de dalt ──────────────────────────────────

MW, MH = 130, 64                                   # el vidre, en píxels de sala del dibuix pla


def mapa_pla(frame=None):
    """El vidre del mapa vist des de dalt (es projecta sobre la tapa de la taula): les òrbites del sistema de Vesper,
    els quatre planetes, el palau i els dipòsits."""
    cv = Canvas(MW, MH, light=None)
    cx, cy = MW / 2, MH / 2
    cv.rect(0, 0, MW - 1, MH - 1, GLASSD, lambda x, y: 2.4 + (1 - abs(y - cy) / cy) * 0.5)
    # (sense graella: a 1× i en escorç, els punts feien soroll)
    for _, r, _, _ in PL.PLANETS:
        for a in range(0, 360, 2):
            cv.put(cx + math.cos(math.radians(a)) * r * 1.1, cy + math.sin(math.radians(a)) * r * 0.5, WBLUE, 4.2, lit=0)
    pulse = 0 if frame is None else frame % 4
    cv.glow(cx, cy, 10 + (2 if pulse in (1, 2) else 0), (255, 170, 60), 0.7)
    cv.disc(cx, cy, 3, 2.4, [(200, 90, 20), (250, 160, 40), (255, 230, 150)], 1.6 + (0.6 if pulse == 2 else 0), lit=0)
    for i, (name, r, ang, col) in enumerate(PL.PLANETS):
        x, y = cx + math.cos(ang) * r * 1.1, cy + math.sin(ang) * r * 0.5
        blink = frame is not None and (frame + i * 2) % 6 == 0
        cv.disc(x, y, 2.4, 2.0, [tuple(int(c * 0.5) for c in col), col, mix(col, (255, 255, 255), 0.5)],
                2.2 if blink else 1.4, lit=0)
        cv.glow(x, y, 5, col, 0.55 if blink else 0.3)
    cv.flat(cx + 38, cy - 9, (250, 220, 120))                      # el palau orbital
    for dx, dy in ((-32, -6), (12, 8), (44, -3)):                   # els tres dipòsits
        cv.flat(cx + dx, cy + dy, (230, 236, 244))
    for k in range(10):                                            # el reflex del llum al vidre
        cv.put(14 + k * 2, 6 + k, GLASSD, 6.0, lit=0)
    return cv.img


# ─── Les superfícies ────────────────────────────────────────────────────────

def _planxa(lvl0, pw=56, ph=50, seed=11):
    """Paret de planxa procedural (on el dibuix pla no arriba): plaques, juntes i reblons, en coordenades del món."""
    def L(s, t, P):
        u, v = s, t
        px, py = int(u // pw), int(v // ph)
        val = lvl0 + (hr(px, py, seed) - 0.5) * 0.7 + (fbm(u / 26, v / 18, seed) - 0.5) * 0.9
        if u % pw < 1.2 or v % ph < 1.2:
            val -= 1.6
        elif u % pw < 2.4 or v % ph < 2.4:
            val += 0.7
        if (v % ph) > ph - 5 and (u % 8) < 1.5:
            val += 1.6                                             # els reblons
        return val
    return L


def _terra(s, t, P):
    """Xapa estriada vista des de dalt: les estries en espiga, les juntes, i gastada pel mig (on es trepitja)."""
    x, z = P[0], P[2]
    gx, gz = int(x // 7), int(z // 7)
    lx, lz = x - (gx + 0.5) * 7, z - (gz + 0.5) * 7
    d = (lx + lz) if (gx + gz) % 2 else (lx - lz)
    stud = abs(d) < 1.0 and abs(lx - lz if (gx + gz) % 2 else lx + lz) < 5.0
    v = 3.0 + (fbm(x / 70, z / 40, 9) - 0.5) * 1.2 + (hr(int(x) // 3, int(z) // 3, 9) - 0.5) * 0.4
    if stud:
        v += 1.1
    if x % 120 < 1.2 or z % 90 < 1.2:
        v -= 1.8
    worn = max(0.0, 1 - abs(z - 200) / 70) * max(0.0, 1 - abs(x - 230) / 220)
    v += worn * 0.5 - (0.6 if stud else 0) * worn
    return v


def _racons(s, t):
    return 0.0


def escena(cv, tex):
    """Tota la sala, de lluny a prop. `tex`: les textures planes (paret, consola). → l'Escena (qui ha pintat què)."""
    e = Escena(cv, CAM, LLUMS, ambient=0.0)
    zn = CAM.pos[2] - 100
    paret, consola = tex['paret'], tex['consola']
    TS = paret.width // W                                          # (textures a 2× encara que el llenç sigui a 1×)
    # el sostre, fosc, amb les costelles
    e.quad('sostre', (0, HW, zn), (W, HW, zn), (W, HW, ZW), (0, HW, ZW), ramp=OLIVE,
           lvl=lambda s, t, P: 1.2 - (1.4 if P[0] % 60 < 4 else 0), dues_cares=True)
    # la paret de l'escala (x = 0): de prop, planxa; del fons cap a la cantonada, el dibuix pla (x 0..146)
    e.quad('paret_esq_prop', (0, HW, zn), (0, HW, ZW - XL), (0, 0, ZW - XL), (0, 0, zn), ramp=OLIVE,
           lvl=_planxa(3.0))
    e.quad('paret_esq', (0, HW, ZW - XL), (0, HW, ZW), (0, 0, ZW), (0, 0, ZW - XL), tex=(paret, (0, 0, XL, HW), TS))
    # la paret del finestral (z = 300): el dibuix pla (x 146..640) i, a la dreta, més planxa
    e.quad('paret_fons', (0, HW, ZW), (W - XL, HW, ZW), (W - XL, 0, ZW), (0, 0, ZW), tex=(paret, (XL, 0, W, HW), TS))
    e.quad('paret_fons_dreta', (W - XL, HW, ZW), (W + 200, HW, ZW), (W + 200, 0, ZW), (W - XL, 0, ZW), ramp=OLIVE,
           lvl=_planxa(3.2, seed=12))
    # el terra
    e.quad('terra', (0, 0, ZW), (W + 200, 0, ZW), (W + 200, 0, zn), (0, 0, zn), ramp=DECKP, lvl=_terra)
    # la foscor dels racons: on les parets es troben amb el terra i entre elles
    e.foscor('racons', (0, 0.5, ZW), (W + 200, 0.5, ZW), (W + 200, 0.5, zn), (0, 0.5, zn),
             lambda s, t: max(0.6 * max(0.0, 1 - t / 26), 0.55 * max(0.0, 1 - s / 22)))
    e.foscor('cantonada', (0, HW, ZW - 0.5), (40, HW, ZW - 0.5), (40, 0, ZW - 0.5), (0, 0, ZW - 0.5),
             lambda s, t: 0.5 * max(0.0, 1 - s / 40))
    e.foscor('cantonada2', (0.5, HW, ZW - 40), (0.5, HW, ZW), (0.5, 0, ZW), (0.5, 0, ZW - 40),
             lambda s, t: 0.5 * max(0.0, 1 - (40 - s) / 40))
    # l'armari de la dreta (les armilles salvavides i la farmaciola), contra la paret, amb l'ombra
    ax0, ax1 = 540, 600
    e.caixa('armari', ax0, ax1, 0, 150, ZW - 26, ZW - 1, OLIVE, 3.0,
            cares={'davant': {'ramp': OLIVE, 'lvl': lambda s, t, P: 3.4 - (1.8 if abs(s - 30) < 1 else 0)
                              - (1.2 if t % 150 < 2 or s < 1.5 or s > 58.5 else 0)
                              + (1.4 if 14 < t < 34 and (int(s) % 4 < 2) and (6 < s < 24 or 36 < s < 54) else 0)
                              + (2.0 if abs(t - 80) < 2 and (abs(s - 26) < 1.5 or abs(s - 34) < 1.5) else 0)},
                   'esquerra': {'ramp': OLIVE, 'lvl': 2.0}, 'dalt': {'ramp': OLIVE, 'lvl': 4.2}})
    e.quad('armari_creu', (ax0 + 22, 132, ZW - 26.5), (ax1 - 22, 132, ZW - 26.5), (ax1 - 22, 116, ZW - 26.5),
           (ax0 + 22, 116, ZW - 26.5), ramp=PL.REDK,
           lvl=lambda s, t, P: 1.0 if (abs(s - 8) < 2.5 or abs(t - 8) < 2.5) else 4.6)
    # la claror càlida que puja de la bodega: surt per la porta de l'escala i s'escampa en diagonal pel terra
    dz0, dz1 = DOOR_Z
    e.claror((0, 0.4, dz1 + 26), (150, 0.4, dz1 + 70), (150, 0.4, dz0 - 50), (0, 0.4, dz0 - 4), (255, 186, 104),
             lambda s, t: 0.6 * max(0.0, 1 - s / 150) ** 1.2 * max(0.0, math.sin(math.pi * min(1.0, t / max(1.0, 70 + 0.75 * s)))))
    # els cables que surten de sota la consola i se'n van, fent corbes, cap a la paret de l'escala
    for k, (ramp, lv, pts) in enumerate((
            (BLACKT, 2.4, [(60, 0.8, 272), (48, 0.8, 250), (60, 0.8, 214), (30, 0.8, 196), (8, 0.8, 190)]),
            (SAFETY, 2.6, [(96, 0.8, 272), (88, 0.8, 252), (104, 0.8, 228), (70, 0.8, 214), (40, 0.8, 222),
                           (8, 0.8, 214)]),
            (BLACKT, 2.0, [(330, 0.8, 272), (340, 0.8, 254), (322, 0.8, 244), (348, 0.8, 236)]))):
        e.cable('cables', pts, ramp, lv, gruix=2.4)
    # la consola: la tapa inclinada i el davant amb el dibuix pla; el costat de la dreta, planxa
    x0, x1, zc = CON
    dx = XL + 4 - x0                                               # (al pla, la consola va de 150 a 502)
    e.quad('consola_costat', (x1, 44, zc), (x1, 74, ZW), (x1, 0, ZW), (x1, 0, zc), ramp=OLIVE,
           lvl=lambda s, t, P: 2.6 - (1.4 if P[1] < 10 else 0))
    e.quad('consola_dalt', (x0, 74, ZW), (x1, 74, ZW), (x1, 44, zc), (x0, 44, zc),
           tex=(consola, (x0 + dx, 126, x1 + dx, 156), TS))
    e.quad('consola_davant', (x0, 44, zc), (x1, 44, zc), (x1, 0, zc), (x0, 0, zc),
           tex=(consola, (x0 + dx, 156, x1 + dx, HW), TS))
    e.foscor('ombra_consola', (x0 - 6, 0.6, zc), (x1 + 8, 0.6, zc), (x1 + 8, 0.6, zc - 22), (x0 - 6, 0.6, zc - 22),
             lambda s, t: 0.55 * max(0.0, 1 - t / 22))
    # la caixa d'eines, a terra, girada (no a 90° de res), amb l'ombra
    e.foscor('ombra_caixa', (36, 0.6, 268), (100, 0.6, 268), (100, 0.6, 232), (36, 0.6, 232),
             lambda s, t: 0.6 * max(0.0, 1 - ((s - 30) / 30) ** 2 - ((t - 18) / 16) ** 2) * 1.5)
    e.caixa_girada('caixa_eines', 66, 250, 38, 18, 16, 0.45, SAFETY, 3.0,
                   cares={'dalt': {'ramp': SAFETY, 'lvl': lambda s, t, P: 4.4 - (1.6 if abs(t - 9) < 1 else 0)},
                          'davant': {'ramp': SAFETY, 'lvl': lambda s, t, P: 3.2 - (1.4 if abs(t - 5) < 0.8 else 0)
                                     + (2.0 if abs(s - 19) < 3 and 6 < t < 10 else 0)},
                          'dreta': {'ramp': SAFETY, 'lvl': 2.2}})
    e.caixa_girada('caixa_eines', 66, 250, 10, 2, 5, 0.45, STEELN, 4.0, y0=16)          # la nansa
    # els seients (dibuixos plans drets), amb la seva ombra
    for i, (sx, sz) in enumerate(SEATS):
        e.foscor(f'ombra_seient{i}', (sx - 26, 0.7, sz + 14), (sx + 26, 0.7, sz + 14), (sx + 26, 0.7, sz - 18),
                 (sx - 26, 0.7, sz - 18),
                 lambda s, t: 0.7 * max(0.0, 1 - ((s - 26) / 26) ** 2 - ((t - 16) / 16) ** 2) * 1.6)
        img, peu = _seient(i)
        e.sprite('seient' if i == 1 else 'seient_pilot', img, peu, (sx, 0, sz), img_S=TS)
    # la taula del mapa: les potes, el marc de llautó i el vidre
    mx0, mx1, mz0, mz1, my = MAPA
    e.foscor('ombra_mapa', (mx0 - 6, 0.8, mz1 + 6), (mx1 + 6, 0.8, mz1 + 6), (mx1 + 6, 0.8, mz0 - 10),
             (mx0 - 6, 0.8, mz0 - 10), lambda s, t: 0.45 * min(1.0, min(s, t, 142 - s, 80 - t) / 14))
    for lx, lz in ((mx0 + 6, mz1 - 6), (mx1 - 6, mz1 - 6), (mx0 + 6, mz0 + 6), (mx1 - 6, mz0 + 6)):
        e.caixa('mapa', lx - 2, lx + 2, 0, my - 4, lz - 2, lz + 2, STEELN, 3.6)
    e.caixa('mapa', (mx0 + mx1) / 2 - 8, (mx0 + mx1) / 2 + 8, 0, my - 4, (mz0 + mz1) / 2 - 8, (mz0 + mz1) / 2 + 8,
            STEELN, 3.0)
    e.caixa('mapa', mx0, mx1, my - 4, my, mz0, mz1, GOLD, 3.6, cares={'dalt': {'ramp': GOLD, 'lvl': 5.0}})
    e.quad('mapa_vidre', (mx0 + 3, my + 0.2, mz1 - 3), (mx1 - 3, my + 0.2, mz1 - 3), (mx1 - 3, my + 0.2, mz0 + 3),
           (mx0 + 3, my + 0.2, mz0 + 3), tex=(tex['mapa'], (0, 0, MW, MH), tex['mapa'].width // MW))
    # les bombetes, penjades del sostre
    img, peu = _bombeta()
    for lx, lz in LAMPS:
        e.linia((lx, HW, lz), (lx, 192, lz), BLACKT, 2.0)
        e.sprite('bombeta', img, peu, (lx, 186, lz), img_S=TS)
    # primer pla: el pilar de la quaderna, a l'esquerra, i la caixa d'eines a terra, a la dreta (es veuen tallats)
    e.caixa('primer_pla', 0, 22, 0, HW, 50, 72, OLIVE, 2.6,
            cares={'dreta': {'ramp': OLIVE, 'lvl': lambda s, t, P: 2.2 - (1.6 if s < 2 else 0) + (1.0 if s > 18 else 0)
                             + (1.8 if (t % 14) < 2 and 6 < s < 16 else 0)},
                   'davant': {'ramp': SAFETY, 'lvl': lambda s, t, P: 3.4 if (s + t) % 14 < 7 else 0.6}})
    for y0, r in ((12, 10), (34, 7)):                              # dues canonades grosses, arran de la paret
        e.tub('primer_pla', (28, y0, 150), (28, y0, 20), r, STEELN, 1.6, brides=34)
    for k, xx in enumerate((34, 46, 58)):                          # cables que pengen del sostre, molt a prop
        e.cable('primer_pla', [(xx, HW, 40 + k * 6), (xx + 6 + k * 4, 150 - k * 22, 46 + k * 6),
                               (xx + 2, 110 - k * 30, 52 + k * 6)], BLACKT, 1.2, gruix=2.2)
    e.caixa('primer_pla', 470, 560, 0, 46, 80, 118, OLIVE, 3.2,
            cares={'dalt': {'ramp': OLIVE, 'lvl': lambda s, t, P: 4.6 - (1.4 if s % 30 < 1.5 else 0)},
                   'esquerra': {'ramp': OLIVE, 'lvl': lambda s, t, P: 2.0 - (1.4 if t > 40 else 0)},
                   'davant': {'ramp': OLIVE, 'lvl': lambda s, t, P: 2.8 + (2.4 if 10 < t < 24 and 8 < s < 70 and
                                                                          (s + t) % 9 < 5 else 0)}})
    return e


# ─── Composició ────────────────────────────────────────────────────────────

@functools.lru_cache(maxsize=None)
def _textures():
    return {'paret': _paret(), 'consola': _consola(), 'mapa': _mapa2x(None)}


def _mapa2x(frame):
    from pixels import nearest
    im = mapa_pla(frame)
    S = Canvas.S
    return im if im.width == MW * S else nearest(im, (MW * S, MH * S))


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


def _flat(fn):
    cv = Canvas(light=PL.LIGHT, transparent=True)
    fn(cv)
    return cv.img


def _vista(planeta):
    def fn(cv):
        _, e = _base()
        cv.img.alpha_composite(e.capa(_flat(PL.vistes_pane(planeta)), {'paret_fons'}))
    return fn


def pantalla_verne(cv):
    """La cara del Magnat a la pantalla i la claror blanca que fa a la paret i a la consola."""
    base, e = _base()
    face = Canvas(light=PL.LIGHT, transparent=True)
    cara_verne(face, PL.SCREEN_IN)
    on = base.copy()
    on.alpha_composite(e.capa(face.img, {'paret_fons'}))
    c = e.cam.projecta(((PL.SCREEN[0] + PL.SCREEN[2]) / 2 - XL, 128, ZW))
    S = cv.S
    P = on.load()
    for Y in range(0, BOTTOM * S):
        for X in range(int((c[0] - 130) * S), min(on.width, int((c[0] + 130) * S))):
            d = math.hypot(X / S - c[0], (Y / S - c[1]) * 1.2) / 120
            if d >= 1:
                continue
            o = P[X, Y]
            k = 0.24 * (1 - d)
            P[X, Y] = (int(o[0] + (214 - o[0]) * k), int(o[1] + (228 - o[1]) * k), int(o[2] + (246 - o[2]) * k), 255)
    cv.img.alpha_composite(_diff(on, base))


PROPS = {
    'vista_terra2': _vista('terra2'),
    'vista_aqua': _vista('aqua'),
    'vista_ferrum': _vista('ferrum'),
    'vista_verdant': _vista('verdant'),
    'pantalla_verne': pantalla_verne,
}


def _frames_mapa():
    _, e = _base()
    return [e.capa(_mapa2x(f), {'mapa_vidre'}) for f in range(12)]


def _frames_consola():
    _, e = _base()
    p0, c0 = _paret(0), _consola(0)
    out = []
    for f in range(8):
        img = e.capa(_diff(_paret(f), p0), {'paret_esq', 'paret_fons'})
        img.alpha_composite(e.capa(_diff(_consola(f), c0), {'consola_dalt', 'consola_davant'}))
        out.append(img)
    return out


ANIMS = {
    'mapa_llums': {'frames': _frames_mapa, 'frameDuration': 240},
    'consola_llums': {'frames': _frames_consola, 'frameDuration': 300},
}


def _davant(x, y):
    _, e = _base()
    S = e.S
    i = e.amo[(y * S + S // 2) * e.cv.w + x * S + S // 2]
    return e.ids[i] == 'primer_pla'


FRONT = {'mask': _davant, 'baseline': 999, 'zIndex': 20}


# ─── Geometria (coordenades de sala, projectades) ────────────────────────────

def _p(x, z, y=0.0):
    u, v, _ = CAM.projecta((x, y, z))
    return round(u), round(v)


def _rect_mon(*Ps):
    pts = [CAM.projecta(P) for P in Ps]
    return (max(0, round(min(p[0] for p in pts))), max(0, round(min(p[1] for p in pts))),
            min(W - 1, round(max(p[0] for p in pts))), min(BOTTOM, round(max(p[1] for p in pts))))


# El terra on es camina (al món): davant la consola i els seients, amb un clot per la taula del mapa i lluny de la
# caixa del primer pla.
WALK_MON = [(44, 230), (352, 230), (352, 172), (520, 172), (520, 128), (462, 128), (462, 112), (44, 112)]
_WALK = [_p(x, z) for x, z in WALK_MON]
_V_FONS, _V_PROP = min(v for _, v in _WALK), max(v for _, v in _WALK)


def _escala_a(v):
    """L'escala d'un personatge amb els peus a la y de pantalla `v` (al terra, la profunditat només depèn de v)."""
    lo, hi = 1.0, 2000.0
    for _ in range(60):                                            # el z (al mig de la sala) que cau a la y v
        z = (lo + hi) / 2
        if CAM.projecta((260, 0, z))[1] > v:
            lo = z
        else:
            hi = z
    return CAM.escala((260, 0, (lo + hi) / 2))


RADIO_Z = (ZW - XL + PL.RADIO[0], ZW - XL + PL.RADIO[2])

GEOMETRIA = {
    'things': {
        'escala': {'rect': _rect_mon((0, HW - PL.DOOR[1] + 20, DOOR_Z[0] - 6), (0, 0, DOOR_Z[1] + 6)),
                   'walk': _p(52, (DOOR_Z[0] + DOOR_Z[1]) / 2 - 8)},
        'radio': {'rect': _rect_mon((0, HW - PL.RADIO[1] + 2, RADIO_Z[0] - 2), (0, HW - PL.RADIO[3] - 12, RADIO_Z[1] + 4)),
                  'walk': _p(56, 226)},
        'finestral': {'rect': _rect_mon((PL.WIN[0] - XL, HW - PL.WIN[1], ZW), (PL.WIN[2] - XL, HW - PL.WIN[3], ZW)),
                      'walk': _p(200, 228)},
        'pantalla': {'rect': _rect_mon((PL.SCREEN[0] - XL, HW - PL.SCREEN[1], ZW), (PL.SCREEN[2] - XL, HW - PL.SCREEN[3], ZW)),
                     'walk': _p(420, 168)},
        'mapa': {'rect': _rect_mon((MAPA[0], MAPA[4] + 4, MAPA[3]), (MAPA[1], 0, MAPA[2])),
                 'walk': _p(437, 164)},
        'seient': {'rect': _rect_mon((SEATS[1][0] - 28, 92, SEATS[1][1]), (SEATS[1][0] + 28, 0, SEATS[1][1])),
                   'walk': _p(SEATS[1][0] + 40, 224)},
    },
    'spawns': {'capitana': _p(352, 226), 'iri': _p(250, 160), 'vet': _p(150, 182)},
    'walkable': _WALK,
    'floorSquash': 0.45,                           # (la càmera, picada, a ≈1,9 m: el terra es veu aixafat)
    'regions': [{'id': 'perspectiva', 'active': True, 'scaleEnabled': True, 'scaleWalkSpeed': True,
                 'scaleTop': round(_escala_a(_V_FONS - 2), 3), 'scaleBottom': round(_escala_a(_V_PROP + 2), 3),
                 'points': [(0, _V_FONS - 2), (W - 1, _V_FONS - 2), (W - 1, _V_PROP + 2), (0, _V_PROP + 2)]}],
}
