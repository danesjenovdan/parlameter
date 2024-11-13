<template>
  <div class="text-frame">
    <slot />
  </div>
</template>

<style lang="scss">
@use 'parlassets/scss/colors';

.text-frame {
  text-align: center;
  background-color: colors.$light-background;
  padding: 30px;
  font-family: 'Roboto Slab', serif;
  font-size: 18px;
  line-height: 30px;
  margin-bottom: 10px;
}
</style>
