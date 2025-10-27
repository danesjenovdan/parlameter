import fs from 'fs-extra';
import axios from 'axios';
import { sanitizeSlug, sanitizeCardName } from './sanitize.js';

class ResponseTimings {
  constructor() {
    this.timings = [];
  }

  push(name, time) {
    this.timings.push([name, time]);
  }

  toString() {
    return this.timings
      .map(([name, time]) => `${name}:${time.toFixed(2)}`)
      .join(',');
  }
}

const parseISOLikeDate = (date) => {
  // parses iso like string (2022-12-31, 2022_12_31, 20221231)
  if (typeof date === 'string') {
    const dateString = date.replace(/[^0-9]/g, '');
    const year = Number.parseInt(dateString.slice(0, 4), 10);
    const month = Number.parseInt(dateString.slice(4, 6), 10);
    const day = Number.parseInt(dateString.slice(6, 8), 10);
    const dateObj = new Date(Date.UTC(year, month - 1, day));
    if (!Number.isNaN(dateObj.getTime())) {
      return dateObj;
    }
  }
  return null;
};

const otherParlasiteUrls = (() => {
  const keys = Object.keys(process.env)
    .filter((key) => key.startsWith('VITE_PARLASITE_URL_BEFORE_'))
    .map((key) => {
      const url = process.env[key];
      const dateString = key.replace(/^VITE_PARLASITE_URL_BEFORE_/g, '');
      const dateObj = parseISOLikeDate(dateString);
      return {
        before: dateObj,
        url,
      };
    })
    .filter(({ before }) => before)
    .sort((a, b) => a.before - b.before);
  return keys;
})();

const getParlasiteUrl = (date) => {
  const dateObj = parseISOLikeDate(date);
  if (dateObj) {
    const other = otherParlasiteUrls.find(({ before }) => dateObj <= before);
    if (other) {
      return other.url;
    }
  }
  return process.env.VITE_PARLASITE_URL;
};

const getUrls = (date) => {
  return {
    site: getParlasiteUrl(date),
    cards: process.env.VITE_PARLACARDS_URL,
    data: process.env.VITE_PARLADATA_URL,
    cdn: process.env.VITE_PARLASSETS_URL,
    metaImages: process.env.VITE_METAIMAGES_URL,
  };
};

const createError = (statusCode, error, message, code) => {
  const obj = {
    message,
    error,
    statusCode,
  };
  if (code) {
    obj.code = code;
  }
  return obj;
};

const moduleCache = {};

const loadCardModule = async (cardName) => {
  cardName = sanitizeCardName(cardName);
  if (!(cardName in moduleCache)) {
    try {
      moduleCache[cardName] = await import(`../dist/server/${cardName}.js`);
    } catch (error) {
      if (error.code !== 'ERR_MODULE_NOT_FOUND') {
        throw error;
      }
      moduleCache[cardName] = null;
    }
  }
  return {
    render: moduleCache[cardName]?.default,
  };
};

const localeCache = {};

const loadLocale = async (locale) => {
  locale = sanitizeSlug(locale);
  if (!(locale in localeCache)) {
    try {
      localeCache[locale] = await fs.readJSON(`./dist/locales/${locale}.json`);
    } catch (error) {
      if (error.code !== 'ENOENT') {
        throw error;
      }
      localeCache[locale] = null;
    }
  }
  return localeCache[locale];
};

function getCardDataUrl(cardName, id, date, state) {
  const searchParams = new URLSearchParams();

  // base params
  if (id) {
    searchParams.set('id', id);
  }
  if (date) {
    searchParams.set('date', date);
  }

  // search params
  if (state?.text) {
    searchParams.set('text', state?.text);
  }
  if (state?.months) {
    searchParams.set('months', state?.months);
  }
  if (state?.people) {
    searchParams.set('people', state?.people);
  }
  if (state?.groups) {
    searchParams.set('groups', state?.groups);
  }

  const { data } = getUrls(date);
  const qs = searchParams.toString();
  return `${data}/cards/${cardName}/${qs ? `?${qs}` : ''}`;
}

const fetchCardData = async ({
  dataUrl,
  id,
  date,
  parlaHeaders,
  currentUrl,
}) => {
  // eslint-disable-next-line no-console
  console.log('Fetching:', dataUrl);
  // eslint-disable-next-line no-console
  console.log('  > from:', currentUrl);

  if (dataUrl) {
    let response;
    try {
      response = await axios.get(dataUrl, {
        headers: {
          ...parlaHeaders,
          'x-parlacards-request-url': dataUrl,
          'x-parlacards-request-from': currentUrl,
        },
      });
    } catch (error) {
      return {
        url: dataUrl,
        id,
        date,
        error: createError(
          error.response?.status ?? 0,
          error.name,
          error.message,
          error.code,
        ),
        data: error.response?.data,
      };
    }
    if (typeof response.data !== 'object') {
      return {
        url: dataUrl,
        id,
        date,
        error: createError(
          response.status ?? 0,
          'Error',
          'Request did not return valid json data',
        ),
        data: response.data,
      };
    }
    return {
      url: dataUrl,
      id,
      date,
      error: false,
      data: response.data,
    };
  }
  return {
    url: dataUrl,
    id,
    date,
    error: false,
    data: null,
  };
};

const siteMapCache = {
  value: null,
  default: fs.readJSONSync('./build/sitemap-default.json'),
};

const fetchSiteMap = async () => {
  if (siteMapCache.value) {
    return siteMapCache.value;
  }
  try {
    const response = await axios.get(
      `${process.env.VITE_PARLASITE_URL}/api/sitemap`,
    );
    siteMapCache.value = response.data;
    return siteMapCache.value;
  } catch {
    return siteMapCache.default;
  }
};

const getParlaHeaders = (headers) => {
  const parlaHeaders = {};
  Object.keys(headers).forEach((key) => {
    if (key.toLowerCase().startsWith('x-parla')) {
      parlaHeaders[key.toLowerCase()] = headers[key];
    }
  });
  return parlaHeaders;
};

export {
  ResponseTimings,
  getUrls,
  createError,
  loadCardModule,
  loadLocale,
  getCardDataUrl,
  fetchCardData,
  fetchSiteMap,
  getParlaHeaders,
};
