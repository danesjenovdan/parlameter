<template>
  <card-wrapper :header-config="headerConfig" max-height>
    <div class="group-attendance">
      <AttendanceByGroups :attendance="results" />
    </div>
  </card-wrapper>
</template>

<script>
import common from '@/_mixins/common.js';
import { sessionHeader } from '@/_mixins/altHeaders.js';
import { sessionOgImage } from '@/_mixins/ogImages.js';
import { sessionTranscriptContextUrl } from '@/_mixins/contextUrls.js';
import AttendanceByGroups from '@/_components/AttendanceByGroups.vue';

export default {
  name: 'CardSessionGroupAttendance',
  components: {
    AttendanceByGroups,
  },
  mixins: [common, sessionTranscriptContextUrl, sessionHeader, sessionOgImage],
  cardInfo: {
    doubleWidth: true,
  },
  data() {
    const { cardData } = this.$root.$options.contextData;

    return {
      results: cardData?.data?.results || [],
    };
  },
};
</script>

<style lang="scss" scoped>
.group-attendance {
  position: relative;
  min-height: 180px;
  margin-bottom: 20px;
}
</style>
