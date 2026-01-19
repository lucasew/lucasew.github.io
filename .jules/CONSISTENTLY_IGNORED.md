# Consistently Ignored Changes

This file lists patterns of changes that have been consistently rejected by
human reviewers. All agents MUST consult this file before proposing a new
change. If a planned change matches any pattern described below, it MUST be
abandoned.

---

## IGNORE: Alternative Command Injection Fixes in update.sh

**- Pattern:** Do not propose alternative fixes for the command injection
vulnerability in the `update.sh` script, particularly those involving
`find ... -exec` or complex shell manipulations that were present in PRs #119,
#117, and #116. **- Justification:** The command injection vulnerability was a
valid finding. However, multiple pull requests attempting to fix it were closed
because a preferred solution was merged in PR #120. This solution uses
`git ls-files` to securely find and iterate over tracked files, which was deemed
the correct approach. Future work should align with this established pattern.
**- Files Affected:** `update.sh`

---

## IGNORE: Adding Checksum Verification to Update Scripts

**- Pattern:** Do not add checksum (e.g., SHA256) verification to the
self-hosted library update scripts. **- Justification:** PR #122, which
introduced this change for the htmx script, was rejected. While checksums can
enhance security against supply chain attacks, the maintenance overhead of
updating hashes for every library update is not desired for this project. The
project prioritizes simplicity here. **- Files Affected:** Any
`assets/**/update_*` script.

---

## IGNORE: Hardening CI/CD Permissions by Separating Jobs

**- Pattern:** Do not refactor the CI/CD pipeline to separate jobs or tighten
permissions as a security hardening measure. **- Justification:** PR #123
attempted to separate build and release jobs to reduce the scope of permissions
for each step. This change was rejected. The project owner prefers the current,
simpler CI/CD configuration and does not consider this change a priority. **-
Files Affected:** `.github/workflows/autorelease.yaml`

---

## IGNORE: Centralizing Tailwind CSS Plugin Configuration

**- Pattern:** Do not move all Tailwind CSS plugins into the central
`tailwind.config.ts` file. **- Justification:** This change was proposed in PR
#129 and rejected. The project intentionally uses a decentralized approach where
some plugins (e.g., `@tailwindcss/typography`) are loaded via `@plugin`
directives directly in CSS files (`assets/input.css`), while others are
configured in `tailwind.config.ts`. This architectural choice is deliberate and
should be respected. **- Files Affected:** `tailwind.config.ts`,
`assets/input.css`

---

## IGNORE: Disabling Unsafe Markdown Rendering

**- Pattern:** Do not set `markup.goldmark.renderer.unsafe = false` in the Hugo
configuration. **- Justification:** This change was proposed in PR #134 to
mitigate an XSS vulnerability but was rejected. Disabling this setting is a
breaking change, as some blog posts rely on raw HTML to render custom components
(e.g., a timeline). The project accepts this risk to maintain existing content.
**- Files Affected:** `hugo.toml`

---

## IGNORE: Adding HSTS Security Header

**- Pattern:** Do not add the `Strict-Transport-Security` (HSTS) header. **-
Justification:** This change has been proposed multiple times and rejected. It
is considered an operational risk because it can break subdomains that do not
support HTTPS. This is a classic example of a security enhancement that, while
good in theory, is a breaking change in this specific context. **- Files
Affected:** `src/hooks.server.ts`, `vercel.json`

---
