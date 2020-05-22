<template>
  <div class="container-fluid">
    <span v-on:click="highlightCard(card_src)" class="card_space">
      <img v-if=card_src v-bind:src="require('../assets/' + card_src.img)" class="card_image center-block" v-bind:class="[is_def ? 'def-position' : '', getTargetStatus()]">
    </span>
  </div>
</template>

<style>
.card_space {
  display: inline-block;
  height: 70px;
  width: 70px;
}
.target_card {
  border-style: solid;
  border-color: red;
}
.target_card_selected {
  border-style: solid;
  border-color: lime;
}
img {
  height:100%;
}
.center-block {
    display: block;
    margin-left: auto;
    margin-right: auto;
}
.def-position {
    -webkit-transform: rotate(90deg); /* Safari and Chrome */
    -moz-transform: rotate(90deg);   /* Firefox */
    -ms-transform: rotate(90deg);   /* IE 9 */
    -o-transform: rotate(90deg);   /* Opera */
    transform: rotate(90deg);
}
</style>

<script>
export default {
  name: 'CardSpace',
  props: {
    card_src: Object,
    is_def: Boolean,
    is_target: Boolean,
    target_list: [],
    selected_targets: [],
  },
  methods: {
    getTargetStatus() {
      if (this.card_src && this.target_list) {
        if (this.target_list.includes(this.card_src['CardID'])) {
          if (this.selected_targets && this.selected_targets.includes(this.card_src['CardID'])) {
            return 'target_card_selected';
          } else {
            return 'target_card';
          }
        }
      }
      return '';
    },
    highlightCard(cardSrc) {
      this.$emit('clicked', cardSrc);
    },
  },
};
</script>
