import Vue from 'vue';
import VueRouter from 'vue-router';
import VueChatScroll from 'vue-chat-scroll';
import Game from '../components/Game.vue';
import Ping from '../components/Ping.vue';
import Console from '../components/Console.vue';
import Index from '../components/Index.vue';
import About from '../components/About.vue';
import Setup from '../components/Setup.vue';

Vue.use(VueRouter);
Vue.use(VueChatScroll);

export default new VueRouter({
  el: '#app',
  mode: 'history',
  base: process.env.BASE_URL,
  routes: [
    {
      path: '/',
      name: 'Index',
      component: Index,
    },
    {
      path: '/about',
      name: 'About',
      component: About,
    },
    {
      path: '/setup',
      name: 'Setup',
      component: Setup,
    },
    {
      path: '/game',
      name: 'Game',
      component: Game,
    },
    {
      path: '/ping',
      name: 'Ping',
      component: Ping,
    },
    {
      path: '/console',
      name: 'Console',
      component: Console,
    },
  ],
});
