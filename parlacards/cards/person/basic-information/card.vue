<template>
  <card-wrapper :header-config="headerConfig">
    <div class="poslanec osnovne-informacije-poslanca">
      <div v-if="showGroup" class="row">
        <div class="parlaicon-container">
          <span class="parlaicon parlaicon-skupina" aria-hidden="true"></span>
        </div>
        <div class="bordertop0">
          <span class="key">
            <span v-t="'party'"></span>:
            <a
              v-if="getPartyLink(group)"
              :href="getPartyLink(group)"
              class="funblue-light-hover"
            >
              {{ group.acronym || group.name || 'N/A' }}
            </a>
            <span v-else>
              {{ $t(unaffiliatedKey) }}
            </span>
          </span>
        </div>
      </div>

      <div
        v-if="results.number_of_points || results.number_of_voters"
        class="row"
      >
        <div class="parlaicon-container">
          <span class="parlaicon parlaicon-delaza" aria-hidden="true"></span>
        </div>
        <div class="bordertop0">
          <i18n-t :keypath="electedToDistrictKey" tag="span" class="key">
            <template #numVotes>
              <b>{{ results.number_of_points || results.number_of_voters }}</b>
            </template>
            <template #district>
              <b>{{ results?.districts?.map((d) => d.name).join(', ') }}</b>
            </template>
          </i18n-t>
        </div>
      </div>

      <div class="row">
        <div class="parlaicon-container">
          <span class="parlaicon parlaicon-mandat" aria-hidden="true"></span>
        </div>
        <div class="bordertop0">
          <span class="key">
            <span v-t="'number-of-terms'"></span>:
            <b>{{ results.number_of_mandates }}</b>
          </span>
        </div>
      </div>

      <div class="row">
        <div class="parlaicon-container">
          <span class="parlaicon parlaicon-status" aria-hidden="true"></span>
        </div>
        <div class="bordertop0">
          <span class="key">
            <span v-t="'previous-occupation'"></span>:
            <b>{{ results.previous_occupation }}</b>
          </span>
        </div>
      </div>

      <div class="row">
        <div class="parlaicon-container">
          <span class="parlaicon parlaicon-izobrazba" aria-hidden="true"></span>
        </div>
        <div class="bordertop0">
          <span class="key">
            <span v-t="'education'"></span>: <b>{{ results.education }}</b>
          </span>
        </div>
      </div>

      <div v-if="age" class="row">
        <div class="parlaicon-container">
          <span class="parlaicon parlaicon-starost" aria-hidden="true"></span>
        </div>
        <div class="bordertop0">
          <span class="key">
            <span v-t="'age'"></span>: <b>{{ $t('age--years', { age }) }}</b>
          </span>
        </div>
      </div>

      <div v-if="results.email" class="row">
        <div class="parlaicon-container">
          <span class="parlaicon parlaicon-kontakt" aria-hidden="true"></span>
        </div>
        <div class="bordertop0 contact-container">
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
          <span class="parlaicon parlaicon-omrezja" aria-hidden="true"></span>
        </div>
        <div class="bordertop0">
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
                    :class="['parlaicon', `parlaicon-${social_network?.type}`]"
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
    </div>
  </card-wrapper>
</template>

<script>
import common from '@/_mixins/common.js';
import { personOverviewContextUrl } from '@/_mixins/contextUrls.js';
import { personTitle } from '@/_mixins/titles.js';
import { personHeader } from '@/_mixins/altHeaders.js';
import { personOgImage } from '@/_mixins/ogImages.js';
import links from '@/_mixins/links.js';
import age from '@/_helpers/age.js';

export default {
  name: 'CardPersonBasicInformation',
  mixins: [
    common,
    personOverviewContextUrl,
    personTitle,
    personHeader,
    personOgImage,
    links,
  ],
  data() {
    const { cardState, cardData } = this.$root.$options.contextData;

    return {
      results: cardData?.data?.results ?? {},
      person: cardData?.data?.person ?? {},
      group: cardData?.data?.person?.group ?? {},
      showGroup: cardState?.showGroup !== 'false',
    };
  },
  computed: {
    age() {
      return age(this.results.date_of_birth);
    },
    electedToDistrictKey() {
      let suffix = '';
      if (this.person.preferred_pronoun === 'she') suffix = '--f';
      if (this.person.preferred_pronoun === 'he') suffix = '--m';
      if (this.person.number_of_points) {
        return `elected-to-district-with-points${suffix}`;
      }
      return `elected-to-district${suffix}`;
    },
    unaffiliatedKey() {
      let suffix = '--f';
      if (this.person.preferred_pronoun === 'he') suffix = '--m';
      return `unaffiliated${suffix}`;
    },
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
  },
};
</script>

<style lang="scss" scoped>
@use 'parlassets/scss/breakpoints';
@use 'parlassets/scss/colors';

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
}

.bordertop {
  border-top: 1px solid colors.$background;
  padding: 10px 0;
  margin: 5px 0;
}

.bordertop0 {
  border-top: 1px solid colors.$background;
  padding: 0;
  margin: 0;
}

.bordertop,
.bordertop0 {
  flex: 1;
}

.poslanec h3 {
  font-weight: 400;
}

.verticalmember {
  width: 100%;

  .member_data {
    text-align: left;
    h4 {
      margin: 5px 0;
    }
    a {
      color: colors.$font-placeholder;
    }
  }

  .img-responsive {
    width: 40px;
    margin: 10px 15px 10px 0;
    @include breakpoints.respond-to(desktop) {
      margin-right: 25px;
    }
  }
}

.socialicon-container {
  margin-right: 10px;
}

.osnovne-informacije-poslanca {
  display: flex;
  flex-direction: column;
  height: 100%;

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
</style>
