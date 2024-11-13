<template>
  <card-wrapper :header-config="headerConfig" max-height>
    <div>
      <div v-if="listData?.response" class="notification-list">
        <table v-if="listData.response.results" class="list-table">
          <thead>
            <tr>
              <th class="keyword">{{ $t('trigger') }}</th>
              <th class="frequency">{{ $t('interval') }}</th>
              <th class="method">{{ $t('match') }}</th>
              <th class="delete"></th>
            </tr>
          </thead>
          <tbody>
            <tr v-for="item in listData.response.results" :key="item.kid">
              <td class="keyword">{{ item.keyword }}</td>
              <td class="frequency">
                {{ $t(frequencies[item.notification_frequency]) }}
              </td>
              <td class="method">
                {{ $t(matchingMethods[item.matching_method]) }}
              </td>
              <td class="delete">
                <button @click="deleteKeyword(item)">
                  <span>&times;</span>
                </button>
              </td>
            </tr>
          </tbody>
        </table>
        <PaginationLimitOffset
          :limit="listData.limit"
          :offset="listData.offset"
          :count="listData.response.count"
          @change="changePage"
        />
      </div>
      <form v-else class="notification-signup" @submit="submitForm">
        <div class="form-group">
          <h4 class="group-title text-center">{{ $t('trigger') }}</h4>

          <div class="text-center">
            <p>{{ $t('notification-steps[0].textfirst') }}</p>
            <p>{{ $t('notification-steps[0].textsecond') }}</p>
          </div>

          <div class="input-container">
            <input
              v-model="signUpData.keyword"
              type="text"
              required
              :placeholder="$t('trigger')"
              class="form-control"
            />
          </div>
        </div>

        <hr />

        <div class="form-group">
          <h4 class="group-title text-center">{{ $t('match') }}</h4>

          <div class="text-center">
            <p>{{ $t('notification-steps[1].textfirst') }}</p>
          </div>

          <div class="input-container inputs-inline">
            <template
              v-for="(methodValue, methodKey) in matchingMethods"
              :key="methodKey"
            >
              <div class="form-element-checkbox">
                <input
                  :id="`method_${methodKey}`"
                  v-model="signUpData.matching_method"
                  type="radio"
                  class="checkbox"
                  :value="methodKey"
                />
                <label :for="`method_${methodKey}`">{{
                  $t(methodValue)
                }}</label>
              </div>
            </template>
          </div>
        </div>

        <hr />

        <div class="form-group">
          <h4 class="group-title text-center">{{ $t('interval') }}</h4>

          <div class="text-center">
            <p>{{ $t('notification-steps[2].textfirst') }}</p>
          </div>

          <div class="input-container inputs-inline">
            <template
              v-for="(frequencyValue, frequencyKey) in frequencies"
              :key="frequencyKey"
            >
              <div class="form-element-checkbox">
                <input
                  :id="`frequency_${frequencyKey}`"
                  v-model="signUpData.notification_frequency"
                  type="radio"
                  class="checkbox"
                  :value="frequencyKey"
                />
                <label :for="`frequency_${frequencyKey}`">{{
                  $t(frequencyValue)
                }}</label>
              </div>
            </template>
          </div>
        </div>

        <hr />

        <div class="form-group">
          <h4 class="group-title text-center">{{ $t('email') }}</h4>

          <div class="text-center">
            <p>{{ $t('notification-steps[3].textfirst') }}</p>
          </div>

          <div class="input-container">
            <input
              v-model="signUpData.email"
              type="email"
              required
              :placeholder="$t('email-address')"
              class="form-control"
            />
          </div>

          <div class="input-container">
            <div class="form-element-checkbox">
              <input id="consent" type="checkbox" class="checkbox" required />
              <label for="consent">{{
                $t('notification-steps[3].textsecond')
              }}</label>
            </div>
          </div>
        </div>

        <div class="submit-container text-center">
          <button type="submit" class="signup-button" :disabled="isLoading">
            {{ $t('notification-steps[3].submit') }}
          </button>
        </div>
      </form>

      <div v-if="isLoading || success || error" class="loader-container">
        <div v-if="isLoading" class="nalagalnik"></div>
        <div v-else-if="success === 'submit'" class="success">
          <button class="close-modal" @click="closeModal">&times;</button>
          <div>
            <p>
              <strong>{{ $t('notification-steps[4].textfirst') }}</strong>
            </p>
            <p>{{ $t('notification-steps[4].textsecond') }}</p>
          </div>
        </div>
        <div v-else-if="success === 'confirm'" class="success">
          <button class="close-modal" @click="closeModal">&times;</button>
          <div>
            <p>
              <strong>{{ $t('notification-steps[5].textfirst') }}</strong>
            </p>
            <i18n-t keypath="notification-steps[5].textsecond" tag="p">
              <template #email>
                <strong>{{ signUpData.email }}</strong>
              </template>
              <template #keyword>
                <strong>{{ signUpData.keyword }}</strong>
              </template>
            </i18n-t>
          </div>
        </div>
        <div v-else-if="error" class="error">
          <button class="close-modal" @click="closeModal">&times;</button>
          <div>
            <p>
              <strong>{{ $t('notification-steps[6].textfirst') }}</strong>
            </p>
            <p>{{ $t('notification-steps[6].textsecond') }}</p>
          </div>
        </div>
      </div>
    </div>
  </card-wrapper>
</template>

<script>
import axios from 'axios';
import common from '@/_mixins/common.js';
import { defaultHeaderConfig } from '@/_mixins/altHeaders.js';
import PaginationLimitOffset from '@/_components/PaginationLimitOffset.vue';

export default {
  name: 'CardToolsNotifications',
  components: {
    PaginationLimitOffset,
  },
  mixins: [common],
  cardInfo: {
    doubleWidth: true,
  },
  data() {
    const { cardState } = this.$root.$options.contextData;

    let isLoading = false;
    const confirmData = {
      kid: null,
      uuid: null,
    };
    const listData = {
      uuid: null,
      response: null,
      limit: 10,
      offset: 0,
    };

    if (cardState?.action === 'confirm' && cardState?.kid && cardState?.uuid) {
      isLoading = true;
      confirmData.kid = cardState.kid;
      confirmData.uuid = cardState.uuid;
    } else if (cardState?.action === 'list' && cardState?.uuid) {
      isLoading = true;
      listData.uuid = cardState.uuid;
    }

    return {
      isLoading,
      success: null,
      error: null,
      confirmData,
      listData,
      signUpData: {
        keyword: '',
        notification_frequency: 'DAILY',
        matching_method: 'NARROW',
        email: '',
      },
      matchingMethods: {
        NARROW: 'notification-steps[1].firstbullet',
        WIDE: 'notification-steps[1].secondbullet',
      },
      frequencies: {
        DAILY: 'notification-steps[2].firstbullet',
        WEEKLY: 'notification-steps[2].secondbullet',
        MONTHLY: 'notification-steps[2].thirdbullet',
      },
      headerConfig: defaultHeaderConfig(this),
    };
  },
  mounted() {
    if (this.confirmData?.kid && this.confirmData?.uuid) {
      this.confirmSubscription();
    }
    if (this.listData?.uuid) {
      this.listSubscriptions();
    }
  },
  methods: {
    async submitForm(event) {
      event.preventDefault();

      const { urls } = this.$root.$options.contextData;
      const api = axios.create({ baseURL: urls.data });

      this.isLoading = true;
      this.success = null;
      this.error = null;
      try {
        await api.post('/notifications/keywords/', this.signUpData);
        this.isLoading = false;
        this.success = 'submit';
      } catch (error) {
        this.isLoading = false;
        this.error = error;
        // eslint-disable-next-line no-console
        console.error(error);
      }
    },
    async confirmSubscription() {
      const { urls } = this.$root.$options.contextData;
      const api = axios.create({ baseURL: urls.data });

      this.isLoading = true;
      this.success = null;
      this.error = null;
      try {
        const response = await api.get(
          `/notifications/keywords/${this.confirmData.kid}/confirm?uuid=${this.confirmData.uuid}`,
        );
        this.signUpData.keyword = response.data.keyword;
        this.signUpData.email = response.data.email;
        this.isLoading = false;
        this.success = 'confirm';
      } catch (error) {
        this.isLoading = false;
        this.error = error;
        // eslint-disable-next-line no-console
        console.error(error);
      }
    },
    async listSubscriptions() {
      const { urls } = this.$root.$options.contextData;
      const api = axios.create({ baseURL: urls.data });

      this.isLoading = true;
      this.success = null;
      this.error = null;
      try {
        const response = await api.get(
          `/notifications/keywords/?limit=${this.listData.limit}&offset=${this.listData.offset}&uuid=${this.listData.uuid}`,
        );
        this.isLoading = false;
        this.listData.response = response.data;
      } catch (error) {
        this.isLoading = false;
        this.error = error;
        // eslint-disable-next-line no-console
        console.error(error);
      }
    },
    changePage(newOffset) {
      this.listData.offset = newOffset;
      this.listSubscriptions();
    },
    async deleteKeyword(item) {
      const { urls } = this.$root.$options.contextData;
      const api = axios.create({ baseURL: urls.data });

      // eslint-disable-next-line no-alert
      const confirmDelete = window.confirm(
        this.$t('confirm-delete-notification'),
      );
      if (!confirmDelete) {
        return;
      }

      this.isLoading = true;
      this.success = null;
      this.error = null;
      try {
        await api.delete(
          `/notifications/keywords/${item.id}/?uuid=${this.listData.uuid}`,
        );
        this.listSubscriptions();
      } catch (error) {
        this.isLoading = false;
        this.error = error;
        // eslint-disable-next-line no-console
        console.error(error);
      }
    },
    closeModal() {
      if (this.success === 'confirm') {
        this.isLoading = true;
        this.listData.uuid = this.confirmData.uuid;
        this.listSubscriptions();
      }

      this.success = null;
      this.error = null;
      this.signUpData = {
        keyword: '',
        notification_frequency: 'DAILY',
        matching_method: 'NARROW',
        email: '',
      };
    },
  },
};
</script>

<style lang="scss" scoped>
@use 'parlassets/scss/colors';
@use 'parlassets/scss/color_classes';

.notification-list {
  .list-table {
    width: 100%;
    border-collapse: collapse;

    th,
    td {
      padding: 0.5rem;
      border-bottom: 1px solid #ccc;
      text-align: left;
    }

    th {
      text-transform: uppercase;
    }

    th.keyword,
    td.keyword {
      width: 50%;
    }

    th.method,
    td.method {
      width: 25%;
    }

    th.frequency,
    td.frequency {
      width: 25%;
    }

    td.delete button {
      border: none;
      border-radius: 50%;
      padding: 0;
      margin: 0 2px;
      height: 24px;
      width: 24px;
      display: flex;
      justify-content: center;
      align-items: center;
      font-size: 24px;
      background-color: colors.$tab-hover;
      color: colors.$white;
      line-height: 1;

      &:hover {
        background-color: colors.$tab-passive;
        color: colors.$white;
      }

      span {
        margin-top: -2px;
      }
    }
  }
}

.notification-signup {
  .group-title {
    margin-bottom: 2rem;
    text-transform: uppercase;
  }

  .input-container {
    max-width: 350px;
    margin-inline: auto;
    margin-block: 2rem;

    &.inputs-inline {
      max-width: 500px;
      display: flex;
      flex-wrap: wrap;
      justify-content: center;
      gap: 1rem 2rem;
    }

    .form-element-checkbox {
      position: relative;

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
        margin-bottom: 0;
        min-height: 22px;
        font-size: 13px;
        line-height: 1.1;
      }
    }
  }

  .submit-container {
    margin-top: 2rem;
    margin-bottom: 2rem;

    .signup-button {
      padding: 10px 16px;
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
  align-items: center;
  background: rgba(255, 255, 255, 0.85);
  z-index: 1000;

  .nalagalnik {
    height: 100%;
  }

  .success,
  .error {
    position: relative;
    display: flex;
    justify-content: center;
    align-items: center;
    min-width: min(100%, 500px);
    padding: 42px 16px 32px;
    background: rgba(255, 255, 255, 0.85);
    border: 1px solid #ccc;
    box-shadow: 0 0 10px rgba(0, 0, 0, 0.1);
    text-align: center;
    font-size: 16px;

    .close-modal {
      position: absolute;
      top: 0;
      right: 0;
      width: 1em;
      margin: 10px;
      padding: 0;
      font-size: 24px;
      line-height: 1em;
      background: none;
      border: none;
      cursor: pointer;

      @include color_classes.link-hover;
    }
  }
}
</style>
