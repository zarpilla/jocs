# Ni un ou · projecte Benne

Projecte de [Benne](https://benne.games/) del joc. **La història no és aquí**: és a `../game/`.
Aquí hi ha l'art i el que genera `npm run benne:sync`. El motor (`src/engine`, `scripts/`,
`electron/`...) és una còpia de només lectura de `packages/benne`, que fa `npm run motor`
(sol, abans de `dev` i `build`): el motor s'edita allà, i val per a tots els jocs.

```bash
npm install      # la primera vegada
npm run dev      # juga al navegador
```

Plantilla 9-verb de Benne 0.1.3, copiada amb `npm run benne:create`.
