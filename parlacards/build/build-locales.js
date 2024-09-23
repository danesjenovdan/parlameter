import fs from 'fs-extra';
import jsYaml from 'js-yaml';
import * as glob from 'glob';
import { resolve, dirname, join, relative } from 'path';
import { fileURLToPath } from 'url';
import { processLocaleMarkdown } from './process-locale-markdown.js';

const dir = dirname(fileURLToPath(import.meta.url));
const localesPath = resolve(dir, '..', 'cards', '_i18n');
const outPath = resolve(dir, '..', 'dist', 'locales');

const locales = {};

glob.sync(join(localesPath, '**/*.yaml')).forEach((file) => {
  const fileParts = relative(localesPath, file).split('/');
  const cardName = fileParts.slice(1).join('/').replace('.yaml', '');
  const locale = fileParts[0];
  const yamlText = fs.readFileSync(file, 'utf-8');
  const data = jsYaml.load(yamlText);

  locales[locale] = locales[locale] ?? {};
  locales[locale][cardName] = data;
});

Object.keys(locales).forEach((locale) => {
  const localeData = locales[locale];

  Object.keys(localeData).forEach((cardName) => {
    localeData[cardName] = processLocaleMarkdown(localeData[cardName] ?? {});
  });

  fs.ensureDirSync(outPath);
  fs.writeJSONSync(join(outPath, `${locale}.json`), localeData);
});
