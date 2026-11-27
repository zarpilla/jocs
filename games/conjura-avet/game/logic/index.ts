/**
 * Lògica pròpia de La Conjura de l'Avet, independent del motor gràfic. Qualsevol adaptador (Benne o un altre) la
 * instal·la sobre el `Narrative`. Només hi ha una regla: «dona la serra a la Vet» (acció `donar`, a les interaccions
 * de l'Iri i la Vet de characters.json), que passa un objecte d'una germana a l'altra quan són a la mateixa sala.
 */
import type { ActionResult, GameContent, Narrative } from '@aventura/narrative-core';

/** Totes les accions que el contingut pot fer servir (`"action": { "name": ... }`). */
export const GAME_ACTIONS: string[] = ['donar'];

/** Claus de text que fa servir el codi del joc. */
export const GAME_TEXT_KEYS: string[] = ['donar.dona', 'donar.no', 'donar.ja', 'donar.guarda', 'donar.ara_no'];

/** Les de `GAME_TEXT_KEYS` més les que depenen del contingut: el nom amb article de cada objecte. */
export function gameTextKeys(content: GameContent): string[] {
  return [...GAME_TEXT_KEYS, ...Object.keys(content.items).map((id) => `obj.${id}.amb_article`)];
}

export function donar(n: Narrative, item: string): ActionResult {
  const who = n.world.activeProtagonist();
  const other = n.content.manifest.protagonists.find((p) => p !== who)!;
  const props = n.content.items[item]?.props ?? {};
  if (props.no_donar === true) return { lines: [{ who: 'player', text: 'donar.no' }] };
  // Quan no es pot canviar de germana, l'altra no podria tornar-ho: es quedaria encallat (al molí, al judici...).
  if (!n.canSwitch()) return { lines: [{ who: 'player', text: 'donar.ara_no' }] };
  // Les proves que la Vet ha de portar al judici (la serra, la cera): un cop les té ella, ja no les deixa.
  if (props.guarda === who) return { lines: [{ who: 'player', text: 'donar.guarda' }] };
  // El pot de resina no es dona: se'n dona un pegot (`dona`), i el pot es queda (l'Iri el necessita al molí).
  if (typeof props.dona === 'string') {
    if (n.world.hasItem(props.dona, other)) return { lines: [{ who: 'player', text: 'donar.ja' }] };
    n.apply([{ giveItem: props.dona, who: other }]);
    return { lines: [DONA] };
  }
  n.apply([{ takeItem: item }, { giveItem: item, who: other }]);
  return { lines: [DONA] };
}

/**
 * «Té.», amb el gest d'allargar el braç (`Fa`). Qui dona s'atura al punt d'arribada de l'altra, que és a la seva
 * dreta: per això es gira a l'esquerra abans del gest.
 */
const DONA: NonNullable<ActionResult['lines']>[number] = {
  who: 'player',
  text: 'donar.dona',
  stage: [{ who: 'player', face: 'L' }, { who: 'player', gest: 'Fa' }],
  stageAfter: [{ who: 'player', gest: null }],
};

export function installGameLogic(n: Narrative): void {
  n.registerAction('donar', ({ args }) => donar(n, String(args.item ?? '')));
}
