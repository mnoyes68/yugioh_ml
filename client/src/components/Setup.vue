<template>
  <div class="container-fluid">
    <h2 class="center">Enter your name</h2>
    <input id="playerNameEntry" class="center">
    <p class="padp"></p>
    <h2 class="center">Select a Player</h2>
    <div class="row">
      <playerbar @choice="setPlayerChoice" id="playerSelect" selector="Player"></playerbar>
    </div>
    <div class="row">
      <playerbar @choice="setOppChoice" id="opponentSelect" selector="Opponent"></playerbar>
    </div>
    <div class="row">
      <!--<router-link v-on:click.native="launchGame" class="center" to="/game">Start Game</router-link>-->
      <button v-on:click="launchGame" class="center btn btn-primary button_right">Start Game</button>
    </div>
  </div>
</template>

<style>
.center {
  display: block;
  margin-left: auto;
  margin-right: auto;
  width: 50%;
}
.padp {
  padding-bottom: 10px;
}
</style>

<script>
import axios from 'axios';
import PlayerBar from './PlayerBar.vue';

export default {
  name: 'Setup',
  props: {
    playerChoice: String,
    oppChoice: String,
  },
  components: {
    playerbar: PlayerBar,
  },
  methods: {
    setPlayerChoice(choice) {
      console.log(choice);
      this.playerChoice = choice;
    },
    setOppChoice(choice) {
      console.log(choice);
      this.oppChoice = choice;
    },
    launchGame() {
      // Launch the game in the python server
      const gameDetails = {};
      gameDetails['Player'] = this.playerChoice;
      gameDetails['Opponent'] = this.oppChoice;
      gameDetails['Username'] = document.getElementById('playerNameEntry').value;

      const path = 'http://localhost:5000/launchgame';
      axios.post(path, gameDetails)
        .then((res) => {
          console.log(res);
        })
        .catch((error) => {
          console.error(error);
        });

      // Take player to the game
      this.$router.push({ path: '/game' });
    },
  },
};
</script>
