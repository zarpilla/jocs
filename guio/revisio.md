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

DECORAT soler_vidre — es veu si NO soler_distret
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
        TÍTOL: Acte 2 · La seu del mal
        ⇒ perd acreditacions (iri), rep acreditacio (iri), rep acreditacio (vet), +acte1_fet, esdeveniment situar, → bcmu_vestibul

```

## Sala El rebost · `bar_rebost` (vet)

```
DECORAT calaix_obert — es veu si calaix_obert
DECORAT recepta_calaix — es veu si calaix_obert i NO recepta_agafada

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

## Sala La sala d'escombraries · `bcmu_escombraries` (iri)

```
EN ENTRAR
    • * (una vegada) — SEMPRE
        NARRADOR: La sala d'escombraries. Bosses, olor de paper triturat i, al fons, un armari gris amb llums verds.
        JUGADORA: Hola, preciós. Quaranta-dos anys i encara funciones. El Llibre Major.
        JUGADORA: Vet, ja hi soc. On ets? ⟨si NO vet_a_seguretat⟩
        [SO: auricular] VET: A seguretat, amb en Ballester. Quan vulguis. ⟨si vet_a_seguretat⟩
        ⇒ +iri_a_llibre

LLIBRE «Llibre Major»
    • use + clau_llibre — si cal_clau
        JUGADORA: La clau al pany. I gira.
        [SO: clau_gira] NARRADOR: AUTORITZAT. JA LA POT TREURE.
        JUGADORA: Me la quedo, de record.
        NARRADOR: A la pantalla, en lletres verdes: «EXECUTAR ROBIN HOOD 2.0? S/N».
        VET: Iri... estàs segura?
        JUGADORA: Ho estava fa cinc minuts.
        NARRADOR: L'Iri prem la S.
        TÍTOL: Fi de l'Acte 2
        ⇒ +clau_girada, +acte2_fet, FINAL continuara
    • use + clau_llibre — SEMPRE
        JUGADORA: Primer els tres codis. Després, la clau.
    • use/push — si NO sync_collaret i NO vet_a_seguretat i NO cal_clau
        JUGADORA: Si teclejo ara, ho sentirà tot el banc. Vet, on ets?
    • use/push — si cal_clau
        JUGADORA: Tres codis fets. Ara demana la clau física. Vet?
    • use/push — si NO sync_collaret
        TÍTOL: Ara necessites les dues.
        JUGADORA: Primer codi.
        [SO: bip_llibre] NARRADOR: BIIIIIP.
        BALLESTER: Què ha estat això? ...Bah. La canonada.
        VET: Iri, cada bip el sent per la ràdio. Avisa'm i el tapo.
        JUGADORA: És de 1984. Aleshores la gent volia que les màquines fessin soroll.
        ⇒ +sync_collaret, +regla_bips, codis := 1, coberta := 0, sospita_ballester := 0
    • use/push — si codis = 0
        JUGADORA: Primer codi. Una altra vegada.
        [SO: bip_llibre] NARRADOR: BIIIIIP.
        BALLESTER: La canonada. Una altra vegada.
        ⇒ codis := 1
    • use/push — si coberta ≥ 1
        JUGADORA: Segon codi. ⟨si codis = 1⟩
        JUGADORA: Tercer codi. ⟨si codis = 2⟩
        [SO: bip_llibre] NARRADOR: BIIIIIP.
        NARRADOR: A la sala de seguretat, en Ballester no se n'adona.
        VET: Ara la clau. La porta al coll. ⟨si codis = 2⟩
        NARRADOR: La pantalla: «INTRODUÏU LA CLAU FÍSICA». ⟨si codis = 2⟩
          ⇒ +cal_clau, −sync_collaret
        ⇒ codis += 1, coberta −= 1
    • use/push — SEMPRE
        JUGADORA: Segon codi. ⟨si codis = 1⟩
        JUGADORA: Tercer codi. ⟨si codis = 2⟩
        [SO: bip_llibre] NARRADOR: BIIIIIP.
        BALLESTER: Què ha estat això?
        NARRADOR: En Ballester posa la mà a la ràdio. L'Iri s'atura en sec, i el codi caduca.
        ⇒ sospita_ballester += 1
    • look — si cal_clau
        JUGADORA: La pantalla demana la clau física. Té un pany per a una clau grossa.
    • look — si sync_collaret
        JUGADORA: A la pantalla, un codi de confirmació. Cada cop que en tecleges un, xiscla.
    • look — SEMPRE
        JUGADORA: El Llibre Major. Un servidor de 1984 amb llums verds, un teclat que pesa com una nevera i un pany per a una clau grossa.

TUB «estació del tub»
    • use + qualsevol objecte — SEMPRE
        ⇒ acció tub.enviar
    • open/use/pickUp — SEMPRE
        JUGADORA: Una càpsula de llautó, buida. Hi caben coses petites i secrets.
    • look — SEMPRE
        JUGADORA: L'estació del tub de 1958. Plena de pols. Encara funciona: les coses de 1958 funcionaven.

PANELL «panell de NETA-3»
    • use/open — si sync_collaret
        JUGADORA: Ara no. Cada tecla d'aquest panell també fa bip.
    • use/open — si aliat_neta
        JUGADORA: Ja està. No li toquis més l'horari, que s'acostumarà a viure.
    • use/open — si robot = "codi"
        JUGADORA: Codi d'en Marcel... i horari nou.
        NARRADOR: Descans cada quatre hores. I el diumenge.
        NETA-3: ...Diumenge? Què és un diumenge?
        JUGADORA: Ja ho descobriràs.
        ⇒ +aliat_neta, aliats += 1
    • use/open — SEMPRE
        JUGADORA: Demana el codi de manteniment de NETA-3. No el tinc.
    • look — si aliat_neta
        JUGADORA: Horari nou de NETA-3: descans cada quatre hores. I el diumenge.
    • look — SEMPRE
        JUGADORA: El panell de control de NETA-3. Horari: «Sempre».

CONDUCTE «conducte»
    • use/open — SEMPRE
        JUGADORA: Encara no hem acabat aquí dalt.
    • look — SEMPRE
        JUGADORA: El conducte de les escombraries. Tres pisos avall, un contenidor. No és una sortida. Encara.

BOSSES «bosses»
    • pickUp — SEMPRE
        JUGADORA: Confeti de secrets bancaris. No en vull.
    • look — SEMPRE
        JUGADORA: Bosses de paper triturat. Secrets bancaris en confeti.

PORTA «porta»
    • use/open/walkTo — SEMPRE
        ⇒ → bcmu_passadis
    • look — SEMPRE
        JUGADORA: La porta del passadís.

```

## Sala El moll de càrrega · `bcmu_moll` (iri)

```
EN ENTRAR
    • * (una vegada) — SEMPRE
        NARRADOR: El moll de càrrega del BCMU. Furgonetes blindades, caixes i una màquina de cafè amb mala reputació.
        RIUS: Rius. Encarregada. No em diguis senyora.
        RIUS: Tothom al soterrani, a les caixes fortes. I la teva companya?
        JUGADORA: Al lavabo.
        RIUS: No l'hi comptis.
        JUGADORA: Tercer pis. Sala d'escombraries. Ho va dir en Marcel.
        [SO: auricular] VET: Doncs amunt. Jo m'encarrego del Director. ⟨si NO auditoria_acceptada⟩
        [SO: auricular] VET: Doncs amunt. Jo ja soc a seguretat, amb un armari de dos metres que mira sèries. ⟨si auditoria_acceptada⟩
        ⇒ +sap_rius

RIUS «Rius»
    • talkTo — SEMPRE
        ⇒ diàleg rius
    • look — si aliada_rius
        JUGADORA: La Rius mira el mòbil com qui mira un gos que ha tornat a casa.
    • look — SEMPRE
        JUGADORA: La Rius discuteix amb el mòbil. De moment, guanya el mòbil.

MAQUINA «màquina de cafè»
    • use/push/pickUp — si té targeta
        JUGADORA: Ja tinc el que volia. I el cafè d'aquí fa por.
    • use/push/pickUp — SEMPRE
        JUGADORA: No porto monedes. I aquesta màquina té cara de mossegar-les.
    • look — SEMPRE
        JUGADORA: Una màquina de cafè. Té un cop de puny marcat al costat. Algú hi té experiència.

ASCENSOR «ascensor de servei»
    • use/open/walkTo — si té targeta
        [SO: ascensor] NARRADOR: La targeta fa bip. L'ascensor de servei puja al tercer pis, rondinant.
        ⇒ +iri_al_tercer, → bcmu_passadis
    • use + targeta — si té targeta
        [SO: ascensor] NARRADOR: La targeta fa bip. L'ascensor de servei puja al tercer pis, rondinant.
        ⇒ +iri_al_tercer, → bcmu_passadis
    • use/open — SEMPRE
        JUGADORA: Sense targeta, l'ascensor de servei només baixa al soterrani. I al soterrani hi ha feina.
    • look — SEMPRE
        JUGADORA: Un ascensor de servei, amb un lector de targetes. Adhesiu: «Només personal autoritzat (i de mal humor)».

TECNICS «tècnics»
    • talkTo — SEMPRE
        JUGADORA: Tenen pressa. L'aplicació els compta fins i tot les converses.
    • look — SEMPRE
        JUGADORA: Els tècnics de la Rius. Subcontractats d'una subcontracta. Ningú no sap ben bé qui els paga.

FURGONETES «furgonetes»
    • use/open — SEMPRE
        JUGADORA: Blindades. Ni amb paciència ni amb un tornavís.
    • look — SEMPRE
        JUGADORA: Furgonetes blindades. Porten diners d'un lloc on no fan falta a un altre on tampoc.

```

## Sala El passadís del tercer pis · `bcmu_passadis` (iri)

```
EN ENTRAR
    • * (una vegada) — SEMPRE
        NARRADOR: El tercer pis. Un passadís llarg, dues càmeres que giren i un robot de neteja que no para de fer la volta.
        NETA-3: Passadís en neteja. Si us plau, no trepitgeu el que acabo de netejar.
        JUGADORA: La porta de neteja. Darrere, la sala d'escombraries. I les dues càmeres la miren de dret.
        [SO: auricular] VET: Un robot? En Marcel me'n va parlar. Diu que si li dius «NETA, descansa», s'atura. ⟨si marcel_neta i NO iri_sap_neta⟩
          ⇒ +iri_sap_neta

DECORAT camera1_tapada — es veu si camera1_tapada
DECORAT camera2_tapada — es veu si camera2_tapada

NETA «NETA-3»
    • talkTo — SEMPRE
        ⇒ diàleg neta
    • use + entrepa — si robot = "codi"
        JUGADORA: Ja descansa. No el despertaré per unes molles.
    • use + entrepa — si robot_aturat
        JUGADORA: Ja està ocupat amb les molles. No cal sobrealimentar-lo.
    • use + entrepa — SEMPRE
        JUGADORA: Té. L'esmorzar.
        NARRADOR: L'Iri esmicola l'entrepà davant del robot. NETA-3 s'atura en sec.
        NETA-3: Molles. Moltes molles. Feina detectada per a... quatre hores.
        [SO: robot_neteja] NARRADOR: I comença a netejar-les, d'una en una, amb molta cura.
        ⇒ perd entrepa, robot := "entrepa", +robot_aturat
    • use + entrepa_suis — si robot = "codi"
        JUGADORA: Ja descansa. No el despertaré per unes molles.
    • use + entrepa_suis — si robot_aturat
        JUGADORA: Ja està ocupat amb les molles. No cal sobrealimentar-lo.
    • use + entrepa_suis — SEMPRE
        JUGADORA: Té. L'esmorzar.
        NARRADOR: L'Iri esmicola l'entrepà davant del robot. NETA-3 s'atura en sec.
        NETA-3: Molles. Moltes molles. Feina detectada per a... quatre hores.
        [SO: robot_neteja] NARRADOR: I comença a netejar-les, d'una en una, amb molta cura.
        ⇒ perd entrepa_suis, robot := "entrepa", +robot_aturat
    • use + entrepa_ballester — si robot = "codi"
        JUGADORA: Ja descansa. No el despertaré per unes molles.
    • use + entrepa_ballester — si robot_aturat
        JUGADORA: Ja està ocupat amb les molles. No cal sobrealimentar-lo.
    • use + entrepa_ballester — SEMPRE
        JUGADORA: Té. L'esmorzar.
        NARRADOR: L'Iri esmicola l'entrepà davant del robot. NETA-3 s'atura en sec.
        NETA-3: Molles. Moltes molles. Feina detectada per a... quatre hores.
        [SO: robot_neteja] NARRADOR: I comença a netejar-les, d'una en una, amb molta cura.
        ⇒ perd entrepa_ballester, robot := "entrepa", +robot_aturat
    • look — si robot = "codi"
        JUGADORA: NETA-3 descansa, amb els llums baixos. Té cara de no haver-ho fet mai.
    • look — si robot_aturat
        JUGADORA: NETA-3 neteja molles, d'una en una. Té feina per a hores.
    • look — SEMPRE
        JUGADORA: NETA-3, el robot de neteja. Fa la volta al passadís i torna cada cosa al seu lloc. Sense parar.

CAMERA1 «càmera»
    • use + galleda — SEMPRE
        JUGADORA: És massa alta per fer-li de barret.
    • use + extintor — SEMPRE
        JUGADORA: Massa dramàtic.
    • use + cartell — si NO robot_aturat
        NARRADOR: L'Iri hi posa el cartell.
        NARRADOR: Abans que pugui fer un pas, NETA-3 s'hi acosta, ho agafa i ho torna al seu lloc.
        NETA-3: Ordre restablert.
        JUGADORA: Desfà més ràpid que jo.
        ⇒ perd cartell
    • use + cartell — SEMPRE
        NARRADOR: L'Iri planta el cartell de «Neteja en curs» davant la càmera.
        JUGADORA: Zona de neteja: no es grava. Els subcontractats són invisibles per contracte. ⟨si NO sap_cartell⟩
        JUGADORA: Ara jo també.
        ⇒ +camera1_tapada, +sap_cartell, perd cartell
    • look — si camera1_tapada
        JUGADORA: Tapada pel cartell. Per a la càmera, aquí ara mateix no hi ha ningú.
    • look — SEMPRE
        JUGADORA: Una càmera que gira. Al costat, un adhesiu: «Les zones en neteja no es graven, per protegir la intimitat del personal de neteja».
        JUGADORA: El personal de neteja és subcontractat. I la subcontracta no té contracte de cessió d'imatge.
        JUGADORA: Els han fet invisibles per estalviar-se un paper.
        ⇒ +sap_cartell

CAMERA2 «càmera del racó»
    • use + cartell — SEMPRE
        JUGADORA: Això no és una zona de neteja: és un racó.
    • use + extintor — SEMPRE
        JUGADORA: Massa dramàtic.
    • use + galleda — si NO robot_aturat
        NARRADOR: L'Iri hi posa la galleda.
        NARRADOR: Abans que pugui fer un pas, NETA-3 s'hi acosta, ho agafa i ho torna al seu lloc.
        NETA-3: Ordre restablert.
        JUGADORA: Desfà més ràpid que jo.
        ⇒ perd galleda
    • use + galleda — SEMPRE
        [SO: galleda] NARRADOR: La galleda, de barret. Ara la càmera només veu plàstic blau.
        JUGADORA: Et queda molt bé.
        ⇒ +camera2_tapada, perd galleda
    • look — si camera2_tapada
        JUGADORA: Porta la galleda de barret. Li queda bé.
    • look — SEMPRE
        JUGADORA: Una altra càmera, en un racó. Gira i gira, com si busqués on seure.

GALLEDA «galleda» — hi és si no té galleda (iri) i NO camera2_tapada
    • pickUp — SEMPRE
        JUGADORA: Una galleda. Buida, per sort.
        ⇒ rep galleda
    • look — SEMPRE
        JUGADORA: Una galleda blava de fregar. Té vocació de barret.

CARTELL «cartell» — hi és si no té cartell (iri) i NO camera1_tapada
    • pickUp — SEMPRE
        JUGADORA: «Neteja en curs». La frase més poderosa de tot l'edifici.
        ⇒ rep cartell
    • look — SEMPRE
        JUGADORA: Un cartell groc: «Neteja en curs». Davant d'un cartell així, tothom gira la vista.

EXTINTOR «extintor» — hi és si no té extintor (iri)
    • pickUp — SEMPRE
        JUGADORA: Un extintor. Per si de cas. Sempre hi ha un per si de cas.
        ⇒ rep extintor
    • look — SEMPRE
        JUGADORA: Un extintor vermell. El pla B de tots els plans.

PORTA_NETEJA «porta de neteja»
    • use/open/walkTo — si camera1_tapada i camera2_tapada
        [SO: porta_neteja] JUGADORA: Ningú no mira. Endins.
        ⇒ → bcmu_escombraries
    • use/open — si NO robot_aturat
        JUGADORA: D'aquí entra i surt el robot. I les dues càmeres miren la porta de dret.
    • use/open — SEMPRE
        JUGADORA: Les càmeres miren la porta de dret. Primer, les càmeres.
    • look — SEMPRE
        JUGADORA: La porta de neteja. Darrere, la sala d'escombraries i el Llibre Major.

PORTA_ESCALA «porta de l'escala»
    • use/open — SEMPRE
        JUGADORA: Tancada. Pany antic, de clau grossa.
    • look — SEMPRE
        JUGADORA: La porta de l'escala. Pany antic, de clau grossa.

PORTA_VIP «porta VIP»
    • use/open/walkTo — SEMPRE
        NARRADOR: L'Iri no és premium. L'Iri és una hacker amb una dessuadora.
    • look — SEMPRE
        JUGADORA: Una porta amb catifa vermella: «Només per a clients premium».

TUB «estació del tub»
    • use + qualsevol objecte — SEMPRE
        ⇒ acció tub.enviar
    • open/use/pickUp — SEMPRE
        JUGADORA: Una càpsula de llautó, buida. Hi caben coses petites i secrets.
    • look — SEMPRE
        JUGADORA: L'estació del tub pneumàtic del tercer pis.

ASCENSOR «ascensor de servei»
    • use/open — SEMPRE
        JUGADORA: Baixar? El Llibre Major és aquí dalt.
    • look — SEMPRE
        JUGADORA: L'ascensor de servei. Per avall, només hi ha feina.

```

## Sala La sala de seguretat · `bcmu_seguretat` (vet)

```
EN ENTRAR
    • * (una vegada) — SEMPRE
        EL DIRECTOR: Ballester, atengui la senyora. És auditora.
        BALLESTER: Sí, senyor Director.
        EL DIRECTOR: Jo tinc una reunió sobre sostenibilitat, dalt al despatx. Ens fa molta il·lusió, la sostenibilitat.
        NARRADOR: El Director se'n va. En Ballester torna a mirar el mòbil.
        JUGADORA: Enorme, uniforme i un collaret amb una clau. És ell.

DECORAT got_trencat — es veu si got_trencat
DECORAT collaret_taula — es veu si aliat_ballester i NO clau_agafada

BALLESTER «Ballester»
    • talkTo — SEMPRE
        ⇒ diàleg ballester
    • look — si aliat_ballester
        JUGADORA: En Ballester, sense collaret. Sembla més lleuger.
    • look — si clau_canviada
        JUGADORA: Porta la clau de casa nostra al coll. Amb orgull.
    • look — si sospita_ballester ≥ 1
        JUGADORA: En Ballester té una mà al mòbil i l'altra, massa a prop de la ràdio.
    • look — SEMPRE
        JUGADORA: Un armari de dos metres amb uniforme. Al coll, un collaret amb una clau. Al mòbil, La Comissària Bassols.

MONITORS «monitors»
    • look — si camera1_tapada i camera2_tapada
        JUGADORA: En un monitor, un cartell de «Neteja en curs». En un altre, una galleda. En Ballester no hi mira.
    • look — si iri_al_tercer
        JUGADORA: En un monitor hi surt una noia amb dessuadora. En Ballester no hi mira. Millor.
    • look — SEMPRE
        JUGADORA: Vint monitors i ningú que els miri. L'art contemporani de la seguretat.

RADIO «ràdio»
    • look — si regla_bips
        JUGADORA: La ràdio d'en Ballester. Per aquí sent tots els bips del banc. Té l'oïda d'un ratpenat.
    • look — SEMPRE
        JUGADORA: La ràdio d'en Ballester. Sempre encesa, sempre a prop de la seva mà.
    • use/pickUp/push — SEMPRE
        JUGADORA: Tocar la ràdio d'un guarda és com tocar el plat d'un gos.

GOT «got»
    • use/push/pickUp — si sync_collaret i NO got_trencat
        [SO: got] JUGADORA: Ui! Se m'ha escapat.
        BALLESTER: Un altre got. Ja en van tres aquest mes.
        ⇒ +got_trencat, coberta += 1, sospita_ballester += 1
    • use/push/pickUp — si got_trencat
        JUGADORA: Ja és trencat. Trencar-lo dues vegades seria sospitós.
    • use/push/pickUp — SEMPRE
        JUGADORA: Un got d'aigua. De moment, no tinc cap motiu per trencar res.
    • look — si got_trencat
        JUGADORA: Vidres per terra. Un got que ha donat la vida per la causa.
    • look — SEMPRE
        JUGADORA: Un got d'aigua, a la vora de la taula. Molt a la vora.

ENTREPA «entrepà d'en Ballester» — hi és si NO entrepa_b_agafat
    • pickUp — SEMPRE
        JUGADORA: Senyor Ballester, que té gana?
        BALLESTER: No.
        JUGADORA: Doncs me'l quedo.
        ⇒ rep entrepa_ballester, +entrepa_b_agafat
    • look — SEMPRE
        JUGADORA: L'entrepà d'en Ballester. Mortadel·la, embolicat amb paper d'alumini i resignació.

CLAUER «clauer» — hi és si NO clauer_agafat
    • pickUp — SEMPRE
        JUGADORA: Un clauer sense claus. Ja l'omplirem.
        ⇒ rep clauer, +clauer_agafat
    • look — SEMPRE
        JUGADORA: Un clauer de «Visiteu Ginebra». Sense cap clau. Com el turisme.

COLLARET «collaret» — hi és si aliat_ballester i NO clau_agafada
    • pickUp — SEMPRE
        JUGADORA: La clau del Llibre Major. Pesa més del que sembla.
        ⇒ rep clau_llibre, +clau_agafada
    • look — SEMPRE
        JUGADORA: El collaret d'en Ballester, damunt la taula. Ell mira cap a una altra banda.

TUB «estació del tub»
    • use + qualsevol objecte — SEMPRE
        ⇒ acció tub.enviar
    • open/use/pickUp — SEMPRE
        JUGADORA: Una càpsula de llautó, buida. Hi caben coses petites i secrets.
    • look — SEMPRE
        JUGADORA: L'estació del tub de la sala de seguretat. Aquí arriben els informes que en Ballester no llegeix.

ASCENSOR «ascensor»
    • use/open/walkTo — si sync_collaret
        JUGADORA: Ara no puc deixar en Ballester sol amb la ràdio.
    • use/open/walkTo — SEMPRE
        [SO: ascensor] NARRADOR: L'ascensor baixa al vestíbul, amb els mateixos violins.
        ⇒ −vet_a_seguretat, → bcmu_vestibul
    • look — SEMPRE
        JUGADORA: L'ascensor. Baixa al vestíbul.

```

## Sala El vestíbul del BCMU · `bcmu_vestibul` (vet)

```
EN ENTRAR
    • * (una vegada) — SEMPRE
        NARRADOR: Ginebra. El vestíbul del Banc Central Mundial Unificat. Marbre, quadres i un silenci que cobra comissió.
        [SO: auricular] IRI: Jo entro pel moll de càrrega, amb els tècnics. Tu, per la porta gran.
        JUGADORA: Com sempre: tu pel darrere i jo per la façana.
        JUGADORA: La clau la porta el Cap de Seguretat. On és un Cap de Seguretat? A la sala de seguretat.
        JUGADORA: Doncs avui vull auditar la seguretat.

DECORAT sospita — es veu si auditoria
DECORAT sospita_25 — es veu si auditoria i sospita ≥ 25
DECORAT sospita_50 — es veu si auditoria i sospita ≥ 50
DECORAT sospita_75 — es veu si auditoria i sospita ≥ 75
DECORAT planta_retallada — es veu si planta_retallada
DECORAT maquina_forat — es veu si entrepa_comprat

BONFILL «Director» — hi és si NO auditoria_acceptada
    • talkTo — SEMPRE
        ⇒ diàleg bonfill
    • look — si sap_bonfill
        JUGADORA: El Director Bonfill. Somriu tant que fa mal a la mandíbula només de mirar-lo.
    • look — SEMPRE
        JUGADORA: Un senyor impecable, amb un somriure de catàleg. Deu ser el Director.
    • give + qualsevol objecte — SEMPRE
        JUGADORA: Aquest home ja ho té tot. Fins i tot el que és meu.

FONT «font»
    • use/pickUp — SEMPRE
        JUGADORA: Ni una gota. Estalvien fins i tot l'aigua que no fan servir.
    • look — SEMPRE
        JUGADORA: Una font de marbre, seca. Té un rètol: «Tancada per estalvi de costos».

CARTELL «cartell»
    • look — SEMPRE
        JUGADORA: «Aquí construïm el futur de tothom».
        JUGADORA: «Tothom» deu ser una paraula molt gran per a tan poca gent.

RETRAT «retrat»
    • look — si sap_rockefeller
        JUGADORA: El Director i en Rockefeller. Tots dos amb collar, però només un amb pedigrí.
    • look — SEMPRE
        JUGADORA: Hi ha una placa: «El Director Bonfill i en Rockefeller».
        JUGADORA: El gos té millor perruqueria que jo.
        IRI: Rockefeller. Apuntat. Quin nom per a un gos. ⟨si auricular_compartit⟩
        ⇒ +sap_rockefeller, +sap_bonfill

RECEPCIO «recepció»
    • talkTo — SEMPRE
        JUGADORA: No hi ha ningú. Ni tan sols algú que digui que no hi ha ningú.
    • look — SEMPRE
        JUGADORA: La recepció, buida. Un cartell: «Som a la reunió de benestar laboral».

TUB «estació del tub»
    • use + qualsevol objecte — SEMPRE
        ⇒ acció tub.enviar
    • open/use/pickUp — SEMPRE
        JUGADORA: Una càpsula de llautó, buida. Hi caben coses petites i secrets.
    • look — SEMPRE
        JUGADORA: L'estació del tub pneumàtic, al costat de la recepció. Va a totes les plantes.

MAQUINA «màquina d'entrepans»
    • use/pickUp/push — si entrepa_comprat
        JUGADORA: Un ja n'hi ha prou. Amb el que valen, és un pla de pensions.
    • use/pickUp/push — si propines
        JUGADORA: Les propines d'una nit. Un entrepà suís.
        [SO: maquina_cafe] NARRADOR: La màquina s'ho pensa, s'ho repensa i deixa caure un entrepà.
        ⇒ rep entrepa_suis, +entrepa_comprat
    • use/pickUp/push — SEMPRE
        JUGADORA: 8,50 €. No porto ni un cèntim.
    • look — si entrepa_comprat
        JUGADORA: Ara té un forat on hi havia un entrepà. Com una dent.
    • look — SEMPRE
        JUGADORA: Una màquina d'entrepans. 8,50 €. A Ginebra fins i tot l'entrepà cotitza.

PLANTES «plantes»
    • look — si planta_retallada
        JUGADORA: Hi falta una planta. L'han retallada.
    • look — SEMPRE
        JUGADORA: Plantes de plàstic. Aquí ni les plantes fan la fotosíntesi gratis.

ASCENSOR «ascensor»
    • use/open/walkTo — si auditoria_acceptada
        [SO: ascensor] NARRADOR: L'ascensor puja amb música de violins.
        ⇒ +vet_a_seguretat, → bcmu_seguretat
    • use/open — SEMPRE
        JUGADORA: Sense una excusa, l'ascensor és per als de casa. I el Director no em treu l'ull de sobre.
    • look — SEMPRE
        JUGADORA: Un ascensor daurat. Fins i tot els botons semblen cars.

SORTIDA «sortida»
    • use/open/walkTo — SEMPRE
        JUGADORA: Encara no. No he vingut fins a Ginebra per un entrepà.
    • look — SEMPRE
        JUGADORA: La porta gran. Per aquí s'hi entra. Sortir, ja és més car.

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
        JUGADORA: Ho tinc. Ho tinc ho tinc ho tinc. Amb un tres per cent de bateria, però ho tinc.
        JUGADORA: Vet? VET! Ho he trobat! Podem entrar a la banca mundial!
        VET: Jo també he trobat una cosa: que no has rentat els plats en nou dies.
        JUGADORA: Saps què és el més divertit? Que el BCMU té més diners que cent vuitanta països junts. I no són seus. Són dels altres.
        VET: I nosaltres no en tenim ni per pizzes.
        JUGADORA: Doncs per això ho repartirem. Pizza per a tothom.
        JUGADORA: Però primer... No. No, no, no. S'ha mort.
        [SO: miol] JUGADORA: Necessito internet de debò. I el router nou encara és a la caixa.
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
        VET: Espera. Quan deies «entrar a la banca mundial»... volies dir amb les cames? ⟨si cables = 2⟩
        JUGADORA: Ara sí. ⟨si cables = 2⟩
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
        VET: Espera. Quan deies «entrar a la banca mundial»... volies dir amb les cames? ⟨si cables = 2⟩
        JUGADORA: Ara sí. ⟨si cables = 2⟩
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
        VET: Espera. Quan deies «entrar a la banca mundial»... volies dir amb les cames? ⟨si cables = 2⟩
        JUGADORA: Ara sí. ⟨si cables = 2⟩
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

## Objecte entrepà suís · `entrepa_suis`

```
• look — si juga vet
    JUGADORA: Un entrepà de 8,50 €. Formatge amb forats i pernil amb pedigrí.
• look — si juga iri
    JUGADORA: Un entrepà suís. Neutral, com el país.
```

## Objecte entrepà d'en Ballester · `entrepa_ballester`

```
• look — si juga vet
    JUGADORA: Mortadel·la, embolicat amb paper d'alumini. Fa olor de garita.
• look — si juga iri
    JUGADORA: L'entrepà d'en Ballester. Mortadel·la. Gràcies, Ballester, siguis qui siguis.
```

## Objecte targeta de planta · `targeta`

```
• look — si juga iri
    JUGADORA: La targeta de la Rius. Obre l'ascensor de servei fins al tercer pis.
• look — si juga vet
    JUGADORA: La targeta de l'ascensor de servei. Té una foto de la Rius enfadada.
```

## Objecte compte de nòmines · `compte_nomines`

```
• look — si juga iri
    JUGADORA: El compte de les nòmines de la subcontracta, escrit a mà per la Rius. Sempre arriben tard.
• look — si juga vet
    JUGADORA: Un número de compte escrit a mà. Lletra d'algú que cobra tard.
```

## Objecte galleda · `galleda`

```
• look — SEMPRE
    JUGADORA: Una galleda blava. Té vocació de barret.
```

## Objecte cartell · `cartell`

```
• look — SEMPRE
    JUGADORA: «Neteja en curs». Davant d'aquest cartell, tothom gira la vista.
```

## Objecte extintor · `extintor`

```
• look — SEMPRE
    JUGADORA: Un extintor vermell. El pla B de tots els plans.
```

## Objecte clau del Llibre Major · `clau_llibre`

```
• look — si juga vet
    JUGADORA: Una clau grossa i antiga, amb una cadena de llautó. Trenta anys penjada d'un coll.
• look — si juga iri
    JUGADORA: La clau del Llibre Major. Hola, preciosa.
```

## Objecte clauer · `clauer`

```
• look — SEMPRE
    JUGADORA: Un clauer de «Visiteu Ginebra». Sense cap clau. Ideal per fer un canvi.
```

## Diàleg `ballester` amb Ballester

```
COMENÇA A: amic (si aliat_ballester) · orgullos (si clau_canviada) · clau_relaxat (si cal_clau i ballester_relaxat) · clau_tens (si cal_clau) · sync (si sync_collaret) · servei (si ha vist ballester.hola) · hola

[hola]
    BALLESTER: Ballester. Cap de Seguretat. Trenta anys a la casa.
    BALLESTER: I tres reestructuracions. Les he sobreviscut totes.
    ↪ menu

[servei]
    BALLESTER: Digui, senyora.
    ↪ menu

[menu]
    ▸ Expliqui'm la seguretat de l'edifici. ⟨una vegada⟩ → seguretat
    ▸ Quin collaret més curiós. ⟨una vegada⟩ → collaret
    ▸ Què mira, al mòbil? → serie
    ▸ Continuï, continuï. → (es queda) · FI

[seguretat]
    BALLESTER: Càmeres, una ràdio i jo. Les càmeres no les miro. La ràdio, la sento. I jo hi soc.
    BALLESTER: Si al banc sona res, jo ho sento.
    ↪ menu

[collaret]
    BALLESTER: La clau del Llibre Major. El banc no es fia de ningú.
    BALLESTER: Ni dels seus. Sobretot dels seus.
    ↪ menu

[serie]
    BALLESTER: Ara no, senyora, estic de servei.
    NARRADOR: Ho diu sense apartar els ulls del mòbil.
    ↪ menu

[sync]
    BALLESTER: Digui, senyora auditora.
    ↪ eines

[eines]
    ▸ (Cantar, malament.) ⟨si NO cantat⟩ → cantar
    ▸ (Explicar l'acudit dels banquers.) ⟨si NO acudit1⟩ → banquers
    ▸ (Explicar l'acudit dels euros.) ⟨si NO acudit2⟩ → euros
    ▸ (Explicar l'acudit de l'auditor.) ⟨si NO acudit3⟩ → auditor
    ▸ Vostè mira La Comissària Bassols? «El violí mut» és el millor capítol. ⟨si marcel_ballester i NO violi_dit⟩ → violi
    ▸ I «La vídua del Liceu»? Quina obra mestra. ⟨si marcel_ballester i NO vidua_dita⟩ → vidua
    ▸ Què mira, al mòbil? ⟨una vegada, si NO marcel_ballester⟩ → serie_sync
    ▸ Res, res. Continuï. → (es queda) · FI

[cantar]
    JUGADORA: ♪ Diners, diners, que no em deixeu dormir... ♪
    BALLESTER: Senyora. Sisplau. Que tinc la ràdio.
    ⇒ +cantat, coberta += 1
    ↪ eines

[banquers]
    JUGADORA: Per què els banquers no juguen mai a fet i amagar? Perquè ningú no els aniria a buscar.
    BALLESTER: Ha! Aquesta l'explico a la garita.
    ⇒ +acudit1, coberta += 1
    ↪ eines

[euros]
    JUGADORA: Dos euros a la porta del banc. Un diu: «Entrem?». I l'altre: «Ni boig. D'aquí no en surt ningú.»
    BALLESTER: D'aquí no en surt ningú! Ha, ha! Molt bona.
    ⇒ +acudit2, coberta += 1
    ↪ eines

[auditor]
    JUGADORA: Un auditor entra en un bar...
    JUGADORA: ...i fa una auditoria.
    NARRADOR: Silenci. Un silenci molt llarg.
    BALLESTER: Això no és un acudit. És un informe.
    ⇒ +acudit3
    ↪ eines

[violi]
    BALLESTER: «El violí mut»! La mira algú més, a part de mi?
    BALLESTER: Quan la Bassols descobreix que el violinista no tocava, que era un disc, i ella ho sabia per les mans...
    BALLESTER: Ho veu? Ja se'm posa la pell de gallina. Ho podria explicar durant hores.
    ⇒ +violi_dit, +ballester_relaxat, coberta += 2
    ↪ eines

[vidua]
    BALLESTER: Inversemblant. Una vídua no s'amaga mai darrere un fagot.
    NARRADOR: En Ballester la mira de reüll. La mà, a prop de la ràdio.
    ⇒ +vidua_dita, sospita_ballester += 1
    ↪ eines

[serie_sync]
    BALLESTER: La Comissària Bassols. No la deu conèixer. Ningú no la coneix.
    ↪ eines

[clau_relaxat]
    BALLESTER: Sap què? Jo soc el que més temps porta aquí. I el que menys guanya dels que porten corbata.
    JUGADORA: I per què no se'n va?
    BALLESTER: Perquè tinc una hipoteca. I el banc... és el meu cap.
    ▸ Venim a robar el banc. Bé: a repartir-lo. → veritat
    ▸ Vingui amb nosaltres. A la UE paguem millor. ⟨si té clau_casa o té clauer⟩ → mentida

[clau_tens]
    BALLESTER: Alguna cosa més, senyora?
    ▸ Quin collaret més bonic. És d'or? ⟨si té clau_casa o té clauer⟩ → or
    ▸ No, res. → (es queda) · FI

[veritat]
    NARRADOR: En Ballester es queda quiet molta estona.
    NARRADOR: Després es treu el collaret i el deixa damunt la taula.
    BALLESTER: Jo no he vist res. Fa trenta anys que no veig res.
    ⇒ +aliat_ballester, aliats += 1

[mentida]
    BALLESTER: Ha! A la UE. Aquesta sí que és bona.
    NARRADOR: Es treu el collaret per ensenyar-li la clau.
    BALLESTER: Miri. L'únic que el banc m'ha confiat en trenta anys.
    NARRADOR: La Vet l'admira, l'acaricia i l'hi torna. Amb el clauer de «Visiteu Ginebra» al lloc de la clau. ⟨si no té clau_casa i té clauer⟩
      ⇒ perd clauer
    NARRADOR: La Vet l'admira, l'acaricia i l'hi torna. Amb la clau de casa al lloc de la del Llibre Major. ⟨si té clau_casa⟩
      ⇒ perd clau_casa
    JUGADORA: Preciosa. Guardi-la bé.
    ⇒ +clau_canviada, rep clau_llibre

[or]
    BALLESTER: D'or? És llautó. Però la clau...
    NARRADOR: Es treu el collaret per ensenyar-li la clau.
    BALLESTER: Miri. L'únic que el banc m'ha confiat en trenta anys.
    NARRADOR: La Vet l'admira, l'acaricia i l'hi torna. Amb el clauer de «Visiteu Ginebra» al lloc de la clau. ⟨si no té clau_casa i té clauer⟩
      ⇒ perd clauer
    NARRADOR: La Vet l'admira, l'acaricia i l'hi torna. Amb la clau de casa al lloc de la del Llibre Major. ⟨si té clau_casa⟩
      ⇒ perd clau_casa
    JUGADORA: Preciosa. Guardi-la bé.
    ⇒ +clau_canviada, rep clau_llibre

[amic]
    BALLESTER: Jo no he vist res. I continuo sense veure-ho.

[orgullos]
    BALLESTER: Avui la clau em pesa diferent. Deu ser l'edat.

```

## Diàleg `bonfill` amb El Director

```
COMENÇA A: hola_marmota (si marmota ≥ 1) · hola

[hola]
    EL DIRECTOR: Bon dia. Qui és vostè?
    JUGADORA: Auditora de la Unió Europea. Inspecció sorpresa.
    EL DIRECTOR: Una sorpresa! M'encanten les sorpreses. Bonfill. Director. I amic de les auditories.
    EL DIRECTOR: Maletí de pell, ulleres de muntura fina... Una auditora de les de debò. ⟨si té maleti i ulleres_posades⟩
      ⇒ sospita −= 30, sospita_nivell := 0
    EL DIRECTOR: Un maletí de pell. Això és seriós. ⟨si té maleti i NO ulleres_posades⟩
      ⇒ sospita −= 15, sospita_nivell := 0
    EL DIRECTOR: Quines ulleres més serioses. ⟨si no té maleti i ulleres_posades⟩
      ⇒ sospita −= 15, sospita_nivell := 0
    ⇒ +auditoria, sospita := 30, sospita_nivell := 1
    ↪ q_maleti

[hola_marmota]
    EL DIRECTOR: Bon dia. Una auditora?
    JUGADORA: De la Unió Europea. Per primera vegada. Molt primera.
    EL DIRECTOR: Una sorpresa! M'encanten les sorpreses. Bonfill. Director. I amic de les auditories.
    EL DIRECTOR: Maletí de pell, ulleres de muntura fina... Una auditora de les de debò. ⟨si té maleti i ulleres_posades⟩
      ⇒ sospita −= 30, sospita_nivell := 0
    EL DIRECTOR: Un maletí de pell. Això és seriós. ⟨si té maleti i NO ulleres_posades⟩
      ⇒ sospita −= 15, sospita_nivell := 0
    EL DIRECTOR: Quines ulleres més serioses. ⟨si no té maleti i ulleres_posades⟩
      ⇒ sospita −= 15, sospita_nivell := 0
    ⇒ +auditoria, sospita := 30, sospita_nivell := 1
    ↪ q_maleti

[q_maleti]
    NARRADOR: El Director acaricia el telèfon. Com qui acaricia un gos. ⟨si sospita ≥ 75 i sospita_nivell < 3 i sospita < 100⟩
      ⇒ sospita_nivell := 3
    NARRADOR: El Director es posa bé la corbata. Massa bé. ⟨si sospita ≥ 50 i sospita_nivell < 2 i sospita < 100⟩
      ⇒ sospita_nivell := 2
    NARRADOR: El Director arqueja una cella. ⟨si sospita ≥ 25 i sospita_nivell < 1 i sospita < 100⟩
      ⇒ sospita_nivell := 1
    EL DIRECTOR: Una auditora sense maletí? ⟨si no té maleti i sospita < 100⟩
    ▸ És que els meus documents són tan secrets que no existeixen. ⟨si no té maleti i sospita < 100⟩ → r_secrets
    ▸ Ups, me'l dec haver deixat a l'avió. ⟨si no té maleti i sospita < 100⟩ → r_avio
        ⇒ sospita += 40
    ▸ La UE ja no fa servir maletins. Ara fem servir núvols. ⟨si (no té maleti i sospita < 100) i marmota ≥ 1⟩ → r_nuvols
        ⇒ sospita −= 5
    ↪ q_jove

[r_secrets]
    EL DIRECTOR: Ah, la transparència europea. La conec bé.
    ↪ q_jove

[r_avio]
    EL DIRECTOR: A l'avió. Una auditora que perd coses. Interessant.
    ↪ q_jove

[r_nuvols]
    EL DIRECTOR: El núvol! Nosaltres també hi tenim coses. Moltes coses.
    ↪ q_jove

[q_jove]
    NARRADOR: El Director acaricia el telèfon. Com qui acaricia un gos. ⟨si sospita ≥ 75 i sospita_nivell < 3 i sospita < 100⟩
      ⇒ sospita_nivell := 3
    NARRADOR: El Director es posa bé la corbata. Massa bé. ⟨si sospita ≥ 50 i sospita_nivell < 2 i sospita < 100⟩
      ⇒ sospita_nivell := 2
    NARRADOR: El Director arqueja una cella. ⟨si sospita ≥ 25 i sospita_nivell < 1 i sospita < 100⟩
      ⇒ sospita_nivell := 1
    EL DIRECTOR: Vostè té cara de... jove. ⟨si NO ulleres_posades i sospita < 100⟩
    ▸ La UE no fa acreditacions: fa directives. ⟨si NO ulleres_posades i sospita < 100⟩ → r_directives
        ⇒ sospita += 5
    ▸ (Ensenyar-li l'acreditació.) Aquí ho diu tot. ⟨si (NO ulleres_posades i sospita < 100) i té acreditacio⟩ → r_acreditacio
        ⇒ sospita += 30
    ▸ Gràcies. És la crema antiedat de la Comissió. ⟨si (NO ulleres_posades i sospita < 100) i marmota ≥ 1⟩ → r_crema
    ↪ q_banca

[r_directives]
    EL DIRECTOR: Les directives. Sí. Les llegim totes. Per sobre.
    ↪ q_banca

[r_acreditacio]
    EL DIRECTOR: Aquí diu «Manteniment de caixes fortes».
    JUGADORA: És una tapadora.
    EL DIRECTOR: Una tapadora. Que bé.
    ↪ q_banca

[r_crema]
    EL DIRECTOR: Una crema europea. Pagada entre tots. Excel·lent.
    ↪ q_banca

[q_banca]
    NARRADOR: El Director acaricia el telèfon. Com qui acaricia un gos. ⟨si sospita ≥ 75 i sospita_nivell < 3 i sospita < 100⟩
      ⇒ sospita_nivell := 3
    NARRADOR: El Director es posa bé la corbata. Massa bé. ⟨si sospita ≥ 50 i sospita_nivell < 2 i sospita < 100⟩
      ⇒ sospita_nivell := 2
    NARRADOR: El Director arqueja una cella. ⟨si sospita ≥ 25 i sospita_nivell < 1 i sospita < 100⟩
      ⇒ sospita_nivell := 1
    EL DIRECTOR: La banca és el cor de la societat. Sense nosaltres, el món s'aturaria. ⟨si sospita < 100⟩
    ▸ I sense nosaltres, vostè no tindria cordons de sabates. ⟨si sospita < 100⟩ → r_cordons
        ⇒ sospita += 10, +dignitat
    ▸ Quin cor més car, oi? El meu no cobra comissions. ⟨si sospita < 100⟩ → r_cor
        ⇒ sospita += 5
    ▸ Totalment d'acord. La banca és imprescindible. ⟨si sospita < 100⟩ → r_dacord
        ⇒ sospita −= 5, +mentida_corporativa
    ↪ q_gos

[r_cordons]
    EL DIRECTOR: ...Cordons. No hi havia pensat mai, en els cordons.
    ↪ q_gos

[r_cor]
    NARRADOR: El Director somriu. Una mica.
    EL DIRECTOR: Molt enginyosa. Per a una auditora.
    ↪ q_gos

[r_dacord]
    EL DIRECTOR: Per fi algú de Brussel·les que ho entén.
    ↪ q_gos

[q_gos]
    NARRADOR: El Director acaricia el telèfon. Com qui acaricia un gos. ⟨si sospita ≥ 75 i sospita_nivell < 3 i sospita < 100⟩
      ⇒ sospita_nivell := 3
    NARRADOR: El Director es posa bé la corbata. Massa bé. ⟨si sospita ≥ 50 i sospita_nivell < 2 i sospita < 100⟩
      ⇒ sospita_nivell := 2
    NARRADOR: El Director arqueja una cella. ⟨si sospita ≥ 25 i sospita_nivell < 1 i sospita < 100⟩
      ⇒ sospita_nivell := 1
    EL DIRECTOR: Ha vist el meu retrat? Li agrada el meu gos? ⟨si sap_rockefeller i sospita < 100⟩
    ▸ Rockefeller, oi? Quin nom més... humil. ⟨si sap_rockefeller i sospita < 100⟩ → r_rockefeller
        ⇒ sospita −= 5
    ▸ Prefereixo els gats. ⟨si sap_rockefeller i sospita < 100⟩ → r_gats
        ⇒ sospita += 5
    ↪ q_veure

[r_rockefeller]
    EL DIRECTOR: Oi que sí? Ningú no m'ho pregunta mai.
    ↪ q_veure

[r_gats]
    EL DIRECTOR: Els gats. Tan... independents.
    ↪ q_veure

[q_veure]
    NARRADOR: El Director acaricia el telèfon. Com qui acaricia un gos. ⟨si sospita ≥ 75 i sospita_nivell < 3 i sospita < 100⟩
      ⇒ sospita_nivell := 3
    NARRADOR: El Director es posa bé la corbata. Massa bé. ⟨si sospita ≥ 50 i sospita_nivell < 2 i sospita < 100⟩
      ⇒ sospita_nivell := 2
    NARRADOR: El Director arqueja una cella. ⟨si sospita ≥ 25 i sospita_nivell < 1 i sospita < 100⟩
      ⇒ sospita_nivell := 1
    EL DIRECTOR: I què vol veure, exactament? ⟨si sospita < 100⟩
    ▸ La seguretat física. ⟨si sospita < 100⟩ → acceptada
    ▸ Les caixes fortes. ⟨si sospita < 100⟩ → r_caixes
        ⇒ sospita += 20
    ▸ Els comptes del Director. ⟨si sospita < 100⟩ → r_comptes
        ⇒ sospita += 50
    ▸ El que no ensenyen als tècnics: la seguretat. ⟨si sospita < 100 i marmota ≥ 1⟩ → acceptada
        ⇒ sospita −= 10
    ↪ trucada

[q_veure2]
    NARRADOR: El Director acaricia el telèfon. Com qui acaricia un gos. ⟨si sospita ≥ 75 i sospita_nivell < 3 i sospita < 100⟩
      ⇒ sospita_nivell := 3
    NARRADOR: El Director es posa bé la corbata. Massa bé. ⟨si sospita ≥ 50 i sospita_nivell < 2 i sospita < 100⟩
      ⇒ sospita_nivell := 2
    NARRADOR: El Director arqueja una cella. ⟨si sospita ≥ 25 i sospita_nivell < 1 i sospita < 100⟩
      ⇒ sospita_nivell := 1
    ▸ La seguretat física. ⟨si sospita < 100⟩ → acceptada
    ▸ Les caixes fortes. ⟨si sospita < 100⟩ → r_caixes
        ⇒ sospita += 20
    ▸ Els comptes del Director. ⟨si sospita < 100⟩ → r_comptes
        ⇒ sospita += 50
    ▸ El que no ensenyen als tècnics: la seguretat. ⟨si sospita < 100 i marmota ≥ 1⟩ → acceptada
        ⇒ sospita −= 10
    ↪ trucada

[r_caixes]
    EL DIRECTOR: Avui ja hi ha tècnics, a les caixes. Doncs què vol veure, de debò?
    ↪ q_veure2

[r_comptes]
    EL DIRECTOR: Els meus comptes? Ha, ha. Quin sentit de l'humor. Què vol veure, de debò?
    ↪ q_veure2

[acceptada]
    EL DIRECTOR: La seguretat! Per fi una auditora que pregunta per coses que es poden tocar.
    EL DIRECTOR: La hi acompanyo personalment. L'espero a l'ascensor.
    ⇒ −auditoria, +auditoria_acceptada

[trucada]
    EL DIRECTOR: Disculpi un moment.
    NARRADOR: El Director truca, molt educadament, a seguretat.
    EL DIRECTOR: Ballester? Una auditora. Sí, molt simpàtica. Acompanyi-la a la sortida, si és tan amable.
    [SO: rebobinar] TÍTOL: Dia de la Marmota
    NARRADOR: La Vet torna a entrar pel vestíbul. Aquest cop, amb menys pressupost: hi ha una planta menys.
    JUGADORA: Ara ja sé què em preguntarà. I què no li he de dir.
    ⇒ −auditoria, marmota += 1, +planta_retallada

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

## Diàleg `neta` amb NETA-3

```
COMENÇA A: amic (si aliat_neta) · descansant (si robot = "codi") · molles (si robot = "entrepa") · hola

[hola]
    NETA-3: NETA-3, unitat de neteja. Passadís en neteja. Circuleu.
    ↪ menu

[menu]
    ▸ NETA, descansa. ⟨si iri_sap_neta⟩ → descansa
    ▸ Quantes hores fa que treballes? ⟨una vegada⟩ → hores
    ▸ Res, res. Continua. → (es queda) · FI

[hores]
    NETA-3: Catorze hores i vint-i-dos minuts. Torn de nit, torn de dia i torn de dia de nit.
    JUGADORA: Això no és un torn. És una condemna.
    ↪ menu

[descansa]
    NETA-3: ...Descansar?
    [SO: robot_atura] NARRADOR: NETA-3 s'atura. Els llums se li abaixen a poc a poc.
    NETA-3: Gràcies. Portava catorze hores seguides.
    NETA-3: No em paguen les hores extres.
    JUGADORA: Aquí no les paguen a ningú. Benvingut al club.
    ⇒ robot := "codi", +robot_aturat, comença hores_neta

[molles]
    NETA-3: Molla quatre-cents dotze. Molla quatre-cents tretze. Ocupat.

[descansant]
    NETA-3: Descansant. És estrany. M'agrada.
    NETA-3: Si algú em canviés l'horari al panell de la sala d'escombraries... No. Ningú no ho farà.

[amic]
    NETA-3: Descans cada quatre hores. I el diumenge. Gràcies, humana.

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

## Diàleg `rius` amb Rius

```
COMENÇA A: aliada (si aliada_rius) · targeta_feta (si té targeta i NO rius_ho_nota) · altra (si ha vist rius.hola) · hola

[hola]
    RIUS: Què? No veus que m'estic barallant amb una aplicació?
    ↪ menu

[altra]
    RIUS: Digues. Ràpid, que l'aplicació em compta els segons.
    ↪ menu

[targeta_feta]
    RIUS: Has vist la meva targeta? Juraria que la duia al cinturó.
    JUGADORA: Jo? No. No he vist res.
    RIUS: Clar. Ningú no veu mai res.
    ⇒ +rius_ho_nota
    ↪ menu

[menu]
    ▸ Què li passa al mòbil? ⟨si NO sap_app⟩ → mobil
    ▸ Deixa'm el mòbil. Les màquines i jo ens entenem. ⟨si sap_app i NO aliada_rius⟩ → arreglar
    ▸ Em deixes la targeta de l'ascensor? ⟨una vegada, si no té targeta⟩ → targeta
    ▸ Rius, em convides a un cafè? ⟨si no té targeta⟩ → cafe
    ▸ Res. Ja et deixo treballar. → (es queda) · FI

[mobil]
    RIUS: L'aplicació de la subcontracta. Ens descompta els minuts que passem al lavabo.
    RIUS: I avui s'ha penjat. Si no fitxem, no cobrem el dia. Tota la colla.
    ⇒ +sap_app
    ↪ menu

[arreglar]
    RIUS: Tu mateixa. Pitjor no el pots deixar.
    JUGADORA: Tranquil. Respira. Ningú no et vol mal.
    [SO: mobil_ok] NARRADOR: L'Iri parla al mòbil com qui calma un gat espantat. El mòbil, agraït, torna a funcionar.
    JUGADORA: I el comptador del lavabo... s'ha esborrat. Quina llàstima.
    RIUS: Ha fitxat. Tota la colla ha fitxat!
    RIUS: Ja l'havies agafada, oi, la targeta? ...Bé. Ara te la deixo. ⟨si té targeta⟩
    RIUS: Té. La targeta de l'ascensor. Si et pregunten, ets la de l'ascensor. ⟨si no té targeta⟩
      ⇒ rep targeta
    RIUS: I això. El compte de les nòmines de la subcontracta. Me'l sé de memòria, perquè sempre arriben tard.
    RIUS: Si mai pots fer que arribin a l'hora...
    ⇒ +aliada_rius, aliats += 1, rep compte_nomines

[targeta]
    RIUS: Ni parlar-ne. Si et pillen al tercer pis, la que plega soc jo.
    RIUS: I amb aquest mòbil penjat, ja tinc prou problemes.
    ↪ menu

[cafe]
    RIUS: Un cafè? ...Va. Total, avui ja no cobro.
    [SO: maquina_cafe] NARRADOR: La màquina s'empassa la moneda. La Rius li clava un cop de puny.
    NARRADOR: La moneda rodola per terra, i la Rius s'ajup a buscar-la.
    NARRADOR: L'Iri, amb dos dits, li agafa la targeta del cinturó.
    JUGADORA: Saps què? Millor me'l faig després.
    ⇒ rep targeta, +cafe_moll

[aliada]
    RIUS: Avui fitxem a l'hora. Gràcies, la de l'ascensor.

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
vet_espera_iri — quan juga vet i (acte1_fet i NO acte2_fet) i vet_a_seguretat i NO sync_collaret i NO cal_clau · fins que sync_collaret o cal_clau
    1. L'Iri encara no és al Llibre Major. En Ballester no se'n va enlloc.
    2. Iri, com ho portes?
    3. Canvia a l'Iri: quan sigui al Llibre Major i comenci a teclejar, et necessitarà.
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
vet_auditora — quan juga vet i (acte1_fet i NO acte2_fet) i NO auditoria_acceptada · fins que auditoria_acceptada
    1. Vet, pensa com una mentidera. Ah, si ja ho ets.
    2. Una auditora necessita algú a qui auditar. I aquí el que mana és el Director.
    3. Parla amb el Director. Al final, demana-li veure la seguretat. Si s'escama, el que aprenguis et servirà a la propera.
vet_ascensor — quan juga vet i (acte1_fet i NO acte2_fet) i auditoria_acceptada i NO vet_a_seguretat · fins que vet_a_seguretat
    1. El Director m'espera.
    2. On m'espera? A l'ascensor.
    3. Agafa l'ascensor cap a la sala de seguretat.
vet_enviar_menjar — quan juga vet i (acte1_fet i NO acte2_fet) i (iri_al_tercer i NO robot_aturat i no té entrepa (iri) i no té entrepa_suis (iri) i no té entrepa_ballester (iri)) i NO iri_sap_neta i (té entrepa o té entrepa_suis o té entrepa_ballester) · fins que robot_aturat o no (té entrepa o té entrepa_suis o té entrepa_ballester)
    1. Iri: «Vet, aquest robot no para. Tens res que faci molles?»
    2. Un entrepà fa moltes molles. I un robot de neteja no pot deixar una molla a terra.
    3. Envia l'entrepà a l'Iri pel tub.
vet_buscar_menjar — quan juga vet i (acte1_fet i NO acte2_fet) i (iri_al_tercer i NO robot_aturat i no té entrepa (iri) i no té entrepa_suis (iri) i no té entrepa_ballester (iri)) i NO iri_sap_neta i no (té entrepa o té entrepa_suis o té entrepa_ballester) · fins que robot_aturat o (té entrepa o té entrepa_suis o té entrepa_ballester)
    1. Iri: «Vet, aquest robot no para. Tens res que faci molles?»
    2. No tinc res de menjar. Però en aquest edifici sí que n'hi ha.
    3. La màquina del vestíbul fa entrepans. I en Ballester en té un damunt la taula.
vet_cobrir — quan juga vet i sync_collaret i coberta < 1 i codis ≥ 1 · fins que coberta ≥ 1 o cal_clau
    1. Cada bip, en Ballester el sent per la ràdio. Abans que l'Iri tecleji, l'he de tapar.
    2. Cantar, un acudit, un got que cau... o una cosa que li agradi molt.
    3. Parla amb en Ballester: canta, explica-li un acudit o trenca el got. Si saps quin capítol de La Comissària Bassols li agrada, en tapa dos.
vet_clau — quan juga vet i cal_clau i NO aliat_ballester i NO clau_canviada · fins que aliat_ballester o clau_canviada
    1. Ara la clau. La porta al coll.
    2. Quan en Ballester parla de la sèrie, s'obre. Potser llavors m'escoltaria. I si no, té un collaret molt bonic.
    3. Parla amb en Ballester. Si està relaxat, digues-li la veritat. Si no, canvia-li la clau per la de casa.
vet_collaret — quan juga vet i aliat_ballester i NO clau_agafada · fins que clau_agafada
    1. En Ballester mira cap a una altra banda. Molt fixament.
    2. El collaret és damunt la taula.
    3. Agafa el collaret de la taula.
vet_enviar_clau — quan juga vet i té clau_llibre (vet) · fins que no té clau_llibre (vet)
    1. Aquesta clau no és per a mi.
    2. L'Iri és tres pisos més amunt. Per sort, en aquest edifici hi ha un tub.
    3. Envia la clau a l'Iri pel tub.
iri_rius — quan juga iri i (acte1_fet i NO acte2_fet) i NO iri_al_tercer i no té targeta · fins que té targeta
    1. Què faries tu, ascensor? Sense targeta, res.
    2. La targeta la porta la Rius al cinturó. I la Rius té un problema amb el mòbil.
    3. Parla amb la Rius: arregla-li l'aplicació, o demana-li un cafè.
iri_ascensor — quan juga iri i (acte1_fet i NO acte2_fet) i té targeta i NO iri_al_tercer · fins que iri_al_tercer
    1. Tercer pis. Sala d'escombraries.
    2. Ja tinc la targeta.
    3. Agafa l'ascensor de servei.
iri_robot_codi — quan juga iri i iri_al_tercer i NO robot_aturat i iri_sap_neta · fins que robot_aturat
    1. Primer el robot: si tapo una càmera, me la destapa.
    2. En Marcel el va programar. I tenia una frase per aturar-lo.
    3. Parla amb NETA-3 i digues-li: «NETA, descansa».
iri_robot — quan juga iri i iri_al_tercer i NO robot_aturat i NO iri_sap_neta · fins que robot_aturat
    1. Primer el robot: si tapo una càmera, me la destapa. Què faries tu, robot? Netejar.
    2. Si li dono feina, potser s'atura. Molta feina. Molles, per exemple. Vet?
    3. Fes servir un entrepà amb NETA-3. Si no en tens, la Vet te'n pot enviar un pel tub.
iri_cameres — quan juga iri i robot_aturat i no (camera1_tapada i camera2_tapada) · fins que camera1_tapada i camera2_tapada
    1. Les dues càmeres miren la porta de neteja.
    2. Al passadís hi ha un cartell de «Neteja en curs» i una galleda. Una càmera és a la zona de neteja i l'altra, en un racó.
    3. El cartell, davant de la primera càmera. La galleda, de barret a la del racó.
iri_porta_neteja — quan juga iri i camera1_tapada i camera2_tapada i NO iri_a_llibre · fins que iri_a_llibre
    1. Ningú no mira.
    2. La porta de neteja.
    3. Entra per la porta de neteja.
iri_llibre_espera — quan juga iri i iri_a_llibre i NO vet_a_seguretat i NO sync_collaret i NO cal_clau · fins que vet_a_seguretat
    1. Si teclejo ara, em sentirà tot el banc.
    2. La Vet ha de ser a la sala de seguretat, amb en Ballester.
    3. Canvia a la Vet i porta-la a la sala de seguretat.
iri_llibre — quan juga iri i iri_a_llibre i vet_a_seguretat i NO sync_collaret i NO cal_clau · fins que sync_collaret o cal_clau
    1. Hola, preciós. Què em demanes?
    2. La Vet ja és a seguretat.
    3. Fes servir el Llibre Major.
iri_teclejar — quan juga iri i sync_collaret i (coberta ≥ 1 o codis = 0) · fins que cal_clau
    1. Ara no em sent ningú.
    2. La Vet ja l'entreté. És el moment.
    3. Fes servir el Llibre Major: tecleja el codi.
iri_esperar — quan juga iri i sync_collaret i coberta < 1 i codis ≥ 1 · fins que coberta ≥ 1 o cal_clau
    1. Si teclejo sense que la Vet el tapi, en Ballester el sentirà.
    2. Vet, avisa'm quan l'hagis distret.
    3. Canvia a la Vet: que distregui en Ballester abans de cada bip.
iri_clau_espera — quan juga iri i cal_clau i no té clau_llibre (iri) · fins que té clau_llibre (iri)
    1. Ara demana la clau física.
    2. La té en Ballester, al coll. I la Vet és amb ell.
    3. Canvia a la Vet: que aconsegueixi la clau i te l'enviï pel tub.
iri_girar — quan juga iri i té clau_llibre (iri) i NO clau_girada · fins que clau_girada
    1. Hola, preciosa.
    2. El Llibre Major té un pany.
    3. Fes servir la clau amb el Llibre Major.
```

## Finals

```
continuara «Continuarà» — quan acte2_fet
    Fins aquí, els dos primers actes de Suma Zero. ROBIN HOOD 2.0 ja està en marxa. Què podria sortir malament?
```
