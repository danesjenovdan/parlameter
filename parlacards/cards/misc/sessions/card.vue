<template>
  <card-wrapper ref="card" :header-config="headerConfig" max-height>
    <div class="filters">
      <div class="filter">
        <label class="filter-label">{{ $t('organization') }}</label>
        <PSearchDropdown
          v-model="workingBodies"
          single
          hide-clear
          class="dropdown-filter"
          @update:model-value="searchSessionsImmediate"
        />
      </div>
    </div>
    <div v-if="isLoading" class="nalagalnik"></div>
    <template v-else>
      <sortable-table
        :columns="columns"
        :items="mappedSessions"
        :sort="currentSort"
        :sort-order="currentSortOrder"
        :sort-callback="selectSort"
        class="session-list"
      />
      <pagination
        v-if="count > perPage"
        :page="page"
        :count="count"
        :per-page="perPage"
        @change="onPageChange"
      />
    </template>
  </card-wrapper>
</template>

<script>
// debounce is required for search field queries debouncing
import { debounce } from 'lodash-es';
import common from '@/_mixins/common.js';
import links from '@/_mixins/links.js';
import { sessionListContextUrl } from '@/_mixins/contextUrls.js';
import { defaultHeaderConfig } from '@/_mixins/altHeaders.js';
// cancelableRequest is how we make requests to update the results
import cancelableRequest from '@/_mixins/cancelableRequest.js';
import PSearchDropdown from '@/_components/SearchDropdown.vue';
import BlueButtonList from '@/_components/BlueButtonList.vue';
import Pagination from '@/_components/Pagination.vue';
import SortableTable from '@/_components/SortableTable.vue';
import { SESSIONS_PER_PAGE } from '@/_helpers/constants.js';
import dateFormatter from '@/_helpers/dateFormatter.js';
import sessionClassification from '@/_helpers/sessionClassification.js';
import sessionName from '@/_helpers/sessionName.js';

export default {
  name: 'CardMiscSessions',
  components: {
    PSearchDropdown,
    BlueButtonList,
    Pagination,
    SortableTable,
  },
  mixins: [common, links, sessionListContextUrl, cancelableRequest],
  cardInfo: {
    doubleWidth: true,
  },
  data() {
    const { cardState, cardData } = this.$root.$options.contextData;

    // check if we're embedded
    const isEmbedded = this.$root.$options.contextData.templateName === 'embed';

    const data = cardData?.data || {};
    let results = data.results?.sessions ?? [];
    let pages = data['sessions:pages'] ?? 1;
    const initialPage = data['sessions:page'] ?? 1;
    const count = data['sessions:count'] ?? results.length ?? 0;
    let perPage = data['sessions:per_page'] ?? SESSIONS_PER_PAGE;
    let page = Number(cardState?.page) || initialPage;

    // if we're embedded we should override our current settings
    if (isEmbedded) {
      pages = Math.ceil(count / 5);
      perPage = 5;
      page = page * 2 - 1;
      results = results.slice(0, 5);
    }

    // create array that has a size equal to number of pages to cache loaded pages
    const sessionsPerPage = Array(pages);
    sessionsPerPage[initialPage - 1] = results;

    const sortedOrgs = (cardData?.data?.results?.organizations || []).sort(
      (a, b) => {
        // make sure `house` comes first and `other` comes last
        if (a.classification !== b.classification) {
          if (a.classification === 'house') {
            return -1;
          }
          if (a.classification === 'other') {
            return 1;
          }
          if (b.classification === 'house') {
            return 1;
          }
          if (b.classification === 'other') {
            return -1;
          }
        }
        return 0;
      },
    );

    const defaultSelectedWorkingBody =
      sortedOrgs.find((org) => org.classification === 'house') ?? sortedOrgs[0];
    const workingBodies = sortedOrgs.map((org) => {
      return {
        id: (org.slug || '').split('-')[0],
        slug: org.slug,
        label: org.name,
        selected: defaultSelectedWorkingBody.slug === org.slug,
      };
    });

    const showEndDate = (() => {
      const value = String(cardState?.showEndDate);
      if (value === 'true') return true;
      if (value === 'false') return false;
      return false;
    })();

    return {
      workingBodies,
      currentSort: 'start_time',
      currentSortOrder: 'desc',
      headerConfig: defaultHeaderConfig(this, {
        heading: cardData?.data?.mandate?.description,
        title: this.$t('card.title'),
      }),
      showEndDate,
      // pagination
      pages,
      initialPage,
      count,
      perPage,
      isLoading: false,
      page,
      sessionsPerPage,
    };
  },
  computed: {
    searchUrl() {
      // cardData.url is automagically provided by the rendering pipeline
      const url = new URL(this.cardData.url);

      // set per-page setting
      url.searchParams.set('sessions:per_page', this.perPage);
      url.searchParams.set('sessions:page', this.page);

      if (this.currentWorkingBodies.length > 0) {
        url.searchParams.set(
          'organizations',
          this.currentWorkingBodies
            .map((workingBodySlug) => workingBodySlug.split('-')[0])
            .join(','),
        );
      }

      // set sort param
      const sortPrefix = this.currentSortOrder === 'desc' ? '-' : '';
      const sort = this.currentSort;
      url.searchParams.set('order_by', `${sortPrefix}${sort}`);
      console.log(url.toString());

      return url.toString();
    },
    columns() {
      const showOrgCol = false; //TODO

      return [
        { id: 'image', label: '', additionalClass: 'image' },
        {
          id: 'name',
          label: this.$t('title'),
          additionalClass: 'name no-sort',
        },
        {
          id: 'start_time',
          label: this.showEndDate ? this.$t('start-date') : this.$t('date'),
          additionalClass: this.showEndDate ? 'date date--start' : 'date',
        },
        this.showEndDate
          ? {
              id: 'end_time',
              label: this.$t('end-date'),
              additionalClass: 'date date--end optional',
            }
          : null,
        // TODO this should be properly optional instead of commented out
        // {
        //   id: 'updated',
        //   label: this.$t('change'),
        //   additionalClass: 'optional',
        // },
        showOrgCol
          ? {
              id: 'workingBody',
              label: this.$t('organization'),
              additionalClass: 'organization optional',
            }
          : null,
      ].filter(Boolean);
    },

    currentWorkingBodies() {
      return this.workingBodies
        .filter((workingBody) => workingBody.selected)
        .map((workingBody) => workingBody.id);
    },

    currentPageSessions() {
      return this.sessionsPerPage[this.page - 1] || [];
    },

    mappedSessions() {
      const showOrgCol = false; //TODO

      return this.currentPageSessions.map((session) =>
        [
          {
            link: this.getSessionLink(session),
            image: `${this.$root.$options.contextData.urls.cdn}/icons/${
              sessionClassification(session.classification).icon
            }.svg`,
          },
          {
            link: this.getSessionLink(session),
            text: sessionName(session, this.$t),
          },
          session.start_time ? dateFormatter(session.start_time) : ' ',
          this.showEndDate
            ? session.end_time
              ? dateFormatter(session.end_time)
              : ' '
            : null,
          showOrgCol
            ? {
                contents: session.organizations.map((org) => ({
                  text: org.name,
                  link: null,
                })),
              }
            : null,
        ].filter(Boolean),
      );
    },
  },
  methods: {
    selectSort(sortId) {
      if (this.currentSort === sortId) {
        this.currentSortOrder =
          this.currentSortOrder === 'asc' ? 'desc' : 'asc';
      } else {
        this.currentSort = sortId;
        this.currentSortOrder = 'asc';
      }
      // start a request to get sorted sessions
      this.searchSessionsImmediate();
    },

    searchSessionsImmediate() {
      this.isLoading = true;
      this.sessionsPerPage = Array(this.pages);
      this.count = 0;
      this.page = 1;
      this.makeRequest(this.searchUrl).then((response) => {
        this.count = response?.data?.['sessions:count'];
        this.page = response?.data?.['sessions:page'];
        this.sessionsPerPage[this.page - 1] =
          response?.data?.results?.sessions || [];
        this.isLoading = false;
      });
    },

    searchSessions: debounce(function searchSessions() {
      this.searchSessionsImmediate();
    }, 750),

    onPageChange(newPage) {
      this.page = newPage;
      this.scrollToTop();
      if (!this.sessionsPerPage[newPage - 1]) {
        this.isLoading = true;
        this.makeRequest(this.searchUrl).then((response) => {
          this.sessionsPerPage[newPage - 1] =
            response?.data?.results?.sessions || [];
          this.isLoading = false;
        });
      }
    },

    // TODO extract this
    scrollToTop() {
      const el = this.$refs.card?.$el || this.$refs.card;
      el.scrollIntoView();
    },
  },
};
</script>

<style lang="scss" scoped>
@use 'parlassets/scss/breakpoints';

.filters {
  display: flex;
  padding-bottom: 12px;

  .filter {
    width: 50%;

    @include breakpoints.respond-to(mobile) {
      width: 100%;
    }
  }

  .filter-label {
    display: block;
    height: 20px;
    margin-bottom: 0;
    overflow: hidden;
  }
}

:deep(.session-list) {
  flex-wrap: nowrap; // make sure we don't wrap, works around a bug in firefox that causes rows to be too high

  .item,
  .headers {
    .column {
      &.date {
        margin: 0 16px;
        flex-basis: 80px;
        flex-shrink: 0;
        flex-grow: 0;
        text-align: left;

        @include breakpoints.respond-to(desktop) {
          flex-basis: 140px;
        }
      }

      &.date--start,
      &.date--end,
      &.date:not(:last-child) {
        @include breakpoints.respond-to(desktop) {
          flex-basis: 110px;
        }
      }

      &.organization {
        text-align: left;
      }
    }
  }

  .headers {
    .column {
      &.date--start,
      &.date--end {
        white-space: normal;
      }
    }
  }
}
</style>
