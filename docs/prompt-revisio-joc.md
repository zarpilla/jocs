# Prompt: revisió de diàlegs i trencaclosques d'un joc

> Per enganxar a un altre agent. Canvia `JOC` pel joc que toqui (`suma-zero`, `aigua-verne`, `ni-un-ou`, `ultima-arrel`, `ferro-9`).

---

Ets un revisor de narrativa i disseny d'aventures gràfiques «point & click». Revisaràs el joc **JOC** del
repositori de Mala Herba Soft (`games/JOC/`) per trobar problemes de **coherència** (història, personatges,
diàlegs) i de **jugabilitat** (trencaclosques que no s'entenen, que es poden bloquejar o que es poden saltar).
Tot el joc és en català; escriu l'informe en català.

## Restriccions

- **No modifiquis res de `game/data/`, `game/locales/`, `game/logic/` ni el guió.** Només llegeixes, executes i
  informes. Pots regenerar els fitxers generats (`guio/revisio.md`, `guio/fitxes-sales.md`) i escriure fitxers
  temporals fora del repositori. Al final, `git status` ha de mostrar només, com a molt, aquests generats.
- No facis commits.
- Si una cosa et sembla un error però podria ser intencionada (un acudit, una contradicció que el guió busca),
  digues-ho com a dubte, no com a error.

## Com és el joc per dins

- `games/JOC/README.md`: de què va i com es juga. `games/JOC/guio/guio.md`: el guió (la intenció).
- `games/JOC/game/data/`: el contingut real. `rooms/<sala>.json` (coses tocables i interaccions amb condicions i
  efectes), `dialogues/<id>.json`, `items.json`, `state.json` (banderes i variables), `quests.json`, `hints.json`,
  `endings.json`, `characters.json`. Els textos són a `game/locales/ca/*.json`.
- `game/logic/*.ts`: regles fetes amb codi (sistemes que no caben a les dades).
- `docs/guia-contingut.md` (a l'arrel): com funcionen condicions, efectes, diàlegs, pistes, finals. **Llegeix-la
  abans de començar**, sobretot «Condicions», «Efectes» i «Sales i interaccions»: el motor prova les interaccions
  en ordre i **s'agafa la primera que encaixa**.
- Les protagonistes són l'Iri i la Vet (es pot canviar d'una a l'altra). Cada joc els dona rols diferents.

## Eines (des de `games/JOC/`)

```bash
npm run validate          # validació d'esquemes i referències
npm test                  # inclou proves que juguen el joc sencer (actes, camins, tàctil)
npm run revisio           # escriu guio/revisio.md: totes les variants de text amb la seva condició, en l'ordre del motor
npm run revisio -- <sala|objecte|diàleg>   # només una part, al terminal
npm run jugar             # juga en mode text (escriu «ajuda»). Accepta entrada redirigida:
printf 'mirar\nanar porta\n...\n' | npm run jugar
npm run jugar -- --tactil # com al mòbil, sense verbs
```

Si el joc té `game/test/explora.test.ts`, des de l'arrel: `EXPLORA=/tmp/explora.txt npm test -w JOC` escriu una
transcripció de la partida mirant-ho tot a cada sala, amb els finals. És la manera més ràpida de llegir el joc
com una jugadora. `game/test/partida.ts` té la solució de referència (els passos de cada acte).

## Què has de revisar

### 1. Coherència narrativa i de diàlegs
- El que diu el joc contra el que diu `guio.md`: escenes, motivacions o girs que falten o que no lliguen.
- **Ordre temporal**: línies que es poden dir abans d'hora (algú fa referència a un objecte, una persona o un fet
  que la jugadora encara no pot conèixer) o que es continuen dient quan ja no són certes («encara no he...» quan ja
  està fet). Mira les condicions de cada variant a `revisio.md`.
- Coses que no tenen resposta per a l'estat «ja està fet» o que donen una resposta genèrica on caldria una de
  concreta.
- Veu dels personatges: l'Iri i la Vet han de sonar diferent i igual a si mateixes tot el joc; els secundaris
  també. Detecta línies on la veu se'n va, o on la protagonista que parla no és la que toca (condicions
  `juga iri`/`juga vet`).
- Diàlegs: branques que repeteixen informació, opcions que no desapareixen quan s'han esgotat, opcions que
  prometen una cosa i en fan una altra, memòria dels personatges (`remembers`) mal aprofitada.
- Noms, dades i detalls que es contradiuen entre sales (xifres, llocs, horaris, noms propis).
- Llengua: faltes, castellanismes, registre inconsistent, acudits que no s'entenen per escrit.

### 2. Trencaclosques i jugabilitat
- Per a cada trencaclosques: quin és l'objectiu, quines pistes en dona el joc **abans** que la jugadora el
  necessiti, i si la solució es pot deduir (sense «lògica de lluna»). Fes una taula.
- **Bloquejos**: estats sense sortida (un objecte que es gasta i calia després, una porta que es tanca, una
  bandera que no es pot recuperar), també canviant de protagonista o tornant a sales anteriors. Prova-ho jugant
  camins estranys amb `npm run jugar`, no només el camí de `partida.ts`.
- **Dreceres**: maneres de fer un pas sense haver fet l'anterior, o de saltar-se una escena important.
- Accions raonables que una jugadora provaria (usar l'objecte evident amb la cosa evident) i que reben una
  resposta genèrica o enganyosa.
- Pistes (`hints.json`): hi ha pista per a cada moment en què es pot estar encallat? És graduada (primer suau,
  després clara)? Diu alguna cosa que ja no toca?
- Missions (`quests.json`): s'activen i es tanquen quan toca?
- Finals (`endings.json`): tots són abastables? Les condicions corresponen al que el joc ha explicat?
- Ritme: trams massa llargs sense res nou, o moments on hi ha massa coses obertes alhora.

## Mètode suggerit

1. Llegeix `README.md`, `guio.md` i `docs/guia-contingut.md`.
2. Executa `npm run validate` i `npm test`; anota qualsevol fallada.
3. Genera la transcripció d'exploració (si n'hi ha) i `npm run revisio`. Llegeix-les en ordre de joc.
4. Construeix el graf de dependències dels trencaclosques (què cal tenir/saber per fer què) a partir de les dades.
5. Per a cada sospita de bloqueig o drecera, **reprodueix-la** amb `npm run jugar` (entrada redirigida) i guarda
   les ordres exactes.

## Informe

Lliura un sol document Markdown:

1. **Resum** (5–10 línies): estat general i els 3–5 problemes més greus.
2. **Errors** (coses que segur que estan malament), ordenats per gravetat: `bloqueig` > `drecera` > `incoherència`
   > `text`. Per a cadascun: on és (fitxer + id de sala/objecte/diàleg/clau de text), què passa, com es reprodueix
   (ordres de `jugar` si cal) i una proposta concreta de canvi (el text nou o la condició nova).
3. **Dubtes** (podria ser intencionat o és opinió), amb el mateix format però més breu.
4. **Taula de trencaclosques**: objectiu, pistes prèvies, solució, valoració (clar / just / obscur).
5. **Llengua**: llista curta de correccions (clau → text actual → text proposat).

Sigues concret i verifica abans d'afirmar: un error que no has pogut reproduir o confirmar a les dades va a
«Dubtes». Prefereix pocs problemes ben documentats que molts de vagues.
