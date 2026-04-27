import rss from '@astrojs/rss'
import type { APIRoute } from 'astro'
import { LANGS, type Lang } from '../../../lib/i18n'
import { allEntries } from '../../../lib/content'
import { renderHtml } from '../../../lib/markdown'

function toDate(value: unknown): Date | undefined {
  if (value instanceof Date && !Number.isNaN(value.getTime())) return value
  if (typeof value !== 'string') return undefined
  const parsed = new Date(value)
  return Number.isNaN(parsed.getTime()) ? undefined : parsed
}

function escapeCdata(value: string): string {
  return value.replaceAll(']]>', ']]]]><![CDATA[>')
}

export function getStaticPaths() {
  return LANGS.map((lang) => ({ params: { lang } }))
}

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
      const date = toDate(post.frontmatter.date ?? post.date)
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
    site,
    xmlns: {
      content: 'http://purl.org/rss/1.0/modules/content/',
    },
    items,
  })
}
