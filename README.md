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

Pendents de fixar abans de la sala de mostra: alçada dels personatges en píxels, mida de les icones
(la casella de l'inventari de Benne és de 49×27) i paleta.

## Ordres

```bash
npm install
npm run jugar          # juga en mode text, al terminal (sense art ni Benne)
npm test               # tests: el nucli i les partides jugades de cap a peus
npm run validate       # comprova el contingut: forma, referències, textos que falten
npm run fitxes         # genera guio/fitxes-sales.md: què cal crear a l'editor per a cada sala
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

- Repositori muntat amb el nucli narratiu, les eines i l'adaptador de Ferro-9, nets del contingut de
  Ferro-9.
- **Contingut mínim** per comprovar que tot funciona: el pis (l'estudi de l'Iri i la cuina de la Vet),
  una caixa de cartró i un final de prova.
- Projecte Benne a `suma-zero/` creat amb `npm run benne:create`, amb els pegats propis al motor
  (`adapters/benne/patches/`) i la font pròpia.
- **Següent pas:** el guió (`guio/guio.md`) i la revisió de coherència, abans d'escriure cap JSON.
