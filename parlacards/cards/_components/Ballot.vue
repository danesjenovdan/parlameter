<template>
  <a :href="getVoteLink(ballot.vote)" class="ballot">
    <div class="disunion">
      <div :class="['icon', optionClass]"></div>
      <div class="text">
        {{ ballot.label }}
      </div>
    </div>
    <div class="name">
      <p>{{ ballot.vote?.title }}</p>
    </div>
    <div class="outcome">
      <i :class="passedGlyphClass"></i>
      <div class="text">{{ $t(passedTranslationKey) }}</div>
    </div>
  </a>
</template>

<script>
import links from '@/_mixins/links.js';

export default {
  name: 'Ballot',
  mixins: [links],
  props: {
    ballot: {
      type: Object,
      required: true,
    },
    type: {
      type: String,
      default: 'person',
    },
  },
  computed: {
    passedTranslationKey() {
      if (this.ballot.vote.passed === true) {
        return 'vote-passed';
      }
      if (this.ballot.vote.passed === false) {
        return 'vote-not-passed';
      }
      return 'vote-unknown';
    },
    passedGlyphClass() {
      let glyphClass = 'glyphicon ';
      if (this.ballot.vote.passed === true) {
        glyphClass += 'glyphicon-ok';
      } else if (this.ballot.vote.passed === false) {
        glyphClass += 'glyphicon-remove';
      } else {
        glyphClass += 'parlaicon-unknown';
      }
      return glyphClass;
    },
    optionClass() {
      return (this.ballot.option || '').replace(/\s+/g, '-');
    },
  },
};
</script>

<style lang="scss">
@import 'parlassets/scss/breakpoints';
@import 'parlassets/scss/colors';

.ballot {
  text-decoration: none;
  background: $background;
  color: $font-default;
  display: block;
  margin: 7px 0 8px;
  min-height: 90px;
  padding: 10px 14px;
  position: relative;

  @include respond-to(desktop) {
    display: flex;
    margin: 10px 0;
  }

  &:hover {
    text-decoration: none;
    background-color: $link-hover-background;
    color: $link;
  }

  .disunion {
    display: flex;
    flex-direction: column;
    justify-content: center;
    text-align: center;

    @include respond-to(mobile) {
      padding-bottom: 10px;
    }

    @include respond-to(desktop) {
      padding-right: 16px;
    }
  }

  .name {
    border-bottom: 1px solid $font-placeholder;
    border-top: 1px solid $font-placeholder;
    font-family: 'Roboto Slab', 'Times New Roman', serif;
    font-size: 11px;
    font-weight: 300;
    line-height: 1.45em;
    padding: 10px 0;

    @include respond-to(desktop) {
      border-bottom: none;
      border-top: none;
      border-left: 1px solid $font-placeholder;
      align-items: center;
      display: flex;
      flex: 4;
      font-size: 14px;
      padding: 5px 20px;
    }

    p {
      margin: 0;
    }
  }

  .outcome {
    align-items: center;
    display: flex;
    justify-content: center;
    font-size: 13px;
    font-weight: bold;
    line-height: 13px;
    text-align: left;
    text-transform: uppercase;
    padding: 10px 0 0;

    @include respond-to(desktop) {
      border-left: 1px solid $font-placeholder;
      justify-content: left;
      padding: 0 0 0 16px;
      width: 136px;
      margin-right: 16px;
    }

    @include respond-to(mobile) {
      margin: 0 15px;
    }

    .text {
      color: $font-default;
      font-size: 14px;
      font-weight: 700;
      text-transform: uppercase;
      margin-left: 6px;
      margin-top: 2px;
    }

    i {
      background-position: center;
      background-repeat: no-repeat;
      background-size: 28px;
      width: 29px;
      font-size: 25px;
      margin-right: 10px;
      line-height: 34px;

      &.glyphicon {
        font-size: 29px;
        text-align: center;

        &.glyphicon-ok {
          color: $icon-accepted;
        }

        &.glyphicon-remove {
          color: $icon-rejected;
        }

        &.parlaicon-unknown {
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
  }

  .icon {
    background-position: center;
    background-repeat: no-repeat;
    background-size: contain;
    width: 29px;
    padding: 5px 55px;
    padding-top: 30px;
    text-transform: uppercase;
    font-size: 12px;
    display: flex;
    align-items: center;
    height: 42px;

    @include show-for(desktop);

    @include respond-to(mobile) {
      margin: 0 auto;
    }

    &.for {
      background-image: url('#{get-parlassets-url()}/icons/g_za_v2.svg');
    }
    &.against {
      background-image: url('#{get-parlassets-url()}/icons/g_proti_v2.svg');
    }
    &.absent {
      background-image: url('#{get-parlassets-url()}/icons/ni_v2.svg');
    }
    &.abstain {
      background-image: url('#{get-parlassets-url()}/icons/g_vzdrzan_v2.svg');
    }
    &.did-not-vote {
      background-image: url('#{get-parlassets-url()}/icons/brez-glasu.svg');
    }
  }

  .text {
    text-align: center;
    font-size: 11px;
    text-transform: uppercase;
    font-weight: 500;

    @include respond-to(desktop) {
      line-height: 12px;
    }
  }
}
</style>
