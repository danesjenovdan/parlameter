import fs from 'fs';
import path from 'path';
import * as glob from 'glob';
import { camelCase, upperFirst } from 'lodash-es';

const FIX_NAMES = process.argv.includes('--fix');

const cardNames = glob
  .sync('./cards/**/card.vue')
  .map((file) => file.split('/').slice(-3, -1).join('/'));

let missingCardComponentNames = 0;
let wrongCardComponentNames = 0;

cardNames.forEach((cardName) => {
  const correctComponentName = `Card${upperFirst(camelCase(cardName))}`;
  const cardFile = path.resolve(`./cards/${cardName}/card.vue`);
  const cardFileText = fs.readFileSync(cardFile, 'utf-8');
  const matchExport = cardFileText.match(/export default {\n/);
  const match = cardFileText.match(/\s{2}name:\s'(?<name>.*)',/);
  if (match?.groups?.name) {
    if (match.groups.name !== correctComponentName) {
      if (FIX_NAMES) {
        const textBefore = cardFileText.slice(0, match.index);
        const textAfter = cardFileText.slice(match.index + match[0].length);
        const newCardFileText = `${textBefore}  name: '${correctComponentName}',${textAfter}`;
        fs.writeFileSync(cardFile, newCardFileText, 'utf-8');
      } else {
        // eslint-disable-next-line no-console
        console.error(
          `WRONG CARD COMPONENT NAME "${match.groups.name}" !== "${correctComponentName}": ${cardFile}`,
        );
        wrongCardComponentNames += 1;
      }
    }
  } else if (FIX_NAMES && matchExport) {
    const insertIndex = matchExport.index + matchExport[0].length;
    const textBefore = cardFileText.slice(0, insertIndex);
    const textAfter = cardFileText.slice(insertIndex);
    const newCardFileText = `${textBefore}  name: '${correctComponentName}',\n${textAfter}`;
    fs.writeFileSync(cardFile, newCardFileText, 'utf-8');
  } else {
    // eslint-disable-next-line no-console
    console.error(`MISSING CARD COMPONENT NAME: ${cardFile}`);
    missingCardComponentNames += 1;
  }
});

const allErrors = missingCardComponentNames + wrongCardComponentNames;

if (allErrors > 0) {
  // eslint-disable-next-line no-console
  console.error(`\nCARD COMPONENT NAME ERORRS: ${allErrors}\n`);
  process.exit(1);
} else {
  // eslint-disable-next-line no-console
  console.error(`\nNO CARD COMPONENT NAME ERORRS\n`);
}
