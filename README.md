# Suma Zero

Aventura gràfica de «point & click» feta amb [Benne](https://benne.games/): comèdia caòtica amb
cor polític. Dues germanes de fet, l'**Iri** (hacker) i la **Vet** (cambrera i mentidera
professional), volen entrar a la seu del Banc Central Mundial Unificat i repartir tots els diners del
món a parts iguals. Funciona massa bé.

Guió: [guio/guio.md](guio/guio.md) (primera versió, a partir de [primer-guio.txt](primer-guio.txt)).

La base tècnica (nucli narratiu, adaptador de Benne, eines) ve de Ferro-9
(`../ferro-9`), amb la història separada del motor.

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
| Resolució | **480×270**, fixa. L'art es dissenya directament en píxels del joc (escala 1) |
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
| Pantalla | 480×270; la sala es veu fins a y≈205 (a sota hi ha la barra de verbs) |
| Personatges | Proporcions de Ferro-9: ≈83 px, fotograma de 49×87, peus a (25, 83). Direccions L, D, U (Benne fa el mirall de R). Dibuix amb volum, llum i trama (`hd/characters.py`) |
| Mobles | Escala real: un escriptori arriba al maluc (≈46 px de terra a taulell) |
| Icones | La casella de l'inventari: 49×27, amb el mateix dibuix de volum (`hd/items.py`) |
| Fons | `hd/pix.py`: rampes de color amb trama ordenada i llums de sala; contorns només on cal |
| To | Urbà, de hacker i d'espies: colors apagats, llum de pantalles (cian) i de neó (magenta). Un accent fort per personatge (l'Iri: dessuadora verd petroli amb «</>» i auriculars vermells) |

On és cada cosa (a `adapters/benne/tools/`):

- `hd/personatges.py`: l'Iri i en Diu; `draw_characters.py` en genera els fulls (el sync els copia).
- `hd/rooms/pis_estudi.py`: el dibuix de la sala; `hd/rooms/comu.py`: eines i rampes comunes;
  `room_designs.py`: la geometria (on es clica, on es camina).
- `python3 hd/render.py <sala> <carpeta>`: previsualitzacions ampliades, amb una de depuració (zones, terra
  i personatges a escala).
- `hd/caricatura/`: la proposta A (caricatura, 64 px i cap gran), guardada per a un joc per a públic infantil.
  No la fa servir el sync.

Les altres sales tindran art provisional amb la geometria definitiva fins que el guió de cada acte estigui
tancat i jugat. La barra de verbs i els menús encara són els de la plantilla (ampliats): falten.

## Ordres

```bash
npm install
npm run jugar          # juga en mode text, al terminal (sense art ni Benne), amb [so: nom] abans de cada so
npm test               # tests: el nucli i les partides jugades de cap a peus
npm run validate       # comprova el contingut: forma, referències, textos que falten
npm run fitxes         # genera guio/fitxes-sales.md: què cal crear a l'editor per a cada sala
npm run revisio        # genera guio/revisio.md: totes les variants de text amb la seva condició [-- <sala>]
npm run typecheck
npm run schemas        # regenera game/schemas/ si canvien els tipus del nucli
npm run font           # regenera la font pròpia (suma-regular i suma-negreta) al projecte Benne
npm run sons           # regenera els efectes de so sintetitzats (game/audio/sfx/; cal numpy i ffmpeg)
npm run musica         # regenera la música (game/audio/music/)
npm run benne:sync     # porta el contingut a suma-zero/ (sales noves, textos, diàlegs, sons...) [--watch]
npm run benne:create -- --from <checkout de Benne>   # (re)crea suma-zero/ o n'actualitza el motor
```

## Documentació

- [docs/guia-contingut.md](docs/guia-contingut.md): com escriure diàlegs, missions, pistes, finals...
- [adapters/benne/README.md](adapters/benne/README.md): com connectar-ho amb el projecte Benne.

## Estat actual

- **Guió** complet i revisat ([guio/guio.md](guio/guio.md)), amb la primera revisió de coherència aplicada.
- **Acte 1 jugable de cap a peus** (en mode text, als tests i a Benne): pròleg, el pis (els tres cables,
  en Diu i el passaplats), el bar (les tres coses per a en Marcel, el pany intel·ligent, la trucada de la «dona»
  d'en Puig) i l'aeroport (la primera sincronia per torns, amb la cigarreta de l'Ortega). Acaba amb un final
  provisional, «Continuarà».
- **Regles en codi:** la sincronia per torns (`game/logic/sincronia.ts`), sobre dues novetats del nucli:
  `onAfterAction` (una regla després de cada acció) i l'esdeveniment `situar` (moure l'altra protagonista).
- **Tests:** l'Acte 1 per tots els camins (els tres sacrificis per a en Diu, amb i sense entrepà, tap i
  preparació, el codi dolent, els reinicis de la sincronia), amb una pista a cada pas, i proves de coherència.
- **Sala de mostra amb l'art definitiu** (l'estudi de l'Iri, l'Iri i en Diu). Les altres sales de l'Acte 1 són
  caixes provisionals; els sons són provisionals (`npm run sons`).
- **Següent pas:** l'art provisional de l'Acte 1 amb tots els estats (taula d'estats del guió), i jugar-lo
  sencer al navegador. Després, l'Acte 2.
