# Agent Instructions

This is a multilingual (English/Portuguese) Hugo-based blog.

## Security Note

Security headers are not a priority as there is no dynamic content or user data.

## Environment & Commands

- **Setup**: `mise install` (tools) && `mise run install` (dependencies)
- **Dev**: `hugo server` (http://localhost:1313)
- **Build**: `mise run build`
- **Lint**: `mise run lint`
- **Format**: `mise run fmt`
- **Maintenance**: `mise run codegen` (runs `./update.sh`)

## Architecture

- **Structure**: `content/post/YYYYMMDD-slug/index.{en,pt}.md`
- **Dates**: Derived from directory names via `content/post/update_dates.py`.
- **Shortcodes**: `eval` (dynamic Hugo templates), `details` (collapsible).
- **Layouts**: `utils_base16` (theme browser), `utils_home`, `slide`.
- **Base16**: Themes generated via `content/utils/base16/update_data.py`.

## Important Notes

- **Hugo Version**: Must match in `mise.toml` and `vercel.json`. mise.toml takes
  precedence.
- **Goldmark**: Unsafe mode is enabled for raw HTML.
- **CI/CD**: GitHub Actions (`.github/workflows/autorelease.yaml`) runs
  `mise run codegen` and `mise run ci`.
