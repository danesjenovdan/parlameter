<template>
  <card-wrapper :header-config="headerConfig">
    <div class="legislation">
      <p-tabs :start-tab="selectedTab">
        <p-tab :label="$t('under-consideration')">
          <div class="row">
            <div
              v-for="legislation in inProcedure"
              :key="legislation.epa"
              class="col-xs-12 col-sm-6 legislation__wrapper"
            >
              <a
                :href="getLegislationLink(legislation)"
                class="legislation__single"
              >
                <div class="icon">
                  <div class="img-circle circle">
                    <img
                      v-if="legislation.icon"
                      :src="`${slugs.urls.cdn}/icons/legislation/${legislation.icon}`"
                    />
                  </div>
                </div>
                <div class="text">
                  {{ legislation.text }}
                </div>
              </a>
            </div>
          </div>
        </p-tab>
        <p-tab :label="$t('recently-passed')">
          <div class="legislation row">
            <div
              v-for="legislation in accepted"
              :key="legislation.epa"
              class="col-sm-6 legislation__wrapper"
            >
              <a
                :href="getLegislationLink(legislation)"
                class="legislation__single"
              >
                <div class="icon">
                  <div class="img-circle circle">
                    <img
                      v-if="legislation.icon"
                      :src="`${slugs.urls.cdn}/icons/legislation/${legislation.icon}`"
                    />
                  </div>
                </div>
                <div class="text">
                  {{ legislation.text }}
                </div>
              </a>
            </div>
          </div>
        </p-tab>
      </p-tabs>
      <div class="legislation__all">
        <a
          v-t="'all-legislation'"
          :href="getLegislationListLink()"
          class="legislation-link-icon funblue-light-hover"
        ></a>
      </div>
    </div>
  </card-wrapper>
</template>

<script>
import common from '@/_mixins/common.js';
import links from '@/_mixins/links.js';
import { defaultHeaderConfig } from '@/_mixins/altHeaders.js';
import PTab from '@/_components/Tab.vue';
import PTabs from '@/_components/Tabs.vue';

export default {
  name: 'CardMiscPromotedLegislation',
  components: {
    PTab,
    PTabs,
  },
  mixins: [common, links],
  cardInfo: {
    doubleWidth: true,
  },
  data() {
    const { cardState, cardData } = this.$root.$options.contextData;

    return {
      inProcedure: cardData?.data?.in_procedure || [],
      accepted: cardData?.data?.accepted || [],
      selectedTab: cardState?.selectedTab || 0,
      headerConfig: defaultHeaderConfig(this),
    };
  },
};
</script>

<style lang="scss" scoped>
@use 'parlassets/scss/breakpoints';
@use 'parlassets/scss/colors';

.legislation {
  overflow: hidden;

  .tab-content {
    margin-top: 15px;
    overflow-y: auto;
    height: 420px;
  }

  &__single {
    background: colors.$background;
    color: colors.$font-default;
    display: flex;
    align-items: center;
    height: 125px;
    padding: 13px 12px 11px;
    text-decoration: none;

    .text {
      $line-height: 18px;
      line-height: $line-height;
      font-weight: 300;
      font-size: 14px;
      overflow: hidden;
      max-height: $line-height * 4;
    }

    .circle {
      height: 101px;
      width: 102px;
      background-color: colors.$white;
      padding: 20px;
    }

    .icon {
      margin-right: 32px;
    }

    &:hover {
      color: colors.$link;
      background-color: colors.$link-hover-background;
    }

    &:focus,
    &:active,
    &:visited {
      text-decoration: none;
    }
  }

  &__wrapper {
    margin-bottom: 15px;
    position: relative;

    &:nth-child(odd) {
      @include breakpoints.respond-to(desktop) {
        padding-right: 7px;
      }
    }

    &:nth-child(even) {
      @include breakpoints.respond-to(desktop) {
        padding-left: 7px;
      }
    }
  }

  &__all {
    position: absolute;
    left: 0;
    bottom: 0;
    padding: 4px 20px 15px 20px;
    background: colors.$white;
    width: 100%;

    a {
      padding-left: 22px;
      font-size: 14px;
      font-weight: 400;
      text-transform: uppercase;
    }
  }
}
</style>
