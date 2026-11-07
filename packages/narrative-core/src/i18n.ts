import type { LocaleTable, TextKey } from './types.js';

export type TextParams = Record<string, string | number | boolean>;

/**
 * Traduccions. Si una clau no existeix a l'idioma actiu, es fa servir l'idioma
 * per defecte; si tampoc hi és, es mostra `⟦clau⟧` (així es veu de seguida).
 *
 * Interpolació: `"Tens {monedes} monedes"` amb `{ monedes: 3 }`.
 */
export class Localizer {
  private tables = new Map<string, LocaleTable>();
  readonly missing = new Set<string>();
  private _locale: string;

  readonly defaultLocale: string;

  constructor(defaultLocale: string, tables: Record<string, LocaleTable> = {}) {
    this.defaultLocale = defaultLocale;
    this._locale = defaultLocale;
    for (const [locale, table] of Object.entries(tables)) this.add(locale, table);
  }

  get locale() {
    return this._locale;
  }

  get locales() {
    return [...this.tables.keys()];
  }

  /** Afegeix (o fusiona) textos d'un idioma. */
  add(locale: string, table: LocaleTable) {
    this.tables.set(locale, { ...this.tables.get(locale), ...table });
  }

  setLocale(locale: string) {
    if (!this.tables.has(locale)) throw new Error(`Idioma no carregat: ${locale}`);
    this._locale = locale;
  }

  has(key: TextKey, locale = this._locale) {
    return this.tables.get(locale)?.[key] !== undefined;
  }

  t(key: TextKey, params?: TextParams): string {
    const raw = this.tables.get(this._locale)?.[key] ?? this.tables.get(this.defaultLocale)?.[key];
    if (raw === undefined) {
      this.missing.add(`${this._locale}:${key}`);
      return `⟦${key}⟧`;
    }
    if (!params) return raw;
    return raw.replace(/\{(\w+)\}/g, (m, name: string) =>
      params[name] !== undefined ? String(params[name]) : m,
    );
  }
}
