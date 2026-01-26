# Janitor's Journal

This journal is for recording CRITICAL refactoring learnings to improve the
codebase over time.

## 2024-05-23 - Unused dependency was actually in use

**Issue:** I attempted to remove the `@tailwindcss/typography` dependency,
believing it was unused because it was not present in `tailwind.config.ts`. This
caused a build failure. **Root Cause:** My analysis was incomplete. I failed to
check for alternative plugin usage methods. The typography plugin was being
imported directly into a CSS file (`assets/input.css`) using the `@plugin`
directive, a method I had not previously encountered. **Solution:** The change
was reverted to restore the dependency. Future dependency removal analysis must
include a global search for the package name within all project files, not just
configuration scripts. **Pattern:** Tailwind CSS plugins can be loaded directly
within CSS files via directives like `@plugin`. Always perform a full repository
text search for a dependency's name before concluding it is unused.

## 2024-05-24 - Sort `devDependencies` for consistency

**Issue:** The `devDependencies` in `package.json` were not alphabetically
sorted, making the file slightly harder to read and manage. **Root Cause:**
Dependencies were likely added over time without a consistent ordering, leading
to a disorganized file. **Solution:** I alphabetically sorted the
`devDependencies` block in `package.json` and regenerated the
`package-lock.json` to match. **Pattern:** Keeping dependency lists in
`package.json` sorted alphabetically is a simple but effective practice for
maintaining code quality. It improves readability and helps prevent accidental
duplicate entries.

## 2024-05-25 - Add standard metadata to package.json

**Issue:** The `package.json` file was missing standard, high-level metadata
fields (`version`, `description`, `repository`, `author`, `license`). **Root
Cause:** The file was likely initialized without these fields being populated,
leaving it incomplete. **Solution:** I added the missing metadata fields,
deriving the values from other project files like `hugo.toml` and the
repository's context. **Pattern:** A complete `package.json` with standard
metadata makes the project more professional, easier to understand for new
contributors, and provides essential information for tooling and package
managers.

## 2026-01-17 - Remove duplicate charset meta tag

**Issue:** The `layouts/_default/baseof.html` template contained duplicate
`<meta charset>` declarations (`UTF-8` and `utf-8`), which is invalid HTML and
redundant. **Root Cause:** Likely a copy-paste error or a merge oversight where
both variations were introduced and persisted. **Solution:** Removed the
redundant `<meta charset="utf-8">` tag, keeping the uppercase version for
consistency. **Pattern:** Ensure HTML templates define the character set exactly
once. Duplicate meta tags increase page size unnecessarily and violate HTML
standards.

## 2026-01-20 - Fix greedy regex in frontmatter update script

**Issue:** The `content/post/update_dates.py` script used a greedy regex (`.*`)
to match frontmatter content. This caused it to incorrectly capture the entire
file content up to the last `---` if multiple `---` separators existed (e.g.,
horizontal rules), leading to incorrect date detection logic where a date in the
body prevented the script from updating the frontmatter. **Root Cause:** The
regex `r"^---\n(.*)\n---"` combined with `re.DOTALL` is greedy by default.
**Solution:** Changed the regex to be non-greedy `r"^---\n(.*?)\n---"` and
switched to `re.search` with span-based replacement to ensure only the actual
frontmatter is targeted. **Pattern:** When parsing delimited blocks like YAML
frontmatter with regex, always use non-greedy quantifiers (`.*?`) or explicit
anchors to prevent consuming subsequent delimiters in the file body.

## 2026-01-20 - Fix invalid HTML nesting in base template

**Issue:** The `layouts/_default/baseof.html` template had a broken HTML
structure where the `navbar-end` div opening tag was inside a `with` block, but
its closing tag was outside. This relies on the `with` block always executing to
produce balanced HTML. Additionally, the deprecated `shrink-to-fit=no` attribute
was present on the viewport meta tag. **Root Cause:** Likely a mistake when
grouping navbar elements, placing the closing `{{ end }}` tag of the `with`
block after the opening `div` tag of the next section. **Solution:** Moved the
`{{ end }}` tag to correctly close the `navbar-start` logic before the
`navbar-end` section begins. Removed the deprecated viewport attribute.
**Pattern:** Ensure HTML tags are properly balanced within template logic
blocks. Avoid splitting opening and closing tags across conditional boundaries
unless strictly necessary.

## 2026-01-26 - Remove redundant directory cleanup in base16 updater

**Issue:** The `content/utils/base16/update_data.py` script unnecessarily
deleted the temporary directory created by `tempfile.TemporaryDirectory` before
calling `git clone`, under the mistaken belief that `git clone` fails if the
directory exists. **Root Cause:** Misunderstanding of `git clone` behavior
combined with `TemporaryDirectory`. `TemporaryDirectory` creates an empty
directory, and `git clone` supports cloning into an empty directory. The code
was adding unnecessary complexity and confusion. **Solution:** Removed the
`rmdir` call and the misleading comment. Verified that `git clone` works
correctly with the empty directory provided by `TemporaryDirectory`.
**Pattern:** Avoid writing code to solve problems that don't exist ("defensive
coding" gone wrong). Trust standard library tools (like `TemporaryDirectory`) to
do their job unless proven otherwise.
