<template>
  <card-wrapper ref="card" :header-config="headerConfig" max-height>
    <template #generator>
      <div class="session-list-generator">
        <!-- only show filters if we have more than one classification to show -->
        <div v-if="filters.length > 1" class="row filters-row">
          <div class="col-md-7">
            <blue-button-list
              v-model="currentFilter"
              :items="filters"
              @update:model-value="selectTab"
            />
          </div>
          <!-- only show working bodies dropdown if we have more than one organization -->
          <div v-if="workingBodies?.length > 1" class="col-md-5 filters">
            <p-search-dropdown
              v-model="workingBodies"
              :placeholder="inputPlaceholder"
              class="dropdown-filter"
              @update:model-value="searchSessionsImmediate"
            />
          </div>
        </div>
      </div>
    </template>
    <div v-if="isLoading" class="nalagalnik"></div>
    <!-- show loader while fetching results -->
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

    // group organizations by classifications
    const classifications = (cardData?.data?.results?.organizations || [])
      .filter((organization) => {
        // this is to filter out organizations without a classification
        return organization.classification != null;
      })
      .sort((a, b) => {
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
      })
      .reduce((returnValue, organization) => {
        if (organization.session_count > 0) {
          const { classification, slug } = organization;
          returnValue[classification] = returnValue[classification] ?? {};
          returnValue[classification][slug] = organization;
        }
        return returnValue;
      }, {});

    // create tabs
    const tabs = Object.keys(classifications).map((classificationKey) => {
      return {
        id: classificationKey,
        title: this.$t(`organization-classifications.${classificationKey}`),
        orgSlugs: Object.keys(classifications[classificationKey]),
        organizations: classifications[classificationKey],
      };
    });

    const showOrganizationColumn = (() => {
      let value = String(cardState?.showOrganizationColumn);
      if (value === 'true') value = 'always';
      if (value === 'false') value = 'never';
      if (['always', 'never', 'secondary-only'].includes(value)) return value;
      return 'secondary-only';
    })();

    const showEndDate = (() => {
      const value = String(cardState?.showEndDate);
      if (value === 'true') return true;
      if (value === 'false') return false;
      return false;
    })();

    return {
      tabs,
      // sessions: cardData?.data?.results,
      workingBodies: [],
      filters: tabs.map((tab) => ({ label: tab.title, id: tab.id })),
      currentSort: 'start_time',
      currentSortOrder: 'desc',
      currentFilter: cardState?.filters || tabs?.[0]?.id,
      headerConfig: defaultHeaderConfig(this, {
        heading: cardData?.data?.mandate?.description,
        title: this.$t('card.title'),
      }),
      showOrganizationColumn,
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

      url.searchParams.set('classification', this.currentFilter);

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

      return url.toString();
    },
    isFirstTabActive() {
      return this.currentFilter === this.tabs?.[0]?.id;
    },
    columns() {
      const showOrgCol =
        this.showOrganizationColumn === 'always' ||
        (this.showOrganizationColumn === 'secondary-only' &&
          !this.isFirstTabActive);

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

    inputPlaceholder() {
      return this.currentWorkingBodies.length > 0
        ? this.$t('selected-placeholder', {
            num: this.currentWorkingBodies.length,
          })
        : this.$t('select-working-body-placeholder');
    },

    currentPageSessions() {
      return this.sessionsPerPage[this.page - 1] || [];
    },

    mappedSessions() {
      const showOrgCol =
        this.showOrganizationColumn === 'always' ||
        (this.showOrganizationColumn === 'secondary-only' &&
          !this.isFirstTabActive);

      return this.currentPageSessions.map((session) =>
        [
          {
            link: this.getSessionLink(session),
            image: `${this.$root.$options.contextData.urls.cdn}/icons/${
              sessionClassification(session.classification).icon
            }.svg`,
          },
          { link: this.getSessionLink(session), text: session.name },
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

    selectTab() {
      // update dropdown of working bodies when tab changes; this is done first
      // to reset the selected working bodies before requesting new sessions,
      // so it doesn't filter out all sessions
      this.updateWorkingBodies();

      // reset sorting
      this.currentSort = 'start_time';
      this.currentSortOrder = 'desc';

      // start a request to get new sessions for this tab
      this.searchSessionsImmediate();
    },

    updateWorkingBodies() {
      // get current tab
      const currentTab = this.tabs.find((tab) => tab.id === this.currentFilter);

      // map all organization slugs in the tab to
      // proper objects that PSearchDropdown can consume
      this.workingBodies = currentTab.orgSlugs.map((slug) => {
        return {
          id: slug,
          selected: false,
          label: currentTab.organizations[slug].name,
        };
      });
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

.filters-row {
  display: flex;
  margin-top: 14px;

  .filters {
    .dropdown-filter {
      margin: 0;
      flex: 1.5;
    }
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
