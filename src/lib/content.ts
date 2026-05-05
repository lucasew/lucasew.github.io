import fs from 'node:fs'
import path from 'node:path'
import matter from 'gray-matter'
import { LANGS, type Lang, toUrl } from './i18n'

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

interface Candidate {
  lang: Lang
  kind: EntryKind
  slugSegments: string[]
  sourceFile: string
  explicitLang: boolean
  frontmatter: Record<string, unknown>
  body: string
}

const CONTENT_ROOT = path.join(process.cwd(), 'src', 'content')
const BY_SLUG_BY_LANG = new Map<string, Map<Lang, Entry>>()
const BY_URL = new Map<string, Entry>()

function readAllContentFiles(root: string): string[] {
  const files: string[] = []
  const stack = [root]

  while (stack.length > 0) {
    const current = stack.pop()
    if (!current) continue

    const items = fs.readdirSync(current, { withFileTypes: true })
    for (const item of items) {
      const full = path.join(current, item.name)
      if (item.isDirectory()) {
        stack.push(full)
        continue
      }

      if (item.isFile() && (item.name.endsWith('.md') || item.name.endsWith('.mdx'))) {
        files.push(full)
      }
    }
  }

  return files
}

function inferKind(baseName: string): EntryKind | null {
  if (baseName.startsWith('_index')) return 'section'
  if (baseName.startsWith('index')) return 'page'
  return null
}

function inferLang(baseName: string): Lang | null {
  const match = baseName.match(/\.(en|pt)\.(md|mdx)$/)
  if (!match) return null
  return match[1] as Lang
}

function slugKey(slug: string[]): string {
  return slug.join('/')
}

function toEntry(candidate: Candidate): Entry {
  const titleRaw = candidate.frontmatter.title
  const title = typeof titleRaw === 'string' && titleRaw.trim().length > 0
    ? titleRaw
    : (candidate.slugSegments.at(-1) ?? 'Untitled')

  const summaryRaw = candidate.frontmatter.summary
  const summary = typeof summaryRaw === 'string' ? summaryRaw : undefined

  const aliasesRaw = candidate.frontmatter.aliases
  const aliases = Array.isArray(aliasesRaw)
    ? aliasesRaw.filter((item): item is string => typeof item === 'string' && item.startsWith('/'))
    : []

  const dateRaw = candidate.frontmatter.date
  const date = typeof dateRaw === 'string' ? dateRaw : undefined

  return {
    id: `${candidate.lang}:${slugKey(candidate.slugSegments)}:${candidate.kind}`,
    lang: candidate.lang,
    kind: candidate.kind,
    slugSegments: candidate.slugSegments,
    title,
    summary,
    body: candidate.body,
    frontmatter: candidate.frontmatter,
    aliases,
    url: toUrl(candidate.lang, candidate.slugSegments),
    date,
    sourceFile: candidate.sourceFile,
  }
}

function loadEntries(): Entry[] {
  const files = readAllContentFiles(CONTENT_ROOT)
  const buckets = new Map<string, Candidate[]>()

  for (const file of files) {
    const rel = path.relative(CONTENT_ROOT, file)
    const relDir = path.dirname(rel)
    const baseName = path.basename(file)
    const kind = inferKind(baseName)
    if (!kind) continue

    const slugSegments = relDir === '.' ? [] : relDir.split(path.sep)
    const langHint = inferLang(baseName)
    const raw = fs.readFileSync(file, 'utf8')
    const parsed = matter(raw)

    const langs = langHint ? [langHint] : LANGS
    for (const lang of langs) {
      const candidate: Candidate = {
        lang,
        kind,
        slugSegments,
        sourceFile: rel,
        explicitLang: Boolean(langHint),
        frontmatter: parsed.data,
        body: parsed.content,
      }

      const key = `${lang}:${kind}:${slugKey(slugSegments)}`
      const items = buckets.get(key) ?? []
      items.push(candidate)
      buckets.set(key, items)
    }
  }

  const entries: Entry[] = []
  for (const candidates of buckets.values()) {
    candidates.sort((a, b) => Number(b.explicitLang) - Number(a.explicitLang))
    entries.push(toEntry(candidates[0]))
  }

  entries.sort((a, b) => a.url.localeCompare(b.url))
  return entries
}

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
 * Returns a list of all fully-resolved canonical URLs and aliases known to the system.
 * Useful for sitemap generation or global link validation.
 */
export function getKnownUrls(): string[] {
  return [...BY_URL.keys()]
}
