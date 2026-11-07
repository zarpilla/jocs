# Fitxes de sales

> Generat amb `npm run fitxes` a partir de `game/data/`. No l'editis a mà.

Cada cosa de la llista és un **prop**, un **hotspot** o un **personatge** de la sala a l'editor del motor, amb **aquest id** (o un id del tipus `<sala>-hotspot-<id>`). Les que tenen condició s'han de lligar amb `bindHotspots`.

## Iri

### Sala de calderes · `fabrica_calderes`

| Id | Nom | Tipus | Apareix | Verbs |
|---|---|---|---|---|
| `capatas` | capatàs Pruna | personatge | sempre | look, talkTo, pull, pickUp, push, use + plomall, use + objecte |
| `segell` | segell oficial | prop | `{"all":[{"flag":"segell_caigut"},{"flag":"segell_agafat","is":false}]}` | look, pickUp |
| `tauler` | tauler d'anuncis | hotspot / prop | sempre | look, pickUp |
| `alarma` | llum d'alarma | hotspot / prop | sempre | look |
| `porta_magatzem` | magatzem | hotspot / prop → `fabrica_magatzem` | sempre | open, use, walkTo, look |
| `porta_cambra` | porta de la cambra | hotspot / prop → `fabrica_cambra` | sempre | use + clau_cambra, open, use, walkTo, pull, push, look |

### Cambra de ressonància · `fabrica_cambra`

| Id | Nom | Tipus | Apareix | Verbs |
|---|---|---|---|---|
| `palanca` | palanca | hotspot / prop | sempre | use + clau_anglesa, pull, push, use, look |
| `cambra` | cambra | hotspot / prop | sempre | look, use + objecte, pickUp, open |
| `boto` | botó de sincronia | prop | `{"flag":"alarma_apagada"}` | look, push, use |
| `porta` | sala de calderes | hotspot / prop → `fabrica_calderes` | sempre | open, use, walkTo |

### Magatzem d'eines · `fabrica_magatzem`

| Id | Nom | Tipus | Apareix | Verbs |
|---|---|---|---|---|
| `cargol` | Cargol | personatge | sempre | talkTo, look, give + objecte, push, pull |
| `plomall` | plomall | prop | `{"hasItem":"plomall","who":"iri","is":false}` | look, pickUp |
| `caixa_eines` | caixa d'eines | prop | `{"hasItem":"caixa_eines","who":"iri","is":false}` | look, pickUp |
| `prestatges` | prestatges | hotspot / prop | sempre | look, pickUp |
| `porta_calderes` | sala de calderes | hotspot / prop → `fabrica_calderes` | sempre | open, use, walkTo |

## Vet

### Cel·la 9 · `gavina_cella`

| Id | Nom | Tipus | Apareix | Verbs |
|---|---|---|---|---|
| `panell` | panell rovellat | hotspot / prop | sempre | look, push, use, use + clau_anglesa, use + objecte, pickUp, open |
| `altaveu` | altaveu de la MARE | hotspot / prop | sempre | talkTo, look, push, pull, use |
| `bruc` | Bruc | personatge | sempre | talkTo, look |
| `avis` | avís | prop | `{"flag":"avis_agafat","is":false}` | look, pickUp |
| `llitera` | llitera | hotspot / prop | sempre | look, pickUp |
| `escarabat` | Senyor Bigotis | prop | `{"flag":"escarabat_agafat","is":false}` | look, pickUp |
| `safata` | safata de sopar | prop | `{"flag":"sopa_agafada","is":false}` | look, pickUp |
| `porta` | porta de la cel·la | hotspot / prop → `gavina_passadis` | sempre | use + imant_ferro9, look, open, push, pull, use |
| `finestreta` | finestreta | hotspot / prop | sempre | look |

### Passadís del mòdul C · `gavina_passadis`

| Id | Nom | Tipus | Apareix | Verbs |
|---|---|---|---|---|
| `cartell` | cartell | hotspot / prop | sempre | look |
| `camera` | càmera | hotspot / prop | sempre | look |
| `porta_cella` | cel·la 9 | hotspot / prop → `gavina_cella` | sempre | open, use, walkTo |

## Objectes d'inventari

| Id | Nom | Pes | Altres |
|---|---|---|---|
| `clau_anglesa` | clau anglesa | 1.2 | material: ferro9 |
| `formulari_27b` | formulari 27-B | 0.01 |  |
| `formulari_segellat` | formulari 27-B segellat | 0.01 |  |
| `formulari_triplicat` | formulari 27-B segellat per triplicat | 0.01 |  |
| `plomall` | plomall | 0.2 |  |
| `segell` | segell oficial | 0.4 |  |
| `clau_cambra` | clau de la cambra | 0.1 |  |
| `llapis` | llapis | 0.01 |  |
| `llibreta_torn` | llibreta de torn | 0.3 |  |
| `caixa_eines` | caixa d'eines | 9 |  |
| `imant_ferro9` | imant de ferro-9 | 0.3 | material: ferro9 |
| `nota_iri` | nota de l'Iri | 0.01 |  |
| `avis_reciclatge` | avís de reciclatge | 0.01 |  |
| `llapis_ulls` | llapis d'ulls | 0.01 |  |
| `nota_vet` | nota de la Vet | 0.01 |  |
| `fullet_reeducacio` | fullet de reeducació | 0.01 |  |
| `nota_pany` | dibuix del pany | 0.01 |  |
| `escarabat` | escarabat | 0.01 | viu: true |
| `sopa` | sopa | 0.5 | liquid: true |
