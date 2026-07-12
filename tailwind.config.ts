import type { Config } from 'tailwindcss'
import daisyui from 'daisyui'

export default {
  content: [
    './src/**/*.{astro,ts,md,mdx}',
    './layouts/**/*.html',
  ],
  theme: {
    extend: {},
  },
  plugins: [
    daisyui,
  ],
} satisfies Config
