# Aigua Verne — fitxes de les sales

> El contracte entre el contingut (`game/data/rooms/<sala>.json`) i l'art (`adapters/benne/tools/hd640/rooms/<sala>.py`).
> Els **ids** d'aquí (sales, coses, decorats, personatges) són els del JSON i els de la `GEOMETRIA` de l'art: si en
> canvia un, s'ha de canviar als dos llocs.

## Normes d'art

- **Resolució 640×360.** La sala ocupa 640×260 (y de 0 a 259); a sota hi ha la barra de verbs (y 260–359). Res
  important per sota de y≈258.
- **Dues mides de càmera** (guió, «Art: dues mides de càmera»):
  - **L (de lluny):** persones de ≈83 px (fotograma 49×87, peus a (25, 83)). Exteriors i sales grans. El terra per
    on es camina, entre y≈200 i y≈255. Les portes i els mobles, a l'escala d'una persona de 83 px.
  - **P (de prop):** persones de ≈100 px. Interiors petits. Terra entre y≈225 i y≈257. Portes de ≈125 px d'alt.
- **Estil:** el de la mostra (`guio/art/mostra/granja_pati.py`) i el de Ni un ou (`hd/pix.py`: rampes fosc→clar,
  llum de sala amb `Light`, dithering, contorns de 1 px). Res de degradats llisos ni antialiasing.
- **Cada planeta, una llum i una paleta:**
  - **Terra-2:** pols ocre, cel groguenc sense núvols, sol dur a dalt a la dreta (ombres cap a l'esquerra).
  - **Cantimplora:** nau cisterna vella, planxa verd oliva i taronja de seguretat, llums càlids de filament, rovell.
  - **Aqua:** blanc de sal i blau pàl·lid, port de pedra, vaixells encallats, el fons del mar sec (sorra blanca,
    algues seques, ossos de peix). Llum freda, migdia.
  - **Ferrum:** ferro, rovell, carbó, cel de fum taronja-grisenc; la fosa, foc i ombres llargues.
  - **Verdant:** verds massa saturats (de plàstic), blancs nets, cel blau d'anunci. Tot brilla massa.
  - **Palau orbital:** blanc i or, vidre, l'espai negre per les finestres; les piscines, turquesa buit (rajola).
- **El lema de Verne** («AIGUA VERNE») i la **gota blava** (logotip) surten a tots els panells i a les màquines de
  Verne. El **panell del preu** (pantalla negra amb lletres taronja: «48 ▲») és a gairebé tots els exteriors.
- **Les Canonades** (columnes blanques fins al cel) es veuen a l'horitzó de Terra-2, Aqua i Ferrum.
- Cada sala és un mòdul amb `LIGHT`, `bg(cv)`, `PROPS` (fotogrames de les coses condicionals i dels decorats),
  `ANIMS` (opcional) i `GEOMETRIA` (`things`: id → `{'rect': (x0, y0, x1, y1), 'walk': (x, y)}`; `spawns`:
  personatge → peus; `walkable`: polígon). Coordenades reals de 640×360. Les sortides també són `things`.

## Llegenda

- **Cosa** (hotspot): es clica. Si duu *(prop)*, es mostra o s'amaga segons l'estat: cal un fotograma a `PROPS`.
- **Decorat** (*decor*): un dibuix que es posa damunt el fons segons l'estat, no es clica: també a `PROPS`.
- **Personatges**: on són (`spawns`), amb la mida de la sala.

---

## Cinemàtiques

### `portada` (L)
La portada. Terra-2 vista de lluny al capvespre de pols, la Canonada al mig fins al cel, i a dalt, en òrbita, un
dels dipòsits (un cilindre blanc amb la gota blava). A baix, petita, la Cantimplora aparcada. El títol **AIGUA
VERNE** com una etiqueta d'ampolla d'aigua (blau i blanc), una mica rovellada. Deixar espai a baix per als botons
«Comença» i «Carrega una partida». ANIMS: la pols que passa, el llum de la Canonada que fa pampallugues.

### `proleg_palau` (P)
El despatx del Magnat al palau orbital. Paret de vidre amb l'espai i Terra-2 de fons; un focus i una càmera
d'anunci (trípode) apuntant a la taula; la taula blanca; l'aquari (trenta-tres peixos platejats) a la dreta; a terra,
a través d'un tros de vidre, la piscina central buida (rajola turquesa). Panell del preu: decorats `preu46` i `preu48`.
Decorat `focus_apagat` (el focus s'apaga després de l'anunci). Personatges: `verne` (darrere la taula), `dividend`
(al costat de la piscina). ANIMS: els peixos que neden.

### `final_pluja` (L)
El pati de la granja (`granja_pati`) tres setmanes després, **plovent**: cel gris, bassals, el pou amb aigua fins a
dalt, la bomba de Verne apagada i amb un cartell «BANC DE VESPER». ANIMS: la pluja i els cercles als bassals.
Personatges: `iri`, `vet`, `quim` (el pare, a la porta, assegut en una cadira, amb un paraigua tancat), `diu`.
Decorats `barril_pou` (el barril de la Cantimplora al costat del pou) i `caixa_ferrum` (una caixa de fusta amb el
segell de Ferrum).

### `credits` (L)
Fons per als crèdits: el sistema de Vesper de nit, amb els quatre planetes petits i núvols de pluja damunt de tres.

### `postcredits` (L)
Ferrum, la plaça amb la font pública que raja. Una cua de miners. Al final de la cua, `verne` (vestit blanc brut,
`dividend` en braços). Davant seu, `rosa`. El panell: «AIGUA VESPER · 4 ▲».

---

## Terra-2

### `granja_pati` (L) — Escena 1
La mostra (`guio/art/mostra/granja_pati.py`): s'hi parteix.
- `porta_casa` → `granja_casa` · `porta_graner` → `granja_graner` · `cami_port` (el camí de la dreta, cap al port) →
  `port_terra2`
- `pou` (pedra, politja, galleda seca) · `bomba` (la bomba de Verne; decorat `bomba_oberta`: el panell obert, amb
  l'etiqueta) · `canonada` · `panell_preu` · `arbre` (l'olivera morta) · `tanca`
- Personatges: `iri`, `vet`, `diu` (a la vora del pou, només a l'Escena 1).

### `granja_casa` (P) — la cuina i el despatx del pare
Una masia per dins: a l'esquerra la cuina (foc a terra apagat, pica seca, prestatges plens de pots de vidre buits),
a la dreta el despatx (taula amb calaixos plens, el quadre de la mare, el videotelèfon vell a la paret).
- `porta` → `granja_pati` · `calaix` (la taula del despatx) · `videotelefon` · `quadre` (el retrat de la mare; prop:
  es veu fins que s'aparta) · `caixa_forta` (prop: es veu quan el quadre s'ha apartat; decorat `caixa_oberta`) ·
  `bol` (el bol del gos a terra, amb «TITUS» gravat) · `pots` (els setanta pots) · `pica`
- Decorat `quadre_apartat` (el quadre, recolzat a terra).

### `granja_graner` (P)
Fusta, pols en els raigs de llum, el tractor vermell de l'avi (Brau 40), el banc de llavors (sacs de tela ordenats en
prestatges, etiquetes a mà), el reg gota a gota enrotllat a la paret, una caixa d'eines.
- `porta` → `granja_pati` · `tractor` (decorat `tractor_obert`: el capó aixecat, sense l'injector) · `llavors` (el
  banc; decorats `sacs_tres`: tres sacs a terra, es veuen fins que es carreguen, i `sac_quart`: el quart sac, fins
  que s'agafa) · `reg` (prop: fins que s'agafa) · `caixa_eines`

### `port_terra2` (L)
Un port de naus de càrrega de terra batuda, mig buit: una grua parada, contenidors amb el logotip de Verne. La
**Cantimplora** a la dreta: una nau cisterna panxuda, oliva i taronja, rovellada, amb nou dipòsits rodons i la rampa
de la bodega oberta. Un tauler d'anuncis de suro ple de papers de Verne S.A.
- `cami_granja` (esquerra) → `granja_pati` · `rampa` → `cantimplora_bodega` · `tauler` · `panell_preu` · `canonada`
- Personatges: cap.

---

## La Cantimplora

### `cantimplora_pont` (P)
La cabina de comandament: dos seients gastats, la consola amb botons i palanques, el **mapa de navegació** (una
taula de vidre amb els planetes de Vesper), la ràdio, la **pantalla** gran (apagada; decorat `pantalla_verne`: la cara
del Magnat, quan truca a l'Escena 6), el finestral. Pel finestral es veu on és la nau: decorats `vista_terra2`,
`vista_aqua`, `vista_ferrum`, `vista_verdant` (un fotograma per planeta, que es veu des del port).
- `escala` → `cantimplora_bodega` · `mapa` · `radio` · `pantalla` · `finestral` · `seient` (el de la Capitana)
- Personatges: `capitana` (dreta, al costat de la consola), `iri`, `vet`.

### `cantimplora_bodega` (P)
La bodega: la rampa (al fons, oberta a la llum del planeta: decorats `llum_terra2`, `llum_aqua`, `llum_ferrum`,
`llum_verdant`), dipòsits rodons buits amb portelles, al mig **l'últim barril** fermat amb cadenes i el rètol «NO. PER
SI DE CAS.», la cuineta (un fogó, una cafetera, una nevera petita), el calaix de la Vet (un moble de calaixos que no
tanquen), el tauler de suro de la cuina (paperets), el banc d'en Tomàs amb la seva carmanyola, el motor (un panell
obert de la sala de màquines al fons) i el quadre elèctric amb fusibles.
- `rampa` → el port del planeta on és la nau · `escala` → `cantimplora_pont`
- `barril` (prop: es veu si no s'ha donat) · `calaix` · `cafetera` · `nevera` · `tauler` · `carmanyola` · `motor`
  (decorat `motor_obert`) · `fusibles` · `diposit` (on dorm en Diu) · `carrega` (l'espai de càrrega, on van les
  llavors; decorat `sacs_carregats`)
- Personatges: `tomas` (al banc), `diu` (dins el dipòsit; a l'Escena 6, damunt la carmanyola: decorat
  `diu_carmanyola`, i el personatge s'amaga), `iri`, `vet`.

---

## Aqua

### `aqua_port` (L)
El port d'un planeta que era mar: un moll de pedra blanca de sal, vaixells encallats i inclinats sobre la sorra, i
l'**escala del port que s'acaba a l'aire**, quaranta metres per sobre del fons. Una grua de port vella amb una
cistella de peix penjada. Al fons, la Canonada d'Aqua. La Cantimplora, aparcada a l'esquerra (només la rampa).
- `rampa` → `cantimplora_bodega` · `escala_port` · `grua` (decorat `grua_arreglada`: llum verd a la cabina) ·
  `cistella` → `aqua_fons` (quan la grua funciona) · `vaixells` · `panell_preu` · `canonada`

### `aqua_fons` (L)
El fons de l'antic mar, vist des de baix: el moll és una paret alta al fons, amb la cistella que hi baixa. Sorra
blanca, nanses i xarxes velles, un bassal (l'única aigua), boies de mesurar amb números pintats, i a la dreta la
casa de la Juana (una caseta feta amb un casc de vaixell bolcat, amb finestra rodona i llum a dins). Una platja de
**sorra fina** (prop: `sorra`, sempre es veu).
- `cistella` → `aqua_port` · `porta_juana` → `casa_juana` · `nanses` · `boies` · `bassal` · `sorra` · `ossos`

### `casa_juana` (P)
L'interior del casc bolcat: costelles de fusta, llibres per tot arreu, mapes del mar clavats a les parets amb línies
de nivell (cada any més avall), un aquari buit amb un rètol «PER QUAN TORNIN», una làmpada.
- `porta` → `aqua_fons` · `mapes` · `llibres` · `aquari` · `finestra`
- Personatges: `juana` (asseguda a la taula).

---

## Ferrum

### `ferrum_carrer` (L)
Un carrer de miners: cases de maó ennegrit, el cel de fum. Un **piquet**: pancartes («QUI NO TREBALLA NO BEU»
ratllat i, a sota, «QUI NO BEU NO TREBALLA»), una foguera en un bidó, canalla asseguda. La **font** de Verne (blanca,
amb un lector de targetes vermell, seca). El **condensador** vell de la mina (una màquina de llauna amb aletes;
decorat `condensador_arreglat`: llum verd i una aixeta que goteja). Una pila de **comptadors** d'aigua arrencats. El
sindicat (porta) i la fosa (portal gran) al fons.
- `rampa` → `cantimplora_bodega` · `porta_sindicat` → `ferrum_sindicat` · `porta_fosa` → `fosa_forn` · `font` ·
  `condensador` · `piquet` · `comptadors` · `panell_preu` · `canonada`
- Decorat `barril_piquet` (l'últim barril, al piquet, amb gots).
- Personatges: `rosa` (al piquet).

### `ferrum_sindicat` (P)
El local del sindicat: taules llargues, cartells de vagues antigues, una pissarra, una estufa. Al fons, el **bagul**
de la colla de teatre, obert, amb el vestit de reina de vellut granat (decorat `vestit`: es veu fins que s'agafa).
Una prestatgeria amb motlles de fosa.
- `porta` → `ferrum_carrer` · `bagul` · `pissarra` · `motlles` · `cartells`
- Personatges: `bru` (a la taula).

### `fosa_forn` (L)
La fosa per dins: una nau alta i fosca, el forn gran (boca de foc; decorats `forn_ences` i `forn_fort`), la **manxa**
(una palanca gran), una pila de comptadors per fondre, un rascle per a l'escòria, un termòmetre de rellotge gran.
- `porta` → `ferrum_carrer` · `pas` → `fosa_colada` · `forn` · `manxa` · `metall` (la pila) · `rascle` ·
  `termometre`

### `fosa_colada` (L)
La mateixa nau, l'altra banda: el pont grua amb el **gresol** penjat, el **llit de colada** (on va el motlle de tres
claus), sacs de sorra. Decorats: `motlle_posat`, `motlle_preparat` (amb sorra), `gresol_ple` (lluu taronja),
`claus_fetes` (tres claus brillant).
- `pas` → `fosa_forn` · `gresol` · `grua_pont` (els comandaments) · `llit` · `sorra_pedra`

---

## Verdant

### `verdant_jardi` (L)
El jardí de la residència d'estiu: gespa artificial perfecta, parterres de flors de plàstic de colors massa vius,
aspersors que fan boira de perfum, la façana blanca de la residència amb una porta de vidre (i **en Fidel**, un
robot majordom, al davant), el cobert del jardiner (fusta pintada de verd), una reixa a terra on degota l'aire
condicionat (decorat `galleda_reixa`), el panell del preu, i a l'esquerra, la rampa de la Cantimplora.
- `rampa` → `cantimplora_bodega` · `porta_residencia` → `verdant_residencia` · `porta_cobert` → `verdant_cobert` ·
  `flors` · `aspersors` · `reixa` · `panell_preu` · `llancadora` (la plataforma de la llançadora dels jardiners)
- Personatges: `nil` (entre les flors), `fidel` (a la porta).

### `verdant_cobert` (P)
El cobert d'en Nil: eines de jardí, sacs d'adob de plàstic, un tamboret, i al racó, amagada, **la tomaquera**: una
mata de tomàquet de debò, mig seca, en un test. Decorats `reg_muntat` (els tubs del reg fins al test) i
`tomaquera_viva` (verda, amb tomàquets). Una galleda (prop: fins que s'agafa).
- `porta` → `verdant_jardi` · `tomaquera` · `galleda` · `sacs` · `eines`

### `verdant_residencia` (P)
El despatx d'estiu del Magnat: tot blanc, una calaixera, una paperera daurada, un arxivador amb calaixos amb
etiquetes («DEUTORS», «DRETS», «PEIXOS»), un quadre enorme del Magnat amb en Dividend, un finestral al jardí.
- `porta` → `verdant_jardi` · `calaixera` · `paperera` · `arxivador` · `quadre` · `finestral`

---

## El palau orbital

### `palau_galeria` (L)
Una galeria llarga amb **vint-i-tres piscines** en terrasses (rajola turquesa, totes buides, amb escales cromades),
finestrals a l'espai, columnes blanques, i l'**aquari** (trenta-tres peixos d'Aqua) amb el rètol «LOT 12». Decorat
`piscines_plenes` (per a la cinemàtica final: aigua a totes). La porta del saló.
- `porta_salo` → `palau_salo` · `piscines` · `aquari` · `finestral` · `escales`
- Personatges: `verne` (abans de la subhasta), `dividend` (amb banyador, a la vora de la piscina central).

### `palau_salo` (L)
El saló de la subhasta: cadires daurades, inversors (dibuixats al fons, no clicables), un escenari amb faristol i
martell, una **pantalla** gegant amb el gràfic del preu (decorats `grafic_112`, `grafic_84`, `grafic_52`, `grafic_31`,
`grafic_29`: la línia baixa, i la ratlla vermella «LLINDAR DEL BANC» a 30), una taula amb copes de cava i la
**safata**.
- `porta_galeria` → `palau_galeria` · `escenari` · `pantalla` · `safata` · `cava` · `martell`
- Personatges: `verne` (a l'escenari, a l'Acte 3 durant la subhasta), `holm`, `kessel`.

### `palau_servei` (P)
Els passadissos de servei: parets llises grises, canonades, carros de neteja, l'**ascensor de servei** (porta d'acer
amb lector de targetes), el passaplats on els cambrers deixen les **safates** (prop: `safates`, sempre), el carro de
flors de plàstic d'en Nil.
- `ascensor` → `palau_control` (amb la targeta) · `safates` · `carro` · `canonades`
- Personatges: `lia` (amb un pal de fregar), `nil` (al costat del carro).

### `palau_control` (P)
La sala de control, sota la piscina central: el sostre és el fons de vidre de la piscina (buida). Un tauler amb tres
**panys** grans (rètols T2, AQUA, FERRUM; decorats `obert_t2`, `obert_aqua`, `obert_ferrum`: llum verd i agulla al
màxim) i una **palanca vermella** «RESERVA» (decorat `reserva_oberta`). Un interfon, una càmera (decorat
`flors_camera`: flors de plàstic tapant-la), pantalletes amb els dipòsits.
- `ascensor` → `palau_servei` · `pany_t2` · `pany_aqua` · `pany_ferrum` · `palanca` · `interfon` · `camera`

---

## Personatges

Tots tenen les dues mides (vegeu el guió, «Art»): l'etiqueta normal és la de prop (≈100 px), i amb el prefix `Lluny`,
la de lluny (≈83 px). L'Iri té, a més, la roba `Gala` (el vestit de reina i la corona d'engranatge) a l'Acte 3.

| id | Qui | Com és |
|---|---|---|
| `iri` | La pilot | Vegeu `guio/art/mostra/personatges.py`. Roba `Gala`: vestit de vellut granat fins als peus, lluentons de llautó, corona d'engranatge. |
| `vet` | L'enginyera | Vegeu `guio/art/mostra/personatges.py`. |
| `diu` | El gat | El de sempre (tigrat amb pitet blanc). |
| `capitana` | Capitana Or, 60 | Alta, cabell blanc curt, **pegat a l'ull**, abric llarg de capità blau fosc amb botons de llautó, gorra vella. |
| `tomas` | Tomàs, 22 | Prim, cabell negre arrissat, granota taronja de mecànic massa gran, mocador vermell al coll. |
| `juana` | Juana, 45 | Cabell gris recollit amb un llapis, ulleres rodones, armilla de pescador amb butxaques, botes d'aigua. |
| `bru` | Bru, 58 | Corpulent, calb, bigoti gris, davantal de cuir de fonedor, braços forts. |
| `lia` | Lia, 24 | Uniforme blanc de servei del palau, cabell negre curt, pal de fregar. |
| `rosa` | Rosa, 55 | Minera: casc amb llum, jaqueta de treball gastada, cabell vermellós. |
| `nil` | Nil, 70 | Jardiner: barret de palla, granota verda, barba blanca, tisores de podar. |
| `verne` | Aurelià Verne, 67 | Alt i prim, vestit blanc impecable, cabell blanc pentinat enrere, ungles perfectes, somriure. Roba `Brut` (postcrèdits): el mateix vestit brut i arrugat. |
| `dividend` | El gos | Petit, blanc, pentinat, amb un banyador de ratlles. Roba `Moll`: xop. |
| `fidel` | El majordom robot | Cos de cilindre blanc amb llacet, cap de pantalla amb dos ulls, braços prims. |
| `holm` | Director del Banc | Vestit gris fosc, ulleres primes, cabell engominat. |
| `kessel` | Magnat de l'aire | Dona gran amb abric de pells sintètiques blau, collar de perles, una mascareta d'oxigen daurada al coll. |
| `quim` | El pare, 82 | Jersei de llana, gorra, molt prim. Només a la cinemàtica final (al videotelèfon, a la pantalla). |
