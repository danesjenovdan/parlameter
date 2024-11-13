<template>
  <global-search />
</template>

<script>
import GlobalSearch from '@/_components/GlobalSearch.vue';

export default {
  name: 'CardMiscMenuSearch',
  components: {
    GlobalSearch,
  },
};
</script>

<style lang="scss" scoped>
:deep(.search-dropdown) {
  // this is intentionally doubled to raise specificity of this rule
  &.search-dropdown {
    border: none;
    padding-left: 20px;

    .search-dropdown-input {
      background-color: transparent;
    }

    &::after {
      right: auto;
      left: 0;
    }
  }
}

:deep(.card-container) {
  margin-top: 0;

  .card-content {
    padding-top: 0;
    padding-bottom: 0;
    min-height: auto;
  }
}
</style>
