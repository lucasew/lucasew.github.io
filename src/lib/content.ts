import { LANGS, type Lang } from './i18n'
import { loadEntries, slugKey } from './contentLoader'

export type EntryKind = 'page' | 'section'

/**
 * Represents a parsed Markdown/MDX content file, resolving metadata, relationships, and URLs.
 *
 * This is the fundamental unit of content used for routing and rendering throughout the application.
 * It abstracts away the physical file path, providing a normalized view of the content that
 * handles localization and inferred properties (like fallback titles).
 */
export interface Entry {
  /** Unique composite identifier format: `{lang}:{slug}:{kind}` (e.g., `en:post/my-article:page`) */
  id: string
  lang: Lang
  kind: EntryKind
  /** The ordered path segments relative to the content root, used for dynamic routing (e.g., `['post', 'my-article']`) */
  slugSegments: string[]
  /** The resolved title. Falls back to the last slug segment or 'Untitled' if not provided in frontmatter. */
  title: string
  summary?: string
  /** The raw markdown content body, unrendered. Shortcodes are not processed at this stage. */
  body: string
  frontmatter: Record<string, unknown>
  /** Historic URLs or alternative paths that should redirect to this entry's primary URL. */
  aliases: string[]
  /** The primary canonical URL path for this entry (e.g., `/en/post/my-article/`). Always includes a trailing slash. */
  url: string
  /** ISO 8601 date string, used primarily for sorting section children. */
  date?: string
  /** The relative path to the physical source file from the content root. */
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

/**
 * Retrieves a content entry by its exact URL path.
 *
 * @param urlPath - The requested URL path. Automatically normalized to ensure trailing slash matching.
 * @returns The matching Entry or undefined if no content maps to this URL. Also resolves aliases.
 */
export function getEntryByUrl(urlPath: string): Entry | undefined {
  const normalized = urlPath.endsWith('/') ? urlPath : `${urlPath}/`
  return BY_URL.get(normalized)
}

/**
 * Retrieves a content entry by its localization and hierarchical slug.
 *
 * @param lang - The target language ('en' or 'pt').
 * @param slugSegments - The path segments identifying the content.
 * @returns The matching Entry or undefined.
 */
export function getEntry(lang: Lang, slugSegments: string[]): Entry | undefined {
  return BY_SLUG_BY_LANG.get(slugKey(slugSegments))?.get(lang)
}

/**
 * Retrieves all available language translations for a given entry.
 *
 * This is useful for building language switchers, ensuring they only link
 * to content that physically exists in the target language.
 *
 * @param entry - The source entry to find translations for.
 * @returns An array of translated entries, including the original entry itself.
 */
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

/**
 * Retrieves the immediate hierarchical children of a given section.
 *
 * Does not traverse deeply; it only returns direct descendants.
 * The resulting array is sorted chronologically descending by date, then alphabetically by title.
 *
 * @param section - The parent section. Must be of kind 'section' (e.g., an `_index.md` file).
 * @returns An ordered array of child entries. Returns an empty array if the input is a 'page'.
 */
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

/**
 * Retrieves the title of a section by its language and slug.
 * Safely falls back to an empty string if the section does not exist.
 */
export function getSectionTitle(lang: Lang, slugSegments: string[]): string {
  const section = getEntry(lang, slugSegments)
  return section?.title ?? ''
}

/**
 * Generates all valid dynamic routing parameters for Astro's `getStaticPaths()`.
 *
 * This function eager-loads all parsed content URLs and defined aliases to ensure
 * Astro generates static HTML files for every possible valid route in the system.
 *
 * @returns An array of route parameters required by Astro's dynamic catch-all route `[...slug].astro`.
 */
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

/**
 * Generates static paths for Astro dynamic routes based on segment names.
 */
export function getStaticPathsForSegments(segmentNames: string[]): Array<{ params: Record<string, string> }> {
  const depth = segmentNames.length
  return getKnownUrls()
    .map((urlPath) => urlPath.split('/').filter(Boolean))
    .filter((parts) => parts.length === depth)
    .map((parts) => {
      const params = Object.fromEntries(segmentNames.map((name, i) => [name, parts[i]]))
      return { params }
    })
}

/**
 * Returns a list of all fully-resolved canonical URLs and aliases known to the system.
 * Useful for sitemap generation or global link validation.
 */
export function getKnownUrls(): string[] {
  return [...BY_URL.keys()]
}
