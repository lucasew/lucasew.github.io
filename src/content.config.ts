import { defineCollection } from 'astro:content'
import { glob } from 'astro/loaders'

const posts = defineCollection({
  loader: glob({
    pattern: '**/index.{en,pt}.md',
    base: './src/content/post',
    generateId: ({ entry }) => {
      const match = entry.match(/^(.*)\/index\.(en|pt)\.md$/)
      if (!match) return entry
      const [, postSlug, lang] = match
      return `${lang}/${postSlug}`
    },
  }),
})

export const collections = { posts }
