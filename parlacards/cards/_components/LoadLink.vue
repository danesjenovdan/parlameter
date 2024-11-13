<template>
  <span class="load">
    <slot />
  </span>
</template>

<style lang="scss" scoped>
@use 'sass:string';
@use 'parlassets/scss/colors';

@function icon-load($color) {
  @return 'data:image/svg+xml;utf8,<svg fill="%23#{string.slice("#{$color}", 2)}" xmlns="http://www.w3.org/2000/svg" viewBox="-949 951 100 100"><g><path d="M-857.3 1008.7c-3.2 0-5.8 2.6-5.8 5.8v16.5H-935v-16.5c0-3.2-2.6-5.8-5.8-5.8-3.2 0-5.8 2.6-5.8 5.8v22.2c0 3.2 2.6 5.8 5.8 5.8h83.5c3.2 0 5.8-2.6 5.8-5.8v-22.2c0-3.2-2.6-5.8-5.8-5.8z"/><path d="M-903 1020c1.1 1.1 2.6 1.7 4.1 1.7s3-.6 4.1-1.7l17.2-17.2c2.3-2.3 2.3-5.9 0-8.2-2.3-2.3-5.9-2.3-8.2 0l-7.3 7.3v-36.6c0-3.2-2.6-5.8-5.8-5.8s-5.8 2.6-5.8 5.8v36.8l-7.5-7.5c-2.3-2.3-5.9-2.3-8.2 0-2.3 2.3-2.3 5.9 0 8.2l17.4 17.2z"/></g></svg>';
}

.load {
  display: inline-block;
  white-space: nowrap;
  color: colors.$white;
  cursor: pointer;

  font-weight: 400;
  font-size: 14px;
  font-family: 'Roboto';
  line-height: 56px;

  width: 166px;
  height: 56px;
  background-color: colors.$first;

  &:hover {
    background-color: colors.$second;
  }

  &::after {
    content: '';
    display: inline-block;
    background-image: url('#{icon-load(colors.$white)}');
    width: 20px;
    height: 20px;
    position: relative;
    top: 3px;
    margin-left: 5px;
  }
}
</style>
