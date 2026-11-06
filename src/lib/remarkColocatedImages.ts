import path from 'node:path'

type Node = {
  type: string
  url?: string
  children?: Node[]
}

/**
 * Pages CMS stores an upload as a repo path under `src/content/post/<slug>/`.
 * Astro resolves markdown images relative to the source file, so rewrite that
 * path to `./<file>` when it sits in the same directory.
 */
export function remarkColocatedImages() {
  return (tree: Node, file: { dirname?: string; path?: string }) => {
    const dir = file.dirname || (file.path ? path.dirname(file.path) : '')
    if (!dir) return

    const slug = path.basename(dir)
    walk(tree, (node) => {
      if (node.type !== 'image' && node.type !== 'definition') return
      const next = colocatedImageUrl(node.url, slug)
      if (next) node.url = next
    })
  }
}

export function colocatedImageUrl(url: string | undefined, slug: string): string | undefined {
  if (!url || /^(https?:|data:|\/\/)/.test(url)) return undefined

  const normalized = url.replace(/\\/g, '/').replace(/^\.\//, '')
  const marker = `${slug}/`
  const index = normalized.lastIndexOf(marker)
  if (index === -1) return undefined

  const fileName = normalized.slice(index + marker.length)
  if (!fileName || fileName.includes('/')) return undefined
  return `./${fileName}`
}

function walk(node: Node, visit: (node: Node) => void) {
  visit(node)
  for (const child of node.children ?? []) walk(child, visit)
}
