"""
Passades de llum sobre una sala ja dibuixada (prototip a pis_estudi): el que fa que l'escena «brilli».

  - `wash`: llums de color que tenyeixen les superfícies (multipliquen) i una mica l'aire (sumen);
  - `haze`: llum volumètrica, un polígon de «boira» il·luminada (el raig de la finestra);
  - `bloom`: el que emet llum (pantalles, neó, llumets) treu halo a la paret del voltant;
  - `grade`: corba de to (contrast i saturació), color a color: no afegeix colors nous.

Tot el que suma llum es **quantitza amb dither de Bayer** (esglaons de `STEP`), perquè el resultat continuï
semblant pixel art i no un degradat llis. Les passades són deterministes: aplicades al fons i a cada
fotograma d'una animació, la resta (_diff) només dona els píxels que canvien.

Ús:  FX = [bloom(...), wash(...), ...];  img = apply(img, FX)
"""
import math

import numpy as np
from PIL import Image, ImageDraw, ImageFilter

B4 = np.array([[0, 8, 2, 10], [12, 4, 14, 6], [3, 11, 1, 9], [15, 7, 13, 5]], dtype=np.float32) / 16
STEP = 10.0          # esglaó de quantització de la llum afegida (sobre 255)


def _bayer(h, w):
    return np.tile(B4, (h // 4 + 1, w // 4 + 1))[:h, :w]


def _q(add):
    """Quantitza una capa de llum additiva (h×w×3, 0..255) a esglaons de STEP amb dither ordenat."""
    m = add.max(axis=2)
    h, w = m.shape
    mq = np.floor(m / STEP + _bayer(h, w)) * STEP
    k = np.divide(mq, m, out=np.zeros_like(m), where=m > 0.5)
    return add * k[..., None]


def _qk(k):
    """Quantitza un factor 0..1 (h×w) amb dither, en 12 esglaons."""
    h, w = k.shape
    return np.floor(k * 12 + _bayer(h, w)) / 12


# ─── Passades ───────────────────────────────────────────────────────────────

def wash(x, y, r, col, k=0.6, air=0.08, squash=1.0, power=1.6, box=None):
    """Llum de color a (x, y), de radi r: les superfícies prenen el color (rgb × (1 + k·col)) i l'aire
    s'hi il·lumina una mica (air·col). `box` (x0, y0, x1, y1): fora d'aquí no hi arriba."""
    def f(rgb, ctx):
        h, w = rgb.shape[:2]
        yy, xx = ctx['grid']
        d = np.hypot(xx - x, (yy - y) * squash) / r
        fall = np.clip(1 - d, 0, 1) ** power
        if box:
            x0, y0, x1, y1 = box
            fall *= (xx >= x0) & (xx <= x1) & (yy >= y0) & (yy <= y1)
        fall = _qk(fall)
        c = np.array(col, dtype=np.float32) / 255
        return rgb * (1 + k * fall[..., None] * c) + _q(air * 255 * fall[..., None] * c)
    return f


def haze(pts, col, k=0.25, fade=None, blur=6):
    """Llum volumètrica: el polígon `pts` s'omple de `col` amb força k, amb les vores suaus (blur) i
    un factor opcional fade(x, y) → 0..1 (on s'esvaeix el raig)."""
    def f(rgb, ctx):
        h, w = rgb.shape[:2]
        sc = ctx['scale']
        m = Image.new('L', (w, h), 0)
        ImageDraw.Draw(m).polygon([(x * sc, y * sc) for x, y in pts], fill=255)
        if blur:
            m = m.filter(ImageFilter.GaussianBlur(blur * sc))
        a = np.asarray(m, dtype=np.float32) / 255 * k
        if fade:
            yy, xx = ctx['grid']
            a = a * fade(xx, yy)
        return rgb + _q(a[..., None] * np.array(col, dtype=np.float32))
    return f


def bloom(thr=150, radii=((3, 0.55), (12, 0.45), (32, 0.25)), sat_boost=1.0, mask=None):
    """Halo del que emet: els píxels més lluminosos que `thr` (luminància) es difuminen a diversos radis
    i se sumen. `mask(x, y)` → 0..1 per limitar d'on surt el bloom."""
    def f(rgb, ctx):
        lum = rgb @ np.array([0.3, 0.55, 0.15], dtype=np.float32)
        hot = np.clip((lum - thr) / (255 - thr), 0, 1)
        if mask is not None:
            yy, xx = ctx['grid']
            hot = hot * mask(xx, yy)
        src = rgb * hot[..., None]
        if sat_boost != 1.0:
            g = src.mean(axis=2, keepdims=True)
            src = np.clip(g + (src - g) * sat_boost, 0, 255)
        img = Image.fromarray(src.clip(0, 255).astype(np.uint8))
        add = np.zeros_like(rgb)
        for r, k in radii:
            add += np.asarray(img.filter(ImageFilter.GaussianBlur(r * ctx['scale'])), dtype=np.float32) * k
        return rgb + _q(add)
    return f


def grade(contrast=1.0, pivot=60, sat=1.0, lift=(0, 0, 0), gamma=1.0):
    """Corba de to, color a color: contrast al voltant de `pivot`, saturació, i un color als negres."""
    def f(rgb, ctx):
        out = rgb
        if gamma != 1.0:
            out = 255 * (np.clip(out, 0, 255) / 255) ** gamma
        out = pivot + (out - pivot) * contrast
        g = out.mean(axis=2, keepdims=True)
        out = g + (out - g) * sat
        dark = np.clip(1 - out.max(axis=2, keepdims=True) / 90, 0, 1)
        return out + dark * np.array(lift, dtype=np.float32)
    return f


# ─── Aplicar ────────────────────────────────────────────────────────────────

def apply(img, fx, scale=None):
    """Aplica les passades `fx` (en ordre) a una imatge RGBA; l'alfa no es toca. Les passades són en
    coordenades de la sala (640×360); `scale` = píxels reals per píxel de sala (2 a 1280×720)."""
    if scale is None:
        import hd.pix as pix
        scale = img.width / pix.W                     # art a 2× (hd1280.Canvas2x): 2
    a = np.asarray(img.convert('RGBA'), dtype=np.float32)
    rgb, alpha = a[..., :3].copy(), a[..., 3:]
    h, w = rgb.shape[:2]
    # la coordenada de sala del centre de cada píxel real
    ctx = {'grid': (np.mgrid[0:h, 0:w].astype(np.float32) + 0.5) / scale - 0.5, 'scale': scale}
    for f in fx:
        rgb = f(rgb, ctx)
    out = np.concatenate([np.clip(rgb, 0, 255), alpha], axis=2).round().astype(np.uint8)
    return Image.fromarray(out, 'RGBA')


def apply_cv(cv, fx):
    """Igual, sobre un Canvas de hd.pix (substitueix-ne la imatge)."""
    img = apply(cv.img, fx)
    cv.img.paste(img)
    cv.P = cv.img.load()


# ─── La llum sobre els personatges (la mateixa fórmula que el motor: engine/room/characterLights.ts) ──────────

def _hex(h):
    h = h.lstrip('#')
    return np.array([int(h[i:i + 2], 16) / 255 for i in (0, 2, 4)], dtype=np.float32)


def sample_character_light(cl, x, y, visible=()):
    v = _hex(cl.get('ambient', '#ffffff')).copy()
    for l in cl.get('lights', []):
        if l.get('whenPropVisible') and l['whenPropVisible'] not in visible:
            continue
        d = math.hypot(x - l['x'], (y - l['y']) * l.get('squash', 1)) / l['radius']
        if d < 1:
            v += _hex(l['color']) * l.get('intensity', 1) * (1 - d) ** l.get('power', 1.6)
    return v


def light_character(spr, pos, cl, visible=()):
    """El sprite d'un personatge (RGBA) a `pos` (cantó de dalt a l'esquerra) amb la llum de la sala `cl`, com el
    motor: la llum als quatre cantons, interpolada, en mode overlay de tint (0.5 = neutre)."""
    w, h = spr.size
    x0, y0 = pos
    top = y0 + h * cl.get('topSample', 0.15)
    c = {k: np.clip(sample_character_light(cl, x, y, visible) * 0.5, 0, 1)
         for k, (x, y) in {'tl': (x0, top), 'tr': (x0 + w, top), 'bl': (x0, y0 + h), 'br': (x0 + w, y0 + h)}.items()}
    u = np.linspace(0, 1, w, dtype=np.float32)[None, :, None]
    v = np.linspace(0, 1, h, dtype=np.float32)[:, None, None]
    t = (c['tl'] * (1 - u) + c['tr'] * u) * (1 - v) + (c['bl'] * (1 - u) + c['br'] * u) * v
    a = np.asarray(spr.convert('RGBA'), dtype=np.float32) / 255
    b = a[..., :3]
    out = np.where(b < 0.5, 2 * t * b, 1 - 2 * (1 - t) * (1 - b))
    return Image.fromarray((np.concatenate([out, a[..., 3:]], axis=2) * 255).round().astype(np.uint8), 'RGBA')
