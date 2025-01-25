<template>
  <div class="row">
    <div class="col-md-12">
      <blue-button-list
        :items="tools"
        :value="currentTool"
        @input="changeTool"
      />
    </div>
  </div>
</template>

<script>
import BlueButtonList from '@/_components/BlueButtonList.vue';

export default {
  name: 'ToolsTabs',
  components: {
    BlueButtonList,
  },
  props: {
    currentTool: {
      type: String,
      required: true,
    },
  },
  data() {
    return {
      tools: [
        {
          id: 'notifications',
          label: this.$t('tools.notifications'),
        },
        {
          id: 'voteComparator',
          label: this.$t('tools.vote-comparator'),
        },
        {
          id: 'unity',
          label: this.$t('tools.unity'),
        },
        {
          id: 'compass',
          label: this.$t('tools.compass'),
        },
        {
          id: 'wordGroups',
          label: this.$t('tools.word-groups'),
        },
      ],
    };
  },
  methods: {
    changeTool(value) {
      const { siteMap: sm } = this.$root.$options.cardData;
      window.location.href = `/${sm.landing.tools}/${sm.tools[value]}`;
    },
  },
};
</script>
