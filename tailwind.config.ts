import type { Config } from 'tailwindcss'
import daisyui from 'daisyui'

export default {
  content: [
    './layouts/**/*.html',
    './content/**/*.md',
  ],
  plugins: [
    daisyui,
  ],
} satisfies Config
