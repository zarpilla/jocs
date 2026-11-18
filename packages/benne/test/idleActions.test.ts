import { describe, expect, it, vi } from 'vitest';

vi.mock('phaser', () => ({}));
vi.mock('../src/engine/benneAnimationRuntime', () => ({ BENNE_CHARACTER_ANIMATION_OVERRIDE_KEY: 'benneAnimationOverride' }));

const { CharacterIdleActions, IDLE_ACTION_DATA_KEY, idleActionTag } = await import('../src/engine/idleActions');

type Tags = Record<string, number>;

function fakeSprite(tags: Tags, character: unknown, start = 'IdleD') {
  const data = new Map<string, unknown>([
    ['character', character],
    ['facingBase', 'Idle'],
  ]);
  const s = {
    active: true,
    visible: true,
    progress: -1,
    anims: {
      currentAnim: null as { key: string; frames: unknown[] } | null,
      isPlaying: false,
      timeScale: 1,
      accumulator: 0,
      nextTick: 800,
      exists: (k: string) => k in tags,
      setProgress: (v: number) => {
        s.progress = v;
      },
    },
    play(k: string) {
      s.anims.currentAnim = { key: k, frames: new Array(tags[k]).fill(0) };
      s.anims.isPlaying = true;
    },
    getData: (k: string) => data.get(k),
    setData: (k: string, v: unknown) => data.set(k, v),
  };
  s.play(start);
  return s;
}

describe('idle actions', () => {
  it('maps the idle tag to the action, keeping prefix and facing', () => {
    expect(idleActionTag('IdleDL', 'Blink')).toBe('BlinkDL');
    expect(idleActionTag('LlunyGalaIdleD', 'Look')).toBe('LlunyGalaLookD');
    expect(idleActionTag('WalkD', 'Blink')).toBeNull();
  });

  it('plays an action after its time, then goes back to the idle loop', () => {
    const s = fakeSprite({ IdleD: 2, BlinkD: 1 }, { idleActions: [{ animation: 'Blink', every: [2, 2] }] });
    const ia = new CharacterIdleActions(() => 0.5);
    ia.update([s], 0);
    expect(s.progress).toBe(0.5); // breathing desynced: frame...
    expect(s.anims.accumulator).toBe(400); // ...and time within it
    ia.update([s], 1999);
    expect(s.anims.currentAnim!.key).toBe('IdleD');
    ia.update([s], 2000);
    expect(s.anims.currentAnim!.key).toBe('BlinkD');
    expect(s.getData(IDLE_ACTION_DATA_KEY)).toBe('BlinkD');
    s.anims.isPlaying = false; // one-shot finished
    ia.update([s], 2150);
    expect(s.anims.currentAnim!.key).toBe('IdleD');
    expect(s.getData(IDLE_ACTION_DATA_KEY)).toBeNull();
    // Still counts as rest: next blink two seconds after the last one, not after the return.
    ia.update([s], 4000);
    expect(s.anims.currentAnim!.key).toBe('BlinkD');
  });

  it('waits `after` more seconds of stillness, and a walk resets it', () => {
    const s = fakeSprite({ IdleD: 1, LookD: 4, WalkD: 6 }, { idleActions: [{ animation: 'Look', every: [1, 1], after: 8 }] });
    const ia = new CharacterIdleActions(() => 0);
    ia.update([s], 0);
    ia.update([s], 5000);
    s.play('WalkD');
    s.setData('facingBase', 'Walk');
    ia.update([s], 6000);
    s.play('IdleD');
    s.setData('facingBase', 'Idle');
    ia.update([s], 7000);
    ia.update([s], 15999);
    expect(s.anims.currentAnim!.key).toBe('IdleD');
    expect(s.anims.timeScale).not.toBe(1); // its own breathing pace while idle
    ia.update([s], 16000);
    expect(s.anims.currentAnim!.key).toBe('LookD');
    s.play('WalkD');
    s.setData('facingBase', 'Walk');
    ia.update([s], 16100);
    expect(s.anims.timeScale).toBe(1); // walking at normal speed
  });

  it('skips actions the sheet lacks for the current outfit, and lets a walk cut one', () => {
    const s = fakeSprite({ GalaIdleD: 1, BlinkD: 1, WalkD: 6 }, { idleActions: [{ animation: 'Blink', every: [1, 1] }] }, 'GalaIdleD');
    const ia = new CharacterIdleActions(() => 0);
    ia.update([s], 0);
    ia.update([s], 1000);
    expect(s.anims.currentAnim!.key).toBe('GalaIdleD'); // no GalaBlinkD: no plain BlinkD either

    const t = fakeSprite({ IdleD: 1, BlinkD: 1, WalkD: 6 }, { idleActions: [{ animation: 'Blink', every: [1, 1] }] });
    ia.update([t], 0);
    ia.update([t], 1000);
    expect(t.anims.currentAnim!.key).toBe('BlinkD');
    t.play('WalkD');
    t.setData('facingBase', 'Walk');
    ia.update([t], 1050);
    expect(t.anims.currentAnim!.key).toBe('WalkD');
    expect(t.getData(IDLE_ACTION_DATA_KEY)).toBeNull();
  });

  it('never starts two characters\' actions together', () => {
    const cfg = { idleActions: [{ animation: 'Blink', every: [2, 2] }] };
    const a = fakeSprite({ IdleD: 1, BlinkD: 1 }, cfg);
    const b = fakeSprite({ IdleD: 1, BlinkD: 1 }, cfg);
    const ia = new CharacterIdleActions(() => 0.5);
    ia.update([a, b], 0);
    ia.update([a, b], 2000);
    expect(a.anims.currentAnim!.key).toBe('BlinkD');
    expect(b.anims.currentAnim!.key).toBe('IdleD'); // waits
    ia.update([a, b], 3499);
    expect(b.anims.currentAnim!.key).toBe('IdleD');
    ia.update([a, b], 4500); // 2000 + 1500 + 0.5 × 2000
    expect(b.anims.currentAnim!.key).toBe('BlinkD');
  });

  it('gives each character its own breathing phase and pace', () => {
    let k = 0;
    const seq = [0.1, 0.9, 0.3, 0.7, 0.2, 0.8];
    const ia = new CharacterIdleActions(() => seq[k++ % seq.length]!);
    const a = fakeSprite({ IdleD: 2 }, {});
    const b = fakeSprite({ IdleD: 2 }, {});
    ia.update([a, b], 0);
    expect(a.anims.timeScale).not.toBe(b.anims.timeScale);
    expect([a.progress, a.anims.accumulator]).not.toEqual([b.progress, b.anims.accumulator]);
  });

  it('does nothing while a script animation override is set', () => {
    const s = fakeSprite({ IdleD: 1, BlinkD: 1 }, { idleActions: [{ animation: 'Blink', every: [1, 1] }] });
    s.setData('benneAnimationOverride', 'IdleD');
    const ia = new CharacterIdleActions(() => 0);
    ia.update([s], 0);
    ia.update([s], 5000);
    expect(s.anims.currentAnim!.key).toBe('IdleD');
  });
});
