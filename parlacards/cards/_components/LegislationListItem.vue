<template>
  <div class="item">
    <div class="column name-col">
      <div>
        <a :href="getLegislationLink(law)" class="funblue-light-hover">
          {{ law.text }}
        </a>
      </div>
    </div>
    <div v-if="showEpaColumn" class="column epa-col">{{ law.epa }}</div>
    <div class="column result-col">
      <div>
        <div class="outcome">
          <i :class="['parlaicon', status.iconClass]" />
          <div class="text">{{ $t(status.translationKey) }}</div>
        </div>
      </div>
    </div>
  </div>
</template>

<script>
import links from '@/_mixins/links.js';
import legislationStatus from '@/_helpers/legislationStatus.js';

export default {
  name: 'LegislationListItem',
  mixins: [links],
  props: {
    law: {
      type: Object,
      required: true,
    },
    showEpaColumn: {
      type: Boolean,
      default: false,
    },
  },
  computed: {
    status() {
      return legislationStatus(this.law.status);
    },
  },
};
</script>

<style lang="scss" scoped>
@use 'parlassets/scss/breakpoints';

.item {
  @include breakpoints.respond-to(mobile) {
    flex-direction: column;
  }

  .column {
    &.name-col {
      flex: 3;
      font-size: 14px;

      a {
        margin-left: -0.3em;
        padding: 0.15em 0.3em;
        -webkit-box-decoration-break: clone;
        box-decoration-break: clone;
      }
    }

    &.epa-col {
      flex: 0 0 80px;
      margin-left: 30px;
    }

    &.result-col {
      flex: 0 0 160px;
      margin-left: 30px;

      .outcome .text {
        min-width: 92px;

        @include breakpoints.respond-to(mobile) {
          min-width: 75px;
          font-size: 14px !important;
        }
      }

      @include breakpoints.respond-to(mobile) {
        margin-left: 8px;
        margin-top: 25px;
      }
    }
  }
}
</style>
