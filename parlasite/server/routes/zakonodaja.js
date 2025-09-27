const express = require('express');
const {
  asyncRender: ar,
  getOgImageUrl,
  stringifyParams,
  sentryFetch,
} = require('../utils');
const { urls, defaultCardDate } = require('../../config');
const { i18n } = require('../server');

const router = express.Router();

async function getNewData(slug) {
  const id = parseInt(slug.split('-')[0], 10);
  const params = stringifyParams({ id, date: defaultCardDate || null });
  try {
    const res = await sentryFetch(
      `${urls.parladata}/cards/legislation/single/${params}`,
    );
    const data = await res.json();
    return {
      ...data,
    };
  } catch (error) {
    if (error.response && [400, 404].includes(error.response.status)) {
      return null;
    }
    throw error;
  }
}

router.get(
  '/',
  ar((render) => {
    render('zakonodaja', {
      ogImageUrl: getOgImageUrl('generic', { title: i18n('menu.legislation') }),
      activeMenu: 'legislation',
      pageTitle: i18n('menu.legislation'),
    });
  }),
);

router.get(
  '/:slug',
  ar(async (render, req, res, next) => {
    const lawData = await getNewData(req.params.slug);
    if (lawData) {
      render('zakonodaja/zakon', {
        ogImageUrl: getOgImageUrl('circle', {
          title: i18n('titles.legislation'),
          h1: lawData.results.text,
        }),
        activeMenu: 'legislation_act',
        pageTitle: i18n('titles.legislation'),
        lawData,
      });
    } else {
      next();
    }
  }),
);

module.exports = router;
