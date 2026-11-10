/**
 * La sospita del Director a l'Escena 4 (regles a guio/guio.md, «Regles del món · 2»).
 *
 * La conversa (`dialogues/bonfill.json`) ho fa gairebé tot: el valor inicial segons la preparació, el que
 * suma o resta cada resposta, els gestos del Director i el Dia de la Marmota quan arriba a 100. Aquí només
 * hi ha el que el JSON no sap fer: que mai baixi de 0 i recordar el màxim (`sospita_max`, per a l'Escena 9).
 */
import type { Narrative } from '@aventura/narrative-core';

export function installSospita(n: Narrative) {
  n.onAfterAction((action) => {
    if (action.kind !== 'choice' || action.dialogue !== 'bonfill') return;
    const sospita = Number(n.getVar('sospita') ?? 0);
    if (sospita < 0) n.apply({ setVar: 'sospita', value: 0 });
    if (sospita > Number(n.getVar('sospita_max') ?? 0)) n.apply({ setVar: 'sospita_max', value: Math.min(sospita, 100) });
  });
}
