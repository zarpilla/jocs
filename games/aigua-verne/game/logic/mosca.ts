/**
 * La Mosca (guio/guio.md, «Regles del món · 3»): el dron de la Vet porta un objecte a l'altra protagonista si són al
 * mateix planeta (la nau compta com el planeta on és aterrada) i no al palau. «Fer servir un objecte amb la Mosca.»
 * Hi cap el que porta `mosca: true` a items.json; `no_mosca: "<clau>"` diu per què no.
 */
import type { ActionResult, Narrative } from '@aventura/narrative-core';

import { OBJECTES_MOSCA, perObjecte } from './perobjecte.js';

export const MOSCA_TEXTS = [
  'mosca.envia', 'mosca.arriba', 'mosca.lluny', 'mosca.palau', 'mosca.no_hi_cap', 'mosca.aqui',
  ...OBJECTES_MOSCA.flatMap((item) => [`mosca.envia.${item}.iri`, `mosca.envia.${item}.vet`, `mosca.arriba.${item}`]),
];

const PLANETA: Record<string, string> = {
  granja_pati: 'terra2', granja_casa: 'terra2', granja_graner: 'terra2', port_terra2: 'terra2',
  aqua_port: 'aqua', aqua_fons: 'aqua', casa_juana: 'aqua',
  ferrum_carrer: 'ferrum', ferrum_sindicat: 'ferrum', fosa_forn: 'ferrum', fosa_colada: 'ferrum',
  verdant_jardi: 'verdant', verdant_cobert: 'verdant', verdant_residencia: 'verdant',
  palau_galeria: 'palau', palau_salo: 'palau', palau_servei: 'palau', palau_control: 'palau',
};

/** El planeta d'una sala (la nau: on és aterrada). */
export function planetaDe(n: Narrative, sala: string | null): string | null {
  if (!sala) return null;
  if (sala.startsWith('cantimplora_')) return String(n.getVar('planeta') ?? '');
  return PLANETA[sala] ?? null;
}

const player = (text: string, params?: Record<string, string>) => ({ who: 'player' as const, text, params });

export function enviar(n: Narrative, item: string): ActionResult {
  const who = n.world.activeProtagonist();
  const other = n.content.manifest.protagonists.find((p) => p !== who)!;
  const aqui = n.world.currentRoom();
  const alla = n.world.protagonistRoom?.(other) ?? null;
  const props = n.content.items[item]?.props ?? {};
  if (typeof props.no_mosca === 'string') return { lines: [player(props.no_mosca)] };
  if (planetaDe(n, aqui) === 'palau') return { lines: [player('mosca.palau')] };
  if (props.mosca !== true) return { lines: [player('mosca.no_hi_cap')] };
  if (aqui === alla) return { lines: [player('mosca.aqui')] };
  if (!alla || planetaDe(n, aqui) !== planetaDe(n, alla)) return { lines: [player('mosca.lluny')] };
  n.apply([{ takeItem: item }, { giveItem: item, who: other }]);
  return {
    lines: [
      { ...player(perObjecte(n, 'mosca.envia', item, other)), sound: 'mosca' },
      { who: other, text: perObjecte(n, 'mosca.arriba', item) },
    ],
  };
}

export function installMosca(n: Narrative) {
  n.registerAction('mosca.enviar', ({ args }) => enviar(n, String(args.item ?? '')));
}
