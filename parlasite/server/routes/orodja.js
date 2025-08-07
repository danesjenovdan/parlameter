const express = require('express');
const { asyncRender: ar, getOgImageUrl } = require('../utils');
const { i18n } = require('../server');

const sm = i18n.siteMap;

const router = express.Router();

router.get(
  '/',
  ar((render) => {
    render('orodja', {
      ogImageUrl: getOgImageUrl('generic', { title: i18n('menu.tools') }),
      activeMenu: 'tools',
      pageTitle: i18n('menu.tools'),
    });
  }),
);

router.get(
  `/${sm.tools.notifications}`,
  ar((render, req) => {
    render('orodja/obvestila', {
      activeMenu: 'tool',
      pageTitle: i18n('tools.notifications.title'),
      currentTool: 'obvestila',
      uid: req.query.uid || false,
      kid: req.query.kid || false,
      settings: req.query.settings || false,
    });
  }),
);

router.get(
  `/${sm.tools.voteComparator}`,
  ar((render) => {
    render('orodja/primerjalnik-glasovanj', {
      activeMenu: 'tool',
      pageTitle: i18n('tools.voteComparator.title'),
      currentTool: 'primerjalnik-glasovanj',
    });
  }),
);

router.get(
  `/${sm.tools.unity}`,
  ar((render) => {
    render('orodja/enotnost', {
      activeMenu: 'tool',
      pageTitle: i18n('tools.unity.title'),
      currentTool: 'enotnost',
    });
  }),
);

router.get(
  `/${sm.tools.compass}`,
  ar((render) => {
    render('orodja/parlamentarni-kompas', {
      activeMenu: 'tool',
      pageTitle: i18n('tools.compass.title'),
      currentTool: 'parlamentarni-kompas',
    });
  }),
);

router.get(
  `/${sm.tools.wordGroups}`,
  ar((render) => {
    render('orodja/skupine-besed', {
      activeMenu: 'tool',
      pageTitle: i18n('tools.wordGroups.title'),
      currentTool: 'skupine-besed',
    });
  }),
);

module.exports = router;
