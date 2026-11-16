/**
 * Frees the sheets of the rooms that are not on screen.
 *
 * A room's sheet (`images/rooms/<id>/<id>.png`, with `artScale: 2` up to 4096 px a side) is loaded when the room is
 * entered and, without this, stays in GPU memory for the rest of the session: on a phone, after half the game, that
 * is enough to lose the WebGL context. When a room is created, the sheets of every other room are released: the
 * texture, the Aseprite JSON in the loader cache (or the loader would skip it next time, as a duplicate key), and the
 * room's animation clips (the ones whose frames are on that texture). Entering a room again loads it again
 * ({@link import('../scenes/roomSceneBootstrap').queueRoomSceneAssetLoads} checks `textures.exists`).
 */
import type * as Phaser from 'phaser';

import { getRoomAsepriteTextureKey } from '../content/roomAseprite';
import { isRoomSheetPageTextureKey } from './roomSheetPages';

const SHEET_PREFIX = getRoomAsepriteTextureKey('');

export function releaseOtherRoomSheets(scene: Phaser.Scene, keepRoomId: string): string[] {
  const keep = getRoomAsepriteTextureKey(keepRoomId);
  const released: string[] = [];
  for (const key of scene.textures.getTextureKeys()) {
    if (isRoomSheetPageTextureKey(key)) {
      scene.textures.remove(key); // a page of a sheet that was never put together (room/roomSheetPages.ts)
      continue;
    }
    if (!key.startsWith(SHEET_PREFIX) || key === keep) {
      continue;
    }
    const roomId = key.slice(SHEET_PREFIX.length);
    for (const animKey of scene.anims.getAnimsFromTexture(key)) {
      scene.anims.remove(animKey);
    }
    if (scene.cache.json.exists(key)) {
      scene.cache.json.remove(key);
    }
    scene.textures.remove(key);
    released.push(roomId);
  }
  return released;
}
