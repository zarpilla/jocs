// GENERAT per adapters/benne/sync.ts. No l'editis aquí.
/**
 * El plànol de l'Arenga, la part seqüenciada (BenneScript): anar a la sala triada, o dir per què no s'hi pot anar.
 * Vegeu mapa.ts.
 *
 * Es copia a `src/game/narrative/` amb `npm run benne:sync`. No l'editis allà: edita
 * `games/ni-un-ou-b/adapters/benne/runtime/`.
 */
import { player } from '@benne/script';
import { benneRoom, recordLine } from './narrative';
import { triaSala } from './mapa';

/** Un clic a una sala del plànol. */
export function viatjaAmbMapa(sala: string) {
  const r = triaSala(sala);
  for (const text of r.linies) {
    recordLine('player', text);
    player.say(text);
  }
  if (!r.sala) return;
  const room = benneRoom(r.sala);
  if (room) room.goTo();
}
