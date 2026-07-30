<template>
  <TransparentWrapper>
    <Seats :seat-data="seatData" />
  </TransparentWrapper>
</template>

<script>
import common from '@/_mixins/common.js';
import TransparentWrapper from '@/_components/TransparentWrapper.vue';
import Seats from '@/_components/Seats.vue';

export default {
  name: 'CardMiscSeats',
  components: {
    TransparentWrapper,
    Seats,
  },
  mixins: [common],
  data() {
    const { cardData } = this.$root.$options.contextData;

    const groups = cardData?.data?.results || [];
    const seatData = groups
      .map((g) => ({
        id: g.slug,
        slug: g.slug,
        name: g.name,
        acronym: g.acronym,
        color: g.color,
        seats: g.results.seat_count,
        members: g.results.members,
      }))
      .sort((a, b) => b.seats - a.seats);

    return {
      seatData,
    };
  },
};
</script>
