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
  background-color: colors.$white;
  border: 1px solid colors.$font-default;
  font-size: 14px;
  height: 40px;
  line-height: 27px;
  outline: none;
  padding: 12px 14px;
  width: 100%;

  &.search-field--has-icon {
    background-image: url('#{get-parlassets-url()}/icons/search.svg');
    background-size: 18px 18px;
    background-repeat: no-repeat;
    background-position: right 9px center;
    padding: 6px 30px 6px 9px;
  }

  &::placeholder {
    color: colors.$font-default-light;
  }
}
</style>
