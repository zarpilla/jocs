// Creat per games/suma-zero/adapters/benne/joc.ts: l'indicador de les sincronies. No l'editis aquí.
// La lògica és a narrative/indicador.ts (games/suma-zero/adapters/benne/runtime/). De pas, a cada fotograma, on surt
// el text de qui parla pel passaplats (narrative/passaplats.ts).
import { onUpdate } from '@benne/script';
import { actualitzaIndicador } from '../../narrative/indicador';
import { actualitzaPassaplats } from '../../narrative/passaplats';

onUpdate(() => {
  actualitzaIndicador();
  actualitzaPassaplats();
})
