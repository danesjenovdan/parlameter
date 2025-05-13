<template>
  <div class="result-chart">
    <donut-chart
      :class="['donut-chart', `option-${option}`]"
      :section-data="chartData"
    />
    <div class="text-container">
      <div v-if="option !== 'cant_compute'" class="percentage">
        {{ formatNumber(score) }}
      </div>
      <div class="text">{{ translatedOption }}</div>
    </div>
  </div>
</template>

<script>
import DonutChart from '@/_components/DonutChart.vue';
import numberFormatter from '@/_helpers/numberFormatter.js';

export default {
  name: 'GlasovanjeSejeResult',
  components: { DonutChart },
  props: {
    chartData: {
      type: Array,
      default: () => [],
    },
    option: {
      type: String,
      default: '',
    },
    score: {
      type: Number,
      default: 0,
    },
  },
  computed: {
    translatedOption() {
      switch (this.option) {
        case 'for':
          return this.$t('vote-for');
        case 'against':
          return this.$t('vote-against');
        case 'abstain':
          return this.$t('vote-abstain-plural');
        case 'absent':
          return this.$t('vote-absent-plural');
        case 'cant_compute':
          return this.$t('vote-no-majority');
        default:
          return '';
      }
    },
  },
  methods: {
    formatNumber(number) {
      return numberFormatter(number, { percent: true });
    },
  },
};
</script>

<style lang="scss" scoped>
@use 'parlassets/scss/breakpoints';

.result-chart {
  align-items: center;
  justify-content: flex-end;

  @include breakpoints.show-for(desktop, flex);

  @include breakpoints.respond-to(desktop) {
    justify-content: flex-start;
  }

  .donut-chart {
    background-size: 41px 41px;
    background-repeat: no-repeat;
    background-position: center center;
    height: 58px;
    margin: 0 0 0 15px;
    width: 58px;

    $icon-path: '#{get-parlassets-url()}/icons';
    &.option-for {
      background-image: url(#{$icon-path}/za_v2.svg);
    }
    &.option-against {
      background-image: url(#{$icon-path}/proti_v2.svg);
    }
    &.option-absent {
      background-image: url(#{$icon-path}/ni.svg);
      background-size: 33px 33px;
    }
    &.option-abstain {
      background-image: url(#{$icon-path}/vzdrzan_v2.svg);
    }
  }

  .text-container {
    text-align: left;
    margin: 0 15px;
    width: 80px;

    .percentage {
      font-size: 24px;
      line-height: 1.1;
      white-space: nowrap;

      @include breakpoints.respond-to(desktop) {
        font-size: 30px;
      }
    }

    .text {
      font-size: 13px;
      line-height: 34px;
      max-width: 140px;
      text-transform: uppercase;

      @include breakpoints.respond-to(desktop) {
        font-size: 16px;
        line-height: 23px;
      }
    }
  }
}
</style>
