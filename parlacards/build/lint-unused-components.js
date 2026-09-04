import fs from 'fs';
import path from 'path';
import * as glob from 'glob';

const cardsDir = path.resolve('./cards');

const compNames = glob.sync('./cards/**/*.{vue,js}');

const compNamesNoCard = compNames.filter(
  (compName) => !compName.endsWith('/card.vue'),
);

const usageCount = compNamesNoCard.reduce((acc, compName) => {
  acc[compName] = 0;
  return acc;
}, {});

compNames.forEach((compName) => {
  const compText = fs.readFileSync(compName, 'utf-8');
  const compDir = path.dirname(compName);
  compNamesNoCard.forEach((compName2) => {
    const compInclude = path.resolve(compName2).replace(cardsDir, '@');
    if (compText.includes(compInclude)) {
      usageCount[compName2] += 1;
    }
    let compRelativeInclude = path.relative(compDir, compName2);
    if (!compRelativeInclude.startsWith('.')) {
      compRelativeInclude = `./${compRelativeInclude}`;
    }
    if (compText.includes(compRelativeInclude)) {
      usageCount[compName2] += 1;
    }
  });
});

const sortedUsageCount = Object.entries(usageCount).sort((a, b) => b[1] - a[1]);
const unusedComponents = sortedUsageCount
  .filter(([, count]) => count === 0)
  .map(([compName]) => compName);

if (unusedComponents.length === 0) {
  // eslint-disable-next-line no-console
  console.log('No unused components found.');
} else {
  // eslint-disable-next-line no-console
  console.log(`Found unused components: \n  ${unusedComponents.join('\n  ')}`);
  process.exit(1);
}
