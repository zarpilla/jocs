# Ferro-9

Aventura gràfica de "point & click" feta amb [Benne](https://benne.games/), amb la història
**separada del motor**: si mai canviem de motor, només cal reescriure l'adaptador.

Dues protagonistes separades per 120 anys: l'**Iri**, enginyera de la fàbrica de ferro-9, i la **Vet**,
presonera de La Gavina, la presó que l'Aldaia va construir en òrbita amb les restes de la fàbrica. Es comuniquen amb la finestra de fase.
Guió: [guio/guio.md](guio/guio.md).

> **Aquest joc és dins del repositori dels jocs de Mala Herba Soft** (`games/ferro-9/`). El nucli narratiu
> (`packages/narrative-core/`), l'adaptador de Benne (`adapters/benne/`), el motor de Benne
> (`packages/benne/`) i les eines (`tools/`) són a l'arrel i **els comparteixen tots els jocs**. Aquí hi
> ha el que és només d'aquest joc: el contingut (`game/`), el guió, l'art, la música i el projecte Benne
> (`ferro-9/`). Les ordres d'aquí sota s'executen des d'aquesta carpeta, o des de l'arrel amb `-w ferro-9`
> (`npm run validate -w ferro-9`). Vegeu el [README de l'arrel](../../README.md).

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
│ ferro-9/   projecte Benne: motor, art, i el que genera el sync     │
│              cd ferro-9 && npm install && npm run dev              │
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
npm install            # a l'arrel del repositori, la primera vegada
npm run jugar          # juga en mode text, al terminal (sense art ni Benne)
npm test               # tests: el nucli i els tres actes jugats de cap a peus, amb els tres finals
npm run validate       # comprova el contingut: forma, referències, textos que falten
npm run fitxes         # genera guio/fitxes-sales.md: què cal crear a l'editor per a cada sala
npm run typecheck      # tipus de tot el repositori (tots els jocs)
npm run schemas        # regenera game/schemas/ si canvien els tipus del nucli
npm run sons           # regenera els efectes de so sintetitzats (game/audio/sfx/; cal numpy i ffmpeg)
npm run musica         # regenera la música d'ambient de la fàbrica i de La Gavina (game/audio/music/)
npm run benne:sync     # porta el contingut a ferro-9/ (sales noves, textos, diàlegs, sons...) [--watch]
npm run benne:create -- --from <checkout de Benne>   # crea ferro-9/ (amb --motor, actualitza el motor compartit)
```

## Documentació

- [docs/guia-contingut.md](../../docs/guia-contingut.md): com escriure diàlegs, missions, pistes, finals...
- [adapters/benne/README.md](../../adapters/benne/README.md): com connectar-ho amb el projecte Benne.

## Estat actual

- **El joc sencer està escrit i es pot jugar de principi a fi**, en mode text (`npm run jugar`) i a Benne:
  - **Acte 1**, «La descoberta»; **Acte 2**, «El camí llarg»; **Acte 3**, «La finestra».
  - **Tres finals** («La fugida», «La veritat a temps», «Correspondència»), amb escenes que canvien segons el
    que s'ha fet.
  - **Missions secundàries:** salvar la Mira, la carta d'en Mos, la memòria del Cargol, el formulari 27-B i les
    notes perdudes.
  - 10 sales, 11 personatges, 8 diàlegs, 52 objectes, 117 pistes i 51 efectes de so.
- **Tests:** cada acte es juga sencer, per diversos camins, comprovant que a cada pas hi ha alguna pista.
- **Projecte Benne a `ferro-9/`**, amb art provisional: `cd ferro-9 && npm install && npm run dev`. Compila
  amb `tsc`; l'Acte 1 s'ha jugat al navegador, i els actes 2 i 3 s'hi estan provant.
- **Pendent:** l'art definitiu (llista del que cal dibuixar a [guio/fitxes-sales.md](guio/fitxes-sales.md)) i la
  música.
