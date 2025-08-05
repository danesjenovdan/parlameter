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
        <div v-if="type === 'person'" class="filter buttons-filter">
          <striped-button
            v-for="voteOption in voteOptions"
            :key="voteOption.id"
            :color="voteOption.color"
            :selected="selectedVoteOptions.includes(voteOption)"
            :small-text="voteOption.label"
            @click="toggleVoteOption(voteOption)"
          />
        </div>
        <!-- <div v-if="type === 'party'" class="filter text-filter">
          <div v-t="'sort-by'" class="filter-label"></div>
          <toggle v-model="selectedSort" :options="sortOptions" />
        </div> -->
      </div>

      <scroll-shadow ref="shadow">
        <div
          v-infinite-scroll="loadMore"
          class="votes-list-shadow has-filters date-list"
          @scroll="$refs.shadow.check($event.currentTarget)"
        >
          <empty-state v-if="!card.isLoading && !ballots?.length" />
          <template v-for="(dayBallots, key) in votingDays" :key="key">
            <div
              v-if="type === 'person' || selectedSort === 'date'"
              class="date"
            >
              {{ formatDate(dayBallots[0].vote?.timestamp) }},
              {{ formatSessionInfo(dayBallots[0].vote?.session) }}
            </div>
            <template v-for="(ballot, i) in dayBallots">
              <ballot
                v-if="ballot.vote"
                :key="ballot.vote.id"
                :ballot="ballot"
                type="person"
              />
              <div v-else :key="`invalid-${i}`">
                Invalid ballot (no `vote` property)
              </div>
            </template>
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
import { debounce, groupBy } from 'lodash-es';
import common from '@/_mixins/common.js';
import cancelableRequest from '@/_mixins/cancelableRequest.js';
import { personHeader, partyHeader } from '@/_mixins/altHeaders.js';
import { personOgImage, partyOgImage } from '@/_mixins/ogImages.js';
import {
  personVotesContextUrl,
  partyVotesContextUrl,
} from '@/_mixins/contextUrls.js';
import { personTitle, partyTitle } from '@/_mixins/titles.js';
import SearchField from '@/_components/SearchField.vue';
import StripedButton from '@/_components/StripedButton.vue';
import ScrollShadow from '@/_components/ScrollShadow.vue';
import Ballot from '@/_components/Ballot.vue';
import EmptyState from '@/_components/EmptyState.vue';
import infiniteScroll from '@/_directives/infiniteScroll.js';
import dateFormatter from '@/_helpers/dateFormatter.js';
import sessionInfoFormatter from '@/_helpers/sessionInfoFormatter.js';

export default {
  name: 'Glasovanja',
  directives: {
    infiniteScroll,
  },
  components: {
    SearchField,
    StripedButton,
    ScrollShadow,
    Ballot,
    EmptyState,
  },
  mixins: [common, cancelableRequest],
  props: {
    type: {
      type: String,
      required: true,
      validator: (value) => ['person', 'party'].indexOf(value) > -1,
    },
  },
  data() {
    const { cardState, cardData } = this.$root.$options.contextData;

    const textFilter = cardState?.text || '';

    const allOptions = cardData?.data?.results?.all_options ?? {};

    const voteFilters = (cardState?.voteFilter || '').split(',');
    const voteOptions = [
      {
        id: 'for',
        color: 'for',
        label: this.$t('vote-for'),
        selected: voteFilters.includes('for'),
      },
      {
        id: 'against',
        color: 'against',
        label: this.$t('vote-against'),
        selected: voteFilters.includes('against'),
      },
      {
        id: 'abstain',
        color: 'abstain',
        label:
          this.type === 'person'
            ? this.$t('vote-abstain')
            : this.$t('vote-abstain-plural'),
        selected: voteFilters.includes('abstain'),
      },
      {
        id: 'absent',
        color: 'absent',
        label:
          this.type === 'person'
            ? this.$t('vote-absent')
            : this.$t('vote-absent-plural'),
        selected: voteFilters.includes('absent'),
      },
    ];
    if ((allOptions['did not vote'] ?? 0) > 0) {
      voteOptions.push({
        id: 'did not vote',
        color: 'did-not-vote',
        label:
          this.type === 'person'
            ? this.$t('vote-did-not-vote')
            : this.$t('vote-did-not-vote-plural'),
        selected: voteFilters.includes('did not vote'),
      });
    }

    return {
      card: {
        objectCount: cardData?.data?.['ballots:count'] ?? 0,
        currentPage: 1,
        isLoading: false,
      },
      ballots: cardData?.data?.results?.ballots ?? [],
      textFilter,
      voteOptions,
      selectedSort: 'date',
      // sortOptions: {
      //   maximum: this.$t('sort-by--inequality'),
      //   date: this.$t('sort-by--date'),
      // },
      // TODO: neenakost filter pri grupah
    };
  },
  computed: {
    selectedVoteOptions() {
      return this.voteOptions.filter((vo) => vo.selected);
    },
    votingDays() {
      let form = 'plural';
      if (this.type === 'person') {
        const person = this.cardData.data?.person;
        form = person?.preferred_pronoun === 'she' ? 'f' : 'm';
      }

      const ballots = this.ballots
        .filter((ballot) => ballot.option != null) // api returns null if nobody from this group voted
        .map((ballot) => {
          const optionLabel = (ballot.option || '').replace(/\s+/g, '-');
          return {
            ...ballot,
            label: this.$t(`voted-${optionLabel}--${form}`),
          };
        });

      return groupBy(ballots, (ballot) => {
        const dateTime = ballot.vote?.timestamp || '';
        const date = dateTime.split('T')[0];
        return `${date}__${ballot.vote?.session?.id}`;
      });
    },
    headerConfig() {
      if (this.type === 'person') {
        return personHeader.computed.headerConfig.call(this);
      }
      return partyHeader.computed.headerConfig.call(this);
    },
    searchUrl() {
      const url = new URL(this.cardData.url);
      url.searchParams.set('ballots:page', this.card.currentPage);
      url.searchParams.set('text', this.textFilter);
      if (this.selectedVoteOptions.length) {
        const voteOptions = this.selectedVoteOptions
          .map((vo) => vo.id)
          .join(',');
        url.searchParams.set('options', voteOptions);
      } else {
        url.searchParams.delete('options');
      }
      return url.toString();
    },
  },
  created() {
    (this.type === 'person'
      ? personVotesContextUrl
      : partyVotesContextUrl
    ).created.call(this);
    (this.type === 'person' ? personTitle : partyTitle).created.call(this);
    (this.type === 'person' ? personOgImage : partyOgImage).created.call(this);
  },
  methods: {
    toggleVoteOption(voteOption) {
      voteOption.selected = !voteOption.selected;
      this.searchVotesImmediate();
    },
    searchVotesImmediate() {
      this.card.isLoading = true;
      this.ballots = [];
      this.card.objectCount = 0;
      this.card.currentPage = 1;
      this.makeRequest(this.searchUrl).then((response) => {
        this.ballots = response?.data?.results?.ballots || [];
        this.card.objectCount = response?.data?.['ballots:count'];
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
      if (this.ballots.length >= this.card.objectCount) {
        return;
      }

      this.card.isLoading = true;
      this.card.currentPage += 1;

      const requestedPage = this.card.currentPage;
      this.makeRequest(this.searchUrl).then((response) => {
        if (response?.data?.['ballots:page'] === requestedPage) {
          const newBallots = response?.data?.results?.ballots || [];
          this.ballots.push(...newBallots);
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
    }

    .text-filter {
      flex-basis: 100%;

      @include breakpoints.respond-to(desktop) {
        flex-basis: 50%;
        flex-grow: 0;
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
        width: 90px;
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
