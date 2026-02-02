import { defineConfig, loadEnv } from 'vite';
import { fileURLToPath } from 'url';
import { readFileSync } from 'fs';
import { resolve, dirname } from 'path';
import * as glob from 'glob';
import vue from '@vitejs/plugin-vue';
import virtual from '@rollup/plugin-virtual';
import scssFunctions from './scss-functions.js';

if (!process.env.VITE_PARLASSETS_URL) {
  throw new Error('process.env.VITE_PARLASSETS_URL is not defined!');
}

const dir = dirname(fileURLToPath(import.meta.url));
const root = resolve(dir, '..');

const isSSR = Boolean(process.env.SSR);
const entryFile = isSSR ? 'card-entry-server.js' : 'card-entry-client.js';
const entrySource = readFileSync(resolve(dir, entryFile), 'utf-8');

const files = glob.sync('./cards/**/card.vue');

const inputs = files.reduce((acc, file) => {
  const cardName = file.split('/').slice(-3, -1).join('/');
  acc[cardName] = cardName;
  return acc;
}, {});

const virtuals = files.reduce((acc, file) => {
  const cardName = file.split('/').slice(-3, -1).join('/');
  acc[cardName] = entrySource
    .replace(/{cardName}/g, cardName)
    .replace(/{sentryDsn}/g, process.env.SENTRY_DSN || '')
    .replace(/{sentryEnv}/g, process.env.SENTRY_ENVIRONMENT || '');
  return acc;
}, {});

// TODO: this is a hack to ssr render v-t and i18n component
//       replace this stub with actual plugin/implementation
const ssrTransformCustomDir = () => {
  return {
    props: [],
    needRuntime: true,
  };
};

export default defineConfig(({ mode }) => {
  Object.assign(process.env, loadEnv(mode, root));
  return {
    clearScreen: false,
    root,
    build: {
      sourcemap: true,
      manifest: true,
      assetsDir: '',
      rollupOptions: {
        input: inputs,
        output: {
          entryFileNames: isSSR ? '[name].js' : '[name].[hash].js',
          chunkFileNames: isSSR ? '[name].js' : '[name].[hash].js',
        },
      },
    },
    plugins: [
      vue({
        template: {
          compilerOptions: {
            directiveTransforms: {
              t: ssrTransformCustomDir,
              'infinite-scroll': ssrTransformCustomDir,
              'click-outside': ssrTransformCustomDir,
            },
          },
        },
      }),
      virtual(virtuals),
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
  };
});
