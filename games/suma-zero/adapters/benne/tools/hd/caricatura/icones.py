"""Proposta A (caricatura), guardada per a un altre joc: icones d'inventari en pixel art caricaturesc."""

from hd.caricatura.cartoon import Fig as CFig  # noqa: F401


def caixa_cartro(f):
    """La caixa del router, oberta, amb les solapes enlaire."""
    f.poly([(12, 9), (36, 9), (37, 24), (11, 24)], 'cartro')
    f.poly([(12, 9), (8, 3), (20, 4), (22, 9)], 'cartro', line=True)
    f.poly([(36, 9), (41, 4), (29, 3), (27, 9)], 'cartro', line=True)
    f.rect(13, 10, 35, 11, 'cartro', tone=0)
    f.rect(16, 15, 27, 19, 'blanc_ull', shade=False)
    f.line(17, 17, 25, 17, 'cable_gris', tone=1)


def cable_alimentacio(f):
    """El cable de la cafetera: endoll, cable en zig-zag i el connector."""
    pts = [(13, 14), (19, 21), (25, 7), (31, 21), (36, 13)]
    for (x0, y0), (x1, y1) in zip(pts, pts[1:]):
        f.line(x0, y0, x1, y1, 'cable_gris', tone=3)
        f.line(x0, y0 + 1, x1, y1 + 1, 'cable_gris', tone=2)
        f.line(x0, y0 + 2, x1, y1 + 2, 'cable_gris', tone=0)
    f.rect(5, 9, 13, 19, 'cable_gris')
    f.rect(1, 11, 4, 12, 'metall')
    f.rect(1, 16, 4, 17, 'metall')
    f.rect(36, 9, 44, 18, 'cable_gris')
    f.px([(39, 12), (40, 12), (39, 13), (40, 13)], 'negre_suau', tone=1)


def pizza(f):
    """La pizza de demà, en un tros de caixa: quatre talls, tomàquet i formatge fos."""
    f.ell(24, 14, 15, 10, 'pizza_caixa')
    f.ell(24, 13, 12.5, 8.5, 'pizza_massa')
    f.ell(24, 13, 10.5, 6.8, 'tomaquet', shade=False)
    for cx, cy, rx, ry in ((20, 11, 3.5, 2.2), (28, 15, 4, 2.4), (25, 10, 2.5, 1.6), (18, 15, 2.8, 1.8)):
        f.ell(cx, cy, rx, ry, 'formatge', shade=False, outline=False)
    f.line(14, 13, 34, 13, 'pizza_massa', tone=0)
    f.line(24, 6, 24, 20, 'pizza_massa', tone=0)
    f.px([(30, 10), (31, 10), (17, 12)], 'verd_llum', tone=1)     # alfàbrega


def auricular(f):
    """L'auricular esquerre de l'Iri: la copa vermella i un tros de diadema."""
    for i in range(10):
        a = 3.14159 * (0.5 + 0.5 * i / 9)
        x, y = round(28 + 12 * __import__('math').cos(a)), round(18 - 13 * __import__('math').sin(a))
        f.px([(x, y), (x + 1, y)], 'negre_suau', tone=2)
    f.ell(18, 16, 6, 8, 'auricular', line=True)
    f.ell(16.5, 16, 3, 5, 'negre_suau', shade=False)
    f.px([(19, 11), (19, 12)], 'auricular', tone=3)


CARTOON = {fn.__name__: fn for fn in (caixa_cartro, cable_alimentacio, pizza, auricular)}


