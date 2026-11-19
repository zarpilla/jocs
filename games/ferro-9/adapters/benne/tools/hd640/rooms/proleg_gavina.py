"""
Pròleg 1 · L'espai, a 640×360. EN 3D (hd640/tres_d.py), a 1×; el dibuix pla de sempre és a
proleg_gavina_pla_comu.py (l'espai, la Terra, la Lluna i la Gavina plana que fan servir altres sales).

Un pla de cinema a tocar de La Gavina, que plana sobre la Terra com una gavina (la càmera, una mica per sobre):
  - l'**ala de babord**, a prop, entra per baix a l'esquerra, tallada per la vora: els panells solars grossos i la
    biga de gelosia fugen en diagonal fins al colze i el cos de l'estació (la línia que porta l'ull);
  - el **cos**, a la dreta, en 3/4: el tambor amb costelles i l'anell de finestres (una de sola encesa), la tapa i
    la cúpula, el con de sota, la tija i el **moll de càrrega** amb les ratlles d'avís i les llums de guia; la
    resclosa mira al sol, i les aletes radiadores, a l'ombra;
  - l'**ala d'estribord**, que fuig petita cap amunt, amb el llum verd a la punta;
  - la **Terra**, enorme a baix a la dreta, i la Lluna petita a dalt a l'esquerra. El sol ve de l'esquerra; la
    Terra il·lumina de blau la panxa de l'estació.
La llançadora (`llancadora_puja`) surt de darrere la Terra, petita i lluny, i s'acosta fins sota el moll.

L'estació es descriu al món en les unitats del dibuix pla (amb s = 1, l'envergadura fa 316): x a la dreta (l'ala
de babord és la de -x, cap al sol), y amunt, z endavant; el cos és a l'origen. `estacio(e)` la munta en una Escena
qualsevol: la portada i els crèdits la fan servir amb una altra càmera (`nau_img`).
"""
import hd640  # noqa: F401  (abans que cap hd.rooms: posa la llibreria a 640×360)

import math
from functools import lru_cache

from hd.pix import Canvas, Light, W, H, hr, mix, STEEL, PANEL, WARN
from hd640.rooms.proleg_gavina_pla_comu import espai, terra, lluna, vinyeta, ambient_frames, llancadora, SOLAR
from hd640.tres_d import Camera, Escena, Llum

LIGHT = Light(ambient=0.0, vignette=None, floor_fade=None)

# ─── L'estació, al món ──────────────────────────────────────────────────────

B = 1.3                                  # el cos, una mica més gros que les ales (com al dibuix pla)
RX = 22 * B                              # radi del tambor
TOP, BOT = 6 * B, -8 * B                 # la tapa i el ventre del tambor
CB = -17 * B                             # la punta del con de sota
DR = 11 * B                              # la cúpula
STEM = (-14 * B, -33 * B, 3 * B)         # la tija: de, fins a, radi
PLAT = (16 * B, -33 * B, -39 * B, 11 * B)   # la plataforma: mig ample, dalt, baix, mig fons
DOCK = (6.0, PLAT[2] - 7.0, -PLAT[3] - 6.0)   # on queda la llançadora atracada (sota el cantell de davant del moll)
ANT = (5 * B, 30 * B)                    # l'antena: x, alçada de la punta
WINDOW_Y = -1 * B                        # l'anell de finestres
LIT_A = -1.25                            # l'angle (des de -z cap a +x) de l'única finestra encesa

# les ales (x, y del dibuix pla amb y amunt), i la corda de cada punt
WING = ((22, 6, 34), (86, 40, 28), (158, 14, 20))
CHORD_DIR = (0.0, -0.26, 0.966)           # la corda dels panells: enrere i una mica avall (la «gavina»)

SUN_POS = (-60000.0, 16000.0, -26000.0)  # el sol, lluny a l'esquerra (una mica davant i amunt)
EARTH_POS = (9000.0, -26000.0, -9000.0)  # la Terra, a sota a la dreta: només fa una mica de llum blava


def _llums():
    return [Llum(SUN_POS, 400000.0, 5.0, power=1.0), Llum(EARTH_POS, 400000.0, 1.0, power=1.0)]


_sl = math.sqrt(sum(c * c for c in SUN_POS))
SUN_DIR = tuple(c / _sl for c in SUN_POS)


def _sol(n):
    """Més contrast que la llum difusa: una lluentor on la cara mira de ple al sol, i ombra on li gira l'esquena."""
    nl = math.sqrt(sum(c * c for c in n)) or 1.0
    d = sum(a * b for a, b in zip(n, SUN_DIR)) / nl
    return 1.6 * max(0.0, d) ** 6 - 0.9 * max(0.0, -d)


# l'acer de les cares que miren avall: la Terra les il·lumina de blau
STEEL_T = [mix(c, (50, 110, 220), 0.22 + 0.04 * i) for i, c in enumerate(STEEL)]
PANEL_T = [mix(c, (50, 110, 220), 0.2 + 0.04 * i) for i, c in enumerate(PANEL)]


def _cil(e, sid, r0, r1, y0, y1, n, ramp, lvl, a0=0.0, a1=2 * math.pi):
    """Un tronc de con vertical (r0 a y0, r1 a y1) fet de `n` cares; `lvl(a, s, t, P)` (a = l'angle de la cara)."""
    for i in range(n):
        aa, ab = a0 + (a1 - a0) * i / n, a0 + (a1 - a0) * (i + 1) / n
        # P0 a dalt a l'esquerra, mirant la cara des de fora
        P0 = (r1 * math.sin(aa), y1, -r1 * math.cos(aa))
        P1 = (r1 * math.sin(ab), y1, -r1 * math.cos(ab))
        P2 = (r0 * math.sin(ab), y0, -r0 * math.cos(ab))
        P3 = (r0 * math.sin(aa), y0, -r0 * math.cos(aa))
        am = (aa + ab) / 2
        brill = _sol((math.sin(am), (r0 - r1) / max(1e-3, y1 - y0), -math.cos(am)))
        f = (lambda s, t, P, a=aa, b=brill: lvl(a, s, t, P) + b) if callable(lvl) else lvl + brill
        e.quad(sid, P0, P1, P2, P3, ramp=ramp, lvl=f)


def _disc(e, sid, cx, cy, cz, r, ramp, lvl, sota=False):
    """Un disc horitzontal (la tapa del tambor, la plataforma vista de sota)."""
    if sota:
        e.quad(sid, (cx - r, cy, cz - r), (cx + r, cy, cz - r), (cx + r, cy, cz + r), (cx - r, cy, cz + r),
               ramp=ramp, lvl=lvl, forma=lambda s, t: (s - r) ** 2 + (t - r) ** 2 <= r * r)
    else:
        e.quad(sid, (cx - r, cy, cz + r), (cx + r, cy, cz + r), (cx + r, cy, cz - r), (cx - r, cy, cz - r),
               ramp=ramp, lvl=lvl, forma=lambda s, t: (s - r) ** 2 + (t - r) ** 2 <= r * r)


def _ala(e, sign):
    """Una ala: dos trams de panells (de l'espatlla al colze i del colze a la punta) amb la biga a la vora d'atac."""
    pts = [(sign * x, y, 0.0, c) for x, y, c in WING]
    cd = CHORD_DIR
    babord = sign < 0
    for (xa, ya, za, ca), (xb, yb, zb, cb), nu in ((pts[0], pts[1], 12), (pts[1], pts[2], 15)):
        A, Bp = (xa, ya, za), (xb, yb, zb)
        Ad = (xa + cd[0] * ca, ya + cd[1] * ca, za + cd[2] * ca)
        Bd = (xb + cd[0] * cb, yb + cd[1] * cb, zb + cd[2] * cb)
        L = math.dist(A, Bp)
        cell = L / nu

        def panell(s, t, P, L=L, ca=ca, cb=cb, cell=cell, xa=xa):
            k = s / L
            ch = ca + (cb - ca) * k
            v = t / max(1e-3, (ca + cb) / 2) * 6                   # 6 cel·les de través
            fu, fv = s % cell, v % 1
            if t < 0.9 or t > ch - 0.7 or s < 0.8 or s > L - 0.8:
                return 4.2                                          # el marc
            if fu < 0.6 or fv < 0.12:
                return 2.6                                          # les juntes entre cel·les
            lv = 2.4 + (hr(int(s / cell), int(v), int(xa)) - 0.5) * 0.5 - (v % 1) * 0.5
            if fv < 0.3:
                lv += 0.5                                           # el cantell de dalt de la cel·la
            if abs(fu - cell / 2) < 0.35 and cell > 5:
                lv -= 0.7                                           # el fil conductor del mig
            return lv
        # la cara de dalt (cèl·lules) i la de sota (l'estructura grisa)
        # (les dues cares són de cèl·lules: la de sota, més fosca, amb les costelles de l'estructura)
        sota = lambda s, t, P, f=panell: f(s, t, P) - 1.1 - (0.8 if int(t / 8) != int((t - 0.7) / 8) else 0)
        if sign < 0:
            e.quad('ala', Bp, A, Ad, Bd, ramp=SOLAR, lvl=lambda s, t, P, f=sota, L=L: f(L - s, t, P))
            e.quad('ala', A, Bp, Bd, Ad, ramp=SOLAR, lvl=panell)
        else:
            e.quad('ala', A, Bp, Bd, Ad, ramp=SOLAR, lvl=sota)
            e.quad('ala', Bp, A, Ad, Bd, ramp=SOLAR, lvl=lambda s, t, P, f=panell, L=L: f(L - s, t, P))
    # la biga de gelosia: dos cordons i diagonals en ziga-zaga (a sobre de la vora d'atac)
    for (xa, ya, za, _), (xb, yb, zb, _) in ((pts[0], pts[1]), (pts[1], pts[2])):
        up, lo = 4.0, 1.2
        e.cable('biga', [(xa, ya + up, za), (xb, yb + up, zb)], STEEL, 6.4 if babord else 4.6, gruix=1.3)
        e.cable('biga', [(xa, ya + lo, za - 1.5), (xb, yb + lo, zb - 1.5)], STEEL, 4.0 if babord else 3.0, gruix=1.0)
        n = max(2, int(math.dist((xa, ya), (xb, yb)) / 5))
        for i in range(n):
            ka, kb = i / n, (i + 1) / n
            Pa = (xa + (xb - xa) * ka, ya + (yb - ya) * ka, za)
            Pb = (xa + (xb - xa) * kb, ya + (yb - ya) * kb, zb)
            if i % 2:
                Pa, Pb = (Pa[0], Pa[1] + up, Pa[2]), (Pb[0], Pb[1] + lo, Pb[2] - 1.5)
            else:
                Pa, Pb = (Pa[0], Pa[1] + lo, Pa[2] - 1.5), (Pb[0], Pb[1] + up, Pb[2])
            e.cable('biga', [Pa, Pb], STEEL, 4.6 if babord else 3.2, gruix=0.6)
    # el colze (una articulació) i l'espatlla
    x, y, _, _ = pts[1]
    e.caixa('colze', x - 3.5, x + 3.5, y - 2.5, y + 4.5, -3.5, 3.5, STEEL, 4.2)
    x, y, _, _ = pts[0]
    e.caixa('espatlla', x - 4.5 if sign > 0 else x - 1, x + 1 if sign > 0 else x + 4.5, y - 4, y + 5, -5, 5,
            STEEL, 3.8)


def _tambor_lvl(a, s, t, P):
    """El costat del tambor: les costelles i l'anell de finestres (fosques: tothom dorm)."""
    lv = 3.2
    w = 2 * math.pi * RX / 36
    if s < 0.9 or s > w - 0.5:
        lv -= 1.3                                                   # costella
    elif s < 1.6:
        lv += 0.6                                                   # el cantell de la costella
    y = P[1]
    if abs(y - WINDOW_Y) < 1.6 and 1.8 < s < w - 1.2:
        return 0.2 if y > WINDOW_Y - 0.6 else -0.4                  # finestra fosca
    if abs(y - TOP) < 1.0 or abs(y - BOT) < 1.0:
        lv -= 1.0
    return lv


def estacio(e):
    """La Gavina sencera (sense llums: vegeu `llums_estacio`), de lluny a prop segons la càmera de `e`."""
    cam = e.cam
    peces = []
    # cada peça, amb el punt que en fa de profunditat
    peces.append(((-110, 20, 15), lambda: _ala(e, -1)))
    peces.append(((110, 20, 15), lambda: _ala(e, 1)))
    peces.append(((0, 0, 0), lambda: _cos(e)))
    peces.sort(key=lambda p: -cam.vista(p[0])[2])
    for _, fn in peces:
        fn()


def _cos(e):
    # les aletes radiadores (darrere, a +x i a l'ombra: es pinten primer)
    for k in range(4):
        y = TOP - 2 - k * 4.4
        e.quad('aletes', (RX - 1, y, 6), (RX + 14 * B, y - 2.6, 9), (RX + 14 * B, y - 2.6, -9), (RX - 1, y, -6),
               ramp=PANEL, lvl=2.4 - k * 0.3, dues_cares=True)
    # la tija i la plataforma del moll (a sota)
    y0, y1, r = STEM
    _cil(e, 'tija', r, r, y1, y0, 10, STEEL,
         lambda a, s, t, P: 3.4 + (0.9 if int((P[1] - y1) / 6) != int((P[1] - y1 - 0.8) / 6) else 0))
    hx, yt, yb, hz = PLAT

    junta = lambda s: 0.9 if int(s / 9) != int((s - 0.8) / 9) else 0
    e.caixa('moll', -hx, hx, yb, yt, -hz, hz, STEEL, 3.0,
            cares={'sota': {'ramp': STEEL_T, 'lvl': lambda s, t, P: 2.6 - junta(s)},
                   'dalt': {'ramp': STEEL, 'lvl': lambda s, t, P: 3.6 - junta(s)},
                   'davant': {'ramp': STEEL, 'lvl': lambda s, t, P: 3.0 - junta(s)},
                   'esquerra': {'ramp': STEEL, 'lvl': lambda s, t, P: 3.0 - junta(s)},
                   'dreta': {'ramp': STEEL, 'lvl': lambda s, t, P: 3.0 - junta(s)}})
    # les ratlles d'avís, a la franja de sota de cada costat
    ratlla = lambda s, t: int((s + t) / 2.6) % 2 == 0
    yr = yb + 2.6
    for P0, P1, P2, P3 in (((-hx, yr, -hz), (hx, yr, -hz), (hx, yb, -hz), (-hx, yb, -hz)),
                           ((-hx, yr, hz), (-hx, yr, -hz), (-hx, yb, -hz), (-hx, yb, hz)),
                           ((hx, yr, -hz), (hx, yr, hz), (hx, yb, hz), (hx, yb, -hz))):
        e.quad('moll', P0, P1, P2, P3, ramp=WARN, lvl=2.2, forma=ratlla)
    # el con de sota
    _cil(e, 'con', 7 * B, RX, CB, BOT, 36, STEEL_T,
         lambda a, s, t, P: 2.6 - (0.9 if abs(t - (BOT - CB) * 0.55) < 0.7 else 0))
    # el tambor
    _cil(e, 'tambor', RX, RX, BOT, TOP, 36, STEEL, _tambor_lvl)
    # la tapa i la cúpula
    _disc(e, 'tapa', 0, TOP, 0, RX, STEEL,
          lambda s, t, P: 4.6 + (0.9 if abs(math.hypot(s - RX, t - RX) - RX * 0.72) < 0.8 else 0)
          - (0.8 if math.hypot(s - RX, t - RX) > RX - 1.2 else 0))
    nlat = 8
    for j in range(nlat):
        la, lb = j * (math.pi / 2) / nlat, (j + 1) * (math.pi / 2) / nlat
        ra, rb = DR * math.cos(la), DR * math.cos(lb)
        ya, yb_ = TOP + DR * math.sin(la), TOP + DR * math.sin(lb)
        _cil(e, 'cupula', ra, rb, ya, yb_, 24, STEEL,
             lambda a, s, t, P, j=j: 4.6 - (1.4 if j == 3 and t < 1.2 else 0) - (1.2 if j == 6 and t < 1.0 else 0)
             - (3.0 if j == 1 and int(a / (math.pi / 6)) % 2 == 0 and 1.0 < s < 4 else 0))
    # la resclosa: una caixa curta que mira al sol (a -x)
    e.caixa('resclosa', -RX - 5 * B, -RX + 2, WINDOW_Y - 4 * B, WINDOW_Y + 4 * B, -4 * B, 4 * B, STEEL, 4.6,
            cares={'esquerra': {'ramp': STEEL, 'lvl': lambda s, t, P: 5.0 - (2.6 if 3 < s < 7 and 3 < t < 7 else 0)}})
    # l'antena i el plat
    ax, ah = ANT
    e.cable('antena', [(ax, TOP + DR * 0.5, 0), (ax, ah, 0)], STEEL, 5.4, gruix=1.3)
    for k in (0.4, 0.7):
        yy = TOP + DR * 0.5 + (ah - TOP - DR * 0.5) * k
        e.cable('antena', [(ax - 2.6, yy, 0), (ax + 2.6, yy, 0)], STEEL, 4.4, gruix=0.8)
    dx_, dy_, dz_ = -12 * B, 22 * B, -4.0
    e.cable('plat', [(-6 * B, TOP + 4, -2), (dx_, dy_, dz_)], STEEL, 3.6, gruix=1.0)
    e.quad('plat', (dx_ - 5, dy_ + 2, dz_ + 3), (dx_ + 5, dy_ + 2, dz_ + 3), (dx_ + 5, dy_ - 1, dz_ - 3),
           (dx_ - 5, dy_ - 1, dz_ - 3), ramp=STEEL, lvl=lambda s, t, P: 5.6 - math.hypot(s - 5, t - 3.3) * 0.25,
           dues_cares=True, forma=lambda s, t: (s - 5) ** 2 / 25 + (t - 3.35) ** 2 / 11.2 <= 1)



def llums_estacio(cam):
    """On cauen les llums de l'estació a la pantalla: {nom: (u, v, escala)}."""
    out = {}
    for nom, P in (('babord', (-WING[2][0], WING[2][1] + 4.5, 0)), ('estribord', (WING[2][0], WING[2][1] + 4.5, 0)),
                   ('balisa', (ANT[0], ANT[1] + 1, 0)),
                   ('finestra', (RX * math.sin(LIT_A) * 1.01, WINDOW_Y, -RX * math.cos(LIT_A) * 1.01)),
                   ('guia', (0, PLAT[2] + 1.3, -PLAT[3]))):
        u, v, _ = cam.projecta(P)
        out[nom] = (u, v, cam.escala(P))
    return out


def llums(cv, cam, t=0.0, e=None, k=1.0):
    """Les llums de l'estació (com al dibuix pla): les de navegació parpellegen per torns (vermell a babord, verd a
    estribord), la balisa de l'antena batega, la finestra encesa tremola, i les llums de guia del moll. Amb t = 0,
    tot encès. `e` (l'Escena de l'estació): les llums que queden darrere d'una peça no s'encenen. `k`: la mida."""
    ph = 2 * math.pi * t
    fr = (t * 24) % 12
    L = llums_estacio(cam)

    def amagat(nom, peces):
        if e is None:
            return False
        u, v, _ = L[nom]
        x, y = int(round(u)), int(round(v))
        if not (0 <= x < e.cv.w and 0 <= y < e.cv.h):
            return True
        return e.ids[e.amo[y * e.cv.w + x]] not in peces + ('',)
    for nom, col, apagat in (('babord', (255, 60, 50), 2.5 <= fr < 4.5),
                             ('estribord', (70, 255, 120), 8.5 <= fr < 10.5)):
        if amagat(nom, ('ala', 'biga', 'colze')):
            continue
        u, v, sc = L[nom]
        n = max(1, round(sc * 1.4 * k))
        for dy in range(n):
            for dx in range(n):
                c = col if (dx, dy) != (0, 0) else mix(col, (255, 255, 255), 0.5)
                cv.flat(u + dx, v + dy, mix(col, (20, 24, 40), 0.65) if apagat else c)
        cv.glow(u + n / 2, v + n / 2, (3 if apagat else 6) * sc * k + 2, col, 0.25 if apagat else 0.8)
    if not amagat('balisa', ('antena',)):
        u, v, sc = L['balisa']
        cv.flat(u, v, (255, 255, 255))
        cv.glow(u, v, 5 * sc * k + 1, (220, 230, 255), 0.6 + 0.25 * (math.cos(ph * 3) - 1))
    if not amagat('finestra', ('tambor',)):
        u, v, sc = L['finestra']
        n = max(2, round(2.2 * sc * k))
        for dy in range(n):
            for dx in range(n):
                c = mix((255, 240, 180), (190, 104, 46), (dx + dy) / (2 * n - 1))
                cv.flat(u - n / 2 + dx, v - n / 2 + dy, c)
        fl = 0.07 * (math.sin(ph * 5 + 1) - math.sin(1)) + 0.04 * math.sin(ph * 2)
        cv.glow(u, v, 10 * sc * k + 2, (255, 190, 110), 0.5 + fl)
    # les llums de guia, al cantell de davant del moll
    hx = PLAT[0]
    for f in (-0.9, -0.45, 0.0, 0.45, 0.9):
        P = (hx * f, PLAT[2] + 1.0, -PLAT[3] - 0.3)
        u, v, _ = cam.projecta(P)
        if e is None or (0 <= int(u) < e.cv.w and 0 <= int(v) < e.cv.h
                         and e.ids[e.amo[int(v) * e.cv.w + int(u)]] in ('moll', '')):
            cv.flat(u, v, (120, 255, 170))
    u, v, sc = L['guia']
    cv.glow(u, v, 9 * sc * k, (120, 255, 170), 0.3)


# ─── El pla del pròleg ──────────────────────────────────────────────────────

def _mira(pos, cap, f, centre):
    d = [cap[i] - pos[i] for i in range(3)]
    return Camera(pos=pos, yaw=math.atan2(d[0], d[2]), pitch=math.atan2(-d[1], math.hypot(d[0], d[2])), f=f,
                  centre=centre)


CAM = _mira((-150.0, 85.0, -70.0), (-10.0, 5.0, 0.0), 300.0, (450, 150))
EX, EY, ER = 560, 560, 300               # la Terra (píxels de pantalla)
MOON = (96, 58, 8)                       # la Lluna, petita, al buit de dalt a l'esquerra


def nau_img(cam, w=W, h=H):
    """L'estació sola sobre transparent, vista per `cam` → (imatge, Escena)."""
    cv = Canvas(w, h, transparent=True)
    cv.S = 1
    e = Escena(cv, cam, llums=_llums(), ambient=-2.4)
    estacio(e)
    return cv.img, e


@lru_cache(maxsize=None)
def _nau():
    return nau_img(CAM)


def bg(cv, t=0.0):
    """`t` (0..1): moment del bucle de l'animació de fons (amb 0, el fons quiet)."""
    espai(cv, t=t)
    lluna(cv, *MOON)
    terra(cv, EX, EY, ER, t=t)
    img, e = _nau()
    cv.img.alpha_composite(img)
    llums(cv, CAM, t, e)
    vinyeta(cv)


PROPS = {}


# ─── La llançadora (capa del pròleg) ─────────────────────────────────────────
# Mentre la narració presenta La Gavina, una llançadora petita surt de darrere la Terra i puja fins sota el moll de
# càrrega («llancadora_puja», 7 s, sense bucle: es queda atracada). Fins llavors, la capa és buida («llancadora»).
# Ve de lluny: comença petita (un punt amb el motor encès) i creix fins a la mida que toca al costat del moll.

LL_DT, LL_LEN = 0.1, 7.0
LL_FROM = (578, 266, 1500.0)             # surt de darrere el limb de la Terra: (u, v) de la pantalla i distància


def desprojecta(cam, u, v, z):
    """El punt del món que cau a (u, v) de la pantalla a la profunditat z (l'invers de `Camera.projecta`)."""
    x2, y2 = (u - cam.centre[0]) * z / cam.f, -(v - cam.centre[1]) * z / cam.f
    cy, sy, cp, sp = math.cos(cam.yaw), math.sin(cam.yaw), math.cos(cam.pitch), math.sin(cam.pitch)
    dy = y2 * cp - z * sp
    z1 = y2 * sp + z * cp
    return (cam.pos[0] + x2 * cy + z1 * sy, cam.pos[1] + dy, cam.pos[2] - x2 * sy + z1 * cy)


def llancadora_pos(k, cam=None):
    """On és la llançadora (0..1 del viatge) → (u, v, escala): del limb de la Terra fins sota el moll, en corba."""
    cam = cam or CAM
    A, Bp = desprojecta(cam, *LL_FROM), DOCK
    P = tuple(a + (b - a) * k for a, b in zip(A, Bp))
    P = (P[0], P[1] + math.sin(k * math.pi) * 25, P[2])
    u, v, _ = cam.projecta(P)
    return u, v, cam.escala(P)


def _llancadora_petita(cv, x, y, t):
    """De lluny: el casc (3 píxels) i el motor encès."""
    cv.flat(x - 1, y, (110, 116, 130))
    cv.flat(x, y, (170, 176, 190))
    cv.flat(x + 1, y, (255, 200, 130))
    fl = 0.7 + 0.3 * math.sin(t * 31)
    cv.glow(x + 1.5, y, 5, (255, 150, 70), 0.5 * fl)


@lru_cache(maxsize=None)
def _base():
    cv = Canvas(light=LIGHT)
    bg(cv)
    return cv.img


def _layer(draw):
    """Capa transparent amb el que `draw(cv)` canvia sobre el fons quiet."""
    from hd640.rooms.fabrica_cambra_pla_comu import frame_diff
    cv = Canvas(light=LIGHT, img=_base().copy())
    cv.P = cv.img.load()
    draw(cv)
    return frame_diff(_base(), cv.img)


def _llancadora(cv, u, v, sc, t):
    if sc < 0.55:
        _llancadora_petita(cv, round(u), round(v), t or 0.0)
        return
    # el dibuix pla (d'un píxel per unitat), a la mida que toca a aquella distància
    from pixels import nearest
    sp = Canvas(24, 12, transparent=True)
    llancadora(sp, 10, 6, t)
    k = max(1, round(sc))
    im = nearest(sp.img, (24 * k, 12 * k)) if k > 1 else sp.img
    cv.img.alpha_composite(im, (round(u - 10 * k), round(v - 6 * k)))
    cv.P = cv.img.load()
    if t is not None:
        fl = 0.7 + 0.3 * math.sin(t * 31)
        cv.glow(u + 6 * k, v, 7 * k, (255, 150, 70), 0.5 * fl)
        if int(t / 0.5) % 2:
            cv.glow(u + 3 * k, v - 2 * k, 4 * k, (255, 60, 50), 0.4)


def _llancadora_frames():
    out = []
    for i in range(round(LL_LEN / LL_DT) + 1):
        t = i * LL_DT
        uu = min(1.0, t / LL_LEN)
        k = (uu * uu * (3 - 2 * uu)) ** 0.9
        u, v, sc = llancadora_pos(k)
        out.append(_layer(lambda cv: _llancadora(cv, u, v, sc, t if uu < 1 else None)))
    return out


ANIMS = {
    'ambient': {'frames': lambda: ambient_frames(bg, LIGHT), 'frameDuration': 130},
    'llancadora': {'frames': lambda: [Canvas(transparent=True).img], 'frameDuration': 1000, 'loop': False, 'zIndex': 2},
    'llancadora_puja': {'frames': _llancadora_frames, 'frameDuration': round(LL_DT * 1000), 'loop': False,
                        'prop': 'llancadora'},
}
