import type { Dialog, DialogOption } from '../../types/dialogue.js';
import type { GameStateManager } from '../gameState/GameStateManager.js';

export function dialogOptionEnabledVariableKey(dialogId: string, optionId: string): string {
  return `dialog:${dialogId}:option:${optionId}:enabled`;
}

export function dialogOptionUsedVariableKey(dialogId: string, optionId: string): string {
  return `dialog:${dialogId}:option:${optionId}:used`;
}

/**
 * Own change: a text the game sets for an option at run time (a keypad that shows the word typed so far), shown instead
 * of the one in the dialog's file. Saved, like the rest of the option's state.
 */
export function dialogOptionTextVariableKey(dialogId: string, optionId: string): string {
  return `dialog:${dialogId}:option:${optionId}:text`;
}

export const BENNE_ACTIVE_DIALOG_ID_VARIABLE = '__benne_active_dialog_id';

export function readEffectiveDialogOptionEnabled(
  manager: GameStateManager,
  definition: Dialog,
  optionId: string,
): boolean {
  const opt = definition.options.find((o) => o.id === optionId);
  const base = opt ? opt.enabled !== false : true;
  const key = dialogOptionEnabledVariableKey(definition.id, optionId);
  if (!manager.hasVariable(key)) {
    return base;
  }
  const v = manager.getVariable(key);
  return v === true;
}

export function readEffectiveDialogOptionUsed(
  manager: GameStateManager,
  definition: Dialog,
  optionId: string,
): boolean {
  const opt = definition.options.find((o) => o.id === optionId);
  const base = opt ? opt.used === true : false;
  const key = dialogOptionUsedVariableKey(definition.id, optionId);
  if (!manager.hasVariable(key)) {
    return base;
  }
  const v = manager.getVariable(key);
  return v === true;
}

/**
 * The options the list shows, in the order it shows them: the unused ones first, then the already-used ones, then the
 * ones marked `last` (goodbyes), each group in definition order. Each with its run-time text, if it has one.
 */
export function visibleDialogOptionsInOrder(manager: GameStateManager, definition: Dialog): DialogOption[] {
  const visible = definition.options.filter((o) => readEffectiveDialogOptionEnabled(manager, definition, o.id));
  const fresh: DialogOption[] = [];
  const used: DialogOption[] = [];
  const last: DialogOption[] = [];
  for (const o of visible) {
    if (o.last === true) last.push(o);
    else if (readEffectiveDialogOptionUsed(manager, definition, o.id)) used.push(o);
    else fresh.push(o);
  }
  return [...fresh, ...used, ...last].map((o) => {
    const key = dialogOptionTextVariableKey(definition.id, o.id);
    const text = manager.hasVariable(key) ? manager.getVariable(key) : undefined;
    return typeof text === 'string' ? { ...o, text } : o;
  });
}
