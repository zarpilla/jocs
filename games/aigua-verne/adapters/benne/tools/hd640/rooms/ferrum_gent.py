"""
Aigua Verne — la gent de Ferrum (figures de fons, no sprites): més real que `ferrum_comu.miner`.

Proporcions de persona (el cap, 1/7,5 de l'alçada; la canalla, 1/5,5), espatlles més amples que els malucs, dues
cames separades amb el pes en una, els dos braços (el del darrere, més fosc), la cara de tres quarts (ull, cella,
nas, orella) i roba diferent segons qui és:

  tipus 'miner'  jaqueta de treball fins al maluc, pantalons i botes; casc (amb llum) o el cap descobert;
  tipus 'dona'   jaqueta o toquilla sobre una faldilla llarga, i mocador al cap (o el cabell recollit);
  tipus 'vell'   abric llarg, gorra de plat, una mica corbat;
  tipus 'nen'    jersei, pantalons curts i mitjons, i la gorra o el casc del pare;
  tipus 'nena'   vestit fins als genolls i el cabell recollit.

`facing`: -1 mira a l'esquerra, 1 a la dreta. `light_from`: d'on li ve la llum. `hold`: None, 'bidon' (una garrafa
buida a la mà), 'got' (un got a l'alçada del pit) o 'butxaca' (la mà a la butxaca).
"""
import hd640  # noqa: F401

import math

from hd.pix import hr
from hd640.rooms.ferrum_comu import (
    COAL, IRONF, RUSTF, PLANKF, WHITEV, BLUEV, CLOTH, REDP, SKINF, JACK, DENIM, HELM, TIN)

GREYH = [(40, 38, 40), (74, 70, 70), (112, 108, 104), (150, 146, 140), (190, 186, 178), (222, 218, 210)]
OLIVE = [(18, 20, 14), (32, 36, 24), (50, 54, 36), (70, 74, 48), (94, 96, 64), (120, 120, 82)]
WINE = [(26, 10, 16), (46, 16, 26), (70, 26, 38), (96, 38, 50), (124, 54, 62), (152, 74, 78)]
MUSTARD = [(40, 28, 10), (72, 52, 18), (108, 80, 28), (142, 108, 40), (176, 138, 58), (204, 170, 86)]

_JAQ = {'miner': (JACK, DENIM, RUSTF, PLANKF, OLIVE),
        'dona': (WINE, OLIVE, DENIM, PLANKF, MUSTARD),
        'vell': (JACK, PLANKF, OLIVE, GREYH),
        'nen': (RUSTF, MUSTARD, DENIM, OLIVE),
        'nena': (WINE, MUSTARD, DENIM, REDP)}
_BAIX = {'miner': (DENIM, JACK, COAL, DENIM, PLANKF),
         'dona': (COAL, PLANKF, JACK, DENIM, WINE),
         'vell': (COAL, JACK, DENIM, PLANKF),
         'nen': (DENIM, JACK, PLANKF, COAL),
         'nena': (WINE, DENIM, MUSTARD, RUSTF)}
_CABELL = (COAL, PLANKF, RUSTF, IRONF, MUSTARD)
_PELL = (SKINF, SKINF, SKINF)


SEIENT = 0.25                                                         # l'alçada d'una caixa per seure, per h


def _row(cv, y, xa, xb, ramp, lvl):
    for x in range(int(round(xa)), int(round(xb)) + 1):
        cv.put(x, y, ramp, lvl(x) if callable(lvl) else lvl)


def persona(cv, x, yf, h=80, facing=-1, var=0, tipus='miner', hold=None, light_from=1, casc=None, lamp=True,
            cua=False, mocador=None, seated=False, cap=None, ample=None):
    s = h / 80.0
    f, lf = facing, light_from
    nen = tipus in ('nen', 'nena')
    vell = tipus == 'vell'
    jack = _JAQ[tipus][var % len(_JAQ[tipus])]
    baix = _BAIX[tipus][(var // 2 + var) % len(_BAIX[tipus])]
    hair = GREYH if vell else _CABELL[(var * 3 + 1) % len(_CABELL)]
    skin = SKINF

    def sh(xx, cx, half, base):
        """Llum lateral: més clar del costat del sol, i el cantell de l'ombra més fosc."""
        u = (xx - cx) / max(1.0, half)
        return base + u * lf * 0.9 - (0.7 if u * lf < -0.8 else 0)

    cap_h = h / (cap or (5.6 if nen else 7.4))                        # `cap`: quants caps fa d'alt
    head_rx, head_ry = cap_h * 0.40, cap_h * 0.5
    # assegut (en una caixa d'alçada SEIENT·h, amb els peus a terra a `yf`): el cos baixa fins que el maluc toca el
    # seient; les cuixes van endavant, horitzontals, i les canyelles avall
    drop = h * ((0.47 if not nen else 0.44) - SEIENT) if seated else 0.0
    top = yf - h + drop
    lean = (2.2 * s if vell else 0.6 * s) * f                         # el vell, una mica corbat endavant
    hcx = x + lean * 1.4 + f * 0.6 * s
    hcy = top + head_ry
    neck_y = top + cap_h * 0.98
    sh_y = top + cap_h * 1.18                                         # les espatlles
    hip_y = yf - h * (0.47 if not nen else 0.44) + drop
    knee_y = yf - h * 0.26
    sw = h * (ample or (0.105 if not nen else 0.12))                  # mitja amplada de les espatlles (tres quarts)
    if tipus == 'dona':
        sw *= 0.88
    hw = sw * 0.78                                                    # mitja amplada dels malucs

    # ── les cames ──
    faldilla = tipus == 'dona' or tipus == 'nena'
    peu_dav = x + f * 1.6 * s                                         # la cama de davant, una mica avançada
    for k, lx in (() if seated else ((1, x - f * 2.6 * s), (0, peu_dav + f * 0.8 * s))):  # primer la del darrere
        for yy in range(int(hip_y), int(yf - 2.5 * s) + 1):
            t = (yy - hip_y) / max(1.0, yf - hip_y)
            w = (3.5 - 1.6 * t) * s if not (nen and tipus == 'nen' and yy > knee_y - 3 * s) else 1.7 * s
            cx = x + (lx - x) * t * 1.15
            if tipus == 'nena':                                       # les mitges, sota el vestit
                ramp, lvl = (GREYH, 2.0) if var % 2 else (COAL, 2.6)
            elif tipus == 'nen' and yy > hip_y + (knee_y - hip_y) * 0.55:   # pantalons curts: cama i mitjó
                ramp = GREYH if yy > knee_y + 2 * s else skin
                lvl = 2.6 if ramp is GREYH else 3.2
            else:
                ramp, lvl = baix, 2.4 - (0.4 if abs(yy - knee_y) < 1 else 0)
            _row(cv, yy, cx - w, cx + w, ramp, lambda xx, cx=cx, w=w, lvl=lvl: sh(xx, cx, w, lvl - k * 0.8))
        # la sabata / la bota: la punta cap on mira
        cx = x + (lx - x) * 1.15
        for yy in range(int(yf - 2.5 * s), int(yf) + 1):
            a, b = cx - 2.4 * s - max(0, -f) * 2.6 * s, cx + 2.4 * s + max(0, f) * 2.6 * s
            _row(cv, yy, a, b, COAL, lambda xx: 2.0 + (1.0 if yy == int(yf - 2.5 * s) else 0) - k * 0.6)

    if seated:
        _cames_assegut(cv, x, yf, hip_y, h, s, f, tipus, var, baix, skin, sh)

    # ── la faldilla (les dones fins al turmell, les nenes fins als genolls) ──
    if faldilla and not seated:
        y1 = yf - (5 * s if tipus == 'dona' else h * 0.24)
        for yy in range(int(hip_y - 4 * s), int(y1) + 1):
            t = (yy - hip_y) / max(1.0, y1 - hip_y)
            w = hw + max(0.0, t) * 3.2 * s
            cx = x + lean * 0.2 - f * max(0.0, t) * 0.8 * s
            _row(cv, yy, cx - w, cx + w, baix,                       # amb els plecs
                 lambda xx, cx=cx, w=w: sh(xx, cx, w, 2.6 - (0.6 if int(xx - cx + 40) % 5 == 0 else 0)))
        if tipus == 'dona' and var % 2 == 0:                          # el davantal
            for yy in range(int(hip_y - 3 * s), int(knee_y)):
                cx = x + f * 3.2 * s
                _row(cv, yy, cx - 3.4 * s, cx + 3.4 * s, CLOTH, lambda xx, cx=cx: sh(xx, cx, 3.4 * s, 2.2))

    # ── el tors ──
    bot = hip_y + (h * 0.07 if tipus in ('miner', 'nen') else h * 0.02)    # la jaqueta tapa el maluc
    if vell:
        bot = knee_y - 2 * s
    if seated:
        bot = min(bot, hip_y - 1.5 * s)                               # assegut, la jaqueta no tapa la cuixa                                          # l'abric, fins sota el genoll
    for yy in range(int(sh_y), int(bot) + 1):
        t = (yy - sh_y) / max(1.0, hip_y - sh_y)
        if t < 0.12:                                                  # les espatlles, arrodonides
            w = sw * (0.82 + 0.18 * math.sqrt(max(0.0, t) / 0.12))
        elif t < 0.62:
            w = sw - (sw - hw * (0.95 if tipus != 'dona' else 0.82)) * (t - 0.12) / 0.5
        else:
            w = hw * (0.95 if tipus != 'dona' else 0.82) + (t - 0.62) * (hw * 0.6 if vell else hw * 0.15)
        cx = x + lean * max(0.0, 1 - t) + f * 0.8 * s * (1 - t)
        base = 3.0 - t * 0.3 - (0.6 if yy > bot - 1.2 * s else 0)
        _row(cv, yy, cx - w, cx + w, jack, lambda xx, cx=cx, w=w, base=base: sh(xx, cx, w, base))
        if tipus in ('miner', 'vell') and yy > sh_y + 3 * s:
            cv.put(cx + f * w * 0.35, yy, jack, 1.6)                  # la tapeta dels botons
    if tipus == 'miner' and var % 2 == 0:                             # la banda reflectant
        yy = int(sh_y + (hip_y - sh_y) * 0.66)
        cx = x + lean * 0.3
        _row(cv, yy, cx - hw - s, cx + hw + s, HELM, lambda xx: sh(xx, cx, hw, 3.2))
    if tipus == 'dona' and var % 3 != 1:                              # la toquilla, sobre les espatlles
        for yy in range(int(sh_y - s), int(sh_y + 7 * s)):
            t = (yy - sh_y) / (7 * s)
            w = sw * 0.96 - t * 2 * s
            cx = x + lean + f * (0.4 + t * 1.2) * s
            _row(cv, yy, cx - w, cx + w, CLOTH if var % 2 else GREYH, lambda xx, cx=cx, w=w: sh(xx, cx, w, 1.4))

    # ── els braços ──
    def brac(k, ax, hx, hy, ramp):
        """Un braç de l'espatlla (ax, sh_y) a la mà (hx, hy): màniga gruixuda que s'aprima, i la mà."""
        n = max(2, int(abs(hy - sh_y)))
        for i in range(n + 1):
            t = i / n
            bx, by = ax + (hx - ax) * t, sh_y + 1.5 * s + (hy - 1.5 * s - sh_y - 1.5 * s) * t
            w = (2.6 - 0.8 * t) * s
            _row(cv, int(by), bx - w, bx + w, ramp, lambda xx, bx=bx, w=w: sh(xx, bx, w, 2.6 - k * 0.9))
        if hold != 'butxaca' or k:
            cv.disc(hx, hy, 1.6 * s, 1.8 * s, skin, 3.0 - k * 0.8)

    # el braç del darrere (del costat contrari a on mira), quasi tot amagat
    brac(1, x - f * sw * 0.55 + lean, x - f * sw * 0.7, hip_y - 1 * s, jack)
    # el de davant
    if hold == 'bidon' and seated:
        hx, hy = x + f * h * 0.14, hip_y - 4 * s
    elif hold == 'bidon':
        hx, hy = x + f * sw * 0.45 + lean * 0.3, hip_y + 2 * s
    elif hold == 'got':
        hx, hy = x + f * sw * 0.9 + lean, sh_y + 9 * s
    elif seated:                                                      # la mà, sobre la cuixa
        hx, hy = x + f * h * 0.11, hip_y - 1.5 * s
    elif hold == 'butxaca':
        hx, hy = x + f * sw * 0.2, hip_y - 2 * s
    else:
        hx, hy = x + f * sw * 0.3 + lean * 0.3, hip_y + 4 * s
    brac(0, x + f * sw * 0.15 + lean, hx, hy, jack)
    if hold == 'bidon':                                               # una garrafa buida, de plàstic
        gx, gy = hx + f * 0.5 * s, hy + 1.5 * s
        cv.rect(gx - 3.6 * s, gy, gx + 3.6 * s, gy + 9.5 * s, WHITEV,
                lambda xx, yy: 3.4 + lf * (xx - gx) / (3.6 * s) * 0.9 - (0.6 if yy > gy + 8.5 * s else 0))
        cv.rect(gx - 1.6 * s, gy - 0.6 * s, gx + 1.6 * s, gy + 0.6 * s, WHITEV, 2.2)   # la nansa
        cv.rect(gx - 3.0 * s + f * 2 * s, gy - 1.8 * s, gx - 1.2 * s + f * 2 * s, gy, BLUEV, 2.6)
        cv.disc(hx, hy, 1.6 * s, 1.8 * s, skin, 3.0)                  # la mà, a la nansa
    elif hold == 'got':
        cv.rect(hx - 1.4 * s, hy - 4.2 * s, hx + 1.4 * s, hy - 0.8 * s, TIN, lambda xx, yy: 3.6 + lf * (xx - hx) * 0.4)
        cv.disc(hx, hy - 1.2 * s, 1.6 * s, 1.6 * s, skin, 3.0)

    # ── el coll i el cap ──
    cv.rect(hcx - 1.8 * s - f * 0.6 * s, neck_y - 1, hcx + 1.8 * s - f * 0.6 * s, sh_y + 1, skin,
            lambda xx, yy: 2.2 + lf * (xx - hcx) * 0.25)
    cv.disc(hcx, hcy, head_rx, head_ry, skin, lambda nx, ny: 3.5 + nx * lf * 0.8 - max(0.0, ny) * 0.5)
    # la mandíbula, una mica cap on mira
    cv.disc(hcx + f * head_rx * 0.25, hcy + head_ry * 0.45, head_rx * 0.7, head_ry * 0.5, skin,
            lambda nx, ny: 3.2 + nx * lf * 0.8)
    ex = hcx + f * head_rx * 0.48
    ey = hcy + head_ry * 0.05
    cv.put(ex, ey, COAL, 1.0, lit=0)                                  # l'ull
    cv.put(ex - f * 1, ey - max(1, round(1.3 * s)), hair, 1.2)        # la cella
    cv.put(ex + f * max(1, round(0.8 * s)), ey - max(1, round(1.3 * s)), hair, 1.2)
    nx_ = hcx + f * (head_rx + 0.6)
    cv.put(nx_, ey + max(1, round(1.2 * s)), skin, 3.4 + lf * f * 0.6)   # el nas, que sobresurt
    cv.put(nx_ - f, ey + max(2, round(2.0 * s)), skin, 2.4)
    if s > 0.8:
        cv.put(hcx + f * head_rx * 0.45, hcy + head_ry * 0.62, REDP, 2.2)  # la boca
    if vell:                                                          # barba blanca, curta
        for yy in range(int(hcy + head_ry * 0.4), int(hcy + head_ry * 1.05)):
            _row(cv, yy, hcx - f * head_rx * 0.2 - 1.5 * s, hcx + f * head_rx * 0.9, GREYH,
                 lambda xx: 3.0 + lf * (xx - hcx) * 0.2)
            cv.put(hcx + f * head_rx * 0.45, hcy + head_ry * 0.62, GREYH, 1.6)

    # el cabell: el clatell i la part de dalt (deixa la cara i l'orella)
    def cabell(curt=True):
        cv.disc(hcx - f * head_rx * 0.25, hcy - head_ry * 0.25, head_rx * 1.02, head_ry * 0.82, hair,
                lambda nx, ny: 2.6 + nx * lf * 0.6 - ny * 0.6 + (0.5 if hr(int(nx * 4), int(ny * 4), var) > 0.7 else 0))
        cv.disc(hcx - f * head_rx * 0.55, hcy + head_ry * 0.15, head_rx * 0.55, head_ry * (0.6 if curt else 0.9),
                hair, lambda nx, ny: 2.2 + nx * lf * 0.5)

    def orella():
        cv.disc(hcx - f * head_rx * 0.2, hcy + head_ry * 0.1, max(0.8, 0.9 * s), max(1.0, 1.4 * s), skin,
                lambda nx, ny: 2.6 + nx * lf * 0.4)

    if casc is None:
        casc = tipus == 'miner' and var % 3 != 2 or (tipus == 'nen' and var % 2 == 1)
    if tipus == 'dona' and (mocador if mocador is not None else var % 2 == 0):
        # el mocador: tapa el cap i el clatell, nuat sota la nuca
        moc = (REDP, CLOTH, OLIVE, MUSTARD)[var % 4]
        cv.disc(hcx - f * head_rx * 0.2, hcy - head_ry * 0.2, head_rx * 1.1, head_ry * 0.92, moc,
                lambda nx, ny: 2.8 + nx * lf * 0.7 - ny * 0.4)
        cv.disc(hcx - f * head_rx * 0.9, hcy + head_ry * 0.8, 1.4 * s, 1.6 * s, moc, 2.2)
        # la cara que surt del mocador
        cv.disc(hcx + f * head_rx * 0.42, hcy + head_ry * 0.2, head_rx * 0.62, head_ry * 0.66, skin,
                lambda nx, ny: 3.5 + nx * lf * 0.8 - max(0.0, ny) * 0.4)
    else:
        cabell(curt=not cua and tipus not in ('dona', 'nena'))
        cv.disc(hcx + f * head_rx * 0.42, hcy + head_ry * 0.22, head_rx * 0.6, head_ry * 0.6, skin,
                lambda nx, ny: 3.5 + nx * lf * 0.8 - max(0.0, ny) * 0.4)
        orella()
        if cua or tipus in ('dona', 'nena'):                         # el cabell recollit: una cua o un monyo
            if tipus == 'dona' and not cua:
                cv.disc(hcx - f * head_rx * 1.0, hcy - head_ry * 0.1, 2.0 * s, 2.0 * s, hair,
                        lambda nx, ny: 2.6 + nx * lf * 0.6)
            else:
                for k in range(int(9 * s)):
                    cv.put(hcx - f * (head_rx + 0.4 + k * 0.2), hcy + k * 0.9, hair, 2.6 - k * 0.06)
                    cv.put(hcx - f * (head_rx + 1.4 + k * 0.2), hcy + k * 0.9, hair, 1.8)
    # els ulls, la cella i el nas, per sobre del cabell
    cv.put(ex, ey, COAL, 1.0, lit=0)
    cv.put(nx_, ey + max(1, round(1.2 * s)), skin, 3.4 + lf * f * 0.6)

    if casc:                                                          # el casc, amb el llum al front
        cy = hcy - head_ry * 0.3
        for yy in range(int(cy - head_ry * 0.95), int(cy) + 1):
            t = (yy - (cy - head_ry * 0.95)) / (head_ry * 0.95)
            w = head_rx * (0.55 + 0.62 * math.sqrt(max(0.0, t)))
            _row(cv, yy, hcx - w, hcx + w, HELM, lambda xx, w=w, t=t: 3.6 - t * 0.6 + (xx - hcx) / w * lf * 0.8)
        _row(cv, int(cy + 1), hcx - head_rx * 1.3 + min(0, f) * s, hcx + head_rx * 1.3 + max(0, f) * s, HELM,
             lambda xx: 2.4)
        if lamp:
            lx = hcx + f * head_rx * 1.0
            cv.rect(lx - s, cy - 2.6 * s, lx + s, cy - 0.4 * s, TIN, 4.2)
            cv.flat(lx + f * max(1, s), cy - 1.6 * s, (255, 236, 170))
    elif vell or (tipus == 'nen' and var % 2 == 0):                  # la gorra de plat, amb la visera cap on mira
        cy = hcy - head_ry * 0.45
        cv.disc(hcx - f * head_rx * 0.1, cy, head_rx * 1.12, head_ry * 0.45, JACK if vell else jack,
                lambda nx, ny: 2.2 + nx * lf * 0.7 - ny * 0.4)
        _row(cv, int(cy + head_ry * 0.3), hcx, hcx + f * head_rx * 1.45, COAL, 2.0)


def _cames_assegut(cv, x, yf, hip_y, h, s, f, tipus, var, baix, skin, sh):
    """Les cames d'algú assegut, de tres quarts: la cuixa endavant (horitzontal), el genoll, la canyella avall i la
    sabata a terra. Primer la del darrere (més fosca i una mica enrere)."""
    thigh = h * 0.24
    for k, dx in ((1, -f * 2.2 * s), (0, f * 0.6 * s)):
        kx = x + f * thigh + dx                                       # el genoll
        # la canyella: del genoll a terra, una mica enrere (els peus sota el genoll)
        sx = kx - f * 1.2 * s
        for yy in range(int(hip_y), int(yf - 2.5 * s) + 1):
            t = (yy - hip_y) / max(1.0, yf - hip_y)
            w = (2.9 - 0.9 * t) * s
            cx = kx + (sx - kx) * t
            if tipus == 'nena':
                ramp, lvl = (GREYH, 2.0) if var % 2 else (COAL, 2.6)
            elif tipus == 'nen':                                      # pantalons curts: el genoll i el mitjó
                ramp = GREYH if t > 0.45 else skin
                lvl = 2.6 if ramp is GREYH else 3.2
            else:
                ramp, lvl = baix, 2.2
            _row(cv, yy, cx - w, cx + w, ramp, lambda xx, cx=cx, w=w, lvl=lvl: sh(xx, cx, w, lvl - k * 0.8))
        for yy in range(int(yf - 2.5 * s), int(yf) + 1):              # la sabata, la punta endavant
            a, b = sx - 2.4 * s - max(0, -f) * 2.6 * s, sx + 2.4 * s + max(0, f) * 2.6 * s
            _row(cv, yy, a, b, COAL, lambda xx: 2.0 + (1.0 if yy == int(yf - 2.5 * s) else 0) - k * 0.6)
        # la cuixa: del maluc al genoll, horitzontal (la de davant tapa la del darrere)
        ramp = baix
        for yy in range(int(hip_y - 3.6 * s), int(hip_y + 2.6 * s) + 1):
            a, b = sorted((x - f * 2.5 * s + dx, kx + f * 2.4 * s))
            top_ = yy < hip_y - 2.4 * s
            _row(cv, yy, a, b, ramp, lambda xx: 2.6 + (0.7 if top_ else 0) - (0.6 if yy > hip_y + 1.6 * s else 0)
                 - k * 0.8 + (xx - x) * f * 0.03)
    if tipus == 'nena':                                               # el vestit, sobre la falda i fins al genoll
        for yy in range(int(hip_y - 8 * s), int(hip_y + 3.4 * s) + 1):
            a, b = sorted((x - f * 4 * s, x + f * (thigh + 3.4 * s)))
            _row(cv, yy, a, b, baix, lambda xx: 2.6 + (0.6 if yy < hip_y - 2.6 * s else 0)
                 - (0.6 if int(xx) % 5 == 0 and yy > hip_y else 0))


def persona_c(cv, *a, **kw):
    """`persona` amb el contorn fosc d'1 px de sala (l'estil de tot el joc), com `ferrum_comu.miner_c`."""
    k = cv.S
    tmp = type(cv)(cv.w // k, cv.h // k, light=cv.light, transparent=True)
    persona(tmp, *a, **kw)
    bb = tmp.img.getbbox()
    if not bb:
        return
    T, D = tmp.img.load(), cv.img.load()
    x0, y0, x1, y1 = bb
    near = [(d, 0) for d in range(-k, k + 1) if d] + [(0, d) for d in range(-k, k + 1) if d]
    out = []
    for y in range(max(0, y0 - k), min(cv.h, y1 + k)):
        for x in range(max(0, x0 - k), min(cv.w, x1 + k)):
            if not T[x, y][3] and any(0 <= x + dx < cv.w and 0 <= y + dy < cv.h and T[x + dx, y + dy][3]
                                      for dx, dy in near):
                out.append((x, y))
    for x, y in out:
        T[x, y] = tuple(int(c * 0.35) for c in D[x, y][:3]) + (255,)
    cv.img.alpha_composite(tmp.img)
