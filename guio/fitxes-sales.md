# Fitxes de sales

> Generat amb `npm run fitxes` a partir de `game/data/`. No l'editis a mà.

Cada cosa de la llista és un **prop**, un **hotspot** o un **personatge** de la sala a l'editor del motor, amb **aquest id** (o un id del tipus `<sala>-hotspot-<id>`). Les que tenen condició s'han de lligar amb `bindHotspots`.

## Iri

### L'oficina de facturació · `aeroport_oficina`

| Id | Nom | Tipus | Apareix | Verbs |
|---|---|---|---|---|
| `terminal` | terminal | hotspot / prop | sempre | use, look |
| `impressora` | impressora | hotspot / prop | sempre | push, use, pickUp, look |
| `porta` | porta | hotspot / prop → `aeroport_personal` | sempre | use, open, walkTo, look |

### La porta de personal · `aeroport_personal`

| Id | Nom | Tipus | Apareix | Verbs |
|---|---|---|---|---|
| `teclat` | teclat | hotspot / prop → `aeroport_oficina` | sempre | use, push, look |
| `porta` | porta de personal | hotspot / prop → `aeroport_oficina` | sempre | use, open, walkTo, look |

### L'estudi · `pis_estudi`

| Id | Nom | Tipus | Apareix | Verbs |
|---|---|---|---|---|
| `finestra` | finestra | hotspot / prop | sempre | look, open |
| `poster` | pòster | hotspot / prop | sempre | look |
| `matalas` | matalàs | hotspot / prop | sempre | look |
| `pizzes` | caixes de pizza | hotspot / prop | sempre | look, open |
| `ordinadors` | ordinadors | hotspot / prop | sempre | use, look |
| `router` | router | hotspot / prop | sempre | use + cable_xarxa, use + cable_alimentacio, use + objecte, look, use, push, pull, pickUp |
| `fibra` | presa de la fibra | hotspot / prop | sempre | pickUp, use, pull, look |
| `passaplats` | passaplats | hotspot / prop | sempre | open, close, talkTo, use, use + objecte, look |
| `caixa` | caixa | prop | `{"all":[{"hasItem":"caixa_cartro","is":false,"who":"iri"},{"not":{"var":"sacrifici","op":"==","value":"caixa"}}]}` | look, open, pickUp |
| `diu` | Diu | personatge | sempre | use + objecte, use + caixa_cartro, use + auriculars, use + pizza, talkTo, look, pickUp |

## Vet

### La terminal · `aeroport_terminal`

| Id | Nom | Tipus | Apareix | Verbs |
|---|---|---|---|---|
| `soler` | agent Soler | personatge | sempre | talkTo, look |
| `taulell` | taulell | hotspot / prop | sempre | look |
| `vidriera` | vidriera | hotspot / prop | sempre | look |
| `empleat` | objectes perduts | personatge | sempre | talkTo, look |
| `maleti` | maletí | prop | `{"hasItem":"maleti","is":false,"who":"vet"}` | look, pickUp |
| `ulleres` | ulleres | prop | `{"hasItem":"ulleres","is":false,"who":"vet"}` | pickUp, look |
| `nen` | nen | personatge → `avio` | sempre | talkTo, use, pickUp, look |

### El rebost · `bar_rebost`

| Id | Nom | Tipus | Apareix | Verbs |
|---|---|---|---|---|
| `calaix` | calaix | hotspot / prop | sempre | open, pickUp, look |
| `caixes` | caixes | hotspot / prop | sempre | look |
| `porta` | bar | hotspot / prop → `bar_sala` | sempre | use, open, walkTo, look |

### Bar La Propina · `bar_sala`

| Id | Nom | Tipus | Apareix | Verbs |
|---|---|---|---|---|
| `marcel` | Marcel | personatge | sempre | give + tap, give + recepta, give + comandament, give + objecte, talkTo, look |
| `tomas` | Tomàs | personatge | `{"flag":"tomas_rebost","is":false}` | give + tap, give + objecte, talkTo, look |
| `tap_barra` | clauer | prop | `{"flag":"tap_barra"}` | pickUp, look |
| `comandament_barra` | comandament | prop | `{"all":[{"flag":"tomas_rebost"},{"hasItem":"comandament","is":false},{"flag":"marcel_comandament","is":false}]}` | pickUp, look |
| `tele` | tele | hotspot / prop | sempre | use + comandament, look |
| `retol` | rètol | hotspot / prop | sempre | look |
| `telefon` | telèfon | hotspot / prop | sempre | talkTo, use, look |
| `porta_rebost` | rebost | hotspot / prop → `bar_rebost` | sempre | use, open, walkTo, look |
| `porta` | sortida | hotspot / prop → `aeroport_terminal` | sempre | use, open, walkTo, look |

### La cuina · `pis_cuina`

| Id | Nom | Tipus | Apareix | Verbs |
|---|---|---|---|---|
| `cafetera` | cafetera | hotspot / prop | sempre | pickUp, pull, use, look |
| `nevera` | nevera | hotspot / prop | sempre | open, close, look, pickUp |
| `pizza_nevera` | pizza | prop | `{"all":[{"flag":"nevera_oberta"},{"hasItem":"pizza","is":false,"who":"vet"},{"hasItem":"pizza","is":false,"who":"iri"},{"var":"sacrifici","op":"!=","value":"pizza"}]}` | pickUp, look |
| `tonyina` | pa i tonyina | prop | `{"all":[{"flag":"nevera_oberta"},{"flag":"te_entrepa","is":false}]}` | pickUp, look |
| `passaplats` | passaplats | hotspot / prop | sempre | open, close, use + cable_alimentacio, use + pizza, use + objecte, talkTo, use, look |
| `plats` | plats | hotspot / prop | sempre | look, use, pickUp |
| `porta` | porta | hotspot / prop → `bar_sala` | sempre | use, open, walkTo, look |

## Sense protagonista

### L'avió · `avio`

| Id | Nom | Tipus | Apareix | Verbs |
|---|---|---|---|---|

### Suma Zero · `portada`

| Id | Nom | Tipus | Apareix | Verbs |
|---|---|---|---|---|

### Ginebra · `proleg_ginebra`

| Id | Nom | Tipus | Apareix | Verbs |
|---|---|---|---|---|

## Objectes d'inventari

| Id | Nom | Pes | Altres |
|---|---|---|---|
| `auriculars` | auriculars | — |  |
| `cable_xarxa` | cable de xarxa | — |  |
| `cable_alimentacio` | cable d'alimentació | — |  |
| `caixa_cartro` | caixa de cartró | — |  |
| `pizza` | pizza | — |  |
| `entrepa` | entrepà | — |  |
| `clau_casa` | clau de casa | — |  |
| `tap` | tap de la cervesera | — |  |
| `recepta` | recepta de la llimonada | — |  |
| `comandament` | comandament | — |  |
| `maleti` | maletí | — |  |
| `ulleres` | ulleres | — |  |
| `acreditacions` | acreditacions | — |  |
| `acreditacio` | acreditació | — |  |
