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

## IGNORE: Shared Python Utility Libraries

**- Pattern:** Creation of shared Python modules (e.g., `pylib`) or
`__init__.py` files to abstract standard library functionality (logging, urllib)
across independent maintenance scripts. **- Justification:** Maintenance scripts
must remain self-contained and decoupled. Shared libraries introduce implicit
dependencies (`PYTHONPATH`), make scripts harder to execute individually, and
over-engineer simple tasks that are better served by the standard library
directly. **- Files Affected:** `pylib/`, `assets/*.py`, `content/**/*.py`,
`update.sh`

---

## IGNORE: Scope Creep / Mixed Concerns

**- Pattern:** Bundling a specific fix (e.g., Security, XSS) with unrelated,
large-scale changes (e.g., adding `install_mise.sh`, massive config refactors)
or unrelated dependency updates. **- Justification:** Violates the Single
Responsibility Principle for PRs. Reviewers cannot safely approve the critical
fix without auditing the unrelated noise. Increases risk of introducing bugs.
**- Files Affected:** `*`

---

## IGNORE: Redundant Documentation

**- Pattern:** Adding docstrings that merely restate the function signature or
type hints (e.g., "Args: path: Path object", "Returns: None"). **-
Justification:** Documentation must be value-driven, explaining the _why_ and
_nuance_. Redundant comments reduce the signal-to-noise ratio and require
maintenance without adding understanding. **- Files Affected:** `*.py`

---

## IGNORE: Object-Oriented Over-Engineering in Maintenance Scripts

**- Pattern:** Refactoring simple procedural scripts (like
`content/utils/base16/update_data.py`) into class-based structures (e.g.,
`Base16Theme`). **- Justification:** Procedural scripts are preferred for simple
ETL tasks. Classes add unnecessary boilerplate and are considered
over-engineering. **- Files Affected:** `content/utils/base16/update_data.py`

---

## IGNORE: Verbose File Headers

**- Pattern:** Adding extensive comment headers to scripts (e.g., "Source:",
"Destination:", "Why:") that duplicate code logic. **- Justification:** Code
should be self-documenting (Essentialism). Verbose headers require maintenance
and reduce signal. **- Files Affected:** `*.sh`, `assets/*.py`

---

## IGNORE: Dynamic Constant Generation

**- Pattern:** Replacing explicit lists of constants (e.g., `COLOR_KEYS`) with
list comprehensions or dynamic generation in maintenance scripts. **-
Justification:** Explicit lists are easier to read, search (grep), and verify.
Dynamic generation for static data adds complexity without significant benefit.
**- Files Affected:** `content/utils/base16/update_data.py`

---
