import * as Sentry from '@sentry/node';

// eslint-disable-next-line no-console
console.log(`Sentry SDK v${Sentry.SDK_VERSION} instrumenting...`);

const isProd = process.env.NODE_ENV === 'production';
const sentryDsn = process.env.SENTRY_DSN || '';
const sentryEnv = process.env.SENTRY_ENVIRONMENT || '';

// Ensure to call this before requiring any other modules!
Sentry.init({
  dsn: isProd ? sentryDsn : '',
  environment: sentryEnv,
});

/* eslint-disable no-console */
console.log(`Sentry instrumentation: `);
console.log(`  Enabled: ${Sentry.isEnabled()}`);
console.log(`  Environment: ${sentryEnv}`);
console.log(`  DSN: ${sentryDsn}`);
/* eslint-enable no-console */
