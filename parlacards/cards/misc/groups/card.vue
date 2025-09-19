<template>
  <card-wrapper :header-config="headerConfig" max-height>
    <template #generator>
      <div class="party-list-generator">
        <div class="row buttons-row">
          <div class="col-md-12">
            <blue-button-list v-model="currentAnalysis" :items="analyses" />
          </div>
        </div>
      </div>
    </template>
    <empty-state v-if="!processedPartyData?.length" />
    <ul v-else class="party-list">
      <li
        v-for="(party, index) in processedPartyData"
        :key="index"
        class="labeled-chart"
      >
        <div class="column chart-label">
          <a :href="getPartyLink(party)" class="funblue-light-hover">
            {{ party.acronym || party.name || 'N/A' }}
          </a>
        </div>
        <div class="column chart">
          <div class="progress hugebar">
            <div
              :style="{ width: party.chartWidth }"
              class="progress-bar funblue"
              role="progressbar"
            ></div>
            <div class="progress_number">{{ party.displayValue }}</div>
          </div>
        </div>
      </li>
    </ul>
  </card-wrapper>
</template>

<script>
import { find } from 'lodash-es';
import common from '@/_mixins/common.js';
import links from '@/_mixins/links.js';
import numberFormatter from '@/_helpers/numberFormatter.js';
import { defaultHeaderConfig } from '@/_mixins/altHeaders.js';
import { partyListContextUrl } from '@/_mixins/contextUrls.js';
import { defaultOgImage } from '@/_mixins/ogImages.js';
import BlueButtonList from '@/_components/BlueButtonList.vue';
import EmptyState from '@/_components/EmptyState.vue';

const analysesIDs = [
  {
    id: 'seat_count',
  },
  // {
  //   id: 'presence_sessions',
  //   unit: 'percent',
  // },
  {
    id: 'vote_attendance',
    unit: 'percent',
  },
  {
    id: 'number_of_questions',
  },
  {
    id: 'number_of_amendments',
  },
  {
    id: 'group_unity',
    precision: 2,
    unit: 'percent',
  },
  {
    id: 'vocabulary_size',
    precision: 2,
  },
  // {
  //   id: 'privzdignjeno',
  //   precision: 3,
  // },
  // {
  //   id: 'preprosto',
  //   precision: 3,
  // },
  // {
  //   id: 'problematicno',
  //   precision: 3,
  // },
];

export default {
  name: 'CardMiscGroups',
  components: {
    BlueButtonList,
    EmptyState,
  },
  mixins: [common, links, partyListContextUrl],
  cardInfo: {
    doubleWidth: true,
  },
  data() {
    const { cardState, cardData } = this.$root.$options.contextData;

    // get current analysis or set default
    const cardStateAnalysis = Array.isArray(cardState?.analysis)
      ? cardState.analysis[0]
      : cardState?.analysis;
    const currentAnalysis =
      cardStateAnalysis && analysesIDs.find((a) => a.id === cardStateAnalysis)
        ? cardStateAnalysis
        : 'seat_count';

    // parse hidden analyses into an array
    const hiddenAnalyses = cardState?.hiddenAnalyses?.split('|') || [];

    // filter out hidden analyses and translate them
    const analyses = analysesIDs
      .filter((a) => !hiddenAnalyses.includes(a.id))
      .map((a) => ({
        ...a,
        label: this.$te(`analysis-texts--party.${a.id}.label`)
          ? this.$t(`analysis-texts--party.${a.id}.label`)
          : '',
        titleSuffix: this.$te(`analysis-texts--party.${a.id}.titleSuffix`)
          ? this.$t(`analysis-texts--party.${a.id}.titleSuffix`)
          : '',
        explanation: this.$te(`analysis-texts--party.${a.id}.explanation`)
          ? this.$t(`analysis-texts--party.${a.id}.explanation`)
          : '',
      }));

    return {
      results: cardData?.data?.results || [],
      currentAnalysis,
      analyses,
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
    headerConfig() {
      return defaultHeaderConfig(this, {
        heading: this.cardData?.data?.mandate?.description,
        title: `${this.$t('card.title')} ${
          this.currentAnalysisData?.titleSuffix
        }`,
      });
    },
    currentAnalysisData() {
      return find(this.analyses, { id: this.currentAnalysis });
    },
    processedPartyData() {
      const maxValue = this.results.reduce(
        (oldValue, nextParty) =>
          Math.max(oldValue, nextParty.results?.[this.currentAnalysis]),
        0,
      );

      const mappedData = this.results.map((party) => {
        const rawValue = party.results?.[this.currentAnalysis] || 0;
        const newParty = JSON.parse(JSON.stringify(party));

        newParty.displayValue = numberFormatter(rawValue, {
          precision: this.currentAnalysisData?.precision || 0,
          percent: this.currentAnalysisData?.unit === 'percent',
        });

        if (maxValue > 0) {
          newParty.chartWidth = `${(rawValue / maxValue) * 85}%`;
        } else {
          newParty.chartWidth = `0%`;
        }

        return newParty;
      });

      return mappedData.sort((memberA, memberB) => {
        const a = memberA.results?.seat_count || 0;
        const b = memberB.results?.seat_count || 0;
        return b - a;
      });
    },
  },
  created() {
    defaultOgImage(this);
  },
};
</script>

<style lang="scss" scoped>
@use 'parlassets/scss/breakpoints';

:deep(.card-content) {
  min-height: 265px;
}

.buttons-row {
  margin-top: 14px;
}

.party-list .labeled-chart {
  // min-height: 46px;

  @include breakpoints.respond-to(mobile) {
    flex-direction: column;
  }

  .column.chart-label {
    line-height: 1.1;
    // margin-top: -10px;
    // margin-bottom: -10px;
    margin-top: 0;
    margin-bottom: 0;
    width: 100px;

    @include breakpoints.respond-to(mobile) {
      width: 100%;
    }
  }

  .column.chart {
    @include breakpoints.respond-to(mobile) {
      width: 100%;
      margin-left: 0;
    }
  }
}
</style>
