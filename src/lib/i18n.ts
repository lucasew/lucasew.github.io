export type Lang = 'en' | 'pt'

export const DEFAULT_LANG: Lang = 'en'
export const LANGS: Lang[] = ['en', 'pt']

/**
 * Type guard to verify if a given string is a supported language code.
 * Used defensively when processing raw URL slugs or user inputs.
 *
 * @param value - The raw string to check, or undefined
 * @returns True if the value is exactly 'en' or 'pt'
 */
export function isLang(value: string | undefined): value is Lang {
  return value === 'en' || value === 'pt'
}

/**
 * Extracts the language prefix from a route's slug segments.
 *
 * This function expects Astro's catch-all route segments. If the first
 * segment is a recognized language (e.g., 'en' or 'pt'), it strips it
 * and returns the remaining segments. Otherwise, it assumes the default
 * language and returns the segments untouched.
 *
 * @param segments - An array of path segments (e.g. `['pt', 'post', 'my-article']`)
 * @returns The resolved language and the remaining path segments
 */
export function parseLangFromSegments(segments: string[]): { lang: Lang; rest: string[] } {
  const maybeLang = segments[0]
  if (isLang(maybeLang)) {
    return { lang: maybeLang, rest: segments.slice(1) }
  }
  return { lang: DEFAULT_LANG, rest: segments }
}

/**
 * Constructs an absolute URL path for a given language and slug.
 *
 * Ensures proper trailing slashes and handles empty slugs gracefully
 * (returning just the language root, e.g. `/pt/`). Empty or falsy segments
 * within the array are stripped out to prevent double-slashes in the URL.
 *
 * @param lang - The target language code
 * @param slug - Array of path segments to append
 * @returns The generated absolute URL path (e.g. `/en/about/`)
 */
export function toUrl(lang: Lang, slug: string[]): string {
  const clean = slug.filter(Boolean)
  return clean.length > 0 ? `/${lang}/${clean.join('/')}/` : `/${lang}/`
}

/**
 * Provides static string translations for hardcoded UI components.
 *
 * This acts as a minimalist i18n dictionary for template strings.
 * It is synchronous and strictly typed to prevent requesting missing keys.
 *
 * @param lang - The active language context
 * @param key - The strictly typed translation key
 * @returns The translated string
 */
export function t(lang: Lang, key: 'also-available-on' | 'discussed-on'): string {
  const table: Record<Lang, Record<string, string>> = {
    en: {
      'also-available-on': 'Also available on',
      'discussed-on': 'Discussed on',
    },
    pt: {
      'also-available-on': 'Também disponível em',
      'discussed-on': 'Discutido em',
    },
  }

  return table[lang][key]
}
