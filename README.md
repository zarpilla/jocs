# Jocs de Mala Herba Soft

Aventures gràfiques de «point & click» fetes amb [Benne](https://benne.games/), totes amb el mateix
motor i la història separada del motor.

| Joc | Carpeta |
|---|---|
| **Ferro-9**: l'Iri i la Vet, separades per 120 anys, es comuniquen amb la finestra de fase. | [games/ferro-9](games/ferro-9/README.md) |
| **Suma Zero**: dues germanes de fet volen repartir tots els diners del món a parts iguals. | [games/suma-zero](games/suma-zero/README.md) |
| **Ni un ou**: a bord d'un vaixell d'una ONG, algú sabota les màquines perquè una mostra de fang no arribi a terra. | [games/ni-un-ou](games/ni-un-ou/README.md) |
| **Aigua Verne**: l'Iri i la Vet volen el pou de la granja; el Magnat Verne s'ha endut l'aigua de tot un sistema planetari. | [games/aigua-verne](games/aigua-verne/README.md) |
| **L'Última Arrel**: l'Iri i la Vet, de nenes, han de tornar a encendre l'internet dels fongs d'un bosc vell abans que hi arribi el formigó. | [games/ultima-arrel](games/ultima-arrel/README.md) |

Suma Zero, Ni un ou i Aigua Verne es juguen sense barra de verbs, també amb el dit en un mòbil apaïsat: tocar una cosa
la mira la primera vegada i després en fa l'acció (amb el ratolí, per defecte el clic esquerre mira i el dret fa l'acció), i
mantenir premut obre el menú d'accions (la interfície tàctil
compartida, [adapters/benne/tactil](adapters/benne/tactil/index.ts)). Ferro-9 manté la barra de verbs.

## Què és compartit i què és de cada joc

```
packages/narrative-core/   MOTOR NARRATIU: estat, condicions, diàlegs, missions, pistes, finals (TS pur)
packages/benne/            MOTOR DE BENNE: un de sol; cada joc en té una còpia de només lectura
adapters/benne/            L'ADAPTADOR: porta el contingut de qualsevol joc al seu projecte Benne
tools/                     EINES: validate, jugar, fitxes, revisio, profunditat, schemas
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

## Skills de Claude Code

Encàrrecs que Claude Code ja sap fer. Es criden amb `/<nom>` des de la carpeta de treball (la que conté `jocs/`,
`malaherbasoft/` i `tasques/`), i viuen a `../.claude/skills/<nom>/SKILL.md`, fora d'aquest repo.

| Skill | Què fa |
|---|---|
| `/tasca` | Apunta, consulta o actualitza les tasques pendents (`tasques/NNN-slug.md`, amb el seu visor). Separa el que escrius de pressa en una tasca per cosa, endevina el joc i el tipus, i hi posa context dels fitxers del joc. |
| `/revisa-joc <joc>` | Juga una partida real al navegador, sense so, com una jugadora i sense mirar la solució. Per cada cosa millorable (art, animacions, personatges, trencaclosques, diàlegs, interfície, rejugabilitat, errors de consola) apunta una tasca amb `/tasca`. No toca el joc. |
| `/resol-tasques [joc \| tipus \| ids]` | Resol les tasques obertes de la més prioritària a la menys, per tandes d'un mateix joc (un sol sync per tanda). Comprova cada una amb els tests i al navegador, fa un commit a `main` per tasca i hi apunta el hash. **No fa mai push.** Deixa les `idea`, les que tenen preguntes obertes i les veus: al final et fa les preguntes juntes i, si falten veus, apunta una sola tasca per joc per regenerar-les. |

`/revisa-joc` i `/resol-tasques` fan servir el mateix navegador: `../.claude/skills/revisa-joc/navegador.mjs`, un
Chromium amb `--mute-audio` (i el joc amb `?voices=off`) que es queda obert entre ordres, perquè Claude pugui jugar
clic a clic mirant captures. També es pot fer servir a mà:

```bash
NAV="node ../.claude/skills/revisa-joc/navegador.mjs"
$NAV obre "http://localhost:5173/?voices=off"   # després d'npm run dev -w <joc>
$NAV foto                                       # escriu el camí de la captura
$NAV clic 640 568                               # clic, dret, prem, mou, arrossega, tecla, fotos, js, consola, tanca
```

El motor té la seva pròpia skill, `bennescript`, a `packages/benne/.claude/skills/`.

## Un joc nou

Tot el procés, de la idea a la web pública, amb una llista de comprovació per fase:
[docs/guia-joc-nou.md](docs/guia-joc-nou.md). L'esquelet:

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

**Benne per dins** ([docs/benne-per-dins.html](docs/benne-per-dins.html), s'obre al navegador): un esquema per a
programadors de com s'acoblen el contingut, el nucli, l'adaptador i el motor, què fa cada fitxer TypeScript, i què
ofereix Benne per donar més profunditat a les sales (escala per regions, scroll, parallax, tint, pujades i
baixades). Les xifres d'ús («0 de 27 sales») són d'Aigua Verne al novembre de 2026.

**Aventures: cap on anem** ([docs/aventures-cap-on-anem.html](docs/aventures-cap-on-anem.html)): com han evolucionat
les aventures gràfiques (barra de verbs, veus, mòbil) i tres camins per als propers jocs: com ara, modernitzar
(sense barra, tàctil) o canviar d'estil. Les xifres dels nostres jocs són del novembre de 2026.
