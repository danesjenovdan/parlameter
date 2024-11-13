<template>
  <card-wrapper :header-config="headerConfig" max-height>
    <div class="media-reports">
      <div class="media-report-headers">
        <div>{{ $t('media') }}</div>
        <div>{{ $t('media-reports') }}</div>
      </div>
      <div
        v-for="(reports, medium) in groupedReports"
        :key="medium"
        class="media-report"
      >
        <div class="name">{{ reports[0].medium.name }}</div>
        <div class="material">
          <div v-for="report in reports" :key="report.url" class="link">
            <a :href="report.url" class="funblue-light-hover" target="_blank">
              {{ report.title }}
            </a>
          </div>
        </div>
      </div>
    </div>
  </card-wrapper>
</template>

<script>
import { groupBy, orderBy } from 'lodash-es';
import common from '@/_mixins/common.js';
import { personOverviewContextUrl } from '@/_mixins/contextUrls.js';
import { personTitle } from '@/_mixins/titles.js';
import { personHeader } from '@/_mixins/altHeaders.js';
import { personOgImage } from '@/_mixins/ogImages.js';

export default {
  name: 'CardPersonMediaReports',
  mixins: [
    common,
    personOverviewContextUrl,
    personTitle,
    personHeader,
    personOgImage,
  ],
  cardInfo: {
    doubleWidth: true,
  },
  data() {
    const { cardData } = this.$root.$options.contextData;

    return {
      mediaReports: cardData?.data?.results || [],
    };
  },
  computed: {
    groupedReports() {
      // first sort all reports by medium order
      const sortedReports = orderBy(
        this.mediaReports,
        ['medium.order', 'report_date'],
        ['asc', 'desc'],
      );
      // because objects keys are guarantied to be in insertion order in js
      // and we sorted reports, groupBy will be ordered correctly
      return groupBy(sortedReports, (report) => report.medium.url);
    },
  },
};
</script>

<style lang="scss" scoped>
@use 'parlassets/scss/breakpoints';
@use 'parlassets/scss/colors';

.media-reports {
  .media-report-headers,
  .media-report {
    display: flex;

    > div {
      flex: 1;
      padding: 0 15px;
    }
  }

  .media-report-headers {
    color: colors.$font-default;
    font-size: 14px;
    font-weight: 500;
    text-transform: uppercase;
    white-space: nowrap;
  }

  .media-report {
    background: colors.$background;
    margin: 12px 0;

    > div {
      padding: 15px;

      &:nth-child(2) {
        border-left: 2px solid colors.$font-placeholder;
      }
    }

    .name {
      font-size: 14px;
      line-height: 20px;
      font-weight: 300;
      font-family: 'Roboto Slab', serif;
    }

    .material {
      .link {
        display: block;

        &:not(:last-child) {
          margin-bottom: 14px;
        }
      }
    }
  }
}

.agenda-links {
  display: flex;
  flex-wrap: wrap;
  gap: 12px;
  margin: 16px 0;

  .link {
    display: block;

    a {
      display: block;
      font-size: 16px;
      font-weight: 300;
      line-height: 30px;
      padding: 10px 30px;
      color: colors.$white;
      border: none;
      background-color: colors.$tab-passive;

      &:hover {
        color: colors.$white;
        background-color: colors.$tab-hover;
        text-decoration: none;
      }

      @include breakpoints.respond-to(mobile) {
        font-size: 14px;
        padding: 6px 16px;
      }
    }

    .nav-icon {
      background-size: 24px 100%;
      background-repeat: no-repeat;
      background-position: 24px center;
      padding-left: 60px;

      @include breakpoints.respond-to(mobile) {
        padding-left: 40px;
        background-size: 18px 100%;
        background-position: 14px center !important;
      }
    }

    .nav-icon-transcripts {
      background-image: url('#{get-parlassets-url()}/icons/navigation/transcripts.svg');
      background-size: 29px 100%;
      background-position: 21px center;

      @include breakpoints.respond-to(mobile) {
        background-size: 22px 100%;
      }
    }
  }
}
</style>
