<template>
  <div class="seats-component">
    <div class="seats">
      <div
        ref="seatTooltip"
        :class="['seat-tooltip', { visible: tooltipVisible }]"
      ></div>
      <svg xmlns="http://www.w3.org/2000/svg" :viewBox="viewBox">
        <g>
          <circle
            v-for="(circle, i) in seats"
            :key="circle.id"
            class="clickable-seat"
            :cx="circle.cx"
            :cy="circle.cy"
            :r="dotSize"
            :data-index="i"
            :data-id="circle.id"
            :fill="getDotColor(i)"
            :title="getTooltipText(i)"
            @mouseout="onMouseOut(i)"
            @mouseover="onMouseOver(i)"
            @click="openLink(getPersonLink(seatIdxToMember[i]))"
          ></circle>
        </g>
      </svg>
    </div>
    <div class="legend">
      <div v-for="group in seatData" :key="group.label" class="legend-item">
        <span
          class="legend-dot"
          :style="{ backgroundColor: group.color }"
        ></span>
        <a
          :href="getPartyLink(group)"
          class="legend-label funblue-light-hover"
          >{{ group.acronym }}</a
        >
        <span class="legend-count">({{ group.seats }})</span>
      </div>
    </div>
  </div>
</template>

<script>
import links from '@/_mixins/links.js';

function generateSeats(count, opts = {}) {
  const { baseRadius, rowGap, seatArcLength, arcDegrees, maxRows = 12 } = opts;

  const viewWidth = 1000;
  const viewHeight = 1000;
  const centerX = viewWidth / 2;
  const centerY = viewHeight / 2;

  const arcRad = (arcDegrees * Math.PI) / 180;

  const capacityForRow = (r) => {
    const radius = baseRadius + r * rowGap;
    return Math.max(1, Math.floor((arcRad * radius) / seatArcLength));
  };

  // find minimal number of rows to fit count
  let rows = 1;
  while (rows <= maxRows) {
    let total = 0;
    for (let r = 0; r < rows; r++) total += capacityForRow(r);
    if (total >= count) break;
    rows++;
  }

  if (rows > maxRows) {
    throw new Error(
      `Cannot fit ${count} seats in ${maxRows} rows. Consider adjusting parameters.`,
    );
  }

  // Distribute count seats across rows proportional to arc circumference so
  // every row always fills the full arc from left edge to right edge.
  const radii = Array.from({ length: rows }, (_, r) => baseRadius + r * rowGap);
  const totalRadius = radii.reduce((a, b) => a + b, 0);
  const exact = radii.map((radius) => (count * radius) / totalRadius);
  const allocated = exact.map((v) => Math.floor(v));
  let totalAllocated = allocated.reduce((a, b) => a + b, 0);

  // Largest Remainder Method: hand out leftover seats to rows with biggest remainders
  const remainders = exact
    .map((v, i) => ({ i, frac: v - Math.floor(v) }))
    .sort((a, b) => b.frac - a.frac);
  for (let k = 0; totalAllocated < count; k++, totalAllocated++) {
    allocated[remainders[k].i]++;
  }

  // Generate all positions for every row, tagged with their normalized angular
  // position (0 = leftmost, 1 = rightmost within that row).
  const allPositions = [];
  for (let r = 0; r < rows; r++) {
    const radius = radii[r];
    const cap = allocated[r];
    const angleStep = cap > 1 ? arcRad / (cap - 1) : 0;
    const startAngle = -Math.PI / 2 - arcRad / 2;

    for (let i = 0; i < cap; i++) {
      const angle = startAngle + i * angleStep;
      const norm = cap > 1 ? i / (cap - 1) : 0.5;
      allPositions.push({
        norm,
        r,
        x: Math.round(centerX + radius * Math.cos(angle)),
        y: Math.round(centerY + radius * Math.sin(angle)),
      });
    }
  }

  // Sort left-to-right so consecutive seat indices form a wedge, not a band.
  // Secondary sort by row (inner first) for seats at the same angular position.
  allPositions.sort((a, b) => a.norm - b.norm || a.r - b.r);

  return allPositions.map((pos, idx) => ({
    id: `c${idx + 1}`,
    cx: pos.x,
    cy: pos.y,
  }));
}

export default {
  name: 'Seats',
  mixins: [links],
  props: {
    seatData: { type: Array, default: () => [] },
    seatCount: { type: Number, default: 90 },
    baseRadius: { type: Number, default: 180 },
    rowGap: { type: Number, default: 75 },
    seatArcLength: { type: Number, default: 70 },
    arcDegrees: { type: Number, default: 320 },
    dotSize: { type: Number, default: 25 },
  },
  data() {
    const seatIdxToMember = {};
    let seatIdx = 0;
    for (const group of this.seatData) {
      const memberGroup = { ...group, members: undefined };
      for (const member of group.members) {
        seatIdxToMember[seatIdx] = { ...member, group: memberGroup };
        seatIdx++;
      }
    }

    return {
      seats: generateSeats(this.seatCount, {
        baseRadius: this.baseRadius,
        rowGap: this.rowGap,
        seatArcLength: this.seatArcLength,
        arcDegrees: this.arcDegrees,
      }),
      seatIdxToMember,
      tooltipVisible: false,
    };
  },
  computed: {
    viewBox() {
      if (!this.seats.length) return '0 0 1000 1000';
      const r = this.dotSize * 1.25; // prevent clipping at the edges
      const xs = this.seats.map((s) => s.cx);
      const ys = this.seats.map((s) => s.cy);
      const minX = Math.min(...xs) - r;
      const minY = Math.min(...ys) - r;
      const maxX = Math.max(...xs) + r;
      const maxY = Math.max(...ys) + r;
      return `${minX} ${minY} ${maxX - minX} ${maxY - minY}`;
    },
  },
  methods: {
    getDotColor(seatIdx) {
      const member = this.seatIdxToMember[seatIdx];
      const group = member ? member.group : null;
      return group ? group.color : '#ccc';
    },
    getTooltipLines(seatIdx) {
      const member = this.seatIdxToMember[seatIdx];
      if (!member) return '';
      const group = member.group;
      if (!group) return member.name || '';
      return [`${member.name}`, `${group.acronym || group.name}`];
    },
    getTooltipText(seatIdx) {
      return this.getTooltipLines(seatIdx).join(' - ');
    },
    onMouseOut() {
      this.tooltipVisible = false;
    },
    onMouseOver(seatIdx) {
      const tooltip = this.$refs.seatTooltip;
      if (!tooltip) return;
      const member = this.seatIdxToMember[seatIdx];
      if (!member) return;
      const circle = this.$el.querySelector(`circle[data-index="${seatIdx}"]`);
      if (!circle) return;
      tooltip.innerHTML = this.getTooltipLines(seatIdx)
        .map((line, i) => {
          if (i === 0) return `<div class="seat-tooltip-name">${line}</div>`;
          return `<div class="seat-tooltip-group">${line}</div>`;
        })
        .join('');
      tooltip.style.left = '';
      tooltip.style.top = '';
      const tooltipRect = tooltip.getBoundingClientRect();
      const rect = circle.getBoundingClientRect();
      const parentRect = this.$el.getBoundingClientRect();

      // put the tooltip above the circle, centered horizontally, but offset it
      // to the left or right if it would go off the edge of the parent container
      const tooltipX =
        Math.min(
          Math.max(
            rect.left + rect.width / 2 - tooltipRect.width / 2,
            parentRect.left,
          ),
          parentRect.right - tooltipRect.width,
        ) - parentRect.left;
      const tooltipY = rect.top - parentRect.top;
      tooltip.style.left = `${tooltipX}px`;
      tooltip.style.top = `${tooltipY - 4}px`;
      this.tooltipVisible = true;
    },
    openLink(url) {
      if (!url) return;
      window.location.href = url;
    },
  },
};
</script>

<style lang="scss" scoped>
@use 'parlassets/scss/colors';

.seats-component {
  position: relative;

  .seats {
    margin-top: 0;
    margin-inline: 10px;

    svg {
      width: 100%;
      height: auto;
      max-height: 280px;
    }

    .clickable-seat {
      cursor: pointer;

      &:hover {
        stroke: colors.$link;
        stroke-width: 6px;
      }
    }

    .seat-tooltip {
      position: absolute;
      top: 0;
      left: 0;
      transform: translateY(-100%);
      background-color: colors.$font-default;
      color: colors.$white;
      padding: 4px 8px;
      border-radius: 4px;
      font-size: 14px;
      text-align: center;
      white-space: pre-line;
      pointer-events: none;
      opacity: 0;
      transition: opacity 0.25s ease-out;

      &.visible {
        opacity: 1;
      }

      :deep(.seat-tooltip-name) {
        font-weight: 500;
      }

      :deep(.seat-tooltip-group) {
        font-size: 12px;
      }
    }
  }

  .legend {
    display: flex;
    flex-wrap: wrap;
    gap: 8px 16px;
    justify-content: center;
    margin-top: 20px;
  }

  .legend-item {
    display: flex;
    align-items: center;
    gap: 6px;
    font-size: 14px;
    font-weight: 500;
    line-height: 1;
  }

  .legend-dot {
    display: inline-block;
    width: 14px;
    height: 14px;
    margin-bottom: 3px;
    border-radius: 50%;
    flex-shrink: 0;
  }
}
</style>
