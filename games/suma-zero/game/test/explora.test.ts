/**
 * Exploració: la partida sencera (amb tots els aliats i repartint-ho tot: «La taula llarga») que, cada vegada que una
 * protagonista entra en una sala nova (a cada acte), ho mira tot. Només s'executa amb EXPLORA=<fitxer>, i hi escriu la
 * transcripció (per llegir-la com una jugadora), amb els tres finals al final.
 */
import { it } from 'vitest';
import { writeFileSync } from 'node:fs';
import { jugarActe1, jugarActe2, jugarActe3, partida } from './partida.js';

it.skipIf(!process.env.EXPLORA)('exploració', () => {
  const { n, p } = partida({ fins: 'escapada' });
  const vist = new Set<string>();
  let escombrant = false;
  const escombra = () => {
    const room = p.room!;
    const clau = `${p.active}@${room}`;
    if (vist.has(clau) || escombrant) return;
    vist.add(clau);
    escombrant = true;
    p.transcript.push(`\n=== ${p.active} a ${room} ===`);
    for (const h of Object.keys(n.content.rooms[room]!.hotspots ?? {}).filter((h) => n.isHotspotVisible(room, h))) {
      if (p.room !== room) break;
      p.transcript.push(`> look ${h}`);
      try { p.do('look', h); } catch (e) { p.transcript.push(`!! ${(e as Error).message}`); }
    }
    for (const i of p.inventory()) { p.transcript.push(`> look ${i}`); try { p.do('look', { kind: 'item', id: i }); } catch { /* */ } }
    const h = n.requestHint();
    p.transcript.push(`? PISTA ${h ? `[${h.id}${h.who ? ` diu ${h.who}` : ''}] ${h.text}` : n.noHintText()}`);
    escombrant = false;
  };
  const q = new Proxy(p, {
    get(t, prop, r) {
      const v = Reflect.get(t, prop, r);
      if (typeof v !== 'function' || !['do', 'use', 'talk', 'goTo', 'switchTo'].includes(String(prop))) return v;
      return (...a: unknown[]) => {
        if (!escombrant) p.transcript.push(`>> ${String(prop)} ${JSON.stringify(a)}`);
        const res = (v as (...x: unknown[]) => unknown).apply(t, a); escombra(); return res;
      };
    },
  });
  escombra();
  p.transcript.push('\n######## ACTE 1'); jugarActe1(q, { entrepa: true, sacrifici: 'pizza' }); vist.clear();
  p.transcript.push('\n######## ACTE 2'); jugarActe2(q, { aliats: true }); vist.clear();
  p.transcript.push('\n######## ACTE 3'); jugarActe3(q, { mobil: 'pons', repartir: true, neta: true });
  const out = [...p.transcript];
  for (const f of ['final_base', 'final_hores', 'final_taula']) {
    const e = n.ending(f);
    out.push(`\n######## FINAL ${f}`, ...e.scene.map((l) => `${l.who}: ${l.text}`), `[${e.title}] ${e.text}`, ...e.credits.map((l) => `${l.who}: ${l.text}`));
  }
  writeFileSync(process.env.EXPLORA!, out.join('\n'));
});
