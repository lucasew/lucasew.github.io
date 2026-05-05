import type { Entry } from './content'
import { createMarkdownProcessor } from '@astrojs/markdown-remark'

/**
 * Represents a single parsed slide within a Reveal.js presentation.
 */
export interface SlideSection {
  /** The rendered HTML content of the slide */
  html: string
  /** Whether Reveal.js should automatically animate transitions between elements on this slide */
  autoAnimate: boolean
}

const markdownProcessorPromise = createMarkdownProcessor({
  syntaxHighlight: 'shiki',
  shikiConfig: {
    theme: 'github-dark',
  },
})

/**
 * Parses a markdown entry's body into individual HTML slide sections for Reveal.js.
 *
 * This function handles markdown rendering with syntax highlighting, and then slices
 * the output into individual slides based on horizontal rules (`<hr />`). It also
 * identifies auto-animate directives (`%auto-animate%` or embedded scripts) so they
 * can be properly applied as data attributes to the parent `<section>` element in the template.
 *
 * @param entry - The parsed content entry to extract slides from
 * @returns A promise resolving to an array of SlideSection objects
 */
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
