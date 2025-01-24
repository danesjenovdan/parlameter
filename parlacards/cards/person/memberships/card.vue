<template>
  <card-wrapper :header-config="headerConfig" half-height>
    <membership-list
      :person="$options.contextData.cardData?.data?.person"
      :results="$options.contextData.cardData?.data?.results || []"
    />
  </card-wrapper>
</template>

<script>
import common from '@/_mixins/common.js';
import { personOverviewContextUrl } from '@/_mixins/contextUrls.js';
import { personHeader } from '@/_mixins/altHeaders.js';
import { personOgImage } from '@/_mixins/ogImages.js';
import { personTitle } from '@/_mixins/titles.js';
import MembershipList from '@/_components/MembershipList.vue';

export default {
  name: 'CardPersonMemberships',
  components: {
    MembershipList,
  },
  mixins: [
    common,
    personHeader,
    personOgImage,
    personOverviewContextUrl,
    personTitle,
  ],
};
</script>
