"""
La Conjura de l'Avet — `arxiu`: la sala capitular a mitjanit (acte 3, Iri). Art definitiu, EN 3D (hd640/tres_d.py), a 1×.

La càmera és alta i mira avall (picat), una mica girada cap a l'esquerra: la paret de l'esquerra fuig cap a la
cantonada i la del fons s'allunya cap a la dreta. Tot és fosc: només hi ha l'espelma de la Vet (en un canelobre de
ferro, damunt el bagul de les butlles) i la llum blava de la lluna, que entra per la finestra petita i alta de la
paret de l'esquerra i fa una clapa al terra, en diagonal.

  - **Paret del fons**, d'esquerra a dreta: la fila de **baguls** ferrats amb etiquetes (censos, `bagul_delmes`,
    `bagul_butlles`, i el `bagul_sunifred`, una mica tret de la fila i girat, amb el lacre vermell), el **tapís** gran
    de la creació del món (com el de Girona: la roda del Creador al mig, els sectors amb Adam, Eva, els peixos i els
    ocells, i la vora dels mesos), l'**estendard** dret en un peu de ferro, i el **banc del fons** de fusta.
  - El **cordill** surt per sota del bagul d'en Sunifred i s'enfila per la paret fins darrere el tapís.
  - **Paret de l'esquerra:** la **finestra** alta i la **porta** de l'scriptorium (tancada; per les escletxes entra la
    llum de les espelmes de l'altra banda). Al peu, el **banc de pedra** corregut.
  - Al mig, a l'esquerra, una pila de baguls vells (`baguls`) girada: s'hi passa per darrere i per davant.
  - **Primer pla:** una columna fosca a la dreta i l'arrencada d'un arc de pedra a dalt, en silueta.

Decorats (cada un és el que canvia respecte del fons; vegeu `PROPS`): `contrapes_terra` (la pedra despenjada, a terra,
amb el cordill fluix), `bagul_obert` (la tapa del bagul d'en
Sunifred aixecada, rotlles de comptes a dins), `doble_fons` (la post del fons aixecada i el forat fosc),
`cofre_dins` (el cofre de plom amb el segell vermell trencat, dins el forat), `tapis_apartat` (el tapís recollit cap a
l'esquerra: el cordill puja per la paret nua fins a una corriola), `estendard_paret` (el pal recolzat a la paret, al
costat del tapís), `gueraula_finestra` (la cara de la Gueraula a la finestra) i `trapa_oberta` (el banc apartat i la
trapa oberta, amb l'escala que baixa a l'aigua del rec). El prop `contrapes` és la pedra penjada a la corriola.

Com que els decorats tenen tots el mateix zIndex, el motor els pinta per ordre alfabètic: `doble_fons` va per sobre
de `cofre_dins` (i per això no en pinta els píxels), i `tapis_apartat` per sobre de `contrapes` i
d'`estendard_paret` (no en pinta la pedra, i el pal recolzat queda fora del tapís).

ANIMS: `espelma` (la flama del canelobre, que belluga, i la seva claror).

El món: x a la dreta, y amunt (0 = terra), z cap al fons (la paret del fons, a z = 480); 1 unitat = 1 px de sala on un
personatge fa la seva mida (escala 1).
"""
import functools
import math

from PIL import Image, ImageDraw

import hd640  # noqa: F401  (abans de cap hd.rooms: posa la llibreria a 640×360)

from hd.pix import Canvas, Light, W, mix
from hd640.tres_d import Camera, Escena, Llum
from hd640.rooms.nit_comu import (BOTTOM, PEDRA, LLOSA, FUSTA, FERRO, FOC, CERA, VERMELL, PERGAMI, TINTA, LLUNA,
                                  TELA, fbm, hr, carreus, lloses, taulons, veta, flama, espelma, ombra, hud_negre,
                                  sense, sense_hud, mascara, llum_personatge, rect_de, _diff)

# ─── La càmera i el món ──────────────────────────────────────────────────────
F = 360
CAM = Camera(pos=(0, 180, 0), yaw=-0.06, pitch=0.18, f=F, centre=(320, 120))

ZB = 480                       # la paret del fons
XL = -300                      # la paret de l'esquerra
XR = 520                       # (la de la dreta no es veu)
ZF = 150                       # el terra arriba fins aquí (per sota de la pantalla)
YT = 460                       # l'alçada de les parets

# Els baguls de la fila (centre x, ample, nom): fons a ZB - 4, 40 d'alt, 38 de fons
BAGULS = [(-262, 58, 'censos'), (-196, 60, 'bagul_delmes'), (-128, 62, 'bagul_butlles')]
BH, BD = 46, 38
# El bagul d'en Sunifred: una mica tret de la fila i girat (cx, cz, ample, fons, alt, angle)
SUNI = (-52, 446, 66, 40, 42, -0.16)
TAPIS = (-30, 150, 46, 214)    # x0, x1, y0, y1 a la paret del fons
CORRIOLA = (136, 226)          # (x, y) a la paret: on penja la pedra (darrere el tapís, a la vora dreta)
ESTENDARD = (196, 440)         # el peu de l'estendard (x, z)
BANC = (282, 452, 92, 30, 34)  # el banc del fons: cx, cz, ample, fons, alt
FINESTRA = (372, 404, 186, 236)    # a la paret de l'esquerra: z0, z1, y0, y1
PORTA = (262, 330, 0, 132)         # a la paret de l'esquerra: z0, z1, y0, y1
PILA = (40, 322, -0.35)           # la pila de baguls vells del mig: cx, cz, angle
CANELOBRE = (-128, 452)            # damunt el bagul de les butlles (x, z)
FLAMA = (-128, BH + 46, 452)       # on és la flama al món

LLUMS = [Llum(FLAMA, 300, 5.0, power=1.8),                         # l'espelma
         Llum((XL + 10, 210, 388), 240, 1.1, power=1.5),            # la lluna, per la finestra
         Llum((XL + 6, 60, 296), 150, 1.2, power=1.6)]              # les escletxes de la porta
AMBIENT = -0.45

LIGHT = Light(ambient=0.0, vignette=None, floor_fade=None)

LLANA = [(16, 12, 10), (34, 26, 20), (56, 44, 32), (82, 66, 46), (110, 90, 62), (140, 116, 80), (170, 144, 102)]


def _p(x, y, z):
    u, v, _ = CAM.projecta((x, y, z))
    return round(u), round(v)


def _z_de_v(v):
    """La z del terra que cau a la y de pantalla `v` (al mig de la pantalla)."""
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


# ─── El tapís de la creació (dibuix pla, en unitats del món: 1 px = 1 unitat) ──────────

TW, THH = TAPIS[1] - TAPIS[0], TAPIS[3] - TAPIS[2]


@functools.lru_cache(maxsize=None)
def _tapis_img():
    """El tapís vist de cara: la vora dels mesos, la gran roda del Creador amb els sectors de la creació (les aigües
    i els peixos, els ocells, Adam i Eva, els animals) i les cantonades amb els vents que bufen. Colors apagats: ocre,
    verd de salvia, blau de pissarra, rajola i crema. Llana: el teixit fa ratlletes verticals."""
    img = Image.new('RGB', (TW, THH), (120, 96, 62))
    d = ImageDraw.Draw(img)
    OCRE, CREMA, VERD, BLAU, RAJ, BRU, FOSC = ((150, 118, 70), (196, 172, 128), (104, 112, 80), (82, 92, 100),
                                               (132, 76, 54), (88, 62, 40), (46, 34, 26))
    # la vora: quadres dels mesos
    d.rectangle([0, 0, TW - 1, THH - 1], fill=BRU)
    n = 9
    for i in range(n):
        x0 = 4 + i * (TW - 8) / n
        d.rectangle([x0 + 1, 3, x0 + (TW - 8) / n - 2, 20], fill=(OCRE, VERD, CREMA)[i % 3])
        d.rectangle([x0 + 1, THH - 21, x0 + (TW - 8) / n - 2, THH - 4], fill=(VERD, CREMA, OCRE)[i % 3])
        cx = x0 + (TW - 8) / n / 2
        d.ellipse([cx - 3, 6, cx + 3, 12], fill=FOSC)                    # un caparró
        d.rectangle([cx - 2, 12, cx + 2, 18], fill=(RAJ, BLAU, BRU)[i % 3])
        d.ellipse([cx - 3, THH - 18, cx + 3, THH - 12], fill=FOSC)
        d.rectangle([cx - 2, THH - 12, cx + 2, THH - 6], fill=(BLAU, RAJ, VERD)[i % 3])
    for j in range(6):
        y0 = 24 + j * (THH - 48) / 6
        for x0 in (3, TW - 21):
            d.rectangle([x0, y0 + 1, x0 + 17, y0 + (THH - 48) / 6 - 2], fill=(CREMA, OCRE, VERD)[(j + x0) % 3])
            d.ellipse([x0 + 5, y0 + 6, x0 + 12, y0 + 13], fill=FOSC)
    # el camp, i les cantonades amb els vents (caps que bufen)
    d.rectangle([22, 22, TW - 23, THH - 23], fill=OCRE)
    for cx, cy in ((34, 34), (TW - 35, 34), (34, THH - 35), (TW - 35, THH - 35)):
        d.ellipse([cx - 10, cy - 10, cx + 10, cy + 10], fill=CREMA, outline=BRU, width=2)
        d.ellipse([cx - 4, cy - 4, cx + 4, cy + 4], fill=FOSC)
    # la gran roda
    cx, cy, R = TW / 2, THH / 2 + 4, min(TW, THH) / 2 - 22
    d.ellipse([cx - R - 4, cy - R - 4, cx + R + 4, cy + R + 4], fill=BRU)
    d.ellipse([cx - R, cy - R, cx + R, cy + R], fill=CREMA)
    sectors = [VERD, BLAU, OCRE, VERD, RAJ, BLAU, OCRE, VERD]
    for k in range(8):
        a0, a1 = k * 45 - 90, (k + 1) * 45 - 90
        d.pieslice([cx - R + 3, cy - R + 3, cx + R - 3, cy + R - 3], a0 + 1, a1 - 1, fill=sectors[k])
    for k in range(8):                                                   # els radis
        a = math.radians(k * 45 - 90)
        d.line([cx, cy, cx + R * math.cos(a), cy + R * math.sin(a)], fill=BRU, width=2)
    # les figures dels sectors (petites i senzilles: es veuen de lluny)
    for k in range(8):
        a = math.radians(k * 45 - 90 + 22.5)
        fx, fy = cx + R * 0.66 * math.cos(a), cy + R * 0.66 * math.sin(a)
        if k in (1, 5):                                                  # peixos
            for j in range(3):
                d.ellipse([fx - 6, fy - 6 + j * 5, fx + 4, fy - 3 + j * 5], fill=CREMA)
                d.polygon([(fx + 4, fy - 4 + j * 5), (fx + 8, fy - 7 + j * 5), (fx + 8, fy - 1 + j * 5)], fill=CREMA)
        elif k in (0, 3):                                                # ocells (un sembla un ànec)
            d.ellipse([fx - 6, fy - 3, fx + 5, fy + 4], fill=CREMA)
            d.ellipse([fx + 2, fy - 7, fx + 7, fy - 2], fill=CREMA)
            d.polygon([(fx + 7, fy - 5), (fx + 11, fy - 4), (fx + 7, fy - 3)], fill=(196, 140, 60))
        elif k in (4, 6):                                                # Adam i Eva
            for dx in (-5, 5):
                d.ellipse([fx + dx - 3, fy - 11, fx + dx + 3, fy - 5], fill=(214, 184, 150))
                d.rectangle([fx + dx - 2, fy - 5, fx + dx + 2, fy + 7], fill=(214, 184, 150))
            d.line([fx, fy - 12, fx, fy + 8], fill=VERD, width=2)       # l'arbre entre els dos
            d.ellipse([fx - 4, fy - 16, fx + 4, fy - 9], fill=VERD)
        else:                                                            # animals de quatre potes
            d.ellipse([fx - 8, fy - 4, fx + 6, fy + 3], fill=CREMA)
            d.ellipse([fx + 4, fy - 8, fx + 10, fy - 2], fill=CREMA)
            for dx in (-6, -2, 2, 5):
                d.line([fx + dx, fy + 2, fx + dx, fy + 7], fill=CREMA, width=1)
    # el Creador, al mig: un cercle amb la figura asseguda i el llibre
    r = R * 0.36
    d.ellipse([cx - r - 3, cy - r - 3, cx + r + 3, cy + r + 3], fill=BRU)
    d.ellipse([cx - r, cy - r, cx + r, cy + r], fill=(176, 150, 104))
    d.ellipse([cx - 5, cy - 15, cx + 5, cy - 5], fill=(214, 184, 150))
    d.ellipse([cx - 9, cy - 19, cx + 9, cy - 1], outline=(196, 160, 70), width=2)   # el nimbe
    d.polygon([(cx - 11, cy + 16), (cx - 7, cy - 4), (cx + 7, cy - 4), (cx + 11, cy + 16)], fill=BLAU)
    d.rectangle([cx - 5, cy + 1, cx + 5, cy + 8], fill=CREMA)           # el llibre obert
    d.line([cx, cy + 1, cx, cy + 8], fill=BRU)
    # el teixit: ratlletes verticals, la llana gastada, les taques de fum; i la vora de baix, desfilada
    px = img.load()
    for y in range(THH):
        for x in range(TW):
            c = px[x, y]
            k = 1.0 + (0.06 if x % 2 else -0.05) + (fbm(x / 9, y / 14, 71) - 0.5) * 0.28 + (hr(x, y, 72) - 0.5) * 0.08
            k -= max(0.0, (fbm(x / 30, y / 26, 73) - 0.6)) * 0.9
            px[x, y] = tuple(max(0, min(255, int(ch * k))) for ch in c)
    out = img.convert('RGBA')
    po = out.load()
    for x in range(TW):
        for y in range(THH - 3 - int(hr(x, 1, 74) * 3), THH):
            po[x, y] = (0, 0, 0, 0)
    return out


@functools.lru_cache(maxsize=None)
def _tapis_recollit():
    """El tapís apartat: recollit cap a l'esquerra, fet un feix de plecs (vist de cara, 56 d'ample)."""
    img = _tapis_img()
    w = 56
    out = Image.new('RGBA', (w, THH), (0, 0, 0, 0))
    src, dst = img.load(), out.load()
    for y in range(THH):
        sag = 6 * (1 - y / THH) ** 2                                     # de dalt, més estret; a baix s'obre
        for x in range(w):
            sx = int(x / w * TW * 0.95 + (y / THH) * 6) % TW
            fold = math.sin(x / w * math.pi * 7 + y / 40)
            k = 0.62 + 0.38 * fold
            if x > w - sag:
                continue
            c = src[sx, y]
            if c[3]:
                dst[x, y] = (int(c[0] * k), int(c[1] * k), int(c[2] * k), 255)
    return out


# ─── La bandera de l'estendard ────────────────────────────────────────────

@functools.lru_cache(maxsize=None)
def _bandera(plegada=False):
    """La bandera del monestir: verd fosc d'avet amb una creu d'or vell i flocs; plegada, un drap que penja."""
    w, h = (34, 64) if not plegada else (18, 58)
    img = Image.new('RGBA', (w, h), (0, 0, 0, 0))
    d = ImageDraw.Draw(img)
    VERD, OR = (34, 58, 38), (176, 140, 66)
    if not plegada:
        d.polygon([(0, 0), (w - 1, 0), (w - 1, h - 14), (w / 2, h - 1), (0, h - 14)], fill=VERD)
        d.rectangle([w / 2 - 3, 8, w / 2 + 2, h - 18], fill=OR)
        d.rectangle([5, 20, w - 6, 25], fill=OR)
    else:
        d.polygon([(0, 0), (w - 1, 0), (w - 3, h - 1), (2, h - 6)], fill=VERD)
        d.rectangle([w / 2 - 2, 10, w / 2 + 1, h - 14], fill=OR)
    px = img.load()
    for y in range(h):
        for x in range(w):
            c = px[x, y]
            if c[3]:
                k = 0.8 + 0.3 * math.sin(x * (1.1 if plegada else 0.35) + y * 0.05) + (hr(x, y, 81) - 0.5) * 0.1
                px[x, y] = (int(c[0] * k), int(c[1] * k), int(c[2] * k), 255)
    return img


# ─── Peces ─────────────────────────────────────────────────────────────────

def parets(e):
    """El terra de lloses, la paret del fons i la de l'esquerra (carreus de gres), més fosques cap amunt."""
    def terra(s, t, P):
        return lloses(P[0], P[2], seed=11, base=3.0)

    e.quad('terra', (XL, 0, ZB), (XR, 0, ZB), (XR, 0, ZF), (XL, 0, ZF), ramp=LLOSA, lvl=terra)

    def fons(s, t, P):
        v = carreus(s, t, alt=28.0, seed=3, base=3.2)
        return v - max(0.0, (P[1] - 200) / 70)                          # cap amunt, la foscor

    e.quad('paret_fons', (XL, YT, ZB), (XR, YT, ZB), (XR, 0, ZB), (XL, 0, ZB), ramp=PEDRA, lvl=fons)

    def esq(s, t, P):
        v = carreus(s, t, alt=28.0, seed=5, base=3.0)
        return v - max(0.0, (P[1] - 200) / 70)

    e.quad('paret_esq', (XL, YT, ZB), (XL, YT, ZF), (XL, 0, ZF), (XL, 0, ZB), ramp=PEDRA, lvl=esq, dues_cares=True)
    # el sòcol: una filada de pedra més grossa que sobresurt (el banc corregut de la paret de l'esquerra)
    e.caixa('bancs', XL, XL + 30, 0, 30, PORTA[1] + 14, ZB, PEDRA, 3.0,
            cares={'dalt': {'ramp': PEDRA, 'lvl': lambda s, t, P: 3.6 + (fbm(s / 20, t / 4, 9) - 0.5) * 0.8},
                   'dreta': {'ramp': PEDRA, 'lvl': lambda s, t, P: carreus(s, t, alt=30.0, seed=7, base=2.6)}})
    # i a la paret del fons, a la dreta del banc de fusta, un altre tros de banc de pedra
    e.caixa('bancs', BANC[0] + BANC[2] / 2 + 8, XR, 0, 30, ZB - 30, ZB, PEDRA, 3.0,
            cares={'dalt': {'ramp': PEDRA, 'lvl': lambda s, t, P: 3.6 + (fbm(s / 20, t / 4, 9) - 0.5) * 0.8},
                   'davant': {'ramp': PEDRA, 'lvl': lambda s, t, P: carreus(s, t, alt=30.0, seed=8, base=2.6)}})


def finestra(e, cv, gueraula=False):
    """La finestra petita i alta de la paret de l'esquerra: un forat amb arc, el cel de nit i la lluna que hi entra;
    amb `gueraula`, la cara de la Gueraula hi treu el cap."""
    z0, z1, y0, y1 = FINESTRA
    # l'esqueixada (el gruix del mur): un forat fosc més gran
    pts = []
    for k in range(13):
        a = math.pi * k / 12
        zc, r = (z0 + z1) / 2, (z1 - z0) / 2
        pts.append(_p(XL, y1 - r + math.sin(a) * r, zc + math.cos(a) * r))
    pts = [_p(XL, y0, z1)] + pts + [_p(XL, y0, z0)]
    cv.poly(pts, LLUNA, lambda x, y: 4.2 + (fbm(x / 3, y / 3, 41) - 0.5) * 0.8, lit=0)
    # els estels i el marc fosc
    for k in range(3):
        sx, sy = _p(XL, y0 + 12 + k * 13, z0 + 8 + k * 9)
        cv.flat(sx, sy, (220, 228, 240))
    cv.line(pts[0][0], pts[0][1], pts[-1][0], pts[-1][1], PEDRA, 5.4, lit=0)   # l'ampit, que la lluna toca
    for a, b in zip(pts, pts[1:]):
        cv.line(a[0], a[1], b[0], b[1], PEDRA, 1.2, lit=0)
    if gueraula:
        _gueraula(cv)


def _gueraula(cv):
    """La Gueraula a la finestra: la toca blanca, la cara rodona, la mà que fa senyals cap avall."""
    z0, z1, y0, y1 = FINESTRA
    u, v = _p(XL, y0 + 2, (z0 + z1) / 2)
    k = CAM.escala((XL, y0, (z0 + z1) / 2))
    TOCA = [(60, 62, 70), (110, 112, 120), (160, 160, 166), (204, 204, 206), (232, 230, 226)]
    CARA = [(70, 42, 34), (120, 78, 60), (170, 120, 92), (204, 156, 122), (226, 186, 152)]
    r = 9 * k
    cv.disc(u, v - r * 1.1, r * 1.15, r * 1.25, TOCA, lambda nx, ny: 2.6 + nx * 0.6 - ny * 0.4, lit=0)
    cv.disc(u + 0.5, v - r * 0.95, r * 0.72, r * 0.82, CARA, lambda nx, ny: 3.2 + nx * 0.5 - ny * 0.3, lit=0)
    for dx in (-0.3, 0.3):                                               # els ulls oberts de bat a bat
        cv.flat(u + 0.5 + dx * r, v - r * 1.05, (30, 20, 20))
    cv.flat(u + 0.5, v - r * 0.62, (90, 40, 34))                         # la boca, cridant
    cv.flat(u + 1.5, v - r * 0.62, (90, 40, 34))
    # el braç que assenyala avall
    for i in range(int(r * 1.6)):
        cv.put(u + r * 0.9 + i * 0.25, v - r * 0.5 + i, TELA, 2.6, lit=0)
        cv.put(u + r * 0.9 + i * 0.25 + 1, v - r * 0.5 + i, TELA, 1.6, lit=0)
    cv.disc(u + r * 0.9 + r * 0.42, v + r * 1.15, 1.8, 1.8, CARA, 3.0, lit=0)


def clapa_lluna(e):
    """La llum de la lluna: entra per la finestra i cau al terra en diagonal, cap a la dreta i cap a nosaltres."""
    z0, z1, _, _ = FINESTRA

    def k(s, t):
        # la forma de la finestra, estirada pel terra: s al llarg de x, t cap a nosaltres
        d = abs(t - (96 + s * 0.3)) / 22
        return max(0.0, 1 - d) ** 0.6 * 0.5 * min(1.0, max(0.0, s - 70) / 40) * max(0.0, 1 - max(0.0, s - 200) / 70)

    e.claror((XL + 30, 0.2, ZB - 6), (XL + 330, 0.2, ZB - 6), (XL + 330, 0.2, ZB - 206), (XL + 30, 0.2, ZB - 206),
             (120, 146, 190), k)


def _dins(pts, x, y):
    """Si (x, y) és dins el polígon `pts` (regla parell-senar)."""
    c = False
    for (xa, ya), (xb, yb) in zip(pts, pts[1:] + pts[:1]):
        if (ya > y) != (yb > y) and x < xa + (y - ya) * (xb - xa) / (yb - ya):
            c = not c
    return c


def raig_lluna(cv):
    """El feix de la lluna a l'aire, de la finestra a la clapa del terra: molt suau, més fort a prop de la finestra."""
    z0, z1, y0, y1 = FINESTRA
    zc = ZB - 6
    a, b = _p(XL, y1 - 10, z1), _p(XL, y0, z0)
    c = _p(XL + 30 + 230, 0, zc - (96 + 230 * 0.3) + 18)
    d = _p(XL + 30 + 100, 0, zc - (96 + 100 * 0.3) - 18)
    pts = [a, b, d, c]
    x0, x1 = min(p[0] for p in pts), max(p[0] for p in pts)
    y0_, y1_ = min(p[1] for p in pts), max(p[1] for p in pts)

    def k(x, y):
        if not _dins(pts, x, y):
            return 0
        t = (y - y0_) / max(1, y1_ - y0_)
        return 0.13 * (1 - t * 0.6) * (0.85 + 0.3 * fbm(x / 14, y / 30, 47))
    cv.tint(x0, y0_, x1, y1_, (150, 176, 220), k)


def porta(e, cv):
    """La porta de l'scriptorium, a la paret de l'esquerra: taulons, ferramenta, i la llum de les espelmes que
    entra per les escletxes."""
    z0, z1, y0, y1 = PORTA
    # el bastiment de pedra (un arc de mig punt) i el forat
    zc, r = (z0 + z1) / 2, (z1 - z0) / 2 + 8
    pts = [_p(XL + 0.5, y1 - r + 8 + math.sin(math.pi * k / 14) * r, zc + math.cos(math.pi * k / 14) * r)
           for k in range(15)]
    pts = [_p(XL + 0.5, 0, zc + r)] + pts + [_p(XL + 0.5, 0, zc - r)]
    cv.poly(pts, PEDRA, 1.8, lit=0)

    def fusta(s, t, P):
        return taulons(s, t, ample=13.0, seed=27, base=2.6) + (0.9 if 52 < t < 58 or 100 < t < 106 else 0)

    zz0, zz1 = z0 + 4, z1 - 4
    e.quad('porta_capitular', (XL + 1, y1 - 6, zz1), (XL + 1, y1 - 6, zz0), (XL + 1, 0, zz0), (XL + 1, 0, zz1),
           ramp=FUSTA, lvl=fusta, dues_cares=True)
    # la ferramenta (frontisses) i l'anella
    for y in (24, 98):
        a, b = _p(XL + 1.5, y, zz1 - 2), _p(XL + 1.5, y, zz0 + 40)
        cv.line(a[0], a[1], b[0], b[1], FERRO, 3.2, lit=0)
        cv.line(a[0], a[1] + 1, b[0], b[1] + 1, FERRO, 1.6, lit=0)
    u, v = _p(XL + 2, 62, zz0 + 12)
    cv.ring(u, v, 2.5, FERRO, 4.0, lit=0, step=20)
    # les escletxes: la llum càlida de l'scriptorium per sota i pel costat de la porta
    for i in range(30):
        t = i / 29
        a = _p(XL + 1.5, 1, zz0 + (zz1 - zz0) * t)
        cv.flat(a[0], a[1], mix((255, 200, 120), (180, 110, 50), abs(t - 0.5)))
    for j in range(0, int(y1 - 10), 2):
        a = _p(XL + 1.5, j, zz0)
        cv.flat(a[0], a[1], (230, 160, 80) if hr(j, 3, 5) > 0.3 else (140, 80, 40))
    # la claror que fa a terra, davant la porta
    e.claror((XL, 0.3, zz1 + 10), (XL + 80, 0.3, zz1 + 10), (XL + 80, 0.3, zz0 - 10), (XL, 0.3, zz0 - 10),
             (230, 150, 80), lambda s, t: max(0.0, 1 - s / 70) ** 2 * 0.35 * max(0.0, 1 - abs(t - 40) / 46))


def _ferros(e, x0, x1, y0, y1, z0, z1, eix='x', n=(0.12, 0.88)):
    """Les bandes de ferro d'un bagul: caixes primes que l'emboliquen."""
    for f in n:
        if eix == 'x':
            c = x0 + (x1 - x0) * f
            e.caixa('ferro', c - 2.5, c + 2.5, y0, y1 + 0.8, z0 - 0.8, z1, FERRO, 3.4)


def bagul(e, cx, w, nom, cz=ZB - 4 - BD / 2, h=BH, etiqueta=True, sid=None):
    """Un bagul ferrat, de cara a la sala: taulons, bandes de ferro, el pany, i l'etiqueta de pergamí."""
    sid = sid or nom
    x0, x1, z0, z1 = cx - w / 2, cx + w / 2, cz - BD / 2, cz + BD / 2
    e.caixa(sid, x0, x1, 0, h, z0, z1, FUSTA, 3.0,
            cares={'davant': {'ramp': FUSTA, 'lvl': lambda s, t, P: veta(s, t, seed=int(cx) % 50, base=3.4)},
                   'dalt': {'ramp': FUSTA, 'lvl': lambda s, t, P: veta(s, t, seed=int(cx) % 50 + 3, base=5.0)
                            - (1.2 if int(t) % 12 == 0 else 0)},
                   'dreta': {'ramp': FUSTA, 'lvl': lambda s, t, P: veta(s, t, seed=4, base=2.6)},
                   'esquerra': {'ramp': FUSTA, 'lvl': lambda s, t, P: veta(s, t, seed=4, base=2.6)}})
    # les bandes de ferro: al davant i per damunt (tires primes, no caixes: no se'n veu el cantell)
    for f in (0.1, 0.9):
        c = x0 + w * f
        e.quad(sid, (c - 2, h, z0 - 0.6), (c + 2, h, z0 - 0.6), (c + 2, 0, z0 - 0.6), (c - 2, 0, z0 - 0.6),
               ramp=FERRO, lvl=3.0)
        e.quad(sid, (c - 2, h + 0.4, z1), (c + 2, h + 0.4, z1), (c + 2, h + 0.4, z0 - 0.6), (c - 2, h + 0.4, z0 - 0.6),
               ramp=FERRO, lvl=3.6)
    e.quad(sid, (x0, h, z0 - 0.7), (x1, h, z0 - 0.7), (x1, h - 4, z0 - 0.7), (x0, h - 4, z0 - 0.7), ramp=FERRO, lvl=2.8)
    # el pany
    e.quad(sid, (cx - 4, h - 4, z0 - 1), (cx + 4, h - 4, z0 - 1), (cx + 4, h - 16, z0 - 1), (cx - 4, h - 16, z0 - 1),
           ramp=FERRO, lvl=4.2)
    if etiqueta:
        e.quad(sid, (x0 + 10, h - 12, z0 - 1.2), (x0 + 22, h - 12, z0 - 1.2), (x0 + 22, h - 22, z0 - 1.2),
               (x0 + 10, h - 22, z0 - 1.2), ramp=PERGAMI,
               lvl=lambda s, t, P: 4.4 - (2.4 if (int(t) in (3, 6) and hr(int(s), int(t), 9) > 0.3) else 0))


def baguls_fila(e):
    for cx, w, nom in BAGULS:
        bagul(e, cx, w, nom, sid='baguls' if nom == 'censos' else nom)
    # la cinta del bagul de les butlles (vermell apagat, no el de la cera)
    cx, w, _ = BAGULS[2]
    z0 = ZB - 4 - BD
    e.quad('bagul_butlles', (cx + 8, BH + 0.9, z0 + 10), (cx + 12, BH + 0.9, z0 + 10), (cx + 12, BH + 0.9, z0 - 1),
           (cx + 8, BH + 0.9, z0 - 1), ramp=[(40, 14, 14), (70, 26, 22), (96, 40, 30), (120, 54, 40)], lvl=2.4)
    e.quad('bagul_butlles', (cx + 8, BH, z0 - 1.3), (cx + 12, BH, z0 - 1.3), (cx + 13, BH - 18, z0 - 1.3),
           (cx + 9, BH - 18, z0 - 1.3), ramp=[(40, 14, 14), (70, 26, 22), (96, 40, 30), (120, 54, 40)], lvl=2.2)


def _suni_pt(lx, y, lz):
    cx, cz, w, d, h, a = SUNI
    return _gir(cx, cz, a)(lx, y, lz)


def bagul_sunifred(e, cv, estat):
    """El bagul d'en Sunifred, tret de la fila i girat: el lacre vermell al pany; obert, la tapa recolzada enrere i
    els rotlles de comptes; amb el doble fons, la post aixecada i el forat; i el cofre de plom."""
    cx, cz, w, d, h, a = SUNI
    obert = 'obert' in estat
    fusta = {'ramp': FUSTA, 'lvl': lambda s, t, P: veta(s, t, seed=17, base=3.4)}
    if not obert:
        e.caixa_girada('bagul_sunifred', cx, cz, w, d, h, a, FUSTA, 3.0,
                       cares={'davant': fusta, 'esquerra': fusta, 'dreta': fusta,
                              'dalt': {'ramp': FUSTA, 'lvl': lambda s, t, P: veta(s, t, seed=18, base=4.2)}})
    else:
        # la caixa sense tapa: les quatre parets (amb el gruix de dalt) i l'interior fosc
        P = _suni_pt
        hw, hd = w / 2, d / 2
        g = 3.0
        fons_y = 22
        # la tapa, oberta i recolzada enrere (contra la paret): es pinta primer, és la que queda més al fons
        e.quad('bagul_sunifred', P(-hw, h + d - 2, hd + 18), P(hw, h + d - 2, hd + 18), P(hw, h, hd),
               P(-hw, h, hd), ramp=FUSTA, lvl=lambda s, t, P_: veta(s, t, seed=22, base=2.4), dues_cares=True)
        # l'interior: el fons (fosc), i les cares de dins de les parets del darrere i dels costats
        e.quad('bagul_sunifred', P(-hw + g, fons_y, hd - g), P(hw - g, fons_y, hd - g), P(hw - g, fons_y, -hd + g),
               P(-hw + g, fons_y, -hd + g), ramp=FUSTA, lvl=lambda s, t, P_: 1.2 + (fbm(s / 6, t / 3, 5) - 0.5))
        e.quad('bagul_sunifred', P(-hw + g, h, hd - g), P(hw - g, h, hd - g), P(hw - g, fons_y, hd - g),
               P(-hw + g, fons_y, hd - g), ramp=FUSTA, lvl=lambda s, t, P_: veta(s, t, seed=19, base=1.8), dues_cares=True)
        e.quad('bagul_sunifred', P(-hw + g, h, -hd + g), P(-hw + g, h, hd - g), P(-hw + g, fons_y, hd - g),
               P(-hw + g, fons_y, -hd + g), ramp=FUSTA, lvl=lambda s, t, P_: veta(s, t, seed=20, base=2.2), dues_cares=True)
        e.quad('bagul_sunifred', P(hw - g, h, hd - g), P(hw - g, h, -hd + g), P(hw - g, fons_y, -hd + g),
               P(hw - g, fons_y, hd - g), ramp=FUSTA, lvl=lambda s, t, P_: veta(s, t, seed=21, base=1.4), dues_cares=True)
        if 'doble' in estat:
            # la post del doble fons, aixecada i dreta contra la paret del darrere (la cara de sota, més clara: fusta
            # que no ha vist mai la llum), i el forat fosc a sota
            e.quad('bagul_sunifred', P(-4, 60, hd - 4), P(hw - g - 1, 60, hd - 4), P(hw - g - 1, 22, hd - g - 3),
                   P(-4, 22, hd - g - 3), ramp=FUSTA, lvl=lambda s, t, P_: veta(s, t, seed=23, base=5.4), dues_cares=True)
            e.quad('bagul_sunifred', P(-6, 22.5, hd - g - 4), P(hw - g, 22.5, hd - g - 4), P(hw - g, 22.5, -hd + g),
                   P(-6, 22.5, -hd + g), ramp=TINTA, lvl=0.4)
            if 'cofre' in estat:
                cofre(e, cv)
        # els rotlles de comptes, ajaguts a la meitat de l'esquerra (no es mouen: el doble fons és a la dreta)
        for i in range(3):
            lx = -hw + 9 + i * 9
            for j in range(3):
                yy = 36 + j * 2.5
                lz = -8 + j * 7
                a0, a1 = _p(*P(lx - 3, yy, lz)), _p(*P(lx + 3, yy, lz))
                cv.line(a0[0], a0[1] - 1, a1[0], a1[1] - 1, PERGAMI, 3.6, lit=0)
                cv.line(a0[0], a0[1], a1[0], a1[1], PERGAMI, 2.6, lit=0)
                cv.flat(a0[0], a0[1] - 1, PERGAMI[5])
        # les vores de dalt (el gruix de la fusta) i la cara de fora
        e.quad('bagul_sunifred', P(-hw, h, -hd), P(hw, h, -hd), P(hw, 0, -hd), P(-hw, 0, -hd), **fusta)
        e.quad('bagul_sunifred', P(-hw, h, hd), P(-hw, h, -hd), P(-hw, 0, -hd), P(-hw, 0, hd), **fusta)
        e.quad('bagul_sunifred', P(hw, h, -hd), P(hw, h, hd), P(hw, 0, hd), P(hw, 0, -hd), **fusta)
        for (ax, az), (bx, bz) in (((-hw, -hd), (hw, -hd)), ((-hw, -hd), (-hw, hd)), ((hw, -hd), (hw, hd)),
                                   ((-hw, hd), (hw, hd))):
            e.linia(P(ax, h + 0.5, az), P(bx, h + 0.5, bz), FUSTA, 5.0)
    # les bandes de ferro
    for f in (-0.4, 0.4):
        lx = w * f
        for (ax, ay, az), (bx, by, bz) in ((((lx, 0, -d / 2 - 0.6), (lx, h + 0.6, -d / 2 - 0.6))),
                                           (((lx, h + 0.6, -d / 2 - 0.6), (lx, h + 0.6, d / 2))) if not obert else
                                           (((lx, h + 0.6, -d / 2 - 0.6), (lx, h + 0.6, -d / 2 + 3)))):
            e.cable('bagul_sunifred', [_suni_pt(ax, ay, az), _suni_pt(bx, by, bz)], FERRO, 3.6, gruix=4.0)
    # el pany i el lacre vermell (l'únic vermell de la sala: que l'ull el trobi)
    u, v = _p(*_suni_pt(0, h - 9, -d / 2 - 1))
    cv.rect(u - 3, v - 5, u + 3, v + 4, FERRO, 4.0, lit=0)
    cv.disc(u, v + 1, 3.6, 3.2, VERMELL, lambda nx, ny: 4.4 - ny * 1.6 - nx * 0.8, lit=0)
    cv.flat(u - 1, v, (255, 150, 110))
    cv.flat(u, v + 1, (120, 16, 16))                                    # el dibuix: la creu
    cv.flat(u, v + 2, (120, 16, 16))
    cv.flat(u - 1, v + 1, (120, 16, 16))
    cv.flat(u + 1, v + 1, (120, 16, 16))
    for i in range(5):                                                   # el cordó que lliga el lacre
        cv.flat(u - 3 - i * 0.6, v + 3 + i, VERMELL[2])
    # l'etiqueta
    if not obert:
        pass
    e.quad('bagul_sunifred', _suni_pt(-w / 2 + 8, h - 12, -d / 2 - 1.2), _suni_pt(-w / 2 + 20, h - 12, -d / 2 - 1.2),
           _suni_pt(-w / 2 + 20, h - 22, -d / 2 - 1.2), _suni_pt(-w / 2 + 8, h - 22, -d / 2 - 1.2), ramp=PERGAMI,
           lvl=lambda s, t, P: 4.4 - (2.4 if (int(t) in (3, 6) and hr(int(s), int(t), 10) > 0.3) else 0))


def cofre(e, cv):
    """El cofre de plom de l'Emma, dins el forat del doble fons, amb el segell vermell trencat a la tapa."""
    cx, cz, w, d, h, a = SUNI
    PLOM = [(14, 16, 20), (28, 30, 36), (46, 50, 56), (68, 72, 78), (94, 98, 104), (126, 130, 134), (160, 164, 166)]
    e.caixa_girada('cofre', cx + 14, cz - 4, 28, 18, 24, a, PLOM, 3.2, y0=26,
                   cares={'dalt': {'ramp': PLOM, 'lvl': lambda s, t, P: 4.4 + (fbm(s / 5, t / 5, 3) - 0.5) * 0.9},
                          'davant': {'ramp': PLOM, 'lvl': 3.0}})
    u, v = _p(*_gir(cx + 14, cz - 4, a)(0, 50.5, -3))
    cv.disc(u, v, 4.2, 2.4, VERMELL, lambda nx, ny: 4.6 - ny * 1.4 - nx * 0.6, lit=0)
    cv.line(u - 1, v - 2, u + 1, v + 2, VERMELL, 1.0, lit=0)             # la ratlla del segell trencat
    cv.flat(u - 2, v - 1, (255, 150, 110))


def cordill(e, cv, estat):
    """El cordill: surt per sota del bagul d'en Sunifred, s'arrapa a la paret i puja cap a la corriola (darrere el
    tapís; amb el tapís apartat, sencer). Amb `pedra`, la pedra penjada a la corriola."""
    cx, cz, w, d, h, a = SUNI
    x0, y0, z0 = _suni_pt(w / 2 - 6, 3, d / 2)
    pts = [(x0, y0, z0), (x0 + 6, 2, ZB - 1), (TAPIS[0] - 2, 40, ZB - 1)]
    if 'tapis' in estat:
        pts += [(CORRIOLA[0] - 30, CORRIOLA[1] - 50, ZB - 1), (CORRIOLA[0] - 2, CORRIOLA[1] - 4, ZB - 1)]
    else:
        pts += [(TAPIS[0] + 4, 60, ZB - 1)]
    COR = [(30, 24, 16), (70, 58, 40), (120, 100, 70), (170, 150, 110)]
    for A, B in zip(pts, pts[1:]):
        e.linia(A, B, COR, 2.6)
    if 'tapis' in estat:
        # la corriola: una roda de ferro clavada a la paret
        u, v = _p(CORRIOLA[0], CORRIOLA[1], ZB - 1)
        cv.disc(u, v, 4, 4, FERRO, lambda nx, ny: 4.2 - ny * 1.2, lit=0)
        cv.flat(u, v, FERRO[1])
        a_, b_ = _p(CORRIOLA[0], CORRIOLA[1] + 14, ZB - 0.5), _p(CORRIOLA[0], CORRIOLA[1], ZB - 0.5)
        cv.line(a_[0], a_[1], b_[0], b_[1], FERRO, 3.0, lit=0)
    if 'pedra' in estat:
        pedra(e, cv)
    if 'terra' in estat:
        pedra_terra(e, cv)


def pedra_terra(e, cv):
    """El contrapès despenjat: la pedra a terra, al peu de la paret just a sota d'on penjava, i el cordill fluix fet
    una garlanda pel terra (tot per sota del tapís: el decorat del tapís apartat, que es pinta per sobre, no el tapa)."""
    COR = [(30, 24, 16), (70, 58, 40), (120, 100, 70), (170, 150, 110)]
    x, z = CORRIOLA[0] + 4, ZB - 16
    u, v = _p(x, 8, z)
    k = CAM.escala((x, 0, z))
    ombra(cv, u + 5, v + 7 * k, 13 * k, 4 * k, k=0.7)
    cv.disc(u, v, 11 * k, 9 * k, PEDRA, lambda nx, ny: 6.0 - nx * 1.6 - ny * 1.8 + (fbm(nx * 3, ny * 3, 5) - 0.5),
            lit=0)
    cv.line(u - 9 * k, v - 2 * k, u + 9 * k, v - 4 * k, COR, 1.4, lit=0)
    # el cordill fluix: de la pedra, pel terra, cap al bagul (fa ziga-zagues) i un tros que puja una mica per la paret
    pts = [(x - 6, 1, z - 2), (x - 30, 0.5, z - 18), (x - 52, 0.5, z - 4), (x - 80, 0.5, z - 20), (x - 104, 0.5, z - 8),
           (TAPIS[0] - 2, 0.5, ZB - 6)]
    for A, B in zip(pts, pts[1:]):
        e.linia(A, B, COR, 2.6)
    e.linia((x + 2, 4, ZB - 1), (x + 2, 30, ZB - 1), COR, 2.4)
    e.linia((x + 2, 4, ZB - 1), (x - 4, 2, z), COR, 2.4)


def pedra(e, cv):
    """El contrapès: una pedra lligada amb el cordill, penjada sota la corriola."""
    COR = [(30, 24, 16), (70, 58, 40), (120, 100, 70), (170, 150, 110)]
    x, y = CORRIOLA[0] + 3, CORRIOLA[1]
    e.linia((x, y, ZB - 2), (x, y - 34, ZB - 2), COR, 2.8)
    u, v = _p(x, y - 46, ZB - 6)
    k = CAM.escala((x, y - 46, ZB - 6))
    cv.disc(u, v, 10 * k, 12 * k, PEDRA, lambda nx, ny: 6.2 - nx * 1.6 - ny * 1.8 + (fbm(nx * 3, ny * 3, 5) - 0.5),
            lit=0)
    cv.line(u - 8 * k, v - 3 * k, u + 8 * k, v - 5 * k, COR, 1.4, lit=0)   # el cordill que la lliga
    ombra(cv, u + 6, v + 3, 7 * k, 10 * k, k=0.5)


def tapis(e, cv, estat):
    """El tapís penjat d'una barra; apartat, recollit cap a l'esquerra (es veu la paret nua i el cordill)."""
    x0, x1, y0, y1 = TAPIS
    # la barra de ferro i els ganxos
    e.cable('tapis', [(x0 - 8, y1 + 3, ZB - 3), (x1 + 8, y1 + 3, ZB - 3)], FERRO, 3.2, gruix=3.0)
    for x in (x0 - 6, x1 + 6):
        e.cable('tapis', [(x, y1 + 3, ZB - 3), (x, y1 + 3, ZB)], FERRO, 2.6, gruix=4.0)
    if 'tapis' not in estat:
        # una mica separat de la paret, amb els plecs que fa en penjar
        e.quad('tapis', (x0, y1, ZB - 4), (x1, y1, ZB - 4), (x1, y0, ZB - 4), (x0, y0, ZB - 4),
               tex=(_tapis_img(), (0, 0, TW, THH), 1),
               ombra=lambda s, t: 0.18 * (0.5 + 0.5 * math.sin(s / TW * math.pi * 9)) * min(1.0, t / 60))
        # l'ombra del tapís a la paret, cap a la dreta (la llum de l'espelma ve de l'esquerra)
        e.foscor('ombra', (x1, y1 - 6, ZB - 0.5), (x1 + 10, y1 - 6, ZB - 0.5), (x1 + 10, y0, ZB - 0.5),
                 (x1, y0, ZB - 0.5), lambda s, t: 0.55 * (1 - s / 10))
    else:
        w = 56
        e.quad('tapis', (x0 - 4, y1, ZB - 6), (x0 - 4 + w, y1, ZB - 6), (x0 - 4 + w, y0, ZB - 6),
               (x0 - 4, y0, ZB - 6), tex=(_tapis_recollit(), (0, 0, w, THH), 1))
        e.foscor('ombra', (x0 + w - 4, y1 - 6, ZB - 0.5), (x0 + w + 8, y1 - 6, ZB - 0.5), (x0 + w + 8, y0, ZB - 0.5),
                 (x0 + w - 4, y0, ZB - 0.5), lambda s, t: 0.5 * (1 - s / 12))
        # la paret on era el tapís, més neta (no hi ha fum): una mica més clara
        e.claror((x0 + w, y1, ZB - 0.3), (x1, y1, ZB - 0.3), (x1, y0, ZB - 0.3), (x0 + w, y0, ZB - 0.3),
                 (150, 116, 84), lambda s, t: 0.12)


def estendard(e, cv, paret=False):
    """L'estendard: un pal de freixe llarg amb la bandera; dret en un peu de ferro, o bé recolzat a la paret, al
    costat del tapís (sota la corriola). El peu sempre hi és."""
    x, z = ESTENDARD
    # el peu: tres potes de ferro
    for ang in (0.3, 2.4, 4.4):
        e.cable('estendard', [(x, 18, z), (x + math.cos(ang) * 14, 0, z + math.sin(ang) * 10)], FERRO, 3.0, gruix=3.0)
    e.cable('estendard', [(x, 0, z), (x, 20, z)], FERRO, 3.6, gruix=4.0)
    FREIXE = [(26, 18, 12), (52, 38, 24), (86, 64, 40), (120, 94, 60), (156, 126, 84), (190, 160, 110)]
    if not paret:
        e.cable('estendard', [(x, 0, z), (x, 200, z)], FREIXE, 3.4, gruix=4.0)
        e.cable('estendard', [(x - 26, 196, z), (x + 26, 196, z)], FREIXE, 3.0, gruix=3.0)
        u0, v0 = _p(x - 24, 194, z)
        u1, v1 = _p(x + 24, 194, z)
        k = (u1 - u0) / 34
        ban = _bandera()
        from pixels import nearest
        b = nearest(ban, (max(1, round(ban.width * k)), max(1, round(ban.height * k))))
        cv.img.alpha_composite(b, (round(u0), round(v0)))
        cv.P = cv.img.load()
        u, v = _p(x, 204, z)
        cv.disc(u, v, 2.4, 2.4, [(60, 46, 20), (120, 96, 40), (180, 146, 70), (220, 190, 110)], 2.4, lit=0)
    else:
        top = (CORRIOLA[0] + 20, CORRIOLA[1] - 46, ZB - 2)
        foot = (x + 30, 0, ZB - 40)
        e.cable('estendard', [foot, top], FREIXE, 3.4, gruix=4.0)
        # la bandera, plegada al llarg del pal
        u0, v0 = _p(*[foot[i] + (top[i] - foot[i]) * 0.97 for i in range(3)])
        k = CAM.escala(top)
        ban = _bandera(True)
        from pixels import nearest
        b = nearest(ban, (max(1, round(ban.width * k)), max(1, round(ban.height * k))))
        cv.img.alpha_composite(b, (round(u0 - b.width / 2), round(v0)))
        cv.P = cv.img.load()


def banc_fons(e, cv, apartat=False):
    """El banc del fons, de fusta; apartat, girat cap a la dreta, i la trapa oberta amb l'escala que baixa a l'aigua."""
    cx, cz, w, d, h = BANC
    if apartat:
        trapa(e, cv)
        cx, cz, ang = cx - 14, cz - 66, 0.32
    else:
        ang = 0.0
    fusta = {'ramp': FUSTA, 'lvl': lambda s, t, P: veta(s, t, seed=41, base=3.6)}
    # el seient i les dues potes de taulell
    e.caixa_girada('banc_fons', cx, cz, w, d, 6, ang, FUSTA, 3.4, y0=h - 6,
                   cares={'dalt': {'ramp': FUSTA, 'lvl': lambda s, t, P: veta(s, t, seed=42, base=4.4)},
                          'davant': fusta, 'esquerra': fusta, 'dreta': fusta})
    G = _gir(cx, cz, ang)
    for lx in (-w / 2 + 8, w / 2 - 12):
        P = lambda a, y, b: G(lx + a, y, b)  # noqa: E731
        e.quad('banc_fons', P(0, h - 6, -d / 2 + 3), P(4, h - 6, -d / 2 + 3), P(4, 0, -d / 2 + 3), P(0, 0, -d / 2 + 3),
               ramp=FUSTA, lvl=2.6, dues_cares=True)
        e.quad('banc_fons', P(4, h - 6, -d / 2 + 3), P(4, h - 6, d / 2 - 3), P(4, 0, d / 2 - 3), P(4, 0, -d / 2 + 3),
               ramp=FUSTA, lvl=1.8, dues_cares=True)


TRAPA = (282, 446, 58, 40)     # cx, cz, ample, fons


def trapa(e, cv):
    """La trapa del rec, oberta: el forat a terra, l'escala de pedra que baixa, l'aigua fosca amb un reflex blau, i la
    tapa de taulons aixecada contra la paret."""
    cx, cz, w, d = TRAPA
    x0, x1, z0, z1 = cx - w / 2, cx + w / 2, cz - d / 2, cz + d / 2
    # el forat: les parets de dins (fosques) i el fons d'aigua
    e.quad('trapa', (x0, 0, z1), (x1, 0, z1), (x1, -60, z1), (x0, -60, z1), ramp=PEDRA,
           lvl=lambda s, t, P: carreus(s, t, alt=14, seed=61, base=1.6) - t / 30)
    e.quad('trapa', (x0, 0, z0), (x0, 0, z1), (x0, -60, z1), (x0, -60, z0), ramp=PEDRA,
           lvl=lambda s, t, P: carreus(s, t, alt=14, seed=62, base=1.2) - t / 30, dues_cares=True)
    e.quad('trapa', (x1, 0, z1), (x1, 0, z0), (x1, -60, z0), (x1, -60, z1), ramp=PEDRA,
           lvl=lambda s, t, P: carreus(s, t, alt=14, seed=63, base=1.0) - t / 30, dues_cares=True)
    e.quad('trapa', (x0, -34, z1), (x1, -34, z1), (x1, -34, z0), (x0, -34, z0), ramp=LLUNA,
           lvl=lambda s, t, P: 2.8 + (1.6 if math.sin(s / 3 + t / 1.5) > 0.7 else 0))
    # els graons que baixen (de la vora del davant cap al fons)
    for i in range(4):
        y = -6 - i * 8
        zz = z0 + 4 + i * 6
        e.caixa('trapa', x0 + 6, x1 - 6, y - 3, y, zz - 3, zz + 3, PEDRA, 3.2 - i * 0.5)
    # la tapa, aixecada: taulons de cara, recolzada enrere
    e.quad('trapa', (x0, 44, z1 + 18), (x1, 44, z1 + 18), (x1, 0, z1), (x0, 0, z1), ramp=FUSTA,
           lvl=lambda s, t, P: taulons(t, s, ample=10.0, seed=64, base=3.0), dues_cares=True)
    a, b = _p(cx - 6, 20, z1 + 9), _p(cx + 6, 20, z1 + 9)
    cv.line(a[0], a[1], b[0], b[1], FERRO, 3.0, lit=0)
    u, v = _p(cx, 0, z0)
    # la vora del forat
    e.linia((x0, 0.5, z0), (x1, 0.5, z0), PEDRA, 4.6)


def canelobre(e, cv, fase=0.0, flama_on=True):
    """El canelobre de ferro damunt el bagul de les butlles, amb l'espelma de la Vet i la seva flama."""
    x, z = CANELOBRE
    e.cable('canelobre', [(x, BH, z), (x, BH + 30, z)], FERRO, 3.0, gruix=2.4)
    for ang in (0.5, 2.6, 4.7):
        e.cable('canelobre', [(x, BH + 6, z), (x + math.cos(ang) * 7, BH, z + math.sin(ang) * 5)], FERRO, 2.6,
                gruix=2.0)
    u, v = _p(x, BH + 30, z)
    cv.disc(u, v, 4, 1.5, FERRO, 3.6, lit=0)
    espelma(cv, u, v - 1, 11, gruix=3, lvl=5.0, ramp=CERA)
    if flama_on:
        flama(cv, u, v - 12, 9, 3.4, fase, seed=3)


def pila(e, cv):
    """La pila de baguls vells del mig (girada): un de gros a terra i un de més petit a sobre, de biaix."""
    cx, cz, ang = PILA
    fusta = lambda seed, b: {'ramp': FUSTA, 'lvl': lambda s, t, P: veta(s, t, seed=seed, base=b)}  # noqa: E731
    e.caixa_girada('pila', cx, cz, 64, 40, 36, ang, FUSTA, 3.0,
                   cares={'davant': fusta(51, 3.0), 'esquerra': fusta(52, 2.2), 'dreta': fusta(53, 3.4),
                          'dalt': fusta(54, 4.0)})
    G = _gir(cx, cz, ang)
    for lx in (-22, 22):
        e.cable('pila', [G(lx, 0, -20.6), G(lx, 36.6, -20.6), G(lx, 36.6, 20)], FERRO, 3.2, gruix=3.6)
    e.caixa_girada('pila', cx + 4, cz + 2, 46, 30, 26, ang - 0.32, FUSTA, 3.0, y0=36,
                   cares={'davant': fusta(55, 3.2), 'esquerra': fusta(56, 2.0), 'dreta': fusta(57, 3.6),
                          'dalt': fusta(58, 4.4)})
    G2 = _gir(cx + 4, cz + 2, ang - 0.32)
    for lx in (-15, 15):
        e.cable('pila', [G2(lx, 36, -15.6), G2(lx, 62.6, -15.6), G2(lx, 62.6, 15)], FERRO, 3.0, gruix=3.0)
    # un rotlle de pergamí oblidat damunt
    u, v = _p(*G2(-4, 62.5, -2))
    cv.disc(u, v, 6, 2.2, PERGAMI, lambda nx, ny: 4.0 - ny * 1.4, lit=0)


def ombres(e):
    """Les ombres a terra: sota els baguls i el banc, i la de la pila, llarga cap a la dreta i cap a nosaltres (la
    llum de l'espelma ve del fons a l'esquerra)."""
    e.foscor('ombra', (XL, 0.3, ZB), (BANC[0] + 70, 0.3, ZB), (BANC[0] + 70, 0.3, ZB - 52), (XL, 0.3, ZB - 52),
             lambda s, t: 0.55 * max(0.0, 1 - (52 - t) / 22))
    cx, cz, _ = PILA
    e.foscor('ombra', (cx - 30, 0.3, cz + 26), (cx + 80, 0.3, cz + 26), (cx + 80, 0.3, cz - 60), (cx - 30, 0.3, cz - 60),
             lambda s, t: 0.6 * max(0.0, 1 - math.hypot((s - 30 - (86 - t) * 0.55) / 36, (t - 50) / 34)) ** 0.6)
    # els racons, foscos
    e.foscor('ombra', (XL, 0.3, ZB), (XL + 120, 0.3, ZB), (XL + 120, 0.3, ZF), (XL, 0.3, ZF),
             lambda s, t: 0.35 * max(0.0, 1 - s / 120))


def primer_pla(cv):
    """Una columna fosca a la dreta, tallada per la vora, i l'arrencada de l'arc a dalt: en silueta, a contrallum."""
    COL = [(6, 5, 6), (12, 9, 10), (20, 14, 14), (30, 21, 19), (42, 29, 25), (56, 39, 32)]
    for y in range(0, BOTTOM + 1):
        x0 = 618
        for x in range(int(x0), W):
            u = (x - x0) / (W - x0)
            lvl = 2.2 + (1 - u) * 1.4 - u * 0.6 + (fbm(x / 6, y / 20, 91) - 0.5) * 0.8
            if (y + int(hr(0, int(y / 30), 92) * 30)) % 30 < 2:
                lvl -= 1.0                                                  # les juntes dels tambors
            cv.put(x, y, COL, lvl, lit=0)
        cv.put(x0, y, COL, 4.2, lit=0)                                      # la vora que toca la llum de l'espelma
    # el capitell i l'arrencada de l'arc, a dalt a la dreta
    for y in range(0, 40):
        for x in range(470 + y * 2, W):
            cv.put(x, y, COL, 1.6 + (fbm(x / 8, y / 8, 93) - 0.5) * 0.8, lit=0)
    for x in range(560, W):
        for y in range(40, 52):
            cv.put(x, y, COL, 2.6 - (y - 40) * 0.1, lit=0)
    # a baix a l'esquerra, la vora del banc de pedra, de prop
    for y in range(226, BOTTOM + 1):
        for x in range(0, int(40 + (y - 226) * 1.2)):
            cv.put(x, y, COL, 2.4 + (1.2 if y < 230 else 0) + (fbm(x / 7, y / 7, 94) - 0.5) * 0.9, lit=0)


@functools.lru_cache(maxsize=None)
def _davant():
    cv = Canvas(light=LIGHT, transparent=True)
    primer_pla(cv)
    return sense_hud(cv.img)


# ─── Composició ────────────────────────────────────────────────────────────

@functools.lru_cache(maxsize=None)
def _escena(estat=frozenset()):
    """→ (imatge, Escena): tota la sala amb un estat ('obert', 'doble', 'cofre', 'tapis', 'pedra', 'estendard',
    'gueraula', 'trapa')."""
    cv = Canvas(light=LIGHT)
    e = Escena(cv, CAM, LLUMS, ambient=AMBIENT)
    parets(e)
    clapa_lluna(e)
    finestra(e, cv, 'gueraula' in estat)
    porta(e, cv)
    ombres(e)
    tapis(e, cv, estat)
    cordill(e, cv, estat)
    baguls_fila(e)
    bagul_sunifred(e, cv, estat)
    canelobre(e, cv)
    estendard(e, cv, 'estendard' in estat)
    banc_fons(e, cv, 'trapa' in estat)
    pila(e, cv)
    raig_lluna(cv)
    # la claror de l'espelma a l'aire
    u, v = _p(*FLAMA)
    cv.glow(u, v - 4, 70, (255, 190, 110), 0.22)
    cv.glow(u, v - 4, 16, (255, 230, 170), 0.5)
    cv.img.alpha_composite(_davant())
    cv.P = cv.img.load()
    hud_negre(cv)
    return cv.img, e


def _render(estat=frozenset()):
    return _escena(frozenset(estat))[0]


def _base():
    return _render()


def bg(cv):
    cv.img.paste(_base())
    cv.P = cv.img.load()


def _canvi(estat, sobre=(), sense_de=()):
    """El que canvia de la sala amb `estat` respecte de la sala amb `sobre` (sense el primer pla, ni els píxels que
    pinten els estats de `sense_de`, cadascun respecte del seu)."""
    img = sense(_diff(_render(estat), _render(sobre)), _davant())
    for est, sob in sense_de:
        img = sense(img, _diff(_render(est), _render(sob)))
    return img


def _decorat(estat, sobre=(), sense_de=()):
    def draw(cv):
        cv.img.alpha_composite(_canvi(frozenset(estat), frozenset(sobre), sense_de))
        cv.P = cv.img.load()
    return draw


def _contrapes_terra(cv):
    """La pedra a terra, i la paret nua on penjava: `tapis_apartat` (que es pinta per sobre) hi deixa un forat amb la
    forma de la pedra penjada, i el que es veu pel forat ha de ser la paret, no el tapís del fons."""
    import numpy as np
    tapis = frozenset(('tapis',))
    forat = np.asarray(_diff(_render(frozenset(('tapis', 'pedra'))), _render(tapis)))[..., 3] > 0
    paret = np.asarray(_render(tapis).convert('RGBA')).copy()
    paret[~forat] = 0
    cv.img.alpha_composite(sense(Image.fromarray(paret, 'RGBA'), _davant()))
    cv.img.alpha_composite(_canvi(frozenset(('tapis', 'terra')), tapis))
    cv.P = cv.img.load()


PROPS = {
    'bagul_obert': _decorat(('obert',)),
    # (doble_fons es pinta per sobre de cofre_dins: no en toca els píxels)
    'doble_fons': _decorat(('obert', 'doble'), ('obert',),
                           sense_de=((frozenset(('obert', 'doble', 'cofre')), frozenset(('obert', 'doble'))),)),
    'cofre_dins': _decorat(('obert', 'doble', 'cofre'), ('obert', 'doble')),
    # (tapis_apartat es pinta per sobre de la pedra del contrapès: no en toca els píxels)
    'tapis_apartat': _decorat(('tapis',), sense_de=((frozenset(('tapis', 'pedra')), frozenset(('tapis',))),)),
    'contrapes': _decorat(('tapis', 'pedra'), ('tapis',)),
    # (la pedra a terra: es mira sobre el tapís apartat, que sempre hi és quan s'ha despenjat)
    'contrapes_terra': lambda cv: _contrapes_terra(cv),
    'estendard_paret': _decorat(('estendard',)),
    'gueraula_finestra': _decorat(('gueraula',)),
    'trapa_oberta': _decorat(('trapa',)),
}


# ─── Animacions ─────────────────────────────────────────────────────────────

def _frames_espelma():
    """La flama de l'espelma, que belluga, i la claror que fa (una mica més o menys)."""
    img = _base()
    davant = _davant()
    u, v = _p(*FLAMA)
    frames = []
    n = 12
    for i in range(n):
        cv = Canvas(light=LIGHT, img=img.copy())
        # (es repinta la flama sobre un retall net: el fons sense flama)
        x, z = CANELOBRE
        uu, vv = _p(x, BH + 30, z)
        cv.rect(uu - 8, vv - 26, uu + 8, vv - 12, [(0, 0, 0)], 0, lit=0)
        cv.img.alpha_composite(_sense_flama().crop((uu - 8, vv - 26, uu + 9, vv - 11)), (uu - 8, vv - 26))
        cv.P = cv.img.load()
        flama(cv, uu, vv - 12, 9, 3.4, i / n, seed=3)
        k = 0.5 + 0.12 * math.sin(2 * math.pi * i / n * 2 + 1)
        cv.glow(u, v - 4, 16, (255, 230, 170), k)
        frames.append(sense(_diff(cv.img, img), davant))
    return frames


@functools.lru_cache(maxsize=None)
def _sense_flama():
    """El fons amb l'espelma apagada (per repintar-hi cada fotograma de la flama)."""
    cv = Canvas(light=LIGHT)
    e = Escena(cv, CAM, LLUMS, ambient=AMBIENT)
    parets(e)
    tapis(e, cv, frozenset())
    cordill(e, cv, frozenset())
    baguls_fila(e)
    bagul_sunifred(e, cv, frozenset())
    canelobre(e, cv, flama_on=False)
    u, v = _p(*FLAMA)
    cv.glow(u, v - 4, 70, (255, 190, 110), 0.22)
    return cv.img


ANIMS = {'espelma': {'frames': _frames_espelma, 'frameDuration': 110}}


# ─── Capes del davant ─────────────────────────────────────────────────────

@functools.lru_cache(maxsize=None)
def _pila_img():
    """Els píxels de la pila de baguls (de l'escena: l'amo de cada píxel)."""
    img, e = _escena(frozenset())
    ids = {i for i, sid in enumerate(e.ids) if sid == 'pila'}
    out = Image.new('RGBA', img.size, (0, 0, 0, 0))
    src, dst, W_ = img.load(), out.load(), img.width
    for k, a in enumerate(e.amo):
        if a in ids:
            x, y = k % W_, k // W_
            if y <= BOTTOM:
                dst[x, y] = src[x, y]
    return out


def _pila_base():
    cx, cz, ang = PILA
    G = _gir(cx, cz, ang)
    # la línia base d'un moble girat: la del cantó de davant que queda més al fons
    return round(max(_p(*G(-32, 0, -20))[1], _p(*G(32, 0, -20))[1]) - 6)


FRONT = [{'id': 'davant_pila', 'mask': mascara(_pila_img()), 'baseline': _pila_base(), 'zIndex': 20},
         {'id': 'davant', 'mask': mascara(_davant()), 'baseline': 999, 'zIndex': 20}]


# ─── Geometria (coordenades de sala) ─────────────────────────────────────────

def _caixa_de(sid, pad=2):
    img, e = _escena(frozenset())
    return tuple(round(c) for c in e.caixes[sid])


def _geometria():
    img, e = _escena(frozenset())
    C = e.caixes

    def rc(b, pad=0):
        return rect_de((b[0], b[1]), (b[2], b[3]), pad=pad)

    def davant_de(x, z, dz=22):
        return _p(x, 0, z - dz)

    things = {}
    # els baguls (la fila, la pila i les cantonades)
    for cx, w, nom in BAGULS[1:]:
        things[nom] = {'rect': rc(C[nom], 1), 'walk': davant_de(cx, ZB - 4 - BD, 20)}
    bx = C['baguls']
    px = C['pila']
    # (els baguls de la pila del mig; el de la cantonada queda darrere la gent)
    things['baguls'] = {'rect': rc(px, 1), 'walk': _p(PILA[0] - 50, 0, PILA[1] - 30)}
    cx, cz, w, d, h, a = SUNI
    things['bagul_sunifred'] = {'rect': rc(C['bagul_sunifred'], 2), 'walk': _p(*_suni_pt(4, 0, -d / 2 - 22))}
    # el cofre (quan hi és): dins el bagul obert
    cu, cv_ = _p(*_gir(cx + 14, cz - 4, a)(0, 40, 0))
    things['cofre'] = {'rect': (cu - 16, cv_ - 10, cu + 16, cv_ + 8), 'walk': things['bagul_sunifred']['walk']}
    x0, x1, y0, y1 = TAPIS
    tp = rect_de(_p(x0, y1, ZB), _p(x1, y0, ZB))
    things['tapis'] = {'rect': tp, 'walk': _p((x0 + x1) / 2, 0, ZB - 60)}
    # el cordill: del bagul al tapís (una franja estreta)
    a0 = _p(*_suni_pt(w / 2 - 6, 3, d / 2))
    a1 = _p(TAPIS[0] + 4, 64, ZB - 1)
    things['cordill'] = {'rect': rect_de(a0, a1, pad=5), 'walk': _p(TAPIS[0] - 4, 0, ZB - 56)}
    # el contrapès (visible amb el tapís apartat)
    pu, pv = _p(CORRIOLA[0] + 3, CORRIOLA[1] - 46, ZB - 6)
    things['contrapes'] = {'rect': (pu - 12, pv - 34, pu + 12, pv + 12), 'walk': _p(CORRIOLA[0] + 20, 0, ZB - 56)}
    sx, sz = ESTENDARD
    things['estendard'] = {'rect': rect_de(_p(sx - 26, 206, sz), _p(sx + 26, 0, sz), pad=2),
                           'walk': _p(sx - 18, 0, sz - 36)}
    bc = C['banc_fons']
    things['banc_fons'] = {'rect': rc(bc, 2), 'walk': _p(BANC[0] - 10, 0, BANC[1] - 46)}
    tx, tz, tw, td = TRAPA
    things['trapa'] = {'rect': rect_de(_p(tx - tw / 2, 44, tz + td / 2 + 18), _p(tx + tw / 2, -10, tz - td / 2), pad=2),
                       'walk': _p(tx - 10, 0, tz - td / 2 - 16)}
    z0, z1, fy0, fy1 = FINESTRA
    things['finestra'] = {'rect': rect_de(_p(XL, fy1 + 4, z0 - 4), _p(XL, fy0 - 4, z1 + 4), pad=3),
                          'walk': _p(XL + 70, 0, (z0 + z1) / 2 - 20)}
    pz0, pz1, py0, py1 = PORTA
    things['porta_capitular'] = {'rect': rect_de(_p(XL, py1 + 8, pz1 + 8), _p(XL, 0, pz0 - 8), pad=2),
                                 'walk': _p(XL + 50, 0, (pz0 + pz1) / 2)}
    things['bancs'] = {'rect': rect_de(_p(XL, 30, ZB), _p(XL + 30, 0, PORTA[1] + 14), pad=2), 'walk': _p(XL + 60, 0, 400)}

    # el terra on es camina: davant de la fila de baguls i del banc, fins a baix; sense el banc de pedra
    zf = ZB - 4 - BD - 6                                     # davant dels baguls
    walk = [_p(XL + 34, 0, zf), _p(BANC[0] + 60, 0, zf), _p(BANC[0] + 120, 0, zf - 30),
            (639, _p(BANC[0] + 120, 0, zf - 30)[1] + 10), (639, 250), (40, 250), _p(XL + 34, 0, 300)]
    v_top = min(p[1] for p in walk)
    v_bot = max(p[1] for p in walk)
    # la pila no es trepitja
    cx_, cz_, ang = PILA
    G = _gir(cx_, cz_, ang)
    forat = [_p(*G(lx, 0, lz)) for lx, lz in ((-34, -22), (34, -22), (34, 22), (-34, 22))]
    llum_esp = llum_personatge(CAM, FLAMA, 360, (255, 190, 120), 0.75)
    llum_lluna = llum_personatge(CAM, (XL + 120, 60, 400), 220, (150, 176, 220), 0.35)
    llum_porta = llum_personatge(CAM, (XL + 20, 60, 296), 130, (255, 170, 90), 0.4)
    peu = _p(XL + 74, 0, 312)
    return {
        'things': things,
        'spawns': {'iri': peu, 'vet': _p(XL + 160, 0, 324)},
        'walkable': walk,
        'forats': [forat],
        'floorSquash': 0.42,
        'regions': [{'id': 'perspectiva', 'active': True, 'scaleEnabled': True, 'scaleWalkSpeed': True,
                     'scaleTop': round(_escala_a(v_top - 4), 3), 'scaleBottom': round(_escala_a(v_bot + 4), 3),
                     'points': [(0, v_top - 4), (W - 1, v_top - 4), (W - 1, v_bot + 4), (0, v_bot + 4)]}],
        # la llum dominant és l'espelma, al fons a l'esquerra: les ombres cauen cap a la dreta i cap a nosaltres
        'characterShadow': {'enabled': True, 'color': '#0a0608', 'alpha': 0.45, 'squash': 0.4, 'core': 0.6,
                            'light': {'x': _p(FLAMA[0], 0, FLAMA[2])[0], 'y': _p(FLAMA[0], 0, FLAMA[2])[1],
                                      'stretch': 0.8, 'reach': 160}},
        'characterLights': {'ambient': '#5a5260', 'lights': [llum_esp, llum_lluna, llum_porta]},
    }


GEOMETRIA = _geometria()
