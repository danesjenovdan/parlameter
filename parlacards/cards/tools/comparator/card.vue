<template>
  <card-wrapper :header-config="headerConfig" max-height>
    <div class="votes-list">
      <div
        :class="{ 'above-filters': true, highlighted: instructionsHighlighted }"
      >
        <div class="instructions">
          <svg
            v-if="!instructionsHighlighted"
            width="15"
            height="13"
            viewBox="0 0 15 13"
            fill="none"
            xmlns="http://www.w3.org/2000/svg"
          >
            <path
              d="M12 0H2.4C1.07422 0 0 1.07422 0 2.4V7.2C0 8.52578 1.07422 9.6 2.4 9.6H3.75625V12.2C3.75625 12.5563 4.18593 12.7344 4.43828 12.482L7.32028 9.60003H12C13.3257 9.60003 14.4 8.52582 14.4 7.20003V2.40003C14.4 1.07425 13.3257 3.3315e-05 12 3.3315e-05L12 0ZM2.7 4.8C2.7 4.19218 3.19218 3.7 3.8 3.7C4.40782 3.7 4.9 4.19218 4.9 4.8C4.9 5.40782 4.40782 5.9 3.8 5.9C3.19218 5.9 2.7 5.40782 2.7 4.8ZM7.2 5.9C6.59218 5.9 6.1 5.40782 6.1 4.8C6.1 4.19218 6.59218 3.7 7.2 3.7C7.80782 3.7 8.3 4.19218 8.3 4.8C8.3 5.40782 7.80782 5.9 7.2 5.9ZM10.6 5.9C9.99218 5.9 9.5 5.40782 9.5 4.8C9.5 4.19218 9.99218 3.7 10.6 3.7C11.2078 3.7 11.7 4.19218 11.7 4.8C11.7 5.40782 11.2078 5.9 10.6 5.9Z"
              fill="black"
            />
          </svg>
          <svg
            v-else
            width="17"
            height="14"
            viewBox="0 0 17 14"
            fill="none"
            xmlns="http://www.w3.org/2000/svg"
          >
            <path
              d="M9.07168 0.580662C8.5795 -0.193554 7.45136 -0.193554 6.95985 0.580662L0.197514 11.2213C-0.332169 12.0534 0.265482 13.1432 1.25376 13.1432H14.7796C15.7655 13.1432 16.364 12.0533 15.8358 11.2213L9.07168 0.580662ZM7.41543 4.18466C7.41543 3.85263 7.6834 3.58466 8.01543 3.58466C8.34747 3.58466 8.61543 3.85263 8.61543 4.18466V7.65266C8.61543 7.9847 8.34747 8.25266 8.01543 8.25266C7.6834 8.25266 7.41543 7.9847 7.41543 7.65266V4.18466ZM8.01543 10.8893C7.50137 10.8893 7.08575 10.4753 7.08575 9.96511C7.08575 9.45496 7.50138 9.0409 8.01543 9.0409C8.52948 9.0409 8.94512 9.45496 8.94512 9.96511C8.94512 10.4753 8.52948 10.8893 8.01543 10.8893Z"
              fill="black"
            />
          </svg>

          <span>
            {{ $t(instructionsKey) }}
          </span>
        </div>
      </div>
      <div class="filters">
        <div
          :class="{
            filter: true,
            'dropdown-filter': true,
            highlighted: firstDropdownHighlighted,
          }"
        >
          <div class="filter-label">
            {{ $t('select-members-voted-same') }}
          </div>
          <PSearchDropdown
            v-model="sameMembersAndGroups"
            :groups="dropdownGroups"
          />
        </div>
        <div
          :class="{
            filter: true,
            'dropdown-filter': true,
            highlighted: secondDropdownHighlighted,
          }"
        >
          <div class="filter-label">
            {{ $t('select-members-voted-different') }}
          </div>
          <PSearchDropdown
            v-model="differentMembersAndGroups"
            :groups="dropdownGroups"
          />
        </div>
        <div class="filter-button">
          <div class="filter-label">&nbsp;</div>
          <button class="button" @click="onCompareClick">
            {{ $t('compare') }}
          </button>
        </div>
      </div>
      <div :class="['under-filters', { shown: showUnderFilters }]">
        <div class="selected-same-different">
          <div>
            {{ $t('comparator-same-vote') }}
            <span>{{ formatList(selectedSame) || '/' }}</span>
          </div>
          <div>
            {{ $t('comparator-different-vote') }}
            <span>{{ formatList(selectedDifferent) || '/' }}</span>
          </div>
        </div>
        <div :class="['results-count', { shown: showResultsCount }]">
          <div>
            {{ $t('comparator-vote-count') }}
            <span>{{ card.objectCount }}</span
            >.
          </div>
          <div>
            <i18n-t keypath="comparator-vote-percentage">
              <template #percent>
                <span>{{
                  votes_total > 0
                    ? formatPercent((card.objectCount / votes_total) * 100)
                    : formatPercent(0)
                }}</span>
              </template>
            </i18n-t>
          </div>
        </div>
      </div>

      <ScrollShadow ref="shadow">
        <div
          v-infinite-scroll="loadMore"
          class="votes-list-shadow"
          @scroll="$refs.shadow.check($event.currentTarget)"
        >
          <VoteListItem v-for="vote in votes" :key="vote.id" :vote="vote" />
        </div>
        <div v-if="card.isLoading" class="nalagalnik__wrapper">
          <div class="nalagalnik"></div>
        </div>
      </ScrollShadow>
    </div>
  </card-wrapper>
</template>

<script>
import { uniqBy } from 'lodash-es';
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

    const initialCount = cardData?.data?.['votes:count'] ?? 0;

    return {
      headerConfig: defaultHeaderConfig(this),
      card: {
        objectCount: initialCount,
        currentPage: 1,
        isLoading: false,
      },
      votes: cardData?.data?.results?.votes ?? [],
      votes_total: cardData?.data?.results?.votes_total ?? 0,
      sameMembersAndGroups,
      differentMembersAndGroups,
      dropdownGroups,
      instructionsKey: 'comparator-empty-state-text',
      instructionsHighlighted: false,
      firstDropdownHighlighted: false,
      secondDropdownHighlighted: false,
      showUnderFilters: initialCount > 0,
      showResultsCount: initialCount > 0,
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
      this.showUnderFilters = true;
      this.resetSearch();
    },
    selectedDifferent(newSelectedDifferent) {
      this.sameMembersAndGroups.forEach((item) => {
        item.disabled = newSelectedDifferent.some((p) => p.slug === item.slug);
      });
      this.showUnderFilters = true;
      this.resetSearch();
    },
  },
  methods: {
    onCompareClick() {
      if (this.selectedSame.length < 1) {
        this.instructionsKey = 'comparator-empty-state-text-same';
        this.instructionsHighlighted = true;
        this.firstDropdownHighlighted = true;
        this.secondDropdownHighlighted = false;
        this.resetSearch();
        return;
      }
      if (this.selectedSame.length + this.selectedDifferent.length < 2) {
        this.instructionsKey = 'comparator-empty-state-text';
        this.instructionsHighlighted = true;
        this.firstDropdownHighlighted = true;
        this.secondDropdownHighlighted = true;
        this.resetSearch();
        return;
      }
      this.instructionsKey = 'comparator-empty-state-text';
      this.instructionsHighlighted = false;
      this.firstDropdownHighlighted = false;
      this.secondDropdownHighlighted = false;
      this.searchVotesImmediate();
    },
    resetSearch() {
      if (this.abortController) {
        this.abortController.abort();
      }
      this.card.isLoading = false;
      this.votes = [];
      this.showResultsCount = false;
      this.card.objectCount = 0;
      this.card.currentPage = 1;
    },
    searchVotesImmediate() {
      this.showResultsCount = false;
      this.card.isLoading = true;
      this.votes = [];
      this.card.objectCount = 0;
      this.card.currentPage = 1;
      this.makeRequest(this.searchUrl).then((response) => {
        this.votes = response?.data?.results?.votes || [];
        this.card.objectCount = response?.data?.['votes:count'];
        this.card.currentPage = 1;
        this.card.isLoading = false;
        this.showResultsCount = true;

        if (this.card.objectCount === 0) {
          this.instructionsKey = 'comparator-empty-state-no-results';
          this.instructionsHighlighted = true;
        }
      });
    },
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
  .above-filters {
    margin-bottom: 20px;
    padding: 4px 10px;
    background-color: colors.$light-background;

    .instructions {
      display: flex;
      gap: 8px;
      align-items: center;
      justify-content: center;
      font-family: 'Roboto Slab', 'Times New Roman', serif;
      font-size: 14px;
      text-align: center;

      @include breakpoints.respond-to(mobile) {
        font-size: 12px;
        text-align: left;
      }

      svg {
        flex-shrink: 0;

        @include breakpoints.respond-to(mobile) {
          width: 14px;
        }
      }
    }

    &.highlighted {
      background-color: #ffdcd6;
    }
  }

  .filters {
    display: flex;
    gap: 6px 10px;
    flex-wrap: wrap;
    padding-bottom: 12px;

    @include breakpoints.respond-to(mobile) {
      flex-direction: column;
    }

    .filter-label {
      overflow: hidden;
      height: 20px;

      @include breakpoints.respond-to(mobile) {
        font-size: 12px;
        height: 18px;
      }
    }

    .dropdown-filter {
      flex: 1;

      &.highlighted {
        .search-dropdown {
          outline: 1px solid colors.$font-default;
        }
      }
    }

    .filter-button {
      .filter-label {
        @include breakpoints.respond-to(mobile) {
          height: 8px;
        }
      }

      .button {
        display: block;
        font-size: 15px;
        font-weight: 400;
        line-height: 20px;
        padding: 10px 25px;
        color: colors.$white;
        border: none;
        background-color: colors.$tab-passive;
        cursor: pointer;

        &:hover {
          color: colors.$white;
          background-color: colors.$tab-hover;
          text-decoration: none;
        }

        &.active {
          color: colors.$white;
          background-color: colors.$tab-active;
          text-decoration: none;
        }

        @include breakpoints.respond-to(mobile) {
          width: 100%;
        }
      }
    }
  }

  .under-filters {
    display: flex;
    padding-bottom: 12px;
    visibility: hidden;

    &.shown {
      visibility: visible;
    }

    @include breakpoints.respond-to(mobile) {
      display: none;
    }

    .selected-same-different,
    .results-count {
      flex: 2;
      display: flex;
      flex-direction: column;

      span {
        font-weight: 500;
      }
    }

    .results-count {
      flex: 1;
      text-align: right;
      visibility: hidden;

      &.shown {
        visibility: visible;
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
