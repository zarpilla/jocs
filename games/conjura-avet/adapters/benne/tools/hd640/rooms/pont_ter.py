"""
La Conjura de l'Avet — `pont_ter`: el Pont Vell sobre el Ter (actes 1 i 4; l'Iri). EN 3D (hd640/tres_d.py), a 1×.

Primera hora de la tarda, els núvols s'obren: llum grisa i verda. La càmera és de lluny, dalt dels horts, mirant el
pont de biaix i una mica avall (la referència `pont-vell.png`):
  - a dalt, el **pont** de gres rosat: l'arc gran al mig, dos arcs petits, el tallamar, l'esquena d'ase que surt del
    quadre; a través de l'arc, l'altra riba (cases, arbres, la muntanya);
  - el **riu** crescut, verd i amb escuma, que baixa de sota el pont; la **resclosa** en diagonal, de la nostra riba
    (on hi ha el **sobreeixidor**, una post de fusta encaixada a la pedra) cap a l'altra; al mig, la **comporta** (un
    pilar amb la vàlvula de fusta) d'on surt el **rec**, que travessa cap a la riba de la dreta i se'n va, buit, fins
    al **molí** (lluny, a la dreta);
  - la nostra riba: el camí que ve de l'esquerra (`cami`), l'herba molla, la **barca** d'en Joanet mig enfonsada a la
    vora (amb el salabre a dins), i a baix, els **horts** (feixes, cols i porros, els marges de pedra);
  - primer pla: el **salze**, a la dreta, en silueta (les branques que pengen; `FRONT`).

PROPS: `aigua_baixa` (el sobreeixidor obert: l'aigua de la resclosa baixa, la comporta i la serra al descobert),
`barca_calafatada` (la barca sura, amb la resina que brilla a les juntes), `serra_treta` (la comporta sense la
serra), `rec_ple` (l'aigua torna al rec), `llum_mati` (l'acte 4: el matí net, el riu manso, la barca que sura), i
`barca_corrent` (la barca, al matí, a mig riu). ANIMS: `escuma` (el riu que corre i l'escuma de la resclosa).

El món: x a la dreta, y amunt (0 = la riba dels horts), z cap al fons; 1 unitat = 1 px de sala on un personatge fa
la seva mida (l'Iri, 84 px).
"""
import functools
import math

import numpy as np
from PIL import Image

import hd640  # noqa: F401  (abans de cap hd.rooms: posa la llibreria a 640×360)
from hd.pix import Canvas, Light, W, hr
from hd640.tres_d import Camera, Escena, Llum
from hd640.rooms.placa_pont_comu import (BOTTOM, GRES, TOSCA, TEULA, FUSTA, FERRO, GESPA, HORT, LLUNY, AIGUA,
                                         ESCUMA, FULLA, SALZE, ESCORÇA, CANEM, _diff, fbm, fbm_np, tramat,
                                         enganxa, nivells_carreus, lvl_paredat, cel_trencat, silueta_muntanyes,
                                         capcada)

TER = [(10, 22, 20), (14, 32, 28), (20, 44, 36), (28, 58, 46), (38, 74, 56), (50, 90, 66), (66, 108, 76),
       (86, 126, 88), (112, 148, 106), (146, 174, 132), (190, 206, 170)]   # el verd del Ter
CAM = Camera(pos=(300, 260, -330), yaw=0.0, pitch=0.18, f=420, centre=(320, 51))
LIGHT = Light(ambient=0.0, vignette=None, floor_fade=None)   # (la llum és la del món: la de l'Escena)

Y_RIU, Y_AVALL, Y_CRESTA = -10.0, -28.0, -12.0      # l'aigua de dalt de la resclosa, la de sota, el coronament
Y_BAIXA = -25.0                                    # l'aigua de dalt, quan s'obre el sobreeixidor


def _add(a, b, k=1.0):
    return (a[0] + b[0] * k, a[1] + b[1] * k, a[2] + b[2] * k)


def _y(P, y):
    return (P[0], y, P[2])


# ─── El món ──────────────────────────────────────────────────────────────────
VORA_Z = 186                                       # la vora de la nostra riba (de l'esquerra fins a x = 430)
BADIA = (430, 0.72)                                # on la riba de la dreta gira cap al fons, i el pendent (dx/dz)


def vora(x):
    """La z de la vora de la nostra riba a x (no és de regle)."""
    return VORA_Z + 6 * math.sin(x * 0.021) + 3 * math.sin(x * 0.057 + 1.0)


def riba_dreta(z):
    """La x de la riba de la dreta a la profunditat z (el riu és a l'esquerra)."""
    return BADIA[0] + max(0.0, z - VORA_Z) * BADIA[1] + 5 * math.sin(z * 0.031)


TALUS = 16                                         # el marge de terra que baixa fins a l'aigua (en planta)


RIBA_LLUNY = 940                                   # l'altra riba, passat el pont


def al_riu(x, z):
    return vora(x) < z < RIBA_LLUNY and x < riba_dreta(z)


def al_riu_o_marge(x, z):
    return vora(x) - TALUS < z < RIBA_LLUNY and x < riba_dreta(z) + TALUS


PONT_C = (330.0, 0.0, 660.0)                       # el mig del pont (a la cara de davant)
PONT_TH = math.radians(8)
PA = (math.cos(PONT_TH), 0.0, math.sin(PONT_TH))   # al llarg del pont (cap a la dreta i endins)
PN = (math.sin(PONT_TH), 0.0, -math.cos(PONT_TH))  # cap a la càmera
PONT_G = 84                                        # el gruix del pont
PONT_S = (-760, 760)                               # on comença i on acaba la cara (s des del mig)
ARCS = ((30, 196, -40), (-330, 78, 4), (-560, 64, 20), (360, 74, 6))    # (s del mig, radi, y de l'arrencada)


def pont_alt(s):
    """L'alçada del pas (sense l'ampit) a s: l'esquena d'ase."""
    return 262 - 0.34 * abs(s - 20)


def pont_pt(s, y, d=0.0):
    """Un punt de la cara de davant del pont (d: endins)."""
    return (PONT_C[0] + PA[0] * s - PN[0] * d, y, PONT_C[2] + PA[2] * s - PN[2] * d)


RESC0, RESC1 = (36.0, 0.0, 196.0), (636.0, 0.0, 472.0)   # la resclosa, de la nostra riba a la de la dreta
RD = (RESC1[0] - RESC0[0], 0.0, RESC1[2] - RESC0[2])
RL = math.hypot(RD[0], RD[2])
RU = (RD[0] / RL, 0.0, RD[2] / RL)                 # al llarg de la resclosa
RN = (RU[2], 0.0, -RU[0])                          # cap avall del riu (cap a la càmera i l'esquerra)
RESC_G = 22                                        # el gruix del coronament


def resc_pt(t, d=0.0, y=0.0):
    """Un punt de la resclosa: t de 0 (la nostra riba) a 1, d cap avall del riu."""
    return (RESC0[0] + RD[0] * t + RN[0] * d, y, RESC0[2] + RD[2] * t + RN[2] * d)


T_SOBRE, T_COMP = 0.13, 0.47                       # on són el sobreeixidor i la comporta (t de la resclosa)
SOBRE_W = 30                                       # l'ample del sobreeixidor
COMP = resc_pt(T_COMP, RESC_G / 2)                 # el pilar de la comporta
REC = [COMP, (512.0, 0.0, 262.0), (590.0, 0.0, 350.0), (664.0, 0.0, 450.0), (712.0, 0.0, 522.0)]   # el rec
REC_W = 20                                         # l'ample del canal
MOLI = (700.0, 520.0)                              # el molí (x, z de la cantonada de davant a l'esquerra)
BARCA = (300.0, 218.0, -0.28)                      # la barca: x, z, gir
BARCA_RIU = (330.0, 420.0, 0.5)                    # la barca a mig riu (al matí)
SALZE_P = (628.0, 70.0)                            # el salze del primer pla


# ─── La llum ─────────────────────────────────────────────────────────────────

def llums(mati=False):
    if mati:                                       # el sol del matí, baix i a l'esquerra
        return [Llum((-6000, 2400, -800), 1e7, 2.3, power=0.0)], -0.6
    # la tarda de núvols que s'obren: un sol tapat, alt i a la dreta, i molta llum grisa del cel
    return [Llum((4000, 5200, -1500), 1e7, 1.3, power=0.0), Llum((300, 4000, 300), 1e7, 0.7, power=0.0)], -0.6


# ─── El riu: una textura vista des de dalt (x, z), que s'anima ───────────────
XT0, XT1, ZT0, ZT1 = -700, 1500, 150, 1500         # la zona que cobreix la textura (unitats del món = px)


def _periodic(h, w, escala, seed):
    """Soroll suau i periòdic (es repeteix a la vora: per a l'aigua que corre en bucle)."""
    rng = np.random.default_rng(seed)
    a = rng.standard_normal((h, w))
    fy = np.fft.fftfreq(h)[:, None]
    fx = np.fft.fftfreq(w)[None, :]
    filt = np.exp(-((fx * escala) ** 2 + (fy * escala * 0.35) ** 2) * 6)
    n = np.real(np.fft.ifft2(np.fft.fft2(a) * filt))
    n = np.clip((n - n.mean()) / n.std() * 0.2 + 0.5, 0, 1)
    return n.astype(np.float32)


@functools.lru_cache(maxsize=None)
def _sorolls():
    return (_periodic(512, 512, 40, 1), _periodic(512, 512, 12, 2), _periodic(512, 512, 90, 3))


NFRAMES = 24                                        # el riu, lent: el soroll fa la volta (512) en 24 fotogrames


@functools.lru_cache(maxsize=None)
def tex_riu(frame=0, mati=False, baixa=False):
    """L'aigua vista des de dalt. Corre de dreta a esquerra (i una mica cap a la càmera): les vetes s'estiren en el
    sentit del corrent; avall de la resclosa, l'escuma (molta, si és crescut); més clara cap al fons (el cel s'hi
    reflecteix). `frame`: el desplaçament de l'aigua (bucle de NFRAMES)."""
    w, h = XT1 - XT0, ZT1 - ZT0
    zz, xx = np.mgrid[0:h, 0:w].astype(np.float32)
    x, z = xx + XT0, ZT1 - zz
    n1, n2, n3 = _sorolls()
    # coordenades del corrent (u al llarg, v de través), que avancen amb el fotograma
    fu, fv = -0.97, -0.25
    u = x * fu + z * fv
    v = -x * fv + z * fu
    vel = 0.0 if mati else 512 / NFRAMES
    iu = ((u * 0.9 + frame * vel) % 512).astype(int)
    iv = ((v * 2.6) % 512).astype(int)
    iu2 = ((u * 2.2 + frame * vel * 2) % 512).astype(int)
    iv2 = ((v * 5.0) % 512).astype(int)
    vetes = n1[iv, iu]
    fines = n2[iv2, iu2]
    # quin costat de la resclosa: d > 0 avall (cap a la càmera)
    d = (x - RESC0[0]) * RN[0] + (z - RESC0[2]) * RN[2]
    tr = ((x - RESC0[0]) * RU[0] + (z - RESC0[2]) * RU[2]) / RL
    dins_resc = (tr > -0.05) & (tr < 1.05)
    lv = 4.3 + (z - 186) / 900 * 2.2                   # el reflex del cel, més clar al fons
    if mati:
        lv = lv + 0.6 + (vetes - 0.5) * 0.8 + (fines - 0.5) * 0.4
        lv += np.where((fines > 0.62), 0.9, 0)        # els reflexos del sol, petits
        return Image.fromarray(tramat(lv, TER), 'RGBA')
    lv = lv + (vetes - 0.5) * 3.2 + (fines - 0.5) * 1.6
    lv -= np.where(d < 0, 0.6, 0)                      # (a dalt de la resclosa, l'aigua és més quieta i fosca)
    img = tramat(lv, TER)
    # l'escuma: avall de la resclosa (es dissol riu avall), i les crestes del riu crescut
    esc_resc = np.where(dins_resc & (d > 0), np.exp(-np.maximum(d, 0) / (60 if not baixa else 14)), 0)
    if baixa:
        esc_resc *= 0.35
    crestes = np.clip((vetes - 0.68) * 4, 0, 1) * (0.5 if d.mean() else 0.5)
    esc = esc_resc * (0.55 + fines * 0.9) + crestes * fines * 0.9
    b = np.tile(np.array([[0, 8, 2, 10], [12, 4, 14, 6], [3, 11, 1, 9], [15, 7, 13, 5]]) / 16, (h // 4 + 1, w // 4 + 1))[:h, :w]
    m = esc > 0.35 + b * 0.4
    lve = 3.0 + esc * 2.6 + (fines - 0.5) * 1.2
    enganxa(img, tramat(lve, ESCUMA), m)
    return Image.fromarray(img, 'RGBA')


@functools.lru_cache(maxsize=None)
def tex_cascada(frame=0, baixa=False, mati=False):
    """La cara d'avall de la resclosa: l'aigua que hi cau per sobre (vetes que baixen) i el gruix de pedra molla.
    1 unitat = 1 px; s al llarg de la resclosa (RL), t cap avall des del coronament (fins a 40)."""
    w, h = int(RL), 40
    tt, ss = np.mgrid[0:h, 0:w].astype(np.float32)
    n1, n2, _ = _sorolls()
    # la pedra (carreus de gres, molls)
    lvp, _ = nivells_carreus(w, h, 3.6, fila=(10, 14), ample=(18, 30), seed=71, relleu=0.5)
    img = tramat(lvp, GRES)
    if mati or baixa:
        caiguda = Y_RIU - Y_CRESTA if mati else -1
    else:
        caiguda = 1
    if caiguda > 0 or mati:
        vel = 0 if mati else 512 / NFRAMES
        iv = ((tt * 2.0 - frame * vel) % 512).astype(int)
        iu = ((ss * 3.0) % 512).astype(int)
        vet = n1[iu, iv]
        lv = 2.2 + (vet - 0.5) * 3.4 + tt * 0.05
        m = np.ones((h, w), bool)
        cap = tramat(lv, ESCUMA)
        if mati:
            cap = tramat(lv + 4.6, AIGUA)
        enganxa(img, cap, m)
    else:
        # l'aigua baixa: només rajolins i la pedra molla, fosca
        a = np.asarray(img).copy()
        a[..., :3] = (a[..., :3] * 0.7).astype(np.uint8)
        img = a
        iu = ((ss * 3.0) % 512).astype(int)
        raj = (n2[iu, (tt * 0.5).astype(int) % 512] > 0.72)
        enganxa(img, tramat(np.full((h, w), 4.0) + tt * 0.02, ESCUMA), raj)
    return Image.fromarray(np.asarray(img).astype(np.uint8), 'RGBA')


# ─── Textures del pont i del molí ────────────────────────────────────────────
TS = 1


@functools.lru_cache(maxsize=None)
def tex_pont():
    """La cara de davant del pont, de cara: carreus de gres rosat i ocre, les dovelles dels arcs, l'ampit amb la seva
    cornisa, les taques d'humitat a l'arrencada. 1 unitat = 1 px; s de PONT_S[0] a PONT_S[1], y de -60 a 300."""
    s0, s1 = PONT_S
    w, h = s1 - s0, 360
    yy, xx = np.mgrid[0:h, 0:w].astype(np.float32)
    s, y = xx + s0, 300 - yy
    lv, _ = nivells_carreus(w, h, 5.0, fila=(10, 14), ample=(18, 34), seed=61, relleu=0.55, gra=1.0)
    # les dovelles dels arcs (llargues, radials)
    for sc, r, ya in ARCS:
        rr = np.hypot(s - sc, y - ya)
        ang = np.arctan2(y - ya, s - sc)
        m = (rr >= r) & (rr < r + 22) & (y >= ya)
        nd = np.floor(ang / (math.pi / max(9, int(r / 7))))
        tone = 5.3 + (np.sin(nd * 12.9898) * 43758.5453 % 1 - 0.5) * 1.0
        junta = np.abs(ang - (nd + 0.5) * math.pi / max(9, int(r / 7))) > math.pi / max(9, int(r / 7)) * 0.44
        val = tone - junta * 1.6 + (rr > r + 20.5) * -1.4 + (rr < r + 1.5) * 0.8
        lv[m] = val[m]
    # l'ampit: la cornisa (una filada que sobresurt, més clara) i les pedres de dalt
    top = 262 - 0.34 * np.abs(s - 20)
    mc = (y >= top - 4) & (y < top)
    lv[mc] = 6.6 - (y[mc] - (top[mc] - 4)) * 0.2
    lv[(y >= top - 6) & (y < top - 4)] = 3.2              # l'ombra de la cornisa
    mp = (y >= top) & (y < top + 22)
    lv[mp & (y >= top + 19)] = 6.8                         # la coberta de l'ampit
    # la humitat: fosca a l'arrencada dels arcs i a prop de l'aigua; verdet
    hum = np.clip((40 - (y + 10)) / 60, 0, 1)
    lv -= hum * 1.2
    alpha = y < top + 22
    img = tramat(lv, GRES, alpha)
    verd = (y < 10) & (fbm_np(w, h, 6, 66, 3) > 0.62) & alpha
    a = img.astype(np.float32)
    a[verd, :3] = a[verd, :3] * np.array([0.72, 0.9, 0.7])
    return Image.fromarray(a.astype(np.uint8), 'RGBA')


def _forat_arcs(s, y):
    """Cert si (s, y) de la cara del pont és dins un arc (on no hi ha pedra)."""
    for sc, r, ya in ARCS:
        if abs(s - sc) < r and (y < ya or math.hypot(s - sc, y - ya) < r):
            return True
    return False


@functools.lru_cache(maxsize=None)
def tex_moli():
    """El molí, de lluny: la façana de paredat, la porta, les dues boques de sota per on surt l'aigua, la finestra."""
    w, h = 140, 110
    yy, xx = np.mgrid[0:h, 0:w].astype(np.float32)
    s, y = xx, h - yy
    lv = np.asarray(_paredat_np(w, h, 4.8, 61))
    img = tramat(lv, TOSCA)
    for bx in (34, 74):                            # les boques del carcabà
        m = (np.abs(s - bx) < 12) & ((y < 12) | (np.hypot(s - bx, y - 12) < 12))
        enganxa(img, tramat(np.full((h, w), 0.6) + y * 0.03, FERRO), m)
    m = (np.abs(s - 112) < 9) & (y > 30) & (y < 62)
    enganxa(img, tramat(np.full((h, w), 2.4) + ((s - 112) % 6 < 1) * -1, FUSTA), m)
    m = (np.abs(s - 60) < 7) & (y > 72) & (y < 90)
    enganxa(img, tramat(np.full((h, w), 0.8), FERRO), m)
    return Image.fromarray(img, 'RGBA')


def _paredat_np(w, h, base, seed):
    from hd640.rooms.placa_pont_comu import nivells_paredat
    return nivells_paredat(w, h, base, mida=(5, 9), seed=seed)


# ─── Superfícies procedurals ────────────────────────────────────────────────
_NT = fbm_np(1800, 1600, 30, 81, 4)
_NT2 = fbm_np(1800, 1600, 7, 82, 3)


def _nt(x, z, a=None):
    a = _NT if a is None else a
    return float(a[min(1599, max(0, int(z) + 300)), min(1799, max(0, int(x) + 700))])


HORTS = [(-420, -40, -120, 64, 0), (-110, 150, -120, 70, 1), (160, 330, -120, 42, 2)]   # x0, x1, z0, z1, mena


def _hort(x, z):
    """→ (mena, s, t) si (x, z) és dins una feixa (s, t des del seu cantó), o None."""
    for x0, x1, z0, z1, k in HORTS:
        if x0 <= x < x1 and z0 <= z < z1:
            return k, x - x0, z - z0, z1 - z0
    return None


def _terra_lvl(mati):
    def L(s, t, P):
        x, z = P[0], P[2]
        n, g = _nt(x, z), _nt(x, z, _NT2)
        h = _hort(x, z)
        if h is not None:
            k, a, b, hz = h
            if a < 5 or b > hz - 5 or b < 3:
                return 4.4 + (g - 0.5) * 1.6                        # el marge de pedra i herba
            solc = (b % 14)
            if k == 1:
                solc = (a % 16)
            v = 3.2 + (n - 0.5) * 1.0
            if solc < 4:
                v -= 1.2                                            # el solc
            elif solc > 9:
                v += 0.6
            return -100 + v                                         # (es pinta amb la rampa dels horts)
        v = 4.8 + (n - 0.5) * 1.8 + (g - 0.5) * 1.6
        # el camí que ve de l'esquerra i baixa cap a la riba
        cami = abs(z - (120 + 0.18 * x)) < 22 and x < 260
        if cami:
            v -= 0.6
            return -200 + v + (g - 0.5) * 0.8
        if z > VORA_Z - 16 and x < 430:
            v -= (z - VORA_Z + 16) / 16 * 0.8                       # la vora, més fosca (fang)
        return v + (0.6 if mati else 0)
    return L


class _Terra:
    """El terra de la riba: herba (GESPA), però els horts i el camí amb la seva rampa (nivells marcats −100, −200)."""

    def __init__(self, mati):
        self.L = _terra_lvl(mati)

    def __call__(self, s, t, P):
        return self.L(s, t, P)


def _pinta_terra(e, mati):
    """La riba i la terra de la dreta (fins al molí), en tres passades: herba, horts i camí."""
    L = _terra_lvl(mati)

    def forma(s, t):
        x, z = -900 + s, 900 - t
        return not al_riu_o_marge(x, z)
    P0, P1, P2, P3 = (-900, 0, 900), (1400, 0, 900), (1400, 0, -200), (-900, 0, -200)
    e.quad('riba', P0, P1, P2, P3, ramp=GESPA, lvl=lambda s, t, P: L(s, t, P) if L(s, t, P) > -50 else -9,
           forma=forma)
    e.quad('riba', (-900, 0.2, 900), (1400, 0.2, 900), (1400, 0.2, -200), (-900, 0.2, -200), ramp=HORT,
           lvl=lambda s, t, P: L(s, t, P) + 100,
           forma=lambda s, t: _hort(-900 + s, 900 - t) is not None)
    e.quad('riba', (-900, 0.3, 900), (1400, 0.3, 900), (1400, 0.3, -200), (-900, 0.3, -200), ramp=HORT,
           lvl=lambda s, t, P: L(s, t, P) + 200 + 1.6,
           forma=lambda s, t: (abs((900 - t) - (120 + 0.18 * (-900 + s))) < 22 and (-900 + s) < 260 and
                               _hort(-900 + s, 900 - t) is None))


def _plantes(cv, e, mati):
    """Les cols i els porros dels horts: petits monticles verds en files (en pantalla, a l'escala de cada lloc)."""
    for x0, x1, z0, z1, k in HORTS:
        if k == 1:
            continue
        z = z0 + 8
        while z < z1 - 6:
            x = x0 + 10
            while x < x1 - 6:
                P = (x + (hr(int(x), int(z), 3) - 0.5) * 4, 0, z)
                u, v, _ = CAM.projecta(P)
                kk = CAM.escala(P)
                if 0 <= u < W and 0 <= v <= BOTTOM:
                    r = (5.0 if k == 0 else 3.4) * kk
                    for yy in range(int(v - r * 1.3), int(v) + 1):
                        for xx in range(int(u - r), int(u + r) + 1):
                            dx, dy = (xx - u) / r, (yy - v) / (r * 1.3)
                            if dx * dx + (dy + 0.4) ** 2 < 0.65 and 0 <= xx < W and 0 <= yy <= BOTTOM:
                                cv.put(xx, yy, GESPA, 4.4 - dy * 1.6 - dx * 0.6 + (0.6 if mati else 0)
                                       + (hr(xx, yy, 5) - 0.5), lit=0)
                x += 14 if k == 0 else 9
            z += 14


# ─── L'escena ────────────────────────────────────────────────────────────────

def _fons(cv, e, mati):
    """El cel, la muntanya, i l'altra riba (cases de teula, arbres): es veu per sobre i a través del pont."""
    cel_trencat(cv, 0, W - 1, 0, 120, 70, seed=12 if not mati else 13, mati=mati, sol=(560, -40) if not mati else None)
    silueta_muntanyes(cv, 0, W - 1, 58, 46, LLUNY, 2.8 if not mati else 3.4, seed=14, rug=0.008, y1=130)
    # la muntanya de prop, amb bosc (verd fosc i blau)
    for x in range(W):
        top = 70 - 26 * fbm(x * 0.012, 0.3, 15, 4) + (x / W) * -10
        for y in range(int(top), 130):
            cv.put(x, y, FULLA, 2.4 + (fbm(x * 0.08, y * 0.08, 16) - 0.5) * 2.2 - (y - top) * 0.01 +
                   (0.4 if mati else 0), lit=0)
    # l'altra riba, a terra
    e.quad('lluny', (-3000, 0, 4000), (4000, 0, 4000), (4000, 0, 980), (-3000, 0, 980), ramp=GESPA,
           lvl=lambda s, t, P: 3.6 + (_nt(P[0] * 0.3, P[2] * 0.3) - 0.5) * 2)
    # les cases de l'altra riba (de lluny a prop)
    cases = [(-500, -260, 1300, 1460, 200), (-220, 60, 1240, 1400, 170), (100, 320, 1300, 1440, 230),
             (380, 620, 1180, 1330, 190), (660, 900, 1120, 1260, 240), (-760, -540, 1150, 1300, 160),
             (-40, 160, 1050, 1150, 120), (240, 420, 1030, 1130, 140)]
    for i, (x0, x1, z0, z1, h) in enumerate(cases):
        e.caixa(f'cases{i}', x0, x1, 0, h, z0, z1, TOSCA, 4.2, cares={
            'davant': {'ramp': TOSCA if i % 3 else GRES, 'lvl': lambda s, t, P, i=i: (
                (0.8 if (s % 46) < 12 and 20 < (t % 70) < 44 else 4.6 + (0.4 if mati else 0)) +
                (hr(int(s // 9), int(t // 6), i) - 0.5) * 0.8)},
            'esquerra': {'ramp': TOSCA, 'lvl': 3.4}, 'dreta': {'ramp': TOSCA, 'lvl': 3.2}})
        e.quad(f'cases{i}', (x0 - 10, h - 2, z0 - 12), (x1 + 10, h - 2, z0 - 12), (x1 + 10, h + 44, (z0 + z1) / 2),
               (x0 - 10, h + 44, (z0 + z1) / 2), ramp=TEULA,
               lvl=lambda s, t, P: 3.8 + (0.8 if (s % 9) < 4.5 else 0), dues_cares=True)
    # arbres a l'altra riba: capçades verdes (i un xiprer)
    for x, z, r in ((-300, 1100, 70), (180, 1000, 60), (520, 1040, 80), (820, 1000, 70), (-620, 1050, 60)):
        k = CAM.escala((x, 0, z))
        u, v, _ = CAM.projecta((x, 0, z))
        capcada(cv, u, v - r * 1.4 * k, r * k * 1.1, r * k, FULLA, 3.8 + (0.5 if mati else 0), seed=int(x) % 97,
                llum=(0.7, -0.6) if not mati else (-0.8, -0.4))


def _pont(e, mati):
    """El pont: l'intradós dels arcs (de dins), l'aigua de sota, i la cara de davant amb els forats dels arcs."""
    # l'intradós de cada arc: franges de volta, de la cara de davant a la de darrere
    for sc, r, ya in ARCS:
        n = 18
        for i in range(n):
            a0, a1 = math.pi * i / n, math.pi * (i + 1) / n
            y0_, y1_ = ya + math.sin(a0) * r, ya + math.sin(a1) * r
            s0_, s1_ = sc + math.cos(a0) * r, sc + math.cos(a1) * r
            # la llum: les franges de dalt, fosques; les de la dreta (de cara a la càmera girada), una mica més clares
            lvl = 2.0 + math.cos((a0 + a1) / 2) * 0.6 - math.sin((a0 + a1) / 2) * 0.6
            e.quad('intrados', pont_pt(s1_, y1_, PONT_G), pont_pt(s0_, y0_, PONT_G), pont_pt(s0_, y0_, 0),
                   pont_pt(s1_, y1_, 0), ramp=GRES, dues_cares=True,
                   lvl=lambda s, t, P, lvl=lvl: lvl + (0.5 if int(s // 7) % 2 else 0) * (1 if int(t) % 12 < 11 else -2))
        # els brancals de dins (sota l'arrencada)
        for sd in (-1, 1):
            e.quad('intrados', pont_pt(sc + sd * r, ya, PONT_G), pont_pt(sc + sd * r, ya, 0),
                   pont_pt(sc + sd * r, -60, 0), pont_pt(sc + sd * r, -60, PONT_G), ramp=GRES, dues_cares=True,
                   lvl=2.4 - sd * 0.4)
    # la cara de davant
    s0, s1 = PONT_S
    e.quad('pont', pont_pt(s0, 300), pont_pt(s1, 300), pont_pt(s1, -60), pont_pt(s0, -60),
           tex=(tex_pont(), (0, 0, s1 - s0, 360), 1),
           forma=lambda s, t: not _forat_arcs(s0 + s, 300 - t))
    # el tallamar: un esperó apuntat a la pila de l'esquerra de l'arc gran
    sp = (ARCS[0][0] - ARCS[0][1] + ARCS[1][0] + ARCS[1][1]) / 2
    base = pont_pt(sp, 0)
    tip = (base[0] + PN[0] * 46, 0, base[2] + PN[2] * 46)
    l_, r_ = pont_pt(sp - 30, 0), pont_pt(sp + 30, 0)
    for A, B, lvl in ((l_, tip, 4.6), (tip, r_, 3.4)):
        e.quad('tallamar', _y(A, 70), _y(B, 40), _y(B, -60), _y(A, -60), ramp=GRES, dues_cares=True,
               lvl=lambda s, t, P, lvl=lvl: lvl + (0.6 if int(t) % 13 < 2 else 0) - max(0, P[1] < 0) * 1.0)
    e.quad('tallamar', _y(l_, 70), _y(r_, 70), _y(tip, 40), _y(tip, 40.1), ramp=GRES, lvl=5.2, dues_cares=True)


def _riu(e, frame, mati, baixa, sid='riu'):
    """L'aigua: a dalt de la resclosa (fins al pont i més enllà) i a sota (fins a la nostra riba)."""
    T = tex_riu(frame, mati, baixa)
    yd = Y_BAIXA if baixa else Y_RIU
    if mati:
        yd = Y_RIU - 4

    def tex(z0, z1):
        return (T, (0, ZT1 - z1, XT1 - XT0, ZT1 - z0), 1)

    def dalt(s, t):                                # a dalt de la resclosa (riu amunt)
        x, z = XT0 + s, ZT1 - t
        return ((x - RESC0[0]) * RN[0] + (z - RESC0[2]) * RN[2]) < RESC_G and al_riu(x, z)

    def avall(s, t):
        x, z = XT0 + s, ZT1 - t
        return ((x - RESC0[0]) * RN[0] + (z - RESC0[2]) * RN[2]) >= 0 and al_riu(x, z)
    e.quad(sid, (XT0, yd, ZT1), (XT1, yd, ZT1), (XT1, yd, ZT0), (XT0, yd, ZT0), tex=tex(ZT0, ZT1), forma=dalt)
    e.quad(sid, (XT0, Y_AVALL, ZT1), (XT1, Y_AVALL, ZT1), (XT1, Y_AVALL, ZT0), (XT0, Y_AVALL, ZT0),
           tex=tex(ZT0, ZT1), forma=avall)


def _resclosa(e, frame, mati, baixa, sobre_obert=False, serra=True):
    """La resclosa: el coronament de pedra, la cara d'avall (amb l'aigua que hi cau), el sobreeixidor i la
    comporta amb el seu pilar; la serra encallada a la comporta."""
    A, B = resc_pt(0, 0), resc_pt(1, 0)
    Ad, Bd = resc_pt(0, RESC_G), resc_pt(1, RESC_G)
    # el coronament (pedra), amb el forat del sobreeixidor
    ts0, ts1 = T_SOBRE - SOBRE_W / 2 / RL, T_SOBRE + SOBRE_W / 2 / RL
    e.quad('resclosa', _y(A, Y_CRESTA), _y(B, Y_CRESTA), _y(Bd, Y_CRESTA), _y(Ad, Y_CRESTA), ramp=GRES,
           lvl=lambda s, t, P: 4.8 + (0.6 if int(s // 18) % 2 else 0) - (1.6 if int(s) % 18 < 1 else 0) +
           (0.5 if t > RESC_G - 3 else 0), forma=lambda s, t: not (ts0 * RL < s < ts1 * RL))
    # la cara d'avall (cap a la càmera), de la cresta fins a l'aigua d'avall
    e.quad('cascada', _y(Ad, Y_CRESTA), _y(Bd, Y_CRESTA), _y(Bd, Y_CRESTA - 40), _y(Ad, Y_CRESTA - 40),
           tex=(tex_cascada(frame, baixa, mati), (0, 0, int(RL), 40), 1),
           forma=lambda s, t: not (ts0 * RL < s < ts1 * RL) or t > 30)
    # el sobreeixidor: la post de fusta encaixada al forat (o, oberta, l'aigua que hi raja)
    S0, S1 = resc_pt(ts0, RESC_G * 0.4), resc_pt(ts1, RESC_G * 0.4)
    if not sobre_obert:
        e.quad('sobreeixidor', _y(S0, Y_CRESTA + 4), _y(S1, Y_CRESTA + 4), _y(S1, Y_CRESTA - 26), _y(S0, Y_CRESTA - 26),
               ramp=FUSTA, dues_cares=True,
               lvl=lambda s, t, P: 4.2 + (-1.4 if int(t) % 9 < 1 else 0) + (0.6 if t < 2 else 0) - (s > SOBRE_W - 3) * 1.2)
        for sd in (0.15, 0.85):                    # les dues tanques de ferro que la subjecten
            Q = _add(S0, (S1[0] - S0[0], 0, S1[2] - S0[2]), sd)
            e.caixa('sobreeixidor', Q[0] - 1.6, Q[0] + 1.6, Y_CRESTA - 4, Y_CRESTA + 6, Q[2] - 6, Q[2] + 2, FERRO, 3.4)
    else:
        # l'aigua que raja pel forat, un doll blanc
        e.quad('sobreeixidor', _y(S0, Y_CRESTA - 2), _y(S1, Y_CRESTA - 2), _y(_add(S1, RN, 16), Y_AVALL + 1),
               _y(_add(S0, RN, 16), Y_AVALL + 1), ramp=ESCUMA, dues_cares=True,
               lvl=lambda s, t, P: 3.4 + (hr(int(s // 2), int(t // 3), frame) - 0.5) * 2.4 + t * 0.06)
    # el pilar de la comporta (pedra), més alt que la resclosa
    c = resc_pt(T_COMP, RESC_G / 2)
    ang = math.atan2(RU[2], RU[0])
    e.caixa_girada('comporta', c[0], c[2], 46, RESC_G + 22, 40, -ang, GRES, 4.4, y0=Y_CRESTA - 30, cares={
        'dalt': {'ramp': GRES, 'lvl': 6.0}, 'davant': {'ramp': GRES, 'lvl': lambda s, t, P: 3.6 + (0.6 if int(t) % 10 < 1 else 0)},
        'dreta': {'ramp': GRES, 'lvl': 4.8}, 'esquerra': {'ramp': GRES, 'lvl': 4.0}})
    # la vàlvula: dos muntants de fusta i la post que puja i baixa (al costat del rec, cap a la dreta)
    g = _add(c, RU, 30)
    for sd in (-13, 13):
        q = _add(g, RN, sd)
        e.caixa('comporta', q[0] - 3.4, q[0] + 3.4, Y_CRESTA - 20, 56, q[2] - 3.4, q[2] + 3.4, FUSTA, 3.6,
                cares={'davant': {'ramp': FUSTA, 'lvl': 3.4}, 'esquerra': {'ramp': FUSTA, 'lvl': 4.4}})
    q0, q1 = _add(g, RN, -13), _add(g, RN, 13)
    e.quad('comporta', _y(q0, 56), _y(q1, 56), _y(q1, 48), _y(q0, 48), ramp=FUSTA, lvl=4.2, dues_cares=True)
    e.quad('comporta', _y(q0, 22), _y(q1, 22), _y(q1, Y_CRESTA - 18), _y(q0, Y_CRESTA - 18), ramp=FUSTA,
           dues_cares=True, lvl=lambda s, t, P: 3.8 + (-1.2 if int(s) % 6 < 1 else 0) - t * 0.02)
    # el cargol (l'eix) de la comporta
    e.cable('comporta', [(g[0], 22, g[2]), (g[0], 74, g[2])], FERRO, 3.2, gruix=2.6)
    for i in range(8):                            # la roda per pujar-la i baixar-la
        a0, a1 = 2 * math.pi * i / 8, 2 * math.pi * (i + 1) / 8
        e.cable('comporta', [(g[0] + math.cos(a0) * 9, 70, g[2] + math.sin(a0) * 9),
                             (g[0] + math.cos(a1) * 9, 70, g[2] + math.sin(a1) * 9)], FERRO, 3.6, gruix=2.0)
    # la serra encallada a la boca de la comporta: sota l'aigua, només una lluïssor; a l'aire, les dents
    if serra:
        sP = _add(_add(g, RN, -4), RU, -6)
        ys = Y_CRESTA - 13
        visible = baixa
        e.quad('serra', (sP[0] - RU[0] * 20, ys + 6, sP[2] - RU[2] * 20), (sP[0] + RU[0] * 14, ys + 3, sP[2] + RU[2] * 14),
               (sP[0] + RU[0] * 14, ys - 2, sP[2] + RU[2] * 14), (sP[0] - RU[0] * 20, ys - 1, sP[2] - RU[2] * 20),
               ramp=FERRO, dues_cares=True,
               lvl=lambda s, t, P: (5.4 if visible else 3.0) + (1.0 if int(s) % 3 == 0 and t > 3.5 else 0) - t * 0.1)


def _rec(e, ple, mati):
    """El rec: el canal de pedra que surt de la comporta, travessa fins a la riba de la dreta i se'n va al molí. Buit,
    el fons de fang i pedres; ple, l'aigua."""
    pts = REC
    for i, (A, B) in enumerate(zip(pts, pts[1:])):
        dx, dz = B[0] - A[0], B[2] - A[2]
        n = math.hypot(dx, dz)
        nx, nz = -dz / n * REC_W / 2, dx / n * REC_W / 2
        a1, a2 = (A[0] + nx, 0, A[2] + nz), (A[0] - nx, 0, A[2] - nz)
        b1, b2 = (B[0] + nx, 0, B[2] + nz), (B[0] - nx, 0, B[2] - nz)
        alt = 0 if i == 0 else 6               # (el primer tram, el que travessa el riu, arran d'aigua)
        base = Y_AVALL if i == 0 else -8
        # els dos murets del canal i el fons
        for P, Q, lvl in ((a2, b2, 4.6), (a1, b1, 3.6)):
            e.quad('rec', _y(P, alt), _y(Q, alt), _y(Q, base), _y(P, base), ramp=GRES, dues_cares=True,
                   lvl=lambda s, t, P_, lvl=lvl: lvl + (0.7 if t < 2 else 0) - (1.2 if int(s) % 16 < 1 else 0))
        e.quad('rec', _y(a1, alt), _y(b1, alt), _y(b1, alt - 1), _y(a1, alt - 1), ramp=GRES, lvl=5.6, dues_cares=True)
        mig = lambda k, P, Q: (P[0] + (Q[0] - P[0]) * k, 0, P[2] + (Q[2] - P[2]) * k)   # noqa: E731
        f1, f2 = mig(0.18, a1, a2), mig(0.82, a1, a2)
        g1, g2 = mig(0.18, b1, b2), mig(0.82, b1, b2)
        if ple:
            e.quad('rec_aigua', _y(f1, alt - 2), _y(g1, alt - 2), _y(g2, alt - 2), _y(f2, alt - 2), ramp=AIGUA,
                   dues_cares=True,
                   lvl=lambda s, t, P_: 5.0 + (0.8 if mati else 0) + (hr(int(s // 6), int(t // 2), 9) - 0.5) * 1.4)
        else:
            e.quad('rec_fons', _y(f1, alt - 7), _y(g1, alt - 7), _y(g2, alt - 7), _y(f2, alt - 7), ramp=HORT,
                   dues_cares=True,
                   lvl=lambda s, t, P_: 3.0 + (hr(int(s // 3), int(t // 3), 8) - 0.5) * 1.8)


def _moli(e, mati):
    """El molí, lluny a la dreta: la caixa de paredat amb la teulada, a la vora del rec."""
    x0, z0 = MOLI
    e.caixa('moli', x0, x0 + 140, 0, 110, z0, z0 + 90, TOSCA, 4.0, cares={
        'davant': {'tex': (tex_moli(), (0, 0, 140, 110), 1)},
        'esquerra': {'ramp': TOSCA, 'lvl': lvl_paredat(3.6 if not mati else 4.6, 8, 62)}})
    e.quad('moli', (x0 - 10, 108, z0 - 12), (x0 + 150, 108, z0 - 12), (x0 + 150, 150, z0 + 45), (x0 - 10, 150, z0 + 45),
           ramp=TEULA, lvl=lambda s, t, P: 3.8 + (0.8 if (s % 9) < 4.5 else 0), dues_cares=True)
    e.quad('moli', (x0 - 10, 150, z0 + 45), (x0 - 10, 108, z0 + 102), (x0 - 10, 108, z0 - 12), (x0 - 10, 150, z0 + 45.1),
           ramp=TOSCA, lvl=3.6, dues_cares=True)


def _barca(e, P, mati, calafatada=False, enfonsada=True, amarrada=True):
    """La barca d'en Joanet: un buc de taulons de proa apuntada i popa plana, amb la borda que puja cap a la proa.
    Mig enfonsada, plena d'aigua i escorada (només en surt la borda); calafatada, sura, amb la resina que brilla a
    les juntes. A dins, el salabre."""
    x, z, ang = P
    c, s_ = math.cos(ang), math.sin(ang)
    esc = 0.12 if enfonsada else 0.0               # (enfonsada, escorada cap a la riba)
    yb = (Y_AVALL - 13) if enfonsada else (Y_AVALL - 7)

    def G(lx, y, lz):
        y = y + lz * esc
        return (x + lx * c - lz * s_, y, z + lx * s_ + lz * c)
    Lp, Lq, B, H = -58, 62, 19, 22                 # popa, proa, mig ample, alt
    N = 10
    secs = []
    for i in range(N + 1):
        lx = Lp + (Lq - Lp) * i / N
        k = (lx - Lp) / (Lq - Lp)
        b = B * (0.82 + 0.5 * k - 0.32 * k * k) if k < 0.7 else B * max(0.0, 1 - (k - 0.7) / 0.3) ** 0.8
        b = max(0.6, b)
        h = H + 7 * k ** 2.4 + 2 * (1 - k) ** 3
        secs.append((lx, b, h))

    def junta(base):
        return lambda s, t, P_: (base + (-1.4 if int(t) % 6 < 1 else 0) +
                                 (3.2 if calafatada and int(t) % 6 < 1 else 0) + (hr(int(s // 5), 1) - 0.5) * 0.6)
    # el costat de dins de l'altra banda (es veu per sobre de la borda de davant)
    for (l0, b0, h0), (l1, b1, h1) in zip(secs, secs[1:]):
        e.quad('barca', G(l0, yb + h0, b0), G(l1, yb + h1, b1), G(l1, yb + 2, b1 * 0.55), G(l0, yb + 2, b0 * 0.55),
               ramp=FUSTA, lvl=lambda s, t, P_: 2.6 + (-1 if int(t) % 6 < 1 else 0), dues_cares=True)
    # el fons de dins: aigua tèrbola (enfonsada) o els taulons i la resina (calafatada)
    for (l0, b0, h0), (l1, b1, h1) in zip(secs, secs[1:]):
        yy = yb + (H - 7 if enfonsada else 3)
        f = 0.55 if not enfonsada else 0.85
        if enfonsada:
            e.quad('barca', G(l0, yy, b0 * f), G(l1, yy, b1 * f), G(l1, yy, -b1 * f), G(l0, yy, -b0 * f), ramp=AIGUA,
                   lvl=3.6 + (0.8 if mati else 0), dues_cares=True)
        else:
            e.quad('barca', G(l0, yy, b0 * f), G(l1, yy, b1 * f), G(l1, yy, -b1 * f), G(l0, yy, -b0 * f), ramp=FUSTA,
                   lvl=lambda s, t, P_: 3.4 + (-1.2 if int(t) % 7 < 1 else 0) + (2.4 if int(t) % 7 < 1 and calafatada else 0),
                   dues_cares=True)
    # els bancs
    for lb in (-30, 14):
        i = min(range(N + 1), key=lambda j: abs(secs[j][0] - lb))
        bb, hh = secs[i][1], secs[i][2]
        e.quad('barca', G(lb - 4, yb + hh - 5, bb), G(lb + 4, yb + hh - 5, bb), G(lb + 4, yb + hh - 5, -bb),
               G(lb - 4, yb + hh - 5, -bb), ramp=FUSTA, lvl=4.4, dues_cares=True)
    # el costat de fora (el de la càmera), de taulons, i el mirall de popa
    for (l0, b0, h0), (l1, b1, h1) in zip(secs, secs[1:]):
        e.quad('barca', G(l0, yb + h0, -b0), G(l1, yb + h1, -b1), G(l1, yb + 1, -b1 * 0.55), G(l0, yb + 1, -b0 * 0.55),
               ramp=FUSTA, lvl=junta(4.0), dues_cares=True)
    l0, b0, h0 = secs[0]
    e.quad('barca', G(l0, yb + h0, b0), G(l0, yb + h0, -b0), G(l0, yb + 1, -b0 * 0.55), G(l0, yb + 1, b0 * 0.55),
           ramp=FUSTA, lvl=junta(3.2), dues_cares=True)
    # la borda (un llistó clar) de les dues bandes
    e.cable('barca', [G(l, yb + h + 1, -b) for l, b, h in secs], FUSTA, 5.4, gruix=2.2)
    e.cable('barca', [G(l, yb + h + 1, b) for l, b, h in secs], FUSTA, 4.4, gruix=1.8)
    # el salabre (el cèrcol, el mànec i la xarxa), a dins
    yr = yb + H + 2
    e.cable('barca', [G(-34, yr - 4, 2), G(4, yr + 10, 6)], FUSTA, 4.6, gruix=1.8)
    for i in range(12):
        a0, a1 = 2 * math.pi * i / 12, 2 * math.pi * (i + 1) / 12
        e.cable('barca', [G(14 + math.cos(a0) * 10, yr + 10 + math.sin(a0) * 4, 6 + math.sin(a0) * 7),
                          G(14 + math.cos(a1) * 10, yr + 10 + math.sin(a1) * 4, 6 + math.sin(a1) * 7)],
                CANEM, 4.0, gruix=1.3)
    # l'amarra: la corda fins a un pal clavat a la riba
    if amarrada:
        pal = (x - 44, 0, vora(x - 44) - TALUS - 4)
        e.cable('barca', [pal, (pal[0], 26, pal[2])], FUSTA, 3.4, gruix=3.0)
        e.cable('barca', [(pal[0], 20, pal[2]), ((pal[0] + G(Lp, 0, 0)[0]) / 2, 2, (pal[2] + G(Lp, 0, 0)[2]) / 2),
                          G(Lp, yb + H, 0)], CANEM, 3.4, gruix=1.4)


def _marge_lvl(mati):
    def L(s, t, P):
        y = P[1]
        v = 3.6 + (hr(int(s // 6), int(t // 4), 4) - 0.5) * 1.2 + (0.6 if mati else 0)
        if y > -6:
            return v + 1.0 + (hr(int(s // 3), 2) - 0.5) * 1.4       # l'herba que penja de dalt
        if y < -20:
            v -= 1.2                                                # el fang mullat, a tocar d'aigua
        if hr(int(s // 9), int(y // 7), 6) < 0.16:
            v += 1.4                                                # una pedra
        return v
    return L


def _marges(e, mati):
    """Els marges de terra que baixen fins a l'aigua (la nostra riba i la de la dreta): en talús, no de paret."""
    L = _marge_lvl(mati)
    xs = list(range(-900, int(BADIA[0]) + 1, 10))
    for x0, x1 in zip(xs, xs[1:]):
        e.quad('marge', (x0, 0, vora(x0) - TALUS), (x1, 0, vora(x1) - TALUS), (x1, Y_AVALL, vora(x1)),
               (x0, Y_AVALL, vora(x0)), ramp=HORT, lvl=L, dues_cares=True)
    zs = list(range(int(VORA_Z) - 8, RIBA_LLUNY + 1, 10))
    for z0, z1 in zip(zs[::-1], zs[::-1][1:]):
        e.quad('marge', (riba_dreta(z0) + TALUS, 0, z0), (riba_dreta(z1) + TALUS, 0, z1), (riba_dreta(z1), Y_AVALL, z1),
               (riba_dreta(z0), Y_AVALL, z0), ramp=HORT, lvl=L, dues_cares=True)


def escena(cv, mati=False, frame=0, baixa=False, calafatada=False, serra=True, ple=False, barca_riu=False):
    """Tot el pont, de lluny a prop (sense z-buffer: l'ordre és el de la profunditat). → l'Escena."""
    lls, amb = llums(mati)
    e = Escena(cv, CAM, lls, ambient=amb)
    _fons(cv, e, mati)
    _riu(e, frame, mati, baixa)
    _pont(e, mati)
    _moli(e, mati)
    _resclosa(e, frame, mati, baixa, sobre_obert=baixa, serra=serra)
    _rec(e, ple, mati)
    # la riba de la dreta (fins al molí) i la nostra: herba, horts i el camí; la vora de terra cap a l'aigua
    _pinta_terra(e, mati)
    _marges(e, mati)
    _plantes(cv, e, mati)
    # la barca (a la vora o, al matí empesa, a mig riu)
    if barca_riu:
        _barca(e, BARCA_RIU, mati, calafatada=True, enfonsada=False, amarrada=False)
    else:
        _barca(e, BARCA, mati, calafatada=calafatada, enfonsada=not calafatada)
    return e


def _salze(cv, mati):
    """El salze del primer pla, a la dreta: el tronc gruixut i les branques que pengen (verd groc a contrallum, en
    silueta). En pantalla. → la màscara."""
    m = np.zeros((cv.h, cv.w), bool)
    x, z = SALZE_P
    u, v, _ = CAM.projecta((x, 0, z))
    k = CAM.escala((x, 0, z))
    lv0 = 2.0 if not mati else 2.6
    # el tronc, inclinat cap a la dreta
    for yy in range(0, int(v) + 1):
        t = (v - yy) / max(1, v)
        cx = u + t * 40 * k
        amp = (24 - t * 8) * k
        for xx in range(int(cx - amp), int(cx + amp) + 1):
            if 0 <= xx < cv.w and 0 <= yy <= BOTTOM:
                cv.put(xx, yy, ESCORÇA, lv0 + (xx - cx) / amp * -0.6 + (fbm(xx * 0.3, yy * 0.08, 33) - 0.5) * 1.4,
                       lit=0)
                m[yy, xx] = True
    # les branques que pengen: cortines de fulles primes des de dalt
    import random
    rnd = random.Random(34)
    for _ in range(300):
        x0 = rnd.uniform(u - 70 * k, W + 20)
        y0 = rnd.uniform(-10, 30)
        llarg = rnd.uniform(90, 200) * (0.6 + 0.4 * min(1, (x0 - (u - 120 * k)) / (150 * k)))
        ben = rnd.uniform(-6, 6)
        for i in range(int(llarg)):
            tt = i / llarg
            xx = int(x0 + ben * tt * tt + math.sin(i * 0.15 + x0) * 1.2)
            yy = int(y0 + i)
            if 0 <= xx < cv.w and 0 <= yy <= BOTTOM:
                val = lv0 + 1.8 + tt * 2.2 + (hr(xx, yy, 35) - 0.5) * 2.0
                cv.put(xx, yy, SALZE, val, lit=0)
                m[yy, xx] = True
                if (i % 5) < 2 and xx + 1 < cv.w:
                    cv.put(xx + 1, yy, SALZE, val + 0.6, lit=0)
                    m[yy, xx + 1] = True
    # unes fulles d'herba alta a la cantonada de baix a l'esquerra
    for _ in range(40):
        x0 = rnd.uniform(-5, 70)
        h = rnd.uniform(10, 34)
        ben = rnd.uniform(-0.6, 0.6)
        for i in range(int(h)):
            xx, yy = int(x0 + ben * (i / h) ** 2 * h * 0.6), BOTTOM - i
            if 0 <= xx < cv.w:
                cv.put(xx, yy, GESPA, 1.6 + (i / h) * 1.4 + (0.6 if mati else 0), lit=0)
                m[yy, xx] = True
    return m


@functools.lru_cache(maxsize=None)
def _base(mati=False, frame=0, baixa=False, calafatada=False, serra=True, ple=False, barca_riu=False):
    cv = Canvas(light=LIGHT)
    e = escena(cv, mati, frame, baixa, calafatada, serra, ple, barca_riu)
    m = _salze(cv, mati)
    if mati:                                       # el matí: tot una mica més daurat
        a = np.asarray(cv.img).astype(np.float32)
        a[..., :3] *= np.array([1.07, 1.02, 0.9], np.float32)
        cv.img = Image.fromarray(np.clip(a, 0, 255).astype(np.uint8), 'RGBA').copy()
        cv.P = cv.img.load()
    else:                                          # la tarda grisa i verda
        a = np.asarray(cv.img).astype(np.float32)
        a[..., :3] = a[..., :3] * 0.94 + np.array([4, 8, 6], np.float32)
        cv.img = Image.fromarray(np.clip(a, 0, 255).astype(np.uint8), 'RGBA').copy()
        cv.P = cv.img.load()
    cv.rect(0, BOTTOM + 1, W - 1, cv.h - 1, [(0, 0, 0)], 0, lit=0)    # la barra de verbs: negre
    return cv.img, e, m


# ─── Fons, props i animacions ────────────────────────────────────────────────

def bg(cv):
    img, _, _ = _base()
    cv.img.paste(img)
    cv.P = cv.img.load()


def _prop_diff(base_kw=None, **kw):
    def draw(pc):
        pc.img.alpha_composite(_diff(_base(**kw)[0], _base(**(base_kw or {}))[0]))
        pc.P = pc.img.load()
    return draw


def llum_mati(pc):
    """L'acte 4: el matí net, el riu manso, la barca calafatada que sura a la vora i la comporta sense la serra.
    Tota la sala."""
    img, _, _ = _base(mati=True, calafatada=True, serra=False)
    pc.img.alpha_composite(img)
    pc.P = pc.img.load()


PROPS = {
    'aigua_baixa': _prop_diff(baixa=True),
    'barca_calafatada': _prop_diff(calafatada=True),
    'serra_treta': _prop_diff(base_kw={'baixa': True}, baixa=True, serra=False),
    'rec_ple': _prop_diff(ple=True),
    'llum_mati': llum_mati,
    'barca_corrent': _prop_diff(base_kw={'mati': True, 'calafatada': True, 'serra': False},
                                mati=True, calafatada=True, serra=False, barca_riu=True),
}


def _escuma_frames():
    """El riu que corre: l'aigua i l'escuma de la resclosa, fotograma a fotograma (només on es veu l'aigua)."""
    base, e, _ = _base()
    out = []
    for f in range(NFRAMES):
        if f == 0:
            out.append(Image.new('RGBA', base.size, (0, 0, 0, 0)))
            continue
        out.append(_diff(_base(frame=f)[0], base))
    return out


ANIMS = {'escuma': {'frames': _escuma_frames, 'frameDuration': 120}}


# ─── Capes del davant ────────────────────────────────────────────────────────

def _salze_mask(x, y):
    return bool(_base()[2][y, x])


FRONT = [{'id': 'davant', 'mask': _salze_mask, 'baseline': 999, 'zIndex': 20}]


# ─── Geometria (coordenades de sala, projectades) ────────────────────────────

def _p(x, z, y=0.0):
    u, v, _ = CAM.projecta((x, y, z))
    return round(u), round(v)


def _rect_mon(*Ps):
    pts = [CAM.projecta(P) for P in Ps]
    return (max(0, round(min(p[0] for p in pts))), max(0, round(min(p[1] for p in pts))),
            min(W - 1, round(max(p[0] for p in pts))), min(BOTTOM, round(max(p[1] for p in pts))))


# El terra on es camina (al món): el camí i la riba, des de la vora de l'aigua fins als horts; a la dreta, la riba
# que gira cap al rec (fins on hi ha l'Ermessenda) i el peu del salze.
WALK_MON = [(-260, 66), (-260, 160), (-60, VORA_Z - 12), (BADIA[0] - 6, VORA_Z - 12), (470, 214), (500, 238),
            (548, 228), (536, 190), (590, 130), (560, 70), (420, 54), (330, 44), (160, 66)]


def _poligon(pts):
    """Projecta, retalla a la sala i treu els punts repetits."""
    out = []
    for x, z in pts:
        u, v = _p(x, z)
        q = (max(0, min(W - 1, u)), min(BOTTOM - 4, v))
        if not out or q != out[-1]:
            out.append(q)
    return out[:-1] if out[0] == out[-1] else out


_WALK = _poligon(WALK_MON)
_V_FONS, _V_PROP = min(v for _, v in _WALK), max(v for _, v in _WALK)


def _escala_a(v):
    """L'escala d'un personatge amb els peus a la y de pantalla `v` (al terra)."""
    lo, hi = -300.0, 3000.0
    for _ in range(60):
        z = (lo + hi) / 2
        if CAM.projecta((300, 0, z))[1] > v:
            lo = z
        else:
            hi = z
    return CAM.escala((300, 0, (lo + hi) / 2))


_SOBRE = resc_pt(T_SOBRE, RESC_G / 2)
_COMP = resc_pt(T_COMP, RESC_G / 2)

GEOMETRIA = {
    'things': {
        'pont': {'rect': (60, 0, 600, 92), 'walk': _p(250, 150)},
        'riu': {'rect': _rect_mon((-100, Y_AVALL, 900), (420, Y_AVALL, VORA_Z + 4)), 'walk': _p(60, VORA_Z - 16)},
        'resclosa': {'rect': _rect_mon(_y(resc_pt(0.2), Y_CRESTA + 4), _y(resc_pt(0.38, RESC_G), Y_CRESTA - 30),
                                       _y(resc_pt(0.62), Y_CRESTA + 4), _y(resc_pt(0.95, RESC_G), Y_CRESTA - 30)),
                     'walk': _p(260, VORA_Z - 14)},
        'sobreeixidor': {'rect': _rect_mon(_y(resc_pt(T_SOBRE - 0.04), Y_CRESTA + 10),
                                           _y(resc_pt(T_SOBRE + 0.04, RESC_G), Y_CRESTA - 30)),
                         'walk': _p(_SOBRE[0] - 10, VORA_Z - 12)},
        'comporta': {'rect': _rect_mon(_y(_add(_COMP, RU, -24), 60), _y(_add(_COMP, RU, 40), Y_CRESTA - 30)),
                     'walk': _p(_COMP[0] - 40, VORA_Z - 12)},
        'barca': {'rect': _rect_mon((BARCA[0] - 70, 12, BARCA[1] - 20), (BARCA[0] + 70, Y_AVALL - 8, BARCA[1] + 20)),
                  'walk': _p(BARCA[0] + 10, VORA_Z - 14)},
        'rec': {'rect': _rect_mon((REC[1][0] - 20, 10, REC[1][2] - 20), (REC[3][0] + 20, -4, REC[3][2] + 20),
                                  (REC[0][0], 10, REC[0][2])),
                'walk': _p(506, 228)},
        'horts': {'rect': _rect_mon((-420, 0, 64), (330, 0, -120)), 'walk': _p(40, 70)},
        'salze': {'rect': (_p(*SALZE_P)[0] - 30, 0, W - 1, _p(*SALZE_P)[1]), 'walk': _p(560, 90)},
        'moli_lluny': {'rect': _rect_mon((MOLI[0], 150, MOLI[1]), (MOLI[0] + 140, 0, MOLI[1])),
                       'walk': _p(520, 230)},
        'cami': {'rect': (0, _p(-200, 150)[1] - 10, 30, BOTTOM - 12), 'walk': (3, _p(-170, 100)[1])},
    },
    # l'Iri arriba pel camí (de l'esquerra); en Joanet, a la vora, al costat de la barca; l'Ermessenda, a la vora del
    # rec, a la dreta
    'spawns': {'iri': _p(-40, 110), 'joanet': _p(BARCA[0] - 76, VORA_Z - 52), 'ermessenda': _p(516, 214)},
    'walkable': _WALK,
    # la tarda: el sol, tapat, alt i a la dreta: les ombres, suaus, cap a l'esquerra
    'characterShadow': {'enabled': True, 'color': '#141a14', 'alpha': 0.36, 'squash': 0.34, 'core': 0.65,
                        'light': {'x': -0.6, 'y': 0.2, 'direction': True, 'stretch': 0.35}},
    'regions': [{'id': 'perspectiva', 'active': True, 'scaleEnabled': True, 'scaleWalkSpeed': True,
                 'scaleTop': round(_escala_a(_V_FONS - 2), 3), 'scaleBottom': round(_escala_a(_V_PROP + 2), 3),
                 'points': [(0, _V_FONS - 2), (W - 1, _V_FONS - 2), (W - 1, _V_PROP + 2), (0, _V_PROP + 2)]}],
    # La llum de la sala sobre els personatges: la tarda grisa i verda (l'ambient, una mica verd), el sol tapat a la
    # dreta; al matí (`llum_mati`), el sol daurat de l'esquerra.
    'characterLights': {
        'ambient': '#c4cec4',
        'lights': [{'x': 900, 'y': -200, 'radius': 1200, 'color': '#f4f0dc', 'intensity': 0.3,
                    'whenPropHidden': 'llum_mati'},
                   {'x': -500, 'y': 120, 'radius': 1400, 'color': '#ffd8a0', 'intensity': 0.5,
                    'whenPropVisible': 'llum_mati'}],
    },
}
