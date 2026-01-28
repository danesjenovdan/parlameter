import { createApp } from 'vue';
import { createI18n } from 'vue-i18n';
import { merge } from 'lodash-es';
import * as Sentry from '@sentry/vue';
// eslint-disable-next-line import/no-unresolved
import Card from '@/{cardName}/card.vue';

const { contextData, i18nData } = window.__INITIAL_STATE__;

const { locale, defaultMessages, cardMessages } = i18nData;
const i18n = createI18n({
  locale,
  messages: {
    [locale]: merge({}, defaultMessages, cardMessages),
  },
});

const app = createApp({ ...Card, contextData });

// SENTRY
Sentry.init({
  app,
  dsn: '{sentryDsn}',
  environment: '{sentryEnv}',
  // Ignore some external errors, such as facebook,
  // twitter, slack bots or link crawlers and scanners.
  ignoreErrors: [
    // Outlook Safe Link scanning
    'Object Not Found Matching Id',
    // Network errors
    'Network Error',
    'Request aborted',
    // Caused by some auto-fill extensions and tools like html2canvas
    'Blocked a frame with origin',
    // Chrome on iOS
    '__gCrWeb',
    'Maximum call stack size exceeded',
  ],
  denyUrls: [
    // Chrome extensions
    /extensions\//i,
    /^chrome:\/\//i,
    /^chrome-extension:\/\//i,
  ],
});

app.use(i18n);
app.mount(`#${contextData.mountId}`);
