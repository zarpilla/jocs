# Guia per escriure contingut

Tot el joc és a `game/`. Els fitxers de `data/` diuen **què passa**; els de `locales/` diuen
**què es llegeix**. Després de qualsevol canvi: `npm run validate`, i per provar-ho, `npm run jugar`.

VS Code autocompleta i marca errors als JSON (gràcies a `game/schemas/`).

## Identificadors i claus de text

- **Identificadors** (personatges, nodes, opcions, missions, flags...): `minuscules_i_xifres`, sense
  accents ni espais. Exemple: `cargol`, `porta_cambra_oberta`.
- **Claus de text**: amb punts, per tema. Exemple: `dlg.mos.primera1`. Els prefixos que fem
  servir: `joc.`, `ui.`, `pj.` (personatges), `obj.` (objectes), `dlg.` (diàlegs), `mis.`
  (missions), `pista.`, `final.`.
- Els textos poden incloure variables: `"Queden {enceses_restants} enceses"`.

## Estat: `data/state.json`

```json
{ "flags": { "alarma_apagada": false }, "vars": { "enceses_restants": 12 } }
```

Qualsevol flag o variable s'ha de declarar aquí (el validador ho comprova).

## Condicions

Es poden posar a qualsevol camp `if`, `when`, `visibleIf`, `startWhen`...

| Condició | Exemple |
|---|---|
| Flag | `{ "flag": "alarma_apagada" }` · `{ "flag": "alarma_apagada", "is": false }` |
| Variable | `{ "var": "finestra_armada", "op": "==", "value": "vet" }` |
| Té un objecte | `{ "hasItem": "segell" }` (la protagonista activa) · `{ "hasItem": "imant_ferro9", "who": "vet" }` |
| Protagonista activa | `{ "protagonist": "iri" }` |
| Un personatge recorda | `{ "remembers": { "who": "mos", "fact": "insultat" } }` (opcional: `"atLeast": 2`) |
| Relació amb un personatge | `{ "relation": { "who": "mos", "op": ">=", "value": 1 } }` |
| Estat d'una missió | `{ "quest": "encendre_far", "status": "active" }` (o una llista d'estats) |
| Objectiu fet | `{ "objective": { "quest": "q", "objective": "o" } }` |
| Sala visitada / sala actual | `{ "visited": "moll" }` · `{ "inRoom": "moll" }` |
| Node de diàleg vist abans | `{ "seen": { "dialogue": "mos", "node": "primera" } }` |
| Opció triada abans | `{ "chosen": { "dialogue": "mos", "node": "convencer", "choice": "insultar" } }` |
| Combinacions | `{ "all": [...] }` · `{ "any": [...] }` · `{ "not": {...} }` |

## Efectes

| Efecte | Exemple |
|---|---|
| Flag | `{ "setFlag": "alarma_apagada" }` (o amb `"value": false`) |
| Variable | `{ "setVar": "nom", "value": "x" }` · `{ "addVar": "sospita_sic", "amount": 1 }` |
| Inventari | `{ "giveItem": "clau_cambra" }` · `{ "takeItem": "formulari_27b" }` (opcional: `"who": "vet"`) |
| Memòria | `{ "remember": { "who": "cargol", "fact": "preguntat_pel_dia" } }` · `{ "forget": ... }` |
| Relació | `{ "relation": { "who": "mos", "change": -2 } }` |
| Missions | `{ "startQuest": "q" }` · `{ "completeObjective": { "quest": "q", "objective": "o" } }` · `{ "completeQuest": "q" }` · `{ "failQuest": "q" }` |
| Final | `{ "ending": "fugida" }` |
| Esdeveniment per al motor | `{ "event": "obrir_porta", "args": { "porta": "taverna" } }` |
| Canviar de protagonista | `{ "event": "protagonista", "args": { "id": "vet" } }` |
| Moure l'altra protagonista | `{ "event": "situar", "args": { "who": "iri", "room": "aeroport_personal" } }` (hi és quan s'hi canviï; no serveix per a la protagonista activa, que va amb `goTo`) |

## Joc i protagonistes: `data/game.json`

```json
"protagonists": ["iri", "vet"],
"start": {
  "iri": { "room": "fabrica_calderes", "items": ["clau_anglesa", "llapis", "llibreta_torn"] },
  "vet": { "room": "gavina_cella" }
}
```

Cada protagonista té el seu inventari i la seva sala. La primera de la llista és la que comença.
`"who": "player"` a les línies és sempre la protagonista que juga en aquell moment.

## Sales i interaccions: `data/rooms/<sala>.json`

Una sala és una llista de **coses** (props, zones o personatges, amb el mateix id que tindran al motor)
i què passa quan el jugador hi fa un verb.

```json
{
  "name": "sala.fabrica_cambra.nom",
  "protagonist": "iri",
  "onEnter": [
    { "id": "primera", "verb": "*", "once": true, "lines": [ { "who": "player", "text": "sala.fabrica_cambra.intro1" } ] }
  ],
  "hotspots": {
    "palanca": {
      "name": "sala.fabrica_cambra.palanca.nom",
      "interactions": [
        { "verb": "use", "item": "clau_anglesa", "if": { "flag": "alarma_apagada", "is": false },
          "lines": [ ... ], "effects": [ { "setFlag": "alarma_apagada" } ] },
        { "verb": ["pull", "push", "use"], "lines": [ ... ] },
        { "verb": "look", "lines": [ ... ] }
      ]
    },
    "boto": { "visibleIf": { "flag": "alarma_apagada" }, "interactions": [ ... ] }
  }
}
```

- **Verbs** (els de la plantilla de 9 verbs de Benne): `look`, `pickUp`, `use`, `open`, `close`, `push`, `pull`,
  `talkTo`, `give`, i també `walkTo`. `"*"` = qualsevol.
- **S'agafa la primera interacció que encaixi**, de dalt a baix: posa primer les més concretes (amb
  condició o amb objecte) i al final les generals.
- `item`: només encaixa si el jugador fa servir aquest objecte ("fer servir X amb..."). `"*"` = qualsevol
  objecte. Una interacció sense `item` no encaixa mai si n'hi ha un.
- Una interacció pot tenir `lines`, `effects`, `dialogue` (comença una conversa), `goTo` (canvia de sala),
  `action` (una regla del joc en codi, vegeu més avall) i `once` (amb `id`).
- `visibleIf` a una cosa: si no es compleix, no es veu ni es pot tocar.
- `onEnter`: s'executa la primera que encaixi en entrar a la sala.
- Si cap interacció no encaixa, la protagonista diu la frase per defecte: `ui.defecte.<verb>.<protagonista>`,
  o si no n'hi ha, `ui.defecte.<verb>`, o `ui.defecte`. Excepció: **mirar un objecte de l'inventari**
  sense `look` propi diu la seva `description` (`items.json`). Per a una frase diferent segons qui
  mira, posa-li un `look` amb `"if": { "protagonist": "vet" }`.

### Sons

Qualsevol línia (d'una interacció o d'un diàleg) pot dur `"sound"`: el so sona just quan la línia comença.
És el nom d'un fitxer de `game/audio/sfx/` sense extensió, i pot dur variables entre claus, que es posen
amb el valor que tenen en acabar la interacció:

```json
{ "who": "player", "text": "obj.molla.estirar", "sound": "molla_{molla_tensio}" }
```

Els sons els genera `npm run sons` (`tools/sons.py`, sintetitzats). Per posar-hi un so fet a mà, deixa
el fitxer a `game/audio/sfx/` i treu-lo de la llista `SONS` del generador. `npm run validate` avisa si una
línia demana un so que no existeix, i `npm run benne:sync` els copia al projecte Benne.

Els **personatges** (`characters.json`) i els **objectes** (`items.json`) també poden tenir
`interactions`: les dels personatges valen a totes les sales (una sala les pot substituir), i les dels
objectes són per mirar-los a l'inventari o combinar-los (`"verb": "use", "item": "formulari_27b"` dins
del `segell` = fer servir el segell amb el formulari; funciona en tots dos sentits).

## Regles del joc en codi: `game/logic/`

El que no es pot dir bé amb JSON (la finestra de fase, per exemple) és codi TypeScript **del joc**, que
només depèn del nucli, mai de Benne. Les regles s'exposen com a **accions**:

```json
{ "verb": "use", "item": "*", "action": { "name": "finestra.posar", "args": { "item": "$item" } } }
```

`"$item"` és l'objecte que s'ha fet servir. Les accions que existeixen ara:

| Acció | Què fa |
|---|---|
| `finestra.posar` | Posa l'objecte a la cambra de la protagonista activa, si hi cap (< 2 kg, ni viu ni líquid) i si la història el necessita a l'altra banda (`finestra`): `props` a `items.json` |
| `finestra.treure` | El torna a l'inventari, si el camp no està armat |
| `finestra.boto` | Arma el camp, o el sincronitza si l'altra ja l'havia armat: l'objecte canvia d'època |

Les propietats que fa servir la finestra són a cada objecte: `"props": { "pes": 1.2, "material": "ferro9" }`,
`"viu": true`, `"liquid": true`, i `"finestra"` per als que s'han de poder enviar: `"vet"` o `"iri"` (qui
l'envia) o `true` (totes dues). Sense aquesta marca, o des de l'altra banda, un objecte que hi cabria no passa:
la protagonista diu que no val una encesa. Si un trencaclosques nou demana enviar alguna cosa, cal marcar-la.

Els textos de la cambra diuen el nom de l'objecte amb article («Poso la molla dins la cambra»): cada objecte
necessita un text `obj.<id>.amb_article` («la molla», «l'imant de ferro-9», «els plànols»). El validador avisa
si en falta algun.

Un `{ "event": "final" }` acaba el joc amb el final que toqui (`endings.json`).

## Canviar de protagonista

El jugador canvia de protagonista amb el botó «Canvia» (a l'esquerra dels verbs) o amb `canviar` en mode text.
`game.json` pot dir des de quan amb `"switchWhen"` (una condició; a Ferro-9, quan l'Iri ha apagat l'alarma i el
joc ha passat per primer cop a la Vet). Fins aleshores, el botó no surt. Els canvis que fa la mateixa història
(`{ "event": "protagonista" }`) no en depenen.

## Pròleg i cinemàtiques

Una sala amb `"cutscene": { "skipTo": "<sala>" }` és una cinemàtica: no té res per clicar ni protagonista,
l'adaptador amaga la barra de verbs, i el seu `onEnter` es reprodueix sol fins al `goTo`, que porta a la
pantalla següent. Amb Esc se salta tot i es va directament a `skipTo`. Per començar la partida amb un pròleg,
`game.json` porta `"intro": "<primera sala>"`. Les imatges de les pantalles es dibuixen com les de les sales.

La **portada** és la sala de `"cover"` a `game.json`: l'adaptador hi amaga la barra de verbs i hi posa els botons
«Comença» (va a `intro`) i «Carrega una partida» (GUI `portada`, creada per la sincronització).

Cada final té un títol (`title`), una escena opcional (`scene`) i un text de tancament (`text`). L'escena és una
llista de línies com les d'una interacció, amb `if` per explicar el que passa després segons la partida (p. ex.
«En Mos surt de la presó» només si la Vet li va tornar la carta). A Benne es mostren sobre negre; si parla un
personatge, surt amb el nom al davant.

## Personatges i memòria: `data/characters.json`

```json
"cargol": {
  "name": "pj.cargol.nom",
  "facts": ["formulari_acceptat", "preguntat_pel_dia", "triplicat_acceptat"],
  "relation": { "initial": 0, "min": -3, "max": 5 }
}
```

`appearance` canvia l'aspecte (l'animació del sprite) segons l'estat; la primera que es compleixi:

```json
"capatas": { "appearance": [ { "if": { "flag": "segell_caigut" }, "anim": "DormSenseSegell" } ] }
```

El Cargol és a les dues èpoques amb **el mateix id**: el que recorda de l'Iri al passat ho continua
recordant 120 anys després, quan el troba la Vet.

`facts` és la llista de coses que el personatge **pot** recordar (si n'escrius una que no hi és, el
validador ho detecta). Cada fet compta quantes vegades ha passat. `relation` és un número per a
l'actitud general (amic / enemic).

## Diàlegs: `data/dialogues/<id>.json`

Un diàleg és un graf de **nodes**. Cada node té línies (el que diuen) i opcions (el que pots
respondre).

```json
{
  "id": "mos",
  "with": "mos",
  "start": [
    { "if": { "remembers": { "who": "mos", "fact": "insultat" } }, "node": "ofes" },
    { "if": { "seen": { "dialogue": "mos", "node": "primera" } }, "node": "hola" },
    { "node": "primera" }
  ],
  "nodes": {
    "primera": {
      "lines": [ { "who": "mos", "text": "dlg.mos.primera1" } ],
      "goto": "menu"
    },
    "menu": {
      "choices": [
        { "id": "reciclatge", "text": "dlg.mos.opt.reciclatge", "once": true, "next": "reciclatge" },
        { "id": "adeu", "text": "dlg.mos.opt.adeu", "next": "adeu", "end": true }
      ]
    }
  }
}
```

- `start`: un node, o una llista; s'agafa el primer que compleixi la condició. Així una conversa
  comença diferent segons el que ha passat. L'última entrada no hauria de tenir condició.
- **Línies**: `who` és un personatge, `player` (el protagonista), `narrator` o `title`. Poden tenir
  `if` (només es diuen si es compleix) i `effects`. Una línia `title` és una pantalla de títol (p. ex.
  «Acte 2 · Els costos»): la pantalla es fon a negre, s'hi mostra el text i torna la imatge. Les
  línies `title` seguides es mostren juntes sobre el mateix negre.
- **Opcions**: `if` (només surt si...), `once` (desapareix un cop triada), `silent` (el protagonista
  no la diu en veu alta), `effects`, `next` (a quin node va), `end` (acaba la conversa).
- `goto`: quan un node no té opcions, salta a un altre (típicament, tornar al `menu`).
- Una opció sense `next` torna al mateix node.
- El protagonista diu el text de l'opció abans de la resposta.

## Missions: `data/quests.json`

```json
"acte1": {
  "kind": "main",
  "title": "mis.acte1.titol",
  "objectives": [
    { "id": "entrar_cambra", "text": "mis.acte1.obj.entrar_cambra", "completeWhen": { "flag": "porta_cambra_oberta" } },
    { "id": "primera_transferencia", "text": "mis.acte1.obj.primera_transferencia",
      "completeWhen": { "var": "transferencies", "op": ">=", "value": 1 } }
  ]
}
```

- `kind`: `main` (principal) o `side` (secundària).
- Una missió s'activa amb `startWhen` o amb l'efecte `startQuest`.
- Els objectius es completen sols (`completeWhen`) o amb l'efecte `completeObjective`.
- La missió es completa quan tots els objectius no `optional` estan fets (o amb `completeWhen`).
- `failWhen` la fa fallar. `onComplete` / `onFail` són efectes.

## Pistes: `data/hints.json`

```json
"iri_segell": {
  "priority": 5,
  "when": { "all": [ { "protagonist": "iri" }, { "hasItem": "formulari_27b", "who": "iri" }, { "hasItem": "segell", "who": "iri", "is": false } ] },
  "doneWhen": { "hasItem": "segell", "who": "iri" },
  "levels": ["pista.iri_segell.1", "pista.iri_segell.2", "pista.iri_segell.3"]
}
```

Quan el jugador demana una pista, es tria la de més prioritat que sigui rellevant (`when`) i no
estigui resolta (`doneWhen`). Cada nova petició mostra el nivell següent, de més vague a més
explícit.

Posa `{ "protagonist": "iri" }` dins del `when` perquè la pista només surti a qui la pot fer servir.
El test de l'Acte 1 comprova que, a cada pas de la partida, hi hagi alguna pista disponible: si
afegeixes un trencaclosques i t'oblides la pista, el test ho diu.

## Objectes condicionals

Són les coses d'una sala amb `visibleIf` (vegeu *Sales i interaccions*). A Benne, la sala les lliga als
seus props amb `bindHotspots` (vegeu l'adaptador). `npm run fitxes` en fa la llista.

### Decorats: una cosa que canvia d'aspecte

Quan una cosa s'ha de **veure diferent** segons l'estat però s'ha de poder seguir clicant igual (un panell
tancat, obert, reparat...), no la dupliquis: afegeix **decorats** a la sala. Són dibuixos que es posen
damunt quan es compleix `visibleIf` i que no es poden clicar (el clic arriba a la cosa de sota).

```json
"decor": {
  "panell_obert":   { "visibleIf": { "all": [ { "flag": "panell_vet_obert" }, { "flag": "panell_vet_reparat", "is": false } ] } },
  "panell_reparat": { "visibleIf": { "flag": "panell_vet_reparat" } }
}
```

`npm run benne:sync` els afegeix a la sala de Benne com a props no clicables. Cada decorat necessita un
fotograma amb el seu id a l'art de la sala (a l'art provisional, una funció a `room_designs.py`).

Un decorat es dibuixa per sobre de les coses clicables. Amb `"sota": true`, per sota: per a un fons que en té
d'altres al davant (l'interior de la nevera oberta, amb la pizza com a prop clicable).

## Finals: `data/endings.json`

```json
"veritat": { "title": "final.veritat.titol", "text": "final.veritat.text", "priority": 2,
             "when": { "all": [ { "flag": "fugida_completada" }, { "flag": "mira_salvada" }, { "flag": "planols_robats" } ] } }
```

En arribar al final, es tria el de més `priority` el `when` del qual es compleixi. Un efecte
`{ "ending": "id" }` en força un directament (p. ex. una decisió que acaba el joc abans d'hora).

## Afegir un idioma

1. Copia `game/locales/ca/` a `game/locales/<codi>/` i tradueix-ne els valors (no les claus).
2. Afegeix el codi a `locales` dins `game/data/game.json`.
3. `npm run validate` avisa dels textos que falten (si en falta algun, s'ensenya en català).
