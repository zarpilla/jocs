/**
 * Objectes gastats (tasca 133). Quan un objecte ja no té cap ús, surt de l'inventari tot sol després de l'acció que
 * l'ha deixat sense feina, perquè els nous no quedin amagats a la segona pàgina. Només hi ha els que no tornen a
 * sortir enlloc més tard: les notes que serveixen per a un sol trencaclosques i les eines d'un sol ús. El segell, la
 * llima, els llapis, la clau anglesa i les notes amb els noms es queden.
 */
import type { Condition, Narrative } from '@aventura/narrative-core';

const ACTE1: Condition = { flag: 'acte1_acabat' };
const COMPORTA: Condition = { flag: 'comporta_oberta' };
const MOTOR: Condition = { flag: 'motor_engegat' };

export const GASTATS: { item: string; quan: Condition }[] = [
  // Acte 1: el plomall ha servit per treure el segell al capatàs, i les dues primeres notes ja són contestades.
  { item: 'plomall', quan: { any: [{ hasItem: 'segell', who: 'iri' }, ACTE1] } },
  { item: 'nota_vet', quan: ACTE1 },
  { item: 'nota_pany', quan: ACTE1 },
  { item: 'nota_iri', quan: ACTE1 },
  // Acte 2: tot el de la comporta.
  { item: 'nota_mida', quan: COMPORTA },
  { item: 'nota_amagatall', quan: COMPORTA },
  { item: 'pols_rovell', quan: COMPORTA },
  { item: 'serra', quan: COMPORTA },
  // Acte 2: la pressió del conducte.
  { item: 'nota_pressio', quan: MOTOR },
  { item: 'nota_massa', quan: MOTOR },
];

const PROTAGONISTES = ['iri', 'vet'];

/**
 * Cada regla neteja l'inventari una sola vegada, a la primera acció en què es compleix: si després algú torna a
 * tenir l'objecte (una prova que l'hi dona), no se li treu. Després de carregar una partida la regla torna a passar
 * un cop, i treu el que s'hagués quedat.
 */
export function installGastats(n: Narrative) {
  const fetes = new Set<string>();
  n.onAfterAction(() => {
    const treure = GASTATS.flatMap(({ item, quan }) => {
      if (!n.check(quan)) {
        fetes.delete(item); // (una partida nova la torna a armar)
        return [];
      }
      if (fetes.has(item)) return [];
      fetes.add(item);
      return PROTAGONISTES.filter((who) => n.check({ hasItem: item, who })).map((who) => ({ takeItem: item, who }));
    });
    if (treure.length) n.apply(treure);
  });
}
