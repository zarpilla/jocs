import { defineConfig } from 'vitest/config';

export default defineConfig({
  test: {
    include: ['packages/*/test/**/*.test.ts', 'game/test/**/*.test.ts', 'adapters/**/test/**/*.test.ts'],
  },
});
