const js = require("@eslint/js");
const pluginVue = require("eslint-plugin-vue");
const globals = require("globals");

module.exports = [
  {
    ignores: ["dist/**", "node_modules/**", "eslint.config.cjs"],
  },
  {
    languageOptions: {
      ecmaVersion: "latest",
      sourceType: "module",
      globals: {
        ...globals.browser,
      },
    },
  },
  js.configs.recommended,
  ...pluginVue.configs["flat/essential"],
  {
    rules: {
      "vue/multi-word-component-names": "off",
    },
  },
];
