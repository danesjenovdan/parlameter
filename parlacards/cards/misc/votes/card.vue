<template>
  <card-wrapper :header-config="headerConfig" max-height>
    <div class="votes-list">
      <div class="filters">
        <div class="filter text-filter">
          <div v-t="'title-search'" class="filter-label"></div>
          <search-field v-model="textFilter" />
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
          class="votes-list-shadow has-filters"
          @scroll="$refs.shadow.check($event.currentTarget)"
        >
          <div v-if="!filteredVotes.length" class="empty-container">
            <empty-state />
          </div>
          <vote-list-item
            v-for="vote in filteredVotes"
            :key="vote.id"
            :vote="vote"
          />
        </div>
      </scroll-shadow>
    </div>
  </card-wrapper>
</template>

<script>
import common from '@/_mixins/common.js';
import links from '@/_mixins/links.js';
import { defaultHeaderConfig } from '@/_mixins/altHeaders.js';
import { legislationListContextUrl } from '@/_mixins/contextUrls.js';
import SearchField from '@/_components/SearchField.vue';
import StripedButton from '@/_components/StripedButton.vue';
import ScrollShadow from '@/_components/ScrollShadow.vue';
import VoteListItem from '@/_components/VoteListItem.vue';
import EmptyState from '@/_components/EmptyState.vue';

export default {
  name: 'CardMiscVotes',
  components: {
    SearchField,
    StripedButton,
    ScrollShadow,
    VoteListItem,
    EmptyState,
  },
  mixins: [common, legislationListContextUrl, links],
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
      votes: cardData?.data?.results || [],
      passedOptions,
      textFilter,
      headerConfig: defaultHeaderConfig(this, {
        heading: cardData?.data?.mandate?.description,
      }),
    };
  },
  computed: {
    filteredVotes() {
      const lowerTextFilter = String(this.textFilter || '').toLowerCase();

      return this.votes.filter((vote) => {
        let textMatch = true;
        let passedOptionMatch = true;

        if (lowerTextFilter) {
          textMatch = vote.title.toLowerCase().includes(lowerTextFilter);
        }

        if (this.selectedPassedOption) {
          passedOptionMatch =
            this.selectedPassedOption.id === String(vote.passed);
        }

        return textMatch && passedOptionMatch;
      });
    },
    selectedPassedOption() {
      return this.passedOptions.find((po) => po.selected);
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
    },
  },
};
</script>

<style lang="scss" scoped>
@use 'parlassets/scss/breakpoints';

.empty-container {
  position: relative;
  min-height: 265px;
}

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

      .striped-button {
        width: 120px;
      }
    }
  }
}
</style>
