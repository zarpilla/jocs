import type { Condition, Effect, GameContent, InteractionDef, LocaleTable, TextKey } from './types.js';

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
export interface ValidateOptions {
  /** Accions de joc registrades (si es dona, es comprova que les interaccions les fan servir bé). */
  actions?: string[];
  /** Claus de text que fa servir el codi del joc: han d'existir i no compten com a sobreres. */
  textKeys?: string[];
  /** Sons que hi ha (`game/audio/sfx/`, sense extensió). Si es dona, es comprova que les línies en fan servir de bons. */
  sounds?: string[];
}

export function validateContent(
  content: GameContent,
  locales: Record<string, LocaleTable>,
  options: ValidateOptions = {},
): ValidationIssue[] {
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

  const { characters, items, rooms, dialogues, quests, hints, endings, state, manifest } = content;
  const speakers = new Set(['player', 'narrator', 'title', ...Object.keys(characters)]);

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
    if ('hasItem' in c) {
      if (!items[c.hasItem]) err(where, `Objecte d'inventari desconegut "${c.hasItem}".`);
      if (c.who && !characters[c.who]) err(where, `Personatge desconegut "${c.who}".`);
      return;
    }
    if ('protagonist' in c) { if (!manifest.protagonists.includes(c.protagonist)) err(where, `"${c.protagonist}" no és cap protagonista (game.json).`); return; }
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
    if ('visited' in c) { if (!rooms[c.visited]) err(where, `Sala desconeguda "${c.visited}".`); return; }
    if ('inRoom' in c) { if (!rooms[c.inRoom]) err(where, `Sala desconeguda "${c.inRoom}".`); return; }
    err(where, `Condició desconeguda: ${JSON.stringify(c)}`);
  };

  const effects = (where: string, list: Effect[] | undefined) => {
    (list ?? []).forEach((e, i) => {
      const w = `${where}[${i}]`;
      if ('setFlag' in e) { if (!(e.setFlag in state.flags)) err(w, `Flag no declarat "${e.setFlag}".`); }
      else if ('setVar' in e) { if (!(e.setVar in state.vars)) err(w, `Variable no declarada "${e.setVar}".`); }
      else if ('addVar' in e) { if (typeof state.vars[e.addVar] !== 'number') err(w, `"${e.addVar}" ha de ser una variable numèrica declarada.`); }
      else if ('giveItem' in e || 'takeItem' in e) {
        const item = 'giveItem' in e ? e.giveItem : e.takeItem;
        if (!items[item]) err(w, `Objecte desconegut "${item}".`);
        if (e.who && !characters[e.who]) err(w, `Personatge desconegut "${e.who}".`);
      }
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

  const sound = (where: string, name: string | undefined) => {
    if (name === undefined) return;
    const vars = [...name.matchAll(/\{(\w+)\}/g)].map((m) => m[1]!);
    for (const v of vars) if (!(v in state.vars)) err(where, `So "${name}": variable no declarada "${v}" (state.json).`);
    if (!options.sounds) return;
    // Amb variables, n'hi ha prou que n'hi hagi algun que encaixi (els valors depenen de la partida).
    const pattern = new RegExp(`^${name.split(/\{\w+\}/).map((s) => s.replace(/[.*+?^$()|[\]\\]/g, '\\$&')).join('[^/]+')}$`);
    if (!options.sounds.some((s) => pattern.test(s))) err(where, `So desconegut "${name}": no hi és a game/audio/sfx/.`);
  };

  const interactions = (where: string, list: InteractionDef[] | undefined) => {
    (list ?? []).forEach((i, n) => {
      const w = `${where}[${n}]`;
      if (i.id) id(w, i.id);
      if (i.once && !i.id) {
        issues.push({ level: 'warning', where: w, message: `Interacció "once" sense "id": si canvia l'ordre de la llista, les partides desades ho notaran.` });
      }
      if (i.item && i.item !== '*' && !items[i.item]) err(w, `Objecte desconegut "${i.item}".`);
      if (i.dialogue && !dialogues[i.dialogue]) err(w, `Diàleg desconegut "${i.dialogue}".`);
      if (i.goTo && !rooms[i.goTo]) err(w, `Sala desconeguda "${i.goTo}".`);
      if (i.action && options.actions && !options.actions.includes(i.action.name)) {
        err(w, `Acció de joc desconeguda "${i.action.name}". Les que hi ha: ${options.actions.join(', ')}.`);
      }
      cond(`${w}.if`, i.if);
      effects(`${w}.effects`, i.effects);
      i.lines?.forEach((l, k) => {
        if (!speakers.has(l.who)) err(`${w}.lines[${k}]`, `Qui parla? "${l.who}" no és cap personatge.`);
        text(`${w}.lines[${k}]`, l.text);
        cond(`${w}.lines[${k}].if`, l.if);
        effects(`${w}.lines[${k}].effects`, l.effects);
        sound(`${w}.lines[${k}].sound`, l.sound);
      });
    });
  };

  // Entitats ────────────────────────────────────────────────────────────────
  for (const key of options.textKeys ?? []) text('codi del joc', key);
  text('game.json', manifest.title);
  if (manifest.protagonists.length === 0) err('game.json', `Cal almenys una protagonista.`);
  for (const p of manifest.protagonists) {
    if (!characters[p]) err('game.json', `La protagonista "${p}" no és a characters.json.`);
  }
  for (const [who, start] of Object.entries(manifest.start ?? {})) {
    if (!manifest.protagonists.includes(who)) err('game.json.start', `"${who}" no és cap protagonista.`);
    if (!rooms[start.room]) err('game.json.start', `Sala desconeguda "${start.room}".`);
    for (const item of start.items ?? []) if (!items[item]) err('game.json.start', `Objecte desconegut "${item}".`);
  }
  cond('game.json.switchWhen', manifest.switchWhen);
  if (manifest.cover && !rooms[manifest.cover]) err('game.json.cover', `Sala desconeguda "${manifest.cover}".`);
  if (manifest.intro && !rooms[manifest.intro]) err('game.json.intro', `Sala desconeguda "${manifest.intro}".`);
  for (const [rid, room] of Object.entries(rooms)) {
    const skip = room.cutscene?.skipTo;
    if (skip && !rooms[skip]) err(`rooms.${rid}.cutscene`, `Sala desconeguda "${skip}".`);
  }
  if (!manifest.locales.includes(manifest.defaultLocale)) err('game.json', `defaultLocale no és a locales.`);
  for (const k of [...Object.keys(state.flags), ...Object.keys(state.vars)]) id('state.json', k);

  for (const [cid, c] of Object.entries(characters)) {
    id(`characters.${cid}`, cid);
    text(`characters.${cid}.name`, c.name);
    text(`characters.${cid}.description`, c.description);
    interactions(`characters.${cid}.interactions`, c.interactions);
    c.appearance?.forEach((a, i) => cond(`characters.${cid}.appearance[${i}].if`, a.if));
  }
  for (const [iid, it] of Object.entries(items)) {
    id(`items.${iid}`, iid);
    text(`items.${iid}.name`, it.name);
    text(`items.${iid}.description`, it.description);
    interactions(`items.${iid}.interactions`, it.interactions);
  }
  for (const [rid, r] of Object.entries(rooms)) {
    const w = `rooms.${rid}`;
    id(w, rid);
    text(`${w}.name`, r.name);
    if (r.protagonist && !manifest.protagonists.includes(r.protagonist)) err(w, `"${r.protagonist}" no és cap protagonista.`);
    interactions(`${w}.onEnter`, r.onEnter);
    for (const [hid, h] of Object.entries(r.hotspots)) {
      id(`${w}.hotspots.${hid}`, hid);
      text(`${w}.hotspots.${hid}.name`, h.name);
      cond(`${w}.hotspots.${hid}.visibleIf`, h.visibleIf);
      interactions(`${w}.hotspots.${hid}.interactions`, h.interactions);
    }
    for (const [did, d] of Object.entries(r.decor ?? {})) {
      id(`${w}.decor.${did}`, did);
      if (did in r.hotspots) err(`${w}.decor.${did}`, `Ja hi ha una cosa "${did}" a la sala: el decorat necessita un altre id.`);
      cond(`${w}.decor.${did}.visibleIf`, d.visibleIf);
    }
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
        sound(`${nw}.lines[${i}].sound`, l.sound);
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
    e.scene?.forEach((l, k) => {
      if (!speakers.has(l.who)) err(`endings.${eid}.scene[${k}]`, `Qui parla? "${l.who}" no és cap personatge.`);
      text(`endings.${eid}.scene[${k}]`, l.text);
      cond(`endings.${eid}.scene[${k}].if`, l.if);
    });
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
