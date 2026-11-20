# L'Última Arrel

Aventura gràfica de «point & click» feta amb [Benne](https://benne.games/), per a nenes de 8 a 12 anys. Al Bosc de la
Coma, l'empresa **NaturaPlus S.A.** vol fer-hi el «Bosc 2.0»: arbres de plàstic amb Wi-Fi, gespa que no s'ha de regar
i Aire Pur embotellat. Les excavadores han tallat la **Xarxa Miceli**, l'internet dels fongs que lliga les arrels. La
**Iri** (11 anys) i la **Vet** (9), germanes, tenen un cap de setmana per tornar-la a encendre i fer que la
presentació a la premsa digui la veritat.

Guió: [guio/guio.md](guio/guio.md). Fitxes de les sales (el contracte entre el contingut i l'art):
[guio/fitxes-sales.md](guio/fitxes-sales.md). Pla de feina: [guio/pla.md](guio/pla.md). Art de mostra i
referències: [guio/art/](guio/art/).

> Aquest joc és dins del repositori dels jocs de Mala Herba Soft. El nucli narratiu, l'adaptador de Benne, el motor i
> les eines són a l'arrel i els comparteixen tots els jocs (vegeu el [README de l'arrel](../../README.md)).

## El que té de propi

- **Una escena, una germana.** Cada escena la juga una sola de les dues, i no es pot canviar: el joc passa a l'altra
  quan comença l'escena següent, amb un rètol de temps. Es parlen pel **walkie**. L'única excepció: la Vet juga la 5
  i la 6a seguides (pel mig hi ha el rètol del dilluns, i la Iri és al bus); vegeu el [guió](guio/guio.md).
- **La lupa** és el botó de pista. Al HUD tàctil ocupa el lloc del botó «Canvia» (`botoPista` a
  [adapters/benne/joc.ts](adapters/benne/joc.ts)): en prémer-la, surt la pista i uns **filaments turquesa** que van de
  la protagonista a les coses on apunta (`targets` a [game/data/hints.json](game/data/hints.json),
  `game.showThreads` al motor). Quan juga la Vet, la pista li diu la Iri pel walkie (`who`). La targeta «Com es juga» ho diu a
  l'última fila, amb la lupa.
- Sense barra de verbs, amb la interfície tàctil compartida, com Suma Zero, Ni un ou i Aigua Verne.

## Ordres

```bash
npm run validate     # comprova el contingut
npm run jugar        # juga en mode text (-- --tactil: com al mòbil)
npm test             # la partida sencera, amb una pista a cada pas, i el camí amb el dit i amb el ratolí
EXPLORA=/tmp/explora.txt npx vitest run --root ../.. games/ultima-arrel/game/test/explora.test.ts
                     # escriu una transcripció que ho mira tot a cada escena (per llegir-la com una jugadora)
npm run sons         # efectes i ambients (tools/sons.py)
npm run musica       # música (tools/musica.py)
npm run benne:sync   # porta el contingut al projecte Benne
npm run dev          # juga al navegador
```
