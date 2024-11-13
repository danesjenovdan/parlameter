<template>
  <div class="event">
    <div :class="['parlaicon', eventIcon]"></div>
    <template
      v-if="
        event.type === 'question' ||
        event.type === 'initiative' ||
        event.type === 'unknown'
      "
    >
      <i18n-t :keypath="translationKey" tag="div" class="motion">
        <template #name>
          <span v-if="showAuthor">
            <span v-for="(author, index) in authors" :key="author.id">
              <a
                :href="getPersonOrPartyLink(author)"
                class="funblue-light-hover"
                >{{ getPersonOrPartyName(author) }}</a
              ><span v-if="index + 1 < authors.length">, </span>
            </span>
          </span>
        </template>
        <template #title>
          <component
            :is="event.url ? 'a' : 'strong'"
            :href="event.url"
            :class="{ 'funblue-light-hover': event.url }"
            target="_blank"
            >{{ event.title }}</component
          >
        </template>
        <template #recipient>
          <span>{{ event.recipient_text }}</span>
        </template>
      </i18n-t>
    </template>
    <template v-else-if="event.type === 'ballot'">
      <i18n-t :keypath="translationKey" tag="div" class="motion">
        <template #title>
          <a :href="getVoteLink(event.vote)" class="funblue-light-hover">{{
            event.vote?.title
          }}</a>
        </template>
      </i18n-t>
    </template>
    <template v-else-if="event.type === 'speech'">
      <i18n-t :keypath="translationKey" tag="div" class="motion">
        <template #session>
          <a :href="getSpeechLink(event)" class="funblue-light-hover">{{
            event.session?.name
          }}</a>
        </template>
        <template #org>
          <span>{{
            event.session?.organizations?.map((o) => o.name).join(', ')
          }}</span>
        </template>
      </i18n-t>
    </template>
    <template v-else>
      <a :href="event.content_url" class="funblue-light-hover" target="_blank">
        {{ event.type }}
      </a>
    </template>
  </div>
</template>

<script>
import links from '@/_mixins/links.js';

export default {
  name: 'Event',
  mixins: [links],
  props: {
    event: {
      type: Object,
      required: true,
    },
    showAuthor: {
      type: Boolean,
      default: false,
    },
  },
  computed: {
    eventIcon() {
      if (
        this.event.type === 'question' ||
        this.event.type === 'initiative' ||
        this.event.type === 'unknown'
      ) {
        return 'parlaicon-vprasanje';
      }
      if (this.event.type === 'ballot') {
        switch (this.event.option) {
          case 'for':
            return 'parlaicon-za';
          case 'against':
            return 'parlaicon-proti';
          case 'absent':
            return 'parlaicon-ni';
          case 'abstain':
            return 'parlaicon-kvorum';
          case 'did not vote':
            return 'parlaicon-brez-glasu';
          default:
            return '';
        }
      }
      if (this.event.type === 'speech') {
        return 'parlaicon-govor';
      }
      return '';
    },
    authors() {
      if (this.$root.cardData.data?.person) {
        return [this.$root.cardData.data?.person];
      }
      return this.event.authors || [];
    },
    translationKey() {
      if (this.authors.length > 0) {
        if (this.authors[0].classification === 'pg') {
          return `${this.event.type}.asked--group`;
        }
        let gender = 'plural';
        if (this.authors.length === 1) {
          gender = this.authors[0].preferred_pronoun === 'she' ? 'f' : 'm';
        }
        if (this.event.type === 'ballot') {
          const optionLabel = (this.event.option || '').replace(/\s+/g, '-');
          return `event.ballot--${optionLabel}--${gender}`;
        }
        if (this.event.type === 'speech') {
          return `event.speech--${gender}`;
        }
        return `${this.event.type}.asked${
          this.showAuthor ? '--with-name' : ''
        }--${gender}`;
      }
      return '';
    },
  },
};
</script>

<style lang="scss">
.event {
  display: flex;
  font-weight: 500;
  font-size: 16px;
  line-height: 18px;
  margin: 7px 0;

  .parlaicon {
    margin-right: 10px;
    margin-top: 15px;
  }

  .motion {
    flex: 1;
    font-weight: 300;
    line-height: 20px;
    padding: 15px 0;
    margin-right: 10px;

    a,
    strong {
      font-weight: normal;
    }
  }
}
</style>
