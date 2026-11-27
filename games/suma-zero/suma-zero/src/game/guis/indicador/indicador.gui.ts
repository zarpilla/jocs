// Creat per games/suma-zero/adapters/benne/joc.ts: l'indicador de les sincronies. No l'editis aquí.
// La lògica és a narrative/indicador.ts (games/suma-zero/adapters/benne/runtime/).
import { onUpdate } from '@benne/script';
import { actualitzaIndicador } from '../../narrative/indicador';

onUpdate(() => actualitzaIndicador())
