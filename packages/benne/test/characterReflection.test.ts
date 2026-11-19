import { describe, expect, it, vi } from 'vitest';

vi.mock('phaser', () => ({ GameObjects: { Events: { DESTROY: 'destroy' } } }));
vi.mock('../src/engine/characterFeet', () => ({
  // the feet: 100 frame px below the top of a sprite with its origin at the top
  getCharacterWorldFeet: (s: { x: number; y: number; scaleY: number }) => ({ x: s.x, y: s.y + 100 * s.scaleY }),
}));

const { compileCharacterReflection, CharacterReflectionLayer } = await import('../src/engine/room/characterReflection');

/** A stand-in for a Phaser Image that records what the layer sets. */
function fakeImage() {
  const img: Record<string, unknown> = { texture: { key: 'vet' }, frame: { name: '0' } };
  const set = (k: string) => (...v: unknown[]) => {
    img[k] = v.length === 1 ? v[0] : v;
    return img;
  };
  for (const k of ['setVisible', 'setDepth', 'setFlipX', 'setDisplayOrigin', 'setScale', 'setPosition', 'setCrop',
    'setTintMode', 'setTint', 'setAlpha']) {
    img[k] = set(k);
  }
  img.setTexture = (key: string, frame: string) => {
    img.texture = { key };
    img.frame = { name: frame };
    return img;
  };
  img.destroy = vi.fn();
  return img;
}

function fakeSprite(over: Record<string, unknown> = {}) {
  return {
    active: true, visible: true, alpha: 1, x: 200, y: 100, scaleX: 1, scaleY: 1, flipX: false,
    displayOriginX: 32, displayOriginY: 0, texture: { key: 'vet' }, frame: { name: '3', width: 64, height: 116 },
    tintMode: 0, tintTopLeft: 1, tintTopRight: 2, tintBottomLeft: 3, tintBottomRight: 4,
    getData: () => undefined, once: vi.fn(), ...over,
  };
}

function layerWith(img: ReturnType<typeof fakeImage>) {
  const scene = { add: { image: () => img } };
  return new CharacterReflectionLayer(scene as never);
}

describe('floor reflection', () => {
  it('is off without room data or with enabled: false, and fills in defaults', () => {
    expect(compileCharacterReflection(undefined)).toBeNull();
    expect(compileCharacterReflection({ enabled: false })).toBeNull();
    expect(compileCharacterReflection({})).toEqual({ alpha: 0.2, fade: 0, length: 1, maxY: null });
  });

  it('mirrors the frame about the feet, faint next to them and fading away', () => {
    const img = fakeImage();
    const r = compileCharacterReflection({ alpha: 0.5, fade: 0.1, length: 0.9 })!;
    layerWith(img).update(r, [fakeSprite() as never], 100.5);
    expect(img.setDepth).toBe(100.5);
    expect(img.frame).toEqual({ name: '3' });
    expect(img.setDisplayOrigin).toEqual([32, 100]);
    expect(img.setPosition).toEqual([200, 200]);
    expect(img.setScale).toEqual([1, -0.9]);
    // only the rows above the feet are mirrored
    expect(img.setCrop).toEqual([0, 0, 64, 100]);
    expect(img.setTint).toEqual([1, 2, 3, 4]);
    expect(img.setAlpha).toEqual([0.05, 0.05, 0.5, 0.5]);
  });

  it('is cut where the polished floor ends', () => {
    const img = fakeImage();
    const r = compileCharacterReflection({ maxY: 240 })!;
    layerWith(img).update(r, [fakeSprite() as never], 100.5);
    // 40 room px below the feet at scale 1: the 40 frame rows next to the feet
    expect(img.setCrop).toEqual([0, 60, 64, 40]);
  });

  it('none for a character with reflection: false', () => {
    const img = fakeImage();
    const r = compileCharacterReflection({})!;
    const created = vi.fn(() => img);
    const layer = new CharacterReflectionLayer({ add: { image: created } } as never);
    layer.update(r, [fakeSprite({ getData: () => ({ reflection: false }) }) as never], 100.5);
    expect(created).not.toHaveBeenCalled();
  });
});
