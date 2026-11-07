import type { Condition, Effect, GameContent, LocaleTable, TextKey } from './types.js';

export interface ValidationIssue {
  level: 'error' | 'warning';
  where: string;
  message: string;
}

const ID_RE = /^[a-z][a-z0-9_]*$/;

/**
 * Comprova el contingut sencer: referències trencades (flags, personatges,
 * nodes, missions...), identificadors mal formats i textos sense traduir.
 * L'idioma per defecte ha de ser complet (error); als altres, avís.
 */
export function validateContent(content: GameContent, locales: Record<string, LocaleTable>): ValidationIssue[] {
  const issues: ValidationIssue[] = [];
  const err = (where: string, message: string): void => {
    issues.push({ level: 'error', where, message });
  };
  const usedKeys = new Map<TextKey, string>();
  const text = (where: string, key: TextKey | undefined) => {
    if (key !== undefined) usedKeys.set(key, where);
  };
  const id = (where: string, value: string) => {
    if (!ID_RE.test(value)) err(where, `Identificador "${value}" no vàlid: minúscules, xifres i "_", començant per lletra.`);
  };

  const { characters, items, objects, dialogues, quests, hints, endings, state, manifest } = content;
  const speakers = new Set(['player', 'narrator', ...Object.keys(characters)]);

  // Condicions i efectes ────────────────────────────────────────────────────
  const checkFact = (where: string, who: string, fact: string) => {
    if (!characters[who]) return err(where, `Personatge desconegut "${who}".`);
    const facts = characters[who].facts;
    if (facts && !facts.includes(fact)) err(where, `"${who}" no declara el fet "${fact}" a characters.json.`);
  };
  const checkQuestObjective = (where: string, quest: string, objective: string) => {
    if (!quests[quest]) return err(where, `Missió desconeguda "${quest}".`);
    if (!quests[quest].objectives.some((o) => o.id === objective)) err(where, `Objectiu "${objective}" no existeix a "${quest}".`);
  };
  const checkNode = (where: string, dialogue: string, node: string) => {
    if (!dialogues[dialogue]) return err(where, `Diàleg desconegut "${dialogue}".`);
    if (!dialogues[dialogue].nodes[node]) err(where, `Node "${node}" no existeix a "${dialogue}".`);
  };

  const cond = (where: string, c: Condition | undefined): void => {
    if (!c) return;
    if ('all' in c) return c.all.forEach((x, i) => cond(`${where}.all[${i}]`, x));
    if ('any' in c) return c.any.forEach((x, i) => cond(`${where}.any[${i}]`, x));
    if ('not' in c) return cond(`${where}.not`, c.not);
    if ('flag' in c) { if (!(c.flag in state.flags)) err(where, `Flag no declarat "${c.flag}" (state.json).`); return; }
    if ('var' in c) { if (!(c.var in state.vars)) err(where, `Variable no declarada "${c.var}" (state.json).`); return; }
    if ('hasItem' in c) { if (!items[c.hasItem]) err(where, `Objecte d'inventari desconegut "${c.hasItem}".`); return; }
    if ('remembers' in c) return checkFact(where, c.remembers.who, c.remembers.fact);
    if ('relation' in c) { if (!characters[c.relation.who]) err(where, `Personatge desconegut "${c.relation.who}".`); return; }
    if ('quest' in c) { if (!quests[c.quest]) err(where, `Missió desconeguda "${c.quest}".`); return; }
    if ('objective' in c) return checkQuestObjective(where, c.objective.quest, c.objective.objective);
    if ('seen' in c) return checkNode(where, c.seen.dialogue, c.seen.node);
    if ('chosen' in c) {
      const { dialogue, node, choice } = c.chosen;
      checkNode(where, dialogue, node);
      if (!dialogues[dialogue]?.nodes[node]?.choices?.some((x) => x.id === choice)) err(where, `Opció "${choice}" no existeix a "${dialogue}/${node}".`);
      return;
    }
    if ('visited' in c || 'inRoom' in c) return; // les sales són del motor gràfic
    err(where, `Condició desconeguda: ${JSON.stringify(c)}`);
  };

  const effects = (where: string, list: Effect[] | undefined) => {
    (list ?? []).forEach((e, i) => {
      const w = `${where}[${i}]`;
      if ('setFlag' in e) { if (!(e.setFlag in state.flags)) err(w, `Flag no declarat "${e.setFlag}".`); }
      else if ('setVar' in e) { if (!(e.setVar in state.vars)) err(w, `Variable no declarada "${e.setVar}".`); }
      else if ('addVar' in e) { if (typeof state.vars[e.addVar] !== 'number') err(w, `"${e.addVar}" ha de ser una variable numèrica declarada.`); }
      else if ('giveItem' in e) { if (!items[e.giveItem]) err(w, `Objecte desconegut "${e.giveItem}".`); }
      else if ('takeItem' in e) { if (!items[e.takeItem]) err(w, `Objecte desconegut "${e.takeItem}".`); }
      else if ('remember' in e) checkFact(w, e.remember.who, e.remember.fact);
      else if ('forget' in e) checkFact(w, e.forget.who, e.forget.fact);
      else if ('relation' in e) { if (!characters[e.relation.who]) err(w, `Personatge desconegut "${e.relation.who}".`); }
      else if ('startQuest' in e) { if (!quests[e.startQuest]) err(w, `Missió desconeguda "${e.startQuest}".`); }
      else if ('completeQuest' in e) { if (!quests[e.completeQuest]) err(w, `Missió desconeguda "${e.completeQuest}".`); }
      else if ('failQuest' in e) { if (!quests[e.failQuest]) err(w, `Missió desconeguda "${e.failQuest}".`); }
      else if ('completeObjective' in e) checkQuestObjective(w, e.completeObjective.quest, e.completeObjective.objective);
      else if ('ending' in e) { if (!endings[e.ending]) err(w, `Final desconegut "${e.ending}".`); }
      else if (!('event' in e)) err(w, `Efecte desconegut: ${JSON.stringify(e)}`);
    });
  };

  // Entitats ────────────────────────────────────────────────────────────────
  text('game.json', manifest.title);
  if (!characters[manifest.player]) err('game.json', `El jugador "${manifest.player}" no és a characters.json.`);
  if (!manifest.locales.includes(manifest.defaultLocale)) err('game.json', `defaultLocale no és a locales.`);
  for (const k of [...Object.keys(state.flags), ...Object.keys(state.vars)]) id('state.json', k);

  for (const [cid, c] of Object.entries(characters)) {
    id(`characters.${cid}`, cid);
    text(`characters.${cid}.name`, c.name);
    text(`characters.${cid}.description`, c.description);
  }
  for (const [iid, it] of Object.entries(items)) {
    id(`items.${iid}`, iid);
    text(`items.${iid}.name`, it.name);
    text(`items.${iid}.description`, it.description);
  }
  for (const [oid, o] of Object.entries(objects)) {
    id(`objects.${oid}`, oid);
    text(`objects.${oid}.name`, o.name);
    cond(`objects.${oid}.visibleIf`, o.visibleIf);
  }

  for (const [did, d] of Object.entries(dialogues)) {
    const w = `dialogues.${did}`;
    id(w, did);
    if (d.id !== did) err(w, `L'"id" del fitxer ("${d.id}") no coincideix amb "${did}".`);
    if (!characters[d.with]) err(w, `Personatge desconegut "${d.with}".`);
    const starts = typeof d.start === 'string' ? [{ node: d.start }] : d.start;
    starts.forEach((s, i) => {
      if (!d.nodes[s.node]) err(`${w}.start[${i}]`, `Node "${s.node}" no existeix.`);
      cond(`${w}.start[${i}].if`, 'if' in s ? s.if : undefined);
    });
    if (Array.isArray(d.start) && d.start.at(-1)?.if) {
      issues.push({ level: 'warning', where: `${w}.start`, message: `L'última entrada té condició: si cap no es compleix, el diàleg no pot començar.` });
    }
    for (const [nid, n] of Object.entries(d.nodes)) {
      const nw = `${w}.nodes.${nid}`;
      id(nw, nid);
      effects(`${nw}.effects`, n.effects);
      if (n.goto && !d.nodes[n.goto]) err(`${nw}.goto`, `Node "${n.goto}" no existeix.`);
      n.lines?.forEach((l, i) => {
        if (!speakers.has(l.who)) err(`${nw}.lines[${i}]`, `Qui parla? "${l.who}" no és cap personatge.`);
        text(`${nw}.lines[${i}]`, l.text);
        cond(`${nw}.lines[${i}].if`, l.if);
        effects(`${nw}.lines[${i}].effects`, l.effects);
      });
      const seen = new Set<string>();
      n.choices?.forEach((c, i) => {
        const cw = `${nw}.choices[${i}]`;
        id(cw, c.id);
        if (seen.has(c.id)) err(cw, `Opció "${c.id}" repetida al node.`);
        seen.add(c.id);
        text(cw, c.text);
        cond(`${cw}.if`, c.if);
        effects(`${cw}.effects`, c.effects);
        if (c.next && !d.nodes[c.next]) err(`${cw}.next`, `Node "${c.next}" no existeix.`);
      });
    }
  }

  for (const [qid, q] of Object.entries(quests)) {
    const w = `quests.${qid}`;
    id(w, qid);
    text(`${w}.title`, q.title);
    text(`${w}.description`, q.description);
    cond(`${w}.startWhen`, q.startWhen);
    cond(`${w}.completeWhen`, q.completeWhen);
    cond(`${w}.failWhen`, q.failWhen);
    effects(`${w}.onComplete`, q.onComplete);
    effects(`${w}.onFail`, q.onFail);
    q.objectives.forEach((o, i) => {
      id(`${w}.objectives[${i}]`, o.id);
      text(`${w}.objectives[${i}]`, o.text);
      cond(`${w}.objectives[${i}].completeWhen`, o.completeWhen);
    });
  }

  for (const [hid, h] of Object.entries(hints)) {
    const w = `hints.${hid}`;
    id(w, hid);
    cond(`${w}.when`, h.when);
    cond(`${w}.doneWhen`, h.doneWhen);
    if (h.levels.length === 0) err(w, `Una pista necessita almenys un nivell.`);
    h.levels.forEach((k, i) => text(`${w}.levels[${i}]`, k));
  }

  for (const [eid, e] of Object.entries(endings)) {
    id(`endings.${eid}`, eid);
    text(`endings.${eid}.title`, e.title);
    text(`endings.${eid}.text`, e.text);
    cond(`endings.${eid}.when`, e.when);
  }

  // Traduccions ─────────────────────────────────────────────────────────────
  for (const locale of manifest.locales) {
    const table = locales[locale];
    const level = locale === manifest.defaultLocale ? 'error' : 'warning';
    if (!table) {
      issues.push({ level, where: `locales/${locale}`, message: `No hi ha textos per a aquest idioma.` });
      continue;
    }
    for (const [key, where] of usedKeys) {
      if (table[key] === undefined) issues.push({ level, where, message: `Falta el text "${key}" a "${locale}".` });
    }
    for (const key of Object.keys(table)) {
      if (!usedKeys.has(key) && !key.startsWith('ui.')) {
        issues.push({ level: 'warning', where: `locales/${locale}`, message: `Text "${key}" no es fa servir enlloc.` });
      }
    }
  }

  return issues;
}
