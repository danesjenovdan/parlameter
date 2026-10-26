<template>
  <card-wrapper ref="card" :header-config="headerConfig" max-height>
    <template #generator>
      <div v-if="organizationTabs?.length" class="party-list-generator">
        <div class="row buttons-row">
          <div class="col-md-12">
            <blue-button-list
              v-model="currentOrganizationTab"
              :items="organizationTabs"
              @update:model-value="searchLegislationImmediate"
            />
          </div>
        </div>
      </div>
    </template>
    <div class="legislation-list-container">
      <div class="filters">
        <div class="filter text-filter">
          <div class="filter-label">{{ $t('title-search') }}</div>
          <search-field
            v-model="textFilter"
            @update:model-value="searchLegislation"
          />
        </div>
        <div
          v-if="filterByStatus && filterOptionsStatus.length > 1"
          class="filter buttons-filter"
        >
          <striped-button
            v-for="filterOption in filterOptionsStatus"
            :key="filterOption.id"
            :color="filterOption.color"
            :selected="selectedFilterOptionStatus === filterOption"
            :small-text="filterOption.label"
            @click="selectFilterOptionStatus(filterOption)"
          />
        </div>
        <div
          v-if="
            filterByClassification && filterOptionsClassification.length > 1
          "
          class="filter buttons-filter"
        >
          <striped-button
            v-for="filterOption in filterOptionsClassification"
            :key="filterOption.id"
            :color="filterOption.color"
            :selected="selectedFilterOptionClassification === filterOption"
            :small-text="filterOption.label"
            @click="selectFilterOptionClassification(filterOption)"
          />
        </div>
      </div>
      <div v-if="isLoading" class="nalagalnik"></div>
      <!-- show loader while fetching results -->
      <template v-else>
        <sortable-table
          :columns="columns"
          :items="mappedItems"
          :sort="currentSort"
          :sort-order="currentSortOrder"
          :sort-callback="selectSort"
          class="legislation-list"
        />
        <pagination
          v-if="count > perPage"
          :page="page"
          :count="count"
          :per-page="perPage"
          @change="onPageChange"
        />
      </template>
    </div>
  </card-wrapper>
</template>

<script>
import { debounce } from 'lodash-es';
import common from '@/_mixins/common.js';
import links from '@/_mixins/links.js';
import cancelableRequest from '@/_mixins/cancelableRequest.js';
import { defaultHeaderConfig, sessionHeader } from '@/_mixins/altHeaders.js';
import {
  legislationListContextUrl,
  sessionLegislationContextUrl,
} from '@/_mixins/contextUrls.js';
import BlueButtonList from '@/_components/BlueButtonList.vue';
import SearchField from '@/_components/SearchField.vue';
import StripedButton from '@/_components/StripedButton.vue';
import SortableTable from '@/_components/SortableTable.vue';
import Pagination from '@/_components/Pagination.vue';
import dateFormatter from '@/_helpers/dateFormatter.js';
import { LEGISLATION_PER_PAGE } from '@/_helpers/constants.js';
import legislationStatus from '@/_helpers/legislationStatus.js';

export default {
  name: 'Legislation',
  components: {
    BlueButtonList,
    SearchField,
    StripedButton,
    SortableTable,
    Pagination,
  },
  mixins: [common, links, cancelableRequest],
  props: {
    type: {
      type: String,
      default: 'misc',
    },
  },
  data() {
    const { cardState, cardData } = this.$root.$options.contextData;

    // check if we're embedded
    const isEmbedded = this.$root.$options.contextData.templateName === 'embed';

    const data = cardData?.data || {};
    let results = data.results?.legislation ?? [];
    let pages = data['legislation:pages'] ?? 1;
    const initialPage = data['legislation:page'] ?? 1;
    const count = data['legislation:count'] ?? results.length ?? 0;
    let perPage = data['legislation:per_page'] ?? LEGISLATION_PER_PAGE;
    let page = Number(cardState?.page) || initialPage;

    // if we're embedded we should override our current settings
    if (isEmbedded) {
      pages = Math.ceil(count / 5);
      perPage = 5;
      page = page * 2 - 1;
      results = results.slice(0, 5);
    }

    // create an array with `size = number of pages` and use it to cache results for each page
    const legislationPerPage = Array(pages);
    // store initial page results (-1 because pages start at 1 and index starts at 0)
    legislationPerPage[initialPage - 1] = results;

    // create filterOptions from classifications contained in the API response
    const classifications = cardData?.data?.results?.classifications || [];
    const filterOptionsClassification = classifications
      .slice()
      .sort()
      .reverse()
      .map((classification) => ({
        id: classification,
        color: 'for',
        label: this.$t(`legislation-classifications.${classification}`),
        selected: cardState?.filter === classification,
      }));

    const statuses = cardData?.data?.results?.statuses || [];
    const filterOptionsStatus = statuses.slice().map((status) => ({
      id: status,
      color: status,
      label: this.$t(legislationStatus(status).translationKey),
      selected: cardState?.filter === status,
    }));

    // by default we filter by classification if not filtering by status, but if
    // the cardState has filterByClassification set to true, we override that
    const filterByStatus =
      cardState?.filterByStatus && cardState?.filterByStatus !== 'false';
    let filterByClassification = !filterByStatus;
    if (
      cardState?.filterByClassification &&
      cardState?.filterByClassification !== 'false'
    ) {
      filterByClassification = true;
    }

    const orgs = (cardState?.organizationTabs || '')
      .split('|')
      .filter(Boolean)
      .map((org) => {
        const [id, name] = org.split(';');
        return { id, name };
      });

    let organizationTabs = [];
    if (orgs.length) {
      organizationTabs = orgs.map((org) => ({
        id: org.id,
        label: org.name,
      }));
      organizationTabs.unshift({
        id: 'all',
        label: this.$t('everybody'),
      });
    }

    return {
      legislation: cardData?.data?.results || [],
      filterOptionsStatus,
      filterOptionsClassification,
      filterByStatus,
      filterByClassification,
      currentFilter: cardState?.filter,
      currentSort: 'last_consideration',
      currentSortOrder: 'desc',
      textFilter: cardState?.text || '',
      showEpaColumn:
        cardState?.showEpaColumn && cardState?.showEpaColumn !== 'false',
      organizationTabs,
      currentOrganizationTab: organizationTabs?.[0]?.id || null,

      // pagination
      pages,
      initialPage,
      count,
      perPage,
      isLoading: false,
      page,
      legislationPerPage,
    };
  },
  computed: {
    headerConfig() {
      if (this.type === 'session') {
        return sessionHeader.computed.headerConfig.call(this);
      }
      return defaultHeaderConfig(this, {
        heading: this.cardData?.data?.mandate?.description,
      });
    },
    searchUrl() {
      // cardData.url is automagically provided by the rendering pipeline
      const url = new URL(this.cardData.url);

      // set per-page setting
      url.searchParams.set('legislation:per_page', this.perPage);

      url.searchParams.set('legislation:page', this.page);
      url.searchParams.set('text', this.textFilter);

      if (
        this.currentOrganizationTab &&
        this.currentOrganizationTab !== 'all'
      ) {
        url.searchParams.set('organization', this.currentOrganizationTab);
      }

      if (
        this.selectedFilterOptionClassification &&
        this.filterByClassification
      ) {
        url.searchParams.set(
          'classification',
          this.selectedFilterOptionClassification.id,
        );
      }
      if (this.selectedFilterOptionStatus && this.filterByStatus) {
        url.searchParams.set('status', this.selectedFilterOptionStatus.id);
      }

      // set sort param
      const sortPrefix = this.currentSortOrder === 'desc' ? '-' : '';
      const sort = this.currentSort;
      url.searchParams.set('order_by', `${sortPrefix}${sort}`);

      return url.toString();
    },
    columns() {
      return [
        {
          id: 'text',
          label: this.$te('name--for-legislation')
            ? this.$t('name--for-legislation')
            : this.$t('name'),
          additionalClass: 'name-col',
        },
        // TODO this is commented out because
        // we don't need it when we deal with
        // municipalities, but it should be an
        // optional thing
        // {
        //   id: 'data',
        //   label: this.$t('data'),
        //   additionalClass: 'narrow no-sort',
        // },
        this.showEpaColumn
          ? {
              id: 'epa',
              label: this.$t('epa'),
              additionalClass: 'epa-col',
            }
          : null,
        {
          id: 'last_consideration',
          label: this.$t('legislation-last-consideration'),
          additionalClass: 'date-col',
        },
        {
          id: 'status',
          label: this.$t('status'),
          additionalClass: 'status-col',
        },
      ].filter(Boolean);
    },
    currentPageLegislation() {
      return this.legislationPerPage[this.page - 1] || [];
    },
    mappedItems() {
      return this.currentPageLegislation.map((legislation) => {
        const status = legislationStatus(legislation.status);
        let dateString = dateFormatter(legislation.last_consideration);
        if (!dateString || dateString === 'Invalid Date') {
          dateString = 'N/A';
        }

        const outcomeHtml = `<div class="outcome"><i class="parlaicon ${
          status.iconClass
        }"></i><div class="text">${this.$t(status.translationKey)}</div></div>`;

        return [
          {
            html: `<a href="${this.getLegislationLink(
              legislation,
            )}" class="funblue-light-hover">${legislation.text}</a>`,
          },
          // TODO optional stuff commented out, this is bad
          // { html: dataIconsHtml },
          this.showEpaColumn ? { text: legislation.epa } : null,
          { text: dateString },
          { html: outcomeHtml },
        ].filter(Boolean);
      });
    },
    selectedFilterOptionStatus() {
      return this.filterOptionsStatus.find((fo) => fo.selected);
    },
    selectedFilterOptionClassification() {
      return this.filterOptionsClassification.find((fo) => fo.selected);
    },
  },

  watch: {
    currentSort() {
      this.searchLegislationImmediate();
    },
    currentSortOrder() {
      this.searchLegislationImmediate();
    },
    selectedFilterOptionStatus() {
      this.searchLegislationImmediate();
    },
    selectedFilterOptionClassification() {
      this.searchLegislationImmediate();
    },
  },

  created() {
    (this.type === 'session'
      ? sessionLegislationContextUrl
      : legislationListContextUrl
    ).created.call(this);
  },

  methods: {
    selectFilterOptionStatus(filterOption) {
      if (filterOption.selected) {
        filterOption.selected = false;
      } else {
        this.filterOptionsStatus.forEach((fo) => {
          fo.selected = filterOption === fo;
        });
      }
    },
    selectFilterOptionClassification(filterOption) {
      if (filterOption.selected) {
        filterOption.selected = false;
      } else {
        this.filterOptionsClassification.forEach((fo) => {
          fo.selected = filterOption === fo;
        });
      }
    },
    selectSort(sortId) {
      if (this.currentSort === sortId) {
        this.currentSortOrder =
          this.currentSortOrder === 'asc' ? 'desc' : 'asc';
      } else {
        this.currentSort = sortId;
        this.currentSortOrder = 'asc';
      }
    },
    searchLegislationImmediate() {
      this.isLoading = true;
      this.legislationPerPage = Array(this.pages);
      this.count = 0;
      this.page = 1;
      this.makeRequest(this.searchUrl).then((response) => {
        this.count = response?.data?.['legislation:count'];
        this.page = response?.data?.['legislation:page'];
        this.legislationPerPage[this.page - 1] =
          response?.data?.results?.legislation || [];
        this.isLoading = false;
      });
    },
    searchLegislation: debounce(function searchLegislation() {
      this.searchLegislationImmediate();
    }, 750),
    onPageChange(newPage) {
      this.page = newPage;
      this.scrollToTop();
      if (!this.legislationPerPage[newPage - 1]) {
        this.isLoading = true;
        this.makeRequest(this.searchUrl).then((response) => {
          this.legislationPerPage[newPage - 1] =
            response?.data?.results?.legislation || [];
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

.buttons-row {
  margin-top: 14px;
}

.legislation-list-container {
  .filters {
    display: flex;
    justify-content: space-between;
    padding-bottom: 12px;
    margin-bottom: 12px;

    @include breakpoints.respond-to(mobile) {
      flex-wrap: wrap;
    }

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
      justify-content: flex-end;
      gap: 3px;

      @include breakpoints.respond-to(mobile) {
        justify-content: center;
        margin-top: 10px;
      }

      .striped-button {
        padding-inline: 8px;

        @include breakpoints.respond-to(mobile) {
          flex: 1;
          padding: 0;
        }
      }
    }
  }
}

.legislation-list-container :deep(.legislation-list) {
  .column {
    margin: 0;

    &.epa-col {
      flex: 0 0 80px;
      margin-left: 30px;

      @include breakpoints.respond-to(mobile) {
        display: none;
      }
    }

    &.date-col {
      flex: 0 0 100px;
      margin-left: 30px;

      @include breakpoints.respond-to(mobile) {
        display: none;
      }
    }

    &.status-col {
      flex: 0 0 150px;
      margin-left: 30px;

      .parlaicon {
        flex-shrink: 0;
      }

      @include breakpoints.respond-to(mobile) {
        flex: 0.45;

        .outcome .text {
          display: none;
        }
      }
    }
  }

  .headers .column {
    &.date-col {
      white-space: normal;
    }
  }

  .item .column {
    &.name-col {
      font-family: 'Roboto Slab', sans-serif;
      font-size: 14px;

      a {
        margin-left: -0.3em;
        padding: 0.15em 0.3em;
        -webkit-box-decoration-break: clone;
        box-decoration-break: clone;
      }
    }
  }
}
</style>
