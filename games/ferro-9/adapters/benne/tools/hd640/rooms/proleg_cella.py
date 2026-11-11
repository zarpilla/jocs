"""
Pròleg 2 a 640×360 (vegeu hd/rooms/proleg_cella.py, la de 480×270): la cel·la 9 de nit. La Vet dorm a la llitera
de baix (en Mos, a la de dalt) i el panell rovellat vibra i treu llum cian per les juntes. Llums: el panell, la
Terra a la finestreta, el cor de la MARE, tènue.
  - la mateixa composició ×4/3, sobre la cel·la de 640 (hd640/rooms/gavina_cella.py, `night=True`);
  - la Vet, redibuixada: la manta amb plecs, la màniga de la granota amb el puny, el cabell platí amb el serrell,
    l'ull tancat i el nas; en Mos, el cap pelat amb l'orella i la barba grisa;
  - les ones de vibració tenen dos píxels (la cresta i un rastre més tènue), i cau més pols del panell.
Animació `ambient`: la màquina de gavina_cella (`Ambient`): el que és quiet a la memòria cau i, a cada fotograma,
només el que es mou (el panell, les ones, la pols, els halos i el que ja es movia a la cel·la), i el tint blau de la
nit, que és un retoc píxel a píxel, només allà on hi ha hagut canvis.
"""
import hd640  # noqa: F401  (abans que cap hd.rooms: posa la llibreria a 640×360)

import math

from hd.pix import Canvas, Light, hr, mix, ramp, CYAN, SKIN, PAPER, GRAY, ORANGE
from hd640.rooms.gavina_cella import (_static as cella_static, _dyn as cella_dyn, COVER, p_escarabat, p_safata,
                                      Ambient, GRIME, MATT)  # noqa: F401

LIGHT = Light(ambient=-0.9, vignette=(120, 67), floor_fade=(253, 40))
LIGHT.point(348, 136, r=227, k=3.4, squash=0.9, power=1.8)          # el panell que vibra
LIGHT.point(448, 67, r=120, k=1.3)                                   # la Terra a la finestreta
LIGHT.point(235, 40, r=67, k=0.8)                                    # el cor de la MARE

BLANKET = ramp((8, 10, 24), (18, 22, 46), (30, 36, 70), (46, 54, 96), (70, 80, 124), n=7)

PCX, PCY = 348, 136      # el centre del panell


def _sleepers(cv):
    """La Vet a la llitera de baix i en Mos a la de dalt (quiets: al fons quiet)."""
    # ─── La Vet dorm a la llitera de baix ─────────────────────────────────────
    # manta: un bony llarg del cos, dels peus (esquerra) a les espatlles
    for x in range(509, 595):
        u = (x - 509) / 85
        top = 165 - math.sin(u * math.pi * 0.95) * 4 - (2.7 if 0.55 < u < 0.8 else 0)
        rt = round(top)
        for y in range(rt, 182):
            lvl = 3.0 - (y - top) * 0.09 + math.sin(x / 5.3 + y / 8.0) * 0.4
            if y == rt:
                lvl += 1.6
            elif y == rt + 1:
                lvl += 0.7
            if y == 179:
                lvl += 0.5                                               # la vora de la manta, que penja
            cv.put(x, y, BLANKET, lvl)
    # el braç fora de la manta, amb la màniga taronja de la granota
    for x in range(565, 588):
        cv.put(x, 169, ORANGE, 2.8)
        cv.put(x, 170, ORANGE, 2.2 + (0.4 if x % 6 == 0 else 0))
        cv.put(x, 171, ORANGE, 1.4)
    cv.vline(586, 169, 171, ORANGE, 3.4)                                 # el puny
    cv.rect(588, 169, 591, 171, SKIN, lambda x, y: 2.4 - (y - 169) * 0.4)
    # el cap: cabell platí sobre el coixí, la cara de perfil, girada cap a nosaltres
    cv.disc(604, 160, 9.3, 6.7, PAPER, lambda nx, ny: 4.2 - nx * 0.9 - ny * 1.2)
    for k in range(5):
        cv.put(602 + k * 2, 156 + (k % 2), PAPER, 5.0)                   # els reflexos del cabell
    cv.disc(599, 165, 5.3, 4.3, SKIN, lambda nx, ny: 3.0 - nx * 0.6 - ny * 0.8)
    for x in range(595, 603):
        cv.put(x, 162, PAPER, 4.6)                                      # serrell
    cv.put(596, 163, PAPER, 4.0)
    cv.put(599, 163, PAPER, 3.6)
    cv.hline(596, 598, 165, SKIN, 0.4)                                  # ull tancat
    cv.put(599, 164, SKIN, 0.8)
    cv.put(594, 167, SKIN, 2.4)                                         # el nas
    cv.put(595, 168, SKIN, 1.2)
    cv.put(597, 169, SKIN, 1.6)                                         # la boca

    # ─── En Mos, a la de dalt: un bony i el cap pelat ─────────────────────────
    cv.disc(595, 95, 6.1, 5.1, SKIN, lambda nx, ny: 3.4 - nx * 0.8 - ny)
    cv.put(592, 92, SKIN, 4.6)
    cv.put(593, 92, SKIN, 4.2)
    cv.put(594, 98, SKIN, 1.6)                                          # l'orella
    for y in range(93, 100):
        cv.put(600, y, GRAY, 3.6)
        cv.put(601, y, GRAY, 2.8)
        cv.put(602, y, GRAY, 2.0 if y % 2 else 2.6)


def _static(cv):
    cella_static(cv, night=True)
    # el sopar i el Senyor Bigotis, de nit
    p_safata(cv)
    p_escarabat(cv)
    _sleepers(cv)


def _panel_fx(cv, t):
    """El panell vibra i fa llum: les juntes, la tapa que tremola, les ones, la pols i els halos."""
    tt = t
    ph = 2 * math.pi * tt
    x0, y0, x1, y1 = COVER
    # la llum de les juntes polsa: ones que corren al voltant de la tapa (0 a t = 0)
    pulse = math.sin(ph * 3)

    def shimmer(x, y):
        f = (x + y) / 12.0
        return 0.9 * (math.sin(ph * 2 - f) - math.sin(-f)) + 0.5 * pulse
    # llum cian per les juntes de la tapa
    for x in range(x0 - 1, x1 + 2):
        for y in (y0 - 1, y1 + 1):
            cv.put(x, y, CYAN, 4.4 + hr(x, y, 3) * 0.8 + shimmer(x, y), 0)
    for y in range(y0 - 1, y1 + 2):
        for x in (x0 - 1, x1 + 1):
            cv.put(x, y, CYAN, 4.4 + hr(x, y, 4) * 0.8 + shimmer(x, y), 0)
    # la tapa tremola: una imatge fantasma desplaçada, en cian
    cv.tint(x0, y0, x1, y1, (120, 220, 255), 0.08 * (1 + 0.6 * pulse))
    jit = 1 if math.sin(ph * 5) > 0.55 else 0                            # el fantasma salta un píxel
    for x in range(x0 + 1, x1 + 2):
        if (x + jit) % 2:
            cv.put(x, y0 - 3, CYAN, 3.2, 0)
    for y in range(y0 + 1, y1 + 2):
        if (y + jit) % 2:
            cv.put(x1 + 3, y, CYAN, 2.6, 0)
    # ones de vibració a banda i banda
    # (les ones s'allunyen del panell: en surt una de nova a cada pas i l'última s'esvaeix)
    wu = (tt * 3) % 1
    for side in (-1, 1):
        bx = (x0 - 8) if side < 0 else (x1 + 8)
        for k in range(4 if wu else 3):
            p = k + wu
            fade = 1.0 if p <= 2 else 3 - p
            cx = bx + side * round(p * 6.7)
            span = 9 + round(p * 2.7)
            for s in range(-span, span + 1):
                xx = cx + side * round(abs(s) ** 2 / (19 + p * 8))
                if fade >= 1 or hr(xx, PCY + s, 31) < fade:
                    cv.put(xx, PCY + s, CYAN, 4.2 - p * 0.9, 0)
                    cv.put(xx - side, PCY + s, CYAN, 2.8 - p * 0.9, 0)   # el rastre, més tènue
    # pols que cau del panell
    for i in range(18):
        v = 1 + (i % 2)                                                  # dues velocitats
        px = x0 + hr(i, 5) * (x1 - x0) + (math.sin(ph * 2 + i) - math.sin(i)) * 1.1
        py = y1 + 4 + (hr(i, 6) * 40 + tt * 40 * v) % 40
        cv.put(px, py, CYAN, 3.0 - (py - y1) / 27, 0)
    cv.glow(PCX, PCY, 85, (90, 200, 255), 0.35)
    # i el halo polsa (barreja suau, sense quadrets, perquè el tramat no bulli)
    hk = 0.09 * (1 - math.cos(ph * 3)) / 2
    if hk:
        cv.tint(267, 60, 429, 212, (110, 215, 255), lambda x, y: hk * max(0, 1 - math.hypot(x - PCX, y - PCY) / 75))
    # llum cian al terra, davant del panell
    cv.tint(227, 211, 480, 272, (80, 180, 240),
            lambda x, y: max(0, 1 - math.hypot((x - PCX) / 120, (y - 220) / 29)) * 0.25 * (1 + 0.25 * pulse))


def _dyn(cv, t):
    cella_dyn(cv, night=True, t=t)
    _panel_fx(cv, t)


NIGHT_COL = (10, 16, 46)


def _post(x, y, o):
    """Nit: tot més fred (el mateix que `cv.tint(…, (10, 16, 46), 0.25 · d/187)`, píxel a píxel)."""
    kk = 0.25 * min(1, math.hypot(x - PCX, y - PCY) / 187)
    if kk > 0 and o[3]:
        return mix(o, NIGHT_COL, min(1, kk)) + (o[3],)
    return o


AMB = Ambient(LIGHT, _static, _dyn, _post)


def bg(cv, t=0.0):
    """`t` (0..1): moment del cicle de l'animació de fons (t = 0 és el fons quiet)."""
    AMB.draw(cv, t)


def _ambient_frames(n=24):
    return AMB.frames(n)


# ─── La Vet obre els ulls (capa del pròleg) ──────────────────────────────────
# A la segona sacsejada de la paret, la Vet es desperta: obre els ulls (el tancat és la ratlla de 596..598, 165),
# parpelleja un cop i es queda mirant («vet_desperta», sense bucle). Fins llavors, la capa és buida («vet_ulls»).

def ulls_vet(cv, mig=False):
    skin = cv.get(599, 166)
    cv.flat(596, 165, (190, 206, 214))                        # el blanc de l'ull, amb la llum freda del panell
    cv.flat(597, 165, mix(skin, (26, 14, 14), 0.6) if mig else (60, 36, 26))   # l'iris (a mig obrir, la parpella)
    cv.flat(598, 165, mix(skin, (26, 14, 14), 0.5))
    for x in (596, 597, 598):                                 # la parpella i les pestanyes, a sobre
        cv.flat(x, 164, (26, 14, 14) if x < 598 else mix(skin, (26, 14, 14), 0.6))


def _base():
    cv = Canvas(light=LIGHT)
    bg(cv)
    return cv.img


def _ulls_frames():
    from hd640.rooms.fabrica_cambra import frame_diff
    base = _base()

    def layer(state):
        if state is None:
            return Canvas(transparent=True).img
        cv = Canvas(light=LIGHT, img=base.copy())
        cv.P = cv.img.load()
        ulls_vet(cv, mig=state == 'mig')
        return frame_diff(base, cv.img)
    closed, half, opened = layer(None), layer('mig'), layer('obert')
    # (fotogrames de 150 ms) tancats, a mig obrir, oberts... un parpelleig... oberts
    return [closed, closed, half, opened, opened, opened, opened, opened, closed, half, opened]


ANIMS = {
    'ambient': {'frames': _ambient_frames, 'frameDuration': 125},
    'vet_ulls': {'frames': lambda: [Canvas(transparent=True).img], 'frameDuration': 1000, 'loop': False, 'zIndex': 2},
    'vet_desperta': {'frames': _ulls_frames, 'frameDuration': 150, 'loop': False, 'prop': 'vet_ulls'},
}

PROPS = {}
