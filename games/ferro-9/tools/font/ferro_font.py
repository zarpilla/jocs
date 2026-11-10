"""Font de píxel pròpia de Ferro-9, dibuixada des de zero.

Genera fonts en mapa de bits en format BMFont (un .xml i una imatge _0.png),
el format que Benne/Phaser carrega des de ferro-9/src/game/assets/fonts/fonts.json.

  npm run font      (escriu a ferro-9/src/game/assets/fonts/)
  python3 tools/font/ferro_font.py [carpeta_de_sortida]

Surten dues variants:
  ferro-regular  per als diàlegs i la línia d'acció
  ferro-negreta  per als verbs i el que diuen els personatges (cada traç fa 2 px d'ample)

Graella de 12 files per lletra:
  files 0-1   accents de les majúscules
  files 3-9   majúscules, xifres i ascendents (7 px d'alçada)
  files 5-9   minúscules (5 px)
  files 10-11 descendents (g, j, p, q, y) i ce trencada
Cada lletra es dibuixa a partir de la fila 3, amb '#' per als píxels pintats.
"""

import sys
from pathlib import Path

from PIL import Image

LINE_HEIGHT = 12
# Mida que declara la font. Benne escala el text per fontSize / mida, i les GUI fan servir
# fontSize 8 (o 16 per a doble mida): amb 8 cada píxel de la font és un píxel de pantalla.
NOMINAL_SIZE = 8
DEFAULT_OUT = Path(__file__).resolve().parents[2] / "ferro-9/src/game/assets/fonts"
TOP = 3  # fila on comença el dibuix de cada lletra
BASE = 10  # primera fila sota la línia de base

# Majúscules, xifres i signes: 7 files (de la 3 a la 9) i, si cal, 2 de descendent.
# Minúscules: 2 files d'ascendent buides o plenes + 5 d'ull + 2 de descendent.
GLYPHS = {
    "A": [".###.", "#...#", "#...#", "#####", "#...#", "#...#", "#...#"],
    "B": ["####.", "#...#", "#...#", "####.", "#...#", "#...#", "####."],
    "C": [".###.", "#...#", "#....", "#....", "#....", "#...#", ".###."],
    "D": ["####.", "#...#", "#...#", "#...#", "#...#", "#...#", "####."],
    "E": ["#####", "#....", "#....", "####.", "#....", "#....", "#####"],
    "F": ["#####", "#....", "#....", "####.", "#....", "#....", "#...."],
    "G": [".###.", "#...#", "#....", "#.###", "#...#", "#...#", ".####"],
    "H": ["#...#", "#...#", "#...#", "#####", "#...#", "#...#", "#...#"],
    "I": ["###", ".#.", ".#.", ".#.", ".#.", ".#.", "###"],
    "J": ["..###", "...#.", "...#.", "...#.", "#..#.", "#..#.", ".##.."],
    "K": ["#...#", "#..#.", "#.#..", "##...", "#.#..", "#..#.", "#...#"],
    "L": ["#....", "#....", "#....", "#....", "#....", "#....", "#####"],
    "M": ["#...#", "##.##", "#.#.#", "#.#.#", "#...#", "#...#", "#...#"],
    "N": ["#...#", "##..#", "#.#.#", "#.#.#", "#..##", "#...#", "#...#"],
    "O": [".###.", "#...#", "#...#", "#...#", "#...#", "#...#", ".###."],
    "P": ["####.", "#...#", "#...#", "####.", "#....", "#....", "#...."],
    "Q": [".###.", "#...#", "#...#", "#...#", "#.#.#", "#..#.", ".##.#"],
    "R": ["####.", "#...#", "#...#", "####.", "#.#..", "#..#.", "#...#"],
    "S": [".###.", "#...#", "#....", ".###.", "....#", "#...#", ".###."],
    "T": ["#####", "..#..", "..#..", "..#..", "..#..", "..#..", "..#.."],
    "U": ["#...#", "#...#", "#...#", "#...#", "#...#", "#...#", ".###."],
    "V": ["#...#", "#...#", "#...#", "#...#", ".#.#.", ".#.#.", "..#.."],
    "W": ["#...#", "#...#", "#...#", "#.#.#", "#.#.#", "##.##", "#...#"],
    "X": ["#...#", "#...#", ".#.#.", "..#..", ".#.#.", "#...#", "#...#"],
    "Y": ["#...#", "#...#", ".#.#.", "..#..", "..#..", "..#..", "..#.."],
    "Z": ["#####", "....#", "...#.", "..#..", ".#...", "#....", "#####"],
    "a": [".....", ".....", ".###.", "....#", ".####", "#...#", ".####"],
    "b": ["#....", "#....", "####.", "#...#", "#...#", "#...#", "####."],
    "c": ["....", "....", ".###", "#...", "#...", "#...", ".###"],
    "d": ["....#", "....#", ".####", "#...#", "#...#", "#...#", ".####"],
    "e": [".....", ".....", ".###.", "#...#", "#####", "#....", ".###."],
    "f": ["..##", ".#..", "####", ".#..", ".#..", ".#..", ".#.."],
    "g": [".....", ".....", ".####", "#...#", "#...#", "#...#", ".####", "....#", ".###."],
    "h": ["#....", "#....", "####.", "#...#", "#...#", "#...#", "#...#"],
    "i": ["#", ".", "#", "#", "#", "#", "#"],
    "j": ["..#", "...", "..#", "..#", "..#", "..#", "..#", "..#", "##."],
    "k": ["#...", "#...", "#..#", "#.#.", "##..", "#.#.", "#..#"],
    "l": ["#.", "#.", "#.", "#.", "#.", "#.", ".#"],
    "m": [".....", ".....", "####.", "#.#.#", "#.#.#", "#.#.#", "#.#.#"],
    "n": [".....", ".....", "####.", "#...#", "#...#", "#...#", "#...#"],
    "o": [".....", ".....", ".###.", "#...#", "#...#", "#...#", ".###."],
    "p": [".....", ".....", "####.", "#...#", "#...#", "#...#", "####.", "#....", "#...."],
    "q": [".....", ".....", ".####", "#...#", "#...#", "#...#", ".####", "....#", "....#"],
    "r": ["....", "....", "#.##", "##..", "#...", "#...", "#..."],
    "s": [".....", ".....", ".####", "#....", ".###.", "....#", "####."],
    "t": [".#..", ".#..", "####", ".#..", ".#..", ".#..", "..##"],
    "u": [".....", ".....", "#...#", "#...#", "#...#", "#...#", ".####"],
    "v": [".....", ".....", "#...#", "#...#", "#...#", ".#.#.", "..#.."],
    "w": [".....", ".....", "#...#", "#...#", "#.#.#", "#.#.#", ".#.#."],
    "x": [".....", ".....", "#...#", ".#.#.", "..#..", ".#.#.", "#...#"],
    "y": [".....", ".....", "#...#", "#...#", "#...#", "#...#", ".####", "....#", ".###."],
    "z": [".....", ".....", "#####", "...#.", "..#..", ".#...", "#####"],
    "ı": [".", ".", "#", "#", "#", "#", "#"],  # i sense punt, base de í, ì, ï
    "0": [".###.", "#...#", "#..##", "#.#.#", "##..#", "#...#", ".###."],
    "1": [".#.", "##.", ".#.", ".#.", ".#.", ".#.", "###"],
    "2": [".###.", "#...#", "....#", "...#.", "..#..", ".#...", "#####"],
    "3": [".###.", "#...#", "....#", "..##.", "....#", "#...#", ".###."],
    "4": ["...#.", "..##.", ".#.#.", "#..#.", "#####", "...#.", "...#."],
    "5": ["#####", "#....", "####.", "....#", "....#", "#...#", ".###."],
    "6": [".###.", "#....", "#....", "####.", "#...#", "#...#", ".###."],
    "7": ["#####", "....#", "...#.", "..#..", ".#...", ".#...", ".#..."],
    "8": [".###.", "#...#", "#...#", ".###.", "#...#", "#...#", ".###."],
    "9": [".###.", "#...#", "#...#", ".####", "....#", "....#", ".###."],
    ".": [".", ".", ".", ".", ".", ".", "#"],
    ",": ["..", "..", "..", "..", "..", "..", ".#", "#."],
    ":": [".", ".", ".", "#", ".", ".", "#"],
    ";": ["..", "..", "..", ".#", "..", "..", ".#", "#."],
    "!": ["#", "#", "#", "#", "#", ".", "#"],
    "?": [".###.", "#...#", "....#", "..##.", "..#..", ".....", "..#.."],
    "'": ["#", "#"],
    "’": [".#", "#."],
    '"': ["#.#", "#.#"],
    "-": ["...", "...", "...", "###"],
    "—": [".....", ".....", ".....", "#####"],
    "_": [".....", ".....", ".....", ".....", ".....", ".....", ".....", ".....", "#####"],
    "·": [".", ".", ".", ".", "#"],
    "«": ["....", "....", "....", ".#.#", "#.#.", ".#.#"],
    "»": ["....", "....", "....", "#.#.", ".#.#", "#.#."],
    "(": [".#", "#.", "#.", "#.", "#.", "#.", ".#"],
    ")": ["#.", ".#", ".#", ".#", ".#", ".#", "#."],
    "{": [".##", ".#.", ".#.", "#..", ".#.", ".#.", ".##"],
    "}": ["##.", ".#.", ".#.", "..#", ".#.", ".#.", "##."],
    "/": ["..#", "..#", ".#.", ".#.", ".#.", "#..", "#.."],
    "→": [".....", ".....", "...#.", "#####", "...#."],
    "…": [".....", ".....", ".....", ".....", ".....", ".....", "#.#.#"],
}

# Accents: es posen damunt de la lletra base (2 files per sobre de la seva primera fila amb tinta).
ACCENTS = {"grave": ["#.", ".#"], "acute": [".#", "#."], "diaeresis": ["#.#"]}
BOLD_ACCENTS = {"grave": ["##.", ".##"], "acute": [".##", "##."], "diaeresis": ["##.##"]}
COMPOSED = {
    "à": ("a", "grave"), "è": ("e", "grave"), "é": ("e", "acute"), "ì": ("ı", "grave"),
    "í": ("ı", "acute"), "ï": ("ı", "diaeresis"), "ò": ("o", "grave"), "ó": ("o", "acute"),
    "ù": ("u", "grave"), "ú": ("u", "acute"), "ü": ("u", "diaeresis"),
    "À": ("A", "grave"), "È": ("E", "grave"), "É": ("E", "acute"), "Í": ("I", "acute"),
    "Ï": ("I", "diaeresis"), "Ò": ("O", "grave"), "Ó": ("O", "acute"), "Ú": ("U", "acute"),
    "Ü": ("U", "diaeresis"),
}
CEDILLA = {"ç": "c", "Ç": "C"}
SPACE_ADVANCE = 3

# Negreta: es fa doblant cada traç cap a la dreta, però les lletres amb traços
# molt junts quedarien plenes. Aquestes es dibuixen a part, i els signes de
# KEEP_REGULAR es queden com a la regular. Les lletres compostes (accents,
# ce trencada) es munten sobre la base ja en negreta.
BOLD = {
    "M": ["##....##", "###..###", "##.##.##", "##.##.##", "##....##", "##....##", "##....##"],
    "W": ["##....##", "##....##", "##....##", "##.##.##", "##.##.##", "###..###", "##....##"],
    "m": ["........", "........", "#######.", "##.##.##", "##.##.##", "##.##.##", "##.##.##"],
    "w": ["........", "........", "##....##", "##....##", "##.##.##", "##.##.##", ".##..##."],
}
KEEP_REGULAR = set("«»\"'’→")


def to_grid(rows):
    """Lletra (llista de cadenes des de la fila TOP) -> conjunt de píxels (x, y) i amplada."""
    width = max(len(r) for r in rows)
    pixels = {(x, TOP + y) for y, r in enumerate(rows) for x, ch in enumerate(r) if ch == "#"}
    return pixels, width


def compose(base, accent, bold=False):
    pixels, width = to_grid(GLYPHS[base])
    if bold:
        pixels, width = embolden(pixels, width)
    mark = (BOLD_ACCENTS if bold else ACCENTS)[accent]
    mark_w = len(mark[0])
    new_w = max(width, mark_w)
    shift = (new_w - width) // 2
    if base == "ı" and accent == "grave" and not bold:
        shift = 1  # el traç de l'accent greu acaba a la dreta: hi posem la i a sota
    pixels = {(x + shift, y) for x, y in pixels}
    top = min(y for _, y in pixels)
    mx = (new_w - mark_w) // 2
    my = top - 1 - len(mark)  # una fila de separació
    for y, r in enumerate(mark):
        for x, ch in enumerate(r):
            if ch == "#":
                pixels.add((mx + x, my + y))
    return pixels, new_w


def cedilla(base, bold=False):
    pixels, width = to_grid(GLYPHS[base])
    cx = width // 2
    pixels |= {(cx, BASE), (cx - 1, BASE + 1)}
    return embolden(pixels, width) if bold else (pixels, width)


def all_glyphs(bold=False):
    out = {}
    for ch, rows in GLYPHS.items():
        if ch == "ı":
            continue
        glyph = to_grid(BOLD.get(ch, rows) if bold else rows)
        if bold and ch not in BOLD and ch not in KEEP_REGULAR:
            glyph = embolden(*glyph)
        out[ch] = glyph
    out.update({ch: compose(b, a, bold) for ch, (b, a) in COMPOSED.items()})
    out.update({ch: cedilla(b, bold) for ch, b in CEDILLA.items()})
    return out


def embolden(pixels, width):
    return pixels | {(x + 1, y) for x, y in pixels}, width + 1


def build(name, face, glyphs, out_dir):
    chars = sorted(glyphs)
    cols = 16
    cell_w = max(w for _, w in glyphs.values()) + 1
    rows = (len(chars) + 1 + cols - 1) // cols
    sheet = Image.new("RGBA", (cols * cell_w, rows * LINE_HEIGHT), (0, 0, 0, 0))
    entries = []
    for i, ch in enumerate([" "] + chars):
        x0, y0 = (i % cols) * cell_w, (i // cols) * LINE_HEIGHT
        if ch == " ":
            w, adv = SPACE_ADVANCE, SPACE_ADVANCE
        else:
            pixels, w = glyphs[ch]
            adv = w + 1
            for x, y in pixels:
                sheet.putpixel((x0 + x, y0 + y), (255, 255, 255, 255))
        entries.append(
            f'    <char id="{ord(ch)}" x="{x0}" y="{y0}" width="{w}" height="{LINE_HEIGHT}" '
            f'xoffset="0" yoffset="0" xadvance="{adv}" page="0" chnl="15" />'
        )
    sheet.save(out_dir / f"{name}_0.png")
    xml = "\n".join([
        '<?xml version="1.0"?>',
        "<font>",
        f'  <info face="{face}" size="-{NOMINAL_SIZE}" bold="0" italic="0" charset="" unicode="1" '
        'stretchH="100" smooth="0" aa="1" padding="0,0,0,0" spacing="1,0" outline="0"/>',
        f'  <common lineHeight="{LINE_HEIGHT}" base="{BASE}" scaleW="{sheet.width}" scaleH="{sheet.height}" '
        'pages="1" packed="0" alphaChnl="0" redChnl="4" greenChnl="4" blueChnl="4"/>',
        "  <pages>",
        f'    <page id="0" file="{name}_0.png" />',
        "  </pages>",
        f'  <chars count="{len(entries)}">',
        *entries,
        "  </chars>",
        "</font>",
        "",
    ])
    (out_dir / f"{name}.xml").write_text(xml, encoding="utf-8")


def main():
    out_dir = Path(sys.argv[1]) if len(sys.argv) > 1 else DEFAULT_OUT
    out_dir.mkdir(parents=True, exist_ok=True)
    glyphs = all_glyphs()
    build("ferro-regular", "Ferro Regular", glyphs, out_dir)
    build("ferro-negreta", "Ferro Negreta", all_glyphs(bold=True), out_dir)
    print(f"{len(glyphs) + 1} caràcters -> {out_dir}")


if __name__ == "__main__":
    main()
