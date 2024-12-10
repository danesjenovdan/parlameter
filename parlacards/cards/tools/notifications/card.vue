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
        <div class="notification-signup-row">
          <div class="left-col">
            <div class="icon-col">
              <div class="parlaicon parlaicon-notification-trigger" />
            </div>
            <div class="text-col">
              <h4 class="group-title">{{ $t('trigger') }}</h4>
              <p>{{ $t('notification-steps[0].textfirst') }}</p>
              <p>{{ $t('notification-steps[0].textsecond') }}</p>
            </div>
          </div>
          <div class="right-col">
            <div class="input-container">
              <label>
                <span>{{ $t('input-trigger') }}</span>
                <input
                  v-model="signUpData.keyword"
                  type="text"
                  required
                  class="form-control"
                />
              </label>
            </div>
          </div>
        </div>

        <hr />

        <div class="notification-signup-row">
          <div class="left-col">
            <div class="icon-col">
              <div class="parlaicon parlaicon-notification-match" />
            </div>
            <div class="text-col">
              <h4 class="group-title">{{ $t('match') }}</h4>
              <p>{{ $t('notification-steps[1].textfirst') }}</p>
            </div>
          </div>
          <div class="right-col">
            <div class="input-container">
              <template
                v-for="(methodValue, methodKey) in matchingMethods"
                :key="methodKey"
              >
                <div class="form-element-checkbox is-radio">
                  <input
                    :id="`method_${methodKey}`"
                    v-model="signUpData.matching_method"
                    type="radio"
                    class="checkbox"
                    :value="methodKey"
                  />
                  <label :for="`method_${methodKey}`">
                    <span>{{ $t(methodValue) }}</span>
                  </label>
                </div>
              </template>
            </div>
          </div>
        </div>

        <hr />

        <div class="notification-signup-row">
          <div class="left-col">
            <div class="icon-col">
              <div class="parlaicon parlaicon-notification-interval" />
            </div>
            <div class="text-col">
              <h4 class="group-title">{{ $t('interval') }}</h4>
              <p>{{ $t('notification-steps[2].textfirst') }}</p>
            </div>
          </div>
          <div class="right-col">
            <div class="input-container">
              <template
                v-for="(frequencyValue, frequencyKey) in frequencies"
                :key="frequencyKey"
              >
                <div class="form-element-checkbox is-radio">
                  <input
                    :id="`frequency_${frequencyKey}`"
                    v-model="signUpData.notification_frequency"
                    type="radio"
                    class="checkbox"
                    :value="frequencyKey"
                  />
                  <label :for="`frequency_${frequencyKey}`">
                    <span>{{ $t(frequencyValue) }}</span>
                  </label>
                </div>
              </template>
            </div>
          </div>
        </div>

        <hr />

        <div class="notification-signup-row">
          <div class="left-col">
            <div class="icon-col">
              <div class="parlaicon parlaicon-notification-email" />
            </div>
            <div class="text-col">
              <h4 class="group-title">{{ $t('email') }}</h4>
              <p>{{ $t('notification-steps[3].textfirst') }}</p>
            </div>
          </div>
          <div class="right-col">
            <div class="input-container">
              <label>
                <span>{{ $t('input-email') }}</span>
                <input
                  v-model="signUpData.email"
                  type="email"
                  required
                  class="form-control"
                />
              </label>
            </div>
            <div class="input-container">
              <div class="form-element-checkbox is-check">
                <input id="consent" type="checkbox" class="checkbox" required />
                <label for="consent">{{
                  $t('notification-steps[3].textsecond')
                }}</label>
              </div>
            </div>
          </div>
        </div>

        <hr />

        <div class="submit-container text-center">
          <button type="submit" class="signup-button" :disabled="isLoading">
            {{ $t('notification-steps[3].submit') }}
          </button>
        </div>
      </form>

      <div v-if="isLoading || success || error" class="loader-container">
        <div v-if="isLoading" class="nalagalnik"></div>
        <div v-else-if="success === 'submit'" class="success">
          <div>
            <div class="circle-with-icon parlaicon-notification-email">
              <strong>{{ $t('notification-steps[4].textfirst') }}</strong>
            </div>
            <p>{{ $t('notification-steps[4].textsecond') }}</p>
            <button class="close-modal" @click="closeModal">
              {{ $t('add-new-trigger') }}
            </button>
          </div>
        </div>
        <div v-else-if="success === 'confirm'" class="success">
          <div>
            <div class="circle-with-icon parlaicon-notification-email">
              <strong>{{ $t('notification-steps[5].textfirst') }}</strong>
            </div>
            <i18n-t keypath="notification-steps[5].textsecond" tag="p">
              <template #email>
                <strong>{{ signUpData.email }}</strong>
              </template>
              <template #keyword>
                <strong>{{ signUpData.keyword }}</strong>
              </template>
            </i18n-t>
            <button class="close-modal" @click="closeModal">
              {{ $t('to-notification-list') }}
            </button>
          </div>
        </div>
        <div v-else-if="error" class="error">
          <div>
            <p>
              <strong>{{ $t('notification-steps[6].textfirst') }}</strong>
            </p>
            <p>{{ $t('notification-steps[6].textsecond') }}</p>
            <button class="close-modal" @click="closeModal">&times;</button>
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
@use 'sass:math';
@use 'sass:string';
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
  margin-top: 12px;

  hr {
    margin-block: 26px;
  }

  .notification-signup-row {
    display: flex;
    gap: 48px;

    .left-col,
    .right-col {
      flex: 1;
    }

    .left-col {
      display: flex;
      gap: 24px;

      .icon-col {
        flex-shrink: 0;
        margin-left: 12px;
      }

      .group-title {
        font-size: 16px;
        font-weight: 700;
        margin-top: 0;
        margin-bottom: 10px;
      }

      p {
        margin-top: 0;
        margin-bottom: 0;
        font-family: 'Roboto Slab', 'Times New Roman', serif;
      }
    }

    .right-col {
      margin-right: 12px;

      .input-container {
        display: flex;
        flex-direction: column;
        gap: 12px;

        label {
          display: block;

          input {
            width: 100%;
            margin-block: 4px;
            font-size: 16px;
            font-weight: 700;
            line-height: 50px;
            height: 50px;

            &,
            &:focus {
              outline: none;
              box-shadow: none;
              color: colors.$font-default;
              border-color: colors.$font-default;
            }
          }
        }

        .form-element-checkbox.is-radio {
          input.checkbox {
            & + label {
              display: flex;
              align-items: center;
              margin: 0;
              font-size: 14px;
              line-height: 20px;
              font-weight: 400;

              span {
                margin-top: 1.5px;
              }

              &::before {
                width: 20px;
                height: 20px;
                border-radius: 9999rem;
                border-color: colors.$font-default;
              }
            }

            &:checked + label {
              font-weight: 700;

              &::before {
                background-repeat: no-repeat;
                background-position: center center;
                background-size: 14px;
                background-image: url('data:image/svg+xml;utf8,<svg xmlns="http://www.w3.org/2000/svg" fill="%23#{string.slice("#{colors.$tab-passive}", 2)}" viewBox="0 0 10 10"><circle cx="5" cy="5" r="5" /></svg>');
                border-color: colors.$tab-passive;
              }
            }
          }
        }

        .form-element-checkbox.is-check {
          input.checkbox {
            & + label {
              font-size: 13px;
              font-weight: 400;
              line-height: 1.2;

              &::before {
                width: 24px;
                height: 24px;
                border-color: colors.$font-default;
              }
            }

            &:checked + label {
              &::before {
                background-repeat: no-repeat;
                background-position: center center;
                background-size: 15px;
                background-image: url('data:image/svg+xml;utf8,<svg xmlns="http://www.w3.org/2000/svg" fill="%23#{string.slice("#{colors.$tab-passive}", 2)}" viewBox="0 0 16 15"><path d="M5.97 13.536 0 7.939l2.848-2.67L5.97 8.197l7.181-6.733L16 4.134 5.97 13.536Z" /></svg>');
              }
            }
          }
        }
      }
    }
  }

  .submit-container {
    margin-top: 2rem;
    margin-bottom: 2rem;

    .signup-button {
      padding: 14px 40px;
      border: none;
      background: none;
      font-size: 16px;
      font-weight: 400;
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
    position: absolute;
    top: 0;
    left: 0;
    right: 0;
    bottom: 0;
    display: flex;
    justify-content: center;
    align-items: center;
    padding: 42px 32px;
    background: #fff;
    box-shadow: 0 0 10px rgba(0, 0, 0, 0.1);
    text-align: center;
    font-size: 16px;

    .circle-with-icon {
      $size: 180px;
      width: $size;
      height: $size;
      margin-inline: auto;
      padding: math.div($size, 1.55) 26px 0;
      background-color: colors.$light-background;
      background-size: math.div($size, 3.5);
      background-position: center math.div($size, 4);
      background-repeat: no-repeat;
      border-radius: 50%;
      font-size: 16px;
      line-height: 20px;
      text-align: center;
    }

    p {
      max-width: 360px;
      margin-block: 21px;
      font-family: 'Roboto Slab', 'Times New Roman', serif;
      font-size: 14px;
      line-height: 20px;
    }

    .close-modal {
      margin-top: 28px;
      padding: 14px 28px;
      border: none;
      background: none;
      font-size: 16px;
      font-weight: 400;
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
</style>
