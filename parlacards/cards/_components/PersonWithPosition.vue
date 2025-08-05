<template>
  <div class="verticalmember">
    <div class="row">
      <a :href="getPersonLink(person)" :title="getPersonName(person)">
        <img
          :src="getPersonPortrait(person)"
          class="img-circle img-responsive"
          :style="{ border: getPersonBorder(person) }"
        />
      </a>
      <div class="member_data">
        <h3>
          <a :href="getPersonLink(person)" class="funblue-light-hover">
            {{ getPersonName(person) }}
          </a>
        </h3>
        <h4>{{ positionTranslation }}</h4>
      </div>
    </div>
  </div>
</template>

<script>
import links from '@/_mixins/links.js';

export default {
  name: 'PersonWithPosition',
  mixins: [links],
  props: {
    person: {
      type: Object,
      required: true,
    },
    position: {
      type: String,
      required: true,
      validator: (value) => ['president', 'deputy', 'member'].includes(value),
    },
  },
  computed: {
    positionTranslation() {
      const form = this.person.preferred_pronoun === 'she' ? '--f' : '--m';
      if (this.position === 'president') {
        return this.$t(`party-leader${form}`);
      }
      if (this.position === 'deputy') {
        return this.$t(`deputy-leader${form}`);
      }
      return this.$t('member');
    },
  },
};
</script>

<style lang="scss" scoped>
@use 'parlassets/scss/breakpoints';
@use 'parlassets/scss/colors';

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

.verticalmember {
  width: 100%;

  .member_data {
    text-align: left;

    h3 {
      font-weight: 300;
    }

    h4 {
      margin: 5px 0;
    }
  }

  .img-responsive {
    width: 40px;
    height: 40px;
    margin: 10px 15px 10px 0;
    object-fit: cover;

    @include breakpoints.respond-to(desktop) {
      margin-right: 25px;
    }
  }
}
</style>
