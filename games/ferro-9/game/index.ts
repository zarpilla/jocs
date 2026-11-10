/**
 * Punt d'entrada del contingut per a entorns Vite (Benne, Vitest...).
 * Carrega tots els JSON de `data/` i `locales/` en temps de compilació.
 */
import { assembleGame } from './assemble.js';

const modules = import.meta.glob(['./data/**/*.json', './locales/**/*.json'], {
  eager: true,
  import: 'default',
});

const files = Object.fromEntries(
  Object.entries(modules).map(([path, json]) => [path.replace(/^\.\//, ''), json]),
);

export const { content, locales } = assembleGame(files);
export { assembleGame };
