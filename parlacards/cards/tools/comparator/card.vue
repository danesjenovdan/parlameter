<template>
  <card-wrapper :header-config="headerConfig" max-height>
    <div id="primerjalnik">
      <TextFrame class="primerjalnik">
        <div class="primerjalnik-text">
          <i18n-t keypath="comparator-text" tag="p" scope="global">
            <template #same>
              <span class="primerjalnik-for">
                <Tag
                  v-for="person in selectedSamePeople"
                  :key="person.id"
                  @click="person.selected = false"
                >
                  {{ person.label }}
                </Tag>
                <plus @click="sameModalVisible = true" />
              </span>
            </template>
            <template #different>
              <span class="primerjalnik-against">
                <Tag
                  v-for="person in selectedDifferentPeople"
                  :key="person.id"
                  @click="person.selected = false"
                >
                  {{ person.label }}
                </Tag>
                <plus @click="differentModalVisible = true" />
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
                @click="special = !special"
              />
              <label for="ignore-absent">{{ $t('ignore-absent') }}</label>
            </div>
          </div>
        </div>
        <div class="primerjalnik-button">
          <div class="spacer"></div>
          <span class="load-button">
            <LoadLink @click="searchVotesImmediate">
              {{ $t('load') }}
            </LoadLink>
          </span>
          <div>
            <i18n-t
              keypath="comparator-vote-percent"
              tag="p"
              class="summary"
              scope="global"
            >
              <template #num>
                <strong>{{ votes.length }}</strong>
              </template>
              <template #percent>
                <strong v-if="total == 0">{{ formatNumber(0) }}</strong>
                <strong v-else>{{
                  formatNumber((votes.length / total) * 100)
                }}</strong>
              </template>
            </i18n-t>
          </div>
        </div>
      </TextFrame>

      <PTabs :start-tab="selectedTab" @switch="focusTab">
        <PTab :label="$t('tabs.vote-list')">
          <EmptyCircle
            v-if="!card.isLoading && votes.length === 0"
            :text="$t('empty-state-text')"
          />
          <div class="votes-list">
            <ScrollShadow ref="shadow">
              <div
                v-infinite-scroll="loadMore"
                class="votes-list-shadow"
                @scroll="$refs.shadow.check($event.currentTarget)"
              >
                <VoteListItem
                  v-for="vote in votes"
                  :key="vote.id"
                  :vote="vote"
                />
              </div>
              <div v-if="card.isLoading" class="nalagalnik__wrapper">
                <div class="nalagalnik"></div>
              </div>
            </ScrollShadow>
          </div>
        </PTab>
        <PTab :label="$t('tabs.time-chart')">
          <EmptyCircle
            v-if="!card.isLoading && votes.length === 0"
            :text="$t('empty-state-text')"
          />
          <!-- <TimeChart v-else :data="data" /> -->
        </PTab>
        <PTab :label="$t('tabs.bar-chart')" class="tab-three">
          <div class="mdt-wrapper">
            <EmptyCircle
              v-if="!card.isLoading && votes.length === 0"
              :text="$t('empty-state-text')"
            />
            <!-- <BarChart v-else :data="barChartData" show-numbers /> -->
          </div>
        </PTab>
      </PTabs>

      <Modal
        v-show="sameModalVisible"
        :header="$t('select-parties-people')"
        :button="$t('confirm')"
        @ok="sameModalVisible = false"
        @close="sameModalVisible = false"
      >
        <PSearchDropdown
          v-model="samePeople"
          :placeholder="samePeoplePlaceholder"
        />
      </Modal>

      <Modal
        v-show="differentModalVisible"
        :header="$t('select-parties-people')"
        :button="$t('confirm')"
        @ok="differentModalVisible = false"
        @close="differentModalVisible = false"
      >
        <PSearchDropdown
          v-model="differentPeople"
          :placeholder="differentPeoplePlaceholder"
        />
      </Modal>
    </div>
  </card-wrapper>
</template>

<script>
// import axios from 'axios';
import EmptyCircle from '@/_components/EmptyCircle.vue';
import LoadLink from '@/_components/LoadLink.vue';
import Modal from '@/_components/Modal.vue';
import Plus from '@/_components/Plus.vue';
import ScrollShadow from '@/_components/ScrollShadow.vue';
import infiniteScroll from '@/_directives/infiniteScroll.js';
import PSearchDropdown from '@/_components/SearchDropdown.vue';
import PTab from '@/_components/Tab.vue';
import PTabs from '@/_components/Tabs.vue';
import Tag from '@/_components/Tag.vue';
import TextFrame from '@/_components/TextFrame.vue';
import VoteListItem from '@/_components/VoteListItem.vue';
import numberFormatter from '@/_helpers/numberFormatter.js';
import { defaultHeaderConfig } from '@/_mixins/altHeaders.js';
import common from '@/_mixins/common.js';
import cancelableRequest from '@/_mixins/cancelableRequest.js';
import links from '@/_mixins/links.js';
// import TimeChart from '@/_components/TimeChart.vue';
// import BarChart from '@/_components/BarChart.vue';

export default {
  name: 'CardToolsComparator',
  directives: {
    infiniteScroll,
  },
  components: {
    // BarChart,
    // TimeChart,
    EmptyCircle,
    LoadLink,
    Modal,
    Plus,
    PSearchDropdown,
    PTab,
    PTabs,
    ScrollShadow,
    Tag,
    TextFrame,
    VoteListItem,
  },
  mixins: [common, cancelableRequest, links],
  cardInfo: {
    doubleWidth: true,
  },
  data() {
    const { cardState, cardData } = this.$root.$options.contextData;

    const selectedSamePeople = (() => {
      const samePeople = cardState?.selectedSamePeople || '';
      return samePeople.split(',').map((id) => id.trim());
    })();

    const selectedDifferentPeople = (() => {
      const differentPeople = cardState?.selectedDifferentPeople || '';
      return differentPeople.split(',').map((id) => id.trim());
    })();

    const people = (cardData?.data?.results?.members || []).map((m) => {
      const mid = (m.slug || '').split('-')[0];
      return {
        id: mid,
        slug: m.slug,
        label: m.name,
        image: m.image,
        selected: false,
      };
    });

    const samePeople = people.map((person) => ({
      ...person,
      selected: selectedSamePeople.includes(person.id),
    }));

    const differentPeople = people.map((person) => ({
      ...person,
      selected: selectedDifferentPeople.includes(person.id),
    }));

    const special = cardState?.special && cardState.special !== 'false';

    // TODO: rename "comparator:" to "votes:" in paginator
    return {
      headerConfig: defaultHeaderConfig(this),
      people,
      card: {
        objectCount: cardData?.data?.['comparator:count'] ?? 0,
        currentPage: 1,
        isLoading: false,
      },
      votes: cardData?.data?.results?.votes ?? [],
      total: 0,
      special,
      samePeople,
      differentPeople,
      sameModalVisible: false,
      differentModalVisible: false,
      selectedTab: 0,
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
    selectedSamePeople() {
      return this.samePeople.filter((person) => person.selected);
    },
    selectedDifferentPeople() {
      return this.differentPeople.filter((person) => person.selected);
    },
    // barChartData() {
    //   const tags = this.data.reduce((acc, d) => {
    //     if (acc.indexOf(d.results.tags[0]) === -1) {
    //       acc.push(d.results.tags[0]);
    //     }
    //     return acc;
    //   }, []);

    //   return tags.map((tag) => ({
    //     label: tag || 'Brez MDT', // TODO i18n
    //     value: this.data.filter((d) => d.results.tags[0] === tag).length,
    //   }));
    // },
    searchUrl() {
      const url = new URL(this.cardData.url);
      url.searchParams.set('comparator:page', this.card.currentPage);

      if (this.selectedSamePeople.length > 0) {
        url.searchParams.set(
          'people_same',
          this.selectedSamePeople.map((p) => p.id).join(','),
        );
      } else {
        url.searchParams.delete('people_same');
      }

      if (this.selectedDifferentPeople.length > 0) {
        url.searchParams.set(
          'people_different',
          this.selectedDifferentPeople.map((p) => p.id).join(','),
        );
      } else {
        url.searchParams.delete('people_different');
      }

      return url.toString();
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
  methods: {
    searchVotesImmediate() {
      this.card.isLoading = true;
      this.votes = [];
      this.card.objectCount = 0;
      this.card.currentPage = 1;
      this.makeRequest(this.searchUrl).then((response) => {
        this.votes = response?.data?.results?.votes || [];
        this.card.objectCount = response?.data?.['comparator:count'];
        this.card.currentPage = 1;
        this.card.isLoading = false;
      });
    },
    loadMore() {
      if (this.card.isLoading) {
        return;
      }
      if (this.votes.length >= this.card.objectCount) {
        return;
      }

      this.card.isLoading = true;
      this.card.currentPage += 1;

      const requestedPage = this.card.currentPage;
      this.makeRequest(this.searchUrl).then((response) => {
        if (response?.data?.['comparator:page'] === requestedPage) {
          const newVotes = response?.data?.results?.votes || [];
          this.votes.push(...newVotes);
        }
        this.card.isLoading = false;
      });
    },
    focusTab(index) {
      this.selectedTab = index;
    },
    formatNumber(number) {
      return numberFormatter(number, { percent: true });
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
    .p-tabs-content {
      margin-top: 8px;
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

  .votes-list {
    .votes-list-shadow {
      overflow-y: auto;
      overflow-x: hidden;
      height: breakpoints.$full-card-height - 117;
    }
  }

  .nalagalnik__wrapper {
    position: absolute;
    top: 0;
    bottom: 0;
    left: 0;
    right: 0;
    background: colors.$white-hover;
    z-index: 4;

    .nalagalnik {
      position: absolute;
      top: calc(50% - 50px);
    }
  }
}
</style>
