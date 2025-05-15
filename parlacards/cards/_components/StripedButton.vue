<template>
  <div
    :class="className"
    @mouseenter="onMouseEnter"
    @mouseleave="onMouseLeave"
    @click="onClick"
  >
    <div class="stripe"></div>
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
@use 'sass:color';
@use 'sass:map';
@use 'parlassets/scss/functions';
@use 'parlassets/scss/colors';
@use 'parlassets/scss/breakpoints';

.striped-button {
  $stripe-height: 6px;

  align-items: center;
  background: colors.$white;
  border: 1px solid colors.$font-default;
  cursor: default;
  display: flex;
  height: 40px;
  justify-content: center;
  gap: 4px;
  position: relative;
  text-align: center;
  user-select: none;
  padding-top: $stripe-height;
  padding-inline: 8px;
  line-height: 1;

  &.is-selected,
  &.is-hovered:not(.is-disabled) {
    color: colors.$white;
  }

  &:not(.is-disabled) {
    cursor: pointer;
  }

  .stripe {
    position: absolute;
    top: 0;
    left: 0;
    right: 0;
    height: $stripe-height;
    border-bottom: 1px solid colors.$font-default;
  }

  .small-text {
    font-size: 10px;
    line-height: 1;

    @include breakpoints.respond-to(desktop) {
      font-size: 12px;
    }

    &.is-uppercase {
      text-transform: uppercase;
    }
  }

  .text {
    font-size: 20px;
    line-height: 1;
    margin-top: -0.05em;

    @include breakpoints.respond-to(desktop) {
      font-size: 20px;
    }
  }

  $all-colors: map.merge(
    colors.$proper-vote-colors,
    colors.$binary-vote-colors
  );
  $all-colors: map.merge($all-colors, colors.$vote-results-colors);
  $all-colors-hover: map.merge(
    colors.$proper-vote-colors-hover,
    colors.$binary-vote-colors-hover
  );
  $all-colors-hover: map.merge(
    $all-colors-hover,
    colors.$vote-results-colors-hover
  );

  @each $name, $color in $all-colors {
    &.#{$name} {
      &.is-selected {
        $selected-color: map.get($all-colors-hover, $name);
        background-color: $selected-color;
        color: functions.choose-contrast-color(
          $selected-color,
          colors.$white,
          colors.$font-default
        );
      }

      &.is-hovered:not(.is-disabled) {
        $hover-color: color.mix($color, colors.$white, 20%);
        background-color: $hover-color;
        color: functions.choose-contrast-color(
          $hover-color,
          colors.$white,
          colors.$font-default
        );
      }

      .stripe {
        background: $color;
      }
    }
  }
}
</style>
