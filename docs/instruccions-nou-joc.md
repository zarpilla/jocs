# Instruccions per fer un joc nou amb Benne

> Per a l'agent d'IA que començarà el segon joc. Amb aquest document reps un `.txt` amb el primer
> guió, que encara s'ha d'afinar.
>
> El joc anterior, **Ferro-9**, és a `/home/jordi/Documents/work/benne` (repositori git, 105 commits).
> Funciona, s'ha jugat de cap a peus i n'estem contents. Aquí hi ha **com es va fer, què va anar bé i
> què hem de fer millor**. Llegeix-lo sencer abans de començar.

---

## 0. Normes de treball

- **Tot en català**: el guió, la documentació, els textos del joc i els missatges de commit.
- **Fes commit a cada pas verificat** (tests en verd, `npm run validate` net), sense que t'ho demanin.
  Missatges curts i descriptius, com els de Ferro-9 (`git log` hi té bons exemples). **No facis push.**
- **Pregunta abans de decidir** les coses que marquen tot el projecte (secció 2). La resta, decideix-la
  tu i explica-ho.
- El guió és la font de la veritat. Si mentre implementes canvies la història, **actualitza el guió en
  el mateix commit**.

---

## 1. Què es reaprofita de Ferro-9

Ferro-9 té la història **separada del motor** en tres capes. Llegeix primer aquests fitxers:

| Fitxer | Per què |
|---|---|
| `README.md` | L'arquitectura, les ordres i l'estat del projecte |
| `docs/guia-contingut.md` | **Com s'escriu tot el contingut** (sales, diàlegs, condicions, efectes, pistes, finals, sons). És el manual que faràs servir cada dia |
| `adapters/benne/README.md` | Com es connecta amb Benne, què genera el sync i les limitacions conegudes |
| `guio/guio.md` | Un exemple de guió ben estructurat (fes-ne servir l'estructura) |
| `game/test/partida.ts`, `game/test/acte*.test.ts` | Com es juga el joc sencer en un test |

```
game/                     EL JOC: data/ (JSON), locales/ca/ (textos), logic/ (regles en TS), test/
packages/narrative-core/  MOTOR NARRATIU: estat, condicions, diàlegs, memòria, missions, pistes, finals
adapters/benne/           L'ÚNICA PEÇA QUE CONEIX BENNE: pont, sync, art provisional
ferro-9/                  El projecte Benne (motor, art i el que genera el sync)
tools/                    validate, jugar (mode text), fitxes, schemas, sons, musica, font
```

### Com començar el repositori nou

Crea un **repositori nou** (no una carpeta dins de Ferro-9) i copia-hi:

- **Tal qual:** `packages/narrative-core/`, `tools/*.ts`, `tools/sons.py`, `tools/musica.py`,
  `tsconfig.json`, `vitest.config.ts`, `package.json` (canvia'n el nom), `.gitignore`.
- **Copia i neteja:** `adapters/benne/`. Hi ha coses de Ferro-9 que s'han de treure o fer configurables:
  - `create-project.ts` i `sync.ts`: el nom per defecte del projecte (`ferro-9`, `ferro9-benne`, `Ferro-9`).
  - `benne-content.ts`: els colors dels personatges i la font `ferro-negreta`.
  - `runtime/narrative.ts`: els missatges `[Ferro-9]` de la consola.
  - `tools/room_designs.py`, `tools/hd/rooms/*`, `tools/hd/characters.py`, `placeholder-art/`: són l'art
    de Ferro-9. **Conserva'n les llibreries** (`hd/pix.py`, `hd/render.py`, `escala.py`,
    `draw_placeholders.py`) i esborra les sales i els personatges.
  - El botó «Canvia» i tot el que és de **dues protagonistes**: si el joc nou en té una sola, el nucli
    ho suporta igual (`protagonists` amb un sol element), però revisa que el botó no surti.
- **No copiïs:** `game/data`, `game/locales`, `game/logic/finestra.ts` (la finestra de fase és una regla
  de Ferro-9; la nova història tindrà les seves en `game/logic/`), `guio/`, `ferro-9/`.
- **La font**: `tools/font/` genera la font pròpia Ferro (amb tots els caràcters catalans). Es pot
  reaprofitar o fer-ne una de nova amb el mateix generador; **no facis servir fonts amb llicència no
  comercial** (a Ferro-9 les vam haver de substituir al final).
- **Llicències**: copia el patró de `LLICENCIES.txt` (joc amb tots els drets reservats + avisos MIT de
  Benne i Phaser) des del principi.

Després: `npm run benne:create -- --from <checkout de Benne>` per crear el projecte Benne nou, i
`npm run benne:sync -- --init`. Guarda el `package-lock.json` del projecte Benne al repositori.

Fes que `npm test`, `npm run validate` i `npm run typecheck` passin amb un contingut mínim (una sala, un
objecte, un final) **abans d'escriure la història**. Primer commit.

---

## 2. Decisions que s'han de prendre el primer dia

A Ferro-9 algunes es van decidir tard i van costar caríssim. Pregunta-les a l'usuari abans de dibuixar res:

1. **Resolució.** Ferro-9 va començar a 352×198 i es va passar a **480×270** a mitja feina: va caldre un
   script de migració (`migra_resolucio.py`), reescalar partides desades i redibuixar-ho tot. **Fixa
   480×270 des del primer dia** si no hi ha cap motiu per a una altra.
2. **Direcció d'art**: estil, paleta, mida dels personatges en píxels. Vegeu la secció 6.
3. **Quantes protagonistes** i si es canvia entre elles.
4. **Idiomes.** Les opcions de diàleg de Benne són estàtiques (una compilació per idioma).
5. **To i públic** (a Ferro-9: adolescents i adults, humor de personatges, cap atzucac, cap derrota).
6. **Títol** i nom del projecte Benne.

---

## 3. Fase 1: afinar el guió (abans de tocar cap JSON)

Ferro-9 va escriure el guió, el va implementar per actes i el va **corregir jugant**. Hi ha uns 25 commits
de «coherència» que es podien haver evitat amb una revisió prèvia (vegeu la secció 4). Aquesta vegada,
el guió s'ha de revisar **abans** d'implementar.

### 3.1 Converteix el `.txt` en `guio/guio.md`

Amb la mateixa estructura que `guio/guio.md` de Ferro-9:

- Premissa, lema i to
- Protagonistes (qui és, què vol, què necessita, arc, com juga) i secundaris (taula: per a què serveix
  cada un)
- Regles del món (les mecàniques pròpies, explicades com a regles, amb els seus límits)
- Estructura per actes, amb pròleg, i cada trencaclosques pas a pas
- Finals (taula: què passa i què cal), missions secundàries, sistema de pistes
- **Mapa de dependències** (què desbloqueja què)
- **Com encaixa amb el motor** (quins flags, vars, fets de memòria, missions)
- Decisions preses i preguntes obertes

**Detecta i pregunta** el que el `.txt` no resol. A Ferro-9 vam fer servir una llista de preguntes
obertes amb la resposta al costat (`-> passat retrofuturista inventat`): funciona bé.

### 3.2 Afegeix al guió tres taules noves (no les teníem i ens van faltar)

**a) Línia de temps del coneixement.** Per a cada protagonista i personatge important: què sap a cada
moment de la història. Columnes: el fet, qui l'aprèn, en quin pas (flag que ho marca).

> Errors de Ferro-9 que això hauria evitat: l'Iri parlava de «la V.» abans de saber que existia; deia
> «ja sé qui» sense haver vist els plànols; llegir la pròpia nota comptava com a descobriment; la Vet
> parlava del diapasó com «la molla de la V.» quan era seu.

**b) Presència dels personatges.** On és cada personatge a cada fase (i quan marxa i torna).

> Errors de Ferro-9: el panell continuava responent amb frases de la Directora quan ja havia marxat; fora
> de la cel·la, la Vet deia que la Directora la vigilava; el despatx del director s'havia de poder obrir
> només quan el director no hi era, i la pista de l'expedient sortia abans d'hora.

**c) Estats de cada objecte i cosa de la sala.** Per a cada cosa: els estats que té (tancat, obert,
reparat, buit...), què el fa canviar, **com es veu** a cada estat i **què se'n diu** a cada estat, per a
cada protagonista que la pot mirar.

> Errors de Ferro-9: la llitera havia d'insinuar les molles només després de sentir el pany sònic; la
> porta de la cel·la havia de quedar oberta després de l'imant; l'Iri podia enviar l'imant quan la Vet
> ja era fora; i van faltar dibuixos d'estats (palanca baixada, alarma apagada, panell sincronitzat, foto
> amb forat, comporta tancada) que es van haver d'afegir al final.

Aquesta taula c) és també **la llista de l'art** (secció 6) i dels **sons** (secció 7).

### 3.3 Escriu el guió de cada escena amb les marques de so

A cada línia on passa una acció que sona, marca-ho **a la línia exacta**: `[SO: segell]`. Vegeu la secció 7.

---

## 4. Fase 2: revisió de coherència (obligatòria abans d'implementar cada acte)

Fes una revisió **adversarial** del guió de l'acte: intenta trencar-lo com ho faria un jugador. Pots fer-la
amb un subagent que només tingui el guió i aquesta llista. Per cada problema, proposa el canvi al guió.

**Llista de comprovació** (sortida dels errors de Ferro-9):

1. **Coneixement:** cap línia diu una cosa que el personatge encara no sap (taula 3.2a). Mira especialment
   els `look` d'objectes i les frases per defecte, que es poden dir en qualsevol moment.
2. **Ordre lliure:** si dos trencaclosques es poden fer en qualsevol ordre, comprova els textos en tots dos
   ordres. Si una cosa ja s'ha fet, les altres no en poden parlar com si estigués pendent.
3. **Qui mira:** cada objecte que poden tenir totes dues protagonistes té un `look` per a cada una (amb
   la seva veu i el que sap). Un objecte que va passar d'una a l'altra en parla com a propi o no?
4. **Després de fer-ho:** cada acció que es pot repetir té una resposta per a «ja està fet». Cada objecte
   enviat, gastat o donat ja no apareix a les línies que el donaven per present.
5. **Personatges absents:** cap frase, pista o resposta d'un personatge que no hi és (taula 3.2b).
6. **Pistes:** cap pista apunta a un trencaclosques que encara no està obert, ni a un objecte inaccessible,
   ni a una persona absent. Cada pista té una condició de final (`doneWhen`).
7. **Atzucacs:** no hi ha cap manera de quedar encallat (objecte gastat que calia després, porta tancada
   sense tornada, diàleg que es tanca sense donar l'objecte). Una petició sense resposta («torna'm la clau
   anglesa») també és un forat.
8. **La mecànica pròpia:** les regles del món tenen límits clars, i el joc reacciona quan el jugador
   prova coses fora del camí (a Ferro-9: «només passa per la finestra el que l'altra necessita»; la resta
   provoca una frase, no un error).
9. **Motivació:** el jugador sap per què fa cada pas. La protagonista ho pensa en veu alta en el moment
   que toca (a Ferro-9: en arreglar el panell, la Vet pensa a enviar un missatge i explica per què; en
   mirar el pany, hi llegeix «Aldaia» i pensa que l'Iri el podria obrir).
10. **Noms:** decideix els noms abans d'implementar. Canviar-los després (en Bruc → en Mos, La Gavina →
    Orís → La Gavina) toca guió, contingut, art i projecte Benne alhora.
11. **Gramàtica dels textos amb variables:** els objectes que surten dins de frases fetes necessiten
    article (`obj.<id>.amb_article`: «la molla», «l'imant»).

---

## 5. Fase 3: implementar per actes

L'ordre que va funcionar a Ferro-9, i que cal mantenir:

1. **Contingut en JSON** (`game/data/`, `game/locales/ca/`) segons `docs/guia-contingut.md`.
   `npm run validate` després de cada canvi.
2. **Jugar en mode text** (`npm run jugar`) abans de passar a Benne. És molt més ràpid per trobar forats.
3. **Test de l'acte sencer** (`game/test/acteN.test.ts`) per **tots els camins** importants (cada ordre
   possible dels trencaclosques, cada final), amb `checkHints` perquè a cada pas hi hagi alguna pista.
4. **Test per a cada error de coherència** que trobis: que una clau de text **no** surti abans d'un flag
   (com fa `acte1.test.ts` amb «la V.»). Així no torna.
5. **Sync a Benne** (`npm run benne:sync`) i jugar al navegador.
6. Fitxes de sales (`npm run fitxes`) per saber què cal dibuixar i lligar a l'editor.

### Condicions: com fer que els textos canviïn segons el que ha passat

És el punt que més feina de retoc va donar. Regles:

- **Una interacció per estat**, de la més concreta a la més general (s'agafa la primera que encaixa). La
  general del final és la de «sempre»; totes les altres porten `if`.
- Per a les coses que **es veuen** diferent segons l'estat: `decor` amb `visibleIf` (no dupliquis la cosa).
  Per a les que **apareixen o desapareixen**: `visibleIf` a la cosa.
- Els diàlegs comencen en un node o un altre amb `start` condicional; les opcions amb `if` i `once`.
- Per a la memòria dels personatges: `remember`/`remembers` i `relation`, no flags globals.
- Els objectes de l'inventari també tenen `interactions` amb `if` (p. ex. `look` diferent per protagonista
  o abans/després d'un fet).

**Eina que convé fer al principi** (a Ferro-9 no la teníem): una ordre `npm run revisio` que, per a cada
cosa de cada sala i cada objecte, llisti **totes les variants de text amb la seva condició**, en text pla.
Es llegeix com un guió i és on es veuen els forats de coherència sense haver de jugar.

---

## 6. Art: provisional i després definitiu?

**Sí, però amb regles.** A Ferro-9 vam fer: caixes etiquetades → pixel art provisional generat amb Python →
pixel art HD redibuixat sencer. El que va anar bé és que **la geometria** (on és cada cosa clicable, on es
camina, on és cada personatge) es definia a part del dibuix i no va canviar en redibuixar. El que va anar
malament és el canvi de resolució a mitja feina i els estats que faltaven.

La recomanació per al joc nou:

1. **Fixa resolució, escala i mides** el primer dia (secció 2): alçada dels personatges, mida de les
   icones, paleta. Escriu-ho al README.
2. **Fes una sala de mostra amb l'art definitiu** al principi (la primera del joc), amb un personatge i
   unes icones. Serveix de guia d'estil, i comprova aviat els límits tècnics.
3. **Les altres sales, provisionals**, però amb **la geometria definitiva** i **tots els estats dibuixats**
   (taula 3.2c), encara que siguin esquemàtics. Un estat sense dibuix és un error de joc, no d'art.
4. L'art definitiu es fa **per actes**, quan el guió de l'acte ja està tancat i jugat. Mai abans:
   redibuixar per canvis de guió és la feina més cara.
5. La marca `.provisional` diu al sync què pot tornar a dibuixar. Quan una sala sigui definitiva, esborra-la.

Límits tècnics que ja coneixem:
- **Cap full de sprites més ample o alt de 4096 px**: el fons surt negre. Les sales animades es posen
  en graella (`draw_placeholders.py` ja ho fa).
- Les animacions de fons es desen a la memòria cau (`hd/.cache`) perquè el sync no les torni a renderitzar.
- Les fonts de mapa de bits només es veuen nítides a múltiples enters de la mida original.

---

## 7. So i música

A Ferro-9, primer el joc i després els efectes i la música: **és l'ordre correcte, mantén-lo**. Els sons
i la música es generen (`npm run sons`, `npm run musica`) i el sync els copia a Benne.

El problema que queda: **alguns efectes no quadren amb el diàleg**. El so sona **quan comença la línia**
que el porta (`"sound"` a la línia). Si el poses a la línia que *comenta* l'acció en lloc de la que la
*fa*, sona tard o d'hora (exemple: el segell sonava una línia després de les rialles del capatàs; es va
haver de moure a la línia anterior, commit `e04f32a`).

Regles per al joc nou:

1. **El so va a la línia en què passa l'acció**, no a la reacció. Si una línia descriu l'acció i la
   reacció alhora, parteix-la en dues.
2. Marca els sons al guió (`[SO: nom]`, secció 3.3), i que la marca passi tal qual al JSON.
3. **Fes que el mode text escrigui els sons** (`npm run jugar` encara no ho fa): `[so: segell]` abans de la
   línia. Així es revisa el ritme llegint, sense navegador.
4. El so ha de durar el que dura l'acció. Un so llarg amb una línia curta trepitja la línia següent.
5. Un test pot comprovar que tots els `sound` existeixen (`game/test/sons.test.ts` ja ho fa).

---

## 8. El que ha anat bé i cal repetir

- **Caminar abans d'actuar.** El pont fa que la protagonista vagi caminant fins a la cosa i s'hi giri
  abans de qualsevol acció (commits `9b11c2e`, `47c0e46`). Ja és a `adapters/benne/runtime/`: conserva-ho.
  (Nota: `walkToClicked()` no funciona als *fallbacks* de Benne; per això el pont camina fins a la cosa
  pel seu nom.)
- **Presentació**: portada (sala de `cover` amb «Comença» i «Carrega una partida»), pròleg com a
  seqüència de cinemàtiques sobre negre, i títols d'acte («Acte 1 · La descoberta») amb línies `title`.
- **Finals**: títol, escena amb línies condicionals (`if`) que expliquen què ha passat segons la partida,
  i pantalles amb imatge i animació de fons. Que tots els finals siguin la mateixa història amb més o menys
  coses arreglades fa que el jugador entengui què li ha faltat.
- **Cap atzucac i cap derrota**; si alguna cosa surt malament, es torna a provar el pas.
- **Pistes en tres nivells** (vaga, concreta, gairebé la solució), dites per la protagonista com si pensés
  en veu alta, i el test que comprova que a cada pas n'hi ha alguna.
- **Missions secundàries que canvien el final**.
- **El mode text i els tests de partida sencera**: van trobar la majoria d'errors abans d'obrir el navegador.

---

## 9. Errors tècnics de Benne que ja estan resolts al pont

No els tornis a trobar: si toques el pont, recorda-ho.

- El plugin BenneScript fa asíncrones **totes** les funcions d'un `*.script.ts`. Les funcions que han de
  retornar un valor al moment van a `narrative.ts`, no a `narrative.script.ts` (`cfd0233`).
- En carregar una partida, Benne avisa del canvi de sala i d'inventari **abans** de `gameState:replaced`.
  El pont adopta primer l'estat narratiu de la partida (`7234463`, `0556e1a`).
- Les zones (hotspots) de Benne amb `visibleIf` també s'han d'amagar, no només els props (`6376a74`).
- Partida nova: cal repartir els objectes inicials explícitament (`d6bb60c`).
- `player.switchTo` només funciona amb personatges de la mateixa sala: cada sala és d'una protagonista.

---

## 10. Pla de feina proposat

1. Repositori nou amb les capes reaprofitades, un contingut mínim i els tests en verd. *Commit.*
2. Decisions de la secció 2 (pregunta-les).
3. `guio/guio.md` a partir del `.txt`, amb les tres taules noves i les preguntes obertes. Revisa'l amb
   l'usuari.
4. Revisió de coherència de tot el guió (secció 4). Revisa els canvis amb l'usuari. *Commit.*
5. Sala de mostra amb art definitiu (secció 6).
6. Per a cada acte: contingut → `npm run revisio` → mode text → tests de tots els camins → sync →
   navegador → art provisional amb tots els estats. *Commit a cada part.*
7. Portada, pròleg, títols d'acte i finals.
8. Art definitiu per actes.
9. Sons i música, amb la revisió del ritme en mode text (secció 7).
10. Partida completa al navegador per cada final; README i `docs/` al dia.
