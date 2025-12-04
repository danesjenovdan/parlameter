<template>
  <div v-if="!items?.length" class="empty-container">
    <empty-state />
  </div>
  <ul v-else>
    <li v-if="sortCallback != null" class="headers">
      <template v-for="column in columns">
        <div
          v-if="column.label"
          :key="column.id"
          :class="getColumnClasses(column)"
          @click="sortCallback(column.id)"
        >
          <span>{{ column.label }}</span>
        </div>
      </template>
    </li>
    <li v-for="(item, k) in items" :key="k" class="item">
      <div
        v-for="(cell, i) in item"
        :key="i"
        :class="getColumnClasses(columns[i], cell)"
      >
        <template v-if="cell && cell.contents">
          <template v-for="(content, j) in cell.contents">
            <template v-if="content.link">
              <a :key="j" :href="content.link">{{ content.text }}</a
              >{{ cell.contents.length - j > 1 ? ', ' : '' }}
            </template>
            <template v-else
              >{{ content.text
              }}{{ cell.contents.length - j > 1 ? ', ' : '' }}</template
            >
          </template>
        </template>
        <template v-else-if="cell && cell.barchart">
          <div class="value">{{ cell.value }}</div>
          <div class="barcontainer">
            <div :style="{ width: cell.width + '%' }" class="bar"></div>
          </div>
        </template>
        <template v-else-if="cell && cell.ticker">
          {{ cell.value > 0 ? '+' + cell.value : cell.value }}
        </template>
        <template v-else-if="cell && cell.html">
          <!-- eslint-disable-next-line vue/no-v-html -->
          <div v-html="cell.html"></div>
        </template>
        <template v-else>
          <template v-if="['string', 'number'].indexOf(typeof cell) > -1">{{
            cell
          }}</template>
          <template v-else-if="cell">
            <template v-if="cell.link">
              <a v-if="cell.image" :href="cell.link">
                <img :src="cell.image" :style="cell.imageStyle" />
              </a>
              <a v-else :href="cell.link" class="funblue-light-hover">
                {{ cell.text }}
              </a>
            </template>
            <template v-else>
              <img
                v-if="cell.image"
                :src="cell.image"
                :style="cell.imageStyle"
              />
              <template v-else>{{ cell.text }}</template>
            </template>
          </template>
        </template>
      </div>
    </li>
  </ul>
</template>

<script>
import EmptyState from '@/_components/EmptyState.vue';

export default {
  name: 'SortableTable',
  components: {
    EmptyState,
  },
  props: {
    columns: {
      type: Array,
      default: () => [],
    },
    items: {
      type: Array,
      default: () => [],
    },
    sort: {
      type: String,
      default: '',
    },
    sortOrder: {
      type: String,
      default: '',
    },
    sortCallback: {
      type: Function,
      default: null,
    },
  },
  methods: {
    getColumnClasses(column, cell) {
      const classes = ['column', column.additionalClass];
      if (!cell) {
        return [
          ...classes,
          { sort: this.sort === column.id },
          { reverse: this.sortOrder === 'desc' },
        ];
      }
      return [...classes, { red: cell && cell.value <= 0 }];
    },
  },
};
</script>

<style scoped lang="scss">
@use 'parlassets/scss/colors';

.empty-container {
  position: relative;
  min-height: 265px;
  margin-bottom: 22px;
}

.headers {
  .column {
    color: colors.$font-default;
    position: relative;

    span {
      display: inline-block;
      margin-right: 10px;
    }

    &.sort span::after,
    &:not(.sort):hover span::after {
      content: '';
      border-style: solid;
      border-color: transparent transparent colors.$dropdown-arrow;
      border-width: 0 6px 7px;
      position: absolute;
      margin-left: 6px;
      margin-top: 6px;
      transform: rotate(0deg);
    }

    &.sort.reverse span::after {
      transform: rotate(180deg);
    }

    &.no-sort {
      cursor: auto;
      pointer-events: none;

      span::after {
        display: none !important;
      }
    }
  }
}

.session-list .item .column.ticker {
  color: colors.$second;
  line-height: 18px;

  &.red {
    color: colors.$third;
  }
}

.barchartcontainer {
  flex-wrap: nowrap;
  flex-direction: row;
  align-content: space-between;
  align-items: center;
  display: flex;
}

.value {
  font-size: 16px;
  line-height: 18px;
  background-color: colors.$white;
  // padding-right: 20px;
  display: flex;
  flex: 0 0 74px;
  width: 74px;
}

.barcontainer {
  display: flex;
  flex: 1 1 0%;
}

.bar {
  width: 100%;
  background-color: colors.$barchart-default;
  height: 18px;
  display: flex;
  flex-wrap: nowrap;
  transition: width 0.6s ease;
}

.card-seznam-zakonov .session-list {
  .item {
    padding: 0;
  }

  .headers {
    margin-left: 0;

    .column {
      text-align: left;
      padding: 0 15px;
      color: colors.$font-default;

      &:first-child {
        margin-left: 0;
      }
    }
  }

  .item {
    .column {
      text-align: left;
      padding: 15px;
      font-size: 16px;

      &:first-child {
        margin-left: 0;
      }
    }
  }
}
</style>
