# Revisió de textos

> Generat amb `npm run revisio` a partir de `game/data/`. No l'editis a mà.
>
> Per a cada cosa, les interaccions en l'ordre en què el motor les prova: s'agafa **la primera que encaixa**.
> Una interacció «SEMPRE» que no és l'última amaga les de sota.

## Sala Fons del mar · `aqua_fons` (iri, vet)

```
EN ENTRAR
    • * (una vegada) — SEMPRE
        NARRADOR: El fons del mar d'Aqua. Sorra blanca, nanses, i al fons, una caseta feta amb un casc de vaixell bolcat.

DECORAT lot9 — es veu si lot9

CISTELLA «cistella»
    • walkTo/use/open — SEMPRE
        [SO: cistella] NARRADOR: La cistella puja.
        ⇒ → aqua_port

PORTA_JUANA «casa de la Juana»
    • look — SEMPRE
        JUGADORA: Una caseta feta amb un vaixell bolcat. Té llum a dins.
    • walkTo/use/open (una vegada) — SEMPRE
        JUGADORA: Pas a pas, entre les nanses...
        [SO: trampa] NARRADOR: Xof.
        JUGADORA: He trepitjat una trampa. Era una trampa de peixos. No fa res. Però fa pudor.
        ⇒ +trampa_trepitjada, → casa_juana
    • walkTo/use/open — SEMPRE
        ⇒ → casa_juana

NANSES «nanses»
    • look — SEMPRE
        JUGADORA: Nanses. Trampes de peixos. Esperant peixos des de fa anys. Com nosaltres l'aigua.
    • pickUp/use — si trampa_trepitjada
        JUGADORA: Ja n'he trepitjat una. Prou.
    • pickUp/use — SEMPRE
        JUGADORA: Millor no tocar-les. Fan cara de mossegar.

BOIES «boies»
    • look — si lot9_vist i NO sorra_agafada
        JUGADORA: La boia més baixa, la del 32, dimarts tocava l'aigua. Ara és en sec, i el bassal s'ha retirat uns quants dits.
        JUGADORA: El lot 9 arriba fins a la línia de l'aigua de dimarts. I l'aigua, des de dimarts, no s'ha estat quieta.
        ⇒ +franja_vista
    • look — SEMPRE
        JUGADORA: Boies de mesurar, clavades a la sorra, amb números pintats: 40, 38, 36, 34... Cada una, més avall que l'anterior.
        JUGADORA: Algú mesura com baixa el mar. Dos metres cada vegada.

BASSAL «bassal»
    • look — SEMPRE
        JUGADORA: L'última aigua del mar d'Aqua. Hi cap una gavina. Si s'aprima.
    • use/pickUp — SEMPRE
        JUGADORA: No. És l'última. Que es quedi on és.

SORRA «sorra fina»
    • look — si lot9 i NO sorra_agafada
        JUGADORA: Sorra de fons, fina com farina. Però ara està plena d'estaques, amb una cinta de Verne.
        JUGADORA: Un cartell: «MAR D'AQUA · LOT 9. De la línia de l'aigua, amidada dimarts, cap amunt. Prohibit endur-se'n res.»
        ⇒ +lot9_vist
    • look — si lot9 i franja_vista
        JUGADORA: Sorra de fons, fina com farina, i les estaques del lot 9 de Verne. La franja de sota la línia de dimarts ja té un forat.
    • look — si lot9
        JUGADORA: Sorra de fons, fina com farina, i les estaques del lot 9 de Verne. Sort que la vam agafar abans que la comptessin.
    • look — SEMPRE
        JUGADORA: Sorra de fons. Blanca i fina com farina.
    • pickUp — si sorra_agafada
        JUGADORA: Ja en porto un sac.
    • pickUp — si lot9 i franja_vista
        JUGADORA: De la línia de dimarts cap avall. Aquesta sorra, dimarts, era sota l'aigua: no és del lot 9. No és de ningú.
        JUGADORA: Un sac de sorra fina. La més fina de Vesper. En Bru en té prou per al motlle. ⟨si cal_sorra⟩
        JUGADORA: Un sac de sorra fina. Per si de cas. ⟨si NO cal_sorra⟩
        ⇒ +sorra_agafada, rep sorra
    • pickUp — si lot9
        JUGADORA: Ara no es pot: hi ha estaques i una cinta de Verne.
        JUGADORA: Un cartell: «MAR D'AQUA · LOT 9. De la línia de l'aigua, amidada dimarts, cap amunt. Prohibit endur-se'n res.»
        ⇒ +lot9_vist
    • pickUp — si sorra_refusada
        JUGADORA: Mig quilo a les botes i un sac a l'esquena. Per si de cas.
        ⇒ +sorra_agafada, rep sorra
    • pickUp — SEMPRE
        JUGADORA: Per què voldria sorra? En porto mig quilo a les botes.
        ⇒ +sorra_refusada

OSSOS «espina»
    • look — SEMPRE
        JUGADORA: L'espina d'un peix gros com una escala. Quan hi havia mar, hi havia peixos així.

```

## Sala Port d'Aqua · `aqua_port` (iri, vet)

```
EN ENTRAR
    • * (una vegada) — SEMPRE
        NARRADOR: Aqua. Era el mar més gran de Vesper. Ara és un desert de sal amb un port al mig.
        IRI: On és el mar? ⟨si iri a aqua_port i vet a aqua_port⟩
        VET: A baix. Molt a baix. ⟨si iri a aqua_port i vet a aqua_port⟩
        JUGADORA: On és el mar? ⟨si no (iri a aqua_port i vet a aqua_port)⟩
        JUGADORA: ...Ah. A baix. Molt a baix. ⟨si no (iri a aqua_port i vet a aqua_port)⟩

DECORAT grua_arreglada — es veu si grua_arreglada

RAMPA «Cantimplora»
    • walkTo/use/open — SEMPRE
        ⇒ → cantimplora_bodega

ESCALA_PORT «escala del port»
    • look — SEMPRE
        JUGADORA: L'escala del port. Baixa, baixa... i s'acaba a l'aire, quaranta metres per sobre del fons.
    • walkTo/use/open — SEMPRE
        JUGADORA: No. Els últims quaranta esglaons són d'aire. L'aire, de moment, encara no el ven ningú.

GRUA «grua»
    • use + fusible_apanyat — si juga vet i NO grua_arreglada
        [SO: grua] JUGADORA: Fusible de trenta, al seu lloc...
        JUGADORA: Llum verd! La grua funciona.
        JUGADORA: Ara, una a la cistella i l'altra als comandaments.
        ⇒ +grua_arreglada, perd fusible_apanyat
    • use + fusible_apanyat — si NO grua_arreglada
        JUGADORA: Això ho ha de muntar la Vet. Si ho faig jo, la grua acabarà a l'òrbita.
    • use + fusible — si NO grua_arreglada
        JUGADORA: És de deu. La grua en demana un de trenta. Petaria abans de dir «grua».
    • look — si juga vet i NO grua_arreglada
        JUGADORA: La grua de descarregar peix. Funcionaria, si tingués el fusible. Li falta. De trenta ampers.
        JUGADORA: A la nau en tenim de recanvi. De deu, però. Embolicat amb alguna cosa que condueixi, un de deu aguantaria. Paper de plata, per exemple.
        ⇒ +grua_vista
    • look — si NO grua_arreglada
        JUGADORA: Una grua de port amb una cistella penjada. La cabina té un forat on hi faltaria alguna peça. La Vet sabrà què és.
        ⇒ +grua_vista
    • look — SEMPRE
        JUGADORA: La grua, amb el llum verd. Va.
    • use — si NO grua_arreglada
        JUGADORA: No arrenca. Hi falta una peça a la cabina.
        ⇒ +grua_vista
    • use — SEMPRE
        JUGADORA: Funciona. Per baixar, a la cistella.

CISTELLA «cistella»
    • look — SEMPRE
        JUGADORA: La cistella de la grua. Hi cabem una persona i un peix. Ara, sense peix.
    • walkTo/use/open — si NO grua_arreglada
        JUGADORA: Sense grua, la cistella és un gronxador.
    • walkTo/use/open — si NO baixada_feta i ((juga iri i vet a aqua_port) o (juga vet i iri a aqua_port))
        JUGADORA: Pujo a la cistella...
        VET: Tu condueixes naus. Jo condueixo grues. ⟨si juga iri⟩
        IRI: Agafa't. Aquesta grua és més vella que la Capitana. ⟨si juga vet⟩
        [SO: cistella] NARRADOR: La cistella baixa, a sacsejades, quaranta metres.
        JUGADORA: Des d'aquí baix, ara que va, la cistella té botó. Ja podem pujar i baixar soles.
        ⇒ +baixada_feta, → aqua_fons
    • walkTo/use/open — si NO baixada_feta
        JUGADORA: La grua funciona, però algú l'ha de fer anar des de dalt. Necessito l'altra aquí, als comandaments.
    • walkTo/use/open — SEMPRE
        [SO: cistella] NARRADOR: La cistella baixa.
        ⇒ → aqua_fons

VAIXELLS «vaixells encallats»
    • look — SEMPRE
        JUGADORA: Vaixells de pesca encallats a la sorra. Un es diu «Sempre Plena». Un altre, «Ja Tornarà».

PANELL_PREU «panell del preu»
    • look — SEMPRE
        JUGADORA: AIGUA VERNE. Un litre: 48 crèdits. I la fletxa, cap amunt. ⟨si preu_aigua = 48⟩
        JUGADORA: AIGUA VERNE. Un litre: 64 crèdits. I la fletxa, cap amunt. ⟨si preu_aigua = 64⟩
        JUGADORA: AIGUA VERNE. Un litre: 97 crèdits. I la fletxa, cap amunt. ⟨si preu_aigua = 97⟩
        JUGADORA: AIGUA VERNE. Un litre: 112 crèdits. I la fletxa, cap amunt. ⟨si preu_aigua = 112⟩
        JUGADORA: AIGUA VERNE. Un litre, i la fletxa. Avui, cap avall. ⟨si preu_aigua ≠ 48 i preu_aigua ≠ 64 i preu_aigua ≠ 97 i preu_aigua ≠ 112⟩
        NARRADOR: AIGUA VERNE · {preu_aigua} ₡ ⟨si preu_aigua ≠ 48 i preu_aigua ≠ 64 i preu_aigua ≠ 97 i preu_aigua ≠ 112⟩
    • use/push/pull/pickUp — SEMPRE
        JUGADORA: A Aqua, el panell és l'única cosa que encara puja.

CANONADA «Canonada»
    • look — SEMPRE
        JUGADORA: La Canonada d'Aqua. Xucla el mar. Literalment.

```

## Sala Bodega de la Cantimplora · `cantimplora_bodega` (iri, vet)

```
EN ENTRAR
    • * (una vegada) — SEMPRE
        NARRADOR: La bodega de la Cantimplora: nou dipòsits buits, una cuina de quatre pams, i un barril.

DECORAT llum_terra2 — es veu si planeta = "terra2"
DECORAT llum_aqua — es veu si planeta = "aqua"
DECORAT llum_ferrum — es veu si planeta = "ferrum"
DECORAT llum_verdant — es veu si planeta = "verdant"
DECORAT motor_obert — es veu si escena = 2 i NO injector_posat
DECORAT sacs_carregats — es veu si sacs_carregats i NO juana_coneguda
DECORAT diu_carmanyola — es veu si escena = 6 i NO diu_aparta

RAMPA «rampa»
    • look — SEMPRE
        JUGADORA: La rampa. Fora hi ha el planeta on som.
    • walkTo/use/open — si planeta = "terra2"
        ⇒ → port_terra2
    • walkTo/use/open — si planeta = "aqua"
        ⇒ → aqua_port
    • walkTo/use/open — si planeta = "ferrum"
        ⇒ → ferrum_carrer
    • walkTo/use/open — si planeta = "verdant"
        ⇒ → verdant_jardi

ESCALA «pont»
    • walkTo/use/open — SEMPRE
        ⇒ → cantimplora_pont

BARRIL «l'últim barril» — hi és si NO barril_donat
    • look — si juga vet
        JUGADORA: L'últim barril. Cent litres. El rètol el vaig escriure jo: «NO. PER SI DE CAS.» Amb dues ratlles a sota.
    • look — SEMPRE
        JUGADORA: L'últim barril de la Cantimplora: cent litres d'aigua. La Vet hi va escriure «NO. PER SI DE CAS.» Amb dues ratlles a sota.
    • push/pull/use/pickUp — si bru_set i NO canalla_beu
        ⇒ diàleg barril
    • push/pull/use/pickUp — si juga vet
        JUGADORA: No.
    • push/pull/use/pickUp — SEMPRE
        JUGADORA: Pesa cent quilos. I la Vet em mataria.

CALAIX «calaix de la Vet»
    • open/look/use/pull/pickUp — si juga vet i NO mosca_activa i té tornavis_flor
        JUGADORA: El meu calaix. Cargols, cinta, dues piles, fil de pescar, una agulla de cosir grossa... i la Mosca.
        JUGADORA: La Mosca: el dron que vaig fer amb un aspirador. Li faltava un cargol de cap de flor. Ara tinc el tornavís.
        [SO: mosca] JUGADORA: ...Ja està. Mosca, desperta.
        NARRADOR: La Mosca brunzeix, fa una volta a la bodega i s'atura a l'espatlla de la Vet.
        VET: Si una de les dues fa servir un objecte amb la Mosca, l'hi porta a l'altra. Si som al mateix planeta, i si pesa poc.
        VET: Aigua, no. És l'única cosa que no porta.
        ⇒ +mosca_activa, rep mosca (iri), rep mosca (vet)
    • look — si juga vet i NO mosca_activa
        JUGADORA: El meu calaix. Hi ha la Mosca, el meu dron, a mig arreglar: li falta un cargol de cap de flor. Amb el meu tornavís i la punta, ho faria en un minut.
    • open/pickUp/use/pull — si juga vet i cal_agulla i NO agulla_agafada
        JUGADORA: L'agulla grossa. Ja sabia jo que un dia em caldria.
        ⇒ +agulla_agafada, rep agulla
    • look — si juga vet
        JUGADORA: Cargols, cinta, dues piles, fil de pescar... Ara no em cal res. Però m'agrada saber que hi és.
    • look — SEMPRE
        JUGADORA: El calaix de la Vet. Cargols, cinta, fil de pescar, dues piles... «Per si de cas.» No el toco: la Vet sap on és cada cosa.

CAFETERA «cafetera»
    • look — SEMPRE
        JUGADORA: La cafetera. Fa el millor cafè de Vesper i el pitjor soroll.
    • pickUp/open/use — SEMPRE
        JUGADORA: Sense cafetera, la Capitana s'amotina. I és la capitana.

NEVERA «nevera»
    • open/pickUp — si escena = 6 i diu_carmanyola_vist i NO pernil_agafat
        JUGADORA: Llenties, una ampolla d'aigua de la mida d'un dit... i el pernil d'en Tomàs. Per a una bona causa.
        ⇒ +pernil_agafat, rep pernil
    • look — si pernil_agafat
        JUGADORA: Llenties i una ampolla d'aigua de la mida d'un dit. El pernil ja ha trobat una bona causa.
    • look — SEMPRE
        JUGADORA: Llenties, el pernil d'en Tomàs i una ampolla d'aigua de la mida d'un dit. No la toquem.

TAULER «tauler de la cuina»
    • look — SEMPRE
        ⇒ diàleg tauler

CARMANYOLA «carmanyola d'en Tomàs»
    • use + pernil — si escena = 6 i NO diu_aparta
        JUGADORA: Ensumo... en Diu ensuma... I salta a buscar el pernil. Se l'endú al dipòsit.
        [SO: gat] NARRADOR: La carmanyola queda lliure.
        ⇒ +diu_aparta, perd pernil
    • look — si escena = 6 i NO diu_aparta
        JUGADORA: En Diu dorm damunt la carmanyola d'en Tomàs. Quan en Diu dorm a sobre d'una cosa, aquella cosa és d'en Diu.
        JUGADORA: Si li oferís alguna cosa més interessant... Té debilitat pel pernil.
        ⇒ +diu_carmanyola_vist
    • open/use — si escena = 6 i cal_espia i NO diu_aparta
        JUGADORA: En Diu dorm a sobre i em clava una mirada. No.
        ⇒ +diu_carmanyola_vist
    • open/use — si escena = 6 i cal_espia i NO tomas_descobert
        JUGADORA: La carmanyola... Al fons, sota l'entrepà, hi ha un comunicador petit. I paperets doblegats.
        JUGADORA: «Avui la Vet ha dit «collons» tres vegades.» «L'Iri és molt bona pilot.» «Hem menjat llenties.»
        JUGADORA: «Les germanes tenen tres claus de comptador fos. Han estat al despatx de Verdant. Han pagat l'entrada amb un sac de llavors.» ⟨si NO fidel_tractor⟩
        JUGADORA: «Les germanes tenen tres claus de comptador fos. Han estat al despatx de Verdant. Han pagat l'entrada amb un tractor que no arrenca.» ⟨si fidel_tractor⟩
        JUGADORA: En Tomàs. ⟨si no (iri a cantimplora_bodega i vet a cantimplora_bodega)⟩
        IRI: En Tomàs. ⟨si iri a cantimplora_bodega i vet a cantimplora_bodega⟩
        VET: En Tomàs. ⟨si iri a cantimplora_bodega i vet a cantimplora_bodega⟩
        ⇒ +tomas_descobert
    • open/use — si tomas_descobert
        JUGADORA: El comunicador d'en Tomàs i els seus informes. Ja ho sabem tot.
    • look — si colada_bip
        JUGADORA: La carmanyola d'en Tomàs. I aquesta nit ha fet bip. Les carmanyoles no fan bip.
    • look — si paper_donat
        JUGADORA: La carmanyola d'en Tomàs. Té un adhesiu d'una nau de curses. A dins, un entrepà sense paper: el paper aguanta un fusible.
    • look — SEMPRE
        JUGADORA: La carmanyola d'en Tomàs. Té un adhesiu d'una nau de curses. A dins, un entrepà embolicat amb paper de plata.
    • open/use — SEMPRE
        JUGADORA: No remeno les coses dels altres. Encara.

MOTOR «motor»
    • use + injector — si juga vet i NO injector_posat
        [SO: cargols] JUGADORA: Injector de l'avi al seu lloc... Rosca bona, broquet net.
        JUGADORA: La Cantimplora tornarà a volar.
        ⇒ +injector_posat, perd injector
    • use + injector — si NO injector_posat
        JUGADORA: Això l'ha de muntar la Vet. Jo, els motors, només els sé fer petar.
    • look — si juga vet i NO injector_posat
        JUGADORA: El motor de salt. L'injector té el broquet esquerdat. Sense injector, la Cantimplora és un dipòsit amb seients.
        JUGADORA: I a la mateixa fàbrica on el van fer, van fer el tractor de l'avi. Mateix broquet.
        ⇒ +injector_vist
    • look — si cap_condicions i NO injector_posat
        JUGADORA: El motor. La Vet diu que l'injector té el broquet esquerdat, i que el tractor de l'avi en té un d'igual.
        ⇒ +injector_vist
    • look — SEMPRE
        JUGADORA: El motor de la Cantimplora. Ronca, però vola.
    • pickUp — si NO oli_agafat
        JUGADORA: Una llauna d'oli de motor. Per al motor, per al tractor, i per a la Capitana quan fa mal temps.
        ⇒ +oli_agafat, rep oli
    • pickUp — SEMPRE
        JUGADORA: L'oli ja el tenim. Amb una llauna n'hi ha prou.

FUSIBLES «quadre de fusibles»
    • look — SEMPRE
        JUGADORA: El quadre de fusibles. Sobren fusibles de deu. De trenta, cap.
    • pickUp/open/use — si grua_vista i NO fusible_agafat
        JUGADORA: Un fusible de deu. Per a la grua n'hi cal un de trenta... Ja hi pensaré.
        ⇒ +fusible_agafat, rep fusible
    • pickUp/open/use — SEMPRE
        JUGADORA: Si en trec un sense motiu, s'apaga la cafetera. I la Capitana.

DIPOSIT «dipòsit»
    • look — SEMPRE
        JUGADORA: Un dipòsit buit. És el dormitori d'en Diu. La Capitana no ho sap. Fa veure que no ho sap.

CARREGA «espai de càrrega»
    • use + sacs_llavors — SEMPRE
        JUGADORA: Tres sacs de llavors, a la bodega. La càrrega més lleugera que ha portat mai la Cantimplora.
        ⇒ +sacs_carregats, perd sacs_llavors
    • look — si sacs_carregats i NO juana_coneguda
        JUGADORA: Tres sacs de llavors per a la Juana.
    • look — si juana_coneguda
        JUGADORA: L'espai de càrrega. Buit una altra vegada: les llavors ja són de la Juana.
    • look — SEMPRE
        JUGADORA: L'espai de càrrega. Buit des de fa tres mesos.

TOMAS «—» — hi és si escena ≥ 2 i escena ≤ 6

DIU «—» — hi és si escena ≥ 2 i no (escena = 6 i NO diu_aparta)

```

## Sala Carta de navegació · `cantimplora_mapa` — cinemàtica

```
EN ENTRAR
    • * — SEMPRE
        NARRADOR: On anem? ⟨si planeta = "terra2"⟩
        NARRADOR: On anem? ⟨si planeta = "aqua"⟩
        NARRADOR: On anem? ⟨si planeta = "ferrum"⟩
        NARRADOR: On anem? ⟨si planeta = "verdant"⟩

TERRA2 «Navega a Terra-2» — hi és si no (planeta = "terra2")
    • walkTo/use — SEMPRE
        NARRADOR: Rumb a Terra-2 · tres hores
        [SO: motor_nau] NARRADOR: La Cantimplora tus, tremola, s'enlaira... ⟨si planeta = "aqua"⟩
        [SO: motor_nau] NARRADOR: La Cantimplora tus, tremola, s'enlaira... ⟨si planeta = "ferrum"⟩
        [SO: motor_nau] NARRADOR: La Cantimplora tus, tremola, s'enlaira... ⟨si planeta = "verdant"⟩
        NARRADOR: ...i aterra al port, entre una nuvolada de pols.
          ⇒ planeta := "terra2"
        NARRADOR: La Vet ja és a bord: puja sempre abans d'enlairar-se. ⟨si no (vet a cantimplora_pont o vet a cantimplora_bodega)⟩
          ⇒ esdeveniment situar
        ⇒ → cantimplora_pont

AQUA «Navega a Aqua» — hi és si no (planeta = "aqua") i aqua_oberta
    • walkTo/use — SEMPRE
        NARRADOR: Rumb a Aqua · nou hores
        [SO: motor_nau] NARRADOR: La Cantimplora tus, tremola, s'enlaira... ⟨si planeta = "terra2"⟩
        [SO: motor_nau] NARRADOR: La Cantimplora tus, tremola, s'enlaira... ⟨si planeta = "ferrum"⟩
        [SO: motor_nau] NARRADOR: La Cantimplora tus, tremola, s'enlaira... ⟨si planeta = "verdant"⟩
        NARRADOR: ...i aterra al port d'Aqua, entre una nuvolada de sal.
          ⇒ planeta := "aqua"
        NARRADOR: La Vet ja és a bord: puja sempre abans d'enlairar-se. ⟨si no (vet a cantimplora_pont o vet a cantimplora_bodega)⟩
          ⇒ esdeveniment situar
        ⇒ → cantimplora_pont

FERRUM «Navega a Ferrum» — hi és si no (planeta = "ferrum") i ferrum_oberta
    • walkTo/use — SEMPRE
        NARRADOR: Rumb a Ferrum · sis hores
        [SO: motor_nau] NARRADOR: La Cantimplora tus, tremola, s'enlaira... ⟨si planeta = "terra2"⟩
        [SO: motor_nau] NARRADOR: La Cantimplora tus, tremola, s'enlaira... ⟨si planeta = "aqua"⟩
        [SO: motor_nau] NARRADOR: La Cantimplora tus, tremola, s'enlaira... ⟨si planeta = "verdant"⟩
        NARRADOR: ...i aterra a Ferrum, entre fum i xemeneies.
          ⇒ planeta := "ferrum"
        NARRADOR: La Vet ja és a bord: puja sempre abans d'enlairar-se. ⟨si no (vet a cantimplora_pont o vet a cantimplora_bodega)⟩
          ⇒ esdeveniment situar
        ⇒ → cantimplora_pont

VERDANT «Navega a Verdant» — hi és si no (planeta = "verdant") i verdant_oberta
    • walkTo/use — SEMPRE
        NARRADOR: Rumb a Verdant · cinc hores
        [SO: motor_nau] NARRADOR: La Cantimplora tus, tremola, s'enlaira... ⟨si planeta = "terra2"⟩
        [SO: motor_nau] NARRADOR: La Cantimplora tus, tremola, s'enlaira... ⟨si planeta = "aqua"⟩
        [SO: motor_nau] NARRADOR: La Cantimplora tus, tremola, s'enlaira... ⟨si planeta = "ferrum"⟩
        NARRADOR: ...i aterra a Verdant, en una pista de gespa artificial.
          ⇒ planeta := "verdant"
        NARRADOR: La Vet ja és a bord: puja sempre abans d'enlairar-se. ⟨si no (vet a cantimplora_pont o vet a cantimplora_bodega)⟩
          ⇒ esdeveniment situar
        ⇒ → cantimplora_pont

PALAU «Navega al palau orbital» — hi és si escena ≥ 6
    • walkTo/use — SEMPRE
        ⇒ +palau_tancat, → cantimplora_pont

AQUI_TERRA2 «Ens quedem on som» — hi és si planeta = "terra2"
    • walkTo/use — SEMPRE
        ⇒ → cantimplora_pont

AQUI_AQUA «Ens quedem on som» — hi és si planeta = "aqua"
    • walkTo/use — SEMPRE
        ⇒ → cantimplora_pont

AQUI_FERRUM «Ens quedem on som» — hi és si planeta = "ferrum"
    • walkTo/use — SEMPRE
        ⇒ → cantimplora_pont

AQUI_VERDANT «Ens quedem on som» — hi és si planeta = "verdant"
    • walkTo/use — SEMPRE
        ⇒ → cantimplora_pont

```

## Sala Pont de la Cantimplora · `cantimplora_pont` (iri, vet)

```
EN ENTRAR
    • * (una vegada) — si escena = 6 i NO trucada_feta
        [SO: pantalla] NARRADOR: La pantalla del pont s'encén sola.
        ⇒ +trucada_activa, diàleg trucada
    • * — si palau_tancat
        JUGADORA: Amb invitació o sense, el palau no deixa atracar ni un mosquit. I la Cantimplora és un mosquit molt gros.
        IRI: Hi hem d'anar per una altra via: la llançadora d'en Nil. La invitació ja la tenim; el que em falta és un vestit de gala. ⟨si no (té vestit_arreglat (iri))⟩
        IRI: Hi hem d'anar per una altra via: la llançadora d'en Nil. Invitació i vestit, ja els tinc. Abans, però, cal deixar la Cantimplora en ordre. ⟨si té vestit_arreglat (iri)⟩
        ⇒ −palau_tancat

DECORAT vista_terra2 — es veu si planeta = "terra2"
DECORAT vista_aqua — es veu si planeta = "aqua"
DECORAT vista_ferrum — es veu si planeta = "ferrum"
DECORAT vista_verdant — es veu si planeta = "verdant"
DECORAT pantalla_verne — es veu si trucada_activa

ESCALA «bodega»
    • walkTo/use/open — SEMPRE
        ⇒ → cantimplora_bodega

MAPA «mapa de navegació»
    • look — SEMPRE
        JUGADORA: El mapa de navegació: una taula de vidre amb Vesper i els seus planetes. Hi brillen els que podem visitar.
    • use — si juga vet
        JUGADORA: Jo sé com funciona. No sé com es fa servir. Això és cosa de l'Iri.
    • use — si NO capitana_accepta
        JUGADORA: Sense permís de la Capitana, no m'hi deixa posar ni el dit.
    • use — SEMPRE
        ⇒ → cantimplora_mapa

RADIO «ràdio»
    • look — SEMPRE
        JUGADORA: La ràdio de banda vella. La Capitana hi té apuntades freqüències amb retolador, al marc.
    • use/talkTo/push — si cap_condicions i NO albara_fet
        [SO: radio] NARRADOR: Xiuxiueig d'estàtica... i una veu.
        ⇒ diàleg radio_juana
    • use/talkTo/push — SEMPRE
        [SO: radio] NARRADOR: Estàtica.
        NARRADOR: «...Aigua Verne. Perquè la set no espera...»

PANTALLA «pantalla»
    • look — si trucada_feta
        JUGADORA: Apagada. Encara hi veig el somriure.
    • look — SEMPRE
        JUGADORA: La pantalla gran. Només hi surten anuncis de Verne.
    • use — SEMPRE
        JUGADORA: No l'encenc. Avui ja hem vist prou anuncis.

FINESTRAL «finestral»
    • look — si planeta = "terra2"
        JUGADORA: Pel finestral, el port de Terra-2 i la Canonada al fons. Pols.
    • look — si planeta = "aqua"
        JUGADORA: Pel finestral, el port d'Aqua, blanc de sal. I a baix, on era el mar, res.
    • look — si planeta = "ferrum"
        JUGADORA: Pel finestral, Ferrum: xemeneies, fum i el piquet.
    • look — si planeta = "verdant"
        JUGADORA: Pel finestral, Verdant. Tot és tan verd que fa mal als ulls.

SEIENT «seient de la Capitana»
    • look — SEMPRE
        JUGADORA: El seient de la Capitana. Té la forma de la Capitana.
    • use — SEMPRE
        JUGADORA: Ni se m'acudiria. La Capitana nota qui s'hi asseu per l'olor.

CAPITANA «—» — hi és si escena ≤ 6

```

## Sala Casa de la Juana · `casa_juana` (iri, vet)

```
PORTA «sortida»
    • walkTo/use/open — SEMPRE
        ⇒ → aqua_fons

MAPES «mapes»
    • look — SEMPRE
        JUGADORA: Mapes del mar d'Aqua amb les línies de nivell. Cada any, més avall. L'últim és gairebé un punt.

LLIBRES «llibres»
    • look — SEMPRE
        JUGADORA: «Oceanografia», «Oceanografia II», «Com sobreviure amb un got d'aigua al dia». Aquest, molt subratllat.

AQUARI «aquari»
    • look — SEMPRE
        JUGADORA: Un aquari buit, net i amb el llum encès. Un rètol: «PER QUAN TORNIN».

FINESTRA «finestra»
    • look — SEMPRE
        JUGADORA: Per la finestra rodona es veu la paret del moll, a dalt, i la cistella penjada.

JUANA «—»

```

## Sala Crèdits · `credits` — cinemàtica

```
```

## Sala Carrer de Ferrum · `ferrum_carrer` (iri, vet)

```
EN ENTRAR
    • * (una vegada) — SEMPRE
        NARRADOR: Ferrum. El planeta de les mines. Fa olor de fum i de vaga.
          ⇒ preu_aigua := 64, +lot9
        JUGADORA: Aquí l'aigua no la pot pagar ningú. ⟨si no (iri a ferrum_carrer i vet a ferrum_carrer)⟩
        IRI: Aquí l'aigua no la pot pagar ningú. ⟨si iri a ferrum_carrer i vet a ferrum_carrer⟩
        VET: És on més se'n necessita. ⟨si iri a ferrum_carrer i vet a ferrum_carrer⟩
        NARRADOR: Des de la rampa, en Tomàs mira el piquet. Al piquet, una dona amb casc també el mira. Cap dels dos no diu res.

DECORAT barril_piquet — es veu si barril_donat
DECORAT condensador_arreglat — es veu si condensador_arreglat
DECORAT pantalla_mosca — es veu si mosca_contractada
DECORAT goteig — es veu si condensador_arreglat

RAMPA «Cantimplora»
    • walkTo/use/open — SEMPRE
        ⇒ → cantimplora_bodega

PORTA_SINDICAT «sindicat»
    • look — SEMPRE
        JUGADORA: El local del sindicat. A la porta: «VAGA. AQUÍ NO ES VEN RES.»
    • walkTo/use/open — SEMPRE
        ⇒ → ferrum_sindicat

PORTA_FOSA «fosa»
    • look — SEMPRE
        JUGADORA: La fosa de Ferrum. Aturada des de la vaga.
    • walkTo/use/open — si NO promesa_lia
        JUGADORA: La fosa és del sindicat. Sense en Bru, no hi entra ningú.
    • walkTo/use/open — si claus_fetes
        JUGADORA: La fosa està tancada. Ja hem fet el que hi havíem de fer.
    • walkTo/use/open — SEMPRE
        ⇒ → fosa_forn

FONT «font de Verne»
    • look — SEMPRE
        JUGADORA: Una font de Verne. Només raja amb «targeta de treballador actiu». Els vaguistes no en tenen.
        JUGADORA: A sota, una pantalla encesa: «VERNE S.A. CONTRACTA». És l'única cosa de la font que funciona. ⟨si NO mosca_contractada⟩
        JUGADORA: A sota, la pantalla: «VERNE S.A. CONTRACTA. Felicitats a la nostra nova operària.» ⟨si mosca_contractada⟩
    • use + mosca — si NO mosca_contractada
        JUGADORA: Mosca. Tens una entrevista de feina. ⟨si juga vet⟩
        JUGADORA: Mosca. Ves-hi tu, que tens el perfil. ⟨si juga iri⟩
        NARRADOR: La Mosca s'atura davant de la pantalla. La pantalla la mira de dalt a baix.
        [SO: bip] NARRADOR: «Vaga: mai. Disponibilitat: vint-i-quatre hores. Necessitat d'aigua: cap. Felicitats. Benvinguda a la família Verne.»
        NARRADOR: La font escup una targeta de plàstic blau.
        JUGADORA: Targeta de treballador actiu. Titular: Mosca. Categoria: operària de càrrega.
        JUGADORA: Fa un minut que treballa per a Verne i ja té més drets que tot el piquet.
        ⇒ +mosca_contractada, rep targeta_verne
    • use + mosca — SEMPRE
        JUGADORA: La Mosca ja hi treballa. Torn de vint-i-quatre hores, i encara no ha cobrat.
    • use + targeta_verne — SEMPRE
        NARRADOR: La font llegeix la targeta: «Titular: Mosca. Ració d'aigua: zero litres. La titular no en necessita.»
        JUGADORA: És clar.
    • use/push/open/pull — SEMPRE
        ⇒ diàleg contractacio

CONDENSADOR «condensador»
    • look — si condensador_arreglat
        JUGADORA: El condensador, en marxa, amb la targeta de la Mosca al lector. Fa poca aigua, però en fa cada dia. I l'aire encara no té amo.
    • look — si juga vet
        JUGADORA: Un condensador d'aire: treu aigua de la humitat. Poca, però cada dia. Verne el va comprar quan venia l'aigua «més barata», i el va apagar.
        JUGADORA: No li falta cap peça. Li'n sobra una: un lector de targetes. «Engegada reservada a treballadors actius de Verne S.A.»
        ⇒ +cal_targeta
    • look — SEMPRE
        JUGADORA: Un condensador vell, amb aletes. Algú hi ha cargolat un lector de targetes nou de trinca: «Engegada reservada a treballadors actius de Verne S.A.»
        ⇒ +cal_targeta
    • use + targeta_verne — si NO condensador_arreglat
        JUGADORA: La targeta de la Mosca, al lector...
        [SO: condensador] NARRADOR: El lector fa un bip satisfet. El condensador tus, brunzeix, i per l'aixeta comença a caure aigua. A gotes, però cau.
        NARRADOR: La canalla del piquet hi fa cua amb gots.
        JUGADORA: La targeta, que s'hi quedi. La Mosca no la necessita: no beu.
        ⇒ +condensador_arreglat, +canalla_beu, perd targeta_verne
    • use + qualsevol objecte — si NO condensador_arreglat
        JUGADORA: El lector només vol targetes de treballador actiu de Verne. Això no ho és.
    • use — si NO condensador_arreglat
        JUGADORA: No arrenca. El lector vol una targeta de treballador actiu de Verne.
        ⇒ +cal_targeta

PIQUET «piquet»
    • look — si NO canalla_beu
        JUGADORA: El piquet. Canalla, mantes, un bidó amb foc i pancartes. «QUI NO TREBALLA NO BEU», ratllat. A sota: «QUI NO BEU NO TREBALLA».
        JUGADORA: Tenen tres garrafes per a quaranta persones.
    • look — SEMPRE
        JUGADORA: La canalla beu. Un nen fa una competició de qui fa més soroll amb el got.

COMPTADORS «comptadors»
    • look — SEMPRE
        JUGADORA: Comptadors d'aigua de Verne, arrencats de les cases. Una muntanya.
    • pickUp — SEMPRE
        JUGADORA: Pesen. I no són meus: ara són de tothom.

PANELL_PREU «panell del preu»
    • look — SEMPRE
        JUGADORA: AIGUA VERNE. Un litre: 48 crèdits. I la fletxa, cap amunt. ⟨si preu_aigua = 48⟩
        JUGADORA: AIGUA VERNE. Un litre: 64 crèdits. I la fletxa, cap amunt. ⟨si preu_aigua = 64⟩
        JUGADORA: AIGUA VERNE. Un litre: 97 crèdits. I la fletxa, cap amunt. ⟨si preu_aigua = 97⟩
        JUGADORA: AIGUA VERNE. Un litre: 112 crèdits. I la fletxa, cap amunt. ⟨si preu_aigua = 112⟩
        JUGADORA: AIGUA VERNE. Un litre, i la fletxa. Avui, cap avall. ⟨si preu_aigua ≠ 48 i preu_aigua ≠ 64 i preu_aigua ≠ 97 i preu_aigua ≠ 112⟩
        NARRADOR: AIGUA VERNE · {preu_aigua} ₡ ⟨si preu_aigua ≠ 48 i preu_aigua ≠ 64 i preu_aigua ≠ 97 i preu_aigua ≠ 112⟩
    • use/push/pull/pickUp — SEMPRE
        JUGADORA: Té més cops de pedra que llums. El piquet ja hi ha dit la seva.

CANONADA «Canonada»
    • look — SEMPRE
        JUGADORA: La Canonada de Ferrum. Xucla l'aigua de sota les mines. I els miners, sense.

ROSA «—» — hi és si escena ≥ 4

```

## Sala Sindicat de Ferrum · `ferrum_sindicat` (iri, vet)

```
DECORAT vestit — es veu si NO vestit_agafat

PORTA «carrer»
    • walkTo/use/open — SEMPRE
        ⇒ → ferrum_carrer

BAGUL «bagul»
    • look — si vestit_agafat
        JUGADORA: El bagul de la colla de teatre de la Festa Major. Ja no hi ha el vestit de reina.
    • look — SEMPRE
        JUGADORA: El bagul de la colla de teatre de la Festa Major. A dalt de tot, un vestit de reina de vellut granat, amb lluentons de llautó i una corona feta amb un engranatge.
        IRI: Això és el més lleig que he vist mai. I he estat a Verdant. ⟨si iri a ferrum_sindicat⟩
    • pickUp — si vestit_agafat
        JUGADORA: El vestit ja el tenim. La resta és de la colla de teatre.
    • pickUp — si rosa_permis i NO vestit_agafat
        JUGADORA: Gràcies, Rosa. Ja el tinc.
        ⇒ +vestit_agafat, rep vestit
    • pickUp — si rosa_vol_tomas i NO vestit_agafat
        JUGADORA: La Rosa vol que el vingui a buscar en Tomàs. Ell.
    • pickUp — si cal_gala i NO vestit_agafat
        JUGADORA: És de la Rosa, la minera del piquet. Li ho he de demanar.
    • pickUp — si vestit_volgut
        JUGADORA: És de la Rosa, la minera del piquet. Primer, demanar-l'hi.
    • pickUp — si juga iri i NO vestit_refusat
        JUGADORA: No em posaria això ni morta. I no és meu.
        ⇒ +vestit_refusat
    • pickUp — si NO vestit_refusat
        JUGADORA: És de la colla de teatre. No ens en cal res.
        ⇒ +vestit_refusat
    • pickUp — si juga iri
        JUGADORA: Ni morta, he dit. Però viva i de gala, potser. Per si de cas.
        JUGADORA: És de la Rosa, la minera del piquet. Li ho he de demanar.
        ⇒ +vestit_volgut
    • pickUp — SEMPRE
        JUGADORA: Un vestit de reina, per si de cas... Però és de la Rosa, la minera del piquet. L'hi hauríem de demanar.
        ⇒ +vestit_volgut

PISSARRA «pissarra»
    • look — SEMPRE
        JUGADORA: Torns de vaga i torns d'aigua. Hi ha més torns que aigua.

MOTLLES «motlles»
    • look — SEMPRE
        JUGADORA: Motlles de fosa, en una prestatgeria. En Bru no deixa tocar-los a ningú.
    • pickUp — SEMPRE
        JUGADORA: En Bru em mira. No.

CARTELLS «cartells»
    • look — SEMPRE
        JUGADORA: Cartells de vagues antigues. «1998: QUI FA EL FERRO, FA EL PREU.» No els va sortir bé.

BRU «—»

```

## Sala El palau, al final · `final_palau` — cinemàtica

```
IRI «—»

VERNE «—»

DIVIDEND «—»

HOLM «—»

```

## Sala La granja, sota la pluja · `final_pluja` — cinemàtica

```
DECORAT barril_pou — es veu si NO barril_donat
DECORAT caixa_ferrum — es veu si barril_donat

IRI «—»

VET «—»

DIU «—»

QUIM «—»

```

## Sala Fosa: la colada · `fosa_colada` (iri, vet)

```
EN ENTRAR
    • * — si escena = 4 i motlle_preparat i NO claus_fetes i NO sync_colada i ((vet a fosa_forn i iri a fosa_colada) o (iri a fosa_forn i vet a fosa_colada))
        TÍTOL: Ara necessites les dues.
        NARRADOR: El forn està a vuit. Cada acció el refreda un grau. Si arriba a zero, el metall s'endureix al gresol.
        NARRADOR: Al forn: manxa, metall i fora l'escòria. A la colada: abocar el gresol i tapar amb sorra.
        ⇒ +sync_colada, temperatura := 8

DECORAT motlle_preparat — es veu si motlle_preparat i NO claus_fetes
DECORAT gresol_ple — es veu si sync_colada i escoria_treta i NO colat
DECORAT fum_gresol — es veu si sync_colada i escoria_treta i NO colat
DECORAT claus_fetes — es veu si colat i NO claus_fetes
DECORAT motlle_posat — es veu si claus_fetes

PAS «forn»
    • walkTo/use/open — SEMPRE
        ⇒ → fosa_forn

GRESOL «gresol»
    • look — SEMPRE
        JUGADORA: El gresol, penjat del pont grua. Quan el metall està fos al forn, hi passa i s'aboca al motlle.
    • use — si sync_colada i NO metall_carregat
        JUGADORA: El gresol està buit. Primer, el metall al forn.
    • use — si sync_colada i NO escoria_treta
        [SO: colada] JUGADORA: Abocant...
        NARRADOR: El metall cau al motlle... amb l'escòria. Fa bombolles.
        JUGADORA: Les claus surten amb forats. Això no obre res. Ni una llauna.
        NARRADOR: Es refon tot i es torna a començar.
        ⇒ −manxa_oberta, −metall_carregat, −escoria_treta, temperatura := 8
    • use — si sync_colada i NO colat
        [SO: colada] JUGADORA: Abocant...
        NARRADOR: El metall cau al motlle com mel encesa. Tres claus, tres raigs de llum.
        ⇒ +colat
    • use — si sync_colada
        JUGADORA: Ja és al motlle. Ara, tapar-lo amb sorra.
    • use — si NO motlle_preparat
        JUGADORA: Sense el motlle preparat al llit, no.
    • use — SEMPRE
        JUGADORA: Ja hem fet les claus.

GRUA_PONT «comandaments de la grua»
    • look — SEMPRE
        JUGADORA: Els comandaments del pont grua. Mouen el gresol del forn al motlle.
    • use — si sync_colada i NO metall_carregat
        JUGADORA: El gresol està buit. Primer, el metall al forn.
    • use — si sync_colada i NO escoria_treta
        [SO: colada] JUGADORA: Abocant...
        NARRADOR: El metall cau al motlle... amb l'escòria. Fa bombolles.
        JUGADORA: Les claus surten amb forats. Això no obre res. Ni una llauna.
        NARRADOR: Es refon tot i es torna a començar.
        ⇒ −manxa_oberta, −metall_carregat, −escoria_treta, temperatura := 8
    • use — si sync_colada i NO colat
        [SO: colada] JUGADORA: Abocant...
        NARRADOR: El metall cau al motlle com mel encesa. Tres claus, tres raigs de llum.
        ⇒ +colat
    • use — si sync_colada
        JUGADORA: Ja és al motlle. Ara, tapar-lo amb sorra.
    • use — si NO motlle_preparat
        JUGADORA: Sense el motlle preparat al llit, no.
    • use — SEMPRE
        JUGADORA: Ja hem fet les claus.

LLIT «llit de colada»
    • look — si motlle_preparat
        JUGADORA: El llit de colada, amb el motlle preparat.
    • look — SEMPRE
        JUGADORA: El llit de colada. Aquí va el motlle, ben colgat de sorra.
    • use + motlle — si no (té sorra)
        JUGADORA: Sorra fina, en tenim. Però la porta l'altra. ⟨si sorra_agafada⟩
        JUGADORA: La sorra d'aquí és pedra picada. Les claus sortirien amb grava. Cal sorra fina de debò. ⟨si NO sorra_agafada⟩
        JUGADORA: ...Al fons del mar d'Aqua n'hi havia una platja. Fina com farina. ⟨si NO sorra_agafada⟩
        ⇒ +cal_sorra
    • use + motlle — SEMPRE
        JUGADORA: Sorra fina d'Aqua? En porto un sac. ⟨si NO cal_sorra⟩
        [SO: motlle] JUGADORA: El motlle al llit, ben colgat de sorra fina d'Aqua. Preparat.
        JUGADORA: Ara, una al forn i l'altra aquí, a la colada.
        ⇒ +motlle_preparat, perd motlle
    • use + sorra — si NO motlle_preparat
        JUGADORA: Primer, el motlle.
    • use + sorra — si sync_colada i colat
        [SO: vapor] JUGADORA: Sorra a sobre. A refredar.
        NARRADOR: El vapor puja fins al sostre. Quan s'esvaeix, al motlle hi ha tres claus de ferro, encara roges.
        ⇒ +claus_fetes, perd sorra, rep claus (iri)
    • use + sorra — si sync_colada
        JUGADORA: Primer, el metall al motlle.
    • use — si NO motlle_preparat
        JUGADORA: Al llit hi va el motlle, preparat amb sorra fina.
    • use — si sync_colada i NO colat
        JUGADORA: El motlle espera el metall: s'aboca amb el gresol.
    • use — si sync_colada
        JUGADORA: Ara, tapar-lo: la sorra, al llit.

SORRA_PEDRA «sacs de sorra»
    • look — SEMPRE
        JUGADORA: Sacs de sorra de Ferrum. Pedra picada. Per a un motlle de precisió, no serveix.
    • pickUp — SEMPRE
        JUGADORA: Aquesta no serveix: és pedra picada.

```

## Sala Fosa: el forn · `fosa_forn` (iri, vet)

```
EN ENTRAR
    • * — si escena = 4 i motlle_preparat i NO claus_fetes i NO sync_colada i ((vet a fosa_forn i iri a fosa_colada) o (iri a fosa_forn i vet a fosa_colada))
        TÍTOL: Ara necessites les dues.
        NARRADOR: El forn està a vuit. Cada acció el refreda un grau. Si arriba a zero, el metall s'endureix al gresol.
        NARRADOR: Al forn: manxa, metall i fora l'escòria. A la colada: abocar el gresol i tapar amb sorra.
        ⇒ +sync_colada, temperatura := 8

DECORAT forn_ences — es veu si sync_colada i manxa_oberta
DECORAT forn_fort — es veu si sync_colada i metall_carregat
DECORAT foc — es veu si sync_colada i manxa_oberta i NO metall_carregat
DECORAT foc_fort — es veu si sync_colada i metall_carregat
DECORAT guspires — es veu si sync_colada i manxa_oberta

PORTA «carrer»
    • walkTo/use/open — si sync_colada
        JUGADORA: Ara no em puc moure d'aquí: el forn es refreda.
    • walkTo/use/open — SEMPRE
        ⇒ → ferrum_carrer

PAS «colada»
    • walkTo/use/open — SEMPRE
        ⇒ → fosa_colada

MANXA «manxa»
    • look — SEMPRE
        JUGADORA: La manxa del forn: una palanca grossa que fa bufar el foc.
    • push/pull/use — si sync_colada i NO manxa_oberta
        [SO: manxa] JUGADORA: Manxa!
        NARRADOR: El forn rugeix i s'encén de taronja.
        ⇒ +manxa_oberta
    • push/pull/use — si sync_colada i temperatura ≤ 6
        [SO: manxa] JUGADORA: Més aire. El forn s'enfila.
        ⇒ temperatura += 3
    • push/pull/use — si sync_colada
        JUGADORA: El forn ja està al màxim. Si bufo més, s'enfadarà.
    • push/pull/use — si NO claus_fetes
        JUGADORA: Sense metall i sense motlle preparat, això només fa vent.
    • push/pull/use — SEMPRE
        JUGADORA: Ja tenim les claus. Deixem descansar el forn.

METALL «comptadors per fondre»
    • look — SEMPRE
        JUGADORA: Una pila de comptadors de Verne, per fondre. Que serveixin per a alguna cosa.
    • pickUp/use/push — si sync_colada i NO manxa_oberta
        JUGADORA: Primer, el foc. Sense manxa, aquest forn no fon ni mantega.
    • pickUp/use/push — si sync_colada i NO metall_carregat
        [SO: cops_ferro] JUGADORA: Comptadors de Verne, al forn.
        NARRADOR: El metall comença a fondre's. A sobre hi sura una crosta grisa: l'escòria.
        ⇒ +metall_carregat
    • pickUp/use/push — si sync_colada
        JUGADORA: Ja n'hi ha prou: tres claus no en demanen més.
    • pickUp/use/push — si NO claus_fetes
        JUGADORA: Encara no. Primer, el motlle preparat al llit de colada.
    • pickUp/use/push — SEMPRE
        JUGADORA: Ja hem fet les claus.

RASCLE «rascle»
    • look — SEMPRE
        JUGADORA: Un rascle de ferro llarg per treure l'escòria del metall fos.
    • use — si sync_colada i metall_carregat i NO escoria_treta
        [SO: vapor] JUGADORA: Fora l'escòria.
        NARRADOR: El metall queda net i brillant com un sol petit.
        ⇒ +escoria_treta
    • use — si sync_colada i NO metall_carregat
        JUGADORA: Encara no hi ha res a escumar.
    • use — si sync_colada
        JUGADORA: Ja està net.
    • use — SEMPRE
        JUGADORA: Ara no cal.

FORN «forn»
    • look — si sync_colada
        JUGADORA: El forn. Si el termòmetre arriba a zero, el metall s'endureix.
        NARRADOR: Termòmetre: {temperatura}
    • look — si NO claus_fetes
        JUGADORA: El forn de la fosa. Fred, de moment.
    • look — SEMPRE
        JUGADORA: El forn, apagat. Ja ha fet la seva feina.
    • use/open — SEMPRE
        JUGADORA: No hi poso la mà. Ni la de l'Iri. ⟨si juga vet⟩
        JUGADORA: No hi poso la mà. Ni la de la Vet. ⟨si juga iri⟩

TERMOMETRE «termòmetre»
    • look — si sync_colada
        JUGADORA: El termòmetre del forn. El metall aguanta fos fins a zero.
        NARRADOR: Termòmetre: {temperatura}
    • look — SEMPRE
        JUGADORA: Un termòmetre de rellotge, gros com una roda.

```

## Sala Casa del pare · `granja_casa` (iri, vet)

```
PORTA «pati»
    • walkTo/use/open — SEMPRE
        ⇒ → granja_pati

CALAIX «calaixos»
    • open/look/use/pull — si NO oferta_vista
        JUGADORA: Cordill, claus de portes que ja no existeixen, factures de fa trenta anys, dotze llapis sense punta...
        JUGADORA: I una carta de Verne S.A.: «Oferim per la finca un crèdit. La terra no val res sense aigua. Signi aquí.»
        IRI: Un crèdit. Si regategem, potser en fem dos. ⟨si iri a granja_casa⟩
        JUGADORA: L'escriptura no hi és.
        ⇒ +oferta_vista
    • look — SEMPRE
        JUGADORA: Res més que el pare no hagi guardat. L'escriptura, aquí no hi és.

VIDEOTELEFON «videotelèfon»
    • look — SEMPRE
        JUGADORA: El videotelèfon. El pare el contesta sempre a la tercera, perquè la primera «és de mala educació».
    • use/talkTo/push — SEMPRE
        [SO: videotelefon] JUGADORA: Ring... ring... ring...
        ⇒ diàleg pare

QUADRE «quadre de la mare» — hi és si NO quadre_apartat
    • look — SEMPRE
        JUGADORA: La mare. La va pintar el pare. Es nota: hi ha posat més cor que traça.
    • push/pull/pickUp/use/open — si pista_quadre
        JUGADORA: Aparto el quadre de la mare... Al darrere hi ha una caixa forta encastada a la paret.
        ⇒ +quadre_apartat
    • push/pull/pickUp/use/open — SEMPRE
        JUGADORA: És el quadre de la mare. No el toco sense un bon motiu.

CAIXA_FORTA «caixa forta» — hi és si quadre_apartat
    • look — si caixa_oberta
        JUGADORA: Buida. El pare no hi guardava res més. Sorprenent.
    • look — SEMPRE
        JUGADORA: Una caixa forta vella amb un teclat de lletres. Cinc caselles: una paraula de cinc lletres.
    • open/use/push — si caixa_oberta
        JUGADORA: Ja està oberta.
    • open/use/push — SEMPRE
        ⇒ diàleg teclat

BOL «bol del gos»
    • look — SEMPRE
        JUGADORA: El bol del gos. Hi diu TITUS, gravat amb un clau.
        JUGADORA: En Titus. Ens esperava a la porta cada dia, quan tornàvem de l'escola. Fa quinze anys que no hi és, i el pare no n'ha llençat el bol.
        ⇒ +bol_vist
    • pickUp — SEMPRE
        JUGADORA: Que es quedi on és. Com tot, en aquesta casa.

POTS «pots»
    • look — SEMPRE
        JUGADORA: Setanta pots de vidre buits. «Per si de cas.»
        VET: ...Jo en tinc trenta a la nau. No diguis res. ⟨si vet a granja_casa⟩
    • pickUp — SEMPRE
        JUGADORA: Si n'agafo un, el pare ho notarà des de la residència.

PICA «pica»
    • look — SEMPRE
        JUGADORA: La pica. Seca.
    • use/open/push/pull — SEMPRE
        JUGADORA: Obro l'aixeta. Fa un soroll com si s'ofegués. No en surt res.

```

## Sala Graner · `granja_graner` (iri, vet)

```
DECORAT sacs_tres — es veu si NO sacs_agafats
DECORAT sac_quart — es veu si NO sac4_agafat
DECORAT tractor_obert — es veu si injector_tret

PORTA «pati»
    • walkTo/use/open — SEMPRE
        ⇒ → granja_pati

TRACTOR «tractor de l'avi»
    • look — si injector_tret
        JUGADORA: El tractor. Ja no té l'injector: és a la Cantimplora, fent volar una nau.
    • look — si juga vet i injector_vist
        JUGADORA: El Brau 40 de l'avi. Té el mateix injector que la Cantimplora: mateix broquet, mateixa rosca. Els feien a la mateixa fàbrica.
    • look — si caixa_oberta
        JUGADORA: El Brau 40 de l'avi. Vermell, rovellat i famós: va costar un pou.
    • look — SEMPRE
        JUGADORA: El tractor de l'avi. No ha arrencat mai, que jo recordi.
    • use + oli — si NO tractor_oliat
        JUGADORA: Oli als cargols del capó i de l'injector. Que s'amarin.
        ⇒ +tractor_oliat, perd oli
    • use + clau_anglesa — si NO tractor_oliat i NO injector_tret
        JUGADORA: El cargol de l'injector està rovellat. Si forço, el trenco. Primer, oli.
    • use + clau_anglesa — si NO injector_tret
        [SO: cargols] JUGADORA: Capó amunt... cargol... cargol... L'injector de l'avi. Sencer!
        VET: El tractor que va costar un pou ens farà volar. ⟨si vet a granja_graner⟩
        IRI: Per fi l'avi va fer un bon negoci. ⟨si iri a granja_graner i vet a granja_graner⟩
        ⇒ +injector_tret, rep injector
    • use/push/pull/open — si NO injector_vist
        JUGADORA: No arrenca. No ha arrencat mai. És un monument.
    • use/push/pull/open — si NO injector_tret
        JUGADORA: L'injector va cargolat al capó. Per treure'l cal una clau anglesa grossa. I oli, perquè està rovellat.
    • use/push/pull/open — SEMPRE
        JUGADORA: Ja li hem pres el que volíem.

LLAVORS «banc de llavors»
    • look — SEMPRE
        JUGADORA: El banc de llavors del pare: blat de secà, cigrons, mongetes de l'avi, tomàquets de la mare... Tot etiquetat a mà. Per si de cas.
    • pickUp — si permis_pare i NO sacs_agafats
        JUGADORA: Tres sacs per a la Juana: secà, cigrons i tomàquet. El quart es queda aquí, que ho ha dit el pare.
        ⇒ +sacs_agafats, rep sacs_llavors
    • pickUp — si juana_llavors i NO permis_pare
        JUGADORA: Són del pare. No me'n vaig a endur ni un sac sense demanar-l'hi.
    • pickUp — si cal_aval i NO sac4_agafat
        JUGADORA: El pare va dir que en guardéssim un, per si de cas. Doncs aquest és el cas.
        ⇒ +sac4_agafat, rep sac_llavors
    • pickUp — si sacs_agafats i sac4_refusat i NO sac4_agafat
        JUGADORA: El pare va dir que en guardéssim un. No va dir on. A la nau també és guardat. Per si de cas.
        ⇒ +sac4_agafat, rep sac_llavors
    • pickUp — si sacs_agafats i NO sac4_agafat
        JUGADORA: El quart sac es queda aquí. El pare ha dit que en guardem un.
        ⇒ +sac4_refusat
    • pickUp — SEMPRE
        JUGADORA: Les llavors del pare no es toquen sense un bon motiu.

REG «reg gota a gota» — hi és si NO reg_agafat
    • look — SEMPRE
        JUGADORA: El reg gota a gota del pare, enrotllat a la paret. Un reg sense aigua. És un acte de fe.
    • pickUp — si permis_reg
        JUGADORA: Me l'emporto. Per a la tomaquera d'en Nil. ⟨si cal_reg⟩
        JUGADORA: «Encara serveix», diu el pare. Doncs que serveixi. Me l'emporto. ⟨si NO cal_reg⟩
        ⇒ +reg_agafat, rep reg
    • pickUp — si cal_reg
        JUGADORA: El pare sempre diu: «El reg no es toca, que encara serveix.» Li ho hauré de demanar pel videotelèfon.
    • pickUp — si reg_refusat
        JUGADORA: Algun dia servirà. Li ho demanaré al pare pel videotelèfon: «per si de cas» és un argument que entén.
        ⇒ +reg_volgut
    • pickUp — SEMPRE
        JUGADORA: El pare sempre diu: «El reg no es toca, que encara serveix.» Ell sabrà per a què.
        ⇒ +reg_refusat

CAIXA_EINES «caixa d'eines»
    • open/pickUp/use — si NO tornavis_agafat
        JUGADORA: Un tornavís vell. Fa de tornavís.
        ⇒ +tornavis_agafat, rep tornavis
    • look — si NO tornavis_agafat
        JUGADORA: La caixa d'eines de l'avi. Hi ha un tornavís.
    • look — SEMPRE
        JUGADORA: Eines que no reconec. L'avi les devia inventar. ⟨si juga iri⟩
        JUGADORA: Eines que ni jo reconec. L'avi les devia inventar. ⟨si juga vet⟩

```

## Sala Pati de la granja · `granja_pati` (iri, vet)

```
EN ENTRAR
    • * (una vegada) — si escena = 1
        VET: Fa sis anys que no venim.
        IRI: Fa sis anys que no plou.
        VET: No és el mateix.
        IRI: Aquí, sí.
        VET: La residència del pare vol tres-cents crèdits al mes de «suplement d'aigua».
        IRI: I nosaltres no en tenim ni trenta. Hem de vendre la granja.
        VET: Per vendre-la cal l'escriptura. Que és en algun racó de la casa del pare.
        IRI: Del pare, que ho guarda tot.
        VET: Tot.
        NARRADOR: (Pots canviar de protagonista amb el botó «Canvia». Totes dues poden fer coses, i es poden donar el que porten.)
    • * (una vegada) — si escena ≥ 5 i NO graner_obert
        JUGADORA: A la porta del graner hi ha un paper groc. El pare no compraria mai res groc.

DECORAT precinte — es veu si escena ≥ 5 i NO graner_obert

PORTA_CASA «casa»
    • look — SEMPRE
        JUGADORA: La porta de casa. El pare no la tancava mai: «Si algú vol entrar, que entri, que no hi ha res a robar.»
    • walkTo/use/open — SEMPRE
        ⇒ → granja_casa

PORTA_GRANER «graner»
    • look — si escena ≥ 5 i NO graner_obert
        JUGADORA: A la porta del graner hi ha un cadenat de Verne, amb una ranura i un llum vermell. I un paper groc.
        JUGADORA: «PRECINTE PREVENTIU. La propietat de la finca 7.788 no ha respost a l'oferta de compra. Mentre no respongui, el graner queda tancat. Només hi pot entrar la propietat.»
        ⇒ +precinte_vist
    • use + escriptura — si escena ≥ 5 i NO graner_obert
        JUGADORA: L'escriptura de la finca, per la ranura...
        NARRADOR: El cadenat la llegeix. El llum es posa verd. «Benvinguda, propietat. Verne S.A. li recorda que l'oferta de compra continua vigent.»
        JUGADORA: Un crèdit. Per tot. Com oblidar-la.
        ⇒ +precinte_vist, +graner_obert
    • use + contracte_7788 — si escena ≥ 5 i NO graner_obert
        NARRADOR: El cadenat llegeix el contracte i fa un soroll de queixa: «Aquest document diu de qui és l'aigua. No de qui és la finca.»
        ⇒ +precinte_vist
    • use + tornavis_flor — si (escena ≥ 5 i NO graner_obert) i juga vet
        JUGADORA: El cadenat va amb cargols de cap de flor. Verne els fa servir perquè no els pugui obrir ningú.
        JUGADORA: Ningú, excepte jo. ...Cadenat a la caixa d'eines. Ja l'inventariaran.
        ⇒ +precinte_vist, +graner_obert
    • use + qualsevol objecte — si escena ≥ 5 i NO graner_obert
        JUGADORA: El cadenat ho mira amb el llum vermell. No.
    • walkTo/use/open — si escena ≥ 5 i NO graner_obert
        JUGADORA: Tancat. Un cadenat de Verne, amb una ranura i un llum vermell.
        JUGADORA: «PRECINTE PREVENTIU. La propietat de la finca 7.788 no ha respost a l'oferta de compra. Mentre no respongui, el graner queda tancat. Només hi pot entrar la propietat.» ⟨si NO precinte_vist⟩
        ⇒ +precinte_vist
    • look — SEMPRE
        JUGADORA: El graner. Hi dormen el tractor de l'avi i les llavors del pare.
    • walkTo/use/open — SEMPRE
        ⇒ → granja_graner

CAMI_PORT «camí del port»
    • look — SEMPRE
        JUGADORA: El camí del port. Allà hi ha la Cantimplora, aparcada i rovellant-se.
    • walkTo/use/open — si escena = 1
        JUGADORA: Primer, l'escriptura. I potser entendre per què el pou està sec.
    • walkTo/use/open — SEMPRE
        ⇒ → port_terra2

POU «pou»
    • look — si NO bomba_llegida
        JUGADORA: El pou. Sec. Hi baixa un tub blanc que no és del pare: el pare no compraria mai res blanc.
    • look — SEMPRE
        JUGADORA: El pou. Sec. El tub de Verne s'hi beu el que queda.
    • use/pull/pickUp — SEMPRE
        JUGADORA: La galleda puja buida. Fa sis anys que puja buida.

BOMBA «bomba de Verne»
    • use + tornavis_flor — si NO bomba_llegida
        [SO: cargols] JUGADORA: Fora cargols.
        JUGADORA: Hi ha una etiqueta: «Estació 7.788. Destinació: Canonada T2. Dipòsit orbital T2.»
        JUGADORA: L'aigua no s'ha acabat. Puja.
        [SO: bomba] NARRADOR: La bomba s'engega sola i fa un soroll de xuclar.
        IRI: Ens beu el pou mentre en parlem. ⟨si iri a granja_pati i vet a granja_pati⟩
        VET: No. Se'l beu ara. En parlem nosaltres. ⟨si iri a granja_pati i vet a granja_pati⟩
        ⇒ +bomba_llegida
    • use + tornavis — si NO bomba_llegida
        JUGADORA: Aquest tornavís no hi fa res: els cargols són de cap de flor. Necessito una punta de flor.
    • use + punta_flor — si NO bomba_llegida
        JUGADORA: La punta sola no gira. Li cal un mànec. Un tornavís.
    • look — si juga vet i NO bomba_llegida
        JUGADORA: Una bomba nova, amb el logotip de Verne. Ningú no posa una bomba al pou d'un altre.
        JUGADORA: El panell està cargolat amb cargols de cap de flor. No els obre cap tornavís del món. Excepte el meu, si li poso la punta.
        ⇒ +bomba_vista
    • look — si NO bomba_llegida
        JUGADORA: Una bomba de Verne al nostre pou. El panell està cargolat amb uns cargols estranys, amb forma de flor.
        JUGADORA: La Vet sempre porta puntes per a cargols rars. «Per si de cas.»
        ⇒ +bomba_vista
    • look — SEMPRE
        JUGADORA: «Estació 7.788. Destinació: Canonada T2. Dipòsit orbital T2.» Ens xucla el pou cap a la Canonada.
    • open/use/pull/push — si NO bomba_llegida
        JUGADORA: Cargols de cap de flor. Amb els dits, no.
    • open/use/pull/push — SEMPRE
        JUGADORA: Si la paro, en vindran deu a engegar-la. I m'enviaran la factura.

CANONADA «Canonada»
    • look — si NO bomba_llegida
        JUGADORA: La Canonada de Terra-2. Una columna blanca que puja fins que no es veu. Va aparèixer fa sis anys. Com la secada.
    • look — SEMPRE
        JUGADORA: La Canonada de Terra-2. Hi va a parar la nostra aigua, i d'allà, a un dipòsit, a dalt de tot.

PANELL_PREU «panell del preu»
    • look — SEMPRE
        JUGADORA: AIGUA VERNE. Un litre: 48 crèdits. I la fletxa, cap amunt. ⟨si preu_aigua = 48⟩
        JUGADORA: AIGUA VERNE. Un litre: 64 crèdits. I la fletxa, cap amunt. ⟨si preu_aigua = 64⟩
        JUGADORA: AIGUA VERNE. Un litre: 97 crèdits. I la fletxa, cap amunt. ⟨si preu_aigua = 97⟩
        JUGADORA: AIGUA VERNE. Un litre: 112 crèdits. I la fletxa, cap amunt. ⟨si preu_aigua = 112⟩
        JUGADORA: AIGUA VERNE. Un litre, i la fletxa. Avui, cap avall. ⟨si preu_aigua ≠ 48 i preu_aigua ≠ 64 i preu_aigua ≠ 97 i preu_aigua ≠ 112⟩
        NARRADOR: AIGUA VERNE · {preu_aigua} ₡ ⟨si preu_aigua ≠ 48 i preu_aigua ≠ 64 i preu_aigua ≠ 97 i preu_aigua ≠ 112⟩
    • use/push/pull/pickUp — SEMPRE
        JUGADORA: És de Verne. Si el toco, segur que algú em cobra el dit.

ARBRE «olivera»
    • look — SEMPRE
        JUGADORA: L'olivera de l'avi. Va aguantar dues guerres i una plaga. La secada, no.
    • pickUp/pull/push — SEMPRE
        JUGADORA: La deixo estar. Ja ha patit prou.

TANCA «tanca»
    • look — SEMPRE
        JUGADORA: La tanca. Ja no hi queda res a tancar.

DIU «—» — hi és si escena = 1

```

## Sala Sala de control · `palau_control` (vet)

```
EN ENTRAR
    • * — si escena = 7 i té claus (vet) i vet a palau_control i iri a palau_salo i NO subhasta_comencada
        MAGNAT VERNE: Benvinguts a la Gran Subhasta de l'Aigua. Avui no venem aigua. Venem set. Que és el que no s'acaba mai.
        HOLM: Lots u a quatre: el subsòl de Terra-2, deu anys. Per comarques.
        TÍTOL: Ara necessites les dues.
        NARRADOR: Dotze lots. Quan s'acabin, el Magnat haurà venut l'aigua de deu anys, i el preu ja no el podrà arruïnar.
        NARRADOR: Vet: tres panys. Iri: fer que la subhasta duri.
        ⇒ +subhasta_comencada, +sync_subhasta, lots := 12
    • * (una vegada) — SEMPRE
        NARRADOR: La sala de control. El sostre és el fons de vidre de la piscina central, buida.
        JUGADORA: Tres panys: T2, AQUA, FERRUM, cadascun amb el seu indicador de gel. I una palanca vermella: RESERVA.
        JUGADORA: Ara cal que la subhasta comenci, amb l'Iri al saló. Si obro les vàlvules abans, el Magnat no s'haurà jugat res. ⟨si NO subhasta_comencada⟩

DECORAT obert_t2 — es veu si obert_t2
DECORAT obert_aqua — es veu si obert_aqua
DECORAT obert_ferrum — es veu si obert_ferrum
DECORAT reserva_oberta — es veu si reserva_oberta
DECORAT flors_camera — es veu si subhasta_comencada

ASCENSOR «ascensor»
    • walkTo/use/open — si sync_subhasta
        JUGADORA: No. Ara no em moc d'aquí.
    • walkTo/use/open — SEMPRE
        [SO: ascensor] NARRADOR: L'ascensor puja.
        ⇒ → palau_servei

PANY_T2 «pany T2»
    • look — si obert_t2
        JUGADORA: Pany T2: el dipòsit de Terra-2. Obert. L'indicador del gel baixa cap a zero.
    • look — SEMPRE
        JUGADORA: Pany T2: la vàlvula d'emergència del dipòsit de Terra-2, per a una clau grossa. A l'indicador: deu milions de tones de gel.
    • use + claus — si no (sync_subhasta)
        JUGADORA: Encara no. Si l'obro abans de la subhasta, el Magnat no s'haurà jugat res.
    • use + claus — si sync_subhasta i NO clau_t2
        JUGADORA: Clau al pany. Gira dura.
        ⇒ +clau_t2
    • use + claus — SEMPRE
        JUGADORA: Ja hi ha la clau.
    • open/push/pull/use — si sync_subhasta i NO clau_t2
        JUGADORA: Primer, la clau.
    • open/push/pull/use — si sync_subhasta i NO obert_t2
        [SO: pany] JUGADORA: Giro...
        [SO: valvula] NARRADOR: Un tro profund, sota els peus. A la pantalla del saló, el dipòsit de Terra-2 s'obre, i a sota, Terra-2 es tapa de núvols.
          ⇒ +obert_t2, valvules += 1, preu_aigua −= 10
        MAGNAT VERNE: Terra-2. Pagesos. Que reguin. Encara em queden dos planetes. ⟨si valvules = 1⟩
        NARRADOR: A la pantalla del saló: {preu_aigua}. ⟨si valvules < 3⟩
        NARRADOR: A la pantalla: 31. Per sobre de la ratlla. Per poc. ⟨si valvules = 3⟩
        NARRADOR: La línia baixa, però encara és per sobre de 60, lluny de la ratlla vermella. El Magnat remata dos lots més, corrent. ⟨si preu_aigua ≥ 60⟩
          ⇒ cuita := 2
        NARRADOR: La línia ja és per sota de 60, a tocar de la ratlla vermella. El Magnat pica el martell sense parar: quatre lots més. ⟨si preu_aigua < 60⟩
          ⇒ cuita := 4
        NARRADOR: El Magnat truca a la sala de control. ⟨si valvules = 1⟩
        LIA: (per l'interfon, des del passadís) Tot en ordre, senyor. Netejant. ⟨si valvules = 1⟩
        MAGNAT VERNE: Senyora Pell. Seguretat a la sala de control. Ara. ⟨si valvules = 2⟩
        SRA. PELL: Seguretat és al moll de càrrega, senyor. Hi ha una cisterna que diu que ha perdut els frens. ⟨si valvules = 2⟩
        CAPITANA OR: (per ràdio) Perdoni, perdoni! Soc vella i bòrnia! ⟨si valvules = 2⟩
        NARRADOR: El Magnat truca pel seu canal al mecànic de la Cantimplora. ⟨si valvules = 3⟩
        TOMÀS: Aquí el mecànic. Les germanes han plegat. Són a Verdant, plorant. Hem menjat llenties. ⟨si valvules = 3⟩
        NARRADOR: El Magnat penja, content. ⟨si valvules = 3⟩
        MAGNAT VERNE: Holm. Holm, és un error tècnic. Demà torna a pujar. ⟨si valvules = 3⟩
        HOLM: Trenta-un, senyor Verne. Per sobre de trenta. Per poc. ⟨si valvules = 3⟩
        MAGNAT VERNE: I tinc la meva reserva. Garantia pròpia. Senyors: el preu de l'aigua no baixa mai de trenta mentre jo tingui una gota guardada. ⟨si valvules = 3⟩
    • open/push/pull/use — si obert_t2
        JUGADORA: Obert. Ja no es pot tancar.
    • open/push/pull/use — SEMPRE
        JUGADORA: Sense clau, no gira.

PANY_AQUA «pany AQUA»
    • look — si obert_aqua
        JUGADORA: Pany AQUA: el dipòsit d'Aqua. Obert. L'indicador del gel baixa cap a zero.
    • look — SEMPRE
        JUGADORA: Pany AQUA: la vàlvula d'emergència del dipòsit d'Aqua, per a una clau grossa. A l'indicador: cinquanta-cinc milions de tones de gel.
    • use + claus — si no (sync_subhasta)
        JUGADORA: Encara no. Si l'obro abans de la subhasta, el Magnat no s'haurà jugat res.
    • use + claus — si sync_subhasta i NO clau_aqua
        JUGADORA: Clau al pany. Gira dura.
        ⇒ +clau_aqua
    • use + claus — SEMPRE
        JUGADORA: Ja hi ha la clau.
    • open/push/pull/use — si sync_subhasta i NO clau_aqua
        JUGADORA: Primer, la clau.
    • open/push/pull/use — si sync_subhasta i NO obert_aqua
        [SO: pany] JUGADORA: Giro...
        [SO: valvula] NARRADOR: Un tro profund, sota els peus. A la pantalla del saló, el dipòsit d'Aqua s'obre, i a sota, Aqua es tapa de núvols.
          ⇒ +obert_aqua, valvules += 1, preu_aigua −= 55
        MAGNAT VERNE: Aqua? Cinquanta mil persones i ni un client solvent. Que plogui. ⟨si valvules = 1⟩
        NARRADOR: A la pantalla del saló: {preu_aigua}. ⟨si valvules < 3⟩
        NARRADOR: A la pantalla: 31. Per sobre de la ratlla. Per poc. ⟨si valvules = 3⟩
        NARRADOR: La línia baixa, però encara és per sobre de 60, lluny de la ratlla vermella. El Magnat remata dos lots més, corrent. ⟨si preu_aigua ≥ 60⟩
          ⇒ cuita := 2
        NARRADOR: La línia ja és per sota de 60, a tocar de la ratlla vermella. El Magnat pica el martell sense parar: quatre lots més. ⟨si preu_aigua < 60⟩
          ⇒ cuita := 4
        NARRADOR: El Magnat truca a la sala de control. ⟨si valvules = 1⟩
        LIA: (per l'interfon, des del passadís) Tot en ordre, senyor. Netejant. ⟨si valvules = 1⟩
        MAGNAT VERNE: Senyora Pell. Seguretat a la sala de control. Ara. ⟨si valvules = 2⟩
        SRA. PELL: Seguretat és al moll de càrrega, senyor. Hi ha una cisterna que diu que ha perdut els frens. ⟨si valvules = 2⟩
        CAPITANA OR: (per ràdio) Perdoni, perdoni! Soc vella i bòrnia! ⟨si valvules = 2⟩
        NARRADOR: El Magnat truca pel seu canal al mecànic de la Cantimplora. ⟨si valvules = 3⟩
        TOMÀS: Aquí el mecànic. Les germanes han plegat. Són a Verdant, plorant. Hem menjat llenties. ⟨si valvules = 3⟩
        NARRADOR: El Magnat penja, content. ⟨si valvules = 3⟩
        MAGNAT VERNE: Holm. Holm, és un error tècnic. Demà torna a pujar. ⟨si valvules = 3⟩
        HOLM: Trenta-un, senyor Verne. Per sobre de trenta. Per poc. ⟨si valvules = 3⟩
        MAGNAT VERNE: I tinc la meva reserva. Garantia pròpia. Senyors: el preu de l'aigua no baixa mai de trenta mentre jo tingui una gota guardada. ⟨si valvules = 3⟩
    • open/push/pull/use — si obert_aqua
        JUGADORA: Obert. Ja no es pot tancar.
    • open/push/pull/use — SEMPRE
        JUGADORA: Sense clau, no gira.

PANY_FERRUM «pany FERRUM»
    • look — si obert_ferrum
        JUGADORA: Pany FERRUM: el dipòsit de Ferrum. Obert. L'indicador del gel baixa cap a zero.
    • look — SEMPRE
        JUGADORA: Pany FERRUM: la vàlvula d'emergència del dipòsit de Ferrum, per a una clau grossa. A l'indicador: setze milions de tones de gel.
    • use + claus — si no (sync_subhasta)
        JUGADORA: Encara no. Si l'obro abans de la subhasta, el Magnat no s'haurà jugat res.
    • use + claus — si sync_subhasta i NO clau_ferrum
        JUGADORA: Clau al pany. Gira dura.
        ⇒ +clau_ferrum
    • use + claus — SEMPRE
        JUGADORA: Ja hi ha la clau.
    • open/push/pull/use — si sync_subhasta i NO clau_ferrum
        JUGADORA: Primer, la clau.
    • open/push/pull/use — si sync_subhasta i NO obert_ferrum
        [SO: pany] JUGADORA: Giro...
        [SO: valvula] NARRADOR: Un tro profund, sota els peus. A la pantalla del saló, el dipòsit de Ferrum s'obre, i a sota, Ferrum es tapa de núvols.
          ⇒ +obert_ferrum, valvules += 1, preu_aigua −= 16
        MAGNAT VERNE: Ferrum. Els vaguistes. Ara tenen aigua i no tenen feina. Ja tornaran. ⟨si valvules = 1⟩
        NARRADOR: A la pantalla del saló: {preu_aigua}. ⟨si valvules < 3⟩
        NARRADOR: A la pantalla: 31. Per sobre de la ratlla. Per poc. ⟨si valvules = 3⟩
        NARRADOR: La línia baixa, però encara és per sobre de 60, lluny de la ratlla vermella. El Magnat remata dos lots més, corrent. ⟨si preu_aigua ≥ 60⟩
          ⇒ cuita := 2
        NARRADOR: La línia ja és per sota de 60, a tocar de la ratlla vermella. El Magnat pica el martell sense parar: quatre lots més. ⟨si preu_aigua < 60⟩
          ⇒ cuita := 4
        NARRADOR: El Magnat truca a la sala de control. ⟨si valvules = 1⟩
        LIA: (per l'interfon, des del passadís) Tot en ordre, senyor. Netejant. ⟨si valvules = 1⟩
        MAGNAT VERNE: Senyora Pell. Seguretat a la sala de control. Ara. ⟨si valvules = 2⟩
        SRA. PELL: Seguretat és al moll de càrrega, senyor. Hi ha una cisterna que diu que ha perdut els frens. ⟨si valvules = 2⟩
        CAPITANA OR: (per ràdio) Perdoni, perdoni! Soc vella i bòrnia! ⟨si valvules = 2⟩
        NARRADOR: El Magnat truca pel seu canal al mecànic de la Cantimplora. ⟨si valvules = 3⟩
        TOMÀS: Aquí el mecànic. Les germanes han plegat. Són a Verdant, plorant. Hem menjat llenties. ⟨si valvules = 3⟩
        NARRADOR: El Magnat penja, content. ⟨si valvules = 3⟩
        MAGNAT VERNE: Holm. Holm, és un error tècnic. Demà torna a pujar. ⟨si valvules = 3⟩
        HOLM: Trenta-un, senyor Verne. Per sobre de trenta. Per poc. ⟨si valvules = 3⟩
        MAGNAT VERNE: I tinc la meva reserva. Garantia pròpia. Senyors: el preu de l'aigua no baixa mai de trenta mentre jo tingui una gota guardada. ⟨si valvules = 3⟩
    • open/push/pull/use — si obert_ferrum
        JUGADORA: Obert. Ja no es pot tancar.
    • open/push/pull/use — SEMPRE
        JUGADORA: Sense clau, no gira.

PALANCA «palanca de la reserva»
    • look — si lia_reserva
        JUGADORA: RESERVA. La reserva personal del Magnat: el seu últim barril. Ple. Sota la piscina central.
    • look — SEMPRE
        JUGADORA: Una palanca vermella: RESERVA. Diu la Lia que no es pot tocar mai.
    • pull/use — si sync_subhasta i (obert_t2 i obert_aqua i obert_ferrum)
        VET: L'últim barril.
        IRI: (pel comunicador) Vet.
        VET: Ja ho sé. Ja ho sé.
        [SO: palanca] NARRADOR: La Vet estira la palanca.
        [SO: piscina] NARRADOR: Sobre el seu cap, la piscina central s'omple. I la del costat. I la del costat...
        ⇒ +reserva_oberta, preu_aigua := 29
    • pull/use — si sync_subhasta
        JUGADORA: La reserva, l'última. Primer, els tres dipòsits: que el Magnat s'hi aferri.
    • pull/use — SEMPRE
        JUGADORA: No es pot tocar mai, diu la Lia. I encara no és l'hora.

INTERFON «interfon»
    • look — SEMPRE
        JUGADORA: L'interfon. Hi truca el Magnat quan vol saber si tot va bé. La Lia contestarà.
    • use/talkTo — SEMPRE
        JUGADORA: Millor no dir res. La meva veu no és de servei.

CAMERA «càmera»
    • look — si subhasta_comencada
        JUGADORA: Una càmera. En Nil hi ha posat unes flors de plàstic al davant. «Feien pols.»
    • look — SEMPRE
        JUGADORA: Una càmera de vigilància. Mira els panys.

```

## Sala Galeria de les piscines · `palau_galeria` (iri)

```
EN ENTRAR
    • * (una vegada) — SEMPRE
        NARRADOR: El palau orbital del Magnat. Vint-i-tres piscines. Ni una gota.
        MAGNAT VERNE: Senyora Pruna! Verdant Holdings. Quin honor. Quin... vestit.
        IRI: És avantguardista.
        MAGNAT VERNE: Ho veig. Ho veig. La subhasta començarà al saló quan tothom tingui una copa a la mà.
        IRI: (baix) Ni m'ha mirat la cara. Només el vestit.

DECORAT piscines_plenes — es veu si reserva_oberta

PORTA_SALO «saló»
    • walkTo/use/open — SEMPRE
        ⇒ → palau_salo

PISCINES «piscines»
    • look — SEMPRE
        JUGADORA: Vint-i-tres piscines. Netes, brillants, sense aigua. El palau més sec de Vesper.
    • use/walkTo — SEMPRE
        JUGADORA: No hi baixo. Si em trenco una cama en una piscina buida, el Magnat em cobrarà la rajola.

AQUARI «aquari»
    • look — SEMPRE
        JUGADORA: Trenta-tres peixos d'Aqua. Un rètol: «Lot 12. Darrers exemplars. Preu de sortida: a la baixa d'exemplars.»
        JUGADORA: Com menys en quedin...
        MAGNAT VERNE: ...més valen. Ho ha entès a la primera, senyora Pruna. ⟨si NO subhasta_comencada⟩
    • open/use/pickUp — SEMPRE
        JUGADORA: Si l'obro aquí, davant de tothom, se m'acaba el vestit i la subhasta.

FINESTRAL «finestral»
    • look — SEMPRE
        JUGADORA: L'espai. Terra-2, petita. I un dipòsit blanc amb la gota blava, gros com una ciutat.

ESCALES «escales cromades»
    • look — SEMPRE
        JUGADORA: Escales cromades per baixar a les piscines. Ningú no les ha baixat mai.

VERNE «—» — hi és si NO subhasta_comencada

DIVIDEND «—»

```

## Sala Saló de la subhasta · `palau_salo` (iri)

```
EN ENTRAR
    • * — si escena = 7 i té claus (vet) i vet a palau_control i iri a palau_salo i NO subhasta_comencada
        MAGNAT VERNE: Benvinguts a la Gran Subhasta de l'Aigua. Avui no venem aigua. Venem set. Que és el que no s'acaba mai.
        HOLM: Lots u a quatre: el subsòl de Terra-2, deu anys. Per comarques.
        TÍTOL: Ara necessites les dues.
        NARRADOR: Dotze lots. Quan s'acabin, el Magnat haurà venut l'aigua de deu anys, i el preu ja no el podrà arruïnar.
        NARRADOR: Vet: tres panys. Iri: fer que la subhasta duri.
        ⇒ +subhasta_comencada, +sync_subhasta, lots := 12

DECORAT grafic_112 — es veu si preu_aigua ≥ 104
DECORAT grafic_t2 — es veu si ordre_valvules = "t2"
DECORAT grafic_ferrum — es veu si ordre_valvules = "ferrum"
DECORAT grafic_aqua — es veu si ordre_valvules = "aqua"
DECORAT grafic_t2_ferrum — es veu si ordre_valvules = "t2_ferrum"
DECORAT grafic_t2_aqua — es veu si ordre_valvules = "t2_aqua"
DECORAT grafic_ferrum_t2 — es veu si ordre_valvules = "ferrum_t2"
DECORAT grafic_ferrum_aqua — es veu si ordre_valvules = "ferrum_aqua"
DECORAT grafic_aqua_t2 — es veu si ordre_valvules = "aqua_t2"
DECORAT grafic_aqua_ferrum — es veu si ordre_valvules = "aqua_ferrum"
DECORAT grafic_t2_ferrum_aqua — es veu si ordre_valvules = "t2_ferrum_aqua" i NO reserva_oberta
DECORAT grafic_t2_ferrum_aqua_reserva — es veu si ordre_valvules = "t2_ferrum_aqua" i reserva_oberta
DECORAT grafic_t2_aqua_ferrum — es veu si ordre_valvules = "t2_aqua_ferrum" i NO reserva_oberta
DECORAT grafic_t2_aqua_ferrum_reserva — es veu si ordre_valvules = "t2_aqua_ferrum" i reserva_oberta
DECORAT grafic_ferrum_t2_aqua — es veu si ordre_valvules = "ferrum_t2_aqua" i NO reserva_oberta
DECORAT grafic_ferrum_t2_aqua_reserva — es veu si ordre_valvules = "ferrum_t2_aqua" i reserva_oberta
DECORAT grafic_ferrum_aqua_t2 — es veu si ordre_valvules = "ferrum_aqua_t2" i NO reserva_oberta
DECORAT grafic_ferrum_aqua_t2_reserva — es veu si ordre_valvules = "ferrum_aqua_t2" i reserva_oberta
DECORAT grafic_aqua_t2_ferrum — es veu si ordre_valvules = "aqua_t2_ferrum" i NO reserva_oberta
DECORAT grafic_aqua_t2_ferrum_reserva — es veu si ordre_valvules = "aqua_t2_ferrum" i reserva_oberta
DECORAT grafic_aqua_ferrum_t2 — es veu si ordre_valvules = "aqua_ferrum_t2" i NO reserva_oberta
DECORAT grafic_aqua_ferrum_t2_reserva — es veu si ordre_valvules = "aqua_ferrum_t2" i reserva_oberta

PORTA_GALERIA «galeria»
    • walkTo/use/open — si sync_subhasta
        JUGADORA: No me'n vaig: si el saló es buida, la subhasta s'acaba abans.
    • walkTo/use/open — SEMPRE
        ⇒ → palau_galeria

ESCENARI «escenari»
    • look — si sync_subhasta
        JUGADORA: L'escenari: el faristol, el martell i el Magnat, somrient.
        NARRADOR: Al faristol, el lot {lot}.
    • look — SEMPRE
        JUGADORA: L'escenari, el faristol i el martell. Encara buit.
    • use — si sync_subhasta
        ⇒ diàleg subhasta
    • use — SEMPRE
        JUGADORA: Encara no ha començat res.

PANTALLA «pantalla»
    • look — si reserva_oberta
        JUGADORA: Vint-i-nou. Sota la ratlla. Ningú no aplaudeix.
    • look — si sync_subhasta
        JUGADORA: El gràfic del preu, i la ratlla vermella a 30: «LLINDAR DEL BANC». Com més s'hi acosta la línia, més de pressa pica el martell el Magnat.
        NARRADOR: AIGUA VERNE · {preu_aigua} ₡
        JUGADORA: A sota, el catàleg. Lots 1 a 4: el subsòl de Terra-2. 5 a 8: la cartera de deutors. 9 a 11: el mar d'Aqua. 12: els peixos d'Aqua.
    • look — SEMPRE
        JUGADORA: El gràfic del preu de l'aigua. I una ratlla vermella a 30: «LLINDAR DEL BANC». La línia, de moment, ben amunt.
        NARRADOR: AIGUA VERNE · {preu_aigua} ₡
        JUGADORA: A sota, el catàleg. Lots 1 a 4: el subsòl de Terra-2. 5 a 8: la cartera de deutors. 9 a 11: el mar d'Aqua. 12: els peixos d'Aqua.

SAFATA «safata de les copes»
    • look — SEMPRE
        JUGADORA: La safata de les copes. Els cambrers se l'enduen per l'ascensor de servei i la tornen plena.
    • use + qualsevol objecte — si NO holm_parlat
        JUGADORA: En Holm no em treu els ulls de sobre. Si deixo res a la safata ara, ho veurà.
    • use + qualsevol objecte — SEMPRE
        ⇒ acció safata.posar

CAVA «cava»
    • look — SEMPRE
        JUGADORA: Cava de Verdant. De raïm de plàstic, segur.
    • pickUp — si NO copa
        JUGADORA: Una copa a la mà. Ara semblo una inversora. Bé: una inversora amb corona d'engranatge.
    • pickUp — SEMPRE
        JUGADORA: Ja en tinc una.

MARTELL «martell»
    • look — SEMPRE
        JUGADORA: El martell de la subhasta. Cada cop que pica, algú es queda sense aigua deu anys.
    • pickUp/use — SEMPRE
        JUGADORA: Si li prenc el martell, en trauran un altre. Aquí tenen de tot, repetit.

VERNE «—» — hi és si subhasta_comencada

HOLM «—»

KESSEL «—»

```

## Sala Passadissos de servei · `palau_servei` (vet)

```
EN ENTRAR
    • * (una vegada) — SEMPRE
        NARRADOR: Els passadissos de servei del palau. Grisos. Aquí no hi ha piscines.
        NIL: Jo vaig a treure la pols. Tu fes com si sabessis on vas.
        VET: Ho faig cada dia.

ASCENSOR «ascensor de servei»
    • look — SEMPRE
        JUGADORA: L'ascensor de servei. Lector de targetes. Baixa a la sala de control, sota la piscina central.
    • walkTo/use/open — si no (té targeta)
        JUGADORA: Lector de targetes. Sense targeta, l'ascensor no es mou. La Lia en deu tenir una.
    • walkTo/use/open — SEMPRE
        [SO: ascensor] NARRADOR: L'ascensor baixa.
        ⇒ → palau_control

SAFATES «safates»
    • look — SEMPRE
        JUGADORA: El passaplats on els cambrers deixen les safates del saló.
    • pickUp/use/open — SEMPRE
        ⇒ acció safata.recollir

CARRO «carro de flors»
    • look — SEMPRE
        JUGADORA: El carro de flors de plàstic d'en Nil.
    • pickUp — SEMPRE
        JUGADORA: En Nil me les deixaria, però ja s'ocupa ell de les flors.

CANONADES «canonades»
    • look — SEMPRE
        JUGADORA: Canonades gruixudes que baixen cap a la sala de control. Aquí passa tota l'aigua del palau. És a dir, cap.

LIA «—»

NIL «—»

```

## Sala Port de Terra-2 · `port_terra2` (iri, vet)

```
EN ENTRAR
    • * (una vegada) — SEMPRE
        NARRADOR: El port de Terra-2. Fa tres mesos que no surt cap nau de càrrega.
        JUGADORA: La Cantimplora és on la vam deixar: rovellant-se. La Capitana deu ser al pont.

CAMI_GRANJA «camí de la granja»
    • walkTo/use/open — SEMPRE
        ⇒ → granja_pati

RAMPA «Cantimplora»
    • look — SEMPRE
        JUGADORA: La Cantimplora. Nou dipòsits buits, un motor tossut i la Capitana. Casa.
    • walkTo/use/open — SEMPRE
        ⇒ → cantimplora_bodega

TAULER «tauler d'anuncis»
    • look — SEMPRE
        JUGADORA: Feines: «Transport d'aigua Verne. Requisit: no fer preguntes.» «Transport d'aigua Verne. Requisit: no tenir nau pròpia.»
        JUGADORA: I un de diferent: «Es busca nau... per desballestar.»
    • pickUp — SEMPRE
        JUGADORA: Cap d'aquestes feines ens porta on volem.

PANELL_PREU «panell del preu»
    • look — SEMPRE
        JUGADORA: AIGUA VERNE. Un litre: 48 crèdits. I la fletxa, cap amunt. ⟨si preu_aigua = 48⟩
        JUGADORA: AIGUA VERNE. Un litre: 64 crèdits. I la fletxa, cap amunt. ⟨si preu_aigua = 64⟩
        JUGADORA: AIGUA VERNE. Un litre: 97 crèdits. I la fletxa, cap amunt. ⟨si preu_aigua = 97⟩
        JUGADORA: AIGUA VERNE. Un litre: 112 crèdits. I la fletxa, cap amunt. ⟨si preu_aigua = 112⟩
        JUGADORA: AIGUA VERNE. Un litre, i la fletxa. Avui, cap avall. ⟨si preu_aigua ≠ 48 i preu_aigua ≠ 64 i preu_aigua ≠ 97 i preu_aigua ≠ 112⟩
        NARRADOR: AIGUA VERNE · {preu_aigua} ₡ ⟨si preu_aigua ≠ 48 i preu_aigua ≠ 64 i preu_aigua ≠ 97 i preu_aigua ≠ 112⟩
    • use/push/pull/pickUp — SEMPRE
        JUGADORA: El mateix panell que a la granja. Verne no gasta imaginació: gasta panells.

CANONADA «Canonada»
    • look — SEMPRE
        JUGADORA: La Canonada, des del port. Fa l'efecte que el cel té un tub de reg.

```

## Sala Portada · `portada`

```
```

## Sala Ferrum, la font · `postcredits` — cinemàtica

```
VERNE «—»

DIVIDEND «—»

ROSA «—»

```

## Sala Despatx del Magnat · `proleg_palau` — cinemàtica

```
EN ENTRAR
    • * — SEMPRE
        NARRADOR: Mentrestant, en òrbita, al palau, el Magnat grava un anunci.
        MAGNAT VERNE: A Verne S.A. creiem que l'aigua és massa important per deixar-la en mans de la pluja.
        MAGNAT VERNE: Aigua Verne. Perquè la set no espera.
        NARRADOR: La llum s'apaga. El Magnat deixa de somriure com qui es treu un abric.
          ⇒ +proleg_focus
        MAGNAT VERNE: Senyora Pell. És dilluns. Apugeu-la dos crèdits.
        SRA. PELL: A Ferrum diuen que si puja més, faran vaga.
        MAGNAT VERNE: Doncs que la facin. Qui no treballa no beu.
          ⇒ +proleg_preu
        NARRADOR: Al costat de la piscina buida, en Dividend, amb banyador, gemega.
        MAGNAT VERNE: No, Dividend. Aquesta aigua no és per a tu.
        MAGNAT VERNE: No és per a ningú.
        NARRADOR: Passa per davant de l'aquari: trenta-tres peixos platejats. Hi dona un copet al vidre.
        MAGNAT VERNE: Aguanteu, petits. Encara sou massa.
        TÍTOL: Aigua Verne
        TÍTOL: Acte 1 · L'aigua que no hi és
        ⇒ → granja_pati

DECORAT preu48 — es veu si proleg_preu
DECORAT preu46 — es veu si NO proleg_preu
DECORAT focus_apagat — es veu si proleg_focus

VERNE «—»

DIVIDEND «—»

```

## Sala Terra-2 · `proleg_terra2` — cinemàtica

```
EN ENTRAR
    • * — SEMPRE
        NARRADOR: Vesper. Un sistema petit, al voltant d'una estrella taronja.
        [SO: bomba] NARRADOR: Terra-2. Granges, pols i pous. Al pou de cada granja hi ha una bomba amb una gota blava.
        NARRADOR: La Canonada puja l'aigua cel amunt, fins als dipòsits de Verne S.A. Allà dalt, es glaça.
        [SO: motor_apaga] NARRADOR: La Cantimplora, una nau cisterna, portava aigua d'un planeta a l'altre. Ja no en queda per portar.
        NARRADOR: L'Iri, la pilot, i la Vet, l'enginyera, tornen a la granja on van créixer. A vendre-la.
        NARRADOR: L'aigua no s'ha acabat. Està guardada.
        ⇒ → proleg_palau

```

## Sala Cobert del jardiner · `verdant_cobert` (iri, vet)

```
DECORAT reg_muntat — es veu si reg_muntat
DECORAT tomaquera_viva — es veu si tomaquera_regada

PORTA «jardí»
    • walkTo/use/open — SEMPRE
        ⇒ → verdant_jardi

TOMAQUERA «tomaquera»
    • look — si tomaquera_regada
        JUGADORA: La tomaquera, verda. Beu a poc a poc, com ha de ser.
    • look — SEMPRE
        JUGADORA: Una tomaquera. De debò. Mig seca, amagada darrere dels sacs.
        JUGADORA: Algú la rega a escondides. Poc. Massa poc.
        ⇒ +tomaquera_vista
    • use + reg — si juga vet
        JUGADORA: Els goters del reg estan tapats de pols de sis anys. Si no els foradem, no regaran.
        JUGADORA: Necessito alguna cosa per foradar-los. Una agulla. ...En tinc una al calaix de la nau.
        ⇒ +cal_agulla
    • use + reg_foradat — si juga vet
        JUGADORA: Tubs al test, goters a la terra, el cap del tub a punt per a l'aigua.
        ⇒ +reg_muntat, perd reg_foradat
    • use + reg — SEMPRE
        JUGADORA: Això ho ha de muntar la Vet.
    • use + reg_foradat — SEMPRE
        JUGADORA: Això ho ha de muntar la Vet.
    • use + galleda_plena — si reg_muntat
        [SO: regar] JUGADORA: L'aigua del Magnat, gota a gota, cap a la tomaquera.
        NARRADOR: La terra s'enfosqueix. Les fulles s'aixequen, a poc a poc, com si es despertessin.
        ⇒ +tomaquera_regada, perd galleda_plena
    • use + galleda_plena — SEMPRE
        JUGADORA: Si l'aboco de cop, l'ofego: la terra està tan seca que l'aigua hi rellisca. Ha de caure a poc a poc. Gota a gota.
        ⇒ +cal_reg
    • use + qualsevol objecte — SEMPRE
        JUGADORA: Això no la farà créixer.
    • pickUp — SEMPRE
        JUGADORA: No és meva. I és la cosa més valuosa de Verdant.

GALLEDA «galleda» — hi és si NO galleda_agafada
    • look — SEMPRE
        JUGADORA: Una galleda de zinc. Buida.
    • pickUp — SEMPRE
        JUGADORA: Me l'emporto. En Nil no la fa servir: no té res per omplir-la.
        ⇒ +galleda_agafada, rep galleda

SACS «sacs d'adob»
    • look — SEMPRE
        JUGADORA: Sacs d'adob per a plantes de plàstic. Ningú no sap què hi ha a dins. Ni per a què.

EINES «eines»
    • look — SEMPRE
        JUGADORA: Eines de jardí, netes i gastades. Unes tisores de podar que no han podat res de viu en anys.

```

## Sala Jardí de la residència · `verdant_jardi` (iri, vet)

```
EN ENTRAR
    • * (una vegada) — SEMPRE
        NARRADOR: Verdant. On viuen els que poden pagar l'aigua. La gespa és de plàstic, les flors són de plàstic, i l'olor de gespa és d'esprai.
        IRI: A Verdant, ningú no saluda qui va amb roba de feina. ⟨si iri a verdant_jardi i vet a verdant_jardi⟩
        VET: Doncs no saludaré. ⟨si iri a verdant_jardi i vet a verdant_jardi⟩
        JUGADORA: A Verdant, ningú no saluda qui va amb roba de feina. La Vet hi farà molts amics. ⟨si juga iri i no (iri a verdant_jardi i vet a verdant_jardi)⟩
        JUGADORA: A Verdant, ningú no saluda qui va amb roba de feina. Doncs no saludaré. ⟨si juga vet i no (iri a verdant_jardi i vet a verdant_jardi)⟩

RAMPA «Cantimplora»
    • walkTo/use/open — SEMPRE
        ⇒ → cantimplora_bodega

PORTA_RESIDENCIA «residència»
    • look — SEMPRE
        JUGADORA: La residència d'estiu del Magnat. Una porta de vidre i, davant, un robot amb llacet.
    • walkTo/use/open — si juga vet
        JUGADORA: En Fidel em mira la roba de feina. «El servei, pel darrere.» La casa no té darrere.
    • walkTo/use/open — si NO fidel_admet
        JUGADORA: El robot es posa al mig de la porta. Molt educadament. Molt al mig.
        ⇒ diàleg fidel
    • walkTo/use/open — SEMPRE
        ⇒ → verdant_residencia

PORTA_COBERT «cobert»
    • look — SEMPRE
        JUGADORA: El cobert del jardiner. L'única cosa de fusta de debò de tot Verdant.
    • walkTo/use/open — SEMPRE
        ⇒ → verdant_cobert

FLORS «flors»
    • look — SEMPRE
        JUGADORA: Flors de plàstic. No es moren. Per això el Magnat les estima.
    • pickUp — SEMPRE
        JUGADORA: Fan olor de cotxe nou.

ASPERSORS «aspersors»
    • look — SEMPRE
        JUGADORA: Aspersors. No reguen: perfumen. Gasten aigua per fer olor d'aigua.
    • use — SEMPRE
        JUGADORA: Per més que hi faci, només en surt boira de perfum.

REIXA «reixa»
    • look — SEMPRE
        JUGADORA: Una reixa a terra. Hi degota l'aire condicionat de la residència: aigua neta, que se'n va per l'aigüera.
    • use + galleda — SEMPRE
        [SO: degoteig] JUGADORA: Poso la galleda sota el degoteig...
        NARRADOR: Deu minuts. Una galleda plena de l'aigua que el Magnat llença.
        ⇒ perd galleda, rep galleda_plena, +galleda_omplerta
    • use/pickUp — SEMPRE
        JUGADORA: Aigua neta caient en una aigüera. Si tingués on posar-la...

LLANCADORA «llançadora»
    • look — SEMPRE
        JUGADORA: La plataforma de la llançadora dels jardiners. Cada dijous puja al palau.
    • walkTo/use/open — si NO nil_ajuda
        JUGADORA: Sense en Nil, la llançadora no s'enlaira. I en Nil no hi porta ningú que no conegui.
    • walkTo/use/open — SEMPRE
        JUGADORA: Dijous. Demà. En Nil ens hi esperarà.

PANELL_PREU «panell del preu»
    • look — SEMPRE
        JUGADORA: AIGUA VERNE. Un litre: 48 crèdits. I la fletxa, cap amunt. ⟨si preu_aigua = 48⟩
        JUGADORA: AIGUA VERNE. Un litre: 64 crèdits. I la fletxa, cap amunt. ⟨si preu_aigua = 64⟩
        JUGADORA: AIGUA VERNE. Un litre: 97 crèdits. I la fletxa, cap amunt. ⟨si preu_aigua = 97⟩
        JUGADORA: AIGUA VERNE. Un litre: 112 crèdits. I la fletxa, cap amunt. ⟨si preu_aigua = 112⟩
        JUGADORA: AIGUA VERNE. Un litre, i la fletxa. Avui, cap avall. ⟨si preu_aigua ≠ 48 i preu_aigua ≠ 64 i preu_aigua ≠ 97 i preu_aigua ≠ 112⟩
        NARRADOR: AIGUA VERNE · {preu_aigua} ₡ ⟨si preu_aigua ≠ 48 i preu_aigua ≠ 64 i preu_aigua ≠ 97 i preu_aigua ≠ 112⟩
    • use/push/pull/pickUp — SEMPRE
        JUGADORA: Aquí ningú no el mira. A Verdant, el preu no es pregunta.

NIL «—» — hi és si escena = 5

FIDEL «—»

```

## Sala Despatx d'estiu del Magnat · `verdant_residencia` (iri, vet)

```
EN ENTRAR
    • * (una vegada) — SEMPRE
        FIDEL: Esperi aquí, senyora inversora. El senyor Verne no hi és: és al seu palau. Com sempre.
        JUGADORA: Esperaré. Molt quieta. Sense tocar res.

PORTA «jardí»
    • walkTo/use/open — SEMPRE
        ⇒ → verdant_jardi

CALAIXERA «calaixera»
    • open/look/pull/use — si NO carta_banc
        JUGADORA: Una carta del Banc de Vesper al senyor Verne...
        JUGADORA: «Garanties del préstec: el preu de l'aigua. Si el preu baixa de 30 crèdits el litre, el Banc executarà les garanties: dipòsits, palau i drets.»
        JUGADORA: Ho té tot hipotecat sobre el preu. No cal buidar-li els dipòsits: cal que el preu baixi. Un dia.
        VET: (pel comunicador) Si el preu toca la ratlla dels trenta, s'ho queda tot el banc.
        ⇒ +carta_banc, rep carta_banc
    • look — SEMPRE
        JUGADORA: Bolígrafs d'or, paper amb la gota blava i la llista de la compra: «Aigua (reciclada). Pinso per a en Dividend (de luxe).»

PAPERERA «paperera daurada»
    • look/open/pickUp/use — si NO invitacio_agafada
        JUGADORA: Una invitació a la «Gran Subhasta de l'Aigua». Dijous al vespre, al palau orbital. El Magnat hi vendrà l'aigua dels pròxims deu anys, i amb els diners comprarà l'últim tros de mar d'Aqua.
        JUGADORA: Adreçada a la «Sra. Pruna, Verdant Holdings». Al dors, escrit a mà: «No hi aniré. Ja tinc set de debò.»
        JUGADORA: La Sra. Pruna, avui, soc jo.
        ⇒ +invitacio_agafada, rep invitacio
    • look — SEMPRE
        JUGADORA: Una paperera daurada. Buida, ara. Fins i tot les escombraries, aquí, brillen.

ARXIVADOR «arxivador»
    • open/look/pull/use — si NO contracte_agafat
        JUGADORA: Tres calaixos: DEUTORS, DRETS, PEIXOS.
        JUGADORA: DRETS: contractes com el del pou de l'avi. Milers.
        JUGADORA: PEIXOS: una fitxa per peix. Trenta-tres. A cada una: «Valor previst quan sigui l'últim».
        JUGADORA: DEUTORS... «Capitana Or. Préstec per a la reparació de la Cantimplora. Interès: variable, segons el preu de l'aigua.»
        JUGADORA: I una casella: «Ànima (opcional)». Marcada.
        JUGADORA: Per això té tanta por, la Capitana. Me l'emporto.
        ⇒ +contracte_agafat, rep contracte_capitana
    • look — SEMPRE
        JUGADORA: DEUTORS, DRETS, PEIXOS. Ja he vist prou.

QUADRE «retrat»
    • look — SEMPRE
        JUGADORA: Un retrat enorme del Magnat amb en Dividend, el seu gos. Tots dos somriuen. Només un de debò.

FINESTRAL «finestral»
    • look — SEMPRE
        JUGADORA: El jardí de plàstic. Hi veig la Vet, parlant amb el jardiner. O amb les flors. ⟨si vet a verdant_jardi⟩
        JUGADORA: El jardí de plàstic. Des d'aquí sembla de debò. Només des d'aquí. ⟨si no (vet a verdant_jardi)⟩

```

## Objecte comunicador · `comunicador`

```
• use/talkTo — SEMPRE
    ⇒ diàleg comunicador
```

## Objecte Mosca · `mosca`

```
• use + qualsevol objecte — SEMPRE
    ⇒ acció mosca.enviar
• use/talkTo — SEMPRE
    JUGADORA: Mosca: fes servir un objecte amb mi i el porto a l'altra.
```

## Objecte punta de flor · `punta_flor`

```
• use + tornavis — SEMPRE
    JUGADORA: Punta de flor al tornavís. Ara sí que és el meu tornavís.
    ⇒ perd punta_flor, perd tornavis, rep tornavis_flor
```

## Objecte tornavís · `tornavis`

```
(sense interaccions: només el text per defecte)
```

## Objecte tornavís de flor · `tornavis_flor`

```
(sense interaccions: només el text per defecte)
```

## Objecte escriptura · `escriptura`

```
(sense interaccions: només el text per defecte)
```

## Objecte contracte 7.788 · `contracte_7788`

```
(sense interaccions: només el text per defecte)
```

## Objecte sacs de llavors · `sacs_llavors`

```
(sense interaccions: només el text per defecte)
```

## Objecte sac de llavors · `sac_llavors`

```
(sense interaccions: només el text per defecte)
```

## Objecte albarà · `albara`

```
(sense interaccions: només el text per defecte)
```

## Objecte llauna d'oli · `oli`

```
(sense interaccions: només el text per defecte)
```

## Objecte clau anglesa · `clau_anglesa`

```
(sense interaccions: només el text per defecte)
```

## Objecte injector · `injector`

```
(sense interaccions: només el text per defecte)
```

## Objecte fusible de deu · `fusible`

```
• use + paper_plata — si juga vet
    JUGADORA: Fusible embolicat amb paper de plata. Ara aguanta trenta. I potser més.
    ⇒ perd fusible, perd paper_plata, rep fusible_apanyat
• use + paper_plata — SEMPRE
    JUGADORA: Això ho sap fer la Vet. Jo hi posaria cinta i pregàries.
```

## Objecte paper de plata · `paper_plata`

```
(sense interaccions: només el text per defecte)
```

## Objecte fusible apanyat · `fusible_apanyat`

```
(sense interaccions: només el text per defecte)
```

## Objecte carta de la Juana · `carta_juana`

```
(sense interaccions: només el text per defecte)
```

## Objecte nota per a la Lia · `nota_lia`

```
(sense interaccions: només el text per defecte)
```

## Objecte motlle · `motlle`

```
(sense interaccions: només el text per defecte)
```

## Objecte sac de sorra fina · `sorra`

```
(sense interaccions: només el text per defecte)
```

## Objecte les tres claus · `claus`

```
(sense interaccions: només el text per defecte)
```

## Objecte reg gota a gota · `reg`

```
• use + agulla — si juga vet
    JUGADORA: Forado els goters un per un amb l'agulla. Ara sí que regarà.
    ⇒ perd reg, rep reg_foradat
• use + agulla — SEMPRE
    JUGADORA: Els forats, els fa la Vet. Jo ho faria tot alhora i amb el dit.
```

## Objecte reg foradat · `reg_foradat`

```
(sense interaccions: només el text per defecte)
```

## Objecte agulla · `agulla`

```
• look — si juga iri
    JUGADORA: L'agulla de cosir de la Vet, amb fil. La guardava per si de cas. Com tot.
• use + vestit — si juga vet
    JUGADORA: Una mica d'aquí, una mica d'allà... Ja està: ara li anirà a mida.
    ⇒ perd vestit, rep vestit_arreglat
• use + vestit — SEMPRE
    JUGADORA: Si cuso jo, entraré al palau amb una màniga al cap.
```

## Objecte galleda · `galleda`

```
(sense interaccions: només el text per defecte)
```

## Objecte galleda plena · `galleda_plena`

```
(sense interaccions: només el text per defecte)
```

## Objecte carta del banc · `carta_banc`

```
(sense interaccions: només el text per defecte)
```

## Objecte invitació · `invitacio`

```
(sense interaccions: només el text per defecte)
```

## Objecte contracte de la Capitana · `contracte_capitana`

```
(sense interaccions: només el text per defecte)
```

## Objecte pernil · `pernil`

```
(sense interaccions: només el text per defecte)
```

## Objecte vestit de reina · `vestit`

```
• look — si juga iri
    JUGADORA: El vestit de reina de la Rosa, amb la corona d'engranatge. Em va gran.
• use + agulla — si juga vet
    JUGADORA: Una mica d'aquí, una mica d'allà... Ja està: ara li anirà a mida.
    ⇒ perd vestit, rep vestit_arreglat
```

## Objecte vestit arreglat · `vestit_arreglat`

```
• look — si juga iri
    JUGADORA: El vestit de reina, a la meva mida. Horrible. Perfecte.
```

## Objecte targeta de servei · `targeta`

```
(sense interaccions: només el text per defecte)
```

## Objecte targeta de la Mosca · `targeta_verne`

```
(sense interaccions: només el text per defecte)
```

## Diàleg `barril` amb Vet

```
COMENÇA A: inici

[inici]
    VET: Ni ho pensis. ⟨si iri a cantimplora_bodega i vet a cantimplora_bodega⟩
    IRI: La canalla del piquet té tres garrafes per a quaranta. ⟨si iri a cantimplora_bodega i vet a cantimplora_bodega⟩
    VET: És el nostre. Per si de cas. ⟨si iri a cantimplora_bodega i vet a cantimplora_bodega⟩
    JUGADORA: L'últim barril. «Per si de cas», diu la Vet. I la canalla del piquet té tres garrafes per a quaranta. ⟨si juga iri i no (vet a cantimplora_bodega)⟩
    JUGADORA: L'últim barril. És el nostre. Per si de cas. ⟨si juga vet i no (iri a cantimplora_bodega)⟩
    ▸ Això és el cas. ⟨si juga iri⟩ → iri
    ▸ (Donar el barril a la canalla.) ⟨si juga vet⟩ → vet
    ▸ Ara no. → (es queda) · FI

[iri]
    VET: ...Fes-ho. Abans que m'ho pensi. ⟨si vet a cantimplora_bodega⟩
    JUGADORA: La Vet m'ho perdonarà. Algun dia. ⟨si no (vet a cantimplora_bodega)⟩
    ↪ baixar

[vet]
    VET: Per si de cas. (sospira) Això és el cas, oi? ⟨si iri a cantimplora_bodega⟩
    IRI: Ho és. ⟨si iri a cantimplora_bodega⟩
    JUGADORA: Per si de cas. (sospira) La canalla del piquet té tres garrafes per a quaranta. Això és el cas. ⟨si no (iri a cantimplora_bodega)⟩
    ↪ baixar

[baixar]
    NARRADOR: Baixen el barril amb el carro de la bodega fins al piquet. La canalla fa cua amb gots. ⟨si iri a cantimplora_bodega i vet a cantimplora_bodega⟩
    NARRADOR: Baixa el barril amb el carro de la bodega fins al piquet. La canalla fa cua amb gots. ⟨si no (iri a cantimplora_bodega i vet a cantimplora_bodega)⟩
    ⇒ +barril_donat, +canalla_beu

```

## Diàleg `bru` amb Bru

```
COMENÇA A: torna (si bru_set) · carta (si té carta_juana (iri) i iri a ferrum_sindicat) · estrany

[estrany]
    BRU: Una pilot i una enginyera. Que us envia el Magnat? ⟨si iri a ferrum_sindicat i vet a ferrum_sindicat⟩
    BRU: Una pilot. Que t'envia el Magnat? ⟨si no (iri a ferrum_sindicat i vet a ferrum_sindicat) i juga iri⟩
    BRU: Una enginyera. Que t'envia el Magnat? ⟨si no (iri a ferrum_sindicat i vet a ferrum_sindicat) i juga vet⟩
    BRU: No parlo amb desconegudes. I menys amb desconegudes de nau.
    JUGADORA: (a part) Sense alguna cosa que digui qui som, en Bru no ens escoltarà. La Juana el coneix. ⟨si juana_claus i no (juga vet i té carta_juana (iri))⟩
    JUGADORA: (a part) La carta de la Juana la porta l'Iri. Sense ella, en Bru no m'escoltarà. ⟨si juga vet i té carta_juana (iri)⟩

[carta]
    BRU: Una pilot i una enginyera. Que us envia el Magnat? ⟨si vet a ferrum_sindicat⟩
    BRU: Una pilot. Que t'envia el Magnat? ⟨si no (vet a ferrum_sindicat)⟩
    IRI: Ens envia la Juana. Té.
    NARRADOR: En Bru llegeix la carta de la Juana. Dues vegades. Somriu, gairebé.
    BRU: La Juana diu que sou de fiar. La Juana també diu que les pedres tenen memòria.
    VET: La Juana diu que el Magnat viu del preu. ⟨si vet a ferrum_sindicat⟩
    JUGADORA: La Juana diu que el Magnat viu del preu. ⟨si no (vet a ferrum_sindicat)⟩
    BRU: La ven gota a gota. Si en vengués més, el preu baixaria. I si el preu baixa, ell deixa de ser el Magnat.
    BRU: És un home. I un home no vol ser un home. Vol ser el Magnat.
    BRU: Voleu les claus de les vàlvules. Ho diu aquí.
    BRU: Mentre la canalla del piquet tingui set, aquí no es parla de claus.
    ⇒ +bru_set, perd carta_juana (iri)
    ↪ menu

[torna]
    BRU: Què hi ha?
    ↪ menu

[menu]
    ▸ Com és la Lia? ⟨una vegada, si bru_lia⟩ → lia
    ▸ La Juana diu que et deu una cervesa. D'aigua. ⟨una vegada⟩ → juana
    ▸ La canalla ja beu. ⟨si canalla_beu i NO bru_lia⟩ → canalla
    ▸ Te la portarem a casa, la Lia. T'ho prometo. ⟨si bru_lia i NO promesa_lia i juga iri⟩ → promesa
    ▸ I si et portem la Lia a casa? ⟨si bru_lia i NO promesa_lia i juga vet⟩ → promesa_vet
    ▸ Com es fan les claus? ⟨si promesa_lia i NO claus_fetes⟩ → colada
    ▸ Recorda'm què cal fer. → recorda
    ▸ Fins ara, Bru. → (es queda) · FI

[canalla]
    BRU: Ho he vist.
    NARRADOR: En Bru mira per la finestra, una estona.
    BRU: Una esquirola amb hèlices. Això, a l'assemblea, no ho explico. ⟨si mosca_contractada⟩
    BRU: Bé. Ara parlem.
    BRU: Els motlles, els tinc. Fondre les claus, sé fer-ho. Les vaig fondre fa vint anys.
    BRU: Però la meva filla, la Lia, treballa al palau del Magnat. El Magnat contracta els fills dels que fem vaga. Diu que és per donar-nos feina.
    BRU: És per tenir-los a prop. Si faig res, la Lia...
    ⇒ +bru_lia
    ↪ menu

[promesa]
    BRU: Una pilot que promet. A Ferrum, les promeses de pilot les fem servir per encendre la foguera.
    IRI: No és un negoci. És una promesa. És nou per a mi també.
    NARRADOR: En Bru la mira una bona estona.
    BRU: ...Bé.
    NARRADOR: En Bru agafa un motlle de la prestatgeria i el deixa a la taula. Després, al dors de la carta de la Juana, escriu unes línies amb lletra gran.
    BRU: El motlle de les tres claus. I això, per a la Lia, perquè us faci cas. Ella coneix la meva lletra.
    BRU: La fosa és vostra. Una al forn i l'altra a la colada.
    ⇒ +promesa_lia, rep motlle, rep nota_lia (iri)
    ↪ menu

[promesa_vet]
    BRU: Això ho ha de prometre la pilot. Ella és la que tracta. Tu ets la que arregla.
    ↪ menu

[colada]
    BRU: Primer, el motlle al llit de colada, preparat amb sorra fina. Fina de debò: si no, les claus surten amb grava.
    BRU: Sorra fina, aquí no en tenim: tot és pedra picada. ⟨si NO sorra_agafada⟩
    BRU: Després, una al forn i l'altra a la colada. Al forn: manxa, metall, i fora l'escòria. A la colada: abocar el gresol i tapar amb sorra.
    BRU: Si l'escòria va al motlle, les claus surten amb bombolles. I el forn es refreda de pressa: no badeu.
    ⇒ +cal_sorra_bru
    ↪ menu

[lia]
    BRU: Té el meu nas i el geni de la seva mare. Neteja piscines buides.
    BRU: Diu que és la feina més fàcil del món, i la més trista.
    ↪ menu

[recorda]
    BRU: Que la canalla del piquet begui. Avui. Tenim tres garrafes per a quaranta. ⟨si NO canalla_beu⟩
    BRU: El condensador de la mina, Verne el va tancar amb un lector de targetes. Sense targeta de Verne, no fa res. ⟨si cal_targeta i NO canalla_beu⟩
    BRU: El motlle, preparat amb sorra fina al llit de colada. Metall al forn, manxa, i fora l'escòria abans d'abocar. ⟨si promesa_lia i NO claus_fetes⟩
    BRU: Sorra fina, aquí no en tenim: tot és pedra picada. ⟨si promesa_lia i NO sorra_agafada⟩
    BRU: Una al forn i l'altra a la colada. A la vegada. ⟨si promesa_lia i NO claus_fetes⟩
    BRU: Ara, al palau: busqueu en Nil, el jardiner de Verdant. Cada dijous hi puja. ⟨si claus_fetes⟩
    ↪ menu

[juana]
    BRU: Ha! Aquesta dona. Li va guanyar una aposta a la meva dona sobre el pes d'un peix. Fa vint anys.
    BRU: El peix era meu.
    ↪ menu

```

## Diàleg `capitana` amb Capitana Or

```
COMENÇA A: nit (si escena = 6 i trucada_feta i NO capitana_si) · torna (si ha vist capitana.primera) · primera

[primera]
    CAPITANA OR: Mira qui torna. La pilot que em va llogar el meu propi motor. ⟨si iri a cantimplora_pont⟩
    IRI: Te'l vaig tornar. ⟨si iri a cantimplora_pont⟩
    CAPITANA OR: Sense el carburador. ⟨si iri a cantimplora_pont⟩
    VET: Hola, Capitana. ⟨si vet a cantimplora_pont⟩
    CAPITANA OR: Hola, Vet. Tu sí que pots pujar. ⟨si iri a cantimplora_pont i vet a cantimplora_pont⟩
    CAPITANA OR: Hola, Vet. Tu sí que pots pujar. La teva germana encara em deu un carburador. ⟨si no (iri a cantimplora_pont)⟩
    ↪ menu

[torna]
    CAPITANA OR: Digues, que tinc un solitari a mitges.
    ↪ menu

[nit]
    CAPITANA OR: ...No tinc ganes de parlar, noia.
    ↪ menu

[menu]
    ▸ Què saps del Magnat? ⟨una vegada, si capitana_accepta i NO capitana_si⟩ → magnat
    ▸ Per què li tens tanta por, al Magnat? ⟨una vegada, si cap_condicions i NO capitana_si⟩ → por
    ▸ Saps que el pare és en una residència? ⟨una vegada⟩ → pare
    ▸ Capitana... tu has vist cap gat, a la nau? ⟨una vegada, si escena ≥ 3⟩ → gat
    ▸ On és l'aigua, Capitana? ⟨si NO cap_aigua⟩ → aigua
    ▸ Porta'ns a algú que sàpiga on és. ⟨si cap_aigua i NO cap_condicions⟩ → portar
    ▸ Albarà i injector. Anem a Aqua? ⟨si té albara i injector_posat i NO capitana_accepta⟩ → entrego
    ▸ Capitana, això és el teu contracte. El vaig trobar al despatx del Magnat. ⟨si (té contracte_capitana i NO capitana_si) i juga iri⟩ → contracte
    ▸ Capitana, això és el teu contracte. L'Iri el va trobar al despatx del Magnat. ⟨si (té contracte_capitana i NO capitana_si) i juga vet⟩ → contracte
    ▸ Què farem demà, Capitana? ⟨si capitana_si⟩ → pla
    ▸ Recorda'm què et cal per volar. ⟨si cap_condicions i NO capitana_accepta⟩ → recorda
    ▸ Res, Capitana. → adeu · FI

[aigua]
    CAPITANA OR: No ha desaparegut. L'han comprada. Tota.
    CAPITANA OR: El Magnat Verne té aigua per omplir deu planetes. No la ven. La guarda.
    VET: Per què? ⟨si vet a cantimplora_pont⟩
    JUGADORA: Per què? ⟨si no (vet a cantimplora_pont)⟩
    CAPITANA OR: Perquè si la ven, deixa de tenir-la. I si deixa de tenir-la, deixa de ser el Magnat.
    CAPITANA OR: És un home que confon tenir amb ser.
    ⇒ +cap_aigua
    ↪ menu

[portar]
    CAPITANA OR: Conec algú a Aqua que sap on va l'aigua: la Juana. Científica. Viu al fons del mar. Del que en queda.
    CAPITANA OR: Però no em ficaria amb el Magnat ni per tot l'or de Vesper. Ni per tota l'aigua, que ara val més.
    IRI: I si...? ⟨si iri a cantimplora_pont⟩
    JUGADORA: I si...? ⟨si no (iri a cantimplora_pont)⟩
    CAPITANA OR: Si volo, ha de ser una feina de veritat, amb albarà: si m'aturen, que hi hagi una càrrega i algú que la pagui.
    CAPITANA OR: I la nau no vola des que es va esquerdar l'injector. Això, pregunta-ho a la Vet. ⟨si juga iri⟩
    CAPITANA OR: I la nau no vola des que es va esquerdar l'injector. Això és cosa teva, enginyera. ⟨si juga vet⟩
    CAPITANA OR: La Juana té ràdio. La freqüència és aquí, al marc, amb retolador: «Juana, fons del mar».
    ⇒ +cap_condicions
    ↪ menu

[recorda]
    CAPITANA OR: Dues coses. Un albarà i un injector.
    CAPITANA OR: Albarà: ja el tens. ⟨si té albara⟩
    CAPITANA OR: Albarà: encara no. Una feina de veritat, amb algú que pagui a l'altra banda. La Juana és a la ràdio. ⟨si no (té albara)⟩
    CAPITANA OR: Injector: posat. Sento el motor des d'aquí. ⟨si injector_posat⟩
    CAPITANA OR: Injector: esquerdat. Pregunta a la Vet. ⟨si NO injector_posat i juga iri⟩
    CAPITANA OR: Injector: esquerdat. Això és cosa teva. ⟨si NO injector_posat i juga vet⟩
    ↪ menu

[entrego]
    CAPITANA OR: A veure aquest albarà...
    CAPITANA OR: «Tres sacs de llavors per a la Doctora Juana. Pagament: en espècie.»
    CAPITANA OR: És una feina de veritat. Ridícula, però de veritat.
    CAPITANA OR: Vola tu. I si ens atura el Magnat, jo no hi era. ⟨si juga iri⟩
    CAPITANA OR: Que voli la pilot. I si ens atura el Magnat, jo no hi era. ⟨si juga vet⟩
    IRI: El mapa és teu, Capitana. ⟨si iri a cantimplora_pont⟩
    JUGADORA: El mapa és teu, Capitana. ⟨si no (iri a cantimplora_pont)⟩
    CAPITANA OR: El mapa és de qui sap llegir-lo. Vinga.
    ⇒ +capitana_accepta, +aqua_oberta, perd albara
    ↪ menu

[por]
    CAPITANA OR: No en tinc por. Li tinc... respecte. Molt de respecte. Com a les tempestes.
    CAPITANA OR: I no en parlem més.
    ↪ menu

[magnat]
    CAPITANA OR: Que té un gos que es diu Dividend. Que viu en un palau en òrbita, amb vint-i-tres piscines buides.
    CAPITANA OR: I que mai, mai, perd un negoci.
    ↪ menu

[contracte]
    CAPITANA OR: ...El meu contracte. No l'havia vist mai sencer.
    NARRADOR: La Capitana llegeix el contracte. Dues vegades.
    CAPITANA OR: «Interès: variable, segons el preu de l'aigua.» Com més puja l'aigua, més li dec. Fa dotze anys que pago i cada any dec més.
    CAPITANA OR: I la casella. «Ànima (opcional).» La vaig marcar per fer broma. Estava de bon humor, aquell dia.
    IRI: Si el preu de l'aigua baixés... ⟨si iri a cantimplora_pont⟩
    JUGADORA: Si el preu de l'aigua baixés... ⟨si no (iri a cantimplora_pont)⟩
    CAPITANA OR: ...el meu deute baixaria.
    CAPITANA OR: Doncs que baixi.
    CAPITANA OR: Demà porto la Cantimplora al moll de càrrega del palau. Si algú ha d'entretenir la seguretat del Magnat, una vella bòrnia és perfecta.
    ⇒ +capitana_si, perd contracte_capitana
    ↪ menu

[pla]
    CAPITANA OR: Vosaltres, a dalt amb la llançadora d'en Nil i la invitació. Jo, al moll de càrrega, a fer de vella i bòrnia.
    CAPITANA OR: I si cal, perdo els frens. Sé perdre els frens molt bé.
    ↪ menu

[pare]
    CAPITANA OR: Ho sé. Li truco cada diumenge. Em guanya a les cartes per telèfon. No sé com ho fa.
    ↪ menu

[gat]
    CAPITANA OR: A la meva nau, res que mengi sense pagar.
    CAPITANA OR: ...Per tant, no. No n'he vist cap. I té el pèl tigrat, el gat que no he vist.
    ↪ menu

[adeu]
    CAPITANA OR: Bé.

```

## Diàleg `comunicador` amb Vet

```
COMENÇA A: inici

[inici]
    ▸ Què hem de fer, ara? → fem
    ▸ A quant és l'aigua? → preu
    ▸ Res. Només volia sentir-te. → (es queda) · FI

[fem]
    VET: Trobar l'escriptura de la granja (el pare ho sap; el videotelèfon és a la casa). ⟨si juga iri i (escena = 1 i NO caixa_oberta)⟩
    IRI: Trobar l'escriptura de la granja (el pare ho sap; el videotelèfon és a la casa). ⟨si juga vet i (escena = 1 i NO caixa_oberta)⟩
    VET: Què fa una bomba de Verne al nostre pou? ⟨si juga iri i (escena = 1 i NO bomba_llegida)⟩
    IRI: Què fa una bomba de Verne al nostre pou? ⟨si juga vet i (escena = 1 i NO bomba_llegida)⟩
    VET: Parlar amb la Capitana, al pont. ⟨si juga iri i (escena = 2 i NO cap_condicions)⟩
    IRI: Parlar amb la Capitana, al pont. ⟨si juga vet i (escena = 2 i NO cap_condicions)⟩
    VET: Un albarà: una feina de veritat per a Aqua (ràdio del pont: la Juana). ⟨si juga iri i (escena = 2 i cap_condicions i no (té albara) i NO capitana_accepta)⟩
    IRI: Un albarà: una feina de veritat per a Aqua (ràdio del pont: la Juana). ⟨si juga vet i (escena = 2 i cap_condicions i no (té albara) i NO capitana_accepta)⟩
    VET: Llavors per a la Juana: el banc del pare, al graner (demanar-li permís pel videotelèfon). ⟨si juga iri i (escena = 2 i juana_llavors i NO sacs_carregats)⟩
    IRI: Llavors per a la Juana: el banc del pare, al graner (demanar-li permís pel videotelèfon). ⟨si juga vet i (escena = 2 i juana_llavors i NO sacs_carregats)⟩
    VET: Llavors carregades: avisar la Juana per ràdio. ⟨si juga iri i (escena = 2 i sacs_carregats i NO albara_fet)⟩
    IRI: Llavors carregades: avisar la Juana per ràdio. ⟨si juga vet i (escena = 2 i sacs_carregats i NO albara_fet)⟩
    VET: L'injector de la nau està esquerdat: l'he de mirar jo (el motor, a la bodega). ⟨si juga iri i (escena = 2 i cap_condicions i NO injector_vist)⟩
    IRI: L'injector de la nau està esquerdat: que el miris tu (el motor, a la bodega). ⟨si juga vet i (escena = 2 i cap_condicions i NO injector_vist)⟩
    VET: Un injector nou: el tractor de l'avi en té un d'igual (oli i una clau anglesa). ⟨si juga iri i (escena = 2 i injector_vist i NO injector_posat)⟩
    IRI: Un injector nou: el tractor de l'avi en té un d'igual (oli i una clau anglesa). ⟨si juga vet i (escena = 2 i injector_vist i NO injector_posat)⟩
    VET: Albarà i injector: tornar a la Capitana. ⟨si juga iri i (escena = 2 i té albara i injector_posat i NO capitana_accepta)⟩
    IRI: Albarà i injector: tornar a la Capitana. ⟨si juga vet i (escena = 2 i té albara i injector_posat i NO capitana_accepta)⟩
    VET: Rumb a Aqua: el mapa del pont. ⟨si juga iri i (escena = 2 i capitana_accepta)⟩
    IRI: Rumb a Aqua: el mapa del pont. ⟨si juga vet i (escena = 2 i capitana_accepta)⟩
    VET: Baixar al fons del mar d'Aqua: la grua del port. ⟨si juga iri i (escena = 3 i NO baixada_feta)⟩
    IRI: Baixar al fons del mar d'Aqua: la grua del port. ⟨si juga vet i (escena = 3 i NO baixada_feta)⟩
    VET: Parlar amb la Juana, al fons del mar. ⟨si juga iri i (escena = 3 i baixada_feta i NO juana_fet)⟩
    IRI: Parlar amb la Juana, al fons del mar. ⟨si juga vet i (escena = 3 i baixada_feta i NO juana_fet)⟩
    VET: Ferrum: trobar en Bru (el sindicat) i donar-li la carta de la Juana. ⟨si juga iri i (escena = 4 i NO bru_set)⟩
    IRI: Ferrum: trobar en Bru (el sindicat) i donar-li la carta de la Juana. ⟨si juga vet i (escena = 4 i NO bru_set)⟩
    VET: Aigua per a la canalla del piquet de Ferrum. ⟨si juga iri i (escena = 4 i bru_set i NO canalla_beu)⟩
    IRI: Aigua per a la canalla del piquet de Ferrum. ⟨si juga vet i (escena = 4 i bru_set i NO canalla_beu)⟩
    VET: El condensador del carrer s'engega amb una targeta de treballador actiu de Verne. ⟨si juga iri i (escena = 4 i cal_targeta i NO mosca_contractada i NO canalla_beu)⟩
    IRI: El condensador del carrer s'engega amb una targeta de treballador actiu de Verne. ⟨si juga vet i (escena = 4 i cal_targeta i NO mosca_contractada i NO canalla_beu)⟩
    VET: La font de Verne contracta: vint-i-quatre hores, cap vaga i cap aigua. ⟨si juga iri i (escena = 4 i contractacio_vista i NO mosca_contractada i NO canalla_beu)⟩
    IRI: La font de Verne contracta: vint-i-quatre hores, cap vaga i cap aigua. ⟨si juga vet i (escena = 4 i contractacio_vista i NO mosca_contractada i NO canalla_beu)⟩
    VET: La Mosca té feina i targeta. El condensador és al carrer. ⟨si juga iri i (escena = 4 i mosca_contractada i NO canalla_beu)⟩
    IRI: La Mosca té feina i targeta. El condensador és al carrer. ⟨si juga vet i (escena = 4 i mosca_contractada i NO canalla_beu)⟩
    VET: Tornar a parlar amb en Bru. ⟨si juga iri i (escena = 4 i canalla_beu i NO promesa_lia)⟩
    IRI: Tornar a parlar amb en Bru. ⟨si juga vet i (escena = 4 i canalla_beu i NO promesa_lia)⟩
    VET: Preparar el motlle de les claus al llit de colada de la fosa. ⟨si juga iri i (escena = 4 i promesa_lia i NO motlle_preparat i NO cal_sorra)⟩
    IRI: Preparar el motlle de les claus al llit de colada de la fosa. ⟨si juga vet i (escena = 4 i promesa_lia i NO motlle_preparat i NO cal_sorra)⟩
    VET: Sorra fina per al motlle: a Ferrum només n'hi ha de pedra picada. ⟨si juga iri i (escena = 4 i cal_sorra i NO motlle_preparat)⟩
    IRI: Sorra fina per al motlle: a Ferrum només n'hi ha de pedra picada. ⟨si juga vet i (escena = 4 i cal_sorra i NO motlle_preparat)⟩
    VET: La platja d'Aqua ara és el lot 9 de Verne: de la línia de l'aigua de dimarts cap amunt. ⟨si juga iri i (escena = 4 i cal_sorra i lot9_vist i NO sorra_agafada)⟩
    IRI: La platja d'Aqua ara és el lot 9 de Verne: de la línia de l'aigua de dimarts cap amunt. ⟨si juga vet i (escena = 4 i cal_sorra i lot9_vist i NO sorra_agafada)⟩
    VET: La colada: una al forn i l'altra a la colada. ⟨si juga iri i (escena = 4 i motlle_preparat i NO claus_fetes)⟩
    IRI: La colada: una al forn i l'altra a la colada. ⟨si juga vet i (escena = 4 i motlle_preparat i NO claus_fetes)⟩
    VET: Verdant: el jardiner Nil puja al palau cada dijous. ⟨si juga iri i (escena = 5 i NO nil_palau)⟩
    IRI: Verdant: el jardiner Nil puja al palau cada dijous. ⟨si juga vet i (escena = 5 i NO nil_palau)⟩
    VET: Mirar què guarda el Magnat a la residència d'estiu de Verdant. ⟨si juga iri i (escena = 5 i NO fidel_admet i no (ha vist fidel.hola))⟩
    IRI: Mirar què guarda el Magnat a la residència d'estiu de Verdant. ⟨si juga vet i (escena = 5 i NO fidel_admet i no (ha vist fidel.hola))⟩
    VET: Entrar al despatx del Magnat: el robot de la porta només deixa passar gent «solvent». ⟨si juga iri i (escena = 5 i NO fidel_admet i ha vist fidel.hola)⟩
    IRI: Entrar al despatx del Magnat: el robot de la porta només deixa passar gent «solvent». ⟨si juga vet i (escena = 5 i NO fidel_admet i ha vist fidel.hola)⟩
    VET: Un aval d'un milió per a en Fidel. La granja, diu, val un crèdit. ⟨si juga iri i (escena = 5 i cal_aval i NO fidel_admet)⟩
    IRI: Un aval d'un milió per a en Fidel. La granja, diu, val un crèdit. ⟨si juga vet i (escena = 5 i cal_aval i NO fidel_admet)⟩
    VET: Remenar el despatx del Magnat. ⟨si juga iri i (escena = 5 i fidel_admet i no (carta_banc i invitacio_agafada i contracte_agafat))⟩
    IRI: Remenar el despatx del Magnat. ⟨si juga vet i (escena = 5 i fidel_admet i no (carta_banc i invitacio_agafada i contracte_agafat))⟩
    VET: Que en Nil ens porti al palau com a ajudants. ⟨si juga iri i (escena = 5 i nil_palau i NO nil_ajuda)⟩
    IRI: Que en Nil ens porti al palau com a ajudants. ⟨si juga vet i (escena = 5 i nil_palau i NO nil_ajuda)⟩
    VET: Un reg gota a gota per a la tomaquera d'en Nil: el del pare, al graner de Terra-2. ⟨si juga iri i (escena = 5 i cal_reg i NO reg_agafat)⟩
    IRI: Un reg gota a gota per a la tomaquera d'en Nil: el del pare, al graner de Terra-2. ⟨si juga vet i (escena = 5 i cal_reg i NO reg_agafat)⟩
    VET: El graner de Terra-2 té un cadenat de Verne: només hi pot entrar la propietat. ⟨si juga iri i (escena = 5 i precinte_vist i NO graner_obert)⟩
    IRI: El graner de Terra-2 té un cadenat de Verne: només hi pot entrar la propietat. ⟨si juga vet i (escena = 5 i precinte_vist i NO graner_obert)⟩
    VET: Qui informa el Magnat? Algú de la nau. ⟨si juga iri i (escena = 6 i cal_espia i NO tomas_girat)⟩
    IRI: Qui informa el Magnat? Algú de la nau. ⟨si juga vet i (escena = 6 i cal_espia i NO tomas_girat)⟩
    VET: Ensenyar el contracte a la Capitana. ⟨si juga iri i (escena = 6 i NO capitana_si)⟩
    IRI: Ensenyar el contracte a la Capitana. ⟨si juga vet i (escena = 6 i NO capitana_si)⟩
    VET: Un vestit de gala per a tu (al sindicat de Ferrum n'hi havia un). ⟨si juga iri i (escena = 6 i cal_gala i no (té vestit_arreglat (iri)) i NO vestit_agafat i NO rosa_vol_tomas)⟩
    IRI: Un vestit de gala per a mi (al sindicat de Ferrum n'hi havia un). ⟨si juga vet i (escena = 6 i cal_gala i no (té vestit_arreglat (iri)) i NO vestit_agafat i NO rosa_vol_tomas)⟩
    VET: La Rosa ens deixa el vestit si en Tomàs baixa a buscar-lo. ⟨si juga iri i (escena = 6 i rosa_vol_tomas i NO tomas_baixa)⟩
    IRI: La Rosa ens deixa el vestit si en Tomàs baixa a buscar-lo. ⟨si juga vet i (escena = 6 i rosa_vol_tomas i NO tomas_baixa)⟩
    VET: El vestit de la Rosa et va gran: ho arreglo amb l'agulla del meu calaix. ⟨si juga iri i (escena = 6 i cal_gala i vestit_agafat i no (té vestit_arreglat (iri) o té vestit_arreglat (vet)))⟩
    IRI: El vestit de la Rosa em va gran: l'agulla del teu calaix. ⟨si juga vet i (escena = 6 i cal_gala i vestit_agafat i no (té vestit_arreglat (iri) o té vestit_arreglat (vet)))⟩
    VET: El vestit arreglat és per a tu: te'l dono o te l'envio amb la Mosca. ⟨si juga iri i (escena = 6 i té vestit_arreglat (vet))⟩
    IRI: El vestit arreglat és per a mi: dona-me'l o envia-me'l amb la Mosca. ⟨si juga vet i (escena = 6 i té vestit_arreglat (vet))⟩
    VET: Palau: he de trobar la Lia (passadissos de servei). ⟨si juga iri i (escena = 7 i NO lia_avisada)⟩
    IRI: Palau: has de trobar la Lia (passadissos de servei). ⟨si juga vet i (escena = 7 i NO lia_avisada)⟩
    VET: Fer-me arribar les claus (la safata de les copes, al saló). ⟨si juga iri i (escena = 7 i no (té claus (vet)) i NO subhasta_comencada)⟩
    IRI: Fer-te arribar les claus (la safata de les copes, al saló). ⟨si juga vet i (escena = 7 i no (té claus (vet)) i NO subhasta_comencada)⟩
    VET: Jo a la sala de control, tu al saló de la subhasta. ⟨si juga iri i (escena = 7 i NO subhasta_comencada)⟩
    IRI: Tu a la sala de control, jo al saló de la subhasta. ⟨si juga vet i (escena = 7 i NO subhasta_comencada)⟩
    VET: Obrir les tres vàlvules (la clau al pany, i girar) abans que s'acabin els lots, sense espantar el Magnat. Tu pots parar el martell: cada objecció, al seu lot. ⟨si juga iri i (sync_subhasta i valvules < 3)⟩
    IRI: Obrir les tres vàlvules (la clau al pany, i girar) abans que s'acabin els lots, sense espantar el Magnat. Jo puc parar el martell: cada objecció, al seu lot. ⟨si juga vet i (sync_subhasta i valvules < 3)⟩
    VET: 31: el Magnat s'aguanta amb la seva reserva. La palanca vermella. ⟨si juga iri i (sync_subhasta i valvules ≥ 3)⟩
    IRI: 31: el Magnat s'aguanta amb la seva reserva. La palanca vermella. ⟨si juga vet i (sync_subhasta i valvules ≥ 3)⟩
    ↪ inici

[preu]
    VET: 48 crèdits el litre. I pujant. ⟨si juga iri i preu_aigua = 48⟩
    VET: 64 crèdits el litre. I pujant. ⟨si juga iri i preu_aigua = 64⟩
    VET: 97 crèdits el litre. I pujant. ⟨si juga iri i preu_aigua = 97⟩
    VET: 112 crèdits el litre. I pujant. ⟨si juga iri i preu_aigua = 112⟩
    VET: Baixant. Que no pari. ⟨si juga iri i (preu_aigua ≠ 48 i preu_aigua ≠ 64 i preu_aigua ≠ 97 i preu_aigua ≠ 112)⟩
    NARRADOR: AIGUA VERNE · {preu_aigua} ₡ ⟨si juga iri i (preu_aigua ≠ 48 i preu_aigua ≠ 64 i preu_aigua ≠ 97 i preu_aigua ≠ 112)⟩
    IRI: 48 crèdits el litre. I pujant. ⟨si juga vet i preu_aigua = 48⟩
    IRI: 64 crèdits el litre. I pujant. ⟨si juga vet i preu_aigua = 64⟩
    IRI: 97 crèdits el litre. I pujant. ⟨si juga vet i preu_aigua = 97⟩
    IRI: 112 crèdits el litre. I pujant. ⟨si juga vet i preu_aigua = 112⟩
    IRI: Baixant. Que no pari. ⟨si juga vet i (preu_aigua ≠ 48 i preu_aigua ≠ 64 i preu_aigua ≠ 97 i preu_aigua ≠ 112)⟩
    NARRADOR: AIGUA VERNE · {preu_aigua} ₡ ⟨si juga vet i (preu_aigua ≠ 48 i preu_aigua ≠ 64 i preu_aigua ≠ 97 i preu_aigua ≠ 112)⟩
    ↪ inici

```

## Diàleg `contractacio` amb Iri

```
COMENÇA A: contractada (si mosca_contractada) · inici

[inici]
    NARRADOR: «VERNE S.A. CONTRACTA. Mines de Ferrum. Incorporació immediata. Targeta de treballador actiu el mateix dia.»
    NARRADOR: «Pregunta 1 de 3. Ha fet vaga alguna vegada?»
    ▸ No. → p2
    ▸ Sí. → vaga · FI
    ▸ (Deixar-ho estar.) → (es queda) · FI

[vaga]
    NARRADOR: «Sol·licitud denegada. Gràcies per la seva sinceritat.»

[p2]
    NARRADOR: «Pregunta 2 de 3. Disponibilitat?»
    ▸ Vint-i-quatre hores. → p3
    ▸ De nou a cinc. → horari · FI

[horari]
    NARRADOR: «Sol·licitud denegada. Verne S.A. busca perfils compromesos.»

[p3]
    NARRADOR: «Pregunta 3 de 3. Necessita aigua per viure?»
    ▸ Sí. → aigua · FI
    ▸ ...No. → menteix · FI

[aigua]
    NARRADOR: «Sol·licitud denegada. Verne S.A. busca perfils sostenibles.»
    IRI: Volen algú que treballi tot el dia, que no faci vaga i que no begui. ⟨si juga iri⟩
    VET: Requisits: vint-i-quatre hores, zero vagues, zero aigua. Cap persona no passa aquest control de qualitat. ⟨si juga vet⟩
    ⇒ +contractacio_vista

[menteix]
    NARRADOR: «Llavors no li cal la targeta de treballador actiu, que dona dret a aigua. Sol·licitud arxivada.»
    IRI: Volen algú que treballi tot el dia, que no faci vaga i que no begui. ⟨si juga iri⟩
    VET: Requisits: vint-i-quatre hores, zero vagues, zero aigua. Cap persona no passa aquest control de qualitat. ⟨si juga vet⟩
    ⇒ +contractacio_vista

[contractada]
    NARRADOR: «VERNE S.A. CONTRACTA. Felicitats a la nostra nova operària: Mosca.»

```

## Diàleg `fidel` amb Fidel

```
COMENÇA A: admesa (si fidel_admet) · hola

[hola]
    [SO: robot] FIDEL: Benvinguda a la residència d'estiu del senyor Verne. Només persones solvents. Actiu mínim: un milió de crèdits.
    ↪ menu

[admesa]
    FIDEL: Senyora Inversora. Passi. ⟨si juga iri⟩
    FIDEL: El servei entra pel darrere. La senyora Inversora ja és a dins. ⟨si juga vet⟩

[menu]
    ▸ Soc inversora. Vinc a comprar Aqua. ⟨si juga iri⟩ → aval
    ▸ Soc... del servei. ⟨si juga vet⟩ → servei
    ▸ Qui ets? ⟨una vegada⟩ → qui
    ▸ Res. Passava per aquí. → (es queda) · FI

[qui]
    FIDEL: Soc en Fidel. Majordom. Programat per distingir la gent solvent de la gent.
    ↪ menu

[servei]
    FIDEL: El servei entra pel darrere.
    NARRADOR: La residència no té darrere.
    ↪ menu

[aval]
    FIDEL: Excel·lent. Un aval, si us plau. Un actiu valuós.
    ▸ Una granja a Terra-2. Aquí en tinc l'escriptura. ⟨si té escriptura⟩ → escriptura
    ▸ Un contracte amb Verne S.A. ⟨si té contracte_7788⟩ → contracte
    ▸ Un sac de llavors resistents a la secada. ⟨si té sac_llavors⟩ → sac
    ▸ I un tractor? Un Brau 40, vermell. Pagat amb un pou. ⟨si té contracte_7788 i fidel_norma⟩ → tractor
    ▸ No porto res a sobre. → res

[sac]
    [SO: robot] FIDEL: Llavors resistents a la secada. Actiu de futur. Valor estimat...
    NARRADOR: Bip.
    FIDEL: ...Inestimable. Passi, senyora. Deixo el seu aval a la caixa forta.
    IRI: (baix) Gràcies, papa.
    ⇒ +fidel_admet, perd sac_llavors

[escriptura]
    FIDEL: Terra sense aigua. Última operació registrada: una oferta de compra de Verne S.A., d'un crèdit. Valor: un crèdit. Ens consta.
    JUGADORA: Què val, a Vesper, més que la terra? ...El que hi creix sense aigua. Llavors que aguanten la secada. El quart sac del pare, al graner! ⟨si no (té sac_llavors) i NO sac4_agafat⟩
    JUGADORA: Què val, a Vesper, més que la terra? ...El que hi creix sense aigua. El quart sac del pare! El porta la Vet. ⟨si no (té sac_llavors) i sac4_agafat⟩
    ⇒ +cal_aval, +fidel_norma
    ↪ menu

[contracte]
    FIDEL: Un contracte en què l'aigua és nostra i el tractor, seu. Valor: el paper.
    JUGADORA: Què val, a Vesper, més que la terra? ...El que hi creix sense aigua. Llavors que aguanten la secada. El quart sac del pare, al graner! ⟨si no (té sac_llavors) i NO sac4_agafat⟩
    JUGADORA: Què val, a Vesper, més que la terra? ...El que hi creix sense aigua. El quart sac del pare! El porta la Vet. ⟨si no (té sac_llavors) i sac4_agafat⟩
    ⇒ +cal_aval
    ↪ menu

[res]
    FIDEL: Torni quan sigui solvent. Bon dia.
    JUGADORA: Què val, a Vesper, més que la terra? ...El que hi creix sense aigua. Llavors que aguanten la secada. El quart sac del pare, al graner! ⟨si no (té sac_llavors) i NO sac4_agafat⟩
    JUGADORA: Què val, a Vesper, més que la terra? ...El que hi creix sense aigua. El quart sac del pare! El porta la Vet. ⟨si no (té sac_llavors) i sac4_agafat⟩
    ⇒ +cal_aval
    ↪ menu

[tractor]
    [SO: robot] FIDEL: Brau 40. Consulto l'última operació registrada.
    NARRADOR: Bip. Bip. Bip.
    FIDEL: Contracte 7.788. Preu pagat per Verne S.A.: l'aigua del subsòl d'una finca, a perpetuïtat. Al preu d'avui, un milió dos-cents mil crèdits.
    FIDEL: Estat de l'actiu?
    IRI: No arrenca. No ha arrencat mai.
    FIDEL: Els actius no arrenquen. Valen. Passi, senyora. Anoto l'aval: un tractor de luxe.
    IRI: (baix) L'avi, inversor.
    ⇒ +fidel_admet, +fidel_tractor

```

## Diàleg `holm` amb Holm

```
COMENÇA A: durant (si sync_subhasta) · torna (si holm_parlat) · hola

[hola]
    HOLM: Senyora... Pruna? Verdant Holdings? No la tenia a la llista d'assistents.
    ↪ q

[q]
    ▸ Inverteixo en llavors resistents a la secada. Són el futur. → llavors
    ▸ La llista es va fer abans que decidís venir. Com aquest vestit. → vestit
    ▸ En Verne m'ha convidat en persona. → magnat

[llavors]
    HOLM: Llavors. Interessant. Molt interessant. Ho apunto.
    ↪ parlat

[vestit]
    HOLM: ...Molt atrevit. Verdant Holdings, sempre tan avantguardistes.
    ↪ parlat

[magnat]
    HOLM: El senyor Verne convida tothom que té diners. És la seva manera de comptar-los.
    ↪ parlat

[parlat]
    HOLM: Al Banc ens agrada el senyor Verne. Mentre el preu sigui alt.
    IRI: I si baixa?
    HOLM: Si baixa de trenta, el Banc es queda el palau, els dipòsits i el gos. Però no baixarà. Mai baixa.
    NARRADOR: En Holm se'n va a buscar una copa. A la senyora Pruna, ja no la mira.
    ⇒ +holm_parlat

[torna]
    HOLM: Senyora Pruna. Gaudeixi del cava. No el paguem nosaltres.
    HOLM: I no pateixi pel preu: el Banc només s'hi fica si baixa de trenta. I no baixarà.

[durant]
    HOLM: Silenci, senyora, que estic comptant lots.
    ↪ sub

[sub]
    ↪ subhasta_menu

[subhasta_menu]

```

## Diàleg `juana` amb Juana

```
COMENÇA A: torna (si ha vist juana.hola) · hola

[hola]
    JUANA: Sou les de la Cantimplora. Les de les llavors.
    JUANA: Diu la Capitana que voleu salvar el món.
    IRI: No. Volem salvar el nostre pou. ⟨si iri a casa_juana⟩
    JUGADORA: No. Volem salvar el nostre pou. ⟨si no (iri a casa_juana)⟩
    JUANA: És el mateix. A una altra escala.
    JUANA: Seieu. A terra, que les cadires les vaig vendre per aigua. ⟨si iri a casa_juana i vet a casa_juana⟩
    JUANA: Seu. A terra, que les cadires les vaig vendre per aigua. ⟨si no (iri a casa_juana i vet a casa_juana)⟩
    ⇒ +juana_coneguda
    ↪ menu

[torna]
    JUANA: Sí?
    ↪ menu

[menu]
    ▸ Les llavors són a la nau. ⟨una vegada⟩ → llavors
    ▸ I els peixos d'Aqua? ⟨una vegada, si juana_mar⟩ → peixos
    ▸ On és el mar d'Aqua? ⟨si NO juana_mar⟩ → mar
    ▸ I on va a parar, l'aigua? ⟨si juana_mar i NO juana_diposits⟩ → on
    ▸ Es pot fer tornar? ⟨si juana_diposits i NO juana_claus⟩ → tornar
    ▸ Com convencem en Bru perquè ens doni les claus? ⟨si juana_claus i NO juana_fet⟩ → bru
    ▸ Tu també ens vols preguntar alguna cosa? ⟨una vegada, si juana_claus⟩ → q1
    ▸ Juana, a la platja hi ha estaques de Verne. ⟨si lot9_vist i NO sorra_agafada⟩ → lot9
    ▸ Recorda'm el que ens has explicat. ⟨si juana_claus⟩ → recorda
    ▸ Adeu, Juana. → adeu · FI

[mar]
    JUANA: Puja.
    JUANA: Des que hi ha la Canonada d'Aqua, el mar baixa dos metres cada mes. Ho mesuro amb les boies.
    JUANA: No s'evapora: se l'enduen. El bomben cap amunt, cap a l'òrbita, i allà es glaça.
    ⇒ +juana_mar
    ↪ menu

[on]
    JUANA: A tres dipòsits orbitals. Un per planeta: el de Terra-2, el de Ferrum i el d'Aqua, que és el gros: s'hi va endur un mar. Plens de gel. Els tinc localitzats.
    JUANA: El Magnat en ven una mica cada dia, gota a gota. La justa perquè la gent visqui i pagui. La resta, la guarda.
    VET: I si en vengués més? ⟨si vet a casa_juana⟩
    JUGADORA: I si en vengués més? ⟨si no (vet a casa_juana)⟩
    JUANA: El preu baixaria. I el Magnat viu del preu.
    ⇒ +juana_diposits
    ↪ menu

[tornar]
    JUANA: Els dipòsits tenen vàlvules d'emergència, per si s'esquerden. Si s'obren, el gel cau a l'atmosfera, es fon... i plou.
    JUANA: El deixen anar a trossets, perquè es fongui abans de tocar a terra. Tres setmanes de pluja a cada planeta. Ho he calculat.
    VET: I on s'obren, aquestes vàlvules? ⟨si vet a casa_juana⟩
    JUGADORA: I on s'obren, aquestes vàlvules? ⟨si no (vet a casa_juana)⟩
    JUANA: A la sala de control del palau del Magnat, sota la piscina central: ho vol tot sota els peus. Amb tres claus.
    IRI: I on són, les claus? ⟨si iri a casa_juana⟩
    JUGADORA: I on són, les claus? ⟨si no (iri a casa_juana)⟩
    JUANA: Les va fondre en Bru, a Ferrum, quan van fer els dipòsits. Ell m'ho va explicar. Encara en té els motlles.
    JUANA: Ara en Bru és el cap de la vaga de Ferrum. I no es fia de ningú.
    ⇒ +juana_claus
    ↪ menu

[bru]
    JUANA: No es fia de ningú. De mi, una mica. Us escric una carta. Té, Iri: tu que parles. ⟨si iri a casa_juana⟩
    JUANA: No es fia de ningú. De mi, una mica. Us escric una carta. Per a l'Iri: ella és la que parla. ⟨si no (iri a casa_juana)⟩
    NARRADOR: La Juana escriu una carta, la plega i la tanca amb un segell de cera amb un peix.
    JUANA: Aneu a Ferrum. I si veieu en Bru, digueu-li que encara li dec una cervesa. D'aigua.
    ⇒ +juana_fet, rep carta_juana (iri)

[peixos]
    JUANA: Els últims peixos d'Aqua se'ls va endur el Magnat. Trenta-tres. En un aquari, al seu palau.
    JUANA: Diu que valdran més quan en quedi un.
    VET: Això és... ⟨si vet a casa_juana⟩
    JUGADORA: Això és... ⟨si no (vet a casa_juana)⟩
    JUANA: Sí. Ho és.
    ↪ menu

[llavors]
    JUANA: Ja ho sé. La Capitana me les baixarà amb la cistella quan pugeu. Gràcies.
    JUANA: Les sembraré aquí, al fons del mar. Algun dia serà el fons d'un camp. O d'un mar. Ja veurem què arriba primer.
    ↪ menu

[q1]
    JUANA: Tres preguntes. Soc científica: pregunto. Primera: què faríeu si tinguéssiu tota l'aigua de Vesper?
    ▸ La vendria. A bon preu. → r1a
    ▸ La regalaria. Però només a qui m'agrada. → r1b
    ▸ Me la beuria tota. → r1c

[r1a]
    JUANA: Ha! Honesta.
    ↪ q2

[r1b]
    JUANA: Ha, ha! Doncs aneu amb compte de caure-us bé.
    ↪ q2

[r1c]
    JUANA: ...No fa gràcia. Però és el que fa el Magnat.
    ↪ q2

[q2]
    JUANA: Segona: i si el Magnat us oferís un milió perquè no féssiu res?
    ▸ L'agafaria. I després faria alguna cosa. → r2a
    ▸ L'agafaria i no faria res. Però em sentiria fatal. → r2b

[r2a]
    JUANA: Això és trampa. Bona trampa.
    ↪ q3

[r2b]
    JUANA: Almenys sabeu que us sentiríeu fatal. Ja és alguna cosa.
    ↪ q3

[q3]
    JUANA: Última: per què ho feu?
    ▸ No vull salvar el món. Vull el meu pou. → r3a
    ▸ Vull salvar el món. Però el meu pou, primer. → r3b

[r3a]
    JUANA: Ets honesta. M'agrada.
    ↪ menu

[r3b]
    JUANA: Bon ordre. Primer el pou. El món ja vindrà.
    ↪ menu

[recorda]
    JUANA: El mar d'Aqua el bomben cap a l'òrbita, i es glaça en tres dipòsits: el de Terra-2, el de Ferrum i el d'Aqua, que és el gros.
    JUANA: Tenen vàlvules d'emergència. Si s'obren, el gel cau a trossets, es fon i plou.
    JUANA: S'obren des de la sala de control del palau del Magnat, sota la piscina central. Amb tres claus que va fondre en Bru, a Ferrum.
    JUANA: La carta per a en Bru ja la porteu. ⟨si juana_fet⟩
    ↪ menu

[adeu]
    JUANA: Si torneu, porteu-me sorra de Terra-2. Per comparar.

[lot9]
    JUANA: El lot 9. Els topògrafs de Verne van baixar dimarts a la nit: ho amiden fins a l'aigua, i d'allà amunt, ho venen.
    JUANA: Però el mar no s'està quiet perquè l'amidin. Pregunteu-ho a les meves boies.
    ↪ menu

```

## Diàleg `kessel` amb Kessel

```
COMENÇA A: hola

[hola]
    KESSEL: Compro drets d'aire. L'aire és el futur. L'aigua ja és el passat.
    KESSEL: Quan tothom respiri a la meva manera, ja en parlarem.

```

## Diàleg `lia` amb Lia

```
COMENÇA A: aliada (si lia_avisada) · torna (si ha vist lia.hola) · hola

[hola]
    LIA: Ets nova? Aquí no es parla. Es frega.
    ↪ menu

[torna]
    LIA: Encara aquí?
    ↪ menu

[menu]
    ▸ Què hi fas, aquí? ⟨una vegada⟩ → feina
    ▸ El teu pare diu que tornis a casa. ⟨si NO lia_prova⟩ → pare
    ▸ Té. És d'ell. ⟨si té nota_lia⟩ → nota
    ▸ Res. Continua fregant. → (es queda) · FI

[pare]
    LIA: Aquí tothom diu coses. El Magnat diu que el meu pare és un perill per a ell mateix.
    LIA: Si de debò t'envia el meu pare, porta'm alguna cosa de la seva mà.
    VET: (a part) La nota d'en Bru. La porta l'Iri. Que me la passi per la safata del saló. ⟨si no (té nota_lia)⟩
    ⇒ +lia_prova
    ↪ menu

[feina]
    LIA: Netejo piscines buides. És la feina més fàcil del món, i la més trista.
    ↪ menu

[nota]
    LIA: ...És la seva lletra. Escriu «cas» amb dues esses quan està nerviós.
    LIA: Què necessiteu?
    VET: Baixar a la sala de control. Sota la piscina central.
    LIA: Amb la meva targeta. I quan el Magnat truqui a la sala per l'interfon, contestaré jo des d'aquí.
    LIA: Allà baix hi ha tres panys i una palanca vermella que no es pot tocar mai. La seva «reserva».
    ⇒ +lia_avisada, +lia_prova, +lia_reserva, perd nota_lia, rep targeta
    ↪ aliada

[aliada]
    ▸ Recorda'm què hi ha a la sala de control. → control
    ▸ Fins ara, Lia. → (es queda) · FI

[control]
    LIA: Tres panys, T2, AQUA, FERRUM, i la palanca de la reserva del Magnat. Baixa amb l'ascensor.
    ↪ aliada

```

## Diàleg `nil` amb Nil

```
COMENÇA A: torna (si ha vist nil.hola) · hola

[hola]
    NIL: ...i tu, rosa, no t'arronsis, que avui ve visita.
    JUGADORA: Hola?
    NIL: Ah. Una persona. Les flors no em contesten, però escolten.
    ↪ menu

[torna]
    NIL: Ah, tu. Digues.
    ↪ menu

[menu]
    ▸ Són de plàstic, oi? ⟨una vegada⟩ → flors
    ▸ Vostè puja al palau del Magnat? ⟨si NO nil_palau⟩ → palau
    ▸ Com és, el Magnat? ⟨una vegada, si nil_palau⟩ → magnat
    ▸ He vist la tomaquera del cobert. ⟨si tomaquera_vista i NO tomaquera_regada⟩ → tomaquera
    ▸ La tomaquera ja beu. Gota a gota. ⟨si tomaquera_regada i NO nil_ajuda⟩ → regada
    ▸ Quan pugem? ⟨si nil_ajuda⟩ → quan
    ▸ Que vagi bé, Nil. → (es queda) · FI

[flors]
    NIL: Aquestes no necessiten aigua. Són de plàstic. Per això duren.
    ↪ menu

[palau]
    NIL: Cada dijous. A treure la pols de les plantes de plàstic del palau. Les plantes de plàstic també fan pols.
    NIL: El Magnat fa totes les festes en dijous. Vol la pols acabada de treure.
    NIL: Hi puc portar dos ajudants. Però no m'hi jugo la feina per desconegudes.
    ⇒ +nil_palau
    ↪ menu

[magnat]
    NIL: El Magnat ho sap tot. Però prefereix les flors de plàstic. No es moren.
    NIL: I ell no vol que res es mori. Vol que tot duri. Que tot sigui seu.
    ↪ menu

[tomaquera]
    NIL: ...Shhh. El Magnat no vol plantes de veritat. «Gasten aigua, es moren i no es revaloren.»
    NIL: La rego amb la meva aigua de beure. Mig got al dia. Ella en vol dos.
    VET: I l'aigua que llença l'aire condicionat, a la reixa del jardí? ⟨si vet a verdant_jardi⟩
    JUGADORA: I l'aigua que llença l'aire condicionat, a la reixa del jardí? ⟨si no (vet a verdant_jardi)⟩
    NIL: Si l'hi tires de cop, la negues: la terra està seca com una teula. Li caldria un reg de veritat. Gota a gota.
    VET: ...El pare en té un, al graner. «Que encara serveix.» ⟨si vet a verdant_jardi i NO reg_agafat⟩
    JUGADORA: ...El pare en té un, al graner. «Que encara serveix.» ⟨si no (vet a verdant_jardi) i NO reg_agafat⟩
    VET: ...Un reg gota a gota. En portem un, el del graner del pare. ⟨si vet a verdant_jardi i reg_agafat⟩
    JUGADORA: ...Un reg gota a gota. En portem un, el del graner del pare. ⟨si no (vet a verdant_jardi) i reg_agafat⟩
    ⇒ +cal_reg
    ↪ menu

[regada]
    NARRADOR: En Nil va al cobert. Quan torna, té els ulls molls.
    NIL: Dijous us porto al palau. Com a ajudants. Porteu guants: les plantes de plàstic piquen.
    NIL: I al palau no hi digueu el meu nom. Ni el de la tomaquera.
    ⇒ +nil_ajuda
    ↪ menu

[quan]
    NIL: Dijous. Demà. Us espero a la llançadora.
    ↪ menu

```

## Diàleg `nil_palau` amb Nil

```
COMENÇA A: hola

[hola]
    NIL: Jo trec la pols. Tu fes la teva.
    NIL: Ah: a la sala de control hi ha una càmera. Hi posaré unes flors al davant. Fan pols.
    NIL: La noia de la fregona és la Lia. La filla d'en Bru. No parla amb ningú. ⟨si NO lia_avisada⟩

```

## Diàleg `pare` amb Pare

```
COMENÇA A: torna (si ha vist pare.hola) · hola

[hola]
    PARE: Qui és? Ah! Les meves noies! Ja era hora. ⟨si iri a granja_casa i vet a granja_casa⟩
    PARE: Qui és? Ah! La meva Iri! Ja era hora. ⟨si no (iri a granja_casa i vet a granja_casa) i juga iri⟩
    PARE: Qui és? Ah! La meva Vet! Ja era hora. ⟨si no (iri a granja_casa i vet a granja_casa) i juga vet⟩
    PARE: Aquí ens donen un got d'aigua al dia, i diuen que és un luxe. El luxe el pago jo.
    ↪ menu

[torna]
    PARE: Altra vegada? Que no tinc res al foc. Ni aigua per bullir-lo.
    ↪ menu

[menu]
    ▸ Com estàs, papa? ⟨una vegada⟩ → com
    ▸ Explica'ns alguna cosa de la granja. → temporal
    ▸ Papa, l'avi va vendre l'aigua del pou a Verne? ⟨una vegada, si caixa_oberta⟩ → verne
    ▸ Papa, on és l'escriptura de la granja? ⟨si NO caixa_oberta i NO quadre_apartat⟩ → escriptura
    ▸ La caixa forta té un teclat. Quina és la paraula? ⟨si quadre_apartat i NO caixa_oberta⟩ → contrasenya
    ▸ Papa, podem vendre llavors del banc a la Juana, d'Aqua? ⟨si juana_llavors i NO permis_pare⟩ → llavors
    ▸ Papa, ens deixes el reg gota a gota del graner? ⟨si (cal_reg o reg_volgut) i NO permis_reg⟩ → reg
    ▸ Adeu, papa. → adeu · FI

[escriptura]
    PARE: Al lloc segur. Darrere de la mare.
    JUGADORA: ...La mare està morta, papa.
    PARE: Del quadre de la mare, filla. Quina mainada.
    ⇒ +pista_quadre
    ↪ menu

[contrasenya]
    PARE: La paraula... És qui ens esperava a la porta. Cada dia. Movent la cua.
    JUGADORA: Qui ens esperava a la porta, movent la cua... El gos! Com es deia? Fa tants anys... ⟨si NO bol_vist⟩
    JUGADORA: Qui ens esperava a la porta, movent la cua... En Titus! El nom està gravat al bol. ⟨si bol_vist⟩
    JUGADORA: El pare ho guarda tot. Segur que per la casa en queda alguna cosa. ⟨si NO bol_vist⟩
    ⇒ +pare_porta
    ↪ menu

[verne]
    PARE: L'avi va comprar un tractor. Un Brau 40, vermell. Deia que era el millor negoci de la seva vida.
    PARE: ...No va arrencar mai.
    ↪ menu

[llavors]
    PARE: Les llavors són per sembrar, no per guardar. Ho deia la mare. Endueu-vos-en.
    PARE: Però guardeu-ne un sac. Per si de cas.
    ⇒ +permis_pare
    ↪ menu

[reg]
    PARE: El reg? Per a què el voleu, si no hi ha aigua?
    JUGADORA: Per a una tomaquera. De veritat. ⟨si cal_reg⟩
    PARE: Una tomaquera de veritat? Fa anys que no en veig cap. Endueu-vos-el. I porteu-me'n un tomàquet. ⟨si cal_reg⟩
    JUGADORA: Per si de cas. ⟨si NO cal_reg⟩
    PARE: ...Per si de cas? Això ho heu après de mi. ⟨si NO cal_reg⟩
    PARE: Endueu-vos-el. I torneu-me'l enrotllat com cal, que és un reg, no un cabdell. ⟨si NO cal_reg⟩
    ⇒ +permis_reg
    ↪ menu

[com]
    PARE: Bé. Si no fos per la set. Ahir vaig somiar que plovia. Em vaig despertar xop.
    PARE: Era la infermera, regant les flors. De plàstic.
    ↪ menu

[temporal]
    PARE: El temporal del trenta-u! Tres dies plovent. La vaca Ramona va nedar fins al poble i va tornar amb un barret.
    PARE: Ningú no va saber mai de qui era, el barret.
    ↪ menu

[adeu]
    PARE: Adeu, noies. Porteu-me aigua. O una cervesa. O totes dues.

```

## Diàleg `radio_juana` amb Juana

```
COMENÇA A: torna (si ha vist radio_juana.hola) · hola

[hola]
    JUANA: Aqua, fons del mar. Juana. Si veneu aigua, no. Si la regaleu, digueu.
    JUGADORA: Som de la Cantimplora. La Capitana diu que tu saps on va l'aigua.
    JUANA: La Capitana diu moltes coses. Veniu i en parlarem.
    JUANA: Però no tinc diners per pagar cap viatge.
    ↪ menu

[torna]
    JUANA: Juana. Digueu.
    ↪ menu

[menu]
    ▸ Necessitem una càrrega per portar-te. Qualsevol cosa. ⟨si NO juana_llavors⟩ → feina
    ▸ Ja tenim les llavors a bord. Tres sacs del banc del pare. ⟨si juana_llavors i sacs_carregats i NO albara_fet⟩ → albara
    ▸ Quines llavors volies? ⟨si juana_llavors i NO sacs_carregats⟩ → llavors
    ▸ Fins ara. → (es queda) · FI

[feina]
    JUANA: Una càrrega... Doncs sí: llavors. Llavors que aguantin la secada.
    JUANA: Pagaria qualsevol cosa per llavors així. Bé: qualsevol cosa que no costi diners.
    JUGADORA: El pare té un banc de llavors al graner. Li ho hauré de demanar.
    ⇒ +juana_llavors
    ↪ menu

[llavors]
    JUANA: De secà, que aguantin la set. Les que tingueu. Carregueu-les a la nau i aviseu-me.
    ↪ menu

[albara]
    JUANA: ...De veritat? Tres sacs?
    JUANA: Doncs firmo. Albarà número u: tres sacs de llavors, pagament en espècie. Ara us l'envio per la impressora de la ràdio.
    [SO: paper] NARRADOR: La ràdio treu un paper, xiulant.
    JUANA: Us espero al fons del mar. Baixeu amb compte: les escales s'acaben abans que el port.
    ⇒ +albara_fet, rep albara
    ↪ menu

```

## Diàleg `rosa` amb Rosa

```
COMENÇA A: baixat (si tomas_baixa i no (ha vist rosa.baixat)) · torna (si ha vist rosa.hola) · hola

[hola]
    ROSA: Sou de la nau d'en Tomàs?
    JUGADORA: ...Sí.
    ROSA: Digueu-li que menja poc. I que no cal que baixi. Ja ho sé, que és allà dalt. ⟨si NO cal_gala⟩
    ROSA: Digueu-li que menja poc. Ja ho sé, que és allà dalt. ⟨si cal_gala⟩
    ↪ menu

[torna]
    ROSA: Què hi ha?
    ↪ menu

[menu]
    ▸ Com va la vaga? ⟨una vegada⟩ → vaga
    ▸ Rosa, ens deixaries el vestit de reina del sindicat? ⟨si cal_gala i NO rosa_permis i NO vestit_agafat i NO rosa_vol_tomas⟩ → vestit
    ▸ Rosa, el vestit de reina del bagul... ens el deixaries? Per si de cas. ⟨si vestit_volgut i NO cal_gala i NO rosa_permis⟩ → vestit_cas
    ▸ I el vestit, Rosa? ⟨si rosa_vol_tomas i NO tomas_baixa⟩ → espera
    ▸ En Tomàs... és bon noi. ⟨una vegada, si tomas_girat⟩ → tomas
    ▸ Res, Rosa. → (es queda) · FI

[vestit]
    ROSA: El de reina? Me'l vaig posar quan vaig ser reina de la Festa Major de la Fosa. Fa trenta anys.
    ROSA: Per entrar a casa del Magnat? Us el deixo. Però una cosa.
    ROSA: Fa setmanes que en Tomàs és a la vostra nau i encara no ha baixat la rampa. Que el vingui a buscar ell.
    ⇒ +rosa_vol_tomas
    ↪ menu

[vaga]
    ROSA: Ens van tallar l'aigua per fer-nos tornar a la mina. Doncs ara no tornem ni per aigua.
    ROSA: Bé. Per aigua, potser sí. Però no per la seva.
    ↪ menu

[tomas]
    ROSA: Ja ho sé. Per això em fa tanta ràbia.
    ↪ menu

[espera]
    ROSA: Que el vingui a buscar en Tomàs. Ell. No és tan lluny: és una rampa.
    ↪ menu

[vestit_cas]
    ROSA: Per si de cas de què? De ser reina?
    JUGADORA: Per si de cas.
    ROSA: Fa trenta anys que espera un cas. Endueu-vos-el. I torneu-me'l sense taques.
    ⇒ +rosa_permis
    ↪ menu

[baixat]
    ROSA: Ha baixat. Ha crescut. Menja poc, però ha baixat.
    ↪ menu

```

## Diàleg `subhasta` amb Holm

```
COMENÇA A: inici

[inici]
    NARRADOR: Queden {lots} lots.
    NARRADOR: Al faristol, el lot {lot}: el subsòl de Terra-2. ⟨si lot ≤ 4⟩
    NARRADOR: Al faristol, el lot {lot}: la cartera de deutors. ⟨si lot ≥ 5 i lot ≤ 8⟩
    NARRADOR: Al faristol, el lot {lot}: el mar d'Aqua. ⟨si lot ≥ 9 i lot ≤ 11⟩
    NARRADOR: Al faristol, el lot 12, l'últim: els peixos d'Aqua. ⟨si lot ≥ 12⟩
    NARRADOR: El martell, quiet: en Holm encara revisa el lot. ⟨si pausa > 0⟩
    ▸ (Treure el contracte 7.788.) Tinc una objecció. Per escrit. ⟨si NO objeccio_7788⟩ → c7788
    ▸ Una pregunta per al Banc: accepten ànimes en garantia? ⟨si NO objeccio_anima⟩ → anima
    ▸ I els peixos del lot 12? Van amb el mar, o a part? ⟨si NO objeccio_peixos⟩ → peixos
    ▸ (Esperar.) → (es queda) · FI

[c7788]
    HOLM: Una objecció per escrit. El reglament obliga a llegir-la. Endavant. ⟨si lot ≤ 4⟩
    IRI: «L'aigua del subsòl d'aquesta finca pertany a Verne S.A. a perpetuïtat. A canvi: un tractor (model Brau 40, vermell).» Finca de Terra-2. ⟨si lot ≤ 4⟩
    HOLM: Una contrapartida. S'ha de verificar que es va lliurar. ...I que arrenca. ⟨si lot ≤ 4⟩
    IRI: Des que tinc ús de raó, no. ⟨si lot ≤ 4⟩
    HOLM: Lot en revisió. ⟨si lot ≤ 4⟩
      ⇒ +objeccio_7788, pausa += 3
    NARRADOR: En Holm truca a Terra-2 per saber si arrenca un tractor. El Magnat tamborineja al faristol. ⟨si objeccio_7788⟩
    HOLM: El subsòl de Terra-2 ja és venut, senyora. Les objeccions, al lot que toquen. ⟨si lot > 4⟩

[anima]
    IRI: Entre aquests deutes hi ha el d'una nau cisterna. Interès lligat al preu de l'aigua. I una casella marcada: «Ànima (opcional)». ⟨si lot ≥ 5 i lot ≤ 8⟩
    HOLM: ...El reglament no diu res d'ànimes. Lot en revisió. ⟨si lot ≥ 5 i lot ≤ 8⟩
      ⇒ +objeccio_anima, pausa += 3
    NARRADOR: En Holm obre el reglament: quatre-cents articles. Cap no parla d'ànimes. Els llegeix tots. ⟨si objeccio_anima⟩
    HOLM: Els deutors són més tard, senyora. Ara venem el subsòl de Terra-2. ⟨si lot < 5⟩
    HOLM: Els deutors ja són venuts, senyora. Amb ànima i tot. ⟨si lot > 8⟩

[peixos]
    MAGNAT VERNE: A part, senyora Pruna. El mar es ven buit. Els peixos són el lot 12. ⟨si lot ≥ 9 i lot ≤ 11⟩
    HOLM: Llavors s'ha de certificar que al mar no n'hi queda cap. I quants n'hi ha a l'aquari. Lot en revisió. ⟨si lot ≥ 9 i lot ≤ 11⟩
      ⇒ +objeccio_peixos, pausa += 3
    NARRADOR: En Holm compta els peixos de l'aquari. Es mouen. Torna a començar. ⟨si objeccio_peixos⟩
    MAGNAT VERNE: Senyora Pruna, el lot dels peixos és més tard. No m'interrompi. ⟨si lot < 9⟩
    MAGNAT VERNE: El mar ja és venut, senyora Pruna. Ara venem els peixos. Puja, o no puja? ⟨si lot ≥ 12⟩

```

## Diàleg `tauler` amb Vet

```
COMENÇA A: inici

[inici]
    NARRADOR: Els paperets del tauler, amb la lletra de la Vet:
    NARRADOR: Trobar l'escriptura de la granja (el pare ho sap; el videotelèfon és a la casa). ⟨si escena = 1 i NO caixa_oberta⟩
    NARRADOR: Què fa una bomba de Verne al nostre pou? ⟨si escena = 1 i NO bomba_llegida⟩
    NARRADOR: Parlar amb la Capitana, al pont. ⟨si escena = 2 i NO cap_condicions⟩
    NARRADOR: Un albarà: una feina de veritat per a Aqua (ràdio del pont: la Juana). ⟨si escena = 2 i cap_condicions i no (té albara) i NO capitana_accepta⟩
    NARRADOR: Llavors per a la Juana: el banc del pare, al graner (demanar-li permís pel videotelèfon). ⟨si escena = 2 i juana_llavors i NO sacs_carregats⟩
    NARRADOR: Llavors carregades: avisar la Juana per ràdio. ⟨si escena = 2 i sacs_carregats i NO albara_fet⟩
    NARRADOR: L'injector de la nau està esquerdat: que el miri la Vet (el motor, a la bodega). ⟨si escena = 2 i cap_condicions i NO injector_vist⟩
    NARRADOR: Un injector nou: el tractor de l'avi en té un d'igual (oli i una clau anglesa). ⟨si escena = 2 i injector_vist i NO injector_posat⟩
    NARRADOR: Albarà i injector: tornar a la Capitana. ⟨si escena = 2 i té albara i injector_posat i NO capitana_accepta⟩
    NARRADOR: Rumb a Aqua: el mapa del pont. ⟨si escena = 2 i capitana_accepta⟩
    NARRADOR: Baixar al fons del mar d'Aqua: la grua del port. ⟨si escena = 3 i NO baixada_feta⟩
    NARRADOR: Parlar amb la Juana, al fons del mar. ⟨si escena = 3 i baixada_feta i NO juana_fet⟩
    NARRADOR: Ferrum: trobar en Bru (el sindicat) i donar-li la carta de la Juana. ⟨si escena = 4 i NO bru_set⟩
    NARRADOR: Aigua per a la canalla del piquet de Ferrum. ⟨si escena = 4 i bru_set i NO canalla_beu⟩
    NARRADOR: El condensador del carrer s'engega amb una targeta de treballador actiu de Verne. ⟨si escena = 4 i cal_targeta i NO mosca_contractada i NO canalla_beu⟩
    NARRADOR: La font de Verne contracta: vint-i-quatre hores, cap vaga i cap aigua. ⟨si escena = 4 i contractacio_vista i NO mosca_contractada i NO canalla_beu⟩
    NARRADOR: La Mosca té feina i targeta. El condensador és al carrer. ⟨si escena = 4 i mosca_contractada i NO canalla_beu⟩
    NARRADOR: Tornar a parlar amb en Bru. ⟨si escena = 4 i canalla_beu i NO promesa_lia⟩
    NARRADOR: Preparar el motlle de les claus al llit de colada de la fosa. ⟨si escena = 4 i promesa_lia i NO motlle_preparat i NO cal_sorra⟩
    NARRADOR: Sorra fina per al motlle: a Ferrum només n'hi ha de pedra picada. ⟨si escena = 4 i cal_sorra i NO motlle_preparat⟩
    NARRADOR: La platja d'Aqua ara és el lot 9 de Verne: de la línia de l'aigua de dimarts cap amunt. ⟨si escena = 4 i cal_sorra i lot9_vist i NO sorra_agafada⟩
    NARRADOR: La colada: una al forn i l'altra a la colada. ⟨si escena = 4 i motlle_preparat i NO claus_fetes⟩
    NARRADOR: Verdant: el jardiner Nil puja al palau cada dijous. ⟨si escena = 5 i NO nil_palau⟩
    NARRADOR: Mirar què guarda el Magnat a la residència d'estiu de Verdant. ⟨si escena = 5 i NO fidel_admet i no (ha vist fidel.hola)⟩
    NARRADOR: Entrar al despatx del Magnat: el robot de la porta només deixa passar gent «solvent». ⟨si escena = 5 i NO fidel_admet i ha vist fidel.hola⟩
    NARRADOR: Un aval d'un milió per a en Fidel. La granja, diu, val un crèdit. ⟨si escena = 5 i cal_aval i NO fidel_admet⟩
    NARRADOR: Remenar el despatx del Magnat. ⟨si escena = 5 i fidel_admet i no (carta_banc i invitacio_agafada i contracte_agafat)⟩
    NARRADOR: Que en Nil ens porti al palau com a ajudants. ⟨si escena = 5 i nil_palau i NO nil_ajuda⟩
    NARRADOR: Un reg gota a gota per a la tomaquera d'en Nil: el del pare, al graner de Terra-2. ⟨si escena = 5 i cal_reg i NO reg_agafat⟩
    NARRADOR: El graner de Terra-2 té un cadenat de Verne: només hi pot entrar la propietat. ⟨si escena = 5 i precinte_vist i NO graner_obert⟩
    NARRADOR: Qui informa el Magnat? Algú de la nau. ⟨si escena = 6 i cal_espia i NO tomas_girat⟩
    NARRADOR: Ensenyar el contracte a la Capitana. ⟨si escena = 6 i NO capitana_si⟩
    NARRADOR: Un vestit de gala per a l'Iri (al sindicat de Ferrum n'hi havia un). ⟨si escena = 6 i cal_gala i no (té vestit_arreglat (iri)) i NO vestit_agafat i NO rosa_vol_tomas⟩
    NARRADOR: La Rosa ens deixa el vestit si en Tomàs baixa a buscar-lo. ⟨si escena = 6 i rosa_vol_tomas i NO tomas_baixa⟩
    NARRADOR: El vestit de la Rosa va gran a l'Iri: l'agulla del calaix de la Vet. ⟨si escena = 6 i cal_gala i vestit_agafat i no (té vestit_arreglat (iri) o té vestit_arreglat (vet))⟩
    NARRADOR: El vestit arreglat és per a l'Iri. ⟨si escena = 6 i té vestit_arreglat (vet)⟩
    NARRADOR: Palau: la Vet ha de trobar la Lia (passadissos de servei). ⟨si escena = 7 i NO lia_avisada⟩
    NARRADOR: Fer arribar les claus a la Vet (la safata de les copes, al saló). ⟨si escena = 7 i no (té claus (vet)) i NO subhasta_comencada⟩
    NARRADOR: La Vet a la sala de control, l'Iri al saló de la subhasta. ⟨si escena = 7 i NO subhasta_comencada⟩
    NARRADOR: Obrir les tres vàlvules (la clau al pany, i girar) abans que s'acabin els lots, sense espantar el Magnat. L'Iri pot parar el martell: cada objecció, al seu lot. ⟨si sync_subhasta i valvules < 3⟩
    NARRADOR: 31: el Magnat s'aguanta amb la seva reserva. La palanca vermella. ⟨si sync_subhasta i valvules ≥ 3⟩

```

## Diàleg `teclat` amb Iri

```
COMENÇA A: inici

[inici]
    NARRADOR: El teclat té cinc caselles.
    JUGADORA: Qui ens esperava a la porta... El gos! Però com es deia? ⟨si pare_porta i NO bol_vist⟩
    ▸ M-A-R-I-A. ⟨una vegada⟩ → maria
    ▸ V-E-R-N-E. ⟨una vegada, si bomba_llegida⟩ → verne
    ▸ T-I-T-U-S. ⟨si bol_vist⟩ → titus
    ▸ Ho deixo estar. → (es queda) · FI

[maria]
    [SO: teclat] JUGADORA: La mare. No.
    NARRADOR: El teclat fa un soroll de queixa.
    ↪ inici

[verne]
    [SO: teclat] JUGADORA: No. El pare no faria mai servir aquesta paraula per a res.
    ↪ inici

[titus]
    [SO: caixa_forta] NARRADOR: Clic.
    JUGADORA: L'escriptura de la granja! I un altre paper, més vell.
    JUGADORA: «Contracte 7.788. L'aigua del subsòl d'aquesta finca pertany a Verne S.A. a perpetuïtat. A canvi: un tractor Brau 40, vermell.» Signat: l'avi.
    VET: L'avi va vendre el pou per un tractor. ⟨si iri a granja_casa i vet a granja_casa⟩
    IRI: El tractor que hi ha al graner. Que no ha arrencat mai. ⟨si iri a granja_casa i vet a granja_casa⟩
    VET: Un pou per un tractor que no arrenca. Ens l'han venut dues vegades. ⟨si iri a granja_casa i vet a granja_casa⟩
    JUGADORA: L'avi va vendre el pou per un tractor. El del graner, que no ha arrencat mai. ⟨si no (iri a granja_casa i vet a granja_casa)⟩
    ⇒ +caixa_oberta, rep escriptura, rep contracte_7788

```

## Diàleg `tomas` amb Tomàs

```
COMENÇA A: enxampat (si tomas_descobert i NO tomas_girat) · girat (si tomas_girat) · nervios (si escena = 6 i trucada_feta) · torna (si ha vist tomas.hola) · hola

[hola]
    TOMÀS: Hola! Soc en Tomàs, el mecànic nou. Bé, el mecànic. Vull dir que soc nou.
    TOMÀS: Tu ets la pilot! La de la jaqueta! Et vaig veure aterrar a Ferrum amb un motor encès! ⟨si juga iri⟩
    TOMÀS: Tu ets l'enginyera. No em revisis els cargols, si us plau. Encara no. ⟨si juga vet⟩
    TOMÀS: I on anirem, ara? Per saber quina roba portar.
    ↪ menu

[torna]
    TOMÀS: Digues! I on anem, després? És per la roba. ⟨si escena ≤ 5⟩
    ↪ menu

[nervios]
    TOMÀS: Bona nit! Jo no he fet res. Vull dir: bona nit.
    ↪ menu

[menu]
    ▸ On has après mecànica? ⟨una vegada⟩ → pilot
    ▸ Em deixes la clau anglesa? ⟨si injector_vist i NO clau_donada⟩ → clau
    ▸ Per què et va contractar la Capitana? ⟨una vegada⟩ → contracte
    ▸ Em dones el paper de plata del teu entrepà? ⟨si grua_vista i NO paper_donat⟩ → paper
    ▸ Tomàs, la teva mare vol que baixis tu a buscar el vestit de reina. ⟨si rosa_vol_tomas i NO tomas_baixa i planeta = "ferrum"⟩ → mare · FI
    ▸ Res, Tomàs. → (es queda) · FI

[clau]
    TOMÀS: La clau anglesa? És meva. Bé, és de la nau. Bé, la porto jo.
    TOMÀS: Aquí la tens. Me la tornaràs?
    JUGADORA: Potser.
    ⇒ +clau_donada, rep clau_anglesa
    ↪ menu

[paper]
    TOMÀS: El paper de plata? És... per reciclar. Bé, té. Està una mica escrit per dins.
    JUGADORA: Números escrits a boli... Algú fa servir el paper de plata de llibreta.
    ⇒ +paper_donat, rep paper_plata
    ↪ menu

[contracte]
    TOMÀS: Va dir que cobrava poc. I cobro poc. Molt poc. Gairebé no cobro.
    TOMÀS: Quan la nau ja no tenia feina. Sort que la Capitana és generosa.
    ↪ menu

[pilot]
    TOMÀS: A Ferrum. La meva mare és minera. Jo volia ser pilot.
    TOMÀS: Però ser pilot costa una fortuna. La llicència, les hores de vol... Algun dia.
    ↪ menu

[enxampat]
    TOMÀS: ...Ho heu trobat.
    ▸ Ens has venut! ⟨si no (ha vist tomas.venut)⟩ → venut
    ▸ Ho diré a la Capitana. ⟨si no (ha vist tomas.amenaca)⟩ → amenaca
    ▸ Per què? ⟨si no (ha vist tomas.per_que)⟩ → per_que
    ▸ Jo t'ensenyo a volar. De franc. Però des d'ara, al Magnat li expliques el que jo et digui. ⟨si juga iri⟩ → girar
    ▸ (Això ho ha d'arreglar l'Iri. És amb ella que en Tomàs vol volar.) ⟨si juga vet⟩ → vet_no · FI

[venut]
    TOMÀS: No! Bé, sí. Una mica. No sabia que era tant.
    ↪ enxampat_menu

[amenaca]
    TOMÀS: No, si us plau. La Capitana em llançaria per la rampa. En vol.
    ↪ enxampat_menu

[per_que]
    TOMÀS: El Magnat em va prometre la llicència de pilot. Només havia d'explicar on anàveu i què fèieu.
    TOMÀS: Els comunicadors de canell passen per la ràdio de la nau. Des de la bodega, ho sento tot.
    TOMÀS: Jo no sabia que tallaria l'aigua als vaguistes. La meva mare és al piquet.
    TOMÀS: ...No m'hi vaig atrevir, a parlar-hi. Des de la rampa la vaig veure. ⟨si NO tomas_baixa⟩
    TOMÀS: Avui hi he parlat, per primer cop. D'això no li he dit res. ⟨si tomas_baixa⟩
    ↪ enxampat_menu

[enxampat_menu]
    ↪ enxampat2

[enxampat2]
    ▸ Ens has venut! ⟨si no (ha vist tomas.venut)⟩ → venut
    ▸ Ho diré a la Capitana. ⟨si no (ha vist tomas.amenaca)⟩ → amenaca
    ▸ Per què? ⟨si no (ha vist tomas.per_que)⟩ → per_que
    ▸ Jo t'ensenyo a volar. De franc. Però des d'ara, al Magnat li expliques el que jo et digui. ⟨si juga iri⟩ → girar
    ▸ (Això ho ha d'arreglar l'Iri. És amb ella que en Tomàs vol volar.) ⟨si juga vet⟩ → vet_no · FI

[vet_no]
    VET: Iri, vine a la bodega. Tenim un mecànic que vol ser pilot. I un problema. ⟨si no (iri a cantimplora_bodega)⟩
    VET: Iri. Tenim un mecànic que vol ser pilot. I un problema. És cosa teva. ⟨si iri a cantimplora_bodega⟩

[girar]
    TOMÀS: ...De franc? Per què ho faríeu de franc?
    IRI: No ho sé. És nou per a mi també.
    TOMÀS: ...D'acord. D'acord! Què li dic, al Magnat?
    IRI: Que hem plegat. Que la Vet plora. Que hem menjat llenties.
    TOMÀS: Hem menjat llenties.
    IRI: I demà, mentre som al palau, el que et digui jo.
    TOMÀS: A les ordres, pilot. Bé: a les ordres no. Amb les ordres.
    ⇒ +tomas_girat
    ↪ girat

[girat]
    ▸ Què li has dit, al Magnat? → informe
    ▸ Tomàs, la teva mare vol que baixis tu a buscar el vestit de reina. ⟨si rosa_vol_tomas i NO tomas_baixa i planeta = "ferrum"⟩ → mare · FI
    ▸ Res, Tomàs. → (es queda) · FI

[informe]
    TOMÀS: «Les germanes han plegat. La Vet plora. Hem menjat llenties.» M'ha contestat: «Excel·lent.»
    ↪ girat

[mare]
    TOMÀS: La mare? ...Vol que baixi jo?
    TOMÀS: Des de la rampa ja la veig. Baixar és una altra cosa.
    NARRADOR: En Tomàs s'eixuga les mans a la granota, dues vegades, i baixa la rampa.
    NARRADOR: Al piquet, la Rosa li diu alguna cosa. Ell mira a terra. Ella li arregla el coll de la granota.
    NARRADOR: Quan torna, porta el vestit de reina doblegat sota el braç, i la corona d'engranatge a la mà.
    TOMÀS: Diu que us el deixa. Que el torneu sense taques de cava. I que menjo poc.
    ⇒ +tomas_baixa, +rosa_permis, +vestit_agafat, rep vestit

```

## Diàleg `trucada` amb Magnat Verne

```
COMENÇA A: inici

[inici]
    MAGNAT VERNE: Les germanes de la granja 7.788. La pilot i l'enginyera.
    MAGNAT VERNE: Tres claus de comptador fos, una visita al meu despatx i un sac de llavors. Molt emprenedor. ⟨si NO fidel_tractor⟩
    MAGNAT VERNE: Tres claus de comptador fos, una visita al meu despatx i un tractor valorat en un milió. Molt emprenedor. ⟨si fidel_tractor⟩
    IRI: Com ho sap?
    MAGNAT VERNE: Jo ho sé tot. És car, però ho sé tot.
    IRI: Ens està veient?
    MAGNAT VERNE: No, senyora. Mirar la gent és feina del servei.
    MAGNAT VERNE: Us faig una oferta. Les claus, a canvi del vostre pou. Ple. Per escrit.
    MAGNAT VERNE: I una altra a la Capitana: el seu deute, perdonat, si la Cantimplora no torna a volar.
    NARRADOR: La Capitana no diu res. Es mira les mans.
    ▸ Acceptem. → si
    ▸ No. → no
    ▸ El pou ja és nostre. → no

[si]
    MAGNAT VERNE: Excel·lent. Envieu les claus amb el vostre mecànic.
    VET: No.
    NARRADOR: La Vet talla la comunicació. La pantalla s'encén tota sola: el Magnat no ha acabat.
    ↪ no

[no]
    MAGNAT VERNE: La residència Bon Repòs beu aigua Verne. Des d'avui, mig got per cap.
    MAGNAT VERNE: Ho sento. És el mercat.
      ⇒ preu_aigua := 97
    NARRADOR: La pantalla s'apaga. Al panell del pont, el preu salta: 97.
    [SO: videotelefon] NARRADOR: Truca el videotelèfon de la nau. És el pare.
    PARE: Avui ens han donat mig got. Diuen que és per culpa vostra.
    PARE: No sé què feu. Feu-ho bé.
    IRI: Com ho sabia? Les claus, el despatx, el sac de llavors... ⟨si NO fidel_tractor⟩
    IRI: Com ho sabia? Les claus, el despatx, el tractor... ⟨si fidel_tractor⟩
    VET: Algú li ho explica. Algú de la nau.
    CAPITANA OR: A mi no em mireu.
    IRI: I la invitació diu «Etiqueta rigorosa». Jo només tinc aquesta jaqueta.
    VET: I la Capitana, un impermeable.
    IRI: ...Al sindicat de Ferrum hi havia un vestit. Horrible. (pausa) Perfecte. ⟨si NO vestit_agafat⟩
    IRI: ...Tinc el vestit de reina de la Rosa. Horrible. ⟨si vestit_agafat⟩
    VET: El vas agafar per si de cas. ⟨si vestit_agafat⟩
    IRI: No en parlem. ⟨si vestit_agafat⟩
    ⇒ +trucada_feta, −trucada_activa, +cal_espia, +cal_gala

```

## Diàleg `verne_galeria` amb Magnat Verne

```
COMENÇA A: menu

[menu]
    MAGNAT VERNE: Senyora Pruna? ⟨si no (ha vist verne_galeria.piscines)⟩
    ▸ Per què estan buides, les piscines? ⟨una vegada⟩ → piscines
    ▸ I vostè, quina aigua beu? ⟨una vegada⟩ → aigua
    ▸ No té aigua, aquí dalt? ⟨si NO lia_reserva⟩ → reserva
    ▸ Com es diu el gos? ⟨una vegada⟩ → gos
    ▸ Quan comença la subhasta? → subhasta
    ▸ Disculpi, vaig per una copa. → (es queda) · FI

[piscines]
    MAGNAT VERNE: Una piscina plena és aigua que ja no es pot vendre.
    ↪ menu

[aigua]
    MAGNAT VERNE: Reciclada. Jo no em bec l'estoc.
    ↪ menu

[reserva]
    MAGNAT VERNE: Sota la piscina central. La meva reserva personal. Plena.
    MAGNAT VERNE: El meu últim barril. Per si de cas.
    VET: (pel comunicador) ...No diguis res.
    ⇒ +lia_reserva
    ↪ menu

[gos]
    MAGNAT VERNE: En Dividend. El vaig comprar quan valia poc.
    NARRADOR: En Dividend mira la piscina. Després mira el Magnat.
    ↪ menu

[subhasta]
    MAGNAT VERNE: Quan tothom tingui una copa a la mà. Al saló, senyora. Vingui: no s'ho perdi. Avui venem set.
    ↪ menu

```

## Pistes

```
escriptura — quan escena = 1 i NO pista_quadre · fins que pista_quadre o caixa_oberta
    1. L'escriptura és en algun racó de la casa del pare. El pare ho guarda tot... però sap on és cada cosa.
    2. El pare és a la residència. A la casa hi ha un videotelèfon.
    3. Truca al pare amb el videotelèfon de la casa i pregunta-li per l'escriptura.
quadre — quan pista_quadre i NO quadre_apartat · fins que quadre_apartat
    1. «Darrere de la mare», ha dit el pare. Del quadre de la mare.
    2. A la casa hi ha el quadre de la mare.
    3. Aparta de la paret el quadre de la mare.
caixa — quan quadre_apartat i NO caixa_oberta i NO pare_porta i NO bol_vist · fins que pare_porta o bol_vist o caixa_oberta
    1. Darrere el quadre hi ha una caixa forta amb un teclat de lletres. Qui en pot saber la paraula?
    2. El pare la deu saber.
    3. Pregunta al pare per la paraula de la caixa forta, amb el videotelèfon.
titus — quan quadre_apartat i pare_porta i NO bol_vist i NO caixa_oberta · fins que bol_vist o caixa_oberta
    1. Qui ens esperava a la porta, movent la cua: el gos. Com es deia?
    2. El pare no llença res. A la casa encara hi deu haver coses del gos.
    3. Mira el bol del gos, a la casa del pare.
teclat — quan quadre_apartat i bol_vist i NO caixa_oberta · fins que caixa_oberta
    1. El gos es deia Titus, i la paraula té cinc lletres.
    2. La caixa forta, darrere el quadre.
    3. Obre la caixa forta i tria T-I-T-U-S.
bomba — quan escena = 1 i NO bomba_llegida · fins que bomba_llegida
    1. Hi ha una bomba de Verne al nostre pou. Què hi fa?
    2. El panell de la bomba té cargols de cap de flor. Tenim una punta de flor, però li cal un mànec.
    3. Agafa el tornavís de la caixa d'eines del graner, ajunta'l amb la punta de flor (si la porta l'altra, doneu-vos-els) i fes-lo servir amb la bomba.
capitana — quan escena = 2 i NO cap_condicions · fins que cap_condicions
    1. Ens cal algú que voli a tot arreu i ho sàpiga tot.
    2. La Capitana, al pont de la Cantimplora, al port.
    3. Ves al port pel camí del pati, puja a la Cantimplora, ves al pont i parla amb la Capitana.
radio — quan escena = 2 i cap_condicions i NO juana_llavors · fins que juana_llavors
    1. La Capitana vol una feina de veritat, amb algú que pagui a l'altra banda.
    2. La Juana és a Aqua. La seva freqüència és al marc de la ràdio del pont.
    3. Fes servir la ràdio del pont i pregunta a la Juana quina càrrega voldria.
permis — quan juana_llavors i NO permis_pare · fins que permis_pare
    1. La Juana vol llavors que aguantin la secada. El pare té un banc de llavors al graner.
    2. Les llavors són del pare: cal demanar-l'hi.
    3. Truca al pare amb el videotelèfon de la casa i demana-li llavors per a la Juana.
sacs — quan permis_pare i NO sacs_agafats · fins que sacs_agafats
    1. El pare diu que sí.
    2. Les llavors són al graner.
    3. Agafa els sacs del banc de llavors del graner.
carrega — quan sacs_agafats i NO sacs_carregats · fins que sacs_carregats
    1. Les llavors han d'anar a la nau.
    2. A la bodega hi ha l'espai de càrrega.
    3. Fes servir els sacs de llavors amb l'espai de càrrega de la bodega.
albara — quan sacs_carregats i NO albara_fet · fins que albara_fet
    1. Les llavors ja són a bord. Cal que la Juana ho sàpiga.
    2. La ràdio del pont.
    3. Fes servir la ràdio del pont i digues-li a la Juana que ja tens les llavors.
injector — quan escena = 2 i cap_condicions i NO injector_vist i juga iri · fins que injector_vist
    1. La Cantimplora no vola: l'injector està esquerdat.
    2. El motor és a la bodega. La Vet en sap.
    3. Mira el motor de la bodega amb la Vet.
injector_vet — quan escena = 2 i cap_condicions i NO injector_vist i juga vet · fins que injector_vist
    1. La Cantimplora no vola: l'injector està esquerdat.
    2. El motor és a la bodega. I de motors, en sap la Vet.
    3. Mira el motor de la bodega.
tractor — quan injector_vist i NO injector_tret · fins que injector_tret
    1. El tractor de l'avi té el mateix injector que la Cantimplora.
    2. El cargol està rovellat: cal oli (hi ha una llauna al motor de la bodega) i una clau anglesa grossa (la porta en Tomàs).
    3. Agafa l'oli del motor, demana la clau anglesa a en Tomàs, posa oli al tractor del graner i treu-ne l'injector amb la clau.
injector2 — quan injector_tret i NO injector_posat i juga iri · fins que injector_posat
    1. L'injector va al motor de la Cantimplora.
    2. El munta la Vet.
    3. La Vet ha de fer servir l'injector amb el motor de la bodega (si el porta l'Iri, que l'hi doni o l'hi enviï amb la Mosca).
injector2_vet — quan injector_tret i NO injector_posat i juga vet · fins que injector_posat
    1. L'injector va al motor de la Cantimplora.
    2. El munta la Vet.
    3. Fes servir l'injector amb el motor de la bodega (si el porta l'Iri, que te'l doni o te l'enviï amb la Mosca).
entrega — quan (té albara (iri) o té albara (vet)) i injector_posat i NO capitana_accepta · fins que capitana_accepta
    1. Ja tenim albarà i injector.
    2. La Capitana és al pont.
    3. Parla amb la Capitana.
aqua — quan capitana_accepta i escena = 2 i juga vet · fins que escena ≥ 3
    1. Rumb a Aqua.
    2. El mapa de navegació, al pont. El fa servir l'Iri.
    3. Amb l'Iri, fes servir el mapa del pont i tria Aqua.
aqua_iri — quan capitana_accepta i escena = 2 i juga iri · fins que escena ≥ 3
    1. Rumb a Aqua.
    2. El mapa de navegació, al pont. Pilotar és cosa de l'Iri.
    3. Fes servir el mapa del pont i tria Aqua.
grua — quan escena = 3 i NO grua_vista · fins que grua_vista
    1. El mar d'Aqua és quaranta metres més avall. Com s'hi baixa?
    2. Al port hi ha una grua amb una cistella.
    3. Mira la grua del port.
fusible — quan grua_vista i NO grua_arreglada i no (té fusible_apanyat (iri) o té fusible_apanyat (vet)) i juga iri · fins que (té fusible_apanyat (iri) o té fusible_apanyat (vet)) o grua_arreglada
    1. A la cabina de la grua hi falta una peça. La Vet sabrà quina.
    2. A la grua li falta un fusible de trenta. A la nau només n'hi ha de deu.
    3. Un fusible de deu embolicat amb alguna cosa que condueixi... com el paper de plata. En Tomàs sempre dina amb entrepà embolicat.
    4. Agafa un fusible del quadre de la bodega, demana a en Tomàs el paper de plata del seu entrepà i que la Vet els ajunti.
fusible_vet — quan grua_vista i NO grua_arreglada i no (té fusible_apanyat (iri) o té fusible_apanyat (vet)) i juga vet · fins que (té fusible_apanyat (iri) o té fusible_apanyat (vet)) o grua_arreglada
    1. A la grua li falta un fusible de trenta. A la nau només n'hi ha de deu.
    2. Un fusible de deu embolicat amb alguna cosa que condueixi... com el paper de plata. En Tomàs sempre dina amb entrepà embolicat.
    3. Agafa un fusible del quadre de la bodega, demana a en Tomàs el paper de plata del seu entrepà i ajunta'ls.
fusible2 — quan (té fusible_apanyat (iri) o té fusible_apanyat (vet)) i NO grua_arreglada i juga iri · fins que grua_arreglada
    1. Ja tenim el fusible apanyat.
    2. El munta la Vet.
    3. La Vet ha de fer servir el fusible apanyat amb la grua del port.
fusible2_vet — quan (té fusible_apanyat (iri) o té fusible_apanyat (vet)) i NO grua_arreglada i juga vet · fins que grua_arreglada
    1. Ja tenim el fusible apanyat.
    2. El munta la Vet.
    3. Fes servir el fusible apanyat amb la grua del port.
baixar — quan grua_arreglada i NO baixada_feta · fins que baixada_feta
    1. Una a la cistella i l'altra als comandaments de la grua.
    2. Cal que siguin totes dues al port.
    3. Porta les dues protagonistes al port d'Aqua i fes servir la cistella.
juana — quan baixada_feta i NO juana_fet · fins que juana_fet
    1. La Juana viu al fons del mar, a la caseta del vaixell bolcat.
    2. Pregunta-li on és el mar, on va l'aigua i si es pot fer tornar.
    3. Parla amb la Juana i fes-li totes les preguntes fins que t'escrigui una carta per a en Bru.
bru — quan escena = 4 i NO bru_set · fins que bru_set
    1. La Juana ens ha enviat a Ferrum, a buscar en Bru.
    2. En Bru és al sindicat. No es fia de ningú, però la carta de la Juana l'ajudarà.
    3. Ves a Ferrum (amb el mapa del pont, si no hi sou), entra al sindicat i parla amb en Bru.
targeta — quan cal_targeta i NO mosca_contractada i NO canalla_beu i juga iri · fins que mosca_contractada o canalla_beu
    1. Què tinc: un condensador que només s'engega amb una targeta de treballador actiu de Verne. Qui en dona, de targetes? Verne, quan contracta.
    2. La pantalla de la font de Verne contracta. Però no vol ningú que faci vaga, que plegui a les cinc o que begui. Qui treballa tot el dia i no beu?
    3. Fes servir la Mosca amb la font de Verne: que s'hi presenti ella.
targeta_vet — quan cal_targeta i NO mosca_contractada i NO canalla_beu i juga vet · fins que mosca_contractada o canalla_beu
    1. Símptoma: el condensador no arrenca. Causa: no és una peça, és un permís. Una targeta de treballador actiu de Verne. On en fan?
    2. A la font de Verne hi ha una pantalla que contracta. Requisits: zero vagues, vint-i-quatre hores, zero aigua. Cap persona no els passa. Una màquina, potser.
    3. Fes servir la Mosca amb la font: que s'hi presenti ella.
targeta2 — quan (té targeta_verne (iri) o té targeta_verne (vet)) i NO canalla_beu · fins que canalla_beu
    1. La Mosca té feina, i targeta de treballador actiu.
    2. Fes servir la targeta de la Mosca amb el condensador del carrer.
canalla — quan bru_set i NO canalla_beu · fins que canalla_beu
    1. La canalla del piquet té set. Hi ha dues maneres d'ajudar-la.
    2. L'últim barril de la Cantimplora... o el condensador vell del carrer, que treu aigua de l'aire i que Verne ha tancat.
    3. Baixa al piquet el barril de la bodega, o mira què li passa al condensador del carrer.
bru2 — quan canalla_beu i NO bru_lia · fins que bru_lia
    1. La canalla ja beu.
    2. En Bru volia veure-ho.
    3. Torna a parlar amb en Bru.
promesa — quan bru_lia i NO promesa_lia i juga vet · fins que promesa_lia
    1. En Bru té por per la seva filla, la Lia, que treballa al palau.
    2. Algú li ha de fer una promesa. La que negocia és l'Iri.
    3. Parla amb en Bru amb l'Iri i promet-li que li portareu la Lia a casa.
promesa_iri — quan bru_lia i NO promesa_lia i juga iri · fins que promesa_lia
    1. En Bru té por per la seva filla, la Lia, que treballa al palau.
    2. Algú li ha de fer una promesa. I negociar és cosa de l'Iri.
    3. Parla amb en Bru i promet-li que li portareu la Lia a casa.
motlle — quan promesa_lia i NO motlle_preparat i NO cal_sorra · fins que cal_sorra o motlle_preparat
    1. En Bru ens ha donat el motlle de les claus.
    2. El motlle va al llit de colada, a la fosa.
    3. Entra a la fosa, passa a la colada i fes servir el motlle amb el llit de colada.
lot9 — quan cal_sorra i lot9_vist i NO franja_vista i NO sorra_agafada i juga iri · fins que franja_vista o sorra_agafada
    1. Què tinc: un cartell que diu que la platja és de Verne. Què diu exactament? Fins on arriba, el lot 9?
    2. Fins a la línia de l'aigua, amidada dimarts. I el mar d'Aqua no s'està quiet: les boies de la Juana ho mesuren.
    3. Mira les boies del fons: des de dimarts, el mar ha baixat. La sorra de sota la línia no és del lot 9. Agafa-la.
lot9_vet — quan cal_sorra i lot9_vist i NO franja_vista i NO sorra_agafada i juga vet · fins que franja_vista o sorra_agafada
    1. Símptoma: la sorra té amo. Causa: un cartell amb lletra petita. Llegeix la lletra petita.
    2. El lot 9 arriba fins a la línia de l'aigua de dimarts. Avaria del cartell: el mar no es queda on el van amidar.
    3. Mira les boies del fons: el mar ha baixat. La franja nova, entre la línia de dimarts i l'aigua, no és de Verne. Agafa'n la sorra.
sorra — quan cal_sorra i NO sorra_agafada · fins que sorra_agafada
    1. Cal sorra fina. On n'hem vist, de sorra fina com farina?
    2. Al fons del mar d'Aqua hi havia una platja.
    3. Ves a Aqua (amb el mapa del pont, si no hi sou), baixa al fons del mar i agafa la sorra fina.
motlle2 — quan promesa_lia i sorra_agafada i NO motlle_preparat · fins que motlle_preparat
    1. Ja tenim sorra fina.
    2. Torna a la fosa de Ferrum.
    3. Fes servir el motlle amb el llit de colada, amb la sorra a l'inventari.
colada_lloc — quan motlle_preparat i NO sync_colada i NO claus_fetes · fins que sync_colada o claus_fetes
    1. Una al forn i l'altra a la colada, a la vegada.
    2. La fosa té dues sales: el forn i la colada.
    3. Posa una protagonista a la sala del forn i l'altra a la de la colada (canvia de protagonista per moure l'altra).
c_manxa — quan sync_colada i NO manxa_oberta · fins que manxa_oberta
    1. Al forn, primer, el foc: la manxa.
c_metall — quan sync_colada i manxa_oberta i NO metall_carregat · fins que metall_carregat
    1. Al forn: el metall. La pila de comptadors.
c_escoria — quan sync_colada i metall_carregat i NO escoria_treta · fins que escoria_treta
    1. Al forn: fora l'escòria amb el rascle, abans d'abocar.
c_gresol — quan sync_colada i escoria_treta i NO colat · fins que colat
    1. A la colada: aboca el gresol.
c_sorra — quan sync_colada i colat i NO claus_fetes · fins que claus_fetes
    1. A la colada: tapa el motlle amb la sorra (fes servir la sorra amb el llit).
verdant — quan escena = 5 i NO nil_palau i NO fidel_admet · fins que nil_palau o fidel_admet
    1. En Bru ha dit: en Nil, el jardiner de la residència de Verdant, puja al palau cada dijous. I que el Magnat hi guarda papers.
    2. En Nil és a Verdant: s'hi va amb el mapa del pont.
    3. A Verdant, parla amb en Nil, al jardí.
nil — quan escena = 5 i NO nil_palau · fins que nil_palau
    1. En Nil és al jardí, parlant amb les flors.
    2. Parla amb en Nil.
tomaquera — quan nil_palau i NO tomaquera_vista · fins que tomaquera_vista
    1. En Nil no s'hi juga la feina per desconegudes. Què li importa, a en Nil?
    2. Mira el seu cobert.
    3. Entra al cobert del jardí i mira la tomaquera.
tomaquera2 — quan tomaquera_vista i NO cal_reg · fins que cal_reg
    1. Una tomaquera de veritat, mig seca.
    2. En Nil la rega d'amagat.
    3. Parla amb en Nil de la tomaquera.
precinte — quan (precinte_vist i NO graner_obert i ((cal_reg i NO reg_agafat) o (cal_aval i NO fidel_admet i NO sac4_agafat))) i juga iri · fins que graner_obert
    1. Què tinc: un cadenat de Verne que només s'obre a la propietat. Què vol: que demostri que la finca és nostra. Amb què?
    2. Un paper que digui de qui és la finca. Per a en Fidel no val res; per a un cadenat de Verne, potser sí.
    3. Fes servir l'escriptura de la granja amb la porta del graner.
precinte_vet — quan (precinte_vist i NO graner_obert i ((cal_reg i NO reg_agafat) o (cal_aval i NO fidel_admet i NO sac4_agafat))) i juga vet · fins que graner_obert
    1. Símptoma: graner tancat. Causa: un cadenat de Verne que només reconeix la propietat.
    2. Diagnosi: o li ensenyem qui és la propietat, amb l'escriptura que porta l'Iri, o el desmuntem. Va amb cargols de cap de flor.
    3. L'Iri: l'escriptura amb la porta del graner. O jo: el tornavís de cap de flor amb la porta del graner.
reg — quan cal_reg i NO reg_agafat · fins que reg_agafat
    1. La tomaquera necessita un reg gota a gota.
    2. El pare en té un al graner de Terra-2. Però «no es toca».
    3. A Terra-2 (amb el mapa del pont, si no hi sou), demana el reg al pare pel videotelèfon de la casa i agafa'l del graner.
reg2 — quan cal_reg i (té reg (iri) o té reg (vet)) i NO cal_agulla i juga iri · fins que cal_agulla
    1. Ja tenim el reg.
    2. Ara, a la tomaquera. Però muntar-lo és cosa de la Vet.
    3. La Vet ha de fer servir el reg amb la tomaquera del cobert.
reg2_vet — quan cal_reg i (té reg (iri) o té reg (vet)) i NO cal_agulla i juga vet · fins que cal_agulla
    1. Ja tenim el reg.
    2. Ara, a la tomaquera.
    3. Fes servir el reg amb la tomaquera del cobert.
agulla — quan cal_agulla i no (té agulla (iri) o té agulla (vet)) i NO reg_muntat i no (té reg_foradat (iri) o té reg_foradat (vet)) i juga iri · fins que (té agulla (iri) o té agulla (vet)) o reg_muntat o (té reg_foradat (iri) o té reg_foradat (vet))
    1. Els goters del reg estan tapats. Cal foradar-los.
    2. La Vet té una agulla al seu calaix.
    3. Agafa l'agulla del calaix de la Vet, a la bodega de la nau.
agulla_vet — quan cal_agulla i no (té agulla (iri) o té agulla (vet)) i NO reg_muntat i no (té reg_foradat (iri) o té reg_foradat (vet)) i juga vet · fins que (té agulla (iri) o té agulla (vet)) o reg_muntat o (té reg_foradat (iri) o té reg_foradat (vet))
    1. Els goters del reg estan tapats. Cal foradar-los.
    2. La Vet té una agulla al seu calaix.
    3. Agafa l'agulla del calaix de la Vet, a la bodega de la nau.
foradar — quan (té agulla (iri) o té agulla (vet)) i (té reg (iri) o té reg (vet)) i juga iri · fins que té reg_foradat (iri) o té reg_foradat (vet)
    1. Agulla i reg.
    2. La Vet ho ha de fer.
    3. Amb la Vet, fes servir l'agulla amb el reg.
foradar_vet — quan (té agulla (iri) o té agulla (vet)) i (té reg (iri) o té reg (vet)) i juga vet · fins que té reg_foradat (iri) o té reg_foradat (vet)
    1. Agulla i reg.
    2. Ho ha de fer la Vet.
    3. Fes servir l'agulla amb el reg.
muntar — quan (té reg_foradat (iri) o té reg_foradat (vet)) i juga iri · fins que reg_muntat
    1. El reg ja està a punt.
    2. La Vet ha de fer servir el reg amb la tomaquera.
muntar_vet — quan (té reg_foradat (iri) o té reg_foradat (vet)) i juga vet · fins que reg_muntat
    1. El reg ja està a punt.
    2. Fes servir el reg amb la tomaquera.
galleda — quan reg_muntat i NO tomaquera_regada i no (té galleda_plena (iri) o té galleda_plena (vet)) · fins que (té galleda_plena (iri) o té galleda_plena (vet)) o tomaquera_regada
    1. Falta l'aigua. La que llença el Magnat.
    2. Al jardí hi ha una reixa on degota l'aire condicionat. I al cobert, una galleda.
    3. Agafa la galleda del cobert i fes-la servir amb la reixa del jardí.
regar — quan (té galleda_plena (iri) o té galleda_plena (vet)) i NO tomaquera_regada · fins que tomaquera_regada
    1. Tenim aigua.
    2. Aboca-la a la tomaquera (amb el reg muntat).
    3. Fes servir la galleda plena amb la tomaquera.
nil2 — quan tomaquera_regada i NO nil_ajuda · fins que nil_ajuda
    1. La tomaquera beu.
    2. Digues-ho a en Nil.
fidel — quan escena = 5 i NO fidel_admet i NO cal_aval i juga vet · fins que fidel_admet o cal_aval
    1. Al despatx del Magnat, a la residència, hi pot haver coses que ens convinguin.
    2. El robot de la porta només deixa passar gent «solvent». Una inversora, per exemple. L'Iri sap fer-ne.
    3. Amb l'Iri, parla amb en Fidel i digues-li que ets inversora.
fidel_iri — quan escena = 5 i NO fidel_admet i NO cal_aval i juga iri · fins que fidel_admet o cal_aval
    1. Al despatx del Magnat, a la residència, hi pot haver coses que ens convinguin.
    2. El robot de la porta només deixa passar gent «solvent». Una inversora, per exemple. D'això, l'Iri en sap fer.
    3. Parla amb en Fidel i digues-li que ets inversora.
aval — quan cal_aval i no (té sac_llavors (iri) o té sac_llavors (vet)) i NO fidel_admet i juga iri · fins que (té sac_llavors (iri) o té sac_llavors (vet)) o fidel_admet
    1. Què tinc: una granja que per a en Fidel val un crèdit. Què vol: un milió. Què val, a Vesper, més que la terra? El que hi creix sense aigua. O el que a Verne li va costar car.
    2. El quart sac de llavors del pare, al graner de Terra-2. O el tractor de l'avi: en Fidel valora les coses pel que se'n va pagar l'última vegada.
    3. Porta a en Fidel el quart sac del graner de Terra-2 (amb el mapa del pont). O ensenya-li l'escriptura, escolta com valora les coses, i parla-li del tractor.
aval_vet — quan cal_aval i no (té sac_llavors (iri) o té sac_llavors (vet)) i NO fidel_admet i juga vet · fins que (té sac_llavors (iri) o té sac_llavors (vet)) o fidel_admet
    1. Símptoma: en Fidel no deixa passar l'Iri. Causa: li falta un actiu d'un milió. Recanvis: el que creix sense aigua, o el que a Verne li va costar un pou.
    2. El quart sac de llavors del pare, al graner de Terra-2. O el tractor de l'avi, que Verne va pagar amb l'aigua de la finca.
    3. Que l'Iri porti a en Fidel el quart sac del graner de Terra-2. O que li parli del tractor, després d'ensenyar-li l'escriptura.
aval2 — quan cal_aval i (té sac_llavors (iri) o té sac_llavors (vet)) i NO fidel_admet i juga vet · fins que fidel_admet
    1. Ja tenim un aval.
    2. En Fidel.
    3. Amb l'Iri, parla amb en Fidel i ofereix-li el sac de llavors.
aval2_iri — quan cal_aval i (té sac_llavors (iri) o té sac_llavors (vet)) i NO fidel_admet i juga iri · fins que fidel_admet
    1. Ja tenim un aval.
    2. En Fidel.
    3. Parla amb en Fidel i ofereix-li el sac de llavors.
despatx — quan fidel_admet i no (carta_banc i invitacio_agafada i contracte_agafat) · fins que carta_banc i invitacio_agafada i contracte_agafat
    1. En Fidel ens deixa passar. Al despatx del Magnat, a la residència, remenem.
    2. La calaixera, la paperera, l'arxivador.
    3. Amb l'Iri, entra a la residència: obre la calaixera, mira la paperera i obre l'arxivador del despatx.
espia — quan cal_espia i NO diu_carmanyola_vist i NO tomas_descobert · fins que diu_carmanyola_vist o tomas_descobert
    1. Algú de la nau ho explica tot al Magnat. Qui pregunta sempre on anem?
    2. En Tomàs. I la seva carmanyola fa bip a les nou.
    3. Mira la carmanyola d'en Tomàs, a la bodega.
diu — quan diu_carmanyola_vist i NO diu_aparta i no (té pernil (iri) o té pernil (vet)) · fins que (té pernil (iri) o té pernil (vet)) o diu_aparta
    1. En Diu dorm damunt la carmanyola. Té debilitat pel pernil.
    2. Hi ha pernil a la nevera de la bodega.
    3. Agafa el pernil de la nevera.
diu2 — quan (té pernil (iri) o té pernil (vet)) i NO diu_aparta · fins que diu_aparta
    1. Ofereix el pernil a en Diu.
    2. Fes servir el pernil amb la carmanyola.
carmanyola — quan diu_aparta i NO tomas_descobert · fins que tomas_descobert
    1. La carmanyola està lliure.
    2. Obre-la.
girar — quan tomas_descobert i NO tomas_girat i juga vet · fins que tomas_girat
    1. En Tomàs informa el Magnat. Per què ho fa?
    2. El Magnat li va prometre una llicència de pilot. L'Iri li pot oferir una cosa millor.
    3. Amb l'Iri, parla amb en Tomàs i ofereix-te a ensenyar-lo a volar.
girar_iri — quan tomas_descobert i NO tomas_girat i juga iri · fins que tomas_girat
    1. En Tomàs informa el Magnat. Per què ho fa?
    2. El Magnat li va prometre una llicència de pilot. L'Iri li pot oferir una cosa millor.
    3. Parla amb en Tomàs i ofereix-te a ensenyar-lo a volar.
contracte — quan escena = 6 i NO capitana_si · fins que capitana_si
    1. La Capitana té por del Magnat. Ara sabem per què.
    2. El contracte del despatx de Verdant.
    3. Parla amb la Capitana, al pont, amb el contracte a l'inventari.
gala — quan cal_gala i NO rosa_permis i NO rosa_vol_tomas i NO vestit_agafat · fins que rosa_permis
    1. La invitació demana etiqueta rigorosa.
    2. Al sindicat de Ferrum, al bagul de la colla de teatre, hi havia un vestit de reina. És de la Rosa.
    3. A Ferrum (amb el mapa del pont, si no hi sou), demana el vestit a la Rosa, al piquet.
gala_tomas — quan rosa_vol_tomas i NO tomas_baixa i juga iri · fins que tomas_baixa
    1. Què tinc: un vestit que la Rosa ens deixa. Què vol, la Rosa? No és un preu. És el seu fill.
    2. Fa setmanes que en Tomàs no baixa la rampa. La Rosa vol que vingui ell a buscar el vestit.
    3. Amb la nau a Ferrum, parla amb en Tomàs, a la bodega: digues-li que la seva mare vol que baixi.
gala_tomas_vet — quan rosa_vol_tomas i NO tomas_baixa i juga vet · fins que tomas_baixa
    1. Símptoma: la Rosa no ens dona el vestit. Causa: no ha baixat qui ella espera.
    2. Fa setmanes que en Tomàs no baixa la rampa. La Rosa vol que vingui ell a buscar el vestit.
    3. Amb la nau a Ferrum, parla amb en Tomàs, a la bodega: digues-li que la seva mare vol que baixi.
gala2 — quan rosa_permis i NO vestit_agafat · fins que vestit_agafat
    1. La Rosa diu que sí.
    2. Agafa el vestit del bagul del sindicat.
gala3 — quan cal_gala i vestit_agafat i no (té vestit_arreglat (iri) o té vestit_arreglat (vet)) i juga iri i escena < 7 · fins que té vestit_arreglat (iri) o té vestit_arreglat (vet)
    1. A l'Iri, el vestit li va gran.
    2. La Vet té agulla i fil.
    3. Amb la Vet, fes servir l'agulla amb el vestit.
gala3_vet — quan cal_gala i vestit_agafat i no (té vestit_arreglat (iri) o té vestit_arreglat (vet)) i juga vet i escena < 7 · fins que té vestit_arreglat (iri) o té vestit_arreglat (vet)
    1. A l'Iri, el vestit li va gran.
    2. La Vet té agulla i fil.
    3. Fes servir l'agulla amb el vestit.
gala4 — quan cal_gala i té vestit_arreglat (vet) i juga vet · fins que té vestit_arreglat (iri)
    1. El vestit és per a l'Iri.
    2. Dona-l'hi o envia-l'hi amb la Mosca.
gala4_iri — quan cal_gala i té vestit_arreglat (vet) i juga iri · fins que té vestit_arreglat (iri)
    1. El vestit és per a l'Iri, però el té la Vet.
    2. Que te'l doni o que te l'enviï amb la Mosca.
lia — quan escena = 7 i NO lia_prova i juga iri · fins que lia_prova
    1. Al palau, la Vet ha de trobar la Lia, la filla d'en Bru.
    2. És als passadissos de servei, amb una fregona.
    3. Amb la Vet, parla amb la Lia.
lia_vet — quan escena = 7 i NO lia_prova i juga vet · fins que lia_prova
    1. Al palau, la Vet ha de trobar la Lia, la filla d'en Bru.
    2. És als passadissos de servei, amb una fregona.
    3. Parla amb la Lia.
holm — quan escena = 7 i NO holm_parlat i (lia_prova o no (té claus (vet))) i juga vet · fins que holm_parlat
    1. L'Iri porta les claus i la nota d'en Bru. I la Vet les necessita.
    2. La safata de les copes del saló baixa al servei. Però en Holm, el del banc, no treu els ulls de sobre a l'Iri.
    3. Amb l'Iri, parla amb en Holm al saló.
holm_iri — quan escena = 7 i NO holm_parlat i (lia_prova o no (té claus (vet))) i juga iri · fins que holm_parlat
    1. L'Iri porta les claus i la nota d'en Bru. La Vet les necessita.
    2. La safata de les copes del saló baixa al servei. Però en Holm, el del banc, no treu els ulls de sobre a l'Iri.
    3. Parla amb en Holm, al saló.
safata_nota — quan holm_parlat i lia_prova i té nota_lia (iri) i juga vet · fins que no (té nota_lia (iri))
    1. La Lia vol la nota d'en Bru.
    2. La safata de les copes.
    3. Amb l'Iri, fes servir la nota amb la safata del saló.
safata_nota_iri — quan holm_parlat i lia_prova i té nota_lia (iri) i juga iri · fins que no (té nota_lia (iri))
    1. La Lia vol la nota d'en Bru.
    2. La safata de les copes.
    3. Fes servir la nota amb la safata del saló.
safata_claus — quan holm_parlat i té claus (iri) i juga iri · fins que no (té claus (iri))
    1. Les claus, a la Vet.
    2. La safata de les copes.
    3. Fes servir les claus amb la safata del saló.
safata_claus_vet — quan holm_parlat i té claus (iri) i juga vet · fins que no (té claus (iri))
    1. Les claus m'han d'arribar aquí baix.
    2. La safata de les copes.
    3. Amb l'Iri, fes servir les claus amb la safata del saló.
recollir — quan no (safata = "") i juga iri · fins que safata = ""
    1. Hi ha alguna cosa a les safates del servei.
    2. Amb la Vet, agafa-ho de les safates.
recollir_vet — quan no (safata = "") i juga vet · fins que safata = ""
    1. Hi ha alguna cosa a les safates del servei.
    2. Agafa-ho de les safates.
nota_lia — quan té nota_lia (vet) i NO lia_avisada i juga iri · fins que lia_avisada
    1. Dona la nota a la Lia.
    2. Amb la Vet, parla amb la Lia.
nota_lia_vet — quan té nota_lia (vet) i NO lia_avisada i juga vet · fins que lia_avisada
    1. Dona la nota a la Lia.
    2. Parla amb la Lia.
control — quan lia_avisada i té claus (vet) i NO subhasta_comencada · fins que subhasta_comencada
    1. Una a la sala de control i l'altra al saló.
    2. A la sala de control s'hi baixa amb l'ascensor de servei i la targeta de la Lia.
    3. Porta la Vet a la sala de control i l'Iri al saló de la subhasta.
subhasta_sola — quan sync_subhasta i valvules < 3 i (reinicis_subhasta ≥ 1 i NO objeccio_7788 i NO objeccio_anima i NO objeccio_peixos) · fins que objeccio_7788 o objeccio_anima o objeccio_peixos o valvules ≥ 3
    1. S'han acabat els lots abans que la Vet acabés la feina: la Vet sola no hi arriba.
    2. L'Iri ha de parar el martell des de l'escenari del saló, amb una objecció que toqui el lot que es ven.
    3. Iri: a l'escenari, el contracte 7.788 ara que es ven el subsòl de Terra-2, abans que la Vet giri cap pany.
subhasta_iri — quan sync_subhasta i valvules < 3 i juga iri i no (reinicis_subhasta ≥ 1 i NO objeccio_7788 i NO objeccio_anima i NO objeccio_peixos) · fins que valvules ≥ 3 o (objeccio_7788 i objeccio_anima i objeccio_peixos)
    1. Què tinc: tres coses que en Holm no pot deixar passar. Què vol: rematar de pressa. Què hi guanyo: temps, si l'objecció toca el lot que es ven.
    2. El 7.788 és un contracte del subsòl de Terra-2. El de la Capitana, un deute lligat al preu de l'aigua. I els peixos, el Magnat els ven a part del mar. Cada objecció, al seu lot: el catàleg és a la pantalla.
    3. A l'escenari: el contracte 7.788 amb els lots de Terra-2 (de l'1 al 4), l'ànima de la Capitana amb els deutors (del 5 al 8) i els peixos amb el mar d'Aqua (del 9 a l'11).
subhasta_vet — quan sync_subhasta i valvules < 3 i juga vet i no (reinicis_subhasta ≥ 1 i NO objeccio_7788 i NO objeccio_anima i NO objeccio_peixos) · fins que valvules ≥ 3
    1. Símptoma: a cada vàlvula, el Magnat remata més lots. Causa probable: la ratlla vermella. Quan la línia del preu passa per sota de 60, pica el martell sense parar.
    2. Cada dipòsit fa baixar el preu tants crèdits com milions de tones de gel té: ho diu l'indicador de cada pany. Si el preu aguanta per sobre de 60 i cau de cop al final, el Magnat només corre de debò una vegada.
    3. De petit a gran: T2, Ferrum i, l'últim, Aqua. A cada pany, les claus i girar. I que l'Iri vagi parant el martell.
reserva — quan sync_subhasta i valvules ≥ 3 i juga iri · fins que reserva_oberta
    1. 31. Per sobre de la ratlla, per culpa de la reserva del Magnat.
    2. La palanca vermella.
    3. Amb la Vet, acciona la palanca vermella de la reserva.
reserva_vet — quan sync_subhasta i valvules ≥ 3 i juga vet · fins que reserva_oberta
    1. 31. Per sobre de la ratlla, per culpa de la reserva del Magnat.
    2. La palanca vermella.
    3. Acciona la palanca vermella de la reserva.
```

## Finals

```
plou «Plou» — quan reserva_oberta
    NARRADOR: A la pantalla del saló: 29. Per sota de la ratlla vermella.
      ⇒ +al_final_lluny
    HOLM: Senyor Verne. Ni reserva ni garantia. Vint-i-nou. El Banc executa.
    MAGNAT VERNE: Jo soc el Magnat Verne.
    HOLM: Era.
    NARRADOR: Les vint-i-tres piscines s'omplen, d'una en una, en cascada, davant de tots els inversors.
    NARRADOR: En Dividend s'hi tira. Neda. El Magnat el mira. I plora.
    MAGNAT VERNE: Era meva.
    IRI: Ara és d'en Dividend.
    NARRADOR: La Lia, la Vet i l'Iri surten pel moll de càrrega, on les espera la Cantimplora.
    NARRADOR: Ningú no es fixa en en Diu, que passa per davant de l'aquari.
    NARRADOR: Tres setmanes després. Terra-2.
      ⇒ −iri_gala
    NARRADOR: Plou. Fa tres setmanes que plou. El pou és ple.
    NARRADOR: Al panell de la carretera, el preu ja no és de Verne: «AIGUA VESPER · 4 ▼». A sota: «Banc de Vesper. Ara, més a prop teu.»
    PARE: Fa sis anys que guardo aquest paraigua per si de cas. Ara que plou, me'l guardo.
    PARE: A la residència em volien cobrar el suplement d'aigua. Els he dit que ara me la bec a casa.
    IRI: El Magnat ho ha perdut tot.
    VET: I el gos ha après a nedar.
    IRI: I nosaltres, que no es pot salvar el món.
    VET: Però es pot salvar un pou. I tres planetes. I una noia de Ferrum que es diu Lia.
    IRI: No ens hi posem medalles.
    IRI: I el contracte 7.788?
    VET: Ara és del Banc, amb tots els drets del Magnat. La bomba del pou l'he desconnectada, i l'he tornada a tancar amb cargols de cap de flor.
    IRI: Que no obre cap tornavís del món.
    VET: Excepte el meu. Fins que el Banc se'n compri un.
    NARRADOR: La Vet porta l'últim barril fins al pou. El mira. I l'hi buida. ⟨si NO barril_donat⟩
    VET: Ja no cal per si de cas. ⟨si NO barril_donat⟩
    VET: Ni una paraula. ⟨si NO barril_donat⟩
    IRI: No he dit res. ⟨si NO barril_donat⟩
    VET: Ho has pensat. ⟨si NO barril_donat⟩
    NARRADOR: Arriba una caixa de Ferrum. A dins, un barril ple d'aigua del condensador i una nota d'en Bru: «Per si de cas.» ⟨si barril_donat⟩
    VET: Una mica de per si de cas està bé. ⟨si barril_donat⟩
    VET: Saps què és el pitjor?
    IRI: Què?
    VET: Que jo també tinc un calaix ple de coses que no faig servir. I no les llenço.
    IRI: Tu no tens vint-i-tres piscines buides.
    VET: No. Però l'entenc. I no m'agrada entendre'l.
    NARRADOR: En Diu entra al pati, xop, amb un peix platejat a la boca. El deixa als peus de l'Iri.
    IRI: Diu. Això és un peix.
    VET: És un regal.
    IRI: D'on ha tret un peix? A Terra-2 no n'hi ha hagut mai.
    VET: ...Era al palau?
    L'aigua no s'havia acabat. Estava guardada.
```
