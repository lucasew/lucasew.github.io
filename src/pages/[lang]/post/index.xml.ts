import rss from '@astrojs/rss'
import type { APIRoute } from 'astro'
import { LANGS, type Lang } from '../../../lib/i18n'
import { allEntries } from '../../../lib/content'
import { renderHtml } from '../../../lib/markdown'

/**
 * Safely parses heterogeneous date formats from frontmatter into a Date object.
 *
 * Frontmatter dates can be parsed as native Date objects or strings by gray-matter.
 * This ensures consistent parsing and filters out invalid dates.
 *
 * @param value Raw date value from frontmatter
 * @returns Parsed Date object or undefined if invalid
 */
function toDate(value: unknown): Date | undefined {
  if (value instanceof Date && !Number.isNaN(value.getTime())) return value
  if (typeof value !== 'string') return undefined
  const parsed = new Date(value)
  return Number.isNaN(parsed.getTime()) ? undefined : parsed
}

/**
 * Escapes CDATA closing sequences within content to prevent XML parsing errors.
 *
 * RSS feeds wrap HTML content in CDATA blocks (`<![CDATA[...]]>`). If the HTML
 * itself contains `]]>`, it prematurely closes the CDATA block. This replaces
 * it with a safe sequence that XML parsers render correctly.
 *
 * @param value Raw HTML content
 * @returns HTML content safe for embedding inside an XML CDATA block
 */
function escapeCdata(value: string): string {
  return value.replaceAll(']]>', ']]]]><![CDATA[>')
}

/**
 * Declares the dynamic routes for Astro's static site generation.
 * Generates an RSS feed URL for each supported language (e.g., `/en/post/index.xml`).
 */
export function getStaticPaths() {
  return LANGS.map((lang) => ({ params: { lang } }))
}

/**
 * Generates the RSS feed XML response for a given language.
 *
 * Filters global entries to find posts in the requested language,
 * sorts them chronologically (newest first), and embeds the fully
 * rendered HTML body inside a CDATA block for RSS readers.
 */
export const GET: APIRoute = async ({ params, site }) => {
  const lang = params.lang as Lang
  if (!LANGS.includes(lang)) {
    return new Response('Not Found', { status: 404 })
  }

  const posts = allEntries
    .filter((entry) => (
      entry.lang === lang
      && entry.kind === 'page'
      && entry.slugSegments.length === 2
      && entry.slugSegments[0] === 'post'
    ))
  const items = posts
    .map((post) => {
      const date = toDate(post.date)
      const description = post.summary ?? ''

      return {
        title: post.title,
        description,
        link: post.url,
        pubDate: date,
        customData: `<content:encoded><![CDATA[${escapeCdata(renderHtml(post.body, post))}]]></content:encoded>`,
      }
    })
    .sort((a, b) => {
      const ad = a.pubDate?.getTime() ?? Number.NEGATIVE_INFINITY
      const bd = b.pubDate?.getTime() ?? Number.NEGATIVE_INFINITY
      return bd - ad
    })

  return rss({
    title: lang === 'pt' ? 'Posts do blog do lucasew' : "lucasew's blog posts",
    description: lang === 'pt'
      ? 'Feed RSS das publicações em português'
      : 'RSS feed for English posts',
    site: site ?? 'https://lucasew.github.io',
    xmlns: {
      content: 'http://purl.org/rss/1.0/modules/content/',
    },
    items,
  })
}
