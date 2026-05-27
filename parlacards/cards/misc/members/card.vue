<template>
  <card-wrapper ref="card" :header-config="headerConfig" max-height>
    <template #generator>
      <div class="party-list-generator">
        <div class="row buttons-row">
          <div class="col-md-12">
            <blue-button-list v-model="currentAnalysis" :items="analyses" />
          </div>
        </div>
        <div class="row">
          <div class="col-md-12 filters">
            <div class="filter text-filter">
              <search-field
                v-model="textFilter"
                @update:model-value="searchPeople"
              />
            </div>
            <div class="filter parties">
              <p-search-dropdown
                v-model="groups"
                :placeholder="partiesPlaceholder"
                @update:model-value="searchPeopleImmediate"
              />
            </div>
            <div v-if="showWorkingBodiesFilter" class="filter working-bodies">
              <p-search-dropdown
                v-model="workingBodies"
                :placeholder="workingBodyPlaceholder"
                @update:model-value="searchPeopleImmediate"
              />
            </div>
            <div v-if="showDistrictsFilter" class="filter districts">
              <p-search-dropdown
                v-model="districts"
                :placeholder="districtsPlaceholder"
                @update:model-value="searchPeopleImmediate"
              />
            </div>
            <div v-if="showGendersFilter" class="genders filter">
              <striped-button
                v-for="gender in genders"
                :key="gender.id"
                :selected="selectedGenderId === gender.id"
                :class="['gender', gender.icon]"
                color="for"
                @click="selectGender(gender.id)"
              />
            </div>
          </div>
        </div>
      </div>
    </template>
    <div v-if="isLoading" class="nalagalnik"></div>
    <template v-else>
      <sortable-table
        :columns="columns"
        :items="currentPageProcessedMembers"
        :sort="currentSort"
        :sort-order="currentSortOrder"
        :sort-callback="sortBy"
        class="person-list"
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
import { debounce } from 'lodash-es';
import { MEMBERS_PER_PAGE } from '@/_helpers/constants.js';
import numberFormatter from '@/_helpers/numberFormatter.js';
import age from '@/_helpers/age.js';
import common from '@/_mixins/common.js';
import cancelableRequest from '@/_mixins/cancelableRequest.js';
import links from '@/_mixins/links.js';
import { memberListContextUrl } from '@/_mixins/contextUrls.js';
import { defaultHeaderConfig } from '@/_mixins/altHeaders.js';
import { defaultOgImage } from '@/_mixins/ogImages.js';
import BlueButtonList from '@/_components/BlueButtonList.vue';
import PSearchDropdown from '@/_components/SearchDropdown.vue';
import SearchField from '@/_components/SearchField.vue';
import StripedButton from '@/_components/StripedButton.vue';
import SortableTable from '@/_components/SortableTable.vue';
import Pagination from '@/_components/Pagination.vue';

const analysesIDs = [
  {
    id: 'demographics',
  },
  {
    id: 'presence_votes',
    unit: 'percent',
  },
  // {
  //   id: 'number_of_questions',
  // },
  {
    id: 'speeches_per_session',
  },
  {
    id: 'spoken_words',
  },
  {
    id: 'agreement_with_group',
    unit: 'percent',
  },
  {
    id: 'working_bodies',
  },
];

export default {
  name: 'CardMiscMembers',
  components: {
    BlueButtonList,
    PSearchDropdown,
    SearchField,
    StripedButton,
    SortableTable,
    Pagination,
  },
  mixins: [common, links, memberListContextUrl, cancelableRequest],
  cardInfo: {
    doubleWidth: true,
  },
  data() {
    const { cardState, cardData } = this.$root.$options.contextData;

    // check if we're embedded
    const isEmbedded = this.$root.$options.contextData.templateName === 'embed';

    const data = cardData?.data || {};
    let members = data.results?.members ?? [];
    let pages = data['members:pages'] ?? 1;
    const initialPage = data['members:page'] ?? 1;
    const count = data['members:count'] ?? members.length ?? 0;
    let perPage = data['members:per_page'] ?? MEMBERS_PER_PAGE;
    let page = Number(cardState?.page) || initialPage;

    // if we're embedded we should override our current settings
    if (isEmbedded) {
      pages = Math.ceil(count / 5);
      perPage = 5;
      page = page * 2 - 1;
      members = members.slice(0, 5);
    }

    const membersPerPage = Array(pages);
    membersPerPage[initialPage - 1] = members;

    const initialGenders = (cardState?.genders || '').split(',');
    const genders = [
      { id: 'he', icon: 'gender-m', selected: initialGenders.includes('he') },
      { id: 'she', icon: 'gender-f', selected: initialGenders.includes('she') },
    ];

    // get current analysis or set default
    const cardStateAnalysis = Array.isArray(cardState?.analysis)
      ? cardState.analysis[0]
      : cardState?.analysis;
    const currentAnalysis =
      cardStateAnalysis && analysesIDs.find((a) => a.id === cardStateAnalysis)
        ? cardStateAnalysis
        : 'demographics';

    // parse hidden analyses into an array
    const hiddenAnalysesParam = Array.isArray(cardState?.hiddenAnalyses)
      ? cardState.hiddenAnalyses.map((a) => String(a)).join('|')
      : String(cardState?.hiddenAnalyses);
    const hiddenAnalyses = hiddenAnalysesParam?.split('|') || [];

    // filter out hidden analyses and translate them
    const analyses = analysesIDs
      .filter((a) => !hiddenAnalyses.includes(a.id))
      .map((a) => ({
        ...a,
        label: this.$te(`analysis-texts.${a.id}.label`)
          ? this.$t(`analysis-texts.${a.id}.label`)
          : '',
        titleSuffix: this.$te(`analysis-texts.${a.id}.titleSuffix`)
          ? this.$t(`analysis-texts.${a.id}.titleSuffix`)
          : '',
        explanation: this.$te(`analysis-texts.${a.id}.explanation`)
          ? this.$t(`analysis-texts.${a.id}.explanation`)
          : '',
      }));

    const initialGroups = (cardState?.groups || '').split(',');
    const groups = (cardData?.data?.results?.groups || []).map((g) => {
      return {
        id: (g.slug || '').split('-')[0],
        slug: g.slug,
        label: g.name,
        selected: initialGroups.includes(g.slug),
        color: g.color,
      };
    });

    const initialWorkingBodies = (cardState?.working_bodies || '').split(',');
    const workingBodies = (cardData?.data?.results?.working_bodies || []).map(
      (g) => {
        return {
          id: (g.slug || '').split('-')[0],
          slug: g.slug,
          label: g.name,
          selected: initialWorkingBodies.includes(g.slug),
          color: g.color,
        };
      },
    );

    const initialDistricts = (cardState?.districts || '').split(',');
    const districts = (cardData?.data?.results?.districts || []).map((g) => {
      return {
        id: (g.slug || '').split('-')[0],
        slug: g.slug,
        label: g.name,
        selected: initialDistricts.includes(g.slug),
      };
    });

    const initialTextFilter = cardState?.text || '';

    return {
      analyses,
      analysesMaxValues: cardData?.data?.results?.maximum_scores || {},
      currentAnalysis,
      textFilter: initialTextFilter,
      groups,
      workingBodies,
      districts,
      genders,
      currentSort: cardState?.sort || 'name',
      currentSortOrder: cardState?.sortOrder || 'asc',
      showWorkingBodiesFilter: cardState?.showWorkingBodiesFilter !== 'false',
      showDistrictsFilter:
        cardState?.showDistrictsFilter &&
        cardState?.showDistrictsFilter !== 'false',
      showGendersFilter: cardState?.showGendersFilter !== 'false',
      showDemographicsAge: cardState?.showDemographicsAge !== 'false',
      showDemographicsEducation:
        cardState?.showDemographicsEducation !== 'false',
      showDemographicsMandates: cardState?.showDemographicsMandates !== 'false',
      showDemographicsGroup: cardState?.showDemographicsGroup !== 'false',
      // pagination
      membersPerPage,
      count,
      perPage,
      page,
      pages,
      initialPage,
      isLoading: false,
      isEmbedded,
    };
  },
  computed: {
    cardUrl() {
      const url = common.computed.cardUrl.call(this);
      const [path, search] = url.split('?');
      const searchParams = new URLSearchParams(search);
      searchParams.set('analysis', this.currentAnalysis);
      return `${path}?${searchParams.toString()}`;
    },
    partiesPlaceholder() {
      return this.selectedGroupIds.length > 0
        ? this.$t('selected-placeholder', { num: this.selectedGroupIds.length })
        : this.$t('select-parties-placeholder');
    },
    workingBodyPlaceholder() {
      return this.selectedWorkingBodyIds.length > 0
        ? this.$t('selected-placeholder', {
            num: this.selectedWorkingBodyIds.length,
          })
        : this.$t('select-working-body-placeholder');
    },
    districtsPlaceholder() {
      return this.selectedDistrictIds.length > 0
        ? this.$t('selected-placeholder', {
            num: this.selectedDistrictIds.length,
          })
        : this.$t('select-district-placeholder');
    },
    columns() {
      if (this.currentAnalysis === 'demographics') {
        const filters = [
          { id: 'image', label: 'image', additionalClass: 'portrait' },
          { id: 'name', label: this.$t('name'), additionalClass: 'wider name' },
        ];
        if (this.showDemographicsAge)
          filters.push({ id: 'birth_date', label: this.$t('age') });
        if (this.showDemographicsEducation)
          filters.push({
            id: 'education',
            label: this.$t('education'),
            additionalClass: 'optional',
          });
        if (this.showDemographicsMandates)
          filters.push({
            id: 'mandates',
            label: this.$t('number-of-terms'),
            additionalClass: 'optional',
          });
        if (this.showDemographicsGroup)
          filters.push({
            id: 'group',
            label: this.$t('party'),
            additionalClass: 'optional',
          });
        if (this.showDistrictsFilter) {
          filters.push({
            id: 'district',
            label: this.$t('district'),
            additionalClass: 'optional no-sort',
          });
        }
        return filters;
      }
      if (this.currentAnalysis === 'working_bodies') {
        return [
          { id: 'image', label: 'image', additionalClass: 'portrait' },
          { id: 'name', label: this.$t('name'), additionalClass: 'name' },
          {
            id: 'working-bodies',
            label: this.$t('working-bodies'),
            additionalClass: 'wider working-bodies-col no-sort',
          },
        ];
      }
      return [
        { id: 'image', label: 'image', additionalClass: 'portrait' },
        { id: 'name', label: this.$t('name'), additionalClass: 'name' },
        {
          id: 'analysis',
          label: this.$t('analysis'),
          additionalClass: 'wider barchartcontainer',
        },
      ];
    },
    currentPageMembers() {
      return this.membersPerPage[this.page - 1] || [];
    },
    currentPageProcessedMembers() {
      if (this.currentAnalysis === 'demographics') {
        return this.currentPageMembers.map((member) => {
          const items = [
            {
              link: this.getPersonLink(member),
              image: this.getPersonPortrait(member),
              imageStyle: { border: this.getPersonBorder(member) },
            },
            {
              link: this.getPersonLink(member),
              text: this.getPersonName(member),
            },
          ];

          if (this.showDemographicsAge) {
            items.push(age(member.results?.birth_date));
          }
          if (this.showDemographicsEducation) {
            items.push(member.results?.education);
          }
          if (this.showDemographicsMandates) {
            items.push(member.results?.mandates);
          }
          if (this.showDemographicsGroup) {
            if (this.getPartyLink(member?.group)) {
              items.push({
                link: this.getPartyLink(member?.group),
                text: member.group?.acronym || member.group?.name || 'N/A',
              });
            } else {
              let suffix = '--f';
              if (member?.preferred_pronoun === 'he') suffix = '--m';
              items.push({
                link: null,
                text: this.$t(`unaffiliated${suffix}`),
              });
            }
          }
          if (this.showDistrictsFilter) {
            items.push(
              (member.results?.districts || []).map((d) => d.name).join(', '),
            );
          }
          return items;
        });
      }
      if (this.currentAnalysis === 'working_bodies') {
        return this.currentPageMembers.map((member) => [
          {
            link: this.getPersonLink(member),
            image: this.getPersonPortrait(member),
            imageStyle: { border: this.getPersonBorder(member) },
          },
          {
            link: this.getPersonLink(member),
            text: this.getPersonName(member),
          },
          {
            text: (member.results?.working_bodies || [])
              .map((wb) => wb.name)
              .join(', '),
          },
        ]);
      }
      return this.currentPageMembers.map((member) => {
        const score = member.results?.[this.currentAnalysis] || 0;
        const formattedScore = numberFormatter(score, {
          precision: this.currentAnalysisData?.precision || 0,
          percent: this.currentAnalysisData?.unit === 'percent',
        });
        const maxScore = this.analysesMaxValues[this.currentAnalysis] || 0;
        const scorePercentage = maxScore > 0 ? (score / maxScore) * 100 : 0;
        return [
          {
            link: this.getPersonLink(member),
            image: this.getPersonPortrait(member),
            imageStyle: { border: this.getPersonBorder(member) },
          },
          {
            link: this.getPersonLink(member),
            text: this.getPersonName(member),
          },
          {
            barchart: true,
            value: formattedScore,
            width: scorePercentage,
          },
        ];
      });
    },
    currentAnalysisData() {
      return this.analyses.find((a) => a.id === this.currentAnalysis);
    },
    headerConfig() {
      return defaultHeaderConfig(this, {
        heading: this.cardData?.data?.mandate?.description,
        titleSuffix: this.currentAnalysisData?.titleSuffix,
      });
    },
    selectedGroupIds() {
      return this.groups.filter((g) => g.selected).map((g) => g.id);
    },
    selectedWorkingBodyIds() {
      return this.workingBodies.filter((wb) => wb.selected).map((wb) => wb.id);
    },
    selectedDistrictIds() {
      return this.districts.filter((d) => d.selected).map((d) => d.id);
    },
    selectedGenderId() {
      return this.genders.find((gender) => gender.selected)?.id;
    },
    searchUrl() {
      const url = new URL(this.cardData.url);

      // set per-page setting
      url.searchParams.set('members:per_page', this.perPage);

      url.searchParams.set('members:page', this.page);
      url.searchParams.set('text', this.textFilter);
      if (this.selectedGenderId) {
        url.searchParams.set('preferred_pronoun', this.selectedGenderId);
      } else {
        url.searchParams.delete('preferred_pronoun');
      }
      if (this.selectedGroupIds.length) {
        url.searchParams.set('groups', this.selectedGroupIds.join(','));
      } else {
        url.searchParams.delete('groups');
      }
      if (this.selectedWorkingBodyIds.length) {
        url.searchParams.set(
          'working_bodies',
          this.selectedWorkingBodyIds.join(','),
        );
      } else {
        url.searchParams.delete('working_bodies');
      }
      if (this.selectedDistrictIds.length) {
        url.searchParams.set('districts', this.selectedDistrictIds.join(','));
      } else {
        url.searchParams.delete('districts');
      }
      url.searchParams.set('current_analysis', this.currentAnalysis);
      const sortPrefix = this.currentSortOrder === 'desc' ? '-' : '';
      const sort =
        this.currentSort === 'analysis'
          ? this.currentAnalysis
          : this.currentSort;
      url.searchParams.set('order_by', `${sortPrefix}${sort}`);
      return url.toString();
    },
  },
  watch: {
    currentAnalysis(newValue) {
      this.onCurrentAnalysisChange(newValue);
      this.searchPeopleImmediate();
    },
    currentSort() {
      this.searchPeopleImmediate();
    },
    currentSortOrder() {
      this.searchPeopleImmediate();
    },
  },
  created() {
    defaultOgImage(this);
  },
  mounted() {
    // fix sort if different analysis was loaded from state
    this.onCurrentAnalysisChange(this.currentAnalysis);
  },
  methods: {
    onCurrentAnalysisChange(newValue) {
      if (newValue === 'demographics' || newValue === 'working_bodies') {
        this.currentSort = 'name';
        this.currentSortOrder = 'asc';
      } else {
        this.currentSort = 'analysis';
        this.currentSortOrder = 'desc';
      }
    },
    selectGender(id) {
      if (this.selectedGenderId === id) {
        this.genders.forEach((g) => {
          g.selected = false;
        });
      } else {
        this.genders.forEach((g) => {
          g.selected = g.id === id;
        });
      }
      this.searchPeopleImmediate();
    },
    sortBy(sort) {
      if (this.currentSort === sort) {
        this.currentSortOrder =
          this.currentSortOrder === 'desc' ? 'asc' : 'desc';
      } else {
        this.currentSortOrder = 'asc';
        this.currentSort = sort;
      }
    },
    onPageChange(newPage) {
      this.page = newPage;
      this.scrollToTop();
      if (!this.membersPerPage[newPage - 1]) {
        this.isLoading = true;
        this.makeRequest(this.searchUrl).then((response) => {
          this.membersPerPage[newPage - 1] =
            response?.data?.results?.members || [];
          this.isLoading = false;
        });
      }
    },
    searchPeopleImmediate() {
      this.isLoading = true;
      this.membersPerPage = Array(this.pages);
      this.count = 0;
      this.page = 1;
      this.makeRequest(this.searchUrl).then((response) => {
        this.count = response?.data?.['members:count'];
        this.page = response?.data?.['members:page'];
        this.membersPerPage[this.page - 1] =
          response?.data?.results?.members || [];
        this.analysesMaxValues = response?.data?.results?.maximum_scores || {};
        this.isLoading = false;
      });
    },
    searchPeople: debounce(function searchPeople() {
      this.searchPeopleImmediate();
    }, 750),
    // TODO: extract scrollToTop
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

.blue-button-list-item {
  font-size: 12px;
}

.filters {
  display: flex;
  align-items: flex-end;
  margin-top: 14px;

  .filter:not(:last-child) {
    margin-right: 10px;
  }

  .filter {
    flex: 1;
    display: block;
    margin-left: 0;
    max-width: 214px;
  }

  .search-field {
    flex: 1.2;
  }

  .filter.genders {
    display: flex;
    flex: 0 1 auto;
    margin-left: auto;

    .gender {
      width: 35px;
      background-repeat: no-repeat;
      background-position: center 14px;
      background-size: 50%;

      &:not(:last-child) {
        margin-right: 3px;
      }

      &.gender-m {
        background-image: url('data:image/svg+xml;utf8,<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 100 100"><path d="M63.472,6.5v10l12.957,0L63.584,29.345c-6.145-4.641-13.592-7.157-21.429-7.157c-9.524,0-18.479,3.709-25.214,10.444  C3.042,46.534,3.042,69.154,16.942,83.057C23.678,89.791,32.632,93.5,42.155,93.5c9.524,0,18.479-3.709,25.214-10.444  c12.7-12.702,13.789-32.677,3.281-46.636L83.5,23.571l-0.001,12.956h10L93.5,6.5L63.472,6.5z M60.298,75.985  C55.451,80.831,49.009,83.5,42.155,83.5c-6.853,0-13.296-2.669-18.142-7.514c-10.002-10.003-10.002-26.28-0.001-36.283  c4.847-4.846,11.289-7.515,18.143-7.515s13.296,2.668,18.142,7.515C70.3,49.706,70.3,65.982,60.298,75.985z"/></svg>');
      }

      &.gender-f {
        background-image: url('data:image/svg+xml;utf8,<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 100 100"><path d="M82.301,35.467C82.3,17.656,67.81,3.166,50.001,3.166c-17.812,0-32.302,14.49-32.302,32.301  c0,16.11,11.856,29.502,27.301,31.912v8.171h-9.189v10H45v8.284h10V85.55h9.189v-10H55v-8.171  C70.444,64.969,82.301,51.577,82.301,35.467z M27.699,35.467c0-12.297,10.005-22.301,22.302-22.301  c12.295,0,22.299,10.004,22.3,22.301c0,12.297-10.004,22.301-22.301,22.301S27.699,47.764,27.699,35.467z"/></svg>');
      }
    }
  }

  @include breakpoints.respond-to(mobile) {
    flex-wrap: wrap;

    .search-field {
      flex-basis: auto;
      order: 1;
    }

    .filter.working-bodies,
    .filter.districts {
      display: none;
    }
  }
}

.person-list {
  margin-bottom: 14px;
}

.person-list :deep(.column) {
  &.name,
  &.working-bodies-col,
  &.barchartcontainer {
    text-align: left;
  }

  &.barchartcontainer {
    @include breakpoints.respond-to(mobile) {
      max-width: 45%;

      .value {
        display: block;
        font-size: 14px;
      }
    }
  }

  &.portrait img {
    object-fit: cover;
  }
}

.person-list :deep(.headers) {
  margin-left: 0;

  .column.portrait {
    flex: none;
    width: 80px + 18px - 16px; // image width + image margin-right - header horizontal margin;
    visibility: hidden;

    @include breakpoints.respond-to(mobile) {
      width: 41px + 4px - 16px; // image width + image margin-right - header horizontal margin;
    }
  }
}

.person-list :deep(.headers) {
  height: 40px;

  .column {
    white-space: normal;
  }
}
</style>
