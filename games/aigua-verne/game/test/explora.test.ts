/**
 * Proves d'exploració: coses fora d'ordre i errors a les sincronies. Només s'executa amb EXPLORA=<fitxer>, i hi
 * escriu la transcripció (per llegir-la com un jugador).
 */
import { it } from 'vitest';
import { writeFileSync } from 'node:fs';
import { amb, anar, partida, viatjar } from './partida.js';
import { acte1 } from './cami.js';

it.skipIf(!process.env.EXPLORA)('exploració', () => {
  const { n, p } = partida();
  const marca = (s: string) => p.transcript.push(`\n=== ${s} ===`);
  const prova = (f: () => void) => { try { f(); } catch (e) { p.transcript.push(`!! ${(e as Error).message}`); } };
  acte1(p, n);
  marca('E4: abans de parlar amb en Bru');
  viatjar(p, n, 'ferrum');
  anar(p, n, 'ferrum_carrer');
  prova(() => p.do('walkTo', 'porta_fosa'));
  p.do('look', 'piquet'); p.do('look', 'font'); p.do('look', 'condensador'); p.talk('contractacio', 'no', 'h24', 'aigua_no');
  p.talk('rosa', 'vaga');
  p.talk('comunicador', 'fem');
  anar(p, n, 'ferrum_sindicat');
  p.do('look', 'bagul'); p.do('pickUp', 'bagul');
  p.talk('bru', 'recorda');
  marca('E4: barril');
  amb(p, 'vet');
  anar(p, n, 'cantimplora_bodega');
  p.do('push', 'barril');
  p.talk('barril', 'mirar');
  amb(p, 'iri');
  p.talk('bru', 'canalla', 'lia', 'promesa', 'colada');
  marca('E4: colada fora d’ordre');
  anar(p, n, 'fosa_colada');
  p.use('motlle', 'llit');
  viatjar(p, n, 'aqua'); anar(p, n, 'aqua_fons'); p.do('pickUp', 'sorra'); p.talk('comunicador', 'fem'); p.do('look', 'boies'); p.do('pickUp', 'sorra');
  viatjar(p, n, 'ferrum'); anar(p, n, 'fosa_colada'); p.use('motlle', 'llit');
  amb(p, 'vet'); anar(p, n, 'fosa_forn');
  p.do('pickUp', 'metall');
  p.do('push', 'manxa'); p.do('pickUp', 'metall');
  amb(p, 'iri'); p.talk('grua', 'bolca_buit', 'esquerra', 'avall_c', 'esquerra_final'); amb(p, 'vet'); p.do('use', 'forn'); amb(p, 'iri');
  marca('E4: deixar refredar');
  for (let k = 0; k < 9; k++) { amb(p, 'vet'); p.do('push', 'manxa'); p.do('pickUp', 'metall'); p.do('use', 'rascle'); amb(p, 'iri'); p.do('use', 'llit'); }
  p.talk('comunicador', 'fem');
  return writeFileSync(process.env.EXPLORA!, p.transcript.join('\n'));
});
