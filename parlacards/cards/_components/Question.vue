<template>
  <div class="question">
    <div :class="['parlaicon', eventIcon]"></div>
    <div class="motion">
      <span>
        {{ question.text }}
      </span>
    </div>
  </div>
</template>

<script>
import links from '@/_mixins/links.js';

export default {
  name: 'Question',
  mixins: [links],
  props: {
    question: {
      type: Object,
      required: true,
    },
  },
  data() {
    return {};
  },
  computed: {
    eventIcon() {
      return 'parlaicon-vprasanje';
    },
  },
};
</script>

<style lang="scss">
.question {
  display: flex;
  font-weight: 500;
  font-size: 16px;
  line-height: 18px;
  margin: 7px 0;

  .parlaicon {
    margin-right: 10px;
    margin-top: 15px;
  }

  .motion {
    flex: 1;
    font-weight: 300;
    line-height: 20px;
    padding: 15px 0;
    margin-right: 10px;
  }
}
</style>
