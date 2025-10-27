const { sanitizeSlug } = require('../server/sanitize');

const config = {
  port: 3066,
  serverTimeout: 120000,
  urls: {
    cdn: process.env.PARLASITE_CDN_URL || 'http://localhost:8080',
    cards: process.env.PARLASITE_CARDS_URL || 'http://localhost:3000',
    parladata: process.env.PARLASITE_DATA_URL || 'http://localhost:8000/v3',
    metaImages: 'https://meta-image-generator.lb.djnd.si/parlameter',
  },
  mandates: [
    // insert mandates for selector here e.g. { id: 1, name: '2018–2022', url: 'https://x.parlameter.si' },
    { id: 3, name: '2022–2026', url: 'https://hrastnik.parlameter.si' },
    { id: 1, name: '2018–2022', url: 'https://2018.hrastnik.parlameter.si' },
  ],
  locale: 'sl-obcina-hrastnik',
  leaderId: process.env.PARLASITE_LEADER_ID,
  rootOrgId: process.env.PARLASITE_ROOT_ORG_ID,
  mandateId: process.env.PARLASITE_MANDATE_ID,
  defaultCardDate: process.env.PARLASITE_DEFAULT_CARD_DATE,
  newsletterSegmentId: process.env.PARLASITE_NEWSLETTER_SEGMENT_ID,
};

config.locale = sanitizeSlug(config.locale);

if (!config.leaderId || !config.rootOrgId || !config.mandateId) {
  throw new Error('Required config values are not defined!');
}

module.exports = config;
