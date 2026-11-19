"""
Final «La fugida»: la Sala de la Memòria, uns mesos després, convertida en un museu de veritat. EN 3D
(hd640/tres_d.py), a 1×; el dibuix pla de sempre és a final_museu_pla_comu.py (d'allà surten les textures: la paret
dels plafons amb la foto del torn de nit, la llibreta i la fàbrica; la porta; la vitrina; el sòcol; els personatges).

Vist des de l'esquerra i des de dalt:
  - la paret de les obres fuig cap a la dreta: la foto del torn de nit, la més a prop i la més gran (a dalt a
    l'esquerra), amb el cartellet «DESAPAREGUDA» sota l'Iri; després la llibreta de torn i la fàbrica, cada cop més
    petites, i el rètol MUSEU DE LA MEMÒRIA. A la cantonada, la paret de la dreta amb la porta oberta (SORTIDA);
  - la Vet, d'esquena, davant la foto; un cordó de vellut entre pals de llautó la separa de nosaltres: és el
    primer pla, fosc i tallat per la vora de baix a l'esquerra;
  - el banc, girat, amb el pom de flors; la vitrina de la clau anglesa (el Lot 1), separada de la paret i amb tres
    cares; el faristol de fullets MUSEU, girat;
  - a baix a la dreta, gros i a prop, el sòcol de l'holograma tapat amb el drap i el cartell «APAGAT PER SEMPRE»;
  - la llum: els focus del carril fan bassals a la paret (els del dibuix pla) i al terra, i els cons de pols que
    respiren; el terra de resina encerat; racons foscos.
`foto_mira` (la Mira a la foto) i `conserge_cargol` (en Cargol vell, conserge, amb la galleda, al costat de la porta)
són la diferència amb el fons. El quadre del text del narrador va al mig (≈145..495 × 140..240): la foto, la Vet i
el sòcol en queden fora.
Animació: `ambient` (la llum dels focus que respira, la pols als cons i un reflex que passa pel vidre de la
vitrina).
"""
import math
from functools import lru_cache

import numpy as np
from PIL import Image

import hd640  # noqa: F401  (posa la llibreria de dibuix a 640×360)
from hd.pix import Canvas, Light, B4, W, H, mix, STEEL, IRON, GOLD, WALNUT, PAPER
import hd640.rooms.final_museu_pla_comu as pla
from hd640.rooms.final_museu_pla_comu import CREAM, WAX, FLOOR_Y, SPOTS, TGT, text, text_w, hr, PILOT
from hd640.tres_d import Camera, Escena, Llum

LIGHT = Light(ambient=0.0, vignette=None, floor_fade=None)

# ─── El món ─────────────────────────────────────────────────────────────────
# x a la dreta, y amunt, z cap al fons; 1 unitat = 1 píxel del dibuix pla. La paret de les obres és a z = ZB, i hi
# va el dibuix pla amb la x desplaçada OFF; la paret de la porta és a x = XR (la cantonada).
ZB = 480.0
OFF = -150.0
XR = 530.0
HW = float(FLOOR_Y)
CAM = Camera(pos=(40.0, 180.0, 40.0), yaw=0.38, pitch=0.22, f=400, centre=(320, 130))

LLUMS = [Llum((SPOTS['foto'][0] + OFF, 190.0, ZB - 120), 380, 1.6),
         Llum((SPOTS['fabrica'][0] + OFF, 190.0, ZB - 120), 340, 1.2),
         Llum((300.0, 190.0, 260.0), 420, 1.0)]
AMBIENT = -0.3


def _pw(x, y):
    """Un punt de la paret de les obres (coordenades del dibuix pla) al món."""
    return (x + OFF, HW - y, ZB)


# ─── Textures planes ────────────────────────────────────────────────────────

@lru_cache(maxsize=None)
def _paret(mira=False):
    """La paret de les obres tal com es veu de cara (el dibuix pla, sense els mobles ni el terra)."""
    cv = Canvas(light=pla.LIGHT)
    pla.wall(cv)
    title = 'MUSEU DE LA MEMÒRIA'
    tw = text_w(title)
    tx = 293 - tw // 2
    cv.darken(tx - 8, 32, tx + tw + 10, 33, 0.6)
    cv.rect(tx - 9, 18, tx + tw + 8, 31, WALNUT, lambda x, y: 2.6 - (y - 18) * 0.08 + (hr(x // 8, y, 3) - 0.5) * 0.3, 0.3)
    cv.hline(tx - 9, tx + tw + 8, 18, WALNUT, 4.6, 0.3)
    cv.hline(tx - 9, tx + tw + 8, 31, WALNUT, 1.0, 0.3)
    for sx in (tx - 6, tx + tw + 5):
        cv.put(sx, 24, GOLD, 5.4, 0)
        cv.put(sx, 25, GOLD, 2.6, 0)
    text(cv, tx, 23, title, GOLD, 5.0, 0)
    for hx in range(130, 560, 110):
        cv.vline(hx, 9, 13, IRON, 2.0)
    cv.hline(0, W - 1, 14, IRON, 4.0)
    cv.hline(0, W - 1, 15, IRON, 3.0)
    cv.hline(0, W - 1, 16, IRON, 1.4)
    for sx, sy in SPOTS.values():
        pla.spot(cv, sx, sy)
    pla.foto(cv, mira)
    pla.llibreta(cv)
    pla.fabrica(cv)
    return cv.img


@lru_cache(maxsize=None)
def _paret_porta():
    """La paret de la porta: la porta oberta de bat a bat (SORTIDA), amb el passadís il·luminat."""
    cv = Canvas(light=pla.LIGHT)
    pla.wall(cv)
    DX0, DX1, DT = 16, 81, 80
    cv.rect(DX0 - 5, DT - 5, DX1 + 5, 204, CREAM,
            lambda x, y: 4.8 if x < DX0 - 2 or y < DT - 2 else (1.8 if x > DX1 + 1 else 3.0))
    for y in range(DT, 205):
        for x in range(DX0, DX1 + 1):
            lvl = 4.4 - abs(x - 48) / 40 - (y - DT) / 160
            if y > 181:
                lvl = 3.0 - (y - 181) / 21 - (0.4 if (y - 181) in (3, 8, 15) else 0)
            cv.put(x, y, CREAM, lvl, 0.4)
    for i in range(5):
        cv.vline(DX0 + i, DT, 204, STEEL, 3.4 - i * 0.45)
        cv.vline(DX1 - 4 + i, DT, 204, STEEL, 2.0 + i * 0.25)
    cv.glow(48, 147, 53, (255, 236, 200), 0.25)
    s = 'SORTIDA'
    sw = text_w(s)
    sx0 = 49 - sw // 2 - 3
    cv.rect(sx0, 63, sx0 + sw + 5, 73, PILOT, 1.5, 0)
    text(cv, sx0 + 3, 65, s, PILOT, 3.5, 0)
    cv.glow(49, 68, 21, (90, 255, 140), 0.25)
    return cv.img


def _retall(fn, *a, **k):
    cv = Canvas(light=pla.LIGHT, transparent=True)
    fn(cv, *a, **k)
    box = cv.img.getbbox()
    return cv.img.crop(box), box[0], box[1]


@lru_cache(maxsize=None)
def _vitrina():
    """El davant de la vitrina (el dibuix pla): → (imatge, x0, y0)."""
    cv = Canvas(light=pla.LIGHT)
    pla.wall(cv)
    pla.vitrina(cv)
    return cv.img.crop((474, 113, 545, 205)), 474, 113


@lru_cache(maxsize=None)
def _expositor():
    return _retall(pla.expositor)


@lru_cache(maxsize=None)
def _socol():
    return _retall(pla.socol_apagat)


@lru_cache(maxsize=None)
def _conserge():
    return _retall(pla.conserge)


@lru_cache(maxsize=None)
def _vet():
    return _retall(pla.vet)


@lru_cache(maxsize=None)
def _flors():
    return _retall(pla.flors, 20, 20)


# ─── Peces del món ──────────────────────────────────────────────────────────

def _terra(s, t, P):
    x, z = P[0], P[2]
    T = 46.0
    ui, vi = math.floor(x / T), math.floor(z / T)
    fu, fv = x - ui * T, z - vi * T
    lvl = 3.0 + (hr(ui, vi, 7) - 0.5) * 0.3 + (hr(int(x) // 5, int(z) // 3, 9) - 0.5) * 0.1
    if fu < 1.2 or fv < 1.2:
        lvl = 1.8
    elif fu < 2.4 or fv < 2.4:
        lvl += 0.3
    return lvl


def ombra_peu(e, x, z, rx, rz=None, k=0.55):
    rz = rz or rx * 0.6
    e.foscor('ombra', (x - rx, 0.2, z + rz), (x + rx, 0.2, z + rz), (x + rx, 0.2, z - rz), (x - rx, 0.2, z - rz),
             lambda s, t: k * max(0.0, 1 - math.hypot(s / rx - 1, t / rz - 1)) * 1.6)


def banc(e):
    """El banc de fusta, girat, amb les potes i el pom de flors damunt."""
    cx, cz, ang = 165.0, 320.0, 0.32
    w, d = 190.0, 30.0
    ombra_peu(e, cx + 10, cz + 4, 105, 26, 0.5)
    c, s_ = math.cos(ang), math.sin(ang)
    for lx in (-w / 2 + 14, w / 2 - 14):
        for lz in (-d / 2 + 5, d / 2 - 5):
            px, pz = cx + lx * c - lz * s_, cz + lx * s_ + lz * c
            e.caixa_girada('banc', px, pz, 5, 5, 20, ang, WALNUT, 2.4)
    e.caixa_girada('banc', cx, cz, w, d, 7, ang, WALNUT, 4.0, y0=20, cares={
        'dalt': {'ramp': WALNUT, 'lvl': lambda s, t, P: 5.0 + (hr(int(s) // 12, int(t) // 6, 3) - 0.5) * 0.5
                 - (1.2 if int(t) % 10 == 0 else 0)},
        'davant': {'ramp': WALNUT, 'lvl': 3.0},
        'dreta': {'ramp': WALNUT, 'lvl': 2.4}, 'esquerra': {'ramp': WALNUT, 'lvl': 3.4}})
    img, ox, oy = _flors()
    fx, fz = cx - 40 * c, cz - 40 * s_
    e.sprite('banc', img, (16 - ox + 18, 24 - oy), (fx, 27, fz))


def vitrina(e):
    """La vitrina de la clau anglesa, separada de la paret i girada: el davant és el dibuix pla."""
    img, x0, y0 = _vitrina()
    cx, cz, ang = 400.0, 395.0, -0.35
    w, d, h = float(img.width), 50.0, float(img.height)
    ombra_peu(e, cx - 6, cz + 2, 46, 30, 0.5)
    e.caixa_girada('vitrina', cx, cz, w, d, h, ang, CREAM, 3.6, cares={
        'davant': {'tex': (img, (0, 0, img.width, img.height))},
        'esquerra': {'tex': (img, (2, 0, 12, img.height))},
        'dreta': {'tex': (img, (img.width - 12, 0, img.width - 2, img.height))},
        'dalt': {'ramp': WALNUT, 'lvl': 4.6},
    })


def expositor(e):
    """El faristol de fullets MUSEU, girat cap a nosaltres."""
    img, ox, oy = _expositor()
    cx, cz, ang = 300.0, 445.0, -0.5
    hw = img.width / 2
    c, s_ = math.cos(ang), math.sin(ang)
    ombra_peu(e, cx, cz, 28, 14, 0.5)
    hh = float(img.height)
    P0 = (cx - hw * c, hh, cz - hw * s_)
    P1 = (cx + hw * c, hh, cz + hw * s_)
    e.quad('expositor', P0, P1, (P1[0], 0, P1[2]), (P0[0], 0, P0[2]), tex=(img, (0, 0, img.width, img.height)),
           dues_cares=True)


def cordo(e):
    """El cordó de vellut entre pals de llautó, davant la foto: el primer pla."""
    pals = [(-160.0, 220.0), (-5.0, 290.0), (95.0, 340.0)]
    for x, z in pals:
        e.tub('cordo', (x, 0, z), (x, 4, z), 11.0, GOLD, 2.4, llum_dir=(-0.4, -1.0))
        e.tub('cordo', (x, 4, z), (x, 92, z), 3.2, GOLD, 3.0, llum_dir=(-0.4, -1.0))
        e.tub('cordo', (x, 92, z), (x, 97, z), 5.5, GOLD, 3.6, llum_dir=(-0.4, -1.0))
    for (ax, az), (bx, bz) in zip(pals, pals[1:]):
        pts = []
        for k in range(9):
            q = k / 8
            pts.append((ax + (bx - ax) * q, 88 - 26 * math.sin(math.pi * q), az + (bz - az) * q))
        e.cable('cordo', pts, pla.VELVET, 3.0, gruix=5)


# ─── Composició ────────────────────────────────────────────────────────────

def scene(cv, mira=False, cargol=False):
    cv.S = 1
    e = Escena(cv, CAM, LLUMS, ambient=AMBIENT)
    pw = _paret(mira)
    e.quad('paret', _pw(0, 0), _pw(W, 0), _pw(W, FLOOR_Y), _pw(0, FLOOR_Y), tex=(pw, (0, 0, W, FLOOR_Y)))
    for x0 in (-192, -128, -64, W, W + 64):     # (la paret continua a banda i banda: plafons llisos)
        e.quad('paret', _pw(x0, 0), _pw(x0 + 64, 0), _pw(x0 + 64, FLOOR_Y), _pw(x0, FLOOR_Y),
               tex=(pw, (5, 0, 69, FLOOR_Y)))
    e.quad('sostre', (-600, HW, -200), (XR, HW, -200), (XR, HW, ZB), (-600, HW, ZB), ramp=CREAM,
           lvl=lambda s, t, P: 1.3 + 0.5 * t / 680 - (0.6 if P[0] % 110 < 2 else 0))
    pp = _paret_porta()                         # (de cara a la paret de la dreta, la cantonada és a l'esquerra)
    e.quad('paret_porta', (XR, HW, ZB), (XR, HW, ZB - 140), (XR, 0, ZB - 140), (XR, 0, ZB),
           tex=(pp, (0, 0, 140, FLOOR_Y)))
    e.quad('paret_porta', (XR, HW, ZB - 140), (XR, HW, -200), (XR, 0, -200), (XR, 0, ZB - 140),
           tex=(pp, (200, 0, 540, FLOOR_Y)))
    e.quad('terra', (-800, 0, ZB), (XR, 0, ZB), (XR, 0, -200), (-800, 0, -200), ramp=WAX, lvl=_terra)
    # els bassals dels focus al terra, i el racó de la cantonada, fosc
    for (sx, _), (tx, _) in zip(SPOTS.values(), TGT):
        x = tx + OFF
        e.claror((x - 90, 0.3, ZB - 2), (x + 90, 0.3, ZB - 2), (x + 90, 0.3, ZB - 150), (x - 90, 0.3, ZB - 150),
                 (255, 214, 160), lambda s, t: 0.28 * max(0.0, 1 - math.hypot((s - 90) / 90, t / 140)))
    e.foscor('ombra', (XR - 160, 0.2, ZB), (XR, 0.2, ZB), (XR, 0.2, ZB - 160), (XR - 160, 0.2, ZB - 160),
             lambda s, t: 0.45 * max(0.0, 1 - math.hypot(160 - s, t) / 160))
    e.foscor('ombra', _pw(-120, FLOOR_Y), _pw(W, FLOOR_Y), (W + OFF, 0.3, ZB - 10), (-120 + OFF, 0.3, ZB - 10),
             lambda s, t: 0.4 * (1 - t / 10))
    # en Cargol conserge, al costat de la porta (només si li van reparar la memòria)
    if cargol:
        img, ox, oy = _conserge()
        e.sprite('cargol', img, (pla.CGX - ox, pla.CGY - oy), (XR - 50, 0, ZB - 180))
    vitrina(e)
    # la Vet, d'esquena, davant la foto
    img, ox, oy = _vet()
    vx, vz = -72.0, 412.0
    e.sprite('vet', img, (pla.VTX - ox, pla.VTY - oy), (vx, 0, vz))
    banc(e)
    expositor(e)
    # el sòcol apagat, a prop
    img, ox, oy = _socol()
    sx, sz = 330.0, 235.0
    ombra_peu(e, sx + 6, sz, 60, 30, 0.45)
    e.sprite('socol', img, (pla.PEDX - ox, pla.PEDY - oy), (sx, 0, sz))
    cordo(e)
    return e


def _primer_pla_fosc(cv, e):
    idx = {i for i, s in enumerate(e.ids) if s == 'cordo'}
    P, amo = cv.P, e.amo
    for Y in range(H):
        for X in range(W):
            if amo[Y * W + X] in idx:
                c = P[X, Y]
                P[X, Y] = (int(c[0] * 0.2 + 6), int(c[1] * 0.16 + 4), int(c[2] * 0.16 + 5), 255)


@lru_cache(maxsize=None)
def _quiet(mira=False, cargol=False):
    cv = Canvas(light=LIGHT)
    e = scene(cv, mira, cargol)
    _primer_pla_fosc(cv, e)
    return cv.img


def _spots_pantalla():
    """Els focus i on apunten, en pantalla (per als cons de llum)."""
    out = []
    for (sx, sy), (tx, ty) in zip(SPOTS.values(), TGT):
        a = CAM.projecta(_pw(sx, sy + 10))
        b = CAM.projecta(_pw(tx, ty))
        out.append(((a[0], a[1]), (b[0], b[1]), CAM.escala(_pw(tx, ty))))
    return out


@lru_cache(maxsize=None)
def _vignette():
    y, x = np.mgrid[0:H, 0:W]
    d = np.hypot((x - 320) / 400, (y - 170) / 253)
    return np.clip(1 - np.maximum(0.0, d - 0.62) * 1.1, 0.0, 1.0)[..., None]


def bg(cv, mira=False, cargol=False, t=0.0):
    cv.img.paste(_quiet(mira, cargol))
    cv.P = P = cv.img.load()
    # els cons de llum dels focus (respiren amb t) i la pols que hi sura
    sp = _spots_pantalla()
    for k, ((sx, sy), (tx_, ty_), sc) in enumerate(sp):
        breath = 1 + 0.35 * math.sin(2 * math.pi * (t * (1 + k % 2) + k * 0.27))
        y1 = ty_ + 40 * sc
        for y in range(int(sy + 8), int(y1)):
            u = (y - sy) / (y1 - sy)
            half = 4 + u * 40 * sc
            mx = sx + (tx_ - sx) * u
            for x in range(int(mx - half), int(mx + half) + 1):
                a = 0.10 * breath * (1 - abs(x - mx) / half) * (1 - u * 0.7)
                if 0 <= x < W and 0 <= y < H and a > B4[y & 3][x & 3] * 0.25:
                    P[x, y] = mix(P[x, y], (255, 232, 190), a) + (255,)
    for i in range(120):
        k = int(hr(i, 1) * 4)
        (sx, sy), (tx_, ty_), sc = sp[k]
        u = 0.15 + hr(i, 2) * 0.8
        ph = hr(i, 4)
        spd = 1 + int(hr(i, 5) * 2)
        x = round(sx + (tx_ - sx) * u + (hr(i, 3) - 0.5) * 53 * sc * u + 3.3 * math.sin(2 * math.pi * (spd * t + ph)))
        y = round(sy + (ty_ - sy) * u + 2.7 * math.sin(2 * math.pi * (t + ph * 1.7)) + 2.0 * math.cos(2 * math.pi * (spd * t + ph)))
        a = 0.35 + 0.35 * (0.5 + 0.5 * math.sin(2 * math.pi * (2 * t + ph * 3)))
        if 0 <= x < W and 0 <= y < H:
            P[x, y] = mix(P[x, y], (255, 240, 200), a) + (255,)
    # un reflex que passa pel vidre de la vitrina (fora del vidre a t = 0)
    g = t * 2.2 - 0.6
    if 0 < g < 1:
        img, x0, y0 = _vitrina()
        cx, cz, ang = 400.0, 395.0, -0.35
        c, s_ = math.cos(ang), math.sin(ang)
        lx = -img.width / 2 + 4 + g * (img.width - 8)
        A = CAM.projecta((cx + lx * c - (-25) * s_, img.height - 30, cz + lx * s_ + (-25) * c))
        B = CAM.projecta((cx + (lx + 14) * c - (-25) * s_, img.height - 74, cz + (lx + 14) * s_ + (-25) * c))
        n = int(abs(B[1] - A[1])) + 1
        for j in range(n):
            q = j / n
            xx, yy = A[0] + (B[0] - A[0]) * q, A[1] + (B[1] - A[1]) * q
            for dx in range(-2, 3):
                X, Y = int(xx + dx), int(yy)
                if 0 <= X < W and 0 <= Y < H:
                    P[X, Y] = mix(P[X, Y], (255, 250, 236), 0.35 * (1 - abs(dx) / 3)) + (255,)
    # tint càlid i vinyeta
    a = np.asarray(cv.img).astype(np.float64)
    rgb = a[..., :3]
    rgb = np.round(rgb + (np.array((255, 196, 128)) - rgb) * 0.07)
    rgb = np.floor(rgb * _vignette())
    a[..., :3] = rgb
    cv.img.paste(Image.fromarray(a.astype(np.uint8), 'RGBA'))
    cv.P = cv.img.load()


def _mask(a, b):
    return np.any(np.asarray(a) != np.asarray(b), axis=-1)


@lru_cache(maxsize=None)
def _render(mira=False, cargol=False):
    cv = Canvas(light=LIGHT)
    bg(cv, mira=mira, cargol=cargol)
    return cv.img


def _diferencia(cv, **amb):
    on, off = _render(**amb), _render()
    m = Image.fromarray((_mask(on, off) * 255).astype(np.uint8), 'L')
    cv.img.paste(on, mask=m)


def foto_mira(cv):
    _diferencia(cv, mira=True)


def conserge_cargol(cv):
    _diferencia(cv, cargol=True)


PROPS = {'foto_mira': foto_mira, 'conserge_cargol': conserge_cargol}


def _ambient_frames(n=16):
    base = _render()
    props = _mask(_render(mira=True), base) | _mask(_render(cargol=True), base)
    blocked = props.copy()
    for dy in (-1, 0, 1):
        for dx in (-1, 0, 1):
            blocked |= np.roll(np.roll(props, dy, axis=0), dx, axis=1)
    frames = []
    for i in range(n):
        cv = Canvas(light=LIGHT)
        bg(cv, t=i / n)
        m = _mask(cv.img, base) & ~blocked
        fr = Image.new('RGBA', (W, H), (0, 0, 0, 0))
        fr.paste(cv.img, mask=Image.fromarray((m * 255).astype(np.uint8), 'L'))
        frames.append(fr)
    return frames


ANIMS = {'ambient': {'frames': _ambient_frames, 'frameDuration': 110}}
