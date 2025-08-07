const { defineConfig } = require('eslint/config');
const js = require('@eslint/js');
const globals = require('globals');
const pluginImport = require('eslint-plugin-import');
const pluginPrettierRecommended = require('eslint-plugin-prettier/recommended');

module.exports = defineConfig([
  js.configs.recommended,
  pluginImport.flatConfigs.recommended,
  {
    languageOptions: {
      ecmaVersion: 'latest',
      globals: {
        ...globals.node,
      },
    },
    rules: {
      'no-console': 'warn',
      'no-alert': 'warn',
    },
  },
  pluginPrettierRecommended,
]);
