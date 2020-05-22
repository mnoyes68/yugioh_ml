<template>
  <div class="container">
    <div id="gameconsole" class="console">
      <ul v-chat-scroll>
        <li v-for="(entry, index) in consoleEntries" :key=index>{{entry}}</li>
      </ul>
    </div>
  </div>
</template>

<style>
.console {
  border-style: solid;
  height: 100px;
  width: 100%;
  padding-bottom: 30px;
  overflow-y: auto;
}
ul {
  list-style-type: none;
}
</style>

<script>
import Vue from 'vue';
import VueChatScroll from 'vue-chat-scroll';

Vue.use(VueChatScroll);

export default {
  name: 'Console',
  data() {
    return {
      ygoconsole: [],
    };
  },
  props: {
    consoleEntries: Array,
  },
  watch: {
    consoleEntries: {
      deep: true,
      handler() {
        const consoleElement = this.$el.querySelector('#gameconsole');
        consoleElement.scrollTop = consoleElement.scrollHeight;
      },
    },
  },
};
</script>
