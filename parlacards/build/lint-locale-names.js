import fs from 'fs';
import path from 'path';
import * as glob from 'glob';

const cardNames = glob
  .sync('./cards/**/card.vue')
  .map((file) => file.split('/').slice(-3, -1).join('/'));

const localeNames = glob
  .sync('./cards/_i18n/*/')
  .map((dir) => dir.split('/').slice(-2, -1).join('/'));

let missingLocaleFiles = 0;

localeNames.forEach((localeName) => {
  const defaultsLocaleFile = path.resolve(
    `./cards/_i18n/${localeName}/defaults.yaml`,
  );
  if (!fs.existsSync(defaultsLocaleFile)) {
    // eslint-disable-next-line no-console
    console.error(`MISSING LOCALE FILE: ${defaultsLocaleFile}`);
    missingLocaleFiles += 1;
  }

  cardNames.forEach((cardName) => {
    const cardLocaleFile = path.resolve(
      `./cards/_i18n/${localeName}/${cardName}.yaml`,
    );
    if (!fs.existsSync(cardLocaleFile)) {
      // const newDirName = path.dirname(cardLocaleFile);
      // if (!fs.existsSync(newDirName)) {
      //   fs.mkdirSync(newDirName);
      // }
      // fs.writeFileSync(cardLocaleFile, '', 'utf-8');

      // eslint-disable-next-line no-console
      console.error(`MISSING LOCALE FILE: ${cardLocaleFile}`);
      missingLocaleFiles += 1;
    }
  });
});

const localeFiles = glob.sync('./cards/_i18n/**', { nodir: true });

let extraLocaleFiles = 0;

localeFiles.forEach((localeFile) => {
  const possibleCardName = localeFile
    .replace(/^\.\/cards\/_i18n\//, '')
    .replace(new RegExp(`^(${localeNames.join('|')})/`), '')
    .replace(/\.yaml$/i, '');

  if (
    !cardNames.includes(possibleCardName) &&
    possibleCardName !== 'defaults' &&
    possibleCardName !== 'd3locales.js'
  ) {
    // const cardLocaleFile = path.resolve(localeFile);
    // if (possibleCardName.includes('tool/')) {
    //   const newCardLocaleFile = cardLocaleFile.replace('tool/', 'tools/');
    //   const newDirName = path.dirname(newCardLocaleFile);
    //   if (!fs.existsSync(newDirName)) {
    //     fs.mkdirSync(newDirName);
    //   }
    //   fs.renameSync(cardLocaleFile, newCardLocaleFile);
    // }

    // eslint-disable-next-line no-console
    console.error(
      `EXTRA LOCALE FILE (no card "${possibleCardName}"): ${path.resolve(
        localeFile,
      )}`,
    );
    extraLocaleFiles += 1;
  }
});

const allErrors = missingLocaleFiles + extraLocaleFiles;

if (allErrors > 0) {
  // eslint-disable-next-line no-console
  console.error(`\nLOCALE FILE NAME ERRORS: ${allErrors}\n`);
  process.exit(1);
} else {
  // eslint-disable-next-line no-console
  console.log(`\nNO LOCALE FILE NAME ERRORS\n`);
}
