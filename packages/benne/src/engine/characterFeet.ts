import type { CharacterData } from '../types/character';

/** Pixel offset from the top-left of the character texture frame to the ground contact (feet). */
export type CharacterFeetLocal = { x: number; y: number };

const FEET_LOCAL_X = 'feetLocalX';
const FEET_LOCAL_Y = 'feetLocalY';

/** The character sheet's `artScale` (1 when omitted or invalid). */
export function characterArtScale(data: { artScale?: number } | undefined): number {
  const k = data?.artScale;
  return typeof k === 'number' && k > 0 ? k : 1;
}

/** Sprite data key: the size-variant scale the sprite was last placed at (see {@link applyCharacterSizeVariant}). */
const PLACED_SIZE_SCALE = 'benneSizeScale';

/**
 * Scale of the size variant an animation tag belongs to (`CharacterData.sizeVariants`): the longest prefix of `tag`
 * listed there, else 1 (the plain sheet).
 */
export function characterSizeVariantScale(
  data: { sizeVariants?: Record<string, number> } | undefined,
  tag: string | undefined,
): number {
  const variants = data?.sizeVariants;
  if (!variants || !tag) {
    return 1;
  }
  let best = '';
  let k = 1;
  for (const [prefix, scale] of Object.entries(variants)) {
    if (prefix.length > best.length && tag.startsWith(prefix) && typeof scale === 'number' && scale > 0) {
      best = prefix;
      k = scale;
    }
  }
  return k;
}

/** Per texture key: frame name → size-variant scale, for the frames that belong to a variant (the rest are 1). */
const sizeVariantFrames = new Map<string, Map<string, number>>();

/**
 * Records which frames of a character sheet belong to a size variant, from the clips `createFromAseprite` made
 * (the tag names). Call once per spawn; a sheet without `sizeVariants` records nothing.
 */
export function registerCharacterSizeVariantFrames(
  textureKey: string,
  data: CharacterData,
  anims: readonly { key: string; frames: readonly { textureFrame: string | number }[] }[],
): void {
  if (!data.sizeVariants || Object.keys(data.sizeVariants).length === 0) {
    sizeVariantFrames.delete(textureKey);
    return;
  }
  const byFrame = new Map<string, number>();
  for (const anim of anims) {
    const k = characterSizeVariantScale(data, anim.key);
    if (k === 1) {
      continue;
    }
    for (const f of anim.frames) {
      byFrame.set(String(f.textureFrame), k);
    }
  }
  sizeVariantFrames.set(textureKey, byFrame);
}

/** Size-variant scale of the frame a sprite / image shows now (1 for the plain sheet or a non-character). */
export function frameSizeVariantScale(obj: {
  texture?: { key: string };
  frame?: { name: string | number };
}): number {
  const key = obj.texture?.key;
  const name = obj.frame?.name;
  if (key === undefined || name === undefined) {
    return 1;
  }
  return sizeVariantFrames.get(key)?.get(String(name)) ?? 1;
}

/**
 * Sheet pixels per 1× frame unit for the frame shown now: `artScale` × the frame's size variant. The sprite is shown
 * at `perspective scale / this`, so a variant drawn bigger keeps the size the room gives the character.
 */
export function characterSpriteArtScale(obj: {
  texture?: { key: string };
  frame?: { name: string | number };
  getData?: (key: string) => unknown;
}): number {
  const data = typeof obj.getData === 'function' ? (obj.getData('character') as CharacterData | undefined) : undefined;
  return characterArtScale(data) * frameSizeVariantScale(obj);
}

/**
 * Resolves feet in the plain sheet's texture space (`feet` × `artScale`, without any size variant): explicit
 * `character.feet`, else bottom-centre of the current frame. A variant's frames keep the 1× layout scaled by its
 * factor (same top-left corner, feet × factor), so the variant's feet are these × its scale
 * ({@link applyCharacterSizeVariant}).
 */
export function resolveCharacterFeetLocal(data: CharacterData, sprite: Phaser.GameObjects.Sprite): CharacterFeetLocal {
  if (data.feet) {
    const k = characterArtScale(data);
    return { x: data.feet.x * k, y: data.feet.y * k };
  }
  const f = sprite.frame;
  const v = frameSizeVariantScale(sprite);
  return { x: (f.width * 0.5) / v, y: f.height / v };
}

/**
 * The plain-sheet feet of a sprite placed by {@link applyCharacterSizeVariant} (its stored feet ÷ the variant it was
 * placed at), or `undefined` when it was never placed.
 */
export function getPlacedPlainFeetLocal(sprite: Phaser.GameObjects.GameObject): CharacterFeetLocal | undefined {
  const lx = sprite.getData(FEET_LOCAL_X) as number | undefined;
  const ly = sprite.getData(FEET_LOCAL_Y) as number | undefined;
  if (typeof lx !== 'number' || typeof ly !== 'number') {
    return undefined;
  }
  const v = (sprite.getData(PLACED_SIZE_SCALE) as number | undefined) ?? 1;
  return { x: lx / v, y: ly / v };
}

/**
 * Places a character by its feet at `perspectiveScale` (the room's region scale), taking the frame's size variant
 * into account: the sprite is scaled by `perspectiveScale / (artScale × variant)` and the feet (`plainFeet`, in the
 * plain sheet's texture px) by the variant. Everything in 1× frame units (collider, talkPoint, shadow) then lands
 * where it would with the plain sheet at that scale.
 */
export function applyCharacterSizeVariant(
  sprite: Phaser.GameObjects.Sprite,
  plainFeet: CharacterFeetLocal,
  perspectiveScale: number,
  worldFeetX: number,
  worldFeetY: number,
): void {
  const v = frameSizeVariantScale(sprite);
  const s = perspectiveScale / (characterArtScale(sprite.getData('character') as CharacterData | undefined) * v);
  sprite.setScale(s, s);
  placeSpriteByFeet(sprite, v === 1 ? plainFeet : { x: plainFeet.x * v, y: plainFeet.y * v }, worldFeetX, worldFeetY);
  sprite.setData(PLACED_SIZE_SCALE, v);
}

/**
 * When the frame switches to another size variant (a new outfit, an idle action, a script tag), rescales the sprite
 * about its feet at once, so the feet and the on-screen size don't jump until the next placement. Attach once per
 * character sprite whose data has `sizeVariants`.
 */
export function keepFeetAcrossSizeVariants(sprite: Phaser.GameObjects.Sprite): void {
  const resync = (): void => {
    const placed = sprite.getData(PLACED_SIZE_SCALE) as number | undefined;
    const v = frameSizeVariantScale(sprite);
    if (typeof placed !== 'number' || placed === v) {
      return;
    }
    const plain = getPlacedPlainFeetLocal(sprite);
    if (!plain) {
      return;
    }
    const feet = getCharacterWorldFeet(sprite);
    const perspective = Math.abs(sprite.scaleX) * characterArtScale(sprite.getData('character') as CharacterData) * placed;
    applyCharacterSizeVariant(sprite, plain, perspective, feet.x, feet.y);
  };
  sprite.on('animationstart', resync);
  sprite.on('animationrestart', resync);
  sprite.on('animationupdate', resync);
}

/** Top-left sprite position so world feet sit at `(worldFeetX, worldFeetY)` (accounts for `sprite.scale`). */
export function placeSpriteByFeet(
  sprite: Phaser.GameObjects.Sprite,
  feet: CharacterFeetLocal,
  worldFeetX: number,
  worldFeetY: number,
): void {
  sprite.setOrigin(0, 0);
  const sx = sprite.scaleX;
  const sy = sprite.scaleY;
  sprite.setPosition(worldFeetX - feet.x * sx, worldFeetY - feet.y * sy);
  sprite.setData(FEET_LOCAL_X, feet.x);
  sprite.setData(FEET_LOCAL_Y, feet.y);
}

export function getCharacterWorldFeet(sprite: Phaser.GameObjects.Sprite): { x: number; y: number } {
  const lx = sprite.getData(FEET_LOCAL_X) as number | undefined;
  const ly = sprite.getData(FEET_LOCAL_Y) as number | undefined;
  if (typeof lx !== 'number' || typeof ly !== 'number') {
    return { x: sprite.x, y: sprite.y };
  }
  return { x: sprite.x + lx * sprite.scaleX, y: sprite.y + ly * sprite.scaleY };
}

/** Camera `startFollow` offset so the follow target is the feet, not the sprite top-left. */
export function cameraFollowOffsetForFeet(feet: CharacterFeetLocal): { x: number; y: number } {
  return { x: -feet.x, y: -feet.y };
}
