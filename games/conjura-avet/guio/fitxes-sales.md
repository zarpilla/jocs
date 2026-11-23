# La Conjura de l'Avet — fitxes de les sales

> El contracte entre el contingut (`game/data/rooms/`) i l'art (`adapters/benne/tools/hd640/rooms/<sala>.py`). Els ids
> de les coses, dels decorats i dels personatges han de ser **exactament** els del JSON: el sync els lliga per id. Si
> l'art necessita una cosa nova, primer s'afegeix al contingut.
>
> **Escrit a mà.** No executis `npm run fitxes` en aquest joc: reescriu aquest fitxer sencer.
>
> Pantalla de 640×360; l'escena es pinta fins a y = 260 (a sota, el HUD), i la pantalla s'adapta a 640×288
> (`hd640/pantalla.py`). Els personatges són adults: a les sales «de lluny» fan ≈84 px (l'Iri) i ≈78 (la Vet); «de
> prop», ≈110 i ≈102. Es decidirà del tot en fer els fulls (fase 8), abans de pintar les sales. Direcció d'art: el
> [pla](pla.md) («Direcció d'art») i les fotos de [art/referencia/](art/referencia/). La sala de mostra serà
> **`mur_avet`**.
>
> **Dues llums, sempre.** Fora: la pedra rosada i ocre del gres, el verd fosc de l'avet, el cel de tempesta o de
> sol. Dins el monestir, de nit: foc, espelmes i torxes, càlid i amb racons foscos. L'únic **vermell** viu del joc és
> la cera dels segells (la de l'Emma, la del jutge, el lacre del bagul): l'ull l'ha de trobar sempre.

## 1. `mur_avet` — L'avet caigut (actes 1 i 4; les dues)

- **Referència:** `absis-tardor-avet.png` (la llum) i `avet-caigut.png` (l'arbre contra l'absis).
- **Quan i llum:** matí, plugim, cel blanc i pla. Llum difusa, sense ombres marcades; la pedra fosca de mullada i el
  terra amb bassals que reflecteixen el cel (`characterReflection` als bassals). Càmera de lluny, en 3/4.
- **Composició:** l'`absis` a la dreta, en 3/4, amb les arcuacions i la finestra. L'`avet` travessa la sala en
  diagonal, de dalt a l'esquerra cap al mig, ajagut damunt el `mur` esbotzat de l'hort. A l'esquerra, les `arrels`
  aixecades com una paret de terra (més altes que l'Iri), i a sota, el `forat`. Les `branques` escampades pel carrer
  tapen el pas cap a les arrels. És la cosa més gran del joc: l'avet ha de fer petit l'absis.
- **Coses:** `absis`, `mur`, `avet`, `branques`, `branca_trencada` (una branca esqueixada que regalima resina, ambre
  sobre el verd), `arrels` (el tall net del costat del vent ha de ser visible de prop: una cara plana i clara entre
  arrels arrencades), `forat`, `cera` (un punt vermell al fang del fons del forat), `faristol` (el faristol de viatge
  del jutge, amb l'`ordre`: un pergamí amb un segell vermell i el signe al peu).
- **Sortides** (des del final del tutorial): `carrer` a l'esquerra (la plaça), `cami_riu` al fons a l'esquerra, entre
  les branques (el pont), `porta_monestir` a la dreta, a l'absis (el claustre).
- **Decorats:** `branques_apartades` (les branques del pas, apartades a banda i banda); `cera_agafada` (sense el punt
  vermell).
- **Personatges:** `ponc` al faristol; `sunifred` al costat, amb el tinter; `ramon` amb la corda i l'olla; `bonfill`
  avorrit, recolzat a l'absis. En Ramon i en Bonfill surten de la sala al final del tutorial (`stage`). L'Iri entra
  amb el pare per la dreta (`walkIn`); la Vet arriba pel `carrer`.
- **A l'acte 4 (el matí del judici, abans del judici):** la mateixa sala amb la llum del `judici` (decorat
  `llum_mati`), el poble que s'aplega (figures de fons, `poble_aplegant`), el jutge al faristol i en Sunifred. Les dues
  germanes, disfressades. Les mateixes sortides.

### `judici` — El judici (acte 4, Vet; l'Iri hi és)

- **L'art de `mur_avet`, amb un altre estat.** Referència: `absis-avet.png`. Matí de sol net després de la tempesta,
  cel blau, ombres llargues i dures cap a l'esquerra (el sol ve de la dreta, darrere l'absis). Tot moll i brillant.
- **Canvis:** el poble al voltant (figures de fons, sense animar, a dues files: les dones de la Sança a l'esquerra,
  les monges a la dreta, davant l'absis); el faristol al mig; les branques ja apartades.
- **Coses:** les mateixes `arrels`, `avet` i `faristol`; a més, `poble` (les figures del fons) i `monges`.
- **Personatges:** `ponc`, `sunifred`, `bonfill`, `ramon` (lligat, al costat d'en Bonfill), `ingilberga`, `gueraula`,
  `sanca`, `joanet`, `ermessenda`, i la **Iri** (sala compartida: necessita un lloc a `spawns`). Les dues germanes,
  disfressades fins a la revelació.

### `epileg` — L'epíleg (Iri; la Vet hi és)

- **L'art de `mur_avet`, a la primavera.** Matí tebi, verd tendre, flors a l'hort; el `mur` arreglat (pedra nova, més
  clara); el tronc de l'avet tallat en `rodanxes` apilades; les arrels velles encara al seu lloc, amb molsa.
- **Coses:** `forat_nou` (al costat de les arrels velles), `carretilla` amb el `planco`, `pala` (la porta en
  Sunifred fins que la dona a l'Iri), `rodanxes`,
  `arrels`, `absis`.
- **Decorats:** `forat_gran` (el forat eixamplat); `planco_plantat` (el plançó al forat, amb la cinta i el segell
  vermell del jutge quan ja l'ha posat: `segell_planco`); `rotul` (el tros de fusta amb «AVET», clavat al costat).
- **Personatges:** `ponc` amb el faristol, `sunifred` amb la galleda, `ramon`, `ingilberga`, `gueraula`, `sanca`, i
  la **Vet**. Sense disfressa.

## 2. `placa_sant_pol` — La plaça de Sant Pol (actes 1 i 4; les dues)

- **Referència:** `sant-pol-sense-parets.png`.
- **Quan i llum:** migdia, ha parat de ploure; cel trencat, amb un raig de sol que entra per la nau oberta. Càmera de
  lluny, **sala ampla amb scroll** (≈960 px), amb parallax lleu.
- **Composició, d'esquerra a dreta:** la façana de `sant_pol` amb la `porta_sant_pol` i la `llinda` («BERNARDUS COMES
  FECIT», en lletres grosses, llegible); la `queixa` clavada a la porta, amb el segell vermell; el `campanar`, amb la
  `campana` a la `finestra_campanar`; la `nau` sense parets, oberta al cel, amb gespa, on seuen les dones; a la dreta,
  la plaça i la `casa_batlle`, amb la `reixa` del celler arran de terra.
- **Coses:** `llinda`, `porta_sant_pol`, `queixa`, `campanar`, `campana`, `nau`, `dones` (figures que filen),
  `casa_batlle`, `reixa`.
- **Decorats:** `corda_campana` (la corda de cànem que penja del campanar); `iri_dalt` (l'Iri a la finestra del
  campanar: no és el personatge, és un decorat amb animació de saludar i d'estirar la corda); `campana_toca`
  (animació: la campana que es gronxa).
- **Sortida:** `carrer` a la dreta (l'avet).
- **Personatges:** `bonfill` davant la porta (surt corrent cap al peu del campanar quan toca la campana, i s'hi queda
  mentre l'Iri és dalt); `sanca` a la nau. Les dues germanes, on siguin (sala de les dues: totes dues necessiten un
  lloc a `spawns`). En Ramon no es veu: parla des de la reixa (veu, sense sprite a la sala).
- **A l'acte 4:** matí de sol (decorat `llum_mati`); la corda ja és al campanar; la queixa ja no hi és (la té el
  jutge); en Bonfill no hi és (és al judici); la Sança i les dones, a la gespa, fins que s'aixequen per anar al judici
  (`dones_marxen`).

## 3. `pont_ter` — El Pont Vell (actes 1 i 4; Iri)

- **Referència:** `pont-vell.png`.
- **Quan i llum:** primera hora de la tarda; núvols que s'obren, llum grisa i verda. El riu baixa crescut, amb
  escuma (animació per codi). Càmera de lluny, des dels horts, mirant el pont de biaix.
- **Composició:** l'arc gran del `pont` ocupa la meitat de dalt; a sota, la `resclosa` en diagonal, amb el
  `sobreeixidor` (una post de fusta) i la `comporta` del `rec` a la dreta; el `rec` (buit) se'n va cap al molí, que es
  veu lluny. Al primer pla, els `horts` i el `salze` (en silueta, `FRONT`).
- **Coses:** `pont`, `riu`, `resclosa`, `sobreeixidor`, `comporta` (al mig de la resclosa, lluny de la vora: s'hi
  arriba amb barca), `serra` (un brill de ferro sota l'aigua; sencera quan baixa l'aigua), la `barca` d'en Joanet (a
  la vora, mig enfonsada; a sobre, el `salabre`), `rec`, `horts`, `salze`, `moli_lluny`.
- **Sortida:** `cami` a l'esquerra (l'avet). Si la Vet hi arriba, s'excusa aquí i no entra.
- **Decorats:** `sobreeixidor_obert` (la post aixecada, l'aigua que s'escola); `aigua_baixa` (l'aigua de la resclosa
  més baixa, la comporta i la serra al descobert); `barca_calafatada` (la barca surant, amb la resina brillant a les
  juntes); `barca_comporta` (la barca amarrada a la comporta, quan l'Iri hi és); `serra_treta`; `rec_ple` (l'aigua
  torna al rec).
- **Personatges:** `joanet` a la vora, assegut a la barca enfonsada, amb la canya; `ermessenda` a la vora del rec,
  amb el sac.
- **A l'acte 4:** matí de sol, el riu ja manso (decorat `llum_mati`, `riu_manso`); en Joanet dorm a la barca, que
  sura (`joanet_dorm`), i en empènyer-la, la barca és al mig del riu (`barca_corrent`); l'Ermessenda al molí, amb la
  mola rodant (`rec_ple`) fins que l'Iri tanca la `comporta`.

## 4. `claustre` — El claustre (actes 1, 2 i 4)

- **Referències:** `claustre-1.png`, `claustre-2.png` (la galeria en perspectiva), `claustre-campanar.png` (el
  campanar al fons), `claustre-pica.png` (la pica al mig).
- **Quan i llum:** tarda, després de la pluja; cel blanc, gotes que cauen de les teulades (animació). Càmera de prop,
  **des de dins la galeria**: les columnes fosques en primer pla (`FRONT`), el sostre de fusta a dalt, i a través
  dels arcs, la gespa, la `pica` i la galeria del davant, amb el campanar.
- **Coses:** `galeria`, `columnes`, `pica` (s'hi renta la cera), `gespa`, `campanar`, `banc` (on seu l'abadessa),
  `morter` (de la Gueraula), `porta_capitular` (al fons de la galeria, tancada: «Inspecció. Prohibit el pas»).
- **Sortides:** `porta_monestir` (l'avet). A l'acte 2, també `porta_bugaderia` i `porta_apotecaria`, a banda i banda
  de la galeria.
- **Personatges:** `ingilberga` asseguda al banc; `gueraula` dreta, amb el morter. A l'acte 1 és de la Vet: l'Iri
  s'excusa a la `porta_monestir` fins al final de l'acte, quan hi entra.
- **A l'acte 2 (capvespre):** llums d'oli a les columnes (decorat `llum_capvespre`), la gespa blava; la Gueraula és a
  l'apotecaria; l'Ingilberga, al banc. Hi passen les dues, i s'hi donen les coses.
- **A l'acte 4:** matí de sol (`llum_mati`); l'Ingilberga, que dona la pista del segell. La Gueraula és al judici.

## 5. `bugaderia` — La bugaderia (acte 2; Iri)

- **Quan i llum:** capvespre, una sala baixa de pedra plena de vapor. Llum taronja del `fogo` (quan és encès) i blava
  per una finestra petita. Càmera de prop.
- **Coses:** la `tina` gran damunt el `fogo`; dues tines petites; les `robes` esteses en diagonal (primer pla,
  `FRONT`, perquè l'Iri hi passi per darrere); el `bagul` de roba vella; la `pila_llenya` amb tres menes ben
  diferents de color (`pi`: clar i resinós; `pollancre`: blanc i lleuger; `alzina`: fosca i densa); les `tisores` de
  bugadera, grosses, penjades d'un clau.
- **Sortida:** `porta` (el claustre). Si la Vet hi arriba, s'excusa a la porta.
- **Decorats:** `bagul_obert`; `foc_ences` (animació de flames i més vapor); `tina_negra` (l'aigua negra a la tina);
  `habits_estesos` (els dos hàbits negres penjats, fumejant); `habits_curts` (escurçats, i els retalls a terra).
- **Personatges:** cap més que l'Iri.

## 6. `apotecaria` — L'apotecaria (acte 2; Vet)

- **Quan i llum:** vespre, espelmes i el fogonet. Prestatges plens fins al sostre. Càmera de prop.
- **Coses:** `prestatges`; quatre flascons d'herbes amb etiqueta, a l'abast: `flasco_menta`, `flasco_ruda`,
  `flasco_salvia` i `flasco_sense_nom` (la valeriana); un pot de pedra amb l'etiqueta *Atramentum*, més amunt
  (`atramentum`, el caparrós); els `manats` d'herbes penjats, entre els quals el `cardo` (un cap espinós i sec,
  ben reconeixible); la `pell_ovella` en un tamboret; la gerra de `mel`; el `morter` gran; la `llar` amb `carbo`; la
  `taula` amb pergamins; el `xarop` (un flascó verd, a la taula).
- **Decorats:** `cardo_agafat`; `disfressa` (al final: la cinemàtica de les dues disfressades, sense decorat si es fa
  amb les aparences).
- **Sortida:** `porta` (el claustre). Si l'Iri hi arriba abans d'hora, s'excusa a la porta; al final de la
  preparació hi entra, per disfressar-se.
- **Personatges:** `gueraula`.

## 7. `porteria` — La porteria (acte 2, nit; Iri, la Vet hi és)

- **Quan i llum:** nit, un passadís estret de pedra que s'allunya cap a la dreta; dues `torxes` (animació de flama,
  `characterLights`), la resta fosc. Càmera de prop.
- **Coses:** `porta_ala` (la porta de l'ala dels canonges, amb el `forrellat`), `banc`, `columna` (per amagar-s'hi),
  `torxes`, `llibre_entrades` (en un faristol: obert, amb ninots en lloc de noms).
- **Decorats:** `porta_oberta`; `ninots` (els dos ninots nous al llibre: «fra Tos i fra Silenci»).
- **Personatges:** `bonfill` assegut al banc, amb la llança; la **Vet** disfressada, darrere l'Iri (sala
  compartida).

## 8. `cuina` — La cuina (acte 2, nit; Vet, amb l'Iri)

- **Quan i llum:** nit, la `llar_foc` gegant fa tota la llum (taronja, ombres llargues que pugen per la paret). Càmera
  de prop.
- **Coses:** `llar_foc` (amb una olla al foc), les `olles` penjades, la `pila_olles` en un racó, la `taula` llarga, la
  `gerra` de vi, la `copa` (davant en Sunifred), el `banc`.
- **Decorats:** `olles_caigudes` (la pila per terra); `sunifred_dorm` (en Sunifred de bigotis a la taula, si no es fa
  amb l'animació del personatge).
- **Personatges:** `sunifred` al cap de la taula, amb el manat de claus al cinyell (ha de ser visible: un brill de
  ferro); la **Iri**, disfressada, al costat de la llar (sala compartida).

## 9. `scriptorium` — L'scriptorium (acte 3; Vet)

- **Quan i llum:** mitjanit; finestrals alts i foscos (una mica de lluna blava), i la llum càlida de les espelmes dels
  faristols. Càmera de prop.
- **Coses:** els `faristols` dels copistes, amb les `copies` de l'ordre; el `faristol_sunifred` (buit, amb el
  `pergami` en blanc); l'`espelma_hores` (gruixuda, amb ratlles, una de vermella); els `finestrals`; la
  `porta_capitular` (ferrada, al fons).
- **Decorats:** `espelma_retallada`; `porta_oberta`.
- **Sortides:** `porta_passadis` a l'esquerra (per on entren; l'Iri hi espera), `porta_capitular` al fons (l'arxiu,
  quan és oberta). Al tram obert, l'Iri és a l'arxiu: per a la Vet, la porta capitular hi porta un moment (per
  llegir etiquetes i la carta de l'Emma), però l'arxiu és de l'Iri.
- **Personatges:** `gombau` i `arnulf` (la mateixa base amb colors canviats), drets als seus faristols. Se'n van per
  l'esquerra (`stage`), i tornen pel mateix lloc quan l'Iri fa soroll a l'arxiu (`canonges_tornen`).

## 10. `arxiu` — L'arxiu (acte 3; Iri)

- **Quan i llum:** mitjanit, la sala capitular a les fosques: només l'espelma de la Vet (`characterLights`) i una
  finestra petita i alta. Càmera de prop.
- **Coses:** els `baguls` ferrats en fila, amb etiquetes (`bagul_delmes`, `bagul_censos`, `bagul_butlles` i el
  `bagul_sunifred`, l'únic amb un lacre vermell); el `tapis` gran (la creació del món, colors apagats); el `cordill`
  (que surt del bagul i se'n va darrere el tapís); l'`estendard` (un pal amb bandera); el `contrapes` (una pedra
  penjada a dalt, visible quan s'aparta el tapís); els `bancs` de pedra, i el `banc_fons` (es pot
  empènyer: a sota hi ha la `trapa` del rec); la `finestra`.
- **Decorats:** `bagul_obert`; `tapis_apartat`; `estendard_paret` (el pal recolzat a la paret, per pujar-hi);
  `doble_fons` (el fons del bagul obert); `cofre` (el cofre de l'Emma, amb el segell vermell trencat);
  `gueraula_finestra` (la cara de la Gueraula a la finestra, al final); `trapa_oberta` (el banc apartat i la
  trapa oberta, amb l'escala que baixa a l'aigua).
- **Sortida:** `porta_capitular` (l'scriptorium; la Vet hi és). A la fi, tancada des de fora.
- **Personatges:** l'Iri. La **Vet** hi entra un moment quan la crida l'Iri (etiquetes, la carta de l'Emma).

## 11. `moli` — El molí (acte 3; Iri, amb la Vet i la Gueraula)

- **Quan i llum:** matinada, el molí per dins: fusta mullada, farina pertot, la llum blava del canal i un fanal. Càmera
  de prop. A dalt, una `finestra_dalt` per on treu el cap la Gueraula, amb el torn de la comporta.
- **Coses:** la `roda` de fusta (gran, a la dreta, mig dins el canal); la `falca` que la bloqueja; la `comporta`; la
  `pastera` recolzada a la paret; el `canal` que surt cap a l'esquerra, fosc; les `moles` i els sacs de farina.
- **Decorats:** `falca_tallada`; `roda_gira` (animació); `pastera_aigua` (la pastera al canal); `aigua_puja`
  (l'aigua que puja quan s'obre la comporta abans d'hora, i torna a baixar).
- **Personatges:** `gueraula` a la finestra de dalt (sprite de mig cos, o decorat amb animació); la **Vet**,
  disfressada (sala compartida). Al final, la sortida en pastera és una cinemàtica curta.

## `portada` i `proleg`

- **El mateix pla** (`*_pla_comu.py`, com a Suma Zero i Ni un ou): l'`absis` i l'avet, de nit, amb tramuntana i
  pluja en diagonal; un llamp de tant en tant (animació per codi). Composició de cinema: l'avet ocupa la meitat
  esquerra, fosc contra el cel, i l'absis, rosat només quan fa llamp.
- **Portada:** l'avet **ajagut** damunt el mur, amb les arrels aixecades, i entre les arrels, el `cofre` amb el segell
  vermell que brilla (batega). El títol a dalt (capa `titol`). Ha de quedar bé sense botons: serà la imatge de la web.
- **Pròleg (capes amb `stage`):** `avet_dret` (l'avet dret, que es gronxa amb el vent), `fanal` (s'acosta),
  `figura` (s'ajup a les arrels, se'n va), `avet_cau` (animació: l'avet que cau damunt el mur, i la sacsejada,
  `shake`), `cofre_brilla`, `ma` (una màniga negra que agafa el cofre).
- **Rètols:** «Sant Joan de les Abadesses, novembre de l'any 1017», el títol i «Acte 1 — El crim botànic».

## `credits`

- L'absis de nit, a la primavera, amb el plançó d'avet petit al costat de les arrels velles i la lluna. Tranquil:
  només els grills i una mica de vent.

## `calc` — El calc (pantalla especial, escenes 4 i 9)

- **No és una sala per caminar:** un primer pla del pergamí damunt la taula, a pantalla completa. El carbonet a la mà
  (punter). En fregar, el carbó va enfosquint el pergamí i hi apareixen en blanc les lletres o el dibuix que hi ha a
  sota.
- **Dos estats:** `calc_segell` (el tros de cera: un cercle amb un arbre i *+ EMMA ABBATISSA*, trencat) i
  `calc_carta` (les línies de la carta d'en Sunifred, i el signe al peu).
- És **la mecànica nova** del joc (fase 5 de la guia): s'ha de provar al navegador abans de dibuixar les sales. Si no
  surt bé, es queda en una imatge fixa del resultat.
