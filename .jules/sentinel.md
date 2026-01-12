## 2024-07-22 - XSS Vulnerability in Hugo Configuration

**Vulnerability:** The Hugo configuration file `hugo.toml` had `[markup.goldmark.renderer] unsafe = true`, which allows raw HTML to be rendered from Markdown files. This creates a significant Cross-Site Scripting (XSS) vulnerability, as it would allow arbitrary HTML and script execution if a compromised post were to be added.

**Learning:** I discovered that at least one older blog post (`content/post/20210228-vivo-easy/index.pt.md`) uses raw HTML to implement a custom timeline component. Disabling the `unsafe` setting is critical for security but will break the visual rendering of this component. This highlights a project-specific pattern of embedding complex HTML directly into content.

## Instructions

* Do not modify or add HTTP headers in `vercel.json`.


## 2024-07-25 - Mitigated Tabnabbing Vulnerability
**Vulnerability:** External links using `target="_blank"` in `layouts/_default/single.html` were missing the `rel="noopener noreferrer"` attribute. This allows the destination page to gain partial control over the source page via `window.opener`, which can be exploited for phishing attacks.
**Learning:** This vulnerability often goes unnoticed but is critical for protecting users from malicious external sites. It was present in a central template, which means a single fix protects all pages that use it. The codebase relies on Hugo templates for HTML generation, making them a critical point for security reviews.
**Prevention:** Always add `rel="noopener noreferrer"` to any link that uses `target="_blank"`. This should be enforced through code reviews and, if possible, a linter or static analysis tool configured to catch this specific pattern.
