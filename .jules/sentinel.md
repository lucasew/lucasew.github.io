## 2024-07-22 - XSS Vulnerability in Hugo Configuration

**Vulnerability:** The Hugo configuration file `hugo.toml` had `[markup.goldmark.renderer] unsafe = true`, which allows raw HTML to be rendered from Markdown files. This creates a significant Cross-Site Scripting (XSS) vulnerability, as it would allow arbitrary HTML and script execution if a compromised post were to be added.

**Learning:** I discovered that at least one older blog post (`content/post/20210228-vivo-easy/index.pt.md`) uses raw HTML to implement a custom timeline component. Disabling the `unsafe` setting is critical for security but will break the visual rendering of this component. This highlights a project-specific pattern of embedding complex HTML directly into content.

## Instructions

* Do not modify or add HTTP headers in `vercel.json`.

## 2026-01-09 - Command Injection in `update.sh`
**Vulnerability:** The `update.sh` script used `find` to dynamically discover and execute any script matching the pattern `update_*`. This would allow an attacker to execute arbitrary code by creating a file with a matching name (e.g., `evil_update_script.sh`).
**Learning:** Dynamic script execution based on file discovery is inherently dangerous, especially in a context like a CI/CD pipeline where the script might run with elevated permissions. Utility scripts should always use an explicit, hardcoded allow-list of scripts to run. This prevents attackers from gaining code execution by simply adding a file to the repository.
**Prevention:** Future scripts that need to execute other scripts must use a non-dynamic, explicit list of targets. Avoid discovery mechanisms like `find` for execution paths. Code reviews should flag any use of dynamic execution as a potential security risk.

## 2026-01-09 - Command Injection in `update.sh`
**Vulnerability:** The `update.sh` script used `find` to dynamically discover and execute any script matching the pattern `update_*`. This would allow an attacker to execute arbitrary code by creating a file with a matching name (e.g., `evil_update_script.sh`).
**Learning:** Dynamic script execution based on file discovery is inherently dangerous, especially in a context like a CI/CD pipeline where the script might run with elevated permissions. Utility scripts should always use an explicit, hardcoded allow-list of scripts to run. This prevents attackers from gaining code execution by simply adding a file to the repository.
**Prevention:** Future scripts that need to execute other scripts must use a non-dynamic, explicit list of targets. Avoid discovery mechanisms like `find` for execution paths. Code reviews should flag any use of dynamic execution as a potential security risk.
