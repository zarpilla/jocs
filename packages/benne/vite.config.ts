import path from 'node:path';
import fs from 'node:fs';
import { fileURLToPath } from 'node:url';
import { defineConfig, type Plugin } from 'vite';
import { benneGenerateGameIdsPlugin } from './vite-plugin-bennegame-ids';
import { benneScriptPlugin } from './vite-plugin-bennescript';

const dir = path.dirname(fileURLToPath(import.meta.url));
const pkg = JSON.parse(fs.readFileSync(path.join(dir, 'package.json'), 'utf8')) as {
  name?: string;
  version?: string;
  benne?: { displayName?: string };
};
const slug = (pkg.name || 'benne-game').replace(/[^a-zA-Z0-9-]+/g, '-').replace(/^-|-$/g, '');
const displayName = pkg.benne?.displayName?.trim() || slug.split('-').map(
  (part: string) => part.slice(0, 1).toUpperCase() + part.slice(1),
).join(' ');
const iconExists = fs.existsSync(path.join(dir, 'src/game/assets/images/icon.png'));

/**
 * El motor és compartit (packages/benne) i aquí n'hi ha una còpia (`npm run motor`). Amb `npm run dev`,
 * cada fitxer del motor que canvia es torna a copiar, i Vite el recarrega com qualsevol altre.
 */
function benneMotorSyncPlugin(): Plugin {
  return {
    name: 'benne-motor-sync',
    apply: 'serve',
    async configureServer(server) {
      const manifest = path.join(dir, '.motor-copiat.json');
      if (!fs.existsSync(manifest)) return;
      const origen = path.resolve(dir, (JSON.parse(fs.readFileSync(manifest, 'utf8')) as { origen: string }).origen);
      const { copyOne } = (await import(path.join(origen, 'copia.mjs'))) as { copyOne: (project: string, rel: string) => boolean };
      const sync = (file: string) => {
        const rel = path.relative(origen, file);
        if (rel.startsWith('..') || path.isAbsolute(rel) || /^(copia\.mjs|package\.base\.json|README\.md|node_modules)/.test(rel)) return;
        if (copyOne(dir, rel.split(path.sep).join('/'))) server.config.logger.info(`motor: ${rel}`, { timestamp: true });
      };
      server.watcher.add(origen);
      server.watcher.on('change', sync);
      server.watcher.on('add', sync);
    },
  };
}

/**
 * Phaser publishes `browser` → UMD (`phaser.js`) and `module` → ESM (`phaser.esm.js`).
 * Vite can resolve the UMD file, which has no `default` export — force the ESM build.
 */
export default defineConfig({
  // Allow itch.io and other static hosts to serve a game under a generated subdirectory.
  base: './',
  // BENNE Play and the editor previews merge this config, so they get the BenneScript transform too.
  plugins: [benneMotorSyncPlugin(), benneGenerateGameIdsPlugin(), benneScriptPlugin(), {
    name: 'benne-game-page',
    transformIndexHtml(html: string) {
      return html.replace(/<title>[^<]*<\/title>/, `<title>${displayName.replace(/&/g, '&amp;').replace(/</g, '&lt;')}</title>`)
        .replace(/<link rel="icon"[^>]*\/>/, iconExists
          ? '<link rel="icon" type="image/png" href="./src/game/assets/images/icon.png" />'
          : '');
    },
  }],
  resolve: {
    alias: {
      phaser: path.join(dir, 'node_modules/phaser/dist/phaser.esm.js'),
      '@engine': path.join(dir, 'src/engine'),
      '@benne/script': path.join(dir, 'src/engine/bennescript/index.ts'),
      '@game': path.join(dir, 'src/game/game.ids.ts'),
    },
  },
  // Namespace for localStorage saves, so games on the same origin don't share them.
  define: {
    'import.meta.env.VITE_BENNE_GAME_ID': JSON.stringify(slug),
    // La versió del joc (camp `version` del package.json), per a `game.version`.
    'import.meta.env.VITE_BENNE_GAME_VERSION': JSON.stringify(pkg.version ?? '0.0.0'),
  },
  build: {
    chunkSizeWarningLimit: 2000,
  },
});
