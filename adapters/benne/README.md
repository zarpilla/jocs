# Adaptador per a Benne

Tot el codi que depèn de Benne és aquí, i és **comú a tots els jocs**. Si canviem de motor, aquesta
carpeta (i el projecte Benne de cada joc) és l'única que cal substituir: `game/` i
`packages/narrative-core/` no canvien.

Les ordres s'executen per a un joc: des de `games/<joc>/` (`npm run benne:sync`) o des de l'arrel amb
`-w <joc>` (`npm run benne:sync -w suma-zero`). Vegeu `tools/joc.ts`.

Un esquema visual de tot plegat (capes, sync, un clic de punta a punta, i les possibilitats visuals del motor):
[docs/benne-per-dins.html](../../docs/benne-per-dins.html).

## Què hi ha

| Fitxer | Què fa |
|---|---|
| `runtime/narrative.ts` | Crea el `Narrative` i hi instal·la la lògica del joc (`game/logic`). Li explica el món de Benne: inventari de cada protagonista, sales, qui juga. Desa l'estat dins les partides de Benne i executa `giveItem`/`takeItem`. Mostra i amaga coses condicionals, i posa els noms traduïts. |
| `runtime/narrative.script.ts` | Funcions de BenneScript que fan coses al llarg del temps: dir línies, resoldre interaccions del JSON, conduir els diàlegs, canviar de protagonista, dir una pista, mostrar un final. |
| `templates/globalScript.ts` | El `globalScript.ts` del projecte Benne. Envia totes les interaccions sense gestor propi i l'entrada a cada sala al JSON. |
| `runtime/historial.ts` | Historial de línies buit, per als jocs que no en tenen. |
| `runtime/estadistiques.ts` | Estadístiques anònimes de tots els jocs (vegeu [Estadístiques](#estadístiques)). |
| `sync.ts` | Valida el contingut i el porta al projecte Benne. |
| `benne-content.ts` | Sales, personatges, objectes, configuració i GUI de Benne a partir del JSON (el fa servir el sync). |
| `create-project.ts` | Crea el projecte Benne d'un joc nou; amb `--motor`, actualitza el motor compartit. |
| `joc-benne.ts` | Què pot configurar cada joc (vegeu més avall). |
| `patches/` | Canvis propis al motor de Benne, per quan s'actualitzi des d'un Benne nou. Els refà `refes-pegat.ts` (`npm run benne:pegat`). |
| `motor-paths.ts` | Quins fitxers del checkout de Benne són el motor, i de quina versió surt el nostre. |

### El que és de cada joc: `games/<joc>/adapters/benne/`

| Fitxer | Què fa |
|---|---|
| `joc.ts` | Nom, carpeta del projecte Benne, fonts, colors de les veus, retocs a `game-config.json`, GUI pròpies (botons del menú, historial), la interfície tàctil (`tactil`) i, als jocs on no es pot canviar de protagonista, el botó «Canvia» del HUD convertit en el de la pista (`botoPista: true`), o només quan no es pot canviar (`botoPista: 'mixt'`, amb la lupa com a control `caraPista` del HUD: La Conjura de l'Avet). Tipus: `JocBenne` a `joc-benne.ts`. |
| `runtime/` | Fitxers del pont propis del joc. Es copien damunt dels comuns: p. ex. `historial.ts`, que cada joc fa a la seva manera. |
| `mapping.json` | Identificadors que no coincideixen entre el nostre JSON i Benne (`characters`, `items`, `rooms`, `hotspots`), la música (`music`: sala o protagonista → pista), el so de fons en bucle de cada sala (`ambient`: sala → so, o una llista de casos `{ "if": condició, "sound": so, "volume": 0–1 }`; sona sota la música, no el tallen ni els canvis de sala ni els diàlegs, i es fon d'un a l'altre) la foscor de les sales (`fosc`: una llista de casos `{ "rooms": [sales], "if": condició, "alpha": 0–1, "color": "#rrggbb" }`; en entrar a la sala es posa de cop, i si canvia l'estat dins la sala es fon) i el so de cada sortida (`doors`: `"sala.cosa": so`, sona en arribar a la sala nova). |
| `placeholder-art/` | Sprites provisionals dels personatges. |
| `tools/` | Les eines d'art del joc (Python): sales, personatges, objectes, GUI. |

## El projecte Benne de cada joc

`games/<joc>/<joc>/` (p. ex. `games/suma-zero/suma-zero/`). Per jugar:

```bash
cd games/suma-zero/suma-zero
npm install      # la primera vegada (cal haver fet també `npm install` a l'arrel)
npm run dev      # obre el joc al navegador
```

El motor (`src/engine`, `src/editor`, `scripts/`, `electron/`, les configuracions de Vite...) és el de
`packages/benne`, compartit. Cada projecte en té una **còpia de només lectura**, que `npm run motor` fa
sola abans de `dev` i `build`, i que no va a git. El motor s'edita a `packages/benne/`.

Com es crea un joc nou (o s'actualitza el motor des d'un Benne nou):

```bash
git clone https://github.com/Bennethon/benne /algun/lloc/benne
npm run benne:create -w <joc> -- --from /algun/lloc/benne            # projecte Benne nou
npm run benne:create -w <joc> -- --from /algun/lloc/benne --motor    # actualitza packages/benne
npm run benne:sync -w <joc> -- --init
```

`benne:create` fa el mateix que l'ordre *BENNE: Create New Game* de l'extensió (copia la plantilla
9-verb, sense la demo), però sense VS Code ni executar codi de Benne. Si prefereixes fer servir
l'extensió de VS Code per editar sales, obre la carpeta del projecte Benne: és un projecte Benne normal.

## Què genera el sync

- `src/game/narrative/`: el pont (el comú i el del joc), `content.generated.json` (dades i textos) i
  `mapping.generated.json`.
- `src/game/dialogs/<id>/`: un diàleg de Benne per cada diàleg nostre. Totes les opcions
  de tots els nodes es converteixen en opcions de Benne (`<node>__<opció>`), i el pont encén
  només les que toquen a cada moment.
- `src/game/globalScript.ts`: el bloc entre les marques es regenera sempre; el que hi
  afegeixis a sota es conserva. (La primera vegada, `--init`.)
- **Sales, personatges i objectes que encara no existeixen a Benne**, amb una disposició automàtica i
  **art provisional** (caixes etiquetades; cal `python3` amb Pillow). El que ja existeix no es toca:
  quan un artista substitueixi un PNG, ha d'esborrar el fitxer `.provisional` del costat.
- **Coses noves en sales que ja existeixen** (una porta, un objecte, un decorat): s'hi afegeixen amb
  la disposició automàtica, sense tocar la resta. Si la sala té disseny propi (`tools/room_designs.py`),
  l'art provisional les col·loca on diu el disseny.
- **Tots els textos de Benne en l'idioma triat**: verbs (`ui.verb.*`), menús (`ui.menu.*`...), noms
  de coses, personatges i objectes.
- El botó **Canvia** a la barra de verbs, la portada, i les GUI pròpies del joc (`guis` al seu `joc.ts`).

Tot porta la marca `GENERAT`: no s'edita a mà. El sync es nega a sobreescriure fitxers sense la marca.

## Com funciona una interacció

1. A Benne, el jugador fa «Usa clau anglesa amb palanca».
2. Cap script de sala no la gestiona, i arriba a `fallbacks.onUseItem`, al `globalScript.ts`.
3. `routeInteraction` la tradueix (`fabrica_cambra-hotspot-palanca` → `palanca`) i la passa al nucli.
4. El nucli busca la interacció a `game/data/rooms/fabrica_cambra.json` i aplica els efectes. Retorna
   les línies, el diàleg, la sala o el canvi de protagonista.
5. `playResult` ho fa a Benne: `player.say`, `dialogs.x.start()`, `player.switchTo`, `rooms.x.goTo()`.

Els scripts de sala de Benne només calen per a coses visuals (animacions, moviments, càmera). Les
coses amb `visibleIf` es generen com a **props** i el pont les mostra o amaga soles. Si una cosa ja era una
zona (hotspot) a Benne abans de tenir `visibleIf`, el sync ho apunta i el pont l'activa o la desactiva. Els **decorats**
(`decor` a la sala) també són props, però amb `clickable: false`; el sync els afegeix també a les sales
que ja existeixen.

## Dues protagonistes en una sola Benne

A Benne, `player.switchTo` només funciona amb personatges de la mateixa sala. Per això **cada sala és d'una protagonista** (`"protagonist"` al JSON de la sala):
canviar de protagonista vol dir anar a la sala on és l'altra, i en entrar-hi el pont en pren el
control. L'última sala de cada protagonista es desa amb la partida.

Les **sales compartides** (`"protagonists": ["iri", "vet"]`) tenen totes dues protagonistes: hi entra qui juga (o,
en canviar de protagonista, l'altra), i la que no juga només es veu si també hi és. Si les dues són a la mateixa sala,
canviar de protagonista no surt de la sala.

**Provar una situació** (només amb `npm run dev`): `window.__aventura.provar({ state, rooms, items, active })` posa la
partida en l'estat que deixa un test de partida a mig jugar i hi va. Serveix per fer captures de cada escena.

## Escenes provisionals

`tools/room_designs.py` (a l'adaptador de cada joc) pot tenir un disseny per a cada sala: el fons en pixel art (o, si és
definitiu, `tools/hd/rooms/<sala>.py`) i, alhora, **la geometria per a Benne**:
on és cada cosa clicable, on hi camina la protagonista i on hi ha cada personatge. El sync la
dibuixa i ajusta el `.room.json` perquè el que es veu i el que es clica coincideixin.

Només mentre la sala sigui provisional (marca `.provisional`): quan hi hagi art de debò i polígons
retocats a l'editor de Benne, s'esborra la marca i el sync ja no hi toca res més que els textos.
Les sales noves sense disseny surten amb caixes etiquetades fins que se'ls en faci un.

## Personatges provisionals

`tools/draw_characters.py` dibuixa en pixel art els sprites dels personatges que hi estiguin definits (a
`placeholder-art/`; mentre no n'hi hagi, el sync fa servir els de la plantilla de Benne), amb les animacions que demana Benne. El sync els copia al
projecte i els actualitza mentre hi hagi la marca `.provisional` a `assets/images/characters/<id>/`.
L'aspecte segons l'estat (`appearance` a `characters.json`) l'aplica el pont en entrar a la sala i
cada vegada que canvia l'estat.

Els objectes d'inventari tenen icona a `tools/draw_items.py`; els que no en tenen surten com una
caixa amb el nom.

## Resolució

El joc és a **480×270**, des del primer dia. Tot l'art (personatges, objectes i sales) es dissenya
en píxels del joc (`tools/escala.py` de cada joc). La disposició automàtica de les sales noves
(`benne-content.ts`) conserva les mides de 352×198 de Ferro-9 escalades amb `s()`.
Les fonts no s'escalen: són de mapa de bits i només es veuen nítides a múltiples enters.

## Fonts

Cada joc té la seva font pròpia (`fonts` al seu `joc.ts`, `npm run font`), amb tots els caràcters
catalans. Cap font amb llicència no comercial. Si mai cal una font de la plantilla:
`python3 games/<joc>/adapters/benne/tools/extend_font.py <font.xml>` hi afegeix les lletres catalanes.

## Canvis propis al motor de Benne

El motor compartit (`packages/benne`) té canvis propis: `stayBlackOnEnter()` per mostrar títols sobre
negre abans d'una sala, el text de pantalla per sobre del fos a negre, `walkToLabel` a
`game-config.json` per traduir «Walk to», `setOutfit()` per canviar la roba d'un personatge (prova les
etiquetes `<roba>IdleD`, `<roba>WalkL`... abans que les normals), `speech.clickProtectMs` (un clic als
primers mil·lisegons d'una línia no la salta), `pauseGame` a les GUI (el joc s'atura mentre és oberta)
i les partides desades amb una clau per joc. Vegeu `packages/benne/README.md`.

`patches/motor-benne.patch` els recull tots, respecte del Benne d'on surt el motor (`BENNE_BASE` a
`motor-paths.ts`): `benne:create --motor` l'aplica. Cada cop que es toca el motor, cal refer-lo amb
`npm run benne:pegat`.

Per a la GUI: `switchProtagonist()` (botó de canviar entre l'Iri i la Vet), `sayHint()` (botó de
pista) i `playEnding()`.

L'**historial** (botó del menú o tecla H) és de cada joc: el `runtime/historial.ts` del joc apunta
cada línia que es diu (`recordLine`) i la GUI `historial` (que crea el seu `joc.ts`) l'ensenya.

Una interfície pròpia es pot quedar alguns clics abans que vagin al JSON: `setTouchRouter({ takes, route })` (a
`runtime/narrative.ts`, i es crida des del `globalScript.ts`). `route` fa la interacció del JSON amb
`performInteraction`. Sense encaminador, tot va com sempre.

### La interfície tàctil (`tactil/`)

Sense barra de verbs, pensada per al mòbil: tocar una cosa la mira la primera vegada i després en fa l'acció (o
obre el menú d'accions si en té més d'una), mantenir premut obre el menú; amb el ratolí, per defecte el clic esquerre
mira i el dret fa l'acció sense mirar primer (a les sortides, l'esquerre també hi va; cada pulsació diu si és un dit o
un ratolí: `pointerType`; a les opcions i a la targeta es pot girar, una preferència de cada joc i aparell:
`tactil/runtime/preferencies.ts`), una targeta «Com es juga» ho explica (surt sola a cada partida nova, quan s'acaba l'entrada i ja es pot jugar, i des de les opcions: «Controls»), i l'alçada de la pantalla s'adapta a
l'aparell. Un joc la fa servir amb `tactil: true` al seu `joc.ts` (Aigua Verne, Suma Zero, Ni un ou), i llavors el
`benne:sync` hi posa el runtime (`tactil/runtime/`), els scripts del HUD i del menú (`tactil/guis/`), l'encaminador al
`globalScript.ts`, la configuració (`configuraTactil`) i, als objectes que el contingut no combina mai amb res
(`objecteSol`), `defaultVerb: "fes"`: tocar-los a l'inventari en fa l'acció en lloc de prendre'ls a la mà (el motor ho
fa quan el verb del botó principal és d'objecte i l'objecte té `defaultVerb`). El joc hi posa l'art i els `.gui.json` (el seu
`tools/hd640/hud.py`, amb els ids i les mides que esperen els scripts), la pantalla adaptable de sales i GUI
(`tools/hd640/pantalla.py`) i els textos `ui.accio.*`. Per als tests, `tactil/mesura.ts` diu com es juga un camí
sencer amb el toc. Detalls: [tactil/index.ts](tactil/index.ts).

Els esdeveniments del nucli arriben com a esdeveniments de Benne `narrative:<tipus>` (per exemple,
`events.on('narrative:questStarted', …)`).

## Estadístiques

`runtime/estadistiques.ts` envia comptadors anònims a `https://malaherbasoft.cat/api/e` (el servei és
al repo de la web, `api/`). Tots els jocs ho fan sols, sense res al seu `joc.ts`:

| Què | D'on surt |
|---|---|
| `nova` | `startFromCover()` (botó «Comença») |
| `continua` | `onRoomLoaded()`: s'ha carregat una partida desada (un cop per pàgina) |
| `acte` 2, 3… | el nucli emet `questStarted` d'una missió `acteN` (l'1 no: ja és `nova`) |
| `final` + id | `playEnding()` |
| `temps` (segons) | en amagar o tancar la pestanya; només compta amb la pestanya visible i alguna acció en els darrers 2 minuts |

El joc s'identifica amb el nom de la seva carpeta (`games/<joc>`), que el sync posa a
`mapping.generated.json` (`id`).

- **No es desa res al dispositiu** (ni galetes ni localStorage) ni s'envia cap identificador. La web
  promet «sense galetes»: no hi afegiu res que ho trenqui.
- **No s'envia res** en desenvolupament (`npm run dev`), des de localhost ni si el navegador té Global
  Privacy Control o Do Not Track.
- **Un joc nou:** perquè se'n comptin els actes, les missions principals s'han de dir `acte1`, `acte2`,
  `acte3`… I el servidor l'ha de tenir a la llista `JOCS` (`api/compose.yaml` del repo de la web), o
  rebutjarà els seus esdeveniments.
- **Un esdeveniment nou:** cal afegir-lo a `estadistiques.ts` i a la validació del servidor
  (`valida()` a `api/servidor.mjs`). Mantingueu-los pocs i agregats.

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
- que un personatge invisible (una veu per l'altaveu) pot parlar;
- l'aspecte: posicions de les caixes, mida dels textos, botó «Empeny» (3 px més ample que el botó).
