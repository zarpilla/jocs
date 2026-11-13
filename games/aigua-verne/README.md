# Aigua Verne

Aventura gràfica de «point & click» feta amb [Benne](https://benne.games/): una comèdia espacial al sistema de
**Vesper**. L'aigua no s'ha acabat: el Magnat **Aurelià Verne** la bomba cap a tres dipòsits en òrbita i la torna a
vendre gota a gota. L'**Iri** (la pilot) i la **Vet** (l'enginyera), germanes d'acollida, només volen el pou de la
granja del pare. Per tenir-lo hauran d'obrir els dipòsits el dia que el Magnat s'ho juga tot.

Guió: [guio/guio.md](guio/guio.md). Fitxes de les sales (el contracte entre el contingut i l'art):
[guio/fitxes-sales.md](guio/fitxes-sales.md). Art de mostra: [guio/art/mostra/](guio/art/mostra/).

> Aquest joc és dins del repositori dels jocs de Mala Herba Soft. El nucli narratiu, l'adaptador de Benne, el motor i
> les eines són a l'arrel i els comparteixen tots els jocs (vegeu el [README de l'arrel](../../README.md)).

## Com és

| Què | Com |
|---|---|
| Estructura | Pròleg, 3 actes i 8 escenes, un final amb variacions (l'últim barril, les respostes a la Juana) |
| Protagonistes | L'Iri i la Vet, amb canvi lliure; les sales són compartides |
| Viatges | La Cantimplora: el mapa del pont (només el fa servir l'Iri) porta a qualsevol planeta obert; alguns trencaclosques demanen tornar a un planeta |
| Comunicació | El comunicador de canell (repeteix què toca fer) i la Mosca, el dron que porta objectes a l'altra si són al mateix planeta |
| Sincronies | Per torns: la colada de les claus (la temperatura del forn) i la subhasta (els lots) |
| Resolució | 640×360, amb **dues mides de personatge**: ≈83 px a les sales de lluny i ≈100 px a les de prop (roba `Lluny` a `characters.json`) |

## Regles en codi (`game/logic/`)

- `sincronia.ts`: els dos passos per torns; els textos són a `sincronies.json`.
- `escenes.ts`: canvis d'escena automàtics; les transicions són a `transicions.json`.
- `mosca.ts`: la Mosca (mateix planeta, no al palau, `mosca: true` a items.json).
- `safata.ts`: la safata de les copes del palau, de l'Iri (saló) a la Vet (servei).
- `donar.ts`: donar un objecte a l'altra a la mateixa sala.

## Ordres

```bash
npm run jugar          # juga en mode text
npm test               # el joc sencer pels dos camins, amb una pista a cada pas
npm run validate       # comprova el contingut
npm run sons           # efectes de so (tools/sons.py)
npm run musica         # música (tools/musica.py)
npm run benne:sync     # porta el contingut i l'art al projecte Benne
npm run dev            # juga al navegador (cal `npm install` dins aigua-verne/)
```

## Art

Cada sala és un mòdul `adapters/benne/tools/hd640/rooms/<sala>.py` (fons, props, animacions i `GEOMETRIA`), amb peces
comunes per planeta (`*_comu.py`). Els personatges són a `adapters/benne/tools/hd/personatges.py` i els fulls els fa
`python3 adapters/benne/tools/draw_characters.py`. Les icones i la interfície, a `hd640/items.py`, `hd640/gui.py` i
`hd640/gui_rest.py`. `python3 adapters/benne/tools/hd640/preview.py --res 640 <sala> <sortida>` en fa una
previsualització.
