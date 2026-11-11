import { activeRoomScene } from './actions.js';
import { getRoomShade, setRoomShadeState } from '../scenes/roomShade.js';

export interface ShadeOptions {
  /** Tint colour (`0x0a1020`). Defaults to the current one (black at first). */
  color?: number;
  /** Seconds to get there; `0` (the default) is instant. */
  seconds?: number;
}

/**
 * The room shade: a tint over the room and its characters, below the HUD and the speech. It stays from room
 * to room until it is changed. Doesn't wait.
 *
 * ```ts
 * shade.set(0.6, { color: 0x05080f, seconds: 1.5 }) // the lights go out
 * shade.set(0, { seconds: 1.5 })                     // and come back
 * ```
 */
export const shade = {
  set(alpha: number, options: ShadeOptions = {}): void {
    setRoomShadeState({ alpha, color: options.color ?? getRoomShade().color });
    activeRoomScene()?.applyRoomShade(options.seconds ?? 0);
  },

  /** The current shade (0: none). */
  get alpha(): number {
    return getRoomShade().alpha;
  },
};
