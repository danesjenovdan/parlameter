<template>
  <card-wrapper :header-config="headerConfig">
    <div class="legislation-list">
      <scroll-shadow ref="shadow">
        <div
          v-infinite-scroll="loadMore"
          class="legislation-list-shadow"
          @scroll="$refs.shadow.check($event.currentTarget)"
        >
          <empty-state v-if="!legislation?.length" />
          <template v-else>
            <legislation-list-item
              v-for="law in legislation"
              :key="law.id"
              :law="law"
              :show-epa-column="showEpaColumn"
            />
          </template>
        </div>
        <div v-if="card.isLoading" class="nalagalnik__wrapper">
          <div class="nalagalnik"></div>
        </div>
      </scroll-shadow>
    </div>
  </card-wrapper>
</template>

<script>
import axios from 'axios';
import ScrollShadow from '@/_components/ScrollShadow.vue';
import EmptyState from '@/_components/EmptyState.vue';
import LegislationListItem from '@/_components/LegislationListItem.vue';
import common from '@/_mixins/common.js';
import { searchTitle } from '@/_mixins/titles.js';
import { searchHeader } from '@/_mixins/altHeaders.js';
import { searchOgImage } from '@/_mixins/ogImages.js';
import { searchContextUrl } from '@/_mixins/contextUrls.js';
import links from '@/_mixins/links.js';
import infiniteScroll from '@/_directives/infiniteScroll.js';

export default {
  name: 'CardSearchLegislation',
  directives: {
    infiniteScroll,
  },
  components: {
    ScrollShadow,
    EmptyState,
    LegislationListItem,
  },
  mixins: [
    common,
    searchContextUrl,
    searchTitle,
    searchHeader,
    searchOgImage,
    links,
  ],
  cardInfo: {
    doubleWidth: true,
  },
  data() {
    const { cardData, cardState } = this.$root.$options.contextData;

    return {
      card: {
        currentPage: 1,
        isLoading: false,
      },
      legislation: cardData?.data?.results || [],
      showEpaColumn:
        cardState?.showEpaColumn && cardState?.showEpaColumn !== 'false',
    };
  },
  computed: {
    searchUrl() {
      const url = new URL(this.cardData.url);
      url.searchParams.set('page', this.card.currentPage);
      return url.toString();
    },
  },
  methods: {
    loadMore() {
      if (this.card.isLoading) {
        return;
      }
      if (this.legislation.length >= this.cardData.data?.count) {
        return;
      }

      this.card.isLoading = true;
      this.card.currentPage += 1;

      const requestedPage = this.card.currentPage;
      axios.get(this.searchUrl).then((response) => {
        if (response?.data?.page === requestedPage) {
          const newLegislation = response?.data?.results || [];
          this.legislation.push(...newLegislation);
        }
        this.card.isLoading = false;
      });
    },
  },
};
</script>

<style lang="scss" scoped>
@use 'parlassets/scss/breakpoints';
@use 'parlassets/scss/colors';

.legislation-list {
  .legislation-list-shadow {
    overflow-y: auto;
    overflow-x: hidden;
    height: breakpoints.$full-card-height;
  }

  .nalagalnik__wrapper {
    position: absolute;
    top: 0;
    bottom: 0;
    left: 0;
    right: 0;
    background: colors.$white-hover;
    z-index: 4;

    .nalagalnik {
      position: absolute;
      top: calc(50% - 50px);
    }
  }
}
</style>
