# La Conjura de l'Avet — pla de feina

> Fase 0 de la [guia de joc nou](../../../docs/guia-joc-nou.md): la revisió de la [proposta inicial](proposta-inicial.md)
> (22-11-2026), el que s'hi ha de canviar i les decisions que falten. Quan hi hagi `guio.md`, la font de la veritat
> serà aquell document i aquest pla quedarà com a historial.
> Carpeta: `games/conjura-avet/` (provisional).

## Ja decidit (per l'usuari)

- **Títol:** *La Conjura de l'Avet*.
- **Lloc i època:** Sant Joan de les Abadesses, any 1017, poc abans que expulsin les monges. El context és
  històric; la història, no.
- **Gènere:** un misteri amb humor buròcrata, no una història de religió.
- **Protagonistes:** la Iri i la Vet, amb la cara de sempre (la de Suma Zero) i rols, roba i cabell nous.
- **L'avet:** un avet vell al costat del monestir cau un dia de pluja i vent, i forma part de la trama.
- **La disfressa:** en algun moment, les dues es vesteixen de monjos per fer una cosa que les dones no podien fer.
- **El fons:** feminista, amb un fil ecologista.
- **Art:** com sempre, 3D de cantonada a 640×360.

## Segones decisions (22-11-2026)

- **Rigor històric, el just.** El context (l'any 1017, l'Ingilberga, l'expulsió) es manté, però el poble es dibuixa
  **com és avui**: l'absis romànic, el claustre gòtic, el Pont Vell i Sant Pol. Les llicències es diuen **als
  crèdits**, al final de tot. Els anacronismes de sota només es corregeixen quan la correcció millora la història
  (el signe de l'escrivà, el jutge Ponç); la resta es queda com era.
- **Referències gràfiques reals** a `art/referencia/` (vegeu «Direcció d'art»), per reproduir-les en pixel art.
- **L'avet és el de debò**: el que hi havia al costat de l'absis, i que va caure (`avet-caigut.png`).
- **Sant Pol, l'església sense parets**, entra al joc, i ens inventem per què no en té (vegeu el punt 9).
- **Una protagonista per sala**, però en alguna sala poden col·laborar.
- **A partir de 12 anys, 2-3 hores.**

## Terceres decisions (22-11-2026)

- **El final resol el misteri** i de l'expulsió en parla poc o gens. **Cap rètol** sobre el nom del poble.
- **El misteri** ha de ser més misteriós: un **cofre** enterrat i lligat a alguna altra cosa robada. Nova proposta al
  punt 1, aprovada.
- **El pare, detingut** a l'acte I (vegeu «El pare, detingut» al punt 1).
- La Iri i la Vet són **germanes**.
- **Sant Pol: l'opció A**, l'església que el comte no va pagar; els diners es van quedar a **Ripoll**.
- **Sales de col·laboració:** la plaça, la cuina i el molí.
- **Persones reals:** l'Ingilberga a escena; el comte Bernat, no; l'Emma, a la llegenda i a la carta.
- **Mecànica nova:** el **calc amb carbonet** com a acció pròpia (a la plaça, a l'scriptorium i potser a la serra).

## Què es queda de la proposta

- L'estructura en quatre actes (missions `acte1`…`acte4`), amb la investigació, la disfressa, l'arxiu i el judici.
- **Els buròcrates pedants en lloc de malvats tenebrosos.** És el millor de la proposta i el to de la casa: l'humor
  ve de les coses (segells, testimonis, pergamins per triplicat) i no dels discursos.
- La **disfressa desastrosa**: hàbits gegants, barbes de llana enganxades amb resina, el «vot de silenci extrem», la
  tos de fum.
- La **resina de l'avet** com a objecte que torna: enganxa les barbes, segella el pot dels pergamins. L'arbre ajuda
  fins i tot caigut.
- La **serra encallada a la resclosa**, que explica per què baixa l'aigua del rec del molí, i el **molí** com a
  sortida a l'acte III: la mateixa aigua obre i tanca la investigació.
- El **carbonet sobre el pergamí** per treure el relleu de l'última carta.
- La **revelació a l'acte IV**: es treuen les caputxes davant de tothom.
- L'**epíleg plantant un avet jove**.
- Reaprofitar sales amb una altra llum, com a L'Última Arrel.

## El context històric (el que lliga i el que no)

El que diuen les fonts (vegeu les referències al final):

- **Ingilberga** va ser l'última abadessa (995/996-1017). Era **filla natural del comte Oliba Cabreta**, i per tant
  **germanastra del comte Bernat Tallaferro** de Besalú i de l'abat Oliba.
- El 1017, Bernat va obtenir del papa Benet VIII una butlla que expulsava les monges, **amb l'acusació de «vida
  dissoluta»**, i va fer del monestir una canònica del nou **bisbat de Besalú**, amb el seu fill Guifré de bisbe.
  Els béns del monestir van passar al bisbat.
- El monestir l'havia fundat el 885 Guifré el Pelós per a la seva filla **Emma**, la primera abadessa.
- Hi ha un estudi sobre les **signatures de les monges i la seva alfabetització** a la Catalunya de finals de l'època
  carolíngia: les monges sabien escriure i signaven elles mateixes (a verificar quan escrivim el guió, però és el
  millor ganxo del fil feminista; vegeu més avall).

Això dona al joc dos regals que la proposta no fa servir:

1. **El dolent és el germà de l'abadessa.** No cal que el comte surti mai a escena, però l'Ingilberga ho sap i ho
   diu amb ironia («El meu germà sempre ha tingut mala memòria per als deutes»).
2. **L'acusació real era moral, no econòmica.** Les dones, acusades de ser dones. La «negligència arbòria i bruixeria
   meteorològica» de la proposta n'és la versió còmica, i funciona perquè és igual d'absurda. A més, l'acusació de
   ser *tempestàries* (provocar tempestes) és d'època: Agobard de Lió en parlava al segle IX.

### Anacronismes de la proposta, i què hi posaríem

> Des de les segones decisions, aquesta taula és un catàleg i no una llista de deures. Es queden el **signe** de
> l'escrivà i el **jutge Ponç**, perquè fan la història millor. El **claustre gòtic** i el **Pont Vell** es dibuixen
> com són avui, i van a la nota dels crèdits. La resta, a criteri del guió.

| A la proposta | El problema | Proposta |
|---|---|---|
| L'**escut** de l'escrivà a la serra | L'heràldica apareix a mitjan segle XII | El **signe** (*signum*) de l'escrivà, el dibuix que cada escrivà feia als pergamins. Surt a la serra i a les signatures falses: és la mateixa mà |
| **Claustre romànic** amb arcs | L'església actual és del 1150 i el claustre, del 1442 (gòtic); els arcs romànics que queden són del segle XII | El monestir preromànic: pedra tosca, un pati amb un porxo de fusta. La sala es pot dir `pati` |
| El **pont** sobre el Ter | El Pont Vell és del 1128-1138 | Una passera de taulons i la **resclosa** del rec del molí (`resclosa_ter`) |
| **Ban municipal**, **picota**, «permís de lectura pública» | No hi ha municipi; la picota és més tardana | La **crida del batlle** del comte, clavada a la porta de l'església, i la **queixa** que els fan signar |
| **Cobradors d'impostos** | — | El **batlle** i el **saig** del comte, que cobren censos i delmes |
| Hàbit **marró** (escorça de noguera) | Els benedictins eren els *monjos negres*; el marró és franciscà (segle XIII) | Tenyir-los de **negre**: clofolles de nou i ferro rovellat (claus vells de la ferreria) a la tina |
| **Fra** Ponç | *Fra* és dels frares mendicants, dos segles més tard | **El jutge Ponç**: als comtats catalans de l'època hi havia jutges (*iudices*). I així presideix el judici de l'acte IV |
| Els **homes del bisbe** | — | Els **canonges** del nou bisbat de Besalú, que ja s'hi han instal·lat |
| **Armadura** del guàrdia | — | Cota de malla o perpunt (on s'hi pot ficar un ratolí igual de bé) |
| Serra d'**acer** | — | Serra de **ferro** |
| El **molí subterrani** | — | El molí del monestir, sobre el rec (`moli`) |
| L'**om** (al text de l'humor) | L'arbre és un avet | Avet a tot arreu |
| L'avet al costat del monestir | A 770 m, l'avet no hi és habitual (creix més amunt) | Una virtut: el va **plantar l'Emma**, portat de la muntanya. Per això és tan especial i tan sol |

## Què cal canviar o resoldre

### 1. El misteri i el crim (proposta 2, aprovada el 22-11-2026)

> La primera proposta (una carta enterrada sota l'avet, que l'escrivà es queda) era justa. Aquesta hi afegeix un
> cofre, dos robatoris i una clàusula que lliga l'avet amb la terra, i que fa que el crim sigui l'arbre mateix.

**Què va passar fa 130 anys.** Quan el comte Guifré va donar les terres de la vall al monestir, l'Emma, la primera
abadessa, va voler una **carta partida**: el mateix text escrit dues vegades en un pergamí, tallat pel mig en
ziga-zaga. Una meitat se la queda el comte, l'altra el monestir, i només val si les dues encaixen. La carta té una
clàusula estranya, idea de l'Emma:

> *Aquestes terres seran de les dones del monestir **mentre l'avet de l'Emma sigui dret**.*

L'Emma va plantar l'avet, portat de la muntanya, i va enterrar la seva meitat sota les arrels, dins un **cofre
segellat amb cera vermella**. «Els pergamins, els homes els perden. Els arbres, no.» Al dors de la seva meitat, i
només de la seva, hi va afegir una línia amb la seva mà:

> ***I si l'avet cau per mà d'home, que qui l'hagi tombat en planti un altre, i que la terra sigui de les dones
> mentre el nou sigui dret.***

Amb els anys, el monestir n'ha oblidat la clàusula. Al poble només en queda una **cançó de bressol** («L'avet de
l'Emma guarda el que és nostre…»), que la Gueraula canta sense saber què vol dir.

**Per què ara.** El comte Bernat va prometre pagar les parets de Sant Pol. Els diners **es van quedar a Ripoll**, i
el comte deu al monestir una fortuna. En Sunifred, el seu escrivà, troba a l'arxiu del comte l'altra meitat de la
carta, llegeix la clàusula i hi veu la solució: **si l'avet cau, la terra torna al comte i el deute desapareix.**

**El crim, en tres robatoris:**

1. **La serra** (una setmana abans). En Sunifred roba la serra del llenyataire, el **pare de l'Iri i la Vet**. Si
   algú veu el tall, culparan el llenyataire.
2. **L'avet** (la nit de la tempesta). Serra les arrels del costat del vent, i la tramuntana fa la resta. L'arbre
   cau damunt el mur, i les arrels arrenquen el cofre de terra. **És la portada:** el segell vermell que brilla entre
   les arrels.
3. **El cofre** (la mateixa nit). En Sunifred se l'endú, l'obre i hi llegeix la línia de l'Emma. Ara l'arbre ha de
   semblar caigut **pel vent**, i no per mà d'home. Llença la serra al riu (s'encalla a la comporta de la resclosa,
   i per això baixa l'aigua del rec del molí). Però **no crema la carta: és escrivà, no un bàrbar.** Un document
   segellat no es destrueix; s'arxiva. L'amaga al doble fons d'un bagul de l'arxiu.

**Vent o mà d'home?** L'avet cau amb la tempesta, i és el que veu tothom. Però en 130 anys n'ha aguantat cent de
tramuntanes, i aquesta nit cau perquè té les arrels serrades. Aquesta és la discussió del judici, i és on hi ha la
gràcia: en Sunifred i el jutge Ponç diuen que l'ha tombat el vent («El vent no és un home. Per tant, no hi ha mà
d'home»), i la Vet respon: «I el vent porta serra?». Les germanes han de demostrar que sense la serra no hauria
caigut: el tall net de les arrels del costat del vent, la serra del pare a la resclosa i l'ordre del jutge escrita
abans de la tempesta.

**Com ho vol tancar.** Sense la meitat del monestir, la carta no es pot comprovar, i per a això la llei demana **tres
testimonis**. En Sunifred en fabrica una queixa signada pel poble: que les monges no cuidaven l'avet
(«negligència arbòria») i que el van fer caure amb les seves arts («bruixeria meteorològica»). L'acusació còmica de
la proposta ara té sentit: és el que necessita perquè l'arbre sembli caigut sol. I l'endemà al matí ja hi ha el
jutge Ponç, amb l'ordre escrita.

**El pare, detingut.** A la sala 1, quan l'Iri diu que el tall és de serra, en Sunifred fa notar, molt amable, que
al poble només hi ha una serra així. El jutge Ponç fa tancar el llenyataire «en custòdia preventiva, pendent de tres
testimonis» al celler del batlle, entre bótes de vi. És el que fa que les germanes no puguin esperar, i el que
posa el rellotge al joc: **el judici és l'endemà al matí**. Es manté el to de comèdia: el pare no té gens de por,
es queixa del vi («Aquest és el del batlle? Ja entenc per què no convida mai») i, quan les filles el visiten, és una
font de pistes (la serra li van robar fa una setmana; a la nit va sentir algú que serrava). Al judici, l'alliberen.

**El que troben, acte per acte:**

| Acte | La pregunta | Les pistes |
|---|---|---|
| I | **Qui ha tombat l'avet, i què hi havia a sota?** | El tall és de serra (l'Iri ho veu, és filla del llenyataire). Al forat de les arrels, un tros de cera vermella amb el segell de l'Emma. L'ordre del jutge Ponç **té data d'ahir**: estava escrita abans de la tempesta. La serra del pare no hi és. A la resclosa, la serra del pare, amb el mànec embolicat amb una tira de pergamí (costum d'escrivà) on es veu un **signe**. A la plaça, la queixa: noms escrits sencers de gent que només sap fer una creu, i el mateix signe al peu. La cançó de la Gueraula |
| II | **Com entrem a l'arxiu?** | La disfressa i les claus |
| III | **On és el cofre, i per què?** | Amb el carbonet, la carta d'en Sunifred al comte: «Quan l'avet caigui, la terra tornarà al comte, i el deute de Sant Pol quedarà saldat.» Al doble fons del bagul, el cofre de l'Emma i la seva meitat de la carta, amb la línia del dors |
| IV | **Com ho fem creure?** | Al judici, la meitat del comte (la porta el jutge Ponç) i la de l'Emma **encaixen**: la carta és bona, i el jutge no pot dir que no a un document tan ben fet. La línia del dors, la serra i el tall: l'avet va caure **per mà d'home**. La queixa, falsa |

**El final.** La clàusula es gira contra en Sunifred: qui l'ha tombat n'ha de plantar un altre, i la terra és de les
dones **mentre el nou sigui dret**. A l'epíleg, l'Iri i la Vet planten el plançó (en Sunifred carrega la galleda),
el jutge Ponç hi posa un segell «perquè consti», i el cofre torna a sota les arrels, amb la carta sencera.

**Per què crec que funciona:**

- **L'avet és el crim, la prova i la solució.** No és decorat: la llei del joc està lligada a l'arbre.
- Hi ha **un enigma de debò** (què hi havia al cofre?) que no es resol fins a l'acte III.
- La **burocràcia** és el motor còmic i també la solució: en Sunifred perd perquè és massa escrupolós per cremar un
  document, i el jutge Ponç dona la raó a les dones perquè els papers són en regla.
- **El fil feminista** és a la història, no als discursos: una dona de fa 130 anys va preveure el que farien els
  homes i ho va deixar escrit on no ho poguessin perdre.
- **És personal:** la serra és del pare de les germanes. Si no troben qui va ser, el culpable serà ell.

### 2. Dos dolents de més

La proposta té el comte (fora d'escena), Fra Ponç, l'escrivà, els homes del bisbe i els guàrdies. Proposta:

- **El jutge Ponç**: pedant, obsessionat amb els segells, **però honest**. Es creu l'acusació perquè té els papers en
  regla. Al final el venç la mateixa burocràcia: la carta de l'Emma és més antiga i té més signatures que la queixa.
- **L'escrivà Sunifred**: el que maquina, el del signe a la serra i a les signatures falses. Educat, amable, mai no
  aixeca la veu.
- Els canonges i el guàrdia són figurants còmics.

### 3. Objectes que no porten enlloc, i objectes que surten del no-res

- **La còpia del ban (sala 2)** no serveix per a res més. Proposta: el que copien és la **queixa del poble contra les
  monges**, amb les signatures. Els veïns diuen que ells no han signat res. I és veritat: la majoria **no saben
  escriure** i signen amb una creu, però a la queixa hi ha els seus noms escrits sencers, amb lletra d'escrivà i el
  signe d'en Sunifred al peu. És una prova de l'acte IV.
- **El salconduit (sala 7)** no surt de cap lloc. Proposta: l'escriu la Vet (sap escriure, i el guàrdia no sap
  llegir: només mira el segell) i el segella amb resina perquè no tenen cera. Gag: el guàrdia l'aguanta de cap per
  avall i el troba «molt en regla».
- **El llibre de comptes i la carta (sala 9)** són dues coses en una. Proposta: el carbonet treu el relleu de la
  carta d'en Sunifred al comte («el deute quedarà saldat quan les monges hagin marxat»). El llibre de comptes, fora.
- **El document original (sala 10)** passa a ser la **carta de l'Emma**, robada de sota l'avet.
- **La resina** surt tres vegades (barbes, salconduit, pot): que sigui un **pot de resina** que no s'acaba, perquè
  no hi hagi atzucacs.

### 4. La sala 4 no té trencaclosques

El pati de l'abadessa és pura conversa. Proposta: l'Ingilberga no deixa que les dues s'hi juguin el coll; l'han de
convèncer que poden passar per monjos. Una prova còmica: la Vet ha d'imitar un canonge (caminar com ells, beneir com
ells), i l'Iri, ella mateixa, no se'n surt. També és on se sent per primer cop la cançó de bressol de l'Emma (la
canta la Gueraula), que a l'acte III diu on és la carta.

### 5. On es fa el judici

La proposta posa l'assemblea a la plaça, però «davant l'avet caigut», que és al mur. Proposta: el **judici de l'avet
es fa al mur**, perquè l'arbre mateix és una prova (el tall de serra). Així `mur_avet` té **tres llums**: el matí de
pluja (acte I), el sol després de la tempesta amb tot el poble (acte IV) i la primavera (epíleg). La plaça es queda
com a sala de l'acte I i, si cal, torna amb una altra llum.

### 6. El final i la història de debò

**Decidit (22-11-2026): el final resol el misteri i parla poc de l'expulsió.** El clímax és el judici de l'avet:
en Sunifred desemmascarat, la carta de l'Emma recuperada, el jutge Ponç que la reconeix amb tots els segells i el
poble que no ha signat res. L'expulsió, com a molt, de passada: una línia de l'Ingilberga a l'epíleg («El meu germà
encara té amics a Roma. Però avui, no.») i la nota dels crèdits, que explica què va passar de debò el 1017. Ni
victòria definitiva de les monges ni comiat trist: el joc acaba amb el plançó d'avet i la carta tornada a enterrar.

*Les opcions que s'havien plantejat, com a historial:*

**Les monges van ser expulsades el 1017.** Si al joc es queden, el joc contradiu el rigor que demanes. Hi ha dues
maneres de fer-ho:

- **A) Agredolç i fidel a la història (recomanat).** El judici es guanya: en Sunifred cau, el jutge Ponç reconeix la
  carta de l'Emma, el poble defensa les monges. Però la butlla del papa ja és signada a Roma, i «una butlla no la
  desfà ni un avet». Les monges marxen. Abans, l'Ingilberga dona a la Vet el seu estilet i la carta de l'Emma per
  guardar, i la Gueraula ensenya a llegir a les nenes del poble a la plaça. L'epíleg: plantar l'avet jove, amb una
  caixa nova a sota. (El rètol sobre el nom del poble, descartat: vegeu les terceres decisions.)
  És el to de la casa (el bosc es salva però NaturaPlus no s'acaba; plou, però el Magnat no cau del tot).
- **B) La victòria de la proposta.** Les monges es queden. Més rodó, però és ucronia i cal dir-ho (un rètol final
  que ho reconegui).

### 7. El fil feminista, ensenyat i no explicat

La regla de la casa: la crítica és a les coses, no als discursos. Proposta de com fer-lo:

- **Les mateixes paraules, una altra roba.** A l'acte I, la Vet explica al jutge Ponç que el tall és de serra, i ell
  no l'escolta («Una dona i un arbre: dos testimonis sense valor»). A l'acte IV, el mateix argument, amb les mateixes
  paraules, el diu un «germà» encaputxat, i el jutge ho troba brillant. Llavors es treuen les caputxes. La Vet
  només diu: «Ho he dit dues vegades. Només ha canviat la roba.» Aquest és el punt feminista, i no cal res més.
- **Saber escriure.** Les monges signen; els homes de la queixa, no (la signen per ells). La Vet sap llegir perquè
  la van ensenyar les monges, i és el que la salva a cada acte.
- **La carta de l'Emma**: una dona que, 130 anys abans, ja sabia que els pergamins es perden.

### 8. L'humor buròcrata, amb mitjans d'època

El «formulari B-12» és un bon acudit però trenca el rigor. El mateix esperit amb coses d'època: **tres testimonis i
un segell** per a qualsevol cosa, el jurament sobre relíquies per entrar a la cuina, el pergamí «per triplicat»
(copiat tres vegades a mà, cada còpia amb errates diferents), el guàrdia que no sap llegir i només mira la cera.

**Gags que tornen** (a tancar a l'epíleg o als crèdits):

- El jutge Ponç i els segells (al final, segella el plançó d'avet «perquè consti»).
- La tos de fum de l'Iri, cada cop més exagerada.
- «Quatre tones», la Vet calculant el pes de tot el que l'Iri vol empènyer.

### 9. Sant Pol: per què no té parets

Sant Pol té la façana, el campanar i un absis, però la nau és oberta al cel, amb gespa on hi hauria d'haver el
terra (`sant-pol-sense-parets.png`). Tres idees per inventar-nos per què. Recomano la primera:

- **A) L'església que el comte no va pagar (triada el 22-11-2026).** El comte Bernat va prometre a les monges una església
  nova. Es van fer la façana i el campanar, amb el seu nom ben gros a la llinda, i les parets no es van fer mai:
  els diners **es van quedar a Ripoll**. És el **deute del comte fet pedra**, al mig del poble, i la
  prova que tothom veu i ningú no llegeix. Els canonges hi diuen missa «a l'aire lliure, per decisió litúrgica». I
  és el lloc on es reuneixen les dones del poble, perquè **en una església sense parets ningú no els pot tancar la
  porta**. La plaça de la vila (sala 2) seria la plaça de davant de Sant Pol.
- **B) Les parets van anar a parar a la resclosa.** En Sunifred va fer desmuntar les parets «per reparar la
  resclosa», i en realitat la va fer més alta per desviar l'aigua del molí de les monges al molí del comte. La
  serra a la comporta (sala 3) i les pedres de Sant Pol formarien part del mateix pla.
- **C) Les parets les tomba el joc.** A l'acte III, l'Iri i la Vet fugen de l'escrivà i les parets cauen (un
  contrapès, la roda del molí, l'avet que s'hi recolza). Al final, el poble decideix deixar-la així. Fa gràcia, però
  és destrossa.

A totes tres, el **campanar** és un lloc on l'Iri s'hi pot enfilar: des de dalt es veu tot el poble, l'avet caigut i
qui entra i surt del monestir.

### 10. On poden col·laborar

Una protagonista per sala, i dues o tres sales de col·laboració, on l'altra fa una cosa des d'un altre lloc (com el
walkie de L'Última Arrel, però a l'any 1017: un **senyal de campana**, un cordill, un mocador a la finestra).
Candidates:

- **La plaça de Sant Pol (sala 2):** l'Iri, dalt del campanar, distreu el guàrdia (el ratolí, la campana) mentre la
  Vet, a baix, calca la queixa.
- **La cuina (sala 8):** les dues de novicis serveixen el sopar; una aboca l'herba al vi mentre l'altra fa parlar
  l'escrivà.
- **El molí (sala 11):** la de la proposta. La comporta i la roda alhora, amb la Gueraula de tercera.

Les sincronies d'Aigua Verne ja ho fan (per torns); caldrà mirar si n'hi ha prou o si cal adaptar-les.

## Les protagonistes

**Germanes** (decidit el 22-11-2026), filles del llenyataire del poble, d'uns 18-20 anys. La Vet, la petita, la van
portar de nena al monestir a aprendre de lletra, i encara hi treballa.

| | Iri | Vet |
|---|---|---|
| **Feina** | **Llenyatera**, amb el pare. Coneix la fusta | **Escrivana** al monestir, ajudant de la Gueraula. Llegeix llatí i sap d'herbes |
| **Què fa al joc** | Veu que el tall és de serra i no de vent; s'enfila, empeny, distreu | Llegeix, copia, falsifica, recepta |
| **Disfressada** | Un monjo alt i robust, que tus | Un monjo petit amb l'hàbit que arrossega, de «vot de silenci extrem» |
| **Roba (provisional)** | Gonella curta de llana, davantal de cuir, destral al cinyell, guants. Cabell nou (no la cua de Suma Zero) | Gonella llarga de color, ploma i tinter al cinyell, una bossa d'herbes. Cabell nou |

Canvi respecte de la proposta: a la sala 1 és **l'Iri** qui veu que el tall és de serra (és llenyatera); la Vet és la
que ho sap demostrar amb paraules. Els guants ja són de l'Iri; el trencaclosques de la sala 1 ha de ser un altre
(per exemple, arribar al forat de la caixa entre les branques).

**Les veus:** a les sales on van disfressades, la guia de veus ja permet canviar el to. Les línies «de monjo» de
l'Iri i la Vet poden sortir més greus (el xarop de menta), i en el moment de la revelació tornen a la seva veu.

## Les sales revisades

| # | Sala | Acte | Lloc i llum | Notes |
|---|---|---|---|---|
| 0 | `portada` | — | El mur i l'avet caient, de nit, tramuntana | La figura amb la serra, el segell que brilla un instant |
| — | `proleg` | — | Mateix pla que la portada | Cinemàtica curta: l'arbre cau. Títol, «Acte 1» |
| 1 | `mur_avet` | I | Matí de pluja | L'absis i l'avet caigut, el forat buit, el tros de cera. El jutge Ponç acusa |
| 2 | `placa_sant_pol` | I | Pluja | Sant Pol sense parets i el campanar. La crida, la queixa, el saig. Els veïns que «no han signat». Col·laboració |
| 3 | `pont_ter` | I | Riu crescut, núvols | El Pont Vell, la resclosa i la serra amb el signe encallada a la comporta |
| 4 | `claustre` | I | Tarda, gotes de les teulades | El claustre i la pica. L'Ingilberga i la Gueraula. Convèncer-les. La cançó de l'Emma |
| 5 | `bugaderia` | II | Vapor, capvespre | Tenyir els hàbits de negre |
| 6 | `apotecaria` | II | Espelmes | Barbes, celles, xarop, herba dormidora, el salconduit |
| 7 | `porteria` | II | Torxes | El guàrdia, el sant i senya, «la conjura de l'avet» |
| 8 | `cuina` | II | Llar de foc | En Sunifred sopa; les claus. Col·laboració |
| 9 | `scriptorium` | III | Espelmes, nit | Els canonges copistes; el relleu de la carta |
| 10 | `arxiu` | III | Fosc | El bagul, el contrapès, la carta de l'Emma |
| 11 | `moli` | III | Nit, aigua | La comporta i la roda amb la Gueraula; sense derrota. Col·laboració |
| 12 | `mur_avet` (judici) | IV | Sol després de la tempesta | Tot el poble. Les proves, la revelació |
| 13 | `mur_avet` (epíleg) | — | Primavera | El plançó. Crèdits |

Són **11 sales jugables diferents** (més dos estats de `mur_avet`), unes quantes més que Aigua Verne, per a **2-3
hores** i a partir de 12 anys. Si cal retallar, les candidates són `porteria` (es pot fondre amb `cuina`) i
`pont_ter` (la serra pot aparèixer al rec, al costat del molí, i així `moli` serveix dues vegades); però el Pont Vell
és de les referències més boniques, i val la pena guardar-lo.

## Direcció d'art (primera idea)

- **Paleta:** pedra tosca grisa i ocre, fusta fosca, el **verd fosc de l'avet** com a color propi del joc i el
  **vermell de la cera** com a accent (la portada, el tros de cera, el signe, els segells del jutge Ponç).
- **Llum:** tempesta freda i blava a l'acte I; foc, espelmes i torxes càlides a l'interior dels actes II i III; el
  sol net del matí a l'acte IV.
- **Escala:** l'avet és enorme, més alt que l'absis. Que l'arbre caigut sigui la cosa més gran del joc.
- **Paleta presa de les fotos:** el gres rosat i ocre de l'absis i del Pont Vell, la pedra grisa i daurada de Sant
  Pol, el blanc trencat i les columnes fosques del claustre, la teula, el verd de la gespa i el verd fosc de l'avet.
- **Roba:** de l'any 1000 (els Beatus, el Tapís de la Creació de Girona), encara que l'arquitectura sigui posterior.

### Referències gràfiques (`art/referencia/`)

| Fitxer | Què és | Per a quina sala | Què se n'agafa |
|---|---|---|---|
| `absis-avet.png` | L'absis romànic amb l'avet a l'esquerra, sol de primavera | `mur_avet` (judici i epíleg), portada | La composició en 3/4, les arcuacions, l'avet al costat. És la candidata a sala de mostra |
| `absis-tardor-avet.png` | El mateix, de tardor i amb el cel blanc | `mur_avet` (acte I) | La llum grisa i plana del dia de pluja |
| `avet-caigut.png` | L'avet al costat de l'absis, el dia que va caure, amb les branques al terra | Portada, pròleg, `mur_avet` | L'arbre contra l'absis, les branques escampades pel carrer |
| `claustre-1.png`, `claustre-2.png` | El claustre des de la galeria, amb els arcs i la gespa | `claustre` | La galeria en perspectiva (càmera de cantonada des de dins), el sostre de fusta |
| `claustre-campanar.png` | El claustre amb el campanar del monestir al fons | `claustre` | El campanar com a fons, la columna en primer pla |
| `claustre-pica.png` | El claustre amb la pica de pedra al mig i un arbre | `claustre` | La pica (un objecte per tocar: s'hi pot amagar alguna cosa) |
| `sant-pol-sense-parets.png` | Sant Pol: la façana, el campanar i la nau oberta | `placa_sant_pol` | La façana, el campanar per enfilar-s'hi, la gespa dins l'església |
| `pont-vell.png` | El Pont Vell sobre el Ter, amb horts i un salze | `pont_ter` | L'arc gran, l'aigua verda, la resclosa a sota, els horts del primer pla |

Les fotos són guies de composició i de color: no s'importen al joc, es redibuixen amb `tres_d.py`.

## Preguntes obertes (per a l'usuari)

Resoltes el 22-11-2026: vegeu les segones i les terceres decisions. No en queda cap per començar el guió.

## Ordre de feina

1. **Aquest pla, revisat** (fase 0). Fet el 22-11-2026.
2. **Esquelet** `games/conjura-avet/` (fase 1): `package.json`, `game/` buit, `adapters/benne/joc.ts`, el projecte
   Benne, i que s'obri al navegador.
3. **Guió** `guio/guio.md` (fase 2), revisat el 22-11-2026; ara és la font de la veritat. Amb l'estructura del d'Aigua Verne: premissa i lema, to, protagonistes,
   secundaris, regles del món, escenes pas a pas, pistes, gags que tornen, mapa de dependències, encaix amb el motor,
   abast. **Revisió de l'usuari abans de seguir.**
4. Fitxes de les sales, contingut jugable en text i tests, art provisional, revisió, i l'art definitiu començant per
   **`mur_avet`** com a sala de mostra (és la que surt tres vegades i la de la portada).

## Referències

- [Ingilberga, Enciclopèdia Catalana](https://www.enciclopedia.cat/EC-GEC-0033638)
- [Monestir de Sant Joan de les Abadesses, Enciclopèdia Catalana](https://www.enciclopedia.cat/gran-enciclopedia-catalana/monestir-de-sant-joan-de-les-abadesses)
- [Bernat I de Besalú, Enciclopèdia Catalana](https://www.enciclopedia.cat/gran-enciclopedia-catalana/bernat-i-de-besalu)
- [Monastery of Sant Joan de les Abadesses: medieval power with a woman's name, Patrimoni Gencat](https://patrimoni.gencat.cat/en/node/10877)
- [Nuns' signatures and literacy in late-Carolingian Catalonia, *Traditio*](https://www.cambridge.org/core/journals/traditio/article/nuns-signatures-and-literacy-in-latecarolingian-catalonia/B8B041290DAA2454521E44CEFF457CA3/share/022f0b20f668f69eb4cc3c18acfcebce01a5f1bb)
- [Sant Joan i Sant Pau, Catalunya Romànica](https://www.enciclopedia.cat/catalunya-romanica/sant-joan-i-sant-pau-o-sant-pol-sant-joan-de-les-abadesses)
