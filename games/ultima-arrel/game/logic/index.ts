/**
 * Lògica pròpia de L'Última Arrel, independent del motor gràfic. Qualsevol adaptador (Benne o un altre) la instal·la
 * sobre el `Narrative`. De moment no n'hi ha cap: tot el joc es diu amb el JSON de `data/`.
 */
import type { GameContent, Narrative } from '@aventura/narrative-core';

/** Totes les accions que el contingut pot fer servir (`"action": { "name": ... }`). */
export const GAME_ACTIONS: string[] = [];

/** Claus de text que fa servir el codi del joc. */
export const GAME_TEXT_KEYS: string[] = [
  // la pàgina de la llibreta de camp (adapters/benne/runtime/llibreta.ts)
  'ui.llibreta.titol',
  'ui.llibreta.compte',
  'ui.llibreta.compte_totes',
  'ui.llibreta.altra',
  'ui.llibreta.peu',
  'ui.llibreta.sala.vora_bosc',
  'ui.llibreta.sala.centraleta',
  'ui.llibreta.sala.campament_fades',
  'ui.llibreta.sala.toll_gripaus',
  'ui.llibreta.sala.caseta_obra',
  'ui.llibreta.sala.zona_mati',
  'ui.llibreta.sala.zona_zero',
  'ui.llibreta.obs_bolets',
  'ui.llibreta.obs_gespa',
  'ui.llibreta.obs_fils',
  'ui.llibreta.obs_corn',
  'ui.llibreta.obs_aglans',
  'ui.llibreta.obs_ortiga',
  'ui.llibreta.obs_toll',
  'ui.llibreta.obs_ampolla',
  'ui.llibreta.obs_maqueta',
  'ui.llibreta.obs_cartell',
  'ui.llibreta.obs_sensors',
  'ui.llibreta.obs_soques',
];

/** Les de `GAME_TEXT_KEYS` més les que depenen del contingut (cap, de moment). */
export function gameTextKeys(_content: GameContent): string[] {
  return [...GAME_TEXT_KEYS];
}

export function installGameLogic(_n: Narrative): void {
  // Cap regla pròpia encara.
}
