/**
 * Ajudes per als tests de partida: una partida sense gràfics i el recorregut sencer de l'Acte 1.
 */
import { expect } from 'vitest';
import { HeadlessPlayer, MemoryWorld, Narrative } from '@aventura/narrative-core';
import { content, locales } from '../index.js';
import { installGameLogic, rutaConducte, type Direccio } from '../logic/index.js';

export const keys = (lines: { key: string }[]) => lines.map((l) => l.key);
export const texts = (lines: { text: string }[]) => lines.map((l) => l.text).join(' ');

/**
 * Partida nova. Amb `checkHints`, després de cada acció del jugador hi ha d'haver alguna pista per
 * a l'una o l'altra protagonista, fins que es compleixi `fins` (per defecte, obrir la comporta).
 */
export function partida(opts: { checkHints?: boolean; fins?: string } = {}) {
  const world = new MemoryWorld();
  const n = new Narrative({ content, locales, world });
  installGameLogic(n);
  const player = new HeadlessPlayer(n, world);
  player.newGame();
  const fins = opts.fins ?? 'comporta_oberta';
  const p = !opts.checkHints ? player : new Proxy(player, {
    get(target, prop, receiver) {
      const value = Reflect.get(target, prop, receiver);
      if (typeof value !== 'function' || !['do', 'use', 'talk', 'goTo', 'switchTo'].includes(String(prop))) return value;
      return (...args: unknown[]) => {
        const result = (value as (...a: unknown[]) => unknown).apply(target, args);
        if (!n.flag(fins)) {
          const any = n.activeHints().length > 0 || altraTePista(n, world);
          expect(any, `Sense pistes després de ${String(prop)}(${JSON.stringify(args)})`).toBe(true);
        }
        return result;
      };
    },
  });
  return { n, p, world };
}

function altraTePista(n: Narrative, world: MemoryWorld) {
  const current = world.active;
  world.active = n.content.manifest.protagonists.find((x) => x !== current)!;
  const has = n.activeHints().length > 0;
  world.active = current;
  return has;
}

type Jugador = ReturnType<typeof partida>['p'];
const item = (id: string) => ({ kind: 'item' as const, id });

/** L'Acte 1 sencer, pel camí més curt: acaba amb la Vet al passadís. */
export function jugarActe1(p: Jugador) {
  p.do('pickUp', 'tauler');
  p.goTo('fabrica_magatzem');
  p.talk('cargol', 'clau');
  p.do('pickUp', 'plomall');
  p.goTo('fabrica_calderes');
  p.use('plomall', 'capatas');
  p.do('pickUp', 'segell');
  p.use('segell', item('formulari_27b'));
  p.goTo('fabrica_magatzem');
  p.talk('cargol', 'clau', 'dia');
  p.goTo('fabrica_calderes');
  p.use('clau_cambra', 'porta_cambra');
  p.use('clau_anglesa', 'palanca');
  p.do('push', 'boto');
  p.do('push', 'panell');
  p.use('clau_anglesa', 'panell');
  p.use('clau_anglesa', 'panell');
  p.do('pickUp', 'avis');
  p.talk('mos', 'familia', 'llapis_demanar', 'elogiar');
  p.use('llapis_ulls', item('avis_reciclatge'));
  p.use('nota_vet', 'panell');
  p.do('push', 'panell');
  p.switchTo('iri');
  p.do('push', 'boto');
  p.do('look', item('nota_vet'));
  p.use('llapis', item('llibreta_torn'));
  p.use('nota_iri', 'cambra');
  p.do('look', item('nota_iri'));
  p.do('look', 'porta');
  p.do('look', 'llitera');
  p.do('pickUp', 'fullet');
  p.use('llapis_ulls', item('fullet_reeducacio'));
  p.use('nota_pany', 'panell');
  p.do('look', item('nota_pany'));
  p.goTo('fabrica_calderes');
  p.do('pickUp', 'tauler');
  p.goTo('fabrica_magatzem');
  p.use('segell', item('formulari_27b'));
  p.use('segell', item('formulari_segellat'));
  p.talk('cargol', 'imant');
  p.goTo('fabrica_calderes');
  p.goTo('fabrica_cambra');
  p.use('imant_ferro9', 'cambra');
  p.use('imant_ferro9', 'porta');
}

/**
 * La Vet escriu en un tros nou del cartell i ho envia des de la cel·la (acaba amb l'Iri). Si l'Iri no és a la
 * cambra, la nota queda armada: l'Iri hi va i la rep en entrar-hi.
 */
function escriureIEnviar(p: Jugador, nota: string) {
  p.do('open', 'porta_passadis');
  p.do('pickUp', 'cartell');
  p.use('llapis_ulls', item('tros_cartell'));
  p.do('open', 'porta_cella');
  p.use(nota, 'panell');
  if (p.active === 'vet') {
    p.switchTo('iri');
    p.goTo('fabrica_cambra');
  }
}

/**
 * L'Acte 2 sencer pel camí més curt (la palanca per peces, sense plànols ni Mira): comença amb la Vet
 * al passadís i acaba amb la Vet a la cel·la, just quan comença l'Acte 3.
 */
export function jugarActe2(p: Jugador, opts: { mira?: boolean; cargol?: boolean } = {}) {
  // La comporta
  p.do('open', 'porta_hangar');
  p.do('open', 'porta_passadis');
  p.do('open', 'porta_cella');
  p.do('pickUp', 'panell');
  p.do('open', 'porta');
  p.do('pickUp', 'cartell');
  p.do('open', 'porta_hangar');
  p.use('clau_anglesa', 'comporta');
  p.use('llapis_ulls', item('tros_cartell'));
  p.do('open', 'porta_passadis');
  p.do('open', 'porta_cella');
  p.use('nota_mida', 'panell');
  p.do('look', item('nota_mida'));
  p.goTo('fabrica_calderes');
  p.do('open', 'porta_moll');
  p.do('pickUp', 'llima');
  p.use('llima', 'pilar');
  p.do('pickUp', 'serra');
  p.use('serra', 'biga_acer');
  p.goTo('fabrica_calderes');
  p.goTo('fabrica_cambra');
  for (const n of [1, 2, 3]) {
    p.use(`tram_biga_${n}`, 'cambra');
    if (n < 3) p.switchTo('iri');
  }
  p.use('tram_biga_1', item('tram_biga_2'));
  p.do('open', 'porta');
  p.do('open', 'porta_hangar');
  p.use('biga_muntada', 'comporta');
  // El diapasó
  p.do('look', 'llancadora');
  p.do('push', 'pany');
  p.do('open', 'porta_passadis');
  p.do('open', 'porta_cella');
  p.do('pickUp', 'llitera');
  p.do('pull', item('molla'));
  p.do('pull', item('molla'));
  p.do('open', 'porta');
  p.do('open', 'porta_hangar');
  p.use('molla', 'pany');
  p.do('open', 'porta_passadis');
  p.do('open', 'porta_cella');
  p.use('molla', 'panell');
  p.do('look', item('molla'));
  p.goTo('fabrica_calderes');
  p.do('pickUp', 'tauler');
  p.use('segell', item('formulari_27b'));
  p.use('segell', item('formulari_segellat'));
  p.goTo('fabrica_magatzem');
  p.talk('cargol', 'diapaso');
  p.goTo('fabrica_calderes');
  p.do('open', 'porta_moll');
  p.use('llima', item('diapaso'));
  p.use('llima', item('diapaso'));
  p.use('diapaso', item('molla'));
  p.goTo('fabrica_calderes');
  p.goTo('fabrica_cambra');
  p.use('diapaso', 'cambra');
  p.do('open', 'porta');
  p.do('open', 'porta_hangar');
  p.use('diapaso', 'pany');
  // La vàlvula
  p.do('push', 'llancadora');
  escriureIEnviar(p, 'nota_pressio');
  p.do('look', item('nota_pressio'));
  p.goTo('fabrica_calderes');
  p.do('open', 'porta_moll');
  p.do('close', 'conducte');
  p.switchTo('vet');
  p.do('open', 'porta');
  p.do('open', 'porta_hangar');
  escriureIEnviar(p, 'nota_massa');
  p.do('look', item('nota_massa'));
  p.goTo('fabrica_calderes');
  p.do('open', 'porta_moll');
  p.do('open', 'conducte');
  p.switchTo('vet');
  p.do('open', 'porta');
  p.do('open', 'porta_hangar');
  p.do('push', 'llancadora');
  if (opts.mira || opts.cargol) {
    p.switchTo('iri');
    if (opts.mira) {
      // Els plànols del despatx (amb un altre imant del Cargol), i la Mira salvada falsificant l'inventari.
      p.goTo('fabrica_magatzem');
      p.do('open', 'porta_despatx');
      p.do('open', 'calaix');
      p.goTo('fabrica_calderes');
      p.do('pickUp', 'tauler');
      p.use('segell', item('formulari_27b'));
      p.use('segell', item('formulari_segellat'));
      p.goTo('fabrica_magatzem');
      p.talk('cargol', 'imant2');
      p.do('open', 'porta_despatx');
      p.use('imant_ferro9', 'calaix');
      p.do('look', 'expedient_sic');
      p.use('segell', 'llibre_inventari');
    }
    if (opts.cargol) {
      // La memòria del Cargol: el segell a la revisió i el nom gravat amb la llima.
      p.goTo('fabrica_magatzem');
      p.talk('cargol', 'memoria');
      p.use('segell', 'cargol');
      p.use('llima', 'cargol');
    }
    p.switchTo('vet');
  }
  // L'arxiu i els noms
  p.use('clau_anglesa', 'escala');
  p.do('open', 'escala');
  p.do('look', 'expedient_iri');
  p.do('open', 'escala_hangar');
  escriureIEnviar(p, 'nota_vet_nom');
  p.do('look', item('nota_vet_nom'));
  p.use('llapis', item('llibreta_torn'));
  p.goTo('fabrica_calderes');
  p.goTo('fabrica_cambra');
  p.use('nota_iri_nom', 'cambra');
  p.do('look', item('nota_iri_nom'));
}

/**
 * L'Acte 3 sencer, des de la Vet a la cel·la fins a la fugida de totes dues. `vet` es fa amb la Vet a
 * l'hangar, quan ja pot anar al passadís pel conducte; `iri`, amb l'Iri al magatzem, abans de fugir.
 * `inici`, amb la Vet a la cel·la just en començar l'acte; `mos`: en Mos distreu la Directora en lloc del pacte.
 */
/**
 * L'Iri entra al conducte per la reixa de la cambra i, a cada revolt, va per on diu `ruta` (per defecte, la del
 * fullet de la Vet). Torna les línies de l'últim revolt (on surt).
 */
export function recorrerConducte(p: Jugador, ruta: Direccio[] = rutaConducte(p.narrative)) {
  p.do('open', 'reixa');
  let lines: { key: string; text: string }[] = [];
  for (const dir of ruta) lines = p.do('walkTo', dir);
  return lines;
}

export function jugarActe3(p: Jugador, extra: { inici?: () => void; vet?: () => void; iri?: () => void; mos?: boolean } = {}) {
  extra.inici?.();
  p.do('push', 'panell');
  p.talk('directora', 'que_vol', 'iri');
  p.switchTo('iri');
  p.talk('sic', 'que_passa');
  p.switchTo('vet');
  p.do('open', 'porta');
  p.do('open', 'porta_memoria');
  p.do('look', 'foto');
  p.do('look', 'mapa');
  p.do('pickUp', 'fullets');
  p.do('open', 'porta_passadis');
  p.do('open', 'porta_cella');
  p.use('llapis_ulls', item('fullet_memoria'));
  p.do('look', 'reixa');
  p.do('open', 'reixa');
  p.use('llapis_ulls', item('fullet_memoria'));
  p.use('mapa_fuga', 'panell');
  if (extra.mos) p.talk('mos', 'distreure');
  else p.talk('directora', 'pacte');
  p.switchTo('iri');
  p.talk('sic', 'enganyar');
  p.do('open', 'porta_cambra');
  p.switchTo('vet');
  p.use('mapa_fuga', 'panell');
  p.do('look', item('mapa_fuga'));
  p.use('llima', 'reixa');
  recorrerConducte(p);
  p.switchTo('vet');
  p.do('open', 'reixa');
  p.do('open', 'reixa');
  extra.vet?.();
  p.do('open', 'sortida_conducte');
  p.switchTo('iri');
  p.goTo('fabrica_magatzem');
  p.talk('cargol', 'tub');
  extra.iri?.();
  p.goTo('fabrica_cambra');
  p.use('llibreta_torn', item('tub_ferro9'));
  p.use('tub_amb_llibreta', 'cambra');
  p.do('open', 'reixa');
  p.use('tub_amb_llibreta', 'llancadora');
  p.do('push', 'llancadora');
  p.do('open', 'reixa');
  p.do('use', 'llancadora');
}
