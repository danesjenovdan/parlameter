<template>
  <div class="members">
    <div class="filters">
      <search-field v-model="nameFilter" :placeholder="$t('all-mps')" />
      <div class="vote-filters">
        <striped-button
          v-for="vote in votes"
          :key="vote.id.replace(/ /g, '-')"
          :color="vote.id.replace(/ /g, '-')"
          :selected="vote.selected"
          :small-text="vote.label"
          :text="String(allVotes[vote.id])"
          :disabled="allVotes[vote.id] === 0"
          @click="toggleVote(vote.id)"
        />
      </div>
      <result
        :score="result.max_option_percentage"
        :option="result.max_option"
        :chart-data="mapVotes(allVotes)"
      />
    </div>
    <scroll-shadow ref="shadow">
      <ul
        class="person-list"
        @scroll="$refs.shadow.check($event.currentTarget)"
      >
        <li v-if="anonymousVotesPresent" class="item anonymous-votes-exist">
          <img
            :src="`${$root.$options.contextData.urls.cdn}/icons/hand-vote.png`"
          />
          <span>{{ $t('anonymous-votes-present') }}</span>
        </li>
        <empty-state
          v-if="!filteredMembers?.length && !anonymousVotesPresent"
        />
        <template v-else>
          <li
            v-for="member in filteredMembers"
            :key="member.person.slug"
            class="item"
          >
            <div class="column portrait">
              <a :href="getPersonLink(member.person)">
                <img
                  :src="getPersonPortrait(member.person)"
                  :style="{ border: getPersonBorder(member.person) }"
                />
              </a>
            </div>
            <div class="column wider name">
              <div class="person-name">
                <a
                  :href="getPersonLink(member.person)"
                  class="funblue-light-hover"
                >
                  {{ getPersonName(member.person) }}
                </a>
              </div>
              <div class="person-party">
                <a
                  v-if="getPartyLink(member.person?.group)"
                  :href="getPartyLink(member.person?.group)"
                  class="funblue-light-hover"
                >
                  {{
                    member.person?.group?.acronym ||
                    member.person?.group?.name ||
                    'N/A'
                  }}
                </a>
                <span v-else>
                  {{ $t(unaffiliatedKey(member.person)) }}
                </span>
              </div>
            </div>
            <div class="column vote">
              <div :class="['option', optionClassName(member.option)]">
                {{
                  translateOption(
                    member.option,
                    member.person?.preferred_pronoun,
                  )
                }}
              </div>
            </div>
          </li>
        </template>
      </ul>
    </scroll-shadow>
  </div>
</template>

<script>
import StripedButton from '@/_components/StripedButton.vue';
import links from '@/_mixins/links.js';
import SearchField from '@/_components/SearchField.vue';
import Result from '@/_components/Result.vue';
import ScrollShadow from '@/_components/ScrollShadow.vue';
import EmptyState from '@/_components/EmptyState.vue';
import mapVotes from '@/_helpers/mapVotes.js';

export default {
  name: 'GlasovanjeSejePoslanci',
  components: {
    StripedButton,
    SearchField,
    Result,
    ScrollShadow,
    EmptyState,
  },
  mixins: [links],
  props: {
    members: {
      type: Array,
      default: () => [],
    },
    result: {
      type: Object,
      default: () => ({}),
    },
    allVotes: {
      type: Object,
      default: () => ({}),
    },
    state: {
      type: Object,
      default: () => ({}),
    },
    didNotVotePresent: {
      type: Boolean,
      default: false,
    },
    anonymousVotesPresent: {
      type: Boolean,
      default: false,
    },
  },
  emits: ['namefilter'],
  data() {
    const selectableBallotOptions = [
      {
        id: 'for',
        label: this.$t('vote-for'),
        selected: this.getSelectedOption('for'),
      },
      {
        id: 'against',
        label: this.$t('vote-against'),
        selected: this.getSelectedOption('against'),
      },
      {
        id: 'abstain',
        label: this.$t('vote-abstain-plural'),
        selected: this.getSelectedOption('abstain'),
      },
      {
        id: 'absent',
        label: this.$t('vote-absent-plural'),
        selected: this.getSelectedOption('absent'),
      },
      {
        id: 'did not vote',
        label: this.$t('vote-did-not-vote-plural'),
        selected: this.getSelectedOption('did not vote'),
      },
    ];

    const filteredBallotOptions = selectableBallotOptions.filter(
      (ballotOption) => {
        if (this.didNotVotePresent) {
          return ballotOption.id !== 'absent' && ballotOption.id !== 'against';
        }
        return ballotOption.id !== 'did not vote';
      },
    );

    return {
      nameFilter: '',
      columns: [
        { id: 'portrait', label: '', additionalClass: 'portrait' },
        { id: 'name', label: 'Ime', additionalClass: 'wider name' },
        { id: 'party', label: 'PS' },
        { id: 'votes', label: 'Glasovi', additionalClass: 'optional' },
      ],
      votes: filteredBallotOptions,
    };
  },
  computed: {
    selectedVotes() {
      return this.votes.filter((vote) => vote.selected).map((vote) => vote.id);
    },
    filteredMembers() {
      const sortedMembers = this.members.slice().sort((a, b) => {
        const aValue = a?.person?.name || '';
        const bValue = b?.person?.name || '';
        return aValue.localeCompare(bValue, 'sl');
      });
      return sortedMembers.filter((member) => {
        let nameMatch = true;
        let optionMatch = true;

        if (this.nameFilter.length > 0) {
          const namesToMatch = this.nameFilter.split('|');
          nameMatch = namesToMatch.reduce((result, nameToMatch) => {
            if (!result && member.person && member.person.name) {
              return (
                member.person.name
                  .toLowerCase()
                  .indexOf(nameToMatch.toLowerCase()) > -1
              );
            }
            return result;
          }, false);
        }

        if (this.selectedVotes.length > 0) {
          optionMatch = this.selectedVotes.indexOf(member.option) > -1;
        }

        return nameMatch && optionMatch;
      });
    },
  },
  watch: {
    nameFilter(newNameFilter) {
      this.$emit('namefilter', newNameFilter);
    },
  },
  mounted() {
    if (this.state.nameFilter) {
      this.nameFilter = this.state.nameFilter;
    }
  },
  methods: {
    getSelectedOption(option) {
      if (this.state.selectedOption) {
        return this.state.selectedOption === option;
      }
      return false;
    },
    mapVotes,
    translateOption(option, preferredPronoun) {
      const form = preferredPronoun === 'she' ? '--f' : '--m';
      return this.$t(`voted-${(option || '').replace(/ /g, '-')}${form}`);
    },
    optionClassName(option) {
      return `option-${(option || '').replace(/ /g, '-')}`;
    },
    toggleVote(id) {
      if (this.allVotes[id] !== 0) {
        this.votes.forEach((vote) => {
          if (vote.id === id) {
            vote.selected = !vote.selected;
          } else {
            vote.selected = false;
          }
        });
      }
    },
    unaffiliatedKey(person) {
      let suffix = '--f';
      if (person?.preferred_pronoun === 'he') suffix = '--m';
      return `unaffiliated${suffix}`;
    },
  },
};
</script>

<style lang="scss" scoped>
@use 'parlassets/scss/breakpoints';

.filters {
  margin-top: 10px;
  margin-bottom: 10px;

  @include breakpoints.respond-to(desktop) {
    align-items: center;
    display: flex;
  }

  .search-field {
    width: 100%;
    @include breakpoints.respond-to(desktop) {
      flex: 1;
      width: auto;
      // max-width: 200px;
    }
  }

  .vote-filters {
    min-width: 33%; // fix ie
    display: flex;
    margin: 8px 0;
    @include breakpoints.respond-to(desktop) {
      margin: 0 0 0 30px;
    }
    .striped-button {
      flex: 1;
      @include breakpoints.respond-to(desktop) {
        width: 97px;
      }
      &:not(:last-child) {
        margin-right: 6px;
      }
    }
  }

  .result-chart {
    @include breakpoints.show-for(above-limbo, flex);
  }
}

.person-list {
  height: 231px;
  overflow: auto;

  @include breakpoints.respond-to(desktop) {
    height: 453px - 65;
  }

  .person-name,
  .person-party {
    line-height: 1.1;
  }

  .person-name {
    font-weight: 300;
  }

  .person-party {
    font-size: 14px;
    margin-top: 5px;
  }
}

.anonymous-votes-exist {
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 14px;
  font-weight: 700;
  background-color: #eef7f7;
  padding: 20px;

  img {
    height: 36px;
    margin-right: 8px;
  }

  @include breakpoints.respond-to(desktop) {
    height: 97px;
    font-size: 18px;
  }
}

.vote {
  display: flex;
  justify-content: flex-end;
  .option {
    background-size: 40px 40px;
    background-repeat: no-repeat;
    background-position: top center;
    font-size: 11px;
    font-weight: 500;
    padding-top: 40px;
    text-transform: uppercase;
    width: 58px;
    @include breakpoints.respond-to(desktop) {
      width: 125px;
    }

    $icon-path: '#{get-parlassets-url()}/icons';
    &.option-for {
      background-image: url(#{$icon-path}/za_v2.svg);
    }
    &.option-against {
      background-image: url(#{$icon-path}/proti_v2.svg);
    }
    &.option-absent {
      background-image: url(#{$icon-path}/ni_v2.svg);
    }
    &.option-abstain {
      background-image: url(#{$icon-path}/vzdrzan_v2.svg);
    }
    &.option-did-not-vote {
      background-image: url(#{$icon-path}/brez-glasu.svg);
    }
  }
}
</style>
