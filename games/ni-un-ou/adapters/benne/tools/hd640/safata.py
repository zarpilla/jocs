"""
El que hi ha a la safata del muntacàrregues (cuina, rebost i pont): la icona de l'inventari de l'objecte, petita,
posada damunt de la safata del dibuix pla de cada parada. Cada parada en fa un prop per objecte, `safata_<objecte>`,
que es veu quan la variable `munta_<parada>` és aquell objecte (game/data/rooms/<parada>.json, `decor`).
"""
import functools
from pathlib import Path

from PIL import Image

INVENTARI = Path(__file__).resolve().parent / 'inventory'

# Els objectes que hi caben (`munta: true` a game/data/items.json) i que tenen icona.
OBJECTES = ('travesser', 'tram', 'cable_nou', 'usb', 'nota_iri', 'nota_vet', 'clau_tomas', 'mostra7', 'registre')


@functools.lru_cache(maxsize=None)
def icona(item, amplada):
    """La icona de l'inventari, retallada i reduïda a `amplada` píxels (com a molt; no s'amplia)."""
    im = Image.open(INVENTARI / f'{item}.png').convert('RGBA')
    im = im.crop(im.getbbox())
    k = min(1.0, amplada / im.width)
    return im.resize((max(1, round(im.width * k)), max(1, round(im.height * k))), Image.Resampling.BOX)


def posa(cv, item, cx, y_base, amplada):
    """Dibuixa l'objecte damunt la safata: centrat a `cx`, amb la base a `y_base` (coordenades del dibuix pla)."""
    im = icona(item, amplada)
    cv.img.alpha_composite(im, (round(cx - im.width / 2), round(y_base - im.height)))
    cv.P = cv.img.load()
