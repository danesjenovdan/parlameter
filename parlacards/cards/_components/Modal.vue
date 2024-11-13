<template>
  <div class="card-modal">
    <div class="card-modal-header">
      {{ header }}
      <div class="closeme" @click="$emit('close')" />
    </div>
    <div class="card-modal-content">
      <slot />
      <div v-if="showButton" class="card-modal-button" @click="$emit('ok')">
        {{ button }}
      </div>
    </div>
  </div>
</template>

<script>
export default {
  name: 'Modal',
  props: {
    header: {
      type: String,
      required: true,
    },
    button: {
      type: String,
      default: 'OK',
    },
    showButton: {
      type: Boolean,
      default: true,
    },
  },
  emits: ['close', 'ok'],
};
</script>

<style lang="scss" scoped>
@use 'parlassets/scss/colors';
@use 'parlassets/scss/helper';

.card-modal {
  position: absolute;
  width: 90%;
  max-width: 360px;
  left: 50%;
  transform: translateX(-50%);
  top: 40px;
  z-index: 100;
  background-color: colors.$background;

  @include helper.card(2);

  &-button {
    width: 100%;
    line-height: 40px;
    font-size: 16px;
    color: colors.$white;
    background-color: colors.$first;
    text-align: center;
    margin-top: 10px;
    cursor: pointer;
    text-transform: uppercase;

    &:hover {
      opacity: 0.7;
    }
  }

  &-header {
    width: 100%;
    background-color: colors.$first;
    color: colors.$white;
    font-family: 'Roboto Slab', serif;
    padding: 10px 50px 10px 10px;
    position: relative;

    .closeme {
      display: block;
      position: absolute;
      right: 10px;
      top: calc(50% - 2px);
      transform: translateY(-50%);
      font-size: 40px;
      cursor: pointer;

      &::before {
        content: '×';
      }
    }
  }

  &-content {
    padding: 10px;
  }
}
</style>
