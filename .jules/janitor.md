# Janitor's Journal

This journal is for recording CRITICAL refactoring learnings to improve the codebase over time.

## 2024-05-23 - Unused dependency was actually in use
**Issue:** I attempted to remove the `@tailwindcss/typography` dependency, believing it was unused because it was not present in `tailwind.config.ts`. This caused a build failure.
**Root Cause:** My analysis was incomplete. I failed to check for alternative plugin usage methods. The typography plugin was being imported directly into a CSS file (`assets/input.css`) using the `@plugin` directive, a method I had not previously encountered.
**Solution:** The change was reverted to restore the dependency. Future dependency removal analysis must include a global search for the package name within all project files, not just configuration scripts.
**Pattern:** Tailwind CSS plugins can be loaded directly within CSS files via directives like `@plugin`. Always perform a full repository text search for a dependency's name before concluding it is unused.

## 2026-01-12 - Standardize package.json Dependency Order
**Issue:** The `devDependencies` in `package.json` were not alphabetically sorted. This is a minor inconsistency but adds friction when visually scanning or manually editing the file.
**Root Cause:** Dependencies were likely added over time without a consistent ordering convention, which is common in many projects.
**Solution:** I alphabetized the keys in the `devDependencies` object. This makes the file cleaner, easier to parse visually, and helps prevent duplicate entries in the future.
**Pattern:** Keep dependencies in `package.json` sorted alphabetically. It is a low-effort, high-impact convention that improves maintainability and signals attention to detail in the codebase.
