<template>
  <div :id="speech.id" :class="['speech-holder', { 'just-quote': showQuote }]">
    <div class="person-session">
      <div class="person">
        <template v-if="getPersonLink(speech.person)">
          <a :href="getPersonLink(speech.person)">
            <img
              :src="getPersonPortrait(speech.person)"
              class="portrait"
              :style="{ border: getPersonBorder(speech.person) }"
            />
          </a>
          <a :href="getPersonLink(speech.person)" class="funblue-light-hover">
            <span class="name">{{ getPersonName(speech.person) }}</span>
          </a>
        </template>
        <template v-else>
          <img
            :src="getPersonPortrait(speech.person)"
            class="portrait"
            :style="{ border: getPersonBorder(speech.person) }"
          />
          <span class="name">{{ getPersonName(speech.person) }}</span>
        </template>
      </div>
      <div v-if="showSession" class="session">
        <a
          :href="getSessionTranscriptLink(session)"
          class="funblue-light-hover"
          >{{ getSessionName(session) }}</a
        ><br />
        <span class="date">{{ formatDate(speech.start_time) }}</span>
      </div>
    </div>
    <div class="everything">
      <div class="speech-text">
        <template v-if="showParagraphs">
          <p v-for="paragraph in speechParagraphs" :key="paragraph">
            {{ paragraph }}
          </p>
        </template>
        <template v-else>
          <p>{{ speechContent }}</p>
        </template>
        <div class="quote-button"></div>
      </div>
      <div v-if="speech.votes?.length" class="votes">
        <div v-for="vote in speech.votes" :key="vote.id" class="vote">
          <div class="title-col">
            <div class="vote-title">
              {{ vote.title }}
            </div>
            <div class="vote-link">
              <a :href="getVoteLink(vote, session)" class="funblue-light-hover">
                {{ $t('vote-roll-results') }} >>>
              </a>
            </div>
          </div>
          <div class="result-col">
            <!-- <result
              :score="vote.result?.max_option_percentage"
              :option="vote.result?.max_option"
              :chart-data="mapVotes(vote.votes)"
            /> -->
            <template v-if="vote.result?.passed === true">
              <i class="accepted glyphicon glyphicon-ok"></i>
              <div v-t="'vote-passed'" class="text"></div>
            </template>
            <template v-else-if="vote.result?.passed === false">
              <i class="not-accepted glyphicon glyphicon-remove"></i>
              <div v-t="'vote-not-passed'" class="text"></div>
            </template>
            <template v-else>
              <i class="glyphicon parlaicon-unknown"></i>
              <div v-t="'vote-unknown'" class="text"></div>
            </template>
          </div>
        </div>
      </div>
    </div>
    <div v-if="showQuote" class="quote">
      <div class="speech-text">
        {{ quoteParts.pre
        }}<span class="quote-text">{{ quoteParts.quote }}</span
        >{{ quoteParts.post }}
      </div>
      <div class="full-text-link">
        <a
          v-t="'full-speech'"
          href="#"
          class="funblue-light-hover"
          @click="showFullSpeech"
        ></a>
      </div>
      <div class="quote-button"></div>
    </div>
    <div class="links">
      <a
        :href="getSpeechLink(speech, session)"
        class="link"
        :title="$t('speech-link')"
      ></a>
      <a
        v-if="!showSession"
        :href="getSpeechCardLink(speech)"
        class="share"
        :title="$t('speech-card-link')"
      ></a>
    </div>
  </div>
</template>

<script>
import links from '@/_mixins/links.js';
import { QUOTE_PADDING_LENGTH } from '@/_helpers/constants.js';
import mapVotes from '@/_helpers/mapVotes.js';
import sessionName from '@/_helpers/sessionName.js';
import dateFormatter from '@/_helpers/dateFormatter.js';

export default {
  name: 'Speech',
  mixins: [links],
  props: {
    quote: {
      type: Object,
      default: null,
    },
    speech: {
      type: Object,
      required: true,
    },
    session: {
      type: Object,
      required: true,
    },
    showSession: {
      type: Boolean,
      default: false,
    },
    showParagraphs: {
      type: Boolean,
      default: true,
    },
  },
  data() {
    return {
      hideQuote: false,
    };
  },
  computed: {
    showQuote() {
      return this.quote?.quote_content && !this.hideQuote;
    },
    quoteParts() {
      const text = this.speechContent;
      const quote = this.quote?.quote_content || '';

      let pre = text.slice(0, this.quote.start_index);
      if (pre.length > QUOTE_PADDING_LENGTH) {
        pre = `... ${pre.slice(-QUOTE_PADDING_LENGTH)}`;
      }

      let post = text.slice(this.quote.end_index);
      if (post.length > QUOTE_PADDING_LENGTH) {
        post = `${post.slice(0, QUOTE_PADDING_LENGTH)} ...`;
      }

      return { pre, quote, post };
    },
    speechContent() {
      return this.showParagraphs
        ? this.speech?.content || ''
        : this.speech?.content.replace(/\n/g, ' ').replace(/\r/g, ' ') || '';
    },
    speechParagraphs() {
      return this.speechContent.split('\n');
    },
  },
  methods: {
    showFullSpeech(event) {
      event.preventDefault();
      this.hideQuote = true;
    },
    getSessionName(session) {
      return sessionName(session, this.$t);
    },
    formatDate(date) {
      return dateFormatter(date, this.$t('missing-date'));
    },
    mapVotes,
  },
};
</script>

<style lang="scss" scoped>
@use 'sass:math';
@use 'sass:string';
@use 'parlassets/scss/breakpoints';
@use 'parlassets/scss/colors';

@function icon-link($color) {
  @return 'data:image/svg+xml;utf8,<svg fill="%23#{string.slice("#{$color}", 2)}" xmlns="http://www.w3.org/2000/svg" height="50.456" width="50.45" viewBox="0 0 50.449501 50.456001"><path d="M16.712 45.482a5.394 5.394 0 0 1-7.62 0l-4.12-4.122a5.393 5.393 0 0 1 0-7.618l6.775-6.775-2.404-2.404-6.775 6.776c-3.424 3.426-3.424 9 0 12.425l4.12 4.123a8.766 8.766 0 0 0 6.216 2.568c2.25 0 4.5-.857 6.213-2.57l13.55-13.55a8.72 8.72 0 0 0 2.575-6.214 8.73 8.73 0 0 0-2.574-6.213l-4.123-4.12-2.404 2.403 4.124 4.12a5.352 5.352 0 0 1 1.578 3.81c0 1.438-.56 2.79-1.578 3.808L16.712 45.483z"/><path d="M43.76 2.575A8.728 8.728 0 0 0 37.545 0h-.002a8.73 8.73 0 0 0-6.213 2.574l-13.548 13.55a8.725 8.725 0 0 0-2.576 6.214 8.73 8.73 0 0 0 2.574 6.215l4.12 4.12 2.405-2.403-4.12-4.12a5.357 5.357 0 0 1-1.58-3.812c0-1.438.562-2.79 1.58-3.81l13.55-13.55a5.348 5.348 0 0 1 3.81-1.578c1.44 0 2.792.56 3.81 1.578l4.12 4.12c2.1 2.1 2.1 5.52 0 7.618l-6.774 6.777 2.405 2.404 6.775-6.777c3.426-3.427 3.426-9 0-12.426l-4.12-4.12z"/></svg>';
}

@function icon-share($color) {
  @return 'data:image/svg+xml;utf8,<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 57.17 43.78"><path fill="none" stroke="%23#{string.slice("#{$color}", 2)}" stroke-width="3" d="M1 1h55.17v41.78H1zm0 31.89h55.17M7.33 7.94zm0 6zm0 6zm0 6z"/><circle fill="%23#{string.slice("#{$color}", 2)}" cx="51.08" cy="38.02" r="1.74"/><circle fill="%23#{string.slice("#{$color}", 2)}" cx="46.08" cy="38.02" r="1.74"/><circle fill="%23#{string.slice("#{$color}", 2)}" cx="41.08" cy="38.02" r="1.74"/></svg>';
}

.person-session {
  $portrait-size: 34px;
  $portrait-margin: 14px;
  display: flex;
  height: 86px;
  justify-content: space-between;

  @include breakpoints.respond-to(desktop) {
    flex-direction: column;
    flex-wrap: wrap;
    height: auto;
    justify-content: flex-start;
    width: 220px;
  }

  .person {
    align-items: center;
    display: flex;

    @include breakpoints.respond-to(desktop) {
      width: 100%;
    }

    .portrait {
      border-radius: 50%;
      box-shadow: 0 0 4px colors.$font-placeholder;
      height: $portrait-size;
      width: $portrait-size;
      margin-right: $portrait-margin;
    }

    .name {
      font-size: 16px;
      font-weight: 300;
    }
  }

  .session {
    font-size: 14px;
    line-height: 22px;
    padding: 21px 0 0 8px;

    @include breakpoints.respond-to(desktop) {
      padding: 7px 0 0 $portrait-size + $portrait-margin;
      width: 100%;
    }

    .date {
      display: inline-block;
      margin-top: 4px;
      font-family: Roboto Slab;
    }
  }
}

.speech-text {
  margin: 0;
  padding: 0;
  position: relative;
  font-size: 14px;
  font-weight: 300;
  line-height: 28px;
  white-space: pre-line;

  @include breakpoints.respond-to(desktop) {
    font-size: 16px;
  }
}

.quote-button {
  background: colors.$first;
  border-radius: 50%;
  color: colors.$white;
  cursor: pointer;
  display: none;
  font-family: 'Times New Roman', serif;
  font-size: 44px;
  height: 33px;
  left: -42px;
  line-height: 52px;
  margin-top: -16px;
  position: absolute;
  text-align: center;
  user-select: none;
  width: 33px;

  &::before {
    content: '“';
  }

  @include breakpoints.respond-to(mobile) {
    display: none !important;
  }
}

.links {
  display: flex;
  padding: 6px 0 16px 0;

  @include breakpoints.respond-to(desktop) {
    justify-content: flex-end;
    padding: 0;
    width: 110px;
  }

  .link,
  .share {
    background-position: center center;
    background-repeat: no-repeat;
    background-size: 17px 17px;
    border-radius: 50%;
    height: 30px;
    width: 30px;
    display: block;
    color: colors.$link;

    &:not(:first-child) {
      margin-left: 9px;
    }

    &:hover {
      background-color: colors.$link-hover-background;
      cursor: pointer;
    }
  }

  .link {
    background-image: url('#{icon-link(colors.$link)}');

    &:hover {
      background-image: url('#{icon-link(colors.$link)}');
    }
  }

  .share {
    background-image: url('#{icon-share(colors.$link)}');

    &:hover {
      background-image: url('#{icon-share(colors.$link)}');
    }
  }
}

.speech-holder {
  padding-left: 16px;
  padding-right: 16px;
  margin-left: -16px;
  margin-right: -16px;

  .everything,
  .quote {
    flex: 1;

    @include breakpoints.respond-to(desktop) {
      padding: 2px 8px 0 8px;
    }
  }

  .everything {
    display: block;

    .votes {
      margin-top: 20px;

      .vote {
        display: flex;
        padding: 10px 14px;
        margin-bottom: 10px;
        background-color: colors.$link-hover-background;

        .title-col {
          flex: 1;
          padding-right: 14px;
          border-right: 1px solid colors.$font-placeholder;
          margin-right: 14px;
          display: flex;
          flex-direction: column;
          justify-content: space-between;

          .vote-title {
            font-weight: 300;
          }

          .vote-link {
            font-size: 12px;
            margin-top: 7px;
          }
        }

        .result-col {
          display: flex;

          :deep(.donut-chart) {
            margin: 0;
            width: 42px;
            height: 42px;
            background-size: 30px 30px;
          }

          :deep(.text-container) {
            margin: 0 0 0 14px;
            width: 66px;

            .percentage {
              font-size: 24px;
              line-height: 1.1;
            }

            .text {
              font-size: 14px;
              line-height: 1.1;
              margin-top: 4px;
            }
          }

          flex-direction: column;
          flex: 0 0 80px;
          align-items: center;
          justify-content: center;

          .glyphicon {
            font-size: 21px;

            &.accepted {
              color: colors.$icon-accepted;
            }

            &.not-accepted {
              color: colors.$icon-rejected;
            }
          }

          .parlaicon-unknown {
            &::before {
              content: '?';
              font-family: sans-serif;
              font-size: 1.2em;
              font-weight: 700;
            }
          }

          .text {
            color: colors.$font-default;
            font-size: 12px;
            font-weight: bold;
            text-transform: uppercase;
            margin-top: 8px;
          }
        }
      }
    }
  }

  .quote {
    display: none;
    position: relative;
  }

  &.just-quote {
    .quote-button {
      background: colors.$font-placeholder;
      cursor: default;
      display: block;
      top: 50%;
    }

    .speech-text {
      color: colors.$font-placeholder;

      .quote-text {
        color: #000;
      }
    }

    .full-text-link {
      $width: 180px;
      bottom: -36px;
      left: calc(50% - #{math.div($width, 2)});
      position: absolute;
      width: $width;
      text-align: center;
      text-transform: uppercase;
    }

    .everything {
      display: none;
    }

    .quote {
      display: block;
    }
  }

  @include breakpoints.respond-to(desktop) {
    display: flex;
    padding-top: 15px;
    padding-bottom: 57px;
  }
}
</style>
