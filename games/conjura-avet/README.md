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

**Esquelet** (fase 1 de la [guia de joc nou](../../docs/guia-joc-nou.md)): una sala provisional (`mur_avet`) amb
l'avet, les arrels i el jutge Ponç, la portada i els crèdits. El projecte Benne es crea, se sincronitza, compila i
s'obre al navegador. La història és al guió, pendent de revisar.

Les eines d'art (`adapters/benne/tools/`) són una còpia de les de L'Última Arrel, sense les sales: el HUD
(`hd640/hud.py`) encara té la paleta del bosc, i `room_designs.py`, els dissenys provisionals d'aquell joc.

## El que té de propi

- **Una sala, una germana**, com a L'Última Arrel: no es pot canviar de protagonista (`switchWhen` que no es compleix
  mai, i `botoPista` a [adapters/benne/joc.ts](adapters/benne/joc.ts)). En tres sales col·laboren (vegeu el guió).
- Sense barra de verbs, amb la interfície tàctil compartida.

## Ordres

```bash
npm run validate     # comprova el contingut
npm run jugar        # juga en mode text (-- --tactil: com al mòbil)
npm run benne:sync   # porta el contingut al projecte Benne
npm run dev          # juga al navegador (cal `npm install` dins conjura-avet/)
```
