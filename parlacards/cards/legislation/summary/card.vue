<template>
  <card-wrapper :header-config="headerConfig" max-height>
    <div class="legislation-summary">
      <template v-if="summary?.text">
        <Excerpt :content="summary.text" is-markdown :show-parent="false" />
        <div class="summary-info">
          <i18n-t
            v-if="summary?.ai_model_version"
            keypath="summary-created-info-ai"
            tag="div"
          >
            <template #date>
              <span class="date">{{ formatDate(summary?.updated_at) }}</span>
            </template>
            <template #model>
              <code>{{ summary?.ai_model_version }}</code>
            </template>
            <template #document>
              <a
                class="document"
                :href="summary?.link?.url"
                :title="summary?.link?.name"
                target="_blank"
                rel="noopener noreferrer"
                >{{ shortenDocumentName(summary?.link?.name) }}</a
              >
            </template>
          </i18n-t>
          <i18n-t v-else keypath="summary-created-info-human" tag="div">
            <template #date>
              <span class="date">{{ formatDate(summary?.updated_at) }}</span>
            </template>
            <template #document>
              <a
                class="document"
                :href="summary?.link?.url"
                :title="summary?.link?.name"
                target="_blank"
                rel="noopener noreferrer"
                >{{ shortenDocumentName(summary?.link?.name) }}</a
              >
            </template>
          </i18n-t>
        </div>
      </template>
      <div v-else-if="!summary?.link?.id" class="summary-empty">
        <EmptyState :text="$t('no-summary-no-document')" />
      </div>
      <div v-else-if="summary?.error" class="summary-empty">
        <EmptyState
          :text="$t('no-summary-error', { error: summary?.error || 'error' })"
        />
      </div>
      <div v-else class="summary-empty">
        <EmptyState :text="$t('no-summary')" />
      </div>
    </div>
  </card-wrapper>
</template>

<script>
import common from '@/_mixins/common.js';
import links from '@/_mixins/links.js';
import { defaultHeaderConfig } from '@/_mixins/altHeaders.js';
import Excerpt from '@/_components/Excerpt.vue';
import EmptyState from '@/_components/EmptyState.vue';
import dateFormatter from '@/_helpers/dateFormatter.js';

export default {
  name: 'CardLegislationSummary',
  components: {
    Excerpt,
    EmptyState,
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
  methods: {
    formatDate(date) {
      return dateFormatter(date);
    },
    shortenDocumentName(name) {
      if (!name || typeof name !== 'string') return name;
      // shorten name from center
      const maxLength = 50;
      if (name.length <= maxLength) return name;
      const half = Math.floor(maxLength / 2);
      return (
        name.slice(0, half).trim() + '…' + name.slice(name.length - half).trim()
      );
    },
  },
};
</script>

<style lang="scss" scoped>
@use 'parlassets/scss/colors';
@use 'parlassets/scss/breakpoints';

.legislation-summary {
  min-height: 265px;

  .summary-info {
    margin-bottom: 20px;
    font-size: 12px;
    font-weight: 400;

    .date {
      font-weight: 600;
    }
  }
}
</style>
