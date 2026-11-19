import type { CharacterFacingLetter, CharacterAnimationsConfig } from './character';

export interface Point2 {
  x: number;
  y: number;
}

/** Inner ring subtracted from a walkable polygon when `active` is not false. */
export interface WalkableHole {
  id: string;
  /** When false, this ring does not cut a hole (ignored for walk tests and debug). Omitted = active. */
  active?: boolean;
  points: Point2[];
}

export interface WalkablePolygon {
  id: string;
  /** BenneScript handle name, when the generated one doesn't fit (docs/bennescript-ergonomics-refactor.md §7.2). */
  scriptName?: string;
  /** When false, this polygon is ignored for walking and debug overlays. Omitted = active. */
  active?: boolean;
  points: Point2[];
  /** Optional holes (each an inner closed ring). Inactive holes are ignored. */
  holes?: WalkableHole[];
}

/**
 * Clickable room hotspot: closed polygon in room pixels (same space as walkable meshes).
 * The engine requires at least three vertices in `points` for hit-testing.
 */
export interface RoomHotspotData {
  id: string;
  /** BenneScript handle name, when the generated one doesn't fit (docs/bennescript-ergonomics-refactor.md §7.2). */
  scriptName?: string;
  /** When false, ignored for interaction. Omitted = active. */
  active?: boolean;
  description?: string;
  /** Draw / hit stacking vs other hotspots (higher tested later, tends to sit on top). */
  zIndex?: number;
  /**
   * Room-space Y (pixels, y increases downward). When set, characters with **world feet Y greater
   * than** this line draw in front of this hotspot’s stack entry; otherwise `zIndex` ordering applies.
   */
  baseline?: number;
  /** Polygon hit area in room pixels (at least three vertices). */
  points: Point2[];
  /** Where the player walks when this hotspot is used (optional; editor + future walk-to flow). */
  walkToPoint?: Point2;
  /** Facing target after walking (optional; pairs with `walkToPoint`). */
  lookAtPoint?: Point2;
  /**
   * Verb id invoked when an `inputProfile` slot resolves to `"defaultVerb"` on this hotspot.
   * Falls back to `"look"` when omitted.
   */
  defaultVerb?: string;
  /** Enables object-level fallback dispatch when no supported verb matches. */
  onVerbFallback?: boolean;
  /**
   * Optional Aseprite tag on the **game** cursor sheet (`game-config.json` `cursor` + `images/cursor/`).
   * When set and the pointer hovers this hotspot, the custom cursor uses this tag instead of
   * `cursor.activeAnimation`. Active inventory with `cursorAnimation` still wins.
   */
  activeCursorOverride?: string;
}

/** Named marker in room space (spawns, triggers, script anchors). */
export interface RoomPointData {
  id: string;
  /** BenneScript handle name, when the generated one doesn't fit (docs/bennescript-ergonomics-refactor.md §7.2). */
  scriptName?: string;
  x: number;
  y: number;
}

/** Logical area (perspective scale, tint, walk blocking, triggers) as a closed polygon in room space. */
export interface RoomRegionData {
  id: string;
  /** BenneScript handle name, when the generated one doesn't fit (docs/bennescript-ergonomics-refactor.md §7.2). */
  scriptName?: string;
  /** When false, ignored by tooling/runtime that respects regions. Omitted = active. */
  active?: boolean;
  /**
   * When `false`, characters cannot walk through this polygon (treated as a hole in the walkable mesh).
   * Omitted or `true` = walkable (no movement restriction from this region).
   */
  walkable?: boolean;
  points: Point2[];
  /**
   * When `true`, this region applies perspective character scale (`scaleTop` / `scaleBottom`) and
   * optional `scaleWalkSpeed`. Omitted or not `true` = this region does not scale (it does not
   * cancel scale from an earlier overlapping region).
   */
  scaleEnabled?: boolean;
  /**
   * Character scale at the **top** of the region (smaller room Y). `1` = normal size. Omitted = `1`.
   * Interpolates linearly with {@link scaleBottom} by feet Y across the region’s vertical bounds.
   * Applied only when {@link scaleEnabled} is `true`.
   */
  scaleTop?: number;
  /**
   * Character scale at the **bottom** of the region (larger room Y). Omitted = `1`.
   * Applied only when {@link scaleEnabled} is `true`.
   */
  scaleBottom?: number;
  /**
   * When `true`, walking speed is multiplied by a perspective factor derived from the same linear
   * {@link scaleTop} / {@link scaleBottom} value as sprite scale (see `game-config.json` `perspective`).
   * Omitted = `false`. Read only from the scale winner (`scaleEnabled`).
   */
  scaleWalkSpeed?: boolean;
  /**
   * When `true`, this region is a character-tint source (`tint` / `tintAlpha`). Omitted or not
   * `true` = this region does not tint (it does not clear tint from an earlier overlapping region).
   */
  tintEnabled?: boolean;
  /**
   * Hex RGB (e.g. `#aabbcc`). When this region is the tint winner (`tintEnabled`), characters
   * multiply-tint toward this color. Omitted or invalid hex = no tint color from this region.
   */
  tint?: string;
  /**
   * 0–1 blend between no tint and full {@link tint} multiply (`1` = full strength). Omitted = `1` when `tint` is set.
   * Applied only when this region is the tint winner ({@link tintEnabled}).
   */
  tintAlpha?: number;
}

/** A point light that falls on the room's characters (see {@link RoomCharacterLightsData}). */
export interface RoomCharacterLightData {
  x: number;
  y: number;
  /** Reach in room pixels: the light fades to nothing here. */
  radius: number;
  /** Hex RGB (e.g. `#50e6d2`). */
  color: string;
  /** Strength; `1` adds the full colour at the centre. Omitted = `1`. */
  intensity?: number;
  /** Vertical stretch of the distance (`> 1` = flatter light). Omitted = `1`. */
  squash?: number;
  /** Falloff exponent. Omitted = `1.6`. */
  power?: number;
  /** Only while this prop is visible (a lamp that is switched on, a hatch that is open). */
  whenPropVisible?: string;
}

/**
 * The room's light on its characters, evaluated at runtime at the corners of each sprite. The light is
 * `ambient + Σ light` per channel, where `#ffffff` ambient and no light leave the sprite as drawn; it is set as an
 * overlay tint (below 1 darkens, above 1 lightens). Replaces region tint (`tintEnabled`) in the room.
 */
export interface RoomCharacterLightsData {
  /** Hex RGB; `#ffffff` = as drawn, darker = a darker room. Omitted = `#ffffff`. */
  ambient?: string;
  lights?: RoomCharacterLightData[];
  /** Where the top corners sample the light, as a fraction of the sprite height from its top. Omitted = `0.15`. */
  topSample?: number;
}

/**
 * Contact shadow under the room's characters: a dark, semi-transparent floor ellipse the engine draws under each
 * character's feet (not part of the sheet), scaled with the character. Width per character: `CharacterData.shadow`.
 */
export interface RoomCharacterShadowData {
  /** `false` turns it off (same as omitting the object). Omitted = on. */
  enabled?: boolean;
  /** Hex RGB. Omitted = `#000000`. */
  color?: string;
  /** Opacity at the centre. Omitted = `0.35`. */
  alpha?: number;
  /** Ellipse height ÷ width: how much of the floor the camera sees from above. Omitted = `0.3`. */
  squash?: number;
  /** Width of the darker core as a fraction of the shadow (two tones); `0` = one flat ellipse. Omitted = `0.6`. */
  core?: number;
  /**
   * The dominant light: the shadow stretches across the floor away from it. `x, y` is the floor point under the
   * light (room px: a lamp, the foot of a window); with `direction: true` it is instead the direction the shadow
   * falls in (screen px, e.g. `{ x: 1, y: 0.3 }` for a low sun on the left).
   */
  light?: {
    x: number;
    y: number;
    direction?: boolean;
    /** Extra length along the fall, as a fraction of the width (`1` = twice as long). Omitted = `0.8`. */
    stretch?: number;
    /** Floor distance (room px) from the light at which the stretch is full; under it the shadow is round. Omitted = `120`. */
    reach?: number;
  };
}

/**
 * A polished floor (marble, wet tiles): each character gets a faint copy of itself mirrored about its feet, fading
 * away from them. The room art carries the reflection of the room itself; this is the characters'.
 */
export interface RoomCharacterReflectionData {
  /** `false` turns it off (same as omitting the object). Omitted = on. */
  enabled?: boolean;
  /** Opacity next to the feet. Omitted = `0.2`. */
  alpha?: number;
  /** Opacity at the far end (the mirrored head), as a fraction of `alpha`. Omitted = `0` (fades out). */
  fade?: number;
  /** Height of the reflection ÷ height of the character (a high camera sees it shorter). Omitted = `1`. */
  length?: number;
  /** Room y below which the floor does not reflect (where the polished floor ends). Omitted = no limit. */
  maxY?: number;
}

export interface RoomCharacterInstance {
  /** Unique id for this placement in the room (Phaser texture key suffix). */
  instanceId: string;
  /** Path relative to `src/game/characters/` (e.g. `clerk/clerk.character.json`). */
  definition: string;
  x: number;
  y: number;
  /** Facing for the first directional animation (e.g. `Idle` + `L` -> `IdleL`). */
  initialFacing?: CharacterFacingLetter;
  /** Base name before direction suffix; default `Idle`. */
  initialAnimation?: string;
  /** When false, sprite is hidden and not interactive. Default true. */
  visible?: boolean;
  /** Added to the engine character layer base depth; higher draws in front of lower. */
  zIndex?: number;
}

/** Clickable / hit-test region for a room prop, in room pixel space (same as walkable polygons). */
export interface RoomPropCollider {
  points: Point2[];
}

/**
 * One placed prop in a room: Aseprite tag on this room's sheet (`images/rooms/<roomId>/`), draw order, and interaction.
 */
export interface RoomPropInstance {
  id: string;
  /** BenneScript handle name, when the generated one doesn't fit (docs/bennescript-ergonomics-refactor.md §7.2). */
  scriptName?: string;
  /**
   * Aseprite frame-tag name for this prop. Must appear in `meta.frameTags` on the room sheet
   * (see `getAsepriteFrameTagNames('room', roomId)`); cels with no tag are not props.
   */
  tag: string;
  /**
   * Optional extra root for `<root>-*` clip families on the room sheet (editor / import tooling).
   * When set (non-empty), tags matching `defaultAnimation` or `defaultAnimation-*` are grouped with this prop
   * alongside tags matching `id` / `id-*`. Omitted when `id` alone is the Aseprite prefix root.
   */
  defaultAnimation?: string;
  /**
   * How the prop’s `x` / `y` fields map to the Aseprite cel when the room sheet uses **trim cells** (JSON
   * `spriteSourceSize` / Phaser `frame.data.trim`).
   * - **`canvas`** (default): `(x, y)` is the **logical cel / sheet canvas** origin — same as a GUI
   *   `screen` anchor; Phaser’s built-in trim offset keeps art aligned with the Aseprite canvas
   *   (typical full-room composite props).
   * - **`tight`**: `(x, y)` is the **top-left of the trimmed opaque** region in room pixels — same
   *   idea as a GUI `top-left` image with trim; the engine subtracts `spriteSourceSize` and keeps
   *   it in sync when the prop’s current frame changes.
   */
  spritePlacement?: 'canvas' | 'tight';
  /** Sprite position in room pixels (default top-left 0,0 for full-room composite frames). */
  x?: number;
  y?: number;
  /** Draw order: higher values render in front of lower values. */
  zIndex?: number;
  /**
   * Room-space Y (pixels, y increases downward). When set, characters with **world feet Y greater
   * than** this line draw in front of this prop; otherwise `zIndex` ordering applies.
   */
  baseline?: number;
  /** When true, the prop may receive clicks; the engine dispatches verb scripts immediately (no auto walk/face). */
  clickable?: boolean;
  visible?: boolean;
  /** 0–1; default 1. */
  alpha?: number;
  /**
   * Optional stand position for script-driven movement (not used by the engine for clicks).
   * Game scripts may read this from payloads / room data when implementing walk-to-object behavior.
   */
  walkToPoint?: Point2;
  /**
   * Optional facing target for script-driven facing (not used by the engine for clicks).
   */
  lookAtPoint?: Point2;
  description?: string;
  /** Hit area in room space; required when `clickable` is true. */
  collider?: RoomPropCollider;
  /**
   * Verb id invoked when an `inputProfile` slot resolves to `"defaultVerb"` on this prop.
   * Falls back to `"look"` when omitted. Shown in the Inspector as the "Default verb" dropdown.
   */
  defaultVerb?: string;
  /** Enables object-level fallback dispatch when no supported verb matches (before global handlers). */
  onVerbFallback?: boolean;
  /**
   * Optional Aseprite tag on the **game** cursor sheet. When set and the pointer hovers this clickable
   * prop, the cursor uses this tag instead of `cursor.activeAnimation`. Inventory cursor clips take precedence.
   */
  activeCursorOverride?: string;
  /** Per-tag playback (loop, frameDuration); keys match Aseprite tags on this room's sheet. */
  animations?: CharacterAnimationsConfig;
  /**
   * Parallax multiplier vs camera view. Each frame:
   * `sprite position = parallaxDepth * (x,y) + (1 - parallaxDepth) * (worldView.x, worldView.y)`.
   * - `0` — moves fully with the camera (world position tracks scroll origin)
   * - `0–1` — distant; moves slower than the camera
   * - `1` — no parallax (default if omitted); stays at authored `(x, y)`
   * - `>1` — foreground; moves faster than the camera
   */
  parallaxDepth?: number;
}

export interface RoomData {
  id: string;
  /** BenneScript handle name, when the generated one doesn't fit (docs/bennescript-ergonomics-refactor.md §7.2). */
  scriptName?: string;
  name: string;
  /**
   * Explicit room dimensions in pixels. When omitted the room is assumed to be the same size as the
   * game viewport (e.g. 352x198). Set this when the prop sheet is wider or taller than
   * the game resolution so the camera can scroll.
   */
  size?: { width: number; height: number };
  /**
   * Camera scroll bounds in room pixel space. Restricts how far the camera can pan within the room.
   * When omitted the camera is bounded by the full room `size`.
   * The character can walk beyond scroll bounds but the camera stops panning before reaching the room edge.
   */
  scrollBounds?: { x: number; y: number; width: number; height: number };
  /**
   * Adaptive height (`resolution.minHeight`): when the scroll bounds are taller than the screen, the camera
   * doesn't follow the player up and down but stays here: 0 = top of the bounds, 1 = bottom, 0.5 = middle.
   * For a room painted for the tallest screen whose playable part fits the shortest.
   */
  viewAnchorY?: number;
  walkable: {
    polygons: WalkablePolygon[];
  };
  hotspots: RoomHotspotData[];
  /** Named points in room space (optional; used by editor and future systems). */
  points?: RoomPointData[];
  /** Closed polygons for regions (optional; editor + future gameplay). */
  regions?: RoomRegionData[];
  /** Runtime light on the characters (optional). */
  characterLights?: RoomCharacterLightsData;
  /** Contact shadow under the characters (optional; off when omitted). */
  characterShadow?: RoomCharacterShadowData;
  /** Characters mirrored in a polished floor. */
  characterReflection?: RoomCharacterReflectionData;
  /**
   * How much the camera flattens the floor: screen height ÷ floor depth of a small patch of floor (the same idea as
   * `characterShadow.squash`; e.g. `0.25` for a high camera far away). Walk facings are then chosen on the floor, so a
   * diagonal walk into the room gets the 3/4 facings even when it looks almost horizontal on screen. Omitted = `1`
   * (facings chosen on the screen, as before).
   */
  floorSquash?: number;
  /**
   * Pixels of the room sheet (`images/rooms/<id>/<id>.png`) per room pixel. `2` = the room art is drawn at twice the
   * room resolution and shown at half scale: the geometry, scripts and characters stay in room pixels, and on a
   * screen of at least twice the internal resolution the art shows all its detail. Omitted = `1`.
   */
  artScale?: number;
  /**
   * Layered Aseprite props from `images/rooms/<id>/<id>.png` + `.json` (one sheet per room).
   */
  props?: RoomPropInstance[];
  /** NPCs / props that use a character definition. */
  characters?: RoomCharacterInstance[];
}
