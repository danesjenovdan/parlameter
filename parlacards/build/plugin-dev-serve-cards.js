import { existsSync, readFileSync } from 'fs';
import { resolve, dirname, join } from 'path';
import { fileURLToPath } from 'url';
import * as glob from 'glob';
import { groupBy, mapValues } from 'lodash-es';

const dir = dirname(fileURLToPath(import.meta.url));
const cardsPath = resolve(dir, '..', 'cards');

export default function devServeCards(env) {
  return {
    name: 'dev-serve-cards',
    configureServer(server) {
      server.middlewares.use((req, res, next) => {
        const url = new URL(req.url, `http://${req.headers.host}/`);
        const pathname = url.pathname.replace(/\/$/, '');
        if (pathname === '') {
          const cards = glob
            .sync(join(cardsPath, '**/card.vue'))
            .map((file) => file.split('/').slice(-3, -1));
          const cardsByGroup = mapValues(
            groupBy(cards, ([g]) => g),
            (v) => v.map(([, m]) => m),
          );
          const cardRows = Object.entries(cardsByGroup)
            .map(
              ([group, methods]) => `
              <table style="margin: 0 auto; border-collapse: collapse; display: inline-block;">
                ${methods
                  .map(
                    (method) => `
                    <tr>
                      <td style="border: 1px solid black;">${group}</td>
                      <td style="border: 1px solid black;"><a href="/${group}/${method}">${method}</a></td>
                    </tr>`,
                  )
                  .join('\n')}
              </table>`,
            )
            .join('\n');
          res.end(cardRows);
        } else if (pathname.slice(1).split('/').length === 2) {
          const [group, method] = pathname.slice(1).split('/');
          const cardName = `${group}/${method}`;
          if (existsSync(join(cardsPath, cardName, 'card.vue'))) {
            const html = readFileSync(
              // TODO: uredi, da lahko developas razlicne template (embed/share/site)
              resolve(dir, 'card-entry-dev.html'),
              'utf-8',
            )
              .replace(/{assetsUrl}/g, env.VITE_PARLASSETS_URL)
              .replace(/{cardName}/g, cardName)
              .replace(
                /{cardEntry}/g,
                `/${cardName}/card-entry-dev.js${url.search}`,
              );
            server
              .transformIndexHtml(`${cardsPath}/${cardName}/index.html`, html)
              .then((transformedHtml) => {
                res.end(transformedHtml);
              })
              .catch((error) => res.status(500).send(error));
          } else {
            next();
          }
        } else {
          next();
        }
      });
    },
    resolveId(id) {
      if (id.includes('/card-entry-dev.js')) {
        return join(cardsPath, id.slice(1));
      }
      return undefined;
    },
    load(id) {
      if (id.includes('/card-entry-dev.js')) {
        const [path, search] = id.split('?');
        const [group, method] = path.split('/').slice(-3, -1);
        const cardName = `${group}/${method}`;
        if (existsSync(join(cardsPath, cardName, 'card.vue'))) {
          const searchParams = new URLSearchParams(search);
          const entryTemplate = readFileSync(
            resolve(dir, 'card-entry-dev.js'),
            'utf-8',
          );
          return entryTemplate
            .replace(/{cardName}/g, cardName)
            .replace(/{cardLang}/g, searchParams.get('locale') || 'sl');
        }
      }
      return undefined;
    },
  };
}
