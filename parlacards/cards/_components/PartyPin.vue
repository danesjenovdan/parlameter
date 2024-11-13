<template>
  <div class="partypin-container">
    <div :class="['partypin-tooltip', { visible: tooltipVisible }]">
      {{ party.name }}
    </div>
    <a
      :href="partyLink"
      class="avgminimg img-circle avgminimg-party img-circle"
      :style="{ 'background-color': party.color }"
      @mouseover="tooltipVisible = true"
      @mouseout="tooltipVisible = false"
    >
      {{ party.acronym ?? party.name }}
    </a>
  </div>
</template>

<script>
import links from '@/_mixins/links.js';

export default {
  name: 'PartyPin',
  mixins: [links],
  props: {
    party: {
      type: Object,
      required: true,
    },
  },
  data() {
    return {
      tooltipVisible: false,
    };
  },
  computed: {
    partyLink() {
      return this.getPartyLink(this.party);
    },
  },
};
</script>

<style lang="scss" scoped>
@use 'parlassets/scss/colors';

.partypin-container {
  float: right;
  position: relative;
  width: 30px;
  height: 30px;

  .avgminimg-party {
    line-height: 27px;
    cursor: pointer;
    font-size: 10px;
    color: colors.$white;
    background-color: colors.$font-default;
    overflow: hidden;
  }

  .partypin-tooltip {
    position: absolute;
    bottom: 35px;
    right: -50px;

    text-align: center;
    border: 0px;
    pointer-events: none;
    background-color: colors.$font-default;
    border-radius: 3px;
    padding: 2px 10px;
    opacity: 0;

    color: colors.$white;

    transition: opacity 0.25s ease-out;

    z-index: 10;

    min-width: 170px;

    &.visible {
      opacity: 1;
    }
  }
}
</style>
