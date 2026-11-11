/**
 * `npm run fitxes`: genera guio/fitxes-sales.md, la llista del que cal crear a
 * l'editor de Benne (o del motor que sigui) per a cada sala: coses, ids,
 * quan apareixen i quins verbs fan alguna cosa. Es regenera; no s'edita a mà.
 */
import { writeFileSync } from 'node:fs';
import { join } from 'node:path';
import { Localizer, type Condition, type InteractionDef } from '@aventura/narrative-core';
import { jocDir } from './joc.js';
import { loadGameFromDisk } from './load-game.js';

const { content, locales } = loadGameFromDisk();
const t = new Localizer(content.manifest.defaultLocale, locales);

const verbsOf = (list: InteractionDef[] = []) => {
  const out = new Set<string>();
  for (const i of list) {
    const verbs = Array.isArray(i.verb) ? i.verb : [i.verb];
    for (const v of verbs) out.add(i.item ? `${v} + ${i.item === '*' ? 'objecte' : i.item}` : v);
  }
  return [...out].join(', ');
};

const cond = (c?: Condition): string => (c ? `\`${JSON.stringify(c)}\`` : 'sempre');

let md = `# Fitxes de sales\n\n> Generat amb \`npm run fitxes\` a partir de \`game/data/\`. No l'editis a mà.\n\n`;
md += `Cada cosa de la llista és un **prop**, un **hotspot** o un **personatge** de la sala a l'editor del motor, `;
md += `amb **aquest id** (o un id del tipus \`<sala>-hotspot-<id>\`). Les que tenen condició s'han de lligar amb \`bindHotspots\`.\n\n`;

const byProtagonist = new Map<string, string[]>();
for (const [id, r] of Object.entries(content.rooms)) {
  const who = r.protagonist ?? (r.protagonists ? '*' : '—');
  byProtagonist.set(who, [...(byProtagonist.get(who) ?? []), id]);
}

for (const [who, rooms] of byProtagonist) {
  md += `## ${who === '—' ? 'Sense protagonista' : who === '*' ? 'Compartides' : t.t(content.characters[who]!.name)}\n\n`;
  for (const id of rooms) {
    const r = content.rooms[id]!;
    md += `### ${t.t(r.name)} · \`${id}\`\n\n| Id | Nom | Tipus | Apareix | Verbs |\n|---|---|---|---|---|\n`;
    for (const [hid, h] of Object.entries(r.hotspots)) {
      const kind = content.characters[hid] ? 'personatge' : h.visibleIf ? 'prop' : 'hotspot / prop';
      const verbs = verbsOf(h.interactions);
      const exits = (h.interactions ?? []).map((i) => i.goTo).filter(Boolean);
      md += `| \`${hid}\` | ${h.name ? t.t(h.name) : '—'} | ${kind}${exits.length ? ` → \`${exits[0]}\`` : ''} | ${cond(h.visibleIf)} | ${verbs} |\n`;
    }
    md += `\n`;
  }
}

md += `## Objectes d'inventari\n\n| Id | Nom | Pes | Altres |\n|---|---|---|---|\n`;
for (const [id, it] of Object.entries(content.items)) {
  const { pes, ...rest } = it.props ?? {};
  md += `| \`${id}\` | ${t.t(it.name)} | ${pes ?? '—'} | ${Object.entries(rest).map(([k, v]) => `${k}: ${v}`).join(', ')} |\n`;
}

const out = join(jocDir(), 'guio/fitxes-sales.md');
writeFileSync(out, md);
console.log(`✔ guio/fitxes-sales.md (${Object.keys(content.rooms).length} sales, ${Object.keys(content.items).length} objectes)`);
