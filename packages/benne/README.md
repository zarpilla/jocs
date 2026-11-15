# El motor de Benne, compartit

El motor de [Benne](https://benne.games/) que fan servir tots els jocs: `src/engine`, `src/editor`,
`src/types`, els scripts, Electron, les configuracions de Vite i els HTML dels editors. És un de sol:
**s'edita aquí** i val per a tots els jocs.

## Com arriba a cada joc

Vite, tsc, Electron i l'extensió de VS Code esperen el motor dins el projecte Benne de cada joc
(`games/<joc>/<joc>/src/engine`...). Per això cada projecte en té una còpia, que fa `npm run motor`
(`copia.mjs`):

- copia tots els fitxers d'aquesta carpeta (menys `copia.mjs`, `package.base.json` i aquest README);
- els deixa de **només lectura**, perquè no s'editin allà per error;
- esborra els que ja no hi són (`.motor-copiat.json`) i els treu de git (un bloc al `.gitignore`);
- posa al dia els scripts i les dependències del `package.json` del projecte des de `package.base.json`
  (el nom, `benne` i les dependències pròpies del joc es conserven). Si canvien, cal `npm install`.

Es fa sola abans de `npm run dev`, `npm run build` i les previsualitzacions. Amb `npm run dev`, a
més, cada fitxer d'aquí que canviï es torna a copiar a l'instant (`benneMotorSyncPlugin` a
`vite.config.ts`), i el joc es recarrega.

Per actualitzar Phaser o qualsevol altra dependència del motor: `package.base.json`, i després
`npm run motor && npm install` a cada projecte Benne.

## Canvis propis respecte de Benne

Benne és de codi obert i aquest motor en surt, amb canvis nostres:

- `stayBlackOnEnter()`: la sala no es mostra fins a un `fadeIn()` (títols sobre negre abans d'una sala);
- el text de pantalla (Display Text) per sobre del fos a negre;
- `walkToLabel` a `game-config.json`, per traduir «Walk to»;
- `shade.set(alpha, { color, seconds })`: una capa de color damunt de la sala i dels personatges, per sota de la
  interfície i del text (una sala sense llum); passa d'una sala a l'altra fins que es canvia;
- `setOutfit()`: la roba d'un personatge (prova `<roba>IdleD`, `<roba>WalkL`... abans que les normals);
- `speech.clickProtectMs` a `game-config.json`: els primers mil·lisegons d'una línia, un clic no la salta;
- `game.isBusy`: si ara mateix es diu una línia, hi ha una conversa oberta, una cinemàtica o un vídeo (les rondes
  dels personatges s'hi aturen);
- `pauseGame` a una GUI modal: mentre és oberta, el joc s'atura (temporitzadors, tweens, caminades), i Esc la tanca;
- les partides desades al `localStorage` amb una clau per joc (`VITE_BENNE_GAME_ID`, del nom del
  `package.json` del projecte), perquè dos jocs al mateix origen no comparteixin partides.
- el favicon de Mala Herba Soft (`favicon.ico` i `favicon.svg`), a `index.html`; els fitxers són al `public/` de
  cada joc.
- la descripció i la targeta per compartir l'enllaç (`description` i `url` al bloc `benne` del `package.json`
  del joc, i `public/portada.png`), i `lang="ca"`.
- per a pantalles tàctils (els fa servir Aigua Verne B): `inputProfile.holdVerb` i `holdMs` a `game-config.json`
  (mantenir premut una cosa fa aquest verb; un toc curt fa el del botó principal, en aixecar el dit;
  `src/engine/verbs/holdGesture.ts`), un verb d'objecte (`usesItem`) com a botó principal fa «Usa X amb...» quan hi ha
  un objecte a la mà, i tocar un objecte de l'inventari que té `defaultVerb` fa aquest verb en lloc de prendre'l a la
  mà (el plànol de Ni un ou B s'obre d'un toc), i `game.showClickables(segons)` marca un moment tot el que es pot
  clicar;
- alçada adaptable (Aigua Verne B): amb `resolution.minHeight` a `game-config.json`, el joc tria en arrencar una alçada
  entre aquesta i `resolution.height` segons la proporció de la pantalla (presa en apaïsat), perquè un mòbil 20:9 i un
  monitor 16:9 quedin plens. Les GUI es dissenyen a l'alçada mínima i `anchorY` (a la GUI o a cada control: `top`,
  `center`, `bottom`, `stretch`) diu on van si la pantalla és més alta; a les sales, `viewAnchorY` (0 dalt … 1 baix)
  fixa la càmera quan la sala és més alta que la pantalla. `pointer.screen` i `game.screenSize` en BenneScript. Si la
  finestra canvia de forma (mida, pantalla completa, mòbil girat), es torna a triar l'alçada i, en un moment quiet
  (sense interacció, diàleg, cinemàtica ni menú obert), la sala es refà com en carregar una partida, amb l'estat
  passat a JSON i tornat a entrar (`src/engine/adaptiveResize.ts`; no toca cap partida desada);
- una pantalla de càrrega a `index.html` (el nom del joc i una barra que segueix el loader de la `BootScene`;
  vegeu `src/engine/bootLoadingScreen.ts`), amb els colors de cada joc (`colors` al bloc `benne` del `package.json`).

`adapters/benne/patches/motor-benne.patch` en recull una part. Si mai s'actualitza el motor des d'un
Benne nou (`npm run benne:create -- --from <benne> --motor`), revisa `git diff packages/benne` i torna a
posar el que s'hagi perdut.
