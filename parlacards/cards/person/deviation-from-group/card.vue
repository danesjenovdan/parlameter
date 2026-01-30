<template>
  <score-avg-max
    :person="$options.contextData.cardData?.data?.person"
    :results="$options.contextData.cardData?.data?.results"
    percent
    type="person"
    context="votings"
    no-data-translation-key="not-in-group"
  />
</template>

<script>
import ScoreAvgMax from '@/_components/ScoreAvgMax.vue';

export default {
  name: 'CardPersonDeviationFromGroup',
  components: {
    ScoreAvgMax,
  },
};
</script>
