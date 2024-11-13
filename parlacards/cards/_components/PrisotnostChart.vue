<template>
  <card-wrapper :header-config="headerConfig" @back-change="handleBackChange">
    <div ref="chart" class="prisotnost-chart"></div>
  </card-wrapper>
</template>

<script>
import * as d3 from 'd3';
import common from '@/_mixins/common.js';
import { personTitle, partyTitle } from '@/_mixins/titles.js';
import { personHeader, partyHeader } from '@/_mixins/altHeaders.js';
import { personOgImage, partyOgImage } from '@/_mixins/ogImages.js';
import {
  personOverviewContextUrl,
  partyOverviewContextUrl,
} from '@/_mixins/contextUrls.js';
import getD3Locale from '@/_i18n/d3locales.js';

export default {
  name: 'PrisotnostChart',
  mixins: [common],
  props: {
    type: {
      type: String,
      required: true,
      validator: (value) => ['person', 'party'].indexOf(value) > -1,
    },
    results: {
      type: Array,
      required: true,
    },
    person: {
      type: Object,
      default: () => ({}),
    },
    party: {
      type: Object,
      default: () => ({}),
    },
  },
  computed: {
    headerConfig() {
      if (this.type === 'person') {
        return personHeader.computed.headerConfig.call(this);
      }
      return partyHeader.computed.headerConfig.call(this);
    },
    translationKeys() {
      if (this.type === 'person') {
        const gender = this.person.preferred_pronoun === 'she' ? 'f' : 'm';
        return {
          present: this.$t(`present--${gender}`),
          absent: this.$t(`absent--${gender}`),
          noMandate: this.$t('no-term'),
          noData: this.$t('no-data'),
        };
      }
      return {
        present: this.$t(`present--plural`),
        absent: this.$t(`absent--plural`),
        noMandate: this.$t('no-term'),
        noData: this.$t('no-data'),
      };
    },
  },
  created() {
    (this.type === 'person' ? personTitle : partyTitle).created.call(this);
    (this.type === 'person' ? personOgImage : partyOgImage).created.call(this);
    (this.type === 'person'
      ? personOverviewContextUrl
      : partyOverviewContextUrl
    ).created.call(this);
  },
  mounted() {
    this.renderChart();
  },
  methods: {
    handleBackChange(newBack) {
      if (newBack === null) {
        this.$nextTick(this.renderChart);
      }
    },
    renderChart() {
      // empty the chart container
      this.$refs.chart.textContent = '';

      d3.timeFormatDefaultLocale(getD3Locale(this.$i18n.locale));

      const dateParser = d3.timeParse('%Y-%m-%d');
      const monthFormat = d3.timeFormat('%b %y');
      const monthFormatLong = d3.timeFormat('%B %Y');
      const formatMonth = (dateString) => monthFormat(dateParser(dateString));
      const formatMonthLong = (dateString) =>
        monthFormatLong(dateParser(dateString));

      const data = this.results
        .slice()
        .sort((a, b) => a.timestamp.localeCompare(b.timestamp))
        .map((obj) => {
          const present = Math.max(0, Math.round(obj.present)) || 0;
          const noMandate = Math.max(0, Math.round(obj.no_mandate)) || 0;
          const noData = Math.max(0, Math.round(obj.no_data)) || 0;
          const absent = 100 - (present + noMandate + noData);
          return {
            date: obj.timestamp,
            present,
            noMandate,
            noData,
            absent,
          };
        });

      const dataKeys = ['present', 'absent', 'noData', 'noMandate'];

      const series = d3
        .stack()
        .keys(dataKeys)(data)
        .map((d) => d.map((v) => ({ ...v, key: d.key })));

      const width = 940;
      const height = 544;
      const margin = { top: 10, right: 10, bottom: 40, left: 40 };

      const svg = d3
        .select(this.$refs.chart)
        .append('svg')
        .attr('viewBox', [0, 0, width, height]);

      // pattern for no data fill
      const pattern = svg
        .append('defs')
        .append('pattern')
        .attr('id', 'noDataPattern')
        .attr('width', 12)
        .attr('height', 12)
        .attr('patternUnits', 'userSpaceOnUse')
        .attr('patternTransform', 'rotate(-45)');
      pattern
        .append('rect')
        .attr('fill', '#8a8a8a')
        .attr('x', 0)
        .attr('y', 0)
        .attr('width', 12)
        .attr('height', 6);
      pattern
        .append('rect')
        .attr('fill', '#c8c8c8')
        .attr('x', 0)
        .attr('y', 6)
        .attr('width', 12)
        .attr('height', 6);

      const x = d3
        .scaleBand()
        .domain(data.map((d) => d.date))
        .range([margin.left, width - margin.right])
        .padding(0.1);

      // prevent x axis labels from touching by only showing some of them
      // dividing by 16 means it will show up to max 16 ticks
      const xValuesGap = Math.ceil(x.domain().length / 16);
      const xTickValues = x.domain().filter((d, i) => !(i % xValuesGap));

      const y = d3
        .scaleLinear()
        .domain([0, d3.max(series, (d) => d3.max(d, (d2) => d2[1]))])
        .rangeRound([height - margin.bottom, margin.top]);

      let tooltip;

      const tooltipHover = (rect) => {
        rect
          .on('mouseover', (e, d) => {
            svg
              .selectAll(`rect[data-time="${d.data.date}"]`)
              .classed('hovered', true);
            if (x(d.data.date) > 748) {
              tooltip.attr(
                'transform',
                `translate(${x(d.data.date) - 70},${y(80)})`,
              );
            } else {
              tooltip.attr(
                'transform',
                `translate(${x(d.data.date) + 108},${y(80)})`,
              );
            }

            tooltip.selectAll('text').remove();

            tooltip
              .append('text')
              .text(formatMonthLong(d.data.date))
              .style('fill', '#fff')
              .attr('text-anchor', 'start')
              .attr('x', -70)
              .attr('y', -18);

            let textTop = 10;
            dataKeys
              .slice()
              .reverse()
              .forEach((key) => {
                const value = d.data[key];
                const text = this.translationKeys[key];
                if (value > 0) {
                  tooltip
                    .append('text')
                    .text(`${text}`)
                    .style('fill', '#fff')
                    .attr('text-anchor', 'start')
                    .attr('x', -70)
                    .attr('y', textTop);
                  tooltip
                    .append('text')
                    .text(`${value} %`)
                    .style('fill', '#fff')
                    .attr('text-anchor', 'end')
                    .attr('x', 60)
                    .attr('y', textTop);
                  textTop += 18;
                }
              });

            tooltip.style('display', null);
          })
          .on('mouseout', (e, d) => {
            svg
              .selectAll(`rect[data-time="${d.data.date}"]`)
              .classed('hovered', false);
            tooltip.style('display', 'none');
          });
      };

      // bars
      svg
        .append('g')
        .selectAll('g')
        .data(series)
        .join('g')
        .selectAll('rect')
        .data((d) => d)
        .join('rect')
        .attr('class', (d) => `prisotnost-bar-${d.key}`)
        .attr('data-time', (d) => d.data.date)
        .attr('x', (d) => x(d.data.date))
        .attr('y', (d) => y(d[1]))
        .attr('height', (d) => y(d[0]) - y(d[1]))
        .attr('width', x.bandwidth())
        .call(tooltipHover);

      // bottom axis
      svg
        .append('g')
        .attr('class', 'axis-bottom')
        .attr('transform', `translate(0,${height - margin.bottom})`)
        .call(d3.axisBottom(x).tickValues(xTickValues).tickFormat(formatMonth))
        .call((g) => g.selectAll('.domain').remove());

      // left axis
      svg
        .append('g')
        .attr('class', 'axis-left')
        .attr('transform', `translate(${margin.left},0)`)
        .call(d3.axisLeft(y).tickFormat((s) => `${s} %`))
        .call((g) => g.selectAll('.domain').remove());

      tooltip = svg
        .append('g')
        .attr('class', 'chart-tooltip')
        .style('display', 'none');

      tooltip
        .append('rect')
        .attr('width', 140)
        .attr('height', 110)
        .attr('y', -35)
        .attr('x', -75)
        .style('rx', 3)
        .style('yx', 3);

      tooltip
        .append('rect')
        .attr('width', 130)
        .attr('height', 1.5)
        .attr('y', -9)
        .attr('x', -70)
        .style('fill', '#fff');
    },
  },
};
</script>

<style lang="scss" scoped>
@use 'parlassets/scss/colors';

.prisotnost-chart :deep(svg) {
  .tick line {
    stroke-width: 1;
    stroke: colors.$font-placeholder;
  }

  .tick text {
    font-size: 10px;
  }

  .axis-bottom .tick text {
    font-size: 12px;
    transform: translate(-4px, 6px) rotate(-25deg);
  }

  .prisotnost-bar-present {
    fill: colors.$time-presence-present-passive;

    &.hovered {
      fill: colors.$time-presence-present-active;
    }
  }

  .prisotnost-bar-absent {
    fill: colors.$time-presence-absent-passive;

    &.hovered {
      fill: colors.$time-presence-absent-active;
    }
  }

  .prisotnost-bar-noMandate {
    fill: colors.$time-presence-no-term-passive;
    opacity: 0.4;

    &.hovered {
      opacity: 0.8;
    }
  }

  .prisotnost-bar-noData {
    fill: url(#noDataPattern);
    opacity: 0.4;

    &.hovered {
      opacity: 0.8;
    }
  }

  .chart-tooltip rect {
    border: 0px;
    background-color: colors.$font-placeholder;
    border-radius: 3px;
    padding: 2px 10px;
    color: colors.$white;
  }
}
</style>
