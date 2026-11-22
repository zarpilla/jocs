# Revisió de textos

> Generat amb `npm run revisio` a partir de `game/data/`. No l'editis a mà.
>
> Per a cada cosa, les interaccions en l'ordre en què el motor les prova: s'agafa **la primera que encaixa**.
> Una interacció «SEMPRE» que no és l'última amaga les de sota.

## Sala Crèdits · `credits` — cinemàtica

```
```

## Sala Sala de calderes · `fabrica_calderes` (iri)

```
EN ENTRAR
    • * — si acte3_iniciat i NO iri_descoberta
        NARRADOR: Mentrestant, cent vint anys abans...
        NARRADOR: «Atenció, operària I. Sé què ha fet amb la meva cambra. Inspector Sic: que no hi torni a entrar.»
        JUGADORA: M'ha descobert. És clar: la cambra la va fer ell.
        ⇒ +iri_descoberta
    • * (una vegada) — SEMPRE
        TÍTOL: Ferro-9
        TÍTOL: Acte 1 · La descoberta
        NARRADOR: Torn de nit. Fàbrica de ferro-9 de la Corporació Aldaia.
        [SO: alarma] JUGADORA: Una altra vegada l'alarma de vibració. Ve de la cambra experimental.
        JUGADORA: La clau la té el Cargol. I el Cargol només dona coses amb paperassa.
        ⇒ comença acte1

DECORAT alarma_encesa — es veu si NO alarma_apagada

CAPATAS «capatàs Tul»
    • use/give + formulari_27be — si té llapis
        [SO: escriure] JUGADORA: Li poso el formulari sota la mà i el llapis entre els dits...
        CAPATÀS TUL: Mmm... cinc minuts més, mare...
        JUGADORA: Ha signat. Literalment: «Cinc minuts més, mare». Per al Cargol, n'hi haurà prou.
        ⇒ perd formulari_27be, rep formulari_27be_signat
    • use/give + formulari_27be — SEMPRE
        JUGADORA: Sense un llapis, no signarà ni dormint.
    • use + diapaso_espatllat — si sospita_sic ≥ 2 i NO mira_salvada
        JUGADORA: Li deixo el diapasó xiulador a la butxaca. Ferro-9 inventariat, a la butxaca del capatàs...
        JUGADORA: No n'estic orgullosa. Però ell dorm i la Mira, no.
        ⇒ perd diapaso_espatllat, +mira_salvada, +capatas_acusat
    • look — si NO segell_caigut
        JUGADORA: El capatàs Tul. Dorm abraçat al segell oficial com si fos un osset de peluix.
    • look — SEMPRE
        [SO: ronc] JUGADORA: Dorm com un angelet. Un angelet que ronca.
    • talkTo — SEMPRE
        JUGADORA: Capatàs? Capatàs Tul?
        [SO: ronc] CAPATÀS TUL: Zzz... cinc minuts més, mare...
    • pull/pickUp — si NO segell_caigut
        JUGADORA: Estiro el segell amb molt de compte...
        CAPATÀS TUL: Mmmf. És meu...
        JUGADORA: L'agafa encara més fort. Per estar dormint, té molta força.
    • push — SEMPRE
        JUGADORA: Si el desperto, m'enviarà a escurar calderes fins a la jubilació.
    • use + plomall — si NO segell_caigut
        JUGADORA: Li faig pessigolles al nas amb el plomall...
        [SO: segell] CAPATÀS TUL: Ji, ji, ji... Prou, Margarida... ji, ji...
        JUGADORA: Ha deixat anar el segell per gratar-se el nas. Ha caigut a terra.
        ⇒ +segell_caigut
    • use + qualsevol objecte — SEMPRE
        JUGADORA: Millor no despertar-lo amb això.

SEGELL «segell oficial» — hi és si segell_caigut i NO segell_agafat
    • look — SEMPRE
        JUGADORA: El segell oficial, a terra. Tan a prop. Tan oficial.
    • pickUp — SEMPRE
        JUGADORA: Ja és meu. Ara tinc autoritat. Una mica.
        ⇒ rep segell, +segell_agafat

TAULER «tauler d'anuncis»
    • look — SEMPRE
        JUGADORA: «RECORDEU: tota sol·licitud de material requereix el formulari 27-B, degudament segellat.»
        JUGADORA: Al costat, una pila de formularis 27-B. Tants que fan pila.
    • pickUp — si no té formulari_27b i no té formulari_segellat i no té formulari_triplicat
        JUGADORA: Un formulari 27-B. En blanc, com la meva carrera professional.
        ⇒ rep formulari_27b
    • pickUp — SEMPRE
        JUGADORA: Ja en tinc un. No vull que la paperassa em domini.

ALARMA «llum d'alarma»
    • look — si NO alarma_apagada
        JUGADORA: L'alarma de vibració. Ve de la cambra de ressonància.
        JUGADORA: La cambra experimental que ningú no fa servir. I que ningú no sap per què es va construir.
    • look — SEMPRE
        JUGADORA: Apagada. Silenci. El meu so preferit.

PORTA_MAGATZEM «magatzem»
    • open/use/walkTo — SEMPRE
        ⇒ → fabrica_magatzem
    • look — SEMPRE
        JUGADORA: El magatzem d'eines. El regne del Cargol.

PORTA_CAMBRA «porta de la cambra»
    • use + qualsevol objecte — si iri_descoberta i NO sic_distret
        INSPECTOR SIC: Ni un pas, operària.
    • open/use/walkTo/push/pull — si iri_descoberta i NO sic_distret
        INSPECTOR SIC: Ni un pas, operària.
    • use + clau_cambra — si NO porta_cambra_oberta
        [SO: clac] JUGADORA: Clic. Oberta.
        ⇒ +porta_cambra_oberta, perd clau_cambra, → fabrica_cambra
    • open/use/walkTo — si porta_cambra_oberta
        ⇒ → fabrica_cambra
    • open/use/pull/push — SEMPRE
        JUGADORA: Tancada. La clau la guarda el Cargol, al magatzem. Amb paperassa, és clar.
    • look — SEMPRE
        JUGADORA: La porta de la cambra de ressonància. Vibra.

PORTA_MOLL «moll de càrrega»
    • open/use/walkTo — SEMPRE
        ⇒ → fabrica_moll

SIC «Inspector Sic» — hi és si iri_descoberta i NO sic_distret
    • talkTo — SEMPRE
        ⇒ diàleg sic
    • look — SEMPRE
        JUGADORA: L'Inspector Sic, plantat davant la porta de la cambra com un pilar més.

```

## Sala Cambra de ressonància · `fabrica_cambra` (iri)

```
EN ENTRAR
    • * — si acte3_iniciat i NO iri_descoberta
        NARRADOR: Mentrestant, cent vint anys abans...
        NARRADOR: «Atenció, operària I. Sé què ha fet amb la meva cambra. Inspector Sic: que no hi torni a entrar.»
        JUGADORA: M'ha descobert. És clar: la cambra la va fer ell.
        JUGADORA: El Sic ja és aquí. M'acompanya a fora de la cambra, amb molta educació i cap mena de dubte.
        ⇒ +iri_descoberta, → fabrica_calderes
    • * — si sic_distret i NO iri_a_la_cambra
        JUGADORA: La cambra. El Sic trigarà a tornar: el magatzem del ferro-9 és al soterrani, i té molts racons.
        JUGADORA: V., si m'has d'enviar alguna cosa, ara és el moment. ⟨si no té mapa_fuga (iri)⟩
        ⇒ +iri_a_la_cambra
    • * (una vegada) — SEMPRE
        [SO: alarma] JUGADORA: La cambra de ressonància. L'alarma ve de la consola.
        JUGADORA: Una palanca, un botó vermell i un vidre gruixut. Què podria anar malament?
    • * — si finestra_armada = "vet"
        JUGADORA: La consola parpelleja. Això abans no ho feia.

DECORAT reixa_llimada — es veu si reixa_preparada
DECORAT palanca_alcada — es veu si NO alarma_apagada
DECORAT palanca_baixada — es veu si alarma_apagada

PALANCA «palanca»
    • use + clau_anglesa — si NO alarma_apagada
        JUGADORA: Faig palanca amb la clau anglesa...
        [SO: palanca] JUGADORA: La palanca baixa de cop! L'alarma, per fi, para.
        JUGADORA: Però ara la cambra brunzeix, i a la consola s'ha encès un botó vermell.
        [SO: cambra_posa] JUGADORA: I la clau anglesa vibra igual que la cambra. Curiós... La poso a dins, a veure què fa.
        ⇒ +alarma_apagada, perd clau_anglesa, finestra_objecte_iri := "clau_anglesa"
    • pull/push/use — si NO alarma_apagada
        JUGADORA: Està encallada. Necessito fer palanca amb alguna cosa.
    • look — SEMPRE
        JUGADORA: La palanca de la consola. Vibra com si tingués fred.
    • pull/push/use — SEMPRE
        JUGADORA: Ja està baixada. Millor no tocar-la més.

CAMBRA «cambra»
    • look — si alarma_apagada i NO accident_cambra i finestra_objecte_iri = "clau_anglesa"
        JUGADORA: La clau anglesa és a dins, i la cambra brunzeix. El botó vermell fa pampallugues.
    • pickUp/open — si alarma_apagada i NO accident_cambra i finestra_objecte_iri = "clau_anglesa"
        JUGADORA: La deixo a dins una estona. Vull veure què passa.
    • look — si finestra_armada = "vet"
        JUGADORA: Dins la cambra hi ha una llum que parpelleja. Com si algú, a l'altra banda, esperés.
    • look — si finestra_armada = "iri" i finestra_objecte_iri ≠ ""
        JUGADORA: El que he posat és a dins, i el vidre no s'obre. El camp està armat.
    • look — si transferencies ≥ 1
        JUGADORA: La cambra està buida. Les coses hi entren... i desapareixen.
    • look — SEMPRE
        JUGADORA: Una cambra de vidre gruixut, plena de bobines de ferro-9.
    • use + diapaso — si NO diapaso_afinat
        JUGADORA: Encara no sona com la molla. Si l'envio així, a la V. no li servirà de res.
    • use + tub_ferro9 — SEMPRE
        JUGADORA: Si envio el tub sol, la llibreta amb les proves es queda aquí. Ha de ser tot en un sol enviament.
    • use + imant_ferro9 — si porta_cella_oberta
        JUGADORA: Un altre imant per a la V.? Ja és fora de la cel·la. Me'l quedo, que aquí també hi ha panys M-3.
    • use + qualsevol objecte — SEMPRE
        ⇒ acció finestra.posar
    • pickUp/open — SEMPRE
        ⇒ acció finestra.treure

BOTO «botó de sincronia» — hi és si alarma_apagada
    • push/use — si alarma_apagada i NO accident_cambra i finestra_objecte_iri = "clau_anglesa"
        JUGADORA: Ningú no ho ha d'autoritzar si ningú no ho veu. Premo el botó.
        [SO: cambra_arma] JUGADORA: El vidre baixa de cop! La clau s'ha quedat a dins.
        JUGADORA: I ara no s'obre. Fantàstic.
        JUGADORA: Ja la recuperaré demà. Uf. Quin brunzit.
        NARRADOR: Mentrestant, cent vint anys després...
        ⇒ +accident_cambra, finestra_armada := "iri", esdeveniment protagonista
    • look — SEMPRE
        JUGADORA: Un botó vermell. «SINCRONIA. NO PRÉMER SENSE AUTORITZACIÓ DE DIRECCIÓ».
    • push/use — SEMPRE
        ⇒ acció finestra.boto

PORTA «sala de calderes»
    • open/use/walkTo — SEMPRE
        ⇒ → fabrica_calderes

REIXA «reixa»
    • open/use/walkTo/pull/pickUp/push — si (té tub_amb_llibreta (vet) o tub_muntat) i reixa_preparada i ruta_marcada
        [SO: reixa] JUGADORA: Ara sí. Aparto la reixa, que surt com si res, i m'hi fico.
        [SO: conducte] JUGADORA: Segueixo les meves pròpies fletxes fins al moll. Qui m'ho havia de dir.
        ⇒ → fabrica_moll
    • open/use/walkTo/pull/pickUp/push — si reixa_preparada i NO ruta_marcada
        [SO: reixa] JUGADORA: Aparto la reixa, que surt com si res, i m'hi fico.
        [SO: conducte] JUGADORA: A dins s'eixampla: hi caben els robots de manteniment. Cinc revolts fins al moll, i al fullet de la V. hi ha un signe per a cada un.
        ⇒ conducte_pas := 0, conducte_errades := 0, conducte_vista := 0, → fabrica_conducte
    • use + llima — si iri_sap_reixa i NO reixa_preparada
        [SO: llima] JUGADORA: Llimo els quatre cargols fins que la reixa s'aguanta per costum. No quedarà res que el rovell pugui soldar.
        JUGADORA: Ara, a provar la ruta de la V. abans que el Sic trobi el seu lladre. Si arribo al moll, li marcaré el camí.
        ⇒ +reixa_preparada
    • use + llima — si reixa_preparada
        JUGADORA: Ja està. Una passada més i em quedo amb la reixa a la mà.
    • use + llima — SEMPRE
        JUGADORA: Fer malbé una reixa nova? El capatàs ho veuria i em faria omplir un formulari per cada cargol.
    • look — si reixa_preparada
        JUGADORA: La reixa del conducte, amb els cargols llimats. Sembla ben cargolada. No ho està.
    • look — si iri_sap_reixa
        JUGADORA: La reixa del conducte de servei: quatre cargols d'acer. D'aquí a cent vint anys, el rovell els soldarà.
    • look — SEMPRE
        JUGADORA: Una reixa de ventilació arran de terra, amb quatre cargols d'acer. Darrere, el conducte de servei.
    • open/pull/pickUp/push/use — si reixa_preparada
        JUGADORA: Encara no. El camí ja està marcat, però no fugiré fins que la V. estigui a punt.
    • use + clau_anglesa — SEMPRE
        JUGADORA: Ben cargolada. Quatre cargols d'acer, nous de trinca. Amb la clau anglesa la desmuntaria en un minut, però què hi perdo, jo, al conducte de servei?
    • open/pull/pickUp/push/use — si té clau_anglesa (iri)
        JUGADORA: Ben cargolada. Quatre cargols d'acer, nous de trinca. Amb la clau anglesa la desmuntaria en un minut, però què hi perdo, jo, al conducte de servei?
    • open/pull/pickUp/push/use — SEMPRE
        JUGADORA: Ben cargolada. Quatre cargols d'acer, nous de trinca. La meva clau anglesa aniria de primera, però és a cent vint anys d'aquí.

```

## Sala Conducte de servei · `fabrica_conducte` (iri)

```
EN ENTRAR
    • * — si conducte_vista = 0
        JUGADORA: Primer revolt. Tres camins, i tots fan la mateixa cara.
    • * — si conducte_vista = 1
        JUGADORA: Segon revolt. Igual que el primer.
    • * — si conducte_vista = 2
        JUGADORA: Tercer revolt. O el segon un altre cop?
    • * — si conducte_vista = 3
        JUGADORA: Quart revolt. Crec.
    • * — si conducte_vista = 4
        JUGADORA: Cinquè revolt. L'últim, si la V. ha comptat bé.

ESQUERRA «passadís de l'esquerra»
    • walkTo/open/use — SEMPRE
        [SO: conducte] JUGADORA: Giro a l'esquerra.
        ⇒ acció conducte.tria, → fabrica_conducte_revolt
    • look — SEMPRE
        JUGADORA: Un passadís que gira a l'esquerra. Igual que el de la dreta. I que el del fons.

RECTE «passadís del fons»
    • walkTo/open/use — SEMPRE
        [SO: conducte] JUGADORA: Tiro recte.
        ⇒ acció conducte.tria, → fabrica_conducte_revolt
    • look — SEMPRE
        JUGADORA: El conducte continua recte, fosc i igual que els altres dos.

DRETA «passadís de la dreta»
    • walkTo/open/use — SEMPRE
        [SO: conducte] JUGADORA: Giro a la dreta.
        ⇒ acció conducte.tria, → fabrica_conducte_revolt
    • look — SEMPRE
        JUGADORA: Un passadís cap a la dreta. Si n'hi hagués dos, ho jugaria a cara o creu.

ENRERE «cap a la reixa»
    • walkTo/open/use — SEMPRE
        [SO: reixa] JUGADORA: Desfaig el camí fins a la reixa de la cambra. Ja hi tornaré.
        ⇒ conducte_pas := 0, conducte_errades := 0, conducte_vista := 0, → fabrica_cambra
    • look — SEMPRE
        JUGADORA: Per allà es torna a la reixa de la cambra.

CARTELL «cartell» — hi és si conducte_vista = 0
    • look — SEMPRE
        JUGADORA: «Conducte de servei. Prohibit fumar.» Ni fumar ni perdre's, suposo.

GUANT «guant» — hi és si conducte_vista = 1
    • look — SEMPRE
        JUGADORA: Un guant de treball, tot sol. L'altre deu ser en un altre revolt. O el seu amo.
    • pickUp — SEMPRE
        JUGADORA: Que s'hi quedi. Si el seu amo torna a buscar-lo, almenys trobarà alguna cosa.

AIXETA «aixeta» — hi és si conducte_vista = 2
    • look — SEMPRE
        JUGADORA: Una aixeta que degota. Plic. Plic. Segur que d'aquí a cent vint anys encara degota.

TASSA «tassa» — hi és si conducte_vista = 3
    • look — SEMPRE
        JUGADORA: Una tassa de llauna amb un dit de cafè fred. Algú del torn de dia ve a fer la becaina aquí dins.

FORMULARI «formulari» — hi és si conducte_vista = 4
    • look — SEMPRE
        JUGADORA: Un formulari 27-B clavat a la paret: «Sol·licitud de senyals al conducte de servei». Denegada. Per triplicat.
    • pickUp — SEMPRE
        JUGADORA: És un document oficial. Si el toco, el capatàs ho sabrà. No sé com, però ho sabrà.

```

## Sala Conducte de servei · `fabrica_conducte_revolt`

```
EN ENTRAR
    • * — si conducte_pas < 5
        ⇒ acció conducte.revolt, → fabrica_conducte
    • * — si conducte_errades = 0 i (té tub_amb_llibreta (vet) o tub_muntat)
        [SO: conducte] JUGADORA: Després del cinquè revolt... llum al fons. El moll! El pilar del 7 és allà mateix.
        [SO: llima] JUGADORA: A cada revolt hi he gravat una I. i una fletxa: si la V. passa per aquí, que sàpiga que hi vaig passar jo.
        ⇒ +ruta_marcada, conducte_pas := 0, conducte_errades := 0, conducte_vista := 0, → fabrica_moll
    • * — si conducte_errades = 0
        [SO: conducte] JUGADORA: Després del cinquè revolt... llum al fons. El moll! El pilar del 7 és allà mateix.
        [SO: llima] JUGADORA: Torno pel mateix camí i, a cada revolt, hi gravo una I. i una fletxa. La V. ja coneix la meva marca.
        JUGADORA: I soc a la cambra abans que el Sic trobi el seu lladre. Ja està, V.
        ⇒ +ruta_marcada, conducte_pas := 0, conducte_errades := 0, conducte_vista := 0, → fabrica_cambra
    • * — SEMPRE
        [SO: conducte] JUGADORA: Després del cinquè revolt... llum al fons. Una reixa.
        JUGADORA: La reixa de la meva cambra. He sortit per on he entrat. M'he perdut.
        JUGADORA: Algun revolt no era el bo. Hauré de tornar a mirar els signes del fullet de la V.
        ⇒ conducte_pas := 0, conducte_errades := 0, conducte_vista := 0, → fabrica_cambra

```

## Sala Despatx del director · `fabrica_despatx` (iri)

```
EN ENTRAR
    • * — si acte3_iniciat i NO iri_descoberta
        NARRADOR: Mentrestant, cent vint anys abans...
        NARRADOR: «Atenció, operària I. Sé què ha fet amb la meva cambra. Inspector Sic: que no hi torni a entrar.»
        JUGADORA: M'ha descobert. És clar: la cambra la va fer ell.
        ⇒ +iri_descoberta
    • * (una vegada) — SEMPRE
        JUGADORA: El despatx del Director Aldaia. De nit, sense ell, fa menys por. Una mica menys.

PORTA_MAGATZEM «magatzem»
    • open/use/walkTo — SEMPRE
        ⇒ → fabrica_magatzem

CALAIX «calaix»
    • use + imant_ferro9 — si NO planols_robats
        [SO: clac] JUGADORA: Acosto l'imant al pany... Clac. Com a la cel·la de la V., d'aquí a cent vint anys.
        JUGADORA: Plànols. Els plànols de la cambra. Me'ls emporto.
        ⇒ rep planols, +planols_robats, sospita_sic += 1
    • open/pickUp/use — si planols_robats
        JUGADORA: Buit. Els plànols ja els tinc jo.
    • open/pickUp/use — SEMPRE
        JUGADORA: Tancat. Pany M-3: s'obre amb un imant de ferro-9.
        ⇒ +iri_sap_calaix
    • look — SEMPRE
        JUGADORA: Un calaix amb pany M-3. El mateix model que la porta de la cel·la de la V.
        ⇒ +iri_sap_calaix

EXPEDIENT_SIC «expedient»
    • use + llapis — si sospita_sic ≥ 2 i NO mira_salvada
        [SO: escriure] JUGADORA: Hi escric, amb la meva lletra: «Ho vaig fer jo. La Mira no hi té res a veure. —Iri.»
        JUGADORA: Si m'han de fer desaparèixer, que no s'emportin ningú més.
        ⇒ +mira_salvada, +iri_confessada
    • look — si inventari_falsificat
        NARRADOR: «Robatoris de ferro-9: material donat de baixa per rovell. Cas arxivat. —Insp. Sic.»
        JUGADORA: S'ho ha empassat. Té més fe en els segells que en la química.
    • look — si iri_confessada
        NARRADOR: «Confessió de l'operària I. del torn de nit. Cas obert contra ella. —Insp. Sic.»
    • look — si capatas_acusat
        NARRADOR: «Sospitós principal: el capatàs Tul. Material inventariat trobat a la seva butxaca. —Insp. Sic.»
    • look — si sospita_sic ≥ 2
        NARRADOR: «Robatoris de material inventariat. Sospitosa principal: M. d'Orís, ajudant del torn de nit. Proposta: acomiadament i denúncia. —Insp. Sic.»
        JUGADORA: La Mira! La meva companya de torn. Ella no hi té res a veure: ho he fet jo.
        ⇒ +iri_sap_mira_acusada
    • look — SEMPRE
        NARRADOR: «Falten una clau anglesa i un imant de ferro-9. S'investiga el torn de nit. —Insp. Sic.»
        JUGADORA: Encara no hi ha cap nom. Encara.

LLIBRE_INVENTARI «llibre d'inventari»
    • use + segell — si sospita_sic ≥ 2 i NO mira_salvada
        [SO: escriure] JUGADORA: Hi afegeixo una línia: «Material de ferro-9 donat de baixa per rovell.»
        [SO: segell] JUGADORA: I el segell oficial a sobre. El ferro-9 no s'oxida mai, però el Sic no és químic.
        ⇒ +mira_salvada, +inventari_falsificat, sospita_sic := 0
    • look — SEMPRE
        JUGADORA: El llibre d'inventari. Tot el ferro-9 de la fàbrica, apuntat a mà, gram a gram.

RETRAT «retrat»
    • look — SEMPRE
        JUGADORA: El Director Aldaia. Somriu com qui ja sap com acaba la pel·lícula.

```

## Sala Magatzem d'eines · `fabrica_magatzem` (iri)

```
EN ENTRAR
    • * — si acte3_iniciat i NO iri_descoberta
        NARRADOR: Mentrestant, cent vint anys abans...
        NARRADOR: «Atenció, operària I. Sé què ha fet amb la meva cambra. Inspector Sic: que no hi torni a entrar.»
        JUGADORA: M'ha descobert. És clar: la cambra la va fer ell.
        ⇒ +iri_descoberta
    • * (una vegada) — si acte3_iniciat i NO mira_salvada i sospita_sic ≥ 2
        JUGADORA: La taquilla de la Mira està buida. Hi ha un paper enganxat: «Acomiadada».
        JUGADORA: La Mira ja no treballa aquí. Per culpa meva.
    • * (una vegada) — SEMPRE
        CARGOL: Bona nit, senyora Iri! Benvinguda al magatzem. Recordi: sense formulari, no hi ha material.

CARGOL «Cargol»
    • talkTo — SEMPRE
        ⇒ diàleg cargol
    • use/give + segell — si cargol_sap_revisio i NO cargol_reparat
        [SO: segell] JUGADORA: Agafo el seu formulari de revisió, ratllo «esborrar» i hi escric «permanent». I hi planto el segell oficial.
        CARGOL: Un canvi segellat pel capatàs! Doncs és oficial: no m'esborraran res.
        CARGOL: Senyora Iri... ara ho recordaré tot. També aquest moment. Sobretot aquest moment.
        CARGOL: Encara que, si algun dia em pregunten qui soc, només sabré dir el que diu la placa: «C-1».
        ⇒ +cargol_reparat, relació cargol +1
    • use/give + llima — si cargol_reparat i NO cargol_gravat
        [SO: llima] JUGADORA: Si ho ha de recordar tot, que recordi com es diu. Li gravo el nom a la placa: C-A-R-G-O-L.
        CARGOL: Un nom gravat. A la placa. Això no surt a cap norma.
        CARGOL: ...M'agrada. Cargol. Ho arxivaré a la memòria permanent. La de debò.
        ⇒ +cargol_gravat, relació cargol +1
    • use/give + llima — si NO cargol_gravat
        JUGADORA: Gravar-li alguna cosa? Per què, si l'any que ve no recordarà ni qui li ho va fer?
    • look — SEMPRE
        JUGADORA: El Cargol, robot de manteniment model C-1. Acabat d'estrenar. Brilla tant que fa mal als ulls.
        JUGADORA: Porta un paper enganxat a la carcassa: «Revisió anual C-1. Dilluns.» I el segell del capatàs. Revisió de què? ⟨si acte1_acabat i NO cargol_reparat⟩
    • give + qualsevol objecte — SEMPRE
        JUGADORA: Millor que li ho expliqui parlant. Li agraden els procediments.
        ⇒ diàleg cargol
    • push/pull — SEMPRE
        CARGOL: Senyora Iri, el contacte físic no autoritzat requereix el formulari 12-F.

PLOMALL «plomall» — hi és si no té plomall (iri)
    • look — SEMPRE
        JUGADORA: Un plomall. Per treure la pols de coses que mai no fan pols.
    • pickUp — SEMPRE
        JUGADORA: Me l'emporto.
        CARGOL: Material de neteja no inventariable. Pot procedir, senyora.
        ⇒ rep plomall

CAIXA_EINES «caixa d'eines» — hi és si no té caixa_eines (iri)
    • look — SEMPRE
        JUGADORA: Una caixa d'eines enorme. Hi ha de tot, i tot pesa.
    • pickUp — si no té caixa_eines (iri)
        JUGADORA: Uf. Nou quilos d'eines. Per si de cas.
        ⇒ rep caixa_eines

PRESTATGES «prestatges»
    • look — SEMPRE
        JUGADORA: Claus, imants, cargols... Tot de ferro-9, tot inventariat. Tot sota la mirada del Cargol.
    • pickUp — SEMPRE
        CARGOL: Senyora Iri, li recordo que sense formulari això seria un furt.

PORTA_CALDERES «sala de calderes»
    • open/use/walkTo — SEMPRE
        ⇒ → fabrica_calderes

PORTA_DESPATX «despatx del director»
    • open/use/walkTo — si NO director_fora
        JUGADORA: Hi ha llum sota la porta i se senten veus: el Director i l'Inspector Sic, reunits. No penso entrar-hi a saludar.
    • open/use/walkTo — SEMPRE
        ⇒ → fabrica_despatx

MIRA «Mira» — hi és si acte3_iniciat i mira_salvada i NO iri_fugida
    • use/give + planols — SEMPRE
        JUGADORA: Mira. Els plànols de la cambra. El Director la va fer per obrir una finestra, i va fer servir el meu torn per provar-la.
        MIRA: Ho sabia. Ho sabia que no havia estat un accident.
        JUGADORA: Jo me'n vaig. Quan jo ja no hi sigui, fes-los públics.
        MIRA: Tu marxa. Jo me n'encarrego. I Iri... gràcies per no deixar que em culpessin a mi.
        ⇒ perd planols, +planols_lliurats
    • talkTo — SEMPRE
        ⇒ diàleg mira
    • look — SEMPRE
        JUGADORA: La Mira, fent inventari de cargols. Per sort, encara treballa aquí.

```

## Sala Moll de càrrega · `fabrica_moll` (iri)

```
EN ENTRAR
    • * — si acte3_iniciat i NO iri_descoberta
        NARRADOR: Mentrestant, cent vint anys abans...
        NARRADOR: «Atenció, operària I. Sé què ha fet amb la meva cambra. Inspector Sic: que no hi torni a entrar.»
        JUGADORA: M'ha descobert. És clar: la cambra la va fer ell.
        ⇒ +iri_descoberta
    • * (una vegada) — SEMPRE
        JUGADORA: El moll de càrrega. De nit, només hi som la llançadora i jo.

DECORAT marca_pilar — es veu si marca_pilar

PORTA_CALDERES «sala de calderes»
    • open/use/walkTo — SEMPRE
        ⇒ → fabrica_calderes

BIGA_ACER «biga d'acer» — hi és si no té biga_acer (iri) i NO biga_acer_serrada i biga_amagada ≠ "acer" i NO biga_acer_enterrada
    • use + serra — si iri_sap_mida i NO marca_pilar
        JUGADORA: Abans, el pilar 7. Que la V. sàpiga que he rebut la nota i que soc aquí mateix.
    • pickUp — si iri_sap_mida i NO marca_pilar
        JUGADORA: Abans, el pilar 7. Que la V. sàpiga que he rebut la nota i que soc aquí mateix.
    • use + serra — si iri_sap_mida
        [SO: serra] JUGADORA: Dos metres en tres trams de seixanta-cinc centímetres, amb forats per cargolar-los.
        JUGADORA: Cadascun, poc menys de dos quilos. Hi passaran.
        ⇒ +biga_acer_serrada, rep tram_biga_1, rep tram_biga_2, rep tram_biga_3
    • use + serra — SEMPRE
        JUGADORA: Si la serro sense saber la mida, en faré serradures.
    • pickUp — si iri_sap_mida
        JUGADORA: Me la carrego a l'espatlla. Dos metres d'acer: fa més nosa que pes.
        ⇒ rep biga_acer
    • pickUp — si iri_sap_pany
        JUGADORA: Per a què la vull? Primer he de saber què necessita la V.
    • pickUp — SEMPRE
        JUGADORA: Una biga? Per a què la vull? Prou feina tinc amb les calderes.
    • look — SEMPRE
        JUGADORA: Una biga d'acer de dos metres, damunt dels cavallets. D'aquestes, n'hi ha a totes les naus.

BIGA_FERRO9 «biga de ferro-9» — hi és si NO biga_ferro9_robada
    • pickUp — si iri_sap_mida i NO marca_pilar
        JUGADORA: Abans, el pilar 7. Que la V. sàpiga que he rebut la nota i que soc aquí mateix.
    • pickUp — si iri_sap_mida
        JUGADORA: Ferro-9 inventariat. Si la prenc, l'Inspector Sic ho sabrà demà al matí.
        JUGADORA: I buscarà algú a qui culpar.
        JUGADORA: ...Me l'emporto.
        ⇒ rep biga_ferro9, +biga_ferro9_robada, sospita_sic += 1
    • pickUp — si iri_sap_pany
        JUGADORA: Per a què la vull? Primer he de saber què necessita la V.
    • pickUp — SEMPRE
        JUGADORA: Una biga? Per a què la vull? Prou feina tinc amb les calderes.
    • look — SEMPRE
        JUGADORA: Una biga de ferro-9 al bastidor, amb l'etiqueta: «Reservada. Caldera 4. No tocar.» No s'oxidarà mai.

SERRA «serra» — hi és si no té serra (iri)
    • pickUp — SEMPRE
        JUGADORA: La serra de metall. Les dents, noves.
        ⇒ rep serra
    • look — SEMPRE
        JUGADORA: Una serra de metall, penjada amb les eines del moll.

TRAPA «reixa del terra»
    • use + biga_acer — SEMPRE
        [SO: reixa] JUGADORA: Aixeco la reixa del costat del pilar 7 i la baixo als fonaments. Aquí no hi baixa mai ningú.
        ⇒ perd biga_acer, biga_amagada := "acer", +biga_acer_enterrada
    • use + biga_ferro9 — SEMPRE
        [SO: reixa] JUGADORA: Aixeco la reixa del costat del pilar 7 i la baixo als fonaments. Cent vint anys de paciència, biga.
        ⇒ perd biga_ferro9, biga_amagada := "ferro9"
    • open/pickUp — si biga_amagada = "acer"
        [SO: reixa] JUGADORA: Torno a pujar la biga d'acer.
        ⇒ biga_amagada := "", rep biga_acer, −biga_acer_enterrada
    • open/pickUp — si biga_amagada = "ferro9"
        JUGADORA: La biga de ferro-9 és a baix. Que s'hi quedi.
    • open/pickUp — SEMPRE
        [SO: reixa] JUGADORA: A sota de la reixa, els fonaments. Fa olor de terra i de secrets.
    • look — SEMPRE
        JUGADORA: Una reixa de desguàs, al costat del pilar 7. S'aixeca: a sota hi ha els fonaments, on baixen els que no volen que els vegi el Sic.

LLANCADORA «llançadora»
    • open/use/push/pull — si (té tub_amb_llibreta (vet) o tub_muntat) i NO iri_fugida i vet_fugida
        [SO: motor] JUGADORA: Pujo a la llançadora. És la mateixa que la V. ha arreglat al seu hangar, cent vint anys més tard. Que ens porti a totes dues.
        JUGADORA: Adéu, Director. Adéu, formulari 27-B.
        [SO: motor] JUGADORA: La comporta s'obre i la fàbrica es fa petita. Desapareguda, diran. Que ho diguin.
        ⇒ +iri_fugida, +fugida_completada, esdeveniment final
    • open/use/push/pull — si (té tub_amb_llibreta (vet) o tub_muntat) i NO iri_fugida
        [SO: motor] JUGADORA: Pujo a la llançadora. És la mateixa que la V. ha arreglat al seu hangar, cent vint anys més tard. Que ens porti a totes dues.
        JUGADORA: Adéu, Director. Adéu, formulari 27-B.
        [SO: motor] JUGADORA: La comporta s'obre i la fàbrica es fa petita. Desapareguda, diran. Que ho diguin.
        NARRADOR: Mentrestant, cent vint anys després...
        ⇒ +iri_fugida, esdeveniment protagonista
    • look — si té tub_amb_llibreta (vet) o tub_muntat
        JUGADORA: La llançadora, nova de trinca. I avui ningú no la vigila.
    • look — SEMPRE
        JUGADORA: La llançadora de càrrega, nova de trinca. Diuen que pot arribar fins a la Lluna. Diuen moltes coses.
    • open/use/push/pull — SEMPRE
        JUGADORA: Si la toco i salta una alarma, no hi haurà formulari que em salvi.

COMPORTA «comporta»
    • look — SEMPRE
        JUGADORA: La comporta del moll. S'obre amb una palanca de dos metres. Aquí, de palanques, en tenim de sobres.

LLIMA «llima» — hi és si no té llima (iri)
    • pickUp — SEMPRE
        JUGADORA: Una llima fina. Per afinar coses.
        ⇒ rep llima
    • look — SEMPRE
        JUGADORA: Una llima fina, al tauler d'eines.

CONDUCTE «conducte»
    • close — si NO iri_sap_pressio
        JUGADORA: Si la toco sense motiu, el capatàs em farà omplir formularis fins a la jubilació.
    • close — si valvula ≠ "tancada"
        [SO: valvula] JUGADORA: Tanco la vàlvula del tot.
        JUGADORA: Cent vint anys de pressió acumulant-se... n'hi haurà de sobres.
        ⇒ valvula := "tancada"
    • close — SEMPRE
        JUGADORA: Ja està tancada del tot.
    • open — si NO iri_sap_pressio
        JUGADORA: Si la toco sense motiu, el capatàs em farà omplir formularis fins a la jubilació.
    • open — si valvula = "tancada"
        [SO: valvula] JUGADORA: L'obro una mica. Ni massa ni massa poc.
        JUGADORA: Cent vint anys. Espero haver-ho calculat bé.
        [SO: altaveu] NARRADOR: Pels altaveus: «Director Aldaia a les calderes. Caiguda de pressió.» El seu despatx es quedarà buit una estona.
        ⇒ valvula := "mig", +director_fora
    • open — si valvula = "mig"
        [SO: valvula] JUGADORA: La torno a obrir del tot.
        ⇒ valvula := "oberta"
    • open — SEMPRE
        JUGADORA: Ja està oberta del tot.
    • use/push/pull — SEMPRE
        JUGADORA: Una vàlvula. S'obre i es tanca.
    • look — si valvula = "tancada"
        JUGADORA: El conducte de pressió, amb la vàlvula tancada del tot.
    • look — si valvula = "mig"
        JUGADORA: El conducte de pressió, amb la vàlvula una mica oberta.
    • look — SEMPRE
        JUGADORA: El conducte de pressió que va de les calderes cap al moll, amb una vàlvula. Per dins és de ferro-9: durarà més que tots nosaltres.

PILAR «pilar»
    • use + llima — si iri_sap_mida i NO marca_pilar
        [SO: llima] JUGADORA: Amb la llima, hi gravo una I. i una clau anglesa. Ben fondo.
        JUGADORA: Si el teu hangar és el meu moll, V., d'aquí a cent vint anys encara hi serà. Vol dir: rebut, soc aquí.
        ⇒ +marca_pilar
    • use + llima — si marca_pilar
        JUGADORA: Ja hi ha la marca. Si n'hi faig més, el capatàs pensarà que és art.
    • use + llima — SEMPRE
        JUGADORA: Gravar-hi què? Encara no tinc res a dir a ningú.
    • look — si marca_pilar
        JUGADORA: El pilar 7, amb la meva marca: una I. i una clau anglesa. Que duri.
    • look — si iri_sap_mida
        JUGADORA: Un pilar amb un 7 pintat. Com el que diu la V. És aquí mateix, cent vint anys més tard.
    • look — SEMPRE
        JUGADORA: Un pilar amb un 7 pintat. Pintura nova: aquí tot és nou.

```

## Sala L'Anell de Baix · `final_anell` — cinemàtica

```
```

## Sala El Cargol · `final_cargol` — cinemàtica

```
```

## Sala L'Estació d'Orís · `final_estacio` — cinemàtica

```
```

## Sala La llançadora · `final_llancadora` — cinemàtica

```
```

## Sala El museu · `final_museu` — cinemàtica

```
DECORAT foto_mira — es veu si mira_salvada
DECORAT conserge_cargol — es veu si cargol_memoria

```

## Sala La nota · `final_nota` — cinemàtica

```
```

## Sala Arxiu · `gavina_arxiu` (vet)

```
EN ENTRAR
    • * (una vegada) — SEMPRE
        JUGADORA: L'arxiu. Fa olor de paper vell i de secrets que algú va voler guardar.
        ⇒ +arxiu_explorat

ESCALA_HANGAR «moll de l'hangar»
    • open/use/walkTo — SEMPRE
        ⇒ → gavina_hangar

EXPEDIENT_IRI «expedients»
    • look/open/pickUp — si iri_confessada
        NARRADOR: «Corporació Aldaia · Expedient de personal. I. (el cognom, ratllat), enginyera del torn de nit. Desapareguda tres dies després de l'accident de la cambra 1. Acusada de robatori per confessió pròpia. Cas tancat per ordre del Director.»
        JUGADORA: Desapareguda tres dies després. Tres dies: el que em queda a mi.
        JUGADORA: I... És ella. És la meva I.
        ⇒ +vet_sap_desaparicio
    • look/open/pickUp — SEMPRE
        NARRADOR: «Corporació Aldaia · Expedient de personal. I. (el cognom, ratllat), enginyera del torn de nit. Desapareguda tres dies després de l'accident de la cambra 1. Cas tancat per ordre del Director.»
        JUGADORA: Desapareguda tres dies després. Tres dies: el que em queda a mi.
        JUGADORA: I... És ella. És la meva I.
        ⇒ +vet_sap_desaparicio

ARXIVADOR «arxivador»
    • open/pickUp/use — si NO carta_mos_trobada
        JUGADORA: Correspondència confiscada... a muntanyes.
        JUGADORA: «Per a la Nura, del seu pare.» La carta d'en Mos! Mai no va sortir d'aquí.
        ⇒ +carta_mos_trobada, rep carta_mos
    • open/pickUp/use — SEMPRE
        JUGADORA: Cartes que no van arribar mai. Ja tinc la que buscava.
    • look — si mira_salvada
        NARRADOR: «Mira d'Orís. Cap antecedent.» I una nota a mà, molt més nova: «La seva besneta treballa aquí, de guàrdia.»
    • look — si sospita_sic ≥ 2
        NARRADOR: «Mira d'Orís, ajudant del torn de nit. Condemnada pel robatori de ferro-9. Vint anys de treballs.»
        JUGADORA: La Mira va pagar el que va fer la I. Cent vint anys tard per arreglar-ho... o no?
    • look — SEMPRE
        JUGADORA: Arxivadors de metall: expedients, cartes confiscades, factures. Cent vint anys de paperassa.

PLANOLS «plànols»
    • look/pickUp/open — SEMPRE
        NARRADOR: «Projecte Gavina. Objectiu: reobrir la finestra de fase de la cambra 1. Mètode: sincronitzadors (interns). Pèrdues previstes: «reciclatge».»
        JUGADORA: Ens tenen aquí perquè fem de sincronitzadors. I el reciclatge és el que passa quan el camp et crema.
        JUGADORA: Jo l'he fet funcionar perquè a l'altra banda hi ha algú.
        ⇒ +vet_sap_gavina

CARPETA «carpeta caiguda» — hi és si NO nota_perduda_4
    • open/pickUp/pull/push/use — SEMPRE
        JUGADORA: Una altra nota amagada. La guardo amb les altres. ⟨si té notes_perdudes⟩
        JUGADORA: Hi ha un paper doblegat, amagat. Una nota. ⟨si no té notes_perdudes⟩
          ⇒ rep notes_perdudes
        [SO: paper] NARRADOR: «Sense número, any 80. He llegit els plànols. El camp crema els que no tenen ningú a l'altra banda. D'això en diuen reciclatge. Si llegeixes això, troba algú a l'altra banda.»
        JUGADORA: Troba algú a l'altra banda. Ja ho he fet.
        ⇒ +nota_perduda_4, notes_trobades += 1
    • look — SEMPRE
        JUGADORA: Una carpeta caiguda darrere l'arxivador. Ningú no l'ha recollida en anys.

```

## Sala Cel·la 9 · `gavina_cella` (vet)

```
EN ENTRAR
    • * (una vegada) — si té tub_amb_llibreta (vet)
        [SO: porta_preso] NARRADOR: La porta de la cel·la s'obre. La Directora torna a fer la ronda.
        DIRECTORA ALDAIA: Què t'ha arribat, interna? Una canonada? Dona-me-la.
        JUGADORA: Ni parlar-ne.
        DIRECTORA ALDAIA: MARE, avisa els guàrdies. La interna 9 ja no és reeducable.
    • * (una vegada) — si reixa_preparada i NO vet_veu_reixa
        JUGADORA: Ai. Mal de cap. Un altre reajust.
        JUGADORA: La reixa de la paret... Fa un moment era una sola peça de rovell.
        ⇒ +vet_veu_reixa
    • * (una vegada) — si ruta_marcada i reixa_oberta i NO vet_veu_fletxes
        JUGADORA: Ai. Mal de cap. Un altre reajust.
        JUGADORA: Al conducte, a cada revolt, hi ha una I. gravada i una fletxa. Fa un moment no hi eren.
        ⇒ +vet_veu_fletxes
    • * (una vegada) — SEMPRE
        NARRADOR: La Gavina. Presó orbital. Mòdul C, cel·la 9.
        [SO: altaveu] MARE: Bon dia, interna 9! Li recordem que d'aquí a tres dies serà reciclada. Que tingui una jornada plena de sentit!
        JUGADORA: Tres dies. Genial. Fantàstic. Meravellós.
        [SO: vibracio] JUGADORA: I ara, a sobre, la paret vibra.

DECORAT panell_afluixat — es veu si panell_vet_trencat i NO panell_vet_obert
DECORAT panell_obert — es veu si panell_vet_obert i NO panell_vet_reparat i NO clau_recuperada
DECORAT panell_reparat — es veu si panell_vet_reparat i NO clau_recuperada
DECORAT reixa_oberta — es veu si reixa_oberta
DECORAT panell_sincronitzat — es veu si clau_recuperada

PANELL «panell rovellat»
    • use + mapa_fuga — si acte3_iniciat i mos_distreu i NO pacte_acceptat
        [SO: tos] JUGADORA: (Tus, tus.)
        MOS: Ai... ai, el cor! Directora, crec que em reciclo tot sol!
        DIRECTORA ALDAIA: Intern! No se t'acudeixi morir-te sense formulari. MARE, el metge!
        NARRADOR: Mentre la Directora s'ajup al costat d'en Mos, la Vet posa el mapa a la cambra.
        [SO: porta_preso] DIRECTORA ALDAIA: Aquesta cel·la és un circ. MARE: quan acabi, tanca-la. La interna 9 no surt d'aquí fins al vespre.
        ⇒ +cella_tancada, acció finestra.posar
    • use + mapa_fuga — si acte3_iniciat i pacte_acceptat
        DIRECTORA ALDAIA: Què hi envies, interna?
        JUGADORA: Un fullet de la Sala de la Memòria. Que vegi que m'he reformat.
        DIRECTORA ALDAIA: Un fullet del museu del meu rebesavi. No cal girar-lo: me'l sé de memòria. La reeducació funciona.
        [SO: porta_preso] DIRECTORA ALDAIA: MARE: quan acabi, tanca la cel·la. La interna no surt d'aquí fins al vespre.
        ⇒ +cella_tancada, acció finestra.posar
    • use/push/look — si acte3_iniciat i (pacte_acceptat o mos_distreu) i no (iri a fabrica_cambra)
        JUGADORA: El panell no vibra. A l'altra banda no hi ha ningú: la I. no és a la cambra.
    • use + qualsevol objecte — si acte3_iniciat i (pacte_acceptat o mos_distreu) i NO cella_tancada
        DIRECTORA ALDAIA: Quan jo t'ho digui, interna. Ni un minut abans.
    • push/pull/pickUp/open/use — si acte3_iniciat i (pacte_acceptat o mos_distreu) i NO cella_tancada
        DIRECTORA ALDAIA: Quan jo t'ho digui, interna. Ni un minut abans.
    • use + qualsevol objecte — si acte3_iniciat i NO cella_tancada
        DIRECTORA ALDAIA: Les mans lluny del panell, interna. Ara és meu.
    • push/pull/pickUp/open/use — si acte3_iniciat i NO cella_tancada
        DIRECTORA ALDAIA: Les mans lluny del panell, interna. Ara és meu.
    • look — si NO panell_vet_trencat i finestra_armada = "iri"
        [SO: vibracio] JUGADORA: Un panell rovellat a la paret. Vibra. Com si tingués son. O ganes de molestar.
    • push/use — si NO panell_vet_trencat i finestra_armada = "iri"
        JUGADORA: Prou de vibrar!
        [SO: cop] NARRADOR: La Vet clava un cop de puny al panell.
        JUGADORA: Au, au, au!
        ⇒ +panell_vet_trencat, acció finestra.boto
    • push/use — si NO panell_vet_trencat
        JUGADORA: Au. La paret guanya. Com sempre.
    • use + clau_anglesa — si panell_vet_trencat i NO panell_vet_obert
        [SO: eina] JUGADORA: Desmunto la tapa amb la clau anglesa...
        JUGADORA: A dins hi ha una consola! Molt vella. Li falta la palanca.
        ⇒ +panell_vet_obert
    • use + clau_anglesa — si panell_vet_obert i NO panell_vet_reparat
        [SO: eina] JUGADORA: La clau anglesa al forat de la palanca... Encaixa com si l'haguessin fet a mida.
        [SO: consola] JUGADORA: Clac. La consola s'encén. Una llumeta verda. Hola, llumeta.
        JUGADORA: Darrere hi ha un buit, com una petita cambra. La clau anglesa ha vingut d'aquí?
        JUGADORA: Si algú m'ha enviat una clau, potser jo li puc enviar un missatge. Em caldrà paper i alguna cosa per escriure.
        ⇒ +panell_vet_reparat, perd clau_anglesa
    • look — si panell_vet_trencat i NO panell_vet_obert
        JUGADORA: L'he trencat. Ja no vibra. Però la tapa s'ha afluixat.
    • look — si panell_vet_obert i NO panell_vet_reparat
        JUGADORA: Una consola antiga, sense palanca. Necessito alguna cosa que hi encaixi.
    • push/use — si NO panell_vet_reparat
        JUGADORA: No fa res. Encara.
    • look — si finestra_armada = "iri"
        JUGADORA: La consola parpelleja. Algú, a l'altra banda?
    • look — si finestra_armada = "vet"
        JUGADORA: El camp està armat. Ara, que algú ho reculli. Si us plau.
    • look — SEMPRE
        JUGADORA: La consola, amb la clau anglesa de palanca. Darrere hi ha un buit, com una petita cambra.
    • use + molla — si NO molla_afinada
        JUGADORA: Encara no sona com el pany. Si l'envio així, la I. afinarà una nota equivocada.
    • use + qualsevol objecte — SEMPRE
        ⇒ acció finestra.posar
    • pickUp/open — si sincronia_automatica i panell_vet_reparat i NO clau_recuperada
        JUGADORA: Ara les coses de la I. arriben soles, sense que jo toqui res. Ja no cal la palanca.
        [SO: eina] JUGADORA: Recupero la clau anglesa.
        ⇒ +clau_recuperada, rep clau_anglesa
    • pickUp/open — SEMPRE
        ⇒ acció finestra.treure
    • push/use — SEMPRE
        ⇒ acció finestra.boto

ALTAVEU «altaveu de la MARE»
    • talkTo — SEMPRE
        ⇒ diàleg mare
    • look — SEMPRE
        JUGADORA: L'altaveu de la MARE. Té forma de cor. És el detall més sinistre de la presó.
    • push/pull/use — SEMPRE
        [SO: altaveu] MARE: Interna 9, detectem una manipulació de l'altaveu. Li enviem una abraçada virtual!

MOS «Mos»
    • give/use + nota_mos — SEMPRE
        JUGADORA: Mos. Això és teu, oi?
        MOS: On l'has trobada? La vaig amagar el primer any. Pensava que algú la llegiria i vindria a buscar-me.
        MOS: No va venir ningú. Al final, em vaig maquillar i vaig esperar.
        JUGADORA: Doncs ara l'ha llegida algú. I tenies raó: no va ser un accident.
        MOS: Ets un sol, nouvinguda. Un sol amb granota taronja.
        ⇒ perd nota_mos, +nota_mos_tornada, relació mos +1
    • give/use + carta_mos — SEMPRE
        JUGADORA: Mos, això és teu. Era a l'arxiu.
        MOS: ...La meva carta a la Nura. No va sortir mai d'aquí.
        MOS: Gràcies, noia. Et diré una cosa que fa anys que sé i no dic: als del reciclatge no els reciclen.
        MOS: Els posen davant d'una cambra vella i esperen que funcioni. Quan el camp crema, crema la persona.
        MOS: Tu l'has fet funcionar, oi? Doncs ara et voldran viva. Vés amb compte.
        ⇒ perd carta_mos, +carta_mos_lliurada, relació mos +2
    • talkTo — SEMPRE
        ⇒ diàleg mos
    • look — SEMPRE
        JUGADORA: En Mos, el meu company de cel·la. Fa vint anys que espera el reciclatge. Diu que l'han oblidat.

AVIS «avís» — hi és si NO avis_agafat
    • look — SEMPRE
        JUGADORA: Un paper que la MARE m'ha passat per sota la porta.
    • pickUp — SEMPRE
        JUGADORA: El meu avís de reciclatge. Per al meu àlbum de records.
        ⇒ rep avis_reciclatge, +avis_agafat

LLITERA «llitera»
    • pickUp/pull — si pany_sonic_sentit i NO molla_agafada
        [SO: ronc] JUGADORA: Arrenco una molla de la llitera. En Mos ni se n'adona: ronca.
        ⇒ +molla_agafada, rep molla
    • look — si NO fullet_agafat
        JUGADORA: La meva llitera. Sota el coixí hi ha un fullet de reeducació. Ideal per a quan no puc dormir.
        ⇒ +fullet_vist
    • look — si pany_sonic_sentit i NO molla_agafada
        JUGADORA: La meva llitera. Cada cop que m'hi assec, les molles fan «nnng». Com el pany de la llançadora.
        JUGADORA: I n'hi ha una que ja penja per sota el matalàs, mig deslligada. ⟨si NO molla_vista⟩
        ⇒ +molla_vista
    • look — SEMPRE
        JUGADORA: Una llitera dura com la vida mateixa.

FULLET «fullet de reeducació» — hi és si fullet_vist i NO fullet_agafat
    • look — SEMPRE
        JUGADORA: Treu el nas per sota el coixí: «La Gavina: la teva segona oportunitat!»
    • pickUp — SEMPRE
        JUGADORA: Agafo el fullet de reeducació.
        ⇒ rep fullet_reeducacio, +fullet_agafat

MOLLA «molla» — hi és si molla_vista i NO molla_agafada
    • look — SEMPRE
        JUGADORA: Una molla que penja per sota el meu matalàs. Si la toco, fa «nnng».
    • pickUp/pull — SEMPRE
        [SO: ronc] JUGADORA: Arrenco una molla de la llitera. En Mos ni se n'adona: ronca.
        ⇒ +molla_agafada, rep molla

ESCARABAT «Senyor Bigotis» — hi és si NO escarabat_agafat
    • look — SEMPRE
        JUGADORA: El Senyor Bigotis, el meu escarabat. Viu a la cantonada. Paga lloguer amb companyia.
    • pickUp — SEMPRE
        JUGADORA: Vine, Senyor Bigotis. Anem d'aventura.
        ⇒ rep escarabat, +escarabat_agafat

SAFATA «safata de sopar» — hi és si NO sopa_agafada
    • look — SEMPRE
        JUGADORA: Sopa de reinserció. Fa bombolles soles. No n'hi he vist mai cap ingredient.
    • pickUp — SEMPRE
        JUGADORA: M'emporto la sopa. Com a arma, no com a menjar.
        ⇒ rep sopa, +sopa_agafada

PORTA «porta de la cel·la»
    • open/use/walkTo/push/pull — si cella_tancada
        JUGADORA: Tancada. La MARE ha canviat el pany, i ja no em queden imants.
    • use + qualsevol objecte — si cella_tancada
        JUGADORA: Tancada. La MARE ha canviat el pany, i ja no em queden imants.
    • open/use/walkTo/push/pull — si porta_cella_oberta
        ⇒ → gavina_passadis
    • look — si porta_cella_oberta
        JUGADORA: Oberta. Gràcies a la I. i a un imant de fa cent vint anys.
    • use + imant_ferro9 — SEMPRE
        JUGADORA: Acosto l'imant al pany...
        [SO: clac] JUGADORA: Clac! Oberta! Siguis qui siguis, I., t'estimo.
        ⇒ perd imant_ferro9, +porta_cella_oberta, → gavina_passadis
    • look — si sap_que_es_temps i NO nota_pany_escrita
        JUGADORA: Un pany magnètic. Hi posa «Aldaia M-3». És més vell que en Mos.
        JUGADORA: Aldaia... Com el segell de la clau anglesa. Com la fàbrica de la I.!
        JUGADORA: Si aquest pany el van fer a la seva fàbrica, potser ella sap com obrir-lo. Li en faré un dibuix.
        ⇒ +pany_mirat
    • look — SEMPRE
        JUGADORA: Un pany magnètic. Hi posa «Aldaia M-3». És més vell que en Mos.
    • open/push/pull/use — SEMPRE
        JUGADORA: Tancada. Si s'obrís empenyent, no seria una presó.

FINESTRETA «finestreta»
    • look — SEMPRE
        JUGADORA: Per la finestreta es veu la Terra, blava i petita.
        JUGADORA: La Gavina dona voltes al planeta com una mosca pesada.

DIRECTORA «Directora Aldaia» — hi és si acte3_iniciat i (NO cella_tancada o té tub_amb_llibreta (vet))
    • talkTo — SEMPRE
        ⇒ diàleg directora
    • look — SEMPRE
        JUGADORA: La Directora Aldaia. Vestit fosc, pin d'or i un somriure que no arriba als ulls.

REIXA «reixa»
    • open/pull/pickUp/use/push — si reixa_preparada i NO reixa_oberta
        [SO: clac] JUGADORA: Els cargols cedeixen com si fossin de galeta.
        JUGADORA: A dins, a la paret del conducte, una I. gravada i una fletxa. La mateixa marca que al pilar 7. ⟨si ruta_marcada⟩
          ⇒ +vet_veu_fletxes
        JUGADORA: A dins, fosc i revolts. Però el camí me'l sé: el del mapa de la Sala de la Memòria. ⟨si NO ruta_marcada⟩
        JUGADORA: M'has obert la porta des de fa cent vint anys, I.
        ⇒ +reixa_oberta, +vet_veu_reixa
    • open/use/walkTo/pull — si reixa_oberta i té tub_amb_llibreta (vet) i vet_fugida_cella
        DIRECTORA ALDAIA: Una altra vegada? MARE! Tapieu aquest forat!
        [SO: conducte] JUGADORA: Que el tapin quan jo ja hi sigui, dins. De quatre grapes, cap a l'hangar.
        ⇒ → gavina_hangar
    • open/use/walkTo/pull — si reixa_oberta i té tub_amb_llibreta (vet)
        [SO: alarma] DIRECTORA ALDAIA: On vas? Atureu-la!
        NARRADOR: Al passadís, la Guàrdia d'Orís busca la clau de la cel·la amb una calma admirable. ⟨si mira_salvada⟩
        [SO: conducte] JUGADORA: Massa tard. Ja soc dins el conducte, seguint les fletxes de la I. ⟨si ruta_marcada⟩
        [SO: conducte] JUGADORA: Massa tard. Ja soc dins el conducte, comptant els revolts del mapa. ⟨si NO ruta_marcada⟩
        ⇒ +vet_fugida_cella, → gavina_hangar
    • open/use/walkTo/pull — si reixa_oberta
        [SO: conducte] JUGADORA: M'hi fico de quatre grapes i segueixo les fletxes de la I. fins a l'hangar. ⟨si ruta_marcada⟩
        [SO: conducte] JUGADORA: M'hi fico de quatre grapes i segueixo els revolts del mapa fins a l'hangar. ⟨si NO ruta_marcada⟩
        ⇒ → gavina_hangar
    • look — si reixa_oberta
        JUGADORA: La reixa del conducte, oberta. A dins, la I. i la fletxa. ⟨si ruta_marcada⟩
        JUGADORA: La reixa del conducte, oberta. A dins, fosc i revolts. ⟨si NO ruta_marcada⟩
        ⇒ +vet_veu_reixa
    • look — si reixa_preparada
        JUGADORA: La reixa. Els quatre cargols, llimats fins a quedar en un fil. Fa cent vint anys.
        ⇒ +vet_veu_reixa
    • look — si vet_sap_conducte
        JUGADORA: Una reixa arran de terra... El conducte de servei del mapa comença al mòdul C. Comença aquí!
        JUGADORA: Però el rovell l'ha soldada a la paret. Per aquí no surt ningú.
        ⇒ +reixa_mirada
    • use + clau_anglesa — si vet_sap_conducte
        [SO: eina] JUGADORA: Ni amb la clau anglesa. Cent vint anys de rovell fan de soldadura.
        ⇒ +reixa_mirada
    • open/pull/pickUp/push/use — si vet_sap_conducte
        JUGADORA: Soldada pel rovell. No es mou ni un pèl.
        ⇒ +reixa_mirada
    • use + clau_anglesa — SEMPRE
        [SO: eina] JUGADORA: Ni amb la clau anglesa. Cent vint anys de rovell fan de soldadura.
    • look — SEMPRE
        JUGADORA: Una reixa de ventilació arran de terra. El rovell l'ha soldada a la paret.
    • open/pull/pickUp/push/use — SEMPRE
        JUGADORA: Soldada pel rovell. No es mou ni un pèl.

ESQUERDA «esquerda» — hi és si NO nota_perduda_1
    • open/pickUp/pull/push/use — SEMPRE
        JUGADORA: Una altra nota amagada. La guardo amb les altres. ⟨si té notes_perdudes⟩
        JUGADORA: Hi ha un paper doblegat, amagat. Una nota. ⟨si no té notes_perdudes⟩
          ⇒ rep notes_perdudes
        [SO: paper] NARRADOR: «Interna 4, any 12. El panell no ha vibrat mai. Li he donat cops, li he cridat, li he escrit. A l'altra banda no hi ha ningú. Si algun dia hi és, digues-li que l'he esperada.»
        JUGADORA: Fa més de cent anys, algú altre parlava amb aquest panell. I a ella no li vibrava: no hi havia ningú a l'altra banda.
        ⇒ +nota_perduda_1, notes_trobades += 1
    • look — SEMPRE
        JUGADORA: Una esquerda a la paret, just a l'altura de la mà. Hi ha alguna cosa encastada.

```

## Sala Moll de l'hangar · `gavina_hangar` (vet)

```
EN ENTRAR
    • * (una vegada) — si valvula = "tancada"
        JUGADORA: Ai... Mal de cap. Com si m'haguessin donat la volta.
        [SO: aigua] JUGADORA: El moll està ple d'aigua! Abans estava sec. N'estic segura.
        ⇒ +vet_ha_vist_inundacio
    • * (una vegada) — si vet_ha_vist_inundacio i valvula ≠ "tancada"
        JUGADORA: Un altre mal de cap. L'aigua ha desaparegut com si no hi hagués estat mai.
        JUGADORA: Però jo me'n recordo.
    • * (una vegada) — si marca_pilar i NO vet_ha_vist_marca i vet_intueix_marca
        JUGADORA: Al pilar 7 hi ha una I. gravada, i una clau anglesa. Abans no hi era: era això, el mal de cap.
        JUGADORA: Fa cent vint anys que hi és... des de fa un minut. Rebut, I.
        ⇒ +vet_ha_vist_marca
    • * (una vegada) — si marca_pilar i NO vet_ha_vist_marca
        JUGADORA: Ai... Mal de cap. Com si m'haguessin donat la volta.
        JUGADORA: Al pilar 7 hi ha una I. gravada, i una clau anglesa. Abans no hi era. N'estic segura.
        JUGADORA: Fa cent vint anys que hi és... des de fa un minut. Rebut, I.
        ⇒ +vet_ha_vist_marca
    • * (una vegada) — SEMPRE
        JUGADORA: Un moll de càrrega. I una comporta.
        JUGADORA: Si darrere hi ha el que crec que hi ha, aquesta és la meva sortida.

DECORAT porta_llancadora — es veu si pany_sonic_obert
DECORAT aigua — es veu si valvula = "tancada"
DECORAT marca_pilar — es veu si marca_pilar

PORTA_PASSADIS «passadís»
    • open/use/walkTo — SEMPRE
        ⇒ → gavina_passadis

COMPORTA «comporta»
    • look — si comporta_oberta
        JUGADORA: Oberta. Darrere, la llançadora.
    • use + biga_ferro9 — si NO comporta_oberta
        JUGADORA: Amunt... amunt... AMUNT!
        [SO: comporta] NARRADOR: La comporta puja amb un gemec de cent vint anys.
        JUGADORA: I aquí la tenim: la llançadora de càrrega.
        JUGADORA: La porta té un pany estrany i el motor sembla mort. Bé, I., tenim feina.
        ⇒ perd biga_ferro9, +comporta_oberta
    • use + biga_muntada — si NO comporta_oberta
        JUGADORA: Amunt... amunt... AMUNT!
        [SO: comporta] NARRADOR: La comporta puja amb un gemec de cent vint anys.
        JUGADORA: I aquí la tenim: la llançadora de càrrega.
        JUGADORA: La porta té un pany estrany i el motor sembla mort. Bé, I., tenim feina.
        ⇒ perd biga_muntada, +comporta_oberta
    • use + tram_biga_1 — SEMPRE
        JUGADORA: Un tram sol no fa palanca. Me'n calen els tres, cargolats.
    • use + tram_biga_2 — SEMPRE
        JUGADORA: Un tram sol no fa palanca. Me'n calen els tres, cargolats.
    • use + tram_biga_3 — SEMPRE
        JUGADORA: Un tram sol no fa palanca. Me'n calen els tres, cargolats.
    • use + clau_anglesa — si NO comporta_mesurada
        JUGADORA: Poso la clau anglesa a l'encaix i vaig comptant...
        JUGADORA: Sis claus angleses i mitja. Com a cinta mètrica, no està malament.
        JUGADORA: La I. coneix aquesta clau. Era seva.
        ⇒ +comporta_mesurada
    • use + clau_anglesa — SEMPRE
        JUGADORA: Sis claus i mitja. No ha canviat.
    • open/push/pull — SEMPRE
        JUGADORA: No es mou ni un mil·límetre. Sense palanca, res.
    • look — SEMPRE
        JUGADORA: Una comporta enorme, encallada. Té un encaix per a una palanca molt llarga, però la palanca fa anys que no hi és.
        JUGADORA: Si la I. m'ha de fer una palanca, li hauré de dir quina mida fa l'encaix. I mesurar-lo amb alguna cosa que ella també conegui, que aquí no hi ha cap cinta mètrica. ⟨si NO comporta_mesurada⟩

PILAR «pilar»
    • look — si marca_pilar
        JUGADORA: El pilar 7. Una I. i una clau anglesa, gravades fa cent vint anys. La I. ha fet servir la paret de bústia.
    • look — SEMPRE
        JUGADORA: Un pilar amb un 7 pintat. Pintura de fàbrica: d'abans de la presó.

PLACA_TERRA «reixa del terra»
    • open/pickUp/use — si vet_sap_amagatall i biga_amagada = "ferro9" i NO biga_trobada
        JUGADORA: Aixeco la reixa i... una biga!
        JUGADORA: Cent vint anys sota terra i ni una taca. Ferro-9. Gràcies, I.
        ⇒ +biga_trobada, rep biga_ferro9
    • open/pickUp/use — si vet_sap_amagatall i biga_amagada = "acer" i NO rovell_trobat
        JUGADORA: Aixeco la reixa i... una ratlla llarga de pols vermella.
        JUGADORA: Això era una biga. Fa cent vint anys.
        JUGADORA: N'agafo un grapat. La I. ho ha de veure.
        ⇒ +rovell_trobat, rep pols_rovell
    • open/pickUp/use — si vet_sap_amagatall
        JUGADORA: A sota no hi ha res més que pols de la normal.
    • open/pickUp/use — SEMPRE
        JUGADORA: Per què hauria d'aixecar una reixa qualsevol? Totes donen al mateix forat fosc.
    • look — si vet_sap_amagatall
        JUGADORA: La reixa del costat del pilar 7. La de la nota de la I.
    • look — SEMPRE
        JUGADORA: Reixes de desguàs, encastades al terra. Totes iguals.

LLANCADORA «llançadora» — hi és si comporta_oberta
    • use + tub_amb_llibreta — SEMPRE
        [SO: paper] JUGADORA: Desenrotllo la llibreta de dins el tub. És la llibreta de torn de la I.: la cambra, el Director, les proves. Tot.
        JUGADORA: Cent vint anys d'holograma dient que va ser un accident. I aquí ho tinc, nit per nit, amb la lletra de la I. Això no ho ratllarà ningú.
        JUGADORA: Me la guardo. Quan sigui lluny, ho llegirà tothom.
        [SO: eina] JUGADORA: I munto el tub on hi havia l'altre. Ferro-9 de fa cent vint anys, nou de trinca.
        ⇒ perd tub_amb_llibreta, rep llibreta_torn, +tub_muntat
    • push/use — si tub_muntat i NO vet_fugida i iri_fugida
        [SO: motor] JUGADORA: Premo el botó d'engegada. El motor arrenca a la primera.
        [SO: comporta] JUGADORA: La comporta s'obre a l'espai. Adéu, Gavina. Adéu, MARE.
        JUGADORA: I gràcies, I. Ara et toca a tu.
        ⇒ +vet_fugida, +fugida_completada, esdeveniment final
    • push/use — si tub_muntat i NO vet_fugida
        [SO: motor] JUGADORA: Premo el botó d'engegada. El motor arrenca a la primera.
        [SO: comporta] JUGADORA: La comporta s'obre a l'espai. Adéu, Gavina. Adéu, MARE.
        JUGADORA: I gràcies, I. Ara et toca a tu.
        NARRADOR: Mentrestant, cent vint anys abans...
        ⇒ +vet_fugida, esdeveniment protagonista
    • look — si tub_muntat
        JUGADORA: La llançadora, amb el tub nou. A punt per marxar.
    • push/use — si acte3_iniciat
        [SO: boto] JUGADORA: Premo el botó d'engegada. Res. Sense el tub de la vàlvula, la pressió no arriba al motor.
        ⇒ +vet_sap_tub
    • look — si acte3_iniciat
        JUGADORA: La llançadora. On hi havia el tub de la vàlvula, un forat i una etiqueta: «Retirat per ordre de la Directora. Per si de cas.»
        ⇒ +vet_sap_tub
    • look — si motor_engegat
        JUGADORA: La llançadora ronca com en Mos. A punt per sortir.
    • push/use — si pany_sonic_obert i valvula = "mig" i NO motor_engegat
        [SO: boto] JUGADORA: Premo el botó d'engegada. L'agulla del manòmetre puja...
        [SO: motor] JUGADORA: El motor tus, s'ofega... i arrenca!
        JUGADORA: Ho tenim, I. La llançadora està a punt.
        ⇒ +motor_engegat, +components_complets
    • push/use — si motor_engegat
        JUGADORA: Ja està engegada. No la toquem, que s'ofega.
    • push/use — si pany_sonic_obert i valvula = "tancada"
        [SO: boto] JUGADORA: Premo el botó d'engegada. La pressió s'escapa pel forat del conducte. Res.
    • push/use — si pany_sonic_obert
        [SO: boto] JUGADORA: Premo el botó d'engegada. Res. L'agulla del manòmetre ni es mou: el motor no té pressió.
        JUGADORA: Del motor surt un tub que es fica dins la paret del moll. Ve de la part vella: la de la fàbrica.
        ⇒ +vet_sap_pressio
    • look — si pany_sonic_obert
        JUGADORA: La llançadora, amb la porta oberta. El motor està mort: sense pressió no anirà enlloc.
        JUGADORA: Del motor surt un tub que es fica dins la paret del moll. Ve de la part vella: la de la fàbrica.
        ⇒ +vet_sap_pressio
    • push/use/pull/open — SEMPRE
        JUGADORA: La porta no té maneta. Només aquell pany rodó, sense forat per a cap clau.
        ⇒ +pany_vist
    • look — SEMPRE
        JUGADORA: La llançadora de càrrega. Vella, coberta de pols. La porta té un pany estrany, sense forat per a cap clau.
        ⇒ +pany_vist

PANY «pany sònic» — hi és si comporta_oberta i pany_vist
    • look — si pany_sonic_obert
        JUGADORA: El pany sònic. Ara la porta està oberta.
    • use + diapaso — si diapaso_afinat i NO pany_sonic_obert
        [SO: diapaso_2] JUGADORA: Toco el diapasó i l'acosto al pany...
        [SO: clac] JUGADORA: El pany respon amb la mateixa nota. Clac!
        [SO: porta_llancadora] NARRADOR: La porta de la llançadora s'obre per primera vegada en cent vint anys.
        JUGADORA: A dins, tot està mort. El motor no té pressió. Ni una mica.
        ⇒ perd diapaso, +pany_sonic_obert
    • use + diapaso — SEMPRE
        [SO: pany_diapaso_{diapaso_to}] JUGADORA: El toco davant del pany... i res. No és ben bé la mateixa nota.
    • use + molla — si molla_afinada
        [SO: pany_molla_3] JUGADORA: La molla i el pany ja canten igual.
    • use + molla — si molla_tensio < 3
        [SO: pany_molla_{molla_tensio}] JUGADORA: La molla fa «nnng»... més greu que el pany.
    • use + molla — si molla_tensio > 3
        [SO: pany_molla_{molla_tensio}] JUGADORA: La molla fa «niiing»... més aguda que el pany.
    • use + molla — SEMPRE
        [SO: pany_molla_3] JUGADORA: Igual! La molla i el pany fan exactament la mateixa nota.
        JUGADORA: Hi lligo una tira de la granota amb un missatge, escrit amb el llapis d'ulls.
        ⇒ +molla_afinada
    • push/use/pull/open — SEMPRE
        [SO: pany] JUGADORA: Toco el pany. Fa «nnnnng». Una nota llarga, neta.
        JUGADORA: Un pany sònic: s'obre amb la mateixa nota. I jo no sé ni què és una nota.
        ⇒ +pany_sonic_sentit
    • look — SEMPRE
        JUGADORA: Un pany rodó, com un ressonador. Sense forat per a cap clau.

CONDUCTE «conducte»
    • look — si valvula = "tancada"
        JUGADORA: Rebentat. D'aquí surt tota l'aigua.
    • look — si valvula = "mig"
        JUGADORA: El conducte vibra, ple de pressió. I aguanta.
    • look — si pany_sonic_obert
        JUGADORA: Un conducte vell de la fàbrica, que va cap a la llançadora. Té un manòmetre: zero. Ni un bri de pressió.
        JUGADORA: La llançadora deu treure la pressió d'aquí. I d'on ve, això? De la part vella: de la fàbrica.
        ⇒ +vet_sap_pressio
    • look — SEMPRE
        JUGADORA: Un conducte vell de la fàbrica, que va cap a la llançadora. Té un manòmetre: zero. Ni un bri de pressió.
    • use/open/close/push/pull — SEMPRE
        JUGADORA: La vàlvula fa cent vint anys que està rovellada. Això s'ha d'arreglar al passat.

ESCALA «escala»
    • open/use/walkTo — si reixa_arxiu_oberta i valvula ≠ "tancada"
        ⇒ → gavina_arxiu
    • look — si valvula = "tancada"
        JUGADORA: L'escala del nivell de sota. Ara és una piscina.
    • look — SEMPRE
        JUGADORA: Una escala cap al nivell de sota. Al fons, una reixa amb un rètol: «ARXIU». Tancada amb una cadena cargolada a la paret.
    • open/use/walkTo — si valvula = "tancada"
        JUGADORA: Sense banyador, no.
    • use + clau_anglesa — si valvula ≠ "tancada" i NO reixa_arxiu_oberta
        [SO: eina] JUGADORA: La cadena va cargolada a una brida. I jo tinc una clau anglesa.
        [SO: eina] JUGADORA: Llesta. La reixa de l'arxiu està oberta.
        ⇒ +reixa_arxiu_oberta
    • open/use/walkTo — SEMPRE
        JUGADORA: La reixa de l'arxiu està tancada amb una cadena, cargolada a la paret. Amb les mans, no hi ha res a fer.

CAIXA_FLOTANT «caixa que sura» — hi és si valvula = "tancada" i NO caixa_agafada
    • pickUp/open — SEMPRE
        JUGADORA: La caixa ha pujat del nivell de sota amb l'aigua.
        JUGADORA: A dins, papers molls... i una fitxa de la fàbrica. Me la quedo.
        ⇒ +caixa_agafada, rep fitxa_mira
    • look — SEMPRE
        JUGADORA: Una caixa de fusta que sura. Hi posa «ARXIU · NIVELL -1».

SORTIDA_CONDUCTE «sortida del conducte» — hi és si reixa_oberta
    • open/use/walkTo/pull — SEMPRE
        [SO: conducte] JUGADORA: Torno a la cel·la pel conducte, seguint les fletxes de la I. al revés. ⟨si ruta_marcada⟩
        [SO: conducte] JUGADORA: Torno a la cel·la pel conducte, amb els revolts del mapa al revés. ⟨si NO ruta_marcada⟩
        ⇒ → gavina_cella
    • look — SEMPRE
        JUGADORA: La reixa del terra per on surt el conducte de servei. Les fletxes de la I. arriben fins aquí. ⟨si ruta_marcada⟩
        JUGADORA: La reixa del terra per on surt el conducte de servei. ⟨si NO ruta_marcada⟩

CAIXA_RECANVIS «caixa de recanvis» — hi és si NO nota_perduda_3
    • open/pickUp/pull/push/use — SEMPRE
        JUGADORA: Una altra nota amagada. La guardo amb les altres. ⟨si té notes_perdudes⟩
        JUGADORA: Hi ha un paper doblegat, amagat. Una nota. ⟨si no té notes_perdudes⟩
          ⇒ rep notes_perdudes
        [SO: paper] NARRADOR: «Interna 23, any 58. He arribat fins a l'hangar. La comporta no té palanca, el pany de la llançadora canta i el motor no té pressió. Algú hi ha tret el ferro-9 a propòsit.»
        JUGADORA: Ella també ho va intentar. Però no tenia ningú a l'altra banda.
        ⇒ +nota_perduda_3, notes_trobades += 1
    • look — SEMPRE
        JUGADORA: Una caixa de recanvis buida, rovellada. Fa anys que no s'hi recanvia res.

```

## Sala Sala de la Memòria · `gavina_memoria` (vet)

```
EN ENTRAR
    • * (una vegada) — SEMPRE
        [SO: holograma] NARRADOR: Un holograma s'encén en veure-la entrar.
        JUGADORA: La Sala de la Memòria. On la corporació explica la seva versió.

DECORAT foto_mira — es veu si mira_salvada
DECORAT placa_robot — es veu si NO vitrina_oberta

PORTA_PASSADIS «passadís»
    • open/use/walkTo — SEMPRE
        ⇒ → gavina_passadis

HOLOGRAMA «holograma del Director»
    • talkTo/use/push (una vegada) — SEMPRE
        [SO: holograma] NARRADOR: «Benvinguts a la Sala de la Memòria! Aquí va començar tot: la Fàbrica Aldaia, el ferro-9 i el somni d'un món millor.»
        NARRADOR: «Fa cent vint anys, un accident a la cambra 1 ens va ensenyar una lliçó: la ciència necessita ordre.»
        JUGADORA: Un accident. Ja.
    • talkTo/use/push (una vegada) — SEMPRE
        [SO: holograma] NARRADOR: «Els obrers de l'era de les fàbriques bevien un elixir ritual, el cafè, per resistir el torn de nit. La corporació l'hi oferia generosament.»
        CONSERGE: Inexacte. El cafè, se'l pagaven ells. Dues monedes, a la màquina del passadís.
    • talkTo/use/push (una vegada) — SEMPRE
        [SO: holograma] NARRADOR: «El fundador treballava colze a colze amb els obrers. Ho demostra el seu casc de seguretat: ni una ratlla.»
        CONSERGE: Ni una ratlla perquè no se'l va posar mai. Consta a l'inventari.
    • talkTo/use/push — SEMPRE
        [SO: holograma] NARRADOR: «Benvinguts a la Sala de la Memòria! Aquí va començar tot: la Fàbrica Aldaia, el ferro-9 i el somni d'un món millor.»
        NARRADOR: «Fa cent vint anys, un accident a la cambra 1 ens va ensenyar una lliçó: la ciència necessita ordre.»
        JUGADORA: Un accident. Ja.
    • look — SEMPRE
        JUGADORA: El Director Aldaia, en holograma. Té el mateix somriure que la Directora.

FOTO «foto del torn de nit»
    • look — si mira_salvada
        NARRADOR: Una foto del torn de nit de la fàbrica. Hi ha un robot de manteniment, nou de trinca. I una cara ratllada, amb un nom mig esborrat: «I... (desapareguda)».
        NARRADOR: Al costat, una noia somrient. A sota hi diu: «M. d'Orís».
        JUGADORA: És ella. La I. Algú li va ratllar la cara.
        JUGADORA: I la noia del costat, la M. d'Orís, somriu al costat de la I. Com una amiga.
        ⇒ +vet_veu_foto
    • look — SEMPRE
        NARRADOR: Una foto del torn de nit de la fàbrica. Hi ha un robot de manteniment, nou de trinca. I una cara ratllada, amb un nom mig esborrat: «I... (desapareguda)».
        NARRADOR: Al costat, un forat: algú en va retallar una altra persona.
        JUGADORA: És ella. La I. Algú li va ratllar la cara.
        ⇒ +vet_veu_foto

VITRINA «vitrina»
    • use + clau_vitrina — si NO vitrina_oberta
        [SO: clac] JUGADORA: Clic. La vitrina s'obre.
        JUGADORA: La clau, ja la tinc. M'emporto la placa.
        ⇒ perd clau_vitrina, rep placa_cargol, +vitrina_oberta
    • look — si vitrina_oberta
        NARRADOR: Una vitrina. El cartell diu: «Clau anglesa Lot 1, la primera peça de ferro-9 (desapareguda). Ús ritual desconegut». A dins, només l'espai buit de la clau.
        CONSERGE: Ús ritual: confirmat. La senyora Iri hi collava cargols cada nit. ⟨si cargol_memoria⟩
        CONSERGE: Correcció: és una clau anglesa. Ús: cargols. Ho he notificat quaranta-tres vegades. ⟨si NO cargol_memoria⟩
        JUGADORA: Ara ja no hi ha ni la clau ni la placa. Un museu cada vegada més honest.
    • look — si cargol_gravat
        NARRADOR: Una vitrina. El cartell diu: «Clau anglesa Lot 1, la primera peça de ferro-9 (desapareguda). Ús ritual desconegut». A dins, només l'espai buit de la clau.
        CONSERGE: Correcció: és una clau anglesa. Ús: cargols. Ho he notificat quaranta-tres vegades.
        NARRADOR: Al costat, una placa de metall: «Placa d'identificació, robot C-1. Donació anònima».
        NARRADOR: Hi ha un nom gravat a mà: «CARGOL».
        JUGADORA: Desapareguda. Ja. Era a la meva cel·la, i ara la tinc a la butxaca.
        ⇒ +placa_vista
    • look — SEMPRE
        NARRADOR: Una vitrina. El cartell diu: «Clau anglesa Lot 1, la primera peça de ferro-9 (desapareguda). Ús ritual desconegut». A dins, només l'espai buit de la clau.
        CONSERGE: Correcció: és una clau anglesa. Ús: cargols. Ho he notificat quaranta-tres vegades.
        NARRADOR: Al costat, una placa de metall: «Placa d'identificació, robot C-1. Donació anònima».
        JUGADORA: C-1. Com el conserge, que no recorda ni com es diu.
        JUGADORA: Desapareguda. Ja. Era a la meva cel·la, i ara la tinc a la butxaca.
        ⇒ +placa_vista
    • open/pickUp/use — si vitrina_oberta
        JUGADORA: Ja l'he buidada. No cal fer-ne més.
    • open/pickUp/use — SEMPRE
        JUGADORA: Tancada amb clau. Algú del personal en deu tenir la clau.
        ⇒ +placa_vista

MAPA «mapa de La Gavina»
    • look — SEMPRE
        NARRADOR: Un mapa de La Gavina, amb una estrella: «Vostè és aquí». Per sota del mòdul C hi passa una línia discontínua: «Conducte de servei de l'antiga fàbrica (en desús)».
        JUGADORA: Un conducte de servei de la fàbrica, que arriba fins a l'hangar.
        JUGADORA: Al temps de la I. encara s'hi deu poder passar. Per allà no la veuria ningú.
        JUGADORA: La línia fa cinc revolts entre el mòdul C i l'hangar. Els copiaré al fullet, amb la ruta. ⟨si NO mapa_fuga_escrit⟩
        NARRADOR: Els revolts del mapa: {ruta_conducte} ⟨si NO mapa_fuga_escrit⟩
        JUGADORA: Els cinc revolts. Els mateixos que vaig copiar al fullet. ⟨si mapa_fuga_escrit⟩
        NARRADOR: Els revolts del mapa: {ruta_conducte} ⟨si mapa_fuga_escrit⟩
        ⇒ +vet_sap_conducte

FULLETS «fullets»
    • pickUp — si no té fullet_memoria (vet)
        JUGADORA: N'agafo un. Per darrere està en blanc: hi cap un mapa.
        ⇒ +fullet_memoria_agafat, rep fullet_memoria
    • pickUp — SEMPRE
        JUGADORA: Ja en tinc un.
    • look — SEMPRE
        JUGADORA: Un expositor de fullets: «La Gavina: aquí va començar tot!» A la portada, la clau anglesa Lot 1: «objecte ritual de l'era de les fàbriques».

CARGOL_VELL «Conserge»
    • use/give + placa_cargol — si cargol_gravat
        JUGADORA: Crec que això és teu.
        [SO: consola] CONSERGE: «CARGOL»... Cargol. Em dic Cargol.
        CONSERGE: La senyora Iri. Em va segellar la memòria i em va gravar el nom amb una llima. Fa cent vint anys.
        CONSERGE: Després va desaparèixer. Tothom deia que no tornaria. Jo vaig esperar.
        CONSERGE: Vaig esperar. Era la meva feina.
        JUGADORA: Ella està bé, Cargol. Ens escrivim.
        CONSERGE: Doncs digui-li que el Cargol ho recorda tot. Tot.
        ⇒ perd placa_cargol, +cargol_memoria
    • use/give + placa_cargol — si cargol_reparat
        CONSERGE: Una placa sense nom. Em sona... Em sona molt.
        CONSERGE: Però sense nom no sé de qui és. Ho sento, interna.
    • use/give + placa_cargol — SEMPRE
        CONSERGE: Una placa de robot. No em diu res. La tornaré a la vitrina quan pugui.
    • talkTo — SEMPRE
        ⇒ diàleg cargol_vell
    • look — si cargol_memoria
        JUGADORA: El Cargol. Llueix la placa al pit com una medalla.
    • look — SEMPRE
        JUGADORA: Un robot de manteniment vell, rovellat de dalt a baix. Treu la pols de les vitrines amb un plomall.

SOCOL «sòcol de l'holograma» — hi és si NO nota_perduda_5
    • open/pickUp/pull/push/use — SEMPRE
        JUGADORA: A dins, un paper doblegat moltes vegades.
        [SO: paper] NARRADOR: «Any 100. El Director de l'holograma diu que va ser un accident. Mireu la foto del torn de nit: no va ser un accident. —M., cel·la 9»
        JUGADORA: M., cel·la 9. La meva cel·la, fa vint anys. En Mos.
        ⇒ +nota_perduda_5, notes_trobades += 1, rep nota_mos
    • look — SEMPRE
        JUGADORA: El sòcol de l'holograma. Una de les plaques està descargolada.

```

## Sala Passadís del mòdul C · `gavina_passadis` (vet)

```
EN ENTRAR
    • * (una vegada) — SEMPRE
        JUGADORA: Fora de la cel·la!
        JUGADORA: Ara només em falta sortir d'una presó orbital. Bufar i fer ampolles.
        JUGADORA: Al mòdul C no hi ha guàrdies. Als del reciclatge no ens vigila ningú: on hem d'anar, en una presó orbital?
        NARRADOR: Mentrestant, al passat, l'inventari del matí no quadra.
        NARRADOR: Falten una clau anglesa i un imant de ferro-9. L'Inspector Sic obre un expedient.
        TÍTOL: Fi de l'Acte 1
        TÍTOL: Acte 2 · El camí llarg
        ⇒ +acte1_acabat, sospita_sic += 1

CARTELL «cartell»
    • pickUp — si NO tros_cartell_agafat
        [SO: paper] JUGADORA: N'arrenco un tros del marge. Per darrere és blanc: paper de primera.
        ⇒ +tros_cartell_agafat, rep tros_cartell
    • pickUp — si té tros_cartell (vet)
        JUGADORA: Ja en tinc un tros. Primer l'he de fer servir.
    • pickUp — SEMPRE
        JUGADORA: N'arrenco un altre tros. El somriure del cartell cada vegada és més petit.
        ⇒ rep tros_cartell
    • look — SEMPRE
        JUGADORA: «RECICLATGE → Per aquí, amb un somriure!» Hi ha una fletxa i un somriure. El somriure fa por.

CAMERA_VIGILANCIA «càmera»
    • look — SEMPRE
        JUGADORA: Una càmera de vigilància. El pilot verd parpelleja. Algú dorm a l'altra banda. Espero.

PORTA_CELLA «cel·la 9»
    • open/use/walkTo — si cella_tancada
        JUGADORA: La MARE l'ha tancada. Si vull tornar a la cel·la, haurà de ser pel conducte.
    • open/use/walkTo — SEMPRE
        ⇒ → gavina_cella

PORTA_HANGAR «porta del fons»
    • open/use/walkTo — SEMPRE
        ⇒ → gavina_hangar

PORTA_MEMORIA «Sala de la Memòria»
    • open/use/walkTo — si acte3_iniciat
        ⇒ → gavina_memoria
    • open/use/walkTo — SEMPRE
        JUGADORA: Tancada. «Sala de la Memòria: visites de reeducació, els dimarts.»
    • look — SEMPRE
        JUGADORA: «SALA DE LA MEMÒRIA». Amb el mateix somriure del cartell.

GUARDIA «Guàrdia d'Orís» — hi és si mira_salvada
    • talkTo — SEMPRE
        ⇒ diàleg guardia
    • look — SEMPRE
        JUGADORA: Una guàrdia jove, amb el cabell coure. Em mira com si em conegués.

RAJOLA «rajola solta» — hi és si NO nota_perduda_2
    • open/pickUp/pull/push/use — SEMPRE
        JUGADORA: Una altra nota amagada. La guardo amb les altres. ⟨si té notes_perdudes⟩
        JUGADORA: Hi ha un paper doblegat, amagat. Una nota. ⟨si no té notes_perdudes⟩
          ⇒ rep notes_perdudes
        [SO: paper] NARRADOR: «Intern 11, any 37. Diuen que el reciclatge és un trasllat. Ningú no torna del trasllat. PD: els cartells del somriure són de paper bo. Per escriure-hi, vull dir.»
        JUGADORA: Paper bo. Ho tindré en compte.
        ⇒ +nota_perduda_2, notes_trobades += 1
    • look — SEMPRE
        JUGADORA: Una rajola del terra que balla. Algú la va aixecar abans que jo.

```

## Sala Ferro-9 · `portada`

```
```

## Sala La cambra · `proleg_cambra` — cinemàtica

```
EN ENTRAR
    • * — SEMPRE
        NARRADOR: Una nit qualsevol. Al fons de la sala de calderes, una cambra que ningú no fa servir.
        [SO: alarma] NARRADOR: I torna a saltar aquella alarma. Ningú no sap per què.
        ⇒ → fabrica_calderes

```

## Sala Cel·la 9 · `proleg_cella` — cinemàtica

```
EN ENTRAR
    • * — SEMPRE
        [SO: vibracio] NARRADOR: Mòdul C, cel·la 9. Fa dies que la paret vibra.
        [SO: vibracio] NARRADOR: Ningú no sap per què.
        ⇒ → proleg_fabrica

```

## Sala La fàbrica · `proleg_fabrica` — cinemàtica

```
EN ENTRAR
    • * — SEMPRE
        TÍTOL: Cent vint anys abans...
        NARRADOR: Aquí, la Corporació Aldaia fabrica el ferro-9: el metall que no s'oxida mai.
        NARRADOR: Un dia, l'Aldaia s'endurà les restes d'aquesta fàbrica a l'òrbita, i en farà La Gavina.
        ⇒ → proleg_cambra

```

## Sala La Gavina · `proleg_gavina` — cinemàtica

```
EN ENTRAR
    • * — SEMPRE
        [SO: vibracio] NARRADOR: La Gavina. Presó orbital.
        NARRADOR: Aquí hi tanquen els qui planten cara a la Corporació Aldaia.
        ⇒ → proleg_cella

```

## Objecte clau anglesa · `clau_anglesa`

```
• look — si juga vet
    JUGADORA: Una clau anglesa reluent, com acabada de fer. Porta un segell: «Aldaia · Ferro-9 · Lot 1».
    JUGADORA: El ferro-9 fa més d'un segle que no es fabrica. D'on dimonis ha sortit?
    JUGADORA: Ni pantalla, ni bateria, ni garantia. Pura arqueologia.
```

## Objecte formulari 27-B · `formulari_27b`

```
(sense interaccions: només el text per defecte)
```

## Objecte formulari 27-B segellat · `formulari_segellat`

```
(sense interaccions: només el text per defecte)
```

## Objecte formulari 27-B segellat per triplicat · `formulari_triplicat`

```
(sense interaccions: només el text per defecte)
```

## Objecte plomall · `plomall`

```
(sense interaccions: només el text per defecte)
```

## Objecte segell oficial · `segell`

```
• use + formulari_27b — SEMPRE
    [SO: segell] JUGADORA: Pam! Formulari 27-B segellat. Me'n sento orgullosa i tot.
    ⇒ perd formulari_27b, rep formulari_segellat
• use + formulari_segellat — SEMPRE
    [SO: segell] JUGADORA: Pam! Pam! Segellat per triplicat. Per si de cas.
    ⇒ perd formulari_segellat, rep formulari_triplicat
• use + formulari_triplicat — SEMPRE
    JUGADORA: Més segells ja seria vici.
```

## Objecte clau de la cambra · `clau_cambra`

```
(sense interaccions: només el text per defecte)
```

## Objecte llapis · `llapis`

```
• use + llibreta_torn — si iri_sap_desaparicio i NO nota_iri_nom_escrita
    JUGADORA: Si ella m'ha dit el seu nom, jo li dic el meu.
    JUGADORA: Em dic Iri. Ja ho sospitava. No penso desaparèixer.
    ⇒ +nota_iri_nom_escrita, rep nota_iri_nom
• use + llibreta_torn — si biga_amagada ≠ "" i NO nota_amagatall_escrita
    JUGADORA: Li he de dir on mirar, o cent vint anys d'espera no serviran de res.
    JUGADORA: Arrenco un full i hi apunto el pilar 7.
    ⇒ +nota_amagatall_escrita, rep nota_amagatall
• use + llibreta_torn — si nota_vet_llegida i NO nota_iri_escrita
    [SO: escriure] JUGADORA: Arrenco un full de la llibreta i escric una resposta.
    JUGADORA: Si això és una broma del torn de dia, és molt elaborada.
    ⇒ +nota_iri_escrita, rep nota_iri
• use + llibreta_torn — SEMPRE
    JUGADORA: No tinc res a apuntar. El torn de nit és així.
```

## Objecte llibreta de torn · `llibreta_torn`

```
• look — si juga vet
    [SO: paper] JUGADORA: La llibreta de torn de la I. Les primeres pàgines: «Torn de nit. Res.» «Torn de nit. Res.» «Torn de nit. Una alarma.»
    JUGADORA: Després ja no hi ha cap «res»: la cambra, el Director, la Mira... i jo.
    JUGADORA: Paper de veritat, escrit a mà amb llapis. Aquí dalt, això aniria a una vitrina.
    JUGADORA: I a l'última pàgina, un glossari de la meva manera de parlar. «Fer òrbita: ?» Vol dir enrotllar-se, I. Com tu ara. ⟨si iri_sap_pany⟩
• look — si juga iri
    [SO: paper] JUGADORA: La meva llibreta de torn. Fins fa tres nits: «Torn de nit. Res.»
    JUGADORA: Ara hi ha l'alarma i la cambra. Tot amb data i amb la meva lletra. ⟨si NO iri_sap_pany⟩
    JUGADORA: Ara hi ha l'alarma, la cambra i les notes de la V. Tot amb data i amb la meva lletra. ⟨si iri_sap_pany⟩
    JUGADORA: A l'última pàgina, un glossari: «Brutal-plus: molt bona. Fer òrbita: ? Filtre: moneda?» ⟨si iri_sap_pany i NO iri_sap_diapaso⟩
    JUGADORA: A l'última pàgina, un glossari: «Brutal-plus: molt bona. Fer òrbita: ? Filtre: moneda? Zero-g: ?» ⟨si iri_sap_diapaso i NO iri_sap_massa⟩
    JUGADORA: A l'última pàgina, el glossari: «Brutal-plus: molt bona. Fer òrbita: ? Filtre: moneda? Zero-g: tranquil·la (vegeu «MASSA»).» ⟨si iri_sap_massa⟩
    JUGADORA: I hi he copiat els plànols: «Prova de camp: torn de nit, operària I.» ⟨si planols_robats⟩
    JUGADORA: Si jo desaparec, això és l'única cosa que dirà la veritat. Ha d'arribar a la V. ⟨si iri_sap_tub⟩
```

## Objecte caixa d'eines · `caixa_eines`

```
(sense interaccions: només el text per defecte)
```

## Objecte imant de ferro-9 · `imant_ferro9`

```
• look — si juga vet
    JUGADORA: Un imant de ferro-9: obre els panys M-3. Sense bateria. A l'època de la I. tot funcionava per fe.
```

## Objecte nota d'I. · `nota_iri`

```
• look — si juga vet i NO sap_que_es_temps
    NARRADOR: «Hola, la de la cel·la 9. Aquí és la fàbrica de ferro-9 de la Corporació Aldaia, i jo en soc l'enginyera del torn de nit. No hi ha cap cel·la. Què vol dir "brutal-plus"? I què vol dir que et reciclen? —I.»
    JUGADORA: La fàbrica Aldaia? Va tancar fa cent vint anys. Ho diuen tots els fullets de reeducació.
    JUGADORA: ...
    JUGADORA: Oh. Oh, no. Oh, sí!
    NARRADOR: Durant una hora, la cambra no para d'espetegar.
    NARRADOR: «"Brutal-plus" vol dir que ets molt bona. "Reciclar" no ho sé: ningú no en torna. Pregunta rara, i no facis òrbita: què veus per la finestra? —La de la cel·la 9»
    NARRADOR: «Xemeneies, fum i el canal. Com cada nit. «Fer òrbita»? Aquí només en fan les arnes, al fanal. I torna'm la clau anglesa, que és la meva preferida. —I.»
    NARRADOR: «Per la meva finestra hi ha estrelles, i la Terra, petita i blava. La Gavina dona voltes al món. I la teva clau porta un segell: "Aldaia · Ferro-9 · Lot 1". Aquest metall fa cent vint anys que no es fabrica: aquí dalt és tan de rovell que la posarien en un museu. —La de la cel·la 9»
    NARRADOR: «... —I.»
    JUGADORA: Un full en blanc i tres punts. Ja ho ha entès.
    JUGADORA: Una enginyera de fa cent vint anys que em pot fer arribar coses. I a mi em queden tres dies.
    ⇒ +sap_que_es_temps, enceses_restants −= 4, transferencies += 4
• look — SEMPRE
    NARRADOR: «Hola, la de la cel·la 9. Aquí és la fàbrica de ferro-9 de la Corporació Aldaia, i jo en soc l'enginyera del torn de nit. No hi ha cap cel·la. Què vol dir "brutal-plus"? I què vol dir que et reciclen? —I.»
```

## Objecte avís de reciclatge · `avis_reciclatge`

```
• look — SEMPRE
    NARRADOR: «AVÍS: La interna de la cel·la 9 (motiu de l'internament: sostracció de 40 filtres d'aire, propietat de la Corporació Aldaia) serà reciclada d'aquí a 3 dies. El reciclatge és una oportunitat! Amb afecte, MARE.»
```

## Objecte llapis d'ulls · `llapis_ulls`

```
• use + fullet_memoria — si vet_sap_conducte i reixa_mirada i NO mapa_fuga_escrit i vet_sap_tub
    [SO: escriure] JUGADORA: Hi dibuixo la ruta: de la reixa de la cambra fins al moll, pel conducte. I els cinc revolts del mapa, un signe per revolt.
    JUGADORA: I una postdata. La més important.
    ⇒ +mapa_fuga_escrit, perd fullet_memoria, rep mapa_fuga
• use + fullet_memoria — si vet_sap_conducte i reixa_mirada
    JUGADORA: Abans de dibuixar res, vull saber què em vol la Directora.
• use + fullet_memoria — si vet_sap_conducte
    JUGADORA: El conducte comença al mòdul C. Però on, exactament? Abans de dibuixar-lo, el vull veure.
• use + tros_cartell — si vet_sap_desaparicio i NO nota_vet_nom_escrita
    [SO: escriure] JUGADORA: Aquesta vegada, la signo amb el meu nom.
    JUGADORA: Em dic Vet. Et faran desaparèixer d'aquí a tres dies. Ho sento.
    ⇒ +nota_vet_nom_escrita, perd tros_cartell, rep nota_vet_nom
• use + tros_cartell — si comporta_mesurada i NO nota_mida_escrita
    [SO: escriure] JUGADORA: Hi escric la mida, ben gran. I que hi ha una comporta. I que la necessito.
    ⇒ +nota_mida_escrita, perd tros_cartell, rep nota_mida
• use + tros_cartell — si vet_sap_pressio i NO nota_pressio_escrita
    [SO: escriure] JUGADORA: Hi escric el del conducte i la pressió. Amb la meva millor lletra, que no és gaire bona.
    ⇒ +nota_pressio_escrita, perd tros_cartell, rep nota_pressio
• use + tros_cartell — si vet_ha_vist_inundacio i valvula = "tancada" i NO nota_massa_escrita
    [SO: escriure] JUGADORA: MASSA. Amb tres exclamacions. I que afluixi.
    ⇒ +nota_massa_escrita, perd tros_cartell, rep nota_massa
• use + tros_cartell — SEMPRE
    JUGADORA: Podria escriure-hi. Però què? Primer he de saber què necessito.
• use + avis_reciclatge — si panell_vet_reparat
    [SO: escriure] JUGADORA: Escric pel darrere de l'avís. Amb llapis d'ulls. Molt professional.
    ⇒ +nota_vet_escrita, perd avis_reciclatge, rep nota_vet
• use + avis_reciclatge — SEMPRE
    JUGADORA: Podria escriure-hi alguna cosa. Però a qui?
• use + fullet_reeducacio — si sap_que_es_temps i pany_mirat
    [SO: escriure] JUGADORA: Dibuixo el pany de la porta. I escric què em passa. Breu: no hi ha gaire espai.
    JUGADORA: La de l'altra banda viu en una fàbrica. Potser coneix aquest pany.
    ⇒ +nota_pany_escrita, perd fullet_reeducacio, rep nota_pany
• use + fullet_reeducacio — SEMPRE
    JUGADORA: Podria pintar bigotis al Director Aldaia de la portada. Ho apunto per a més tard.
```

## Objecte nota de la cel·la 9 · `nota_vet`

```
• look — si juga iri
    NARRADOR: «Ei, qui ets?? Soc a la cel·la 9 de La Gavina. Gràcies per la clau, ets brutal-plus. Però no entenc res. Ajuda'm, d'aquí a 3 dies em reciclen. —La de la cel·la 9»
    JUGADORA: «Brutal-plus»? «La Gavina»? «Reciclen»?
    JUGADORA: No hi ha cap cel·la a la fàbrica. Ni cap gavina. Aquí no hi ha ni ocells.
    ⇒ +nota_vet_llegida
• look — SEMPRE
    NARRADOR: «Ei, qui ets?? Soc a la cel·la 9 de La Gavina. Gràcies per la clau, ets brutal-plus. Però no entenc res. Ajuda'm, d'aquí a 3 dies em reciclen. —La de la cel·la 9»
```

## Objecte fullet de reeducació · `fullet_reeducacio`

```
(sense interaccions: només el text per defecte)
```

## Objecte dibuix del pany · `nota_pany`

```
• look — si juga iri
    NARRADOR: «I.: Necessito sortir de la cel·la. El pany és com el del dibuix, hi posa "Aldaia M-3". Si és de la teva fàbrica, saps obrir-lo? Et deuré un filtre. —V.»
    JUGADORA: «V.» Ara ella també signa amb una lletra. I cent vint anys després, encara fan servir els nostres panys.
    JUGADORA: Però aquest dibuix... És un M-3! N'hi ha a tota la fàbrica. S'obren amb un imant de ferro-9.
    JUGADORA: «Et deuré un filtre.» Un filtre de què? Si és de cafè, accepto.
    ⇒ +iri_sap_pany
• look — SEMPRE
    NARRADOR: «I.: Necessito sortir de la cel·la. El pany és com el del dibuix, hi posa "Aldaia M-3". Si és de la teva fàbrica, saps obrir-lo? Et deuré un filtre. —V.»
```

## Objecte escarabat · `escarabat`

```
• look — SEMPRE
    JUGADORA: El Senyor Bigotis. No té bigotis. És un nom aspiracional.
• talkTo — SEMPRE
    JUGADORA: Tranquil, Senyor Bigotis. A tu no et reciclaran. Ets massa petit.
```

## Objecte sopa · `sopa`

```
(sense interaccions: només el text per defecte)
```

## Objecte tros de cartell · `tros_cartell`

```
(sense interaccions: només el text per defecte)
```

## Objecte nota de la mida · `nota_mida`

```
• look — si juga iri
    NARRADOR: «I.: per sortir d'aquí he d'obrir la comporta de l'hangar, i la palanca fa anys que no hi és. L'encaix fa sis claus angleses i mitja de llarg. La teva clau, la del segell. No tinc res més per mesurar: aquí dalt, els metres són de rovell. Soc al costat d'un pilar amb un 7 pintat, per si et diu alguna cosa. —V.»
    JUGADORA: Sis claus i mitja. Una clau Lot 1 fa trenta centímetres...
    JUGADORA: Uns dos metres de biga. Per una finestra on no hi passa res de més de dos quilos.
    JUGADORA: «Els metres són de rovell.» D'aquí a cent vint anys es mesura en claus angleses. Progrés.
    JUGADORA: Un pilar amb un 7 pintat. Al moll de la fàbrica, els pilars van numerats així.
    JUGADORA: Si la V. és al costat del meu pilar 7, cent vint anys més tard, el que jo hi deixi ella ho podria trobar. La biga, per exemple.
    JUGADORA: Però primer, que sàpiga que l'he rebuda, i sense gastar cap enviament. Una marca al pilar, gravada ben fonda: si dura cent vint anys, la V. la veurà. Vol dir: rebut, soc aquí.
    ⇒ +iri_sap_mida
• look — SEMPRE
    NARRADOR: «I.: per sortir d'aquí he d'obrir la comporta de l'hangar, i la palanca fa anys que no hi és. L'encaix fa sis claus angleses i mitja de llarg. La teva clau, la del segell. No tinc res més per mesurar: aquí dalt, els metres són de rovell. Soc al costat d'un pilar amb un 7 pintat, per si et diu alguna cosa. —V.»
```

## Objecte biga d'acer · `biga_acer`

```
(sense interaccions: només el text per defecte)
```

## Objecte biga de ferro-9 · `biga_ferro9`

```
(sense interaccions: només el text per defecte)
```

## Objecte serra · `serra`

```
• use + biga_acer — si iri_sap_mida
    [SO: serra] JUGADORA: Dos metres en tres trams de seixanta-cinc centímetres, amb forats per cargolar-los.
    JUGADORA: Cadascun, poc menys de dos quilos. Hi passaran.
    ⇒ perd biga_acer, +biga_acer_serrada, rep tram_biga_1, rep tram_biga_2, rep tram_biga_3
• use + biga_acer — SEMPRE
    JUGADORA: Si la serro sense saber la mida, en faré serradures.
```

## Objecte tram de biga (1) · `tram_biga_1`

```
• use + tram_biga_2 — si té tram_biga_3 (vet)
    [SO: eina] JUGADORA: Encaixo els tres trams i hi passo els cargols.
    JUGADORA: Una biga de dos metres. Aguantarà. Segur. Probablement.
    ⇒ perd tram_biga_1 (vet), perd tram_biga_2 (vet), perd tram_biga_3 (vet), +biga_muntada_feta, rep biga_muntada (vet)
• use + tram_biga_2 — si juga iri
    JUGADORA: Si els encaixo, la biga ja no passarà per la finestra. Millor d'un en un.
• use + tram_biga_2 — SEMPRE
    JUGADORA: Encaixen, però me'n falta un. La I. els envia d'un en un.
• use + tram_biga_3 — si té tram_biga_2 (vet)
    [SO: eina] JUGADORA: Encaixo els tres trams i hi passo els cargols.
    JUGADORA: Una biga de dos metres. Aguantarà. Segur. Probablement.
    ⇒ perd tram_biga_1 (vet), perd tram_biga_2 (vet), perd tram_biga_3 (vet), +biga_muntada_feta, rep biga_muntada (vet)
• use + tram_biga_3 — si juga iri
    JUGADORA: Si els encaixo, la biga ja no passarà per la finestra. Millor d'un en un.
• use + tram_biga_3 — SEMPRE
    JUGADORA: Encaixen, però me'n falta un. La I. els envia d'un en un.
```

## Objecte tram de biga (2) · `tram_biga_2`

```
• use + tram_biga_3 — si té tram_biga_1 (vet)
    [SO: eina] JUGADORA: Encaixo els tres trams i hi passo els cargols.
    JUGADORA: Una biga de dos metres. Aguantarà. Segur. Probablement.
    ⇒ perd tram_biga_1 (vet), perd tram_biga_2 (vet), perd tram_biga_3 (vet), +biga_muntada_feta, rep biga_muntada (vet)
• use + tram_biga_3 — si juga iri
    JUGADORA: Si els encaixo, la biga ja no passarà per la finestra. Millor d'un en un.
• use + tram_biga_3 — SEMPRE
    JUGADORA: Encaixen, però me'n falta un. La I. els envia d'un en un.
```

## Objecte tram de biga (3) · `tram_biga_3`

```
(sense interaccions: només el text per defecte)
```

## Objecte biga muntada · `biga_muntada`

```
(sense interaccions: només el text per defecte)
```

## Objecte nota del moll · `nota_amagatall`

```
• look — si juga vet
    NARRADOR: «V.: no hi cap per la finestra, així que l'he amagada als fonaments del moll, al costat del pilar on et vaig gravar la I. Aixeca la reixa del terra que hi ha al costat. —I.»
    JUGADORA: El pilar 7. És aquí mateix, al moll de l'hangar!
    ⇒ +vet_sap_amagatall
• look — SEMPRE
    NARRADOR: «V.: no hi cap per la finestra, així que l'he amagada als fonaments del moll, al costat del pilar on et vaig gravar la I. Aixeca la reixa del terra que hi ha al costat. —I.»
```

## Objecte pols de rovell · `pols_rovell`

```
• look — si juga iri
    JUGADORA: Pols de rovell. La meva biga...
    JUGADORA: Clar: l'acer no aguanta cent vint anys sota terra. O ferro-9, o a trossos per la finestra.
    ⇒ +iri_sap_rovell
```

## Objecte molla · `molla`

```
• pull/push — si molla_afinada
    [SO: molla_3] JUGADORA: Ara que sona com el pany, no la toco ni per riure.
• pull — si molla_tensio ≥ 5
    [SO: molla_5] JUGADORA: Si l'estiro més, es trenca.
• pull — SEMPRE
    [SO: molla_{molla_tensio}] JUGADORA: L'estiro una mica.
    ⇒ molla_tensio += 1
• push — si molla_tensio ≤ 0
    [SO: molla_0] JUGADORA: Més arronsada no pot estar.
• push — SEMPRE
    [SO: molla_{molla_tensio}] JUGADORA: L'arronso una mica.
    ⇒ molla_tensio −= 1
• look — si juga iri i molla_afinada
    NARRADOR: Una molla de llit, amb una tira de tela lligada.
    NARRADOR: «I.: fes-me una cosa de ferro-9 que soni EXACTAMENT com aquesta molla. És per obrir un pany. No la toquis, que està afinada. I zero-g, eh. —V.»
    JUGADORA: Una nota dins d'una molla. Necessito un diapasó de ferro-9 que soni igual.
    JUGADORA: «Zero-g.» Ho apunto al costat de «brutal-plus». Començo a tenir un diccionari.
    ⇒ +iri_sap_diapaso
• look — si molla_afinada
    JUGADORA: La molla afinada, amb el missatge per a la I.
```

## Objecte llima · `llima`

```
• use + diapaso — si diapaso_to ≥ 2 o diapaso_afinat
    [SO: llima] JUGADORA: Una passada més, per si de cas...
    [SO: diapaso_xiulet] JUGADORA: Massa! Ara xiula com una tetera. Aquest diapasó ja no serveix.
    ⇒ perd diapaso, rep diapaso_espatllat, −diapaso_afinat, diapaso_to := 0
• use + diapaso — SEMPRE
    [SO: llima] JUGADORA: Llimo les puntes amb compte. Ara sona una mica més agut.
    ⇒ diapaso_to += 1
```

## Objecte diapasó · `diapaso`

```
• use + molla — si diapaso_afinat
    [SO: molla_diapaso_2] JUGADORA: El diapasó i la molla ja sonen igual.
• use + molla — si diapaso_to < 2
    [SO: molla_diapaso_{diapaso_to}] JUGADORA: Toco el diapasó i la molla. El diapasó és més greu.
• use + molla — SEMPRE
    [SO: molla_diapaso_2] JUGADORA: Toco el diapasó i la molla... la mateixa nota.
    JUGADORA: Afinat. Que no se m'acudeixi tornar-lo a llimar.
    ⇒ +diapaso_afinat
• look — si juga vet i diapaso_afinat
    JUGADORA: El diapasó de la I. Fa la mateixa nota que la meva molla. I que el pany de la llançadora, espero.
• look — si diapaso_afinat
    JUGADORA: Un diapasó de ferro-9, afinat com la molla de la V.
```

## Objecte diapasó espatllat · `diapaso_espatllat`

```
(sense interaccions: només el text per defecte)
```

## Objecte nota de la pressió · `nota_pressio`

```
• look — si juga iri
    NARRADOR: «I.: la llançadora engega amb pressió, i li arriba per un conducte vell de la fàbrica, el que passa per la paret del moll. Està buit. Pots fer-hi alguna cosa, des d'allà? Ja et dec dos filtres. —V.»
    JUGADORA: El conducte de pressió del moll. Si el tapo ara, cent vint anys de pressió s'hi aniran acumulant...
    JUGADORA: I ja li he fet guanyar dos filtres. El deute creix, i encara no sé en quina moneda.
    ⇒ +iri_sap_pressio
• look — SEMPRE
    NARRADOR: «I.: la llançadora engega amb pressió, i li arriba per un conducte vell de la fàbrica, el que passa per la paret del moll. Està buit. Pots fer-hi alguna cosa, des d'allà? Ja et dec dos filtres. —V.»
```

## Objecte nota «MASSA» · `nota_massa`

```
• look — si juga iri
    NARRADOR: «MASSA!!! El conducte ha rebentat i el nivell de sota és una piscina. AFLUIXA. Gens zero-g. —V.»
    JUGADORA: Massa pressió. Cent vint anys és molt de temps.
    JUGADORA: «Gens zero-g.» Ara ja sé què vol dir zero-g.
    JUGADORA: L'he d'obrir una mica. Només una mica.
    ⇒ +iri_sap_massa
• look — SEMPRE
    NARRADOR: «MASSA!!! El conducte ha rebentat i el nivell de sota és una piscina. AFLUIXA. Gens zero-g. —V.»
```

## Objecte fitxa de personal · `fitxa_mira`

```
• look — si sospita_sic ≥ 2 i NO mira_salvada
    NARRADOR: «Corporació Aldaia · Ferro-9 · Fitxa de personal. Mira d'Orís, ajudant de torn de nit. Observacions: acusada del robatori de material inventariat. Acomiadada.»
    JUGADORA: Acomiadada per robatori... Torn de nit, com la I. Què hi va passar, aquí?
    ⇒ +vet_coneix_mira, +vet_va_veure_mira_acusada
• look — si vet_va_veure_mira_acusada i mira_salvada i NO vet_veu_mira_salvada
    NARRADOR: «Corporació Aldaia · Ferro-9 · Fitxa de personal. Mira d'Orís, ajudant de torn de nit. Observacions: cap.»
    JUGADORA: Ai. Mal de cap. Abans hi deia «acomiadada per robatori». N'estic segura.
    JUGADORA: Ara no hi diu res. La I. hi ha fet alguna cosa, des de l'altra banda.
    ⇒ +vet_coneix_mira, +vet_veu_mira_salvada
• look — SEMPRE
    NARRADOR: «Corporació Aldaia · Ferro-9 · Fitxa de personal. Mira d'Orís, ajudant de torn de nit. Observacions: cap.»
    JUGADORA: Mira d'Orís. Torn de nit, com la I. Potser es coneixen.
    ⇒ +vet_coneix_mira
```

## Objecte plànols · `planols`

```
• look — SEMPRE
    NARRADOR: «Cambra de ressonància 1. Finalitat: obrir una finestra de fase. Prova de camp: torn de nit, operària I. No informar l'operària. —Dir. Aldaia.»
    JUGADORA: No va ser un accident. Va construir la cambra per a això, i em va triar a mi.
    JUGADORA: La Mira, la meva companya de torn, i jo ho podríem fer públic. Algun dia.
    ⇒ +iri_sap_cambra
```

## Objecte carta d'en Mos · `carta_mos`

```
(sense interaccions: només el text per defecte)
```

## Objecte nota de la Vet · `nota_vet_nom`

```
• look — si juga iri
    NARRADOR: «Em dic Vet. Et faran desaparèixer d'aquí a tres dies. Ho sento.»
    JUGADORA: Vet. Es diu Vet.
    JUGADORA: Desaparèixer... He vist els plànols del Director. Ja sé qui. ⟨si planols_robats⟩
    JUGADORA: Desaparèixer... Aquí només hi ha una persona que pugui fer desaparèixer algú: el Director. ⟨si NO planols_robats⟩
    ⇒ +iri_sap_desaparicio
• look — SEMPRE
    NARRADOR: «Em dic Vet. Et faran desaparèixer d'aquí a tres dies. Ho sento.»
```

## Objecte nota de l'Iri · `nota_iri_nom`

```
• look — si juga vet i NO acte2_noms
    NARRADOR: «Em dic Iri. Ja ho sospitava. No penso desaparèixer.»
    JUGADORA: Iri.
    TÍTOL: Fi de l'Acte 2
    TÍTOL: Acte 3 · La finestra
    MARE: Bon dia, interna 9! Bones notícies: el seu reciclatge s'avança a avui!
    MARE: I abans, visita de reeducació obligatòria a la Sala de la Memòria. Hi ha galetes!
    DIRECTORA ALDAIA: No tan de pressa, MARE. Abans, la interna i jo hem de parlar.
    ⇒ +acte2_noms, +acte2_acabat, +acte3_iniciat
• look — si juga vet
    NARRADOR: «Em dic Iri. Ja ho sospitava. No penso desaparèixer.»
    JUGADORA: Iri.
• look — SEMPRE
    NARRADOR: «Em dic Iri. Ja ho sospitava. No penso desaparèixer.»
```

## Objecte fullet de la Sala de la Memòria · `fullet_memoria`

```
(sense interaccions: només el text per defecte)
```

## Objecte mapa de fuga · `mapa_fuga`

```
• look — si a fabrica_conducte
    JUGADORA: El fullet de la V.: un signe per revolt. La fletxa amunt vol dir recte.
    NARRADOR: {ruta_conducte}   (↑ = recte)
• look — si juga iri
    JUGADORA: Per davant, el fullet d'un museu. Hi surt la meva clau anglesa: «objecte ritual de l'era de les fàbriques». És una clau anglesa.
    NARRADOR: «I.: per fugir, el conducte de servei. Comença a la reixa de la paret de la teva cambra i baixa fins al moll. Cinc revolts, un signe per revolt:
    NARRADOR: {ruta_conducte}   (↑ = recte)
    NARRADOR: El Director no hi vigila. PD: al meu temps, aquesta reixa és una sola peça de rovell, i jo també n'he de sortir. Fes que s'obri d'aquí a cent vint anys. PD 2: la Directora ha fet treure el tub de la vàlvula de la llançadora, i sense no engega. Si me'n fas un, que sigui l'últim enviament. —V.»
    JUGADORA: Una ruta per fugir. I la V. també la necessita.
    JUGADORA: La reixa té quatre cargols d'acer. En cent vint anys, el rovell els soldarà.
    JUGADORA: Si els llimo fins que s'aguantin per un fil, no hi quedarà res per soldar.
    JUGADORA: I un tub de vàlvula per a la llançadora. De ferro-9, com les peces que li van arrencar.
    JUGADORA: L'últim enviament. Després jo desapareixeré, d'una manera o d'una altra, i aquí el Director explicarà el que vulgui. Ningú no el contradirà.
    JUGADORA: Però el que passa per la cambra arriba intacte a l'altra banda. La meva llibreta de torn ho té tot apuntat: si l'envio amb el tub, la V. tindrà les proves, i allà no les podrà fer desaparèixer ningú.
    ⇒ +iri_sap_reixa, +iri_sap_tub
• look — SEMPRE
    NARRADOR: «I.: per fugir, el conducte de servei. Comença a la reixa de la paret de la teva cambra i baixa fins al moll. Cinc revolts, un signe per revolt:
    NARRADOR: {ruta_conducte}   (↑ = recte)
    NARRADOR: El Director no hi vigila. PD: al meu temps, aquesta reixa és una sola peça de rovell, i jo també n'he de sortir. Fes que s'obri d'aquí a cent vint anys. PD 2: la Directora ha fet treure el tub de la vàlvula de la llançadora, i sense no engega. Si me'n fas un, que sigui l'últim enviament. —V.»
```

## Objecte tub de ferro-9 · `tub_ferro9`

```
• use + llibreta_torn — SEMPRE
    [SO: paper] JUGADORA: Enrotllo la llibreta de torn i la fico dins el tub. Hi he apuntat tot: la cambra, el Director, les notes de la V.
    JUGADORA: Un sol objecte, d'un quilo i mig. Hi passarà.
    ⇒ perd tub_ferro9, perd llibreta_torn, rep tub_amb_llibreta
```

## Objecte tub amb la llibreta · `tub_amb_llibreta`

```
• look — si juga vet i a gavina_cella
    JUGADORA: Un tub de vàlvula, nou. I a dins hi ha alguna cosa enrotllada.
    JUGADORA: Ja ho miraré a l'hangar. Aquí la Directora no em treu els ulls de sobre.
• look — si juga vet
    JUGADORA: Un tub de vàlvula, nou. I a dins hi ha alguna cosa enrotllada.
    JUGADORA: És el tub que li falta a la llançadora! El que hi ha a dins, ho trauré quan el munti.
```

## Objecte clau de la vitrina · `clau_vitrina`

```
(sense interaccions: només el text per defecte)
```

## Objecte placa de robot · `placa_cargol`

```
• look — si cargol_gravat
    NARRADOR: «Robot de manteniment C-1. Corporació Aldaia.»
    NARRADOR: Sota, gravat a mà amb una llima, un nom: «CARGOL».
    JUGADORA: Algú li va voler deixar el nom per escrit. Algú amb una llima.
• look — SEMPRE
    NARRADOR: «Robot de manteniment C-1. Corporació Aldaia.»
    JUGADORA: No hi ha cap nom. És la placa d'un robot sense nom.
```

## Objecte formulari 27-B/E · `formulari_27be`

```
(sense interaccions: només el text per defecte)
```

## Objecte formulari 27-B/E signat · `formulari_27be_signat`

```
(sense interaccions: només el text per defecte)
```

## Objecte carnet d'usuària exemplar · `carnet_exemplar`

```
(sense interaccions: només el text per defecte)
```

## Objecte notes perdudes · `notes_perdudes`

```
• look — SEMPRE
    JUGADORA: La nota que he trobat per la presó. D'algú que també va parlar amb el panell. ⟨si notes_trobades = 1⟩
    JUGADORA: Les notes que he trobat per la presó. Cadascuna d'algú que també va parlar amb el panell. ⟨si notes_trobades ≥ 2⟩
    NARRADOR: «Interna 4, any 12. El panell no ha vibrat mai. Li he donat cops, li he cridat, li he escrit. A l'altra banda no hi ha ningú. Si algun dia hi és, digues-li que l'he esperada.» ⟨si nota_perduda_1⟩
    NARRADOR: «Intern 11, any 37. Diuen que el reciclatge és un trasllat. Ningú no torna del trasllat. PD: els cartells del somriure són de paper bo. Per escriure-hi, vull dir.» ⟨si nota_perduda_2⟩
    NARRADOR: «Interna 23, any 58. He arribat fins a l'hangar. La comporta no té palanca, el pany de la llançadora canta i el motor no té pressió. Algú hi ha tret el ferro-9 a propòsit.» ⟨si nota_perduda_3⟩
    NARRADOR: «Sense número, any 80. He llegit els plànols. El camp crema els que no tenen ningú a l'altra banda. D'això en diuen reciclatge. Si llegeixes això, troba algú a l'altra banda.» ⟨si nota_perduda_4⟩
```

## Objecte nota vella · `nota_mos`

```
• look — SEMPRE
    NARRADOR: «Any 100. El Director de l'holograma diu que va ser un accident. Mireu la foto del torn de nit: no va ser un accident. —M., cel·la 9»
```

## Diàleg `cargol` amb Cargol

```
COMENÇA A: amiga (si cargol recorda formulari_acceptat) · salutacio

[salutacio]
    CARGOL: Senyora Iri! En què la pot servir el Cargol, robot de manteniment model C-1?
    ↪ menu

[amiga]
    CARGOL: Senyora Iri! La meva usuària preferida. Vostè sí que entén els procediments.
    ↪ menu

[menu]
    ▸ Necessito la clau de la cambra de ressonància. ⟨si NO porta_cambra_oberta i no té clau_cambra⟩ → clau
    ▸ Necessito un imant de ferro-9. ⟨si iri_sap_pany i no té imant_ferro9 (iri) i no té imant_ferro9 (vet) i finestra_objecte_iri ≠ "imant_ferro9" i NO acte1_acabat⟩ → imant
    ▸ Necessito un diapasó de ferro-9. ⟨si iri_sap_diapaso i NO pany_sonic_obert i no té diapaso (iri) i no té diapaso (vet)⟩ → diapaso
    ▸ Necessito un altre imant de ferro-9. ⟨si iri_sap_calaix i NO planols_robats i no té imant_ferro9 (iri)⟩ → imant2
    ▸ Necessito un tub de vàlvula de ferro-9. ⟨si iri_sap_tub i no té tub_ferro9 (iri) i no té tub_amb_llibreta (iri) i no (té tub_amb_llibreta (vet) o tub_muntat)⟩ → tub
    ▸ Cargol, hi ha cap manera d'omplir menys formularis? ⟨una vegada, si formularis_arxivats ≥ 2⟩ → carnet
    ▸ Aquí tens el 27-B/E, signat pel capatàs. ⟨si té formulari_27be_signat⟩ → carnet_lliurar
    ▸ Com estàs, Cargol? ⟨una vegada⟩ → dia
        ⇒ cargol recorda preguntat_pel_dia, relació cargol +1
    ▸ Què et fan, a la revisió anual? ⟨una vegada, si acte1_acabat⟩ → memoria
    ▸ Per què es va construir la cambra? ⟨una vegada⟩ → per_que
    ▸ Com va la fàbrica, Cargol? ⟨si acte1_acabat i NO iri_fugida⟩ → fabrica
    ▸ Fins després, Cargol. → adeu · FI

[clau]
    CARGOL: Formulari 27-B, degudament segellat. Procedint. ⟨si té formulari_segellat o té formulari_triplicat⟩
    CARGOL: Aquí té la clau. Que tingui un torn productiu, senyora Iri! ⟨si té formulari_segellat o té formulari_triplicat⟩
      ⇒ rep clau_cambra, cargol recorda formulari_acceptat, relació cargol +1
    CARGOL: Aquest formulari no està segellat, senyora. Un formulari sense segell és només un paper trist. ⟨si no (té formulari_segellat o té formulari_triplicat) i té formulari_27b⟩
    CARGOL: Per lliurar material, necessito el formulari 27-B, degudament segellat. Són les normes. Les normes són boniques. ⟨si no (té formulari_segellat o té formulari_triplicat) i no té formulari_27b⟩
    ↪ menu

[imant]
    CARGOL: El material de ferro-9 requereix el formulari 27-B segellat per triplicat. Sense excepcions. Ni per a vostè. ⟨si no té carnet_exemplar i no té formulari_triplicat⟩
    [SO: eina] CARGOL: Carnet d'usuària exemplar! Procedint sense paperassa. Em sap greu: m'encanta la paperassa. ⟨si té carnet_exemplar⟩
      ⇒ rep imant_ferro9
    CARGOL: Tres segells! Senyora Iri, se m'escalfen els circuits d'emoció. ⟨si no té carnet_exemplar i té formulari_triplicat⟩
    [SO: eina] CARGOL: Un imant de ferro-9, lot 7. Arxivo el formulari. Que en faci bon ús! ⟨si no té carnet_exemplar i té formulari_triplicat⟩
      ⇒ perd formulari_triplicat, rep imant_ferro9, cargol recorda triplicat_acceptat, relació cargol +1, formularis_arxivats += 1
    ↪ menu

[dia]
    CARGOL: ...
    CARGOL: Ningú no m'ho havia preguntat mai.
    CARGOL: Estic... funcional. Gràcies, senyora Iri. Ho registraré a la meva memòria permanent.
    ↪ menu

[per_que]
    CARGOL: Ordre directa del Director Aldaia. Classificació: secret. Accés: només direcció.
    CARGOL: Si em pregunta per què el Director em va fer posar-la a punt just abans del seu torn... també és secret.
    JUGADORA: Abans del meu torn? Per què el meu?
    CARGOL: Secret, senyora.
    ↪ menu

[adeu]
    CARGOL: Recordi: un formulari a temps estalvia disgustos!

[diapaso]
    CARGOL: El material de ferro-9 requereix el formulari 27-B segellat per triplicat. Sense excepcions. Ni per a vostè. ⟨si no té carnet_exemplar i no té formulari_triplicat⟩
    [SO: eina] CARGOL: Carnet d'usuària exemplar! Procedint sense paperassa. Em sap greu: m'encanta la paperassa. ⟨si té carnet_exemplar⟩
      ⇒ perd diapaso_espatllat, rep diapaso, diapaso_to := 0, cargol recorda diapaso_lliurat
    CARGOL: Un altre diapasó, senyora Iri? El d'abans xiulava, oi? Ho he sentit des d'aquí. ⟨si no té carnet_exemplar i (té formulari_triplicat i cargol recorda diapaso_lliurat)⟩
    [SO: eina] CARGOL: Diapasó de ferro-9, la 440. Formulari arxivat. Que soni bé! ⟨si no té carnet_exemplar i té formulari_triplicat⟩
      ⇒ perd formulari_triplicat, perd diapaso_espatllat, rep diapaso, diapaso_to := 0, cargol recorda diapaso_lliurat, formularis_arxivats += 1
    ↪ menu

[imant2]
    CARGOL: El material de ferro-9 requereix el formulari 27-B segellat per triplicat. Sense excepcions. Ni per a vostè. ⟨si no té carnet_exemplar i no té formulari_triplicat⟩
    [SO: eina] CARGOL: Carnet d'usuària exemplar! Procedint sense paperassa. Em sap greu: m'encanta la paperassa. ⟨si té carnet_exemplar⟩
      ⇒ rep imant_ferro9
    [SO: eina] CARGOL: Un altre imant, senyora Iri? Cada vegada m'omple més l'arxiu. M'encanta. Que en faci bon ús! ⟨si no té carnet_exemplar i té formulari_triplicat⟩
      ⇒ perd formulari_triplicat, rep imant_ferro9, formularis_arxivats += 1
    ↪ menu

[tub]
    CARGOL: Un tub de ferro-9, senyora Iri? El Director l'ha anomenada per megafonia. Segons el meu manual, això la converteix en fugitiva.
    CARGOL: I els fugitius no omplen formularis. No hi ha casella.
    CARGOL: I el seu carnet no diu res de fugitives. És un buit legal preciós. ⟨si té carnet_exemplar⟩
    [SO: eina] CARGOL: Té. Que no em vegi ningú donant-l'hi. M'agradaria continuar arxivant.
      ⇒ rep tub_ferro9
    ↪ menu

[memoria]
    CARGOL: M'esborren la memòria, senyora Iri. Cada any. Norma 4-C: un robot no ha de tenir records.
    CARGOL: La propera revisió és la setmana que ve. El formulari diu: «Memòria: esborrar». Segellat i tot.
    CARGOL: Així que, tècnicament, la meva memòria permanent dura fins dilluns.
    JUGADORA: Un formulari segellat pel capatàs... Fins dilluns. Ja ho veurem.
    ⇒ +cargol_sap_revisio
    ↪ menu

[carnet]
    CARGOL: Quina pregunta tan bonica! Amb dos triplicats arxivats, vostè opta al Carnet d'Usuària Exemplar.
    CARGOL: Només cal el formulari 27-B/E, signat a mà pel capatàs en persona. El segell no val: ha de ser la signatura.
    CARGOL: El capatàs no ha signat mai res. Però la norma és la norma.
    JUGADORA: Un formulari per deixar d'omplir formularis. És clar.
    ⇒ rep formulari_27be
    ↪ menu

[carnet_lliurar]
    CARGOL: «Cinc minuts més, mare.» Signatura manuscrita del capatàs. Inconfusible.
    [SO: segell] CARGOL: Felicitats, senyora Iri! Carnet d'Usuària Exemplar. A partir d'ara, el material de ferro-9 li surt sense formularis.
    CARGOL: L'arxivaré amb molt d'amor. És el darrer formulari que em portarà.
    ⇒ perd formulari_27be_signat, rep carnet_exemplar, +carnet_obtingut, relació cargol +1
    ↪ menu

[fabrica]
    CARGOL: La cambra fa estona que calla, senyora Iri. Quan una cambra calla, és que a l'altra banda algú encara no ha acabat d'escriure. ⟨si NO acte3_iniciat i (no (iri_sap_mida) i no (té nota_mida (iri)))⟩
    CARGOL: Porta un paper a la butxaca que fa olor de no reglamentari, senyora Iri. Jo el llegiria. ⟨si NO acte3_iniciat i (no (iri_sap_mida) i té nota_mida (iri))⟩
    CARGOL: Bigues, al moll, n'hi ha de sobres. Però totes pesen més de dos quilos, i la cambra no n'admet ni un gram més. Les seves normes són gairebé tan estrictes com les meves. ⟨si NO acte3_iniciat i (iri_sap_mida i no (comporta_oberta))⟩
    CARGOL: Li ha arribat una molla per la cambra, senyora Iri? No consta a cap inventari. Jo, abans d'arxivar-la, la miraria bé. ⟨si NO acte3_iniciat i (iri_sap_mida i comporta_oberta i (té molla (iri) i NO iri_sap_diapaso))⟩
    CARGOL: Porta un paper a la butxaca que fa olor de no reglamentari, senyora Iri. Jo el llegiria. ⟨si NO acte3_iniciat i (iri_sap_mida i comporta_oberta i (té nota_pressio (iri) i NO iri_sap_pressio))⟩
    CARGOL: La cambra no ha fet «zing» des de fa una estona. Deu ser que a l'altra banda algú està ocupat. ⟨si NO acte3_iniciat i (iri_sap_mida i comporta_oberta i no ((iri_sap_diapaso i no (pany_sonic_obert)) o (pany_sonic_obert i iri_sap_pressio) o valvula = "mig" o (té molla (iri) i NO iri_sap_diapaso) o (té nota_pressio (iri) i NO iri_sap_pressio)))⟩
    CARGOL: Productiva, senyora Iri. I si li cal una peça de ferro-9 que soni d'una manera concreta, ja sap el procediment: formulari 27-B, segellat per triplicat. I una llima, i paciència. ⟨si NO acte3_iniciat i (iri_sap_mida i comporta_oberta i (iri_sap_diapaso i no (pany_sonic_obert)))⟩
    CARGOL: El conducte del moll té cent vint anys de servei previst, segons el manual. El que vostè hi faci avui, algú ho notarà d'aquí a molt de temps. ⟨si NO acte3_iniciat i (iri_sap_mida i comporta_oberta i (pany_sonic_obert i iri_sap_pressio) i no (valvula = "mig"))⟩
    CARGOL: Tot en ordre, senyora Iri. Massa en ordre. El Director ha cridat l'Inspector Sic dues vegades aquesta setmana. ⟨si NO acte3_iniciat i (iri_sap_mida i comporta_oberta i valvula = "mig" i no (acte2_acabat))⟩
    CARGOL: Senyora Iri, el Director l'ha anomenada per megafonia. L'Inspector Sic vigila la cambra i diu que no es mourà fins que atrapi el lladre del ferro-9. ⟨si acte3_iniciat i (no (té mapa_fuga (iri)) i NO sic_distret)⟩
    CARGOL: L'Inspector Sic ha passat corrent pel meu magatzem buscant un lladre. No l'ha trobat. La cambra està lliure, senyora Iri. ⟨si acte3_iniciat i (no (té mapa_fuga (iri)) i sic_distret)⟩
    CARGOL: Un fullet del futur? No el puc arxivar: no tinc carpeta per al futur. Però vostè té una llima, i una reixa a la cambra. ⟨si acte3_iniciat i (té mapa_fuga (iri) i no (reixa_preparada))⟩
    CARGOL: Si marxa, senyora Iri, que no sigui amb les mans buides. Algú, a l'altra banda, encara espera una peça. ⟨si acte3_iniciat i (té mapa_fuga (iri) i reixa_preparada i no (té tub_amb_llibreta (vet) o tub_muntat))⟩
    CARGOL: La peça ja ha arribat on havia d'arribar, oi? Doncs vostè, senyora Iri, també hauria de ser lluny. El moll, diuen, és molt bonic a aquesta hora. ⟨si acte3_iniciat i (té mapa_fuga (iri) i reixa_preparada i (té tub_amb_llibreta (vet) o tub_muntat) i no (iri_fugida))⟩
    ↪ menu

```

## Diàleg `cargol_vell` amb Conserge

```
COMENÇA A: recorda (si cargol_memoria) · hola (si ha vist cargol_vell.primera) · primera

[primera]
    CONSERGE: Benvinguda a la Sala de la Memòria. No toqui les vitrines.
    CONSERGE: No recordo per què. Però no les toqui.
    ↪ menu

[hola]
    CONSERGE: No toqui les vitrines, interna.
    ↪ menu

[recorda]
    CONSERGE: Interna 9! La senyora Iri n'estaria orgullosa.
    ↪ menu

[menu]
    ▸ Qui ets? ⟨una vegada⟩ → qui
    ▸ Què són totes aquestes coses de les vitrines? ⟨una vegada⟩ → peces
    ▸ Adéu. → adeu · FI

[qui]
    CONSERGE: Un robot de manteniment, model C-1. Nom... no en tinc. Em diuen «el conserge».
    CONSERGE: Abans de ser conserge vaig ser alguna cosa més. No ho recordo. Ningú no em va deixar recordar-ho.
    ↪ menu

[adeu]
    CONSERGE: Adéu. No toqui les vitrines.

[peces]
    CONSERGE: Peces de l'era de les fàbriques. Segons els cartells, tot era ritual.
    CONSERGE: Segons el meu inventari, tot eren eines. Mana el cartell.
    ↪ menu

```

## Diàleg `directora` amb Directora Aldaia

```
COMENÇA A: tornada (si vet_fugida_cella) · tub (si té tub_amb_llibreta (vet)) · hola_pacte (si pacte_acceptat) · hola (si ha vist directora.primera) · primera

[primera]
    DIRECTORA ALDAIA: Interna 9. O hauria de dir... Vet?
    DIRECTORA ALDAIA: Ets la primera que fa funcionar la finestra en cent vint anys. Felicitats: ja no et reciclarem.
    DIRECTORA ALDAIA: Treballaràs per a mi. I la cambra, a partir d'ara, és meva.
    DIRECTORA ALDAIA: Ah, i he fet treure el tub de la vàlvula de la teva llançadora. Per si et venien ganes de viatjar: ara l'única sortida d'aquí és el meu pacte.
      ⇒ +vet_sap_tub
    ↪ menu

[hola]
    DIRECTORA ALDAIA: Encara t'ho penses, interna?
    ↪ menu

[menu]
    ▸ Què vol de mi? → que_vol
    ▸ Què li passarà a la I.? ⟨una vegada⟩ → iri
    ▸ D'acord. Ho faré per vosaltres. ⟨una vegada⟩ → pacte
        ⇒ +pacte_acceptat
    ▸ I si dic que no? ⟨si NO pacte_acceptat⟩ → no
    ▸ Ja m'ho pensaré. ⟨si NO pacte_acceptat⟩ → adeu · FI
    ▸ Vaig a reformar-me una mica més. ⟨si pacte_acceptat⟩ → adeu_pacte · FI

[que_vol]
    DIRECTORA ALDAIA: Que sincronitzis quan jo t'ho digui, amb la teva amiga de l'altra banda.
    DIRECTORA ALDAIA: El meu rebesavi, el Director, també la vol. Entre tots dos, la finestra serà de la família Aldaia.
    DIRECTORA ALDAIA: Mentre sincronitzis, ningú no et reciclarà. Després, ja veurem. ⟨si NO tub_muntat⟩
    ↪ menu

[iri]
    DIRECTORA ALDAIA: Ja ho has llegit a l'arxiu, oi? Desapareix. Sempre ha desaparegut.
    DIRECTORA ALDAIA: La història no es discuteix, interna. S'arxiva.
    ↪ menu

[no]
    DIRECTORA ALDAIA: Ja vas dir que no a la corporació una vegada, per quaranta filtres d'aire i un barri de morosos. Mira on t'ha portat.
    DIRECTORA ALDAIA: Aleshores el reciclatge torna a ser per avui. Tu tries.
    ↪ menu

[adeu]
    DIRECTORA ALDAIA: Fins al vespre. La MARE et vigila.

[pacte]
    DIRECTORA ALDAIA: Sàvia decisió, interna. Ho sabia: al final, tothom es reforma.
    DIRECTORA ALDAIA: El panell torna a ser teu, sota la meva supervisió. Envia alguna cosa a la teva amiga: que vegi que continues allà.
    ↪ menu

[tornada]
    DIRECTORA ALDAIA: Mira qui torna pel forat. Ja t'ho has pensat, interna?
    JUGADORA: Sí. La resposta és no.
    DIRECTORA ALDAIA: Els guàrdies venen de camí. Gaudeix de la teva cel·la mentre la tinguis.

[tub]
    DIRECTORA ALDAIA: Dona'm aquesta canonada, interna. Els guàrdies ja estan de camí.
    JUGADORA: Que vinguin. Ja em trobaran, si poden.

[hola_pacte]
    DIRECTORA ALDAIA: Com va la reeducació, interna?
    ↪ menu

[adeu_pacte]
    DIRECTORA ALDAIA: Així m'agrada. La MARE et vigila.

```

## Diàleg `guardia` amb Guàrdia d'Orís

```
COMENÇA A: fugitiva (si cella_tancada i no (ha vist guardia.fugitiva)) · hola (si ha vist guardia.primera) · primera

[primera]
    GUÀRDIA D'ORÍS: Interna 9. Perdona, és que... Tinc la sensació que et conec.
    GUÀRDIA D'ORÍS: Bé. No et puc deixar passar de la zona comuna, però no et trepitjaré els talons.
    ↪ menu

[hola]
    GUÀRDIA D'ORÍS: Interna 9. Tot bé?
    ↪ menu

[menu]
    ▸ Qui ets? ⟨una vegada⟩ → qui
    ▸ Tens la clau de les vitrines del museu? ⟨si placa_vista i NO vitrina_oberta i no té clau_vitrina⟩ → vitrina
    ▸ Fins després. → adeu · FI

[qui]
    GUÀRDIA D'ORÍS: Guàrdia d'Orís. La meva besàvia va treballar a la fàbrica d'aquí sota, al torn de nit.
    GUÀRDIA D'ORÍS: Sempre deia que una tal I. li havia salvat la feina. I potser alguna cosa més.
    JUGADORA: (a part) D'Orís... Algú del torn de nit de la I. I la I. li va salvar la feina.
    ↪ menu

[vitrina]
    GUÀRDIA D'ORÍS: Les vitrines? Sí, les tinc totes en aquest clauer. Per què?
    GUÀRDIA D'ORÍS: ...No m'ho diguis. Té. Si algú pregunta, se m'ha caigut.
    ⇒ rep clau_vitrina
    ↪ menu

[adeu]
    GUÀRDIA D'ORÍS: Vés amb compte, interna 9.

[fugitiva]
    GUÀRDIA D'ORÍS: Interna 9? Tu no eres a la cel·la, tancada amb clau?
    GUÀRDIA D'ORÍS: ...Saps què? No t'he vist. Avui tinc la vista fatal.
    ↪ menu

```

## Diàleg `mare` amb MARE

```
COMENÇA A: hola

[hola]
    MARE: Hola, interna 9! Soc la MARE, el seu Mòdul d'Atenció i Reinserció Ecològica. Com la puc fer feliç?
    ↪ menu

[menu]
    ▸ Què és exactament el reciclatge? → reciclatge
    ▸ Vull sortir d'aquí. → sortir
    ▸ Qui va construir aquesta presó? ⟨una vegada⟩ → preso
    ▸ Res. Adéu, MARE. → adeu · FI

[reciclatge]
    MARE: El reciclatge és una experiència transformadora! Literalment.
    JUGADORA: Literalment com?
    MARE: Aquesta informació no està disponible per a la seva tranquil·litat. De res!
    ↪ menu

[sortir]
    MARE: Sol·licitud de sortida registrada! Temps d'espera estimat: tres-cents quaranta anys.
    MARE: Gràcies per la seva paciència!
    ↪ menu

[preso]
    MARE: La Gavina es va construir amb les restes de la gloriosa fàbrica de ferro-9 de la Corporació Aldaia, pujades a l'òrbita peça a peça!
    MARE: La fàbrica va tancar fa cent vint anys, després d'un petit accident del torn de nit. Res de greu!
    ↪ menu

[adeu]
    MARE: Fins aviat, interna 9! Recordi: queden tres dies! ⟨si NO acte3_iniciat⟩
    MARE: Fins aviat, interna 9! Recordi: el seu reciclatge és avui! O no. Ho estem revisant! ⟨si acte3_iniciat⟩

```

## Diàleg `mira` amb Mira

```
COMENÇA A: despres (si planols_lliurats) · hola (si ha vist mira.primera) · primera

[primera]
    MIRA: Iri! Tothom diu que el Director et busca. Què has fet?
    MIRA: No, no m'ho diguis. Si no ho sé, no ho puc explicar.
    ↪ menu

[hola]
    MIRA: Encara aquí? Vés amb compte.
    ↪ menu

[despres]
    MIRA: Ves-te'n, Iri. Jo m'encarrego dels plànols.

[menu]
    ▸ Què diuen de mi? ⟨una vegada⟩ → que_dius
    ▸ Tinc una cosa per a tu. ⟨si té planols⟩ → planols
    ▸ He de marxar, Mira. → adeu · FI

[que_dius]
    MIRA: Que vas trencar la cambra del Director. I que el Sic t'ha de portar a declarar.
    MIRA: Jo dic que no et conec gaire. Menteixo fatal, però ho dic.
    ↪ menu

[planols]
    JUGADORA: Mira. Els plànols de la cambra. El Director la va fer per obrir una finestra, i va fer servir el meu torn per provar-la.
    MIRA: Ho sabia. Ho sabia que no havia estat un accident.
    JUGADORA: Jo me'n vaig. Quan jo ja no hi sigui, fes-los públics.
    MIRA: Tu marxa. Jo me n'encarrego. I Iri... gràcies per no deixar que em culpessin a mi.
    ⇒ perd planols, +planols_lliurats

[adeu]
    MIRA: Doncs marxa. I no em diguis on.

```

## Diàleg `mos` amb Mos

```
COMENÇA A: ofes (si mos recorda insultat) · hola (si ha vist mos.primera) · primera

[primera]
    MOS: Ah, la nouvinguda està desperta. Tres dies, eh? Jo en porto vint, d'esperar.
    MOS: Diuen que m'han oblidat. Jo dic que m'estan reservant per a una ocasió especial.
    ↪ menu

[hola]
    MOS: Digues, nena.
    ↪ menu

[ofes]
    MOS: Ah. La que creu que soc un vell inútil.
    ↪ menu

[menu]
    ▸ Em deixes alguna cosa per escriure? ⟨si NO llapis_donat i panell_vet_reparat i relació mos ≥ 1⟩ → llapis
    ▸ Necessito alguna cosa per escriure. Tens res? ⟨si NO llapis_donat i panell_vet_reparat i relació mos < 1⟩ → llapis_que
    ▸ Per què vas maquillat? ⟨una vegada⟩ → maquillatge
    ▸ Què és el reciclatge, Mos? ⟨una vegada⟩ → reciclatge
        ⇒ mos recorda preguntat_reciclatge
    ▸ Què diuen de mi, a la galeria? ⟨una vegada⟩ → galeria
    ▸ Tens família, Mos? ⟨una vegada, si no (mos recorda insultat)⟩ → familia
        ⇒ mos recorda preguntat_familia
    ▸ Perdona pel que et vaig dir, Mos. ⟨una vegada, si mos recorda insultat⟩ → perdo
        ⇒ mos oblida insultat, mos recorda perdonat, relació mos +2
    ▸ Mos, necessito que la Directora miri cap a una altra banda. Un moment. ⟨una vegada, si acte3_iniciat i carta_mos_lliurada i NO pacte_acceptat⟩ → distreure
    ▸ Com ho veus, Mos? ⟨si acte1_acabat i NO vet_fugida⟩ → veus
    ▸ Res, res. → adeu · FI

[reciclatge]
    MOS: Ningú no ho sap. Els que se'n van no tornen.
    MOS: I cap no ha tornat a queixar-se, que és el més sospitós de tot.
    MOS: Això sí: diuen que els porten a la part vella de l'estació. On hi havia la fàbrica.
    ↪ menu

[maquillatge]
    MOS: Per estar presentable per al reciclatge. Si m'han de reciclar, que estigui guapo.
    ↪ menu

[familia]
    MOS: Una filla. La Nura. Li vaig escriure una carta quan em van tancar.
    MOS: Mai no he sabut si la va rebre. Aquí les cartes se les menja l'arxiu.
    ⇒ comença carta_mos
    ↪ menu

[llapis]
    MOS: Té, el meu llapis d'ulls. Torna-me'l abans del reciclatge, eh?
      ⇒ rep llapis_ulls, +llapis_donat
    ↪ menu

[llapis_que]
    MOS: Només tinc el meu llapis d'ulls. I què hi guanyo jo, si te'l deixo?
    ↪ convencer

[convencer]
    ▸ Que estaràs guapíssim al reciclatge. Més que ara, i mira que és difícil. ⟨si NO llapis_donat i no (mos recorda insultat)⟩ → elogiat
        ⇒ mos recorda elogiat, relació mos +1
    ▸ Que un vell inútil com tu no el necessita. ⟨si NO llapis_donat i no (mos recorda insultat)⟩ → insultat
        ⇒ mos recorda insultat, relació mos -2
    ▸ Res. Oblida-ho. → menu

[elogiat]
    MOS: Oh. Tu sí que en saps. Té, el llapis d'ulls. Fes-ne bon ús.
      ⇒ rep llapis_ulls, +llapis_donat
    ↪ menu

[insultat]
    MOS: Això ho recordaré, nena. Tinc vint anys de temps lliure per recordar-ho.
    ↪ menu

[perdo]
    MOS: Mmm. Acceptat. Però que no es repeteixi, que soc sensible.
    ↪ menu

[adeu]
    MOS: Res, res. Com la meva vida.

[galeria]
    MOS: Que vas buidar un magatzem Aldaia de filtres d'aire. Quaranta.
    MOS: I que els vas instal·lar a l'Anell de Baix, casa per casa, quan la corporació els va tallar l'aire. De franc.
    VET: Els vaig vendre. Molt cars. Soc lladre, Mos, no una santa.
    MOS: Ja. Per això a l'Anell de Baix pinten claus angleses a les parets.
    ↪ menu

[distreure]
    MOS: Per tu, nouvinguda? El millor desmai de la història de La Gavina. Fa vint anys que l'assajo.
    MOS: Quan siguis al panell, tus dues vegades. I no em miris, que se m'escapa el riure.
    JUGADORA: Gràcies, Mos.
    ⇒ +mos_distreu
    ↪ menu

[veus]
    NARRADOR: En Mos abaixa la veu i mira de reüll la Directora. ⟨si acte3_iniciat⟩
    MOS: Ja ets fora i encara tornes? Al fons del passadís hi ha l'hangar. Diuen que allà s'acaba el reciclatge. O que hi comença. ⟨si NO acte3_iniciat i no (ha estat a gavina_hangar)⟩
    MOS: Una comporta sense palanca. Doncs demana-la a la de la paret. Però digues-li la mida, nena: el que tu en dius un pam, ella no ho ha vist mai. ⟨si NO acte3_iniciat i (ha estat a gavina_hangar i no (iri_sap_mida) i no (té nota_mida (iri)))⟩
    MOS: Ja li has escrit? Doncs ara li toca a ella. La paret té el seu ritme. ⟨si NO acte3_iniciat i (ha estat a gavina_hangar i no (iri_sap_mida) i té nota_mida (iri))⟩
    MOS: La palanca, ara, és cosa seva. Tu, ulls oberts: amb cent vint anys pel mig, les coses no sempre arriben per la paret. ⟨si NO acte3_iniciat i (ha estat a gavina_hangar i iri_sap_mida i no (comporta_oberta))⟩
    MOS: Un pany que canta? I el so no passa per la paret: això t'ho dic jo, que m'hi vaig passar anys cridant. Li hauràs de fer arribar la nota d'una altra manera. Dins d'alguna cosa que soni. ⟨si NO acte3_iniciat i (ha estat a gavina_hangar i iri_sap_mida i comporta_oberta i no (molla_afinada))⟩
    MOS: Una molla afinada. Ara l'ha de copiar ella, en ferro del bo, i fer-te-la arribar. ⟨si NO acte3_iniciat i (ha estat a gavina_hangar i iri_sap_mida i comporta_oberta i molla_afinada i no (pany_sonic_obert))⟩
    MOS: Al motor no li arriba pressió? A la fàbrica tot anava per canonades. Pregunta-li a ella què hi pot fer, des d'allà. ⟨si NO acte3_iniciat i (ha estat a gavina_hangar i iri_sap_mida i comporta_oberta i molla_afinada i pany_sonic_obert i no (valvula = "mig") i no (valvula = "tancada"))⟩
    MOS: Diuen a la galeria que el nivell de sota és una piscina. Jo no hi he vist mai aigua. Tu sí, oi? Doncs digues-li que afluixi. ⟨si NO acte3_iniciat i (ha estat a gavina_hangar i iri_sap_mida i comporta_oberta i molla_afinada i pany_sonic_obert i no (valvula = "mig") i valvula = "tancada")⟩
    MOS: Si el conducte ja vibra, prova d'engegar aquesta andròmina. Que se senti a tota La Gavina. ⟨si NO acte3_iniciat i (ha estat a gavina_hangar i iri_sap_mida i comporta_oberta i molla_afinada i pany_sonic_obert i valvula = "mig" i no (components_complets))⟩
    MOS: Tens nau. Però abans de marxar, baixa a l'arxiu: l'escala de l'hangar hi porta. Allà hi ha totes les respostes que la MARE no dona. ⟨si NO acte3_iniciat i (ha estat a gavina_hangar i iri_sap_mida i comporta_oberta i molla_afinada i pany_sonic_obert i valvula = "mig" i components_complets i no (arxiu_explorat))⟩
    MOS: Has vist alguna cosa a l'arxiu que no m'expliques. Si és d'ella, digues-l'hi. I digues-li com et dius: ja va sent hora. ⟨si NO acte3_iniciat i (ha estat a gavina_hangar i iri_sap_mida i comporta_oberta i molla_afinada i pany_sonic_obert i valvula = "mig" i components_complets i arxiu_explorat i no (acte2_acabat))⟩
    MOS: La MARE diu que t'esperen a la Sala de la Memòria. Hi ha galetes. I a la paret, un mapa de tota l'estació, fàbrica inclosa. ⟨si acte3_iniciat i no (ha estat a gavina_memoria)⟩
    MOS: Si la de la paret ha de fugir, li cal un camí. El mapa de la Sala de la Memòria el té, si saps mirar-lo. ⟨si acte3_iniciat i (ha estat a gavina_memoria i no (vet_sap_conducte))⟩
    MOS: Ja saps per on? Doncs dibuixa-ho i envia-ho. Amb la Directora davant, això sí. Digues-li que sí a tot: no costa res. ⟨si acte3_iniciat i (ha estat a gavina_memoria i vet_sap_conducte i no (té mapa_fuga (iri)) i NO carta_mos_lliurada)⟩
    MOS: Ja saps per on? Doncs dibuixa-ho i envia-ho. Amb la Directora davant, això sí. O em desmaio jo, que ho tinc assajat. ⟨si acte3_iniciat i (ha estat a gavina_memoria i vet_sap_conducte i no (té mapa_fuga (iri)) i carta_mos_lliurada)⟩
    MOS: Ara li toca a ella. Tu, mira la reixa de tant en tant. Cent vint anys són molts per a un cargol. ⟨si acte3_iniciat i (ha estat a gavina_memoria i vet_sap_conducte i té mapa_fuga (iri) i no (reixa_preparada))⟩
    MOS: Per on sortir ja ho tens. Però la Directora va fer treure el tub de la llançadora, i sense tub no surt de l'hangar. Te l'ha d'enviar ella. L'últim. ⟨si acte3_iniciat i (ha estat a gavina_memoria i vet_sap_conducte i té mapa_fuga (iri) i reixa_preparada i no (té tub_amb_llibreta (vet) o tub_muntat))⟩
    MOS: Ja tens el tub? Doncs vés-te'n, nena: a l'hangar, i que no et vegi la Directora. I no em miris, que em poso sentimental. ⟨si acte3_iniciat i (ha estat a gavina_memoria i vet_sap_conducte i té mapa_fuga (iri) i reixa_preparada i (té tub_amb_llibreta (vet) o tub_muntat) i no (vet_fugida))⟩
    ↪ menu

```

## Diàleg `sic` amb Inspector Sic

```
COMENÇA A: hola (si ha vist sic.primera) · primera

[primera]
    INSPECTOR SIC: Operària I. Ordres del Director: ningú entra a la cambra. Vostè, menys que ningú.
    ↪ menu

[hola]
    INSPECTOR SIC: Encara aquí, operària?
    ↪ menu

[menu]
    ▸ Què ha passat? → que_passa
    ▸ Deixi'm passar. → passar
    ▸ On és el Director? ⟨una vegada⟩ → director
    ▸ Inspector, m'ha semblat veure algú al soterrani, al magatzem del ferro-9. ⟨una vegada, si ha triat sic.menu.que_passa⟩ → enganyar
    ▸ Res, res. → adeu · FI

[que_passa]
    INSPECTOR SIC: Falten coses. Una clau anglesa, un imant... i qui sap què més.
    INSPECTOR SIC: I cada vegada que la cambra fa «zing», en falta una altra.
    INSPECTOR SIC: L'expedient ja té una sospitosa: la d'Orís, la seva companya de torn. Ja veurem si és l'única. ⟨si sospita_sic ≥ 2 i NO mira_salvada⟩
    ↪ menu

[passar]
    INSPECTOR SIC: No.
    ↪ menu

[director]
    INSPECTOR SIC: Al despatx. Esperant que vostè hi vagi a confessar.
    INSPECTOR SIC: Jo no hi aniria.
    ↪ menu

[adeu]
    INSPECTOR SIC: Ni un pas, operària.

[enganyar]
    INSPECTOR SIC: Al magatzem? El lladre!
    INSPECTOR SIC: No es mogui d'aquí, operària. I no toqui res.
    ⇒ +sic_distret

```

## Pistes

```
iri_clau — quan juga iri i NO porta_cambra_oberta · fins que porta_cambra_oberta o té clau_cambra (iri)
    1. La clau de la cambra la té el Cargol, al magatzem.
    2. El Cargol només dona material amb el formulari 27-B segellat.
    3. Hi ha formularis al tauler d'anuncis. El segell el té el capatàs... agafat, mentre dorm.
iri_segell — quan juga iri i té formulari_27b (iri) i no té segell (iri) · fins que té segell (iri)
    1. El capatàs no deixarà anar el segell per les bones.
    2. Si el fes riure, potser l'afluixaria.
    3. Fes-li pessigolles al nas amb el plomall del magatzem.
iri_alarma — quan juga iri i porta_cambra_oberta i NO alarma_apagada · fins que alarma_apagada
    1. L'alarma ve de la consola de la cambra.
    2. La palanca està encallada. Cal fer palanca amb alguna cosa.
    3. Fes servir la clau anglesa amb la palanca.
iri_boto — quan juga iri i alarma_apagada i NO accident_cambra · fins que accident_cambra
    1. La clau és dins la cambra, i el botó vermell fa pampallugues.
    2. Prem el botó vermell.
iri_esperar — quan juga iri i finestra_armada = "iri" · fins que finestra_armada ≠ "iri"
    1. Aquí ja no puc fer res més. Què deu passar a l'altra banda del camp?
    2. Canvia a la Vet.
vet_panell — quan juga vet i NO panell_vet_trencat · fins que panell_vet_trencat
    1. La paret vibra. Potser li he d'explicar qui mana.
    2. Empeny el panell rovellat.
vet_reparar — quan juga vet i panell_vet_trencat i NO panell_vet_reparat · fins que panell_vet_reparat
    1. La clau anglesa serveix per desmuntar coses.
    2. Fes servir la clau anglesa amb el panell. I torna-ho a fer.
vet_mos_perdo — quan juga vet i panell_vet_reparat i NO llapis_donat i mos recorda insultat · fins que no (mos recorda insultat)
    1. En Mos no em deixarà res mentre estigui ofès. I té vint anys per recordar-ho.
    2. Parla amb en Mos i demana-li perdó. Després, demana-li el llapis d'ulls amb bones paraules.
vet_nota — quan juga vet i panell_vet_reparat i NO nota_vet_escrita · fins que nota_vet_escrita
    1. Algú m'ha enviat una clau anglesa. Li podria respondre.
    2. Per escriure necessito paper i alguna cosa que pinti.
    3. L'avís que m'han passat per sota la porta i el llapis d'ulls d'en Mos. Potser en Mos s'ha de deixar afalagar.
vet_enviar — quan juga vet i té nota_vet (vet) · fins que no té nota_vet (vet)
    1. La nota ha d'anar al buit de darrere el panell.
    2. Fes servir la nota amb el panell, i després prem el panell.
vet_enviar_pany — quan juga vet i té nota_pany (vet) · fins que no té nota_pany (vet)
    1. El dibuix ha d'arribar a la I. Pel mateix camí que la nota.
    2. Fes servir el dibuix del pany amb el panell.
vet_esperar — quan juga vet i finestra_armada = "vet" · fins que finestra_armada ≠ "vet"
    1. He enviat el que podia. Ara ho ha de recollir algú.
    2. Canvia a l'Iri.
iri_rebre_ritual — quan juga iri i NO sincronia_automatica i finestra_armada = "vet" · fins que finestra_armada ≠ "vet"
    1. La consola parpelleja. Hi ha algú a l'altra banda?
    2. Ves a la cambra i prem el botó de sincronia.
iri_rebre — quan juga iri i sincronia_automatica i finestra_armada = "vet" · fins que finestra_armada ≠ "vet"
    1. A l'altra banda han armat el camp. A la cambra m'hi espera alguna cosa.
    2. Ves a la cambra: el que t'han enviat hi arribarà en entrar-hi.
iri_llegir — quan juga iri i ((té nota_vet (iri) i NO nota_vet_llegida) o (té nota_pany (iri) i NO iri_sap_pany)) · fins que no ((té nota_vet (iri) i NO nota_vet_llegida) o (té nota_pany (iri) i NO iri_sap_pany))
    1. Hauria de llegir el que m'ha arribat.
    2. Mira la nota de l'inventari.
iri_respondre — quan juga iri i nota_vet_llegida i NO nota_iri_escrita · fins que nota_iri_escrita
    1. Algú m'ha escrit. Li podria respondre.
    2. Fes servir el llapis amb la llibreta de torn.
iri_enviar — quan juga iri i (té nota_iri (iri) o (té imant_ferro9 (iri) i NO porta_cella_oberta)) · fins que no té nota_iri (iri) i (no té imant_ferro9 (iri) o porta_cella_oberta)
    1. Si les coses que hi poso desapareixen... arriben a algun lloc.
    2. Posa-ho dins la cambra.
vet_llegir — quan juga vet i té nota_iri (vet) i NO sap_que_es_temps · fins que sap_que_es_temps
    1. M'han contestat!
    2. Mira la nota de l'inventari.
vet_pany — quan juga vet i sap_que_es_temps i NO nota_pany_escrita · fins que nota_pany_escrita
    1. Si la I. és en una fàbrica, potser coneix el pany de la meva porta.
    2. Mira bé el pany, i després dibuixa'l en algun paper.
    3. Hi ha un fullet sota el coixí. I el llapis d'ulls encara pinta.
vet_mirar_llancadora — quan juga vet i comporta_oberta i NO pany_vist · fins que pany_vist
    1. La llançadora té una porta. Com s'obre?
    2. Mira la llançadora.
vet_pany_sonic — quan juga vet i comporta_oberta i NO pany_sonic_sentit i pany_vist · fins que pany_sonic_sentit
    1. La llançadora té un pany ben estrany.
    2. Fes servir el pany sònic de la porta de la llançadora, a veure què fa.
iri_imant — quan juga iri i (iri_sap_pany i no té imant_ferro9 (iri) i no té imant_ferro9 (vet) i finestra_objecte_iri ≠ "imant_ferro9" i NO acte1_acabat) · fins que no (iri_sap_pany i no té imant_ferro9 (iri) i no té imant_ferro9 (vet) i finestra_objecte_iri ≠ "imant_ferro9" i NO acte1_acabat)
    1. Necessito un imant de ferro-9. El Cargol en té.
    2. Per al ferro-9, el Cargol vol el formulari segellat per triplicat.
    3. Fes servir el segell amb el formulari segellat. Si no en tens, agafa'n un altre del tauler.
vet_sortir — quan juga vet i té imant_ferro9 (vet) i NO porta_cella_oberta · fins que no té imant_ferro9 (vet)
    1. Un imant. El pany és magnètic...
    2. Fes servir l'imant amb la porta.
iri_porta — quan juga iri i té clau_cambra (iri) i NO porta_cambra_oberta · fins que porta_cambra_oberta
    1. Ja tinc la clau de la cambra. Ara només cal trobar-li el pany.
    2. Fes servir la clau de la cambra amb la porta de la cambra, a la sala de calderes.
vet_armar — quan juga vet i finestra_objecte_vet ≠ "" i finestra_armada = "" · fins que finestra_objecte_vet = "" o finestra_armada ≠ ""
    1. La nota ja és a dins. Ara cal engegar aquest trasto.
    2. Prem el panell per armar el camp.
iri_armar — quan juga iri i finestra_objecte_iri ≠ "" i finestra_armada = "" · fins que finestra_objecte_iri = "" o finestra_armada ≠ ""
    1. Ja hi ha alguna cosa dins la cambra. Si armo el camp, potser arriba a algun lloc.
    2. Prem el botó de sincronia.
vet_hangar — quan juga vet i acte1_acabat i no (ha estat a gavina_hangar) · fins que ha estat a gavina_hangar
    1. El cartell diu que el reciclatge és per aquí. Jo prefereixo qualsevol altre lloc.
    2. Ves cap a la porta del fons del passadís.
vet_mesurar — quan juga vet i ha estat a gavina_hangar i NO comporta_mesurada · fins que comporta_mesurada
    1. Per demanar-li una palanca a la I., primer he de saber quina mida ha de tenir.
    2. Necessito mesurar l'encaix amb alguna cosa que la I. també conegui.
    3. Fes servir la clau anglesa amb la comporta. Si encara és al panell de la cel·la, recupera-la primer.
vet_nota_mida — quan juga vet i comporta_mesurada i NO nota_mida_escrita · fins que nota_mida_escrita
    1. He d'enviar la mida a la I.
    2. Em cal paper. El cartell del passadís, per exemple.
    3. Agafa un tros del cartell i fes-hi servir el llapis d'ulls.
vet_enviar_mida — quan juga vet i té nota_mida (vet) · fins que no té nota_mida (vet)
    1. La mida l'ha de saber la I. Pel mateix camí de sempre.
    2. Fes servir la nota de la mida amb el panell de la cel·la.
vet_enviar_rovell — quan juga vet i té pols_rovell (vet) · fins que no té pols_rovell (vet)
    1. Aquesta pols l'ha de veure la I. Pel mateix camí de sempre.
    2. Fes servir la pols de rovell amb el panell de la cel·la.
iri_llegir_a2 — quan juga iri i ((té nota_mida (iri) i NO iri_sap_mida) o (té pols_rovell (iri) i NO iri_sap_rovell)) · fins que no ((té nota_mida (iri) i NO iri_sap_mida) o (té pols_rovell (iri) i NO iri_sap_rovell))
    1. M'ha arribat alguna cosa de la V.
    2. Mira-ho a l'inventari.
iri_biga — quan juga iri i iri_sap_mida i marca_pilar i NO comporta_oberta i (no té biga_acer (iri) i no té biga_ferro9 (iri) i NO biga_acer_serrada i biga_amagada = "" i no té biga_ferro9 (vet) i no té biga_muntada (vet)) · fins que no (NO comporta_oberta i (no té biga_acer (iri) i no té biga_ferro9 (iri) i NO biga_acer_serrada i biga_amagada = "" i no té biga_ferro9 (vet) i no té biga_muntada (vet)))
    1. Dos metres de biga per una finestra on no hi passa res de més de dos quilos...
    2. Al moll de càrrega hi ha bigues. Puc serrar-ne una a trossos, o amagar-la perquè la V. la trobi d'aquí a cent vint anys.
    3. Agafa la serra del moll i fes-la servir amb la biga d'acer. O amaga una biga sota la reixa del costat del pilar 7.
iri_amagar — quan juga iri i NO comporta_oberta i (té biga_acer (iri) o té biga_ferro9 (iri)) · fins que no té biga_acer (iri) i no té biga_ferro9 (iri)
    1. Per la finestra no hi cap. Pel camí llarg, sí.
    2. Amaga-la sota la reixa del costat del pilar 7. O, si és d'acer, serra-la.
iri_trams — quan juga iri i (té tram_biga_1 (iri) o té tram_biga_2 (iri) o té tram_biga_3 (iri)) · fins que no té tram_biga_1 (iri) i no té tram_biga_2 (iri) i no té tram_biga_3 (iri)
    1. Tres trams, tres viatges.
    2. Posa els trams dins la cambra, d'un en un.
vet_muntar — quan juga vet i (té tram_biga_1 (vet) o té tram_biga_2 (vet) o té tram_biga_3 (vet)) · fins que biga_muntada_feta
    1. Uns trams de biga. Si els ajunto...
    2. Quan tinguis els tres trams, fes-ne servir un amb un altre.
iri_nota_amagatall — quan juga iri i biga_amagada ≠ "" i NO nota_amagatall_escrita · fins que nota_amagatall_escrita
    1. Si la V. no sap on mirar, no la trobarà mai.
    2. Escriu-li on és: el llapis i la llibreta.
iri_enviar_a2 — quan juga iri i té nota_amagatall (iri) · fins que no té nota_amagatall (iri)
    1. La nota ha d'arribar a la V.
    2. Posa-la dins la cambra.
vet_placa — quan juga vet i té placa_cargol i cargol_gravat i NO cargol_memoria · fins que cargol_memoria
    1. La placa porta un nom. I al museu hi ha algú que no recorda el seu.
    2. Dona la placa al conserge del museu.
vet_buscar — quan juga vet i vet_sap_amagatall i NO biga_trobada i NO rovell_trobat · fins que biga_trobada o rovell_trobat
    1. El pilar 7... és al moll de l'hangar.
    2. Aixeca la reixa del terra del costat del pilar.
iri_rovell — quan juga iri i iri_sap_rovell i NO comporta_oberta i biga_amagada = "acer" · fins que biga_amagada ≠ "acer"
    1. L'acer no aguanta cent vint anys. O ferro-9, o a trossos per la finestra.
    2. Torna a pujar la biga de sota la reixa i serra-la, o amaga-hi la de ferro-9.
vet_obrir — quan juga vet i NO comporta_oberta i (té biga_ferro9 (vet) o té biga_muntada (vet)) · fins que comporta_oberta
    1. Ara sí que tinc palanca.
    2. Fes servir la biga amb la comporta.
vet_esperar_a2 — quan juga vet i acte1_acabat i NO comporta_oberta i comporta_mesurada i nota_mida_escrita · fins que comporta_oberta
    1. La I. hi està treballant. Potser li he de donar un cop de mà des de l'altra banda.
    2. Canvia a l'Iri.
iri_esperar_a2 — quan juga iri i acte1_acabat i NO comporta_oberta · fins que comporta_oberta
    1. Què deu necessitar, la V.?
    2. Canvia a la Vet.
vet_molla — quan juga vet i pany_sonic_sentit i NO molla_agafada · fins que molla_agafada
    1. El so no passa per la finestra. Però una cosa que faci el mateix so, sí.
    2. Alguna cosa que vibri... Les lliteres tenen molles.
    3. Agafa una molla de la llitera de la cel·la.
vet_afinar — quan juga vet i té molla (vet) i NO molla_afinada · fins que molla_afinada
    1. La molla ha de sonar igual que el pany.
    2. Prova-la amb el pany. Si cal, estira-la o arronsa-la.
    3. Fes servir la molla amb el pany sònic per comparar-les. «Estira» la tiba i «Empeny» l'arronsa.
vet_enviar_molla — quan juga vet i té molla (vet) i molla_afinada · fins que no té molla (vet)
    1. La molla afinada ha d'arribar a la I.
    2. Fes servir la molla amb el panell de la cel·la.
iri_llegir_molla — quan juga iri i té molla (iri) i NO iri_sap_diapaso · fins que iri_sap_diapaso
    1. M'ha arribat una molla. Amb una etiqueta.
    2. Mira la molla de l'inventari.
iri_diapaso — quan juga iri i iri_sap_diapaso i NO pany_sonic_obert i (no té diapaso (iri) i no té diapaso (vet) i no té diapaso_espatllat (iri)) · fins que no (NO pany_sonic_obert i (no té diapaso (iri) i no té diapaso (vet) i no té diapaso_espatllat (iri)))
    1. Per fer un diapasó de ferro-9, primer necessito ferro-9.
    2. El Cargol en té. Amb paperassa, és clar.
    3. Segella un formulari per triplicat i demana-li un diapasó al Cargol.
iri_afinar — quan juga iri i té diapaso (iri) i NO diapaso_afinat · fins que diapaso_afinat o no té diapaso (iri)
    1. Ha de sonar com la molla de la V.
    2. Llima'l a poc a poc i compara'l amb la molla cada vegada.
    3. La llima és al tauler d'eines del moll. Llima el diapasó i fes-lo servir amb la molla per comparar.
iri_espatllat — quan juga iri i té diapaso_espatllat (iri) · fins que no té diapaso_espatllat (iri)
    1. M'he passat de llima. Necessito un altre diapasó.
    2. Un altre formulari per triplicat, i cap al Cargol.
iri_enviar_diapaso — quan juga iri i té diapaso (iri) i diapaso_afinat · fins que no té diapaso (iri)
    1. El diapasó ha d'arribar a la V.
    2. Posa el diapasó dins la cambra.
vet_obrir_pany — quan juga vet i té diapaso (vet) i NO pany_sonic_obert · fins que pany_sonic_obert o no té diapaso (vet)
    1. Un diapasó. Per al pany.
    2. Fes servir el diapasó amb el pany sònic.
vet_esperar_diapaso — quan juga vet i molla_afinada i no té molla (vet) i NO pany_sonic_obert i no té diapaso (vet) · fins que pany_sonic_obert
    1. La I. hi està treballant.
    2. Canvia a l'Iri.
iri_esperar_diapaso — quan juga iri i comporta_oberta i NO pany_sonic_obert i NO iri_sap_diapaso i no té molla (iri) · fins que pany_sonic_obert o iri_sap_diapaso
    1. Què deu necessitar, ara, la V.?
    2. Canvia a la Vet.
vet_provar_motor — quan juga vet i pany_sonic_obert i NO vet_sap_pressio · fins que vet_sap_pressio
    1. La porta de la llançadora està oberta. A veure si aquesta andròmina engega.
    2. Prova d'engegar la llançadora.
vet_pressio — quan juga vet i pany_sonic_obert i NO motor_engegat i NO nota_pressio_escrita i vet_sap_pressio · fins que nota_pressio_escrita
    1. El motor no té pressió. D'on li ha de venir?
    2. Hi ha un conducte vell a la paret del moll de l'hangar. Potser la I. hi pot fer alguna cosa al passat.
    3. Escriu-li a la I.: un altre tros de cartell i el llapis d'ulls.
vet_enviar_pressio — quan juga vet i (té nota_pressio (vet) o té nota_massa (vet)) · fins que no té nota_pressio (vet) i no té nota_massa (vet)
    1. Això ho ha de llegir la I.
    2. Fes servir la nota amb el panell de la cel·la.
iri_llegir_pressio — quan juga iri i ((té nota_pressio (iri) i NO iri_sap_pressio) o (té nota_massa (iri) i NO iri_sap_massa)) · fins que no ((té nota_pressio (iri) i NO iri_sap_pressio) o (té nota_massa (iri) i NO iri_sap_massa))
    1. La V. m'ha escrit.
    2. Mira la nota de l'inventari.
iri_valvula — quan juga iri i iri_sap_pressio i valvula = "oberta" i NO motor_engegat · fins que valvula ≠ "oberta" o motor_engegat
    1. Si tapo el conducte ara, la pressió s'hi anirà acumulant durant cent vint anys.
    2. El conducte del moll té una vàlvula.
    3. Tanca la vàlvula del conducte del moll.
vet_reajust — quan juga vet i valvula = "tancada" i NO vet_ha_vist_inundacio · fins que vet_ha_vist_inundacio
    1. Tinc mal de cap. Alguna cosa ha canviat.
    2. Ves al moll de l'hangar.
vet_massa — quan juga vet i valvula = "tancada" i vet_ha_vist_inundacio i NO nota_massa_escrita · fins que nota_massa_escrita o valvula ≠ "tancada"
    1. Massa pressió! El conducte ha rebentat.
    2. La I. ho ha d'arreglar al passat. Digues-li.
    3. Un altre tros de cartell, el llapis d'ulls... i que afluixi la vàlvula.
iri_afluixar — quan juga iri i iri_sap_massa i valvula = "tancada" · fins que valvula ≠ "tancada"
    1. Massa pressió. Afluixa, Iri.
    2. Obre una mica la vàlvula del conducte del moll.
iri_massa_poc — quan juga iri i iri_sap_massa i valvula = "oberta" i NO motor_engegat · fins que valvula ≠ "oberta" o motor_engegat
    1. Oberta del tot no fa res, i tancada del tot rebenta.
    2. Tanca-la del tot i després obre-la una mica.
vet_engegar — quan juga vet i pany_sonic_obert i valvula = "mig" i NO motor_engegat · fins que motor_engegat
    1. El conducte vibra. Ara sí que hi ha pressió.
    2. Prova d'engegar la llançadora: empeny-la.
vet_esperar_pressio — quan juga vet i NO motor_engegat i ((nota_pressio_escrita i no té nota_pressio (vet) i valvula = "oberta") o (nota_massa_escrita i no té nota_massa (vet) i valvula = "tancada")) · fins que motor_engegat o valvula = "mig"
    1. Ara li toca a la I.
    2. Canvia a l'Iri.
iri_esperar_pressio — quan juga iri i pany_sonic_obert i NO motor_engegat i ((NO iri_sap_pressio i no té nota_pressio (iri)) o (valvula = "tancada" i NO iri_sap_massa i no té nota_massa (iri)) o valvula = "mig") · fins que motor_engegat
    1. Què deu passar, a l'altra banda?
    2. Canvia a la Vet.
vet_reixa_arxiu — quan juga vet i motor_engegat i NO reixa_arxiu_oberta · fins que reixa_arxiu_oberta
    1. La llançadora ja engega. Però què amaga, l'arxiu?
    2. La reixa de l'escala està lligada amb una cadena cargolada.
    3. Fes servir la clau anglesa amb l'escala del moll de l'hangar.
vet_baixar_arxiu — quan juga vet i reixa_arxiu_oberta i NO arxiu_explorat · fins que arxiu_explorat
    1. La reixa està oberta.
    2. Baixa per l'escala.
vet_expedients — quan juga vet i arxiu_explorat i NO vet_sap_desaparicio · fins que vet_sap_desaparicio
    1. Expedients de personal de la fàbrica... potser n'hi ha algun de la I.
    2. Mira els expedients de la taula de l'arxiu.
vet_planols_arxiu — quan juga vet i arxiu_explorat i NO vet_sap_gavina · fins que vet_sap_gavina
    1. Què hi fan, uns plànols a l'arxiu d'una presó?
    2. Mira els plànols de l'arxiu.
vet_carta_mos — quan juga vet i arxiu_explorat i NO carta_mos_trobada · fins que carta_mos_trobada
    1. En Mos deia que les cartes se les menja l'arxiu.
    2. Remena l'arxivador.
vet_tornar_carta — quan juga vet i té carta_mos (vet) · fins que no té carta_mos (vet)
    1. Aquesta carta és d'en Mos.
    2. Dona-li la carta a en Mos.
vet_avisar — quan juga vet i vet_sap_desaparicio i NO nota_vet_nom_escrita · fins que nota_vet_nom_escrita
    1. La I. ha de saber-ho. I potser ja és hora que sàpiga com em dic.
    2. Escriu-li: un tros de cartell i el llapis d'ulls.
vet_enviar_nom — quan juga vet i té nota_vet_nom (vet) · fins que no té nota_vet_nom (vet)
    1. La nota ha d'arribar a la I.
    2. Fes servir la nota amb el panell de la cel·la.
iri_llegir_nom — quan juga iri i té nota_vet_nom (iri) i NO iri_sap_desaparicio · fins que iri_sap_desaparicio
    1. La V. m'ha escrit. Amb el seu nom.
    2. Mira la nota de l'inventari.
iri_respondre_nom — quan juga iri i iri_sap_desaparicio i NO nota_iri_nom_escrita · fins que nota_iri_nom_escrita
    1. Li he de contestar. Amb el meu nom.
    2. El llapis i la llibreta.
iri_enviar_nom — quan juga iri i té nota_iri_nom (iri) · fins que no té nota_iri_nom (iri)
    1. La nota ha d'arribar a la Vet.
    2. Posa-la dins la cambra.
vet_llegir_nom — quan juga vet i té nota_iri_nom (vet) i NO acte2_acabat · fins que acte2_acabat
    1. La I. m'ha contestat.
    2. Mira la nota de l'inventari.
iri_planols — quan juga iri i motor_engegat i NO planols_robats i no (té imant_ferro9 (iri) i porta_cella_oberta) · fins que planols_robats
    1. El despatx del director és al costat del magatzem. Què hi deu guardar?
    2. El calaix del despatx té un pany M-3: s'obre amb un imant de ferro-9.
    3. Demana un altre imant al Cargol (amb un formulari per triplicat) i obre el calaix del despatx.
iri_calaix — quan juga iri i motor_engegat i NO planols_robats i té imant_ferro9 (iri) i porta_cella_oberta · fins que planols_robats o no té imant_ferro9 (iri)
    1. Ja tens l'imant. El calaix del despatx té un pany M-3.
    2. Fes servir l'imant amb el calaix del despatx.
iri_expedient — quan juga iri i sospita_sic ≥ 2 i NO iri_sap_mira_acusada i director_fora · fins que iri_sap_mira_acusada
    1. Massa robatoris. Què deu haver apuntat el Sic?
    2. Mira l'expedient del despatx del director.
iri_mira — quan juga iri i sospita_sic ≥ 2 i iri_sap_mira_acusada i NO mira_salvada · fins que mira_salvada
    1. La Mira pagarà per mi. No pot ser.
    2. Puc falsificar l'inventari, culpar el capatàs o confessar.
    3. Fes servir el segell amb el llibre d'inventari, o el llapis amb l'expedient del Sic.
vet_esperar_nom — quan juga vet i nota_vet_nom_escrita i no té nota_vet_nom (vet) i no té nota_iri_nom (vet) i NO acte2_acabat · fins que acte2_acabat
    1. Ara li toca a la I.
    2. Canvia a l'Iri.
iri_esperar_nom — quan juga iri i motor_engegat i NO iri_sap_desaparicio i no té nota_vet_nom (iri) · fins que iri_sap_desaparicio o acte2_acabat
    1. Què deu haver trobat, la V.?
    2. Canvia a la Vet.
vet_directora — quan juga vet i acte3_iniciat i no (ha vist directora.primera) · fins que ha vist directora.primera
    1. Hi ha algú a la meva cel·la. I no és en Mos.
    2. Parla amb la Directora Aldaia.
vet_memoria — quan juga vet i acte3_iniciat i no (ha estat a gavina_memoria) · fins que ha estat a gavina_memoria
    1. La MARE diu que he d'anar a la Sala de la Memòria.
    2. La Sala de la Memòria és al passadís.
vet_foto — quan juga vet i ha estat a gavina_memoria i NO vet_veu_foto · fins que vet_veu_foto
    1. En aquesta sala hi ha fotos de la fàbrica.
    2. Mira la foto del torn de nit.
vet_mapa_fuga — quan juga vet i ha estat a gavina_memoria i NO vet_sap_conducte · fins que vet_sap_conducte
    1. Si la I. ha de fugir de la fàbrica, necessito saber per on.
    2. Mira el mapa de La Gavina.
vet_fullet_mapa — quan juga vet i vet_sap_conducte i NO fullet_memoria_agafat · fins que fullet_memoria_agafat
    1. Per dibuixar-li la ruta, em cal paper.
    2. Agafa un fullet de l'expositor.
vet_canvia_iri — quan juga vet i acte3_iniciat i NO iri_descoberta · fins que iri_descoberta
    1. I a l'altra banda? Què li deu estar passant, a la I.?
    2. Canvia a l'Iri.
iri_sic — quan juga iri i iri_descoberta i no (ha vist sic.primera) · fins que ha vist sic.primera
    1. El Sic vigila la porta de la cambra.
    2. Parla amb el Sic.
iri_marca — quan juga iri i iri_sap_mida i NO marca_pilar · fins que marca_pilar
    1. La V. és al costat d'un pilar amb un 7 pintat. Al meu moll n'hi ha un.
    2. La V. m'ha dit on és. Una marca al pilar, si dura cent vint anys, li dirà: rebut, soc aquí.
    3. Agafa la llima del moll i fes-la servir amb el pilar.
vet_veure_marca — quan juga vet i marca_pilar i NO vet_ha_vist_marca · fins que vet_ha_vist_marca
    1. Li vaig dir a la I. que soc al costat del pilar 7. Potser m'ha contestat allà, sense gastar cap enviament.
    2. Torna al moll de l'hangar i mira el pilar 7.
vet_reixa — quan juga vet i vet_sap_conducte i fullet_memoria_agafat i NO reixa_mirada · fins que reixa_mirada
    1. El conducte comença al mòdul C. On hi ha una entrada?
    2. Mira la reixa de la paret de la cel·la.
vet_dibuixar — quan juga vet i reixa_mirada i NO mapa_fuga_escrit i vet_sap_tub · fins que mapa_fuga_escrit
    1. Ja sé per on ha de fugir la I. Li ho he de dibuixar.
    2. Fes servir el llapis d'ulls amb el fullet.
vet_pacte — quan juga vet i té mapa_fuga (vet) i NO pacte_acceptat i NO mos_distreu · fins que pacte_acceptat o mos_distreu
    1. La Directora no em deixa tocar el panell. Potser, si li dic que sí... O si algú la distreu.
    2. Parla amb la Directora i accepta el pacte, de mentida. O demana a en Mos que la distregui.
vet_enviar_mapa — quan juga vet i té mapa_fuga (vet) i (pacte_acceptat o mos_distreu) · fins que no (té mapa_fuga (vet))
    1. La Directora em deixa fer. Ara!
    2. Fes servir el mapa de fuga amb el panell.
iri_enganyar — quan juga iri i iri_descoberta i NO sic_distret i ha vist sic.primera · fins que sic_distret
    1. El Sic només pensa en una cosa: els robatoris.
    2. Potser, si li dic que he vist el lladre...
    3. Pregunta-li què ha passat, i després digues-li que has vist algú al magatzem.
iri_tornar_cambra — quan juga iri i sic_distret i NO iri_a_la_cambra · fins que iri_a_la_cambra
    1. La porta de la cambra està lliure.
    2. Entra a la cambra.
iri_esperar_mapa — quan juga iri i iri_a_la_cambra i no (té mapa_fuga (iri)) · fins que té mapa_fuga (iri)
    1. Què deu estar fent, la V.?
    2. Canvia a la Vet.
iri_llegir_mapa — quan juga iri i té mapa_fuga (iri) i NO iri_sap_reixa · fins que iri_sap_reixa
    1. La V. m'ha enviat un fullet.
    2. Mira el mapa de fuga de l'inventari.
iri_reixa — quan juga iri i iri_sap_reixa i NO reixa_preparada · fins que reixa_preparada
    1. La reixa del conducte és aquí, a la cambra.
    2. Si els cargols no hi són, el rovell no té res per soldar.
    3. Fes servir la llima amb la reixa.
iri_conducte — quan juga iri i reixa_preparada i NO ruta_marcada · fins que ruta_marcada
    1. La reixa ja cedeix. Abans de dir-ho a la V., vull provar la seva ruta fins al moll.
    2. Al fullet de la V. hi ha cinc signes, un per revolt: ← esquerra, ↑ recte, → dreta.
    3. Mira el mapa de fuga i, a cada revolt, tria el passadís del signe que toca, per ordre. Si t'hi perds, torna a mirar el fullet.
vet_esperar_ruta — quan juga vet i reixa_preparada i NO ruta_marcada · fins que ruta_marcada
    1. La reixa ja s'obre: la I. ha llimat els cargols. Ara deu estar provant la ruta del fullet.
    2. El conducte l'ha de recórrer la I., amb els signes del fullet. Canvia a l'Iri.
iri_esperar_reixa — quan juga iri i ruta_marcada i NO reixa_oberta i no (té tub_ferro9 (iri) o té tub_amb_llibreta (iri) o (té tub_amb_llibreta (vet) o tub_muntat)) · fins que reixa_oberta
    1. La reixa ja està. La V. ho hauria de notar.
    2. Canvia a la Vet.
vet_esperar_reixa — quan juga vet i no (té mapa_fuga (vet)) i mapa_fuga_escrit i NO reixa_preparada · fins que reixa_preparada
    1. La I. ja té el mapa. Què farà amb la reixa?
    2. Canvia a l'Iri.
vet_obrir_reixa — quan juga vet i reixa_preparada i NO reixa_oberta · fins que reixa_oberta
    1. La reixa ha canviat.
    2. Obre la reixa de la cel·la.
vet_tub_directora — quan juga vet i reixa_mirada i NO vet_sap_tub · fins que vet_sap_tub
    1. Abans de planejar res, vull saber què vol de mi la Directora.
    2. Parla amb la Directora, o mira la llançadora de l'hangar.
iri_tub — quan juga iri i iri_sap_tub i no (té tub_ferro9 (iri) o té tub_amb_llibreta (iri) o (té tub_amb_llibreta (vet) o tub_muntat)) · fins que no (no (té tub_ferro9 (iri) o té tub_amb_llibreta (iri) o (té tub_amb_llibreta (vet) o tub_muntat)))
    1. Un tub de vàlvula de ferro-9. Qui guarda peces, en aquesta fàbrica?
    2. Demana-li un tub al Cargol, al magatzem.
iri_tub_llibreta — quan juga iri i té tub_ferro9 (iri) · fins que no té tub_ferro9 (iri)
    1. Només em queda un enviament, i la llibreta amb les proves també ha d'arribar.
    2. El tub és buit per dins.
    3. Fes servir la llibreta de torn amb el tub.
iri_enviar_tub — quan juga iri i té tub_amb_llibreta (iri) · fins que no té tub_amb_llibreta (iri)
    1. Tot a punt. A la cambra.
    2. Posa el tub a la cambra.
iri_fugir — quan juga iri i (té tub_amb_llibreta (vet) o tub_muntat) i NO iri_fugida · fins que iri_fugida
    1. La V. ja té el tub. Ara em toca a mi.
    2. Fuig per la reixa del conducte i, al moll, puja a la llançadora.
vet_esperar_tub — quan juga vet i reixa_oberta i no (té tub_amb_llibreta (vet) o tub_muntat) · fins que té tub_amb_llibreta (vet) o tub_muntat
    1. La I. m'ha d'enviar el tub.
    2. Canvia a l'Iri.
vet_tub — quan juga vet i té tub_amb_llibreta (vet) · fins que no té tub_amb_llibreta (vet)
    1. La Directora vol el tub. Hora de marxar.
    2. Per la reixa, fins a l'hangar. I el tub, a la llançadora.
    3. Fes servir el tub amb la llançadora de l'hangar.
vet_volar — quan juga vet i tub_muntat i NO vet_fugida · fins que vet_fugida
    1. La llançadora té el tub. Aquí ja no em queda res.
    2. Fes servir la llançadora: engega-la.
iri_cargol_segell — quan juga iri i cargol_sap_revisio i NO cargol_reparat · fins que cargol_reparat
    1. Per al Cargol, un paper segellat és llei. Fins i tot el formulari de la seva revisió.
    2. Fes servir el segell oficial amb el Cargol.
iri_cargol_nom — quan juga iri i cargol_reparat i NO cargol_gravat i té llima · fins que cargol_gravat
    1. Ara el Cargol ho recordarà tot. Però sap com es diu?
    2. Grava-li el nom a la placa amb la llima.
iri_mira_planols — quan juga iri i (acte3_iniciat i mira_salvada i NO iri_fugida) i té planols · fins que planols_lliurats
    1. La Mira és al magatzem. Ella podria fer públics els plànols quan tu ja no hi siguis.
    2. Dona els plànols a la Mira.
vet_vitrina — quan juga vet i placa_vista i mira_salvada i NO vitrina_oberta i no té clau_vitrina · fins que vitrina_oberta
    1. La vitrina està tancada. Algú del personal de la presó en deu tenir la clau.
    2. Demana la clau de la vitrina a la Guàrdia d'Orís, al passadís.
vet_vitrina_obrir — quan juga vet i té clau_vitrina · fins que vitrina_oberta
    1. Obre la vitrina del museu amb la clau.
iri_carnet_signar — quan juga iri i té formulari_27be · fins que té formulari_27be_signat o carnet_obtingut
    1. El 27-B/E l'ha de signar el capatàs. Dorm, però té mans.
    2. Fes servir el formulari 27-B/E amb el capatàs (amb el llapis a l'inventari).
iri_carnet_lliurar — quan juga iri i té formulari_27be_signat · fins que carnet_obtingut
    1. Porta el formulari signat al Cargol.
vet_notes — quan juga vet i notes_trobades ≥ 1 i notes_trobades < 5 · fins que notes_trobades ≥ 5
    1. Hi ha més notes amagades per la presó: en esquerdes, sota rajoles, en racons que ningú no mira.
    2. N'hi ha una a cada lloc on pots anar: la cel·la, el passadís, l'hangar, l'arxiu i la Sala de la Memòria.
vet_nota_mos — quan juga vet i té nota_mos · fins que nota_mos_tornada
    1. «M., cel·la 9», fa vint anys. Qui fa vint anys que és a la cel·la 9?
    2. Dona la nota a en Mos.
vet_rebre — quan juga vet i sincronia_automatica i finestra_armada = "iri" · fins que finestra_armada ≠ "iri"
    1. A l'altra banda han armat el camp. Al panell de la cel·la m'hi espera alguna cosa.
    2. Torna a la cel·la: el que t'han enviat hi arribarà en entrar-hi.
```

## Finals

```
fugida «Final · La fugida» — quan fugida_completada
    NARRADOR: La llançadora vella travessa la nit. A dins, una presonera, un tub de ferro-9 nou i una llibreta de torn de fa cent vint anys.
    NARRADOR: La Vet fa pública la llibreta. Una operària desapareguda fa cent vint anys explica, amb la seva lletra, que la cambra no va ser cap accident. I la Vet, l'única sincronitzadora que n'ha sortit viva, explica la resta: el reciclatge.
    NARRADOR: La Corporació Aldaia s'aguantava sobre una sola història: l'accident i la lliçó. Sense la història, uns mesos després La Gavina tanca. La corporació, també.
    NARRADOR: La Sala de la Memòria es converteix en un museu de veritat. L'holograma del Director, apagat per sempre. A la vitrina buida, un cartell nou: «Clau anglesa. Servia per collar cargols».
    NARRADOR: A la foto del torn de nit ja no hi ha cap cara ratllada. Sota l'Iri, un cartell nou: «Desapareguda».
    NARRADOR: Al seu costat, la Mira d'Orís somriu. Ella no va perdre mai la feina. ⟨si mira_salvada⟩
    NARRADOR: El conserge del museu és un robot vell i rovellat. Es diu Cargol, i ho explica a tothom qui hi entra. ⟨si cargol_memoria⟩
    NARRADOR: En Mos surt de la presó maquillat, com sempre. A fora l'espera una dona que té els seus ulls: la Nura. ⟨si carta_mos_lliurada⟩
    La Vet somriu. Ella sap on va anar la I. Després pren el camí de l'Anell de Baix, on encara respiren amb els seus filtres.
veritat «Final · La veritat a temps» — quan fugida_completada i mira_salvada i planols_lliurats
    NARRADOR: La llançadora vella travessa la nit. La Vet té mal de cap: el pitjor de tots. El món sencer es reescriu al seu voltant, i a ella no la toca: ha passat massa nits dins el camp.
    NARRADOR: Cent vint anys abans, una ajudant del torn de nit, la Mira d'Orís, va fer públics uns plànols.
    NARRADOR: La Corporació Aldaia no va arribar a construir mai cap presó. La Gavina és una estació orbital: l'Estació d'Orís.
    NARRADOR: La Vet hi fa mitja volta. Al moll l'espera una dona jove amb el cabell coure i l'uniforme de directora de l'estació.
    NARRADOR: «Benvinguda a l'Estació d'Orís. Perdona... Tinc la sensació que et conec.»
    NARRADOR: Al moll, un home gran amb els ulls pintats ajuda a descarregar. No ha estat mai a cap cel·la.
    En aquest món, la Vet no ha estat mai presa. Però ho recorda tot: el camp no esborra qui hi ha estat a dins. I a l'altra banda de cent vint anys, una enginyera del torn de nit també.
correspondencia «Final · Correspondència» — quan fugida_completada i mira_salvada i planols_lliurats i cargol_memoria
    NARRADOR: La llançadora vella travessa la nit. La Vet té mal de cap: el pitjor de tots. El món sencer es reescriu al seu voltant, i a ella no la toca: ha passat massa nits dins el camp.
    NARRADOR: Cent vint anys abans, una ajudant del torn de nit, la Mira d'Orís, va fer públics uns plànols.
    NARRADOR: La Corporació Aldaia no va arribar a construir mai cap presó. La Gavina és una estació orbital: l'Estació d'Orís.
    NARRADOR: La Vet hi fa mitja volta. Al moll l'espera una dona jove amb el cabell coure i l'uniforme de directora de l'estació.
    NARRADOR: «Benvinguda a l'Estació d'Orís. Perdona... Tinc la sensació que et conec.»
    NARRADOR: Al moll, un home gran amb els ulls pintats ajuda a descarregar. No ha estat mai a cap cel·la.
    NARRADOR: Al costat de la directora hi ha un robot vell i rovellat, amb una placa al pit: «CARGOL».
    NARRADOR: «Senyora Vet. Fa cent vint anys que l'espero. Tinc una cosa per a vostè.»
    NARRADOR: Una carta plegada mil vegades.
    NARRADOR: «V.: he viscut molt, i he viscut lliure. La Mira et saluda. El Cargol m'ha promès arreglar la cambra. Escriu-me. —I.»
    NARRADOR: «Cent vint anys reparant la cambra, i ningú no ho sabia. Vaig esperar. Era la meva feina.»
    La finestra torna a funcionar. Dins la cambra, una nota nova: «Hola, V. Tinc tantes coses per explicar-te. —I.»
```
