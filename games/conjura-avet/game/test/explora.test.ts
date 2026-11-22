/**
 * Exploració: a cada moment del camí, mira totes les coses i els objectes, prova verbs que no toquen i demana les
 * pistes. Només s'executa amb EXPLORA=<fitxer>, i hi escriu la transcripció (per llegir-la com una jugadora).
 */
import { it } from 'vitest';
import { writeFileSync } from 'node:fs';
import type { Narrative } from '@aventura/narrative-core';
import { item, partida, type Jugador } from './partida.js';
import { acte1, acte2, acte3, acte4, tutorial } from './cami.js';

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
    p.transcript.push(`? PISTA ${h ? `[${h.id} ${h.level}/${h.levels}${h.who ? ` diu ${h.who}` : ''}]` : ''} ${h ? h.text : n.noHintText()}`);
  }
}

it.skipIf(!process.env.EXPLORA)('exploració', () => {
  const marca = (p: Jugador, s: string) => p.transcript.push(`\n=== ${s} (${p.active} a ${p.room}) ===`);
  const mira = (p: Jugador, n: Narrative, s: string, verbs = ['look', 'use', 'push', 'pickUp']) => {
    marca(p, s); escombra(p, n, verbs); inventari(p); pistes(p, n);
  };
  const out: string[] = [];
  // 1. El tutorial, abans de fer res.
  { const { n, p } = partida(); mira(p, n, 'TUTORIAL en arribar'); out.push(...p.transcript); }
  // 2. Acte 1 obert: les dues a cada sala.
  { const { n, p } = partida(); tutorial(p, n);
    mira(p, n, 'ACTE 1 Iri a l\'avet');
    p.switchTo('vet'); mira(p, n, 'ACTE 1 Vet a l\'avet');
    p.do('walkTo', 'carrer'); mira(p, n, 'ACTE 1 Vet a la plaça', ['look', 'talkTo', 'use']);
    p.do('walkTo', 'carrer'); p.do('walkTo', 'porta_monestir'); mira(p, n, 'ACTE 1 Vet al claustre', ['look', 'talkTo']);
    p.switchTo('iri'); p.do('walkTo', 'cami_riu'); mira(p, n, 'ACTE 1 Iri al pont', ['look', 'talkTo', 'push', 'pull']);
    out.push(...p.transcript); }
  // 3. Acte 2 i següents: un cop fet cada acte.
  { const { n, p } = partida(); acte1(p, n);
    mira(p, n, 'ACTE 2 en començar', ['look', 'talkTo']);
    p.switchTo('iri'); p.do('walkTo', 'porta_bugaderia'); mira(p, n, 'ACTE 2 Iri a la bugaderia');
    p.do('walkTo', 'porta'); p.switchTo('vet'); p.do('walkTo', 'porta_apotecaria'); mira(p, n, 'ACTE 2 Vet a l\'apotecaria');
    out.push(...p.transcript); }
  { const { n, p } = partida(); acte1(p, n); acte2(p, n); mira(p, n, 'ACTE 3 Vet a l\'scriptorium', ['look', 'talkTo']); out.push(...p.transcript); }
  { const { n, p } = partida(); acte1(p, n); acte2(p, n); acte3(p, n);
    mira(p, n, 'ACTE 4 Iri a l\'avet', ['look', 'talkTo']);
    p.switchTo('vet'); p.do('walkTo', 'carrer'); mira(p, n, 'ACTE 4 Vet a la plaça', ['look', 'talkTo']);
    out.push(...p.transcript); }
  { const { n, p } = partida(); acte1(p, n); acte2(p, n); acte3(p, n); acte4(p, n); out.push(...p.transcript); }
  writeFileSync(process.env.EXPLORA!, out.join('\n'));
});
