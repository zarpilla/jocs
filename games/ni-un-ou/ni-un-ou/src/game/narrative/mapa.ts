// GENERAT per adapters/benne/sync.ts. No l'editis aquí.
/**
 * El plànol de l'Arenga a Benne (GUI `mapa`, la dibuixa adapters/benne/tools/hd640/mapa.py): fer servir l'objecte
 * `mapa` envia l'esdeveniment `mapa`, i aquí s'obre. Quines sales s'hi poden triar i on va cada clic ho decideix
 * game/logic/mapa.ts (no obre cap porta que no s'obri caminant).
 *
 * Es copia a `src/game/narrative/` amb `npm run benne:sync`. No l'editis allà: edita
 * `games/ni-un-ou/adapters/benne/runtime/`.
 */
import { events, type GuiControlHandle } from '@benne/script';
import { guis } from '@game';
import { accessibles, salesDelPlanol, viatge } from '@aventura/game/logic';
import { narrative, protagonistRoom } from './narrative';

/** L'id del botó d'una sala a la GUI (en camelCase, com els escriu mapa.py). */
export const botoSala = (sala: string) => `sala${sala.split('_').map((p) => p[0]!.toUpperCase() + p.slice(1)).join('')}`;

const control = (id: string) => (guis.mapa.controls as unknown as Record<string, GuiControlHandle | undefined>)[id];

/** Posa un punt (`aqui`, `altraIri`, `altraVet`) a la cantonada d'una sala, o l'amaga. */
function posaPunt(punt: string, sala: string | null, desplaça = 0) {
  const p = control(punt);
  const b = sala ? control(botoSala(sala)) : undefined;
  if (!p) return;
  p.visible = !!b;
  if (b) {
    p.x = b.x + 3 + desplaça;
    p.y = b.y + 3;
  }
}

/** Obre el plànol: les sales on ara no es pot anar, ratllades; on és cadascuna. */
export function mostraMapa() {
  const aqui = narrative.world.currentRoom();
  const obertes = accessibles(narrative);
  for (const sala of salesDelPlanol(narrative)) {
    const boto = control(botoSala(sala));
    if (boto) boto.text = narrative.t(`ui.mapa.sala.${sala}`);
    const off = control(`${botoSala(sala)}Off`);
    if (off) off.visible = !obertes.has(sala);
  }
  const jo = narrative.world.activeProtagonist();
  posaPunt('aqui', aqui);
  for (const who of narrative.content.manifest.protagonists) {
    const punt = `altra${who[0]!.toUpperCase()}${who.slice(1)}`;
    if (who === jo) posaPunt(punt, null);
    else {
      const sala = protagonistRoom(who);
      posaPunt(punt, sala ?? null, sala === aqui ? 12 : 0);
    }
  }
  peuMapa(null);
  const tanca = control('tanca');
  if (tanca) tanca.text = narrative.t('ui.mapa.tanca');
  guis.mapa.show();
}

export const mapaObert = () => guis.mapa.visible;

export function tancaMapa() {
  guis.mapa.hide();
}

/** El peu del plànol: el nom sencer de la sala que hi ha sota el ratolí (o, si no s'hi pot anar, que no). */
export function peuMapa(sala: string | null) {
  const peu = control('peu');
  if (!peu) return;
  if (!sala) {
    peu.text = narrative.t('ui.mapa.peu');
    return;
  }
  const nom = narrative.t(narrative.content.rooms[sala]?.name ?? sala);
  peu.text = accessibles(narrative).has(sala) ? nom : narrative.t('ui.mapa.tancada', { sala: nom });
}

/** Tria una sala: tanca el plànol i diu on s'ha d'anar (o què diu la protagonista si no hi pot anar). */
export function triaSala(sala: string): { sala: string | null; linies: string[] } {
  tancaMapa();
  const v = viatge(narrative, sala);
  return { sala: v.sala, linies: v.linies.map((l) => narrative.t(l.text)) };
}

events.on('narrative:mapa', () => mostraMapa());

// Esc tanca el plànol.
if (typeof window !== 'undefined') {
  window.addEventListener('keydown', (ev) => {
    if (ev.key === 'Escape' && mapaObert()) tancaMapa();
  });
}
