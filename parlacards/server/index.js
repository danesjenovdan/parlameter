import createFastify from 'fastify';
import * as Sentry from '@sentry/node';
import fastifyCors from '@fastify/cors';
import { HTTPError, renderCard } from './render-card.js';
import { ResponseTimings, getParlaHeaders } from './utils.js';
import { sanitizeCardName, sanitizeSlug } from './sanitize.js';

const fastify = createFastify({
  logger: true,
  routerOptions: { ignoreTrailingSlash: true },
});

Sentry.setupFastifyErrorHandler(fastify);

process.on('unhandledRejection', (error) => {
  fastify.log.error(error);
  Sentry.captureException(error);
  Sentry.close().then(() => {
    process.exit(2);
  });
});

process.on('uncaughtException', (error) => {
  fastify.log.error(error);
  Sentry.captureException(error);
  Sentry.close().then(() => {
    process.exit(3);
  });
});

fastify.register(fastifyCors, {
  origin: '*',
});

const renderCardHandler = async (request, reply) => {
  const responseTimings = new ResponseTimings();
  responseTimings.push('requestStart', reply.elapsedTime);

  const { group, method } = request.params;
  const {
    id,
    date,
    locale: _locale,
    template: _template,
    ...state
  } = request.query;
  const locale = sanitizeSlug(_locale);
  const template = sanitizeSlug(_template);
  const cardName = sanitizeCardName(`${group}/${method}`);
  const currentUrl = `${request.protocol}://${request.hostname}${request.originalUrl}`;
  const parlaHeaders = getParlaHeaders(request.headers);

  try {
    responseTimings.push('beforeRender', reply.elapsedTime);
    const html = await renderCard({
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
    });
    responseTimings.push('afterRender', reply.elapsedTime);

    responseTimings.push('requestEnd', reply.elapsedTime);
    reply.header('x-parlacards-timings', responseTimings.toString());
    return reply.type('text/html').send(html);
  } catch (error) {
    if (error instanceof HTTPError) {
      if (error.statusCode < 500) {
        return reply
          .status(error.statusCode)
          .type('text/html')
          .send(error.message);
      }
    }
    fastify.log.error(error);
    Sentry.captureException(error);
    return reply.status(500).type('text/html').send(error.stack);
  }
};

fastify.get('/:group/:method', renderCardHandler);

fastify.listen({ port: process.env.PORT || 3000, host: '0.0.0.0' }, (error) => {
  if (error) {
    fastify.log.error(error);
    Sentry.captureException(error);
    Sentry.close().then(() => {
      process.exit(1);
    });
  }
});
