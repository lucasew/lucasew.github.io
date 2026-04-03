import { defineConfig } from 'astro/config'
import mdx from '@astrojs/mdx'
import tailwindcss from '@tailwindcss/vite'

export default defineConfig({
  site: 'https://lucasew.github.io',
  publicDir: 'static',
  outDir: 'public',
  integrations: [mdx()],
  vite: {
    plugins: [tailwindcss()],
  },
})
