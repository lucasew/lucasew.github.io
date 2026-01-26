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

## 2024-07-25 - Mitigated Tabnabbing Vulnerability

**Vulnerability:** External links using `target="_blank"` in
`layouts/_default/single.html` were missing the `rel="noopener noreferrer"`
attribute. This allows the destination page to gain partial control over the
source page via `window.opener`, which can be exploited for phishing attacks.
**Learning:** This vulnerability often goes unnoticed but is critical for
protecting users from malicious external sites. It was present in a central
template, which means a single fix protects all pages that use it. The codebase
relies on Hugo templates for HTML generation, making them a critical point for
security reviews. **Prevention:** Always add `rel="noopener noreferrer"` to any
link that uses `target="_blank"`. This should be enforced through code reviews
and, if possible, a linter or static analysis tool configured to catch this
specific pattern.

## 2026-01-17 - Missing Subresource Integrity (SRI) for Local Scripts

**Vulnerability:** The scripts `htmx.js`, `analytics.js`, and `sentry.js` in
`layouts/_default/baseof.html` were included without Subresource Integrity (SRI)
hashes. Although these scripts are self-hosted, serving them without integrity
checks means that if the files were modified on the server or during delivery
(e.g., via CDN tampering), browsers would execute the modified code.

**Learning:** Hugo's `fingerprint` pipe makes it trivial to add SRI to local
resources at build time. This ensures that the file served to the user matches
exactly what was generated during the build, protecting against tampering. Even
for self-hosted assets, this is a best practice that adds a layer of
defense-in-depth.

**Prevention:** Always use `resources.Get "..." | fingerprint` for local
JavaScript and CSS assets, and include the `integrity` attribute in the
corresponding HTML tag.

## 2026-01-20 - Unmitigated Tabnabbing in Markdown Links

**Vulnerability:** The Markdown render hook
`layouts/_default/_markup/render-link.html` was configured to force
`target="_blank"` on all links but failed to add `rel="noopener noreferrer"`.
This exposed users to tabnabbing vulnerabilities, where the opened page could
potentially hijack the browsing context of the source page via `window.opener`.

**Learning:** While the issue was previously identified and fixed in
`layouts/_default/single.html`, the custom Markdown render hook was overlooked.
This reinforces the need to check all templates that generate links, especially
"global" ones like render hooks. Consistency in security controls across
different parts of the application (e.g., templates vs. render hooks) is
crucial.

**Prevention:** Ensure that any template forcing `target="_blank"` explicitly
includes `rel="noopener noreferrer"`. Review all custom render hooks
(`_markup/*.html`) during security audits as they often bypass standard theme
logic.

## 2026-01-21 - Missing Subresource Integrity (SRI) for External Scripts

**Vulnerability:** The template `layouts/slide/single.html` loaded external
Reveal.js resources from `cdnjs` without Subresource Integrity (SRI) hashes.
This meant that if the CDN were compromised or the files tampered with,
malicious code could be injected into the presentation slides.

**Learning:** Managing SRI hashes manually for external resources is error-prone
and tedious. Hugo's `resources.GetRemote` combined with `fingerprint` allows us
to fetch external assets during the build process, generate their hashes
automatically, and serve them from our own domain (or just use the hash). This
provides the security of SRI without the maintenance burden of manual manual
hash updates.

**Prevention:** Instead of hardcoding external URLs and hashes, use
`resources.GetRemote <url> | fingerprint`. This ensures the asset is verified at
build time and the correct integrity hash is always used.

## 2026-01-22 - Argument Injection and Protocol Policy in Base16 Updater

**Vulnerability:** The `content/utils/base16/update_data.py` script passed the
`repo_url` (derived from an external YAML list) directly to
`subprocess.run(['git', 'clone', ...])`. If the YAML source were compromised to
include a "URL" starting with `-`, `git clone` would interpret it as an option
(Argument Injection), potentially leading to command execution (e.g. via
`--upload-pack`). Additionally, there was no restriction on the protocol,
allowing potentially dangerous schemes like `ssh://` or `file://`.

**Learning:** When invoking shell commands with user-controlled or external
input, always assume the input might be interpreted as a flag. Python's
`subprocess` module avoids shell injection when using a list of arguments, but
it does _not_ prevent argument injection into the called program itself.

**Prevention:**

1. **Protocol Whitelisting:** Enforce strictly expected protocols (e.g.,
   `https://` only) to reduce the attack surface.
2. **Argument Separation:** Use the `--` separator (e.g., `git clone -- <url>`)
   to explicitly tell the command that subsequent arguments are positional,
   preventing them from being interpreted as options.
