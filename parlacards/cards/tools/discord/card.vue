<template>
  <card-wrapper :header-config="headerConfig">
    <template #generator>
      <tools-tabs current-tool="discord" />
    </template>

    <div class="filters">
      <!-- <div class="filter text-filter">
        <div v-t="'title-search'" class="filter-label"></div>
        <search-field v-model="textFilter" />
      </div> -->
      <div class="filter type-dropdown">
        <div v-t="'parties'" class="filter-label"></div>
        <p-search-dropdown v-model="groups" :single="true" hide-clear @update:model-value="fetchVotesForGroup" />
      </div>
      <!-- <div class="filter tag-dropdown">
        <div v-t="'working-body'" class="filter-label"></div>
        <p-search-dropdown v-model="allTags" />
      </div> -->
      <div class="filter text-filter">
        <div v-t="'sort-by'" class="filter-label"></div>
        <toggle v-model="selectedSort" :options="sortOptions" />
      </div>
    </div>

    <scroll-shadow ref="shadow">
      <div v-infinite-scroll="loadMore" class="votes-list-shadow has-filters date-list"
        @scroll="$refs.shadow.check($event.currentTarget)">
        <empty-state v-if="!card.isLoading && !votes?.length" />
        <template v-for="(dayBallots, key) in votingDays" :key="key">
          <div v-if="selectedSort === 'date'" class="date">
            {{ formatDate(dayBallots[0].timestamp) }},
            {{ formatSessionInfo(dayBallots[0].session) }}
          </div>
          <a v-for="vote in dayBallots" :key="vote.vote_id" :href="getVoteLink(vote.vote_id, vote.session)
            " :target="voteLinkTarget" class="ballot">
            <div class="disunion">
              <div class="percentage">{{ Math.round(100 - vote.value) }} %</div>
              <div v-t="'inequality'" class="text"></div>
            </div>
            <div class="name">
              {{ vote.title }}
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
        </template>
      </div>
      <div v-if="card.isLoading" class="nalagalnik__wrapper">
        <div class="nalagalnik"></div>
      </div>
    </scroll-shadow>
  </card-wrapper>
</template>

<script>
import { parseISO } from 'date-fns';
import { groupBy } from 'lodash-es';
import ToolsTabs from '@/_components/ToolsTabs.vue';
import PSearchDropdown from '@/_components/SearchDropdown.vue';
import StripedButton from '@/_components/StripedButton.vue';
import Toggle from '@/_components/Toggle.vue';
import common from '@/_mixins/common.js';
import links from '@/_mixins/links.js';
import { defaultHeaderConfig } from '@/_mixins/altHeaders.js';
import ScrollShadow from '@/_components/ScrollShadow.vue';
import infiniteScroll from '@/_directives/infiniteScroll.js';
import SearchField from '@/_components/SearchField.vue';
import { parseVoteTitle, shortenVoteTitle } from '@/_helpers/voteTitle.js';
import axios from 'axios';
import dateFormatter from '@/_helpers/dateFormatter.js';
import sessionInfoFormatter from '@/_helpers/sessionInfoFormatter.js';

export default {
  name: 'CardToolsDiscord',
  directives: {
    infiniteScroll,
  },
  components: {
    ToolsTabs,
    PSearchDropdown,
    StripedButton,
    Toggle,
    ScrollShadow,
    SearchField,
  },
  mixins: [common, links],
  cardInfo: {
    doubleWidth: true,
  },
  data() {
    const { cardState, cardData } = this.$root.$options.contextData;

    const initialGroups = cardData?.data?.results?.organizations ?? [];
    const groups = initialGroups.map((g) => {
      return {
        id: (g.slug || '').split('-')[0],
        slug: g.slug,
        label: g.name,
        selected: initialGroups.includes(g.slug),
        color: g.color,
      };
    });

    return {
      type: "vote",
      card: {
        objectCount: cardData?.data?.['results:count'] ?? 0,
        currentPage: 1,
        isLoading: false,
      },
      votes: cardData?.data?.results?.votes ?? [],
      selectedSort: 'date',
      sortOptions: {
        inequality: this.$t('sort-by--inequality'),
        date: this.$t('sort-by--date'),
      },
      groups: groups,
      // selectedGroup: groups[0]?.id,


      textFilter: '',
      allTags: [],

      allClassifications: [],
    };
  },
  computed: {
    // allItems() {
    //   return this.groups.map((group) => ({
    //     id: group.acronym,
    //     label: group.acronym,
    //     selected: group.acronym === this.selectedGroup,
    //     // colorClass: `${group.acronym
    //     //   .toLowerCase()
    //     //   .replace(/[ +,]/g, '_')}-background`,
    //   }));
    // },
    // selectedTags() {
    //   return this.allTags.filter((tag) => tag.selected).map((tag) => tag.id);
    // },
    selectedGroup() {
      const selectedGroup = this.groups.filter((g) => g.selected).map((g) => g.id);
      if (selectedGroup.length > 0) {
        return selectedGroup[0];
      } else {
        return this.groups[0].id;
      }
    },
    selectedClassifications() {
      return this.allClassifications
        .filter((classification) => classification.selected)
        .map((classification) => classification.id);
    },
    headerConfig() {
      return defaultHeaderConfig(this, {
        circleIcon: 'seznam-glasovanj',
        title: this.dynamicTitle,
      });
    },
    dynamicTitle() {
      return (
        this.$t('card.title') +
        (this.selectedSort === 'date'
          ? this.$t('sort-by--date').toLowerCase()
          : this.$t('sort-by--inequality').toLowerCase())
      );
    },
    voteLinkTarget() {
      if (typeof window !== 'undefined') {
        if (window === window.top) {
          return '_self';
        }
      }
      return '_blank';
    },
    votingDays() {
      if (this.selectedSort === 'date') {
        return groupBy(this.votes, (vote) => {
          const dateTime = vote.timestamp || '';
          const date = dateTime.split('T')[0];
          return `${date}__${vote.session?.id}`;
        });
      } else {
        return {"all": this.votes};
      }

    },
    searchUrl() {
      const url = new URL(this.cardData.url);
      url.searchParams.set('id', this.selectedGroup);
      url.searchParams.set('page', this.card.currentPage);
      url.searchParams.set('order_by', `${this.selectedSort}`);
      return url.toString();

      // url.searchParams.set('text', this.textFilter);
      // if (this.selectedVoteOptions.length) {
      //   const voteOptions = this.selectedVoteOptions
      //     .map((vo) => vo.id)
      //     .join(',');
      //   url.searchParams.set('options', voteOptions);
      // } else {
      //   url.searchParams.delete('options');
      // }
      // return url.toString();
    },
  },
  watch: {
    // selectedGroup(newValue) {
    //   this.fetchVotesForGroup();
    // },
    selectedSort(newValue) {
      this.fetchVotesForGroup();
    },
  },
  beforeMount() {
    this.fetchVotesForGroup();
  },
  methods: {
    // selectCallback(id) {
    //   this.selectGroup(id);
    // },
    // clearCallback() {
    //   this.selectGroup(this.groups[0].acronym);
    // },
    // selectGroup(id) {
    //   this.selectedGroup =
    //     this.selectedGroup !== id ? id : this.groups[0].id;
    // },
    fetchVotesForGroup() {
      // eslint-disable-next-line no-console
      console.log('fetch votes for group ', this.selectedGroup);

      this.card.isLoading = true;
      this.card.currentPage = 1;

      this.votes = []

      // const groupId = find(this.groups, { id })?.id;

      const requestedPage = this.card.currentPage;
      axios.get(this.searchUrl).then((response) => {
        if (response?.data?.page === requestedPage) {
          const newVotes = response?.data?.results?.votes || [];
          this.votes.push(...newVotes);
        }
        this.card.isLoading = false;
      });
    },
    loadMore() {
      console.log("Load more")
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

.votes-list-shadow {
  overflow-y: auto;
  overflow-x: hidden;
  height: breakpoints.$full-card-height - 89;
}

.groups {
  display: flex;
  flex-wrap: wrap;
  justify-content: space-between;
  margin-bottom: 16px;

  .striped-button {
    width: calc(33.33% - 3.33px);
    margin-bottom: 5px;

    @include breakpoints.respond-to(desktop) {
      flex: 1;
      margin-bottom: 0;

      &:not(:first-child) {
        margin-left: 5px;
      }
    }
  }
}

.filters {
  $label-height: 26px;

  display: flex;
  justify-content: space-between;
  margin-bottom: 20px;

  @include breakpoints.respond-to(mobile) {
    flex-wrap: wrap;
    min-height: 154px;
  }

  .filter-label {
    font-size: 14px;
    font-weight: 300;
    line-height: $label-height;
  }

  .text-filter {
    width: 100%;

    @include breakpoints.respond-to(desktop) {
      width: 26%;
    }
  }

  .tag-dropdown {
    width: 100%;

    @include breakpoints.respond-to(desktop) {
      width: 26%;
    }
  }

  .type-dropdown {
    width: 100%;

    @include breakpoints.respond-to(desktop) {
      width: 17.5%;
    }
  }
}

.results {
  height: 447px;
  overflow-y: auto;

  /*
  &.is-loading {
    overflow-y: hidden;
    position: relative;
    &::before {
      background: colors.$white url('#{get-parlassets-url()}/img/loader.gif') no-repeat
        center center;
      content: '';
      height: 100%;
      position: absolute;
      width: 100%;
      z-index: 1;
    }
  }
  */
}

.date-row {
  &:not(:first-child) {
    margin-top: 20px;
  }
}

.ballot {
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

  .disunion {
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

</style>
