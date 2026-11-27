// GENERAT per adapters/benne/sync.ts. No l'editis aquí.
/**
 * La llibreta de camp (tasca 051): una pàgina sencera amb les 12 observacions, escena per escena. Les que ja s'han
 * apuntat surten amb el seu nom; les que falten, amb un interrogant. Les d'una partida anterior (al `localStorage`
 * del navegador, només les claus `obs_*`) surten més clares: la llibreta es pot acabar d'omplir en una altra partida.
 * No toca l'estat de la partida (ni el comptador `observacions` ni els flags).
 *
 * S'obre amb l'esdeveniment `llibreta` (mirar o obrir la llibreta, game/data/items.json), quan s'acaben les línies.
 * La GUI `llibreta` la crea games/ultima-arrel/adapters/benne/joc.ts; el seu script crida `actualitzaLlibreta()`
 * a cada fotograma.
 *
 * Es copia a `src/game/narrative/` amb `npm run benne:sync`. No l'editis allà: edita
 * `games/ultima-arrel/adapters/benne/runtime/`.
 */
import { events, game } from '@benne/script';
import { guis } from '@game';
import { narrative } from './narrative';

/** Les escenes i les seves observacions (el flag i el nom curt), en l'ordre del joc (game/test/llibreta.test.ts). */
export const ESCENES: { sala: string; obs: string[] }[] = [
  { sala: 'vora_bosc', obs: ['obs_bolets', 'obs_gespa'] },
  { sala: 'centraleta', obs: ['obs_fils', 'obs_corn'] },
  { sala: 'campament_fades', obs: ['obs_aglans', 'obs_ortiga'] },
  { sala: 'toll_gripaus', obs: ['obs_toll', 'obs_ampolla'] },
  { sala: 'caseta_obra', obs: ['obs_maqueta', 'obs_cartell'] },
  { sala: 'zona_mati', obs: ['obs_sensors'] },
  { sala: 'zona_zero', obs: ['obs_soques'] },
];
const TOTES = ESCENES.flatMap((e) => e.obs);

const CLAU = 'ultima-arrel:llibreta';
const TINTA = '#3a2814';
const ALTRA = '#8a7a64';
const FALTA = '#b0a080';

function desades(): Set<string> {
  try {
    if (typeof localStorage === 'undefined') return new Set();
    const v = JSON.parse(localStorage.getItem(CLAU) ?? '[]');
    return new Set(Array.isArray(v) ? v.filter((x) => TOTES.includes(x)) : []);
  } catch {
    return new Set();
  }
}

/** Apunta al navegador les observacions d'aquesta partida (s'hi afegeixen; no se n'esborra cap). */
function desa() {
  const fetes = TOTES.filter((o) => narrative.flag(o));
  if (!fetes.length) return;
  const totes = desades();
  const abans = totes.size;
  for (const o of fetes) totes.add(o);
  if (totes.size === abans) return;
  try {
    localStorage.setItem(CLAU, JSON.stringify([...totes]));
  } catch {
    // sense localStorage: només es veuen les d'aquesta partida
  }
}

narrative.on((e) => {
  if (e.type === 'stateChanged') desa();
});

let pendent = false;
events.on('narrative:llibreta', () => { pendent = true; });

function omple() {
  const anteriors = desades();
  const esquerra: string[] = [];
  const dreta: string[] = [];
  const colors: (string | undefined)[] = [];
  let ara = 0;
  let totes = 0;
  for (const e of ESCENES) {
    e.obs.forEach((o, i) => {
      esquerra.push(i === 0 ? narrative.t(`ui.llibreta.sala.${e.sala}`) : '');
      if (narrative.flag(o)) {
        ara++; totes++;
        dreta.push(narrative.t(`ui.llibreta.${o}`));
        colors.push(TINTA);
      } else if (anteriors.has(o)) {
        totes++;
        dreta.push(`${narrative.t(`ui.llibreta.${o}`)} ${narrative.t('ui.llibreta.altra')}`);
        colors.push(ALTRA);
      } else {
        dreta.push('?');
        colors.push(FALTA);
      }
    });
  }
  const c = guis.llibreta.controls;
  c.titol.text = narrative.t('ui.llibreta.titol');
  c.compte.text = totes > ara
    ? narrative.t('ui.llibreta.compte_totes', { n: ara, totes })
    : narrative.t('ui.llibreta.compte', { n: ara });
  c.sales.text = esquerra.join('\n');
  c.obs.text = dreta.join('\n');
  c.obs.setLineColors(colors);
  c.peu.text = narrative.t('ui.llibreta.peu');
}

const tanca = () => guis.llibreta.hide();
guis.llibreta.controls.fons.onClick(async () => tanca());
guis.llibreta.controls.pagina.onClick(async () => tanca());
if (typeof window !== 'undefined') {
  window.addEventListener('keydown', (ev) => {
    if (guis.llibreta.visible && (ev.key === 'Escape' || ev.key === 'Enter' || ev.key === ' ')) tanca();
  });
}

/** Es crida a cada fotograma (el script de la GUI): obre la pàgina quan s'acaben les línies de mirar la llibreta. */
export function actualitzaLlibreta() {
  if (!pendent || game.isBusy) return;
  pendent = false;
  omple();
  guis.llibreta.show();
}
