"""
L'Última Arrel — `toll_gripaus`, el toll dels gripaus buròcrates (Escena 4, Iri). Diumenge, migdia. Sala «de lluny».

Un aiguamoll sec, calorós, amb la llum alta i blanca. La càmera és a l'alçada dels ulls d'un adult (sense picat: les
verticals, verticals), amb l'horitzó a y = 110: el terra fuig cap al fons i les esquerdes del fang s'empetiteixen.

  - Al mig a l'esquerra, l'**arxiu** dels gripaus: una soca buida enorme amb calaixets a l'escorça, una finestreta de
    taquilla a l'alçada d'un gripau (amb el cartellet «VAGA» i un ràfec de taulons), impresos clavats i els rètols
    «REGISTRE DEL BOSC» i «HORARI: QUAN HI HA AIGUA». La façana mira cap a l'esquerra, cap al camí: es veu de tres
    quarts (es dibuixa plana i s'embolcalla a la soca; els rètols, clavats, es tomben). El Registrador (`bufo`) és
    davant la finestreta.
  - Al mig a la dreta, el **toll** sec, amb fondària: la paret del fons, les pedres i el llavi de la vora, fang
    clivellat, una línia de sal i els **joncs** grocs i caiguts (alguns, a la vora de davant).
  - Al fons a la dreta, el turó, i el **rierol** que en baixa per un llit de pedres i no arriba: el tapa el
    **tap de plàstics** (ampolles buides d'«Aire Pur»; prop `tap_plastics`, que desapareix), i just a sobre, el tub nou
    de NaturaPlus, blanc i gris, amb la roda de la **comporta** i la placa «ASPERSORS GESPA — SECTOR 4», que se'n va
    cap a la tanca del fons.
  - El gripau vaguista (`gripau`) amb la pancarta, i al costat un altre de fons (sense id) amb una altra pancarta.
  - A l'esquerra, el **camí** (sortida, que no surt), i el bosc càlid, que fa ombra.
  - La mata de joncs de l'esquerra del toll és una capa del davant amb la seva línia base (FRONT): s'hi passa per
    darrere i per davant.
  - Primer pla (FRONT): a les cantonades de baix, molt a prop i a l'ombra, falgueres, joncs i boga en silueta, el
    tronc caigut i una pedra: emmarquen el quadre.

Decorat `aigua` (sota els personatges): el toll ple, el rierol que corre fins al toll i els joncs redreçats.
ANIMS: `libellules` (tres libèl·lules que volen sobre el toll) i `calor` (l'aire que tremola a l'horitzó).
"""
import functools
import math
import random

from PIL import Image

from hd.pix import Canvas, Light
from hd640.rooms._comu_dia import (
    W, H, RH, Terra, fbm, hr, boira_px, esquerda, smooth, lletres, ample, arrel, ombra, jonc, mata_joncs, capcada, tronc,
    falguera, diferencia, mascara, HAZE, LEAVES, BARK, MOSS, EARTH, PLANK, IRONK, STONE, CREAM, BRASS, PLASTIC, STEEL, NEON,
    REDL, YELLOWM, SKYD, DRYG, CLAY, GREENL, WATER, FERN, TURQ)

T = Terra(hor=110, h=140, f=500)
HOR = T.hor
SOL = (150, -40)                                   # el sol, alt i una mica a l'esquerra

LIGHT = Light(ambient=0.35, vignette=(60, 12), floor_fade=None)
LIGHT.width = W
LIGHT.point(SOL[0], SOL[1], r=520, k=0.9, squash=0.7, power=1.2)

# On és cada cosa (en píxels de sala)
SOCA = (236, 206, 62)                              # l'arxiu: centre x, base, mig ample
FINESTRA = (222, 166, 252, 192)                   # x0, y0, x1, y1 de la finestreta
TOLL = (462, 221, 100, 15)                         # el toll: centre, radis
TAP = (566, 189)                                   # el tap de plàstics (al llit del rierol)
RODA = (606, 168)                                  # la roda de la comporta
# El llit del rierol: del turó (lluny) fins al toll (a prop): punts de pantalla i ample
RIEROL = [(532, 70, 1.5), (540, 88, 2.5), (530, 110, 3.5), (546, 138, 5), (560, 164, 7), (TAP[0], TAP[1], 9),
          (558, 205, 10), (TOLL[0] + TOLL[2] - 16, TOLL[1] - 5, 12)]


# ─── El cel, el bosc i el turó del fons ──────────────────────────────────────

def cel(cv):
    for y in range(0, HOR + 4):
        for x in range(W):
            d = math.hypot(x - SOL[0], (y - SOL[1]) * 1.3)
            lvl = 2.4 + 3.6 * (y / HOR) ** 1.6 + 2.2 * max(0.0, 1 - d / 300) ** 1.5
            lvl += (fbm(x / 90, y / 10, 3) - 0.5) * 0.7
            cv.put(x, y, SKYD, lvl, lit=0)
    cv.glow(SOL[0], 0, 120, (255, 252, 236), 0.6)


BOIRA = (220, 226, 222)                            # el color de la calitja del migdia


def bosc_fons(cv):
    """La ratlla del bosc a l'horitzó: càlid però esvaït per la calitja del migdia."""
    for x in range(0, W):
        top = HOR - 24 - 14 * fbm(x / 30, 0.5, 9) - 8 * fbm(x / 8, 1.5, 4) + 16 * smooth(380, 600, x)
        for y in range(int(top), HOR + 3):
            f = fbm(x / 6, y / 5, 6)
            fulla = fbm(x / 22, y / 14, 7) > 0.5
            lvl = 3.6 + (f - 0.5) * 2.0 - (y - top) * 0.04 + (1.0 if top + 2 > y else 0)
            cv.put(x, y, LEAVES if fulla else GREENL, lvl + (0.6 if fulla else 0), lit=0.2)
            boira_px(cv, x, y, BOIRA, 0.45 - (y - top) * 0.004)


def tanca_fons(cv):
    """La tanca de NaturaPlus, lluny, a la dreta del turó: freda i gris."""
    for x in range(596, W):
        base = HOR + 6
        h = 12
        for y in range(base - h, base):
            if (x + y) % 3 == 0 or (x - y) % 3 == 0:
                cv.put(x, y, STEEL, 5.4, lit=0)
        cv.put(x, base - h, STEEL, 6.4, lit=0)
    for x in (600, 614, 628):
        cv.rect(x, HOR - 8, x, HOR + 6, STEEL, 4.4, lit=0)


def _turo_dalt(x):
    return 64 + max(0.0, 470 - x) * 0.6 + 5 * fbm(x / 24, 0.3, 12) + 10 * smooth(570, 640, x)


def turo(cv):
    """El turó de la dreta: herba seca, pedres, unes mates; d'aquí baixa el rierol."""
    for x in range(384, W):
        top = _turo_dalt(x)
        for y in range(int(top), HOR + 6):
            t = (y - top) / max(1, HOR + 6 - top)
            f = fbm(x / 14, y / 6, 13)
            lvl = 3.6 + (f - 0.5) * 1.6 - t * 0.5 + (1.0 if y - top < 2 else 0)
            lvl -= 1.0 * smooth(560, 640, x)                                      # la cara de la dreta, a l'ombra
            cv.put(x, y, DRYG, lvl, lit=0.4)
            if hr(x, y, 31) > 0.985:
                cv.put(x, y, STONE, 5.0, lit=0.3)
            boira_px(cv, x, y, BOIRA, 0.22)
    # unes mates al turó, amb la seva ombra
    for (x, y, r, s) in ((426, 102, 7, 1), (470, 84, 5, 2), (604, 76, 8, 3), (626, 84, 5, 4), (590, 102, 5, 5),
                         (506, 96, 4, 6)):
        ombra(cv, x + 2, y + 1, r * 1.6, 1.6)
        capcada(cv, x - r * 2, x + r * 2, y - r * 1.8, y + 2, s, ramp=GREENL, base=2.6, edge=0.36, lit=0.4, sx=5, sy=4,
                forma=lambda xx, yy, x=x, y=y, r=r: max(0.0, math.hypot((xx - x) / (r * 1.9), (yy - y + r * 0.6) / (r * 1.2)) - 0.6),
                boira=(BOIRA, 0.15))


def bosc_esquerra(cv):
    """El bosc càlid de l'esquerra: troncs i la capçada que fa ombra a la cantonada de dalt."""
    tronc(cv, 150, 20, 198, 6, 10, 7, base=3.0, lit=0.4, molsa=0.8)
    tronc(cv, 66, -4, 216, 14, 24, 3, base=2.8, lit=0.4, molsa=0.75)
    tronc(cv, 6, -4, 234, 18, 28, 5, base=1.8, lit=0.3, molsa=0.8)
    for p0, p1, p2, r0, r1, s in (((72, 40), (150, 24), (270, 4), 7, 2, 21), ((66, 74), (24, 64), (-10, 46), 6, 3, 22),
                                  ((150, 52), (200, 40), (244, 30), 3, 1, 23), ((150, 70), (190, 66), (214, 76), 2, 1, 24)):
        arrel(cv, p0, p1, p2, r0, r1, base=2.6, seed=s, lit=0.3, moss=False)

    def forma(x, y):
        return max(0.0, math.hypot((x + 20) / 360, (y + 40) / 140) - 0.72) * 1.3
    capcada(cv, -10, 350, -4, 110, 41, ramp=LEAVES, ramp2=GREENL, base=3.0, edge=0.38, lit=0.5, sx=15, sy=10,
            forma=forma)


# ─── El terra ────────────────────────────────────────────────────────────────

def _cami(u, v):
    """Distància (px) al camí de terra trepitjada, que ve de l'esquerra i arriba a l'arxiu."""
    if v < 200:
        return 99
    t = (v - 200) / 60
    cx = 200 - (v - 204) * 3.4
    return abs(u - cx) - (10 + 34 * t)


def _toll_d(u, v):
    cx, cy, rx, ry = TOLL
    return math.hypot((u - cx) / rx, (v - cy) / ry)


def terra(cv):
    for v in range(HOR + 2, RH):
        for u in range(W):
            if u >= 390 and v < HOR + 6:
                continue                                                         # (el peu del turó ja hi és)
            x, z = T.mon(u, v)
            near = smooth(600, 300, z)                                           # 0 lluny … 1 a prop
            f = fbm(x / 60, z / 110, 12)
            lvl = 3.0 + (f - 0.5) * 2.6 + near * 0.4
            ramp = DRYG
            # l'herba seca en mates, més grosses a prop
            g = fbm(x / (5 + 3 * near), z / (9 + 6 * near), 14)
            if g > 0.6:
                lvl += 1.0
            elif g < 0.36:
                lvl -= 0.7
            if fbm(x / 90, z / 160, 15) > 0.62:                                  # clapes d'herba encara verda
                ramp = MOSS
                lvl += 1.6
            # el fang sec (al voltant del toll i pel camí)
            dt = _toll_d(u, v)
            if dt < 1.9 or _cami(u, v) < 0:
                k = smooth(1.9, 1.3, dt) if dt < 1.9 else 1.0
                if _cami(u, v) < 0:
                    k = max(k, smooth(0, -8, _cami(u, v)))
                if hr(u, v, 3) < k:
                    ramp = CLAY
                    lvl = 4.6 + (f - 0.5) * 1.4 + near * 0.3
            # l'ombra de la capçada de l'esquerra, a clapes (el sol és alt: cau just a sota)
            om = smooth(250, 120, u + (v - 200) * 0.6) * (0.6 + 0.6 * fbm(u / 14, v / 6, 33))
            lvl -= 2.2 * min(1.0, om)
            cv.put(u, v, ramp, lvl, lit=0.5)
            if hr(u, v, 9) > 0.993 - near * 0.01:                                 # còdols
                cv.put(u, v, STONE, 5.2 - 2 * om, lit=0.3)
            if v < HOR + 30:
                boira_px(cv, u, v, BOIRA, 0.4 * (1 - (v - HOR) / 30))


def toll_sec(cv):
    """El toll: una cubeta de fang clivellat, més fosca a la vora del fons (el desnivell) i amb la línia de sal."""
    cx, cy, rx, ry = TOLL
    for v in range(int(cy - ry - 2), int(cy + ry + 3)):
        for u in range(int(cx - rx - 2), int(cx + rx + 3)):
            d = _toll_d(u, v)
            if d > 1.04:
                continue
            x, z = T.mon(u, v)
            c = esquerda(x / 16, z / 22, 5)
            lvl = 4.4 + (fbm(x / 20, z / 30, 3) - 0.5) * 1.2
            ny = (v - cy) / ry
            lvl += ny * 0.8                                                      # la paret del fons, a l'ombra
            if d > 0.9:
                lvl += 1.6 if ny > 0 else -1.2                                   # la vora: sal a prop, ombra al fons
            if c < 0.05 + 0.04 * smooth(700, 450, z):
                lvl -= 2.4                                                       # les esquerdes
            elif c < 0.09:
                lvl += 0.8                                                       # la vora aixecada de cada placa
            cv.put(u, v, CLAY, lvl, lit=0.4)
    vores_toll(cv)
    # unes petjades de gripau i una ampolla mig enterrada
    for (u, v) in ((420, 224), (428, 226), (436, 223)):
        cv.put(u, v, CLAY, 2.0, lit=0)
    cv.rect(500, 226, 505, 227, PLASTIC, 5.0, lit=0)
    cv.flat(506, 226, (90, 210, 70))


def vores_toll(cv):
    """La fondària del toll: la paret del fons (de cara a nosaltres i al sol: clara, amb les capes del fang i les
    arrels que hi pengen), el llavi de terra de la vora de davant i pedres a la vora, amb la seva ombra."""
    cx, cy, rx, ry = TOLL
    for u in range(int(cx - rx), int(cx + rx) + 1):
        n = (u - cx) / rx
        if abs(n) >= 1:
            continue
        q = math.sqrt(1 - n * n)
        yt, hw = cy - ry * q, 6.5 * q ** 0.7
        for v in range(int(yt), int(yt + hw) + 1):
            t = (v - yt) / max(1.0, hw)
            lvl = 5.2 - t * 1.6 - (0.9 if int(v - n * 3) % 3 == 0 else 0) + (fbm(u / 5, v / 2, 81) - 0.5) * 1.0
            cv.put(u, v, CLAY, lvl, lit=0.4)
        cv.put(u, yt + hw + 1, CLAY, 1.4, lit=0)                                # l'ombra al peu de la paret
        if hr(u, 3, 82) > 0.86:                                                   # arrels que pengen
            for j in range(int(2 + hr(u, 4, 83) * hw)):
                cv.put(u, yt + 1 + j, BARK, 2.0, lit=0)
        yb = cy + ry * q                                                          # el llavi de davant
        cv.put(u, yb, DRYG, 5.4, lit=0.4)
        cv.put(u, yb + 1, DRYG, 4.0, lit=0.4)
    for k, a in enumerate((3.5, 3.9, 4.4, 5.4, 5.9, 0.4, 1.0, 2.2, 2.7)):        # pedres a la vora
        px, py = cx + math.cos(a) * rx * 1.02, cy + math.sin(a) * ry * 1.06
        r = 2.5 + (py - (cy - ry)) / (2 * ry) * 3.5 + hr(k, 1, 84) * 2
        ombra(cv, px + r * 0.5, py + r * 0.3, r * 1.1, r * 0.35, k=0.7)
        cv.disc(px, py - r * 0.3, r, r * 0.6, STONE, lambda nx, ny: 4.6 - ny * 1.6 - nx * 0.8, lit=0.4)


# Joncs de la vora de davant del toll: hi queden davant (i amb l'aigua, també: es tornen a pintar)
JONCS_DAVANT = ((404, 238, 9, 22, 11), (526, 236, 11, 26, 12), (566, 230, 6, 18, 13))


def joncs_davant(cv, verds=False):
    for (x, y, n, h, sd) in JONCS_DAVANT:
        if verds:
            mata_joncs(cv, x, y, n + 3, h * 1.25, sd + 10, caiguts=False, ramp=GREENL, lvl=3.6, escala=1.0)
        else:
            mata_joncs(cv, x, y, n, h, sd, caiguts=True, escala=1.0, lvl=3.0)


def _rierol_punts():
    """El llit del rierol, mostrejat (Catmull-Rom pels punts de RIEROL): [(x, y, mig ample)]."""
    P = [RIEROL[0]] + RIEROL + [RIEROL[-1]]
    out = []
    for i in range(1, len(P) - 2):
        p0, p1, p2, p3 = P[i - 1], P[i], P[i + 1], P[i + 2]
        n = int(math.hypot(p2[0] - p1[0], p2[1] - p1[1]) * 2) + 1
        for k in range(n):
            t = k / n
            t2, t3 = t * t, t * t * t
            c = [0.5 * (2 * p1[j] + (-p0[j] + p2[j]) * t + (2 * p0[j] - 5 * p1[j] + 4 * p2[j] - p3[j]) * t2 +
                        (-p0[j] + 3 * p1[j] - 3 * p2[j] + p3[j]) * t3) for j in range(3)]
            out.append(tuple(c))
    return out


def rierol_sec(cv):
    """El llit del rierol: pedres clares i fang esquerdat, amb el marge de l'esquerra a l'ombra (del turó al toll)."""
    for (x, y, w) in _rierol_punts():
        for k in range(-int(w) - 2, int(w) + 3):
            u = x + k
            nx = k / max(1.0, w)
            if abs(nx) > 1:
                lvl = 2.4 if nx < 0 else 4.2                                         # els marges
                cv.put(u, y, DRYG, lvl, lit=0.3)
                continue
            st = fbm(u / 2.5, y / 1.6, 17)
            lvl = 4.0 - abs(nx) * 0.4 + (st - 0.5) * 2.2 - (0.8 if nx < -0.5 else 0)
            cv.put(u, y, STONE if st > 0.48 else CLAY, lvl + 1.0, lit=0.3)
            if y < HOR + 6:
                boira_px(cv, u, y, BOIRA, 0.2)


# ─── L'arxiu ─────────────────────────────────────────────────────────────────

def _soca_w(y):
    cx, base, hw = SOCA
    return hw + 18 * max(0.0, (y - (base - 22)) / 22) ** 2 - 4 * max(0.0, (130 - y) / 30)


def _soca_top(x):
    cx = SOCA[0]
    return 104 + 14 * fbm(x / 7, 0.2, 51) + (10 if 222 <= x <= 240 else 0) - (8 if 250 <= x <= 262 else 0) \
        + abs(x - cx) * 0.12


def arxiu(cv):
    cx, base, hw = SOCA
    # l'ombra curta, sota (el sol és alt)
    ombra(cv, cx + 10, base + 2, hw + 20, 6, k=0.9)
    # el tronc
    for y in range(96, base + 3):
        w = _soca_w(y)
        for x in range(int(cx - w), int(cx + w) + 1):
            if y < _soca_top(x):
                continue
            u = (x - cx) / w
            fis = fbm(u * 8 + 3, y / 30, 41, 3)
            lvl = 3.8 - u * 1.4 - abs(u) ** 6 * 1.8 + (fis - 0.5) * 2.2 - (1.4 if fis < 0.36 else 0)
            if u > 0.2 and fbm(x / 8, y / 10, 44) > 0.72 - u * 0.06:
                cv.put(x, y, MOSS, lvl + 0.4, lit=0.6)
            else:
                cv.put(x, y, BARK, lvl, lit=0.6)
    # la boca de dalt (és buida): la vora de fusta clara i el forat fosc
    for x in range(int(cx - hw + 6), int(cx + hw - 5)):
        t = _soca_top(x)
        cv.put(x, t, PLANK, 6.0, lit=0.3)
        cv.put(x, t + 1, PLANK, 4.6, lit=0.3)
    # les arrels del peu
    for p1, p2, r0, s in (((cx - 70, base + 2), (cx - 92, base + 8), 7, 1), ((cx + 74, base), (cx + 96, base + 6), 6, 2),
                          ((cx - 30, base + 8), (cx - 40, base + 12), 5, 3), ((cx + 40, base + 6), (cx + 54, base + 10), 4, 4)):
        arrel(cv, (cx + (p2[0] - cx) * 0.4, base - 6), p1, p2, r0, 2, base=3.6, seed=s, lit=0.5)
    # la façana (els calaixets i la finestreta) es dibuixa plana i s'embolcalla a la soca, girada cap a l'esquerra
    # (cap al camí per on s'arriba): així es veu de tres quarts i no de cara. Els rètols són taulons clavats: no
    # s'arruguen, es tomben (la lletra no es remostreja, que es perdria: només es desplacen columnes senceres).
    fac = Canvas(W, H, light=LIGHT, transparent=True)
    calaixets(fac)
    finestreta(fac)
    impresos(fac)
    _embolcalla(cv, fac)
    rafec(cv)
    x0, y0, x1, _ = FINESTRA
    cartellet(cv, round(_a_pantalla((x0 + x1) // 2 + 2, y0)), y0)
    pla = Canvas(W, H, light=LIGHT, transparent=True)
    retols(pla)
    _tomba(cv, pla, SOCA[0] + 4, round(_a_pantalla(SOCA[0] + 4, 140)), 0.07)


# La façana: el seu mig (x = SOCA[0] al dibuix pla) mira cap a GIR (radiants; < 0, cap a l'esquerra). R_FAC és el
# radi amb què s'embolcalla (una mica més gran que el de la soca: la façana no s'arrugui tant a la vora).
GIR, R_FAC = -0.34, 74


def _a_pantalla(sx, y):
    """Un punt de la façana plana (x del dibuix, y) → la x de pantalla, embolcallat a la soca."""
    cx = SOCA[0]
    return cx + _soca_w(y) * math.sin(GIR + (sx - cx) / R_FAC)


def _embolcalla(cv, fac):
    """Copia la façana plana sobre el cilindre de la soca: cada píxel de pantalla busca el seu punt de la façana.
    La llum ve de dalt a l'esquerra: el que gira cap a la dreta s'enfosqueix."""
    cx, base, _ = SOCA
    F = fac.img.load()
    for y in range(96, base + 3):
        w = _soca_w(y)
        for x in range(int(cx - w), int(cx + w) + 1):
            u = (x - cx) / w
            if abs(u) >= 1:
                continue
            phi = math.asin(u)
            sx = cx + (phi - GIR) * R_FAC
            if not 0 <= sx < W - 1:
                continue
            c = F[int(sx), y]
            if not c[3]:
                continue
            k = 0.62 + 0.38 * max(0.0, math.cos(phi + 0.5)) - 0.25 * abs(u) ** 6
            cv.P[x, y] = (int(c[0] * k), int(c[1] * k), int(c[2] * k), 255)


def _tomba(cv, pla, sx0, x0, pend):
    """Un tauló pla (dibuixat a `pla` amb el mig a sx0) es posa amb el mig a x0 de pantalla i tombat: cada columna
    puja `pend` px per px cap a la dreta (el cantó que fuig, cap a l'horitzó)."""
    F = pla.img.load()
    for sx in range(W):
        x = sx - sx0 + x0
        dy = -round((x - x0) * pend)
        if not 0 <= x < W:
            continue
        for y in range(80, 230):
            c = F[sx, y]
            if c[3] and 0 <= y + dy < H:
                cv.P[x, y + dy] = c[:3] + (255,)


def _quad(cv, pts, ramp, lvl, lit=0.3):
    """Un quadrilàter ple (pts en ordre), amb lvl(x, y) o un nombre."""
    xs, ys = [p[0] for p in pts], [p[1] for p in pts]
    for y in range(int(min(ys)), int(max(ys)) + 1):
        for x in range(int(min(xs)), int(max(xs)) + 1):
            cr = [(bx - ax) * (y + 0.5 - ay) - (by - ay) * (x + 0.5 - ax)
                  for (ax, ay), (bx, by) in zip(pts, pts[1:] + pts[:1])]
            if all(c >= 0 for c in cr) or all(c <= 0 for c in cr):
                cv.put(x, y, ramp, lvl(x, y) if callable(lvl) else lvl, lit)


def rafec(cv):
    """Un ràfec de taulons damunt la finestreta, que surt de la soca cap a fora (cap a l'esquerra i cap aquí): se'n
    veu la cara de dalt, el cantell de davant i el costat de l'esquerra (la regla de les tres cares)."""
    x0, y0, x1, _ = FINESTRA
    yb = y0 - 9                                                        # on toca la soca
    a, b = (_a_pantalla(x0 - 8, yb), yb), (_a_pantalla(x1 + 8, yb), yb)
    out = (-9, 5)                                                      # cap a fora (la normal de la façana, en pantalla)
    c, d = (b[0] + out[0], b[1] + out[1]), (a[0] + out[0], a[1] + out[1])
    ombra(cv, (a[0] + b[0]) / 2 - 2, yb + 10, (b[0] - a[0]) / 2 + 2, 4, k=0.6)
    _quad(cv, [a, b, c, d], PLANK, lambda x, y: 5.6 - (1.2 if int(x - (y - yb) * out[0] / out[1]) % 8 == 0 else 0)
          + (fbm(x / 4, y, 70) - 0.5) * 0.8)                         # la cara de dalt, de taulons
    _quad(cv, [d, c, (c[0], c[1] + 3), (d[0], d[1] + 3)], PLANK, 3.0)  # el cantell de davant
    _quad(cv, [a, d, (d[0], d[1] + 3), (a[0], a[1] + 3)], PLANK, 3.8)  # el costat
    for t in (0.12, 0.88):                                             # els tornapuntes, de la soca al cantell
        px, py = d[0] + (c[0] - d[0]) * t, d[1] + (c[1] - d[1]) * t + 3
        qx, qy = a[0] + (b[0] - a[0]) * t, a[1] + 16
        for i in range(12):
            cv.put(px + (qx - px) * i / 11, py + (qy - py) * i / 11, PLANK, 2.4, lit=0.3)


def calaixets(cv):
    """Els calaixets, encastats a l'escorça de l'esquerra: fusta clara, poms de llautó i etiquetes."""
    x0, y0 = 181, 156
    for j in range(3):
        for i in range(3):
            x, y = x0 + i * 13 - j * 1, y0 + j * 11
            if j == 2 and i == 1:
                continue
            cv.rect(x - 1, y - 1, x + 11, y + 9, BARK, 1.0, lit=0)                  # el forat
            cv.rect(x, y, x + 10, y + 8, PLANK, lambda xx, yy: 4.6 - (yy - y) * 0.12 - (xx - x) * 0.04, lit=0.4)
            cv.rect(x + 2, y + 1, x + 8, y + 3, CREAM, 4.2, lit=0)                   # l'etiqueta
            cv.flat(x + 3 + (i + j) % 3, y + 2, (90, 80, 70))
            cv.put(x + 5, y + 6, BRASS, 4.6, lit=0)                                  # el pom
            cv.put(x + 5, y + 7, BRASS, 2.4, lit=0)
    # un calaix obert, ple de fitxes
    x, y = x0 + 13 - 2, y0 + 22
    cv.rect(x - 1, y - 1, x + 11, y + 9, BARK, 0.6, lit=0)
    cv.rect(x - 1, y + 4, x + 12, y + 11, PLANK, 5.0, lit=0.4)
    for k in range(5):
        cv.rect(x + 1 + k * 2, y + 1, x + 1 + k * 2, y + 5, CREAM, 4.6 - k % 2, lit=0)


def finestreta(cv):
    """La finestreta de taquilla, a l'alçada d'un gripau: el marc, l'interior fosc, el taulell i el cartellet VAGA."""
    x0, y0, x1, y1 = FINESTRA
    cv.rect(x0 - 3, y0 - 3, x1 + 3, y1 + 1, PLANK, lambda x, y: 4.2 - (0.8 if x in (x0 - 3, x1 + 3) else 0), lit=0.4)
    for y in range(y0, y1):
        for x in range(x0, x1 + 1):
            cv.put(x, y, BARK, 0.6 + (y - y0) / (y1 - y0) * 0.8 + (fbm(x / 3, y / 3, 61) - 0.5), lit=0)
    # un prestatge amb carpetes, a dins
    for k in range(6):
        cv.rect(x0 + 3 + k * 4, y0 + 5, x0 + 5 + k * 4, y0 + 12, [(60, 50, 30), (110, 90, 50), (160, 140, 90)],
                1 + k % 3, lit=0)
    # el taulell
    cv.rect(x0 - 6, y1, x1 + 6, y1 + 2, PLANK, 6.0, lit=0.3)
    cv.rect(x0 - 5, y1 + 3, x1 + 5, y1 + 4, PLANK, 2.6, lit=0.3)
    # el tampó, sec, i un timbre de taulell
    cv.rect(x1 - 4, y1 - 2, x1 + 1, y1 - 1, IRONK, 3.0, lit=0)
    cv.disc(x0 + 2, y1 - 2, 2, 1.4, BRASS, lambda nx, ny: 4.4 - ny * 1.4, lit=0)


def impresos(cv):
    """Impresos clavats a l'escorça, a la dreta de la finestreta (fan la volta a la soca): formularis amb ratlles i
    una caselleta, i un de grapat que fa punxa."""
    for k, (x, y, w, h) in enumerate(((266, 150, 12, 16), (281, 156, 11, 15), (295, 148, 11, 17), (272, 170, 10, 13))):
        cv.rect(x, y, x + w, y + h, CREAM, lambda xx, yy, x=x: 4.8 - (xx - x) * 0.05, lit=0.3)
        for j in range(y + 3, y + h - 2, 2):
            cv.rect(x + 2, j, x + w - 2 - (j * 7 + k) % 4, j, NOTE_INK, 0, lit=0)
        cv.rect(x + w - 4, y + h - 4, x + w - 2, y + h - 2, NOTE_INK, 0, lit=0)
        cv.flat(x + w // 2, y + 1, (120, 110, 100))                             # la xinxeta
        cv.darken(x + 1, y + h + 1, x + w + 1, y + h + 1, 0.5)


NOTE_INK = [(70, 62, 56)]


def cartellet(cv, cx, y0):
    """El cartellet «VAGA» de la finestreta, penjat d'un cordill (pla: no s'embolcalla)."""
    cv.line(cx - 6, y0 - 1, cx - 9, y0 + 4, IRONK, 3.0, lit=0)
    cv.line(cx + 6, y0 - 1, cx + 9, y0 + 4, IRONK, 3.0, lit=0)
    cv.rect(cx - 10, y0 + 4, cx + 10, y0 + 12, CREAM, 4.8, lit=0)
    lletres(cv, 'VAGA', cx - ample('VAGA') // 2, y0 + 6, (170, 30, 20))


def retols(cv):
    """«REGISTRE DEL BOSC» al tauló de dalt, i «HORARI: QUAN HI HA AIGUA» a la placa de sota (lletra fosca sobre clar)."""
    cx = SOCA[0] + 4
    s1 = 'REGISTRE DEL BOSC'
    w1 = ample(s1)
    x0, y0 = cx - w1 // 2 - 4, 120
    cv.rect(x0, y0, x0 + w1 + 8, y0 + 10, PLANK, lambda x, y: 5.4 - (y - y0) * 0.1 - (1.2 if y == y0 + 10 else 0), lit=0.3)
    lletres(cv, s1, x0 + 4, y0 + 3, (40, 24, 12))
    for x in (x0 + 2, x0 + w1 + 6):
        cv.flat(x, y0 + 2, (60, 50, 40))
    s2a, s2b = 'HORARI:', 'QUAN HI HA AIGUA'
    w2 = ample(s2b)
    x0, y0 = cx - w2 // 2 - 3, 134
    cv.rect(x0, y0, x0 + w2 + 6, y0 + 15, CREAM, lambda x, y: 5.0 - (0.8 if y == y0 + 15 else 0), lit=0.2)
    lletres(cv, s2a, x0 + 3 + (w2 - ample(s2a)) // 2, y0 + 2, (40, 30, 24))
    lletres(cv, s2b, x0 + 3, y0 + 8, (40, 30, 24))


# ─── Els gripaus de fons i la pancarta ──────────────────────────────────────

TOAD = [(20, 26, 10), (40, 50, 18), (66, 76, 28), (96, 104, 40), (130, 132, 58), (170, 166, 90)]


def gripau_fons(cv, x, y, text_, seed=1):
    """Un gripau vaguista de fons (sense id): assegut, amb un pal i una pancarta."""
    cv.disc(x, y - 6, 9, 6.5, TOAD, lambda nx, ny: 3.2 - ny * 1.4 - nx * 0.6 + (0.8 if fbm(nx * 4, ny * 4, seed) > 0.6 else 0),
            lit=0.4)
    cv.disc(x - 4, y - 12, 2.4, 2.2, TOAD, lambda nx, ny: 3.8 - ny, lit=0.4)               # els ulls
    cv.disc(x + 3, y - 12, 2.4, 2.2, TOAD, lambda nx, ny: 3.6 - ny, lit=0.4)
    cv.flat(x - 4, y - 12, (20, 14, 6))
    cv.flat(x + 3, y - 12, (20, 14, 6))
    cv.rect(x - 6, y - 7, x + 5, y - 7, TOAD, 1.0, lit=0)                                  # la boca, seriosa
    cv.disc(x - 8, y - 1, 4, 2, TOAD, 2.0, lit=0.4)                                        # les potes
    cv.disc(x + 8, y - 1, 4, 2, TOAD, 2.0, lit=0.4)
    ombra(cv, x + 2, y + 1, 11, 2)
    # la pancarta
    px = x + 9
    cv.rect(px, y - 34, px + 1, y - 3, PLANK, 4.0, lit=0.3)
    w = ample(text_) + 6
    cv.rect(px - w // 2, y - 42, px + w // 2, y - 32, CREAM, lambda xx, yy: 5.2 - (0.8 if yy == y - 32 else 0), lit=0.2)
    lletres(cv, text_, px - w // 2 + 3, y - 40, (150, 26, 18))


# ─── NaturaPlus: el tub i la comporta ────────────────────────────────────────

def tub(cv):
    """El tub d'aspersors: surt del rierol (just a sobre del tap) i se'n va cap a la dreta, a la tanca."""
    # de (574, 176) a la vora dreta, una mica amunt (fuig cap al fons)
    for x in range(570, W):
        t = (x - 570) / (W - 570)
        yc = 176 - t * 10
        r = 4.2 - t * 1.2
        for y in range(int(yc - r), int(yc + r) + 1):
            ny = (y - yc) / r
            cv.put(x, y, PLASTIC, 5.0 - ny * 1.8 - (1.4 if ny > 0.5 else 0) - (1.6 if int(x) % 22 == 0 else 0), lit=0.2)
    # la boca dins el rierol (on xucla l'aigua), amb una reixa
    cv.disc(571, 176, 3, 4.6, STEEL, lambda nx, ny: 2.0 + nx, lit=0)
    for y in range(173, 180, 2):
        cv.flat(571, y, (180, 186, 196))
    # la franja verda de NaturaPlus i la fulla
    for x in range(586, 600):
        cv.put(x, 176 - (x - 570) / 70 * 10 - 1, NEON, 3.6, lit=0)
    # el pal de la placa
    cv.rect(626, 136, 627, 172, STEEL, 4.0, lit=0)
    s1, s2 = 'ASPERSORS GESPA', 'SECTOR 4'
    w = ample(s1) + 6
    x0, y0 = W - w - 2, 132
    cv.rect(x0, y0, x0 + w, y0 + 16, PLASTIC, lambda x, y: 6.0 - (1.2 if y == y0 + 16 else 0), lit=0)
    cv.rect(x0, y0, x0 + w, y0 + 1, NEON, 3.6, lit=0)
    lletres(cv, s1, x0 + 3, y0 + 3, (30, 40, 50))
    lletres(cv, s2, x0 + 3 + (w - 6 - ample(s2)) // 2, y0 + 10, (30, 40, 50))
    cv.glow(x0 + w // 2, y0 + 8, 30, (220, 255, 230), 0.15)


def comporta(cv):
    """La comporta: una vàlvula de pas al tub, amb la roda vermella."""
    x, y = RODA
    cv.rect(x - 4, y + 2, x + 4, y + 8, STEEL, lambda xx, yy: 4.6 - (xx - x) * 0.2, lit=0.2)   # el cos
    cv.rect(x - 1, y - 3, x + 1, y + 2, STEEL, 5.0, lit=0)                                    # l'eix
    for a in range(0, 360, 6):                                                                # la roda
        r = math.radians(a)
        cv.put(x + math.cos(r) * 8, y - 4 + math.sin(r) * 3, REDL, 3.6 + math.sin(r) * 0.6, lit=0)
        cv.put(x + math.cos(r) * 8, y - 3 + math.sin(r) * 3, REDL, 2.4, lit=0)
    for a in (0, 60, 120):
        r = math.radians(a)
        cv.line(x - math.cos(r) * 8, y - 4 - math.sin(r) * 3, x + math.cos(r) * 8, y - 4 + math.sin(r) * 3, REDL, 3.2, lit=0)
    cv.disc(x, y - 4, 1.6, 1, STEEL, 5.4, lit=0)


def tap(cv):
    """El tap de plàstics: ampolles buides d'«Aire Pur» encallades entre les pedres del rierol."""
    x, y = TAP
    ampolles = [(-13, 3, 0.3), (-6, -1, -0.25), (2, 3, 0.1), (9, -1, 0.5), (14, 4, -0.3), (-2, -6, 0.9),
                (6, -7, -0.6), (-10, -5, 1.4), (15, -4, 1.1), (1, -11, 0.2)]
    cv.disc(x, y + 3, 19, 5, STONE, lambda nx, ny: 2.6 - ny * 0.8, lit=0.2)                  # pedres i fang
    for dx, dy, a in ampolles:
        bx, by = x + dx, y + dy
        c, s_ = math.cos(a), math.sin(a)

        def P(k, j):
            return bx + c * k - s_ * j, by + s_ * k + c * j
        for k in range(-7, 8):                                                               # el contorn
            for j in (-3, 3):
                cv.put(*P(k, j * 0.8), STEEL, 2.0, lit=0)
        for k in range(-7, 8):
            jj = 2.2 if k < 4 else 1.2                                                       # el coll, més prim
            for j in (-jj, -jj / 2, 0, jj / 2, jj):
                lvl = 5.2 - j * 0.6 + (1.0 if abs(j) < 0.3 else 0) - (1.4 if k in (-3, 3) else 0)
                if -2 <= k <= 1:
                    cv.put(*P(k, j), NEON, 3.4 - j * 0.3, lit=0)                              # l'etiqueta verda
                else:
                    cv.put(*P(k, j), PLASTIC, lvl, lit=0.1)
        cv.put(*P(8, 0), NEON, 4.6, lit=0)                                                   # el tap verd
        cv.put(*P(8, 1), NEON, 3.6, lit=0)
    # la pedra que encalla la de sota
    cv.disc(x + 5, y + 6, 7, 3.4, STONE, lambda nx, ny: 4.4 - ny * 1.6 - nx * 0.6, lit=0.2)
    cv.glow(x - 4, y - 6, 16, (255, 255, 255), 0.2)


# ─── El primer pla ───────────────────────────────────────────────────────────

def primer_pla(cv):
    """Les cantonades de baix, molt a prop i a l'ombra (en silueta, amb la vora de dalt tocada pel sol): emmarquen el
    quadre com al campament de les fades."""
    # a l'esquerra: el tronc caigut, falgueres grosses i joncs foscos
    arrel(cv, (-20, 252), (40, 246), (110, 264), 11, 8, ramp=BARK, base=1.4, seed=71, moss=True, lit=0)
    for i, (x, y, a, l, sd) in enumerate(((-14, 272, 1.15, 150, -1), (2, 272, 0.7, 160, -1), (26, 272, 1.45, 120, 1),
                                          (-16, 230, 0.35, 110, -1), (58, 272, 1.95, 84, 1), (14, 272, 1.7, 136, 1),
                                          (40, 272, 1.25, 104, -1))):
        falguera(cv, x, y, a, l, side=sd, ramp=FERN, lvl=1.5 + i * 0.08, rim=1, seed=i)
    for i, x in enumerate(range(44, 90, 5)):
        jonc(cv, x, 264, 50 + (i * 13) % 34, (0.35 if i % 2 else -0.2) * (1 + i % 3 * 0.4), FERN, 2.0, gruix=2, lit=0)
    # a la dreta: la pedra, falgueres i una mata alta de boga (amb la panotxa)
    cv.disc(616, 258, 34, 14, STONE, lambda nx, ny: 2.2 - ny * 1.2 - nx * 0.6 + (fbm(nx * 4, ny * 4, 3) - 0.5) * 1.4, lit=0)
    for i, (x, y, a, l, sd) in enumerate(((604, 272, 1.95, 140, 1), (632, 272, 2.35, 156, 1), (652, 240, 2.75, 120, 1),
                                          (586, 272, 1.6, 96, -1), (620, 272, 1.75, 120, 1))):
        falguera(cv, x, y, a, l, side=sd, ramp=FERN, lvl=1.7, rim=-1, seed=20 + i)
    for i, x in enumerate(range(556, 646, 4)):
        jonc(cv, x, 264, 60 + (i * 11) % 46, (-0.5 if i % 2 else 0.25) * (1 + i % 3 * 0.3), FERN, 2.0, gruix=2, lit=0,
             cap=i % 3 == 0)


# ─── Composició ─────────────────────────────────────────────────────────────

IRI = (150, 236)                                   # (fora de les falgueres del primer pla)
# Les mates de joncs del toll: x, y del peu, quants, alçada, llavor
JONCS = ((376, 208, 18, 34, 1), (404, 205, 14, 30, 2), (430, 204, 8, 22, 7), (536, 210, 16, 30, 3),
         (556, 217, 8, 20, 4), (356, 218, 9, 24, 5), (480, 205, 7, 18, 6))
BUFO = (round(_a_pantalla(237, 192)), 211)                  # davant la finestreta (girada amb la façana)
GRIPAU = (322, 216)


@functools.lru_cache(maxsize=None)
def _base(sense_mata=None):
    """→ (la sala, el primer pla). `sense_mata`: l'índex d'una mata de JONCS que no es pinta (per a la màscara de la
    seva capa del davant: el que canvia sense ella)."""
    cv = Canvas(W, H, light=LIGHT)
    cel(cv)
    bosc_fons(cv)
    tanca_fons(cv)
    turo(cv)
    terra(cv)
    bosc_esquerra(cv)
    rierol_sec(cv)
    toll_sec(cv)
    # els joncs del toll (secs i caiguts), del fons a prop
    for i, (x, y, n, h, s) in enumerate(JONCS):
        if i != sense_mata:
            mata_joncs(cv, x, y, n, h, s, caiguts=True, escala=1.0, lvl=4.0)
    joncs_davant(cv)
    tub(cv)
    comporta(cv)
    arxiu(cv)
    gripau_fons(cv, 352, 206, 'VAGA!', 3)
    # sota la sala, negre
    for y in range(RH, H):
        for x in range(W):
            cv.flat(x, y, (0, 0, 0))
    # el primer pla, en una capa a part (per a la màscara del FRONT)
    pp = Canvas(W, H, light=LIGHT, transparent=True)
    primer_pla(pp)
    for y in range(RH, H):
        for x in range(W):
            pp.P[x, y] = (0, 0, 0, 0)
    cv.img.alpha_composite(pp.img)
    return cv.img, pp.img


def bg(cv):
    img, _ = _base()
    cv.img.paste(img)
    cv.P = cv.img.load()


# ─── Props i decorats ────────────────────────────────────────────────────────

def _aigua(cv):
    """El toll ple (amb el cel reflectit), el rierol que corre fins al toll i els joncs redreçats i verds."""
    cx, cy, rx, ry = TOLL
    for v in range(int(cy - ry - 2), int(cy + ry + 3)):
        for u in range(int(cx - rx - 2), int(cx + rx + 3)):
            d = _toll_d(u, v)
            if d > 1.02:
                continue
            x, z = T.mon(u, v)
            ny = (v - cy) / ry
            lvl = 4.6 - ny * 1.6 + (fbm(x / 30, z / 8, 77) - 0.5) * 1.4
            if fbm(x / 12, z / 4, 78) > 0.66:
                lvl += 1.6                                                            # reflexos del cel
            if d > 0.93:
                lvl = 2.4 if ny < 0 else 5.6                                           # la vora mullada
            cv.put(u, v, WATER, lvl, lit=0)
    cv.glow(cx - 30, cy - 4, 40, (250, 255, 255), 0.25)
    # el rierol, ple: aigua que baixa pel llit
    for (x, y, w) in _rierol_punts():
        w *= 0.7
        if True:
            for k in range(int(-w), int(w) + 1):
                lvl = 4.2 - abs(k) / max(1, w) * 1.0 + (1.8 if hr(int(x + k), int(y), 5) > 0.8 else 0)
                cv.put(x + k, y, WATER, lvl, lit=0)
    # els joncs, drets i verds
    for (x, y, n, h, s) in JONCS:
        cv.disc(x, y, 11, 3, MOSS, 2.2, lit=0.4)
        mata_joncs(cv, x, y, n + 4, h * 1.25, s + 10, caiguts=False, ramp=GREENL, lvl=4.4, escala=1.0)
    joncs_davant(cv, verds=True)


def _tap(cv):
    tap(cv)


PROPS = {'tap_plastics': _tap, 'aigua': _aigua}


# ─── Animacions ──────────────────────────────────────────────────────────────

def _frames_libellules():
    """Tres libèl·lules que volen en vuits sobre el toll (el cos blau, les ales que llampurnegen)."""
    n = 32
    out = []
    vols = [((440, 186), 46, 10, 0.0, (40, 120, 210)), ((500, 194), 30, 7, 2.1, (30, 170, 160)),
            ((410, 178), 24, 6, 4.0, (200, 70, 40))]
    for i in range(n):
        cv = Canvas(W, H, transparent=True)
        for (cx, cy), ax, ay, ph, col in vols:
            t = i / n * 2 * math.pi + ph
            x = cx + ax * math.sin(t)
            y = cy + ay * math.sin(2 * t) + 2 * math.sin(i * 1.7 + ph)
            dx = math.cos(t)                                                           # cap on va
            d = 1 if dx >= 0 else -1
            for k in range(-3, 4):
                cv.flat(x + k * d, y, col if k < 2 else tuple(min(255, c + 60) for c in col))
            wing = (230, 240, 250) if i % 2 else (190, 205, 220)
            cv.flat(x, y - 1, wing)
            cv.flat(x - d, y - 1, wing)
            cv.flat(x + d * 0, y - 2 if i % 2 else y + 1, wing)
            cv.flat(x - d, y - 2 if i % 2 else y + 1, wing)
        out.append(cv.img)
    return out


def _frames_calor():
    """L'aire que tremola a l'horitzó (només el bosc del fons, a l'esquerra del turó)."""
    base, _ = _base()
    src = base.load()
    out = []
    y0, y1, x1 = HOR - 30, HOR + 4, 384
    for i in range(8):
        fr = base.copy()
        P = fr.load()
        for y in range(y0, y1):
            s = round(math.sin(y * 0.9 + i * math.pi / 4) * 0.8 + math.sin(y * 0.37 - i * math.pi / 2) * 0.5)
            if s == 0:
                continue
            for x in range(150, x1):
                P[x, y] = src[min(x1, max(0, x + s)), y]
        out.append(diferencia(fr, base))
    return out


ANIMS = {'libellules': {'frames': _frames_libellules, 'frameDuration': 70},
         'calor': {'frames': _frames_calor, 'frameDuration': 140}}

# La mata de joncs de l'esquerra del toll (JONCS[5]) és dins el terra on es camina: qui va pel darrere del toll hi
# passa per darrere (les cames tapades), i qui va pel davant, per davant. La màscara: el que canvia sense la mata (el
# gripau de fons, que hi ha a sobre, no hi entra). Amb l'aigua, la mata és verda i dreta: la variant `aigua`.
MATA_DAVANT = 5


@functools.lru_cache(maxsize=None)
def _mask_mata():
    import numpy as np
    a = np.asarray(_base()[0].convert('RGB'))
    b = np.asarray(_base(MATA_DAVANT)[0].convert('RGB'))
    m = (a != b).any(axis=2)
    return lambda x, y: bool(m[y, x])


FRONT = [{'id': 'davant_joncs', 'mask': lambda x, y: _mask_mata()(x, y), 'baseline': JONCS[MATA_DAVANT][1],
          'zIndex': 20, 'variants': ('aigua',)},
         {'id': 'davant', 'mask': lambda x, y: mascara(_base()[1])(x, y), 'baseline': 999, 'zIndex': 22}]


# ─── Geometria ───────────────────────────────────────────────────────────────

def _el(cx, cy, rx, ry, n=12):
    return [(round(cx + rx * math.cos(2 * math.pi * i / n)), round(cy + ry * math.sin(2 * math.pi * i / n)))
            for i in range(n)]


_V_FONS, _V_PROP = 208, 256
# Els fulls dels personatges fan l'Iri de 68 px a escala 1 (la sala es va dibuixar pensant en 97): ×97/68.
K_FULLS = 97 / 68
ESCALA = (round(0.58 * K_FULLS, 3), round(0.77 * K_FULLS, 3))                              # a y = 198 i a y = 259

GEOMETRIA = {
    'things': {
        'arxiu': {'rect': (176, 100, 300, 206), 'walk': (200, 224)},
        'toll': {'rect': (362, 204, 562, 236), 'walk': (440, 242)},
        'joncs': {'rect': (364, 180, 432, 210), 'walk': (380, 238)},
        'rierol': {'rect': (500, 60, 584, 172), 'walk': (548, 226)},
        'tap_plastics': {'rect': (546, 174, 590, 198), 'walk': (566, 222)},
        'comporta': {'rect': (592, 128, 639, 186), 'walk': (602, 226)},
        'cami': {'rect': (0, 196, 34, 258), 'walk': (14, 240)},
    },
    'spawns': {'iri': IRI, 'bufo': BUFO, 'gripau': GRIPAU},
    'walkable': [(0, 226), (60, 220), (150, 210), (300, 208), (380, 212), (540, 212), (639, 214), (639, 256),
                 (0, 256)],
    'forats': [_el(TOLL[0], TOLL[1] + 1, TOLL[2] - 4, TOLL[3] - 3),
               _el(JONCS[MATA_DAVANT][0], JONCS[MATA_DAVANT][1] + 1, 9, 3, n=8)],
    # El sol és alt i una mica a l'esquerra: l'ombra, curta, cau cap a la dreta i endavant.
    'floorSquash': 0.25,
    'characterShadow': {'enabled': True, 'color': '#3a2a12', 'alpha': 0.42, 'squash': 0.28, 'core': 0.6,
                        'light': {'x': 0.5, 'y': 0.25, 'direction': True, 'stretch': 0.25}},
    # La llum de la sala sobre els personatges: el migdia (l'ambient, clar i una mica groc de calitja), el sol alt
    # a l'esquerra, blanc, i l'ombra del bosc de l'esquerra (un ambient més fosc no es pot fer per zones: el sol
    # hi arriba menys). Amb l'aigua, el reflex fresc del toll, de baix.
    'characterLights': {
        'ambient': '#d6cdb6',
        'lights': [{'x': SOL[0] + 120, 'y': SOL[1], 'radius': 420, 'color': '#fff2d6', 'intensity': 0.3},
                   {'x': TOLL[0], 'y': TOLL[1] + 6, 'radius': 130, 'color': '#a8e0ec', 'intensity': 0.3,
                    'whenPropVisible': 'aigua'}],
    },
    # A escala 1 l'Iri fa ≈97 px: aquí, de lluny, ≈0,6 al fons (58 px, al peu de l'arxiu) i ≈0,77 a baix de tot.
    # (No és l'escala exacta de l'horitzó, que encongiria massa el fons: el terra s'ha dibuixat a l'ull.)
    'regions': [{'id': 'perspectiva', 'active': True, 'scaleEnabled': True, 'scaleWalkSpeed': True,
                 'scaleTop': ESCALA[0], 'scaleBottom': ESCALA[1],
                 'points': [(0, _V_FONS - 10), (W - 1, _V_FONS - 10), (W - 1, RH - 1), (0, RH - 1)]}],
}
