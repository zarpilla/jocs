# La Conjura de l'Avet

Aventura gràfica de «point & click» feta amb [Benne](https://benne.games/), a partir de 12 anys, de 2-3 hores. Sant
Joan de les Abadesses, any 1017. Una nit de tramuntana, l'avet que l'abadessa Emma va plantar fa 130 anys cau damunt
el mur del monestir. Al matí, el jutge del comte ja té escrita l'ordre contra les monges, i el llenyataire és al
celler del batlle. Les seves filles, la **Iri** (llenyatera) i la **Vet** (escrivana del monestir), saben que l'arbre
no l'ha tombat el vent.

Pla i decisions: [guio/pla.md](guio/pla.md). Guió: [guio/guio.md](guio/guio.md). Proposta inicial:
[guio/proposta-inicial.md](guio/proposta-inicial.md). Referències gràfiques: [guio/art/referencia/](guio/art/referencia/).

> Aquest joc és dins del repositori dels jocs de Mala Herba Soft. El nucli narratiu, l'adaptador de Benne, el motor i
> les eines són a l'arrel i els comparteixen tots els jocs (vegeu el [README de l'arrel](../../README.md)).

## Estat

Jugable de punta a punta, amb l'art, la música, els sons i les veus definitius (totes les línies gravades, amb
ElevenLabs: `npm run veus`; configuració a [game/audio/veus.json](game/audio/veus.json)). No es publica encara (no és a
`.github/workflows/publica.yml`).

## El que té de propi

- **Trams oberts i seguits.** A l'acte 1, a la preparació de l'acte 2, a l'arxiu de l'acte 3 i al matí de l'acte 4
  es pot canviar de germana (`switchWhen` a [game/data/game.json](game/data/game.json), amb la variable `fase`); a la
  resta, el joc passa d'una a l'altra. El botó «Canvia» del HUD fa de lupa (pista) quan no es pot canviar
  (`botoPista: 'mixt'` a [adapters/benne/joc.ts](adapters/benne/joc.ts)).
- **Sales amb mestressa**, com a Aigua Verne: el pont i la bugaderia són de l'Iri; el claustre (a l'acte 1),
  l'apotecaria i l'scriptorium, de la Vet. L'altra s'excusa a la porta.
- **Donar-se coses**: l'acció `donar` ([game/logic/index.ts](game/logic/index.ts)). El pot de resina no es dona: se'n
  dona un pegot (`props.dona`).
- **El calc amb carbonet**: la pantalla `calc`, on es frega el pergamí (tres tocs) i surt el segell de l'Emma o la
  carta de l'escrivà.
- La música d'algunes sales canvia a l'acte 4 (casos `{if, track}` a `music` del
  [mapping.json](adapters/benne/mapping.json)).
- Sense barra de verbs, amb la interfície tàctil compartida.

## L'art

- Sales en 3D a 1×: `adapters/benne/tools/hd640/rooms/` (`avet_comu.py` per a l'avet, la portada, el pròleg, el
  judici i l'epíleg; `placa_pont_comu.py`, `claustre_comu.py`, `nit_comu.py`). Redibuixar-ne una:
  `python3 redibuixa_sala.py <sala>` des de `adapters/benne/tools/`.
- Personatges: `adapters/benne/tools/hd/conjura.py` i `draw_characters.py [--installa]`; làmina a
  `guio/art/personatges.png`.
- Icones: `hd640/items.py`; HUD: `hd640/hud.py` (després, `hd640/pantalla.py`); làmines a `guio/art/`.
- Música: `tools/musica.py`; sons: `tools/sons.py`.

## Ordres

```bash
npm run validate     # comprova el contingut
npm run jugar        # juga en mode text (-- --tactil: com al mòbil)
npm run benne:sync   # porta el contingut al projecte Benne
npm run dev          # juga al navegador (cal `npm install` dins conjura-avet/)
```
