# Adaptador per a Benne

Tot el codi que depèn de Benne és aquí. Si canviem de motor, aquesta carpeta (i el projecte Benne)
és l'única que cal substituir: `game/` i `packages/narrative-core/` no canvien.

## Què hi ha

| Fitxer | Què fa |
|---|---|
| `runtime/narrative.ts` | Crea el `Narrative` i hi instal·la la lògica del joc (`game/logic`). Li explica el món de Benne: inventari de cada protagonista, sales, qui juga. Desa l'estat dins les partides de Benne i executa `giveItem`/`takeItem`. Mostra i amaga coses condicionals, i posa els noms traduïts. |
| `runtime/narrative.script.ts` | Funcions de BenneScript que fan coses al llarg del temps: dir línies, resoldre interaccions del JSON, conduir els diàlegs, canviar de protagonista, dir una pista, mostrar un final. |
| `templates/globalScript.ts` | El `globalScript.ts` del projecte Benne. Envia totes les interaccions sense gestor propi i l'entrada a cada sala al JSON. |
| `sync.ts` | Valida el contingut i el porta al projecte Benne. |
| `mapping.json` | Identificadors que no coincideixen entre el nostre JSON i Benne (`characters`, `items`, `rooms`, `hotspots`). Per defecte, són iguals. |

## Posar-ho en marxa (un sol cop)

1. A VS Code, amb l'extensió **BENNE Editor**: *BENNE: Create New Game*, plantilla **9-verb**,
   carpeta `joc-benne` dins d'aquest repositori.
2. Al `package.json` de `joc-benne`, afegeix les dependències i instal·la:
   ```json
   "dependencies": {
     "@aventura/narrative-core": "file:../packages/narrative-core",
     "@aventura/game": "file:../game"
   }
   ```
   ```bash
   cd joc-benne && npm install
   ```
3. Des de l'arrel: `npm run benne:sync -- --init`. Fa una còpia de l'antic `globalScript.ts` a
   `.bak` i hi posa el de l'adaptador. Després, `npm run benne:sync` (o amb `--watch` mentre escrivim).
4. A Benne, crea els personatges `iri` i `vet` (les dues protagonistes) i els altres de
   `characters.json`. Crea les sales i les coses de [guio/fitxes-sales.md](../../guio/fitxes-sales.md)
   amb aquests ids (`npm run fitxes` la regenera).

## Què genera el sync

- `joc-benne/src/game/narrative/`: el pont, `content.generated.json` (dades i textos) i
  `mapping.generated.json`.
- `joc-benne/src/game/dialogs/<id>/`: un diàleg de Benne per cada diàleg nostre. Totes les opcions
  de tots els nodes es converteixen en opcions de Benne (`<node>__<opció>`), i el pont encén
  només les que toquen a cada moment.
- Amb `--init`: `joc-benne/src/game/globalScript.ts`.

Tot porta la marca `GENERAT`: no s'edita a mà. El sync es nega a sobreescriure fitxers sense la marca.

## Com funciona una interacció

1. A Benne, el jugador fa «Fer servir clau anglesa amb palanca».
2. Cap script de sala no la gestiona, i arriba a `fallbacks.onUseItem`, al `globalScript.ts`.
3. `routeInteraction` la tradueix (`fabrica_cambra-hotspot-palanca` → `palanca`) i la passa al nucli.
4. El nucli busca la interacció a `game/data/rooms/fabrica_cambra.json` i aplica els efectes. Retorna
   les línies, el diàleg, la sala o el canvi de protagonista.
5. `playResult` ho fa a Benne: `player.say`, `dialogs.x.start()`, `player.switchTo`, `rooms.x.goTo()`.

Els scripts de sala de Benne només calen per a coses visuals (animacions, moviments, càmera) i per
lligar les coses condicionals:

```ts
// joc-benne/src/game/rooms/fabrica_calderes/fabrica_calderes.room.ts
import { bindHotspots } from '../../narrative/narrative';
import { room, segell } from './fabrica_calderes.ids';

room.onEnter(() => {
  bindHotspots({ segell })   // apareix quan el capatàs el deixa caure
})
```

Per a la GUI: `switchProtagonist()` (botó de canviar entre l'Iri i la Vet), `sayHint()` (botó de
pista) i `playEnding()`.

Els esdeveniments del nucli arriben com a esdeveniments de Benne `narrative:<tipus>` (per exemple,
`events.on('narrative:questStarted', …)` o `events.on('narrative:finestra.transferencia', …)` per a
l'efecte visual de la finestra).

## Limitacions conegudes de Benne (versió actual)

- **El text de les llistes d'opcions de diàleg és estàtic** a `*.dialog.json`: el sync l'escriu en
  un idioma (`--locale`). Les línies dites, els noms i les pistes sí que canvien d'idioma en temps
  real. Per tenir el joc en un altre idioma, de moment cal fer una compilació per idioma. Benne té
  la localització al seu full de ruta.
- Benne no permet desar enmig d'una conversa, així que la posició dins un diàleg no es desa (no cal).
- `fallbacks.onUnhandled` no porta la informació del clic, i per tant `walkToClicked()` potser no
  camina. Si cal que la protagonista s'hi acosti, es pot fer des de l'script de la sala.

## Pendent de provar dins Benne

El pont s'ha comprovat amb `tsc` contra els tipus reals de Benne (amb la plantilla 9-verb i els
diàlegs generats), però **encara no s'ha executat dins un joc Benne**. Coses a confirmar a la primera
prova:

- que `gameState:replaced` es dispara en començar una partida nova (si no, els inventaris inicials no
  es reparteixen);
- que `player.switchTo` porta a la sala de l'altra protagonista;
- que les interaccions arriben a `fallbacks.onUnhandled` i a `onUseItem` / `onGiveItem`;
- quins ids exactes posa Benne a les coses de sala (per si cal ajustar el `mapping.json`).
