import { defineCollection } from 'astro:content'
import { glob } from 'astro/loaders'

/**
 * Astro Content Collection for blog posts.
 *
 * Uses a glob loader to find localized markdown files within the post directory.
 * The `generateId` function normalizes the collection entry IDs to follow the
 * `<lang>/<slug>` format, stripping out the file extension and `index` prefix,
 * which ensures predictable lookup across the site.
 */
const posts = defineCollection({
  loader: glob({
    pattern: '**/index.{en,pt}.{md,mdx}',
    base: './src/content/post',
    generateId: ({ entry }) => {
      const match = entry.match(/^(.*)\/index\.(en|pt)\.(md|mdx)$/)
      if (!match) return entry
      const [, postSlug, lang] = match
      return `${lang}/${postSlug}`
    },
  }),
})

export const collections = { posts }
