<template>
  <div ref="chart" class="time-bar-chart"></div>
</template>

<script>
import * as d3 from 'd3';
import getD3Locale from '@/_i18n/d3locales.js';

export default {
  name: 'TimeBarChart',
  props: {
    data: {
      type: Array,
      default: () => [],
    },
  },
  watch: {
    data() {
      this.$nextTick(this.renderChart);
    },
  },
  mounted() {
    this.renderChart();
  },
  methods: {
    renderChart() {
      // empty the chart container
      this.$refs.chart.textContent = '';

      d3.timeFormatDefaultLocale(getD3Locale(this.$i18n.locale));

      const monthFormat = d3.timeFormat('%b %y');

      const width = 940;
      const height = 420;
      const margin = { top: 35, right: 20, bottom: 25, left: 20 };

      const svg = d3
        .select(this.$refs.chart)
        .append('svg')
        .attr('viewBox', [0, 0, width, height]);

      const x = d3
        .scaleBand()
        .domain(this.data.map((d) => d.date))
        .range([margin.left, width - margin.right])
        .padding(0.1);

      const y = d3
        .scaleLinear()
        .domain([0, d3.max(this.data, (d) => d.value)])
        .rangeRound([height - margin.bottom, margin.top]);

      // bottom axis
      svg
        .append('g')
        .attr('class', 'axis-bottom')
        .attr('transform', `translate(0,${height - margin.bottom})`)
        .call(d3.axisBottom(x).tickFormat(monthFormat))
        .call((g) => g.selectAll('.domain').remove());

      // bars
      svg
        .append('g')
        .selectAll('.bar')
        .data(this.data)
        .join('rect')
        .attr('class', 'bar')
        .attr('x', (d) => x(d.date))
        .attr('y', (d) => y(d.value))
        .attr('height', (d) => y(0) - y(d.value))
        .attr('width', x.bandwidth());

      // values
      svg
        .append('g')
        .selectAll('.value')
        .data(this.data)
        .join('text')
        .attr('class', 'value')
        .text((d) => d.value)
        .attr('x', (d) => x(d.date) + x.bandwidth() / 2)
        .attr('y', (d) => y(d.value) - 5)
        .attr('text-anchor', 'middle')
        .attr('fill', '#000')
        .style('cursor', 'default');
    },
  },
};
</script>

<style lang="scss" scoped>
@use 'parlassets/scss/colors';

.time-bar-chart :deep(svg) {
  .bar {
    fill: colors.$time-chart-passive;
  }
}
</style>
