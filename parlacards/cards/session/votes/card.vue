<template>
  <card-wrapper :header-config="headerConfig">
    <div class="votes-list">
      <div class="filters">
        <div class="filter text-filter">
          <div v-t="'title-search'" class="filter-label"></div>
          <search-field
            v-model="textFilter"
            @update:model-value="searchVotes"
          />
        </div>
        <div class="filter" style="flex: 1"></div>
        <div class="filter buttons-filter">
          <striped-button
            v-for="passedOption in passedOptions"
            :key="passedOption.id"
            :color="passedOption.color"
            :selected="selectedPassedOption === passedOption"
            :small-text="passedOption.label"
            @click="selectPassedOption(passedOption)"
          />
        </div>
      </div>
      <scroll-shadow ref="shadow">
        <div
          v-infinite-scroll="loadMore"
          class="votes-list-shadow has-filters"
          @scroll="$refs.shadow.check($event.currentTarget)"
        >
          <empty-state v-if="!votes.length && !card.isLoading" />
          <template v-else>
            <vote-list-item
              v-for="vote in votes"
              :key="vote.id"
              :vote="vote"
              :session="session"
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
import common from '@/_mixins/common.js';
import cancelableRequest from '@/_mixins/cancelableRequest.js';
import links from '@/_mixins/links.js';
import { sessionHeader } from '@/_mixins/altHeaders.js';
import { sessionOgImage } from '@/_mixins/ogImages.js';
import { sessionVotesContextUrl } from '@/_mixins/contextUrls.js';
import SearchField from '@/_components/SearchField.vue';
import StripedButton from '@/_components/StripedButton.vue';
import ScrollShadow from '@/_components/ScrollShadow.vue';
import VoteListItem from '@/_components/VoteListItem.vue';
import EmptyState from '@/_components/EmptyState.vue';
import infiniteScroll from '@/_directives/infiniteScroll.js';
import { debounce } from 'lodash-es';

export default {
  name: 'CardSessionVotes',
  directives: {
    infiniteScroll,
  },
  components: {
    SearchField,
    StripedButton,
    ScrollShadow,
    VoteListItem,
    EmptyState,
  },
  mixins: [
    common,
    sessionVotesContextUrl,
    sessionHeader,
    sessionOgImage,
    links,
    cancelableRequest,
  ],
  cardInfo: {
    doubleWidth: true,
  },
  data() {
    const { cardState, cardData } = this.$root.$options.contextData;

    const textFilter = cardState?.text || '';

    const passedOptions = [
      {
        id: 'true',
        color: 'binary-for',
        label: this.$t('vote-passed'),
        selected: cardState?.passed === 'true',
      },
      {
        id: 'false',
        color: 'binary-against',
        label: this.$t('vote-not-passed'),
        selected: cardState?.passed === 'false',
      },
    ];

    return {
      card: {
        objectCount: cardData?.data?.count,
        currentPage: 1,
        isLoading: false,
      },
      votes: cardData?.data?.results || [],
      session: cardData?.data?.session || {},
      passedOptions,
      textFilter,
    };
  },
  computed: {
    selectedPassedOption() {
      return this.passedOptions.find((po) => po.selected);
    },
    searchUrl() {
      const url = new URL(this.cardData.url);
      url.searchParams.set('page', this.card.currentPage);
      url.searchParams.set('text', this.textFilter);
      if (this.selectedPassedOption) {
        url.searchParams.set('passed', this.selectedPassedOption?.id);
      } else {
        url.searchParams.delete('passed');
      }
      return url.toString();
    },
  },
  methods: {
    selectPassedOption(passedOption) {
      if (passedOption.selected) {
        passedOption.selected = false;
      } else {
        this.passedOptions.forEach((po) => {
          po.selected = passedOption === po;
        });
      }
      this.searchVotesImmediate();
    },
    searchVotesImmediate() {
      this.card.isLoading = true;
      this.votes = [];
      this.card.objectCount = 0;
      this.card.currentPage = 1;
      this.makeRequest(this.searchUrl).then((response) => {
        this.votes = response?.data?.results || [];
        this.card.objectCount = response?.data?.count;
        this.card.currentPage = 1;
        this.card.isLoading = false;
      });
    },
    searchVotes: debounce(function searchVotes() {
      this.searchVotesImmediate();
    }, 750),
    loadMore() {
      if (this.card.isLoading) {
        return;
      }
      if (this.votes.length >= this.card.objectCount) {
        return;
      }

      this.card.isLoading = true;
      this.card.currentPage += 1;

      const requestedPage = this.card.currentPage;
      this.makeRequest(this.searchUrl).then((response) => {
        if (response?.data?.page === requestedPage) {
          const newVotes = response?.data?.results || [];
          this.votes.push(...newVotes);
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

.votes-list {
  .filters {
    display: flex;
    padding-bottom: 12px;

    .filter {
      @include breakpoints.respond-to(desktop) {
        margin-right: 10px;
      }

      @include breakpoints.respond-to(mobile) {
        width: 100%;
      }

      &:last-child {
        margin-right: 0;
      }
    }

    .filter-label {
      overflow: hidden;
      height: 20px;
    }

    .text-filter {
      width: 100%;

      @include breakpoints.respond-to(desktop) {
        width: 50%;
      }
    }

    .buttons-filter {
      display: flex;
      align-items: flex-end;
      gap: 3px;

      @include breakpoints.respond-to(mobile) {
        display: none;
      }

      .striped-button {
        width: 120px;
      }
    }
  }

  .votes-list-shadow {
    overflow-y: auto;
    overflow-x: hidden;
    height: breakpoints.$full-card-height;

    &.has-filters {
      height: breakpoints.$full-card-height - 72;
    }
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
