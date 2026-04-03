import type { Entry } from './content'
import { renderHtml } from './markdown'

export function splitSlideSections(entry: Entry): string[] {
  const rendered = renderHtml(entry.body, entry)
    .replaceAll(
      '<p>%auto-animate%</p>',
      '<script>document.currentScript.parentNode.setAttribute("data-auto-animate", "1")</script>',
    )

  return rendered
    .split(/<hr\s*\/?>/gi)
    .map((chunk) => chunk.trim())
    .filter(Boolean)
}
