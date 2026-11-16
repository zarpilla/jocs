/**
 * Mesura com es juga un camí amb la interfície tàctil (sense barra de verbs). Embolcalla el jugador del test i, a
 * cada `do` i `use`, mira què hauria fet el jugador (regla del toc: `queFaElToc`, adapters/benne/tactil/runtime/accions.ts):
 *
 *  - toc: tocar la cosa fa exactament el que fa el camí (o tocar-la amb l'objecte a la mà);
 *  - menú: el toc obre el menú (la cosa té més d'una acció) i s'hi tria;
 *  - premut: el toc faria una altra cosa (p. ex. ja s'ha mirat i ara faria l'acció, o és un objecte de l'inventari
 *    que es pot combinar i el toc el pren a la mà): cal mantenir premut i triar;
 *  - mira primer: abans de l'acció, el primer toc ha mirat la cosa (un toc de més, però amb la descripció);
 *  - dret: amb el ratolí, mirar és un clic dret (un gest).
 *
 * `mode`: `dit` (el mòbil: el primer toc mira) o `ratoli` (l'ordinador: el clic esquerre fa l'acció, el dret mira).
 *
 * Si alguna interacció del camí no es pot fer de cap manera, `impossibles` no és buit. És pur (només el nucli):
 * serveix per a qualsevol joc de narrative-core.
 */
import type { InteractionTarget, Narrative } from '@aventura/narrative-core';
import { accions, haFet, marcaMirat, objecteSol, potAnarALaMa, queFaElToc, verbAmbObjecte } from './runtime/accions.js';

export type Com = 'toc' | 'menú' | 'premut' | 'dret';
export type Mode = 'dit' | 'ratoli';
export interface Pas { com: Com; on: string; miraPrimer: boolean }

export interface Mesura {
  passos: Pas[];
  impossibles: string[];
  /** El jugador embolcallat: el camí s'ha de jugar amb aquest. */
  jugador<T extends object>(p: T): T;
  resum(nom: string): string;
}

export function mesura(n: Narrative, mode: Mode = 'dit'): Mesura {
  const mirarPrimer = mode === 'dit';
  const passos: Pas[] = [];
  const impossibles: string[] = [];
  const kind = (id: string): InteractionTarget['kind'] => (n.content.characters[id] ? 'character' : 'hotspot');
  const target = (t: string | InteractionTarget): InteractionTarget => (typeof t === 'string' ? { kind: kind(t), id: t } : t);

  const mira = (verb: string, t: InteractionTarget, item?: string) => {
    const on = `${n.world.currentRoom()}: ${verb} ${t.id}${item ? ` amb ${item}` : ''}`;
    const volgut = n.peek({ verb, target: t, item });
    if (!volgut) return; // el camí fa una cosa que no fa res (la frase per defecte): no compta
    if (item) {
      if (n.peek({ verb: verbAmbObjecte(n, t, item), target: t, item }) !== volgut) impossibles.push(on);
      // l'objecte s'ha de poder prendre a la mà: tocant-lo, o (si es fa servir sol) des del menú
      if (!potAnarALaMa(n.content, item)) impossibles.push(`${on} (no es pot prendre a la mà)`);
      passos.push({ com: objecteSol(n.content, item) ? 'premut' : 'toc', on, miraPrimer: false });
      return;
    }
    if (mode === 'ratoli' && verb === 'look') {
      marcaMirat(n, t);
      passos.push({ com: 'dret', on, miraPrimer: false });
      return;
    }
    if (t.kind === 'item' && !objecteSol(n.content, t.id)) {
      // tocar-lo el pren a la mà: per fer-ne alguna altra cosa, cal el menú
      const menu = [{ verb: 'look' }, ...accions(n, t)].map((a) => n.peek({ verb: a.verb, target: t }));
      if (!menu.includes(volgut)) impossibles.push(on);
      if (verb === 'look') marcaMirat(n, t);
      passos.push({ com: 'premut', on, miraPrimer: false });
      return;
    }
    let toc = queFaElToc(n, t, undefined, { mirarPrimer });
    let miraPrimer = false;
    if (toc.fa === 'mira' && verb !== 'look') {
      // el primer toc la mira (al joc, de debò; aquí només s'apunta: el camí no la mira)
      marcaMirat(n, t);
      miraPrimer = true;
      toc = queFaElToc(n, t, undefined, { mirarPrimer });
    }
    if (verb === 'look') marcaMirat(n, t);
    const tocFa = toc.fa === 'mira' ? 'look' : toc.fa === 'accio' ? toc.verb : null;
    if (tocFa && n.peek({ verb: tocFa, target: t }) === volgut) {
      passos.push({ com: 'toc', on, miraPrimer });
      return;
    }
    const menu = [{ verb: 'look' }, ...accions(n, t)].map((a) => n.peek({ verb: a.verb, target: t }));
    if (!menu.includes(volgut)) impossibles.push(on);
    passos.push({ com: toc.fa === 'menu' ? 'menú' : 'premut', on, miraPrimer });
  };

  return {
    passos,
    impossibles,
    jugador<T extends object>(p: T): T {
      return new Proxy(p, {
        get(obj, prop, receiver) {
          const value = Reflect.get(obj, prop, receiver) as unknown;
          const fn = value as (...args: unknown[]) => unknown;
          if (prop === 'do') return (verb: string, t: string | InteractionTarget, item?: string) => {
            mira(verb, target(t), item);
            const sala = n.world.currentRoom() ?? undefined;
            const lines = fn.call(obj, verb, t, item);
            haFet(n, target(t), sala); // com al runtime (`acted`): el que en queda ja és vist
            return lines;
          };
          if (prop === 'use') return (item: string, t: string | InteractionTarget) => {
            mira('use', target(t), item);
            const sala = n.world.currentRoom() ?? undefined;
            const lines = fn.call(obj, item, t);
            haFet(n, target(t), sala);
            return lines;
          };
          return typeof value === 'function' ? fn.bind(obj) : value;
        },
      });
    },
    resum(nom: string) {
      const c = (k: Com) => passos.filter((x) => x.com === k).length;
      const mp = passos.filter((x) => x.miraPrimer).length;
      // gestos: un toc, o dos (tocar i triar al menú); mantenir premut i triar, dos; mirar primer, un més
      const gestos = c('toc') + c('dret') + 2 * c('menú') + 2 * c('premut') + mp;
      const llista = passos.filter((x) => x.com !== 'toc' && x.com !== 'dret').map((x) => `  ${x.com}: ${x.on}`);
      return [`${nom} (${mode === 'dit' ? 'dit' : 'ratolí'}): ${passos.length} passos; toc ${c('toc')}, clic dret ${c('dret')}, ` +
        `menú ${c('menú')}, premut ${c('premut')}; ` +
        `mira primer ${mp}; ${gestos} gestos (${(gestos / passos.length).toFixed(2)} per pas)`, ...llista].join('\n');
    },
  };
}
