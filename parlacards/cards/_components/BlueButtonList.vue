<template>
  <div>
    <ul class="blue-button-list">
      <li
        v-for="item in items"
        :key="item.id"
        :class="[
          'blue-button-list-item',
          { 'is-selected': item.id === modelValue },
        ]"
        @click="$emit('update:modelValue', item.id)"
      >
        {{ item.label }}
      </li>
    </ul>
    <div class="blue-button-list-mobile">
      <div class="select">
        <select @change="changeSelection">
          <option
            v-for="item in items"
            :key="item.id"
            :value="item.id"
            :selected="item.id === modelValue"
          >
            {{ item.label }}
          </option>
        </select>
      </div>
    </div>
  </div>
</template>

<script>
export default {
  props: {
    items: {
      type: Array,
      required: true,
    },
    modelValue: {
      type: String,
      default: '',
    },
  },
  emits: ['update:modelValue'],
  methods: {
    changeSelection(event) {
      this.$emit('update:modelValue', event.target.value);
    },
  },
};
</script>

<style lang="scss" scoped>
@import 'parlassets/scss/breakpoints';
@import 'parlassets/scss/colors';

.blue-button-list {
  list-style: none;
  margin-top: 14px;
  margin-bottom: 0;
  padding: 0;

  @include show-for(desktop, flex);

  &-item {
    align-items: center;
    border-left: 1px solid $font-placeholder;
    box-sizing: border-box;
    color: $link;
    display: flex;
    font-size: 13px;
    line-height: 16px;
    padding: 7px 10px;
    min-height: 46px;

    &:last-child {
      border-right: 1px solid $font-placeholder;
    }

    &:hover,
    &.is-selected {
      border-left-color: transparent;
      border-right-color: transparent;
      background-color: $link-hover-background;
    }

    &:hover {
      cursor: pointer;
    }

    &:hover + &,
    &.is-selected + & {
      border-left-color: transparent;
    }

    &.is-selected {
      &:hover {
        cursor: default;
      }
    }
  }

  &-mobile {
    @include show-for(mobile, block);

    label {
      font-size: 11px;
      width: 100%;
    }

    .select {
      width: 100%;

      select {
        width: 100%;
      }
    }
  }
}
</style>
