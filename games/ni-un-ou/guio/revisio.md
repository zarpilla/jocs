# Revisió de textos

> Generat amb `npm run revisio` a partir de `game/data/`. No l'editis a mà.
>
> Per a cada cosa, les interaccions en l'ordre en què el motor les prova: s'agafa **la primera que encaixa**.
> Una interacció «SEMPRE» que no és l'última amaga les de sota.

## Sala Cabina de la Capitana · `cabina_capitana` (iri, vet)

```
DECORAT ulls_dia — es veu si escena = 2 o escena = 3
DECORAT ulls_dia_mar — es veu si escena = 2 o escena = 3

PORTA «passadís»
    • walkTo/use/open — SEMPRE
        ⇒ → passadis
    • look — SEMPRE
        JUGADORA: La porta del passadís.

CONTRACTE «contracte»
    • look — SEMPRE
        JUGADORA: El contracte de la donació. Capçalera: «FUNDACIÓ BLAU NET · Per un mar més net, junts».
        JUGADORA: Condició 4: embarcar N. Vidal.
        ⇒ +contracte_vist
    • use + registre — si escena = 8 i NO reunio_comencada
        ⇒ +registre_ensenyat, diàleg capitana
    • use + registre — si escena = 8
        JUGADORA: La Capitana ja és al menjador. Ara ja no hi ha temps.
    • pickUp — si escena = 6 o (escena = 8 i NO reunio_comencada)
        JUGADORA: És de la Capitana. I la Capitana és a dos pams.
    • pickUp — SEMPRE
        JUGADORA: És de la Capitana. No el toco.

NOVELLA «novel·la»
    • look — SEMPRE
        JUGADORA: «Amor a alta mar», volum tres. Hi ha un punt de llibre amb una àncora.

CARTA «carta nàutica»
    • look — SEMPRE
        JUGADORA: La carta de la campanya. Galway, encerclat. Port Hallen, encerclat amb un altre color, i més fort.

CAPITANA «—» — hi és si (escena = 2 i pacient ≠ "capitana") o escena = 6 o (escena = 8 i NO reunio_comencada)
    • look — SEMPRE
        JUGADORA: La Capitana. Fins i tot asseguda, sembla que estigui al timó.
    • talkTo — SEMPRE
        ⇒ diàleg capitana
    • give + registre — SEMPRE
        ⇒ diàleg capitana

```

## Sala Caixa de cadenes · `caixa_cadenes` (iri, vet)

```
EN ENTRAR
    • * (una vegada) — si escena = 6
        NARRADOR: Dins la caixa de cadenes, a les fosques, hi ha la Juana, amb una manta i un paper d'entrepà.
        JUANA FERRER: Ah. Ara sí que m'heu trobat.
        JUANA FERRER: M'ha agafat aquesta tarda a la sala de bombes. Duia passamuntanyes. M'ha deixat una manta i un entrepà de truita. El llibre, no. Era a la meitat.
        VET: I l'entrepà, te l'has menjat?
        JUANA FERRER: Aquest sí.
        NARRADOR: Una pausa.
        JUANA FERRER: Ha estat el millor dia de la campanya.
        JUANA FERRER: Em va preguntar on era la mostra. Li vaig dir que l'havia llençada al mar.
        NARRADOR: Una pausa.
        JUANA FERRER: No s'ho va creure. No va dir res, però no s'ho va creure.
        JUANA FERRER: Feia olor de pipa.
        IRI: Ell no.
        NARRADOR: Una pausa.
        IRI: Ell, mai.
        JUANA FERRER: No he dit cap nom.
        ⇒ +juana_trobada, +prova_pipa, +juana_entrepa

ESCOTILLA «escotilla»
    • walkTo/use/open — si escena = 6 i juana_trobada
        VET: Infermeria. Ara, Juana. I no et queixis.
        TÍTOL: Una de la matinada.
        ⇒ escena := 7, esdeveniment situar, esdeveniment situar, esdeveniment protagonista
    • walkTo/use/open — SEMPRE
        ⇒ → coberta_proa
    • look — SEMPRE
        JUGADORA: L'escotilla. Amunt, l'aire.

CADENES «cadenes»
    • look — SEMPRE
        JUGADORA: Cent metres de cadena, rovellada i freda.

JUANA «—» — hi és si escena = 6
    • look — si juga iri
        JUANA FERRER: Molta gent fuma pipa.
        IRI: A bord? Un.
    • look — SEMPRE
        JUGADORA: Té fred, i està contenta. Les dues coses alhora.
    • talkTo — SEMPRE
        JUANA FERRER: A la infermeria m'explico millor. Aquí fa fred fins i tot per als peixos.

MANTA «manta» — hi és si escena = 6
    • look — SEMPRE
        JUGADORA: Una manta i el paper d'un entrepà de truita.

```

## Sala Camarot de l'Iri · `camarot_iri` (iri, vet)

```
EN ENTRAR
    • * (una vegada) — si escena = 1
        NARRADOR: Tres i quaranta de la matinada. A bord de l'Arenga, tothom dorm.
        [SO: mossegada] NARRADOR: Bé, gairebé tothom. L'Iri s'ha despertat i no sap per què.
        NARRADOR: En Diu mossega el cable del carregador. Després, la porta del camarot queda entreoberta, i el gat ja no hi és.
        JUGADORA: Diu? Diu!
        JUGADORA: Si et troba la Capitana, ets sopa de peix.
        JUGADORA: Un moment.
        JUGADORA: El terra fa pendent. Poquet. Però fa tres campanyes que dormo a bord d'aquest vaixell, i l'Arenga no dorm mai torçada.
        JUGADORA: Primer, a buscar en Diu. I ja que hi som, a veure què li passa a l'Arenga.
        ⇒ +diu_fora

DECORAT ulls_dia — es veu si escena = 2 o escena = 3

PORTA «porta»
    • walkTo/use/open — SEMPRE
        ⇒ → passadis_baix
    • look — SEMPRE
        JUGADORA: La porta del camarot. Entreoberta. Aquest gat sap obrir portes, però no sap tancar-les.

CARREGADOR «carregador»
    • look — si juga iri
        JUGADORA: El cable del carregador. Mossegat de punta a punta. Té la forma exacta de les dents d'en Diu.
    • pickUp — SEMPRE
        JUGADORA: Ja no carrega res. Ara és art.

GOT «got d'aigua»
    • look — si escena = 1 i juga iri
        JUGADORA: L'aigua del got no està plana. Fa pendent cap a popa.
        JUGADORA: L'Arenga s'ha assegut de cul. I a popa, a sota de la línia de flotació, hi ha la meva sala de màquines.
    • look — si juga iri
        JUGADORA: L'aigua del got balla, però balla recta. Així m'agrada.
    • pickUp/use — SEMPRE
        JUGADORA: Si me l'emporto, qui em dirà com seu el vaixell?

MACETA «maceta» — hi és si NO maceta_agafada
    • look — si juga iri
        JUGADORA: La maceta de goma. La tinc aquí per la falca de baix de la porta de màquines, que s'encalla des de l'agost.
    • pickUp — si juga iri
        JUGADORA: Per si la falca de baix ha tornat a fer de les seves. Sempre en fa.
        ⇒ rep maceta, +maceta_agafada

LLITERA «llitera»
    • look — si juga iri i escena = 1
        JUGADORA: Encara està calenta. Jo també voldria ser-hi.
    • look — SEMPRE
        JUGADORA: La meva llitera. Feta. Com cada matí, encara que no hagi dormit.
    • use — SEMPRE
        JUGADORA: Ara no és hora de dormir. Bé, sí que ho és. Però no puc.

MOTXILLA «motxilla»
    • look — si juga iri
        JUGADORA: La motxilla d'en Diu. Bé, meva. Però hi viu ell.
    • pickUp/open — si escena = 1
        JUGADORA: Buida. En Diu ha sortit de patrulla.
    • pickUp/open — SEMPRE
        JUGADORA: Millor no remenar-la. Fa olor de sardina.

ULL_DE_BOU «ull de bou»
    • look — si escena = 2 o escena = 3
        JUGADORA: Gris i esquitxat. El mar es veu, i encara se sent més.
    • look — SEMPRE
        JUGADORA: Fosc. El mar no es veu, però se sent.

DIU «—» — hi és si escena = 1 i NO diu_fora

```

## Sala Coberta de popa · `coberta_popa` (iri, vet)

```
EN ENTRAR
    • * (una vegada) — si escena = 2
        NARRADOR: Fa un matí gris i fred de febrer, i l'esmorzar és a coberta, a popa, amb guants.
        NARRADOR: L'Arenga encara és on va passar la nit. A una milla, a babord, hi ha una plataforma.
        CAPITANA ROIG: Aquesta nit hem tingut una fuita a popa. Per seguretat, farem escala a Port Hallen. Inspecció del buc.
        IRI: No ha estat una fuita. Algú ha obert la vàlvula.
        ERNEST BASTIDA: L'Arenga té quaranta anys, Iri. Les vàlvules velles fan coses.
        CAPITANA ROIG: Si l'Ernest diu que és vella, és vella. Port Hallen.
        NARRADOR: L'Iri baixa a màquines sense acabar-se el cafè.
        NARRADOR: En Bastida s'aixeca a trincar la zòdiac de la nit, que encara penja de la grua. Hi fa el nus Bastida, a poc a poc.
        VET: Aquest és el famós nus Bastida?
        MARCEL: El sap fer tothom. Ens el va ensenyar a tots.
        VET: Ernest, hi has fet una volta de més. L'he comptada. Soc metgessa: compto coses.
        ERNEST BASTIDA: Aquesta volta no l'ensenyo. Un nus ha de tenir un secret, doctora.
        NARRADOR: Tothom torna a la seva feina. La Juana no ha vingut a esmorzar.
        NARRADOR: Més tard, pel walkie:
        VET: En Bastida diu que la vàlvula és vella. I la Capitana se'l creu.
        IRI: Tothom se'l creu. Fa dues campanyes, en un temporal, vaig caure per la borda. Em va treure ell.
        IRI: Tot el que sé de mar, m'ho ha ensenyat ell.
        IRI: Tu ets nova. No sé si em puc fiar de tu.
        IRI: Però a tu no et mentiran per costum.
        VET: No és problema meu. Jo faig de metgessa, no de detectiu.
        IRI: Doncs fes revisions.
        ⇒ +esmorzar_fet, +prova_volta, esdeveniment situar
    • * (una vegada) — si escena = 6 i NO bastida_baixa
        NARRADOR: Onze de la nit. Els llums de popa, l'estela blanca i en Bastida, amb una llanterna, «ajudant a buscar».

DECORAT dia — es veu si escena = 2 o escena = 3
DECORAT dia_mar — es veu si escena = 2 o escena = 3

PORTA «menjador»
    • walkTo/use/open — si escena = 6 i juga vet i nus_lico
        JUGADORA: Si me'n vaig ara, en Bastida torna a vigilar.
    • walkTo/use/open — SEMPRE
        ⇒ → menjador
    • look — SEMPRE
        JUGADORA: La porta del menjador.

PROA «cap a proa»
    • walkTo/use/open — si escena = 6 i juga vet i nus_lico
        JUGADORA: Si me'n vaig ara, en Bastida torna a vigilar.
    • walkTo/use/open — si juga vet i escena = 6
        JUGADORA: Si en Bastida em veu anar cap a proa, sabrà on busquem. Me'l quedo jo.
    • walkTo/use/open — SEMPRE
        ⇒ → coberta_proa
    • look — SEMPRE
        JUGADORA: La coberta lateral, cap a proa.

GRUA «grua»
    • look — si escena = 2
        JUGADORA: La zòdiac de la nit, trincada a la grua amb un nus Bastida.
        JUGADORA: Amb una volta de més.
    • look — SEMPRE
        JUGADORA: La grua de popa i la zòdiac, trincada.

BORDA «borda»
    • look — si escena ≥ 3
        JUGADORA: La borda de popa. A sota, l'estela blanca.
    • look — SEMPRE
        JUGADORA: La borda. A sota, el mar, quiet com una sopa freda.

PLATAFORMA «plataforma» — hi és si escena = 2
    • look — si juga vet i NO plataforma_vista
        JUGADORA: La plataforma que no surt als mapes. El logotip, tapat amb cinta americana. Al voltant, una taca d'aigua tèrbola.
        JUGADORA: L'aigua és d'un altre color, allà.
        NARRADOR: Ningú no li respon. A la borda, en Bastida es gira d'esquena a babord.
        ⇒ +plataforma_vista
    • look — SEMPRE
        JUGADORA: La plataforma que no surt als mapes. El logotip, tapat amb cinta americana. Al voltant, una taca d'aigua tèrbola.
        JUGADORA: Les gavines hi passen per sobre i no s'hi posen.

TAULA «esmorzar» — hi és si escena = 2
    • look — SEMPRE
        JUGADORA: Croissants, cafè i guants. La Nadia n'ha repetit, de croissant.
    • pickUp — SEMPRE
        JUGADORA: Ja n'he pres un. La Nadia, dos.

HORITZO «horitzó» — hi és si escena ≥ 3
    • look — si escena = 3
        JUGADORA: L'estela blanca i, a l'horitzó, cap a on anem, mar gris i prou.
    • look — SEMPRE
        JUGADORA: Els llums de popa, l'estela blanca i, a l'horitzó, cap a on anem, res.

BASTIDA «—» — hi és si escena = 2 o (escena = 6 i NO bastida_baixa)
    • look — si escena = 2
        JUGADORA: En Bastida, a la borda, fumant la pipa d'esquena al vent.
    • look — SEMPRE
        JUGADORA: En Bastida, fent la ronda per la coberta, «ajudant a buscar».
    • talkTo — SEMPRE
        ⇒ diàleg bastida

CAPITANA «—» — hi és si escena = 2 i NO esmorzar_fet
    • look — SEMPRE
        JUGADORA: La Capitana es pren el cafè dreta, com si el vaixell li pogués fugir.

MARCEL «—» — hi és si escena = 2 i NO esmorzar_fet
    • look — SEMPRE
        JUGADORA: El Marcel, amb la boca plena de croissant. Té cara de no haver dormit.

NADIA «—» — hi és si escena = 2 i NO esmorzar_fet
    • look — SEMPRE
        JUGADORA: La Nadia, amb el mòbil a la mà. Fa fotos del mar. O d'alguna cosa que hi ha al mar.

TOMAS «—» — hi és si escena = 2 i NO esmorzar_fet
    • look — SEMPRE
        JUGADORA: En Tomàs reparteix croissants com qui reparteix medalles.

```

## Sala Coberta de proa · `coberta_proa` (iri, vet)

```
DECORAT dia — es veu si escena = 2 o escena = 3
DECORAT dia_mar — es veu si escena = 2 o escena = 3
DECORAT cadenat — es veu si escena ≥ 4 i NO cadenat_tallat

POPA «cap a popa»
    • walkTo/use/open — si juga iri i escena = 3
        JUGADORA: Ara no. Si l'Ernest em veu, sabrà que no soc a dormir.
    • walkTo/use/open — si juga iri
        JUGADORA: A coberta hi ha l'Ernest fumant. Avui no el vull mirar a la cara.
    • walkTo/use/open — SEMPRE
        ⇒ → coberta_popa
    • look — SEMPRE
        JUGADORA: La coberta lateral, cap a popa.

PORTA «passadís»
    • walkTo/use/open — SEMPRE
        ⇒ → passadis
    • look — SEMPRE
        JUGADORA: La porta del passadís.

BALSA «balsa salvavides»
    • look — SEMPRE
        JUGADORA: La balsa salvavides, en el seu contenidor blanc. Sota, un racó on no passa ningú.
    • open/use/pull — SEMPRE
        JUGADORA: Només si ens enfonsem. I no ens enfonsem. Encara.

MOLINET «molinet de l'àncora»
    • look — SEMPRE
        JUGADORA: El molinet de l'àncora. Les cadenes baixen per un forat a la caixa de cadenes.

ESCOTILLA «escotilla de la caixa de cadenes»
    • walkTo/use/open — si cadenat_tallat
        ⇒ → caixa_cadenes
    • look — si juga iri i escena = 6
        JUGADORA: L'escotilla de la caixa de cadenes. Un cadenat nou.
        [SO: cops] NARRADOR: Cops a dins.
        JUGADORA: Juana? Juana, ets tu?
        NARRADOR: Tres cops. Més forts.
        JUGADORA: Aguanta. Vaig a buscar una cisalla. ⟨si no té cisalla⟩
        JUGADORA: Aguanta. Ara ho obro. ⟨si té cisalla⟩
        ⇒ +cops_sentits
    • look — SEMPRE
        JUGADORA: L'escotilla de la caixa de cadenes. Hi ha les cadenes de l'àncora i, diuen, una rata.
    • use + cisalla — si juga iri i escena = 6 i NO bastida_baixa i NO nus_lico
        JUGADORA: Si sent la cisalla, ve. I no vull que vingui.
        NARRADOR: Una pausa.
        JUGADORA: No sé per què no vull que vingui.
    • use + cisalla — si juga iri i escena = 6
        [SO: cisalla] JUGADORA: ...
        JUGADORA: Té una dent mellada. ⟨si NO cisalla_mellada⟩
        NARRADOR: Una pausa. ⟨si NO cisalla_mellada⟩
        JUGADORA: Aquesta matinada, quan vaig tallar la brida, no la tenia. ⟨si NO cisalla_mellada⟩
        JUGADORA: La mateixa que va tallar el cable de la ràdio.
        JUGADORA: És la cisalla del taller. Hi pot entrar tothom.
        NARRADOR: Una pausa.
        JUGADORA: Tothom que estigués despert després de les quatre.
        NARRADOR: La Vet arriba corrents per coberta: ha sentit la cisalla. ⟨si no (vet a coberta_proa)⟩
        ⇒ +cadenat_tallat, +cisalla_mellada, +prova_cisalla, −nus_lico, esdeveniment situar, → caixa_cadenes
    • open/use/pull — si juga iri i escena = 6 i NO cadenat_tallat
        JUGADORA: Tancada amb un cadenat. Nou.
    • open/use/pull — si NO cadenat_tallat
        JUGADORA: Tancada. Les cadenes no s'escapen.

JUANA «—» — hi és si escena = 2
    • look — SEMPRE
        JUGADORA: La Juana, estirada damunt d'una manta sota la balsa, embolicada fins al nas, llegint. El vent li gira les pàgines.
    • talkTo — SEMPRE
        ⇒ diàleg juana

```

## Sala Crèdits · `credits` — cinemàtica

```
```

## Sala Cuina · `cuina` (iri, vet)

```
EN ENTRAR
    • * (una vegada) — si juga vet i escena = 1
        NARRADOR: La cuina, buida i fosca a aquesta hora. El muntacàrregues és a la paret del fons.
    • * (una vegada) — si juga vet i escena = 5
        JUGADORA: En Tomàs se n'ha anat a dormir. El torn de cuina és meu: rentar, eixugar i desar. Glamur.

DECORAT armari_obert — es veu si escena = 5 i vet_amagada i NO nadia_decidida
DECORAT ulls_dia — es veu si escena = 2 o escena = 3

PORTA «menjador»
    • walkTo/use/open — si juga vet i escena = 5 i NO nadia_decidida
        JUGADORA: Torn de cuina: a bord, tothom en fa. Fins que no acabi, no em moc.
    • walkTo/use/open — SEMPRE
        ⇒ → menjador
    • look — SEMPRE
        JUGADORA: La porta del menjador.

MUNTA «muntacàrregues»
    • look — si juga vet
        JUGADORA: El muntacàrregues. Tres botons: CUINA, REBOST, PONT.
        JUGADORA: Un muntacàrregues de cuina, de quan l'Arenga portava trenta persones.
    • use + qualsevol objecte — SEMPRE
        ⇒ acció munta.enviar
    • use — si juga vet i munta_cuina = ""
        JUGADORA: Si l'envio buit, no hi haurà res a l'altra banda. Això ho entenc fins i tot jo.

SAFATA «safata del muntacàrregues» — hi és si munta_cuina ≠ ""
    • look — SEMPRE
        ⇒ acció munta.mirar
    • pickUp/open/use — si munta_cuina = "nota_iri"
        JUGADORA: Un paper doblegat. Lletra de l'Iri.
        NARRADOR: «Cada cosa que diem pel walkie, algú hi arriba primer. Ens escolten. Ni una paraula.»
        JUGADORA: Escric a sota.
        NARRADOR: «Doncs diguem-los alguna cosa.»
        ⇒ munta_cuina := "", +nota_llegida, acció munta.nota
    • pickUp/open/use — SEMPRE
        ⇒ acció munta.recollir

BOCA «boca del tub de veu»
    • look — si NO tub_de_veu
        JUGADORA: Una trompeta de llautó a la paret. «PONT · MÀQUINES · INFERMERIA».
    • look — SEMPRE
        JUGADORA: La boca del tub de veu. Des del menjador també se sent.
    • talkTo/use — si NO tub_de_veu
        JUGADORA: Hola? ...Res. Fa anys que ningú no hi parla.
    • talkTo/use — SEMPRE
        ⇒ −cara_a_cara, diàleg tub

CAMBRA_FREDA «cambra freda»
    • look — SEMPRE
        JUGADORA: La cambra freda. Llet, ous, i el que queda de les postres.
    • open — si escena ≥ 7
        JUGADORA: El flam continua aquí, sencer. Al final, ningú no se l'ha empassat.
    • open — si escena > 5 o nota_llegida
        JUGADORA: Fa fred. Aquí no hi ha cap mostra. Només un flam trist.
    • open — SEMPRE
        JUGADORA: Fa fred, i fa olor de peix. Normal.

ARMARI «armari de les olles»
    • open/use — si juga vet i escena = 5 i mentida_dita i NO vet_amagada
        NARRADOR: La Vet s'amaga dins l'armari de les olles i mira per l'escletxa.
        NARRADOR: Passa un minut. En passen tres.
        NARRADOR: Entra la Nadia, amb el mòbil a la mà, i obre la cambra freda.
        NADIA VIDAL: Sí. Ja hi soc.
        VET: Bon vespre.
        NADIA VIDAL: ...Tenia gana de postres.
        VET: Les postres d'avui són una mentida. L'hem dita pel walkie.
        ⇒ +vet_amagada, diàleg nadia
    • open/use — si juga vet i escena = 5 i nota_llegida i NO nadia_decidida
        JUGADORA: Amagar-me per què? Encara no hem dit res.
    • look — SEMPRE
        JUGADORA: L'armari de les olles. Hi cabria una persona. Una persona petita, que no tingui por de les paelles.
    • open — SEMPRE
        JUGADORA: Olles, paelles i una cassola que sembla un casc.

FORN «forn»
    • look — si escena = 6
        JUGADORA: El forn. Fa olor de pa.
    • look — SEMPRE
        JUGADORA: El forn. Encara està tebi.

TOMAS «—» — hi és si (escena = 2 i pacient ≠ "tomas") o escena = 6 o escena = 7
    • look — SEMPRE
        JUGADORA: En Tomàs. Farina fins als colzes, i un davantal amb les taques de tota una vida.
    • talkTo — SEMPRE
        ⇒ diàleg tomas

NADIA «—» — hi és si escena = 5 i vet_amagada i NO nadia_decidida
    • look — SEMPRE
        JUGADORA: La Nadia, amb la cambra freda oberta i el mòbil a punt. Enxampada.
    • talkTo — SEMPRE
        ⇒ diàleg nadia

```

## Sala Dipòsit 2 · `diposit2` (iri, vet)

```
EN ENTRAR
    • * (una vegada) — SEMPRE
        NARRADOR: Dins del dipòsit fa fred, i ressona com una catedral petita.

REGISTRE «registre»
    • walkTo/use/open — SEMPRE
        ⇒ → rebost
    • look — SEMPRE
        JUGADORA: El registre, cap al rebost.

FILTRE «carcassa del filtre»
    • look — si NO mostra_trobada
        JUGADORA: La carcassa del filtre. Hi ha una bossa a dins.
    • look — SEMPRE
        JUGADORA: La carcassa del filtre. Buida.
    • open/pickUp/use — si NO mostra_trobada
        [SO: pot] JUGADORA: Un pot de fang, dins d'una bossa segellada.
        JUGADORA: «Mostra 7 — Punt 7 — SK-4».
        JUGADORA: On ningú no beu.
        ⇒ +mostra_trobada, rep mostra7, perd clau_tubs (iri), −clau_tubs_fora, perd clau_tomas (vet)
    • open/pickUp/use — SEMPRE
        JUGADORA: Ja no hi ha res més.

CARTELL «cartell»
    • look — SEMPRE
        JUGADORA: «AIGUA NO POTABLE». En lletra de 1984. Amb una gota que somriu.

```

## Sala Galway · `final_galway` — cinemàtica

```
DECORAT tele_apagada — es veu si tele_apagada

IRI «—»

VET «—»

DIU «—»

NADIA «—» — hi és si aliada_nadia

CAPITANA «—» — hi és si aliada_capitana

MARCEL «—» — hi és si aliat_marcel

TOMAS «—» — hi és si tomas_content

```

## Sala Infermeria · `infermeria` (iri, vet)

```
EN ENTRAR
    • * (una vegada) — si escena = 1 i vet_desperta
        NARRADOR: A la infermeria, la Vet s'incorpora, amb els ulls plens de son.
        VET: Una barra de metall. D'un pam i mig. A les quatre de la matinada.
        VET: On és la proa, aquí? Bé. És igual.
    • * (una vegada) — si escena = 3
        IRI: Vet. Vull veure el cable de la ràdio abans que l'Ernest l'arregli.
        VET: No te'n fies.
        IRI: No és que no me'n fiï. És que vull mirar-ho. És diferent.
        VET: No ho és.
        IRI: Entretén-lo. Soc a la sala de ràdio, just a sobre teu.
        NARRADOR: En Bastida treu el cap per la porta.
        ERNEST BASTIDA: Em buscaves, doctora?
        VET: La revisió, Ernest. Cinc minuts. És obligatòria.
        ERNEST BASTIDA: Cinc.
        NARRADOR: Es recolza a la llitera. Mira la porta.
        ERNEST BASTIDA: Per cert. La Juana encara té aquelles mostres? A la cambra freda estarien més segures.
        NARRADOR: Mira la cafetera.
        ERNEST BASTIDA: El cafè de la infermeria. El pitjor del vaixell. Algun dia te'n faré un de bo.
        ⇒ +prova_cambra, +bastida_cafe, +sync_radio, paciencia := 0, coberta := 0
    • * (una vegada) — si escena = 7
        NARRADOR: La Juana surt de la caixa de cadenes tremolant, i la Vet no la deixa moure de la llitera.
        JUANA FERRER: Estic bé.
        VET: Tens hipotèrmia lleu. Metgessa. Mana la metgessa.
        ⇒ diàleg juana
    • * — si escena = 7 i té mostra7
        ⇒ diàleg juana

DECORAT sense_travesser — es veu si travesser_tret
DECORAT mantes — es veu si escena = 7 o (escena = 8 i NO reunio_comencada)
DECORAT ulls_dia — es veu si escena = 2 o escena = 3
DECORAT ulls_dia_mar — es veu si escena = 2 o escena = 3

PORTA «passadís»
    • walkTo/use/open — si escena = 1 i NO vet_desperta
        JUGADORA: Encara no sé ni on soc.
    • walkTo/use/open — si escena = 2 i pacient ≠ ""
        JUGADORA: Primer acabo la revisió.
    • walkTo/use/open — si juga vet i escena = 3 i NO radio_feta
        JUGADORA: Si me'n vaig, en Bastida també.
    • walkTo/use/open — si escena = 7 i juga vet i NO juana_parla
        JUGADORA: Primer, la Juana.
    • walkTo/use/open — SEMPRE
        ⇒ → passadis
    • look — SEMPRE
        JUGADORA: La porta del passadís.

LLITERA «llitera de rescat»
    • look — si juga vet i NO travesser_tret
        JUGADORA: La llitera de rescat. Ningú no l'ha desmuntada mai.
    • look — SEMPRE
        JUGADORA: La llitera de rescat, sense un travesser. Ningú no ho notarà. Espero.
    • pickUp/use/pull/open — si juga vet i escena = 1 i vet_desperta i NO travesser_tret
        [SO: travesser] JUGADORA: Doncs avui serà la primera vegada.
        JUGADORA: Un travesser d'acer. D'un pam i mig, i més.
        ⇒ +travesser_tret, rep travesser
    • pickUp/use/pull/open — si travesser_tret
        JUGADORA: Ja li falta un travesser. Amb un n'hi ha prou.
    • pickUp/use/pull/open — SEMPRE
        JUGADORA: Una llitera de rescat s'ha de poder fer servir. No la desmunto per gust.

ARMARI «armari»
    • look — si juga vet
        JUGADORA: L'armari de la infermeria. Gases, iode, benes. I el jersei de llana del Ferran, que ara porto jo.
    • open — SEMPRE
        JUGADORA: Gases, iode, benes, un tensiòmetre i una ampolla d'alguna cosa que va deixar el metge d'abans. No és alcohol de ferides.

FITXES «fitxes mèdiques»
    • look — si escena < 2
        JUGADORA: Les fitxes mèdiques de la tripulació. Nom i contacte d'emergència, de l'embarcament. La revisió, en blanc: ningú no l'ha passada.
    • look — si escena = 2
        JUGADORA: Les fitxes mèdiques. Encara no he fet cap revisió. ⟨si revisions = 0⟩
        JUGADORA: Les fitxes mèdiques. Una revisió feta. ⟨si revisions = 1⟩
        JUGADORA: Les fitxes mèdiques. Dues revisions fetes. ⟨si revisions = 2⟩
        JUGADORA: Les fitxes mèdiques. Tres revisions fetes. ⟨si revisions = 3⟩
        JUGADORA: Les fitxes mèdiques. Quatre revisions fetes. ⟨si revisions ≥ 4⟩
    • look — SEMPRE
        JUGADORA: Les fitxes mèdiques de tothom.
    • use — si escena = 2 i pacient = ""
        ⇒ diàleg fitxes
    • use — si escena = 2
        JUGADORA: Primer acabo amb qui tinc aquí.
    • use/open/pickUp — si escena ≠ 2
        JUGADORA: Les deixo a lloc. Hi ha la vida de tothom, i no és meva.

CAFETERA «cafetera»
    • look — SEMPRE
        JUGADORA: La cafetera de la infermeria. Fa un cafè que no recomanaria a cap pacient.
    • use — SEMPRE
        JUGADORA: No. Ja n'he pres un, i encara el noto.

BOCA «boca del tub de veu»
    • look — si NO tub_de_veu
        JUGADORA: A la porta hi ha una boca de llautó. «PONT · MÀQUINES · CUINA».
    • look — SEMPRE
        JUGADORA: La boca del tub de veu.
    • talkTo/use — si NO tub_de_veu
        JUGADORA: Hola? ...Res. Una trompeta morta.
    • talkTo/use — SEMPRE
        ⇒ −cara_a_cara, diàleg tub

CAPITANA «—» — hi és si escena = 2 i pacient = "capitana"
    • look — SEMPRE
        JUGADORA: La Capitana. Tensió perfecta, mirada de paret. Res que no quadri.
    • talkTo — SEMPRE
        ⇒ diàleg capitana

TOMAS «—» — hi és si escena = 2 i pacient = "tomas"
    • look — SEMPRE
        JUGADORA: En Tomàs. Farina fins a les orelles. Res que no quadri.
    • talkTo — SEMPRE
        ⇒ diàleg tomas

NADIA «—» — hi és si escena = 2 i pacient = "nadia"
    • look — si nadia_mareig
        JUGADORA: Diu que té mareig. Però a l'esmorzar ha repetit croissant.
        JUGADORA: Dos.
        ⇒ +nadia_croissant
    • look — SEMPRE
        JUGADORA: La periodista. Bon color de cara. Massa bon color.
        JUGADORA: Que parli ella primer.
    • talkTo — SEMPRE
        ⇒ diàleg nadia

MARCEL «—» — hi és si escena = 2 i pacient = "marcel"
    • look — SEMPRE
        JUGADORA: Té pèls de gat al jersei.
        JUGADORA: I fa olor de sardina.
        ⇒ +marcel_gat
    • talkTo — SEMPRE
        ⇒ diàleg marcel

BASTIDA «—» — hi és si escena = 3 i NO radio_feta
    • look — SEMPRE
        JUGADORA: En Bastida, recolzat a la llitera. Mira la porta més que a mi.
    • talkTo — SEMPRE
        ⇒ diàleg bastida

JUANA «—» — hi és si escena = 7 o (escena = 8 i NO reunio_comencada)
    • look — si juga vet
        JUGADORA: La Juana, amb dues mantes. Ja no tremola.
    • talkTo — SEMPRE
        ⇒ diàleg juana

```

## Sala Laboratori · `laboratori` (iri, vet)

```
EN ENTRAR
    • * (una vegada) — si juga iri i escena = 4
        NARRADOR: La Juana no ha vingut a sopar. Tothom diu el mateix: «Està descansant. Ja la coneixeu.»
        JUGADORA: La conec. No es perd mai un sopar.
        NARRADOR: Al costat del portàtil hi ha una nota.
    • * (una vegada) — si juga iri i escena = 5
        NARRADOR: L'Iri torna al laboratori. El portàtil no hi és.
        JUGADORA: Se l'han endut.
        JUGADORA: Sort de la còpia.
        JUGADORA: El laboratori, remenat aquesta tarda, després que la Vet digués «amb la mostra a bord».
        JUGADORA: En Bastida, preguntant per les mostres just després que la Vet parlés amb la Juana.
        JUGADORA: I el portàtil, desaparegut just després de dir que l'havia obert.
        JUGADORA: Tot el que hem dit pel walkie.
        JUGADORA: Ens escolten.
        ⇒ +portatil_robat

DECORAT remenat — es veu si escena ≥ 4
DECORAT ulls_dia — es veu si escena = 2 o escena = 3
DECORAT ulls_dia_mar — es veu si escena = 2 o escena = 3

PORTA «passadís»
    • walkTo/use/open — SEMPRE
        ⇒ → passadis
    • look — SEMPRE
        JUGADORA: La porta del passadís.

PORTATIL «portàtil» — hi és si escena < 5
    • look — si NO portatil_obert
        JUGADORA: El portàtil de la Juana. Amb contrasenya.
    • look — si juga iri
        JUGADORA: El portàtil de la Juana. Ja en tinc la còpia.
    • use — si juga vet
        JUGADORA: Contrasenya. No la sé. I no és meu.
    • use — si escena = 4 i NO portatil_obert
        ⇒ diàleg portatil
    • use — si juga iri i portatil_obert
        JUGADORA: Ja en tinc la còpia, a l'USB.

LLIBRE «llibre de peixos»
    • look — si juga vet
        JUGADORA: «Peixos de l'Atlàntic Nord». Ple de notes al marge, en lletra petitíssima.
    • look — si juga iri i escena ≥ 4
        JUGADORA: «Peixos de l'Atlàntic Nord». A dins hi ha una postal.
        NARRADOR: «Per molts anys, filla. T'estimo. La mare.»
        JUGADORA: Sense nom. Al costat, la Juana hi ha escrit: «Pili 65».
        JUGADORA: Pili. Seixanta-cinc. Com a contrasenya és massa curta.
        ⇒ +postal_vista
    • look — SEMPRE
        JUGADORA: «Peixos de l'Atlàntic Nord». No és meu.

NOTA «nota» — hi és si escena = 4
    • look — si juga iri
        NARRADOR: «Si no torno, el portàtil. J.»
        JUGADORA: És per a la Vet: és a ella que li va dir com era la contrasenya.
        JUGADORA: «Si no torno.» I no ha tornat.
        JUGADORA: El portàtil té contrasenya. La Juana li va dir a la Vet que és el nom de la seva mare.
        ⇒ +nota_juana

NEVERA «nevera de mostres»
    • look — SEMPRE
        JUGADORA: La nevera de mostres. Pots etiquetats: Punt 3, Punt 4, Punt 5, Punt 6...
        JUGADORA: El 7 no hi és.
    • open — SEMPRE
        JUGADORA: Fred i pots. Cap no és el 7.

JUANA «—» — hi és si escena = 3
    • look — SEMPRE
        JUGADORA: La Juana, comptant ous en una placa. No aixeca el cap.
    • talkTo — SEMPRE
        JUANA FERRER: Ara no. Estic comptant. Si em parles, perdo el compte, i si perdo el compte, plorarem totes dues.

TAULELL «taulell»
    • look — si escena < 4
        JUGADORA: Tot endreçat, com un quiròfan. La Juana és endreçada.
    • look — SEMPRE
        JUGADORA: Remenat. Calaixos mal tancats, llibres girats.
        JUGADORA: Algú ha buscat alguna cosa aquí, i ho ha volgut dissimular.

```

## Sala Menjador · `menjador` (iri, vet)

```
EN ENTRAR
    • * (una vegada) — si escena = 8 i reunio_comencada i juga vet
        ⇒ diàleg reunio

DECORAT ulls_dia — es veu si escena = 2 o escena = 3

PORTA_PASSADIS «passadís»
    • walkTo/use/open — SEMPRE
        ⇒ → passadis
    • look — SEMPRE
        JUGADORA: La porta del passadís.

PORTA_CUINA «cuina»
    • walkTo/use/open — si juga iri
        JUGADORA: La cuina és d'en Tomàs. Si hi entro, em posa a pelar patates.
    • walkTo/use/open — SEMPRE
        ⇒ → cuina
    • look — SEMPRE
        JUGADORA: La cuina.

PORTA_POPA «coberta de popa»
    • walkTo/use/open — si juga vet i escena = 1
        JUGADORA: A coberta? De nit, amb aquest vent? Ni parlar-ne.
    • walkTo/use/open — si juga iri
        JUGADORA: De nit i amb aquest vent, a coberta no hi tinc res a fer.
    • walkTo/use/open — SEMPRE
        ⇒ → coberta_popa
    • look — SEMPRE
        JUGADORA: La porta de popa. A fora, el mar.

PASSAPLATS «passaplats»
    • look — SEMPRE
        JUGADORA: El passaplats de la cuina. Tot el que es diu a la cuina se sent aquí. I al revés.
    • talkTo — si tub_de_veu
        ⇒ −cara_a_cara, diàleg tub

POSTER «pòster»
    • look — SEMPRE
        JUGADORA: «CIMERA DELS OCEANS · PORT HALLEN». A sota: «Patrocinada per Skarn. Els metalls de la transició verda.»
        JUGADORA: Una balena somriu al costat d'un cotxe elèctric.

TAULA «taula»
    • use/talkTo — si escena = 8 i juga vet i NO reunio_comencada
        JUGADORA: La reunió, la convoca la Capitana. És el seu vaixell.
    • talkTo — si escena = 8 i reunio_comencada i juga vet
        ⇒ diàleg reunio
    • use/talkTo — si escena = 8 i juga iri
        JUGADORA: Ho ha de dir la Vet. És ella qui ha fet les revisions.
    • look — SEMPRE
        JUGADORA: La taula llarga del menjador. Quaranta anys de cafès, de cartes i de mapes.

CAPITANA «—» — hi és si escena = 8 i reunio_comencada
    • look — SEMPRE
        JUGADORA: La Capitana, dreta al cap de la taula. No ha tocat el te.
    • talkTo — si escena = 8 i reunio_comencada i juga vet
        ⇒ diàleg reunio
    • talkTo — si escena = 8 i reunio_comencada
        NARRADOR: Tothom espera que la doctora parli.
    • talkTo — SEMPRE
        ⇒ diàleg capitana

BASTIDA «—» — hi és si escena = 8 i reunio_comencada
    • look — SEMPRE
        JUGADORA: En Bastida. La pipa apagada, i les mans quietes damunt la taula. Massa quietes.
    • talkTo — si escena = 8 i reunio_comencada
        NARRADOR: Tothom espera que la doctora parli.
    • talkTo — SEMPRE
        ⇒ diàleg bastida

MARCEL «—» — hi és si escena = 8 i reunio_comencada
    • look — SEMPRE
        JUGADORA: El Marcel, encongit a la cadira, com si l'acusat fos ell.
    • talkTo — si escena = 8 i reunio_comencada
        NARRADOR: Tothom espera que la doctora parli.
    • talkTo — SEMPRE
        ⇒ diàleg marcel

TOMAS «—» — hi és si escena = 8 i reunio_comencada
    • look — SEMPRE
        JUGADORA: En Tomàs ha portat te i galetes. Ningú no en menja.
    • talkTo — si escena = 8 i reunio_comencada
        NARRADOR: Tothom espera que la doctora parli.
    • talkTo — SEMPRE
        ⇒ diàleg tomas

JUANA «—» — hi és si escena = 8 i reunio_comencada
    • look — SEMPRE
        JUGADORA: La Juana, amb dues mantes i la bossa a la falda. No la deixarà anar.
    • talkTo — si escena = 8 i reunio_comencada
        NARRADOR: Tothom espera que la doctora parli.
    • talkTo — SEMPRE
        ⇒ diàleg juana

NADIA «—» — hi és si (escena = 6 i aliada_nadia) o ((escena = 8 i reunio_comencada) i aliada_nadia)
    • look — SEMPRE
        JUGADORA: La Nadia, amb el mòbil a la mà. Ara treballa per a nosaltres. Crec.
    • talkTo — si escena = 8 i reunio_comencada
        NARRADOR: Tothom espera que la doctora parli.
    • talkTo — SEMPRE
        ⇒ diàleg nadia

```

## Sala Pal · `pal` (iri, vet)

```
EN ENTRAR
    • * (una vegada) — si escena = 9 i juga iri i aliat_marcel
        NARRADOR: Dalt del pal, el vent ho vol tot.
        MARCEL: La tinc, Iri. Ja està desbloquejada. Volta de més inclosa.
        ⇒ +antena_desbloquejada, +iri_al_pal
    • * (una vegada) — si escena = 9 i juga iri i NO iri_al_pal
        NARRADOR: Dalt del pal, el vent ho vol tot.
        JUGADORA: No miris avall.
        ⇒ +iri_al_pal

DECORAT fosc — es veu si escena = 9 i NO rele_posat

ESCALA «escala»
    • walkTo/use/open — SEMPRE
        ⇒ → pont
    • look — SEMPRE
        JUGADORA: Avall. A poc a poc.

ANTENA «antena»
    • use + cisalla — si NO antena_desbloquejada
        JUGADORA: Amb la cisalla, no. Aquí dalt, si rellisca, l'antena acaba al mar. El nus es desfà amb els dits.
    • look — si NO antena_desbloquejada
        JUGADORA: L'antena del satèl·lit. Desorientada. I lligada amb un nus Bastida, amb una volta de més.
    • look — si NO antena_ok
        JUGADORA: L'antena. Desbloquejada. Falta girar-la fins al senyal.
    • look — SEMPRE
        JUGADORA: L'antena, cap al satèl·lit. Ara, avall, al terminal.
    • use — si NO antena_desbloquejada
        [SO: clau_tubs] JUGADORA: El nus, fora. Volta de més inclosa.
        ⇒ +antena_desbloquejada
    • use — si NO antena_ok
        [SO: antena] JUGADORA: Una mica més... Aquí. Senyal.
        ⇒ +antena_ok
    • use — SEMPRE
        JUGADORA: Ja apunta on toca. No la toco més.

MARCEL «—» — hi és si escena = 9 i aliat_marcel
    • look — SEMPRE
        JUGADORA: El Marcel, agafat a la barana amb les dues mans. Diu que no té por. Té por.
    • talkTo — SEMPRE
        JUGADORA: Marcel.
        MARCEL: Aquí. Agafat. Fes via, que fa fred.

MAR «mar»
    • look — SEMPRE
        JUGADORA: No miris avall. No miris avall.
        JUGADORA: He mirat avall.

```

## Sala Pallol · `pallol` (iri, vet)

```
DECORAT cadenat_sise — es veu si escena < 4

PORTA «passadís»
    • walkTo/use/open — SEMPRE
        ⇒ → passadis_baix
    • look — SEMPRE
        JUGADORA: La porta del passadís.

PRESTATGES «prestatges»
    • look — si juga iri i escena = 3
        JUGADORA: Cable apantallat, connectors, cinta, caps. Tot el que algun dia pot fer falta.
    • look — SEMPRE
        JUGADORA: Caps, pintura, cadenats, cable. El pallol de l'Arenga.
    • pickUp — si escena = 3 i sync_radio i no té cable_nou (iri) i empalmat < 2
        JUGADORA: Cable apantallat i un connector. Amb això n'hi ha prou.
        ⇒ rep cable_nou
    • pickUp — si escena = 3 i té cable_nou (iri)
        JUGADORA: Ja en tinc prou.

INVENTARI «inventari»
    • look — si escena ≥ 4
        JUGADORA: L'inventari del pallol, clavat a la porta. Cadenats: sis.
        JUGADORA: Aquí n'hi ha cinc.
        ⇒ +cadenat_falta
    • look — SEMPRE
        JUGADORA: L'inventari del pallol. Tot quadra. En Bastida el porta al dia.

MARCEL «—» — hi és si escena ≥ 6 i escena ≤ 7
    • look — si juga iri
        JUGADORA: El Marcel, recolzat a les caixes. I en Diu, als seus peus, menjant sardines.
    • talkTo — SEMPRE
        ⇒ diàleg marcel

DIU «—» — hi és si escena ≥ 6 i escena ≤ 7

```

## Sala Passadís · `passadis` (iri, vet)

```
EN ENTRAR
    • * — si escena = 6 i NO planol_vist i NO mapa_agafat i juga vet
        JUGADORA: Cinc llocs on mirar, i jo encara confonc babord amb estribord.
        JUGADORA: Aquell plànol de la paret m'aniria bé.
        ⇒ +planol_vist
    • * — si escena = 6 i NO planol_vist i NO mapa_agafat i juga iri
        JUGADORA: Ara cal mirar per tot el vaixell. La Vet, amb el plànol de la paret, ho faria més de pressa.
        ⇒ +planol_vist

DECORAT ulls_dia — es veu si escena = 2 o escena = 3

PORTA_MENJADOR «menjador»
    • walkTo/use/open — si juga iri i escena = 5 i NO pla_fet
        JUGADORA: Al menjador hi ha tothom fent el te. Si entro a xiuxiuejar-li coses a la Vet, ho veurà qui no ho ha de veure.
    • walkTo/use/open — si juga iri i escena = 5
        JUGADORA: Ara no. La Vet ha de semblar sola a la cuina.
    • walkTo/use/open — si juga iri i escena = 3
        JUGADORA: Ara no. Si l'Ernest em veu, sabrà que no soc a dormir.
    • walkTo/use/open — si juga iri i no (escena = 8 i reunio_comencada)
        JUGADORA: Al menjador, ara, no hi tinc res a fer. I com menys em vegin voltar pel vaixell, millor.
    • walkTo/use/open — SEMPRE
        ⇒ → menjador
    • look — SEMPRE
        JUGADORA: El menjador. I la cuina, al fons.

PORTA_INFERMERIA «infermeria»
    • walkTo/use/open — si juga iri i escena = 3 i NO radio_feta
        JUGADORA: Ara no. Si l'Ernest em veu, sabrà que no soc a dormir.
    • walkTo/use/open — si juga iri i escena = 4
        JUGADORA: La Vet està amb les seves fitxes. Si la necessito, pel walkie.
    • walkTo/use/open — si juga iri
        JUGADORA: A la infermeria només hi entro si sagno. I avui no sagno.
    • walkTo/use/open — SEMPRE
        ⇒ → infermeria
    • look — si juga vet
        JUGADORA: La infermeria. La meva consulta. Fa olor de iode i de mar.
    • look — SEMPRE
        JUGADORA: La infermeria.

PORTA_LABORATORI «laboratori»
    • walkTo/use/open — si juga vet i escena = 1
        JUGADORA: El laboratori de la biòloga. A les fosques, i no és meu.
    • walkTo/use/open — SEMPRE
        ⇒ → laboratori
    • look — SEMPRE
        JUGADORA: El laboratori de la Juana.

PORTA_CAPITANA «cabina de la Capitana»
    • walkTo/use/open — si escena = 1
        JUGADORA: Si la desperto, haurà de baixar a veure-ho. I la maquinista diu que hi ha coses que no ha de veure.
    • walkTo/use/open — si escena = 3
        JUGADORA: La Capitana és al pont, i aquesta és casa seva. Ara no.
    • walkTo/use/open — si juga iri i escena = 4
        JUGADORA: La Capitana dorm. I quan dorm, mossega més que en Diu.
    • walkTo/use/open — si juga iri i escena = 5
        JUGADORA: La Capitana no hi és. I la seva cabina no és lloc per entrar-hi sense ella.
    • walkTo/use/open — si juga iri i reunio_comencada
        JUGADORA: La Capitana no hi és. I la seva cabina no és lloc per entrar-hi sense ella.
    • walkTo/use/open — si juga iri
        JUGADORA: Si pico a la cabina, la Capitana voldrà saber què hi faig, fora de màquines.
    • walkTo/use/open — SEMPRE
        ⇒ → cabina_capitana
    • look — SEMPRE
        JUGADORA: La porta de la cabina de la Capitana. «TRUQUEU ABANS». I a sota, a llapis: «I DESPRÉS NO ENTREU».

ESCALA_AMUNT «escala del pont»
    • walkTo/use/open — si juga vet i escena = 1 i travesser_tret
        JUGADORA: No. Tinc una maquinista que s'enfonsa, i el travesser és per a ella.
    • walkTo/use/open — si juga vet i escena = 1
        JUGADORA: No. Tinc una maquinista que s'enfonsa, i un travesser per trobar.
    • walkTo/use/open — si juga vet i escena = 3
        JUGADORA: Ara no.
    • walkTo/use/open — si juga vet i escena = 2
        JUGADORA: El pont és de la Capitana, i a la Capitana no li agraden les visites.
    • walkTo/use/open — si juga vet i escena = 8 i NO reunio_comencada
        JUGADORA: L'Iri està de guàrdia al pont. La Capitana ha dit que ningú no la distregui.
    • walkTo/use/open — si juga vet
        JUGADORA: El pont és de l'Iri i de la Capitana. Jo allà dalt només faria nosa.
    • walkTo/use/open — SEMPRE
        ⇒ → pont
    • look — SEMPRE
        JUGADORA: L'escala del pont.

ESCALA_AVALL «escala de baix»
    • walkTo/use/open — si juga vet i escena = 1
        JUGADORA: La maquinista ha dit «muntacàrregues». No discutiré amb algú que té el vaixell ple d'aigua.
    • walkTo/use/open — si juga vet
        JUGADORA: A baix hi ha les màquines i la maquinista. Totes dues de mal humor.
    • walkTo/use/open — SEMPRE
        ⇒ → passadis_baix
    • look — SEMPRE
        JUGADORA: L'escala que baixa a la sala de màquines i als camarots de la tripulació.

PORTA_PROA «porta de proa»
    • walkTo/use/open — si juga vet i escena = 1
        JUGADORA: A coberta? De nit, amb aquest vent? Ni parlar-ne.
    • walkTo/use/open — si juga iri i (escena = 4 o escena = 5 o escena = 8)
        JUGADORA: De nit i amb aquest vent, a coberta no hi tinc res a fer.
    • walkTo/use/open — si juga vet i escena = 6
        JUGADORA: Si en Bastida em veu anar cap a proa, sabrà on busquem. Me'l quedo jo.
    • walkTo/use/open — SEMPRE
        ⇒ → coberta_proa
    • look — SEMPRE
        JUGADORA: La porta de coberta, cap a proa.

PLANOL «plànol d'emergència»
    • look — si juga iri
        JUGADORA: El plànol d'emergència. Me'l sé de memòria: tres campanyes.
        JUGADORA: A sota hi ha còpies plastificades, per a qui no se'l sap.
    • look — SEMPRE
        JUGADORA: El plànol d'emergència. Un punt vermell: «Sou aquí». Gràcies.
        JUGADORA: A sota hi ha còpies plastificades. Per a qui no sap on és la proa, suposo.
    • pickUp/use — si mapa_agafat
        JUGADORA: Ja en tenim un. Amb un n'hi ha prou.
    • pickUp/use — si escena ≥ 6 i juga iri
        JUGADORA: Jo no el necessito. Però així no camino.
        ⇒ rep mapa, +mapa_agafat
    • pickUp/use — si escena ≥ 6
        JUGADORA: Quaranta metres de vaixell. I em cal un plànol.
        ⇒ rep mapa, +mapa_agafat
    • pickUp/use — si juga iri
        JUGADORA: No el necessito. Me'l sé de memòria.
    • pickUp/use — SEMPRE
        JUGADORA: Ara no tinc temps ni de perdre'm.

```

## Sala Passadís de baix · `passadis_baix` (iri, vet)

```
EN ENTRAR
    • * (una vegada) — si escena = 1
        [SO: miol] NARRADOR: Un miol, darrere la porta de la sala de màquines.

PORTA_CAMAROT «camarot de l'Iri»
    • walkTo/use/open — SEMPRE
        ⇒ → camarot_iri
    • look — si juga iri
        JUGADORA: El meu camarot. El més petit del vaixell, al costat de les màquines. El vaig triar jo.

PORTA_MAQUINES «sala de màquines»
    • use + maceta — si NO falca_desencallada
        [SO: cops] JUGADORA: Un cop. Dos. Tres. La falca salta.
        [SO: porta_estanca] JUGADORA: La maceta, la deixo penjada aquí. Tornarà a fer falta.
        ⇒ perd maceta, +falca_desencallada, → sala_maquines
    • walkTo/use/open — si escena = 1 i NO falca_desencallada i té maceta
        JUGADORA: La falca de baix, encallada. Com sempre. Un cop de maceta i va.
    • walkTo/use/open — si escena = 1 i NO falca_desencallada
        JUGADORA: La falca de baix no es mou. S'encalla des de l'agost, i ningú no l'arregla perquè jo hi baixo cada dia.
        JUGADORA: Per això tinc una maceta penjada al camarot.
    • walkTo/use/open — SEMPRE
        ⇒ → sala_maquines
    • look — si escena = 1
        JUGADORA: La sala de màquines. Darrere, un miol.
    • look — SEMPRE
        JUGADORA: La sala de màquines.

REPETIDOR «repetidor d'alarmes»
    • look — si escena = 1 i juga iri
        JUGADORA: El repetidor d'alarmes de la sala de màquines: sentina, incendi, gasoil, temperatura. Tot verd.
        JUGADORA: Tot verd, i el vaixell assegut de popa. Un dels dos menteix, i el vaixell no sap mentir.
    • look — si juga iri
        JUGADORA: El repetidor d'alarmes. Des de la nit de la vàlvula, no me'n refio gens.
    • push/use — si juga iri
        JUGADORA: El botó de prova encén totes les alarmes del vaixell. Despertaria tothom. I la Capitana, la primera.

PETJADES «petjades» — hi és si escena = 1
    • look — SEMPRE
        JUGADORA: Petjades mullades, petites. Van i venen entre el meu camarot i la porta de màquines.
        JUGADORA: En Diu ha trepitjat aigua. I dins del vaixell, l'aigua no hi ha de ser.
    • pickUp — SEMPRE
        JUGADORA: Són petjades. No s'agafen. S'interpreten.

PORTA_PALLOL «pallol»
    • walkTo/use/open — si escena = 1 i juga iri
        JUGADORA: Ara no. Primer, en Diu. I l'aigua.
    • walkTo/use/open — SEMPRE
        ⇒ → pallol
    • look — SEMPRE
        JUGADORA: El pallol: caps, cadenats, pintura i tot el que algun dia pot fer falta.

ESCOTILLA «escotilla de la sala de bombes»
    • walkTo/use/open — si escena = 1 i juga iri
        JUGADORA: Ara no. Primer, en Diu. I l'aigua.
    • walkTo/use/open — si escena < 4
        JUGADORA: La sala de bombes. Allà no hi baixa ningú. Ni jo, si puc.
    • walkTo/use/open — SEMPRE
        ⇒ → sala_bombes
    • look — SEMPRE
        JUGADORA: L'escotilla de la sala de bombes. Allà no hi baixa mai ningú.

ESCALA «escala»
    • walkTo/use/open — si escena = 1 i juga iri
        JUGADORA: Ara no. Primer, en Diu. I l'aigua.
    • walkTo/use/open — SEMPRE
        ⇒ → passadis
    • look — SEMPRE
        JUGADORA: L'escala cap a la coberta principal.

```

## Sala Pont · `pont` (iri, vet)

```
DECORAT dia — es veu si escena = 2 o escena = 3
DECORAT guardacostes — es veu si escena ≥ 8 i NO rumb_galway
DECORAT fosc — es veu si escena = 9 i NO rele_posat

ESCALA «escala»
    • walkTo/use/open — si juga iri i escena = 8 i NO reunio_comencada
        JUGADORA: Estic de guàrdia. Si deixo el timó, el pilot automàtic fa el que vol.
    • walkTo/use/open — si juga iri i escena = 9 i NO enviat
        JUGADORA: No. Les dades, primer.
    • walkTo/use/open — SEMPRE
        ⇒ → passadis
    • look — SEMPRE
        JUGADORA: L'escala cap al passadís.

PORTA_RADIO «sala de ràdio»
    • walkTo/use/open — SEMPRE
        ⇒ → sala_radio
    • look — SEMPRE
        JUGADORA: La sala de ràdio.

ESCALA_PAL «escala del pal»
    • walkTo/use/open — si escena < 9
        JUGADORA: Amb aquest vent, al pal no s'hi puja. Només si no hi ha més remei.
    • walkTo/use/open — SEMPRE
        ⇒ → pal
    • look — SEMPRE
        JUGADORA: L'escala del pal. A dalt, l'antena del satèl·lit. I el vent.

TERMINAL «terminal de satèl·lit»
    • look — si escena = 9 i NO antena_ok
        JUGADORA: El terminal de satèl·lit. «SENSE SENYAL»: l'antena del pal no apunta enlloc.
        NARRADOR: SAI: {sai} torns
    • look — si escena = 9
        JUGADORA: El terminal de satèl·lit. Té senyal, i el SAI encara aguanta.
        NARRADOR: «SENYAL: {senyal}» · SAI: {sai} torns
    • look — SEMPRE
        JUGADORA: El terminal de satèl·lit. «SENSE SENYAL».
    • use — si escena = 4 i NO portatil_obert
        JUGADORA: Primer, les dades. Al portàtil de la Juana.
    • use + usb — si escena = 4 i NO portatil_obert
        JUGADORA: Primer, les dades. Al portàtil de la Juana.
    • use — si escena = 4 i NO satellit_provat
        JUGADORA: Sense senyal. L'antena del pal està desorientada.
        JUGADORA: De nit i amb aquest vent, al pal no s'hi puja. Només si no hi ha més remei.
        JUGADORA: Les dades poden esperar. La Juana, no.
        ⇒ +satellit_provat
    • use + usb — si escena = 4 i NO satellit_provat
        JUGADORA: Sense senyal. L'antena del pal està desorientada.
        JUGADORA: De nit i amb aquest vent, al pal no s'hi puja. Només si no hi ha més remei.
        JUGADORA: Les dades poden esperar. La Juana, no.
        ⇒ +satellit_provat
    • use — si escena < 9 i satellit_provat
        JUGADORA: Sense senyal. Ja ho he provat.
    • use + usb — si escena < 9 i satellit_provat
        JUGADORA: Sense senyal. Ja ho he provat.
    • use — si escena < 9
        JUGADORA: «SENSE SENYAL». El satèl·lit sempre fa el que vol.
    • use + usb — si escena < 9
        JUGADORA: «SENSE SENYAL». El satèl·lit sempre fa el que vol.
    • use — si NO antena_ok
        JUGADORA: Sense senyal. Primer, l'antena.
        ⇒ +intent_buit
    • use + usb — si NO antena_ok
        JUGADORA: Sense senyal. Primer, l'antena.
        ⇒ +intent_buit
    • use — si NO enviament_iniciat i aliada_nadia
        [SO: terminal] JUGADORA: Inicio l'enviament. Amb el SAI.
        NARRADOR: Pel walkie, la veu de la Nadia:
        NADIA VIDAL: El primer paquet l'envio jo, pel telèfon de Blau Net. Que la Lind ho vegi. Quan ho vegi, ja serà tard.
        ⇒ +enviament_iniciat, sai −= 1, paquets := 1
    • use + usb — si NO enviament_iniciat i aliada_nadia
        [SO: terminal] JUGADORA: Inicio l'enviament. Amb el SAI.
        NARRADOR: Pel walkie, la veu de la Nadia:
        NADIA VIDAL: El primer paquet l'envio jo, pel telèfon de Blau Net. Que la Lind ho vegi. Quan ho vegi, ja serà tard.
        ⇒ +enviament_iniciat, sai −= 1, paquets := 1
    • use — si NO enviament_iniciat
        [SO: terminal] JUGADORA: Inicio l'enviament. Amb el SAI.
        ⇒ +enviament_iniciat, sai −= 1
    • use + usb — si NO enviament_iniciat
        [SO: terminal] JUGADORA: Inicio l'enviament. Amb el SAI.
        ⇒ +enviament_iniciat, sai −= 1
    • use — si NO rele_posat i sai ≤ 0
        JUGADORA: Sense corrent. El SAI s'ha esgotat, i el generador està parat.
        JUGADORA: Vet. Sense el relé, no envio res més.
        ⇒ +intent_buit
    • use + usb — si NO rele_posat i sai ≤ 0
        JUGADORA: Sense corrent. El SAI s'ha esgotat, i el generador està parat.
        JUGADORA: Vet. Sense el relé, no envio res més.
        ⇒ +intent_buit
    • use — si paquets = 2
        [SO: enviat] JUGADORA: Paquet 3 de 3.
        NARRADOR: «ENVIAT».
        ⇒ paquets := 3, +enviat, diàleg enviat
    • use + usb — si paquets = 2
        [SO: enviat] JUGADORA: Paquet 3 de 3.
        NARRADOR: «ENVIAT».
        ⇒ paquets := 3, +enviat, diàleg enviat
    • use — si paquets = 0 i rele_posat
        [SO: terminal] JUGADORA: Paquet 1 de 3. Enviat.
        ⇒ paquets := 1
    • use + usb — si paquets = 0 i rele_posat
        [SO: terminal] JUGADORA: Paquet 1 de 3. Enviat.
        ⇒ paquets := 1
    • use — si paquets = 0
        [SO: terminal] JUGADORA: Paquet 1 de 3. Amb el SAI.
        ⇒ paquets := 1, sai −= 1
    • use + usb — si paquets = 0
        [SO: terminal] JUGADORA: Paquet 1 de 3. Amb el SAI.
        ⇒ paquets := 1, sai −= 1
    • use — si rele_posat
        [SO: terminal] JUGADORA: Paquet 2 de 3. Enviat.
        ⇒ paquets := 2
    • use + usb — si rele_posat
        [SO: terminal] JUGADORA: Paquet 2 de 3. Enviat.
        ⇒ paquets := 2
    • use — SEMPRE
        [SO: terminal] JUGADORA: Paquet 2 de 3. Amb el SAI.
        ⇒ paquets := 2, sai −= 1
    • use + usb — SEMPRE
        [SO: terminal] JUGADORA: Paquet 2 de 3. Amb el SAI.
        ⇒ paquets := 2, sai −= 1

IMPRESSORA «impressora»
    • look — SEMPRE
        JUGADORA: La impressora del pont. Imprimeix cartes, butlletins i, si li ho demanes bé, coses que no et convenen.
    • use + usb — si escena = 8 i NO registre_impres
        [SO: impressora] JUGADORA: La carpeta «Qui ens paga el gasoil?». Imprimeixo la pàgina del registre.
        JUGADORA: La Vet l'ha de posar al costat del contracte de la Capitana.
        ⇒ +registre_impres, rep registre
    • use + usb — si registre_impres
        JUGADORA: Ja l'he impresa.
    • use + usb — SEMPRE
        JUGADORA: Ara no cal imprimir res.

MUNTA «muntacàrregues»
    • use + llibreta — si escena = 5
        JUGADORA: Des del pont? Aquí hi puja tothom a buscar cafè. Millor des del rebost: allà no hi baixa ningú.
    • look — SEMPRE
        JUGADORA: La parada de dalt del muntacàrregues: pugen cafès, baixen tasses.
    • use + qualsevol objecte — SEMPRE
        ⇒ acció munta.enviar
    • use — si munta_pont = ""
        JUGADORA: Buit no l'envio.

SAFATA «safata del muntacàrregues» — hi és si munta_pont ≠ ""
    • look — SEMPRE
        ⇒ acció munta.mirar
    • pickUp/open/use — SEMPRE
        ⇒ acció munta.recollir

BOCA «boca del tub de veu»
    • look — si tub_de_veu
        JUGADORA: La boca del tub de veu: màquines, cuina i infermeria.
    • look — SEMPRE
        JUGADORA: Una boca de llautó. Ningú no hi parla des que van posar els walkies.
    • talkTo/use — si tub_de_veu
        ⇒ −cara_a_cara, diàleg tub
    • talkTo/use — si NO tub_de_veu
        JUGADORA: Hola? ...Res. A l'altra banda deu haver-hi un pam de pols.

TIMO «timó»
    • look — si rumb_galway
        JUGADORA: El timó. Rumb a Galway.
    • look — si escena ≥ 3
        JUGADORA: El timó. Rumb a Port Hallen.
    • look — SEMPRE
        JUGADORA: El timó. Encara som al Punt 7.
    • use — si juga iri
        JUGADORA: El rumb el decideix la Capitana. Jo només el faig complir.

VIDRE «vidre»
    • look — si escena ≥ 8 i rumb_galway
        JUGADORA: Pel vidre, només el mar fosc. El guardacostes s'ha quedat enrere.
    • look — si escena ≥ 8
        JUGADORA: Pel vidre, els llums del guardacostes de Valmark. Cada cop més a prop.
    • look — SEMPRE
        JUGADORA: El mar. Gris, de nit i de dia.

CAPITANA «—» — hi és si escena = 3
    • look — SEMPRE
        JUGADORA: La Capitana, al timó. Mira el terminal del satèl·lit com si li degués diners.
    • talkTo — SEMPRE
        ⇒ diàleg capitana
    • give + tram — SEMPRE
        CAPITANA ROIG: Tallat, trencat... Me l'arregles igual, Iri. Vull avisar l'oficina.
        IRI: A bord, ningú no vol veure res.

```

## Sala Ni un ou · `portada`

```
```

## Sala Postcrèdits · `postcredits` — cinemàtica

```
```

## Sala Punt 7 · `proleg_punt7` — cinemàtica

```
EN ENTRAR
    • * — SEMPRE
        NARRADOR: Atlàntic Nord. Punt 7. Febrer. Tres de la matinada.
        NARRADOR: A popa de l'Arenga, en Bastida baixa una zòdiac amb la grua. A dins, la Juana.
        JUANA FERRER: Deu minuts, Ernest.
        ERNEST BASTIDA: Deu. I tornes.
        NARRADOR: La Juana treu un pot de fang gris de l'aigua i el mira a contrallum. No s'hi mou res.
        JUANA FERRER: Ni un ou.
        NARRADOR: Hi escriu amb retolador.
        JUANA FERRER: Mostra 7.
        NARRADOR: Mira la plataforma. Té el logotip tapat amb cinta americana.
        NARRADOR: Als llums de la plataforma, una silueta la mira amb uns prismàtics.
        JUANA FERRER: Bona nit a tu també.
        NARRADOR: A bord, algú més la mira. Quan la Juana aixeca el pot, en algun lloc del vaixell s'encén una pantalla petita. Una mà hi escriu.
        TÍTOL: Ni un ou
        TÍTOL: Acte 1 · Aigua a la sentina
        ⇒ → camarot_iri

```

## Sala Rebost · `rebost` (iri, vet)

```
DECORAT rascades — es veu si escena ≥ 4
DECORAT registre_obert — es veu si registre_obert

PORTA «sala de màquines»
    • walkTo/use/open — SEMPRE
        ⇒ → sala_maquines
    • look — SEMPRE
        JUGADORA: La porta de la sala de màquines.

MUNTA «muntacàrregues»
    • look — SEMPRE
        JUGADORA: El muntacàrregues de la cuina. De quan l'Arenga portava trenta persones.
        JUGADORA: Tres parades: la cuina, el rebost i el pont.
    • use + llibreta — si escena = 5 i NO nota_enviada
        JUGADORA: Arrenco un full de la llibreta i hi escric.
        JUGADORA: «Cada cosa que diem pel walkie, algú hi arriba primer. Ens escolten. Ni una paraula.»
        ⇒ +nota_enviada, acció munta.nota
    • use + llibreta — si escena = 5 i pla_fet i NO mentida_triada
        ⇒ diàleg paperets
    • use + llibreta — si escena = 5 i NO pla_fet
        JUGADORA: Ara toca esperar la resposta. Sense fer soroll.
    • use + llibreta — si escena = 5 i NO mentida_dita
        JUGADORA: No cal escriure res més. Ara, la mentida, pel walkie.
    • use + llibreta — si escena = 5
        JUGADORA: Ja està tot dit.
    • use + qualsevol objecte — SEMPRE
        ⇒ acció munta.enviar
    • use — si munta_rebost = ""
        JUGADORA: Sense res a dins, no l'envio. Fer-lo anar buit no porta res a ningú.

SAFATA «safata del muntacàrregues» — hi és si munta_rebost ≠ ""
    • look — SEMPRE
        ⇒ acció munta.mirar
    • pickUp/open/use — si munta_rebost = "nota_vet"
        JUGADORA: La resposta de la Vet, a sota de la meva.
        NARRADOR: «Doncs diguem-los alguna cosa.»
        JUGADORA: Ara, la mentida. L'escric i l'envio amunt: que la triï ella.
        ⇒ munta_rebost := "", +pla_fet
    • pickUp/open/use — SEMPRE
        ⇒ acció munta.recollir

PRESTATGES «prestatges»
    • look — si juga iri
        JUGADORA: Llaunes de sardines de Portugal. N'hi falten unes quantes. Cada nit, unes quantes.
    • pickUp — si juga iri
        JUGADORA: Les sardines no són meves. I sé de qui són.

REGISTRE «registre del dipòsit 2»
    • walkTo/use/open — si registre_obert
        ⇒ → diposit2
    • use + cisalla — si NO registre_obert
        JUGADORA: És un pany, no un cadenat. Aquí la cisalla no hi mossega.
    • look — si escena ≥ 7
        JUGADORA: El registre del dipòsit d'aigua 2. Hi ha rascades fresques al pany i la pintura saltada.
        JUGADORA: Algú l'ha provat de forçar amb una clau de tubs. I no ha pogut.
        JUGADORA: Ens han sentit dir «on ningú no beu». Ho han entès. I no tenien la clau.
        ⇒ +prova_pany
    • look — SEMPRE
        JUGADORA: El registre del dipòsit d'aigua 2. «AIGUA NO POTABLE». Fa anys que està fora de servei.
    • use + clau_tomas — SEMPRE
        [SO: clau_vella] JUGADORA: Gira amb un gemec.
        JUGADORA: Era la del dipòsit 2. Era del cuiner d'abans.
        ⇒ perd clau_tomas, +registre_obert, → diposit2
    • use + clau_tubs — si NO registre_obert i NO frontissa1
        JUGADORA: Primer la frontissa de dalt...
        JUGADORA: Cargols nous. La Juana no menteix.
        ⇒ +frontissa1
    • use + clau_tubs — si NO registre_obert
        [SO: frontissa] JUGADORA: I la de baix.
        JUGADORA: Fora. El registre s'obre per l'altra banda, com una porta mal posada.
        ⇒ +registre_obert
    • open/use/pull — si escena < 7 i tomas_clau i NO registre_obert
        JUGADORA: Tancat amb clau. Una clau antiga... Com la que guarda en Tomàs, que no sap què obre?
    • open/use/pull — si escena < 7 i NO registre_obert
        JUGADORA: Tancat amb clau. Una clau antiga, que fa anys que no es veu.
    • open/use/pull — si NO registre_obert i frontissa1
        JUGADORA: Tancat amb clau. I encara aguanta per la frontissa de baix.
    • open/use/pull — si NO registre_obert
        JUGADORA: Tancat amb clau. O amb la clau, o sense les frontisses.

```

## Sala Sala de bombes · `sala_bombes` (iri, vet)

```
EN ENTRAR
    • * (una vegada) — si escena = 4
        NARRADOR: La Juana no hi és.

ESCOTILLA «escotilla»
    • walkTo/use/open — SEMPRE
        ⇒ → passadis_baix
    • look — SEMPRE
        JUGADORA: L'escotilla, cap al passadís.

LLIBRE «llibre» — hi és si escena ≥ 4
    • look/pickUp — si escena = 4
        JUGADORA: El llibre de la Juana, a terra. I la llanterna, encesa.
        IRI: Vet. El llibre de la Juana és a terra de la sala de bombes. I la llanterna, encesa.
        IRI: La Juana no descansa.
        VET: Ningú no deixa un llibre a terra. I menys la Juana.
        TÍTOL: Deu del vespre.
        ⇒ escena := 5, esdeveniment situar, esdeveniment anar
    • look — SEMPRE
        JUGADORA: El llibre de la Juana. «Ous i larves de l'Atlàntic». Era a la meitat.

LLANTERNA «llanterna» — hi és si escena = 4 o escena = 5
    • look — SEMPRE
        JUGADORA: La llanterna de la Juana. Encesa. Fa estona que està encesa.
    • pickUp — SEMPRE
        JUGADORA: La deixo on és. Si torna, la trobarà.

BASTIDA «—» — hi és si escena = 6 i bastida_baixa
    • look — SEMPRE
        JUGADORA: En Bastida, buscant soroll on no n'hi ha.
    • talkTo — si juga iri
        ERNEST BASTIDA: Aquí no hi ha res, noia. Ni ningú. Ves-te'n a dormir.

BOMBES «bombes»
    • look — si juga iri
        JUGADORA: Les bombes de llast i de contraincendis. Netes, pintades, callades. No hi baixa mai ningú.

```

## Sala Sala de màquines · `sala_maquines` (iri, vet)

```
EN ENTRAR
    • * (una vegada) — si escena = 1 i juga iri
        NARRADOR: Al terra hi ha dos dits d'aigua. En Diu, assegut damunt del col·lector calent, s'ho mira com si no fos cosa seva.
        JUGADORA: La sentina de popa està plena. I l'alarma no ha sonat.
    • * (una vegada) — si escena = 9 i juga vet i NO aliada_capitana
        NARRADOR: A les fosques, amb el llum d'emergència. En Bastida és al peu de l'escala, amb el registre de la sentina obert als peus.
        NARRADOR: Té el relé a la mà, damunt de l'aigua bruta.
        ERNEST BASTIDA: Si s'acosta ningú, va a la sentina. I l'Iri sap que a la sentina no s'hi fica la mà.
        NARRADOR: El missatger de satèl·lit d'en Bastida s'encén: «Recordi el nostre acord.»
        ⇒ dubte := 5
    • * (una vegada) — si escena = 9 i juga vet i aliada_capitana
        NARRADOR: A les fosques, amb el llum d'emergència. En Bastida és al peu de l'escala, amb el registre de la sentina obert als peus.
        NARRADOR: Té el relé a la mà, damunt de l'aigua bruta.
        ERNEST BASTIDA: Si s'acosta ningú, va a la sentina. I l'Iri sap que a la sentina no s'hi fica la mà.
        NARRADOR: El missatger d'en Bastida fa estona que no s'encén. La Lind ja no escriu.
        ⇒ dubte := 4

DECORAT aigua — es veu si escena = 1 i NO bomba_engegada
DECORAT valvula_tancada — es veu si valvula_tancada
DECORAT brida — es veu si NO brida_tallada
DECORAT sentina_oberta — es veu si escena = 9 i NO rele_posat
DECORAT fosc — es veu si escena = 9 i NO rele_posat
DECORAT generador_marxa — es veu si escena ≠ 9 o rele_posat
DECORAT bomba_marxa — es veu si escena = 1 i bomba_engegada

PORTA_PASSADIS «passadís»
    • walkTo/use/open — si escena = 1 i valvula_vista
        JUGADORA: No me'n puc anar amb la sentina així.
    • walkTo/use/open — si juga vet i escena = 9
        JUGADORA: No. No me'n vaig sense el relé. ⟨si NO rele_posat⟩
        JUGADORA: Em quedo amb l'Ernest. ⟨si rele_posat⟩
    • walkTo/use/open — SEMPRE
        ⇒ → passadis_baix
    • look — SEMPRE
        JUGADORA: La porta del passadís.

PORTA_TALLER «taller»
    • walkTo/use/open — si juga vet i escena = 9
        JUGADORA: No. No me'n vaig sense el relé. ⟨si NO rele_posat⟩
        JUGADORA: Em quedo amb l'Ernest. ⟨si rele_posat⟩
    • walkTo/use/open — SEMPRE
        ⇒ → taller
    • look — SEMPRE
        JUGADORA: El taller.

PORTA_REBOST «rebost»
    • walkTo/use/open — si juga vet i escena = 9
        JUGADORA: No. No me'n vaig sense el relé. ⟨si NO rele_posat⟩
        JUGADORA: Em quedo amb l'Ernest. ⟨si rele_posat⟩
    • walkTo/use/open — SEMPRE
        ⇒ → rebost
    • look — SEMPRE
        JUGADORA: El rebost. Porta amb porta amb la sala de màquines: el cuiner d'abans hi baixava a fumar.

VALVULA «vàlvula de presa de mar»
    • look — si valvula_tancada
        JUGADORA: Tancada. El travesser de la llitera fa de volant.
        JUGADORA: Quedarà millor que l'original.
    • look — si juga iri i NO valvula_vista
        JUGADORA: La vàlvula de presa de mar de popa. Oberta.
        JUGADORA: Li han tret el volant.
        JUGADORA: Algú ha obert això. I no ha estat el gat.
        JUGADORA: Bé, podria haver estat el gat. Però el gat no té polzes.
        ⇒ +valvula_vista
    • look — si juga iri
        JUGADORA: Oberta, i sense volant. Necessito una palanca: una barra de metall d'un pam i mig, com a mínim.
    • use + travesser — si NO valvula_tancada
        [SO: valvula] JUGADORA: Hi encaixa.
        JUGADORA: Gira dur... Ja està. Tancada.
        ⇒ perd travesser, +valvula_tancada, +valvula_vista
    • use + cisalla — SEMPRE
        JUGADORA: Amb la cisalla? No. Necessito una palanca.
    • close/use/push/pull — si NO valvula_tancada
        JUGADORA: Sense volant no la puc girar. Necessito una palanca: una barra de metall d'un pam i mig, com a mínim.
        ⇒ +valvula_vista

QUADRE «quadre de la bomba»
    • look — si NO brida_tallada i juga iri
        JUGADORA: El quadre de la bomba de sentina. L'interruptor està lligat amb una brida.
        JUGADORA: Amb un nus Bastida.
        JUGADORA: Aquest nus el sap fer tothom a bord. Ens el va ensenyar ell a tots.
        ⇒ +brida_vista
    • look — si juga iri
        JUGADORA: El quadre de la bomba de sentina. Sense brida, ja.
    • use — si juga vet i escena > 1
        JUGADORA: No toco res que faci llum, aquí baix.
    • look — si juga vet
        JUGADORA: Un quadre elèctric. Llumetes. Em recorda la UCI.
    • use + cisalla — si NO brida_tallada
        [SO: clic] JUGADORA: Fora.
        JUGADORA: Té una volta de més.
        JUGADORA: Algú que l'ha après malament.
        JUGADORA: Després tornaré la cisalla al taller. Les eines, al seu lloc.
        ⇒ +brida_tallada, +brida_vista, +prova_nus_brida
    • use — si NO brida_tallada
        JUGADORA: No arrenca: l'interruptor està lligat amb una brida. Cal tallar-la.
    • use — si NO valvula_vista
        JUGADORA: Si buido ara, l'aigua torna a entrar. Primer he de veure per on.
    • use — si NO valvula_tancada
        JUGADORA: Si buido ara, la vàlvula la torna a omplir. Primer, tancar-la.
    • use — si NO vies_separador
        JUGADORA: La bomba ha d'escopir l'aigua a algun lloc. Primer, la vàlvula de tres vies.
    • use — si escena = 1 i NO bomba_engegada
        [SO: bomba] NARRADOR: La bomba arrenca. L'aigua comença a baixar, a poc a poc, cap al separador.
        NARRADOR: Algú baixa per l'escala, amb la pipa apagada a la boca i el jersei damunt del pijama.
        ⇒ +bomba_engegada, diàleg bastida1
    • use — si juga iri
        JUGADORA: La bomba treballa. A poc a poc, com ha de ser.

VIES «vàlvula de tres vies»
    • look — si NO vies_separador
        JUGADORA: La vàlvula de tres vies de la bomba. Dues posicions: BORDA o SEPARADOR.
    • look — SEMPRE
        JUGADORA: La vàlvula de tres vies, cap al SEPARADOR.
    • use — si NO vies_separador
        ⇒ diàleg vies
    • use — SEMPRE
        JUGADORA: Al separador. I al separador es queda.

SEPARADOR «separador d'aigües oleoses»
    • look — si juga iri
        JUGADORA: El separador d'aigües oleoses. Treu el gasoil de l'aigua abans de tornar-la al mar.
        JUGADORA: Va a poc a poc. Com tot el que val la pena.
    • look — si juga vet
        JUGADORA: Una màquina que fa glu-glu. Sembla contenta.

SENSOR «sensor de sentina»
    • look — si juga iri i escena = 1 i NO valvula_tancada
        JUGADORA: El sensor de sentina. Desconnectat.
        JUGADORA: Les alarmes no callen soles.
    • look — si juga iri i escena = 1
        JUGADORA: El sensor de sentina. Ja el tornaré a connectar quan la sentina estigui buida.
    • look — si juga iri
        JUGADORA: El sensor de sentina. Connectat i callat, com ha de ser.
    • look — si juga vet
        JUGADORA: Un sensor. Si xiula, mal assumpte. Això ho entenc fins i tot jo.
    • use — si escena = 1
        JUGADORA: Si el connecto ara, xisclarà fins a Galway. Quan la sentina estigui buida.

MOTOR «motor principal»
    • look — si juga iri i escena = 1
        JUGADORA: El motor principal. Dorm. Com hauria de fer tothom a aquestes hores.
    • look — si juga iri i escena ≥ 4 i escena ≤ 8
        JUGADORA: El motor principal. «Molt expressiu», diu la doctora. Tres campanyes escoltant-lo, i no ho havia sabut dir.
    • look — si juga iri
        JUGADORA: El motor principal. Ronca. Al mar no es veu, però se sent.
    • look — si juga vet
        JUGADORA: Un motor. Gran. Ronca com el meu pare.
    • use — si juga iri
        JUGADORA: No t'espatlles. Et queixes. Ja ho sé.

BOCA «boca del tub de veu»
    • look — si NO tub_de_veu
        JUGADORA: La boca del tub de veu. De llautó, de 1984. Ningú no hi parla des que van posar els walkies.
    • look — SEMPRE
        JUGADORA: La boca del tub de veu: el pont, la cuina i la infermeria.
    • talkTo/use — si tub_de_veu
        ⇒ −cara_a_cara, diàleg tub
    • talkTo/use — si NO tub_de_veu
        JUGADORA: Hola? ...Res. Des que hi ha walkies, aquí dins no hi parla ningú.

DIU «—» — hi és si escena = 1

BASTIDA «—» — hi és si escena = 9 o (escena = 1 i bomba_engegada)
    • look — si juga vet i escena = 9 i NO rele_posat
        JUGADORA: En Bastida. Dret al peu de l'escala, amb el relé a la mà, damunt del registre obert de la sentina.
    • look — si juga iri
        JUGADORA: L'Ernest. El contramestre. El que em va treure de l'aigua.
    • look — si juga vet
        JUGADORA: En Bastida. Ulls de mar, mans de mar.
    • talkTo — si escena = 9
        ⇒ diàleg bastida

GENERADOR «generador»
    • look — si juga vet i escena = 9 i NO rele_posat
        JUGADORA: El generador. Parat. Sense el relé de sincronització, no arrenca.
    • look — si NO rele_posat
        JUGADORA: El generador. Gira, amb la remor de sempre.
    • look — si juga vet
        JUGADORA: El generador. Torna a girar.
    • use — si juga vet i escena = 9 i NO rele_posat
        JUGADORA: Sense el relé no fa res. I el relé el té ell.

SENTINA «registre de la sentina»
    • look — si juga vet i escena = 9 i NO rele_posat
        JUGADORA: El registre de la sentina, obert. Aigua bruta i gasoil. Si el relé hi cau, ja no el traurem.
    • look — SEMPRE
        JUGADORA: El registre de la sentina. A sota, aigua bruta i gasoil, com a tots els vaixells.
    • pickUp/use — si juga vet i escena = 9
        JUGADORA: A la sentina no s'hi fica la mà. Ni per un relé.

```

## Sala Sala de ràdio · `sala_radio` (iri, vet)

```
DECORAT dia — es veu si escena = 2 o escena = 3
DECORAT dia_mar — es veu si escena = 2 o escena = 3
DECORAT panell_obert — es veu si panell_obert
DECORAT panell_reparat — es veu si panell_obert i empalmat ≥ 2

PORTA «pont»
    • walkTo/use/open — SEMPRE
        ⇒ → pont
    • look — SEMPRE
        JUGADORA: La porta del pont.

RADIO «ràdio de llarg abast»
    • look — si NO radio_feta i empalmat ≥ 2
        JUGADORA: La ràdio de llarg abast. Cable nou, connector crimpat. A veure si parla.
    • look — si NO radio_feta
        JUGADORA: La ràdio de llarg abast. Morta.
    • look — SEMPRE
        JUGADORA: La ràdio de llarg abast. Funciona. I Valmark escolta tota la banda.
    • use — si (escena = 3 i sync_radio) i empalmat ≥ 2 i panell_obert i paciencia ≥ 5 i coberta = 0
        JUGADORA: Provem-ho.
        NARRADOR: Abans que la ràdio s'escalfi, a sota, la porta de la infermeria s'obre.
        ⇒ +radio_interrompuda
    • use — si (escena = 3 i sync_radio) i empalmat ≥ 2 i panell_obert
        [SO: estatica_neta] JUGADORA: Provem-ho.
        NARRADOR: Estàtica. Estàtica neta: viva.
        JUGADORA: Arenga a Mar Obert. Arenga a Mar Obert.
        ⇒ +radio_feta, diàleg radio
    • use — si NO radio_feta
        JUGADORA: Morta. Ni estàtica.
    • use — SEMPRE
        JUGADORA: Ara no. Aquesta ràdio ara la sent tot Valmark.

PANELL «panell»
    • look — si panell_obert i NO prova_sang
        JUGADORA: Una gota de sang a la vora. Seca.
        JUGADORA: Aquesta xapa talla com un ganivet: qui l'ha obert a les fosques s'ha fet mal.
        ⇒ +prova_sang
    • look — si empalmat ≥ 2
        JUGADORA: El panell, obert. El cable de malla d'acer, nou, crimpat.
    • look — si panell_obert
        JUGADORA: El panell, obert.
    • look — si juga iri
        JUGADORA: El panell de la ràdio. Algú l'ha obert i tancat fa poc: els cargols tenen la pintura saltada.
    • open/use/pull — si (escena = 3 i sync_radio) i NO panell_obert i NO soroll_fet
        [SO: panell] JUGADORA: Els cargols, fora. La xapa grinyola.
        ERNEST BASTIDA: Sents això?
        VET: És el motor. Sempre fa això.
        ERNEST BASTIDA: El motor no fa aquest soroll.
        VET: Avui sí. És un motor molt expressiu.
        ERNEST BASTIDA: Ets graciosa, doctora.
        ⇒ +panell_obert, +soroll_fet
    • open/use/pull — si (escena = 3 i sync_radio) i NO panell_obert i coberta = 0
        [SO: panell] JUGADORA: La xapa grinyola. Massa.
        NARRADOR: A sota, en Bastida aixeca el cap.
        ⇒ +panell_obert, paciencia += 1
    • open/use/pull — si (escena = 3 i sync_radio) i NO panell_obert
        [SO: panell] JUGADORA: La xapa grinyola. A sota, la Vet parla més fort que ella.
        ⇒ +panell_obert
    • open/use/pull — si escena = 3 i NO panell_obert
        JUGADORA: En Bastida diu que l'arreglarà ell. Vull veure-ho abans, però no ara: amb ell a la vora, no.
    • use + cable_nou — si (escena = 3 i sync_radio) i panell_obert i tram_tret i empalmat = 0
        JUGADORA: Pelo el cable. Malla d'acer: per això ha mellat la cisalla. Ara, el connector.
        ⇒ empalmat := 1
    • use + cable_nou — si (escena = 3 i sync_radio) i panell_obert i tram_tret i empalmat = 1
        JUGADORA: Connector crimpat. Fet.
        ⇒ empalmat := 2, perd cable_nou
    • use + cable_nou — si panell_obert
        JUGADORA: Primer he de treure el tram tallat.
    • use + cable_nou — SEMPRE
        JUGADORA: Primer, obrir el panell.
    • close — si escena = 3 i radio_feta i rut_parlat
        [SO: panell] JUGADORA: Tancat. Com si no hagués passat res.
        NARRADOR: En Bastida mira el panell. Mira l'Iri.
        ERNEST BASTIDA: Ja l'has arreglada?
        NARRADOR: Una pausa.
        ERNEST BASTIDA: Ets massa bona, noia.
        IRI: M'ho vas ensenyar tu.
        ERNEST BASTIDA: Sí.
        NARRADOR: Se'n va.
        ERNEST BASTIDA: Massa bona.
        JUGADORA: La vàlvula, la ràdio... Ho ha fet algú de bord. Algú que té una cisalla mellada.
        VET: Doncs soles no en sortirem. Ens cal gent de bord al nostre costat: com més en siguin, més lluny arribarà la història.
        JUGADORA: Gent de bord. Que no tingui una cisalla.
        TÍTOL: Falten 10 hores.
        TÍTOL: Acte 2 · Algú escolta
        TÍTOL: Nou del vespre.
        ⇒ −panell_obert, escena := 4, hores := 10, +bastida_passa, perd tram, esdeveniment situar, esdeveniment anar
    • close — si panell_obert
        JUGADORA: Encara no.

CABLE «cable tallat» — hi és si panell_obert i NO tram_tret
    • look — SEMPRE
        JUGADORA: El cable de l'antena. Tallat. Hi ha un tram que s'ha de treure.
    • pickUp/pull/use — si escena = 3 i sync_radio
        JUGADORA: Fora el tram tallat.
        JUGADORA: Tall net. I una osca al mig, sempre al mateix lloc.
        JUGADORA: Això ho ha fet una cisalla amb una dent mellada.
        JUGADORA: Aquest cable porta malla d'acer. Mella qualsevol cisalla.
        JUGADORA: ...Això no ho ha fet en Diu.
        ⇒ +tram_tret, rep tram, +prova_osca

BASTIDA «—» — hi és si escena = 3 i rut_parlat
    • look — SEMPRE
        JUGADORA: En Bastida, a la porta. Mira el panell obert.
    • talkTo — SEMPRE
        ERNEST BASTIDA: Tu acaba, noia. Tanca-ho, que no hi entri humitat.

```

## Sala Taller · `taller` (iri, vet)

```
PORTA «sala de màquines»
    • walkTo/use/open — SEMPRE
        ⇒ → sala_maquines
    • look — SEMPRE
        JUGADORA: La porta de la sala de màquines.

TAULER «tauler d'eines»
    • look — si juga iri i NO silueta_vista
        JUGADORA: El tauler d'eines. Hi ha una silueta buida: la clau de vàlvules no hi és.
        JUGADORA: Algú ha endreçat el taller a les tres de la matinada. Ningú no endreça res a les tres de la matinada.
        ⇒ +silueta_vista
    • look — si juga iri
        JUGADORA: El tauler, amb la silueta buida de la clau de vàlvules.
    • use + cisalla — SEMPRE
        JUGADORA: La deixo al seu lloc.
        ⇒ perd cisalla, −cisalla_fora
    • use + clau_tubs — SEMPRE
        JUGADORA: La deixo al seu lloc.
        ⇒ perd clau_tubs, −clau_tubs_fora

CISALLA «cisalla» — hi és si NO cisalla_fora
    • look — si escena = 1
        JUGADORA: La cisalla del taller. Talla com el primer dia.
    • look — si juga iri i prova_osca i NO cisalla_mellada
        JUGADORA: La cisalla del taller. Té una dent mellada.
        JUGADORA: Aquesta matinada, quan vaig tallar la brida, no la tenia.
        ⇒ +cisalla_mellada, +prova_cisalla
    • look — si cisalla_mellada
        JUGADORA: La cisalla del taller. Amb la dent mellada.
    • look — SEMPRE
        JUGADORA: La cisalla del taller.
    • pickUp — si escena = 1
        JUGADORA: La cisalla. Per a una brida, sobra.
        ⇒ rep cisalla, +cisalla_fora
    • pickUp — SEMPRE
        JUGADORA: La cisalla.
        ⇒ rep cisalla, +cisalla_fora

CLAU_TUBS «clau de tubs» — hi és si NO clau_tubs_fora
    • look — SEMPRE
        JUGADORA: La clau de tubs. Grossa i pesant.
    • pickUp — si escena = 7
        JUGADORA: La clau de tubs.
        ⇒ rep clau_tubs, +clau_tubs_fora
    • pickUp — si escena = 1 i NO valvula_tancada
        JUGADORA: La clau de tubs mossega i rellisca: a una tija sense volant no s'hi agafa.
        JUGADORA: Necessito una barra que hi encaixi. D'un pam i mig, com a mínim.
    • pickUp — SEMPRE
        JUGADORA: La clau de tubs, al seu lloc. Ara no em fa falta.

BANC «banc de treball»
    • look — si juga iri
        JUGADORA: El banc de treball. Hi ha un torn, un cargol de banc i un entrepà a mig menjar de fa tres dies.

```

## Objecte walkie · `walkie`

```
• look — si nadia_escolta
    JUGADORA: El walkie. Canal 9. L'escolta la Nadia, i per tant la Lind. Ara només serveix per dir mentides.
• look — si portatil_robat
    JUGADORA: El walkie. Canal 9. Algú l'escolta: tot el que hi diem, algú hi arriba primer.
• talkTo — SEMPRE
    ⇒ diàleg walkie
• use — SEMPRE
    ⇒ diàleg walkie
```

## Objecte quadern · `quadern`

```
• look — SEMPRE
    ⇒ diàleg quadern
```

## Objecte llibreta de màquines · `llibreta`

```
(sense interaccions: només el text per defecte)
```

## Objecte maceta · `maceta`

```
(sense interaccions: només el text per defecte)
```

## Objecte cisalla · `cisalla`

```
• look — si juga iri i cisalla_mellada
    JUGADORA: La cisalla del taller. Té una dent mellada.
• look — si juga iri i escena = 1
    JUGADORA: La cisalla del taller. Talla com el primer dia.
• look — si juga iri
    JUGADORA: La cisalla del taller.
```

## Objecte travesser · `travesser`

```
(sense interaccions: només el text per defecte)
```

## Objecte tram de cable tallat · `tram`

```
• look — SEMPRE
    JUGADORA: Tall net. I una osca al mig, sempre al mateix lloc.
    JUGADORA: Una cisalla amb una dent mellada.
    ⇒ +prova_osca
```

## Objecte cable i connector · `cable_nou`

```
(sense interaccions: només el text per defecte)
```

## Objecte USB · `usb`

```
(sense interaccions: només el text per defecte)
```

## Objecte paper de l'Iri · `nota_iri`

```
• look — SEMPRE
    JUGADORA: «Cada cosa que diem pel walkie, algú hi arriba primer. Ens escolten. Ni una paraula.»
```

## Objecte paper de la Vet · `nota_vet`

```
• look — SEMPRE
    JUGADORA: «Doncs diguem-los alguna cosa.»
```

## Objecte clau antiga · `clau_tomas`

```
(sense interaccions: només el text per defecte)
```

## Objecte clau de tubs · `clau_tubs`

```
(sense interaccions: només el text per defecte)
```

## Objecte Mostra 7 · `mostra7`

```
• look — SEMPRE
    JUGADORA: Un pot de fang gris, dins d'una bossa segellada. «Mostra 7 — Punt 7 — SK-4».
```

## Objecte pàgina del registre · `registre`

```
• look — SEMPRE
    JUGADORA: El registre de fundacions de Valmark. Fundació Blau Net. Patró únic: Skarn.
```

## Objecte plànol · `mapa`

```
• use/open — SEMPRE
    ⇒ esdeveniment mapa
```

## Diàleg `bastida` amb Ernest Bastida

```
COMENÇA A: esc2 (si escena = 2) · esc3 (si escena = 3 i sync_radio) · nus_mes (si escena = 6 i nus_lico i juga vet) · esc6 (si escena = 6) · fet (si escena = 9 i rele_posat) · torna9 (si escena = 9 i ha vist bastida.esc9) · esc9 (si escena = 9) · res

[esc2]
    ERNEST BASTIDA: Doctora.
    ↪ esc2_menu

[esc2_menu]
    ▸ Fumes molt? ⟨una vegada⟩ → pipa
    ▸ I la revisió, Ernest? → revisio2
    ▸ Aquella plataforma... ⟨una vegada, si plataforma_vista⟩ → plataforma
    ▸ Bon dia per pescar? ⟨si NO bastida_arengades⟩ → mar
    ▸ Res. Bon vent. → (es queda) · FI

[revisio2]
    ERNEST BASTIDA: Ara no puc, doctora. Més tard.
    ⇒ +bastida_ara_no
    ↪ esc2_menu

[mar]
    ERNEST BASTIDA: De jove, a l'hivern, el mar bullia d'arengades. Les treies amb la galleda.
    VET: I ara?
    ERNEST BASTIDA: Ara no en queda ni una.
    NARRADOR: Xucla la pipa.
    ERNEST BASTIDA: El mar ja està mort, doctora. Només que encara no ho sap.
    ⇒ +bastida_arengades
    ↪ esc2_menu

[pipa]
    ERNEST BASTIDA: Només a coberta. Les normes són les normes.
    ↪ esc2_menu

[plataforma]
    ERNEST BASTIDA: No surt als mapes, doctora. El que no surt als mapes, no hi és.
    ↪ esc2_menu

[esc3]
    ERNEST BASTIDA: Doncs què, doctora? Que tinc pressa.
    ↪ esc3_menu

[esc3_menu]
    ▸ Diuen que ets una llegenda. Explica'm això del temporal. Per la història clínica. ⟨si NO eina_temporal⟩ → temporal
    ▸ La tensió. Arremanga't. ⟨si NO eina_tensio⟩ → tensio
    ▸ Ensenya'm les mans. ⟨si NO eina_mans⟩ → mans
    ▸ (Deixar-lo una estona) → (es queda) · FI

[temporal]
    ERNEST BASTIDA: Quin? N'hi ha hagut uns quants. El 2003: ones de deu metres i un pesquer gallec bolcat.
    ERNEST BASTIDA: En vaig treure tres de l'aigua. Al tercer, ja no em sentia les mans.
    ERNEST BASTIDA: I fa dues campanyes, l'Iri. Va caure per la borda amb mar grossa. Quan la vaig treure, encara renegava.
    ERNEST BASTIDA: I encara hi tornaria.
    NARRADOR: Li encanta explicar-ho.
    ⇒ +eina_temporal, coberta_nova := 3
    ↪ esc3_menu

[tensio]
    NARRADOR: El maniguet s'infla, a poc a poc. Molt a poc a poc.
    ERNEST BASTIDA: Això no s'acaba mai?
    VET: És un aparell vell. Com tot, aquí.
    ⇒ +eina_tensio, coberta_nova := 2
    ↪ esc3_menu

[mans]
    NARRADOR: Un tall fresc al palmell.
    ERNEST BASTIDA: Un cap. En tallo deu cada dia.
    ⇒ +eina_mans, +prova_tall_ma
    ↪ esc3_menu

[esc6]
    ERNEST BASTIDA: A proa ja hi he mirat jo. Deu ser per aquí, a popa: li agrada el vent.
    ▸ Ensenya'm a fer el nus Bastida. Per si mai he de lligar un pacient. ⟨si juga vet i NO nus_lico i NO cadenat_tallat⟩ → nus
    ▸ D'acord. Bona nit. → (es queda) · FI

[nus]
    ERNEST BASTIDA: Mira. La volta per aquí, la passes per sota...
    NARRADOR: En Bastida l'hi ensenya a poc a poc, d'esquena a proa.
    ERNEST BASTIDA: I aquesta, no.
    VET: Quina?
    ERNEST BASTIDA: La que no t'ensenyo.
    VET: Una altra vegada. No ho he entès.
    ERNEST BASTIDA: Ets lenta, doctora. Mira...
    ⇒ +nus_lico

[nus_mes]
    ERNEST BASTIDA: Una altra vegada? Mira: per aquí, i per sota...

[esc9]
    ERNEST BASTIDA: A tu no et tinc por, doctora. Ets l'única que no sap on és la proa.
    ↪ dubte

[dubte]
    ⇒ −rele_ara
    ▸ Si surt, ets un testimoni. Si no surt, ets l'únic culpable. T'ho acaba de dir ella. ⟨si NO rele_posat i NO dubte_veritat⟩ → veritat
    ▸ Saps qui ha pujat al pal, amb aquest vent? ⟨si NO rele_posat i iri_al_pal i NO dubte_iri⟩ → iri
    ▸ A la revisió em vas dir que el cafè de la infermeria era el pitjor del vaixell. Que algun dia me'n faries un de bo. ⟨si NO rele_posat i bastida_cafe i NO dubte_cafe⟩ → cafe
    ▸ Em vas dir que de jove el mar en bullia. Al Punt 7 encara n'hi havia, Ernest. Fins que hi van tirar el fang. ⟨si NO rele_posat i bastida_arengades i NO dubte_arengades⟩ → arengades
    ▸ Ja ho hem enviat. Això que fas no serveix de res. ⟨si NO rele_posat i NO dubte_mentida⟩ → mentida
    ▸ Quant pagaries tu, ara, per tornar a ser l'Ernest Bastida del temporal? ⟨si NO rele_posat i NO dubte_diners⟩ → diners
    ▸ (Deixar-lo pensar) ⟨si NO rele_posat⟩ → (es queda) · FI

[veritat]
    NARRADOR: En Bastida mira el missatger. Després, el relé.
    ERNEST BASTIDA: ...Ho ha dit, sí.
    ⇒ +dubte_veritat, dubte −= 2, +bastida_veritat
    ↪ rele

[iri]
    ERNEST BASTIDA: ...Encara no en sap baixar bé. Li vaig ensenyar jo.
    ⇒ +dubte_iri, dubte −= 2
    ↪ rele

[cafe]
    ERNEST BASTIDA: Algun dia.
    ⇒ +dubte_cafe, dubte −= 1
    ↪ rele

[arengades]
    ERNEST BASTIDA: ...Encara n'hi havia.
    ⇒ +dubte_arengades, dubte −= 1
    ↪ rele

[mentida]
    ERNEST BASTIDA: Doncs per què has baixat?
    VET: ...Bona pregunta.
    ⇒ +dubte_mentida, dubte += 1
    ↪ rele

[diners]
    NARRADOR: Un silenci llarg.
    ⇒ +dubte_diners, dubte −= 2
    ↪ rele

[rele]
    [SO: generador_engega] NARRADOR: En Bastida s'aixeca. Va fins al generador i hi posa el relé. ⟨si dubte ≤ 0 i NO rele_posat⟩
      ⇒ +rele_posat, +rele_ara
    NARRADOR: Els llums tornen, un darrere l'altre. ⟨si rele_ara⟩
    ERNEST BASTIDA: Si cal declarar, declararé. ⟨si rele_ara i bastida_veritat⟩
      ⇒ +aliat_bastida, aliats += 1
    NARRADOR: En Bastida està amb vosaltres. Aliats: {aliats} de 4. ⟨si rele_ara i bastida_veritat⟩
    ↪ dubte

[torna9]
    ERNEST BASTIDA: Doctora.
    ↪ dubte

[fet]
    ERNEST BASTIDA: Ja està, doctora. Ara, envia-ho. Abans que me'n penedeixi.

[res]
    ERNEST BASTIDA: Ara no, doctora. ⟨si juga vet⟩

```

## Diàleg `bastida1` amb Ernest Bastida

```
COMENÇA A: arriba

[arriba]
    ERNEST BASTIDA: He sentit la bomba.
    NARRADOR: Mira la vàlvula. Mira l'Iri.
    ERNEST BASTIDA: Ho has fet bé, noia. Molt bé.
    NARRADOR: Mira el separador, que treballa a poc a poc.
    ERNEST BASTIDA: Amb tanta aigua, l'hauries pogut tirar per la borda. Ningú no ho hauria vist.
    IRI: El mar sí.
    NARRADOR: Un moment massa llarg.
    ERNEST BASTIDA: ...El mar sí.
    IRI: Algú l'ha oberta, Ernest. I s'ha endut el volant.
    ERNEST BASTIDA: Aquesta vàlvula té quaranta anys. Els volants cauen.
    ERNEST BASTIDA: Demà en parlem amb la Capitana. Ves a dormir.
    ERNEST BASTIDA: I la cisalla, al taller. Que no és teva.
    NARRADOR: En Diu, assegut damunt d'un tub calent, mira en Bastida molta estona.
    NARRADOR: Quan la sentina està buida, l'Iri torna a connectar el sensor. Calla, com ha de fer.
    TÍTOL: Vuit del matí.
    ⇒ perd cisalla (iri), −cisalla_fora, escena := 2, esdeveniment situar, esdeveniment situar, esdeveniment protagonista

```

## Diàleg `capitana` amb Capitana Roig

```
COMENÇA A: revisio (si escena = 2 i pacient = "capitana") · cabina2 (si escena = 2 i NO revisio_capitana) · pont3 (si escena = 3) · esc6 (si escena = 6) · registre (si escena = 8 i té registre i NO aliada_capitana i NO reunio_comencada) · esc8g (si escena = 8 i aliada_capitana) · esc8 (si escena = 8) · res

[revisio]
    CAPITANA ROIG: Cinc minuts, doctora. Tinc un vaixell.
    ↪ revisio_menu

[revisio_menu]
    ▸ I la periodista? ⟨una vegada⟩ → nadia
    ▸ Has vist la Juana? ⟨una vegada, si NO juana_explica⟩ → juana
    ▸ La vàlvula d'aquesta nit... ⟨una vegada⟩ → valvula
    ▸ Com es paga, una campanya així? ⟨una vegada⟩ → gasoil
    ▸ Antecedents? Operacions, malalties... ⟨una vegada⟩ → antecedents
    ▸ Quantes hores dorms? ⟨una vegada⟩ → dormir
    ▸ Ja està. Tensió perfecta. → fi

[juana]
    CAPITANA ROIG: La Juana és al laboratori. Sempre hi és. És com una planta, però amb més ansietat.
    ⇒ +juana_laboratori
    ↪ revisio_menu

[gasoil]
    CAPITANA ROIG: Aquest any, el gasoil el paga una donació. La Fundació Blau Net.
    CAPITANA ROIG: Sense ells, no sortíem. Mar Obert no té ni per a cordills.
    ⇒ +sap_blaunet
    ↪ revisio_menu

[nadia]
    CAPITANA ROIG: Va amb el paquet. Condició de la donació: que algú expliqui la campanya.
    CAPITANA ROIG: Explicar, explica poc. Menja molt.
    ↪ revisio_menu

[valvula]
    CAPITANA ROIG: Si l'Ernest diu que és vella, és vella. Trenta-cinc anys de mar, doctora.
    CAPITANA ROIG: Port Hallen. Una inspecció i tornem a sortir.
    ↪ revisio_menu

[fi]
    CAPITANA ROIG: Com sempre. Bon dia, doctora.
    ⇒ +revisio_capitana, revisions += 1, pacient := ""

[cabina2]
    CAPITANA ROIG: Doctora? Les revisions, a la infermeria. Crida'm pel 6 i hi vinc.

[pont3]
    CAPITANA ROIG: L'Ernest diu que l'arregla ell. Si l'arregles tu, millor: ell té feina.
    CAPITANA ROIG: I fes via, Iri. Vull avisar l'oficina.

[esc6]
    CAPITANA ROIG: La Juana sempre torna, doctora. Sempre. ⟨si juga vet⟩
    CAPITANA ROIG: I si em vens a interrompre, que sigui per una urgència.

[registre]
    NARRADOR: La Vet posa la pàgina del registre al costat del contracte de Blau Net.
    NARRADOR: La Capitana les mira molta estona. S'asseu. No diu res.
    CAPITANA ROIG: Una periodista que ven el que sent, i una fundació que la hi va posar. Doctora, he estat molt burra. ⟨si nadia_denunciada⟩
    CAPITANA ROIG: Blau Net. «Per un mar més net, junts». Junts.
    CAPITANA ROIG: Galway. I que el guardacostes ens vingui a buscar nedant.
    NARRADOR: La Capitana està amb vosaltres. Aliats: {aliats} de 4.
    ⇒ perd registre, +aliada_capitana, +rumb_galway, aliats += 1

[esc8g]
    CAPITANA ROIG: Galway, doctora. I el guardacostes, que nedi.
    CAPITANA ROIG: Si tens alguna cosa més a dir, digues-la a tothom. Al menjador.
    ▸ Reuneix tothom, Capitana. Ara. → reunir
    ▸ Encara no. → (es queda) · FI

[esc8]
    CAPITANA ROIG: Doctora. Port Hallen és a cinc hores. Si tens alguna cosa a dir, digues-la a tothom.
    CAPITANA ROIG: Al menjador. Jo hi baixo quan em diguis.
    ▸ Reuneix tothom, Capitana. Ara. → reunir
    ▸ Encara no. → (es queda) · FI

[res]
    CAPITANA ROIG: Ara no, doctora. ⟨si juga vet⟩

[reunir]
    CAPITANA ROIG: Al menjador, doncs. Tothom. I que la maquinista baixi del pont.
    ⇒ +reunio_comencada, esdeveniment situar, esdeveniment anar

[antecedents]
    CAPITANA ROIG: Una apendicitis, el 2004. A l'altura de les Fèroe.
    VET: Qui te la va operar?
    CAPITANA ROIG: Ningú. Quan vam arribar a port, ja m'havia passat.
    VET: Les apendicitis no passen.
    CAPITANA ROIG: Tenia un vaixell, doctora.
    ↪ revisio_menu

[dormir]
    CAPITANA ROIG: Les que calen.
    VET: En números.
    CAPITANA ROIG: Quatre. Tres, si baixa el baròmetre.
    VET: Apunto «poques».
    ↪ revisio_menu

```

## Diàleg `enviat` amb Ernest Bastida

```
COMENÇA A: enviat

[enviat]
    NARRADOR: Les dades són a Mar Obert, a tres redaccions, al blog de la Juana i a l'institut de pesca d'Irlanda.
    NARRADOR: El guardacostes de Valmark, que ja no té res a buscar, fa mitja volta.
    CAPITANA ROIG: Galway. ⟨si NO rumb_galway⟩
      ⇒ +rumb_galway
    ERNEST BASTIDA: Em convides a aquell cafè?
    VET: Sí. Però el pagues tu.
    ERNEST BASTIDA: No tinc diners.
    VET: En tens tres-cents mil.
    ERNEST BASTIDA: ...Ja no.
    ⇒ −sync_satellit, esdeveniment final

```

## Diàleg `fitxes` amb Vet

```
COMENÇA A: tria

[tria]
    JUGADORA: Revisió d'inici de campanya. Qui ve ara?
    ▸ La Capitana. ⟨si NO revisio_capitana⟩ → capitana
    ▸ En Tomàs, el cuiner. ⟨si NO revisio_tomas⟩ → tomas
    ▸ La Nadia, la periodista. ⟨si NO revisio_nadia⟩ → nadia
    ▸ El Marcel, el mariner. ⟨si NO revisio_marcel⟩ → marcel
    ▸ En Bastida, el contramestre. → bastida
    ▸ La Juana, la biòloga. ⟨si NO juana_explica⟩ → juana
    ▸ Ningú, de moment. → (es queda) · FI

[capitana]
    NARRADOR: Pel canal 6: «Revisió mèdica. Capitana, a la infermeria, sisplau.»
    NARRADOR: Al cap d'un moment, truquen a la porta.
    ⇒ pacient := "capitana"

[tomas]
    NARRADOR: Pel canal 6: «Revisió mèdica. Tomàs, a la infermeria, sisplau.»
    NARRADOR: Al cap d'un moment, truquen a la porta.
    ⇒ pacient := "tomas"

[nadia]
    NARRADOR: Pel canal 6: «Revisió mèdica. Nadia Vidal, a la infermeria, sisplau.»
    NARRADOR: Al cap d'un moment, truquen a la porta.
    ⇒ pacient := "nadia"

[marcel]
    NARRADOR: Pel canal 6: «Revisió mèdica. Marcel, a la infermeria, sisplau.»
    NARRADOR: Al cap d'un moment, truquen a la porta.
    ⇒ pacient := "marcel"

[bastida]
    NARRADOR: Pel canal 6: «Revisió mèdica. Ernest Bastida, a la infermeria, sisplau.»
    ERNEST BASTIDA: Ara no puc, doctora. Més tard.
    ⇒ +bastida_ara_no

[juana]
    NARRADOR: Pel canal 6: «Revisió mèdica. Juana Ferrer, a la infermeria, sisplau.»
    NARRADOR: Ningú no contesta.
    CAPITANA ROIG: La Juana és al laboratori, doctora. Sempre hi és. ⟨si NO juana_laboratori⟩
    ⇒ +juana_no_contesta

```

## Diàleg `juana` amb Juana Ferrer

```
COMENÇA A: trobada (si escena = 2 i no ha vist juana.trobada) · hola (si escena = 2) · mostra (si escena = 7 i té mostra7) · esc7 (si escena = 7 i NO juana_parla) · esc7b (si escena = 7) · esc8 (si escena = 8) · res

[trobada]
    JUANA FERRER: Ah. M'heu trobat.
    VET: Et pensàvem desapareguda.
    JUANA FERRER: Desapareguda no. Descansant. Porto quaranta-vuit hores sense parlar amb ningú.
    JUANA FERRER: Bé, amb l'Ernest. Però l'Ernest no compta: només diu «deu minuts». Ha estat meravellós.
    ↪ menu

[hola]
    JUANA FERRER: Encara aquí, doctora?
    ↪ menu

[menu]
    ▸ Revisió mèdica. Cinc minuts. ⟨una vegada⟩ → revisio
    ▸ Aquesta nit algú ha obert una vàlvula. Ens volen portar a Port Hallen. ⟨si NO juana_explica⟩ → valvula
    ▸ Res. Continua descansant. → (es queda) · FI

[valvula]
    JUANA FERRER: El metge d'abans va plegar de cop. Tu vas arribar de cop.
    VET: I per això soc l'única que no sap res. Ni on és la proa.
    JUANA FERRER: Ets a la proa.
    NARRADOR: La Juana tanca el llibre. S'ho pensa.
    JUANA FERRER: Aquesta nit he baixat al Punt 7, amb la zòdiac. Al costat hi ha una plataforma que no surt a cap mapa.
    JUANA FERRER: Al fang hi ha el marcador químic que Skarn posa als seus residus. Els de la mina que diuen que tracten a terra.
    JUANA FERRER: Skarn és de Valmark. Bé, mig: el cinquanta-u per cent és de l'estat.
    VET: I Port Hallen?
    JUANA FERRER: És a Valmark.
    JUANA FERRER: N'he agafat una mostra. L'he etiquetada Mostra 7. I l'he posada on ningú no la buscarà.
    JUANA FERRER: L'any passat, al Punt 7, vaig comptar dos mil ous d'arengada per metre quadrat. Aquest any, cap.
    VET: I a la gent? Què fa, aquest marcador?
    JUANA FERRER: A la gent, no ho sé. Als peixos s'hi queda. Hi ha qui se'ls menja.
    VET: I les dades? Si et passa alguna cosa...
    JUANA FERRER: Al portàtil. Xifrades. La contrasenya és el nom de la meva mare.
    JUANA FERRER: No us diré quin és. Encara no us conec.
    NARRADOR: La Vet agafa el walkie.
    VET: Iri. No volen enfonsar el vaixell. Volen que arribem a Port Hallen, a Valmark. Amb la mostra a bord.
    IRI: ...Valmark.
    ⇒ +juana_explica, +juana_contrasenya
    ↪ menu

[revisio]
    JUANA FERRER: Estic bé. Tinc fred i son, que és com estar viva.
    ↪ menu

[esc7]
    JUANA FERRER: Al dipòsit d'aigua 2. On ningú no beu.
    JUANA FERRER: Fa anys que està fora de servei, i està tancat amb una clau antiga que no té ningú.
    JUANA FERRER: No vaig fer servir la clau. Vaig treure les frontisses del registre i les vaig tornar a posar.
    JUANA FERRER: Les màquines no són cosa meva, però les frontisses sí.
    VET: Tu no et mous d'aquí.
    ⇒ +juana_parla

[esc7b]
    JUANA FERRER: El dipòsit 2. El registre és al rebost. Jo no em moc, ja ho sé.
    JUANA FERRER: La clau no la té ningú. Jo vaig treure les frontisses, i les vaig tornar a posar. ⟨si NO registre_obert⟩
    VET: Algú ha volgut forçar el pany. ⟨si prova_pany i NO registre_obert⟩
    JUANA FERRER: Doncs ja saben on és. Afanya't, doctora. ⟨si prova_pany i NO registre_obert⟩
    VET: En Tomàs té una clau. Però està ofès: li han robat un entrepà de truita. ⟨si tomas_ofes i NO clau_donada i NO registre_obert⟩
    JUANA FERRER: Un entrepà de truita? Me'l vaig menjar jo, a la caixa de cadenes. El que em va portar qui em va tancar. ⟨si tomas_ofes i NO clau_donada i NO registre_obert⟩

[mostra]
    NARRADOR: La Juana mira la bossa molta estona.
    JUANA FERRER: A Minamata, al Japó, els primers a emmalaltir van ser els gats.
    JUANA FERRER: Ningú no en va fer cas fins que van ser les persones.
    VET: Iri. Les sardines del Marcel, d'on són? ⟨si marcel_secret⟩
    IRI: De llauna. De Portugal. ⟨si marcel_secret⟩
    VET: Iri. El gat que corre per màquines, què menja? ⟨si NO marcel_secret⟩
    IRI: Sardines de llauna. De Portugal. ⟨si NO marcel_secret⟩
    VET: Bé.
    NARRADOR: Una pausa.
    VET: Per res.
    NARRADOR: La Juana es queda la bossa a la falda, sota les mantes. No la deixarà anar fins a terra.
    CAPITANA ROIG: Atenció. Falten cinc hores per entrar a aigües de Valmark.
    CAPITANA ROIG: Valmark ens ofereix l'escorta d'un guardacostes. Per la nostra seguretat.
    TÍTOL: Falten 5 hores.
    TÍTOL: Acte 3 · Mostra 7
    TÍTOL: Dues de la matinada.
    IRI: Vet. Em sents? Soc al pont, de guàrdia.
    VET: Tenim la Mostra 7. La Juana la té a la falda i no la deixarà anar.
    IRI: Cinc hores. Si entrem a Valmark, la mostra es perd a la duana. I sense l'antena, les dades no surten.
    VET: Doncs abans d'arribar-hi, ho diem. Davant de tothom: qui ha estat, i per què ho sabem.
    IRI: Al menjador. La Capitana pot reunir tothom. Jo no em puc moure del pont fins que ens cridi.
    VET: I la Capitana encara es pensa que Blau Net és una fundació.
    IRI: El registre és a l'USB. Si l'imprimeixo aquí, te'l puc enviar pel muntacàrregues, a la cuina. ⟨si té usb (iri)⟩
    IRI: El registre és a l'USB, i l'USB el tens tu. Envia-me'l pel muntacàrregues i te'l torno imprès. ⟨si no té usb (iri)⟩
    ⇒ perd mostra7, escena := 8, hores := 5, esdeveniment situar, esdeveniment situar, esdeveniment protagonista

[esc8]
    JUANA FERRER: La Capitana és a la seva cabina. Que us reuneixi ella: a ella l'escolten.
    JUANA FERRER: Ves, doctora. Jo ja hi seré, a la reunió. Amb dues mantes.

[res]
    JUANA FERRER: Ara no. Estic comptant.

```

## Diàleg `marcel` amb Marcel

```
COMENÇA A: revisio (si escena = 2 i pacient = "marcel") · callat (si marcel_enfadat) · amic (si aliat_marcel) · esc6 (si escena ≥ 6 i escena ≤ 7) · res

[revisio]
    MARCEL: No sé res de res.
    ↪ revisio_menu

[revisio_menu]
    ▸ Qui ha obert la vàlvula, aquesta nit? ⟨una vegada⟩ → valvula
    ▸ Què feies a les tres de la matinada? ⟨una vegada⟩ → nit
    ▸ Vacunes al dia? ⟨una vegada⟩ → vacunes
    ▸ Al·lèrgies? ⟨una vegada⟩ → alergies
    ▸ Ja està. Pots marxar. → fi

[valvula]
    MARCEL: Si voleu saber qui ha obert la vàlvula: el Tomàs. O el vent. O tu.
    ↪ revisio_menu

[nit]
    MARCEL: Dormia. Com un tronc. Un tronc que no s'aixeca per res.
    ↪ revisio_menu

[fi]
    MARCEL: Ja ho sabia. Estic més sa que tots vosaltres.
    ⇒ +revisio_marcel, revisions += 1, pacient := ""

[esc6]
    MARCEL: Aquesta tarda he sentit cops a proa. Pensava que eren fantasmes. Jo crec en fantasmes. ⟨si NO juana_trobada⟩
    MARCEL: Diuen que la Juana era a la caixa de cadenes. Els cops d'aquesta tarda. I jo pensant que eren fantasmes. ⟨si juana_trobada⟩
    ⇒ +cops_marcel
    ↪ esc6_menu

[esc6_menu]
    ▸ Aquest gat... ⟨si juga iri i NO marcel_secret⟩ → secret
    ▸ Res. Bona nit. → (es queda) · FI

[secret]
    MARCEL: D'acord. La nit de la vàlvula jo era a la sala de màquines.
    MARCEL: Hi baixo cada nit a donar-li sardines. El vaig trobar fa una setmana, amagat darrere el motor.
    MARCEL: Vaig mentir per protegir-lo. Si la Capitana el veu, el desembarca.
    MARCEL: I jo no tinc ningú més a bord que m'escolti.
    IRI: És meu.
    MARCEL: ...El gat?
    IRI: En Diu. Va a la meva motxilla.
    MARCEL: Diu.
    NARRADOR: El mira.
    MARCEL: Jo li deia Capità.
    NARRADOR: Una pausa.
    MARCEL: O sigui que he mentit a tothom per protegir el teu gat.
    IRI: Sí.
    MARCEL: De res, eh.
    ⇒ +marcel_secret
    ▸ Hauries d'haver dit la veritat. Ara tothom sospita de tu. → enfadat_veritat
    ▸ No ho sabrà ningú. Ni que eres a màquines, ni el gat. → aliat
    ▸ Ho diré jo a la Capitana. El gat i tot. → enfadat_capitana

[aliat]
    MARCEL: Capità. Diu. El que sigui.
    NARRADOR: El Marcel està amb vosaltres. Aliats: {aliats} de 4.
    ⇒ +aliat_marcel, aliats += 1

[enfadat_veritat]
    MARCEL: Mira qui parla.
    ⇒ +marcel_enfadat

[enfadat_capitana]
    MARCEL: Doncs a mi no m'hi posis.
    ⇒ +marcel_enfadat

[callat]
    NARRADOR: El Marcel no diu res. En Diu continua menjant sardines.

[amic]
    MARCEL: Capità. Diu. El que sigui.
    DIU: Mrrau.

[res]
    MARCEL: No sé res de res.

[vacunes]
    MARCEL: Totes. I cap xip.
    VET: Les vacunes no porten xip.
    MARCEL: Això és el que diria el xip.
    ↪ revisio_menu

[alergies]
    MARCEL: Als gats. Molt. Si n'hi hagués cap a bord, ja ho sabríem tots.
    NARRADOR: No esternuda gens.
    ↪ revisio_menu

```

## Diàleg `nadia` amb Nadia Vidal

```
COMENÇA A: revisio (si escena = 2 i pacient = "nadia") · pillada (si escena = 5 i vet_amagada i NO nadia_decidida) · esc6 (si escena = 6 i aliada_nadia i juga vet) · res

[revisio]
    NADIA VIDAL: Hola, doctora. Vaig una mica marejada, eh.
    ↪ revisio_menu

[revisio_menu]
    ▸ Has vist la Juana? ⟨una vegada, si NO juana_explica⟩ → juana
    ▸ Com estàs? ⟨una vegada⟩ → mareig
    ▸ Què fas a bord, exactament? ⟨una vegada⟩ → feina
    ▸ Què has esmorzat? ⟨una vegada⟩ → esmorzar
    ▸ Tens metge de capçalera? ⟨una vegada⟩ → capcalera
    ▸ Ja està. Beu aigua. → fi

[juana]
    NADIA VIDAL: La Juana està bé.
    NARRADOR: Una pausa.
    NADIA VIDAL: Crec. No la conec tant.
    ↪ revisio_menu

[mareig]
    NADIA VIDAL: Mareig. Molt. Per això em passo el dia al camarot.
    ⇒ +nadia_mareig
    ↪ revisio_menu

[feina]
    NADIA VIDAL: Explico la campanya. Blau Net paga, jo escric.
    NADIA VIDAL: Freelance: vol dir que si no escric, no menjo.
    ↪ revisio_menu

[fi]
    NADIA VIDAL: I menjar poc. Ja ho sé.
    ⇒ +revisio_nadia, revisions += 1, pacient := ""

[pillada]
    NADIA VIDAL: D'acord. D'acord.
    NADIA VIDAL: Tinc un escàner. Escolto el walkie. Tots els canals.
    NADIA VIDAL: Blau Net em paga un any de sou perquè expliqui on és el vaixell i què s'hi diu. A una tal Hedda Lind.
    NADIA VIDAL: Avui la Lind m'ha demanat una cosa més: una foto de la mostra abans d'avisar «el tècnic».
    NADIA VIDAL: Jo escolto. I avui, una foto. Però no toco res. No he tocat cap vàlvula.
    VET: Qui és el tècnic?
    NADIA VIDAL: Algú de bord que s'encarrega de la part tècnica. No sé qui és. De veritat.
    NADIA VIDAL: Mira, jo no soc dolenta. Soc pobra. És diferent.
    VET: No, no és diferent.
    NADIA VIDAL: Una mica, sí.
    VET: No.
    NADIA VIDAL: D'acord, no ho és. Però em pagaven el sou d'un any per escoltar una ràdio. Tu no ho faries?
    NARRADOR: Una pausa.
    VET: Depèn de la ràdio.
    ⇒ +nadia_escolta
    ▸ Ho sabrà la Capitana. → denunciada
    ▸ Continuaràs informant la Lind. Però del que jo et digui. I quan arribem a terra, escriuràs la història de debò. Amb la teva firma. → aliada

[denunciada]
    NARRADOR: Mitja hora després, la Capitana es queda l'escàner i el telèfon, i la Nadia, tancada al seu camarot fins a port.
    CAPITANA ROIG: Una periodista que ven el que sent. Blau Net és una fundació, doctora. Segur que l'han enganyada a ella també.
    ⇒ +nadia_denunciada, +nadia_decidida
    ↪ ultima

[aliada]
    NARRADOR: La Nadia s'ho pensa molt.
    NADIA VIDAL: Amb la meva firma?
    VET: Amb la teva firma.
    NADIA VIDAL: ...D'acord.
    NARRADOR: La Nadia està amb vosaltres. Aliats: {aliats} de 4.
    ⇒ +aliada_nadia, +nadia_decidida, aliats += 1
    ↪ ultima

[ultima]
    NADIA VIDAL: Una cosa. La Lind diu que «el tècnic» ja s'encarrega de la biòloga.
    NADIA VIDAL: No sé què vol dir. No m'agrada com ho ha dit.
    NARRADOR: De la paret de la cuina surt una veu de llauna.
    IRI: Em sents?
    VET: Sembla que parlis des de dins d'una trompeta.
    IRI: És un tub de llautó de 1984. Respecte.
    VET: Iri. Ja sé qui escolta: la Nadia, amb un escàner. I la Lind diu que «el tècnic» s'encarrega de la Juana.
    IRI: El llibre a terra. La llanterna encesa. La Juana no descansa.
    IRI: La busquem. Ara.
    VET: On? D'aquest vaixell, jo només conec la infermeria i la cuina.
    IRI: Per tot arreu. Pregunta a tothom: aquí tothom sent coses. Al passadís hi ha el plànol d'emergència.
    IRI: I ens parlem pel tub. El walkie, només per dir mentides.
    TÍTOL: Onze de la nit.
    ⇒ +tub_de_veu, escena := 6, esdeveniment situar

[esc6]
    NADIA VIDAL: Doctora. Digues què he de dir a la Lind.
    ▸ Digues-li que han sentit soroll a la sala de bombes. ⟨si NO bastida_baixa⟩ → soroll
    ▸ Res, de moment. → (es queda) · FI

[soroll]
    NADIA VIDAL: Fet.
    NARRADOR: A popa, en Bastida rep un missatge. Deixa la llanterna i baixa a la sala de bombes.
    ⇒ +bastida_baixa

[res]
    NADIA VIDAL: Ara no, que vaig marejada.

[esmorzar]
    NADIA VIDAL: Res. Amb aquest mareig...
    NADIA VIDAL: Un te. I una galeta. Mitja.
    VET: Apuntat. Mitja galeta.
    ↪ revisio_menu

[capcalera]
    NADIA VIDAL: Soc freelance. Tinc un cercador.
    VET: I què et diu?
    NADIA VIDAL: Que em moriré de tot. Per això ja no li pregunto.
    ↪ revisio_menu

```

## Diàleg `paperets` amb Vet

```
COMENÇA A: proposta

[proposta]
    JUGADORA: Escric una mentida i l'envio amunt. Que la triï ella. ⟨si no (ha triat paperets.proposta.flam o ha triat paperets.proposta.ernest)⟩
    JUGADORA: Una altra, doncs. ⟨si ha triat paperets.proposta.flam o ha triat paperets.proposta.ernest⟩
    ▸ «La Mostra 7 és dins un flam, a la cambra freda.» ⟨una vegada⟩ → flam
    ▸ «Ho va dir l'Ernest: a la cambra freda estaria més segura.» ⟨una vegada, si prova_cambra⟩ → ernest
    ▸ «La Juana va deixar la mostra a la cambra freda de la cuina, darrere les postres. Diu que allà sempre hi fa fred.» → postres
    ▸ (Pensar-hi una mica més) → (es queda) · FI

[flam]
    [SO: muntacarregues] NARRADOR: El muntacàrregues puja i baixa.
    NARRADOR: La resposta de la Vet: «Ningú no s'ho empassarà.»
    ↪ proposta

[ernest]
    [SO: muntacarregues] NARRADOR: El muntacàrregues puja i baixa.
    NARRADOR: La resposta de la Vet: «Ni pensar-hi. Si és ell, sabrà que el tenim al cap.»
    JUGADORA: ...Si és ell.
    ⇒ +vet_sospita
    ↪ proposta

[postres]
    [SO: muntacarregues] NARRADOR: El muntacàrregues puja i baixa.
    NARRADOR: La resposta de la Vet: «Aquesta. Digues-la pel walkie. Jo m'amago.»
    ⇒ +mentida_triada

```

## Diàleg `portatil` amb Iri

```
COMENÇA A: contrasenya

[contrasenya]
    NARRADOR: «CONTRASENYA:»
    ▸ Pili65 ⟨una vegada, si postal_vista⟩ → pili
    ▸ Pilar ⟨si sap_pilar⟩ → pilar
    ▸ Juana ⟨una vegada⟩ → juana
    ▸ (Pensar-hi una mica més) → (es queda) · FI

[pili]
    NARRADOR: «Contrasenya incorrecta.»
    JUGADORA: Massa curta. Ja ho deia jo.
    ↪ contrasenya

[juana]
    NARRADOR: «Contrasenya incorrecta.»
    JUGADORA: Era massa fàcil. La Juana no és fàcil.
    ↪ contrasenya

[pilar]
    [SO: portatil] NARRADOR: «Benvinguda, Juana.»
    JUGADORA: Fotos de la plataforma. Les coordenades del Punt 7. L'anàlisi del marcador de Skarn.
    JUGADORA: I una carpeta: «Qui ens paga el gasoil?»
    NARRADOR: El registre de fundacions de Valmark. Fundació Blau Net. Patró únic: Skarn.
    JUGADORA: La Capitana això no ho sap. Si ho sabés, no hauria acceptat ni un litre.
    JUGADORA: Un correu de l'Ernest, de fa tres dies.
    NARRADOR: «Juana, fes-me'n una còpia, de les dades. Per seguretat. Les guardo a la caixa del pont.»
    JUGADORA: La Juana no li va contestar.
    JUGADORA: I l'última entrada del registre de la Juana. D'avui, a les 15:10.
    NARRADOR: «Algú ha remenat el laboratori. Me'n vaig a la sala de bombes: allà no hi ve ningú. La 7 és on ningú no beu.»
    JUGADORA: Còpia. Sempre faig còpia. Les màquines m'han ensenyat a no fiar-me de ningú.
    JUGADORA: Les dades, cap a terra: per satèl·lit, des del pont.
    JUGADORA: Però la Juana ho va escriure a les tres i deu. I ara són les nou passades.
    JUGADORA: Sis hores a la sala de bombes? Ningú no s'hi està sis hores. Ni la Juana.
    IRI: Vet. He obert el portàtil. La Juana hi escriu que se'n va a la sala de bombes. Que la 7 és «on ningú no beu».
    VET: On ningú no beu. En un vaixell d'una ONG, de nit... Això és a tot arreu.
    VET: I fa sis hores que hi és? Ves-hi, Iri.
    IRI: Hi baixo. L'escotilla és al passadís de baix.
    ⇒ +portatil_obert, +prova_blaunet, +prova_correu, rep usb

```

## Diàleg `quadern` amb Vet

```
COMENÇA A: llegir

[llegir]
    JUGADORA: El quadern. El que sabem:
    JUGADORA: La brida de la bomba: un nus Bastida, amb una volta de més. ⟨si prova_nus_brida⟩
    JUGADORA: En Bastida fa el nus amb una volta de més. «Un nus ha de tenir un secret.» ⟨si prova_volta⟩
    JUGADORA: En Bastida: «El mar ja està mort, doctora. Només que encara no ho sap.» ⟨si bastida_arengades⟩
    JUGADORA: En Tomàs va veure el Marcel baixant a màquines a les tres. El Marcel diu que dormia. ⟨si marcel_vist i NO marcel_secret⟩
    JUGADORA: El Marcel baixa cada nit a màquines a donar sardines a en Diu. Per això mentia. ⟨si marcel_secret⟩
    JUGADORA: El Marcel té pèls de gat al jersei. I fa olor de sardina. ⟨si marcel_gat⟩
    JUGADORA: La Nadia diu que té mareig. I repeteix croissant. ⟨si nadia_croissant⟩
    JUGADORA: En Tomàs té una clau que no sap què obre. ⟨si tomas_clau⟩
    JUGADORA: El gasoil d'aquest any el paga la Fundació Blau Net. ⟨si sap_blaunet⟩
    JUGADORA: En Bastida, a la revisió: les mostres «a la cambra freda estarien més segures». ⟨si prova_cambra⟩
    JUGADORA: En Bastida té un tall fresc al palmell. «Un cap. En tallo deu cada dia.» ⟨si prova_tall_ma⟩
    JUGADORA: Una gota de sang seca a la vora del panell de la ràdio. ⟨si prova_sang⟩
    JUGADORA: El cable de la ràdio, tallat amb una cisalla amb una dent mellada. ⟨si prova_osca⟩
    JUGADORA: El Ferran, el metge d'abans, s'ha comprat un pis a primera línia de mar. ⟨si ferran_pis⟩
    JUGADORA: Valmark escolta tota la banda de ràdio. ⟨si banda_escoltada⟩
    JUGADORA: El patró únic de la Fundació Blau Net és Skarn. ⟨si prova_blaunet⟩
    JUGADORA: En Bastida va demanar a la Juana una còpia de les dades. «Per seguretat.» ⟨si prova_correu⟩
    JUGADORA: La Nadia escolta el walkie amb un escàner, per a una tal Hedda Lind. Blau Net li paga el sou. ⟨si nadia_escolta⟩
    JUGADORA: La Juana, al seu registre, a les 15:10: «Me'n vaig a la sala de bombes. La 7 és on ningú no beu.» ⟨si portatil_obert⟩
    JUGADORA: L'antena del satèl·lit, desorientada. Al pal, de nit, no s'hi puja. ⟨si satellit_provat⟩
    JUGADORA: La cisalla del taller té una dent mellada. A les quatre de la matinada, no la tenia. ⟨si prova_cisalla⟩
    JUGADORA: La Juana: qui la va tancar feia olor de pipa. ⟨si prova_pipa⟩
    JUGADORA: Al pany del dipòsit 2 hi ha rascades: algú el va voler forçar. ⟨si prova_pany⟩
    JUGADORA: La contrasenya del portàtil de la Juana és el nom de la seva mare. ⟨si juana_contrasenya⟩
    JUGADORA: Al pallol falta un cadenat. ⟨si cadenat_falta⟩
    JUGADORA: El Marcel va sentir cops a proa, aquesta tarda. ⟨si cops_marcel⟩
    JUGADORA: Encara no hi ha res apuntat. ⟨si NO prova_nus_brida i NO prova_volta i NO bastida_arengades i NO marcel_vist i NO marcel_secret i NO marcel_gat i NO nadia_croissant i NO tomas_clau i NO sap_blaunet i NO prova_cambra i NO prova_tall_ma i NO prova_sang i NO prova_osca i NO ferran_pis i NO banda_escoltada i NO prova_blaunet i NO prova_correu i NO nadia_escolta i NO satellit_provat i NO prova_cisalla i NO prova_pipa i NO prova_pany i NO juana_contrasenya i NO cadenat_falta i NO cops_marcel i NO portatil_obert⟩

```

## Diàleg `radio` amb Rut

```
COMENÇA A: trucada

[trucada]
    RUT: Arenga, aquí Mar Obert. Us sento. Per fi.
    IRI: Rut. Fem escala a Port Hallen. Una avaria.
    RUT: Arenga, no envieu res de les mostres per aquí. Valmark escolta tota la banda.
    IRI: Perfecte. Gràcies.
    RUT: I una altra cosa. El vostre metge, el Ferran...
    RUT: S'acaba de comprar un pis. A primera línia de mar.
    IRI: Amb el sou de Mar Obert?
    RUT: Amb el sou de Mar Obert no et compres ni l'aparcament.
    NARRADOR: La Vet ho ha sentit tot pel walkie.
    VET: Per això soc aquí. El Ferran feia vint anys que navegava amb vosaltres. Us coneixia a tots. Hauria vist coses.
    VET: Algú li va pagar perquè plegués, comptant que a dos dies de salpar Mar Obert només trobaria algú que no sap on és la proa.
    VET: I aquesta soc jo.
    IRI: Ets un error de càlcul.
    VET: Soc el millor error de càlcul que tindran mai.
    NARRADOR: Passos a la porta. En Bastida, amb la revisió feta, s'atura a mirar.
    IRI: La tapa del panell de la ràdio, encara oberta. L'he de tancar ara mateix.
    ⇒ −sync_radio, +rut_parlat, +banda_escoltada, +ferran_pis

```

## Diàleg `reunio` amb Ernest Bastida

```
COMENÇA A: torna (si ha vist reunio.inici) · inici

[inici]
    NARRADOR: Al menjador, tothom amb una tassa de te, sota el pòster de la Cimera dels Oceans.
    VET: Algú d'aquesta taula ha obert una vàlvula, ha tallat una ràdio i ha tancat la Juana en una caixa de cadenes.
    NARRADOR: Silenci. En Tomàs deixa la tassa.
    ↪ qui

[torna]
    NARRADOR: Tothom espera.
    ↪ qui

[qui]
    VET: Ha estat...
    ▸ Ernest Bastida. → bastida
    ▸ El Marcel. → marcel
    ▸ La Nadia. ⟨si aliada_nadia⟩ → nadia
    ▸ En Tomàs. → tomas
    ▸ La Capitana. → capitana
    ▸ (Encara no ho tinc. Pensar-hi una mica més) → (es queda) · FI

[marcel]
    MARCEL: Jo? Jo dono sardines a un gat que no existeix.
    NARRADOR: Ho diu en veu baixa, mirant l'Iri. ⟨si aliat_marcel⟩
    VET: No. Encara no ho tinc.
    ↪ qui

[nadia]
    NADIA VIDAL: Jo escolto. I faig fotos de postres. Vàlvules, no.
    VET: No. Encara no ho tinc.
    ↪ qui

[tomas]
    TOMÀS: Jo faig pa.
    NARRADOR: S'ofèn una mica.
    VET: No. Encara no ho tinc.
    ↪ qui

[capitana]
    CAPITANA ROIG: Doctora. Sisplau.
    VET: No. Encara no ho tinc.
    ↪ qui

[bastida]
    NARRADOR: En Bastida riu. No gaire.
    ERNEST BASTIDA: Jo?
    VET: Tres coses, Ernest.
    ↪ proves

[proves]
    ▸ Els pèls de gat. ⟨una vegada, si marcel_gat⟩ → p_gat
    ▸ La cisalla mellada. ⟨una vegada, si prova_cisalla i prova_osca⟩ → p_cisalla
    ▸ El tall a la mà. ⟨una vegada, si prova_tall_ma⟩ → p_ma
    ▸ El mareig i el croissant. ⟨una vegada, si nadia_croissant⟩ → p_croissant
    ▸ La pipa. ⟨una vegada, si prova_pipa⟩ → p_pipa
    ▸ L'escàner. ⟨una vegada, si nadia_escolta⟩ → p_escaner
    ▸ El nus de la brida. ⟨una vegada, si prova_nus_brida i prova_volta⟩ → p_nus
    ▸ El correu de les dades. ⟨una vegada, si prova_correu⟩ → p_correu
    ▸ La clau d'en Tomàs. ⟨una vegada, si tomas_clau⟩ → p_clau
    ▸ «A la cambra freda estarien més segures.» ⟨una vegada, si prova_cambra⟩ → p_cambra
    ▸ Blau Net. ⟨una vegada, si prova_blaunet⟩ → p_blaunet
    ▸ (Pensar-hi una mica més) → (es queda) · FI

[p_cisalla]
    VET: El cable de la ràdio el va tallar una cisalla amb una dent mellada. La del taller.
    VET: A les quatre de la matinada, l'Iri la va fer servir per tallar la brida, i encara no tenia la dent mellada. I qui estava despert, a les quatre? Qui va venir de seguida quan va sentir la bomba?
    ⇒ proves += 1
    ↪ compta

[p_ma]
    VET: Tens un tall fresc al palmell, Ernest. «Un cap.»
    VET: I al panell de la ràdio hi ha una gota de sang. Aquella xapa talla com un ganivet. ⟨si prova_sang⟩
    ⇒ proves += 1
    ↪ compta

[p_pipa]
    VET: Qui va tancar la Juana a la caixa de cadenes feia olor de pipa. A bord, només en fuma un.
    ⇒ proves += 1
    ↪ compta

[p_nus]
    VET: La brida que lligava la bomba de sentina estava feta amb un nus Bastida.
    ⇒ proves += 1
    ↪ compta

[p_correu]
    VET: Fa tres dies vas demanar a la Juana una còpia de les dades. «Per seguretat. Les guardo a la caixa del pont.»
    ⇒ proves += 1
    ↪ compta

[p_cambra]
    VET: A la revisió em vas preguntar per les mostres de la Juana. Que a la cambra freda estarien més segures.
    ⇒ proves += 1
    ↪ compta

[p_gat]
    VET: Pèls de gat...
    VET: No. Això no és d'ell.
    ↪ compta

[p_croissant]
    VET: El mareig, el croissant...
    VET: No. Això no és d'ell.
    ↪ compta

[p_escaner]
    VET: L'escàner del walkie...
    VET: No. Això no és d'ell.
    ↪ compta

[p_clau]
    VET: La clau d'en Tomàs...
    VET: No. Això no és d'ell.
    ↪ compta

[p_blaunet]
    VET: Blau Net...
    VET: No. Això no és d'ell.
    ↪ compta

[compta]
    ERNEST BASTIDA: Coses que pot haver fet qualsevol, doctora. Això no és res. ⟨si proves ≥ 3⟩
    NARRADOR: Tothom mira l'Iri. ⟨si proves ≥ 3⟩
    ▸ Iri: «Ho dic jo.» ⟨si proves ≥ 3⟩ → iri
    ↪ proves

[iri]
    IRI: Ho dic jo.
    IRI: La brida del quadre de la bomba. El nus Bastida, amb una volta de més.
    IRI: Aquesta volta no l'has ensenyada mai a ningú, Ernest. Dius que un nus ha de tenir un secret.
    NARRADOR: Silenci.
    VET: Ho havies de dir tu, Iri.
    ↪ confessio

[confessio]
    ERNEST BASTIDA: Tres-cents mil euros. I un lloc d'assessor a Skarn, d'aquells on no cal anar-hi.
    VET: Per cansament?
    ERNEST BASTIDA: No. Per diners. Molts.
    ERNEST BASTIDA: Trenta-cinc anys traient gent de l'aigua per un sou de misèria, i un dia et truquen i et diuen una xifra. I descobreixes que tens un preu.
    NARRADOR: Una pausa.
    ERNEST BASTIDA: I que no era tan alt com pensaves.
    ERNEST BASTIDA: Em vaig dir que el mar ja estava mort. Que quan jo era jove les arengades bullien, i ara no en queda ni una. Què hi feia, una mica més de fang?
    NARRADOR: Una pausa.
    ERNEST BASTIDA: M'ho vaig dir perquè la xifra em fes menys vergonya.
    JUANA FERRER: No estava mort. Al Punt 7 encara hi fresaven. Fins l'any passat.
    IRI: Em vas treure de l'aigua.
    ERNEST BASTIDA: I ara t'hi he tornat a tirar. Ja ho sé.
    ERNEST BASTIDA: La vàlvula era la de popa. No us hauríeu enfonsat. Només volia que tornéssim a port.
    ERNEST BASTIDA: La ràdio, perquè ningú de terra us expliqués res.
    NARRADOR: Mira l'Iri.
    ERNEST BASTIDA: T'ho va explicar igualment la Rut.
    ERNEST BASTIDA: El volant, la clau de vàlvules del taller i el portàtil són al fons del mar.
    NARRADOR: Una pausa.
    ERNEST BASTIDA: Al fons del mar hi ha moltes coses, últimament.
    JUANA FERRER: I a mi em vas tancar en una caixa.
    ERNEST BASTIDA: Amb una manta.
    JUANA FERRER: L'entrepà era bo. La resta, no.
    [SO: telefon_satellit] NARRADOR: Sona un telèfon de satèl·lit.
    NARRADOR: El de la Nadia. ⟨si aliada_nadia⟩
    NARRADOR: El de la Nadia. El té la Capitana, requisat. ⟨si NO aliada_nadia⟩
    NARRADOR: Videotrucada. A la pantalla, una dona somriu.
    HEDDA LIND: Senyor Bastida. Entenc que hi ha hagut un inconvenient.
    HEDDA LIND: Si alguna dada surt d'aquest vaixell, Skarn no ha sentit parlar mai de vostè. Vostè és un mariner que ha sabotejat el seu propi vaixell. Molt trist.
    HEDDA LIND: I, doctora, una cosa. Sense el nostre coure no hi ha cotxes elèctrics, ni molins, ni transició.
    HEDDA LIND: Vol ser vostè qui l'atura per un pot de fang?
    VET: No és el coure. És on llenceu el que en sobra.
    HEDDA LIND: Un inconvenient tècnic.
    NARRADOR: Penja.
    NADIA VIDAL: L'he gravada. Tota. ⟨si aliada_nadia⟩
      ⇒ +lind_gravada
    NARRADOR: Una pausa. ⟨si aliada_nadia⟩
    NADIA VIDAL: Soc periodista. Gravo coses. ⟨si aliada_nadia⟩
    NARRADOR: En Bastida s'aixeca, blanc, i surt del menjador.
    [SO: generador_para] NARRADOR: Un minut després, el generador s'atura. El vaixell es queda a les fosques.
    ERNEST BASTIDA: Si no surt res, no ha passat res. Ho sento.
    IRI: Ha tret el relé del generador.
    IRI: L'antena del satèl·lit és al pal. Hi pujo. El terminal té una bateria per a dos enviaments; la resta, generador.
    MARCEL: Hi pujo primer, Iri. L'antena, la desbloquejo jo. ⟨si aliat_marcel⟩
    IRI: I el relé el té ell. A mi no em deixarà acostar.
    VET: Doncs hi baixo jo.
    TÍTOL: Tres de la matinada. Ara necessites les dues.
    ⇒ +bastida_confessa, escena := 9, esdeveniment situar, esdeveniment situar, +sync_satellit, senyal := 12, sai := 2, paquets := 0, esdeveniment anar

```

## Diàleg `tomas` amb Tomàs

```
COMENÇA A: revisio (si escena = 2 i pacient = "tomas") · cuina2 (si escena = 2 i (NO revisio_tomas o (NO sap_raco i NO juana_explica))) · esc5 (si escena = 5) · esc6 (si escena = 6) · esc7 (si escena = 7) · res

[revisio]
    TOMÀS: Revisió? Jo estic bé. Faig pa.
    ↪ revisio_menu

[revisio_menu]
    ▸ Has vist la Juana? ⟨una vegada, si NO juana_explica⟩ → juana
    ▸ Alguna cosa més? Al·lèrgies, manies, secrets? ⟨una vegada⟩ → clau
    ▸ Has dormit, aquesta nit? ⟨una vegada⟩ → nit
    ▸ Algun ensurt de salut? ⟨una vegada⟩ → cremades
    ▸ I tu, què menges? ⟨una vegada⟩ → menjar
    ▸ Ja està. Pots tornar al pa. → fi

[juana]
    TOMÀS: Ahir li vaig portar un entrepà. No el va agafar.
    TOMÀS: M'ha ofès una mica, la veritat.
    TOMÀS: Quan vol estar sola, va on hi ha sol i no hi ha gent.
    ⇒ +sap_raco
    ↪ revisio_menu

[clau]
    TOMÀS: Tinc una clau que no sé què obre. Era del cuiner d'abans.
    TOMÀS: Me la guardo. Una clau sempre obre alguna cosa.
    ⇒ +tomas_clau
    ↪ revisio_menu

[nit]
    TOMÀS: A les tres m'he llevat per posar el pa.
    TOMÀS: He vist el Marcel baixant a màquines. Ell diu que dormia. Doncs dorm caminant.
    ⇒ +marcel_vist
    ↪ revisio_menu

[fi]
    TOMÀS: El pa no espera. Ni per la medicina.
    ⇒ +revisio_tomas, revisions += 1, pacient := ""

[cuina2]
    TOMÀS: Doctora! Una revisió? Crida'm pel 6, que ara tinc les mans a la massa. ⟨si juga vet i NO revisio_tomas⟩
    JUGADORA: I la Juana, Tomàs? L'has vista? ⟨si NO juana_explica⟩
    TOMÀS: Avui no. Quan vol estar sola, va on hi ha sol i no hi ha gent. ⟨si NO juana_explica⟩
    ⇒ +sap_raco

[esc5]
    TOMÀS: Torn de cuina, doctora. Tu renta, jo pasto. ⟨si juga vet⟩
    TOMÀS: I no toquis les postres, que són per demà.
    TOMÀS: És un flam. Un flam ha de reposar una nit. Com les persones.

[esc6]
    TOMÀS: Algú m'ha robat un entrepà de truita de la safata del berenar.
    TOMÀS: Si és la Juana, l'hi perdono.
    ⇒ +entrepa_robat

[esc7]
    TOMÀS: Doctora! Li he fet un altre entrepà a la Juana. Doble de truita. I amb el seu nom. ⟨si juga vet i tomas_content⟩
    TOMÀS: Doctora. Avui no estic per ningú. ⟨si juga vet i NO tomas_content⟩
    ↪ esc7_menu

[esc7_menu]
    ▸ Tomàs. La clau del dipòsit 2. Algú la té? ⟨si juga vet i NO clau_donada i NO tomas_ofes i NO registre_obert⟩ → clau7
    ▸ Tomàs, què et passa? ⟨si juga vet i registre_obert i NO clau_donada i NO tomas_ofes⟩ → passa7
    ▸ L'entrepà se'l va menjar la Juana. Diu que ha estat el millor dia de la campanya. ⟨si juga vet i tomas_ofes i juana_entrepa i NO clau_donada⟩ → entrepa7
    ▸ Res. Fins després. → (es queda) · FI

[clau7]
    TOMÀS: Jo tinc una clau que no sé què obre. Era del cuiner d'abans.
    TOMÀS: Però avui no estic per ningú. Algú m'ha robat un entrepà de truita.
    TOMÀS: Un entrepà fet amb amor, doctora.
    ⇒ +tomas_ofes, +tomas_clau
    ↪ esc7_menu

[passa7]
    TOMÀS: Algú m'ha robat un entrepà de truita.
    TOMÀS: Un entrepà fet amb amor, doctora.
    ⇒ +tomas_ofes
    ↪ esc7_menu

[entrepa7]
    TOMÀS: ...El millor dia?
    TOMÀS: De la campanya?
    NARRADOR: En Tomàs s'eixuga els ulls amb el davantal.
    TOMÀS: Té. La clau. Si obre alguna cosa, que sigui bona.
    ⇒ +clau_donada, +tomas_content, rep clau_tomas

[res]
    TOMÀS: Ara no, que se'm cou el pa.

[cremades]
    TOMÀS: Em vaig cremar amb el forn el 2011. I el 2013. I el 2019.
    VET: Sempre el mateix forn?
    TOMÀS: És un forn amb caràcter. Com jo.
    ↪ revisio_menu

[menjar]
    TOMÀS: El que deixeu al plat.
    TOMÀS: Que últimament és molt.
    VET: No és personal, Tomàs.
    TOMÀS: És menjar, doctora. Tot és personal.
    ↪ revisio_menu

```

## Diàleg `tub` amb Vet

```
COMENÇA A: lluny (si juga iri i no (vet a pont/sala_maquines/cuina/infermeria/menjador) i NO cara_a_cara) · lluny (si juga vet i no (iri a pont/sala_maquines/cuina/infermeria/menjador) i NO cara_a_cara) · esc6 (si escena = 6) · esc7 (si escena = 7) · esc8 (si escena = 8) · esc9 (si escena = 9) · res

[lluny]
    JUGADORA: No contesta. No deu ser a prop de cap boca del tub.

[esc6]
    JUGADORA: On pot ser, la Juana? ⟨si NO cops_sentits⟩
    JUGADORA: En Bastida diu que deu ser a popa, que li agrada el vent. Però quan la Juana vol estar sola, va a proa. ⟨si NO cops_sentits i ha vist bastida.esc6⟩
    JUGADORA: El Marcel diu que aquesta tarda va sentir cops a proa. ⟨si NO cops_sentits i cops_marcel⟩
    JUGADORA: I al pallol falta un cadenat. ⟨si NO cops_sentits i cadenat_falta⟩
    JUGADORA: A en Tomàs li han robat un entrepà de truita. Algú alimenta algú que no pot venir a sopar. ⟨si NO cops_sentits i entrepa_robat⟩
    IRI: Pregunta. Algú haurà sentit alguna cosa. En aquest vaixell, tothom sent coses. ⟨si juga vet i NO cops_sentits i NO cops_marcel⟩
    VET: Pregunta. Algú haurà sentit alguna cosa. En aquest vaixell, tothom sent coses. ⟨si juga iri i NO cops_sentits i NO cops_marcel⟩
    IRI: Cops a proa. On no hi passa ningú. Hi pujo jo a mirar. ⟨si juga vet i NO cops_sentits i cops_marcel⟩
    VET: Cops a proa. On no hi passa ningú. Ves-hi a mirar, Iri. ⟨si juga iri i NO cops_sentits i cops_marcel⟩
    JUGADORA: A proa, a la caixa de cadenes, hi ha un cadenat nou. I cops a dins. ⟨si cops_sentits i NO cadenat_tallat⟩
    IRI: La cisalla és al taller. Però en Bastida és a popa. Si la sent, vindrà. ⟨si cops_sentits i NO cadenat_tallat i NO bastida_baixa i NO nus_lico⟩
    VET: Doncs que no la senti. L'entretinc jo. ⟨si cops_sentits i NO cadenat_tallat i NO bastida_baixa i NO nus_lico⟩
    VET: En Bastida m'està ensenyant el nus. A poc a poc. Ara, Iri: la cisalla. ⟨si cops_sentits i NO cadenat_tallat i nus_lico i NO bastida_baixa⟩
    IRI: La cisalla és al taller. I en Bastida ara és a la sala de bombes, buscant soroll: no ens sentirà. ⟨si cops_sentits i NO cadenat_tallat i bastida_baixa⟩
    JUGADORA: Ja la tenim. Ara, a la infermeria. ⟨si cadenat_tallat⟩

[esc7]
    JUGADORA: La tenim. La Mostra 7. Ara, a la infermeria, que la vegi la Juana. ⟨si mostra_trobada⟩
    VET: La Juana diu que la mostra és al dipòsit 2. Tancat amb una clau que no té ningú. ⟨si NO mostra_trobada⟩
    VET: Ella en va treure les frontisses. ⟨si NO mostra_trobada⟩
    IRI: I algú ja ha volgut forçar el pany del registre. Ens van sentir dir «on ningú no beu». ⟨si prova_pany i NO mostra_trobada⟩
    IRI: Una clau antiga que no té ningú... En Tomàs en té una que no sap què obre. ⟨si tomas_clau i NO clau_donada i NO registre_obert⟩
    IRI: Les frontisses del registre. Amb la clau de tubs ho puc fer jo, des del rebost. ⟨si NO registre_obert⟩
    IRI: Ja està obert. ⟨si registre_obert i NO mostra_trobada⟩

[esc8]
    VET: La Capitana no sap que Blau Net és de Skarn. ⟨si NO aliada_capitana⟩
    IRI: Puc imprimir la pàgina del registre aquí, al pont. Te l'envio pel muntacàrregues, a la cuina. ⟨si NO aliada_capitana i NO registre_impres⟩
    IRI: Ja l'he impresa. Si no la tens, és a la safata. ⟨si NO aliada_capitana i registre_impres⟩
    VET: Galway. La Capitana ho ha entès. ⟨si aliada_capitana⟩
    VET: Ara, la Capitana: que ens reuneixi a tots al menjador. I ho dic jo. ⟨si juga vet⟩
    IRI: Quan la Capitana us reuneixi, baixo. Fins llavors, estic de guàrdia. ⟨si juga iri⟩

[esc9]
    IRI: Encara tinc senyal. Encara hi som.
    VET: En Bastida té el relé a la mà. Hi parlo. ⟨si NO rele_posat⟩
    VET: Ja tens corrent. ⟨si rele_posat⟩

[res]
    IRI: Vet? ⟨si juga iri⟩
    VET: Aquí. ⟨si juga iri⟩
    VET: Iri? ⟨si juga vet⟩
    IRI: Aquí. ⟨si juga vet⟩

```

## Diàleg `vies` amb Iri

```
COMENÇA A: tria

[tria]
    JUGADORA: BORDA o SEPARADOR?
    ▸ BORDA → borda
    ▸ SEPARADOR → separador

[borda]
    JUGADORA: No.
    JUGADORA: La sentina porta gasoil. La sentina no va al mar. Va al separador.
    ↪ tria

[separador]
    [SO: vies] JUGADORA: Al separador. A poc a poc, però net.
    ⇒ +vies_separador

```

## Diàleg `walkie` amb Vet

```
COMENÇA A: trucada (si escena = 1 i juga iri i NO vet_desperta i silueta_vista i valvula_vista) · taller (si escena = 1 i juga iri i NO vet_desperta i valvula_vista) · sala_maquines (si escena = 1 i juga iri i NO vet_desperta i silueta_vista) · aviat (si escena = 1 i juga iri i NO vet_desperta) · esc1_vet (si escena = 1 i juga vet) · esc1_iri (si escena = 1) · esc2 (si escena = 2) · esc3 (si escena = 3) · fitxa (si escena = 4 i postal_vista i NO sap_pilar) · esc4 (si escena = 4) · mentida (si escena = 5 i juga iri i mentida_triada i NO mentida_dita) · esc5_vet (si escena = 5 i juga vet i NO nota_llegida) · escolten (si escena = 5 i NO pla_fet) · esc5 (si escena = 5) · codi (si escena = 7 i no (ha vist walkie.codi)) · res

[trucada]
    JUGADORA: Canal 9. El de la infermeria. Si hi ha metgessa, hi ha d'haver algú despert.
    VET: Hola? Soc la metgessa nova. Si algú sagna, digues on. Si no, deixa'm dormir.
    IRI: No sagna ningú. S'enfonsa una mica el vaixell.
    VET: Una mica com?
    IRI: Necessito una barra de metall. D'un pam i mig, com a mínim.
    IRI: I no ho diguis pel 6. Si ho sent la Capitana, vindrà a veure-ho, i hi ha coses que no ha de veure.
    VET: Quines coses?
    NARRADOR: En Diu passa entre les cames de l'Iri.
    IRI: Coses.
    IRI: A la cuina hi ha un muntacàrregues. Posa-hi la barra i que baixi al rebost.
    VET: La cuina. I la proa és la punxeguda, oi?
    IRI: La cuina és al fons del menjador. Surt al passadís.
    ⇒ +vet_desperta, esdeveniment protagonista

[aviat]
    JUGADORA: A qui truco, i per demanar què? Primer, mirar com està la sala de màquines.

[taller]
    JUGADORA: Abans de despertar ningú, miro bé el tauler d'eines. Hi hauria de ser la clau de vàlvules.

[sala_maquines]
    JUGADORA: Falta la clau de vàlvules. Abans de trucar, vull saber per a què la volien: la sala de màquines.

[esc1_vet]
    VET: Iri? On era la cuina? ⟨si NO travesser_tret⟩
    IRI: Al fons del menjador. Surt al passadís, primera porta. ⟨si NO travesser_tret⟩
    IRI: I la barra? ⟨si NO travesser_tret⟩
    VET: La busco. A la infermeria tot és de plàstic, menys la llitera. ⟨si NO travesser_tret⟩
    VET: Iri? Tinc una barra. Un travesser de la llitera. ⟨si té travesser (vet)⟩
    IRI: Perfecte. Al muntacàrregues de la cuina, i avall. ⟨si té travesser (vet)⟩
    VET: Iri? Ja l'he enviada avall. T'ha arribat? ⟨si munta_rebost = "travesser"⟩
    IRI: Ara vaig al rebost. ⟨si munta_rebost = "travesser"⟩
    VET: Iri? Ha servit, la barra? ⟨si té travesser (iri) i NO valvula_tancada⟩
    IRI: La tinc. Ara, a la vàlvula. ⟨si té travesser (iri) i NO valvula_tancada⟩
    VET: Iri? Encara ens enfonsem? ⟨si valvula_tancada⟩
    IRI: Ja no entra aigua. Ara falta treure la que hi ha: la bomba. ⟨si valvula_tancada⟩

[esc1_iri]
    IRI: Vet?
    VET: Encara la busco. No em desesperis. ⟨si NO travesser_tret⟩
    VET: La tinc. Ara la poso al muntacàrregues de la cuina. ⟨si té travesser (vet)⟩
    VET: Ja ha baixat. Al rebost, oi? ⟨si munta_rebost = "travesser"⟩
    VET: Ja la tens? Doncs a la vàlvula, que l'aigua no espera. ⟨si té travesser (iri) i NO valvula_tancada⟩
    VET: Tot bé, allà baix? ⟨si valvula_tancada⟩
    IRI: Vàlvula tancada. Ara, que la bomba tregui l'aigua. ⟨si valvula_tancada⟩

[esc2]
    VET: Iri?
    IRI: La Juana ja ha aparegut. Bé. ⟨si juana_explica⟩
    IRI: Fes les revisions. Necessito saber qui menteix. ⟨si no (revisio_capitana i revisions ≥ 4)⟩
    IRI: La Capitana també. Sobretot la Capitana: és qui decideix on anem. ⟨si no (revisio_capitana i revisions ≥ 4) i NO revisio_capitana⟩
    IRI: Ja en portes alguna. Les fitxes són a la infermeria: que hi passin tots. ⟨si no (revisio_capitana i revisions ≥ 4) i revisio_capitana⟩
    IRI: I la Juana no ha vingut a esmorzar. No és normal. ⟨si (revisio_capitana i revisions ≥ 4) i NO juana_explica⟩
    IRI: Al laboratori no hi és. En Tomàs la coneix més que ningú. ⟨si (revisio_capitana i revisions ≥ 4) i NO juana_explica i NO sap_raco⟩
    VET: En Tomàs diu que, quan la Juana vol estar sola, va on hi ha sol i no hi ha gent. ⟨si sap_raco i NO juana_explica⟩
    IRI: Sol i ningú? Això és proa. Allà no hi passa ni el Marcel. ⟨si sap_raco i NO juana_explica⟩

[esc3]
    IRI: Vet. Porta'm en Bastida a la infermeria. Mentre hi sigui, la ràdio és meva. ⟨si juga iri i (NO sync_radio i NO radio_feta)⟩
    VET: La seva revisió. Cinc minuts, Ernest. És obligatòria. ⟨si juga iri i (NO sync_radio i NO radio_feta)⟩
    IRI: Ja hi soc. Entretén-lo. ⟨si juga iri i sync_radio i NO panell_obert i NO radio_feta⟩
    VET: L'entretinc. Tu, de pressa. ⟨si juga iri i sync_radio i NO panell_obert i NO radio_feta⟩
    IRI: Panell obert. Primer, fora el tram tallat. ⟨si juga iri i (panell_obert i NO tram_tret)⟩
    IRI: Em falta cable apantallat, i un connector. Al pallol n'hi ha d'haver. ⟨si juga iri i (tram_tret i no té cable_nou (iri) i empalmat < 2)⟩
    IRI: Tinc el cable. Pelar, crimpar. I l'altra punta. ⟨si juga iri i (té cable_nou (iri) i empalmat < 2)⟩
    IRI: Empalmat. A veure si parla. ⟨si juga iri i (empalmat ≥ 2 i NO radio_feta)⟩
    VET: Mm-hm. ⟨si juga iri i ((panell_obert i NO tram_tret) o (tram_tret i no té cable_nou (iri) i empalmat < 2) o (té cable_nou (iri) i empalmat < 2) o (empalmat ≥ 2 i NO radio_feta))⟩
    IRI: Ara, a tancar el panell. Que sembli que aquí no hi ha entrat ningú. ⟨si juga iri i radio_feta⟩
    VET: Iri? Ja ets a la ràdio? ⟨si juga vet i (NO sync_radio i NO radio_feta)⟩
    IRI: Hi vaig. Tu, en Bastida a la infermeria. Que no pugi. ⟨si juga vet i (NO sync_radio i NO radio_feta)⟩
    NARRADOR: La Vet no pot parlar: té en Bastida davant. ⟨si juga vet i sync_radio i NO radio_feta⟩
    NARRADOR: La feina de la Vet és que no s'aixequi. Del temporal, en Bastida en parlaria hores. ⟨si juga vet i sync_radio i NO radio_feta⟩
    VET: Iri? Ja tenim ràdio? ⟨si juga vet i radio_feta⟩
    IRI: Tenim ràdio. Ara tanco el panell, que no es noti. ⟨si juga vet i radio_feta⟩

[fitxa]
    IRI: Vet. Tens les fitxes de les revisions?
    VET: Les tinc. Són confidencials.
    IRI: La de la Juana. El contacte d'emergència.
    NARRADOR: Un silenci. Paper.
    VET: «Contacte d'emergència: Pilar Solà Puig, 65 anys. Parentiu: mare.»
    IRI: Pilar. Pili. Seixanta-cinc.
    VET: No t'ho he dit. Que consti.
    ⇒ +sap_pilar

[esc4]
    IRI: Vet?
    VET: Aquí. Tinc les fitxes de tothom i res a fer. Quina vida. ⟨si NO sap_pilar⟩
    VET: La Juana em va dir que la contrasenya és el nom de la seva mare. Busca alguna cosa de la mare entre les seves coses. ⟨si NO postal_vista i NO portatil_obert⟩
    VET: Prova Pilar. I no ho diguis gaire fort. ⟨si sap_pilar i NO portatil_obert⟩
    IRI: El portàtil està obert. Les dades, les vull a terra. ⟨si portatil_obert i NO satellit_provat⟩
    VET: El pont té satèl·lit, no? ⟨si portatil_obert i NO satellit_provat⟩
    IRI: El satèl·lit, sense senyal. ⟨si satellit_provat⟩
    VET: Però primer, la Juana. Sala de bombes, has dit? Ves-hi. I si hi és, digues-li que la metgessa diu que ha de sopar. ⟨si portatil_obert⟩

[escolten]
    JUGADORA: No. Si ens escolten, també escolten això.
    IRI: Si li he de dir res, en paper. Per un camí sense orelles. ⟨si juga iri i NO nota_enviada⟩
    IRI: El paper ja és amunt. Ara, esperar la resposta a la safata del rebost. ⟨si juga iri i nota_enviada i munta_rebost ≠ "nota_vet"⟩
    IRI: Ha baixat alguna cosa. Al rebost. ⟨si juga iri i munta_rebost = "nota_vet"⟩
    VET: La resposta, pel mateix camí que ha vingut el paper: el muntacàrregues. ⟨si juga vet⟩

[esc5_vet]
    VET: Iri?
    NARRADOR: Res. Només estàtica. L'Iri no contesta.
    NARRADOR: Però a la cuina, el muntacàrregues ha fet clec. Ha pujat alguna cosa. ⟨si munta_cuina = "nota_iri"⟩

[mentida]
    IRI: Vet. Una cosa.
    IRI: La Juana va deixar la mostra a la cambra freda de la cuina, darrere les postres. Diu que allà sempre hi fa fred.
    VET: Rebut. Darrere les postres.
    NARRADOR: Ara, a esperar qui té gana.
    ⇒ +mentida_dita

[esc5]
    JUGADORA: Pel walkie, res. Ni el temps que fa.
    IRI: Primer, en paper: quina mentida diem. Des del rebost. ⟨si juga iri i NO mentida_triada⟩
    VET: Ara, a esperar qui té gana. Des d'un lloc on no em vegin. ⟨si juga vet i mentida_dita i NO vet_amagada⟩
    VET: I si ara sona el walkie, em troben dins l'armari. ⟨si juga vet i vet_amagada⟩

[res]
    JUGADORA: Flam. ⟨si escena = 7 i ha vist walkie.codi⟩
    VET: Flam. ⟨si (escena = 7 i ha vist walkie.codi) i juga iri⟩
    IRI: Flam. ⟨si (escena = 7 i ha vist walkie.codi) i juga vet⟩
    JUGADORA: Pel walkie no. Ens escolten. ⟨si no (escena = 7 i ha vist walkie.codi)⟩
    JUGADORA: Pel tub de veu: hi ha boca al pont, a la sala de màquines, a la cuina i a la infermeria. ⟨si escena ≥ 6⟩

[codi]
    IRI: Vet. Codi flam. Repeteixo: codi flam.
    VET: No tenim cap codi flam.
    IRI: Ara sí. Vol dir «tot va bé». Si algú escolta, que s'hi entretingui.
    VET: I «gelatina»?
    IRI: Vol dir «corre».
    VET: A bord no hi ha gelatina.
    IRI: Doncs no correrem.

```

## Pistes

```
iri_falca — quan escena = 1 i juga iri i NO falca_desencallada i no té maceta (iri) · fins que falca_desencallada o té maceta (iri)
    1. La porta de màquines s'encalla des de l'agost. La falca de baix. I tu saps com es desencalla.
    2. La falca de baix s'encalla. Al camarot hi ha la maceta de goma.
    3. Agafa la maceta del camarot i fes-la servir amb la porta de la sala de màquines.
iri_maceta — quan escena = 1 i juga iri i NO falca_desencallada i té maceta (iri) · fins que falca_desencallada
    1. Tens la maceta. La falca de baix, un cop i va.
    2. La porta de la sala de màquines és al passadís de baix.
    3. Fes servir la maceta amb la porta de la sala de màquines.
iri_diu — quan escena = 1 i juga iri i NO valvula_vista i NO brida_vista i falca_desencallada · fins que valvula_vista o brida_vista
    1. En Diu ja és aquí, tan tranquil. Però a la sala de màquines hi ha aigua. D'on ve?
    2. Mira què passa a la sala de màquines: la vàlvula de presa de mar, el quadre de la bomba.
    3. Mira la vàlvula de presa de mar.
iri_mira_valvula — quan escena = 1 i juga iri i brida_vista i NO valvula_vista · fins que valvula_vista
    1. Per on entra l'aigua?
    2. Mira la vàlvula de presa de mar.
    3. Mira la vàlvula de presa de mar, a la sala de màquines.
iri_brida — quan escena = 1 i juga iri i brida_vista i NO brida_tallada · fins que brida_tallada
    1. Què em diries tu, bomba? Per què no arrenques?
    2. L'interruptor està lligat amb una brida. Cal tallar-la.
    3. Agafa la cisalla del taller i fes-la servir amb el quadre de la bomba.
iri_quadre — quan escena = 1 i juga iri i valvula_vista i NO brida_vista · fins que brida_vista o brida_tallada
    1. Què em diries tu, sentina? Algú ha callat l'alarma. I la bomba?
    2. Mira el quadre de la bomba de sentina.
    3. Mira el quadre de la bomba, a la sala de màquines.
iri_palanca — quan escena = 1 i juga iri i valvula_vista i NO silueta_vista i NO valvula_tancada · fins que silueta_vista o valvula_tancada
    1. Sense volant, la vàlvula necessita una palanca. El taller és ple d'eines.
    2. Mira el tauler d'eines del taller.
    3. Ves al taller (des de la sala de màquines) i mira el tauler d'eines.
iri_trucada — quan escena = 1 i juga iri i silueta_vista i NO vet_desperta · fins que vet_desperta
    1. Algú ha d'estar despert. Algú que no sigui la Capitana.
    2. El walkie. El canal 9 és el de la infermeria: hi ha una metgessa nova.
    3. Parla amb el walkie (és a l'inventari) per trucar a la metgessa.
vet_travesser — quan escena = 1 i juga vet i vet_desperta i NO travesser_tret · fins que travesser_tret
    1. Símptomes: una maquinista que necessita una barra de metall. Tractament: buscar acer.
    2. A la infermeria tot és de plàstic. Menys la llitera de rescat.
    3. Agafa la llitera de rescat: en trauràs un travesser.
vet_munta — quan escena = 1 i juga vet i té travesser (vet) i NO valvula_tancada i no (a cuina) · fins que no té travesser (vet) o valvula_tancada
    1. Diagnòstic: s'ha d'enviar avall. La maquinista ha dit «muntacàrregues».
    2. El muntacàrregues és a la cuina: passadís, menjador, cuina.
    3. Ves a la cuina i fes servir el travesser amb el muntacàrregues.
vet_munta_cuina — quan escena = 1 i juga vet i té travesser (vet) i NO valvula_tancada i a cuina · fins que no té travesser (vet) o valvula_tancada
    1. Diagnòstic: s'ha d'enviar avall. I el muntacàrregues és aquí mateix.
    2. Fes servir el travesser amb el muntacàrregues.
    3. Fes servir el travesser amb el muntacàrregues de la cuina.
iri_rebost — quan escena = 1 i juga iri i munta_rebost = "travesser" · fins que munta_rebost ≠ "travesser"
    1. Ha baixat alguna cosa pel muntacàrregues.
    2. El muntacàrregues para al rebost, porta amb porta amb la sala de màquines.
    3. Ves al rebost i agafa el travesser de la safata.
iri_valvula — quan escena = 1 i juga iri i té travesser (iri) i NO valvula_tancada · fins que valvula_tancada
    1. Un pam i mig d'acer. Una vàlvula sense volant.
    2. Fes servir el travesser amb la vàlvula de presa de mar.
    3. Fes servir el travesser amb la vàlvula de presa de mar.
iri_vies — quan escena = 1 i juga iri i valvula_tancada i brida_tallada i NO vies_separador · fins que vies_separador
    1. La bomba ha d'escopir l'aigua a algun lloc.
    2. La vàlvula de tres vies: borda o separador.
    3. Fes servir la vàlvula de tres vies i tria SEPARADOR.
iri_bomba — quan escena = 1 i juga iri i valvula_tancada i brida_tallada i vies_separador i NO bomba_engegada · fins que bomba_engegada
    1. Tot a punt. Que treballi la bomba.
    2. Engega la bomba des del quadre.
    3. Fes servir el quadre de la bomba.
iri_espera — quan escena = 1 i juga iri i vet_desperta i NO valvula_tancada i no té travesser (iri) i munta_rebost ≠ "travesser" · fins que valvula_tancada
    1. La metgessa busca la barra. Ara és cosa seva.
    2. Canvia a la Vet: ella ha de trobar la barra i enviar-la pel muntacàrregues.
    3. Amb el botó «Canvia», passa a la Vet. A la infermeria hi ha la llitera de rescat.
vet_revisions — quan escena = 2 i (NO revisio_capitana o revisions < 4) i pacient = "" · fins que revisio_capitana i revisions ≥ 4
    1. Diagnòstic: una tripulació sense revisió mèdica. Tractament: revisions.
    2. A la infermeria hi ha les fitxes. Des d'allà, tothom es crida pel canal 6.
    3. Fes servir les fitxes de la infermeria i crida tothom: la Capitana, en Tomàs, la Nadia i el Marcel.
vet_pacient — quan escena = 2 i pacient ≠ "" · fins que pacient = ""
    1. Tinc un pacient a la consulta. Escoltar i mirar: el que diu i el que no quadra.
    2. Parla amb el pacient. I mira'l: sempre hi ha alguna cosa que no quadra.
    3. Parla amb el pacient i, quan acabis, digues-li que ja està.
vet_juana — quan escena = 2 i NO juana_explica i NO sap_raco · fins que sap_raco o juana_explica
    1. Símptomes: una biòloga que no ve a esmorzar.
    2. Al laboratori no hi és. En Tomàs la coneix bé.
    3. Parla amb en Tomàs, a la cuina (o a la seva revisió), i pregunta-li per la Juana.
vet_proa — quan escena = 2 i NO juana_explica i sap_raco · fins que juana_explica
    1. On hi ha sol i no hi ha gent?
    2. A proa, sota la balsa salvavides, no hi passa ningú.
    3. Ves a la coberta de proa i parla amb la Juana. Explica-li la vàlvula.
vet_bastida — quan (escena = 3 i NO radio_feta) i juga vet i (NO eina_temporal o NO eina_tensio) · fins que radio_feta
    1. Diagnòstic: un contramestre impacient. Tractament: conversa.
    2. Parla amb en Bastida: el temporal el distreu tres torns; la tensió, dos.
    3. Fes-li explicar el temporal. Quan l'Iri hagi d'empalmar, pren-li la tensió.
iri_panell — quan (escena = 3 i NO radio_feta) i juga iri i NO panell_obert · fins que panell_obert
    1. Què em diries tu, ràdio? Ensenya'm el cable.
    2. Obre el panell. Fa soroll: millor si la Vet té en Bastida distret.
    3. Quan en Bastida estigui distret (amb la Vet), obre el panell.
iri_tram — quan (escena = 3 i NO radio_feta) i juga iri i panell_obert i NO tram_tret · fins que tram_tret
    1. El tram tallat, fora.
    2. Agafa el cable tallat del panell.
    3. Agafa el cable tallat del panell.
iri_cable — quan (escena = 3 i NO radio_feta) i juga iri i tram_tret i no té cable_nou (iri) i empalmat < 2 i no (a pallol) · fins que té cable_nou (iri) o empalmat ≥ 2
    1. Cable apantallat i un connector. Al pallol n'hi ha.
    2. El pallol és al passadís de baix.
    3. Baixa al pallol i agafa cable dels prestatges.
iri_cable_pallol — quan (escena = 3 i NO radio_feta) i juga iri i tram_tret i no té cable_nou (iri) i empalmat < 2 i a pallol · fins que té cable_nou (iri) o empalmat ≥ 2
    1. Cable apantallat i un connector. Aquí n'hi ha d'haver.
    2. Mira els prestatges.
    3. Agafa cable dels prestatges.
iri_empalmar — quan (escena = 3 i NO radio_feta) i juga iri i té cable_nou (iri) i empalmat = 0 · fins que empalmat ≥ 1
    1. Pelar i crimpar.
    2. Fes servir el cable nou amb el panell obert.
    3. Fes servir el cable nou amb el panell obert: primer el peles, després hi crimpes el connector.
iri_crimpar — quan (escena = 3 i NO radio_feta) i juga iri i té cable_nou (iri) i empalmat = 1 · fins que empalmat ≥ 2
    1. Pelat. Ara, el connector.
    2. Torna a fer servir el cable nou amb el panell.
    3. Fes servir una altra vegada el cable nou amb el panell obert, per crimpar-hi el connector.
iri_provar — quan (escena = 3 i NO radio_feta) i juga iri i empalmat ≥ 2 · fins que radio_feta
    1. A veure si parla.
    2. Prova la ràdio.
    3. Fes servir la ràdio.
iri_tancar — quan escena = 3 i juga iri i rut_parlat · fins que escena ≥ 4
    1. Com si no hagués passat res.
    2. Tanca la tapa del panell de la ràdio, a la paret, a la dreta de la ràdio.
    3. Toca la tapa del panell d'ANTENA / PERILL, a la paret a la dreta de la ràdio, fins que la tanquis.
iri_postal — quan escena = 4 i NO portatil_obert i NO postal_vista · fins que postal_vista
    1. La Juana va dir a la Vet que la contrasenya és el nom de la seva mare. Què hi ha al laboratori que en parli?
    2. Els llibres de la Juana. Algú hi guarda records.
    3. Mira el llibre de peixos del laboratori.
iri_fitxa — quan escena = 4 i postal_vista i NO sap_pilar · fins que sap_pilar
    1. «Pili 65». Pili de què? La Vet té les fitxes mèdiques de tothom.
    2. Pregunta a la Vet pel walkie: el contacte d'emergència de la Juana.
    3. Parla amb el walkie.
iri_obrir — quan escena = 4 i sap_pilar i NO portatil_obert · fins que portatil_obert
    1. «El nom de la meva mare.» El nom: ni el diminutiu ni l'edat.
    2. Fes servir el portàtil del laboratori i escriu el nom de la mare de la Juana, sencer.
    3. Fes servir el portàtil del laboratori i escriu Pilar.
iri_bombes — quan escena = 4 i portatil_obert i no (a sala_bombes) · fins que escena ≥ 5
    1. La sala de bombes. «Allà no hi ve ningú.»
    2. L'escotilla de la sala de bombes és al passadís de baix.
    3. Baixa a la sala de bombes, per l'escotilla del passadís de baix, i mira-hi bé.
iri_bombes_dins — quan escena = 4 i portatil_obert i a sala_bombes · fins que escena ≥ 5
    1. La Juana no hi és. Però hi ha deixat coses.
    2. Què fa un llibre a terra?
    3. Mira el llibre que hi ha a terra de la sala de bombes.
iri_nota — quan escena = 5 i juga iri i NO nota_enviada · fins que nota_enviada
    1. Què em diries tu, muntacàrregues? Tu no xerres, i puges fins a la cuina.
    2. El muntacàrregues: del rebost, puja a la cuina, on és la Vet.
    3. Al rebost, fes servir la llibreta amb el muntacàrregues.
vet_espera — quan escena = 5 i juga vet i NO nota_llegida i munta_cuina ≠ "nota_iri" · fins que nota_llegida
    1. Torn de cuina. Si l'Iri té res a dir, ja ho dirà.
    2. La que s'ha de moure és l'Iri.
    3. Canvia a l'Iri.
vet_nota — quan escena = 5 i juga vet i munta_cuina = "nota_iri" · fins que nota_llegida
    1. Hi ha alguna cosa a la safata del muntacàrregues de la cuina.
    2. Agafa el que hi ha a la safata.
    3. A la cuina, agafa el que hi ha a la safata del muntacàrregues.
iri_resposta — quan escena = 5 i juga iri i munta_rebost = "nota_vet" · fins que pla_fet
    1. Ha baixat la resposta.
    2. Agafa el paper de la safata del rebost.
    3. Ves al rebost i agafa el paper de la safata.
iri_mentida — quan escena = 5 i juga iri i pla_fet i NO mentida_triada · fins que mentida_triada
    1. Una mentida que s'empassin. Primer, per paper.
    2. Al rebost, fes servir la llibreta amb el muntacàrregues i proposa una mentida creïble.
    3. Proposa la de la Juana, que la va deixar a la cambra freda, darrere les postres.
iri_dir — quan escena = 5 i juga iri i mentida_triada i NO mentida_dita · fins que mentida_dita
    1. Ara, pel walkie. Que ho sentin.
    2. Digues-ho pel walkie.
    3. Parla amb el walkie.
vet_amagar — quan escena = 5 i juga vet i mentida_dita i NO vet_amagada · fins que vet_amagada
    1. Diagnòstic: algú tindrà gana de postres. Tractament: esperar-lo amagada.
    2. L'armari de les olles de la cuina.
    3. Obre l'armari de les olles de la cuina.
vet_nadia — quan escena = 5 i juga vet i vet_amagada i NO nadia_decidida · fins que nadia_decidida
    1. La Nadia. Ara toca decidir.
    2. Parla amb la Nadia.
    3. Parla amb la Nadia.
buscar — quan escena = 6 i juga iri i NO cops_sentits i NO cops_marcel · fins que cops_sentits o cops_marcel
    1. On pot ser la Juana? Algú haurà sentit alguna cosa.
    2. El Marcel és al pallol. I a proa, on no hi passa ningú?
    3. Mira l'escotilla de la caixa de cadenes, a la coberta de proa.
buscar_vet — quan escena = 6 i juga vet i NO cops_sentits i NO cops_marcel · fins que cops_sentits o cops_marcel
    1. On pot ser la Juana? Algú haurà sentit alguna cosa.
    2. La Capitana és a la cabina; en Tomàs, a la cuina; en Bastida, a popa. Pregunta. I el que sàpigues, digues-ho a l'Iri pel tub.
    3. A proa hi ha d'anar l'Iri: a tu, en Bastida et veuria. Canvia a l'Iri i que miri l'escotilla de la caixa de cadenes.
buscar_proa — quan escena = 6 i juga iri i NO cops_sentits i cops_marcel · fins que cops_sentits
    1. El Marcel ha sentit cops a proa aquesta tarda.
    2. A la coberta de proa hi ha l'escotilla de la caixa de cadenes.
    3. Mira l'escotilla de la caixa de cadenes, a la coberta de proa.
buscar_proa_vet — quan escena = 6 i juga vet i NO cops_sentits i cops_marcel · fins que cops_sentits
    1. Símptomes: cops a proa, aquesta tarda. Ho diu el Marcel.
    2. A proa, si en Bastida em veu, sabrà on busquem. Que hi vagi l'Iri: digues-l'hi pel tub.
    3. Canvia a l'Iri: que miri l'escotilla de la caixa de cadenes, a la coberta de proa.
cisalla — quan escena = 6 i juga iri i cops_sentits i no té cisalla (iri) i NO cadenat_tallat · fins que té cisalla (iri) o cadenat_tallat
    1. Un cadenat nou. Per a un cadenat, una cisalla.
    2. La cisalla és al taller.
    3. Agafa la cisalla del taller.
distreure — quan escena = 6 i juga vet i cops_sentits i (escena = 6 i NO bastida_baixa i NO nus_lico) i NO cadenat_tallat · fins que no (escena = 6 i NO bastida_baixa i NO nus_lico) o cadenat_tallat
    1. Si en Bastida sent la cisalla, vindrà. Algú l'ha d'entretenir.
    2. Demana a en Bastida que t'ensenyi el nus Bastida. I si la Nadia treballa per a nosaltres, ella també hi pot fer alguna cosa.
    3. Ves a popa, parla amb en Bastida i demana-li que t'ensenyi el nus.
tallar — quan escena = 6 i juga iri i cops_sentits i té cisalla (iri) i no (escena = 6 i NO bastida_baixa i NO nus_lico) i NO cadenat_tallat · fins que cadenat_tallat
    1. Ara. Ningú no vigila.
    2. Fes servir la cisalla amb l'escotilla de la caixa de cadenes.
    3. Fes servir la cisalla amb l'escotilla de la caixa de cadenes, a proa.
sortir — quan escena = 6 i juana_trobada · fins que escena ≥ 7
    1. La Juana té fred. A la infermeria.
    2. Surt per l'escotilla.
    3. Surt per l'escotilla.
registre — quan escena = 7 i juga vet i NO registre_obert i NO prova_pany i NO clau_donada · fins que prova_pany o registre_obert o clau_donada
    1. Diagnòstic: un dipòsit que ningú no fa servir. On és el registre?
    2. El registre del dipòsit 2 és al rebost, a baix: allà hi va l'Iri.
    3. Canvia a l'Iri i que miri el registre del dipòsit 2, al rebost.
clau — quan escena = 7 i juga vet i NO registre_obert i NO tomas_ofes i no té clau_tomas (vet) · fins que tomas_ofes o registre_obert
    1. Una clau que no té ningú. O que algú té i no sap què obre.
    2. El cuiner d'abans va deixar coses a la cuina. Potser en Tomàs en sap alguna cosa. I l'Iri sap treure frontisses.
    3. Parla amb en Tomàs, a la cuina, i demana-li la clau del dipòsit 2.
entrepa — quan escena = 7 i juga vet i tomas_ofes i NO clau_donada i NO registre_obert · fins que clau_donada o registre_obert
    1. En Tomàs està ofès per un entrepà robat. Qui se'l va menjar?
    2. La Juana: «Ha estat el millor dia de la campanya.»
    3. Explica a en Tomàs que la Juana es va menjar l'entrepà.
obrir — quan escena = 7 i juga iri i té clau_tomas (iri) i NO registre_obert · fins que registre_obert
    1. La clau antiga.
    2. La clau va al registre del dipòsit 2, al rebost.
    3. Fes servir la clau amb el registre del rebost.
obrir_vet — quan escena = 7 i juga vet i té clau_tomas (vet) i NO registre_obert · fins que registre_obert
    1. La clau antiga.
    2. La clau va al registre del dipòsit 2, al rebost, on és l'Iri. Pel muntacàrregues de la cuina, baixa al rebost.
    3. A la cuina, fes servir la clau amb el muntacàrregues: l'Iri l'agafarà de la safata del rebost.
frontisses — quan escena = 7 i juga iri i NO registre_obert i no té clau_tubs (iri) i NO frontissa1 · fins que registre_obert o té clau_tubs (iri) o frontissa1
    1. Què em diries tu, frontissa?
    2. La clau de tubs és al taller. Les frontisses del registre, al rebost.
    3. Agafa la clau de tubs del taller i fes-la servir amb el registre del rebost, dues vegades.
frontisses_clau — quan escena = 7 i juga iri i NO registre_obert i té clau_tubs (iri) i NO frontissa1 · fins que registre_obert o frontissa1
    1. Una clau de tubs i dues frontisses.
    2. Les frontisses del registre del dipòsit 2, al rebost.
    3. Fes servir la clau de tubs amb el registre del rebost, dues vegades: una per frontissa.
frontissa2 — quan escena = 7 i juga iri i NO registre_obert i frontissa1 · fins que registre_obert
    1. Una frontissa fora. En queda una.
    2. Torna a fer servir la clau de tubs amb el registre.
    3. Fes servir la clau de tubs amb el registre del rebost un altre cop.
mostra — quan escena = 7 i juga iri i registre_obert i NO mostra_trobada · fins que mostra_trobada
    1. «On ningú no beu.»
    2. Entra al dipòsit 2 i obre la carcassa del filtre.
    3. Entra al dipòsit 2 (pel registre del rebost) i obre la carcassa del filtre.
mostra_vet — quan escena = 7 i juga vet i registre_obert i NO mostra_trobada · fins que mostra_trobada
    1. Diagnòstic: el registre és obert. La mostra, a l'altra banda.
    2. El dipòsit 2 és cosa de l'Iri. Ella hi pot entrar.
    3. Canvia a l'Iri: que entri al dipòsit 2 i obri la carcassa del filtre.
tornar — quan escena = 7 i juga iri i mostra_trobada i no té mostra7 (vet) i munta_cuina ≠ "mostra7" · fins que escena ≥ 8
    1. La Juana l'ha de veure.
    2. La Mostra 7 ha d'arribar a la infermeria, i a la infermeria no hi entro. Pel muntacàrregues, a la Vet.
    3. Al rebost, fes servir la Mostra 7 amb el muntacàrregues: puja a la cuina, i la Vet la portarà a la infermeria.
tornar_vet — quan escena = 7 i juga vet i té mostra7 (vet) · fins que escena ≥ 8
    1. La Juana l'ha de veure.
    2. Porta la Mostra 7 a la infermeria.
    3. Porta la Mostra 7 a la infermeria i ensenya-la a la Juana.
reunio — quan escena = 8 i juga vet i NO reunio_comencada · fins que reunio_comencada
    1. Diagnòstic: algú menteix. Tractament: dir-ho davant de tothom.
    2. La reunió, la convoca la Capitana. A la seva cabina.
    3. Parla amb la Capitana i demana-li que reuneixi tothom. (Abans, si vols, ensenya-li qui paga el gasoil.)
imprimir — quan escena = 8 i juga iri i NO registre_impres i NO aliada_capitana i NO reunio_comencada i té usb (iri) · fins que registre_impres o reunio_comencada
    1. La Capitana no sap qui paga el gasoil. L'USB, sí.
    2. Imprimeix la pàgina del registre a la impressora del pont.
    3. Fes servir l'USB amb la impressora del pont i envia la pàgina a la Vet pel muntacàrregues.
enviar_registre — quan escena = 8 i juga iri i té registre (iri) i NO aliada_capitana i NO reunio_comencada · fins que no té registre (iri) o reunio_comencada
    1. La pàgina ha d'arribar a la Vet.
    2. Pel muntacàrregues del pont, cap a la cuina.
    3. Fes servir la pàgina amb el muntacàrregues del pont.
capitana — quan escena = 8 i juga vet i té registre (vet) i NO aliada_capitana i NO reunio_comencada · fins que aliada_capitana o reunio_comencada
    1. Blau Net i Skarn. Que ho vegi la Capitana.
    2. Fes servir la pàgina del registre amb el contracte de la cabina de la Capitana.
    3. Ves a la cabina de la Capitana i fes servir la pàgina amb el contracte.
registre_safata — quan escena = 8 i juga vet i munta_cuina = "registre" · fins que munta_cuina ≠ "registre"
    1. Ha arribat una cosa a la cuina.
    2. Agafa la pàgina de la safata de la cuina.
    3. Ves a la cuina i agafa la pàgina de la safata.
qui — quan escena = 8 i juga vet i reunio_comencada i NO bastida_confessa · fins que bastida_confessa
    1. Qui, i per què ho sabem. Tres proves.
    2. Pensa en qui estava despert, qui fuma pipa, qui fa el nus amb una volta de més.
    3. Acusa en Bastida i tria tres proves del quadern: el nus amb la volta de més, el tall a la mà i la pipa.
pal — quan (escena = 9 i NO enviat) i juga iri i NO antena_ok i no (a pal) · fins que antena_ok
    1. Ja no hi ha més remei: l'antena del pal.
    2. Puja al pal per l'escala del pont.
    3. Puja al pal per l'escala del pont i fes servir l'antena.
pal_antena — quan (escena = 9 i NO enviat) i juga iri i NO antena_ok i a pal · fins que antena_ok
    1. L'antena ha d'apuntar al satèl·lit.
    2. Fes servir l'antena.
    3. Fes servir l'antena fins que apunti al satèl·lit (desbloquejar-la, si cal, i girar-la).
terminal — quan (escena = 9 i NO enviat) i juga iri i antena_ok i (rele_posat o sai > 0) · fins que enviat
    1. Ara, avall. Paquet a paquet.
    2. Fes servir el terminal del pont. La bateria (el SAI) aguanta dos torns; després cal el generador.
    3. Fes servir el terminal del pont fins a enviar els tres paquets.
sense_corrent — quan (escena = 9 i NO enviat) i juga iri i NO rele_posat i sai ≤ 0 · fins que rele_posat o enviat
    1. Sense corrent. El relé el té en Bastida.
    2. És cosa de la Vet: ha de convèncer en Bastida.
    3. Canvia a la Vet i parla amb en Bastida.
vet_rele — quan (escena = 9 i NO enviat) i juga vet i NO rele_posat · fins que rele_posat
    1. Diagnòstic: un home amb un relé i un dubte. Tractament: parlar-hi.
    2. Parla amb en Bastida. Recorda-li el que t'ha dit ell mateix, i el que perd.
    3. Digues-li la veritat: si surt, és un testimoni; si no, l'únic culpable. I quan l'Iri sigui dalt del pal, recorda-l'hi.
vet_espera9 — quan (escena = 9 i NO enviat) i juga vet i rele_posat · fins que enviat
    1. Ja té corrent. Ara és cosa de l'Iri.
    2. Canvia a l'Iri.
    3. Canvia a l'Iri: ha de fer servir el terminal del pont.
clau_safata — quan escena = 7 i juga iri i munta_rebost = "clau_tomas" · fins que munta_rebost ≠ "clau_tomas"
    1. Ha baixat la clau.
    2. La clau d'en Tomàs és a la safata del rebost.
    3. Ves al rebost i agafa la clau de la safata.
mostra_safata — quan escena = 7 i juga vet i munta_cuina = "mostra7" · fins que munta_cuina ≠ "mostra7"
    1. Ha pujat la Mostra 7.
    2. Agafa-la de la safata de la cuina.
    3. Agafa la Mostra 7 de la safata de la cuina i porta-la a la infermeria.
usb_amunt — quan escena = 8 i juga vet i té usb (vet) i NO registre_impres i NO aliada_capitana i NO reunio_comencada · fins que no té usb (vet) o registre_impres o aliada_capitana o reunio_comencada
    1. La Capitana no sap qui paga el gasoil. L'USB, sí. Però la impressora és al pont, amb l'Iri.
    2. Envia l'USB a l'Iri pel muntacàrregues: de la cuina, puja al pont si ella hi és.
    3. A la cuina, fes servir l'USB amb el muntacàrregues. Després, amb l'Iri, agafa'l i imprimeix el registre.
usb_safata — quan escena = 8 i juga iri i munta_pont = "usb" · fins que munta_pont ≠ "usb"
    1. Ha pujat l'USB.
    2. Agafa l'USB de la safata del pont.
    3. Agafa l'USB de la safata del pont i fes-lo servir amb la impressora.
```

## Finals

```
final_primera «Primera plana» — quan enviat i (aliada_nadia i aliats ≥ 3)
    NARRADOR: Galway. Dues setmanes després, a primera hora del matí.
    NARRADOR: A la terrassa d'un bar del port. Davant, al moll, l'Arenga espera que li posin un volant nou a la vàlvula de popa.
    IRI: Ho hem aconseguit?
    VET: La Mostra 7 és en un laboratori de Dublín. Ningú de Valmark no l'ha tocada. I diu el que deia la Juana.
    IRI: I Skarn?
    VET: Skarn diu que «investigarà». Que és el que diuen sempre.
    LA TELE: ...una ONG denuncia abocaments a l'Atlàntic Nord. Fonts properes a la investigació qüestionen les finances de l'ONG... ⟨si no (aliada_nadia i aliats ≥ 3)⟩
    NARRADOR: La notícia, a la pàgina 4. ⟨si no (aliada_nadia i aliats ≥ 3)⟩
    VET: Les dades són al blog de la Juana. Tres mil visites. ⟨si no (aliada_nadia i aliats ≥ 3)⟩
    VET: I Skarn continua abocant «dins la legalitat». ⟨si no (aliada_nadia i aliats ≥ 3)⟩
    LA TELE: ...la periodista Nadia Vidal, que viatjava a bord pagada per la mateixa fundació que... ⟨si aliada_nadia i aliats ≥ 3⟩
    LA TELE: ...en una gravació, la directora de comunicació de Skarn, Hedda Lind, diu que el fang és «un inconvenient tècnic»... ⟨si aliada_nadia i aliats ≥ 3⟩
    LA TELE: ...i el govern de Valmark ha suspès el permís d'abocament mentre duri la investigació... ⟨si aliada_nadia i aliats ≥ 3⟩
    NARRADOR: L'article de la Nadia és a la primera plana del North Atlantic Herald, amb la seva firma. Valmark «ajorna» la Cimera dels Oceans. ⟨si aliada_nadia i aliats ≥ 3⟩
    NARRADOR: El director de Skarn dimiteix «per passar més temps amb la seva família». ⟨si aliada_nadia i aliats ≥ 3⟩
    NARRADOR: La Capitana torna la donació de Blau Net en una roda de premsa. ⟨si (aliada_nadia i aliats ≥ 3) i aliada_capitana⟩
    IRI: I el Punt 7?
    VET: La Juana diu que, si deixen d'abocar avui, les arengades trigaran vint anys a tornar.
    NARRADOR: Una pausa.
    VET: Si tornen.
    IRI: Doncs que deixin d'abocar avui.
    NADIA VIDAL: M'han ofert feina fixa. És la primera vegada que algú em paga per dir la veritat. ⟨si aliada_nadia⟩
    CAPITANA ROIG: A l'abril no tindrem gasoil. Però el que tinguem serà net. ⟨si aliada_capitana⟩
    MARCEL: En Diu? Ningú no l'ha vist mai. Jo tampoc. ⟨si aliat_marcel⟩
    TOMÀS: Ha vingut la Juana a demanar-me la recepta de l'entrepà. M'he emocionat. ⟨si tomas_content⟩
    VET: I l'Ernest ha declarat. Ha tornat a casa d'un cosí, a Osca, a esperar el judici. ⟨si aliat_bastida⟩
    VET: Diu que és el primer lloc en trenta-cinc anys des d'on no veu el mar. Diu que s'ho mereix. ⟨si aliat_bastida⟩
    IRI: Osca? ⟨si aliat_bastida⟩
    VET: Osca. ⟨si aliat_bastida⟩
    NARRADOR: Una pausa. ⟨si aliat_bastida⟩
    IRI: Podríem anar a veure'l. ⟨si aliat_bastida⟩
    VET: Sí. Però el cafè el pagues tu. ⟨si aliat_bastida⟩
    VET: L'Ernest no ha dit res. Skarn diu que no el coneix. L'han deixat anar fins al judici, i ningú no sap on para. ⟨si NO aliat_bastida⟩
    IRI: Ell sí que ho sap. ⟨si NO aliat_bastida⟩
    NARRADOR: Una pausa. ⟨si NO aliat_bastida⟩
    IRI: Mira el mar des d'algun lloc. Segur. ⟨si NO aliat_bastida⟩
    NARRADOR: Una pausa.
    VET: Tres-cents mil euros. Tu què n'hauries fet?
    IRI: Res. No els hauria agafat.
    NARRADOR: Una pausa.
    IRI: Què em compro, amb tres-cents mil euros? Un altre mar?
    VET: Jo tampoc. Fa tres setmanes no sabia on era la proa. Ara em llevo de nit per veure sortir el sol per la popa.
    IRI: Per la proa. Anàvem cap a l'est.
    VET: Per la punxeguda. Això.
    NARRADOR: Una pausa.
    VET: Això no t'ho paga ningú.
    IRI: La Capitana diu que a l'abril tornem a sortir. Que no tindrem gasoil, però que potser tindrem metgessa.
    NARRADOR: Una pausa.
    IRI: I que el cap de màquines es jubila. Que la plaça és meva.
    VET: Felicitats, cap.
    VET: I tindreu metgessa.
    [SO: mossegada] NARRADOR: En Diu salta damunt la taula i mossega el cable de la tele. La pantalla s'apaga a mitja notícia.
      ⇒ +tele_apagada
    IRI: Diu!
    VET: Deixa'l. Ja hem vist prou notícies.
    NARRADOR: Les dues es queden mirant la badia, sense dir res. El sol surt per darrere seu, per damunt de la ciutat, i encén primer el pal de l'Arenga i després l'aigua.
    Ni un ou. Encara.
final_testimonis «Testimonis» — quan enviat i aliats ≥ 1
    NARRADOR: Galway. Dues setmanes després, a primera hora del matí.
    NARRADOR: A la terrassa d'un bar del port. Davant, al moll, l'Arenga espera que li posin un volant nou a la vàlvula de popa.
    IRI: Ho hem aconseguit?
    VET: La Mostra 7 és en un laboratori de Dublín. Ningú de Valmark no l'ha tocada. I diu el que deia la Juana.
    IRI: I Skarn?
    VET: Skarn diu que «investigarà». Que és el que diuen sempre.
    LA TELE: ...una ONG denuncia abocaments a l'Atlàntic Nord. Fonts properes a la investigació qüestionen les finances de l'ONG... ⟨si no (aliada_nadia i aliats ≥ 3)⟩
    NARRADOR: La notícia, a la pàgina 4. ⟨si no (aliada_nadia i aliats ≥ 3)⟩
    VET: Les dades són al blog de la Juana. Tres mil visites. ⟨si no (aliada_nadia i aliats ≥ 3)⟩
    VET: I Skarn continua abocant «dins la legalitat». ⟨si no (aliada_nadia i aliats ≥ 3)⟩
    LA TELE: ...la periodista Nadia Vidal, que viatjava a bord pagada per la mateixa fundació que... ⟨si aliada_nadia i aliats ≥ 3⟩
    LA TELE: ...en una gravació, la directora de comunicació de Skarn, Hedda Lind, diu que el fang és «un inconvenient tècnic»... ⟨si aliada_nadia i aliats ≥ 3⟩
    LA TELE: ...i el govern de Valmark ha suspès el permís d'abocament mentre duri la investigació... ⟨si aliada_nadia i aliats ≥ 3⟩
    NARRADOR: L'article de la Nadia és a la primera plana del North Atlantic Herald, amb la seva firma. Valmark «ajorna» la Cimera dels Oceans. ⟨si aliada_nadia i aliats ≥ 3⟩
    NARRADOR: El director de Skarn dimiteix «per passar més temps amb la seva família». ⟨si aliada_nadia i aliats ≥ 3⟩
    NARRADOR: La Capitana torna la donació de Blau Net en una roda de premsa. ⟨si (aliada_nadia i aliats ≥ 3) i aliada_capitana⟩
    IRI: I el Punt 7?
    VET: La Juana diu que, si deixen d'abocar avui, les arengades trigaran vint anys a tornar.
    NARRADOR: Una pausa.
    VET: Si tornen.
    IRI: Doncs que deixin d'abocar avui.
    NADIA VIDAL: M'han ofert feina fixa. És la primera vegada que algú em paga per dir la veritat. ⟨si aliada_nadia⟩
    CAPITANA ROIG: A l'abril no tindrem gasoil. Però el que tinguem serà net. ⟨si aliada_capitana⟩
    MARCEL: En Diu? Ningú no l'ha vist mai. Jo tampoc. ⟨si aliat_marcel⟩
    TOMÀS: Ha vingut la Juana a demanar-me la recepta de l'entrepà. M'he emocionat. ⟨si tomas_content⟩
    VET: I l'Ernest ha declarat. Ha tornat a casa d'un cosí, a Osca, a esperar el judici. ⟨si aliat_bastida⟩
    VET: Diu que és el primer lloc en trenta-cinc anys des d'on no veu el mar. Diu que s'ho mereix. ⟨si aliat_bastida⟩
    IRI: Osca? ⟨si aliat_bastida⟩
    VET: Osca. ⟨si aliat_bastida⟩
    NARRADOR: Una pausa. ⟨si aliat_bastida⟩
    IRI: Podríem anar a veure'l. ⟨si aliat_bastida⟩
    VET: Sí. Però el cafè el pagues tu. ⟨si aliat_bastida⟩
    VET: L'Ernest no ha dit res. Skarn diu que no el coneix. L'han deixat anar fins al judici, i ningú no sap on para. ⟨si NO aliat_bastida⟩
    IRI: Ell sí que ho sap. ⟨si NO aliat_bastida⟩
    NARRADOR: Una pausa. ⟨si NO aliat_bastida⟩
    IRI: Mira el mar des d'algun lloc. Segur. ⟨si NO aliat_bastida⟩
    NARRADOR: Una pausa.
    VET: Tres-cents mil euros. Tu què n'hauries fet?
    IRI: Res. No els hauria agafat.
    NARRADOR: Una pausa.
    IRI: Què em compro, amb tres-cents mil euros? Un altre mar?
    VET: Jo tampoc. Fa tres setmanes no sabia on era la proa. Ara em llevo de nit per veure sortir el sol per la popa.
    IRI: Per la proa. Anàvem cap a l'est.
    VET: Per la punxeguda. Això.
    NARRADOR: Una pausa.
    VET: Això no t'ho paga ningú.
    IRI: La Capitana diu que a l'abril tornem a sortir. Que no tindrem gasoil, però que potser tindrem metgessa.
    NARRADOR: Una pausa.
    IRI: I que el cap de màquines es jubila. Que la plaça és meva.
    VET: Felicitats, cap.
    VET: I tindreu metgessa.
    [SO: mossegada] NARRADOR: En Diu salta damunt la taula i mossega el cable de la tele. La pantalla s'apaga a mitja notícia.
      ⇒ +tele_apagada
    IRI: Diu!
    VET: Deixa'l. Ja hem vist prou notícies.
    NARRADOR: Les dues es queden mirant la badia, sense dir res. El sol surt per darrere seu, per damunt de la ciutat, i encén primer el pal de l'Arenga i després l'aigua.
    Ni un ou. Encara.
final_pagina4 «Pàgina 4» — quan enviat
    NARRADOR: Galway. Dues setmanes després, a primera hora del matí.
    NARRADOR: A la terrassa d'un bar del port. Davant, al moll, l'Arenga espera que li posin un volant nou a la vàlvula de popa.
    IRI: Ho hem aconseguit?
    VET: La Mostra 7 és en un laboratori de Dublín. Ningú de Valmark no l'ha tocada. I diu el que deia la Juana.
    IRI: I Skarn?
    VET: Skarn diu que «investigarà». Que és el que diuen sempre.
    LA TELE: ...una ONG denuncia abocaments a l'Atlàntic Nord. Fonts properes a la investigació qüestionen les finances de l'ONG... ⟨si no (aliada_nadia i aliats ≥ 3)⟩
    NARRADOR: La notícia, a la pàgina 4. ⟨si no (aliada_nadia i aliats ≥ 3)⟩
    VET: Les dades són al blog de la Juana. Tres mil visites. ⟨si no (aliada_nadia i aliats ≥ 3)⟩
    VET: I Skarn continua abocant «dins la legalitat». ⟨si no (aliada_nadia i aliats ≥ 3)⟩
    LA TELE: ...la periodista Nadia Vidal, que viatjava a bord pagada per la mateixa fundació que... ⟨si aliada_nadia i aliats ≥ 3⟩
    LA TELE: ...en una gravació, la directora de comunicació de Skarn, Hedda Lind, diu que el fang és «un inconvenient tècnic»... ⟨si aliada_nadia i aliats ≥ 3⟩
    LA TELE: ...i el govern de Valmark ha suspès el permís d'abocament mentre duri la investigació... ⟨si aliada_nadia i aliats ≥ 3⟩
    NARRADOR: L'article de la Nadia és a la primera plana del North Atlantic Herald, amb la seva firma. Valmark «ajorna» la Cimera dels Oceans. ⟨si aliada_nadia i aliats ≥ 3⟩
    NARRADOR: El director de Skarn dimiteix «per passar més temps amb la seva família». ⟨si aliada_nadia i aliats ≥ 3⟩
    NARRADOR: La Capitana torna la donació de Blau Net en una roda de premsa. ⟨si (aliada_nadia i aliats ≥ 3) i aliada_capitana⟩
    IRI: I el Punt 7?
    VET: La Juana diu que, si deixen d'abocar avui, les arengades trigaran vint anys a tornar.
    NARRADOR: Una pausa.
    VET: Si tornen.
    IRI: Doncs que deixin d'abocar avui.
    NADIA VIDAL: M'han ofert feina fixa. És la primera vegada que algú em paga per dir la veritat. ⟨si aliada_nadia⟩
    CAPITANA ROIG: A l'abril no tindrem gasoil. Però el que tinguem serà net. ⟨si aliada_capitana⟩
    MARCEL: En Diu? Ningú no l'ha vist mai. Jo tampoc. ⟨si aliat_marcel⟩
    TOMÀS: Ha vingut la Juana a demanar-me la recepta de l'entrepà. M'he emocionat. ⟨si tomas_content⟩
    VET: I l'Ernest ha declarat. Ha tornat a casa d'un cosí, a Osca, a esperar el judici. ⟨si aliat_bastida⟩
    VET: Diu que és el primer lloc en trenta-cinc anys des d'on no veu el mar. Diu que s'ho mereix. ⟨si aliat_bastida⟩
    IRI: Osca? ⟨si aliat_bastida⟩
    VET: Osca. ⟨si aliat_bastida⟩
    NARRADOR: Una pausa. ⟨si aliat_bastida⟩
    IRI: Podríem anar a veure'l. ⟨si aliat_bastida⟩
    VET: Sí. Però el cafè el pagues tu. ⟨si aliat_bastida⟩
    VET: L'Ernest no ha dit res. Skarn diu que no el coneix. L'han deixat anar fins al judici, i ningú no sap on para. ⟨si NO aliat_bastida⟩
    IRI: Ell sí que ho sap. ⟨si NO aliat_bastida⟩
    NARRADOR: Una pausa. ⟨si NO aliat_bastida⟩
    IRI: Mira el mar des d'algun lloc. Segur. ⟨si NO aliat_bastida⟩
    NARRADOR: Una pausa.
    VET: Tres-cents mil euros. Tu què n'hauries fet?
    IRI: Res. No els hauria agafat.
    NARRADOR: Una pausa.
    IRI: Què em compro, amb tres-cents mil euros? Un altre mar?
    VET: Jo tampoc. Fa tres setmanes no sabia on era la proa. Ara em llevo de nit per veure sortir el sol per la popa.
    IRI: Per la proa. Anàvem cap a l'est.
    VET: Per la punxeguda. Això.
    NARRADOR: Una pausa.
    VET: Això no t'ho paga ningú.
    IRI: La Capitana diu que a l'abril tornem a sortir. Que no tindrem gasoil, però que potser tindrem metgessa.
    NARRADOR: Una pausa.
    IRI: I que el cap de màquines es jubila. Que la plaça és meva.
    VET: Felicitats, cap.
    VET: I tindreu metgessa.
    [SO: mossegada] NARRADOR: En Diu salta damunt la taula i mossega el cable de la tele. La pantalla s'apaga a mitja notícia.
      ⇒ +tele_apagada
    IRI: Diu!
    VET: Deixa'l. Ja hem vist prou notícies.
    NARRADOR: Les dues es queden mirant la badia, sense dir res. El sol surt per darrere seu, per damunt de la ciutat, i encén primer el pal de l'Arenga i després l'aigua.
    Ni un ou. Encara.
```
