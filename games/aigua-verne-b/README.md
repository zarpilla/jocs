# Aigua Verne B: sense barra de verbs (prova de concepte)

Una segona versió d'[Aigua Verne](../aigua-verne/README.md) per provar el camí **B · Modernitzar** de
[docs/aventures-cap-on-anem.html](../../docs/aventures-cap-on-anem.html): el mateix joc (contingut, trencaclosques,
art, textos), però sense barra de verbs i pensat per jugar-lo amb el dit en un mòbil apaïsat. Sense veus.
La versió original no es toca: aquesta és una còpia (del commit «pròleg animat a Terra-2»).

## Com es juga

| Gest | Què fa |
|---|---|
| Tocar (clic) una cosa | La primera vegada, mirar-la (la descripció, amb la pista). Després: si té una sola acció, la fa (obrir, agafar, parlar...); si en té més d'una, encara que alguna sigui una broma, obre el menú i tries tu. Les sortides no es miren: s'hi va |
| Mantenir premut (o clic dret) | El menú d'accions: «Mira» i les accions que té ara mateix (2–3 opcions) |
| Tocar el terra | Caminar |
| Bossa (a baix a la dreta) | Desplega la safata de l'inventari |
| Tocar un objecte de la safata | El pren a la mà («Usa X amb...»); tocar una cosa l'hi fa servir, o li dona si és un personatge. Tocar el terra o el mateix objecte, el deixa |
| Radar (a baix a l'esquerra) | Marca un moment tot el que es pot tocar (al mòbil no hi ha «passar per sobre») |
| La cara (a dalt a l'esquerra), el menú (a dalt a la dreta) | Canviar de protagonista; desar, carregar, opcions, pista, historial |

L'acció principal es decideix en el moment, a partir del JSON de sempre ([adapters/benne/runtime/accions.ts](adapters/benne/runtime/accions.ts)):
dels verbs que tenen una interacció que encaixa ara mateix, els que porten a la mateixa interacció compten com una sola
acció; la que canvia alguna cosa (efectes, diàleg, canvi de sala) passa davant de la que només diu una frase, i entre
iguals mana l'ordre anar-hi, parlar, agafar, obrir, tancar, empènyer, estirar, fer servir. El contingut no ha canviat.

## Què ha calgut

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
  (art i `.gui.json`), i els scripts `guis/verbs/verbs.gui.ts` i `guis/accions/accions.gui.ts` del projecte Benne.
  La GUI del HUD es diu `verbs` perquè el pont compartit la mostra, l'amaga i hi busca el botó «Canvia».
- **Dos verbs de la interfície**, `toca` i `accions`, que no surten mai al contingut ([adapters/benne/joc.ts](adapters/benne/joc.ts)),
  i el runtime que els resol: [runtime/tactil.ts](adapters/benne/runtime/tactil.ts) i
  [runtime/tactil.script.ts](adapters/benne/runtime/tactil.script.ts), enganxat al pont amb `setTouchRouter` (globalScript.ts).
- **Canvis compartits**, opcionals (els altres jocs no canvien de comportament):
  - motor: `inputProfile.holdVerb` / `holdMs` (mantenir premut, `engine/verbs/holdGesture.ts`), un verb d'objecte com a
    botó principal fa «Usa X amb...» quan hi ha un objecte a la mà, `game.showClickables()` (els marcadors), l'alçada
    adaptable (`resolution.minHeight`, `anchorY` a les GUI, `viewAnchorY` a les sales) i `pointer.screen` /
    `game.screenSize`;
  - nucli: `Narrative.peek(req)`, la interacció que faria una petició sense fer-la;
  - pont: `setTouchRouter` i `performInteraction` (adapters/benne/runtime).

## Resultat de la prova

`game/test/tactil.test.ts` juga la partida sencera (els dos camins de `cami.ts`) amb el mesurador de
`game/test/tactil.ts`, que mira què hauria fet el jugador a cada pas (`TACTIL=1 npm test` en fa la llista). El
mesurador només fa servir el nucli: s'ha passat també pels altres jocs.

Regla del toc: la primera vegada mira; després, una sola acció la fa i més d'una obre el menú (`queFaElToc`,
[runtime/accions.ts](adapters/benne/runtime/accions.ts)). Així el joc no tria per tu el verb que resol un trencaclosques
(empènyer o estirar), i les descripcions es llegeixen sense gestos de més.

| Joc | Passos | Un toc | Toc + menú | Mantenir premut | Toc de més (mira primer) | Gestos per pas |
|---|---|---|---|---|---|---|
| Aigua Verne (barril) | 163 | 163 | 0 | 0 | 27 | 1,17 |
| Suma Zero | 66 | 61 | 5 | 0 | 20 | 1,38 |
| Ni un ou | 106 | 102 | 3 | 1 | 12 | 1,15 |
| Ferro-9 | 149 | 136 | 13 | 0 | 15 | 1,19 |

A Aigua Verne cap cosa del camí té dues accions diferents: el contingut ja agrupa els verbs en una sola interacció
(`["walkTo", "use", "open"]`). Al Ferro-9, el menú surt just on el verb és el trencaclosques (el panell, la molla, la
llançadora, el conducte, la reixa).

## Ordres

```bash
npm test                                   # (des de l'arrel) inclou tactil.test.ts
python3 adapters/benne/tools/hd640/hud.py          # torna a fer el HUD i el menú d'accions
python3 adapters/benne/tools/hd640/pantalla.py     # càmeres de les sales i GUI per a la pantalla adaptable (es pot repetir)
cd aigua-verne && npm run dev -- --host            # al navegador, i des del mòbil a la mateixa xarxa
```

Compte: `hd640/gui_rest.py` torna a fer la barra de verbs; en aquesta versió no s'ha d'executar (o cal tornar a passar
`hud.py` i `pantalla.py` després). Les partides desades no es barregen amb les de l'original (`aigua-verne-b-benne`).
No es publica (no és a `publica.yml`).

---

Aventura gràfica de «point & click» feta amb [Benne](https://benne.games/): una comèdia espacial al sistema de
**Vesper**. L'aigua no s'ha acabat: el Magnat **Aurelià Verne** la bomba cap a tres dipòsits en òrbita i la torna a
vendre gota a gota. L'**Iri** (la pilot) i la **Vet** (l'enginyera), germanes d'acollida, només volen el pou de la
granja del pare. Per tenir-lo hauran d'obrir els dipòsits el dia que el Magnat s'ho juga tot.

Guió: [guio/guio.md](guio/guio.md). Fitxes de les sales (el contracte entre el contingut i l'art):
[guio/fitxes-sales.md](guio/fitxes-sales.md). Art de mostra: [guio/art/mostra/](guio/art/mostra/).

> Aquest joc és dins del repositori dels jocs de Mala Herba Soft. El nucli narratiu, l'adaptador de Benne, el motor i
> les eines són a l'arrel i els comparteixen tots els jocs (vegeu el [README de l'arrel](../../README.md)).

## Com és

| Què | Com |
|---|---|
| Estructura | Pròleg, 3 actes i 8 escenes, un final amb variacions (l'últim barril, les respostes a la Juana) |
| Protagonistes | L'Iri i la Vet, amb canvi lliure; les sales són compartides |
| Viatges | La Cantimplora: el mapa del pont (només el fa servir l'Iri) porta a qualsevol planeta obert; alguns trencaclosques demanen tornar a un planeta |
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
