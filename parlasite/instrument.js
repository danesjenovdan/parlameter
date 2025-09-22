const Sentry = require('@sentry/node');

// eslint-disable-next-line no-console
console.log(`| SENTRY | - SDK v${Sentry.SDK_VERSION} instrumenting...`);

// Ensure to call this before requiring any other modules!
Sentry.init({
  dsn:
    process.env.NODE_ENV === 'production'
      ? 'https://64b10a3bec54dedb44314a61dc68a82b@o1076834.ingest.us.sentry.io/4510062422327296'
      : '',
});

// eslint-disable-next-line no-console
console.log(
  `| SENTRY | - instrumentation done (${Sentry.isEnabled() ? 'enabled' : 'disabled'})`,
);
