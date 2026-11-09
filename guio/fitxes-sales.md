# Fitxes de sales

> Generat amb `npm run fitxes` a partir de `game/data/`. No l'editis a mà.

Cada cosa de la llista és un **prop**, un **hotspot** o un **personatge** de la sala a l'editor del motor, amb **aquest id** (o un id del tipus `<sala>-hotspot-<id>`). Les que tenen condició s'han de lligar amb `bindHotspots`.

## Iri

### Sala de calderes · `fabrica_calderes`

| Id | Nom | Tipus | Apareix | Verbs |
|---|---|---|---|---|
| `capatas` | capatàs Tul | personatge | sempre | use + formulari_27be, give + formulari_27be, use + diapaso_espatllat, look, talkTo, pull, pickUp, push, use + plomall, use + objecte |
| `segell` | segell oficial | prop | `{"all":[{"flag":"segell_caigut"},{"flag":"segell_agafat","is":false}]}` | look, pickUp |
| `tauler` | tauler d'anuncis | hotspot / prop | sempre | look, pickUp |
| `alarma` | llum d'alarma | hotspot / prop | sempre | look |
| `porta_magatzem` | magatzem | hotspot / prop → `fabrica_magatzem` | sempre | open, use, walkTo, look |
| `porta_cambra` | porta de la cambra | hotspot / prop → `fabrica_cambra` | sempre | use + objecte, open, use, walkTo, push, pull, use + clau_cambra, look |
| `porta_moll` | moll de càrrega | hotspot / prop → `fabrica_moll` | sempre | open, use, walkTo |
| `sic` | Inspector Sic | personatge | `{"all":[{"flag":"iri_descoberta"},{"flag":"sic_distret","is":false}]}` | talkTo, look |

### Cambra de ressonància · `fabrica_cambra`

| Id | Nom | Tipus | Apareix | Verbs |
|---|---|---|---|---|
| `palanca` | palanca | hotspot / prop | sempre | use + clau_anglesa, pull, push, use, look |
| `cambra` | cambra | hotspot / prop | sempre | look, use + diapaso, use + tub_ferro9, use + objecte, pickUp, open |
| `boto` | botó de sincronia | prop | `{"flag":"alarma_apagada"}` | look, push, use |
| `porta` | sala de calderes | hotspot / prop → `fabrica_calderes` | sempre | open, use, walkTo |
| `reixa` | reixa | hotspot / prop → `fabrica_moll` | sempre | open, use, walkTo, pull, pickUp, push, use + llima, look |

### Despatx del director · `fabrica_despatx`

| Id | Nom | Tipus | Apareix | Verbs |
|---|---|---|---|---|
| `porta_magatzem` | magatzem | hotspot / prop → `fabrica_magatzem` | sempre | open, use, walkTo |
| `calaix` | calaix | hotspot / prop | sempre | use + imant_ferro9, open, pickUp, use, look |
| `expedient_sic` | expedient | hotspot / prop | sempre | use + llapis, look |
| `llibre_inventari` | llibre d'inventari | hotspot / prop | sempre | use + segell, look |
| `retrat` | retrat | hotspot / prop | sempre | look |

### Magatzem d'eines · `fabrica_magatzem`

| Id | Nom | Tipus | Apareix | Verbs |
|---|---|---|---|---|
| `cargol` | Cargol | personatge | sempre | talkTo, use + segell, give + segell, use + llima, give + llima, look, give + objecte, push, pull |
| `plomall` | plomall | prop | `{"hasItem":"plomall","who":"iri","is":false}` | look, pickUp |
| `caixa_eines` | caixa d'eines | prop | `{"hasItem":"caixa_eines","who":"iri","is":false}` | look, pickUp |
| `prestatges` | prestatges | hotspot / prop | sempre | look, pickUp |
| `porta_calderes` | sala de calderes | hotspot / prop → `fabrica_calderes` | sempre | open, use, walkTo |
| `porta_despatx` | despatx del director | hotspot / prop → `fabrica_despatx` | sempre | open, use, walkTo |
| `mira` | Mira | personatge | `{"all":[{"flag":"acte3_iniciat"},{"flag":"mira_salvada"},{"flag":"iri_fugida","is":false}]}` | use + planols, give + planols, talkTo, look |

### Moll de càrrega · `fabrica_moll`

| Id | Nom | Tipus | Apareix | Verbs |
|---|---|---|---|---|
| `porta_calderes` | sala de calderes | hotspot / prop → `fabrica_calderes` | sempre | open, use, walkTo |
| `biga_acer` | biga d'acer | prop | `{"all":[{"hasItem":"biga_acer","who":"iri","is":false},{"flag":"biga_acer_serrada","is":false},{"var":"biga_amagada","op":"!=","value":"acer"}]}` | use + serra, pickUp, look |
| `biga_ferro9` | biga de ferro-9 | prop | `{"flag":"biga_ferro9_robada","is":false}` | pickUp, look |
| `serra` | serra | prop | `{"hasItem":"serra","who":"iri","is":false}` | pickUp, look |
| `trapa` | reixa del terra | hotspot / prop | sempre | use + biga_acer, use + biga_ferro9, open, pickUp, look |
| `llancadora` | llançadora | hotspot / prop | sempre | open, use, push, pull, look |
| `comporta` | comporta | hotspot / prop | sempre | look |
| `llima` | llima | prop | `{"hasItem":"llima","who":"iri","is":false}` | pickUp, look |
| `conducte` | conducte | hotspot / prop | sempre | close, open, use, push, pull, look |
| `pilar` | pilar | hotspot / prop | sempre | use + llima, look |

## Vet

### Arxiu · `gavina_arxiu`

| Id | Nom | Tipus | Apareix | Verbs |
|---|---|---|---|---|
| `escala_hangar` | moll de l'hangar | hotspot / prop → `gavina_hangar` | sempre | open, use, walkTo |
| `expedient_iri` | expedients | hotspot / prop | sempre | look, open, pickUp |
| `arxivador` | arxivador | hotspot / prop | sempre | open, pickUp, use, look |
| `planols` | plànols | hotspot / prop | sempre | look, pickUp, open |
| `carpeta` | carpeta caiguda | prop | `{"flag":"nota_perduda_4","is":false}` | open, pickUp, pull, push, use, look |

### Cel·la 9 · `gavina_cella`

| Id | Nom | Tipus | Apareix | Verbs |
|---|---|---|---|---|
| `panell` | panell rovellat | hotspot / prop | sempre | use + mapa_fuga, use + objecte, push + objecte, look + objecte, use, push, look, pull, pickUp, open, use + clau_anglesa, use + molla |
| `altaveu` | altaveu de la MARE | hotspot / prop | sempre | talkTo, look, push, pull, use |
| `mos` | Mos | personatge | sempre | give + nota_mos, use + nota_mos, give + carta_mos, use + carta_mos, talkTo, look |
| `avis` | avís | prop | `{"flag":"avis_agafat","is":false}` | look, pickUp |
| `llitera` | llitera | hotspot / prop | sempre | pickUp, pull, look |
| `escarabat` | Senyor Bigotis | prop | `{"flag":"escarabat_agafat","is":false}` | look, pickUp |
| `safata` | safata de sopar | prop | `{"flag":"sopa_agafada","is":false}` | look, pickUp |
| `porta` | porta de la cel·la | hotspot / prop → `gavina_passadis` | sempre | open, use, walkTo, push, pull, use + objecte, look, use + imant_ferro9 |
| `finestreta` | finestreta | hotspot / prop | sempre | look |
| `directora` | Directora Aldaia | personatge | `{"flag":"acte3_iniciat"}` | talkTo, look |
| `reixa` | reixa | hotspot / prop → `gavina_hangar` | sempre | open, pull, pickUp, use, push, walkTo, look, use + clau_anglesa |
| `esquerda` | esquerda | prop | `{"flag":"nota_perduda_1","is":false}` | open, pickUp, pull, push, use, look |

### Moll de l'hangar · `gavina_hangar`

| Id | Nom | Tipus | Apareix | Verbs |
|---|---|---|---|---|
| `porta_passadis` | passadís | hotspot / prop → `gavina_passadis` | sempre | open, use, walkTo |
| `comporta` | comporta | hotspot / prop | sempre | look, use + biga_ferro9, use + biga_muntada, use + tram_biga_1, use + tram_biga_2, use + tram_biga_3, use + clau_anglesa, open, push, pull |
| `pilar` | pilar | hotspot / prop | sempre | look |
| `placa_terra` | reixa del terra | hotspot / prop | sempre | open, pickUp, use, look |
| `llancadora` | llançadora | prop | `{"flag":"comporta_oberta"}` | use + tub_amb_llibreta, push, use, look, pull, open |
| `pany` | pany sònic | prop | `{"all":[{"flag":"comporta_oberta"},{"flag":"pany_vist"}]}` | look, use + diapaso, use + molla, push, use, pull, open |
| `conducte` | conducte | hotspot / prop | sempre | look, use, open, close, push, pull |
| `escala` | escala | hotspot / prop → `gavina_arxiu` | sempre | open, use, walkTo, look, use + clau_anglesa |
| `caixa_flotant` | caixa que sura | prop | `{"all":[{"var":"valvula","op":"==","value":"tancada"},{"flag":"caixa_agafada","is":false}]}` | pickUp, open, look |
| `sortida_conducte` | sortida del conducte | prop → `gavina_cella` | `{"flag":"reixa_oberta"}` | open, use, walkTo, pull, look |
| `caixa_recanvis` | caixa de recanvis | prop | `{"flag":"nota_perduda_3","is":false}` | open, pickUp, pull, push, use, look |

### Sala de la Memòria · `gavina_memoria`

| Id | Nom | Tipus | Apareix | Verbs |
|---|---|---|---|---|
| `porta_passadis` | passadís | hotspot / prop → `gavina_passadis` | sempre | open, use, walkTo |
| `holograma` | holograma del Director | hotspot / prop | sempre | talkTo, use, push, look |
| `foto` | foto del torn de nit | hotspot / prop | sempre | look |
| `vitrina` | vitrina | hotspot / prop | sempre | use + clau_vitrina, look, open, pickUp, use |
| `mapa` | mapa de La Gavina | hotspot / prop | sempre | look |
| `fullets` | fullets | hotspot / prop | sempre | pickUp, look |
| `cargol_vell` | Conserge | personatge | sempre | use + placa_cargol, give + placa_cargol, talkTo, look |
| `socol` | sòcol de l'holograma | prop | `{"flag":"nota_perduda_5","is":false}` | open, pickUp, pull, push, use, look |

### Passadís del mòdul C · `gavina_passadis`

| Id | Nom | Tipus | Apareix | Verbs |
|---|---|---|---|---|
| `cartell` | cartell | hotspot / prop | sempre | pickUp, look |
| `camera_vigilancia` | càmera | hotspot / prop | sempre | look |
| `porta_cella` | cel·la 9 | hotspot / prop → `gavina_cella` | sempre | open, use, walkTo |
| `porta_hangar` | porta del fons | hotspot / prop → `gavina_hangar` | sempre | open, use, walkTo |
| `porta_memoria` | Sala de la Memòria | hotspot / prop → `gavina_memoria` | sempre | open, use, walkTo, look |
| `guardia` | Guàrdia d'Orís | personatge | `{"flag":"mira_salvada"}` | talkTo, look |
| `rajola` | rajola solta | prop | `{"flag":"nota_perduda_2","is":false}` | open, pickUp, pull, push, use, look |

## Sense protagonista

### La cambra · `proleg_cambra`

| Id | Nom | Tipus | Apareix | Verbs |
|---|---|---|---|---|

### Cel·la 9 · `proleg_cella`

| Id | Nom | Tipus | Apareix | Verbs |
|---|---|---|---|---|

### La fàbrica · `proleg_fabrica`

| Id | Nom | Tipus | Apareix | Verbs |
|---|---|---|---|---|

### La Gavina · `proleg_gavina`

| Id | Nom | Tipus | Apareix | Verbs |
|---|---|---|---|---|

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
| `imant_ferro9` | imant de ferro-9 | 0.3 | material: ferro9, finestra: iri |
| `nota_iri` | nota d'I. | 0.01 | finestra: iri |
| `avis_reciclatge` | avís de reciclatge | 0.01 |  |
| `llapis_ulls` | llapis d'ulls | 0.01 |  |
| `nota_vet` | nota de la cel·la 9 | 0.01 | finestra: vet |
| `fullet_reeducacio` | fullet de reeducació | 0.01 |  |
| `nota_pany` | dibuix del pany | 0.01 | finestra: vet |
| `escarabat` | escarabat | 0.01 | viu: true |
| `sopa` | sopa | 0.5 | liquid: true |
| `tros_cartell` | tros de cartell | 0.01 |  |
| `nota_mida` | nota de la mida | 0.01 | finestra: vet |
| `biga_acer` | biga d'acer | 40 | material: acer |
| `biga_ferro9` | biga de ferro-9 | 30 | material: ferro9 |
| `serra` | serra | 0.6 |  |
| `tram_biga_1` | tram de biga (1) | 1.8 | material: acer, finestra: iri |
| `tram_biga_2` | tram de biga (2) | 1.8 | material: acer, finestra: iri |
| `tram_biga_3` | tram de biga (3) | 1.8 | material: acer, finestra: iri |
| `biga_muntada` | biga muntada | 5.4 | material: acer |
| `nota_amagatall` | nota del moll | 0.01 | finestra: iri |
| `pols_rovell` | pols de rovell | 0.2 | finestra: vet |
| `molla` | molla | 0.05 | finestra: vet |
| `llima` | llima | 0.3 |  |
| `diapaso` | diapasó | 0.2 | material: ferro9, finestra: iri |
| `diapaso_espatllat` | diapasó espatllat | 0.2 | material: ferro9 |
| `nota_pressio` | nota de la pressió | 0.01 | finestra: vet |
| `nota_massa` | nota «MASSA» | 0.01 | finestra: vet |
| `fitxa_mira` | fitxa de personal | 0.01 |  |
| `planols` | plànols | 0.3 |  |
| `carta_mos` | carta d'en Mos | 0.01 |  |
| `nota_vet_nom` | nota de la Vet | 0.01 | finestra: vet |
| `nota_iri_nom` | nota de l'Iri | 0.01 | finestra: iri |
| `fullet_memoria` | fullet de la Sala de la Memòria | 0.01 |  |
| `mapa_fuga` | mapa de fuga | 0.01 | finestra: vet |
| `tub_ferro9` | tub de ferro-9 | 1.2 | material: ferro9 |
| `tub_amb_llibreta` | tub amb la llibreta | 1.5 | material: ferro9, finestra: iri |
| `clau_vitrina` | clau de la vitrina | 0.05 |  |
| `placa_cargol` | placa de robot | 0.2 |  |
| `formulari_27be` | formulari 27-B/E | 0.01 |  |
| `formulari_27be_signat` | formulari 27-B/E signat | 0.01 |  |
| `carnet_exemplar` | carnet d'usuària exemplar | 0.01 |  |
| `notes_perdudes` | notes perdudes | 0.05 |  |
| `nota_mos` | nota de la cel·la 9 | 0.01 |  |
