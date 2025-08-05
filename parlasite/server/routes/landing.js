const express = require('express');
const { asyncRender: ar, getOgImageUrl } = require('../utils');
const { i18n } = require('../server');

const sm = i18n.siteMap;

const router = express.Router();

/**
 * TOP NAVIGATION
 */

router.get(
  '/',
  ar((render, req) => {
    render('landing', {
      activeMenu: 'landing',
      pageTitle: i18n('landing.title'),
      query: req.query.q,
    });
  }),
);

// get /zakonodaja -> routes/zakonodaja.js

// get /seje -> routes/seje.js

router.get(
  `/${sm.landing.members}`,
  ar((render) => {
    render('landing/poslanci', {
      ogImageUrl: getOgImageUrl('generic', { title: i18n('menu.mps') }),
      activeMenu: 'mps',
      pageTitle: i18n('menu.mps'),
    });
  }),
);

router.get(
  `/${sm.landing.parties}`,
  ar((render) => {
    render('landing/poslanske-skupine', {
      ogImageUrl: getOgImageUrl('generic', { title: i18n('menu.pgs') }),
      activeMenu: 'pgs',
      pageTitle: i18n('menu.pgs'),
    });
  }),
);

// get /orodja -> routes/orodja.js

/**
 * ABOUT PAGES
 */

router.get(
  `/${sm.landing.media}`,
  ar((render) => {
    render('landing/za-medije', {
      activeMenu: 'landing',
      pageTitle: i18n('footer.press'),
    });
  }),
);

router.get(
  `/${sm.landing.legal}`,
  ar((render) => {
    render('landing/pravno-obvestilo', {
      activeMenu: 'landing',
      pageTitle: i18n('legal.title'),
    });
  }),
);

router.get(
  `/${sm.landing.thankYou}`,
  ar((render) => {
    render('landing/hvala', {
      activeMenu: 'landing',
      pageTitle: i18n('titles.thank-you'),
    });
  }),
);

router.get(
  `/${sm.landing.error}`,
  ar((render) => {
    render('landing/ups', {
      activeMenu: 'landing',
      pageTitle: i18n('titles.ups'),
    });
  }),
);

module.exports = router;
