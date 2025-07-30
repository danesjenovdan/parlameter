<template>
  <card-wrapper
    :content-class="{ 'is-loading': loading }"
    :header-config="headerConfig"
  >
    <div id="primerjalnik">
      <text-frame class="primerjalnik">
        <div class="primerjalnik-text">
          <i18n-t keypath="comparator-text" tag="p">
            <template #same>
              <span class="primerjalnik-for">
                <tag
                  v-for="party in sameParties"
                  :key="party.id"
                  @click="togglePartySame(party)"
                >
                  {{ party.acronym }}
                </tag>
                <tag
                  v-for="person in selectedSamePeople"
                  :key="person.id"
                  @click="removePerson(person)"
                >
                  {{ person.label }}
                </tag>
                <plus @click="toggleModal('same', true)" />
              </span>
            </template>
            <template #different>
              <span class="primerjalnik-against">
                <tag
                  v-for="party in differentParties"
                  :key="party.id"
                  @click="togglePartyDifferent(party)"
                >
                  {{ party.acronym }}
                </tag>
                <tag
                  v-for="person in selectedDifferentPeople"
                  :key="person.id"
                  @click="removePerson(person)"
                >
                  {{ person.name }}
                </tag>
                <plus @click="toggleModal('different', true)" />
              </span>
            </template>
          </i18n-t>
          <div class="searchfilter-checkboxes">
            <div class="searchfilter-checkbox">
              <input
                id="ignore-absent"
                :checked="special"
                type="checkbox"
                class="checkbox"
                @click="toggleSpecial"
              />
              <label v-t="'ignore-absent'" for="ignore-absent"></label>
            </div>
          </div>
        </div>
        <div class="primerjalnik-button">
          <div class="spacer"></div>
          <span place="load" class="load-button">
            <load-link @click="loadResults">
              {{ $t('load') }}
            </load-link>
          </span>
          <div>
            <i18n-t keypath="comparator-vote-percent" tag="p" class="summary">
              <strong place="num">{{ votes.length }}</strong>
              <strong place="percent">
                {{ total === 0 ? 0 : round((votes.length / total) * 100, 2) }}%
              </strong>
            </i18n-t>
          </div>
        </div>
      </text-frame>

      <p-tabs :start-tab="selectedTab" @switch="focusTab">
        <p-tab :label="$t('tabs.vote-list')">
          <empty-circle
            v-if="votes.length === 0"
            :text="$t('empty-state-text')"
          />
          <div v-else class="glasovanja">
            <seznam-glasovanj :data="voteObject" :show-filters="false" />
          </div>
        </p-tab>
        <p-tab :label="$t('tabs.time-chart')">
          <empty-circle
            v-if="votes.length === 0"
            :text="$t('empty-state-text')"
          />
          <time-chart v-else :data="data" />
        </p-tab>
        <p-tab :label="$t('tabs.bar-chart')" class="tab-three">
          <div class="mdt-wrapper">
            <empty-circle
              v-if="votes.length === 0"
              :text="$t('empty-state-text')"
            />
            <bar-chart v-else :data="barChartData" show-numbers />
          </div>
        </p-tab>
      </p-tabs>

      <modal
        v-show="sameModalVisible"
        :header="$t('select-parties-people')"
        :button="$t('confirm')"
        @ok="toggleModal('same', false)"
        @close="toggleModal('same', false)"
      >
        <p>
          <span
            v-for="party in parties"
            :key="party.id"
            :class="['primerjalnik-ps-switch', { on: party.isSame }]"
            :data-id="party.id"
            :data-acronym="party.acronym"
            @click="togglePartySame(party)"
          >
            {{ party.acronym }}
          </span>
        </p>
        <p-search-dropdown
          v-model="samePeople"
          :placeholder="samePeoplePlaceholder"
        />
      </modal>

      <modal
        v-show="differentModalVisible"
        :header="$t('select-parties-people')"
        :button="$t('confirm')"
        @ok="toggleModal('different', false)"
        @close="toggleModal('different', false)"
      >
        <p>
          <span
            v-for="party in parties"
            :key="party.id"
            :class="['primerjalnik-ps-switch', { on: party.isDifferent }]"
            :data-id="party.id"
            :data-acronym="party.acronym"
            @click="togglePartyDifferent(party)"
          >
            {{ party.acronym }}
          </span>
        </p>
        <p-search-dropdown
          v-model="differentPeople"
          :placeholder="differentPeoplePlaceholder"
        />
      </modal>
    </div>
  </card-wrapper>
</template>

<script>
import axios from 'axios';
import common from '@/_mixins/common.js';
import links from '@/_mixins/links.js';
import { defaultDynamicHeaderConfig } from '@/_mixins/altHeaders.js';
import BarChart from '@/_components/BarChart.vue';
import EmptyCircle from '@/_components/EmptyCircle.vue';
import LoadLink from '@/_components/LoadLink.vue';
import Modal from '@/_components/Modal.vue';
import Plus from '@/_components/Plus.vue';
import PSearchDropdown from '@/_components/SearchDropdown.vue';
import PTab from '@/_components/Tab.vue';
import PTabs from '@/_components/Tabs.vue';
import Tag from '@/_components/Tag.vue';
import TextFrame from '@/_components/TextFrame.vue';
import TimeChart from '@/_components/TimeChart.vue';

export default {
  name: 'CardToolsComparator',
  components: {
    BarChart,
    EmptyCircle,
    PSearchDropdown,
    LoadLink,
    Modal,
    Plus,
    PTab,
    PTabs,
    Tag,
    TextFrame,
    TimeChart,
    // SeznamGlasovanj,
  },
  mixins: [common, links],
  cardInfo: {
    doubleWidth: true,
  },
  data() {
    const { cardState, cardData } = this.$root.$options.contextData;

    return {
      parentOrgId: cardData?.id,
      loading: true,
      parties: [],
      samePeople: [],
      differentPeople: [],
      special: !!cardState?.special,
      data: [],
      total: 0,
      sameModalVisible: false,
      differentModalVisible: false,
      selectedTab: cardState?.selectedTab || 0,
      headerConfig: defaultDynamicHeaderConfig(this, {
        circleIcon: 'primerjalnik',
      }),
    };
  },
  computed: {
    samePeoplePlaceholder() {
      return this.selectedSamePeople.length > 0
        ? this.$t('selected-mps', { num: this.selectedSamePeople.length })
        : this.$t('select-mps');
    },
    differentPeoplePlaceholder() {
      return this.selectedDifferentPeople.length > 0
        ? this.$t('selected-mps', { num: this.selectedDifferentPeople.length })
        : this.$t('select-mps');
    },
    queryUrl() {
      // const base = `${this.slugs.urls.analize}/s/getComparedVotes/`;
      // const samePeopleIds = this.selectedSamePeople
      //   .map((person) => person.id)
      //   .toString();
      // const samePartyIds = this.sameParties.map((party) => party.id).toString();
      // const diffPeopleIds = this.selectedDifferentPeople
      //   .map((person) => person.id)
      //   .toString();
      // const diffPartyIds = this.differentParties
      //   .map((party) => party.id)
      //   .toString();
      // const url = `${base}?people_same=${samePeopleIds}&parties_same=${samePartyIds}&people_different=${diffPeopleIds}&parties_different=${diffPartyIds}`;
      // if (this.special) {
      //   return `${url}&special=true`;
      // }
      // return url;
      return '';
    },
    votes() {
      return this.data || [];
    },
    voteObject() {
      return {
        votes: this.data.map((v) => ({
          ...v.results,
          session_id: v.session.id,
        })),
        session: {},
        tags: [],
      };
    },
    sameParties() {
      return this.parties.filter((party) => party.isSame);
    },
    differentParties() {
      return this.parties.filter((party) => party.isDifferent);
    },
    selectedSamePeople() {
      return this.samePeople.filter((person) => person.selected);
    },
    selectedDifferentPeople() {
      return this.differentPeople.filter((person) => person.selected);
    },
    barChartData() {
      const tags = this.data.reduce((acc, d) => {
        if (acc.indexOf(d.results.tags[0]) === -1) {
          acc.push(d.results.tags[0]);
        }
        return acc;
      }, []);

      return tags.map((tag) => ({
        label: tag || 'Brez MDT', // TODO i18n
        value: this.data.filter((d) => d.results.tags[0] === tag).length,
      }));
    },
  },
  watch: {
    selectedSamePeople(newSelectedSamePeople) {
      newSelectedSamePeople.forEach((person) => {
        this.selectedDifferentPeople
          .filter((p) => p.id === person.id)
          .forEach((p) => {
            p.selected = false;
          });
      });
    },
    selectedDifferentPeople(newSelectedDifferentPeople) {
      newSelectedDifferentPeople.forEach((person) => {
        this.selectedSamePeople
          .filter((p) => p.id === person.id)
          .forEach((p) => {
            p.selected = false;
          });
      });
    },
  },
  mounted() {
    // const sameParties = this.$options.contextData.cardState?.sameParties || [];
    // const differentParties =
    //   this.$options.contextData.cardState?.differentParties || [];
    // this.parties = this.generateParties(this.$options.contextData.cardData).map(
    //   (party) => ({
    //     id: party.properId,
    //     acronym: party.acronym,
    //     isCoalition: party.isCoalition,
    //     name: party.name,
    //     isSame: sameParties.indexOf(party.properId) > -1,
    //     isDifferent: differentParties.indexOf(party.properId) > -1,
    //   })
    // );
    // const samePeople = this.$options.contextData.cardState?.samePeople || [];
    // const differentPeople =
    //   this.$options.contextData.cardState?.differentPeople || [];
    // this.samePeople = this.generatePeople(
    //   this.$options.contextData.cardData
    // ).map((person) => ({
    //   selected: samePeople.indexOf(person.id) > -1,
    //   label: person.label,
    //   id: person.id,
    //   image: person.image,
    // }));
    // this.differentPeople = this.generatePeople(
    //   this.$options.contextData.cardData
    // ).map((person) => ({
    //   selected: differentPeople.indexOf(person.id) > -1,
    //   label: person.label,
    //   id: person.id,
    //   image: person.image,
    // }));
    // this.loadResults();
  },
  methods: {
    toggleSpecial() {
      this.special = !this.special;
    },
    round(value, decimals) {
      return Number(`${Math.round(`${value}e${decimals}`)}e-${decimals}`);
    },
    togglePartySame(party) {
      party.isDifferent = false;
      party.isSame = !party.isSame;
    },
    togglePartyDifferent(party) {
      party.isDifferent = !party.isDifferent;
      party.isSame = false;
    },
    removePerson(person) {
      person.selected = false;
    },
    toggleModal(modalType, newState) {
      this[`${modalType}ModalVisible`] = newState;
    },
    loadResults() {
      this.loading = true;
      axios
        .get(this.queryUrl)
        .then((response) => {
          // TODO: time-chart needs this:
          // const dateParser = d3.timeParse('%d.%m.%Y');
          // const data = Array.from(new Set(this.data.map((d) => d.results.date)))
          //   .map((date) => ({
          //     date: dateParser(date),
          //     value: this.data.filter((d) => d.results.date === date).length,
          //   }))
          //   .sort((a, b) => a.date - b.date);

          this.data = response.data.results;
          this.total = response.data.total;
          this.loading = false;
        })
        .catch((error) => {
          // eslint-disable-next-line no-console
          console.log(error);
          this.loading = false;
        });
    },
    focusTab(tabindex) {
      this.selectedTab = tabindex;
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

#primerjalnik {
  :deep(.p-tabs) {
    .p-tabs-content,
    .p-tabs-content .tab-content {
      overflow-y: visible;
      overflow-x: visible;
    }

    .p-tabs-content {
      margin-top: 6px;
    }
  }

  :deep(.word-list) {
    max-height: none;
    height: 420px;
    overflow-y: auto;

    .column-label {
      flex: 2;

      .chart-label .label-container {
        line-height: 1;

        @include breakpoints.respond-to(mobile) {
          font-size: 12px;
        }
      }
    }
  }

  .glasovanja {
    :deep(#votingCard) {
      height: 420px;
    }
  }

  .mdt-wrapper {
    :deep(.progress-bar) {
      background-color: colors.$third;
    }
  }

  .tab-content,
  .mdt-wrapper {
    height: 420px;
  }

  .primerjalnik-ps-switch {
    background: colors.$white;
    cursor: pointer;
    padding: 5px;
    display: inline-block;
    margin: 5px;
    color: colors.$font-default;

    &::after {
      content: '×';
      margin-left: 8px;
      font-size: 20px;
      line-height: 20px;
      position: relative;
      top: 2px;
      transform: rotate(45deg);
      display: inline-block;
      transition: transform 0.2s ease-out;
      color: colors.$first;
    }

    &.on {
      background: colors.$first;
      color: colors.$white;

      &::after {
        transform: rotate(0deg);
        color: colors.$white;
      }
    }
  }

  .primerjalnik.text-frame {
    display: flex;
    padding: 10px;

    @include breakpoints.respond-to(mobile) {
      flex-direction: column;
    }

    .primerjalnik-text,
    .primerjalnik-button {
      display: flex;
      flex-direction: column;
      justify-content: space-between;
    }

    .primerjalnik-text {
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

    .primerjalnik-button {
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
