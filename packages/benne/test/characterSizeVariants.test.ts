import { describe, expect, it, vi } from 'vitest';

vi.mock('phaser', () => ({}));

const {
  applyCharacterSizeVariant,
  characterSizeVariantScale,
  characterSpriteArtScale,
  frameSizeVariantScale,
  getCharacterWorldFeet,
  getPlacedPlainFeetLocal,
  keepFeetAcrossSizeVariants,
  registerCharacterSizeVariantFrames,
} = await import('../src/engine/characterFeet');

type Data = Record<string, unknown>;

/** Just enough of a Phaser sprite: data, scale, position, the frame shown and animation listeners. */
function fakeSprite(textureKey: string, frame: string, character: Data) {
  const data: Data = { character };
  const listeners = new Map<string, (() => void)[]>();
  const sprite = {
    texture: { key: textureKey },
    frame: { name: frame, width: 37, height: 64 },
    scaleX: 1,
    scaleY: 1,
    x: 0,
    y: 0,
    getData: (k: string) => data[k],
    setData: (k: string, v: unknown) => {
      data[k] = v;
      return sprite;
    },
    setScale(sx: number, sy: number) {
      sprite.scaleX = sx;
      sprite.scaleY = sy;
    },
    setOrigin() {},
    setPosition(x: number, y: number) {
      sprite.x = x;
      sprite.y = y;
    },
    on(ev: string, fn: () => void) {
      listeners.set(ev, [...(listeners.get(ev) ?? []), fn]);
    },
    /** Shows another frame, as an animation would, and fires its event. */
    show(name: string, width: number, height: number, ev = 'animationstart') {
      sprite.frame = { name, width, height };
      for (const fn of listeners.get(ev) ?? []) fn();
    },
  };
  return sprite;
}

const VET = { id: 'vet', feet: { x: 18, y: 60 }, sizeVariants: { Gran: 1.5, Lluny: 0.5, LlunyGala: 0.6 } };
const ANIMS = [
  { key: 'IdleD', frames: [{ textureFrame: '0' }, { textureFrame: '1' }] },
  { key: 'GranIdleD', frames: [{ textureFrame: '2' }, { textureFrame: '3' }] },
  { key: 'LlunyIdleD', frames: [{ textureFrame: '4' }] },
];

describe('character size variants', () => {
  it('picks the scale by the longest tag prefix', () => {
    expect(characterSizeVariantScale(VET, 'IdleD')).toBe(1);
    expect(characterSizeVariantScale(VET, 'GranWalkL')).toBe(1.5);
    expect(characterSizeVariantScale(VET, 'LlunyWalkL')).toBe(0.5);
    expect(characterSizeVariantScale(VET, 'LlunyGalaWalkL')).toBe(0.6);
    expect(characterSizeVariantScale({}, 'GranWalkL')).toBe(1);
    expect(characterSizeVariantScale(undefined, 'GranWalkL')).toBe(1);
  });

  it('knows the variant of each frame of a registered sheet', () => {
    registerCharacterSizeVariantFrames('vet', VET as never, ANIMS);
    expect(frameSizeVariantScale({ texture: { key: 'vet' }, frame: { name: '1' } })).toBe(1);
    expect(frameSizeVariantScale({ texture: { key: 'vet' }, frame: { name: '3' } })).toBe(1.5);
    expect(frameSizeVariantScale({ texture: { key: 'vet' }, frame: { name: '4' } })).toBe(0.5);
    expect(frameSizeVariantScale({ texture: { key: 'other' }, frame: { name: '3' } })).toBe(1);
    const art2 = { ...VET, artScale: 2 };
    expect(
      characterSpriteArtScale({ texture: { key: 'vet' }, frame: { name: '3' }, getData: () => art2 }),
    ).toBeCloseTo(3);
  });

  it('a sheet without variants records nothing (everything stays at 1)', () => {
    registerCharacterSizeVariantFrames('iri', { id: 'iri' } as never, ANIMS);
    expect(frameSizeVariantScale({ texture: { key: 'iri' }, frame: { name: '3' } })).toBe(1);
  });

  it('shows a variant frame at perspective / variant, with the feet and the 1× layout where the plain sheet has them', () => {
    registerCharacterSizeVariantFrames('vet', VET as never, ANIMS);
    const plain = fakeSprite('vet', '0', VET);
    applyCharacterSizeVariant(plain as never, { x: 18, y: 60 }, 1.8, 300, 200);
    const big = fakeSprite('vet', '2', VET);
    big.frame = { name: '2', width: 56, height: 96 };
    applyCharacterSizeVariant(big as never, { x: 18, y: 60 }, 1.8, 300, 200);
    expect(big.scaleX).toBeCloseTo(1.2);
    // same feet, same top-left corner, same on-screen size: collider / talkPoint (sprite.x + offset) land the same
    expect(getCharacterWorldFeet(big as never)).toEqual(getCharacterWorldFeet(plain as never));
    expect(big.x).toBeCloseTo(plain.x);
    expect(big.y).toBeCloseTo(plain.y);
    expect(getPlacedPlainFeetLocal(big as never)).toEqual({ x: 18, y: 60 });
  });

  it('switching variant on the spot keeps the feet and the size', () => {
    registerCharacterSizeVariantFrames('vet', VET as never, ANIMS);
    const s = fakeSprite('vet', '0', VET);
    keepFeetAcrossSizeVariants(s as never);
    applyCharacterSizeVariant(s as never, { x: 18, y: 60 }, 1.8, 300, 200);
    const before = { ...getCharacterWorldFeet(s as never) };
    s.show('2', 56, 96);
    expect(s.scaleX).toBeCloseTo(1.2);
    expect(getCharacterWorldFeet(s as never).x).toBeCloseTo(before.x);
    expect(getCharacterWorldFeet(s as never).y).toBeCloseTo(before.y);
    s.show('4', 19, 32, 'animationupdate');
    expect(s.scaleX).toBeCloseTo(3.6);
    expect(getCharacterWorldFeet(s as never).y).toBeCloseTo(before.y);
    s.show('1', 37, 64);
    expect(s.scaleX).toBeCloseTo(1.8);
    expect(getPlacedPlainFeetLocal(s as never)).toEqual({ x: 18, y: 60 });
  });
});
