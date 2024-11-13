<template>
  <card-wrapper :header-config="headerConfig">
    <div class="errored">
      <div class="icon"></div>
      <empty-state v-if="is404" />
      <template v-else>
        <div v-t="'card-errored'" class="content"></div>
        <pre class="message" v-text="message"></pre>
      </template>
    </div>
  </card-wrapper>
</template>

<script>
import common from '@/_mixins/common.js';
import { defaultHeaderConfig } from '@/_mixins/altHeaders.js';
import EmptyState from '@/_components/EmptyState.vue';

export default {
  name: 'CardMiscError',
  components: {
    EmptyState,
  },
  mixins: [common],
  data() {
    const { cardState } = this.$root.$options.contextData;

    const title = cardState?.title || this.$t('card.title');
    const message = cardState?.error?.message || cardState?.message || '';
    // const height = cardState?.height || 1;

    const is404 = Number(cardState?.error?.statusCode) === 404 || false;
    return {
      title,
      message,
      is404,
      // contentClass: height === 2 ? 'full' : 'half',
      headerConfig: defaultHeaderConfig(this, {
        heading: title,
      }),
    };
  },
  beforeCreate() {
    // const { cardState } = this.$root.$options.contextData;
    // const width = cardState?.width || 1;
    // this.$root.$options.cardData.cardData.big = width === 2;
  },
};
</script>

<style lang="scss" scoped>
.errored {
  display: flex;
  flex-direction: column;
  height: 100%;
  justify-content: center;
  min-height: 180px;

  .icon {
    width: 100%;
    padding-top: 100px;
    background-image: url('#{get-parlassets-url()}/icons/missing-file.svg');
    background-size: 100% 100%;
    background-position: center;
    background-repeat: no-repeat;
  }

  .content {
    font-size: 17px;
    font-family: 'Roboto Slab', 'Times New Roman', Times, serif;
    font-style: italic;
    font-weight: 300;
    line-height: 19px;
    text-align: center;
    width: 100%;
    margin: 10px auto 0;
  }

  .message {
    margin-top: 10px;
    font-size: 10px;
  }
}

:deep(.card-container) {
  &::before,
  .card-footer > * {
    visibility: hidden;
    display: none;
  }
}
</style>
