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

## El projecte Benne: `ferro-9/`

Ja està creat i dins del repositori. Per jugar:

```bash
cd ferro-9
npm install      # la primera vegada (cal haver fet també `npm install` a l'arrel)
npm run dev      # obre el joc al navegador
```

Al joc: botó de menú (a baix a l'esquerra) → **Canvia** (a l'altra protagonista) i **Pista**.

Com s'ha creat (per si mai cal refer-lo o actualitzar el motor):

```bash
git clone https://github.com/Bennethon/benne /algun/lloc/benne
npm run benne:create -- --from /algun/lloc/benne [--force]   # --force: només substitueix el motor
npm run benne:sync -- --init
```

`benne:create` fa el mateix que l'ordre *BENNE: Create New Game* de l'extensió (copia el motor i la
plantilla 9-verb, sense la demo), però sense VS Code ni executar codi de Benne. Si prefereixes fer
servir l'extensió de VS Code per editar sales, obre la carpeta `ferro-9`: és un projecte Benne normal.

## Què genera el sync

- `ferro-9/src/game/narrative/`: el pont, `content.generated.json` (dades i textos) i
  `mapping.generated.json`.
- `ferro-9/src/game/dialogs/<id>/`: un diàleg de Benne per cada diàleg nostre. Totes les opcions
  de tots els nodes es converteixen en opcions de Benne (`<node>__<opció>`), i el pont encén
  només les que toquen a cada moment.
- `ferro-9/src/game/globalScript.ts`: el bloc entre les marques es regenera sempre; el que hi
  afegeixis a sota es conserva. (La primera vegada, `--init`.)
- **Sales, personatges i objectes que encara no existeixen a Benne**, amb una disposició automàtica i
  **art provisional** (caixes etiquetades; cal `python3` amb Pillow). El que ja existeix no es toca:
  quan un artista substitueixi un PNG, ha d'esborrar el fitxer `.provisional` del costat.
- **Tots els textos de Benne en l'idioma triat**: verbs (`ui.verb.*`), menús (`ui.menu.*`...), noms
  de coses, personatges i objectes.
- Botons **Canvia** i **Pista** al menú del joc (una sola vegada).

Tot porta la marca `GENERAT`: no s'edita a mà. El sync es nega a sobreescriure fitxers sense la marca.

## Com funciona una interacció

1. A Benne, el jugador fa «Usa clau anglesa amb palanca».
2. Cap script de sala no la gestiona, i arriba a `fallbacks.onUseItem`, al `globalScript.ts`.
3. `routeInteraction` la tradueix (`fabrica_cambra-hotspot-palanca` → `palanca`) i la passa al nucli.
4. El nucli busca la interacció a `game/data/rooms/fabrica_cambra.json` i aplica els efectes. Retorna
   les línies, el diàleg, la sala o el canvi de protagonista.
5. `playResult` ho fa a Benne: `player.say`, `dialogs.x.start()`, `player.switchTo`, `rooms.x.goTo()`.

Els scripts de sala de Benne només calen per a coses visuals (animacions, moviments, càmera). Les
coses amb `visibleIf` es generen com a **props** i el pont les mostra o amaga soles.

## Dues protagonistes en una sola Benne

A Benne, `player.switchTo` només funciona amb personatges de la mateixa sala, i l'Iri i la Vet no
coincideixen mai. Per això **cada sala és d'una protagonista** (`"protagonist"` al JSON de la sala):
canviar de protagonista vol dir anar a la sala on és l'altra, i en entrar-hi el pont en pren el
control. L'última sala de cada protagonista es desa amb la partida.

## Escenes provisionals

`tools/room_designs.py` té un disseny per a cada sala de l'Acte 1: el fons en pixel art (fàbrica de
maons i coure al passat, presó orbital de metall al present) i, alhora, **la geometria per a Benne**:
on és cada cosa clicable, on hi camina la protagonista i on hi ha cada personatge. El sync la
dibuixa i ajusta el `.room.json` perquè el que es veu i el que es clica coincideixin.

Només mentre la sala sigui provisional (marca `.provisional`): quan hi hagi art de debò i polígons
retocats a l'editor de Benne, s'esborra la marca i el sync ja no hi toca res més que els textos.
Les sales noves sense disseny surten amb caixes etiquetades fins que se'ls en faci un.

## Personatges provisionals

`tools/draw_characters.py` dibuixa en pixel art els sprites de l'Iri, la Vet, el Cargol, el capatàs,
en Bruc i la MARE (a `placeholder-art/`), amb les animacions que demana Benne. El sync els copia al
projecte i els actualitza mentre hi hagi la marca `.provisional` a `assets/images/characters/<id>/`.
L'aspecte segons l'estat (`appearance` a `characters.json`) l'aplica el pont en entrar a la sala i
cada vegada que canvia l'estat.

## Fonts

Les fonts de mapa de bits de la plantilla no tenien la majoria de caràcters catalans (à, è, ò, ç,
l·l...). `tools/extend_font.py` els afegeix compostos amb els píxels de la mateixa font (ja aplicat a
`ferro-9`). Si s'afegeix una font nova: `python3 adapters/benne/tools/extend_font.py <font.xml>`.

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

## Què està comprovat i què no

Comprovat sense executar el joc:
- el pont, els diàlegs, el menú i el `globalScript.ts` passen `tsc` amb la configuració estricta del
  projecte Benne i amb els noms reals que genera Benne (`generate-game-ids`);
- el contingut generat passa el validador de contingut de Benne (`scripts/lib/validate-game-content.mjs`).

Pendent de confirmar a la primera partida al navegador:
- que `game.onEnterAnyRoom` es dispara també a la primera sala (hi depèn l'inventari inicial);
- que `fallbacks.onUnhandled` rep els verbs sense cap gestor (i que no hi ha una frase per defecte
  de Benne abans de la nostra);
- que un personatge invisible (la MARE, que parla per l'altaveu) pot parlar;
- l'aspecte: posicions de les caixes, mida dels textos, botó «Empeny» (3 px més ample que el botó).
