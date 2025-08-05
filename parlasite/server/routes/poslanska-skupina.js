const express = require('express');
const { asyncRender: ar, getOgImageUrl, stringifyParams } = require('../utils');
const { urls, defaultCardDate } = require('../../config');
const { i18n } = require('../server');

const sm = i18n.siteMap;

const router = express.Router();

async function getNewData(slug) {
  const id = parseInt(slug.split('-')[0], 10);
  const params = stringifyParams({ id, date: defaultCardDate || null });
  const response = await fetch(
    `${urls.parladata}/cards/group/basic-information/${params}`,
  );
  // response.ok means status is 2xx
  if (response.ok) {
    const data = await response.json();
    return {
      group: {
        ...data.group,
        ...data.results,
        id, // TODO this might be simpler if parladata would return the ID
      },
    };
  }
  return false;
}

router.get(
  ['/:slug([a-z0-9-]+)', `/:slug([a-z0-9-]+)/${sm.party.overview}`],
  ar(async (render, req, res, next) => {
    const pgData = await getNewData(req.params.slug);
    if (pgData) {
      render('poslanska-skupina/pregled', {
        ogImageUrl: getOgImageUrl('circle', {
          title: i18n('general.overview'),
          h1: pgData.group.name,
          acronym: pgData.group.acronym,
        }),
        activeMenu: 'pg',
        pageTitle: `${i18n('general.overview')} - ${pgData.group.name}`,
        activeTab: 'pregled',
        ...pgData,
      });
    } else {
      next();
    }
  }),
);

router.get(
  [`/:slug([a-z0-9-]+)/${sm.party.votings}`],
  ar(async (render, req, res, next) => {
    const pgData = await getNewData(req.params.slug);
    if (pgData) {
      render('poslanska-skupina/glasovanja', {
        ogImageUrl: getOgImageUrl('circle', {
          title: i18n('general.voting'),
          h1: pgData.group.name,
          acronym: pgData.group.acronym,
        }),
        activeMenu: 'pg',
        pageTitle: `${i18n('general.voting')} - ${pgData.group.name}`,
        activeTab: 'glasovanja',
        ...pgData,
      });
    } else {
      next();
    }
  }),
);

router.get(
  [`/:slug([a-z0-9-]+)/${sm.party.speeches}`],
  ar(async (render, req, res, next) => {
    const pgData = await getNewData(req.params.slug);
    if (pgData) {
      render('poslanska-skupina/govori', {
        ogImageUrl: getOgImageUrl('circle', {
          title: i18n('general.speeches'),
          h1: pgData.group.name,
          acronym: pgData.group.acronym,
        }),
        activeMenu: 'pg',
        pageTitle: `${i18n('general.speeches')} - ${pgData.group.name}`,
        activeTab: 'govori',
        ...pgData,
      });
    } else {
      next();
    }
  }),
);

module.exports = router;
