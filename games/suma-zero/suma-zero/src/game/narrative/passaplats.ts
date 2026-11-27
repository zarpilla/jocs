// GENERAT per adapters/benne/sync.ts. No l'editis aquí.
/**
 * Qui parla pel passaplats (tasca 218): amb el passaplats obert, la germana que és a l'altra sala es veu a la
 * finestreta (els decorats `vet_passaplats` i `iri_passaplats`), i el que diu ha de sortir allà, no a la cantonada de
 * dalt a l'esquerra (on Benne posa el text de qui no és a la sala). Es fa amb `speechPosition`, que val per a totes
 * les sales: per això es posa i es treu a cada fotograma, segons la sala on s'és.
 *
 * Es crida a cada fotograma des del script de la GUI `indicador` (el crea games/suma-zero/adapters/benne/joc.ts).
 * Es copia a `src/game/narrative/` amb `npm run benne:sync`. No l'editis allà: edita
 * `games/suma-zero/adapters/benne/runtime/`.
 */
import { benneCharacter, narrative, protagonistRoom } from './narrative';

type Punt = { x: number; y: number };

/** La finestreta de cada sala (al mig, a dalt del forat: el text hi queda a sobre) i qui s'hi veu. */
const FINESTRETES: Record<string, { qui: string; on: Punt }> = {
  pis_estudi: { qui: 'vet', on: { x: 500, y: 40 } },
  pis_cuina: { qui: 'iri', on: { x: 350, y: 55 } },
};

type AmbVeu = { speechPosition: Punt | null };

export function actualitzaPassaplats() {
  const sala = narrative.world.currentRoom();
  const obert = narrative.flag('passaplats_obert');
  for (const [salaFinestreta, { qui, on }] of Object.entries(FINESTRETES)) {
    const handle = benneCharacter(qui) as unknown as AmbVeu | undefined;
    if (!handle) continue;
    const vol = obert && sala === salaFinestreta && protagonistRoom(qui) !== salaFinestreta ? on : null;
    const ara = handle.speechPosition;
    if (vol ? !ara || ara.x !== vol.x || ara.y !== vol.y : ara) handle.speechPosition = vol;
  }
}
