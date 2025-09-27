const express = require('express');
const {
  asyncRender: ar,
  getOgImageUrl,
  slovenianDate,
  stringifyParams,
  sentryFetch,
} = require('../utils');
const { urls, locale, defaultCardDate } = require('../../config');
const { i18n } = require('../server');

const sm = i18n.siteMap;

const router = express.Router();

// TODO: figure out how to know when to return 404
// TODO: is there a way to preload this?
async function isMotionValid(/* sessionId, motionId */) {
  return true;
}

async function getNewData(id) {
  const params = stringifyParams({ id, date: defaultCardDate || null });
  try {
    const res = await sentryFetch(
      `${urls.parladata}/cards/session/single/${params}`,
    );
    const data = await res.json();
    return {
      session: {
        ...data.results,
        id,
      },
    };
  } catch (error) {
    if (error.response && [400, 404].includes(error.response.status)) {
      return null;
    }
    throw error;
  }
}

const SESSION_CLASSIFICATIONS = {
  unknown: {
    icon: 'seja-neznana',
  },
  regular: {
    icon: 'seja-redna',
  },
  irregular: {
    icon: 'seja-izredna',
  },
  correspondent: {
    icon: 'seja-na-daljavo',
  },
};

function sessionClassification(classification) {
  const key = classification || 'unknown';
  return SESSION_CLASSIFICATIONS[key] || SESSION_CLASSIFICATIONS.unknown;
}

const renderLegislation = async (render, req, res, next) => {
  const sesData = await getNewData(req.params.id);
  if (sesData) {
    render('seja/zakonodaja', {
      ogImageUrl: getOgImageUrl('circle', {
        title: `${i18n('titles.session')} - ${i18n('general.legislation')}`,
        h1: sesData.session.name,
        h2: slovenianDate(sesData.session.start_time),
        icon: `${urls.cdn}/icons/${sessionClassification(sesData.session.classification).icon}.svg`,
      }),
      activeMenu: 'session',
      pageTitle: `${i18n('titles.session')} - ${i18n('general.legislation')}`,
      activeTab: 'zakonodaja',
      ...sesData,
    });
  } else {
    next();
  }
};

const renderVotes = async (render, req, res, next) => {
  const sesData = await getNewData(req.params.id);
  if (sesData) {
    render('seja/glasovanja', {
      ogImageUrl: getOgImageUrl('circle', {
        title: `${i18n('titles.session')} - ${i18n('titles.other-votings')}`,
        h1: sesData.session.name,
        h2: slovenianDate(sesData.session.start_time),
        icon: `${urls.cdn}/icons/${sessionClassification(sesData.session.classification).icon}.svg`,
      }),
      activeMenu: 'session',
      pageTitle: `${i18n('titles.session')} - ${i18n('titles.other-votings')}`,
      activeTab: 'glasovanja',
      ...sesData,
    });
  } else {
    next();
  }
};

const renderAgenda = async (render, req, res, next) => {
  const sesData = await getNewData(req.params.id);
  if (sesData) {
    render('seja/dnevni-red', {
      ogImageUrl: getOgImageUrl('circle', {
        title: `${i18n('titles.session')} - ${i18n('titles.agenda')}`,
        h1: sesData.session.name,
        h2: slovenianDate(sesData.session.start_time),
        icon: `${urls.cdn}/icons/${sessionClassification(sesData.session.classification).icon}.svg`,
      }),
      activeMenu: 'session',
      pageTitle: `${i18n('titles.session')} - ${i18n('titles.agenda')}`,
      activeTab: 'dnevni-red',
      ...sesData,
    });
  } else {
    next();
  }
};

const renderTranscript = async (render, req, res, next) => {
  const sesData = await getNewData(req.params.id);
  if (sesData) {
    render('seja/transkript', {
      ogImageUrl: getOgImageUrl('circle', {
        title: `${i18n('titles.session')} - ${i18n('titles.transcript')}`,
        h1: sesData.session.name,
        h2: slovenianDate(sesData.session.start_time),
        icon: `${urls.cdn}/icons/${sessionClassification(sesData.session.classification).icon}.svg`,
      }),
      activeMenu: 'session',
      pageTitle: `${i18n('titles.session')} - ${i18n('titles.transcript')}`,
      activeTab: 'transkript',
      ...sesData,
      page: req.query.page || 1,
    });
  } else {
    next();
  }
};

const renderMinutes = async (render, req, res, next) => {
  const sesData = await getNewData(req.params.id);
  if (sesData) {
    render('seja/zapisnik', {
      ogImageUrl: getOgImageUrl('circle', {
        title: `${i18n('titles.session')} - ${i18n('titles.minutes')}`,
        h1: sesData.session.name,
        h2: slovenianDate(sesData.session.start_time),
        icon: `${urls.cdn}/icons/${sessionClassification(sesData.session.classification).icon}.svg`,
      }),
      activeMenu: 'session',
      pageTitle: `${i18n('titles.session')} - ${i18n('titles.minutes')}`,
      activeTab: 'minutes',
      ...sesData,
      page: req.query.page || 1,
    });
  } else {
    next();
  }
};

const renderMotion = async (render, req, res, next) => {
  const sesData = await getNewData(req.params.id);
  if (sesData) {
    const motionId = Number(req.params.motionId);
    const isValid = await isMotionValid(sesData.session.id, motionId);
    if (isValid) {
      render('seja/glasovanje', {
        ogImageUrl: getOgImageUrl('circle', {
          title: `${i18n('titles.session')} - ${i18n('titles.voting')}`,
          h1: sesData.session.name,
          h2: slovenianDate(sesData.session.start_time),
          icon: `${urls.cdn}/icons/${sessionClassification(sesData.session.classification).icon}.svg`,
        }),
        activeMenu: 'session',
        pageTitle: `${i18n('titles.session')} - ${i18n('titles.voting')}`,
        activeTab: 'glasovanje',
        ...sesData,
        motionId,
      });
    } else {
      next();
    }
  } else {
    next();
  }
};

const renderEmpty = async (render, req, res, next) => {
  const sesData = await getNewData(req.params.id);
  if (sesData) {
    render('seja/ni-podatkov', {
      ogImageUrl: getOgImageUrl('circle', {
        title: `${i18n('titles.session')}`,
        h1: sesData.session.name,
        h2: slovenianDate(sesData.session.start_time),
        icon: `${urls.cdn}/icons/${sessionClassification(sesData.session.classification).icon}.svg`,
      }),
      activeMenu: 'session',
      pageTitle: `${i18n('titles.session')}`,
      activeTab: 'no-data',
      ...sesData,
    });
  } else {
    next();
  }
};

// dynacally decide what tab to render by default based on session info
const renderDynamic = async (render, req, res, next) => {
  const sesData = await getNewData(req.params.id);
  if (!sesData) {
    next();
    return;
  }

  if (sesData.session.has_legislation && !locale.startsWith('sl-obcina')) {
    await renderLegislation(render, req, res, next);
    return;
  }
  if (sesData.session.has_agenda_items) {
    await renderAgenda(render, req, res, next);
    return;
  }
  if (sesData.session.has_votes) {
    await renderVotes(render, req, res, next);
    return;
  }
  if (sesData.session.has_transcript) {
    await renderTranscript(render, req, res, next);
    return;
  }

  await renderEmpty(render, req, res, next);
};

router.get('/:id', ar(renderDynamic));
router.get(`/:id/${sm.session.legislation}`, ar(renderLegislation));
router.get(`/:id/${sm.session.otherVotings}`, ar(renderVotes));
router.get(`/:id/${sm.session.agenda}`, ar(renderAgenda));
router.get(`/:id/${sm.session.transcript}`, ar(renderTranscript));
router.get(`/:id/${sm.session.minutes}`, ar(renderMinutes));
router.get(`/:id/${sm.session.vote}/:motionId`, ar(renderMotion));

module.exports = router;
