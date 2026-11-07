# Ferro-9

Aventura gràfica de "point & click" feta amb [Benne](https://benne.games/), amb la història
**separada del motor**: si mai canviem de motor, només cal reescriure l'adaptador.

Dues protagonistes separades per 120 anys: l'**Iri**, enginyera de la fàbrica de ferro-9, i la **Vet**,
presonera de La Gavina, la presó construïda damunt les seves restes. Es comuniquen amb la finestra de fase.
Guió: [guio/proposta-1-v2.md](guio/proposta-1-v2.md).

## Les tres capes

```
┌──────────────────────────────────────────────────────────────────────┐
│ game/                 EL JOC                                         │
│   data/               sales, personatges, objectes, diàlegs,         │
│                       missions, pistes, finals (JSON)                │
│   locales/ca/         textos en català (un fitxer per tema)          │
│   logic/              regles pròpies del joc (finestra de fase), TS  │
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
│ joc-benne/   (projecte Benne: sales, art, so, scripts de sala)       │
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

## Què ja funciona

| Necessitat | Com |
|---|---|
| Dues protagonistes | Inventaris i sales separats; condició `protagonist`; canvi des del contingut (`{"event": "protagonista"}`) o per GUI |
| Sales i interaccions sense codi | `data/rooms/<sala>.json`: verb + cosa (+ objecte) → línies, efectes, diàleg, canvi de sala, acció de joc |
| Decisions que afecten converses posteriors | Opcions amb `effects` + condicions `chosen` / `seen` / `flag` |
| Personatges que recorden | `remember` / `forget` fets i `relation` (amb límits) per personatge; el diàleg pot començar en un node o altre segons el que recorden |
| Diferents finals | `endings.json`: es tria pel `when` de més prioritat, o es força amb l'efecte `ending` |
| Objectes que només apareixen en certes circumstàncies | `visibleIf` a les coses de cada sala; l'adaptador les mostra o amaga soles |
| Missions secundàries | `quests.json` (`kind: "side"`), amb inici, objectius, èxit i fracàs automàtics |
| Sistema de pistes | `hints.json`: pistes per prioritat, amb nivells cada cop més explícits i segons la protagonista. Un test comprova que a cada pas n'hi hagi alguna |
| Multiidioma | Claus + `locales/`, amb tornada a l'idioma per defecte i `{variables}` |
| Desar / carregar | L'estat narratiu va dins les partides de Benne, i les partides antigues funcionen amb contingut nou |

## Ordres

```bash
npm install
npm run jugar          # juga en mode text, al terminal (sense art ni Benne)
npm test               # tests: nucli + l'Acte 1 jugat de cap a peus
npm run validate       # comprova el contingut: forma, referències, textos que falten
npm run fitxes         # genera guio/fitxes-sales.md: què cal crear a l'editor per a cada sala
npm run typecheck
npm run schemas        # regenera game/schemas/ si canvien els tipus del nucli
npm run benne:sync -- --project joc-benne [--init] [--locale ca] [--watch]
```

## Documentació

- [docs/guia-contingut.md](docs/guia-contingut.md): com escriure diàlegs, missions, pistes, finals...
- [adapters/benne/README.md](adapters/benne/README.md): com connectar-ho amb el projecte Benne.

## Estat actual

- **Acte 1, «La descoberta»: escrit i jugable en mode text** (5 sales, 3 diàlegs, 19 objectes, 20 pistes).
- Actes 2 i 3: al guió, pendents d'escriure en JSON.
- Benne: el pont està comprovat amb els tipus reals de Benne, però **encara no s'ha executat dins un
  projecte Benne**. Falta crear el projecte i l'art (vegeu [guio/fitxes-sales.md](guio/fitxes-sales.md)).
