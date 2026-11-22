# Guia: d'una idea a un joc publicat

Tot el que cal per fer un joc nou de Mala Herba Soft, en l'ordre en què s'ha fet amb els cinc jocs que tenim. Cada fase
acaba amb una **llista de comprovació**. Els detalls són a les altres guies, i aquí només s'hi enllacen:

- [Guia per escriure contingut](guia-contingut.md): el JSON del joc (sales, diàlegs, pistes, finals).
- [Guia d'art: sales amb profunditat](guia-art-profunditat.md): càmera, llum, personatges dins la sala, cinemàtiques.
- [README de l'arrel](../README.md), [adaptador de Benne](../adapters/benne/README.md) i
  [Benne per dins](benne-per-dins.html): l'estructura i les ordres.
- Un pla de feina real: [guio/pla.md de L'Última Arrel](../games/ultima-arrel/guio/pla.md).

Les ordres d'un joc s'executen des de `games/<joc>/` (o des de l'arrel amb `-w <joc>`).

## Resum

| Fase | Què en surt | Qui ho revisa |
|---|---|---|
| 0. La idea i les decisions | Un `guio/pla.md` amb les decisions preses | L'usuari |
| 1. Esquelet | `games/<joc>/` que compila i s'obre al navegador | — |
| 2. Guió | `guio/guio.md` | **L'usuari, abans de seguir** |
| 3. Fitxes de les sales | `guio/fitxes-sales.md` | — |
| 4. Contingut jugable en text | `game/data`, `locales/ca`, tests de partida | — |
| 5. Mecànica nova (si n'hi ha) | Provada al navegador amb art provisional | L'usuari |
| 6. Art provisional | Joc sencer jugable al navegador | — |
| 7. Revisió de coherència, pistes i humor | Textos i pistes corregits, frases per defecte, gags | L'usuari, jugant-hi |
| 8. Personatges definitius | Fulls a 1×, en 3/4 | L'usuari |
| 9. Sales definitives | Una sala de mostra, i després totes | **L'usuari, la de mostra** |
| 10. Portada, pròleg, cinemàtiques, finals | La pantalla de títol animada i els crèdits | L'usuari |
| 11. Detalls d'acabat | Ombres, llum, reflexos, respiració, ulls | — |
| 12. Música, sons i font | `game/audio/`, la font del títol | L'usuari, escoltant-ho |
| 13. Jugar-hi | Partides senceres al mòbil i a l'ordinador | L'usuari |
| 14. Publicació | `malaherbasoft.cat/<joc>/` | — |
| 15. A la web pública | Fitxa, portada, captures i full de sales | L'usuari |
| 16. Estadístiques i README | El joc compta i surt a les llistes | — |

---

## 0. La idea i les decisions

Abans d'escriure res, cal decidir el que condiciona tota la resta, i deixar-ho escrit a `guio/pla.md` (amb la data).

- **Títol, premissa i lema** d'una línia (el lema surt a la web).
- **Públic, durada i dificultat.** A L'Última Arrel: nenes de 8 a 12 anys, 45-60 minuts, 2-3 objectius alhora, cap
  atzucac. Els altres: a partir de 12 anys, 2-3 hores.
- **Idioma.** Fins ara, només català.
- **Les protagonistes.** Sempre la Iri i la Vet, **amb la cara de Suma Zero**; la feina, el rol, l'edat, la roba i el
  pentinat són nous a cada joc i han de servir la història.
- **Com es reparteixen:** canvi lliure (Aigua Verne), per escenes sense canvi (L'Última Arrel), separades en el
  temps (Ferro-9). Com es comuniquen i si es passen objectes.
- **Interfície:** sense barra de verbs i tàctil (`tactil: true`, el camí per defecte) o amb barra (només Ferro-9).
- **Estructura:** pròleg, actes (les missions s'han de dir `acte1`, `acte2`…), escenes, sales, finals.
- **Mecànica nova**, si n'hi ha (la lupa amb filaments de L'Última Arrel, les sincronies d'Aigua Verne). Si n'hi ha,
  s'ha de provar abans que l'art (fase 5).
- **Direcció d'art:** paleta, llum, càmera, mida dels personatges, i imatges de referència a `guio/art/referencia/`
  (què se n'agafa i què no).
- **To:** les regles de la casa (l'humor ve de les coses; ningú no diu més de tres línies seguides sobre el sistema; la
  crítica és a les coses, no als discursos).

- [ ] `guio/pla.md` amb les decisions i les preguntes obertes, revisat per l'usuari.

## 1. Esquelet

Com diu el [README de l'arrel](../README.md#un-joc-nou):

1. `games/<joc>/` amb `game/` (copiat d'un altre joc i buidat), `package.json` (com el dels altres, canviant el nom i
   la ruta de `test`, `dev`, `build` i `font`) i `adapters/benne/joc.ts` + `mapping.json`.
2. `npm run benne:create -w <joc> -- --from <checkout de Benne>`.
3. `npm run benne:sync -w <joc> -- --init`, i `npm install` dins `games/<joc>/<joc>/`.
4. `npm run dev -w <joc>`: s'ha d'obrir al navegador, encara que buit.

- [ ] `npm run validate`, `npm test` i `npm run typecheck` passen.
- [ ] El joc s'obre al navegador.

## 2. Guió (`guio/guio.md`)

Amb la mateixa estructura que el d'Aigua Verne: premissa i lema, to, protagonistes, secundaris, regles del món, les
escenes amb els diàlegs i els trencaclosques pas a pas, el sistema de pistes, el **mapa de dependències** (què cal
per a què), l'encaix amb el motor, l'abast i les preguntes obertes.

- [ ] Cada trencaclosques es pot resoldre amb el que hi ha a la sala o a l'inventari, i se sap per què.
- [ ] Cap atzucac: no es pot gastar ni perdre res que encara calgui.
- [ ] Cada protagonista té feina a cada acte (si es pot canviar).
- [ ] **Revisió de l'usuari abans de seguir.** A partir d'aquí, `guio.md` és la font de la veritat i `pla.md` queda
      com a historial.

## 3. Fitxes de les sales (`guio/fitxes-sales.md`)

El contracte entre el contingut i l'art: per a cada sala, la mida de la càmera (ampla amb scroll o no, de prop o de
lluny), les coses que s'hi toquen, els decorats que canvien amb l'estat, les sortides i on és cada personatge.

Quan ja hi ha contingut, `npm run fitxes` en genera la part mecànica (ids, condicions, verbs) a partir de
`game/data/`.

- [ ] Totes les sales del guió tenen fitxa, amb els ids que farà servir el contingut.

## 4. Contingut jugable en text

`game/data/` (sales, diàlegs, objectes, personatges, missions, pistes, finals) i `game/locales/ca/`, seguint la
[guia de contingut](guia-contingut.md). Per escriure de pressa, la clau i el text alhora (`"clau=Text"`) i després
`npm run textos`.

Les regles que no caben al JSON van a `game/logic/` (vegeu les d'Aigua Verne al seu README).

**Tests** a `game/test/` (copiar-los d'Aigua Verne o de L'Última Arrel i adaptar-los):

| Fitxer | Què comprova |
|---|---|
| `cami.ts` + `partida.test.ts` | La partida sencera, per tots els camins, i que hi ha **una pista a cada pas** |
| `tactil.test.ts` | El mateix camí amb el dit i amb el ratolí (quants gestos per pas) |
| `explora.test.ts` | Una transcripció que ho mira tot a cada escena, per llegir-la com una jugadora |
| `situacions.test.ts`, `arreglos.test.ts` | Casos concrets que s'han trencat alguna vegada |

- [ ] `npm run validate` sense errors.
- [ ] `npm run jugar` (i `-- --tactil`): el joc sencer es pot acabar en mode text.
- [ ] `npm test` passa, amb tots els camins i tots els finals.
- [ ] Missions principals `acte1`, `acte2`, `acte3`… (les estadístiques les compten).

## 5. Mecànica nova (si n'hi ha)

Si el joc té una cosa que el motor o l'adaptador no fan, es fa **ara**, amb art provisional, i es prova al
navegador abans de dibuixar res. Si serveix per a tots els jocs, va a `adapters/benne/` o al motor (i
`npm run benne:pegat` torna a fer el pegat del motor i el comprova). Si és només d'aquest joc, a
`games/<joc>/adapters/benne/joc.ts`.

- [ ] Funciona al navegador, amb el dit i amb el ratolí.
- [ ] Els altres jocs no canvien de comportament (`npm test` de l'arrel).

## 6. Art provisional

`npm run benne:sync` porta el contingut al projecte Benne. Mentre no hi ha art de debò, les sales surten amb caixes
etiquetades o amb el disseny de `tools/room_designs.py`, i els personatges amb `draw_characters.py`
([escenes i personatges provisionals](../adapters/benne/README.md#escenes-provisionals)). Les icones de l'inventari,
amb `draw_items.py`.

Amb la interfície tàctil: `tools/hd640/hud.py` (HUD i menú d'accions) i `tools/hd640/pantalla.py` (càmeres i GUI per a la
pantalla adaptable, de 640×288 a 640×360).

- [ ] El joc sencer es pot jugar al navegador, de la portada al final.

## 7. Revisió de coherència, pistes i humor

És el pas que més s'oblida i el que més es nota. `npm run revisio` escriu `guio/revisio.md`: totes les variants de text
amb la seva condició, en l'ordre en què el motor les prova. Es llegeix com un guió, sense jugar.

Què s'hi busca (vegeu els commits de revisió de Suma Zero i de Ni un ou):

- [ ] Textos que no segueixen l'estat: una línia que es pot dir abans d'hora, un objecte que ja no hi és i encara es
      descriu, «ja està fet» sense resposta.
- [ ] Una interacció «SEMPRE» que no és l'última i amaga les de sota.
- [ ] Verbs equivalents que responen igual («donar» com «usar» amb un personatge).
- [ ] Les pistes: que surtin quan toca (`when`), que s'acabin quan toca (`doneWhen`), que sàpiguen **qui porta què**,
      que el nivell 1 no doni la solució, i que n'hi hagi a la veu de qui juga (o pel walkie, `who`).
- [ ] Sense pista per a qui juga: «li toca a l'altra» (`ui.pista.altra.<qui>`).
- [ ] Errates i frases que no s'entenen. Tot en un català natural (cap calc: «roba de feina», no «granota»).
- [ ] La transcripció d'`explora.test.ts`, llegida sencera.

### La revisió amb un agent d'IA, en iteracions

Sovint aquesta revisió la fa un agent d'IA (Claude Code): juga el joc i el llegeix sencer, apunta les incoherències,
les corregeix i hi torna. **Cal iterar fins que no trobi res important.** Una sola passada no n'hi ha prou: cada volta
n'ha trobat moltes, també després de passades que semblaven netes, perquè un canvi en destapa d'altres.

A cada volta, l'agent:

1. **Juga** el joc sencer en text (`npm run jugar`, i `-- --tactil`), pels diversos camins, demanant pistes a cada pas
   i mirant-ho tot a cada sala. També llegeix `guio/revisio.md` (`npm run revisio`) i la transcripció d'`explora`.
2. **Fa una llista** del que no lliga: textos que no segueixen l'estat, pistes que no surten, que diuen massa o que
   apunten on no toca, objectes que encara es descriuen quan ja no hi són, frases poc naturals, forats del guió.
3. **Corregeix** el que és clar i en fa un test (`situacions.test.ts`, `arreglos.test.ts`), perquè no torni.
4. **Ho torna a provar** des del principi: `npm run validate`, `npm test` i una altra volta sencera.

S'atura quan el que troba és molt menor o quan cal una **decisió important** que no li toca a ell: un canvi del guió,
un trencaclosques que no s'entén, un personatge que diu el contrari en dos llocs. Aquestes decisions les apunta i les
passa a l'usuari, en lloc de triar-ne una. Al final fa un resum del que ha canviat a cada volta, que va al missatge
del commit.

Es pot repetir després de cada canvi gros (l'art definitiu mou coses, els textos nous trenquen pistes) i abans de
publicar.

### L'humor: una passada pròpia

L'humor dels diàlegs surt sol en escriure el guió; el que s'oblida és el de tot el que la jugadora fa per provar. Les
receptes que han funcionat (vegeu la valoració dels jocs, `referencia/valoracio-jocs.md` al repo `malaherbasoft`, i
els commits d'humor de Ferro-9 i Ni un ou):

- [ ] **Les frases per defecte**, tres per verb i protagonista, que van per torns (vegeu la
      [guia de contingut](guia-contingut.md)). És la recepta que dona més per menys feina: surten a tota la partida.
- [ ] **Combinacions absurdes que es provaran segur** (l'objecte clau amb cada personatge, amb la cosa més grossa de
      la sala) amb una resposta pròpia, sense tocar el camí.
- [ ] **El que la premissa té de graciós, aprofitat fins al final.** A Ferro-9, els 120 anys entre les dues: l'argot
      de la Vet, el glossari de la Iri, el museu que interpreta malament les coses de la Iri. Cada joc en té un: cal
      trobar-lo al guió i comprovar que el joc el fa servir, no només que el promet.
- [ ] **Gags recurrents amb tornada i final**: dues o tres bromes que tornen en moments tranquils i es tanquen als
      crèdits o a l'epíleg (a Ni un ou, el «codi flam» del walkie, el gat sense polzes). Que el guió en tingui la llista.
- [ ] **On no n'hi ha:** cap broma als moments que han de pesar (una captura, la revelació, el final agredolç). En un
      thriller, l'humor és el descans, no l'acompanyament.
- [ ] Cap broma no dona una pista falsa ni canvia res de l'estat: les preguntes còmiques d'un diàleg, optatives i
      sense efectes.

## 8. Personatges definitius

A `adapters/benne/tools/hd/personatges.py` i `draw_characters.py` (vegeu
[els personatges dins la sala](guia-art-profunditat.md#els-personatges-dins-la-sala-amb-profunditat)).

- [ ] La Iri i la Vet amb la cara de sempre i silueta diferent l'una de l'altra (que es vegi a qui portes).
- [ ] Fulls a 1×, a la mida del joc (si són nenes, redibuixats, no reduïts).
- [ ] Vistes en 3/4 (`DL`, `UL`) per a qui camina, i passa de cara amb cuixa, genoll i canyella.
- [ ] Roba segons l'estat (`appearance` a `characters.json`) i, si cal, mida de lluny (`Lluny`).
- [ ] Llegibles a 640×360 (els petits, de prop, amb la silueta clara).
- [ ] Revisats per l'usuari sobre una sala abans de fer-los tots.

## 9. Sales definitives

Cada sala és un mòdul `adapters/benne/tools/hd640/rooms/<sala>.py` (fons, props, animacions i `GEOMETRIA`), amb peces
comunes a `*_comu.py`, dibuixat en 3D amb `hd640/tres_d.py` (`Escena`, `Llum`, `Camera`) seguint la
[guia de profunditat](guia-art-profunditat.md).

1. **Una sala de mostra** contra la referència, i l'**usuari la revisa** abans de fer les altres.
2. La resta. `python3 adapters/benne/tools/hd640/preview.py --res 640 <sala> <sortida>` en fa una previsualització.
3. Quan una sala és definitiva, se n'esborra la marca `.provisional`; per redibuixar-la després,
   `python3 redibuixa_sala.py <sala>` (des de `adapters/benne/tools/`).

Als scripts Python, `from pixels import nearest`, mai `resize(..., Image.NEAREST)` (el Pillow del sistema peta).

- [ ] Cada sala passa la [llista de comprovació de la guia de profunditat](guia-art-profunditat.md#llista-de-comprovació-per-a-una-sala-nova).
- [ ] El que es veu i el que es clica coincideixen (polígons, sortides, on camina).
- [ ] Els rètols que informen es llegeixen (grossos, en escorç).
- [ ] Les coses que canvien amb l'estat (decorats) es veuen en tots els estats.
- [ ] Al mòbil (640×288) no queda res important tapat pels botons de les cantonades.

## 10. Portada, pròleg, cinemàtiques i finals

Les cinemàtiques són on més es pot trencar la càmera fixa del joc. També són el primer que veu qui obre el joc, i
l'últim. Detalls: [pròleg i cinemàtiques](guia-contingut.md#pròleg-i-cinemàtiques) (el contingut),
[moviment a mitja escena](guia-contingut.md#moviment-a-mitja-escena-stage) (l'animació) i
[cinemàtiques](guia-art-profunditat.md#cinemàtiques) (l'art).

### Quines n'hi ha

Es decideixen al guió (fase 2), amb el text de cada pla. Als nostres jocs:

| Cinemàtica | Què fa | Exemples |
|---|---|---|
| **Portada** (`cover`) | La pantalla de títol, animada en bucle, amb «Comença» i «Carrega» | Totes |
| **Pròleg** (`intro`) | Planteja el conflicte abans de la primera sala; acaba amb el títol i «Acte 1» | `proleg_ginebra` (Suma Zero), `proleg_terra2` → `proleg_palau` (Aigua Verne) |
| **Entre actes o escenes** | Un salt de lloc o de temps, el dolent que mou fitxa | `muntatge` (Suma Zero), els pròlegs de la Gavina i de la cel·la (Ferro-9) |
| **Pantalles especials** | Una pantalla que no és una sala per caminar | `avio` (Suma Zero), `cantimplora_mapa` (Aigua Verne) |
| **Finals** | Un per final, amb el que ha passat segons la partida | `final_bar`, `final_palau`, `final_galway`, els sis de Ferro-9 |
| **Crèdits i postcrèdits** | Els noms, el «Fi» i, si n'hi ha, una última escena | `credits`, `postcredits` |

### Com es fa una cinemàtica

1. **El contingut.** Una sala de `game/data/rooms/` amb `"cutscene": { "skipTo": "<sala següent>" }` i un
   `onEnter` amb les línies, que acaba amb `goTo`. Línies especials:
   - `"who": "title"`: un rètol a pantalla (`joc.titol`, `acte.1`, «L'endemà al matí»);
   - `"who": "narrator"`: el narrador;
   - `stage` i `stageAfter` amb `"prop"`: una capa de l'art canvia d'animació (`anim`) o es mostra o s'amaga
     (`visible`), i `hold` espera aquells segons sense text mentre dura l'animació; `shake` sacseja la pantalla.
     Així anima la cinemàtica el contingut, i no cal codi. Vegeu el pròleg de Suma Zero
     (`games/suma-zero/game/data/rooms/proleg_ginebra.json`): el senyal va de l'antena a la torre, el pis es fon,
     la pantalla del BCMU entra, parla, talla i somriu.
2. **L'art.** Un mòdul `hd640/rooms/<sala>.py` com qualsevol sala. Cada cosa que s'anima és una capa (un prop) amb
   les seves animacions (`pis`, `pis_fon`, `pis_torna`…). Les capes quietes amb parallax i els llums que bateguen
   es fan per codi, sense dibuixar fotogrames.
3. **Portada i pròleg al mateix pla.** El títol és una capa a part (`titol`): «Comença» l'esvaeix i el pròleg
   comença sense tall, sobre el mateix dibuix (un `*_pla_comu.py` que comparteixen `portada.py` i el pròleg). Ho
   fan Suma Zero i Ni un ou.
4. **Els finals** són a `data/endings.json`: títol, escena (amb `if` segons la partida, p. ex. qui ha ajudat qui),
   text de tancament i crèdits. Cada línia pot dur `room` (una cinemàtica) per sortir damunt la imatge; sense, es
   llegeix sobre negre.
5. **La música:** el tema a la portada i al pròleg, i el final amb la seva peça (vegeu la fase 12).

### Llista de comprovació

- [ ] **Portada**: animada en bucle (parallax, llums que bateguen, algú que es mou), i que quedi bé **sense els
      botons**: serà la imatge de la web.
- [ ] **Pròleg** curt: en mig minut s'ha d'entendre el conflicte. Acaba amb el títol i «Acte 1».
- [ ] Totes es poden saltar (Esc → `skipTo`) i, saltant-les, la partida queda igual que mirant-les (els efectes
      d'estat no poden dependre de veure-les senceres).
- [ ] Composició de cinema: contrast d'escala, 3/4 i no de perfil, línies que guien l'ull, barres negres (~24 px).
- [ ] Les animacions de les capes duren el que diu `hold`: ni es tallen ni es queden esperant.
- [ ] **Finals** amb títol, escena (amb `if`), text de tancament i **crèdits** («Una aventura gràfica feta amb males
      herbes - malaherbasoft.cat»), i postcrèdits si n'hi ha. Els tests arriben a tots els finals.
- [ ] Rètols de temps entre escenes si hi ha salts («L'endemà al matí»).
- [ ] Al full de sales (`npm run full-sales`) surten a «Pantalles»: si no hi surten, no tenen `cutscene`.

## 11. Detalls d'acabat

El que fa que una sala deixi de semblar una casa de nines i un personatge una estàtua de cartró. Gairebé tot és
configuració del motor més unes quantes etiquetes al full; és barat i es nota molt.

**Llum i ombres de la sala**

- [ ] Llum per cara dels volums (`Llum` de `tres_d.py`), bassals sota els llums, racons foscos (`foscor`).
- [ ] Ombres projectades en diagonal pel terra, que pugen per la paret.
- [ ] Una llum dominant per sala, coherent amb la finestra, el sol o el llum del sostre.
- [ ] Primer pla fosc, en silueta i tallat per la vora; el personatge pot passar per darrere d'alguna cosa
      (`FRONT`, `baseline`).

**Personatges dins la sala** (detall a la [guia de profunditat](guia-art-profunditat.md#els-personatges-dins-la-sala-amb-profunditat))

- [ ] **Ombra de contacte** (`characterShadow` de la sala), allargada i girada lluny de la llum dominant.
- [ ] **Reflex** al terra polit (`characterReflection`), on n'hi hagi.
- [ ] **Contorn selectiu** al sprite (`Fig.render` de `hd/characters.py`: la vora del costat, enfosquida), i cap
      halo de sala (`characterOutline`), ni clar ni fosc: el personatge es retalla amb l'ombra i la llum.
- [ ] **Llum de la sala** sobre els personatges (`characterLights`), a partir dels llums de l'escena.
- [ ] **Escala contínua** amb la profunditat (regió `scaleEnabled`), sense passar de ≈1,2 a prop (on es camina, no
      a la vora de la regió). La mida dels fulls, decidida abans de dibuixar les sales.
- [ ] `npm run profunditat` sense avisos: llum, ombra, escala, velocitat i capes de totes les sales jugables.
- [ ] **Respiració**: `Idle` de quatre fotogrames, la clariana del pit puja i baixa, a 650 ms (`respira`).
- [ ] **Parpelleig** (`Blink`, cada 2,5-5 s) i **mirar al voltant** (`Look`), a `idleActions` del
      `.character.json`, on es veu la cara (D, L, DL).
- [ ] Un **tic** propi d'algun personatge (tocar-se el cabell, creuar els braços), si val la pena.
- [ ] *Follow-through* en aturar-se (la trena, l'abric), si es fa `StopD`.
- [ ] Ningú quiet del tot; ningú no respira ni parpelleja alhora (el motor ja ho desfasa).
- [ ] La gent que seu, seu de debò; i millor drets o recolzats que asseguts sense motiu.

**Vida a la sala**

- [ ] Animacions barates per codi sobre capes quietes: el que sura es gronxa, els pilots bateguen, fum, pols en un
      feix de llum, aigua, núvols lents.
- [ ] Parallax a les sales amples amb scroll (`parallaxDepth`), i la càmera amb zona morta.
- [ ] Tint de la sala segons l'hora o el lloc, si cal.

## 12. Música, sons i font

- **Música:** `tools/musica.py` (`npm run musica`), tot sintetitzat amb numpy i ffmpeg. Com a Aigua Verne: un sol
  tema amb instruments diferents per lloc, totes les peces de la mateixa durada perquè s'encadenin al mateix punt
  (`sync`) i en bucle perfecte. Peces per a la portada, cada lloc, la tensió i el final.
- **Ambients i efectes:** `tools/sons.py` (`npm run sons`). Ambient per sala (vent, motor, bosc) i efectes a les
  línies (`"sound"`, també amb variables: `molla_{molla_tensio}`). Si hi ha `sons.test.ts`, comprova que tots els
  sons que s'esmenten existeixen.
- **Font del títol i de la interfície:** `tools/font/<joc>_font.py` (`npm run font`).
- **Veus (opcional):** amb ElevenLabs (`npm run veus`). Tot el procés és a la [guia de veus](guia-veus.md).

- [ ] Cada lloc té la seva peça, i el canvi de lloc no talla la música.
- [ ] Cada acció important té so (portes, objectes, màquines).
- [ ] Volums equilibrats entre peces i amb els efectes.
- [ ] Revisat per l'usuari escoltant-ho al navegador.

## 13. Jugar-hi

Els tests diuen que el joc es pot acabar; no diuen si és divertit ni si s'entén.

- [ ] Una partida sencera **a l'ordinador** (ratolí: esquerre mira, dret fa) i una **al mòbil apaïsat**
      (`npm run dev -- --host` des del projecte Benne, i el mòbil a la mateixa xarxa).
- [ ] Una partida demanant **només pistes**: totes porten a algun lloc.
- [ ] Desar, carregar i «Continua» a mitja partida, i que tot torni on era.
- [ ] Canviar la mida de la finestra a mitja sala (la pantalla adaptable).
- [ ] Mirar-ho tot a cada sala: cap «Això no funciona» on hi hauria d'haver una resposta.
- [ ] Si el públic ho permet, que hi jugui algú que no l'hagi vist mai. Apuntar on s'encalla.
- [ ] Cada cosa trobada → test a `situacions.test.ts` o `arreglos.test.ts`, i tornar a la fase 7.

## 14. Publicació

- [ ] `description` i `url` al bloc `benne` del `package.json` del projecte Benne (`games/<joc>/<joc>/`).
- [ ] `public/portada.png` al projecte Benne.
- [ ] El joc a [publica.yml](../.github/workflows/publica.yml): a la llista d'`options` i a la llista de `jocs` per
      defecte.
- [ ] La carpeta del joc a les exclusions del `rsync --delete` del `deploy.yml` del repo de la web.
- [ ] `LLICENCIES.txt` si fa servir res de fora (fonts, sons).
- [ ] Versió a la portada i al menú, si se'n porta (Ferro-9 0.9.0).
- [ ] Un push a `main` el publica a `malaherbasoft.cat/<joc>/`. Comprovar-hi que s'obre i es juga, també al mòbil.

## 15. A la web pública (repo `malaherbasoft`)

Tot el procés és a `eines/README.md` d'aquell repo. Amb el joc engegat en desenvolupament (`npx vite --port 518x`
dins `games/<joc>/<joc>/`):

| Imatge | Com | On |
|---|---|---|
| **Portada** (la pantalla de títol sense botons) | `node eines/portada.mjs <url> /tmp/<joc>-portada.png`, reduïda a 640×360 | `public/img/<joc>-portada.png` |
| **Captura 1 i 2** (una protagonista a la sala, de vegades dient una frase) | Una escena a `eines/escenes/<joc>-<sala>.json` i `node eines/grava.mjs <url> <escena> /tmp/<carpeta>`; se'n tria un fotograma i es redueix a 640×360 | `public/img/<joc>-joc.png`, `<joc>-joc2.png` |
| **Revisió de profunditat** (no fa cap imatge) | `npm run profunditat` des de `games/<joc>/` ([tools/profunditat.py](../tools/profunditat.py)): per a cada sala, la llum i l'ombra dels personatges, l'escala on es camina i les capes | la terminal |
| **Full de totes les sales** (només de referència) | `npm run full-sales` des de `games/<joc>/` ([tools/full_sales.py](../tools/full_sales.py)): les pantalles i les sales del projecte Benne, sense personatges | `referencia/<joc>-sales.png` |

A les reduccions, NEAREST (amb `pixels.nearest` si el Pillow del sistema peta).

- [ ] Les tres imatges de la fitxa (portada i dues captures) triades d'entre les sales que més expliquen el joc, i
      revisades per l'usuari. Si la frase de la captura és «Això no funciona», es torna a gravar.
- [ ] La fitxa a `public/index.html`: títol, lema, gènere («Comèdia espacial especulativa»), **durada**, **edat**,
      resolució, l'enllaç al joc, i un `alt` que descrigui cada imatge.
- [ ] Primer «properament», i l'enllaç quan ja es pugui jugar.

## 16. Estadístiques i llistes

- [ ] El joc a `JOCS` d'`api/compose.yaml` del repo de la web, i tornar a aixecar el contenidor (si no, el servidor
      en rebutja els esdeveniments).
- [ ] La fila del joc a la taula del [README de l'arrel](../README.md) i, si és sense barra, a la frase de la
      interfície tàctil.
- [ ] El `README.md` del joc: què té de propi, com es juga, les ordres i l'art.
- [ ] Si s'ha fet alguna cosa nova per a tots els jocs, a les guies (aquesta, la de contingut o la de profunditat) i
      al README de l'adaptador.
