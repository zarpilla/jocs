"""
La Conjura de l'Avet — `moli`: el molí del monestir per dins, a la matinada (acte 3, Iri amb la Vet). Art definitiu,
EN 3D (hd640/tres_d.py), a 1×.

La càmera és alta i mira avall (picat), una mica girada cap a l'esquerra. Al fons, el **canal** del rec corre arran de
la paret, de dreta a esquerra, fosc i fred, i se'n va per un arc baix de la paret de l'esquerra (cap al riu: per
l'arc entra la primera llum blava del dia). A la dreta, la **roda** gran de fusta, amb les pales mig dins l'aigua, i
la **falca** d'alzina clavada entre la roda i la vora del canal. Darrere la roda, a la paret del fons, la **comporta**
del rec, amb la cremallera que puja fins a la **finestra de dalt**: hi treu el cap la Gueraula, amb la mà al torn.
A l'esquerra, la **pastera** dreta, recolzada a la paret; al mig, les **moles** dins la caixa de fusta, amb la
tremuja a sobre i els sacs de farina; farina pertot. Un fanal penja d'una biga (la llum càlida); la lluna ja és fora
i la claror freda ve de l'arc i de la finestra.

Primer pla: un puntal de fusta a l'esquerra i una biga a dalt, foscos i tallats per la vora, i sacs de farina a baix a
la dreta. S'hi passa per darrere de les moles.

Decorats: `falca_tallada` (la falca partida a terra, amb estelles; la falca sencera és el prop `falca`) i
`pastera_aigua` (la pastera ja no és a la paret: sura al canal, lligada a una anella).
ANIMS: `aigua` (l'aigua del canal, que corre cap a l'esquerra, i les gotes que cauen de les pales) i `fanal` (la flama).

El món: x a la dreta, y amunt (0 = terra; l'aigua del canal a y = -30), z cap al fons (la paret del fons, a z = 520).
"""
import functools
import math

from PIL import Image

import hd640  # noqa: F401  (abans de cap hd.rooms: posa la llibreria a 640×360)

from hd.pix import Canvas, Light, W, mix
from hd640.tres_d import Camera, Escena, Llum
from hd640.rooms.nit_comu import (BOTTOM, PEDRA, LLOSA, FUSTA, FERRO, FOC, LLUNA, TELA, fbm, hr, carreus, taulons, veta,
                                  flama, ombra, hud_negre, sense, sense_hud, mascara, llum_personatge, rect_de, _diff)

# ─── La càmera i el món ──────────────────────────────────────────────────────
F = 360
CAM = Camera(pos=(0, 240, 0), yaw=-0.07, pitch=0.30, f=F, centre=(320, 90))

ZB = 476                       # la paret del fons
XL = -320                      # la paret de l'esquerra
XR = 560
ZF = 150
YT = 420
CZ0, CZ1 = 396, ZB             # el canal: de la vora fins a la paret
YA = -10                       # l'aigua
ROD = (96, 56, 438, 112, 30)  # la roda: centre x, y, z, radi, gruix
COMPORTA = (250, 318)          # x0, x1 a la paret del fons
FINESTRA = (246, 326, 150, 206)    # la finestra de dalt (a la paret del fons): x0, x1, y0, y1
ARC = (CZ0 - 4, ZB, 84)        # l'arc del canal a la paret de l'esquerra: z0, z1, alçada de la clau
PASTERA = (XL + 4, 290, 96)    # recolzada a la paret de l'esquerra: x, z0, llargada (de z0 cap al fons)
MOLES = (-130, 340, 0.3)       # la caixa de les moles: cx, cz, angle
FANAL = (-34, 150, 300)         # el fanal (penja d'una biga)
FALCA = (ROD[0] - 64, CZ0 + 4)     # on és clavada la falca (x, z)

LLUMS = [Llum(FANAL, 330, 4.2, power=1.6),
         Llum((XL + 10, 40, (ARC[0] + ARC[1]) / 2), 260, 1.4, power=1.4),
         Llum(((FINESTRA[0] + FINESTRA[1]) / 2, 240, ZB - 10), 260, 1.2, power=1.4)]
AMBIENT = -0.5

LIGHT = Light(ambient=0.0, vignette=None, floor_fade=None)

# Fusta mullada del molí (més grisa que la del monestir) i la farina.
MULLA = [(8, 8, 8), (16, 15, 14), (28, 25, 22), (42, 37, 31), (58, 50, 41), (76, 66, 52), (96, 84, 66), (118, 104, 82),
         (142, 126, 100), (168, 150, 122)]
FARINA = [(60, 56, 54), (100, 94, 88), (140, 134, 124), (180, 174, 162), (212, 206, 194), (234, 230, 220),
          (248, 246, 240)]
AIGUA = [(4, 8, 12), (8, 16, 22), (12, 26, 34), (18, 38, 48), (28, 54, 64), (44, 74, 86), (70, 104, 116),
         (110, 146, 156), (170, 200, 206)]
ALZINA = [(20, 12, 8), (44, 28, 16), (74, 48, 26), (108, 74, 40), (144, 104, 60), (180, 140, 88), (214, 180, 124)]
SAC = [(30, 26, 22), (58, 52, 44), (92, 84, 70), (128, 118, 98), (164, 152, 128), (196, 186, 160), (222, 214, 192)]
CORDA = [(30, 24, 16), (70, 58, 40), (120, 100, 70), (170, 150, 110)]


def _p(x, y, z):
    u, v, _ = CAM.projecta((x, y, z))
    return round(u), round(v)


def _z_de_v(v):
    lo, hi = 100.0, 4000.0
    for _ in range(60):
        mid = (lo + hi) / 2
        if CAM.projecta((0, 0, mid))[1] > v:
            lo = mid
        else:
            hi = mid
    return (lo + hi) / 2


def _escala_a(v):
    return CAM.escala((0, 0, _z_de_v(v)))


def _gir(cx, cz, ang):
    c, s = math.cos(ang), math.sin(ang)
    return lambda lx, y, lz: (cx + lx * c - lz * s, y, cz + lx * s + lz * c)


# ─── La sala ───────────────────────────────────────────────────────────────

def _farina_terra(x, z):
    """Quanta farina hi ha a terra (0..1): molta a la vora de les moles, clapes i petjades."""
    cx, cz, _ = MOLES
    d = math.hypot((x - cx) / 120, (z - cz) / 80)
    k = max(0.0, 1 - d) * 0.9 + max(0.0, fbm(x / 40, z / 40, 51) - 0.55) * 1.4
    return min(1.0, k)


def terra(e):
    """El terra de taulons (vells i mullats, enfarinats)."""
    e.quad('terra', (XL, 0, CZ0), (XR, 0, CZ0), (XR, 0, ZF), (XL, 0, ZF), ramp=MULLA, lvl=_terra_lvl())


def _terra_lvl():
    def terra(s, t, P):
        x, z = P[0], P[2]
        v = taulons(z, x, ample=16.0, seed=31, base=3.4)               # taulons que van de costat (al llarg de x)
        v += _farina_terra(x, z) * 2.4
        if hr(int(x / 3), int(z / 3), 52) > 0.97:
            v += 1.6                                                    # grumolls de farina
        return v

    return terra


def parets(e):
    """La paret del fons i la de l'esquerra (pedra, humitat a baix)."""
    def fons(s, t, P):
        v = carreus(s, t, alt=26.0, ample=(40.0, 64.0), seed=13, base=3.2)
        v -= max(0.0, (P[1] - 180) / 60)                                # amunt, la foscor
        if P[1] < 30:
            v -= (30 - P[1]) / 26                                       # la humitat, a baix
        return v

    e.quad('paret_fons', (XL, YT, ZB), (XR, YT, ZB), (XR, YA - 20, ZB), (XL, YA - 20, ZB), ramp=PEDRA, lvl=fons)

    def esq(s, t, P):
        v = carreus(s, t, alt=26.0, ample=(40.0, 64.0), seed=15, base=3.0)
        return v - max(0.0, (P[1] - 180) / 60) - (max(0.0, (30 - P[1]) / 26) if P[1] < 30 else 0)

    e.quad('paret_esq', (XL, YT, ZB), (XL, YT, ZF), (XL, YA - 20, ZF), (XL, YA - 20, ZB), ramp=PEDRA, lvl=esq,
           dues_cares=True)


def canal_sota(e):
    """El canal: la paret de dins de la vora (no es veu: mira cap al fons) i el llit, fosc."""
    e.quad('canal', (XL, YA - 18, ZB), (XR, YA - 18, ZB), (XR, YA - 18, CZ0), (XL, YA - 18, CZ0), ramp=AIGUA, lvl=0.6)


def vora_canal(e):
    """La vora de pedra del canal (els carreus de la cantonada, gastats i molls)."""
    def vora(s, t, P):
        return carreus(s, t, alt=12.0, ample=(30.0, 48.0), seed=21, base=4.0) - (1.0 if t < 2 else 0)

    e.quad('vora', (XL, 0.4, CZ0 + 8), (XR, 0.4, CZ0 + 8), (XR, 0.4, CZ0 - 6), (XL, 0.4, CZ0 - 6), ramp=PEDRA,
           lvl=vora)


def aigua(e, fase=0.0):
    """La superfície de l'aigua (es barreja amb el que hi ha a sota: les pales submergides es veuen fosques)."""
    def k(s, t):
        return 0.78
    e.claror((XL, YA, ZB), (XR, YA, ZB), (XR, YA, CZ0), (XL, YA, CZ0), (10, 22, 30), k)


def _onades(x, z, fase):
    """La brillantor de l'aigua a (x, z): ratlles que corren cap a l'esquerra, més fortes a la sortida de la roda."""
    xx = x + fase * 120
    v = math.sin(xx / 9 + math.sin(z / 7) * 1.2) + 0.6 * math.sin(xx / 4.3 + z / 3)
    k = max(0.0, v - 1.0) * 0.5
    k *= 0.5 + 0.8 * max(0.0, 1 - abs(x - ROD[0] + 70) / 220)
    return k


def reflexos(cv, e, fase=0.0):
    """Les ratlles de llum a l'aigua (la claror de l'arc i del fanal)."""
    idx = {i for i, sid in enumerate(e.ids) if sid == 'aigua_sup'}
    S = 1
    P0, e1, e3 = (XL, YA, ZB), (XR - XL, 0, 0), (0, 0, CZ0 - ZB)
    from hd640.tres_d import _inversa
    inv = _inversa(CAM.homografia(P0, e1, e3, S))
    a, b, c, d, e_, f, g, h, i = inv
    out = []
    for Y in range(int(_p(0, YA, ZB)[1]) - 4, int(_p(0, YA, CZ0)[1]) + 4):
        for X in range(0, W):
            if e.amo[Y * W + X] not in idx:
                continue
            xc, yc = X + 0.5, Y + 0.5
            wq = g * xc + h * yc + i
            s, t = (a * xc + b * yc + c) / wq, (d * xc + e_ * yc + f) / wq
            x, z = XL + s * (XR - XL), ZB + t * (CZ0 - ZB)
            k = _onades(x, z, fase)
            if k > 0.05:
                out.append((X, Y, min(0.7, k)))
    for X, Y, k in out:
        o = cv.P[X, Y]
        cv.P[X, Y] = mix(o, (120, 160, 176), k) + (255,)


def arc_canal(e, cv):
    """L'arc baix de la paret de l'esquerra per on el canal se'n va cap al riu: fosc, i al fons la claror blava."""
    z0, z1, hk = ARC
    zc, r = (z0 + z1) / 2, (z1 - z0) / 2
    pts = []
    for k in range(17):
        a = math.pi * k / 16
        pts.append(_p(XL + 0.5, YA + hk - r + math.sin(a) * r, zc + math.cos(a) * r))
    pts = [_p(XL + 0.5, YA - 2, z1)] + pts + [_p(XL + 0.5, YA - 2, z0)]
    cv.poly(pts, LLUNA, lambda x, y: 1.2 + max(0.0, 1 - abs(y - pts[0][1] + 18) / 30) * 3.0, lit=0)
    # les dovelles de l'arc
    for k in range(0, 17, 2):
        a = math.pi * k / 16
        A = _p(XL + 0.6, YA + hk - r + math.sin(a) * r, zc + math.cos(a) * r)
        B = _p(XL + 0.6, YA + hk - r + math.sin(a) * (r + 12), zc + math.cos(a) * (r + 12))
        cv.line(A[0], A[1], B[0], B[1], PEDRA, 2.0, lit=0)
    for a, b in zip(pts[1:-2], pts[2:-1]):
        cv.line(a[0], a[1], b[0], b[1], PEDRA, 4.8, lit=0)


def comporta(e, cv):
    """La comporta del rec a la paret del fons: el marc de pedra, les posts de fusta, la cremallera de ferro que puja
    fins a la finestra de dalt."""
    x0, x1 = COMPORTA
    e.quad('comporta_marc', (x0 - 10, 70, ZB - 0.5), (x1 + 10, 70, ZB - 0.5), (x1 + 10, YA - 18, ZB - 0.5),
           (x0 - 10, YA - 18, ZB - 0.5), ramp=PEDRA, lvl=lambda s, t, P: carreus(s, t, alt=16, seed=27, base=4.2))
    e.quad('comporta', (x0, 56, ZB - 3), (x1, 56, ZB - 3), (x1, YA - 16, ZB - 3), (x0, YA - 16, ZB - 3), ramp=MULLA,
           lvl=lambda s, t, P: taulons(t, s, ample=11.0, seed=29, base=3.6) - max(0.0, (P[1] - YA)) * 0.0
           - (1.4 if P[1] < YA + 14 else 0))
    for y in (8, 40):
        e.quad('comporta', (x0, y + 3, ZB - 4), (x1, y + 3, ZB - 4), (x1, y, ZB - 4), (x0, y, ZB - 4), ramp=FERRO, lvl=3.4)
    # la cremallera: dues barres de ferro que pugen fins a la finestra
    for dx in (14, x1 - x0 - 14):
        e.cable('comporta', [(x0 + dx, 56, ZB - 5), (x0 + dx, FINESTRA[2] - 2, ZB - 5)], FERRO, 3.2, gruix=3.6)
        for y in range(60, FINESTRA[2] - 6, 9):
            A, B = _p(x0 + dx + 2, y, ZB - 5), _p(x0 + dx + 4, y, ZB - 5)
            cv.line(A[0], A[1], B[0], B[1], FERRO, 4.4, lit=0)
    # l'aigua que s'escola per sota de la comporta (una mica d'escuma)
    for i in range(24):
        u, v = _p(x0 + 4 + i * (x1 - x0 - 8) / 23, YA + 1, ZB - 8 - hr(i, 1, 4) * 6)
        cv.flat(u, v, (170, 196, 200) if hr(i, 2, 4) > 0.4 else (90, 120, 130))


def finestra(e, cv):
    """La finestra de dalt (al pis del torn): la claror blava de l'alba, i la Gueraula que hi treu el cap, amb la mà al
    torn de la comporta."""
    x0, x1, y0, y1 = FINESTRA
    e.quad('finestra', (x0, y1, ZB - 0.4), (x1, y1, ZB - 0.4), (x1, y0, ZB - 0.4), (x0, y0, ZB - 0.4), ramp=LLUNA,
           lvl=lambda s, t, P: 5.4 - t / 40 + (fbm(s / 10, t / 6, 61) - 0.5) * 0.8)
    # l'ampit, de fusta, i els muntants
    e.quad('finestra', (x0 - 6, y0 + 2, ZB - 3), (x1 + 6, y0 + 2, ZB - 3), (x1 + 6, y0 - 6, ZB - 3),
           (x0 - 6, y0 - 6, ZB - 3), ramp=MULLA, lvl=4.6)
    for x in (x0 - 3, x1 + 3):
        e.quad('finestra', (x - 3, y1 + 4, ZB - 2), (x + 3, y1 + 4, ZB - 2), (x + 3, y0, ZB - 2), (x - 3, y0, ZB - 2),
               ramp=MULLA, lvl=3.2)
    # el torn: una roda de radis, al costat de la finestra
    tu, tv = _p(x1 - 4, y0 + 20, ZB - 8)
    k = CAM.escala((x1, y0, ZB))
    rr = 15 * k
    cv.ring(tu, tv, rr, MULLA, 4.6, lit=0, step=6)
    cv.ring(tu, tv, rr - 1, MULLA, 3.0, lit=0, step=6)
    for a in range(0, 360, 60):
        cv.line(tu, tv, tu + math.cos(math.radians(a)) * rr, tv + math.sin(math.radians(a)) * rr, MULLA, 3.6, lit=0)
    cv.disc(tu, tv, 2, 2, FERRO, 4.0, lit=0)
    # la Gueraula: la toca blanca, la cara, el braç que va al torn
    u, v = _p((x0 + x1) / 2 - 10, y0 + 2, ZB - 6)
    r = 9 * k
    TOCA = [(50, 54, 66), (96, 100, 112), (146, 148, 156), (194, 196, 200), (226, 226, 224)]
    CARA = [(70, 42, 34), (120, 78, 60), (166, 116, 90), (200, 152, 120), (224, 184, 150)]
    HABIT = [(10, 10, 12), (20, 20, 24), (32, 32, 38), (48, 48, 56)]
    cv.disc(u, v + r * 0.3, r * 1.5, r * 0.8, HABIT, lambda nx, ny: 2.0 - ny * 0.6, lit=0)     # les espatlles
    cv.disc(u, v - r * 1.1, r * 1.15, r * 1.3, TOCA, lambda nx, ny: 2.8 + nx * 0.4 - ny * 0.6, lit=0)
    cv.disc(u + 0.5, v - r * 0.95, r * 0.7, r * 0.82, CARA, lambda nx, ny: 3.0 + nx * 0.4 - ny * 0.3, lit=0)
    for dx in (-0.3, 0.3):
        cv.flat(u + 0.5 + dx * r, v - r * 1.05, (30, 20, 20))
    cv.flat(u + 0.5, v - r * 0.6, (110, 60, 50))
    for i in range(int(rr + 10)):
        t = i / (rr + 10)
        cv.put(u + r * 1.1 + (tu - u - r * 1.1) * t, v + (tv - v) * t, HABIT, 2.6, lit=0)
        cv.put(u + r * 1.1 + (tu - u - r * 1.1) * t, v + 1 + (tv - v) * t, HABIT, 1.6, lit=0)
    cv.disc(tu - 2, tv + 1, 2.2, 2.2, CARA, 3.2, lit=0)


# ─── La roda ───────────────────────────────────────────────────────────────

ROD_GIR = 0.42                 # la roda, girada: l'eix apunta enrere i cap a l'esquerra (es veuen les pales)


def _rpt(ang, r, dz):
    """Un punt de la roda: a l'angle `ang` del pla de la roda, a `r` del centre, i a `dz` al llarg de l'eix."""
    cx, cy, cz, R, G = ROD
    c, s = math.cos(ROD_GIR), math.sin(ROD_GIR)
    h = math.cos(ang) * r
    return (cx + h * c - dz * s, cy + math.sin(ang) * r, cz + h * s + dz * c)


BANDES = {'aigua': (-999, YA), 'canal': (YA, 0.0), 'aire': (0.0, 999)}


def roda(e, cv, banda):
    """La roda de pales: dues llantes, 16 pales entre les dues i vuit radis per banda; l'eix entra a la paret. Es pinta
    per bandes d'alçada, perquè l'aigua i el terra la tapin on toca: `aigua` (sota l'aigua, fosca: l'aigua s'hi pinta
    al damunt), `canal` (entre l'aigua i el terra, dins el canal) i `aire` (per sobre del terra). El que queda sota el
    terra fora del canal no es pinta."""
    cx, cy, cz, R, G = ROD
    lo, hi = BANDES[banda]
    n = 16
    seg = 48

    def dins(P):
        return lo <= P[1] < hi and not (P[1] < 0 and P[2] < CZ0)

    def clip(A, B):
        """El tros del segment AB dins la banda (per alçada); fora del canal, sota terra, res."""
        ts = [0.0, 1.0]
        for yb in (lo, hi):
            if (A[1] - yb) * (B[1] - yb) < 0:
                ts.append((yb - A[1]) / (B[1] - A[1]))
        ts.sort()
        best = None
        for t0, t1 in zip(ts, ts[1:]):
            M = tuple(A[i] + (B[i] - A[i]) * (t0 + t1) / 2 for i in range(3))
            if t1 - t0 > 1e-6 and dins(M):
                best = (tuple(A[i] + (B[i] - A[i]) * t0 for i in range(3)), tuple(A[i] + (B[i] - A[i]) * t1 for i in range(3)))
        return best

    dl = {'aigua': -1.8, 'canal': -0.7, 'aire': 0.0}[banda]
    # l'eix, que surt de la paret
    if banda == 'aire':
        e.tub('roda', _rpt(0, 0, (ZB - cz) / math.cos(ROD_GIR)), _rpt(0, 0, G / 2), 7, MULLA, 3.0)
    # la llanta del darrere, els radis del darrere
    for k in range(seg):
        c = clip(_rpt(2 * math.pi * k / seg, R, G / 2), _rpt(2 * math.pi * (k + 1) / seg, R, G / 2))
        if c:
            e.cable('roda', list(c), MULLA, 2.4 + dl, gruix=10.0)
    for k in range(8):
        c = clip(_rpt(0, 0, G / 2), _rpt(2 * math.pi * k / 8 + 0.2, R, G / 2))
        if c:
            e.cable('roda', list(c), MULLA, 2.0 + dl, gruix=6.0)
    # les pales: de la llanta cap enfora, entre les dues llantes (de les de dalt a les de baix)
    angs = sorted((2 * math.pi * k / n + 0.1 for k in range(n)), key=lambda a: -math.sin(a))
    for a in angs:
        P0, P1 = _rpt(a, R - 6, -G / 2 - 2), _rpt(a, R + 24, -G / 2 - 2)
        P2, P3 = _rpt(a, R + 24, G / 2 + 2), _rpt(a, R - 6, G / 2 + 2)
        if dins(_rpt(a, R + 9, 0)):
            lv = 3.4 + math.cos(a + 0.8) * 0.9 + dl
            e.quad('roda', P1, P2, P3, P0, ramp=MULLA, lvl=lambda s, t, P, lv=lv: lv + (fbm(s / 4, t / 4, 7) - 0.5)
                   - (1.2 if s < 2 or t < 2 else 0), dues_cares=True)
    # la llanta del davant i els radis del davant
    for k in range(seg):
        c = clip(_rpt(2 * math.pi * k / seg, R, -G / 2), _rpt(2 * math.pi * (k + 1) / seg, R, -G / 2))
        if c:
            ang = 2 * math.pi * (k + 0.5) / seg
            e.cable('roda', list(c), MULLA, 4.4 + math.sin(ang) * 0.8 + dl, gruix=12.0)
    for k in range(8):
        c = clip(_rpt(0, 0, -G / 2), _rpt(2 * math.pi * k / 8 + 0.2, R, -G / 2))
        if c:
            e.cable('roda', list(c), MULLA, 4.0 + dl, gruix=8.0)
    if banda == 'aire':
        u, v = _p(*_rpt(0, 0, -G / 2 - 2))
        k = CAM.escala((cx, cy, cz))
        cv.disc(u, v, 13 * k, 13 * k, MULLA, lambda nx, ny: 4.2 - nx * 0.8 - ny * 1.0, lit=0)
        cv.disc(u, v, 5 * k, 5 * k, FERRO, lambda nx, ny: 4.0 - ny * 1.2, lit=0)
        for a in range(0, 360, 45):
            cv.flat(u + math.cos(math.radians(a)) * 9 * k, v + math.sin(math.radians(a)) * 9 * k, FERRO[2])


def falca(e, cv):
    """La falca d'alzina, clavada entre la pala de baix i la vora del canal: un tascó clar, amb els cops de la maça."""
    x, z = FALCA
    P = [(x - 10, 0.5, z - 6), (x + 14, 0.5, z - 6), (x + 14, 0.5, z + 6), (x - 10, 0.5, z + 6)]
    top = [(x + 6, 16, z - 6), (x + 14, 16, z - 6), (x + 14, 16, z + 6), (x + 6, 16, z + 6)]
    # la cara inclinada (cap a la càmera i cap a l'esquerra), la de dalt (els cops) i el costat
    e.quad('falca', top[3], top[2], (x + 14, 0.5, z - 6), P[0], ramp=ALZINA, lvl=lambda s, t, P_: veta(t, s, seed=71,
           base=4.4), dues_cares=True)
    e.quad('falca', top[3], top[2], top[1], top[0], ramp=ALZINA, lvl=lambda s, t, P_: 5.0
           - (1.6 if hr(int(s), int(t), 72) > 0.8 else 0), dues_cares=True)
    e.quad('falca', top[1], top[2], P[2], P[1], ramp=ALZINA, lvl=2.6, dues_cares=True)
    u, v = _p(x + 10, 16, z)
    cv.flat(u, v - 1, ALZINA[6])


def falca_tallada(e, cv):
    """La falca partida en dos trossos a terra, i estelles al voltant."""
    x, z = FALCA
    for (dx, dz, ang) in ((-26, -24, 0.5), (8, -34, -0.7)):
        e.caixa_girada('falca_tallada', x + dx, z + dz, 16, 8, 6, ang, ALZINA, 4.2,
                       cares={'dalt': {'ramp': ALZINA, 'lvl': 5.2}, 'davant': {'ramp': ALZINA, 'lvl': 3.4}})
    for i in range(14):
        u, v = _p(x - 40 + hr(i, 1, 73) * 70, 0.5, z - 10 - hr(i, 2, 73) * 40)
        cv.put(u, v, ALZINA, 5.6, lit=0)
        cv.put(u + 1, v, ALZINA, 4.2, lit=0)


def pastera(e, cv, al_canal=False):
    """La pastera de pastar el pa: una caixa llarga de fusta, de costats inclinats. Dreta, recolzada a la paret de
    l'esquerra (es veu el clot de dins); o bé al canal, surant, lligada a una anella de la vora."""
    def fusta(seed, base):
        return {'ramp': FUSTA, 'lvl': lambda s, t, P: veta(s, t, seed=seed, base=base)}
    if not al_canal:
        x, z0, L = PASTERA
        z1 = z0 + 38
        top = L
        # dreta sobre un cap, amb el clot de cara a la sala; una mica inclinada contra la paret
        lean = 10
        e.quad('pastera', (x + 2, top, z1), (x + 2, top, z0), (x + 26, 0, z0), (x + 26, 0, z1), **fusta(81, 2.2),
               dues_cares=True)                                           # el fons de dins (fosc)
        for zz, sd in ((z0, 82), (z1, 83)):
            e.quad('pastera', (x + 2, top, zz), (x + 2 + lean + 26, top, zz), (x + 26 + 30, 0, zz), (x + 26, 0, zz),
                   **fusta(sd, 3.2 if zz == z0 else 4.4), dues_cares=True)
        e.quad('pastera', (x + 2 + lean + 26, top, z0), (x + 2 + lean + 26, top, z1), (x + 56, 0, z1), (x + 56, 0, z0),
               **fusta(84, 3.0), dues_cares=True)
        e.linia((x + 2, top + 0.5, z0), (x + 2 + lean + 26, top + 0.5, z0), FUSTA, 6.4)
        e.linia((x + 2, top + 0.5, z1), (x + 2 + lean + 26, top + 0.5, z1), FUSTA, 5.4)
        # una mica de pasta seca i farina al clot
        for i in range(10):
            u, v = _p(x + 18 + hr(i, 1, 85) * 10, 10 + hr(i, 2, 85) * 70, z0 + 6 + hr(i, 3, 85) * 26)
            cv.put(u, v, FARINA, 3.6, lit=0)
    else:
        cx, cz, L, wd = -250, (CZ0 + ZB) / 2 + 4, 96, 34
        y0 = YA - 6
        x0, x1, z0, z1 = cx - L / 2, cx + L / 2, cz - wd / 2, cz + wd / 2
        # el clot (fosc) i les quatre parets, de costats inclinats
        e.quad('pastera_aigua', (x0 + 8, y0 + 2, z1 - 6), (x1 - 8, y0 + 2, z1 - 6), (x1 - 8, y0 + 2, z0 + 6),
               (x0 + 8, y0 + 2, z0 + 6), **fusta(86, 1.6))
        e.quad('pastera_aigua', (x0, y0 + 24, z1), (x1, y0 + 24, z1), (x1 - 8, y0 + 2, z1 - 6), (x0 + 8, y0 + 2, z1 - 6),
               **fusta(87, 3.4), dues_cares=True)
        e.quad('pastera_aigua', (x0, y0 + 24, z1), (x0, y0 + 24, z0), (x0 + 8, y0 + 2, z0 + 6), (x0 + 8, y0 + 2, z1 - 6),
               **fusta(88, 2.6), dues_cares=True)
        e.quad('pastera_aigua', (x1, y0 + 24, z0), (x1, y0 + 24, z1), (x1 - 8, y0 + 2, z1 - 6), (x1 - 8, y0 + 2, z0 + 6),
               **fusta(89, 2.6), dues_cares=True)
        e.quad('pastera_aigua', (x0, y0 + 24, z0), (x1, y0 + 24, z0), (x1 - 8, y0, z0 + 6), (x0 + 8, y0, z0 + 6),
               **fusta(90, 3.8), dues_cares=True)
        for (a, b) in (((x0, z0), (x1, z0)), ((x0, z1), (x1, z1)), ((x0, z0), (x0, z1)), ((x1, z0), (x1, z1))):
            e.linia((a[0], y0 + 24.5, a[1]), (b[0], y0 + 24.5, b[1]), FUSTA, 6.0)
        # l'aigua que l'envolta: una línia d'escuma
        for i in range(40):
            t = i / 39
            u, v = _p(x0 + 2 + t * (L - 4), YA + 0.5, z0 - 1)
            cv.flat(u, v, (150, 180, 186) if hr(i, 1, 91) > 0.3 else (80, 110, 120))
        # la corda, lligada a una anella de la vora
        e.cable('pastera_aigua', [(x1 - 4, y0 + 24, z0 + 2), (x1 + 8, -10, CZ0 + 2), (x1 + 16, 1, CZ0 - 2)], CORDA, 3.0,
                gruix=1.6)
        u, v = _p(x1 + 16, 1, CZ0 - 3)
        cv.ring(u, v, 2, FERRO, 4.0, lit=0, step=30)


def _cilindre(e, sid, cx, cz, r, y0, y1, ramp, lvl, n=20, llum=(-0.6, -0.8)):
    """Un cilindre dret (en quads verticals) amb la tapa de dalt."""
    lx, lz = llum
    for k in range(n):
        a0, a1 = 2 * math.pi * k / n, 2 * math.pi * (k + 1) / n
        A = (cx + math.cos(a0) * r, cz + math.sin(a0) * r)
        B = (cx + math.cos(a1) * r, cz + math.sin(a1) * r)
        am = (a0 + a1) / 2
        lv = lvl + (math.cos(am) * lx + math.sin(am) * lz) * 1.2
        e.quad(sid, (A[0], y1, A[1]), (B[0], y1, B[1]), (B[0], y0, B[1]), (A[0], y0, A[1]), ramp=ramp,
               lvl=lambda s, t, P, lv=lv: lv + (fbm(s / 3, t / 8, 3) - 0.5) * 0.7)
    e.quad(sid, (cx - r, y1, cz + r), (cx + r, y1, cz + r), (cx + r, y1, cz - r), (cx - r, y1, cz - r), ramp=ramp,
           lvl=lambda s, t, P: lvl + 1.2 + (fbm(s / 6, t / 6, 4) - 0.5) * 0.6,
           forma=lambda s, t: (s - r) ** 2 + (t - r) ** 2 <= r * r)


def moles(e, cv):
    """Les moles: la plataforma de taulons, la caixa rodona de fusta que les tapa (la tolva), la tremuja quadrada a
    sobre amb el seu bastiment, i sacs de farina al voltant."""
    cx, cz, ang = MOLES
    G = _gir(cx, cz, ang)
    fusta = {'ramp': FUSTA, 'lvl': lambda s, t, P: veta(s, t, seed=95, base=3.4)}
    e.caixa_girada('moles', cx, cz, 110, 84, 20, ang, FUSTA, 3.0,
                   cares={'dalt': {'ramp': FUSTA, 'lvl': lambda s, t, P: taulons(s, t, ample=14, seed=96, base=4.0)
                                   + _farina_terra(P[0], P[2]) * 1.6},
                          'davant': fusta, 'esquerra': fusta, 'dreta': fusta})
    # la caixa rodona de les moles (tolva), enfarinada
    _cilindre(e, 'moles', cx, cz + 4, 34, 20, 50, FUSTA, 3.6)
    # la mola de dalt treu el cap: pedra
    u, v = _p(cx, 50.5, cz + 4)
    k = CAM.escala((cx, 50, cz))
    cv.disc(u, v, 25 * k, 7 * k, FARINA, lambda nx, ny: 3.2 - ny * 0.8, lit=0)
    cv.disc(u, v, 8 * k, 2.6 * k, FUSTA, 1.6, lit=0)
    # la tremuja: una piràmide al revés, damunt un bastiment de quatre pals
    for dx, dz in ((-26, -22), (26, -22), (26, 22), (-26, 22)):
        e.cable('moles', [(cx + dx * 0.9, 0, cz + 4 + dz), (cx + dx * 0.8, 112, cz + 4 + dz * 0.8)], FUSTA, 3.0,
                gruix=4.0)
    tq, bq = 26, 7
    yt, yb = 116, 82
    zc = cz + 4
    e.quad('moles', (cx - tq, yt, zc - tq), (cx + tq, yt, zc - tq), (cx + bq, yb, zc - bq), (cx - bq, yb, zc - bq),
           ramp=FUSTA, lvl=lambda s, t, P: taulons(s, t, ample=10, seed=97, base=4.0))
    e.quad('moles', (cx - tq, yt, zc + tq), (cx - tq, yt, zc - tq), (cx - bq, yb, zc - bq), (cx - bq, yb, zc + bq),
           ramp=FUSTA, lvl=lambda s, t, P: taulons(s, t, ample=10, seed=98, base=3.0))
    e.quad('moles', (cx + tq, yt, zc - tq), (cx + tq, yt, zc + tq), (cx + bq, yb, zc + bq), (cx + bq, yb, zc - bq),
           ramp=FUSTA, lvl=lambda s, t, P: taulons(s, t, ample=10, seed=99, base=3.4))
    e.quad('moles', (cx - tq, yt, zc + tq), (cx + tq, yt, zc + tq), (cx + tq, yt, zc - tq), (cx - tq, yt, zc - tq),
           ramp=FARINA, lvl=2.8, forma=lambda s, t: 4 < s < 2 * tq - 4 and 4 < t < 2 * tq - 4)
    e.cable('moles', [(cx, yb, zc), (cx + 1, 52, zc - 4)], FARINA, 3.6, gruix=1.4)   # el raig de gra


def sacs(e, cv, llista):
    """Sacs de farina: cossos rodons de tela clara, lligats a dalt, una mica caiguts."""
    for (x, z, h, w, inc) in llista:
        u, v = _p(x, 0, z)
        k = CAM.escala((x, 0, z))
        hh, ww = h * k, w * k
        ombra(cv, u + ww * 0.5, v, ww * 0.8, ww * 0.22, k=0.6)
        cv.disc(u + inc * hh * 0.1, v - hh * 0.45, ww / 2, hh / 2, SAC,
                lambda nx, ny: 2.8 - nx * 0.9 - ny * 0.9 + (fbm(nx * 4, ny * 4, int(x) % 30) - 0.5) * 0.8, lit=0)
        cv.disc(u + inc * hh * 0.18, v - hh * 0.92, ww * 0.18, hh * 0.1, SAC, 2.4, lit=0)   # el nus
        cv.disc(u + inc * hh * 0.2, v - hh * 1.0, ww * 0.12, hh * 0.08, SAC, 4.2, lit=0)


def fanal(cv, fase=0.0):
    """El fanal de ferro que penja d'una biga: una caixa de llauna amb vidres de banya, la flama dins."""
    x, y, z = FANAL
    u, v = _p(x, y, z)
    k = CAM.escala((x, y, z))
    top = _p(x, 300, z)
    cv.line(u, top[1], u, v - 12 * k, FERRO, 2.0, lit=0)
    cv.rect(u - 6 * k, v - 9 * k, u + 6 * k, v + 7 * k, FERRO, 1.6, lit=0)
    cv.rect(u - 5 * k + 1, v - 7 * k, u + 5 * k - 1, v + 6 * k, [(120, 70, 30), (190, 120, 50), (240, 180, 90),
                                                                  (255, 220, 150)], 2.2, lit=0)
    cv.line(u - 6 * k, v - 10 * k, u, v - 14 * k, FERRO, 2.4, lit=0)
    cv.line(u + 6 * k, v - 10 * k, u, v - 14 * k, FERRO, 2.4, lit=0)
    flama(cv, u, v + 4 * k, 7, 2.8, fase, seed=5)
    cv.glow(u, v, 60, (255, 190, 110), 0.25)
    cv.glow(u, v, 14, (255, 230, 170), 0.55)


def bigues(e):
    """Les bigues del sostre (fugen cap al fons) i la del fanal."""
    for x in (-200, 40, 280):
        e.caixa('biga', x - 10, x + 10, 262, 282, ZF, ZB, MULLA, 2.0,
                cares={'sota': {'ramp': MULLA, 'lvl': 1.4}, 'esquerra': {'ramp': MULLA, 'lvl': 2.4},
                       'dreta': {'ramp': MULLA, 'lvl': 1.6}})


def clarors(e):
    """La claror freda de l'alba: la que entra per l'arc del canal i s'escampa per l'aigua i la vora, i la de la
    finestra de dalt a la paret del fons."""
    z0, z1, _ = ARC
    e.claror((XL, 0.5, ZB), (XL + 260, 0.5, ZB), (XL + 260, 0.5, CZ0 - 70), (XL, 0.5, CZ0 - 70), (110, 140, 180),
             lambda s, t: 0.32 * max(0.0, 1 - math.hypot(s / 240, (t - 40) / 120)) ** 1.2)
    e.claror((XL, YA, ZB), (XL + 400, YA, ZB), (XL + 400, YA, CZ0), (XL, YA, CZ0), (90, 130, 160),
             lambda s, t: 0.4 * max(0.0, 1 - s / 400) ** 1.5)


def ombres(e):
    """Ombres a terra: la de les moles, llarga cap a l'esquerra i cap a nosaltres (el fanal és a la dreta), la de la
    roda a la vora del canal, i els racons."""
    cx, cz, _ = MOLES
    e.foscor('ombra', (cx - 150, 0.3, cz + 60), (cx + 40, 0.3, cz + 60), (cx + 40, 0.3, cz - 110), (cx - 150, 0.3, cz - 110),
             lambda s, t: 0.6 * max(0.0, 1 - math.hypot((s - 110 + (170 - t) * 0.35) / 80, (t - 90) / 60)) ** 0.6)
    e.foscor('ombra', (XL, 0.3, CZ0), (XL + 140, 0.3, CZ0), (XL + 140, 0.3, ZF), (XL, 0.3, ZF),
             lambda s, t: 0.45 * max(0.0, 1 - s / 140))
    e.foscor('ombra', (XL, 0.4, CZ0), (XR, 0.4, CZ0), (XR, 0.4, CZ0 - 30), (XL, 0.4, CZ0 - 30),
             lambda s, t: 0.25 * max(0.0, 1 - t / 30))


def primer_pla(cv):
    """Un puntal de fusta a l'esquerra (tallat per dalt i per baix), la biga de dalt i sacs a baix a la dreta."""
    COL = [(5, 5, 6), (10, 9, 10), (18, 15, 14), (28, 23, 20), (40, 33, 27), (54, 45, 36)]
    for y in range(0, BOTTOM + 1):
        x1 = 14 + y * 0.03
        for x in range(0, int(x1) + 1):
            lvl = 2.0 + (x / x1) * 1.0 + (fbm(x / 3, y / 30, 101) - 0.5) * 1.0
            cv.put(x, y, COL, lvl, lit=0)
        cv.put(x1 + 1, y, COL, 3.6, lit=0)                                  # la vora que toca el fanal
    for x in range(0, W):
        for y in range(0, 14 + int(x * 0.015)):
            cv.put(x, y, COL, 1.6 + (fbm(x / 30, y / 3, 102) - 0.5) * 0.8 + (0.8 if y > 10 + x * 0.015 else 0), lit=0)
    # els sacs de baix a la dreta, en silueta (una mica de llum a la vora de dalt)
    for cx, cy, rx, ry in ((598, 262, 44, 30), (548, 270, 34, 22), (630, 236, 26, 30)):
        cv.disc(cx, cy, rx, ry, COL, lambda nx, ny: 2.0 - ny * 1.6 + (fbm(nx * 3, ny * 3, 103) - 0.5) * 0.6, lit=0)


@functools.lru_cache(maxsize=None)
def _davant():
    cv = Canvas(light=LIGHT, transparent=True)
    primer_pla(cv)
    return sense_hud(cv.img)


# ─── Composició ────────────────────────────────────────────────────────────

def _munta(estat=frozenset(), amb_reflexos=True):
    """→ (imatge, Escena) de tota la sala amb un estat ('falca': la falca encara hi és; 'tallada': partida a terra;
    'pastera': la pastera al canal). Sense `amb_reflexos`, l'aigua sense les ratlles de llum (per a l'animació)."""
    cv = Canvas(light=LIGHT)
    e = Escena(cv, CAM, LLUMS, ambient=AMBIENT)
    parets(e)
    canal_sota(e)
    roda(e, cv, 'aigua')
    aigua(e)
    _marca_aigua(e)
    roda(e, cv, 'canal')
    arc_canal(e, cv)
    comporta(e, cv)
    finestra(e, cv)
    terra(e)
    vora_canal(e)
    clarors(e)
    ombres(e)
    bigues(e)
    if 'pastera' in estat:
        pastera(e, cv, al_canal=True)
    roda(e, cv, 'aire')
    if 'falca' in estat:
        falca(e, cv)
    if 'tallada' in estat:
        falca_tallada(e, cv)
    if 'pastera' not in estat:
        pastera(e, cv)
    sacs(e, cv, [(-24, 384, 32, 24, 1), (6, 390, 28, 22, -1)])
    moles(e, cv)
    sacs(e, cv, [(-56, 296, 36, 28, -1), (-30, 284, 30, 24, 1), (240, 300, 34, 26, -1)])
    fanal(cv)
    if amb_reflexos:
        reflexos(cv, e)
    cv.img.alpha_composite(_davant())
    cv.P = cv.img.load()
    hud_negre(cv)
    return cv.img, e


@functools.lru_cache(maxsize=None)
def _escena(estat=frozenset()):
    return _munta(estat)


def _marca_aigua(e):
    """Marca com a «aigua_sup» els píxels de la superfície del canal (per a les ratlles que es mouen): el que es pinti
    després (la roda de sobre l'aigua, la vora) ja en canviarà l'amo."""
    idx = e._index('aigua_sup')
    proj = e._retalla(((XL, YA, ZB), (XR, YA, ZB), (XR, YA, CZ0), (XL, YA, CZ0)))
    for X, Y in e._scan([(p[0], p[1]) for p in proj]):
        e.amo[Y * W + X] = idx


def _render(estat=frozenset()):
    return _escena(frozenset(estat))[0]


def _base():
    """El fons: la pastera a la paret, i sense la falca (és un prop)."""
    return _render()


def bg(cv):
    cv.img.paste(_base())
    cv.P = cv.img.load()


def _decorat(estat, sobre=()):
    def draw(cv):
        cv.img.alpha_composite(sense(_diff(_render(frozenset(estat)), _render(frozenset(sobre))), _davant()))
        cv.P = cv.img.load()
    return draw


PROPS = {
    'falca': _decorat(('falca',)),
    'falca_tallada': _decorat(('tallada',)),
    'pastera_aigua': _decorat(('pastera',)),
}


# ─── Animacions ─────────────────────────────────────────────────────────────

def _frames_aigua():
    """L'aigua del canal corre cap a l'esquerra (les ratlles de llum), i de les pales cauen gotes."""
    img, e = _escena(frozenset())
    davant = _davant()
    n = 16
    cx, cy, cz, R, G = ROD
    frames = []
    for i in range(n):
        cv = Canvas(light=LIGHT, img=_sense_reflexos().copy())
        reflexos(cv, e, fase=i / n)
        # les gotes: cauen de tres pales de baix a l'aigua
        for j, a in enumerate((math.pi * 1.18, math.pi * 1.32, math.pi * 1.7)):
            x0, y0_, z0 = _rpt(a, R + 14, -G / 2)
            t = ((i / n) + j * 0.37) % 1.0
            y = y0_ - t * (y0_ - YA)
            if y > YA + 1:
                u, v = _p(x0, y, z0)
                cv.flat(u, v, (180, 206, 212))
            else:
                u, v = _p(x0, YA, z0)
                cv.flat(u - 1, v, (150, 180, 186))
                cv.flat(u + 1, v, (150, 180, 186))
        frames.append(sense(_diff(cv.img, img), davant))
    return frames


@functools.lru_cache(maxsize=None)
def _sense_reflexos():
    """El fons sense les ratlles de llum de l'aigua (cada fotograma hi pinta les seves)."""
    return _munta(frozenset(), amb_reflexos=False)[0]


def _frames_fanal():
    img = _base()
    davant = _davant()
    x, y, z = FANAL
    u, v = _p(x, y, z)
    k = CAM.escala((x, y, z))
    frames = []
    n = 10
    for i in range(n):
        cv = Canvas(light=LIGHT, img=img.copy())
        cv.rect(u - 5 * k + 1, v - 7 * k, u + 5 * k - 1, v + 6 * k, [(120, 70, 30), (190, 120, 50), (240, 180, 90),
                                                                      (255, 220, 150)], 2.2 + 0.3 * math.sin(i), lit=0)
        flama(cv, u, v + 4 * k, 7, 2.8, i / n, seed=5)
        cv.glow(u, v, 14, (255, 230, 170), 0.5 + 0.1 * math.sin(2 * math.pi * i / n * 2))
        frames.append(sense(_diff(cv.img, img), davant))
    return frames


ANIMS = {'aigua': {'frames': _frames_aigua, 'frameDuration': 110},
         'fanal': {'frames': _frames_fanal, 'frameDuration': 120}}


# ─── Capes del davant ─────────────────────────────────────────────────────

@functools.lru_cache(maxsize=None)
def _moles_img():
    img, e = _escena(frozenset())
    ids = {i for i, sid in enumerate(e.ids) if sid == 'moles'}
    out = Image.new('RGBA', img.size, (0, 0, 0, 0))
    src, dst = img.load(), out.load()
    for k, a in enumerate(e.amo):
        if a in ids:
            x, y = k % W, k // W
            if y <= BOTTOM:
                dst[x, y] = src[x, y]
    # (i els sacs de davant les moles, que són de pantalla: el que hi ha a sota de la línia base, al voltant)
    return out


def _moles_base():
    cx, cz, ang = MOLES
    G = _gir(cx, cz, ang)
    return round(max(_p(*G(-55, 0, -42))[1], _p(*G(55, 0, -42))[1]) - 6)


FRONT = [{'id': 'davant_moles', 'mask': mascara(_moles_img()), 'baseline': _moles_base(), 'zIndex': 20},
         {'id': 'davant', 'mask': mascara(_davant()), 'baseline': 999, 'zIndex': 20}]


# ─── Geometria ─────────────────────────────────────────────────────────────

def _geometria():
    img, e = _escena(frozenset())
    C = e.caixes
    cx, cy, cz, R, G = ROD
    roda_r = rect_de(_p(cx - R - 16, cy + R + 16, cz), _p(cx + R + 16, YA, cz), pad=0)
    fx, fz = FALCA
    things = {
        'roda': {'rect': roda_r, 'walk': _p(cx + 10, 0, CZ0 - 36)},
        'falca': {'rect': rect_de(_p(fx - 12, 18, fz), _p(fx + 16, 0, fz - 6), pad=4), 'walk': _p(fx - 20, 0, CZ0 - 34)},
        'comporta': {'rect': rect_de(_p(COMPORTA[0] - 10, 70, ZB), _p(COMPORTA[1] + 10, YA, ZB), pad=1),
                     'walk': _p((COMPORTA[0] + COMPORTA[1]) / 2, 0, CZ0 - 30)},
        'finestra_dalt': {'rect': rect_de(_p(FINESTRA[0] - 30, FINESTRA[3] + 6, ZB), _p(FINESTRA[1] + 30, FINESTRA[2] - 10, ZB),
                                          pad=2),
                          'walk': _p((FINESTRA[0] + FINESTRA[1]) / 2 - 30, 0, CZ0 - 40)},
        'pastera': {'rect': rect_de(_p(PASTERA[0], PASTERA[2] + 4, PASTERA[1]), _p(PASTERA[0] + 58, 0, PASTERA[1] + 38),
                                    pad=3),
                    'walk': _p(PASTERA[0] + 80, 0, PASTERA[1] + 14)},
        'canal': {'rect': rect_de(_p(XL + 20, 2, ZB), _p(cx - R - 20, YA, CZ0), pad=0), 'walk': _p(-60, 0, CZ0 - 30)},
        'moles': {'rect': rect_de((C['moles'][0], C['moles'][1]), (C['moles'][2], C['moles'][3])),
                  'walk': _p(MOLES[0] + 90, 0, MOLES[1] - 70)},
    }
    # el terra on es camina: de la vora del canal fins a baix; sense el puntal ni els sacs del primer pla
    zv = CZ0 - 8
    walk = [_p(XL + 70, 0, zv), _p(XR - 120, 0, zv), (639, _p(XR - 120, 0, zv)[1] + 6), (639, 214), (560, 232),
            (500, 250), (40, 250), _p(XL + 70, 0, 320)]
    v_top = min(p[1] for p in walk)
    v_bot = max(p[1] for p in walk)
    mx, mz, ang = MOLES
    Gm = _gir(mx, mz, ang)
    forat = [_p(*Gm(lx, 0, lz)) for lx, lz in ((-58, -46), (58, -46), (58, 46), (-58, 46))]
    llum_fanal = llum_personatge(CAM, FANAL, 330, (255, 186, 110), 0.8)
    llum_arc = llum_personatge(CAM, (XL + 40, 60, (ARC[0] + ARC[1]) / 2), 260, (130, 160, 210), 0.4)
    llum_fin = llum_personatge(CAM, ((FINESTRA[0] + FINESTRA[1]) / 2, 60, ZB - 60), 240, (140, 170, 210), 0.3)
    peu = _p(-20, 0, 290)
    return {
        'things': things,
        'spawns': {'iri': peu, 'vet': _p(70, 0, 300)},
        'walkable': walk,
        'forats': [forat],
        'floorSquash': 0.42,
        'regions': [{'id': 'perspectiva', 'active': True, 'scaleEnabled': True, 'scaleWalkSpeed': True,
                     'scaleTop': round(_escala_a(v_top - 4), 3), 'scaleBottom': round(_escala_a(v_bot + 4), 3),
                     'points': [(0, v_top - 4), (W - 1, v_top - 4), (W - 1, v_bot + 4), (0, v_bot + 4)]}],
        # la llum dominant és el fanal (al mig, una mica a la dreta)
        'characterShadow': {'enabled': True, 'color': '#06080a', 'alpha': 0.42, 'squash': 0.4, 'core': 0.6,
                            'light': {'x': _p(FANAL[0], 0, FANAL[2])[0], 'y': _p(FANAL[0], 0, FANAL[2])[1],
                                      'stretch': 0.8, 'reach': 150}},
        'characterLights': {'ambient': '#5c6470', 'lights': [llum_fanal, llum_arc, llum_fin]},
    }


GEOMETRIA = _geometria()
