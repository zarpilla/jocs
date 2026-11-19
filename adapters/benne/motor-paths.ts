/**
 * Què del checkout de Benne és el motor compartit (packages/benne). Ho fan servir `benne:create --motor`
 * (per copiar-lo) i `benne:pegat` (per comparar-lo amb el nostre i refer patches/motor-benne.patch).
 */

/** Carpetes que es copien senceres (i s'esborren abans, perquè no en quedin fitxers vells). */
export const SHARED_DIRS = ['src/engine', 'src/editor', 'src/types', 'electron', 'scripts/lib'];

/** Fitxers solts (si el checkout no en té algun, se salta). */
export const SHARED_FILES = [
  'src/main.ts', 'src/style.css',
  'scripts/generate-game-ids.mjs', 'scripts/resolveBennePreviewOutDir.mjs', 'scripts/package-itch.mjs',
  'scripts/prepare-desktop.mjs', 'scripts/smoke-desktop.cjs', 'scripts/run-electron-test.cjs', 'scripts/test-webgl-recovery.cjs',
  'electron-builder.config.cjs',
  'vite.config.ts', 'vite.room-preview.config.ts', 'vite.character-preview.config.ts', 'vite.gui-preview.config.ts',
  'vite.inventory-preview.config.ts', 'vite.benne-play.config.ts', 'vite-plugin-bennegame-ids.ts', 'vite-plugin-bennescript.ts',
  'tsconfig.json', 'index.html', 'room-editor.html', 'character-editor.html', 'gui-editor.html', 'inventory-editor.html',
  'benne-play.html', '.claude/skills/bennescript/SKILL.md', '.agents/skills/bennescript/SKILL.md',
];

/** La versió de Benne d'on surt el motor: la base del pegat. */
export const BENNE_BASE = 'v0.1.3';
