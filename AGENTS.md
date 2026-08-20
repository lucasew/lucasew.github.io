# Agent Instructions

Multilingual (English/Portuguese) Astro blog.

## Security Note

Security headers are not a priority as there is no dynamic content or user data.

## Environment & Commands

- **Setup**: `mise install` then `mise run install`
- **Dev**: `mise run dev` (`astro dev`, http://localhost:4321)
- **Build**: `pnpm build` (`astro build` → `public/`)
- **Preview**: `pnpm preview`
- **Format**: `dprint fmt` or `pnpm format`
- **Maintenance**: `./update.sh` or `mise codegen` (runs executable
  `**/update_*` scripts)

## Architecture

- **Posts**: `src/content/post/YYYYMMDD-slug/index.{en,pt}.{md,mdx}`
- **Dates**: Always from `YYYYMMDD` prefix of `src/content/post/<dir>/` in
  `contentLoader` (no frontmatter `date:`)
- **Collections**: `src/content.config.ts` (glob loader for posts)
- **Key dirs**: `src/pages/`, `src/layouts/`, `src/lib/`, `src/components/`
- **Static assets**: `static/` (Astro `publicDir`) → site root
- **i18n**: `en` / `pt` (`src/lib/i18n.ts`)

## Important Notes

- **Node**: versions from `mise.toml` (`node`, `pnpm`)
- **CI/CD**: `.github/workflows/autorelease.yaml` — `pnpm install --frozen-lockfile`,
  `mise codegen`, `pnpm build`, deploy Pages on `main`
- **Site URL**: `https://lucasew.github.io` (`astro.config.mjs` / Vercel
  `public` output)
