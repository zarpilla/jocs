# L'Última Arrel — fitxes de les sales

> El contracte entre el contingut (`game/data/rooms/`) i l'art (`adapters/benne/tools/hd640/rooms/<sala>.py`). Els ids
> de les coses, dels decorats i dels personatges han de ser **exactament** els del JSON: el sync els lliga per id. Si
> l'art necessita una cosa nova, primer s'afegeix al contingut.
>
> Pantalla de 640×360; l'escena es pinta fins a y = 260 (a sota, el HUD). Les nenes són petites dins un món gran:
> a les sales «de lluny», la Iri fa ≈66-70 px, la Vet ≈60, l'àvia ≈80, l'Espora ≈35. Direcció d'art: el
> [guió](guio.md) («Regles del món», §4) i el [pla](pla.md) («Direcció d'art»). Mostres d'estil: `art/mostra/`
> (`vora_bosc.py` i `centraleta.py`, amb `bosc.py` i `nenes.py`); la referència que mana és
> `art/referencia/irivet-vora-bosc.png`.
>
> **Dues paletes, sempre.** El bosc: càlid (molsa, ocres de tardor, raigs daurats) i, quan va bé, punts i fils
> turquesa bioluminescents. NaturaPlus: fred i pla (blanc de plàstic, gris acer, verd fluor, cartells lluminosos).
> D'un cop d'ull s'ha de saber què és de qui.

## 1. `vora_bosc` — La vora del bosc (Escena 1, Iri)

- **Quan i llum:** dissabte, capvespre. El sol es pon entre els troncs, a l'esquerra. Càmera arran de terra, una mica
  contrapicada; primer pla de falgueres i arrels en silueta (`FRONT`).
- **Esquerra, el bosc:** el roure gegant amb la `porta_roure` (un metre: l'alçada de la Iri fins a l'espatlla), la
  `campaneta` al costat, la `bustia`, el `llum_vermell` (fanalet que parpelleja: `ANIMS`), l'`estaca` de topògraf
  clavada just davant la porta (cinta de NaturaPlus), i els `bolets` turquesa **apagats**.
- **Dreta, NaturaPlus:** la `tanca` metàl·lica, el `cartell` lluminós «BOSC 2.0 — NaturaPlus S.A. — INAUGURACIÓ: 2
  DIES», la `gespa` artificial en rotllos, l'`excavadora` i (de fons, sense id) la caseta d'obra i els cons. Al peu de
  la tanca, entre el fang, el `cargol` (que brilla massa).
- **Sortida:** `cami` a l'esquerra (no surt: la Iri diu que encara no és fosc).
- **Decorats:** `porta_oberta` (la porta oberta, amb llum càlida a dins: quan la Iri torna a sortir de la centraleta).
- **Personatges:** l'`avia` (només a la intro: entra amb la Iri per l'esquerra i se'n va pel `cami`). La Iri entra
  caminant per l'esquerra (`walkIn`).

## 2. `centraleta` — La centraleta del Miceli (Escena 2, Iri)

- **Quan i llum:** dissabte, capvespre, sota terra. Càmera de prop. Un forat de llum a dalt; la resta, càlid i fosc.
  Composició: la de la referència 2 (`art/referencia/centraleta-composicio.png`), però el personatge no.
- **Coses:** l'`escala` de mà que puja a la porta (sortida); el `tauler` de fusta (rodes, clavilles de bolet, rètol
  «MICELI»); el `radar` d'arrels (pantalla rodona de mica, apagada); el `corn` de fusta per escoltar; els
  `fils_paret` (fils de fong apagats per les parets); tres arrels a la paret, **iguals a ull nu**: `arrel_1`
  (esquerra), `arrel_2` (al mig: la viva), `arrel_3` (dreta). El `fil_saba` penja del tauler (només després
  d'encendre el radar).
- **Decorats:** `radar_ences` (la pantalla verda i tremolosa, amb el node 12 aixafat); `xarxa_encesa` (tots els fils
  de la paret i l'arrel del mig, turquesa fins al sostre, i el fil de saba lligat a l'arrel del mig).
- **Personatges:** l'`espora` (≈35 px), al costat del tauler.

## 3. `campament_fades` — El campament de les Fades d'Ortiga (Escena 3, Vet)

- **Quan i llum:** diumenge al matí, a les branques altes del roure gros. **Càmera molt a prop**: la Vet és gran, i
  les fades fan ≈30-35 px, amb la silueta clara (jaqueta de cuir d'escarabat, cresta de pelussa de card, ales de
  libèl·lula apedaçades). Llum de matí, verda i daurada entre les fulles.
- **Coses:** la `tenda` de cinta d'obra «PERILL — NO PASSAR»; el `gronxador` de cinta rosa fluor, que penja just al
  costat de la flor; la `catapulta` d'aglans (amb una pinça d'estendre); la `diana` amb el logotip de NaturaPlus; els
  `grafits` de suc de móra («FORA NATURAPLUS», «AIRE PUR? AIRE TEU!»); la `branca` prima com un llapis que surt cap a
  la dreta, i a la punta la `flor` (Flor de Pebre, vermella, amb pol·len); l'`escala_corda` per on puja la Vet
  (sortida, que no surt).
- **Decorats:** `flor_buida` (la flor sense pol·len, quan ja s'ha collit).
- **Personatges:** `urtica` (la cap), `pica` i `card` (la mateixa base amb colors canviats).

## 4. `toll_gripaus` — El toll dels gripaus buròcrates (Escena 4, Iri)

- **Quan i llum:** diumenge, migdia: un aiguamoll sec, calorós, llum alta i blanca. Càmera de lluny.
- **Coses:** l'`arxiu` (una soca buida amb calaixets i una finestreta de taquilla; rètol «REGISTRE DEL BOSC —
  HORARI: QUAN HI HA AIGUA»); el `toll` sec, amb el fang clivellat; els `joncs` grocs i caiguts; al fons a la dreta,
  el `rierol` que baixa d'un turó i no arriba: el tapa el `tap_plastics` (ampolles buides d'«Aire Pur NaturaPlus»), i
  un tub nou de NaturaPlus amb una roda, la `comporta` («ASPERSORS GESPA — SECTOR 4»); el `cami` (sortida, que no
  surt).
- **Decorats:** `aigua` (sota: el toll ple, l'aigua que baixa pel rierol i els joncs redreçats).
- **Personatges:** el `bufo` (Registrador, a la finestreta: armilla, visera, segell de goma) i un `gripau` vaguista
  amb pancarta (al costat, un segon gripau de fons, sense id, amb una altra pancarta). La Iri entra per l'esquerra.

## 5. `caseta_obra` — La caseta d'obra de NaturaPlus (Escena 5, Vet)

- **Quan i llum:** diumenge a la tarda, a dins d'un contenidor blanc. Llum de fluorescent, freda i plana: tota la
  sala és de la paleta NaturaPlus. La porta és oberta (a fora, el bosc càlid, una mica).
- **Coses:** l'`escriptori` (papers, cafè fred, una caixa de polseres); la `maqueta` del Bosc 2.0 (arbres de plàstic,
  tobogan, botiga d'Aire Pur, un ninotet que somriu); el `cartell` «La natura, però millor» amb un arbre que somriu;
  l'`arbre_wifi` de prova a la cantonada (arbret de plàstic amb llumetes i un endoll a la paret); sobre una caixa,
  l'`altaveu` gran, amb l'etiqueta «Sons del Bosc — versió prèmium» i una ruleta de ràdio; la `porta` (sortida, que no
  surt).
- **Personatges:** la `pla` (vestit blanc, tauleta, auriculars), de cara a una pantalla de videotrucada. La Vet entra
  per l'esquerra.

## 6. `zona_zero` — La Zona Zero (Escena 6, Iri; la Vet hi és, entre el públic)

- **Quan i llum:** dilluns, Festa Major, les deu del matí. Un clar del bosc a mig desbrossar. Càmera de lluny.
- **Coses:** les `soques` tallades; l'`escenari` blanc amb una cinta per tallar; la `pantalla` gegant «BOSC 2.0»; els
  `sensors` d'aire (tres columnes blanques amb la lectura verda «AIRE: PUR 100%»); l'`altaveu` de la caseta; el
  `public` del poble (figures de fons, sense animar, amb polseres de punts); la `formigonera` al fons, amb el motor
  engegat.
- **Decorats:** `sensors_vermells` (la lectura vermella «AIRE: PICANT»).
- **Personatges:** la `pla` a l'escenari; la `txell` (TV Comarca) amb el càmera (figura de fons); el `bufo` a la vora
  d'un bassal, amb la carpeta; l'`avia` entre el públic; la `urtica` a les branques de dalt (de lluny: tres crestes);
  i la **Vet** entre el públic (és sala compartida: la Vet necessita un lloc a `spawns`).

## 7. `bosc_obert` — El bosc obert (Escena 7, Vet; la Iri hi és)

- **Quan i llum:** una setmana després, de dia. La vora del bosc de l'escena 1 **sense la tanca**: es pot fer a partir
  de `vora_bosc`. El bosc és viu: els `bolets` i les arrels brillen de turquesa.
- **Coses:** la `porta_oberta` del roure (llum turquesa, ja no vermella); la `taula` feta d'una soca, amb tasses de te
  de menta; els `forats` on hi havia els pals de la tanca, on ja torna a créixer l'herba. De l'obra no en queda res
  més: el prat ha florit, i el sol del matí entra baix i daurat per la clariana de la dreta.
- **Personatges:** l'`espora`, l'`avia` i la **Iri** a la taula (sala compartida: la Iri necessita un lloc a
  `spawns`); la `urtica` a una branca; el `bufo` en un bassal. La Vet entra per l'esquerra.

## `portada` i `credits`

- **Portada:** el títol *L'Última Arrel* sobre el roure de la porta petita al capvespre, amb els fils turquesa de la
  xarxa sota terra. (També és `public/portada.png`.)
- **Crèdits:** el bosc obert de nit, amb tot el turquesa encès.
