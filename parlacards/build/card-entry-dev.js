import { createApp } from 'vue';
import { createI18n } from 'vue-i18n';
import { merge } from 'lodash-es';
import siteMap from '@/../build/sitemap-default.json';
/* eslint-disable import/no-unresolved */
import defaultMessages from '@/_i18n/{cardLang}/defaults.yaml';
import Card from './card.vue';
import cardData from './data.json';
import cardState from './state.json';
/* eslint-enable import/no-unresolved */

(async () => {
  let cardMessages = {};
  try {
    // eslint-disable-next-line import/no-unresolved
    const module = await import('@/_i18n/{cardLang}/{cardName}.yaml');
    cardMessages = module.default ?? {};
  } catch {
    // noop
  }

  const locale = '{cardLang}';
  const i18n = createI18n({
    locale,
    messages: {
      [locale]: merge({}, defaultMessages, cardMessages),
    },
  });

  const urls = {
    site: import.meta.env.VITE_PARLASITE_URL,
    cards: import.meta.env.VITE_PARLACARDS_URL,
    data: import.meta.env.VITE_PARLADATA_URL,
    cdn: import.meta.env.VITE_PARLASSETS_URL,
    metaImages: import.meta.env.VITE_METAIMAGES_URL,
  };

  const cardName = '{cardName}';
  const uid = Math.random().toString(36).slice(2);
  const mountId = `${cardName.replace(/\//g, '_')}__${uid}`;
  const contextData = {
    mountId,
    cardName,
    cardData,
    cardState,
    urls,
    siteMap,
  };

  window.card = createApp({ ...Card, contextData });
  window.card.use(i18n);
  window.card.mount('#card');

  const element = window.card._container.parentElement;
  const { template } = window.card._component.contextData;
  element.className = template.frameContainerClass;

  const templateDataElement = document.querySelector('#template-data');
  templateDataElement.innerHTML = JSON.stringify(template, null, 2);
  // eslint-disable-next-line no-console
})().catch((error) => console.error(error));
