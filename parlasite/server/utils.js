const Sentry = require('@sentry/node');
const fs = require('fs');
const _ = require('lodash');
const { sanitizeSlug } = require('./sanitize');
const { urls, locale, defaultCardDate } = require('../config');

function formatError(error, indent = '') {
  let lines = [];

  lines.push(`${error}`);
  lines.push(`${error.stack}`);

  if (error.cause) {
    lines = lines.concat(formatError(error.cause));
  }

  // stack can have multiple lines, so join and split again
  let str = lines.join('\n');
  lines = str.split('\n');

  // dedupe same consecutive lines
  lines = lines.filter(
    (line, index) => index === 0 || line !== lines[index - 1],
  );

  // indent all lines except the first
  lines = lines.map((line, index) => (index === 0 ? line : `${indent}${line}`));

  // join lines again
  str = lines.join('\n');
  return str;
}

function isValidErrorForSentry(error, responseText) {
  if (error.response) {
    if (error.response.status === 400 && responseText != null) {
      if (/^Query parameter '.*' missing$/.test(responseText)) {
        return false;
      }
      if (/^{"error": "`id` needs to be an integer."}$/.test(responseText)) {
        return false;
      }
    }
    if (error.response.status === 404 && responseText != null) {
      if (/^(Template|Card|Locale) '.*' not found$/.test(responseText)) {
        return false;
      }
      if (responseText === '') {
        return false;
      }
    }
  }
  return true;
}

async function cloneResponseTextForSentry(response) {
  if (!response) {
    return null;
  }
  try {
    const responseClone = response.clone();
    const responseText = await responseClone.text();
    return responseText;
  } catch {
    return '<could not read response text>';
  }
}

async function sentryFetch(resource, options) {
  try {
    const res = await fetch(resource, options);
    if (!res.ok) {
      const error = new Error('fetch response not ok');
      error.response = res;
      throw error;
    }
    return res;
  } catch (error) {
    let responseText = await cloneResponseTextForSentry(error.response);
    if (isValidErrorForSentry(error, responseText)) {
      Sentry.withScope(function (scope) {
        const resourceTag = (resource || '').split('?')[0];
        scope.setTag('fetch-resource', resourceTag);
        scope.setExtras({
          'fetch-resource': resource,
          'fetch-options': options,
        });
        if (error.response) {
          scope.setTag('fetch-status', error.response.status);
          scope.setExtras({
            'fetch-status': error.response.status,
            'fetch-response-text': responseText,
          });
        }
        Sentry.captureException(error);
      });
    }
    throw error;
  }
}

class ResponseTimings {
  constructor() {
    this.start = performance.now();
    this.timings = [];
  }

  push(name, time) {
    this.timings.push([name, time]);
  }

  toString() {
    return this.timings
      .map(([name, time]) => `${name}:${(time - this.start).toFixed(2)}`)
      .join(',');
  }
}

function stringifyParams(params) {
  if (Object.keys(params).length > 0) {
    const query = Object.keys(params)
      .filter((key) => params[key] != null) // maybe params[key] is undefined
      .map((key) => {
        const val =
          typeof params[key] === 'object'
            ? JSON.stringify(params[key])
            : String(params[key]);
        return `${key}=${encodeURIComponent(val)}`;
      })
      .join('&');
    return `?${query}`;
  }
  return '';
}

function slovenianDate(isoDate) {
  if (!isoDate) {
    return 'Invalid Date';
  }
  const date = new Date(isoDate);
  if (Number.isNaN(date.getTime())) {
    return 'Invalid Date';
  }
  return `${date.getDate()}. ${date.getMonth() + 1}. ${date.getFullYear()}`;
}

function fixFetchCardArgs(cardPath, id, params = {}) {
  // optional second argument
  if (typeof id === 'object') {
    params = id;
    id = undefined;
  }

  // remove leading and trailing slashes
  cardPath = cardPath
    .trim()
    .replace(/^\/+/, '')
    .replace(/\/+$/, '')
    .toLowerCase();

  // set params
  if (id) {
    params.id = id;
  }

  params.template = 'site';
  params.locale = locale;

  if (!params.date && defaultCardDate) {
    params.date = defaultCardDate;
  }

  return { cardPath, params };
}

async function fetchCardAsync(req, cardPath, params, uid, responseTimings) {
  const cardUrl = `${urls.cards}/${cardPath}${stringifyParams(params)}`;
  const currentUrl = `${req.protocol}://${req.hostname}${req.originalUrl}`;

  // eslint-disable-next-line no-console
  console.log(`[${uid} | ${cardPath}] Fetching card:\n  > url: ${cardUrl}`);

  try {
    responseTimings.push(`beforeFetch/${uid}`, performance.now());
    const res = await sentryFetch(cardUrl, {
      headers: {
        'x-parlasite-request-url': cardUrl,
        'x-parlasite-request-from': currentUrl,
        'x-parlasite-request-user-agent': req.headers['user-agent'],
      },
    });
    const text = await res.text();
    responseTimings.push(`afterFetch/${uid}`, performance.now());
    return [res.headers, text];
  } catch (error) {
    // eslint-disable-next-line no-console
    console.error(
      `\n[${uid} | ${cardPath}] Failed to fetch card:\n  > url: ${cardUrl}\n  > ${formatError(error, '  > ')}\n`,
    );
    return [
      null,
      `<div class="alert alert-danger" style="margin-top:20px;text-align:left">Failed to fetch card: ${cardPath}<pre>${error}</pre></div>`,
    ];
  }
}

// This function is called from the template and synchronously returns a placeholder
// string that will be replaced with the card content later. This is done so that
// all the fetchCard calls can be made in parallel and the HTML can be generated faster.
//
// It has a bound `this` object with {req, res, outPromises, responseTimings}
function fetchCard(cardPath, id, params = {}) {
  // due to historical reasons, fix different ways of calling this function
  ({ cardPath, params } = fixFetchCardArgs(cardPath, id, params));

  // generate a unique ID for this async call
  // this is used to replace the placeholder in the HTML later
  const uid = Math.random().toString(36).slice(2);

  // save the promise to be resolved later
  this.outPromises.push([
    uid,
    cardPath,
    fetchCardAsync(this.req, cardPath, params, uid, this.responseTimings),
  ]);

  return `<!--asyncReplace(${uid})-->`;
}

// This function replaces the placeholders in the HTML with the actual card content
// after all async calls have been resolved.
async function replaceAsyncPlaceholders(res, rawHtml, outPromises) {
  const promises = outPromises.map(([uid, cardPath, promise]) =>
    promise.then(([headers, html]) => {
      rawHtml = rawHtml.replace(
        `<!--asyncReplace(${uid})-->`,
        `<!--async(${uid})-->${html}`,
      );
      if (headers) {
        const timingHeader = headers.get('x-parlacards-timings');
        if (timingHeader) {
          res.setHeader(
            `x-parlacards-timings-${uid}-${cardPath.replaceAll('/', '-')}`,
            timingHeader,
          );
        }
      }
    }),
  );
  return Promise.all(promises).then(() => rawHtml);
}

const asyncRoute =
  (fn) =>
  (...args) =>
    fn(...args).catch(args[2]);

const asyncRender = (fn) => (req, res, next) => {
  const responseTimings = new ResponseTimings();
  responseTimings.push('requestStart', performance.now());

  const outPromises = [];
  const render = (view, opts) => {
    const options = {
      ...opts,
      slovenianDate,
      // bind the `this` object to the fetchCard function so we can access the
      // req, res and outPromises in the function when called from the template
      fetchCard: fetchCard.bind({ req, res, outPromises, responseTimings }),
      async: true,
    };
    res.render(view, options, (error, promise) => {
      if (error) {
        next(error);
      } else {
        promise
          // rawHtml is filled with placeholders for async fetchCard calls
          // replaceAsyncPlaceholders will await them in parallel and replace
          // the placeholders with the actual card HTML
          .then((rawHtml) =>
            replaceAsyncPlaceholders(res, rawHtml, outPromises),
          )
          .then((html) => {
            responseTimings.push('requestEnd', performance.now());
            res.setHeader('x-parlasite-timings', responseTimings.toString());
            return res.send(html);
          })
          .catch((pError) => next(pError));
      }
    });
  };

  try {
    const ret = fn(render, req, res, next);
    // if return value is a promise (also true with async functions)
    if (ret && ret.then && ret.catch) {
      // catch any async errors
      ret.catch((error) => next(error));
    }
  } catch (error) {
    // catch any sync errors
    next(error);
  }
};

function expandProps(msg, props) {
  msg = String(msg);
  Object.keys(props).forEach((key) => {
    msg = msg.replace(`{${key}}`, String(props[key]));
  });
  return msg;
}

function i18n(lang) {
  lang = sanitizeSlug(lang);
  const messagesStr = fs.readFileSync(`./i18n/${lang}/defaults.json`, 'utf-8');
  const messages = JSON.parse(messagesStr);
  const siteMapStr = fs.readFileSync(`./i18n/${lang}/sitemap.json`, 'utf-8');
  const siteMap = JSON.parse(siteMapStr);
  const legalBody = fs.existsSync(`./i18n/${lang}/legal.html`)
    ? fs.readFileSync(`./i18n/${lang}/legal.html`, 'utf-8')
    : null;

  const get = (path, props = {}) => {
    if (path === 'legal.body' && legalBody) {
      return legalBody;
    }

    const msg = messages[path] || _.get(messages, path);
    if (msg == null || msg === '[empty]' || msg === '') {
      // eslint-disable-next-line no-console
      console.warn(
        `[i18n] Translation value for lang="${lang}" path="${path}" is missing.`,
      );
      return path;
    }
    if (typeof msg !== 'string') {
      // eslint-disable-next-line no-console
      console.warn(
        `[i18n] Translation value for lang="${lang}" path="${path}" is not a string.`,
      );
      if (typeof msg === 'object') {
        return JSON.stringify(msg);
      }
      return String(msg);
    }
    return expandProps(msg, props);
  };

  get.exists = (path) => {
    const msg = messages[path] || _.get(messages, path);
    return !(msg == null || msg === '[empty]' || msg === '');
  };

  get.siteMap = siteMap;

  return get;
}

function getOgImageUrl(type, params = {}) {
  const url = `${urls.metaImages}/${type}`;
  const query = stringifyParams({ theme: locale, ...params });
  return `${url}${query}`;
}

module.exports = {
  sentryFetch,
  stringifyParams,
  slovenianDate,
  asyncRoute,
  asyncRender,
  i18n,
  getOgImageUrl,
};
