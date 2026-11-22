/**
 * Situacions per a les captures (adapters/benne/tools/captures.mjs): l'estat de la partida en alguns punts, i les sales
 * on posar-hi les protagonistes. Només amb SITUACIONS=<fitxer.json>.
 */
import { it } from 'vitest';
import { writeFileSync } from 'node:fs';
import { partida } from './partida.js';
import { acte1, acte2, acte3, punt } from './cami.js';

const SALES: Record<string, [string, string][]> = {
  e1: [['iri', 'granja_pati'], ['iri', 'granja_casa'], ['vet', 'granja_graner']],
  e2: [['iri', 'port_terra2'], ['iri', 'cantimplora_pont'], ['vet', 'cantimplora_bodega']],
  e3: [['vet', 'aqua_port'], ['iri', 'aqua_fons'], ['iri', 'casa_juana']],
  e4: [['iri', 'ferrum_carrer'], ['iri', 'ferrum_sindicat'], ['vet', 'fosa_forn'], ['iri', 'fosa_colada']],
  e5: [['vet', 'verdant_jardi'], ['vet', 'verdant_cobert'], ['iri', 'verdant_residencia']],
  e7: [['iri', 'palau_galeria'], ['iri', 'palau_salo'], ['vet', 'palau_servei'], ['vet', 'palau_control']],
  e8: [['iri', 'palau_salo'], ['vet', 'palau_control']],
};

it.skipIf(!process.env.SITUACIONS)('situacions', () => {
  const { n, p, world } = partida();
  const out: unknown[] = [];
  punt.f = (tag) => {
    for (const [who, room] of SALES[tag] ?? []) {
      const rooms = Object.fromEntries(world.rooms);
      rooms[who] = room;
      const other = who === 'iri' ? 'vet' : 'iri';
      if (!rooms[other]) rooms[other] = room;
      out.push({ nom: `${tag}_${room}`, state: n.snapshot(), rooms, active: who,
        items: { iri: world.items('iri'), vet: world.items('vet') } });
    }
  };
  acte1(p, n);
  acte2(p, n, true);
  acte3(p, n);
  writeFileSync(process.env.SITUACIONS!, JSON.stringify(out));
});
