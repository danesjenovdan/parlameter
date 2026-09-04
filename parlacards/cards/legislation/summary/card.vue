<template>
  <card-wrapper :header-config="headerConfig" max-height>
    <div class="legislation-summary">
      <Excerpt :content="summary.text || 'N/A'" :show-parent="false" />
    </div>
  </card-wrapper>
</template>

<script>
import common from '@/_mixins/common.js';
import links from '@/_mixins/links.js';
import { defaultHeaderConfig } from '@/_mixins/altHeaders.js';
import Excerpt from '@/_components/Excerpt.vue';

export default {
  name: 'CardLegislationSummary',
  components: {
    Excerpt,
  },
  mixins: [common, links],
  cardInfo: {
    doubleWidth: true,
  },
  data() {
    const { cardData } = this.$root.$options.contextData;

    return {
      summary: cardData?.data?.results?.summary || {},
      legislation: cardData?.data?.legislation || {},
      headerConfig: defaultHeaderConfig(this, {
        heading: cardData?.data?.mandate?.description,
        // title:
      }),
    };
  },
};
</script>

<style lang="scss" scoped>
@use 'parlassets/scss/colors';
@use 'parlassets/scss/breakpoints';

.legislation-summary :deep(.excerpt) {
  margin-top: 0;
  margin-bottom: 20px;
  min-height: breakpoints.$half-card-height;
  height: auto;

  .rich-text {
    max-height: initial;
    padding-left: 0;
    padding-right: 0;
  }
}
</style>
