/**
 * Character lights: the room's light falls on its characters at runtime.
 *
 * The room art is lit when it is drawn (in the content tools); the characters are separate sprites, so without
 * this they look the same everywhere. A room's {@link RoomCharacterLightsData} lists an ambient and point lights;
 * each frame the light is sampled at the four corners of every character sprite and set as a per-corner tint in
 * Phaser's **overlay** tint mode, where `0.5` grey is neutral: below it darkens, above it lightens, and a colour
 * colours. So one tint both dims a character in a dark corner and lights the side that faces a screen.
 *
 * When a room has character lights they replace the region tint (`tintEnabled` regions) for its characters.
 */
import * as Phaser from 'phaser';

import type { RoomCharacterLightsData, RoomCharacterLightData } from '../../types/room';

type Rgb = [number, number, number];

function parseHexRgb(hex: string | undefined, fallback: Rgb): Rgb {
  if (typeof hex !== 'string') {
    return fallback;
  }
  const m = /^#?([0-9a-f]{6})$/i.exec(hex.trim());
  if (!m) {
    return fallback;
  }
  const n = parseInt(m[1], 16);
  return [((n >> 16) & 255) / 255, ((n >> 8) & 255) / 255, (n & 255) / 255];
}

interface CompiledLight {
  x: number;
  y: number;
  radius: number;
  squash: number;
  power: number;
  rgb: Rgb;
  whenPropVisible?: string;
}

export interface CompiledCharacterLights {
  ambient: Rgb;
  lights: CompiledLight[];
  /** Fraction of the sprite height, from the top, that samples the light for the top corners. */
  topSample: number;
}

const cache = new WeakMap<RoomCharacterLightsData, CompiledCharacterLights>();

/** Parses (once per room data object) the room's character lights; `null` when the room has none. */
export function compileCharacterLights(data: RoomCharacterLightsData | undefined): CompiledCharacterLights | null {
  if (!data) {
    return null;
  }
  const hit = cache.get(data);
  if (hit) {
    return hit;
  }
  const lights = (data.lights ?? []).map((l: RoomCharacterLightData): CompiledLight => {
    const rgb = parseHexRgb(l.color, [1, 1, 1]);
    const k = typeof l.intensity === 'number' ? l.intensity : 1;
    return {
      x: l.x,
      y: l.y,
      radius: Math.max(1, l.radius),
      squash: l.squash ?? 1,
      power: l.power ?? 1.6,
      rgb: [rgb[0] * k, rgb[1] * k, rgb[2] * k],
      whenPropVisible: l.whenPropVisible,
    };
  });
  const out: CompiledCharacterLights = {
    ambient: parseHexRgb(data.ambient, [1, 1, 1]),
    lights,
    topSample: Math.max(0, Math.min(1, data.topSample ?? 0.15)),
  };
  cache.set(data, out);
  return out;
}

/** Light (`1` = unlit, per channel) at a room point. */
export function sampleCharacterLight(
  cl: CompiledCharacterLights,
  x: number,
  y: number,
  isPropVisible: (propId: string) => boolean,
): Rgb {
  const v: Rgb = [cl.ambient[0], cl.ambient[1], cl.ambient[2]];
  for (const l of cl.lights) {
    if (l.whenPropVisible && !isPropVisible(l.whenPropVisible)) {
      continue;
    }
    const d = Math.hypot(x - l.x, (y - l.y) * l.squash) / l.radius;
    if (d >= 1) {
      continue;
    }
    const f = Math.pow(1 - d, l.power);
    v[0] += l.rgb[0] * f;
    v[1] += l.rgb[1] * f;
    v[2] += l.rgb[2] * f;
  }
  return v;
}

/** Overlay tint for a light value: half of it (so `1`, unlit, is the neutral `0.5` grey), packed `0xRRGGBB`. */
function overlayTint(v: Rgb): number {
  const c = (n: number): number => Math.max(0, Math.min(255, Math.round(n * 0.5 * 255)));
  return (c(v[0]) << 16) | (c(v[1]) << 8) | c(v[2]);
}

/**
 * Lights a character sprite: samples the light at its left and right edges, near the head and at the feet, and
 * sets the four corner tints in overlay mode.
 */
export function applyCharacterLights(
  sprite: Phaser.GameObjects.Sprite | Phaser.GameObjects.Image,
  cl: CompiledCharacterLights,
  isPropVisible: (propId: string) => boolean,
): void {
  const b = sprite.getBounds();
  const top = b.top + b.height * cl.topSample;
  const bottom = b.bottom;
  const tl = overlayTint(sampleCharacterLight(cl, b.left, top, isPropVisible));
  const tr = overlayTint(sampleCharacterLight(cl, b.right, top, isPropVisible));
  const bl = overlayTint(sampleCharacterLight(cl, b.left, bottom, isPropVisible));
  const br = overlayTint(sampleCharacterLight(cl, b.right, bottom, isPropVisible));
  // a flipped sprite swaps its corners: the tint is in room space, so swap them back
  if (sprite.flipX) {
    sprite.setTint(tr, tl, br, bl);
  } else {
    sprite.setTint(tl, tr, bl, br);
  }
  sprite.setTintMode(Phaser.TintModes.OVERLAY);
}
