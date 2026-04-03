import { defineConfig } from 'astro/config'
import tailwindcss from '@tailwindcss/vite'

export default defineConfig({
  site: 'https://lucasew.github.io',
  publicDir: 'static',
  outDir: 'public',
  vite: {
    plugins: [tailwindcss()],
  },
})
