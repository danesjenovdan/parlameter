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
          <div v-t="'title-search'" class="filter-label"></div>
          <search-field
            v-model="textFilter"
            @update:model-value="searchLegislation"
          />
        </div>
        <!-- only show filters if we have more than one classification to show -->
        <div v-if="filterOptions.length > 1" class="filter buttons-filter">
          <striped-button
            v-for="filterOption in filterOptions"
            :key="filterOption.id"
            :color="filterOption.color"
            :selected="selectedFilterOption === filterOption"
            :small-text="filterOption.label"
            @click="selectFilterOption(filterOption)"
          />
        </div>
        <!--
          these filters are commented out because
          they are currently not in use, but they
          should be made properly optional
        -->
        <!-- <div class="checkbox-filters">
          <div class="filter align-checkbox">
            <input
              id="only-abstracts"
              v-model="onlyAbstracts"
              type="checkbox"
              class="checkbox"
            />
            <label v-t="'only-abstracts'" for="only-abstracts"></label>
          </div>
          <div class="filter align-checkbox">
            <input
              id="only-with-votes"
              v-model="onlyWithVotes"
              type="checkbox"
              class="checkbox"
            />
            <label v-t="'only-with-votes'" for="only-with-votes"></label>
          </div>
        </div> -->
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
import legislationStatus, {
  sortLegislationStatuses,
} from '@/_helpers/legislationStatus.js';

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
    const filterOptionsStatus = statuses
      .slice()
      .sort(sortLegislationStatuses)
      .map((status) => ({
        id: status,
        color: status,
        label: this.$t(legislationStatus(status).translationKey),
        selected: cardState?.filter === status,
      }));

    const filterByStatus =
      cardState?.filterByStatus && cardState?.filterByStatus !== 'false';

    const filterOptions = filterByStatus
      ? filterOptionsStatus
      : filterOptionsClassification;

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
      filterOptions,
      filterByStatus,
      currentFilter: cardState?.filter,
      currentSort: 'timestamp',
      currentSortOrder: 'desc',
      textFilter: cardState?.text || '',
      // onlyAbstracts: !!state.onlyAbstracts,
      // onlyWithVotes: !!state.onlyWithVotes,
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

      if (this.selectedFilterOption && !this.filterByStatus) {
        url.searchParams.set('classification', this.selectedFilterOption.id);
      }
      if (this.selectedFilterOption && this.filterByStatus) {
        url.searchParams.set('status', this.selectedFilterOption.id);
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
          id: 'timestamp',
          label: this.$t('date'),
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
        let dateString = dateFormatter(legislation.timestamp);
        if (!dateString || dateString === 'Invalid Date') {
          dateString = 'N/A';
        }

        const outcomeHtml = `<div class="outcome"><i class="parlaicon ${
          status.iconClass
        }"></i><div class="text">${this.$t(status.translationKey)}</div></div>`;

        // TODO there are no abstracts so this is commented out
        // we should have a way to make this optional
        // const dataIconsHtml = `
        //   <div class="data-icons">
        //     <i class="parlaicon icon-abstract ${
        //       legislation.abstractVisible ? 'icon-show' : 'icon-hide'
        //     }"></i>
        //     <i class="parlaicon icon-votes ${
        //       legislation.hasVotes ? 'icon-show' : 'icon-hide'
        //     }"></i>
        //   </div>
        // `;

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
    selectedFilterOption() {
      return this.filterOptions.find((fo) => fo.selected);
    },
  },

  watch: {
    currentSort() {
      this.searchLegislationImmediate();
    },

    currentSortOrder() {
      this.searchLegislationImmediate();
    },

    selectedFilterOption() {
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
    selectFilterOption(filterOption) {
      if (filterOption.selected) {
        filterOption.selected = false;
      } else {
        this.filterOptions.forEach((fo) => {
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

// @function icon-abstract($color) {
//   @return 'data:image/svg+xml;utf8,<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 128 128" fill="%23#{str_slice("#{$color}", 2)}"><path d="M112 8h-6V4a4 4 0 0 0-4-4H16a4 4 0 0 0-4 4v120a4 4 0 0 0 4 4h86a4 4 0 0 0 4-4v-4h6a4 4 0 0 0 4-4V12a4 4 0 0 0-4-4zM16 4h86v4H24a4 4 0 0 0-4 4v9h-4zm0 21h4v6h-4zm0 10h4v6h-4zm0 10h4v6h-4zm0 10h4v6h-4zm0 10h4v6h-4zm0 10h4v6h-4zm0 10h4v6h-4zm0 10h4v6h-4zm0 29v-19h4v11a4 4 0 0 0 4 4h78v4zm8-8v-11h4a2 2 0 0 0 0-4h-4v-6h4a2 2 0 0 0 0-4h-4v-6h4a2 2 0 0 0 0-4h-4v-6h4a2 2 0 0 0 0-4h-4v-6h4a2 2 0 0 0 0-4h-4v-6h4a2 2 0 0 0 0-4h-4v-6h4a2 2 0 0 0 0-4h-4v-6h4a2 2 0 0 0 0-4h-4v-6h4a2 2 0 0 0 0-4h-4v-9h88v104z"/><path d="M106 97H36a2 2 0 0 0 0 4h70a2 2 0 0 0 0-4zm0-70H36a2 2 0 0 0 0 4h70a2 2 0 0 0 0-4zM34 39a2 2 0 0 0 2 2h13.56a29.54 29.54 0 0 1 6.58-4H36a2 2 0 0 0-2 2zm72-2H79.87a29.54 29.54 0 0 1 6.58 4H106a2 2 0 0 0 0-4zM36 51h5.53a29.52 29.52 0 0 1 2.39-4H36a2 2 0 0 0 0 4zm70-4H92.09a29.52 29.52 0 0 1 2.39 4H106a2 2 0 0 0 0-4zm0 10h-9.35a29.3 29.3 0 0 1 .69 4H106a2 2 0 0 0 0-4zm-70 4h2.65a29.3 29.3 0 0 1 .69-4H36a2 2 0 0 0 0 4zm70 6h-8.65a29.3 29.3 0 0 1-.69 4H106a2 2 0 0 0 0-4zm-70 4h3.35a29.3 29.3 0 0 1-.69-4H36a2 2 0 0 0 0 4zm70 6H94.47a29.52 29.52 0 0 1-2.39 4H106a2 2 0 0 0 0-4zm-70 4h7.91a29.52 29.52 0 0 1-2.39-4H36a2 2 0 0 0 0 4zm0 10h20.13a29.54 29.54 0 0 1-6.58-4H36a2 2 0 0 0 0 4zm70-4H86.44a29.54 29.54 0 0 1-6.58 4H106a2 2 0 0 0 0-4zM52.74 67l8.19 8.19a2 2 0 0 0 2.83 0l19.5-19.5a2 2 0 0 0-2.83-2.83L62.34 70.92l-6.77-6.77A2 2 0 0 0 52.74 67z"/><path d="M68 89.5A25.5 25.5 0 1 0 42.5 64 25.53 25.53 0 0 0 68 89.5zm0-47A21.5 21.5 0 1 1 46.5 64 21.52 21.52 0 0 1 68 42.5z"/></svg>';
// }

// @function icon-votes($color) {
//   @return 'data:image/svg+xml;utf8,<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 100 100" fill="%23#{str_slice("#{$color}", 2)}"><path d="M29 11C17.978 11 9 20.006 9 31.023c0 8.928 5.9 16.499 14 19.055v10.933h-2.062c-1.256.053-2.146.745-3.032 1.406-.25-.807-1.061-1.404-1.906-1.406H9.813c-.984.093-1.817 1.012-1.813 2V87c0 1.047.953 2 2 2h6c.774.01 1.53-.48 1.844-1.187.418.246.835.463 1.25.656.548.254.985.53 1.906.53h14.844c.2 0 .402-.032.594-.093 3.128-.944 4.137-4.455 2.937-7.341.923-.84 1.623-1.818 1.75-2.967.108-.984-.086-1.955-.469-2.843 1.14-.773 2.045-1.75 2.313-2.968.26-1.182-.036-2.257-.531-3.28.898-.869 1.562-1.911 1.562-3.123 0-2.005-1.255-3.803-3.125-5.06a2.014 2.014 0 0 0-1.094-.313H35V50.078c8.1-2.556 14-10.127 14-19.055C49 20.006 40.022 11 29 11zm42 0c-11.022 0-20 9.006-20 20.023 0 8.928 5.9 16.499 14 19.055v10.933h-4.969a2.01 2.01 0 0 0-.906.312C57.255 62.582 56 64.38 56 66.383c0 1.213.664 2.256 1.563 3.125-.496 1.022-.792 2.097-.532 3.28.269 1.218 1.173 2.194 2.313 2.967-.383.888-.577 1.86-.469 2.843.127 1.149.827 2.127 1.75 2.967-1.2 2.886-.191 6.397 2.938 7.34.191.062.392.094.593.095H79c.92 0 1.358-.277 1.906-.531.415-.193.832-.41 1.25-.656A2.049 2.049 0 0 0 84 89h6c1.047 0 2-.952 2-2V63.01c0-1.046-.953-1.999-2-1.999h-6.187a2.05 2.05 0 0 0-1.75 1.406c-.902-.754-2.05-1.394-3-1.406H77V50.078c8.1-2.556 14-10.127 14-19.055C91 20.006 82.022 11 71 11zm-42 4.03c8.86 0 16 7.137 16 15.993 0 8.857-7.14 15.963-16 15.963S13 39.88 13 31.023c0-8.856 7.14-15.993 16-15.993zm42 0c8.86 0 16 7.137 16 15.993 0 8.857-7.14 15.963-16 15.963S55 39.88 55 31.023c0-8.856 7.14-15.993 16-15.993zm8.031 7.622L68.344 34.24l-5.531-4.748c-.794-.687-2.141-.59-2.828.203-.687.793-.59 2.14.203 2.827l7 5.997c.776.673 2.085.6 2.78-.156l12-12.995c.894-1.14.564-2.265-.315-3.015-.899-.628-1.79-.394-2.622.298zm-45.781 1.28L29 28.18l-4.25-4.248c-1.015-.771-1.886-.707-2.71-.129-.992.913-.781 2.181-.102 2.972l4.25 4.248-4.25 4.217c-.77.73-.79 2.102-.045 2.855.746.754 2.118.748 2.857-.013L29 33.834l4.25 4.248c.739.76 2.111.767 2.857.013.746-.753.724-2.125-.045-2.855l-4.25-4.217 4.25-4.248c.8-1.067.722-1.998-.049-2.969-1.045-.76-1.711-.524-2.763.126zM12 65.009h2v19.992h-2zm9.188 0H39.03c1.096 1.043 1.022 1.429.313 2h-4.531c-1.048.049-1.956 1.046-1.907 2.093.049 1.047 1.047 1.954 2.094 1.905h3.781c.662 1.288-.565 1.79-1.281 2h-3.687c-1.048.048-1.956 1.045-1.907 2.092.049 1.047 1.047 1.955 2.094 1.906h2.844c.584 1.102.1 1.522-.469 1.999h-3.562c-1.048.049-1.956 1.046-1.907 2.093.049 1.047 1.047 1.954 2.094 1.905h2.781c.435.886.07 1.78-.468 2H21c-.982-.607-2.096-1.275-3-1.937V67.82c1.075-.98 2.128-2.056 3.188-2.812zm39.78 0h17.845c1.223.763 2.306 1.93 3.187 2.812v15.243c-.985.669-1.973 1.336-3 1.937H64.687c-.538-.219-.903-1.113-.468-2H67c1.057.016 2.028-.942 2.028-1.998s-.971-2.014-2.028-2h-3.375c-1.054-.54-.742-1.176-.469-1.999H66c1.057.015 2.028-.942 2.028-1.999 0-1.056-.971-2.014-2.028-1.999h-3.5c-1.42-.404-1.676-.93-1.281-2H65c1.057.016 2.028-.942 2.028-1.998 0-1.057-.971-2.014-2.028-2h-4.344c-1.199-.548-.244-1.503.313-1.999zm25.032 0h2v19.992h-2z"/></svg>';
// }

// label[for='only-abstracts']::after,
// label[for='only-with-votes']::after {
//   content: '';
//   display: inline-block;
//   width: 20px;
//   height: 20px;
//   margin: -5px 0 -5px 5px;
//   background-repeat: no-repeat;
//   background-position: center;
// }

// label[for='only-abstracts']::after {
//   background-image: url('#{icon-abstract(colors.$font-default)}');
//   background-size: 17px;
// }

// label[for='only-with-votes']::after {
//   background-image: url('#{icon-votes(colors.$font-default)}');
//   background-size: 19px;
// }
</style>
