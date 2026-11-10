# Revisió de textos

> Generat amb `npm run revisio` a partir de `game/data/`. No l'editis a mà.
>
> Per a cada cosa, les interaccions en l'ordre en què el motor les prova: s'agafa **la primera que encaixa**.
> Una interacció «SEMPRE» que no és l'última amaga les de sota.

## Sala L'oficina de facturació · `aeroport_oficina` (iri)

```
DECORAT llista_feta — es veu si llista_feta
DECORAT imprimint — es veu si imprimint
DECORAT acreditacions_llestes — es veu si acreditacions_llestes

TERMINAL «terminal»
    • use — si NO soler_distret
        JUGADORA: En Soler torna a ser a la porta. Si tecleja ara, ho sentirà.
    • use — si NO llista_feta
        [SO: teclat] JUGADORA: Vol BCMU-07, llista de tripulació. Afegeixo: «I. i V., tècniques de manteniment de caixes fortes».
        [SO: impressora] JUGADORA: I imprimeixo dues acreditacions.
        ⇒ +llista_feta, +imprimint
    • use — si NO imprimint i NO acreditacions_llestes i no té acreditacions
        [SO: impressora] JUGADORA: Ja som a la llista. Torno a imprimir les acreditacions.
        ⇒ +imprimint
    • use — SEMPRE
        JUGADORA: Ja som a la llista. La resta és cosa de la impressora.
    • look — SEMPRE
        JUGADORA: El terminal de facturació. Contrasenya: «facturacio1». La gent és meravellosa.

IMPRESSORA «impressora»
    • push/use — si imprimint
        JUGADORA: Va, va, va...
        [SO: impressora] NARRADOR: La impressora rumia, grinyola i, finalment, treu dos cartons plastificats.
        ⇒ −imprimint, +acreditacions_llestes
    • pickUp — si acreditacions_llestes
        JUGADORA: Dues acreditacions. Encara són calentes.
        ⇒ rep acreditacions, −acreditacions_llestes
    • pickUp — si imprimint
        JUGADORA: Encara imprimeix. Li podria donar ànims.
    • push/use/pickUp — SEMPRE
        JUGADORA: No hi ha res per imprimir.
    • look — si imprimint
        JUGADORA: Imprimint. A la velocitat d'un cargol amb ansietat.
    • look — SEMPRE
        JUGADORA: Una impressora làser del segle passat.

PORTA «porta»
    • use/open/walkTo — si no té acreditacions
        JUGADORA: Sense les acreditacions no me'n vaig.
    • use/open/walkTo — si NO soler_distret
        JUGADORA: En Soler em veuria sortir. Espero que la Vet el torni a entretenir.
    • use/open/walkTo — SEMPRE
        JUGADORA: Fora. Vet, ja les tinc!
        ⇒ +iri_fora, → aeroport_personal
    • look — SEMPRE
        JUGADORA: La sortida. A l'altra banda, en Soler. O no, si la Vet plora prou.

```

## Sala La porta de personal · `aeroport_personal` (iri)

```
EN ENTRAR
    • * (una vegada) — SEMPRE
        JUGADORA: La porta de personal. Teclat numèric, quatre xifres. I en Soler, a tres metres.

DECORAT porta_oberta — es veu si porta_oberta
DECORAT alarma — es veu si alarma_porta

TECLAT «teclat»
    • use/push — si iri_fora
        JUGADORA: Ja tinc les acreditacions. Ara, que la Vet acabi la funció.
    • use/push — si porta_oberta
        JUGADORA: Ja la sé obrir.
        ⇒ → aeroport_oficina
    • use/push — si NO soler_distret
        JUGADORA: En Soler mira cap aquí. Ara no.
    • use/push — si alarma_porta
        JUGADORA: La porta encara xiula! Vet, plora!
    • use/push — si codi_porta_llegit
        [SO: teclat_porta] JUGADORA: 8-4-2-6.
        NARRADOR: Clic.
        ⇒ +porta_oberta, → aeroport_oficina
    • use/push — SEMPRE
        JUGADORA: Provo sort: 1-2-3-4.
        [SO: alarma_porta] NARRADOR: La porta xiula.
        JUGADORA: Vet! Plora més fort!
        ⇒ +alarma_porta, alarma := 2
    • look — SEMPRE
        JUGADORA: Un teclat de quatre xifres. Les tecles 2, 4, 6 i 8 estan gastades. No és cap pista: és un teclat.

PORTA «porta de personal»
    • use/open/walkTo — si porta_oberta i NO iri_fora
        ⇒ → aeroport_oficina
    • use/open — SEMPRE
        JUGADORA: Tancada. Cal el codi del teclat.
    • look — SEMPRE
        JUGADORA: «Només personal autoritzat.» Avui, jo.

```

## Sala La terminal · `aeroport_terminal` (vet)

```
EN ENTRAR
    • * (una vegada) — SEMPRE
        [SO: megafonia] NARRADOR: Dimarts, de matinada. L'aeroport.
        [SO: auricular] IRI: Té. L'auricular dret. Ara el que diguis, ho sento.
        JUGADORA: I el que pensi?
        IRI: Això encara no. Jo vaig a la porta de personal. Tu fes que el guàrdia se'n vagi.
        JUGADORA: Un guàrdia que vigila una porta. Necessitarà un motiu per deixar-la.
        ⇒ +auricular_compartit

DECORAT cigarreta_mitja — es veu si sync_aeroport i cigarreta ≤ 8 i cigarreta > 4
DECORAT cigarreta_curta — es veu si sync_aeroport i cigarreta ≤ 4

SOLER «agent Soler»
    • talkTo — SEMPRE
        ⇒ diàleg soler
    • look — si soler_distret
        JUGADORA: En Soler busca un nen que no existeix. Amb molta dedicació.
    • look — SEMPRE
        JUGADORA: L'agent Soler, segons la placa. Vigila la porta de personal amb cara de no vigilar res. Té cara de bona persona.

TAULELL «taulell»
    • look — si codi_porta_llegit
        JUGADORA: El pòsit: 8-4-2-6. L'Iri ja ho sap.
    • look — si soler_distret
        JUGADORA: Sota el taulell hi ha un pòsit enganxat. «Porta personal: 8426.»
        JUGADORA: Iri: 8-4-2-6.
        ⇒ +codi_porta_llegit
    • look — SEMPRE
        JUGADORA: El taulell de facturació. Si hi remeno ara, en Soler em veurà.

VIDRIERA «vidriera»
    • look — si sync_aeroport
        JUGADORA: L'Ortega fuma a fora i, de tant en tant, mira cap a dins. Li queden {cigarreta} pipades, si fa no fa.
    • look — SEMPRE
        JUGADORA: Darrere la vidriera, la supervisora Ortega (ho diu el gafet) fuma i mira el mòbil. Entrarà quan s'acabi la cigarreta.

EMPLEAT «objectes perduts»
    • talkTo — si sync_aeroport
        JUGADORA: Ara no: he perdut un fill.
    • talkTo — SEMPRE
        ⇒ diàleg empleat
    • look — SEMPRE
        JUGADORA: L'oficina d'objectes perduts. L'empleat té cara d'haver-ho perdut tot, també la il·lusió.

MALETI «maletí» — hi és si no té maleti (vet)
    • look — SEMPRE
        JUGADORA: Un maletí de pell al prestatge d'objectes perduts. Té un adhesiu: «AGENDA 2019 — COMPTE, LLIMONA».
        ⇒ +maleti_vist
    • pickUp — SEMPRE
        JUGADORA: Darrere el taulell? Hauria de convèncer l'empleat que és meu.

ULLERES «ulleres» — hi és si no té ulleres (vet)
    • pickUp — si sync_aeroport
        JUGADORA: Ara no: he perdut un fill.
    • pickUp — SEMPRE
        JUGADORA: Unes ulleres de pasta oblidades. Me les poso. Ara semblo que llegeixi directives per gust.
        ⇒ rep ulleres, +ulleres_posades
    • look — SEMPRE
        JUGADORA: Unes ulleres de pasta en una taula de la cafeteria. Sense graduació. Amb autoritat.

NEN «nen»
    • talkTo/use/pickUp — si sync_aeroport i iri_fora
        JUGADORA: L'HE TROBAT! El meu fill!
        SOLER: Senyora... aquest nen és d'una altra família.
        JUGADORA: ...Tots els nens s'assemblen tant.
        NEN: ...
        NARRADOR: Mentrestant, l'Iri ja és a la porta d'embarcament amb dues acreditacions calentes.
        ⇒ +aeroport_fet, −sync_aeroport, −soler_distret, → avio
    • talkTo/use/pickUp — si sync_aeroport
        JUGADORA: Encara no: l'Iri no ha sortit.
    • talkTo/use/pickUp — SEMPRE
        JUGADORA: Aquest nen no és meu. Ni tan sols el conec.
    • look — SEMPRE
        JUGADORA: Un nen amb una samarreta vermella i un dinosaure. Mira el món amb desconfiança. Fa bé.

```

## Sala L'avió · `avio` — cinemàtica

```
EN ENTRAR
    • * — SEMPRE
        NARRADOR: A l'avió del BCMU, entre tècnics de debò.
        IRI: Té, la teva. Amb la teva cara, que costa d'imprimir.
        RIUS: Sou noves? Doncs benvingudes a la subcontracta. Aquí ningú no cobra el viatge.
        VET: Ni el viatge ni res, pel que veig.
        IRI: I aquest vestit? Fa una hora anaves amb la bomber.
        VET: Objectes perduts. Algú s'hi va deixar un vestit jaqueta de la meva talla. Era el destí.
        IRI: Era d'un altre.
        NARRADOR: L'avió s'enlaira cap a Ginebra.
        TÍTOL: Fi de l'Acte 1
        ⇒ perd acreditacions (iri), rep acreditacio (iri), rep acreditacio (vet), +acte1_fet, FINAL continuara

```

## Sala El rebost · `bar_rebost` (vet)

```
DECORAT calaix_obert — es veu si calaix_obert

CALAIX «calaix»
    • open/pickUp — si calaix_obert i NO recepta_agafada
        JUGADORA: La recepta secreta de llimonada. En una servilleta, com els grans secrets.
        ⇒ rep recepta, +recepta_agafada
    • open/pickUp — si calaix_obert
        JUGADORA: Buit. Com el pot de les propines a les deu.
    • open/pickUp/look — si NO sap_pany
        JUGADORA: Tancat. Un pany amb aplicació: d'aquests que s'obren des del mòbil.
        JUGADORA: L'Iri el podria obrir des de casa. Li hauria de trucar.
        ⇒ +sap_pany
    • open/pickUp — SEMPRE
        JUGADORA: Tancat. L'Iri el podria obrir des de casa, si li truco.
    • look — SEMPRE
        JUGADORA: El calaix d'en Tomàs. Hi guarda la recepta secreta de llimonada.

CAIXES «caixes»
    • look — SEMPRE
        JUGADORA: Caixes de cervesa, tovallons i un cartell de «Prohibit fumar» ple de cremades.

PORTA «bar»
    • use/open/walkTo — SEMPRE
        ⇒ → bar_sala
    • look — SEMPRE
        JUGADORA: Cap al bar.

```

## Sala Bar La Propina · `bar_sala` (vet)

```
EN ENTRAR
    • * (una vegada) — SEMPRE
        [SO: porta_bar] NARRADOR: Dilluns, nit. Bar La Propina, a la sortida de l'autopista.
        JUGADORA: Bona nit, Tomàs. Bona nit, Marcel. Bona nit, gent que no paga.

DECORAT tele_bassols — es veu si bassols
DECORAT rebost_tancat — es veu si tomas_rebost

MARCEL «Marcel»
    • give + tap — SEMPRE
        MARCEL: El tap del clauer d'en Tomàs! Ni se n'ha adonat, oi?
          ⇒ perd tap, +marcel_tap, donats += 1
        MARCEL: Ja en falten menys. ⟨si donats < 3⟩
        MARCEL: Tres de tres. Ara et fio. ⟨si donats ≥ 3⟩
        MARCEL: No les vull, eh. Volia saber si ho faries. ⟨si donats ≥ 3⟩
        NARRADOR: En Marcel li torna el tap i la recepta. ⟨si donats ≥ 3⟩
          ⇒ rep tap, rep recepta
        MARCEL: Pregunta. ⟨si donats ≥ 3⟩
    • give + recepta — SEMPRE
        MARCEL: La recepta secreta... «1. Obrir el pot. 2. Abocar.» Vint anys guardant un secret de pot.
          ⇒ perd recepta, +marcel_recepta, donats += 1
        MARCEL: Ja en falten menys. ⟨si donats < 3⟩
        MARCEL: Tres de tres. Ara et fio. ⟨si donats ≥ 3⟩
        MARCEL: No les vull, eh. Volia saber si ho faries. ⟨si donats ≥ 3⟩
        NARRADOR: En Marcel li torna el tap i la recepta. ⟨si donats ≥ 3⟩
          ⇒ rep tap, rep recepta
        MARCEL: Pregunta. ⟨si donats ≥ 3⟩
    • give + comandament — SEMPRE
        MARCEL: El comandament! A veure... Ah! El capítol del violí!
          ⇒ perd comandament, +marcel_comandament, donats += 1
        NARRADOR: En Tomàs surt del rebost amb el telèfon a la mà.
          ⇒ −tomas_rebost
        TOMÀS: Ja està. Som lliures. Tots dos.
        TOMÀS: ...Qui ha posat aquesta sèrie? Bé, igual. Avui no tinc forces.
        MARCEL: Ja en falten menys. ⟨si donats < 3⟩
        MARCEL: Tres de tres. Ara et fio. ⟨si donats ≥ 3⟩
        MARCEL: No les vull, eh. Volia saber si ho faries. ⟨si donats ≥ 3⟩
        NARRADOR: En Marcel li torna el tap i la recepta. ⟨si donats ≥ 3⟩
          ⇒ rep tap, rep recepta
        MARCEL: Pregunta. ⟨si donats ≥ 3⟩
    • give + qualsevol objecte — SEMPRE
        MARCEL: No, això no l'has pres a en Tomàs. No compta.
    • talkTo — SEMPRE
        ⇒ diàleg marcel
    • look — SEMPRE
        JUGADORA: En Marcel. Vint anys al BCMU, ara un cafè amb llet. Diu que és més feliç.

TOMAS «Tomàs» — hi és si NO tomas_rebost
    • give + tap — SEMPRE
        TOMÀS: ...El meu tap? On era?
        JUGADORA: A la barra. Allà on el deixes sempre.
        TOMÀS: ...Gràcies? Mai ningú m'havia tornat res.
        ⇒ perd tap, +tap_tornat
    • give + qualsevol objecte — SEMPRE
        TOMÀS: Jo només accepto efectiu. I propines, que també són efectiu.
    • talkTo — SEMPRE
        ⇒ diàleg tomas
    • look — SEMPRE
        JUGADORA: En Tomàs. Bigoti i ràbia, a parts iguals.

TAP_BARRA «clauer» — hi és si tap_barra
    • pickUp — SEMPRE
        JUGADORA: Al davantal. Ni se n'ha adonat.
        ⇒ rep tap, −tap_barra
    • look — SEMPRE
        JUGADORA: El clauer d'en Tomàs: un tap de la cervesera. Damunt la barra, sol i desprotegit.

COMANDAMENT_BARRA «comandament» — hi és si tomas_rebost i no té comandament i NO marcel_comandament
    • pickUp — SEMPRE
        JUGADORA: El ceptre d'en Tomàs. Partit fora.
        ⇒ rep comandament
    • look — SEMPRE
        JUGADORA: El comandament de la tele. Sense vigilància, per primera vegada en la història.

TELE «tele»
    • use + comandament — SEMPRE
        JUGADORA: No. Que ho faci en Marcel. És el seu premi.
    • look — si bassols
        JUGADORA: La Comissària Bassols. En Marcel no parpelleja.
    • look — SEMPRE
        JUGADORA: Futbol. Un equip que guanya molts diners contra un altre que en guanya més.

RETOL «rètol»
    • look — si cal_contrasenya
        JUGADORA: «El cliente siempre tiene razón (excepto si no paga)».
        JUGADORA: «Exceptosinopaga». Tot junt. És la contrasenya de la wifi. Sempre ho ha estat.
        ⇒ +contrasenya_llegida
    • look — SEMPRE
        JUGADORA: «El cliente siempre tiene razón (excepto si no paga)». La filosofia d'en Tomàs. I la de la banca mundial.

TELEFON «telèfon»
    • talkTo/use — SEMPRE
        ⇒ diàleg trucada
    • look — SEMPRE
        JUGADORA: El telèfon de paret del bar. Amb fil i tot. Per trucar a l'Iri.

PORTA_REBOST «rebost»
    • use/open/walkTo — si tomas_rebost
        JUGADORA: En Tomàs és a dins, divorciant-se d'una persona que no existeix. Millor no entrar.
    • use/open/walkTo — SEMPRE
        ⇒ → bar_rebost
    • look — SEMPRE
        JUGADORA: El rebost. I el despatx d'en Tomàs, que és el mateix amb una cadira.

PORTA «sortida»
    • use/open/walkTo — si NO marcel_fet
        JUGADORA: No me'n vaig sense parlar amb en Marcel. I el torn no s'acaba fins a les dues.
    • use/open/walkTo — si NO resum_fet
        JUGADORA: Abans he de trucar a l'Iri i explicar-li-ho tot.
    • use/open/walkTo — SEMPRE
        NARRADOR: La Vet plega. Al pot de les propines hi ha 9,20 €.
          ⇒ +propines
        JUGADORA: Les propines d'una nit. A Ginebra, potser un entrepà.
        [SO: porta_bar] TOMÀS: On és el meu tap? ⟨si NO tap_tornat⟩
        [SO: porta_bar] TOMÀS: Bona nit, Vet. I gràcies pel tap. ⟨si tap_tornat⟩
        ⇒ +bar_fet, esdeveniment situar, → aeroport_terminal
    • look — SEMPRE
        JUGADORA: La sortida. Fora, l'autopista i els camions que no paren mai.

```

## Sala La cuina · `pis_cuina` (vet)

```
EN ENTRAR
    • * (una vegada) — SEMPRE
        JUGADORA: Torn de nit al bar d'aquí a mitja hora. Abans, sobreviure a l'Iri.

DECORAT cable_cafetera — es veu si NO cable_tret
DECORAT nevera_oberta — es veu si nevera_oberta
DECORAT passaplats_obert — es veu si passaplats_obert

CAFETERA «cafetera»
    • pickUp/pull/use — si cable_tret
        JUGADORA: Ja no té cable. Ja no té sentit.
    • pickUp/pull/use — si cable_demanat
        JUGADORA: Adeu, cafè. Tot sigui per la banca mundial.
        ⇒ rep cable_alimentacio, +cable_tret
    • pickUp/pull/use — SEMPRE
        JUGADORA: La cafetera. Sense ella, aquesta casa s'apaga. Per què la tocaria?
    • look — si cable_tret
        JUGADORA: Sense cable. Com jo sense cafè.
    • look — SEMPRE
        JUGADORA: Cafè: el combustible del pla.

NEVERA «nevera»
    • open — si NO nevera_oberta
        [SO: nevera] JUGADORA: A veure què hi ha.
        JUGADORA: Hi ha una pizza per a demà. ⟨si NO pizza_demanada i no té pizza⟩
        JUGADORA: Pa i tonyina. ⟨si NO te_entrepa⟩
        JUGADORA: I un iogurt que ja vota.
        ⇒ +nevera_oberta
    • open — SEMPRE
        JUGADORA: Ja és oberta. Se m'escapa el fred.
    • close — si nevera_oberta
        JUGADORA: Tancada.
        ⇒ −nevera_oberta
    • look — si nevera_oberta
        JUGADORA: Hi ha una pizza per a demà. ⟨si NO pizza_demanada i no té pizza⟩
        JUGADORA: Pa i tonyina. ⟨si NO te_entrepa⟩
        JUGADORA: I un iogurt que ja vota.
    • look — SEMPRE
        JUGADORA: La nevera. Brunzeix com si es queixés. Té motius.
    • pickUp — si NO nevera_oberta
        JUGADORA: Primer l'hauria d'obrir.

PIZZA_NEVERA «pizza» — hi és si nevera_oberta i no té pizza (vet) i no té pizza (iri) i sacrifici ≠ "pizza"
    • pickUp — si pizza_demanada
        JUGADORA: Perdona'm, pizza. És per una bona causa. Crec.
        ⇒ rep pizza
    • pickUp — SEMPRE
        JUGADORA: És la pizza de demà. Demà és sagrat.
    • look — SEMPRE
        JUGADORA: Quatre formatges. L'únic pla que sempre surt bé.

TONYINA «pa i tonyina» — hi és si nevera_oberta i NO te_entrepa
    • pickUp — SEMPRE
        JUGADORA: M'emporto un entrepà de tonyina, per si de cas.
        IRI: Per si de cas què?
        JUGADORA: Per si de cas tinc gana.
        ⇒ rep entrepa, +te_entrepa
    • look — SEMPRE
        JUGADORA: Pa i tonyina. Un entrepà en potència.

PASSAPLATS «passaplats»
    • open — si NO passaplats_obert
        [SO: passaplats] JUGADORA: Obert. Ja em pots dir coses, Iri.
        ⇒ +passaplats_obert
    • open — SEMPRE
        JUGADORA: Ja és obert.
    • close — si passaplats_obert
        [SO: passaplats] JUGADORA: Tancat. Una mica de pau.
        ⇒ −passaplats_obert
    • close — SEMPRE
        JUGADORA: Ja és tancat. L'Iri, en canvi, no tanca mai.
    • use + cable_alimentacio — si passaplats_obert
        [SO: passaplats] JUGADORA: Té. El cable de la cafetera. Que consti en acta.
        IRI: Gràcies!
        ⇒ perd cable_alimentacio, rep cable_alimentacio (iri)
    • use + pizza — si passaplats_obert
        [SO: passaplats] JUGADORA: La pizza. Que el gat sàpiga el que val.
        IRI: La tracto com a una reina.
        ⇒ perd pizza, rep pizza (iri)
    • use + qualsevol objecte — si NO passaplats_obert
        JUGADORA: Pel vidre no passa. Primer l'hauria d'obrir.
    • use + qualsevol objecte — SEMPRE
        JUGADORA: L'Iri no ho necessita. I jo, potser sí.
    • talkTo/use — si passaplats_obert
        JUGADORA: Iri? Si em necessites, crida. Ja ho fas.
    • talkTo/use — SEMPRE
        JUGADORA: Està tancat. Primer l'hauria d'obrir.
    • look — SEMPRE
        JUGADORA: El passaplats. Per aquí l'Iri em demana coses que després no torna.

PLATS «plats»
    • look — SEMPRE
        JUGADORA: Nou dies. Els he comptat.
    • use/pickUp — SEMPRE
        JUGADORA: Avui no. Avui hi ha un pla.

PORTA «porta»
    • use/open/walkTo — si llibre_trobat
        [SO: porta_pis] JUGADORA: Claus, mòbil, davantal. Me'n vaig.
        IRI: Pregunta-li on és el servidor!
        JUGADORA: I tu renta els plats!
        ⇒ rep clau_casa, +vet_marxa, → bar_sala
    • use/open/walkTo — SEMPRE
        JUGADORA: Encara no. L'Iri està a punt de trobar alguna cosa, i després m'ho explicarà igualment.
    • look — SEMPRE
        JUGADORA: La porta del pis. A l'altra banda, el món, i el torn de nit.

```

## Sala L'estudi · `pis_estudi` (iri)

```
EN ENTRAR
    • * (una vegada) — SEMPRE
        [SO: teclat] JUGADORA: Ho tinc. Ho tinc ho tinc ho tinc. Amb un tres per cent de bateria, però ho tinc.
        JUGADORA: Vet? VET! Ho he trobat! Podem entrar a la banca mundial!
        VET: Jo també he trobat una cosa: que no has rentat els plats en nou dies.
        JUGADORA: Saps què és el més divertit? Que el BCMU té més diners que cent vuitanta països junts. I no són seus. Són dels altres.
        VET: I nosaltres no en tenim ni per pizzes.
        JUGADORA: Per això robem. Perquè no ens queda pizza.
        [SO: miol] JUGADORA: Però primer necessito internet de debò. El router nou encara és a la caixa.
        ⇒ comença acte1

DECORAT router_connectat — es veu si router_connectat
DECORAT fibra_connectada — es veu si fibra_connectada
DECORAT xarxa_connectada — es veu si xarxa_connectada
DECORAT alimentacio_connectada — es veu si alimentacio_connectada
DECORAT passaplats_obert — es veu si passaplats_obert

FINESTRA «finestra»
    • look — SEMPRE
        JUGADORA: Plou. La ciutat dorm. La pizzeria del davant, no.
    • open — SEMPRE
        JUGADORA: Si l'obro, entra la pluja i surt la wifi del veí.

POSTER «pòster»
    • look — SEMPRE
        JUGADORA: Un gat amb ulleres de sol i un 404. Error: motivació no trobada.

MATALAS «matalàs»
    • look — SEMPRE
        JUGADORA: El llit. Bé, el matalàs. El somier és una idea que encara no he implementat.

PIZZES «caixes de pizza»
    • look — SEMPRE
        JUGADORA: Quatre caixes. Totes buides. Les he comprovat dues vegades.
    • open — SEMPRE
        JUGADORA: Buida. Com les altres tres. Com el meu compte corrent.

ORDINADORS «ordinadors»
    • use — si trucada_demanada i NO trucada_feta
        [SO: teclat] JUGADORA: Veu sintètica: activada. Accent: dona enfadada. Ho puc fer.
        [SO: telefon_bar] NARRADOR: L'Iri truca al bar.
        TOMÀS: Digui? Bar La Propina.
        JUGADORA: (Veu sintètica) Soc la teva dona.
        TOMÀS: ...La meva dona? Jo no estic casat.
        JUGADORA: (Veu sintètica) Doncs ja ho saps. Vull el divorci.
        TOMÀS: ...Un moment.
        JUGADORA: He parlat amb una persona. Bé, ho ha fet el portàtil. Compta igual.
        ⇒ +trucada_feta, +tomas_rebost
    • use — si contrasenya_dita i NO calaix_obert
        [SO: teclat] JUGADORA: Xarxa del bar. Contrasenya: «exceptosinopaga». Dins.
        [SO: pany_clic] JUGADORA: Un pany intel·ligent de 19,99 €. Obrir. Fet.
        JUGADORA: Vet, el calaix és obert.
        ⇒ +calaix_obert
    • use — si NO router_connectat
        JUGADORA: Sense internet, només puc mirar el codi amb angoixa.
    • use — si vet_marxa
        JUGADORA: Ara no puc fer res més des d'aquí. Si la Vet em necessita, trucarà.
    • use — SEMPRE
        JUGADORA: Ja tinc el servidor. Ara cal saber on és. I això ho sap la Vet.
    • look — SEMPRE
        JUGADORA: Tres pantalles. Una pel codi, una per la documentació i una per mirar el codi amb angoixa.

ROUTER «router»
    • use + cable_xarxa — si diu_distret
        JUGADORA: Cable de xarxa: dins.
        [SO: router] JUGADORA: Llums verdes. Internet de debò. ⟨si cables = 2⟩
          ⇒ +router_connectat
        JUGADORA: Ja hi som. El Llibre Major: un servidor de 1984 que porta els comptes de tot el sistema. ⟨si cables = 2⟩
        JUGADORA: I no té internet. Per això ningú no l'ha hackejat mai. Cal entrar-hi en persona. ⟨si cables = 2⟩
        JUGADORA: És en algun lloc de la seu de Ginebra. Però on? ⟨si cables = 2⟩
        VET: Conec algú que ho sap. Beu cafè amb llet al bar i té opinió sobre tot. ⟨si cables = 2⟩
        JUGADORA: Qui? ⟨si cables = 2⟩
        VET: En Marcel. Va treballar vint anys al BCMU. Ara li costa pagar el dentista. ⟨si cables = 2⟩
        VET: Vaig a treballar. ⟨si cables = 2⟩
          ⇒ +llibre_trobat
        JUGADORA: Això és un sí. ⟨si cables = 2⟩
        ⇒ perd cable_xarxa, +xarxa_connectada, cables += 1
    • use + cable_xarxa — SEMPRE
        [SO: mossegada] JUGADORA: Diu! És un cable de xarxa, no un espagueti!
        NARRADOR: En Diu el desendolla d'una queixalada i se'l mira, satisfet.
        ⇒ +diu_ha_mossegat
    • use + cable_alimentacio — si diu_distret
        JUGADORA: El cable de la cafetera, al router. Que el cafè ens perdoni.
        [SO: router] JUGADORA: Llums verdes. Internet de debò. ⟨si cables = 2⟩
          ⇒ +router_connectat
        JUGADORA: Ja hi som. El Llibre Major: un servidor de 1984 que porta els comptes de tot el sistema. ⟨si cables = 2⟩
        JUGADORA: I no té internet. Per això ningú no l'ha hackejat mai. Cal entrar-hi en persona. ⟨si cables = 2⟩
        JUGADORA: És en algun lloc de la seu de Ginebra. Però on? ⟨si cables = 2⟩
        VET: Conec algú que ho sap. Beu cafè amb llet al bar i té opinió sobre tot. ⟨si cables = 2⟩
        JUGADORA: Qui? ⟨si cables = 2⟩
        VET: En Marcel. Va treballar vint anys al BCMU. Ara li costa pagar el dentista. ⟨si cables = 2⟩
        VET: Vaig a treballar. ⟨si cables = 2⟩
          ⇒ +llibre_trobat
        JUGADORA: Això és un sí. ⟨si cables = 2⟩
        ⇒ perd cable_alimentacio, +alimentacio_connectada, cables += 1
    • use + cable_alimentacio — SEMPRE
        [SO: mossegada] JUGADORA: Diu! Aquest és el cable de la cafetera! La Vet ens matarà a tots dos!
        NARRADOR: En Diu el desendolla d'una queixalada i se'l mira, satisfet.
        ⇒ +diu_ha_mossegat
    • use + qualsevol objecte — SEMPRE
        JUGADORA: Això no s'endolla enlloc. Ho he comprovat.
    • look — si router_connectat
        JUGADORA: Connectat. Hola, preciós.
    • look — si cables = 0
        JUGADORA: El router nou. Li calen tres cables: la fibra, el de xarxa i el d'alimentació.
    • look — SEMPRE
        JUGADORA: {cables} cables de tres. Ens mirem i ens entenem.
    • use/push/pull/pickUp — si router_connectat
        JUGADORA: Funciona. No el toquis. No el miris gaire.
    • use/push/pull/pickUp — SEMPRE
        JUGADORA: Sense els tres cables, és un pisapapers amb antenes.

FIBRA «presa de la fibra»
    • pickUp/use/pull — si fibra_connectada
        JUGADORA: Ja està connectada. Llum dins d'un fil.
    • pickUp/use/pull — si diu_distret
        JUGADORA: La fibra, al router. Amb cura: és llum.
        [SO: router] JUGADORA: Llums verdes. Internet de debò. ⟨si cables = 2⟩
          ⇒ +router_connectat
        JUGADORA: Ja hi som. El Llibre Major: un servidor de 1984 que porta els comptes de tot el sistema. ⟨si cables = 2⟩
        JUGADORA: I no té internet. Per això ningú no l'ha hackejat mai. Cal entrar-hi en persona. ⟨si cables = 2⟩
        JUGADORA: És en algun lloc de la seu de Ginebra. Però on? ⟨si cables = 2⟩
        VET: Conec algú que ho sap. Beu cafè amb llet al bar i té opinió sobre tot. ⟨si cables = 2⟩
        JUGADORA: Qui? ⟨si cables = 2⟩
        VET: En Marcel. Va treballar vint anys al BCMU. Ara li costa pagar el dentista. ⟨si cables = 2⟩
        VET: Vaig a treballar. ⟨si cables = 2⟩
          ⇒ +llibre_trobat
        JUGADORA: Això és un sí. ⟨si cables = 2⟩
        ⇒ +fibra_connectada, cables += 1
    • pickUp/use/pull — SEMPRE
        [SO: mossegada] JUGADORA: Diu! Això és fibra òptica! És llum, no espaguetis!
        NARRADOR: En Diu el desendolla d'una queixalada i se'l mira, satisfet.
        ⇒ +diu_ha_mossegat
    • look — si fibra_connectada
        JUGADORA: La fibra, connectada. En Diu la mira amb nostàlgia.
    • look — SEMPRE
        JUGADORA: La presa de la fibra, amb el cable enrotllat. En Diu se'l mira com si fos un sopar.

PASSAPLATS «passaplats»
    • open — si NO passaplats_obert
        [SO: passaplats] JUGADORA: Obert. Ja fa olor de cafè.
        ⇒ +passaplats_obert
    • open — SEMPRE
        JUGADORA: Ja és obert. Més obert, seria un forat a la paret.
    • close — si passaplats_obert
        [SO: passaplats] JUGADORA: Tancat. Privacitat.
        ⇒ −passaplats_obert
    • close — SEMPRE
        JUGADORA: Ja és tancat.
    • talkTo/use — si passaplats_obert
        ⇒ diàleg passaplats
    • talkTo/use — SEMPRE
        JUGADORA: Primer l'he d'obrir. Pel vidre, la Vet només em sent si crido, i ja crido prou.
    • use + qualsevol objecte — si NO passaplats_obert
        JUGADORA: Tancat. Primer l'hauria d'obrir.
    • use + qualsevol objecte — SEMPRE
        JUGADORA: La Vet no ho necessita. I jo, potser sí.
    • look — SEMPRE
        JUGADORA: El passaplats de la cuina. Per aquí passen plats, pizzes i ordres de la Vet.

CAIXA «caixa» — hi és si no té caixa_cartro (iri) i no (sacrifici = "caixa")
    • look — si NO cable_xarxa_tret
        JUGADORA: La caixa del router. A dins hi ha el cable de xarxa.
    • look — SEMPRE
        JUGADORA: Buida. Per al gat, és un palau.
    • open/pickUp — si NO cable_xarxa_tret
        JUGADORA: Primer, el cable de xarxa.
        ⇒ rep cable_xarxa, +cable_xarxa_tret
    • pickUp — SEMPRE
        JUGADORA: Me l'emporto. Ho sento, Diu. O no: ja veurem.
        ⇒ rep caixa_cartro
    • open — SEMPRE
        JUGADORA: Ja és oberta. I buida.

DIU «Diu»
    • use + qualsevol objecte — si diu_distret
        JUGADORA: Ja està ocupat. No li prenguis la il·lusió.
    • use + caixa_cartro — SEMPRE
        JUGADORA: Diu. Mira. Una caixa.
        [SO: miol] NARRADOR: En Diu s'hi fica de cap. Ja no existeix res més.
        ⇒ perd caixa_cartro, sacrifici := "caixa", +diu_distret
    • use + auriculars — si NO auricular_pensat
        JUGADORA: Els auriculars? No me'ls trec mai. Mai.
        ⇒ +auricular_pensat
    • use + auriculars — SEMPRE
        [SO: auricular] JUGADORA: ...Està bé. L'esquerre. Adeu, estèreo.
        NARRADOR: En Diu agafa l'auricular i se'l mira com si fos un ratolí car.
        ⇒ sacrifici := "auricular", +diu_distret
    • use + pizza — SEMPRE
        JUGADORA: Diu. La pizza de demà. És teva.
        [SO: miol] NARRADOR: En Diu mira la pizza. Després mira l'Iri. Amb respecte.
        ⇒ perd pizza, sacrifici := "pizza", +diu_distret
    • use + qualsevol objecte — SEMPRE
        JUGADORA: No crec que l'interessi. Li interessen els cables. I la pizza. I les caixes.
    • talkTo — SEMPRE
        ⇒ diàleg diu
    • look — si sacrifici = "caixa"
        JUGADORA: Dins la caixa. Feliç. Els cables ja no existeixen.
    • look — si sacrifici = "auricular"
        JUGADORA: Mossegant el meu auricular. Feliç. Jo, no tant.
    • look — si sacrifici = "pizza"
        JUGADORA: Assegut davant la pizza, solemne. Em mira amb respecte. No sé si m'agrada.
    • look — SEMPRE
        JUGADORA: En Diu. Té els ullals posats en els cables.
    • pickUp — SEMPRE
        JUGADORA: En Diu no s'agafa. En Diu t'agafa a tu.

```

## Sala Suma Zero · `portada`

```
```

## Sala Ginebra · `proleg_ginebra` — cinemàtica

```
EN ENTRAR
    • * — SEMPRE
        NARRADOR: Ginebra. Seu del Banc Central Mundial Unificat.
        NARRADOR: Aquest banc custodia més diners que cent vuitanta països junts.
        EL DIRECTOR: Al BCMU construïm el futur de tothom.
        EL DIRECTOR: ...Una altra? Amb més «tothom»?
        [SO: teclat] NARRADOR: Lluny. Prou lluny. En un pis ple de cables, algú acaba de trobar una porta oberta.
        TÍTOL: Suma Zero
        TÍTOL: Acte 1 · El pla és un desastre
        ⇒ → pis_estudi

```

## Objecte auriculars · `auriculars`

```
• look — si sacrifici = "auricular"
    JUGADORA: Ara només en tinc un. Tot sona en mono. En Diu té l'altra meitat de la meva vida.
• look — si juga iri
    JUGADORA: Els meus auriculars. No me'ls trec mai.
```

## Objecte cable de xarxa · `cable_xarxa`

```
• look — SEMPRE
    JUGADORA: Un cable de xarxa. Blau. Mossegable.
```

## Objecte cable d'alimentació · `cable_alimentacio`

```
• look — si juga iri
    JUGADORA: El cable de la cafetera. La Vet m'odia una mica.
• look — si juga vet
    JUGADORA: El cable de la cafetera. Un sacrifici.
```

## Objecte caixa de cartró · `caixa_cartro`

```
• look — SEMPRE
    JUGADORA: La caixa del router. Per al gat, és un palau.
```

## Objecte pizza · `pizza`

```
• look — si juga iri
    JUGADORA: La pizza de demà. En Diu la mira. Jo també.
• look — si juga vet
    JUGADORA: La pizza de demà. Quatre talls d'esperança.
```

## Objecte entrepà · `entrepa`

```
• look — si juga vet
    JUGADORA: Un entrepà de tonyina. Per si de cas.
• look — si juga iri
    JUGADORA: L'entrepà de la Vet. No preguntis d'on surt.
```

## Objecte clau de casa · `clau_casa`

```
• look — si juga vet
    JUGADORA: La clau de casa. Si la perdo, dormim al replà.
```

## Objecte tap de la cervesera · `tap`

```
• look — si juga vet
    JUGADORA: El clauer d'en Tomàs: un tap de la cervesera. Pesa més que les claus.
```

## Objecte recepta de la llimonada · `recepta`

```
• look — si juga vet
    JUGADORA: La recepta secreta d'en Tomàs: «1. Obrir el pot. 2. Abocar.»
```

## Objecte comandament · `comandament`

```
• look — si juga vet
    JUGADORA: El comandament de la tele. El ceptre d'en Tomàs.
```

## Objecte maletí · `maleti`

```
• look — si juga vet
    JUGADORA: Un maletí de pell. Amb una agenda de 2019 i una llimona. Molt d'auditora.
```

## Objecte ulleres · `ulleres`

```
• look — si juga vet
    JUGADORA: Unes ulleres de pasta. No tenen graduació, però donen autoritat.
```

## Objecte acreditacions · `acreditacions`

```
• look — si juga iri
    JUGADORA: Dues acreditacions de «tècnica de manteniment de caixes fortes». Amb les nostres cares. Més o menys.
```

## Objecte acreditació · `acreditacio`

```
• look — SEMPRE
    JUGADORA: La meva acreditació de tècnica de manteniment de caixes fortes. Diu «caixes fortes». Ho diu ben clar.
```

## Diàleg `diu` amb Diu

```
COMENÇA A: hola

[hola]
    DIU: Miau.
    ↪ menu

[menu]
    ▸ Diu, deixa els cables, sisplau. ⟨si NO diu_distret⟩ → cables
    ▸ Gràcies per deixar-me treballar. ⟨si diu_distret⟩ → gracies
    ▸ Res, res. → adeu · FI

[cables]
    [SO: miol] DIU: Miau.
    JUGADORA: Això és un no.
    ↪ menu

[gracies]
    DIU: ...
    ↪ menu

[adeu]
    DIU: Miau.

```

## Diàleg `empleat` amb Empleat

```
COMENÇA A: hola

[hola]
    EMPLEAT: Objectes perduts. Ha perdut alguna cosa? Tothom perd alguna cosa.
    ↪ menu

[menu]
    ▸ Aquell maletí és meu. ⟨si no té maleti⟩ → maleti
    ▸ Res, gràcies. → adeu · FI

[maleti]
    EMPLEAT: Ah, sí? Què hi ha a dins?
    ▸ Una agenda de 2019 i una llimona. ⟨si maleti_vist⟩ → llimona
    ▸ Papers. Molt importants. → no
    ▸ Ara mateix no ho recordo. → no

[llimona]
    EMPLEAT: ...Exacte. És seu. Signi aquí.
    NARRADOR: La Vet signa amb una lletra que no és la seva.
    ⇒ rep maleti
    ↪ menu

[no]
    EMPLEAT: No.
    ↪ menu

[adeu]
    EMPLEAT: Si perd alguna cosa, ja sap on soc.

```

## Diàleg `marcel` amb Marcel

```
COMENÇA A: hola (si ha vist marcel.intro) · intro

[intro]
    MARCEL: Voleu robar el banc? Tothom ho vol. Ho porteu escrit a la cara.
    JUGADORA: Qui ha parlat de robar?
    MARCEL: Jo vaig construir el sistema que voleu robar. Sabeu què vaig aprendre? Que el diner és confiança. I la confiança la tenen quatre.
    JUGADORA: Marcel, m'estàs posant trist i he de tornar a la feina.
    MARCEL: Jo treballava dotze hores perquè un senyor a Ginebra tingués una casa a tres països.
    MARCEL: Ara tinc un cafè amb llet i soc més feliç. Però no tinc dentista.
    MARCEL: Al BCMU, la propina se la queda el banc.
    MARCEL: Si vols que parli, porta'm tres coses d'en Tomàs sense que se n'adoni: el tap del seu clauer, la recepta secreta de llimonada i el comandament de la tele.
    MARCEL: Si robes al teu cap per mi, et fiaré.
    ⇒ +prova_marcel
    ↪ menu

[hola]
    MARCEL: Què, ja ho tens? ⟨si donats < 3⟩
    MARCEL: Pregunta, pregunta. ⟨si donats ≥ 3⟩
    ↪ menu

[menu]
    ▸ Què em falta? ⟨si donats < 3⟩ → falten
    ▸ On és el servidor antic? ⟨una vegada, si donats ≥ 3⟩ → servidor
    ▸ I com s'hi entra? ⟨una vegada, si donats ≥ 3⟩ → clau
    ▸ Com es passen coses d'un pis a l'altre, allà dins? ⟨una vegada, si donats ≥ 3⟩ → tub
    ▸ I com arribem a Ginebra, si no tenim ni per pizzes? ⟨una vegada, si donats ≥ 3⟩ → vol
    ▸ I el Cap de Seguretat, com és? ⟨una vegada, si donats ≥ 3 i marcel_clau⟩ → ballester
    ▸ Hi ha algú més pel mig, al tercer pis? ⟨una vegada, si donats ≥ 3 i marcel_servidor⟩ → neta
    ▸ Gràcies, Marcel. Te'n dec una. ⟨si (marcel_servidor i marcel_clau i marcel_tub i marcel_vol) i NO marcel_fet⟩ → gracies · FI
    ▸ Ja tornaré. → adeu · FI

[falten]
    MARCEL: El tap del clauer d'en Tomàs. ⟨si NO marcel_tap⟩
    MARCEL: La recepta de la llimonada. ⟨si NO marcel_recepta⟩
    MARCEL: El comandament de la tele. ⟨si NO marcel_comandament⟩
    ↪ menu

[servidor]
    MARCEL: A la sala d'escombraries del tercer pis. El van posar allà quan el van jubilar.
    MARCEL: Però encara porta tots els comptes. Ningú no s'ha atrevit a desendollar-lo.
    ⇒ +marcel_servidor
    ↪ menu

[clau]
    MARCEL: Per fer-lo anar, cal una clau. I la clau la porta el Cap de Seguretat al coll. Literalment. És un collaret.
    JUGADORA: Perfecte. M'agraden els reptes estúpids.
    ⇒ +marcel_clau
    ↪ menu

[tub]
    MARCEL: Amb el tub pneumàtic. El vaig modernitzar jo. Cada planta té una estació.
    MARCEL: Hi cap una clau. Hi cap un entrepà, si no te l'estimes gaire.
    ⇒ +marcel_tub
    ↪ menu

[vol]
    MARCEL: El BCMU té un vol propi cada dimarts al matí per als tècnics de manteniment de caixes fortes.
    MARCEL: Ningú no comprova res. Qui vol robar una caixa forta?
    ⇒ +marcel_vol
    ↪ menu

[ballester]
    MARCEL: En Ballester. Trenta anys a la casa. Miràvem La Comissària Bassols cada dilluns, a la garita.
    MARCEL: El seu capítol preferit és «El violí mut». El que odia és «La vídua del Liceu»: diu que és inversemblant.
    JUGADORA: Tothom té un capítol que odia.
    ⇒ +marcel_ballester
    ↪ menu

[neta]
    MARCEL: El robot de neteja. NETA-3. El vaig programar jo.
    MARCEL: Si li dius «NETA, descansa», s'atura. Mai ningú no li ho ha dit.
    ⇒ +marcel_neta
    ↪ menu

[gracies]
    MARCEL: Me'n deus un dentista.
    MARCEL: I ves amb compte. El banc no crida mai. Només somriu.
    ⇒ +marcel_fet

[adeu]
    MARCEL: Aquí seré. Sempre soc aquí.

```

## Diàleg `passaplats` amb Vet

```
COMENÇA A: hola

[hola]
    VET: Què vols, ara?
    ↪ menu

[menu]
    ▸ Vet, em cal el cable de la cafetera. ⟨si NO cable_demanat⟩ → cable
    ▸ Vet, passa'm la pizza de demà. ⟨si diu_ha_mossegat i NO diu_distret i NO pizza_demanada⟩ → pizza
    ▸ Qui és aquest Marcel? ⟨una vegada, si llibre_trobat i NO vet_marxa⟩ → marcel
    ▸ Res, res. → adeu · FI

[cable]
    VET: El de la cafetera? Sense cafè no hi ha pla.
    VET: ...Està bé. Ara te'l passo.
    ⇒ +cable_demanat

[pizza]
    VET: La de demà? Per a què la vols?
    JUGADORA: Per al gat.
    VET: ...Això és un sacrilegi. Ara te la passo.
    ⇒ +pizza_demanada

[marcel]
    VET: Un client del bar. Enginyer. El van «reestructurar».
    VET: Ara beu cafè amb llet i té opinió sobre tot. Sobretot sobre els bancs.
    ↪ menu

[adeu]
    VET: Doncs no em distreguis, que faig tard.

```

## Diàleg `soler` amb Soler

```
COMENÇA A: xiulet (si alarma_porta) · buscant (si soler_distret) · hola

[hola]
    SOLER: Bon dia. Si busca la cua, és allà.
    ↪ menu

[menu]
    ▸ He perdut el meu fill! ⟨si NO aeroport_fet⟩ → fill
    ▸ Res, gràcies. → adeu · FI

[fill]
    TÍTOL: Ara necessites les dues.
    SOLER: Un nen perdut? Tranquil·la, senyora. El trobarem.
    SOLER: Com es diu?
    ⇒ +sync_aeroport, +soler_distret, cigarreta := 12
    ↪ nom

[nom]
    ▸ Jordi. → edat
    ▸ Jordi Bartomeu Puigdollers i Reixac, com el seu avi, que era notari, i el notari de l'avi, que també era notari... → edat
        ⇒ cigarreta −= 1

[edat]
    SOLER: Quants anys té?
    ▸ Set. → roba
    ▸ Set i mig. Bé, set i tres quarts, si comptem el temps que va passar a la incubadora, que va ser molt, perquè... → roba
        ⇒ cigarreta −= 1

[roba]
    SOLER: Com va vestit?
    ▸ Samarreta vermella. → busca
    ▸ Samarreta vermella amb un dinosaure que fa de dentista, perquè ell vol ser dentista, i el dinosaure... → busca
        ⇒ cigarreta −= 1

[busca]
    SOLER: Samarreta vermella, set anys. El busco. No es mogui.
    NARRADOR: En Soler deixa la porta de personal i se'n va a mirar darrere de cada columna.

[buscant]
    SOLER: Encara no l'he trobat, senyora. Però el trobarem.

[xiulet]
    SOLER: Què ha estat això? Ha xiulat alguna cosa allà darrere...
    ▸ BUAAAAA! EL MEU FILL! → plorat
        ⇒ −alarma_porta
    ▸ Res, res. Jo no he sentit res. → res

[plorat]
    [SO: plor] NARRADOR: La Vet plora com una sirena d'ambulància.
    SOLER: Ja, ja, senyora, no pateixi! El trobarem!

[res]
    SOLER: Doncs a mi m'ha semblat... Vaig a mirar.

[adeu]
    SOLER: Bon viatge.

```

## Diàleg `tomas` amb Tomàs

```
COMENÇA A: hola

[hola]
    TOMÀS: Què vols? Estàs treballant, eh. Que consti.
    ↪ menu

[menu]
    ▸ Un cafè amb llet per a en Marcel. ⟨si prova_marcel i NO tap_barra i no té tap i NO marcel_tap i NO tap_tornat⟩ → cafe
    ▸ Un altre cafè per a en Marcel? ⟨si té tap o marcel_tap o tap_tornat⟩ → cafe2
    ▸ Em deixes el comandament de la tele? ⟨si prova_marcel i NO sap_dona⟩ → comandament
    ▸ Quina és la contrasenya de la wifi? ⟨una vegada, si cal_contrasenya i NO contrasenya_llegida⟩ → wifi
    ▸ Res, Tomàs. → adeu · FI

[cafe]
    TOMÀS: Per a en Marcel. Que no paga mai.
    TOMÀS: Està bé. Però el pagues tu.
    [SO: vaporitzador] NARRADOR: En Tomàs es treu el clauer, el deixa a la barra i es posa a escumar la llet com si li anés la vida.
    ⇒ +tap_barra
    ↪ menu

[cafe2]
    TOMÀS: Un altre? En Marcel ja va prou excitat.
    ↪ menu

[comandament]
    TOMÀS: El comandament? Hi ha partit.
    TOMÀS: Només el deixaria per una cosa: una trucada de la meva dona.
    JUGADORA: ...La teva dona.
    TOMÀS: La meva dona. Que és de viatge. Des de fa vint anys.
    ⇒ +sap_dona
    ↪ menu

[wifi]
    TOMÀS: Està al rètol. Sempre ho ha estat. Llegeix, que per això el vaig penjar.
    ↪ menu

[adeu]
    TOMÀS: Doncs a treballar.

```

## Diàleg `trucada` amb Iri

```
COMENÇA A: hola

[hola]
    [SO: telefon_bar] JUGADORA: Iri? Soc jo.
    IRI: Digues.
    ↪ menu

[menu]
    ▸ Saps obrir un pany intel·ligent? ⟨si sap_pany i NO cal_contrasenya⟩ → pany
    ▸ La contrasenya és «exceptosinopaga». Tot junt. ⟨si contrasenya_llegida i NO contrasenya_dita⟩ → contrasenya
    ▸ Necessito que truquis al bar i facis de dona d'en Tomàs. ⟨si sap_dona i NO trucada_demanada⟩ → trucada
    ▸ Ho tinc tot. Apunta. ⟨si marcel_fet i NO resum_fet⟩ → resum
    ▸ I el robot de neteja: si li dius «NETA, descansa», s'atura. ⟨si resum_fet i marcel_neta i NO iri_sap_neta⟩ → robot
    ▸ Res, ja et trucaré. → adeu · FI

[pany]
    IRI: Si és dels de 19,99 €, amb l'aplicació. Necessito la contrasenya d'administrador.
    IRI: Que segur que és la mateixa que la de la wifi. Sempre ho és.
    ⇒ +cal_contrasenya
    ↪ menu

[contrasenya]
    IRI: Esclar que sí. Dona'm un minut. Ho faig des de l'ordinador.
    ⇒ +contrasenya_dita
    ↪ menu

[trucada]
    IRI: Jo? Parlar? Amb una persona?
    IRI: ...Amb una veu sintètica. D'acord. Ho faig des de l'ordinador.
    ⇒ +trucada_demanada
    ↪ menu

[resum]
    JUGADORA: El servidor és a la sala d'escombraries del tercer pis.
    JUGADORA: La clau, la porta el Cap de Seguretat penjada al coll.
    JUGADORA: A dins hi ha un tub pneumàtic a cada planta. Hi cap una clau.
    JUGADORA: I dimarts hi ha un vol del BCMU per als tècnics de caixes fortes. Ningú no comprova res.
    JUGADORA: I una cosa d'un tal Ballester i una sèrie. Això és cosa meva. ⟨si marcel_ballester⟩
    IRI: Un vol de tècnics. Si soc a la llista, soc tècnica.
    IRI: Plega i ves a casa a dormir. Demà a les cinc, a l'aeroport.
    ⇒ +resum_fet
    ↪ menu

[robot]
    IRI: Una contrasenya per a un robot. M'encanta.
    ⇒ +iri_sap_neta
    ↪ menu

[adeu]
    IRI: Vale. Ah, i no et deixis cap cable a la cafetera.

```

## Pistes

```
iri_caixa — quan juga iri i NO cable_xarxa_tret · fins que cable_xarxa_tret
    1. Calen tres cables. Un deu ser a la caixa del router.
    2. Si obro la caixa del router, hi trobaré el cable de xarxa.
    3. Obro la caixa del router i n'agafo el cable de xarxa.
iri_cable_cafetera — quan juga iri i NO cable_demanat i NO alimentacio_connectada · fins que cable_demanat
    1. El cable d'alimentació... on n'hi ha un, en aquesta casa?
    2. La cafetera de la cuina en té un. La Vet és a la cuina.
    3. Obro el passaplats i hi demano a la Vet el cable de la cafetera.
iri_espera_cable — quan juga iri i cable_demanat i no té cable_alimentacio (iri) i NO alimentacio_connectada · fins que té cable_alimentacio (iri) o alimentacio_connectada
    1. La Vet té el cable. Ara li toca a ella.
    2. Canvio a la Vet: ella pot treure el cable de la cafetera.
    3. Canvio a la Vet, agafa el cable de la cafetera i me'l passa pel passaplats.
iri_diu — quan juga iri i diu_ha_mossegat i NO diu_distret · fins que diu_distret
    1. Mentre en Diu vigili els cables, no en connectaré cap. Cal distreure'l.
    2. Als gats els agraden les caixes. I les coses cares. I la pizza.
    3. Li dono a en Diu la caixa del router. O un auricular. O la pizza de demà, que té la Vet.
iri_connectar — quan juga iri i diu_distret i NO router_connectat · fins que router_connectat
    1. En Diu està distret. Ara és el moment dels cables.
    2. Connecto al router la fibra, el cable de xarxa i el d'alimentació.
    3. Faig servir cada cable amb el router, i la fibra directament.
iri_mossegar — quan juga iri i NO diu_ha_mossegat i NO diu_distret i NO router_connectat · fins que diu_ha_mossegat o diu_distret
    1. El router necessita els seus cables.
    2. La fibra penja de la paret, al costat del router.
    3. Connecto la fibra al router.
iri_ara_vet — quan juga iri i llibre_trobat i NO vet_marxa · fins que vet_marxa
    1. La Vet coneix algú que sap on és el servidor.
    2. Ara li toca a la Vet: ha d'anar al bar a parlar amb en Marcel.
    3. Canvio a la Vet, i que surti per la porta de la cuina cap al bar.
vet_espera — quan juga vet i NO cable_demanat i NO llibre_trobat · fins que cable_demanat o llibre_trobat
    1. L'Iri està connectant coses. Ja em demanarà alguna cosa.
    2. Si l'Iri necessita alguna cosa de la cuina, me la demanarà pel passaplats.
    3. Canvio a l'Iri: ella té feina amb el router.
vet_cable — quan juga vet i cable_demanat i no té cable_alimentacio (iri) i NO alimentacio_connectada · fins que té cable_alimentacio (iri) o alimentacio_connectada
    1. L'Iri vol el cable de la cafetera. Adeu, cafè.
    2. Agafo el cable de la cafetera.
    3. Agafo el cable de la cafetera i el faig servir amb el passaplats (obert).
vet_pizza — quan juga vet i pizza_demanada i no té pizza (iri) i no (sacrifici = "pizza") · fins que té pizza (iri) o sacrifici = "pizza" o diu_distret
    1. L'Iri vol la pizza de demà. Pel gat. Quin món.
    2. La pizza és a la nevera.
    3. Obro la nevera, agafo la pizza i la passo pel passaplats (obert).
vet_marxar — quan juga vet i llibre_trobat i NO vet_marxa · fins que vet_marxa
    1. He d'anar al bar. En Marcel sabrà on és el servidor.
    2. La porta del pis és a la cuina.
    3. Surto per la porta de la cuina. (I, si vull, abans em faig un entrepà.)
iri_bar — quan juga iri i vet_marxa i NO bar_fet · fins que bar_fet
    1. La Vet és al bar. Si em necessita, trucarà.
    2. Mentre la Vet parla amb en Marcel, potser li cal ajuda des de l'ordinador.
    3. Canvio a la Vet i miro com va al bar.
iri_pany — quan juga iri i contrasenya_dita i NO calaix_obert · fins que calaix_obert
    1. La Vet m'ha donat la contrasenya del bar.
    2. Amb la contrasenya de la wifi puc obrir el pany des de l'ordinador.
    3. Faig servir els ordinadors.
iri_trucar — quan juga iri i trucada_demanada i NO trucada_feta · fins que trucada_feta
    1. La Vet vol que truqui al bar i faci de dona d'en Tomàs. Jo.
    2. Amb una veu sintètica, des de l'ordinador, ho puc fer.
    3. Faig servir els ordinadors per trucar al bar.
vet_marcel — quan juga vet i vet_marxa i NO prova_marcel · fins que prova_marcel
    1. He vingut a parlar amb en Marcel.
    2. En Marcel és a la barra, amb el seu cafè amb llet.
    3. Parlo amb en Marcel.
vet_tap — quan juga vet i prova_marcel i no té tap i NO marcel_tap i NO tap_tornat · fins que té tap o marcel_tap
    1. El tap del clauer d'en Tomàs. El porta penjat al cinturó.
    2. En Tomàs es treu el clauer quan fa cafè, perquè li molesta.
    3. Demano a en Tomàs un cafè amb llet per a en Marcel i agafo el clauer de la barra.
vet_recepta — quan juga vet i prova_marcel i no té recepta i NO marcel_recepta · fins que té recepta o marcel_recepta
    1. La recepta de la llimonada és al calaix del rebost.
    2. El calaix té un pany amb aplicació. L'Iri el podria obrir des de casa, amb la contrasenya de la wifi.
    3. Miro el calaix, truco a l'Iri, llegeixo el rètol, li dic la contrasenya, i quan l'hagi obert agafo la recepta.
vet_comandament — quan juga vet i prova_marcel i no té comandament i NO marcel_comandament · fins que té comandament o marcel_comandament
    1. En Tomàs no deixa el comandament per res del món. Per res?
    2. Només el deixaria per una trucada de la seva dona. Que no existeix. L'Iri podria fer de dona.
    3. Demano el comandament a en Tomàs, truco a l'Iri perquè truqui al bar, i agafo el comandament de la barra.
vet_donar — quan juga vet i (té tap o té recepta o té comandament) i donats < 3 · fins que donats ≥ 3
    1. En Marcel vol les tres coses.
    2. Li he de donar el que tinc.
    3. Dono a en Marcel el tap, la recepta i el comandament.
vet_preguntar — quan juga vet i donats ≥ 3 i NO marcel_fet · fins que marcel_fet
    1. En Marcel ja em fia. Ara, preguntes.
    2. Vull saber on és el servidor, com s'hi entra, com es passen coses i com arribem a Ginebra.
    3. Parlo amb en Marcel i li pregunto tot.
vet_resum — quan juga vet i marcel_fet i NO resum_fet · fins que resum_fet
    1. L'Iri ha de saber el que m'ha dit en Marcel.
    2. El telèfon de paret.
    3. Truco a l'Iri des del telèfon i li ho explico tot.
vet_plegar — quan juga vet i resum_fet i NO bar_fet · fins que bar_fet
    1. Ja ho tenim. Hora de plegar.
    2. (I potser tornar-li el tap a en Tomàs.)
    3. Surto per la porta del bar.
vet_preparar — quan juga vet i bar_fet i NO sync_aeroport i NO aeroport_fet i (no té maleti o no té ulleres) · fins que sync_aeroport o aeroport_fet o (té maleti i té ulleres)
    1. A Ginebra hauré de semblar algú important. Una auditora, per exemple.
    2. Una auditora porta maletí i ulleres. A objectes perduts hi ha un maletí; a la cafeteria, unes ulleres.
    3. Miro el maletí i el reclamo a objectes perduts. Agafo les ulleres de la cafeteria.
vet_distreure — quan juga vet i bar_fet i NO sync_aeroport i NO aeroport_fet · fins que sync_aeroport o aeroport_fet
    1. En Soler vigila la porta de personal. Necessito que la deixi.
    2. Un guàrdia de cor tendre no deixaria sola una mare desesperada.
    3. Parlo amb en Soler: he perdut el meu fill.
vet_codi — quan juga vet i soler_distret i NO codi_porta_llegit · fins que codi_porta_llegit
    1. La porta de personal té un codi. Els codis sempre són a prop.
    2. Ara que en Soler no hi és, puc mirar el taulell de facturació.
    3. Miro el taulell: sota hi ha el codi.
vet_plorar — quan juga vet i alarma_porta · fins que NO alarma_porta
    1. La porta ha xiulat. En Soler ho ha sentit.
    2. Cal tapar-ho amb un drama més gran.
    3. Parlo amb en Soler i ploro més fort.
vet_trobat — quan juga vet i iri_fora i NO aeroport_fet · fins que aeroport_fet
    1. L'Iri ja és fora. Cal acabar la funció.
    2. Un nen perdut s'acaba quan es troba.
    3. Assenyalo el nen de la samarreta vermella: l'he trobat!
vet_espera_iri — quan juga vet i codi_porta_llegit i soler_distret i NO iri_fora · fins que iri_fora
    1. L'Iri ja té el codi. Ara li toca a ella.
    2. Canvio a l'Iri.
    3. Canvio a l'Iri: que entri, faci les acreditacions i surti.
iri_aeroport_espera — quan juga iri i bar_fet i NO soler_distret i NO aeroport_fet · fins que soler_distret o aeroport_fet
    1. Amb en Soler aquí davant no puc fer res.
    2. La Vet ha de fer que en Soler se'n vagi.
    3. Canvio a la Vet: que distregui en Soler.
iri_codi — quan juga iri i soler_distret i NO porta_oberta · fins que porta_oberta
    1. Necessito el codi de la porta.
    2. La Vet és al taulell. Potser el veu.
    3. Si la Vet ja m'ha dit el codi, faig servir el teclat. Si no, canvio a la Vet perquè el busqui.
iri_imprimir — quan juga iri i soler_distret i porta_oberta i no té acreditacions i NO iri_fora · fins que té acreditacions o iri_fora
    1. Som a dins. Ara, la llista i les acreditacions.
    2. El terminal per a la llista; la impressora, per imprimir. És lenta.
    3. Faig servir el terminal, després la impressora, i agafo les acreditacions.
iri_sortir — quan juga iri i té acreditacions i NO iri_fora · fins que iri_fora
    1. Ja les tinc. Fora d'aquí.
    2. La porta de l'oficina.
    3. Surto per la porta (amb en Soler distret).
iri_fora — quan juga iri i iri_fora i NO aeroport_fet · fins que aeroport_fet
    1. Ja soc fora. Ara, que la Vet acabi la funció.
    2. Canvio a la Vet.
    3. Canvio a la Vet: que trobi «el seu fill».
```

## Finals

```
continuara «Continuarà» — quan acte1_fet
    Fins aquí, l'Acte 1 de Suma Zero. L'Iri i la Vet volen cap a Ginebra.
```
