import fs from 'fs-extra';
import stringify from 'html-safe-json';
import {
  loadLocale,
  loadCardModule,
  getCardDataUrl,
  fetchCardData,
  getUrls,
  fetchSiteMap,
} from './utils.js';

class HTTPError extends Error {
  constructor(statusCode, message, cause) {
    super(message);
    this.name = 'HTTPError';
    this.statusCode = statusCode;
    if (cause) {
      this.cause = cause;
    }
  }
}

const templates = {
  dev: fs.readFileSync('./build/card-template-dev.html', 'utf-8'),
  share: fs.readFileSync('./build/card-template-share.html', 'utf-8'),
  embed: fs.readFileSync('./build/card-template-embed.html', 'utf-8'),
  site: fs.readFileSync('./build/card-template-site.html', 'utf-8'),
};

const getTemplate = (templateName) => {
  if (!Object.prototype.hasOwnProperty.call(templates, templateName)) {
    throw new HTTPError(404, `Template '${templateName}' not found`);
  }

  return (replacements = {}) => {
    let template = templates[templateName];

    // eslint-disable-next-line no-restricted-syntax
    for (const [key, value] of Object.entries(replacements)) {
      template = template.replaceAll(`<!--${key}-->`, value);
    }

    return template;
  };
};

const manifest = fs.readJSONSync('./dist/client/.vite/manifest.json');

const getChunkAssets = (chunkName, seenChunks = new Set()) => {
  let entry = null;
  const assets = new Set();

  if (!seenChunks.has(chunkName)) {
    seenChunks.add(chunkName);

    const chunk = manifest[chunkName];
    if (chunk) {
      entry = `${process.env.VITE_PARLASSETS_URL}/assets/${chunk.file}`;
      assets.add(entry);
      if (Array.isArray(chunk.css)) {
        chunk.css.forEach((css) => {
          assets.add(`${process.env.VITE_PARLASSETS_URL}/assets/${css}`);
        });
      }
      if (Array.isArray(chunk.imports)) {
        chunk.imports.forEach((importChunkName) => {
          const importAssets = getChunkAssets(importChunkName, seenChunks)[1];
          importAssets.forEach((importAsset) => {
            assets.add(importAsset);
          });
        });
      }
    }
  }

  return [entry, assets];
};

const getClientAssets = (cardName) => {
  return getChunkAssets(`virtual:${cardName}`);
};

const renderAssets = (cardName, modules, mountId) => {
  let preloads = '';
  let styles = '';
  let scripts = '';

  const [entry, assets] = getClientAssets(cardName);
  scripts += `<script type="module" src="${entry}?mountId=${mountId}"></script>`;
  assets.forEach((asset) => {
    if (asset.endsWith('.css')) {
      styles += `<link rel="stylesheet" href="${asset}">`;
    } else if (asset.endsWith('.js')) {
      preloads += `<link rel="modulepreload" href="${asset}">`;
    }
  });

  return { preloads, styles, scripts };
};

const renderInitialState = (state) => {
  const json = stringify(state);
  return `<script type="module">window.__INITIAL_STATE__=${json};</script>`;
};

const renderCard = async ({
  cardName,
  id,
  date,
  locale,
  template,
  state,
  currentUrl,
  parlaHeaders,
  responseTimings,
  reply,
}) => {
  if (!id) {
    throw new HTTPError(400, `Query parameter 'id' missing`);
  }
  if (!template) {
    throw new HTTPError(400, `Query parameter 'template' missing`);
  }

  const renderTemplate = getTemplate(template);

  responseTimings.push('beforeModuleLoad', reply.elapsedTime);
  const [{ render }, localeData] = await Promise.all([
    await loadCardModule(cardName, reply),
    await loadLocale(locale, reply),
  ]);
  responseTimings.push('afterModuleLoad', reply.elapsedTime);

  if (!render) {
    throw new HTTPError(404, `Card '${cardName}' not found`);
  }
  if (!localeData) {
    throw new HTTPError(404, `Locale '${locale}' not found`);
  }

  const defaultMessages = localeData.defaults ?? {};
  const cardMessages = localeData[cardName] ?? {};

  responseTimings.push('beforeDataFetch', reply.elapsedTime);
  let cardData = {};
  if (cardName !== 'misc/error' && !state.no_card_data) {
    const dataUrl = getCardDataUrl(cardName, id, date, state);
    cardData = await fetchCardData({
      dataUrl,
      id,
      date,
      currentUrl,
      parlaHeaders,
    });
  }
  responseTimings.push('afterDataFetch', reply.elapsedTime);

  const cardState = { ...state };
  // force altHeader if card is shared or embedded
  if (template === 'share' || template === 'embed') {
    cardState.altHeader = true;
  }
  const urls = getUrls(date);
  const siteMap = await fetchSiteMap();

  const uid = Math.random().toString(36).slice(2);
  const mountId = `${cardName.replace(/\//g, '_')}__${uid}`;
  const contextData = {
    mountId,
    cardName,
    cardData,
    cardState,
    urls,
    siteMap,
    templateName: template,
  };
  const i18nData = {
    locale,
    defaultMessages,
    cardMessages,
  };

  const [cardHtml, ctx] = await render(contextData, i18nData);
  const initialState = renderInitialState({ contextData, i18nData });
  const { preloads, styles, scripts } = renderAssets(
    cardName,
    ctx.modules,
    mountId,
  );

  const outputHtml = `${styles}${preloads}<div id="${mountId}">${cardHtml}</div>${initialState}${scripts}`;

  const html = renderTemplate({
    'page-title': contextData.template.pageTitle,
    'parlassets-url': urls.cdn,
    'parlasite-url': urls.site,
    'container-class': contextData.template.frameContainerClass,
    'embed-class': contextData.template.embedContainerClass,
    'context-url': contextData.template.contextUrl,
    'context-text': defaultMessages?.frame?.['show-in-context'],
    'og-image': contextData.template.ogImage,
    'ssr-outlet': outputHtml,
    'debug-data-url': cardData.url,
  });

  return html;
};

export { HTTPError, renderCard };
