import { describe, expect, it, vi } from 'vitest';

vi.mock('phaser', () => ({}));

const { compileCharacterShadow, characterShadowBaseWidth, shadowEllipse } = await import(
  '../src/engine/room/characterShadow'
);

function bounds(points: { x: number; y: number }[]) {
  const xs = points.map((p) => p.x);
  const ys = points.map((p) => p.y);
  return { x0: Math.min(...xs), x1: Math.max(...xs), y0: Math.min(...ys), y1: Math.max(...ys) };
}

describe('contact shadow', () => {
  it('is off without room data or with enabled: false', () => {
    expect(compileCharacterShadow(undefined)).toBeNull();
    expect(compileCharacterShadow({ enabled: false })).toBeNull();
  });

  it('without a light is a flat ellipse centred on the feet', () => {
    const s = compileCharacterShadow({ squash: 0.25 })!;
    const e = shadowEllipse(s, 100, 200, 20);
    expect(e.cx).toBeCloseTo(100);
    expect(e.cy).toBeCloseTo(200);
    const b = bounds(e.points);
    expect(b.x1 - b.x0).toBeCloseTo(40, 0);
    expect(b.y1 - b.y0).toBeCloseTo(10, 0);
  });

  it('stretches away from a lamp on the left and keeps its near end under the feet', () => {
    const s = compileCharacterShadow({ light: { x: 0, y: 200, stretch: 1, reach: 50 } })!;
    const e = shadowEllipse(s, 100, 200, 20);
    const b = bounds(e.points);
    expect(e.cx).toBeGreaterThan(100); // falls to the right
    expect(b.x0).toBeCloseTo(80, 0); // near end: feet − rx
    expect(b.x1).toBeCloseTo(160, 0); // far end: twice as long
  });

  it('is round right under the light', () => {
    const s = compileCharacterShadow({ light: { x: 100, y: 200, stretch: 1 } })!;
    const e = shadowEllipse(s, 100, 200, 20);
    expect(e.cx).toBeCloseTo(100);
  });

  it('follows a sun direction regardless of position', () => {
    const s = compileCharacterShadow({ squash: 0.5, light: { x: 0, y: 1, direction: true, stretch: 1 } })!;
    const e = shadowEllipse(s, 100, 200, 20);
    expect(e.cx).toBeCloseTo(100);
    expect(e.cy).toBeCloseTo(210); // 20 px further on the floor, squashed by 0.5
  });

  it('takes its width from the character, then the collider, then the frame', () => {
    expect(characterShadowBaseWidth({ shadow: { width: 30 } } as never, 60)).toBe(30);
    const collider = { points: [{ x: 18, y: 0 }, { x: 42, y: 0 }, { x: 30, y: 100 }] };
    expect(characterShadowBaseWidth({ collider } as never, 60)).toBeCloseTo(24 * 0.85);
    expect(characterShadowBaseWidth({ artScale: 2 } as never, 120)).toBeCloseTo(24);
  });
});
