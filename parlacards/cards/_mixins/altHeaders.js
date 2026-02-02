import { assign } from 'lodash-es';
import sessionClassification from '@/_helpers/sessionClassification.js';

function getCardTitle(comp) {
  const { cardState } = comp.$root.$options.contextData;

  let cardTitle;
  if (cardState?.cardTitle) {
    cardTitle = cardState.cardTitle;
  } else if (cardState?.cardTitleKey && comp.$te(cardState?.cardTitleKey)) {
    cardTitle = comp.$t(cardState?.cardTitleKey);
  } else {
    cardTitle = comp.$t('card.title');
  }
  return cardTitle;
}

export const personHeader = {
  computed: {
    headerConfig() {
      const { cardData, cardState } = this.$root.$options.contextData;
      const person = cardData?.data?.person || {};
      return {
        circlePerson: person,
        heading: person.name,
        subheading: person.group?.is_in_coalition
          ? `${person.group?.acronym} | ${this.$t('coalition')}`
          : person.group?.acronym,
        alternative: cardState?.altHeader,
        title: getCardTitle(this),
      };
    },
  },
};

export const partyHeader = {
  computed: {
    headerConfig() {
      const { cardData, cardState } = this.$root.$options.contextData;
      const group = cardData?.data?.group || {};
      return {
        mediaImage: 'party',
        circleColor: group.color,
        heading: group.name,
        subheading: group.is_in_coalition
          ? `${group.acronym} | ${this.$t('coalition')}`
          : group.acronym,
        alternative: cardState?.altHeader,
        title: getCardTitle(this),
      };
    },
  },
};

export const searchHeader = {
  computed: {
    headerConfig() {
      const { cardState } = this.$root.$options.contextData;
      return {
        circleIcon: 'og-search',
        heading: `"${cardState.text}"`,
        alternative: cardState?.altHeader,
        title: getCardTitle(this),
      };
    },
  },
};

export const sessionHeader = {
  computed: {
    headerConfig() {
      const { cardState } = this.$root.$options.contextData;
      const session = this.cardData.data?.session;
      const sessionName = session?.name || '';
      const imageName = sessionClassification(session?.classification).icon;

      return {
        mediaImage: imageName,
        circleColor: '#ffffff',
        heading: sessionName,
        subheading: session?.date,
        alternative: cardState?.altHeader,
        title: getCardTitle(this),
      };
    },
  },
};

export const defaultHeaderConfig = (comp, overrides = {}) => {
  const { cardState } = comp.$root.$options.contextData;

  let cardTitle = getCardTitle(comp);
  const { titleSuffix, ...otherOverrides } = overrides;
  if (titleSuffix) {
    cardTitle = `${cardTitle} ${titleSuffix}`;
  }

  const headerConfig = {
    circleIcon: 'og-list',
    heading: '&nbsp;',
    subheading: '',
    alternative: cardState?.altHeader,
    title: cardTitle,
  };
  return assign({}, headerConfig, otherOverrides);
};

export const defaultDynamicHeaderConfig = (comp, overrides = {}) => {
  const { cardState } = comp.$root.$options.contextData;

  let cardTitle = getCardTitle(comp);
  const { titleSuffix, ...otherOverrides } = overrides;
  if (titleSuffix) {
    cardTitle = `${cardTitle} ${titleSuffix}`;
  }

  const headerConfig = {
    circleIcon: 'og-list',
    heading: '&nbsp;',
    subheading: '',
    alternative: cardState?.altHeader,
    title: cardTitle,
  };
  return assign({}, headerConfig, otherOverrides);
};
