<template>
  <div class="data-not-published">
    <div class="icon-empty-state"></div>
    <p>
      {{ text }}
      <a
        v-if="linkUrl"
        v-t="'data-not-published.link-text'"
        :href="linkUrl"
        target="_blank"
      ></a>
    </p>
  </div>
</template>

<script>
export default {
  name: 'DataNotPublished',
  props: {
    text: {
      type: String,
      required: true,
    },
  },
  computed: {
    linkUrl() {
      if (!this.$te('data-not-published.link-url')) {
        return null;
      }
      const url = this.$t('data-not-published.link-url');
      if (!url || url === '[empty]') {
        return null;
      }
      return url;
    },
  },
};
</script>

<style lang="scss">
.data-not-published {
  min-height: 320px;
  display: flex;
  flex-direction: column;
  justify-content: center;

  .icon-empty-state {
    background-image: url('#{get-parlassets-url()}/img/icons/icon-empty-state.png');
    background-repeat: no-repeat;
    width: 68px;
    height: 53px;
    margin: 0 auto 40px;
  }

  p {
    text-align: center;
    font-size: 18px;
    font-style: italic;
    font-weight: 300;
    font-family: 'Roboto Slab', 'Times New Roman', serif;
    line-height: 1.5;
  }
}
</style>
