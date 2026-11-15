/**
 * Que no us vegin juntes. Des que l'Iri sap que algú les escolta (el portàtil robat, Escena 4) fins que la Capitana
 * reuneix tothom al menjador (Escena 8; a partir d'aquí ho diuen tot davant de tothom), l'Iri i la Vet no entren a
 * la sala on és l'altra: si les veiessin juntes, sabrien que tramen alguna cosa. Per això, mentrestant, es parlen pel
 * tub i es passen les coses pel muntacàrregues.
 *
 * Es fa amb una interacció més a cada porta (la primera, abans de la que hi porta), i no amb una regla a part: així
 * el plànol (`mapa.ts`), que mira què passaria en caminar per cada porta, també la respecta. Les portes que ja tenen
 * un bloqueig propi abans del `goTo` (la cuina a l'Escena 5) el conserven: la regla va just abans del `goTo`.
 *
 * Els passadissos no compten: s'hi passa, no s'hi està. Les escenes on són juntes per guió (la caixa de cadenes) les
 * hi porten els efectes (`situar`), no les portes.
 */
import type { Condition, InteractionDef, Narrative } from '@aventura/narrative-core';

export const SEPARADES_TEXTS = ['separades.iri', 'separades.vet', 'separades.1', 'separades.tub'];

/** Quan han d'anar separades. */
export const SEPARADES: Condition = { all: [{ flag: 'portatil_robat' }, { flag: 'reunio_comencada', is: false }] };

/** Sales de pas, on sí que es poden creuar. */
export const SALES_DE_PAS = ['passadis', 'passadis_baix'];

const ID = 'separades';

function bloqueig(cap: string, verb: InteractionDef['verb']): InteractionDef {
  const laltra = { any: [
    { all: [{ protagonist: 'iri' }, { inRoom: cap, who: 'vet' }] },
    { all: [{ protagonist: 'vet' }, { inRoom: cap, who: 'iri' }] },
  ] } satisfies Condition;
  return {
    id: ID,
    verb,
    if: { all: [SEPARADES, laltra] },
    lines: [
      { who: 'player', text: 'separades.iri', if: { protagonist: 'iri' } },
      { who: 'player', text: 'separades.vet', if: { protagonist: 'vet' } },
      { who: 'player', text: 'separades.1' },
      { who: 'player', text: 'separades.tub', if: { flag: 'tub_de_veu' } },
    ],
  };
}

/** Afegeix el bloqueig a totes les portes. Es pot cridar més d'una vegada amb el mateix contingut. */
export function installSeparades(n: Narrative) {
  for (const room of Object.values(n.content.rooms)) {
    for (const h of Object.values(room.hotspots ?? {})) {
      const list = h.interactions ?? [];
      if (list.some((i) => i.id === ID)) continue;
      const k = list.findIndex((i) => i.goTo && !i.item);
      if (k < 0) continue;
      const porta = list[k]!;
      if (SALES_DE_PAS.includes(porta.goTo!)) continue;
      list.splice(k, 0, bloqueig(porta.goTo!, porta.verb));
    }
  }
}
