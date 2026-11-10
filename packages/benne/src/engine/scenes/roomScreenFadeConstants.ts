/** Default full-screen fade duration when the duration argument is omitted (BenneScript `fadeOut()` / `fadeIn()`). */
export const BENNE_SCREEN_FADE_DEFAULT_DURATION_SEC = 0.35;

export const BENNE_SCREEN_FADE_DEFAULT_COLOR = 0x000000;

/**
 * Renders above HUD and choice-dialog GUI overlays; below Display Text, Speaking Text
 * ({@link SPEAKING_TEXT_OVERLAY_DEPTH}) and the {@link RoomScene} custom game cursor
 * (see `CUSTOM_CURSOR_DEPTH` in `RoomScene.ts`).
 */
export const BENNE_SCREEN_FADE_OVERLAY_DEPTH = 450_000;

/**
 * Speaking Text (`speaking-text`, Bennescript `say`) draws above the screen fade so lines
 * stay readable during `fadeOut()`, and below the custom cursor (`CUSTOM_CURSOR_DEPTH`).
 */
export const SPEAKING_TEXT_OVERLAY_DEPTH = 460_000;

/**
 * Display Text (`display-text`, Bennescript `display`) also draws above the screen fade, so a
 * title or an ending can be shown over black (`fadeOut()` then `display()`).
 */
export const DISPLAY_TEXT_OVERLAY_DEPTH = 455_000;

/**
 * A GUI with `pauseGame` (e.g. a line history) draws above the speech and display text it pauses,
 * and above the screen fade, so it can be opened during a title over black.
 */
export const PAUSE_GUI_OVERLAY_DEPTH = 470_000;
