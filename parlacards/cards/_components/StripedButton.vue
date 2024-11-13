<template>
  <div
    :class="className"
    @mouseenter="onMouseEnter"
    @mouseleave="onMouseLeave"
    @click="onClick"
  >
    <div
      v-if="smallText"
      :class="['small-text', { 'is-uppercase': isUppercase }]"
    >
      {{ smallText }}
    </div>
    <div v-if="text" class="text">{{ text }}</div>
  </div>
</template>

<script>
export default {
  name: 'StripedButton',
  props: {
    selected: {
      type: Boolean,
      default: false,
    },
    smallText: {
      type: String,
      default: '',
    },
    isUppercase: {
      type: Boolean,
      default: true,
    },
    text: {
      type: String,
      default: '',
    },
    color: {
      type: String,
      default: '',
    },
    disabled: {
      type: Boolean,
      default: false,
    },
    stripePosition: {
      type: String,
      default: 'top',
      validator: (value) => ['top', 'bottom'].indexOf(value) > -1,
    },
  },
  data() {
    return {
      hovered: false,
    };
  },
  computed: {
    className() {
      return [
        'striped-button',
        { 'is-disabled': this.disabled },
        { 'is-selected': this.selected },
        { 'is-hovered': this.hovered },
        this.color,
        `has-stripe-on-${this.stripePosition}`,
      ];
    },
  },
  methods: {
    onMouseEnter() {
      this.hovered = true;
    },
    onMouseLeave() {
      this.hovered = false;
    },
    onClick() {
      this.hovered = false;
    },
  },
};
</script>

<style lang="scss" scoped>
@use 'sass:map';
@use 'parlassets/scss/functions';
@use 'parlassets/scss/colors';
@use 'parlassets/scss/breakpoints';

.striped-button {
  align-items: center;
  background: colors.$white;
  border: 1px solid colors.$font-placeholder;
  cursor: default;
  display: flex;
  flex-direction: column;
  height: 51px;
  justify-content: center;
  position: relative;
  text-align: center;
  user-select: none;

  &.has-stripe-on-top {
    border-top-width: 9px;

    &::after {
      content: '';
      display: block;
      position: absolute;
      top: -9px;
      left: -1px;
      right: -1px;
      height: 9px;
    }
  }

  &.has-stripe-on-bottom {
    border-bottom-width: 9px;

    &::after {
      content: '';
      display: block;
      position: absolute;
      bottom: -9px;
      left: -1px;
      right: -1px;
      height: 9px;
    }
  }

  &.is-selected,
  &.is-hovered:not(.is-disabled) {
    border-color: transparent !important;
    color: colors.$white;
  }

  &:not(.is-disabled) {
    cursor: pointer;
  }

  .small-text {
    padding: 0 8px;
    font-size: 10px;
    line-height: 1.2;

    @include breakpoints.respond-to(desktop) {
      font-size: 12px;
    }

    &.is-uppercase {
      text-transform: uppercase;
    }
  }

  .text {
    font-size: 22px;
    line-height: 1;

    @include breakpoints.respond-to(desktop) {
      font-size: 24px;
    }
  }

  $all-colors: map.merge(colors.$proper-vote-colors, colors.$binary-vote-colors);
  $all-colors: map.merge($all-colors, colors.$vote-results-colors);
  $all-colors-hover: map.merge(
    colors.$proper-vote-colors-hover,
    colors.$binary-vote-colors-hover
  );
  $all-colors-hover: map.merge($all-colors-hover, colors.$vote-results-colors-hover);

  @each $name, $color in $all-colors {
    &.#{$name} {
      &.has-stripe-on-top::after,
      &.has-stripe-on-bottom::after {
        background-color: $color;
      }

      &.is-selected {
        background-color: $color;
        color: choose-contrast-color($color, colors.$white, colors.$font-default);
      }

      &.is-hovered:not(.is-disabled) {
        background-color: map.get($all-colors-hover, $name);
        color: choose-contrast-color($color, colors.$white, colors.$font-default);

        &::after {
          background-color: $color;
        }
      }
    }
  }
}
</style>
