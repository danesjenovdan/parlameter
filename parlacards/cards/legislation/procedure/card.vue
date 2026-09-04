<template>
  <card-wrapper :header-config="headerConfig">
    <div>TODO</div>
  </card-wrapper>
</template>

<script>
import common from '@/_mixins/common.js';
import links from '@/_mixins/links.js';
import { defaultHeaderConfig } from '@/_mixins/altHeaders.js';
import dateFormatter from '@/_helpers/dateFormatter.js';

export default {
  name: 'CardLegislationProcedure',
  mixins: [common, links],
  data() {
    const { cardData } = this.$root.$options.contextData;
    const results = cardData?.data?.results ?? {};

    return {
      results,
      headerConfig: defaultHeaderConfig(this, {
        heading: cardData?.data?.mandate?.description,
        // title: results?.legislation?.text,
      }),
    };
  },
  methods: {
    formatDate: dateFormatter,
  },
};
</script>

<style lang="scss" scoped>
@use 'parlassets/scss/breakpoints';
@use 'parlassets/scss/colors';
</style>
