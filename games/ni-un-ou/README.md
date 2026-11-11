# Ni un ou

Aventura gràfica de «point & click» feta amb [Benne](https://benne.games/): un thriller amb humor a bord de
l'**Arenga**, el vaixell més petit d'una ONG que mesura la salut de l'Atlàntic Nord. L'**Iri** (la maquinista) i la
**Vet** (la metgessa nova) descobreixen que les avaries són sabotatges, que algú de bord treballa per a la minera
Skarn, i que tot gira al voltant d'un pot de fang: la Mostra 7.

Guió: [guio/guio.md](guio/guio.md). Art de mostra (la guia d'estil): [guio/art/mostra/](guio/art/mostra/).

> Aquest joc és dins del repositori dels jocs de Mala Herba Soft. El nucli narratiu, l'adaptador de Benne, el motor i
> les eines són a l'arrel i els comparteixen tots els jocs (vegeu el [README de l'arrel](../../README.md)). Aquí hi ha
> el contingut (`game/`), el guió, l'art, la música i el projecte Benne (`ni-un-ou/`).

## Com és

| Què | Com |
|---|---|
| Estructura | Pròleg, 3 actes i 9 escenes, i 3 finals segons els aliats (la Capitana, el Marcel, la Nadia i en Bastida) |
| Protagonistes | L'Iri i la Vet, amb canvi lliure entre elles (menys a les escenes 2 i 4) |
| Sales | **Compartides**: totes dues hi poden ser alhora, es veuen i es poden donar coses (`"protagonists"` al JSON) |
| Comunicació | El walkie (que escolta algú) i, des de l'Escena 5, el tub de veu; el muntacàrregues passa objectes entre la cuina, el rebost i el pont |
| Sincronies | Per torns, com a Suma Zero: la ràdio (la paciència d'en Bastida) i el satèl·lit (el senyal que se'n va) |
| Resolució | 480×270; personatges de ≈83 px amb el sistema de figures de Suma Zero (`adapters/benne/tools/hd/`) |

## Regles en codi (`game/logic/`)

- `sincronia.ts`: els dos passos per torns. No compten mirar, caminar, parlar, el walkie, el quadern, el tub ni les
  respostes que no fan res.
- `muntacarregues.ts`: les tres parades i les safates (una variable per safata).
- `escenes.ts`: canvis d'escena automàtics quan es compleix una condició (el final de l'Escena 2).
- `donar.ts`: donar un objecte a l'altra protagonista quan són a la mateixa sala.

## Ordres

```bash
npm run jugar          # juga en mode text
npm test               # tests: el joc sencer per tots els camins, amb una pista a cada pas
npm run validate       # comprova el contingut
npm run textos         # porta als locales els textos escrits al JSON com a "clau=Text"
npm run sons           # efectes de so (tools/sons.py)
npm run musica         # música (tools/musica.py)
npm run font           # la font del joc
npm run benne:sync     # porta el contingut al projecte Benne
npm run dev            # juga al navegador (cal `npm install` dins ni-un-ou/)
```

## Art

Cada sala és un mòdul `adapters/benne/tools/hd/rooms/<sala>.py` amb el dibuix i la seva geometria (`GEOMETRIA`: on
es clica, on es camina, on és cada personatge); `hd/rooms/arenga.py` té les rampes i les eines comunes, que vénen de
la sala de mostra. `python3 adapters/benne/tools/hd/render.py <sala> <carpeta>` en fa previsualitzacions.

Per veure una escena concreta sense jugar-la, en desenvolupament: `window.__aventura.provar(situació)` (vegeu
`adapters/benne/README.md`).
