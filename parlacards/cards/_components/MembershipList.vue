<template>
  <scroll-shadow ref="shadow">
    <div
      class="membership-list date-list"
      @scroll="$refs.shadow.check($event.currentTarget)"
    >
      <empty-state v-if="!results?.length" small />
      <div v-else>
        <div v-for="(memberships, role) in membershipsByRole" :key="role">
          <div class="date">{{ formatRole(role || 'member') }}</div>
          <div class="membership-items">
            <div
              v-for="(membership, i) in memberships"
              :key="`${role}-${i}`"
              class="membership-item"
            >
              {{ membership?.organization?.name }}
            </div>
          </div>
        </div>
      </div>
    </div>
  </scroll-shadow>
</template>

<script>
import ScrollShadow from '@/_components/ScrollShadow.vue';
import EmptyState from '@/_components/EmptyState.vue';
import { groupBy } from 'lodash-es';

export default {
  name: 'MembershipList',
  components: {
    ScrollShadow,
    EmptyState,
  },
  props: {
    results: {
      type: Array,
      required: true,
    },
    person: {
      type: Object,
      default: () => ({}),
    },
  },
  computed: {
    membershipsByRole() {
      const grouped = groupBy(
        this.results,
        (membership) => membership.role || 'member',
      );

      // insertion order is guaranteed, so insert the roles in the order we want
      let sorted = {};
      ['leader', 'president', 'deputy', 'member'].forEach((role) => {
        if (role in grouped && grouped[role].length) {
          sorted[role] = grouped[role];
          delete grouped[role];
        }
      });
      // add any remaining roles
      sorted = { ...sorted, ...grouped };

      return sorted;
    },
  },
  methods: {
    formatRole(role) {
      const transKey = role.toLowerCase().replaceAll(' ', '-');
      const form = this.person.preferred_pronoun === 'she' ? '--f' : '--m';
      return this.$te(`${transKey}${form}`)
        ? this.$t(`${transKey}${form}`)
        : this.$te(transKey)
          ? this.$t(transKey)
          : role;
    },
  },
};
</script>

<style lang="scss" scoped>
.membership-list {
  height: 180px;
  overflow-y: auto;

  .date {
    font-weight: 500;
  }

  .membership-items {
    padding: 8px 0 16px;

    .membership-item {
      padding: 2px 10px;
    }
  }
}
</style>
