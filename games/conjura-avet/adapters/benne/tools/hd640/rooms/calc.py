"""
La Conjura de l'Avet — `calc` (pantalla especial, escenes 4 i 9): el calc amb carbonet. Art definitiu, a 1×.

Un primer pla del pergamí damunt la taula de l'scriptorium, a pantalla sencera, vist una mica des de dalt (el
pergamí és un trapezi: el cantó de dalt, més lluny, més estret) i girat, amb la claror càlida de l'espelma que ve de
dalt a l'esquerra. A les vores, la taula de fusta fosca, el tinter i la ploma, i l'espelma fora de quadre.

El pergamí i tot el que hi passa es dibuixa pla (`PW` × `PH`) i es projecta a la pantalla amb la mateixa homografia
(`_projecta`): així els decorats encaixen al píxel.

Decorats (el motor els pinta per ordre alfabètic: `calc_1` < `calc_2` < `calc_3` < `calc_carta` < `calc_segell`):
  - `calc_1`, `calc_2`, `calc_3`: el carbó que va enfosquint el pergamí per franges (la de dalt, la del mig, la de
    baix), a traços de biaix i amb les vores esparracades. Són els mateixos per als dos casos.
  - `calc_segell` (el pergamí damunt el tros de cera) i `calc_carta` (damunt el pergamí ratllat): el relleu de sota,
    en blanc mig transparent, i el bony que fa. Com que van per sobre del carbó, sobre el pergamí net el relleu
    gairebé no es veu (una mica més clar: com quan es mira de biaix), i sobre el carbó surt en blanc.
    · el segell: un cercle amb un avet al mig i «+ EMMA ABBATISSA» al voltant, trencat (en falta un tros, i amb ell
      la creu, la E i l'última A: es llegeix «...MMA ABBATISS...»);
    · la carta: les línies de lletra de la carta d'en Sunifred i, a baix a la dreta, el signe (una creu amb un llaç).
"""
import functools
import math

from PIL import Image

import hd640  # noqa: F401  (abans de cap hd.rooms: posa la llibreria a 640×360)

from hd.pix import Canvas, Light, W, H, mix
from hd640.font import GLYPHS
from hd640.tres_d import _homografia, _inversa
from hd640.rooms.nit_comu import FUSTA, FERRO, PERGAMI, TINTA, CERA, fbm, hr, flama, veta

LIGHT = Light(ambient=0.0, vignette=None, floor_fade=None)

PW, PH = 480, 228                                   # el pergamí, pla (en píxels del dibuix)
QUAD = ((92, 20), (560, 12), (594, 250), (52, 242))  # on cau a la pantalla (dalt esq., dalt dreta, baix dreta, baix esq.)
SEGELL = (240, 112, 78)                              # el segell al pergamí: centre x, y, radi
LLEGENDA = '+ EMMA ABBATISSA'                        # al voltant del segell, des de dalt (en sentit horari)
A_INI = -0.42                                        # l'angle on comença (0 = dalt)


# ─── La projecció ────────────────────────────────────────────────────────────

@functools.lru_cache(maxsize=None)
def _coefs():
    """Coeficients de PIL (PERSPECTIVE) que porten cada píxel de la pantalla al dibuix pla del pergamí."""
    Hm = _homografia(QUAD)                           # quadrat unitat → pantalla
    a, b, c, d, e, f, g, h, i = _inversa(Hm)         # pantalla → quadrat unitat
    # (s, t) = ((a x + b y + c) / (g x + h y + i), ...) → píxels del dibuix: × PW, × PH; normalitzat perquè i = 1
    return (a * PW / i, b * PW / i, c * PW / i, d * PH / i, e * PH / i, f * PH / i, g / i, h / i)


def _projecta(img):
    """Un dibuix pla del pergamí (PW × PH, RGBA) → la capa de la pantalla (640 × 360)."""
    out = img.transform((W, H), Image.Transform.PERSPECTIVE, _coefs(), Image.Resampling.BILINEAR)
    # (els vores mig transparents del bilineal: o hi són o no hi són, llevat del que ja és mig transparent)
    return out


# ─── El pergamí ──────────────────────────────────────────────────────────────

def _vora(x, y):
    """Quant hi ha de pergamí a (x, y) del dibuix: les vores no són rectes (pell, retallada a mà)."""
    d = min(x, y, PW - 1 - x, PH - 1 - y)
    n = (fbm(x / 18, y / 18, 3) - 0.5) * 7 + (fbm(x / 4, y / 4, 4) - 0.5) * 2
    return d + n > 2


@functools.lru_cache(maxsize=None)
def _pergami():
    """El pergamí net: pell crema, més fosca i groguenca a les vores, amb fibres, taques i la claror de l'espelma
    (de dalt a l'esquerra)."""
    cv = Canvas(PW, PH, light=LIGHT, transparent=True)
    for y in range(PH):
        for x in range(PW):
            if not _vora(x, y):
                continue
            d = min(x, y, PW - 1 - x, PH - 1 - y)
            v = 4.6 + (fbm(x / 40, y / 30, 11) - 0.5) * 0.9 + (fbm(x / 3, y / 9, 12) - 0.5) * 0.35
            v -= max(0.0, 1 - d / 26) * 1.1                                  # les vores, més torrades
            v -= (x / PW) * 0.5 + (y / PH) * 0.5                             # la llum, de dalt a l'esquerra
            if fbm(x / 22, y / 22, 13) > 0.7:
                v -= 0.6                                                     # taques
            cv.put(x, y, PERGAMI, v, lit=0)
    return cv.img


# ─── El relleu del segell ────────────────────────────────────────────────────
# El relleu es pinta del color del pergamí, gairebé opac: sobre el pergamí net quasi no es veu, i sobre el carbó és el
# pergamí que el carbonet no ha tocat (les ratlles enfonsades): surt clar.
BLANC = (216, 194, 150, 215)


def _angles(text=LLEGENDA, r=None, k=2):
    """(lletra, angle del mig, amplada en radians) de cada lletra de la llegenda."""
    r = r or SEGELL[2] - 7
    a = A_INI
    out = []
    # l'espai entre lletres: que la llegenda faci tota la volta, menys un bocí (on es toquen el principi i el final)
    base = sum((len(GLYPHS[ch][0]) if ch in GLYPHS else 2) * k for ch in text)
    esp = (2 * math.pi * r - 0.35 * r - base) / len(text)
    for ch in text:
        w = ((len(GLYPHS[ch][0]) if ch in GLYPHS else 2) * k + esp) / r
        out.append((ch, a + w / 2, w))
        a += w
    return out


@functools.lru_cache(maxsize=None)
def _tros():
    """El tros que falta del segell (de l'angle a l'angle): s'hi perden la creu, la E i l'última A."""
    ang = _angles()
    _, am_e, w_e = ang[2]
    _, am_a, w_a = ang[-1]
    return (am_a - w_a / 2 - 2 * math.pi - 0.04, am_e + w_e / 2 + 0.03)


def _al_tros(a):
    """Si l'angle `a` (0 = dalt, en sentit horari) cau al tros que falta del segell."""
    a0, a1 = _tros()
    a = (a - a0) % (2 * math.pi) + a0
    return a <= a1


def _dins_segell(x, y, marge=0.0):
    cx, cy, R = SEGELL
    dx, dy = x - cx, y - cy
    r = math.hypot(dx, dy)
    a = math.atan2(dx, -dy)
    # la vora del trencat és en ziga-zaga
    zz = math.sin(r / 4) * 0.08
    a0, a1 = _tros()
    aa = (a - a0) % (2 * math.pi) + a0
    trencat = (a0 + zz) <= aa <= (a1 - zz) and r > R * 0.18
    return r <= R + marge and not trencat


def _punt(img, x, y, col, k=2):
    P = img.load()
    for yy in range(int(y), int(y) + k):
        for xx in range(int(x), int(x) + k):
            if 0 <= xx < img.width and 0 <= yy < img.height:
                P[xx, yy] = col


def _lletres_cercle(img, text, cx, cy, r, a_ini, col, k=2):
    """Escriu `text` al voltant d'un cercle (en sentit horari, des de l'angle `a_ini`; 0 = dalt), amb la lletra del
    joc a escala `k`, les lletres dretes cap enfora. No pinta el que cau al tros que falta."""
    for ch, am, da in _angles(text, r, k):
        if ch != ' ' and ch in GLYPHS:
            g = GLYPHS[ch]
            gw, gh = len(g[0]), len(g)
            if not _al_tros(am):
                for j, row in enumerate(g):
                    for i, bit in enumerate(row):
                        if bit != '#':
                            continue
                        for sy in range(k):
                            for sx in range(k):
                                lx = (i * k + sx + 0.5) - gw * k / 2           # tangent
                                ly = (j * k + sy + 0.5)                        # cap a dins
                                rr = r - ly
                                aa = am + lx / max(1.0, rr)
                                px, py = cx + math.sin(aa) * rr, cy - math.cos(aa) * rr
                                _punt(img, px, py, col, 1)


def _creu(img, x, y, s, col, k=2):
    for d in range(-s, s + 1):
        _punt(img, x + d, y, col, k)
        _punt(img, x, y + d, col, k)


@functools.lru_cache(maxsize=None)
def _relleu_segell():
    """El relleu del tros de cera (blanc mig transparent) i el bony que fa sota el pergamí."""
    img = Image.new('RGBA', (PW, PH), (0, 0, 0, 0))
    P = img.load()
    cx, cy, R = SEGELL
    # el bony: llum a dalt a l'esquerra, ombra a baix a la dreta, a la vora del tros de cera
    for y in range(int(cy - R - 10), int(cy + R + 11)):
        for x in range(int(cx - R - 10), int(cx + R + 11)):
            if not (0 <= x < PW and 0 <= y < PH and _vora(x, y)):
                continue
            dx, dy = x - cx, y - cy
            r = math.hypot(dx, dy)
            if r > R + 9:
                continue
            dins = _dins_segell(x, y)
            if dins and r > R - 6:
                k = (-(dx + dy) / max(1.0, r)) * 0.5                      # >0: cara que mira la llum
                if k > 0:
                    P[x, y] = (255, 246, 220, int(110 * k))
                else:
                    P[x, y] = (40, 24, 10, int(-140 * k))
            elif not dins and r <= R + 9 and _dins_segell(x - 6, y - 6, 0):
                P[x, y] = (40, 24, 10, 70)                               # l'ombra que fa fora
    blanc = BLANC
    # la doble vora del segell
    for r in (R - 4, R - 22):
        for i in range(int(2 * math.pi * r * 1.5)):
            a = i / (r * 1.5)
            if _al_tros(a):
                continue
            x, y = cx + math.sin(a) * r, cy - math.cos(a) * r
            if _dins_segell(x, y):
                _punt(img, x, y, blanc, 2)
    # la llegenda: «+ EMMA ABBATISSA» des de dalt
    _lletres_cercle(img, LLEGENDA, cx, cy, R - 7, A_INI, blanc, k=2)
    # (la creu del principi, si no ha caigut al tros)
    # l'avet al mig: un tronc i cinc pisos de branques, cada pis més ample
    for i in range(5):
        yy = cy - 42 + i * 13
        w = 8 + i * 6
        for t in range(14):
            for x in range(int(cx - w * t / 13), int(cx + w * t / 13) + 1):
                if t >= 12 or abs(x - cx) >= int(w * t / 13) - 2:
                    _punt(img, x, yy + t, blanc, 1)
    for y in range(int(cy + 24), int(cy + 42)):
        for dx in (-4, -3, 3, 4):
            _punt(img, cx + dx, y, blanc, 1)
    for x in range(int(cx - 16), int(cx + 17)):
        _punt(img, x, cy + 42, blanc, 2)                                    # la terra
    # el que queda fora del tros de cera (el trencat) no té relleu
    for y in range(PH):
        for x in range(PW):
            p = P[x, y]
            if p[3] and p[1] > 150 and not _dins_segell(x, y):
                P[x, y] = (0, 0, 0, 0)
    return img


# ─── El relleu de la carta ───────────────────────────────────────────────────

@functools.lru_cache(maxsize=None)
def _relleu_carta():
    """El que deixa la carta de sota (el pergamí ratllat): línies de lletra petita i apretada, i el signe a baix."""
    img = Image.new('RGBA', (PW, PH), (0, 0, 0, 0))
    blanc = BLANC
    x0, x1 = 40, PW - 40
    linies = 9
    for li in range(linies):
        y = 26 + li * 19
        fi = x1 - (120 if li == linies - 1 else int(hr(li, 2, 5) * 40))
        x = x0 + (24 if li == 0 else 0)
        while x < fi:
            paraula = 10 + int(hr(int(x), li, 6) * 34)
            for i in range(paraula):
                xx = x + i
                if xx > fi:
                    break
                # la lletra: pals amunt i avall, i el traç que els lliga (una lletra de llibre, vista de lluny)
                fase = (xx * 0.9 + li * 3) % 5
                alt = 7 if (hr(int(xx / 5), li, 7) > 0.8 and fase < 1) else 4
                if fase < 1.0:
                    for yy in range(y - alt, y + 1):
                        _punt(img, xx, yy, blanc, 1)
                _punt(img, xx, y - 1 + math.sin(xx * 0.7) * 1.2, blanc, 1)
            x += paraula + 6 + int(hr(int(x), li, 8) * 4)
    # la caplletra de la primera línia
    for t in range(16):
        _punt(img, x0 + 4 + math.sin(t / 3) * 4, 14 + t, blanc, 2)
    # el signe, a baix a la dreta: una creu amb un llaç (la creu, i al peu una llaçada)
    sx, sy = x1 - 54, PH - 56
    for d in range(-16, 17):
        _punt(img, sx + d, sy - 6, blanc, 3)
    for d in range(-24, 18):
        _punt(img, sx, sy + d, blanc, 3)
    for i in range(80):
        a = i / 80 * 2 * math.pi
        _punt(img, sx + math.sin(a) * 9 + math.sin(2 * a) * 3, sy + 26 + math.cos(a) * 6, blanc, 3)
    return img


# ─── El carbó ────────────────────────────────────────────────────────────────

FRANGES = ((0, 86), (68, 162), (144, PH))         # les tres franges (y de dalt i de baix, al dibuix)


@functools.lru_cache(maxsize=None)
def _carbo(n):
    """La franja `n` (1..3) de carbó: traços de biaix, més o menys apretats, i les vores esparracades (on s'acaba
    cada passada)."""
    img = Image.new('RGBA', (PW, PH), (0, 0, 0, 0))
    P = img.load()
    y0, y1 = FRANGES[n - 1]
    for y in range(max(0, y0 - 10), min(PH, y1 + 10)):
        for x in range(PW):
            if not _vora(x, y):
                continue
            # la vora de la passada: esparracada, amb traços que en surten
            traç = math.sin((x + y * 0.55) / 2.2 + fbm(x / 9, y / 9, 20 + n) * 6)
            top = y0 + (fbm(x / 14, 1, 30 + n) - 0.5) * 16 + (4 if traç > 0.4 else 0)
            bot = y1 + (fbm(x / 14, 2, 40 + n) - 0.5) * 16 - (4 if traç > 0.4 else 0)
            if n == 1:
                top = -99
            if n == 3:
                bot = PH + 99
            if not (top <= y <= bot):
                continue
            # i també als costats, que no arriben del tot a la vora
            d = min(x, PW - 1 - x)
            if d < 10 + fbm(1, y / 10, 50 + n) * 14:
                continue
            # traços de biaix (la passada del carbonet): més o menys carregats, amb el gra del pergamí
            ratlla = math.sin((x * 0.8 - y * 1.6) / 1.7 + fbm(x / 20, y / 6, 80 + n) * 9)
            k = 0.78 + ratlla * 0.12 + (fbm(x / 7, y / 5, 60 + n) - 0.5) * 0.35 + (hr(x, y, 70 + n) - 0.5) * 0.14
            k = max(0.4, min(1.0, k))
            g = int(34 + (1 - k) * 70)
            vora = min(y - top, bot - y)                                 # a la vora de la passada, menys carregat
            fa = min(1.0, max(0.25, vora / 8))
            P[x, y] = (g, g - 2, g - 4, int(255 * min(1.0, 0.62 + k * 0.32) * fa))
    return img


# ─── La taula ────────────────────────────────────────────────────────────────

@functools.lru_cache(maxsize=None)
def _fons():
    cv = Canvas(light=LIGHT)
    # la taula: fusta fosca, la veta de biaix, la claror de l'espelma a dalt a l'esquerra
    for y in range(H):
        for x in range(W):
            s, t = x * 0.94 + y * 0.34, y * 0.94 - x * 0.34
            v = veta(s, t / 3, seed=5, base=3.0) - (0.9 if int(t) % 46 < 2 else 0)
            v += max(0.0, 1 - math.hypot(x - 40, y + 30) / 520) * 2.2 - 0.6
            cv.put(x, y, FUSTA, v, lit=0)
    # l'ombra del pergamí a la taula (una mica cap a la dreta i avall)
    sh = _projecta(_pergami())
    a = sh.getchannel('A').point(lambda v: 150 if v > 128 else 0)
    ombra = Image.new('RGBA', (W, H), (8, 4, 2, 0))
    ombra.putalpha(a)
    cv.img.alpha_composite(ombra, (6, 7))
    cv.P = cv.img.load()
    # el pergamí
    cv.img.alpha_composite(_projecta(_pergami()))
    cv.P = cv.img.load()
    # les pedres que el tenen pla (cantons de dalt): dos còdols
    for x, y in ((104, 30), (548, 22)):
        cv.disc(x, y, 12, 8, [(20, 18, 18), (40, 36, 34), (64, 58, 52), (92, 84, 74), (124, 114, 100)],
                lambda nx, ny: 2.8 - nx * 0.8 - ny * 1.0, lit=0)
    # el tinter i la ploma, a baix a la dreta (fora del pergamí)
    cv.disc(612, 300, 20, 12, FERRO, lambda nx, ny: 2.6 - nx * 0.6 - ny * 0.8, lit=0)
    cv.disc(612, 296, 12, 6, TINTA, 0.6, lit=0)
    for i in range(70):
        t = i / 69
        x, y = 600 - t * 70, 292 - t * 60
        cv.put(x, y, CERA, 5.2 - t * 0.8, lit=0)
        if 0.2 < t < 0.95:
            for j in range(1, int(7 * math.sin(t * math.pi)) + 1):
                cv.put(x - j * 0.6, y + j * 0.7, CERA, 4.4 - j * 0.25, lit=0)
    # la resplendor de l'espelma, que és fora de quadre a dalt a l'esquerra
    cv.glow(0, 0, 260, (255, 190, 110), 0.18)
    # vinyeta a les cantonades de baix
    cv.darken(0, 0, W - 1, H - 1, lambda x, y: max(0.0, math.hypot((x - 320) / 400, (y - 140) / 260) - 0.85) * 2.0)
    return cv.img


def bg(cv):
    cv.img.paste(_fons())
    cv.P = cv.img.load()


def _capa(fn):
    def draw(cv):
        cv.img.alpha_composite(_projecta(fn()))
        cv.P = cv.img.load()
    return draw


PROPS = {
    'calc_1': _capa(lambda: _carbo(1)),
    'calc_2': _capa(lambda: _carbo(2)),
    'calc_3': _capa(lambda: _carbo(3)),
    'calc_segell': _capa(_relleu_segell),
    'calc_carta': _capa(_relleu_carta),
}


GEOMETRIA = {
    'things': {'pergami': {'rect': (56, 14, 592, 250), 'walk': (320, 252)}},
    'spawns': {},
}
