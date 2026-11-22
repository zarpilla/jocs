import * as Phaser from 'phaser';
import { applyCharacterEffectiveAnimation, getCharacterAnimationOverrideTag } from '../benneAnimationRuntime.js';
import { computeSpeechLineDurationMs, getSpeechSettings } from '../ConfigManager.js';
import {
  playDirectionalAnimation,
  resolveInitialIdleFacing,
  type CharacterFacing,
} from '../directionalCharacterAnimation.js';
import { resolveGameStateManager } from '../gameState/resolveGameStateManager.js';
import type { RoomScene } from '../scenes/RoomScene.js';
import { tryGetBenneSoundManager } from '../sound/benneSoundRegistry.js';
import { isVoiceReady, waitForVoice } from '../sound/benneVoiceLoader.js';

/** Pause after a voiced line's recording ends, before the next line starts. */
const VOICE_TAIL_MS = 250;

/** Longest wait for a line's voice to download before the line goes on without it. */
export const VOICE_LOAD_WAIT_MS = 2500;

/** Per-line options for a scripted speech line. */
export interface ScriptedSayLineOptions {
  clickToSkip?: boolean;
}

export interface BenneSayVoiceMarkerParseResult {
  readonly text: string;
  readonly voiceNumber: string | null;
}

export function parseBenneSayVoiceMarker(line: string): BenneSayVoiceMarkerParseResult {
  const m = /^\|(\d+)\|\s*/.exec(line);
  if (!m) {
    return { text: line, voiceNumber: null };
  }
  return { text: line.slice(m[0].length), voiceNumber: m[1] ?? null };
}

export interface BenneSayRuntimeLine {
  readonly text: string;
  readonly voiceStem: string | null;
}

export function resolveBenneSayRuntimeLine(line: string, talkCharacterDefinitionId: string): BenneSayRuntimeLine {
  const parsed = parseBenneSayVoiceMarker(line);
  return {
    text: parsed.text,
    voiceStem: parsed.voiceNumber == null ? null : `${talkCharacterDefinitionId}${parsed.voiceNumber}`,
  };
}

function applySayLineDirectionalBase(
  scene: RoomScene,
  characterDefinitionId: string,
  baseName: 'Talk' | 'Idle',
): void {
  const sprite = scene.getCharacterSprite(characterDefinitionId);
  if (!sprite || !(sprite instanceof Phaser.GameObjects.Sprite) || !sprite.anims) {
    return;
  }
  if (getCharacterAnimationOverrideTag(sprite)) {
    if (baseName === 'Talk') {
      return;
    }
    applyCharacterEffectiveAnimation(sprite);
    return;
  }
  const facing: CharacterFacing =
    (sprite.getData('facing') as CharacterFacing | undefined) ?? resolveInitialIdleFacing(sprite);
  playDirectionalAnimation(sprite, baseName, facing);
}

/**
 * One scripted dialog line through completion (overlay + input suppression): BenneScript's `say`.
 */
export function playScriptedSayLine(
  scene: RoomScene,
  line: string,
  talkCharacterDefinitionId: string,
  options?: ScriptedSayLineOptions,
  voiceStem?: string | null,
): Promise<void> {
  // A skipped cutscene plays no lines: no overlay, no voice, no timer — the end state of a
  // say line is simply "line finished".
  if (scene.isCutsceneSkipFastForwarding()) {
    return Promise.resolve();
  }
  // Voices load on demand: if this one isn't here yet, wait for it (input stays off meanwhile), up to
  // VOICE_LOAD_WAIT_MS; after that the line goes on without it.
  if (voiceStem && !isVoiceReady(scene.game, voiceStem)) {
    scene.pushScriptedDialogInputSuppression();
    return waitForVoice(scene, voiceStem, VOICE_LOAD_WAIT_MS).then(() => {
      scene.popScriptedDialogInputSuppression();
      return playScriptedSayLineNow(scene, line, talkCharacterDefinitionId, options, voiceStem);
    });
  }
  return playScriptedSayLineNow(scene, line, talkCharacterDefinitionId, options, voiceStem);
}

function playScriptedSayLineNow(
  scene: RoomScene,
  line: string,
  talkCharacterDefinitionId: string,
  options?: ScriptedSayLineOptions,
  voiceStem?: string | null,
): Promise<void> {
  if (scene.isCutsceneSkipFastForwarding()) {
    return Promise.resolve();
  }
  const manager = resolveGameStateManager(scene.game);
  const speech = getSpeechSettings(manager);
  const voice = voiceStem ? tryGetBenneSoundManager(scene.game)?.playVoice(voiceStem) ?? null : null;
  const textMs = computeSpeechLineDurationMs(line, manager);
  // With a voice, the line lasts the whole recording (plus a short breath): `maxDurationMs` caps reading time, and
  // clamping a voice to it would cut the sentence off mid-word.
  const ms =
    voice?.durationMs == null
      ? textMs
      : Math.round(Math.max(speech.minDurationMs, voice.durationMs + VOICE_TAIL_MS));
  const lineOpt = options?.clickToSkip;
  const allowClickToSkip =
    lineOpt === true || (lineOpt !== false && speech.clickToSkip);

  return new Promise<void>((resolve) => {
    let completed = false;
    let timer: Phaser.Time.TimerEvent | null = null;
    let unregisterSkipFinisher: (() => void) | null = null;

    const finish = (): void => {
      if (completed) {
        return;
      }
      completed = true;
      unregisterSkipFinisher?.();
      unregisterSkipFinisher = null;
      voice?.stop();
      timer?.remove(false);
      timer = null;
      scene.clearScriptedDialogClickToSkip();
      applySayLineDirectionalBase(scene, talkCharacterDefinitionId, 'Idle');
      scene.setDialogTextOverlay({ visible: false });
      scene.popScriptedDialogInputSuppression();
      resolve();
    };

    scene.interruptCharacterWalkForScriptedSpeech(talkCharacterDefinitionId);
    scene.pushScriptedDialogInputSuppression();
    scene.setDialogTextOverlay({
      visible: true,
      text: line,
      talkCharacterDefinitionId,
    });
    applySayLineDirectionalBase(scene, talkCharacterDefinitionId, 'Talk');

    timer = scene.time.delayedCall(ms, finish);
    // ESC ends the line the same way its timer would, whatever the per-line click-to-skip setting.
    unregisterSkipFinisher = scene.registerCutsceneSkipFinisher(finish);

    if (allowClickToSkip) {
      scene.setScriptedDialogClickToSkip(() => {
        timer?.remove(false);
        timer = null;
        finish();
      });
    }
  });
}
