import { defineConfig, loadEnv } from 'vite';
import { fileURLToPath } from 'url';
import { resolve, dirname } from 'path';
import yaml from '@rollup/plugin-yaml';
import vue from '@vitejs/plugin-vue';
import devServeCards from './plugin-dev-serve-cards.js';
import scssFunctions from './scss-functions.js';
import { processLocaleMarkdown } from './process-locale-markdown.js';

if (!process.env.VITE_PARLASSETS_URL) {
  process.env.VITE_PARLASSETS_URL = 'http://localhost:8080';
}

const dir = dirname(fileURLToPath(import.meta.url));
const root = resolve(dir, '..');

export default defineConfig(({ mode }) => {
  Object.assign(process.env, loadEnv(mode, root));
  return {
    clearScreen: false,
    root,
    plugins: [
      yaml({
        transform(data) {
          return processLocaleMarkdown(data ?? {});
        },
      }),
      vue(),
      devServeCards(process.env),
    ],
    resolve: {
      alias: {
        '@': resolve(root, 'cards'),
        parlassets: resolve(root, '..', 'parlassets', 'src'),
      },
    },
    css: {
      preprocessorOptions: {
        scss: {
          api: 'modern-compiler',
          functions: scssFunctions,
        },
      },
    },
    server: {
      port: process.env.VITE_PORT || 3000,
      strictPort: true,
      host: '0.0.0.0',
    },
  };
});
