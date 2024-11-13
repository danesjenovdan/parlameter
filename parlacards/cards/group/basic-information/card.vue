<template>
  <card-wrapper :header-config="headerConfig">
    <scroll-shadow ref="shadow">
      <div
        v-infinite-scroll="loadMore"
        class="poslanec osnovne-informacije-poslanca"
        @scroll="$refs.shadow.check($event.currentTarget)"
      >
        <div v-if="results.presidents?.length" class="row">
          <div class="parlaicon-container">
            <span class="parlaicon parlaicon-vodja" aria-hidden="true" />
          </div>
          <div class="bordertop">
            <template v-for="person in results.presidents" :key="person.slug">
              <person-with-position :person="person" position="president" />
            </template>
          </div>
        </div>

        <div v-if="results.deputies?.length" class="row">
          <div class="parlaicon-container">
            <span class="parlaicon parlaicon-namestnik" aria-hidden="true" />
          </div>
          <div class="bordertop">
            <template v-for="person in results.deputies" :key="person.slug">
              <person-with-position :person="person" position="deputy" />
            </template>
          </div>
        </div>

        <div v-if="results.email" class="row">
          <div class="parlaicon-container">
            <span class="parlaicon parlaicon-kontakt" aria-hidden="true" />
          </div>
          <div class="bordertop contact-container">
            <span class="key">
              <span v-t="'contact'"></span>:
              <a
                :href="`mailto:${results.email}`"
                target="_blank"
                class="funblue-light-hover"
                >{{ shortEmail }}</a
              >
            </span>
          </div>
        </div>

        <div v-if="results.social_networks?.length" class="row">
          <div class="parlaicon-container">
            <span class="parlaicon parlaicon-omrezja" aria-hidden="true" />
          </div>
          <div class="bordertop">
            <span class="key">
              <span v-t="'social-media'"></span>:
              <template v-if="results.social_networks?.length">
                <template
                  v-for="social_network in results.social_networks"
                  :key="`${social_network?.type}_${social_network?.url}`"
                >
                  <a
                    :href="social_network?.url"
                    class="socialicon-container"
                    target="_blank"
                  >
                    <div
                      :class="[
                        'parlaicon',
                        `parlaicon-${social_network?.type}`,
                      ]"
                    />
                  </a>
                </template>
              </template>
              <template v-else>
                <b v-t="'no-social-media'"></b>
              </template>
            </span>
          </div>
        </div>

        <div class="row">
          <div class="parlaicon-container">
            <span class="parlaicon parlaicon-sedezi" aria-hidden="true" />
          </div>
          <div class="bordertop">
            <span class="key">
              <span v-t="'number-of-seats'"></span>:
              <strong>{{ results.number_of_members }}</strong>
            </span>
          </div>
        </div>

        <div v-if="members?.length" class="row">
          <div class="parlaicon-container parlaicon-top">
            <!-- <span class="parlaicon parlaicon-clanstva" aria-hidden="true" /> -->
          </div>
          <div class="bordertop">
            <template v-for="person in members" :key="person.slug">
              <person-with-position :person="person" position="member" />
            </template>
          </div>
        </div>
      </div>
      <div v-if="card.isLoading" class="nalagalnik__wrapper">
        <div class="nalagalnik"></div>
      </div>
    </scroll-shadow>
  </card-wrapper>
</template>

<script>
import axios from 'axios';
import common from '@/_mixins/common.js';
import { partyOverviewContextUrl } from '@/_mixins/contextUrls.js';
import { partyTitle } from '@/_mixins/titles.js';
import { partyHeader } from '@/_mixins/altHeaders.js';
import { partyOgImage } from '@/_mixins/ogImages.js';
import links from '@/_mixins/links.js';
import PersonWithPosition from '@/_components/PersonWithPosition.vue';
import ScrollShadow from '@/_components/ScrollShadow.vue';
import infiniteScroll from '@/_directives/infiniteScroll.js';

export default {
  name: 'CardGroupBasicInformation',
  directives: {
    infiniteScroll,
  },
  components: {
    PersonWithPosition,
    ScrollShadow,
  },
  mixins: [
    common,
    partyOverviewContextUrl,
    partyTitle,
    partyHeader,
    partyOgImage,
    links,
  ],
  data() {
    const { cardData } = this.$root.$options.contextData;

    return {
      card: {
        currentPage: 1,
        isLoading: false,
      },
      results: cardData?.data?.results || {},
      group: cardData?.data?.group || {},
      members: cardData?.data?.results?.members || [],
    };
  },
  computed: {
    shortEmail() {
      if (this.results.email?.length) {
        if (this.results.email.length < 26) {
          return this.results.email;
        }
        const [addr, domain] = this.results.email.split('@');
        if (addr.length < 18) {
          return this.results.email;
        }
        return `${addr.slice(0, 17)}…@${domain}`;
      }
      return '';
    },
    searchUrl() {
      const url = new URL(this.cardData.url);
      url.searchParams.set('members:page', this.card.currentPage);
      return url.toString();
    },
  },
  methods: {
    loadMore() {
      if (this.card.isLoading) {
        return;
      }
      if (this.members.length >= this.cardData.data?.['members:count']) {
        return;
      }

      this.card.isLoading = true;
      this.card.currentPage += 1;

      const requestedPage = this.card.currentPage;
      axios.get(this.searchUrl).then((response) => {
        if (response?.data?.['members:page'] === requestedPage) {
          const newMembers = response?.data?.results?.members || [];
          this.members.push(...newMembers);
        }
        this.card.isLoading = false;
      });
    },
  },
};
</script>

<style lang="scss" scoped>
@use 'parlassets/scss/breakpoints';
@use 'parlassets/scss/colors';

.parlaicon-namestnik {
  background-image: url('#{get-parlassets-url()}/icons/namestnik.svg');
}
.parlaicon-sedezi {
  background-image: url('#{get-parlassets-url()}/icons/sedezi.svg');
}

.parlaicon-omrezja {
  width: 30px;
  height: 30px;
  line-height: normal;
}

.parlaicon-container {
  padding: 10px 16px;
  @include breakpoints.respond-to(desktop) {
    min-width: 70px;
  }

  &.parlaicon-top {
    justify-content: flex-start !important;
    padding-top: 27px;
  }
}

.bordertop {
  border-top: 1px solid colors.$background;
  padding: 10px 0;
  flex: 1;
}

.poslanec {
  padding: 0;
}

.socialicon-container {
  margin-right: 10px;
}

.osnovne-informacije-poslanca {
  display: flex;
  flex-direction: column;
  height: 100%;
  max-height: breakpoints.$full-card-height;
  overflow-y: auto;

  .row {
    display: flex;
    flex: 1;
    margin: 0;
    min-height: 0; // firefox flex bug
    min-height: -moz-fit-content;
    min-height: fit-content;

    > div {
      display: flex;
      flex-direction: column;
      justify-content: center;
    }

    .key {
      color: colors.$font-default;
    }
  }
}

.contact-container {
  overflow: hidden;

  .key {
    overflow: hidden;
    text-overflow: ellipsis;
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
