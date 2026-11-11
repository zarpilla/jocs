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
- `setOutfit()`: la roba d'un personatge (prova `<roba>IdleD`, `<roba>WalkL`... abans que les normals);
- `speech.clickProtectMs` a `game-config.json`: els primers mil·lisegons d'una línia, un clic no la salta;
- `pauseGame` a una GUI modal: mentre és oberta, el joc s'atura (temporitzadors, tweens, caminades), i Esc la tanca;
- les partides desades al `localStorage` amb una clau per joc (`VITE_BENNE_GAME_ID`, del nom del
  `package.json` del projecte), perquè dos jocs al mateix origen no comparteixin partides.
- el favicon de Mala Herba Soft (`favicon.ico` i `favicon.svg`), a `index.html`; els fitxers són al `public/` de
  cada joc.
- la descripció i la targeta per compartir l'enllaç (`description` i `url` al bloc `benne` del `package.json`
  del joc, i `public/portada.png`), i `lang="ca"`.
- una pantalla de càrrega a `index.html` (el nom del joc i una barra que segueix el loader de la `BootScene`;
  vegeu `src/engine/bootLoadingScreen.ts`).

`adapters/benne/patches/motor-benne.patch` en recull una part. Si mai s'actualitza el motor des d'un
Benne nou (`npm run benne:create -- --from <benne> --motor`), revisa `git diff packages/benne` i torna a
posar el que s'hagi perdut.
