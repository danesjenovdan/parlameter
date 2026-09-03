<template>
  <card-wrapper :header-config="headerConfig">
    <div class="zakon osnovne-informacije-zakona">
      <div class="row">
        <div class="parlaicon-container">
          <span
            class="parlaicon parlaicon-legislation-act"
            aria-hidden="true"
          ></span>
        </div>
        <div class="bordertop0">
          <span class="key">
            <span>{{ $t('legislation-type') }}: </span>
            <b>{{
              $t(`legislation-classifications.${results.classification}`)
            }}</b>
          </span>
        </div>
      </div>

      <div v-if="results.epa" class="row">
        <div class="parlaicon-container">
          <span
            class="parlaicon parlaicon-legislation-epa"
            aria-hidden="true"
          ></span>
        </div>
        <div class="bordertop0">
          <span class="key">
            <span>{{ $t('epa') }}: </span>
            <b>{{ results.epa }}</b>
          </span>
        </div>
      </div>

      <div v-if="results.proposed_by" class="row">
        <div class="parlaicon-container">
          <span
            class="parlaicon parlaicon-legislation-proposer"
            aria-hidden="true"
          ></span>
        </div>
        <div class="bordertop0">
          <span class="key">
            <span>{{ $t('legislation-proposer') }}: </span>
            <b>{{ results.proposed_by }}</b>
          </span>
        </div>
      </div>

      <div v-if="results.procedure_type" class="row">
        <div class="parlaicon-container">
          <span
            class="parlaicon parlaicon-legislation-procedure"
            aria-hidden="true"
          ></span>
        </div>
        <div class="bordertop0">
          <span class="key">
            <span>{{ $t('legislation-procedure-type') }}: </span>
            <b>{{ results.procedure_type }}</b>
          </span>
        </div>
      </div>

      <div v-if="results.timestamp" class="row">
        <div class="parlaicon-container">
          <span
            class="parlaicon parlaicon-legislation-date"
            aria-hidden="true"
          ></span>
        </div>
        <div class="bordertop0">
          <span class="key">
            <span>{{ $t('legislation-procedure-start') }}: </span>
            <b>{{ formatDate(results.timestamp) }}</b>
          </span>
        </div>
      </div>

      <div v-if="results.tags?.length" class="row">
        <div class="parlaicon-container">
          <span
            class="parlaicon parlaicon-legislation-tags"
            aria-hidden="true"
          ></span>
        </div>
        <div class="bordertop0">
          <span class="key">
            <span>{{ $t('legislation-areas') }}: </span>
            <template v-for="tag in results.tags" :key="`${tag}`">
              <span class="badge">{{ tag }}</span>
            </template>
          </span>
        </div>
      </div>
    </div>
  </card-wrapper>
</template>

<script>
import common from '@/_mixins/common.js';
import links from '@/_mixins/links.js';
import { defaultHeaderConfig } from '@/_mixins/altHeaders.js';
import dateFormatter from '@/_helpers/dateFormatter.js';

export default {
  name: 'CardLegislationInfo',
  mixins: [common, links],
  data() {
    const { cardData } = this.$root.$options.contextData;
    const results = cardData?.data?.results ?? {};

    return {
      results,
      headerConfig: defaultHeaderConfig(this, {
        heading: cardData?.data?.mandate?.description,
        // title: results?.legislation?.text,
      }),
    };
  },
  methods: {
    formatDate: dateFormatter,
  },
};
</script>

<style lang="scss" scoped>
@use 'parlassets/scss/breakpoints';
@use 'parlassets/scss/colors';

.parlaicon-container {
  padding: 10px 16px;
  @include breakpoints.respond-to(desktop) {
    min-width: 70px;
  }
}

.bordertop {
  border-top: 1px solid colors.$background;
  padding: 10px 0;
  margin: 5px 0;
}

.bordertop0 {
  border-top: 1px solid colors.$background;
  padding: 0;
  margin: 0;
}

.bordertop,
.bordertop0 {
  flex: 1;
}

.zakon h3 {
  font-weight: 400;
}

.osnovne-informacije-zakona {
  display: flex;
  flex-direction: column;
  height: 100%;

  .row {
    display: flex;
    flex: 1;
    margin: 0;
    min-height: 0; // firefox flex bug
    min-height: -moz-fit-content;
    min-height: fit-content;

    > div {
      display: flex;
      flex-direction: column;
      justify-content: center;
    }

    .key {
      color: colors.$font-default;
    }

    .badge {
      display: inline-block;
      margin-left: 4px;
      background-color: transparent;
      border: 1px solid colors.$font-default;
      border-radius: 0;
      font-size: 14px;
      font-weight: 400;
      color: colors.$font-default;
    }
  }
}
</style>
