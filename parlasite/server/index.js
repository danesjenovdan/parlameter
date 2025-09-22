// Sentry instrumentation (this must be the first import before anything else)
require('../instrument.js');
const Sentry = require('@sentry/node');
const server = require('./server');

Promise.resolve()
  .then(() => server.init())
  .catch((error) => {
    // eslint-disable-next-line no-console
    console.error('Failed to start:', error);

    Sentry.captureException(error);
    Sentry.close().then(() => {
      process.exit(1);
    });
  });
