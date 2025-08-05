<template>
  <li class="person-speech">
    <div class="person-container">
      <div class="name">
        <a
          :href="getSessionAgendaLink(agendaItem, agendaItem.session)"
          class="funblue-light-hover"
          >{{ agendaItem.name }}</a
        >
      </div>
    </div>
    <div class="speech">
      <!-- eslint-disable vue/no-v-html -->
      <a
        :href="getSessionAgendaLink(agendaItem, agendaItem.session)"
        class="funblue-light-hover"
        v-html="agendaItem.text"
      ></a>
      <!-- eslint-enable vue/no-v-html -->
    </div>
  </li>
</template>

<script>
import links from '@/_mixins/links.js';

export default {
  name: 'SearchMinutesItem',
  mixins: [links],
  props: {
    agendaItem: {
      type: Object,
      required: true,
    },
  },
};
</script>

<style lang="scss" scoped>
@use 'parlassets/scss/breakpoints';
@use 'parlassets/scss/colors';

.person-speech {
  border-bottom: 1px solid colors.$background;
  padding: 15px 0;
  list-style: none;
  display: flex;
  align-items: center;

  @include breakpoints.respond-to(mobile) {
    flex-wrap: wrap;
  }

  &:last-child {
    border-bottom: 0;
  }

  .person-container {
    flex: 2;
    display: flex;
    padding: 0 7px;

    @include breakpoints.respond-to(mobile) {
      flex-grow: 1;
      flex-shrink: 0;
      flex-basis: 100%;
      padding: 0 4px;
    }

    .name {
      text-align: left;
      font-size: 14px;
      font-weight: 300;
      padding-right: 10p;
      flex: 1;
      align-self: center;

      a {
        padding: 0.15em 0.3em;
        margin: 0 -0.3em;
        -webkit-box-decoration-break: clone;
        box-decoration-break: clone;
      }
    }
  }

  .speech {
    flex: 4;
    padding: 0 7px;

    @include breakpoints.respond-to(mobile) {
      padding: 10px 4px 0;
    }

    a {
      color: colors.$font-default;
      font-size: 14px;
      line-height: 20px;
      font-weight: 300;
      font-family: 'Roboto Slab', serif;
      padding: 0.15em 0.3em;
      margin: 0 -0.3em;
      -webkit-box-decoration-break: clone;
      box-decoration-break: clone;
    }

    :deep(em) {
      font-style: normal;
      font-weight: 400;
    }
  }
}
</style>
