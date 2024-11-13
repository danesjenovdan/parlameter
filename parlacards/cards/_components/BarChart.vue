<template>
  <div class="word-list">
    <div :class="['column-label', { flexible: flexibleLabels }]">
      <div v-for="(row, index) in rows" :key="index" class="column chart-label">
        <div class="label-container">
          <template v-if="row.link">
            <img v-if="row.portrait" :src="row.portrait" class="portrait" />
            <a :href="row.link" class="funblue-light-hover">
              {{ row.name }}
            </a>
          </template>
          <template v-else>
            <img v-if="row.portrait" :src="row.portrait" class="portrait" />
            {{ row.name }}
          </template>
        </div>
      </div>
    </div>
    <div class="column-bar">
      <div v-for="(row, index) in rows" :key="index" class="column chart">
        <div class="progress hugebar">
          <div
            :style="{ width: `${row.barWidth}%` }"
            class="progress-bar funblue"
          ></div>
          <div v-if="showNumbers && showPercentage" class="progress_number">
            {{ `${row.formattedValue} | ${row.percentage}` }}
          </div>
          <div v-else-if="showNumbers" class="progress_number">
            {{ row.formattedValue }}
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script>
import numberFormatter from '@/_helpers/numberFormatter.js';

export default {
  name: 'BarChart',
  props: {
    data: {
      type: Array,
      default: () => [],
    },
    showNumbers: {
      type: Boolean,
      default: false,
    },
    showPercentage: {
      type: Boolean,
      default: true,
    },
    max: {
      type: Number,
      default: null,
    },
    total: {
      type: Number,
      default: null,
    },
    flexibleLabels: {
      type: Boolean,
      default: false,
    },
  },
  computed: {
    rows() {
      const maxValue =
        this.max != null
          ? this.max
          : this.data.reduce((acc, row) => Math.max(acc, row.value || 0), 0);

      const totalValue =
        this.total != null
          ? this.total
          : this.data.reduce((acc, row) => acc + row.value, 0);

      return this.data
        .map((row) => ({
          link: row.link,
          name: row.label,
          value: row.value || 0,
          formattedValue: numberFormatter(row.value || 0),
          portrait: row.portrait,
          barWidth: (row.value / maxValue) * (this.showNumbers ? 70 : 100),
          percentage: numberFormatter((row.value / totalValue) * 100, {
            precision: 2,
            percent: true,
          }),
        }))
        .sort((a, b) => b.value - a.value);
    },
  },
};
</script>

<style lang="scss" scoped>
@use 'parlassets/scss/breakpoints';

.word-list {
  max-height: 480px;
  overflow: hidden;
  display: flex;

  .column-label {
    margin-right: 15px;

    &:not(.flexible) {
      flex: 1;
    }
  }

  .column-bar {
    flex: 4;
  }

  .column {
    height: 27px;
    margin-top: 10px;
    margin-bottom: 21px;
  }

  .chart-label {
    display: flex;
    align-items: center;

    .label-container {
      margin-top: -5px;
      margin-bottom: -5px;
      font-size: 16px;
      font-weight: 300;

      @include breakpoints.respond-to(mobile) {
        font-size: 14px;
      }

      .portrait {
        border-radius: 50%;
        height: 40px;
        margin-right: 10px;
        width: 40px;

        @include breakpoints.show-for('above-limbo', inline);
      }
    }
  }
}

.progress_number {
  line-height: 27px;

  @include breakpoints.respond-to(mobile) {
    display: none;
  }
}

.progress.hugebar {
  height: 27px;
}
</style>
