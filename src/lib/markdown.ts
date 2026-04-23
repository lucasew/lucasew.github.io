import MarkdownIt from 'markdown-it'
import type { Entry } from './content'

const md = new MarkdownIt({
  html: true,
  linkify: true,
  typographer: true,
})

const defaultLinkOpen = md.renderer.rules.link_open
md.renderer.rules.link_open = (tokens, idx, options, env, self) => {
  const token = tokens[idx]
  token.attrSet('target', '_blank')

  const rel = token.attrGet('rel')
  if (!rel) {
    token.attrSet('rel', 'noopener noreferrer')
  } else if (!rel.includes('noopener')) {
    token.attrSet('rel', `${rel} noopener noreferrer`)
  }

  if (defaultLinkOpen) {
    return defaultLinkOpen(tokens, idx, options, env, self)
  }
  return self.renderToken(tokens, idx, options)
}

function evalTemplate(input: string, entry: Entry): string {
  return input.replace(/\{\{\s*\.Title\s*\}\}/g, entry.title)
}

function renderDetailsShortcodes(input: string, entry: Entry, depth: number): string {
  const detailsRegex = /\{\{%?\s*details([^%}]*)%?\}\}([\s\S]*?)\{\{%?\s*\/details\s*%?\}\}/g

  return input.replace(detailsRegex, (_whole, rawArgs: string, rawInner: string) => {
    const args = rawArgs?.trim() ?? ''

    const quotedArg = args.match(/"([\s\S]*?)"/)
    const summaryRaw = quotedArg?.[1] ?? 'Details'
    const isOpen = /open\s*=\s*"?true"?/i.test(args)

    const summary = evalTemplate(summaryRaw, entry)
    const inner = renderHtml(evalTemplate(rawInner.trim(), entry), entry, depth + 1)
    const summaryHtml = md.renderInline(summary)

    return `<details${isOpen ? ' open' : ''}><summary>${summaryHtml}</summary>${inner}</details>`
  })
}

function renderEvalShortcodes(input: string, entry: Entry, depth: number): string {
  const evalRegex = /\{\{%?\s*eval\s*%?\}\}([\s\S]*?)\{\{%?\s*\/eval\s*%?\}\}/g

  return input.replace(evalRegex, (_whole, rawInner: string) => {
    const expanded = evalTemplate(rawInner.trim(), entry)
    return renderShortcodes(expanded, entry, depth + 1)
  })
}

function renderShortcodes(input: string, entry: Entry, depth: number): string {
  if (depth > 8) {
    return input
  }

  let current = input
  current = renderEvalShortcodes(current, entry, depth)
  current = renderDetailsShortcodes(current, entry, depth)
  return current
}

/**
 * Renders raw markdown into full HTML.
 *
 * This function handles the primary compilation pipeline for content entries.
 * Before handing off to `markdown-it`, it eagerly evaluates custom Hugo-style
 * shortcodes (e.g., `{{ eval }}` and `{{ details }}`).
 *
 * @param markdown - The raw markdown string to render.
 * @param entry - The contextual content entry, used to evaluate shortcode templates (like `{{ .Title }}`).
 * @param depth - Internal recursion tracker to prevent infinite shortcode nesting. Hard-capped at 8.
 * @returns Fully rendered HTML string.
 */
export function renderHtml(markdown: string, entry: Entry, depth = 0): string {
  const withShortcodes = renderShortcodes(markdown, entry, depth)
  return md.render(withShortcodes)
}

/**
 * Renders raw markdown into inline HTML, omitting block-level wrapping tags like `<p>`.
 *
 * Useful for rendering small snippets of formatted text, such as summary fields
 * or titles, where block tags would break the surrounding layout.
 *
 * Note: This does *not* evaluate shortcodes.
 *
 * @param markdown - The raw markdown string to render.
 * @returns Inline HTML string.
 */
export function renderInline(markdown: string): string {
  return md.renderInline(markdown)
}
