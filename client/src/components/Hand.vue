<template inline-template>
  <span class="container d-inline-block">
    <ul>
      <li class="handlist" v-for="(card, index) in cards" :key=index>
        <cardspace @clicked="cardSpaceClicked" v-bind:card_src=card></cardspace>
      </li>
    </ul>
  </span>
</template>

<style>
ul {
  list-style-type: none;
}
.handlist {
  display: inline-block;
  padding: 0px;
  overflow-x: auto;
}
</style>

<script>
import CardSpace from './CardSpace.vue';

export default {
  components: {
    cardspace: CardSpace,
  },
  name: 'Hand',
  props: {
    cards: Array,
  },
  methods: {
    cardSpaceClicked(cardSrc) {
      this.$emit('highlight', cardSrc);
    },
  },
};
</script>
