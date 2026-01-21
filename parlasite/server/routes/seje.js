const express = require('express');
const {
  asyncRender: ar,
  getOgImageUrl,
  getQueryParamString,
} = require('../utils');
const { i18n } = require('../server');

const sm = i18n.siteMap;

const router = express.Router();

router.get(
  '/',
  ar((render) => {
    render('seje', {
      ogImageUrl: getOgImageUrl('generic', {
        title: i18n('titles.session-list'),
      }),
      activeMenu: 'sessions',
      pageTitle: i18n('titles.session-list'),
    });
  }),
);

router.get(
  `/${sm.sessions.search.base}`,
  ar((render, req) => {
    render('seje/isci', {
      activeMenu: 'sessions_search',
      pageTitle: i18n('titles.sessions-search'),
      query: getQueryParamString(req.query.q),
      mps: req.query.mps,
      pgs: req.query.pgs,
    });
  }),
);

module.exports = router;
