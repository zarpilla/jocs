/**
 * `npm run jugar`: juga el joc en mode text, sense gràfics ni Benne.
 * Serveix per provar el guió i els trencaclosques abans de tenir art.
 */
import { createInterface } from 'node:readline';
import { stdin, stdout } from 'node:process';
import { HeadlessPlayer, MemoryWorld, Narrative, type ResolvedLine } from '@aventura/narrative-core';
import { loadGameLogic } from './joc.js';
import { loadGameFromDisk } from './load-game.js';

const { installGameLogic } = await loadGameLogic();

const { content, locales } = loadGameFromDisk();
const world = new MemoryWorld();
const n = new Narrative({ content, locales, world });
installGameLogic(n);
const p = new HeadlessPlayer(n, world);
p.deferDialogues = true;

const VERBS: Record<string, string> = {
  mirar: 'look', agafar: 'pickUp', usar: 'use', fer: 'use', obrir: 'open', tancar: 'close',
  empenyer: 'push', prémer: 'push', premer: 'push', estirar: 'pull', parlar: 'talkTo', donar: 'give', anar: 'walkTo',
};

const c = { dim: '\x1b[2m', bold: '\x1b[1m', cyan: '\x1b[36m', yellow: '\x1b[33m', green: '\x1b[32m', red: '\x1b[31m', off: '\x1b[0m' };
const rl = createInterface({ input: stdin, output: stdout, terminal: stdin.isTTY });
const input = rl[Symbol.asyncIterator]();

/** Llegeix una línia (funciona igual amb teclat que amb una entrada redirigida). */
async function ask(prompt: string): Promise<string | null> {
  stdout.write(prompt);
  const next = await input.next();
  if (next.done) return null;
  if (!stdin.isTTY) stdout.write(`${next.value}\n`);
  return next.value;
}

function name(who: string) {
  if (who === 'narrator') return '';
  return n.characterName(who);
}

function print(lines: ResolvedLine[]) {
  for (const l of lines) {
    if (l.who === 'title') {
      console.log(`\n${c.bold}${c.cyan}═══ ${l.text} ═══${c.off}\n`);
      continue;
    }
    // El so sona quan comença la línia: s'escriu abans, per revisar el ritme llegint.
    if (l.sound) console.log(`${c.dim}[so: ${l.sound}]${c.off}`);
    const who = name(l.who);
    console.log(who ? `${c.bold}${who}:${c.off} ${l.text}` : `${c.dim}${l.text}${c.off}`);
  }
}

function visibleThings() {
  const room = p.room!;
  const hs = content.rooms[room]?.hotspots ?? {};
  return Object.entries(hs).filter(([id]) => n.isHotspotVisible(room, id));
}

function describeRoom() {
  const room = p.room!;
  console.log(`\n${c.cyan}── ${n.t(content.rooms[room]!.name)} · ${n.characterName(p.active)} ──${c.off}`);
  const things = visibleThings().map(([id, h]) => `${h.name ? n.t(h.name) : id} ${c.dim}[${id}]${c.off}`);
  console.log(`Hi ha: ${things.join(', ')}`);
}

/** Busca per id o nom: primer exacte, després que el contingui ("calderes" → "sala de calderes"). */
function match<T>(word: string, list: T[], keys: (x: T) => string[]): T | undefined {
  const w = word.toLowerCase().replace(/^(el|la|els|les|l'|un|una)\s*/, '');
  if (!w) return undefined;
  const exact = list.find((x) => keys(x).some((k) => k.toLowerCase() === w));
  if (exact) return exact;
  const partial = list.filter((x) => keys(x).some((k) => k.toLowerCase().includes(w)));
  if (partial.length > 1) {
    throw new Error(`«${word}»? Pot ser: ${partial.map((x) => keys(x)[1] ?? keys(x)[0]).join(', ')}.`);
  }
  return partial[0];
}

function findThing(word: string) {
  return match(word, visibleThings(), ([id, h]) => [id, h.name ? n.t(h.name) : id])?.[0];
}

function findItem(word: string) {
  return match(word, p.inventory(), (id) => [id, n.itemName(id)]);
}

async function runDialogue(id: string) {
  let step = n.startDialogue(id);
  print(p.say(step.lines));
  while (!step.ended) {
    step.choices.forEach((ch, i) => console.log(`  ${c.yellow}${i + 1}.${c.off} ${ch.text}`));
    const raw = await ask('> ');
    if (raw === null) return;
    // Un número, o un tros del text de l'opció («fins» → «Fins després»).
    const word = raw.trim().toLowerCase();
    const choice = step.choices[Number(word) - 1] ??
      (word ? step.choices.find((ch) => ch.id === word || ch.text.toLowerCase().includes(word)) : undefined);
    if (!choice) {
      if (raw.trim() === 'sortir') { n.endDialogue(id); return; }
      console.log(`${c.red}Tria un número (o «sortir» per deixar la conversa).${c.off}`);
      continue;
    }
    step = n.choose(id, choice.id);
    print(p.say(step.lines));
  }
}

function help() {
  console.log(`${c.dim}Verbs: ${Object.keys(VERBS).join(', ')}  ·  «usar X amb Y», «donar X a Y»
Altres: mirar (la sala), inventari, canviar, pista, missions, ajuda, sortir
Pots fer servir els noms o els [ids].${c.off}`);
}

async function main() {
  console.log(`${c.bold}${n.t(content.manifest.title)}${c.off} — mode text`);
  help();
  let acabat = false;
  n.on((e) => { if (e.type === 'custom' && e.name === 'final') acabat = true; });
  // El pròleg: les sales de cinemàtica, l'una darrere l'altra (amb el `goTo` de cada una).
  for (let r = content.manifest.intro; r && content.rooms[r]?.cutscene;) {
    const res = n.enterRoom(r);
    if (!res) break;
    print(res.lines);
    r = res.goTo;
  }
  print(p.newGame());
  describeRoom();
  for (;;) {
    const raw = await ask(`${c.green}${p.active}>${c.off} `);
    if (raw === null) break;
    const line = raw.trim();
    if (!line) continue;
    const [cmd = '', ...rest] = line.split(/\s+/);
    const args = rest.join(' ');
    try {
      if (cmd === 'sortir') break;
      if (cmd === 'ajuda') { help(); continue; }
      if (cmd === 'inventari') {
        console.log(p.inventory().map((i) => `${n.itemName(i)} ${c.dim}[${i}]${c.off}`).join(', ') || '(buit)');
        continue;
      }
      if (cmd === 'pista') {
        const h = n.requestHint();
        console.log(`${c.yellow}${h ? h.text : n.t('ui.pista.cap')}${c.off}`);
        continue;
      }
      if (cmd === 'missions') {
        for (const q of n.quests({ status: ['active', 'completed'] })) {
          console.log(`${c.bold}${q.title}${c.off} (${q.status})`);
          for (const o of q.objectives) console.log(`  ${o.done ? '✔' : '·'} ${o.text}`);
        }
        continue;
      }
      if (cmd === 'canviar') {
        if (!n.canSwitch()) { console.log(`${c.dim}${n.t('ui.canvia.encara_no')}${c.off}`); continue; }
        const all = content.manifest.protagonists;
        print(p.switchTo(all[(all.indexOf(p.active) + 1) % all.length]!));
        describeRoom();
        continue;
      }
      if (cmd === 'mirar' && !args) { describeRoom(); continue; }

      const verb = VERBS[cmd];
      if (!verb) { console.log(`${c.red}No t'entenc. Escriu «ajuda».${c.off}`); continue; }

      // «usar X amb Y» / «donar X a Y»
      const before = p.room;
      const activeBefore = p.active;
      const thingsBefore = new Set(visibleThings().map(([id]) => id));
      const [a = '', b] = args.split(/\s+(?:amb|a)\s+/);
      let lines: ResolvedLine[];
      if (b) {
        const item = findItem(a);
        if (!item) { console.log(`${c.red}No tens «${a}».${c.off}`); continue; }
        const thing = findThing(b);
        const otherItem = findItem(b);
        if (!thing && !otherItem) { console.log(`${c.red}No veig «${b}».${c.off}`); continue; }
        lines = p.do(verb, thing ? thing : { kind: 'item', id: otherItem! }, item);
      } else {
        const thing = findThing(a);
        const item = findItem(a);
        if (!thing && !item) { console.log(`${c.red}No veig «${a}».${c.off}`); continue; }
        lines = p.do(verb, thing ? thing : { kind: 'item', id: item! });
      }
      print(lines);
      if (p.pendingDialogue) {
        const d = p.pendingDialogue;
        p.pendingDialogue = null;
        await runDialogue(d);
      }
      if (acabat) {
        const id = n.resolveEnding();
        if (id) {
          const f = n.ending(id);
          console.log(`\n${c.bold}${f.title}${c.off}\n`);
          print(f.scene);
          console.log(`\n${f.text}\n`);
          print(f.credits);
          console.log(`\n${n.t('ui.fi')}`);
        }
        break;
      }
      if (p.room !== before || p.active !== activeBefore) describeRoom();
      else {
        // Al joc, el que apareix es veu; aquí cal dir-ho.
        const nous = visibleThings().filter(([id]) => !thingsBefore.has(id));
        if (nous.length) {
          console.log(`${c.dim}Ara també hi ha: ${nous.map(([id, h]) => `${h.name ? n.t(h.name) : id} [${id}]`).join(', ')}${c.off}`);
        }
      }
    } catch (e) {
      console.log(`${c.red}${(e as Error).message}${c.off}`);
    }
  }
  rl.close();
}

main();
