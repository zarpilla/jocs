"""
Soroll suau per a les sales en 3D (hd640/tres_d.py i les sales): el mateix `fbm` que a Aigua Verne i Ni un ou, on
viu a hd/rooms/exterior.py amb els exteriors. A Ferro-9 (com a Suma Zero) només hi ha el soroll.
"""
import math

from hd.pix import hr


def _s(t):
    return t * t * (3 - 2 * t)


def vnoise(u, v, seed=0):
    """Soroll de valors suau (0..1) en una graella unitària."""
    x0, y0 = math.floor(u), math.floor(v)
    fx, fy = _s(u - x0), _s(v - y0)
    a, b = hr(x0, y0, seed), hr(x0 + 1, y0, seed)
    c, d = hr(x0, y0 + 1, seed), hr(x0 + 1, y0 + 1, seed)
    return a + (b - a) * fx + (c - a) * fy + (a - b - c + d) * fx * fy


def fbm(u, v, seed=0, octaves=3):
    s, amp, tot = 0.0, 1.0, 0.0
    for o in range(octaves):
        s += vnoise(u * 2 ** o, v * 2 ** o, seed + o * 17) * amp
        tot += amp
        amp *= 0.5
    return s / tot


def smooth(a, b, t):
    if t <= a:
        return 0.0
    if t >= b:
        return 1.0
    return _s((t - a) / (b - a))
