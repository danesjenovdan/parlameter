<template>
  <card-wrapper :header-config="headerConfig">
    <div class="speeches">
      <scroll-shadow ref="shadow">
        <div
          v-infinite-scroll="loadMore"
          class="speeches-list-shadow"
          @scroll="$refs.shadow.check($event.currentTarget)"
        >
          <empty-state v-if="!card.isLoading && !agendaItems?.length" />
          <div v-for="(dayAgendas, key) in groupAgendaDays" :key="key">
            <div class="date">
              {{ formatDate(dayAgendas[0].session?.start_time) }},
              {{ formatSessionInfo(dayAgendas[0].session) }}
            </div>
            <ul class="speeches__list">
              <search-minutes-item
                v-for="agendaItem in dayAgendas"
                :key="agendaItem.id"
                :agenda-item="agendaItem"
              />
            </ul>
          </div>
        </div>
        <div v-if="card.isLoading" class="nalagalnik__wrapper">
          <div class="nalagalnik"></div>
        </div>
      </scroll-shadow>
    </div>
  </card-wrapper>
</template>

<script>
import { groupBy } from 'lodash-es';
import SearchMinutesItem from '@/_components/SearchMinutesItem.vue';
import ScrollShadow from '@/_components/ScrollShadow.vue';
import EmptyState from '@/_components/EmptyState.vue';
import common from '@/_mixins/common.js';
import cancelableRequest from '@/_mixins/cancelableRequest.js';
import { searchTitle } from '@/_mixins/titles.js';
import { searchHeader } from '@/_mixins/altHeaders.js';
import { searchOgImage } from '@/_mixins/ogImages.js';
import { searchContextUrl } from '@/_mixins/contextUrls.js';
import infiniteScroll from '@/_directives/infiniteScroll.js';
import dateFormatter from '@/_helpers/dateFormatter.js';
import sessionInfoFormatter from '@/_helpers/sessionInfoFormatter.js';

export default {
  name: 'SearchMinutes',
  directives: {
    infiniteScroll,
  },
  components: {
    SearchMinutesItem,
    ScrollShadow,
    EmptyState,
  },
  mixins: [
    common,
    cancelableRequest,
    searchHeader,
    searchContextUrl,
    searchTitle,
    searchOgImage,
  ],
  data() {
    const { cardState, cardData } = this.$root.$options.contextData;

    return {
      card: {
        objectCount: cardData?.data?.count,
        currentPage: 1,
        isLoading: false,
      },
      agendaItems: cardData?.data?.results || [],
      textFilter: cardState?.text || '',
    };
  },
  computed: {
    searchUrl() {
      const url = new URL(this.cardData.url);
      url.searchParams.set('text', this.textFilter);
      url.searchParams.set('page', this.card.currentPage);
      return url.toString();
    },
    groupAgendaDays() {
      return groupBy(this.agendaItems, (item) => {
        const dateTime = item.session?.start_time || '';
        const date = dateTime.split('T')[0];
        return `${date}__${item.session?.id}`;
      });
    },
  },
  methods: {
    loadMore() {
      if (this.card.isLoading) {
        return;
      }
      if (this.agendaItems.length >= this.card.objectCount) {
        return;
      }

      this.card.isLoading = true;
      this.card.currentPage += 1;

      const requestedPage = this.card.currentPage;
      this.makeRequest(this.searchUrl).then((response) => {
        if (response?.data?.page === requestedPage) {
          const newAgendaItems = response?.data?.results || [];
          this.agendaItems.push(...newAgendaItems);
        }
        this.card.isLoading = false;
      });
    },
    formatDate: dateFormatter,
    formatSessionInfo: sessionInfoFormatter,
  },
};
</script>

<style lang="scss" scoped>
@use 'parlassets/scss/breakpoints';
@use 'parlassets/scss/colors';

.speeches {
  .speeches-list-shadow {
    overflow-y: auto;
    overflow-x: hidden;
    height: breakpoints.$full-card-height;
  }

  &__list {
    padding: 0 0 10px;
    margin: 0;
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

  .date {
    background-color: colors.$background;
    font-weight: bold;
    padding: 10px;
  }
}
</style>
