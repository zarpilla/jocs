"""
La Conjura de l'Avet — el pla de cinema de la portada i el pròleg (i les peces que s'hi animen). EN 3D, a 1×, a
pantalla completa (640×360, sense HUD).

És el mateix carrer de `mur_avet` (avet_comu.py), amb la mateixa càmera però amb més cel (el centre òptic més avall:
tot baixa 52 px i es pinta fins a baix): així el pròleg acaba exactament on comença el joc. De nit, amb tramuntana:
la pluja en diagonal, els llamps (per codi: el cel i l'absis s'encenen, rosats, i l'avet queda fosc, en silueta),
les finestres de l'absis enceses (les monges resen matines) i, entre les arrels, el cofre amb el segell vermell.

    portada.py: l'avet ajagut, el cofre que batega (`cofre`), la pluja, els llamps i el títol (`titol`).
    proleg.py:  el carrer sense l'avet; les capes `avet_dret` (es gronxa), `avet_cau` (`cau`), `fanal`
                (`fanal_arriba`), `figura` (`figura_serra`), `cofre_brilla` (`brilla`) i `ma` (`agafa`).
"""
import functools
import math

import numpy as np
from PIL import Image

import hd640  # noqa: F401
from hd640.rooms import avet_comu as A
from hd640.rooms.avet_comu import Estat, W, H, diff
from hd640.tres_d import Camera
from pixels import nearest

CAM_CINE = Camera(pos=(0.0, A.CAMY, 0.0), f=A.F, centre=(320.0, 180.0))
DY = 52                                     # (tot és 52 px més avall que a `mur_avet`)

# La portada: l'avet ajagut, el mur esbotzat, les branques pel carrer, el cofre entre les arrels
NIT = Estat(llum='nit', cam=CAM_CINE, h=H, extres=('cofre', 'primer_pla'))
NIT_LLAMP = Estat(llum='llamp', cam=CAM_CINE, h=H, extres=('cofre', 'primer_pla'))
# El pròleg: el carrer abans que caigui l'avet
NIT_ABANS = Estat(llum='nit', arbre='cap', forat='cap', mur='sencer', branques='cap', cam=CAM_CINE, h=H,
                  extres=('primer_pla',))
NIT_ABANS_LLAMP = Estat(llum='llamp', arbre='cap', forat='cap', mur='sencer', branques='cap', cam=CAM_CINE, h=H,
                        extres=('primer_pla',))
ARBRE = {'avet', 'avet_tronc', 'arrels', 'arrels_tall', 'branques', 'branques_fons', 'cofre', 'primer_pla', 'runa'}


def render(e):
    return A.render(e)


# ─── La pluja i els llamps ─────────────────────────────────────────────────

@functools.lru_cache(maxsize=None)
def pluja(seed=3):
    """La pluja de tramuntana: en diagonal, de dalt a l'esquerra cap a baix a la dreta, freda."""
    _, v = render(NIT)
    return A.pluja_frames(v_h=H, n=8, dens=760, seed=seed, llarg=(7, 13), inc=0.55, col=(150, 170, 210), alpha=120,
                          ones=A.ones_bassals(v, n=50))


def _llamp_ratlla(img, seed=4, x0=520, x1=470):
    """El raig: una línia trencada del cel fins darrere les cases, amb branquetes, blanca i blava."""
    rng = np.random.default_rng(seed)
    a = np.asarray(img).copy()
    pts = [(x0, 0)]
    x, y = x0, 0
    while y < 150:
        y += rng.uniform(6, 14)
        x += rng.uniform(-9, 7) + (x1 - x0) / 15
        pts.append((x, y))

    def linia(p0, p1, col, gruix=1):
        n = int(max(abs(p1[0] - p0[0]), abs(p1[1] - p0[1]))) + 1
        for i in range(n + 1):
            X = int(p0[0] + (p1[0] - p0[0]) * i / n)
            Y = int(p0[1] + (p1[1] - p0[1]) * i / n)
            for dx in range(-gruix + 1, gruix):
                if 0 <= X + dx < W and 0 <= Y < H:
                    a[Y, X + dx] = (*col, 255)
    for p0, p1 in zip(pts, pts[1:]):
        linia(p0, p1, (200, 214, 255), 2)
    for p0, p1 in zip(pts, pts[1:]):
        linia(p0, p1, (255, 255, 255), 1)
    for k in (3, 7):
        if k < len(pts):
            bx, by = pts[k]
            linia((bx, by), (bx + rng.uniform(15, 30) * (1 if k % 2 else -1), by + rng.uniform(15, 28)), (190, 206, 250))
    return Image.fromarray(a, 'RGBA')


@functools.lru_cache(maxsize=None)
def _flaix(e_nit, e_llamp, protegeix=frozenset(ARBRE)):
    """El que canvia quan fa llamp (el cel, l'absis, el carrer), sense tocar l'avet (que queda en silueta).

    No és l'escena encesa sencera (semblaria que s'ha fet de dia): és la nit amb una llum blanca i blava al damunt, a
    `FLAIX` de l'escena encesa, i les finestres continuen enceses."""
    base, v = render(e_nit)
    ll, _ = render(e_llamp)
    b = np.asarray(base)
    a = b.astype(np.float64)
    a[..., :3] += (np.asarray(ll)[..., :3] - a[..., :3]) * FLAIX
    a = np.clip(np.round(a), 0, 255).astype(np.uint8)
    full = np.zeros((H, W), bool)
    full[:v.h] = v.mascara(protegeix) | v.emissiu
    a[full] = b[full]
    return diff(Image.fromarray(a, 'RGBA'), base)


# Quant s'acosta el flaix a l'escena encesa pel llamp (1: tota).
FLAIX = 0.7


def llamps(e_nit, e_llamp, n=44, seed=4):
    """Fotogrames dels llamps, en bucle (≈4,8 s): fosc, i de tant en tant un flaix doble amb el raig."""
    fl = _flaix(e_nit, e_llamp)
    buit = Image.new('RGBA', (W, H), (0, 0, 0, 0))
    mig = Image.fromarray((np.asarray(fl).astype(np.float64) * np.array((1, 1, 1, 0.45))).astype(np.uint8), 'RGBA')
    raig = _llamp_ratlla(fl, seed)
    frames = [buit] * n
    for (i, img) in ((6, raig), (7, mig), (8, fl), (9, mig), (30, mig), (31, buit), (32, fl), (33, mig)):
        frames[i] = img
    return list(frames)


# ─── El títol ──────────────────────────────────────────────────────────────

def titol():
    """«La Conjura de l'Avet», a dalt: lletres grosses de la font del joc, color de cera vella i or, amb la vora
    fosca, i el segell vermell al costat (l'únic vermell viu, com al joc)."""
    from hd640.font import font640, text_width, draw_text
    g = font640(bold=True)
    out = Image.new('RGBA', (W, H), (0, 0, 0, 0))
    fi = 0
    for (text, k, y, col) in (("La Conjura", 3, -4, (232, 196, 120)), ("de l'Avet", 4, 22, (240, 210, 140))):
        w = text_width(g, text)
        small = Image.new('RGBA', (w + 3, 18), (0, 0, 0, 0))
        draw_text(small, g, text, 1, 0, col, outline=(20, 16, 24))
        # una mica de degradat: més clar a dalt
        a = np.asarray(small).astype(np.float64)
        lit = (a[..., 3] > 0) & (np.abs(a[..., :3] - np.array(col)).sum(-1) < 4)
        ys = np.arange(a.shape[0])[:, None] * np.ones((1, a.shape[1]))
        f = np.clip(1.15 - (ys - 4) / 14, 0.75, 1.2)
        a[lit, :3] = np.clip(a[lit, :3] * f[lit][:, None], 0, 255)
        small = Image.fromarray(a.astype(np.uint8), 'RGBA')
        big = nearest(small, (small.width * k, small.height * k))
        # l'ombra, a baix a la dreta
        sh = Image.fromarray(np.where(np.asarray(big)[..., 3:] > 0, np.array((6, 6, 12, 200), np.uint8),
                                      np.zeros(4, np.uint8)).astype(np.uint8), 'RGBA')
        x = (W - big.width) // 2
        out.alpha_composite(sh, (x + k, y + k))
        out.alpha_composite(big, (x, y))
        fi = x + big.width
    # el segell de cera, a la dreta de «de l'Avet»
    a = np.asarray(out).copy()
    cx, cy, r = fi + 14, 62, 11
    Y, X = np.mgrid[0:H, 0:W]
    d = np.hypot(X - cx, Y - cy)
    vora = r * (1 + 0.08 * np.sin(np.arctan2(Y - cy, X - cx) * 7))
    m = d < vora
    lv = 3.0 - (Y - cy) / r * 1.0 + (d < r * 0.62) * 0.6 - ((d > r * 0.62) & (d < r * 0.74)) * 1.2
    i = np.clip(np.floor(lv + A._B4[Y & 3, X & 3] - 0.5), 0, len(A.CERA) - 1).astype(int)
    a[m, :3] = A.CERA[i][m]
    a[m, 3] = 255
    # l'arbre gravat al segell (un avet petit, més fosc)
    for dy in range(-6, 6):
        half = max(0, (dy + 6) // 2)
        for dx in range(-half, half + 1):
            if (dy + 6) % 3 != 2:
                a[cy + dy, cx + dx, :3] = A.CERA[1]
    a[cy + 6, cx, :3] = A.CERA[1]
    return Image.fromarray(a, 'RGBA')


# ─── El cofre que batega ───────────────────────────────────────────────────

def cofre_bategs(base_img, n=10, r=30.0):
    """La lluïssor vermella del segell, que puja i baixa (additiva, damunt del fons)."""
    u, vv = A.segell_xy(CAM_CINE)
    frames = []
    for i in range(n):
        k = 0.25 + 0.45 * (0.5 - 0.5 * math.cos(2 * math.pi * i / n))
        frames.append(diff(A.brillantor(base_img, u, vv, k, r=r), base_img))
    return frames


# ─── La figura i el fanal (el pròleg) ──────────────────────────────────────

def _copia(v):
    """Una còpia de la Vista (per dibuixar-hi a sobre sense tocar la de la memòria cau)."""
    c = A.Vista.__new__(A.Vista)
    c.__dict__.update(v.__dict__)
    c.col, c.z, c.own, c.emissiu = v.col.copy(), v.z.copy(), v.own.copy(), v.emissiu.copy()
    c.ids = list(v.ids)
    return c


def encaputxat(v, e, P, ajupit=0.0, serra=None, fanal=None):
    """Una figura encaputxada (capa fosca), a la profunditat de P. `ajupit` 0..1: ajupida (serrant); `serra`: la
    fase del moviment de la serra (o None); `fanal`: on porta el fanal (un punt del món) o None."""
    alt = 88.0 * (1 - 0.42 * ajupit)
    A.figura(v, e, P, alt=alt, roba=(30, 28, 40), cap='caputxa', seed=61, sid='figura', mira=1, ample=88.0 / alt)
    if serra is not None:
        u, vv, z = v.cam.projecta(tuple(P + np.array((14, alt * 0.38, -4))))
        k = v.cam.f / z
        L = 16 * k
        dx = math.sin(serra) * 4 * k
        for i in range(int(L)):
            X, Y = int(u + dx + i), int(vv + i * 0.25)
            if 0 <= X < v.w and 0 <= Y < v.h:
                v.col[Y, X] = (120, 120, 130)
                v.own[Y, X] = v.idx('figura')
    if fanal is not None:
        fanalet(v, fanal)


def fanalet(v, P):
    """El fanal: una caixeta de llum càlida, amb el ferro fosc a dalt i a baix."""
    u, vv, z = v.cam.projecta(tuple(P))
    k = v.cam.f / z
    w, h = max(2, round(4 * k)), max(3, round(6 * k))
    x0, y0 = int(u - w / 2), int(vv - h)
    for y in range(y0 - 1, y0 + h + 1):
        for x in range(x0, x0 + w):
            if 0 <= x < v.w and 0 <= y < v.h:
                ferro = y in (y0 - 1, y0 + h)
                v.col[y, x] = (30, 26, 30) if ferro else ((255, 236, 170) if abs(x - u) < w / 3 else (240, 170, 70))
                v.emissiu[y, x] = not ferro
                v.own[y, x] = v.idx('fanal')


def llum_fanal(img, P, k=1.0, cam=CAM_CINE):
    """La llum del fanal: una taca càlida al voltant (i a terra, aixafada)."""
    u, vv, z = cam.projecta(tuple(P))
    s = cam.f / z
    out = A.brillantor(img, u, vv - 3 * s, 0.9 * k, col=(255, 170, 70), r=56 * s)
    ug, vg, _ = cam.projecta(tuple(np.array((P[0], 0.0, P[2]))))
    X, Y = np.meshgrid(np.arange(W), np.arange(H))
    d = np.hypot((X + 0.5 - ug) / (70 * s), (Y + 0.5 - vg) / (16 * s))
    a = np.clip(1 - d, 0, 1) ** 1.5 * 0.8 * k
    o = np.asarray(out).astype(np.float64)
    o[..., :3] = np.clip(o[..., :3] + a[..., None] * np.array((150, 96, 40.0)), 0, 255)
    return Image.fromarray(o.astype(np.uint8), 'RGBA')
