<template>
  <scroll-shadow ref="shadow">
    <div
      v-infinite-scroll="() => $emit('load-more')"
      class="questions date-list"
      @scroll="$refs.shadow.check($event.currentTarget)"
    >
      <empty-state v-if="!sortedQuestionDays?.length" />
      <div v-else>
        <div v-for="day in sortedQuestionDays" :key="day.date">
          <div class="date">{{ formatDate(day.date) }}</div>
          <div v-for="(event, i) in day.events" :key="`${day.date}-${i}`">
            <event
              v-if="listType == 'events'"
              :key="`${day.date}-${i}`"
              :event="event"
              :show-author="showAuthor"
            />
            <question
              v-if="listType == 'questions'"
              :key="`${day.date}-${i}`"
              :question="event"
              :show-author="false"
            />
            <answer v-if="event.answer" :event="event" />
          </div>
        </div>
      </div>
    </div>
    <div v-if="isLoading" class="nalagalnik__wrapper">
      <div class="nalagalnik"></div>
    </div>
  </scroll-shadow>
</template>

<script>
import { orderBy } from 'lodash-es';
import ScrollShadow from '@/_components/ScrollShadow.vue';
import Event from '@/_components/Event.vue';
import Answer from '@/_components/Answer.vue';
import Question from '@/_components/Question.vue';
import EmptyState from '@/_components/EmptyState.vue';
import dateFormatter from '@/_helpers/dateFormatter.js';
import infiniteScroll from '@/_directives/infiniteScroll.js';

export default {
  name: 'QuestionList',
  directives: {
    infiniteScroll,
  },
  components: {
    ScrollShadow,
    Event,
    Answer,
    Question,
    EmptyState,
  },
  props: {
    questionDays: {
      type: Array,
      required: true,
    },
    showAuthor: {
      type: Boolean,
      default: false,
    },
    isLoading: {
      type: Boolean,
      default: false,
    },
    listType: {
      type: String,
      default: 'events',
    },
  },
  emits: ['load-more'],
  computed: {
    sortedQuestionDays() {
      return orderBy(this.questionDays, ['date'], ['desc']);
    },
  },
  methods: {
    formatDate(date) {
      return dateFormatter(date, this.$t('missing-date'));
    },
  },
};
</script>

<style lang="scss" scoped>
@use 'parlassets/scss/colors';
@use 'parlassets/scss/breakpoints';

.questions {
  min-height: 100px;
  flex: 1;
  overflow-y: auto;
  max-height: 100%;
  position: relative;
  height: breakpoints.$full-card-height;

  .date {
    font-weight: 500;
  }
}

.nalagalnik__wrapper {
  position: absolute;
  top: 0;
  bottom: 0;
  left: 0;
  right: 0;
  background: colors.$white-hover;
  z-index: 4;

  .nalagalnik {
    position: absolute;
    top: calc(50% - 50px);
  }
}
</style>
