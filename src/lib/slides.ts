import type { Entry } from './content'
import { createMarkdownProcessor } from '@astrojs/markdown-remark'

export interface SlideSection {
  html: string
  autoAnimate: boolean
}

const markdownProcessorPromise = createMarkdownProcessor({
  syntaxHighlight: 'shiki',
  shikiConfig: {
    theme: 'github-dark',
  },
})

export async function splitSlideSections(entry: Entry): Promise<SlideSection[]> {
  const markdownProcessor = await markdownProcessorPromise
  const renderedResult = await markdownProcessor.render(entry.body)
  const rendered = renderedResult.code

  return rendered
    .split(/<hr\s*\/?>/gi)
    .map((chunk) => chunk.trim())
    .filter(Boolean)
    .map((chunk) => {
      const marker = '<script>document.currentScript.parentNode.setAttribute("data-auto-animate", "1")</script>'
      const hasAutoAnimateMarker = chunk.includes('<p>%auto-animate%</p>') || chunk.includes(marker)
      const cleaned = chunk
        .replace('<p>%auto-animate%</p>', '')
        .replace(marker, '')
        .trim()
      return {
        html: cleaned,
        autoAnimate: hasAutoAnimateMarker,
      }
    })
}
