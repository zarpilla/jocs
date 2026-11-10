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

### La sala d'escombraries · `bcmu_escombraries`

| Id | Nom | Tipus | Apareix | Verbs |
|---|---|---|---|---|
| `llibre` | Llibre Major | hotspot / prop | sempre | use + clau_llibre, use, push, look |
| `tub` | estació del tub | hotspot / prop | sempre | use + objecte, open, use, pickUp, look |
| `panell` | panell de NETA-3 | hotspot / prop | sempre | use, open, look |
| `conducte` | conducte | hotspot / prop | sempre | use, open, look |
| `bosses` | bosses | hotspot / prop | sempre | pickUp, look |
| `porta` | porta | hotspot / prop → `bcmu_passadis` | sempre | use, open, walkTo, look |

### El moll de càrrega · `bcmu_moll`

| Id | Nom | Tipus | Apareix | Verbs |
|---|---|---|---|---|
| `rius` | Rius | personatge | sempre | talkTo, look |
| `maquina` | màquina de cafè | hotspot / prop | sempre | use, push, pickUp, look |
| `ascensor` | ascensor de servei | hotspot / prop → `bcmu_passadis` | sempre | use, open, walkTo, use + targeta, look |
| `tecnics` | tècnics | hotspot / prop | sempre | talkTo, look |
| `furgonetes` | furgonetes | hotspot / prop | sempre | use, open, look |

### El passadís del tercer pis · `bcmu_passadis`

| Id | Nom | Tipus | Apareix | Verbs |
|---|---|---|---|---|
| `neta` | NETA-3 | personatge | sempre | talkTo, use + entrepa, use + entrepa_suis, use + entrepa_ballester, look |
| `camera1` | càmera | hotspot / prop | sempre | use + galleda, use + extintor, use + cartell, look |
| `camera2` | càmera del racó | hotspot / prop | sempre | use + cartell, use + extintor, use + galleda, look |
| `galleda` | galleda | prop | `{"all":[{"hasItem":"galleda","who":"iri","is":false},{"flag":"camera2_tapada","is":false}]}` | pickUp, look |
| `cartell` | cartell | prop | `{"all":[{"hasItem":"cartell","who":"iri","is":false},{"flag":"camera1_tapada","is":false}]}` | pickUp, look |
| `extintor` | extintor | prop | `{"hasItem":"extintor","who":"iri","is":false}` | pickUp, look |
| `porta_neteja` | porta de neteja | hotspot / prop → `bcmu_escombraries` | sempre | use, open, walkTo, look |
| `porta_escala` | porta de l'escala | hotspot / prop | sempre | use, open, look |
| `porta_vip` | porta VIP | hotspot / prop | sempre | use, open, walkTo, look |
| `tub` | estació del tub | hotspot / prop | sempre | use + objecte, open, use, pickUp, look |
| `ascensor` | ascensor de servei | hotspot / prop | sempre | use, open, look |

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

### La sala de seguretat · `bcmu_seguretat`

| Id | Nom | Tipus | Apareix | Verbs |
|---|---|---|---|---|
| `ballester` | Ballester | personatge | sempre | talkTo, look |
| `monitors` | monitors | hotspot / prop | sempre | look |
| `radio` | ràdio | hotspot / prop | sempre | look, use, pickUp, push |
| `got` | got | hotspot / prop | sempre | use, push, pickUp, look |
| `entrepa` | entrepà d'en Ballester | prop | `{"flag":"entrepa_b_agafat","is":false}` | pickUp, look |
| `clauer` | clauer | prop | `{"flag":"clauer_agafat","is":false}` | pickUp, look |
| `collaret` | collaret | prop | `{"all":[{"flag":"aliat_ballester"},{"flag":"clau_agafada","is":false}]}` | pickUp, look |
| `tub` | estació del tub | hotspot / prop | sempre | use + objecte, open, use, pickUp, look |
| `ascensor` | ascensor | hotspot / prop → `bcmu_vestibul` | sempre | use, open, walkTo, look |

### El vestíbul del BCMU · `bcmu_vestibul`

| Id | Nom | Tipus | Apareix | Verbs |
|---|---|---|---|---|
| `bonfill` | Director | personatge | `{"flag":"auditoria_acceptada","is":false}` | talkTo, look, give + objecte |
| `font` | font | hotspot / prop | sempre | use, pickUp, look |
| `cartell` | cartell | hotspot / prop | sempre | look |
| `retrat` | retrat | hotspot / prop | sempre | look |
| `recepcio` | recepció | hotspot / prop | sempre | talkTo, look |
| `tub` | estació del tub | hotspot / prop | sempre | use + objecte, open, use, pickUp, look |
| `maquina` | màquina d'entrepans | hotspot / prop | sempre | use, pickUp, push, look |
| `plantes` | plantes | hotspot / prop | sempre | look |
| `ascensor` | ascensor | hotspot / prop → `bcmu_seguretat` | sempre | use, open, walkTo, look |
| `sortida` | sortida | hotspot / prop | sempre | use, open, walkTo, look |

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
| `auriculars` | auriculars | — | no_enviar: tub.auriculars |
| `cable_xarxa` | cable de xarxa | — |  |
| `cable_alimentacio` | cable d'alimentació | — |  |
| `caixa_cartro` | caixa de cartró | — |  |
| `pizza` | pizza | — |  |
| `entrepa` | entrepà | — | cap_al_tub: true, tub_per: iri, tub_fins: robot_aturat |
| `clau_casa` | clau de casa | — | no_enviar: tub.clau_casa |
| `tap` | tap de la cervesera | — | cap_al_tub: true |
| `recepta` | recepta de la llimonada | — | cap_al_tub: true |
| `comandament` | comandament | — |  |
| `maleti` | maletí | — |  |
| `ulleres` | ulleres | — | cap_al_tub: true |
| `acreditacions` | acreditacions | — |  |
| `acreditacio` | acreditació | — | cap_al_tub: true |
| `entrepa_suis` | entrepà suís | — | cap_al_tub: true, tub_per: iri, tub_fins: robot_aturat |
| `entrepa_ballester` | entrepà d'en Ballester | — | cap_al_tub: true, tub_per: iri, tub_fins: robot_aturat |
| `targeta` | targeta de planta | — | cap_al_tub: true |
| `compte_nomines` | compte de nòmines | — | cap_al_tub: true |
| `galleda` | galleda | — |  |
| `cartell` | cartell | — |  |
| `extintor` | extintor | — |  |
| `clau_llibre` | clau del Llibre Major | — | cap_al_tub: true, tub_per: iri |
| `clauer` | clauer | — | cap_al_tub: true |
