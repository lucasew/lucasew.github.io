## 2024-07-22 - XSS Vulnerability in Hugo Configuration

**Vulnerability:** The Hugo configuration file `hugo.toml` had `[markup.goldmark.renderer] unsafe = true`, which allows raw HTML to be rendered from Markdown files. This creates a significant Cross-Site Scripting (XSS) vulnerability, as it would allow arbitrary HTML and script execution if a compromised post were to be added.

**Learning:** I discovered that at least one older blog post (`content/post/20210228-vivo-easy/index.pt.md`) uses raw HTML to implement a custom timeline component. Disabling the `unsafe` setting is critical for security but will break the visual rendering of this component. This highlights a project-specific pattern of embedding complex HTML directly into content.

## Instructions

* Do not modify or add HTTP headers in `vercel.json`.
## 2026-01-09 - Command Injection in update.sh

**Vulnerability:** The `update.sh` script used a dynamic `find` command to locate and execute any script matching the pattern `update_*`. This created a critical command injection vulnerability, allowing an attacker with file creation privileges to execute arbitrary code by creating a malicious script with a matching name (e.g., `update_exploit.sh`).

**Learning:** The script's reliance on dynamic execution for convenience introduced a severe security risk. This indicates a potential pattern in the codebase where shell scripts might not be written with security best practices in mind. It's a reminder that even seemingly simple automation scripts can be attack vectors.

**Prevention:** To prevent similar vulnerabilities, all automation scripts must avoid executing files based on dynamic discovery. Instead, they should use hardcoded, explicit allowlists of the full paths to the intended executables. Adding `set -euo pipefail` to shell scripts also helps enforce stricter error handling and prevent unexpected behavior.
