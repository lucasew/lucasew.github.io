# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

This is a multilingual (English/Portuguese) Hugo-based blog deployed to GitHub Pages at https://lucasew.github.io. The site features blog posts, utilities, and interactive Base16 color scheme previews.

## Development Commands

### Environment Setup
- **Install tools**: `mise install` - Sets up Hugo 0.126.1 and other dependencies
- **Check versions**: `mise list` - Verify installed tool versions

### Local Development
- **Start dev server**: `hugo server` - Starts local server at http://localhost:1313
- **Build site**: `hugo` - Generates static files to `./public` directory
- **Build for production**: `hugo --minify --baseURL https://lucasew.github.io`

### Maintenance Scripts
- **Run all updaters**: `./update.sh` - Executes all `update_*` scripts in the repository
  - `content/post/update_dates.py` - Adds missing date frontmatter to posts based on directory naming
  - `content/utils/base16/update_data.py` - Fetches and generates Base16 color scheme pages

### Formatting
- **Format markdown**: `dprint fmt` - Formats markdown files with text wrapping

## Architecture

### Content Structure

- **Multilingual setup**: Content uses Hugo's language system with `.en.md` and `.pt.md` suffixes
- **Post organization**: Posts are in `content/post/YYYYMMDD-slug/` directories containing:
  - `index.en.md` and/or `index.pt.md` for content
  - Images and assets co-located with posts
- **Date extraction**: Post dates are derived from directory names (format: `YYYYMMDD-slug`)

### Custom Hugo Features

#### Shortcodes
- **`{{< eval >}}`** (`layouts/shortcodes/eval.html`): Evaluates content as a Hugo template at render time, enabling dynamic content generation within markdown
- **`{{< details >}}`** (`layouts/shortcodes/details.html`): Creates collapsible details/summary elements

#### Custom Layouts
- **`utils_base16`**: Interactive Base16 color scheme browser with dynamic theme generation
- **`utils_home`**: Custom home page layout
- **`slide`**: Presentation/slide layout

#### Link Behavior
- **External link handling** (`layouts/_default/_markup/render-link.html`): Customizes how external links are rendered (e.g., adding target="_blank")

### Automated Update Scripts

The repository uses executable Python scripts prefixed with `update_` that are discovered and run by `update.sh`:

- **Base16 themes**: Fetches all Base16 color schemes from official repos and generates markdown pages with frontmatter containing color data
- **Post dates**: Ensures all post frontmatter includes proper date fields

These scripts run automatically in CI on a weekly schedule (Saturday 2am) and create a PR if changes are detected.

## CI/CD Pipeline

### GitHub Actions Workflow
Located at `.github/workflows/gh-pages.yaml`:

1. **Update scripts**: Runs `./update.sh` to refresh generated content
2. **PR creation**: If updaters modify files, creates "updater-bot" PR and stops deployment
3. **Build**: Runs `hugo --minify` with production baseURL
4. **Deploy**: Uploads to GitHub Pages

**Triggers**:
- Push to main branch
- Pull requests
- Manual workflow dispatch
- Weekly schedule (Saturday 2am UTC)

### Deployment
- **Platform**: GitHub Pages
- **Domain**: https://lucasew.github.io
- **Vercel config**: Also configured for Vercel deployment with Hugo 0.126.1

## Important Notes

- **Hugo version consistency**: Hugo version is managed in three places and must match:
  - `mise.toml` (local development)
  - `vercel.json` (Vercel deployment)
  - GitHub Actions uses mise.toml via `jdx/mise-action`

- **Goldmark unsafe mode**: Enabled in `hugo.toml` to allow raw HTML in markdown

- **Post naming convention**: Posts must follow `YYYYMMDD-slug` format for date extraction to work

- **Renovate bot**: Configured for automated dependency updates with default recommended config
