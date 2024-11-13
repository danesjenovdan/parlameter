<template>
  <input
    :placeholder="placeholder"
    :value="modelValue"
    :class="['search-field', { 'search-field--has-icon': type === 'text' }]"
    :type="type"
    :required="required"
    @input="$emit('update:modelValue', $event.target.value)"
    @keyup.enter="$emit('enter', $event.target.value)"
  />
</template>

<script>
export default {
  name: 'SearchField',
  props: {
    modelValue: {
      type: String,
      default: '',
    },
    placeholder: {
      type: String,
      default: '',
    },
    type: {
      type: String,
      default: 'text',
    },
    required: {
      type: Boolean,
      default: false,
    },
  },
  emits: ['update:modelValue', 'enter'],
};
</script>

<style lang="scss" scoped>
@use 'parlassets/scss/colors';

.search-field {
  border: 1px solid colors.$font-placeholder;
  font-size: 16px;
  height: 51px;
  line-height: 27px;
  outline: none;
  padding: 12px 14px;
  width: 100%;

  &.search-field--has-icon {
    background-image: url('#{get-parlassets-url()}/icons/search.svg');
    background-size: 24px 24px;
    background-repeat: no-repeat;
    background-position: right 9px center;
    padding: 12px 42px 12px 14px;
  }
}
</style>
