import * as Phaser from 'phaser';
import { adaptiveHeightFor, applyAdaptiveResolution, getGameSettings } from './ConfigManager.js';
import { tryGetActiveGameStateManager } from './gameState/resolveGameStateManager.js';
import { isGameplayInteractionRunning } from './interaction/interactionActivity.js';
import { getActiveDialogSession } from './dialog/dialogSession.js';
import { isRoomTransitionInProgress, tryGetRoomTransitionOrchestrator } from './scenes/roomTransitionGlobals.js';
import { SCENE_ROOM } from './content/constants.js';
import type { RoomScene } from './scenes/RoomScene.js';

/** How long the window must stay the same size before the height is chosen again. */
const SETTLE_MS = 300;

/**
 * Adaptive height (`resolution.minHeight`) after boot: when the window changes shape (a resize, full screen, a phone
 * turned), the height is chosen again and the room is rebuilt for it, the way a loaded game enters its room: the game
 * state goes out to JSON and back in (no save slot is touched), so GUIs, anchors and the camera are all laid out anew.
 * It waits for a quiet moment: no interaction, dialog, cutscene, room transition or modal GUI (a menu) under way.
 */
export function wireAdaptiveResolutionResize(game: Phaser.Game): void {
  if (getGameSettings().resolution.minHeight === undefined || typeof window === 'undefined') {
    return;
  }
  let timer = 0;
  let pending = false;
  const onResize = (): void => {
    window.clearTimeout(timer);
    timer = window.setTimeout(() => {
      const next = adaptiveHeightFor(window.innerWidth, window.innerHeight);
      pending = next !== null && next !== getGameSettings().resolution.height;
    }, SETTLE_MS);
  };
  const onStep = (): void => {
    if (!pending) {
      return;
    }
    const room = game.scene.getScene(SCENE_ROOM) as RoomScene | null;
    const manager = tryGetActiveGameStateManager();
    const orchestrator = tryGetRoomTransitionOrchestrator();
    if (
      !room?.sys.isActive() ||
      !manager ||
      !orchestrator ||
      isGameplayInteractionRunning() ||
      getActiveDialogSession() != null ||
      isRoomTransitionInProgress(game) ||
      !room.isQuietForRebuild()
    ) {
      return;
    }
    pending = false;
    const snapshot = manager.exportSnapshotJson();
    applyAdaptiveResolution(window.innerWidth, window.innerHeight);
    if (manager.importSnapshotJson(snapshot)) {
      void orchestrator.transitionToLoadedRoom(true);
    }
  };
  window.addEventListener('resize', onResize);
  document.addEventListener('fullscreenchange', onResize);
  game.events.on(Phaser.Core.Events.POST_STEP, onStep);
  game.events.once(Phaser.Core.Events.DESTROY, () => {
    window.clearTimeout(timer);
    window.removeEventListener('resize', onResize);
    document.removeEventListener('fullscreenchange', onResize);
    game.events.off(Phaser.Core.Events.POST_STEP, onStep);
  });
}
