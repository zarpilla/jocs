#!/usr/bin/env python3
"""
Passa el projecte Benne de Ferro-9 de 480×270 a 640×360 (una vegada; és idempotent).

  - game-config.json: la resolució i l'alçada de la llista d'opcions de diàleg (hd640/guis/game-config.640.json);
  - GUI: els fulls i els .gui.json de hd640/guis/ (els fa hd640/gui_rest.py) i el cursor, sense les marques que
    farien que el sync els tornés a dibuixar a 480;
  - fonts: ferro-regular i ferro-negreta de 640 (hd640/font.py), en BMFont;
  - personatges: placeholder-art/ amb els de 640 (draw_characters.py, que a 640 crida hd640/draw_characters.py);
  - historial: s'esborra (GUI i art) perquè joc.ts el torni a fer a 640, amb el fons del menú nou;
  - sales: la mida i tota la geometria ×4/3 (el sync després la reescriu des de room_designs.py, a 640/352),
    i la marca `.provisional` perquè draw_placeholders torni a dibuixar el fons i les animacions a 640;
  - inventari: la marca `.provisional`, perquè el redibuixi amb les icones de hd640/items.py.

Abans cal posar escala.RESOLUCIO = 640. Després, `npm run benne:sync` (des de games/ferro-9/), que ho redibuixa tot a 640.
Ús: python3 hd640/aplica.py [src/game del projecte Benne]
"""
import json
import shutil
import subprocess
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
TOOLS = HERE.parent
GAME = Path(sys.argv[1]) if len(sys.argv) > 1 else TOOLS.parents[2] / 'ferro-9/src/game'
K = 640 / 480
ROOM_KEYS = {'x', 'y', 'width', 'height', 'baseline'}
MARQUES = ('.provisional', '.generat', '.canvia-provisional')


def load(p):
    return json.loads(Path(p).read_text(encoding='utf-8'))


def save(p, data):
    Path(p).write_text(json.dumps(data, indent=2, ensure_ascii=False) + '\n', encoding='utf-8')


def scale(o):
    if isinstance(o, dict):
        for k, v in o.items():
            if k in ROOM_KEYS and isinstance(v, (int, float)) and not isinstance(v, bool):
                o[k] = round(v * K)
            else:
                scale(v)
    elif isinstance(o, list):
        for v in o:
            scale(v)


def config():
    p = GAME / 'game-config.json'
    cfg = load(p)
    extra = load(HERE / 'guis/game-config.640.json')
    cfg['resolution'] = extra['resolution']
    cfg.setdefault('dialog', {}).update(extra.get('dialog', {}))
    save(p, cfg)
    print('✔ game-config.json: 640×360')


def guis():
    for d in sorted((HERE / 'guis').iterdir()):
        if not d.is_dir():
            continue
        name = d.name
        art = GAME / 'assets/images' / ('cursor' if name == 'cursor' else f'guis/{name}')
        for f in d.iterdir():
            if f.name.endswith('.gui.json'):
                (GAME / 'guis' / name).mkdir(parents=True, exist_ok=True)
                shutil.copy2(f, GAME / 'guis' / name / f.name)
            elif f.suffix in ('.png', '.json'):
                art.mkdir(parents=True, exist_ok=True)
                shutil.copy2(f, art / f.name)
        for m in MARQUES:
            (art / m).unlink(missing_ok=True)
        # el full d'Aseprite de 480 ja no correspon al PNG
        (art / f'{name}.aseprite').unlink(missing_ok=True)
    print('✔ GUI i cursor de 640')


def fonts():
    subprocess.run([sys.executable, str(HERE / 'font.py'), str(GAME / 'assets/fonts')], check=True)
    print('✔ fonts de 640')


def historial():
    for d in (GAME / 'guis/historial', GAME / 'assets/images/guis/historial'):
        if d.exists():
            shutil.rmtree(d)
    print("✔ historial esborrat (joc.ts el torna a fer al sync)")


def characters():
    subprocess.run([sys.executable, str(TOOLS / 'draw_characters.py')], check=True)
    for d in (GAME / 'assets/images/characters').iterdir():
        if d.is_dir():
            (d / '.provisional').write_text('Art provisional: esborra aquest fitxer quan el sprite sigui definitiu.\n')
    print('✔ personatges de 640 (placeholder-art/)')


def rooms():
    n = 0
    for p in sorted((GAME / 'rooms').glob('*/*.room.json')):
        room = load(p)
        if room['size']['width'] == 480:
            scale(room)
            save(p, room)
            n += 1
        art = GAME / 'assets/images/rooms' / p.parent.name
        art.mkdir(parents=True, exist_ok=True)
        (art / '.provisional').write_text('Art provisional: esborra aquest fitxer quan el PNG sigui definitiu.\n')
    inv = GAME / 'assets/images/inventory'
    inv.mkdir(parents=True, exist_ok=True)
    (inv / '.provisional').write_text("Art provisional: esborra aquest fitxer quan el PNG sigui definitiu.\n")
    print(f'✔ sales: {n} passades a 640×360 (geometria ×4/3)')


if __name__ == '__main__':
    sys.path.insert(0, str(TOOLS))
    from escala import RESOLUCIO
    if RESOLUCIO != 640:
        sys.exit('Primer posa RESOLUCIO = 640 a escala.py.')
    config()
    guis()
    historial()
    fonts()
    characters()
    rooms()
    print('Ara: npm run benne:sync (des de games/ferro-9/)')
