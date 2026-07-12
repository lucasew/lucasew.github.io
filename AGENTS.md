# Agent Instructions

Multilingual (English/Portuguese) Astro blog.

## Security Note

Security headers are not a priority as there is no dynamic content or user data.

## Environment & Commands

- **Setup**: `mise install` then `npm install`
- **Dev**: `npm run dev` (`astro dev`, http://localhost:4321)
- **Build**: `npm run build` (`astro build` → `public/`)
- **Preview**: `npm run preview`
- **Format**: `dprint fmt` or `npm run format`
- **Maintenance**: `./update.sh` or `mise codegen` (runs executable
  `**/update_*` scripts)

## Architecture

- **Posts**: `src/content/post/YYYYMMDD-slug/index.{en,pt}.{md,mdx}`
- **Dates**: Directory name prefix via `src/content/post/update_dates.py`
- **Collections**: `src/content.config.ts` (glob loader for posts)
- **Key dirs**: `src/pages/`, `src/layouts/`, `src/lib/`, `src/components/`
- **Static assets**: `static/` (Astro `publicDir`) → site root
- **i18n**: `en` / `pt` (`src/lib/i18n.ts`, `i18n/*.yaml`)

## Important Notes

- **Node**: version from `mise.toml` (`node` tool only)
- **CI/CD**: `.github/workflows/autorelease.yaml` — `npm install`,
  `mise codegen`, `npm run build`, deploy Pages on `main`
- **Site URL**: `https://lucasew.github.io` (`astro.config.mjs` / Vercel
  `public` output)
