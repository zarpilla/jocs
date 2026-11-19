"""
Portada, a 640×360 (pantalla sencera, sense barra de verbs). EN 3D (hd640/tres_d.py), a 1×; el dibuix pla de
sempre és a portada_pla_comu.py (el títol, el tall de llum) i les textures surten dels pròlegs.

Dos plans de cinema partits pel tall en diagonal que brilla (el passat a l'esquerra, el present a la dreta):
  - **la fàbrica de ferro-9**, de nit, des de l'altra riba del canal i arran d'aigua (contrapicat): la nau de la
    façana (el frontó, la roda dentada, el portal dels forns encès) a prop, en 3/4, i la nau llarga que fuig cap a
    l'esquerra; les xemeneies treuen fum, el moll amb el fanal i la gavarra fa la diagonal que porta l'ull cap al
    portal, i el canal ho reflecteix tot. Primer pla: la barana de ferro de la riba, a contrallum, tallada per baix;
  - **La Gavina**, en 3/4 des de dalt (l'estació de proleg_gavina.py, amb una altra càmera), i la Terra enorme a
    baix a la dreta.
El títol «FERRO-9», de metall, a dalt (el cel fred a dalt i el foc a baix). Els botons de la GUI `portada` van a
220..420 × 224..328 i la versió a baix a la dreta: allà no hi ha res important (el canal, enfosquit) i no s'hi anima
res. Els crèdits (credits.py) fan servir aquest fons sense el títol.

El món de la fàbrica: x a la dreta (les x del dibuix pla de la façana), y amunt (0 = el moll), z endavant (0 = la
façana); 1 unitat = 1 píxel del dibuix pla del pròleg.
"""
import hd640  # noqa: F401  (abans que cap hd.rooms: posa la llibreria a 640×360)

import math
from functools import lru_cache

from PIL import Image

from hd.pix import Canvas, Light, W, H, hr, mix, BRICK, GLASS, NAVY, SIL
from hd640.rooms import proleg_fabrica_pla_comu as fab
from hd640.rooms import proleg_gavina as ga
from hd640.rooms.portada_pla_comu import title, glint, sparkle, seam_x
from hd640.rooms.proleg_gavina_pla_comu import espai, terra, vinyeta, ambient_frames
from hd640.tres_d import Camera, Escena, Llum

LIGHT = Light(ambient=0.0, vignette=None, floor_fade=None)

# On van els botons de la GUI (x0, y0, x1, y1), i el rectangle on no s'hi anima res (amb la versió, a baix a la dreta)
BOTONS = (220, 224, 420, 328)
QUIET = (210, 214, 430, 338)

QY = fab.QY                              # el moll, al dibuix pla
WL = -12.0                               # el nivell de l'aigua del canal
QD = 40.0                                # l'amplada del moll (de la façana a la vora)
BANK = -215.0                            # la riba d'on mirem
A_D, B_D = 130.0, 180.0                  # el fons de les dues naus


def _y(fy):
    """y del dibuix pla → y del món."""
    return QY - fy


def _mira(pos, cap, f, centre):
    d = [cap[i] - pos[i] for i in range(3)]
    return Camera(pos=pos, yaw=math.atan2(d[0], d[2]), pitch=math.atan2(-d[1], math.hypot(d[0], d[2])), f=f,
                  centre=centre)


CAM_F = _mira((680.0, 20.0, -260.0), (350.0, 80.0, 0.0), 230.0, (112, 190))


def _mirall(cam):
    """La càmera reflectida a l'aigua (vegeu `_reflex`)."""
    x, y, z = cam.pos
    return Camera(pos=(x, 2 * WL - y, z), yaw=cam.yaw, pitch=-cam.pitch, f=cam.f, centre=cam.centre)


# ─── Les textures (el dibuix pla del pròleg de la fàbrica) ──────────────────

@lru_cache(maxsize=None)
def _tex_fabrica():
    """La fàbrica sola, sobre transparent (amb les seves llums), sense el rètol del teulat."""
    cv = Canvas(light=fab.LIGHT, transparent=True)
    fab.factory(cv, retol=False)
    return cv.img


@lru_cache(maxsize=None)
def _tex_moll():
    cv = Canvas(light=fab.LIGHT, transparent=True)
    fab.quay(cv)
    return cv.img


@lru_cache(maxsize=None)
def _tex_gavarra():
    cv = Canvas(light=fab.LIGHT, transparent=True)
    fab.barge(cv)
    return cv.img


@lru_cache(maxsize=None)
def _tex_barana():
    cv = Canvas(transparent=True)
    fab.railing(cv)
    return cv.img


def _maons(s, t, P, base=2.2, seed=3):
    """Maó procedural (s, t en unitats): filades de 4 i peces de 10, amb el morter."""
    row = int(t / 4)
    x = s + (row % 2) * 5
    lv = base + (hr(int(x / 10), row, seed) - 0.5) * 0.6
    if t % 4 > 3.1 or x % 10 > 9.1:
        lv -= 1.0
    return lv


# ─── L'escena de la fàbrica ─────────────────────────────────────────────────

B_X0, B_X1, B_TOP, B_PEAK = fab.B_X0, fab.B_X1, fab.B_TOP, fab.B_PEAK
A_X0, A_X1, A_TOP = fab.A_X0, fab.A_X1, fab.A_TOP
CHIMS = ((61, 53, A_D * 0.55, 9), (292, 69, A_D * 0.55, 8), (579, 45, B_D * 0.7, 9))   # x, y de la boca (pla), z, r
LAMP = (315.0, 0.0, -QD + 6)


def edificis(e):
    """Les dues naus, les xemeneies i el que hi ha al moll (el que es reflecteix al canal)."""
    tf = _tex_fabrica()
    # les xemeneies (darrere les naus)
    for x, fy, z, r in CHIMS:
        e.tub('xemeneia', (x, _y(fy), z), (x, _y(A_TOP) - 20, z), r, BRICK, 2.6, llum_dir=(0.8, 0.3))
        e.tub('xemeneia', (x, _y(fy) + 1, z), (x, _y(fy) - 4, z), r + 3, BRICK, 3.2, llum_dir=(0.8, 0.3))
    # nau A: el llanternó del teulat (la cara de davant, del dibuix pla) i la façana
    yl0, yl1 = _y(103), _y(89)
    e.quad('llanterno', (59, yl1, 50), (298, yl1, 50), (298, yl0, 50), (59, yl0, 50), tex=(tf, (59, 89, 298, 103)))
    e.quad('teulat', (A_X0 - 5, _y(A_TOP) + 2, 0), (A_X1 + 5, _y(A_TOP) + 2, 0),
           (A_X1 + 5, _y(A_TOP) + 40, A_D * 0.5), (A_X0 - 5, _y(A_TOP) + 40, A_D * 0.5), ramp=fab.SLATE, lvl=2.0)
    e.quad('facana_a', (A_X0 - 3, _y(A_TOP - 1), 0), (A_X1 + 3, _y(A_TOP - 1), 0), (A_X1 + 3, 0, 0),
           (A_X0 - 3, 0, 0), tex=(tf, (A_X0 - 3, A_TOP - 1, A_X1 + 3, QY)))
    # nau B: la façana amb el frontó (el triangle, retallat), el costat que fuig cap a la riba, i la teulada
    px_, py_ = B_PEAK
    top = py_ - 9

    def fronto(s, t):
        x, y = B_X0 - 5 + s, top + t
        if y >= B_TOP + 2:
            return True
        k = (x - px_) / ((B_X1 + 5 - px_) if x > px_ else (px_ - B_X0 + 5))
        return y >= py_ - 8 + abs(k) * (B_TOP + 2 - py_ + 8) or (abs(x - px_) <= 3 and y >= py_ - 8)
    e.quad('facana_b', (B_X0 - 5, _y(top), 0), (B_X1 + 5, _y(top), 0), (B_X1 + 5, 0, 0), (B_X0 - 5, 0, 0),
           tex=(tf, (B_X0 - 5, top, B_X1 + 5, QY)), forma=fronto)
    yb = _y(B_TOP)
    e.quad('costat_b', (B_X1, yb, 0), (B_X1, yb, B_D), (B_X1, 0, B_D), (B_X1, 0, 0), ramp=BRICK,
           lvl=lambda s, t, P: _maons(s, t, P, 1.8) - t * 0.004)
    for i in range(4):                                             # finestrals del costat (dos d'encesos)
        z0 = 24 + i * 40
        for y0, h in ((_y(139 + 35), 35), (_y(192 + 35), 35)):
            lit = (i, y0 > 60) in ((0, True), (2, False), (1, False))
            e.quad('costat_b', (B_X1 + 0.5, y0 + h, z0), (B_X1 + 0.5, y0 + h, z0 + 16), (B_X1 + 0.5, y0, z0 + 16),
                   (B_X1 + 0.5, y0, z0), ramp=GLASS if lit else NAVY,
                   lvl=(lambda s, t, P: 3.4 - t * 0.04 - (1.4 if abs(s - 8) < 0.7 or abs(t - 12) < 0.6 else 0))
                   if lit else 1.2)
    e.quad('teulat', (B_X1 + 6, yb - 2, -2), (px_, _y(py_), -2), (px_, _y(py_), B_D), (B_X1 + 6, yb - 2, B_D),
           ramp=fab.SLATE, lvl=2.2)
    # el moll: la vora de pedra, els noràis i el fanal (sprites del dibuix pla)
    tm = _tex_moll()
    for bx in (80, 224, 389, 560):
        e.sprite('norai', tm.crop((bx - 1, QY - 9, bx + 6, QY)), (3.5, 9), (bx + 2, 0, -QD + 5))
    lx = 315
    e.sprite('fanal', tm.crop((lx - 5, 187, lx + 7, QY)), (5.5, QY - 187), LAMP)


def _terra_moll(s, t, P):
    """Les llambordes del moll: fileres de 6 i peces de 9, amb el morter."""
    row = int(P[2] / 6)
    x = P[0] + (row % 2) * 4.5
    lv = 1.7 + (hr(int(x / 9), row, 11) - 0.5) * 0.6
    if P[2] % 6 > 5.2 or x % 9 > 8.2:
        lv -= 0.8
    return lv


def escena_fabrica(cv, cam):
    """La fàbrica, el moll, el canal (sense el reflex) i la riba d'on mirem, sobre el cel ja pintat."""
    e = Escena(cv, cam, llums=[Llum((476, 22, -6), 150, 2.4), Llum((LAMP[0], 50, LAMP[2]), 90, 1.8)])
    edificis(e)
    # el terra del moll i el mur de la vora
    e.quad('moll', (-400, 0, 0), (B_X1 + 400, 0, 0), (B_X1 + 400, 0, -QD), (-400, 0, -QD), ramp=fab.STONE,
           lvl=_terra_moll)
    tm = _tex_moll()
    for x0 in range(-640, 1280, 640):
        e.quad('mur', (x0, 0, -QD), (x0 + 640, 0, -QD), (x0 + 640, WL, -QD), (x0, WL, -QD),
               tex=(tm, (0, QY, 639, QY + 11)))
    # el canal (el reflex s'hi pinta després)
    e.quad('aigua', (-3000, WL, -QD), (3000, WL, -QD), (3000, WL, BANK), (-3000, WL, BANK), ramp=fab.WATER,
           lvl=lambda s, t, P: 1.3 + (0.6 if hr(int(P[0] / 9), int(P[2] / 2), 4) > 0.86 else 0))
    # la gavarra, amarrada davant de la nau llarga (el dibuix pla, de costat, en un pla paral·lel al moll)
    tg = _tex_gavarra()
    yt = QY + 9
    e.quad('gavarra', (88, WL + 22, -QD - 12), (266, WL + 22, -QD - 12), (266, WL - 3, -QD - 12),
           (88, WL - 3, -QD - 12), tex=(tg, (88, yt - 22, 266, yt + 3)))
    # la riba d'on mirem, i la barana a contrallum (el primer pla)
    e.quad('riba', (-3000, 0, BANK), (3000, 0, BANK), (3000, 0, BANK - 400), (-3000, 0, BANK - 400), ramp=SIL,
           lvl=0.6)
    tb = _tex_barana()
    for x0 in range(-200, 1400, 220):
        e.quad('barana', (x0, 14, BANK - 6), (x0 + 220, 14, BANK - 6), (x0 + 220, 0, BANK - 6), (x0, 0, BANK - 6),
               tex=(tb, (0, 303, 219, 342)))
    # la llum dels forns i del fanal, escampada pel moll (càlida)
    e.claror((420, 0.2, 0), (532, 0.2, 0), (560, 0.2, -QD), (392, 0.2, -QD), (255, 150, 70),
             lambda s, t: 0.45 * max(0.0, 1 - abs(s - 56) / 70) * (1 - t / 55))
    e.claror((LAMP[0] - 40, 0.2, 0), (LAMP[0] + 40, 0.2, 0), (LAMP[0] + 40, 0.2, -QD), (LAMP[0] - 40, 0.2, -QD),
             (255, 200, 110), lambda s, t: 0.35 * max(0.0, 1 - math.hypot(s - 40, t - (QD - 6)) / 40))
    return e


@lru_cache(maxsize=None)
def _reflex():
    """El reflex de les naus al canal: l'escena vista per la càmera reflectida, capgirada."""
    cv = Canvas(transparent=True)
    cv.S = 1
    cam = _mirall(CAM_F)
    edificis(Escena(cv, cam))
    return cv.img.transpose(Image.Transpose.FLIP_TOP_BOTTOM), 2 * cam.centre[1] - (H - 1)


def canal(cv, e, t=0.0):
    """El reflex trencat per les ones (com al pla del pròleg), només als píxels de l'aigua."""
    ref, dy = _reflex()
    R = ref.load()
    ph = 2 * math.pi * t
    P = cv.P
    idx = {i for i, s in enumerate(e.ids) if s == 'aigua'}
    v0 = int(e.caixes['aigua'][1])
    for y in range(max(0, v0), H):
        depth = max(0.0, (y - v0) / 4)
        for x in range(W):
            if e.amo[y * W + x] not in idx:
                continue
            wob = math.sin(y * 0.6 + math.sin(x * 0.05 + ph) * 1.5 - ph * 2) * (1 + depth * 0.06)
            sy = y - dy
            sx = int(x + wob)
            if not (0 <= sy < H and 0 <= sx < W):
                continue
            if math.sin(y * 1.2 + math.sin(x / 10 + y * 0.7 - ph) * 2 - ph * 3) <= -0.25 - depth / 140:
                continue                                          # el reflex surt a franges
            c = R[sx, sy]
            if not c[3]:
                continue
            k = max(0.0, 0.6 - depth / 260)
            lum = sum(c[:3]) / 3
            o = P[x, y]
            P[x, y] = mix(o, c, min(1, k * 1.1) if lum > 70 else k * 0.5) + (255,)
    # la vora fosca sota el mur
    return cv


def fum(cv, cam, t=0.0):
    src = []
    for x, fy, z, r in CHIMS:
        u, v, _ = cam.projecta((x, _y(fy) + 2, z))
        src.append((u, v, 120 + 100 * cam.escala((x, 0, z))))
    fab.smoke(cv, src, t=t)


# ─── El costat de La Gavina ─────────────────────────────────────────────────

CAM_G = ga._mira((-220.0, -110.0, -380.0), (0.0, 0.0, 0.0), 470.0, (500, 170))
TERRA = (667, 512, 248)


@lru_cache(maxsize=None)
def _fabrica_quieta():
    """El costat de la fàbrica sense res que es mogui: el cel, la ciutat, l'escena 3D. → (imatge, Escena)"""
    cv = Canvas(light=fab.LIGHT)
    fab.sky(cv)
    # la ciutat de l'altra banda, a l'horitzó de la càmera
    c = Canvas(transparent=True)
    fab.city(c)
    hz = CAM_F.centre[1] - CAM_F.f * math.tan(CAM_F.pitch)
    cv.img.alpha_composite(c.img.crop((0, 150, W, QY)), (0, round(hz) - (QY - 150) + 6))
    cv.P = cv.img.load()
    cv.S = 1
    e = escena_fabrica(cv, CAM_F)
    return cv.img.copy(), e


def fabrica(t=0.0):
    img, e = _fabrica_quieta()
    cv = Canvas(light=fab.LIGHT, img=img.copy())
    canal(cv, e, t)
    fum(cv, CAM_F, t)
    return cv


@lru_cache(maxsize=None)
def _nau():
    return ga.nau_img(CAM_G)


def gavina_costat(cv, t=0.0):
    espai(cv, x0=240, t=t)
    terra(cv, *TERRA, x0=240, t=t)
    img, e = _nau()
    cv.img.alpha_composite(img)
    ga.llums(cv, CAM_G, t, e)


def bg(cv, t=0.0, titol=True):
    """`t` (0..1): moment del bucle de l'animació de fons (amb 0, el fons quiet). Amb `titol=False`, sense el títol
    ni la zona fosca dels botons (els crèdits)."""
    gavina_costat(cv, t)
    F = fabrica(t).img.load()
    P = cv.P
    for y in range(H):
        sx = seam_x(y)
        for x in range(0, min(W, math.ceil(sx) + 1)):
            if x < sx - 0.5:
                P[x, y] = F[x, y]
    # el tall: una esquerda de llum entre els dos temps
    for y in range(H):
        sx = seam_x(y)
        cv.flat(round(sx), y, (236, 240, 255))
        cv.flat(round(sx) - 1, y, mix(cv.get(round(sx) - 1, y), (255, 190, 110), 0.6))
        cv.flat(round(sx) + 1, y, mix(cv.get(round(sx) + 1, y), (120, 200, 255), 0.6))
        cv.flat(round(sx) - 2, y, mix(cv.get(round(sx) - 2, y), (255, 170, 90), 0.25))
        cv.flat(round(sx) + 2, y, mix(cv.get(round(sx) + 2, y), (110, 190, 255), 0.25))
    for y in range(0, H, 4):
        sx = seam_x(y)
        cv.glow(sx - 4, y, 9, (255, 170, 90), 0.12)
        cv.glow(sx + 4, y, 9, (110, 190, 255), 0.12)
    if not titol:
        vinyeta(cv, 0.5)
        return
    # fosc a dalt (on va el títol) i a baix al mig (on van els botons)
    cv.darken(0, 0, W - 1, 120, lambda x, y: 0.45 * (1 - y / 120), dither=False)
    cv.darken(165, 200, 475, H - 1, lambda x, y: 0.5 * max(0.0, 1 - math.hypot((x - 320) / 150, (y - 276) / 70) ** 2),
              dither=False)
    M = title(cv, 'FERRO-9', W / 2, 19, m=11, depth=5)
    glint(cv, M, t)
    sparkle(cv, min(p[0] for p in M) + 4, 21, 6 if 0.29 <= t < 0.36 else 5)
    xs = [p[0] for p in M]
    sparkle(cv, max(xs) - 4, 53, 6 if 0.58 <= t < 0.62 else 5 if 0.62 <= t < 0.7 else 4)
    vinyeta(cv, 0.5)


PROPS = {}

# Res d'animació sota els botons de la GUI (220..420 × 224..328), amb marge
ANIMS = {'ambient': {'frames': lambda: ambient_frames(bg, LIGHT, mask=QUIET), 'frameDuration': 130}}
