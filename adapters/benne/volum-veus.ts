/**
 * El control «volum de les veus» del menú d'opcions (GUI `settings-menu` de la plantilla): una fila més, just a sota
 * de la de la música, amb un control lliscant que mou `settings.voiceVolume` (canvi propi del motor, vegeu
 * packages/benne/README.md). La fa servir benne-content.ts a cada `benne:sync`, després d'`opcionsTactils`.
 *
 * Es pot tornar a executar: si la fila ja hi és, només es regenera el codi afegit al script.
 */
import { existsSync, readFileSync, writeFileSync } from 'node:fs';
import { join } from 'node:path';

type Json = Record<string, unknown>;
type Control = Json & { id?: string; x?: number; y?: number; height?: number; rows?: number; gridPlacement?: Json };

const MARCA = '// Afegit per adapters/benne/volum-veus.ts';

export function filaVolumVeus(gameDir: string, etiquetaText = 'volum de les veus') {
  const dir = join(gameDir, 'guis/settings-menu');
  const jsonPath = join(dir, 'settings-menu.gui.json');
  const tsPath = join(dir, 'settings-menu.gui.ts');
  if (!existsSync(jsonPath) || !existsSync(tsPath)) return;
  const def = JSON.parse(readFileSync(jsonPath, 'utf8')) as Json;
  const controls = (def.controls as Control[]) ?? [];
  const per = (id: string) => controls.find((c) => c.id === id);
  const grid = per('settings-layout');
  const fons = per('settings-BG');
  const lliscant = per('musicVolume');
  const etiqueta = per('music-volume');
  if (grid && fons && lliscant && etiqueta && !per('voiceVolume')) {
    const files = Number(grid.rows ?? 4);
    const alt = Math.round(Number(grid.height ?? 116) / files);     // l'alçada d'una fila
    const puja = Math.round(alt / 2);                                // per tornar-ho a centrar
    const sotaGrid = Number(grid.y) + Number(grid.height);
    const fila = Number(lliscant.gridPlacement?.row) + 1;
    // Les files de sota baixen una posició; el que hi ha sota la graella (Torna, Controls, la versió) baixa una fila.
    for (const c of controls) {
      const gp = c.gridPlacement as Json | undefined;
      if (gp && gp.gridControlId === grid.id && Number(gp.row) >= fila) gp.row = Number(gp.row) + 1;
      else if (!gp && c !== fons && typeof c.y === 'number' && c.y >= sotaGrid) c.y += alt - puja;
    }
    for (const c of [fons, per('title'), grid]) if (c && typeof c.y === 'number') c.y -= puja;
    fons.height = Number(fons.height) + alt;
    grid.rows = files + 1;
    grid.height = Number(grid.height) + alt;
    const novaEtiqueta: Control = {
      ...structuredClone(etiqueta), id: 'voice-volume', scriptName: 'voiceVolumeLabel', text: etiquetaText,
      gridPlacement: { ...(etiqueta.gridPlacement as Json), row: fila },
    };
    const index = controls.indexOf(lliscant) + 1;
    controls.splice(index, 0,
      { ...structuredClone(lliscant), id: 'voiceVolume', gridPlacement: { ...(lliscant.gridPlacement as Json), row: fila } },
      novaEtiqueta,
    );
    writeFileSync(jsonPath, JSON.stringify(def, null, 2) + '\n');
  }
  let script = readFileSync(tsPath, 'utf8');
  const marca = script.indexOf(MARCA);
  if (marca >= 0) script = script.slice(0, marca);
  writeFileSync(tsPath, `${script.trimEnd()}

${MARCA}: el volum de les veus.
import { settings as opcionsVeus } from '@benne/script'
import { voiceVolume } from './settings-menu.ids'

gui.onBuilt(() => {
  voiceVolume.value = opcionsVeus.voiceVolume * 100
})

voiceVolume.onChange((v: number) => {
  opcionsVeus.voiceVolume = v / 100
})
`);
}
