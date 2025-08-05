import { defineConfig, globalIgnores } from 'eslint/config';
import js from '@eslint/js';
import globals from 'globals';
import pluginImport from 'eslint-plugin-import';
import pluginPrettierRecommended from 'eslint-plugin-prettier/recommended';
import pluginVue from 'eslint-plugin-vue';

export default defineConfig([
  js.configs.recommended,
  pluginImport.flatConfigs.recommended,
  ...pluginVue.configs['flat/recommended'],
  globalIgnores(['dist/']),
  {
    languageOptions: {
      ecmaVersion: 'latest',
      sourceType: 'module',
      globals: {
        ...globals.browser,
        ...globals.node,
      },
    },
    rules: {
      'no-console': 'warn',
      'no-alert': 'warn',
      'vue/multi-word-component-names': ['off'],
      'import/extensions': ['error', 'always', { ignorePackages: true }],
      'import/no-extraneous-dependencies': [
        'error',
        {
          optionalDependencies: false,
          devDependencies: ['build/**', 'eslint.config.js'],
        },
      ],
    },
    settings: {
      'import/resolver': {
        alias: [
          ['@', './cards'],
          ['parlassets', './parlassets'],
        ],
      },
    },
  },
  pluginPrettierRecommended,
]);
