import { assign } from 'lodash-es';
import sessionClassification from '@/_helpers/sessionClassification.js';
import stringifyParams from '@/_helpers/stringifyParams.js';
import dateFormatter from '@/_helpers/dateFormatter.js';

function getOgImageUrl(comp, type, params = {}) {
  const { urls } = comp.$root.$options.contextData;
  const url = `${urls.metaImages}/${type}`;
  const query = stringifyParams({ theme: comp.$i18n.locale, ...params });
  return `${url}${query}`;
}

export const personOgImage = {
  created() {
    const { template, cardData } = this.$root.$options.contextData;
    const person = cardData?.data?.person || {};
    template.ogImage = getOgImageUrl(this, 'circle', {
      title: this.$te('card.title') ? this.$t('card.title') : '',
      h1: person.name,
      h2: person.group?.name || person.group?.acronym || '',
      image: person.image,
    });
  },
};

export const partyOgImage = {
  created() {
    const { template, cardData } = this.$root.$options.contextData;
    const group = cardData?.data?.group || {};
    template.ogImage = getOgImageUrl(this, 'circle', {
      title: this.$te('card.title') ? this.$t('card.title') : '',
      h1: group.name,
      acronym: group.acronym,
    });
  },
};

export const sessionOgImage = {
  created() {
    const { template, urls, cardData } = this.$root.$options.contextData;
    const session =
      cardData?.data?.session || cardData?.data?.results?.session || {};
    template.ogImage = getOgImageUrl(this, 'circle', {
      title: this.$te('card.title') ? this.$t('card.title') : '',
      h1: session.name,
      h2: dateFormatter(session.start_time),
      icon: `${urls.cdn}/icons/${
        sessionClassification(session.classification).icon
      }.svg`,
    });
  },
};

export const searchOgImage = {
  created() {
    const { template, urls } = this.$root.$options.contextData;
    template.ogImage = getOgImageUrl(this, 'circle', {
      title: this.$te('card.title') ? this.$t('card.title') : '',
      // h1: this.keywords, // TODO: get from contextData not from this
      // h2: 'iskalni niz', // TODO: translate
      icon: `${urls.cdn}/icons/og-search.svg`,
    });
  },
};

export const defaultOgImage = (comp, overrides = {}) => {
  const { template, cardState } = comp.$root.$options.contextData;

  let cardTitle;
  if (cardState?.cardTitle) {
    cardTitle = cardState.cardTitle;
  } else if (cardState?.cardTitleKey && this.$te(cardState?.cardTitleKey)) {
    cardTitle = this.$t(cardState?.cardTitleKey);
  } else {
    cardTitle = this.$t('card.title');
  }

  const { titleSuffix, ...otherOverrides } = overrides;
  if (titleSuffix) {
    cardTitle = `${cardTitle} ${titleSuffix}`;
  }

  const obj = {
    title: cardTitle,
  };
  template.ogImage = getOgImageUrl(
    comp,
    'generic',
    assign({}, obj, otherOverrides),
  );
};
