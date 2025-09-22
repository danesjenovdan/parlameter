const Sentry = require('@sentry/node');
const express = require('express');
const config = require('../config');
const { i18n: _i18n, asyncRender: ar } = require('./utils');

const i18n = _i18n(config.locale);

const app = express();

function setupExpress() {
  return new Promise((resolve, reject) => {
    // eslint-disable-next-line no-console
    console.log('| EXPRESS SERVER | - starting...');

    // disable "X-Powered-By: Express" header
    app.disable('x-powered-by');

    // set template renderer
    app.set('view engine', 'ejs');
    app.set('view options', {
      async: true,
    });
    app.locals.lang = config.locale;
    app.locals.i18n = i18n;
    app.locals.config = config;
    app.locals.sm = i18n.siteMap;
    app.locals.rootOrgId = config.rootOrgId;
    app.locals.rootOrgId2 = config.rootOrgId2;
    app.locals.mandateId = config.mandateId;
    app.locals.newsletterSegmentId = config.newsletterSegmentId;

    // i18n middleware
    app.use((req, res, next) => {
      if (req.query.lang) {
        res.locals.i18n = _i18n(req.query.lang);
        res.locals.lang = req.query.lang;
      }
      next();
    });

    require('./routes')(app);

    // all other routes
    app.get(
      '*any',
      ar((render, req, res) => {
        res.status(404);
        render('error/404', {
          pageTitle: '404 Not Found',
          activeMenu: '',
        });
      }),
    );

    // needs to be after all routes and before any other error handlers
    Sentry.setupExpressErrorHandler(app);

    // catch-all error handler (needs all 4 args)
    app.use((error, req, res, next) => {
      // eslint-disable-next-line no-console
      console.error('express catch-all error', error);

      ar((render) => {
        res.status(500);
        render('error/500', {
          pageTitle: '500 Internal Server Error',
          activeMenu: '',
          error,
        });
      })(req, res, next);
    });

    // start listening on port
    const server = app.listen(config.port, (error) => {
      if (!error) {
        // eslint-disable-next-line no-console
        console.log(
          `| EXPRESS SERVER | - started on: http://localhost:${config.port}/`,
        );
        resolve();
      } else {
        reject(error);
      }
    });

    server.on('error', (error) => {
      reject(error);
    });

    server.timeout = config.serverTimeout;
  });
}

function init() {
  return Promise.resolve().then(setupExpress);
}

module.exports = {
  init,
  i18n,
};
