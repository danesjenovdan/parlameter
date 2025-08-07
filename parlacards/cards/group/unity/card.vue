<template>
  <score-avg-max
    :party="$options.contextData.cardData?.data?.group"
    :results="$options.contextData.cardData?.data?.results"
    type="party"
    :precision="2"
    context="votings"
    :percent="true"
  />
</template>

<script>
import ScoreAvgMax from '@/_components/ScoreAvgMax.vue';

export default {
  name: 'CardGroupUnity',
  components: {
    ScoreAvgMax,
  },
};
</script>
