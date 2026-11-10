/**
 * `npm run revisio`: escriu guio/revisio.md, totes les variants de text del joc amb la seva condició,
 * en text pla i en l'ordre en què el motor les prova (la primera que encaixa). Es llegeix com un guió:
 * és on es veuen els forats de coherència (una línia que es pot dir abans d'hora, un objecte que
 * no té resposta per a «ja està fet»...) sense haver de jugar. Es regenera; no s'edita a mà.
 *
 * `npm run revisio -- <sala|objecte|diàleg>` només en mostra una part, i l'escriu al terminal.
 */
import { writeFileSync } from 'node:fs';
import { fileURLToPath } from 'node:url';
import { Localizer, type Condition, type DialogueLineDef, type Effect, type InteractionDef } from '@aventura/narrative-core';
import { loadGameFromDisk } from './load-game.js';

const { content, locales } = loadGameFromDisk();
const t = new Localizer(content.manifest.defaultLocale, locales);
const filtre = process.argv[2];

const OPS: Record<string, string> = { '==': '=', '!=': '≠', '>': '>', '>=': '≥', '<': '<', '<=': '≤' };

/** Una condició en paraules. */
export function cond(c: Condition): string {
  if ('all' in c) return c.all.map((x) => paren(x)).join(' i ');
  if ('any' in c) return c.any.map((x) => paren(x)).join(' o ');
  if ('not' in c) return `no (${cond(c.not)})`;
  if ('flag' in c) return c.is === false ? `NO ${c.flag}` : c.flag;
  if ('var' in c) return `${c.var} ${OPS[c.op] ?? c.op} ${JSON.stringify(c.value)}`;
  if ('hasItem' in c) return `${c.is === false ? 'no té' : 'té'} ${c.hasItem}${c.who ? ` (${c.who})` : ''}`;
  if ('protagonist' in c) return `juga ${c.protagonist}`;
  if ('remembers' in c) return `${c.is === false ? 'no ' : ''}${c.remembers.who} recorda ${c.remembers.fact}${c.remembers.atLeast ? ` ×${c.remembers.atLeast}` : ''}`;
  if ('relation' in c) return `relació ${c.relation.who} ${OPS[c.relation.op] ?? c.relation.op} ${c.relation.value}`;
  if ('quest' in c) return `missió ${c.quest}: ${[c.status].flat().join('/')}`;
  if ('objective' in c) return `${c.is === false ? 'pendent' : 'fet'} ${c.objective.quest}.${c.objective.objective}`;
  if ('visited' in c) return `${c.is === false ? 'no ha estat a' : 'ha estat a'} ${c.visited}`;
  if ('inRoom' in c) return `a ${c.inRoom}`;
  if ('seen' in c) return `${c.is === false ? 'no ha vist' : 'ha vist'} ${c.seen.dialogue}.${c.seen.node}`;
  if ('chosen' in c) return `${c.is === false ? 'no ha triat' : 'ha triat'} ${c.chosen.dialogue}.${c.chosen.node}.${c.chosen.choice}`;
  return JSON.stringify(c);
}
const paren = (c: Condition) => ('all' in c || 'any' in c ? `(${cond(c)})` : cond(c));

function effect(e: Effect): string {
  if ('setFlag' in e) return e.value === false ? `−${e.setFlag}` : `+${e.setFlag}`;
  if ('setVar' in e) return `${e.setVar} := ${JSON.stringify(e.value)}`;
  if ('addVar' in e) return `${e.addVar} ${e.amount >= 0 ? '+' : '−'}= ${Math.abs(e.amount)}`;
  if ('giveItem' in e) return `rep ${e.giveItem}${e.who ? ` (${e.who})` : ''}`;
  if ('takeItem' in e) return `perd ${e.takeItem}${e.who ? ` (${e.who})` : ''}`;
  if ('remember' in e) return `${e.remember.who} recorda ${e.remember.fact}`;
  if ('forget' in e) return `${e.forget.who} oblida ${e.forget.fact}`;
  if ('relation' in e) return `relació ${e.relation.who} ${e.relation.change >= 0 ? '+' : ''}${e.relation.change}`;
  if ('startQuest' in e) return `comença ${e.startQuest}`;
  if ('completeObjective' in e) return `objectiu ${e.completeObjective.quest}.${e.completeObjective.objective}`;
  if ('completeQuest' in e) return `completa ${e.completeQuest}`;
  if ('failQuest' in e) return `falla ${e.failQuest}`;
  if ('ending' in e) return `FINAL ${e.ending}`;
  if ('event' in e) return `esdeveniment ${e.event}`;
  return JSON.stringify(e);
}

const speaker = (who: string) =>
  who === 'player' ? 'JUGADORA' : who === 'narrator' ? 'NARRADOR' : who === 'title' ? 'TÍTOL' : t.t(content.characters[who]?.name ?? who).toUpperCase();

function lines(list: DialogueLineDef[] = [], indent: string) {
  let out = '';
  for (const l of list) {
    const so = l.sound ? `[SO: ${l.sound}] ` : '';
    const si = l.if ? ` ⟨si ${cond(l.if)}⟩` : '';
    out += `${indent}${so}${speaker(l.who)}: ${t.t(l.text)}${si}\n`;
    if (l.effects?.length) out += `${indent}  ⇒ ${l.effects.map(effect).join(', ')}\n`;
  }
  return out;
}

function interaction(i: InteractionDef, indent = '    ') {
  const verbs = [i.verb].flat().join('/');
  const amb = i.item ? ` + ${i.item === '*' ? 'qualsevol objecte' : i.item}` : '';
  let out = `${indent}• ${verbs}${amb}${i.once ? ' (una vegada)' : ''} — ${i.if ? `si ${cond(i.if)}` : 'SEMPRE'}\n`;
  out += lines(i.lines, `${indent}    `);
  const fx = [...(i.effects ?? []).map(effect)];
  if (i.action) fx.push(`acció ${i.action.name}`);
  if (i.dialogue) fx.push(`diàleg ${i.dialogue}`);
  if (i.goTo) fx.push(`→ ${i.goTo}`);
  if (fx.length) out += `${indent}    ⇒ ${fx.join(', ')}\n`;
  return out;
}

/** Interaccions que no es poden donar mai: una de SEMPRE (sense `if` ni `once`) n'hi ha al damunt per al mateix verb i objecte. */
function hidden(list: InteractionDef[] = []) {
  const out: string[] = [];
  list.forEach((later, j) => {
    for (const verb of [later.verb].flat()) {
      const before = list.slice(0, j).find((i) => !i.if && !i.once && (i.item ?? '') === (later.item ?? '') && [i.verb].flat().some((v) => v === verb || v === '*'));
      if (before) out.push(`«${verb}${later.item ? ` + ${later.item}` : ''}» ${later.if ? `(si ${cond(later.if)}) ` : ''}no surt mai: la tapa una interacció SEMPRE de més amunt`);
    }
  });
  return out;
}

let md = `# Revisió de textos\n\n> Generat amb \`npm run revisio\` a partir de \`game/data/\`. No l'editis a mà.\n>\n`;
md += `> Per a cada cosa, les interaccions en l'ordre en què el motor les prova: s'agafa **la primera que encaixa**.\n`;
md += `> Una interacció «SEMPRE» que no és l'última amaga les de sota.\n\n`;

const parts: string[] = [];

for (const [id, r] of Object.entries(content.rooms)) {
  if (filtre && filtre !== id) continue;
  let s = `## Sala ${t.t(r.name)} · \`${id}\`${r.protagonist ? ` (${r.protagonist})` : ''}${r.cutscene ? ' — cinemàtica' : ''}\n\n\`\`\`\n`;
  if (r.onEnter?.length) {
    s += `EN ENTRAR\n`;
    for (const i of r.onEnter) s += interaction(i);
    s += '\n';
  }
  for (const [did, d] of Object.entries(r.decor ?? {})) s += `DECORAT ${did} — es veu si ${cond(d.visibleIf)}\n`;
  if (Object.keys(r.decor ?? {}).length) s += '\n';
  for (const [hid, h] of Object.entries(r.hotspots)) {
    s += `${hid.toUpperCase()} «${h.name ? t.t(h.name) : '—'}»${h.visibleIf ? ` — hi és si ${cond(h.visibleIf)}` : ''}\n`;
    for (const i of h.interactions ?? []) s += interaction(i);
    for (const w of hidden(h.interactions)) s += `    ⚠ ${w}\n`;
    s += '\n';
  }
  parts.push(s + '```\n');
}

for (const [id, it] of Object.entries(content.items)) {
  if (filtre && filtre !== id) continue;
  let s = `## Objecte ${t.t(it.name)} · \`${id}\`\n\n\`\`\`\n`;
  for (const i of it.interactions ?? []) s += interaction(i, '');
  if (!it.interactions?.length) s += `(sense interaccions: només el text per defecte)\n`;
  parts.push(s + '```\n');
}

for (const [id, d] of Object.entries(content.dialogues)) {
  if (filtre && filtre !== id) continue;
  let s = `## Diàleg \`${id}\` amb ${t.t(content.characters[d.with]?.name ?? d.with)}\n\n\`\`\`\n`;
  const starts = typeof d.start === 'string' ? [{ node: d.start }] : d.start;
  s += `COMENÇA A: ${starts.map((e) => ('if' in e && e.if ? `${e.node} (si ${cond(e.if)})` : e.node)).join(' · ')}\n\n`;
  for (const [nid, node] of Object.entries(d.nodes)) {
    s += `[${nid}]\n`;
    s += lines(node.lines, '    ');
    if (node.effects?.length) s += `    ⇒ ${node.effects.map(effect).join(', ')}\n`;
    for (const ch of node.choices ?? []) {
      const tags = [ch.once && 'una vegada', ch.if && `si ${cond(ch.if)}`].filter(Boolean).join(', ');
      s += `    ▸ ${t.t(ch.text)}${tags ? ` ⟨${tags}⟩` : ''} → ${ch.next ?? '(es queda)'}${ch.end ? ' · FI' : ''}\n`;
      if (ch.effects?.length) s += `        ⇒ ${ch.effects.map(effect).join(', ')}\n`;
    }
    if (node.goto) s += `    ↪ ${node.goto}\n`;
    s += '\n';
  }
  parts.push(s + '```\n');
}

if (!filtre) {
  let s = `## Pistes\n\n\`\`\`\n`;
  for (const [id, h] of Object.entries(content.hints)) {
    s += `${id} — quan ${cond(h.when)} · fins que ${cond(h.doneWhen)}\n`;
    h.levels.forEach((k, i) => (s += `    ${i + 1}. ${t.t(k)}\n`));
  }
  parts.push(s + '```\n');
  let f = `## Finals\n\n\`\`\`\n`;
  for (const [id, e] of Object.entries(content.endings)) {
    f += `${id} «${t.t(e.title)}» — ${e.when ? `quan ${cond(e.when)}` : 'només forçat'}\n`;
    f += lines(e.scene, '    ');
    f += `    ${t.t(e.text)}\n`;
  }
  parts.push(f + '```\n');
}

if (filtre) {
  if (!parts.length) {
    console.error(`✖ No hi ha cap sala, objecte ni diàleg «${filtre}».`);
    process.exit(1);
  }
  console.log(parts.join('\n'));
} else {
  writeFileSync(fileURLToPath(new URL('../guio/revisio.md', import.meta.url)), md + parts.join('\n'));
  console.log(`✔ guio/revisio.md (${parts.length} seccions)`);
}
