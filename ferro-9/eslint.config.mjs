// ESLint del joc (npm run lint). Les regles de BenneScript són a scripts/lib/.
import tseslint from 'typescript-eslint';
import { gameScriptsConfig } from './scripts/lib/eslint-plugin-bennescript.mjs';

export default [gameScriptsConfig({ parser: tseslint.parser, tsconfigRootDir: import.meta.dirname })];
