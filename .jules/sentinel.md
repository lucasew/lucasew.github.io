## 2024-07-22 - XSS Vulnerability in Hugo Configuration

**Vulnerability:** The Hugo configuration file `hugo.toml` had
`[markup.goldmark.renderer] unsafe = true`, which allows raw HTML to be rendered
from Markdown files. This creates a significant Cross-Site Scripting (XSS)
vulnerability, as it would allow arbitrary HTML and script execution if a
compromised post were to be added.

**Learning:** I discovered that at least one older blog post
(`content/post/20210228-vivo-easy/index.pt.md`) uses raw HTML to implement a
custom timeline component. Disabling the `unsafe` setting is critical for
security but will break the visual rendering of this component. This highlights
a project-specific pattern of embedding complex HTML directly into content.

## Instructions

- Do not modify or add HTTP headers in `vercel.json`.
