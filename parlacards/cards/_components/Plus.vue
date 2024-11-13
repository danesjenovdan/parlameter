<template>
  <span class="plus">+</span>
</template>

<style lang="scss">
@use 'parlassets/scss/colors';

.plus {
  background-color: colors.$white;
  padding: 0.2px 7px;
  font-size: 21px;
  line-height: 12px;
  cursor: pointer;
  color: colors.$first;
  position: relative;
  top: 3px;
  font-family: 'Roboto', sans-serif;
  margin-left: 5px;
}
</style>
