<template>
  <div>
    <template v-if="hasGenerator && showGenerator">
      <slot name="generator" />
    </template>
    <div :class="['card-container', transitionClass]">
      <card-header :config="headerConfig" :current-back="currentBack" />

      <div
        :class="[
          'card-content',
          { full: !halfHeight && !maxHeight, half: halfHeight },
        ]"
      >
        <card-info v-if="currentBack === 'info'" :info="infoText" />

        <card-embed v-else-if="currentBack === 'embed'" />

        <card-share v-else-if="currentBack === 'share'" />

        <card-previous v-else-if="currentBack === 'previous'" />

        <card-export v-else-if="currentBack === 'export'" />

        <div v-else v-cloak class="card-content-front">
          <slot />
        </div>
      </div>
      <card-footer @toggle-back="toggleBack" />
    </div>
  </div>
</template>

<script>
import { RIPPLE_DURATION } from '@/_helpers/constants.js';
import CardInfo from '@/_components/Card/Info.vue';
import CardEmbed from '@/_components/Card/Embed.vue';
import CardShare from '@/_components/Card/Share.vue';
import CardPrevious from '@/_components/Card/Previous.vue';
import CardExport from '@/_components/Card/Export.vue';
import CardHeader from '@/_components/Card/Header.vue';
import CardFooter from '@/_components/Card/Footer.vue';

export default {
  name: 'CardWrapper',
  components: {
    CardInfo,
    CardEmbed,
    CardShare,
    CardPrevious,
    CardExport,
    CardHeader,
    CardFooter,
  },
  props: {
    headerConfig: {
      type: Object,
      required: true,
    },
    halfHeight: {
      type: Boolean,
      default: false,
    },
    maxHeight: {
      type: Boolean,
      default: false,
    },
  },
  emits: ['back-change'],
  data() {
    const { cardState } = this.$root.$options.contextData;

    return {
      currentBack: null,
      transitionClass: null,
      previousHeight: null,
      hasGenerator: this.$slots.generator?.()?.length,
      showGenerator: cardState?.generator,
      cardInfoKey: cardState?.cardInfoKey,
    };
  },
  computed: {
    infoText() {
      if (this.cardInfoKey && this.$te(this.cardInfoKey)) {
        return this.$t(this.cardInfoKey);
      }
      if (this.$te('card.info')) {
        return this.$t('card.info');
      }
      return '';
    },
  },
  watch: {
    currentBack(newBack) {
      this.$emit('back-change', newBack);
    },
  },
  methods: {
    toggleBack(newBack) {
      const contentElement = this.$el.querySelector('.card-content');

      if (this.currentBack !== newBack) {
        this.transitionClass = ['covered', `clicked-${newBack}`];

        window.setTimeout(() => {
          this.previousHeight = contentElement.offsetHeight;
          contentElement.style.height = `${contentElement.offsetHeight}px`;
          this.currentBack = newBack;
        }, RIPPLE_DURATION / 2);
        window.setTimeout(() => {
          this.transitionClass = null;
        }, RIPPLE_DURATION);
      } else {
        this.transitionClass = ['revealed', `clicked-${newBack}`];

        window.setTimeout(() => {
          this.currentBack = null;
          contentElement.style.height = this.previousHeight;
        }, RIPPLE_DURATION / 2);
        window.setTimeout(() => {
          this.transitionClass = null;
        }, RIPPLE_DURATION);
      }
    },
  },
};
</script>

<style lang="scss" scoped>
@use 'parlassets/scss/colors';

.card-content {
  &__empty {
    height: 40vh;
  }

  &.is-loading {
    overflow-y: hidden;
    position: relative;

    &::before {
      background-color: colors.$white-hover;
      background-image: url('#{get-parlassets-url()}/img/loader.gif');
      background-repeat: no-repeat;
      background-position: center center;
      content: '';
      position: absolute;
      left: 0;
      right: 0;
      top: 0;
      bottom: 0;
      z-index: 1;
    }
  }
}
</style>
