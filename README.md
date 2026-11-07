# Aventura gràfica (nom provisional)

Aventura gràfica de "point & click" feta amb [Benne](https://benne.games/), però amb la història
**separada del motor**: si mai canviem de motor, només cal reescriure l'adaptador.

## Les tres capes

```
┌──────────────────────────────────────────────────────────────────────┐
│ game/                 EL JOC: només dades (JSON) i textos            │
│   data/               personatges, diàlegs, missions, pistes, finals │
│   locales/ca/         textos en català (un fitxer per tema)          │
│   schemas/            JSON Schema (autocompletat i errors a VS Code) │
└──────────────────────────────────────────────────────────────────────┘
                 │ llegeix
┌──────────────────────────────────────────────────────────────────────┐
│ packages/narrative-core/   MOTOR NARRATIU (TypeScript pur)           │
│   estat · condicions · efectes · diàlegs · memòria dels personatges  │
│   missions · pistes · finals · objectes condicionals · traduccions   │
│   No sap res de Benne, ni de pantalles, ni d'inventaris.             │
└──────────────────────────────────────────────────────────────────────┘
                 │ WorldPort (preguntes)  ▲ NarrativeEvent (ordres)
┌──────────────────────────────────────────────────────────────────────┐
│ adapters/benne/        L'ÚNICA PEÇA QUE CONEIX BENNE                 │
│   runtime/             pont que es copia al projecte Benne           │
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
| Decisions que afecten converses posteriors | Opcions amb `effects` + condicions `chosen` / `seen` / `flag` |
| Personatges que recorden | `remember` / `forget` fets i `relation` (amb límits) per personatge; el diàleg pot començar en un node o altre segons el que recorden |
| Diferents finals | `endings.json`: es tria pel `when` de més prioritat, o es força amb l'efecte `ending` |
| Objectes que només apareixen en certes circumstàncies | `objects.json` amb `visibleIf`; l'adaptador els mostra o amaga sols |
| Missions secundàries | `quests.json` (`kind: "side"`), amb inici, objectius, èxit i fracàs automàtics |
| Sistema de pistes | `hints.json`: pistes per prioritat amb nivells cada cop més explícits |
| Multiidioma | Claus + `locales/`, amb tornada a l'idioma per defecte i `{variables}` |
| Desar / carregar | L'estat narratiu va dins les partides de Benne, i les partides antigues funcionen amb contingut nou |

## Ordres

```bash
npm install
npm test               # tests del nucli (juga la història d'exemple sencera)
npm run validate       # comprova el contingut: forma, referències, textos que falten
npm run typecheck
npm run schemas        # regenera game/schemas/ si canvien els tipus del nucli
npm run benne:sync -- --project joc-benne [--locale ca] [--watch]
```

## Documentació

- [docs/guia-contingut.md](docs/guia-contingut.md): com escriure diàlegs, missions, pistes, finals...
- [adapters/benne/README.md](adapters/benne/README.md): com connectar-ho amb el projecte Benne.

## Estat actual

El contingut de `game/` és un **exemple** (un pescador, un far, una missió secundària) per provar
totes les mecàniques. El substituirem quan tinguem el guió.
