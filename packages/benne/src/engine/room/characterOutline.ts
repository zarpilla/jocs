/**
 * Character outline: a dark rim around each character, for rooms whose floor or walls are so bright (white marble,
 * sunlit water) that the sprites' own edges get lost against them.
 *
 * A room's {@link RoomCharacterOutlineData} turns on four copies of each character's current frame, filled with the
 * outline colour and shifted one step left, right, up and down, just under the character in the room stack: only the
 * rim around the silhouette shows. The copies use the character's own render nodes and data, so they are sampled
 * exactly like the character (perspective scale, `artScale` sheets) and stay aligned with it; the room's front
 * layers cover them the way they cover the character.
 */
import * as Phaser from 'phaser';

import type { CharacterData } from '../../types/character';
import type { RoomCharacterOutlineData } from '../../types/room';
import { attachBenneCharacterPerspectiveRenderNodes } from '../rendering/benneCharacterPerspectiveBatch';

export interface CompiledCharacterOutline {
  /** Fill colour (0xRRGGBB). */
  color: number;
  /** Opacity of the rim (times the character's own alpha). */
  alpha: number;
  /** Thickness in room pixels. */
  width: number;
}

const cache = new WeakMap<RoomCharacterOutlineData, CompiledCharacterOutline>();

function num(v: unknown, fallback: number): number {
  return typeof v === 'number' && Number.isFinite(v) ? v : fallback;
}

/** Parses (once per room data object) the room's character outline; `null` when the room has none. */
export function compileCharacterOutline(data: RoomCharacterOutlineData | undefined): CompiledCharacterOutline | null {
  if (!data || data.enabled === false) {
    return null;
  }
  const hit = cache.get(data);
  if (hit) {
    return hit;
  }
  const m = typeof data.color === 'string' ? /^#?([0-9a-f]{6})$/i.exec(data.color.trim()) : null;
  const out: CompiledCharacterOutline = {
    color: m ? parseInt(m[1], 16) : 0x000000,
    alpha: Math.max(0, Math.min(1, num(data.alpha, 0.7))),
    width: Math.max(0.25, num(data.width, 1)),
  };
  cache.set(data, out);
  return out;
}

type CharacterSprite = Phaser.GameObjects.Sprite | Phaser.GameObjects.Image;

/** The four offsets of the rim copies (left, right, up, down), in units of the outline width. */
export const OUTLINE_OFFSETS: ReadonlyArray<readonly [number, number]> = [[-1, 0], [1, 0], [0, -1], [0, 1]];

/** Owns the rim copies of each character sprite and keeps them in step with the character every frame. */
export class CharacterOutlineLayer {
  private readonly outlines = new Map<CharacterSprite, Phaser.GameObjects.Image[]>();

  private readonly scene: Phaser.Scene;

  constructor(scene: Phaser.Scene) {
    this.scene = scene;
  }

  /** Drops every outline (scene teardown destroys the Images themselves). */
  clear(): void {
    this.outlines.clear();
  }

  /** `outline` null = the room has none. */
  update(outline: CompiledCharacterOutline | null, sprites: Iterable<CharacterSprite>): void {
    const seen = new Set<CharacterSprite>();
    if (outline) {
      for (const sprite of sprites) {
        if (!sprite.active) {
          continue;
        }
        seen.add(sprite);
        this.updateOne(outline, sprite);
      }
    }
    for (const [sprite, imgs] of this.outlines) {
      if (!seen.has(sprite)) {
        for (const img of imgs) {
          img.destroy();
        }
        this.outlines.delete(sprite);
      }
    }
  }

  private drop(sprite: CharacterSprite): void {
    for (const img of this.outlines.get(sprite) ?? []) {
      img.destroy();
    }
    this.outlines.delete(sprite);
  }

  private updateOne(outline: CompiledCharacterOutline, sprite: CharacterSprite): void {
    const data = sprite.getData('character') as CharacterData | undefined;
    if (data?.outline === false) {
      this.drop(sprite);
      return;
    }
    let imgs = this.outlines.get(sprite);
    if (!imgs) {
      const created = OUTLINE_OFFSETS.map(() => {
        const img = this.scene.add.image(0, 0, sprite.texture.key, sprite.frame.name);
        attachBenneCharacterPerspectiveRenderNodes(img);
        return img;
      });
      imgs = created;
      this.outlines.set(sprite, created);
      sprite.once(Phaser.GameObjects.Events.DESTROY, () => {
        if (this.outlines.get(sprite) === created) {
          this.drop(sprite);
        }
      });
    }
    const alpha = outline.alpha * sprite.alpha;
    const visible = sprite.visible && alpha > 0.001;
    // Just under the character, above its contact shadow (at depth − 0.5).
    const depth = sprite.depth - 0.25;
    OUTLINE_OFFSETS.forEach(([dx, dy], i) => {
      const img = imgs[i];
      img.setVisible(visible);
      if (!visible) {
        return;
      }
      if (img.texture.key !== sprite.texture.key || img.frame.name !== sprite.frame.name) {
        img.setTexture(sprite.texture.key, sprite.frame.name);
      }
      // (the batch reads the character data: the sheet's artScale)
      img.setData('character', data);
      img.setDepth(depth);
      img.setFlipX(sprite.flipX);
      img.setDisplayOrigin(sprite.displayOriginX, sprite.displayOriginY);
      img.setScale(sprite.scaleX, sprite.scaleY);
      img.setPosition(sprite.x + dx * outline.width, sprite.y + dy * outline.width);
      img.setTintMode(Phaser.TintModes.FILL);
      img.setTint(outline.color);
      img.setAlpha(alpha);
    });
  }
}
