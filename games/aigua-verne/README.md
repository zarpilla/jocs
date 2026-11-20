Aventura gràfica de «point & click» feta amb [Benne](https://benne.games/): una comèdia espacial al sistema de
**Vesper**. L'aigua no s'ha acabat: el Magnat **Aurelià Verne** la bomba cap a tres dipòsits en òrbita i la torna a
vendre gota a gota. L'**Iri** (la pilot) i la **Vet** (l'enginyera), germanes d'acollida, només volen el pou de la
granja del pare. Per tenir-lo hauran d'obrir els dipòsits el dia que el Magnat s'ho juga tot.

Guió: [guio/guio.md](guio/guio.md). Fitxes de les sales (el contracte entre el contingut i l'art):
[guio/fitxes-sales.md](guio/fitxes-sales.md). Art de mostra: [guio/art/mostra/](guio/art/mostra/).

> Aquest joc és dins del repositori dels jocs de Mala Herba Soft. El nucli narratiu, l'adaptador de Benne, el motor i
> les eines són a l'arrel i els comparteixen tots els jocs (vegeu el [README de l'arrel](../../README.md)).

## Sense barra de verbs

Es juga sense barra de verbs, també amb el dit en un mòbil apaïsat (el camí **B · Modernitzar** de
[docs/aventures-cap-on-anem.html](../../docs/aventures-cap-on-anem.html)). Va ser el primer joc a provar-ho, i
d'aquí va sortir la interfície tàctil compartida.

### Com es juga

| Gest | Què fa |
|---|---|
| Tocar una cosa (amb el dit) | La primera vegada, mirar-la (la descripció, amb la pista). Després: si té una sola acció, la fa (obrir, agafar, parlar...); si en té més d'una, encara que alguna sigui una broma, obre el menú i tries tu. Les sortides no es miren: s'hi va |
| Amb el ratolí: clic esquerre, clic dret | Per defecte, el clic esquerre mira (a les sortides, hi va) i el dret fa el mateix que el toc, però sense mirar primer (l'acció, o el menú si n'hi ha més d'una) |
| Mantenir premut (el dit o el botó esquerre) | El menú d'accions: «Mira» i les accions que té ara mateix (2–3 opcions) |
| «Com es juga» | Una targeta que ho explica, amb el dit o amb el ratolí segons l'aparell (amb el ratolí, s'hi pot triar què fa cada botó); l'última fila diu on es demana una pista (menú → «Pista»). Surt sola un cop a cada partida nova, quan s'acaba l'entrada i ja es pot jugar, i també s'obre a Opcions → Controls |
| Opcions → «clic esquerre per fer» | Gira els botons del ratolí: l'esquerre fa i el dret mira. Es desa en aquell aparell |
| Tocar el terra | Caminar |
| Bossa (a baix a la dreta) | Desplega la safata de l'inventari |
| Tocar un objecte de la safata | El pren a la mà («Usa X amb...»); tocar una cosa l'hi fa servir, o li dona si és un personatge. Tocar el terra o el mateix objecte, el deixa |
| Radar (a baix a l'esquerra) | Marca un moment tot el que es pot tocar (al mòbil no hi ha «passar per sobre») |
| La cara (a dalt a l'esquerra), el menú (a dalt a la dreta) | Canviar de protagonista; desar, carregar, opcions, pista, historial |

Què fa el toc es decideix en el moment, a partir del JSON de sempre (`queFaElToc`,
[adapters/benne/tactil/runtime/accions.ts](../../adapters/benne/tactil/runtime/accions.ts)): dels verbs que tenen una
interacció que encaixa ara mateix, els que porten a la mateixa interacció compten com una sola acció; si en queda una,
el toc la fa, i si en queden més, obre el menú. El que ja s'ha mirat es recorda (va amb la partida desada). El
contingut no ha canviat.

La interfície tàctil és compartida ([adapters/benne/tactil/](../../adapters/benne/tactil/index.ts)): la fa servir
qualsevol joc amb `tactil: true` al seu `joc.ts`, posant-hi l'art. [Suma Zero](../suma-zero/README.md) és el
segon.

### Què ha calgut

- **Pantalla que s'adapta a l'aparell**: de 640×288 en un mòbil (20:9) a 640×360 en un monitor (16:9), sense
  franges. L'alçada la tria el motor en arrencar (`resolution.minHeight`), i la torna a triar si la finestra canvia de
  forma (la sala es refà en un moment quiet, sense perdre res). Les GUI es dissenyen a 288 i s'enganxen a
  dalt, al mig o a baix (`anchorY`). [tools/hd640/pantalla.py](adapters/benne/tools/hd640/pantalla.py) prepara les GUI
  i la càmera de cada sala.
- **L'art no canvia.** El de les sales és pintat fins a y = 260 (la resta era sota la barra), i el HUD té dos modes
  (`guis/verbs/hud.ts`):
  - **mòbil** (pantalla baixa): l'escena ocupa gairebé tota la pantalla; els botons van a les cantonades, sobre l'escena,
    i la safata de l'inventari es desplega amb la bossa (i es plega sola quan prens un objecte a la mà);
  - **tauler** (si sota l'escena queden 56 px o més: una finestra de navegador a l'ordinador, que sol fer uns 320–340
    d'alt, o un monitor a pantalla completa): la franja de sota l'escena és un tauler de comandaments amb la frase,
    «Canvia», els punts, el menú i l'inventari sempre a la vista, en una fila de 6 o, des de 94 px (360 d'alt), en dues.
    Els diàlegs surten a la mateixa franja, i no tapen l'escena.
  El motor també permet pintar una sala fins a 360 i fixar-ne la càmera al mòbil (`viewAnchorY`), però sense coses
  per tocar a la part de baix no val la pena en aquest joc; en un de nou, seria primer pla decoratiu.
- **HUD i menú d'accions** nous, amb la planxa oliva de la barra: [tools/hd640/hud.py](adapters/benne/tools/hd640/hud.py)
  (art i `.gui.json`). Els scripts (`hud.ts`, `verbs.gui.ts`, `accions.gui.ts`) són compartits
  ([adapters/benne/tactil/guis/](../../adapters/benne/tactil/guis/verbs/hud.ts)) i el `benne:sync` els copia.
  La GUI del HUD es diu `verbs` perquè el pont compartit la mostra, l'amaga i hi busca el botó «Canvia».
- **Dos verbs de la interfície**, `toca` i `accions`, que no surten mai al contingut, i el runtime que els resol
  ([adapters/benne/tactil/runtime/](../../adapters/benne/tactil/runtime/tactil.ts)), enganxat al pont amb
  `setTouchRouter` (al bloc generat de globalScript.ts). Tot ho posa el `benne:sync` perquè
  [adapters/benne/joc.ts](adapters/benne/joc.ts) diu `tactil: true`.
- **Canvis compartits**, opcionals (els altres jocs no canvien de comportament):
  - motor: `inputProfile.holdVerb` / `holdMs` (mantenir premut, `engine/verbs/holdGesture.ts`), un verb d'objecte com a
    botó principal fa «Usa X amb...» quan hi ha un objecte a la mà, `game.showClickables()` (els marcadors), l'alçada
    adaptable (`resolution.minHeight`, `anchorY` a les GUI, `viewAnchorY` a les sales) i `pointer.screen` /
    `game.screenSize`;
  - nucli: `Narrative.peek(req)`, la interacció que faria una petició sense fer-la;
  - pont: `setTouchRouter` i `performInteraction` (adapters/benne/runtime).

### Resultat de la prova

`game/test/tactil.test.ts` juga la partida sencera (els dos camins de `cami.ts`) amb el mesurador compartit
([adapters/benne/tactil/mesura.ts](../../adapters/benne/tactil/mesura.ts)), que mira què hauria fet el jugador a cada pas (`TACTIL=1 npm test` en fa la llista). El
mesurador només fa servir el nucli: s'ha passat també pels altres jocs.

Regla del toc: la primera vegada mira; després, una sola acció la fa i més d'una obre el menú (`queFaElToc`). Així el joc no tria per tu el verb que resol un trencaclosques
(empènyer o estirar), i les descripcions es llegeixen sense gestos de més. A més (des de Ni un ou):

- es recorda quina **descripció** s'ha vist, no només la cosa: quan en té una de nova, el primer toc la torna a mirar;
- dos verbs que fan **exactament el mateix** (el walkie: «parla» i «fes servir» obren el mateix diàleg) són una sola
  acció;
- un **objecte que el contingut no combina mai amb res** (el plànol, el walkie) no es pren a la mà en tocar-lo a
  l'inventari: en fa l'acció (el sync li posa `defaultVerb: "fes"`). Els que es combinen es prenen a la mà, i per
  mirar-los cal mantenir premut.

| Joc | Passos | Un toc | Toc + menú | Mantenir premut | Toc de més (mira primer) | Gestos per pas (dit) | Gestos per pas (ratolí) |
|---|---|---|---|---|---|---|---|
| Aigua Verne (barril) | 171 | 171 | 0 | 0 | 29 | 1,17 | 1,00 |
| Suma Zero | 66 | 61 | 5 | 0 | 25 | 1,45 | 1,08 |
| Ni un ou | 109 | 109 | 0 | 0 | 15 | 1,14 | 1,00 |
| Ferro-9 (amb barra de verbs; mesura del 15-11-2026) | 149 | 134 | 11 | 4 | 22 | 1,25 | — |

Amb el ratolí (l'ordinador), un botó fa l'acció sense mirar primer i l'altre mira (per defecte, l'esquerre mira i el
dret fa): no hi ha tocs de més, i mirar és un gest quan el camí ho demana.

A Aigua Verne cap cosa del camí té dues accions diferents: el contingut ja agrupa els verbs en una sola interacció
(`["walkTo", "use", "open"]`). Al Ferro-9, el menú surt just on el verb és el trencaclosques (el panell, la molla, la
llançadora, el conducte, la reixa).

### Ordres de la interfície tàctil

```bash
npm test                                   # (des de l'arrel) inclou tactil.test.ts
python3 adapters/benne/tools/hd640/hud.py          # torna a fer el HUD i el menú d'accions
python3 adapters/benne/tools/hd640/pantalla.py     # càmeres de les sales i GUI per a la pantalla adaptable (es pot repetir)
cd aigua-verne && npm run dev -- --host            # al navegador, i des del mòbil a la mateixa xarxa
```

Compte: `hd640/gui_rest.py` torna a fer la barra de verbs; no s'ha d'executar (o cal tornar a passar
`hud.py` i `pantalla.py` després).

## Com és

| Què | Com |
|---|---|
| Estructura | Pròleg, 3 actes i 8 escenes, un final amb variacions (l'últim barril, les respostes a la Juana) |
| Protagonistes | L'Iri i la Vet, amb canvi lliure; les sales són compartides |
| Viatges | La Cantimplora: el mapa del pont (només el fa servir l'Iri) obre la carta de navegació, on es toca el planeta on es vol anar (només hi surt «Navega a...» si és obert) i la nau hi vola; alguns trencaclosques demanen tornar a un planeta |
| Comunicació | El comunicador de canell (repeteix què toca fer) i la Mosca, el dron que porta objectes a l'altra si són al mateix planeta |
| Sincronies | Per torns: la colada de les claus (la temperatura del forn) i la subhasta (els lots) |
| Resolució | 640×360, amb **dues mides de personatge**: ≈83 px a les sales de lluny i ≈100 px a les de prop (roba `Lluny` a `characters.json`) |

## Regles en codi (`game/logic/`)

- `sincronia.ts`: els dos passos per torns; els textos són a `sincronies.json`.
- `escenes.ts`: canvis d'escena automàtics; les transicions són a `transicions.json`.
- `mosca.ts`: la Mosca (mateix planeta, no al palau, `mosca: true` a items.json).
- `safata.ts`: la safata de les copes del palau, de l'Iri (saló) a la Vet (servei).
- `donar.ts`: donar un objecte a l'altra a la mateixa sala.

## Ordres

```bash
npm run jugar          # juga en mode text
npm test               # el joc sencer pels dos camins, amb una pista a cada pas
npm run validate       # comprova el contingut
npm run sons           # efectes de so (tools/sons.py)
npm run musica         # música (tools/musica.py)
npm run benne:sync     # porta el contingut i l'art al projecte Benne
npm run dev            # juga al navegador (cal `npm install` dins aigua-verne/)
```

## Art

Cada sala és un mòdul `adapters/benne/tools/hd640/rooms/<sala>.py` (fons, props, animacions i `GEOMETRIA`), amb peces
comunes per planeta (`*_comu.py`). Els personatges són a `adapters/benne/tools/hd/personatges.py` i els fulls els fa
`python3 adapters/benne/tools/draw_characters.py`. Les icones i la interfície, a `hd640/items.py`, `hd640/gui.py` i
`hd640/gui_rest.py`. `python3 adapters/benne/tools/hd640/preview.py --res 640 <sala> <sortida>` en fa una
previsualització.
