const Sentry = require('@sentry/node');

// eslint-disable-next-line no-console
console.log(`| SENTRY | - SDK v${Sentry.SDK_VERSION} instrumenting...`);

const isProd = process.env.NODE_ENV === 'production';
const sentryDsn = process.env.SENTRY_DSN || '';
const sentryEnv = process.env.SENTRY_ENVIRONMENT || '';

// Ensure to call this before requiring any other modules!
Sentry.init({
  dsn: isProd ? sentryDsn : '',
  environment: sentryEnv,
  tracesSampleRate: 0,
});

/* eslint-disable no-console */
console.log(`| SENTRY | - instrumentation: `);
console.log(`| SENTRY | -   Enabled: ${Sentry.isEnabled()}`);
console.log(`| SENTRY | -   Environment: ${sentryEnv}`);
console.log(`| SENTRY | -   DSN: ${sentryDsn}`);
/* eslint-enable no-console */
