"""
Entre revolt i revolt del conducte de servei (Iri). EN 3D (hd640/tres_d.py), a 1×.

L'Iri camina a les fosques fins al revolt següent (o fins on surt), i el pas és només un fos entre revolt i revolt.
Hi surten, al damunt, les frases de l'arribada al moll o de quan s'ha perdut. No és una cinemàtica (així la barra de
verbs no desapareix i torna a aparèixer a cada revolt), però no hi ha res per clicar (room_designs.py,
`CONDUCTE_REVOLT`: sense `GEOMETRIA`, es queda la d'allà).

Gairebé negre: un tram del mateix conducte (la planxa reblonada, la canonada de coure i la reixeta del terra de
fabrica_conducte.py), sense làmpada, que al fons gira cap a la dreta; només es llegeix per una claror que ve de
darrere la girada i, a prop, pel reflex del coure i dels reblons. La meitat de dalt queda prou fosca perquè les frases s'hi llegeixin.

El món: x a la dreta (el conducte va de 0 a 150), y amunt, z cap al fons.
"""
import functools
import math

import hd640  # noqa: F401  (abans de cap hd.rooms: posa la llibreria a 640×360)

from hd.pix import Canvas, Light, W, H, IRON, COPPER
from hd640.rooms.fabrica_conducte import _planxa, _reixeta
from hd640.tres_d import Camera, Escena, Llum

BOTTOM = 259
CW, HW = 150, 170                                  # el conducte: ample, alçada
ZN, ZF = -250, 760                                 # d'on es veu fins a la paret del revolt
ZR = 640                                           # on gira cap a la dreta
LLUMETA = (CW + 70, 40, (ZR + ZF) / 2)             # la llumeta, darrere la girada

CAM = Camera(pos=(70, 150, -240), yaw=0.08, pitch=0.08, f=420, centre=(320, 96))

LIGHT = Light(ambient=0.0, vignette=None, floor_fade=None)
LLUMS = [Llum(LLUMETA, 500, 1.8, power=2.0),                     # la llumeta, darrere la girada
         Llum((CW / 2, 120, -120), 320, 0.9, power=2.0)]           # la poca claror que porta l'Iri al darrere


class _Cv(Canvas):
    S = 1


@functools.lru_cache(maxsize=None)
def _fons():
    cv = _Cv(light=LIGHT)
    cv.img.paste((0, 0, 0, 255), (0, 0, W, H))
    e = Escena(cv, CAM, LLUMS, ambient=-0.6)
    fosc = lambda f: (lambda s, t, P: f(s, t, P) - 0.6)            # noqa: E731
    # la girada cap a la dreta: la paret del revolt (al fons), i el tros de passadís nou, d'on ve la llumeta
    e.quad('fons', (0, HW, ZF), (CW + 200, HW, ZF), (CW + 200, 0, ZF), (0, 0, ZF), ramp=IRON, lvl=fosc(_planxa(2.0, 6)))
    e.quad('fons', (CW, 0, ZF), (CW + 200, 0, ZF), (CW + 200, 0, ZR), (CW, 0, ZR), ramp=IRON, lvl=fosc(_reixeta))
    e.quad('paret', (0, HW, ZN), (0, HW, ZF), (0, 0, ZF), (0, 0, ZN), ramp=IRON, lvl=fosc(_planxa(2.0, 3)))
    e.quad('paret', (CW, HW, ZR), (CW, HW, ZN), (CW, 0, ZN), (CW, 0, ZR), ramp=IRON, lvl=fosc(_planxa(2.0, 4)))
    e.caixa('paret', CW - 4, CW + 4, 0, HW, ZR - 4, ZR + 4, IRON, 2.4,
            cares={'davant': {'ramp': IRON, 'lvl': lambda s, t, P: 2.6 + (1.4 if int(t) % 11 == 3 else 0)}})
    e.quad('sostre', (0, HW, ZN), (CW, HW, ZN), (CW, HW, ZF), (0, HW, ZF), ramp=IRON, lvl=lambda s, t, P: 0.4,
           dues_cares=True)
    e.quad('terra', (0, 0, ZF), (CW, 0, ZF), (CW, 0, ZN), (0, 0, ZN), ramp=IRON, lvl=fosc(_reixeta))
    for xx, ld in ((5.5, (0.6, 1.0)), (CW - 5.5, (-0.6, 1.0))):
        e.tub('canonada', (xx, 120, ZF if xx < CW / 2 else ZR - 6), (xx, 120, 20), 5, COPPER, 2.2, brides=58, llum_dir=ld)
    # la claror que ve de darrere la girada, al terra i a la paret del revolt
    e.claror((0, 0.5, ZF), (CW + 200, 0.5, ZF), (CW + 200, 0.5, ZF - 400), (0, 0.5, ZF - 400), (150, 110, 70),
             lambda s, t: 0.4 * max(0.0, 1 - math.hypot((s - CW - 60) / 200, t / 260)))
    e.claror((0, HW, ZF - 0.5), (CW + 200, HW, ZF - 0.5), (CW + 200, 0, ZF - 0.5), (0, 0, ZF - 0.5), (150, 110, 70),
             lambda s, t: 0.45 * max(0.0, 1 - math.hypot((s - CW - 60) / 170, (HW - t - 30) / 120)))
    # a les fosques: tot s'apaga, menys a prop de la llumeta (i encara)
    u, v, _ = CAM.projecta(LLUMETA)
    P = cv.img.load()
    for y in range(BOTTOM + 1):
        for x in range(W):
            k = 0.24 + 0.5 * max(0.0, 1 - math.hypot(x - u, (y - v) * 1.4) / 90) ** 2
            o = P[x, y]
            P[x, y] = (int(o[0] * k), int(o[1] * k), int(o[2] * k), 255)
    cv.img.paste((0, 0, 0, 255), (0, BOTTOM + 1, W, H))
    return cv.img


def bg(cv):
    cv.img.paste(_fons())
    cv.P = cv.img.load()


PROPS = {}
