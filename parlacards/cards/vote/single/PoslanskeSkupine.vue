<template>
  <scroll-shadow ref="shadow">
    <div class="parties" @scroll="$refs.shadow.check($event.currentTarget)">
      <div
        v-for="(party, key) in sortedParties"
        :key="party.group?.slug || key"
        class="party"
      >
        <div class="description">
          <div class="name">
            <template v-if="getPartyLink(party.group)">
              <a :href="getPartyLink(party.group)" class="funblue-light-hover">
                {{ partyName(party) }}
              </a>
            </template>
            <template v-else>
              {{ partyName(party) }}
            </template>
          </div>
          <result
            :score="party.max.max_option_percentage"
            :option="party.max.max_option"
            :chart-data="mapVotes(party.votes)"
          />
          <div class="votes">
            <striped-button
              v-for="vote in votes"
              :key="vote.id"
              :class="{
                'lightning-badge':
                  party.outliers && party.outliers.indexOf(vote.id) > -1,
              }"
              :color="vote.id.replace(/ /g, '-')"
              :selected="
                slugOrGovSide(party) === expandedParty &&
                vote.id === expandedOption
              "
              :small-text="vote.label"
              :text="String(party.votes[vote.id])"
              :disabled="party.votes[vote.id] === 0"
              @click="expandVote(party, vote.id)"
            />
          </div>
        </div>
        <div v-if="slugOrGovSide(party) === expandedParty" class="members">
          <ul class="person-list">
            <li
              v-for="member in expandedMembers"
              :key="member.person.id"
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
            </li>
          </ul>
        </div>
      </div>
    </div>
  </scroll-shadow>
</template>

<script>
import links from '@/_mixins/links.js';
import StripedButton from '@/_components/StripedButton.vue';
import Result from '@/_components/Result.vue';
import ScrollShadow from '@/_components/ScrollShadow.vue';
import mapVotes from '@/_helpers/mapVotes.js';

export default {
  name: 'GlasovanjeSejePoslanskeSkupine',
  components: {
    StripedButton,
    Result,
    ScrollShadow,
  },
  mixins: [links],
  props: {
    members: {
      type: Array,
      default: () => [],
    },
    parties: {
      type: Array,
      default: () => [],
    },
    state: {
      type: Object,
      default: () => ({}),
    },
    selectedParty: {
      type: [String, Number],
      default: null,
    },
    selectedOption: {
      type: String,
      default: null,
    },
    didNotVotePresent: {
      type: Boolean,
      default: false,
    },
  },
  emits: ['selectedparty', 'selectedoption'],
  data() {
    const selectableBallotOptions = [
      { id: 'for', label: this.$t('vote-for') },
      { id: 'against', label: this.$t('vote-against') },
      { id: 'abstain', label: this.$t('vote-abstain-plural') },
      { id: 'absent', label: this.$t('vote-absent-plural') },
      { id: 'did not vote', label: this.$t('vote-did-not-vote-plural') },
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
      votes: filteredBallotOptions,
      expandedParty: null,
      expandedOption: null,
    };
  },
  computed: {
    sortedParties() {
      const includesCoalition = this.parties
        .map((party) => party?.group?.name)
        .includes('coalition');

      // if we have coalition, sort alphabetically (coalition on top)
      if (includesCoalition) {
        return this.parties.slice().sort((a, b) => {
          const aValue = a?.group?.name || '';
          const bValue = b?.group?.name || '';
          return aValue.localeCompare(bValue, 'sl');
        });
      }

      // otherwise sort by total number of votes
      return this.parties.slice().sort((a, b) => {
        return this.votesSum(b.votes) - this.votesSum(a.votes);
      });
    },
    expandedMembers() {
      const sortedMembers = this.members.slice().sort((a, b) => {
        const aValue = a?.person?.name || '';
        const bValue = b?.person?.name || '';
        return aValue.localeCompare(bValue, 'sl');
      });
      const optionMembers = sortedMembers.filter(
        (member) => member.option === this.expandedOption,
      );
      if (['coalition', 'opposition'].includes(this.expandedParty)) {
        const expandedCoalition = this.expandedParty === 'coalition';
        return optionMembers.filter((member) => {
          // explicitly cast to boolean for equality check in case of undefined
          const memberCoalition = Boolean(member.person.group?.is_in_coalition);
          return memberCoalition === expandedCoalition;
        });
      }
      return optionMembers.filter(
        (member) => member.person.group?.slug === this.expandedParty,
      );
    },
  },
  mounted() {
    this.expandedParty = this.selectedParty;
    this.expandedOption = this.selectedOption;
  },
  methods: {
    mapVotes,
    votesSum(votes) {
      const voteKeys = Object.keys(votes);
      return voteKeys.reduce((sum, vote) => sum + votes[vote], 0);
    },
    partyName(party) {
      if (['coalition', 'opposition'].includes(party.group?.name)) {
        return this.$t(party.group.name);
      }
      return party.group?.acronym || party.group?.name || 'N/A';
    },
    slugOrGovSide(party) {
      if (party?.group?.slug) {
        return party?.group?.slug;
      }
      if (['coalition', 'opposition'].includes(party?.group?.name)) {
        return party?.group?.name;
      }
      return null;
    },
    expandVote(party, option) {
      if (party.votes[option] === 0) {
        return;
      }

      const slug = this.slugOrGovSide(party);
      if (this.expandedParty === slug && this.expandedOption === option) {
        this.expandedParty = null;
        this.expandedOption = null;
      } else {
        this.expandedParty = slug;
        this.expandedOption = option;
      }

      this.$emit('selectedparty', this.expandedParty);
      this.$emit('selectedoption', this.expandedOption);
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
@use 'parlassets/scss/colors';
@use 'parlassets/scss/breakpoints';

.parties {
  height: 453px;
  margin-top: 13px;
  overflow-y: auto;
}

.party {
  background: colors.$background;
  margin-bottom: 12px;
  padding: 10px 18px 14px;

  @include breakpoints.respond-to(desktop) {
    padding-bottom: 0;
    padding-top: 0;
  }
}

.description {
  align-items: center;
  display: flex;
  flex-wrap: wrap;
  justify-content: space-between;

  @include breakpoints.respond-to(desktop) {
    flex-wrap: nowrap;
    height: 79px;
  }
}

.name {
  font-size: 14px;
  min-width: 94px;

  @include breakpoints.respond-to(desktop) {
    font-size: 18px;
    order: 1;
    font-weight: 300;
    flex: 0.8;
  }
}

.votes {
  display: flex;
  width: 100%;

  @include breakpoints.respond-to(desktop) {
    order: 2;
    width: 400px;
  }

  .striped-button {
    flex: 1;

    &:not(:last-child) {
      margin-right: 6px;
    }
  }
}

.result-chart {
  flex: 1.2;

  @include breakpoints.respond-to(desktop) {
    max-width: 300px;
    order: 3;
    justify-content: center;
  }

  @include breakpoints.respond-to(mobile) {
    display: flex;
    flex: 0;

    :deep(.donut-chart) {
      display: none;
    }

    :deep(.text-container) {
      display: flex;
      margin-right: 0;
      width: auto;
      white-space: nowrap;

      .text {
        margin-left: 15px;
      }
    }
  }
}

.members {
  padding-top: 14px;

  @include breakpoints.respond-to(desktop) {
    padding-top: 0;
  }

  .person-list {
    .item {
      border-color: colors.$font-placeholder;
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
}
</style>
