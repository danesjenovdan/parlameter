<template>
  <div class="excerpt">
    <div
      v-if="icon"
      :class="{ 'show-parent': showParent }"
      class="icon-container"
    >
      <div
        :style="{
          'background-image': `url('${slugs.urls.cdn}/icons/legislation/${icon}')`,
        }"
        class="icon"
      />
    </div>
    <div
      v-if="content || content.length !== 0"
      :class="{ 'show-parent': showParent }"
      class="rich-text"
    >
      <!-- eslint-disable-next-line vue/no-v-html -->
      <div class="text-container" v-html="content"></div>
    </div>
    <div v-else class="no-abstract">
      <p v-t="'no-abstract'"></p>
    </div>
    <div v-if="showParent && mainLaw?.epa" class="metacontainer">
      <hr />
      <div class="metadata">
        <div class="main-law-label">Matični zakon:</div>
        <div class="main-law-name">
          <a :href="mainLaw?.link">{{ mainLaw.name }}</a>
        </div>
      </div>
    </div>
  </div>
</template>

<script>
export default {
  name: 'Excerpt',
  props: {
    content: {
      type: String,
      required: true,
    },
    mainLaw: {
      type: Object,
      default: () => ({}),
    },
    showParent: {
      type: Boolean,
      default: true,
    },
    icon: {
      type: String,
      default: '',
    },
  },
  data() {
    return {
      slugs: this.$root.slugs,
    };
  },
};
</script>

<style lang="scss" scoped>
@use 'parlassets/scss/breakpoints';
@use 'parlassets/scss/colors';

.excerpt {
  display: flex;
  flex-wrap: no-wrap;
  font-size: 13px;
  font-family: 'Roboto Slab', serif;
  font-weight: 300;
  line-height: 1.5em;
  margin: 12px 0;
  padding: 40px;
  background: colors.$background;
  height: 442px;
  position: relative;

  @include breakpoints.respond-to(mobile) {
    padding: 20px;
  }

  .icon-container {
    display: flex;

    @include breakpoints.respond-to(mobile) {
      display: none;
    }

    &.show-parent {
      max-height: 349px;
    }

    .icon {
      display: block;
      flex: 1;
      background-position: center;
      background-repeat: no-repeat;
      background-size: 65%;
      width: 100px;
      height: 100px;
      background-color: colors.$white;
      border-radius: 50%;
      align-self: center;
    }
  }

  .rich-text {
    overflow-x: hidden;
    overflow-y: auto;
    padding: 0 40px;
    max-height: 360px;
    display: flex;
    margin: auto;
    width: 100%;

    @include breakpoints.respond-to(mobile) {
      padding: 0 20px 0 10px;
      height: 320px;
    }

    &.show-parent {
      max-height: 320px;

      @include breakpoints.respond-to(mobile) {
        padding: 0;
        min-height: 320px;
      }
    }

    .text-container {
      width: 100%;

      :deep(p) {
        flex: 2;
        font-size: 18px;
        border-bottom: 1px solid colors.$font-placeholder;
        margin-bottom: 0;
        padding-top: 1em;
        padding-bottom: 1em;

        &:empty {
          display: none;
        }

        > br:only-child {
          display: none;
        }
      }

      :deep(ul) {
        padding-left: 0;
        margin-bottom: 1em;
        font-size: 14px;

        li {
          list-style-type: none;
          padding-left: 20px;
          padding-top: 1em;
          padding-bottom: 1em;
          border-bottom: 1px solid colors.$font-placeholder;

          &:last-child {
            border-bottom: none !important;
          }

          &::before {
            content: '';
            display: inline-block;
            width: 10px;
            height: 10px;
            background-image: url('#{get-parlassets-url()}/icons/puscica-izvlecki.svg');
            background-size: contain;
            margin-right: 5px;
            margin-left: -18px;
          }
        }
      }
    }
  }
}

hr {
  background: colors.$font-placeholder;
  height: 1px;
  margin: 10px 0 0 0;
}

.metacontainer {
  position: absolute;
  width: calc(100% - 80px);
  bottom: 10px;
  background: colors.$background;

  .metadata {
    font-size: 14px;
    @include breakpoints.respond-to(desktop) {
      display: flex;
    }

    .main-law-label {
      background-image: url('#{get-parlassets-url()}/icons/zakon.svg');
      background-size: 20px 19px;
      background-repeat: no-repeat;
      font-family: Roboto, sans-serif;
      font-weight: 300;
      margin-top: 12px;
      padding-left: 30px;
      width: 130px;
    }

    .main-law-name {
      flex: 1;
      margin-top: 12px;
    }
  }
}

.no-abstract {
  font-family: 'Roboto Slab', serif;
  text-align: center;
  font-size: 16px;
  color: colors.$font-default;
  width: 100%;
  font-style: italic;
  padding-bottom: 40px;

  p {
    max-width: 150px;
    margin: auto;
    margin-top: 18px;
    font-size: 13px;
  }

  &::before {
    content: '';
    width: 70px;
    height: 70px;
    position: relative;
    margin: auto;
    margin-top: 100px;
    display: block;
    background-image: url('#{get-parlassets-url()}/icons/missing-excerpt.svg');
    background-repeat: no-repeat;
    background-position: center;
    background-size: contain;
  }
}
</style>
