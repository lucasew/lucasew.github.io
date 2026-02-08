import globals from "globals";
import pluginJs from "@eslint/js";
import eslintConfigPrettier from "eslint-config-prettier";
import prettierPlugin from "eslint-plugin-prettier";

export default [
  {
    ignores: [
      "assets/*.js",
      "public/",
      "resources/",
      "content/utils/base16/*.js",
    ],
  },
  { languageOptions: { globals: globals.browser } },
  pluginJs.configs.recommended,
  eslintConfigPrettier,
  {
    plugins: {
      prettier: prettierPlugin,
    },
    rules: {
      "prettier/prettier": "error",
      "no-unused-vars": "warn",
      "no-undef": "off", // Global variables are common in simple scripts or handled by other means
    },
  },
];
