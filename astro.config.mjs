import { defineConfig } from 'astro/config'
import mdx from '@astrojs/mdx'
import sentry from '@sentry/astro'
import tailwindcss from '@tailwindcss/vite'

const sentryOptions = {
  autoInstrumentation: {
    requestHandler: false,
  },
}

if (process.env.SENTRY_AUTH_TOKEN && process.env.SENTRY_ORG && process.env.SENTRY_PROJECT) {
  sentryOptions.sourceMapsUploadOptions = {
    authToken: process.env.SENTRY_AUTH_TOKEN,
    org: process.env.SENTRY_ORG,
    project: process.env.SENTRY_PROJECT,
  }
}

export default defineConfig({
  site: 'https://lucasew.github.io',
  publicDir: 'static',
  outDir: 'public',
  integrations: [mdx(), sentry(sentryOptions)],
  vite: {
    plugins: [tailwindcss()],
  },
})
