import type * as Phaser from 'phaser';
import type { VerbInputProfile } from '../../types/game';
import type { PointerSlot } from './resolvePointerVerb';

/** Default press-and-hold delay ({@link VerbInputProfile.holdMs}). */
export const DEFAULT_HOLD_MS = 450;

/** A press that moves farther than this (screen px) before the delay is a drag, not a hold. */
const HOLD_MOVE_TOLERANCE = 14;

/**
 * Press-and-hold for touch screens (`inputProfile.holdVerb`). Call it at the top of a target's
 * pointer-down handler, after the click-to-skip and input-blocked checks. When the profile has a
 * hold slot, the pointer is a primary press and nothing is armed, it takes over and returns `true`:
 * the caller returns, and `run` is called later with the slot the press turned out to be —
 * `'primary'` when released before the delay (on pointer-up), `'hold'` when still down at the delay.
 * A press dragged away, or cancelled by the browser, runs nothing. Otherwise it returns `false` and
 * the caller resolves the press right away, as before.
 */
export function deferPressForHold(
  pointer: Phaser.Input.Pointer,
  profile: VerbInputProfile,
  armed: boolean,
  run: (slot: PointerSlot) => void,
): boolean {
  if (!profile.holdVerb || armed || !pointer.leftButtonDown()) {
    return false;
  }
  if (typeof window === 'undefined') {
    return false;
  }
  const delay = profile.holdMs ?? DEFAULT_HOLD_MS;
  const startX = pointer.event && 'clientX' in pointer.event ? pointer.event.clientX : null;
  const startY = pointer.event && 'clientY' in pointer.event ? pointer.event.clientY : null;
  let done = false;

  const finish = (slot: PointerSlot | null): void => {
    if (done) {
      return;
    }
    done = true;
    window.clearTimeout(timer);
    window.removeEventListener('pointerup', onUp, true);
    window.removeEventListener('pointercancel', onCancel, true);
    window.removeEventListener('pointermove', onMove, true);
    if (slot) {
      run(slot);
    }
  };
  const onUp = (): void => finish('primary');
  const onCancel = (): void => finish(null);
  const onMove = (e: PointerEvent): void => {
    if (startX === null || startY === null) {
      return;
    }
    if (Math.hypot(e.clientX - startX, e.clientY - startY) > HOLD_MOVE_TOLERANCE * (window.devicePixelRatio || 1)) {
      finish(null);
    }
  };
  const timer = window.setTimeout(() => finish('hold'), delay);
  window.addEventListener('pointerup', onUp, true);
  window.addEventListener('pointercancel', onCancel, true);
  window.addEventListener('pointermove', onMove, true);
  return true;
}
