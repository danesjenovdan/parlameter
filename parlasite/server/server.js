const express = require('express');
const chalk = require('chalk');
const config = require('../config');
const { i18n: _i18n, asyncRender: ar } = require('./utils');

const i18n = _i18n(config.locale);

const app = express();

function setupExpress() {
  return new Promise((resolve, reject) => {
    // eslint-disable-next-line no-console
    console.log(`${chalk.magenta('| EXPRESS SERVER |')} - ${chalk.green('starting')}`);

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
    app.use('*', (req, res, next) => {
      if (req.query.lang) {
        res.locals.i18n = _i18n(req.query.lang);
        res.locals.lang = req.query.lang;
      }
      next();
    });

    // eslint-disable-next-line global-require
    require('./routes')(app);

    // all other routes
    app.get('*', ar((render, req, res) => {
      res.status(404);
      render('error/404', {
        pageTitle: '404 Not Found',
        activeMenu: '',
      });
    }));

    // catch-all error handler (needs all 4 args)
    // eslint-disable-next-line no-unused-vars
    app.use((error, req, res, next) => {
      ar((render) => {
        // TODO: sentry
        // eslint-disable-next-line no-console
        console.log('error', error);
        res.status(500);
        render('error/500', {
          pageTitle: '500 Internal Server Error',
          activeMenu: '',
          error,
        });
      })(req, res, next);
    });

    // start listening on port
    const server = app.listen(config.port, () => {
      // eslint-disable-next-line no-console
      console.log(`${chalk.magenta('| EXPRESS SERVER |')} - ${chalk.green(`started on: http://localhost:${config.port}/`)}`);
      resolve();
    });

    server.on('error', (err) => {
      reject(err);
    });

    server.timeout = config.serverTimeout;
  });
}

function init() {
  return Promise.resolve()
    .then(setupExpress);
}

module.exports = {
  init,
  i18n,
};
