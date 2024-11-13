<template>
  <card-wrapper
    :content-class="{ 'is-loading': loading }"
    :header-config="headerConfig"
  >
    <template #generator>
      <tools-tabs current-tool="wordGroups" />
    </template>

    <div id="skupine-besed">
      <text-frame class="skupine-besed">
        <div class="skupine-besed-text">
          <i18n-t keypath="wordgroups-text" tag="p">
            <template #words>
              <span>
                <tag
                  v-for="(word, index) in words"
                  :key="index + word"
                  @click="removeWord(word)"
                >
                  {{ word }}
                </tag>
                <plus @click="toggleModal(true)" />
              </span>
            </template>
          </i18n-t>
          <div class="searchfilter-checkboxes">
            <div class="searchfilter-checkbox">
              <input
                id="show-relative"
                :checked="showRelative"
                type="checkbox"
                class="checkbox"
                @click="changeShowRelative"
              />
              <label v-t="'show-relative'" for="show-relative"></label>
            </div>
          </div>
        </div>
        <div class="skupine-besed-button">
          <div class="spacer"></div>
          <span class="load-button">
            <load-link @click="loadResults(true)">
              {{ $t('load') }}
            </load-link>
          </span>
          <div class="spacer"></div>
        </div>
      </text-frame>

      <p-tabs :start-tab="selectedTab" @switch="focusTab">
        <p-tab :label="$t('speakers')">
          <scroll-shadow ref="shadow">
            <div
              class="results"
              @scroll="$refs.shadow.check($event.currentTarget)"
            >
              <bar-chart
                v-if="results.people.length"
                :data="showRelative ? resultsRelative.people : results.people"
                :show-percentage="!showRelative"
                show-numbers
                flexible-labels
              />
              <empty-circle v-else :text="emptyText" />
            </div>
          </scroll-shadow>
        </p-tab>
        <p-tab :label="$t('parties')">
          <scroll-shadow ref="shadowPS">
            <div
              class="results"
              @scroll="$refs.shadowPS.check($event.currentTarget)"
            >
              <bar-chart
                v-if="results.parties.length"
                :data="showRelative ? resultsRelative.parties : results.parties"
                :show-percentage="!showRelative"
                show-numbers
                flexible-labels
              />
              <empty-circle v-else :text="emptyText" />
            </div>
          </scroll-shadow>
        </p-tab>
      </p-tabs>

      <modal
        v-if="modalShown"
        :header="$t('input-words')"
        :button="$t('confirm')"
        @close="toggleModal(false)"
        @ok="toggleModal(false, true)"
      >
        <search-field
          v-model="modalInputText"
          @enter="toggleModal(false, true)"
        />
      </modal>
    </div>
  </card-wrapper>
</template>

<script>
import axios from 'axios';
import links from '@/_mixins/links.js';
import { defaultHeaderConfig } from '@/_mixins/altHeaders.js';
import common from '@/_mixins/common.js';
import ToolsTabs from '@/_components/ToolsTabs.vue';
import BarChart from '@/_components/BarChart.vue';
import EmptyCircle from '@/_components/EmptyCircle.vue';
import LoadLink from '@/_components/LoadLink.vue';
import Modal from '@/_components/Modal.vue';
import Plus from '@/_components/Plus.vue';
import PTab from '@/_components/Tab.vue';
import PTabs from '@/_components/Tabs.vue';
import SearchField from '@/_components/SearchField.vue';
import Tag from '@/_components/Tag.vue';
import TextFrame from '@/_components/TextFrame.vue';
import ScrollShadow from '@/_components/ScrollShadow.vue';

export default {
  name: 'CardToolsWordGroups',
  components: {
    ToolsTabs,
    BarChart,
    EmptyCircle,
    LoadLink,
    Modal,
    Plus,
    PTab,
    PTabs,
    SearchField,
    Tag,
    TextFrame,
    ScrollShadow,
  },
  mixins: [common, links],
  cardInfo: {
    doubleWidth: true,
  },
  data() {
    const { cardState, cardData } = this.$root.$options.contextData;

    return {
      data: cardData || {},
      emptyText: this.$t('empty-text'),
      headerConfig: defaultHeaderConfig(this),
      showRelative: cardState?.showRelative || false,
      modalShown: false,
      modalInputText: '',
      results: {
        people: [],
        parties: [],
      },
      resultsRelative: {
        people: [],
        parties: [],
      },
      selectedTab: cardState?.selectedTab || 0,
      words: cardState?.words || [],
      loading: false,
    };
  },
  computed: {
    urlParameters() {
      const state = {};
      if (this.words.length > 0) {
        state.words = this.words;
      }
      if (this.selectedTab !== 0) {
        state.selectedTab = this.selectedTab;
      }
      if (this.showRelative) {
        state.showRelative = this.showRelative;
      }
      return state;
    },
  },
  mounted() {
    if (this.words.length) {
      this.loadResults();
    }
  },
  methods: {
    focusTab(tab) {
      this.selectedTab = tab;
    },
    changeShowRelative() {
      this.showRelative = !this.showRelative;
    },
    toggleModal(newState, addWords = false) {
      if (addWords) {
        this.modalInputText
          .split(',')
          .map((word) => word.trim())
          .forEach(this.addWord);
      }
      this.modalInputText = '';
      this.modalShown = newState;
    },
    addWord(word) {
      const position = this.words.indexOf(word);
      if (position === -1) {
        this.words.push(word);
      }
    },
    removeWord(word) {
      const position = this.words.indexOf(word);
      if (position > -1) {
        this.words.splice(position, 1);
      }
    },
    loadResults(user) {
      if (this.words.length < 2 || this.loading) {
        if (user) {
          // eslint-disable-next-line no-alert
          alert(this.$t('empty-text'));
        }
        return;
      }

      this.loading = true;

      const query = this.words
        .map((word) => (word.indexOf(' ') > -1 ? `"${word}"` : word))
        .join(' ');

      axios
        .get(
          `${this.slugs.urls.isci}/search/speeches?q=${encodeURIComponent(
            query,
          )}`,
        )
        .then((response) => {
          const scoreHigherThanZero = (i) => i.score > 0;

          const parties = response.data.facet_counts.facet_fields.party
            .filter((party) => party.party)
            .filter((party) => party.party.classification === 'pg')
            .filter(scoreHigherThanZero)
            .filter((party) => party.party.acronym !== 'unknown')
            .map((party) => ({
              label: party.party.acronym,
              value: Number(
                (
                  party.score /
                  (this.data.orgs[party.party.id] / this.data.all_speeches)
                ).toFixed(4) || 0,
              ),
              link: this.getPartyLinkSafe(party.party),
            }))
            .reduce((prev, cur) => {
              const out = prev;
              let push = true;
              if (cur.label === 'PS NP') {
                prev.forEach((thing) => {
                  if (thing.label === 'PS NP') {
                    push = false;
                  }
                });
              }
              if (push) {
                out.push(cur);
              }
              return out;
            }, []);

          const people = response.data.facet_counts.facet_fields.person
            .filter((person) => person.person)
            .filter(scoreHigherThanZero)
            .map((person) => ({
              label: person.person.name,
              // eslint-disable-next-line max-len
              value: Number(
                (
                  person.score /
                  (this.data.people[person.person.id] / this.data.all_speeches)
                ).toFixed(4),
              ),
              link: this.getPersonLink(person.person),
              portrait: this.getPersonPortrait(person.person),
            }));

          this.resultsRelative = { parties, people };

          const parties2 = response.data.facet_counts.facet_fields.party
            .filter((party) => party.party)
            .filter((party) => party.party.classification === 'pg')
            .filter(scoreHigherThanZero)
            .filter((party) => party.party.acronym !== 'unknown')
            .map((party) => ({
              label: party.party.acronym,
              // eslint-disable-next-line max-len
              value: party.score,
              link: this.getPartyLinkSafe(party.party),
            }));

          const people2 = response.data.facet_counts.facet_fields.person
            .filter((person) => person.person)
            .filter(scoreHigherThanZero)
            .map((person) => ({
              label: person.person.name,
              // eslint-disable-next-line max-len
              value: person.score,
              link: this.getPersonLink(person.person),
              portrait: this.getPersonPortrait(person.person),
            }));

          this.results = { parties: parties2, people: people2 };

          this.loading = false;
        });
    },
    getPartyLinkSafe(party) {
      return party.id === -1 ? '' : this.getPartyLink(party);
    },
  },
};
</script>

<style lang="scss" scoped>
@use 'parlassets/scss/breakpoints';
@use 'parlassets/scss/colors';

:deep(.card-content) {
  min-height: 660px;
}

#skupine-besed {
  :deep(.p-tabs .p-tabs-content),
  :deep(.p-tabs .p-tabs-content .tab-content) {
    overflow-y: visible;
    overflow-x: visible;
  }

  .results {
    height: 400px;
    padding-top: 12px;
    overflow-y: auto;
    margin-top: 6px;

    :deep(.word-list) {
      max-height: none;
    }
  }

  .skupine-besed.text-frame {
    display: flex;
    padding: 10px;

    @include breakpoints.respond-to(mobile) {
      flex-direction: column;
    }

    .skupine-besed-text,
    .skupine-besed-button {
      display: flex;
      flex-direction: column;
      justify-content: space-between;
    }

    .skupine-besed-text {
      flex: 1 0 66%;
      padding: 5px 10px 5px 0;

      @include breakpoints.respond-to(mobile) {
        padding-right: 0;
      }

      p {
        margin: 15px 0 20px;

        @include breakpoints.respond-to(mobile) {
          border-bottom: 1px solid colors.$tools-border;
          padding-bottom: 25px;
        }
      }

      .searchfilter-checkboxes {
        display: flex;
        justify-content: center;

        @include breakpoints.respond-to(mobile) {
          margin-bottom: 20px;
        }

        .searchfilter-checkbox {
          height: 30px;

          .checkbox + label {
            text-align: left;
            margin-bottom: 0;
            font-size: 11px;
            line-height: 30px;
            color: colors.$font-default;

            &::before {
              margin-top: 0;
              background-color: transparent;
            }
          }
        }
      }
    }

    .skupine-besed-button {
      flex: 1 0 33%;
      padding: 5px 0 5px 10px;
      border-left: 1px solid colors.$tools-border;

      @include breakpoints.respond-to(mobile) {
        border-left: none;
        padding-left: 0;
      }

      .summary {
        margin: 0;
        line-height: 20px;
        text-align: center;
        font-size: 11px;
        color: colors.$font-default;

        @include breakpoints.respond-to(mobile) {
          margin-top: 15px;
        }
      }
    }
  }
}
</style>
