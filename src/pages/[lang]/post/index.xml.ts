import rss from '@astrojs/rss'
import { getCollection } from 'astro:content'
import type { APIRoute } from 'astro'
import { LANGS, type Lang } from '../../../lib/i18n'

function toDate(value: unknown): Date | undefined {
  if (value instanceof Date && !Number.isNaN(value.getTime())) return value
  if (typeof value !== 'string') return undefined
  const parsed = new Date(value)
  return Number.isNaN(parsed.getTime()) ? undefined : parsed
}

export function getStaticPaths() {
  return LANGS.map((lang) => ({ params: { lang } }))
}

export const GET: APIRoute = async ({ params, site }) => {
  const lang = params.lang as Lang
  if (!LANGS.includes(lang)) {
    return new Response('Not Found', { status: 404 })
  }

  const posts = await getCollection('posts', ({ id }) => id.startsWith(`${lang}/`))
  const items = posts
    .map((post) => {
      const postSlug = post.id.replace(`${lang}/`, '')
      const date = toDate(post.data.date)
      const description = typeof post.data.summary === 'string'
        ? post.data.summary
        : (typeof post.data.description === 'string' ? post.data.description : '')

      return {
        title: post.data.title,
        description,
        link: `/${lang}/post/${postSlug}/`,
        pubDate: date,
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
    items,
  })
}
