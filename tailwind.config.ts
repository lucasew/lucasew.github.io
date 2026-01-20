import type { Config } from 'tailwindcss'
import typography from '@tailwindcss/typography'
import typography from '@tailwindcss/typography'
import daisyui from 'daisyui'

export default {
  content: [
    './layouts/**/*.html',
    './content/**/*.md',
  ],
  theme: {
    extend: {},
  },
  plugins: [
    typography,
    daisyui,
  ],
} satisfies Config
