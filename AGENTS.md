# Agent Instructions

## Hugo Configuration: `unsafe` HTML Rendering

The setting `[markup.goldmark.renderer] unsafe = true` in `hugo.toml` is intentionally enabled. This allows for the use of raw HTML to create interactive elements within Markdown content.

This design choice has been reviewed, and the project owner has accepted the associated security risk, as the `content/` directory is under their full control. Future security agents should not disable this setting without explicit instruction, as doing so will break intentional functionality.
