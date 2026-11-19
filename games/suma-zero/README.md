# Suma Zero

Aventura gràfica de «point & click» feta amb [Benne](https://benne.games/): comèdia caòtica amb
cor polític. Dues germanes de fet, l'**Iri** (hacker) i la **Vet** (cambrera i mentidera
professional), volen entrar a la seu del Banc Central Mundial Unificat i repartir tots els diners del
món a parts iguals. Funciona massa bé.

Guió: [guio/guio.md](guio/guio.md) (primera versió, a partir de [primer-guio.txt](primer-guio.txt)).

La base tècnica (nucli narratiu, adaptador de Benne, eines) ve de Ferro-9
(`../ferro-9`), amb la història separada del motor.

> **Aquest joc és dins del repositori dels jocs de Mala Herba Soft** (`games/suma-zero/`). El nucli narratiu
> (`packages/narrative-core/`), l'adaptador de Benne (`adapters/benne/`), el motor de Benne
> (`packages/benne/`) i les eines (`tools/`) són a l'arrel i **els comparteixen tots els jocs**. Aquí hi
> ha el que és només d'aquest joc: el contingut (`game/`), el guió, l'art, la música i el projecte Benne
> (`suma-zero/`). Les ordres d'aquí sota s'executen des d'aquesta carpeta, o des de l'arrel amb `-w suma-zero`
> (`npm run validate -w suma-zero`). Vegeu el [README de l'arrel](../../README.md).

## Sense barra de verbs

Es juga sense barra de verbs, també amb el dit en un mòbil apaïsat (el camí **B · Modernitzar** de
[docs/aventures-cap-on-anem.html](../../docs/aventures-cap-on-anem.html)), amb la interfície tàctil compartida.

### Com es juga

| Gest | Què fa |
|---|---|
| Tocar una cosa (amb el dit) | La primera vegada, mirar-la. Després: si té una sola acció, la fa; si en té més d'una (la nevera: obrir o tancar; la impressora: empènyer o agafar), obre el menú i tries tu. Les sortides no es miren: s'hi va |
| Amb el ratolí: clic esquerre, clic dret | Per defecte, el clic esquerre mira (a les sortides, hi va) i el dret fa el mateix que el toc, però sense mirar primer (l'acció, o el menú si n'hi ha més d'una) |
| Mantenir premut (el dit o el botó esquerre) | El menú d'accions: «Mira» i les accions que té ara mateix |
| «Com es juga» | A Opcions → Controls, una targeta que ho explica, amb el dit o amb el ratolí segons l'aparell (amb el ratolí, s'hi pot triar què fa cada botó). No surt sola en començar |
| Opcions → «clic esquerre per fer» | Gira els botons del ratolí: l'esquerre fa i el dret mira. Es desa en aquell aparell |
| Tocar el terra | Caminar |
| Carpeta (a baix a la dreta) | Desplega la safata de l'inventari |
| Tocar un objecte de la safata | El pren a la mà («Usa X amb...»); tocar una cosa l'hi fa servir, o li dona si és un personatge |
| Escàner (a baix a l'esquerra) | Marca un moment tot el que es pot tocar |
| «Canvia» (a dalt a l'esquerra), el menú (a dalt a la dreta) | Canviar de protagonista; desar, carregar, opcions, pista, historial |

En una finestra d'ordinador o un monitor (si sota l'escena queden 56 px o més), la franja de sota és la consola amb
tot el HUD i l'inventari sempre a la vista, com a Aigua Verne.

### Què ha calgut

- **`tactil: true`** al joc.ts: el `benne:sync` hi posa el runtime, els scripts del HUD i del menú d'accions, els dos
  verbs de la interfície i l'alçada adaptable (de 640×288 a 640×360).
- **L'art del HUD i del menú**, amb l'estil de la barra (la consola d'hacker: plàstic blau marí, tecles fosques,
  pantalletes amb cantoneres de visor, la línia de llum i l'accent magenta):
  [tools/hd640/hud.py](adapters/benne/tools/hd640/hud.py). Mateixos ids i mides que el d'Aigua Verne. El botó
  «Canvia» és el de la barra (mitja Iri i mitja Vet).
- **La pantalla adaptable**: [tools/hd640/pantalla.py](adapters/benne/tools/hd640/pantalla.py), com el d'Aigua Verne.
  Aquí gairebé totes les sales són pintades fins a baix, però el joc (el que es pot tocar i el terra) va de y = 20 a
  271: al mòbil la càmera es queda a dalt.
- L'historial (`runtime/historial.ts`, i la GUI a joc.ts), a l'alçada mínima; els textos `ui.accio.*`,
  `ui.verb.toca` i `ui.verb.accions` (game/locales/ca/interficie.json).

### Resultat

`game/test/tactil.test.ts` juga el joc sencer per dos camins amb el mesurador compartit (`TACTIL=1 npm test` en fa
la llista). Cap pas és impossible.

| Camí | Passos | Un toc | Toc + menú | Toc de més (mira primer) | Gestos per pas (dit) | Gestos per pas (ratolí) |
|---|---|---|---|---|---|---|
| Sense aliats | 66 | 61 | 5 | 25 | 1,45 | 1,08 |
| Amb tots els aliats | 67 | 62 | 5 | 26 | 1,46 | 1,07 |

Amb el ratolí no hi ha tocs de més per mirar: mirar és un clic (l'esquerre, per defecte), i fer, l'altre (mesurat amb els botons girats: el resultat és el mateix).

El menú surt al passaplats, la nevera, la capsa i la impressora: on hi ha més d'una cosa a fer. (Els tocs de més
per mirar inclouen les coses que tenen una descripció nova: vegeu [Aigua Verne](../aigua-verne/README.md#resultat-de-la-prova).)

### Ordres de la interfície tàctil

```bash
npm test                                           # (des de l'arrel) inclou tactil.test.ts
npm run benne:sync                                 # el contingut i la interfície tàctil al projecte Benne
python3 adapters/benne/tools/hd640/hud.py          # torna a fer el HUD i el menú d'accions
python3 adapters/benne/tools/hd640/pantalla.py     # càmeres de les sales i GUI per a la pantalla adaptable (es pot repetir)
cd suma-zero && npm run dev -- --host              # al navegador, i des del mòbil a la mateixa xarxa
```

Compte: `hd640/gui_rest.py` torna a fer la barra de verbs; no s'ha d'executar (o cal tornar a passar
`hud.py` i `pantalla.py` després).

## Les tres capes

```
┌──────────────────────────────────────────────────────────────────────┐
│ game/                 EL JOC                                         │
│   data/               sales, personatges, objectes, diàlegs,         │
│                       missions, pistes, finals (JSON)                │
│   locales/ca/         textos en català (un fitxer per tema)          │
│   logic/              regles pròpies del joc, TS                     │
│                       pur, sense cap motor                           │
│   schemas/            JSON Schema (autocompletat i errors a VS Code) │
└──────────────────────────────────────────────────────────────────────┘
                 │ llegeix
┌──────────────────────────────────────────────────────────────────────┐
│ packages/narrative-core/   MOTOR NARRATIU (TypeScript pur)           │
│   estat · condicions · efectes · sales i interaccions · diàlegs      │
│   memòria · missions · pistes · finals · traduccions · protagonistes │
│   HeadlessPlayer: el joc sense gràfics (tests i mode text)           │
│   No sap res de Benne, ni de pantalles, ni d'inventaris.             │
└──────────────────────────────────────────────────────────────────────┘
                 │ WorldPort (preguntes)  ▲ NarrativeEvent (ordres)
┌──────────────────────────────────────────────────────────────────────┐
│ adapters/benne/        L'ÚNICA PEÇA QUE CONEIX BENNE                 │
│   runtime/             pont que es copia al projecte Benne           │
│   templates/           globalScript.ts: clics de Benne → JSON        │
│   sync.ts              genera els diàlegs de Benne des dels nostres  │
└──────────────────────────────────────────────────────────────────────┘
                 │ npm run benne:sync
┌──────────────────────────────────────────────────────────────────────┐
│ suma-zero/ projecte Benne: motor, art, i el que genera el sync     │
│              cd suma-zero && npm install && npm run dev              │
└──────────────────────────────────────────────────────────────────────┘
```

Regles:

- **Cap text visible dins el codi ni dins les estructures.** Les estructures fan servir claus
  (`"dlg.pescador.hola"`) i els textos són a `game/locales/<idioma>/`. Afegir un idioma = afegir una
  carpeta i posar-lo a `game/data/game.json`.
- **El nucli no toca el món.** Pregunta al motor (`hasItem`, `hasVisited`, `currentRoom`) i li demana
  coses amb esdeveniments (`giveItem`, `questStarted`, `ending`...).
- **Benne és el responsable** de les sales, l'art, els moviments i l'inventari. La lògica de la
  història (qui recorda què, què es pot dir, quines missions hi ha) és al nostre JSON.

## Decisions de base

| Decisió | Valor |
|---|---|
| Resolució | **640×360**, fixa (fins a l'11/2026, 480×270). L'art es dissenya directament en píxels del joc (escala 1) |
| Direcció d'art | Pixel art **caricaturesc**, estil LucasArts clàssic: personatges cabuts i exagerats, colors vius |
| Protagonistes | Dues, l'Iri i la Vet, amb canvi lliure entre elles (excepte a les escenes de sincronització) |
| Sincronització | **Per torns**: sense pantalla dividida ni rellotge real. Cada acció avança un comptador; si s'acaba, es repeteix el pas |
| Idiomes | Només català (el sistema de claus permet afegir-ne més endavant) |
| To | Comèdia per a adolescents i adults, crítica amb el sistema però mai panfletària. Cap atzucac ni derrota |
| Títol | **Suma Zero**; projecte Benne `suma-zero` |
| Font | Pròpia (`suma-regular`, `suma-negreta`), mai fonts amb llicència no comercial |

## Art

Fixat amb la **sala de mostra** (`pis_estudi`, l'estudi de l'Iri), que fa de guia d'estil. Es van comparar
dues propostes ([guio/art/comparacio.png](guio/art/comparacio.png)); s'ha triat la **B: urbana, sense
caricatura**, amb la calidesa lila de la A. Captura al joc: [guio/art/sala-mostra-joc.png](guio/art/sala-mostra-joc.png).

| Què | Mida i regla |
|---|---|
| Pantalla | De 640×288 (un mòbil) a 640×360 (un monitor), segons l'aparell; a sota de l'escena (y≈260), el HUD tàctil |
| Personatges | ≈110 px, fotograma de 65×116, peus a (34, 111) (les de Ferro-9 ×4/3). Direccions L, D, U (Benne fa el mirall de R). Dibuix amb volum, llum i trama (`hd/characters.py`, a ×4/3 amb `hd640/draw_characters.py`) |
| Mobles | Escala real: un escriptori arriba al maluc (≈61 px de terra a taulell) |
| Icones | La casella de l'inventari: 65×36, amb el mateix dibuix de volum (`hd640/items.py`) |
| Fons | `hd/pix.py`: rampes de color amb trama ordenada i llums de sala; contorns només on cal |
| To | Urbà, de hacker i d'espies: colors apagats, llum de pantalles (cian) i de neó (magenta). Un accent fort per personatge (l'Iri: dessuadora verd petroli amb «</>» i auriculars vermells) |

On és cada cosa (a `adapters/benne/tools/`). L'art del joc és el de `hd640/` (640×360); el de `hd/` és l'original
a 480×270, del qual surt (`escala.RESOLUCIO` tria quin fan servir les eines; `hd640/aplica.py` va passar el
projecte Benne a 640, i `python3 hd640/preview.py --res 640|480 <sala> <sortida>` els compara):

- `hd/personatges.py`: l'Iri, la Vet (amb la roba de cada escena), en Diu i els secundaris;
  `draw_characters.py` en genera els fulls (el sync els copia).
- `hd/rooms/<sala>.py`: el dibuix de cada sala; `hd/rooms/comu.py`: eines i rampes comunes;
  `room_designs.py`: la geometria (on es clica, on es camina).
- `hd/items.py`: les icones de l'inventari; `hd/gui.py`: la interfície (la barra de verbs original, opcions de diàleg i
  menús), una consola d'hacker on els verbs i els botons són tecles. El HUD tàctil d'ara el fa `hd640/hud.py`.
- `python3 hd/render.py <sala> <carpeta>`: previsualitzacions ampliades, amb una de depuració (zones, terra
  i personatges a escala).
- `hd/caricatura/`: la proposta A (caricatura, 64 px i cap gran), guardada per a un joc per a públic infantil.
  No la fa servir el sync.

Cada acte comença amb art provisional (caixes amb la geometria definitiva) i passa a l'art definitiu sala
per sala quan el guió de l'acte està tancat i jugat. L'Acte 1 ja és tot definitiu.

## Ordres

```bash
npm install            # a l'arrel del repositori, la primera vegada
npm run jugar          # juga en mode text, al terminal (sense art ni Benne), amb [so: nom] abans de cada so
npm test               # tests: el nucli i les partides jugades de cap a peus
npm run validate       # comprova el contingut: forma, referències, textos que falten
npm run fitxes         # genera guio/fitxes-sales.md: què cal crear a l'editor per a cada sala
npm run revisio        # genera guio/revisio.md: totes les variants de text amb la seva condició [-- <sala>]
npm run typecheck      # tipus de tot el repositori (tots els jocs)
npm run schemas        # regenera game/schemas/ si canvien els tipus del nucli
npm run font           # regenera la font pròpia (suma-regular i suma-negreta) al projecte Benne
npm run sons           # regenera els efectes de so sintetitzats (game/audio/sfx/; cal numpy i ffmpeg)
npm run musica         # regenera la música (game/audio/music/)
npm run benne:sync     # porta el contingut a suma-zero/ (sales noves, textos, diàlegs, sons...) [--watch]
npm run benne:create -- --from <checkout de Benne>   # crea suma-zero/ (amb --motor, actualitza el motor compartit)
```

## Documentació

- [docs/guia-contingut.md](../../docs/guia-contingut.md): com escriure diàlegs, missions, pistes, finals...
- [adapters/benne/README.md](../../adapters/benne/README.md): com connectar-ho amb el projecte Benne.

## Estat actual

- **Guió** complet i revisat ([guio/guio.md](guio/guio.md)), amb la primera revisió de coherència aplicada.
- **Acte 1 jugable de cap a peus** (en mode text, als tests i a Benne): pròleg, el pis (els tres cables,
  en Diu i el passaplats), el bar (les tres coses per a en Marcel, el pany intel·ligent, la trucada de la «dona»
  d'en Tomàs) i l'aeroport (la primera sincronia per torns, amb la cigarreta de l'Ortega).
- **Acte 2 jugable de cap a peus** (en mode text, als tests i a Benne, amb l'art definitiu): el vestíbul (el Director i la sospita, amb el
  Dia de la Marmota), el moll (la Rius i la targeta), el tercer pis (NETA-3 i les càmeres) i la sincronia del
  collaret (els bips del Llibre Major i en Ballester).
- **Acte 3 jugable de cap a peus** (en mode text, als tests i a Benne): el muntatge del virus,
  la planta noble (la senyora Pons i el Director, la contrasenya i la sincronia del mòbil, amb la regla del
  Director que mira el mòbil), la decisió de l'Iri (tornar els diners al banc o repartir-los tots a parts iguals; i el compte zero, que continua ple i amb contrasenya) i la sortida (l'escala
  plena, el conducte amb NETA-3 o l'extintor, la recepcionista i el contenidor). Tres finals segons els aliats.
- **Regles en codi:** la sincronia (`game/logic/sincronia.ts`: per torns a l'aeroport, per sospita al collaret),
  el tub pneumàtic (`tub.ts`) i la sospita del Director (`sospita.ts`), sobre dues novetats del nucli:
  `onAfterAction` (una regla després de cada acció) i l'esdeveniment `situar` (moure l'altra protagonista).
- **Tests:** l'Acte 3 per tots els camins (els tres finals; el mòbil resolt per la Vet, la Pons o en Ballester; els
  reinicis del Director; sense la placa del retrat; la recepcionista; el contenidor abans d'hora), l'Acte 2 per tots els camins (amb els tres aliats o cap, els tres entrepans per al robot, l'Iri
  primer, el Dia de la Marmota, els reinicis del collaret, la veritat i la mentida a en Ballester) i l'Acte 1 per tots els camins (els tres sacrificis per a en Diu, amb i sense entrepà, tap i
  preparació, el codi dolent, els reinicis de la sincronia), amb una pista a cada pas, i proves de coherència.
- **Art de l'Acte 1, definitiu:** totes les sales (el pis, el bar, l'aeroport) i les cinemàtiques (la portada,
  el pròleg a Ginebra, l'avió), amb un fotograma per a cada estat; l'Iri, la Vet (cinc conjunts i les ulleres),
  en Diu i els secundaris; les icones de tots els objectes; i la interfície pròpia (la consola d'hacker: verbs,
  menús, desa, carrega i opcions). Font de píxels pròpia, amb accents.
- **So:** efectes sintetitzats (`npm run sons`) i música d'ambient per lloc (`npm run musica`): el tema de la
  portada, el pis, el bar, l'aeroport, el banc i el rellotge de l'Acte 3, el mateix tema amb instruments diferents que s'encadena al mateix punt
  en canviar de sala.
- **Per jugar:** `cd suma-zero && npm run dev` (al menú del joc, botons «Pista» i «Historial»; la tecla H també obre l'historial).
- **Per veure els finals sense jugar** (només amb `npm run dev`): obre el joc amb `?final=<id>` a l'adreça i prem
  «Comença». La condició del final es compleix sola; amb `flags=` (i `vars=`) s'hi afegeix la resta de l'estat:
  - `?final=final_base` (sense aliats; l'Iri ho torna al banc)
  - `?final=final_hores&flags=aliat_ballester,aliada_rius` (dos aliats; afegeix `repartit` perquè ho hagi repartit)
  - `?final=final_taula&flags=aliat_ballester,aliat_neta,aliada_rius,aliada_pons,tap_tornat,mentida_corporativa`
    (tothom a la taula; `tap_tornat` i `mentida_corporativa` o `dignitat` canvien les línies d'en Tomàs i en Marcel)
- **Art de l'Acte 2, definitiu:** les cinc sales del BCMU (`hd/rooms/bcmu_*.py`, amb la paleta i l'estació del tub
  comunes a `hd/rooms/bcmu.py`), el Director, la Rius, en Ballester i NETA-3 amb les seves animacions d'estat, i les
  icones dels objectes nous. Els sons de l'Acte 2 són sintetitzats, i la música del banc (`banc`) sona a les cinc sales.
- **Art de l'Acte 3, definitiu:** l'avantdespatx (els cavalls, la porta del Director) i el despatx (el llac i el Jet
  d'Eau, el sofà, el bol de plata), el carrer del darrere amb el contenidor i el conducte, el muntatge del virus (sis
  pantalles i el rellotge de les 11:15), el bar del final (la tele, la taula llarga) i els postcrèdits (el pis de nit,
  «ROBIN HOOD 3.0?»); la senyora Pons i la recepcionista.
- **Següent pas:** jugar el joc sencer a Benne i recollir-ne les impressions.
