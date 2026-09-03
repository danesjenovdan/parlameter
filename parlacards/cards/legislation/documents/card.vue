<template>
  <card-wrapper :header-config="headerConfig">
    <div class="legislation-documents">
      <documents :documents="documents" group-by="group" />
    </div>
  </card-wrapper>
</template>

<script>
import common from '@/_mixins/common.js';
import links from '@/_mixins/links.js';
import { defaultHeaderConfig } from '@/_mixins/altHeaders.js';
import Documents from '@/_components/Documents.vue';

export default {
  name: 'CardLegislationDocuments',
  components: {
    Documents,
  },
  mixins: [common, links],
  cardInfo: {
    doubleWidth: true,
  },
  data() {
    const { cardData } = this.$root.$options.contextData;

    return {
      documents: cardData?.data?.results || [],
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

.legislation-documents :deep(.documents) {
  margin-top: 0;
  height: breakpoints.$full-card-height;
}
</style>
