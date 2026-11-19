"""
Aigua Verne — la portada (pantalla sencera de 640×360, sense barra de verbs; mida de lluny). EN 3D (hd640/tres_d.py),
a 1×; referència: docs/referencies/cinematica-portada-desert.png.

Terra-2 al capvespre de pols, vist des d'un turó: el sol baix i vermellós a l'esquerra, el cel que passa de l'ocre al
morat i les primeres estrelles. Els solcs dels camps secs fugen cap a l'horitzó. La Canonada s'alça a la dreta fins
a dalt de tot, on penja un dels dipòsits orbitals (el cilindre blanc amb la gota blava).

La Cantimplora (el model canònic de cantimplora_comu.py), aparcada a l'esquerra, en 3/4, amb la proa cap a la dreta:
el buc panxut oliva amb la franja taronja, els nou dipòsits al llom, el finestral encès a proa, la porta d'estribord
oberta amb la rampa i la llum de dins; la seva ombra, llarga, cap a la càmera i a la dreta (sense entrar als botons).
La canonada de terra surt de baix, gruixuda i a prop, i puja en diagonal fins a la bomba de Verne del pou; d'allà,
prima, fins a la base de la Canonada: és la línia que porta l'ull. En primer pla, roques i matolls secs en silueta
emmarquen els cantons de baix. De la rampa de la nau surt un corriol cap a la posta.

El títol, «AIGUA VERNE», és l'etiqueta d'una ampolla d'aigua de Verne: blanca i blava, una mica rovellada, i
les lletres són de vidre, mig plenes d'aigua (cadascuna fins a un nivell diferent).

Els botons de la GUI van a 220..420 × 224..328: allà només hi ha camp (i la canonada, a baix).
ANIMS: `pols` (la pols que passa arran de terra), `llums` (els llums vermells de la Canonada i de la nau que fan
pampallugues) i `titol` (el títol, en una capa a part amb l'aigua de dins les lletres que es gronxa: «Comença»
l'esvaeix i el pròleg, `proleg_terra2`, continua al mateix pla).

El món: x a la dreta, y amunt, z endavant (la càmera a l'origen, a 220 d'alçada); 1 unitat = 1 px a la distància on
un personatge «de lluny» fa la seva mida normal (z = 400).
"""
import hd640  # noqa: F401  (abans de cap hd.rooms: posa la llibreria a 640×360)

import functools
import math

from hd.pix import Canvas, Light, W, H, hr, mix, RUST
from hd.rooms.comu import text, text_width
from hd.rooms.exterior import fbm, smooth
from hd640.rooms.nau_comu import (STEELN, WBLUE, WHITEV, COL, BLACKT, INK, drop,
                                  diposit_orbital, canonada)
from hd640.rooms.cantimplora_comu import Cantimplora
from hd640.tres_d import Camera, Escena, Llum

HOR = 196
CAM = Camera(pos=(0, 220, 0), yaw=0.0, pitch=0.0, f=400, centre=(320, HOR))
SUN = (96, HOR - 14)
CAN_X = 548                              # la Canonada
TANK = (548, 22)                         # el dipòsit orbital
PUMP = (490, 255)                        # la bomba de Verne: el pal del balancí i terra (en pantalla)
PIPE = ((PUMP[0] + 18, PUMP[1] - 3), (CAN_X - 10, HOR - 2))   # la canonada prima, del pou a la base de la Canonada
LABEL = (122, 26, 518, 192)              # l'etiqueta del títol
S = 8                                    # el «píxel» de les lletres grosses

LIGHT = Light(ambient=0.0, vignette=None, floor_fade=None)
LLUMS_MON = [Llum((-60000, 5000, 110000), 1e7, 1.7, power=1.0)]   # el sol, darrere a l'esquerra, baix
AMBIENT = -0.4

# ─── Rampes ─────────────────────────────────────────────────────────────────
DUSK = [(14, 10, 26), (24, 16, 38), (38, 22, 48), (56, 30, 54), (80, 40, 58), (108, 54, 58), (140, 72, 58),
        (172, 96, 62), (204, 126, 70), (228, 156, 84), (244, 186, 108), (252, 214, 146), (255, 238, 196)]
PLAIN = [(18, 12, 14), (30, 20, 20), (46, 30, 26), (64, 42, 32), (86, 56, 38), (110, 72, 46), (136, 92, 56),
         (164, 114, 68), (192, 138, 84)]
HILLS = [(34, 22, 34), (50, 30, 40), (68, 40, 46), (88, 52, 50), (110, 66, 56)]
CREAM = [(96, 86, 72), (142, 132, 112), (184, 176, 156), (214, 208, 190), (232, 228, 214), (244, 242, 232),
         (252, 251, 246)]
NAVY = [(6, 12, 34), (10, 22, 60), (16, 36, 92)]
GLASS = [(150, 176, 206), (184, 206, 228), (212, 228, 242), (232, 242, 250)]
WATER = [(10, 40, 110), (18, 64, 156), (30, 92, 196), (52, 128, 226), (96, 170, 244), (170, 214, 255)]
ROCK = [(10, 7, 10), (18, 12, 15), (28, 19, 21), (40, 27, 27), (56, 37, 33), (74, 49, 40)]

LETTERS = {
    'A': ['01110', '10001', '10001', '11111', '10001', '10001', '10001'],
    'I': ['11111', '00100', '00100', '00100', '00100', '00100', '11111'],
    'G': ['01111', '10000', '10000', '10011', '10001', '10001', '01111'],
    'U': ['10001', '10001', '10001', '10001', '10001', '10001', '01110'],
    'V': ['10001', '10001', '10001', '10001', '01010', '01010', '00100'],
    'E': ['11111', '10000', '10000', '11110', '10000', '10000', '11111'],
    'R': ['11110', '10001', '10001', '11110', '10100', '10010', '10001'],
    'N': ['10001', '11001', '10101', '10011', '10001', '10001', '10001'],
}


# ─── Cel ────────────────────────────────────────────────────────────────────

def sky(cv):
    for y in range(0, HOR + 1):
        t = y / HOR
        for x in range(W):
            d = math.hypot(x - SUN[0], (y - SUN[1]) * 1.8)
            lvl = 0.8 + 6.4 * t ** 1.7 + 4.0 * max(0.0, 1 - d / 260) ** 2.2
            band = fbm(x / 160, y / 9, 61)                                 # bandes de pols allargades
            lvl += (band - 0.5) * 1.4 * t
            lvl -= 0.6 * smooth(0.55, 0.75, fbm(x / 90, y / 14, 62)) * t ** 2
            cv.put(x, y, DUSK, lvl, lit=0)
            if t < 0.5 and hr(x, y, 63) > 0.9975:                          # les primeres estrelles
                cv.flat(x, y, (170, 160, 190) if hr(x, y, 64) > 0.5 else (110, 96, 140))
    # el sol: un disc enterbolit, partit per les bandes de pols
    cv.glow(SUN[0], SUN[1], 70, (255, 200, 130), 0.5)
    for y in range(SUN[1] - 11, SUN[1] + 12):
        for x in range(SUN[0] - 11, SUN[0] + 12):
            if (x - SUN[0]) ** 2 + (y - SUN[1]) ** 2 <= 121 and not (y - SUN[1]) % 6 == 3:
                cv.put(x, y, DUSK, 12.0 - (y - SUN[1] + 11) * 0.05, lit=0)
    # turons llunyans, morats, amb desnivells
    for x in range(W):
        h = HOR - 3 - 9 * fbm(x / 80, 0.5, 65) - 4 * fbm(x / 20, 1.5, 66)
        for y in range(int(h), HOR + 1):
            cv.put(x, y, HILLS, 2.6 - (y - h) * 0.08 + 1.4 * max(0.0, 1 - abs(x - SUN[0]) / 200), lit=0)


def tank_and_pipe(cv, light=None):
    # la Canonada, de l'horitzó fins al dipòsit, amb els llums vermells
    canonada(cv, CAN_X, TANK[1] + 6, HOR - 6, 1.0, 3.0, ring=9, haze=(200, 120, 90), haze_k=0.45)
    # la llum del sol, de costat, a l'esquerra de la columna
    cv.tint(CAN_X - 4, TANK[1], CAN_X - 1, HOR, (255, 170, 100), lambda x, y: 0.25)
    cv.tint(CAN_X + 1, TANK[1], CAN_X + 4, HOR, (60, 30, 70), lambda x, y: 0.3)
    cv.tint(CAN_X - 4, TANK[1], CAN_X + 4, HOR, (40, 24, 60), lambda x, y: 0.35 * (1 - (y - TANK[1]) / (HOR - TANK[1])))
    for y in range(TANK[1] + 30, HOR - 20, 40):
        on = light is not None and (light + y // 40) % 4 == 0
        cv.flat(CAN_X, y, (255, 70, 50) if on else (130, 30, 30))
        if on:
            cv.glow(CAN_X, y, 5, (255, 80, 60), 0.6)
    # l'estació de la base, a l'horitzó
    cv.rect(CAN_X - 10, HOR - 5, CAN_X + 10, HOR, COL, lambda x, y: 0.8 - (x - CAN_X) * 0.03, lit=0)
    cv.rect(CAN_X - 10, HOR - 6, CAN_X + 10, HOR - 6, COL, 2.0, lit=0)
    for x in range(CAN_X - 8, CAN_X + 9, 4):
        cv.flat(x, HOR - 5, (255, 210, 120))
    # el dipòsit orbital: un cilindre blanc amb la gota, il·luminat de baix per la posta
    diposit_orbital(cv, TANK[0], TANK[1], 64, 8)
    cv.tint(TANK[0] - 36, TANK[1] - 9, TANK[0] + 36, TANK[1] + 9, (255, 160, 90),
            lambda x, y: 0.35 * max(0.0, (y - TANK[1] + 4) / 18) + 0.1 * max(0.0, (TANK[0] - x) / 50))
    cv.tint(TANK[0] - 36, TANK[1] - 9, TANK[0] + 36, TANK[1] + 9, (40, 30, 70),
            lambda x, y: 0.4 * max(0.0, (TANK[1] - y - 4) / 10))
    for side in (-1, 1):                                               # els panells solars i els braços
        x0 = TANK[0] + side * 40
        for j in range(2):
            cv.rect(min(x0, x0 + side * 20), TANK[1] - 2 + j * 3, max(x0, x0 + side * 20), TANK[1] - 1 + j * 3,
                    [(20, 30, 60), (40, 60, 110), (80, 110, 170)], 1.4 + j * 0.3, lit=0)
        cv.hline(min(TANK[0] + side * 34, x0), max(TANK[0] + side * 34, x0), TANK[1], STEELN, 4.0, lit=0)
    if light is not None and light % 2 == 0:
        cv.flat(TANK[0] - 33, TANK[1] - 1, (255, 80, 60))
        cv.flat(TANK[0] + 33, TANK[1] - 1, (120, 255, 120))


# ─── La Cantimplora (el model canònic, cantimplora_comu) ─────────────────────
# En 3/4: la proa, a la dreta, s'acosta a la càmera; es veu el costat d'estribord, amb la porta i la rampa.

NAU_A = 0.3                                          # el rumb: la proa, cap a la dreta (de costat, la línia de
#                                                      mirada ja la gira a 3/4: es veu el costat i una mica la proa)
NAU_C = (-610.0, 1320.0)                             # on és el mig del buc (x, z)
_D = (math.cos(-NAU_A), math.sin(-NAU_A))
NAU = Cantimplora(popa=(NAU_C[0] - _D[0] * 200, NAU_C[1] - _D[1] * 200), rumb=-NAU_A, porta='estribord')
SOL_DIR = (-0.5, 0.6, 0.86)                         # cap al sol: darrere a l'esquerra, baix (l'ombra, llarga)
SHIP_C = NAU_C


# les caixes (coordenades de sala) que el pròleg apaga: la cabina, el llum de navegació, la porta i la rampa (amb
# la claror de cadascuna), i on surt el fum dels motors
_GLOW_C = max(4, round(70 * CAM.escala(NAU.CABINA)))
_GLOW_P = max(4, round(56 * CAM.escala(NAU.PORTA)))
CABIN = NAU.caixa(CAM, 'cabina', _GLOW_C + 2)
NAV = NAU.caixa(CAM, 'llum_nav', 6)
RAMP = NAU.caixa(CAM, 'porta', _GLOW_P + 2)
EXHAUST = NAU.xy(CAM, NAU.TOVERES[0])
RAMP_TOP_P = NAU.RAMPA_DALT
RAMP_FOOT_P = NAU.RAMPA_PEU


def cantimplora(e, off=False):
    NAU.dibuixa(e, llums=not off, ombra={'sol': SOL_DIR, 'k': 0.6, 'esvaeix': 500}, to=((70, 40, 60), 0.28))


def ship_glow(cv, off=False):
    """La claror de la cabina i de la porta (en pantalla, damunt de tot)."""
    if not off:
        NAU.resplendor(cv, cam=CAM)


def ship_lights(cv, light=None, off=False):
    """El llum de navegació (fa pampallugues) i la brasa dels motors."""
    NAU.llum_nav(cv, encès=light is not None and light % 3 == 0 and not off, cam=CAM, apagat=off)
    NAU.brasa(cv, encesa=not off, cam=CAM)


# ─── El terra, el corriol, la canonada i el primer pla ─────────────────────────

# el corriol: del peu de la rampa, se'n va cap a la posta (punts del món, x, z)
# (es pensa en pantalla: passa per l'esquerra de la popa, sense amagar-s'hi darrere, i s'ajunta amb el sol de lluny)
def _terra_mon(u, v):
    z = CAM.f * CAM.pos[1] / (v - HOR)
    return ((u - CAM.centre[0]) * z / CAM.f, z)


PATH_MON = [(RAMP_FOOT_P[0], RAMP_FOOT_P[2])] + [_terra_mon(u, v) for u, v in (
    (45, 248), (36, 238), (36, 226), (42, 216), (54, 208), (78, 203), (96, 199))]
NEAR_PIPE = ((70.0, 6.0, 470.0), (606.0, 6.0, 1490.0))     # la canonada gruixuda: de baix fins a la bomba


@functools.lru_cache(maxsize=None)
def _path_pts():
    """El corriol, suavitzat (Chaikin) i repartit per igual al llarg del camí (al món)."""
    pts = [tuple(map(float, p)) for p in PATH_MON]
    for _ in range(4):
        out = [pts[0]]
        for (ax, az), (bx, bz) in zip(pts, pts[1:]):
            out += [(0.75 * ax + 0.25 * bx, 0.75 * az + 0.25 * bz), (0.25 * ax + 0.75 * bx, 0.25 * az + 0.75 * bz)]
        pts = out + [pts[-1]]
    acc = [0.0]
    for (ax, az), (bx, bz) in zip(pts, pts[1:]):
        acc.append(acc[-1] + math.hypot(bx - ax, bz - az) / ((az + bz) / 2) ** 0.85)   # (de lluny, a poc a poc)
    n, out, j = 600, [], 0
    for i in range(n + 1):
        d = acc[-1] * i / n
        while j < len(acc) - 2 and acc[j + 1] < d:
            j += 1
        k = (d - acc[j]) / max(1e-9, acc[j + 1] - acc[j])
        out.append((pts[j][0] + (pts[j + 1][0] - pts[j][0]) * k, pts[j][1] + (pts[j + 1][1] - pts[j][1]) * k))
    return tuple(out)


def path_mon(u):
    """El corriol al món: u=0 al peu de la rampa, u=1 a l'horitzó, sota el sol. → (x, z)"""
    pts = _path_pts()
    return pts[round(max(0.0, min(1.0, u)) * (len(pts) - 1))]


def path_xy(u):
    """El corriol a la pantalla → (x, y, escala d'un personatge allà)."""
    x, z = path_mon(u)
    px, py, _ = CAM.projecta((x, 0, z))
    return px, py, CAM.escala((x, 0, z))


def _dist_path(x, z):
    best = 1e9
    pts = _path_pts()
    for (ax, az), (bx, bz) in zip(pts[::8], pts[8::8]):
        if not (min(az, bz) - 40 <= z <= max(az, bz) + 40):
            continue
        dx, dz = bx - ax, bz - az
        k = max(0.0, min(1.0, ((x - ax) * dx + (z - az) * dz) / (dx * dx + dz * dz or 1)))
        best = min(best, math.hypot(x - ax - dx * k, z - az - dz * k))
    return best


_B = 0.12                                                  # els solcs, una mica girats: fugen cap a la dreta


def _terra(s, t, P):
    x, z = P[0], P[2]
    fc = x * math.cos(_B) - z * math.sin(_B)
    # els solcs: es veuen a prop i s'esvaeixen abans que siguin més prims que un píxel (si no, fan moaré); de lluny,
    # bandes allargades de terra més clara i més fosca, que també fugen
    fade = 1 - smooth(700, 1900, z)
    fur = math.sin(fc / 22 * math.pi)
    lvl = 4.3 + fur * 0.7 * fade + (fbm(x / 140, z / 90, 67) - 0.5) * 1.4
    lvl += (fbm(fc / 60, z / 900, 69) - 0.5) * 1.6 * (1 - fade)
    lvl += (hr(int(fc) // 6, int(z) // 10, 68) - 0.5) * 0.5 * fade
    lvl -= 1.1 * (1 - smooth(500, 1100, z))                # a prop, a contrallum
    if z < 8000:                                           # el corriol, de terra trepitjada
        d = _dist_path(x, z)
        if d < 14:
            lvl += 1.2 * (1 - d / 14) + (hr(int(x) // 3, int(z) // 3, 82) - 0.5) * 0.6
    return lvl


def far_fence(e):
    """Una tanca vella que fuig cap a l'horitzó, a la dreta."""
    (x0, z0), (x1, z1) = (1500.0, 3600.0), (5200.0, 9800.0)
    n = 26
    tops = []
    for i in range(n + 1):
        u = i / n
        x, z = x0 + (x1 - x0) * u, z0 + (z1 - z0) * u
        e.caixa('tanca', x - 3, x + 3, 0, 38 + (hr(i, 5) - 0.5) * 8, z - 3, z + 3, BLACKT, 2.0)
        tops.append((x, z))
    for (xa, za), (xb, zb) in zip(tops, tops[1:]):
        e.cable('tanca', [(xa, 26, za), (xb, 26, zb)], BLACKT, 1.6, gruix=1.4)


def near_pipe(e):
    A, B = NEAR_PIPE
    e.foscor('ombra', (A[0] + 4, 0.3, A[2]), (B[0] + 4, 0.3, B[2]), (B[0] + 26, 0.3, B[2] - 8), (A[0] + 26, 0.3, A[2] - 8),
             lambda s, t: 0.5)
    e.tub('canonada', B, A, 7, COL, 3.0, brides=90, llum_dir=(0.5, 1.0))


def primer_pla(e):
    """Roques i matolls secs en silueta als dos cantons de baix (a contrallum: gairebé negres)."""
    for (x, z, r, seed) in ((-470, 620, 84, 11), (-590, 740, 60, 12), (-330, 590, 40, 13), (-640, 600, 70, 14),
                            (460, 640, 92, 21), (330, 590, 40, 22), (600, 720, 64, 23)):
        e.roca('primer_pla', (x, 0, z), r, ROCK, 1.6, llum_dir=(-0.8, -0.5), seed=seed)
    # una iuca a l'esquerra: fulles com espases
    bx, bz = -470.0, 570.0
    for j in range(17):
        a = math.pi / 2 + (j - 8) * 0.17 + (hr(j, 31) - 0.5) * 0.15
        L = 60 + hr(j, 32) * 40
        e.cable('primer_pla', [(bx, 40, bz), (bx + math.cos(a) * L, 40 + math.sin(a) * L, bz - 4)], ROCK, 2.0,
                gruix=3.6)
    e.cable('primer_pla', [(bx, 0, bz), (bx, 42, bz)], ROCK, 1.6, gruix=10)
    # un matoll sec a la dreta: branques
    mx, mz = 320.0, 590.0

    def branca(P, a, L, n, seed):
        if n == 0 or L < 5:
            return
        Q = (P[0] + math.cos(a) * L, P[1] + math.sin(a) * L, P[2])
        e.cable('primer_pla', [P, Q], ROCK, 2.0, gruix=max(1.4, n * 1.1))
        for k, da in enumerate((-0.45, 0.4)):
            branca(Q, a + da + (hr(seed, k) - 0.5) * 0.3, L * 0.68, n - 1, seed * 3 + k + 1)
    for k, a in enumerate((1.25, 1.6, 1.95)):
        branca((mx, 0, mz), a, 46, 4, 50 + k)


def ground_pipe(cv):
    """La canonada prima, de la bomba a la base de la Canonada: blanca, amb abraçadores, més prima de lluny."""
    (ax, ay), (bx, by) = PIPE
    n = max(abs(bx - ax), abs(by - ay)) * 2
    for i in range(n + 1):
        u = i / n
        x, y = round(ax + (bx - ax) * u), round(ay + (by - ay) * u)
        thick = 2 if u < 0.4 else 1
        cv.put(x, y, COL, 3.6 - u * 0.8, lit=0)
        if thick == 2:
            cv.put(x, y + 1, COL, 2.0, lit=0)
        cv.darken(x, y + thick, x, y + thick, 0.35)
    for k in range(1, 6):                                                # les abraçadores
        u = k / 6
        x, y = round(ax + (bx - ax) * u), round(ay + (by - ay) * u)
        cv.put(x - 1, y, STEELN, 1.6, lit=0)
        cv.put(x + 1, y, STEELN, 1.6, lit=0)


def pipe_xy(u):
    (ax, ay), (bx, by) = PIPE
    return ax + (bx - ax) * u, ay + (by - ay) * u


def bomba_verne(cv, phase=0.25):
    """La bomba de Verne al pou d'una granja: un balancí blanc amb la gota blava. El cap del balancí (a la dreta)
    puja i baixa damunt del pou; a l'esquerra, la manovella amb el contrapès. `phase` (0..1): una cabotada."""
    px, gy = PUMP
    # l'ombra, llarga cap a la dreta (el sol és a l'esquerra)
    cv.darken(px - 16, gy - 1, px + 54, gy + 4,
              lambda x, y: 0.6 if ((x - px - 18) / 36) ** 2 + ((y - gy - 1) / 2.6) ** 2 <= 1 else 0)
    cv.rect(px - 16, gy - 2, px + 20, gy, STEELN, lambda x, y: 1.8 - (y - gy + 2) * 0.4, lit=0)   # el sòcol
    wx = px + 15                                                         # el pou: el capçal blau, amb la gota
    cv.rect(wx - 3, gy - 7, wx + 3, gy - 3, WBLUE, lambda x, y: 3.2 - (x - wx) * 0.25, lit=0)
    cv.hline(wx - 4, wx + 4, gy - 8, WBLUE, 4.2, lit=0)
    cv.flat(wx, gy - 5, (220, 236, 255))
    pv = (px, gy - 18)                                                   # el pal (una A)
    cv.line(px - 5, gy - 2, pv[0], pv[1], STEELN, 2.6, lit=0)
    cv.line(px + 4, gy - 2, pv[0], pv[1], STEELN, 1.4, lit=0)
    ang = 2 * math.pi * phase                                            # la manovella i el contrapès
    ck = (px - 11, gy - 7)
    cv.rect(ck[0] - 2, ck[1] - 1, ck[0] + 2, gy - 2, STEELN, 1.2, lit=0)
    cw = (ck[0] - 3 * math.cos(ang), ck[1] - 3 * math.sin(ang))
    cv.disc(cw[0], cw[1], 2.6, 2.6, STEELN, 2.2, lit=0)
    pin = (ck[0] + 3 * math.cos(ang), ck[1] + 3 * math.sin(ang))
    a = 0.2 * math.sin(ang)                                              # el balancí
    lx, ly = pv[0] - 12 * math.cos(a), pv[1] + 12 * math.sin(a)
    rx, ry = pv[0] + 15 * math.cos(a), pv[1] - 15 * math.sin(a)
    cv.line(lx, ly, pin[0], pin[1], STEELN, 2.8, lit=0)                  # la biela
    n = 40
    for i in range(n + 1):
        t = i / n
        x, y = lx + (rx - lx) * t, ly + (ry - ly) * t
        cv.put(x, y - 1, WHITEV, 4.6, lit=0)
        cv.put(x, y, WBLUE if 0.3 < t < 0.6 else WHITEV, 3.0, lit=0)
    cv.flat(pv[0], pv[1], INK)
    hx, hy = round(rx), round(ry)                                        # el cap de cavall i la barra
    cv.rect(hx, hy - 2, hx + 1, hy + 3, WHITEV, lambda x, y: 4.2 - (y - hy) * 0.3, lit=0)
    cv.flat(hx + 2, hy, WHITEV[5])
    cv.vline(hx + 1, hy + 4, gy - 9, STEELN, 3.2, lit=0)
    gx, gy2 = round(pv[0] + 4 * math.cos(a)), round(pv[1] - 4 * math.sin(a))
    cv.flat(gx, gy2 - 2, (40, 110, 220))


# ─── El títol ──────────────────────────────────────────────────────────────

def _cells(word, x0, y0):
    out = []
    col = 0
    for ch in word:
        for r, bits in enumerate(LETTERS[ch]):
            for c, b in enumerate(bits):
                if b == '1':
                    out.append((x0 + (col + c) * S, y0 + r * S, ch))
        col += 6
    return out


def _wordw(word):
    return len(word) * 6 * S - S


LEVELS = {0: (0.58, 0.40, 0.66, 0.52, 0.30), 1: (0.46, 0.62, 0.36, 0.70, 0.55)}   # fins on és plena cada lletra


def title(cv, phase=0.0):
    x0, y0, x1, y1 = LABEL
    # l'etiqueta: paper blanc (una mica groguenc), corbada com una ampolla (fosca als cantons)
    for y in range(y0, y1 + 1):
        for x in range(x0, x1 + 1):
            u = (x - x0) / (x1 - x0)
            lvl = 4.6 - (2 * u - 1) ** 4 * 2.6 + (0.6 if 0.18 < u < 0.24 else 0) + (hr(x // 2, y // 2, 71) - 0.5) * 0.3
            cv.put(x, y, CREAM, lvl, lit=0)
    # les franges blaves de dalt i de baix, amb una onada blanca
    for band, (ya, yb) in enumerate(((y0, y0 + 15), (y1 - 15, y1))):
        for y in range(ya, yb + 1):
            for x in range(x0, x1 + 1):
                u = (x - x0) / (x1 - x0)
                wave = math.sin(x / 9 + band * 2) * 2.2
                inner = (y - ya) if band == 1 else (yb - y)
                if band == 0 and y > yb - 4 + wave * 0.6:
                    continue
                if band == 1 and y < ya + 4 + wave * 0.6:
                    continue
                lvl = 2.6 - (2 * u - 1) ** 4 * 2.0 + (0.5 if 0.18 < u < 0.24 else 0)
                cv.put(x, y, WBLUE, lvl, lit=0)
                if abs(y - (yb - 3 if band == 0 else ya + 3) - wave * 0.6) < 0.8:
                    cv.flat(x, y, mix(cv.get(x, y), (220, 236, 255), 0.7))
    # el text petit de les franges: el lema de Verne i el preu
    s1 = 'PERQUÈ LA SET NO ESPERA'
    text(cv, s1, (x0 + x1 - text_width(s1)) // 2, y1 - 7, None, 0, flat=(230, 240, 255))
    s2 = 'AIGUA DE DIPOSIT ORBITAL  ·  1 L'
    text(cv, s2, (x0 + x1 - text_width(s2)) // 2, y0 + 2, None, 0, flat=(230, 240, 255))
    # les lletres grosses, de vidre, mig plenes d'aigua
    lines = ('AIGUA', 'VERNE')
    ly = (y0 + 22, y0 + 22 + 7 * S + 10)
    for li, word in enumerate(lines):
        wx = (x0 + x1 - _wordw(word)) // 2 + (10 if li == 0 else 10)
        cells = _cells(word, wx, ly[li])
        filled = {(cx_, cy_) for cx_, cy_, _ in cells}
        # l'ombra i el contorn
        for cx_, cy_, _ in cells:
            cv.rect(cx_ + 3, cy_ + 3, cx_ + S + 2, cy_ + S + 2, [mix(CREAM[2], (0, 0, 0), 0.25)], 0, lit=0)
        for cx_, cy_, _ in cells:
            cv.rect(cx_ - 2, cy_ - 2, cx_ + S + 1, cy_ + S + 1, [NAVY[0]], 0, lit=0)
        for cx_, cy_, ch in cells:
            k = 'AIGUA'.index(ch) if li == 0 else 'VERNE'.index(ch) if ch != 'E' else (1 if cx_ < wx + 3 * 6 * S
                                                                                       else 4)
            col_idx = (cx_ - wx) // (6 * S)
            level = LEVELS[li][col_idx]
            top_l, bot_l = ly[li], ly[li] + 7 * S
            wl_base = bot_l - (bot_l - top_l) * level
            for py in range(cy_, cy_ + S):
                for px in range(cx_, cx_ + S):
                    wl = wl_base + math.sin(px / 7 + phase + col_idx * 1.3) * 2.0
                    edge_t = (px, py - S) if False else None
                    if py < wl:
                        # vidre buit: blanc blavós, amb un reflex
                        lvl = 2.0 - (py - top_l) / (7 * S) * 0.8
                        if (px - cx_) < 2 and (cx_ - S, cy_) not in filled:
                            lvl += 1.0
                        cv.put(px, py, GLASS, lvl, lit=0)
                    else:
                        d = (py - wl) / max(1, bot_l - wl)
                        lvl = 4.2 - d * 2.6 + (0.6 if (px - cx_) < 2 and (cx_ - S, cy_) not in filled else 0)
                        cv.put(px, py, WATER, lvl, lit=0)
                        if py - wl < 1.2:
                            cv.flat(px, py, (220, 240, 255))
                        elif py - wl < 6 and hr(px, py, 72) > 0.94:
                            cv.flat(px, py, (180, 220, 255))          # bombolles
                    if py == cy_ and (cx_, cy_ - S) not in filled:
                        cv.flat(px, py, mix(cv.get(px, py), (255, 255, 255), 0.5))
                    if px == cx_ + S - 1 and (cx_ + S, cy_) not in filled:
                        cv.flat(px, py, mix(cv.get(px, py), NAVY[2], 0.4))
        # cantons arrodonits: es treuen els píxels dels cantons de fora
        for cx_, cy_, _ in cells:
            for dx, dy, nx_, ny_ in ((-2, -2, -S, -S), (S + 1, -2, S, -S), (-2, S + 1, -S, S), (S + 1, S + 1, S, S)):
                if (cx_ + nx_, cy_) not in filled and (cx_, cy_ + ny_) not in filled:
                    px, py = cx_ + dx, cy_ + dy
                    cv.flat(px, py, cv.get(px + (1 if dx < 0 else -1) * 3, py) if False else CREAM[4])
    # la gota de Verne, grossa, al costat de «AIGUA»
    drop(cv, x0 + 30, ly[0] + 40, 13, WBLUE, 3.6)
    cv.disc(x0 + 26, ly[0] + 36, 2.5, 3.5, WBLUE, 6.4, lit=0)
    # rovell: les vores esquerdades, taques i un regalim del cantó de dalt a la dreta
    for k in range(70):
        side = k % 4
        if side == 0:
            px, py = x0 + int(hr(k, 73) * (x1 - x0)), y0 + int(hr(k, 74) * 4)
        elif side == 1:
            px, py = x0 + int(hr(k, 73) * (x1 - x0)), y1 - int(hr(k, 74) * 4)
        elif side == 2:
            px, py = x0 + int(hr(k, 74) * 5), y0 + int(hr(k, 73) * (y1 - y0))
        else:
            px, py = x1 - int(hr(k, 74) * 5), y0 + int(hr(k, 73) * (y1 - y0))
        r = 1 + hr(k, 75) * 3
        cv.disc(px, py, r, r * 0.8, RUST, lambda nx, ny: 2.6 + nx * 0.6 + (hr(int(nx * 4), int(ny * 4), k) - 0.5),
                lit=0)
    for j in range(46):                                                 # el regalim
        if hr(j, 76) > 0.2:
            cv.put(x1 - 22 + (1 if j > 30 else 0), y0 + 2 + j, RUST, 2.8 - j * 0.04, lit=0)
    for k in range(10):                                                 # esquerdes de l'esmalt
        px, py = x0 + 8 + int(hr(k, 77) * (x1 - x0 - 16)), y0 + 16 + int(hr(k, 78) * (y1 - y0 - 32))
        for j in range(4 + int(hr(k, 79) * 6)):
            cv.flat(px + j, py + int(math.sin(j + k) * 1.2), mix(cv.get(px + j, py), (120, 100, 80), 0.5))
    # el cantó de baix a l'esquerra, esquinçat i doblegat
    for j in range(12):
        for i in range(12 - j):
            cv.put(x0 + i, y1 - j, CREAM, 2.4 - i * 0.06, lit=0)
    cv.line(x0, y1 - 12, x0 + 12, y1, [INK], 0, lit=0)
    # el contorn de l'etiqueta
    for x in range(x0 - 1, x1 + 2):
        cv.flat(x, y0 - 1, INK)
        if x > x0 + 12:
            cv.flat(x, y1 + 1, INK)
    for y in range(y0 - 1, y1 + 2):
        cv.flat(x0 - 1, y, INK) if y < y1 - 12 else None
        cv.flat(x1 + 1, y, INK)
    cv.darken(x0 + 4, y1 + 2, x1 + 4, y1 + 5, 0.5)
    cv.darken(x1 + 2, y0 + 4, x1 + 5, y1 + 5, 0.5)



# ─── La pols ───────────────────────────────────────────────────────────────

def dust(cv, frame):
    """Cortines de pols que passen arran de terra, de dreta a esquerra."""
    for y in range(HOR - 26, H):
        t = (y - HOR + 26) / (H - HOR + 26)
        for x in range(W):
            u = (x + frame * 6) / 120
            d = fbm(u, y / 10, 81) - 0.52 + 0.16 * math.sin(u * 3 + y / 30)
            if d > 0:
                a = min(1.0, d * 3.0) * 0.32 * (1 - abs(t - 0.4))
                if a > 0 and (a > 0.2 or hr(x, y, frame) < a * 4):
                    o = cv.get(x, y)
                    cv.flat(x, y, mix(o, (214, 150, 104), a))


# ─── Composició ────────────────────────────────────────────────────────────

def scene(cv, light=None, ship_off=False, pump=True):
    """L'escena sense el títol (el fons de la portada i del pròleg). Per a les capes del pròleg: `ship_off`, la nau
    apagada; `pump=False`, sense la bomba (per dibuixar-la en una altra posició). → l'Escena (qui ha pintat què)."""
    sky(cv)
    tank_and_pipe(cv, light)
    e = Escena(cv, CAM, LLUMS_MON, ambient=AMBIENT)
    e.quad('terra', (-80000, 0, 60000), (80000, 0, 60000), (80000, 0, 300), (-80000, 0, 300), ramp=PLAIN, lvl=_terra)
    e.claror((-80000, 0.2, 60000), (80000, 0.2, 60000), (80000, 0.2, 900), (-80000, 0.2, 900), (200, 120, 92),
             lambda s, t: 0.55 * smooth(1500, 30000, 60000 - t))          # la calitja: el fons es confon amb el cel
    # la claror de la posta pel terra, i la boira de pols arran de l'horitzó
    cv.tint(0, HOR + 1, W - 1, H - 1, (255, 170, 100),
            lambda x, y: 0.4 * max(0.0, 1 - math.hypot(x - SUN[0], (y - HOR) * 4) / 300))
    cv.tint(0, HOR - 14, W - 1, HOR + 18, (220, 140, 90), lambda x, y: 0.28 * max(0.0, 1 - abs(y - HOR) / 18))
    far_fence(e)
    ground_pipe(cv)
    cantimplora(e, off=ship_off)
    if pump:
        bomba_verne(cv)
    near_pipe(e)
    primer_pla(e)
    ship_glow(cv, ship_off)
    ship_lights(cv, light, ship_off)
    return e


@functools.lru_cache(maxsize=None)
def _base():
    cv = Canvas(light=LIGHT)
    e = scene(cv)
    return cv.img.copy(), e


def bg(cv):
    cv.img.paste(_base()[0])
    cv.P = cv.img.load()


def base_img():
    """El fons (sense títol ni animacions), per fer-hi capes a sobre: no el modifiquis, copia'l."""
    return _base()[0]


def base_escena():
    """L'Escena del fons: qui ha pintat cada píxel (per tapar el que passa per darrere de la nau)."""
    return _base()[1]


def diff(img, base=None, force=()):
    """Els píxels de `img` que canvien respecte de `base` (el fons), i tots els de les caixes de `force`."""
    import numpy as np
    from PIL import Image
    a = np.asarray(img.convert('RGBA')).copy()
    b = np.asarray((base or base_img()).convert('RGBA'))
    same = (a == b).all(axis=2)
    s = img.width // W
    for x0, y0, x1, y1 in force:
        same[max(0, y0 * s):(y1 + 1) * s, max(0, x0 * s):(x1 + 1) * s] = False
    a[same] = (0, 0, 0, 0)
    return Image.fromarray(a, 'RGBA')


def tower_lights(cv, light):
    """Només els llums (la Canonada, el dipòsit, la nau): per a la capa `llums`, damunt del fons."""
    for y in range(TANK[1] + 30, HOR - 20, 40):
        on = (light + y // 40) % 4 == 0
        cv.flat(CAN_X, y, (255, 70, 50) if on else (130, 30, 30))
        if on:
            cv.glow(CAN_X, y, 5, (255, 80, 60), 0.6)
    if light % 2 == 0:
        cv.flat(TANK[0] - 33, TANK[1] - 1, (255, 80, 60))
        cv.flat(TANK[0] + 33, TANK[1] - 1, (120, 255, 120))
    ship_lights(cv, light)


@functools.lru_cache(maxsize=None)
def _frames(key, n):
    """(La portada i el pròleg en fan servir els mateixos: es dibuixen una sola vegada.)"""
    out = []
    for f in range(n):
        cv = Canvas(light=LIGHT, img=base_img().copy())
        if key == 'pols':
            dust(cv, f)
        else:
            tower_lights(cv, f)
        out.append(diff(cv.img))
    return out


def _title_frames(n=8):
    out = []
    for f in range(n):
        cv = Canvas(light=LIGHT, img=base_img().copy())
        title(cv, f * math.pi / 4)
        out.append(diff(cv.img))
    return out


PROPS = {}

POLS = {'frames': lambda: _frames('pols', 16), 'frameDuration': 160}
LLUMS = {'frames': lambda: _frames('llums', 12), 'frameDuration': 260}

ANIMS = {
    'pols': POLS,
    'llums': LLUMS,
    'titol': {'frames': _title_frames, 'frameDuration': 180, 'zIndex': 3},
}

GEOMETRIA = {'things': {}, 'spawns': {}}
