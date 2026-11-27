// Creat per games/ultima-arrel/adapters/benne/joc.ts: la llibreta de camp. No l'editis aquí.
// La lògica és a narrative/llibreta.ts (games/ultima-arrel/adapters/benne/runtime/).
import { onUpdate } from '@benne/script';
import { actualitzaLlibreta } from '../../narrative/llibreta';

onUpdate(() => actualitzaLlibreta())
