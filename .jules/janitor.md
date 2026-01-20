# Janitor's Journal

This journal is for recording CRITICAL refactoring learnings to improve the codebase over time.

## 2024-05-23 - Unused dependency was actually in use
**Issue:** I attempted to remove the `@tailwindcss/typography` dependency, believing it was unused because it was not present in `tailwind.config.ts`. This caused a build failure.
**Root Cause:** My analysis was incomplete. I failed to check for alternative plugin usage methods. The typography plugin was being imported directly into a CSS file (`assets/input.css`) using the `@plugin` directive, a method I had not previously encountered.
**Solution:** The change was reverted to restore the dependency. Future dependency removal analysis must include a global search for the package name within all project files, not just configuration scripts.
**Pattern:** Tailwind CSS plugins can be loaded directly within CSS files via directives like `@plugin`. Always perform a full repository text search for a dependency's name before concluding it is unused.

## YYYY-MM-DD - [Title]
**Issue:** [What complexity/chaos you found]
**Root Cause:** [Why it existed]
**Solution:** [How you simplified it]
**Pattern:** [Reusable lesson for this codebase]
