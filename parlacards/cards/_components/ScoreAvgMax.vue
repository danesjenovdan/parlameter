<template>
  <card-wrapper :header-config="headerConfig" half-height>
    <empty-state v-if="!getMaxValue || getMaxValue <= 0" small />
    <div v-else v-cloak class="card-content-front">
      <div class="progress_flex">
        <div class="column-title progress_title">
          <div class="me_poslanec">
            <div class="poslanec_title">
              {{ getName }}
            </div>
          </div>
          <div class="other_poslanec">
            <div v-t="'average'" class="poslanec_title"></div>
          </div>
          <div class="other_poslanec">
            <div v-t="'maximum'" class="poslanec_title"></div>
          </div>
        </div>
        <div class="column-bar progress_bar">
          <div class="me_poslanec">
            <div class="progress smallbar">
              <div
                :aria-valuenow="getScore"
                :style="getBarStyle('score')"
                class="progress-bar this"
                role="progressbar"
                aria-valuemin="0"
                aria-valuemax="100"
              >
                <span class="sr-only">{{ getScore }}%</span>
                <div class="progress_number">
                  {{ formatNumberWithPrecision(getScore) }}
                </div>
              </div>
            </div>
          </div>
          <div class="other_poslanec">
            <div class="progress smallbar">
              <div
                :aria-valuenow="results.average"
                :style="getBarStyle('average')"
                class="progress-bar other"
                role="progressbar"
                aria-valuemin="0"
                aria-valuemax="100"
              >
                <span class="sr-only">{{ results.average }}%</span>
                <div class="progress_number">
                  {{ formatNumberWithPrecision(results.average) }}
                </div>
              </div>
            </div>
          </div>
          <div class="other_poslanec">
            <div class="progress smallbar">
              <div
                :aria-valuenow="getMaxValue"
                :style="getBarStyle('max')"
                class="progress-bar other"
                role="progressbar"
                aria-valuemin="0"
                aria-valuemax="100"
              >
                <span class="sr-only">{{ getMaxValue }}%</span>
                <template v-if="type === 'person'">
                  <person-pin
                    v-for="member in results.maximum.members"
                    :key="member.slug"
                    :person="member"
                  />
                </template>
                <template v-else>
                  <party-pin v-for="pg in getMaxPGs" :key="pg.id" :party="pg" />
                </template>
              </div>
            </div>
          </div>
        </div>
        <div class="column-number">
          <div class="me_poslanec">
            <div class="progress_number invisible">&nbsp;</div>
          </div>
          <div class="other_poslanec">
            <div class="progress_number invisible">&nbsp;</div>
          </div>
          <div class="other_poslanec">
            <div class="progress_number">
              {{ formatNumberWithPrecision(getMaxValue) }}
            </div>
          </div>
        </div>
      </div>
    </div>
  </card-wrapper>
</template>

<script>
import common from '@/_mixins/common.js';
import links from '@/_mixins/links.js';
import {
  personOverviewContextUrl,
  partyOverviewContextUrl,
  personVotesContextUrl,
  partyVotesContextUrl,
  personSpeechesContextUrl,
  partySpeechesContextUrl,
} from '@/_mixins/contextUrls.js';
import { personTitle, partyTitle } from '@/_mixins/titles.js';
import { personHeader, partyHeader } from '@/_mixins/altHeaders.js';
import { personOgImage, partyOgImage } from '@/_mixins/ogImages.js';
import PersonPin from '@/_components/PersonPin.vue';
import PartyPin from '@/_components/PartyPin.vue';
import EmptyState from '@/_components/EmptyState.vue';
import numberFormatter from '@/_helpers/numberFormatter.js';

export default {
  name: 'ScoreAvgMax',
  components: {
    PersonPin,
    PartyPin,
    EmptyState,
  },
  mixins: [common, links],
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
    context: {
      type: String,
      default: 'overview',
      validator: (value) =>
        ['overview', 'votings', 'speeches'].indexOf(value) > -1,
    },
    precision: {
      type: Number,
      default: 0,
    },
    percent: {
      type: Boolean,
      default: false,
    },
  },
  computed: {
    getName() {
      return this.type === 'person'
        ? this.getPersonName(this.person)
        : this.party.acronym || this.party.name || 'N/A';
    },
    headerConfig() {
      if (this.type === 'person') {
        return personHeader.computed.headerConfig.call(this);
      }
      return partyHeader.computed.headerConfig.call(this);
    },
    getScore() {
      return this.results?.score ?? 0;
    },
    getMaxValue() {
      return this.results?.maximum?.score ?? 0;
    },
    getMaxPGs() {
      return this.results?.maximum?.groups ?? [];
    },
  },
  created() {
    (this.type === 'person' ? personTitle : partyTitle).created.call(this);
    (this.type === 'person' ? personOgImage : partyOgImage).created.call(this);
    if (this.context === 'overview') {
      (this.type === 'person'
        ? personOverviewContextUrl
        : partyOverviewContextUrl
      ).created.call(this);
    } else if (this.context === 'votings') {
      (this.type === 'person'
        ? personVotesContextUrl
        : partyVotesContextUrl
      ).created.call(this);
    } else if (this.context === 'speeches') {
      (this.type === 'person'
        ? personSpeechesContextUrl
        : partySpeechesContextUrl
      ).created.call(this);
    }
  },
  methods: {
    getBarStyle(key) {
      if (key === 'max') {
        return { width: '100%' };
      }
      if (key === 'score') {
        return { width: `${(this.getScore / this.getMaxValue) * 100}%` };
      }
      return { width: `${(this.results[key] / this.getMaxValue) * 100}%` };
    },
    formatNumberWithPrecision(number) {
      return numberFormatter(number, {
        precision: this.precision,
        percent: this.percent,
      });
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
.column-number .progress_number {
  padding-left: 20px;
  line-height: 30px;
}
.me_poslanec,
.other_poslanec {
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
