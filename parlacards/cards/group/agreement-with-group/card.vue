<template>
  <card-wrapper :header-config="headerConfig">
    <person-list :people="people" />
  </card-wrapper>
</template>

<script>
import common from '@/_mixins/common.js';
import { partyVotesContextUrl } from '@/_mixins/contextUrls.js';
import { partyTitle } from '@/_mixins/titles.js';
import { partyHeader } from '@/_mixins/altHeaders.js';
import { partyOgImage } from '@/_mixins/ogImages.js';
import PersonList from '@/_components/PersonList.vue';
import numberFormatter from '@/_helpers/numberFormatter.js';

export default {
  name: 'CardGroupAgreementWithGroup',
  components: {
    PersonList,
  },
  mixins: [common, partyVotesContextUrl, partyHeader, partyOgImage, partyTitle],
  data() {
    const { cardData } = this.$root.$options.contextData;

    const results = (cardData?.data?.results || [])
      .slice()
      .sort((a, b) => b.value - a.value);
    const people = results.map((entry) => ({
      ...entry.person,
      score: numberFormatter(entry.value, { percent: true }),
    }));
    return {
      people,
    };
  },
};
</script>
