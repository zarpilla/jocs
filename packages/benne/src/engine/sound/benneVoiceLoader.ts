import * as Phaser from 'phaser';
import { getBenneAudioBootEntries } from '../content/resolveGameAssetUrl.js';
import { benneVoiceCacheKey } from './benneAudioCacheKeys.js';

/**
 * Voice files are not loaded at boot: a voiced game has hundreds of them, and most players hear only some.
 * A line loads its voice when it needs it ({@link waitForVoice}); scripts can ask for the next lines' voices
 * ahead of time (`game.preloadVoices`), so those lines don't wait.
 */

let voiceUrls: Map<string, string[]> | null = null;
const loading = new Map<string, Promise<boolean>>();

function bundledVoices(): Map<string, string[]> {
  voiceUrls ??= new Map(getBenneAudioBootEntries().voice.map((e) => [e.cacheKey, [...e.urls]]));
  return voiceUrls;
}

/** True when `assets/audio/voice/<id>.*` exists and is already decoded in the audio cache. */
export function isVoiceReady(game: Phaser.Game, id: string): boolean {
  return game.cache.audio.has(benneVoiceCacheKey(id));
}

/**
 * Loads `assets/audio/voice/<id>.*` through `scene`'s loader. Resolves `true` once it is in the audio cache, `false`
 * when there is no such file, audio is off, the download fails, or `scene` shuts down first. Concurrent calls for the
 * same voice share one download.
 */
export function loadVoice(scene: Phaser.Scene, id: string): Promise<boolean> {
  const key = benneVoiceCacheKey(id);
  if (scene.game.cache.audio.has(key)) {
    return Promise.resolve(true);
  }
  const urls = bundledVoices().get(key);
  if (!urls || scene.sound instanceof Phaser.Sound.NoAudioSoundManager) {
    return Promise.resolve(false);
  }
  const pending = loading.get(key);
  if (pending) {
    return pending;
  }
  const promise = new Promise<boolean>((resolve) => {
    const load = scene.load;
    const completeEvent = `${Phaser.Loader.Events.FILE_KEY_COMPLETE}audio-${key}`;
    let settled = false;
    const settle = (ok: boolean): void => {
      if (settled) {
        return;
      }
      settled = true;
      load.off(completeEvent, onComplete);
      load.off(Phaser.Loader.Events.FILE_LOAD_ERROR, onError);
      scene.events.off(Phaser.Scenes.Events.SHUTDOWN, onShutdown);
      loading.delete(key);
      resolve(ok && scene.game.cache.audio.has(key));
    };
    const onComplete = (): void => settle(true);
    const onError = (file: Phaser.Loader.File): void => {
      if (file.key === key) {
        settle(false);
      }
    };
    const onShutdown = (): void => settle(false);
    load.once(completeEvent, onComplete);
    load.on(Phaser.Loader.Events.FILE_LOAD_ERROR, onError);
    scene.events.once(Phaser.Scenes.Events.SHUTDOWN, onShutdown);
    load.audio(key, urls.length === 1 ? urls[0]! : urls);
    if (!load.isLoading()) {
      load.start();
    }
  });
  loading.set(key, promise);
  return promise;
}

/** {@link loadVoice}, but gives up (resolves `false`) after `maxMs`; the download goes on for the next time. */
export function waitForVoice(scene: Phaser.Scene, id: string, maxMs: number): Promise<boolean> {
  if (isVoiceReady(scene.game, id)) {
    return Promise.resolve(true);
  }
  return Promise.race([
    loadVoice(scene, id),
    new Promise<boolean>((resolve) => setTimeout(() => resolve(false), maxMs)),
  ]);
}
