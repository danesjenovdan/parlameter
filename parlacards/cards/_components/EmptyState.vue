<template>
  <div class="empty">
    <div :class="['circle', icon, { small }]">{{ $t(text) }}</div>
  </div>
</template>

<script>
export default {
  name: 'EmptyState',
  props: {
    icon: {
      type: String,
      default: 'empty-icon',
    },
    text: {
      type: String,
      default: 'no-results',
    },
    small: {
      type: Boolean,
      default: false,
    },
  },
};
</script>

<style scoped lang="scss">
@use 'sass:math';
@use 'parlassets/scss/breakpoints';
@use 'parlassets/scss/colors';

@mixin circle($size: 220px) {
  width: $size;
  height: $size;
  padding: #{math.div($size, 1.6)} #{math.div($size, 8)} 0;
  background-color: colors.$light-background;
  background-size: math.div($size, 3);
  background-position: center #{math.div($size, 5)};
  background-repeat: no-repeat;
  border-radius: 50%;
  font-size: math.div($size, 220px) * 17px;
  font-style: italic;
  line-height: 1.1;
  text-align: center;
  position: absolute;
  top: calc(50% - #{math.div($size, 2)});
  left: calc(50% - #{math.div($size, 2)});
}

.empty {
  position: absolute;
  top: 0;
  left: 0;
  bottom: 0;
  right: 0;

  .circle {
    @include circle;

    &.small {
      @include circle(180px);
    }

    @include breakpoints.respond-to(mobile) {
      &,
      &.small {
        @include circle(150px);
      }
    }
  }
}
</style>
