"""
Sales en 3D: una càmera senzilla i superfícies planes que es projecten sobre un Canvas (o Canvas2x).

L'art de les sales es feia de cara, amb `rect` i `poly` en coordenades de pantalla: tot paral·lel a la pantalla.
Aquí la sala es descriu en el món (x a la dreta, y amunt, z endavant; 1 unitat ≈ 1 píxel de sala a la distància on
un personatge fa la seva mida normal) i la càmera la projecta, amb dos punts de fuga si està girada:

    cam = Camera(pos=(300, 165, -40), yaw=-0.3, f=190, centre=(320, 70))
    esc = Escena(cv, cam, llums=[Llum((80, 170, 220), 260, 1.6)])
    esc.quad('terra', P0, P1, P2, P3, ramp=DECKP, lvl=lambda s, t, P: ...)   # procedural (s, t en unitats)
    esc.quad('paret', P0, P1, P2, P3, tex=(img, (x0, y0, x1, y1)))           # textura: un retall d'un dibuix pla
    esc.sprite('seient', img, (fx, fy), peu=(x, 0, z))                        # un dibuix pla dret, a escala

`P0..P3` són els cantons d'un rectangle del món (P0 a dalt a l'esquerra, P1 a dalt a la dreta, P2 a baix a la dreta,
P3 a baix a l'esquerra, mirant-lo de cara). Es pinta en l'ordre en què es crida (de lluny a prop). Cada píxel recorda
quina superfície l'ha pintat (`amo`): així es poden projectar després capes del mateix dibuix pla (un decorat, els
fotogrames d'una animació) per les mateixes superfícies, i el que hi ha davant les continua tapant (`capa`).

Les textures es reaprofiten d'un dibuix pla fet com sempre (la paret vista de cara): no es perd cap detall, i la
perspectiva, les cantonades i la llum per cara surten soles.
"""
import math
from array import array

from PIL import Image

from hd.pix import B4


def _sub(a, b):
    return (a[0] - b[0], a[1] - b[1], a[2] - b[2])


def _dot(a, b):
    return a[0] * b[0] + a[1] * b[1] + a[2] * b[2]


def _cross(a, b):
    return (a[1] * b[2] - a[2] * b[1], a[2] * b[0] - a[0] * b[2], a[0] * b[1] - a[1] * b[0])


def _norm(a):
    n = math.sqrt(_dot(a, a)) or 1.0
    return (a[0] / n, a[1] / n, a[2] / n)


class Camera:
    """Càmera estenopeica. `yaw` > 0 gira la mirada cap a +x; `pitch` > 0 mira avall. Amb `pitch` = 0 les verticals
    del món surten verticals (dos punts de fuga); `centre` = on cau el centre òptic a la pantalla (moure'l en y és com
    descentrar l'objectiu: es veu més terra sense que les verticals convergeixin)."""

    def __init__(self, pos, yaw=0.0, pitch=0.0, f=200.0, centre=(320, 130)):
        self.pos, self.yaw, self.pitch, self.f, self.centre = pos, yaw, pitch, f, centre
        self._cy, self._sy = math.cos(yaw), math.sin(yaw)
        self._cp, self._sp = math.cos(pitch), math.sin(pitch)

    def vista(self, P):
        dx, dy, dz = _sub(P, self.pos)
        x1 = dx * self._cy - dz * self._sy
        z1 = dx * self._sy + dz * self._cy
        y2 = dy * self._cp + z1 * self._sp
        z2 = -dy * self._sp + z1 * self._cp
        return x1, y2, z2

    def gira(self, v):
        """Un vector (no un punt) del món, a l'espai de la càmera."""
        x1 = v[0] * self._cy - v[2] * self._sy
        z1 = v[0] * self._sy + v[2] * self._cy
        return x1, v[1] * self._cp + z1 * self._sp, -v[1] * self._sp + z1 * self._cp

    def homografia(self, P0, e1, e3, S=1):
        """Matriu 3×3 (per files) que porta (s, t, 1) del rectangle P0 + s·e1 + t·e3 a (X·w, Y·w, w) de la pantalla
        (en píxels reals, ×S). Exacta encara que part del rectangle quedi darrere la càmera."""
        f, cu, cv = self.f, self.centre[0], self.centre[1]
        cols = []
        for v in (self.gira(e1), self.gira(e3), self.vista(P0)):
            cols.append(((f * v[0] + cu * v[2]) * S, (-f * v[1] + cv * v[2]) * S, v[2]))
        (a, d, g), (b, e, h), (c, ff, i) = cols
        return (a, b, c, d, e, ff, g, h, i)

    def projecta(self, P):
        """→ (u, v, z): coordenades de sala i profunditat."""
        x, y, z = self.vista(P)
        z = max(z, 1e-3)
        return self.centre[0] + self.f * x / z, self.centre[1] - self.f * y / z, z

    def escala(self, P):
        """Píxels de sala per unitat del món, a la profunditat de P (la mida d'un personatge allà)."""
        return self.f / max(self.vista(P)[2], 1e-3)

    def ull(self):
        return self.pos


class Llum:
    """Llum puntual del món: suma `k` nivells al costat que la mira, i s'apaga amb la distància fins a `r`."""

    def __init__(self, pos, r, k, power=1.5):
        self.pos, self.r, self.k, self.power = pos, r, k, power

    def __call__(self, P, n):
        d = _sub(self.pos, P)
        dist = math.sqrt(_dot(d, d))
        if dist >= self.r:
            return 0.0
        cos = max(0.0, _dot(n, d) / (dist or 1.0))
        return (1 - dist / self.r) ** self.power * self.k * (0.35 + 0.65 * cos)


def _homografia(q):
    """Matriu 3×3 que porta el quadrat unitat (s, t) al quadrilàter q (P0, P1, P2, P3) de la pantalla."""
    (x0, y0), (x1, y1), (x2, y2), (x3, y3) = q
    dx1, dx2, dx3 = x1 - x2, x3 - x2, x0 - x1 + x2 - x3
    dy1, dy2, dy3 = y1 - y2, y3 - y2, y0 - y1 + y2 - y3
    den = dx1 * dy2 - dx2 * dy1
    g = (dx3 * dy2 - dx2 * dy3) / den if den else 0.0
    h = (dx1 * dy3 - dx3 * dy1) / den if den else 0.0
    a, b, c = x1 - x0 + g * x1, x3 - x0 + h * x3, x0
    d, e, f = y1 - y0 + g * y1, y3 - y0 + h * y3, y0
    return (a, b, c, d, e, f, g, h, 1.0)


def _inversa(m):
    a, b, c, d, e, f, g, h, i = m
    A, B, C = e * i - f * h, -(d * i - f * g), d * h - e * g
    det = a * A + b * B + c * C
    if abs(det) < 1e-12:
        return None
    k = 1.0 / det
    return (A * k, -(b * i - c * h) * k, (b * f - c * e) * k,
            B * k, (a * i - c * g) * k, -(a * f - c * d) * k,
            C * k, -(a * h - b * g) * k, (a * e - b * d) * k)


class Escena:
    """Pinta superfícies del món sobre `cv` (Canvas o Canvas2x), de lluny a prop, i recorda qui ha pintat cada píxel."""

    def __init__(self, cv, cam, llums=(), ambient=0.0):
        self.cv, self.cam, self.llums, self.ambient = cv, cam, list(llums), ambient
        self.S = cv.S
        # 0 = ningú; si no, l'índex de la superfície + 1 (de 16 bits: una sala gran en té més de 255)
        self.amo = array('H', bytes(2 * cv.w * cv.h))
        self.ids = ['']
        self.caixes = {}                                 # id → (u0, v0, u1, v1) en coordenades de sala
        self.mapes = {}                                  # índex → (array X, Y, TX, TY, k): per reprojectar capes
        self.retalls = None                              # (u0, v0, u1, v1): només es pinta dins (None: a tot arreu)
        self._px = getattr(cv, 'px', None) or cv.put     # un píxel real (al Canvas d'1×, un de sala)

    # ── utilitats ──
    def _index(self, sid):
        self.ids.append(sid)
        return len(self.ids) - 1

    def _caixa(self, sid, pts):
        us, vs = [p[0] for p in pts], [p[1] for p in pts]
        b = (min(us), min(vs), max(us), max(vs))
        o = self.caixes.get(sid)
        self.caixes[sid] = b if o is None else (min(o[0], b[0]), min(o[1], b[1]), max(o[2], b[2]), max(o[3], b[3]))

    def llum(self, P, n):
        return self.ambient + sum(l(P, n) for l in self.llums)

    def _scan(self, poly):
        """Píxels reals (X, Y) dins el polígon convex `poly` (coordenades reals)."""
        ys = [p[1] for p in poly]
        h, w = self.cv.h, self.cv.w
        for Y in range(max(0, int(min(ys))), min(h, int(max(ys)) + 1)):
            yc = Y + 0.5
            xs = []
            for (xa, ya), (xb, yb) in zip(poly, poly[1:] + poly[:1]):
                if (ya <= yc < yb) or (yb <= yc < ya):
                    xs.append(xa + (yc - ya) * (xb - xa) / (yb - ya))
            if len(xs) < 2:
                continue
            xs.sort()
            for X in range(max(0, math.ceil(xs[0] - 0.5)), min(w, math.floor(xs[-1] - 0.5) + 1)):
                yield X, Y

    def _retalla(self, Ps, prop=2.0):
        """Els cantons d'un polígon del món retallats pel pla de davant de la càmera (z ≥ prop), projectats."""
        V = [self.cam.vista(P) for P in Ps]
        out = []
        for A, B in zip(V, V[1:] + V[:1]):
            if A[2] >= prop:
                out.append(A)
            if (A[2] >= prop) != (B[2] >= prop):
                k = (prop - A[2]) / (B[2] - A[2])
                out.append((A[0] + (B[0] - A[0]) * k, A[1] + (B[1] - A[1]) * k, prop))
        f, (cu, cv) = self.cam.f, self.cam.centre
        return [(cu + f * x / z, cv - f * y / z, z) for x, y, z in out]

    # ── superfícies ──
    def quad(self, sid, P0, P1, P2, P3, ramp=None, lvl=3.0, tex=None, ombra=None, dues_cares=False, tint=None,
             forma=None):
        """Un rectangle del món. `ramp` + `lvl(s, t, P)` (s, t en unitats del món des de P0) o bé `tex` = (imatge
        d'un dibuix pla a la resolució del llenç, (x0, y0, x1, y1) en píxels de sala del dibuix pla). `ombra(s, t)`:
        nivells que es resten (o un factor que enfosqueix la textura). `forma(s, t)` → False: aquell punt no es pinta
        (un disc, una el·lipse dins el rectangle). No es pinta si es veu d'esquena."""
        Ps = (P0, P1, P2, P3)
        e1, e3 = _sub(P1, P0), _sub(P3, P0)
        n = _norm(_cross(e1, e3))                        # cap a la càmera si P0..P3 van en sentit horari vist de cara
        if _dot(n, _sub(self.cam.ull(), P0)) < 0:
            if not dues_cares:
                return
            n = (-n[0], -n[1], -n[2])
        L1, L3 = math.sqrt(_dot(e1, e1)), math.sqrt(_dot(e3, e3))
        S = self.S
        proj = self._retalla(Ps)
        if len(proj) < 3:
            return
        scr = [(p[0] * S, p[1] * S) for p in proj]
        inv = _inversa(self.cam.homografia(P0, e1, e3, S))
        if inv is None:
            return
        self._caixa(sid, proj)
        idx = self._index(sid)
        a, b, c, d, e, f, g, h, i = inv
        cv, amo, W = self.cv, self.amo, self.cv.w
        P = cv.P
        px = getattr(cv, 'px', None) or cv.put             # (Canvas a 1×: un píxel real és un de sala)
        llum_cache = {}
        if tex is not None:
            img, (tx0, ty0, tx1, ty1) = tex[:2]
            TS = tex[2] if len(tex) > 2 else S           # píxels de la textura per píxel de sala (pot ser > S)
            src = img.load()
            tw, th = img.size
            mostra = max(1, TS // S)                     # una textura més fina que el llenç: es fa la mitjana
            rec = (array('i'), array('i'), array('i'), array('i'), array('f'))
        for X, Y in self._scan(scr):
            if self.retalls is not None:
                u0, v0, u1, v1 = self.retalls
                if not (u0 * S <= X < u1 * S and v0 * S <= Y < v1 * S):
                    continue
            xc, yc = X + 0.5, Y + 0.5
            wq = g * xc + h * yc + i
            s = (a * xc + b * yc + c) / wq
            t = (d * xc + e * yc + f) / wq
            s = 0.0 if s < 0 else 1.0 if s > 1 else s
            t = 0.0 if t < 0 else 1.0 if t > 1 else t
            if forma is not None and not forma(s * L1, t * L3):
                continue
            key = (int(s * 24), int(t * 24))             # la llum varia a poc a poc: es calcula en una graella
            lv = llum_cache.get(key)
            if lv is None:
                Pw = (P0[0] + e1[0] * s + e3[0] * t, P0[1] + e1[1] * s + e3[1] * t, P0[2] + e1[2] * s + e3[2] * t)
                lv = llum_cache[key] = self.llum(Pw, n)
            if tex is None:
                Pw = (P0[0] + e1[0] * s + e3[0] * t, P0[1] + e1[1] * s + e3[1] * t, P0[2] + e1[2] * s + e3[2] * t)
                v = lvl(s * L1, t * L3, Pw) if callable(lvl) else lvl
                if ombra is not None:
                    v -= ombra(s * L1, t * L3)
                px(X, Y, ramp, v + lv, lit=0)
            else:
                TX = int((tx0 + (tx1 - tx0) * s) * TS)
                TY = int((ty0 + (ty1 - ty0) * t) * TS)
                TX = min(tw - mostra, max(0, TX))
                TY = min(th - mostra, max(0, TY))
                if mostra == 1:
                    col = src[TX, TY]
                else:
                    r_ = g_ = b_ = a_ = n_ = 0
                    for yy in range(TY, TY + mostra):
                        for xx in range(TX, TX + mostra):
                            c_ = src[xx, yy]
                            if c_[3] >= 128:
                                r_ += c_[0]; g_ += c_[1]; b_ += c_[2]; n_ += 1
                    if n_ * 2 < mostra * mostra:
                        continue
                    col = (r_ // n_, g_ // n_, b_ // n_, 255)
                if col[3] < 128:
                    continue
                k = 1.0 + lv * 0.18                       # la llum del món, sobre la que ja porta el dibuix pla
                if ombra is not None:
                    k *= 1.0 - ombra(s * L1, t * L3)
                k += (B4[Y & 3][X & 3] - 0.5) * 0.06     # (a quadres: sense franges)
                if tint is not None:
                    col = tint(col, s * L1, t * L3)
                P[X, Y] = (min(255, int(col[0] * k)), min(255, int(col[1] * k)), min(255, int(col[2] * k)), 255)
                for arr, val in zip(rec, (X, Y, TX, TY)):
                    arr.append(val)
                rec[4].append(k)
            amo[Y * W + X] = idx
        if tex is not None:
            self.mapes[idx] = rec
        return idx

    def caixa(self, sid, x0, x1, y0, y1, z0, z1, ramp, lvl=3.0, cares=None):
        """Un paral·lelepípede alineat amb els eixos del món: les cares que es veuen. `cares`: {'davant', 'dalt',
        'esquerra', 'dreta', 'darrere', 'sota'} → (ramp, lvl) o kwargs de `quad` (p. ex. una textura)."""
        cares = cares or {}
        F = {
            'darrere': ((x1, y1, z1), (x0, y1, z1), (x0, y0, z1), (x1, y0, z1)),
            'davant': ((x0, y1, z0), (x1, y1, z0), (x1, y0, z0), (x0, y0, z0)),
            'esquerra': ((x0, y1, z1), (x0, y1, z0), (x0, y0, z0), (x0, y0, z1)),
            'dreta': ((x1, y1, z0), (x1, y1, z1), (x1, y0, z1), (x1, y0, z0)),
            'dalt': ((x0, y1, z1), (x1, y1, z1), (x1, y1, z0), (x0, y1, z0)),
            'sota': ((x0, y0, z0), (x1, y0, z0), (x1, y0, z1), (x0, y0, z1)),
        }
        # de lluny a prop: primer les cares de darrere (quad ja descarta les que es veuen d'esquena)
        for nom in ('darrere', 'sota', 'esquerra', 'dreta', 'dalt', 'davant'):
            kw = cares.get(nom, {'ramp': ramp, 'lvl': lvl})
            self.quad(sid, *F[nom], **kw)

    def caixa_girada(self, sid, cx, cz, w, d, h, ang, ramp, lvl=3.0, y0=0.0, cares=None):
        """Una caixa damunt el terra (o a l'alçada `y0`), centrada a (cx, cz) i girada `ang` radians al voltant de la
        vertical: per als mobles que no van a 90° de la paret. `cares`: 'dalt', 'davant', 'darrere', 'esquerra',
        'dreta' (les del costat de -z, +z, -x, +x abans de girar) → kwargs de `quad`."""
        c, s_ = math.cos(ang), math.sin(ang)

        def P(lx, y, lz):
            return (cx + lx * c - lz * s_, y, cz + lx * s_ + lz * c)
        a, b, y1 = w / 2, d / 2, y0 + h
        F = {
            'darrere': (P(a, y1, b), P(-a, y1, b), P(-a, y0, b), P(a, y0, b)),
            'davant': (P(-a, y1, -b), P(a, y1, -b), P(a, y0, -b), P(-a, y0, -b)),
            'esquerra': (P(-a, y1, b), P(-a, y1, -b), P(-a, y0, -b), P(-a, y0, b)),
            'dreta': (P(a, y1, -b), P(a, y1, b), P(a, y0, b), P(a, y0, -b)),
            'dalt': (P(-a, y1, b), P(a, y1, b), P(a, y1, -b), P(-a, y1, -b)),
        }
        cares = cares or {}
        for nom in ('darrere', 'esquerra', 'dreta', 'davant', 'dalt'):
            self.quad(sid, *F[nom], **cares.get(nom, {'ramp': ramp, 'lvl': lvl}))

    def cable(self, sid, punts, ramp, lvl, gruix=2.0):
        """Un cable (o un tub prim) que passa pels punts del món: una corba suau, del gruix que toca a cada distància."""
        S = self.S
        pts = []
        for (ax, ay, az), (bx, by, bz) in zip(punts, punts[1:]):
            for k in range(8):
                t = k / 8
                pts.append((ax + (bx - ax) * t, ay + (by - ay) * t, az + (bz - az) * t))
        pts.append(punts[-1])
        for A, B in zip(pts, pts[1:]):
            a, b = self.cam.projecta(A), self.cam.projecta(B)
            r = max(0.5, gruix * self.cam.escala(A) / 2)
            n = max(1, int(math.hypot(b[0] - a[0], b[1] - a[1]) * S))
            for i in range(n + 1):
                u, v = a[0] + (b[0] - a[0]) * i / n, a[1] + (b[1] - a[1]) * i / n
                for dy in range(-int(r * S), int(r * S) + 1):
                    X, Y = int(u * S), int(v * S) + dy
                    if 0 <= X < self.cv.w and 0 <= Y < self.cv.h:
                        f = dy / max(1.0, r * S)
                        self._px(X, Y, ramp, lvl - f * 1.2, lit=0)
                        self.amo[Y * self.cv.w + X] = self._idx_de(sid)

    def tub(self, sid, A, B, r, ramp, lvl=3.0, brides=0, llum_dir=(-0.4, 1.0)):
        """Un tub cilíndric gruixut de A a B (punts del món): cada secció es pinta com un disc projectat, amb la llum
        de costat (més clar cap a `llum_dir`, en pantalla) i, si `brides` > 0, una brida cada `brides` unitats."""
        S = self.S
        L = math.sqrt(_dot(_sub(B, A), _sub(B, A)))
        n = max(2, int(L / 1.5))
        idx = self._idx_de(sid)
        lx, ly = llum_dir
        ln = math.hypot(lx, ly) or 1
        lx, ly = lx / ln, ly / ln
        for k in range(n, -1, -1):                       # del lluny al prop
            t = k / n
            P = (A[0] + (B[0] - A[0]) * t, A[1] + (B[1] - A[1]) * t, A[2] + (B[2] - A[2]) * t)
            u, v, _ = self.cam.projecta(P)
            rr = r * self.cam.escala(P)
            brida = brides and (t * L) % brides < 2.0
            R = rr * (1.18 if brida else 1.0)
            for Y in range(int((v - R) * S), int((v + R) * S) + 1):
                for X in range(int((u - R) * S), int((u + R) * S) + 1):
                    dx, dy = (X / S - u) / R, (Y / S - v) / R
                    d2 = dx * dx + dy * dy
                    if d2 > 1 or not (0 <= X < self.cv.w and 0 <= Y < self.cv.h):
                        continue
                    nz = math.sqrt(1 - d2)
                    val = lvl + (-dx * lx - dy * ly) * 1.6 + nz * 0.6 - (0.0 if not brida else -0.6)
                    self._px(X, Y, ramp, val, lit=0)
                    self.amo[Y * self.cv.w + X] = idx

    def roca(self, sid, P, r, ramp, lvl=2.6, llum_dir=(0.7, -0.6), aplana=0.62, seed=1):
        """Una roca (o una mata, un monticle): un bony de radi `r` assegut a terra a P, amb la llum de costat i la vora
        irregular (soroll). Es pinta en pantalla, a la mida que toca a aquella distància."""
        from hd.rooms.exterior import fbm
        S = self.S
        k = self.cam.escala(P)
        u, v, _ = self.cam.projecta(P)
        R = r * k
        H = R * aplana * 1.6
        idx = self._idx_de(sid)
        lx, ly = llum_dir
        for Y in range(int((v - H) * S), int(v * S) + 1):
            for X in range(int((u - R * 1.2) * S), int((u + R * 1.2) * S) + 1):
                if not (0 <= X < self.cv.w and 0 <= Y < self.cv.h):
                    continue
                dx, dy = (X / S - u) / R, (Y / S - v) / H           # dy: de -1 (dalt) a 0 (terra)
                a = math.atan2(dy, dx)
                vora = 1.0 + (fbm(math.cos(a) * 1.5 + seed, math.sin(a) * 1.5, seed) - 0.5) * 0.5
                d2 = dx * dx + (dy * 1.0) ** 2
                if d2 > vora * vora:
                    continue
                nz = math.sqrt(max(0.0, 1 - d2 / (vora * vora)))
                val = lvl + (dx * lx + dy * ly) * 1.4 + nz * 0.5 + (fbm(X / (3.0 * S), Y / (2.0 * S), seed + 3) - 0.5) * 1.2
                if dy > -0.12:
                    val -= 0.8                                      # la base, a l'ombra
                self._px(X, Y, ramp, val, lit=0)
                self.amo[Y * self.cv.w + X] = idx

    def _idx_de(self, sid):
        if sid not in self.ids:
            self.ids.append(sid)
        return self.ids.index(sid)

    def claror(self, P0, P1, P2, P3, col, fn):
        """Barreja cap a `col` (factor 0..1 de `fn(s, t)`) el que ja hi ha pintat dins el rectangle del món: la llum que
        entra per una porta o una finestra i s'escampa pel terra."""
        S = self.S
        proj = self._retalla((P0, P1, P2, P3))
        if len(proj) < 3:
            return
        scr = [(p[0] * S, p[1] * S) for p in proj]
        e1, e3 = _sub(P1, P0), _sub(P3, P0)
        inv = _inversa(self.cam.homografia(P0, e1, e3, S))
        if inv is None:
            return
        L1, L3 = math.sqrt(_dot(e1, e1)), math.sqrt(_dot(e3, e3))
        a, b, c, d, e, f, g, h, i = inv
        P = self.cv.P
        for X, Y in self._scan(scr):
            xc, yc = X + 0.5, Y + 0.5
            wq = g * xc + h * yc + i
            s, t = (a * xc + b * yc + c) / wq, (d * xc + e * yc + f) / wq
            if not (0 <= s <= 1 and 0 <= t <= 1):
                continue
            k = fn(s * L1, t * L3) + (B4[Y & 3][X & 3] - 0.5) * 0.06
            if k <= 0:
                continue
            k = min(1.0, k)
            o = P[X, Y]
            P[X, Y] = (int(o[0] + (col[0] - o[0]) * k), int(o[1] + (col[1] - o[1]) * k), int(o[2] + (col[2] - o[2]) * k),
                       o[3])

    def sprite(self, sid, img, peu_img, peu, escala_img=1.0, img_S=None):
        """Un dibuix pla dret (un seient, una bombeta): `img` a la resolució del llenç, `peu_img` = el punt de la imatge
        (en píxels de sala del dibuix pla) que toca a `peu` del món. `escala_img`: unitats del món per píxel de sala
        del dibuix (1: el dibuix pla ja és a la mida «normal»)."""
        from pixels import nearest
        k = self.cam.escala(peu) * escala_img
        u, v, _ = self.cam.projecta(peu)
        S = self.S
        f = S / (img_S or S)                             # (una imatge més fina que el llenç: es redueix fent la mitjana)
        w, h = max(1, round(img.width * k * f)), max(1, round(img.height * k * f))
        im = nearest(img, (w, h)) if f * k >= 1 or f == 1 else img.resize((w, h), Image.Resampling.BOX)
        ox, oy = round(u * S - peu_img[0] * S * k), round(v * S - peu_img[1] * S * k)
        self._caixa(sid, [(ox / S, oy / S), ((ox + w) / S, (oy + h) / S)])
        idx = self._index(sid)
        src, P, amo, W = im.load(), self.cv.P, self.amo, self.cv.w
        for y in range(h):
            Y = oy + y
            if not 0 <= Y < self.cv.h:
                continue
            for x in range(w):
                X = ox + x
                if not 0 <= X < W:
                    continue
                c = src[x, y]
                if c[3] < 128:
                    continue
                P[X, Y] = c
                amo[Y * W + X] = idx
        return idx

    def linia(self, A, B, ramp, lvl, thin=False):
        a, b = self.cam.projecta(A), self.cam.projecta(B)
        if self.S > 1:
            self.cv.line(a[0], a[1], b[0], b[1], ramp, lvl, lit=0, thin=thin)
        else:
            self.cv.line(a[0], a[1], b[0], b[1], ramp, lvl, lit=0)

    def foscor(self, sid, P0, P1, P2, P3, fn):
        """Enfosqueix (factor 0..1 de `fn(s, t)`) el que ja hi ha pintat dins el rectangle del món: ombres projectades al
        terra, la foscor dels racons. No canvia l'amo dels píxels."""
        S = self.S
        proj = self._retalla((P0, P1, P2, P3))
        if len(proj) < 3:
            return
        scr = [(p[0] * S, p[1] * S) for p in proj]
        e1, e3 = _sub(P1, P0), _sub(P3, P0)
        inv = _inversa(self.cam.homografia(P0, e1, e3, S))
        if inv is None:
            return
        L1, L3 = math.sqrt(_dot(e1, e1)), math.sqrt(_dot(e3, e3))
        a, b, c, d, e, f, g, h, i = inv
        P = self.cv.P
        for X, Y in self._scan(scr):
            xc, yc = X + 0.5, Y + 0.5
            wq = g * xc + h * yc + i
            s, t = (a * xc + b * yc + c) / wq, (d * xc + e * yc + f) / wq
            if not (0 <= s <= 1 and 0 <= t <= 1):
                continue
            k = fn(s * L1, t * L3)
            if k <= 0:
                continue
            if k < 0.5 and k * 2 < B4[Y & 3][X & 3]:     # vores a quadres
                continue
            o = P[X, Y]
            m = 1 - min(0.85, k)
            P[X, Y] = (int(o[0] * m), int(o[1] * m), int(o[2] * m), o[3])

    # ── capes ──
    def capa(self, flat, sids=None):
        """Un dibuix pla del mateix sistema que les textures (un decorat, un fotograma: transparent on no hi ha res)
        projectat per les superfícies amb textura (totes, o les de `sids`), només on aquella superfície és la que es
        veu. → imatge RGBA de la mida del llenç."""
        out = Image.new('RGBA', (self.cv.w, self.cv.h), (0, 0, 0, 0))
        dst, src, W = out.load(), flat.load(), self.cv.w
        fw, fh = flat.size
        for idx, (Xs, Ys, TXs, TYs, ks) in self.mapes.items():
            if sids is not None and self.ids[idx] not in sids:
                continue
            for X, Y, TX, TY, k in zip(Xs, Ys, TXs, TYs, ks):
                if self.amo[Y * W + X] != idx or TX >= fw or TY >= fh:
                    continue
                col = src[TX, TY]
                if col[3]:
                    dst[X, Y] = (min(255, int(col[0] * k)), min(255, int(col[1] * k)), min(255, int(col[2] * k)), col[3])
        return out
