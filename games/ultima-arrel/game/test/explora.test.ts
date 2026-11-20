/**
 * Exploració: a cada escena, mira totes les coses i els objectes, prova verbs que no toquen i demana les pistes. Només
 * s'executa amb EXPLORA=<fitxer>, i hi escriu la transcripció (per llegir-la com una jugadora).
 */
import { it } from 'vitest';
import { writeFileSync } from 'node:fs';
import type { Narrative } from '@aventura/narrative-core';
import { item, partida, type Jugador } from './partida.js';

function escombra(p: Jugador, n: Narrative, verbs: string[] = ['look']) {
  const room = p.room!;
  const hs = Object.keys(n.content.rooms[room]!.hotspots ?? {}).filter((h) => n.isHotspotVisible(room, h));
  for (const v of verbs) for (const h of hs) {
    if (v === 'talkTo' && !n.content.characters[h]) continue;
    p.transcript.push(`> ${v} ${h}`);
    try { p.do(v, h); } catch (e) { p.transcript.push(`!! ${(e as Error).message}`); }
    if (p.room !== room) { p.transcript.push(`!! (ha sortit a ${p.room})`); return; }
  }
}
function inventari(p: Jugador) {
  for (const i of p.inventory()) { p.transcript.push(`> look ${i}`); p.do('look', item(i)); }
}
function pistes(p: Jugador, n: Narrative, k = 3) {
  for (let j = 0; j < k; j++) {
    const h = n.requestHint();
    p.transcript.push(`? PISTA ${h ? `[${h.id} ${h.level}/${h.levels}${h.who ? ` diu ${h.who}` : ''} → ${h.targets.join(',')}]` : ''} ${h ? h.text : n.noHintText()}`);
  }
}

it.skipIf(!process.env.EXPLORA)('exploració', () => {
  const { n, p } = partida();
  const marca = (s: string) => p.transcript.push(`\n=== ${s} ===`);
  const fes = (f: () => void) => { try { f(); } catch (e) { p.transcript.push(`!! ${(e as Error).message}`); } };
  marca('E1 en arribar'); escombra(p, n); inventari(p); pistes(p, n);
  marca('E1 provant'); fes(() => p.do('walkTo', 'cami')); fes(() => p.do('use', 'porta_roure'));
  fes(() => p.use('centim', item('llimona'))); fes(() => p.do('use', item('walkie'))); fes(() => p.do('use', item('walkie')));
  fes(() => p.do('push', 'estaca')); pistes(p, n, 2); fes(() => p.do('pull', 'estaca'));
  pistes(p, n, 1);
  fes(() => p.do('use', 'campaneta'));
  marca('E2 en arribar'); escombra(p, n); inventari(p); pistes(p, n);
  fes(() => p.use('llimona', 'radar')); fes(() => p.talk('espora', 'qui', 'miceli', 'node', 'melmelada', 'que', 'adeu'));
  fes(() => p.do('use', item('walkie')));
  fes(() => p.do('walkTo', 'escala')); fes(() => p.do('pickUp', 'cargol')); fes(() => p.do('walkTo', 'porta_roure'));
  fes(() => p.use('cargol', item('llimona'))); fes(() => p.use('centim', item('llimona_cargol'))); fes(() => p.use('pila_llimona', 'radar'));
  marca('E2 radar encès'); escombra(p, n); pistes(p, n);
  fes(() => p.do('pickUp', 'fil_saba')); pistes(p, n);
  fes(() => p.use('fil_saba', 'arrel_1')); fes(() => p.use('lupa', 'arrel_3')); fes(() => p.use('fil_saba', 'arrel_2'));
  marca('E2 xarxa encesa'); escombra(p, n); inventari(p); pistes(p, n);
  fes(() => p.use('walkie', 'corn'));
  marca('E3 en arribar'); escombra(p, n); escombra(p, n, ['talkTo']); inventari(p); pistes(p, n);
  fes(() => p.talk('urtica', 'avia', 'espora', 'apunteu', 'adeu')); fes(() => p.do('use', 'gronxador')); fes(() => p.do('walkTo', 'branca'));
  fes(() => p.do('use', item('walkie')));
  fes(() => p.use('pot_melmelada', 'card'));
  marca('E3 amigues'); escombra(p, n); escombra(p, n, ['talkTo']); inventari(p); pistes(p, n);
  fes(() => p.talk('urtica', 'pla', 'flor', 'empeny'));
  marca('E4 en arribar'); escombra(p, n); escombra(p, n, ['talkTo']); inventari(p); pistes(p, n);
  fes(() => p.do('use', 'comporta')); pistes(p, n, 1); fes(() => p.talk('gripau', 'vaga', 'ajuda'));
  fes(() => p.use('estaca', 'tap_plastics'));
  marca('E4 aigua'); escombra(p, n); inventari(p); pistes(p, n, 2);
  fes(() => p.talk('bufo'));
  marca('E5 en arribar'); escombra(p, n); inventari(p); pistes(p, n);
  fes(() => p.do('use', 'altaveu')); fes(() => p.talk('pla', 'bosc', 'vells', 'ocells', 'aire', 'altaveu', 'adeu'));
  fes(() => p.do('look', item('kit'))); fes(() => p.do('use', item('walkie')));
  fes(() => p.do('pull', 'arbre_wifi')); pistes(p, n);
  fes(() => p.do('use', 'altaveu')); fes(() => p.do('use', 'altaveu')); fes(() => p.do('use', 'altaveu'));
  marca('E6 en arribar'); escombra(p, n); escombra(p, n, ['talkTo']); inventari(p); pistes(p, n);
  fes(() => p.do('talkTo', 'urtica')); fes(() => p.do('use', item('walkie')));
  fes(() => p.use('kit', 'bastida')); fes(() => p.do('open', item('kit')));
  marca('E6a caseta'); inventari(p); pistes(p, n);
  fes(() => p.use('caseta_paper', 'bastida'));
  marca('E6a amagatall'); escombra(p, n); escombra(p, n, ['talkTo']); pistes(p, n);
  fes(() => p.talk('txell', 'canal7'));
  marca('E6b en arribar'); escombra(p, n); escombra(p, n, ['talkTo']); inventari(p); pistes(p, n);
  fes(() => p.use('walkie', 'altaveu')); fes(() => p.do('talkTo', 'bufo'));
  fes(() => p.use('xiulet', 'sensors'));
  marca('E6b discurs 2'); escombra(p, n); pistes(p, n, 2); fes(() => p.do('use', item('walkie')));
  fes(() => p.use('walkie', 'altaveu')); fes(() => p.do('talkTo', 'bufo'));
  marca('E6b discurs 3'); pistes(p, n, 2); fes(() => p.do('talkTo', 'pla')); fes(() => p.use('walkie', 'altaveu'));
  marca('E7 en arribar'); escombra(p, n); escombra(p, n, ['talkTo']); fes(() => p.do('look', 'iri')); fes(() => p.do('talkTo', 'iri'));
  inventari(p); pistes(p, n); fes(() => p.do('use', item('walkie')));
  fes(() => p.do('use', 'taula'));
  writeFileSync(process.env.EXPLORA!, p.transcript.join('\n'));
});
