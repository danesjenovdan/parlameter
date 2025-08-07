<template>
  <card-wrapper :header-config="headerConfig" max-height>
    <div class="votes-list">
      <div class="filters">
        <div class="filter dropdown-filter">
          <div class="filter-label">
            {{ $t('select-members-voted-same') }}
          </div>
          <PSearchDropdown
            v-model="sameMembersAndGroups"
            :groups="dropdownGroups"
            @update:model-value="searchVotes"
          />
        </div>
        <div class="filter dropdown-filter">
          <div class="filter-label">
            {{ $t('select-members-voted-different') }}
          </div>
          <PSearchDropdown
            v-model="differentMembersAndGroups"
            :groups="dropdownGroups"
            @update:model-value="searchVotes"
          />
        </div>
        <div class="filter-text">
          <i18n-t
            keypath="comparator-vote-percent"
            tag="div"
            class="filter-summary"
            scope="global"
          >
            <template #num>
              <strong v-if="card.isLoading">?</strong>
              <strong v-else>{{ card.objectCount }}</strong>
            </template>
            <template #percent>
              <br />
              <strong v-if="card.isLoading">?</strong>
              <strong v-else-if="votes_total == 0">{{
                formatPercent(0)
              }}</strong>
              <strong v-else>{{
                formatPercent((card.objectCount / votes_total) * 100)
              }}</strong>
            </template>
          </i18n-t>
        </div>
        <div class="under-filters">
          <i18n-t
            keypath="comparator-text"
            tag="div"
            class="filter-explainer"
            scope="global"
          >
            <template #same>
              <span class="primerjalnik-for">
                <strong v-if="!selectedSame.length">?</strong>
                <strong v-else>{{ formatList(selectedSame) }}</strong>
              </span>
            </template>
            <template #different>
              <span class="primerjalnik-against">
                <strong v-if="!selectedDifferent.length">?</strong>
                <strong v-else>{{ formatList(selectedDifferent) }}</strong>
              </span>
            </template>
          </i18n-t>
        </div>
      </div>

      <ScrollShadow ref="shadow">
        <div
          v-infinite-scroll="loadMore"
          class="votes-list-shadow"
          @scroll="$refs.shadow.check($event.currentTarget)"
        >
          <EmptyCircle
            v-if="
              !card.isLoading &&
              selectedSame.length + selectedDifferent.length < 2
            "
            :text="$t('comparator-empty-state-text')"
          />
          <EmptyCircle
            v-else-if="!card.isLoading && !selectedSame.length"
            :text="$t('comparator-empty-state-text-same')"
          />
          <EmptyCircle
            v-else-if="!card.isLoading && !votes?.length"
            :text="$t('filtered-to-none')"
          />
          <VoteListItem
            v-for="vote in votes"
            v-else
            :key="vote.id"
            :vote="vote"
          />
        </div>
        <div v-if="card.isLoading" class="nalagalnik__wrapper">
          <div class="nalagalnik"></div>
        </div>
      </ScrollShadow>
    </div>
  </card-wrapper>
</template>

<script>
import { debounce, uniqBy } from 'lodash-es';
import EmptyCircle from '@/_components/EmptyCircle.vue';
import ScrollShadow from '@/_components/ScrollShadow.vue';
import infiniteScroll from '@/_directives/infiniteScroll.js';
import PSearchDropdown from '@/_components/SearchDropdown.vue';
import VoteListItem from '@/_components/VoteListItem.vue';
import numberFormatter from '@/_helpers/numberFormatter.js';
import listFormatter from '@/_helpers/listFormatter.js';
import { defaultHeaderConfig } from '@/_mixins/altHeaders.js';
import common from '@/_mixins/common.js';
import cancelableRequest from '@/_mixins/cancelableRequest.js';
import links from '@/_mixins/links.js';

export default {
  name: 'CardToolsComparator',
  directives: {
    infiniteScroll,
  },
  components: {
    EmptyCircle,
    PSearchDropdown,
    ScrollShadow,
    VoteListItem,
  },
  mixins: [common, cancelableRequest, links],
  cardInfo: {
    doubleWidth: true,
  },
  data() {
    const { cardState, cardData } = this.$root.$options.contextData;

    const getSelectedIDs = (stateKey) => {
      return (cardState?.[stateKey] || '').split(',').map((id) => id.trim());
    };
    const sameMemberIds = getSelectedIDs('sameMembers');
    const differentMemberIds = getSelectedIDs('differentMembers');
    // const sameGroupIds = getSelectedIDs('sameGroups');
    // const differentGroupIds = getSelectedIDs('differentGroups');

    const rawMembers = cardData?.data?.results?.members || [];
    const members = rawMembers.map((member) => {
      const mid = (member.slug || '').split('-')[0];
      return {
        id: mid,
        slug: member.slug,
        label: member.name,
        image: member.image,
        imageStyle: { border: this.getPersonBorder(member) },
        selected: false,
        disabled: false,
        isMember: true,
      };
    });

    const groups = (cardData?.data?.results?.groups || []).map((group) => {
      const gid = (group.slug || '').split('-')[0];
      return {
        id: gid,
        slug: group.slug,
        label: group.name,
        selected: false,
        disabled: false,
        color: group.color,
        isGroup: true,
      };
    });

    const sameMembersAndGroups = (() => {
      const sameMembers = members.map((member) => ({
        ...member,
        selected: sameMemberIds.includes(member.id),
        disabled: differentMemberIds.includes(member.id),
      }));
      const sameGroups = [];
      // const sameGroups = groups.map((group) => ({
      //   ...group,
      //   selected: sameGroupIds.includes(group.id),
      //   disabled: differentGroupIds.includes(group.id),
      // }));
      return [...sameMembers, ...sameGroups];
    })();

    const differentMembersAndGroups = (() => {
      const differentMembers = members.map((member) => ({
        ...member,
        selected: differentMemberIds.includes(member.id),
        disabled: sameMemberIds.includes(member.id),
      }));
      const differentGroups = [];
      // const differentGroups = groups.map((group) => ({
      //   ...group,
      //   selected: differentGroupIds.includes(group.id),
      //   disabled: sameGroupIds.includes(group.id),
      // }));
      return [...differentMembers, ...differentGroups];
    })();

    const dropdownGroups = (() => {
      const memberGroups = uniqBy(
        rawMembers.map((member) => member?.group),
        (group) => group?.slug,
      );
      return [
        {
          id: 'groups',
          label: this.$t('parties'),
          items: groups.map((group) => group?.id),
        },
        ...memberGroups.map((group) => {
          return {
            id: group?.slug || 'null',
            label: group?.name || ' ',
            items: rawMembers
              .filter((member) => member?.group?.slug === group?.slug)
              .map((member) => {
                return (member.slug || '').split('-')[0];
              }),
          };
        }),
      ];
    })();

    return {
      headerConfig: defaultHeaderConfig(this),
      card: {
        objectCount: cardData?.data?.['votes:count'] ?? 0,
        currentPage: 1,
        isLoading: false,
      },
      votes: cardData?.data?.results?.votes ?? [],
      votes_total: cardData?.data?.results?.votes_total ?? 0,
      sameMembersAndGroups,
      differentMembersAndGroups,
      dropdownGroups,
    };
  },
  computed: {
    selectedSame() {
      return this.sameMembersAndGroups.filter((item) => item.selected);
    },
    selectedDifferent() {
      return this.differentMembersAndGroups.filter((item) => item.selected);
    },
    selectedSameMembers() {
      return this.selectedSame.filter((item) => item.isMember);
    },
    selectedSameGroups() {
      return this.selectedSame.filter((item) => item.isGroup);
    },
    selectedDifferentMembers() {
      return this.selectedDifferent.filter((item) => item.isMember);
    },
    selectedDifferentGroups() {
      return this.selectedDifferent.filter((item) => item.isGroup);
    },
    searchUrl() {
      const url = new URL(this.cardData.url);
      url.searchParams.set('votes:page', this.card.currentPage);

      if (this.selectedSameMembers.length > 0) {
        url.searchParams.set(
          'members_same',
          this.selectedSameMembers.map((p) => p.id).join(','),
        );
      } else {
        url.searchParams.delete('members_same');
      }

      if (this.selectedDifferentMembers.length > 0) {
        url.searchParams.set(
          'members_different',
          this.selectedDifferentMembers.map((p) => p.id).join(','),
        );
      } else {
        url.searchParams.delete('members_different');
      }

      if (this.selectedSameGroups.length > 0) {
        url.searchParams.set(
          'groups_same',
          this.selectedSameGroups.map((g) => g.id).join(','),
        );
      } else {
        url.searchParams.delete('groups_same');
      }

      if (this.selectedDifferentGroups.length > 0) {
        url.searchParams.set(
          'groups_different',
          this.selectedDifferentGroups.map((g) => g.id).join(','),
        );
      } else {
        url.searchParams.delete('groups_different');
      }

      return url.toString();
    },
  },
  watch: {
    selectedSame(newSelectedSame) {
      this.differentMembersAndGroups.forEach((item) => {
        item.disabled = newSelectedSame.some((p) => p.slug === item.slug);
      });
    },
    selectedDifferent(newSelectedDifferent) {
      this.sameMembersAndGroups.forEach((item) => {
        item.disabled = newSelectedDifferent.some((p) => p.slug === item.slug);
      });
    },
  },
  methods: {
    searchVotesImmediate() {
      this.card.isLoading = true;
      this.votes = [];
      this.card.objectCount = 0;
      this.card.currentPage = 1;
      this.makeRequest(this.searchUrl).then((response) => {
        this.votes = response?.data?.results?.votes || [];
        this.card.objectCount = response?.data?.['votes:count'];
        this.card.currentPage = 1;
        this.card.isLoading = false;
      });
    },
    searchVotes: debounce(function searchVotes() {
      this.searchVotesImmediate();
    }, 750),
    loadMore() {
      if (this.card.isLoading) {
        return;
      }
      if (this.votes.length >= this.card.objectCount) {
        return;
      }

      this.card.isLoading = true;
      this.card.currentPage += 1;

      const requestedPage = this.card.currentPage;
      this.makeRequest(this.searchUrl).then((response) => {
        if (response?.data?.['votes:page'] === requestedPage) {
          const newVotes = response?.data?.results?.votes || [];
          this.votes.push(...newVotes);
        }
        this.card.isLoading = false;
      });
    },
    formatPercent(number) {
      return numberFormatter(number, { percent: true });
    },
    formatList(items) {
      return listFormatter(items.map((item) => item.label));
    },
  },
};
</script>

<style lang="scss" scoped>
@use 'parlassets/scss/breakpoints';
@use 'parlassets/scss/colors';

.votes-list {
  .filters {
    display: flex;
    gap: 6px 10px;
    flex-wrap: wrap;
    padding-bottom: 12px;

    .filter-label {
      overflow: hidden;
      height: 20px;
    }

    .dropdown-filter {
      flex-basis: 28%;
    }

    .filter-text {
      margin-left: auto;
      margin-top: 20px;
      align-content: center;
      justify-content: center;
      text-align: center;

      strong {
        white-space: nowrap;
      }
    }

    .under-filters {
      flex-basis: 100%;
      margin-top: 4px;

      .filter-explainer {
        text-align: center;
        font-style: italic;
      }
    }
  }

  .votes-list-shadow {
    overflow-y: auto;
    overflow-x: hidden;
    height: breakpoints.$full-card-height - 72;
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
}
</style>
