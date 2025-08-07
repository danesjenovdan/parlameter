<template>
  <card-wrapper :header-config="headerConfig">
    <compass
      :compass-data="$options.contextData.cardData?.data?.results || []"
    />
  </card-wrapper>
</template>

<script>
import common from '@/_mixins/common.js';
import { defaultHeaderConfig } from '@/_mixins/altHeaders.js';
import Compass from './Compass.vue';

export default {
  name: 'CardToolsCompass',
  components: {
    Compass,
  },
  mixins: [common],
  cardInfo: {
    doubleWidth: true,
  },
  data() {
    return {
      headerConfig: defaultHeaderConfig(this, { circleIcon: 'og-kompas' }),
    };
  },
};
</script>
