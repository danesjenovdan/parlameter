<template>
  <div class="toggle">
    <div
      v-for="(optionLabel, optionValue) in options"
      :key="optionValue"
      :class="['option', { 'is-selected': optionValue === modelValue }]"
      @click="handleClick(optionValue)"
    >
      <div>
        <i class="glyphicon glyphicon-ok"></i>
        <span>{{ optionLabel }}</span>
      </div>
      <div class="width-spacer" aria-hidden="true">
        <i class="glyphicon glyphicon-ok"></i>
        <span>{{ optionLabel }}</span>
      </div>
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
  $height: 40px;

  position: relative;
  display: flex;
  height: $height;
  font-size: 14px;

  .option {
    flex: 1;
    position: relative;
    display: flex;
    flex-direction: column;
    align-items: center;
    justify-content: center;
    padding: 0 9px;
    background: colors.$white;
    border: 1px solid colors.$font-default;
    color: colors.$font-default;
    text-align: center;
    white-space: nowrap;
    cursor: pointer;
    z-index: 1;

    &:not(:last-child) {
      margin-right: -1px;
    }

    .glyphicon {
      display: none;
      margin-right: 6px;
      color: colors.$dropdown-arrow;
    }

    &.is-selected {
      background-color: rgba(colors.$dropdown-arrow, 0.2);
      border-color: colors.$dropdown-arrow;
      font-weight: 500;
      cursor: default;
      z-index: 2;

      .glyphicon {
        display: inline;
      }
    }

    .width-spacer {
      background: red;
      font-weight: 500;
      height: 0;
      visibility: hidden;

      .glyphicon {
        display: inline;
      }
    }
  }
}
</style>
