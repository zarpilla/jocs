/**
 * Exploració: la partida sencera (amb tots els aliats: «Primera plana») que, cada vegada que una protagonista entra en
 * una sala nova, ho mira tot i després en restaura l'estat, perquè el camí no se'n ressenti. Només s'executa amb
 * EXPLORA=<fitxer>, i hi escriu la transcripció (per llegir-la com una jugadora), amb els tres finals al final.
 */
import { it } from 'vitest';
import { writeFileSync } from 'node:fs';
import { jugarTot, partida } from './partida.js';

it.skipIf(!process.env.EXPLORA)('exploració', () => {
  const { n, p, world } = partida();
  const vist = new Set<string>();
  let escombrant = false;
  const escombra = () => {
    const room = p.room!;
    const clau = `${p.active}@${room}`;
    if (vist.has(clau) || escombrant) return;
    vist.add(clau);
    escombrant = true;
    // Mirar-ho tot no ha de canviar la partida: es desa l'estat i, en acabar, es restaura (menys la transcripció).
    const desat = n.snapshot();
    const mon = structuredClone(Object.fromEntries(Object.entries(world).filter(([, v]) => typeof v !== 'function')));
    p.transcript.push(`\n=== ${p.active} a ${room} ===`);
    for (const h of Object.keys(n.content.rooms[room]!.hotspots ?? {}).filter((h) => n.isHotspotVisible(room, h))) {
      if (p.room !== room) break;
      p.transcript.push(`> look ${h}`);
      try { p.do('look', h); } catch (e) { p.transcript.push(`!! ${(e as Error).message}`); }
    }
    for (const i of p.inventory()) { p.transcript.push(`> look ${i}`); try { p.do('look', { kind: 'item', id: i }); } catch { /* */ } }
    const h = n.requestHint();
    p.transcript.push(`? PISTA ${h ? `[${h.id}${h.who ? ` diu ${h.who}` : ''}] ${h.text}` : n.noHintText()}`);
    n.load(desat);
    for (const [k, v] of Object.entries(mon)) if (k !== 'transcript' && v !== undefined) (world as unknown as Record<string, unknown>)[k] = v;
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
  jugarTot(q);
  const out = [...p.transcript];
  for (const f of ['final_pagina4', 'final_testimonis', 'final_primera']) {
    const e = n.ending(f);
    out.push(`\n######## FINAL ${f}`, ...e.scene.map((l) => `${l.who}: ${l.text}`), `[${e.title}] ${e.text}`, ...e.credits.map((l) => `${l.who}: ${l.text}`));
  }
  writeFileSync(process.env.EXPLORA!, out.join('\n'));
});
