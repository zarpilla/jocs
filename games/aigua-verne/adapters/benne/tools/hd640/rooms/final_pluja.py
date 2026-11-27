"""
Cinemàtica final: el pati de la granja tres setmanes després, **plovent**. Sala «de lluny» (persones de ≈83 px).
EN 3D (hd640/tres_d.py), a 1×.

És l'escena 3D del pati (granja_pati.py: la mateixa càmera i la mateixa geometria), mullada, i el llenç de 640 en
mostra la meitat esquerra (la que es veu del pati quan la càmera és a l'esquerra): la masia girada, amb la cadira de
boga del pare a la porta (en Quim hi seu, amb el paraigua tancat); l'olivera amb un brot; el pou ple fins a dalt; la
bomba de Verne apagada amb el cartell del banc («BANC DE VESPER»); el panell de la carretera amb el preu nou (AIGUA
VESPER ▼); la tanca; la Canonada que es perd dins els núvols; i les roques del primer pla. El cel tapat i gris, la
terra fosca i xopa, bassals que reflecteixen el cel (en coordenades del món: s'empetiteixen cap al fons) i brots
verds a la carena dels solcs. No hi ha sol: la llum ve de dalt, i les ombres són taques suaus sota les coses.

El detall (la façana, la bomba, l'olivera, el panell, la cadira) ve del pati pla de sempre (granja_estreta_comu.py)
dibuixat mullat (`wet=True`) i projectat.
Props (decorats): `barril_pou` (l'últim barril de la Cantimplora, al costat del pou) i `caixa_ferrum` (la caixa de
fusta amb el segell de Ferrum): es dibuixen plans com sempre i es posen drets al lloc del món que toca, a escala.
ANIMS: `pluja` (la pluja en perspectiva: les gotes de prop, grosses, llargues i ràpides; les de lluny, fines i
lentes, i darrere de les coses; els esquitxos i els cercles als bassals i al pou).
"""
import functools
import math

import hd640  # noqa: F401  (posa la llibreria de dibuix a 640×360)
from PIL import Image

from hd.pix import Canvas, Light, W, H, hr, mix
from hd.rooms.exterior import fbm, smooth
from hd640.rooms import granja_estreta_comu as G
from hd640.rooms import granja_pati as P
from hd640.rooms.terra2_comu import (
    RH, OLIVE, ORANGE, RUSTT, IRONR, BLACKT, WATER, STONE, MUD, RSKY, RHILL, SPROUT, GREYW,
    text, text_width, rain_sky, canonada)
from hd640.tres_d import Escena, Llum

# La càmera i el món del pati, tal qual: la sala (640) n'és la meitat esquerra.
CAM, HOR = P.CAM, P.HOR
POU, POU_R, POU_H = P.POU, P.POU_R, P.POU_H
BOMBA, ARBRE, PANELL = P.BOMBA, P.ARBRE, P.PANELL

LIGHT = Light(ambient=0.0, vignette=None, floor_fade=None)       # (la llum és la del món: la de l'Escena)
LLUMS = [Llum((-300, 60000, 900), 1e6, 1.5, power=1.0)]          # el cel tapat: la llum ve de dalt
AMBIENT = -1.5

# la llum dels dibuixos plans (textures i decorats): el cel tapat, de tot arreu, sense vinyeta
LIGHT_PLA = Light(ambient=0.2, vignette=None, floor_fade=None)
LIGHT_PLA.point(320, -120, r=700, k=0.7, power=1.0)

# On són les coses noves (x, z del món)
CADIRA = None                                      # (es calcula: davant la porta de la casa, a la dreta)
BARRIL = (-432.0, 610.0)                           # al costat del pou, cap a la casa
CAIXA = (-262.0, 676.0)                            # davant la bomba, a la dreta
BASSALS = [                                        # (x, z, radi x, radi z): on el pati fa clot
    (-262, 548, 46, 20), (-96, 602, 58, 24), (-418, 528, 30, 12), (-190, 688, 34, 16), (-30, 760, 50, 20),
    (-560, 470, 40, 14), (-330, 840, 44, 18), (90, 520, 36, 14),
]


def _cadira_peu():
    # la cadira, a la dreta de la porta (al pla, la porta és a x≈103 i la cadira a 133), a 22 unitats de la façana (dins el terra on es camina)
    p = P._facana(133, 184)
    return (p[0] + P.NF[0] * 22, 0.0, p[2] + P.NF[2] * 22)


CADIRA = _cadira_peu()


# ─── Les textures: el pati pla de sempre, mullat ─────────────────────────────

def _pla(fn):
    cv = Canvas(light=LIGHT_PLA, transparent=True)
    fn(cv)
    return cv.img


@functools.lru_cache(maxsize=None)
def _textures():
    return {
        'masia': _pla(lambda cv: G.masia(cv, wet=True)),
        'bomba': _pla(lambda cv: G.bomba(cv, wet=True)),
        'arbre': _pla(lambda cv: G.arbre(cv, wet=True)),
        'panell': _pla(lambda cv: G.panel(cv, wet=True)),
        'cadira': _pla(G.cadira).crop((118, 170, 150, 202)),       # (el peu, a (15, 27))
    }


# ─── El fons (en pantalla): el cel tapat, les dunes, la Canonada ───────────────

def fons(cv):
    rain_sky(cv, HOR)
    for x in range(W):                                             # les dunes, fosques i mullades
        h1 = HOR - 3 - 16 * fbm(x / 170, 0.3, 7) - 6 * fbm(x / 40, 0.9, 8)
        h2 = HOR - 1 - 7 * fbm(x / 70, 1.7, 9)
        for y in range(int(h1), HOR + 5):
            cv.put(x, y, RHILL, 3.6 - (y - h1) * 0.04 + (fbm(x / 30, y / 6, 4) - 0.5) * 0.6, lit=0)
        for y in range(int(h2), HOR + 5):
            cv.put(x, y, RHILL, 2.6 + (fbm(x / 8, y / 4, 3) - 0.5) * 0.8 - (y - h2) * 0.05, lit=0)
    canonada(cv, P.CAN_U, HOR + 1, haze=(150, 152, 150))
    # els núvols s'empassen la Canonada
    cv.tint(P.CAN_U - 8, 0, P.CAN_U + 8, 44, (150, 152, 152), lambda x, y: 0.9 - y / 50)


# ─── El terra (en el món), xop ────────────────────────────────────────────────

def _terra(s, t, Pw):
    return P._terra(s, t, Pw) - 0.6 + (fbm(Pw[0] / 30, Pw[2] / 20, 77) - 0.5) * 0.4


def _bassal_forma(rx, rz):
    def f(s, t):
        x, z = (s - rx) / rx, (t - rz) / rz
        return x * x + z * z <= 1 - (fbm((s + rx * 7) / 14, t / 6, 91) - 0.5) * 0.7
    return f


def bassals(e):
    for k, (cx, cz, rx, rz) in enumerate(BASSALS):
        P0, P1 = (cx - rx, 0.25, cz + rz), (cx + rx, 0.25, cz + rz)
        P2, P3 = (cx + rx, 0.25, cz - rz), (cx - rx, 0.25, cz - rz)
        # la vora, fangosa, i a dins el reflex del cel gris (més clar a la vora del fons: hi veu el cel baix)
        e.quad('bassal', P0, P1, P2, P3, ramp=MUD, lvl=1.2, forma=_bassal_forma(rx * 1.08, rz * 1.15))
        e.quad('bassal', P0, P1, P2, P3, ramp=RSKY,
               lvl=lambda s, t, Pw, rz=rz: 3.3 - t / (2 * rz) * 1.4 + (fbm(Pw[0] / 26, Pw[2] / 4, 3) - 0.5) * 1.2
               + (1.0 if fbm(Pw[0] / 8, Pw[2] / 2, 5) > 0.68 else 0),
               forma=_bassal_forma(rx, rz))


def brots(e):
    """Els brots verds a la carena dels solcs dels camps (cada brot, una cel·la del món: s'empetiteixen sols)."""
    z0, z1, x0, x1 = 930.0, 3200.0, -4200.0, 400.0

    def forma(s, t):
        x, z = x0 + s, z1 - t
        fur = math.sin(x / 9.0 * math.pi)
        dens = 0.3 * (1 - smooth(1100, 2600, z))
        return fur > 0.55 and hr(int(x // 3), int(z // 5), 77) < dens

    e.quad('brots', (x0, 0.4, z1), (x1, 0.4, z1), (x1, 0.4, z0), (x0, 0.4, z0), ramp=SPROUT,
           lvl=lambda s, t, Pw: 1.4 + hr(int(Pw[0]), int(Pw[2]), 3) * 1.4, forma=forma)


# ─── Les peces ──────────────────────────────────────────────────────────────

def pou(e):
    """El pou del pati, però ple d'aigua fins a dalt."""
    cx, cz = POU

    def pedra(a, y, Pw):
        row = int(y // 6)
        colf = a * 5 + (0.5 if row % 2 else 0)
        v = 2.8 + (hr(row, round(colf)) - 0.5) * 1.0 - (0.6 if y > POU_H - 8 else 0)
        if y % 6 < 1 or abs(colf - round(colf)) < 0.09:
            v -= 1.8
        return v
    P.cilindre(e, 'pou', cx, cz, POU_R, 0, POU_H, STONE, pedra)
    r, ri = POU_R, POU_R - 5
    sq = ((cx - r, POU_H, cz + r), (cx + r, POU_H, cz + r), (cx + r, POU_H, cz - r), (cx - r, POU_H, cz - r))
    e.quad('pou_vora', *sq, ramp=STONE,
           lvl=lambda s, t, Pw: 4.2 - (1.6 if abs(math.atan2(Pw[2] - cz, Pw[0] - cx) * 4 % 1) < 0.12 else 0),
           forma=lambda s, t: ri * ri <= (s - r) ** 2 + (t - r) ** 2 <= r * r)
    sqa = tuple((p[0], POU_H - 1.0, p[2]) for p in sq)
    e.quad('pou_aigua', *sqa, ramp=WATER,
           lvl=lambda s, t, Pw: 3.6 - t / (2 * r) * 1.4 + (1.6 if abs(t - r * 0.8) < 1.6 and s > r * 0.7 else 0),
           forma=lambda s, t: (s - r) ** 2 + (t - r) ** 2 < ri * ri)
    for px in (cx - 22, cx + 22):
        e.caixa('pou_pals', px - 2, px + 2, POU_H, 74, cz - 2, cz + 2, GREYW, 2.6)
    e.caixa('pou_pals', cx - 27, cx + 27, 74, 78, cz - 3, cz + 3, GREYW, 3.0)
    e.tub('pou_pals', (cx, 67, cz - 3), (cx, 67, cz + 3), 5, IRONR, 2.2)
    e.cable('pou_pals', [(cx - 5, 67, cz), (cx - 5, POU_H + 1, cz)], P.PLANK, 2.8, gruix=0.8)
    e.cable('pou_pals', [(cx + 5, 67, cz), (cx + 5, 54, cz)], P.PLANK, 2.8, gruix=0.8)
    P.cilindre(e, 'pou_pals', cx + 5, cz, 6, 42, 54, IRONR, lambda a, y, Pw: 2.6 - (1.2 if abs(y - 49) < 0.8 else 0),
               n=12)


def tanca(e):
    """La tanca del pati (com a granja_pati.tanca), però només el tros que cau dins la sala: cada pal és una
    superfície i l'Escena en recorda com a molt 255."""
    (x0, z0), (x1, z1) = P.TANCA0, P.TANCA1
    n = int(math.hypot(x1 - x0, z1 - z0) // 44)
    tops = []
    for i in range(n + 1):
        u = i / n
        x, z = x0 + (x1 - x0) * u, z0 + (z1 - z0) * u
        tops.append((x, z))
        if CAM.projecta((x, 0, z))[0] > W + 40:
            break
        lean = (hr(i, 3) - 0.5) * 3
        e.caixa('tanca', x - 1.5, x + 1.5, 0, 26 + lean, z - 1.5, z + 1.5, GREYW, 2.8)
    for h in (10, 20):
        for (xa, za), (xb, zb) in zip(tops, tops[1:]):
            e.cable('tanca', [(xa, h, za), ((xa + xb) / 2, h - 1.4, (za + zb) / 2), (xb, h, zb)], GREYW, 3.4, gruix=0.9)


def ombres(e):
    """El cel tapat no fa ombres llargues: només una taca fosca i suau just a sota de cada cosa."""
    def taca(cx, cz, rx, rz, k=0.5):
        e.foscor('ombra', (cx - rx, 0.3, cz + rz), (cx + rx, 0.3, cz + rz), (cx + rx, 0.3, cz - rz),
                 (cx - rx, 0.3, cz - rz),
                 lambda s, t: k * min(1.0, 1.6 * max(0.0, 1 - ((s - rx) / rx) ** 2 - ((t - rz) / rz) ** 2)))
    taca(POU[0], POU[1], 36, 34)
    taca(BOMBA[0], BOMBA[1], 22, 16)
    taca(ARBRE[0], ARBRE[1], 14, 8, 0.4)
    taca(CADIRA[0], CADIRA[2], 13, 8, 0.5)
    # al peu de la façana, l'aigua que regalima del ràfec: una franja fosca
    a, b = P._facana(-4, 184), P._facana(212, 184)
    e.foscor('ombra', (a[0], 0.3, a[2]), (b[0], 0.3, b[2]), (b[0] + P.NF[0] * 14, 0.3, b[2] + P.NF[2] * 14),
             (a[0] + P.NF[0] * 14, 0.3, a[2] + P.NF[2] * 14), lambda s, t: 0.45 * (1 - t / 14))


# ─── Composició ─────────────────────────────────────────────────────────────

def escena(cv, tex):
    e = Escena(cv, CAM, LLUMS, ambient=AMBIENT)
    fons(cv)
    zn = 300
    e.quad('terra', (-80000, 0, 20000), (80000, 0, 20000), (80000, 0, zn), (-80000, 0, zn), ramp=MUD, lvl=_terra)
    e.claror((-80000, 0.2, 20000), (80000, 0.2, 20000), (80000, 0.2, 900), (-80000, 0.2, 900), (124, 128, 132),
             lambda s, t: 0.7 * smooth(1200, 9000, 20000 - t))             # la cortina de pluja: el fons s'esvaeix
    brots(e)
    bassals(e)
    ombres(e)
    # de lluny a prop
    P.panell(e, tex)
    tanca(e)
    P.bomba(e, tex)
    e.sprite('arbre', tex['arbre'], (232, 188), (ARBRE[0], 0, ARBRE[1]), escala_img=1.5)
    pou(e)
    P.masia(e, tex)
    e.sprite('cadira', tex['cadira'], (15, 27), CADIRA)
    P.roques(e)
    # tot, més fred i apagat; i la cortina de pluja, que s'empassa la part de dalt
    cv.tint(0, 0, W - 1, RH - 1, (96, 104, 112), 0.16)
    cv.tint(0, 0, W - 1, 190, (170, 176, 180), lambda x, y: 0.18 * (1 - y / 190))
    return e


@functools.lru_cache(maxsize=None)
def _base():
    cv = Canvas(light=LIGHT)
    e = escena(cv, _textures())
    for y in range(RH, H):                                         # sota la sala: negre
        for x in range(W):
            cv.flat(x, y, (0, 0, 0))
    return cv.img, e


def bg(cv):
    img, _ = _base()
    cv.img.paste(img)
    cv.P = cv.img.load()


# ─── Profunditat de cada píxel (per tapar la pluja i els decorats) ─────────────

_Z_ID = {'masia': 540, 'cadira': 520, 'pou': 640, 'pou_vora': 650, 'pou_aigua': 650, 'pou_pals': 650,
         'bomba': 726, 'arbre': 700, 'tanca': 1600, 'panell': 1050, 'primer_pla': 470,
         'tub0': 720, 'tub1': 700, 'tub2': 680, 'tub3': 668}
_TERRA = {'terra', 'bassal', 'brots'}


def _z(e, x, y):
    """La profunditat del que es veu al píxel (x, y) de sala (infinit: el cel)."""
    sid = e.ids[e.amo[y * e.cv.w + x]]
    if sid in _TERRA:
        return CAM.f * CAM.pos[1] / max(0.5, y + 0.5 - HOR)
    return _Z_ID.get(sid, 1e9)


# ─── Props: dibuixats plans, posats drets al món ───────────────────────────────

WOODF = [(30, 22, 16), (48, 36, 24), (70, 52, 34), (94, 72, 46), (118, 92, 60), (142, 114, 76), (164, 136, 94)]


def _barril_pla(cv):
    """L'últim barril de la Cantimplora: oliva, amb les cèrcols i la franja taronja, el rètol de la Vet («NO. PER
    SI DE CAS.») mig desenganxat, i xop."""
    cx, base, rx, h = 254, 214, 12, 34
    for y in range(base - h, base + 1):
        bulge = 1 + 0.08 * math.sin((y - base + h) / h * math.pi)
        w = rx * bulge
        for x in range(int(cx - w), int(cx + w) + 1):
            u = (x - cx) / w
            hoop = (y - base + h) in (3, 4, h - 4, h - 3)
            band = h // 2 - 3 <= (y - base + h) <= h // 2 + 1
            lvl = 3.4 + u * 1.2 - abs(u) ** 4 * 1.6 + (0.9 if hoop else 0)
            ramp = ORANGE if band else OLIVE
            if fbm(x / 3, y / 8, 9) > 0.7:
                ramp = RUSTT
            cv.put(x, y, ramp, lvl - (0.6 if band else 0))
        if (y - base + h) % 5 == 0:                                         # la pluja hi regalima
            cv.put(cx + int(rx * 0.5), y, OLIVE, 5.2)
    cv.disc(cx, base - h, rx, 3, OLIVE, lambda nx, ny: 3.0 + nx * 0.6 - ny * 0.4)
    cv.disc(cx, base - h, rx - 2, 2, WATER, lambda nx, ny: 3.6 - ny, lit=0)   # aigua a la tapa
    cv.disc(cx + 5, base - h, 1.6, 1, IRONR, 4.0)                            # el tap
    cv.poly([(cx - 9, base - 22), (cx + 3, base - 23), (cx + 4, base - 15), (cx - 8, base - 13)],
            [(150, 140, 120), (196, 188, 166), (226, 220, 200)], 1.6)        # el rètol de la Vet, mig desenganxat
    for k in range(3):
        cv.line(cx - 7, base - 21 + k * 2.4, cx + 1, base - 22 + k * 2.4, BLACKT, 1.2)


def _caixa_pla(cv):
    """La caixa de fusta que arriba de Ferrum: taules clavades, el segell de Ferrum cremat (l'engranatge i el
    martell) i, al damunt, la nota d'en Bru («Per si de cas.») sota una pedra."""
    x0, x1, base, h = 380, 416, 228, 22
    top = base - h
    cv.poly([(x0, top), (x1, top), (x1 - 4, top - 6), (x0 - 4, top - 6)], WOODF,
            lambda x, y: 4.0 - (1.4 if (y - top) % 3 == 0 else 0))               # la tapa
    cv.poly([(x0 - 4, top - 6), (x0, top), (x0, base), (x0 - 4, base - 5)], WOODF, 1.8)   # el costat
    cv.rect(x0, top, x1, base, WOODF, lambda x, y: 3.2 - (1.6 if (y - top) % 7 == 0 else 0) +
            (fbm(x / 4, y / 9, 7) - 0.5) * 0.8)
    for sx in (x0 + 1, x1 - 1):
        cv.rect(sx, top, sx, base, WOODF, 4.2)
    cv.line(x0 + 1, top + 1, x1 - 1, base - 1, WOODF, 4.0)                  # la creu de reforç
    cx, cy = (x0 + x1) // 2, top + 11                                        # el segell cremat
    for a in range(0, 360, 30):
        ar = math.radians(a)
        cv.put(cx + math.cos(ar) * 6, cy + math.sin(ar) * 5, BLACKT, 1.6)
    cv.ring(cx, cy, 4, BLACKT, 1.4, step=20)
    cv.line(cx - 2, cy + 2, cx + 2, cy - 2, BLACKT, 1.0)
    cv.rect(cx + 1, cy - 3, cx + 3, cy - 2, BLACKT, 1.0)
    text(cv, 'FERRUM', cx - text_width('FERRUM') // 2, base - 6, BLACKT, 1.0, lit=0, flat=(40, 28, 20))
    cv.poly([(x0 + 8, top - 3), (x0 + 20, top - 4), (x0 + 22, top - 1), (x0 + 9, top)],
            [(150, 140, 120), (196, 188, 166), (226, 220, 200)], 1.8)       # la nota d'en Bru, sota una pedra
    cv.disc(x0 + 15, top - 4, 3, 2, [(60, 56, 50), (90, 84, 76), (120, 114, 104)], lambda nx, ny: 1.6 + nx - ny)


def _dret(draw, retall, peu_img, peu, rx, rz):
    """Un dibuix pla dret al món, a escala, amb la taca d'ombra a sota; tapat pel que hi hagi més a prop."""
    from pixels import nearest
    _, e = _base()
    cv = Canvas(light=LIGHT_PLA, transparent=True)
    draw(cv)
    img = cv.img.crop(retall)
    out = Image.new('RGBA', (W, H), (0, 0, 0, 0))
    o = out.load()
    zp = CAM.vista(peu)[2]
    # la taca d'ombra, al terra
    u0, v0, _ = CAM.projecta((peu[0] - rx, 0, peu[2] + rz))
    u1, v1, _ = CAM.projecta((peu[0] + rx, 0, peu[2] - rz))
    cu, cvv, _ = CAM.projecta(peu)
    hu, hv = (u1 - u0) / 2, (v1 - v0) / 2
    for y in range(int(v0) - 1, int(v1) + 2):
        for x in range(int(u0) - 1, int(u1) + 2):
            if not (0 <= x < W and 0 <= y < RH):
                continue
            d = ((x + 0.5 - cu) / hu) ** 2 + ((y + 0.5 - cvv) / max(0.5, hv)) ** 2
            if d < 1 and _z(e, x, y) >= zp - 20:
                o[x, y] = (12, 10, 10, int(150 * min(1.0, 1.5 * (1 - d))))
    # el dibuix
    k = CAM.escala(peu)
    w, h = max(1, round(img.width * k)), max(1, round(img.height * k))
    im = nearest(img, (w, h)) if k >= 1 else img.resize((w, h), Image.Resampling.BOX)
    ox, oy = round(cu - peu_img[0] * k), round(cvv - peu_img[1] * k)
    src = im.load()
    for y in range(h):
        for x in range(w):
            X, Y = ox + x, oy + y
            if 0 <= X < W and 0 <= Y < RH and src[x, y][3] >= 128 and _z(e, X, Y) >= zp - 6:
                c = src[x, y]
                o[X, Y] = (int(c[0] * 0.86), int(c[1] * 0.88), int(c[2] * 0.92), 255)   # (el fred de la pluja)
    return out


def barril_pou(cv):
    cv.img.alpha_composite(_dret(_barril_pla, (238, 176, 270, 218), (16, 38), (BARRIL[0], 0, BARRIL[1]), 14, 8))


def caixa_ferrum(cv):
    cv.img.alpha_composite(_dret(_caixa_pla, (372, 194, 422, 232), (26, 34), (CAIXA[0], 0, CAIXA[1]), 22, 12))


def peix(cv):
    """El peix platejat que en Diu deixa als peus de la Iri (tasca 142): petit, de costat a terra, xop, amb la cua
    cap a la dreta i un ull fosc."""
    out = Image.new('RGBA', (W, H), (0, 0, 0, 0))
    o = out.load()
    x0, y0, n = 412, 230, 11                                   # el musell, a l'esquerra dels peus de la Iri
    for i in range(n):
        t = i / (n - 1)
        half = round(2.2 * math.sin(math.pi * min(1.0, t * 1.15)))   # el cos, més gruixut cap al cap
        for dy in range(-half, half + 1):
            top = dy < 0
            c = (150, 160, 170) if top else (206, 214, 220)
            if dy == 0 and 2 < i < n - 2:
                c = (232, 238, 242)                                  # la llum de l'aigua al llom
            o[x0 + i, y0 + dy] = c + (255,)
    for dy in (-2, -1, 0, 1, 2):                                     # la cua
        o[x0 + n, y0 + dy] = (128, 138, 150, 255)
        if abs(dy) == 2:
            o[x0 + n + 1, y0 + dy] = (128, 138, 150, 255)
    o[x0 + 2, y0 - 1] = (20, 22, 26, 255)                           # l'ull
    for i in range(1, n):                                            # l'ombra, a terra
        if not o[x0 + i, y0 + 3][3]:
            o[x0 + i, y0 + 3] = (12, 10, 10, 90)
    cv.img.alpha_composite(out)


PROPS = {'barril_pou': barril_pou, 'caixa_ferrum': caixa_ferrum, 'peix': peix}


# ─── La pluja, en perspectiva ──────────────────────────────────────────────────

RAIN_N = 20                                   # fotogrames (a 70 ms): en 20 tot torna on era
SLANT = 0.2                                   # el vent ve de la dreta: cada unitat que baixa, 0,2 cap a l'esquerra


def _frames_pluja():
    base, e = _base()
    src = base.load()
    # les gotes: una posició del món (x, z) i una fase; cauen de dalt de la pantalla fins a terra. Les de prop fan
    # més voltes per bucle (van més de pressa en pantalla) i fan la ratlla més llarga i gruixuda.
    drops = []
    for k in range(700):
        z = 1 / (1 / 2600 + hr(k, 4) * (1 / 150 - 1 / 2600))
        u = -40 + hr(k, 1) * (W + 120)
        x = (u - CAM.centre[0]) * z / CAM.f
        top = CAM.pos[1] + (HOR + 10) * z / CAM.f                  # l'alçada del món que cau a la vora de dalt
        voltes = 3 if z < 320 else 2 if z < 700 else 1
        drops.append((x, z, top, hr(k, 2), voltes))
    rings = []                                                     # els cercles: als bassals i al pou
    for k in range(60):
        cx, cz, rx, rz = BASSALS[k % len(BASSALS)]
        a, r = hr(k, 11) * 2 * math.pi, math.sqrt(hr(k, 12)) * 0.75
        rings.append((cx + math.cos(a) * rx * r, 0.3, cz + math.sin(a) * rz * r, int(hr(k, 13) * RAIN_N)))
    for j in range(10):
        a, r = hr(j, 21) * 2 * math.pi, math.sqrt(hr(j, 22)) * (POU_R - 9)
        rings.append((POU[0] + math.cos(a) * r, POU_H - 0.8, POU[1] + math.sin(a) * r, int(hr(j, 23) * RAIN_N)))
    splashes = []
    for k in range(110):
        z = 470 + hr(k, 32) * 900
        x = (hr(k, 31) * (W + 20) - 10 - CAM.centre[0]) * z / CAM.f
        splashes.append((x, z, int(hr(k, 33) * RAIN_N)))

    frames = []
    for i in range(RAIN_N):
        img = Image.new('RGBA', (W, H), (0, 0, 0, 0))
        p = img.load()

        def put(x, y, col, a, z):
            x, y = int(x), int(y)
            if 0 <= x < W and 0 <= y < RH and _z(e, x, y) > z:
                o = p[x, y] if p[x, y][3] else src[x, y]
                p[x, y] = mix(o, col, min(0.85, a)) + (255,)

        for x0, z, top, fase, voltes in drops:
            caiguda = top / RAIN_N * voltes                        # unitats del món per fotograma
            y = top - ((fase * top + i * caiguda) % top)
            x = x0 - SLANT * (top - y)
            ln = caiguda * 0.8
            A = CAM.projecta((x, y, z))
            B = CAM.projecta((x + SLANT * ln, y + ln, z))
            k = CAM.escala((x, y, z))
            gruix = 2 if k > 1.9 else 1
            alfa = 0.16 + 0.32 * min(1.0, k / 1.8)
            n = max(1, int(math.hypot(B[0] - A[0], B[1] - A[1])))
            for j in range(n + 1):
                t = j / n
                xx, yy = A[0] + (B[0] - A[0]) * t, A[1] + (B[1] - A[1]) * t
                a = alfa * (1.0 - 0.6 * t)                          # la punta de baix, més marcada
                for g in range(gruix):
                    put(xx + g, yy, (206, 214, 222), a, z)
        for x, y0, z, s in rings:                                  # els cercles creixen 4 fotogrames
            age = (i - s) % RAIN_N
            if age < 4:
                r = 1.5 + age * 2.6
                zz = CAM.vista((x, y0, z))[2]
                for a in range(0, 360, 15 if age < 2 else 9):
                    ar = math.radians(a)
                    u, v, _ = CAM.projecta((x + math.cos(ar) * r, y0, z + math.sin(ar) * r))
                    put(u, v, (214, 220, 226), 0.55 - age * 0.12, zz + 30)
        for x, z, s in splashes:                                   # els esquitxos, 2 fotogrames
            age = (i - s) % RAIN_N
            u, v, _ = CAM.projecta((x, 0, z))
            k = CAM.escala((x, 0, z))
            d = max(1, round(1.4 * k))
            if age == 0:
                put(u, v, (196, 202, 208), 0.5, z + 20)
                put(u - d, v - d, (196, 202, 208), 0.45, z + 20)
                put(u + d, v - d, (196, 202, 208), 0.45, z + 20)
            elif age == 1:
                put(u - 2 * d, v - d, (196, 202, 208), 0.3, z + 20)
                put(u + 2 * d, v - d, (196, 202, 208), 0.3, z + 20)
        frames.append(img)
    return frames


ANIMS = {'pluja': {'frames': _frames_pluja, 'frameDuration': 70}}


# ─── Capes del davant (com al pati) ──────────────────────────────────────────

def _amo(ids):
    def mask(x, y):
        _, e = _base()
        return e.ids[e.amo[y * e.cv.w + x]] in ids
    return mask


def _v(z):
    return HOR + CAM.f * CAM.pos[1] / z


FRONT = [
    {'id': 'davant_pou', 'mask': _amo({'pou', 'pou_vora', 'pou_aigua', 'pou_pals'}), 'baseline': round(_v(POU[1])),
     'zIndex': 20},
    {'id': 'davant_bomba', 'mask': _amo({'bomba'}), 'baseline': round(_v(BOMBA[1])), 'zIndex': 20},
    *[{'id': f'davant_tub{k}', 'mask': _amo({f'tub{k}'}), 'baseline': round(_v((A[2] + B[2]) / 2)), 'zIndex': 20}
      for k, (A, B) in enumerate(zip(P.TUB, P.TUB[1:]))],
    {'id': 'davant_arbre', 'mask': _amo({'arbre'}), 'baseline': round(_v(ARBRE[1])), 'zIndex': 20},
    {'id': 'davant', 'mask': _amo({'primer_pla'}), 'baseline': 999, 'zIndex': 20},
]


# ─── Geometria (coordenades de sala, projectades) ─────────────────────────────

def _retalla(poly, x0=0, x1=W - 1):
    """El polígon de terra del pati, retallat a la part de la sala que es veu (x0..x1)."""
    def clip(pts, inside, cut):
        out = []
        for a, b in zip(pts, pts[1:] + pts[:1]):
            if inside(a):
                out.append(a)
            if inside(a) != inside(b):
                out.append(cut(a, b))
        return out

    def cut_x(xc):
        return lambda a, b: (xc, a[1] + (b[1] - a[1]) * (xc - a[0]) / (b[0] - a[0]))
    pts = clip(list(poly), lambda p: p[0] >= x0, cut_x(x0))
    pts = clip(pts, lambda p: p[0] <= x1, cut_x(x1))
    return [(round(x), round(y)) for x, y in pts]


_WALK = _retalla(P._WALK)
_V_FONS, _V_PROP = min(v for _, v in _WALK), max(v for _, v in _WALK)
_Q = P._p(CADIRA[0], CADIRA[2])

GEOMETRIA = {
    'things': {},
    # en Quim, assegut a la cadira de la porta; la Iri i la Vet al mig del pati, davant del pou; en Diu, a la dreta,
    # entre la bomba i les roques
    'spawns': {'quim': (_Q[0], _Q[1] + 1), 'iri': P._p(-250, 600), 'vet': P._p(-330, 585), 'diu': P._p(-150, 640)},
    'walkable': _WALK,
    'floorSquash': 0.25,
    # el cel tapat: l'ombra de contacte, rodona i suau, just a sota (sense una llum que l'allargui)
    'characterShadow': {'enabled': True, 'color': '#141210', 'alpha': 0.38, 'squash': 0.28, 'core': 0.6},
    'forats': [P._cercle(POU[0], POU[1], POU_R + 8), P._cercle(BOMBA[0], BOMBA[1], 20, 8),
               P._cercle(ARBRE[0], ARBRE[1], 10, 6)],
    'regions': [{'id': 'perspectiva', 'active': True, 'scaleEnabled': True, 'scaleWalkSpeed': True,
                 'scaleTop': round((_V_FONS - 2 - HOR) / CAM.pos[1], 3),
                 'scaleBottom': round((_V_PROP + 2 - HOR) / CAM.pos[1], 3),
                 'points': [(0, _V_FONS - 2), (W - 1, _V_FONS - 2), (W - 1, _V_PROP + 2), (0, _V_PROP + 2)]}],
    # La llum de la sala sobre els personatges (characterLights del motor): la pluja: el cel tapat, gris i fred, sense
    # cap llum que destaqui.
    'characterLights': {
        'ambient': '#90969e',
        'lights': [
            {'x': 320, 'y': -400, 'radius': 1000, 'color': '#c8d4e0', 'intensity': 0.12},  # la claror del cel tapat, de dalt
        ],
    },
}
