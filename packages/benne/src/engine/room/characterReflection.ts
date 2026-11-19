/**
 * Floor reflection: a polished floor (marble, wet tiles) mirrors the characters that stand on it.
 *
 * The room art already carries the reflection of the room itself (drawn by the content tools); the characters are
 * separate sprites, so a room's {@link RoomCharacterReflectionData} turns on a copy of each character's current frame
 * mirrored about its feet: same texture, frame, facing, scale and light tint, faint and fading away from the feet.
 *
 * Every reflection sits just above the room background, under all props and characters: the reflection always falls
 * towards the camera (below the feet on screen), where anything that stands on the floor is in front of the
 * character anyway, and the room's front layers cover it the way they cover the character.
 *
 * Phaser flips a sprite about the middle of its frame, so the mirror is a negative `scaleY` with the display origin
 * on the feet instead. With a negative scale the frame's top row is drawn at the bottom, so the per-corner tint and
 * alpha are set in frame space: the "bottom" corners are the ones next to the feet.
 */
import * as Phaser from 'phaser';

import type { CharacterData } from '../../types/character';
import type { RoomCharacterReflectionData } from '../../types/room';
import { getCharacterWorldFeet } from '../characterFeet';

export interface CompiledCharacterReflection {
  /** Opacity next to the feet. */
  alpha: number;
  /** Opacity at the far end, as a fraction of `alpha` (0 = fades out completely). */
  fade: number;
  /** Height of the reflection ÷ height of the character (a high camera sees it shorter). */
  length: number;
  /** Below this room y the floor is not polished (or the room ends): the reflection is cut there. */
  maxY: number | null;
}

const cache = new WeakMap<RoomCharacterReflectionData, CompiledCharacterReflection>();

function num(v: unknown, fallback: number): number {
  return typeof v === 'number' && Number.isFinite(v) ? v : fallback;
}

/** Parses (once per room data object) the room's floor reflection; `null` when the room has none. */
export function compileCharacterReflection(
  data: RoomCharacterReflectionData | undefined,
): CompiledCharacterReflection | null {
  if (!data || data.enabled === false) {
    return null;
  }
  const hit = cache.get(data);
  if (hit) {
    return hit;
  }
  const out: CompiledCharacterReflection = {
    alpha: Math.max(0, Math.min(1, num(data.alpha, 0.2))),
    fade: Math.max(0, Math.min(1, num(data.fade, 0))),
    length: Math.max(0.05, num(data.length, 1)),
    maxY: typeof data.maxY === 'number' && Number.isFinite(data.maxY) ? data.maxY : null,
  };
  cache.set(data, out);
  return out;
}

type CharacterSprite = Phaser.GameObjects.Sprite | Phaser.GameObjects.Image;

/** Owns one mirrored Image per character sprite and keeps it in step with the character every frame. */
export class CharacterReflectionLayer {
  private readonly reflections = new Map<CharacterSprite, Phaser.GameObjects.Image>();

  private readonly scene: Phaser.Scene;

  constructor(scene: Phaser.Scene) {
    this.scene = scene;
  }

  /** Drops every reflection (scene teardown destroys the Images themselves). */
  clear(): void {
    this.reflections.clear();
  }

  /**
   * `reflection` null = the room has no polished floor. `depth`: just above the room background (the lowest sprite
   * of the room stack).
   */
  update(reflection: CompiledCharacterReflection | null, sprites: Iterable<CharacterSprite>, depth: number): void {
    const seen = new Set<CharacterSprite>();
    if (reflection) {
      for (const sprite of sprites) {
        if (!sprite.active) {
          continue;
        }
        seen.add(sprite);
        this.updateOne(reflection, sprite, depth);
      }
    }
    for (const [sprite, img] of this.reflections) {
      if (!seen.has(sprite)) {
        img.destroy();
        this.reflections.delete(sprite);
      }
    }
  }

  private updateOne(reflection: CompiledCharacterReflection, sprite: CharacterSprite, depth: number): void {
    const data = sprite.getData('character') as CharacterData | undefined;
    let img = this.reflections.get(sprite);
    if (data?.reflection === false) {
      if (img) {
        img.destroy();
        this.reflections.delete(sprite);
      }
      return;
    }
    if (!img) {
      const created = this.scene.add.image(0, 0, sprite.texture.key, sprite.frame.name);
      img = created;
      this.reflections.set(sprite, created);
      sprite.once(Phaser.GameObjects.Events.DESTROY, () => {
        if (this.reflections.get(sprite) === created) {
          created.destroy();
          this.reflections.delete(sprite);
        }
      });
    }
    const alpha = reflection.alpha * sprite.alpha;
    const visible = sprite.visible && alpha > 0.001;
    img.setVisible(visible);
    if (!visible) {
      return;
    }
    img.setDepth(depth);
    if (img.texture.key !== sprite.texture.key || img.frame.name !== sprite.frame.name) {
      img.setTexture(sprite.texture.key, sprite.frame.name);
    }
    const feet = getCharacterWorldFeet(sprite as Phaser.GameObjects.Sprite);
    const sy = sprite.scaleY;
    // The feet row in frame pixels (from the frame's top), then the mirror about it.
    const top = sprite.y - sprite.displayOriginY * sy;
    const feetRow = (feet.y - top) / sy;
    img.setFlipX(sprite.flipX);
    img.setDisplayOrigin(sprite.displayOriginX, feetRow);
    img.setScale(sprite.scaleX, -sy * reflection.length);
    img.setPosition(sprite.x, feet.y);
    // Only the part of the frame under the feet would mirror onto the wall: crop the frame to the feet row, and to
    // the end of the polished floor.
    const fh = sprite.frame.height;
    let rows = Math.max(0, Math.min(fh, feetRow));
    if (reflection.maxY !== null) {
      const room = (reflection.maxY - feet.y) / (sy * reflection.length);
      rows = Math.max(0, Math.min(rows, room));
    }
    img.setCrop(0, feetRow - rows, sprite.frame.width, rows);
    // The light falls on the reflection as on the character (frame space: the tints copy as they are).
    img.setTintMode(sprite.tintMode);
    img.setTint(sprite.tintTopLeft, sprite.tintTopRight, sprite.tintBottomLeft, sprite.tintBottomRight);
    // Faint next to the feet (the frame's bottom corners), fading towards the mirrored head (its top corners).
    const far = alpha * reflection.fade;
    img.setAlpha(far, far, alpha, alpha);
  }
}
