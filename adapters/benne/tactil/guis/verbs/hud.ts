// La interfície tàctil: el HUD (GUI `verbs`), part instantània: on va cada cosa i la frase. Els esdeveniments són a
// verbs.gui.ts. Compartit (adapters/benne/tactil/guis/); l'art, el .gui.json i les posicions de partida els fa el
// hud.py de cada joc (games/<joc>/adapters/benne/tools/hd640/hud.py), amb aquests mateixos ids i mides. L'escena acaba
// a y = 260; segons quanta pantalla queda a sota (el motor tria l'alçada en arrencar, de 288 a 360):
//
//  - mòbil (menys de 56 px, un mòbil 20:9): sobre l'escena. A dalt, «Canvia» (la cara de l'altra protagonista) i el
//    menú; a les cantonades de baix, els punts (què es pot tocar) i la bossa, que desplega la safata de l'inventari; a
//    la franja negra de sota, la frase: el nom del que hi ha sota el dit (o «Usa X amb...»).
//  - tauler (56 px o més: una finestra de navegador, un monitor): la franja de sota l'escena és un tauler amb tot: la
//    frase a dalt; a l'esquerra, «Canvia», el menú i els punts; i l'inventari sempre a la vista, fins a la dreta de
//    tot: una fila de 7 (tauler baix) o, des de 94 px, dues (tauler alt, un monitor 16:9 a pantalla completa).
//    «Canvia» fa tant d'alt com el menú i els punts petits l'un sobre l'altre (52 px). Amb dues files, «Canvia» a
//    dalt i, a sota, el menú i els punts petits l'un al costat de l'altre; amb una, «Canvia» i, al costat, el menú
//    a sobre dels punts petits.
//
// A una cinemàtica amb coses per tocar (la carta de navegació d'Aigua Verne), només la frase i els punts: no hi ha
// protagonista, ni inventari, ni «Canvia».
import { game, player, pointer } from '@benne/script';
import { guis, verbs } from '@game';
import {
  botoEsPista, botoPistaMixt, clickablePrompt, isClickableCutscene, narrative, switchButtonWanted, targetFromBenne,
} from '../../narrative/narrative';
import { esSortida, queFaElToc } from '../../narrative/accions';
import { esDit } from '../../narrative/tactil';
import { esquerreMira } from '../../narrative/preferencies';
import {
  bossaBtn, canviaBtn, caraIri, caraVet, downBtn, downBtn2, downBtn3, inventoryPanel, inventoryPanel2, inventoryPanel3,
  menuBtn, puntsBtn, puntsPetitBtn, safata, safata2, safata3, tauler, upBtn, upBtn2, upBtn3, verbLineText,
  verbLineVerb,
} from './verbs.ids';

/** On acaba l'escena (l'art de les sales és pintat fins aquí). */
const ESCENA = 260;
/** Franja mínima per al tauler baix (una fila), i per a l'alt (dues). */
const TAULER_BAIX = 56;
const TAULER_ALT = 94;
/** On va la cara dins la pantalla rodona del botó «Canvia» (hud.py). */
const CARA = { x: 15, y: 10 };
/** Les safates del tauler (hud.py): l'alta, de dues files, i la baixa, d'una; totes dues a 4 px de baix. */
const SAFATA2_H = 82;
const SAFATA3_H = 44;
/** La franja de seguretat de dalt del tauler (fins on arriba, des de dalt). */
const FRANJA_SEGURETAT = 6;
/** La frase: on comença la lletra respecte a la y del text, i quant fa d'alt. */
const LLETRA_DALT = 5;
const LLETRA_H = 10;
/** El mig de la pantalla (on es centra la frase) i l'espai entre el verb i el nom (el de les fonts). */
const MIG = 320;
const ESPAI = 4;

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
/** La lupa del botó «Canvia» amb `botoPista: 'mixt'` (l'art el fa el hud.py del joc): no tots els jocs la tenen. */
const caraPistaCtrl = () => (guis.verbs.controls as unknown as Record<string, (Lloc & Visible) | undefined>).caraPista;

const cartaOberta = () => isClickableCutscene(narrative.world.currentRoom());

/** Posa cada cosa on va en el mode d'ara (els controls es tornen a fer a cada sala: es crida a cada fotograma). */
export function layoutHud() {
  const caraPista = caraPistaCtrl();
  // (els controls amagats al .gui.json surten visibles en construir-se la GUI: per això es diu sempre què es veu)
  const gran = [safata2, inventoryPanel2, upBtn2, downBtn2];
  const petita = [safata3, inventoryPanel3, upBtn3, downBtn3];
  const h = alt();
  const carta = cartaOberta();
  if (carta) refreshLine();
  // «Canvia», només si es pot canviar (narrative.ts). Es diu a cada fotograma: una GUI que es refà (en tornar d'un
  // diàleg) el tornaria a mostrar, com al .gui.json.
  mostra([canviaBtn], !carta && switchButtonWanted());
  mostra([menuBtn], !carta);
  if (!modeTauler()) {
    mostra([tauler, puntsPetitBtn, ...gran, ...petita], false);
    mostra([bossaBtn], !carta);
    mostra([puntsBtn], true);
    if (carta) safataOberta = false;
    showTray(safataOberta);
  } else {
    const dues = franja() >= TAULER_ALT;
    mostra([tauler], true);
    mostra(gran, dues && !carta);
    mostra(petita, !dues && !carta);
    mostra([bossaBtn, safata, inventoryPanel, upBtn, downBtn], false);
    // la frase, centrada entre la franja de seguretat i la safata (si no hi ha lloc, tan amunt com es pot)
    const safataTop = franja() - (dues ? SAFATA2_H + 4 : SAFATA3_H + 4);
    const lletra = Math.round((FRANJA_SEGURETAT + safataTop - LLETRA_H) / 2);
    // (la x la posa refreshLine: depèn de si hi ha verb)
    const y = ESCENA + Math.max(1, lletra - LLETRA_DALT);
    posa(verbLineText, verbLineText.x, y);
    posa(verbLineVerb, verbLineVerb.x, y);
    mostra([puntsBtn], false);
    mostra([puntsPetitBtn], true);
    if (dues) {
      // dues files: «Canvia» a dalt, arran de dalt de la safata; a sota, el menú i els punts, arran de baix
      posa(canviaBtn, 6, h - 4 - SAFATA2_H);
      posa(menuBtn, 8, h - 29);
      posa(puntsPetitBtn, 36, h - 29);
    } else {
      // una fila: «Canvia» a baix a l'esquerra i, al costat, el menú a sobre dels punts petits (tot cap en 56 px)
      posa(canviaBtn, 4, h - 56);
      posa(menuBtn, 65, h - 56);
      posa(puntsPetitBtn, 65, h - 29);
    }
    posa(caraIri, canviaBtn.x + CARA.x, canviaBtn.y + CARA.y);
    posa(caraVet, canviaBtn.x + CARA.x, canviaBtn.y + CARA.y);
    if (caraPista) posa(caraPista, canviaBtn.x + CARA.x, canviaBtn.y + CARA.y);
  }
  // La pantalla rodona del botó «Canvia» mostra la cara de l'altra protagonista (la que no juga). El botó el mostra o
  // l'amaga narrative.ts (si es pot canviar).
  // (amb `botoPista`, el botó és la lupa i no hi ha cap cara; amb `'mixt'`, la lupa és `caraPista` quan no es pot canviar)
  const esPista = botoEsPista();
  const on = canviaBtn.visible && !esPista;
  const lupa = canviaBtn.visible && esPista && botoPistaMixt;
  if (caraPista && caraPista.visible !== lupa) caraPista.visible = lupa;
  const iri = on && player.id === 'vet';
  const vet = on && player.id !== 'vet';
  if (caraIri.visible !== iri) caraIri.visible = iri;
  if (caraVet.visible !== vet) caraVet.visible = vet;
}

/**
 * La frase: el nom de la cosa; amb un objecte a la mà, «Usa la clau amb la porta». A la carta de navegació, sense res a
 * sota, el text d'entrada («On anem?»).
 *
 * Si el clic (o el toc) fa una acció, la frase la diu abans del nom: «Obre passaplats», amb el verb més apagat (és un
 * altre text, `verbLineVerb`, a l'esquerra del nom; tots dos junts, centrats). Si el clic mira, o obre el menú perquè
 * n'hi ha més d'una, només el nom.
 */
export function refreshLine() {
  const item = pointer.item;
  const hover = pointer.hover;
  const sobre = hover && !(item && hover.kind === 'item' && hover.id === item.id) ? (hover.description ?? '') : '';
  const text = item
    ? `${verbs.use.label} ${item.name} ${verbs.use.preposition ?? ''} ${sobre}`.trim()
    : sobre || (cartaOberta() ? clickablePrompt() : '');
  const verb = !item && sobre ? verbDelClic() : '';
  if (verbLineText.text !== text) verbLineText.text = text;
  if (verbLineVerb.text !== verb) verbLineVerb.text = verb;
  // el verb i el nom, junts al mig
  const wV = verb ? verbLineVerb.width : 0;
  const wN = verbLineText.width;
  const esquerra = MIG - (wV + (verb ? ESPAI : 0) + wN) / 2;
  const xVerb = Math.round(esquerra);
  const xNom = verb ? Math.round(esquerra + wV + ESPAI + wN / 2) : MIG;
  if (verbLineVerb.x !== xVerb) verbLineVerb.x = xVerb;
  if (verbLineText.x !== xNom) verbLineText.x = xNom;
}

/**
 * El verb que farà el clic esquerre (o el toc) sobre la cosa de sota (`ui.verb.*`: «Obre», «Parla amb»), o '' si el
 * clic mira o obre el menú. El mateix que decideix tactil.script.ts (`fesElToc`): amb el dit, el primer toc mira; amb
 * el ratolí, per defecte (`esquerreMira`), l'esquerre mira (menys a les sortides: hi va). Els objectes de l'inventari no: tocar-los els pren a la mà.
 */
function verbDelClic(): string {
  const hover = pointer.hover;
  if (!hover?.kind || !hover.id || hover.kind === 'item' || cartaOberta()) return '';
  const dit = esDit();
  if (!dit && esquerreMira() && !esSortida(narrative, targetFromBenne(hover.kind, hover.id))) return '';
  const toc = queFaElToc(narrative, targetFromBenne(hover.kind, hover.id), undefined, { mirarPrimer: dit });
  return toc.fa === 'accio' ? narrative.t(`ui.verb.${toc.verb}`) : '';
}
