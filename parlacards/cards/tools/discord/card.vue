<template>
  <card-wrapper :header-config="headerConfig">
    <template #generator>
      <tools-tabs current-tool="discord" />
    </template>

    <div class="filters">
      <div class="filter text-filter">
        <div v-t="'title-search'" class="filter-label"></div>
        <search-field v-model="textFilter" />
      </div>
      <div class="filter type-dropdown">
        <div v-t="'parties'" class="filter-label"></div>
        <p-search-dropdown
          :model-value="allItems"
          :single="true"
          hide-clear
          @select="selectCallback"
        />
      </div>
      <div class="filter tag-dropdown">
        <div v-t="'working-body'" class="filter-label"></div>
        <p-search-dropdown v-model="allTags" />
      </div>
      <div class="filter text-filter">
        <div v-t="'sort-by'" class="filter-label"></div>
        <toggle v-model="selectedSort" :options="sortOptions" />
      </div>
    </div>

    <scroll-shadow ref="shadow">
      <div
        :class="['results', { 'is-loading': loading }]"
        @scroll="$refs.shadow.check($event.currentTarget)"
      >
        <template v-for="day in filteredVotingDays">
          <date-row
            v-if="selectedSort === 'date'"
            :key="day.date"
            :date="day.date"
          />
          <a
            v-for="ballot in day.ballots"
            :key="ballot.id_parladata"
            :href="
              getVoteLink({
                session_id: ballot.session_id,
                vote_id: ballot.id_parladata,
              })
            "
            :target="voteLinkTarget"
            class="ballot"
          >
            <div class="disunion">
              <div class="percentage">{{ Math.round(ballot.maximum) }} %</div>
              <div v-t="'inequality'" class="text"></div>
            </div>
            <div class="name">
              <template
                v-if="
                  ballot.shortened_projects && ballot.shortened_projects.length
                "
              >
                <template v-for="(project, i) in ballot.projects">
                  <div
                    v-if="i !== 0 || project !== ballot.shortened_projects[0]"
                    :key="`${ballot.id_parladata}-${project}-${i}`"
                    :style="{ top: visibleTooltipTopPos }"
                    :class="[
                      'tooltip',
                      `tooltip-${ballot.id_parladata}-${i}`,
                      {
                        'tooltip--show':
                          visibleTooltip === `${ballot.id_parladata}-${i}`,
                      },
                    ]"
                  >
                    {{ project }}
                  </div>
                </template>
                <p class="projects">
                  <component
                    :is="i > 0 ? 'a' : 'span'"
                    v-for="(project, i) in ballot.shortened_projects"
                    :key="`${ballot.id_parladata}-${project}-${i}`"
                    :class="[
                      'project',
                      {
                        'project--tooltip': i !== 0,
                        'project--has-tooltip':
                          i !== 0 || project !== ballot.projects[0],
                      },
                    ]"
                    :data-target="`${ballot.id_parladata}-${i}`"
                    href="#"
                    @click.prevent="() => {}"
                    @mouseover="
                      setVisibleTooltip(`${ballot.id_parladata}-${i}`)
                    "
                    @mouseout="visibleTooltip = null"
                  >
                    <template v-if="i === 0">{{ project }}</template>
                    <span v-else>{{ i + 1 }}</span>
                  </component>
                </p>
              </template>
              {{ ballot.shortened_title }}
            </div>
            <div class="result">
              <template v-if="ballot.result">
                <i class="accepted glyphicon glyphicon-ok"></i>
                <div v-t="'vote-passed'" class="text"></div>
              </template>
              <template v-else>
                <i class="not-accepted glyphicon glyphicon-remove"></i>
                <div v-t="'vote-not-passed'" class="text"></div>
              </template>
            </div>
          </a>
        </template>
      </div>
    </scroll-shadow>
  </card-wrapper>
</template>

<script>
import { parseISO, format } from 'date-fns';
import { groupBy, sortBy, zipObject } from 'lodash-es';
import ToolsTabs from '@/_components/ToolsTabs.vue';
import PSearchDropdown from '@/_components/SearchDropdown.vue';
import StripedButton from '@/_components/StripedButton.vue';
import Toggle from '@/_components/Toggle.vue';
import common from '@/_mixins/common.js';
import links from '@/_mixins/links.js';
import { defaultHeaderConfig } from '@/_mixins/altHeaders.js';
import ScrollShadow from '@/_components/ScrollShadow.vue';
import SearchField from '@/_components/SearchField.vue';
import { parseVoteTitle, shortenVoteTitle } from '@/_helpers/voteTitle.js';
// import axios from 'axios';

export default {
  name: 'CardToolsDiscord',
  components: {
    ToolsTabs,
    PSearchDropdown,
    StripedButton,
    Toggle,
    ScrollShadow,
    SearchField,
  },
  mixins: [common, links],
  cardInfo: {
    doubleWidth: true,
  },
  data() {
    // const { cardData } = this.$root.$options.contextData;
    // const data = Object.keys(cardData).map((key) => {
    //   const obj = cardData[key];
    //   return {
    //     id: Number(key),
    //     ...obj,
    //   };
    // });

    // const all = data.find((o) => o.type === 'parliament');

    // let groups = [];
    // groups.push({
    //   id: all.id,
    //   color: 'dz',
    //   acronym: this.$t('everybody'),
    //   name: this.$t('everybody'),
    // });

    // let coalitions = data.filter((o) => o.type === 'coalition');
    // coalitions = sortBy(coalitions, ['name']);

    // coalitions.forEach((coalition) => {
    //   groups.push({
    //     id: coalition.id,
    //     color: 'koal',
    //     acronym: coalition.name,
    //     name: coalition.name,
    //   });
    // });

    // let namedGroups = [];
    // data.forEach((group) => {
    //   if (!group.disbanded && group.type === 'party') {
    //     namedGroups.push({
    //       id: group.id,
    //       acronym: group.acronym,
    //       color: group.acronym.toLowerCase().replace(/[ +,]/g, '_'),
    //       name: group.acronym,
    //     });
    //   }
    // });

    // namedGroups = sortBy(namedGroups, ['name']);
    // groups = groups.concat(namedGroups);

    return {
      voteData: [],
      loading: false, // true,
      selectedSort: 'maximum',
      sortOptions: {
        maximum: this.$t('sort-by--inequality'),
        date: this.$t('sort-by--date'),
      },
      textFilter: '',
      allTags: [],
      selectedGroup: null, // groups[0].acronym,
      groups: [], // groups,
      allClassifications: [],
      visibleTooltip: null,
      visibleTooltipTopPos: '20px',
    };
  },
  computed: {
    allItems() {
      return this.groups.map((group) => ({
        id: group.acronym,
        label: group.acronym,
        selected: group.acronym === this.selectedGroup,
        colorClass: `${group.acronym
          .toLowerCase()
          .replace(/[ +,]/g, '_')}-background`,
      }));
    },
    selectedTags() {
      return this.allTags.filter((tag) => tag.selected).map((tag) => tag.id);
    },
    selectedClassifications() {
      return this.allClassifications
        .filter((classification) => classification.selected)
        .map((classification) => classification.id);
    },
    filteredVotingDays() {
      return this.getFilteredVotingDays();
    },
    headerConfig() {
      return defaultHeaderConfig(this, {
        circleIcon: 'seznam-glasovanj',
        title: this.dynamicTitle,
      });
    },
    dynamicTitle() {
      return (
        this.$t('card.title') +
        (this.selectedSort === 'date'
          ? this.$t('sort-by--date').toLowerCase()
          : this.$t('sort-by--inequality').toLowerCase())
      );
    },
    voteLinkTarget() {
      if (typeof window !== 'undefined') {
        if (window === window.top) {
          return '_self';
        }
      }
      return '_blank';
    },
  },
  watch: {
    selectedGroup(newValue) {
      this.fetchVotesForGroup(newValue);
    },
  },
  beforeMount() {
    this.fetchVotesForGroup(this.groups?.[0]?.acronym);
  },
  methods: {
    groupBy(array, f) {
      const groups = {};
      array.forEach((o) => {
        const group = JSON.stringify(f(o));
        groups[group] = groups[group] || [];
        groups[group].push(o);
      });
      return Object.keys(groups).map((group) => groups[group]);
    },
    selectCallback(acronym) {
      this.selectGroup(acronym);
    },
    clearCallback() {
      this.selectGroup(this.groups[0].acronym);
    },
    getFilteredVotingDays(onlyFilterByText = false) {
      if (!this.voteData || this.voteData.length === 0) {
        return [];
      }

      const filterBallots = (ballot) => {
        const tagMatch =
          onlyFilterByText ||
          this.selectedTags.length === 0 ||
          ballot.tag.filter((tag) => this.selectedTags.indexOf(tag) > -1)
            .length > 0;
        const textMatch =
          this.textFilter === '' ||
          ballot.text.toLowerCase().indexOf(this.textFilter.toLowerCase()) > -1;
        const classificationMatch =
          onlyFilterByText ||
          this.selectedClassifications.length === 0 ||
          this.selectedClassifications.indexOf(ballot.classification) > -1;
        return tagMatch && textMatch && classificationMatch;
      };

      const votes = sortBy(this.voteData, [this.selectedSort])
        .reverse()
        .map((vote) => {
          const { title, projects } = parseVoteTitle(vote.text);
          const agendas = (vote.agenda_items || []).concat(projects);
          return {
            ...vote,
            title,
            projects: agendas,
            shortened_title: shortenVoteTitle(title),
            shortened_projects: agendas.map((p) => shortenVoteTitle(p, 80)),
          };
        });
      const getDateFromVote = (vote) =>
        vote.date ? format(parseISO(vote.date), 'd. M. y') : null;

      let currentVotingDays;

      if (this.selectedSort === 'date') {
        currentVotingDays = groupBy(votes, getDateFromVote);
      } else {
        currentVotingDays = zipObject(
          votes.map((vote, index) => `${getDateFromVote(vote)}-${index}`),
          votes.map((vote) => [vote]),
        );
      }

      const mappedVotingDays = [];
      Object.keys(currentVotingDays).forEach((key) => {
        mappedVotingDays.push({
          date: key,
          ballots: currentVotingDays[key].filter(filterBallots),
        });
      });

      return mappedVotingDays.filter(
        (votingDay) => votingDay.ballots.length > 0,
      );
    },
    selectGroup(acronym) {
      this.selectedGroup =
        this.selectedGroup !== acronym ? acronym : this.groups[0].acronym;
    },
    fetchVotesForGroup(acronym) {
      // eslint-disable-next-line no-console
      console.log('TODO: fetchVotesForGroup for', acronym);
      // this.loading = true;
      // const groupId = find(this.groups, { acronym })?.id;
      // axios
      //   .get(`${this.slugs.urls.analize}/pg/getIntraDisunionOrg/${groupId}`)
      //   .then((response) => {
      //     if (this.allTags.length === 0) {
      //       this.allTags = response.data.all_tags.map((tag) => ({
      //         id: tag,
      //         label: tag,
      //         selected: false,
      //       }));
      //     }
      //     // TODO: this.voteData = response.data.results;
      //     this.voteData = response.data.results || response.data[acronym];
      //     this.allClassifications = [];
      //     // eslint-disable-next-line no-restricted-syntax, guard-for-in
      //     for (const classificationKey in response.data.classifications) {
      //       this.allClassifications.push({
      //         id: classificationKey,
      //         label: this.$t(
      //           `vote_types.${response.data.classifications[classificationKey]}`
      //         ),
      //         selected: false,
      //       });
      //     }
      //     const selectFromState = (items, stateItemIds) =>
      //       items.map((item) =>
      //         assign({}, item, { selected: stateItemIds.indexOf(item.id) > -1 })
      //       );
      //     if (cardState) {
      //       const state = cardState;
      //       if (state.text) {
      //         this.textFilter = state.text;
      //       }
      //       if (state.classifications) {
      //         this.allClassifications = selectFromState(
      //           this.allClassifications,
      //           state.classifications
      //         );
      //       }
      //       if (state.sort) {
      //         this.selectedSort = state.sort;
      //       }
      //       if (state.tags) {
      //         this.allTags = selectFromState(this.allTags, state.tags);
      //       }
      //       if (state.selectedGroup) {
      //         this.selectedGroup = state.selectedGroup;
      //       }
      //     }
      //     this.loading = false;
      //   });
    },
    setVisibleTooltip(target) {
      const elem = document.querySelector(`[data-target="${target}"]`);
      if (elem) {
        const elemRect = elem.getBoundingClientRect();
        this.visibleTooltipTopPos = `${elemRect.bottom + 10}px`;
        this.visibleTooltip = target;
      }
    },
  },
};
</script>

<style lang="scss" scoped>
@import 'parlassets/scss/breakpoints';
@import 'parlassets/scss/colors';

.groups {
  display: flex;
  flex-wrap: wrap;
  justify-content: space-between;
  margin-bottom: 16px;

  .striped-button {
    width: calc(33.33% - 3.33px);
    margin-bottom: 5px;

    @include respond-to(desktop) {
      flex: 1;
      margin-bottom: 0;

      &:not(:first-child) {
        margin-left: 5px;
      }
    }
  }
}

.filters {
  $label-height: 26px;

  display: flex;
  justify-content: space-between;
  margin-bottom: 20px;

  @include respond-to(mobile) {
    flex-wrap: wrap;
    min-height: 154px;
  }

  .filter-label {
    font-size: 14px;
    font-weight: 300;
    line-height: $label-height;
  }

  .text-filter {
    width: 100%;

    @include respond-to(desktop) {
      width: 26%;
    }
  }

  .tag-dropdown {
    width: 100%;

    @include respond-to(desktop) {
      width: 26%;
    }
  }

  .type-dropdown {
    width: 100%;

    @include respond-to(desktop) {
      width: 17.5%;
    }
  }
}

.results {
  height: 447px;
  overflow-y: auto;

  &.is-loading {
    overflow-y: hidden;
    position: relative;
    &::before {
      background: $white url('#{get-parlassets-url()}/img/loader.gif') no-repeat
        center center;
      content: '';
      height: 100%;
      position: absolute;
      width: 100%;
      z-index: 1;
    }
  }
}

.date-row {
  &:not(:first-child) {
    margin-top: 20px;
  }
}

.ballot {
  $section-border: 1px solid $font-placeholder;
  background: $background;
  color: $font-default;
  display: block;
  margin: 7px 0 8px 0;
  min-height: 90px;
  padding: 10px 14px;
  position: relative;

  &:hover,
  &:active,
  &:focus {
    text-decoration: none;
    background: $link-hover-background;
    color: $link;
  }

  @include respond-to(desktop) {
    display: flex;
    margin: 10px 0;
    &:first-child {
      margin-top: 0;
    }
  }

  .disunion {
    display: flex;
    justify-content: center;
    text-align: center;

    @include respond-to(desktop) {
      flex-direction: column;
      padding-right: 16px;
    }

    .percentage {
      font-size: 24px;

      @include respond-to(desktop) {
        font-size: 30px;
      }
    }

    .text {
      font-size: 13px;
      line-height: 34px;
      margin-left: 10px;
      text-transform: uppercase;

      @include respond-to(desktop) {
        font-size: 16px;
        line-height: 23px;
        margin-left: 0;
      }
    }
  }

  .name {
    border-bottom: $section-border;
    border-top: $section-border;
    font-family: 'Roboto Slab', 'Times New Roman', serif;
    font-size: 11px;
    font-weight: 300;
    line-height: 1.45em;
    padding: 10px 0;

    @include respond-to(desktop) {
      border-bottom: none;
      border-top: none;
      border-left: $section-border;
      display: flex;
      flex: 4;
      font-size: 14px;
      padding: 5px 20px;
      flex-direction: column;
      justify-content: center;
    }

    .projects {
      font-family: Roboto, sans-serif;
      font-size: 12px;
      line-height: 1.2;
      font-weight: 600;
      text-transform: uppercase;

      .project--has-tooltip {
        cursor: help;
      }

      .project--tooltip {
        color: $font-default;
        text-decoration: none;
        cursor: help;

        &::after {
          content: ', ';
        }

        &:first-of-type::before {
          content: '(';
          margin-left: 0.25em;
        }

        &:last-of-type::after {
          content: ')';
        }

        span {
          text-decoration: underline;

          &:hover {
            text-decoration: none;
          }
        }
      }
    }
  }

  .result {
    align-items: center;
    display: flex;
    justify-content: center;
    padding: 10px 0 0 0;

    @include respond-to(desktop) {
      border-left: $section-border;
      justify-content: left;
      padding: 0 0 0 16px;
      width: 136px;
    }

    .glyphicon {
      font-size: 24px;
      margin-bottom: 4px;

      &.accepted {
        color: $icon-accepted;
      }

      &.not-accepted {
        color: $icon-rejected;
      }

      @include respond-to(desktop) {
        font-size: 29px;
      }
    }

    .text {
      color: $font-default;
      font-size: 14px;
      font-weight: bold;
      text-transform: uppercase;
      margin-left: 12px;
    }
  }
}

.tooltip {
  position: fixed;
  background-color: $font-default;
  color: #fff;
  top: 45%;
  font-family: Roboto;
  padding: 3px 10px;
  border-radius: 3px;
  text-transform: uppercase;
  max-width: 90%;
  left: 50%;
  transform: translateX(-50%);
  pointer-events: none;
  visibility: hidden;

  &.tooltip--show {
    opacity: 1;
    visibility: visible;
  }
}

@media (max-width: 767px) {
  .tooltip {
    max-width: 100%;
    width: 90%;
  }
}
</style>
