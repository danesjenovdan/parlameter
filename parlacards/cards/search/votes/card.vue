<template>
  <card-wrapper :header-config="headerConfig">
    <div class="votes-list">
      <scroll-shadow ref="shadow">
        <div
          v-infinite-scroll="loadMore"
          class="votes-list-shadow date-list"
          @scroll="$refs.shadow.check($event.currentTarget)"
        >
          <empty-state v-if="!votes?.length" />
          <template v-for="(dayVotes, key) in votingDays" :key="key">
            <div class="date">
              {{ formatDate(dayVotes[0].timestamp) }},
              {{ formatSessionInfo(dayVotes[0].session) }}
            </div>
            <vote-list-item
              v-for="vote in dayVotes"
              :key="vote.id"
              :vote="vote"
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
import { groupBy } from 'lodash-es';
import axios from 'axios';
import common from '@/_mixins/common.js';
import { searchContextUrl } from '@/_mixins/contextUrls.js';
import { searchHeader } from '@/_mixins/altHeaders.js';
import { searchOgImage } from '@/_mixins/ogImages.js';
import { searchTitle } from '@/_mixins/titles.js';
import ScrollShadow from '@/_components/ScrollShadow.vue';
import VoteListItem from '@/_components/VoteListItem.vue';
import EmptyState from '@/_components/EmptyState.vue';
import infiniteScroll from '@/_directives/infiniteScroll.js';
import dateFormatter from '@/_helpers/dateFormatter.js';
import sessionInfoFormatter from '@/_helpers/sessionInfoFormatter.js';

export default {
  name: 'CardSearchVotes',
  directives: {
    infiniteScroll,
  },
  components: {
    ScrollShadow,
    VoteListItem,
    EmptyState,
  },
  mixins: [common, searchTitle, searchHeader, searchOgImage, searchContextUrl],
  cardInfo: {
    doubleWidth: true,
  },
  data() {
    const { cardData } = this.$root.$options.contextData;

    return {
      card: {
        currentPage: 1,
        isLoading: false,
      },
      votes: cardData?.data?.results,
    };
  },
  computed: {
    votingDays() {
      return groupBy(this.votes, (o) => {
        const dateTime = o.timestamp || o.session?.start_time || '';
        const date = dateTime.split('T')[0];
        return `${date}__${o.session?.id}`;
      });
    },
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
      if (this.votes.length >= this.cardData.data?.count) {
        return;
      }

      this.card.isLoading = true;
      this.card.currentPage += 1;

      const requestedPage = this.card.currentPage;
      axios.get(this.searchUrl).then((response) => {
        if (response?.data?.page === requestedPage) {
          const newVotes = response?.data?.results || [];
          this.votes.push(...newVotes);
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

.votes-list {
  .votes-list-shadow {
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
