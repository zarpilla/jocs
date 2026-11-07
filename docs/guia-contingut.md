# Guia per escriure contingut

Tot el joc és a `game/`. Els fitxers de `data/` diuen **què passa**; els de `locales/` diuen
**què es llegeix**. Després de qualsevol canvi: `npm run validate`.

VS Code autocompleta i marca errors als JSON (gràcies a `game/schemas/`).

## Identificadors i claus de text

- **Identificadors** (personatges, nodes, opcions, missions, flags...): `minuscules_i_xifres`, sense
  accents ni espais. Exemple: `pescador`, `sobre_el_far`.
- **Claus de text**: amb punts, per tema. Exemple: `dlg.pescador.hola.1`. Els prefixos que fem
  servir: `joc.`, `ui.`, `pj.` (personatges), `obj.` (objectes), `dlg.` (diàlegs), `mis.`
  (missions), `pista.`, `final.`.
- Els textos poden incloure variables: `"Tens {monedes} monedes"`.

## Estat: `data/state.json`

```json
{ "flags": { "far_ences": false }, "vars": { "monedes": 0 } }
```

Qualsevol flag o variable s'ha de declarar aquí (el validador ho comprova).

## Condicions

Es poden posar a qualsevol camp `if`, `when`, `visibleIf`, `startWhen`...

| Condició | Exemple |
|---|---|
| Flag | `{ "flag": "far_ences" }` · `{ "flag": "far_ences", "is": false }` |
| Variable | `{ "var": "monedes", "op": ">=", "value": 3 }` |
| Té un objecte | `{ "hasItem": "esquer" }` |
| Un personatge recorda | `{ "remembers": { "who": "pescador", "fact": "insultat" } }` (opcional: `"atLeast": 2`) |
| Relació amb un personatge | `{ "relation": { "who": "pescador", "op": ">=", "value": 1 } }` |
| Estat d'una missió | `{ "quest": "encendre_far", "status": "active" }` (o una llista d'estats) |
| Objectiu fet | `{ "objective": { "quest": "q", "objective": "o" } }` |
| Sala visitada / sala actual | `{ "visited": "moll" }` · `{ "inRoom": "moll" }` |
| Node de diàleg vist abans | `{ "seen": { "dialogue": "pescador", "node": "sobre_el_far" } }` |
| Opció triada abans | `{ "chosen": { "dialogue": "pescador", "node": "menu", "choice": "insultar" } }` |
| Combinacions | `{ "all": [...] }` · `{ "any": [...] }` · `{ "not": {...} }` |

## Efectes

| Efecte | Exemple |
|---|---|
| Flag | `{ "setFlag": "far_ences" }` (o amb `"value": false`) |
| Variable | `{ "setVar": "nom", "value": "x" }` · `{ "addVar": "monedes", "amount": 3 }` |
| Inventari | `{ "giveItem": "clau_far" }` · `{ "takeItem": "esquer" }` |
| Memòria | `{ "remember": { "who": "pescador", "fact": "ajudat" } }` · `{ "forget": ... }` |
| Relació | `{ "relation": { "who": "pescador", "change": -2 } }` |
| Missions | `{ "startQuest": "q" }` · `{ "completeObjective": { "quest": "q", "objective": "o" } }` · `{ "completeQuest": "q" }` · `{ "failQuest": "q" }` |
| Final | `{ "ending": "fugida" }` |
| Esdeveniment per al motor | `{ "event": "obrir_porta", "args": { "porta": "taverna" } }` |

## Personatges i memòria: `data/characters.json`

```json
"pescador": {
  "name": "pj.pescador.nom",
  "facts": ["insultat", "ajudat"],
  "relation": { "initial": 0, "min": -3, "max": 3 }
}
```

`facts` és la llista de coses que el personatge **pot** recordar (si n'escrius una que no hi és, el
validador ho detecta). Cada fet compta quantes vegades ha passat. `relation` és un número per a
l'actitud general (amic / enemic).

## Diàlegs: `data/dialogues/<id>.json`

Un diàleg és un graf de **nodes**. Cada node té línies (el que diuen) i opcions (el que pots
respondre).

```json
{
  "id": "pescador",
  "with": "pescador",
  "start": [
    { "if": { "remembers": { "who": "pescador", "fact": "insultat" } }, "node": "rancunios" },
    { "node": "primera_vegada" }
  ],
  "nodes": {
    "primera_vegada": {
      "lines": [ { "who": "pescador", "text": "dlg.pescador.hola" } ],
      "goto": "menu"
    },
    "menu": {
      "choices": [
        { "id": "far", "text": "dlg.pescador.opt.far", "once": true, "next": "sobre_el_far" },
        { "id": "adeu", "text": "dlg.pescador.opt.adeu", "next": "adeu", "end": true }
      ]
    }
  }
}
```

- `start`: un node, o una llista; s'agafa el primer que compleixi la condició. Així una conversa
  comença diferent segons el que ha passat. L'última entrada no hauria de tenir condició.
- **Línies**: `who` és un personatge, `player` (el protagonista) o `narrator`. Poden tenir `if`
  (només es diuen si es compleix) i `effects`.
- **Opcions**: `if` (només surt si...), `once` (desapareix un cop triada), `silent` (el protagonista
  no la diu en veu alta), `effects`, `next` (a quin node va), `end` (acaba la conversa).
- `goto`: quan un node no té opcions, salta a un altre (típicament, tornar al `menu`).
- Una opció sense `next` torna al mateix node.
- El protagonista diu el text de l'opció abans de la resposta.

## Missions: `data/quests.json`

```json
"esquer_pescador": {
  "kind": "side",
  "title": "mis.esquer.titol",
  "startWhen": { ... },
  "objectives": [
    { "id": "trobar_esquer", "text": "mis.esquer.obj.trobar", "completeWhen": { "hasItem": "esquer" } },
    { "id": "donar_esquer", "text": "mis.esquer.obj.donar" }
  ],
  "failWhen": { "relation": { "who": "pescador", "op": "<=", "value": -3 } },
  "onComplete": [ { "relation": { "who": "pescador", "change": 2 } } ]
}
```

- `kind`: `main` (principal) o `side` (secundària).
- Una missió s'activa amb `startWhen` o amb l'efecte `startQuest`.
- Els objectius es completen sols (`completeWhen`) o amb l'efecte `completeObjective`.
- La missió es completa quan tots els objectius no `optional` estan fets (o amb `completeWhen`).
- `failWhen` la fa fallar. `onComplete` / `onFail` són efectes.

## Pistes: `data/hints.json`

```json
"com_aconseguir_clau": {
  "priority": 10,
  "when": { "quest": "encendre_far", "status": "active" },
  "doneWhen": { "hasItem": "clau_far" },
  "levels": ["pista.clau.1", "pista.clau.2", "pista.clau.3"]
}
```

Quan el jugador demana una pista, es tria la de més prioritat que sigui rellevant (`when`) i no
estigui resolta (`doneWhen`). Cada nova petició mostra el nivell següent, de més vague a més
explícit.

## Objectes condicionals: `data/objects.json`

```json
"esquer_al_moll": { "room": "moll", "visibleIf": { "quest": "esquer_pescador", "status": "active" } }
```

Coses d'una sala que apareixen o desapareixen. A Benne, la sala les lliga als seus props amb
`bindObjects` (vegeu l'adaptador).

## Finals: `data/endings.json`

```json
"heroi_del_port": { "title": "final.heroi.titol", "text": "final.heroi.text", "priority": 10, "when": { ... } }
```

En arribar al final, es tria el de més `priority` el `when` del qual es compleixi. Un efecte
`{ "ending": "id" }` en força un directament (p. ex. una decisió que acaba el joc abans d'hora).

## Afegir un idioma

1. Copia `game/locales/ca/` a `game/locales/<codi>/` i tradueix-ne els valors (no les claus).
2. Afegeix el codi a `locales` dins `game/data/game.json`.
3. `npm run validate` avisa dels textos que falten (si en falta algun, s'ensenya en català).
