<template inline-template>
  <span class="container d-inline-block">
    <h5>{{selector}}</h5>
    <ul>
      <li id="playerList">
        <img id="yugi" class="playerIcon" v-on:click="highlightCard('yugi')" v-bind:class="isSelected('yugi')" v-bind:src="require('../assets/images/portraits/YugiThumbnail.png')">
        <img id="kaiba" class="playerIcon" v-on:click="highlightCard('kaiba')" v-bind:class="isSelected('kaiba')" v-bind:src="require('../assets/images/portraits/Kaiba.png')">
        <img id="joey" class="playerIcon" v-on:click="highlightCard('joey')" v-bind:class="isSelected('joey')" v-bind:src="require('../assets/images/portraits/Joey.png')">
        <img id="pegasus" class="playerIcon" v-on:click="highlightCard('pegasus')" v-bind:class="isSelected('pegasus')" v-bind:src="require('../assets/images/portraits/Pegasus.png')">
        <img id="random" class="playerIcon" v-on:click="highlightCard('random')" v-bind:class="isSelected('random')" v-bind:src="require('../assets/images/portraits/Random.png')">
      </li>
    </ul>
  </span>
</template>

<style>
ul {
  list-style-type: none;
}
.playerIcon {
  padding: 12px;
  max-height: 150px;
  max-width: 150px;
}
.selected {
  border-style: solid;
  border-color: red;
  border-width: thick;
}
</style>

<script>
export default {
  name: 'PlayerBar',
  props: {
    selector: String,
    chosenName: String,
  },
  methods: {
    highlightCard(name) {
      this.$emit('choice', name);
      this.chosenName = name;
    },
    isSelected(name) {
      // Returns the class name selected if true
      if (this.chosenName === name) {
        return 'selected';
      } else {
        return '';
      }
    },
  },
};
</script>
