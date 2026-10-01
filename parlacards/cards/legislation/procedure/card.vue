<template>
  <card-wrapper :header-config="headerConfig">
    <div class="legislation-procedure-card">
      <div v-if="results.procedure_type" class="procedure-info">
        <span>{{ $t(procedureTypeKey) }}</span>
        <svg xmlns="http://www.w3.org/2000/svg" fill="#333" viewBox="0 0 56 47">
          <path
            d="M55.025 37.391 33.346 2.945A6.28 6.28 0 0 0 28 0a6.28 6.28 0 0 0-5.346 2.945L.974 37.39c-1.235 1.962-1.298 4.344-.173 6.371C1.928 45.789 3.99 47 6.32 47h43.357c2.329 0 4.392-1.211 5.52-3.238s1.062-4.41-.173-6.37m-27.026 3.332a3.145 3.145 0 0 1-3.154-3.138 3.145 3.145 0 0 1 3.154-3.139 3.145 3.145 0 0 1 3.155 3.139 3.145 3.145 0 0 1-3.155 3.138m2.466-11.737A2.467 2.467 0 0 1 28 31.308a2.467 2.467 0 0 1-2.465-2.322l-.845-15.12a3.305 3.305 0 0 1 3.31-3.48c1.903 0 3.417 1.59 3.31 3.48z"
          />
        </svg>
      </div>
      <div class="procedure-timeline">
        <div class="considerations">
          <div
            v-for="(c, i) in allConsiderations"
            :class="{ consideration: true, 'consideration--future': c.future }"
            :style="`--this-anchor: --consideration-${i}; --next-anchor: --consideration-${i + 1};`"
          >
            <div class="consideration-icon-col">
              <div class="consideration-circle">
                <svg
                  v-if="c.future"
                  xmlns="http://www.w3.org/2000/svg"
                  fill="none"
                  viewBox="0 0 49 14"
                >
                  <circle
                    cx="6.667"
                    cy="6.667"
                    r="5.833"
                    stroke-width="1.667"
                  />
                  <circle
                    cx="24.167"
                    cy="6.667"
                    r="5.833"
                    stroke-width="1.667"
                  />
                  <circle
                    cx="41.667"
                    cy="6.667"
                    r="5.833"
                    stroke-width="1.667"
                  />
                </svg>
                <svg
                  v-else
                  xmlns="http://www.w3.org/2000/svg"
                  fill="none"
                  viewBox="0 0 46 37"
                >
                  <path
                    stroke-width="1.667"
                    d="M38.385.833c.302 0 .591.106.822.295l.095.087 5.188 5.202.001.001c.517.516.51 1.335.006 1.83L43.36 9.365l.017.003-25.629 25.644c-.275.266-.61.391-.928.391a1.3 1.3 0 0 1-.917-.381L1.218 20.337l-.005-.005-.088-.097c-.414-.5-.39-1.25.094-1.734V18.5l5.188-5.202c.47-.47 1.364-.47 1.835 0l7.99 7.99.588.589.59-.59L37.468 1.214c.243-.244.573-.381.917-.381Z"
                  />
                </svg>
              </div>
            </div>
            <div class="consideration-text-col">
              <div class="consideration-name">{{ c.name }}</div>
              <div class="consideration-timestamp">
                {{ formatDate(c.timestamp) }}
              </div>
            </div>
            <div class="consideration-connector">
              <div class="consideration-connector-line"></div>
            </div>
          </div>
        </div>
      </div>
    </div>
  </card-wrapper>
</template>

<script>
import common from '@/_mixins/common.js';
import links from '@/_mixins/links.js';
import { defaultHeaderConfig } from '@/_mixins/altHeaders.js';
import dateFormatter from '@/_helpers/dateFormatter.js';

export default {
  name: 'CardLegislationProcedure',
  mixins: [common, links],
  data() {
    const { cardData } = this.$root.$options.contextData;
    const results = cardData?.data?.results ?? {};

    return {
      results,
      headerConfig: defaultHeaderConfig(this, {
        heading: cardData?.data?.mandate?.description,
        // title: results?.legislation?.text,
      }),
    };
  },
  computed: {
    allConsiderations() {
      const curr = (this.results.considerations || []).map((c) => {
        return { ...c, future: false };
      });
      const future = (this.results.future_considerations || []).map((c) => {
        return { ...c, future: true };
      });
      return [...curr, ...future];
    },
    procedureTypeKey() {
      return `procedure-type.${this.results.procedure_type || 'unknown'}`;
    },
  },
  methods: {
    formatDate: dateFormatter,
  },
};
</script>

<style lang="scss" scoped>
@use 'sass:string';
@use 'parlassets/scss/breakpoints';
@use 'parlassets/scss/colors';

.legislation-procedure-card {
  display: flex;
  flex-direction: column;
  height: 100%;

  .procedure-info {
    display: flex;
    align-items: center;
    justify-content: space-between;
    width: 100%;
    background-color: colors.$background;
    font-weight: 500;
    padding: 1rem 1.25rem;

    svg {
      display: block;
      height: 2rem;
      margin-block: -0.5rem;
    }
  }

  .procedure-timeline {
    width: 100%;
    padding: 0 1rem;
    overflow-x: hidden;
    overflow-y: scroll;

    .considerations {
      position: relative;
      anchor-scope: --this-anchor, --next-anchor;
      display: flex;
      flex-direction: column;
      gap: 4rem;
      padding-block: 2rem;

      .consideration {
        display: flex;
        align-items: center;
        gap: 2rem;
        anchor-name: var(--this-anchor);

        .consideration-icon-col {
          flex-basis: 40px;
          flex-shrink: 0;

          .consideration-circle {
            display: grid;
            place-items: center;
            width: 40px;
            height: 40px;
            padding: 7px;
            border-radius: 50%;
            background-color: colors.$link-hover-background;
            border: 1px solid colors.$font-default;

            svg {
              width: 100%;
              height: 100%;
              fill: colors.$button-for;
              stroke: colors.$font-default;
            }
          }
        }

        .consideration-text-col {
          flex: 1;

          .consideration-name {
            font-size: 1.6rem;
            font-weight: 500;
          }

          .consideration-timestamp {
            font-family: Roboto Slab;
            font-size: 1.4rem;
          }
        }

        .consideration-connector {
          position: absolute;
          z-index: -1;
          top: anchor(center var(--this-anchor));
          bottom: anchor(center var(--next-anchor));
          left: 20px;
          transform: translateX(-50%);
          width: 8px;
          padding: 1px;
          border: 1px solid colors.$font-default;
          background-color: colors.$button-for;

          .consideration-connector-line {
            width: 100%;
            height: 100%;
          }
        }

        &:not(.consideration--future):has(+ .consideration--future) {
          .consideration-connector {
            background-color: colors.$background;

            .consideration-connector-line {
              background-image: url('data:image/svg+xml,%3Csvg xmlns="http://www.w3.org/2000/svg" width="4" height="8"%3E%3Crect width="4" height="4" fill="%23#{string.slice("#{colors.$button-for}", 2)}"/%3E%3C/svg%3E');
              background-repeat: repeat-y;
            }
          }
        }

        &.consideration--future {
          .consideration-circle {
            background-color: #fff;

            svg {
              fill: colors.$background;
            }
          }

          .consideration-connector {
            background-color: colors.$background;
          }
        }

        &:last-child {
          .consideration-connector {
            display: none;
          }
        }
      }
    }
  }
}
</style>
