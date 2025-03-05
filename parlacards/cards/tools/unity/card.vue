<template>
  <card-wrapper :header-config="headerConfig">
    <template #generator>
      <tools-tabs current-tool="unity" />
    </template>

    <div class="votes-list">
      <div class="filters">
        <div class="filter text-filter">
          <div v-t="'title-search'" class="filter-label"></div>
          <SearchField v-model="textFilter" @update:model-value="searchVotes" />
        </div>
        <div class="filter dropdown-filter">
          <div v-t="'party'" class="filter-label"></div>
          <PSearchDropdown
            v-model="groups"
            single
            @update:model-value="searchVotesImmediate"
          />
        </div>
        <div class="filter dropdown-filter">
          <div v-t="'working-body'" class="filter-label"></div>
          <PSearchDropdown
            v-model="bodies"
            single
            @update:model-value="searchVotesImmediate"
          />
        </div>
        <div class="filter toggle-filter">
          <div v-t="'sort-by'" class="filter-label"></div>
          <Toggle v-model="selectedSort" :options="sortOptions" />
        </div>
      </div>

      <scroll-shadow ref="shadow">
        <div
          v-infinite-scroll="loadMore"
          class="votes-list-shadow has-filters date-list"
          @scroll="$refs.shadow.check($event.currentTarget)"
        >
          <EmptyState v-if="!card.isLoading && !votes?.length" />
          <a
            v-for="vote in votes"
            :key="vote.vote_id"
            :href="getVoteLink(vote.vote_id, vote.session)"
            :target="voteLinkTarget"
            class="vote"
          >
            <div class="unity">
              <div class="percentage">{{ Math.round(vote.value) }} %</div>
              <div v-t="'unity'" class="text"></div>
            </div>
            <div class="name">
              {{ vote.title }}
              <br />
              <strong>
                {{ formatDate(vote.timestamp) }},
                {{ formatSessionInfo(vote.session) }}
              </strong>
            </div>
            <div class="result">
              <template v-if="vote.passed">
                <i class="accepted glyphicon glyphicon-ok"></i>
                <div v-t="'vote-passed'" class="text"></div>
              </template>
              <template v-else>
                <i class="not-accepted glyphicon glyphicon-remove"></i>
                <div v-t="'vote-not-passed'" class="text"></div>
              </template>
            </div>
          </a>
        </div>
        <div v-if="card.isLoading" class="nalagalnik__wrapper">
          <div class="nalagalnik"></div>
        </div>
      </scroll-shadow>
    </div>
  </card-wrapper>
</template>

<script>
import { debounce } from 'lodash-es';
import ToolsTabs from '@/_components/ToolsTabs.vue';
import EmptyState from '@/_components/EmptyState.vue';
import PSearchDropdown from '@/_components/SearchDropdown.vue';
import Toggle from '@/_components/Toggle.vue';
import SearchField from '@/_components/SearchField.vue';
import common from '@/_mixins/common.js';
import cancelableRequest from '@/_mixins/cancelableRequest.js';
import links from '@/_mixins/links.js';
import { defaultHeaderConfig } from '@/_mixins/altHeaders.js';
import ScrollShadow from '@/_components/ScrollShadow.vue';
import infiniteScroll from '@/_directives/infiniteScroll.js';
import dateFormatter from '@/_helpers/dateFormatter.js';
import sessionInfoFormatter from '@/_helpers/sessionInfoFormatter.js';

export default {
  name: 'CardToolsUnity',
  directives: {
    infiniteScroll,
  },
  components: {
    ToolsTabs,
    EmptyState,
    PSearchDropdown,
    Toggle,
    SearchField,
    ScrollShadow,
  },
  mixins: [common, cancelableRequest, links],
  cardInfo: {
    doubleWidth: true,
  },
  data() {
    const { cardState, cardData } = this.$root.$options.contextData;

    const textFilter = cardState?.text || '';

    const groups = (cardData?.data?.results?.groups || []).map((g) => {
      return {
        id: (g.slug || '').split('-')[0],
        slug: g.slug,
        label: g.name,
        selected: false,
        color: g.color,
      };
    });

    const bodies = (cardData?.data?.results?.bodies || []).map((b) => {
      return {
        id: (b.slug || '').split('-')[0],
        slug: b.slug,
        label: b.name,
        selected: false,
        color: b.color,
      };
    });

    return {
      headerConfig: defaultHeaderConfig(this),
      card: {
        objectCount: cardData?.data?.['votes:count'] ?? 0,
        currentPage: 1,
        isLoading: false,
      },
      votes: cardData?.data?.results?.votes ?? [],
      groups,
      bodies,
      textFilter,
      selectedSort: 'unity',
      sortOptions: {
        unity: this.$t('sort-by--unity'),
        disunity: this.$t('sort-by--disunity'),
      },
    };
  },
  computed: {
    selectedGroup() {
      return this.groups.find((g) => g.selected);
    },
    selectedBody() {
      return this.bodies.find((b) => b.selected);
    },
    voteLinkTarget() {
      if (typeof window !== 'undefined') {
        if (window === window.top) {
          return '_self';
        }
      }
      return '_blank';
    },
    searchUrl() {
      const url = new URL(this.cardData.url);
      url.searchParams.set('votes:page', this.card.currentPage);
      url.searchParams.set('text', this.textFilter);
      if (this.selectedGroup) {
        url.searchParams.set('group', this.selectedGroup.id);
      } else {
        url.searchParams.delete('group');
      }
      if (this.selectedBody) {
        url.searchParams.set('body', this.selectedBody.id);
      } else {
        url.searchParams.delete('body');
      }
      url.searchParams.set(
        'order_by',
        this.selectedSort === 'unity' ? '-value' : 'value',
      );
      return url.toString();
    },
  },
  watch: {
    selectedSort() {
      this.searchVotesImmediate();
    },
  },
  methods: {
    searchVotesImmediate() {
      this.card.isLoading = true;
      this.votes = [];
      this.card.objectCount = 0;
      this.card.currentPage = 1;
      this.makeRequest(this.searchUrl).then((response) => {
        this.votes = response?.data?.results?.votes || [];
        this.card.objectCount = response?.data?.['votes:count'];
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
        if (response?.data?.['votes:page'] === requestedPage) {
          const newVotes = response?.data?.results?.votes || [];
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
      margin-top: 6px;
    }

    .text-filter {
      flex-basis: 100%;
    }

    .dropdown-filter {
      flex-basis: 50%;
    }

    .toggle-filter {
      flex-basis: 25%;
    }
  }

  .vote {
    $section-border: 1px solid colors.$font-placeholder;
    background: colors.$background;
    color: colors.$font-default;
    display: block;
    margin: 7px 0 8px 0;
    min-height: 90px;
    padding: 10px 14px;
    position: relative;

    &:hover,
    &:active,
    &:focus {
      text-decoration: none;
      background: colors.$link-hover-background;
      color: colors.$link;
    }

    @include breakpoints.respond-to(desktop) {
      display: flex;
      margin: 10px 0;

      &:first-child {
        margin-top: 0;
      }
    }

    .unity {
      display: flex;
      justify-content: center;
      text-align: center;

      @include breakpoints.respond-to(desktop) {
        flex-direction: column;
        padding-right: 16px;
      }

      .percentage {
        font-size: 24px;

        @include breakpoints.respond-to(desktop) {
          font-size: 30px;
        }
      }

      .text {
        font-size: 13px;
        line-height: 34px;
        margin-left: 10px;
        text-transform: uppercase;

        @include breakpoints.respond-to(desktop) {
          font-size: 16px;
          line-height: 23px;
          margin-left: 0;
        }
      }
    }

    .name {
      border-bottom: $section-border;
      border-top: $section-border;
      font-family: 'Roboto Slab', 'Times New Roman', serif;
      font-size: 11px;
      font-weight: 300;
      line-height: 1.45em;
      padding: 10px 0;

      @include breakpoints.respond-to(desktop) {
        border-bottom: none;
        border-top: none;
        border-left: $section-border;
        display: flex;
        flex: 4;
        font-size: 14px;
        padding: 5px 20px;
        flex-direction: column;
        justify-content: center;
      }
    }

    .result {
      align-items: center;
      display: flex;
      justify-content: center;
      padding: 10px 0 0 0;

      @include breakpoints.respond-to(desktop) {
        border-left: $section-border;
        justify-content: left;
        padding: 0 0 0 16px;
        width: 136px;
      }

      .glyphicon {
        font-size: 24px;
        margin-bottom: 4px;

        &.accepted {
          color: colors.$icon-accepted;
        }

        &.not-accepted {
          color: colors.$icon-rejected;
        }

        @include breakpoints.respond-to(desktop) {
          font-size: 29px;
        }
      }

      .text {
        color: colors.$font-default;
        font-size: 14px;
        font-weight: bold;
        text-transform: uppercase;
        margin-left: 12px;
      }
    }
  }

  .votes-list-shadow {
    overflow-y: auto;
    overflow-x: hidden;
    height: breakpoints.$full-card-height - 89;
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
