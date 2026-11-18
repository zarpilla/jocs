/**
 * Idle micro-actions: a character standing still now and then blinks, looks around or does its own tic, then goes
 * back to its `Idle` loop (the breathing).
 *
 * A character's `idleActions` (see {@link CharacterIdleActionData}) names base animations such as `Blink` or `Look`.
 * The tag played is the current idle tag with `Idle` replaced by that name, so it keeps the outfit / size prefix,
 * the facing and the mirror: `LlunyGalaIdleDL` → `LlunyGalaBlinkDL`. When that tag does not exist the action is
 * skipped (no falling back to another outfit's art). Anything else the character plays (a walk, a line, a script
 * animation) cuts the action, and the stillness count starts again.
 *
 * Several characters in a room never do the same thing at the same moment: each comes to rest at a random point of
 * its `Idle` loop (frame and time within it) and breathes at its own pace (±12%, only while idle), and an action
 * waits while another character's has just started.
 */
import type * as Phaser from 'phaser';

import type { CharacterData, CharacterIdleActionData } from '../types/character';
import { BENNE_CHARACTER_ANIMATION_OVERRIDE_KEY } from './benneAnimationRuntime';

/** Sprite data key: the idle action tag this layer is playing on the sprite. */
export const IDLE_ACTION_DATA_KEY = 'benneIdleAction';

const DEFAULT_EVERY: [number, number] = [5, 12];
/** Gap between two actions of the same character that come due together. */
const ACTION_GAP_MS = 600;
/** No two characters start an action closer than this. */
const ROOM_GAP_MS = 1500;
/** Personal breathing pace: idle `timeScale` in `1 ± PACE_SPREAD`. */
const PACE_SPREAD = 0.12;

/** The subset of a Phaser sprite this layer touches (kept small so it can be tested without Phaser). */
export interface IdleActionSprite {
  active: boolean;
  visible: boolean;
  anims: {
    currentAnim: { key: string; frames: unknown[] } | null;
    isPlaying: boolean;
    timeScale: number;
    accumulator: number;
    nextTick: number;
    exists(key: string): boolean;
    setProgress(value: number): unknown;
  };
  play(key: string): unknown;
  getData(key: string): unknown;
  setData(key: string, value: unknown): unknown;
}

interface SpriteState {
  /** `now` when the character came to rest; `null` while it moves, talks or plays anything else. */
  stillSince: number | null;
  /** The idle tag to go back to after an action. */
  idleKey: string | null;
  /** Per action: `now` when it is next due. */
  next: number[];
  /** This character's breathing pace (idle `timeScale`). */
  pace: number;
}

/** `Idle` replaced by `action` in an idle tag (the last occurrence, so prefixes stay): `GalaIdleDL` → `GalaBlinkDL`. */
export function idleActionTag(idleKey: string, action: string): string | null {
  const i = idleKey.lastIndexOf('Idle');
  return i < 0 ? null : idleKey.slice(0, i) + action + idleKey.slice(i + 4);
}

function rangeMs(a: CharacterIdleActionData, rand: () => number): number {
  const [lo, hi] = Array.isArray(a.every) && a.every.length === 2 ? a.every : DEFAULT_EVERY;
  const min = Math.max(0.1, Math.min(lo, hi));
  const max = Math.max(min, Math.max(lo, hi));
  return (min + (max - min) * rand()) * 1000;
}

export class CharacterIdleActions {
  private readonly states = new WeakMap<IdleActionSprite, SpriteState>();
  private readonly rand: () => number;
  /** When the last action in the room started, and on whom. */
  private lastActionAt = -Infinity;
  private lastActionSprite: IdleActionSprite | null = null;

  constructor(rand: () => number = Math.random) {
    this.rand = rand;
  }

  /** Once per frame, with the room's character sprites and the scene clock (ms). */
  update(sprites: Iterable<IdleActionSprite>, now: number): void {
    for (const sprite of sprites) {
      this.updateOne(sprite, now);
    }
  }

  private updateOne(sprite: IdleActionSprite, now: number): void {
    if (!sprite.active || !sprite.anims) {
      return;
    }
    let st = this.states.get(sprite);
    if (!st) {
      st = { stillSince: null, idleKey: null, next: [], pace: 1 + (this.rand() * 2 - 1) * PACE_SPREAD };
      this.states.set(sprite, st);
    }
    const key = sprite.anims.currentAnim?.key ?? null;
    const action = sprite.getData(IDLE_ACTION_DATA_KEY) as string | null | undefined;

    if (action) {
      if (key === action && sprite.anims.isPlaying) {
        return; // still playing
      }
      sprite.setData(IDLE_ACTION_DATA_KEY, null);
      if (key === action) {
        // Finished: back to breathing, still counting as rest.
        if (st.idleKey && sprite.anims.exists(st.idleKey)) {
          sprite.play(st.idleKey);
        }
        return;
      }
      // Something else took over (a walk, a line, a script animation).
    }

    const isIdle =
      key !== null &&
      sprite.visible &&
      sprite.getData('facingBase') === 'Idle' &&
      key.includes('Idle') &&
      !sprite.getData(BENNE_CHARACTER_ANIMATION_OVERRIDE_KEY);
    if (!isIdle) {
      if (st.stillSince !== null) {
        sprite.anims.timeScale = 1; // the pace is only for breathing
      }
      st.stillSince = null;
      return;
    }
    sprite.anims.timeScale = st.pace;

    const actions = (sprite.getData('character') as CharacterData | undefined)?.idleActions ?? [];
    if (st.stillSince === null) {
      st.stillSince = now;
      // Desync the breathing: a random frame, and a random time already spent in it.
      if ((sprite.anims.currentAnim?.frames.length ?? 0) > 1) {
        sprite.anims.setProgress(this.rand());
        sprite.anims.accumulator = this.rand() * sprite.anims.nextTick;
      }
      st.next = actions.map((a) => now + (a.after ?? 0) * 1000 + rangeMs(a, this.rand));
    }
    st.idleKey = key;

    for (let i = 0; i < actions.length; i++) {
      const due = st.next[i] ?? Infinity;
      if (now < due) {
        continue;
      }
      const a = actions[i]!;
      const tag = idleActionTag(key, a.animation);
      if (!tag || !sprite.anims.exists(tag)) {
        st.next[i] = now + rangeMs(a, this.rand);
        continue;
      }
      if (this.lastActionSprite !== sprite && now - this.lastActionAt < ROOM_GAP_MS) {
        // Someone else just did something: wait a moment, not all together.
        st.next[i] = this.lastActionAt + ROOM_GAP_MS + this.rand() * 2000;
        continue;
      }
      st.next[i] = now + rangeMs(a, this.rand);
      sprite.play(tag);
      sprite.setData(IDLE_ACTION_DATA_KEY, tag);
      this.lastActionAt = now;
      this.lastActionSprite = sprite;
      // Anything else due about now waits a little, so two actions don't run back to back.
      for (let j = 0; j < actions.length; j++) {
        if (j !== i && (st.next[j] ?? Infinity) < now + ACTION_GAP_MS) {
          st.next[j] = now + ACTION_GAP_MS + rangeMs(actions[j]!, this.rand) * 0.25;
        }
      }
      return;
    }
  }
}

/** Narrowing helper for the room stack (static characters are Images without animations). */
export function isIdleActionSprite(o: Phaser.GameObjects.GameObject): o is Phaser.GameObjects.Sprite {
  return 'anims' in o && (o as Phaser.GameObjects.Sprite).anims !== undefined;
}
