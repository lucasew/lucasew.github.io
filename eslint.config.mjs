import js from "@eslint/js";
import tseslint from "typescript-eslint";
import prettier from "eslint-config-prettier";

export default tseslint.config(
  js.configs.recommended,
  ...tseslint.configs.recommended,
  prettier,
  {
    ignores: [
      "public/",
      "resources/",
      "node_modules/",
      "assets/analytics.js",
      "assets/htmx.js",
      "assets/sentry.js",
    ],
  }
);
