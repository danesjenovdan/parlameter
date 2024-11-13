<template>
  <div class="personpin-container">
    <div :class="['personpin-tooltip', { visible: tooltipVisible }]">
      {{ getPersonName(person) }}
    </div>
    <a
      :href="getPersonLink(person)"
      :style="{
        'background-image': `url('${getPersonPortrait(person)}')`,
        border: getPersonBorder(person),
      }"
      class="avgminimg img-circle"
      @mouseover="tooltipVisible = true"
      @mouseout="tooltipVisible = false"
    />
  </div>
</template>

<script>
import links from '@/_mixins/links.js';

export default {
  name: 'PersonPin',
  mixins: [links],
  props: {
    person: {
      type: Object,
      required: true,
    },
  },
  data() {
    return {
      tooltipVisible: false,
    };
  },
};
</script>

<style lang="scss" scoped>
@use 'parlassets/scss/colors';

.personpin-container {
  float: right;
  position: relative;

  width: 30px;
  height: 30px;

  .personpin-tooltip {
    position: absolute;
    top: -30px;
    left: -25px;

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

    min-width: 100px;

    &.visible {
      opacity: 1;
    }
  }
}
</style>
