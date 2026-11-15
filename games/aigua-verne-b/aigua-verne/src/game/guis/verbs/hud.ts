// Aigua Verne B: el HUD (GUI `verbs`), part instantània: on va cada cosa i la frase. Els esdeveniments són a
// verbs.gui.ts. Art i posicions de partida: adapters/benne/tools/hd640/hud.py. L'escena acaba a y = 260; segons quanta
// pantalla queda a sota (el motor tria l'alçada en arrencar, de 288 a 360):
//
//  - mòbil (menys de 56 px, un mòbil 20:9): sobre l'escena. A dalt, «Canvia» (la cara de l'altra protagonista) i el
//    menú; a les cantonades de baix, els punts (què es pot tocar) i la bossa, que desplega la safata de l'inventari; a
//    la franja negra de sota, el nom del que hi ha sota el dit (o «Usa X amb...»).
//  - tauler (56 px o més: una finestra de navegador, un monitor): la franja de sota l'escena és un tauler amb tot: la
//    frase a dalt, «Canvia» i els punts a l'esquerra, el menú a la dreta i, al mig, l'inventari sempre a la vista:
//    una fila de 6 (tauler baix) o, des de 94 px, dues (tauler alt, un monitor 16:9 a pantalla completa).
import { game, player, pointer } from '@benne/script';
import { verbs } from '@game';
import {
  bossaBtn, canviaBtn, caraIri, caraVet, downBtn, downBtn2, downBtn3, inventoryPanel, inventoryPanel2, inventoryPanel3,
  menuBtn, puntsBtn, safata, safata2, safata3, tauler, upBtn, upBtn2, upBtn3, verbLineText,
} from './verbs.ids';

/** On acaba l'escena (l'art de les sales és pintat fins aquí). */
const ESCENA = 260;
/** Franja mínima per al tauler baix (una fila), i per a l'alt (dues). */
const TAULER_BAIX = 56;
const TAULER_ALT = 94;
/** On va la cara dins la pantalla rodona del botó «Canvia» (hud.py). */
const CARA = { x: 15, y: 6 };

const alt = () => game.screenSize.height;
const franja = () => alt() - ESCENA;
export const modeTauler = () => franja() >= TAULER_BAIX;

let safataOberta = false;
export const isTrayOpen = () => safataOberta;

/** Desplega o plega la safata del mòbil (al tauler, l'inventari sempre és a la vista). */
export function showTray(on: boolean) {
  safataOberta = on;
  for (const c of [safata, inventoryPanel, upBtn, downBtn]) if (c.visible !== on) c.visible = on;
}

type Lloc = { x: number; y: number };
const posa = (c: Lloc, x: number, y: number) => {
  if (c.x !== x) c.x = x;
  if (c.y !== y) c.y = y;
};
type Visible = { visible: boolean };
const mostra = (cs: Visible[], on: boolean) => {
  for (const c of cs) if (c.visible !== on) c.visible = on;
};

/** Posa cada cosa on va en el mode d'ara (els controls es tornen a fer a cada sala: es crida a cada fotograma). */
export function layoutHud() {
  // (els controls amagats al .gui.json surten visibles en construir-se la GUI: per això es diu sempre què es veu)
  const gran = [safata2, inventoryPanel2, upBtn2, downBtn2];
  const petita = [safata3, inventoryPanel3, upBtn3, downBtn3];
  const h = alt();
  if (!modeTauler()) {
    mostra([tauler, ...gran, ...petita], false);
    mostra([bossaBtn], true);
    showTray(safataOberta);
  } else {
    const dues = franja() >= TAULER_ALT;
    mostra([tauler], true);
    mostra(gran, dues);
    mostra(petita, !dues);
    mostra([bossaBtn, safata, inventoryPanel, upBtn, downBtn], false);
    posa(verbLineText, 320, ESCENA + 1);
    if (dues) {
      posa(canviaBtn, 22, h - 90);
      posa(puntsBtn, 34, h - 40);
      posa(menuBtn, 594, h - 88);
    } else {
      // una fila: «Canvia» i els punts un al costat de l'altre, a l'alçada de la safata (els 44 px de baix)
      posa(canviaBtn, 6, h - 47);
      posa(puntsBtn, 70, h - 40);
      posa(menuBtn, 600, h - 37);
    }
    posa(caraIri, canviaBtn.x + CARA.x, canviaBtn.y + CARA.y);
    posa(caraVet, canviaBtn.x + CARA.x, canviaBtn.y + CARA.y);
  }
  // La pantalla rodona del botó «Canvia» mostra la cara de l'altra protagonista (la que no juga). El botó el mostra o
  // l'amaga narrative.ts (si es pot canviar).
  const on = canviaBtn.visible;
  const iri = on && player.id === 'vet';
  const vet = on && player.id !== 'vet';
  if (caraIri.visible !== iri) caraIri.visible = iri;
  if (caraVet.visible !== vet) caraVet.visible = vet;
}

/** La frase: el nom de la cosa; amb un objecte a la mà, «Usa la clau amb la porta». */
export function refreshLine() {
  const item = pointer.item;
  const hover = pointer.hover;
  const sobre = hover && !(item && hover.kind === 'item' && hover.id === item.id) ? (hover.description ?? '') : '';
  verbLineText.text = item ? `${verbs.use.label} ${item.name} ${verbs.use.preposition ?? ''} ${sobre}`.trim() : sobre;
}
