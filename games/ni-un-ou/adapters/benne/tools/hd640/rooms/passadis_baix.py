"""
El passadís de la coberta de sota. EN 3D (hd640/tres_d.py), a 1×.

Estret, verd i de ferro. Una càmera alta, girada cap a la dreta, que mira la paret de les portes de biaix:
  - la paret fuig cap a la dreta amb les quadernes, els reblons i les soldadures, i les **portes estanques en escorç**:
    la del **camarot** de l'Iri (a prop, a l'esquerra), la de la **sala de màquines** (amb el tauler de suro i el
    **repetidor d'alarmes** al costat) i la del **pallol**; l'extintor, el tub que baixa amb la vàlvula i el rètol
    de les bombes;
  - els tubs d'aigua de mar i de gasoil, amb volum, recorren la paret; els llums de gàbia, penjats del sostre baix;
  - a terra, la planxa estriada que s'empetiteix cap al fons, l'**escotilla** de la sala de bombes (vista des de
    dalt, amb la vora de seguretat) i, a l'Escena 1, les **petjades** mullades d'en Diu;
  - al fons, la paret del cap del passadís i l'**escala** de vaixell, que hi puja arrambada cap al forat del sostre,
    d'on baixa la llum de la coberta principal (la sortida);
  - uns bidons amarrats, separats de la paret (s'hi passa per darrere);
  - primer pla: un tub gros i una safata de cables al sostre, i un puntal amb un rotllo de cap a l'esquerra.

El detall de la paret ve del dibuix pla de sempre (passadis_baix_pla_comu.py), projectat. Les animacions (`llum`, el
llum de gàbia que fa mal contacte, i `gota`, la condensació sota el tub de gasoil) i les petjades es pinten al món i
es projecten.

El món: x a la dreta (= la x del dibuix pla de la paret), y amunt (0 = el terra), z cap al fons (200 = la paret);
1 unitat = 1 píxel de sala a la distància on un personatge fa ≈110 px (escala 1).
"""
import functools
import math

import hd640  # noqa: F401  (abans de cap hd.rooms: posa la llibreria a 640×360)
from PIL import Image

from hd.pix import Canvas, Light, W, H, hr, mix
from hd.rooms.arenga import WALL, ENG, DECK, CAB, DARK, WHITEP, YELL, SEAG, FUEL, BRASS
from hd.rooms.exterior import fbm
from hd640.rooms import sota
from hd640.rooms import passadis_baix_pla_comu as PL
from hd640.tres_d import Camera, Escena, Llum

BOTTOM = 259                                       # la sala acaba aquí (a sota, la barra de verbs)
FY = PL.FLOOR_Y                                    # al dibuix pla, el terra (203)
FY0 = 30                                           # al dibuix pla, on comença la paret (a dalt, el sostre pintat)
HW = FY - FY0                                      # l'alçada de les parets (173)
ZW = 200                                           # la paret de les portes
XR = 540                                           # la paret del cap del passadís (on s'arramba l'escala)
XE = -260                                          # fins on arriba la paret per l'esquerra (fora de la pantalla)
LAMPS = ((PL.LAMPS[0], ZW - 34), (PL.LAMPS[1], ZW - 34))       # els llums de gàbia (x, z), penjats del sostre
ESC = (XR - 50, XR - 4, 52, ZW - 2)                # l'escala: x0, x1, z del peu, z de dalt
FORAT = (XR - 58, XR, ZW - 50, ZW)                 # el forat del sostre: x0, x1, z0, z1
HATCH = (356, 452, 96, 146)                        # l'escotilla: x0, x1, z0, z1
BIDONS = ((120, 70), (152, 62), (102, 46))         # els bidons (x, z): dos de grans i un de petit
VALV = 373                                         # el tub que baixa amb la vàlvula (x)


def _y(fy):
    """Una y del dibuix pla (el terra, a 203) → l'alçada del món."""
    return FY - fy


CAM = Camera(pos=(250, 150, -360), yaw=0.24, pitch=0.12, f=420, centre=(330, 96))

LIGHT = Light(ambient=0.0, vignette=None, floor_fade=None)  # (la llum és la del món: la de l'Escena)
LLUMS = [Llum((x, HW - 16, z), 230, 1.8, power=1.4) for x, z in LAMPS] + [
    Llum(((FORAT[0] + FORAT[1]) / 2, HW + 40, (FORAT[2] + FORAT[3]) / 2), 260, 2.2, power=1.3)]   # la coberta, per dalt

# la llum de les textures: la del dibuix pla, sense la vinyeta
TEX_LIGHT = Light(ambient=-0.45, vignette=None, floor_fade=None)
TEX_LIGHT.points = list(PL.LIGHT.points)

FOSC = [(2, 4, 4), (5, 9, 8), (9, 15, 13), (14, 22, 19), (20, 30, 26), (28, 40, 34)]
ROPE = [(30, 24, 14), (60, 50, 30), (100, 86, 56), (140, 124, 86), (176, 162, 120)]


# ─── Les textures: el dibuix pla de sempre ───────────────────────────────────

def _bombes(cv):
    """El rètol de les bombes, amb la fletxa avall (al pla, el dibuixava l'escotilla)."""
    sota.centered_sign(cv, 440, 157, 'BOMBES', ramp=WHITEP, lvl=4.0)
    cv.vline(440, 172, 184, WHITEP, 3.6)
    cv.vline(441, 172, 184, WHITEP, 2.4)
    cv.poly([(435, 183), (446, 183), (440, 189)], WHITEP, 3.6)


@functools.lru_cache(maxsize=None)
def _paret():
    """La paret de les portes, de cara: la planxa (sense els tubs, que van en 3D), les tres portes, el tauler de
    suro, el repetidor d'alarmes, l'extintor, el rètol de sortida i el de les bombes."""
    cv = Canvas(light=TEX_LIGHT)
    sota.plate_wall(cv, 0, W - 1, frames=85, frame0=-40, seams=(75, 149), rust=40, seed=11)
    PL.notice(cv)
    PL.alarms(cv)
    PL.cabin_door(cv)
    PL.engine_door(cv)
    PL.store_door(cv)
    PL.extinguisher(cv)
    PL.ladder_sign(cv)
    _bombes(cv)
    return cv.img


@functools.lru_cache(maxsize=None)
def _paret_nua():
    """La planxa sola (per a la paret de més enllà i la del cap del passadís)."""
    cv = Canvas(light=Light(ambient=-0.25, vignette=None, floor_fade=None))
    sota.plate_wall(cv, 0, W - 1, frames=85, frame0=-40, seams=(75, 149), rust=30, seed=12)
    return cv.img


@functools.lru_cache(maxsize=None)
def _peces():
    """Els llums de gàbia i la vàlvula, plans sobre transparent (en surten els retalls)."""
    cv = Canvas(light=TEX_LIGHT, transparent=True)
    sota.cage_lamp(cv, 200, 29)
    from hd.rooms.arenga import box
    box(cv, 369, 128, 377, 136, CAB, 3.2)
    cv.disc(373, 124, 6, 2, PL.REDP, lambda nx, ny: 3.6 - nx - ny)          # el volant de la vàlvula
    cv.vline(373, 124, 128, CAB, 3.6)
    return cv.img


LAMP_BOX = (191, 20, 210, 40)                       # el llum de gàbia, al pla
VALV_BOX = (366, 121, 381, 137)


# ─── Les superfícies ────────────────────────────────────────────────────────

def _planxa(s, t, P):
    """Planxa estriada en coordenades del món: planxes de 100 amb soldadures, i les estries en parelles creuades."""
    x, z = P[0], P[2]
    if x % 100 < 1.2 or z % 70 < 1.2:
        return 1.1
    if x % 100 < 2.2 or z % 70 < 2.2:
        return 3.2
    a, b = int(x / 3.2) % 4, int(z / 3.2) % 4
    v = 2.5 + (fbm(x / 70, z / 50, 7) - 0.5) * 0.6
    if (a == 0 and b in (0, 1)) or (a == 2 and b in (2, 3)):
        v += 0.9
    elif (a == 1 and b == 1) or (a == 3 and b == 3):
        v -= 0.3
    return v


def _escotilla(s, t, P):
    """L'escotilla vista des de dalt: la vora pintada a franges grogues i negres, la tapa estriada, els cargols, les
    frontisses i la nansa encastada."""
    w, d = HATCH[1] - HATCH[0], HATCH[3] - HATCH[2]
    if s < 7 or s > w - 7 or t < 7 or t > d - 7:
        if s < 1 or s > w - 1 or t < 1 or t > d - 1:
            return 0.6
        return 3.2 - (0.8 if hr(int(s), int(t), 21) > 0.9 else 0) if int(s + t) // 5 % 2 == 0 else -9
    v = 3.6 + (0.9 if (int(s / 2) + int(t)) % 4 == 0 else 0)
    if s < 8.5 or s > w - 8.5 or t < 8.5 or t > d - 8.5:
        return 5.0 if t < 8.5 else 1.2
    for bx, bz in ((11, 11), (w - 11, 11), (11, d - 11), (w - 11, d - 11)):
        if abs(s - bx) < 1.2 and abs(t - bz) < 1.2:
            return 5.6
    if abs(s - w / 2) < 9 and abs(t - d / 2) < 4:
        return 1.6 if abs(s - w / 2) < 6 and abs(t - d / 2) < 1.5 else 4.4
    return v


def escena(cv, tex):
    """Tot el passadís, de lluny a prop. → l'Escena (qui ha pintat què)."""
    e = Escena(cv, CAM, LLUMS, ambient=-0.4)
    zn = CAM.pos[2] + 40
    paret, nua, pec = tex['paret'], tex['nua'], tex['peces']
    fx0, fx1, fz0, fz1 = FORAT
    # el forat del sostre: la coberta principal, clara (el sostre de dalt i les parets del forat)
    e.quad('forat', (fx0 - 40, HW + 70, fz1 + 30), (fx1 + 40, HW + 70, fz1 + 30), (fx1 + 40, HW + 70, fz0 - 40),
           (fx0 - 40, HW + 70, fz0 - 40), ramp=PL.CREAM, lvl=lambda s, t, P: 3.4 + (0.6 if int(P[0]) % 29 < 1.5 else 0),
           dues_cares=True)
    for a, b in (((fx0, HW, fz0), (fx1, HW, fz0)), ((fx0, HW, fz0), (fx0, HW, fz1))):
        e.quad('forat', (a[0], HW + 70, a[2]), (b[0], HW + 70, b[2]), (b[0], HW, b[2]), (a[0], HW, a[2]), ramp=PL.CREAM,
               lvl=lambda s, t, P: 2.6 - t * 0.012, dues_cares=True)
    # el sostre, fosc, amb els baos (sobre les quadernes) i el forat de l'escala
    e.quad('sostre', (XE, HW, zn), (fx0, HW, zn), (fx0, HW, ZW), (XE, HW, ZW), ramp=ENG,
           lvl=lambda s, t, P: 1.0 + (fbm(P[0] / 60, P[2] / 40, 4) - 0.5) * 0.6, dues_cares=True)
    e.quad('sostre', (fx0, HW, zn), (XR, HW, zn), (XR, HW, fz0), (fx0, HW, fz0), ramp=ENG, lvl=1.0, dues_cares=True)
    for bx in range(-40 - 85 * 3, XR, 85):
        e.caixa('sostre', bx - 3, bx + 11, HW - 10, HW, zn, ZW, ENG, 1.8,
                cares={'sota': {'ramp': ENG, 'lvl': 1.4}, 'esquerra': {'ramp': ENG, 'lvl': 2.2}})
    e.caixa('sostre', fx0 - 4, fx0, HW - 14, HW, fz0, fz1, ENG, 2.4)                     # la brazola del forat
    e.caixa('sostre', fx0, fx1, HW - 14, HW, fz0 - 4, fz0, ENG, 2.0)
    # la safata de cables, a tocar de la paret, amb els cables de colors
    e.caixa('sostre', XE, XR, HW - 20, HW - 16, ZW - 34, ZW - 12, CAB, 2.4, cares={'dalt': {'ramp': CAB, 'lvl': 1.6}})
    for k, col in enumerate(([(20, 20, 24), (40, 36, 30), (70, 50, 34)], [(40, 12, 10), (110, 40, 34), (160, 70, 50)],
                             [(12, 20, 40), (30, 50, 80), (60, 90, 130)])):
        e.cable('sostre', [(XE, HW - 15, ZW - 30 + k * 7), (XR, HW - 15, ZW - 30 + k * 7)], col, 1.8, gruix=2.4)
    # la paret de les portes (z = 200): de lluny a l'esquerra, planxa; després, el dibuix pla
    e.quad('paret_esq', (XE, HW, ZW), (0, HW, ZW), (0, 0, ZW), (XE, 0, ZW), tex=(nua, (380, FY0, 640, FY)))
    e.quad('paret', (0, HW, ZW), (XR, HW, ZW), (XR, 0, ZW), (0, 0, ZW), tex=(paret, (0, FY0, XR, FY)))
    # la paret del cap del passadís (x = 540), de cara al passadís
    e.quad('paret_cap', (XR, HW, ZW), (XR, HW, zn), (XR, 0, zn), (XR, 0, ZW), tex=(nua, (0, FY0, 600, FY)))
    # el terra: la planxa estriada i l'escotilla
    e.quad('terra', (XE, 0, ZW), (XR, 0, ZW), (XR, 0, zn), (XE, 0, zn), ramp=DECK, lvl=_planxa)
    hx0, hx1, hz0, hz1 = HATCH
    e.quad('escotilla', (hx0, 0.3, hz1), (hx1, 0.3, hz1), (hx1, 0.3, hz0), (hx0, 0.3, hz0), ramp=DECK,
           lvl=lambda s, t, P: (lambda v: 1.0 if v == -9 else v)(_escotilla(s, t, P)))
    _franges(e)
    # la llum: bassals sota els llums, i la de la coberta, que baixa per l'escala i s'estira pel terra
    for x, z in LAMPS:
        e.claror((x - 130, 0.5, ZW), (x + 130, 0.5, ZW), (x + 130, 0.5, ZW - 200), (x - 130, 0.5, ZW - 200),
                 (210, 220, 170), lambda s, t: 0.16 * max(0.0, 1 - math.hypot(s - 130, (t - 34) * 1.2) / 130))
    e.claror((XR - 200, 0.6, ZW), (XR, 0.6, ZW), (XR, 0.6, ZW - 200), (XR - 200, 0.6, ZW - 200), (255, 236, 190),
             lambda s, t: 0.30 * max(0.0, 1 - math.hypot((200 - s) * 0.9, t * 1.1) / 190))
    e.claror((XR - 0.5, HW, ZW), (XR - 0.5, HW, ZW - 160), (XR - 0.5, 0, ZW - 160), (XR - 0.5, 0, ZW), (255, 236, 190),
             lambda s, t: 0.32 * max(0.0, 1 - math.hypot(s * 0.9, t * 0.6) / 150))
    e.claror((XR - 160, HW, ZW - 0.5), (XR, HW, ZW - 0.5), (XR, 0, ZW - 0.5), (XR - 160, 0, ZW - 0.5), (255, 236, 190),
             lambda s, t: 0.26 * max(0.0, 1 - math.hypot((160 - s) * 0.9, t * 0.6) / 150))
    # la foscor dels racons i de dalt de la paret
    e.foscor('racons', (XE, 0.7, ZW), (XR, 0.7, ZW), (XR, 0.7, zn), (XE, 0.7, zn),
             lambda s, t: max(0.5 * max(0.0, 1 - t / 22), 0.4 * max(0.0, 1 - (s - 200) / 160) if s > 200 else 0.4))
    e.foscor('sostre_fosc', (XE, HW - 0.5, ZW - 0.6), (XR, HW - 0.5, ZW - 0.6), (XR, 0, ZW - 0.6), (XE, 0, ZW - 0.6),
             lambda s, t: max(0.45 * max(0.0, 1 - t / 40), 0.5 * max(0.0, 1 - (s - 40) / 220)))
    # els tubs de la paret, amb volum: l'aigua de mar i el gasoil, amb les abraçadores; el tub que baixa i la vàlvula
    ys, yf = _y(48), _y(61)
    e.tub('tubs', (XE, ys, ZW - 8), (XR, ys, ZW - 8), 4.5, SEAG, 3.0, brides=69)
    e.tub('tubs', (XE, yf, ZW - 7), (539, yf, ZW - 7), 3.5, FUEL, 3.0, brides=69)
    for x in range(27 - 64 * 4, 540, 64):
        e.caixa('tubs', x, x + 2, yf - 6, ys + 7, ZW - 13, ZW - 1, CAB, 3.0)
    e.tub('tubs', (VALV, ys, ZW - 12), (VALV, 0, ZW - 12), 3.5, SEAG, 2.8, brides=64)
    e.sprite('tubs', pec.crop(VALV_BOX), (7, 13), (VALV, _y(137), ZW - 14))
    # els llums de gàbia, penjats del sostre (amb el cable)
    for x, z in LAMPS:
        e.caixa('llums', x - 1, x + 1, HW - 8, HW, z - 1, z + 1, CAB, 2.0)
        e.sprite('llum_%d' % x, pec.crop(LAMP_BOX), (9.5, 1), (x, HW - 8, z))
    # els bidons amarrats (un de tombat davant), separats de la paret, amb la seva ombra
    e.foscor('ombra_bidons', (76, 0.8, 106), (174, 0.8, 106), (174, 0.8, 22), (76, 0.8, 22),
             lambda s, t: 0.6 * max(0.0, 1 - ((s - 50) / 48) ** 2 - ((t - 42) / 40) ** 2) * 1.5)
    for i, (bx, bz) in enumerate(BIDONS[:2]):
        _bido(e, bx, bz, 54 if i == 0 else 48, FUEL if i == 0 else SEAG, seed=i)
    e.cable('bidons', [(BIDONS[0][0] - 14, 30, BIDONS[0][1] - 10), (BIDONS[1][0], 28, BIDONS[1][1] - 13),
                       (BIDONS[1][0] + 15, 30, BIDONS[1][1] - 4)], ROPE, 2.4, gruix=1.8)
    _bido(e, BIDONS[2][0], BIDONS[2][1], 30, PL.REDP, seed=4)
    # a la paret del cap: l'armari de la mànega contra incendis i dos tubs que baixen
    e.caixa('armari', XR - 12, XR, 50, 104, 0, 34, PL.REDP, 3.0,
            cares={'esquerra': {'ramp': PL.REDP, 'lvl': lambda s, t, P: 4.0 if 5 < s < 29 and 8 < t < 16 else
                                (1.6 if abs(t - 30) < 1 else 3.0)},
                   'davant': {'ramp': PL.REDP, 'lvl': 2.0}, 'dalt': {'ramp': PL.REDP, 'lvl': 3.6}})
    for z, r, ramp in ((44, 4, SEAG), (54, 3, FUEL)):
        e.tub('tubs', (XR - 8, HW, z), (XR - 8, 0, z), r, ramp, 2.8, brides=58)
    # l'escala de vaixell, arrambada a la paret del cap, que puja cap al forat
    _escala(e)
    # primer pla: un tub gros i la safata de cables al sostre, un puntal amb un rotllo de cap a l'esquerra
    e.tub('primer_pla', (XE, HW - 8, 14), (XR + 40, HW - 8, 14), 7, FOSC, 2.0, brides=90)
    e.caixa('primer_pla', XE, XR + 40, HW - 4, HW, -8, 6, FOSC, 1.4,
            cares={'sota': {'ramp': FOSC, 'lvl': lambda s, t, P: 2.4 if int(P[0]) % 12 < 2 else 1.0}})
    e.tub('primer_pla', (-40, 0, 40), (-40, HW, 40), 7, FOSC, 2.0, brides=50)
    for k in range(5):
        e.tub('primer_pla', (-60 + k * 2, 10 + k * 7, 34), (-20 - k * 2, 10 + k * 7, 34), 4, ROPE, 1.4)
    return e


def _franges(e):
    """Les franges grogues de la vora de l'escotilla (a sobre de la planxa)."""
    hx0, hx1, hz0, hz1 = HATCH
    w, d = hx1 - hx0, hz1 - hz0

    def forma(s, t):
        if 7 <= s <= w - 7 and 7 <= t <= d - 7:
            return False
        if s < 1 or s > w - 1 or t < 1 or t > d - 1:
            return False
        return int(s + (d - t)) // 6 % 2 == 0
    e.quad('escotilla', (hx0, 0.5, hz1), (hx1, 0.5, hz1), (hx1, 0.5, hz0), (hx0, 0.5, hz0), ramp=YELL,
           lvl=lambda s, t, P: 3.2 - (0.9 if hr(int(s), int(t), 21) > 0.9 else 0), forma=forma)


def _bido(e, x, z, h, ramp, seed=0):
    """Un bidó dret: el cos rodó (facetes que la llum de l'escena fa de cada to, i a més una mica de llum de costat),
    les dues anelles i la tapa vista des de dalt, amb el tap."""
    r = 16 if h > 40 else 12
    n = 18
    for i in range(n):
        a0, a1 = 2 * math.pi * i / n, 2 * math.pi * (i + 1) / n
        A = (x + r * math.cos(a0), z + r * math.sin(a0))
        B = (x + r * math.cos(a1), z + r * math.sin(a1))
        lum = 0.9 * math.cos((a0 + a1) / 2 - math.pi * 1.15)              # la llum ve de l'esquerra i del davant

        def lv(s, t, P, lum=lum):
            yy = h - t
            anella = abs(yy - h * 0.33) < 1.6 or abs(yy - h * 0.66) < 1.6
            return 2.6 + lum + (0.9 if anella else 0) - (0.7 if yy < 2.5 else 0) + (hr(int(s), int(t // 3), seed) - 0.5) * 0.4
        e.quad('bidons', (A[0], h, A[1]), (B[0], h, B[1]), (B[0], 0, B[1]), (A[0], 0, A[1]), ramp=ramp, lvl=lv)
    e.quad('bidons', *[(x + dx, h, z + dz) for dx, dz in ((-r, r), (r, r), (r, -r), (-r, -r))], ramp=ramp,
           lvl=lambda s, t, P: (3.4 if math.hypot(s - r, t - r) < r - 2 else 4.2) +
           (0.8 if math.hypot(s - r - 6, t - r + 4) < 2.5 else 0),
           forma=lambda s, t: math.hypot(s - r, t - r) <= r)


def _escala(e):
    """L'escala inclinada: dos zancs, els graons amb la vora groga, i els passamans de tub amb els puntals."""
    x0, x1, za, zb = ESC
    n = 15

    def P(y, x):
        return (x, y, za + (zb - za) * y / HW)
    for x in (x1, x0):
        p0, p1, p3 = (x, 6, za - 4), (x, HW + 6, zb - 4), (x, -6, za + 10)
        p2 = (p1[0] + p3[0] - p0[0], p1[1] + p3[1] - p0[1], p1[2] + p3[2] - p0[2])
        e.quad('escala', p0, p1, p2, p3, ramp=ENG, lvl=3.0 if x == x0 else 2.0, dues_cares=True)
    for i in range(1, n):
        y = HW * i / n
        z = za + (zb - za) * i / n
        e.caixa('escala', x0 + 1, x1 - 1, y - 2.5, y, z - 6, z + 5, CAB, 3.0,
                cares={'dalt': {'ramp': CAB, 'lvl': lambda s, t, P: 4.0 if int(s) % 3 == 0 else 3.2},
                       'davant': {'ramp': YELL, 'lvl': 3.0}})
    for x in (x0 - 3, x1 - 2):
        e.tub('escala', P(42, x), P(HW + 42, x), 1.6, BRASS, 3.4)
        for yy in (14, 90):
            a = P(yy, x)
            e.tub('escala', a, (a[0], a[1] + 40, a[2]), 1.3, BRASS, 2.8)


# ─── Composició ─────────────────────────────────────────────────────────────

def _proj(P):
    u, v, _ = CAM.projecta(P)
    return u, v


@functools.lru_cache(maxsize=None)
def _textures():
    return {'paret': _paret(), 'nua': _paret_nua(), 'peces': _peces()}


def _post(img):
    """El halo dels llums de gàbia i la claror que baixa per l'escala, damunt l'escena."""
    cv = Canvas(light=LIGHT, img=img.copy())
    for x, z in LAMPS:
        u, v = _proj((x, HW - 13, z))
        cv.glow(u, v, 40, (255, 236, 190), 0.4)
        cv.glow(u, v, 12, (255, 246, 220), 0.55)
    u, v = _proj(((FORAT[0] + FORAT[1]) / 2, HW, (FORAT[2] + FORAT[3]) / 2))
    cv.glow(u, v, 60, (255, 236, 190), 0.35)
    return cv.img


def _render(tex=None):
    cv = Canvas(light=LIGHT)
    e = escena(cv, tex or _textures())
    cv.rect(0, BOTTOM + 1, W - 1, H - 1, [(0, 0, 0)], 0, lit=0)    # la barra de verbs: negre
    return cv.img, e


@functools.lru_cache(maxsize=None)
def _base():
    return _render()


@functools.lru_cache(maxsize=None)
def _base_llum():
    return _post(_base()[0])


def bg(cv):
    cv.img.paste(_base_llum())
    cv.P = cv.img.load()


def _taca(img, P, r, col, k, amo=None):
    """Una taca d'aigua a terra (una el·lipse del món al punt P, de radi `r`), barrejada cap a `col`."""
    src = _base_llum().load()
    dst = img.load()
    _, e = _base()
    ids = e.ids
    u, v = _proj(P)
    s = CAM.escala(P)
    rx, ry = max(0.6, r * s), max(0.5, r * s * 0.42)
    for y in range(int(v - ry - 1), int(v + ry + 2)):
        for x in range(int(u - rx - 1), int(u + rx + 2)):
            if not (0 <= x < W and 0 <= y <= BOTTOM):
                continue
            if ((x - u) / rx) ** 2 + ((y - v) / ry) ** 2 > 1:
                continue
            if amo and ids[e.amo[y * W + x]] not in amo:
                continue
            dst[x, y] = mix(src[x, y], col, k) + (255,)


def petjades(cv):
    """Escena 1: les petjades mullades d'en Diu, que van i vénen entre la porta del camarot i la de màquines."""
    img = Image.new('RGBA', (W, H), (0, 0, 0, 0))
    for i in range(9):                                                   # anada (a prop de la paret)
        t = i / 8
        x, z = 70 + (176 - 70) * t + (0 if i % 2 else 4), ZW - 26 - (i % 2) * 5
        for dx, dz, r in ((0, 0, 2.2), (-2.6, 3.0, 1.0), (0, 3.6, 1.0), (2.6, 3.0, 1.0)):
            _taca(img, (x + dx, 0, z + dz), r, (120, 156, 160), 0.5 - t * 0.12, {'terra'})
        _taca(img, (x + 0.6, 0, z - 0.4), 0.9, (200, 228, 228), 0.5 - t * 0.12, {'terra'})
    for i in range(8):                                                   # tornada (més endavant, més seca)
        t = i / 7
        x, z = 172 - (172 - 76) * t + (3 if i % 2 else 0), ZW - 48 - (i % 2) * 5
        for dx, dz, r in ((0, 0, 2.2), (-2.6, -3.0, 1.0), (0, -3.6, 1.0), (2.6, -3.0, 1.0)):
            _taca(img, (x + dx, 0, z + dz), r, (120, 156, 160), 0.42 - t * 0.14, {'terra'})
    cv.img.alpha_composite(img)
    cv.P = cv.img.load()


PROPS = {'petjades': petjades}


# ─── Animacions ─────────────────────────────────────────────────────────────

def _frames_llum():
    """El llum de gàbia de la dreta fa mal contacte: de tant en tant baixa dues vegades i torna."""
    base = _base_llum()
    x, z = LAMPS[1]
    lx, ly = _proj((x, HW - 13, z))
    fx, fy = _proj((x, 0, z))
    R = 200 * CAM.escala((x, 0, z))
    dims = {38: 0.55, 39: 0.25, 41: 0.6, 42: 0.35}              # fotograma → quant s'apaga
    area = (max(0, int(lx - R)), 0, min(W, int(lx + R)), BOTTOM + 1)
    empty = Image.new('RGBA', base.size, (0, 0, 0, 0))
    frames, fets = [], {}
    for i in range(48):
        k = dims.get(i, 0)
        if not k:
            frames.append(empty)
            continue
        if k not in fets:
            cv = Canvas(light=LIGHT, img=base.copy())
            cv.darken(area[0], area[1], area[2] - 1, area[3] - 1,
                      lambda X, Y: k * max(0.0, 1 - math.hypot(X - lx, (Y - (ly + fy) / 2) * 0.9) / R), dither=False)
            cv.darken(lx - 9, ly - 10, lx + 9, ly + 6, min(0.85, k * 1.4), dither=False)
            fets[k] = sota.fast_diff(cv.img, base, area)
        frames.append(fets[k])
    return frames


def _frames_gota():
    """Una gota de condensació que es forma sota el tub de gasoil, cau a terra i hi fa una rodoneta."""
    base = _base_llum()
    gx, gz = 389, ZW - 7
    top = _y(61) - 4
    seq = [('f', 0)] * 3 + [('f', 1)] * 3 + [('f', 2)] * 2 + [('f', 3)] * 2
    y, v = top, 0.0
    while y > 0:
        seq.append(('c', y))
        v += 2.6
        y -= v
    seq += [('s', 0), ('r', 1), ('r', 2), ('r', 3), ('r', 4), ('r', 5)] + [('n', 0)] * 40
    gu, gv = _proj((gx, top, gz))
    fu, fv = _proj((gx, 0, gz))
    area = (int(gu) - 14, int(gv) - 3, int(gu) + 15, int(fv) + 6)
    empty = Image.new('RGBA', base.size, (0, 0, 0, 0))
    frames = []
    for kind, val in seq:
        if kind == 'n':
            frames.append(empty)
            continue
        cv = Canvas(light=LIGHT, img=base.copy())
        if kind == 'f':                                             # la gota s'infla sota el tub
            for k in range(val + 1):
                cv.flat(gu, gv + k, mix(cv.get(gu, gv + k), (150, 190, 185), 0.7))
        elif kind == 'c':                                           # cau (amb una cua)
            u, v = _proj((gx, val, gz))
            cv.flat(u, v, (190, 222, 216))
            cv.flat(u, v + 1, (170, 205, 200))
            cv.flat(u, v - 1, mix(cv.get(u, v - 1), (130, 170, 165), 0.5))
        elif kind == 's':                                           # l'esquitx
            for dx, dy in ((-2, -2), (2, -2), (-3, -1), (3, -1), (0, -3)):
                cv.flat(fu + dx, fv + dy, (180, 215, 210))
        else:                                                       # la rodoneta que s'eixampla (al terra)
            for a in range(0, 360, 18):
                P = (gx + math.cos(math.radians(a)) * val * 2.6, 0, gz + math.sin(math.radians(a)) * val * 2.6)
                u, v = _proj(P)
                if 0 <= u < W and 0 <= v <= BOTTOM:
                    cv.flat(u, v, mix(cv.get(u, v), (150, 190, 185), 0.6 - val * 0.08))
        frames.append(sota.fast_diff(cv.img, base, area))
    return frames


ANIMS = {'llum': {'frames': _frames_llum, 'frameDuration': 110},
         'gota': {'frames': _frames_gota, 'frameDuration': 80}}


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


def _escala_a(v):
    """L'escala d'un personatge amb els peus a la y de pantalla `v` (al terra, la profunditat només depèn de v)."""
    lo, hi = -300.0, 2000.0
    for _ in range(60):
        z = (lo + hi) / 2
        if CAM.projecta((250, 0, z))[1] > v:
            lo = z
        else:
            hi = z
    return CAM.escala((250, 0, (lo + hi) / 2))


def _cantons_bidons(marge):
    xs = [b[0] for b in BIDONS]
    zs = [b[1] for b in BIDONS]
    return [(min(xs) - 16 - marge, min(zs) - 12 - marge), (max(xs) + 16 + marge, min(zs) - 12 - marge),
            (max(xs) + 16 + marge, max(zs) + 16 + marge), (min(xs) - 16 - marge, max(zs) + 16 + marge)]


# Capes del davant: el primer pla (sempre davant) i els bidons (qui hi passa per darrere, hi queda darrere).
FRONT = [
    {'id': 'davant', 'mask': _amo({'primer_pla'}), 'baseline': 999, 'zIndex': 20},
    {'id': 'davant_bidons', 'mask': _amo({'bidons'}), 'baseline': _p(BIDONS[2][0], BIDONS[2][1] - 6)[1], 'zIndex': 20},
]

# El terra on es camina (al món): de la vora de l'esquerra fins al peu de l'escala, de la paret fins on el personatge
# arriba a 1,2 (més a prop, el terra és primer pla).
WALK_MON = [(-20, ZW - 16), (ESC[0] - 8, ZW - 16), (ESC[0] - 8, ESC[2] - 6), (300, 20), (60, 32), (-20, 52)]
_WALK = []
for _x, _z in WALK_MON:                           # (retallat a la vora de l'esquerra de la pantalla)
    _u, _v = _p(_x, _z)
    if not _WALK or _WALK[-1] != (max(0, _u), _v):
        _WALK.append((max(0, _u), _v))
_V_FONS, _V_PROP = min(v for _, v in _WALK), max(v for _, v in _WALK)


def _porta(fx0, fy0, fx1):
    return _rect_mon((fx0 - 3, _y(fy0) + 4, ZW), (fx1 + 3, 0, ZW))


GEOMETRIA = {
    'things': {
        'porta_camarot': {'rect': _porta(*PL.CAMAROT[:3]), 'walk': _p((PL.CAMAROT[0] + PL.CAMAROT[2]) / 2, ZW - 24)},
        'porta_maquines': {'rect': _porta(*PL.MAQUINES[:3]), 'walk': _p((PL.MAQUINES[0] + PL.MAQUINES[2]) / 2, ZW - 24)},
        'repetidor': {'rect': _rect_mon((99, _y(148), ZW), (141, _y(185), ZW)), 'walk': _p(120, ZW - 26)},
        # Només el tros de les petjades que es veu: la resta queda darrere els bidons (que si no, es quedaven el rètol).
        'petjades': {'rect': _rect_mon((150, 0, ZW - 20), (186, 0, ZW - 20), (150, 0, ZW - 56), (186, 0, ZW - 56)),
                     'walk': _p(150, ZW - 70)},
        'porta_pallol': {'rect': _porta(*PL.PALLOL[:3]), 'walk': _p((PL.PALLOL[0] + PL.PALLOL[2]) / 2, ZW - 24)},
        'escotilla': {'rect': _rect_mon((HATCH[0], 0, HATCH[2]), (HATCH[1], 0, HATCH[2]), (HATCH[0], 0, HATCH[3]),
                                        (HATCH[1], 0, HATCH[3])),
                      'walk': _p((HATCH[0] + HATCH[1]) / 2, HATCH[2] - 18)},
        'escala': {'rect': _rect_mon((ESC[0] - 4, 0, ESC[2]), (ESC[1], 0, ESC[2]), (ESC[0] - 4, HW, ESC[3]),
                                     (ESC[1], HW, ESC[3]), (ESC[0], 60, ESC[2])),
                   'walk': _p(ESC[0] - 16, ESC[2] + 14)},
    },
    'spawns': {'iri': _p(200, 110), 'vet': _p(ESC[0] - 26, ESC[2] + 30)},
    'walkable': _WALK,
    'forats': [[_p(x, z) for x, z in _cantons_bidons(4)]],
    'floorSquash': 0.42,                           # (la càmera, picada: el terra es veu aixafat)
    # L'ombra de contacte: la llum dominant és la que baixa per l'escala (el punt del terra sota el forat).
    'characterShadow': {'enabled': True, 'color': '#040806', 'alpha': 0.45, 'squash': 0.4, 'core': 0.6,
                        'light': {'x': _p(FORAT[0] + 20, FORAT[2] - 10)[0], 'y': _p(FORAT[0] + 20, FORAT[2] - 10)[1],
                                  'stretch': 0.6, 'reach': 220}},
    'regions': [{'id': 'perspectiva', 'active': True, 'scaleEnabled': True, 'scaleWalkSpeed': True,
                 'scaleTop': round(_escala_a(_V_FONS - 2), 3), 'scaleBottom': round(_escala_a(_V_PROP + 2), 3),
                 'points': [(0, _V_FONS - 2), (W - 1, _V_FONS - 2), (W - 1, _V_PROP + 2), (0, _V_PROP + 2)]}],
    # la llum de la sala sobre els personatges, en temps d'execució
    'characterLights': {
        'ambient': '#7a8a7e',                                                           # passadís verd i fosc
        'lights': [
            *[{'x': _p(x, z, HW - 13)[0], 'y': _p(x, z, HW - 13)[1], 'radius': 190, 'color': '#ffecbe',
               'intensity': 0.7} for x, z in LAMPS],                                    # els llums de gàbia
            {'x': _p(FORAT[0] + 20, FORAT[2], HW)[0], 'y': _p(FORAT[0] + 20, FORAT[2], HW)[1], 'radius': 220,
             'color': '#ffecbe', 'intensity': 1.0},                                     # la coberta, per l'escala
        ],
    },
}

# Coses per mirar (tasca 061), en píxels de pantalla: el tauler de suro, l'extintor, els bidons i les caixes vermelles.
GEOMETRIA['things'].update({
    'suro': {'rect': (102, 77, 136, 120), 'walk': (120, 170)},
    'extintor': {'rect': (222, 82, 239, 136), 'walk': (254, 167)},
    'bidons': {'rect': (42, 150, 139, 220), 'walk': (150, 200)},
    'caixes': {'rect': (495, 87, 525, 145), 'walk': (440, 180)},
})
