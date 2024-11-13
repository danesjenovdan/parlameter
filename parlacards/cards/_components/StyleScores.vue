<template>
  <card-wrapper :header-config="headerConfig" half-height>
    <div v-cloak class="card-content-front">
      <div class="progress_flex">
        <div class="column-title progress_title">
          <div class="me_poslanec">
            <div
              v-t="'style-scores.elevated-vocabulary'"
              class="poslanec_title"
            ></div>
          </div>
          <div class="me_poslanec">
            <div
              v-t="'style-scores.simple-vocabulary'"
              class="poslanec_title"
            ></div>
          </div>
          <div class="me_poslanec">
            <div
              v-t="'style-scores.excessive-vocabulary'"
              class="poslanec_title"
            ></div>
          </div>
        </div>
        <div class="column-bar progress_bar">
          <div class="me_poslanec">
            <div class="progress smallbar">
              <div
                :aria-valuenow="results.sophisticated"
                :style="getBarStyle('sophisticated')"
                class="progress-bar funblue"
                role="progressbar"
                aria-valuemin="0"
                aria-valuemax="100"
              >
                <div class="progress_number">
                  {{ formatNumber(results.sophisticated) }}
                </div>
              </div>
            </div>
          </div>
          <div class="me_poslanec">
            <div class="progress smallbar">
              <div
                :aria-valuenow="results.simple"
                :style="getBarStyle('simple')"
                class="progress-bar funblue"
                role="progressbar"
                aria-valuemin="0"
                aria-valuemax="100"
              >
                <div class="progress_number">
                  {{ formatNumber(results.simple) }}
                </div>
              </div>
            </div>
          </div>
          <div class="me_poslanec">
            <div class="progress smallbar">
              <div
                :aria-valuenow="results.problematic"
                :style="getBarStyle('problematic')"
                class="progress-bar funblue"
                role="progressbar"
                aria-valuemin="0"
                aria-valuemax="100"
              >
                <div class="progress_number">
                  {{ formatNumber(results.problematic) }}
                </div>
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>
  </card-wrapper>
</template>

<script>
import common from '@/_mixins/common.js';
import {
  personSpeechesContextUrl,
  partySpeechesContextUrl,
} from '@/_mixins/contextUrls.js';
import { personTitle, partyTitle } from '@/_mixins/titles.js';
import { personHeader, partyHeader } from '@/_mixins/altHeaders.js';
import { personOgImage, partyOgImage } from '@/_mixins/ogImages.js';
import numberFormatter from '@/_helpers/numberFormatter.js';

export default {
  name: 'StyleScores',
  mixins: [common],
  props: {
    type: {
      type: String,
      required: true,
      validator: (value) => ['person', 'party'].indexOf(value) > -1,
    },
    results: {
      type: Object,
      required: true,
    },
    person: {
      type: Object,
      default: () => ({}),
    },
    party: {
      type: Object,
      default: () => ({}),
    },
  },
  computed: {
    headerConfig() {
      if (this.type === 'person') {
        return personHeader.computed.headerConfig.call(this);
      }
      return partyHeader.computed.headerConfig.call(this);
    },
    maxValue() {
      return Math.max(
        this.results.sophisticated,
        this.results.simple,
        this.results.problematic,
      );
    },
  },
  created() {
    (this.type === 'person' ? personTitle : partyTitle).created.call(this);
    (this.type === 'person' ? personOgImage : partyOgImage).created.call(this);
    (this.type === 'person'
      ? personSpeechesContextUrl
      : partySpeechesContextUrl
    ).created.call(this);
  },
  methods: {
    getBarStyle(key) {
      return { width: `${(this.results[key] / this.maxValue) * 70}%` };
    },
    formatNumber(number) {
      return numberFormatter(number, { precision: 2, percent: true });
    },
  },
};
</script>

<style lang="scss" scoped>
@use 'parlassets/scss/colors';

.progress {
  overflow: visible; /* this overrides bootstrap which we should get rid of anyway */
}
.column-title .poslanec_title {
  line-height: 20px;
  margin-top: 5px;
  margin-bottom: 5px;
  margin-right: 10px;
}
.column-title .me_poslanec {
  display: flex;
  align-items: center;
  height: 54px;
}
.me_poslanec {
  padding-top: 12px;
  padding-bottom: 12px;
}
.column-bar .progress-bar {
  position: relative;
}
.column-bar .progress_number {
  position: absolute;
  right: 0;
  transform: translateX(100%);
  color: colors.$font-default;
  line-height: 30px;
  min-width: 70px;
  text-align: left;
}
</style>
