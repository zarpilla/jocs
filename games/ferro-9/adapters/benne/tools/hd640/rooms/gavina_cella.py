"""
Cel·la 9 de La Gavina (Acte 1, Vet). EN 3D (hd640/tres_d.py), a 1×.

Una càmera alta que mira de biaix la cantonada del fons a l'esquerra (com la referència de l'habitació 404,
docs/referencies/sala-habitacio-404.png): acer fred i net, amb peces velles i rovellades de la fàbrica encastades.
  - a la paret de l'esquerra, en escorç, la **porta** corredissa amb el pany Aldaia M-3 (la sortida al passadís);
  - a la paret del fons, la **reixa** del conducte (arran de terra), la càmera, el **cor** de la MARE, l'**esquerda**
    amb la nota, el **panell** rovellat i la **finestreta** amb la Terra; el fluorescent, a dalt de tot;
  - la **llitera** de dos pisos, separada de la paret i girada, amb tres cares: els pals, els matalassos, la manta
    d'en Mos, el coixí de la Vet, l'escala i la caixa de sota (s'hi passa per darrere);
  - primer pla: el vàter-lavabo d'acer de la cel·la, en silueta a baix a l'esquerra, i una canonada a la dreta.

El detall de les parets ve del dibuix pla de sempre (gavina_cella_pla_comu.py), projectat; els decorats de la paret
(el panell, la reixa oberta, la nota) i l'animació (el fluorescent, el cor que batega, els estels, el LED) també, per
les mateixes superfícies. Els decorats de terra i de la llitera (l'avís, l'escarabat, la safata, el fullet, la molla)
són el seu dibuix pla, dret, en 3D (en surt la diferència amb el fons).

El món: x a la dreta (0 = la paret de la porta), y amunt (0 = el terra), z cap al fons (300 = la paret del fons);
1 unitat = 1 píxel de sala a la distància on un personatge fa ≈110 px (escala 1).
"""
import functools
import math

import hd640  # noqa: F401  (abans de cap hd.rooms: posa la llibreria a 640×360)
from PIL import Image

from hd.pix import Canvas, Light, W, H, STEEL, PANEL, ORANGE, NAVY, IRON, PAPER
from hd.rooms.gavina_cella import DECK, MATT, SHEET
from hd640.rooms import gavina_cella_pla_comu as PL
from hd640.rooms.gavina_passadis_pla_comu import diff
from hd640.tres_d import Camera, Escena, Llum

BOTTOM = 259                                       # la sala acaba aquí (a sota, la barra de verbs)
ZW = 300                                           # la paret del fons
HW = PL.FLOOR_Y                                    # l'alçada de les parets (el dibuix pla fa 211 fins al terra)
XL = 100                                           # al dibuix pla, la cantonada: a l'esquerra, la paret de la porta
XR = 820                                           # on s'acaba la paret del fons (fora de la pantalla)
BUNK = (466, 246, 136, 48, 0.3)                   # la llitera: x, z del centre, llarg, fons, gir
TIERS = (42, 106)                                  # l'alçada dels dos matalassos (la cara de dalt)
POST_H = 128
WC = (30, -46)                                      # el vàter-lavabo (primer pla): x, z del centre
PIPE = (508, -14)                                   # la canonada del primer pla (x, z)
AVIS = (40, 236)                                   # on cauen els decorats de terra (x, z)
ESCARABAT = (122, 270)
SAFATA = (318, 196)
LAMP = (225, 150)                                  # el punt del terra sota el fluorescent


def _w(fx):
    """Una x del dibuix pla de la paret del fons → la x del món."""
    return fx - XL


def _wz(fx):
    """Una x del dibuix pla de la paret de la porta → la z del món."""
    return ZW - XL + fx


def _y(fy):
    """Una y del dibuix pla (el terra, a 211) → l'alçada del món."""
    return HW - fy


CAM = Camera(pos=(440, 175, -320), yaw=-0.36, pitch=0.10, f=450, centre=(320, 84))

LIGHT = Light(ambient=0.0, vignette=None, floor_fade=None)  # (la llum és la del món: la de l'Escena)
LLUMS = [Llum((_w(325), HW - 8, ZW - 30), 520, 2.0, power=1.3),     # el fluorescent, a dalt de la paret del fons
         Llum((_w(235), HW - 37, ZW - 10), 110, 0.9, power=1.6),    # el cor de la MARE
         Llum((_w(448), HW - 67, ZW - 10), 130, 0.6, power=1.6)]    # la finestreta


def _h(*a):
    """Soroll determinista (0..1) ràpid, per als píxels de les superfícies procedurals."""
    n = 0x345678
    for v in a:
        n = ((n ^ (int(v) & 0xFFFFFFFF)) * 1000003) & 0xFFFFFFFF
    n ^= n >> 13
    n = (n * 0x5BD1E995) & 0xFFFFFFFF
    n ^= n >> 15
    return (n & 0xFFFF) / 65535


# ─── Les textures: el dibuix pla de sempre ───────────────────────────────────

TEX_LIGHT = Light(ambient=1.2, vignette=None, floor_fade=None)        # (la paret llisa: la llum, la del món)


@functools.lru_cache(maxsize=None)
def _llisa():
    """La paret sense res: planxes, canal de cables, franja i sòcol (per a les parets que el dibuix pla no cobreix)."""
    cv = Canvas(light=TEX_LIGHT)
    PL._ceiling(cv)
    PL._wall(cv)
    cv.rect(259, 0, 392, 13, STEEL, lambda x, y: 1.0 + y * 0.09)          # (sense el fluorescent)
    cv.hline(259, 392, 14, STEEL, 4.0)
    return cv.img


@functools.lru_cache(maxsize=None)
def _estatic():
    """Les parets planes, de cara, sense el que es mou: la porta, el panell, la reixa, la càmera, les ratlles."""
    cv = Canvas(light=PL.LIGHT)
    PL._ceiling(cv)
    PL._wall(cv)
    PL._door(cv)
    PL.text(cv, 'MODUL C', 101, 59, STEEL, 0.9, worn=0.2)
    PL._panel(cv)
    PL._crack(cv)
    PL.vent_hole(cv)
    PL.vent_grille(cv, *PL.VENT)
    PL.bunk_wall(cv)
    PL._camera(cv)
    return cv.img


@functools.lru_cache(maxsize=None)
def _paret(t=0.0):
    """Les parets amb el que es mou (el fluorescent, el cor, la finestreta, el LED) al moment `t` del cicle."""
    cv = Canvas(light=PL.LIGHT, img=_estatic().copy())
    PL._dyn(cv, False, t)
    PL.DAY.apply_post(cv)
    return cv.img


def _paret_amb(draw):
    """Les parets amb un decorat pla dibuixat al damunt."""
    cv = Canvas(light=PL.LIGHT, img=_paret().copy())
    draw(cv)
    return cv.img


@functools.lru_cache(maxsize=None)
def _pla(nom):
    """Un decorat pla (de terra o de la llitera) sobre transparent, retallat: (imatge, (x0, y0) del retall)."""
    cv = Canvas(light=PL.LIGHT, transparent=True)
    PL.PROPS[nom](cv)
    box = cv.img.getbbox()
    return cv.img.crop(box), box[:2]


# ─── Les superfícies ────────────────────────────────────────────────────────

DRAIN = (236, 150)                                 # el desguàs (x, z)


def _cami(x):
    """El camí gastat de la porta a la llitera: la z del mig a cada x."""
    return 236 - 70 * min(1.0, max(0.0, x / 420)) + 10 * math.sin(x / 70)


def _terra(s, t, P):
    """Planxes d'acer de 64×48, amb la junta, el cantell il·luminat, reblons als cantons i el relleu antilliscant;
    el desguàs al mig i el camí gastat. En coordenades del món: s'empetiteix sol cap al fons."""
    x, z = P[0], P[2]
    dx, dz = x - DRAIN[0], z - DRAIN[1]
    if abs(dx) < 15 and abs(dz) < 9:                                      # el desguàs, amb les lamel·les
        if abs(dx) > 13.5 or abs(dz) > 7.5:
            return 3.6 if dz < 0 else 1.2
        return 0.5 if int(x - DRAIN[0] + 15) % 3 == 0 else 2.0
    cx, cz = math.floor(x / 64), math.floor(z / 48)
    fx, fz = x - cx * 64, z - cz * 48
    if fx < 1.0 or fz < 1.0:
        return 0.9
    v = 2.3 + (_h(cx, cz, 4) - 0.5) * 0.4
    if fx < 2.2 or fz < 2.2:
        v += 0.6
    elif fx > 62.6 or fz > 46.6:
        v -= 0.4
    for rx in (4.5, 59.5):
        for rz in (4.5, 43.5):
            d = (fx - rx) ** 2 + (fz - rz) ** 2
            if d < 2.2:
                return 4.4 if fx - rx + fz - rz < 0 else 1.6
    if _h(cx, cz, 9) > 0.45 and int(z) % 4 == 0 and (int(x) + (int(z) // 4 % 2) * 3) % 6 < 2:
        v += 0.4                                                          # les llàgrimes antilliscants
    if abs(z - _cami(x)) < 22 and _h(int(x) // 2, int(z), 91) > 0.7:
        v += 0.45                                                         # el camí gastat
    if _h(int(x) // 6, int(z) // 3, 44) > 0.985:
        v += 1.2                                                          # rascades
    return v


def _llum_fluorescent(s, t):
    """El bassal de llum del fluorescent al terra (s, t des del cantó del fons a l'esquerra)."""
    return 0.24 * max(0.0, 1 - math.hypot((s - LAMP[0]) / 300, (t - (ZW - LAMP[1])) / 150)) ** 1.3


def _bp(lx, y, lz):
    """Un punt del marc de la llitera (lx al llarg, lz cap al fons) → el món."""
    cx, cz, _, _, a = BUNK
    c, s_ = math.cos(a), math.sin(a)
    return (cx + lx * c - lz * s_, y, cz + lx * s_ + lz * c)


def _bcaixa(e, sid, lx, lz, w, d, h, ramp, lvl=3.0, y0=0.0, cares=None):
    """Una caixa del marc de la llitera, centrada a (lx, lz) del marc."""
    P = _bp(lx, 0, lz)
    e.caixa_girada(sid, P[0], P[2], w, d, h, BUNK[4], ramp, lvl, y0=y0, cares=cares)


def _llitera(e, estat):
    _, _, L, D, _ = BUNK
    # l'ombra al terra (una mica cap al fons: la llum ve de dalt i de la paret)
    e.foscor('ombra_llitera', _bp(-L / 2 - 8, 0.6, D / 2 + 30), _bp(L / 2 + 8, 0.6, D / 2 + 30),
             _bp(L / 2 + 8, 0.6, -D / 2 - 10), _bp(-L / 2 - 8, 0.6, -D / 2 - 10),
             lambda s, t: 0.6 * max(0.0, 1 - ((s - L / 2 - 8) / (L / 2 + 8)) ** 4 - ((t - 25 - D / 2) / (D / 2 + 20)) ** 2) * 1.4)
    # l'ombra que fa el fluorescent: allargada en diagonal cap a la dreta i endavant
    e.foscor('ombra_llitera', _bp(-L / 2 + 10, 0.7, D / 2), (_bp(L / 2, 0, D / 2)[0] + 70, 0.7, _bp(L / 2, 0, D / 2)[2] - 26),
             (_bp(L / 2, 0, -D / 2)[0] + 70, 0.7, _bp(L / 2, 0, -D / 2)[2] - 26), _bp(-L / 2 + 10, 0.7, -D / 2),
             lambda s, t: 0.6 * min(1.0, s / 30) * max(0.0, 1 - s / 230))
    # la caixa de sota i les espardenyes
    _bcaixa(e, 'llitera', 22, 2, 38, 28, 16, PANEL, 2.2,
            cares={'dalt': {'ramp': PANEL, 'lvl': lambda s, t, P: 3.4 - (0.8 if abs(t - 14) < 1 else 0)},
                   'davant': {'ramp': PANEL, 'lvl': lambda s, t, P: 2.0 + (1.0 if t < 1.5 else 0)
                              - (1.0 if abs(s - 19) < 6 and abs(t - 7) < 1.2 else 0)}})
    for k, (lx, lz) in enumerate(((-L / 2 + 22, -D / 2 - 8), (-L / 2 + 32, -D / 2 - 5))):
        _bcaixa(e, 'llitera', lx, lz, 6, 11, 2.5, ORANGE, 2.6,
                cares={'dalt': {'ramp': ORANGE, 'lvl': lambda s, t, P: 3.4 if t > 4 else 1.6}})
    # els pals del darrere i els travessers de baix
    for lz in (D / 2 - 2,):
        for lx in (-L / 2 + 2, L / 2 - 2):
            _bcaixa(e, 'llitera', lx, lz, 4, 4, POST_H, STEEL, 2.4)
    for top in TIERS:
        # el somier (les molles, vistes per sota el travesser) i el travesser d'acer
        _bcaixa(e, 'llitera', 0, 0, L - 2, D - 2, 6, STEEL, 1.8, y0=top - 16,
                cares={'davant': {'ramp': STEEL, 'lvl': lambda s, t, P: 2.6 + (1.6 if t < 1 else 0) - t * 0.25},
                       'esquerra': {'ramp': STEEL, 'lvl': lambda s, t, P: 2.2 + (1.4 if t < 1 else 0) - t * 0.25},
                       'dalt': {'ramp': STEEL, 'lvl': 1.4}})
        # el matalàs: les vores arrodonides, el ribet i les ratlles de la tela
        def tela(s, t, P, top=top):
            v = 3.2 - t * 0.12 + (0.3 if int(s) % 5 == 0 else 0)
            if t < 1.2:
                v += 0.9
            elif t > 8:
                v -= 1.0
            return v

        def dalt(s, t, P, top=top):
            v = 3.6 + (0.3 if int(s + t) % 5 == 0 else 0) - (0.5 if t > D - 10 else 0)
            if top == TIERS[1] and 18 < s < 92:                           # la manta d'en Mos, rebregada
                v = 2.8 + 0.6 * math.sin(s / 6.7 + t / 5.3) - (0.8 if t > D - 12 else 0)
            return v
        _bcaixa(e, 'llitera', 0, 0, L - 8, D - 6, 10, MATT, 2.6, y0=top - 10,
                cares={'davant': {'ramp': MATT, 'lvl': tela}, 'esquerra': {'ramp': MATT, 'lvl': tela},
                       'dreta': {'ramp': MATT, 'lvl': tela}, 'dalt': {'ramp': MATT, 'lvl': dalt}})
        # el coixí, a la dreta
        _bcaixa(e, 'llitera', L / 2 - 22, 2, 24, 30, 6 if top == TIERS[0] else 5, SHEET, 3.0, y0=top,
                cares={'dalt': {'ramp': SHEET, 'lvl': lambda s, t, P: 4.4 - abs(t - 15) * 0.07 - abs(s - 12) * 0.05},
                       'davant': {'ramp': SHEET, 'lvl': 2.6}, 'esquerra': {'ramp': SHEET, 'lvl': 2.4}})
    # la manta de la Vet, plegada als peus
    _bcaixa(e, 'llitera', -L / 2 + 22, 0, 26, 36, 5, NAVY, 3.0, y0=TIERS[0],
            cares={'dalt': {'ramp': NAVY, 'lvl': lambda s, t, P: 3.6 + (0.6 if int(t) % 9 == 0 else 0)},
                   'davant': {'ramp': NAVY, 'lvl': lambda s, t, P: 2.6 - (0.6 if abs(t - 2.5) < 0.6 else 0)}})
    # els decorats de la llitera: el fullet, sota el coixí de la Vet; la molla, que penja del somier
    if 'fullet' in estat:
        img, _ = _pla('fullet')
        e.sprite('fullet', img, (img.width * 0.6, img.height - 1), _bp(L / 2 - 38, TIERS[0], -6), escala_img=0.9)
    if 'molla' in estat:
        img, (ox, oy) = _pla('molla')
        e.sprite('molla', img, (548 - ox, 185 - oy), _bp(-14, TIERS[0] - 16, -D / 2 + 1))
    # els pals del davant i l'escala (al cap de l'esquerra)
    for lx in (-L / 2 + 2, L / 2 - 2):
        _bcaixa(e, 'llitera', lx, -D / 2 + 2, 4, 4, POST_H, STEEL, 2.6,
                cares={'davant': {'ramp': STEEL, 'lvl': lambda s, t, P: 3.4 + (1.0 if s < 1.2 else 0)},
                       'esquerra': {'ramp': STEEL, 'lvl': 2.4}, 'dalt': {'ramp': STEEL, 'lvl': 4.4}})
    for k in range(4):
        _bcaixa(e, 'llitera', -L / 2 - 1, 0, 3, D - 4, 2.5, STEEL, 3.2, y0=TIERS[0] + 12 + k * 13,
                cares={'dalt': {'ramp': STEEL, 'lvl': 4.4}, 'esquerra': {'ramp': STEEL, 'lvl': 3.0}})


def _primer_pla(e):
    """El vàter-lavabo d'acer, en silueta, i la canonada de la dreta."""
    FOSC = [(4, 5, 8), (9, 11, 16), (15, 18, 25), (22, 26, 34), (31, 36, 46), (42, 48, 60)]
    wx, wz = WC
    e.caixa('primer_pla', wx - 30, wx + 30, 0, 40, wz - 26, wz + 26, FOSC, 1.8,
            cares={'dalt': {'ramp': FOSC, 'lvl': lambda s, t, P: (0.6 if math.hypot(s - 30, t - 30) < 17 else 3.2)
                            + (1.2 if abs(math.hypot(s - 30, t - 30) - 18) < 1.5 else 0)},
                   'davant': {'ramp': FOSC, 'lvl': lambda s, t, P: 1.4 + (0.8 if t < 2 else 0)},
                   'dreta': {'ramp': FOSC, 'lvl': lambda s, t, P: 2.2 + (0.8 if t < 2 else 0)}})
    e.caixa('primer_pla', wx - 30, wx + 30, 40, 84, wz + 14, wz + 26, FOSC, 1.6,
            cares={'dalt': {'ramp': FOSC, 'lvl': 3.0}, 'dreta': {'ramp': FOSC, 'lvl': 2.2}})
    e.tub('primer_pla', (wx + 12, 84, wz + 20), (wx + 12, 92, wz + 6), 2.4, FOSC, 3.0)    # l'aixeta
    px, pz = PIPE
    e.tub('primer_pla', (px, 0, pz), (px, HW + 40, pz), 9, FOSC, 2.0, brides=70)
    e.tub('primer_pla', (px - 4, HW - 30, pz), (px - 150, HW + 20, pz - 20), 5, FOSC, 1.6)


def escena(cv, estat=frozenset()):
    """Tota la sala, de lluny a prop. `estat`: els decorats de terra i de la llitera que hi són ('avis',
    'escarabat', 'safata', 'fullet', 'molla'). → l'Escena (qui ha pintat què)."""
    cv.S = 1                                               # (el Canvas d'1× de Ferro-9 no ho diu)
    e = Escena(cv, CAM, LLUMS, ambient=-0.4)
    zn = CAM.pos[2] + 60
    paret, llisa = _paret(), _llisa()
    # el sostre, fosc, amb les bigues
    e.quad('sostre', (0, HW, zn), (XR, HW, zn), (XR, HW, ZW), (0, HW, ZW), ramp=STEEL, dues_cares=True,
           lvl=lambda s, t, P: 1.0 + (1.6 if P[2] % 70 < 6 else 0) - (0.6 if P[2] % 70 < 1 else 0))
    # la paret de la porta (x = 0): de prop, la paret llisa; cap a la cantonada, el dibuix pla (x 0..100)
    e.quad('paret_esq_prop', (0, HW, zn), (0, HW, ZW - XL), (0, 0, ZW - XL), (0, 0, zn),
           tex=(llisa, (180, 0, 180 + ZW - XL - zn, HW)))
    e.quad('paret_esq', (0, HW, ZW - XL), (0, HW, ZW), (0, 0, ZW), (0, 0, ZW - XL), tex=(paret, (0, 0, XL, HW)))
    # la paret del fons (z = 300): el dibuix pla (x 100..640) i, a la dreta, la paret llisa
    e.quad('paret_fons', (0, HW, ZW), (W - XL, HW, ZW), (W - XL, 0, ZW), (0, 0, ZW), tex=(paret, (XL, 0, W, HW)))
    e.quad('paret_fons_dreta', (W - XL, HW, ZW), (XR, HW, ZW), (XR, 0, ZW), (W - XL, 0, ZW),
           tex=(llisa, (157, 0, 157 + XR - W + XL, HW)))
    # el terra, amb el bassal del fluorescent
    e.quad('terra', (0, 0, ZW), (XR, 0, ZW), (XR, 0, zn), (0, 0, zn), ramp=DECK, lvl=_terra)
    e.claror((0, 0.3, ZW), (XR, 0.3, ZW), (XR, 0.3, 0), (0, 0.3, 0), (200, 230, 255), _llum_fluorescent)
    # la claror rosa del cor a la paret i la foscor dels racons
    e.foscor('racons', (0, 0.5, ZW), (XR, 0.5, ZW), (XR, 0.5, zn), (0, 0.5, zn),
             lambda s, t: max(0.6 * max(0.0, 1 - t / 26), 0.5 * max(0.0, 1 - s / 22)))
    e.foscor('cantonada', (0, HW, ZW - 0.5), (70, HW, ZW - 0.5), (70, 0, ZW - 0.5), (0, 0, ZW - 0.5),
             lambda s, t: 0.5 * max(0.0, 1 - s / 70))
    e.foscor('cantonada2', (0.5, HW, ZW - 70), (0.5, HW, ZW), (0.5, 0, ZW), (0.5, 0, ZW - 70),
             lambda s, t: 0.5 * max(0.0, 1 - (70 - s) / 70))
    e.foscor('paret_prop', (0.5, HW, zn), (0.5, HW, ZW - 70), (0.5, 0, ZW - 70), (0.5, 0, zn),
             lambda s, t: 0.35 * max(0.0, 1 - s / 300))
    # l'ombra de la llitera a la paret del fons (la llum ve de dalt a l'esquerra)
    _, _, L, D, _ = BUNK
    bx0, bx1 = _bp(-L / 2, 0, D / 2)[0], _bp(L / 2, 0, D / 2)[0]
    for top in TIERS:
        e.foscor('ombra_paret', (bx0 + 6, top - 18, ZW - 0.5), (bx1 + 24, top - 18, ZW - 0.5),
                 (bx1 + 24, top - 52, ZW - 0.5), (bx0 + 6, top - 52, ZW - 0.5),
                 lambda s, t: 0.55 * max(0.0, 1 - t / 34) * min(1.0, s / 14))
    # els decorats de terra
    for nom, (x, z) in (('avis', AVIS), ('escarabat', ESCARABAT), ('safata', SAFATA)):
        if nom in estat:
            img, _ = _pla(nom)
            e.foscor('ombra_' + nom, (x - 20, 0.6, z + 8), (x + 20, 0.6, z + 8), (x + 20, 0.6, z - 8),
                     (x - 20, 0.6, z - 8), lambda s, t: 0.5 * max(0.0, 1 - ((s - 20) / 20) ** 2 - ((t - 8) / 8) ** 2))
            e.sprite(nom, img, (img.width / 2, img.height - 1), (x, 0, z))
    _llitera(e, estat)
    _primer_pla(e)
    return e


# ─── Composició ─────────────────────────────────────────────────────────────

def _render(estat=frozenset()):
    cv = Canvas(light=LIGHT)
    e = escena(cv, estat)
    cv.rect(0, BOTTOM + 1, W - 1, H - 1, [(0, 0, 0)], 0, lit=0)    # la barra de verbs: negre
    return cv.img, e


@functools.lru_cache(maxsize=None)
def _base():
    return _render()


def bg(cv):
    cv.img.paste(_base()[0])
    cv.P = cv.img.load()


def _de_paret(draw):
    """Un decorat de la paret: el dibuix pla, projectat per les parets (on es veuen)."""
    def fn(cv):
        _, e = _base()
        cv.img.alpha_composite(e.capa(diff(_paret_amb(draw), _paret()), {'paret_fons', 'paret_esq'}))
        cv.P = cv.img.load()
    return fn


def _decorat(nom):
    """Un decorat en 3D: la sala amb ell, menys la de sempre (només el que canvia)."""
    def fn(cv):
        img, _ = _render(frozenset({nom}))
        cv.img.alpha_composite(diff(img, _base()[0]))
        cv.P = cv.img.load()
    return fn


PROPS = {
    'avis': _decorat('avis'),
    'escarabat': _decorat('escarabat'),
    'safata': _decorat('safata'),
    'panell_afluixat': _de_paret(PL.p_panell_afluixat),
    'panell_obert': _de_paret(PL.p_panell_obert),
    'panell_reparat': _de_paret(PL.p_panell_reparat),
    'panell_sincronitzat': _de_paret(PL.p_panell_sincronitzat),
    'reixa_oberta': _de_paret(PL.p_reixa_oberta),
    'esquerda': _de_paret(PL.p_esquerda),
    'fullet': _decorat('fullet'),
    'molla': _decorat('molla'),
    # la clau anglesa encaixada al panell, que es pot agafar: la dibuixa el decorat `panell_reparat`; aquest prop
    # només n'és la zona clicable (transparent)
    'clau_panell': lambda cv: None,
}


# ─── Animació: el fluorescent que parpelleja, el cor que batega, els estels i el LED ──

def _ambient_frames(n=24):
    img0, e = _base()
    out = []
    for i in range(n):
        img = img0.copy()
        img.alpha_composite(e.capa(diff(_paret(i / n), _paret()), {'paret_fons', 'paret_esq'}))
        out.append(diff(img, img0))
    return out


# ─── La finestra de fase, a aquesta banda: el cop de puny al panell ──────────
#
# Quan la Vet rep el que l'Iri ha enviat (el primer cop, la clau anglesa), el panell fa un espetec: una llum blanca,
# espurnes, i la clau que surt del panell i cau a terra, on brilla un moment i s'apaga (se l'emporta la Vet: l'objecte
# va a l'inventari). Un prop buit (`fase_panell`) i l'animació que s'hi posa (`espetec`).

def _llum(d, u, v, r, col, a):
    """Un halo rodó (cercles concèntrics, transparents), damunt d'una capa buida."""
    for k in range(6, 0, -1):
        rr = r * k / 6
        d.ellipse((u - rr, v - rr * 0.9, u + rr, v + rr * 0.9), fill=col + (round(a * (1 - k / 7) ** 1.3),))


def _frames_espetec():
    from PIL import ImageDraw
    from hd640 import items as IT
    pu, pv, _ = CAM.projecta((_w(349), _y(136), ZW - 1))
    tu, tv, _ = CAM.projecta((_w(349) + 44, 0, ZW - 20))          # on cau la clau: a terra, al costat del panell
    ic = IT.render('clau_anglesa')
    k = CAM.escala((_w(349) + 44, 0, ZW - 20)) * 0.62
    ic = ic.resize((max(1, round(ic.width * k)), max(1, round(ic.height * k))), Image.NEAREST)
    out = []
    n = 16
    for i in range(n):
        img = Image.new('RGBA', (W, H), (0, 0, 0, 0))
        d = ImageDraw.Draw(img)
        if i < 4:                                                  # l'espetec: la llum i les espurnes
            _llum(d, pu, pv, 46 - i * 6, (210, 235, 255), 255 - i * 45)
            for j in range(9):
                ang = j * 2 * math.pi / 9 + i * 0.35
                r0, r1 = 8 + i * 7, 16 + i * 11
                d.line([(pu + r0 * math.cos(ang), pv + r0 * math.sin(ang)),
                        (pu + r1 * math.cos(ang), pv + r1 * math.sin(ang) + i * 2)],
                       fill=(255, 250, 200, 255 - i * 40), width=1)
        if 2 <= i < 6:                                             # la clau surt del panell i cau
            f = (i - 2) / 3
            u, v = pu + (tu - pu) * f, pv + (tv - pv) * f ** 2
            img.alpha_composite(ic, (round(u - ic.width / 2), round(v - ic.height / 2)))
        elif i >= 6:                                               # a terra, brilla i s'apaga
            a = max(0.0, 1 - (i - 6) / (n - 8))
            if a > 0:
                _llum(d, tu, tv - 2, 20, (120, 220, 255), round(170 * a))
                img.alpha_composite(ic, (round(tu - ic.width / 2), round(tv - ic.height + 3)))
        out.append(img)
    out.append(Image.new('RGBA', (W, H), (0, 0, 0, 0)))
    return out


ANIMS = {
    'ambient': {'frames': _ambient_frames, 'frameDuration': 125},
    'fase_panell': {'frames': lambda: [Image.new('RGBA', (W, H), (0, 0, 0, 0))], 'frameDuration': 1000, 'loop': False,
                    'zIndex': 4},
    'espetec': {'frames': _frames_espetec, 'frameDuration': 90, 'loop': False, 'prop': 'fase_panell'},
}


def _amo(ids):
    def mask(x, y):
        _, e = _base()
        return e.ids[e.amo[y * e.cv.w + x]] in ids
    return mask


def _p(x, z, y=0.0):
    u, v, _ = CAM.projecta((x, y, z))
    return round(u), round(v)


# Capes del davant: el primer pla (sempre davant) i la llitera (qui hi passa per darrere, hi queda darrere). La
# llitera és girada: la línia base és la del cantó de davant que queda més al fons (qui és davant de qualsevol tros
# de la llitera, hi passa per davant).
FRONT = [
    {'id': 'davant', 'mask': _amo({'primer_pla'}), 'baseline': 999, 'zIndex': 20},
    {'id': 'davant_llitera', 'mask': _amo({'llitera', 'fullet', 'molla'}),
     'baseline': min(_p(*_bp(lx, 0, -BUNK[3] / 2)[::2])[1] for lx in (-BUNK[2] / 2, BUNK[2] / 2)), 'zIndex': 20,
     'props': ('fullet', 'molla')},
]


# ─── Geometria (coordenades de sala, projectades) ────────────────────────────

def _rect_mon(*Ps):
    pts = [CAM.projecta(P) for P in Ps]
    return (max(0, round(min(p[0] for p in pts))), max(0, round(min(p[1] for p in pts))),
            min(W - 1, round(max(p[0] for p in pts))), min(BOTTOM, round(max(p[1] for p in pts))))


def _wall(fx0, fy0, fx1, fy1):
    return _rect_mon((_w(fx0), _y(fy0), ZW), (_w(fx1), _y(fy1), ZW))


V_MAX = 252                                        # més a prop, el personatge passaria d'1,2: és per al primer pla


def _talla(poly, vmax):
    """El polígon de pantalla retallat per sota de la y `vmax`."""
    out = []
    for (ax, ay), (bx, by) in zip(poly, poly[1:] + poly[:1]):
        if ay <= vmax:
            out.append((ax, ay))
        if (ay <= vmax) != (by <= vmax):
            k = (vmax - ay) / (by - ay)
            out.append((round(ax + (bx - ax) * k), vmax))
    return out


def _bunk_mon(lx, lz):
    P = _bp(lx, 0, lz)
    return P[0], P[2]


def _talla_x(poly, x0, x1):
    """El polígon de pantalla retallat entre les x `x0` i `x1`: el personatge no surt tallat per les vores (tasca 109)."""
    for dins, tall in ((lambda p: p[0] >= x0, x0), (lambda p: p[0] <= x1, x1)):
        out = []
        for a, b in zip(poly, poly[1:] + poly[:1]):
            if dins(a):
                out.append(a)
            if dins(a) != dins(b):
                out.append((tall, round(a[1] + (b[1] - a[1]) * (tall - a[0]) / (b[0] - a[0]))))
        poly = out
    return poly


MARGE_X = 22                                       # la meitat d'una figura de prop, i una mica més


# El terra on es camina (al món): de la porta a la llitera, arran de la paret del fons; per davant de la llitera
# (i una mica pel seu costat esquerre, per darrere del cap). El vàter i la canonada del primer pla hi passen per
# davant (capa `davant`).
_L, _D = BUNK[2], BUNK[3]
WALK_MON = [(16, 286), (_bunk_mon(-_L / 2 - 8, _D / 2)[0], 286), _bunk_mon(-_L / 2 - 10, _D / 2 - 4),
            _bunk_mon(-_L / 2 - 10, -_D / 2 - 14), _bunk_mon(_L / 2 + 6, -_D / 2 - 14), (600, 170), (PIPE[0] - 14, -40),
            (16, -40)]
# a la dreta, fins al pilar de primer pla (x ≈ 589..624): més enllà, la Vet hi quedava amagada al darrere o tallada per
# la vora (tasca 109); el punt de la llitera (x 581) hi queda a dins
PILAR_X0 = 582
_WALK = _talla_x(_talla([_p(x, z) for x, z in WALK_MON], V_MAX), MARGE_X, PILAR_X0)
_V_FONS, _V_PROP = min(v for _, v in _WALK), max(v for _, v in _WALK)


def _escala_a(v):
    """L'escala d'un personatge amb els peus a la y de pantalla `v` (al terra, la profunditat només depèn de v)."""
    lo, hi = -400.0, 2000.0
    for _ in range(60):
        z = (lo + hi) / 2
        if CAM.projecta((260, 0, z))[1] > v:
            lo = z
        else:
            hi = z
    return CAM.escala((260, 0, (lo + hi) / 2))


def _sprite_rect(nom, peu, peu_img=None, escala_img=1.0):
    img, _ = _pla(nom)
    fx, fy = peu_img or (img.width / 2, img.height - 1)
    k = CAM.escala(peu) * escala_img
    u, v, _ = CAM.projecta(peu)
    return (round(u - fx * k) - 2, round(v - fy * k) - 2, round(u + (img.width - fx) * k) + 2,
            round(v + (img.height - fy) * k) + 2)


def _llitera_rect():
    pts = [_bp(lx, y, lz) for lx in (-_L / 2, _L / 2) for lz in (-_D / 2, _D / 2) for y in (0, POST_H)]
    return _rect_mon(*pts)


_HEART = _p(_w(PL.HX), ZW, _y(PL.HY + 18))
_MOLLA_IMG, (_MOX, _MOY) = _pla('molla')

GEOMETRIA = {
    'things': {
        'porta': {'rect': _rect_mon((0, _y(65), _wz(10)), (0, 0, _wz(88))), 'walk': _p(30, _wz(52))},
        'panell': {'rect': _wall(319, 105, 379, 168), 'walk': _p(_w(349), 236)},
        'clau_panell': {'rect': _wall(355, 79, 381, 138), 'walk': _p(_w(349), 236)},
        'altaveu': {'rect': _wall(210, 17, 260, 61), 'walk': _p(_w(235), 236)},
        'llitera': {'rect': _llitera_rect(), 'walk': _p(*_bunk_mon(_L / 2 - 8, -_D / 2 - 24))},
        'fullet': {'rect': _sprite_rect('fullet', _bp(_L / 2 - 38, TIERS[0], -6), escala_img=0.9),
                   'walk': _p(*_bunk_mon(_L / 2 - 8, -_D / 2 - 24))},
        'molla': {'rect': _sprite_rect('molla', _bp(-14, TIERS[0] - 16, -_D / 2 + 1), (548 - _MOX, 185 - _MOY)),
                  'walk': _p(*_bunk_mon(-14, -_D / 2 - 24))},
        'finestreta': {'rect': _wall(412, 31, 484, 103), 'walk': _p(_w(448), 236)},
        'avis': {'rect': _sprite_rect('avis', (AVIS[0], 0, AVIS[1])), 'walk': _p(AVIS[0] + 26, AVIS[1] - 10)},
        'escarabat': {'rect': _sprite_rect('escarabat', (ESCARABAT[0], 0, ESCARABAT[1])),
                      'walk': _p(ESCARABAT[0] + 24, ESCARABAT[1] - 10)},
        'safata': {'rect': _sprite_rect('safata', (SAFATA[0], 0, SAFATA[1])), 'walk': _p(SAFATA[0] - 34, SAFATA[1])},
        # a la dreta de la reixa: al davant, la Directora (Acte 3) tapava la Vet (tasca 176)
        'reixa': {'rect': _wall(112, 152, 184, 201), 'walk': _p(_w(220), 262)},
        'esquerda': {'rect': _wall(268, 116, 299, 157), 'walk': _p(_w(284), 250)},
    },
    'spawns': {'vet': _p(250, 150), 'mos': _p(*_bunk_mon(-_L / 2 + 26, -_D / 2 - 30)), 'mare': _HEART,
               'directora': _p(150, 120)},
    'walkable': _WALK,
    'floorSquash': 0.4,                            # (la càmera, picada: el terra es veu aixafat)
    # L'ombra de contacte: el fluorescent (el punt del terra just a sota); curta, és llum de dalt.
    'characterShadow': {'enabled': True, 'color': '#06080e', 'alpha': 0.42, 'squash': 0.4, 'core': 0.6,
                        'light': {'x': _p(*LAMP)[0], 'y': _p(*LAMP)[1], 'stretch': 0.5, 'reach': 160}},
    'regions': [{'id': 'perspectiva', 'active': True, 'scaleEnabled': True, 'scaleWalkSpeed': True,
                 'scaleTop': round(_escala_a(_V_FONS - 2), 3), 'scaleBottom': round(_escala_a(_V_PROP + 2), 3),
                 'points': [(0, _V_FONS - 2), (W - 1, _V_FONS - 2), (W - 1, _V_PROP + 2), (0, _V_PROP + 2)]}],
    # la llum de la sala sobre els personatges, en temps d'execució
    'characterLights': {
        'ambient': '#a8b4c6',                                                           # acer fred
        'lights': [
            {'x': _p(_w(325), ZW - 30, HW - 10)[0], 'y': _p(_w(325), ZW - 30, HW - 10)[1], 'radius': 360,
             'color': '#d8f0ff', 'intensity': 0.7},                                     # el fluorescent
            {'x': _HEART[0], 'y': _HEART[1] - 20, 'radius': 120, 'color': '#ff78be', 'intensity': 0.6},   # el cor
            {'x': _p(_w(448), ZW, _y(67))[0], 'y': _p(_w(448), ZW, _y(67))[1], 'radius': 110,
             'color': '#5a96ff', 'intensity': 0.4},                                     # la finestreta
        ],
    },
}
