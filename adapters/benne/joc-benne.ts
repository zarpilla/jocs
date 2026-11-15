/**
 * El que cada joc fa diferent a l'hora de portar-lo a Benne. Cada joc en té un a
 * `games/<joc>/adapters/benne/joc.ts` (`export default { ... } satisfies JocBenne`).
 *
 * La resta de l'adaptador (sync.ts, benne-content.ts, create-project.ts, runtime/) és compartida.
 */
import { existsSync } from 'node:fs';
import { join } from 'node:path';
import { pathToFileURL } from 'node:url';
import { jocDir } from '../../tools/joc.js';

type Json = Record<string, unknown>;
export type Translate = (key: string | undefined, def?: string) => string;

export interface JocBenne {
  /** Nom del joc (títol de la finestra, README, missatges de la consola). */
  nom: string;
  /** Carpeta del projecte Benne dins games/<joc>/ (p. ex. `suma-zero`). */
  projecte: string;
  /** Nom del paquet npm del projecte Benne (en surt la clau de les partides desades). */
  paquet: string;
  /** Les dues fonts del joc (ids de `assets/fonts/fonts.json`) i l'script que les genera. */
  fonts: { regular: string; negreta: string; script: string };
  /** Colors de parla dels personatges que no fan servir la paleta automàtica. */
  colorsVeu?: Record<string, string>;
  /**
   * Si una protagonista pot ser una veu a la sala de l'altra (la Vet des de la cuina, l'Iri per
   * telèfon): llavors s'hi afegeix com a personatge, com qualsevol altra veu.
   */
  veusProtagonistes?: boolean;
  /** Si totes les pistes de música duren el mateix i, en canviar de sala, la nova continua al mateix punt. */
  musicaSincronitzada?: boolean;
  /** Textos de més per a les GUI (GUI → control → clau de text), a més dels comuns. */
  textosGui?: Record<string, Record<string, string>>;
  /**
   * La interfície tàctil, sense barra de verbs (adapters/benne/tactil): tocar mira o fa l'acció, mantenir premut obre
   * el menú d'accions, i l'alçada de la pantalla s'adapta a l'aparell. El joc hi posa l'art (tools/hd640/hud.py).
   */
  tactil?: boolean;
  /** Retocs propis a game-config.json, cada vegada que se sincronitza. */
  configura?(config: Json, t: Translate): void;
  /** GUI pròpies del joc (menú, historial...), cada vegada que se sincronitza. */
  guis?(gameDir: string): void;
}

/** La configuració del joc actual (vegeu tools/joc.ts per saber quin és). */
export async function loadJocBenne(): Promise<JocBenne> {
  const path = join(jocDir(), 'adapters/benne/joc.ts');
  if (!existsSync(path)) throw new Error(`Falta ${path}: la configuració del joc per a l'adaptador de Benne.`);
  return ((await import(pathToFileURL(path).href)) as { default: JocBenne }).default;
}

/** La carpeta de l'adaptador del joc: games/<joc>/adapters/benne/ (mapping.json, art provisional, eines d'art). */
export const jocAdapterDir = () => join(jocDir(), 'adapters/benne');
