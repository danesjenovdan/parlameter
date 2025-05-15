<template>
  <card-wrapper :header-config="headerConfig">
    <div v-if="type !== 'search'" class="filters">
      <div class="filter text-filter">
        <div v-t="'contents-search'" class="filter-label"></div>
        <search-field
          v-model="textFilter"
          @update:model-value="searchSpeeches"
        />
      </div>
      <div v-if="type === 'party' && allPeople.length" class="filter">
        <div v-t="'mps'" class="filter-label"></div>
        <p-search-dropdown
          v-model="allPeople"
          @update:model-value="searchSpeechesImmediate"
        />
      </div>
      <div class="filter">
        <div v-t="'time-period'" class="filter-label"></div>
        <p-search-dropdown
          v-model="allMonths"
          :alphabetise="false"
          :placeholder-func="getMonthsPlaceholder"
          @update:model-value="searchSpeechesImmediate"
          @clear="searchSpeechesImmediate"
        />
      </div>
      <div v-if="allWorkingBodies.length" class="filter">
        <div v-t="'session-type'" class="filter-label"></div>
        <p-search-dropdown
          v-model="allWorkingBodies"
          @update:model-value="searchSpeechesImmediate"
          @clear="searchSpeechesImmediate"
        />
      </div>
    </div>

    <div class="speeches">
      <scroll-shadow ref="shadow">
        <div
          v-infinite-scroll="loadMore"
          :class="[
            'speeches-list-shadow',
            { 'has-filters': type !== 'search' },
          ]"
          @scroll="$refs.shadow.check($event.currentTarget)"
        >
          <empty-state v-if="!card.isLoading && !speeches?.length" />
          <div v-for="(daySpeeches, key) in groupSpeakingDays" :key="key">
            <div class="date">
              {{ formatDate(daySpeeches[0].start_time) }},
              {{ formatSessionInfo(daySpeeches[0].session) }}
            </div>
            <ul class="speeches__list">
              <govor
                v-for="speech in daySpeeches"
                :key="speech.id"
                :speech="speech"
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
import { groupBy, debounce } from 'lodash-es';
import Govor from '@/_components/Govor.vue';
import SearchField from '@/_components/SearchField.vue';
import PSearchDropdown from '@/_components/SearchDropdown.vue';
import ScrollShadow from '@/_components/ScrollShadow.vue';
import EmptyState from '@/_components/EmptyState.vue';
import generateMonths from '@/_helpers/generateMonths.js';
import common from '@/_mixins/common.js';
import cancelableRequest from '@/_mixins/cancelableRequest.js';
import { personTitle, partyTitle, searchTitle } from '@/_mixins/titles.js';
import {
  personHeader,
  partyHeader,
  searchHeader,
} from '@/_mixins/altHeaders.js';
import {
  personOgImage,
  partyOgImage,
  searchOgImage,
} from '@/_mixins/ogImages.js';
import {
  personSpeechesContextUrl,
  partySpeechesContextUrl,
  searchContextUrl,
} from '@/_mixins/contextUrls.js';
import infiniteScroll from '@/_directives/infiniteScroll.js';
import dateFormatter from '@/_helpers/dateFormatter.js';
import sessionInfoFormatter from '@/_helpers/sessionInfoFormatter.js';
import getD3Locale from '@/_i18n/d3locales.js';

export default {
  directives: {
    infiniteScroll,
  },
  components: {
    SearchField,
    PSearchDropdown,
    Govor,
    ScrollShadow,
    EmptyState,
  },
  mixins: [common, cancelableRequest],
  props: {
    type: {
      type: String,
      required: true,
      validator: (value) => ['person', 'party', 'search'].includes(value),
    },
  },
  data() {
    const { cardState, cardData } = this.$root.$options.contextData;

    const allPeople = [];

    const { months } = getD3Locale(this.$i18n.locale);
    const start = cardData?.data?.mandate?.beginning;
    const allMonths = generateMonths(months, start);
    allMonths.forEach((month) => {
      month.selected = (cardState?.months || []).includes(month.id);
    });

    const allWorkingBodies = (cardData?.organizations || []).map((org) => ({
      label: org.name,
      id: org.id,
      selected: (cardState?.wb || []).indexOf(org.id) !== -1,
    }));

    const textFilter = cardState?.text || '';

    return {
      card: {
        objectCount: cardData?.data?.count,
        currentPage: 1,
        isLoading: false,
      },
      speeches: cardData?.data?.results || [],
      textFilter,
      allMonths,
      allWorkingBodies,
      allPeople,
    };
  },
  computed: {
    searchUrl() {
      const url = new URL(this.cardData.url);

      const months = this.selectedMonths.map((m) => m.id).join(',');
      url.searchParams.set('months', months);

      url.searchParams.set('text', this.textFilter);

      url.searchParams.set('page', this.card.currentPage);

      return url.toString();
    },
    selectedWorkingBodies() {
      return this.allWorkingBodies.filter((session) => session.selected);
    },
    selectedMonths() {
      return this.allMonths.filter((month) => month.selected);
    },
    selectedPeople() {
      return this.allPeople.filter((person) => person.selected);
    },
    groupSpeakingDays() {
      return groupBy(this.speeches, (speech) => {
        const dateTime = speech.start_time || speech.session?.start_time || '';
        const date = dateTime.split('T')[0];
        return `${date}__${speech.session?.id}`;
      });
    },
    headerConfig() {
      if (this.type === 'person') {
        return personHeader.computed.headerConfig.call(this);
      }
      if (this.type === 'party') {
        return partyHeader.computed.headerConfig.call(this);
      }
      return searchHeader.computed.headerConfig.call(this);
    },
  },
  created() {
    if (this.type === 'person') {
      personSpeechesContextUrl.created.call(this);
      personTitle.created.call(this);
      personOgImage.created.call(this);
      return;
    }
    if (this.type === 'party') {
      partySpeechesContextUrl.created.call(this);
      partyTitle.created.call(this);
      partyOgImage.created.call(this);
      return;
    }
    searchContextUrl.created.call(this);
    searchTitle.created.call(this);
    searchOgImage.created.call(this);
  },
  methods: {
    getMonthsPlaceholder(selectedItems) {
      if (!selectedItems?.length) {
        return this.$t('whole-term');
      }
      return false;
    },
    searchSpeechesImmediate() {
      this.card.isLoading = true;
      this.speeches = [];
      this.card.objectCount = 0;
      this.card.currentPage = 1;
      this.makeRequest(this.searchUrl).then((response) => {
        this.speeches = response?.data?.results || [];
        this.card.objectCount = response?.data?.count;
        this.card.currentPage = 1;
        this.card.isLoading = false;
      });
    },
    searchSpeeches: debounce(function searchSpeeches() {
      this.searchSpeechesImmediate();
    }, 750),
    loadMore() {
      if (this.card.isLoading) {
        return;
      }
      if (this.speeches.length >= this.card.objectCount) {
        return;
      }

      this.card.isLoading = true;
      this.card.currentPage += 1;

      const requestedPage = this.card.currentPage;
      this.makeRequest(this.searchUrl).then((response) => {
        if (response?.data?.page === requestedPage) {
          const newSpeeches = response?.data?.results || [];
          this.speeches.push(...newSpeeches);
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

.filters {
  display: flex;
  padding-bottom: 12px;

  @include breakpoints.respond-to(mobile) {
    flex-wrap: wrap;
    min-height: 154px;
  }

  .filter {
    @include breakpoints.respond-to(desktop) {
      margin-right: 10px;
      flex: 1;
    }

    @include breakpoints.respond-to(mobile) {
      width: 100%;
    }

    &:last-child {
      margin-right: 0;
    }

    .filter-label {
      height: 20px;
    }
  }

  .text-filter {
    flex-basis: 100%;

    @include breakpoints.respond-to(desktop) {
      flex-basis: 50%;
      flex-grow: 0;
    }
  }
}

.speeches {
  .speeches-list-shadow {
    overflow-y: auto;
    overflow-x: hidden;
    height: breakpoints.$full-card-height;

    &.has-filters {
      height: breakpoints.$full-card-height - 72;
    }
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
