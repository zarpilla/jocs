/**
 * Exploració: la partida sencera (amb la Mira i el Cargol, el final 3) que, cada vegada que una protagonista entra en
 * una sala nova (a cada acte), ho mira tot i parla amb tothom. Només s'executa amb EXPLORA=<fitxer>, i hi escriu la
 * transcripció (per llegir-la com una jugadora), amb els tres finals al final.
 */
import { it } from 'vitest';
import { writeFileSync } from 'node:fs';
import { jugarActe1, jugarActe2, jugarActe3, partida, texts } from './partida.js';

it.skipIf(!process.env.EXPLORA)('exploració', () => {
  const { n, p, world } = partida({ fins: 'fugida_completada' });
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
  p.transcript.push('\n######## ACTE 1'); jugarActe1(q); vist.clear();
  p.transcript.push('\n######## ACTE 2'); jugarActe2(q, { mira: true, cargol: true }); vist.clear();
  p.transcript.push('\n######## ACTE 3');
  jugarActe3(q, {
    vet: () => {
      q.do('open', 'porta_passadis'); q.talk('guardia', 'qui'); q.do('open', 'porta_memoria'); q.do('open', 'vitrina');
      q.talk('cargol_vell', 'qui'); q.do('open', 'porta_passadis'); q.talk('guardia', 'vitrina'); q.do('open', 'porta_memoria');
      q.use('clau_vitrina', 'vitrina'); q.use('placa_cargol', 'cargol_vell'); q.do('open', 'porta_passadis'); q.do('open', 'porta_hangar');
    },
    iri: () => { q.use('planols', 'mira'); },
  });
  const out = [...p.transcript];
  for (const f of ['fugida', 'veritat', 'correspondencia']) {
    const e = n.ending(f);
    out.push(`\n######## FINAL ${f}`, ...e.scene.map((l) => `${l.who}: ${l.text}`), `[${e.title}] ${e.text}`, ...e.credits.map((l) => `${l.who}: ${l.text}`));
  }
  void world; void texts;
  writeFileSync(process.env.EXPLORA!, out.join('\n'));
});
