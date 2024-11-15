const config = {
  port: 3066,
  serverTimeout: 120000,
  urls: {
    // cdn: 'http://localhost:8080',
    // cards: 'http://localhost:7004',
    // parladata: 'http://localhost:8000/v3',
    cdn: 'https://cdn.10.parlametar.hr',
    cards: 'https://gledaj.10.parlametar.hr',
    parladata: 'https://data.10.parlametar.hr/v3',
    metaImages: 'https://meta-image-generator.lb.djnd.si/parlameter',
  },
  mandates: [
    // insert mandates for selector here e.g. { id: 1, name: '2018–2022', url: 'https://x.parlameter.si' },
  ],
  locale: 'hr',
  leaderId: process.env.PARLASITE_LEADER_ID,
  rootOrgId: process.env.PARLASITE_ROOT_ORG_ID,
  mandateId: process.env.PARLASITE_MANDATE_ID,
  defaultCardDate: process.env.PARLASITE_DEFAULT_CARD_DATE,
  newsletterSegmentId: process.env.PARLASITE_NEWSLETTER_SEGMENT_ID,
};

if (!config.leaderId || !config.rootOrgId || !config.mandateId) {
  throw new Error('Required config values are not defined!');
}

module.exports = config;
