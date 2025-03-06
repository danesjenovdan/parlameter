<template>
  <div class="toggle">
    <div
      v-for="(optionLabel, optionValue) in options"
      :key="optionValue"
      :class="['option', { 'is-selected': optionValue === modelValue }]"
      @click="handleClick(optionValue)"
    >
      {{ optionLabel }}
    </div>
  </div>
</template>

<script>
export default {
  name: 'Toggle',
  props: {
    options: {
      type: Object,
      default: () => ({}),
    },
    modelValue: {
      type: [String, Number, Boolean],
      default: '',
    },
  },
  emits: ['update:modelValue'],
  methods: {
    handleClick(newValue) {
      this.$emit('update:modelValue', newValue);
    },
  },
};
</script>

<style lang="scss" scoped>
@use 'parlassets/scss/colors';

.toggle {
  $height: 51px;
  display: flex;
  font-size: 15px;
  height: $height;
  line-height: $height;

  .option {
    align-items: center;
    background: colors.$tab-passive;
    color: colors.$white;
    cursor: pointer;
    flex: 1;
    text-align: center;
    padding: 0 10px;
    white-space: nowrap;

    &:hover {
      background: colors.$tab-hover;
    }

    &.is-selected {
      background: colors.$tab-active;
      color: colors.$white;
      cursor: default;
    }
  }
}
</style>
