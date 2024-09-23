import fs from 'fs';
import * as glob from 'glob';
import jsYaml from 'js-yaml';
import { intersection, difference } from 'lodash-es';

function getDeepKeys(data, prefix = '', separator = '.') {
  return Object.keys(data).flatMap((key) => {
    const newKey = `${prefix}${prefix ? separator : ''}${key}`;
    if (typeof data[key] === 'object' && data[key] != null) {
      return getDeepKeys(data[key], newKey);
    }
    return newKey;
  });
}

const localeNames = glob
  .sync('./cards/_i18n/*/')
  .map((dir) => dir.split('/').slice(-2, -1).join('/'));

const allLocaleKeys = {};

localeNames.forEach((localeName) => {
  allLocaleKeys[localeName] = [];

  const localeFiles = glob.sync(`./cards/_i18n/${localeName}/**`, {
    nodir: true,
  });

  localeFiles.forEach((file) => {
    const yamlText = fs.readFileSync(file, 'utf-8');
    const data = jsYaml.load(yamlText);
    if (!data) {
      // file is empty (data is null)
      return;
    }

    const shortFile = file
      .replace(`./cards/_i18n/${localeName}/`, '')
      .replace(/\.ya?ml$/i, '');

    const keys = getDeepKeys(data, shortFile, '|');

    allLocaleKeys[localeName].push(...keys);
  });
});

const keysIncludedInAllLocales = intersection(...Object.values(allLocaleKeys));

const allLocaleMissingKeys = {};
const allLocaleExtraKeys = {};

// TODO: when there are no more ignored locales remove this
const VALID_LOCALES_FOR_NEW_KEYS = [
  'sl',
  'sl-obcina-hrastnik',
  'sl-obcina-lendava',
  'sl-obcina-ljubljana',
  'sl-obcina-ajdovscina',
];

// TODO: fix these locales and stop ignoring them
const IGNORED_LOCALES_FOR_MISSING_KEYS = ['en', 'hr', 'sh', 'pl', 'ua'];

localeNames.forEach((localeName) => {
  const extraKeys = difference(
    allLocaleKeys[localeName],
    keysIncludedInAllLocales,
  );

  allLocaleExtraKeys[localeName] = extraKeys;

  if (extraKeys.length > 0 && VALID_LOCALES_FOR_NEW_KEYS.includes(localeName)) {
    localeNames
      .filter((otherLocaleName) => otherLocaleName !== localeName)
      .forEach((otherLocaleName) => {
        const missingKeys = difference(
          extraKeys,
          allLocaleKeys[otherLocaleName],
        );

        if (
          missingKeys.length > 0 &&
          !IGNORED_LOCALES_FOR_MISSING_KEYS.includes(otherLocaleName)
        ) {
          allLocaleMissingKeys[otherLocaleName] =
            allLocaleMissingKeys[otherLocaleName] || new Set();

          missingKeys.forEach((missingKey) => {
            allLocaleMissingKeys[otherLocaleName].add(missingKey);
          });
        }
      });
  }
});

// console.log(allLocaleMissingKeys.bs);
// console.log(allLocaleExtraKeys.bs);
// const bsmissing = allLocaleMissingKeys['bs'];
// fs.writeFileSync('./bsmiggins.txt', Array.from(bsmissing).join('\n'), 'utf-8');

// if (missingKeysCount > 0) {
//   // eslint-disable-next-line no-console
//   console.error(`\nMISSING LOCALE KEYS: ${missingKeysCount}\n`);
//   process.exit(1);
// } else {
//   // eslint-disable-next-line no-console
//   console.log(`\nNO MISSING LOCALE KEYS\n`);
// }
