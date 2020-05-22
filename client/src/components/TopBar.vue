<template>
  <nav class="navbar navbar-default">
    <div class="container-fluid topbar">
      <div class="col-sm-2">
        <!--<img class="portrait" v-bind:src="require('../assets/images/portraits/YugiThumbnail.png')">-->
        <img class="portrait" v-bind:src="require('../assets/images/portraits/' + game.PlayerPortrait)">
      </div>
      <div class="col-sm-1">
        {{ game.PlayerLP }}
      </div>
      <div class="col-sm-2"> {{ game.Phase }} </div>
      <div class="col-sm-2"> {{ this.getTurnPlayerName() }}'s Turn </div>
      <div class="col-sm-1">
        <img class="cardback" v-bind:src="require('../assets/images/cardback.jpg')">
      </div>
      <div class="col-sm-1">
        <p class="text-center">
          {{ 'x' + game.OppHandSize }}
        </p>
      </div>
      <div class="col-sm-1">
        {{ game.OpponentLP }}
      </div>
      <div class="col-sm-2">
        <!--<img class="portrait" v-bind:src="require('../assets/images/portraits/Random.png')">-->
        <img class="portrait" v-bind:src="require('../assets/images/portraits/' + game.OpponentPortrait)">
      </div>
    </div>
  </nav>
</template>

<style>
.topbar {
  width: 100%;
  height: 75px;
}
.portrait {
  height: 75px;
  width: 75px;
}
.cardback {
  height: 75px;
}
</style>

<script>
export default {
  name: 'TopBar',
  props: {
    game: {},
  },
  methods: {
    getTurnPlayerName() {
      if (this.game.Turn === 1) {
        return this.game.PlayerName;
      } else if (this.game.Turn === 2) {
        return this.game.OpponentName;
      } else {
        return '';
      }
    },
  },
};
</script>
