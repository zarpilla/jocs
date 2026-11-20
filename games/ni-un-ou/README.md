# Ni un ou

Aventura gràfica de «point & click» feta amb [Benne](https://benne.games/): un thriller amb humor a bord de
l'**Arenga**, el vaixell més petit d'una ONG que mesura la salut de l'Atlàntic Nord. L'**Iri** (la maquinista) i la
**Vet** (la metgessa nova) descobreixen que les avaries són sabotatges, que algú de bord treballa per a la minera
Skarn, i que tot gira al voltant d'un pot de fang: la Mostra 7.

Guió: [guio/guio.md](guio/guio.md). Art de mostra (la guia d'estil): [guio/art/mostra/](guio/art/mostra/).

> Aquest joc és dins del repositori dels jocs de Mala Herba Soft. El nucli narratiu, l'adaptador de Benne, el motor i
> les eines són a l'arrel i els comparteixen tots els jocs (vegeu el [README de l'arrel](../../README.md)). Aquí hi ha
> el contingut (`game/`), el guió, l'art, la música i el projecte Benne (`ni-un-ou/`).

## Sense barra de verbs

Es juga sense barra de verbs, també amb el dit en un mòbil apaïsat (el camí **B · Modernitzar** de
[docs/aventures-cap-on-anem.html](../../docs/aventures-cap-on-anem.html)), amb la interfície tàctil compartida.

### Com es juga

| Gest | Què fa |
|---|---|
| Tocar una cosa (amb el dit) | La primera vegada (o quan té una descripció nova), mirar-la. Després: si té una sola acció, la fa; si en té més d'una, obre el menú i tries tu. Les sortides no es miren: s'hi va |
| Amb el ratolí: clic esquerre, clic dret | Per defecte, el clic esquerre mira (a les sortides, hi va) i el dret fa el mateix que el toc, però sense mirar primer (l'acció, o el menú si n'hi ha més d'una) |
| Mantenir premut (el dit o el botó esquerre) | El menú d'accions: «Mira» i les accions que té ara mateix |
| «Com es juga» | A Opcions → Controls, una targeta que ho explica, amb el dit o amb el ratolí segons l'aparell (amb el ratolí, s'hi pot triar què fa cada botó); l'última fila diu on es demana una pista (menú → «Pista»). No surt sola en començar |
| Opcions → «clic esquerre per fer» | Gira els botons del ratolí: l'esquerre fa i el dret mira. Es desa en aquell aparell |
| Tocar el terra | Caminar |
| Sac (a baix a la dreta) | Desplega la safata de l'inventari |
| Tocar un objecte de la safata | El plànol s'obre, el walkie truca, les notes i el quadern es miren (el contingut no els combina mai amb res). La resta es prenen a la mà («Usa X amb...»): tocar una cosa l'hi fa servir, o li dona si és un personatge |
| Sonar (a baix a l'esquerra) | Marca un moment tot el que es pot tocar |
| L'ull de bou (a dalt a l'esquerra), el menú (a dalt a la dreta) | Canviar de protagonista (s'hi veu la cara de l'altra); desar, carregar, opcions, pista, historial |

En una finestra d'ordinador o un monitor (si sota l'escena queden 56 px o més), la franja de sota és la planxa amb
tot el HUD i l'inventari sempre a la vista, com a les altres B.

### Què ha calgut

- **`tactil: true`** al joc.ts: el `benne:sync` hi posa el runtime, els scripts del HUD i del menú d'accions, els verbs
  de la interfície, l'alçada adaptable (de 640×288 a 640×360) i el `defaultVerb` dels objectes que es fan servir sols.
- **L'art del HUD i del menú**, amb l'estil de la barra (la planxa blau marí amb reblons, la corda trenada, el llautó,
  l'ull de bou): [tools/hd640/hud.py](adapters/benne/tools/hd640/hud.py), fet a partir del d'Aigua Verne.
- **La pantalla adaptable**: [tools/hd640/pantalla.py](adapters/benne/tools/hd640/pantalla.py). Hi ha coses per tocar
  arran de dalt (escotilles, escales): al mòbil la càmera es queda a dalt.
- **El plànol a 288 d'alt** ([tools/hd640/mapa.py](adapters/benne/tools/hd640/mapa.py)): la mateixa geometria que
  l'original, encongida en vertical per trams (les cobertes ≈0,8; els espais dels rètols es queden). En una pantalla més
  alta va centrat sobre el fons de la planxa.
- **Dos errors del plànol arreglats** (`runtime/mapa.ts`), que també té l'original amb el motor d'ara: canviava el text
  dels botons (el motor no ho permet, i el plànol no s'obria) i deia què es veu abans de mostrar-lo (en construir-se, la
  GUI ho mostrava tot: totes les sales ratllades i un punt de més).
- L'historial (`runtime/historial.ts`, i la GUI a joc.ts), a l'alçada mínima; els textos `ui.accio.*` i `ui.verb.*` de la
  interfície (game/locales/ca/interficie.json).

### Resultat

`game/test/tactil.test.ts` juga el joc sencer per dos camins amb el mesurador compartit (`TACTIL=1 npm test` en fa
la llista). Cap pas és impossible.

| Camí | Passos | Un toc | Toc + menú | Toc de més (mira primer) | Gestos per pas (dit) | Gestos per pas (ratolí) |
|---|---|---|---|---|---|---|
| Amb tots els aliats | 109 | 109 | 0 | 15 | 1,14 | 1,00 |
| Amb les frontisses de l'Iri | 110 | 109 | 1 | 17 | 1,16 | 1,01 |

Amb el ratolí no hi ha tocs de més per mirar: mirar és un clic (l'esquerre, per defecte), i fer, l'altre (mesurat amb els botons girats: el resultat és el mateix).

L'únic menú és el registre del rebost (s'hi pot fer més d'una cosa). És el joc que millor encaixa amb el toc.

### Ordres de la interfície tàctil

```bash
npm test                                           # (des de l'arrel) inclou tactil.test.ts
npm run benne:sync                                 # el contingut i la interfície tàctil al projecte Benne
python3 adapters/benne/tools/hd640/hud.py          # torna a fer el HUD i el menú d'accions
python3 adapters/benne/tools/hd640/mapa.py         # torna a fer el plànol (a 288)
python3 adapters/benne/tools/hd640/pantalla.py     # càmeres de les sales i GUI per a la pantalla adaptable (es pot repetir)
cd ni-un-ou && npm run dev -- --host               # al navegador, i des del mòbil a la mateixa xarxa
```

Compte: `hd640/gui_rest.py` torna a fer la barra de verbs; no s'ha d'executar (o cal tornar a passar
`hud.py` i `pantalla.py` després).

## Com és

| Què | Com |
|---|---|
| Estructura | Pròleg, 3 actes i 9 escenes, i 3 finals segons els aliats (la Capitana, el Marcel, la Nadia i en Bastida) |
| Protagonistes | L'Iri i la Vet, amb canvi lliure entre elles (menys a les escenes 2 i 4) |
| Sales | **Compartides**: totes dues hi poden ser alhora, es veuen i es poden donar coses (`"protagonists"` al JSON) |
| Comunicació | El walkie (que escolta algú) i, des de l'Escena 5, el tub de veu; el muntacàrregues passa objectes entre la cuina, el rebost i el pont |
| Sincronies | Per torns, com a Suma Zero: la ràdio (la paciència d'en Bastida) i el satèl·lit (el senyal que se'n va) |
| Resolució | 480×270; personatges de ≈83 px amb el sistema de figures de Suma Zero (`adapters/benne/tools/hd/`) |

## Regles en codi (`game/logic/`)

- `sincronia.ts`: els dos passos per torns. No compten mirar, caminar, parlar, el walkie, el quadern, el tub ni les
  respostes que no fan res.
- `muntacarregues.ts`: les tres parades i les safates (una variable per safata).
- `escenes.ts`: canvis d'escena automàtics quan es compleix una condició (el final de l'Escena 2).
- `donar.ts`: donar un objecte a l'altra protagonista quan són a la mateixa sala.
- `mapa.ts`: el plànol d'emergència (des de l'Escena 6): on es pot anar ara, i per on, amb les mateixes portes que
  caminant. La pantalla és la GUI `mapa` (`adapters/benne/tools/hd640/mapa.py` i `adapters/benne/runtime/mapa*.ts`).

## Ordres

```bash
npm run jugar          # juga en mode text
npm test               # tests: el joc sencer per tots els camins, amb una pista a cada pas
npm run validate       # comprova el contingut
npm run textos         # porta als locales els textos escrits al JSON com a "clau=Text"
npm run sons           # efectes de so (tools/sons.py)
npm run musica         # música (tools/musica.py)
npm run font           # la font del joc
npm run benne:sync     # porta el contingut al projecte Benne
npm run dev            # juga al navegador (cal `npm install` dins ni-un-ou/)
```

## Art

Cada sala és un mòdul `adapters/benne/tools/hd/rooms/<sala>.py` amb el dibuix i la seva geometria (`GEOMETRIA`: on
es clica, on es camina, on és cada personatge); `hd/rooms/arenga.py` té les rampes i les eines comunes, que vénen de
la sala de mostra. `python3 adapters/benne/tools/hd/render.py <sala> <carpeta>` en fa previsualitzacions.

Per veure una escena concreta sense jugar-la, en desenvolupament: `window.__aventura.provar(situació)` (vegeu
`adapters/benne/README.md`).
