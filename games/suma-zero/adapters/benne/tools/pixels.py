"""Ampliar o reduir píxel a píxel (veí més proper) sense passar per `Image.resize`.

El Pillow 12.1.1 d'Ubuntu (python3-pil) peta a qualsevol `resize(..., NEAREST)` amb
`SystemError: <method 'resize' of 'ImagingCore' objects> returned NULL`. `transform` amb EXTENT
fa la mateixa feina (mateix mostreig, mateixos bytes) i funciona amb qualsevol Pillow.
"""

from PIL import Image


def nearest(im, size, box=None):
    """El mateix que `im.resize(size, Image.NEAREST, box)`."""
    if box is None:
        box = (0, 0, im.width, im.height)
    return im.transform(tuple(size), Image.Transform.EXTENT, box, Image.Resampling.NEAREST)
