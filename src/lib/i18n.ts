export type Lang = 'en' | 'pt'

export const DEFAULT_LANG: Lang = 'en'
export const LANGS: Lang[] = ['en', 'pt']

export function isLang(value: string | undefined): value is Lang {
  return value === 'en' || value === 'pt'
}

export function parseLangFromSegments(segments: string[]): { lang: Lang; rest: string[] } {
  const maybeLang = segments[0]
  if (isLang(maybeLang)) {
    return { lang: maybeLang, rest: segments.slice(1) }
  }
  return { lang: DEFAULT_LANG, rest: segments }
}

export function toUrl(lang: Lang, slug: string[]): string {
  const clean = slug.filter(Boolean)
  return clean.length > 0 ? `/${lang}/${clean.join('/')}/` : `/${lang}/`
}

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
