<template>
  <div ref="chart" class="time-chart"></div>
</template>

<script>
import * as d3 from 'd3';
import getD3Locale from '@/_i18n/d3locales.js';

export default {
  name: 'TimeChart',
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
      const dateFormat = d3.timeFormat('%B %Y');

      const width = 940;
      const height = 420;
      const margin = { top: 35, right: 20, bottom: 25, left: 20 };

      const svg = d3
        .select(this.$refs.chart)
        .append('svg')
        .attr('viewBox', [0, 0, width, height]);

      const dataDates = this.data
        .map((d) => d.date)
        .filter((d, i, a) => {
          const maxTicks = 24;
          const factor = Math.ceil(a.length / maxTicks);
          if (i === 0 || i === a.length - 1) {
            return true;
          }
          return i % factor === 0;
        });

      const extent = d3.extent(dataDates);

      const x = d3
        .scaleTime()
        .domain(extent)
        .range([margin.left, width - margin.right]);

      const y = d3
        .scaleLinear()
        .domain([0, d3.max(this.data, (d) => d.value)])
        .rangeRound([height - margin.bottom, margin.top]);

      // bottom axis
      svg
        .append('g')
        .attr('class', 'axis-bottom')
        .attr('transform', `translate(0,${height - margin.bottom})`)
        .call(d3.axisBottom(x).tickValues(dataDates).tickFormat(monthFormat))
        .call((g) => g.selectAll('.domain').remove());

      const line = d3
        .line()
        .x((d) => x(d.date))
        .y((d) => y(d.value));

      // line
      svg
        .append('g')
        .append('path')
        .datum(this.data)
        .attr('fill', 'none')
        .attr('stroke', '#000')
        .attr('stroke-width', 2)
        .attr('d', line);

      const bisectDate = d3.bisector((d) => d.date).left;

      let dots;
      let tooltip;
      let tooltipLine;
      let lastTooltipDatum = null;
      let lastTooltipWidth = 0;

      const tooltipHover = (elem) => {
        elem
          .on('mousemove', (e) => {
            const [pointerX, pointerY] = d3.pointer(e, elem.node());
            const hoveredDate = x.invert(pointerX);
            const i = bisectDate(this.data, hoveredDate);
            if (i >= this.data.length) {
              return;
            }

            // work out which date value is closest
            const [index, d, lineX] = (() => {
              const d1 = this.data[i];
              const lineX1 = x(d1.date);
              if (i === 0) {
                return [i, d1, lineX1];
              }
              const d0 = this.data[i - 1];
              const lineX0 = x(d0.date);
              if (Math.abs(pointerX - lineX0) < Math.abs(pointerX - lineX1)) {
                return [i - 1, d0, lineX0];
              }
              return [i, d1, lineX1];
            })();

            if (lastTooltipDatum !== d) {
              lastTooltipDatum = d;

              const bbox = tooltip
                .select('text')
                .text(`${dateFormat(d.date)} | ${d.value}`)
                .node()
                .getBBox();

              const padX = 8;
              const padY = 4;

              lastTooltipWidth = tooltip
                .select('rect')
                .attr('x', bbox.x - padX)
                .attr('y', bbox.y - padY * 1.25)
                .attr('width', bbox.width + padX * 2)
                .attr('height', bbox.height + padY * 2)
                .node()
                .getBBox().width;

              tooltipLine.attr('x1', lineX).attr('x2', lineX);

              dots
                .attr('r', (d_, idx) => (idx === index ? 4 : 2))
                .classed('hovered', (d_, idx) => idx === index);
            }

            const xPos = Math.max(
              0 + lastTooltipWidth / 2,
              Math.min(x(lastTooltipDatum.date), width - lastTooltipWidth / 2),
            );
            const yPos = Math.max(
              margin.top,
              Math.min(height - margin.bottom, pointerY),
            );

            tooltip.attr('transform', `translate(${xPos},${yPos - 15})`);
          })
          .on('mouseover', () => {
            tooltip
              .interrupt()
              .transition()
              .duration(150)
              .style('opacity', 1)
              .style('display', null);
            tooltipLine.style('display', null);
          })
          .on('mouseout', () => {
            tooltip
              .transition()
              .duration(150)
              .style('opacity', 0)
              .transition()
              .style('display', 'none');
            tooltipLine.style('display', 'none');
            dots.attr('r', 2).classed('hovered', false);
            lastTooltipDatum = null;
          });
      };

      tooltipLine = svg
        .append('line')
        .attr('x1', -100)
        .attr('x2', -100)
        .attr('y1', margin.top - 20)
        .attr('y2', height - margin.bottom)
        .style('stroke-width', 1)
        .style('stroke', '#888')
        .style('stroke-dasharray', '4 4')
        .style('fill', 'none');

      // dots
      dots = svg
        .append('g')
        .selectAll('.dot')
        .data(this.data)
        .join('circle')
        .attr('class', 'dot')
        .attr('r', 2)
        .attr('cx', (d) => x(d.date))
        .attr('cy', (d) => y(d.value));

      tooltip = svg
        .append('g')
        .attr('class', 'time-tooltip')
        .style('pointer-events', 'none')
        .style('user-select', 'none')
        .style('display', 'none');

      tooltip.append('rect').attr('fill', '#000').attr('rx', 3);
      tooltip
        .append('text')
        .attr('fill', '#fff')
        .attr('font-size', 14)
        .attr('text-anchor', 'middle');

      svg.call(tooltipHover);
    },
  },
};
</script>

<style lang="scss" scoped>
@use 'parlassets/scss/colors';

.time-chart :deep(svg) {
  path {
    stroke: colors.$time-chart-passive;
  }

  text {
    font-family: Roboto, sans-serif;
  }

  .dot {
    fill: colors.$time-chart-passive;

    &.hovered {
      fill: colors.$time-chart-active;
    }
  }
}
</style>
