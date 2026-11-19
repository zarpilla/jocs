// GENERAT per adapters/benne/sync.ts. No l'editis aquí.
/**
 * Les preferències de la interfície tàctil, de cada joc i de cada aparell (al `localStorage` del navegador, amb l'id
 * del joc a la clau): què fa cada botó del ratolí (per defecte, el clic esquerre mira i el dret fa). No van amb les
 * partides desades: són de qui juga, no de la partida. Si el navegador no deixa desar (mode privat,
 * previsualitzacions), valen els valors per defecte.
 *
 * Compartida (adapters/benne/tactil/runtime/): `npm run benne:sync` la copia a `src/game/narrative/`. No l'editis allà.
 */
import mapping from './mapping.generated.json';

export interface Preferencies {
  /** Amb el ratolí, el clic esquerre fa i el dret mira; per defecte, a l'inrevés (l'esquerre mira, el dret fa). */
  esquerreFa: boolean;
}

const PER_DEFECTE: Preferencies = { esquerreFa: false };
// (abans hi havia `esquerreMira`, amb l'esquerre que feia per defecte, i `noMostrisControls`: no es llegeixen, i així
// tothom comença amb el valor per defecte d'ara)
const CLAU = `benne-tactil:${(mapping as { id?: string }).id ?? 'joc'}`;

let actuals: Preferencies | null = null;

/** Només les preferències d'ara (les velles que hi hagi desades no hi passen). */
function neteja(desat: Record<string, unknown>): Partial<Preferencies> {
  const net: Partial<Preferencies> = {};
  if (typeof desat.esquerreFa === 'boolean') net.esquerreFa = desat.esquerreFa;
  return net;
}

export function preferencies(): Preferencies {
  if (actuals) return actuals;
  actuals = { ...PER_DEFECTE };
  try {
    if (typeof localStorage !== 'undefined') {
      const desat = localStorage.getItem(CLAU);
      if (desat) actuals = { ...actuals, ...neteja(JSON.parse(desat) as Record<string, unknown>) };
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

/** Amb el ratolí, si el clic esquerre mira (i el dret fa): per defecte, sí. */
export const esquerreMira = () => !preferencies().esquerreFa;
