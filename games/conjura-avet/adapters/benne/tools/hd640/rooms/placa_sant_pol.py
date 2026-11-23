"""
La Conjura de l'Avet — `placa_sant_pol`: la plaça de Sant Pol (actes 1 i 4; les dues germanes). EN 3D
(hd640/tres_d.py), a 1×, sala ampla (960 px) que la càmera recorre.

Migdia, ha parat de ploure: cel trencat, blau net entre núvols, el terra de la plaça moll i amb bassals que fan de
mirall. La càmera és de lluny, a l'altura d'un primer pis, i mira la plaça de cara (`pitch` 0: les verticals,
verticals). D'esquerra a dreta (la referència `sant-pol-sense-parets.png`):
  - la **façana** de Sant Pol, girada cap a l'esquerra, amb la **portada** (dues arquivoltes, columnes i el timpà)
    i, a la **llinda**, «BERNARDUS / COMES FECIT» en lletres grosses; la porta de fusta fosca; la finestreta del
    capcer; el gruix del mur, assolellat, a la dreta;
  - el **campanar** octogonal, a la cantonada de la nau: la porteta de baix i, a dalt, la **finestra** amb la
    **campana** (de bronze) penjada del jou; la torre surt del quadre per dalt;
  - la **nau** sense parets: la plataforma de pedra amb la **gespa** a dins, els murs esbotzats arran de terra i, al
    fons, l'absis esmotxat; un arbre gran darrere;
  - la **creu de terme** al mig de la plaça (s'hi passa per darrere i per davant);
  - la **casa del batlle**, de pedra, amb el portal adovellat, la finestra amb porticons i la **reixa** del celler
    arran de terra; a la dreta, el **carrer** que puja cap a l'avet (que treu el cap per damunt de les teulades).
  - Primer pla: pedres, herba molla i un bassal, a les cantonades de baix (`FRONT`).

PROPS: `queixa` (el pergamí clavat a la porta, amb el segell de cera vermella), `dones` (les dones que filen a la
gespa), `corda_campana` (la corda de cànem que penja de la finestra del campanar fins a terra), `llum_mati` (l'acte
4: el sol net del matí, tota la sala), `dones_marxen` (les dones ja no hi són: les cadiretes i els cistells buits).
ANIMS: `campana_toca` (la campana que es gronxa; és el decorat del mateix nom).

El món: x a la dreta, y amunt (0 = el terra de la plaça), z cap al fons; 1 unitat = 1 px de sala on un personatge fa
la seva mida (l'Iri, 84 px).
"""
import functools
import math

import numpy as np
from PIL import Image

import hd640  # noqa: F401  (abans de cap hd.rooms: posa la llibreria a 640×360)
from hd.pix import Canvas, Light, W, hr
from hd640.font import GLYPHS
from hd640.tres_d import Camera, Escena, Llum
from hd640.rooms.placa_pont_comu import (BOTTOM, PEDRA, TOSCA, TEULA, FUSTA, FERRO, GESPA, TERRA, NUVOL, LLUNY,
                                         PAPER, CERA, FULLA, BRONZE, CANEM, PELL, LLANA, ROBA_BLAVA, ROBA_OCRE,
                                         ROBA_VERDA, ESCORÇA, CEL, CEL_MATI, _diff, fbm, fbm_np, tramat, enganxa,
                                         nivells_carreus, nivells_paredat, lvl_carreus, lvl_paredat, cel_trencat,
                                         silueta_muntanyes, capcada)

ROOM_W = 960
CAM = Camera(pos=(480, 150, -460), yaw=0.0, pitch=0.0, f=480, centre=(480, 90))
LIGHT = Light(ambient=0.0, vignette=None, floor_fade=None)   # (la llum és la del món: la de l'Escena)


def _add(a, b, k=1.0):
    return (a[0] + b[0] * k, a[1] + b[1] * k, a[2] + b[2] * k)


def _y(P, y):
    return (P[0], y, P[2])


# ─── El món ──────────────────────────────────────────────────────────────────
FI = math.radians(18)                              # la façana, girada cap a l'esquerra
EF = (math.cos(FI), 0.0, -math.sin(FI))            # al llarg de la façana (d'esquerra a dreta)
NB = (math.sin(FI), 0.0, math.cos(FI))             # cap endins (el gruix del mur)
K = (250.0, 0.0, 120.0)                            # la cantonada de davant a la dreta de la façana
WF, HE, HP, GRUIX = 330, 200, 262, 36              # ample, ràfec, capcer, gruix
L = _add(K, EF, -WF)
PC = 150                                           # el mig de la portada (s des de L)
DOOR = (46, 96)                                    # la porta: mig ample, alt
LLINDA = (74, 96, 128)                             # la llinda: mig ample, y de baix, y de dalt
ARQ = (74, 84, 94)                                 # els radis de la portada (timpà, arquivolta 1, 2)
FIN = (165, 226, 252, 6)                           # la finestreta del capcer: s, y0, y1, mig ample

FN = math.radians(55)                              # la nau, cap al fons a la dreta
DN = (math.sin(FN), 0.0, math.cos(FN))
EN = (math.cos(FN), 0.0, -math.sin(FN))
NAU_A = _add(K, NB, GRUIX)                         # la cantonada de davant a la dreta de la nau
NL, NW, NH = 560, 300, 16                          # llarg, ample, alt de la plataforma
NAU_B = _add(NAU_A, DN, NL)
NAU_C = _add(NAU_B, EN, -NW)
NAU_D = _add(NAU_A, EN, -NW)
GRAONS = 280                                       # els graons per pujar a la nau (s des de NAU_A)

TORRE = _add(_add(NAU_A, DN, 112), EN, 54)         # el centre del campanar (a la plaça, arran de la nau)
TR, TH = 50, 360                                   # radi (als vèrtexs) i alçada del campanar
CAMPANA_Y = 222                                    # on penja la campana (el jou)
TFIN = (196, 258, 15)                              # la finestra del campanar: y0, y1 (amb l'arc), mig ample

CASA = (700, 925, 232, 450, 228, 292)              # la casa del batlle: x0, x1, z0, z1, ràfec, carener
REIXA = (16, 70, 3, 26)                            # la reixa del celler, a la façana de la casa: s0, s1, y0, y1
CASA2 = (925, 1500, 262, 640, 214)                 # la casa del costat, amb la volta per on passa el carrer
VOLTA = (1128, 1206, 128)                          # la volta del carrer: x0, x1, alt
CREU = (606, 92)                                   # la creu de terme (x, z)
AVET = (995, 1350)                                 # l'avet, al capdamunt del carrer (x, z)
ARBRE = (560, 820)                                 # l'arbre de darrere la nau


def _orient_torre():
    """L'angle de la cara del campanar que mira la càmera."""
    return math.atan2(CAM.pos[2] - TORRE[2], CAM.pos[0] - TORRE[0])


TANG = _orient_torre()


def torre_cara(k):
    """Els dos vèrtexs (a terra) de la cara k del campanar: la 0 mira la càmera, l'1 és la de la seva dreta."""
    a0 = TANG + (k - 0.5) * math.pi / 4
    a1 = TANG + (k + 0.5) * math.pi / 4
    return ((TORRE[0] + TR * math.cos(a1), 0.0, TORRE[2] + TR * math.sin(a1)),
            (TORRE[0] + TR * math.cos(a0), 0.0, TORRE[2] + TR * math.sin(a0)))


TCARA = 2 * TR * math.sin(math.pi / 8)             # l'ample de cada cara


# ─── La llum ─────────────────────────────────────────────────────────────────

def llums(mati=False):
    if mati:                                       # el sol del matí, baix i a l'esquerra (ve de llevant)
        return [Llum((-6000, 2600, -1200), 1e7, 2.4, power=0.0)], -0.5
    # migdia després de la pluja: el sol, alt, a l'esquerra i una mica de cara; el cel blanc que ho omple tot
    return [Llum((-3200, 5200, -2400), 1e7, 1.9, power=0.0), Llum((480, 3000, 600), 1e7, 0.5, power=0.0)], -0.7


def _sol_dir(mati=False):
    """La direcció cap al sol (per a les ombres al terra)."""
    P = llums(mati)[0][0].pos
    n = math.sqrt(P[0] ** 2 + P[1] ** 2 + P[2] ** 2)
    return (P[0] / n, P[1] / n, P[2] / n)


def _ombra_terra(P, sd):
    """On cau a terra l'ombra del punt P amb el sol a la direcció sd."""
    k = P[1] / sd[1]
    return (P[0] - sd[0] * k, 0.0, P[2] - sd[2] * k)


# ─── Textures (dibuixos plans; 1 unitat del món = TS píxels de textura) ───────
TS = 2


def _glif(ch):
    rows = GLYPHS[ch]
    return rows, len(rows[0])


def _text(lv, s, x, y, px, val, ombra=None, py=None):
    """Lletres gravades (de la font del joc) a la graella de nivells, cada píxel de la lletra = px × py (més
    amples que altes: l'escorç de la façana les aprima)."""
    py = px if py is None else py
    cx = x
    for ch in s:
        if ch == ' ':
            cx += 3 * px
            continue
        rows, w = _glif(ch)
        for j, row in enumerate(rows):
            for i, c in enumerate(row):
                if c == '#':
                    y0, x0 = int(round(y + j * py)), int(round(cx + i * px))
                    y1, x1 = int(round(y + (j + 1) * py)), int(round(cx + (i + 1) * px))
                    if ombra is not None:
                        lv[y1:y1 + 1, x0:x1] = np.maximum(lv[y1:y1 + 1, x0:x1], ombra)
                    lv[y0:y1, x0:x1] = val
        cx += (w + 1) * px


def _text_w(s, px):
    return sum((3 if c == ' ' else len(GLYPHS[c][0]) + 1) for c in s) * px - px


@functools.lru_cache(maxsize=None)
def tex_facana():
    """La façana de cara: carreus grisos i daurats, la portada, la llinda amb la inscripció, la porta i la
    finestreta. → imatge RGBA (WF·TS × HP·TS); a dalt, transparent fora del capcer."""
    w, h = WF * TS, HP * TS
    lv, _ = nivells_carreus(w, h, 5.2, fila=(24, 34), ample=(40, 76), seed=11, relleu=0.7, gra=0.8)
    yy, xx = np.mgrid[0:h, 0:w].astype(np.float32)
    s = xx / TS                                    # (unitats del món, d'esquerra a dreta)
    y = HP - yy / TS                               # (alçada al món)
    cx = PC
    # la portada: les arquivoltes (dovelles), de fora a dins, cada una un graó més endins i més fosca
    r = np.hypot(s - cx, y - LLINDA[2])
    ang = np.arctan2(y - LLINDA[2], s - cx)
    for k, (r0, r1) in enumerate(((ARQ[2] - 10, ARQ[2]), (ARQ[1] - 10, ARQ[1]))):
        dovella = np.floor(ang / (math.pi / (13 + k * 3)))
        m = (r >= r0) & (r < r1) & (y >= LLINDA[2])
        tone = 5.4 - k * 0.6 + (np.vectorize(lambda d: hr(int(d), k, 3))(dovella) - 0.5) * 0.8
        val = tone + np.where(r > r1 - 1.6, 0.9, 0) - np.where(r < r0 + 1.6, 1.2, 0)
        val = val - np.where(np.abs(ang - dovella * (math.pi / (13 + k * 3))) < 0.012 * (60 / r1) * 2, 1.4, 0)
        lv[m] = val[m]
        # els brancals (sota l'arrencada): columnes, amb el capitell
        mb = (np.abs(s - cx) >= r0) & (np.abs(s - cx) < r1) & (y < LLINDA[2]) & (y >= 4)
        col = 5.2 - k * 0.7 + np.cos((np.abs(s - cx) - (r0 + r1) / 2) / ((r1 - r0) / 2) * 1.4) * 0.9
        col = np.where((y > LLINDA[2] - 9) & (y < LLINDA[2]), 6.0 - k * 0.5 + ((yy // 3) % 2) * 0.6, col)
        col = np.where(y < 12, 4.6 - k * 0.5, col)
        lv[mb] = col[mb]
    # el timpà (llis, una mica endins) i la llinda
    mt = (r < ARQ[0]) & (y >= LLINDA[2])
    lv[mt] = (4.4 + (fbm_np(w, h, 14, 21, 3) - 0.5) * 1.2)[mt]
    lv[(r >= ARQ[0] - 1.5) & (r < ARQ[0]) & (y >= LLINDA[2])] = 3.2
    ml = (np.abs(s - cx) < LLINDA[0]) & (y >= LLINDA[1]) & (y < LLINDA[2])
    lv[ml] = (6.4 + (fbm_np(w, h, 8, 22, 3) - 0.5) * 0.9)[ml]
    lv[ml & (y >= LLINDA[2] - 1.2)] = 7.2
    lv[ml & (y < LLINDA[1] + 1.5)] = 3.4
    # la inscripció: dues ratlles, lletra gravada (fosca, amb la vora de baix clara)
    px, py = 1.85 * TS, 1.5 * TS
    for i, txt in enumerate(('BERNARDUS', 'COMES FECIT')):
        tw = _text_w(txt, px)
        ty = (HP - LLINDA[2] + 2.5) * TS + i * 15.5 * TS
        _text(lv, txt, (cx * TS) - tw / 2, ty, px, 1.4, ombra=7.6, py=py)
    # els brancals de dins (de la porta a la llinda) i la porta
    mj = (np.abs(s - cx) >= DOOR[0]) & (np.abs(s - cx) < LLINDA[0] - 0) & (y < LLINDA[1]) & (y >= 4) & \
         (np.abs(s - cx) < ARQ[0])
    lv[mj] = (4.6 - (np.abs(s - cx) - DOOR[0]) * 0.03 + ((yy // (14 * TS)) % 2) * 0.5)[mj]
    lv[(np.abs(s - cx) >= DOOR[0]) & (np.abs(s - cx) < DOOR[0] + 1.5) & (y < LLINDA[1])] = 2.6
    alpha = np.ones((h, w), bool)
    img = tramat(lv, PEDRA)
    # la porta: dues fulles de taulons de fusta fosca, amb les frontisses i els claus de ferro
    md = (np.abs(s - cx) < DOOR[0]) & (y < LLINDA[1]) & (y >= 4)
    dl = 4.2 + np.where(((s - cx + DOOR[0]) % 10) < 1.2, -1.6, 0) + (fbm_np(w, h, 6, 31, 3) - 0.5) * 1.4
    dl -= np.where(np.abs(s - cx) < 0.8, 2.0, 0)
    dl -= (y < 30) * 0.4
    fusta = tramat(dl, FUSTA)
    enganxa(img, fusta, md)
    ferro = np.zeros((h, w), bool)
    for fy in (18, 52, 82):
        ferro |= md & (np.abs(y - fy) < 2.2) & (np.abs(s - cx) > 3) & (np.abs(s - cx) < DOOR[0] - 4)
    for fy in (18, 52, 82):
        for fx in range(-DOOR[0] + 6, DOOR[0] - 4, 8):
            ferro |= (np.hypot(s - cx - fx, y - fy) < 1.3)
    ferro |= md & (np.hypot(s - cx - 4, y - 50) < 2.4)         # l'anella
    ferro &= md
    enganxa(img, tramat(np.where(np.hypot(s - cx - 4, y - 50) < 2.4, 3.4, 2.4) + (yy % 3 == 0) * 0.6, FERRO), ferro)
    # el graó de pedra
    mg = (np.abs(s - cx) < LLINDA[0] + 4) & (y < 4)
    enganxa(img, tramat(np.full((h, w), 6.4) - (y < 1.5) * 1.6, PEDRA), mg)
    # la finestreta del capcer: una espitllera amb l'arc, fosca i fonda
    fs, fy0, fy1, fw = FIN
    mf = (np.abs(s - fs) < fw) & (y >= fy0) & ((y < fy1 - fw) | (np.hypot(s - fs, y - (fy1 - fw)) < fw))
    mfv = (np.abs(s - fs) < fw + 5) & (y >= fy0 - 5) & ((y < fy1 - fw) | (np.hypot(s - fs, y - (fy1 - fw)) < fw + 5))
    enganxa(img, tramat(np.full((h, w), 6.0) - (np.abs(s - fs) > fw + 3) * 0.8, PEDRA), mfv & ~mf)
    enganxa(img, tramat(0.6 + (y - fy0) / (fy1 - fy0) * 0.8, PEDRA), mf)
    # el capcer: la cornisa de les dues aigües, i fora, res
    dist_capcer = (HP - y) - (HP - HE) * np.abs(s - WF / 2) / (WF / 2)
    alpha &= dist_capcer >= 0
    mc = (dist_capcer >= 0) & (dist_capcer < 7)
    enganxa(img, tramat(6.8 - dist_capcer * 0.35 + (np.floor(s / 9) % 2) * 0.4, PEDRA), mc)
    img[..., 3] = np.where(alpha, img[..., 3], 0)
    # la vora de baix, bruta de fang i d'humitat
    hum = (y < 26) & alpha
    img[hum, :3] = (img[hum, :3] * (0.72 + 0.28 * np.clip(y[hum] / 26, 0, 1))[:, None]).astype(np.uint8)
    return Image.fromarray(img, 'RGBA')


@functools.lru_cache(maxsize=None)
def tex_queixa():
    """La queixa: un pergamí clavat a la fulla dreta de la porta, amb el segell de cera vermella. Transparent a la
    resta (es projecta per la façana amb `Escena.capa`)."""
    w, h = WF * TS, HP * TS
    yy, xx = np.mgrid[0:h, 0:w].astype(np.float32)
    s, y = xx / TS, HP - yy / TS
    x0, x1, y0, y1 = PC + 8, PC + 33, 36, 74
    ondula = np.sin(y * 0.4) * 0.6
    m = (s >= x0 + ondula) & (s < x1 + ondula * 0.5) & (y >= y0 + np.sin(s * 0.5) * 0.8) & (y < y1)
    lv = 4.6 + (fbm_np(w, h, 5, 41, 3) - 0.5) * 1.4 - (s - x0) * 0.02
    lv -= ((np.floor((y1 - y) / 3.2) % 1 == 0) & (((y1 - y) % 3.2) < 0.9) & (s > x0 + 3) & (s < x1 - 3) &
           (y > y0 + 9) & (y < y1 - 4)) * 1.8                  # les ratlles d'escriptura
    lv += (y > y1 - 2.4) * 0.7
    img = tramat(lv, PAPER, m)
    # l'ombra del pergamí damunt la porta
    mo = (s >= x0 + 1.5) & (s < x1 + 2) & (y >= y0 - 2) & (y < y1 - 1) & ~m
    img[mo] = (12, 8, 6, 150)
    # el segell de cera, penjat d'una cinta, i el clau de dalt
    cxs, cys = (x0 + x1) / 2, y0 + 1
    mc = np.hypot(s - cxs, (y - cys) * 1.1) < 5.2
    seg = 3.4 + (-(s - cxs) * 0.22 + (y - cys) * 0.25) - (np.hypot(s - cxs, y - cys) < 2.4) * 0.8
    enganxa(img, tramat(seg, CERA), mc)
    mcin = (np.abs(s - cxs) < 1.0) & (y >= cys + 4) & (y < y0 + 6)
    enganxa(img, tramat(np.full((h, w), 2.4), CANEM), mcin)
    mclau = np.hypot(s - cxs, y - (y1 - 2.5)) < 1.6
    enganxa(img, tramat(np.full((h, w), 4.0), FERRO), mclau)
    return Image.fromarray(img, 'RGBA')


@functools.lru_cache(maxsize=None)
def tex_costat():
    """El gruix del mur de la façana (assolellat): carreus grans de la cantonada."""
    w, h = GRUIX * TS, HP * TS
    lv, _ = nivells_carreus(w, h, 5.6, fila=(26, 36), ample=(30, 70), seed=12, relleu=0.6, gra=0.7)
    return Image.fromarray(tramat(lv, PEDRA), 'RGBA')


@functools.lru_cache(maxsize=None)
def tex_torre(k, angle=0.0):
    """La cara k del campanar (la 0 mira la càmera): carreus, la cornisa a mitja alçada, i a dalt la finestra; a la
    0, la campana penjada del jou (gronxada `angle` radians) i, a baix, la porteta. → (imatge, finestra (màscara))."""
    w, h = int(round(TCARA * TS)), TH * TS
    lv, _ = nivells_carreus(w, h, 4.9 + (0.3 if k == 0 else 0), fila=(20, 28), ample=(26, 44), seed=20 + k,
                            relleu=0.6, gra=0.8)
    yy, xx = np.mgrid[0:h, 0:w].astype(np.float32)
    s, y = xx / TS - TCARA / 2, TH - yy / TS
    # la cornisa (un fris d'arquets llombards, com a les esglésies de la comarca)
    mfr = (y > 176) & (y < 186)
    lv[mfr] = (5.6 + np.where(((s + 40) % 10) < 1.4, -1.6, 0) + (y[mfr.any(1)][:, None].mean() * 0))[mfr] \
        if False else (5.8 - (np.abs(((s + 40) % 10) - 5) < 3.2) * (y < 181) * 1.8)[mfr]
    lv[(y >= 186) & (y < 189)] = 6.8
    y0, y1, fw = TFIN
    yc = y1 - fw
    mf = (np.abs(s) < fw) & (y >= y0) & ((y < yc) | (np.hypot(s, y - yc) < fw))
    mvora = (np.abs(s) < fw + 4) & (y >= y0 - 4) & ((y < yc) | (np.hypot(s, y - yc) < fw + 4)) & ~mf
    lv[mvora] = (6.2 - (np.hypot(s, y - yc) > fw + 2.5) * 0.6)[mvora]
    lv[mf] = (0.4 + (y - y0) * 0.012)[mf]
    lv[mf & (y < y0 + 3)] = 3.0                    # l'ampit
    if k == 0:
        mp = (np.abs(s) < 13) & (y < 62) & ((y < 50) | (np.hypot(s, y - 50) < 13))
        mpv = (np.abs(s) < 17) & (y < 66) & ((y < 50) | (np.hypot(s, y - 50) < 17)) & ~mp
        lv[mpv] = (6.0 - (np.abs(s) > 15) * 0.5)[mpv]
        lv[mp] = (1.0 + (y < 4) * 0.4)[mp]
    img = tramat(lv, PEDRA)
    hum = y < 30
    img[hum, :3] = (img[hum, :3] * (0.74 + 0.26 * np.clip(y[hum] / 30, 0, 1))[:, None]).astype(np.uint8)
    if k == 0:
        _campana(img, s, y, angle)
    return Image.fromarray(img, 'RGBA'), Image.fromarray((mf * 255).astype(np.uint8), 'L')


def _campana(img, s, y, angle):
    """La campana de bronze dins la finestra, penjada del jou de fusta, gronxada `angle` radians."""
    jy = CAMPANA_Y + 14
    mj = (np.abs(s) < TFIN[2] + 3) & (np.abs(y - jy) < 2.6)
    enganxa(img, tramat(np.full(s.shape, 3.0) + (y > jy) * 0.8, FUSTA), mj)
    # coordenades de la campana, girades al voltant del jou
    c, sn = math.cos(angle), math.sin(angle)
    ls = (s * c + (jy - y) * sn)
    ly = (-s * sn + (jy - y) * c)                  # cap avall des del jou
    # el perfil de la campana: estreta a dalt, oberta a baix
    hb = 22.0
    perfil = 6.0 + 5.0 * np.clip(ly / hb, 0, 1) ** 2.2
    m = (ly >= 1.5) & (ly < hb) & (np.abs(ls) < perfil)
    m |= (ly >= hb) & (ly < hb + 2.2) & (np.abs(ls) < perfil + 1.2)
    m |= (ly >= -0.5) & (ly < 2.5) & (np.abs(ls) < 2.2)      # les anses
    sh = 3.4 + np.cos(ls / 12.0 * 2.4 - 0.7) * 1.6 + (np.abs(ly - 8) < 0.9) * 0.6 + (ly > hb) * 0.9
    sh -= np.where(np.abs(ls) > perfil - 1.3, 1.0, 0)
    enganxa(img, tramat(sh, BRONZE), m)
    # el batall, a sota
    mb = (np.abs(ls - math.sin(angle) * 2) < 1.4) & (ly >= hb + 2.2) & (ly < hb + 5.2)
    enganxa(img, tramat(np.full(s.shape, 2.0), FERRO), mb)


@functools.lru_cache(maxsize=None)
def tex_casa(cara):
    """La casa del batlle: `davant` (el portal adovellat, la finestra amb porticons, la reixa del celler arran de
    terra) o `costat` (paredat, el capcer i un finestró). → imatge RGBA."""
    x0, x1, z0, z1, hr_, hc = CASA
    if cara == 'davant':
        w, h = int(x1 - x0), int(hr_)
    else:
        w, h = int(z1 - z0), int(hc)
    W_, H_ = w * TS, h * TS
    lv = nivells_paredat(W_, H_, 4.9, mida=(10, 18), seed=30 if cara == 'davant' else 31)
    yy, xx = np.mgrid[0:H_, 0:W_].astype(np.float32)
    s, y = xx / TS, h - yy / TS
    # les cantoneres de carreus
    for cxs in (0, w - 14):
        m = (s >= cxs) & (s < cxs + 14)
        lvc, _ = nivells_carreus(W_, H_, 5.6, fila=(28, 36), ample=(28, 28), seed=33 + cxs, relleu=0.6)
        lv[m] = lvc[m]
    alpha = np.ones((H_, W_), bool)
    img = None
    if cara == 'davant':
        pc, pw, ph = 140, 26, 92
        r = np.hypot(s - pc, y - ph)
        ang = np.arctan2(y - ph, s - pc)
        dov = (r >= pw) & (r < pw + 22) & (y >= ph)
        nd = np.floor(ang / (math.pi / 9))
        lv[dov] = (5.8 + (np.vectorize(lambda d: hr(int(d), 9))(nd) - 0.5) * 0.9 -
                   (np.abs(ang - (nd + 0.5) * math.pi / 9) > math.pi / 9 * 0.42) * 1.6)[dov]
        bran = (np.abs(s - pc) >= pw) & (np.abs(s - pc) < pw + 8) & (y < ph)
        lv[bran] = (5.6 + ((yy // (20 * TS)) % 2) * 0.5 - (np.abs(s - pc) < pw + 1.5) * 1.6)[bran]
        porta = ((np.abs(s - pc) < pw) & (y < ph)) | ((r < pw) & (y >= ph))
        img = tramat(lv, TOSCA)
        dl = 3.8 + np.where(((s - pc) % 9) < 1.2, -1.4, 0) + (fbm_np(W_, H_, 6, 35, 3) - 0.5) * 1.2
        enganxa(img, tramat(dl, FUSTA), porta)
        # la finestra del pis, amb els porticons oberts
        fx, fy, fw_, fh_ = 70, 140, 16, 26
        mfin = (np.abs(s - fx) < fw_) & (np.abs(y - fy) < fh_)
        mmarc = (np.abs(s - fx) < fw_ + 4) & (np.abs(y - fy) < fh_ + 4) & ~mfin
        enganxa(img, tramat(np.full(s.shape, 6.0) + (y > fy + fh_) * 0.8, TOSCA), mmarc)
        enganxa(img, tramat(0.8 + (y - fy + fh_) * 0.02, FERRO), mfin)
        for sd in (-1, 1):
            mp = (np.abs(s - (fx + sd * (fw_ + 4 + 9))) < 9) & (np.abs(y - fy) < fh_ + 2)
            enganxa(img, tramat(3.6 + (((s - fx) % 6) < 1) * -1.2 + sd * 0.3, FUSTA), mp)
        # la reixa del celler, arran de terra: el forat fosc i els barrots
        s0, s1, ry0, ry1 = REIXA
        mr = (s >= s0) & (s < s1) & (y >= ry0) & (y < ry1)
        mrv = (s >= s0 - 4) & (s < s1 + 4) & (y >= ry0 - 2) & (y < ry1 + 4) & ~mr
        enganxa(img, tramat(np.full(s.shape, 6.2) - (y < ry0) * 1.2, TOSCA), mrv)
        enganxa(img, tramat(0.3 + (y - ry0) * 0.03, FERRO), mr)
        barrots = mr & ((((s - s0) % 9) < 2.2) | (np.abs(y - (ry0 + ry1) / 2) < 1.2))
        enganxa(img, tramat(2.8 + (((s - s0) % 9) < 1) * 1.0, FERRO), barrots)
        # una taca d'humitat que baixa de la reixa (i el llindar de pedra)
    else:
        img = tramat(lv, TOSCA)
        # el capcer: la casa té el carener al mig (s = la meitat), a hc; el ràfec a hr_
        dist = (h - y) - (hc - hr_) * np.abs(s - w / 2) / (w / 2)
        alpha &= dist >= 0
        fx, fy = 120, 150
        mfin = (np.abs(s - fx) < 7) & (np.abs(y - fy) < 10)
        enganxa(img, tramat(np.full(s.shape, 0.8), FERRO), mfin)
        enganxa(img, tramat(np.full(s.shape, 6.0), TOSCA), (np.abs(s - fx) < 10) & (np.abs(y - fy) < 13) & ~mfin)
    img[..., 3] = np.where(alpha, img[..., 3], 0)
    hum = (y < 34) & alpha
    img[hum, :3] = (img[hum, :3] * (0.7 + 0.3 * np.clip(y[hum] / 34, 0, 1))[:, None]).astype(np.uint8)
    return Image.fromarray(img, 'RGBA')


# ─── Superfícies procedurals ────────────────────────────────────────────────
_NT = fbm_np(2600, 2600, 40, 51, 4)                # el soroll del terra: [z + 400, x + 600]
_NT2 = fbm_np(2600, 2600, 9, 52, 3)


def _nt(x, z, arr=None):
    a = _NT if arr is None else arr
    return float(a[min(2599, max(0, int(z) + 400)), min(2599, max(0, int(x) + 600))])


def _bassal(x, z, mati=False):
    """0..1: quant hi ha aigua a la terra (bassals que fan de mirall)."""
    if mati:
        return 0.0
    n = _nt(x * 1.3 + 300, z * 1.3)
    rodera = math.exp(-((x * 0.25 + z - 140) % 260 - 130) ** 2 / 90) * 0.12 if 380 < x < 980 else 0
    return max(0.0, min(1.0, (n + rodera - 0.67) * 9))


def _terra_lvl(mati):
    def L(s, t, P):
        x, z = P[0], P[2]
        n, g = _nt(x, z), _nt(x, z, _NT2)
        v = 4.3 + (n - 0.5) * 1.6 + (g - 0.5) * 1.0
        # pedres escampades (es fan petites cap al fons)
        cel = 26
        i, j = math.floor(x / cel), math.floor(z / cel)
        if z < 520 and hr(i, j, 61) < 0.22 * min(1.0, (520 - z) / 200):
            cx, cz, rr = (i + hr(i, j, 62)) * cel, (j + hr(i, j, 63)) * cel, 3 + hr(i, j, 64) * 5
            d = math.hypot(x - cx, (z - cz) * 1.2)
            if d < rr:
                v += 1.0 + (cz - z) / rr * 0.8
            elif d < rr + 1.6:
                v -= 0.9
        if not mati:
            v -= 0.5                                # la terra molla, més fosca
            b = _bassal(x, z)
            if 0 < b < 0.35:
                v -= 1.0                            # la vora fosca del bassal
        else:
            v += 0.4
        return v
    return L


def _gespa_lvl(s, t, P):
    x, z = P[0], P[2]
    g = _nt(x * 3, z * 3, _NT2)
    v = 5.0 + (g - 0.5) * 2.2 + (_nt(x, z) - 0.5) * 1.2
    if hr(int(x * 0.9), int(z * 0.9), 71) < 0.18:
        v += 1.0                                    # les fulles que brillen (mullades)
    return v


# ─── L'escena ────────────────────────────────────────────────────────────────

def _cel(cv, mati):
    cel_trencat(cv, 0, ROOM_W - 1, 0, 100, 92, seed=5 if not mati else 6, mati=mati,
                sol=(60, -30) if not mati else None)
    # la serralada, blava, i els turons de més a prop
    silueta_muntanyes(cv, 0, ROOM_W - 1, 84, 30, LLUNY, 3.4 if not mati else 3.9, seed=9, rug=0.006, y1=100)
    silueta_muntanyes(cv, 0, ROOM_W - 1, 92, 16, LLUNY, 2.2 if not mati else 2.8, seed=10, rug=0.014, y1=110)


def _arbre(cv, e, mati):
    """L'arbre gran de darrere la nau (com a la foto): el tronc i la capçada, en pantalla."""
    x, z = ARBRE
    k = CAM.escala((x, 0, z))
    u, v, _ = CAM.projecta((x, 0, z))
    for yy in range(int(v - 120 * k), int(v) + 1):
        for xx in range(int(u - 6 * k), int(u + 6 * k) + 1):
            cv.put(xx, yy, ESCORÇA, 2.2 + (xx - u) / (6 * k) * 0.8, lit=0)
    capcada(cv, u - 10 * k, v - 210 * k, 150 * k, 112 * k, FULLA, 3.9 if not mati else 4.4, seed=4,
            llum=(-0.6, -0.7) if not mati else (-0.9, -0.3))
    capcada(cv, u + 70 * k, v - 170 * k, 90 * k, 80 * k, FULLA, 3.5 if not mati else 4.0, seed=5,
            llum=(-0.6, -0.7) if not mati else (-0.9, -0.3))


def _avet(cv, mati):
    """L'avet, al capdamunt del carrer: enorme, fosc, per damunt de les teulades."""
    x, z = AVET
    k = CAM.escala((x, 0, z))
    u, v, _ = CAM.projecta((x, 0, z))
    alt = 1500 * k
    for yy in range(max(0, int(v - alt)), int(v) + 1):
        t = (v - yy) / alt                          # 0 a baix, 1 a dalt
        amp = 260 * k * (1 - t) ** 1.05 + 2
        for xx in range(int(u - amp - 4), int(u + amp + 5)):
            dx = (xx - u) / amp
            pis = (t * 26) % 1.0
            vora = amp * (0.8 + 0.2 * pis) + (fbm(xx * 0.4, yy * 0.4, 81) - 0.5) * 6
            if abs(xx - u) > vora:
                continue
            val = 1.6 + (-dx) * 0.9 + (pis - 0.5) * 1.0 + (fbm(xx * 0.3, yy * 0.3, 82) - 0.5) * 1.0
            cv.put(xx, yy, FULLA, val + (0.5 if mati else 0), lit=0)


def lvl_finestres(base, seed, mida=11):
    """Paredat amb finestres i portes (fosques, amb l'ampit clar) a una façana: per a les cases de fons."""
    par = lvl_paredat(base, mida, seed)

    def L(s, t, P):
        col = int(s // 64)
        fx = col * 64 + 24 + hr(col, seed) * 16
        alt = P[1]
        for y0, y1 in ((112, 142), (170, 196)):
            if hr(col, y0, seed) < 0.62 and fx <= s < fx + 13 and y0 <= alt < y1:
                return 0.8 + (alt - y0) * 0.02
            if hr(col, y0, seed) < 0.62 and fx - 2 <= s < fx + 15 and y0 - 3 <= alt < y0:
                return base + 1.4
        if hr(col, 7, seed) < 0.3 and fx - 4 <= s < fx + 18 and alt < 64:
            return 1.4 + alt * 0.01
        return par(s, t, P)
    return L


def _cases_fons(e, mati):
    """Les cases del fons, darrere la nau i el carrer: caixes amb teulada, perquè la plaça tingui poble darrere."""
    cases = [(-700, -380, 760, 1000, 170), (-300, 40, 1080, 1300, 190), (120, 380, 1180, 1400, 150),
             (700, 980, 900, 1200, 180), (1100, 1500, 820, 1100, 230), (-1100, -720, 520, 800, 200)]
    for i, (x0, x1, z0, z1, h) in enumerate(cases):
        e.caixa(f'fons{i}', x0, x1, 0, h, z0, z1, TOSCA, 4.0, cares={
            'davant': {'ramp': TOSCA, 'lvl': lvl_finestres(4.4 + (0.3 if mati else 0), 90 + i, 12)},
            'dreta': {'ramp': TOSCA, 'lvl': lvl_paredat(3.4, 12, 95 + i)},
            'esquerra': {'ramp': TOSCA, 'lvl': lvl_paredat(3.6, 12, 97 + i)}})
        # la teulada: dues aigües (el carener paral·lel a la façana)
        zm = (z0 + z1) / 2
        e.quad(f'fons{i}', (x0 - 8, h + 50, zm), (x1 + 8, h + 50, zm), (x1 + 8, h - 4, z0 - 14), (x0 - 8, h - 4, z0 - 14),
               ramp=TEULA, lvl=lambda s, t, P: 3.8 + (0.8 if (s % 9) < 4.5 else 0) - t * 0.01)


def _ombres(e, mati):
    """Les ombres al terra (del campanar, la façana, la casa i la creu), en diagonal segons el sol."""
    sd = _sol_dir(mati)
    k = 0.42 if not mati else 0.5

    def ombra_poligon(sid, base, alt):
        """L'ombra d'un prisma vertical (la base, un polígon convex a terra) d'alçada `alt`."""
        top = [_ombra_terra((p[0], alt, p[2]), sd) for p in base]
        pts = [(p[0], p[2]) for p in base] + [(p[0], p[2]) for p in top]
        xs, zs = [p[0] for p in pts], [p[1] for p in pts]
        x0, x1, z0, z1 = min(xs) - 4, max(xs) + 4, min(zs) - 4, max(zs) + 4
        # l'envolupant convexa (Andrew)
        P = sorted(set(pts))

        def cr(o, a, b):
            return (a[0] - o[0]) * (b[1] - o[1]) - (a[1] - o[1]) * (b[0] - o[0])
        lo, up = [], []
        for p in P:
            while len(lo) >= 2 and cr(lo[-2], lo[-1], p) <= 0:
                lo.pop()
            lo.append(p)
        for p in reversed(P):
            while len(up) >= 2 and cr(up[-2], up[-1], p) <= 0:
                up.pop()
            up.append(p)
        hull = lo[:-1] + up[:-1]

        def dins(px, pz):
            n = len(hull)
            for i in range(n):
                a, b = hull[i], hull[(i + 1) % n]
                if (b[0] - a[0]) * (pz - a[1]) - (b[1] - a[1]) * (px - a[0]) < 0:
                    return False
            return True
        e.foscor(sid, (x0, 0.6, z1), (x1, 0.6, z1), (x1, 0.6, z0), (x0, 0.6, z0),
                 lambda s, t: k if dins(x0 + s, z1 - t) else 0.0)
    ombra_poligon('ombra_torre', [torre_cara(i)[0] for i in range(8)], TH)
    ombra_poligon('ombra_facana', [L, K, _add(K, NB, GRUIX), _add(L, NB, GRUIX)], HE)
    x0, x1, z0, z1, hr_, _ = CASA
    ombra_poligon('ombra_casa', [(x0, 0, z0), (x1, 0, z0), (x1, 0, z1), (x0, 0, z1)], hr_)
    cx, cz = CREU
    ombra_poligon('ombra_creu', [(cx - 4, 0, cz - 4), (cx + 4, 0, cz - 4), (cx + 4, 0, cz + 4), (cx - 4, 0, cz + 4)],
                  150)


def _mur_nau(e, A, B, alt, seed, sid='murs'):
    """Un mur esbotzat de la nau, d'A a B (a terra), amb el capçal irregular (`alt(s)`) i paredat."""
    e.quad(sid, _y(A, 140), _y(B, 140), _y(B, 0), _y(A, 0), ramp=TOSCA,
           lvl=lambda s, t, P: lvl_paredat(4.6, 10, seed)(s, t, P) + (0.9 if 140 - t > alt(s) - 3 else 0),
           forma=lambda s, t: 140 - t <= alt(s))


def escena(cv, mati=False, corda=False, campana=0.0):
    """Tota la plaça, de lluny a prop (sense z-buffer: l'ordre és el de la profunditat). → l'Escena."""
    lls, amb = llums(mati)
    e = Escena(cv, CAM, lls, ambient=amb)
    _cel(cv, mati)
    # el terra de la plaça (molt ample: si no, els marges entren a l'horitzó)
    e.quad('terra', (-30000, 0, 9000), (30000, 0, 9000), (30000, 0, -300), (-30000, 0, -300), ramp=TERRA,
           lvl=_terra_lvl(mati))
    # els bassals: el cel s'hi reflecteix (més clar com més lluny: el cel de prop de l'horitzó)
    if not mati:
        e.claror((-300, 0.3, 700), (1300, 0.3, 700), (1300, 0.3, -60), (-300, 0.3, -60), (150, 174, 204),
                 lambda s, t: 0.5 * min(1.0, _bassal(-300 + s, 700 - t) * 1.4) * (0.7 + 0.3 * (t / 760)))
    _ombres(e, mati)
    _avet(cv, mati)
    _cases_fons(e, mati)
    _arbre(cv, e, mati)
    # ── la casa del costat de la del batlle, amb la volta per on el carrer surt de la plaça
    a0, a1, b0, b1, h2 = CASA2
    v0, v1, vh = VOLTA

    def volta(s_, t):
        """Dins la volta (s_ des de a0, t des de dalt): 0 fora, 1 a la volta, 2 a la sortida del fons (assolellada)."""
        x, y = a0 + s_, h2 - t
        r = (v1 - v0) / 2
        cx = (v0 + v1) / 2
        dins = abs(x - cx) < r and (y < vh - r or math.hypot(x - cx, y - (vh - r)) < r)
        if not dins:
            return 0
        r2 = r * 0.5
        fons = abs(x - cx - 6) < r2 and (y < (vh - r) * 0.62 or math.hypot(x - cx - 6, y - (vh - r) * 0.62) < r2)
        return 2 if fons else 1

    def lvl_casa2(s_, t, P):
        q = volta(s_, t)
        if q == 2:
            return 5.6 + (1.0 if (h2 - t) < 10 else 0) - (h2 - t) * 0.01
        if q == 1:
            return 0.8 + (h2 - t) * 0.006 + (0.8 if abs(s_ - (v0 + v1) / 2 + a0 - 6) > (v1 - v0) / 2 - 3 else 0)
        return lvl_finestres(4.6 if not mati else 5.2, 160, 11)(s_, t, P)
    e.caixa('casa2', a0, a1, 0, h2, b0, b1, TOSCA, 4.0, cares={
        'davant': {'ramp': TOSCA, 'lvl': lvl_casa2}})
    e.quad('casa2', (a0 - 12, h2 - 2, b0 - 14), (a1 + 12, h2 - 2, b0 - 14), (a1 + 12, h2 + 50, (b0 + b1) / 2),
           (a0 - 12, h2 + 50, (b0 + b1) / 2), ramp=TEULA,
           lvl=lambda s, t, P: 3.8 + (0.9 if (s % 10) < 5 else 0) + (hr(int(s // 10), int(t // 7), 6) - 0.5) * 0.7,
           dues_cares=True)
    e.foscor('ombra_rafec2', (a0, h2 - 1, b0 - 0.5), (a1, h2 - 1, b0 - 0.5), (a1, h2 - 26, b0 - 0.5),
             (a0, h2 - 26, b0 - 0.5), lambda s, t: 0.35 * max(0.0, 1 - t / 26))
    # ── la casa de l'esquerra (tallada per la vora)
    e.caixa('casa_esq', -900, -300, 0, 196, 360, 760, TOSCA, 4.0, cares={
        'dreta': {'ramp': TOSCA, 'lvl': lvl_finestres(4.6 if not mati else 5.4, 150, 11)},
        'davant': {'ramp': TOSCA, 'lvl': lvl_paredat(4.0, 11, 151)}})
    e.quad('casa_esq', (-300 + 14, 196 - 2, 340), (-300 + 14, 196 - 2, 780), (-380, 236, 780), (-380, 236, 340),
           ramp=TEULA, lvl=lambda s, t, P: 3.6 + (0.9 if (s % 9) < 4.5 else 0), dues_cares=True)
    # ── la nau: la plataforma de pedra amb la gespa, els murs esbotzats, l'absis esmotxat al fons
    e.quad('gespa', _y(NAU_D, NH), _y(NAU_C, NH), _y(NAU_B, NH), _y(NAU_A, NH), ramp=GESPA, lvl=_gespa_lvl,
           dues_cares=True)
    if not mati:                                   # el raig de sol que entra per la nau oberta
        e.claror(_y(NAU_D, NH + 0.3), _y(NAU_C, NH + 0.3), _y(NAU_B, NH + 0.3), _y(NAU_A, NH + 0.3),
                 (236, 232, 160), lambda s, t: 0.22 * max(0.0, math.sin((s + t * 0.6) / NL * math.pi * 1.1 + 0.2)))
    for i in range(10):                            # l'absis esmotxat: una corba de pedra baixa al fons
        a0_, a1_ = math.pi * i / 10, math.pi * (i + 1) / 10
        cen = _add(NAU_B, EN, -NW / 2)
        r = NW / 2

        def pt(a):
            return (cen[0] + EN[0] * math.cos(a) * r + DN[0] * math.sin(a) * r * 0.8, 0.0,
                    cen[2] + EN[2] * math.cos(a) * r + DN[2] * math.sin(a) * r * 0.8)
        _mur_nau(e, pt(a1_), pt(a0_), lambda s, i=i: 60 + 30 * math.sin(i * 1.7) + (s % 7), 110 + i, sid='absis')
    e.quad('nau', _y(NAU_A, NH), _y(NAU_B, NH), NAU_B, NAU_A, ramp=TOSCA, lvl=lvl_paredat(4.2, 9, 44))

    def alt_dreta(s):
        if s < 40:
            return 128 - s * 1.2
        return max(NH + 10, 72 - (s - 40) * 0.18 + 14 * math.sin(s * 0.05) - (60 if GRAONS - 40 < s < GRAONS + 40 else 0) +
                   (hr(int(s // 8), 7) - 0.5) * 8)
    # el mur de la dreta de la nau, esbotzat (darrere del campanar), i els graons per pujar a la gespa
    _mur_nau(e, _add(NAU_A, DN, 8), NAU_B, alt_dreta, 120)
    for g in range(3):
        c = _add(_add(NAU_A, DN, GRAONS), EN, 10 - g * 8)
        e.caixa_girada('graons', c[0], c[2], 70, 9, NH - g * 5, -(math.pi / 2 - FN), TOSCA, 5.0,
                       cares={'dalt': {'ramp': TOSCA, 'lvl': 6.2}, 'davant': {'ramp': TOSCA, 'lvl': 4.4},
                              'esquerra': {'ramp': TOSCA, 'lvl': 5.4}})
    # ── el campanar (de darrere a davant; quad descarta les cares d'esquena)
    for k in (3, 2, 1, 0, -1, -2):
        a, b = torre_cara(k)
        img, _ = tex_torre(k % 8, campana if k == 0 else 0.0)
        e.quad(f'torre{k % 8}', _y(b, TH), _y(a, TH), a, b, tex=(img, (0, 0, TCARA, TH), TS))
    if corda:
        _corda(e)
    # ── la façana de Sant Pol: el gruix del mur (de cara al sol) i la cara de la portada
    Kb = _add(K, NB, GRUIX)
    e.quad('facana_costat', _y(K, HE + 2), _y(Kb, HE + 2), Kb, K, tex=(tex_costat(), (0, HP - HE - 2, GRUIX, HP), TS))
    e.quad('facana', _y(L, HP), _y(K, HP), K, L, tex=(tex_facana(), (0, 0, WF, HP), TS))
    # el ràfec de teula damunt del gruix de la cantonada, com a la foto
    e.quad('facana_costat', _y(_add(K, EF, 2), HE + 10), _y(_add(Kb, EF, 2), HE + 10), _y(_add(Kb, EF, -26), HE),
           _y(_add(K, EF, -26), HE), ramp=TEULA, lvl=lambda s, t, P: 4.0 + (0.9 if (s % 8) < 4 else 0))
    # ── la casa del batlle
    x0, x1, z0, z1, hr_, hc = CASA
    zm = (z0 + z1) / 2
    e.quad('casa_costat', (x0, hc, z1), (x0, hc, z0), (x0, 0, z0), (x0, 0, z1),
           tex=(tex_casa('costat'), (0, 0, z1 - z0, hc), TS))
    e.quad('casa', (x0, hr_, z0), (x1, hr_, z0), (x1, 0, z0), (x0, 0, z0), tex=(tex_casa('davant'), (0, 0, x1 - x0, hr_), TS))
    # la teulada: el carener de costat a costat (paral·lel a la façana), el ràfec que sobresurt
    e.quad('teulada', (x0 - 12, hc + 2, zm), (x1 + 12, hc + 2, zm), (x1 + 12, hr_ - 4, z0 - 16),
           (x0 - 12, hr_ - 4, z0 - 16), ramp=TEULA,
           lvl=lambda s, t, P: 4.2 + (0.9 if (s % 10) < 5 else -0.3) + (hr(int(s // 10), int(t // 7), 5) - 0.5) * 0.7)
    e.quad('teulada', (x0 - 12, hr_ - 4, z0 - 16), (x1 + 12, hr_ - 4, z0 - 16), (x1 + 12, hr_ - 10, z0 - 16),
           (x0 - 12, hr_ - 10, z0 - 16), ramp=FUSTA, lvl=2.6)
    e.foscor('ombra_rafec', (x0, hr_ - 1, z0 - 0.5), (x1, hr_ - 1, z0 - 0.5), (x1, hr_ - 30, z0 - 0.5),
             (x0, hr_ - 30, z0 - 0.5), lambda s, t: 0.4 * max(0.0, 1 - t / 30))
    # ── la creu de terme: tres graons, la columna i la creu
    cx, cz = CREU
    for g, (mw, h0, h1) in enumerate(((36, 0, 8), (27, 8, 16), (18, 16, 24))):
        e.caixa('creu', cx - mw, cx + mw, h0, h1, cz - mw, cz + mw, PEDRA, 5.0, cares={
            'dalt': {'ramp': PEDRA, 'lvl': 6.4}, 'davant': {'ramp': PEDRA, 'lvl': lambda s, t, P: 4.8 - t * 0.08},
            'esquerra': {'ramp': PEDRA, 'lvl': 5.6}, 'dreta': {'ramp': PEDRA, 'lvl': 3.6}})
    e.caixa('creu', cx - 7, cx + 7, 24, 34, cz - 7, cz + 7, PEDRA, 5.0)
    e.caixa('creu', cx - 4.5, cx + 4.5, 34, 150, cz - 4.5, cz + 4.5, PEDRA, 5.0, cares={
        'esquerra': {'ramp': PEDRA, 'lvl': 6.0}, 'davant': {'ramp': PEDRA, 'lvl': 5.0},
        'dreta': {'ramp': PEDRA, 'lvl': 3.4}})
    e.caixa('creu', cx - 7, cx + 7, 150, 156, cz - 7, cz + 7, PEDRA, 5.6)
    e.caixa('creu', cx - 3.5, cx + 3.5, 156, 196, cz - 3.5, cz + 3.5, PEDRA, 5.4, cares={
        'esquerra': {'ramp': PEDRA, 'lvl': 6.2}, 'dreta': {'ramp': PEDRA, 'lvl': 3.6}})
    e.caixa('creu', cx - 18, cx + 18, 176, 183, cz - 3.5, cz + 3.5, PEDRA, 5.4, cares={
        'esquerra': {'ramp': PEDRA, 'lvl': 6.2}, 'dreta': {'ramp': PEDRA, 'lvl': 3.6}})
    return e


def _corda(e):
    """La corda de cànem: penja de la finestra del campanar, resseguint el mur, fins a terra (on s'estira)."""
    a, b = torre_cara(0)
    m = ((a[0] + b[0]) / 2, 0, (a[2] + b[2]) / 2)
    n = (math.cos(TANG), 0.0, math.sin(TANG))
    top = (m[0] + n[0] * 3, TFIN[0] + 4, m[2] + n[2] * 3)
    peu = (m[0] + n[0] * 22 + 6, 0.0, m[2] + n[2] * 22)
    pts = [top, (top[0] + n[0] * 4, 140, top[2] + n[2] * 4), (top[0] + n[0] * 8 + 2, 50, top[2] + n[2] * 8),
           (peu[0] - 3, 6, peu[2] - 2), peu]
    e.cable("corda", pts, CANEM, 3.4, gruix=3.2)
    # el rotlle que sobra, a terra
    for i in range(3):
        e.cable('corda', [(peu[0] + 2 * i, 1 + i, peu[2] - 6), (peu[0] + 10 + 2 * i, 1 + i, peu[2] + 2),
                          (peu[0] + 2 * i, 1 + i, peu[2] + 8), (peu[0] - 6, 1 + i, peu[2])], CANEM, 2.6 + i * 0.2,
                gruix=2.0)


def _primer_pla(cv, mati):
    """El primer pla, en pantalla: pedres i matolls d'herba molla a les cantonades de baix (en silueta, tallats per la
    vora). → la màscara (on hi ha primer pla)."""
    m = np.zeros((cv.h, cv.w), bool)
    import random
    rnd = random.Random(91)
    # a l'esquerra: un munt de pedres i herba alta
    for cx, cy, rx, ry in ((18, 262, 46, 22), (70, 266, 30, 14), (128, 270, 22, 10)):
        for y in range(int(cy - ry), min(BOTTOM, int(cy + ry)) + 1):
            for x in range(int(cx - rx), int(cx + rx) + 1):
                nx, ny = (x - cx) / rx, (y - cy) / ry
                if nx * nx + ny * ny > 1 + (fbm(x * 0.2, y * 0.2, 92) - 0.5) * 0.5 or not 0 <= x < cv.w:
                    continue
                cv.put(x, y, TOSCA, 1.6 + (-nx * 0.6 - ny * 1.0) + (fbm(x * 0.4, y * 0.4, 93) - 0.5) * 1.2, lit=0)
                m[y, x] = True
    # herba: fulles llargues que es dobleguen
    for _ in range(70):
        x0 = rnd.uniform(-10, 170) if rnd.random() < 0.6 else rnd.uniform(ROOM_W - 160, ROOM_W + 10)
        h = rnd.uniform(10, 36) * (1.4 if x0 < 60 or x0 > ROOM_W - 60 else 1.0)
        ben = rnd.uniform(-0.6, 0.6)
        lvl = rnd.uniform(1.2, 2.8) + (0.6 if mati else 0)
        for i in range(int(h)):
            t = i / h
            x = int(x0 + ben * t * t * h * 0.6)
            y = BOTTOM - i
            if 0 <= x < cv.w and y >= 0:
                cv.put(x, y, GESPA, lvl + t * 1.4, lit=0)
                m[y, x] = True
    # a la dreta: un bassal amb la vora d'herba i una pedra grossa
    for y in range(240, BOTTOM + 1):
        for x in range(ROOM_W - 130, ROOM_W):
            nx, ny = (x - (ROOM_W - 40)) / 70, (y - 262) / 18
            if nx * nx + ny * ny <= 1 + (fbm(x * 0.2, y * 0.2, 94) - 0.5) * 0.4:
                cv.put(x, y, TOSCA, 1.8 + (-nx * 0.5 - ny * 1.1) + (fbm(x * 0.4, y * 0.4, 95) - 0.5), lit=0)
                m[y, x] = True
    return m


@functools.lru_cache(maxsize=None)
def _base(mati=False, corda=False, campana=0.0, queixa=False):
    cv = Canvas(ROOM_W, light=LIGHT)
    e = escena(cv, mati, corda, campana)
    if queixa:
        cv.img.alpha_composite(e.capa(tex_queixa(), {'facana'}))
        cv.P = cv.img.load()
    m = _primer_pla(cv, mati)
    if mati:                                       # el matí: tot una mica més daurat
        a = np.asarray(cv.img).astype(np.float32)
        a[..., :3] *= np.array([1.07, 1.01, 0.88], np.float32)
        cv.img = Image.fromarray(np.clip(a, 0, 255).astype(np.uint8), 'RGBA').copy()
        cv.P = cv.img.load()
    cv.rect(0, BOTTOM + 1, ROOM_W - 1, cv.h - 1, [(0, 0, 0)], 0, lit=0)    # la barra de verbs: negre
    return cv.img, e, m


# ─── Les dones que filen ─────────────────────────────────────────────────────
# Assegudes a la gespa de la nau (en coordenades del món: x, z i cap on miren), amb el fus i la filosa.
DONES = ((470, 470, 1, ROBA_OCRE, LLANA), (530, 430, -1, ROBA_BLAVA, LLANA), (600, 560, -1, ROBA_VERDA, PAPER),
         (420, 560, 1, ROBA_BLAVA, PAPER))


def _dona(cv, u, v, k, costat, roba, toca, ids_ok, amo, ww):
    """Una dona asseguda a terra, filant (la filosa a l'espatlla, el fus que penja). Pintada en pantalla a
    l'escala k (l'alçada asseguda ≈ 52·k)."""
    def put(x, y, rmp, lvl):
        x, y = int(round(x)), int(round(y))
        if 0 <= x < cv.w and 0 <= y < cv.h and (ids_ok is None or amo[y * ww + x] in ids_ok):
            cv.put(x, y, rmp, lvl, lit=0)
    h = 52 * k
    # la faldilla, estesa a terra
    for y in range(int(v - h * 0.36), int(v) + 1):
        t = (y - (v - h * 0.36)) / (h * 0.36)
        amp = h * (0.22 + 0.2 * t)
        for x in range(int(u - amp + costat * h * 0.08), int(u + amp + costat * h * 0.08) + 1):
            put(x, y, roba, 2.6 - (x - u) * costat * 0.04 - t * 0.6 + ((x * 3) % 7 == 0) * -0.6)
    # el cos
    for y in range(int(v - h * 0.78), int(v - h * 0.3)):
        t = (y - (v - h * 0.78)) / (h * 0.48)
        amp = h * (0.12 + 0.07 * t)
        for x in range(int(u - amp), int(u + amp) + 1):
            put(x, y, roba, 3.0 - (x - u) * costat * -0.08 - 0.2)
    # el cap (la cara de perfil cap al costat) i la toca blanca
    cy = v - h * 0.88
    r = h * 0.11
    for y in range(int(cy - r * 1.4), int(cy + r * 1.3) + 1):
        for x in range(int(u - r * 1.4), int(u + r * 1.4) + 1):
            dx, dy = (x - u) / r, (y - cy) / r
            if dx * dx + dy * dy <= 1.0 and dx * costat > -0.1:
                put(x, y, PELL, 3.0 + dy * -0.4)
            elif dx * dx + dy * dy <= 1.7 and dy < 0.9:
                put(x, y, toca, 4.2 - dy * 0.6 + dx * costat * -0.3)
    # la filosa (un pal a l'espatlla, amb el borrall de llana) i el fus
    fx0, fy0 = u - costat * h * 0.1, v - h * 0.5
    for i in range(int(h * 0.62)):
        put(fx0 - costat * i * 0.25, fy0 - i, FUSTA, 3.4)
    bx, by = fx0 - costat * h * 0.15, fy0 - h * 0.58
    for y in range(int(by - h * 0.08), int(by + h * 0.08) + 1):
        for x in range(int(bx - h * 0.05), int(bx + h * 0.05) + 1):
            put(x, y, LLANA, 4.4 + (y - by) * -0.2)
    hx = u + costat * h * 0.2
    for i in range(int(h * 0.3)):
        put(hx, v - h * 0.55 + i, LLANA, 4.6)
    put(hx, v - h * 0.25, FUSTA, 3.0)
    put(hx, v - h * 0.25 + 1, FUSTA, 3.0)
    # el braç que estira el fil
    for i in range(int(h * 0.2)):
        put(u + costat * (h * 0.08 + i * 0.6), v - h * 0.6 + i * 0.25, roba, 3.4)


def _ids_dones(e):
    return {i for i, sid in enumerate(e.ids) if sid in ('', 'gespa', 'absis', 'fons0', 'fons1', 'fons2', 'fons3',
                                                         'terra', 'nau')}


def dones(pc, mati=False):
    img, e, _ = _base(mati)
    cv = Canvas(ROOM_W, light=None, img=img.copy())
    ok = _ids_dones(e)
    for x, z, costat, roba, toca in DONES:
        P = (x, NH, z)
        u, v, _ = CAM.projecta(P)
        _dona(cv, u, v, CAM.escala(P), costat, roba, toca, ok, e.amo, e.cv.w)
    pc.img.alpha_composite(_diff(cv.img, img))
    pc.P = pc.img.load()


def dones_marxen(pc):
    """Les dones s'han aixecat: a la gespa hi queden un cistell de llana i un tamboret."""
    img, e, _ = _base()
    cv = Canvas(ROOM_W, light=None, img=img.copy())
    ok = _ids_dones(e)
    for x, z, costat, roba, toca in DONES[:3]:
        P = (x + 10 * costat, NH, z)
        u, v, _ = CAM.projecta(P)
        k = CAM.escala(P)
        for y in range(int(v - 8 * k), int(v) + 1):
            for xx in range(int(u - 7 * k), int(u + 7 * k) + 1):
                if 0 <= xx < cv.w and e.amo[y * e.cv.w + xx] in ok:
                    cv.put(xx, y, FUSTA if toca is LLANA else CANEM, 3.4 + ((xx + y) % 3 == 0) * 0.8 -
                           (y - v + 8 * k) * 0.08, lit=0)
        for y in range(int(v - 11 * k), int(v - 7 * k)):
            for xx in range(int(u - 5 * k), int(u + 5 * k) + 1):
                if 0 <= xx < cv.w and e.amo[y * e.cv.w + xx] in ok:
                    cv.put(xx, y, LLANA, 4.6 - (y - v) * 0.02, lit=0)
    pc.img.alpha_composite(_diff(cv.img, img))
    pc.P = pc.img.load()


# ─── Fons, props i animacions ────────────────────────────────────────────────

def bg(cv):
    img, _, _ = _base()
    cv.img.paste(img)
    cv.P = cv.img.load()


def _prop_diff(**kw):
    def draw(pc):
        pc.img.alpha_composite(_diff(_base(**kw)[0], _base()[0]))
        pc.P = pc.img.load()
    return draw


def llum_mati(pc):
    """L'acte 4: el matí net. Tota la sala (el fons sencer, amb el sol de llevant)."""
    img, _, _ = _base(mati=True)
    pc.img.alpha_composite(img)
    pc.P = pc.img.load()


PROPS = {
    'queixa': _prop_diff(queixa=True),
    'dones': dones,
    'corda_campana': _prop_diff(corda=True),
    'llum_mati': llum_mati,
    'dones_marxen': dones_marxen,
}


def _campana_frames():
    """La campana que es gronxa (un vaivé sencer en 8 fotogrames): només la finestra del campanar."""
    base = _base()[0]
    out = []
    for i in range(8):
        ang = 0.55 * math.sin(i / 8 * 2 * math.pi)
        out.append(_diff(_base(campana=round(ang, 3))[0], base))
    return out


ANIMS = {'campana_toca': {'frames': _campana_frames, 'frameDuration': 110}}


# ─── Capes del davant ────────────────────────────────────────────────────────

def _v(x, z, y=0.0):
    return CAM.projecta((x, y, z))[1]


def _p(x, z, y=0.0):
    u, v, _ = CAM.projecta((x, y, z))
    return round(u), round(v)


def _amo(ids):
    def mask(x, y):
        _, e, _ = _base()
        return e.ids[e.amo[y * e.cv.w + x]] in ids
    return mask


def _primer_pla_mask(x, y):
    return bool(_base()[2][y, x])


FRONT = [
    # la creu de terme: qui és darrere la creu (més amunt de la línia del graó de davant) hi passa per darrere
    {'id': 'davant_creu', 'mask': _amo({'creu'}), 'baseline': round(_v(CREU[0], CREU[1] - 36)), 'zIndex': 20},
    {'id': 'davant', 'mask': _primer_pla_mask, 'baseline': 999, 'zIndex': 20},
]


# ─── Geometria (coordenades de sala, projectades) ────────────────────────────

def _rect_mon(*Ps):
    pts = [CAM.projecta(P) for P in Ps]
    return (max(0, round(min(p[0] for p in pts))), max(0, round(min(p[1] for p in pts))),
            min(ROOM_W - 1, round(max(p[0] for p in pts))), min(BOTTOM, round(max(p[1] for p in pts))))


def _davant(P, d):
    """Un punt a `d` unitats davant de P, cap a la càmera (a terra)."""
    dx, dz = CAM.pos[0] - P[0], CAM.pos[2] - P[2]
    n = math.hypot(dx, dz)
    return (P[0] + dx / n * d, 0.0, P[2] + dz / n * d)


def _fs(s, y=0.0):
    """Un punt de la façana: s des de L, a l'alçada y."""
    return _y(_add(L, EF, s), y)


_PORTA = _fs(PC)


def _fsd(s, d):
    """Un punt a terra davant de la façana: s des de L, d unitats enfora."""
    P = _add(L, EF, s)
    return (P[0] - NB[0] * d, P[2] - NB[2] * d)


def _torre_pt(graus, d):
    a = math.radians(graus)
    return (TORRE[0] + math.cos(a) * d, TORRE[2] + math.sin(a) * d)


def _nau_pt(s, d):
    """Un punt a terra davant del mur de la dreta de la nau: s des de NAU_A, d unitats enfora."""
    return (NAU_A[0] + DN[0] * s + EN[0] * d, NAU_A[2] + DN[2] * s + EN[2] * d)


_TPEU = _davant(TORRE, TR + 18)                    # al peu del campanar, on penja la corda
_X0, _X1, _Z0, _Z1, _HR, _HC = CASA
_V0, _V1, _VH = VOLTA
# El terra on es camina (al món): la plaça, de la façana, el campanar i el mur de la nau fins a la casa del batlle i la
# volta del carrer; a prop, fins on el personatge no passa de ≈1,07.
WALK_MON = ([(-420, -12), (-420, 200), _fsd(4, 14), _fsd(WF + 4, 14)] +
            [_torre_pt(g, TR + 10) for g in (-172, -135, -95, -55, -20)] +
            [_nau_pt(250, 16), _nau_pt(GRAONS + 46, 16), (_X0 - 14, _Z0 - 12), (_X1 + 2, _Z0 - 12),
             (_X1 + 8, CASA2[2] - 12), (_V0 + 4, CASA2[2] - 12), (_V0 + 8, CASA2[2] + 14), (_V1 - 8, CASA2[2] + 14),
             (_V1 - 4, CASA2[2] - 12), (1500, CASA2[2] - 12), (1500, -12)])


def _poligon(pts):
    """Projecta, retalla a la sala i treu els punts repetits."""
    out = []
    for x, z in pts:
        u, v = _p(x, z)
        q = (max(0, min(ROOM_W - 1, u)), min(BOTTOM - 4, v))
        if not out or q != out[-1]:
            out.append(q)
    return out[:-1] if out[0] == out[-1] else out


_WALK = _poligon(WALK_MON)
_V_FONS, _V_PROP = min(v for _, v in _WALK), max(v for _, v in _WALK)


def _escala_a(v):
    """L'escala d'un personatge amb els peus a la y de pantalla `v` (al terra: la profunditat només depèn de v)."""
    D = CAM.f * CAM.pos[1] / max(1e-3, v - CAM.centre[1])
    return CAM.f / D


_CREU_FORAT = [_p(CREU[0] + dx, CREU[1] + dz) for dx, dz in ((-42, -42), (42, -42), (42, 42), (-42, 42))]
_NAU_WALK = _p(*_nau_pt(GRAONS + 30, 34))

GEOMETRIA = {
    'things': {
        'llinda': {'rect': _rect_mon(_fs(PC - LLINDA[0], LLINDA[2] + 4), _fs(PC + LLINDA[0], LLINDA[1] - 2)),
                   'walk': _p(*_fsd(PC, 52))},
        'porta_sant_pol': {'rect': _rect_mon(_fs(PC - DOOR[0], DOOR[1]), _fs(PC + DOOR[0], 0)),
                           'walk': _p(*_fsd(PC - 6, 30))},
        'queixa': {'rect': _rect_mon(_fs(PC + 6, 76), _fs(PC + 35, 30)), 'walk': _p(*_fsd(PC + 22, 26))},
        'campanar': {'rect': _rect_mon(*[_y(torre_cara(k)[0], y) for k in (-2, -1, 0, 1, 2) for y in (0, 186)]),
                     'walk': _p(*_TPEU[::2])},
        'campana': {'rect': _rect_mon(*[_y(torre_cara(0)[i], y) for i in (0, 1) for y in (TFIN[0] - 4, TFIN[1] + 2)]),
                    'walk': _p(*_davant(TORRE, TR + 40)[::2])},
        'nau': {'rect': (_rect_mon(*[_y(torre_cara(k)[0], 0) for k in (-1, 0, 1, 2)])[2] + 2,
                         *_rect_mon(_y(_add(NAU_A, DN, 200), 0), _y(NAU_B, 90), _y(NAU_C, 60),
                                    _y(_add(NAU_D, DN, 240), 40))[1:]),
                'walk': _NAU_WALK},
        'dones': {'rect': _rect_mon(*[(x, NH + y, z) for x, z, *_ in DONES for y in (0, 56)]), 'walk': _NAU_WALK},
        'casa_batlle': {'rect': _rect_mon((_X0, _HC, _Z1), (_X1, _HR + 20, _Z0), (_X1, 30, _Z0)),
                        'walk': _p(_X0 + 150, _Z0 - 36)},
        'reixa': {'rect': _rect_mon((_X0 + REIXA[0] - 4, REIXA[3] + 4, _Z0), (_X0 + REIXA[1] + 4, 0, _Z0)),
                  'walk': _p(_X0 + (REIXA[0] + REIXA[1]) / 2, _Z0 - 24)},
        'carrer': {'rect': (_rect_mon((_V0 - 6, _VH + 4, CASA2[2]), (_V1 + 6, 0, CASA2[2]))[0], 96, ROOM_W - 1, BOTTOM),
                   'walk': _p((_V0 + _V1) / 2, CASA2[2] + 8)},
    },
    # l'Iri i la Vet arriben pel carrer (de la volta, a la dreta); en Bonfill fa guàrdia davant la porta; la Sança,
    # al peu dels graons de la nau, on seuen les dones
    'spawns': {'iri': _p(870, 150), 'vet': _p(950, 116), 'bonfill': _p(*_fsd(PC - 30, 40)),
               'sanca': _p(*_nau_pt(GRAONS - 30, 30))},
    'walkable': _WALK,
    'forats': [_CREU_FORAT],
    # el sol de migdia, alt i a l'esquerra: les ombres, curtes, cap a la dreta i endins
    'characterShadow': {'enabled': True, 'color': '#1a1612', 'alpha': 0.42, 'squash': 0.3, 'core': 0.6,
                        'light': {'x': 0.75, 'y': -0.2, 'direction': True, 'stretch': 0.45}},
    'regions': [{'id': 'perspectiva', 'active': True, 'scaleEnabled': True, 'scaleWalkSpeed': True,
                 'scaleTop': round(_escala_a(_V_FONS - 2), 3), 'scaleBottom': round(_escala_a(_V_PROP + 2), 3),
                 'points': [(0, _V_FONS - 2), (ROOM_W - 1, _V_FONS - 2), (ROOM_W - 1, _V_PROP + 2),
                            (0, _V_PROP + 2)]}],
    # La llum de la sala sobre els personatges: el migdia de després de la pluja (clar i una mica fred), el sol a
    # l'esquerra (càlid, suau) i, a l'acte 4, el matí (més càlid; quan es veu `llum_mati`)
    'characterLights': {
        'ambient': '#d2d4d6',
        'lights': [{'x': -400, 'y': -200, 'radius': 1500, 'color': '#fff0d0', 'intensity': 0.35,
                    'whenPropHidden': 'llum_mati'},
                   {'x': -600, 'y': 120, 'radius': 1700, 'color': '#ffd8a0', 'intensity': 0.45,
                    'whenPropVisible': 'llum_mati'}],
    },
}
# On va en Bonfill quan toca la campana (el `place` del contingut): al peu del campanar, a la dreta de la corda.
BONFILL_CAMPANAR = _p(*_torre_pt(-38, TR + 26))
