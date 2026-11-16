// GENERAT per adapters/benne/sync.ts. No l'editis aquí.
/**
 * Les preferències de la interfície tàctil, de cada joc i de cada aparell (al `localStorage` del navegador, amb l'id
 * del joc a la clau): si es torna a mostrar la targeta «Com es juga» en començar, i què fa cada botó del ratolí
 * (per defecte, el clic esquerre fa i el dret mira). No van amb les partides desades: són de qui juga, no de la
 * partida. Si el navegador no deixa desar (mode privat, previsualitzacions), valen els valors per defecte.
 *
 * Compartida (adapters/benne/tactil/runtime/): `npm run benne:sync` la copia a `src/game/narrative/`. No l'editis allà.
 */
import mapping from './mapping.generated.json';

export interface Preferencies {
  /** «No ho tornis a mostrar» a la targeta «Com es juga». */
  noMostrisControls: boolean;
  /** Amb el ratolí, el clic esquerre mira i el dret fa; per defecte, a l'inrevés (l'esquerre fa, com és habitual). */
  esquerreMira: boolean;
}

const PER_DEFECTE: Preferencies = { noMostrisControls: false, esquerreMira: false };
const CLAU = `benne-tactil:${(mapping as { id?: string }).id ?? 'joc'}`;

let actuals: Preferencies | null = null;

export function preferencies(): Preferencies {
  if (actuals) return actuals;
  actuals = { ...PER_DEFECTE };
  try {
    if (typeof localStorage !== 'undefined') {
      const desat = localStorage.getItem(CLAU);
      if (desat) actuals = { ...actuals, ...(JSON.parse(desat) as Partial<Preferencies>) };
      // la primera vegada (o amb una preferència nova), queden desades també les per defecte
      const json = JSON.stringify(actuals);
      if (json !== desat) localStorage.setItem(CLAU, json);
    }
  } catch {
    // sense localStorage (o malmès): els valors per defecte
  }
  return actuals;
}

export function setPreferencia<K extends keyof Preferencies>(clau: K, valor: Preferencies[K]) {
  actuals = { ...preferencies(), [clau]: valor };
  try {
    if (typeof localStorage !== 'undefined') localStorage.setItem(CLAU, JSON.stringify(actuals));
  } catch {
    // no es pot desar: val per a aquesta sessió
  }
}

export const esquerreMira = () => preferencies().esquerreMira;
