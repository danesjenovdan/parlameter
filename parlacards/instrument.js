import * as Sentry from '@sentry/node';

// Ensure to call this before requiring any other modules!
Sentry.init({
  dsn:
    process.env.NODE_ENV === 'production'
      ? 'https://07dc842d53be467b8f158c93984a3fb9@o1076834.ingest.sentry.io/6080015'
      : '',
});
