<template>
  <nav class="pagination-container">
    <ul class="pagination">
      <li :class="['prev', { disabled: page === 1 }]" :disabled="page === 1">
        <a href="#" aria-label="Previous" @click="pageChange($event, page - 1)">
          <span aria-hidden="true">&laquo;</span>
        </a>
      </li>
      <li
        v-for="pageNum in pagesDisplay"
        :key="pageNum"
        :class="{ active: pageNum === page }"
      >
        <span v-if="pageNum < 0" class="separator">...</span>
        <a v-else href="#" @click="pageChange($event, pageNum)">{{
          pageNum
        }}</a>
      </li>
      <li
        :class="['next', { disabled: page >= pages }]"
        :disabled="page >= pages"
      >
        <a href="#" aria-label="Next" @click="pageChange($event, page + 1)">
          <span aria-hidden="true">&raquo;</span>
        </a>
      </li>
    </ul>
  </nav>
</template>

<script>
import { range } from 'lodash-es';

export default {
  name: 'Pagination',
  props: {
    page: {
      type: Number,
      required: true,
    },
    count: {
      type: Number,
      required: true,
    },
    perPage: {
      type: Number,
      default: 150,
    },
  },
  emits: ['change'],
  computed: {
    pages() {
      return Math.ceil(this.count / this.perPage);
    },
    pagesRange() {
      return range(1, this.pages + 1);
    },
    pagesDisplay() {
      if (this.pages <= 7) {
        return this.pagesRange;
      }
      if (this.page <= 4) {
        return this.pagesRange
          .slice(0, 5)
          .concat([-1])
          .concat(this.pagesRange.slice(-1));
      }
      if (this.pages - this.page < 4) {
        return this.pagesRange
          .slice(0, 1)
          .concat([-1])
          .concat(this.pagesRange.slice(-5));
      }
      return this.pagesRange
        .slice(0, 1)
        .concat([-1])
        .concat(range(this.page - 1, this.page + 2))
        .concat([-2])
        .concat(this.pagesRange.slice(-1));
    },
  },
  methods: {
    pageChange(event, newPage) {
      event.preventDefault();
      if (newPage < 1 || newPage > this.pages) {
        return;
      }
      this.$emit('change', newPage);
    },
  },
};
</script>

<style lang="scss" scoped>
@use 'parlassets/scss/colors';

.pagination-container {
  text-align: center;

  .pagination {
    li {
      a,
      .separator {
        border: none;
        border-radius: 50%;
        padding: 0;
        margin: 0 2px;
        height: 24px;
        width: 24px;
        display: flex;
        justify-content: center;
        align-items: center;
        font-size: 12px;
        background-color: colors.$card-footer-button-hover-background;
        color: colors.$white;
        line-height: 1;
      }

      .separator {
        background-color: transparent;
        color: colors.$font-default;
      }

      &.prev,
      &.next {
        a {
          background-color: transparent;
          color: colors.$link;
          font-size: 28px;
          padding-bottom: 5px;
          font-weight: 300;
          overflow: hidden;
        }
      }

      &.active {
        a,
        a:hover {
          background-color: colors.$card-footer-button-passive-background;
        }
      }

      a:hover {
        background-color: colors.$card-footer-button-passive-background;
        color: colors.$white;
      }

      &.disabled,
      &[disabled] {
        a,
        a:hover {
          background-color: transparent;
          color: colors.$font-default;
        }
      }
    }
  }
}
</style>
