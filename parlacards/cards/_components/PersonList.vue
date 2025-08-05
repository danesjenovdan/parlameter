<template>
  <empty-state v-if="!people?.length" />
  <scroll-shadow v-else ref="shadow">
    <div
      v-infinite-scroll="() => $emit('load-more')"
      class="person-list-shadow"
      @scroll="$refs.shadow.check($event.currentTarget)"
    >
      <ul class="person-list">
        <li v-for="person in people" :key="person.slug" class="person">
          <a :href="getPersonLink(person)" class="portrait column">
            <img
              :src="getPersonPortrait(person)"
              :style="{ border: getPersonBorder(person) }"
            />
          </a>
          <div class="column name">
            <div class="person-name">
              <a :href="getPersonLink(person)" class="funblue-light-hover">
                {{ getPersonName(person) }}
              </a>
            </div>
            <template v-if="showPartyLink">
              <div class="person-party">
                <a
                  v-if="getPartyLink(person.group)"
                  :href="getPartyLink(person.group)"
                  class="funblue-light-hover"
                >
                  {{ person.group?.acronym || person.group?.name || 'N/A' }}
                </a>
                <span v-else>
                  {{ $t(unaffiliatedKey(person)) }}
                </span>
              </div>
            </template>
          </div>
          <div v-if="person.score" class="column large-number">
            {{ person.score }}
          </div>
        </li>
      </ul>
    </div>
    <div v-if="paginationState.isLoading" class="nalagalnik__wrapper">
      <div class="nalagalnik"></div>
    </div>
  </scroll-shadow>
</template>

<script>
import links from '@/_mixins/links.js';
import ScrollShadow from '@/_components/ScrollShadow.vue';
import EmptyState from '@/_components/EmptyState.vue';
import infiniteScroll from '@/_directives/infiniteScroll.js';

export default {
  name: 'PersonList',
  directives: {
    infiniteScroll,
  },
  components: {
    ScrollShadow,
    EmptyState,
  },
  mixins: [links],
  props: {
    people: {
      type: Array,
      required: true,
    },
    showPartyLink: {
      type: Boolean,
      default: false,
    },
    paginationState: {
      type: Object,
      default: () => ({}),
    },
  },
  emits: ['load-more'],
  methods: {
    unaffiliatedKey(person) {
      let suffix = '--f';
      if (person.preferred_pronoun === 'he') suffix = '--m';
      return `unaffiliated${suffix}`;
    },
  },
};
</script>

<style lang="scss" scoped>
@use 'parlassets/scss/breakpoints';
@use 'parlassets/scss/colors';

.person-list-shadow {
  overflow-y: auto;
  height: breakpoints.$full-card-height;

  @include breakpoints.respond-to(mobile) {
    height: auto;
    max-height: breakpoints.$full-card-height;
  }

  .person-name,
  .person-party {
    line-height: 1.1;
  }

  .person-name {
    font-weight: 300;
  }

  .person-party {
    font-size: 14px;
    margin-top: 5px;
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
