import fs from 'fs';
import path from 'path';
import * as glob from 'glob';
import { camelCase, upperFirst } from 'lodash-es';

const FIX_NAMES = process.argv.includes('--fix');

const cardNames = glob
  .sync('./cards/**/card.vue')
  .map((file) => file.split('/').slice(-3, -1).join('/'));

const componentNames = glob
  .sync('./cards/_components/**/*.vue')
  .map((file) => file.split('/').slice(2).join('/'));

let missingComponentNames = 0;
let wrongComponentNames = 0;

function checkComponentName(componentFile, correctComponentName) {
  const compFileText = fs.readFileSync(componentFile, 'utf-8');
  const matchExport = compFileText.match(/export default {\n/);
  const match = compFileText.match(/\s{2}name:\s'(?<name>.*)',/);
  if (match?.groups?.name) {
    if (match.groups.name !== correctComponentName) {
      if (FIX_NAMES) {
        const textBefore = compFileText.slice(0, match.index);
        const textAfter = compFileText.slice(match.index + match[0].length);
        const newFileText = `${textBefore}  name: '${correctComponentName}',${textAfter}`;
        fs.writeFileSync(componentFile, newFileText, 'utf-8');
      } else {
        // eslint-disable-next-line no-console
        console.error(
          `WRONG COMPONENT NAME "${match.groups.name}" !== "${correctComponentName}": ${componentFile}`,
        );
        wrongComponentNames += 1;
      }
    }
  } else if (FIX_NAMES && matchExport) {
    const insertIndex = matchExport.index + matchExport[0].length;
    const textBefore = compFileText.slice(0, insertIndex);
    const textAfter = compFileText.slice(insertIndex);
    const newFileText = `${textBefore}  name: '${correctComponentName}',\n${textAfter}`;
    fs.writeFileSync(componentFile, newFileText, 'utf-8');
  } else if (compFileText.includes('<script')) {
    // eslint-disable-next-line no-console
    console.error(`MISSING COMPONENT NAME: ${componentFile}`);
    missingComponentNames += 1;
  }
}

cardNames.forEach((cardName) => {
  const correctComponentName = `Card${upperFirst(camelCase(cardName))}`;
  const componentFile = path.resolve(`./cards/${cardName}/card.vue`);
  checkComponentName(componentFile, correctComponentName);
});

componentNames.forEach((componentName) => {
  const correctComponentName = `${upperFirst(camelCase(componentName.replace('.vue', '')))}`;
  const componentFile = path.resolve(`./cards/_components/${componentName}`);
  checkComponentName(componentFile, correctComponentName);
});

const allErrors = missingComponentNames + wrongComponentNames;

if (allErrors > 0) {
  // eslint-disable-next-line no-console
  console.error(`\nCOMPONENT NAME ERORRS: ${allErrors}\n`);
  process.exit(1);
} else {
  // eslint-disable-next-line no-console
  console.error(`\nNO COMPONENT NAME ERORRS\n`);
}
