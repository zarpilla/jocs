/**
 * Room shade: a full-screen tint drawn above the room art and its characters, and below every GUI (so the HUD,
 * the inventory and Speaking Text stay as they are). For a room without light (a power cut, the night).
 *
 * The shade belongs to the game, not to one room: it is kept here and every new {@link RoomScene} starts with it.
 * Bennescript `shade.set()` changes it.
 */
import { ROOM_VIDEO_LAYER_DEPTH } from './roomVideoConstants';

/** Above the room stack and the dev debug overlays (`20_000`), below the video layer and every GUI. */
export const ROOM_SHADE_LAYER_DEPTH = ROOM_VIDEO_LAYER_DEPTH - 10;

export interface RoomShadeState {
  /** 0 (no shade) to 1 (the room is not seen). */
  alpha: number;
  color: number;
}

let current: RoomShadeState = { alpha: 0, color: 0x000000 };

export function getRoomShade(): RoomShadeState {
  return current;
}

export function setRoomShadeState(state: RoomShadeState): void {
  current = { alpha: Math.max(0, Math.min(1, state.alpha)), color: state.color };
}
