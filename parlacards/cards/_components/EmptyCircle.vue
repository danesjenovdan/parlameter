<template>
  <div class="empty">
    <div class="circle">{{ text }}</div>
  </div>
</template>

<script>
export default {
  name: 'EmptyCircle',
  props: {
    text: {
      type: String,
      required: true,
    },
  },
};
</script>

<style scoped lang="scss">
@use 'sass:math';
@use 'parlassets/scss/colors';

.empty {
  bottom: 0;
  left: 0;
  position: absolute;
  right: 0;
  top: 0;

  .circle {
    $size: 220px;
    border-radius: 50%;
    background-image: url('#{get-parlassets-url()}/img/orodja/primerjalnik.svg');
    background-color: colors.$light-background;
    background-size: math.div($size, 2.5);
    background-position: center 40px;
    background-repeat: no-repeat;
    font-size: 17px;
    font-family: 'Roboto Slab', 'Times New Roman', Times, serif;
    font-style: italic;
    font-weight: 300;
    height: $size;
    left: calc(50% - #{math.div($size, 2)});
    line-height: 19px;
    padding: 145px 26px 0;
    position: absolute;
    text-align: center;
    top: calc(50% - #{math.div($size, 2)});
    width: $size;
  }
}
</style>
