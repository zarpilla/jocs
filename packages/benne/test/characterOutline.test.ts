import { describe, expect, it, vi } from 'vitest';

vi.mock('phaser', () => ({ GameObjects: { Events: { DESTROY: 'destroy' } }, TintModes: { FILL: 2 } }));
vi.mock('../src/engine/rendering/benneCharacterPerspectiveBatch', () => ({
  attachBenneCharacterPerspectiveRenderNodes: vi.fn(),
}));

const { compileCharacterOutline, CharacterOutlineLayer, OUTLINE_OFFSETS } = await import(
  '../src/engine/room/characterOutline'
);

/** A stand-in for a Phaser Image that records what the layer sets. */
function fakeImage() {
  const img: Record<string, unknown> = { texture: { key: 'vet' }, frame: { name: '0' }, data: {} };
  const set = (k: string) => (...v: unknown[]) => {
    img[k] = v.length === 1 ? v[0] : v;
    return img;
  };
  for (const k of ['setVisible', 'setDepth', 'setFlipX', 'setDisplayOrigin', 'setScale', 'setPosition', 'setTintMode',
    'setTint', 'setAlpha']) {
    img[k] = set(k);
  }
  img.setData = (k: string, v: unknown) => {
    (img.data as Record<string, unknown>)[k] = v;
    return img;
  };
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
    active: true, visible: true, alpha: 1, x: 200, y: 100, depth: 7, scaleX: 0.8, scaleY: 0.8, flipX: true,
    displayOriginX: 32, displayOriginY: 116, texture: { key: 'vet' }, frame: { name: '3' },
    getData: () => ({ id: 'vet' }), once: vi.fn(), ...over,
  };
}

function layer() {
  const made: ReturnType<typeof fakeImage>[] = [];
  const scene = { add: { image: () => { const i = fakeImage(); made.push(i); return i; } } };
  return { layer: new CharacterOutlineLayer(scene as never), made };
}

describe('character outline', () => {
  it('is off without room data or with enabled: false, and fills in defaults', () => {
    expect(compileCharacterOutline(undefined)).toBeNull();
    expect(compileCharacterOutline({ enabled: false })).toBeNull();
    expect(compileCharacterOutline({})).toEqual({ color: 0, alpha: 0.7, width: 1 });
    expect(compileCharacterOutline({ color: '#1a1020', alpha: 2, width: 2 })).toEqual({ color: 0x1a1020, alpha: 1,
      width: 2 });
  });

  it('puts four filled copies of the current frame around the character, just under it', () => {
    const { layer: l, made } = layer();
    const sprite = fakeSprite();
    l.update(compileCharacterOutline({ color: '#102030', alpha: 0.5, width: 2 }), [sprite as never]);
    expect(made).toHaveLength(OUTLINE_OFFSETS.length);
    const pos = made.map((m) => m.setPosition);
    expect(pos).toEqual([[198, 100], [202, 100], [200, 98], [200, 102]]);
    for (const m of made) {
      expect(m.frame).toEqual({ name: '3' });
      expect(m.setDepth).toBeCloseTo(6.75);
      expect(m.setScale).toEqual([0.8, 0.8]);
      expect(m.setFlipX).toBe(true);
      expect(m.setDisplayOrigin).toEqual([32, 116]);
      expect(m.setTintMode).toBe(2);
      expect(m.setTint).toBe(0x102030);
      expect(m.setAlpha).toBe(0.5);
      expect((m.data as Record<string, unknown>).character).toEqual({ id: 'vet' });
    }
  });

  it('hides with the character, and drops the copies when the room has none or the character opts out', () => {
    const { layer: l, made } = layer();
    const sprite = fakeSprite({ visible: false });
    const o = compileCharacterOutline({});
    l.update(o, [sprite as never]);
    expect(made.every((m) => m.setVisible === false)).toBe(true);
    l.update(null, [sprite as never]);
    expect(made.every((m) => (m.destroy as ReturnType<typeof vi.fn>).mock.calls.length === 1)).toBe(true);
    const { layer: l2, made: made2 } = layer();
    l2.update(o, [fakeSprite({ getData: () => ({ outline: false }) }) as never]);
    expect(made2).toHaveLength(0);
  });
});
