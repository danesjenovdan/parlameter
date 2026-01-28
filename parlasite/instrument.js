const Sentry = require('@sentry/node');
const { TokenBucket } = require('limiter');

// eslint-disable-next-line no-console
console.log(`| SENTRY | - SDK v${Sentry.SDK_VERSION} instrumenting...`);

// Rate limiting configuration
// Burst rate of 30 tokens per hour and sustained rate of 10 tokens per hour
// Burst rate of 5 tokens per second and sustained rate of 1 token per second
const hourBucket = new TokenBucket({
  bucketSize: 30,
  tokensPerInterval: 10,
  interval: 'hour',
});
const secondBucket = new TokenBucket({
  bucketSize: 5,
  tokensPerInterval: 1,
  interval: 'second',
  parentBucket: hourBucket,
});

function rateLimit(event) {
  // Will try to remove a token from both buckets (secondBucket will check hourBucket as parent)
  if (secondBucket.tryRemoveTokens(1)) {
    return event;
  }

  // eslint-disable-next-line no-console
  console.warn('| SENTRY | - rate limit exceeded, dropping event');
  return null;
}

const isProd = process.env.NODE_ENV === 'production';
const sentryDsn = process.env.SENTRY_DSN || '';
const sentryEnv = process.env.SENTRY_ENVIRONMENT || '';

// Ensure to call this before requiring any other modules!
Sentry.init({
  dsn: isProd ? sentryDsn : '',
  environment: sentryEnv,
  beforeSend(event) {
    return rateLimit(event);
  },
});

/* eslint-disable no-console */
console.log(`| SENTRY | - instrumentation: `);
console.log(`| SENTRY | -   Enabled: ${Sentry.isEnabled()}`);
console.log(`| SENTRY | -   Environment: ${sentryEnv}`);
console.log(`| SENTRY | -   DSN: ${sentryDsn}`);
/* eslint-enable no-console */
