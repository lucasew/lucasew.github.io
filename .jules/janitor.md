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
