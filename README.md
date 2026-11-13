# Jocs de Mala Herba Soft

Aventures gràfiques de «point & click» fetes amb [Benne](https://benne.games/), totes amb el mateix
motor i la història separada del motor.

| Joc | Carpeta |
|---|---|
| **Ferro-9**: l'Iri i la Vet, separades per 120 anys, es comuniquen amb la finestra de fase. | [games/ferro-9](games/ferro-9/README.md) |
| **Suma Zero**: dues germanes de fet volen repartir tots els diners del món a parts iguals. | [games/suma-zero](games/suma-zero/README.md) |
| **Ni un ou**: a bord d'un vaixell d'una ONG, algú sabota les màquines perquè una mostra de fang no arribi a terra. | [games/ni-un-ou](games/ni-un-ou/README.md) |
| **Aigua Verne**: l'Iri i la Vet volen el pou de la granja; el Magnat Verne s'ha endut l'aigua de tot un sistema planetari. | [games/aigua-verne](games/aigua-verne/README.md) |

## Què és compartit i què és de cada joc

```
packages/narrative-core/   MOTOR NARRATIU: estat, condicions, diàlegs, missions, pistes, finals (TS pur)
packages/benne/            MOTOR DE BENNE: un de sol; cada joc en té una còpia de només lectura
adapters/benne/            L'ADAPTADOR: porta el contingut de qualsevol joc al seu projecte Benne
tools/                     EINES: validate, jugar, fitxes, revisio, schemas
games/<joc>/
  game/                    el contingut del joc (JSON, textos, regles pròpies a logic/)
  guio/                    el guió
  adapters/benne/          el que el joc fa diferent a Benne (joc.ts), art provisional i eines d'art
  tools/                   música, sons i font del joc (Python)
  <joc>/                   el projecte Benne: art, sales, GUI, i el que genera el sync
```

Una millora al motor, al nucli, a l'adaptador o a les eines **val per a tots els jocs** alhora. El que
cada joc fa a la seva manera (l'historial, els botons del menú, les fonts, els colors de les veus) és a
`games/<joc>/adapters/benne/joc.ts`.

## Ordres

```bash
npm install                      # la primera vegada
npm test                         # tests de tot: el nucli i les partides de tots els jocs
npm run typecheck

# Les d'un joc, des de l'arrel amb -w, o des de games/<joc>/ sense:
npm run validate -w suma-zero    # comprova el contingut
npm run jugar -w ferro-9         # juga en mode text
npm run benne:sync -w suma-zero  # porta el contingut al projecte Benne [-- --watch]
npm run dev -w suma-zero         # juga al navegador (cal `npm install` dins games/suma-zero/suma-zero)
```

Totes les ordres d'un joc: el `package.json` de `games/<joc>/`. Les eines saben de quin joc parles per
la carpeta des d'on s'executen (o per la variable `JOC=<joc>`): vegeu `tools/joc.ts`.

## Publicació

Cada push a `main` que toqui els jocs o el motor passa els tests, compila els jocs i els puja a
`malaherbasoft.cat/<joc>/` ([.github/workflows/publica.yml](.github/workflows/publica.yml)), per rsync, cadascun
a la seva carpeta. Amb `[skip deploy]` al missatge del commit, no es publica. També es pot llançar a mà des
de la pestanya Actions (*Run workflow*), per a un joc o per a tots.

És independent de la CI del web (repo `malaherbasoft`), que publica l'arrel i deixa estar les carpetes dels
jocs. Fan servir els mateixos secrets: `DEPLOY_SSH_KEY`, `DEPLOY_KNOWN_HOSTS` i `DEPLOY_TARGET`.

## Un joc nou

1. `games/<joc>/` amb `game/` (copiat d'un altre joc i buidat), `package.json` (com el dels altres) i
   `adapters/benne/joc.ts` + `mapping.json`.
2. `npm run benne:create -w <joc> -- --from <checkout de Benne>` crea el projecte Benne.
3. `npm run benne:sync -w <joc> -- --init`.
4. Publicació: `description` i `url` al bloc `benne` del `package.json` del projecte Benne, una
   `public/portada.png`, el joc a la llista de [publica.yml](.github/workflows/publica.yml) i la carpeta a
   les exclusions del `deploy.yml` del web.
5. Estadístiques: anomena les missions principals `acte1`, `acte2`, `acte3`… i afegeix el joc a `JOCS`
   del servidor (vegeu [Estadístiques](adapters/benne/README.md#estadístiques)).

Més detalls a [adapters/benne/README.md](adapters/benne/README.md) i
[packages/benne/README.md](packages/benne/README.md).
