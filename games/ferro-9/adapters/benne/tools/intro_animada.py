#!/usr/bin/env python3
"""
Intro animada de Ferro-9 (vídeo de pixel art, 640×360), feta com la de Ni un ou: el pròleg del joc, en moviment.

  Pla A, la portada: fosa des del negre, la fàbrica i La Gavina partides pel tall de llum; el títol apareix tramat,
  el destell el travessa i s'encenen les dues espurnes.
  Pla B, l'espai: La Gavina plana sobre la Terra; una llançadora hi puja des de baix i s'acosta al moll.
  Pla C, la cel·la 9: la Vet dorm, el panell vibra; dues sacsejades, i a la segona la Vet obre els ulls.
  «Cent vint anys abans...», sobre negre.
  Pla D, la fàbrica de nit: fum, finestres, el canal. L'Iri passa sota el fanal i entra al torn de nit pel portal
  dels forns (es reflecteix a l'aigua).
  Pla E, la cambra de ressonància: l'alarma gira i ho tenyeix tot de vermell. Entra l'Iri, s'atura davant de la
  cambra; el camp es desperta (arcs violeta entre les bobines, cada cop més), i un flaix blanc ho acaba. Negre.

Tot es dibuixa fotograma a fotograma amb les mateixes funcions que les sales (hd640/rooms/portada.py, proleg_*.py):
la llançadora, els ulls de la Vet, l'Iri petita, l'Iri a la cambra i el camp són els de les capes del pròleg del joc,
i ffmpeg ho munta amb la música (gavina.ogg i, des de «Cent vint anys abans», fabrica.ogg) i els sons del pròleg.

Ús: python3 intro_animada.py <carpeta de sortida> [--fps 12] [--only 120,240]
"""
import argparse
import functools
import math
import os
import subprocess
import sys
from multiprocessing import Pool
from pathlib import Path

import numpy as np
from PIL import Image

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))

import hd640  # noqa: E402,F401  (posa la llibreria a 640×360)
import room_designs  # noqa: E402,F401  (carrega les sales en l'ordre bo)
from hd.pix import Canvas, W, H  # noqa: E402
from hd640.font import font640, text_width, draw_text  # noqa: E402
from hd640.rooms import portada as po  # noqa: E402
from hd640.rooms import proleg_gavina as ga  # noqa: E402
from hd640.rooms import proleg_cella as ce  # noqa: E402
from hd640.rooms import proleg_fabrica as fa  # noqa: E402
from hd640.rooms import proleg_cambra as ca  # noqa: E402

GAME = HERE.parent.parent.parent
AUDIO = GAME / 'game' / 'audio'

# ─── Temps (segons) ─────────────────────────────────────────────────────────
# Pla A, la portada
A_FADE_IN = (0.0, 1.4)
A_TITLE_IN = (1.4, 2.6)
A_GLINT = (3.0, 4.1)
A_LEN = 6.6
# Pla B, l'espai (comença amb una fosa tramada des de A)
B0 = 5.8
B_LEN = 8.0
# Pla C, la cel·la (fosa tramada des de B)
C0 = B0 + B_LEN - 0.9
C_SHAKES = ((1.7, 2.4), (3.9, 4.7))         # les dues sacsejades de la paret
C_EYES = 4.9                                 # la Vet obre els ulls
C_BLINK = (5.9, 6.05)
C_LEN = 7.6
C_FADE_OUT = (C_LEN - 1.0, C_LEN)
# «Cent vint anys abans...»
T_CAP = C0 + C_LEN
CAP_IN = (0.3, 1.0)
CAP_OUT = (2.1, 2.7)
CAP_LEN = 2.9
# Pla D, la fàbrica
D0 = T_CAP + CAP_LEN
D_FADE_IN = (0.0, 1.2)
D_WALK = (0.5, 5.9)                          # l'Iri camina pel moll, del fanal al portal
D_ENTER = (5.9, 7.0)                         # es gira i entra a la llum
D_LEN = 8.6
# Pla E, la cambra (fosa tramada des de D)
E0 = D0 + D_LEN - 0.8
E_WALK = (1.0, 5.2)                          # entra per l'esquerra i va fins davant de la cambra
E_TURN = 5.5                                 # es gira cap a la cambra
E_FIELD = (6.0, 10.2)                        # el camp es desperta
E_FLASH = (10.0, 10.5)
E_WHITE = (10.5, 11.0)
E_DARK = (11.0, 12.2)
E_LEN = 12.6
TOTAL = E0 + E_LEN


def ease(t):
    t = max(0.0, min(1.0, t))
    return t * t * (3 - 2 * t)


def seg(t, ab):
    return ease((t - ab[0]) / (ab[1] - ab[0]))


def lin(t, ab):
    return max(0.0, min(1.0, (t - ab[0]) / (ab[1] - ab[0])))


def lerp(a, b, k):
    return a + (b - a) * k


# Bayer 8×8 per a les foses tramades (64 nivells)
def _bayer(n):
    if n == 1:
        return np.zeros((1, 1))
    m = _bayer(n // 2)
    return np.block([[4 * m, 4 * m + 2], [4 * m + 3, 4 * m + 1]])


TH = np.tile((_bayer(8) + 0.5) / 64, (H // 8 + 1, W // 8 + 1))[:H, :W]
BLACK = np.zeros((H, W, 3), np.uint8)
WHITE = np.full((H, W, 3), 255, np.uint8)


def dmix(a, b, k):
    """Fosa tramada: k=0 → a, k=1 → b."""
    if k <= 0:
        return a
    if k >= 1:
        return b
    m = TH < k
    out = a.copy()
    out[m] = b[m]
    return out


def arr(cv):
    return np.asarray(cv.img)[:, :, :3].copy()


def loop(t, period):
    """El moment del bucle d'animació d'una sala (0..1), sense tocar mai el 0 (amb 0, les sales surten quietes)."""
    u = (t / period) % 1.0
    return u if u > 1e-6 else 1e-6


# ─── Pla A: la portada ──────────────────────────────────────────────────────

def shot_a(t):
    tt = loop(t, 3.12)
    cv = Canvas(light=po.LIGHT)
    po.bg(cv, t=tt, titol=False)
    cv.darken(0, 0, W - 1, 120, lambda x, y: 0.45 * (1 - y / 120), dither=False)
    plain = arr(cv)
    k_in = seg(t, A_TITLE_IN)
    if k_in <= 0:
        return plain
    M = po.title(cv, 'FERRO-9', W / 2, 19, m=11, depth=5)
    g = lin(t, A_GLINT)
    if 0 < g < 1:
        po.glint(cv, M, 0.30 + g * 0.32)
    if t >= A_GLINT[0]:                                    # les espurnes, quan hi passa el destell
        xs = [p[0] for p in M]
        po.sparkle(cv, min(xs) + 4, 21, 6 if 0 < g < 0.2 else 5)
        if g > 0.85:
            po.sparkle(cv, max(xs) - 4, 53, 6 if g < 1 else 4 + (int(t * 3) % 2))
    return dmix(plain, arr(cv), k_in)


# ─── Pla B: l'espai ─────────────────────────────────────────────────────────

def shot_b(tb):
    tt = loop(tb, 3.12)
    cv = Canvas(light=ga.LIGHT)
    ga.espai(cv, t=tt)
    ga.lluna(cv, 557, 61, 12)
    ga.terra(cv, ga.EX, ga.EY, ga.ER, t=tt)
    k = lin(tb, (0.0, B_LEN))
    gx, gy = round(lerp(ga.GX + 34, ga.GX - 6, k)), round(lerp(ga.GY + 5, ga.GY - 1, k))
    # la llançadora surt de darrere la Terra i puja cap al moll de La Gavina (sota el cos central)
    sx, sy = ga.llancadora_pos(ease(lin(tb, (0.6, B_LEN - 0.4)) ** 0.8), gx, gy)
    ga.llancadora(cv, sx, sy, tb)
    ga.gavina(cv, gx, gy, ga.GS, t=tt)
    ga.vinyeta(cv)
    return arr(cv)


# ─── Pla C: la cel·la 9 ─────────────────────────────────────────────────────

def vet_eyes(cv, tc):
    """La Vet obre els ulls i parpelleja un cop (el dibuix és el de la capa del pròleg)."""
    if tc < C_EYES or C_BLINK[0] <= tc < C_BLINK[1]:
        return
    ce.ulls_vet(cv, mig=tc < C_EYES + 0.15)


def shot_c(tc):
    cv = Canvas(light=ce.LIGHT)
    # en les sacsejades, la vibració va més de pressa
    boost = sum(seg(tc, (a - 0.3, a)) - seg(tc, (b, b + 0.4)) for a, b in C_SHAKES)
    ce.bg(cv, t=loop(tc + boost * 0.4 * math.sin(tc * 9), 3.0))
    vet_eyes(cv, tc)
    img = arr(cv)
    for a, b in C_SHAKES:
        if a <= tc < b:
            dx = (1 if int(tc * 24) % 2 else -1) * (2 if a == C_SHAKES[1][0] and tc < a + 0.35 else 1)
            img = np.roll(img, dx, axis=1)
            img[:, :2] = img[:, 2:4] if dx > 0 else img[:, :2]
            img[:, -2:] = img[:, -4:-2] if dx < 0 else img[:, -2:]
    return img


# ─── «Cent vint anys abans...» ──────────────────────────────────────────────

@functools.cache
def caption_layer():
    im = Image.new('RGB', (W, H), (0, 0, 0))
    g = font640()
    s = 'Cent vint anys abans...'
    draw_text(im, g, s, round((W - text_width(g, s)) / 2), H // 2 - 8, (236, 226, 196))
    return np.asarray(im).copy()


def shot_cap(tq):
    k = seg(tq, CAP_IN) - seg(tq, CAP_OUT)
    return dmix(BLACK, caption_layer(), k)


# ─── Pla D: la fàbrica ──────────────────────────────────────────────────────

def shot_d(td):
    tt = loop(td, 3.12)
    cv = Canvas(light=fa.LIGHT)
    fa.sky(cv)
    fa.city(cv)
    fa.factory(cv, True, t=tt)
    fa.smoke(cv, [(61, 48, 253), (292, 64, 227), (579, 40, 120)], t=tt)
    fa.quay(cv, t=tt)
    # l'Iri, abans del canal perquè s'hi reflecteixi
    if td < D_WALK[1]:
        k = lin(td, D_WALK)
        fa.iri_petita(cv, round(lerp(fa.IRI_X0, fa.PORTAL_C[0], k)), fa.FEET_Y, td, 1, True)
    elif td < D_ENTER[1]:
        k = lin(td, D_ENTER)
        before = arr(cv)
        fa.iri_petita(cv, fa.PORTAL_C[0], fa.FEET_Y - round(k * 2), td, 0, k < 1)
        if k > 0.35:                                      # s'endinsa a la llum: es fon amb el foc
            after = arr(cv)
            cv.img.paste(Image.fromarray(dmix(after, before, (k - 0.35) / 0.65)))
            cv.P = cv.img.load()
    fa.canal(cv, t=tt)
    fa.barge(cv)
    fa.railing(cv)
    ga.vinyeta(cv, 0.6)
    return arr(cv)


# ─── Pla E: la cambra ───────────────────────────────────────────────────────

def field_level(te):
    return ca.field_level(lin(te, E_FIELD))


def shot_e(te):
    tt = max(te / 1.68, 1e-6)                          # el llum dona mitja volta cada 1,68 s
    bm = ca.beams_at(tt)
    cv = Canvas(light=ca._light(tt))
    ca.bg(cv, t=tt)
    if te >= E_WALK[0]:
        ca.draw_iri(cv, te, beams=bm, k_field=field_level(te) if te >= E_TURN else 0.0, walk=E_WALK)
    ca.field(cv, field_level(te), int(te * 12))
    img = arr(cv)
    img = dmix(img, WHITE, seg(te, E_FLASH))
    if te >= E_WHITE[1]:
        img = dmix(WHITE, BLACK, seg(te, E_DARK))
    return img


# ─── Muntatge ───────────────────────────────────────────────────────────────

def frame(t):
    img = None
    if t < B0 + 1.0:
        img = dmix(BLACK, shot_a(t), seg(t, A_FADE_IN))
    if B0 <= t < C0 + 1.0:
        b = shot_b(t - B0)
        img = b if img is None else dmix(img, b, seg(t, (B0, B0 + 1.0)))
    if C0 <= t < T_CAP:
        c = shot_c(t - C0)
        c = dmix(c, BLACK, seg(t - C0, C_FADE_OUT))
        img = c if img is None else dmix(img, c, seg(t, (C0, C0 + 0.9)))
    if T_CAP <= t < D0:
        img = shot_cap(t - T_CAP)
    if D0 <= t < E0 + 0.8:
        img = dmix(BLACK, shot_d(t - D0), seg(t - D0, D_FADE_IN))
    if t >= E0:
        e = shot_e(t - E0)
        img = e if img is None else dmix(img, e, seg(t, (E0, E0 + 0.8)))
    return img


def work(job):
    i, fps, out = job
    Image.fromarray(frame(i / fps)).save(out / f'{i:04d}.png')
    return i


def audio_graph():
    """Els sons: (fitxer, a quin segon entra, volum, durada o None, en bucle?) i la música."""
    sfx = AUDIO / 'sfx'
    shakes = [C0 + a for a, _ in C_SHAKES]
    return [
        (AUDIO / 'music' / 'gavina.ogg', 0.0, 0.9, T_CAP + 0.4, False, 1.5, 1.8),
        (AUDIO / 'music' / 'fabrica.ogg', T_CAP + 0.2, 0.9, TOTAL - T_CAP - 0.2, False, 1.4, 2.6),
        (sfx / 'vibracio.ogg', shakes[0] - 0.2, 0.6, None, False, 0, 0),
        (sfx / 'vibracio.ogg', shakes[1] - 0.2, 0.85, None, False, 0, 0),
        (sfx / 'alarma.ogg', E0, 0.32, E_FLASH[0] + 0.3, True, 0.8, 0.6),
        (sfx / 'fase.ogg', E0 + E_FLASH[0] - 0.5, 0.9, None, False, 0, 0),
    ]


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('out')
    ap.add_argument('--fps', type=int, default=12)
    ap.add_argument('--only', help='índexs de fotogrames, separats per comes (per provar)')
    a = ap.parse_args()
    out = Path(a.out)
    frames = out / 'frames'
    frames.mkdir(parents=True, exist_ok=True)
    n = int(TOTAL * a.fps)
    idx = [int(x) for x in a.only.split(',')] if a.only else list(range(n))
    with Pool(os.cpu_count()) as pool:
        for k, _ in enumerate(pool.imap_unordered(work, [(i, a.fps, frames) for i in idx], chunksize=2)):
            if k % 24 == 0:
                print(f'{k}/{len(idx)}', flush=True)
    if a.only:
        return
    video = out / 'intro_ferro_9.mp4'
    cmd = ['ffmpeg', '-y', '-loglevel', 'error', '-framerate', str(a.fps), '-i', str(frames / '%04d.png')]
    chains, labels = [], []
    for j, (f, start, vol, dur, looped, fin, fout) in enumerate(audio_graph(), start=1):
        if looped:
            cmd += ['-stream_loop', '-1']
        cmd += ['-i', str(f)]
        c = f'[{j}:a]aformat=sample_rates=44100:channel_layouts=stereo'
        if dur:
            c += f',atrim=0:{dur:.2f}'
        if fin:
            c += f',afade=t=in:d={fin}'
        if fout and dur:
            c += f',afade=t=out:st={dur - fout:.2f}:d={fout}'
        c += f',volume={vol},adelay={int(start * 1000)}:all=1[s{j}]'
        chains.append(c)
        labels.append(f'[s{j}]')
    mixc = f'{"".join(labels)}amix=inputs={len(labels)}:normalize=0:duration=longest,atrim=0:{TOTAL:.2f}[a]'
    cmd += ['-filter_complex', ';'.join(chains + [f'[0:v]scale=1920:1080:flags=neighbor,fps=24[v]', mixc]),
            '-map', '[v]', '-map', '[a]', '-c:v', 'libx264', '-crf', '14', '-pix_fmt', 'yuv420p',
            '-c:a', 'aac', '-b:a', '192k', '-t', f'{TOTAL:.2f}', str(video)]
    subprocess.run(cmd, check=True)
    print(video)


if __name__ == '__main__':
    main()
