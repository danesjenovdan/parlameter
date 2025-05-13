<template>
  <card-wrapper :header-config="headerConfig">
    <template #generator>
      <tools-tabs current-tool="unity" />
    </template>

    <div class="votes-list">
      <div class="filters">
        <div class="left-filters">
          <div class="filter text-filter">
            <div v-t="'title-search'" class="filter-label"></div>
            <SearchField
              v-model="textFilter"
              @update:model-value="searchVotes"
            />
          </div>
          <div class="filter group-filter">
            <div v-t="'select-group'" class="filter-label"></div>
            <PSearchDropdown
              v-model="groups"
              single
              hide-clear
              @update:model-value="searchVotesImmediate"
            />
          </div>
          <div class="filter body-filter">
            <div v-t="'select-body'" class="filter-label"></div>
            <PSearchDropdown
              v-model="bodies"
              single
              hide-clear
              @update:model-value="searchVotesImmediate"
            />
          </div>
          <div class="filter month-filter">
            <div v-t="'select-time-period'" class="filter-label"></div>
            <PSearchDropdown
              v-model="allMonths"
              :alphabetise="false"
              :placeholder-func="getMonthsPlaceholder"
              @update:model-value="searchVotesImmediate"
              @clear="searchVotesImmediate"
            />
          </div>
        </div>
        <div class="right-filters">
          <div class="filter toggle-filter">
            <div v-t="'sort-by'" class="filter-label"></div>
            <Toggle v-model="selectedSort" :options="sortOptions" />
          </div>
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
            :href="getVoteLink({ id: vote.vote_id }, vote.session)"
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
                <a
                  :href="getSessionLink(vote.session)"
                  class="funblue-light-hover"
                  >{{ formatSessionInfo(vote.session) }}</a
                >,
                {{ formatDate(vote.timestamp) }}
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
import getD3Locale from '@/_i18n/d3locales.js';
import generateMonths from '@/_helpers/generateMonths.js';
import { capitalizeFirst } from '@/_helpers/stringCasing.js';

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

    const defaultGroupId = cardData.id;

    const textFilter = cardState?.text || '';
    const groupFilter = String(cardState?.group || defaultGroupId);
    const bodyFilter = String(cardState?.body || defaultGroupId);
    const monthsFilter = String(cardState?.months || '').split(',');

    const sortGroupsFunc = (a, b) => {
      if (a.classification === 'root') {
        return -1;
      }
      if (b.classification === 'root') {
        return 1;
      }
      if (a.classification === 'coalition') {
        return -1;
      }
      if (b.classification === 'coalition') {
        return 1;
      }
      return a.name.localeCompare(b.name);
    };

    const coalitionName = capitalizeFirst(this.$t('coalition'));
    const sortedGroups = (cardData?.data?.results?.groups || []).sort(
      sortGroupsFunc,
    );
    const sortedBodies = (cardData?.data?.results?.bodies || []).sort(
      sortGroupsFunc,
    );

    const groups = sortedGroups.map((g) => {
      const gid = (g.slug || '').split('-')[0];
      const isCoalition = g.classification === 'coalition';
      return {
        id: gid,
        slug: g.slug,
        label: isCoalition ? coalitionName : g.name,
        selected: gid === groupFilter,
        color: g.color,
      };
    });

    const bodies = sortedBodies.map((b) => {
      const bid = (b.slug || '').split('-')[0];
      const isCoalition = b.classification === 'coalition';
      return {
        id: bid,
        slug: b.slug,
        label: isCoalition ? coalitionName : b.name,
        selected: bid === bodyFilter,
      };
    });

    const { months } = getD3Locale(this.$i18n.locale);
    const start = cardData?.data?.mandate?.beginning;
    const allMonths = generateMonths(months, start);
    allMonths.forEach((month) => {
      month.selected = monthsFilter.includes(month.id);
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
      allMonths,
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
    selectedMonths() {
      return this.allMonths.filter((month) => month.selected);
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
      if (this.selectedMonths.length) {
        url.searchParams.set(
          'months',
          this.selectedMonths.map((m) => m.id).join(','),
        );
      } else {
        url.searchParams.delete('months');
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
  mounted() {
    if (
      this.textFilter ||
      this.selectedGroup?.id !== String(this.cardData.id) ||
      this.selectedBody?.id !== String(this.cardData.id) ||
      this.selectedMonths.length
    ) {
      this.searchVotesImmediate();
    }
  },
  methods: {
    getMonthsPlaceholder(selectedItems) {
      if (!selectedItems?.length) {
        return this.$t('whole-term');
      }
      return false;
    },
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
    justify-content: space-between;

    @include breakpoints.respond-to(up-to-limbo) {
      flex-wrap: wrap;
    }

    .left-filters,
    .right-filters {
      display: flex;
      gap: 6px 10px;
    }

    .left-filters {
      max-width: 700px;
      margin-right: 10px;

      @include breakpoints.respond-to(up-to-limbo) {
        max-width: 100%;
        margin-right: 0;
      }

      @include breakpoints.respond-to(mobile) {
        flex-wrap: wrap;
        margin-right: 0;
      }
    }

    // .right-filters {
    //   @include breakpoints.respond-to(up-to-limbo) {
    //     width: 100%;
    //     justify-content: flex-end;
    //   }
    // }

    .filter-label {
      overflow: hidden;
      height: 20px;
    }

    .text-filter {
      flex: 1;

      @include breakpoints.respond-to(mobile) {
        flex: 40% 1 0;
      }
    }

    .group-filter {
      flex: 1;

      @include breakpoints.respond-to(mobile) {
        flex: 40% 1 0;
      }
    }

    .body-filter {
      flex: 1;

      @include breakpoints.respond-to(mobile) {
        flex: 40% 1 0;
      }
    }

    .month-filter {
      flex: 1;

      @include breakpoints.respond-to(mobile) {
        flex: 40% 1 0;
      }
    }

    .toggle-filter {
      @include breakpoints.respond-to(up-to-limbo) {
        margin-top: 6px;
        flex: 100% 1 0;
      }
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
      text-align: center;
      min-width: 95px;

      @include breakpoints.respond-to(desktop) {
        flex-direction: column;
        justify-content: center;
        padding-right: 14px;
      }

      .percentage {
        font-size: 24px;
        line-height: 1;

        @include breakpoints.respond-to(desktop) {
          font-size: 30px;
        }
      }

      .text {
        font-size: 12px;
        line-height: 34px;
        font-weight: 600;
        margin-left: 10px;
        text-transform: uppercase;

        @include breakpoints.respond-to(desktop) {
          font-size: 14px;
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

      strong {
        font-weight: 300;
      }
    }

    .result {
      align-items: center;
      display: flex;
      justify-content: flex-start;
      padding: 10px 0 0 0;

      @include breakpoints.respond-to(desktop) {
        border-left: $section-border;
        justify-content: flex-start;
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
    height: breakpoints.$full-card-height - 72;
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
