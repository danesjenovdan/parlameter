<template>
  <div class="card-content-embed">
    <div class="card-back-content">
      <div class="embed-content">
        <div class="embed-divider"></div>
        <!-- <div class="embed-switch-container">
          <div v-t="'embed.always-refresh'" class="embed-label"></div>
          <div class="embed-switch-big-box" @click="refresh = !refresh">
            <div :class="['embed-switch-box', { off: !refresh }]">
              <div class="embed-switch">
                <div class="embed-switches">
                  <div v-t="'yes'" class="leftswitch"></div>
                  <div v-t="'no'" class="rightswitch"></div>
                </div>
              </div>
            </div>
            <div class="embed-switch-ball"></div>
          </div>
        </div> -->
        <div class="embed-divider"></div>
        <div class="embed-script">
          <!-- eslint-disable vue/no-v-html -->
          <textarea
            ref="embedInput"
            class="form-control"
            rows="5"
            v-html="embedCode"
          ></textarea>
          <!-- eslint-enable vue/no-v-html -->
          <button
            class="btn-parlameter btn-full-width btn-blue btn-copy-embed"
            @click="copyEmbedCode"
          >
            <span v-if="copied" v-t="'copied'"></span>
            <span v-else v-t="'copy'"></span>
          </button>
        </div>
      </div>
    </div>
  </div>
</template>

<script>
import copyInput from '@/_helpers/copyInput.js';

export default {
  name: 'CardEmbed',
  inject: ['cardUrl'],
  data() {
    return {
      copied: false,
      refresh: true,
    };
  },
  computed: {
    embedUrl() {
      return `${this.cardUrl}&locale=${this.$i18n.locale}&template=embed`;
    },
    embedCode() {
      const { mountId } = this.$root.$options.contextData;

      // TODO: refresh
      // let newUrl = this.url;
      // if (!this.refresh) {
      //   newUrl = `${this.url.split('?')[0]}${format(new Date(), 'd.M.y')}?${
      //     this.url.split('?')[1]
      //   }`;
      // }

      let htmlCode = '';
      htmlCode += `<iframe id="${mountId}" frameborder="0" width="100%" style="max-width:100%;" src="${this.embedUrl}"></iframe>`;
      htmlCode +=
        '<script src="https://cdnjs.cloudflare.com/ajax/libs/iframe-resizer/4.3.2/iframeResizer.min.js"></' + // break up script end tag to fix parsing
        `script><script>iFrameResize({checkOrigin:false},'#${mountId}');</` + // break up script end tag to fix parsing
        'script>';

      return htmlCode;
    },
  },
  methods: {
    copyEmbedCode() {
      this.copied = copyInput(this.$refs.embedInput);
    },
  },
};
</script>

<style lang="scss" scoped>
textarea.form-control {
  resize: vertical;
}
</style>
