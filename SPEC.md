# Dev-mode post editor

Reference for the in-browser post editor that runs in `astro dev` only.
The reader is the person (or agent) who implements v1.
After you read this file, implement v1 without adding scope.

Production is static GitHub Pages. The editor and the write endpoint
must not appear in `pnpm build` output.

## Terminology

| Concept | Term | Do not use |
| --- | --- | --- |
| On-disk post location | post directory | folder, slug dir |
| Markdown or MDX file | source file | document, note |
| Block editor with `/` commands | slash editor | Notion editor, block editor, CMS |
| Plain textarea for MDX | source editor | raw mode, fallback |
| HTTP handler that writes files | write endpoint | API, save route, admin API |
| Clipboard or file drop into the editor | paste | upload, import |
| Unsaved editor state | dirty | pending, modified |

## Out of scope for v1

Do not implement these in v1. Edit the source file by hand, or do them later.

- Add a translation of an existing post
- Delete a post
- Rename a slug
- Change the date prefix on the post directory
- Footnotes or Hugo shortcodes in the slash menu
- Git commit or push from the browser
- Authentication or any production CMS

## Entry points

The published post is the default view in `astro dev`.

On a post page (`/{lang}/post/{YYYYMMDD-slug}/`), the navbar shows a pencil
icon. The pencil sets `?edit=1` and opens the editor for that source file.

On the post list (`/{lang}/post/`), the navbar or list chrome shows a `+`
control. The `+` control starts create-post.

Do not put the pencil on utils, slides, or other non-post pages.

## Create a post

Create writes one language. The language is the language of the page that
shows the `+` control. Do not create an empty source file in the other language.

Create asks for a title only.

1. Build a slug from the title (lowercase, hyphens, ASCII-safe).
2. Use today's date as `YYYYMMDD`.
3. Create `src/content/post/YYYYMMDD-slug/`.
4. Write `index.{lang}.md` with `title` in frontmatter and an empty body.
5. Open `/{lang}/post/YYYYMMDD-slug/?edit=1`.

The post date always comes from the `YYYYMMDD` prefix of the post directory.
Do not write a `date:` field in frontmatter.

If the post directory already exists, do not overwrite it. Change the slug
or report the clash.

## Open the editor

If the query string contains `edit=1`, open the editor instead of the
published body. Keep `edit=1` on refresh so debounce save does not kick
the author out.

Choose the editor from the source file suffix:

| Source file | Editor |
| --- | --- |
| `index.{lang}.md` | slash editor |
| `index.{lang}.mdx` | source editor |

The source editor shows the file text. It must not run a block serializer
on save. A serializer can drop MDX `import` lines and JSX.

## Slash editor library

The slash editor is `@milkdown/crepe` (MIT). Do not write a custom block editor.

Crepe is vanilla JS. This repo has no React. Give it Markdown. Read Markdown
back with `getMarkdown()`. Listen with `markdownUpdated` for debounce save.

The milkdown.dev homepage editor turns `Crepe.Feature.BlockEdit` off, so the
slash menu is missing there. A default Crepe instance keeps `BlockEdit` on.
Keep it on. Do not copy the homepage feature flags.

Leave `Table`, `Latex`, and `TopBar` on. `Table` and `Latex` are on by
default. `TopBar` is off by default. Turn it on. Leave `AI` off.
Drop `TopBar` later if the extra strip is noise.

Open the insert menu in either of these ways:

- Type `/` at the start of a paragraph or heading.
- Click the `+` handle on the left of a block.

The menu does not open inside a code block or a list. That is Crepe behavior.

Wire `ImageBlock.onUpload` to the write endpoint. Do not keep blob URLs.

Load `@milkdown/crepe` only in `astro dev`. It must stay out of `pnpm build`.

## Slash editor

The slash editor is a Notion-like surface that writes Markdown.

The slash menu contains these blocks:

- heading
- list
- code
- quote
- image
- divider
- table
- math (LaTeX)

Bold, italic, and link are inline selection actions. They are not slash items.

The slash editor must round-trip common Markdown without eating it:
paragraphs, headings, lists, fenced code, quotes, images, links,
thematic breaks, GFM tables, and `$` / `$$` LaTeX.

Post pages use Astro `render()`. GFM tables already work there. LaTeX
does not. Add remark-math (or the Astro equivalent) so a saved `$…$`
block looks the same on the published page as it does in Crepe.

If the source file contains Markdown the serializer cannot own, do not
open the slash editor. Open the source editor instead. Do not rewrite
the file in that case.

## Frontmatter

The editor can change these keys only:

- `title` (string)
- `summary` (string)
- `discussedOn` (list of URL strings)
- `alsoAvailable` (list of URL strings)

Title and summary fields are at the top of the editor. `discussedOn`
and `alsoAvailable` use an "add URL" control. Do not expose a YAML editor.

Any other frontmatter key must stay in the source file unchanged.
Examples that exist in the tree today: `aliases`, `math`, `showToc`,
`language`.

## Images

Paste is the primary way to add an image. A slash `/image` item may
also open a file picker. Both paths use the same write rules.

Write the image file into the post directory of the open source file.

| Paste payload | Filename |
| --- | --- |
| Has a real filename (Finder file, and more) | Keep that basename |
| Clipboard screenshot with no useful name | `paste-YYYYMMDD-HHMMSS.png` |

If that name already exists in the post directory, append `-2`, `-3`,
and so on. Never overwrite an existing image file.

Do not convert the image format. Insert a Markdown image that points
at that basename. Alt text may be empty. The author can edit alt text
in the source file later.

Do not write `astro:assets` imports. Those belong in MDX, which the
slash editor does not own.

## Save

Debounce save: after the author stops typing, write the source file
on disk. About one second is enough.

Write the full source file: frontmatter plus body. Preserve unknown
frontmatter keys.

Git dirty state is acceptable. The author commits on the command line.

The published Astro page is the faithful preview after the write.
The editor must survive the HMR reload that follows a write, or the
author loses the cursor and dirty state.

## Write endpoint

Register a write endpoint only when `astro dev` is running.

The write endpoint may create or update files only under
`src/content/post/`. Reject any path that resolves outside that tree.

Allowed writes:

- create a new post directory
- create or replace `index.{lang}.md` in that directory
- create a new image file in that directory
- replace `index.{lang}.mdx` only from the source editor (byte-for-byte
  text save, no serializer)

Do not delete files through the write endpoint in v1.

Do not ship the write endpoint or the editor client in `pnpm build`.
A static host has no server, but the editor JavaScript must also stay
out of the production bundle.

No login. The endpoint is local `astro dev` only.

## Layout of a post

```
src/content/post/YYYYMMDD-slug/
  index.en.md      # or index.pt.md; one language on create
  some-image.png   # optional; referenced as ![](some-image.png)
```

An MDX post uses `index.{lang}.mdx` and may contain JSX. The slash
editor must not own that file.

## Success

v1 is complete when these checks pass in `mise run dev`:

1. A post page shows a pencil. The post list shows `+`. Neither appears
   after `pnpm build`.
2. `+` creates one `index.{lang}.md` and opens `?edit=1`.
3. The slash editor can edit an existing `.md` post and debounce-write
   the source file. Title, summary, and the two URL lists persist.
4. Paste of a screenshot creates `paste-*.png` in that post directory
   and inserts a Markdown image that points at that file.
5. Opening `20251118-acionando-fgc` (`index.pt.mdx`) uses the source
   editor. A save does not strip the `import` lines or the JSX.
