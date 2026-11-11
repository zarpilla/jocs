"""
Sala de la Memòria (La Gavina, Vet), a 640×360 (hd/rooms/gavina_memoria.py redibuixat a ×4/3): el museu de
propaganda de la corporació. Plafons nets, terra polit que reflecteix, focus de museu sobre les peces i
l'holograma del Director Aldaia fent de guia.
Llums: l'holograma (cian, la més forta), focus sobre la foto i sobre la vitrina, i la pantalla del mapa.
"""
import math

import hd640  # noqa: F401  (posa la llibreria de dibuix a 640×360)
from hd.pix import Canvas, B4, W, H, mix, STEEL, CYAN, WARN, RED, PAPER, IRON, NAVY
from hd.rooms.gavina_memoria import MUSE, RESIN, SEPIA, FRAME, VELVET, HOLO, SPOT  # noqa: F401
from hd640.rooms.gavina_passadis import (LAMPW, SIGN, CORPG, PILOT, FLOOR_Y, WALL_B, CachedLight, hr, text,
                                         text_w, smile, ambient_frames)

HX, HY = 408, 123                    # centre de l'holograma
SPOT_FOTO = (173, 16)
SPOT_VITRINA = (509, 16)


def spot_cone(sx, sy, tx, ty, rx, k):
    """Taca el·líptica d'un focus de museu sobre la paret (centrada a tx, ty) amb el con que hi baixa."""
    def f(x, y):
        if y < sy:
            return 0.0
        d = math.hypot((x - tx) / rx, (y - ty) / (rx * 0.9))
        v = k * max(0.0, 1 - d) ** 1.2 if d < 1 else 0.0
        # con suau entre el focus i la taca
        if sy < y < ty:
            t = (y - sy) / (ty - sy)
            w = 4 + t * rx * 0.9
            if abs(x - (sx + (tx - sx) * t)) < w:
                v += 0.35 * k * (1 - abs(x - (sx + (tx - sx) * t)) / w) * t
        return v
    return f


def holo_light(x, y):
    d = math.hypot(x - HX, (y - HY) * 0.7)
    return 2.4 * max(0.0, 1 - d / 160) ** 1.6


LIGHT = CachedLight(ambient=0.0, vignette=(85, 40), floor_fade=(264, 45))
LIGHT.add(spot_cone(*SPOT_FOTO, 173, 88, 112, 2.4))
LIGHT.add(spot_cone(*SPOT_VITRINA, 509, 128, 83, 2.4))
LIGHT.add(lambda x, y: 0.9 * max(0.0, 1 - math.hypot((x - 293) / 267, (y - 233) / 40)) if y >= FLOOR_Y else 0.0)
LIGHT.add(holo_light)
LIGHT.point(292, 85, r=93, k=0.8)                                     # pantalla del mapa


def museum_wall(cv, x0, x1):
    pw = 64
    SOC = [3.6, 2.6, 1.6, 1.4, 1.3, 1.2, 1.1, 1.0, 0.8, 0.4]
    for y in range(0, FLOOR_Y):
        for x in range(x0, x1 + 1):
            px = (x - 5) % pw
            lvl = 2.7 + (hr((x - 5) // pw, 2) - 0.5) * 0.15 + (hr(x // 2, y // 3, 4) - 0.5) * 0.06
            if y < 13:
                lvl = 1.2 + (0.8 if y in (9, 10) else 0)
            elif y == 13:
                lvl = 4.0
            elif y == 14:
                lvl = 3.0
            elif y < 17:
                lvl = 1.0
            elif y < 149:
                if px == 0:
                    lvl = 1.2                                               # junta d'ombra entre plafons
                elif px == 1:
                    lvl += 0.8
                elif px == pw - 1:
                    lvl -= 0.6
                lvl -= max(0.0, 1 - (y - 17) / 21) * 1.2
            elif y < 154:
                lvl = [4.6, 4.2, 3.6, 2.6, 1.4][y - 149]                    # passamà
            elif y < 195:
                lvl = 2.6 + (0.2 if px < 2 else 0)
                if px == 0:
                    lvl = 1.4
                if y == 154:
                    lvl -= 0.6
            else:
                lvl = SOC[y - 195]                                          # sòcol fosc
            cv.put(x, y, MUSE, lvl)
    for x in range(x0, x1 + 1):                                             # cargolets del passamà
        if (x - 5) % pw == pw // 2:
            cv.put(x, 151, MUSE, 6.0)


def resin_floor(cv):
    vx, vy, S, K = 320, 40, 1.7, 933.3
    for y in range(FLOOR_Y, H):
        d = y - vy
        v = K / d
        vi = math.floor(v)
        fv = (vi + 1 - v) * d * d / K
        for x in range(W):
            u = (x - vx) / d * S
            ui = math.floor(u)
            fu = (u - ui) * d / S
            lvl = 3.0 + (hr(ui, vi, 7) - 0.5) * 0.25
            if fu < 1 or fv < 1:
                lvl = 1.4
            elif fu < 2 or fv < 2:
                lvl += 0.2                                                  # el cantell polit de la junta
            if y < 213:
                lvl -= (213 - y) / 8 * 0.9
            cv.put(x, y, RESIN, lvl)


def reflect(cv, k=0.18):
    """Reflex del terra polit: barreja amb la paret capgirada."""
    for y in range(FLOOR_Y, 275):
        sy = 2 * WALL_B - y
        a = k * max(0.0, 1 - (y - FLOOR_Y) / 64)
        for x in range(W):
            if a > B4[y & 3][x & 3] * 0.45:
                s = cv.P[x, sy]
                o = cv.P[x, y]
                if sum(s[:3]) > sum(o[:3]):
                    cv.P[x, y] = mix(o, s, a) + (255,)


def bg(cv, mira=False, t=0.0):
    tt = t                                   # (dins la funció, `t` es fa servir per a altres coses)
    ph = 2 * math.pi * tt
    museum_wall(cv, 0, W - 1)
    resin_floor(cv)

    # ─── Rètol del sostre ─────────────────────────────────────────────────
    title = 'LA GAVINA · AQUÍ VA COMENÇAR TOT'
    tw = text_w(title)
    tx = 293 - tw // 2
    cv.rect(tx - 19, 18, tx + tw + 5, 32, CORPG, lambda x, y: 2.5 - (0.5 if y == 32 else 0), 0.2)
    cv.hline(tx - 19, tx + tw + 5, 18, CORPG, 4.5, 0.2)
    text(cv, tx, 22, title, SIGN, 4.5, 0)
    smile(cv, tx - 10, 25, 5, lit=0, lvl=3.8)
    cv.darken(tx - 19, 33, tx + tw + 5, 35, 0.4)
    for sx in (tx - 4, tx + tw - 8):                                        # els cables que el pengen
        cv.vline(sx, 16, 17, IRON, 2.0)

    # ─── Focus de museu al carril del sostre ──────────────────────────────
    cv.hline(93, 560, 14, IRON, 3.0)
    cv.hline(93, 560, 15, IRON, 1.4)
    for sx, sy in (SPOT_FOTO, SPOT_VITRINA):
        cv.rect(sx - 3, 14, sx + 3, 17, IRON, lambda x, y: 3.4 if y == 14 else 2.6)
        cv.poly([(sx - 7, 19), (sx + 4, 17), (sx + 7, 25), (sx - 4, 28)], IRON, lambda x, y: 3.6 - (x - sx) * 0.2)
        cv.line(sx - 6, 19, sx + 3, 17, IRON, 4.8)                           # el cantell de dalt, amb llum
        for k in range(3):
            cv.line(sx - 6 + k * 3, 21 + k, sx - 3 + k * 3, 20 + k, IRON, 1.6)   # aletes de refredar
        cv.line(sx - 4, 28, sx + 7, 25, SPOT, 0, 0)
        cv.line(sx - 3, 27, sx + 6, 24, SPOT, 0, 0)
        cv.glow(sx + 1, 28, 13, (255, 240, 210), 0.6)

    # ─── Porta cap al passadís (10..88 × 61..208) ─────────────────────────
    DX0, DX1, DT = 16, 81, 80
    cv.rect(DX0 - 5, DT - 5, DX1 + 5, WALL_B, MUSE, lambda x, y: 4.6 if x < DX0 - 3 or y < DT - 3 else (1.6 if x > DX1 + 2 else 3.0))
    cv.rect(DX0 - 1, DT - 1, DX1 + 1, WALL_B, STEEL, 0.4)
    mid = (DX0 + DX1) // 2
    for y in range(DT, FLOOR_Y):
        for x in range(DX0, DX1 + 1):
            side = x <= mid
            u = (x - DX0) / (mid - DX0) if side else (x - mid - 1) / (DX1 - mid - 1)
            lvl = 3.2 + (0.6 - u * 0.9) - (0.3 if not side else 0)
            if x in (mid, mid + 1):
                lvl = 1.0 if x == mid else 4.2
            if 128 <= y <= 149 and (x - DX0 in range(7, 25) or DX1 - x in range(7, 25)):
                lvl = 2.0 + (0.8 if y == 128 else 0) + (0.4 if (x + y) % 7 == 0 else 0)   # vidre esmerilat
            if y > 196:
                lvl -= 0.5                                                  # la xapa de peu
            cv.put(x, y, STEEL, lvl)
    for hx in (mid - 5, mid + 4):
        cv.rect(hx, 144, hx + 1, 163, STEEL, lambda x, y: 6.0 if x == hx else 4.4)
        cv.hline(hx, hx + 1, 164, STEEL, 1.2)
    # rètol de sortida
    cv.rect(29, 63, 69, 74, PILOT, 1.5, 0)
    cv.hline(29, 69, 63, PILOT, 2.0, 0)
    text(cv, 33, 65, 'SORTIDA', PILOT, 3.5, 0)
    cv.glow(49, 69, 24, (90, 255, 140), 0.35)
    # lector d'accés
    cv.rect(DX1 + 9, 131, DX1 + 16, 144, MUSE, lambda x, y: 1.6 if x == DX1 + 16 else 4.0)
    cv.rect(DX1 + 11, 138, DX1 + 14, 141, MUSE, 2.2)
    on = 1.0 if (tt * 2 + 0.37) % 1 < 0.1 else 3.0                        # el pilot s'apaga un instant
    cv.put(DX1 + 12, 134, PILOT, on, 0)
    cv.put(DX1 + 13, 134, PILOT, on - 0.6, 0)

    # ─── Foto del torn de nit (120..226 × 47..136) ────────────────────────
    FX0, FY0, FX1, FY1 = 123, 49, 223, 123
    cv.rect(FX0 + 3, FY0 + 3, FX1 + 4, FY1 + 4, MUSE, 1.4)                  # ombra
    for y in range(FY0, FY1 + 1):
        for x in range(FX0, FX1 + 1):
            dd = min(x - FX0, FX1 - x, y - FY0, FY1 - y)
            if dd > 4:
                continue
            lvl = [2.0, 4.6, 4.0, 3.2, 2.4][dd]
            if (FX1 - x) < 5 or (FY1 - y) < 5:
                lvl -= 0.8
            if dd == 2 and (x + y) % 5 == 0:
                lvl += 0.5                                                  # el daurat gravat del marc
            cv.put(x, y, FRAME, lvl)
    PX0, PY0, PX1, PY1 = FX0 + 5, FY0 + 5, FX1 - 5, FY1 - 5               # 128..218 × 54..118
    # fons de la foto: la nau de la fàbrica, amb la boca d'un forn encesa
    for y in range(PY0, PY1 + 1):
        for x in range(PX0, PX1 + 1):
            lvl = 2.6 + (y - PY0) / 53 + (hr(x // 3, y // 3, 3) - 0.5) * 0.2 + (hr(x, y, 9) - 0.5) * 0.15
            if (x - PX0) % 16 == 0 and y < PY0 + 35:
                lvl -= 0.6                                                  # pilars de la nau
            if y < PY0 + 5:
                lvl -= 0.6
            if (y - PY0) == 14 and (x - PX0) % 16 < 14:
                lvl -= 0.3                                                  # la biga del pont grua
            fd = math.hypot(x - 203, y - 75)
            if fd < 12:
                lvl += (1 - fd / 12) * 2.8                                 # la boca del forn
            cv.put(x, y, SEPIA, lvl, 0.3)
    # el torn de nit, en fila
    people = [(139, 0, 37, True), (152, 1, 36, False), (164, 2, 31, False), (177, 3, 39, True), (191, 4, 36, True)]
    for px, k, h, cap in people:
        if k == 2 and not mira:
            continue                                                        # la M. d'Orís: retallada (vegeu el forat)
        top = PY1 - h
        # cos (granota de treball fosca)
        for y in range(top + 9, PY1 + 1):
            half = 4 + (1 if y > top + 12 else 0)
            for x in range(px - half, px + half + 1):
                lvl = 1.4 - (x - px) * 0.08 + (0.6 if x == px - half else 0)
                if y == top + 22 and abs(x - px) < half:
                    lvl -= 0.5                                              # el cinturó
                if x == px and top + 11 < y < top + 21:
                    lvl += 0.3                                              # la cremallera
                cv.put(x, y, SEPIA, lvl, 0.3)
        cv.rect(px - 1, top + 7, px + 1, top + 9, SEPIA, 3.6, 0.3)        # coll
        cv.disc(px, top + 4, 3.3, 4, SEPIA, lambda nx, ny: 4.6 - nx * 0.8 - ny * 0.4, 0.3)
        if cap:
            cv.rect(px - 4, top, px + 3, top + 1, SEPIA, 1.2, 0.3)        # gorra de treball
            cv.hline(px - 5, px - 2, top + 2, SEPIA, 0.8, 0.3)
        else:
            cv.rect(px - 3, top, px + 3, top + 1, SEPIA, 0.8, 0.3)        # cabells
            cv.vline(px - 4, top + 1, top + 5, SEPIA, 0.8, 0.3)
    # la I. (segona): cara ratllada
    ix, itop = 152, PY1 - 36
    for i in range(-4, 5):
        cv.put(ix + i, itop + 4 + i // 2, SEPIA, 6.4, 0.3)
        cv.put(ix + i, itop + 5 - i // 2, SEPIA, 6.0, 0.3)
        cv.put(ix + i + 1, itop + 3 + (i * 3) // 4, SEPIA, 0.4, 0.3)
    # la del costat (M. d'Orís): més baixeta, somrient, amb una trena
    mx, mtop = 164, PY1 - 31
    if mira:
        cv.vline(mx + 4, mtop + 3, mtop + 11, SEPIA, 0.8, 0.3)            # trena
        cv.put(mx + 5, mtop + 11, SEPIA, 1.4, 0.3)
        cv.hline(mx - 1, mx + 1, mtop + 6, SEPIA, 2.0, 0.3)                # somriure
    else:
        # algú la va retallar amb tisores: un forat amb la seva silueta, i a dins el cartró fosc del darrere
        def cut(x, y):
            j = (hr(x, y, 71) - 0.5) * 1.1                                 # tall de tisora, no gaire net
            if y <= mtop + 8:
                return math.hypot((x - mx) / 5.0, (y - mtop - 4) / 5.7) + j * 0.2 < 1
            if y <= mtop + 12:
                return abs(x - mx) <= 3.5 + j
            return abs(x - mx) <= 6.7 + j + (1 if y > mtop + 15 else 0)
        for y in range(mtop - 3, PY1 + 1):
            for x in range(mx - 11, mx + 12):
                if not cut(x, y):
                    continue
                edge = not cut(x - 1, y) or not cut(x, y - 1)
                if edge:
                    cv.put(x, y, SEPIA, 6.2, 0.3)                          # vora blanca del paper tallat
                else:
                    cv.put(x, y, FRAME, 0.9 + (y - mtop) / 40 + (hr(x, y, 72) - 0.5) * 0.3, 0.3)
    # el Cargol, nou de trinca, a la dreta
    cv.rect(204, PY1 - 29, 213, PY1 - 13, SEPIA, lambda x, y: 5.0 - (x - 204) * 0.22, 0.3)   # cos
    cv.hline(204, 213, PY1 - 21, SEPIA, 3.6, 0.3)                                            # la junta del pit
    cv.rect(205, PY1 - 36, 212, PY1 - 31, SEPIA, 5.4, 0.3)                                   # cap
    cv.put(207, PY1 - 34, SEPIA, 0.6, 0.3); cv.put(210, PY1 - 34, SEPIA, 0.6, 0.3)          # ulls
    cv.vline(208, PY1 - 40, PY1 - 37, SEPIA, 4.0, 0.3)                                       # antena
    cv.put(208, PY1 - 41, SEPIA, 6.0, 0.3)
    cv.rect(205, PY1 - 12, 206, PY1, SEPIA, 3.6, 0.3); cv.rect(211, PY1 - 12, 212, PY1, SEPIA, 3.6, 0.3)
    cv.rect(208, PY1 - 26, 209, PY1 - 25, SEPIA, 6.4, 0.3)                                   # la placa, nova
    # taques i vinyeta de foto vella
    cv.darken(PX0, PY0, PX1, PY1, lambda x, y: max(0.0, 0.5 - min(x - PX0, PX1 - x, y - PY0, PY1 - y) / 9), dither=False)
    for i in range(5):                                                      # rascades del paper
        sx, sy = PX0 + int(hr(i, 81) * (PX1 - PX0)), PY0 + int(hr(i, 82) * (PY1 - PY0 - 6))
        cv.line(sx, sy, sx + 2, sy + 4, SEPIA, 5.6, 0.3)
    # cartel·la
    cv.rect(144, 127, 201, 133, PAPER, 4.5, 0.3)
    cv.hline(144, 201, 133, PAPER, 3.0, 0.3)
    cv.hline(147, 199, 129, MUSE, 2.5, 0)
    cv.hline(149, 181, 131, MUSE, 3.5, 0)

    # ─── Mapa de La Gavina (232..354 × 40..136) ───────────────────────────
    MX0, MY0, MX1, MY1 = 235, 43, 349, 131
    cv.rect(MX0 - 3, MY0 - 3, MX1 + 3, MY1 + 3, STEEL, lambda x, y: 1.4 if x > MX1 or y > MY1 else (4.4 if x < MX0 - 1 or y < MY0 - 1 else 3.4))
    for y in range(MY0, MY1 + 1):
        for x in range(MX0, MX1 + 1):
            lvl = 1.6 + (0.25 if (x - MX0) % 11 == 0 or (y - MY0) % 11 == 0 else 0) + (y - MY0) / 160
            cv.put(x, y, NAVY, lvl + 1.0, 0.2)

    def mp(x, y, lvl=4.5, rmp=CYAN):
        cv.put(x, y, rmp, lvl, 0)

    text(cv, MX0 + 5, MY0 + 4, 'LA GAVINA', CYAN, 4.5, 0)
    # l'estació: anell de mòduls al voltant d'un nucli
    cx, cy = 284, 83
    for a in range(0, 360, 2):
        mp(round(cx + math.cos(math.radians(a)) * 32), round(cy + math.sin(math.radians(a)) * 17), 3.5)
    for a in range(0, 360, 30):                                             # radis de l'anell
        for k in range(9, 30, 3):
            mp(round(cx + math.cos(math.radians(a)) * k), round(cy + math.sin(math.radians(a)) * k * 0.53), 2.6)
    MODS = [('A', -40), ('B', 30), ('C', 100), ('D', 170), ('E', 240)]
    for name, a in MODS:
        mx_, my_ = round(cx + math.cos(math.radians(a)) * 32), round(cy + math.sin(math.radians(a)) * 17)
        cv.rect(mx_ - 6, my_ - 5, mx_ + 6, my_ + 5, NAVY, 2.5, 0)
        for xx in range(mx_ - 6, mx_ + 7):
            mp(xx, my_ - 5); mp(xx, my_ + 5)
        for yy in range(my_ - 5, my_ + 6):
            mp(mx_ - 6, yy); mp(mx_ + 6, yy)
        text(cv, mx_ - 1, my_ - 3, name, CYAN, 4.5 if name != 'C' else 5.5, 0)
    cv.disc(cx, cy, 7, 4, CYAN, lambda nx, ny: 2.5 + (1.0 if nx * nx + ny * ny > 0.6 else 0), 0)
    # «Vostè és aquí» (estrella al mòdul C)
    sx_, sy_ = round(cx + math.cos(math.radians(100)) * 32) + 10, round(cy + math.sin(math.radians(100)) * 17) - 1
    star_dim = (tt * 3) % 1 >= 0.75                                    # parpelleja
    STAR = ((0, -3), (0, -2), (0, -1), (-3, 0), (-2, 0), (-1, 0), (0, 0), (1, 0), (2, 0), (3, 0), (-1, 1), (0, 1),
            (1, 1), (-1, 2), (1, 2), (-2, 3), (2, 3))
    for dx, dy in STAR:
        cv.put(sx_ + dx, sy_ + dy, WARN, (2.6 if star_dim else 4.5) + (0.6 if (dx, dy) == (0, 0) else 0), 0)
    cv.glow(sx_, sy_, 7, (255, 220, 80), 0.2 if star_dim else 0.6)
    # conducte de servei en discontínua, per sota del mòdul C fins a l'hangar
    hx_, hy_ = 325, 120
    cmx, cmy = round(cx + math.cos(math.radians(100)) * 32), round(cy + math.sin(math.radians(100)) * 17) + 6
    off = int(tt * 12) % 6                                             # la ruta avança cap a l'hangar
    for i in range(0, 46):
        t = i / 45
        if ((i - off) // 3) % 2 == 0:
            x = round(cmx + (hx_ - cmx) * t)
            y = round(cmy + 13 * math.sin(t * math.pi) * 0.8 + (hy_ - cmy) * t)
            cv.put(x, y, WARN, 3.5, 0)
    cv.rect(hx_ - 4, hy_ - 3, hx_ + 7, hy_ + 3, NAVY, 2.5, 0)
    for xx in range(hx_ - 4, hx_ + 8):
        mp(xx, hy_ - 3, 3.5); mp(xx, hy_ + 3, 3.5)
    for yy in range(hy_ - 3, hy_ + 4):
        mp(hx_ - 4, yy, 3.5); mp(hx_ + 7, yy, 3.5)
    # llegenda
    for y in (121, 125):
        cv.hline(MX0 + 5, MX0 + 5 + int(hr(y, 1) * 27) + 13, y, CYAN, 3.5, 0)
    cv.rect(MX0 + 5, 128, MX0 + 7, 129, WARN, 3.5, 0)
    # línia d'escaneig que baixa per la pantalla
    f = tt % 1
    env = math.sin(math.pi * f)
    if env > 0.02:
        ys = int(MY0 + f * (MY1 - MY0))
        cv.tint(MX0, ys, MX1, ys, (150, 215, 255), 0.28 * env)
        cv.tint(MX0, ys - 1, MX1, ys - 1, (150, 215, 255), 0.14 * env)
        cv.tint(MX0, ys - 2, MX1, ys - 2, (150, 215, 255), 0.06 * env)
    cv.glow(292, 87, 61, (90, 170, 255), 0.25)

    # ─── Holograma del Director (370..448 × 47..190) i el sòcol ───────────
    # con de llum del projector
    kc = 0.22 * (1 + 0.15 * math.sin(ph * 2) + 0.06 * math.sin(ph * 5))      # el raig respira
    cone = lambda x, y: max(0.0, 1 - abs(x - HX) / (11 + (195 - y) * 0.26)) if y < 195 else 0  # noqa: E731
    cv.tint(363, 53, 453, 195, (140, 230, 255), lambda x, y: kc * cone(x, y))
    # polsos de llum que pugen pel raig des del sòcol (dos per cicle)
    for f in ((tt * 2) % 1,):
        env = math.sin(math.pi * f)
        if env > 0.02:
            yb = 192 - f * 133
            cv.tint(363, yb - 7, 453, yb + 7, (170, 240, 255),
                    lambda x, y: 0.2 * env * (1 - abs(y - yb) / 8) * cone(x, y))
    _director(cv, tt)
    _socol(cv, tt)

    # ─── Vitrina (472..547 × 116..205) ────────────────────────────────────
    VX0, VX1 = 475, 543
    # pedestal
    cv.rect(VX0 + 3, 161, VX1 - 3, WALL_B, MUSE, lambda x, y: 4.4 - (x - VX0) / 53 - (2.4 if y > 199 else 0) + (0.8 if x == VX0 + 3 else 0))
    cv.hline(VX0 + 1, VX1 - 1, 160, MUSE, 5.2)
    cv.hline(VX0 + 3, VX1 - 3, 161, MUSE, 3.4)
    cv.vline(VX1 - 3, 161, WALL_B, MUSE, 2.0)
    # placa de la peça, al pedestal
    cv.rect(491, 171, 527, 181, SIGN, lambda x, y: 3.5 - (0.6 if y == 181 or x == 527 else 0), 0.3)
    cv.hline(494, 524, 173, MUSE, 2.5, 0)
    cv.hline(494, 515, 176, MUSE, 2.5, 0)
    cv.hline(494, 520, 179, MUSE, 3.0, 0)
    # caixa de vidre
    GT = 119
    for y in range(GT, 160):
        for x in range(VX0, VX1 + 1):
            lvl = 2.6 + (y - GT) / 80
            cv.put(x, y, MUSE, lvl, 0.6)
    # base de vellut i el buit de la clau anglesa
    cv.rect(VX0 + 3, 144, VX1 - 3, 159, VELVET, lambda x, y: 3.4 - (y - 144) * 0.09 + (0.3 if hr(x, y, 51) > 0.85 else 0))
    cv.hline(VX0 + 3, VX1 - 3, 144, VELVET, 4.6)
    for x in range(485, 523):                                         # silueta de la clau (buida)
        cv.put(x, 150, VELVET, 0.6)
        cv.put(x, 151, VELVET, 0.6)
        cv.put(x, 152, VELVET, 1.2)
    cv.disc(485, 151, 4.3, 3.5, VELVET, lambda nx, ny: 0.6 + (0.6 if ny > 0.5 else 0))
    cv.disc(523, 151, 4.5, 3.7, VELVET, lambda nx, ny: 0.6 + (0.6 if ny > 0.5 else 0))
    cv.rect(481, 149, 485, 153, VELVET, 3.4)                         # boca oberta de la clau
    cv.rect(524, 149, 528, 153, VELVET, 3.4)
    # buit de la placa del robot, petit, a la dreta (la placa és un prop)
    cv.rect(529, 145, 537, 151, VELVET, lambda x, y: 2.2 + (y - 145) * 0.12)
    cv.hline(529, 537, 145, VELVET, 1.0)
    cv.vline(529, 145, 151, VELVET, 1.2)
    # cartellet dins la vitrina
    cv.poly([(488, 156), (504, 156), (503, 158), (489, 158)], PAPER, 4.0)
    cv.hline(491, 499, 157, MUSE, 3.0, 0.3)
    # marc d'acer, tapa amb llum interior i reflexos
    cv.rect(VX0 - 1, GT - 4, VX1 + 1, GT - 1, STEEL, lambda x, y: 5.0 - (y - GT + 4) * 0.8)
    cv.hline(VX0 + 3, VX1 - 3, GT, LAMPW, 3.5, 0)
    cv.hline(VX0 + 3, VX1 - 3, GT + 1, LAMPW, 2.0, 0)
    for x in (VX0, VX1):
        cv.vline(x, GT, 159, STEEL, 5.0 if x == VX0 else 2.4)
    cv.vline(VX0 + 1, GT, 159, STEEL, 3.0)
    for i in range(19):
        cv.put(VX0 + 8 + i, 133 - i, LAMPW, 3.0, 0)
        cv.put(VX0 + 12 + i, 139 - i, LAMPW, 2.0, 0)
        cv.put(VX0 + 40 + i // 2, 131 - i, LAMPW, 2.0, 0)
    cv.glow(508, 131, 35, (255, 245, 220), 0.25)
    cv.darken(VX0, WALL_B, VX1 + 5, 211, lambda x, y: 0.8 - (y - WALL_B) / 8)

    # ─── Expositor de fullets (567..623 × 134..205) ───────────────────────
    EX0, EX1 = 571, 617
    for lx in (EX0 + 4, EX1 - 5):
        cv.rect(lx, 181, lx + 1, 208, STEEL, lambda x, y: 3.4 if x == lx else 2.4)
    cv.rect(EX0 + 3, 205, EX1 - 3, 208, STEEL, lambda x, y: 3.2 if y == 205 else 2.2)
    cv.rect(EX0, 141, EX1, 184, STEEL, lambda x, y: 2.2 - (x - EX0) / 80)
    cv.hline(EX0, EX1, 141, STEEL, 4.6)
    cv.hline(EX0, EX1, 184, STEEL, 1.2)
    # capçalera
    cv.rect(EX0 - 1, 132, EX1 + 1, 141, CORPG, lambda x, y: 2.5 + (0.6 if y == 132 else 0), 0.3)
    text(cv, (EX0 + EX1) // 2 - text_w('GAVINA') // 2, 133, 'GAVINA', SIGN, 4.5, 0)
    for row, y0 in enumerate((143, 156, 169)):
        for col, x0 in enumerate((EX0 + 3, EX0 + 25)):
            # fullet: capçalera verda, el somriure i text
            cv.rect(x0, y0, x0 + 19, y0 + 12, SIGN, lambda x, y: 4.5 - (0.6 if x == x0 + 19 else 0), 0.4)
            cv.rect(x0, y0, x0 + 19, y0 + 3, CORPG, 2.5 + (row % 2), 0.2)
            smile(cv, x0 + 5, y0 + 8, 3, lit=0, lvl=3.6)
            cv.hline(x0 + 10, x0 + 16, y0 + 6, MUSE, 2.5, 0)
            cv.hline(x0 + 10, x0 + 15, y0 + 8, MUSE, 2.5, 0)
            cv.hline(x0 + 10, x0 + 16, y0 + 10, MUSE, 3.0, 0)
            # butxaca de plàstic
            cv.hline(x0 - 1, x0 + 20, y0 + 12, STEEL, 4.0)
            cv.hline(x0 - 1, x0 + 20, y0 + 13, STEEL, 2.6)
            cv.put(x0 + 2, y0 + 10, LAMPW, 1.6, 0)                        # lluu del plàstic
    cv.darken(EX0, 208, EX1 + 4, 212, 0.6)

    # Ombres de contacte paret-terra
    cv.darken(0, FLOOR_Y, W - 1, FLOOR_Y + 4, lambda x, y: 0.5 - (y - FLOOR_Y) * 0.11)
    # reflex del terra polit
    reflect(cv)
    # la llum de l'holograma, també al terra
    cv.tint(320, FLOOR_Y, 496, 273, (110, 220, 255), lambda x, y: 0.28 * max(0.0, 1 - math.hypot((x - HX) / 85, (y - 213) / 29)))


def _holo_shape(x, y):
    """Silueta del Director: retorna un nivell de to (o None si és fora)."""
    cx = HX
    # cap
    dx, dy = (x - cx) / 8.0, (y - 71) / 9.6
    if dx * dx + dy * dy <= 1:
        return 3.4 - dx * 0.8 - dy * 0.3
    # orelles
    if 69 <= y <= 74 and abs(abs(x - cx) - 8.5) < 1:
        return 2.8
    # coll
    if 80 <= y <= 84 and abs(x - cx) <= 3:
        return 2.6
    # tors (americana)
    if 84 <= y <= 131:
        t = (y - 84) / 47
        half = 17 - t * 4
        if abs(x - cx) <= half:
            return 2.6 - (x - cx) / half * 0.7 + (0.6 if abs(x - cx) > half - 2 else 0)
    # braços: l'esquerre alçat (gest de benvinguda), el dret avall
    for (ax, ay), (bx, by), r in (((cx - 16, 88), (cx - 29, 109), 4.0), ((cx - 29, 109), (cx - 40, 99), 3.5),
                                  ((cx + 16, 88), (cx + 19, 128), 4.0)):
        vx, vy = bx - ax, by - ay
        t = max(0.0, min(1.0, ((x - ax) * vx + (y - ay) * vy) / (vx * vx + vy * vy)))
        if math.hypot(x - ax - vx * t, y - ay - vy * t) <= r:
            return 2.8 - (x - cx) / 27
    # mà oberta (i els dits)
    if math.hypot(x - (cx - 43), y - 95) <= 3.5:
        return 3.6
    if 89 <= y <= 92 and x in (cx - 45, cx - 43, cx - 41):
        return 3.4
    # cames
    if 131 < y <= 184:
        for lx in (cx - 7, cx + 7):
            if abs(x - lx) <= 5.3 - (y - 131) / 30:
                return 2.2 - (x - cx) / 19
    # sabates
    if 181 <= y <= 185 and (abs(x - (cx - 8)) <= 5 or abs(x - (cx + 8)) <= 5):
        return 1.8
    return None


def _director(cv, tt=0.0):
    ph = 2 * math.pi * tt
    so = int(tt * 12) % 3                                                 # les línies d'escaneig pugen
    yb = 53 + (41 + int(tt * 135)) % 135                                  # franja de glitch que baixa
    g149 = round(3 * math.cos(ph * 2))
    seed = 77 + int(tt * 6) % 6                                           # guspires que canvien
    jolt = 0.375 <= tt < 0.417                                            # una sacsejada de tant en tant
    head = 0.79 <= tt < 0.83
    fa = 1 + 0.06 * math.sin(ph * 5) + 0.04 * math.sin(ph * 3)            # tremolor de la intensitat
    for y in range(53, 188):
        glitch = 3 if y in (yb, yb + 1, yb + 2) else (g149 if y in (149, 150) else 0)
        if jolt:
            glitch += 1 + (-5 if 112 <= y <= 123 else 0)
        if head and 64 <= y <= 75:
            glitch += 3
        scan = (y + so) % 3 == 0
        for x in range(365, 454):
            v = _holo_shape(x - glitch, y)
            if v is None:
                continue
            # detalls de la cara i el vestit (la mateixa cara del retrat del despatx)
            cx = HX + glitch
            ax = abs(x - cx)
            if 61 <= y <= 67 and ax >= 4:
                v += 1.0                                                  # cabells grisos
            if y == 62 and ax < 4:
                v += 0.6                                                  # el clatell, pentinat enrere
            if y == 68 and 2 <= ax <= 5:
                v -= 0.8                                                  # celles
            if y == 70 and ax in (3, 4):
                v = 0.8                                                   # ulls
            if y == 76 and ax <= 5:
                v = 4.2                                                   # bigoti
            if y == 79 and ax <= 4:
                v = 4.6 if ax <= 3 else 1.2                               # el somriure
            if 84 <= y <= 104 and ax <= 1:
                v = 4.0 if y < 88 else 1.4                                # camisa i corbata
            if 85 <= y <= 99 and abs(ax - (3 + (y - 85) // 3)) < 0.6:
                v += 1.2                                                  # solapes
            if y in (110, 119) and x == cx + 3:
                v += 1.4                                                  # botons
            if scan:
                v -= 0.9                                                  # línies d'escaneig
            if hr(x, y, seed) > 0.94:
                v += 1.2
            o = cv.P[x, y]
            col = HOLO[max(0, min(len(HOLO) - 1, math.floor(v + B4[y & 3][x & 3] - 0.5)))]
            a = min(1.0, (0.5 if scan else 0.78) * fa * (0.8 if jolt else 1))
            cv.P[x, y] = mix(o, col, a) + (255,)
    # vora brillant
    cv.glow(HX, 117, 61, (150, 235, 255), 0.22)


SX0, SX1, SY0, SY1 = 375, 441, 189, 209


def _socol(cv, tt=0.0):
    # cos cilíndric amb plaques
    for y in range(SY0 + 5, SY1 + 1):
        for x in range(SX0, SX1 + 1):
            nx = (x - HX) / ((SX1 - SX0) / 2)
            if abs(nx) > 1:
                continue
            lvl = 5.6 - nx * 1.4 - abs(nx) ** 3 * 2.0 - (y - SY0) / 13
            ang = math.degrees(math.asin(max(-1, min(1, nx))))
            if abs((ang + 90) % 30 - 15) > 14:
                lvl = 2.0                                                  # juntes entre plaques
            if y >= SY1 - 2:
                lvl -= 1.6
            if y == SY1 - 3:
                lvl += 0.6                                                 # el bisell de baix
            cv.put(x, y, MUSE, lvl)
    # cargols de les plaques
    for ang in range(-75, 90, 30):
        x = round(HX + math.sin(math.radians(ang)) * 32)
        for yy in (SY0 + 9, SY1 - 5):
            cv.put(x, yy, MUSE, 7.6)
            cv.put(x + 1, yy, MUSE, 4.0)
            cv.put(x, yy + 1, MUSE, 3.0)
            cv.put(x + 1, yy + 1, MUSE, 1.6)
    # tapa amb l'anell emissor
    cv.disc(HX, SY0 + 4, 35, 5.6, MUSE, lambda nx, ny: 6.4 - ny * 0.8 - nx * 0.6)
    p = 0.6 * math.sin(4 * math.pi * tt)                                   # l'emissor batega amb els polsos
    cv.disc(HX, SY0 + 4, 27, 4, HOLO, lambda nx, ny: 4.6 + p - (nx * nx + ny * ny) * 1.5, 0)
    cv.disc(HX, SY0 + 4, 12, 1.9, HOLO, 5.5 + p * 0.5, 0)
    cv.glow(HX, SY0 + 3, 32, (150, 235, 255), 0.5)
    # ombra al terra
    cv.darken(SX0 - 3, SY1 + 1, SX1 + 3, SY1 + 5, lambda x, y: 0.7 - (y - SY1 - 1) * 0.15)


# ─── Sòcol (prop): una de les plaques descargolada, amb un paper amagat ──────

def socol(cv):
    # la placa de davant a la dreta (entre 15° i 45°), oberta i tort
    x0 = round(HX + math.sin(math.radians(15)) * 33)
    x1 = round(HX + math.sin(math.radians(45)) * 33)
    # forat fosc
    cv.rect(x0 + 1, SY0 + 8, x1, SY1 - 1, MUSE, 0.2, 0)
    cv.hline(x0 + 1, x1, SY0 + 8, MUSE, 1.0, 0)
    # cables a dins
    cv.line(x0 + 2, SY0 + 12, x1 - 1, SY0 + 16, RED, 2.4, 0.3)
    cv.line(x0 + 2, SY0 + 15, x1 - 2, SY0 + 11, HOLO, 2.2, 0)
    cv.line(x0 + 3, SY0 + 10, x1 - 3, SY0 + 13, MUSE, 3.0, 0.3)
    # el paper doblegat, amagat al forat
    cv.rect(x0 + 4, SY1 - 7, x0 + 11, SY1 - 3, PAPER, 4.2, 0.6)
    cv.hline(x0 + 4, x0 + 11, SY1 - 3, PAPER, 2.4, 0.6)
    cv.vline(x0 + 8, SY1 - 7, SY1 - 4, PAPER, 3.4, 0.6)
    # la placa, penjant d'un sol cargol i girada
    pts = [(x1 - 1, SY0 + 9), (x1 + 8, SY0 + 13), (x1 + 5, SY1 + 3), (x1 - 4, SY1)]
    cv.poly(pts, MUSE, lambda x, y: 4.8 - (y - SY0) / 13)
    cv.line(pts[0][0], pts[0][1], pts[1][0], pts[1][1], MUSE, 7.0)
    cv.line(pts[1][0], pts[1][1], pts[2][0], pts[2][1], MUSE, 2.2)
    cv.line(pts[3][0], pts[3][1], pts[2][0], pts[2][1], MUSE, 1.6)
    cv.put(x1, SY0 + 11, MUSE, 8.0)
    cv.put(x1 + 1, SY0 + 11, MUSE, 3.0)
    # cargol caigut al terra
    cv.put(x1 + 12, SY1 + 4, MUSE, 7.6)
    cv.put(x1 + 13, SY1 + 4, MUSE, 2.6)
    cv.put(x1 + 12, SY1 + 5, MUSE, 1.6)


# ─── Placa del robot (prop): a la vitrina, fins que s'obre ─────────────────

def placa_robot(cv):
    cv.rect(529, 145, 537, 151, IRON, lambda x, y: 4.4 - (y - 145) * 0.3)
    cv.hline(529, 537, 145, IRON, 5.4)
    cv.put(530, 146, IRON, 6.0); cv.put(536, 146, IRON, 6.0)
    for x in range(531, 536):                                       # el nom gravat a mà, ratllat
        cv.put(x, 148 + (x & 1), IRON, 1.6)
    cv.hline(529, 537, 152, VELVET, 1.0)                            # ombra sota la placa


# ─── La M. d'Orís a la foto (prop): torna a ser-hi ──────────────────────────
# Es dibuixa la sala amb ella i sense (amb el forat) i es copia la diferència dins la foto.
_FOTO = []


def foto_mira(cv):
    if not _FOTO:
        on, off = Canvas(light=LIGHT), Canvas(light=LIGHT)
        bg(on, mira=True)
        bg(off)
        _FOTO.append((on, off))
    on, off = _FOTO[0]
    for y in range(49, 124):
        for x in range(123, 224):
            p = on.P[x, y]
            if p != off.P[x, y]:
                cv.P[x, y] = p


PROPS = {'socol': socol, 'foto_mira': foto_mira, 'placa_robot': placa_robot}


# ─── Animació de fons: l'holograma tremola (línies d'escaneig que pugen, franges de glitch, alguna
# sacsejada), el raig del sòcol respira i hi pugen polsos, i al mapa la ruta avança i l'estrella parpelleja ──

def _ambient_frames(n=24):
    return ambient_frames(bg, LIGHT, n)


ANIMS = {'ambient': {'frames': _ambient_frames, 'frameDuration': 120}}
