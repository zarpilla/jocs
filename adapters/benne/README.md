# Adaptador per a Benne

Tot el codi que depèn de Benne és aquí. Si canviem de motor, aquesta carpeta (i el projecte Benne)
és l'única que cal substituir: `game/` i `packages/narrative-core/` no canvien.

## Què hi ha

| Fitxer | Què fa |
|---|---|
| `runtime/narrative.ts` | Crea el `Narrative`, li explica el món de Benne (inventari, sales), desa l'estat dins les partides de Benne, executa `giveItem`/`takeItem`, mostra i amaga objectes condicionals, posa noms traduïts. |
| `runtime/narrative.script.ts` | Funcions de BenneScript que fan coses al llarg del temps: dir línies, conduir els diàlegs, dir una pista, mostrar un final. |
| `sync.ts` | Valida el contingut i el porta al projecte Benne. |
| `mapping.json` | Identificadors que no coincideixen entre el nostre JSON i Benne (per defecte, iguals). |

## Posar-ho en marxa (un sol cop)

1. A VS Code, amb l'extensió **BENNE Editor**: *BENNE: Create New Game*, plantilla **9-verb**,
   carpeta `joc-benne` dins d'aquest repositori.
2. Al `package.json` de `joc-benne`, afegeix la dependència del nucli i instal·la:
   ```json
   "dependencies": { "@aventura/narrative-core": "file:../packages/narrative-core" }
   ```
   ```bash
   cd joc-benne && npm install
   ```
3. Des de l'arrel: `npm run benne:sync` (o `npm run benne:sync -- --watch` mentre escrivim).

## Què genera el sync

- `joc-benne/src/game/narrative/`: el pont, `content.generated.json` (dades + textos) i
  `mapping.generated.json`.
- `joc-benne/src/game/dialogs/<id>/`: un diàleg de Benne per cada diàleg nostre. Totes les opcions
  de tots els nodes es converteixen en opcions de Benne (`<node>__<opció>`), i el pont n'encén
  només les que toquen a cada moment.

Tot porta la marca `GENERAT`: no s'edita a mà. El sync es nega a sobreescriure fitxers sense la marca.

## Com es fa servir des dels scripts de sala

```ts
// joc-benne/src/game/rooms/moll/moll.room.ts
import { walkToClicked } from '@benne/script';
import { dialogs } from '@game';
import { narrative, bindObjects } from '../../narrative/narrative';
import { sayHint } from '../../narrative/narrative.script';
import { room, pescador, esquer, llumFar, cucs } from './moll.ids';

room.onEnter(() => {
  // Objectes de objects.json ↔ props d'aquesta sala.
  bindObjects({ esquer_al_moll: esquer, llum_del_far: llumFar })
})

pescador.onTalkTo(() => {
  walkToClicked()
  dialogs.pescador.start()
})

cucs.onPickUp(() => {
  walkToClicked()
  narrative.apply({ giveItem: 'esquer' })   // missions i objectes s'actualitzen sols
})

// Lectures per a lògica pròpia de la sala:
//   narrative.flag('far_ences'), narrative.remembers('pescador', 'insultat'), narrative.relation('pescador')
```

Les pistes (`sayHint()`) i els finals (`playEnding()`) es poden lligar a un botó de GUI o a un verb.

Els esdeveniments del nucli que no són d'inventari arriben com a esdeveniments de Benne
`narrative:<tipus>` (p. ex. `events.on('narrative:questStarted', …)`), per si volem mostrar avisos
de missió o reaccionar a `{ "event": "..." }` del contingut.

## Limitacions conegudes de Benne (versió actual)

- **El text de les llistes d'opcions de diàleg és estàtic** a `*.dialog.json`: el sync l'escriu en
  un idioma (`--locale`). Les línies dites, els noms i les pistes sí que canvien d'idioma en temps
  real. Per tenir el joc en un altre idioma, de moment cal fer una compilació per idioma. Benne té
  la localització al seu full de ruta.
- Benne no permet desar enmig d'una conversa, així que la posició dins un diàleg no es desa (no cal).

## Pendent de provar dins Benne

El pont s'ha comprovat amb `tsc` contra els tipus reals de Benne, però encara no s'ha executat dins
un joc Benne. La primera prova serà amb la primera sala.
