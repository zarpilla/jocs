"""
Sala de la Memòria (La Gavina, Vet): el museu de propaganda de la corporació. Plafons nets, terra polit que
reflecteix, focus de museu sobre les peces i l'holograma del Director Aldaia fent de guia.
Llums: l'holograma (cian, la més forta), focus sobre la foto i sobre la vitrina, i la pantalla del mapa.
"""
import math

from hd.pix import (Canvas, Light, B4, W, H, hr, ramp, mix, STEEL, PANEL, CYAN, WARN, RED, PAPER, IRON, SPACE, GRAY, NAVY,
                    TEAL, SKIN)
from hd.rooms.gavina_passadis import (HULL, LAMPW, SIGN, CORPG, PILOT, FLOOR_Y, text, text_w, smile, rivet)

# Plafons de museu: gris clar i net, ombres blavoses
MUSE = ramp((14, 16, 26), (32, 36, 50), (56, 62, 78), (84, 92, 108), (114, 122, 138), (146, 154, 166),
            (176, 182, 192), (204, 208, 214), (228, 230, 232), n=10)
# Terra polit de resina
RESIN = ramp((8, 10, 18), (18, 22, 34), (32, 38, 52), (50, 58, 72), (72, 80, 94), (98, 106, 118), (130, 136, 146),
             (168, 172, 178), n=9)
SEPIA = ramp((34, 22, 16), (66, 46, 32), (104, 78, 54), (146, 116, 84), (188, 160, 120), (222, 204, 166),
             (240, 232, 206), n=8)
FRAME = ramp((10, 8, 10), (24, 20, 22), (42, 36, 34), (70, 58, 48), (110, 90, 64), (160, 132, 84), (206, 178, 116),
             n=7)
VELVET = ramp((24, 6, 14), (48, 12, 24), (80, 20, 36), (116, 32, 48), (150, 50, 62), (186, 84, 90), n=6)
HOLO = [(20, 60, 90), (40, 110, 150), (70, 170, 210), (120, 220, 245), (190, 245, 255), (240, 255, 255)]
SPOT = [(255, 240, 214)]

HX, HY = 306, 92                     # centre de l'holograma
SPOT_FOTO = (130, 12)
SPOT_VITRINA = (382, 12)


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
            w = 3 + t * rx * 0.9
            if abs(x - (sx + (tx - sx) * t)) < w:
                v += 0.35 * k * (1 - abs(x - (sx + (tx - sx) * t)) / w) * t
        return v
    return f


def holo_light(x, y):
    d = math.hypot(x - HX, (y - HY) * 0.7)
    return 2.4 * max(0.0, 1 - d / 120) ** 1.6


LIGHT = Light(ambient=0.0, vignette=(64, 30), floor_fade=(198, 34))
LIGHT.add(spot_cone(*SPOT_FOTO, 130, 66, 84, 2.4))
LIGHT.add(spot_cone(*SPOT_VITRINA, 382, 96, 62, 2.4))
LIGHT.add(lambda x, y: 0.9 * max(0.0, 1 - math.hypot((x - 220) / 200, (y - 175) / 30)) if y >= FLOOR_Y else 0.0)
LIGHT.add(holo_light)
LIGHT.point(219, 64, r=70, k=0.8)                                     # pantalla del mapa


def museum_wall(cv, x0, x1):
    pw = 48
    for y in range(0, 154):
        for x in range(x0, x1 + 1):
            px = (x - 4) % pw
            lvl = 2.7 + (hr((x - 4) // pw, 2) - 0.5) * 0.15
            if y < 10:
                lvl = 1.2 + (0.8 if y in (7, 8) else 0)
            elif y == 10:
                lvl = 4.0
            elif y < 13:
                lvl = 1.0
            elif y < 112:
                if px == 0:
                    lvl = 1.2                                               # junta d'ombra entre plafons
                elif px == 1:
                    lvl += 0.8
                elif px == pw - 1:
                    lvl -= 0.6
                lvl -= max(0.0, 1 - (y - 13) / 16) * 1.2
            elif y < 116:
                lvl = [4.6, 3.8, 2.6, 1.4][y - 112]                         # passamà
            elif y < 146:
                lvl = 2.6 + (0.2 if px < 2 else 0)
                if px == 0:
                    lvl = 1.4
            else:
                lvl = [3.6, 1.6, 1.4, 1.3, 1.2, 1.0, 0.8, 0.4][y - 146]     # sòcol fosc
            cv.put(x, y, MUSE, lvl)


def resin_floor(cv):
    vx, vy, S, K = 240, 30, 1.7, 700.0
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
            if y < 160:
                lvl -= (160 - y) / 6 * 0.9
            cv.put(x, y, RESIN, lvl)


def reflect(cv, k=0.18):
    """Reflex del terra polit: barreja amb la paret capgirada."""
    for y in range(FLOOR_Y, 206):
        sy = 2 * 153 - y
        a = k * max(0.0, 1 - (y - FLOOR_Y) / 48)
        for x in range(W):
            if a > B4[y & 3][x & 3] * 0.45:
                s = cv.P[x, sy]
                o = cv.P[x, y]
                if sum(s[:3]) > sum(o[:3]):
                    cv.P[x, y] = mix(o, s, a) + (255,)


def bg(cv, mira=False):
    museum_wall(cv, 0, W - 1)
    resin_floor(cv)

    # ─── Rètol del sostre ─────────────────────────────────────────────────
    title = 'LA GAVINA · AQUI VA COMENCAR TOT'
    tw = text_w(title)
    tx = 220 - tw // 2
    cv.rect(tx - 14, 14, tx + tw + 4, 22, CORPG, 2.5, 0.2)
    cv.hline(tx - 14, tx + tw + 4, 14, CORPG, 4.5, 0.2)
    text(cv, tx, 16, title, SIGN, 4.5, 0)
    cv.put(tx + text_w('LA GAVINA · AQUI VA COMEN') + 1, 21, SIGN, 4.5, 0)   # la ce trencada
    smile(cv, tx - 7, 18, 3, lit=0, lvl=3.8)
    cv.darken(tx - 14, 23, tx + tw + 4, 24, 0.4)

    # ─── Focus de museu al carril del sostre ──────────────────────────────
    cv.hline(70, 420, 11, IRON, 3.0)
    cv.hline(70, 420, 12, IRON, 1.4)
    for sx, sy in (SPOT_FOTO, SPOT_VITRINA):
        cv.rect(sx - 2, 11, sx + 2, 13, IRON, 3.0)
        cv.poly([(sx - 5, 14), (sx + 3, 13), (sx + 5, 19), (sx - 3, 21)], IRON, lambda x, y: 3.6 - (x - sx) * 0.25)
        cv.line(sx - 3, 21, sx + 5, 19, SPOT, 0, 0)
        cv.glow(sx + 1, 21, 10, (255, 240, 210), 0.6)

    # ─── Porta cap al passadís (8..65 × 46..155) ──────────────────────────
    DX0, DX1, DT = 12, 61, 60
    cv.rect(DX0 - 4, DT - 4, DX1 + 4, 153, MUSE, lambda x, y: 4.6 if x < DX0 - 2 or y < DT - 2 else (1.6 if x > DX1 + 1 else 3.0))
    cv.rect(DX0 - 1, DT - 1, DX1 + 1, 153, STEEL, 0.4)
    mid = (DX0 + DX1) // 2
    for y in range(DT, 154):
        for x in range(DX0, DX1 + 1):
            side = x <= mid
            u = (x - DX0) / (mid - DX0) if side else (x - mid - 1) / (DX1 - mid - 1)
            lvl = 3.2 + (0.6 - u * 0.9) - (0.3 if not side else 0)
            if x in (mid, mid + 1):
                lvl = 1.0 if x == mid else 4.2
            if 96 <= y <= 112 and (x - DX0 in range(5, 19) or DX1 - x in range(5, 19)):
                lvl = 2.0 + (0.8 if y == 96 else 0)                       # finestretes de vidre esmerilat
            cv.put(x, y, STEEL, lvl)
    for hx in (mid - 4, mid + 3):
        cv.rect(hx, 108, hx + 1, 122, STEEL, 6.0)
    # rètol de sortida
    cv.rect(24, 48, 50, 55, PILOT, 1.5, 0)
    text(cv, 25, 49, 'SORTIDA', PILOT, 3.5, 0, gap=0)
    cv.glow(37, 52, 18, (90, 255, 140), 0.35)
    # lector d'accés
    cv.rect(DX1 + 7, 98, DX1 + 12, 108, MUSE, lambda x, y: 1.6 if x == DX1 + 12 else 4.0)
    cv.put(DX1 + 9, 101, PILOT, 3.0, 0)

    # ─── Foto del torn de nit (90..169 × 35..101) ─────────────────────────
    FX0, FY0, FX1, FY1 = 92, 37, 167, 92
    cv.rect(FX0 + 2, FY0 + 2, FX1 + 3, FY1 + 3, MUSE, 1.4)                  # ombra
    for y in range(FY0, FY1 + 1):
        for x in range(FX0, FX1 + 1):
            dd = min(x - FX0, FX1 - x, y - FY0, FY1 - y)
            if dd > 3:
                continue
            lvl = [2.0, 4.6, 3.6, 2.4][dd]
            if (FX1 - x) < 4 or (FY1 - y) < 4:
                lvl -= 0.8
            cv.put(x, y, FRAME, lvl)
    PX0, PY0, PX1, PY1 = FX0 + 4, FY0 + 4, FX1 - 4, FY1 - 4               # 96..163 × 41..88
    # fons de la foto: la nau de la fàbrica, amb la boca d'un forn encesa
    for y in range(PY0, PY1 + 1):
        for x in range(PX0, PX1 + 1):
            lvl = 2.6 + (y - PY0) / 40 + (hr(x // 3, y // 3, 3) - 0.5) * 0.2
            if (x - PX0) % 12 == 0 and y < PY0 + 26:
                lvl -= 0.6                                                  # pilars de la nau
            if y < PY0 + 4:
                lvl -= 0.6
            fd = math.hypot(x - 152, y - 56)
            if fd < 9:
                lvl += (1 - fd / 9) * 2.8                                  # la boca del forn
            cv.put(x, y, SEPIA, lvl, 0.3)
    # el torn de nit, en fila
    people = [(104, 0, 28, True), (114, 1, 27, False), (123, 2, 23, False), (133, 3, 29, True), (143, 4, 27, True)]
    for px, k, h, cap in people:
        if k == 2 and not mira:
            continue                                                        # la M. d'Orís: retallada (vegeu el forat)
        top = PY1 - h
        # cos (granota de treball fosca)
        for y in range(top + 7, PY1 + 1):
            half = 3 + (1 if y > top + 9 else 0)
            for x in range(px - half, px + half + 1):
                cv.put(x, y, SEPIA, 1.4 - (x - px) * 0.1 + (0.6 if x == px - half else 0), 0.3)
        cv.rect(px - 1, top + 5, px + 1, top + 7, SEPIA, 3.6, 0.3)        # coll
        cv.disc(px, top + 3, 2.5, 3, SEPIA, lambda nx, ny: 4.6 - nx * 0.8 - ny * 0.4, 0.3)
        if cap:
            cv.rect(px - 3, top, px + 2, top + 1, SEPIA, 1.2, 0.3)        # gorra de treball
        else:
            cv.rect(px - 2, top, px + 2, top + 1, SEPIA, 0.8, 0.3)        # cabells
            cv.vline(px - 3, top + 1, top + 4, SEPIA, 0.8, 0.3)
    # la I. (segona): cara ratllada
    ix, itop = 114, PY1 - 27
    for i in range(-3, 4):
        cv.put(ix + i, itop + 3 + i // 2, SEPIA, 6.4, 0.3)
        cv.put(ix + i, itop + 4 - i // 2, SEPIA, 6.0, 0.3)
        cv.put(ix + i + 1, itop + 2 + (i * 3) // 4, SEPIA, 0.4, 0.3)
    # la del costat (M. d'Orís): més baixeta, somrient, amb una trena
    mx, mtop = 123, PY1 - 23
    if mira:
        cv.vline(mx + 3, mtop + 2, mtop + 8, SEPIA, 0.8, 0.3)             # trena
        cv.hline(mx - 1, mx + 1, mtop + 5, SEPIA, 2.0, 0.3)                # somriure
    else:
        # algú la va retallar amb tisores: un forat amb la seva silueta, i a dins el cartró fosc del darrere
        def cut(x, y):
            j = (hr(x, y, 71) - 0.5) * 1.1                                 # tall de tisora, no gaire net
            if y <= mtop + 6:
                return math.hypot((x - mx) / 3.8, (y - mtop - 3) / 4.3) + j * 0.2 < 1
            if y <= mtop + 9:
                return abs(x - mx) <= 2.6 + j
            return abs(x - mx) <= 5 + j + (1 if y > mtop + 11 else 0)
        for y in range(mtop - 2, PY1 + 1):
            for x in range(mx - 8, mx + 9):
                if not cut(x, y):
                    continue
                edge = not cut(x - 1, y) or not cut(x, y - 1)
                if edge:
                    cv.put(x, y, SEPIA, 6.2, 0.3)                          # vora blanca del paper tallat
                else:
                    cv.put(x, y, FRAME, 0.9 + (y - mtop) / 30 + (hr(x, y, 72) - 0.5) * 0.3, 0.3)
    # el Cargol, nou de trinca, a la dreta
    cv.rect(153, PY1 - 22, 160, PY1 - 10, SEPIA, lambda x, y: 5.0 - (x - 153) * 0.3, 0.3)   # cos
    cv.rect(154, PY1 - 27, 159, PY1 - 23, SEPIA, 5.4, 0.3)                                   # cap
    cv.put(155, PY1 - 26, SEPIA, 0.6, 0.3); cv.put(158, PY1 - 26, SEPIA, 0.6, 0.3)          # ulls
    cv.vline(156, PY1 - 30, PY1 - 28, SEPIA, 4.0, 0.3)                                       # antena
    cv.rect(154, PY1 - 9, 155, PY1, SEPIA, 3.6, 0.3); cv.rect(158, PY1 - 9, 159, PY1, SEPIA, 3.6, 0.3)
    cv.put(156, PY1 - 18, SEPIA, 6.4, 0.3)                                                   # la placa, nova
    # taques i vinyeta de foto vella
    cv.darken(PX0, PY0, PX1, PY1, lambda x, y: max(0.0, 0.5 - min(x - PX0, PX1 - x, y - PY0, PY1 - y) / 7), dither=False)
    # cartel·la
    cv.rect(108, 95, 151, 100, PAPER, 4.5, 0.3)
    cv.hline(110, 149, 97, MUSE, 2.5, 0)
    cv.hline(112, 136, 99, MUSE, 3.5, 0)

    # ─── Mapa de La Gavina (174..264 × 29..101) ───────────────────────────
    MX0, MY0, MX1, MY1 = 176, 32, 262, 98
    cv.rect(MX0 - 2, MY0 - 2, MX1 + 2, MY1 + 2, STEEL, lambda x, y: 1.4 if x > MX1 or y > MY1 else 4.4)
    for y in range(MY0, MY1 + 1):
        for x in range(MX0, MX1 + 1):
            lvl = 1.6 + (0.25 if (x - MX0) % 8 == 0 or (y - MY0) % 8 == 0 else 0) + (y - MY0) / 120
            cv.put(x, y, NAVY, lvl + 1.0, 0.2)

    def mp(x, y, lvl=4.5, rmp=CYAN):
        cv.put(x, y, rmp, lvl, 0)

    text(cv, MX0 + 4, MY0 + 3, 'LA GAVINA', CYAN, 4.5, 0)
    # l'estació: anell de mòduls al voltant d'un nucli
    cx, cy = 213, 62
    for a in range(0, 360, 2):
        mp(round(cx + math.cos(math.radians(a)) * 24), round(cy + math.sin(math.radians(a)) * 13), 3.5)
    MODS = [('A', -40), ('B', 30), ('C', 100), ('D', 170), ('E', 240)]
    for name, a in MODS:
        mx_, my_ = round(cx + math.cos(math.radians(a)) * 24), round(cy + math.sin(math.radians(a)) * 13)
        cv.rect(mx_ - 4, my_ - 3, mx_ + 4, my_ + 3, NAVY, 2.5, 0)
        for xx in range(mx_ - 4, mx_ + 5):
            mp(xx, my_ - 3); mp(xx, my_ + 3)
        for yy in range(my_ - 3, my_ + 4):
            mp(mx_ - 4, yy); mp(mx_ + 4, yy)
        text(cv, mx_ - 1, my_ - 2, name, CYAN, 4.5 if name != 'C' else 5.5, 0)
    cv.disc(cx, cy, 5, 3, CYAN, 2.5, 0)
    # «Vostè és aquí» (estrella al mòdul C)
    sx_, sy_ = round(cx + math.cos(math.radians(100)) * 24) + 7, round(cy + math.sin(math.radians(100)) * 13) - 1
    for dx, dy in ((0, -2), (0, -1), (-2, 0), (-1, 0), (0, 0), (1, 0), (2, 0), (0, 1), (-1, 2), (1, 2)):
        cv.put(sx_ + dx, sy_ + dy, WARN, 4.5, 0)
    cv.glow(sx_, sy_, 5, (255, 220, 80), 0.6)
    # conducte de servei en discontínua, per sota del mòdul C fins a l'hangar
    hx_, hy_ = 244, 90
    cmx, cmy = round(cx + math.cos(math.radians(100)) * 24), round(cy + math.sin(math.radians(100)) * 13) + 4
    for i in range(0, 34):
        t = i / 33
        if (i // 2) % 2 == 0:
            x = round(cmx + (hx_ - cmx) * t)
            y = round(cmy + 10 * math.sin(t * math.pi) * 0.8 + (hy_ - cmy) * t)
            cv.put(x, y, WARN, 3.5, 0)
    cv.rect(hx_ - 3, hy_ - 2, hx_ + 5, hy_ + 2, NAVY, 2.5, 0)
    for xx in range(hx_ - 3, hx_ + 6):
        mp(xx, hy_ - 2, 3.5); mp(xx, hy_ + 2, 3.5)
    # llegenda
    for y in (91, 94):
        cv.hline(MX0 + 4, MX0 + 4 + int(hr(y, 1) * 20) + 10, y, CYAN, 3.5, 0)
    cv.glow(219, 65, 46, (90, 170, 255), 0.25)

    # ─── Holograma del Director (278..335 × 35..142) i el sòcol ───────────
    # con de llum del projector
    cv.tint(272, 40, 340, 146, (140, 230, 255), lambda x, y: max(0.0, 0.22 * (1 - abs(x - HX) / (8 + (146 - y) * 0.26))) if y < 146 else 0)
    _director(cv)
    _socol(cv)

    # ─── Vitrina (354..409 × 87..153) ─────────────────────────────────────
    VX0, VX1 = 356, 407
    # pedestal
    cv.rect(VX0 + 2, 121, VX1 - 2, 153, MUSE, lambda x, y: 4.4 - (x - VX0) / 40 - (2.4 if y > 149 else 0) + (0.8 if x == VX0 + 2 else 0))
    cv.hline(VX0 + 1, VX1 - 1, 120, MUSE, 5.2)
    cv.vline(VX1 - 2, 121, 153, MUSE, 2.0)
    # placa de la peça, al pedestal
    cv.rect(368, 128, 395, 136, SIGN, 3.5, 0.3)
    cv.hline(370, 393, 130, MUSE, 2.5, 0)
    cv.hline(370, 386, 132, MUSE, 2.5, 0)
    cv.hline(370, 390, 134, MUSE, 3.0, 0)
    # caixa de vidre
    GT = 89
    for y in range(GT, 120):
        for x in range(VX0, VX1 + 1):
            lvl = 2.6 + (y - GT) / 60
            cv.put(x, y, MUSE, lvl, 0.6)
    # base de vellut i el buit de la clau anglesa
    cv.rect(VX0 + 2, 108, VX1 - 2, 119, VELVET, lambda x, y: 3.4 - (y - 108) * 0.12)
    cv.hline(VX0 + 2, VX1 - 2, 108, VELVET, 4.6)
    for x in range(364, 392):                                         # silueta de la clau (buida)
        t = (x - 364) / 27
        cv.put(x, 113, VELVET, 0.6)
        cv.put(x, 114, VELVET, 1.0)
    cv.disc(364, 113.5, 3.2, 2.6, VELVET, 0.6)
    cv.disc(392, 113.5, 3.4, 2.8, VELVET, 0.6)
    cv.rect(361, 112, 364, 115, VELVET, 3.4)                         # boca oberta de la clau
    cv.rect(393, 112, 396, 115, VELVET, 3.4)
    # buit de la placa del robot, petit, a la dreta (la placa és un prop)
    cv.rect(397, 109, 403, 113, VELVET, lambda x, y: 2.2 + (y - 109) * 0.15)
    cv.hline(397, 403, 109, VELVET, 1.0)
    cv.vline(397, 109, 113, VELVET, 1.2)
    # cartellet dins la vitrina
    cv.poly([(366, 117), (378, 117), (377, 119), (367, 119)], PAPER, 4.0)
    # marc d'acer, tapa amb llum interior i reflexos
    cv.rect(VX0 - 1, GT - 3, VX1 + 1, GT - 1, STEEL, lambda x, y: 5.0 - (y - GT + 3))
    cv.hline(VX0 + 2, VX1 - 2, GT, LAMPW, 3.5, 0)
    for x in (VX0, VX1):
        cv.vline(x, GT, 119, STEEL, 5.0 if x == VX0 else 2.4)
    for i in range(14):
        cv.put(VX0 + 6 + i, 100 - i, LAMPW, 3.0, 0)
        cv.put(VX0 + 9 + i, 104 - i, LAMPW, 2.0, 0)
        cv.put(VX0 + 30 + i // 2, 98 - i, LAMPW, 2.0, 0)
    cv.glow(381, 98, 26, (255, 245, 220), 0.25)
    cv.darken(VX0, 153, VX1 + 4, 158, lambda x, y: 0.8 - (y - 153) / 6)

    # ─── Expositor de fullets (425..466 × 100..153) ───────────────────────
    EX0, EX1 = 428, 463
    for lx in (EX0 + 3, EX1 - 4):
        cv.rect(lx, 136, lx + 1, 156, STEEL, 3.0)
    cv.rect(EX0 + 2, 154, EX1 - 2, 156, STEEL, 2.4)
    cv.rect(EX0, 104, EX1, 138, STEEL, lambda x, y: 2.2 - (x - EX0) / 60)
    cv.hline(EX0, EX1, 104, STEEL, 4.6)
    # capçalera
    cv.rect(EX0 - 1, 100, EX1 + 1, 105, CORPG, 2.5, 0.3)
    text(cv, EX0 + 6, 101, 'GAVINA', SIGN, 4.5, 0)
    for row, y0 in enumerate((107, 117, 127)):
        for col, x0 in enumerate((EX0 + 2, EX0 + 19)):
            # fullet: capçalera verda, el somriure i text
            cv.rect(x0, y0, x0 + 14, y0 + 9, SIGN, 4.5, 0.4)
            cv.rect(x0, y0, x0 + 14, y0 + 2, CORPG, 2.5 + (row % 2), 0.2)
            smile(cv, x0 + 4, y0 + 6, 2, lit=0, lvl=3.6)
            cv.hline(x0 + 8, x0 + 12, y0 + 5, MUSE, 2.5, 0)
            cv.hline(x0 + 8, x0 + 11, y0 + 7, MUSE, 2.5, 0)
            # butxaca de plàstic
            cv.hline(x0 - 1, x0 + 15, y0 + 9, STEEL, 4.0)
    cv.darken(EX0, 156, EX1 + 3, 159, 0.6)

    # Ombres de contacte paret-terra
    cv.darken(0, 154, W - 1, 157, lambda x, y: 0.5 - (y - 154) * 0.14)
    # reflex del terra polit
    reflect(cv)
    # la llum de l'holograma, també al terra
    cv.tint(240, 154, 372, 205, (110, 220, 255), lambda x, y: 0.28 * max(0.0, 1 - math.hypot((x - HX) / 64, (y - 160) / 22)))


def _holo_shape(x, y):
    """Silueta del Director: retorna un nivell de to (o None si és fora)."""
    cx = HX
    # cap
    dx, dy = (x - cx) / 6.0, (y - 53) / 7.2
    if dx * dx + dy * dy <= 1:
        lvl = 3.4 - dx * 0.8 - dy * 0.3
        return lvl
    # coll
    if 60 <= y <= 63 and abs(x - cx) <= 2:
        return 2.6
    # tors (americana)
    if 63 <= y <= 98:
        t = (y - 63) / 35
        half = 13 - t * 3
        if abs(x - cx) <= half:
            return 2.6 - (x - cx) / half * 0.7 + (0.6 if abs(x - cx) > half - 1.5 else 0)
    # braç esquerre (alçat, gest de benvinguda)
    for (ax, ay), (bx, by), r in (((cx - 12, 66), (cx - 22, 82), 3.0), ((cx - 22, 82), (cx - 30, 74), 2.6),
                                  ((cx + 12, 66), (cx + 14, 96), 3.0)):
        vx, vy = bx - ax, by - ay
        t = max(0.0, min(1.0, ((x - ax) * vx + (y - ay) * vy) / (vx * vx + vy * vy)))
        if math.hypot(x - ax - vx * t, y - ay - vy * t) <= r:
            return 2.8 - (x - cx) / 20
    # mà oberta
    if math.hypot(x - (cx - 32), y - 71) <= 2.6:
        return 3.6
    # cames
    if 98 < y <= 138:
        for lx in (cx - 5, cx + 5):
            if abs(x - lx) <= 4 - (y - 98) / 30:
                return 2.2 - (x - cx) / 14
    # sabates
    if 136 <= y <= 139 and (abs(x - (cx - 6)) <= 4 or abs(x - (cx + 6)) <= 4):
        return 1.8
    return None


def _director(cv):
    for y in range(40, 141):
        glitch = 2 if y in (71, 72, 112) else 0
        for x in range(274, 340):
            v = _holo_shape(x - glitch, y)
            if v is None:
                continue
            # detalls de la cara i el vestit (la mateixa cara del retrat del despatx)
            cx = HX + glitch
            if 46 <= y <= 50 and abs(x - cx) >= 3:
                v += 1.0                                                  # cabells grisos
            if y in (52,) and x in (cx - 3, cx - 2, cx + 2, cx + 3):
                v = 0.8                                                   # ulls
            if y == 57 and abs(x - cx) <= 4:
                v = 4.2                                                   # bigoti
            if y == 59 and abs(x - cx) <= 3:
                v = 4.6 if abs(x - cx) <= 2 else 1.2                       # el somriure
            if 63 <= y <= 78 and abs(x - cx) <= 1:
                v = 4.0 if y < 66 else 1.4                                # camisa i corbata
            if 64 <= y <= 74 and abs(abs(x - cx) - (2 + (y - 64) // 3)) < 0.6:
                v += 1.2                                                  # solapes
            if (y % 3) == 0:
                v -= 0.9                                                  # línies d'escaneig
            if hr(x, y, 77) > 0.94:
                v += 1.2
            o = cv.P[x, y]
            col = HOLO[max(0, min(len(HOLO) - 1, math.floor(v + B4[y & 3][x & 3] - 0.5)))]
            a = 0.78 if y % 3 else 0.5
            cv.P[x, y] = mix(o, col, a) + (255,)
    # vora brillant
    cv.glow(HX, 88, 46, (150, 235, 255), 0.22)


SX0, SX1, SY0, SY1 = 281, 331, 142, 157


def _socol(cv):
    # cos cilíndric amb plaques
    for y in range(SY0 + 4, SY1 + 1):
        for x in range(SX0, SX1 + 1):
            nx = (x - HX) / ((SX1 - SX0) / 2)
            if abs(nx) > 1:
                continue
            lvl = 5.6 - nx * 1.4 - abs(nx) ** 3 * 2.0 - (y - SY0) / 10
            ang = math.degrees(math.asin(max(-1, min(1, nx))))
            if abs((ang + 90) % 30 - 15) > 14:
                lvl = 2.0                                                  # juntes entre plaques
            if y >= SY1 - 1:
                lvl -= 1.6
            cv.put(x, y, MUSE, lvl)
    # cargols de les plaques
    for ang in range(-75, 90, 30):
        x = round(HX + math.sin(math.radians(ang)) * 24)
        for yy in (SY0 + 7, SY1 - 3):
            cv.put(x, yy, MUSE, 7.6)
            cv.put(x + 1, yy, MUSE, 2.6)
    # tapa amb l'anell emissor
    cv.disc(HX, SY0 + 3, 26, 4.2, MUSE, lambda nx, ny: 6.4 - ny * 0.8 - nx * 0.6)
    cv.disc(HX, SY0 + 3, 20, 3, HOLO, lambda nx, ny: 4.6 - (nx * nx + ny * ny) * 1.5, 0)
    cv.disc(HX, SY0 + 3, 9, 1.4, HOLO, 5.5, 0)
    cv.glow(HX, SY0 + 2, 24, (150, 235, 255), 0.5)
    # ombra al terra
    cv.darken(SX0 - 2, SY1 + 1, SX1 + 2, SY1 + 4, lambda x, y: 0.7 - (y - SY1 - 1) * 0.2)


# ─── Sòcol (prop): una de les plaques descargolada, amb un paper amagat ──────

def socol(cv):
    # la placa de davant a la dreta (entre 15° i 45°), oberta i tort
    x0 = round(HX + math.sin(math.radians(15)) * 25)
    x1 = round(HX + math.sin(math.radians(45)) * 25)
    # forat fosc
    cv.rect(x0 + 1, SY0 + 6, x1, SY1 - 1, MUSE, 0.2, 0)
    cv.hline(x0 + 1, x1, SY0 + 6, MUSE, 1.0, 0)
    # cables a dins
    cv.line(x0 + 2, SY0 + 9, x1 - 1, SY0 + 12, RED, 2.4, 0.3)
    cv.line(x0 + 2, SY0 + 11, x1 - 2, SY0 + 8, HOLO, 2.2, 0)
    # el paper doblegat, amagat al forat
    cv.rect(x0 + 3, SY1 - 5, x0 + 8, SY1 - 2, PAPER, 4.2, 0.6)
    cv.hline(x0 + 3, x0 + 8, SY1 - 2, PAPER, 2.4, 0.6)
    # la placa, penjant d'un sol cargol i girada
    pts = [(x1 - 1, SY0 + 7), (x1 + 6, SY0 + 10), (x1 + 4, SY1 + 2), (x1 - 3, SY1)]
    cv.poly(pts, MUSE, lambda x, y: 4.8 - (y - SY0) / 10)
    cv.line(pts[0][0], pts[0][1], pts[1][0], pts[1][1], MUSE, 7.0)
    cv.line(pts[1][0], pts[1][1], pts[2][0], pts[2][1], MUSE, 2.2)
    cv.line(pts[3][0], pts[3][1], pts[2][0], pts[2][1], MUSE, 1.6)
    cv.put(x1, SY0 + 8, MUSE, 8.0)
    # cargol caigut al terra
    cv.put(x1 + 9, SY1 + 3, MUSE, 7.6)
    cv.put(x1 + 10, SY1 + 3, MUSE, 2.6)



# ─── Placa del robot (prop): a la vitrina, fins que s'obre ─────────────────

def placa_robot(cv):
    cv.rect(397, 109, 403, 113, IRON, lambda x, y: 4.4 - (y - 109) * 0.4)
    cv.put(398, 110, IRON, 6.0); cv.put(402, 110, IRON, 6.0)
    for x in (399, 400, 401):                                       # el nom gravat a mà, ratllat
        cv.put(x, 111 + (x & 1), IRON, 1.6)
    cv.hline(397, 403, 114, VELVET, 1.0)                            # ombra sota la placa


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
    for y in range(37, 93):
        for x in range(92, 168):
            p = on.P[x, y]
            if p != off.P[x, y]:
                cv.P[x, y] = p


PROPS = {'socol': socol, 'foto_mira': foto_mira, 'placa_robot': placa_robot}
