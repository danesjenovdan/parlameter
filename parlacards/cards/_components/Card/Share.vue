<template>
  <div class="card-content-share">
    <div class="card-back-content">
      <div class="share-content">
        <label v-t="'share.direct-link'" :for="shareUrlElementId"></label>
        <input
          :id="shareUrlElementId"
          ref="urlInput"
          :value="shareUrl"
          type="url"
          class="form-control share-url"
        />
        <button
          class="btn-parlameter btn-full-width btn-blue"
          @click="copyLink"
        >
          <span v-if="copied" v-t="'copied'"></span>
          <span v-else v-t="'copy'"></span>
        </button>
      </div>
    </div>
  </div>
</template>

<script>
import copyInput from '@/_helpers/copyInput.js';

export default {
  name: 'CardShare',
  inject: ['cardUrl'],
  data() {
    return {
      copied: false,
    };
  },
  computed: {
    shareUrl() {
      return `${this.cardUrl}&locale=${this.$i18n.locale}&template=share`;
    },
    shareUrlElementId() {
      // use unique id for label[for] and input[id] attributes in case more than
      // one card is embeded on the same page
      return `share-url__${this.$root.$options.contextData.mountId}`;
    },
  },
  methods: {
    copyLink() {
      this.copied = copyInput(this.$refs.urlInput);
    },
  },
};
</script>
