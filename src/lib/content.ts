import { LANGS, type Lang } from './i18n'
import { loadEntries, slugKey } from './contentLoader'

export type EntryKind = 'page' | 'section'

export interface Entry {
  id: string
  lang: Lang
  kind: EntryKind
  slugSegments: string[]
  title: string
  summary?: string
  body: string
  frontmatter: Record<string, unknown>
  aliases: string[]
  url: string
  date?: string
  sourceFile: string
}

const BY_SLUG_BY_LANG = new Map<string, Map<Lang, Entry>>()
const BY_URL = new Map<string, Entry>()

export const allEntries = loadEntries()

for (const entry of allEntries) {
  if (!BY_SLUG_BY_LANG.has(slugKey(entry.slugSegments))) {
    BY_SLUG_BY_LANG.set(slugKey(entry.slugSegments), new Map())
  }
  BY_SLUG_BY_LANG.get(slugKey(entry.slugSegments))?.set(entry.lang, entry)

  BY_URL.set(entry.url, entry)

  for (const alias of entry.aliases) {
    // aliases are maintained for backward compatibility and normalized to include lang
    const normalized = alias.endsWith('/') ? alias : `${alias}/`
    const langPrefix = `/${entry.lang}`
    const aliasWithLang = normalized.startsWith(langPrefix)
      ? normalized
      : `${langPrefix}${normalized}`.replace('//', '/')
    BY_URL.set(aliasWithLang, entry)
  }
}

export function getEntryByUrl(urlPath: string): Entry | undefined {
  const normalized = urlPath.endsWith('/') ? urlPath : `${urlPath}/`
  return BY_URL.get(normalized)
}

export function getEntry(lang: Lang, slugSegments: string[]): Entry | undefined {
  return BY_SLUG_BY_LANG.get(slugKey(slugSegments))?.get(lang)
}

export function getTranslations(entry: Entry): Entry[] {
  const all = BY_SLUG_BY_LANG.get(slugKey(entry.slugSegments))
  if (!all) return [entry]
  return LANGS.map((lang) => all.get(lang)).filter((item): item is Entry => Boolean(item))
}

function isDirectChild(parent: string[], child: string[]): boolean {
  if (child.length !== parent.length + 1) return false
  for (let i = 0; i < parent.length; i += 1) {
    if (parent[i] !== child[i]) return false
  }
  return true
}

export function getChildren(section: Entry): Entry[] {
  if (section.kind !== 'section') return []

  const children = allEntries.filter((entry) => (
    entry.lang === section.lang &&
    entry.id !== section.id &&
    isDirectChild(section.slugSegments, entry.slugSegments)
  ))

  children.sort((a, b) => {
    const ad = a.date ? Date.parse(a.date) : Number.NEGATIVE_INFINITY
    const bd = b.date ? Date.parse(b.date) : Number.NEGATIVE_INFINITY
    if (ad !== bd) return bd - ad
    return a.title.localeCompare(b.title)
  })

  return children
}

export function getSectionTitle(lang: Lang, slugSegments: string[]): string {
  const section = getEntry(lang, slugSegments)
  return section?.title ?? ''
}

export function getStaticPathsForEntries(): Array<{ params: { slug: string } }> {
  const paths = new Map<string, { params: { slug: string } }>()

  for (const entry of allEntries) {
    const slug = [entry.lang, ...entry.slugSegments]
    paths.set(`/${slug.join('/')}/`, { params: { slug: slug.join('/') } })
  }

  for (const [urlPath] of BY_URL.entries()) {
    const clean = urlPath.replace(/^\//, '').replace(/\/$/, '')
    if (!clean) continue
    paths.set(urlPath, { params: { slug: clean } })
  }

  return [...paths.values()]
}

export function getKnownUrls(): string[] {
  return [...BY_URL.keys()]
}
