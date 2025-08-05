const { i18n } = require('../server');

const sm = i18n.siteMap;

module.exports = (app) => {
  app.use('/', require('./landing'));

  app.get('/hello', (req, res) => {
    res.json({
      ok: true,
    });
  });

  app.use(`/${sm.landing.legislation}`, require('./zakonodaja'));
  app.use(`/${sm.landing.sessions}`, require('./seje'));
  app.use(`/${sm.landing.tools}`, require('./orodja'));
  app.use(`/${sm.member.leaderBase}`, require('./poslanec').leader);
  app.use(`/${sm.member.base}`, require('./poslanec').poslanec);
  app.use(`/${sm.party.base}`, require('./poslanska-skupina'));
  app.use(`/${sm.session.base}`, require('./seja'));

  app.use('/api', require('./api'));
};
