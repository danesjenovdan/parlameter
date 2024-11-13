<template>
  <svg viewBox="0 0 2 2" xmlns="http://www.w3.org/2000/svg">
    <defs>
      <mask :id="`donut-hole${uid}`">
        <circle cx="1" cy="1" r="1" fill="white" />
        <circle cx="1" cy="1" r="0.7" fill="black" />
      </mask>
    </defs>
    <path
      v-for="sector in sectors"
      :key="sector.class"
      :class="sector.class"
      :d="`M${sector.L},${sector.L} L${sector.L},0 A${sector.L},${sector.L} 0 ${sector.arcSweep},1 ${sector.X}, ${sector.Y} z`"
      :transform="`rotate(${sector.R}, ${sector.L}, ${sector.L})`"
      :mask="`url(#donut-hole${uid})`"
    />
  </svg>
</template>

<script>
import { uniqueId } from 'lodash-es';

export default {
  name: 'DonutChart',
  props: {
    sectionData: {
      type: Array,
      default: () => [],
    },
  },
  data() {
    return {
      size: 100,
      uid: uniqueId('donut'),
    };
  },
  computed: {
    sectors() {
      let a = 0; // Angle
      let aRad = 0; // Angle in Rad
      let aCalc = 0;
      let arcSweep = 0;
      let z = 0; // Size z
      let x = 0; // Side x
      let y = 0; // Side y
      let X = 0; // SVG X coordinate
      let Y = 0; // SVG Y coordinate
      let R = 0; // Rotation

      return this.sectionData.map((item) => {
        a = 360 * item.percentage;
        if (a === 360) {
          a = 359.999;
        }
        aCalc = a > 180 ? 360 - a : a;
        aRad = (aCalc * Math.PI) / 180;
        z = Math.sqrt(2 - 2 * Math.cos(aRad));
        if (aCalc <= 90) {
          x = Math.sin(aRad);
        } else {
          x = Math.sin(((180 - aCalc) * Math.PI) / 180);
        }

        y = Math.sqrt(z * z - x * x);
        Y = y;

        if (a <= 180) {
          X = 1 + x;
          arcSweep = 0;
        } else {
          X = 1 - x;
          arcSweep = 1;
        }

        const oldR = R;
        R += a;

        return {
          class: item.type,
          arcSweep,
          L: 1,
          X,
          Y,
          R: oldR,
        };
      });
    },
  },
};
</script>

<style lang="scss" scoped>
@use 'parlassets/scss/colors';

path {
  &.for {
    fill: colors.$button-for;
  }

  &.against {
    fill: colors.$button-against;
  }

  &.abstain {
    fill: colors.$button-abstained;
  }

  &.absent {
    fill: colors.$button-absent;
  }
}
</style>
