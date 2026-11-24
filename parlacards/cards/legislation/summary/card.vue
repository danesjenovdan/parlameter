<template>
  <card-wrapper :header-config="headerConfig" max-height>
    <div class="legislation-summary">
      <div v-if="summary?.error" class="summary-empty">
        <EmptyState v-if="hasNoSummary(summary)" :text="$t('no-summary')" />
        <EmptyState
          v-else
          :text="$t('no-summary-error', { error: summary.error || 'error' })"
        />
      </div>
      <template v-else-if="summary?.text">
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
            <template #documents>
              <template v-for="(link, index) in summary.links">
                <a
                  class="document"
                  :href="link.url"
                  :title="link.name"
                  target="_blank"
                  rel="noopener noreferrer"
                  >{{ shortenDocumentName(link.name) }} </a
                >{{ index < summary.links.length - 1 ? ', ' : '' }}
              </template>
            </template>
          </i18n-t>
          <i18n-t v-else keypath="summary-created-info-human" tag="div">
            <template #date>
              <span class="date">{{ formatDate(summary?.updated_at) }}</span>
            </template>
            <template #documents>
              <template v-for="(link, index) in summary.links">
                <a
                  class="document"
                  :href="link.url"
                  :title="link.name"
                  target="_blank"
                  rel="noopener noreferrer"
                  >{{ shortenDocumentName(link.name) }} </a
                >{{ index < summary.links.length - 1 ? ', ' : '' }}
              </template>
            </template>
          </i18n-t>
        </div>
      </template>
      <div v-else-if="!summary?.links?.length" class="summary-empty">
        <EmptyState :text="$t('no-summary-no-document')" />
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
    hasNoSummary(summary) {
      return (
        summary?.error?.toLowerCase().includes('no approved summary') ||
        summary?.error == 'no_summary'
      );
    },
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
