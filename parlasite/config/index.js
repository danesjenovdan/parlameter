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
    { id: 14, name: '2024–2028', url: 'https://parlametar.hr' },
    { id: 1, name: '2020–2024', url: 'https://10.parlametar.hr' },
    { id: 13, name: '2016–2020', url: 'https://9.parlametar.hr' },
  ],
  locale: 'hr',
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
