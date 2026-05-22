<template>
  <div class="session_voting">
    <div class="clearfix single_voting">
      <div class="vote-badges">
        <div v-if="vote.is_outlier" class="fire-badge"></div>
        <div v-if="vote.has_outliers" class="lightning-badge"></div>
        <div v-if="!vote.has_named_votes" class="hand-badge"></div>
      </div>
      <a :href="getVoteLink(vote, session)" class="show clearfix">
        <div class="col-md-1 icon-col">
          <div :class="passedClass">
            <p>
              <i :class="passedGlyphClass"></i>
            </p>
          </div>
        </div>
        <div class="col-md-11 border-left">
          <div class="col-md-6">
            <div class="session_title">
              <p>
                {{ vote.title }}
              </p>
            </div>
          </div>
          <div class="col-md-6">
            <div class="session_votes">
              <div
                v-if="votePercentages?.for != null"
                class="progress smallbar"
              >
                <div
                  :style="{ width: votePercentages.for + '%' }"
                  class="progress-bar aye"
                >
                  <span class="sr-only"
                    >{{ votePercentages.for }}% votes for</span
                  >
                </div>
                <div
                  :style="{ width: votePercentages.against + '%' }"
                  class="progress-bar ney"
                >
                  <span class="sr-only"
                    >{{ votePercentages.against }}% votes against</span
                  >
                </div>
                <div
                  :style="{ width: votePercentages.abstain + '%' }"
                  class="progress-bar abstention"
                >
                  <span class="sr-only"
                    >{{ votePercentages.abstain }}% votes abstained</span
                  >
                </div>
                <div
                  :style="{ width: votePercentages.absent + '%' }"
                  class="progress-bar not"
                >
                  <span class="sr-only"
                    >{{ votePercentages.absent }}% not present</span
                  >
                </div>
                <div
                  :style="{ width: votePercentages['did not vote'] + '%' }"
                  class="progress-bar none"
                >
                  <span class="sr-only"
                    >{{ votePercentages['did not vote'] }}% did not vote</span
                  >
                </div>
              </div>
              <div class="row">
                <div
                  v-if="
                    !(voteNumbers['did not vote'] > 0 && voteNumbers?.for === 0)
                  "
                  :class="{
                    'col-xs-2 col-xs-offset-1': numberOfBallotTypes === 5,
                    'col-xs-3': numberOfBallotTypes === 4,
                    'col-xs-4': numberOfBallotTypes === 3,
                    'col-xs-6': numberOfBallotTypes === 2,
                  }"
                >
                  {{ voteNumbers?.for }}
                  <div class="type">{{ $t('vote-for-plural') }}</div>
                  <div class="indicator aye">&nbsp;</div>
                </div>
                <div
                  v-if="
                    !(
                      voteNumbers['did not vote'] > 0 &&
                      voteNumbers?.against === 0
                    )
                  "
                  :class="{
                    'col-xs-2': numberOfBallotTypes === 5,
                    'col-xs-3': numberOfBallotTypes === 4,
                    'col-xs-4': numberOfBallotTypes === 3,
                    'col-xs-6': numberOfBallotTypes === 2,
                  }"
                >
                  {{ voteNumbers?.against }}
                  <div class="type">{{ $t('vote-against-plural') }}</div>
                  <div class="indicator ney">&nbsp;</div>
                </div>
                <div
                  v-if="
                    !(
                      voteNumbers['did not vote'] > 0 &&
                      voteNumbers?.abstain === 0
                    )
                  "
                  :class="{
                    'col-xs-2': numberOfBallotTypes === 5,
                    'col-xs-3': numberOfBallotTypes === 4,
                    'col-xs-4': numberOfBallotTypes === 3,
                    'col-xs-6': numberOfBallotTypes === 2,
                  }"
                >
                  {{ voteNumbers?.abstain }}
                  <div class="type">{{ $t('vote-abstain-plural') }}</div>
                  <div class="indicator abstention">&nbsp;</div>
                </div>
                <div
                  v-if="
                    !(
                      voteNumbers['did not vote'] > 0 &&
                      voteNumbers?.absent === 0
                    )
                  "
                  :class="{
                    'col-xs-2': numberOfBallotTypes === 5,
                    'col-xs-3': numberOfBallotTypes === 4,
                    'col-xs-4': numberOfBallotTypes === 3,
                    'col-xs-6': numberOfBallotTypes === 2,
                  }"
                >
                  {{ voteNumbers?.absent }}
                  <div class="type">{{ $t('vote-absent-plural') }}</div>
                  <div class="indicator not">&nbsp;</div>
                </div>
                <div
                  v-if="voteNumbers['did not vote'] > 0"
                  :class="{
                    'col-xs-2': numberOfBallotTypes === 5,
                    'col-xs-3': numberOfBallotTypes === 4,
                    'col-xs-4': numberOfBallotTypes === 3,
                    'col-xs-6': numberOfBallotTypes === 2,
                  }"
                >
                  {{ voteNumbers['did not vote'] }}
                  <div class="type">{{ $t('vote-did-not-vote-plural') }}</div>
                  <div class="indicator none">&nbsp;</div>
                </div>
              </div>
            </div>
          </div>
        </div>
      </a>
    </div>
  </div>
</template>

<script>
import { sum } from 'lodash-es';
import links from '@/_mixins/links.js';

export default {
  name: 'VoteListItem',
  mixins: [links],
  props: {
    vote: {
      type: Object,
      required: true,
    },
    session: {
      type: Object,
      default: null,
    },
  },
  data() {
    return {};
  },
  computed: {
    passedClass() {
      let className = 'accepted ';
      if (this.vote.passed === true) {
        className += 'aye';
      } else if (this.vote.passed === false) {
        className += 'nay';
      } else {
        className += 'unknown';
      }
      return className;
    },
    passedGlyphClass() {
      let glyphClass = 'glyphicon ';
      if (this.vote.passed === true) {
        glyphClass += 'glyphicon-ok';
      } else if (this.vote.passed === false) {
        glyphClass += 'glyphicon-remove';
      } else {
        glyphClass += 'parlaicon-unknown';
      }
      return glyphClass;
    },
    voteNumbers() {
      // const OPTIONS = ['for', 'against', 'abstain', 'absent'];
      return this.vote.all_votes;
    },
    votePercentages() {
      const keys = Object.keys(this.voteNumbers);
      const voteSum = sum(keys.map((key) => this.voteNumbers?.[key] || 0));

      const percentages = {};
      keys.forEach((key) => {
        const num = this.voteNumbers?.[key] || 0;
        percentages[key] = (num / voteSum) * 100;
      });
      return percentages;
    },
    numberOfBallotTypes() {
      const realNumberOfBallotTypes = Object.values(this.voteNumbers).filter(
        (ballotTypeCount) => {
          return ballotTypeCount > 0;
        },
      ).length;
      return this.voteNumbers['did not vote'] > 0 ? realNumberOfBallotTypes : 4;
    },
  },
};
</script>

<style lang="scss" scoped>
@use 'parlassets/scss/breakpoints';
@use 'parlassets/scss/colors';

.session_voting {
  padding: 0;
  margin: 12px 0;

  &:first-child {
    margin-top: 0;
  }
}

.single_voting {
  position: relative;
  margin-bottom: 0;

  .vote-badges {
    position: absolute;
    top: -8px;
    left: 2px;
    z-index: 2;

    .fire-badge,
    .hand-badge,
    .lightning-badge {
      position: relative;
      display: inline-block;
      height: 31px;
      width: 31px;
      margin-right: 2px;

      &::before {
        position: absolute;
        top: 0;
        left: 0;
        right: auto;
        bottom: auto;
      }
    }
  }

  .session_votes .progress.smallbar {
    height: 15px;
  }

  .session_votes {
    font-size: 30px;
    line-height: 40px;
    margin: 15px 0 10px 0;

    .type {
      font-size: 14px;
      line-height: 20px;
      text-transform: uppercase;

      @include breakpoints.respond-to(mobile) {
        font-size: 10px;
      }
    }
  }

  .accepted {
    line-height: normal;
    height: 95px;

    p {
      position: relative;
      top: 50%;
      -webkit-transform: translateY(-50%);
      -ms-transform: translateY(-50%);
      transform: translateY(-50%);

      margin: 0;
      line-height: 30px;
      margin-top: 6px;
      text-align: center;

      .parlaicon-unknown {
        width: 24px;
        height: 28px;
        background-repeat: no-repeat;
        background-size: contain;
        background-position: center;

        &::before {
          content: '?';
          font-family: sans-serif;
          font-size: 1.2em;
          font-weight: 900;
          color: #333;
        }
      }
    }
  }

  .session_title {
    height: 95px;
    margin: 0;
    display: flex;
    flex-direction: column;
    margin: 3px 0;
    justify-content: center;

    @include breakpoints.respond-to(mobile) {
      margin-top: 15px;
      margin-bottom: 10px;
    }

    p {
      font-size: 14px;
      font-weight: 300;
      line-height: 1.4;
      margin: 6px 0;

      display: -webkit-box;
      -webkit-line-clamp: 4;
      line-clamp: 4;
      -webkit-box-orient: vertical;
      overflow: hidden;
    }
  }

  a:hover {
    background-color: colors.$link-hover-background;
    text-decoration: none;
    color: colors.$link;
  }
}

@media (max-width: 991px) {
  .single_voting .session_title {
    height: 93px;
  }

  .single_voting .accepted {
    height: 60px;
  }

  .border-left {
    border-left: none;
  }

  .single_voting {
    padding-bottom: 15px;

    .icon-col {
      float: left;
      margin-left: 15px;
      margin-right: 15px;
      margin-top: 18px;
    }
  }
}

@media (max-width: 767px) {
  .single_voting .session_title {
    height: 80px;
    margin: 15px 0;

    p {
      max-height: 80px;
      margin: 0;
      overflow: hidden;
    }
  }

  .single_voting .session_votes {
    margin: 15px 0;

    .row {
      font-size: 21px;
    }
  }

  .border-left {
    border-left: none;
    padding-inline: 0;
  }

  .single_voting {
    padding-bottom: 0;

    .icon-col {
      margin-top: 21px;
    }
  }
}
</style>
