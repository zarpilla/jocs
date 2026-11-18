import type { Point2 } from './room';

/**
 * Frame-synced marker from character JSON (footsteps, SFX hooks, dialogue beats, etc.).
 */
export interface CharacterAnimationFrameEvent {
  /** 0-based index within the Aseprite tag / Phaser animation sequence. */
  frame: number;
  type: string;
  data?: unknown;
}

/**
 * Per-tag animation policy (keys match Aseprite frame tag names, e.g. `WalkL`, `IdleD`).
 */
export interface CharacterAnimationClipConfig {
  /** When true, repeat forever (`repeat: -1` in Phaser). When false or omitted, play once. */
  loop?: boolean;
  /**
   * Milliseconds each frame is shown (uniform for this tag). Applied to every frame in the clip.
   * When omitted, keeps per-frame durations from the Aseprite export.
   */
  frameDuration?: number;
  events?: CharacterAnimationFrameEvent[];
  // Future: pingPong?: boolean; reverse?: boolean;
}

export type CharacterAnimationsConfig = Record<string, CharacterAnimationClipConfig>;

/** Facing suffix on directional clips (`IdleL`, `WalkDR`, …). */
export type CharacterFacingLetter = 'L' | 'R' | 'U' | 'D' | 'UL' | 'UR' | 'DL' | 'DR';

/**
 * Character template loaded from `src/game/characters/` as `*.character.json` files.
 */
export interface CharacterDisplayData {
  /**
   * Static portrait / NPC image under `src/game/assets/`.
   * Required when `aseprite` is not true.
   */
  defaultImage?: string;
  /**
   * When true, loads `images/characters/<characterId>/<characterId>.png` and `.json` (Aseprite sheet export).
   */
  aseprite?: boolean;
}

/**
 * One idle micro-action (see `CharacterData.idleActions`): a short one-shot animation the character plays now and
 * then while standing still, before going back to its `Idle` loop.
 */
export interface CharacterIdleActionData {
  /**
   * Base name, e.g. `Blink`, `Look`, `Tap`. The tag played is the current idle tag with `Idle` replaced by this
   * (`IdleDL` → `BlinkDL`, `LlunyGalaIdleD` → `LlunyGalaBlinkD`); when the sheet lacks it, the action is skipped.
   * Make the tag non-looping (the default when `animations` doesn't say `loop: true`).
   */
  animation: string;
  /** Seconds between two plays, picked at random in `[min, max]`. Omitted = `[5, 12]`. */
  every?: [number, number];
  /** Extra seconds of stillness before the first play, on top of `every` (a tic only after a long wait). Omitted = `0`. */
  after?: number;
}

export interface CharacterData {
  id: string;
  /** BenneScript handle name, when the generated one doesn't fit (docs/bennescript-ergonomics-refactor.md §7.2). */
  scriptName?: string;
  name: string;
  description: string;
  /**
   * Ground contact in **texture / frame pixel space**: from the top-left of each cel to the feet
   * (Y increases downward). When omitted, the engine uses the bottom-centre of the current frame.
   */
  feet?: { x: number; y: number };
  /**
   * The sheet is drawn at `artScale`× (a denser texture) and shown at 1/artScale, so the character keeps its size.
   * `feet`, `collider`, `walkToPoint` and `talkPoint` stay in the 1× frame units (the sheet's pixels ÷ artScale).
   * Default 1. Same idea as the room `artScale`.
   */
  artScale?: number;
  /** Idle micro-actions (blink, look around, a tic) played at random while the character stands still. */
  idleActions?: CharacterIdleActionData[];
  /**
   * Contact shadow in rooms that have one (`RoomData.characterShadow`). `false` = none for this character (a ghost, a
   * screen). `width` is in 1× frame units at scale 1 (default: 85% of the collider width, else 40% of the frame);
   * `offsetX` / `offsetY` move it from the feet, in the same units.
   */
  shadow?: false | { width?: number; offsetX?: number; offsetY?: number };
  /**
   * Click hit area in **texture / frame pixel space** (same origin as `feet`). When omitted and the
   * character is clickable, the full sprite rectangle is used. Requires at least three vertices.
   */
  collider?: { points: { x: number; y: number }[] };
  /**
   * Optional stand position in **texture / frame pixel space** (same origin as `feet`).
   * World stand = sprite position + this offset. Used when scripts call `walkTo('<this id>')` targeting
   * this character, or when resolving another walker’s target to this character — same idea as prop `walkToPoint`.
   */
  walkToPoint?: Point2;
  /**
   * Optional “face / dialogue” point in **texture / frame pixel space** (same origin as `feet`).
   * World position = sprite position + offset. Verb payloads expose this as **world** `talkPoint`
   * for scripts (similar role to prop `lookAtPoint` in room space).
   */
  talkPoint?: Point2;
  /** Game pixels per second when walking (used when movement is implemented). */
  walkSpeed: number;
  /**
   * When false, pathfind walking is disabled for this character (`walkTo`, click-to-walk, verb walks).
   * Teleports (`moveTo` / `moveToNow`) still apply. Default true when omitted.
   */
  movable?: boolean;
  clickable: boolean;
  display: CharacterDisplayData;
  /** Optional per Aseprite-tag playback (keys must match `meta.frameTags` on `images/characters/<id>/<id>.json`). */
  animations?: CharacterAnimationsConfig;
  /**
   * Verb id invoked when an `inputProfile` slot resolves to `"defaultVerb"` on this character.
   * Falls back to `"look"` when omitted.
   */
  defaultVerb?: string;
  /** Enables character fallback dispatch when no supported verb matches. */
  onVerbFallback?: boolean;
  /**
   * Optional Aseprite tag on the **game** cursor sheet. When set and the pointer hovers this clickable
   * character, the cursor uses this tag instead of `cursor.activeAnimation`. Inventory cursor clips take precedence.
   */
  activeCursorOverride?: string;
  /**
   * Hex color for this character's speech text in the `speaking-text` GUI (e.g. `"#ff0000"`).
   * When omitted, the overlay keeps its authored default color (`#ffffff`).
   */
  speechColor?: string;
}
