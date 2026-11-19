/**
 * Contact shadow: a dark, semi-transparent ellipse on the floor under each character's feet.
 *
 * It is drawn by the engine, not in the character sheet, so it follows the character's perspective scale and the
 * room's light: a room's {@link RoomCharacterShadowData} turns it on and may name a dominant light (a lamp, a window,
 * the sun); the shadow then stretches across the floor away from it. The ellipse lives in floor coordinates (x to
 * the right, z into the room) and is squashed vertically onto the screen, so a stretched shadow keeps lying flat.
 *
 * The shadow is a Phaser Graphics just below the character in the room stack (depth − 0.5), redrawn only when its
 * shape changes.
 */
import * as Phaser from 'phaser';

import type { CharacterData } from '../../types/character';
import type { RoomCharacterShadowData } from '../../types/room';
import {
  characterArtScale,
  characterSpriteArtScale,
  frameSizeVariantScale,
  getCharacterWorldFeet,
} from '../characterFeet';

export interface CompiledCharacterShadow {
  color: number;
  alpha: number;
  squash: number;
  /** Fraction of the width taken by the darker core (0 = one flat ellipse). */
  core: number;
  /** Floor point under the dominant light, room px. */
  lightPoint: { x: number; y: number } | null;
  /** Floor direction the shadow falls in (screen px, normalised in floor space) for a far light such as the sun. */
  direction: { x: number; y: number } | null;
  stretch: number;
  reach: number;
}

const cache = new WeakMap<RoomCharacterShadowData, CompiledCharacterShadow>();

function num(v: unknown, fallback: number): number {
  return typeof v === 'number' && Number.isFinite(v) ? v : fallback;
}

/** Parses (once per room data object) the room's contact shadow; `null` when the room has none. */
export function compileCharacterShadow(data: RoomCharacterShadowData | undefined): CompiledCharacterShadow | null {
  if (!data || data.enabled === false) {
    return null;
  }
  const hit = cache.get(data);
  if (hit) {
    return hit;
  }
  const m = typeof data.color === 'string' ? /^#?([0-9a-f]{6})$/i.exec(data.color.trim()) : null;
  const light = data.light;
  const out: CompiledCharacterShadow = {
    color: m ? parseInt(m[1], 16) : 0x000000,
    alpha: Math.max(0, Math.min(1, num(data.alpha, 0.35))),
    squash: Math.max(0.05, num(data.squash, 0.3)),
    core: Math.max(0, Math.min(0.95, num(data.core, 0.6))),
    lightPoint: light && light.direction !== true ? { x: num(light.x, 0), y: num(light.y, 0) } : null,
    direction: light && light.direction === true ? { x: num(light.x, 0), y: num(light.y, 0) } : null,
    stretch: Math.max(0, num(light?.stretch, 0.8)),
    reach: Math.max(1, num(light?.reach, 120)),
  };
  cache.set(data, out);
  return out;
}

/** Shadow width at scale 1 (room px): `character.shadow.width`, else from the collider, else from the frame. */
export function characterShadowBaseWidth(data: CharacterData | undefined, frameWidth: number): number {
  const s = data?.shadow;
  if (s && typeof s === 'object' && typeof s.width === 'number' && s.width > 0) {
    return s.width;
  }
  const pts = data?.collider?.points;
  if (pts && pts.length >= 3) {
    let lo = Infinity;
    let hi = -Infinity;
    for (const p of pts) {
      lo = Math.min(lo, p.x);
      hi = Math.max(hi, p.x);
    }
    if (hi > lo) {
      return (hi - lo) * 0.85;
    }
  }
  return (frameWidth / characterArtScale(data)) * 0.4;
}

export interface ShadowEllipse {
  /** Centre on screen, room px. */
  cx: number;
  cy: number;
  /** Screen-space outline (room px), closed. */
  points: { x: number; y: number }[];
}

/**
 * The shadow outline for feet at `(feetX, feetY)` and half-width `rx` (room px, already scaled): a floor ellipse
 * stretched by `1 + stretch` away from the light, with its near end still under the feet.
 */
export function shadowEllipse(
  shadow: CompiledCharacterShadow,
  feetX: number,
  feetY: number,
  rx: number,
  segments = 24,
): ShadowEllipse {
  const q = shadow.squash;
  // Unit direction the shadow falls in, in floor space (screen y unsquashed), and how far it stretches.
  let fx = 0;
  let fz = 0;
  let stretch = 0;
  if (shadow.direction) {
    const len = Math.hypot(shadow.direction.x, shadow.direction.y / q);
    if (len > 1e-6) {
      fx = shadow.direction.x / len;
      fz = shadow.direction.y / q / len;
      stretch = shadow.stretch;
    }
  } else if (shadow.lightPoint) {
    const dx = feetX - shadow.lightPoint.x;
    const dz = (feetY - shadow.lightPoint.y) / q;
    const len = Math.hypot(dx, dz);
    if (len > 1e-6) {
      fx = dx / len;
      fz = dz / len;
      // Right under the light the shadow is round; it grows to full stretch at `reach`.
      stretch = shadow.stretch * Math.min(1, len / shadow.reach);
    }
  }
  const along = rx * (1 + stretch);
  // Centre in floor space: shifted along the fall so the near edge stays under the feet.
  const czx = fx * rx * stretch;
  const czz = fz * rx * stretch;
  const nx = -fz;
  const nz = fx;
  const points: { x: number; y: number }[] = [];
  for (let i = 0; i < segments; i++) {
    const t = (i / segments) * Math.PI * 2;
    const c = Math.cos(t);
    const s = Math.sin(t);
    // Unstretched (no light): plain circle of radius rx (fx = fz = 0 → use x axis).
    const ax = stretch > 0 ? fx : 1;
    const az = stretch > 0 ? fz : 0;
    const bx = stretch > 0 ? nx : 0;
    const bz = stretch > 0 ? nz : 1;
    const px = czx + ax * along * c + bx * rx * s;
    const pz = czz + az * along * c + bz * rx * s;
    points.push({ x: feetX + px, y: feetY + pz * q });
  }
  return { cx: feetX + czx, cy: feetY + czz * q, points };
}

type CharacterSprite = Phaser.GameObjects.Sprite | Phaser.GameObjects.Image;

/** Owns one Graphics per character sprite and keeps it under its feet. */
export class CharacterShadowLayer {
  private readonly shadows = new Map<CharacterSprite, { g: Phaser.GameObjects.Graphics; key: string }>();

  private readonly scene: Phaser.Scene;

  constructor(scene: Phaser.Scene) {
    this.scene = scene;
  }

  /** Drops every shadow (scene teardown destroys the Graphics themselves). */
  clear(): void {
    this.shadows.clear();
  }

  /** Call after the room stack depths are set. `shadow` null = the room has no contact shadow. */
  update(shadow: CompiledCharacterShadow | null, sprites: Iterable<CharacterSprite>): void {
    const seen = new Set<CharacterSprite>();
    if (shadow) {
      for (const sprite of sprites) {
        if (!sprite.active) {
          continue;
        }
        seen.add(sprite);
        this.updateOne(shadow, sprite);
      }
    }
    for (const [sprite, entry] of this.shadows) {
      if (!seen.has(sprite)) {
        entry.g.destroy();
        this.shadows.delete(sprite);
      }
    }
  }

  private updateOne(shadow: CompiledCharacterShadow, sprite: CharacterSprite): void {
    const data = sprite.getData('character') as CharacterData | undefined;
    let entry = this.shadows.get(sprite);
    if (data?.shadow === false) {
      if (entry) {
        entry.g.destroy();
        this.shadows.delete(sprite);
      }
      return;
    }
    if (!entry) {
      const g = this.scene.add.graphics();
      entry = { g, key: '' };
      this.shadows.set(sprite, entry);
      sprite.once(Phaser.GameObjects.Events.DESTROY, () => {
        const e = this.shadows.get(sprite);
        if (e) {
          e.g.destroy();
          this.shadows.delete(sprite);
        }
      });
    }
    const { g } = entry;
    const alpha = shadow.alpha * sprite.alpha;
    const visible = sprite.visible && alpha > 0.001;
    g.setVisible(visible);
    g.setDepth(sprite.depth - 0.5);
    if (!visible) {
      return;
    }
    // `artScale` × the frame's size variant: the perspective scale in 1× frame units.
    const artScale = characterSpriteArtScale(sprite);
    const perspective = Math.abs(sprite.scaleX) * artScale;
    const feet = getCharacterWorldFeet(sprite as Phaser.GameObjects.Sprite);
    const cfg = data?.shadow && typeof data.shadow === 'object' ? data.shadow : undefined;
    const fx = feet.x + num(cfg?.offsetX, 0) * perspective;
    const fy = feet.y + num(cfg?.offsetY, 0) * perspective;
    const rx = (characterShadowBaseWidth(data, sprite.frame.width / frameSizeVariantScale(sprite)) * perspective) / 2;
    const key = `${fx.toFixed(2)},${fy.toFixed(2)},${rx.toFixed(3)},${alpha.toFixed(3)}`;
    if (key === entry.key) {
      return;
    }
    entry.key = key;
    g.clear();
    // Two tones: a lighter rim and a darker core, together reaching `alpha` at the centre.
    const core = shadow.core;
    const rim = core > 0 ? 1 - Math.sqrt(1 - alpha) : alpha;
    g.fillStyle(shadow.color, rim);
    const fill = (r: number): void => {
      g.fillPoints(
        shadowEllipse(shadow, fx, fy, r).points.map((p) => new Phaser.Math.Vector2(p.x, p.y)),
        true,
      );
    };
    fill(rx);
    if (core > 0) {
      fill(rx * core);
    }
  }
}
