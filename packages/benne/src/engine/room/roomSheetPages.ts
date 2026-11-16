/**
 * A room sheet in several pages.
 *
 * A room sheet that does not fit in one 4096×4096 image (the safe maximum on phones), typically with `artScale: 2`
 * and many animations, comes as pages: `images/rooms/<id>/<id>.png`, `<id>-2.png`... The Aseprite JSON lists them in
 * `meta.pages`, and each frame says its page (`"page": n`, 0 = the first; the frame rectangle is in that page).
 *
 * Each page is loaded as a plain image, and when the room is created they are put together as **one** texture with
 * several sources (Phaser's multi-source atlas), under the usual room sheet key. Everything else (frame names,
 * Aseprite animation clips, release when leaving the room) works as with a single page.
 */
import type * as Phaser from 'phaser';

import { getNormalizedRoomAsepriteAtlasData } from '../content/loadAsepriteAtlasData';
import { resolveGameAssetUrl } from '../content/resolveGameAssetUrl';
import { getRoomAsepriteTextureKey } from '../content/roomAseprite';

const PAGE_PREFIX = 'roomSheetPage:';

/** Texture key of one page while it loads (removed once the pages are put together). */
export function roomSheetPageTextureKey(roomId: string, page: number): string {
  return `${PAGE_PREFIX}${roomId}:${page}`;
}

export function isRoomSheetPageTextureKey(key: string): boolean {
  return key.startsWith(PAGE_PREFIX);
}

/** Page image paths (under `assets/`), or `null` for a sheet in one image. */
export function getRoomSheetPagePaths(roomId: string): string[] | null {
  const data = getNormalizedRoomAsepriteAtlasData(roomId);
  const pages = (data.meta as { pages?: unknown } | undefined)?.pages;
  if (!Array.isArray(pages) || pages.length < 2) {
    return null;
  }
  return pages.map((file) => `images/rooms/${roomId}/${String(file)}`);
}

/** Queues the page images of a multi-page room sheet. */
export function queueRoomSheetPages(load: Phaser.Loader.LoaderPlugin, roomId: string, paths: string[]): void {
  paths.forEach((p, n) => {
    load.image(roomSheetPageTextureKey(roomId, n), resolveGameAssetUrl(p));
  });
}

type FrameEntry = Record<string, unknown> & { page?: number };

/**
 * When the room sheet comes in pages and they are loaded, builds the room sheet texture from them (and the Aseprite
 * JSON in the loader cache, for `createFromAseprite`). No-op for a single-page sheet or one already built.
 */
export function assembleRoomSheetPages(scene: Phaser.Scene, roomId: string): void {
  const key = getRoomAsepriteTextureKey(roomId);
  const paths = getRoomSheetPagePaths(roomId);
  if (!paths || scene.textures.exists(key)) {
    return;
  }
  const pageKeys = paths.map((_, n) => roomSheetPageTextureKey(roomId, n));
  if (!pageKeys.every((k) => scene.textures.exists(k))) {
    console.warn(`[Benne] Room "${roomId}": the pages of its sheet are not loaded.`);
    return;
  }
  const data = getNormalizedRoomAsepriteAtlasData(roomId);
  const frames = data.frames as Record<string, FrameEntry>;
  const perPage: Record<string, FrameEntry>[] = paths.map(() => ({}));
  for (const [name, f] of Object.entries(frames)) {
    const { page, ...frame } = f;
    perPage[typeof page === 'number' ? page : 0][name] = frame;
  }
  const sources = pageKeys.map((k) => scene.textures.get(k).getSourceImage() as HTMLImageElement);
  scene.textures.addAtlasJSONHash(
    key,
    sources,
    perPage.map((fr) => ({ frames: fr })),
  );
  scene.cache.json.add(key, data);
  for (const k of pageKeys) {
    scene.textures.remove(k);
  }
}
