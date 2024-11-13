<template>
  <empty-state v-if="!attendance?.length" small />
  <div v-else class="party-grid">
    <template v-for="(party, index) in sortedAttendance" :key="index">
      <div class="grid-item chart-label">
        <div class="party-name">
          <a :href="getPartyLink(party.group)" class="funblue-light-hover">
            {{ party.group?.acronym || party.group?.name || 'N/A' }}
          </a>
        </div>
      </div>
      <div class="grid-item chart-percent">
        <div class="number-percent">
          {{ formatNumber(party.value, { percent: true }) }}
        </div>
      </div>
      <div class="grid-item chart">
        <div class="progress hugebar">
          <div
            :style="{ width: `${Math.round(party.value)}%` }"
            class="progress-bar funblue"
            role="progressbar"
          ></div>
        </div>
      </div>
    </template>
  </div>
</template>

<script>
import links from '@/_mixins/links.js';
import numberFormatter from '@/_helpers/numberFormatter.js';
import EmptyState from '@/_components/EmptyState.vue';

export default {
  name: 'AttendanceByGroups',
  components: {
    EmptyState,
  },
  mixins: [links],
  props: {
    attendance: {
      type: Array,
      default: () => [],
    },
  },
  computed: {
    sortedAttendance() {
      return (this.attendance || []).slice().sort((a, b) => {
        const aValue = a.group.acronym || a.group.name || '';
        const bValue = b.group.acronym || b.group.name || '';
        return aValue.localeCompare(bValue, 'sl');
      });
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

.party-grid {
  display: grid;
  grid-template-columns: auto 60px minmax(50%, 85%);
  gap: 10px;
  align-items: center;

  @include breakpoints.respond-to(mobile) {
    grid-template-columns: 1fr;
    gap: 0;
  }

  .grid-item {
    font-family: Roboto, sans-serif;
    font-size: 18px;
    line-height: 1.1;

    @include breakpoints.respond-to(mobile) {
      font-size: 14px;
      line-height: 1.3;
    }

    &.chart-label {
      font-weight: 300;

      .party-name {
        margin-right: 20px;

        @include breakpoints.respond-to(mobile) {
          margin-right: 0;
        }
      }
    }

    &.chart-percent {
      font-weight: 500;
      text-align: right;

      @include breakpoints.respond-to(mobile) {
        text-align: left;
      }
    }

    &.chart {
      @include breakpoints.respond-to(mobile) {
        margin-bottom: 10px;
      }
    }
  }
}

// .party-list .labeled-chart {
//   // min-height: 46px;

//   @include breakpoints.respond-to(mobile) {
//     flex-direction: column;
//     align-items: start;
//   }

//   .column.chart-label {
//     line-height: 1.1;
//     // margin-top: -10px;
//     // margin-bottom: -10px;
//     margin-top: 0;
//     margin-bottom: 0;
//     width: 100px;

//     @include breakpoints.respond-to(mobile) {
//       width: 100%;
//     }
//   }

//   .column.chart-percent {
//     width: 60px;
//     flex: none;
//     .progress_number {
//       padding-left: 0;
//     }
//   }

//   .column.chart {
//     @include breakpoints.respond-to(mobile) {
//       width: 100%;
//       margin-left: 0;
//     }
//   }
// }
</style>
