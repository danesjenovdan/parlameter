<template>
  <div :class="['newsletter-signup-container', `type-${type}`]">
    <div v-if="email && token">
      <div class="unsubscribe">
        <button
          v-if="showUnsubscribe"
          type="button"
          class="signup-button"
          :disabled="isLoading || !segmentId"
          @click="onUnsubscribe"
        >
          {{ $t('newsletter-signup-unsubscribe-button-text') }}
        </button>
        <div v-if="isLoading" class="loader-container">
          <div class="nalagalnik"></div>
        </div>
      </div>
    </div>
    <template v-else>
      <div class="title-and-description">
        <h1>{{ $t('newsletter-signup-title') }}</h1>
        <p>
          {{ $t('newsletter-signup-description') }}
        </p>
      </div>
      <form class="form-elements" @submit.prevent="onSubmit">
        <div class="form-element-email">
          <search-field
            ref="email"
            v-model="inputEmail"
            type="email"
            :placeholder="$t('newsletter-signup-input-placeholder')"
            required
          />
          <button
            v-if="type === 'banner'"
            type="submit"
            class="signup-button"
            :disabled="isLoading || !segmentId"
          >
            {{ $t('newsletter-signup-button-text') }}
          </button>
        </div>
        <div class="form-element-checkbox">
          <input
            :id="newsletterGdprCheckElementId"
            v-model="gdprChecked"
            name="newsletter-gdpr-check"
            type="checkbox"
            class="checkbox"
            required
          />
          <label :for="newsletterGdprCheckElementId">
            {{ $t('newsletter-signup-checkbox-text') }}
          </label>
        </div>
        <div v-if="type === 'card'">
          <button
            type="submit"
            class="signup-button"
            :disabled="isLoading || !segmentId"
          >
            {{ $t('newsletter-signup-button-text') }}
          </button>
        </div>
        <div v-if="isLoading || success" class="loader-container">
          <div v-if="isLoading" class="nalagalnik"></div>
          <div v-else-if="success" class="success">
            {{ $t('newsletter-signup-success-text') }}
          </div>
        </div>
      </form>
    </template>
  </div>
</template>

<script>
import axios from 'axios';
import SearchField from '@/_components/SearchField.vue';

export default {
  name: 'NewsletterSignup',
  components: {
    SearchField,
  },
  props: {
    type: {
      type: String,
      required: true,
      validator: (value) => ['card', 'banner'].includes(value),
    },
  },
  data() {
    const { cardState } = this.$root.$options.contextData;

    return {
      inputEmail: '',
      gdprChecked: false,
      segmentId: Number(cardState?.segment) || 0,
      email: cardState?.email || null,
      token: cardState?.token || null,
      //
      showUnsubscribe: false,
      isLoading: false,
      success: false,
    };
  },
  computed: {
    newsletterGdprCheckElementId() {
      // use unique id for label[for] and input[id] attributes in case more than
      // one card is embeded on the same page
      return `newsletter-gdpr-check__${this.$root.$options.contextData.mountId}`;
    },
  },
  mounted() {
    if (this.email && this.token) {
      this.fetchMySubscriptions();
    }
  },
  methods: {
    resetCard() {
      this.email = null;
      this.token = null;
      this.showUnsubscribe = false;
      this.isLoading = false;
      this.success = false;
    },
    onSubmit() {
      if (this.gdprChecked && this.inputEmail) {
        this.isLoading = true;
        axios
          .post('https://podpri.djnd.si/api/subscribe/', {
            email: this.inputEmail,
            segment_id: this.segmentId,
          })
          .then((response) => {
            if (response.data?.msg === 'mail sent') {
              this.success = true;
            }
          })
          .then(() => {
            this.isLoading = false;
          });
      }
    },
    fetchMySubscriptions() {
      this.isLoading = true;
      const email = encodeURIComponent(this.email);
      const token = encodeURIComponent(this.token);
      const url = `https://podpri.djnd.si/api/segments/my/?email=${email}&token=${token}`;
      axios
        .get(url)
        .then((response) => {
          if (response.data?.segments?.length) {
            const segment = response.data.segments.find(
              (s) => s.id === this.segmentId,
            );
            if (segment) {
              this.showUnsubscribe = true;
              this.isLoading = false;
              return;
            }
          }
          throw new Error('Not subscribed!');
        })
        .catch(() => {
          this.resetCard();
        });
    },
    onUnsubscribe() {
      this.isLoading = true;
      const email = encodeURIComponent(this.email);
      const token = encodeURIComponent(this.token);
      const url = `https://podpri.djnd.si/api/segments/${this.segmentId}/contact/?email=${email}&token=${token}`;
      axios.delete(url).then(() => {
        this.resetCard();
      });
    },
  },
};
</script>

<style lang="scss" scoped>
@use 'parlassets/scss/colors';

.newsletter-signup-container {
  padding: 32px 16px;

  .signup-button {
    display: block;
    width: 100%;
    padding: 15px 16px;
    border: none;
    background: none;
    font-weight: 300;
    color: colors.$white;
    background-color: colors.$tab-passive;

    &:disabled {
      cursor: not-allowed;
    }

    &:not(:disabled):hover {
      color: colors.$white;
      background-color: colors.$tab-hover;
    }

    &:active,
    &:hover:active {
      color: colors.$white;
      background-color: colors.$tab-active;
    }
  }

  .loader-container {
    position: absolute;
    top: 0;
    left: 0;
    right: 0;
    bottom: 0;
    display: flex;
    justify-content: center;
    align-content: center;
    background: rgba(255, 255, 255, 0.75);

    .nalagalnik {
      height: 100%;
    }

    .success {
      display: flex;
      align-items: center;
      text-align: center;
      font-size: 16px;
      font-weight: 700;
    }
  }

  .unsubscribe {
    position: relative;
    display: flex;
    justify-content: center;
    align-items: center;
    min-height: 200px;
  }

  .title-and-description {
    h1 {
      margin: 0;
      font-size: 24px;
      font-weight: 500;
      margin-bottom: 12px;
    }

    p {
      margin: 0;
      font-family: 'Roboto Slab', 'Times New Roman', Times, serif;
      font-size: 16px;
      font-weight: 300;
    }
  }

  .form-elements {
    position: relative;
    margin-top: 16px;

    .form-element-email {
      margin-bottom: 10px;
    }

    .form-element-checkbox {
      position: relative;
      margin-bottom: 10px;

      .checkbox {
        position: absolute;
        top: 15px;
        left: 11px;
        clip: rect(0, 0, 0, 0);
        pointer-events: none;
        display: inline;
        width: 1px;
        height: 1px;
      }

      label {
        display: flex;
        align-items: center;
        min-height: 22px;
        font-size: 11px;
        line-height: 1.1;
      }
    }
  }

  &.type-banner {
    display: flex;
    padding: 20px 24px;
    background: colors.$white;

    .title-and-description {
      flex: 1;

      h1 {
        font-size: 20px;
        margin-bottom: 8px;
      }

      p {
        font-size: 14px;
      }
    }

    .form-elements {
      flex: 1;
      margin-top: 0;

      .form-element-email {
        display: flex;

        input {
          flex: 4;
          height: 40px;
          font-size: 14px;
        }

        button {
          flex: 1;
          margin-left: 10px;
          padding-top: 5px;
          padding-bottom: 5px;
        }
      }

      .form-element-checkbox {
        margin-bottom: 0;

        label {
          margin-bottom: 0;
        }
      }
    }
  }
}
</style>
