import fs from 'node:fs'
import path from 'node:path'
import matter from 'gray-matter'
import { LANGS, type Lang, toUrl } from './i18n'
import { reportError } from './errors'
import type { EntryKind, Entry } from './content'

interface Candidate {
  lang: Lang
  kind: EntryKind
  slugSegments: string[]
  sourceFile: string
  explicitLang: boolean
  frontmatter: Record<string, unknown>
  body: string
}

export const CONTENT_ROOT = path.join(process.cwd(), 'src', 'content')

export function readAllContentFiles(root: string): string[] {
  const files: string[] = []
  const stack = [root]

  while (stack.length > 0) {
    const current = stack.pop()
    if (!current) continue

    let items: fs.Dirent[] = []
    try {
      items = fs.readdirSync(current, { withFileTypes: true })
    } catch (error) {
      reportError(error, { current })
      throw error
    }

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

export function inferKind(baseName: string): EntryKind | null {
  if (baseName.startsWith('_index')) return 'section'
  if (baseName.startsWith('index')) return 'page'
  return null
}

export function inferLang(baseName: string): Lang | null {
  const match = baseName.match(/\.(en|pt)\.(md|mdx)$/)
  if (!match) return null
  return match[1] as Lang
}

export function slugKey(slug: string[]): string {
  return slug.join('/')
}

export function toEntry(candidate: Candidate): Entry {
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

export function loadEntries(): Entry[] {
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
    let raw = ''
    try {
      raw = fs.readFileSync(file, 'utf8')
    } catch (error) {
      reportError(error, { file })
      throw error
    }

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
