<template>
  <div class="excerpt">
    <div class="rich-text">
      <!-- eslint-disable-next-line vue/no-v-html -->
      <div v-if="isMarkdown" class="markdown-content" v-html="mdContent"></div>
      <!-- eslint-disable-next-line vue/no-v-html -->
      <div v-else class="text-container" v-html="content"></div>
    </div>
  </div>
</template>

<script>
import { Remarkable } from 'remarkable';

const md = new Remarkable();

export default {
  name: 'Excerpt',
  props: {
    content: {
      type: String,
      required: true,
    },
    isMarkdown: {
      type: Boolean,
      default: false,
    },
  },
  computed: {
    mdContent() {
      return md.render(this.content);
    },
  },
};
</script>

<style lang="scss" scoped>
@use 'parlassets/scss/breakpoints';
@use 'parlassets/scss/colors';

.excerpt {
  display: flex;
  flex-direction: column;
  margin-bottom: 20px;
  padding: 40px;
  min-height: breakpoints.$half-card-height;
  background: colors.$background;
  font-family: 'Roboto Slab', serif;
  --_font-size: 16px;
  font-size: var(--_font-size);
  font-weight: 300;
  line-height: 1.5;

  @include breakpoints.respond-to(mobile) {
    padding: 20px;
    --_font-size: 14px;
  }

  :deep(.markdown-content) {
    > *:first-child {
      margin-top: 0;
    }

    > *:last-child {
      margin-bottom: 0;
    }

    h1 {
      margin-top: 1em;
      margin-bottom: var(--_font-size);
      font-size: 1.5em;
      font-weight: 500;
    }

    h2 {
      margin-top: 1em;
      margin-bottom: var(--_font-size);
      font-size: 1.25em;
      font-weight: 500;
    }

    h3,
    h4,
    h5,
    h6 {
      margin-top: 1em;
      margin-bottom: var(--_font-size);
      font-size: 1.125em;
      font-weight: 500;
    }

    p,
    ul,
    ol {
      margin-bottom: var(--_font-size);
      font-size: 1em;
    }

    ul,
    ol {
      padding-left: 2em;

      li {
        &::marker {
          font-variant-numeric: tabular-nums;
        }

        ul,
        ol {
          margin-bottom: 0;
        }
      }
    }

    strong,
    b {
      font-weight: 500;
    }
  }
}
</style>
