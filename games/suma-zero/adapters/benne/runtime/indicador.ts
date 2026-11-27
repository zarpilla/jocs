/**
 * L'indicador de les sincronies (tasca 016): una placa petita a dalt a la dreta, a l'estil de la barra «SOSPITA» del
 * vestíbul, que diu quant marge queda mentre un pas de sincronia és en marxa (game/logic/sincronia.ts). És el mateix
 * per als tres passos: els torns que queden (la cigarreta de l'Ortega, el mòbil del Director) o, si el pas no té
 * rellotge sinó un límit, com s'acosta al límit (la sospita d'en Ballester). Surt a les sales del pas, de totes dues
 * protagonistes, i se'n va quan s'acaba.
 *
 * La GUI `indicador` la crea games/suma-zero/adapters/benne/joc.ts (rectangles de color, sense art): una tira de
 * segments per a cada mida de pas, en quatre colors (buit, groc, taronja, vermell). Aquí només es diu quins es veuen
 * i on va la placa. Es crida a cada fotograma (el script de la GUI).
 *
 * Es copia a `src/game/narrative/` amb `npm run benne:sync`. No l'editis allà: edita
 * `games/suma-zero/adapters/benne/runtime/`.
 */
import { game, type GuiControlHandle } from '@benne/script';
import { guis } from '@game';
import { pasActiu } from '@aventura/game/logic';
import { narrative } from './narrative';

// La geometria ha de coincidir amb la de joc.ts (addIndicadorGui).
const PLACA_W = 156;
const MARGE = 4;
const ESCENA = 260;
const TAULER_BAIX = 56;            // (adapters/benne/tactil/guis/verbs/hud.ts)
const MENU_W = 25;                 // el botó del menú, a dalt a la dreta quan no hi ha tauler

/** Els colors dels segments: el control de cada segment és `t<mida>s<i><Color>` (p. ex. `t12s0Groc`). */
export const COLORS = ['Buit', 'Groc', 'Taronja', 'Vermell'] as const;

const controls = () => guis.indicador.controls as unknown as Record<string, GuiControlHandle | undefined>;

/** La x de la placa: arran de la dreta o, al mòbil, a l'esquerra del botó del menú. */
function placaX() {
  const tauler = game.screenSize.height - ESCENA >= TAULER_BAIX;
  return 640 - MARGE - PLACA_W - (tauler ? 0 : MENU_W + MARGE);
}

/** La x de cada control amb la placa a x = 0, com és al .gui.json (es llegeix la primera vegada, abans de moure res). */
const base = new Map<string, number>();

function color(valor: number, total: number, rellotge: boolean): typeof COLORS[number] {
  const f = valor / total;
  if (rellotge) return f > 0.5 ? 'Groc' : f > 0.25 ? 'Taronja' : 'Vermell';
  return f < 0.5 ? 'Groc' : f < 0.9 ? 'Taronja' : 'Vermell';
}

let mides: number[] | null = null;

export function actualitzaIndicador() {
  const gui = guis.indicador;
  const pas = pasActiu(narrative);
  const sala = narrative.world.currentRoom();
  const titol = (guis as unknown as Record<string, { visible: boolean } | undefined>).titol;
  const on = !!pas && !!sala && pas.sales.includes(sala) && !titol?.visible;
  if (!on) {
    if (gui.visible) gui.hide();
    return;
  }
  if (!gui.visible) gui.show();
  const cs = controls();
  // (els controls es tornen a fer en tornar d'un diàleg o a cada sala, a la posició del .gui.json: es posen a lloc
  // a cada fotograma)
  if (!base.size) for (const [id, c] of Object.entries(cs)) if (c) base.set(id, c.x);
  mides ??= Object.keys(cs).filter((id) => /^t\d+s0Buit$/.test(id)).map((id) => Number(id.slice(1, id.indexOf('s'))));

  const rellotge = !!pas!.rellotge;
  const total = rellotge ? pas!.torns ?? 0 : pas!.limit?.max ?? 0;
  const valor = Math.max(0, Math.min(total, Number(narrative.getVar(rellotge ? pas!.rellotge! : pas!.limit!.var) ?? (rellotge ? total : 0))));
  const ple = color(valor, total, rellotge);
  // si no hi ha cap tira de la mida del pas, la més petita que hi càpiga
  const n = mides.includes(total) ? total : mides.filter((m) => m >= total).sort((a, b) => a - b)[0] ?? 0;

  const x0 = placaX();
  for (const [id, c] of Object.entries(cs)) {
    if (!c) continue;
    const x = x0 + (base.get(id) ?? 0);
    if (c.x !== x) c.x = x;
    const m = /^t(\d+)s(\d+)([A-Z]\w+)$/.exec(id);
    const vol = !m ? true : Number(m[1]) === n && (Number(m[2]) < valor ? m[3] === ple : m[3] === 'Buit');
    if (c.visible !== vol) c.visible = vol;
  }
  const etiqueta = cs.etiqueta;
  if (etiqueta) {
    const text = narrative.t(rellotge ? 'ui.sync.torns' : 'ui.sync.sospita');
    if (etiqueta.text !== text) etiqueta.text = text;
  }
}
