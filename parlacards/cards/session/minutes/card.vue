<template>
  <card-wrapper :header-config="headerConfig" max-height>
    <div class="multiple-speeches">
      <pagination
        v-if="count > perPage"
        :page="page"
        :count="count"
        :per-page="perPage"
        @change="onPageChange"
      />
      <div v-if="fetching" class="nalagalnik"></div>
      <div v-else-if="!agendaItems.length" class="empty-container">
        <empty-state />
      </div>
      <template v-else>
        <minutes-item
          v-for="agendaItem in agendaItems"
          :key="agendaItem.id"
          :agenda-item="agendaItem"
          :session="session"
        />
        <pagination
          v-if="count > perPage"
          :page="page"
          :count="count"
          :per-page="perPage"
          @change="onPageChange"
        />
      </template>
    </div>
  </card-wrapper>
</template>

<script>
import axios from 'axios';
import links from '@/_mixins/links.js';
import common from '@/_mixins/common.js';
import { sessionHeader } from '@/_mixins/altHeaders.js';
import { sessionOgImage } from '@/_mixins/ogImages.js';
import { sessionAgendaContextUrl } from '@/_mixins/contextUrls.js';
import { MINUTES_PER_PAGE } from '@/_helpers/constants.js';
import MinutesItem from '@/_components/MinutesItem.vue';
import Pagination from '@/_components/Pagination.vue';
import EmptyState from '@/_components/EmptyState.vue';

export default {
  name: 'CardSessionMinutes',
  components: {
    MinutesItem,
    Pagination,
    EmptyState,
  },
  mixins: [
    common,
    links,
    sessionAgendaContextUrl,
    sessionHeader,
    sessionOgImage,
  ],
  cardInfo: {
    doubleWidth: true,
  },
  data() {
    const { cardState, cardData } = this.$root.$options.contextData;

    const {
      results = [],
      pages = 1,
      page: initialPage = 1,
      count = results?.length ?? 0,
      per_page: perPage = MINUTES_PER_PAGE,
    } = cardData?.data || {};

    const minutesPerPage = Array(pages);
    minutesPerPage[initialPage - 1] = results;

    const page = Number(cardState?.page) || initialPage;

    return {
      minutesPerPage,
      count,
      perPage,
      page,
      initialPage,
      fetching: false,
      session: cardData?.data?.session,
      showParagraphs: cardState?.showParagraphs?.toString() !== 'false',
    };
  },
  computed: {
    agendaItems() {
      return this.minutesPerPage[this.page - 1] || [];
    },
    searchUrl() {
      const url = new URL(this.cardData.url);
      url.searchParams.set('page', this.page);
      return url.toString();
    },
  },
  mounted() {
    document.body.style.overflowAnchor = 'none';
    if (this.page !== this.initialPage) {
      this.onPageChange(this.page);
    }
  },
  methods: {
    onPageChange(newPage) {
      if (this.fetching) {
        return;
      }
      this.page = newPage;
      this.scrollToTop();
      if (!this.minutesPerPage[newPage - 1]) {
        this.fetching = true;
        axios.get(this.searchUrl).then((response) => {
          const responsePage = response?.data?.page || 1;
          this.page = responsePage;
          this.minutesPerPage[responsePage - 1] = response?.data?.results;
          this.fetching = false;

          // needed if dynamically loaded to reset the css :target and scroll to selected element
          this.$nextTick(() => {
            const target = document.getElementById(
              window.location.hash.slice(1),
            );
            if (target) {
              const tmp = window.location.hash;
              window.location.hash = '';
              window.location.hash = tmp;
            } else {
              this.scrollToTop();
            }
          });
        });
      }
    },
    scrollToTop() {
      const id = this.$root.$options.contextData.mountId;
      const el = document.getElementById(id);
      if (el) {
        el.scrollIntoView();
      }
    },
  },
};
</script>

<style lang="scss" scoped>
@use 'parlassets/scss/breakpoints';
@use 'parlassets/scss/colors';

.empty-container {
  position: relative;
  min-height: 265px;
}

.multiple-speeches :deep(.speech-holder) {
  border-top: 1px solid colors.$background;

  @include breakpoints.respond-to(desktop) {
    padding-bottom: 20px;
    padding-top: 20px;
  }

  .person-session {
    height: 64px;

    @include breakpoints.respond-to(desktop) {
      height: auto;
    }
  }

  &:target {
    background: colors.$background;
  }
}

.nalagalnik {
  height: 51px;
  background-size: 38px;
}
</style>
